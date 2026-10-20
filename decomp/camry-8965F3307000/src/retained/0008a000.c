#include "common.h"

void thunk_synchronize_instruction_execution_8b060(void)

{
  synchronize_instruction_execution_8b060();
  return;
}

void set_eic292_293_mask_from_boolean_8a22c(int param_1)

{
  uint16_t EVar1;
  
  EVar1 = EIC292;
  if (param_1 == 1) {
    EIC292 = (uint16_t)((ushort)EVar1 & 0xff7f);
    EVar1 = EIC293;
    EVar1 = (uint16_t)((ushort)EVar1 & 0xff7f);
  }
  else {
    EIC292 = (uint16_t)((ushort)EVar1 | 0x80);
    EVar1 = EIC293;
    EVar1 = (uint16_t)((ushort)EVar1 | 0x80);
  }
  EIC293 = EVar1;
  EVar1 = EIC293;
  thunk_synchronize_instruction_execution_8b060();
  return;
}

undefined4 abort_busy_icus_and_wait_ready_8a26a(void)

{
  ICUS_Status IVar1;
  uint uVar2;
  uint16_t EVar3;
  uint16_t EVar4;
  int iVar5;
  undefined4 uVar6;
  
  IVar1.raw = ICUSSTS;
  if (IVar1.BUSY == 0) {
    uVar6 = 1;
  }
  else {
    EVar3 = EIC292;
    EVar4 = EIC293;
    set_eic292_293_mask_from_boolean_8a22c(0);
    uVar6 = 2;
    ICUSCMD = (uint32_t)0x3f;
    iVar5 = 0x9c4;
    do {
      IVar1.raw = ICUSSTS;
      uVar2 = ICUSSTS2;
      if ((IVar1.BUSY == 0) && ((uVar2 & 2) == 2)) {
        ICUSCTL = 3;
        uVar2 = ICUSCTL;
        thunk_synchronize_instruction_execution_8b060();
        uVar6 = 1;
        break;
      }
      iVar5 = iVar5 + -1;
    } while (iVar5 != 0);
    EIC292 = (uint16_t)((ushort)EVar3 & 0xefff);
    EIC293 = (uint16_t)((ushort)EVar4 & 0xefff);
    EVar3 = EIC293;
    thunk_synchronize_instruction_execution_8b060();
  }
  return uVar6;
}

undefined4 write_verify_d0e0_and_four_words_8a2e4(uint param_1)

{
  uint uVar1;
  
  DAT_ffc5d0e0 = param_1 & 1;
  DAT_ffc5d0f0 = param_1;
  DAT_ffc5d0f4 = param_1;
  DAT_ffc5d0f8 = param_1;
  DAT_ffc5d0fc = param_1;
  uVar1 = DAT_ffc5d0e0;
  if (((((uVar1 & 1) == (param_1 & 1)) && (uVar1 = DAT_ffc5d0f0, uVar1 == param_1)) &&
      (uVar1 = DAT_ffc5d0f4, uVar1 == param_1)) &&
     ((uVar1 = DAT_ffc5d0f8, uVar1 == param_1 && (uVar1 = DAT_ffc5d0fc, uVar1 == param_1)))) {
    return 1;
  }
  return 2;
}

undefined4 write_verify_icusparam_and_four_words_8a332(uint param_1)

{
  uint uVar1;
  
  ICUSPARAM = param_1;
  DAT_ffc5d090 = param_1;
  DAT_ffc5d094 = param_1;
  DAT_ffc5d098 = param_1;
  DAT_ffc5d09c = param_1;
  uVar1 = ICUSPARAM;
  if ((((uVar1 == param_1) && (uVar1 = DAT_ffc5d090, uVar1 == param_1)) &&
      (uVar1 = DAT_ffc5d094, uVar1 == param_1)) &&
     ((uVar1 = DAT_ffc5d098, uVar1 == param_1 && (uVar1 = DAT_ffc5d09c, uVar1 == param_1)))) {
    return 1;
  }
  return 2;
}

undefined4 write_verify_eight_d0a0_words_8a378(int param_1)

{
  int iVar1;
  
  DAT_ffc5d0a0 = param_1;
  DAT_ffc5d0a4 = param_1;
  DAT_ffc5d0a8 = param_1;
  DAT_ffc5d0ac = param_1;
  DAT_ffc5d0b0 = param_1;
  DAT_ffc5d0b4 = param_1;
  DAT_ffc5d0b8 = param_1;
  DAT_ffc5d0bc = param_1;
  iVar1 = DAT_ffc5d0a0;
  if (((((iVar1 == param_1) && (iVar1 = DAT_ffc5d0a4, iVar1 == param_1)) &&
       (iVar1 = DAT_ffc5d0a8, iVar1 == param_1)) &&
      ((iVar1 = DAT_ffc5d0ac, iVar1 == param_1 && (iVar1 = DAT_ffc5d0b0, iVar1 == param_1)))) &&
     ((iVar1 = DAT_ffc5d0b4, iVar1 == param_1 &&
      ((iVar1 = DAT_ffc5d0b8, iVar1 == param_1 && (iVar1 = DAT_ffc5d0bc, iVar1 == param_1)))))) {
    return 1;
  }
  return 2;
}

uint32_t exercise_icus_register_patterns_and_clear_8a3e2(void)

{
  uint32_t camry_r10_result;
  uint uVar1;
  int iVar2;
  
  iVar2 = (camry_r10_result = write_verify_d0e0_and_four_words_8a2e4((int)0xaaaaaaaa));
  if ((((iVar2 == 1) && (iVar2 = (camry_r10_result = write_verify_d0e0_and_four_words_8a2e4(0x55555555)), iVar2 == 1)) &&
      (iVar2 = (camry_r10_result = write_verify_icusparam_and_four_words_8a332((int)0xaaaaaaaa)), iVar2 == 1)) &&
     ((iVar2 = (camry_r10_result = write_verify_icusparam_and_four_words_8a332(0x55555555)), iVar2 == 1 &&
      (iVar2 = (camry_r10_result = write_verify_eight_d0a0_words_8a378((int)0xaaaaaaaa)), iVar2 == 1)))) {
    (camry_r10_result = write_verify_eight_d0a0_words_8a378(0x55555555));
  }
  uVar1 = DAT_ffc5d0e0;
  DAT_ffc5d0e0 = uVar1 & 0xfffffffe;
  DAT_ffc5d0f0 = 0;
  DAT_ffc5d0f4 = 0;
  DAT_ffc5d0f8 = 0;
  DAT_ffc5d0fc = 0;
  return camry_r10_result;
}

void fill_constant_block_8a450(void)

{
  DAT_febf131c = 0;
  DAT_febf1320 = 0;
  DAT_febf1324 = 0;
  DAT_febf1328 = 0;
  DAT_febf132c = 0;
  DAT_febf1330 = 0;
  DAT_febf1334 = 0;
  DAT_febf1338 = 0;
  DAT_febf133c = 0;
  DAT_febf1340 = 0;
  DAT_febf1344 = 0;
  DAT_febf1348 = 0;
  DAT_febf134c = 0;
  DAT_febf136d = 0;
  DAT_febf1360 = 0xffffffff;
  DAT_febf1364 = 0xffffffff;
  DAT_febf1368 = 0xffffffff;
  DAT_febf1350 = 0xffffffff;
  DAT_febf1354 = 0xffffffff;
  DAT_febf1358 = 0xffffffff;
  DAT_febf135c = 0xffffffff;
  return;
}

void configure_icus_control_and_clear_words_8a4a8(void)

{
  uint uVar1;
  
  uVar1 = DAT_ffc5d0e0;
  DAT_ffc5d0e0 = uVar1 & 0xfffffffe;
  DAT_ffc5d0f0 = 0;
  DAT_ffc5d0f4 = 0;
  DAT_ffc5d0f8 = 0;
  DAT_ffc5d0fc = 0;
  DAT_ffc5d0c0 = 0x600;
  ICUSCTL = 3;
  DAT_ffc5d0e4 = 1;
  return;
}

int initialize_icus_unless_irq_pending_8a4ce(void)

{
  uint uVar1;
  uint32_t puVar2;
  char cVar3;
  int iVar4;
  
  cVar3 = DAT_febf136c;
  puVar2 = 0xfebeb800u;
  uVar1 = ICUSIRQSTS;
  if ((uVar1 & 1) == 0) {
    puVar2 = 0xfebeb800u;
    iVar4 = abort_busy_icus_and_wait_ready_8a26a();
    if ((iVar4 == 1) && ((cVar3 != '\0' || (iVar4 = exercise_icus_register_patterns_and_clear_8a3e2(), iVar4 == 1)))) {
      fill_constant_block_8a450();
      configure_icus_control_and_clear_words_8a4a8();
      cVar3 = -0x1f;
    }
  }
  else {
    iVar4 = 0x30;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x5b6c))))) = cVar3;
  return iVar4;
}

void write_four_words_to_icusdat_8a514(uint *param_1)

{
  ICUSDAT = *param_1;
  ICUSDAT = param_1[1];
  ICUSDAT = param_1[2];
  ICUSDAT = param_1[3];
  return;
}

undefined4 feed_next_validated_icus_input_block_8a538(void)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  uint32_t puVar4;
  uVar3 = DAT_febf1350;
  uVar2 = DAT_febf1340;
  uVar1 = DAT_febf1330;
  puVar4 = 0xfebeb800u;
  ICUSCTL = 1;
  if (~DAT_febf1340 == DAT_febf1350) {
    if (DAT_febf1330 < DAT_febf132c) {
      write_four_words_to_icusdat_8a514(((uint *)camry_host_ptr((uint32_t)(DAT_febf1340))));
      (*((uint *)camry_host_ptr((uint32_t)(puVar4 + 0x5b40)))) = uVar2 + 0x10;
      (*((uint *)camry_host_ptr((uint32_t)(puVar4 + 0x5b50)))) = uVar3 - 0x10;
      (*((uint *)camry_host_ptr((uint32_t)(puVar4 + 0x5b30)))) = uVar1 + 1;
      return 0;
    }
  }
  else {
    DAT_febf136d = 1;
  }
  return 0x12;
}

void read_four_words_from_icusout_8a58a(uint *param_1)

{
  uint uVar1;
  
  uVar1 = ICUSOUT;
  *param_1 = uVar1;
  uVar1 = ICUSOUT;
  param_1[1] = uVar1;
  uVar1 = ICUSOUT;
  param_1[2] = uVar1;
  uVar1 = ICUSOUT;
  param_1[3] = uVar1;
  return;
}

undefined4 drain_next_validated_icus_output_block_8a5ae(void)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  uint32_t puVar4;
  uVar3 = DAT_febf1354;
  uVar2 = DAT_febf1344;
  uVar1 = DAT_febf1338;
  puVar4 = 0xfebeb800u;
  ICUSCTL = 2;
  if (~DAT_febf1344 == DAT_febf1354) {
    if (DAT_febf1338 < DAT_febf1334) {
      read_four_words_from_icusout_8a58a(((uint *)camry_host_ptr((uint32_t)(DAT_febf1344))));
      (*((uint *)camry_host_ptr((uint32_t)(puVar4 + 0x5b44)))) = uVar2 + 0x10;
      (*((uint *)camry_host_ptr((uint32_t)(puVar4 + 0x5b54)))) = uVar3 - 0x10;
      (*((uint *)camry_host_ptr((uint32_t)(puVar4 + 0x5b38)))) = uVar1 + 1;
      return 0;
    }
  }
  else {
    DAT_febf136d = 1;
  }
  return 0x12;
}

undefined4 prepare_icus_command_one_or_three_8a63c(undefined4 *param_1)

{
  ICUS_Status IVar1;
  uint uVar2;
  undefined4 uVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  uint *puVar7;
  uint uVar8;
  
  if (DAT_febf136c == '\0') {
    return 0x10;
  }
  if (((camry_host_addr((param_1))!= 0) && (puVar7 = ((uint *)camry_host_ptr((uint32_t)(*param_1))),camry_host_addr((puVar7))!= 0)) &&
     (((uint32_t)(param_1[1]))!=camry_host_addr((((uint *)0x0))))) {
    uVar8 = puVar7[1];
    uVar6 = puVar7[3];
    if ((((uVar8 != 0) && (puVar7[2] < 0xf)) &&
        ((uVar4 = *puVar7, uVar4 != 0 && (uVar5 = (*((uint *)camry_host_ptr((uint32_t)(param_1[1])))), uVar5 != 0)))) &&
       ((uVar6 == 0 || (uVar6 == 1)))) {
      if (uVar6 == 0) {
        uVar6 = 1;
      }
      else {
        uVar6 = 3;
      }
      uVar3 = 2;
      if (((((int8_t)DAT_febf136c) == -0x1f) && (IVar1.raw = ICUSSTS, IVar1.BUSY == 0)) &&
         (uVar2 = ICUSSTS2, (uVar2 & 3) == 0)) {
        DAT_febf1350 = ~uVar4;
        uVar3 = 0;
        ICUSPARAM = uVar8;
        DAT_febf131c = 0x8a538u;
        DAT_febf1354 = ~uVar5;
        DAT_febf1360 = 0xfff75ac7;
        DAT_febf1330 = 0;
        DAT_febf1364 = 0xfff75a51;
        DAT_febf1338 = 0;
        DAT_febf1368 = 0xfff759ff;
        DAT_febf1320 = 0x8a5aeu;
        DAT_febf1324 = ((uint32_t)(0x8a600u));
        DAT_febf136c = -0x2e;
        DAT_febf1328 = uVar6;
        DAT_febf132c = uVar8;
        DAT_febf1334 = uVar8;
        DAT_febf1340 = uVar4;
        DAT_febf1344 = uVar5;
      }
      ICUSCMD = (uint32_t)(uVar6 | puVar7[2] << 0x10);
      return uVar3;
    }
  }
  return 0x11;
}

undefined4 prepare_icus_command_five_with_bit_length_8a720(undefined4 *param_1)

{
  ICUS_Status IVar1;
  uint uVar2;
  uint uVar3;
  undefined4 uVar4;
  uint uVar5;
  uint uVar6;
  uint *puVar7;
  
  if (DAT_febf136c == '\0') {
    return 0x10;
  }
  if (((camry_host_addr((param_1))!= 0) && (puVar7 = ((uint *)camry_host_ptr((uint32_t)(*param_1))),camry_host_addr((puVar7))!= 0)) &&
     ((uint32_t)(param_1[1] )!= 0)) {
    uVar3 = puVar7[1];
    if (((puVar7[2] < 0xf) && ((uVar5 = *puVar7, uVar5 != 0 || (uVar3 == 0)))) &&
       (uVar6 = (*((uint *)camry_host_ptr((uint32_t)(param_1[1])))), uVar6 != 0)) {
      uVar4 = 2;
      if (((((int8_t)DAT_febf136c) == -0x1f) && (IVar1.raw = ICUSSTS, IVar1.BUSY == 0)) &&
         (uVar2 = ICUSSTS2, (uVar2 & 3) == 0)) {
        DAT_febf132c = 0x2000000;
        if (uVar3 < 0xffffff81) {
          DAT_febf132c = uVar3 + 0x7f >> 7;
        }
        DAT_febf1334 = 1;
        DAT_febf1350 = ~uVar5;
        uVar4 = 0;
        DAT_febf1330 = 0;
        DAT_febf1354 = ~uVar6;
        DAT_febf1328 = 5;
        ICUSDAT = 0;
        DAT_febf131c = 0x8a538u;
        ICUSDAT = uVar3 >> 0x18 | uVar3 >> 8 & 0xff00 | (uVar3 & 0xff00) << 8 | uVar3 << 0x18;
        DAT_febf1360 = 0xfff75ac7;
        ICUSDAT = 0;
        DAT_febf1364 = 0xfff75a51;
        DAT_febf1338 = 0;
        DAT_febf1368 = 0xfff759ff;
        ICUSDAT = 0;
        DAT_febf1320 = 0x8a5aeu;
        DAT_febf1324 = ((uint32_t)(0x8a600u));
        DAT_febf136c = -0x2e;
        DAT_febf1340 = uVar5;
        DAT_febf1344 = uVar6;
      }
      ICUSCMD = (uint32_t)(puVar7[2] << 0x10 | 5);
      return uVar4;
    }
  }
  return 0x11;
}

undefined4 feed_icus_blocks_with_special_final_block_8a832(void)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  uint32_t puVar4;
  uint uVar5;
  
  uVar3 = DAT_febf1350;
  uVar2 = DAT_febf1340;
  uVar1 = DAT_febf1330;
  puVar4 = 0xfebeb800u;
  ICUSCTL = 1;
  if ((~DAT_febf1340 == DAT_febf1350) && (~DAT_febf1348 == DAT_febf1358)) {
    if (DAT_febf1330 < DAT_febf132c) {
      uVar5 = DAT_febf1348;
      if (DAT_febf1330 != DAT_febf132c - 1) {
        uVar5 = DAT_febf1340;
      }
      write_four_words_to_icusdat_8a514(((uint *)camry_host_ptr((uint32_t)(uVar5))));
      (*((uint *)camry_host_ptr((uint32_t)(puVar4 + 0x5b40)))) = uVar2 + 0x10;
      (*((uint *)camry_host_ptr((uint32_t)(puVar4 + 0x5b50)))) = uVar3 - 0x10;
      (*((uint *)camry_host_ptr((uint32_t)(puVar4 + 0x5b30)))) = uVar1 + 1;
      return 0;
    }
  }
  else {
    DAT_febf136d = 1;
  }
  return 0x12;
}

undefined4 read_icus_block_and_store_first_word_8a898(void)

{
  uint uVar1;
  undefined4 *puVar2;
  uint32_t puVar3;
  undefined4 local_1c [4];
  
  puVar2 = ((void *)camry_host_ptr((uint32_t)(DAT_febf1344)));
  uVar1 = DAT_febf1338;
  puVar3 = 0xfebeb800u;
  ICUSCTL = 2;
  if (~(uint)DAT_febf1344 == DAT_febf1354) {
    if (DAT_febf1338 < DAT_febf1334) {
      read_four_words_from_icusout_8a58a(local_1c);
      *puVar2 = local_1c[0];
      (*((uint *)camry_host_ptr((uint32_t)(puVar3 + 0x5b38)))) = uVar1 + 1;
      return 0;
    }
  }
  else {
    DAT_febf136d = 1;
  }
  return 0x12;
}

undefined4 prepare_icus_command_seven_with_final_block_8a8e4(int *param_1)

{
  ICUS_Status IVar1;
  uint *puVar2;
  uint uVar3;
  undefined4 uVar4;
  uint uVar5;
  uint uVar6;
  uint uVar7;
  uint uVar8;
  
  if (DAT_febf136c == '\0') {
    return 0x10;
  }
  if (((camry_host_addr((param_1))!= 0) && (puVar2 = ((uint *)camry_host_ptr((uint32_t)(*param_1))),camry_host_addr((puVar2))!= 0)) &&
     (uVar5 = param_1[1], uVar5 != 0)) {
    uVar3 = puVar2[1];
    if ((((puVar2[4] < 0xf) && (puVar2[3] < 0x80)) &&
        ((uVar6 = *puVar2, uVar6 != 0 || (uVar3 == 0)))) && (uVar7 = puVar2[2], uVar7 != 0)) {
      IVar1.raw = ICUSSTS;
      uVar4 = 2;
      uVar8 = ICUSSTS2;
      if (((((int8_t)DAT_febf136c) == -0x1f) && (IVar1.BUSY == 0)) && ((uVar8 & 3) == 0)) {
        uVar8 = 0x2000000;
        if (uVar3 < 0xffffff81) {
          uVar8 = uVar3 + 0x7f >> 7;
        }
        ICUSDAT = 0;
        DAT_febf1334 = 1;
        DAT_febf132c = uVar8 + 1;
        ICUSDAT = uVar3 >> 0x18 | uVar3 >> 8 & 0xff00 | (uVar3 & 0xff00) << 8 | uVar3 << 0x18;
        DAT_febf1350 = ~uVar6;
        DAT_febf1338 = 0;
        DAT_febf1358 = ~uVar7;
        DAT_febf1330 = 0;
        DAT_febf1354 = ~uVar5;
        DAT_febf1328 = 7;
        DAT_febf131c = 0x8a832u;
        DAT_febf1320 = 0x8a898u;
        DAT_febf1360 = 0xfff757cd;
        ICUSDAT = puVar2[3];
        DAT_febf1364 = 0xfff75767;
        DAT_febf1324 = ((uint32_t)(0x8a600u));
        DAT_febf1368 = 0xfff759ff;
        ICUSDAT = 0;
        DAT_febf136c = -0x2e;
        uVar4 = 0;
        DAT_febf1340 = uVar6;
        DAT_febf1344 = uVar5;
        DAT_febf1348 = uVar7;
      }
      ICUSCMD = (uint32_t)(puVar2[4] << 0x10 | 7);
      return uVar4;
    }
  }
  return 0x11;
}

void read_fhve3_and_fhve15_if_nonnull_8aa04(uint *param_1)

{
  uint uVar1;
  
  if (camry_host_addr((param_1))!= 0) {
    uVar1 = camry_read32(0xfff82410u);
    *param_1 = uVar1;
    uVar1 = camry_read32(0xfff8a430u);
    param_1[1] = uVar1;
  }
  return;
}

void write_fhve3_and_fhve15_bit_zero_8aa1c(uint *param_1)

{
  uint uVar1;
  
  if (camry_host_addr((param_1))!= 0) {
    camry_write32(0xfff82410u, *param_1 & 1);
    camry_write32(0xfff8a430u, param_1[1] & 1);
    uVar1 = camry_read32(0xfff8a430u);
    thunk_synchronize_instruction_execution_8b060();
  }
  return;
}

void set_fhve3_and_fhve15_bit_zero_8aa4a(void)

{
  uint local_c[2];
  
  local_c[0] = 0;
  local_c[1] = 0;
  read_fhve3_and_fhve15_if_nonnull_8aa04(local_c);
  local_c[0] = local_c[0] | 1;
  local_c[1] = local_c[1] | 1;
  write_fhve3_and_fhve15_bit_zero_8aa1c(local_c);
  return;
}

undefined4 prepare_icus_command_eight_four_in_three_out_8aa6a(uint *param_1)

{
  ICUS_Status IVar1;
  uint uVar2;
  uint32_t puVar3;
  undefined4 uVar4;
  uint uVar5;
  uint uVar6;
  
  puVar3 = 0xfebeb800u;
  if (DAT_febf136c == '\0') {
    uVar4 = 0x10;
  }
  else if (((camry_host_addr((param_1))== 0) || (uVar6 = *param_1, uVar6 == 0)) ||
          (uVar5 = param_1[1], uVar5 == 0)) {
    uVar4 = 2;
  }
  else {
    uVar4 = 2;
    if (((((int8_t)DAT_febf136c) == -0x1f) && (IVar1.raw = ICUSSTS, IVar1.BUSY == 0)) &&
       (uVar2 = ICUSSTS2, (uVar2 & 3) == 0)) {
      set_fhve3_and_fhve15_bit_zero_8aa4a();
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar3 + 0x5b2c)))) = 4;
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar3 + 0x5b34)))) = 3;
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar3 + 0x5b30)))) = 0;
      (*((uint *)camry_host_ptr((uint32_t)(puVar3 + 0x5b50)))) = ~uVar6;
      uVar4 = 0;
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar3 + 0x5b38)))) = 0;
      (*((uint *)camry_host_ptr((uint32_t)(puVar3 + 0x5b54)))) = ~uVar5;
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar3 + 0x5b28)))) = 8;
      (*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar3 + 0x5b1c)))) = 0x8a538u;
      (*((uint *)camry_host_ptr((uint32_t)(puVar3 + 0x5b40)))) = uVar6;
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar3 + 0x5b60)))) = 0xfff75ac7;
      (*((uint *)camry_host_ptr((uint32_t)(puVar3 + 0x5b44)))) = uVar5;
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar3 + 0x5b64)))) = 0xfff75a51;
      (*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar3 + 0x5b20)))) = 0x8a5aeu;
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar3 + 0x5b68)))) = 0xfff759ff;
      (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(0x5b24) * 1u)))) = ((uint32_t)(0x8a600u));
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x5b6c))))) = 0xd2;
    }
    ICUSCMD = (uint32_t)0x8;
  }
  return uVar4;
}

undefined4 drain_icus_output_to_first_or_alternate_block_8ab82(void)

{
  uint uVar1;
  uint32_t puVar2;
  uint uVar3;
  
  uVar1 = DAT_febf1338;
  puVar2 = 0xfebeb800u;
  ICUSCTL = 2;
  if ((~DAT_febf1344 == DAT_febf1354) && (~DAT_febf134c == DAT_febf135c)) {
    if (DAT_febf1338 < DAT_febf1334) {
      uVar3 = DAT_febf1344;
      if (DAT_febf1338 != 0) {
        uVar3 = DAT_febf134c;
      }
      read_four_words_from_icusout_8a58a(((uint *)camry_host_ptr((uint32_t)(uVar3))));
      (*((uint *)camry_host_ptr((uint32_t)(puVar2 + 0x5b38)))) = uVar1 + 1;
      return 0;
    }
  }
  else {
    DAT_febf136d = 1;
  }
  return 0x12;
}

undefined4 request_abort_for_busy_icus_operation_8aca8(void)

{
  ICUS_Status IVar1;
  
  IVar1.raw = ICUSSTS;
  if (DAT_febf136c == '\0') {
    return 0x10;
  }
  if ((((int8_t)DAT_febf136c) != -0x1f) && (((int8_t)DAT_febf136c) != -0x3d)) {
    if (((int8_t)DAT_febf136c) != -0x2e) {
      return 2;
    }
    if (IVar1.BUSY != 0) {
      DAT_febf1320 = 0;
      DAT_febf131c = 0;
      ICUSCMD = (uint32_t)0x3f;
      DAT_febf1364 = 0xffffffff;
      DAT_febf1324 = ((uint32_t)(0x8a600u));
      DAT_febf1360 = 0xffffffff;
      DAT_febf1368 = 0xfff759ff;
      DAT_febf1328 = 0x3f;
      DAT_febf136c = 0xc3;
      return 0;
    }
  }
  return 1;
}

void write_twelve_icus_parameter_words_8ad16(undefined4 *param_1)

{
  DAT_ffc5d090 = *param_1;
  DAT_ffc5d094 = param_1[1];
  DAT_ffc5d098 = param_1[2];
  DAT_ffc5d09c = param_1[3];
  DAT_ffc5d0a0 = param_1[4];
  DAT_ffc5d0a4 = param_1[5];
  DAT_ffc5d0a8 = param_1[6];
  DAT_ffc5d0ac = param_1[7];
  DAT_ffc5d0b0 = param_1[8];
  DAT_ffc5d0b4 = param_1[9];
  DAT_ffc5d0b8 = param_1[10];
  DAT_ffc5d0bc = param_1[0xb];
  return;
}

uint encode_icus_error_bit_with_bit_nine_fallthrough_8ad7a(void)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  
  uVar1 = DAT_ffc5d010;
  uVar3 = 0;
  if ((uVar1 & 0xfff) != 0) {
    uVar2 = 0;
    do {
      if (((1 << (uVar2 & 0x1f) & uVar1 & 0xfff) != 0) && (uVar3 = uVar2 + 1 | 0x1000, uVar2 != 9))
      {
        return uVar3;
      }
      uVar2 = uVar2 + 1;
    } while (uVar2 < 0xc);
  }
  return uVar3;
}

undefined4 finish_icus_7000_or_7100_check_8ada8(void)

{
  ICUS_Command IVar1;
  int iVar2;
  undefined4 uVar3;
  uint32_t puVar4;
  int iVar5;
  
  iVar2 = DAT_febf133c;
  puVar4 = 0xfebeb800u;
  IVar1.raw = ICUSCMD;
  if ((((IVar1.raw & 0xffff) == 0x7000) && (DAT_febf133c == 1)) ||
     (((IVar1.raw & 0xffff) == 0x7100 && (DAT_febf133c == 2)))) {
    ICUSCTL = 3;
    iVar5 = encode_icus_error_bit_with_bit_nine_fallthrough_8ad7a();
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x5b6c))))) = 0xe1;
    uVar3 = 1;
    if (((iVar2 == 1) && (iVar5 != 0)) || ((iVar2 == 2 && (iVar5 != 0x100c)))) {
      uVar3 = 2;
    }
  }
  else {
    uVar3 = 0x12;
  }
  return uVar3;
}

void install_icus_parameter_check_completion_8ae02(undefined4 *param_1)

{
  DAT_febf131c = 0;
  DAT_febf1320 = 0;
  DAT_febf1360 = 0xffffffff;
  DAT_febf1328 = *param_1;
  DAT_febf1324 = 0x8ada8;
  DAT_febf1364 = 0xffffffff;
  DAT_febf1368 = 0xfff75257;
  return;
}

undefined4 load_icus_parameters_or_start_mode_check_8ae2e(undefined4 *param_1)

{
  ICUS_Status IVar1;
  uint uVar2;
  uint uVar3;
  uint32_t puVar4;
  undefined4 uVar5;
  uint *puVar6;
  ICUS_Command local_8;
  
  puVar4 = 0xfebeb800u;
  if (DAT_febf136c == '\0') {
    return 0x10;
  }
  if (((camry_host_addr((param_1))!= 0) && (puVar6 = ((uint *)camry_host_ptr((uint32_t)(*param_1))),camry_host_addr((puVar6))!= 0)) &&
     (param_1[1] == 0)) {
    uVar3 = *puVar6;
    if ((uVar3 < 3) && ((uVar3 != 0 || (puVar6[1] != 0)))) {
      local_8.CMD = 0;
      local_8.reserved_8_15 = 0;
      local_8.KEY_SLOT = 0;
      uVar5 = 2;
      if (uVar3 == 1) {
        local_8.CMD = 0;
        local_8.reserved_8_15 = 0x70;
        local_8.KEY_SLOT = 0;
      }
      if (uVar3 == 2) {
        local_8.CMD = 0;
        local_8.reserved_8_15 = 0x71;
        local_8.KEY_SLOT = 0;
      }
      if (((((int8_t)DAT_febf136c) == -0x1f) && (IVar1.raw = ICUSSTS, IVar1.BUSY == 0)) &&
         (uVar2 = ICUSSTS2, (uVar2 & 3) == 0)) {
        DAT_febf133c = uVar3;
        if (uVar3 == 0) {
          write_twelve_icus_parameter_words_8ad16((undefined4 *)camry_host_ptr((uint32_t)puVar6[1]));
          return 1;
        }
        install_icus_parameter_check_completion_8ae02(&local_8);
        uVar5 = 0;
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x5b6c))))) = 0xd2;
      }
      else if (uVar3 == 0) {
        return 2;
      }
      ICUSCMD = local_8.raw;
      return uVar5;
    }
  }
  return 0x11;
}

undefined4 validate_active_icus_command_low16_8aed6(uint param_1)

{
  ICUS_Command IVar1;
  
  IVar1.raw = ICUSCMD;
  if ((DAT_febf136c == '\0') || (((int8_t)DAT_febf136c) == -0x1f)) {
    return 0x10;
  }
  if ((((int8_t)DAT_febf136c) != -0x2e) && (((int8_t)DAT_febf136c) != -0x3d)) {
    return 2;
  }
  if ((IVar1.raw & 0xffff) != param_1) {
    return 0x12;
  }
  return 0;
}

int service_icus_feed_drain_and_completion_callbacks_8af10(void)

{
  ICUS_Status IVar1;
  uint uVar2;
  uint16_t EVar3;
  uint32_t pcVar4;
  uint32_t pcVar5;
  uint32_t pcVar6;
  uint uVar7;
  uint uVar8;
  uint uVar9;
  uint32_t puVar10;
  int iVar11;
  int iVar12;
  uint uVar13;
  uint uVar14;
  uint uVar15;
  
  uVar9 = DAT_febf1368;
  uVar8 = DAT_febf1364;
  uVar7 = DAT_febf1360;
  iVar12 = DAT_febf1328;
  pcVar6 = (uint32_t)((uint32_t)(DAT_febf1324));
  pcVar5 = (uint32_t)((uint32_t)(DAT_febf1320));
  pcVar4 = (uint32_t)((uint32_t)(DAT_febf131c));
  puVar10 = 0xfebeb800u;
  uVar15 = ~(uint)DAT_febf131c;
  uVar14 = ~(uint)DAT_febf1320;
  IVar1.raw = ICUSSTS;
  uVar13 = ~(uint)DAT_febf1324;
  uVar2 = ICUSSTS2;
  iVar11 = validate_active_icus_command_low16_8aed6(DAT_febf1328);
  if (iVar11 != 0) {
    return iVar11;
  }
  if (((uVar15 == uVar7) && (uVar14 == uVar8)) && (uVar13 == uVar9)) {
    if (IVar1.BUSY != 0) {
      if ((uVar2 & 1) != 0) {
        if ((uint32_t)(pcVar4) == 0u) {
          return 0;
        }
        iVar12 = (*(int (*)())camry_indirect((uint32_t)(pcVar4)))();
        return iVar12;
      }
      if ((uVar2 >> 1 & 1) == 0) {
        return 0;
      }
      if ((uint32_t)(pcVar5) == 0u) {
        return 0;
      }
      iVar12 = (*(int (*)())camry_indirect((uint32_t)(pcVar5)))();
      return iVar12;
    }
    if ((uVar2 >> 1 & 1) != 0) {
      if ((uint32_t)(pcVar6) == 0u) {
        return 0;
      }
      iVar12 = encode_icus_error_bit_with_bit_nine_fallthrough_8ad7a();
      if (iVar12 == 0x100a) {
        DAT_ffc5d0e4 = 1;
      }
      iVar12 = (*(int (*)())camry_indirect((uint32_t)(pcVar6)))();
      EVar3 = EIC292;
      EIC292 = (uint16_t)((ushort)EVar3 & 0xefff);
      EVar3 = EIC293;
      EIC293 = (uint16_t)((ushort)EVar3 & 0xefff);
      EVar3 = EIC293;
      thunk_synchronize_instruction_execution_8b060();
      return iVar12;
    }
    if ((iVar12 != 0xb) && (iVar12 != 0x3f)) {
      return 0;
    }
  }
  else {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar10 + (uint32_t)(0x5b6d))))) = 1;
  }
  return 0x12;
}

undefined4 get_icus_error_code_if_initialized_8afea(void)

{
  undefined4 uVar1;
  
  if (DAT_febf136c == '\0') {
    uVar1 = 0;
  }
  else {
    uVar1 = encode_icus_error_bit_with_bit_nine_fallthrough_8ad7a();
  }
  return uVar1;
}
