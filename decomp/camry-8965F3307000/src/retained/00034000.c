#include "common.h"

void step_mode600_stimulus_fit(void)

{
  camry_write32((camry_sp - 4u) & ~3u, camry_gpr[26]);
  camry_write32((camry_sp - 8u) & ~3u, camry_gpr[27]);
  camry_write32((camry_sp - 12u) & ~3u, camry_gpr[28]);
  camry_write32((camry_sp - 16u) & ~3u, camry_gpr[29]);
  camry_write32((camry_sp - 20u) & ~3u, camry_gpr[31]);
  camry_sp -= 52u;
  camry_gpr[3] = camry_sp;

  uint8_t *stack_record_25 = (uint8_t *)camry_host_ptr(camry_sp + 15u);
  uint uVar1;
  short sVar2;
  uint uVar3;
  int iVar4;
  uint32_t puVar5;
  uint32_t puVar8;
  int iVar9;
  int iVar10;
  int iVar11;
  int iVar12;
  uint uVar13;
  ushort uVar14;
  uint uVar15;
  uint32_t puVar6;
  uint32_t puVar7;
  uVar13 = mode600_stimulus_fit_work.signed_component_sum;
  iVar12 = mode600_stimulus_fit_work.folded_angle_sum;
  uVar14 = mode600_stimulus_fit_work.sample_count;
  puVar8 = 0xfebeb800u;
  puVar7 = 0xfebeb800u;
  puVar6 = 0xfebeb800u;
  puVar5 = (uint32_t)(0xfebeb800u);
  stack_record_25[1] = mode600_stimulus_fit_work.active;
  if ((DAT_febeeacc & 0xff00) != 0x600) {
    { if (!camry_halted) { camry_gpr[26] = camry_read32((camry_sp + 48u) & ~3u); camry_gpr[27] = camry_read32((camry_sp + 44u) & ~3u); camry_gpr[28] = camry_read32((camry_sp + 40u) & ~3u); camry_gpr[29] = camry_read32((camry_sp + 36u) & ~3u); camry_gpr[31] = camry_read32((camry_sp + 32u) & ~3u); camry_sp += 52u; camry_gpr[3] = camry_sp; } return; }
  }
  if (mode600_stimulus_fit_work.active != 'Z') {
    { if (!camry_halted) { camry_gpr[26] = camry_read32((camry_sp + 48u) & ~3u); camry_gpr[27] = camry_read32((camry_sp + 44u) & ~3u); camry_gpr[28] = camry_read32((camry_sp + 40u) & ~3u); camry_gpr[29] = camry_read32((camry_sp + 36u) & ~3u); camry_gpr[31] = camry_read32((camry_sp + 32u) & ~3u); camry_sp += 52u; camry_gpr[3] = camry_sp; } return; }
  }
  iVar9 = (int)mode600_stimulus_fit_work.positive_mean;
  iVar10 = (int)mode600_stimulus_fit_work.negative_mean;
  stack_record_25[0] = mode600_stimulus_fit_work.stimulus_valid;
  (*((int16_t *)(stack_record_25 + 9))) = mode600_stimulus_fit_work.stimulus;
  (*((int16_t *)(stack_record_25 + 3))) = mode600_stimulus_fit_work.positive_mean;
  (*((int16_t *)(stack_record_25 + 5))) = mode600_stimulus_fit_work.negative_mean;
  (*((uint16_t *)(stack_record_25 + 7))) = mode600_stimulus_fit_work.hold_count;
  uVar15 = (uint)mode600_stimulus_fit_work.sample_count;
  stack_record_25[2] = mode600_stimulus_fit_work.state;
  if ((fit_parameters.mode600_input_upper < DAT_febeeac4) ||
     (DAT_febe7db0 < fit_parameters.mode600_qualifier_lower)) goto switchD_000340ae_caseD_15;
  if (0x1f < mode600_stimulus_fit_work.state) {
    if (0x20 < mode600_stimulus_fit_work.state) {
      if (mode600_stimulus_fit_work.state != '!') {
        if (mode600_stimulus_fit_work.state < 0x23) goto switchD_000340ae_caseD_12;
        if (mode600_stimulus_fit_work.state == '#') goto switchD_000340ae_caseD_13;
        if (mode600_stimulus_fit_work.state == '$') goto switchD_000340ae_caseD_14;
        if (mode600_stimulus_fit_work.state == '&') goto switchD_000340ae_caseD_16;
        if (mode600_stimulus_fit_work.state == '1') {
          iVar4 = iVar9 - iVar10;
          if (iVar9 - iVar10 < 0) {
            iVar4 = -iVar4;
          }
          iVar11 = (int)fit_parameters.pass_difference_limit;
          if (iVar4 - iVar11 < 0 != (iVar4 < 0 != iVar11 < 0 && iVar11 < 0 == iVar4 - iVar11 < 0) ||
              iVar4 == iVar11) {
            uVar3 = 0;
            do {
              uVar1 = uVar3 + 1;
              ((int16_t *)((stack_record_25 + 13)))[uVar3] = -(short)((iVar10 + iVar9) / 2);
              uVar3 = uVar1;
            } while (uVar1 < 2);
            stage_pair_correction('\0',((int16_t *)((stack_record_25 + 13))));
            queue_pair_correction_records();
            stack_record_25[2] = 0xff;
            puVar5 = (uint32_t)((uint32_t)(puVar8));
            goto LAB_00034204;
          }
        }
        else if (mode600_stimulus_fit_work.state == 0xff) {
          if (DAT_febe68b4 == -0x5aa5a55b) {
            stack_record_25[1] = '\0';
            stack_record_25[0] = '\0';
            stack_record_25[2] = '\x10';
            puVar5 = (uint32_t)((uint32_t)(puVar7));
            submit_up_to_eight_response_bytes_or_error_34ea4(0,0);
            cancel_mode600_stimulus_fit();
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
      ((int16_t *)((stack_record_25 + 13)))[uVar15] = 0;
      uVar15 = uVar3;
    } while (uVar3 < 2);
    puVar5 = (uint32_t)((uint32_t)(puVar7));
    stage_pair_correction('\0',((int16_t *)((stack_record_25 + 13))));
    (*((int16_t *)(stack_record_25 + 9))) = -fit_parameters.stimulus;
    stack_record_25[2] = '!';
LAB_0003415e:
    (*((uint16_t *)(stack_record_25 + 7))) = 0;
    stack_record_25[0] = 'Z';
    goto LAB_000343b2;
  }
  switch(mode600_stimulus_fit_work.state) {
  case '\x10':
    (*((int16_t *)(stack_record_25 + 5))) = 0;
    (*((int16_t *)(stack_record_25 + 3))) = 0;
    uVar15 = 0;
    do {
      uVar3 = uVar15 + 1;
      ((int16_t *)((stack_record_25 + 13)))[uVar15] = 0;
      uVar15 = uVar3;
    } while (uVar3 < 2);
    puVar5 = (uint32_t)((uint32_t)(puVar7));
    stage_pair_correction('\0',((int16_t *)((stack_record_25 + 13))));
    (*((int16_t *)(stack_record_25 + 9))) = fit_parameters.stimulus;
    stack_record_25[2] = '\x11';
    goto LAB_0003415e;
  case '\x11':
switchD_000340ae_caseD_11:
    if (fit_parameters.initial_hold_calls <= mode600_stimulus_fit_work.hold_count) {
      uVar15 = 0;
      iVar12 = 0;
      stack_record_25[2] = '\"';
      puVar5 = (uint32_t)(0xfebeb800u);
      if (mode600_stimulus_fit_work.state == '\x11') {
        stack_record_25[2] = '\x12';
      }
LAB_00034204:
      uVar14 = (ushort)uVar15;
      goto LAB_000343b2;
    }
    break;
  case '\x12':
switchD_000340ae_caseD_12:
    iVar9 = (int)fit_parameters.sample_admission;
    iVar10 = (int)((int)(int16_t)DAT_febe5f36);
    if (mode600_stimulus_fit_work.state == '\x12') {
      if (iVar10 - iVar9 < 0 == (iVar10 < 0 != iVar9 < 0 && iVar9 < 0 == iVar10 - iVar9 < 0)) {
LAB_000341a0:
        uVar3 = (uint)fit_parameters.sample_count;
        if (uVar15 < uVar3) {
          uVar14 = mode600_stimulus_fit_work.sample_count + 1;
          puVar5 = (uint32_t)(0xfebeb800u);
          compute_s16_atan2_turn_angle_70be0((int)(short)(((int)(int16_t)DAT_febe6c44) + ((int)(int16_t)DAT_febe6c40)),
                       (int)(short)(((int)(int16_t)DAT_febe6c46) + ((int)(int16_t)DAT_febe6c42)),((int16_t *)((stack_record_25 + 11))));
          iVar9 = (int)(*((int16_t *)(stack_record_25 + 11)));
          if (iVar9 + -0x4000 < 0 == (iVar9 < 0 && -1 < iVar9 + -0x4000) && iVar9 != 0x4000) {
            iVar9 = iVar9 + -0x8000;
          }
          else if (iVar9 + 0x4000 < 0 != (-1 < iVar9 && iVar9 + 0x4000 < 0)) {
            iVar9 = iVar9 + 0x8000;
          }
          iVar12 = iVar12 + iVar9;
          goto LAB_000343b2;
        }
        iVar9 = mode600_stimulus_fit_work.folded_angle_sum;
        if (uVar3 != 0) {
          if (mode600_stimulus_fit_work.folded_angle_sum == -0x80000000 && uVar3 == 0xffffffff)
          {
            iVar9 = 0;
          }
          else {
            iVar9 = mode600_stimulus_fit_work.folded_angle_sum / (int)uVar3;
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
        iVar10 = (int)fit_parameters.folded_angle_limit;
        if (iVar9 - iVar10 < 0 != (iVar9 < 0 != iVar10 < 0 && iVar10 < 0 == iVar9 - iVar10 < 0) ||
            iVar9 == iVar10) {
          (*((uint16_t *)(stack_record_25 + 7))) = 0;
          uVar3 = 0;
          if (mode600_stimulus_fit_work.state == '\x12') {
            do {
              uVar1 = uVar3 + 1;
              ((int16_t *)((stack_record_25 + 13)))[uVar3] = -sVar2;
              uVar3 = uVar1;
            } while (uVar1 < 2);
            (*((int16_t *)(stack_record_25 + 3))) = sVar2;
            stage_pair_correction('\0',((int16_t *)((stack_record_25 + 13))));
            stack_record_25[2] = '\x13';
            puVar5 = (uint32_t)((uint32_t)(puVar7));
          }
          else {
            do {
              uVar1 = uVar3 + 1;
              ((int16_t *)((stack_record_25 + 13)))[uVar3] = -sVar2;
              uVar3 = uVar1;
            } while (uVar1 < 2);
            (*((int16_t *)(stack_record_25 + 5))) = sVar2;
            stage_pair_correction('\0',((int16_t *)((stack_record_25 + 13))));
            stack_record_25[2] = '#';
            puVar5 = (uint32_t)((uint32_t)(puVar6));
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
    puVar5 = (uint32_t)(0xfebeb800u);
    camry_gpr[26] = (uint32_t)iVar12;
  camry_gpr[27] = uVar13;
  camry_gpr[28] = uVar14;
  camry_gpr[29] = 0x30ed8u;
  camry_gpr[1] = camry_sp + 0x12u;
  camry_gpr[30] = camry_sp;
  camry_write32(camry_sp, camry_gpr[1]);
  camry_gpr[6] = camry_sp + 0x10u;
  camry_gpr[1] += 2u;
  camry_r7 = camry_gpr[7] = camry_sp + 0xfu;
  camry_write32(camry_sp + 4u, camry_gpr[1]);
  camry_gpr[8] = camry_sp + 0x18u;
  camry_gpr[1] = camry_sp + 0x11u;
  camry_gpr[9] = camry_sp + 0x16u;
  camry_write32(camry_sp + 8u, camry_gpr[1]);
  camry_gpr[31] = 0x343b2u;
  abort_mode600_stimulus_fit
              (((uint8_t *)((stack_record_25 + 1))),((uint8_t *)(stack_record_25)),((int16_t *)((stack_record_25 + 9))),((uint16_t *)((stack_record_25 + 7))),((int16_t *)((stack_record_25 + 3))),((int16_t *)((stack_record_25 + 5))),((uint8_t *)((stack_record_25 + 2))));
    goto LAB_000343b2;
  case '\x13':
switchD_000340ae_caseD_13:
    if (fit_parameters.recheck_hold_calls <= mode600_stimulus_fit_work.hold_count) {
      uVar13 = 0;
      stack_record_25[2] = '$';
      uVar15 = uVar13;
      puVar5 = (uint32_t)(0xfebeb800u);
      if (mode600_stimulus_fit_work.state == '\x13') {
        stack_record_25[2] = '\x14';
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
    iVar10 = (int)fit_parameters.sample_admission;
    if (iVar9 - iVar10 < 0 == (iVar9 < 0 != iVar10 < 0 && iVar10 < 0 == iVar9 - iVar10 < 0)) {
      if (uVar15 < fit_parameters.sample_count) {
        uVar14 = mode600_stimulus_fit_work.sample_count + 1;
        uVar13 = mode600_stimulus_fit_work.signed_component_sum +
                 (int)((int)(int16_t)DAT_febe6c44) + (int)((int)(int16_t)DAT_febe6c40);
        goto LAB_000343b2;
      }
      if (mode600_stimulus_fit_work.signed_component_sum + 0x7fffffff < 0 ==
          (-1 < mode600_stimulus_fit_work.signed_component_sum &&
          mode600_stimulus_fit_work.signed_component_sum + 0x7fffffff < 0) &&
          mode600_stimulus_fit_work.signed_component_sum != -0x7fffffff) {
        iVar9 = mode600_stimulus_fit_work.signed_component_sum;
        if (mode600_stimulus_fit_work.signed_component_sum < 0) {
          iVar9 = -mode600_stimulus_fit_work.signed_component_sum;
        }
      }
      else {
        iVar9 = 0x7fffffff;
      }
      iVar10 = (int)fit_parameters.component_mean_limit * (uint)fit_parameters.sample_count;
      if (iVar9 - iVar10 < 0 != (iVar9 < 0 != iVar10 < 0 && iVar10 < 0 == iVar9 - iVar10 < 0) ||
          iVar9 == iVar10) {
        (*((int16_t *)(stack_record_25 + 9))) = 0;
        stack_record_25[2] = '&';
        stack_record_25[0] = 'Z';
        (*((uint16_t *)(stack_record_25 + 7))) = 0;
        puVar5 = (uint32_t)(0xfebeb800u);
        if (mode600_stimulus_fit_work.state == '\x14') {
          stack_record_25[2] = '\x16';
        }
        goto LAB_00034204;
      }
    }
    goto switchD_000340ae_caseD_15;
  case '\x16':
switchD_000340ae_caseD_16:
    if (fit_parameters.release_hold_calls <= mode600_stimulus_fit_work.hold_count) {
      stack_record_25[2] = '1';
      puVar5 = (uint32_t)(0xfebeb800u);
      if (mode600_stimulus_fit_work.state == '\x16') {
        stack_record_25[2] = ' ';
      }
      goto LAB_00034204;
    }
  }
  (*((uint16_t *)(stack_record_25 + 7))) = mode600_stimulus_fit_work.hold_count + 1;
LAB_000343b2:
  *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xffffb26cu + (uint32_t)((int)puVar5) * 1u)))) = uVar14;
  *(short *)(((undefined *)camry_host_ptr((uint32_t)(0xffffb268u + (uint32_t)((int)puVar5) * 1u)))) = (*((int16_t *)(stack_record_25 + 9)));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb261u + (uint32_t)((int)puVar5) * 1u)))) = stack_record_25[1];
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb262u + (uint32_t)((int)puVar5) * 1u)))) = stack_record_25[0];
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb260u + (uint32_t)((int)puVar5) * 1u)))) = stack_record_25[2];
  *(short *)(((undefined *)camry_host_ptr((uint32_t)(0xffffb264u + (uint32_t)((int)puVar5) * 1u)))) = (*((int16_t *)(stack_record_25 + 3)));
  *(short *)(((undefined *)camry_host_ptr((uint32_t)(0xffffb266u + (uint32_t)((int)puVar5) * 1u)))) = (*((int16_t *)(stack_record_25 + 5)));
  *(int *)(((undefined *)camry_host_ptr((uint32_t)(0xffffb270u + (uint32_t)((int)puVar5) * 1u)))) = iVar12;
  *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xffffb274u + (uint32_t)((int)puVar5) * 1u)))) = uVar13;
  *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xffffb26au + (uint32_t)((int)puVar5) * 1u)))) = (*((uint16_t *)(stack_record_25 + 7)));
  { if (!camry_halted) { camry_gpr[26] = camry_read32((camry_sp + 48u) & ~3u); camry_gpr[27] = camry_read32((camry_sp + 44u) & ~3u); camry_gpr[28] = camry_read32((camry_sp + 40u) & ~3u); camry_gpr[29] = camry_read32((camry_sp + 36u) & ~3u); camry_gpr[31] = camry_read32((camry_sp + 32u) & ~3u); camry_sp += 52u; camry_gpr[3] = camry_sp; } return; }
}

uint begin_mode600_stimulus_fit(void)

{
  mode600_stimulus_fit_work.active = 'Z';
  initialize_mode600_stimulus_fit();
  return 0;
}

void return_only_stub_34406(void)

{
  return;
}

uint32_t restore_fit_coefficients(void)

{
  uint32_t camry_r10_result;
  uint8_t stack_record_44[68];
  uint *puVar1;
  uint32_t puVar2;
  uint uVar3;
  undefined4 uVar4;
  char *pcVar5;
  
  puVar2 = 0xfebeb800u;
  puVar1 = ((uint32_t *)(stack_record_44));
  pcVar5 = (undefined *)camry_host_ptr(0x21058u);
  do {
    uVar4 = *(undefined4 *)pcVar5;
    pcVar5 = pcVar5 + 4;
    *puVar1 = uVar4;
    puVar1 = puVar1 + 1;
  } while (camry_host_addr(pcVar5)!=((uint32_t)(0x21098u)));
  uVar3 = (camry_r10_result = nvm_get_record(0x202, camry_host_addr(((uint32_t *)(stack_record_44)))));
  if (uVar3 == 0x10) {
    uVar3 = (camry_r10_result = priority_mask_enter(0xffc0));
    (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb284u + (uint32_t)((int)puVar2)))))) = (*((uint16_t *)(stack_record_44 + 8)));
    (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb286u + (uint32_t)((int)puVar2)))))) = (*((uint16_t *)(stack_record_44 + 10)));
    (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb290u + (uint32_t)((int)puVar2)))))) = (*((uint16_t *)(stack_record_44 + 12)));
    (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb292u + (uint32_t)((int)puVar2)))))) = (*((uint16_t *)(stack_record_44 + 14)));
    (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb288u + (uint32_t)((int)puVar2)))))) = (*((uint16_t *)(stack_record_44 + 16)));
    (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb28au + (uint32_t)((int)puVar2)))))) = (*((uint16_t *)(stack_record_44 + 18)));
    (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb294u + (uint32_t)((int)puVar2)))))) = (*((uint16_t *)(stack_record_44 + 20)));
    (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb296u + (uint32_t)((int)puVar2)))))) = (*((uint16_t *)(stack_record_44 + 22)));
    (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb28cu + (uint32_t)((int)puVar2)))))) = (*((uint16_t *)(stack_record_44 + 24)));
    (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb28eu + (uint32_t)((int)puVar2)))))) = (*((uint16_t *)(stack_record_44 + 26)));
    (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb298u + (uint32_t)((int)puVar2)))))) = (*((uint16_t *)(stack_record_44 + 28)));
    (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb29au + (uint32_t)((int)puVar2)))))) = (*((uint16_t *)(stack_record_44 + 30)));
    (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb29cu + (uint32_t)((int)puVar2)))))) = (*((uint16_t *)(stack_record_44 + 32)));
    (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb29eu + (uint32_t)((int)puVar2)))))) = (*((uint16_t *)(stack_record_44 + 34)));
    (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb2a8u + (uint32_t)((int)puVar2)))))) = (*((uint16_t *)(stack_record_44 + 36)));
    (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb2aau + (uint32_t)((int)puVar2)))))) = (*((uint16_t *)(stack_record_44 + 38)));
    (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb2b4u + (uint32_t)((int)puVar2)))))) = (*((uint16_t *)(stack_record_44 + 40)));
    (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb2a0u + (uint32_t)((int)puVar2)))))) = (*((uint16_t *)(stack_record_44 + 42)));
    (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb2a2u + (uint32_t)((int)puVar2)))))) = (*((uint16_t *)(stack_record_44 + 44)));
    (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb2acu + (uint32_t)((int)puVar2)))))) = (*((uint16_t *)(stack_record_44 + 46)));
    (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb2aeu + (uint32_t)((int)puVar2)))))) = (*((uint16_t *)(stack_record_44 + 48)));
    (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb2b6u + (uint32_t)((int)puVar2)))))) = (*((uint16_t *)(stack_record_44 + 50)));
    (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb2a4u + (uint32_t)((int)puVar2)))))) = (*((uint16_t *)(stack_record_44 + 52)));
    (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb2a6u + (uint32_t)((int)puVar2)))))) = (*((uint16_t *)(stack_record_44 + 54)));
    (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb2b0u + (uint32_t)((int)puVar2)))))) = (*((uint16_t *)(stack_record_44 + 56)));
    (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb2b2u + (uint32_t)((int)puVar2)))))) = (*((uint16_t *)(stack_record_44 + 58)));
    (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb2b8u + (uint32_t)((int)puVar2)))))) = (*((uint16_t *)(stack_record_44 + 60)));
    priority_mask_restore(uVar3);
  }
  return camry_r10_result;
}

uint check_retained_fit_bounds(void)

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
  
  iVar1 = (int)retained_fit_coefficients.second_center[0];
  iVar9 = (int)retained_fit_coefficients.second_center[1];
  iVar8 = (int)retained_fit_coefficients.second_center[2];
  iVar7 = (int)retained_fit_coefficients.second_center[3];
  iVar6 = (int)retained_fit_coefficients.second_center[4];
  iVar5 = (int)retained_fit_coefficients.second_center[5];
  if (((((((((DAT_00030ef6 < retained_fit_coefficients.first_gain[0]) ||
            (retained_fit_coefficients.first_gain[0] < DAT_00030ef8)) ||
           (DAT_00030ef6 < retained_fit_coefficients.first_gain[1])) ||
          ((retained_fit_coefficients.first_gain[1] < DAT_00030ef8 ||
           (DAT_00030efe < retained_fit_coefficients.first_center[0])))) ||
         (retained_fit_coefficients.first_center[0] < DAT_00030f00)) ||
        (((DAT_00030efe < retained_fit_coefficients.first_center[1] ||
          (retained_fit_coefficients.first_center[1] < DAT_00030f00)) ||
         ((DAT_00030ef6 < retained_fit_coefficients.first_gain[2] ||
          (((retained_fit_coefficients.first_gain[2] < DAT_00030ef8 ||
            (DAT_00030ef6 < retained_fit_coefficients.first_gain[3])) ||
           (retained_fit_coefficients.first_gain[3] < DAT_00030ef8)))))))) ||
       (((((DAT_00030efe < retained_fit_coefficients.first_center[2] ||
           (retained_fit_coefficients.first_center[2] < DAT_00030f00)) ||
          ((DAT_00030efe < retained_fit_coefficients.first_center[3] ||
           (((retained_fit_coefficients.first_center[3] < DAT_00030f00 ||
             (DAT_00030ef6 < retained_fit_coefficients.first_gain[4])) ||
            ((retained_fit_coefficients.first_gain[4] < DAT_00030ef8 ||
             (((DAT_00030ef6 < retained_fit_coefficients.first_gain[5] ||
               (retained_fit_coefficients.first_gain[5] < DAT_00030ef8)) ||
              (DAT_00030efe < retained_fit_coefficients.first_center[4])))))))))) ||
         ((retained_fit_coefficients.first_center[4] < DAT_00030f00 ||
          (DAT_00030efe < retained_fit_coefficients.first_center[5])))) ||
        (retained_fit_coefficients.first_center[5] < DAT_00030f00)))) ||
      (((((DAT_00030efa < retained_fit_coefficients.second_gain[0] ||
          (retained_fit_coefficients.second_gain[0] < DAT_00030efc)) ||
         ((DAT_00030efa < retained_fit_coefficients.second_gain[1] ||
          ((((retained_fit_coefficients.second_gain[1] < DAT_00030efc ||
             (iVar4 = (int)DAT_00030f02,
             iVar1 - iVar4 < 0 == (iVar1 < 0 != iVar4 < 0 && iVar4 < 0 == iVar1 - iVar4 < 0) &&
             iVar1 != iVar4)) ||
            (iVar3 = (int)DAT_00030f04,
            iVar1 - iVar3 < 0 != (iVar1 < 0 != iVar3 < 0 && iVar3 < 0 == iVar1 - iVar3 < 0))) ||
           ((iVar9 - iVar4 < 0 == (iVar9 < 0 != iVar4 < 0 && iVar4 < 0 == iVar9 - iVar4 < 0) &&
             iVar9 != iVar4 ||
            (iVar9 - iVar3 < 0 != (iVar9 < 0 != iVar3 < 0 && iVar3 < 0 == iVar9 - iVar3 < 0)))))))))
        || (DAT_00030f06 < retained_fit_coefficients.component_angle[0])) ||
       (((retained_fit_coefficients.component_angle[0] < DAT_00030f08 ||
         (DAT_00030efa < retained_fit_coefficients.second_gain[2])) ||
        ((retained_fit_coefficients.second_gain[2] < DAT_00030efc ||
         (((DAT_00030efa < retained_fit_coefficients.second_gain[3] ||
           (retained_fit_coefficients.second_gain[3] < DAT_00030efc)) ||
          (iVar8 - iVar4 < 0 == (iVar8 < 0 != iVar4 < 0 && iVar4 < 0 == iVar8 - iVar4 < 0) &&
           iVar8 != iVar4)))))))))) ||
     ((((iVar8 - iVar3 < 0 != (iVar8 < 0 != iVar3 < 0 && iVar3 < 0 == iVar8 - iVar3 < 0) ||
        (iVar7 - iVar4 < 0 == (iVar7 < 0 != iVar4 < 0 && iVar4 < 0 == iVar7 - iVar4 < 0) &&
         iVar7 != iVar4)) ||
       (iVar7 - iVar3 < 0 != (iVar7 < 0 != iVar3 < 0 && iVar3 < 0 == iVar7 - iVar3 < 0))) ||
      ((((DAT_00030f06 < retained_fit_coefficients.component_angle[1] ||
         (retained_fit_coefficients.component_angle[1] < DAT_00030f08)) ||
        ((((DAT_00030efa < retained_fit_coefficients.second_gain[4] ||
           (((retained_fit_coefficients.second_gain[4] < DAT_00030efc ||
             (DAT_00030efa < retained_fit_coefficients.second_gain[5])) ||
            (retained_fit_coefficients.second_gain[5] < DAT_00030efc)))) ||
          ((iVar6 - iVar4 < 0 == (iVar6 < 0 != iVar4 < 0 && iVar4 < 0 == iVar6 - iVar4 < 0) &&
            iVar6 != iVar4 ||
           (iVar6 - iVar3 < 0 != (iVar6 < 0 != iVar3 < 0 && iVar3 < 0 == iVar6 - iVar3 < 0))))) ||
         (iVar5 - iVar4 < 0 == (iVar5 < 0 != iVar4 < 0 && iVar4 < 0 == iVar5 - iVar4 < 0) &&
          iVar5 != iVar4)))) ||
       (((iVar5 - iVar3 < 0 != (iVar5 < 0 != iVar3 < 0 && iVar3 < 0 == iVar5 - iVar3 < 0) ||
         (DAT_00030f06 < retained_fit_coefficients.component_angle[2])) ||
        (retained_fit_coefficients.component_angle[2] < DAT_00030f08)))))))) {
    uVar2 = 0x5a;
  }
  else {
    uVar2 = 0;
  }
  return uVar2;
}

uint reset_retained_fit_coefficients(void)

{
  uint32_t puVar1;
  uint saved_mask;
  
  puVar1 = 0xfebeb800u;
  saved_mask = priority_mask_enter(0xffc0);
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
  priority_mask_restore(saved_mask);
  return saved_mask;
}

uint validate_or_default_retained_fit(void)

{
  uint uVar1;
  
  uVar1 = check_retained_fit_bounds();
  if (uVar1 == 0x5a) {
    reset_retained_fit_coefficients();
  }
  return uVar1;
}

void mark_record_206_status_healthy_default_346cc(void)

{
  DAT_febe6a7f = 0x44;
  DAT_febe6ac4 = 0xa55a5aa5;
  DAT_febe6a7e = 0;
  report_diagnostic_healthy_observed(0x127);
  return;
}

void initialize_fit_and_record_205_validity_states_346f0(void)

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
  uVar3 = nvm_get_record(0x202, camry_host_addr(local_54));
  uVar5 = 0xa55a5aa5;
  if ((uVar3 == 0x10) && (local_54[0] == 0xa55a5aa5)) {
    restore_fit_coefficients();
    uVar3 = validate_or_default_retained_fit();
    if (uVar3 == 0) {
      uVar7 = 0xa55a5aa5;
      uVar8 = 0x44;
      report_diagnostic_healthy_observed(0x125);
      goto LAB_00034744;
    }
  }
  uVar7 = 0x5aa5a55a;
  uVar8 = 0x22;
  report_diagnostic_event_failure(0x125,0x32);
LAB_00034744:
  uVar3 = nvm_get_record_status(0x205);
  iVar4 = camry_host_addr(get_monitor_current_rom_record_567be());
  if ((uVar3 == 0x10) && ((*((int *)camry_host_ptr((uint32_t)(iVar4 + 0xb8)))) == -0x5aa5a55b)) {
    uVar6 = 0x44;
    report_diagnostic_healthy_observed(0x126);
  }
  else {
    uVar5 = 0x5aa5a55a;
    uVar6 = 0x22;
    report_diagnostic_event_failure(0x126,0x32);
  }
  mark_record_206_status_healthy_default_346cc();
  uVar1 = DAT_00030ef2;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb279u + (uint32_t)((int)puVar2) * 1u)))) = uVar8;
  (*((undefined4 *)camry_host_ptr((uint32_t)((0xffffb2bcu + (uint32_t)((int)puVar2)))))) = uVar7;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb27cu + (uint32_t)((int)puVar2) * 1u)))) = uVar6;
  (*((undefined4 *)camry_host_ptr((uint32_t)((0xffffb2c0u + (uint32_t)((int)puVar2)))))) = uVar5;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb282u + (uint32_t)((int)puVar2)))))) = uVar1;
  return;
}

undefined4 restore_validate_fit_and_return_validity_marker_347a2(void)

{
  uint uVar1;
  uint local_44 [16];
  
  uVar1 = nvm_get_record(0x202, camry_host_addr(local_44));
  if ((uVar1 == 0x10) && (local_44[0] == 0xa55a5aa5)) {
    restore_fit_coefficients();
    uVar1 = validate_or_default_retained_fit();
    if (uVar1 == 0) {
      return 0xa55a5aa5;
    }
  }
  return 0x5aa5a55a;
}

void service_fit_revalidation_and_status_countdown_347e2(void)

{
  char cVar1;
  undefined4 uVar2;
  uint32_t puVar3;
  int iVar4;
  undefined1 uVar5;
  short sVar6;
  
  uVar2 = DAT_febe6ac0;
  cVar1 = DAT_febe6a7c;
  puVar3 = (0xfebeb800u);
  sVar6 = DAT_febe6a82;
  if (DAT_febe6a82 != 0) {
    sVar6 = DAT_febe6a82 + -1;
  }
  iVar4 = DAT_febe6abc;
  if (((DAT_febe6579 == 'Z') && (DAT_febe6abc == -0x5aa5a55b)) &&
     (puVar3 = (0xfebeb800u), iVar4 = restore_validate_fit_and_return_validity_marker_347a2(), iVar4 != -0x5aa5a55b)) {
    report_diagnostic_event_failure(0x125,0x32);
  }
  uVar5 = 0;
  if (cVar1 == 'D') {
    uVar5 = 0x5a;
  }
  if (DAT_00030ef0 == 'Z') {
    uVar5 = 0;
  }
  mark_record_206_status_healthy_default_346cc();
  DAT_febe6abc = (uint)iVar4;
  DAT_febe6ac0 = (uint)uVar2;
  DAT_febe6a7b = (uint8_t)uVar5;
  DAT_febe6a82 = (ushort)sVar6;
  return;
}

void validate_record_206_status_and_retained_marker_34858(void)

{
  uint32_t puVar1;
  uint uVar2;
  int iVar3;
  undefined4 uVar4;
  undefined1 uVar5;
  
  puVar1 = 0xfebeb800u;
  uVar2 = nvm_get_record_status(0x206);
  iVar3 = camry_host_addr(get_monitor_current_rom_record_567be());
  if ((uVar2 == 0x10) && ((*((int *)camry_host_ptr((uint32_t)(iVar3 + 0x4c8)))) == -0x5aa5a55b)) {
    uVar5 = 0x44;
    report_diagnostic_healthy_observed(0x127);
    uVar4 = 0xa55a5aa5;
  }
  else {
    uVar4 = 0x5aa5a55a;
    uVar5 = 0x22;
    report_diagnostic_event_failure(0x127,0x32);
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb27fu + (uint32_t)((int)puVar1) * 1u)))) = uVar5;
  (*((undefined4 *)camry_host_ptr((uint32_t)((0xffffb2c4u + (uint32_t)((int)puVar1)))))) = uVar4;
  return;
}

uint32_t publish_fit_candidate_record(void)

{
  uint32_t camry_r10_result;
  uint8_t stack_record_6c[108];
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  retained_fit_coefficients.first_center[0] = DAT_febe654e;
  retained_fit_coefficients.first_center[1] = DAT_febe6550;
  retained_fit_coefficients.first_gain[0] = DAT_febe6542;
  retained_fit_coefficients.first_gain[1] = DAT_febe6544;
  retained_fit_coefficients.first_center[2] = DAT_febe6552;
  retained_fit_coefficients.first_center[3] = DAT_febe6554;
  retained_fit_coefficients.first_gain[2] = DAT_febe6546;
  retained_fit_coefficients.first_gain[3] = DAT_febe6548;
  retained_fit_coefficients.first_center[4] = DAT_febe6556;
  retained_fit_coefficients.first_center[5] = DAT_febe6558;
  retained_fit_coefficients.first_gain[4] = DAT_febe654a;
  retained_fit_coefficients.first_gain[5] = DAT_febe654c;
  retained_fit_coefficients.second_center[0] = ((int)(int16_t)DAT_febe6566);
  retained_fit_coefficients.second_center[1] = ((int)(int16_t)DAT_febe6568);
  retained_fit_coefficients.second_gain[0] = DAT_febe655a;
  retained_fit_coefficients.second_gain[1] = DAT_febe655c;
  retained_fit_coefficients.component_angle[0] = DAT_febe6572;
  retained_fit_coefficients.second_center[2] = ((int)(int16_t)DAT_febe656a);
  retained_fit_coefficients.second_center[3] = ((int)(int16_t)DAT_febe656c);
  retained_fit_coefficients.second_gain[2] = DAT_febe655e;
  retained_fit_coefficients.second_gain[3] = DAT_febe6560;
  retained_fit_coefficients.component_angle[1] = DAT_febe6574;
  retained_fit_coefficients.second_center[4] = ((int)(int16_t)DAT_febe656e);
  retained_fit_coefficients.second_center[5] = ((int)(int16_t)DAT_febe6570);
  retained_fit_coefficients.second_gain[4] = DAT_febe6562;
  retained_fit_coefficients.second_gain[5] = DAT_febe6564;
  retained_fit_coefficients.component_angle[2] = DAT_febe6576;
  ((uint32_t *)(stack_record_6c))[1] = 0;
  ((uint32_t *)(stack_record_6c))[0] = 0xa55a5aa5;
  (*((uint16_t *)(stack_record_6c + 10))) = DAT_febe6550;
  (*((uint16_t *)(stack_record_6c + 8))) = DAT_febe654e;
  (*((uint16_t *)(stack_record_6c + 26))) = DAT_febe6558;
  (*((int16_t *)(stack_record_6c + 34))) = ((int)(int16_t)DAT_febe6568);
  (*((uint16_t *)(stack_record_6c + 36))) = DAT_febe655a;
  (*((uint16_t *)(stack_record_6c + 12))) = DAT_febe6542;
  (*((uint16_t *)(stack_record_6c + 14))) = DAT_febe6544;
  (*((uint16_t *)(stack_record_6c + 16))) = DAT_febe6552;
  (*((uint16_t *)(stack_record_6c + 18))) = DAT_febe6554;
  (*((uint16_t *)(stack_record_6c + 20))) = DAT_febe6546;
  (*((uint16_t *)(stack_record_6c + 22))) = DAT_febe6548;
  (*((uint16_t *)(stack_record_6c + 24))) = DAT_febe6556;
  (*((uint16_t *)(stack_record_6c + 28))) = DAT_febe654a;
  (*((uint16_t *)(stack_record_6c + 30))) = DAT_febe654c;
  (*((int16_t *)(stack_record_6c + 32))) = ((int)(int16_t)DAT_febe6566);
  (*((uint16_t *)(stack_record_6c + 38))) = DAT_febe655c;
  (*((uint16_t *)(stack_record_6c + 40))) = DAT_febe6572;
  (*((int16_t *)(stack_record_6c + 42))) = ((int)(int16_t)DAT_febe656a);
  (*((int16_t *)(stack_record_6c + 44))) = ((int)(int16_t)DAT_febe656c);
  (*((uint16_t *)(stack_record_6c + 46))) = DAT_febe655e;
  (*((uint16_t *)(stack_record_6c + 48))) = DAT_febe6560;
  (*((uint16_t *)(stack_record_6c + 50))) = DAT_febe6574;
  (*((int16_t *)(stack_record_6c + 52))) = ((int)(int16_t)DAT_febe656e);
  (*((int16_t *)(stack_record_6c + 54))) = ((int)(int16_t)DAT_febe6570);
  (*((uint16_t *)(stack_record_6c + 56))) = DAT_febe6562;
  (*((uint16_t *)(stack_record_6c + 58))) = DAT_febe6564;
  (*((uint16_t *)(stack_record_6c + 60))) = DAT_febe6576;
  (*((uint16_t *)(stack_record_6c + 62))) = 0;
  (camry_r10_result = nvm_set_record(0x202,((uint32_t *)(stack_record_6c))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb27au + (uint32_t)((int)puVar1) * 1u)))) = 0x44;
  (*((undefined4 *)camry_host_ptr((uint32_t)((0xffffb2bcu + (uint32_t)((int)puVar1)))))) = 0xa55a5aa5;
  return camry_r10_result;
}

void invalidate_fit_record_202_header_34bce(void)

{
  uint32_t puVar1;
  uint local_44 [16];
  
  puVar1 = 0xfebeb800u;
  nvm_get_record(0x202, camry_host_addr(local_44));
  local_44[0] = 0;
  nvm_set_record(0x202,local_44);
  (*((undefined4 *)camry_host_ptr((uint32_t)((0xffffb2bcu + (uint32_t)((int)puVar1)))))) = 0x5aa5a55a;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb278u + (uint32_t)((int)puVar1) * 1u)))) = 0x44;
  return;
}

bool check_zero_fit_state_and_event_52_gate_34c00(void)

{
  ushort uVar1;
  int iVar2;
  char cVar3;
  bool bVar4;
  uint uVar5;
  
  cVar3 = DAT_febee81a;
  iVar2 = DAT_febe6abc;
  uVar1 = DAT_febe66b8;
  uVar5 = get_diagnostic_event_state(0x52);
  if (((cVar3 == '\x01') && (DAT_00030ef4 <= uVar1)) && (iVar2 == 0)) {
    bVar4 = (uVar5 >> 1 & 1) == 0;
  }
  else {
    bVar4 = false;
  }
  return bVar4;
}

uint check_fit_record_admission(void)

{
  uint uVar1;
  
  uVar1 = check_retained_fit_bounds();
  return uVar1;
}

void return_only_stub_34c46(void)

{
  return;
}

void clear_state_bytes_6ac8_and_counter_6acc_34c48(void)

{
  DAT_febe6acc = 0;
  DAT_febe6ac8 = 0;
  DAT_febe6ac9 = 0;
  DAT_febe6aca = 0;
  return;
}

void select_mode600_stimulus_request(void)

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
      interpolate_s16_axis_s16_values_70208(((undefined *)camry_host_ptr(0x30f0cu)),(int)-((int)(int16_t)DAT_febe7e0c),&sStack_e);
      sStack_e = -sStack_e;
    }
    else {
      interpolate_s16_axis_s16_values_70208(((undefined *)camry_host_ptr(0x30f0cu)),(int)((int)(int16_t)DAT_febe7e0c),&sStack_e);
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb2c9u + (uint32_t)((int)puVar1) * 1u)))) = uVar3;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb2c8u + (uint32_t)((int)puVar1) * 1u)))) = uVar2;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb2ccu + (uint32_t)((int)puVar1)))))) = -sStack_e;
  return;
}

void return_only_stub_34cce(void)

{
  return;
}

uint32_t reload_ba_admission_records(void)

{
  uint8_t stack_record_18[24];
  uint32_t camry_r10_result;
  uint32_t puVar1;
  uint uVar2;
  undefined1 uVar3;
  
  puVar1 = 0xfebeb800u;
  uVar2 = (camry_r10_result = nvm_get_record(0x105, camry_host_addr(((uint32_t *)((stack_record_18 + 8))))));
  if ((uVar2 == 0x10) && (((uint32_t *)((stack_record_18 + 8)))[0] == 0xa55a5aa5)) {
    uVar3 = 0x5a;
  }
  else {
    uVar3 = 0;
  }
  uVar2 = (camry_r10_result = nvm_get_record(0x18, camry_host_addr((uint *)((uint8_t *)(stack_record_18)))));
  if ((uVar2 != 0x10) || (ba_retained_admission_count_limit < ((uint8_t *)(stack_record_18))[0])) {
    ((uint8_t *)(stack_record_18))[0] = 0;
    uVar3 = 0;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x58b0))))) = ((uint8_t *)(stack_record_18))[0];
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x58b1))))) = uVar3;
  return camry_r10_result;
}

void poll_ba_retained_start(void)

{
  uint32_t puVar1;
  uint uVar2;
  int iVar3;
  uchar uVar4;
  uchar auStack_4f [63];
  
  puVar1 = 0xfebeb800u;
  uVar4 = '\0';
  uVar2 = (uint)ba_application_work.selected_index;
  if (ba_application_work.retained_start_phase == 'Z') {
    iVar3 = (*(int (*)())camry_indirect((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x27ec4u + (uint32_t)(uVar2) * (uint32_t)sizeof(F33BaConfiguredOperation)) + (uint32_t)(0) * (uint32_t)sizeof(F33BaConfiguredOperation) + (uint32_t)offsetof(F33BaConfiguredOperation, start))))))))(ba_application_work.selected_index,camry_host_addr((uchar *)0x0),camry_host_addr(auStack_4f));
    if (iVar3 != -1) {
      if (-1 < iVar3) {
        uVar4 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0x27ec4u + (uint32_t)(uVar2) * (uint32_t)sizeof(F33BaConfiguredOperation)) + (uint32_t)(0) * (uint32_t)sizeof(F33BaConfiguredOperation) + (uint32_t)offsetof(F33BaConfiguredOperation, response_body_length)))));
      }
      ((void)(auStack_4f), complete_ba10_pending_result_4d4ca(iVar3, uVar4));
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x58b4))))) = 0;
    }
  }
  return;
}

uint compare_ba_token_bytes(uchar *left,uchar *right,uchar length)

{
  uint uVar1;
  
  uVar1 = 0;
  while( true ) {
    if (length <= uVar1) {
      return 1;
    }
    if ((uintptr_t)(((left[uVar1])))!=(uintptr_t)(((right[uVar1])))) break;
    uVar1 = uVar1 + 1 & 0xff;
  }
  return 0;
}

uint ba_enable_closed_gate_exception(uchar operation,uchar request_length,uchar *payload)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = 0;
  uVar1 = compare_ba_token_bytes
                    (payload,(uchar *)"BAENAJTEKMTMPCLJTRM1JTRM2BADISBAENATZCLRJTRM3VSPDASINC",
                     '\x05');
  if (((operation == 0xf7) && (request_length == '\x06')) && (uVar1 == 1)) {
    uVar2 = 0x5a;
  }
  return uVar2;
}

int dispatch_ba_configured_start
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
  uVar3 = ba_enable_closed_gate_exception(operation,request_length,request + 1);
  if (((*((char *)camry_host_ptr((uint32_t)((int)uVar2 + -0x58b1)))) == 'Z') || (uVar3 == 0x5a)) {
    for (uVar3 = 0; uVar3 < ba_operation_count; uVar3 = uVar3 + 1 & 0xff) {
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0x27ec4u + (uint32_t)(uVar3) * (uint32_t)sizeof(F33BaConfiguredOperation)) + (uint32_t)(0) * (uint32_t)sizeof(F33BaConfiguredOperation) + (uint32_t)offsetof(F33BaConfiguredOperation, operation))))) == operation) {
        bVar1 = true;
        if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0x27ec4u + (uint32_t)(uVar3) * (uint32_t)sizeof(F33BaConfiguredOperation)) + (uint32_t)(0) * (uint32_t)sizeof(F33BaConfiguredOperation) + (uint32_t)offsetof(F33BaConfiguredOperation, request_length))))) == request_length) {
          iVar4 = -3;
          if ((*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x27ec4u + (uint32_t)(uVar3) * (uint32_t)sizeof(F33BaConfiguredOperation)) + (uint32_t)(0) * (uint32_t)sizeof(F33BaConfiguredOperation) + (uint32_t)offsetof(F33BaConfiguredOperation, start))))) != 0x0u) {
            phase = (uchar)uVar3;
            iVar4 = (*(int (*)())camry_indirect((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x27ec4u + (uint32_t)(uVar3) * (uint32_t)sizeof(F33BaConfiguredOperation)) + (uint32_t)(0) * (uint32_t)sizeof(F33BaConfiguredOperation) + (uint32_t)offsetof(F33BaConfiguredOperation, start))))))))(phase,camry_host_addr(request + 1),camry_host_addr(response));
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

int dispatch_ba_configured_finish(uchar configured_index,uint *response_length)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  if ((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x27ec4u + (uint32_t)(configured_index) * (uint32_t)sizeof(F33BaConfiguredOperation) + (uint32_t)offsetof(F33BaConfiguredOperation, finish))))) )==0x0u) {
    iVar2 = -3;
  }
  else {
    iVar2 = (*(int (*)())camry_indirect((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x27ec4u + (uint32_t)(configured_index) * (uint32_t)sizeof(F33BaConfiguredOperation) + (uint32_t)offsetof(F33BaConfiguredOperation, finish))))))))((uint)(byte)configured_index, camry_host_addr(response_length));
    if (-1 < iVar2) {
      *response_length = (uint)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x27ec4u + (uint32_t)(configured_index) * (uint32_t)sizeof(F33BaConfiguredOperation) + (uint32_t)offsetof(F33BaConfiguredOperation, response_body_length)))));
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x58ad))))) = 0x5a;
    }
  }
  return iVar2;
}

void submit_up_to_eight_response_bytes_or_error_34ea4(int param_1,int param_2)

{
  uint8_t stack_record_15[21];
  uint uVar1;
  undefined4 uVar2;
  
  uVar1 = 0;
  do {
    ((uint8_t *)((stack_record_15 + 1)))[uVar1] = 0;
    uVar1 = uVar1 + 1;
  } while (uVar1 < 8);
  store_s32_saturated_to_u8_6a624(param_2,((uint8_t *)(stack_record_15)));
  if ((param_2 < 0) || (8 < stack_record_15[0])) {
    uVar2 = 0xfffffffa;
  }
  else {
    uVar2 = 0;
    for (uVar1 = 0; uVar1 < stack_record_15[0]; uVar1 = uVar1 + 1 & 0xff) {
      ((uint8_t *)((stack_record_15 + 1)))[uVar1] = (*((undefined1 *)camry_host_ptr((uint32_t)(uVar1 + param_1))));
    }
  }
  ((void)(((uint8_t *)((stack_record_15 + 1)))), complete_ba10_pending_result_4d4ca(uVar2, stack_record_15[0]));
  return;
}

int encode_ba_numeric_source_values_by_format_34f00(uint param_1,int param_2)

{
  uint8_t stack_record_2c[44];
  uchar uVar1;
  uint uVar2;
  int iVar3;
  uint uVar4;
  uint uVar5;
  
  param_1 = param_1 & 0xff;
  iVar3 = 0;
  uVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0x27ec4u + (uint32_t)(param_1) * (uint32_t)sizeof(F33BaConfiguredOperation)) + (uint32_t)(0) * (uint32_t)sizeof(F33BaConfiguredOperation) + (uint32_t)offsetof(F33BaConfiguredOperation, numeric_format)))));
  if ((*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x27ec4u + (uint32_t)(param_1) * (uint32_t)sizeof(F33BaConfiguredOperation)) + (uint32_t)(0) * (uint32_t)sizeof(F33BaConfiguredOperation) + (uint32_t)offsetof(F33BaConfiguredOperation, numeric_source))))) != 0x0u) {
    (*(int (*)())camry_indirect((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x27ec4u + (uint32_t)(param_1) * (uint32_t)sizeof(F33BaConfiguredOperation)) + (uint32_t)(0) * (uint32_t)sizeof(F33BaConfiguredOperation) + (uint32_t)offsetof(F33BaConfiguredOperation, numeric_source))))))))(camry_host_addr(((uint32_t *)(stack_record_2c))),camry_host_addr(((uint32_t *)((stack_record_2c + 4)))));
    if ((*((uint32_t *)(stack_record_2c + 4))) != 0) {
      uVar4 = 2;
      ((uint32_t *)((stack_record_2c + 8)))[0] = (*((uint32_t *)(stack_record_2c + 0)));
      goto LAB_00034f56;
    }
    if ((*((uint32_t *)(stack_record_2c + 0))) != 0) {
      ((uint32_t *)((stack_record_2c + 8)))[0] = (*((uint32_t *)(stack_record_2c + 0)));
      uVar4 = 1;
      (*((uint32_t *)(stack_record_2c + 4))) = 0;
      goto LAB_00034f56;
    }
  }
  uVar4 = 0;
  (*((uint32_t *)(stack_record_2c + 4))) = 0;
  ((uint32_t *)((stack_record_2c + 8)))[0] = 0;
LAB_00034f56:
  ((uint32_t *)((stack_record_2c + 8)))[1] = (*((uint32_t *)(stack_record_2c + 4)));
  uVar5 = 0;
  do {
    if (uVar4 <= uVar5) {
      return iVar3;
    }
    if (iVar3 == 0) {
      if (uVar1 == '\x01') {
LAB_00034fa6:
        (*((char *)camry_host_ptr((uint32_t)(uVar5 + param_2)))) = (char)((uint32_t *)((stack_record_2c + 8)))[uVar5];
      }
      else if (uVar1 == '\x02') {
        store_low_u16_big_endian_bytes_6a574((short)((uint32_t *)((stack_record_2c + 8)))[uVar5], ((undefined1 *)camry_host_ptr((uint32_t)(uVar5 * 2 + param_2))));
      }
      else if (uVar1 == '\x04') {
        store_u32_big_endian_bytes_6a55c(((uint32_t *)((stack_record_2c + 8)))[uVar5], ((undefined1 *)camry_host_ptr((uint32_t)(uVar5 * 4 + param_2))));
      }
      else {
        if (uVar1 == '\t') goto LAB_00034fa6;
        if (uVar1 == '\n') {
          store_low_u16_big_endian_bytes_6a5ac((int)(short)((uint32_t *)((stack_record_2c + 8)))[uVar5], ((undefined1 *)camry_host_ptr((uint32_t)(uVar5 * 2 + param_2))));
        }
        else if (uVar1 == '\f') {
          store_u32_big_endian_bytes_6a594(((uint32_t *)((stack_record_2c + 8)))[uVar5], ((undefined1 *)camry_host_ptr((uint32_t)(uVar5 * 4 + param_2))));
        }
        else {
          iVar3 = -6;
        }
      }
    }
    else {
      for (uVar2 = 0; uVar2 < (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0x27ec4u + (uint32_t)(param_1) * (uint32_t)sizeof(F33BaConfiguredOperation)) + (uint32_t)(0) * (uint32_t)sizeof(F33BaConfiguredOperation) + (uint32_t)offsetof(F33BaConfiguredOperation, response_body_length)))));
          uVar2 = uVar2 + 1 & 0xff) {
        (*((undefined1 *)camry_host_ptr((uint32_t)(uVar2 + param_2)))) = 0;
      }
    }
    uVar5 = uVar5 + 1 & 0xff;
  } while( true );
}
