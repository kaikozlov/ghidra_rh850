#include "common.h"


/* WARNING: Removing unreachable block (ram,0x0003433a) */
/* Family0600 active5A sequencer: positive and negative1280 stimulus, bounded delayed angle
   averaging and independent signed component sum, paired correction staging, mean agreement, queued
   records0208/0209. Abort response-6 resets live request but retains count/sums. Completion polls
   only RAM marker. */

void f33_step_mode600_stimulus_fit(void)

{
  uint uVar1;
  short sVar2;
  uint uVar3;
  int iVar4;
  undefined *puVar5;
  uint32_t puVar8;
  int iVar9;
  int iVar10;
  int iVar11;
  int iVar12;
  uint uVar13;
  ushort uVar14;
  uint uVar15;
  uchar uStack_25;
  uchar uStack_24;
  uchar uStack_23;
  short sStack_22;
  short sStack_20;
  ushort uStack_1e;
  short sStack_1c;
  short sStack_1a;
  short asStack_18 [2];
  uint32_t puVar6;
  uint32_t puVar7;
  uVar13 = f33_mode600_stimulus_fit_work.signed_component_sum;
  iVar12 = f33_mode600_stimulus_fit_work.folded_angle_sum;
  uVar14 = f33_mode600_stimulus_fit_work.sample_count;
  puVar8 = 0xfebeb800u;
  puVar7 = 0xfebeb800u;
  puVar6 = 0xfebeb800u;
  puVar5 = ((undefined *)camry_host_ptr(0xfebeb800u));
  uStack_24 = f33_mode600_stimulus_fit_work.active;
  if ((DAT_febeeacc & 0xff00) != 0x600) {
    return;
  }
  if (f33_mode600_stimulus_fit_work.active != 'Z') {
    return;
  }
  iVar9 = (int)f33_mode600_stimulus_fit_work.positive_mean;
  iVar10 = (int)f33_mode600_stimulus_fit_work.negative_mean;
  uStack_25 = f33_mode600_stimulus_fit_work.stimulus_valid;
  sStack_1c = f33_mode600_stimulus_fit_work.stimulus;
  sStack_22 = f33_mode600_stimulus_fit_work.positive_mean;
  sStack_20 = f33_mode600_stimulus_fit_work.negative_mean;
  uStack_1e = f33_mode600_stimulus_fit_work.hold_count;
  uVar15 = (uint)f33_mode600_stimulus_fit_work.sample_count;
  uStack_23 = f33_mode600_stimulus_fit_work.state;
  if ((f33_fit_parameters.mode600_input_upper < DAT_febeeac4) ||
     (DAT_febe7db0 < f33_fit_parameters.mode600_qualifier_lower)) goto switchD_000340ae_caseD_15;
  if (0x1f < f33_mode600_stimulus_fit_work.state) {
    if (0x20 < f33_mode600_stimulus_fit_work.state) {
      if (f33_mode600_stimulus_fit_work.state != '!') {
        if (f33_mode600_stimulus_fit_work.state < 0x23) goto switchD_000340ae_caseD_12;
        if (f33_mode600_stimulus_fit_work.state == '#') goto switchD_000340ae_caseD_13;
        if (f33_mode600_stimulus_fit_work.state == '$') goto switchD_000340ae_caseD_14;
        if (f33_mode600_stimulus_fit_work.state == '&') goto switchD_000340ae_caseD_16;
        if (f33_mode600_stimulus_fit_work.state == '1') {
          iVar4 = iVar9 - iVar10;
          if (iVar9 - iVar10 < 0) {
            iVar4 = -iVar4;
          }
          iVar11 = (int)f33_fit_parameters.pass_difference_limit;
          if (iVar4 - iVar11 < 0 != (iVar4 < 0 != iVar11 < 0 && iVar11 < 0 == iVar4 - iVar11 < 0) ||
              iVar4 == iVar11) {
            uVar3 = 0;
            do {
              uVar1 = uVar3 + 1;
              asStack_18[uVar3] = -(short)((iVar10 + iVar9) / 2);
              uVar3 = uVar1;
            } while (uVar1 < 2);
            f33_stage_pair_correction('\0',asStack_18);
            f33_queue_pair_correction_records();
            uStack_23 = 0xff;
            puVar5 = ((undefined *)camry_host_ptr((uint32_t)(puVar8)));
            goto LAB_00034204;
          }
        }
        else if (f33_mode600_stimulus_fit_work.state == 0xff) {
          if (DAT_febe68b4 == -0x5aa5a55b) {
            uStack_24 = '\0';
            uStack_25 = '\0';
            uStack_23 = '\x10';
            puVar5 = ((undefined *)camry_host_ptr((uint32_t)(puVar7)));
            FUN_00034ea4(0,0);
            f33_cancel_mode600_stimulus_fit();
          }
          goto LAB_000343b2;
        }
        goto switchD_000340ae_caseD_15;
      }
      goto switchD_000340ae_caseD_11;
    }
    uVar15 = 0;
    do {
      uVar3 = uVar15 + 1;
      asStack_18[uVar15] = 0;
      uVar15 = uVar3;
    } while (uVar3 < 2);
    puVar5 = ((undefined *)camry_host_ptr((uint32_t)(puVar7)));
    f33_stage_pair_correction('\0',asStack_18);
    sStack_1c = -f33_fit_parameters.stimulus;
    uStack_23 = '!';
LAB_0003415e:
    uStack_1e = 0;
    uStack_25 = 'Z';
    goto LAB_000343b2;
  }
  switch(f33_mode600_stimulus_fit_work.state) {
  case '\x10':
    sStack_20 = 0;
    sStack_22 = 0;
    uVar15 = 0;
    do {
      uVar3 = uVar15 + 1;
      asStack_18[uVar15] = 0;
      uVar15 = uVar3;
    } while (uVar3 < 2);
    puVar5 = ((undefined *)camry_host_ptr((uint32_t)(puVar7)));
    f33_stage_pair_correction('\0',asStack_18);
    sStack_1c = f33_fit_parameters.stimulus;
    uStack_23 = '\x11';
    goto LAB_0003415e;
  case '\x11':
switchD_000340ae_caseD_11:
    if (f33_fit_parameters.initial_hold_calls <= f33_mode600_stimulus_fit_work.hold_count) {
      uVar15 = 0;
      iVar12 = 0;
      uStack_23 = '\"';
      puVar5 = ((undefined *)camry_host_ptr(0xfebeb800u));
      if (f33_mode600_stimulus_fit_work.state == '\x11') {
        uStack_23 = '\x12';
      }
LAB_00034204:
      uVar14 = (ushort)uVar15;
      goto LAB_000343b2;
    }
    break;
  case '\x12':
switchD_000340ae_caseD_12:
    iVar9 = (int)f33_fit_parameters.sample_admission;
    iVar10 = (int)((int)(int16_t)DAT_febe5f36);
    if (f33_mode600_stimulus_fit_work.state == '\x12') {
      if (iVar10 - iVar9 < 0 == (iVar10 < 0 != iVar9 < 0 && iVar9 < 0 == iVar10 - iVar9 < 0)) {
LAB_000341a0:
        uVar3 = (uint)f33_fit_parameters.sample_count;
        if (uVar15 < uVar3) {
          uVar14 = f33_mode600_stimulus_fit_work.sample_count + 1;
          puVar5 = ((undefined *)camry_host_ptr(0xfebeb800u));
          FUN_00070be0((int)(short)(((int)(int16_t)DAT_febe6c44) + ((int)(int16_t)DAT_febe6c40)),
                       (int)(short)(((int)(int16_t)DAT_febe6c46) + ((int)(int16_t)DAT_febe6c42)),&sStack_1a);
          iVar9 = (int)sStack_1a;
          if (iVar9 + -0x4000 < 0 == (iVar9 < 0 && -1 < iVar9 + -0x4000) && iVar9 != 0x4000) {
            iVar9 = iVar9 + -0x8000;
          }
          else if (iVar9 + 0x4000 < 0 != (-1 < iVar9 && iVar9 + 0x4000 < 0)) {
            iVar9 = iVar9 + 0x8000;
          }
          iVar12 = iVar12 + iVar9;
          goto LAB_000343b2;
        }
        iVar9 = f33_mode600_stimulus_fit_work.folded_angle_sum;
        if (uVar3 != 0) {
          if (f33_mode600_stimulus_fit_work.folded_angle_sum == -0x80000000 && uVar3 == 0xffffffff)
          {
            iVar9 = 0;
          }
          else {
            iVar9 = f33_mode600_stimulus_fit_work.folded_angle_sum / (int)uVar3;
          }
        }
        sVar2 = (short)iVar9;
        iVar9 = (int)sVar2;
        if (iVar9 + 0x7fff < 0 == (-1 < iVar9 && iVar9 + 0x7fff < 0) && iVar9 != -0x7fff) {
          if (iVar9 < 0) {
            iVar9 = (int)-sVar2;
          }
        }
        else {
          iVar9 = 0x7fff;
        }
        iVar10 = (int)f33_fit_parameters.folded_angle_limit;
        if (iVar9 - iVar10 < 0 != (iVar9 < 0 != iVar10 < 0 && iVar10 < 0 == iVar9 - iVar10 < 0) ||
            iVar9 == iVar10) {
          uStack_1e = 0;
          uVar3 = 0;
          if (f33_mode600_stimulus_fit_work.state == '\x12') {
            do {
              uVar1 = uVar3 + 1;
              asStack_18[uVar3] = -sVar2;
              uVar3 = uVar1;
            } while (uVar1 < 2);
            sStack_22 = sVar2;
            f33_stage_pair_correction('\0',asStack_18);
            uStack_23 = '\x13';
            puVar5 = ((undefined *)camry_host_ptr((uint32_t)(puVar7)));
          }
          else {
            do {
              uVar1 = uVar3 + 1;
              asStack_18[uVar3] = -sVar2;
              uVar3 = uVar1;
            } while (uVar1 < 2);
            sStack_20 = sVar2;
            f33_stage_pair_correction('\0',asStack_18);
            uStack_23 = '#';
            puVar5 = ((undefined *)camry_host_ptr((uint32_t)(puVar6)));
          }
          goto LAB_00034204;
        }
      }
    }
    else {
      iVar4 = -iVar9;
      if (iVar10 + iVar9 < 0 != (iVar10 < 0 != iVar4 < 0 && iVar4 < 0 == iVar10 + iVar9 < 0) ||
          iVar10 == iVar4) goto LAB_000341a0;
    }
  default:
switchD_000340ae_caseD_15:
    puVar5 = ((undefined *)camry_host_ptr(0xfebeb800u));
    f33_abort_mode600_stimulus_fit
              (&uStack_24,&uStack_25,&sStack_1c,&uStack_1e,&sStack_22,&sStack_20,&uStack_23);
    goto LAB_000343b2;
  case '\x13':
switchD_000340ae_caseD_13:
    if (f33_fit_parameters.recheck_hold_calls <= f33_mode600_stimulus_fit_work.hold_count) {
      uVar13 = 0;
      uStack_23 = '$';
      uVar15 = uVar13;
      puVar5 = ((undefined *)camry_host_ptr(0xfebeb800u));
      if (f33_mode600_stimulus_fit_work.state == '\x13') {
        uStack_23 = '\x14';
        uVar15 = 0;
      }
      goto LAB_00034204;
    }
    break;
  case '\x14':
switchD_000340ae_caseD_14:
    iVar9 = (int)((int)(int16_t)DAT_febe5f36);
    if (iVar9 + 0x7fff < 0 == (-1 < iVar9 && iVar9 + 0x7fff < 0) && iVar9 != -0x7fff) {
      if (iVar9 < 0) {
        iVar9 = (int)-((int)(int16_t)DAT_febe5f36);
      }
    }
    else {
      iVar9 = 0x7fff;
    }
    iVar10 = (int)f33_fit_parameters.sample_admission;
    if (iVar9 - iVar10 < 0 == (iVar9 < 0 != iVar10 < 0 && iVar10 < 0 == iVar9 - iVar10 < 0)) {
      if (uVar15 < f33_fit_parameters.sample_count) {
        uVar14 = f33_mode600_stimulus_fit_work.sample_count + 1;
        uVar13 = f33_mode600_stimulus_fit_work.signed_component_sum +
                 (int)((int)(int16_t)DAT_febe6c44) + (int)((int)(int16_t)DAT_febe6c40);
        goto LAB_000343b2;
      }
      if (f33_mode600_stimulus_fit_work.signed_component_sum + 0x7fffffff < 0 ==
          (-1 < f33_mode600_stimulus_fit_work.signed_component_sum &&
          f33_mode600_stimulus_fit_work.signed_component_sum + 0x7fffffff < 0) &&
          f33_mode600_stimulus_fit_work.signed_component_sum != -0x7fffffff) {
        iVar9 = f33_mode600_stimulus_fit_work.signed_component_sum;
        if (f33_mode600_stimulus_fit_work.signed_component_sum < 0) {
          iVar9 = -f33_mode600_stimulus_fit_work.signed_component_sum;
        }
      }
      else {
        iVar9 = 0x7fffffff;
      }
      iVar10 = (int)f33_fit_parameters.component_mean_limit * (uint)f33_fit_parameters.sample_count;
      if (iVar9 - iVar10 < 0 != (iVar9 < 0 != iVar10 < 0 && iVar10 < 0 == iVar9 - iVar10 < 0) ||
          iVar9 == iVar10) {
        sStack_1c = 0;
        uStack_23 = '&';
        uStack_25 = 'Z';
        uStack_1e = 0;
        puVar5 = ((undefined *)camry_host_ptr(0xfebeb800u));
        if (f33_mode600_stimulus_fit_work.state == '\x14') {
          uStack_23 = '\x16';
        }
        goto LAB_00034204;
      }
    }
    goto switchD_000340ae_caseD_15;
  case '\x16':
switchD_000340ae_caseD_16:
    if (f33_fit_parameters.release_hold_calls <= f33_mode600_stimulus_fit_work.hold_count) {
      uStack_23 = '1';
      puVar5 = ((undefined *)camry_host_ptr(0xfebeb800u));
      if (f33_mode600_stimulus_fit_work.state == '\x16') {
        uStack_23 = ' ';
      }
      goto LAB_00034204;
    }
  }
  uStack_1e = f33_mode600_stimulus_fit_work.hold_count + 1;
LAB_000343b2:
  *(ushort *)(((undefined *)camry_host_ptr(0xffffb26cu)) + (int)camry_host_addr(puVar5)) = uVar14;
  *(short *)(((undefined *)camry_host_ptr(0xffffb268u)) + (int)camry_host_addr(puVar5)) = sStack_1c;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb261u + (uint32_t)((int)camry_host_addr(puVar5)) * 1u)))) = uStack_24;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb262u + (uint32_t)((int)camry_host_addr(puVar5)) * 1u)))) = uStack_25;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb260u + (uint32_t)((int)camry_host_addr(puVar5)) * 1u)))) = uStack_23;
  *(short *)(((undefined *)camry_host_ptr(0xffffb264u)) + (int)camry_host_addr(puVar5)) = sStack_22;
  *(short *)(((undefined *)camry_host_ptr(0xffffb266u)) + (int)camry_host_addr(puVar5)) = sStack_20;
  *(int *)(((undefined *)camry_host_ptr(0xffffb270u)) + (int)camry_host_addr(puVar5)) = iVar12;
  *(uint *)(((undefined *)camry_host_ptr(0xffffb274u)) + (int)camry_host_addr(puVar5)) = uVar13;
  *(ushort *)(((undefined *)camry_host_ptr(0xffffb26au)) + (int)camry_host_addr(puVar5)) = uStack_1e;
  return;
}



/* Set active6A61=5A then full initializer33FAA and return0. No registered call/xref was recovered;
   keep admission boundary unresolved rather than claiming diagnostic reachability. */

uint f33_begin_mode600_stimulus_fit(void)

{
  f33_mode600_stimulus_fit_work.active = 'Z';
  f33_initialize_mode600_stimulus_fit();
  return 0;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_34406(void)

{
  return;
}

/* Get64-byte0202 record and publish unpacked centers/gains/angles only when getter returns10, under
   existing PMR helper. Does not itself validate marker or numeric bounds; caller346F0 owns
   marker/status and346B2 owns bounds/defaulting. */

uint f33_restore_fit_coefficients(void)

{
  uint *puVar1;
  uint32_t puVar2;
  uint uVar3;
  undefined4 uVar4;
  char *pcVar5;
  uint local_44 [2];
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
  undefined2 uStack_14;
  undefined2 uStack_12;
  undefined2 uStack_10;
  undefined2 uStack_e;
  undefined2 uStack_c;
  undefined2 uStack_a;
  undefined2 uStack_8;
  
  puVar2 = 0xfebeb800u;
  puVar1 = local_44;
  pcVar5 = (undefined *)camry_host_ptr(0x21058u);
  do {
    uVar4 = *(undefined4 *)pcVar5;
    pcVar5 = pcVar5 + 4;
    *puVar1 = uVar4;
    puVar1 = puVar1 + 1;
  } while ((uintptr_t)(pcVar5)!=(uintptr_t)((undefined *)camry_host_ptr(0x21098u)));
  uVar3 = f33_nvm_get_record(0x202, camry_host_addr(local_44));
  if (uVar3 == 0x10) {
    uVar3 = f33_priority_mask_enter(0xffc0);
    (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb284u + (uint32_t)((int)puVar2)))))) = uStack_3c;
    (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb286u + (uint32_t)((int)puVar2)))))) = uStack_3a;
    (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb290u + (uint32_t)((int)puVar2)))))) = uStack_38;
    (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb292u + (uint32_t)((int)puVar2)))))) = uStack_36;
    (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb288u + (uint32_t)((int)puVar2)))))) = uStack_34;
    (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb28au + (uint32_t)((int)puVar2)))))) = uStack_32;
    (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb294u + (uint32_t)((int)puVar2)))))) = uStack_30;
    (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb296u + (uint32_t)((int)puVar2)))))) = uStack_2e;
    (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb28cu + (uint32_t)((int)puVar2)))))) = uStack_2c;
    (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb28eu + (uint32_t)((int)puVar2)))))) = uStack_2a;
    (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb298u + (uint32_t)((int)puVar2)))))) = uStack_28;
    (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb29au + (uint32_t)((int)puVar2)))))) = uStack_26;
    (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb29cu + (uint32_t)((int)puVar2)))))) = uStack_24;
    (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb29eu + (uint32_t)((int)puVar2)))))) = uStack_22;
    (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb2a8u + (uint32_t)((int)puVar2)))))) = uStack_20;
    (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb2aau + (uint32_t)((int)puVar2)))))) = uStack_1e;
    (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb2b4u + (uint32_t)((int)puVar2)))))) = uStack_1c;
    (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb2a0u + (uint32_t)((int)puVar2)))))) = uStack_1a;
    (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb2a2u + (uint32_t)((int)puVar2)))))) = uStack_18;
    (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb2acu + (uint32_t)((int)puVar2)))))) = uStack_16;
    (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb2aeu + (uint32_t)((int)puVar2)))))) = uStack_14;
    (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb2b6u + (uint32_t)((int)puVar2)))))) = uStack_12;
    (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb2a4u + (uint32_t)((int)puVar2)))))) = uStack_10;
    (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb2a6u + (uint32_t)((int)puVar2)))))) = uStack_e;
    (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb2b0u + (uint32_t)((int)puVar2)))))) = uStack_c;
    (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb2b2u + (uint32_t)((int)puVar2)))))) = uStack_a;
    (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb2b8u + (uint32_t)((int)puVar2)))))) = uStack_8;
    f33_priority_mask_restore(uVar3);
  }
  return uVar3;
}




/* Return5A for invalid retained6A84..6AB8,0 valid. Unlike permissive foreground candidate check,
   exact retained gains24097..32768, first centers31623..33913, signed second centers-286..286 and
   angles8118..8374. Does not mutate retained values. */

uint f33_check_retained_fit_bounds(void)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  
  iVar1 = (int)f33_retained_fit_coefficients.second_center[0];
  iVar9 = (int)f33_retained_fit_coefficients.second_center[1];
  iVar8 = (int)f33_retained_fit_coefficients.second_center[2];
  iVar7 = (int)f33_retained_fit_coefficients.second_center[3];
  iVar6 = (int)f33_retained_fit_coefficients.second_center[4];
  iVar5 = (int)f33_retained_fit_coefficients.second_center[5];
  if (((((((((DAT_00030ef6 < f33_retained_fit_coefficients.first_gain[0]) ||
            (f33_retained_fit_coefficients.first_gain[0] < DAT_00030ef8)) ||
           (DAT_00030ef6 < f33_retained_fit_coefficients.first_gain[1])) ||
          ((f33_retained_fit_coefficients.first_gain[1] < DAT_00030ef8 ||
           (DAT_00030efe < f33_retained_fit_coefficients.first_center[0])))) ||
         (f33_retained_fit_coefficients.first_center[0] < DAT_00030f00)) ||
        (((DAT_00030efe < f33_retained_fit_coefficients.first_center[1] ||
          (f33_retained_fit_coefficients.first_center[1] < DAT_00030f00)) ||
         ((DAT_00030ef6 < f33_retained_fit_coefficients.first_gain[2] ||
          (((f33_retained_fit_coefficients.first_gain[2] < DAT_00030ef8 ||
            (DAT_00030ef6 < f33_retained_fit_coefficients.first_gain[3])) ||
           (f33_retained_fit_coefficients.first_gain[3] < DAT_00030ef8)))))))) ||
       (((((DAT_00030efe < f33_retained_fit_coefficients.first_center[2] ||
           (f33_retained_fit_coefficients.first_center[2] < DAT_00030f00)) ||
          ((DAT_00030efe < f33_retained_fit_coefficients.first_center[3] ||
           (((f33_retained_fit_coefficients.first_center[3] < DAT_00030f00 ||
             (DAT_00030ef6 < f33_retained_fit_coefficients.first_gain[4])) ||
            ((f33_retained_fit_coefficients.first_gain[4] < DAT_00030ef8 ||
             (((DAT_00030ef6 < f33_retained_fit_coefficients.first_gain[5] ||
               (f33_retained_fit_coefficients.first_gain[5] < DAT_00030ef8)) ||
              (DAT_00030efe < f33_retained_fit_coefficients.first_center[4])))))))))) ||
         ((f33_retained_fit_coefficients.first_center[4] < DAT_00030f00 ||
          (DAT_00030efe < f33_retained_fit_coefficients.first_center[5])))) ||
        (f33_retained_fit_coefficients.first_center[5] < DAT_00030f00)))) ||
      (((((DAT_00030efa < f33_retained_fit_coefficients.second_gain[0] ||
          (f33_retained_fit_coefficients.second_gain[0] < DAT_00030efc)) ||
         ((DAT_00030efa < f33_retained_fit_coefficients.second_gain[1] ||
          ((((f33_retained_fit_coefficients.second_gain[1] < DAT_00030efc ||
             (iVar4 = (int)DAT_00030f02,
             iVar1 - iVar4 < 0 == (iVar1 < 0 != iVar4 < 0 && iVar4 < 0 == iVar1 - iVar4 < 0) &&
             iVar1 != iVar4)) ||
            (iVar3 = (int)DAT_00030f04,
            iVar1 - iVar3 < 0 != (iVar1 < 0 != iVar3 < 0 && iVar3 < 0 == iVar1 - iVar3 < 0))) ||
           ((iVar9 - iVar4 < 0 == (iVar9 < 0 != iVar4 < 0 && iVar4 < 0 == iVar9 - iVar4 < 0) &&
             iVar9 != iVar4 ||
            (iVar9 - iVar3 < 0 != (iVar9 < 0 != iVar3 < 0 && iVar3 < 0 == iVar9 - iVar3 < 0)))))))))
        || (DAT_00030f06 < f33_retained_fit_coefficients.component_angle[0])) ||
       (((f33_retained_fit_coefficients.component_angle[0] < DAT_00030f08 ||
         (DAT_00030efa < f33_retained_fit_coefficients.second_gain[2])) ||
        ((f33_retained_fit_coefficients.second_gain[2] < DAT_00030efc ||
         (((DAT_00030efa < f33_retained_fit_coefficients.second_gain[3] ||
           (f33_retained_fit_coefficients.second_gain[3] < DAT_00030efc)) ||
          (iVar8 - iVar4 < 0 == (iVar8 < 0 != iVar4 < 0 && iVar4 < 0 == iVar8 - iVar4 < 0) &&
           iVar8 != iVar4)))))))))) ||
     ((((iVar8 - iVar3 < 0 != (iVar8 < 0 != iVar3 < 0 && iVar3 < 0 == iVar8 - iVar3 < 0) ||
        (iVar7 - iVar4 < 0 == (iVar7 < 0 != iVar4 < 0 && iVar4 < 0 == iVar7 - iVar4 < 0) &&
         iVar7 != iVar4)) ||
       (iVar7 - iVar3 < 0 != (iVar7 < 0 != iVar3 < 0 && iVar3 < 0 == iVar7 - iVar3 < 0))) ||
      ((((DAT_00030f06 < f33_retained_fit_coefficients.component_angle[1] ||
         (f33_retained_fit_coefficients.component_angle[1] < DAT_00030f08)) ||
        ((((DAT_00030efa < f33_retained_fit_coefficients.second_gain[4] ||
           (((f33_retained_fit_coefficients.second_gain[4] < DAT_00030efc ||
             (DAT_00030efa < f33_retained_fit_coefficients.second_gain[5])) ||
            (f33_retained_fit_coefficients.second_gain[5] < DAT_00030efc)))) ||
          ((iVar6 - iVar4 < 0 == (iVar6 < 0 != iVar4 < 0 && iVar4 < 0 == iVar6 - iVar4 < 0) &&
            iVar6 != iVar4 ||
           (iVar6 - iVar3 < 0 != (iVar6 < 0 != iVar3 < 0 && iVar3 < 0 == iVar6 - iVar3 < 0))))) ||
         (iVar5 - iVar4 < 0 == (iVar5 < 0 != iVar4 < 0 && iVar4 < 0 == iVar5 - iVar4 < 0) &&
          iVar5 != iVar4)))) ||
       (((iVar5 - iVar3 < 0 != (iVar5 < 0 != iVar3 < 0 && iVar3 < 0 == iVar5 - iVar3 < 0) ||
         (DAT_00030f06 < f33_retained_fit_coefficients.component_angle[2])) ||
        (f33_retained_fit_coefficients.component_angle[2] < DAT_00030f08)))))))) {
    uVar2 = 0x5a;
  }
  else {
    uVar2 = 0;
  }
  return uVar2;
}



/* Under existing FFC0 priority mask, default retained first centers/gains and second gains8000,
   second centers0 and angles2000; does not imply accepted physical calibration. */

uint f33_reset_retained_fit_coefficients(void)

{
  uint32_t puVar1;
  uint saved_mask;
  
  puVar1 = 0xfebeb800u;
  saved_mask = f33_priority_mask_enter(0xffc0);
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb284u + (uint32_t)((int)puVar1)))))) = 0x8000;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb286u + (uint32_t)((int)puVar1)))))) = 0x8000;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb290u + (uint32_t)((int)puVar1)))))) = 0x8000;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb292u + (uint32_t)((int)puVar1)))))) = 0x8000;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb288u + (uint32_t)((int)puVar1)))))) = 0x8000;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb28au + (uint32_t)((int)puVar1)))))) = 0x8000;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb294u + (uint32_t)((int)puVar1)))))) = 0x8000;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb296u + (uint32_t)((int)puVar1)))))) = 0x8000;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb28cu + (uint32_t)((int)puVar1)))))) = 0x8000;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb28eu + (uint32_t)((int)puVar1)))))) = 0x8000;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb298u + (uint32_t)((int)puVar1)))))) = 0x8000;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb29au + (uint32_t)((int)puVar1)))))) = 0x8000;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb29cu + (uint32_t)((int)puVar1)))))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb29eu + (uint32_t)((int)puVar1)))))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb2a8u + (uint32_t)((int)puVar1)))))) = 0x8000;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb2aau + (uint32_t)((int)puVar1)))))) = 0x8000;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb2b4u + (uint32_t)((int)puVar1)))))) = 0x2000;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb2a0u + (uint32_t)((int)puVar1)))))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb2a2u + (uint32_t)((int)puVar1)))))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb2acu + (uint32_t)((int)puVar1)))))) = 0x8000;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb2aeu + (uint32_t)((int)puVar1)))))) = 0x8000;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb2b6u + (uint32_t)((int)puVar1)))))) = 0x2000;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb2a4u + (uint32_t)((int)puVar1)))))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb2a6u + (uint32_t)((int)puVar1)))))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb2b0u + (uint32_t)((int)puVar1)))))) = 0x8000;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb2b2u + (uint32_t)((int)puVar1)))))) = 0x8000;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb2b8u + (uint32_t)((int)puVar1)))))) = 0x2000;
  f33_priority_mask_restore(saved_mask);
  return saved_mask;
}



/* Return344F4 status;5A first defaults retained values via3465A. Existing346F0 marker/diagnostic
   owner remains separate from candidate publication. */

uint f33_validate_or_default_retained_fit(void)

{
  uint uVar1;
  
  uVar1 = f33_check_retained_fit_bounds();
  if (uVar1 == 0x5a) {
    f33_reset_retained_fit_coefficients();
  }
  return uVar1;
}



void FUN_000346cc(void)

{
  DAT_febe6a7f = 0x44;
  DAT_febe6ac4 = 0xa55a5aa5;
  DAT_febe6a7e = 0;
  f33_report_diagnostic_healthy_observed(0x127);
  return;
}



void FUN_000346f0(void)

{
  undefined2 uVar1;
  uint32_t puVar2;
  uint uVar3;
  int iVar4;
  undefined4 uVar5;
  undefined1 uVar6;
  undefined4 uVar7;
  undefined1 uVar8;
  uint local_54 [16];
  
  puVar2 = 0xfebeb800u;
  uVar3 = f33_nvm_get_record(0x202, camry_host_addr(local_54));
  uVar5 = 0xa55a5aa5;
  if ((uVar3 == 0x10) && (local_54[0] == 0xa55a5aa5)) {
    f33_restore_fit_coefficients();
    uVar3 = f33_validate_or_default_retained_fit();
    if (uVar3 == 0) {
      uVar7 = 0xa55a5aa5;
      uVar8 = 0x44;
      f33_report_diagnostic_healthy_observed(0x125);
      goto LAB_00034744;
    }
  }
  uVar7 = 0x5aa5a55a;
  uVar8 = 0x22;
  f33_report_diagnostic_event_failure(0x125,0x32);
LAB_00034744:
  uVar3 = f33_nvm_get_record_status(0x205);
  iVar4 = camry_host_addr(FUN_000567be());
  if ((uVar3 == 0x10) && ((*((int *)camry_host_ptr((uint32_t)(iVar4 + 0xb8)))) == -0x5aa5a55b)) {
    uVar6 = 0x44;
    f33_report_diagnostic_healthy_observed(0x126);
  }
  else {
    uVar5 = 0x5aa5a55a;
    uVar6 = 0x22;
    f33_report_diagnostic_event_failure(0x126,0x32);
  }
  FUN_000346cc();
  uVar1 = DAT_00030ef2;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb279u + (uint32_t)((int)puVar2) * 1u)))) = uVar8;
  (*((undefined4 *)camry_host_ptr((uint32_t)((0xffffb2bcu + (uint32_t)((int)puVar2)))))) = uVar7;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb27cu + (uint32_t)((int)puVar2) * 1u)))) = uVar6;
  (*((undefined4 *)camry_host_ptr((uint32_t)((0xffffb2c0u + (uint32_t)((int)puVar2)))))) = uVar5;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb282u + (uint32_t)((int)puVar2)))))) = uVar1;
  return;
}



undefined4 FUN_000347a2(void)

{
  uint uVar1;
  uint local_44 [16];
  
  uVar1 = f33_nvm_get_record(0x202, camry_host_addr(local_44));
  if ((uVar1 == 0x10) && (local_44[0] == 0xa55a5aa5)) {
    f33_restore_fit_coefficients();
    uVar1 = f33_validate_or_default_retained_fit();
    if (uVar1 == 0) {
      return 0xa55a5aa5;
    }
  }
  return 0x5aa5a55a;
}



void FUN_000347e2(void)

{
  char cVar1;
  undefined4 uVar2;
  undefined *puVar3;
  int iVar4;
  undefined1 uVar5;
  short sVar6;
  
  uVar2 = DAT_febe6ac0;
  cVar1 = DAT_febe6a7c;
  puVar3 = ((undefined *)camry_host_ptr(0xfebeb800u));
  sVar6 = DAT_febe6a82;
  if (DAT_febe6a82 != 0) {
    sVar6 = DAT_febe6a82 + -1;
  }
  iVar4 = DAT_febe6abc;
  if (((DAT_febe6579 == 'Z') && (DAT_febe6abc == -0x5aa5a55b)) &&
     (puVar3 = ((undefined *)camry_host_ptr(0xfebeb800u)), iVar4 = FUN_000347a2(), iVar4 != -0x5aa5a55b)) {
    f33_report_diagnostic_event_failure(0x125,0x32);
  }
  uVar5 = 0;
  if (cVar1 == 'D') {
    uVar5 = 0x5a;
  }
  if (DAT_00030ef0 == 'Z') {
    uVar5 = 0;
  }
  FUN_000346cc();
  *(int *)(((undefined *)camry_host_ptr(0xffffb2bcu)) + (int)camry_host_addr(puVar3)) = iVar4;
  *(undefined4 *)(((undefined *)camry_host_ptr(0xffffb2c0u)) + (int)camry_host_addr(puVar3)) = uVar2;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb27bu + (uint32_t)((int)camry_host_addr(puVar3)) * 1u)))) = uVar5;
  *(short *)(((undefined *)camry_host_ptr(0xffffb282u)) + (int)camry_host_addr(puVar3)) = sVar6;
  return;
}



void FUN_00034858(void)

{
  uint32_t puVar1;
  uint uVar2;
  int iVar3;
  undefined4 uVar4;
  undefined1 uVar5;
  
  puVar1 = 0xfebeb800u;
  uVar2 = f33_nvm_get_record_status(0x206);
  iVar3 = camry_host_addr(FUN_000567be());
  if ((uVar2 == 0x10) && ((*((int *)camry_host_ptr((uint32_t)(iVar3 + 0x4c8)))) == -0x5aa5a55b)) {
    uVar5 = 0x44;
    f33_report_diagnostic_healthy_observed(0x127);
    uVar4 = 0xa55a5aa5;
  }
  else {
    uVar4 = 0x5aa5a55a;
    uVar5 = 0x22;
    f33_report_diagnostic_event_failure(0x127,0x32);
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb27fu + (uint32_t)((int)puVar1) * 1u)))) = uVar5;
  (*((undefined4 *)camry_host_ptr((uint32_t)((0xffffb2c4u + (uint32_t)((int)puVar1)))))) = uVar4;
  return;
}



/* Copy foreground centers/gains/angles into retained6A84..6AB8, serialize64-byte0202 record
   markerA55A5AA5 plus reserved zero, enqueue setter; publish6A7A=44 and6ABC marker immediately. Do
   not interpret immediate software marker as durable write success. */

void f33_publish_fit_candidate_record(void)

{
  uint32_t puVar1;
  uint auStack_6c [2];
  ushort uStack_64;
  ushort uStack_62;
  ushort uStack_60;
  ushort uStack_5e;
  ushort uStack_5c;
  ushort uStack_5a;
  ushort uStack_58;
  ushort uStack_56;
  ushort uStack_54;
  ushort uStack_52;
  ushort uStack_50;
  ushort uStack_4e;
  short sStack_4c;
  short sStack_4a;
  ushort uStack_48;
  ushort uStack_46;
  ushort uStack_44;
  short sStack_42;
  short sStack_40;
  ushort uStack_3e;
  ushort uStack_3c;
  ushort uStack_3a;
  short sStack_38;
  short sStack_36;
  ushort uStack_34;
  ushort uStack_32;
  ushort uStack_30;
  undefined2 uStack_2e;
  
  puVar1 = 0xfebeb800u;
  f33_retained_fit_coefficients.first_center[0] = DAT_febe654e;
  f33_retained_fit_coefficients.first_center[1] = DAT_febe6550;
  f33_retained_fit_coefficients.first_gain[0] = DAT_febe6542;
  f33_retained_fit_coefficients.first_gain[1] = DAT_febe6544;
  f33_retained_fit_coefficients.first_center[2] = DAT_febe6552;
  f33_retained_fit_coefficients.first_center[3] = DAT_febe6554;
  f33_retained_fit_coefficients.first_gain[2] = DAT_febe6546;
  f33_retained_fit_coefficients.first_gain[3] = DAT_febe6548;
  f33_retained_fit_coefficients.first_center[4] = DAT_febe6556;
  f33_retained_fit_coefficients.first_center[5] = DAT_febe6558;
  f33_retained_fit_coefficients.first_gain[4] = DAT_febe654a;
  f33_retained_fit_coefficients.first_gain[5] = DAT_febe654c;
  f33_retained_fit_coefficients.second_center[0] = ((int)(int16_t)DAT_febe6566);
  f33_retained_fit_coefficients.second_center[1] = ((int)(int16_t)DAT_febe6568);
  f33_retained_fit_coefficients.second_gain[0] = DAT_febe655a;
  f33_retained_fit_coefficients.second_gain[1] = DAT_febe655c;
  f33_retained_fit_coefficients.component_angle[0] = DAT_febe6572;
  f33_retained_fit_coefficients.second_center[2] = ((int)(int16_t)DAT_febe656a);
  f33_retained_fit_coefficients.second_center[3] = ((int)(int16_t)DAT_febe656c);
  f33_retained_fit_coefficients.second_gain[2] = DAT_febe655e;
  f33_retained_fit_coefficients.second_gain[3] = DAT_febe6560;
  f33_retained_fit_coefficients.component_angle[1] = DAT_febe6574;
  f33_retained_fit_coefficients.second_center[4] = ((int)(int16_t)DAT_febe656e);
  f33_retained_fit_coefficients.second_center[5] = ((int)(int16_t)DAT_febe6570);
  f33_retained_fit_coefficients.second_gain[4] = DAT_febe6562;
  f33_retained_fit_coefficients.second_gain[5] = DAT_febe6564;
  f33_retained_fit_coefficients.component_angle[2] = DAT_febe6576;
  auStack_6c[1] = 0;
  auStack_6c[0] = 0xa55a5aa5;
  uStack_62 = DAT_febe6550;
  uStack_64 = DAT_febe654e;
  uStack_52 = DAT_febe6558;
  sStack_4a = ((int)(int16_t)DAT_febe6568);
  uStack_48 = DAT_febe655a;
  uStack_60 = DAT_febe6542;
  uStack_5e = DAT_febe6544;
  uStack_5c = DAT_febe6552;
  uStack_5a = DAT_febe6554;
  uStack_58 = DAT_febe6546;
  uStack_56 = DAT_febe6548;
  uStack_54 = DAT_febe6556;
  uStack_50 = DAT_febe654a;
  uStack_4e = DAT_febe654c;
  sStack_4c = ((int)(int16_t)DAT_febe6566);
  uStack_46 = DAT_febe655c;
  uStack_44 = DAT_febe6572;
  sStack_42 = ((int)(int16_t)DAT_febe656a);
  sStack_40 = ((int)(int16_t)DAT_febe656c);
  uStack_3e = DAT_febe655e;
  uStack_3c = DAT_febe6560;
  uStack_3a = DAT_febe6574;
  sStack_38 = ((int)(int16_t)DAT_febe656e);
  sStack_36 = ((int)(int16_t)DAT_febe6570);
  uStack_34 = DAT_febe6562;
  uStack_32 = DAT_febe6564;
  uStack_30 = DAT_febe6576;
  uStack_2e = 0;
  f33_nvm_set_record(0x202,auStack_6c);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb27au + (uint32_t)((int)puVar1) * 1u)))) = 0x44;
  (*((undefined4 *)camry_host_ptr((uint32_t)((0xffffb2bcu + (uint32_t)((int)puVar1)))))) = 0xa55a5aa5;
  return;
}



void FUN_00034bce(void)

{
  uint32_t puVar1;
  uint local_44 [16];
  
  puVar1 = 0xfebeb800u;
  f33_nvm_get_record(0x202, camry_host_addr(local_44));
  local_44[0] = 0;
  f33_nvm_set_record(0x202,local_44);
  (*((undefined4 *)camry_host_ptr((uint32_t)((0xffffb2bcu + (uint32_t)((int)puVar1)))))) = 0x5aa5a55a;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb278u + (uint32_t)((int)puVar1) * 1u)))) = 0x44;
  return;
}



bool FUN_00034c00(void)

{
  ushort uVar1;
  int iVar2;
  char cVar3;
  bool bVar4;
  uint uVar5;
  
  cVar3 = DAT_febee81a;
  iVar2 = DAT_febe6abc;
  uVar1 = DAT_febe66b8;
  uVar5 = f33_get_diagnostic_event_state(0x52);
  if (((cVar3 == '\x01') && (DAT_00030ef4 <= uVar1)) && (iVar2 == 0)) {
    bVar4 = (uVar5 >> 1 & 1) == 0;
  }
  else {
    bVar4 = false;
  }
  return bVar4;
}



/* Preserve344F4 full R10 result across PREPARE/DISPOSE.33CDC consumes0 for admissible changed
   record and5A for invalid. Replace existing void prototype; no unrelated register clobber/inline
   fiction. */

uint f33_check_fit_record_admission(void)

{
  uint uVar1;
  
  uVar1 = f33_check_retained_fit_bounds();
  return uVar1;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_34c46(void)

{
  return;
}



void FUN_00034c48(void)

{
  DAT_febe6acc = 0;
  DAT_febe6ac8 = 0;
  DAT_febe6ac9 = 0;
  DAT_febe6aca = 0;
  return;
}



/* Prioritize cached6210/6212 from34028 over6959/695C request, else signed torque map. Publish
   source ID and negated selected request. No inferred physical current actuation, freshness or
   actual output consumer. */

void f33_select_mode600_stimulus_request(void)

{
  uint32_t puVar1;
  undefined1 uVar2;
  undefined1 uVar3;
  short sStack_e;
  
  puVar1 = 0xfebeb800u;
  if (DAT_febe6210 == 'Z') {
    uVar3 = 1;
    sStack_e = ((int)(int16_t)DAT_febe6212);
    uVar2 = 0x5a;
  }
  else if (DAT_febe6959 == 'Z') {
    uVar3 = 2;
    sStack_e = ((int)(int16_t)DAT_febe695c);
    uVar2 = 0x5a;
  }
  else {
    uVar3 = 0;
    uVar2 = 0;
    puVar1 = 0xfebeb800u;
    if (((int)(int16_t)DAT_febe7e0c) < 0) {
      FUN_00070208(((undefined *)camry_host_ptr(0x30f0cu)),(int)-((int)(int16_t)DAT_febe7e0c),&sStack_e);
      sStack_e = -sStack_e;
    }
    else {
      FUN_00070208(((undefined *)camry_host_ptr(0x30f0cu)),(int)((int)(int16_t)DAT_febe7e0c),&sStack_e);
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb2c9u + (uint32_t)((int)puVar1) * 1u)))) = uVar3;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb2c8u + (uint32_t)((int)puVar1) * 1u)))) = uVar2;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb2ccu + (uint32_t)((int)puVar1)))))) = -sStack_e;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_34cce(void)

{
  return;
}



/* Get record105 marker and record18 count. Exact10/A55A5AA5 establishes5A; invalid status or
   count>30 clears gate and count. Valid count0 preserves marker-derived gate. RAM publication, not
   a physical flash read. */

uint f33_reload_ba_admission_records(void)

{
  uint32_t puVar1;
  uint uVar2;
  undefined1 uVar3;
  byte local_18 [8];
  uint auStack_10 [2];
  
  puVar1 = 0xfebeb800u;
  uVar2 = f33_nvm_get_record(0x105, camry_host_addr(auStack_10));
  if ((uVar2 == 0x10) && (auStack_10[0] == 0xa55a5aa5)) {
    uVar3 = 0x5a;
  }
  else {
    uVar3 = 0;
  }
  uVar2 = f33_nvm_get_record(0x18, camry_host_addr(((uint *)camry_host_ptr((uint32_t)(local_18)))));
  if ((uVar2 != 0x10) || (f33_ba_retained_admission_count_limit < local_18[0])) {
    local_18[0] = 0;
    uVar3 = 0;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x58b0))))) = local_18[0];
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x58b1))))) = uVar3;
  return uVar2;
}



/* Only phase5F4C==5A reinvokes retained start with null payload and stack response. Pending-1
   retains phase; terminal reports to4D4CA and clears phase. Recovered direct writers
   initialize/clear phase only; no phase-arming producer is established. */

void f33_poll_ba_retained_start(void)

{
  uint32_t puVar1;
  uint uVar2;
  int iVar3;
  uchar uVar4;
  uchar auStack_4f [63];
  
  puVar1 = 0xfebeb800u;
  uVar4 = '\0';
  uVar2 = (uint)f33_ba_application_work.selected_index;
  if (f33_ba_application_work.retained_start_phase == 'Z') {
    iVar3 = (*(int (*)())f33_ba_operations[uVar2].start)(f33_ba_application_work.selected_index,(uchar *)0x0,auStack_4f);
    if (iVar3 != -1) {
      if (-1 < iVar3) {
        uVar4 = f33_ba_operations[uVar2].response_body_length;
      }
      ((void)(auStack_4f), FUN_0004d4ca(iVar3, uVar4));
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x58b4))))) = 0;
    }
  }
  return;
}



/* Compare zero-extended low8 length bytes exactly; return1 on equality,0 on first mismatch. No
   independent source-size validation. */

uint f33_compare_ba_token_bytes(uchar *left,uchar *right,uchar length)

{
  uint uVar1;
  
  uVar1 = 0;
  while( true ) {
    if (length <= uVar1) {
      return 1;
    }
    if ((uintptr_t)(left[uVar1])!=(uintptr_t)(right[uVar1])) break;
    uVar1 = uVar1 + 1 & 0xff;
  }
  return 0;
}



/* Return5A only for F7,length6 and five exact BAENA bytes. Token comparison runs before
   selector/length conjunction; this is not a general input-bounds guard. */

uint f33_ba_enable_closed_gate_exception(uchar operation,uchar request_length,uchar *payload)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = 0;
  uVar1 = f33_compare_ba_token_bytes
                    (payload,(uchar *)"BAENAJTEKMTMPCLJTRM1JTRM2BADISBAENATZCLRJTRM3VSPDASINC",
                     '\x05');
  if (((operation == 0xf7) && (request_length == '\x06')) && (uVar1 == 1)) {
    uVar2 = 0x5a;
  }
  return uVar2;
}



/* Require admission5A or exact F7/BAENA exception, then scan ten fixed16-byte rows. Require length6
   and call fixed start; retain index even for negative result. Closed gate returns-13,
   unknown/null-3, wrong length-6. All configured result lengths are0. */

int f33_dispatch_ba_configured_start
              (uchar request_length,uchar *request,uchar *response,uchar *selected_index)

{
  uchar operation;
  bool bVar1;
  uchar phase;
  undefined8 uVar2;
  uint uVar3;
  int iVar4;
  
  uVar2 = 0xfebeb800;
  operation = *request;
  bVar1 = false;
  iVar4 = 0;
  uVar3 = f33_ba_enable_closed_gate_exception(operation,request_length,request + 1);
  if (((*((char *)camry_host_ptr((uint32_t)((int)uVar2 + -0x58b1)))) == 'Z') || (uVar3 == 0x5a)) {
    for (uVar3 = 0; uVar3 < f33_ba_operation_count; uVar3 = uVar3 + 1 & 0xff) {
      if (f33_ba_operations[uVar3].operation == operation) {
        bVar1 = true;
        if (f33_ba_operations[uVar3].request_length == request_length) {
          iVar4 = -3;
          if (f33_ba_operations[uVar3].start != 0x0u) {
            phase = (uchar)uVar3;
            iVar4 = (*(int (*)())f33_ba_operations[uVar3].start)(phase,request + 1,response);
            (*((uchar *)camry_host_ptr((uint32_t)((int)uVar2 + -0x58b3)))) = phase;
            *selected_index = phase;
          }
        }
        else {
          iVar4 = -6;
        }
      }
    }
    if (!bVar1) {
      iVar4 = -3;
    }
  }
  else {
    iVar4 = -0xd;
  }
  return iVar4;
}



/* Call fixed finish indexed by low8 without a local bounds check. Nonnegative result writes
   full32-bit configured length0 and latches5F53=5A. Negative result preserves length and latch.
   Preserve real signedR10 from finish callbacks. */

int f33_dispatch_ba_configured_finish(uchar configured_index,uint *response_length)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  if (f33_ba_operations[configured_index].finish == 0x0u) {
    iVar2 = -3;
  }
  else {
    iVar2 = (*(int (*)())camry_indirect((uint32_t)(f33_ba_operations[configured_index].finish)))();
    if (-1 < iVar2) {
      *response_length = (uint)f33_ba_operations[configured_index].response_body_length;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x58ad))))) = 0x5a;
    }
  }
  return iVar2;
}



void FUN_00034ea4(int param_1,int param_2)

{
  uint uVar1;
  undefined4 uVar2;
  byte bStack_15;
  undefined1 auStack_14 [8];
  
  uVar1 = 0;
  do {
    auStack_14[uVar1] = 0;
    uVar1 = uVar1 + 1;
  } while (uVar1 < 8);
  FUN_0006a624(param_2,&bStack_15);
  if ((param_2 < 0) || (8 < bStack_15)) {
    uVar2 = 0xfffffffa;
  }
  else {
    uVar2 = 0;
    for (uVar1 = 0; uVar1 < bStack_15; uVar1 = uVar1 + 1 & 0xff) {
      auStack_14[uVar1] = (*((undefined1 *)camry_host_ptr((uint32_t)(uVar1 + param_1))));
    }
  }
  ((void)(auStack_14), FUN_0004d4ca(uVar2, bStack_15));
  return;
}



int FUN_00034f00(uint param_1,int param_2)

{
  uchar uVar1;
  uint uVar2;
  int iVar3;
  uint uVar4;
  uint uVar5;
  uint local_2c;
  uint uStack_28;
  uint auStack_24 [2];
  
  param_1 = param_1 & 0xff;
  iVar3 = 0;
  uVar1 = f33_ba_operations[param_1].numeric_format;
  if (f33_ba_operations[param_1].numeric_source != 0x0u) {
    (*(int (*)())f33_ba_operations[param_1].numeric_source)(&local_2c,&uStack_28);
    if (uStack_28 != 0) {
      uVar4 = 2;
      auStack_24[0] = local_2c;
      goto LAB_00034f56;
    }
    if (local_2c != 0) {
      auStack_24[0] = local_2c;
      uVar4 = 1;
      uStack_28 = 0;
      goto LAB_00034f56;
    }
  }
  uVar4 = 0;
  uStack_28 = 0;
  auStack_24[0] = 0;
LAB_00034f56:
  auStack_24[1] = uStack_28;
  uVar5 = 0;
  do {
    if (uVar4 <= uVar5) {
      return iVar3;
    }
    if (iVar3 == 0) {
      if (uVar1 == '\x01') {
LAB_00034fa6:
        (*((char *)camry_host_ptr((uint32_t)(uVar5 + param_2)))) = (char)auStack_24[uVar5];
      }
      else if (uVar1 == '\x02') {
        FUN_0006a574((short)auStack_24[uVar5], ((undefined1 *)camry_host_ptr((uint32_t)(uVar5 * 2 + param_2))));
      }
      else if (uVar1 == '\x04') {
        FUN_0006a55c(auStack_24[uVar5], ((undefined1 *)camry_host_ptr((uint32_t)(uVar5 * 4 + param_2))));
      }
      else {
        if (uVar1 == '\t') goto LAB_00034fa6;
        if (uVar1 == '\n') {
          FUN_0006a5ac((int)(short)auStack_24[uVar5], ((undefined1 *)camry_host_ptr((uint32_t)(uVar5 * 2 + param_2))));
        }
        else if (uVar1 == '\f') {
          FUN_0006a594(auStack_24[uVar5], ((undefined1 *)camry_host_ptr((uint32_t)(uVar5 * 4 + param_2))));
        }
        else {
          iVar3 = -6;
        }
      }
    }
    else {
      for (uVar2 = 0; uVar2 < f33_ba_operations[param_1].response_body_length;
          uVar2 = uVar2 + 1 & 0xff) {
        (*((undefined1 *)camry_host_ptr((uint32_t)(uVar2 + param_2)))) = 0;
      }
    }
    uVar5 = uVar5 + 1 & 0xff;
  } while( true );
}



int FUN_00035004(byte *param_1)

{
  return (uint)param_1[1] + (uint)*param_1 * 0x100;
}



int FUN_00035010(byte *param_1)

{
  return (uint)param_1[3] +
         (uint)param_1[2] * 0x100 + (uint)param_1[1] * 0x10000 + (uint)*param_1 * 0x1000000;
}



undefined4 FUN_00035028(uint param_1,undefined1 *param_2,undefined1 *param_3)

{
  uchar uVar1;
  undefined2 *extraout_r8;
  undefined2 *extraout_r8_00;
  undefined4 *extraout_r8_01;
  undefined2 uVar2;
  undefined4 uVar3;
  
  uVar1 = f33_ba_operations[param_1 & 0xff].numeric_format;
  if (uVar1 == '\x01') {
    *param_3 = *param_2;
  }
  else if (uVar1 == '\x02') {
    uVar2 = FUN_00035004(param_2);
    *extraout_r8 = uVar2;
  }
  else {
    if (uVar1 != '\x04') {
      if (uVar1 == '\t') {
        *param_3 = *param_2;
        return 0;
      }
      if (uVar1 == '\n') {
        uVar2 = FUN_00035004(param_2);
        *extraout_r8_00 = uVar2;
        return 0;
      }
      if (uVar1 != '\f') {
        return 0xfffffffa;
      }
    }
    uVar3 = FUN_00035010(param_2);
    *extraout_r8_01 = uVar3;
  }
  return 0;
}



/* Exact JTEKM requests internal selector3 admission in modes0400/0500/0700..0702/0800; no latch
   mutation at start. */

int f33_ba_f1_validate_jtekm(uchar configured_index,uchar *payload,uchar *response)

{
  int iVar1;
  uint uVar2;
  
  uVar2 = f33_compare_ba_token_bytes
                    (payload,"JTEKMTMPCLJTRM1JTRM2BADISBAENATZCLRJTRM3VSPDASINC",'\x05');
  iVar1 = -6;
  if (uVar2 == 1) {
    iVar1 = f33_admit_internal_ba_selector(3,0);
  }
  return iVar1;
}



/* Return real B338C(3) R10=0; setB112=5A,B113=11. Persistent software selector, not a physical
   completion. */

int f33_ba_f1_latch_selector3(void)

{
  int iVar1;
  
  iVar1 = f33_latch_internal_ba_selector(3);
  return iVar1;
}



/* Phase0 requires TMPCL; phase5A returns-1 while either thermal tracker1,0 only when
   bothFF,otherwise-6. This start does not reset thermal state. */

int f33_ba_f3_validate_tmpcl(uchar configured_index,uchar *payload,uchar *response)

{
  uint uVar1;
  
  if (f33_ba_application_work.retained_start_phase == '\0') {
    uVar1 = f33_compare_ba_token_bytes
                      (payload,"TMPCLJTRM1JTRM2BADISBAENATZCLRJTRM3VSPDASINC",'\x05');
    if (uVar1 == 1) {
      return 0;
    }
  }
  else if (f33_ba_application_work.retained_start_phase == 'Z') {
    if ((DAT_febe6ee4 == '\x01') || (DAT_febe7de4 == '\x01')) {
      return -1;
    }
    if ((((int8_t)DAT_febe6ee4) == -1) && (((int8_t)DAT_febe7de4) == -1)) {
      return 0;
    }
  }
  return -6;
}



/* Configured F3 finish callback. Phase0 resets squared-drive/model state, requests records6/5 and
   arms5F51=5A while returning-1. Wait for both trackers to leave1; bothFF return0,other terminal
   combination-6; clear phase on terminal. Tracker arming ignores store admission; no durable-clear
   proof. Existing thermal/record ownership retained; static reconstruction, no separate native
   execution claim. */

int f33_service_clear_thermal_history(void)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  if (f33_ba_application_work.thermal_clear_phase == '\0') {
    FUN_0003ba78();
    f33_reset_thermal_models_and_history_record();
    f33_publish_thermal_reference_record();
    iVar2 = -1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x58af))))) = 0x5a;
  }
  else if (f33_ba_application_work.thermal_clear_phase == 'Z') {
    if ((DAT_febe6ee4 == '\x01') || (DAT_febe7de4 == '\x01')) {
      iVar2 = -1;
    }
    else {
      if ((((int8_t)DAT_febe6ee4) == -1) && (((int8_t)DAT_febe7de4) == -1)) {
        iVar2 = 0;
      }
      else {
        iVar2 = -6;
      }
      f33_ba_application_work.thermal_clear_phase = '\0';
    }
  }
  else {
    iVar2 = -6;
  }
  return iVar2;
}



/* Exact JTRM1 requests internal selector5 admission in allowed modes; start does not setB112. */

int f33_ba_f4_validate_jtrm1(uchar configured_index,uchar *payload,uchar *response)

{
  int iVar1;
  uint uVar2;
  
  uVar2 = f33_compare_ba_token_bytes(payload,"JTRM1JTRM2BADISBAENATZCLRJTRM3VSPDASINC",'\x05');
  iVar1 = -6;
  if (uVar2 == 1) {
    iVar1 = f33_admit_internal_ba_selector(5,0);
  }
  return iVar1;
}



/* Return real B338C(5) R10=0; setB112=5A,B113=22. */

int f33_ba_f4_latch_selector5(void)

{
  int iVar1;
  
  iVar1 = f33_latch_internal_ba_selector(5);
  return iVar1;
}



/* Exact JTRM2 requests internal selector6 admission in allowed modes; start does not setB112. */

int f33_ba_f5_validate_jtrm2(uchar configured_index,uchar *payload,uchar *response)

{
  int iVar1;
  uint uVar2;
  
  uVar2 = f33_compare_ba_token_bytes(payload,"JTRM2BADISBAENATZCLRJTRM3VSPDASINC",'\x05');
  iVar1 = -6;
  if (uVar2 == 1) {
    iVar1 = f33_admit_internal_ba_selector(6,0);
  }
  return iVar1;
}



/* Return real B338C(6) R10=0; setB112=5A,B113=44. */

int f33_ba_f5_latch_selector6(void)

{
  int iVar1;
  
  iVar1 = f33_latch_internal_ba_selector(6);
  return iVar1;
}



/* Phase0 exact BADIS requests zero record18 and105, ignoring admissions. Phase5A polls both cached
   statuses: exact10 clears live gate/count,20/21 waits-1,otherwise-9. */

int f33_ba_f6_request_disable(uchar configured_index,uchar *payload,uchar *response)

{
  uint32_t puVar1;
  uint uVar2;
  uint uVar3;
  undefined1 local_18;
  undefined1 uStack_17;
  undefined2 uStack_16;
  undefined4 uStack_14;
  uint auStack_10 [2];
  
  puVar1 = 0xfebeb800u;
  if (f33_ba_application_work.retained_start_phase == '\0') {
    uVar2 = f33_compare_ba_token_bytes(payload,"BADISBAENATZCLRJTRM3VSPDASINC",'\x05');
    if (uVar2 == 1) {
      uStack_14 = 0;
      uStack_16 = 0;
      uStack_17 = 0;
      local_18 = 0;
      f33_nvm_set_record(0x18,(uint *)&local_18);
      auStack_10[1] = 0;
      auStack_10[0] = 0;
      f33_nvm_set_record(0x105,auStack_10);
      return 0;
    }
    return -6;
  }
  if (f33_ba_application_work.retained_start_phase == 'Z') {
    uVar2 = f33_nvm_get_record_status(0x105);
    uVar3 = f33_nvm_get_record_status(0x18);
    if ((uVar2 == 0x10) && (uVar3 == 0x10)) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x58b0))))) = 0;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x58b1))))) = 0;
      return 0;
    }
    if ((uVar2 == 0x20 || uVar2 == 0x21) || (uVar3 == 0x20 || uVar3 == 0x21)) {
      return -1;
    }
  }
  return -9;
}



/* Both cached statuses10 clear5F4F/50 and return0; either20/21 waits-1;otherwise-9. Does not prove
   either setter was admitted. */

int f33_ba_f6_finish_disable(void)

{
  uint32_t puVar1;
  uint uVar2;
  uint uVar3;
  int iVar4;
  
  puVar1 = 0xfebeb800u;
  uVar2 = f33_nvm_get_record_status(0x105);
  uVar3 = f33_nvm_get_record_status(0x18);
  if ((uVar2 == 0x10) && (uVar3 == 0x10)) {
    iVar4 = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x58b0))))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x58b1))))) = 0;
  }
  else if ((uVar2 == 0x20 || uVar2 == 0x21) || (uVar3 == 0x20 || uVar3 == 0x21)) {
    iVar4 = -1;
  }
  else {
    iVar4 = -9;
  }
  return iVar4;
}



/* Read numerical published DCM security level and return5A if its bit1 is set, else0. This is not a
   greater-than-or-equal security-level comparison. */

uint f33_ba_security_level_bit1_enabled(void)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = FUN_0008d9b6();
  uVar1 = 0x5a;
  if ((uVar2 & 2) == 0) {
    uVar1 = 0;
  }
  return uVar1;
}



/* Require numerical security-level bit1 at every invocation. Phase0 exact BAENA requests
   record18=count30 and105=markerA55A5AA5, ignoring admission returns. Phase5A joins cached statuses
   and publishes gate/count on exact10. */

int f33_ba_f7_request_enable(uchar configured_index,uchar *payload,uchar *response)

{
  uint32_t puVar1;
  uint32_t puVar2;
  uint uVar3;
  uint uVar4;
  int iVar5;
  uchar local_1c [8];
  uint auStack_14 [2];
  
  puVar1 = 0xfebeb800u;
  puVar2 = 0x23dfcu;
  uVar3 = f33_ba_security_level_bit1_enabled();
  if (uVar3 == 0x5a) {
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x58b4))))) == '\0') {
      uVar3 = f33_compare_ba_token_bytes(payload, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x2d46))), '\x05');
      if (uVar3 == 1) {
        iVar5 = 0;
        local_1c[1] = 0;
        local_1c[2] = '\0';
        local_1c[3] = '\0';
        local_1c[4] = '\0';
        local_1c[5] = '\0';
        local_1c[6] = '\0';
        local_1c[7] = '\0';
        local_1c[0] = f33_ba_retained_admission_count_limit;
        f33_nvm_set_record(0x18,((uint *)camry_host_ptr((uint32_t)(local_1c))));
        auStack_14[0] = 0xa55a5aa5;
        auStack_14[1] = 0;
        f33_nvm_set_record(0x105,auStack_14);
      }
      else {
        iVar5 = -6;
      }
    }
    else {
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x58b4))))) == 'Z') {
        uVar3 = f33_nvm_get_record_status(0x105);
        uVar4 = f33_nvm_get_record_status(0x18);
        if ((uVar3 == 0x10) && (uVar4 == 0x10)) {
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x58b0))))) = f33_ba_retained_admission_count_limit;
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x58b1))))) = 0x5a;
          return 0;
        }
        if ((uVar3 == 0x20 || uVar3 == 0x21) || (uVar4 == 0x20 || uVar4 == 0x21)) {
          return -1;
        }
      }
      iVar5 = -9;
    }
  }
  else {
    iVar5 = -0xe;
  }
  return iVar5;
}



/* Both cached statuses10 publish count30/gate5A and return0; either20/21 waits-1,otherwise-9. No
   token/security recheck or marker re-read; old success can satisfy rejected requests. */

int f33_ba_f7_finish_enable(void)

{
  uint32_t puVar1;
  uint uVar2;
  uint uVar3;
  int iVar4;
  
  puVar1 = 0xfebeb800u;
  uVar2 = f33_nvm_get_record_status(0x105);
  uVar3 = f33_nvm_get_record_status(0x18);
  if ((uVar2 == 0x10) && (uVar3 == 0x10)) {
    iVar4 = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x58b0))))) = f33_ba_retained_admission_count_limit;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x58b1))))) = 0x5a;
  }
  else if ((uVar2 == 0x20 || uVar2 == 0x21) || (uVar3 == 0x20 || uVar3 == 0x21)) {
    iVar4 = -1;
  }
  else {
    iVar4 = -9;
  }
  return iVar4;
}



/* Require TZCLR,byteE81F==0,unsigned halfwordE892<=384,bytesE884/E88A!=5A. Return0 or-6; no reset
   mutation at start. */

int f33_ba_f8_validate_tzclr(uchar configured_index,uchar *payload,uchar *response)

{
  char cVar1;
  char cVar2;
  char cVar3;
  ushort uVar4;
  uint uVar5;
  
  uVar4 = DAT_febee892;
  cVar3 = DAT_febee88a;
  cVar2 = DAT_febee884;
  cVar1 = DAT_febee81f;
  uVar5 = f33_compare_ba_token_bytes(payload,"TZCLRJTRM3VSPDASINC",'\x05');
  if ((((uVar5 != 1) || (cVar1 != '\0')) || (f33_ba_tzclr_raw_input_limit < uVar4)) ||
     ((cVar2 == 'Z' || (uVar5 = (uint)(cVar3 == 'Z'), cVar3 == 'Z')))) {
    uVar5 = 0xfffffffa;
  }
  return uVar5;
}



/* Return real B90CA(22,2) signedR10, not void. Request record100 reset via existing learned
   lifecycle; pending ownership survives rejected setter. Published completion is not physical
   persistence. */

int f33_ba_f8_request_learned_reset(void)

{
  int iVar1;
  
  iVar1 = thunk_FUN_000b90ca(0x22,2);
  return iVar1;
}



/* Exact JTRM3 requests internal selector7 admission in allowed modes; start does not setB112. */

int f33_ba_f9_validate_jtrm3(uchar configured_index,uchar *payload,uchar *response)

{
  int iVar1;
  uint uVar2;
  
  uVar2 = f33_compare_ba_token_bytes(payload,"JTRM3VSPDASINC",'\x05');
  iVar1 = -6;
  if (uVar2 == 1) {
    iVar1 = f33_admit_internal_ba_selector(7,0);
  }
  return iVar1;
}



/* Return real B338C(7) R10=0; setB112=5A,B113=88. */

int f33_ba_f9_latch_selector7(void)

{
  int iVar1;
  
  iVar1 = f33_latch_internal_ba_selector(7);
  return iVar1;
}



/* Compare payload[1..4] with VSPD; require receive-status80A5!=0, then copy payload[0] unchanged
   to5F52. No numeric clamp, physical speed or persistence assertion. */

int f33_ba_fa_stage_unsigned_override(uchar configured_index,uchar *payload,uchar *response)

{
  char cVar1;
  uint32_t puVar2;
  uint uVar3;
  int iVar4;
  
  cVar1 = DAT_febe80a5;
  puVar2 = 0xfebeb800u;
  uVar3 = f33_compare_ba_token_bytes(payload + 1,"VSPDASINC",'\x04');
  if ((uVar3 == 1) && (cVar1 != '\0')) {
    iVar4 = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x58ae))))) = *payload;
  }
  else {
    iVar4 = -6;
  }
  return iVar4;
}



/* Return real B33BC(5F52) R10=0; setB116=5A andB117=staged unsigned byte. ScheduledBEE2C later
   selects zero-extendedB117<<7. */

int f33_ba_fa_latch_unsigned_override(void)

{
  int iVar1;
  
  iVar1 = f33_latch_ba_unsigned_override(f33_ba_application_work.staged_unsigned_override);
  return iVar1;
}



/* Exact ASINC returns0,otherwise-6. No mutation in start. */

int f33_ba_fb_validate_asinc(uchar configured_index,uchar *payload,uchar *response)

{
  uint uVar1;
  int iVar2;
  
  uVar1 = f33_compare_ba_token_bytes(payload,"ASINC",'\x05');
  if (uVar1 == 1) {
    iVar2 = 0;
  }
  else {
    iVar2 = -6;
  }
  return iVar2;
}



/* Return real B33CC R10=0; setB118=5A. Later owner5 rising-limit release selects fast coefficient;
   this does not directly set the limit or physical output. */

int f33_ba_fb_latch_owner5_fast_release(void)

{
  int iVar1;
  
  iVar1 = f33_latch_ba_owner5_fast_release();
  return iVar1;
}



/* Called by mode0700 entry, not an inferred timer or ignition event. If gate and count are nonzero,
   decrement low8 count, request record18; reaching0 also clears gate and requests zero record105.
   Ignore setter return and publish decremented RAM regardless. Gate5A/count0 remains unchanged. */

void f33_consume_ba_retained_admission_count(void)

{
  uint32_t puVar1;
  uchar uVar2;
  uchar uVar3;
  char local_1c [8];
  uint auStack_14 [2];
  
  puVar1 = 0xfebeb800u;
  uVar2 = f33_ba_application_work.admission;
  uVar3 = f33_ba_application_work.remaining_mode700_entries;
  if ((f33_ba_application_work.admission != '\0') &&
     (f33_ba_application_work.remaining_mode700_entries != '\0')) {
    local_1c[0] = f33_ba_application_work.remaining_mode700_entries + 0xff;
    local_1c[1] = 0;
    uVar3 = f33_ba_application_work.remaining_mode700_entries + 0xff;
    if (uVar3 == '\0') {
      uVar2 = '\0';
    }
    local_1c[2] = '\0';
    local_1c[3] = '\0';
    local_1c[4] = '\0';
    local_1c[5] = '\0';
    local_1c[6] = '\0';
    local_1c[7] = '\0';
    puVar1 = 0xfebeb800u;
    f33_nvm_set_record(0x18,((uint *)camry_host_ptr((uint32_t)(local_1c))));
    if (uVar2 == '\0') {
      auStack_14[0] = 0;
      auStack_14[1] = 0;
      f33_nvm_set_record(0x105,auStack_14);
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x58b0))))) = uVar3;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x58b1))))) = uVar2;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_3552e(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_35530(void)

{
  return;
}



undefined4 FUN_00035532(void)

{
  if ((((DAT_febe6ad2 == f33_learned_quad[0]) && (DAT_febe6ad4 == f33_learned_quad[1])) &&
      (DAT_febe6ad6 == f33_learned_quad[2])) && (DAT_febe6ad8 == f33_learned_quad[3])) {
    return 0;
  }
  return 0x5a;
}



void FUN_00035568(void)

{
  DAT_febe6ad2 = f33_learned_quad[0];
  DAT_febe6ad4 = f33_learned_quad[1];
  DAT_febe6ad6 = f33_learned_quad[2];
  DAT_febe6ad8 = f33_learned_quad[3];
  return;
}



void FUN_00035586(void)

{
  DAT_febe6ad2 = 0x800;
  DAT_febe6ad4 = 0x800;
  DAT_febe6ad6 = 0x800;
  DAT_febe6ad8 = 0x800;
  return;
}



void FUN_00035598(void)

{
  uint32_t puVar1;
  uint uVar2;
  uint uVar3;
  
  puVar1 = 0xfebeb800u;
  if (DAT_febe8a18 != 'Z') {
    return;
  }
  uVar3 = (uint)DAT_febe6ad0;
  uVar2 = (uint)DAT_febe6ad1;
  if ((DAT_febe6af0 == -0x5aa5a55b) && (DAT_febe6ae1 == '\0')) {
    puVar1 = 0xfebeb800u;
    uVar3 = FUN_00035532();
    if (uVar3 != 0x5a) {
      uVar2 = 0;
      goto LAB_000355e8;
    }
    uVar2 = f33_check_learned_quad_bounds();
    if (uVar2 == 0) {
      FUN_00035568();
      goto LAB_000355e8;
    }
  }
  FUN_00035586();
LAB_000355e8:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb2d0u + (uint32_t)((int)puVar1) * 1u)))) = (char)uVar3;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb2d1u + (uint32_t)((int)puVar1) * 1u)))) = (char)uVar2;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_355f4(void)

{
  return;
}



void FUN_000356c8(void)

{
  undefined2 uVar1;
  uint32_t puVar2;
  uint uVar3;
  uint uVar4;
  undefined1 uVar5;
  uint local_1c [4];
  
  puVar2 = 0xfebeb800u;
  uVar3 = f33_nvm_get_record(0x100, camry_host_addr(local_1c));
  if (uVar3 == 0x10) {
    if (local_1c[0] != 0) {
      if (local_1c[0] == 0xa55a5aa5) {
        f33_publish_learned_quad();
        uVar3 = f33_check_learned_quad_bounds();
        if (uVar3 == 0) {
          uVar5 = 0x44;
          f33_report_diagnostic_healthy_observed(0x128);
          uVar4 = f33_get_diagnostic_event_state(0xe);
          uVar3 = local_1c[0];
          if ((uVar4 & 1) == 0) {
            FUN_000524be(0xe);
          }
          else {
            f33_report_diagnostic_event_pass(0xe);
          }
          goto LAB_0003575c;
        }
      }
LAB_00035746:
      uVar3 = 0x5aa5a55a;
      uVar5 = 0x22;
      f33_report_diagnostic_event_failure(0x128,0x32);
      goto LAB_0003575c;
    }
    f33_report_diagnostic_healthy_observed(0x128);
  }
  else {
    if (uVar3 != 0x11) goto LAB_00035746;
    local_1c[0] = 0;
  }
  uVar5 = 0x44;
  FUN_00051d38(0xe,10,0x32);
  uVar3 = local_1c[0];
LAB_0003575c:
  uVar1 = DAT_00030e30;
  (*((uint *)camry_host_ptr((uint32_t)((0xffffb2f0u + (uint32_t)((int)puVar2)))))) = uVar3;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb2e0u + (uint32_t)((int)puVar2) * 1u)))) = uVar5;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb2e4u + (uint32_t)((int)puVar2)))))) = uVar1;
  return;
}



void FUN_00035772(ushort param_1,ushort param_2,ushort param_3,ushort param_4)

{
  f33_learned_quad[0] = param_1;
  f33_learned_quad[1] = param_2;
  f33_learned_quad[2] = param_3;
  f33_learned_quad[3] = param_4;
  return;
}



void FUN_00035780(void)

{
  uint32_t puVar1;
  uint local_14;
  ushort uStack_10;
  ushort uStack_e;
  ushort uStack_c;
  ushort uStack_a;
  undefined4 uStack_8;
  
  puVar1 = 0xfebeb800u;
  uStack_10 = f33_learned_quad[0];
  uStack_e = f33_learned_quad[1];
  uStack_c = f33_learned_quad[2];
  uStack_8 = 0;
  uStack_a = f33_learned_quad[3];
  local_14 = 0xa55a5aa5;
  f33_nvm_set_record(0x100,&local_14);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb2ddu + (uint32_t)((int)puVar1) * 1u)))) = 0x11;
  return;
}



void FUN_000357c0(void)

{
  char cVar1;
  undefined *puVar2;
  int iVar3;
  
  puVar2 = ((undefined *)camry_host_ptr(0xfebeb800u));
  if ((((DAT_febe6ae2 == '\x11') && (((int8_t)DAT_febe6add) != -0x78)) && (DAT_febe6add != '\x11')) &&
     (((DAT_febee8cc & 0xff00) != 0x500 || (DAT_febe6af0 != -0x5aa5a55b)))) {
    puVar2 = ((undefined *)camry_host_ptr(0xfebeb800u));
    if ((DAT_febe6add == '\"') ||
       (puVar2 = ((undefined *)camry_host_ptr(0xfebeb800u)), iVar3 = f33_queue_application_service('\x01'), iVar3 != -1)) {
      FUN_0004d0a4(8,0x20);
    }
    else {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb2ddu + (uint32_t)((int)camry_host_addr(puVar2)) * 1u)))) = 0x88;
    }
  }
  else {
    cVar1 = DAT_febe6ae2;
    if ((DAT_febe6ae2 != '\"') || (0x3fe < (DAT_febee8cc & 0xff00) - 0x201)) goto LAB_00035842;
    puVar2 = ((undefined *)camry_host_ptr(0xfebeb800u));
    FUN_00035772(0x800,0x800,0x800,0x800);
    FUN_00035780();
  }
  cVar1 = '\0';
LAB_00035842:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb2e2u + (uint32_t)((int)camry_host_addr(puVar2)) * 1u)))) = cVar1;
  return;
}



/* After357C0, decrement nonzero6AE4. Valid source66D5=5A and marker6AF0=A55A5AA5 invoke
   learned-quad restoration; failed restoration reports128 and sets6AE1=5A. Pending
   write/reset6ADD/6ADC poll record100: exact10 succeeds,high-nibble20 waits,other status reports130
   and publishes slot17/kind1. Write success restores valid marker and passes0E; reset success
   clears marker and reports0E through51D38. Publication and physical persistence remain distinct.
    */

void f33_step_learned_quad_record_completion(void)

{
  uint32_t puVar1;
  uint uVar2;
  undefined1 uVar3;
  char cVar4;
  char cVar5;
  uint uVar6;
  short sVar7;
  
  puVar1 = 0xfebeb800u;
  FUN_000357c0();
  sVar7 = (*((short *)camry_host_ptr((uint32_t)((0xffffb2e4u + (uint32_t)((int)puVar1))))));
  uVar6 = (*((uint *)camry_host_ptr((uint32_t)((0xffffb2f0u + (uint32_t)((int)puVar1))))));
  cVar5 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb2ddu + (uint32_t)((int)puVar1) * 1u))));
  cVar4 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb2dcu + (uint32_t)((int)puVar1) * 1u))));
  if (sVar7 != 0) {
    sVar7 = sVar7 + -1;
  }
  uVar3 = 0;
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x512b))))) == 'Z') && (uVar6 == 0xa55a5aa5)) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb2e1u + (uint32_t)((int)puVar1) * 1u)))) = 0x5a;
    uVar6 = f33_restore_learned_quad();
    if (uVar6 == 0xa55a5aa5) {
      uVar3 = 0;
    }
    else {
      f33_report_diagnostic_event_failure(0x128,0x32);
      uVar3 = 0x5a;
    }
  }
  if (cVar5 == '\x11') {
    uVar2 = f33_nvm_get_record_status(0x100);
    if (uVar2 == 0x10) {
      uVar6 = 0xa55a5aa5;
      cVar5 = 'D';
      f33_report_diagnostic_event_pass(0xe);
    }
    else if ((uVar2 & 0xf0) != 0x20) {
      cVar5 = '\"';
      f33_report_diagnostic_event_failure(0x130,0x32);
      f33_retain_and_clear_fault_record(0x11);
      f33_encode_fault_action_kind('\x11','\x01');
      f33_select_current_fault_record(0x11);
    }
  }
  if (cVar4 == '\x11') {
    uVar2 = f33_nvm_get_record_status(0x100);
    if (uVar2 == 0x10) {
      uVar6 = 0;
      cVar4 = 'D';
      FUN_00051d38(0xe,10,0x32);
    }
    else if ((uVar2 & 0xf0) != 0x20) {
      cVar4 = '\"';
      f33_report_diagnostic_event_failure(0x130,0x32);
      f33_retain_and_clear_fault_record(0x11);
      f33_encode_fault_action_kind('\x11','\x01');
      f33_select_current_fault_record(0x11);
    }
  }
  (*((uint *)camry_host_ptr((uint32_t)((0xffffb2f0u + (uint32_t)((int)puVar1)))))) = uVar6;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb2e4u + (uint32_t)((int)puVar1)))))) = sVar7;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb2ddu + (uint32_t)((int)puVar1) * 1u)))) = cVar5;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb2dcu + (uint32_t)((int)puVar1) * 1u)))) = cVar4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb2e1u + (uint32_t)((int)puVar1) * 1u)))) = uVar3;
  return;
}



void FUN_0003599e(void)

{
  uint32_t puVar1;
  undefined1 uVar2;
  uint local_18;
  undefined2 uStack_14;
  undefined2 uStack_12;
  undefined2 uStack_10;
  undefined2 uStack_e;
  undefined4 uStack_c;
  
  puVar1 = 0xfebeb800u;
  uVar2 = 0x44;
  if (DAT_febe6af0 != 0) {
    local_18 = 0;
    uStack_c = 0;
    uStack_e = 0x800;
    uStack_10 = 0x800;
    uStack_12 = 0x800;
    uStack_14 = 0x800;
    uVar2 = 0x11;
    puVar1 = 0xfebeb800u;
    f33_nvm_set_record(0x100,&local_18);
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb2dcu + (uint32_t)((int)puVar1) * 1u)))) = uVar2;
  return;
}



bool FUN_00035a06(void)

{
  int iVar1;
  ushort uVar2;
  ushort uVar3;
  char cVar4;
  char cVar5;
  char cVar6;
  ushort uVar7;
  bool bVar8;
  short sStack_1e;
  
  uVar7 = DAT_febee892;
  cVar6 = DAT_febee81a;
  cVar5 = DAT_febe80a5;
  cVar4 = DAT_febe80a0;
  uVar3 = DAT_febe66b8;
  uVar2 = DAT_febe6764 & 0x81ff;
  FUN_0006a522((int)DAT_febe66a8,&sStack_1e);
  if ((((cVar6 == '\x01') && (DAT_00030e32 <= uVar3)) && (uVar7 <= DAT_00030e34)) &&
     (((cVar5 == '\0' && (cVar4 == '\0')) &&
      (iVar1 = sStack_1e + -0x200, ((iVar1 < 0) || (sStack_1e < 0)))))) {
    bVar8 = uVar2 == 0;
  }
  else {
    bVar8 = false;
  }
  return bVar8;
}



void FUN_00035a68(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  FUN_00035a06();
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb2dfu + (uint32_t)((int)puVar1) * 1u)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb2deu + (uint32_t)((int)puVar1) * 1u)))) = 0;
  return;
}



void FUN_00035a7c(void)

{
  if (DAT_febe6af0 == 0) {
    f33_report_diagnostic_event_failure(0xe,0x32);
  }
  return;
}



undefined4 FUN_00035a96(void)

{
  DAT_febe6ae2 = 0x11;
  return 2;
}



void FUN_00035aa2(void)

{
  if ((((DAT_febe6af0 != -1) && (DAT_febe6af0 != -0x5aa5a55b)) && (((int8_t)DAT_febe6add) != -0x78)) &&
     ((DAT_febe6add != '\x11' && (DAT_febe6ae2 != '\x11')))) {
    DAT_febe6ae2 = '\"';
  }
  return;
}



void FUN_00035ad6(void)

{
  if (((int8_t)DAT_febe6add) == -0x78) {
    DAT_febe6add = '\0';
  }
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_35ae8(void)

{
  return;
}



/* Constant-block fill: 10 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_35aea(void)

{
  DAT_febe5f58 = 0;
  DAT_febe5f59 = 0;
  DAT_febe5f5a = 0;
  DAT_febe5f5e = DAT_0002bd02;
  DAT_febe5f60 = DAT_0002bd02;
  DAT_febe5f5b = 0;
  DAT_febe5f5c = 0;
  DAT_febe5f5d = 0;
  DAT_febe5f62 = DAT_0002bd06;
  DAT_febe5f64 = DAT_0002bd06;
  return;
}



undefined4 FUN_00035b12(undefined4 param_1,undefined4 param_2,uint param_3)

{
  undefined2 uVar1;
  byte bVar2;
  undefined4 uVar3;
  
  uVar1 = DAT_0002bd02;
  bVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5f58u + (uint32_t)(param_3 & 0xff) * 1u))));
  uVar3 = 0;
  if (DAT_0002bd00 <= bVar2) {
    uVar3 = 0x5a;
    bVar2 = 0;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5f58u + (uint32_t)(param_3 & 0xff) * 1u)))) = bVar2;
  (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe5f5eu + (uint32_t)(param_3 & 0xff) * 2u)))) = uVar1;
  return uVar3;
}



undefined4 FUN_00035b44(undefined4 param_1,undefined4 param_2,uint param_3)

{
  undefined2 uVar1;
  byte bVar2;
  undefined4 uVar3;
  
  uVar1 = DAT_0002bd06;
  param_3 = param_3 & 0xff;
  bVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5f5au + (uint32_t)(param_3) * 1u))));
  uVar3 = 0;
  if (DAT_0002bd01 <= bVar2) {
    uVar3 = 0x5a;
    bVar2 = 0;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5f5au + (uint32_t)(param_3) * 1u)))) = bVar2;
  (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe5f62u + (uint32_t)(param_3) * 2u)))) = uVar1;
  return uVar3;
}



void FUN_00035b78(void)

{
  undefined1 uVar1;
  int iVar2;
  int iVar3;
  
  uVar1 = DAT_febe5f5c;
  iVar2 = FUN_00035b12(0,DAT_febe5f5c,0);
  iVar3 = FUN_00035b12(0x0, (*((volatile uint8_t *)camry_host_ptr(0xfebe5f5du))), 0x1);
  if ((iVar2 == 0x5a) || (iVar3 == 0x5a)) {
    FUN_00051866();
    DAT_febe5f58 = 0;
    DAT_febe5f59 = 0;
    DAT_febe5f5e = DAT_0002bd02;
    DAT_febe5f60 = DAT_0002bd02;
  }
  iVar2 = FUN_00035b44(0,uVar1,0);
  iVar3 = FUN_00035b44(0x0, (*((volatile uint8_t *)camry_host_ptr(0xfebe5f5du))), 0x1);
  if ((iVar2 == 0x5a) || (iVar3 == 0x5a)) {
    thunk_FUN_000b90ca(0x22,0);
    DAT_febe5f5a = 0;
    DAT_febe5f5b = 0;
    DAT_febe5f62 = DAT_0002bd06;
    DAT_febe5f64 = DAT_0002bd06;
  }
  DAT_febe5f5c = 0;
  DAT_febe5f5d = 0;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_35c00(void)

{
  return;
}



void FUN_00035c02(void)

{
  DAT_febe5f6c = 0;
  DAT_febe5f68 = 0;
  DAT_febe5f6a = 0;
  DAT_febe5f69 = 0;
  return;
}



void FUN_00035c10(void)

{
  if ((DAT_0002bd08 <= DAT_febe5f6a) ||
     (DAT_febe5f6a = DAT_febe5f6a + 1, DAT_0002bd08 <= DAT_febe5f6a)) {
    DAT_febe5f69 = 0;
  }
  DAT_febe5f68 = 0;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_35c36(void)

{
  return;
}



void FUN_00035c38(void)

{
  FUN_00035c10();
  f33_return_only_stub_35c36();
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_35c48(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_35c4a(void)

{
  return;
}



/* Normally publish diagnostic6AF6=EE40A, pre-override6AF8=EE410 and motor6AF4=-EE40C. In mode
   family0500, E780==5A selects clamped EB10 first; otherwise EE406==5A selects clamped EE416. Exact
   ROM30F1C/31914 are zero, so their forced branch is inactive. Command publication and current
   conversion use separate interrupt contexts. Motor sample normally negates EE40C; family0500
   permits two explicitly prioritized bounded service substitutions. Diagnostic mirror EE40A is a
   separate sample. Static instructions/dataflow; no new vehicle behavior. */

void f33_sample_motor_command(void)

{
  short sVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  
  iVar5 = (int)((int)(int16_t)DAT_febee782);
  iVar4 = (int)((int)(int16_t)DAT_febeeb10);
  iVar2 = (int)((int)(int16_t)DAT_febee416);
  iVar3 = (int)((int)(int16_t)DAT_febee418);
  if ((DAT_00030f1c == 'Z') && (DAT_00031914 == 'Z')) {
    DAT_febe6af4 = DAT_00031916;
    DAT_febe6af6 = DAT_00031916;
    DAT_febe6af8 = DAT_00031916;
    DAT_febe6afa = ((int)(int16_t)DAT_febee782);
    return;
  }
  DAT_febe6af6 = ((int)(int16_t)DAT_febee40a);
  DAT_febe6af8 = ((int)(int16_t)DAT_febee410);
  sVar1 = ((int)(int16_t)DAT_febee40c);
  if ((DAT_febeeb1e & 0xff00) == 0x500) {
    if (DAT_febee780 == 'Z') {
      if (iVar5 - iVar4 < 0 != (iVar5 < 0 != iVar4 < 0 && iVar4 < 0 == iVar5 - iVar4 < 0)) {
        iVar4 = iVar5;
      }
      iVar3 = -iVar5;
      if (iVar4 + iVar5 < 0 == (iVar4 < 0 != iVar3 < 0 && iVar3 < 0 == iVar4 + iVar5 < 0)) {
        iVar3 = iVar4;
      }
      DAT_febe6af8 = (short)iVar3;
      DAT_febe6af6 = ((int)(int16_t)DAT_febeeb10);
      sVar1 = DAT_febe6af8;
    }
    else if (DAT_febee406 == 'Z') {
      iVar4 = (int)-((int)(int16_t)DAT_febee418);
      if (iVar2 - iVar3 < 0 != (iVar2 < 0 != iVar3 < 0 && iVar3 < 0 == iVar2 - iVar3 < 0)) {
        iVar3 = iVar2;
      }
      if (iVar3 - iVar4 < 0 == (iVar3 < 0 != iVar4 < 0 && iVar4 < 0 == iVar3 - iVar4 < 0)) {
        iVar4 = iVar3;
      }
      DAT_febe6af8 = (short)iVar4;
      DAT_febe6af6 = ((int)(int16_t)DAT_febee416);
      sVar1 = DAT_febe6af8;
    }
  }
  DAT_febe6af4 = -sVar1;
  DAT_febe6afa = ((int)(int16_t)DAT_febee782);
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_35ce8(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_35cea(void)

{
  return;
}



/* 71ECbit0 disables branch; otherwise selectedconstant minus62BC*62D4,dividebyabs62D6
   orboundonzero,clamp\u00b126604 into6AFC. No physicalunitsassigned. otherwise selectedconstant
   minus62BC*62D4,dividebyabs62D6 orboundonzero,clamp±26604 into6AFC. */

void f33_update_limit_budget_branch0(void)

{
  int iVar1;
  int iVar2;
  
  if ((DAT_febe71ec & 1) != 0) {
    DAT_febe6afc = 0;
    DAT_febe6b00 = 0;
    DAT_febe6b04 = 0;
    return;
  }
  iVar1 = DAT_00031938;
  if ((DAT_febe71ec >> 1 & 1) != 0) {
    iVar1 = DAT_0003193c;
  }
  iVar2 = (int)DAT_febe62d6;
  DAT_febe6b04 = iVar1 - (int)DAT_febe62bc * (int)DAT_febe62d4;
  if (iVar2 < 0) {
    iVar2 = -iVar2;
  }
  else {
    iVar1 = DAT_0003191c;
    if (iVar2 == 0) goto LAB_00035d38;
  }
  iVar1 = DAT_febe6b04;
  if (iVar2 != 0) {
    if (DAT_febe6b04 == -0x80000000 && iVar2 == -1) {
      iVar1 = -0x80000000;
    }
    else {
      iVar1 = DAT_febe6b04 / iVar2;
    }
  }
LAB_00035d38:
  iVar2 = DAT_0003191c;
  if (iVar1 - DAT_0003191c < 0 !=
      (iVar1 < 0 != DAT_0003191c < 0 && DAT_0003191c < 0 == iVar1 - DAT_0003191c < 0)) {
    iVar2 = iVar1;
  }
  DAT_febe6afc = -DAT_0003191c;
  if (iVar2 + DAT_0003191c < 0 ==
      (iVar2 < 0 != DAT_febe6afc < 0 && DAT_febe6afc < 0 == iVar2 + DAT_0003191c < 0)) {
    DAT_febe6afc = iVar2;
  }
  DAT_febe6b00 = (int)DAT_febe62bc * (int)DAT_febe62d4;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_35d54(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_35d56(void)

{
  return;
}



/* Companionbranch using71ECbit1,62C0*62D8 andabs62DA,clamp\u00b126604
   into6B08;otherchannelbitselectsalternateconstant. Companionbranch using71ECbit1,62C0*62D8
   andabs62DA,clamp±26604 into6B08;otherchannelbitselectsalternateconstant. */

void f33_update_limit_budget_branch1(void)

{
  int iVar1;
  int iVar2;
  
  if ((DAT_febe71ec & 2) != 0) {
    DAT_febe6b08 = 0;
    DAT_febe6b0c = 0;
    DAT_febe6b10 = 0;
    return;
  }
  iVar1 = DAT_00031938;
  if ((DAT_febe71ec & 1) != 0) {
    iVar1 = DAT_0003193c;
  }
  iVar2 = (int)((int)(int16_t)DAT_febe62da);
  DAT_febe6b10 = iVar1 - (int)((int)(int16_t)DAT_febe62c0) * (int)((int)(int16_t)DAT_febe62d8);
  if (iVar2 < 0) {
    iVar2 = -iVar2;
  }
  else {
    iVar1 = DAT_00031920;
    if (iVar2 == 0) goto LAB_00035da4;
  }
  iVar1 = DAT_febe6b10;
  if (iVar2 != 0) {
    if (DAT_febe6b10 == -0x80000000 && iVar2 == -1) {
      iVar1 = -0x80000000;
    }
    else {
      iVar1 = DAT_febe6b10 / iVar2;
    }
  }
LAB_00035da4:
  iVar2 = DAT_00031920;
  if (iVar1 - DAT_00031920 < 0 !=
      (iVar1 < 0 != DAT_00031920 < 0 && DAT_00031920 < 0 == iVar1 - DAT_00031920 < 0)) {
    iVar2 = iVar1;
  }
  DAT_febe6b08 = -DAT_00031920;
  if (iVar2 + DAT_00031920 < 0 ==
      (iVar2 < 0 != DAT_febe6b08 < 0 && DAT_febe6b08 < 0 == iVar2 + DAT_00031920 < 0)) {
    DAT_febe6b08 = iVar2;
  }
  DAT_febe6b0c = (int)((int)(int16_t)DAT_febe62c0) * (int)((int)(int16_t)DAT_febe62d8);
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_35dc0(void)

{
  return;
}



/* Seedfilteredbudget,maprequest/finalrequest26604, bothaccumulators26604<<16;
   clearnegativequalificationandreleasemarkers/counts. */

void f33_reset_owner9_budget_limit_state(void)

{
  DAT_febe6b14 = 0;
  DAT_febe6b15 = 0;
  DAT_febe6b1e = 0;
  DAT_febe6b18 = DAT_0003192a;
  DAT_febe6b24 = (uint)DAT_0003192a << 0x10;
  DAT_febe6b1a = DAT_0003192a;
  DAT_febe6b16 = DAT_0003192a;
  DAT_febe6b28 = (uint)DAT_0003192a << 0x10;
  DAT_febe6b1c = 0;
  return;
}



/* Zeroextend low16budget; map38678 withsigned6422 selector, signedcap22170 andzeroextendresult. */

uint f33_map_owner9_budget_limit(uint budget)

{
  uint uVar1;
  
  uVar1 = f33_lookup_signed_five_map_signal(budget & 0xffff,DAT_febe6422);
  if ((int)(uVar1 - 0x569a) < 0 == ((int)uVar1 < 0 && -1 < (int)(uVar1 - 0x569a))) {
    uVar1 = 0x569a;
  }
  return uVar1 & 0xffff;
}



/* Enabledmode33 withcalibratedrisegain0 holdsincreasesandpassesdecreases, thenclamp[0,22170].
   Othermode11lowpass/mode22stepremainnotselectedbythisimage. */

uint f33_follow_owner9_limit_request(uint target)

{
  short sVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  int iVar5;
  uint uVar6;
  int iVar7;
  undefined *puVar8;
  undefined *puVar9;
  
  uVar4 = target & 0xffff;
  uVar6 = 0;
  DAT_febe6b1e = 0;
  uVar2 = (uint)DAT_febe6b16;
  puVar9 = ((undefined *)camry_host_ptr((uint32_t)((uint)DAT_febe6b1c)));
  uVar3 = uVar4;
  if (DAT_00031925 == 'Z') {
    sVar1 = (short)target;
    if (DAT_00031926 == '\x11') {
      if (uVar2 <= uVar4) {
        uVar3 = (uint)DAT_0003192c;
        if (uVar3 - 1 < 0xffff) {
          iVar5 = uVar2 * uVar3;
          iVar7 = uVar4 * uVar3;
        }
        else {
          iVar5 = uVar2 << 0x10;
          iVar7 = target << 0x10;
        }
        DAT_febe6b28 = iVar7 + (DAT_febe6b28 - iVar5);
        iVar5 = (int)DAT_00031930;
        iVar7 = (int)(short)(sVar1 - (short)(DAT_febe6b28 >> 0x10));
        uVar3 = DAT_febe6b28 >> 0x10;
        if (iVar7 - iVar5 < 0 == (iVar7 < 0 != iVar5 < 0 && iVar5 < 0 == iVar7 - iVar5 < 0) &&
            iVar7 != iVar5) goto LAB_00035ec0;
      }
      DAT_febe6b28 = target << 0x10;
      uVar3 = uVar4;
    }
    else {
      if (DAT_00031926 == '\"') {
        uVar3 = (uint)(short)(sVar1 - DAT_febe6b16);
        iVar5 = DAT_0003192e - uVar3;
        puVar8 = puVar9;
        if (iVar5 < 0 != ((int)uVar3 < 0 && (int)uVar3 < 0 == iVar5 < 0)) {
          uVar3 = (uint)DAT_0003192e;
        }
      }
      else {
        if (DAT_00031926 != '3') goto LAB_00035ec0;
        puVar8 = (undefined *)0x0;
        if ((uVar2 < uVar4) &&
           (puVar8 = ((undefined *)camry_host_ptr((uint32_t)((uint)camry_host_addr((puVar9 + 1)) & 0xffff))),(uintptr_t)(((undefined *)camry_host_ptr(0xfffdu)))<(uintptr_t)(puVar8))) {
          puVar8 = ((undefined *)camry_host_ptr((uint32_t)(0xfffe)));
        }
        uVar6 = (uint)((int)camry_host_addr(puVar8) * DAT_00031940) >> 3;
        if (0x5699 < uVar6) {
          uVar6 = 0x569a;
        }
        uVar3 = (uint)(short)(sVar1 - DAT_febe6b16);
        if ((int)(uVar6 - uVar3) < 0 !=
            ((int)uVar3 < 0 && (int)uVar3 < 0 == (int)(uVar6 - uVar3) < 0)) {
          uVar3 = uVar6;
        }
      }
      DAT_febe6b1e = (undefined2)uVar6;
      DAT_febe6b1c = (ushort)puVar8;
      uVar3 = uVar2 + uVar3 & 0xffff;
    }
  }
LAB_00035ec0:
  uVar2 = (uint)DAT_00031932;
  DAT_febe6b20 = (short)uVar3;
  if (uVar3 < uVar2) {
    uVar2 = uVar3;
  }
  uVar3 = (uint)DAT_00031934;
  if (uVar3 <= uVar2) {
    uVar3 = uVar2;
  }
  return uVar3;
}



/* Clampbranchsum[0,26604],filterunsignedbudget,mapandretainrequest. Sustainednegative62DCmarkerA5
   or7827/7937nonzero bypassesrequesttonominal22170. RealFDFD4callerpublishesowner9. */

void f33_publish_owner9_budget_limit(void)

{
  uint uVar1;
  uint32_t puVar2;
  uint uVar3;
  uint uVar4;
  ushort limit;
  int iVar5;
  int iVar6;
  
  puVar2 = 0xfebeb800u;
  if (((int)(int16_t)DAT_febe62dc) < 0) {
    if (DAT_febe6b15 < DAT_00031924) {
      DAT_febe6b15 = DAT_febe6b15 + 1;
      DAT_febe6b14 = 'Z';
    }
    else {
      DAT_febe6b14 = -0x5b;
    }
  }
  else {
    DAT_febe6b15 = 0;
    DAT_febe6b14 = '\0';
  }
  uVar1 = DAT_febe6b08 + DAT_febe6afc;
  uVar4 = (uint)DAT_0003192a;
  if ((int)(uVar1 - uVar4) < 0 != ((int)uVar1 < 0 && -1 < (int)(uVar1 - uVar4))) {
    uVar4 = uVar1;
  }
  if ((int)uVar4 < 0) {
    uVar4 = 0;
  }
  uVar1 = (uint)DAT_00031928;
  if (uVar1 - 1 < 0xffff) {
    iVar5 = DAT_febe6b18 * uVar1;
    iVar6 = (uVar4 & 0xffff) * uVar1;
  }
  else {
    iVar5 = (uint)DAT_febe6b18 << 0x10;
    iVar6 = uVar4 << 0x10;
  }
  uVar1 = iVar6 + (DAT_febe6b24 - iVar5);
  if (((((int8_t)DAT_febe6b14) == -0x5b) || (DAT_febe7827 != '\0')) || (DAT_febe7937 != '\0')) {
    uVar4 = 0x569a;
    limit = 0x569a;
    DAT_febe6b28 = 0x569a0000;
  }
  else {
    puVar2 = 0xfebeb800u;
    uVar4 = f33_map_owner9_budget_limit(uVar1 >> 0x10);
    uVar3 = f33_follow_owner9_limit_request(uVar4);
    limit = (ushort)uVar3;
  }
  f33_set_current_limit_request(9,limit);
  (*((short *)camry_host_ptr((uint32_t)((0xffffb318u + (uint32_t)((int)puVar2)))))) = (short)(uVar1 >> 0x10);
  (*((uint *)camry_host_ptr((uint32_t)((0xffffb324u + (uint32_t)((int)puVar2)))))) = uVar1;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb31au + (uint32_t)((int)puVar2)))))) = (short)uVar4;
  (*((ushort *)camry_host_ptr((uint32_t)((0xffffb316u + (uint32_t)((int)puVar2)))))) = limit;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_35fac(void)

{
  return;
}



/* Clear active6B2C,phase6B2D,reserved6B2E and invocation counter6B30. Does not itself release slot1
   or request word7. */

void f33_initialize_terminal_output_ramp(void)

{
  DAT_febe6b2c = 0;
  DAT_febe6b2d = 0;
  DAT_febe6b2e = 0;
  DAT_febe6b30 = 0;
  return;
}



/* Only active6B2C==5A publishes slot1 in both banks. Entry count<60000 requests owner7 mask40004,
   advances by200 only when6798==1 otherwise1, interpolates exact30E60, and sets phase1. Map is0
   through59950 then rises to8000 at60000. Already-terminal count requests70017001, codes8000 and
   phase2 without advancing. Inactive clears request7/count/phase and releases slot1, retaining its
   triplets. No wall-time or electrical-duty claim; later aggregate neutral slot3 can outrank slot1.
    */

void f33_step_terminal_output_ramp(void)

{
  short sVar1;
  uint32_t puVar2;
  undefined1 uVar3;
  ushort uVar4;
  ushort uStack_1a;
  ushort uStack_18;
  ushort uStack_16;
  ushort uStack_14;
  ushort uStack_12;
  ushort uStack_10;
  ushort uStack_e;
  
  uVar4 = DAT_febe6b30;
  puVar2 = 0xfebeb800u;
  if (DAT_febe6b2c == 'Z') {
    if (DAT_febe6b30 < DAT_00030e5a) {
      puVar2 = 0xfebeb800u;
      f33_set_output_request_word('\a',0x40004);
      sVar1 = DAT_00030e5c;
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x5068))))) != '\x01') {
        sVar1 = 1;
      }
      uVar4 = uVar4 + sVar1;
      FUN_00070304(((undefined *)camry_host_ptr(0x30e60u)),uVar4,&uStack_1a);
      uVar3 = 1;
    }
    else {
      puVar2 = 0xfebeb800u;
      f33_set_output_request_word('\a',0x70017001);
      uStack_1a = 0x8000;
      uVar3 = 2;
    }
    uStack_18 = uStack_1a;
    uStack_16 = uStack_1a;
    uStack_14 = uStack_1a;
    uStack_12 = uStack_1a;
    uStack_10 = uStack_1a;
    uStack_e = uStack_1a;
    f33_write_phase_output_slot_pair(2,'\x01',&uStack_12,&uStack_18);
    f33_activate_phase_output_slot_pair('\x01');
  }
  else {
    f33_set_output_request_word('\a',0);
    uVar4 = 0;
    uVar3 = 0;
    f33_release_phase_output_slot_pair('\x01');
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb32du + (uint32_t)((int)puVar2) * 1u)))) = uVar3;
  (*((ushort *)camry_host_ptr((uint32_t)((0xffffb330u + (uint32_t)((int)puVar2)))))) = uVar4;
  return;
}



undefined1 FUN_00036066(byte param_1,short param_2)

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



/* Set active6B2C=5A only; do not reset retained ramp count. Fault output router3C470 is the
   recovered requester. */

void f33_request_terminal_output_ramp(void)

{
  DAT_febe6b2c = 0x5a;
  return;
}



/* Clear active6B2C only. Subsequent35FBC invocation clears request7/count/phase and releases slot1;
   this setter is not immediate output retirement. */

void f33_cancel_terminal_output_ramp(void)

{
  DAT_febe6b2c = 0;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_360cc(void)

{
  return;
}



void FUN_000360ce(void)

{
  DAT_febe6798 = 0;
  DAT_febe6799 = DAT_00030e70;
  return;
}



void FUN_000360e0(void)

{
  int iVar1;
  bool bVar2;
  char cVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  
  iVar5 = -(int)DAT_febe64e2;
  cVar3 = DAT_00030e70;
  if ((DAT_febe64cc & 0x40004) == 0) {
    DAT_febe6798 = 0;
  }
  else {
    iVar6 = (int)DAT_febe6770;
    iVar7 = (int)DAT_00030e72;
    if (((iVar6 - iVar7 < 0 == (iVar6 < 0 != iVar7 < 0 && iVar7 < 0 == iVar6 - iVar7 < 0) &&
          iVar6 != iVar7) &&
        (iVar4 = (int)DAT_00030e74, iVar1 = iVar5 + -iVar4,
        iVar1 < 0 == (iVar5 < 0 != iVar4 < 0 && iVar4 < 0 == iVar1 < 0) &&
        -iVar4 != (int)DAT_febe64e2)) ||
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



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_36140(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_36142(void)

{
  return;
}



/* WARNING: Removing unreachable block (ram,0x00036250) */
/* WARNING: Removing unreachable block (ram,0x0003624a) */
/* WARNING: Removing unreachable block (ram,0x00036230) */
/* WARNING: Removing unreachable block (ram,0x00036222) */
/* WARNING: Removing unreachable block (ram,0x0003621e) */
/* WARNING: Removing unreachable block (ram,0x0003621a) */
/* WARNING: Removing unreachable block (ram,0x000361a8) */
/* WARNING: Removing unreachable block (ram,0x000361a2) */
/* WARNING: Removing unreachable block (ram,0x00036188) */
/* WARNING: Removing unreachable block (ram,0x0003617a) */
/* WARNING: Removing unreachable block (ram,0x00036176) */
/* WARNING: Removing unreachable block (ram,0x00036172) */
/* Transform two conditioned phase-current banks using measured-frame coefficient pairs7D4E/50
   and7D5A/5C. Keep32-bit results6B3C/40/44/48 plus saturated halfword mirrors6B34..3A. ADC/DMA
   freshness and physical phase identity are separate dependencies. Dual-bank measured
   phase-to-rotating-frame transform preserves32-bit outputs and separate saturated halfword
   mirrors. Measured-frame coefficients differ from output-frame coefficients. ADC freshness and
   rotor/sample alignment not established. */

void f33_transform_measured_phase_currents(void)

{
  int iVar1;
  int iVar2;
  
  iVar2 = (((((int)(int16_t)DAT_febe7e46) * 2 - (int)((int)(int16_t)DAT_febe7e48)) - (int)((int)(int16_t)DAT_febe7e4a)) * 0x3441) / 0x8000;
  iVar1 = (((int)((int)(int16_t)DAT_febe7e48) - (int)((int)(int16_t)DAT_febe7e4a)) * 0x5a82) / 0x8000;
  DAT_febe6b3c = (iVar1 * (((int)(int16_t)DAT_febe7d4e) / 4) + iVar2 * (((int)(int16_t)DAT_febe7d50) / 4)) / 0x2000;
  DAT_febe6b40 = (iVar1 * (((int)(int16_t)DAT_febe7d50) / 4) - iVar2 * (((int)(int16_t)DAT_febe7d4e) / 4)) / 0x2000;
  if ((int)DAT_febe6b3c + 0x7fff < 0 == (-1 < (int)DAT_febe6b3c && (int)DAT_febe6b3c + 0x7fff < 0) &&
      DAT_febe6b3c != -0x7fff) {
    iVar2 = DAT_febe6b3c;
    if ((int)DAT_febe6b3c + -0x7fff < 0 == ((int)DAT_febe6b3c < 0 && -1 < (int)DAT_febe6b3c + -0x7fff) &&
        DAT_febe6b3c != 0x7fff) {
      iVar2 = 0x7fff;
    }
  }
  else {
    iVar2 = -0x7fff;
  }
  DAT_febe6b34 = (short)iVar2;
  if ((int)DAT_febe6b40 + 0x7fff < 0 == (-1 < (int)DAT_febe6b40 && (int)DAT_febe6b40 + 0x7fff < 0) &&
      DAT_febe6b40 != -0x7fff) {
    iVar2 = DAT_febe6b40;
    if ((int)DAT_febe6b40 + -0x7fff < 0 == ((int)DAT_febe6b40 < 0 && -1 < (int)DAT_febe6b40 + -0x7fff) &&
        DAT_febe6b40 != 0x7fff) {
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
      DAT_febe6b44 != -0x7fff) {
    iVar2 = DAT_febe6b44;
    if ((int)DAT_febe6b44 + -0x7fff < 0 == ((int)DAT_febe6b44 < 0 && -1 < (int)DAT_febe6b44 + -0x7fff) &&
        DAT_febe6b44 != 0x7fff) {
      iVar2 = 0x7fff;
    }
  }
  else {
    iVar2 = -0x7fff;
  }
  DAT_febe6b38 = (short)iVar2;
  if ((int)DAT_febe6b48 + 0x7fff < 0 == (-1 < (int)DAT_febe6b48 && (int)DAT_febe6b48 + 0x7fff < 0) &&
      DAT_febe6b48 != -0x7fff) {
    iVar2 = DAT_febe6b48;
    if ((int)DAT_febe6b48 + -0x7fff < 0 == ((int)DAT_febe6b48 < 0 && -1 < (int)DAT_febe6b48 + -0x7fff) &&
        DAT_febe6b48 != 0x7fff) {
      iVar2 = 0x7fff;
    }
  }
  else {
    iVar2 = -0x7fff;
  }
  DAT_febe6b3a = (short)iVar2;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_36296(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_36298(void)

{
  return;
}



/* Unsigned EB94 window[8960,38400), plus abs(s16 63D4)>=2347 or abs63D4>=1630 and abs63D8>=2048,
   forms predicate5A. Rising predicate OR prior active5A with count<3000 admits only if7568/E603
   zero,71EC&1FF zero andEB83=11. Predicate is published even on denied activation. Failed admission
   clears active/count; admitted count increments only below3000. A new edge at3000 can retain
   active for that invocation without restarting the budget. Raw invocation count and sampled
   qualifiers have no assigned physical units. */

void f33_update_transient_current_reference_qualification(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uchar uVar4;
  int iVar5;
  
  iVar2 = (int)((int)(int16_t)DAT_febe63d8);
  iVar5 = (int)((int)(int16_t)DAT_febe63d4);
  if (((DAT_febeeb94 < f33_current_reference_qualification.window_lower_inclusive) ||
      (f33_current_reference_qualification.window_upper_exclusive <= DAT_febeeb94)) ||
     (((iVar3 = (int)f33_current_reference_qualification.first_absolute_threshold,
       iVar5 - iVar3 < 0 != (iVar5 < 0 != iVar3 < 0 && iVar3 < 0 == iVar5 - iVar3 < 0) &&
       (iVar1 = -iVar3,
       iVar5 + iVar3 < 0 == (iVar5 < 0 != iVar1 < 0 && iVar1 < 0 == iVar5 + iVar3 < 0) &&
       iVar5 != iVar1)) &&
      (((iVar3 = (int)f33_current_reference_qualification.first_combined_threshold,
        iVar5 - iVar3 < 0 != (iVar5 < 0 != iVar3 < 0 && iVar3 < 0 == iVar5 - iVar3 < 0) &&
        (iVar1 = -iVar3,
        iVar5 + iVar3 < 0 == (iVar5 < 0 != iVar1 < 0 && iVar1 < 0 == iVar5 + iVar3 < 0) &&
        iVar5 != iVar1)) ||
       ((iVar5 = (int)f33_current_reference_qualification.second_combined_threshold,
        iVar2 - iVar5 < 0 != (iVar2 < 0 != iVar5 < 0 && iVar5 < 0 == iVar2 - iVar5 < 0) &&
        (iVar3 = -iVar5,
        iVar2 + iVar5 < 0 == (iVar2 < 0 != iVar3 < 0 && iVar3 < 0 == iVar2 + iVar5 < 0) &&
        iVar2 != iVar3)))))))) {
    uVar4 = '\0';
  }
  else {
    uVar4 = 'Z';
  }
  if (((((f33_current_reference_transient.previous_predicate == '\0') && (uVar4 == 'Z')) ||
       ((f33_current_reference_transient.active == 'Z' &&
        (f33_current_reference_transient.invocation_count <
         f33_current_reference_qualification.count_limit)))) &&
      (((DAT_febe7568 == '\0' && (DAT_febee603 == '\0')) && ((DAT_febe71ec & 0x1ff) == 0)))) &&
     (DAT_febeeb83 == '\x11')) {
    f33_current_reference_transient.active = 'Z';
    if (f33_current_reference_transient.invocation_count <
        f33_current_reference_qualification.count_limit) {
      f33_current_reference_transient.invocation_count =
           f33_current_reference_transient.invocation_count + 1;
    }
  }
  else {
    f33_current_reference_transient.active = '\0';
    f33_current_reference_transient.invocation_count = 0;
  }
  f33_current_reference_transient.previous_predicate = uVar4;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_36344(void)

{
  return;
}



/* Clear output, previous error, current error, gains, raw/clamped correction fields and opaque
   reset-only word. Retain measured ratio and padding; do not clear the separate387CE staged
   snapshot. */

void f33_reset_bank0_current_reference_feedback(void)

{
  f33_current_reference_feedback[0].request = 0;
  f33_current_reference_feedback[0].error = 0;
  f33_current_reference_feedback[0].previous_error = 0;
  f33_current_reference_feedback[0].opaque_14 = 0;
  f33_current_reference_feedback[0].request_before_global_clamp = 0;
  f33_current_reference_feedback[0].current_gain = 0;
  f33_current_reference_feedback[0].previous_gain = 0;
  f33_current_reference_feedback[0].retained_transient_delta = 0;
  f33_current_reference_feedback[0].saturated_base_plus_delta = 0;
  return;
}



/* Mode-entry initializer forwards to bank0 feedback reset; no enable test or acquisition. */

void f33_initialize_bank0_current_reference_feedback(void)

{
  f33_reset_bank0_current_reference_feedback();
  return;
}



/* WARNING: Removing unreachable block (ram,0x000364d4) */
/* WARNING: Removing unreachable block (ram,0x00036442) */
/* WARNING: Removing unreachable block (ram,0x0003643e) */
/* WARNING: Removing unreachable block (ram,0x00036432) */
/* WARNING: Removing unreachable block (ram,0x000363f8) */
/* Use prior unclipped second-axis regulator output: saturating signed16 absolute magnitude*1024
   divided by min(bank envelope,shared6CE4). Zero denominator selects1024; ratio clamps0..1024.
   Error922-ratio clamps-1024..1024 and halves toward zero when71EC&3. Gains6144/-1228,
   or30720/-6144 for transient5A; exact optional gain-scaling flag0. Correction is
   low32(gain0*error-gain1*previous_error), added to prior6DCA*32768 with symmetric signed32
   saturation. Transient path then clamps the relative delta to +/-41943040 and re-adds baseline
   without another saturation. Global bounds[-726474424,0], division toward zero by32768 and
   signed16 publication follow. Normal mode retains old transient delta. Native scheduled
   composition checks independent histories and zero-denominator behavior. */

void f33_update_bank0_current_reference_feedback(void)

{
  short sVar1;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  short sVar2;
  
  iVar5 = (int)f33_shared_second_axis_envelope;
  iVar6 = (int)f33_regulator_output_envelopes[0].second_upper;
  iVar3 = f33_regulator_output_envelopes[0].second_unclipped;
  if (f33_regulator_output_envelopes[0].second_unclipped + -0x7fff < 0 ==
      (f33_regulator_output_envelopes[0].second_unclipped < 0 &&
      -1 < f33_regulator_output_envelopes[0].second_unclipped + -0x7fff)) {
    iVar3 = 0x7fff;
  }
  if (iVar3 + 0x7fff < 0 != (-1 < iVar3 && iVar3 + 0x7fff < 0)) {
    iVar3 = -0x7fff;
  }
  iVar4 = (int)(short)iVar3;
  iVar7 = iVar6;
  if (((f33_current_reference_feedback_calibration[0].bypass_shared_ceiling == '\0') &&
      (f33_current_reference_feedback_calibration[0].shared_ceiling_enabled != '\0')) &&
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
    iVar4 = (int)f33_current_reference_feedback_calibration[0].ratio_upper;
  }
  else {
    iVar4 = iVar4 << 10;
    if (iVar7 != 0) {
      if (iVar4 == -0x80000000 && iVar7 == -1) {
        iVar4 = -0x80000000;
      }
      else {
        iVar4 = iVar4 / iVar7;
      }
    }
  }
  iVar3 = (int)f33_current_reference_feedback_calibration[0].ratio_upper;
  if (iVar3 - iVar4 < 0 != (iVar3 < 0 != iVar4 < 0 && iVar4 < 0 == iVar3 - iVar4 < 0)) {
    iVar4 = iVar3;
  }
  if (iVar4 < 0) {
    iVar4 = 0;
  }
  f33_current_reference_feedback[0].ratio = (short)iVar4;
  iVar5 = (int)f33_current_reference_feedback_calibration[0].ratio_target - (int)(short)iVar4;
  if (iVar3 - iVar5 < 0 != (iVar3 < 0 != iVar5 < 0 && iVar5 < 0 == iVar3 - iVar5 < 0)) {
    iVar5 = iVar3;
  }
  f33_current_reference_feedback[0].error =
       (int)f33_current_reference_feedback_calibration[0].error_lower;
  if (iVar5 - f33_current_reference_feedback[0].error < 0 ==
      (iVar5 < 0 != f33_current_reference_feedback[0].error < 0 &&
      f33_current_reference_feedback[0].error < 0 ==
      iVar5 - f33_current_reference_feedback[0].error < 0)) {
    f33_current_reference_feedback[0].error = iVar5;
  }
  if ((DAT_febe71ec & 3) != 0) {
    f33_current_reference_feedback[0].error = f33_current_reference_feedback[0].error / 2;
  }
  sVar1 = f33_current_reference_feedback_calibration[0].normal_current_gain;
  sVar2 = f33_current_reference_feedback_calibration[0].normal_previous_gain;
  if (f33_current_reference_transient.active == 'Z') {
    sVar1 = f33_current_reference_feedback_calibration[0].transient_current_gain;
    sVar2 = f33_current_reference_feedback_calibration[0].transient_previous_gain;
  }
  f33_current_reference_feedback[0].previous_gain = (int)sVar2;
  f33_current_reference_feedback[0].current_gain = (int)sVar1;
  if (f33_current_reference_feedback_calibration[0].error_gain_scaling_enabled == 'Z') {
    iVar3 = f33_current_reference_feedback_calibration[0].nonpositive_error_gain_scale;
    if (0 < f33_current_reference_feedback[0].error) {
      iVar3 = f33_current_reference_feedback_calibration[0].positive_error_gain_scale;
    }
    iVar3 = (f33_current_reference_feedback[0].error * iVar3) / 0x1000;
    f33_current_reference_feedback[0].current_gain =
         (f33_current_reference_feedback[0].current_gain * iVar3) / 0x1000;
    f33_current_reference_feedback[0].previous_gain =
         (f33_current_reference_feedback[0].previous_gain * iVar3) / 0x1000;
  }
  iVar6 = (int)f33_first_current_feedback_baseline;
  iVar5 = iVar6 * 0x8000;
  iVar3 = f33_current_reference_feedback[0].current_gain * f33_current_reference_feedback[0].error -
          f33_current_reference_feedback[0].previous_gain *
          f33_current_reference_feedback[0].previous_error;
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
  f33_current_reference_feedback[0].saturated_base_plus_delta = iVar3;
  if (f33_current_reference_transient.active == 'Z') {
    iVar3 = iVar3 + iVar6 * -0x8000;
    if (f33_current_reference_feedback_calibration[0].transient_delta_upper - iVar3 < 0 !=
        (f33_current_reference_feedback_calibration[0].transient_delta_upper < 0 != iVar3 < 0 &&
        iVar3 < 0 == f33_current_reference_feedback_calibration[0].transient_delta_upper - iVar3 < 0
        )) {
      iVar3 = f33_current_reference_feedback_calibration[0].transient_delta_upper;
    }
    f33_current_reference_feedback[0].retained_transient_delta =
         f33_current_reference_feedback_calibration[0].transient_delta_lower;
    if (iVar3 - f33_current_reference_feedback_calibration[0].transient_delta_lower < 0 ==
        (iVar3 < 0 != f33_current_reference_feedback_calibration[0].transient_delta_lower < 0 &&
        f33_current_reference_feedback_calibration[0].transient_delta_lower < 0 ==
        iVar3 - f33_current_reference_feedback_calibration[0].transient_delta_lower < 0)) {
      f33_current_reference_feedback[0].retained_transient_delta = iVar3;
    }
    iVar3 = f33_current_reference_feedback[0].retained_transient_delta + iVar5;
  }
  f33_current_reference_feedback[0].request_before_global_clamp = iVar3;
  if (f33_current_reference_feedback_calibration[0].request_upper_q15 - iVar3 < 0 !=
      (f33_current_reference_feedback_calibration[0].request_upper_q15 < 0 != iVar3 < 0 &&
      iVar3 < 0 == f33_current_reference_feedback_calibration[0].request_upper_q15 - iVar3 < 0)) {
    iVar3 = f33_current_reference_feedback_calibration[0].request_upper_q15;
  }
  f33_current_reference_feedback[0].previous_error = (short)f33_current_reference_feedback[0].error;
  iVar5 = f33_current_reference_feedback_calibration[0].request_lower_q15;
  if (iVar3 - f33_current_reference_feedback_calibration[0].request_lower_q15 < 0 ==
      (iVar3 < 0 != f33_current_reference_feedback_calibration[0].request_lower_q15 < 0 &&
      f33_current_reference_feedback_calibration[0].request_lower_q15 < 0 ==
      iVar3 - f33_current_reference_feedback_calibration[0].request_lower_q15 < 0)) {
    iVar5 = iVar3;
  }
  f33_current_reference_feedback[0].request = (short)(iVar5 / 0x8000);
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_364dc(void)

{
  return;
}



/* Clear output, previous error, current error, gains, raw/clamped correction fields and opaque
   reset-only word. Retain measured ratio and padding; do not clear the separate387CE staged
   snapshot. */

void f33_reset_bank1_current_reference_feedback(void)

{
  f33_current_reference_feedback[1].request = 0;
  f33_current_reference_feedback[1].error = 0;
  f33_current_reference_feedback[1].previous_error = 0;
  f33_current_reference_feedback[1].opaque_14 = 0;
  f33_current_reference_feedback[1].request_before_global_clamp = 0;
  f33_current_reference_feedback[1].current_gain = 0;
  f33_current_reference_feedback[1].previous_gain = 0;
  f33_current_reference_feedback[1].retained_transient_delta = 0;
  f33_current_reference_feedback[1].saturated_base_plus_delta = 0;
  return;
}



/* Mode-entry initializer forwards to bank1 feedback reset; no enable test or acquisition. */

void f33_initialize_bank1_current_reference_feedback(void)

{
  f33_reset_bank1_current_reference_feedback();
  return;
}



/* WARNING: Removing unreachable block (ram,0x0003666c) */
/* WARNING: Removing unreachable block (ram,0x000365da) */
/* WARNING: Removing unreachable block (ram,0x000365d6) */
/* WARNING: Removing unreachable block (ram,0x000365ca) */
/* WARNING: Removing unreachable block (ram,0x00036590) */
/* Use prior unclipped second-axis regulator output: saturating signed16 absolute magnitude*1024
   divided by min(bank envelope,shared6CE4). Zero denominator selects1024; ratio clamps0..1024.
   Error922-ratio clamps-1024..1024 and halves toward zero when71EC&3. Gains6144/-1228,
   or30720/-6144 for transient5A; exact optional gain-scaling flag0. Correction is
   low32(gain0*error-gain1*previous_error), added to prior6DCA*32768 with symmetric signed32
   saturation. Transient path then clamps the relative delta to +/-41943040 and re-adds baseline
   without another saturation. Global bounds[-726474424,0], division toward zero by32768 and
   signed16 publication follow. Normal mode retains old transient delta. Native scheduled
   composition checks independent histories and zero-denominator behavior. */

void f33_update_bank1_current_reference_feedback(void)

{
  short sVar1;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  short sVar2;
  
  iVar5 = (int)f33_shared_second_axis_envelope;
  iVar6 = (int)f33_regulator_output_envelopes[1].second_upper;
  iVar3 = f33_regulator_output_envelopes[1].second_unclipped;
  if (f33_regulator_output_envelopes[1].second_unclipped + -0x7fff < 0 ==
      (f33_regulator_output_envelopes[1].second_unclipped < 0 &&
      -1 < f33_regulator_output_envelopes[1].second_unclipped + -0x7fff)) {
    iVar3 = 0x7fff;
  }
  if (iVar3 + 0x7fff < 0 != (-1 < iVar3 && iVar3 + 0x7fff < 0)) {
    iVar3 = -0x7fff;
  }
  iVar4 = (int)(short)iVar3;
  iVar7 = iVar6;
  if (((f33_current_reference_feedback_calibration[1].bypass_shared_ceiling == '\0') &&
      (f33_current_reference_feedback_calibration[1].shared_ceiling_enabled != '\0')) &&
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
    iVar4 = (int)f33_current_reference_feedback_calibration[1].ratio_upper;
  }
  else {
    iVar4 = iVar4 << 10;
    if (iVar7 != 0) {
      if (iVar4 == -0x80000000 && iVar7 == -1) {
        iVar4 = -0x80000000;
      }
      else {
        iVar4 = iVar4 / iVar7;
      }
    }
  }
  iVar3 = (int)f33_current_reference_feedback_calibration[1].ratio_upper;
  if (iVar3 - iVar4 < 0 != (iVar3 < 0 != iVar4 < 0 && iVar4 < 0 == iVar3 - iVar4 < 0)) {
    iVar4 = iVar3;
  }
  if (iVar4 < 0) {
    iVar4 = 0;
  }
  f33_current_reference_feedback[1].ratio = (short)iVar4;
  iVar5 = (int)f33_current_reference_feedback_calibration[1].ratio_target - (int)(short)iVar4;
  if (iVar3 - iVar5 < 0 != (iVar3 < 0 != iVar5 < 0 && iVar5 < 0 == iVar3 - iVar5 < 0)) {
    iVar5 = iVar3;
  }
  f33_current_reference_feedback[1].error =
       (int)f33_current_reference_feedback_calibration[1].error_lower;
  if (iVar5 - f33_current_reference_feedback[1].error < 0 ==
      (iVar5 < 0 != f33_current_reference_feedback[1].error < 0 &&
      f33_current_reference_feedback[1].error < 0 ==
      iVar5 - f33_current_reference_feedback[1].error < 0)) {
    f33_current_reference_feedback[1].error = iVar5;
  }
  if ((DAT_febe71ec & 3) != 0) {
    f33_current_reference_feedback[1].error = f33_current_reference_feedback[1].error / 2;
  }
  sVar1 = f33_current_reference_feedback_calibration[1].normal_current_gain;
  sVar2 = f33_current_reference_feedback_calibration[1].normal_previous_gain;
  if (f33_current_reference_transient.active == 'Z') {
    sVar1 = f33_current_reference_feedback_calibration[1].transient_current_gain;
    sVar2 = f33_current_reference_feedback_calibration[1].transient_previous_gain;
  }
  f33_current_reference_feedback[1].previous_gain = (int)sVar2;
  f33_current_reference_feedback[1].current_gain = (int)sVar1;
  if (f33_current_reference_feedback_calibration[1].error_gain_scaling_enabled == 'Z') {
    iVar3 = f33_current_reference_feedback_calibration[1].nonpositive_error_gain_scale;
    if (0 < f33_current_reference_feedback[1].error) {
      iVar3 = f33_current_reference_feedback_calibration[1].positive_error_gain_scale;
    }
    iVar3 = (f33_current_reference_feedback[1].error * iVar3) / 0x1000;
    f33_current_reference_feedback[1].current_gain =
         (f33_current_reference_feedback[1].current_gain * iVar3) / 0x1000;
    f33_current_reference_feedback[1].previous_gain =
         (f33_current_reference_feedback[1].previous_gain * iVar3) / 0x1000;
  }
  iVar6 = (int)f33_first_current_feedback_baseline;
  iVar5 = iVar6 * 0x8000;
  iVar3 = f33_current_reference_feedback[1].current_gain * f33_current_reference_feedback[1].error -
          f33_current_reference_feedback[1].previous_gain *
          f33_current_reference_feedback[1].previous_error;
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
  f33_current_reference_feedback[1].saturated_base_plus_delta = iVar3;
  if (f33_current_reference_transient.active == 'Z') {
    iVar3 = iVar3 + iVar6 * -0x8000;
    if (f33_current_reference_feedback_calibration[1].transient_delta_upper - iVar3 < 0 !=
        (f33_current_reference_feedback_calibration[1].transient_delta_upper < 0 != iVar3 < 0 &&
        iVar3 < 0 == f33_current_reference_feedback_calibration[1].transient_delta_upper - iVar3 < 0
        )) {
      iVar3 = f33_current_reference_feedback_calibration[1].transient_delta_upper;
    }
    f33_current_reference_feedback[1].retained_transient_delta =
         f33_current_reference_feedback_calibration[1].transient_delta_lower;
    if (iVar3 - f33_current_reference_feedback_calibration[1].transient_delta_lower < 0 ==
        (iVar3 < 0 != f33_current_reference_feedback_calibration[1].transient_delta_lower < 0 &&
        f33_current_reference_feedback_calibration[1].transient_delta_lower < 0 ==
        iVar3 - f33_current_reference_feedback_calibration[1].transient_delta_lower < 0)) {
      f33_current_reference_feedback[1].retained_transient_delta = iVar3;
    }
    iVar3 = f33_current_reference_feedback[1].retained_transient_delta + iVar5;
  }
  f33_current_reference_feedback[1].request_before_global_clamp = iVar3;
  if (f33_current_reference_feedback_calibration[1].request_upper_q15 - iVar3 < 0 !=
      (f33_current_reference_feedback_calibration[1].request_upper_q15 < 0 != iVar3 < 0 &&
      iVar3 < 0 == f33_current_reference_feedback_calibration[1].request_upper_q15 - iVar3 < 0)) {
    iVar3 = f33_current_reference_feedback_calibration[1].request_upper_q15;
  }
  f33_current_reference_feedback[1].previous_error = (short)f33_current_reference_feedback[1].error;
  iVar5 = f33_current_reference_feedback_calibration[1].request_lower_q15;
  if (iVar3 - f33_current_reference_feedback_calibration[1].request_lower_q15 < 0 ==
      (iVar3 < 0 != f33_current_reference_feedback_calibration[1].request_lower_q15 < 0 &&
      f33_current_reference_feedback_calibration[1].request_lower_q15 < 0 ==
      iVar3 - f33_current_reference_feedback_calibration[1].request_lower_q15 < 0)) {
    iVar5 = iVar3;
  }
  f33_current_reference_feedback[1].request = (short)(iVar5 / 0x8000);
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_36674(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_36676(void)

{
  return;
}



/* WARNING: Removing unreachable block (ram,0x00036742) */
/* WARNING: Removing unreachable block (ram,0x000366c6) */
/* WARNING: Removing unreachable block (ram,0x000366a6) */
/* Only8A14==1 recomputes32-bit6B98; otherwise retain it. Exact calibrated7DB2 base curve collapses
   to100. WhenEAC6<512, abs(7EA8)>683 reduces the base toward0 at3413, and above3413 selects0. Scale
   by6BE4/1024. No recovered physical units; native composition exercises retained amplitude, not
   this entire recomputation surface. Native nonzero tail from5E280 and full
   staging-only5E202(2,0101) verify scoped transform, retention and arbitration effects. No fresh
   acquisition, upstream nonzero regulation or physical PWM claim. */

void f33_refresh_phase_compensation_amplitude(void)

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
  uVar6 = (uint)DAT_febe7ea8;
  if ((int)(uVar6 + 0x7fff) < 0 == (-1 < (int)uVar6 && (int)(uVar6 + 0x7fff) < 0) &&
      uVar6 != 0xffff8001) {
    if ((int)uVar6 < 0) {
      uVar6 = (uint)-DAT_febe7ea8;
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
          iVar2 = iVar2 / iVar1;
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



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_3674c(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_3674e(void)

{
  return;
}



/* Retain raw regulated triplet in6BB4/B8/BC. Reference6E58/5A/5C selects signed compensation
   bounded by +/-6B98, linear within +/-96. Always calculate6BA8/AC/B0; modeA5 suppresses ADDITION,
   not calculation. Publish adjusted32-bit triplet6B9C/BA0/BA4. Native nonzero tail from5E280 and
   full staging-only5E202(2,0101) verify scoped transform, retention and arbitration effects. No
   fresh acquisition, upstream nonzero regulation or physical PWM claim. */

void f33_compensate_first_regulated_phases(void)

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
        DAT_febe6ba8 = DAT_febe6ba8 / iVar4;
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
        DAT_febe6bac = DAT_febe6bac / iVar4;
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
        DAT_febe6bb0 = DAT_febe6bb0 / iVar4;
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



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_367fa(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_367fc(void)

{
  return;
}



/* Second bank: reference6E60/62/64 and regulated6E70/72/74; raw backup6BD8/DC/E0, computed
   deltas6BCC/D0/D4, adjusted6BC0/C4/C8. ModeA5 retains raw output despite nonzero computed deltas.
   Signed divisions truncate toward zero. Native nonzero tail from5E280 and full
   staging-only5E202(2,0101) verify scoped transform, retention and arbitration effects. No fresh
   acquisition, upstream nonzero regulation or physical PWM claim. */

void f33_compensate_second_regulated_phases(void)

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
        DAT_febe6bcc = DAT_febe6bcc / iVar4;
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
        DAT_febe6bd0 = DAT_febe6bd0 / iVar4;
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
        DAT_febe6bd4 = DAT_febe6bd4 / iVar4;
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



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_368a8(void)

{
  return;
}



/* Single constant publisher: DAT_febe6be4 = 0; Shape-classified from the canonical corpus; the
   target cell is not yet named, so the written state's meaning is unknown. */

void FUN_000368aa(void)

{
  DAT_febe6be4 = 0;
  return;
}



/* WARNING: Removing unreachable block (ram,0x000368fa) */
/* Use saturating absolute signed16 command6E0A to interpolate unsigned ordinates of2BD10
   with16-count spacing; index>=127 returns1024. Publish6BE4. Table x words and finalFFFFFFFF row
   are not read by this consumer. Native nonzero tail from5E280 and full staging-only5E202(2,0101)
   verify scoped transform, retention and arbitration effects. No fresh acquisition, upstream
   nonzero regulation or physical PWM claim. */

void f33_map_phase_compensation_gain(void)

{
  uint uVar1;
  uint uVar2;
  
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
  uVar2 = (uVar1 & 0xffff) >> 4;
  if (uVar2 < 0x7f) {
    DAT_febe6be4 = f33_phase_compensation_gain_curve[uVar2].y +
                   (short)((int)((uVar1 & 0xf) *
                                ((uint)f33_phase_compensation_gain_curve[uVar2 + 1].y -
                                (uint)f33_phase_compensation_gain_curve[uVar2].y)) / 0x10);
  }
  else {
    DAT_febe6be4 = 0x400;
  }
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_3690e(void)

{
  return;
}



/* WARNING: Removing unreachable block (ram,0x0003694e) */
/* WARNING: Removing unreachable block (ram,0x00036932) */

void FUN_00036910(void)

{
  f33_regulator_output_envelopes[0].second_saturation = '\0';
  f33_regulator_output_envelopes[0].first_saturation = '\0';
  f33_regulator_output_envelopes[0].first = 0;
  f33_regulator_output_envelopes[0].second = 0;
  f33_regulator_output_envelopes[0].first_unclipped = 0;
  f33_regulator_output_envelopes[0].second_unclipped = 0;
  f33_regulator_output_envelopes[0].raw_cubic = f33_regulator_output_envelope_calibrations[0].base;
  f33_regulator_output_envelopes[0].selected_second_limit =
       (short)(f33_regulator_output_envelope_calibrations[0].base / 0x800);
  f33_regulator_output_envelopes[0].second_upper =
       f33_regulator_output_envelopes[0].selected_second_limit;
  f33_regulator_output_envelopes[0].combined_second = 0;
  f33_regulator_output_envelopes[0].reset_cleared_status = '\0';
  f33_regulator_output_envelopes[0].lower_before_clamp =
       f33_regulator_output_envelope_calibrations[0].base -
       f33_regulator_output_envelope_calibrations[0].band_width;
  f33_regulator_output_envelopes[0].retained_24 = 0x400;
  f33_regulator_output_envelopes[0].retained_28 = 0x400;
  f33_regulator_output_envelopes[0].second_lower =
       (short)((f33_regulator_output_envelope_calibrations[0].base -
               f33_regulator_output_envelope_calibrations[0].band_width) / 0x800);
  return;
}



/* WARNING: Removing unreachable block (ram,0x0003699c) */
/* WARNING: Removing unreachable block (ram,0x0003698c) */
/* WARNING: Removing unreachable block (ram,0x000369a6) */
/* Bank0 cubic in saturating abs16 of clamped first-axis output. Leading coefficient is signed
   BYTEF5=-11 (SLD.B), not halfword245. Sequential truncation:
   ((-1135+((127+(-11*x)/128)*x)/1024)/4)*x; symmetric32 saturated add to17365676. No physical unit
   inferred. */

int f33_regulator_output_envelope_cubic_bank0(void)

{
  int iVar1;
  int iVar2;
  
  iVar2 = (int)f33_regulator_output_envelopes[0].first;
  if (iVar2 + 0x7fff < 0 == (-1 < iVar2 && iVar2 + 0x7fff < 0) && iVar2 != -0x7fff) {
    if (iVar2 < 0) {
      iVar2 = (int)-f33_regulator_output_envelopes[0].first;
    }
  }
  else {
    iVar2 = 0x7fff;
  }
  iVar2 = (((int)f33_regulator_output_envelope_calibrations[0].linear_coefficient +
           (((int)f33_regulator_output_envelope_calibrations[0].quadratic_coefficient +
            ((int)(short)iVar2 *
            (int)(short)f33_regulator_output_envelope_calibrations[0].cubic_coefficient) / 0x80) *
           iVar2) / 0x400) / 4) * iVar2;
  if (iVar2 < 1) {
    if ((f33_regulator_output_envelope_calibrations[0].base < 1) &&
       (iVar1 = -0x7fffffff - iVar2,
       iVar1 - f33_regulator_output_envelope_calibrations[0].base < 0 ==
       (iVar1 < 0 != f33_regulator_output_envelope_calibrations[0].base < 0 &&
       f33_regulator_output_envelope_calibrations[0].base < 0 ==
       iVar1 - f33_regulator_output_envelope_calibrations[0].base < 0) &&
       iVar1 != f33_regulator_output_envelope_calibrations[0].base)) {
      return -0x7fffffff;
    }
  }
  else if ((0 < f33_regulator_output_envelope_calibrations[0].base) &&
          (iVar1 = (0x7fffffff - iVar2) - f33_regulator_output_envelope_calibrations[0].base,
          iVar1 < 0 !=
          (0x7fffffff - iVar2 < 0 != f33_regulator_output_envelope_calibrations[0].base < 0 &&
          f33_regulator_output_envelope_calibrations[0].base < 0 == iVar1 < 0))) {
    return 0x7fffffff;
  }
  return f33_regulator_output_envelope_calibrations[0].base + iVar2;
}



/* WARNING: Removing unreachable block (ram,0x00036bb2) */
/* WARNING: Removing unreachable block (ram,0x00036bae) */
/* WARNING: Removing unreachable block (ram,0x00036b4e) */
/* WARNING: Removing unreachable block (ram,0x00036af8) */
/* WARNING: Removing unreachable block (ram,0x00036af0) */
/* WARNING: Removing unreachable block (ram,0x00036a9c) */
/* WARNING: Removing unreachable block (ram,0x00036a64) */
/* WARNING: Removing unreachable block (ram,0x00036a36) */
/* WARNING: Removing unreachable block (ram,0x00036a6a) */
/* WARNING: Removing unreachable block (ram,0x00036a18) */
/* Bank0: reset on8BAE nonzero or8B28&40004. Healthy71EC low bits0 uses wrapping32
   common+differential then signed/2; any invalid bit uses common terms directly. Clamp own signed
   scale6CF0 to700..1707; truncate/256, symmetric32 multiply, truncate/2048. First axis
   clamps+/-7658 with equality saturation. Second limit uses signed-byte cubic and209715-wide band,
   retaining prior output magnitude inside new band; current magnitude below lower edge selects
   lower edge. Publish separate unclipped values, band and saturation directions. Not physical PWM
   delivery. */

void f33_compose_regulator_output_bank0(void)

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
  if ((DAT_febe8bae != '\0') || ((f33_output_request_status & 0x40004) != 0)) {
    f33_regulator_output_envelopes[0].selected_second_limit =
         (short)(f33_regulator_output_envelope_calibrations[0].base / 0x800);
    f33_regulator_output_envelopes[0].second_saturation = '\0';
    f33_regulator_output_envelopes[0].first_saturation = '\0';
    f33_regulator_output_envelopes[0].reset_cleared_status = '\0';
    f33_regulator_output_envelopes[0].first = 0;
    f33_regulator_output_envelopes[0].second = 0;
    f33_regulator_output_envelopes[0].second_lower =
         (short)((f33_regulator_output_envelope_calibrations[0].base -
                 f33_regulator_output_envelope_calibrations[0].band_width) / 0x800);
    f33_regulator_output_envelopes[0].second_upper =
         f33_regulator_output_envelopes[0].selected_second_limit;
    f33_regulator_output_envelopes[0].first_unclipped = 0;
    f33_regulator_output_envelopes[0].second_unclipped = 0;
    f33_regulator_output_envelopes[0].raw_cubic = f33_regulator_output_envelope_calibrations[0].base
    ;
    f33_regulator_output_envelopes[0].lower_before_clamp =
         f33_regulator_output_envelope_calibrations[0].base -
         f33_regulator_output_envelope_calibrations[0].band_width;
    f33_regulator_output_envelopes[0].combined_second = 0;
    f33_regulator_output_envelopes[0].retained_24 = 0x400;
    f33_regulator_output_envelopes[0].retained_28 = 0x400;
    return;
  }
  iVar10 = DAT_febe6c8c;
  f33_regulator_output_envelopes[0].combined_second = DAT_febe6ccc;
  if ((DAT_febe71ec & 3) == 0) {
    iVar10 = (DAT_febe6c78 + DAT_febe6c8c) / 2;
    f33_regulator_output_envelopes[0].combined_second = (DAT_febe6ca0 + DAT_febe6ccc) / 2;
  }
  uVar5 = (uint)f33_regulator_output_envelope_calibrations[0].scale_lower;
  iVar8 = f33_regulator_output_envelope_calibrations[0].scale_upper - DAT_febe6cf0;
  uVar7 = DAT_febe6cf0;
  if (iVar8 < 0 != ((int)DAT_febe6cf0 < 0 && (int)DAT_febe6cf0 < 0 == iVar8 < 0)) {
    uVar7 = (uint)f33_regulator_output_envelope_calibrations[0].scale_upper;
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
       (uVar7 = iVar10 * uVar5, 0x7fffffff < uVar7)) {
      uVar7 = 0x7fffffff;
    }
  }
LAB_00036aec:
  f33_regulator_output_envelopes[0].first_unclipped = (int)uVar7 / 0x800;
  iVar10 = f33_regulator_output_envelopes[0].combined_second / 0x100;
  if ((iVar10 == 0) || (uVar5 == 0)) {
    iVar10 = 0;
    goto LAB_00036b46;
  }
  if (iVar10 < 0) {
    if (-1 < (int)uVar5) goto LAB_00036b2a;
LAB_00036b14:
    if ((-1 < (longlong)(int)uVar5 * (longlong)iVar10 &&
         (int)((ulonglong)((longlong)(int)uVar5 * (longlong)iVar10) >> 0x20) != 0) ||
       (0x7fffffff < iVar10 * uVar5)) {
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
  iVar8 = (int)f33_regulator_output_envelope_calibrations[0].first_upper;
  iVar10 = iVar10 / 0x800;
  if (iVar8 - f33_regulator_output_envelopes[0].first_unclipped < 0 ==
      (iVar8 < 0 != f33_regulator_output_envelopes[0].first_unclipped < 0 &&
      f33_regulator_output_envelopes[0].first_unclipped < 0 ==
      iVar8 - f33_regulator_output_envelopes[0].first_unclipped < 0) &&
      iVar8 != f33_regulator_output_envelopes[0].first_unclipped) {
    f33_regulator_output_envelopes[0].first =
         (short)f33_regulator_output_envelopes[0].first_unclipped;
    iVar8 = f33_regulator_output_envelope_calibrations[0].first_lower -
            f33_regulator_output_envelopes[0].first_unclipped;
    if (iVar8 < 0 ==
        (f33_regulator_output_envelope_calibrations[0].first_lower < 0 !=
         f33_regulator_output_envelopes[0].first_unclipped < 0 &&
        f33_regulator_output_envelopes[0].first_unclipped < 0 == iVar8 < 0)) {
      f33_regulator_output_envelopes[0].first_saturation = '\x02';
      f33_regulator_output_envelopes[0].first =
           f33_regulator_output_envelope_calibrations[0].first_lower;
    }
    else {
      f33_regulator_output_envelopes[0].first_saturation = '\0';
    }
  }
  else {
    f33_regulator_output_envelopes[0].first_saturation = '\x01';
    f33_regulator_output_envelopes[0].first =
         f33_regulator_output_envelope_calibrations[0].first_upper;
  }
  f33_regulator_output_envelopes[0].second_unclipped = iVar10;
  iVar4 = f33_regulator_output_envelope_cubic_bank0();
  iVar9 = f33_regulator_output_envelope_calibrations[0].upper;
  iVar8 = f33_regulator_output_envelope_calibrations[0].lower;
  puVar11 = ((undefined *)camry_host_ptr((uint32_t)((0xffffb3e8u + (uint32_t)((int)puVar3)))));
  (*((int *)camry_host_ptr((uint32_t)((0xffffb400u + (uint32_t)((int)puVar3)))))) = iVar4;
  if (iVar9 - iVar4 < 0 != (iVar9 < 0 != iVar4 < 0 && iVar4 < 0 == iVar9 - iVar4 < 0)) {
    iVar4 = iVar9;
  }
  iVar9 = iVar8;
  if (iVar4 - iVar8 < 0 == (iVar4 < 0 != iVar8 < 0 && iVar8 < 0 == iVar4 - iVar8 < 0)) {
    iVar9 = iVar4;
  }
  iVar4 = iVar9 - f33_regulator_output_envelope_calibrations[0].band_width;
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



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_36c1a(void)

{
  return;
}



/* WARNING: Removing unreachable block (ram,0x00036c5a) */
/* WARNING: Removing unreachable block (ram,0x00036c3e) */

void FUN_00036c1c(void)

{
  f33_regulator_output_envelopes[1].second_saturation = '\0';
  f33_regulator_output_envelopes[1].first_saturation = '\0';
  f33_regulator_output_envelopes[1].first = 0;
  f33_regulator_output_envelopes[1].second = 0;
  f33_regulator_output_envelopes[1].first_unclipped = 0;
  f33_regulator_output_envelopes[1].second_unclipped = 0;
  f33_regulator_output_envelopes[1].raw_cubic = f33_regulator_output_envelope_calibrations[1].base;
  f33_regulator_output_envelopes[1].selected_second_limit =
       (short)(f33_regulator_output_envelope_calibrations[1].base / 0x800);
  f33_regulator_output_envelopes[1].second_upper =
       f33_regulator_output_envelopes[1].selected_second_limit;
  f33_regulator_output_envelopes[1].combined_second = 0;
  f33_regulator_output_envelopes[1].reset_cleared_status = '\0';
  f33_regulator_output_envelopes[1].lower_before_clamp =
       f33_regulator_output_envelope_calibrations[1].base -
       f33_regulator_output_envelope_calibrations[1].band_width;
  f33_regulator_output_envelopes[1].retained_24 = 0x400;
  f33_regulator_output_envelopes[1].retained_28 = 0x400;
  f33_regulator_output_envelopes[1].second_lower =
       (short)((f33_regulator_output_envelope_calibrations[1].base -
               f33_regulator_output_envelope_calibrations[1].band_width) / 0x800);
  return;
}



/* WARNING: Removing unreachable block (ram,0x00036ca8) */
/* WARNING: Removing unreachable block (ram,0x00036c98) */
/* WARNING: Removing unreachable block (ram,0x00036cb2) */
/* Bank1 cubic in saturating abs16 of clamped first-axis output. Leading coefficient is signed
   BYTEF5=-11 (SLD.B), not halfword245. Sequential truncation:
   ((-1135+((127+(-11*x)/128)*x)/1024)/4)*x; symmetric32 saturated add to17365676. No physical unit
   inferred. */

int f33_regulator_output_envelope_cubic_bank1(void)

{
  int iVar1;
  int iVar2;
  
  iVar2 = (int)f33_regulator_output_envelopes[1].first;
  if (iVar2 + 0x7fff < 0 == (-1 < iVar2 && iVar2 + 0x7fff < 0) && iVar2 != -0x7fff) {
    if (iVar2 < 0) {
      iVar2 = (int)-f33_regulator_output_envelopes[1].first;
    }
  }
  else {
    iVar2 = 0x7fff;
  }
  iVar2 = (((int)f33_regulator_output_envelope_calibrations[1].linear_coefficient +
           (((int)f33_regulator_output_envelope_calibrations[1].quadratic_coefficient +
            ((int)(short)iVar2 *
            (int)(short)f33_regulator_output_envelope_calibrations[1].cubic_coefficient) / 0x80) *
           iVar2) / 0x400) / 4) * iVar2;
  if (iVar2 < 1) {
    if ((f33_regulator_output_envelope_calibrations[1].base < 1) &&
       (iVar1 = -0x7fffffff - iVar2,
       iVar1 - f33_regulator_output_envelope_calibrations[1].base < 0 ==
       (iVar1 < 0 != f33_regulator_output_envelope_calibrations[1].base < 0 &&
       f33_regulator_output_envelope_calibrations[1].base < 0 ==
       iVar1 - f33_regulator_output_envelope_calibrations[1].base < 0) &&
       iVar1 != f33_regulator_output_envelope_calibrations[1].base)) {
      return -0x7fffffff;
    }
  }
  else if ((0 < f33_regulator_output_envelope_calibrations[1].base) &&
          (iVar1 = (0x7fffffff - iVar2) - f33_regulator_output_envelope_calibrations[1].base,
          iVar1 < 0 !=
          (0x7fffffff - iVar2 < 0 != f33_regulator_output_envelope_calibrations[1].base < 0 &&
          f33_regulator_output_envelope_calibrations[1].base < 0 == iVar1 < 0))) {
    return 0x7fffffff;
  }
  return f33_regulator_output_envelope_calibrations[1].base + iVar2;
}



/* WARNING: Removing unreachable block (ram,0x00036eba) */
/* WARNING: Removing unreachable block (ram,0x00036eb6) */
/* WARNING: Removing unreachable block (ram,0x00036e56) */
/* WARNING: Removing unreachable block (ram,0x00036e00) */
/* WARNING: Removing unreachable block (ram,0x00036df8) */
/* WARNING: Removing unreachable block (ram,0x00036da4) */
/* WARNING: Removing unreachable block (ram,0x00036d78) */
/* WARNING: Removing unreachable block (ram,0x00036d42) */
/* WARNING: Removing unreachable block (ram,0x00036d24) */
/* WARNING: Removing unreachable block (ram,0x00036d7c) */
/* Bank1: reset on8BAF nonzero or8B28&40004. Healthy71EC low bits0 uses wrapping32
   common-differential then signed/2; any invalid bit uses common terms directly. Clamp own signed
   scale6CF4 to700..1707; truncate/256, symmetric32 multiply, truncate/2048. First axis
   clamps+/-7658 with equality saturation. Second limit uses signed-byte cubic and209715-wide band,
   retaining prior output magnitude inside new band; current magnitude below lower edge selects
   lower edge. Publish separate unclipped values, band and saturation directions. Not physical PWM
   delivery. */

void f33_compose_regulator_output_bank1(void)

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
  if ((DAT_febe8baf != '\0') || ((f33_output_request_status & 0x40004) != 0)) {
    f33_regulator_output_envelopes[1].selected_second_limit =
         (short)(f33_regulator_output_envelope_calibrations[1].base / 0x800);
    f33_regulator_output_envelopes[1].second_saturation = '\0';
    f33_regulator_output_envelopes[1].first_saturation = '\0';
    f33_regulator_output_envelopes[1].reset_cleared_status = '\0';
    f33_regulator_output_envelopes[1].first = 0;
    f33_regulator_output_envelopes[1].second = 0;
    f33_regulator_output_envelopes[1].second_lower =
         (short)((f33_regulator_output_envelope_calibrations[1].base -
                 f33_regulator_output_envelope_calibrations[1].band_width) / 0x800);
    f33_regulator_output_envelopes[1].second_upper =
         f33_regulator_output_envelopes[1].selected_second_limit;
    f33_regulator_output_envelopes[1].first_unclipped = 0;
    f33_regulator_output_envelopes[1].second_unclipped = 0;
    f33_regulator_output_envelopes[1].raw_cubic = f33_regulator_output_envelope_calibrations[1].base
    ;
    f33_regulator_output_envelopes[1].lower_before_clamp =
         f33_regulator_output_envelope_calibrations[1].base -
         f33_regulator_output_envelope_calibrations[1].band_width;
    f33_regulator_output_envelopes[1].combined_second = 0;
    f33_regulator_output_envelopes[1].retained_24 = 0x400;
    f33_regulator_output_envelopes[1].retained_28 = 0x400;
    return;
  }
  f33_regulator_output_envelopes[1].combined_second = DAT_febe6ccc;
  iVar10 = DAT_febe6c8c;
  if ((DAT_febe71ec & 3) == 0) {
    f33_regulator_output_envelopes[1].combined_second = (DAT_febe6ccc - DAT_febe6ca0) / 2;
    iVar10 = (DAT_febe6c8c - DAT_febe6c78) / 2;
  }
  uVar5 = (uint)f33_regulator_output_envelope_calibrations[1].scale_lower;
  iVar8 = f33_regulator_output_envelope_calibrations[1].scale_upper - DAT_febe6cf4;
  uVar7 = DAT_febe6cf4;
  if (iVar8 < 0 != ((int)DAT_febe6cf4 < 0 && (int)DAT_febe6cf4 < 0 == iVar8 < 0)) {
    uVar7 = (uint)f33_regulator_output_envelope_calibrations[1].scale_upper;
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
       (uVar7 = iVar10 * uVar5, 0x7fffffff < uVar7)) {
      uVar7 = 0x7fffffff;
    }
  }
LAB_00036df4:
  f33_regulator_output_envelopes[1].first_unclipped = (int)uVar7 / 0x800;
  iVar10 = f33_regulator_output_envelopes[1].combined_second / 0x100;
  if ((iVar10 == 0) || (uVar5 == 0)) {
    iVar10 = 0;
    goto LAB_00036e4e;
  }
  if (iVar10 < 0) {
    if (-1 < (int)uVar5) goto LAB_00036e32;
LAB_00036e1c:
    if ((-1 < (longlong)(int)uVar5 * (longlong)iVar10 &&
         (int)((ulonglong)((longlong)(int)uVar5 * (longlong)iVar10) >> 0x20) != 0) ||
       (0x7fffffff < iVar10 * uVar5)) {
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
  iVar8 = (int)f33_regulator_output_envelope_calibrations[1].first_upper;
  iVar10 = iVar10 / 0x800;
  if (iVar8 - f33_regulator_output_envelopes[1].first_unclipped < 0 ==
      (iVar8 < 0 != f33_regulator_output_envelopes[1].first_unclipped < 0 &&
      f33_regulator_output_envelopes[1].first_unclipped < 0 ==
      iVar8 - f33_regulator_output_envelopes[1].first_unclipped < 0) &&
      iVar8 != f33_regulator_output_envelopes[1].first_unclipped) {
    f33_regulator_output_envelopes[1].first =
         (short)f33_regulator_output_envelopes[1].first_unclipped;
    iVar8 = f33_regulator_output_envelope_calibrations[1].first_lower -
            f33_regulator_output_envelopes[1].first_unclipped;
    if (iVar8 < 0 ==
        (f33_regulator_output_envelope_calibrations[1].first_lower < 0 !=
         f33_regulator_output_envelopes[1].first_unclipped < 0 &&
        f33_regulator_output_envelopes[1].first_unclipped < 0 == iVar8 < 0)) {
      f33_regulator_output_envelopes[1].first_saturation = '\x02';
      f33_regulator_output_envelopes[1].first =
           f33_regulator_output_envelope_calibrations[1].first_lower;
    }
    else {
      f33_regulator_output_envelopes[1].first_saturation = '\0';
    }
  }
  else {
    f33_regulator_output_envelopes[1].first_saturation = '\x01';
    f33_regulator_output_envelopes[1].first =
         f33_regulator_output_envelope_calibrations[1].first_upper;
  }
  f33_regulator_output_envelopes[1].second_unclipped = iVar10;
  iVar4 = f33_regulator_output_envelope_cubic_bank1();
  iVar9 = f33_regulator_output_envelope_calibrations[1].upper;
  iVar8 = f33_regulator_output_envelope_calibrations[1].lower;
  puVar11 = ((undefined *)camry_host_ptr((uint32_t)((0xffffb414u + (uint32_t)((int)puVar3)))));
  (*((int *)camry_host_ptr((uint32_t)((0xffffb42cu + (uint32_t)((int)puVar3)))))) = iVar4;
  if (iVar9 - iVar4 < 0 != (iVar9 < 0 != iVar4 < 0 && iVar4 < 0 == iVar9 - iVar4 < 0)) {
    iVar4 = iVar9;
  }
  iVar9 = iVar8;
  if (iVar4 - iVar8 < 0 == (iVar4 < 0 != iVar8 < 0 && iVar8 < 0 == iVar4 - iVar8 < 0)) {
    iVar9 = iVar4;
  }
  iVar4 = iVar9 - f33_regulator_output_envelope_calibrations[1].band_width;
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



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_36f22(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_36f24(void)

{
  return;
}



/* WARNING: Removing unreachable block (ram,0x000370ca) */
/* WARNING: Removing unreachable block (ram,0x000370c6) */
/* WARNING: Removing unreachable block (ram,0x000370b6) */
/* WARNING: Removing unreachable block (ram,0x000370aa) */
/* WARNING: Removing unreachable block (ram,0x00037096) */
/* WARNING: Removing unreachable block (ram,0x00036ff0) */
/* WARNING: Removing unreachable block (ram,0x00036f9e) */
/* WARNING: Removing unreachable block (ram,0x00036f94) */
/* WARNING: Removing unreachable block (ram,0x00036f8a) */
/* WARNING: Removing unreachable block (ram,0x00036f84) */
/* WARNING: Removing unreachable block (ram,0x00036f66) */
/* Retained output scaling follows a projected bank-axis product and a separate scale accumulator.
   Unconditionally load unsigned7DA6/7DA8 before admission. A zero filtered estimate selects
   target128; actual fractional recurrence still runs. Staged scale128 forwards nonzero bank axes
   without implying fresh acquisition or PWM duty. Unconditional7DA6/7DA8 loads precede scale
   admission. Zero projected estimate selects target128 while the real retained scale recurrence
   still runs; nonzero bank axes reach both regulated transforms. */

void FUN_00036f26(void)

{
  bool bVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  int iVar5;
  
  DAT_febe6c4c = DAT_000319c4;
  DAT_febe6c4e = DAT_000319c8;
  DAT_febe6c54 = (((int)((int)(int16_t)DAT_febe6e12) * (int)f33_regulator_output_envelopes[0].first +
                  (int)((int)(int16_t)DAT_febe6e14) * (int)((int)(int16_t)DAT_febe6cec)) / 0x8000) * (uint)DAT_000319c4;
  DAT_febe6c58 = (((int)((int)(int16_t)DAT_febe6e16) * (int)f33_regulator_output_envelopes[1].first +
                  (int)((int)(int16_t)DAT_febe6e18) * (int)((int)(int16_t)DAT_febe6cee)) / 0x8000) * (uint)DAT_000319c8;
  DAT_febe6c68 = (DAT_febe6c58 / 2 + DAT_febe6c54 / 2) / 0x3000;
  if ((int)DAT_febe6c68 + -0x7fff < 0 == ((int)DAT_febe6c68 < 0 && -1 < (int)DAT_febe6c68 + -0x7fff) &&
      DAT_febe6c68 != 0x7fff) {
    iVar5 = 0x7fff;
  }
  else {
    iVar5 = (int)(short)DAT_febe6c68;
    if ((int)DAT_febe6c68 + 0x7fff < 0 != (-1 < (int)DAT_febe6c68 && (int)DAT_febe6c68 + 0x7fff < 0)) {
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
  DAT_febe6c4a = (short)(DAT_febe6c6c / 0x10000);
  iVar5 = (int)((int)(int16_t)DAT_febe6c4a);
  if (DAT_00031a20 == 'Z') {
    DAT_febe6c50 = DAT_00031a24;
    if ((DAT_febe71ec & 3) == 0) {
      DAT_febe6c50 = DAT_00031a22;
    }
    iVar2 = (int)DAT_00031a26;
    if ((iVar5 - iVar2 < 0 != (iVar5 < 0 != iVar2 < 0 && iVar2 < 0 == iVar5 - iVar2 < 0) ||
         iVar5 == iVar2) &&
       (((DAT_febe6c60 + -0x80 < 0 != (DAT_febe6c60 < 0 && -1 < DAT_febe6c60 + -0x80) ||
         (((iVar3 = (int)DAT_00031a28, iVar2 = f33_current_reference_feedback[0].ratio - iVar3,
           iVar2 < 0 ==
           (f33_current_reference_feedback[0].ratio < 0 != iVar3 < 0 && iVar3 < 0 == iVar2 < 0) ||
           (iVar2 = f33_current_reference_feedback[1].ratio - iVar3,
           iVar2 < 0 ==
           (f33_current_reference_feedback[1].ratio < 0 != iVar3 < 0 && iVar3 < 0 == iVar2 < 0))) &&
          ((DAT_00031a2a <= DAT_febe7da6 || (DAT_00031a2a <= DAT_febe7da8)))))) && (iVar5 != 0)))) {
      DAT_febe6c5c = (int)DAT_febe6c50 << 7;
      bVar1 = DAT_febe6c5c < 0;
      if (iVar5 != 0) {
        if (DAT_febe6c5c == -0x80000000 && iVar5 == -1) {
          bVar1 = true;
          DAT_febe6c5c = -0x80000000;
        }
        else {
          DAT_febe6c5c = DAT_febe6c5c / iVar5;
          bVar1 = DAT_febe6c5c < 0;
        }
      }
      if (bVar1) {
        DAT_febe6c5c = -DAT_febe6c5c;
      }
      if (DAT_febe6c5c + -0x80 < 0 != (DAT_febe6c5c < 0 && -1 < DAT_febe6c5c + -0x80) ||
          DAT_febe6c5c == 0x80) goto LAB_00037068;
    }
  }
  DAT_febe6c5c = 0x80;
LAB_00037068:
  uVar4 = (uint)DAT_00031a2e;
  if (uVar4 == 0) {
    iVar5 = (int)(short)DAT_febe6c60 << 0x10;
    iVar2 = (int)(short)DAT_febe6c5c << 0x10;
  }
  else {
    iVar5 = (int)(short)DAT_febe6c60 * uVar4;
    iVar2 = (int)(short)DAT_febe6c5c * uVar4;
  }
  DAT_febe6c64 = iVar2 + (DAT_febe6c64 - iVar5);
  DAT_febe6c60 = (int)(short)(DAT_febe6c64 / 0x10000);
  DAT_febe6c42 = (short)((DAT_febe6c60 * ((int)(int16_t)DAT_febe6cec)) / 0x80);
  DAT_febe6c40 = (short)((DAT_febe6c60 * f33_regulator_output_envelopes[0].first) / 0x80);
  DAT_febe6c46 = (short)((DAT_febe6c60 * ((int)(int16_t)DAT_febe6cee)) / 0x80);
  DAT_febe6c44 = (short)((DAT_febe6c60 * f33_regulator_output_envelopes[1].first) / 0x80);
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_370d4(void)

{
  return;
}



/* Constant-block fill: 5 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_370d6(void)

{
  DAT_febe6c70 = 0;
  DAT_febe6c72 = 0;
  DAT_febe6c74 = 0;
  DAT_febe6c76 = 0;
  DAT_febe6c78 = 0;
  return;
}



/* WARNING: Removing unreachable block (ram,0x000371b2) */
/* Differential first-axis regulator: error=sat(6D82-6D74), accumulator6C78. Prior output-direction
   flags gate integration; both nonzero selected slot indices or8B28&40004 reset state. Additional
   accumulator clamp uses ROM31A3C. Selected slot indices are not physical-disable booleans.
   Differential first-axis recurrence follows common update, reverses bank1 saturation-direction
   interpretation, retains raw-error proportional term and applies extra ROM accumulator bound. */

void FUN_000370e6(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  uint uVar5;
  int iVar6;
  uint uVar7;
  
  if (((DAT_febe8bae != '\0') && (DAT_febe8baf != '\0')) ||
     ((f33_output_request_status & 0x40004) != 0)) {
    DAT_febe6c70 = 0;
    DAT_febe6c72 = 0;
    DAT_febe6c74 = 0;
    DAT_febe6c76 = 0;
    DAT_febe6c78 = 0;
    return;
  }
  iVar3 = (int)((int)(int16_t)DAT_febe6d82) - (int)((int)(int16_t)DAT_febe6d74);
  if (iVar3 + 0x7fff < 0 == (-1 < iVar3 && iVar3 + 0x7fff < 0) && iVar3 != -0x7fff) {
    if (iVar3 + -0x7fff < 0 == (iVar3 < 0 && -1 < iVar3 + -0x7fff) && iVar3 != 0x7fff) {
      iVar6 = 0x7fff;
    }
    else {
      iVar6 = -0x8000;
      if (iVar3 + 0x8000 < 0 == (-1 < iVar3 && iVar3 + 0x8000 < 0)) {
        iVar6 = (int)(short)iVar3;
      }
    }
  }
  else {
    iVar6 = -0x7fff;
  }
  if ((((f33_regulator_output_envelopes[0].first_saturation == '\x01') ||
       (f33_regulator_output_envelopes[1].first_saturation == '\x02')) && (-1 < iVar6)) ||
     (((f33_regulator_output_envelopes[0].first_saturation == '\x02' ||
       (f33_regulator_output_envelopes[1].first_saturation == '\x01')) && (iVar6 < 0)))) {
    DAT_febe6c70 = 1;
    iVar3 = 0;
  }
  else {
    DAT_febe6c70 = 0;
    iVar3 = iVar6;
  }
  uVar4 = (uint)DAT_00031a30;
  if (DAT_febe6d16 <= uVar4) {
    uVar4 = (uint)DAT_febe6d16;
  }
  uVar5 = (uint)DAT_00031a32;
  if (uVar5 <= uVar4) {
    uVar5 = uVar4;
  }
  uVar4 = DAT_00031a34;
  if (DAT_febe6d58 <= DAT_00031a34) {
    uVar4 = DAT_febe6d58;
  }
  uVar7 = DAT_00031a38;
  if (DAT_00031a38 <= uVar4) {
    uVar7 = uVar4;
  }
  iVar1 = uVar5 * (iVar6 - ((int)(int16_t)DAT_febe6c72)) + (int)((uVar7 >> 9) * (((int)(int16_t)DAT_febe6c74) + iVar3)) / 0x40;
  if (iVar1 < 1) {
    if ((DAT_febe6c78 < 1) &&
       (iVar2 = -0x7fffffff - iVar1,
       iVar2 - DAT_febe6c78 < 0 ==
       (iVar2 < 0 != DAT_febe6c78 < 0 && DAT_febe6c78 < 0 == iVar2 - DAT_febe6c78 < 0) &&
       iVar2 != DAT_febe6c78)) {
      iVar1 = -0x7fffffff;
      goto LAB_000371f4;
    }
  }
  else if ((0 < DAT_febe6c78) &&
          (iVar2 = (0x7fffffff - iVar1) - DAT_febe6c78,
          iVar2 < 0 != (0x7fffffff - iVar1 < 0 != (int)DAT_febe6c78 < 0 && (int)DAT_febe6c78 < 0 == iVar2 < 0)
          )) {
    iVar1 = 0x7fffffff;
    goto LAB_000371f4;
  }
  iVar1 = iVar1 + DAT_febe6c78;
LAB_000371f4:
  iVar2 = DAT_00031a3c;
  if (iVar1 - DAT_00031a3c < 0 !=
      (iVar1 < 0 != DAT_00031a3c < 0 && DAT_00031a3c < 0 == iVar1 - DAT_00031a3c < 0) ||
      iVar1 == DAT_00031a3c) {
    iVar2 = iVar1;
  }
  DAT_febe6c78 = -DAT_00031a3c;
  if (iVar2 + DAT_00031a3c < 0 ==
      (iVar2 < 0 != DAT_febe6c78 < 0 && DAT_febe6c78 < 0 == iVar2 + DAT_00031a3c < 0)) {
    DAT_febe6c78 = iVar2;
  }
  DAT_febe6c72 = (short)iVar6;
  DAT_febe6c74 = (short)iVar3;
  DAT_febe6c76 = (short)iVar6;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_37216(void)

{
  return;
}



/* Constant-block fill: 5 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_37218(void)

{
  DAT_febe6c7c = 0;
  DAT_febe6c7e = 0;
  DAT_febe6c80 = 0;
  DAT_febe6c82 = 0;
  DAT_febe6c8c = 0;
  return;
}



/* WARNING: Removing unreachable block (ram,0x0003737e) */
/* WARNING: Removing unreachable block (ram,0x00037366) */
/* Common first-axis regulator: error=sat(6D80-6D70), accumulator6C8C. Prior saturation gates
   integration, not proportional error difference. First-invalid correction requires ENTIRE
   previous6C84==0: bit0 selects(common-old differential)/2 before bit1's plus case. Symmetric
   saturation precedes division. Publish corrected6C88, then update before370E6; the reset branch
   does not clear6C84/6C88. Prior saturation gates integration but not proportional error
   difference. First-invalid correction requires whole previous mask0 and uses old differential
   before its update. Reset preserves6C84/6C88. */

void FUN_00037228(void)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  uint uVar9;
  
  if (((DAT_febe8bae != '\0') && (DAT_febe8baf != '\0')) ||
     ((f33_output_request_status & 0x40004) != 0)) {
    DAT_febe6c7c = 0;
    DAT_febe6c7e = 0;
    DAT_febe6c80 = 0;
    DAT_febe6c82 = 0;
    DAT_febe6c8c = 0;
    return;
  }
  iVar7 = (int)((int)(int16_t)DAT_febe6d80) - (int)((int)(int16_t)DAT_febe6d70);
  if (iVar7 + 0x7fff < 0 == (-1 < iVar7 && iVar7 + 0x7fff < 0) && iVar7 != -0x7fff) {
    if (iVar7 + -0x7fff < 0 == (iVar7 < 0 && -1 < iVar7 + -0x7fff) && iVar7 != 0x7fff) {
      iVar8 = 0x7fff;
    }
    else {
      iVar8 = -0x8000;
      if (iVar7 + 0x8000 < 0 == (-1 < iVar7 && iVar7 + 0x8000 < 0)) {
        iVar8 = (int)(short)iVar7;
      }
    }
  }
  else {
    iVar8 = -0x7fff;
  }
  if ((((f33_regulator_output_envelopes[0].first_saturation == '\x01') ||
       (f33_regulator_output_envelopes[1].first_saturation == '\x01')) && (-1 < iVar8)) ||
     (((f33_regulator_output_envelopes[0].first_saturation == '\x02' ||
       (f33_regulator_output_envelopes[1].first_saturation == '\x02')) && (iVar8 < 0)))) {
    DAT_febe6c7c = 1;
    iVar7 = 0;
  }
  else {
    DAT_febe6c7c = 0;
    iVar7 = iVar8;
  }
  uVar2 = (uint)DAT_00031a40;
  if (DAT_febe6d06 <= uVar2) {
    uVar2 = (uint)DAT_febe6d06;
  }
  uVar3 = (uint)DAT_00031a42;
  if (uVar3 <= uVar2) {
    uVar3 = uVar2;
  }
  uVar2 = DAT_00031a44;
  if (DAT_febe6d40 <= DAT_00031a44) {
    uVar2 = DAT_febe6d40;
  }
  uVar9 = DAT_00031a48;
  if (DAT_00031a48 <= uVar2) {
    uVar9 = uVar2;
  }
  iVar6 = 0x7fffffff;
  iVar5 = -0x7fffffff;
  iVar4 = iVar6;
  if (((DAT_febe71ec & 1) == 0) || (DAT_febe6c84 != 0)) {
    if (((DAT_febe71ec >> 1 & 1) != 0) && (DAT_febe6c84 == 0)) {
      if (DAT_febe6c8c < 1) {
        if ((0 < DAT_febe6c78) ||
           (iVar1 = -0x7fffffff - DAT_febe6c8c, iVar4 = iVar5,
           iVar1 - DAT_febe6c78 < 0 !=
           (iVar1 < 0 != DAT_febe6c78 < 0 && DAT_febe6c78 < 0 == iVar1 - DAT_febe6c78 < 0) ||
           iVar1 == DAT_febe6c78)) goto LAB_00037360;
      }
      else if ((DAT_febe6c78 < 1) ||
              (iVar1 = (0x7fffffff - DAT_febe6c8c) - DAT_febe6c78,
              iVar1 < 0 ==
              (0x7fffffff - (int)DAT_febe6c8c < 0 != (int)DAT_febe6c78 < 0 && (int)DAT_febe6c78 < 0 == iVar1 < 0)))
      {
LAB_00037360:
        iVar4 = DAT_febe6c78 + DAT_febe6c8c;
      }
      goto LAB_00037364;
    }
  }
  else {
    if (DAT_febe6c8c < 0) {
      if ((DAT_febe6c78 < 0) ||
         (iVar1 = (DAT_febe6c8c + 0x7fffffff) - DAT_febe6c78, iVar4 = iVar5,
         iVar1 < 0 ==
         ((int)DAT_febe6c8c + 0x7fffffff < 0 != (int)DAT_febe6c78 < 0 && (int)DAT_febe6c78 < 0 == iVar1 < 0)))
      goto LAB_0003732e;
    }
    else if ((-1 < DAT_febe6c78) ||
            (iVar1 = -(0x7fffffff - DAT_febe6c8c),
            iVar1 - DAT_febe6c78 < 0 !=
            (iVar1 < 0 != DAT_febe6c78 < 0 && DAT_febe6c78 < 0 == iVar1 - DAT_febe6c78 < 0) ||
            iVar1 == DAT_febe6c78)) {
LAB_0003732e:
      iVar4 = DAT_febe6c8c - DAT_febe6c78;
    }
LAB_00037364:
    DAT_febe6c8c = iVar4 / 2;
  }
  iVar4 = uVar3 * (iVar8 - ((int)(int16_t)DAT_febe6c7e)) + (int)((uVar9 >> 9) * (((int)(int16_t)DAT_febe6c80) + iVar7)) / 0x40;
  if (iVar4 < 1) {
    if ((DAT_febe6c8c < 1) &&
       (iVar1 = -0x7fffffff - iVar4, iVar6 = iVar5,
       iVar1 - DAT_febe6c8c < 0 ==
       (iVar1 < 0 != DAT_febe6c8c < 0 && DAT_febe6c8c < 0 == iVar1 - DAT_febe6c8c < 0) &&
       iVar1 != DAT_febe6c8c)) goto LAB_000373b0;
  }
  else if ((0 < DAT_febe6c8c) &&
          (iVar5 = (0x7fffffff - iVar4) - DAT_febe6c8c,
          iVar5 < 0 != (0x7fffffff - iVar4 < 0 != (int)DAT_febe6c8c < 0 && (int)DAT_febe6c8c < 0 == iVar5 < 0)
          )) goto LAB_000373b0;
  iVar6 = iVar4 + DAT_febe6c8c;
LAB_000373b0:
  DAT_febe6c88 = DAT_febe6c8c;
  DAT_febe6c84 = DAT_febe71ec;
  DAT_febe6c82 = (short)iVar8;
  DAT_febe6c80 = (short)iVar7;
  DAT_febe6c8c = iVar6;
  DAT_febe6c7e = DAT_febe6c82;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_373bc(void)

{
  return;
}



/* Constant-block fill: 13 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_373be(void)

{
  DAT_febe6c90 = 0;
  DAT_febe6c92 = 0;
  DAT_febe6c94 = 0;
  DAT_febe6c9c = DAT_febe6d14;
  DAT_febe6c96 = 0;
  DAT_febe6ca0 = 0;
  DAT_febe6cb4 = 0;
  DAT_febe6c98 = 0;
  DAT_febe6c9a = 0;
  DAT_febe6ca8 = 0;
  DAT_febe6cb0 = 0;
  DAT_febe6cac = 0;
  DAT_febe6ca4 = DAT_febe6d54;
  return;
}



int FUN_000373e6(void)

{
  int iVar1;
  int iVar2;
  
  iVar1 = (int)DAT_febe6d7e - (int)DAT_febe6d76;
  if (iVar1 + 0x7fff < 0 == (-1 < iVar1 && iVar1 + 0x7fff < 0) && iVar1 != -0x7fff) {
    if (iVar1 + -0x7fff < 0 == (iVar1 < 0 && -1 < iVar1 + -0x7fff) && iVar1 != 0x7fff) {
      iVar2 = 0x7fff;
    }
    else {
      iVar2 = -0x8000;
      if (iVar1 + 0x8000 < 0 == (-1 < iVar1 && iVar1 + 0x8000 < 0)) {
        iVar2 = (int)(short)iVar1;
      }
    }
    return iVar2;
  }
  return -0x7fff;
}



uint FUN_00037418(short param_1)

{
  uint uVar1;
  
  if ((((f33_regulator_output_envelopes[0].second < 0) ||
       (f33_regulator_output_envelopes[0].second_saturation != '\x01')) &&
      ((-1 < f33_regulator_output_envelopes[1].second ||
       (f33_regulator_output_envelopes[1].second_saturation != '\x02')))) || (param_1 < 0)) {
    if (((f33_regulator_output_envelopes[0].second < 0) &&
        (f33_regulator_output_envelopes[0].second_saturation == '\x02')) ||
       ((-1 < f33_regulator_output_envelopes[1].second &&
        (f33_regulator_output_envelopes[1].second_saturation == '\x01')))) {
      uVar1 = (uint)(int)param_1 >> 0x1f;
    }
    else {
      uVar1 = 0;
    }
  }
  else {
    uVar1 = 1;
  }
  DAT_febe6c90 = (char)uVar1;
  return uVar1;
}



/* WARNING: Removing unreachable block (ram,0x000374d0) */

void FUN_00037460(short param_1,char param_2)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  int iVar4;
  int iVar5;
  uint uVar6;
  
  DAT_febe6ca4 = DAT_febe6d54;
  DAT_febe6c9c = DAT_febe6d14;
  uVar2 = (uint)DAT_00031a4c;
  iVar5 = (int)param_1;
  if (param_2 == '\x01') {
    iVar5 = 0;
  }
  if (DAT_febe6d14 < uVar2) {
    uVar2 = (uint)DAT_febe6d14;
  }
  uVar3 = (uint)DAT_00031a4e;
  if (uVar3 <= uVar2) {
    uVar3 = uVar2;
  }
  uVar2 = DAT_00031a50;
  if (DAT_febe6d54 < DAT_00031a50) {
    uVar2 = DAT_febe6d54;
  }
  uVar6 = DAT_00031a54;
  if (DAT_00031a54 <= uVar2) {
    uVar6 = uVar2;
  }
  iVar4 = DAT_00031a58;
  if (DAT_febe6ca0 - DAT_00031a58 < 0 !=
      (DAT_febe6ca0 < 0 != DAT_00031a58 < 0 && DAT_00031a58 < 0 == DAT_febe6ca0 - DAT_00031a58 < 0))
  {
    iVar4 = DAT_febe6ca0;
  }
  DAT_febe6ca0 = -DAT_00031a58;
  DAT_febe6ca8 = DAT_febe6ca0;
  if (iVar4 + DAT_00031a58 < 0 ==
      (iVar4 < 0 != DAT_febe6ca0 < 0 && DAT_febe6ca0 < 0 == iVar4 + DAT_00031a58 < 0)) {
    DAT_febe6ca8 = iVar4;
  }
  DAT_febe6cac = (uVar6 >> 9) * (((int)(int16_t)DAT_febe6c94) + iVar5);
  DAT_febe6cb0 = uVar3 * ((int)param_1 - (int)((int)(int16_t)DAT_febe6c92));
  iVar4 = DAT_febe6cac / 0x40 + DAT_febe6cb0;
  if (iVar4 < 1) {
    if ((DAT_febe6ca8 < 1) &&
       (iVar1 = -0x7fffffff - iVar4,
       iVar1 - DAT_febe6ca8 < 0 ==
       (iVar1 < 0 != DAT_febe6ca8 < 0 && DAT_febe6ca8 < 0 == iVar1 - DAT_febe6ca8 < 0) &&
       iVar1 != DAT_febe6ca8)) {
      DAT_febe6cb4 = -0x7fffffff;
      goto LAB_00037512;
    }
  }
  else if ((0 < DAT_febe6ca8) &&
          (iVar1 = (0x7fffffff - iVar4) - DAT_febe6ca8,
          iVar1 < 0 != (0x7fffffff - iVar4 < 0 != (int)DAT_febe6ca8 < 0 && (int)DAT_febe6ca8 < 0 == iVar1 < 0)
          )) {
    DAT_febe6cb4 = 0x7fffffff;
    goto LAB_00037512;
  }
  DAT_febe6cb4 = DAT_febe6ca8 + iVar4;
LAB_00037512:
  DAT_febe6c98 = ((int)(int16_t)DAT_febe6c92);
  iVar4 = DAT_00031a58;
  if (DAT_febe6cb4 - DAT_00031a58 < 0 !=
      (DAT_febe6cb4 < 0 != DAT_00031a58 < 0 && DAT_00031a58 < 0 == DAT_febe6cb4 - DAT_00031a58 < 0))
  {
    iVar4 = DAT_febe6cb4;
  }
  DAT_febe6c9a = ((int)(int16_t)DAT_febe6c94);
  DAT_febe6c92 = param_1;
  if (iVar4 + DAT_00031a58 < 0 ==
      (iVar4 < 0 != DAT_febe6ca0 < 0 && DAT_febe6ca0 < 0 == iVar4 + DAT_00031a58 < 0)) {
    DAT_febe6ca0 = iVar4;
  }
  DAT_febe6c94 = (short)iVar5;
  DAT_febe6c96 = param_1;
  return;
}



/* Differential second-axis regulator aggregate373E6/37418/37460: error=sat(6D7E-6D76),
   accumulator6CA0, directional anti-windup and additional clamp31A58. Reset follows selected
   arbitration indices and acquisition status, not a generic diagnostic inhibit. */

void FUN_00037538(void)

{
  undefined4 uVar1;
  undefined4 uVar2;
  
  if (((DAT_febe8bae == '\0') || (DAT_febe8baf == '\0')) &&
     ((f33_output_request_status & 0x40004) == 0)) {
    uVar1 = FUN_000373e6();
    uVar2 = FUN_00037418(uVar1);
    FUN_00037460(uVar1,uVar2);
  }
  else {
    DAT_febe6c90 = 0;
    DAT_febe6c92 = 0;
    DAT_febe6c94 = 0;
    DAT_febe6c9c = DAT_febe6d14;
    DAT_febe6c96 = 0;
    DAT_febe6ca0 = 0;
    DAT_febe6cb4 = 0;
    DAT_febe6c98 = 0;
    DAT_febe6c9a = 0;
    DAT_febe6ca8 = 0;
    DAT_febe6cb0 = 0;
    DAT_febe6cac = 0;
    DAT_febe6ca4 = DAT_febe6d54;
  }
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_3759a(void)

{
  return;
}



/* Constant-block fill: 12 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_3759c(void)

{
  DAT_febe6cb8 = 0;
  DAT_febe6cba = 0;
  DAT_febe6cbc = 0;
  DAT_febe6cc4 = DAT_febe6d04;
  DAT_febe6cbe = 0;
  DAT_febe6ccc = 0;
  DAT_febe6cc0 = 0;
  DAT_febe6cc2 = 0;
  DAT_febe6cd4 = 0;
  DAT_febe6cdc = 0;
  DAT_febe6cd8 = 0;
  DAT_febe6cd0 = DAT_febe6d3c;
  return;
}



int FUN_000375c2(void)

{
  int iVar1;
  
  iVar1 = DAT_febe6d7c - DAT_febe6d78;
  if (iVar1 + -0x7fff < 0 == (iVar1 < 0 && -1 < iVar1 + -0x7fff)) {
    iVar1 = 0x7fff;
  }
  if (iVar1 + 0x7fff < 0 != (-1 < iVar1 && iVar1 + 0x7fff < 0)) {
    iVar1 = -0x7fff;
  }
  return (int)(short)iVar1;
}



uint FUN_000375e6(short param_1)

{
  uint uVar1;
  
  if ((((f33_regulator_output_envelopes[0].second < 0) ||
       (f33_regulator_output_envelopes[0].second_saturation != '\x01')) &&
      ((f33_regulator_output_envelopes[1].second < 0 ||
       (f33_regulator_output_envelopes[1].second_saturation != '\x01')))) || (param_1 < 0)) {
    if (((f33_regulator_output_envelopes[0].second < 0) &&
        (f33_regulator_output_envelopes[0].second_saturation == '\x02')) ||
       ((f33_regulator_output_envelopes[1].second < 0 &&
        (f33_regulator_output_envelopes[1].second_saturation == '\x02')))) {
      uVar1 = (uint)(int)param_1 >> 0x1f;
    }
    else {
      uVar1 = 0;
    }
  }
  else {
    uVar1 = 1;
  }
  DAT_febe6cb8 = (char)uVar1;
  return uVar1;
}



/* WARNING: Removing unreachable block (ram,0x00037728) */
/* WARNING: Removing unreachable block (ram,0x0003770a) */

void FUN_0003762e(short param_1,char param_2)

{
  uint uVar1;
  uint uVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  uint uVar6;
  
  iVar5 = (int)param_1;
  if (param_2 == '\x01') {
    iVar5 = 0;
  }
  DAT_febe6cc4 = DAT_febe6d04;
  DAT_febe6cd0 = DAT_febe6d3c;
  uVar1 = (uint)DAT_00031a5c;
  if (DAT_febe6d04 < uVar1) {
    uVar1 = (uint)DAT_febe6d04;
  }
  uVar2 = (uint)DAT_00031a5e;
  if (uVar2 <= uVar1) {
    uVar2 = uVar1;
  }
  uVar1 = DAT_00031a60;
  if (DAT_febe6d3c < DAT_00031a60) {
    uVar1 = DAT_febe6d3c;
  }
  uVar6 = DAT_00031a64;
  if (DAT_00031a64 <= uVar1) {
    uVar6 = uVar1;
  }
  iVar4 = DAT_00031a68;
  if (DAT_febe6ccc - DAT_00031a68 < 0 !=
      (DAT_febe6ccc < 0 != DAT_00031a68 < 0 && DAT_00031a68 < 0 == DAT_febe6ccc - DAT_00031a68 < 0))
  {
    iVar4 = DAT_febe6ccc;
  }
  DAT_febe6ccc = -DAT_00031a68;
  DAT_febe6cc8 = DAT_febe6ccc;
  if (iVar4 + DAT_00031a68 < 0 ==
      (iVar4 < 0 != DAT_febe6ccc < 0 && DAT_febe6ccc < 0 == iVar4 + DAT_00031a68 < 0)) {
    DAT_febe6cc8 = iVar4;
  }
  iVar4 = 0x7fffffff;
  if (((DAT_febe71ec & 1) == 0) || (DAT_febe6cc6 != 0)) {
    if (((DAT_febe71ec >> 1 & 1) != 0) && (DAT_febe6cc6 == 0)) {
      if (DAT_febe6cc8 < 1) {
        if ((0 < DAT_febe6ca0) ||
           (iVar4 = -0x7fffffff - DAT_febe6cc8,
           iVar4 - DAT_febe6ca0 < 0 !=
           (iVar4 < 0 != DAT_febe6ca0 < 0 && DAT_febe6ca0 < 0 == iVar4 - DAT_febe6ca0 < 0) ||
           iVar4 == DAT_febe6ca0)) goto LAB_00037704;
        iVar4 = -0x7fffffff;
      }
      else if ((DAT_febe6ca0 < 1) ||
              (iVar3 = (0x7fffffff - DAT_febe6cc8) - DAT_febe6ca0,
              iVar3 < 0 ==
              (0x7fffffff - (int)DAT_febe6cc8 < 0 != (int)DAT_febe6ca0 < 0 && (int)DAT_febe6ca0 < 0 == iVar3 < 0)))
      {
LAB_00037704:
        iVar4 = DAT_febe6ca0 + DAT_febe6cc8;
      }
      goto LAB_00037708;
    }
  }
  else {
    if (DAT_febe6cc8 < 0) {
      if ((DAT_febe6ca0 < 0) ||
         (iVar4 = (DAT_febe6cc8 + 0x7fffffff) - DAT_febe6ca0,
         iVar4 < 0 ==
         ((int)DAT_febe6cc8 + 0x7fffffff < 0 != (int)DAT_febe6ca0 < 0 && (int)DAT_febe6ca0 < 0 == iVar4 < 0)))
      goto LAB_000376d2;
      iVar4 = -0x7fffffff;
    }
    else if ((-1 < DAT_febe6ca0) ||
            (iVar3 = -(0x7fffffff - DAT_febe6cc8),
            iVar3 - DAT_febe6ca0 < 0 !=
            (iVar3 < 0 != DAT_febe6ca0 < 0 && DAT_febe6ca0 < 0 == iVar3 - DAT_febe6ca0 < 0) ||
            iVar3 == DAT_febe6ca0)) {
LAB_000376d2:
      iVar4 = DAT_febe6cc8 - DAT_febe6ca0;
    }
LAB_00037708:
    DAT_febe6cc8 = iVar4 / 2;
  }
  DAT_febe6cd8 = (uVar6 >> 9) * (((int)(int16_t)DAT_febe6cbc) + iVar5);
  DAT_febe6cc6 = DAT_febe71ec;
  DAT_febe6cdc = uVar2 * ((int)param_1 - (int)((int)(int16_t)DAT_febe6cba));
  iVar4 = DAT_febe6cd8 / 0x40 + DAT_febe6cdc;
  if (iVar4 < 1) {
    if ((DAT_febe6cc8 < 1) &&
       (iVar3 = -0x7fffffff - iVar4,
       iVar3 - DAT_febe6cc8 < 0 ==
       (iVar3 < 0 != DAT_febe6cc8 < 0 && DAT_febe6cc8 < 0 == iVar3 - DAT_febe6cc8 < 0) &&
       iVar3 != DAT_febe6cc8)) {
      iVar4 = -0x7fffffff;
      goto LAB_0003775e;
    }
  }
  else if ((0 < DAT_febe6cc8) &&
          (iVar3 = (0x7fffffff - iVar4) - DAT_febe6cc8,
          iVar3 < 0 != (0x7fffffff - iVar4 < 0 != (int)DAT_febe6cc8 < 0 && (int)DAT_febe6cc8 < 0 == iVar3 < 0)
          )) {
    iVar4 = 0x7fffffff;
    goto LAB_0003775e;
  }
  iVar4 = DAT_febe6cc8 + iVar4;
LAB_0003775e:
  DAT_febe6cd4 = DAT_febe6cc8;
  DAT_febe6cc0 = ((int)(int16_t)DAT_febe6cba);
  iVar3 = DAT_00031a68;
  if (iVar4 - DAT_00031a68 < 0 !=
      (iVar4 < 0 != DAT_00031a68 < 0 && DAT_00031a68 < 0 == iVar4 - DAT_00031a68 < 0)) {
    iVar3 = iVar4;
  }
  DAT_febe6cc2 = ((int)(int16_t)DAT_febe6cbc);
  DAT_febe6cba = param_1;
  if (iVar3 + DAT_00031a68 < 0 ==
      (iVar3 < 0 != DAT_febe6ccc < 0 && DAT_febe6ccc < 0 == iVar3 + DAT_00031a68 < 0)) {
    DAT_febe6ccc = iVar3;
  }
  DAT_febe6cbc = (short)iVar5;
  DAT_febe6cbe = param_1;
  return;
}



/* Common second-axis regulator aggregate375C2/375E6/3762E: error uses unsaturated32-bit
   feedback6D78, not halfword6D72. Persistent accumulator6CCC, directional anti-windup and first
   channel-invalid transition adjustment; additional clamp31A68. */

void FUN_0003777e(void)

{
  undefined4 uVar1;
  undefined4 uVar2;
  
  if (((DAT_febe8bae == '\0') || (DAT_febe8baf == '\0')) &&
     ((f33_output_request_status & 0x40004) == 0)) {
    uVar1 = FUN_000375c2();
    uVar2 = FUN_000375e6(uVar1);
    FUN_0003762e(uVar1,uVar2);
  }
  else {
    DAT_febe6cb8 = 0;
    DAT_febe6cba = 0;
    DAT_febe6cbc = 0;
    DAT_febe6cc4 = DAT_febe6d04;
    DAT_febe6cbe = 0;
    DAT_febe6ccc = 0;
    DAT_febe6cc0 = 0;
    DAT_febe6cc2 = 0;
    DAT_febe6cd4 = 0;
    DAT_febe6cdc = 0;
    DAT_febe6cd8 = 0;
    DAT_febe6cd0 = DAT_febe6d3c;
  }
  return;
}



/* Set retained6CE4 to exact317AC=20480 only; no fresh input or qualification. */

void f33_initialize_shared_second_axis_envelope(void)

{
  f33_shared_second_axis_envelope = DAT_000317ac;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_377ec(void)

{
  return;
}



/* For E741=11/22 use signed-axis70208 curve selected byE5C3&1 and supplied absolute magnitude;
   otherwise choose configured default. Publish6CE2.37840 supplies the saturated absolute E744 in
   actualR6. */

void f33_map_additional_second_axis_envelope(short magnitude)

{
  uint32_t puVar1;
  undefined2 uStack_6;
  
  puVar1 = 0xfebeb800u;
  if ((DAT_febee741 == '\x11') || (DAT_febee741 == '\"')) {
    puVar1 = 0xfebeb800u;
    FUN_00070208(((short *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x31eacu + (uint32_t)(DAT_febee5c3 & 1) * 4u))))))), (int)magnitude, &uStack_6);
  }
  else {
    uStack_6 = (*((undefined2 *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x31ea4u + (uint32_t)(DAT_febee5c3 & 1) * 4u)))) + 2))));
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb4e2u + (uint32_t)((int)puVar1)))))) = uStack_6;
  return;
}



/* Only8A20==1 refreshes. Saturate s32 E744 to +/-32767, take abs, store6CE0 and pass actualR6
   to377EE. Choose mapped6CE2 only when qualifier6EA8=5A, otherwise20480; lower-bound by selected
   signed calibration and publish6CE4. Closed gate retains all state; paired first-axis feedback
   consumes this prior envelope. */

void f33_refresh_shared_second_axis_envelope(void)

{
  short sVar1;
  byte bVar2;
  short sVar3;
  int iVar4;
  uint32_t puVar5;
  int iVar6;
  
  puVar5 = 0xfebeb800u;
  if (DAT_febe8a20 == '\x01') {
    if (DAT_febee744 + -0x7fff < 0 == (DAT_febee744 < 0 && -1 < DAT_febee744 + -0x7fff) &&
        DAT_febee744 != 0x7fff) {
      DAT_febe6ce0 = 0x7fff;
    }
    else {
      iVar4 = DAT_febee744;
      if (DAT_febee744 + 0x7fff < 0 != (-1 < DAT_febee744 && DAT_febee744 + 0x7fff < 0)) {
        iVar4 = -0x7fff;
      }
      DAT_febe6ce0 = (short)iVar4;
      iVar4 = (int)DAT_febe6ce0;
      if (iVar4 + 0x7fff < 0 == (-1 < iVar4 && iVar4 + 0x7fff < 0) && iVar4 != -0x7fff) {
        if (DAT_febe6ce0 < 0) {
          DAT_febe6ce0 = -DAT_febe6ce0;
        }
      }
      else {
        DAT_febe6ce0 = 0x7fff;
      }
    }
    f33_map_additional_second_axis_envelope(DAT_febe6ce0);
    sVar1 = DAT_000317ac;
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb6a8u + (uint32_t)((int)puVar5) * 1u)))) == 'Z') {
      sVar1 = (*((short *)camry_host_ptr((uint32_t)((0xffffb4e2u + (uint32_t)((int)puVar5))))));
    }
    iVar4 = (int)sVar1;
    bVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(0x2dc3)))));
    (*((int *)camry_host_ptr((uint32_t)((0xffffb4e8u + (uint32_t)((int)puVar5)))))) = iVar4;
    sVar3 = (*((short *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x31ea4u + (uint32_t)(bVar2 & 1) * 4u)))))));
    iVar6 = (int)sVar3;
    if (iVar4 - iVar6 < 0 == (iVar4 < 0 != iVar6 < 0 && iVar6 < 0 == iVar4 - iVar6 < 0) &&
        iVar4 != iVar6) {
      sVar3 = sVar1;
    }
    (*((short *)camry_host_ptr((uint32_t)((0xffffb4e4u + (uint32_t)((int)puVar5)))))) = sVar3;
  }
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_378d0(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_378d2(void)

{
  return;
}



/* Copy regulated second-axis bank outputs6BEE/6C1A to6CEC/6CEE, clamping symmetrically to6CE4 only
   for6EA8=5A. This later output-envelope use is separate from the denominator choice in3636A/36502.
    */

void f33_apply_shared_second_axis_envelope(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = (int)f33_shared_second_axis_envelope;
  iVar2 = (int)f33_regulator_output_envelopes[0].second;
  DAT_febe6cec = f33_regulator_output_envelopes[0].second;
  if (((f33_additional_current_envelope_qualified == 'Z') &&
      (DAT_febe6cec = f33_shared_second_axis_envelope,
      iVar2 - iVar3 < 0 != (iVar2 < 0 != iVar3 < 0 && iVar3 < 0 == iVar2 - iVar3 < 0))) &&
     (iVar1 = -iVar3, DAT_febe6cec = f33_regulator_output_envelopes[0].second,
     iVar2 + iVar3 < 0 != (iVar2 < 0 != iVar1 < 0 && iVar1 < 0 == iVar2 + iVar3 < 0) ||
     iVar2 == iVar1)) {
    DAT_febe6cec = (short)iVar1;
  }
  iVar2 = (int)f33_regulator_output_envelopes[1].second;
  DAT_febe6cee = f33_regulator_output_envelopes[1].second;
  if (((f33_additional_current_envelope_qualified == 'Z') &&
      (DAT_febe6cee = f33_shared_second_axis_envelope,
      iVar2 - iVar3 < 0 != (iVar2 < 0 != iVar3 < 0 && iVar3 < 0 == iVar2 - iVar3 < 0))) &&
     (iVar1 = -iVar3, DAT_febe6cee = f33_regulator_output_envelopes[1].second,
     iVar2 + iVar3 < 0 != (iVar2 < 0 != iVar1 < 0 && iVar1 < 0 == iVar2 + iVar3 < 0) ||
     iVar2 == iVar1)) {
    DAT_febe6cee = (short)iVar1;
  }
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_3791e(void)

{
  return;
}



/* Single constant publisher: DAT_febe6cf0 = 0x400; Shape-classified from the canonical corpus; the
   target cell is not yet named, so the written state's meaning is unknown. */

void FUN_00037920(void)

{
  DAT_febe6cf0 = 0x400;
  return;
}



void FUN_0003792a(void)

{
  int iVar1;
  uint uVar2;
  
  uVar2 = (uint)DAT_febe7da6;
  DAT_febe6cf0 = 0x400;
  if (uVar2 != 0) {
    iVar1 = (DAT_00031a6e - uVar2) * (uint)DAT_00031a6c;
    if (uVar2 != 0) {
      if (iVar1 == -0x80000000 && uVar2 == 0xffffffff) {
        iVar1 = -0x80000000;
      }
      else {
        iVar1 = iVar1 / (int)uVar2;
      }
    }
    DAT_febe6cf0 = iVar1 + 0x400;
  }
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_37954(void)

{
  return;
}



/* Single constant publisher: DAT_febe6cf4 = 0x400; Shape-classified from the canonical corpus; the
   target cell is not yet named, so the written state's meaning is unknown. */

void FUN_00037956(void)

{
  DAT_febe6cf4 = 0x400;
  return;
}



void FUN_00037960(void)

{
  int iVar1;
  uint uVar2;
  
  uVar2 = (uint)DAT_febe7da8;
  DAT_febe6cf4 = 0x400;
  if (uVar2 != 0) {
    iVar1 = (DAT_00031a72 - uVar2) * (uint)DAT_00031a70;
    if (uVar2 != 0) {
      if (iVar1 == -0x80000000 && uVar2 == 0xffffffff) {
        iVar1 = -0x80000000;
      }
      else {
        iVar1 = iVar1 / (int)uVar2;
      }
    }
    DAT_febe6cf4 = iVar1 + 0x400;
  }
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_3798a(void)

{
  return;
}



void FUN_0003798c(void)

{
  DAT_febe6cfa = 0;
  DAT_febe6cf8 = 0;
  DAT_febe6d08 = DAT_00031a78;
  DAT_febe6d34 = (uint)DAT_00031a78 << 0x10;
  DAT_febe6d00 = DAT_00031a7a;
  DAT_febe6d2c = (uint)DAT_00031a7a << 0x10;
  DAT_febe6d0a = DAT_00031a80;
  DAT_febe6d38 = (uint)DAT_00031a80 << 0x10;
  DAT_febe6d02 = DAT_00031a82;
  DAT_febe6d30 = (uint)DAT_00031a82 << 0x10;
  DAT_febe6d18 = DAT_00031a7c;
  DAT_febe6d4c = (uint)DAT_00031a7c << 0x10;
  DAT_febe6d10 = DAT_00031a7e;
  DAT_febe6d44 = (uint)DAT_00031a7e << 0x10;
  DAT_febe6d1a = DAT_00031a84;
  DAT_febe6d50 = (uint)DAT_00031a84 << 0x10;
  DAT_febe6d12 = DAT_00031a86;
  DAT_febe6d48 = (uint)DAT_00031a86 << 0x10;
  return;
}



undefined4 FUN_000379fc(void)

{
  if (((uint)((int)DAT_febe6e12 * (int)DAT_febe6e12 + (int)DAT_febe6e14 * (int)DAT_febe6e14) <
       DAT_00031ae0) &&
     ((uint)((int)DAT_febe6e16 * (int)DAT_febe6e16 + (int)DAT_febe6e18 * (int)DAT_febe6e18) <
      DAT_00031ae0)) {
    if ((DAT_febe6cf8 != 0) && (DAT_febe6cf8 < DAT_00031a9a)) goto LAB_00037a50;
    if ((DAT_febe7826 != 'Z') && (DAT_febe7936 != 'Z')) {
      DAT_febe6cf8 = 0;
      return 0;
    }
  }
  if (DAT_00031a9a <= DAT_febe6cf8) {
    return 0x5a;
  }
LAB_00037a50:
  DAT_febe6cf8 = DAT_febe6cf8 + 2;
  return 0x5a;
}



undefined4 FUN_00037a62(void)

{
  if (DAT_febee5c0 == '\0') {
    DAT_febe6cfa = 0;
    return 0;
  }
  if (DAT_febe6cfa < DAT_00031a98) {
    DAT_febe6cfa = DAT_febe6cfa + 2;
    return 0x5a;
  }
  return 0;
}



void FUN_00037a92(void)

{
  ushort uVar1;
  ushort uVar5;
  int iVar6;
  int iVar7;
  uint uVar8;
  uint32_t puVar9;
  int iVar10;
  undefined2 uVar11;
  undefined2 uVar12;
  undefined2 uVar13;
  undefined2 uVar14;
  int iVar15;
  uint uVar16;
  uint uVar17;
  uint uVar18;
  undefined2 *puVar19;
  ushort uVar2;
  ushort uVar3;
  ushort uVar4;
  
  uVar5 = DAT_febe71ec;
  puVar9 = 0xfebeb800u;
  if (DAT_febe8a14 != '\x01') {
    return;
  }
  DAT_febe6d20 = DAT_00031a78;
  DAT_febe6d1c = DAT_00031a7a;
  DAT_febe6d22 = DAT_00031a80;
  DAT_febe6d1e = DAT_00031a82;
  iVar6 = (int)DAT_febe5f36;
  if (iVar6 + 0x7fff < 0 == (-1 < iVar6 && iVar6 + 0x7fff < 0) && iVar6 != -0x7fff) {
    if (iVar6 < 0) {
      iVar6 = (int)-DAT_febe5f36;
    }
  }
  else {
    iVar6 = 0x7fff;
  }
  iVar10 = DAT_00031a76 - iVar6;
  uVar1 = DAT_00031a8c;
  uVar2 = DAT_00031a96;
  uVar3 = DAT_00031a94;
  uVar4 = DAT_00031a8e;
  if (iVar10 < 0 == (DAT_00031a76 < 0 != iVar6 < 0 && iVar6 < 0 == iVar10 < 0)) {
    uVar1 = DAT_00031a7c;
    uVar2 = DAT_00031a86;
    uVar3 = DAT_00031a84;
    uVar4 = DAT_00031a7e;
  }
  iVar6 = (uint)DAT_00031abc * 4;
  iVar10 = (uint)DAT_00031abe * 4;
  if (iVar6 - 1U < 0xffff) {
    iVar15 = (uint)DAT_febe6d18 * iVar6;
    iVar7 = (uint)uVar1 * iVar6;
  }
  else {
    iVar15 = (uint)DAT_febe6d18 << 0x10;
    iVar7 = (uint)uVar1 << 0x10;
  }
  DAT_febe6d4c = iVar7 + (DAT_febe6d4c - iVar15);
  DAT_febe6d18 = (ushort)((uint)DAT_febe6d4c >> 0x10);
  if (iVar10 - 1U < 0xffff) {
    iVar15 = (uint)DAT_febe6d10 * iVar10;
    iVar7 = (uint)uVar4 * iVar10;
  }
  else {
    iVar15 = (uint)DAT_febe6d10 << 0x10;
    iVar7 = (uint)uVar4 << 0x10;
  }
  DAT_febe6d44 = iVar7 + (DAT_febe6d44 - iVar15);
  DAT_febe6d10 = (ushort)((uint)DAT_febe6d44 >> 0x10);
  if (iVar6 - 1U < 0xffff) {
    iVar15 = (uint)DAT_febe6d1a * iVar6;
    iVar6 = (uint)uVar3 * iVar6;
  }
  else {
    iVar15 = (uint)DAT_febe6d1a << 0x10;
    iVar6 = (uint)uVar3 << 0x10;
  }
  DAT_febe6d50 = iVar6 + (DAT_febe6d50 - iVar15);
  DAT_febe6d1a = (ushort)((uint)DAT_febe6d50 >> 0x10);
  if (iVar10 - 1U < 0xffff) {
    iVar6 = (uint)DAT_febe6d12 * iVar10;
    iVar10 = (uint)uVar2 * iVar10;
  }
  else {
    iVar6 = (uint)DAT_febe6d12 << 0x10;
    iVar10 = (uint)uVar2 << 0x10;
  }
  DAT_febe6d48 = iVar10 + (DAT_febe6d48 - iVar6);
  DAT_febe6d12 = (ushort)((uint)DAT_febe6d48 >> 0x10);
  DAT_febe6d24 = DAT_febe6d10;
  DAT_febe6d26 = DAT_febe6d12;
  DAT_febe6d28 = DAT_febe6d18;
  DAT_febe6d2a = DAT_febe6d1a;
  iVar6 = FUN_000379fc();
  iVar10 = FUN_00037a62();
  if ((uVar5 & 3) == 0) {
    if (iVar6 == 0x5a) {
      puVar19 = ((undefined *)camry_host_ptr(0x31aacu));
    }
    else {
      if (iVar10 != 0x5a) {
        uVar14 = (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb520u + (uint32_t)((int)puVar9))))));
        uVar8 = (uint)(*((ushort *)camry_host_ptr((uint32_t)((0xffffb51cu + (uint32_t)((int)puVar9))))));
        uVar13 = (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb522u + (uint32_t)((int)puVar9))))));
        uVar18 = (uint)(*((ushort *)camry_host_ptr((uint32_t)((0xffffb51eu + (uint32_t)((int)puVar9))))));
        uVar12 = (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb528u + (uint32_t)((int)puVar9))))));
        uVar17 = (uint)(*((ushort *)camry_host_ptr((uint32_t)((0xffffb524u + (uint32_t)((int)puVar9))))));
        uVar11 = (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb52au + (uint32_t)((int)puVar9))))));
        uVar16 = (uint)(*((ushort *)camry_host_ptr((uint32_t)((0xffffb526u + (uint32_t)((int)puVar9))))));
        goto LAB_00037c18;
      }
      puVar19 = ((undefined *)camry_host_ptr(0x31a9cu));
    }
    uVar14 = *puVar19;
    uVar8 = (uint)(ushort)puVar19[1];
    uVar13 = puVar19[4];
    uVar18 = (uint)(ushort)puVar19[5];
    uVar12 = puVar19[2];
    uVar17 = (uint)(ushort)puVar19[3];
    uVar11 = puVar19[6];
    uVar16 = (uint)(ushort)puVar19[7];
  }
  else {
    uVar12 = 0;
    uVar11 = 0;
    uVar8 = (uint)DAT_00031ac2;
    uVar17 = 0;
    uVar16 = 0;
    uVar18 = (uint)DAT_00031ac6;
    uVar14 = DAT_00031ac0;
    uVar13 = DAT_00031ac4;
  }
LAB_00037c18:
  (*((short *)camry_host_ptr((uint32_t)((0xffffb4fcu + (uint32_t)((int)puVar9)))))) = (short)uVar8;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb4feu + (uint32_t)((int)puVar9)))))) = (short)uVar18;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb50cu + (uint32_t)((int)puVar9)))))) = (short)uVar17;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb50eu + (uint32_t)((int)puVar9)))))) = (short)uVar16;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb504u + (uint32_t)((int)puVar9)))))) = uVar14;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb506u + (uint32_t)((int)puVar9)))))) = uVar13;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb514u + (uint32_t)((int)puVar9)))))) = uVar12;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb516u + (uint32_t)((int)puVar9)))))) = uVar11;
  (*((uint *)camry_host_ptr((uint32_t)((0xffffb53cu + (uint32_t)((int)puVar9)))))) = uVar8 * 0x69;
  (*((uint *)camry_host_ptr((uint32_t)((0xffffb540u + (uint32_t)((int)puVar9)))))) = uVar18 * 0x69;
  (*((uint *)camry_host_ptr((uint32_t)((0xffffb554u + (uint32_t)((int)puVar9)))))) = uVar17 * 0x69;
  (*((uint *)camry_host_ptr((uint32_t)((0xffffb558u + (uint32_t)((int)puVar9)))))) = uVar16 * 0x69;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_37c48(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_37c4a(void)

{
  return;
}



/* WARNING: Removing unreachable block (ram,0x00037d9c) */
/* WARNING: Removing unreachable block (ram,0x00037d66) */
/* WARNING: Removing unreachable block (ram,0x00037ca0) */
/* WARNING: Removing unreachable block (ram,0x00037cd4) */
/* Square signed16 axis pairs6C40/42 and6C44/46 into unsigned32 energies6D64/68. Curve input is
   low16(energy>>12), with32-count interpolation and fixed endpoint beyond index126. Selector6D6C
   swaps upper/lower offset maps between banks. Each8B88/89==5A overrides energy with mode0 and
   offset6144. Otherwise energy<6166256 gives0, <54546923 gives5A, elseA5. These are software
   modulation classes, not physical bridge states. Native nonzero tail from5E280 and full
   staging-only5E202(2,0101) verify scoped transform, retention and arbitration effects. No fresh
   acquisition, upstream nonzero regulation or physical PWM claim. */

void f33_select_phase_modulation_modes(void)

{
  uint uVar1;
  uint uVar2;
  
  DAT_febe6d64 = (int)((int)(int16_t)DAT_febe6c40) * (int)((int)(int16_t)DAT_febe6c40) + (int)((int)(int16_t)DAT_febe6c42) * (int)((int)(int16_t)DAT_febe6c42);
  uVar1 = DAT_febe6d64 >> 0xc;
  uVar2 = (uVar1 & 0xffff) >> 5;
  if (f33_phase_offset_selector == 'Z') {
    if (uVar2 < 0x7f) {
      DAT_febe6d5e = (short)((int)((uVar1 & 0x1f) *
                                  ((uint)f33_phase_upper_modulation_offset_curve[uVar2 + 1].y -
                                  (uint)f33_phase_upper_modulation_offset_curve[uVar2].y)) / 0x20) +
                     f33_phase_upper_modulation_offset_curve[uVar2].y;
    }
    else {
      DAT_febe6d5e = 0x2366;
    }
  }
  else if (uVar2 < 0x7f) {
    DAT_febe6d5e = f33_phase_lower_modulation_offset_curve[uVar2].y +
                   (short)((int)((uVar1 & 0x1f) *
                                ((uint)f33_phase_lower_modulation_offset_curve[uVar2 + 1].y -
                                (uint)f33_phase_lower_modulation_offset_curve[uVar2].y)) / 0x20);
  }
  else {
    DAT_febe6d5e = 0xc9a;
  }
  if (DAT_febe8b88 == 'Z') {
    DAT_febe6d5c = 0;
    DAT_febe6d5e = f33_phase_forced_offset;
  }
  else if (DAT_febe6d64 < f33_phase_modulation_first_energy_threshold) {
    DAT_febe6d5c = 0;
  }
  else {
    DAT_febe6d5c = 0x5a;
    if (f33_phase_modulation_second_energy_threshold <= DAT_febe6d64) {
      DAT_febe6d5c = 0xa5;
    }
  }
  DAT_febe6d68 = (int)((int)(int16_t)DAT_febe6c44) * (int)((int)(int16_t)DAT_febe6c44) + (int)((int)(int16_t)DAT_febe6c46) * (int)((int)(int16_t)DAT_febe6c46);
  uVar1 = DAT_febe6d68 >> 0xc;
  uVar2 = (uVar1 & 0xffff) >> 5;
  if (f33_phase_offset_selector == 'Z') {
    if (uVar2 < 0x7f) {
      DAT_febe6d60 = f33_phase_lower_modulation_offset_curve[uVar2].y +
                     (short)((int)((uVar1 & 0x1f) *
                                  ((uint)f33_phase_lower_modulation_offset_curve[uVar2 + 1].y -
                                  (uint)f33_phase_lower_modulation_offset_curve[uVar2].y)) / 0x20);
    }
    else {
      DAT_febe6d60 = 0xc9a;
    }
  }
  else if (uVar2 < 0x7f) {
    DAT_febe6d60 = f33_phase_upper_modulation_offset_curve[uVar2].y +
                   (short)((int)((uVar1 & 0x1f) *
                                ((uint)f33_phase_upper_modulation_offset_curve[uVar2 + 1].y -
                                (uint)f33_phase_upper_modulation_offset_curve[uVar2].y)) / 0x20);
  }
  else {
    DAT_febe6d60 = 0x2366;
  }
  if (DAT_febe8b89 == 'Z') {
    DAT_febe6d5d = 0;
    DAT_febe6d60 = f33_phase_forced_offset;
  }
  else if (DAT_febe6d68 < f33_phase_modulation_first_energy_threshold) {
    DAT_febe6d5d = 0;
  }
  else {
    DAT_febe6d5d = 0x5a;
    if (f33_phase_modulation_second_energy_threshold <= DAT_febe6d68) {
      DAT_febe6d5d = 0xa5;
    }
  }
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_37de2(void)

{
  return;
}



/* Set selector6D6C=5A, adjacent byte6D6D=0 and counter6D6E=0. This initializes software offset
   alternation, not a PWM period or electrical phase. */

void f33_initialize_phase_offset_selector(void)

{
  DAT_febe6d6d = 0;
  f33_phase_offset_selector_counter = 0;
  f33_phase_offset_selector = 'Z';
  return;
}



/* Increment low16 counter; entry>=125 or increment reaching125 resets counter and toggles5A toA5,
   any other selector to5A. ROM31B18 then overrides to5A for33 orA5 for22; exact value11 leaves
   alternation enabled. No physical cadence inferred. */

void f33_advance_phase_offset_selector(void)

{
  uchar uVar1;
  
  if ((f33_phase_offset_selector_period <= f33_phase_offset_selector_counter) ||
     (f33_phase_offset_selector_counter = f33_phase_offset_selector_counter + 1,
     uVar1 = f33_phase_offset_selector,
     f33_phase_offset_selector_period <= f33_phase_offset_selector_counter)) {
    f33_phase_offset_selector_counter = 0;
    uVar1 = 'Z';
    if (f33_phase_offset_selector == 'Z') {
      uVar1 = 0xa5;
    }
  }
  if (f33_phase_offset_selector_override == '3') {
    uVar1 = 'Z';
  }
  else if (f33_phase_offset_selector_override == '\"') {
    uVar1 = 0xa5;
  }
  f33_phase_offset_selector = uVar1;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_37e44(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_37e46(void)

{
  return;
}



/* Exclude bank0 for71EC.bit0 and bank1 forbit1, then form common/difference feedback. Preserve
   unsaturated32-bit second-axis sum6D78 separately from saturated6D72; the common regulator
   consumes6D78. Acquisition-status8B28&40004 takes the reset branch. Validity-masked
   common/difference feedback, including unsaturated32-bit second-axis sum6D78 and separate
   saturated mirror6D72. Reset follows8B28&40004; exact software dataflow, not acquisition validity.
    */

void f33_compose_current_feedback(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  
  if ((f33_output_request_status & 0x40004) != 0) {
    DAT_febe6d70 = 0;
    DAT_febe6d72 = 0;
    DAT_febe6d78 = 0;
    return;
  }
  iVar4 = DAT_febe6e2c;
  iVar1 = DAT_febe6e28;
  if ((DAT_febe71ec & 1) != 0) {
    iVar4 = 0;
    iVar1 = 0;
  }
  iVar2 = DAT_febe6e34;
  iVar5 = DAT_febe6e30;
  if ((DAT_febe71ec >> 1 & 1) != 0) {
    iVar2 = 0;
    iVar5 = 0;
  }
  iVar3 = iVar5 + iVar1;
  DAT_febe6d78 = iVar2 + iVar4;
  iVar1 = iVar1 - iVar5;
  iVar4 = iVar4 - iVar2;
  if (iVar3 + 0x7fff < 0 == (-1 < iVar3 && iVar3 + 0x7fff < 0) && iVar3 != -0x7fff) {
    if (iVar3 + -0x7fff < 0 == (iVar3 < 0 && -1 < iVar3 + -0x7fff) && iVar3 != 0x7fff) {
      iVar3 = 0x7fff;
    }
    DAT_febe6d70 = (undefined2)iVar3;
  }
  else {
    DAT_febe6d70 = 0x8001;
  }
  if ((int)DAT_febe6d78 + 0x7fff < 0 == (-1 < (int)DAT_febe6d78 && (int)DAT_febe6d78 + 0x7fff < 0) &&
      DAT_febe6d78 != -0x7fff) {
    iVar5 = DAT_febe6d78;
    if ((int)DAT_febe6d78 + -0x7fff < 0 == ((int)DAT_febe6d78 < 0 && -1 < (int)DAT_febe6d78 + -0x7fff) &&
        DAT_febe6d78 != 0x7fff) {
      iVar5 = 0x7fff;
    }
  }
  else {
    iVar5 = -0x7fff;
  }
  DAT_febe6d72 = (short)iVar5;
  if (iVar1 + 0x7fff < 0 == (-1 < iVar1 && iVar1 + 0x7fff < 0) && iVar1 != -0x7fff) {
    if (iVar1 + -0x7fff < 0 == (iVar1 < 0 && -1 < iVar1 + -0x7fff) && iVar1 != 0x7fff) {
      DAT_febe6d74 = 0x7fff;
    }
    else {
      DAT_febe6d74 = (undefined2)iVar1;
    }
  }
  else {
    DAT_febe6d74 = 0x8001;
  }
  if (iVar4 + 0x7fff < 0 == (-1 < iVar4 && iVar4 + 0x7fff < 0) && iVar4 != -0x7fff) {
    if (iVar4 + -0x7fff < 0 == (iVar4 < 0 && -1 < iVar4 + -0x7fff) && iVar4 != 0x7fff) {
      DAT_febe6d76 = 0x7fff;
    }
    else {
      DAT_febe6d76 = (undefined2)iVar4;
    }
  }
  else {
    DAT_febe6d76 = 0x8001;
  }
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_37f12(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_37f14(void)

{
  return;
}



/* Mirror actual main second/first commands6DD6/6DC8 to6D84/86. Add main corrections6DA8/6DA6 with
   symmetric signed16 saturation into common references6D7C/80. Differential references6D7E/82 add
   retained correction and ROM baseline without the same saturation. Feedback baseline6DCA is not
   the published first-axis command. */

void f33_publish_corrected_current_reference_pairs(void)

{
  int iVar1;
  int iVar2;
  
  DAT_febe6d84 = ((int)(int16_t)DAT_febe6dd6);
  DAT_febe6d86 = f33_actual_first_current_command;
  iVar2 = (int)((int)(int16_t)DAT_febe6da6) + (int)f33_actual_first_current_command;
  iVar1 = (int)((int)(int16_t)DAT_febe6da8) + (int)((int)(int16_t)DAT_febe6dd6);
  if (iVar2 + 0x7fff < 0 == (-1 < iVar2 && iVar2 + 0x7fff < 0) && iVar2 != -0x7fff) {
    if (iVar2 + -0x7fff < 0 == (iVar2 < 0 && -1 < iVar2 + -0x7fff) && iVar2 != 0x7fff) {
      iVar2 = 0x7fff;
    }
    DAT_febe6d80 = (undefined2)iVar2;
  }
  else {
    DAT_febe6d80 = 0x8001;
  }
  if (iVar1 + 0x7fff < 0 == (-1 < iVar1 && iVar1 + 0x7fff < 0) && iVar1 != -0x7fff) {
    if (iVar1 + -0x7fff < 0 == (iVar1 < 0 && -1 < iVar1 + -0x7fff) && iVar1 != 0x7fff) {
      DAT_febe6d7c = 0x7fff;
    }
    else {
      DAT_febe6d7c = (undefined2)iVar1;
    }
  }
  else {
    DAT_febe6d7c = 0x8001;
  }
  DAT_febe6d82 = DAT_00031b2a + ((int)(int16_t)DAT_febe6daa);
  DAT_febe6d7e = DAT_00031b28 + ((int)(int16_t)DAT_febe6dac);
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_37f8e(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_37f90(void)

{
  return;
}



/* Read signed second-axis feedback mirror6D72; double when71EC&3, clamp to +/-32767, then return
   saturated absolute magnitude. This is measured-feedback-derived map input, not the sampled torque
   command. */

uint f33_current_reference_curve_feedback_magnitude(void)

{
  int iVar1;
  uint uVar2;
  
  iVar1 = (int)DAT_febe6d72;
  if ((DAT_febe71ec & 3) != 0) {
    iVar1 = iVar1 << 1;
  }
  if (iVar1 + -0x7fff < 0 == (iVar1 < 0 && -1 < iVar1 + -0x7fff)) {
    iVar1 = 0x7fff;
  }
  if (iVar1 + 0x7fff < 0 != (-1 < iVar1 && iVar1 + 0x7fff < 0)) {
    iVar1 = -0x7fff;
  }
  uVar2 = (uint)(short)iVar1;
  if ((int)(uVar2 + 0x7fff) < 0 == (-1 < (int)uVar2 && (int)(uVar2 + 0x7fff) < 0) &&
      uVar2 != 0xffff8001) {
    if ((int)uVar2 < 0) {
      return (int)(short)-(short)iVar1;
    }
    return uVar2;
  }
  return 0x7fff;
}



/* WARNING: Removing unreachable block (ram,0x000380b2) */
/* WARNING: Removing unreachable block (ram,0x0003806a) */
/* WARNING: Removing unreachable block (ram,0x00038038) */
/* Transient5A uses unsigned-axis/signed-ordinate31B5C; ordinary mode interpolates signed2C31E
   ordinates in128-count intervals and applies floor6F7E. Halve toward zero when71EC&3. Leaving
   transient seeds Q16 accumulator from previous output and enables filtering. While active
   A=low32(A-old_output*K+raw*K),K=304; publish trunc(A/65536). Signed16(raw-old_output)<=128
   releases directly to raw, not an absolute-delta test. Accumulator/filtered candidate are updated
   before release; inactive filtering retains those fields. */

void f33_update_current_reference_curve_floor(ushort feedback_magnitude)

{
  uchar uVar1;
  short sVar2;
  ushort uVar3;
  int iVar4;
  uint32_t puVar5;
  uint uVar6;
  int iVar7;
  short sVar8;
  int iVar9;
  int iVar10;
  uchar uVar11;
  short sStack_1a;
  
  uVar3 = DAT_febe71ec;
  iVar7 = f33_current_reference_floor.accumulator_q16;
  sVar2 = f33_current_reference_floor.curve_floor;
  uVar11 = f33_current_reference_floor.filter_active;
  uVar1 = f33_current_reference_transient.active;
  puVar5 = 0xfebeb800u;
  iVar10 = (int)f33_current_reference_floor.curve_floor;
  if (f33_current_reference_transient.active == 'Z') {
    puVar5 = 0xfebeb800u;
    FUN_000702b0(f33_switched_signed_request_curve,(uint)feedback_magnitude,&sStack_1a);
  }
  else {
    uVar6 = (uint)(feedback_magnitude >> 7);
    if (uVar6 < 0xff) {
      iVar9 = (int)(short)(*(short *)(((undefined *)camry_host_ptr(0x2c31eu)) + uVar6 * 4) +
                          (short)((int)((feedback_magnitude & 0x7f) *
                                       ((int)*(short *)(((undefined *)camry_host_ptr(0x2c31eu)) + (uVar6 + 1) * 4) -
                                       (int)*(short *)(((undefined *)camry_host_ptr(0x2c31eu)) + uVar6 * 4))) / 0x80));
    }
    else {
      iVar9 = 0;
    }
    sStack_1a = (short)iVar9;
    if (f33_current_reference_floor.previous_transient == 'Z') {
      iVar7 = iVar10 << 0x10;
      uVar11 = 'Z';
    }
    iVar4 = (int)((int)(int16_t)DAT_febe6f7e);
    if (iVar4 - iVar9 < 0 == (iVar4 < 0 != iVar9 < 0 && iVar9 < 0 == iVar4 - iVar9 < 0) &&
        iVar4 != iVar9) {
      sStack_1a = ((int)(int16_t)DAT_febe6f7e);
    }
  }
  if ((uVar3 & 3) != 0) {
    sStack_1a = sStack_1a / 2;
  }
  (*((short *)camry_host_ptr((uint32_t)((0xffffb58eu + (uint32_t)((int)puVar5)))))) = sStack_1a;
  sVar8 = sStack_1a;
  if (uVar11 == 'Z') {
    uVar6 = (uint)f33_current_reference_floor_calibration.filter_coefficient;
    if (uVar6 - 1 < 0xffff) {
      iVar10 = iVar10 * uVar6;
      iVar9 = (int)sStack_1a * uVar6;
    }
    else {
      iVar10 = iVar10 << 0x10;
      iVar9 = (int)sStack_1a << 0x10;
    }
    iVar9 = iVar9 + (iVar7 - iVar10);
    (*((int *)camry_host_ptr((uint32_t)((0xffffb598u + (uint32_t)((int)puVar5)))))) = iVar9;
    iVar7 = (int)f33_current_reference_floor_calibration.release_delta_threshold;
    iVar10 = (int)(short)(sStack_1a - sVar2);
    sVar8 = (short)(iVar9 / 0x10000);
    (*((short *)camry_host_ptr((uint32_t)((0xffffb592u + (uint32_t)((int)puVar5)))))) = sVar8;
    (*((short *)camry_host_ptr((uint32_t)((0xffffb590u + (uint32_t)((int)puVar5)))))) = sStack_1a - sVar2;
    if (iVar10 - iVar7 < 0 != (iVar10 < 0 != iVar7 < 0 && iVar7 < 0 == iVar10 - iVar7 < 0) ||
        iVar10 == iVar7) {
      uVar11 = '\0';
      sVar8 = sStack_1a;
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb588u + (uint32_t)((int)puVar5) * 1u)))) = uVar1;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb589u + (uint32_t)((int)puVar5) * 1u)))) = uVar11;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb58cu + (uint32_t)((int)puVar5)))))) = sVar8;
  return;
}


