#include "common.h"


/* Refresh curve floor first. MarkerEAD0=5AA5A55A resets both feedback banks and selects0. Otherwise
   healthy banks select min(staged6E1A,6E1C); bit0 selects bank1/resetbank0, else bit1 selects
   bank0/resetbank1. Both bits therefore take bit0 precedence, not neutral fallback. Clamp selected
   request at upper0 then lower curve floor6D8C, publish6D8A. Reset leaves staged snapshot/ratio
   intact. Exact forced-override31B2C is0. */

void f33_select_feedback_bounded_first_current_request(void)

{
  short sVar1;
  uint32_t puVar2;
  uint uVar3;
  int iVar4;
  int iVar5;
  short sVar6;
  int iVar7;
  
  puVar2 = 0xfebeb800u;
  uVar3 = f33_current_reference_curve_feedback_magnitude();
  f33_update_current_reference_curve_floor((ushort)uVar3);
  sVar6 = (*((short *)camry_host_ptr((uint32_t)((0xffffb58cu + (uint32_t)((int)puVar2))))));
  iVar5 = (int)sVar6;
  if ((*((int *)camry_host_ptr((uint32_t)(puVar2 + 0x32d0)))) == 0x5aa5a55a) {
    iVar7 = 0;
    f33_reset_bank0_current_reference_feedback();
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
      f33_reset_bank0_current_reference_feedback();
      iVar7 = iVar4;
      goto LAB_00038130;
    }
  }
  f33_reset_bank1_current_reference_feedback();
LAB_00038130:
  sVar1 = f33_current_reference_floor_calibration.forced_request;
  if (f33_current_reference_floor_calibration.force_enabled == '\x01') {
    f33_reset_bank0_current_reference_feedback();
    f33_reset_bank1_current_reference_feedback();
    sVar6 = sVar1;
  }
  else {
    iVar4 = (int)f33_current_reference_floor_calibration.request_upper;
    if (iVar4 - iVar7 < 0 != (iVar4 < 0 != iVar7 < 0 && iVar7 < 0 == iVar4 - iVar7 < 0)) {
      iVar7 = iVar4;
    }
    if (iVar7 - iVar5 < 0 == (iVar7 < 0 != iVar5 < 0 && iVar5 < 0 == iVar7 - iVar5 < 0)) {
      sVar6 = (short)iVar7;
    }
  }
  (*((short *)camry_host_ptr((uint32_t)((0xffffb58au + (uint32_t)((int)puVar2)))))) = sVar6;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_3815e(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_38160(void)

{
  return;
}



/* WARNING: Removing unreachable block (ram,0x0003832e) */
/* WARNING: Removing unreachable block (ram,0x0003832a) */
/* WARNING: Removing unreachable block (ram,0x00038304) */
/* WARNING: Removing unreachable block (ram,0x00038300) */
/* WARNING: Removing unreachable block (ram,0x000382f4) */
/* WARNING: Removing unreachable block (ram,0x000382ee) */
/* WARNING: Removing unreachable block (ram,0x000382ac) */
/* WARNING: Removing unreachable block (ram,0x00038250) */
/* WARNING: Removing unreachable block (ram,0x00038216) */
/* WARNING: Removing unreachable block (ram,0x000381b8) */
/* Use current-pair squared magnitude and a separate abs(5F36) map, quadrant-aware angle70BE0 and
   trig70E32. Sixfold wrapped phase produces corrections clamped to +/-1280;71EC low2bits suppress
   them. Publish6DA6/8=0 and6DAA/C corrections. This is not the complete downstream motor transform.
   Squared-vector gain and wrapped sixfold-angle correction feed separate current-pair corrections.
   Native case exercises the zero-tail speed-gain branch; other gain and trigonometric branches
   instruction/dataflow checked. Not the complete motor transform. */

void f33_calculate_sixfold_current_correction(void)

{
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
  ushort uStack_1e;
  short sStack_1c;
  short sStack_1a;
  
  puVar4 = 0xfebeb800u;
  iVar5 = (int)DAT_febe6dd6;
  iVar9 = (int)f33_actual_first_current_command;
  uVar3 = (uint)((int)DAT_febe6dd6 * (int)DAT_febe6dd6 +
                (int)f33_actual_first_current_command * (int)f33_actual_first_current_command) >>
          0xd;
  if (0xffff < uVar3) {
    uVar3 = 0xffff;
  }
  uVar12 = (uVar3 & 0xffff) >> 8;
  DAT_febe6db2 = (undefined2)uVar3;
  if (uVar12 < 0xff) {
    DAT_febe6dbc = (uint)*(ushort *)(((undefined *)camry_host_ptr(0x2cb26u)) + uVar12 * 4) +
                   (int)((uVar3 & 0xff) *
                        ((uint)*(ushort *)(((undefined *)camry_host_ptr(0x2cb26u)) + (uVar12 + 1) * 4) -
                        (uint)*(ushort *)(((undefined *)camry_host_ptr(0x2cb26u)) + uVar12 * 4))) / 0x100 & 0xffff;
  }
  else {
    DAT_febe6dbc = 0x400;
  }
  uVar3 = (uint)DAT_febe5f36;
  if ((int)(uVar3 + 0x7fff) < 0 == (-1 < (int)uVar3 && (int)(uVar3 + 0x7fff) < 0) &&
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
    DAT_febe6d9e = *(ushort *)(((undefined *)camry_host_ptr(0x2c722u)) + uVar13 * 4) +
                   (short)((int)((uVar12 & 1) *
                                ((uint)*(ushort *)(((undefined *)camry_host_ptr(0x2c722u)) + (uVar13 + 1) * 4) -
                                (uint)*(ushort *)(((undefined *)camry_host_ptr(0x2c722u)) + uVar13 * 4))) / 2);
  }
  else {
    DAT_febe6d9e = 0;
  }
  sVar6 = -DAT_00031b84;
  iVar8 = (int)DAT_00031b84 - uVar3;
  iVar7 = (int)sVar6;
  sVar10 = DAT_febe5f36;
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
  FUN_00070be0(iVar9,iVar5,&uStack_1e);
  iVar9 = (int)f33_current_correction_phase_slope;
  iVar5 = (*((int *)camry_host_ptr((uint32_t)((0xffffb5bcu + (uint32_t)((int)puVar4))))));
  uVar1 = (*((ushort *)camry_host_ptr((uint32_t)((0xffffb59eu + (uint32_t)((int)puVar4))))));
  (*((ushort *)camry_host_ptr((uint32_t)((0xffffb5aeu + (uint32_t)((int)puVar4)))))) = uStack_1e;
  sVar10 = (*((short *)camry_host_ptr((uint32_t)(puVar4 + -0x3ab6))));
  iVar9 = (int)((uint)uStack_1e * iVar9) / 0x400;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb5b0u + (uint32_t)((int)puVar4)))))) = (short)iVar9;
  uVar3 = (iVar9 + (int)sVar10 + (sVar6 * iVar8 * 5) / 0x400) * 6;
  uVar2 = (undefined2)uVar3;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb5a0u + (uint32_t)((int)puVar4)))))) = uVar2;
  FUN_00070e32(uVar3 & 0xffff,&sStack_1c,&sStack_1a);
  sVar6 = f33_current_correction_coefficient_b;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb5a4u + (uint32_t)((int)puVar4)))))) = sStack_1a;
  sVar10 = f33_current_correction_coefficient_a;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb5a2u + (uint32_t)((int)puVar4)))))) = sStack_1c;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb5a0u + (uint32_t)((int)puVar4)))))) = uVar2;
  (*((int *)camry_host_ptr((uint32_t)((0xffffb5c0u + (uint32_t)((int)puVar4)))))) = (int)sVar6 * (int)sStack_1a;
  (*((int *)camry_host_ptr((uint32_t)((0xffffb5c4u + (uint32_t)((int)puVar4)))))) = (int)sVar10 * (int)sStack_1c;
  iVar9 = (((((int)sVar6 * (int)sStack_1a) / 0x100) * iVar5) / 0x400) * (uint)uVar1;
  iVar5 = (((((int)sVar10 * (int)sStack_1c) / 0x100) * iVar5) / 0x400) * (uint)uVar1;
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
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_3835a(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_3835c(void)

{
  return;
}



/* Publish actual first-axis6DC8=min(base map6DEC,additional bound6DFA), except exact disabled
   override31BF0=0. Separately publish feedback baseline6DCA=min(base map6DEC,pre-additional
   request6D8A). These can differ; paired feedback uses6DCA, not final6DC8. Native scaled-release
   composition verifies this distinction. */

void f33_select_actual_and_feedback_first_current_baselines(void)

{
  int iVar1;
  int iVar2;
  
  iVar2 = (int)DAT_febe6dec;
  f33_actual_first_current_command = DAT_00031bf2;
  if ((DAT_00031bf0 != 'Z') &&
     (iVar1 = f33_additional_first_current_reference.output - iVar2,
     f33_actual_first_current_command = DAT_febe6dec,
     iVar1 < 0 !=
     (f33_additional_first_current_reference.output < 0 != iVar2 < 0 && iVar2 < 0 == iVar1 < 0))) {
    f33_actual_first_current_command = f33_additional_first_current_reference.output;
  }
  iVar1 = f33_current_reference_floor.selected_request - iVar2;
  f33_first_current_feedback_baseline = DAT_febe6dec;
  if (iVar1 < 0 !=
      (f33_current_reference_floor.selected_request < 0 != iVar2 < 0 && iVar2 < 0 == iVar1 < 0)) {
    f33_first_current_feedback_baseline = f33_current_reference_floor.selected_request;
  }
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_38392(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_38394(void)

{
  return;
}



/* WARNING: Removing unreachable block (ram,0x000384d0) */
/* WARNING: Removing unreachable block (ram,0x000384aa) */
/* WARNING: Removing unreachable block (ram,0x00038464) */
/* Use signed first component to select/blend five ROM curves over -12800,-10240,-7237,-3840,0. Each
   curve indexes saturating_abs(6E0A) with128-count spacing and unsigned ordinates; inter-curve
   weight is scaled1024. Publish bank/weight/ordinate state and return magnitude in R10. Caller384D8
   applies command sign. Interpolate signed first-component breakpoints and unsigned current-curve
   ordinates, publish interpolation state and return second-component magnitude. Native
   negative-command composition covers adjacent banks3/4; not exhaustive calibration-domain
   execution. */

int f33_interpolate_current_curve(short first_component)

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
  uVar1 = (uint)DAT_febe6e0a;
  if ((int)(uVar1 + 0x7fff) < 0 == (-1 < (int)uVar1 && (int)(uVar1 + 0x7fff) < 0) &&
      uVar1 != 0xffff8001) {
    if ((int)uVar1 < 0) {
      uVar1 = -uVar1;
    }
  }
  else {
    uVar1 = 0x7fff;
  }
  iVar7 = (int)DAT_00031bfa;
  if (iVar4 - iVar7 < 0 == (iVar4 < 0 != iVar7 < 0 && iVar7 < 0 == iVar4 - iVar7 < 0)) {
    iVar2 = (int)DAT_00031bfe;
    if (iVar4 - iVar2 < 0 == (iVar4 < 0 != iVar2 < 0 && iVar2 < 0 == iVar4 - iVar2 < 0)) {
      iVar10 = 4;
      iVar4 = 4;
      uVar3 = 0x400;
    }
    else {
      iVar8 = (int)DAT_00031bfc;
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
    iVar2 = (int)DAT_00031bf8;
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
      iVar7 = (int)DAT_00031bf6;
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
  iVar7 = *(int *)(((undefined *)camry_host_ptr(0x210e0u)) + iVar4 * 4);
  if (uVar9 < 0xff) {
    uVar5 = (uint)(*((ushort *)camry_host_ptr((uint32_t)(uVar9 * 4 + iVar7 + 2))));
    uVar9 = uVar5 + (int)((uVar1 & 0x7f) * ((*((ushort *)camry_host_ptr((uint32_t)((uVar9 + 1) * 4 + iVar7 + 2)))) - uVar5)) /
                    0x80 & 0xffff;
  }
  else {
    uVar9 = (uint)(*((ushort *)camry_host_ptr((uint32_t)(iVar7 + 0x3fe))));
  }
  uVar5 = (uVar1 & 0xffff) >> 7;
  iVar7 = *(int *)(((undefined *)camry_host_ptr(0x210e0u)) + iVar10 * 4);
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



void FUN_000384d8(void)

{
  short sVar1;
  short sVar2;
  uint32_t puVar3;
  int iVar4;
  
  sVar2 = DAT_febe6e0a;
  sVar1 = f33_actual_first_current_command;
  puVar3 = 0xfebeb800u;
  iVar4 = f33_interpolate_current_curve(f33_actual_first_current_command);
  if (sVar2 < 1) {
    iVar4 = -iVar4;
  }
  (*((int *)camry_host_ptr((uint32_t)((0xffffb5dcu + (uint32_t)((int)puVar3)))))) = iVar4;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb5ceu + (uint32_t)((int)puVar3)))))) = sVar1;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb5d6u + (uint32_t)((int)puVar3)))))) = (short)iVar4;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_384fe(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_38500(void)

{
  return;
}



/* WARNING: Removing unreachable block (ram,0x0003854e) */
/* Saturating abs(s16 sampled command6E0A), including-32768 to32767, selects signed2E33E ordinates
   with seven fractional bits. Index>=255 uses-7297. Clamp to exact[-25600,0], publish base
   first-axis6DEC and independent command magnitude6DEE. This is not the measured-feedback floor
   map37FD2. */

void f33_map_sampled_command_to_base_first_current(void)

{
  uint uVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  
  uVar1 = (uint)DAT_febe6e0a;
  if ((int)(uVar1 + 0x7fff) < 0 == (-1 < (int)uVar1 && (int)(uVar1 + 0x7fff) < 0) &&
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
    iVar2 = (int)(short)(*(short *)(((undefined *)camry_host_ptr(0x2e33eu)) + uVar4 * 4) +
                        (short)((int)((uVar1 & 0x7f) *
                                     ((int)*(short *)(((undefined *)camry_host_ptr(0x2e33eu)) + (uVar4 + 1) * 4) -
                                     (int)*(short *)(((undefined *)camry_host_ptr(0x2e33eu)) + uVar4 * 4))) / 0x80));
  }
  else {
    iVar2 = -0x1c81;
  }
  iVar3 = (int)f33_first_current_curve_upper_bound;
  if (iVar2 - iVar3 < 0 != (iVar2 < 0 != iVar3 < 0 && iVar3 < 0 == iVar2 - iVar3 < 0) ||
      iVar2 == iVar3) {
    iVar3 = iVar2;
  }
  iVar2 = (int)f33_first_current_curve_lower_bound;
  DAT_febe6dee = (short)uVar1;
  DAT_febe6dec = f33_first_current_curve_lower_bound;
  if (iVar3 - iVar2 < 0 == (iVar3 < 0 != iVar2 < 0 && iVar2 < 0 == iVar3 - iVar2 < 0)) {
    DAT_febe6dec = (short)iVar3;
  }
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_3857e(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_38580(void)

{
  return;
}



/* WARNING: Removing unreachable block (ram,0x00038592) */
/* Multiply signed input by signed gain6DF0, divide toward zero by128 and return signed low16 inR10.
   Publish prior output, quotient and unsaturated difference/pass-through observables; no actual
   slew clamp occurs in this image. Native bank1 gain69 case checks return use by385C4. */

short f33_scale_additional_first_current_request(short request)

{
  f33_additional_first_current_reference.previous_output =
       f33_additional_first_current_reference.output;
  f33_additional_first_current_reference.scaled_request =
       (short)(((int)f33_additional_first_current_reference.gain_q7 * (int)request) / 0x80);
  f33_additional_first_current_reference.delta =
       f33_additional_first_current_reference.scaled_request -
       f33_additional_first_current_reference.output;
  f33_additional_first_current_reference.delta_passthrough =
       f33_additional_first_current_reference.delta;
  f33_additional_first_current_reference.candidate =
       f33_additional_first_current_reference.delta + f33_additional_first_current_reference.output;
  return f33_additional_first_current_reference.delta +
         f33_additional_first_current_reference.output;
}



/* Return max(retained curve floor6D8C,min(signed input,ROM31B30=0)). Clamp occurs after38582
   signed16 narrowing. */

short f33_clamp_additional_first_current_request(short request)

{
  int iVar1;
  int iVar2;
  short sVar3;
  int iVar4;
  
  iVar2 = (int)request;
  iVar4 = (int)f33_current_reference_floor.curve_floor;
  iVar1 = (int)f33_current_reference_floor_calibration.request_upper;
  if (iVar1 - iVar2 < 0 != (iVar1 < 0 != iVar2 < 0 && iVar2 < 0 == iVar1 - iVar2 < 0)) {
    iVar2 = iVar1;
  }
  sVar3 = f33_current_reference_floor.curve_floor;
  if (iVar2 - iVar4 < 0 == (iVar2 < 0 != iVar4 < 0 && iVar4 < 0 == iVar2 - iVar4 < 0)) {
    sVar3 = (short)iVar2;
  }
  return sVar3;
}



/* Select gain calibration by E5C3&1. E741=11/22 maps saturated abs(s32 E744); other states use
   default128. Exact bank0 curve is flat128; bank1 decreases128 to0 between5287 and6809.
   With31B2C!=1,31D40=1 and6EA8=5A, scale6D8A through38582 then re-clamp385A8; otherwise retain
   unscaled6D8A. Publish6DFA. E744 is a staged AC1C copy, not independently identified external CAN
   authority. */

void f33_update_additional_first_current_request(void)

{
  uchar uVar1;
  char cVar2;
  uchar uVar3;
  uint32_t puVar4;
  int iVar5;
  short sVar6;
  undefined *puVar7;
  undefined2 local_1c;
  undefined2 uStack_1a;
  
  uVar3 = f33_additional_current_envelope_qualified;
  sVar6 = f33_current_reference_floor.selected_request;
  cVar2 = DAT_00031d40;
  uVar1 = f33_current_reference_floor_calibration.force_enabled;
  puVar4 = 0xfebeb800u;
  puVar7 = ((void *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x31ebcu + (uint32_t)(DAT_febee5c3 & 1) * 4u)))))));
  if ((DAT_febee741 == '\x11') || (DAT_febee741 == '\"')) {
    if (DAT_febee744 + -0x7fff < 0 == (DAT_febee744 < 0 && -1 < DAT_febee744 + -0x7fff) &&
        DAT_febee744 != 0x7fff) {
      iVar5 = 0x7fff;
    }
    else {
      iVar5 = DAT_febee744;
      if (DAT_febee744 + 0x7fff < 0 != (-1 < DAT_febee744 && DAT_febee744 + 0x7fff < 0)) {
        iVar5 = -0x7fff;
      }
    }
    puVar4 = 0xfebeb800u;
    FUN_0006a522((int)(short)iVar5,&local_1c);
    FUN_000702b0(puVar7,local_1c,&uStack_1a);
  }
  else {
    uStack_1a = (*((undefined2 *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x31eb4u + (uint32_t)(DAT_febee5c3 & 1) * 4u)))))));
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb5f0u + (uint32_t)((int)puVar4)))))) = uStack_1a;
  if (((uVar1 != '\x01') && (cVar2 == '\x01')) && (uVar3 == 'Z')) {
    sVar6 = f33_scale_additional_first_current_request(sVar6);
    sVar6 = f33_clamp_additional_first_current_request(sVar6);
  }
  (*((short *)camry_host_ptr((uint32_t)((0xffffb5fau + (uint32_t)((int)puVar4)))))) = sVar6;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_38674(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_38676(void)

{
  return;
}



/* WARNING: Removing unreachable block (ram,0x00038790) */
/* WARNING: Removing unreachable block (ram,0x00038776) */
/* WARNING: Removing unreachable block (ram,0x00038738) */
/* Symmetricabs signedinput bounded65535, interpolate128-grid unsignedordinates from5
   realmapsselected bysignedselector andQ10crossmapweight,restoreinputsign. No
   physicalaxisunitsclaimed. */

int f33_lookup_signed_five_map_signal(int value,short selector)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  int iVar6;
  uint uVar7;
  int iVar8;
  undefined *puVar9;
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
  puVar9 = ((void *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x210f4u + (uint32_t)(iVar10) * 4u)))))));
  if (uVar7 < 0xff) {
    uVar4 = (uint)*(ushort *)(puVar9 + uVar7 * 4 + 2) +
            (int)((uVar5 & 0x7f) *
                 ((uint)*(ushort *)(puVar9 + (uVar7 + 1) * 4 + 2) -
                 (uint)*(ushort *)(puVar9 + uVar7 * 4 + 2))) / 0x80 & 0xffff;
  }
  else {
    uVar4 = (uint)*(ushort *)(puVar9 + 0x3fe);
  }
  puVar9 = ((void *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x210f4u + (uint32_t)(iVar1) * 4u)))))));
  if (uVar7 < 0xff) {
    uVar5 = (uint)*(ushort *)(puVar9 + uVar7 * 4 + 2) +
            (int)((uVar5 & 0x7f) *
                 ((uint)*(ushort *)(puVar9 + (uVar7 + 1) * 4 + 2) -
                 (uint)*(ushort *)(puVar9 + uVar7 * 4 + 2))) / 0x80 & 0xffff;
  }
  else {
    uVar5 = (uint)*(ushort *)(puVar9 + 0x3fe);
  }
  iVar2 = (int)((uVar4 - uVar5) * uVar3) / 0x400 + uVar5;
  if (value < 1) {
    iVar2 = -iVar2;
  }
  return iVar2;
}



void FUN_0003879e(void)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  iVar2 = f33_lookup_signed_five_map_signal(DAT_febe6d78,DAT_febe6d70);
  (*((short *)camry_host_ptr((uint32_t)((0xffffb600u + (uint32_t)((int)puVar1)))))) = (short)iVar2;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_387b6(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_387b8(void)

{
  return;
}



void FUN_000387ba(void)

{
  DAT_febe6e04 = 0;
  DAT_febe6e05 = 0;
  DAT_febe6e0a = DAT_febe6af4;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_387ca(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_387cc(void)

{
  return;
}



/* Sequentially stage measured halfwords and full32-bit component banks6B34..48, paired feedback
   requests6B50/74 to6E1A/1C, diagnostic sibling6AF6 and prior saturation directions. Later380DE
   resets do not rewrite this generation; no atomic hardware acquisition claim. */

void f33_latch_current_feedback_and_reference_inputs(void)

{
  DAT_febe6e12 = DAT_febe6b34;
  DAT_febe6e14 = DAT_febe6b36;
  DAT_febe6e16 = DAT_febe6b38;
  DAT_febe6e18 = DAT_febe6b3a;
  DAT_febe6e28 = DAT_febe6b3c;
  DAT_febe6e2c = DAT_febe6b40;
  DAT_febe6e30 = DAT_febe6b44;
  DAT_febe6e1e = 0;
  DAT_febe6e20 = 0;
  DAT_febe6e34 = DAT_febe6b48;
  DAT_febe6e1a = f33_current_reference_feedback[0].request;
  DAT_febe6e1c = f33_current_reference_feedback[1].request;
  DAT_febe6e22 = DAT_febe6af6;
  DAT_febe6e24 = DAT_febe6af6;
  DAT_febe6e0c = f33_regulator_output_envelopes[0].first_saturation;
  DAT_febe6e0e = f33_regulator_output_envelopes[1].first_saturation;
  DAT_febe6e0d = f33_regulator_output_envelopes[0].second_saturation;
  DAT_febe6e0f = f33_regulator_output_envelopes[1].second_saturation;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_38836(void)

{
  return;
}



/* Paired constant publisher: DAT_febe6e40 = 0; and DAT_febe6e44 = 0;; shape-classified from the
   canonical corpus. Target cells not yet named. */

void FUN_00038838(void)

{
  DAT_febe6e40 = 0;
  DAT_febe6e44 = 0;
  return;
}



/* Mode0 adds the recovered offset. Mode5A aligns max to11426 when selector5A, otherwise min to492.
   Other modes choose upper12288-max when3*max>12288, otherwise0-min, then clamp each32-bit sum
   to0..12288. Publish halfwords6E3A/3C/3E; subsequent scaling and arbitration remain distinct.
   Native nonzero tail from5E280 and full staging-only5E202(2,0101) verify scoped transform,
   retention and arbitration effects. No fresh acquisition, upstream nonzero regulation or physical
   PWM claim. */

void f33_modulate_first_phase_triplet(void)

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
  
  sVar3 = (short)DAT_febe6b9c;
  sVar4 = (short)DAT_febe6ba0;
  sVar7 = (short)DAT_febe6ba4;
  if (DAT_febe6d5c == '\0') {
    DAT_febe6e3a = DAT_febe6d5e + sVar3;
    DAT_febe6e3c = DAT_febe6d5e + sVar4;
    DAT_febe6e3e = DAT_febe6d5e + sVar7;
  }
  else if (DAT_febe6d5c == 'Z') {
    iVar12 = DAT_febe6b9c;
    if (DAT_febe6ba0 - DAT_febe6b9c < 0 !=
        (DAT_febe6ba0 < 0 != DAT_febe6b9c < 0 && DAT_febe6b9c < 0 == DAT_febe6ba0 - DAT_febe6b9c < 0
        )) {
      iVar12 = DAT_febe6ba0;
    }
    if (DAT_febe6ba4 - iVar12 < 0 !=
        (DAT_febe6ba4 < 0 != iVar12 < 0 && iVar12 < 0 == DAT_febe6ba4 - iVar12 < 0)) {
      iVar12 = DAT_febe6ba4;
    }
    iVar11 = DAT_febe6b9c;
    if (DAT_febe6ba0 - DAT_febe6b9c < 0 ==
        (DAT_febe6ba0 < 0 != DAT_febe6b9c < 0 && DAT_febe6b9c < 0 == DAT_febe6ba0 - DAT_febe6b9c < 0
        ) && DAT_febe6ba0 != DAT_febe6b9c) {
      iVar11 = DAT_febe6ba0;
    }
    if (DAT_febe6ba4 - iVar11 < 0 ==
        (DAT_febe6ba4 < 0 != iVar11 < 0 && iVar11 < 0 == DAT_febe6ba4 - iVar11 < 0) &&
        DAT_febe6ba4 != iVar11) {
      iVar11 = DAT_febe6ba4;
    }
    sVar5 = DAT_00031e20 - (short)iVar11;
    sVar6 = (short)iVar12 - DAT_00031e22;
    if (f33_phase_offset_selector == 'Z') {
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
    iVar12 = DAT_febe6b9c;
    if (DAT_febe6ba0 - DAT_febe6b9c < 0 !=
        (DAT_febe6ba0 < 0 != DAT_febe6b9c < 0 && DAT_febe6b9c < 0 == DAT_febe6ba0 - DAT_febe6b9c < 0
        )) {
      iVar12 = DAT_febe6ba0;
    }
    if (DAT_febe6ba4 - iVar12 < 0 !=
        (DAT_febe6ba4 < 0 != iVar12 < 0 && iVar12 < 0 == DAT_febe6ba4 - iVar12 < 0)) {
      iVar12 = DAT_febe6ba4;
    }
    iVar11 = DAT_febe6b9c;
    if (DAT_febe6ba0 - DAT_febe6b9c < 0 ==
        (DAT_febe6ba0 < 0 != DAT_febe6b9c < 0 && DAT_febe6b9c < 0 == DAT_febe6ba0 - DAT_febe6b9c < 0
        ) && DAT_febe6ba0 != DAT_febe6b9c) {
      iVar11 = DAT_febe6ba0;
    }
    if (DAT_febe6ba4 - iVar11 < 0 ==
        (DAT_febe6ba4 < 0 != iVar11 < 0 && iVar11 < 0 == DAT_febe6ba4 - iVar11 < 0) &&
        DAT_febe6ba4 != iVar11) {
      iVar11 = DAT_febe6ba4;
    }
    iVar2 = uVar10 - iVar11;
    iVar1 = iVar11 * 3 - uVar10;
    if (iVar1 < 0 != (iVar11 * 3 < 0 && -1 < iVar1) || iVar1 == 0) {
      iVar2 = -(iVar12 - uVar9);
    }
    uVar15 = iVar2 + DAT_febe6ba4;
    uVar13 = iVar2 + DAT_febe6b9c;
    uVar8 = iVar2 + DAT_febe6ba0;
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



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_38940(void)

{
  return;
}



/* Paired constant publisher: DAT_febe6e50 = 0; and DAT_febe6e54 = 0;; shape-classified from the
   canonical corpus. Target cells not yet named. */

void FUN_00038942(void)

{
  DAT_febe6e50 = 0;
  DAT_febe6e54 = 0;
  return;
}



/* Paired modulation to6E4A/4C/4E. Mode5A selects upper alignment for selectorA5, opposite the first
   bank. Mode0 adds its offset; other modes use the same strict3*max threshold and0..12288 clamp.
   Native composition exercises first5A and secondA5 with nonzero deltas. Native nonzero tail
   from5E280 and full staging-only5E202(2,0101) verify scoped transform, retention and arbitration
   effects. No fresh acquisition, upstream nonzero regulation or physical PWM claim. */

void f33_modulate_second_phase_triplet(void)

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
  
  sVar3 = (short)DAT_febe6bc0;
  sVar4 = (short)DAT_febe6bc4;
  sVar7 = (short)DAT_febe6bc8;
  if (DAT_febe6d5d == '\0') {
    DAT_febe6e4a = DAT_febe6d60 + sVar3;
    DAT_febe6e4c = DAT_febe6d60 + sVar4;
    DAT_febe6e4e = DAT_febe6d60 + sVar7;
  }
  else if (DAT_febe6d5d == 'Z') {
    iVar12 = DAT_febe6bc0;
    if (DAT_febe6bc4 - DAT_febe6bc0 < 0 !=
        (DAT_febe6bc4 < 0 != DAT_febe6bc0 < 0 && DAT_febe6bc0 < 0 == DAT_febe6bc4 - DAT_febe6bc0 < 0
        )) {
      iVar12 = DAT_febe6bc4;
    }
    if (DAT_febe6bc8 - iVar12 < 0 !=
        (DAT_febe6bc8 < 0 != iVar12 < 0 && iVar12 < 0 == DAT_febe6bc8 - iVar12 < 0)) {
      iVar12 = DAT_febe6bc8;
    }
    iVar11 = DAT_febe6bc0;
    if (DAT_febe6bc4 - DAT_febe6bc0 < 0 ==
        (DAT_febe6bc4 < 0 != DAT_febe6bc0 < 0 && DAT_febe6bc0 < 0 == DAT_febe6bc4 - DAT_febe6bc0 < 0
        ) && DAT_febe6bc4 != DAT_febe6bc0) {
      iVar11 = DAT_febe6bc4;
    }
    if (DAT_febe6bc8 - iVar11 < 0 ==
        (DAT_febe6bc8 < 0 != iVar11 < 0 && iVar11 < 0 == DAT_febe6bc8 - iVar11 < 0) &&
        DAT_febe6bc8 != iVar11) {
      iVar11 = DAT_febe6bc8;
    }
    sVar5 = DAT_00031e2c - (short)iVar11;
    sVar6 = (short)iVar12 - DAT_00031e2e;
    if (f33_phase_offset_selector == 0xa5) {
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
    iVar12 = DAT_febe6bc0;
    if (DAT_febe6bc4 - DAT_febe6bc0 < 0 !=
        (DAT_febe6bc4 < 0 != DAT_febe6bc0 < 0 && DAT_febe6bc0 < 0 == DAT_febe6bc4 - DAT_febe6bc0 < 0
        )) {
      iVar12 = DAT_febe6bc4;
    }
    if (DAT_febe6bc8 - iVar12 < 0 !=
        (DAT_febe6bc8 < 0 != iVar12 < 0 && iVar12 < 0 == DAT_febe6bc8 - iVar12 < 0)) {
      iVar12 = DAT_febe6bc8;
    }
    iVar11 = DAT_febe6bc0;
    if (DAT_febe6bc4 - DAT_febe6bc0 < 0 ==
        (DAT_febe6bc4 < 0 != DAT_febe6bc0 < 0 && DAT_febe6bc0 < 0 == DAT_febe6bc4 - DAT_febe6bc0 < 0
        ) && DAT_febe6bc4 != DAT_febe6bc0) {
      iVar11 = DAT_febe6bc4;
    }
    if (DAT_febe6bc8 - iVar11 < 0 ==
        (DAT_febe6bc8 < 0 != iVar11 < 0 && iVar11 < 0 == DAT_febe6bc8 - iVar11 < 0) &&
        DAT_febe6bc8 != iVar11) {
      iVar11 = DAT_febe6bc8;
    }
    iVar2 = uVar10 - iVar11;
    iVar1 = iVar11 * 3 - uVar10;
    if (iVar1 < 0 != (iVar11 * 3 < 0 && -1 < iVar1) || iVar1 == 0) {
      iVar2 = -(iVar12 - uVar9);
    }
    uVar15 = iVar2 + DAT_febe6bc8;
    uVar13 = iVar2 + DAT_febe6bc0;
    uVar8 = iVar2 + DAT_febe6bc4;
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



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_38a4a(void)

{
  return;
}



void FUN_00038a4c(void)

{
  DAT_febe6e58 = 0;
  DAT_febe6e5a = 0;
  DAT_febe6e5c = 0;
  return;
}



/* WARNING: Removing unreachable block (ram,0x00038b16) */
/* WARNING: Removing unreachable block (ram,0x00038b0a) */
/* WARNING: Removing unreachable block (ram,0x00038ada) */
/* WARNING: Removing unreachable block (ram,0x00038aca) */
/* WARNING: Removing unreachable block (ram,0x00038ab8) */
/* WARNING: Removing unreachable block (ram,0x00038ab4) */
/* WARNING: Removing unreachable block (ram,0x00038aa4) */
/* WARNING: Removing unreachable block (ram,0x00038a9c) */
/* WARNING: Removing unreachable block (ram,0x00038a98) */
/* WARNING: Removing unreachable block (ram,0x00038a94) */
/* WARNING: Removing unreachable block (ram,0x00038a76) */
/* WARNING: Removing unreachable block (ram,0x00038a72) */
/* Reference-derived first-bank phase transform used by compensation36750, not the final regulated
   output transform. Combine main/correction current pairs, halve when71EC low2bits clear, use
   output-frame coefficients7D54/56 and saturate triplet6E58/5A/5C. */

void FUN_00038a58(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  iVar2 = (int)DAT_febe6d82 + (int)DAT_febe6d80;
  iVar4 = (int)DAT_febe6d7e + (int)DAT_febe6d7c;
  if ((DAT_febe71ec & 3) == 0) {
    iVar2 = iVar2 / 2;
    iVar4 = iVar4 / 2;
  }
  iVar1 = (((iVar2 * (DAT_febe7d56 / 4) - iVar4 * (DAT_febe7d54 / 4)) / 0x8000) * 0x6883) / 0x2000;
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
  iVar2 = ((((iVar4 / 2 + (iVar2 * 0x6eda) / 0x8000) * (int)(DAT_febe7d54 / 4) +
            ((iVar4 * 0x6eda) / 0x8000 + -iVar2 / 2) * (int)(DAT_febe7d56 / 4)) / 0x8000) * 0x6883)
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



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_38b5c(void)

{
  return;
}



void FUN_00038b5e(void)

{
  DAT_febe6e60 = 0;
  DAT_febe6e62 = 0;
  DAT_febe6e64 = 0;
  return;
}



/* WARNING: Removing unreachable block (ram,0x00038c28) */
/* WARNING: Removing unreachable block (ram,0x00038c1c) */
/* WARNING: Removing unreachable block (ram,0x00038bec) */
/* WARNING: Removing unreachable block (ram,0x00038bdc) */
/* WARNING: Removing unreachable block (ram,0x00038bca) */
/* WARNING: Removing unreachable block (ram,0x00038bc6) */
/* WARNING: Removing unreachable block (ram,0x00038bb6) */
/* WARNING: Removing unreachable block (ram,0x00038bae) */
/* WARNING: Removing unreachable block (ram,0x00038baa) */
/* WARNING: Removing unreachable block (ram,0x00038ba6) */
/* WARNING: Removing unreachable block (ram,0x00038b88) */
/* WARNING: Removing unreachable block (ram,0x00038b84) */
/* Second-bank reference-derived phase compensation transform, paired with38A58. Its triplet is
   distinct from the regulated output of38D6C. */

void FUN_00038b6a(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  iVar2 = (int)DAT_febe6d80 - (int)DAT_febe6d82;
  iVar4 = (int)DAT_febe6d7c - (int)DAT_febe6d7e;
  if ((DAT_febe71ec & 3) == 0) {
    iVar2 = iVar2 / 2;
    iVar4 = iVar4 / 2;
  }
  iVar1 = (((iVar2 * (DAT_febe7d62 / 4) - iVar4 * (DAT_febe7d60 / 4)) / 0x8000) * 0x6883) / 0x2000;
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
  iVar2 = ((((iVar4 / 2 + (iVar2 * 0x6eda) / 0x8000) * (int)(DAT_febe7d60 / 4) +
            ((iVar4 * 0x6eda) / 0x8000 + -iVar2 / 2) * (int)(DAT_febe7d62 / 4)) / 0x8000) * 0x6883)
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



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_38c6e(void)

{
  return;
}



void FUN_00038c70(void)

{
  DAT_febe6e68 = 0;
  DAT_febe6e6a = 0;
  DAT_febe6e6c = 0;
  return;
}



/* WARNING: Removing unreachable block (ram,0x00038d18) */
/* WARNING: Removing unreachable block (ram,0x00038d0c) */
/* WARNING: Removing unreachable block (ram,0x00038cdc) */
/* WARNING: Removing unreachable block (ram,0x00038ccc) */
/* WARNING: Removing unreachable block (ram,0x00038cbe) */
/* WARNING: Removing unreachable block (ram,0x00038cba) */
/* WARNING: Removing unreachable block (ram,0x00038cae) */
/* WARNING: Removing unreachable block (ram,0x00038ca4) */
/* WARNING: Removing unreachable block (ram,0x00038ca0) */
/* WARNING: Removing unreachable block (ram,0x00038c98) */
/* Transform limited first-bank axes with output-frame sine/cosine coefficients. Signed division
   truncates toward zero. Compute third phase from the negative sum of UNSATURATED first/second
   intermediates; publish all three saturated to +/-32767 at6E68/6A/6C. Measured-current and
   reference-compensation transforms are different producers. Native nonzero tail from5E280 and full
   staging-only5E202(2,0101) verify scoped transform, retention and arbitration effects. No fresh
   acquisition, upstream nonzero regulation or physical PWM claim. */

void f33_transform_first_regulated_phase_commands(void)

{
  int iVar1;
  int iVar2;
  
  iVar1 = ((((int)(DAT_febe7d56 / 4) * (int)DAT_febe6c40 -
            (int)(DAT_febe7d54 / 4) * (int)DAT_febe6c42) / 0x8000) * 0x6883) / 0x2000;
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
  iVar2 = (((((int)DAT_febe6c42 / 2 + (int)(short)((DAT_febe6c40 * 0x6eda) / 0x8000)) *
             (int)(DAT_febe7d54 / 4) +
            ((int)(short)((DAT_febe6c42 * 0x6eda) / 0x8000) + -(int)DAT_febe6c40 / 2) *
            (int)(DAT_febe7d56 / 4)) / 0x8000) * 0x6883) / 0x2000;
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



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_38d5e(void)

{
  return;
}



void FUN_00038d60(void)

{
  DAT_febe6e70 = 0;
  DAT_febe6e72 = 0;
  DAT_febe6e74 = 0;
  return;
}



/* WARNING: Removing unreachable block (ram,0x00038e08) */
/* WARNING: Removing unreachable block (ram,0x00038dfc) */
/* WARNING: Removing unreachable block (ram,0x00038dcc) */
/* WARNING: Removing unreachable block (ram,0x00038dbc) */
/* WARNING: Removing unreachable block (ram,0x00038dae) */
/* WARNING: Removing unreachable block (ram,0x00038daa) */
/* WARNING: Removing unreachable block (ram,0x00038d9e) */
/* WARNING: Removing unreachable block (ram,0x00038d94) */
/* WARNING: Removing unreachable block (ram,0x00038d90) */
/* WARNING: Removing unreachable block (ram,0x00038d88) */
/* Second-bank output-frame transform to6E70/72/74. Third phase uses unsaturated intermediate sum
   before its own +/-32767 clamp. Native nonzero composition covers both banks, subsequent
   compensation, modulation and losing slot0 publication. Native nonzero tail from5E280 and full
   staging-only5E202(2,0101) verify scoped transform, retention and arbitration effects. No fresh
   acquisition, upstream nonzero regulation or physical PWM claim. */

void f33_transform_second_regulated_phase_commands(void)

{
  int iVar1;
  int iVar2;
  
  iVar1 = ((((int)(DAT_febe7d62 / 4) * (int)DAT_febe6c44 -
            (int)(DAT_febe7d60 / 4) * (int)DAT_febe6c46) / 0x8000) * 0x6883) / 0x2000;
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
  iVar2 = (((((int)DAT_febe6c46 / 2 + (int)(short)((DAT_febe6c44 * 0x6eda) / 0x8000)) *
             (int)(DAT_febe7d60 / 4) +
            ((int)(short)((DAT_febe6c46 * 0x6eda) / 0x8000) + -(int)DAT_febe6c44 / 2) *
            (int)(DAT_febe7d62 / 4)) / 0x8000) * 0x6883) / 0x2000;
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



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_38e4e(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_38e50(void)

{
  return;
}



/* WARNING: This is an inlined function */
/* WARNING: Removing unreachable block (ram,0x00038e7e) */
/* WARNING: Removing unreachable block (ram,0x00038e7a) */
/* WARNING: Removing unreachable block (ram,0x00038e76) */
/* Scale first regulated phase triplet by shared scale/1024 with modulation-dependent output-code
   bounds; write three halfwords through R7. R6 remains the scale input used by subsequent38EE2.
   Signed scale in r6, unsigned-halfword triplet destination in r7. Scale and modulation-dependent
   code bounds; real leaf p-code inlining preserves shared r6 for the second bank. Native full
   caller reaches both compare buffers; no electrical-duty interpretation. */

void f33_scale_first_phase_codes(int scale,ushort *triplet)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  
  DAT_febe6e90 = (DAT_febe6e3a * scale) / 0x400;
  uVar6 = (DAT_febe6e3c * scale) / 0x400;
  uVar1 = (DAT_febe6e3e * scale) / 0x400;
  DAT_febe6e7c = DAT_00031e3c;
  DAT_febe6e86 = DAT_00031e3a;
  if (DAT_febe6d5c == '\0') {
    DAT_febe6e7c = DAT_00031e40;
    DAT_febe6e86 = DAT_00031e3e;
  }
  uVar5 = (uint)DAT_febe6e86;
  uVar4 = (uint)DAT_febe6e7c;
  uVar2 = uVar5;
  if ((int)(DAT_febe6e90 - uVar5) < 0 != ((int)DAT_febe6e90 < 0 && -1 < (int)(DAT_febe6e90 - uVar5))
     ) {
    uVar2 = DAT_febe6e90;
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



/* WARNING: This is an inlined function */
/* WARNING: Removing unreachable block (ram,0x00038f0e) */
/* WARNING: Removing unreachable block (ram,0x00038f0a) */
/* WARNING: Removing unreachable block (ram,0x00038f06) */
/* Second-bank counterpart of38E52. Real ABI consumes scale in R6 and destination in R7; caller38F72
   reuses retained R6 and supplies SP for this triplet, SP+6 for the first. Second-bank phase-code
   scaling and bound selection with the same two-argument interface. Native full caller executes
   both banks with retained shared scale and separate triplet destinations. */

void f33_scale_second_phase_codes(int scale,ushort *triplet)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  
  DAT_febe6e9c = (DAT_febe6e4a * scale) / 0x400;
  uVar6 = (DAT_febe6e4c * scale) / 0x400;
  uVar1 = (DAT_febe6e4e * scale) / 0x400;
  DAT_febe6e82 = DAT_00031e3c;
  DAT_febe6e8a = DAT_00031e3a;
  if (DAT_febe6d5d == '\0') {
    DAT_febe6e82 = DAT_00031e40;
    DAT_febe6e8a = DAT_00031e3e;
  }
  uVar5 = (uint)DAT_febe6e8a;
  uVar4 = (uint)DAT_febe6e82;
  uVar2 = uVar5;
  if ((int)(DAT_febe6e9c - uVar5) < 0 != ((int)DAT_febe6e9c < 0 && -1 < (int)(DAT_febe6e9c - uVar5))
     ) {
    uVar2 = DAT_febe6e9c;
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



/* WARNING: Inlined function: f33_scale_first_phase_codes */
/* WARNING: Inlined function: f33_scale_second_phase_codes */
/* WARNING: Removing unreachable block (ram,0x00038f0e) */
/* WARNING: Removing unreachable block (ram,0x00038f0a) */
/* WARNING: Removing unreachable block (ram,0x00038f06) */
/* WARNING: Removing unreachable block (ram,0x00038e7e) */
/* WARNING: Removing unreachable block (ram,0x00038e7a) */
/* WARNING: Removing unreachable block (ram,0x00038e76) */
/* Run both real phase-code scaling helpers with ROM31E38, publish the paired triplets
   through57BCA(2,0,...) and enable slot0 through57C48(0). Arbitration, staging and later hardware
   commit remain distinct operations. Publish bounded triplets to arbitration slot0 and enable it.
   First destination sp+6, second sp; shared r6 scale remains live across the first real helper.
   Native full caller includes subsequent arbitration and compare staging without replacement
   callees or binary patches. */

void f33_publish_current_output_slot(void)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  ushort uStack_14;
  undefined2 uStack_12;
  ushort uStack_10;
  ushort local_e;
  undefined2 uStack_c;
  ushort uStack_a;
  
  uVar2 = (uint)DAT_00031e38;
  DAT_febe6e90 = (int)((int)DAT_febe6e3a * uVar2) / 0x400;
  DAT_febe6e94 = (int)((int)DAT_febe6e3c * uVar2) / 0x400;
  DAT_febe6e98 = (int)((int)DAT_febe6e3e * uVar2) / 0x400;
  DAT_febe6e88 = DAT_00031e3c;
  DAT_febe6e86 = DAT_00031e3a;
  if (DAT_febe6d5c == '\0') {
    DAT_febe6e88 = DAT_00031e40;
    DAT_febe6e86 = DAT_00031e3e;
  }
  uVar4 = (uint)DAT_febe6e86;
  uVar3 = (uint)DAT_febe6e88;
  uVar5 = uVar4;
  if ((int)(DAT_febe6e90 - uVar4) < 0 != ((int)DAT_febe6e90 < 0 && -1 < (int)(DAT_febe6e90 - uVar4))
     ) {
    uVar5 = DAT_febe6e90;
  }
  uVar1 = uVar3;
  if ((int)(uVar5 - uVar3) < 0 == ((int)uVar5 < 0 && -1 < (int)(uVar5 - uVar3))) {
    uVar1 = uVar5;
  }
  DAT_febe6e78 = (ushort)uVar1;
  uVar5 = uVar4;
  if ((int)(DAT_febe6e94 - uVar4) < 0 != ((int)DAT_febe6e94 < 0 && -1 < (int)(DAT_febe6e94 - uVar4))
     ) {
    uVar5 = DAT_febe6e94;
  }
  uVar1 = uVar3;
  if ((int)(uVar5 - uVar3) < 0 == ((int)uVar5 < 0 && -1 < (int)(uVar5 - uVar3))) {
    uVar1 = uVar5;
  }
  DAT_febe6e7a = (undefined2)uVar1;
  if ((int)(DAT_febe6e98 - uVar4) < 0 != ((int)DAT_febe6e98 < 0 && -1 < (int)(DAT_febe6e98 - uVar4))
     ) {
    uVar4 = DAT_febe6e98;
  }
  DAT_febe6e7c = DAT_febe6e88;
  if ((int)(uVar4 - uVar3) < 0 == ((int)uVar4 < 0 && -1 < (int)(uVar4 - uVar3))) {
    DAT_febe6e7c = (ushort)uVar4;
  }
  DAT_febe6e9c = (int)((int)DAT_febe6e4a * uVar2) / 0x400;
  DAT_febe6ea0 = (int)((int)DAT_febe6e4c * uVar2) / 0x400;
  DAT_febe6ea4 = (int)((int)DAT_febe6e4e * uVar2) / 0x400;
  DAT_febe6e8c = DAT_00031e3c;
  DAT_febe6e8a = DAT_00031e3a;
  if (DAT_febe6d5d == '\0') {
    DAT_febe6e8c = DAT_00031e40;
    DAT_febe6e8a = DAT_00031e3e;
  }
  uVar5 = (uint)DAT_febe6e8a;
  uVar4 = (uint)DAT_febe6e8c;
  uVar2 = uVar5;
  if ((int)(DAT_febe6e9c - uVar5) < 0 != ((int)DAT_febe6e9c < 0 && -1 < (int)(DAT_febe6e9c - uVar5))
     ) {
    uVar2 = DAT_febe6e9c;
  }
  uVar3 = uVar4;
  if ((int)(uVar2 - uVar4) < 0 == ((int)uVar2 < 0 && -1 < (int)(uVar2 - uVar4))) {
    uVar3 = uVar2;
  }
  DAT_febe6e7e = (ushort)uVar3;
  uVar2 = uVar5;
  if ((int)(DAT_febe6ea0 - uVar5) < 0 != ((int)DAT_febe6ea0 < 0 && -1 < (int)(DAT_febe6ea0 - uVar5))
     ) {
    uVar2 = DAT_febe6ea0;
  }
  uVar3 = uVar4;
  if ((int)(uVar2 - uVar4) < 0 == ((int)uVar2 < 0 && -1 < (int)(uVar2 - uVar4))) {
    uVar3 = uVar2;
  }
  DAT_febe6e80 = (undefined2)uVar3;
  if ((int)(DAT_febe6ea4 - uVar5) < 0 != ((int)DAT_febe6ea4 < 0 && -1 < (int)(DAT_febe6ea4 - uVar5))
     ) {
    uVar5 = DAT_febe6ea4;
  }
  DAT_febe6e82 = DAT_febe6e8c;
  if ((int)(uVar5 - uVar4) < 0 == ((int)uVar5 < 0 && -1 < (int)(uVar5 - uVar4))) {
    DAT_febe6e82 = (ushort)uVar5;
  }
  DAT_febe6e84 = DAT_00031e38;
  uStack_14 = DAT_febe6e7e;
  uStack_12 = DAT_febe6e80;
  uStack_10 = DAT_febe6e82;
  local_e = DAT_febe6e78;
  uStack_c = DAT_febe6e7a;
  uStack_a = DAT_febe6e7c;
  f33_write_phase_output_slot_pair(2,'\0',&local_e,&uStack_14);
  f33_activate_phase_output_slot_pair('\0');
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_38fa8(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_38faa(void)

{
  return;
}



/* Use706AE symmetric signed32 saturation on s32 E744 times sign-extended s16 E5C4; return resulting
   fullR10 product. Qualifier38FC6 tests its sign; no physical-unit assignment. */

int f33_current_reference_envelope_signed_product(void)

{
  int local_8;
  
  FUN_000706ae(DAT_febee744,(int)DAT_febee5c4,&local_8);
  return local_8;
}



/* Admit5A for E741=0 or E741=11/22 with positive supplied product; require EAC0!=11 or unsignedEAC6
   below selected threshold, plusE740/E742 zero. Exact317B0=0 does not force rejection; EAC2=5A
   does. This is numerical envelope qualification, not engagement authority. */

uint f33_qualify_additional_current_reference_envelope(int signed_product)

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



/* Only8A20==1 recomputes signed product38FAC and qualifier38FC6, publishing6EA8. Other invocations
   retain the previous qualifier; consumers run in separate current-control generations. */

void f33_refresh_current_reference_envelope_qualification(void)

{
  uint32_t puVar1;
  int signed_product;
  uint uVar2;
  
  puVar1 = 0xfebeb800u;
  if (DAT_febe8a20 == '\x01') {
    signed_product = f33_current_reference_envelope_signed_product();
    uVar2 = f33_qualify_additional_current_reference_envelope(signed_product);
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb6a8u + (uint32_t)((int)puVar1) * 1u)))) = (char)uVar2;
  }
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_39058(void)

{
  return;
}



void FUN_0003905a(void)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  iVar2 = FUN_000588b6();
  if (iVar2 == 0) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb6acu + (uint32_t)((int)puVar1) * 1u)))) = 0;
  }
  return;
}



/* Same strict32000/marker0/source-byte selection; histories6ED8/6EDC. Caller39126 loads record+32
   intoR6 and preserves it through the39152 call; no invented NvM return argument. Source5 marker
   argument is loaded from record+32 into R6 and preserved through caller; it is not an invented
   secondary NvM result. Selected signed difference must exceed32000. */

uint f33_should_zero_ecu_source5_thermal_seed(ushort record_marker)

{
  int iVar1;
  uint uVar2;
  
  if ((DAT_febe7bf8 & 0xff) == 0) {
    if ((DAT_febe7bf8 & 0xff00) != 0) {
      DAT_febe6ed8 = (int)DAT_febe7dd0 - (int)DAT_febe7dce;
      iVar1 = DAT_febe6ed8;
      goto LAB_000390b6;
    }
  }
  else if ((DAT_febe7bf8 & 0xff00) == 0) {
    DAT_febe6edc = (int)DAT_febe7dd8 - (int)DAT_febe7dd6;
    iVar1 = DAT_febe6edc;
    goto LAB_000390b6;
  }
  DAT_febe6ed8 = (int)DAT_febe7dd0 - (int)DAT_febe7dce;
  DAT_febe6edc = (int)DAT_febe7dd8 - (int)DAT_febe7dd6;
  iVar1 = DAT_febe6ed8;
  if (DAT_febe6edc - DAT_febe6ed8 < 0 !=
      (DAT_febe6edc < 0 != DAT_febe6ed8 < 0 && DAT_febe6ed8 < 0 == DAT_febe6edc - DAT_febe6ed8 < 0))
  {
    iVar1 = DAT_febe6edc;
  }
LAB_000390b6:
  if ((iVar1 - DAT_0002b2b4 < 0 ==
       (iVar1 < 0 != DAT_0002b2b4 < 0 && DAT_0002b2b4 < 0 == iVar1 - DAT_0002b2b4 < 0) &&
       iVar1 != DAT_0002b2b4) && (record_marker == 0)) {
    uVar2 = 0x5a;
  }
  else {
    uVar2 = 0;
  }
  return uVar2;
}



undefined4 FUN_000390d4(short param_1,short param_2)

{
  int iVar1;
  int iVar2;
  undefined4 local_8;
  
  iVar2 = (int)param_2;
  if (iVar2 == 0) {
    local_8 = 0;
  }
  else {
    iVar1 = (int)param_1 << 0xc;
    if (iVar2 != 0) {
      if (iVar1 == -0x80000000 && iVar2 == -1) {
        iVar1 = -0x80000000;
      }
      else {
        iVar1 = iVar1 / iVar2;
      }
    }
    FUN_000706ae(iVar1,0x80,&local_8);
  }
  return local_8;
}



/* Record6 terms18..22 and marker32; same exact-status and conditional-zero contract. Rejected
   record uses539/3803/0/0/0/0. Seed via signed contribution*4096/gain followed by saturating
   multiply128; zero gain seeds0. Does not rewrite the retained record. Source5 six saved
   contributions pass exact status/marker qualification. Strict selected-difference boundary changes
   downstream model/map winner while retaining the source record. */

void f33_restore_ecu_source5_thermal_model(void)

{
  uint *puVar1;
  uint32_t puVar2;
  int iVar3;
  uint uVar4;
  undefined4 uVar5;
  undefined4 uVar6;
  undefined4 uVar7;
  undefined4 uVar8;
  undefined4 uVar9;
  undefined4 uVar10;
  int iVar11;
  int iVar12;
  int iVar13;
  int iVar14;
  int iVar15;
  undefined4 *puVar16;
  uint local_58 [6];
  short sStack_40;
  short sStack_3e;
  short sStack_3c;
  short sStack_3a;
  short sStack_38;
  short sStack_36;
  ushort uStack_26;
  
  puVar2 = 0xfebeb800u;
  puVar1 = local_58;
  puVar16 = ((undefined *)camry_host_ptr(0x21108u));
  do {
    uVar10 = *puVar16;
    puVar16 = puVar16 + 1;
    *puVar1 = uVar10;
    puVar1 = puVar1 + 1;
  } while ((uintptr_t)(puVar16)!=(uintptr_t)(((undefined *)camry_host_ptr(0x21140u))));
  uVar4 = f33_nvm_get_record(6, camry_host_addr(local_58));
  if ((uVar4 == 0x10) && (uStack_26 != 0xa55a)) {
    if ((((((*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x3c08)))) & 0xff) == 0) ||
         (((*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x3c08)))) & 0xff00) == 0)) && (uStack_26 != 0x5aa5)) &&
       (uVar4 = f33_should_zero_ecu_source5_thermal_seed(uStack_26), uVar4 == 0x5a)) {
      iVar3 = 0;
      iVar15 = 0;
      iVar14 = 0;
      iVar13 = 0;
      iVar12 = 0;
      iVar11 = 0;
    }
    else {
      iVar3 = (int)sStack_40;
      iVar15 = (int)sStack_3e;
      iVar14 = (int)sStack_3c;
      iVar13 = (int)sStack_3a;
      iVar12 = (int)sStack_38;
      iVar11 = (int)sStack_36;
    }
  }
  else {
    iVar3 = (int)DAT_0002b2a6;
    iVar15 = (int)DAT_0002b2a8;
    iVar14 = (int)DAT_0002b2aa;
    iVar13 = (int)DAT_0002b2ac;
    iVar12 = (int)DAT_0002b2ae;
    iVar11 = (int)DAT_0002b2b0;
  }
  uVar10 = FUN_000390d4(iVar3,(int)DAT_0002b28c);
  uVar5 = FUN_000390d4(iVar15,(int)DAT_0002b28e);
  uVar6 = FUN_000390d4(iVar14,(int)DAT_0002b290);
  uVar7 = FUN_000390d4(iVar13,(int)DAT_0002b292);
  uVar8 = FUN_000390d4(iVar12,(int)DAT_0002b294);
  uVar9 = FUN_000390d4(iVar11,(int)DAT_0002b296);
  (*((undefined4 *)camry_host_ptr((uint32_t)((0xffffb6c0u + (uint32_t)((int)puVar2)))))) = uVar10;
  (*((undefined4 *)camry_host_ptr((uint32_t)((0xffffb6c4u + (uint32_t)((int)puVar2)))))) = uVar5;
  (*((undefined4 *)camry_host_ptr((uint32_t)((0xffffb6c8u + (uint32_t)((int)puVar2)))))) = uVar6;
  (*((undefined4 *)camry_host_ptr((uint32_t)((0xffffb6ccu + (uint32_t)((int)puVar2)))))) = uVar7;
  (*((undefined4 *)camry_host_ptr((uint32_t)((0xffffb6d0u + (uint32_t)((int)puVar2)))))) = uVar8;
  (*((undefined4 *)camry_host_ptr((uint32_t)((0xffffb6d4u + (uint32_t)((int)puVar2)))))) = uVar9;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb6aeu + (uint32_t)((int)puVar2)))))) = 0x3480;
  return;
}



/* Six poles6EC0..6ED4: first three use6EF0, last three70B0. Divisors200/420/1/1/1/1,
   gains13/100/0/0/0/0 and bias0. Clamp summed contributions then selector3 offset/following using
   source index2. Return adjusted signedR10; zero-gain poles still evolve. Three poles use6EF0 and
   three70B0; divisors200/420/1/1/1/1 and gains13/100/0/0/0/0. Zero-gain poles still evolve;
   selector3 returns adjusted signed estimate. */

int f33_calculate_ecu_source5_thermal_estimate(void)

{
  short upper;
  short lower;
  uint32_t puVar1;
  int state;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  int iVar10;
  int local_3c;
  short sStack_38;
  short sStack_36;
  short sStack_34;
  short sStack_32;
  undefined2 uStack_30;
  short sStack_2e;
  
  iVar8 = DAT_febe70b0;
  iVar7 = DAT_febe6ef0;
  iVar6 = DAT_febe6ed4;
  iVar5 = DAT_febe6ed0;
  iVar4 = DAT_febe6ecc;
  iVar3 = DAT_febe6ec8;
  iVar2 = DAT_febe6ec4;
  puVar1 = 0xfebeb800u;
  sStack_2e = DAT_febe6eae;
  state = f33_update_nonnegative_thermal_pole(DAT_febe6ec0,DAT_febe6ef0,(uint)DAT_0002b29a);
  iVar2 = f33_update_nonnegative_thermal_pole(iVar2,iVar7,(uint)DAT_0002b29c);
  iVar3 = f33_update_nonnegative_thermal_pole(iVar3,iVar7,(uint)DAT_0002b29e);
  iVar4 = f33_update_nonnegative_thermal_pole(iVar4,iVar8,(uint)DAT_0002b2a0);
  iVar5 = f33_update_nonnegative_thermal_pole(iVar5,iVar8,(uint)DAT_0002b2a2);
  iVar6 = f33_update_nonnegative_thermal_pole(iVar6,iVar8,(uint)DAT_0002b2a4);
  lower = DAT_0002b28a;
  upper = DAT_0002b288;
  iVar9 = (int)DAT_0002b288;
  iVar10 = (int)DAT_0002b28a;
  iVar7 = f33_scale_thermal_contribution(state,DAT_0002b28c,DAT_0002b288,DAT_0002b28a);
  iVar8 = f33_scale_thermal_contribution(iVar2,DAT_0002b28e,upper,lower);
  sStack_38 = (short)iVar8;
  iVar8 = f33_scale_thermal_contribution(iVar3,DAT_0002b290,upper,lower);
  sStack_36 = (short)iVar8;
  iVar8 = f33_scale_thermal_contribution(iVar4,DAT_0002b292,upper,lower);
  sStack_34 = (short)iVar8;
  iVar8 = f33_scale_thermal_contribution(iVar5,DAT_0002b294,upper,lower);
  sStack_32 = (short)iVar8;
  iVar8 = f33_scale_thermal_contribution(iVar6,DAT_0002b296,upper,lower);
  uStack_30 = (undefined2)iVar8;
  local_3c = (int)DAT_0002b298 +
             (int)sStack_34 + (int)sStack_36 + sStack_38 + iVar7 + (int)sStack_32 + iVar8;
  FUN_0007012a(local_3c,iVar9,iVar10,&local_3c);
  iVar8 = f33_apply_thermal_offset_and_following(3,(short)local_3c,sStack_2e);
  (*((int *)camry_host_ptr((uint32_t)((0xffffb6c0u + (uint32_t)((int)puVar1)))))) = state;
  (*((int *)camry_host_ptr((uint32_t)((0xffffb6c4u + (uint32_t)((int)puVar1)))))) = iVar2;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb6b0u + (uint32_t)((int)puVar1)))))) = (short)local_3c;
  (*((int *)camry_host_ptr((uint32_t)((0xffffb6c8u + (uint32_t)((int)puVar1)))))) = iVar3;
  (*((int *)camry_host_ptr((uint32_t)((0xffffb6ccu + (uint32_t)((int)puVar1)))))) = iVar4;
  (*((int *)camry_host_ptr((uint32_t)((0xffffb6d0u + (uint32_t)((int)puVar1)))))) = iVar5;
  (*((int *)camry_host_ptr((uint32_t)((0xffffb6d4u + (uint32_t)((int)puVar1)))))) = iVar6;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb6b2u + (uint32_t)((int)puVar1)))))) = (short)iVar7;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb6b4u + (uint32_t)((int)puVar1)))))) = sStack_38;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb6b6u + (uint32_t)((int)puVar1)))))) = sStack_36;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb6b8u + (uint32_t)((int)puVar1)))))) = sStack_34;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb6bau + (uint32_t)((int)puVar1)))))) = sStack_32;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb6bcu + (uint32_t)((int)puVar1)))))) = uStack_30;
  return iVar8;
}



/* Only zero6EAC requires7DCC/7BF6 both5A and390FE restoration. Store calculated signedR10 low16
   at6EAE; initialized updates do not require fresh admission bytes. Source5 six-pole update and
   offset source2 feed real maps and selected-bank arbitration; composed interval requests zero
   owner0 without touching other owners. */

void f33_update_ecu_source5_thermal_estimate(void)

{
  undefined *puVar1;
  undefined *puVar2;
  int iVar4;
  char cVar5;
  uint32_t puVar3;
  puVar3 = 0xfebeb800u;
  puVar2 = ((undefined *)camry_host_ptr(0xfebeb800u));
  cVar5 = DAT_febe6eac;
  puVar1 = ((undefined *)camry_host_ptr(0xfebeb800u));
  if (DAT_febe6eac == '\0') {
    if ((DAT_febe7dcc != 'Z') || (DAT_febe7bf6 != 'Z')) goto LAB_0003936a;
    f33_restore_ecu_source5_thermal_model();
    cVar5 = 'Z';
    puVar1 = ((undefined *)camry_host_ptr((uint32_t)(puVar3)));
  }
  puVar2 = puVar1;
  iVar4 = f33_calculate_ecu_source5_thermal_estimate();
  *(short *)(((undefined *)camry_host_ptr(0xffffb6aeu)) + (int)camry_host_addr(puVar2)) = (short)iVar4;
LAB_0003936a:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb6acu + (uint32_t)((int)camry_host_addr(puVar2)) * 1u)))) = cVar5;
  return;
}



/* Constant-block fill: 12 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_39372(void)

{
  DAT_febe6eb2 = 0;
  DAT_febe6eb4 = 0;
  DAT_febe6eb6 = 0;
  DAT_febe6eb8 = 0;
  DAT_febe6eba = 0;
  DAT_febe6ebc = 0;
  DAT_febe6ec0 = 0;
  DAT_febe6ec4 = 0;
  DAT_febe6ec8 = 0;
  DAT_febe6ecc = 0;
  DAT_febe6ed0 = 0;
  DAT_febe6ed4 = 0;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_39390(void)

{
  return;
}



/* Paired constant publisher: DAT_febe6ee0 = 0x569a; and DAT_febe6ee2 = 0x2b4d;; shape-classified
   from the canonical corpus. Target cells not yet named. */

void FUN_00039392(void)

{
  DAT_febe6ee0 = 0x569a;
  DAT_febe6ee2 = 0x2b4d;
  return;
}



/* Signed6EAE selects2B2B8/2B2D4 into6EE0/6EE2. Bank0 reaches5542 at18560, bank1 reaches0 at15216.
   Distinct from flat motor/source3 maps and the signed current floor. Source5 maps reach5542
   at18560 in bank0 and zero at15216 in bank1. Bank selection is not cross-bank minimization. */

void f33_publish_ecu_source5_thermal_limit_maps(void)

{
  uint32_t puVar1;
  int iVar2;
  undefined2 local_c;
  undefined2 uStack_a;
  
  puVar1 = 0xfebeb800u;
  iVar2 = (int)DAT_febe6eae;
  FUN_0007025c(f33_ecu_source5_current_curve_bank0,iVar2,&local_c);
  FUN_0007025c(f33_ecu_source5_current_curve_bank1,iVar2,&uStack_a);
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb6e0u + (uint32_t)((int)puVar1)))))) = local_c;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb6e2u + (uint32_t)((int)puVar1)))))) = uStack_a;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_393dc(void)

{
  return;
}



void FUN_000393de(void)

{
  DAT_febe6ee6 = DAT_febe6f06;
  DAT_febe6ee8 = DAT_febe6f08;
  return;
}



/* Only tracker6EE4==1 polls object6: exact10 becomesFF, high-nibble30 becomesFE, all other statuses
   retain1. No transaction identity ties this poll to accepted publication. Only tracker1 polls
   record6: exact10 becomesFF, high-nibble30 becomesFE, otherwise pending holds. No accepted-request
   transaction identity. */

void f33_poll_thermal_history_record_status(void)

{
  uint32_t puVar1;
  uint uVar2;
  char cVar3;
  
  cVar3 = DAT_febe6ee4;
  puVar1 = 0xfebeb800u;
  if (DAT_febe6ee4 == '\x01') {
    puVar1 = 0xfebeb800u;
    uVar2 = f33_nvm_get_record_status(6);
    if (uVar2 == 0x10) {
      cVar3 = -1;
    }
    else if ((uVar2 & 0xf0) == 0x30) {
      cVar3 = -2;
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb6e4u + (uint32_t)((int)puVar1) * 1u)))) = cVar3;
  return;
}



/* Unsigned low16 product >>10, cappedFFFF; high input bits ignored. Unsigned low16 product
   shifted10 and cappedFFFF; high input bits do not participate. */

uint f33_scale_thermal_divisor(uint base,uint scale)

{
  uint uVar1;
  uint uVar2;
  
  uVar1 = (base & 0xffff) * (scale & 0xffff) >> 10;
  uVar2 = uVar1 & 0xffff;
  if (0xffff < uVar1) {
    uVar2 = 0xffff;
  }
  return uVar2;
}



/* Saturate drive-previous to +/-7FFFFFFF, divide by low16 divisor if nonzero, saturating-add
   previous, then floor0. Zero divisor uses the whole error, not hold. Symmetric saturating signed
   error and addition surround low16-divisor truncation; zero divisor uses undivided error. Final
   state floors at0. */

int f33_update_nonnegative_thermal_pole(int previous,int drive,uint divisor)

{
  int iVar1;
  uint uVar2;
  int local_c;
  int iStack_8;
  
  uVar2 = divisor & 0xffff;
  if (drive < 0) {
    if ((-1 < previous) &&
       (iVar1 = (drive + 0x7fffffff) - previous,
       iVar1 < 0 != (drive + 0x7fffffff < 0 != previous < 0 && previous < 0 == iVar1 < 0))) {
      local_c = -0x7fffffff;
      goto LAB_00039472;
    }
  }
  else if ((previous < 0) &&
          (iVar1 = -(0x7fffffff - drive),
          iVar1 - previous < 0 ==
          (iVar1 < 0 != previous < 0 && previous < 0 == iVar1 - previous < 0) && iVar1 != previous))
  {
    local_c = 0x7fffffff;
    goto LAB_00039472;
  }
  local_c = drive - previous;
LAB_00039472:
  if ((uVar2 != 0) && (uVar2 != 0)) {
    if (local_c == -0x80000000 && uVar2 == 0xffffffff) {
      local_c = -0x80000000;
    }
    else {
      local_c = local_c / (int)uVar2;
    }
  }
  FUN_00070674(previous,local_c,&local_c);
  FUN_00070152(local_c,0,&iStack_8);
  return iStack_8;
}



/* WARNING: Removing unreachable block (ram,0x000394fe) */
/* WARNING: Removing unreachable block (ram,0x000394a4) */
/* Signed state/128, symmetric saturating32 multiply by gain, signed /4096, then upper/lower clamp
   and sign-extended16 result. Preserve both truncation stages. Signed state/128 then saturating
   multiply by signed16 gain and division4096; signed16 bounds and sign-extended return. Do not
   merge truncation stages. */

int f33_scale_thermal_contribution(int state,short gain,short upper,short lower)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  uint uVar6;
  
  iVar3 = (int)gain;
  iVar4 = (int)upper;
  iVar5 = (int)lower;
  iVar2 = state / 0x80;
  if ((iVar2 == 0) || (iVar3 == 0)) {
    uVar6 = 0;
    goto LAB_000394fa;
  }
  if (iVar2 < 0) {
    if (-1 < iVar3) goto LAB_000394dc;
  }
  else if (iVar3 < 0) {
LAB_000394dc:
    iVar1 = (int)((ulonglong)((longlong)iVar3 * (longlong)iVar2) >> 0x20) + 1;
    if ((iVar1 < 0 != (-1 < (longlong)iVar3 * (longlong)iVar2 && iVar1 < 0)) ||
       (uVar6 = iVar2 * iVar3, uVar6 < 0x80000001)) {
      uVar6 = 0x80000001;
    }
    goto LAB_000394fa;
  }
  if ((-1 < (longlong)iVar3 * (longlong)iVar2 &&
       (int)((ulonglong)((longlong)iVar3 * (longlong)iVar2) >> 0x20) != 0) ||
     (uVar6 = iVar2 * iVar3, 0x7fffffff < (uint)(iVar2 * iVar3))) {
    uVar6 = 0x7fffffff;
  }
LAB_000394fa:
  iVar2 = (int)uVar6 / 0x1000;
  if (iVar2 - iVar4 < 0 != (iVar2 < 0 != iVar4 < 0 && iVar4 < 0 == iVar2 - iVar4 < 0) ||
      iVar2 == iVar4) {
    iVar4 = iVar2;
  }
  if (iVar4 - iVar5 < 0 == (iVar4 < 0 != iVar5 < 0 && iVar5 < 0 == iVar4 - iVar5 < 0)) {
    lower = (short)iVar4;
  }
  return (int)lower;
}



/* Nonzero7071 admits56-byte family0 record6. Marker5AA5 if7BF8!=0, otherwise FFFF iff6FB0A5, else0.
   Cache6F00/02 into6EE6/8. Ignore setter acceptance and arm6EE4=1. Nonzero7071 stages56-byte
   record6; marker chooses5AA5/FFFF/0 from7BF8 and6FB0. Cache maxima and arm6EE4 even when setter
   rejects. */

void f33_publish_thermal_history_record(void)

{
  uint32_t puVar1;
  undefined2 local_3c;
  undefined2 uStack_3a;
  undefined2 uStack_38;
  undefined2 uStack_36;
  undefined2 uStack_34;
  undefined2 uStack_32;
  undefined2 uStack_30;
  undefined2 uStack_2e;
  undefined2 uStack_2c;
  undefined2 uStack_2a;
  undefined2 uStack_28;
  undefined2 uStack_26;
  undefined2 uStack_24;
  undefined2 uStack_22;
  undefined2 uStack_20;
  undefined2 uStack_1e;
  undefined2 uStack_1c;
  undefined2 uStack_1a;
  undefined2 uStack_18;
  undefined2 uStack_16;
  undefined2 uStack_14;
  undefined2 uStack_12;
  undefined4 uStack_10;
  undefined2 uStack_c;
  undefined2 uStack_a;
  undefined2 uStack_8;
  undefined2 uStack_6;
  
  puVar1 = 0xfebeb800u;
  if (DAT_febe7071 != '\0') {
    local_3c = DAT_febe6f8e;
    uStack_10 = 0;
    uStack_3a = DAT_febe6f90;
    uStack_38 = DAT_febe6f9e;
    uStack_36 = DAT_febe6fa0;
    uStack_34 = DAT_febe6f42;
    uStack_32 = DAT_febe6f44;
    uStack_30 = DAT_febe6f56;
    uStack_2e = DAT_febe6f58;
    uStack_2c = DAT_febe6f16;
    uStack_2a = DAT_febe6f18;
    uStack_24 = DAT_febe6eb2;
    uStack_22 = DAT_febe6eb4;
    uStack_20 = DAT_febe6eb6;
    uStack_1e = DAT_febe6eb8;
    uStack_1c = DAT_febe6eba;
    uStack_1a = DAT_febe6ebc;
    uStack_18 = DAT_febe6ff0;
    uStack_16 = DAT_febe6ff2;
    uStack_14 = DAT_febe7000;
    uStack_12 = DAT_febe7002;
    uStack_28 = DAT_febe707c;
    uStack_26 = DAT_febe707a;
    uStack_c = DAT_febee8ac;
    if (DAT_febe7bf8 == 0) {
      if (f33_thermal_history_qualification[0] == 0xa5) {
        uStack_a = 0xffff;
      }
      else {
        uStack_a = 0;
      }
    }
    else {
      uStack_a = 0x5aa5;
    }
    uStack_8 = DAT_febe6f00;
    uStack_6 = DAT_febe6f02;
    DAT_febe6ee6 = DAT_febe6f00;
    DAT_febe6ee8 = DAT_febe6f02;
    f33_nvm_set_record(6,(uint *)&local_3c);
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb6e4u + (uint32_t)((int)puVar1) * 1u)))) = 1;
  }
  return;
}



/* Clear model contributions/poles, offset poles and drive maxima, not every published limit or
   initialization marker. Publish zero terms, ancillary7F80 and marker0; clear6EE6/8, ignore setter
   acceptance and arm6EE4=1. Clear model contributions/poles, offset poles and drive maxima; publish
   zero record6 with ancillary7F80/marker0 and arm tracker, ignoring acceptance. Published
   limits/init markers are not all reset. */

void f33_reset_thermal_models_and_history_record(void)

{
  uint32_t puVar1;
  undefined2 local_40;
  undefined2 uStack_3e;
  undefined2 uStack_3c;
  undefined2 uStack_3a;
  undefined2 uStack_38;
  undefined2 uStack_36;
  undefined2 uStack_34;
  undefined2 uStack_32;
  undefined2 uStack_30;
  undefined2 uStack_2e;
  undefined2 uStack_2c;
  undefined2 uStack_2a;
  undefined2 uStack_28;
  undefined2 uStack_26;
  undefined2 uStack_24;
  undefined2 uStack_22;
  undefined2 uStack_20;
  undefined2 uStack_1e;
  undefined2 uStack_1c;
  undefined2 uStack_1a;
  undefined2 uStack_18;
  undefined2 uStack_16;
  undefined4 uStack_14;
  undefined2 uStack_10;
  undefined2 uStack_e;
  undefined2 uStack_c;
  undefined2 uStack_a;
  
  puVar1 = 0xfebeb800u;
  FUN_0003a84e();
  FUN_0003a844();
  FUN_0003a990();
  FUN_0003a986();
  FUN_00039ba2();
  FUN_0003a25c();
  FUN_00039ffa();
  FUN_0003ba84();
  f33_fill_constant_block_39372();
  FUN_0003afc0();
  FUN_0003b0d8();
  uStack_14 = 0;
  uStack_e = 0;
  uStack_10 = 0x7f80;
  uStack_2a = 0;
  uStack_2c = 0;
  uStack_16 = 0;
  uStack_18 = 0;
  uStack_1a = 0;
  uStack_1c = 0;
  uStack_1e = 0;
  uStack_20 = 0;
  uStack_22 = 0;
  uStack_24 = 0;
  uStack_26 = 0;
  uStack_28 = 0;
  uStack_2e = 0;
  uStack_30 = 0;
  uStack_32 = 0;
  uStack_34 = 0;
  uStack_36 = 0;
  uStack_38 = 0;
  uStack_3a = 0;
  uStack_3c = 0;
  uStack_3e = 0;
  local_40 = 0;
  f33_fill_constant_block_398fa();
  uStack_a = 0;
  uStack_c = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb6e8u + (uint32_t)((int)puVar1)))))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb6e6u + (uint32_t)((int)puVar1)))))) = 0;
  f33_nvm_set_record(6,(uint *)&local_40);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb6e4u + (uint32_t)((int)puVar1) * 1u)))) = 1;
  return;
}



/* Publish ROM default terms, ancillary7F80 and rejecting markerA55A while retaining cached6EE6/8
   maxima. Ignore setter acceptance; unlike normal/clear publication do not arm6EE4. Publish ROM
   defaults with A55A rejecting marker and7F80 ancillary value, retain cached maxima, ignore setter
   acceptance and leave tracker unchanged. */

void f33_invalidate_thermal_history_record(void)

{
  undefined2 local_3c;
  undefined2 uStack_3a;
  undefined2 uStack_38;
  undefined2 uStack_36;
  undefined2 uStack_34;
  undefined2 uStack_32;
  undefined2 uStack_30;
  undefined2 uStack_2e;
  undefined2 uStack_2c;
  undefined2 uStack_2a;
  undefined2 uStack_28;
  undefined2 uStack_26;
  undefined2 uStack_24;
  undefined2 uStack_22;
  undefined2 uStack_20;
  undefined2 uStack_1e;
  undefined2 uStack_1c;
  undefined2 uStack_1a;
  undefined2 uStack_18;
  undefined2 uStack_16;
  undefined2 uStack_14;
  undefined2 uStack_12;
  undefined4 uStack_10;
  undefined2 uStack_c;
  undefined2 uStack_a;
  undefined2 uStack_8;
  undefined2 uStack_6;
  
  uStack_38 = DAT_0002b4b6;
  uStack_3a = DAT_0002b4b4;
  uStack_36 = DAT_0002b4b4;
  local_3c = DAT_0002b4b6;
  uStack_34 = DAT_0002b39e;
  uStack_32 = DAT_0002b3a0;
  uStack_30 = DAT_0002b3ba;
  uStack_2e = DAT_0002b3bc;
  uStack_2c = DAT_0002b31e;
  uStack_2a = DAT_0002b320;
  uStack_24 = DAT_0002b2a6;
  uStack_22 = DAT_0002b2a8;
  uStack_20 = DAT_0002b2aa;
  uStack_1e = DAT_0002b2ac;
  uStack_1c = DAT_0002b2ae;
  uStack_1a = DAT_0002b2b0;
  uStack_18 = DAT_0002b532;
  uStack_10 = 0;
  uStack_16 = DAT_0002b534;
  uStack_14 = DAT_0002b54a;
  uStack_12 = DAT_0002b54c;
  uStack_28 = DAT_0002b5b2;
  uStack_26 = DAT_0002b5b0;
  uStack_c = 0x7f80;
  uStack_a = 0xa55a;
  uStack_8 = DAT_febe6ee6;
  uStack_6 = DAT_febe6ee8;
  f33_nvm_set_record(6,(uint *)&local_3c);
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_39756(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_39758(void)

{
  return;
}



/* WARNING: Removing unreachable block (ram,0x00039762) */

int FUN_0003975a(short param_1,short param_2)

{
  return ((int)param_2 * (int)param_1) / 0x3000;
}



void FUN_00039768(void)

{
  uint32_t puVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  int local_28;
  int iStack_24;
  
  puVar1 = 0xfebeb800u;
  iVar8 = (int)DAT_febe65b2;
  iVar7 = (int)DAT_febe65b4;
  iVar6 = (int)DAT_febe65b6;
  iVar5 = (int)DAT_febe66e8;
  iVar4 = (int)DAT_febe66ea;
  iVar3 = (int)DAT_febe66ec;
  iVar2 = FUN_0003975a((int)DAT_febe65b0,(int)DAT_febe66e6);
  iVar5 = FUN_0003975a(iVar8,iVar5);
  FUN_0007012a(iVar5 + iVar2,0x4000,0xffffc000,&local_28);
  iVar2 = FUN_0003975a(iVar7,iVar4);
  iVar5 = FUN_0003975a(iVar6,iVar3);
  FUN_0007012a(iVar5 + iVar2,0x4000,0xffffc000,&iStack_24);
  (*((short *)camry_host_ptr((uint32_t)((0xffffb6eeu + (uint32_t)((int)puVar1)))))) = (short)iStack_24;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb6ecu + (uint32_t)((int)puVar1)))))) = (short)local_28;
  (*((int *)camry_host_ptr((uint32_t)((0xffffb6fcu + (uint32_t)((int)puVar1)))))) = iStack_24 + local_28;
  return;
}



/* Low32 squares of32-bit6EFC and signed16 6EEC/6EEE, then signed calibration bounds,
   publish6EF0/6EF4/6EF8. Do not replace low32 multiplication by an unbounded mathematical square.
   Low32 squares of staged32-bit6EFC and signed16 6EEC/6EEE pass signed bounds into6EF0/6EF4/6EF8.
   Acquisition freshness remains upstream. */

void f33_stage_ecu_thermal_squared_inputs(void)

{
  uint32_t puVar1;
  int iVar2;
  int iVar3;
  undefined4 local_1c;
  undefined4 uStack_18;
  undefined4 uStack_14;
  
  puVar1 = 0xfebeb800u;
  iVar2 = (int)DAT_febe6eee;
  iVar3 = (int)DAT_febe6eec;
  FUN_0007012a(DAT_febe6efc * DAT_febe6efc,DAT_0002b2f0,DAT_0002b2f4,&local_1c);
  FUN_0007012a(iVar3 * iVar3,DAT_0002b2f8,DAT_0002b2fc,&uStack_18);
  FUN_0007012a(iVar2 * iVar2,DAT_0002b300,DAT_0002b304,&uStack_14);
  (*((undefined4 *)camry_host_ptr((uint32_t)((0xffffb6f0u + (uint32_t)((int)puVar1)))))) = local_1c;
  (*((undefined4 *)camry_host_ptr((uint32_t)((0xffffb6f4u + (uint32_t)((int)puVar1)))))) = uStack_18;
  (*((undefined4 *)camry_host_ptr((uint32_t)((0xffffb6f8u + (uint32_t)((int)puVar1)))))) = uStack_14;
  return;
}



void FUN_0003984a(void)

{
  FUN_00039768();
  f33_stage_ecu_thermal_squared_inputs();
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_3985a(void)

{
  return;
}



/* Copy record6, accept tail+34/+36 on exact status10 WITHOUT checking markerA55A. Otherwise clear
   both restored maxima6F06/08. Separate from model-term validity. Restore record6 tail maxima on
   exact10 without markerA55A rejection; otherwise clear pair. History admission differs from model
   terms. */

void f33_restore_thermal_drive_epoch_maxima(void)

{
  uint *puVar1;
  uint32_t puVar2;
  uint uVar3;
  undefined4 uVar4;
  undefined4 *puVar5;
  uint local_3c [13];
  undefined2 uStack_8;
  undefined2 uStack_6;
  
  puVar2 = 0xfebeb800u;
  puVar1 = local_3c;
  puVar5 = ((undefined *)camry_host_ptr(0x21140u));
  do {
    uVar4 = *puVar5;
    puVar5 = puVar5 + 1;
    *puVar1 = uVar4;
    puVar1 = puVar1 + 1;
  } while ((uintptr_t)(puVar5)!=(uintptr_t)(((undefined *)camry_host_ptr(0x21178u))));
  uVar3 = f33_nvm_get_record(6, camry_host_addr(local_3c));
  if (uVar3 == 0x10) {
    (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb706u + (uint32_t)((int)puVar2)))))) = uStack_8;
  }
  else {
    (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb706u + (uint32_t)((int)puVar2)))))) = 0;
    uStack_6 = 0;
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb708u + (uint32_t)((int)puVar2)))))) = uStack_6;
  return;
}



/* Filter70B0 with divisor30000/gain25, clamp contribution0..32767 and retain run maximum6F04. Merge
   that one maximum with restored6F06/08 into6F00/02; ties permitted. Do not feed current outputs
   back into the restored pair. Filter70B0 with30000 divisor/25 gain, retain current-run maximum,
   merge with restored pair into two maxima without feeding outputs back into restored pair; ties
   allowed. */

void f33_update_thermal_drive_epoch_maxima(void)

{
  bool bVar1;
  bool bVar2;
  short sVar3;
  short sVar4;
  uint32_t puVar5;
  int state;
  int iVar6;
  int iVar7;
  int iVar8;
  short sVar9;
  int iVar10;
  
  sVar3 = DAT_febe6f08;
  sVar4 = DAT_febe6f06;
  sVar9 = DAT_0002b30a;
  puVar5 = 0xfebeb800u;
  iVar8 = (int)DAT_febe6f06;
  iVar7 = (int)DAT_febe6f08;
  iVar10 = (int)DAT_febe6f04;
  state = f33_update_nonnegative_thermal_pole(DAT_febe6f0c,DAT_febe70b0,(uint)DAT_0002b308);
  iVar6 = f33_scale_thermal_contribution(state,sVar9,0x7fff,0);
  if (iVar10 - iVar6 < 0 == (iVar10 < 0 != iVar6 < 0 && iVar6 < 0 == iVar10 - iVar6 < 0) &&
      iVar10 != iVar6) {
    iVar6 = iVar10;
  }
  sVar9 = (short)iVar6;
  if ((iVar6 - iVar8 < 0 != (iVar6 < 0 != iVar8 < 0 && iVar8 < 0 == iVar6 - iVar8 < 0) ||
       iVar6 == iVar8) &&
     (iVar10 = iVar6 - iVar7, bVar2 = iVar6 < 0, bVar1 = iVar6 != iVar7, iVar6 = iVar8,
     sVar4 = sVar3, iVar10 < 0 == (bVar2 != iVar7 < 0 && iVar7 < 0 == iVar10 < 0) && bVar1)) {
    sVar4 = sVar9;
  }
  (*((int *)camry_host_ptr((uint32_t)((0xffffb70cu + (uint32_t)((int)puVar5)))))) = state;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb700u + (uint32_t)((int)puVar5)))))) = (short)iVar6;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb702u + (uint32_t)((int)puVar5)))))) = sVar4;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb704u + (uint32_t)((int)puVar5)))))) = sVar9;
  return;
}



/* Constant-block fill: 6 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_398fa(void)

{
  DAT_febe6f06 = 0;
  DAT_febe6f08 = 0;
  DAT_febe6f0c = 0;
  DAT_febe6f00 = 0;
  DAT_febe6f02 = 0;
  DAT_febe6f04 = 0;
  return;
}



void FUN_0003990c(void)

{
  DAT_febe6f06 = 0;
  DAT_febe6f08 = 0;
  DAT_febe6f00 = 0;
  DAT_febe6f02 = 0;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_3991a(void)

{
  return;
}



void FUN_0003991c(void)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  iVar2 = FUN_000588b6();
  if (iVar2 == 0) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb710u + (uint32_t)((int)puVar1) * 1u)))) = 0;
  }
  return;
}



/* Same strict32000/marker0/source-byte selection; selected difference histories6F28/6F2C. Source4
   matching conditional-zero predicate retains the unselected history and requires strict32000 plus
   marker0. */

uint f33_should_zero_ecu_source4_thermal_seed(ushort record_marker)

{
  int iVar1;
  uint uVar2;
  
  if ((DAT_febe7bf8 & 0xff) == 0) {
    if ((DAT_febe7bf8 & 0xff00) != 0) {
      DAT_febe6f28 = (int)DAT_febe7dd0 - (int)DAT_febe7dce;
      iVar1 = DAT_febe6f28;
      goto LAB_00039978;
    }
  }
  else if ((DAT_febe7bf8 & 0xff00) == 0) {
    DAT_febe6f2c = (int)DAT_febe7dd8 - (int)DAT_febe7dd6;
    iVar1 = DAT_febe6f2c;
    goto LAB_00039978;
  }
  DAT_febe6f28 = (int)DAT_febe7dd0 - (int)DAT_febe7dce;
  DAT_febe6f2c = (int)DAT_febe7dd8 - (int)DAT_febe7dd6;
  iVar1 = DAT_febe6f28;
  if (DAT_febe6f2c - DAT_febe6f28 < 0 !=
      (DAT_febe6f2c < 0 != DAT_febe6f28 < 0 && DAT_febe6f28 < 0 == DAT_febe6f2c - DAT_febe6f28 < 0))
  {
    iVar1 = DAT_febe6f2c;
  }
LAB_00039978:
  if ((iVar1 - DAT_0002b328 < 0 ==
       (iVar1 < 0 != DAT_0002b328 < 0 && DAT_0002b328 < 0 == iVar1 - DAT_0002b328 < 0) &&
       iVar1 != DAT_0002b328) && (record_marker == 0)) {
    uVar2 = 0x5a;
  }
  else {
    uVar2 = 0;
  }
  return uVar2;
}



int FUN_00039996(short param_1,short param_2)

{
  int iVar1;
  int iVar2;
  
  iVar2 = (int)param_2;
  if (iVar2 == 0) {
    return 0;
  }
  iVar1 = (int)param_1 << 0xc;
  if (iVar2 != 0) {
    if (iVar1 == -0x80000000 && iVar2 == -1) {
      iVar1 = -0x80000000;
    }
    else {
      iVar1 = iVar1 / iVar2;
    }
  }
  if (iVar1 < 0) {
    iVar2 = (int)((ulonglong)((longlong)iVar1 * 0x80) >> 0x20) + 1;
    if ((iVar2 < 0 != (-1 < (longlong)iVar1 * 0x80 && iVar2 < 0)) ||
       ((uint)(iVar1 * 0x80) < 0x80000001)) {
      return -0x7fffffff;
    }
  }
  else {
    if (iVar1 == 0) {
      return 0;
    }
    if ((-1 < (longlong)iVar1 * 0x80 && (int)((ulonglong)((longlong)iVar1 * 0x80) >> 0x20) != 0) ||
       (0x7fffffff < (uint)(iVar1 * 0x80))) {
      return 0x7fffffff;
    }
  }
  return iVar1 * 0x80;
}



void FUN_000399e6(short param_1,short param_2)

{
  uint32_t puVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  
  puVar1 = 0xfebeb800u;
  uVar2 = FUN_00039996((int)param_1,(int)DAT_0002b310);
  uVar3 = FUN_00039996((int)param_2,(int)DAT_0002b312);
  (*((undefined4 *)camry_host_ptr((uint32_t)((0xffffb720u + (uint32_t)((int)puVar1)))))) = uVar2;
  (*((undefined4 *)camry_host_ptr((uint32_t)((0xffffb724u + (uint32_t)((int)puVar1)))))) = uVar3;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb712u + (uint32_t)((int)puVar1)))))) = 0x3480;
  return;
}



/* Record6 terms10/12 and common marker32/conditional-zero contract. Rejection uses zero defaults.
   Exact gains0/0 seed both poles0 even with nonzero saved contributions. Source4 reads terms10/12
   and common marker32; rejected records use zeros. Exact zero gains seed zero poles even when saved
   contributions are nonzero. */

void f33_restore_ecu_source4_thermal_model(void)

{
  uint *puVar1;
  uint32_t puVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  undefined4 uVar6;
  undefined4 *puVar7;
  uint local_3c [4];
  short sStack_2c;
  short sStack_2a;
  ushort uStack_a;
  
  puVar2 = 0xfebeb800u;
  puVar1 = local_3c;
  puVar7 = ((undefined *)camry_host_ptr(0x21178u));
  do {
    uVar6 = *puVar7;
    puVar7 = puVar7 + 1;
    *puVar1 = uVar6;
    puVar1 = puVar1 + 1;
  } while ((uintptr_t)(puVar7)!=(uintptr_t)(((undefined *)camry_host_ptr(0x211b0u))));
  uVar5 = f33_nvm_get_record(6, camry_host_addr(local_3c));
  if ((uVar5 == 0x10) && (uStack_a != 0xa55a)) {
    if ((((((*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x3c08)))) & 0xff) == 0) ||
         (((*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x3c08)))) & 0xff00) == 0)) && (uStack_a != 0x5aa5)) &&
       (uVar5 = f33_should_zero_ecu_source4_thermal_seed(uStack_a), uVar5 == 0x5a)) {
      iVar3 = 0;
      iVar4 = 0;
    }
    else {
      iVar3 = (int)sStack_2c;
      iVar4 = (int)sStack_2a;
    }
  }
  else {
    iVar3 = (int)DAT_0002b31e;
    iVar4 = (int)DAT_0002b320;
  }
  FUN_000399e6(iVar3,iVar4);
  return;
}



/* Drive70B0 updates two poles with exact divisors1/1. High-load scale1536 truncates these divisors
   back to1. Gains0/0 leave raw bias1536; selector2 adds offset source index1 and optional
   following. Return adjusted estimate inR10, not void. Drive70B0 advances two poles with divisors1
   and zero gains. High-load scale still truncates both divisors to1; selector2 adds offset source1
   and real signed R10 reaches parent publication. */

int f33_calculate_ecu_source4_thermal_estimate(void)

{
  short upper;
  short lower;
  short previous;
  int iVar1;
  uint32_t puVar2;
  uint divisor;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  uint uVar7;
  int iVar8;
  int iVar9;
  
  iVar9 = DAT_febe70b0;
  iVar8 = DAT_febe6f24;
  iVar5 = DAT_febe6f20;
  previous = DAT_febe6f12;
  puVar2 = 0xfebeb800u;
  iVar1 = (int)DAT_febe64e2;
  iVar6 = (int)DAT_0002b31c;
  if (iVar1 + 0x7fff < 0 == (-1 < iVar1 && iVar1 + 0x7fff < 0) && iVar1 != -0x7fff) {
    if (iVar1 < 0) {
      iVar1 = (int)-DAT_febe64e2;
    }
  }
  else {
    iVar1 = 0x7fff;
  }
  if ((iVar1 - iVar6 < 0 == (iVar1 < 0 != iVar6 < 0 && iVar6 < 0 == iVar1 - iVar6 < 0) &&
       iVar1 != iVar6) &&
     (DAT_febe70b0 - DAT_0002b324 < 0 ==
      (DAT_febe70b0 < 0 != DAT_0002b324 < 0 && DAT_0002b324 < 0 == DAT_febe70b0 - DAT_0002b324 < 0)
      && DAT_febe70b0 != DAT_0002b324)) {
    uVar7 = (uint)DAT_0002b31a;
    puVar2 = 0xfebeb800u;
    divisor = f33_scale_thermal_divisor((uint)DAT_0002b316,uVar7);
    uVar7 = f33_scale_thermal_divisor((uint)DAT_0002b318,uVar7);
  }
  else {
    divisor = (uint)DAT_0002b316;
    uVar7 = (uint)DAT_0002b318;
  }
  iVar1 = f33_update_nonnegative_thermal_pole(iVar5,iVar9,divisor);
  iVar6 = f33_update_nonnegative_thermal_pole(iVar8,iVar9,uVar7);
  lower = DAT_0002b30e;
  upper = DAT_0002b30c;
  iVar9 = (int)DAT_0002b30c;
  iVar8 = (int)DAT_0002b30e;
  iVar3 = f33_scale_thermal_contribution(iVar1,DAT_0002b310,DAT_0002b30c,DAT_0002b30e);
  iVar4 = f33_scale_thermal_contribution(iVar6,DAT_0002b312,upper,lower);
  iVar5 = (int)DAT_0002b314 + iVar3 + iVar4;
  if (iVar5 - iVar9 < 0 != (iVar5 < 0 != iVar9 < 0 && iVar9 < 0 == iVar5 - iVar9 < 0) ||
      iVar5 == iVar9) {
    iVar9 = iVar5;
  }
  if (iVar9 - iVar8 < 0 == (iVar9 < 0 != iVar8 < 0 && iVar8 < 0 == iVar9 - iVar8 < 0)) {
    iVar8 = iVar9;
  }
  iVar5 = f33_apply_thermal_offset_and_following(2,(short)iVar8,previous);
  (*((short *)camry_host_ptr((uint32_t)((0xffffb714u + (uint32_t)((int)puVar2)))))) = (short)iVar8;
  (*((int *)camry_host_ptr((uint32_t)((0xffffb724u + (uint32_t)((int)puVar2)))))) = iVar6;
  (*((int *)camry_host_ptr((uint32_t)((0xffffb720u + (uint32_t)((int)puVar2)))))) = iVar1;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb71au + (uint32_t)((int)puVar2)))))) = (short)divisor;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb71cu + (uint32_t)((int)puVar2)))))) = (short)uVar7;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb716u + (uint32_t)((int)puVar2)))))) = (short)iVar3;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb718u + (uint32_t)((int)puVar2)))))) = (short)iVar4;
  return iVar5;
}



/* Only zero6F10 requires7DCC/7BF6 both5A and39A1C restoration. Then calculate adjusted estimate and
   store real signedR10 low16 at6F12; nonzero marker bypasses initialization gates. Source4
   initialized model updates despite absent initial validity markers. Zero contribution gains still
   leave bias1536 plus selected offset feeding nonflat current maps. */

void f33_update_ecu_source4_thermal_estimate(void)

{
  undefined *puVar1;
  undefined *puVar2;
  int iVar4;
  char cVar5;
  uint32_t puVar3;
  puVar3 = 0xfebeb800u;
  puVar2 = ((undefined *)camry_host_ptr(0xfebeb800u));
  cVar5 = DAT_febe6f10;
  puVar1 = ((undefined *)camry_host_ptr(0xfebeb800u));
  if (DAT_febe6f10 == '\0') {
    if ((DAT_febe7dcc != 'Z') || (DAT_febe7bf6 != 'Z')) goto LAB_00039b9a;
    f33_restore_ecu_source4_thermal_model();
    cVar5 = 'Z';
    puVar1 = ((undefined *)camry_host_ptr((uint32_t)(puVar3)));
  }
  puVar2 = puVar1;
  iVar4 = f33_calculate_ecu_source4_thermal_estimate();
  *(short *)(((undefined *)camry_host_ptr(0xffffb712u)) + (int)camry_host_addr(puVar2)) = (short)iVar4;
LAB_00039b9a:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb710u + (uint32_t)((int)camry_host_addr(puVar2)) * 1u)))) = cVar5;
  return;
}



void FUN_00039ba2(void)

{
  DAT_febe6f16 = 0;
  DAT_febe6f18 = 0;
  DAT_febe6f20 = 0;
  DAT_febe6f24 = 0;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_39bb0(void)

{
  return;
}



/* Paired constant publisher: DAT_febe6f30 = 0x569a; and DAT_febe6f32 = 0x2b4d;; shape-classified
   from the canonical corpus. Target cells not yet named. */

void FUN_00039bb2(void)

{
  DAT_febe6f30 = 0x569a;
  DAT_febe6f32 = 0x2b4d;
  return;
}



/* Signed6F12 selects2B32C/2B348 into6F30/6F32. Bank0 reaches5542 at16512 and bank1 reaches0
   at16628. Zero pole gains do not disable this offset-driven derating path. Source4 maps are active
   despite zero pole gains; bank0 reaches5542 at16512 and bank1 zero at16628. */

void f33_publish_ecu_source4_thermal_limit_maps(void)

{
  uint32_t puVar1;
  int iVar2;
  undefined2 local_c;
  undefined2 uStack_a;
  
  puVar1 = 0xfebeb800u;
  iVar2 = (int)DAT_febe6f12;
  FUN_0007025c(f33_ecu_source4_current_curve_bank0,iVar2,&local_c);
  FUN_0007025c(f33_ecu_source4_current_curve_bank1,iVar2,&uStack_a);
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb730u + (uint32_t)((int)puVar1)))))) = local_c;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb732u + (uint32_t)((int)puVar1)))))) = uStack_a;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_39bfc(void)

{
  return;
}



void FUN_00039bfe(void)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  iVar2 = FUN_000588b6();
  if (iVar2 == 0) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb734u + (uint32_t)((int)puVar1) * 1u)))) = 0;
  }
  return;
}



/* Return5A only for marker0 and selected signed difference>32000. 7BF8 low0/high nonzero
   selects7DD0-7DCE; low nonzero/high0 selects7DD8-7DD6; otherwise use minimum. Update
   selected6F38/6F3C histories; retain an unselected history. Source2 conditional zero predicate
   selects signed difference by7BF8 bytes and requires marker0 plus difference>32000. Update
   selected histories only; equality retains terms. */

uint f33_should_zero_ecu_source2_thermal_seed(ushort record_marker)

{
  int iVar1;
  uint uVar2;
  
  if ((DAT_febe7bf8 & 0xff) == 0) {
    if ((DAT_febe7bf8 & 0xff00) != 0) {
      DAT_febe6f38 = (int)DAT_febe7dd0 - (int)DAT_febe7dce;
      iVar1 = DAT_febe6f38;
      goto LAB_00039c5a;
    }
  }
  else if ((DAT_febe7bf8 & 0xff00) == 0) {
    DAT_febe6f3c = (int)DAT_febe7dd8 - (int)DAT_febe7dd6;
    iVar1 = DAT_febe6f3c;
    goto LAB_00039c5a;
  }
  DAT_febe6f38 = (int)DAT_febe7dd0 - (int)DAT_febe7dce;
  DAT_febe6f3c = (int)DAT_febe7dd8 - (int)DAT_febe7dd6;
  iVar1 = DAT_febe6f38;
  if (DAT_febe6f3c - DAT_febe6f38 < 0 !=
      (DAT_febe6f3c < 0 != DAT_febe6f38 < 0 && DAT_febe6f38 < 0 == DAT_febe6f3c - DAT_febe6f38 < 0))
  {
    iVar1 = DAT_febe6f3c;
  }
LAB_00039c5a:
  if ((iVar1 - DAT_0002b368 < 0 ==
       (iVar1 < 0 != DAT_0002b368 < 0 && DAT_0002b368 < 0 == iVar1 - DAT_0002b368 < 0) &&
       iVar1 != DAT_0002b368) && (record_marker == 0)) {
    uVar2 = 0x5a;
  }
  else {
    uVar2 = 0;
  }
  return uVar2;
}



/* Record6 terms08/0A/0C/0E, marker32. Exact status10 and marker!=A55A admit saved terms,
   conditionally zeroed for marker0/selected difference>32000 with a zero7BF8 byte. Rejected record
   uses3390/222 per branch. 6764&3 chooses initial gains and6F35; seed poles from
   contribution*4096/gain then saturating multiply128. Restore source2 contributions from shared
   record6 RAM mirror before status admission; marker0/difference32000 retains and32001 zeros terms.
   Gain-dependent pole seeding then feeds both branch updates. */

void f33_restore_ecu_source2_thermal_model(void)

{
  ushort uVar1;
  uint *puVar2;
  uint32_t puVar3;
  int iVar4;
  int iVar5;
  uint uVar6;
  undefined4 uVar7;
  int iVar8;
  int iVar9;
  undefined1 uVar10;
  undefined4 *puVar11;
  uint local_4c [2];
  short sStack_44;
  short sStack_42;
  short sStack_40;
  short sStack_3e;
  ushort uStack_1a;
  
  uVar1 = DAT_febe6764;
  puVar3 = 0xfebeb800u;
  puVar2 = local_4c;
  puVar11 = ((undefined *)camry_host_ptr(0x211b0u));
  do {
    uVar7 = *puVar11;
    puVar11 = puVar11 + 1;
    *puVar2 = uVar7;
    puVar2 = puVar2 + 1;
  } while ((uintptr_t)(puVar11)!=(uintptr_t)(((undefined *)camry_host_ptr(0x211e8u))));
  uVar6 = f33_nvm_get_record(6, camry_host_addr(local_4c));
  if ((uVar6 == 0x10) && (uStack_1a != 0xa55a)) {
    if ((((((*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x3c08)))) & 0xff) == 0) ||
         (((*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x3c08)))) & 0xff00) == 0)) && (uStack_1a != 0x5aa5)) &&
       (uVar6 = f33_should_zero_ecu_source2_thermal_seed(uStack_1a), uVar6 == 0x5a)) {
      iVar4 = 0;
      iVar9 = 0;
      iVar5 = 0;
      iVar8 = 0;
    }
    else {
      iVar4 = (int)sStack_44;
      iVar9 = (int)sStack_40;
      iVar5 = (int)sStack_42;
      iVar8 = (int)sStack_3e;
    }
  }
  else {
    iVar4 = (int)DAT_0002b39e;
    iVar9 = (int)DAT_0002b3ba;
    iVar5 = (int)DAT_0002b3a0;
    iVar8 = (int)DAT_0002b3bc;
  }
  uVar10 = 0;
  if ((uVar1 & 3) != 0) {
    uVar10 = 0x5a;
  }
  FUN_00039efe(iVar4,iVar5,uVar10);
  FUN_0003a160(iVar9,iVar8,uVar10);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb735u + (uint32_t)((int)puVar3) * 1u)))) = uVar10;
  return;
}



/* Only zero6F34 requires7DCC/7BF6 both5A and record6 restoration. Initialized model continues
   without those validity gates. First6764&3!=0 with6F35==0 rebases both pole pairs and latches
   alternate gains5A; clearing6764 does not revert it. Publish signed branch maximum6F36. Source2
   first alternate-bank selection rebases both retained pole pairs and latches gains. Initialized
   updates bypass initial validity gates and publish signed branch maximum into real derating maps.
    */

void f33_update_ecu_source2_thermal_estimate(void)

{
  short upper;
  short lower;
  ushort uVar1;
  undefined2 uVar2;
  uint32_t puVar3;
  int iVar4;
  int iVar5;
  char cVar6;
  uchar alternate_gains;
  
  uVar1 = DAT_febe6764;
  puVar3 = 0xfebeb800u;
  cVar6 = DAT_febe6f34;
  if (((DAT_febe7dcc == 'Z') && (DAT_febe7bf6 == 'Z')) && (DAT_febe6f34 == '\0')) {
    puVar3 = 0xfebeb800u;
    f33_restore_ecu_source2_thermal_model();
    cVar6 = 'Z';
  }
  alternate_gains = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb735u + (uint32_t)((int)puVar3) * 1u))));
  if (cVar6 != '\0') {
    if (((uVar1 & 3) != 0) && (alternate_gains == '\0')) {
      f33_rebase_ecu_source2_thermal_branch0();
      f33_rebase_ecu_source2_thermal_branch1();
      alternate_gains = 'Z';
    }
    lower = DAT_0002b366;
    upper = DAT_0002b364;
    iVar4 = f33_update_ecu_source2_thermal_branch0(DAT_0002b364,DAT_0002b366,alternate_gains);
    iVar5 = f33_update_ecu_source2_thermal_branch1(upper,lower,alternate_gains);
    if (iVar5 - iVar4 < 0 == (iVar5 < 0 != iVar4 < 0 && iVar4 < 0 == iVar5 - iVar4 < 0) &&
        iVar5 != iVar4) {
      uVar2 = (undefined2)iVar5;
    }
    else {
      uVar2 = (undefined2)iVar4;
    }
    (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb736u + (uint32_t)((int)puVar3)))))) = uVar2;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb734u + (uint32_t)((int)puVar3) * 1u)))) = cVar6;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb735u + (uint32_t)((int)puVar3) * 1u)))) = alternate_gains;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_39da6(void)

{
  return;
}



/* Drive70B4 and poles6F4C/6F50; gains23/10 or54/6, bias512. Base divisors13/5000 scale1536 only
   when sat_abs16(64E2)>32 AND signed drive>1638400; otherwise unsigned speed map is flat1024.
   Selector0 offset/following returns signedR10 and stores6F40. Source2 branch0 uses70B4 and
   gains23/10 or54/6 with bias512. Strict amplitude/drive gate selects divisors19/7500;
   otherwise13/5000. Offset selector0 and signed R10 return are independent of map selection. */

int f33_update_ecu_source2_thermal_branch0(short upper,short lower,uchar alternate_gains)

{
  short gain;
  int iVar1;
  uint32_t puVar2;
  uint divisor;
  uint divisor_00;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  ushort local_30;
  short sStack_2e;
  short gain_00;
  
  iVar4 = DAT_febe70b4;
  iVar3 = DAT_febe6f50;
  iVar5 = DAT_febe6f4c;
  puVar2 = 0xfebeb800u;
  iVar7 = (int)lower;
  iVar8 = (int)upper;
  iVar1 = (int)DAT_febe64e2;
  sStack_2e = DAT_febe6f40;
  gain = DAT_0002b38e;
  gain_00 = DAT_0002b38c;
  if (alternate_gains != '\0') {
    gain = DAT_0002b392;
    gain_00 = DAT_0002b390;
  }
  if (iVar1 + 0x7fff < 0 == (-1 < iVar1 && iVar1 + 0x7fff < 0) && iVar1 != -0x7fff) {
    if (iVar1 < 0) {
      iVar1 = (int)-DAT_febe64e2;
    }
  }
  else {
    iVar1 = 0x7fff;
  }
  iVar6 = (int)DAT_0002b39c;
  if ((iVar1 - iVar6 < 0 == (iVar1 < 0 != iVar6 < 0 && iVar6 < 0 == iVar1 - iVar6 < 0) &&
       iVar1 != iVar6) &&
     (DAT_febe70b4 - DAT_0002b3a4 < 0 ==
      (DAT_febe70b4 < 0 != DAT_0002b3a4 < 0 && DAT_0002b3a4 < 0 == DAT_febe70b4 - DAT_0002b3a4 < 0)
      && DAT_febe70b4 != DAT_0002b3a4)) {
    local_30 = DAT_0002b39a;
  }
  else {
    puVar2 = 0xfebeb800u;
    FUN_00070304(((undefined *)camry_host_ptr(0x2b36cu)),DAT_febe668a & 0x7fff,&local_30);
  }
  divisor = f33_scale_thermal_divisor((uint)DAT_0002b396,(uint)local_30);
  divisor_00 = f33_scale_thermal_divisor((uint)DAT_0002b398,(uint)local_30);
  iVar1 = f33_update_nonnegative_thermal_pole(iVar5,iVar4,divisor);
  iVar3 = f33_update_nonnegative_thermal_pole(iVar3,iVar4,divisor_00);
  iVar4 = f33_scale_thermal_contribution(iVar1,gain_00,upper,lower);
  iVar6 = f33_scale_thermal_contribution(iVar3,gain,upper,lower);
  iVar5 = (int)DAT_0002b394 + iVar4 + iVar6;
  if (iVar5 - iVar8 < 0 != (iVar5 < 0 != iVar8 < 0 && iVar8 < 0 == iVar5 - iVar8 < 0) ||
      iVar5 == iVar8) {
    iVar8 = iVar5;
  }
  if (iVar8 - iVar7 < 0 == (iVar8 < 0 != iVar7 < 0 && iVar7 < 0 == iVar8 - iVar7 < 0)) {
    iVar7 = iVar8;
  }
  iVar5 = f33_apply_thermal_offset_and_following(0,(short)iVar7,sStack_2e);
  (*((short *)camry_host_ptr((uint32_t)((0xffffb74au + (uint32_t)((int)puVar2)))))) = (short)iVar7;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb740u + (uint32_t)((int)puVar2)))))) = (short)iVar5;
  (*((int *)camry_host_ptr((uint32_t)((0xffffb74cu + (uint32_t)((int)puVar2)))))) = iVar1;
  (*((int *)camry_host_ptr((uint32_t)((0xffffb750u + (uint32_t)((int)puVar2)))))) = iVar3;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb746u + (uint32_t)((int)puVar2)))))) = (short)divisor;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb748u + (uint32_t)((int)puVar2)))))) = (short)divisor_00;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb742u + (uint32_t)((int)puVar2)))))) = (short)iVar4;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb744u + (uint32_t)((int)puVar2)))))) = (short)iVar6;
  return iVar5;
}



int FUN_00039eae(short param_1,short param_2)

{
  int iVar1;
  int iVar2;
  
  iVar2 = (int)param_2;
  if (iVar2 == 0) {
    return 0;
  }
  iVar1 = (int)param_1 << 0xc;
  if (iVar2 != 0) {
    if (iVar1 == -0x80000000 && iVar2 == -1) {
      iVar1 = -0x80000000;
    }
    else {
      iVar1 = iVar1 / iVar2;
    }
  }
  if (iVar1 < 0) {
    iVar2 = (int)((ulonglong)((longlong)iVar1 * 0x80) >> 0x20) + 1;
    if ((iVar2 < 0 != (-1 < (longlong)iVar1 * 0x80 && iVar2 < 0)) ||
       ((uint)(iVar1 * 0x80) < 0x80000001)) {
      return -0x7fffffff;
    }
  }
  else {
    if (iVar1 == 0) {
      return 0;
    }
    if ((-1 < (longlong)iVar1 * 0x80 && (int)((ulonglong)((longlong)iVar1 * 0x80) >> 0x20) != 0) ||
       (0x7fffffff < (uint)(iVar1 * 0x80))) {
      return 0x7fffffff;
    }
  }
  return iVar1 * 0x80;
}



void FUN_00039efe(short param_1,short param_2,char param_3)

{
  short sVar1;
  uint32_t puVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  short sVar2;
  
  puVar3 = 0xfebeb800u;
  sVar1 = DAT_0002b38c;
  sVar2 = DAT_0002b38e;
  if (param_3 != '\0') {
    sVar1 = DAT_0002b390;
    sVar2 = DAT_0002b392;
  }
  uVar4 = FUN_00039eae((int)param_1,(int)sVar1);
  uVar5 = FUN_00039eae((int)param_2,(int)sVar2);
  (*((undefined4 *)camry_host_ptr((uint32_t)((0xffffb74cu + (uint32_t)((int)puVar3)))))) = uVar4;
  (*((undefined4 *)camry_host_ptr((uint32_t)((0xffffb750u + (uint32_t)((int)puVar3)))))) = uVar5;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb740u + (uint32_t)((int)puVar3)))))) = 0x3480;
  return;
}



/* WARNING: Removing unreachable block (ram,0x00039faa) */
/* WARNING: Removing unreachable block (ram,0x00039f5a) */
/* Convert each old pole by signed /2048, multiply old gain23/10, divide new54/6, then symmetric
   saturating32 multiply2048. Preserve staged truncation; not exact real-valued rescaling.
   Alternate-gain transition rebases source2 branch0 through separate /2048 multiply-old/divide-new
   and saturating multiply2048 stages; truncation is consequential. */

void f33_rebase_ecu_source2_thermal_branch0(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  iVar2 = 0x7fffffff;
  iVar4 = (int)DAT_0002b390;
  iVar3 = (int)DAT_0002b392;
  if (iVar4 == 0) {
LAB_00039f72:
    iVar2 = 0;
  }
  else {
    iVar1 = (DAT_febe6f4c / 0x800) * (int)DAT_0002b38c;
    if (iVar4 != 0) {
      if (iVar1 == -0x80000000 && iVar4 == -1) {
        iVar1 = -0x80000000;
      }
      else {
        iVar1 = iVar1 / iVar4;
      }
    }
    if (iVar1 < 0) {
      iVar2 = (int)((ulonglong)((longlong)iVar1 * 0x800) >> 0x20) + 1;
      if ((iVar2 < 0 != (-1 < (longlong)iVar1 * 0x800 && iVar2 < 0)) ||
         ((uint)(iVar1 * 0x800) < 0x80000001)) {
        iVar2 = -0x7fffffff;
        goto LAB_00039fa2;
      }
    }
    else {
      if (iVar1 == 0) goto LAB_00039f72;
      if ((-1 < (longlong)iVar1 * 0x800 && (int)((ulonglong)((longlong)iVar1 * 0x800) >> 0x20) != 0)
         || (0x7fffffff < (uint)(iVar1 * 0x800))) goto LAB_00039fa2;
    }
    iVar2 = iVar1 * 0x800;
  }
LAB_00039fa2:
  if (iVar3 != 0) {
    iVar4 = ((int)DAT_febe6f50 / 0x800) * (int)DAT_0002b38e;
    if (iVar3 != 0) {
      if (iVar4 == -0x80000000 && iVar3 == -1) {
        iVar4 = -0x80000000;
      }
      else {
        iVar4 = iVar4 / iVar3;
      }
    }
    if (iVar4 < 0) {
      iVar3 = (int)((ulonglong)((longlong)iVar4 * 0x800) >> 0x20) + 1;
      if ((iVar3 < 0 == (-1 < (longlong)iVar4 * 0x800 && iVar3 < 0)) &&
         (0x80000000 < (uint)(iVar4 * 0x800))) {
        DAT_febe6f4c = iVar2;
        DAT_febe6f50 = iVar4 * 0x800;
        return;
      }
      DAT_febe6f4c = iVar2;
      DAT_febe6f50 = 0x80000001;
      return;
    }
    if (iVar4 != 0) {
      if (((longlong)iVar4 * 0x800 < 0 || (int)((ulonglong)((longlong)iVar4 * 0x800) >> 0x20) == 0)
         && ((uint)(iVar4 * 0x800) < 0x80000000)) {
        DAT_febe6f4c = iVar2;
        DAT_febe6f50 = iVar4 * 0x800;
        return;
      }
      DAT_febe6f4c = iVar2;
      DAT_febe6f50 = 0x7fffffff;
      return;
    }
  }
  DAT_febe6f4c = iVar2;
  DAT_febe6f50 = 0;
  return;
}



void FUN_00039ffa(void)

{
  DAT_febe6f42 = 0;
  DAT_febe6f44 = 0;
  DAT_febe6f4c = 0;
  DAT_febe6f50 = 0;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_3a008(void)

{
  return;
}



/* Independent drive70B8/poles6F60/6F64, same exact coefficients as branch0, speed axis6694 and
   selector1 offset/following. Return/store adjusted6F54. Parallel source2 branch uses70B8 and
   independent retained poles with selector1 offset/following; same exact coefficients and signed
   return. */

int f33_update_ecu_source2_thermal_branch1(short upper,short lower,uchar alternate_gains)

{
  short gain;
  int iVar1;
  uint32_t puVar2;
  uint divisor;
  uint divisor_00;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  ushort local_30;
  short sStack_2e;
  short gain_00;
  
  iVar4 = DAT_febe70b8;
  iVar3 = DAT_febe6f64;
  iVar5 = DAT_febe6f60;
  puVar2 = 0xfebeb800u;
  iVar7 = (int)lower;
  iVar8 = (int)upper;
  iVar1 = (int)DAT_febe64e2;
  sStack_2e = DAT_febe6f54;
  gain = DAT_0002b3aa;
  gain_00 = DAT_0002b3a8;
  if (alternate_gains != '\0') {
    gain = DAT_0002b3ae;
    gain_00 = DAT_0002b3ac;
  }
  if (iVar1 + 0x7fff < 0 == (-1 < iVar1 && iVar1 + 0x7fff < 0) && iVar1 != -0x7fff) {
    if (iVar1 < 0) {
      iVar1 = (int)-DAT_febe64e2;
    }
  }
  else {
    iVar1 = 0x7fff;
  }
  iVar6 = (int)DAT_0002b3b8;
  if ((iVar1 - iVar6 < 0 == (iVar1 < 0 != iVar6 < 0 && iVar6 < 0 == iVar1 - iVar6 < 0) &&
       iVar1 != iVar6) &&
     (DAT_febe70b8 - DAT_0002b3c0 < 0 ==
      (DAT_febe70b8 < 0 != DAT_0002b3c0 < 0 && DAT_0002b3c0 < 0 == DAT_febe70b8 - DAT_0002b3c0 < 0)
      && DAT_febe70b8 != DAT_0002b3c0)) {
    local_30 = DAT_0002b3b6;
  }
  else {
    puVar2 = 0xfebeb800u;
    FUN_00070304(((undefined *)camry_host_ptr(0x2b36cu)),DAT_febe6694 & 0x7fff,&local_30);
  }
  divisor = f33_scale_thermal_divisor((uint)DAT_0002b3b2,(uint)local_30);
  divisor_00 = f33_scale_thermal_divisor((uint)DAT_0002b3b4,(uint)local_30);
  iVar1 = f33_update_nonnegative_thermal_pole(iVar5,iVar4,divisor);
  iVar3 = f33_update_nonnegative_thermal_pole(iVar3,iVar4,divisor_00);
  iVar4 = f33_scale_thermal_contribution(iVar1,gain_00,upper,lower);
  iVar6 = f33_scale_thermal_contribution(iVar3,gain,upper,lower);
  iVar5 = (int)DAT_0002b3b0 + iVar4 + iVar6;
  if (iVar5 - iVar8 < 0 != (iVar5 < 0 != iVar8 < 0 && iVar8 < 0 == iVar5 - iVar8 < 0) ||
      iVar5 == iVar8) {
    iVar8 = iVar5;
  }
  if (iVar8 - iVar7 < 0 == (iVar8 < 0 != iVar7 < 0 && iVar7 < 0 == iVar8 - iVar7 < 0)) {
    iVar7 = iVar8;
  }
  iVar5 = f33_apply_thermal_offset_and_following(1,(short)iVar7,sStack_2e);
  (*((short *)camry_host_ptr((uint32_t)((0xffffb75eu + (uint32_t)((int)puVar2)))))) = (short)iVar7;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb754u + (uint32_t)((int)puVar2)))))) = (short)iVar5;
  (*((int *)camry_host_ptr((uint32_t)((0xffffb760u + (uint32_t)((int)puVar2)))))) = iVar1;
  (*((int *)camry_host_ptr((uint32_t)((0xffffb764u + (uint32_t)((int)puVar2)))))) = iVar3;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb75au + (uint32_t)((int)puVar2)))))) = (short)divisor;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb75cu + (uint32_t)((int)puVar2)))))) = (short)divisor_00;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb756u + (uint32_t)((int)puVar2)))))) = (short)iVar4;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb758u + (uint32_t)((int)puVar2)))))) = (short)iVar6;
  return iVar5;
}



int FUN_0003a110(short param_1,short param_2)

{
  int iVar1;
  int iVar2;
  
  iVar2 = (int)param_2;
  if (iVar2 == 0) {
    return 0;
  }
  iVar1 = (int)param_1 << 0xc;
  if (iVar2 != 0) {
    if (iVar1 == -0x80000000 && iVar2 == -1) {
      iVar1 = -0x80000000;
    }
    else {
      iVar1 = iVar1 / iVar2;
    }
  }
  if (iVar1 < 0) {
    iVar2 = (int)((ulonglong)((longlong)iVar1 * 0x80) >> 0x20) + 1;
    if ((iVar2 < 0 != (-1 < (longlong)iVar1 * 0x80 && iVar2 < 0)) ||
       ((uint)(iVar1 * 0x80) < 0x80000001)) {
      return -0x7fffffff;
    }
  }
  else {
    if (iVar1 == 0) {
      return 0;
    }
    if ((-1 < (longlong)iVar1 * 0x80 && (int)((ulonglong)((longlong)iVar1 * 0x80) >> 0x20) != 0) ||
       (0x7fffffff < (uint)(iVar1 * 0x80))) {
      return 0x7fffffff;
    }
  }
  return iVar1 * 0x80;
}



void FUN_0003a160(short param_1,short param_2,char param_3)

{
  short sVar1;
  uint32_t puVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  short sVar2;
  
  puVar3 = 0xfebeb800u;
  sVar1 = DAT_0002b3a8;
  sVar2 = DAT_0002b3aa;
  if (param_3 != '\0') {
    sVar1 = DAT_0002b3ac;
    sVar2 = DAT_0002b3ae;
  }
  uVar4 = FUN_0003a110((int)param_1,(int)sVar1);
  uVar5 = FUN_0003a110((int)param_2,(int)sVar2);
  (*((undefined4 *)camry_host_ptr((uint32_t)((0xffffb760u + (uint32_t)((int)puVar3)))))) = uVar4;
  (*((undefined4 *)camry_host_ptr((uint32_t)((0xffffb764u + (uint32_t)((int)puVar3)))))) = uVar5;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb754u + (uint32_t)((int)puVar3)))))) = 0x3480;
  return;
}



/* WARNING: Removing unreachable block (ram,0x0003a20c) */
/* WARNING: Removing unreachable block (ram,0x0003a1bc) */
/* Same staged conversion for6F60/6F64 before first alternate-gain model update. Matching staged
   rebase for the independent second source2 pole pair; clearing the parent bank selector does not
   undo the latched transition. */

void f33_rebase_ecu_source2_thermal_branch1(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  iVar2 = 0x7fffffff;
  iVar4 = (int)DAT_0002b3ac;
  iVar3 = (int)DAT_0002b3ae;
  if (iVar4 == 0) {
LAB_0003a1d4:
    iVar2 = 0;
  }
  else {
    iVar1 = (DAT_febe6f60 / 0x800) * (int)DAT_0002b3a8;
    if (iVar4 != 0) {
      if (iVar1 == -0x80000000 && iVar4 == -1) {
        iVar1 = -0x80000000;
      }
      else {
        iVar1 = iVar1 / iVar4;
      }
    }
    if (iVar1 < 0) {
      iVar2 = (int)((ulonglong)((longlong)iVar1 * 0x800) >> 0x20) + 1;
      if ((iVar2 < 0 != (-1 < (longlong)iVar1 * 0x800 && iVar2 < 0)) ||
         ((uint)(iVar1 * 0x800) < 0x80000001)) {
        iVar2 = -0x7fffffff;
        goto LAB_0003a204;
      }
    }
    else {
      if (iVar1 == 0) goto LAB_0003a1d4;
      if ((-1 < (longlong)iVar1 * 0x800 && (int)((ulonglong)((longlong)iVar1 * 0x800) >> 0x20) != 0)
         || (0x7fffffff < (uint)(iVar1 * 0x800))) goto LAB_0003a204;
    }
    iVar2 = iVar1 * 0x800;
  }
LAB_0003a204:
  if (iVar3 != 0) {
    iVar4 = ((int)DAT_febe6f64 / 0x800) * (int)DAT_0002b3aa;
    if (iVar3 != 0) {
      if (iVar4 == -0x80000000 && iVar3 == -1) {
        iVar4 = -0x80000000;
      }
      else {
        iVar4 = iVar4 / iVar3;
      }
    }
    if (iVar4 < 0) {
      iVar3 = (int)((ulonglong)((longlong)iVar4 * 0x800) >> 0x20) + 1;
      if ((iVar3 < 0 == (-1 < (longlong)iVar4 * 0x800 && iVar3 < 0)) &&
         (0x80000000 < (uint)(iVar4 * 0x800))) {
        DAT_febe6f60 = iVar2;
        DAT_febe6f64 = iVar4 * 0x800;
        return;
      }
      DAT_febe6f60 = iVar2;
      DAT_febe6f64 = 0x80000001;
      return;
    }
    if (iVar4 != 0) {
      if (((longlong)iVar4 * 0x800 < 0 || (int)((ulonglong)((longlong)iVar4 * 0x800) >> 0x20) == 0)
         && ((uint)(iVar4 * 0x800) < 0x80000000)) {
        DAT_febe6f60 = iVar2;
        DAT_febe6f64 = iVar4 * 0x800;
        return;
      }
      DAT_febe6f60 = iVar2;
      DAT_febe6f64 = 0x7fffffff;
      return;
    }
  }
  DAT_febe6f60 = iVar2;
  DAT_febe6f64 = 0;
  return;
}



void FUN_0003a25c(void)

{
  DAT_febe6f56 = 0;
  DAT_febe6f58 = 0;
  DAT_febe6f60 = 0;
  DAT_febe6f64 = 0;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_3a26a(void)

{
  return;
}



/* Paired constant publisher: DAT_febe6f68 = 0x569a; and DAT_febe6f6a = 0x2b4d;; shape-classified
   from the canonical corpus. Target cells not yet named. */

void FUN_0003a26c(void)

{
  DAT_febe6f68 = 0x569a;
  DAT_febe6f6a = 0x2b4d;
  return;
}



/* Signed6F36 selects nonflat2B3C4/2B3E0 curves into6F68/6F6A. Bank0 reaches5542 at18560; bank1
   reaches0 at19376. Signed-axis7FFF terminates; FFFF ordinate is not an endpoint. Source2 signed
   estimate selects nonflat bank0/1 curves. Real final bank0 ordinate5542 and bank1 zero
   breakpoint19376 precede the7FFF/FFFF terminator. */

void f33_publish_ecu_source2_thermal_limit_maps(void)

{
  uint32_t puVar1;
  int iVar2;
  undefined2 local_c;
  undefined2 uStack_a;
  
  puVar1 = 0xfebeb800u;
  iVar2 = (int)DAT_febe6f36;
  FUN_0007025c(f33_ecu_source2_current_curve_bank0,iVar2,&local_c);
  FUN_0007025c(f33_ecu_source2_current_curve_bank1,iVar2,&uStack_a);
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb768u + (uint32_t)((int)puVar1)))))) = local_c;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb76au + (uint32_t)((int)puVar1)))))) = uStack_a;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_3a2b6(void)

{
  return;
}



/* Constant-block fill: 6 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_3a2b8(void)

{
  DAT_febe6f6e = 0x569a;
  DAT_febe6f70 = 0x569a;
  DAT_febe6f72 = 0x2b4d;
  DAT_febe6f74 = 0x569a;
  DAT_febe6f76 = 0x569a;
  DAT_febe6f78 = 0x2b4d;
  return;
}



/* WARNING: This is an inlined function */
/* With nonnull source, candidate<=current replaces both limit and source; ties choose the later
   candidate. Null source retains current. Real leaf preserves R8 across the selector's successive
   calls; inline its actual effects rather than inventing pointer arguments. Unsigned
   candidate<=current replaces limit and source when pointer is nonnull; equality favors later
   candidate. Real leaf preserves R8 across successive reductions; inline actual effects. */

uint f33_choose_thermal_limit_source
               (ushort current,ushort candidate,uchar *source,uchar candidate_source)

{
  uint uVar1;
  
  uVar1 = (uint)current;
  if (((uintptr_t)(source)!=(uintptr_t)((uchar *)0x0)) && (candidate <= uVar1)) {
    *source = candidate_source;
    uVar1 = (uint)candidate;
  }
  return uVar1;
}



/* WARNING: Inlined function: f33_choose_thermal_limit_source */
/* Reduce sources2,4,5,3 in that order, with later equal minima winning. Bank0 reads
   6F68/6F30/6EE0/700C; nonzero bank reads their +2 partners. Null source returns nominal 22170
   or11085 without reading the limits. Reduce ECU thermal limit sources2/4/5/3 with later-wins
   equality, independently by bank. Null source pointer returns nominal22170/11085 without reading
   candidate limits. */

uint f33_select_ecu_thermal_limit(uchar *source,uchar bank)

{
  uint32_t puVar1;
  uint32_t puVar2;
  ushort uVar3;
  uchar *extraout_r8;
  uchar *source_00;
  uchar *source_01;
  uchar *extraout_r8_00;
  ushort uVar4;
  uint uVar5;
  
  uVar4 = DAT_febe6f6a;
  uVar3 = DAT_febe6f68;
  puVar2 = 0xfebeb800u;
  puVar1 = 0xfebeb800u;
  if ((uintptr_t)(source)==(uintptr_t)((uchar *)0x0)) {
    if (bank == '\0') {
      uVar5 = 0x569a;
    }
    else {
      uVar5 = 0x2b4d;
    }
  }
  else {
    if (bank == '\0') {
      *source = '\x02';
      uVar4 = DAT_febe6f30;
      if (((uintptr_t)(source)!=(uintptr_t)((uchar *)0x0)) && (DAT_febe6f30 <= uVar3)) {
        *source = '\x04';
        uVar3 = uVar4;
      }
                    /* WARNING: Could not inline here */
      uVar5 = f33_choose_thermal_limit_source(uVar3,DAT_febe6ee0,source,'\x05');
      uVar4 = (ushort)uVar5;
      uVar3 = (*((ushort *)camry_host_ptr((uint32_t)((0xffffb80cu + (uint32_t)((int)puVar1))))));
      source_00 = extraout_r8;
    }
    else {
      *source = '\x02';
                    /* WARNING: Could not inline here */
      uVar5 = f33_choose_thermal_limit_source(uVar4,DAT_febe6f32,source,'\x04');
                    /* WARNING: Could not inline here */
      uVar5 = f33_choose_thermal_limit_source
                        ((ushort)uVar5,(*((ushort *)camry_host_ptr((uint32_t)((0xffffb6e2u + (uint32_t)((int)puVar2)))))),source_01,'\x05');
      uVar4 = (ushort)uVar5;
      uVar3 = (*((ushort *)camry_host_ptr((uint32_t)((0xffffb80eu + (uint32_t)((int)puVar2))))));
      source_00 = extraout_r8_00;
    }
                    /* WARNING: Could not inline here */
    uVar5 = f33_choose_thermal_limit_source(uVar4,uVar3,source_00,'\x03');
  }
  return uVar5;
}



/* Only limit below bank nominal22170/11085 and source2/3/4/5 publishes its source and signed
   temperature6F36/6FE2/6F12/6EAE. Otherwise publish source0 and return0; null output returns0
   without a write. Not selection of the globally strongest motor limit. Below bank nominal only,
   source2/3/4/5 selects signed temperature6F36/6FE2/6F12/6EAE and activity source. Equality/invalid
   source clears both; null output returns0 without write. This is separate from the global
   motor-versus-ECU minimum. */

int f33_select_ecu_thermal_diagnostic(ushort limit,uchar source,uchar *active_source,uchar bank)

{
  ushort uVar1;
  int iVar2;
  
  if ((uintptr_t)(active_source)==(uintptr_t)((uchar *)0x0)) {
    return 0;
  }
  uVar1 = 0x2b4d;
  if (bank == '\0') {
    uVar1 = 0x569a;
  }
  if (uVar1 <= limit) {
switchD_0003a386_default:
    *active_source = '\0';
    return 0;
  }
  switch(source) {
  case '\x02':
    iVar2 = (int)DAT_febe6f36;
    break;
  case '\x03':
    iVar2 = (int)DAT_febe6fe2;
    break;
  case '\x04':
    iVar2 = (int)DAT_febe6f12;
    break;
  case '\x05':
    iVar2 = (int)DAT_febe6eae;
    break;
  default:
    goto switchD_0003a386_default;
  }
  *active_source = source;
  return iVar2;
}



/* Limit strictly below nominal publishes active1 and signed6F82; equality or above publishes
   active0/temperature0. Both output pointers are required. Motor limit strictly below nominal
   publishes activity1 and signed6F82. Equality or above publishes activity0 and temperature0.
   Output pointers are required. */

void f33_select_motor_thermal_diagnostic
               (ushort limit,ushort nominal,uchar *active,short *temperature)

{
  short sVar1;
  
  if (limit < nominal) {
    *active = '\x01';
    sVar1 = DAT_febe6f82;
  }
  else {
    *active = '\0';
    sVar1 = 0;
  }
  *temperature = sVar1;
  return;
}



/* Rank by saturated absolute magnitude (-32768 ranks32767), retain original signed value and choose
   first on equality. Return is full sign-extended R10. Select original signed16 value with smaller
   saturated absolute magnitude; -32768 ranks32767 and equality preserves first. Full R10 return is
   sign-extended. */

int f33_select_smaller_magnitude_s16(short first,short second)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  iVar2 = (int)first;
  iVar3 = (int)second;
  if (iVar2 + 0x7fff < 0 == (-1 < iVar2 && iVar2 + 0x7fff < 0) && iVar2 != -0x7fff) {
    iVar1 = iVar2;
    if (iVar2 < 0) {
      iVar1 = (int)-first;
    }
  }
  else {
    iVar1 = 0x7fff;
  }
  if (iVar3 + 0x7fff < 0 == (-1 < iVar3 && iVar3 + 0x7fff < 0) && iVar3 != -0x7fff) {
    iVar4 = iVar3;
    if (iVar3 < 0) {
      iVar4 = (int)-second;
    }
  }
  else {
    iVar4 = 0x7fff;
  }
  if (iVar1 - iVar4 < 0 != (iVar1 < 0 != iVar4 < 0 && iVar4 < 0 == iVar1 - iVar4 < 0) ||
      iVar1 == iVar4) {
    iVar3 = iVar2;
  }
  return iVar3;
}



/* Map four signed temperature states and unsigned effective limit; retain the smallest absolute
   output at6F7E. All five exact maps are flat -22170 before their sentinels. 37FD2 applies this as
   a signed floor in its ordinary current-component branch. Compose four temperature maps and one
   unsigned-current-limit map by minimum absolute value. Exact pre-sentinel ordinates are all-22170;
   publish6F7E as the signed floor consumed by37FD2. Flat calibration does not imply the floor never
   binds. */

void f33_map_thermal_current_floor(ushort current_limit)

{
  uint32_t puVar1;
  int iVar2;
  short local_c;
  short sStack_a;
  
  puVar1 = 0xfebeb800u;
  FUN_00070208(((undefined *)camry_host_ptr(0x2b420u)),(int)DAT_febe6f36,&local_c);
  FUN_00070208(((undefined *)camry_host_ptr(0x2b43cu)),(int)(*((short *)camry_host_ptr((uint32_t)((0xffffb712u + (uint32_t)((int)puVar1)))))),&sStack_a);
  iVar2 = f33_select_smaller_magnitude_s16(local_c,sStack_a);
  local_c = (short)iVar2;
  FUN_00070208(((undefined *)camry_host_ptr(0x2b458u)),(int)(*((short *)camry_host_ptr((uint32_t)((0xffffb6aeu + (uint32_t)((int)puVar1)))))),&sStack_a);
  iVar2 = f33_select_smaller_magnitude_s16(local_c,sStack_a);
  local_c = (short)iVar2;
  FUN_00070208(((undefined *)camry_host_ptr(0x2b474u)),(int)(*((short *)camry_host_ptr((uint32_t)((0xffffb7e2u + (uint32_t)((int)puVar1)))))),&sStack_a);
  iVar2 = f33_select_smaller_magnitude_s16(local_c,sStack_a);
  local_c = (short)iVar2;
  FUN_000702b0(((undefined *)camry_host_ptr(0x2b3fcu)),current_limit,&sStack_a);
  iVar2 = f33_select_smaller_magnitude_s16(local_c,sStack_a);
  (*((short *)camry_host_ptr((uint32_t)((0xffffb77eu + (uint32_t)((int)puVar1)))))) = (short)iVar2;
  return;
}



/* Compute both ECU minima, combine each with its motor limit6FAC/6FAE, and choose bank0
   iff6764&3==0. Publish effective limit to owner0 viaBB736, but publish ECU and motor diagnostic
   activity/temperatures independently at6F6C..6F7C. No new-sample or heating proof. Native
   arbitration selects later ECU source3 on equal limits, retains its distinct temperature despite
   stronger motor limit1800, publishes independent diagnostic activities and exact-22170 floor, and
   writes only owner0. Explicit upstream RAM inputs; no heating or estimator-domain claim. */

void f33_arbitrate_thermal_current_limits(void)

{
  ushort uVar1;
  ushort uVar2;
  uint32_t puVar3;
  ushort limit;
  ushort nominal;
  undefined2 uVar4;
  uint uVar5;
  uint uVar6;
  ushort uVar8;
  ushort limit_00;
  uchar uStack_2a;
  uchar uStack_29;
  uchar uStack_28;
  uchar uStack_27;
  short sStack_26;
  int iVar7;
  uint uVar9;
  
  uVar8 = DAT_febe6764;
  puVar3 = 0xfebeb800u;
  uStack_28 = '\0';
  uStack_27 = '\0';
  uVar5 = f33_select_ecu_thermal_limit(&uStack_28,'\0');
  uVar1 = (*((ushort *)camry_host_ptr((uint32_t)((0xffffb7acu + (uint32_t)((int)puVar3))))));
  iVar7 = uVar1 - uVar5;
  uVar9 = uVar5;
  if (iVar7 < 0 != ((int)uVar5 < 0 && (int)uVar5 < 0 == iVar7 < 0)) {
    uVar9 = (uint)uVar1;
  }
  limit_00 = (ushort)uVar9;
  uVar6 = f33_select_ecu_thermal_limit(&uStack_27,'\x01');
  uVar2 = (*((ushort *)camry_host_ptr((uint32_t)((0xffffb7aeu + (uint32_t)((int)puVar3))))));
  iVar7 = uVar2 - uVar6;
  uVar9 = uVar6;
  if (iVar7 < 0 != ((int)uVar6 < 0 && (int)uVar6 < 0 == iVar7 < 0)) {
    uVar9 = (uint)uVar2;
  }
  limit = (ushort)uVar5;
  if ((uVar8 & 3) == 0) {
    iVar7 = f33_select_ecu_thermal_diagnostic(limit,uStack_28,&uStack_2a,(byte)uVar8 & 3);
    uVar4 = (undefined2)iVar7;
    nominal = 0x569a;
    uVar8 = uVar1;
  }
  else {
    iVar7 = f33_select_ecu_thermal_diagnostic((ushort)uVar6,uStack_27,&uStack_2a,'\x01');
    uVar4 = (undefined2)iVar7;
    nominal = 0x2b4d;
    uVar5 = uVar6;
    uVar8 = uVar2;
    limit_00 = (ushort)uVar9;
  }
  f33_select_motor_thermal_diagnostic(uVar8,nominal,&uStack_29,&sStack_26);
  f33_set_current_limit_request(0,limit_00);
  f33_map_thermal_current_floor(limit_00);
  (*((short *)camry_host_ptr((uint32_t)((0xffffb76eu + (uint32_t)((int)puVar3)))))) = (short)uVar5;
  (*((ushort *)camry_host_ptr((uint32_t)((0xffffb770u + (uint32_t)((int)puVar3)))))) = limit;
  (*((ushort *)camry_host_ptr((uint32_t)((0xffffb772u + (uint32_t)((int)puVar3)))))) = (ushort)uVar6;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb76cu + (uint32_t)((int)puVar3) * 1u)))) = uStack_2a;
  (*((ushort *)camry_host_ptr((uint32_t)((0xffffb774u + (uint32_t)((int)puVar3)))))) = uVar8;
  (*((ushort *)camry_host_ptr((uint32_t)((0xffffb776u + (uint32_t)((int)puVar3)))))) = uVar1;
  (*((ushort *)camry_host_ptr((uint32_t)((0xffffb778u + (uint32_t)((int)puVar3)))))) = uVar2;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb76du + (uint32_t)((int)puVar3) * 1u)))) = uStack_29;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb77au + (uint32_t)((int)puVar3)))))) = uVar4;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb77cu + (uint32_t)((int)puVar3)))))) = sStack_26;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_3a558(void)

{
  return;
}



void FUN_0003a55a(void)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  iVar2 = FUN_000588b6();
  if (iVar2 == 0) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb780u + (uint32_t)((int)puVar1) * 1u)))) = 0;
  }
  return;
}



/* Same strict32000/marker0/source-byte selection; selected histories6F84/6F88. Motor conditional
   zero predicate uses the shared marker0 and selected signed-difference>32000 contract with
   independent histories. */

uint f33_should_zero_motor_thermal_seed(ushort record_marker)

{
  int iVar1;
  uint uVar2;
  
  if ((DAT_febe7bf8 & 0xff) == 0) {
    if ((DAT_febe7bf8 & 0xff00) != 0) {
      DAT_febe6f84 = (int)DAT_febe7dd0 - (int)DAT_febe7dce;
      iVar1 = DAT_febe6f84;
      goto LAB_0003a5b6;
    }
  }
  else if ((DAT_febe7bf8 & 0xff00) == 0) {
    DAT_febe6f88 = (int)DAT_febe7dd8 - (int)DAT_febe7dd6;
    iVar1 = DAT_febe6f88;
    goto LAB_0003a5b6;
  }
  DAT_febe6f84 = (int)DAT_febe7dd0 - (int)DAT_febe7dce;
  DAT_febe6f88 = (int)DAT_febe7dd8 - (int)DAT_febe7dd6;
  iVar1 = DAT_febe6f84;
  if (DAT_febe6f88 - DAT_febe6f84 < 0 !=
      (DAT_febe6f88 < 0 != DAT_febe6f84 < 0 && DAT_febe6f84 < 0 == DAT_febe6f88 - DAT_febe6f84 < 0))
  {
    iVar1 = DAT_febe6f88;
  }
LAB_0003a5b6:
  if ((iVar1 - DAT_0002b4b8 < 0 ==
       (iVar1 < 0 != DAT_0002b4b8 < 0 && DAT_0002b4b8 < 0 == iVar1 - DAT_0002b4b8 < 0) &&
       iVar1 != DAT_0002b4b8) && (record_marker == 0)) {
    uVar2 = 0x5a;
  }
  else {
    uVar2 = 0;
  }
  return uVar2;
}



/* Seed56-byte local from211E8 then get application record6. Status!=10 or markerA55A uses ROM
   terms307/2893 per branch. Otherwise use saved terms unless at least one7BF8 byte is zero,
   marker==0 and selected signed source difference>32000. Marker is passed in realR6 to3A56E.
   Restore chooses live poles; it does not erase the record or prove durability. Record6 exact
   status10 and marker admission choose saved motor contributions or defaults307/2893. Marker0 and
   selected signed difference>32000 conditionally zero terms; equality retains. Real pole seeding
   and all-model arbitration executed from RAM mirror; no physical durability claim. */

void f33_restore_motor_thermal_model(void)

{
  undefined4 *puVar1;
  uint32_t puVar2;
  uint uVar3;
  undefined4 uVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  undefined4 *puVar9;
  undefined4 local_4c;
  short sStack_48;
  short sStack_46;
  ushort uStack_1a;
  
  puVar2 = 0xfebeb800u;
  puVar1 = &local_4c;
  puVar9 = ((undefined *)camry_host_ptr(0x211e8u));
  do {
    uVar4 = *puVar9;
    puVar9 = puVar9 + 1;
    *puVar1 = uVar4;
    puVar1 = puVar1 + 1;
  } while ((uintptr_t)(puVar9)!=(uintptr_t)(((undefined *)camry_host_ptr(0x21220u))));
  uVar3 = f33_nvm_get_record(6, camry_host_addr(&local_4c));
  iVar8 = (int)(short)local_4c;
  iVar7 = (int)sStack_48;
  iVar6 = (int)(*((uint16_t *)((uint8_t *)&local_4c + 2u)));
  iVar5 = (int)sStack_46;
  if ((uVar3 == 0x10) && (uStack_1a != 0xa55a)) {
    if ((((((*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x3c08)))) & 0xff) == 0) ||
         (((*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x3c08)))) & 0xff00) == 0)) && (uStack_1a != 0x5aa5)) &&
       (uVar3 = f33_should_zero_motor_thermal_seed(uStack_1a), uVar3 == 0x5a)) {
      iVar8 = 0;
      iVar5 = 0;
      iVar7 = 0;
      iVar6 = 0;
    }
  }
  else {
    iVar8 = (int)DAT_0002b4b6;
    iVar5 = (int)DAT_0002b4b4;
    iVar7 = iVar8;
    iVar6 = iVar5;
  }
  FUN_0003a808(iVar8);
  FUN_0003a94a(iVar7);
  FUN_0003a82a(iVar6);
  FUN_0003a96c(iVar5);
  return;
}



/* Only uninitialized6F80==0 requires7DCC/7BF6 both5A and restore3A5D4. Nonzero marker continues
   both branches without rechecking validity; publish signed maximum at6F82. Temperature estimation
   and later current-limit mapping are separate operations. Motor model initialization alone
   requires acquisition-valid markers. Initialized branches continue with absent markers and publish
   signed maximum of actual R10 returns; maps/arbitration remain separate. */

void f33_update_motor_thermal_estimate(void)

{
  short upper;
  short lower;
  undefined *puVar1;
  undefined2 uVar2;
  undefined *puVar3;
  int iVar5;
  int iVar6;
  char cVar7;
  uint32_t puVar4;
  puVar4 = 0xfebeb800u;
  puVar3 = ((undefined *)camry_host_ptr(0xfebeb800u));
  cVar7 = DAT_febe6f80;
  puVar1 = ((undefined *)camry_host_ptr(0xfebeb800u));
  if (DAT_febe6f80 == '\0') {
    if ((DAT_febe7dcc != 'Z') || (DAT_febe7bf6 != 'Z')) goto LAB_0003a6be;
    f33_restore_motor_thermal_model();
    cVar7 = 'Z';
    puVar1 = ((undefined *)camry_host_ptr((uint32_t)(puVar4)));
  }
  puVar3 = puVar1;
  lower = DAT_0002b4b2;
  upper = DAT_0002b4b0;
  iVar5 = f33_update_motor_thermal_branch0(DAT_0002b4b0,DAT_0002b4b2);
  iVar6 = f33_update_motor_thermal_branch1(upper,lower);
  if (iVar6 - iVar5 < 0 == (iVar6 < 0 != iVar5 < 0 && iVar5 < 0 == iVar6 - iVar5 < 0) &&
      iVar6 != iVar5) {
    uVar2 = (undefined2)iVar6;
  }
  else {
    uVar2 = (undefined2)iVar5;
  }
  *(undefined2 *)(((undefined *)camry_host_ptr(0xffffb782u)) + (int)camry_host_addr(puVar3)) = uVar2;
LAB_0003a6be:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb780u + (uint32_t)((int)camry_host_addr(puVar3)) * 1u)))) = cVar7;
  return;
}



int FUN_0003a6c6(short param_1,short param_2)

{
  int iVar1;
  int iVar2;
  
  iVar2 = (int)param_2;
  if (iVar2 == 0) {
    return 0;
  }
  iVar1 = (int)param_1 << 0xc;
  if (iVar2 != 0) {
    if (iVar1 == -0x80000000 && iVar2 == -1) {
      iVar1 = -0x80000000;
    }
    else {
      iVar1 = iVar1 / iVar2;
    }
  }
  if (iVar1 < 0) {
    iVar2 = (int)((ulonglong)((longlong)iVar1 * 0x80) >> 0x20) + 1;
    if ((iVar2 < 0 != (-1 < (longlong)iVar1 * 0x80 && iVar2 < 0)) ||
       ((uint)(iVar1 * 0x80) < 0x80000001)) {
      return -0x7fffffff;
    }
  }
  else {
    if (iVar1 == 0) {
      return 0;
    }
    if ((-1 < (longlong)iVar1 * 0x80 && (int)((ulonglong)((longlong)iVar1 * 0x80) >> 0x20) != 0) ||
       (0x7fffffff < (uint)(iVar1 * 0x80))) {
      return 0x7fffffff;
    }
  }
  return iVar1 * 0x80;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_3a716(void)

{
  return;
}



/* Drive70B4 updates poles6F94/6F98. Divisors1000/250 use flat1024 gain map unless
   sat_abs16(64E2)>32 AND drive>1638400, selecting1536 scale and divisors1500/375. Contributions use
   gains5/38, bias384; clamp then offset/follow selector6. Real signedR10 adjusted estimate is both
   stored6F8C and consumed by the parent maximum. Motor branch0 drives two poles from70B4. Strict
   amplitude>32 and drive>1638400 select divisor scale1536 instead of flat1024. Gains5/38 and
   bias384 precede selector6 offset/following. */

int f33_update_motor_thermal_branch0(short upper,short lower)

{
  short previous;
  int iVar1;
  uint32_t puVar2;
  uint divisor;
  uint divisor_00;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  ushort uStack_2a;
  
  iVar4 = DAT_febe70b4;
  iVar3 = DAT_febe6f98;
  iVar5 = DAT_febe6f94;
  previous = DAT_febe6f8c;
  puVar2 = 0xfebeb800u;
  iVar7 = (int)lower;
  iVar8 = (int)upper;
  iVar1 = (int)DAT_febe64e2;
  iVar6 = (int)DAT_0002b4c8;
  if (iVar1 + 0x7fff < 0 == (-1 < iVar1 && iVar1 + 0x7fff < 0) && iVar1 != -0x7fff) {
    if (iVar1 < 0) {
      iVar1 = (int)-DAT_febe64e2;
    }
  }
  else {
    iVar1 = 0x7fff;
  }
  if ((iVar1 - iVar6 < 0 == (iVar1 < 0 != iVar6 < 0 && iVar6 < 0 == iVar1 - iVar6 < 0) &&
       iVar1 != iVar6) &&
     (DAT_febe70b4 - DAT_0002b4cc < 0 ==
      (DAT_febe70b4 < 0 != DAT_0002b4cc < 0 && DAT_0002b4cc < 0 == DAT_febe70b4 - DAT_0002b4cc < 0)
      && DAT_febe70b4 != DAT_0002b4cc)) {
    uStack_2a = DAT_0002b4c6;
  }
  else {
    puVar2 = 0xfebeb800u;
    FUN_00070304(((undefined *)camry_host_ptr(0x2b490u)),DAT_febe668a & 0x7fff,&uStack_2a);
  }
  divisor = f33_scale_thermal_divisor((uint)DAT_0002b4c2,(uint)uStack_2a);
  divisor_00 = f33_scale_thermal_divisor((uint)DAT_0002b4c4,(uint)uStack_2a);
  iVar1 = f33_update_nonnegative_thermal_pole(iVar5,iVar4,divisor);
  iVar3 = f33_update_nonnegative_thermal_pole(iVar3,iVar4,divisor_00);
  iVar4 = f33_scale_thermal_contribution(iVar1,DAT_0002b4bc,upper,lower);
  iVar6 = f33_scale_thermal_contribution(iVar3,DAT_0002b4be,upper,lower);
  iVar5 = (int)DAT_0002b4c0 + iVar6 + iVar4;
  if (iVar5 - iVar8 < 0 != (iVar5 < 0 != iVar8 < 0 && iVar8 < 0 == iVar5 - iVar8 < 0) ||
      iVar5 == iVar8) {
    iVar8 = iVar5;
  }
  if (iVar8 - iVar7 < 0 == (iVar8 < 0 != iVar7 < 0 && iVar7 < 0 == iVar8 - iVar7 < 0)) {
    iVar7 = iVar8;
  }
  iVar5 = f33_apply_thermal_offset_and_following(6,(short)iVar7,previous);
  (*((short *)camry_host_ptr((uint32_t)((0xffffb792u + (uint32_t)((int)puVar2)))))) = (short)iVar7;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb78cu + (uint32_t)((int)puVar2)))))) = (short)iVar5;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb78eu + (uint32_t)((int)puVar2)))))) = (short)iVar4;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb790u + (uint32_t)((int)puVar2)))))) = (short)iVar6;
  (*((int *)camry_host_ptr((uint32_t)((0xffffb794u + (uint32_t)((int)puVar2)))))) = iVar1;
  (*((int *)camry_host_ptr((uint32_t)((0xffffb798u + (uint32_t)((int)puVar2)))))) = iVar3;
  return iVar5;
}



void FUN_0003a808(short param_1)

{
  uint32_t puVar1;
  undefined4 uVar2;
  
  puVar1 = 0xfebeb800u;
  uVar2 = FUN_0003a6c6((int)param_1,(int)DAT_0002b4bc);
  (*((undefined4 *)camry_host_ptr((uint32_t)((0xffffb794u + (uint32_t)((int)puVar1)))))) = uVar2;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb78cu + (uint32_t)((int)puVar1)))))) = 0x3480;
  return;
}



void FUN_0003a82a(short param_1)

{
  uint32_t puVar1;
  undefined4 uVar2;
  
  puVar1 = 0xfebeb800u;
  uVar2 = FUN_0003a6c6((int)param_1,(int)DAT_0002b4be);
  (*((undefined4 *)camry_host_ptr((uint32_t)((0xffffb798u + (uint32_t)((int)puVar1)))))) = uVar2;
  return;
}



/* Paired constant publisher: DAT_febe6f8e = 0; and DAT_febe6f94 = 0;; shape-classified from the
   canonical corpus. Target cells not yet named. */

void FUN_0003a844(void)

{
  DAT_febe6f8e = 0;
  DAT_febe6f94 = 0;
  return;
}



/* Paired constant publisher: DAT_febe6f90 = 0; and DAT_febe6f98 = 0;; shape-classified from the
   canonical corpus. Target cells not yet named. */

void FUN_0003a84e(void)

{
  DAT_febe6f90 = 0;
  DAT_febe6f98 = 0;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_3a858(void)

{
  return;
}



/* Drive70B8 and poles6FA4/6FA8; same exact numerical coefficients as branch0, separate
   speed-axis6694 and selector7. Return/store adjusted6F9C, not void. Motor branch1 has
   independent70B8 drive and poles but matching exact coefficients. Selector7 adjusted6F9C is a
   signed return consumed by parent maximum. */

int f33_update_motor_thermal_branch1(short upper,short lower)

{
  short previous;
  int iVar1;
  uint32_t puVar2;
  uint divisor;
  uint divisor_00;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  ushort uStack_2a;
  
  iVar4 = DAT_febe70b8;
  iVar3 = DAT_febe6fa8;
  iVar5 = DAT_febe6fa4;
  previous = DAT_febe6f9c;
  puVar2 = 0xfebeb800u;
  iVar7 = (int)lower;
  iVar8 = (int)upper;
  iVar1 = (int)DAT_febe64e2;
  iVar6 = (int)DAT_0002b4dc;
  if (iVar1 + 0x7fff < 0 == (-1 < iVar1 && iVar1 + 0x7fff < 0) && iVar1 != -0x7fff) {
    if (iVar1 < 0) {
      iVar1 = (int)-DAT_febe64e2;
    }
  }
  else {
    iVar1 = 0x7fff;
  }
  if ((iVar1 - iVar6 < 0 == (iVar1 < 0 != iVar6 < 0 && iVar6 < 0 == iVar1 - iVar6 < 0) &&
       iVar1 != iVar6) &&
     (DAT_febe70b8 - DAT_0002b4e0 < 0 ==
      (DAT_febe70b8 < 0 != DAT_0002b4e0 < 0 && DAT_0002b4e0 < 0 == DAT_febe70b8 - DAT_0002b4e0 < 0)
      && DAT_febe70b8 != DAT_0002b4e0)) {
    uStack_2a = DAT_0002b4da;
  }
  else {
    puVar2 = 0xfebeb800u;
    FUN_00070304(((undefined *)camry_host_ptr(0x2b490u)),DAT_febe6694 & 0x7fff,&uStack_2a);
  }
  divisor = f33_scale_thermal_divisor((uint)DAT_0002b4d6,(uint)uStack_2a);
  divisor_00 = f33_scale_thermal_divisor((uint)DAT_0002b4d8,(uint)uStack_2a);
  iVar1 = f33_update_nonnegative_thermal_pole(iVar5,iVar4,divisor);
  iVar3 = f33_update_nonnegative_thermal_pole(iVar3,iVar4,divisor_00);
  iVar4 = f33_scale_thermal_contribution(iVar1,DAT_0002b4d0,upper,lower);
  iVar6 = f33_scale_thermal_contribution(iVar3,DAT_0002b4d2,upper,lower);
  iVar5 = (int)DAT_0002b4d4 + iVar6 + iVar4;
  if (iVar5 - iVar8 < 0 != (iVar5 < 0 != iVar8 < 0 && iVar8 < 0 == iVar5 - iVar8 < 0) ||
      iVar5 == iVar8) {
    iVar8 = iVar5;
  }
  if (iVar8 - iVar7 < 0 == (iVar8 < 0 != iVar7 < 0 && iVar7 < 0 == iVar8 - iVar7 < 0)) {
    iVar7 = iVar8;
  }
  iVar5 = f33_apply_thermal_offset_and_following(7,(short)iVar7,previous);
  (*((short *)camry_host_ptr((uint32_t)((0xffffb7a2u + (uint32_t)((int)puVar2)))))) = (short)iVar7;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb79cu + (uint32_t)((int)puVar2)))))) = (short)iVar5;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb79eu + (uint32_t)((int)puVar2)))))) = (short)iVar4;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb7a0u + (uint32_t)((int)puVar2)))))) = (short)iVar6;
  (*((int *)camry_host_ptr((uint32_t)((0xffffb7a4u + (uint32_t)((int)puVar2)))))) = iVar1;
  (*((int *)camry_host_ptr((uint32_t)((0xffffb7a8u + (uint32_t)((int)puVar2)))))) = iVar3;
  return iVar5;
}



void FUN_0003a94a(short param_1)

{
  uint32_t puVar1;
  undefined4 uVar2;
  
  puVar1 = 0xfebeb800u;
  uVar2 = FUN_0003a6c6((int)param_1,(int)DAT_0002b4d0);
  (*((undefined4 *)camry_host_ptr((uint32_t)((0xffffb7a4u + (uint32_t)((int)puVar1)))))) = uVar2;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb79cu + (uint32_t)((int)puVar1)))))) = 0x3480;
  return;
}



void FUN_0003a96c(short param_1)

{
  uint32_t puVar1;
  undefined4 uVar2;
  
  puVar1 = 0xfebeb800u;
  uVar2 = FUN_0003a6c6((int)param_1,(int)DAT_0002b4d2);
  (*((undefined4 *)camry_host_ptr((uint32_t)((0xffffb7a8u + (uint32_t)((int)puVar1)))))) = uVar2;
  return;
}



/* Paired constant publisher: DAT_febe6f9e = 0; and DAT_febe6fa4 = 0;; shape-classified from the
   canonical corpus. Target cells not yet named. */

void FUN_0003a986(void)

{
  DAT_febe6f9e = 0;
  DAT_febe6fa4 = 0;
  return;
}



/* Paired constant publisher: DAT_febe6fa0 = 0; and DAT_febe6fa8 = 0;; shape-classified from the
   canonical corpus. Target cells not yet named. */

void FUN_0003a990(void)

{
  DAT_febe6fa0 = 0;
  DAT_febe6fa8 = 0;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_3a99a(void)

{
  return;
}



/* Paired constant publisher: DAT_febe6fac = 0x569a; and DAT_febe6fae = 0x2b4d;; shape-classified
   from the canonical corpus. Target cells not yet named. */

void FUN_0003a99c(void)

{
  DAT_febe6fac = 0x569a;
  DAT_febe6fae = 0x2b4d;
  return;
}



/* Map signed6F82 through2B4E4/2B500 into6FAC/6FAE. Exact curves are flat22170/14965 before
   signed-axis7FFF terminators, at or above arbitration nominals22170/11085. Exact motor estimate
   maps are flat22170/14965 before signed-axis7FFF terminators. Real scheduler composition leaves
   owner0 nominal and clears inactive diagnostic projections despite positive model estimate. */

void f33_publish_motor_thermal_limit_maps(void)

{
  uint32_t puVar1;
  int iVar2;
  undefined2 local_c;
  undefined2 uStack_a;
  
  puVar1 = 0xfebeb800u;
  iVar2 = (int)DAT_febe6f82;
  FUN_0007025c(((undefined *)camry_host_ptr(0x2b4e4u)),iVar2,&local_c);
  FUN_0007025c(((undefined *)camry_host_ptr(0x2b500u)),iVar2,&uStack_a);
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb7acu + (uint32_t)((int)puVar1)))))) = local_c;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb7aeu + (uint32_t)((int)puVar1)))))) = uStack_a;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_3a9e6(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_3a9e8(void)

{
  return;
}



/* Return real R10 A5 iff minimum of five bank0 maps>=21248. Map raw model maxima plus common10880
   and margins803/3370/0/0/983 after symmetric32767 saturation. Publish adjusted inputs6FB4..6FBC,
   maps6FBE..6FC6, minimum6FC8 and status6FB1. Five raw-estimate maxima plus fixed margins feed
   bank0 maps; inclusive minimum21248 controls real R10/status6FB1. Ordinary offset bank is not the
   input. */

uint f33_check_thermal_raw_estimate_margin(void)

{
  int iVar1;
  uint32_t puVar2;
  uint uVar3;
  uint uVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  ushort uStack_26;
  ushort uStack_24;
  ushort uStack_22;
  ushort uStack_20;
  ushort uStack_1e;
  
  puVar2 = 0xfebeb800u;
  iVar1 = (int)DAT_febe6fa2;
  iVar8 = (int)DAT_febe6f92;
  iVar5 = (int)DAT_0002fb54;
  iVar7 = (int)DAT_febe6f4a;
  iVar6 = (int)DAT_febe6fee;
  if (iVar1 - iVar8 < 0 == (iVar1 < 0 != iVar8 < 0 && iVar8 < 0 == iVar1 - iVar8 < 0) &&
      iVar1 != iVar8) {
    iVar8 = iVar1;
  }
  iVar8 = iVar8 + iVar5 + (int)DAT_0002fb56;
  iVar1 = (int)DAT_febe6f5e;
  if (iVar1 - iVar7 < 0 == (iVar1 < 0 != iVar7 < 0 && iVar7 < 0 == iVar1 - iVar7 < 0) &&
      iVar1 != iVar7) {
    iVar7 = iVar1;
  }
  iVar7 = iVar7 + iVar5 + (int)DAT_0002fb58;
  iVar1 = (int)DAT_febe6ffe;
  if (iVar1 - iVar6 < 0 == (iVar1 < 0 != iVar6 < 0 && iVar6 < 0 == iVar1 - iVar6 < 0) &&
      iVar1 != iVar6) {
    iVar6 = iVar1;
  }
  iVar6 = iVar6 + iVar5 + (int)DAT_0002fb5a;
  iVar1 = (int)DAT_0002fb5c + DAT_febe6f14 + iVar5;
  iVar5 = (int)DAT_0002fb5e + DAT_febe6eb0 + iVar5;
  if (iVar8 + 0x7fff < 0 == (-1 < iVar8 && iVar8 + 0x7fff < 0) && iVar8 != -0x7fff) {
    if (iVar8 + -0x7fff < 0 == (iVar8 < 0 && -1 < iVar8 + -0x7fff) && iVar8 != 0x7fff) {
      iVar8 = 0x7fff;
    }
    else {
      iVar8 = (int)(short)iVar8;
    }
  }
  else {
    iVar8 = -0x7fff;
  }
  if (iVar7 + 0x7fff < 0 == (-1 < iVar7 && iVar7 + 0x7fff < 0) && iVar7 != -0x7fff) {
    if (iVar7 + -0x7fff < 0 == (iVar7 < 0 && -1 < iVar7 + -0x7fff) && iVar7 != 0x7fff) {
      iVar7 = 0x7fff;
    }
    else {
      iVar7 = (int)(short)iVar7;
    }
  }
  else {
    iVar7 = -0x7fff;
  }
  if (iVar6 + 0x7fff < 0 == (-1 < iVar6 && iVar6 + 0x7fff < 0) && iVar6 != -0x7fff) {
    if (iVar6 + -0x7fff < 0 == (iVar6 < 0 && -1 < iVar6 + -0x7fff) && iVar6 != 0x7fff) {
      iVar6 = 0x7fff;
    }
    else {
      iVar6 = (int)(short)iVar6;
    }
  }
  else {
    iVar6 = -0x7fff;
  }
  if (iVar1 + 0x7fff < 0 == (-1 < iVar1 && iVar1 + 0x7fff < 0) && iVar1 != -0x7fff) {
    if (iVar1 + -0x7fff < 0 == (iVar1 < 0 && -1 < iVar1 + -0x7fff) && iVar1 != 0x7fff) {
      iVar1 = 0x7fff;
    }
    else {
      iVar1 = (int)(short)iVar1;
    }
  }
  else {
    iVar1 = -0x7fff;
  }
  if (iVar5 + 0x7fff < 0 == (-1 < iVar5 && iVar5 + 0x7fff < 0) && iVar5 != -0x7fff) {
    if (iVar5 + -0x7fff < 0 == (iVar5 < 0 && -1 < iVar5 + -0x7fff) && iVar5 != 0x7fff) {
      iVar5 = 0x7fff;
    }
    else {
      iVar5 = (int)(short)iVar5;
    }
  }
  else {
    iVar5 = -0x7fff;
  }
  FUN_0007025c(((undefined *)camry_host_ptr(0x2b4e4u)),iVar8,&uStack_26);
  FUN_0007025c(f33_ecu_source2_current_curve_bank0,iVar7,&uStack_24);
  FUN_0007025c(((undefined *)camry_host_ptr(0x2b554u)),iVar6,&uStack_22);
  FUN_0007025c(f33_ecu_source4_current_curve_bank0,iVar1,&uStack_20);
  FUN_0007025c(f33_ecu_source5_current_curve_bank0,iVar5,&uStack_1e);
  uVar4 = (uint)uStack_26;
  uVar3 = 0x5a;
  if ((int)(uStack_24 - uVar4) < 0) {
    uVar4 = (uint)uStack_24;
  }
  if ((int)(uStack_22 - uVar4) < 0) {
    uVar4 = (uint)uStack_22;
  }
  if ((int)(uStack_20 - uVar4) < 0) {
    uVar4 = (uint)uStack_20;
  }
  if ((int)(uStack_1e - uVar4) < 0) {
    uVar4 = (uint)uStack_1e;
  }
  if (DAT_0002fb60 <= uVar4) {
    uVar3 = 0xa5;
  }
  (*((short *)camry_host_ptr((uint32_t)((0xffffb7b4u + (uint32_t)((int)puVar2)))))) = (short)iVar8;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb7b6u + (uint32_t)((int)puVar2)))))) = (short)iVar7;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb7b8u + (uint32_t)((int)puVar2)))))) = (short)iVar6;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb7bau + (uint32_t)((int)puVar2)))))) = (short)iVar1;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb7bcu + (uint32_t)((int)puVar2)))))) = (short)iVar5;
  (*((ushort *)camry_host_ptr((uint32_t)((0xffffb7beu + (uint32_t)((int)puVar2)))))) = uStack_26;
  (*((ushort *)camry_host_ptr((uint32_t)((0xffffb7c0u + (uint32_t)((int)puVar2)))))) = uStack_24;
  (*((ushort *)camry_host_ptr((uint32_t)((0xffffb7c2u + (uint32_t)((int)puVar2)))))) = uStack_22;
  (*((ushort *)camry_host_ptr((uint32_t)((0xffffb7c4u + (uint32_t)((int)puVar2)))))) = uStack_20;
  (*((ushort *)camry_host_ptr((uint32_t)((0xffffb7c6u + (uint32_t)((int)puVar2)))))) = uStack_1e;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb7c8u + (uint32_t)((int)puVar2)))))) = (short)uVar4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb7b1u + (uint32_t)((int)puVar2) * 1u)))) = (char)uVar3;
  return uVar3;
}



/* Map maximum individual contribution of each model, then require maximum map output strictly below
   unsigned688C/2. Maps2FB64..2FBC7: motor/source3 flat125; source2/4/5 step125 to65534 at1229.
   Counter251 rejects equality,252 admits flat125. Publish maxima6FCA..6FD2, maps6FD4..6FDC,
   maximum6FDE and real R10/status6FB2. Maximum individual contribution per model feeds count maps;
   strict maximum<688C/2 rejects251 and admits252 for flat125. Source2/4/5 breakpoint1229
   yields65534. */

uint f33_check_thermal_contribution_count(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  uint32_t puVar6;
  uint uVar7;
  uint uVar8;
  uint uVar9;
  uint uVar10;
  uint uVar11;
  int iVar12;
  uint uVar13;
  uint uVar14;
  ushort uStack_26;
  ushort uStack_24;
  ushort uStack_22;
  ushort uStack_20;
  ushort uStack_1e;
  
  puVar6 = 0xfebeb800u;
  iVar12 = (int)DAT_febe6f90;
  iVar1 = (int)DAT_febe6fa0;
  uVar14 = (uint)f33_thermal_shutdown_count;
  if (iVar1 - iVar12 < 0 == (iVar1 < 0 != iVar12 < 0 && iVar12 < 0 == iVar1 - iVar12 < 0) &&
      iVar1 != iVar12) {
    iVar12 = iVar1;
  }
  iVar2 = (int)DAT_febe6f8e;
  iVar1 = (int)DAT_febe6f42;
  if (iVar2 - iVar12 < 0 == (iVar2 < 0 != iVar12 < 0 && iVar12 < 0 == iVar2 - iVar12 < 0) &&
      iVar2 != iVar12) {
    iVar12 = iVar2;
  }
  iVar2 = (int)DAT_febe6f9e;
  if (iVar2 - iVar12 < 0 == (iVar2 < 0 != iVar12 < 0 && iVar12 < 0 == iVar2 - iVar12 < 0) &&
      iVar2 != iVar12) {
    iVar12 = iVar2;
  }
  iVar2 = (int)DAT_febe6f56;
  if (iVar2 - iVar1 < 0 == (iVar2 < 0 != iVar1 < 0 && iVar1 < 0 == iVar2 - iVar1 < 0) &&
      iVar2 != iVar1) {
    iVar1 = iVar2;
  }
  iVar3 = (int)DAT_febe6f44;
  iVar2 = (int)DAT_febe6ff0;
  if (iVar3 - iVar1 < 0 == (iVar3 < 0 != iVar1 < 0 && iVar1 < 0 == iVar3 - iVar1 < 0) &&
      iVar3 != iVar1) {
    iVar1 = iVar3;
  }
  iVar3 = (int)DAT_febe6f58;
  if (iVar3 - iVar1 < 0 == (iVar3 < 0 != iVar1 < 0 && iVar1 < 0 == iVar3 - iVar1 < 0) &&
      iVar3 != iVar1) {
    iVar1 = iVar3;
  }
  iVar3 = (int)DAT_febe7000;
  if (iVar3 - iVar2 < 0 == (iVar3 < 0 != iVar2 < 0 && iVar2 < 0 == iVar3 - iVar2 < 0) &&
      iVar3 != iVar2) {
    iVar2 = iVar3;
  }
  iVar3 = (int)DAT_febe6ff2;
  if (iVar3 - iVar2 < 0 == (iVar3 < 0 != iVar2 < 0 && iVar2 < 0 == iVar3 - iVar2 < 0) &&
      iVar3 != iVar2) {
    iVar2 = iVar3;
  }
  iVar4 = (int)DAT_febe7002;
  iVar3 = (int)DAT_febe6f16;
  if (iVar4 - iVar2 < 0 == (iVar4 < 0 != iVar2 < 0 && iVar2 < 0 == iVar4 - iVar2 < 0) &&
      iVar4 != iVar2) {
    iVar2 = iVar4;
  }
  iVar4 = (int)DAT_febe6f18;
  if (iVar4 - iVar3 < 0 == (iVar4 < 0 != iVar3 < 0 && iVar3 < 0 == iVar4 - iVar3 < 0) &&
      iVar4 != iVar3) {
    iVar3 = iVar4;
  }
  iVar5 = (int)DAT_febe6eb4;
  iVar4 = (int)DAT_febe6eb2;
  if (iVar5 - iVar4 < 0 == (iVar5 < 0 != iVar4 < 0 && iVar4 < 0 == iVar5 - iVar4 < 0) &&
      iVar5 != iVar4) {
    iVar4 = iVar5;
  }
  iVar5 = (int)DAT_febe6eb6;
  if (iVar5 - iVar4 < 0 == (iVar5 < 0 != iVar4 < 0 && iVar4 < 0 == iVar5 - iVar4 < 0) &&
      iVar5 != iVar4) {
    iVar4 = iVar5;
  }
  iVar5 = (int)DAT_febe6eb8;
  if (iVar5 - iVar4 < 0 == (iVar5 < 0 != iVar4 < 0 && iVar4 < 0 == iVar5 - iVar4 < 0) &&
      iVar5 != iVar4) {
    iVar4 = iVar5;
  }
  iVar5 = (int)DAT_febe6eba;
  if (iVar5 - iVar4 < 0 == (iVar5 < 0 != iVar4 < 0 && iVar4 < 0 == iVar5 - iVar4 < 0) &&
      iVar5 != iVar4) {
    iVar4 = iVar5;
  }
  iVar5 = (int)DAT_febe6ebc;
  if (iVar5 - iVar4 < 0 == (iVar5 < 0 != iVar4 < 0 && iVar4 < 0 == iVar5 - iVar4 < 0) &&
      iVar5 != iVar4) {
    iVar4 = iVar5;
  }
  FUN_0007025c(((undefined *)camry_host_ptr(0x2fb64u)),iVar12,&uStack_26);
  FUN_0007025c(((undefined *)camry_host_ptr(0x2fb78u)),iVar1,&uStack_24);
  FUN_0007025c(((undefined *)camry_host_ptr(0x2fb8cu)),iVar2,&uStack_22);
  FUN_0007025c(((undefined *)camry_host_ptr(0x2fba0u)),iVar3,&uStack_20);
  FUN_0007025c(((undefined *)camry_host_ptr(0x2fbb4u)),iVar4,&uStack_1e);
  uVar8 = (uint)uStack_26;
  uVar9 = (uint)uStack_24;
  uVar7 = 0x5a;
  uVar10 = (uint)uStack_22;
  uVar11 = (uint)uStack_20;
  uVar13 = (uint)uStack_1e;
  if (-1 < (int)(uVar9 - uVar8) && uVar9 != uVar8) {
    uVar8 = uVar9;
  }
  if (-1 < (int)(uVar10 - uVar8) && uVar10 != uVar8) {
    uVar8 = uVar10;
  }
  if (-1 < (int)(uVar11 - uVar8) && uVar11 != uVar8) {
    uVar8 = uVar11;
  }
  if (-1 < (int)(uVar13 - uVar8) && uVar13 != uVar8) {
    uVar8 = uVar13;
  }
  if (uVar8 < (uint)((int)uVar14 >> 1)) {
    uVar7 = 0xa5;
  }
  (*((short *)camry_host_ptr((uint32_t)((0xffffb7cau + (uint32_t)((int)puVar6)))))) = (short)iVar12;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb7ccu + (uint32_t)((int)puVar6)))))) = (short)iVar1;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb7ceu + (uint32_t)((int)puVar6)))))) = (short)iVar2;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb7d0u + (uint32_t)((int)puVar6)))))) = (short)iVar3;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb7d2u + (uint32_t)((int)puVar6)))))) = (short)iVar4;
  (*((ushort *)camry_host_ptr((uint32_t)((0xffffb7d4u + (uint32_t)((int)puVar6)))))) = uStack_26;
  (*((ushort *)camry_host_ptr((uint32_t)((0xffffb7d6u + (uint32_t)((int)puVar6)))))) = uStack_24;
  (*((ushort *)camry_host_ptr((uint32_t)((0xffffb7d8u + (uint32_t)((int)puVar6)))))) = uStack_22;
  (*((ushort *)camry_host_ptr((uint32_t)((0xffffb7dau + (uint32_t)((int)puVar6)))))) = uStack_20;
  (*((ushort *)camry_host_ptr((uint32_t)((0xffffb7dcu + (uint32_t)((int)puVar6)))))) = uStack_1e;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb7deu + (uint32_t)((int)puVar6)))))) = (short)uVar8;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb7b2u + (uint32_t)((int)puVar6) * 1u)))) = (char)uVar7;
  return uVar7;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_3acf6(void)

{
  return;
}



void FUN_0003acf8(void)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  iVar2 = FUN_000588b6();
  if (iVar2 == 0) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb7e0u + (uint32_t)((int)puVar1) * 1u)))) = 0;
  }
  return;
}



/* Same strict32000/marker0/source-byte selection; selected histories6FE4/6FE8. Source3 conditional
   zero predicate has matching byte-selection and strict-boundary semantics with separate retained
   histories. */

uint f33_should_zero_ecu_source3_thermal_seed(ushort record_marker)

{
  int iVar1;
  uint uVar2;
  
  if ((DAT_febe7bf8 & 0xff) == 0) {
    if ((DAT_febe7bf8 & 0xff00) != 0) {
      DAT_febe6fe4 = (int)DAT_febe7dd0 - (int)DAT_febe7dce;
      iVar1 = DAT_febe6fe4;
      goto LAB_0003ad54;
    }
  }
  else if ((DAT_febe7bf8 & 0xff00) == 0) {
    DAT_febe6fe8 = (int)DAT_febe7dd8 - (int)DAT_febe7dd6;
    iVar1 = DAT_febe6fe8;
    goto LAB_0003ad54;
  }
  DAT_febe6fe4 = (int)DAT_febe7dd0 - (int)DAT_febe7dce;
  DAT_febe6fe8 = (int)DAT_febe7dd8 - (int)DAT_febe7dd6;
  iVar1 = DAT_febe6fe4;
  if (DAT_febe6fe8 - DAT_febe6fe4 < 0 !=
      (DAT_febe6fe8 < 0 != DAT_febe6fe4 < 0 && DAT_febe6fe4 < 0 == DAT_febe6fe8 - DAT_febe6fe4 < 0))
  {
    iVar1 = DAT_febe6fe8;
  }
LAB_0003ad54:
  if ((iVar1 - DAT_0002b520 < 0 ==
       (iVar1 < 0 != DAT_0002b520 < 0 && DAT_0002b520 < 0 == iVar1 - DAT_0002b520 < 0) &&
       iVar1 != DAT_0002b520) && (record_marker == 0)) {
    uVar2 = 0x5a;
  }
  else {
    uVar2 = 0;
  }
  return uVar2;
}



/* Uninitialized6FE0 requires7DCC/7BF6 both5A and restore3AD72. Otherwise update both branches and
   publish signed maximum6FE2; source3 is a structural code, not an OEM component. ECU structural
   source3 updates initialized branches without rechecking acquisition validity and publishes their
   signed maximum. Native scheduler interval also executes real request maps. */

void f33_update_ecu_source3_thermal_estimate(void)

{
  short upper;
  short lower;
  undefined *puVar1;
  undefined2 uVar2;
  undefined *puVar3;
  int iVar5;
  int iVar6;
  char cVar7;
  uint32_t puVar4;
  puVar4 = 0xfebeb800u;
  puVar3 = ((undefined *)camry_host_ptr(0xfebeb800u));
  cVar7 = DAT_febe6fe0;
  puVar1 = ((undefined *)camry_host_ptr(0xfebeb800u));
  if (DAT_febe6fe0 == '\0') {
    if ((DAT_febe7dcc != 'Z') || (DAT_febe7bf6 != 'Z')) goto LAB_0003ae5e;
    f33_restore_ecu_source3_thermal_model();
    cVar7 = 'Z';
    puVar1 = ((undefined *)camry_host_ptr((uint32_t)(puVar4)));
  }
  puVar3 = puVar1;
  lower = DAT_0002b51e;
  upper = DAT_0002b51c;
  iVar5 = f33_update_ecu_source3_thermal_branch0(DAT_0002b51c,DAT_0002b51e);
  iVar6 = f33_update_ecu_source3_thermal_branch1(upper,lower);
  if (iVar6 - iVar5 < 0 == (iVar6 < 0 != iVar5 < 0 && iVar5 < 0 == iVar6 - iVar5 < 0) &&
      iVar6 != iVar5) {
    uVar2 = (undefined2)iVar6;
  }
  else {
    uVar2 = (undefined2)iVar5;
  }
  *(undefined2 *)(((undefined *)camry_host_ptr(0xffffb7e2u)) + (int)camry_host_addr(puVar3)) = uVar2;
LAB_0003ae5e:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb7e0u + (uint32_t)((int)camry_host_addr(puVar3)) * 1u)))) = cVar7;
  return;
}



int FUN_0003ae66(short param_1,short param_2)

{
  int iVar1;
  int iVar2;
  
  iVar2 = (int)param_2;
  if (iVar2 == 0) {
    return 0;
  }
  iVar1 = (int)param_1 << 0xc;
  if (iVar2 != 0) {
    if (iVar1 == -0x80000000 && iVar2 == -1) {
      iVar1 = -0x80000000;
    }
    else {
      iVar1 = iVar1 / iVar2;
    }
  }
  if (iVar1 < 0) {
    iVar2 = (int)((ulonglong)((longlong)iVar1 * 0x80) >> 0x20) + 1;
    if ((iVar2 < 0 != (-1 < (longlong)iVar1 * 0x80 && iVar2 < 0)) ||
       ((uint)(iVar1 * 0x80) < 0x80000001)) {
      return -0x7fffffff;
    }
  }
  else {
    if (iVar1 == 0) {
      return 0;
    }
    if ((-1 < (longlong)iVar1 * 0x80 && (int)((ulonglong)((longlong)iVar1 * 0x80) >> 0x20) != 0) ||
       (0x7fffffff < (uint)(iVar1 * 0x80))) {
      return 0x7fffffff;
    }
  }
  return iVar1 * 0x80;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_3aeb6(void)

{
  return;
}



/* Drive6EF4 updates6FF4/6FF8. Exact divisors1/1 and contribution gains/bias0 still evolve poles,
   while raw thermal contribution is0. Selector4 offset/following remains active; return
   adjusted6FEC. Do not infer an entirely disabled thermal path. Source3 branch0 poles follow6EF4
   with exact divisors1. Zero contribution gains/bias leave selector4 offset/following active; */

int f33_update_ecu_source3_thermal_branch0(short upper,short lower)

{
  short previous;
  int iVar1;
  uint32_t puVar2;
  uint base;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  uint scale;
  uint base_00;
  int iVar7;
  int iVar8;
  
  iVar4 = DAT_febe6ff8;
  iVar3 = DAT_febe6ff4;
  previous = DAT_febe6fec;
  iVar5 = DAT_febe6ef4;
  puVar2 = 0xfebeb800u;
  iVar7 = (int)lower;
  iVar8 = (int)upper;
  iVar1 = (int)DAT_febe64e2;
  if (iVar1 + 0x7fff < 0 == (-1 < iVar1 && iVar1 + 0x7fff < 0) && iVar1 != -0x7fff) {
    if (iVar1 < 0) {
      iVar1 = (int)-DAT_febe64e2;
    }
  }
  else {
    iVar1 = 0x7fff;
  }
  iVar6 = (int)DAT_0002b530;
  base = (uint)DAT_0002b52a;
  base_00 = (uint)DAT_0002b52c;
  if ((iVar1 - iVar6 < 0 == (iVar1 < 0 != iVar6 < 0 && iVar6 < 0 == iVar1 - iVar6 < 0) &&
       iVar1 != iVar6) &&
     (DAT_febe6ef4 - DAT_0002b538 < 0 ==
      (DAT_febe6ef4 < 0 != DAT_0002b538 < 0 && DAT_0002b538 < 0 == DAT_febe6ef4 - DAT_0002b538 < 0)
      && DAT_febe6ef4 != DAT_0002b538)) {
    scale = (uint)DAT_0002b52e;
    puVar2 = 0xfebeb800u;
    base = f33_scale_thermal_divisor(base,scale);
    base_00 = f33_scale_thermal_divisor(base_00,scale);
  }
  iVar3 = f33_update_nonnegative_thermal_pole(iVar3,iVar5,base);
  iVar4 = f33_update_nonnegative_thermal_pole(iVar4,iVar5,base_00);
  iVar1 = f33_scale_thermal_contribution(iVar3,DAT_0002b524,upper,lower);
  iVar6 = f33_scale_thermal_contribution(iVar4,DAT_0002b526,upper,lower);
  iVar5 = (int)DAT_0002b528 + iVar6 + iVar1;
  if (iVar5 - iVar8 < 0 != (iVar5 < 0 != iVar8 < 0 && iVar8 < 0 == iVar5 - iVar8 < 0) ||
      iVar5 == iVar8) {
    iVar8 = iVar5;
  }
  if (iVar8 - iVar7 < 0 == (iVar8 < 0 != iVar7 < 0 && iVar7 < 0 == iVar8 - iVar7 < 0)) {
    iVar7 = iVar8;
  }
  iVar5 = f33_apply_thermal_offset_and_following(4,(short)iVar7,previous);
  (*((short *)camry_host_ptr((uint32_t)((0xffffb7eeu + (uint32_t)((int)puVar2)))))) = (short)iVar7;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb7ecu + (uint32_t)((int)puVar2)))))) = (short)iVar5;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb7f0u + (uint32_t)((int)puVar2)))))) = (short)iVar1;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb7f2u + (uint32_t)((int)puVar2)))))) = (short)iVar6;
  (*((int *)camry_host_ptr((uint32_t)((0xffffb7f4u + (uint32_t)((int)puVar2)))))) = iVar3;
  (*((int *)camry_host_ptr((uint32_t)((0xffffb7f8u + (uint32_t)((int)puVar2)))))) = iVar4;
  return iVar5;
}



void FUN_0003af8a(short param_1,short param_2)

{
  uint32_t puVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  
  puVar1 = 0xfebeb800u;
  uVar2 = FUN_0003ae66((int)param_1,(int)DAT_0002b524);
  uVar3 = FUN_0003ae66((int)param_2,(int)DAT_0002b526);
  (*((undefined4 *)camry_host_ptr((uint32_t)((0xffffb7f4u + (uint32_t)((int)puVar1)))))) = uVar2;
  (*((undefined4 *)camry_host_ptr((uint32_t)((0xffffb7f8u + (uint32_t)((int)puVar1)))))) = uVar3;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb7ecu + (uint32_t)((int)puVar1)))))) = 0x3480;
  return;
}



void FUN_0003afc0(void)

{
  DAT_febe6ff0 = 0;
  DAT_febe6ff2 = 0;
  DAT_febe6ff4 = 0;
  DAT_febe6ff8 = 0;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_3afce(void)

{
  return;
}



/* Drive6EF8 updates7004/7008; exact zero contribution gains/bias and divisors1/1 as branch0.
   Selector5 supplies adjusted6FFC, returned in signedR10. Source3 branch1 uses6EF8 and independent
   poles; zero contribution gains do not suppress selector5 offset or signed adjusted return6FFC. */

int f33_update_ecu_source3_thermal_branch1(short upper,short lower)

{
  short previous;
  int iVar1;
  uint32_t puVar2;
  uint base;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  uint scale;
  uint base_00;
  int iVar7;
  int iVar8;
  
  iVar4 = DAT_febe7008;
  iVar3 = DAT_febe7004;
  previous = DAT_febe6ffc;
  iVar5 = DAT_febe6ef8;
  puVar2 = 0xfebeb800u;
  iVar7 = (int)lower;
  iVar8 = (int)upper;
  iVar1 = (int)DAT_febe64e2;
  if (iVar1 + 0x7fff < 0 == (-1 < iVar1 && iVar1 + 0x7fff < 0) && iVar1 != -0x7fff) {
    if (iVar1 < 0) {
      iVar1 = (int)-DAT_febe64e2;
    }
  }
  else {
    iVar1 = 0x7fff;
  }
  iVar6 = (int)DAT_0002b548;
  base = (uint)DAT_0002b542;
  base_00 = (uint)DAT_0002b544;
  if ((iVar1 - iVar6 < 0 == (iVar1 < 0 != iVar6 < 0 && iVar6 < 0 == iVar1 - iVar6 < 0) &&
       iVar1 != iVar6) &&
     (DAT_febe6ef8 - DAT_0002b550 < 0 ==
      (DAT_febe6ef8 < 0 != DAT_0002b550 < 0 && DAT_0002b550 < 0 == DAT_febe6ef8 - DAT_0002b550 < 0)
      && DAT_febe6ef8 != DAT_0002b550)) {
    scale = (uint)DAT_0002b546;
    puVar2 = 0xfebeb800u;
    base = f33_scale_thermal_divisor(base,scale);
    base_00 = f33_scale_thermal_divisor(base_00,scale);
  }
  iVar3 = f33_update_nonnegative_thermal_pole(iVar3,iVar5,base);
  iVar4 = f33_update_nonnegative_thermal_pole(iVar4,iVar5,base_00);
  iVar1 = f33_scale_thermal_contribution(iVar3,DAT_0002b53c,upper,lower);
  iVar6 = f33_scale_thermal_contribution(iVar4,DAT_0002b53e,upper,lower);
  iVar5 = (int)DAT_0002b540 + iVar6 + iVar1;
  if (iVar5 - iVar8 < 0 != (iVar5 < 0 != iVar8 < 0 && iVar8 < 0 == iVar5 - iVar8 < 0) ||
      iVar5 == iVar8) {
    iVar8 = iVar5;
  }
  if (iVar8 - iVar7 < 0 == (iVar8 < 0 != iVar7 < 0 && iVar7 < 0 == iVar8 - iVar7 < 0)) {
    iVar7 = iVar8;
  }
  iVar5 = f33_apply_thermal_offset_and_following(5,(short)iVar7,previous);
  (*((short *)camry_host_ptr((uint32_t)((0xffffb7feu + (uint32_t)((int)puVar2)))))) = (short)iVar7;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb7fcu + (uint32_t)((int)puVar2)))))) = (short)iVar5;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb800u + (uint32_t)((int)puVar2)))))) = (short)iVar1;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb802u + (uint32_t)((int)puVar2)))))) = (short)iVar6;
  (*((int *)camry_host_ptr((uint32_t)((0xffffb804u + (uint32_t)((int)puVar2)))))) = iVar3;
  (*((int *)camry_host_ptr((uint32_t)((0xffffb808u + (uint32_t)((int)puVar2)))))) = iVar4;
  return iVar5;
}



void FUN_0003b0a2(short param_1,short param_2)

{
  uint32_t puVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  
  puVar1 = 0xfebeb800u;
  uVar2 = FUN_0003ae66((int)param_1,(int)DAT_0002b53c);
  uVar3 = FUN_0003ae66((int)param_2,(int)DAT_0002b53e);
  (*((undefined4 *)camry_host_ptr((uint32_t)((0xffffb804u + (uint32_t)((int)puVar1)))))) = uVar2;
  (*((undefined4 *)camry_host_ptr((uint32_t)((0xffffb808u + (uint32_t)((int)puVar1)))))) = uVar3;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb7fcu + (uint32_t)((int)puVar1)))))) = 0x3480;
  return;
}



void FUN_0003b0d8(void)

{
  DAT_febe7000 = 0;
  DAT_febe7002 = 0;
  DAT_febe7004 = 0;
  DAT_febe7008 = 0;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_3b0e6(void)

{
  return;
}



/* Paired constant publisher: DAT_febe700c = 0x569a; and DAT_febe700e = 0x2b4d;; shape-classified
   from the canonical corpus. Target cells not yet named. */

void FUN_0003b0e8(void)

{
  DAT_febe700c = 0x569a;
  DAT_febe700e = 0x2b4d;
  return;
}



/* Map signed6FE2 through2B554/2B570 into700C/700E; exact flat22170/14965 curves. This source alone
   does not lower either arbitration nominal. Exact source3 maps publish22170/14965 from the nonzero
   adjusted estimate. Sentinel ordinateFFFF is not an interpolation endpoint. */

void f33_publish_ecu_source3_thermal_limit_maps(void)

{
  uint32_t puVar1;
  int iVar2;
  undefined2 local_c;
  undefined2 uStack_a;
  
  puVar1 = 0xfebeb800u;
  iVar2 = (int)DAT_febe6fe2;
  FUN_0007025c(((undefined *)camry_host_ptr(0x2b554u)),iVar2,&local_c);
  FUN_0007025c(((undefined *)camry_host_ptr(0x2b570u)),iVar2,&uStack_a);
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb80cu + (uint32_t)((int)puVar1)))))) = local_c;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb80eu + (uint32_t)((int)puVar1)))))) = uStack_a;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_3b132(void)

{
  return;
}



void FUN_0003b134(void)

{
  uint uVar1;
  uint uVar2;
  
  DAT_febe7010 = 0x5a;
  uVar2 = 0;
  do {
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe701eu + (uint32_t)(uVar2) * 2u)))) = 0x3480;
    uVar2 = uVar2 + 1;
  } while (uVar2 < 6);
  uVar2 = 0;
  do {
    uVar1 = uVar2 + 1;
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe702au + (uint32_t)(uVar2) * 2u)))) = 0x3480;
    uVar2 = uVar1;
  } while (uVar1 < 6);
  DAT_febe7038 = 0;
  DAT_febe703c = 0;
  return;
}



void FUN_0003b16c(void)

{
  uint uVar1;
  short sVar2;
  uint uVar3;
  uint uVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  undefined2 auStack_c [6];
  
  sVar2 = DAT_febe7dce;
  uVar3 = DAT_febe7bf8 & 0x33;
  if ((DAT_febe7bf8 & 0x33) == 0) {
    iVar6 = (int)DAT_febe7dce;
    if (DAT_febe7010 == 0x5a) {
      uVar4 = 1;
      do {
        uVar1 = uVar4 + 1;
        (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe701eu + (uint32_t)(uVar4) * 2u)))) = sVar2;
        uVar4 = uVar1;
      } while (uVar1 < 6);
    }
    else {
      do {
        uVar4 = uVar3 + 1;
        auStack_c[uVar3] = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe701eu + (uint32_t)(uVar3) * 2u))));
        uVar3 = uVar4;
      } while (uVar4 < 6);
      uVar4 = 0;
      do {
        uVar1 = uVar4 + 1;
        (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7020u + (uint32_t)(uVar4) * 2u)))) = auStack_c[uVar4];
        uVar4 = uVar1;
        uVar3 = (uint)DAT_febe7010;
      } while (uVar1 < 5);
    }
  }
  else {
    iVar6 = (int)DAT_febe7028;
    uVar3 = 0x5a;
  }
  iVar5 = (int)DAT_0002b58c;
  iVar7 = (int)DAT_0002b58e;
  DAT_febe7010 = (char)uVar3;
  if (iVar5 - iVar6 < 0 != (iVar5 < 0 != iVar6 < 0 && iVar6 < 0 == iVar5 - iVar6 < 0)) {
    iVar6 = iVar5;
  }
  DAT_febe701e = DAT_0002b58e;
  if (iVar6 - iVar7 < 0 == (iVar6 < 0 != iVar7 < 0 && iVar7 < 0 == iVar6 - iVar7 < 0)) {
    DAT_febe701e = (short)iVar6;
  }
  return;
}



void FUN_0003b1fa(void)

{
  uint uVar1;
  short sVar2;
  uint uVar3;
  uint uVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  undefined2 auStack_c [6];
  
  sVar2 = DAT_febe7dd6;
  uVar3 = DAT_febe7bf8 & 0x3300;
  if ((DAT_febe7bf8 & 0x3300) == 0) {
    iVar6 = (int)DAT_febe7dd6;
    if (DAT_febe7011 == 0x5a) {
      uVar4 = 1;
      do {
        uVar1 = uVar4 + 1;
        (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe702au + (uint32_t)(uVar4) * 2u)))) = sVar2;
        uVar4 = uVar1;
      } while (uVar1 < 6);
    }
    else {
      do {
        uVar4 = uVar3 + 1;
        auStack_c[uVar3] = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe702au + (uint32_t)(uVar3) * 2u))));
        uVar3 = uVar4;
      } while (uVar4 < 6);
      uVar4 = 0;
      do {
        uVar1 = uVar4 + 1;
        (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe702cu + (uint32_t)(uVar4) * 2u)))) = auStack_c[uVar4];
        uVar4 = uVar1;
        uVar3 = (uint)DAT_febe7011;
      } while (uVar1 < 5);
    }
  }
  else {
    iVar6 = (int)DAT_febe7034;
    uVar3 = 0x5a;
  }
  iVar5 = (int)DAT_0002b58c;
  iVar7 = (int)DAT_0002b58e;
  DAT_febe7011 = (char)uVar3;
  if (iVar5 - iVar6 < 0 != (iVar5 < 0 != iVar6 < 0 && iVar6 < 0 == iVar5 - iVar6 < 0)) {
    iVar6 = iVar5;
  }
  DAT_febe702a = DAT_0002b58e;
  if (iVar6 - iVar7 < 0 == (iVar6 < 0 != iVar7 < 0 && iVar7 < 0 == iVar6 - iVar7 < 0)) {
    DAT_febe702a = (short)iVar6;
  }
  return;
}



void FUN_0003b288(void)

{
  int iVar1;
  int iVar2;
  
  iVar2 = (int)DAT_febe701e;
  iVar1 = (int)DAT_febe702a;
  DAT_febe7036 = DAT_febe701e;
  if (iVar1 - iVar2 < 0 == (iVar1 < 0 != iVar2 < 0 && iVar2 < 0 == iVar1 - iVar2 < 0) &&
      iVar1 != iVar2) {
    DAT_febe7036 = DAT_febe702a;
  }
  if ((((DAT_febe7bf8 & 0x22) == 0) && ((DAT_febe7bf8 & 0x2200) != 0)) || (DAT_febe6764 == 2)) {
    DAT_febe7012 = '\x11';
    DAT_febe7014 = DAT_febe701e;
  }
  else if ((((DAT_febe7bf8 & 0x22) == 0) || ((DAT_febe7bf8 & 0x2200) != 0)) && (DAT_febe6764 != 1))
  {
    DAT_febe7014 = DAT_febe7036;
    if (((DAT_febe7bf8 & 0x22) == 0) || ((DAT_febe7bf8 & 0x2200) == 0)) {
      DAT_febe7012 = '\0';
    }
    else {
      if (DAT_febe7012 == '\x11') {
        DAT_febe7014 = DAT_febe701e;
        return;
      }
      if (DAT_febe7012 == '\"') {
        DAT_febe7014 = DAT_febe702a;
        return;
      }
    }
  }
  else {
    DAT_febe7012 = '\"';
    DAT_febe7014 = DAT_febe702a;
  }
  return;
}



/* WARNING: Removing unreachable block (ram,0x0003b362) */
/* WARNING: Removing unreachable block (ram,0x0003b30e) */

void FUN_0003b2f6(void)

{
  short sVar1;
  short sVar2;
  uint32_t puVar3;
  int iVar4;
  int local_2c;
  short sStack_28;
  short sStack_26;
  int iStack_24;
  F33FractionalFollowing16 FStack_20;
  F33FractionalFollowing16 FStack_18;
  
  sVar1 = DAT_febe7014;
  puVar3 = 0xfebeb800u;
  iVar4 = (int)DAT_febe7014;
  FStack_18.accumulator = DAT_febe7038;
  FStack_18.target = DAT_febe7014;
  FStack_18.previous = DAT_febe7016;
  if ((short)(DAT_febe7038 / 0x10000) != DAT_febe7016) {
    FStack_18.previous = DAT_febe7014;
    FStack_18.accumulator = iVar4 << 0x10;
  }
  f33_follow_s16_fractional(&FStack_18,(uint)DAT_0002b590,&sStack_28,&local_2c);
  sVar2 = DAT_febe7018;
  FStack_20.target = sVar1;
  DAT_febe7016 = sStack_28;
  FStack_20.previous = DAT_febe7018;
  (*((int *)camry_host_ptr((uint32_t)((0xffffb838u + (uint32_t)((int)puVar3)))))) = local_2c;
  FStack_20.accumulator = (*((int *)camry_host_ptr((uint32_t)((0xffffb83cu + (uint32_t)((int)puVar3))))));
  if ((short)(FStack_20.accumulator / 0x10000) != sVar2) {
    FStack_20.previous = sVar1;
    FStack_20.accumulator = iVar4 << 0x10;
  }
  f33_follow_s16_fractional(&FStack_20,(uint)DAT_0002b592,&sStack_26,&iStack_24);
  DAT_febe7018 = sStack_26;
  (*((int *)camry_host_ptr((uint32_t)((0xffffb83cu + (uint32_t)((int)puVar3)))))) = iStack_24;
  return;
}



/* Sequential initializer chain: 4 unconditional calls and no other statements; shape-verified. The
   called sequence is the function's entire behavior; chain family members differ in callee sets. */

void f33_run_init_chain_3b398(void)

{
  FUN_0003b16c();
  FUN_0003b1fa();
  FUN_0003b288();
  FUN_0003b2f6();
  return;
}



/* f33_reset_latched_monitor wrapper resetting exactly one monitor state ((F33LatchedMonitorState
   *)((undefined *)camry_host_ptr(0xfebe7040u))); whole-body shape-verified from the canonical corpus. Per-instance semantics
   derive from the referenced state cell; not individually executed. */

void f33_reset_latched_monitor_febe7040(void)

{
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7040u)));
  return;
}



/* f33_reset_latched_monitor wrapper resetting exactly one monitor state ((F33LatchedMonitorState
   *)((undefined *)camry_host_ptr(0xfebe7040u))); whole-body shape-verified from the canonical corpus. Per-instance semantics
   derive from the referenced state cell; not individually executed. */

void f33_reset_latched_monitor_febe7040_3b3c0(void)

{
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7040u)));
  return;
}



void FUN_0003b3d0(void)

{
  if (DAT_0002bb30 == 'Z') {
    f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7040u)));
  }
  else {
    f33_step_latched_monitor
              ((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7040u)),(F33MonitorLimits *)((undefined *)camry_host_ptr(0x2b5d0u)),
               (F33TwoSidedMonitorCallbacks *)&PTR_FUN_00027f64);
  }
  return;
}



undefined4 FUN_0003b400(void)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  uint uVar4;
  short sStack_a;
  
  uVar4 = (uint)DAT_febe6f6e;
  FUN_0006a522((int)DAT_febe6772,&sStack_a);
  iVar3 = (int)DAT_0002b5d8;
  iVar1 = ((int)sStack_a - uVar4) - iVar3;
  if (iVar1 < 0 == ((int)((int)sStack_a - uVar4) < 0 != iVar3 < 0 && iVar3 < 0 == iVar1 < 0)) {
    uVar2 = 0x22;
  }
  else {
    uVar2 = 0x11;
  }
  return uVar2;
}



void FUN_0003b434(void)

{
  f33_report_diagnostic_event_failure(0x6e,800);
  FUN_000545de(3);
  FUN_00051cf6(0,800);
  return;
}



/* f33_reset_latched_monitor wrapper resetting exactly one monitor state ((F33LatchedMonitorState
   *)((undefined *)camry_host_ptr(0xfebe704cu))); whole-body shape-verified from the canonical corpus. Per-instance semantics
   derive from the referenced state cell; not individually executed. */

void f33_reset_latched_monitor_febe704c(void)

{
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe704cu)));
  return;
}



/* f33_reset_latched_monitor wrapper resetting exactly one monitor state ((F33LatchedMonitorState
   *)((undefined *)camry_host_ptr(0xfebe704cu))); whole-body shape-verified from the canonical corpus. Per-instance semantics
   derive from the referenced state cell; not individually executed. */

void f33_reset_latched_monitor_febe704c_3b468(void)

{
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe704cu)));
  return;
}



void FUN_0003b478(void)

{
  if (DAT_0002bb34 == 'Z') {
    f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe704cu)));
  }
  else {
    f33_step_latched_monitor
              ((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe704cu)),(F33MonitorLimits *)((undefined *)camry_host_ptr(0x2b5d4u)),
               (F33TwoSidedMonitorCallbacks *)&PTR_FUN_00027f98);
  }
  return;
}



undefined4 FUN_0003b4a8(void)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  uint uVar4;
  short sStack_a;
  
  uVar4 = (uint)DAT_febe6f74;
  FUN_0006a522((int)DAT_febe6772,&sStack_a);
  iVar3 = (int)DAT_0002b5dc;
  iVar1 = ((int)sStack_a - uVar4) - iVar3;
  if (iVar1 < 0 == ((int)((int)sStack_a - uVar4) < 0 != iVar3 < 0 && iVar3 < 0 == iVar1 < 0)) {
    uVar2 = 0x22;
  }
  else {
    uVar2 = 0x11;
  }
  return uVar2;
}



void FUN_0003b4dc(void)

{
  f33_report_diagnostic_event_failure(0x6d,800);
  FUN_000545de(2);
  FUN_00051cf6(1,800);
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_3b500(void)

{
  return;
}



void FUN_0003b502(void)

{
  int iVar1;
  int iVar2;
  uint32_t puVar3;
  int iVar4;
  
  puVar3 = 0xfebeb800u;
  iVar4 = FUN_000588b6();
  if (iVar4 == 0) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb858u + (uint32_t)((int)puVar3) * 1u)))) = 0;
    iVar4 = 0;
    do {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7059u + (uint32_t)(iVar4) * 1u)))) = 0;
      iVar2 = iVar4 + 1;
      iVar1 = iVar4 + -7;
      iVar4 = iVar2;
    } while (((iVar1 < 0) || (iVar2 < 0)));
    iVar4 = 0;
    do {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7061u + (uint32_t)(iVar4) * 1u)))) = 0;
      iVar2 = iVar4 + 1;
      iVar1 = iVar4 + -7;
      iVar4 = iVar2;
    } while (((iVar1 < 0) || (iVar2 < 0)));
    iVar4 = 0;
    do {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7069u + (uint32_t)(iVar4) * 1u)))) = 0;
      iVar2 = iVar4 + 1;
      iVar1 = iVar4 + -7;
      iVar4 = iVar2;
    } while (((iVar1 < 0) || (iVar2 < 0)));
    iVar4 = 0;
    do {
      iVar2 = iVar4 + 1;
      *(undefined4 *)(((undefined *)camry_host_ptr(0xfebe7090u)) + iVar4 * 4) = 0;
      iVar1 = iVar4 + -7;
      iVar4 = iVar2;
    } while (((iVar1 < 0) || (iVar2 < 0)));
    DAT_febe7071 = 0;
    DAT_febe7072 = 0;
  }
  return;
}



/* Select signed absolute reference7DCE/7DD6 by7BF8 byte availability, otherwise their maximum.
   Return5A only for selected<14720 AND marker0; not a reference delta. Always snapshot references
   into707E/7080; real marker arrives in R6. Offset restoration selects signed absolute reference
   by7BF8 availability, otherwise maximum; selected<14720 and marker0 alone return5A. Not the model
   restore delta predicate. */

uint f33_should_zero_restored_thermal_offset(short record_marker)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  int iVar4;
  
  iVar4 = (int)DAT_febe7dce;
  iVar3 = (int)DAT_febe7dd6;
  if ((DAT_febe7bf8 & 0xff) == 0) {
    iVar1 = iVar4;
    if ((DAT_febe7bf8 & 0xff00) != 0) goto LAB_0003b586;
  }
  else {
    iVar1 = iVar3;
    if ((DAT_febe7bf8 & 0xff00) == 0) goto LAB_0003b586;
  }
  iVar1 = iVar4;
  if (iVar3 - iVar4 < 0 == (iVar3 < 0 != iVar4 < 0 && iVar4 < 0 == iVar3 - iVar4 < 0) &&
      iVar3 != iVar4) {
    iVar1 = iVar3;
  }
LAB_0003b586:
  iVar3 = (int)DAT_0002b59e;
  if ((iVar1 - iVar3 < 0 == (iVar1 < 0 != iVar3 < 0 && iVar3 < 0 == iVar1 - iVar3 < 0)) ||
     (record_marker != 0)) {
    uVar2 = 0;
  }
  else {
    uVar2 = 0x5a;
  }
  DAT_febe707e = DAT_febe7dce;
  DAT_febe7080 = DAT_febe7dd6;
  return uVar2;
}



/* Gain0 returns0; otherwise signed contribution*4096/gain, then saturating multiply128. Seed offset
   pole with signed contribution*4096/gain then saturating multiply128; zero gain returnszero. */

int f33_seed_thermal_offset_pole(short contribution,short gain)

{
  int iVar1;
  int iVar2;
  int local_8;
  
  iVar2 = (int)gain;
  if (iVar2 == 0) {
    local_8 = 0;
  }
  else {
    iVar1 = (int)contribution << 0xc;
    if (iVar2 != 0) {
      if (iVar1 == -0x80000000 && iVar2 == -1) {
        iVar1 = -0x80000000;
      }
      else {
        iVar1 = iVar1 / iVar2;
      }
    }
    FUN_000706ae(iVar1,0x80,&local_8);
  }
  return local_8;
}



void FUN_0003b5d2(short param_1,short param_2)

{
  uint32_t puVar1;
  int iVar2;
  int iVar3;
  
  puVar1 = 0xfebeb800u;
  iVar2 = f33_seed_thermal_offset_pole(param_1,DAT_0002b5ac);
  iVar3 = f33_seed_thermal_offset_pole(param_2,DAT_0002b5ae);
  (*((int *)camry_host_ptr((uint32_t)((0xffffb8bcu + (uint32_t)((int)puVar1)))))) = iVar2;
  (*((int *)camry_host_ptr((uint32_t)((0xffffb8c0u + (uint32_t)((int)puVar1)))))) = iVar3;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb874u + (uint32_t)((int)puVar1)))))) = 0x3980;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb876u + (uint32_t)((int)puVar1)))))) = 0x3980;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb878u + (uint32_t)((int)puVar1)))))) = 0x3980;
  return;
}



/* Copy record6 before exact status10/marker!=A55A admission. Zero-byte7BF8 and marker!=5AA5
   permit3B55A conditional zero. Restore+16 then+14 through gains100/25; rejection uses exact zero
   defaults. Seed baseline outputs7074/76/78 to14720. Copy record6 before exact10/nonA55A admission;
   selected absolute-reference test can zero saved offsets, otherwise restore+16/+14 through
   gains100/25. Zero defaults and14720 output baseline. */

void f33_restore_thermal_offset_terms(void)

{
  uint *puVar1;
  uint32_t puVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  undefined4 uVar6;
  undefined4 *puVar7;
  uint local_3c [5];
  short sStack_28;
  short sStack_26;
  short sStack_a;
  
  puVar2 = 0xfebeb800u;
  puVar1 = local_3c;
  puVar7 = ((undefined *)camry_host_ptr(0x21268u));
  do {
    uVar6 = *puVar7;
    puVar7 = puVar7 + 1;
    *puVar1 = uVar6;
    puVar1 = puVar1 + 1;
  } while ((uintptr_t)(puVar7)!=(uintptr_t)(((undefined *)camry_host_ptr(0x212a0u))));
  uVar5 = f33_nvm_get_record(6, camry_host_addr(local_3c));
  if ((uVar5 == 0x10) && (sStack_a != -0x5aa6)) {
    if ((((((*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x3c08)))) & 0xff) == 0) ||
         (((*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x3c08)))) & 0xff00) == 0)) && (sStack_a != 0x5aa5)) &&
       (uVar5 = f33_should_zero_restored_thermal_offset(sStack_a), uVar5 == 0x5a)) {
      iVar3 = 0;
      iVar4 = 0;
    }
    else {
      iVar3 = (int)sStack_26;
      iVar4 = (int)sStack_28;
    }
  }
  else {
    iVar3 = (int)DAT_0002b5b0;
    iVar4 = (int)DAT_0002b5b2;
  }
  FUN_0003b5d2(iVar3,iVar4);
  return;
}



/* Low32 sums66E6^2+66E8^2 and66EA^2+66EC^2 pass unsigned bounds and publish70B4/70B8. Their bounded
   sum also drives independent70BC/70C0 poles and a separate returned estimate. These staged
   squared-input drives are not measurements of power in watts. Bounded low32 squared-input pairs
   publish70B4/70B8 and feed a separate retained estimate. Mathematical square magnitude and
   physical watt units are not implied. */

int f33_stage_dual_thermal_squared_inputs(short upper,short lower)

{
  undefined4 uVar1;
  undefined4 uVar2;
  short sVar3;
  short sVar4;
  int iVar5;
  int iVar6;
  uint32_t puVar7;
  int iVar8;
  int iVar9;
  int iVar10;
  int iVar11;
  int local_38;
  int iStack_34;
  int iStack_30;
  int iStack_2c;
  
  iVar9 = DAT_febe70c0;
  iVar8 = DAT_febe70bc;
  sVar4 = DAT_febe66ec;
  sVar3 = DAT_febe66ea;
  uVar2 = DAT_0002b5c4;
  uVar1 = DAT_0002b5c0;
  puVar7 = 0xfebeb800u;
  iStack_30 = (int)DAT_febe66e8 * (int)DAT_febe66e8 + (int)DAT_febe66e6 * (int)DAT_febe66e6;
  FUN_0007013e(iStack_30,DAT_0002b5c0,DAT_0002b5c4,&iStack_30);
  iStack_2c = (int)sVar4 * (int)sVar4 + (int)sVar3 * (int)sVar3;
  FUN_0007013e(iStack_2c,uVar1,uVar2,&iStack_2c);
  iVar6 = iStack_2c;
  iVar5 = iStack_30;
  local_38 = iStack_2c + iStack_30;
  FUN_0007012a(local_38,DAT_0002b5c8,DAT_0002b5cc,&local_38);
  iVar8 = f33_update_nonnegative_thermal_pole(iVar8,local_38,(uint)DAT_0002b5a8);
  iVar9 = f33_update_nonnegative_thermal_pole(iVar9,local_38,(uint)DAT_0002b5aa);
  iVar10 = f33_scale_thermal_contribution(iVar8,DAT_0002b5ac,upper,lower);
  iVar11 = f33_scale_thermal_contribution(iVar9,DAT_0002b5ae,upper,lower);
  iStack_34 = (int)DAT_0002b59e + iVar10 + iVar11;
  FUN_0007012a(iStack_34,(int)upper,(int)lower,&iStack_34);
  (*((int *)camry_host_ptr((uint32_t)((0xffffb8b4u + (uint32_t)((int)puVar7)))))) = iVar5;
  (*((int *)camry_host_ptr((uint32_t)((0xffffb8b8u + (uint32_t)((int)puVar7)))))) = iVar6;
  (*((int *)camry_host_ptr((uint32_t)((0xffffb8b0u + (uint32_t)((int)puVar7)))))) = local_38;
  (*((int *)camry_host_ptr((uint32_t)((0xffffb8c0u + (uint32_t)((int)puVar7)))))) = iVar9;
  (*((int *)camry_host_ptr((uint32_t)((0xffffb8bcu + (uint32_t)((int)puVar7)))))) = iVar8;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb87au + (uint32_t)((int)puVar7)))))) = (short)iVar10;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb87cu + (uint32_t)((int)puVar7)))))) = (short)iVar11;
  return (int)(short)iStack_34;
}



/* WARNING: Removing unreachable block (ram,0x0003b7da) */
/* WARNING: Removing unreachable block (ram,0x0003b786) */

void FUN_0003b76e(void)

{
  short sVar1;
  short sVar2;
  uint32_t puVar3;
  int iVar4;
  int local_2c;
  short sStack_28;
  short sStack_26;
  int iStack_24;
  F33FractionalFollowing16 FStack_20;
  F33FractionalFollowing16 FStack_18;
  
  sVar1 = DAT_febe7074;
  puVar3 = 0xfebeb800u;
  iVar4 = (int)DAT_febe7074;
  FStack_18.accumulator = DAT_febe7088;
  FStack_18.target = DAT_febe7074;
  FStack_18.previous = DAT_febe7076;
  if ((short)(DAT_febe7088 / 0x10000) != DAT_febe7076) {
    FStack_18.previous = DAT_febe7074;
    FStack_18.accumulator = iVar4 << 0x10;
  }
  f33_follow_s16_fractional(&FStack_18,(uint)DAT_0002b5b4,&sStack_28,&local_2c);
  sVar2 = DAT_febe7078;
  FStack_20.target = sVar1;
  DAT_febe7076 = sStack_28;
  FStack_20.previous = DAT_febe7078;
  (*((int *)camry_host_ptr((uint32_t)((0xffffb888u + (uint32_t)((int)puVar3)))))) = local_2c;
  FStack_20.accumulator = (*((int *)camry_host_ptr((uint32_t)((0xffffb88cu + (uint32_t)((int)puVar3))))));
  if ((short)(FStack_20.accumulator / 0x10000) != sVar2) {
    FStack_20.previous = sVar1;
    FStack_20.accumulator = iVar4 << 0x10;
  }
  f33_follow_s16_fractional(&FStack_20,(uint)DAT_0002b5b6,&sStack_26,&iStack_24);
  DAT_febe7078 = sStack_26;
  (*((int *)camry_host_ptr((uint32_t)((0xffffb88cu + (uint32_t)((int)puVar3)))))) = iStack_24;
  return;
}



void FUN_0003b810(void)

{
  int iVar1;
  ushort uVar2;
  int iVar3;
  
  uVar2 = DAT_febe7bf8;
  iVar3 = 7;
  do {
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7061u + (uint32_t)(iVar3) * 1u)))) == '\0') goto LAB_0003b83a;
    iVar1 = iVar3 + -1;
    iVar3 = iVar3 + -1;
  } while (-1 < iVar1);
  DAT_febe7058 = '\x02';
  iVar3 = 7;
  do {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7061u + (uint32_t)(iVar3) * 1u)))) = 0;
    iVar1 = iVar3 + -1;
    iVar3 = iVar3 + -1;
  } while (-1 < iVar1);
LAB_0003b83a:
  iVar3 = 7;
  do {
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7069u + (uint32_t)(iVar3) * 1u)))) == '\0') goto LAB_0003b85a;
    iVar1 = iVar3 + -1;
    iVar3 = iVar3 + -1;
  } while (-1 < iVar1);
  DAT_febe7058 = '\0';
  iVar3 = 7;
  do {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7069u + (uint32_t)(iVar3) * 1u)))) = 0;
    iVar1 = iVar3 + -1;
    iVar3 = iVar3 + -1;
  } while (-1 < iVar1);
LAB_0003b85a:
  if ((((DAT_febe7058 == '\0') || (DAT_febe7058 == '\x03')) && ((uVar2 & 0x22) != 0)) &&
     ((uVar2 & 0x2200) != 0)) {
    DAT_febe7058 = '\x01';
  }
  else if (DAT_febe7058 != '\x01' && DAT_febe7058 != '\x02') {
    return;
  }
  if (((uVar2 & 0x22) == 0) || ((uVar2 & 0x2200) == 0)) {
    DAT_febe7058 = '\x03';
  }
  return;
}



void FUN_0003b88e(void)

{
  undefined *puVar1;
  undefined *puVar2;
  int iVar4;
  char cVar5;
  uint32_t puVar3;
  puVar3 = 0xfebeb800u;
  puVar2 = ((undefined *)camry_host_ptr(0xfebeb800u));
  cVar5 = DAT_febe7072;
  puVar1 = ((undefined *)camry_host_ptr(0xfebeb800u));
  if (DAT_febe7072 == '\0') {
    if ((DAT_febe7dcc != 'Z') || (DAT_febe7bf6 != 'Z')) goto LAB_0003b8dc;
    f33_restore_thermal_offset_terms();
    cVar5 = 'Z';
    puVar1 = ((undefined *)camry_host_ptr((uint32_t)(puVar3)));
  }
  puVar2 = puVar1;
  iVar4 = f33_stage_dual_thermal_squared_inputs(DAT_0002b596,DAT_0002b598);
  DAT_febe7074 = (undefined2)iVar4;
  FUN_0003b76e();
  FUN_0003b810();
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb871u + (uint32_t)((int)camry_host_addr(puVar2)) * 1u)))) = 0x5a;
LAB_0003b8dc:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb872u + (uint32_t)((int)camry_host_addr(puVar2)) * 1u)))) = cVar5;
  return;
}



/* WARNING: Removing unreachable block (ram,0x0003b908) */
/* Reseed selector accumulator7090 from previous<<16 when its signed /65536 narrowed16 disagrees.
   Apply fractional follower with exact coefficient800; add bias to accumulator/output, cap output
   at32000 and return signed16. Exact mode1/3 biases are0. Mismatch to previous quantized estimate
   reseeds per-selector accumulator. Exact coefficient800 follows target with retained fractional
   remainder; bias and upper cap follow. Native composition checks independent accumulators. */

int f33_follow_thermal_offset_target(uint selector,short target,short previous,short bias)

{
  int iVar1;
  int iVar2;
  short sStack_22;
  int iStack_20;
  int iStack_1c;
  F33FractionalFollowing16 FStack_18;
  
  iVar1 = (selector & 0xff) * 4;
  FStack_18.accumulator = *(int *)(((undefined *)camry_host_ptr(0xfebe7090u)) + iVar1);
  if ((int)(short)(FStack_18.accumulator / 0x10000) != (int)previous) {
    FStack_18.accumulator = (int)previous << 0x10;
  }
  FStack_18.previous = previous;
  FStack_18.target = target;
  f33_follow_s16_fractional(&FStack_18,(uint)DAT_0002b594 * 800,&sStack_22,&iStack_1c);
  iVar2 = (int)DAT_0002b596;
  *(int *)(((undefined *)camry_host_ptr(0xfebe7090u)) + iVar1) = bias * 0x10000 + iStack_1c;
  iStack_20 = (int)sStack_22 + (int)bias;
  FUN_00070160(iStack_20,iVar2,&iStack_20);
  return (int)(short)iStack_20;
}



/* Low8 selector indexes two-byte21258 rows without local bounds check. Use7014 offset bank unless
   both7BF8 masks22/2200 are nonzero, then7074. Saturating16 add and clamp[-6400,32000]. First
   selector use bypasses following; initialized modes7058=1/3 follow only for saturated absolute
   change>=128, otherwise set separate completion flags. Low8 selector chooses paired
   normal/alternate offset indices; both7BF8 masks must be nonzero for alternate bank. Saturating
   add/clamp precedes first-use bypass or initialized mode1/3 following. */

int f33_apply_thermal_offset_and_following(uint selector,short raw_estimate,short previous)

{
  char cVar1;
  undefined4 uVar2;
  uint32_t puVar3;
  short sVar4;
  int iVar5;
  int iVar6;
  uint selector_00;
  short local_1c;
  short sStack_1a;
  
  puVar3 = 0xfebeb800u;
  selector_00 = selector & 0xff;
  if (((DAT_febe7bf8 & 0x22) == 0) || ((DAT_febe7bf8 & 0x2200) == 0)) {
    sVar4 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7014u + (uint32_t)(""[selector_00 * 2]) * 2u))));
  }
  else {
    sVar4 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7074u + (uint32_t)(""[selector_00 * 2 + 1]) * 2u))));
  }
  FUN_0006a5fa((int)sVar4 + (int)raw_estimate,&local_1c);
  FUN_00070110((int)local_1c,(int)DAT_0002b59a,(int)DAT_0002b59c,&local_1c);
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb858u + (uint32_t)((int)puVar3) * 1u))));
  FUN_00070706((int)local_1c,(int)previous,&sStack_1a);
  FUN_0006a522((int)sStack_1a,&sStack_1a);
  uVar2 = 0;
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7059u + (uint32_t)(selector_00) * 1u)))) != '\0') {
    if (cVar1 == '\x01') {
      iVar6 = (int)DAT_0002b5a0;
      iVar5 = sStack_1a - iVar6;
      if (iVar5 < 0 == (sStack_1a < 0 != iVar6 < 0 && iVar6 < 0 == iVar5 < 0)) {
        uVar2 = 2;
      }
      else {
        uVar2 = 3;
      }
    }
    else if (cVar1 == '\x03') {
      iVar6 = (int)DAT_0002b5a0;
      iVar5 = sStack_1a - iVar6;
      if (iVar5 < 0 == (sStack_1a < 0 != iVar6 < 0 && iVar6 < 0 == iVar5 < 0)) {
        uVar2 = 4;
      }
      else {
        uVar2 = 5;
      }
    }
    else if (cVar1 == '\0') {
      uVar2 = 1;
    }
    else {
      uVar2 = 6;
    }
  }
  switch(uVar2) {
  case 0:
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7059u + (uint32_t)(selector_00) * 1u)))) = 1;
    break;
  case 2:
    sVar4 = DAT_0002b5a2;
    goto LAB_0003ba5e;
  case 3:
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7061u + (uint32_t)(selector_00) * 1u)))) = 1;
    break;
  case 4:
    sVar4 = DAT_0002b5a4;
LAB_0003ba5e:
    iVar5 = f33_follow_thermal_offset_target(selector_00,local_1c,previous,sVar4);
    local_1c = (short)iVar5;
    break;
  case 5:
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7069u + (uint32_t)(selector_00) * 1u)))) = 1;
  }
  return (int)local_1c;
}



void FUN_0003ba78(void)

{
  DAT_febe70b4 = 0;
  DAT_febe70b8 = 0;
  DAT_febe70b0 = 0;
  return;
}



void FUN_0003ba84(void)

{
  DAT_febe707a = 0;
  DAT_febe707c = 0;
  DAT_febe70bc = 0;
  DAT_febe70c0 = 0;
  return;
}



/* f33_reset_windowed_monitor wrapper resetting exactly one monitor state
   ((0xfebe70c8u)); whole-body shape-verified from the canonical corpus.
   Per-instance semantics derive from the referenced state cell; not individually executed. */

void f33_reset_scalar_monitor_3bab2(void)

{
  f33_reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)((0xfebe70c8u)))));
  return;
}



/* f33_reset_windowed_monitor wrapper resetting exactly one monitor state
   ((0xfebe70c8u)); whole-body shape-verified from the canonical corpus.
   Per-instance semantics derive from the referenced state cell; not individually executed. */

void f33_reset_scalar_monitor_3bab2_3baa2(void)

{
  f33_reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)((0xfebe70c8u)))));
  return;
}



/* State70C8 -> slot20 index0. Predicate81D0=5A fails. Windowed qualifier limits pass2/windowFFFF
   and fail3/window6; confirmed failure latches. EventD3; published status is low result byte. */

void f33_step_acquisition_status_a_monitor(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bb38 == 'Z') {
    f33_reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)((0xfebe70c8u)))));
  }
  else {
    f33_step_windowed_monitor
              (((F33WindowedMonitorState *)camry_host_ptr((uint32_t)((0xfebe70c8u)))), ((F33WindowedMonitorLimits *)camry_host_ptr((uint32_t)((0x2b5e0u)))), ((F33TwoSidedMonitorCallbacks *)camry_host_ptr((uint32_t)((0x27fccu)))));
  }
  f33_publish_acquisition_monitor_status('\0',(*((uint *)camry_host_ptr((uint32_t)((0xffffb8c8u + (uint32_t)((int)puVar1)))))));
  return;
}



/* 81D0=5A returns22; any other byte returns11. Full R10 is defined. */

uint f33_classify_acquisition_status_a(void)

{
  if (DAT_febe81d0 == 'Z') {
    return 0x22;
  }
  return 0x11;
}



/* Report eventD3 through51E2C/52A2A healthy-observed bitmap; does not clear current failure
   history. */

void f33_report_scalar_event_d3_healthy_observed(void)

{
  f33_report_diagnostic_healthy_observed(0xd3);
  return;
}



/* Report eventD3 with capture kind10; diagnostic admission remains in51C66. */

void f33_report_scalar_event_d3_failure(void)

{
  f33_report_diagnostic_event_failure(0xd3,10);
  return;
}



/* f33_reset_windowed_monitor wrapper resetting exactly one monitor state
   ((0xfebe70d8u)); whole-body shape-verified from the canonical corpus.
   Per-instance semantics derive from the referenced state cell; not individually executed. */

void f33_reset_scalar_monitor_3bb44(void)

{
  f33_reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)((0xfebe70d8u)))));
  return;
}



/* f33_reset_windowed_monitor wrapper resetting exactly one monitor state
   ((0xfebe70d8u)); whole-body shape-verified from the canonical corpus.
   Per-instance semantics derive from the referenced state cell; not individually executed. */

void f33_reset_scalar_monitor_3bb44_3bb34(void)

{
  f33_reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)((0xfebe70d8u)))));
  return;
}



/* State70D8 -> slot20 index1. Predicate81D1=5A fails. Same windowed2/FFFF/3/6 limits; eventD4.
   Status flags are staged from380A/B through66932 and50A06, not physical timing proof. */

void f33_step_acquisition_status_b_monitor(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bb3c == 'Z') {
    f33_reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)((0xfebe70d8u)))));
  }
  else {
    f33_step_windowed_monitor
              (((F33WindowedMonitorState *)camry_host_ptr((uint32_t)((0xfebe70d8u)))), ((F33WindowedMonitorLimits *)camry_host_ptr((uint32_t)((0x2b5e8u)))), ((F33TwoSidedMonitorCallbacks *)camry_host_ptr((uint32_t)((0x28000u)))));
  }
  f33_publish_acquisition_monitor_status('\x01',(*((uint *)camry_host_ptr((uint32_t)((0xffffb8d8u + (uint32_t)((int)puVar1)))))));
  return;
}



/* 81D1=5A returns22; any other byte returns11. Full R10 is defined. */

uint f33_classify_acquisition_status_b(void)

{
  if (DAT_febe81d1 == 'Z') {
    return 0x22;
  }
  return 0x11;
}



/* Report eventD4 through51E2C/52A2A healthy-observed bitmap; does not clear current failure
   history. */

void f33_report_scalar_event_d4_healthy_observed(void)

{
  f33_report_diagnostic_healthy_observed(0xd4);
  return;
}



/* Report eventD4 with capture kind10; diagnostic admission remains in51C66. */

void f33_report_scalar_event_d4_failure(void)

{
  f33_report_diagnostic_event_failure(0xd4,10);
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_3bbb6(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_3bbb8(void)

{
  return;
}



/* Always retain/clear slot20; any confirmed mask22 among70E8..EB selects kind31,then select
   current. Any nonzero source status sets diagnostic-cache blocker1=11. Unlike shared startup-stage
   producers, an all-clear invocation replaces current with zero. Native acquisition scheduler
   interval publishes slot20 action on confirmation despite closed diagnostic lifecycle admission;
   expiry instead clears current action and retains the prior record. */

void f33_publish_acquisition_monitor_actions(void)

{
  uint32_t puVar1;
  uchar status;
  
  puVar1 = 0xfebeb800u;
  f33_retain_and_clear_fault_record(0x14);
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb8ebu + (uint32_t)((int)puVar1) * 1u)))) |
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb8eau + (uint32_t)((int)puVar1) * 1u)))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb8e9u + (uint32_t)((int)puVar1) * 1u)))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb8e8u + (uint32_t)((int)puVar1) * 1u))))) &
      0x22) == 0x22) {
    f33_encode_fault_action_kind('\x14','1');
  }
  f33_select_current_fault_record(0x14);
  status = '\0';
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb8ebu + (uint32_t)((int)puVar1) * 1u)))) != '\0' ||
      ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb8eau + (uint32_t)((int)puVar1) * 1u)))) != '\0' ||
      ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb8e9u + (uint32_t)((int)puVar1) * 1u)))) != '\0' || (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb8e8u + (uint32_t)((int)puVar1) * 1u)))) != '\0'))) {
    status = '\x11';
  }
  f33_set_diagnostic_cache_blocker('\x01',status);
  return;
}



/* If low8(index)<4, store low8(packed_status) to FEBE70E8+index. Other bits of the packed qualifier
   result are not published. */

void f33_publish_acquisition_monitor_status(uchar index,uint packed_status)

{
  if (index < 4) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe70e8u + (uint32_t)(index) * 1u)))) = (char)packed_status;
  }
  return;
}



/* f33_reset_latched_monitor wrapper resetting exactly one monitor state
   ((0xfebe70ecu)); whole-body shape-verified from the canonical corpus.
   Per-instance semantics derive from the referenced state cell; not individually executed. */

void f33_reset_scalar_monitor_3bc4c(void)

{
  f33_reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebe70ecu)))));
  return;
}



/* f33_reset_latched_monitor wrapper resetting exactly one monitor state
   ((0xfebe70ecu)); whole-body shape-verified from the canonical corpus.
   Per-instance semantics derive from the referenced state cell; not individually executed. */

void f33_reset_scalar_monitor_3bc4c_3bc3c(void)

{
  f33_reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebe70ecu)))));
  return;
}



/* State70EC -> slot20 index2. Predicate requires81D4=5A, then unsigned81D6>=61211 and81D8<=3093.
   Latched limits2/20; eventD6. Do not reinterpret these two separate unsigned bounds as a signed
   interval. */

void f33_step_acquisition_range_a_monitor(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bb40 == 'Z') {
    f33_reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebe70ecu)))));
  }
  else {
    f33_step_latched_monitor
              (((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebe70ecu)))), ((F33MonitorLimits *)camry_host_ptr((uint32_t)((0x2b5f0u)))), ((F33TwoSidedMonitorCallbacks *)camry_host_ptr((uint32_t)((0x28034u)))));
  }
  f33_publish_acquisition_monitor_status('\x02',(*((uint *)camry_host_ptr((uint32_t)((0xffffb8ecu + (uint32_t)((int)puVar1)))))));
  return;
}



/* 81D4!=5A returns44. Otherwise unsigned81D6>=61211 AND81D8<=3093 returns11,else22. Separate lower
   and upper samples, not a signed scalar range. */

uint f33_classify_acquisition_range_a(void)

{
  if (DAT_febe81d4 != 'Z') {
    return 0x44;
  }
  if ((DAT_0002b5f8 <= DAT_febe81d6) && (DAT_febe81d8 <= DAT_0002b5fa)) {
    return 0x11;
  }
  return 0x22;
}



/* Report eventD6 through51E2C/52A2A healthy-observed bitmap; does not clear current failure
   history. */

void f33_report_scalar_event_d6_healthy_observed(void)

{
  f33_report_diagnostic_healthy_observed(0xd6);
  return;
}



/* Report eventD6 with capture kind10; diagnostic admission remains in51C66. */

void f33_report_scalar_event_d6_failure(void)

{
  f33_report_diagnostic_event_failure(0xd6,10);
  return;
}



/* f33_reset_latched_monitor wrapper resetting exactly one monitor state
   ((0xfebe70f8u)); whole-body shape-verified from the canonical corpus.
   Per-instance semantics derive from the referenced state cell; not individually executed. */

void f33_reset_scalar_monitor_3bcfc(void)

{
  f33_reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebe70f8u)))));
  return;
}



/* f33_reset_latched_monitor wrapper resetting exactly one monitor state
   ((0xfebe70f8u)); whole-body shape-verified from the canonical corpus.
   Per-instance semantics derive from the referenced state cell; not individually executed. */

void f33_reset_scalar_monitor_3bcfc_3bcec(void)

{
  f33_reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebe70f8u)))));
  return;
}



/* State70F8 -> slot20 index3. Valid81D5 gates unsigned81DA>=61211 and81DC<=3093. Latched
   limits2/20; eventD7. */

void f33_step_acquisition_range_b_monitor(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bb44 == 'Z') {
    f33_reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebe70f8u)))));
  }
  else {
    f33_step_latched_monitor
              (((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebe70f8u)))), ((F33MonitorLimits *)camry_host_ptr((uint32_t)((0x2b5f4u)))), ((F33TwoSidedMonitorCallbacks *)camry_host_ptr((uint32_t)((0x28068u)))));
  }
  f33_publish_acquisition_monitor_status('\x03',(*((uint *)camry_host_ptr((uint32_t)((0xffffb8f8u + (uint32_t)((int)puVar1)))))));
  return;
}



/* 81D5!=5A returns44. Otherwise unsigned81DA>=61211 AND81DC<=3093 returns11,else22. */

uint f33_classify_acquisition_range_b(void)

{
  if (DAT_febe81d5 != 'Z') {
    return 0x44;
  }
  if ((DAT_0002b5fc <= DAT_febe81da) && (DAT_febe81dc <= DAT_0002b5fe)) {
    return 0x11;
  }
  return 0x22;
}



/* Report eventD7 through51E2C/52A2A healthy-observed bitmap; does not clear current failure
   history. */

void f33_report_scalar_event_d7_healthy_observed(void)

{
  f33_report_diagnostic_healthy_observed(0xd7);
  return;
}



/* Report eventD7 with capture kind10; diagnostic admission remains in51C66. */

void f33_report_scalar_event_d7_failure(void)

{
  f33_report_diagnostic_event_failure(0xd7,10);
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_3bd8c(void)

{
  return;
}



char FUN_0003bd8e(uint param_1)

{
  char cVar1;
  uint saved_mask;
  char cVar2;
  
  cVar2 = '\0';
  if ((param_1 & 0xff) < 3) {
    saved_mask = f33_priority_mask_enter(0xffc0);
    cVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7104u + (uint32_t)(param_1 & 0xff) * 1u))));
    if (((int8_t)cVar2) != -1) {
      cVar1 = cVar2 + '\x01';
      cVar2 = cVar2 + '\x01';
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7104u + (uint32_t)(param_1 & 0xff) * 1u)))) = cVar1;
    }
    f33_priority_mask_restore(saved_mask);
  }
  return cVar2;
}



/* Under PMRFFC0 publish71EC and XOR copies7108/710A, plus minimum enabled317E0 entry at71F2
   (default22170). Bits0/1 select14965, bits2..8 select11085, remaining bits select22170. This is an
   amplitude bound, not a command or an age counter. Publish redundant qualification and minimum
   active317E0 amplitude bound under PMRFFC0. Bits0/1=14965;2..8=11085;others/default22170. Neither
   command magnitude nor age. */

void f33_publish_fault_qualification_limit(ushort classes)

{
  uint uVar1;
  uint32_t puVar2;
  uint uVar3;
  uint uVar4;
  
  puVar2 = 0xfebeb800u;
  uVar3 = 0x569a;
  if (classes != 0) {
    uVar1 = 0;
    uVar4 = uVar3;
    do {
      uVar3 = uVar4;
      if (((classes >> (uVar1 & 0x1f) & 1) != 0) &&
         (uVar3 = (uint)f33_fault_class_amplitude_limits[uVar1], (int)(uVar4 - uVar3) < 0)) {
        uVar3 = uVar4;
      }
      uVar1 = uVar1 + 1;
      uVar4 = uVar3;
    } while (uVar1 < 0x10);
  }
  uVar1 = f33_priority_mask_enter(0xffc0);
  f33_publish_redundant_u16
            (classes,((ushort *)camry_host_ptr((uint32_t)((0xffffb9ecu + (uint32_t)((int)puVar2))))),((ushort *)camry_host_ptr((uint32_t)((0xffffb908u + (uint32_t)((int)puVar2)))))
             ,((ushort *)camry_host_ptr((uint32_t)((0xffffb90au + (uint32_t)((int)puVar2))))));
  (*((short *)camry_host_ptr((uint32_t)((0xffffb9f2u + (uint32_t)((int)puVar2)))))) = (short)uVar3;
  f33_priority_mask_restore(uVar1);
  return;
}



void FUN_0003be22(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  iVar4 = 0;
  do {
    iVar3 = iVar4 * 2;
    *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe710cu)) + iVar3) = 0xffff;
    iVar2 = iVar4 + 1;
    *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe713cu)) + iVar3) = 0xffff;
    iVar1 = iVar4 + -0x17;
    *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe716cu)) + iVar3) = 0xffff;
    *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe719cu)) + iVar3) = 0xffff;
    iVar4 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  f33_publish_fault_qualification_limit(0);
  return;
}



void FUN_0003be52(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  f33_publish_fault_qualification_limit(0);
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb9eeu + (uint32_t)((int)puVar1)))))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffbc40u + (uint32_t)((int)puVar1)))))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffbc42u + (uint32_t)((int)puVar1)))))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffbc44u + (uint32_t)((int)puVar1)))))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffbc46u + (uint32_t)((int)puVar1)))))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffbc48u + (uint32_t)((int)puVar1)))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb9e4u + (uint32_t)((int)puVar1) * 1u)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb9e5u + (uint32_t)((int)puVar1) * 1u)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb9e6u + (uint32_t)((int)puVar1) * 1u)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb9e7u + (uint32_t)((int)puVar1) * 1u)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb9e8u + (uint32_t)((int)puVar1) * 1u)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb9e9u + (uint32_t)((int)puVar1) * 1u)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb9eau + (uint32_t)((int)puVar1) * 1u)))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb9f0u + (uint32_t)((int)puVar1)))))) = 0;
  return;
}



/* Classify low16 mask into71EE: zero->0, one bit->that bit, multiple bits->8000. These internal
   classes are not diagnostic event IDs or OEM fault names. Low16 class mask becomes zero, the
   original single bit, or8000 for multiple bits; publish71EE. */

void f33_classify_fault_qualification(uint classes)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  
  DAT_febe71ee = 0;
  if ((classes & 0xffff) != 0) {
    uVar3 = 0;
    uVar4 = 0;
    do {
      uVar5 = uVar4;
      if ((((classes & 0xffff) >> (uVar3 & 0x1f) & 1) != 0) && (uVar5 = 0x8000, uVar4 == 0)) {
        uVar5 = 1 << (uVar3 & 0x1f) & 0xffff;
      }
      DAT_febe71ee = (undefined2)uVar5;
      uVar2 = uVar3 + 1;
      iVar1 = uVar3 - 0xf;
      uVar3 = uVar2;
      uVar4 = uVar5;
    } while (iVar1 < 0 != ((int)uVar2 < 0 && -1 < iVar1));
  }
  return;
}



/* Vote71EC with XOR5555/XORAAAA copies7108/710A using707AC; ignore voter status and return the
   voted unsigned16 value in full R10. Vote71EC with XOR copies7108/710A; voter status is ignored
   and voted unsigned16 is returned in fullR10. */

uint f33_vote_fault_qualification(void)

{
  ushort uStack_6;
  
  FUN_000707ac(((undefined *)camry_host_ptr(0xfebe71ecu)),((undefined *)camry_host_ptr(0xfebe7108u)),((undefined *)camry_host_ptr(0xfebe710au)),&uStack_6);
  return (uint)uStack_6;
}



/* Candidate71EE intersecting317DA=3E1C becomes8000. Nonzero candidate disjoint from nonzero prior
   vote also becomes8000, then OR prior. Zero candidate retains prior except clears4000 if prior
   bit15 is clear. Publish redundant qualification/limit;71E4=5A only for prior0 -> new nonzero.
   Sticky mask3E1C and incompatible nonzero classes promote candidate8000 before ORing prior
   qualification. Zero candidate retains prior except4000 without bit15. First nonzero transition
   alone sets71E4. */

void f33_update_fault_qualification(void)

{
  ushort uVar1;
  undefined1 uVar2;
  uint32_t puVar3;
  uint uVar4;
  uint uVar5;
  
  uVar1 = DAT_febe71ee;
  puVar3 = 0xfebeb800u;
  uVar5 = (uint)DAT_febe71ee;
  uVar4 = f33_vote_fault_qualification();
  if ((DAT_000317da & uVar1) == 0) {
    if (uVar5 == 0) {
      uVar5 = uVar4;
      if ((uVar4 >> 0xf & 1) == 0) {
        uVar5 = uVar4 & 0xffffbfff;
      }
      goto LAB_0003bf1c;
    }
  }
  else {
    uVar5 = 0x8000;
  }
  if (((uVar5 & uVar4) == 0) && (uVar4 != 0)) {
    uVar5 = 0x8000;
  }
  uVar5 = uVar4 | uVar5;
LAB_0003bf1c:
  f33_publish_fault_qualification_limit((ushort)uVar5);
  if ((uVar4 == 0) && (uVar5 != 0)) {
    uVar2 = 0x5a;
  }
  else {
    uVar2 = 0;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb9e4u + (uint32_t)((int)puVar3) * 1u)))) = uVar2;
  return;
}



/* On first nonzero qualification71E4==5A, strip masks12/70/C00 from current records whose word4
   intersects71EC, repairing word0 complements. Retained records are untouched. With71EC.bit15,
   accumulate those masks in7440/42/44 and retain7446; otherwise clear overrides. First
   qualification strips current-source masks12/70/C00 and repairs word0 complements, not retained
   records. Bit15 retains masked overrides; otherwise overrides clear. */

void f33_maintain_qualified_fault_actions
               (ushort mode_actions,ushort status_actions,ushort output_actions)

{
  int iVar1;
  int iVar2;
  byte *pbVar3;
  ushort uVar4;
  ushort uVar5;
  ushort uVar6;
  ushort uVar7;
  ushort uVar8;
  int iVar9;
  
  uVar4 = DAT_febe71ec;
  if (DAT_febe71e4 == 'Z') {
    iVar9 = 0;
    do {
      if (((*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7208u + (uint32_t)(iVar9 * 6) * 2u)))) & uVar4) != 0) {
        uVar5 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7200u + (uint32_t)(iVar9 * 6) * 2u))));
        pbVar3 = ((byte *)camry_host_ptr((uint32_t)((int)0xfebe7204u + iVar9 * 0xc + 1)));
        *pbVar3 = *pbVar3 & 0xf7;
        pbVar3 = ((byte *)camry_host_ptr((uint32_t)((int)0xfebe7204u + iVar9 * 0xc + 1)));
        *pbVar3 = *pbVar3 & 0xfb;
        (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7200u + (uint32_t)(iVar9 * 6) * 2u)))) = uVar5 & 0xffed;
        (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7202u + (uint32_t)(iVar9 * 6) * 2u)))) = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7202u + (uint32_t)(iVar9 * 6) * 2u)))) & 0xff8f;
        *(ushort *)(((undefined *)camry_host_ptr(0xfebe713cu)) + iVar9 * 2) = *(ushort *)(((undefined *)camry_host_ptr(0xfebe713cu)) + iVar9 * 2) | 0x12;
      }
      iVar2 = iVar9 + 1;
      iVar1 = iVar9 + -0x17;
      iVar9 = iVar2;
    } while (((iVar1 < 0) || (iVar2 < 0)));
  }
  uVar8 = uVar4 & 0x8000;
  uVar5 = uVar8;
  uVar6 = uVar8;
  uVar7 = uVar8;
  if ((uVar4 & 0x8000) != 0) {
    uVar8 = DAT_febe7440 | mode_actions & 0x12;
    uVar5 = DAT_febe7446;
    uVar6 = DAT_febe7444 | output_actions & 0xc00;
    uVar7 = DAT_febe7442 | status_actions & 0x70;
  }
  DAT_febe7440 = uVar8;
  DAT_febe7442 = uVar7;
  DAT_febe7444 = uVar6;
  DAT_febe7446 = uVar5;
  return;
}



/* Optionally OR317D8 into local word4 only when317D4==5A (exact byte0 disables). Classify word4,
   advance retained qualification, then maintain current records and overrides from the original
   action words. Does not replace the caller's aggregate words. Optional exact-disabled class
   override precedes class reduction, retained qualification and action maintenance. Caller
   aggregate is not replaced by source-record stripping. */

void f33_qualify_fault_action_aggregate(ushort *actions)

{
  ushort mode_actions;
  ushort status_actions;
  ushort output_actions;
  ushort uVar1;
  
  mode_actions = *actions;
  status_actions = actions[1];
  output_actions = actions[2];
  uVar1 = actions[4];
  if (DAT_000317d4 == 'Z') {
    uVar1 = uVar1 | DAT_000317d8;
  }
  f33_classify_fault_qualification((uint)uVar1);
  f33_update_fault_qualification();
  f33_maintain_qualified_fault_actions(mode_actions,status_actions,output_actions);
  return;
}


