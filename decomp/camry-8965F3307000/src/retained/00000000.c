#include "common.h"

volatile uint32_t CDBCR;
volatile uint32_t ICCTRL;

void reset_vector(void)

{
  __synchronize();
  reset_context_and_startup();
  return;
}

void boot_eiint_vector(void)

{
  __synchronize();
  boot_eiint_context();
  return;
}

void boot_eiint_context(void)

{
  uint camry_saved_eipc = camry_SR[0][0];
  uint uVar1;
  uint uVar2;
  uint uVar3;
  undefined4 in_r6 = 0x11111111;
  uint extraout_r6;
  undefined4 in_r7 = 0x11111111;
  undefined4 extraout_r7;
  undefined4 in_r8 = 0x11111111;
  undefined4 extraout_r8;
  undefined4 in_r9 = 0x11111111;
  undefined4 extraout_r9;
  uint in_EIPSW = camry_SR[0][1];
  uint uVar4;
  uint in_FPEC = camry_SR[0][11];
  uint in_EIIC = camry_SR[0][13];
  uint in_RBASE = camry_SR[1][2];
  uint in_EBASE = camry_SR[1][3];
  uint in_FPIPR = camry_SR[1][7];
  uint in_ISPR = camry_SR[2][10];
  uint in_INTCFG = camry_SR[2][13];
  
  uVar4 = camry_psw & 0xffffffd0;
  if ((in_FPEC & 1) != 0) {
    uVar1 = in_FPIPR & 0x1f;
    if (0xf < uVar1) {
      uVar1 = 0x10;
    }
    uVar2 = uVar1;
    if (0xf < uVar1) {
      uVar2 = 0xf;
    }
    uVar3 = PMR;
    if ((((uVar3 & 1 << uVar2) == 0) && ((in_ISPR & (1 << uVar1 + 1) - 1U & 0xffff) == 0)) &&
       ((camry_psw & 0x80) == 0)) {
      in_FPEC = 0;
      uVar4 = 0x40;
      uVar1 = in_EBASE;
      if ((camry_psw & 0x8000) == 0) {
        uVar1 = in_RBASE;
      }
      (*(int (*)())camry_indirect((uint32_t)((uVar1 & 0xfffffe00) + 0x70)))();
      in_EIIC = extraout_r6;
      in_r7 = extraout_r7;
      in_r8 = extraout_r8;
      in_r9 = extraout_r9;
    }
  }
  __enable_irq();
  boot_dispatch_eiic(in_EIIC);
  __disable_irq();
  camry_SR[0][0] = camry_saved_eipc;
  camry_SR[0][1] = in_EIPSW;
  if (((uVar4 >> 6 & 1) == 0) && ((in_INTCFG & 1) == 0)) {
    in_ISPR = in_ISPR & in_ISPR - 1;
    camry_SR[2][10] = in_ISPR;
  }
  camry_psw = in_EIPSW;
  camry_SR[2][12] &= ~2u;
  if ((in_FPEC & 1) != 0) {
    uint camry_fpi_priority = in_FPIPR & 31u;
    if (camry_fpi_priority > 15u) camry_fpi_priority = 15u;
    camry_SR[2][12] |= ((camry_pmr >> camry_fpi_priority) & 1u) << 1;
    uVar4 = in_FPIPR & 0x1f;
    if (0xf < uVar4) {
      uVar4 = 0x10;
    }
    uVar1 = uVar4;
    if (0xf < uVar4) {
      uVar1 = 0xf;
    }
    uVar2 = PMR;
    if ((((uVar2 & 1 << uVar1) == 0) && ((in_ISPR & (1 << uVar4 + 1) - 1U & 0xffff) == 0)) &&
       ((in_EIPSW & 0xa0) == 0)) {
      if (((in_EIPSW & 0xbfffffbf) >> 0xf & 1) == 0) {
        in_EBASE = in_RBASE;
      }
      (*(int (*)())camry_indirect((uint32_t)((in_EBASE & 0xfffffe00) + 0x70)))(in_r6,in_r7,in_r8,in_r9);
    }
  }
  camry_psw = camry_SR[0][1];
    return;
}

void reset_context_and_startup(void)

{
  camry_gpr[1] = camry_gpr[2] = 0;
  for (uint32_t reg = 6; reg < 32; ++reg) camry_gpr[reg] = 0;
  camry_gpr[3] = 0xfebe8000u;
  camry_gpr[4] = 0xfebf9800u;
  camry_gpr[5] = 0x869cu;
  camry_gpr_export_aliases();
  camry_psw = 0x18020u;
  camry_SR[0][0] = 0;
  camry_SR[0][2] = 0;
  camry_SR[0][13] = 0;
  camry_SR[0][14] = 0;
  camry_SR[0][16] = 0;
  camry_SR[0][17] = 0;
  camry_SR[0][20] = 0;
  camry_SR[0][28] = 0;
  camry_SR[0][29] = 0;
  camry_SR[1][4] = 0;
  camry_SR[1][11] = 0;
  camry_SR[1][12] = 0;
  camry_SR[2][6] = 0;
  camry_SR[2][7] = 0;
  camry_SR[2][8] = 0;
  camry_SR[5][0] = 0;
  camry_SR[0][1] = camry_SR[0][3] = 0x18020u;
  camry_SR[1][0] = 0x20004u;
  camry_SR[1][5] = 0x80000002u;
  uint uVar1;
  uint uVar2;
  undefined4 uVar3;
  uint uVar4;
  int iVar5;
  short sVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  int iVar10;
  int iVar11;
  undefined1 uVar12;
  undefined4 *puVar13;
  uint uVar14;
  uint uVar15;
  uint in_FPEC = camry_SR[0][11];
  uint in_RBASE = camry_SR[1][2];
  uint in_FPIPR = camry_SR[1][7];
  uint in_ISPR = camry_SR[2][10];
  
  __disable_irq();
  if ((in_FPEC & 1) != 0) {
    uVar3 = PMR;
  }
  __synchronize();
  __synchronize();
  __synchronize();
  __synchronize();
  __synchronize();
  __synchronize();
  __synchronize();
  __synchronize();
  __synchronize();
  __synchronize();
  __synchronize();
  __synchronize();
  __synchronize();
  __synchronize();
  camry_SR[1][3] = 1;
  __synchronize();
  __synchronize();
  __synchronize();
  __synchronize();
  __synchronize();
  __synchronize();
  __synchronize();
  ICCTRL = 0x10002;
  __synchronize();
  PMR = 0xffff;
  if ((in_FPEC & 1) != 0) {
    uVar3 = PMR;
  }
  __synchronize();
  __synchronize();
  __synchronize();
  sVar6 = Ramffc2000c;
  uVar14 = (uint)(((uint)(int)sVar6 >> 4 & 1) != 0) << 3 | 0x18020;
  if (((bool)((byte)(uVar14 >> 3) & 1)) || ((bool)((byte)(uVar14 >> 3) & 1))) {
    sVar6 = Ramffc2000c;
    uVar14 = (uint)(((uint)(int)sVar6 >> 4 & 1) != 0) << 3 | 0x18020;
    if ((bool)((byte)(uVar14 >> 3) & 1)) goto LAB_00000744;
  }
  uVar15 = ECMMESSTR2;
  uVar1 = ECMCESSTR2;
  uVar15 = uVar14 & 0xfffffff4 | (uint)((uVar15 >> 0x13 & 1) != 0) << 3;
  if (((bool)((byte)(uVar15 >> 3) & 1)) ||
     (uVar15 = uVar14 & 0xfffffff4 | (uint)((uVar1 >> 0x13 & 1) != 0) << 3,
     (bool)((byte)(uVar15 >> 3) & 1))) {
    uVar14 = ECMMESSTR2;
    uVar1 = ECMCESSTR2;
    if (((uVar14 >> 0x13 & 1) == 0) &&
       (uVar15 = uVar15 & 0xfffffff4 | (uint)((uVar1 >> 0x13 & 1) != 0) << 3,
       !(bool)((byte)(uVar15 >> 3) & 1))) goto LAB_00000320;
    ECMPCMD1 = 0xa5;
    ECMESSTC2 = 0x80000;
    ECMESSTC2 = 0xfff7ffff;
    ECMESSTC2 = 0x80000;
    uVar3 = (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xffd62044u))));
    __synchronize();
  }
  else {
LAB_00000320:
    iVar5 = Ramffcda000;
    iVar7 = Ramffcda004;
    iVar8 = Ramffcda008;
    iVar9 = Ramffcda010;
    iVar10 = Ramffcda014;
    iVar11 = Ramffcda018;
    uVar14 = uVar15 & 0xfffffff4 | (uint)(iVar5 == iVar9);
    if (((!(bool)((byte)uVar14 & 1)) ||
        (uVar14 = uVar15 & 0xfffffff0 | (uint)(iVar7 == iVar10), !(bool)((byte)uVar14 & 1))) ||
       (uVar14 = uVar15 & 0xfffffff0 | (uint)(iVar8 == iVar11), !(bool)((byte)uVar14 & 1))) {
      iVar5 = Ramffcda000;
      iVar7 = Ramffcda004;
      iVar8 = Ramffcda008;
      iVar9 = Ramffcda010;
      iVar10 = Ramffcda014;
      iVar11 = Ramffcda018;
      if (((iVar5 != iVar9) || (iVar7 != iVar10)) ||
         (uVar14 = uVar14 & 0xfffffff0 | (uint)(iVar8 == iVar11), !(bool)((byte)uVar14 & 1)))
      goto LAB_000006b0;
    }
    iVar5 = Ramffcda030;
    iVar7 = Ramffcda034;
    uVar15 = uVar14 & 0xfffffff0 | (uint)(iVar5 == 2);
    if ((!(bool)((byte)uVar15 & 1)) ||
       (uVar15 = uVar14 & 0xfffffff0 | (uint)(iVar7 == 1), !(bool)((byte)uVar15 & 1))) {
      iVar5 = Ramffcda030;
      iVar7 = Ramffcda034;
      if ((iVar5 != 2) ||
         (uVar15 = uVar15 & 0xfffffff0 | (uint)(iVar7 == 1), !(bool)((byte)uVar15 & 1)))
      goto LAB_000006b0;
    }
    uVar14 = ECMMESSTR2;
    uVar1 = ECMCESSTR2;
    uVar14 = uVar15 & 0xfffffff0 | (uint)((uVar14 >> 0x1b & 1) != 0) << 3;
    if (((bool)((byte)(uVar14 >> 3) & 1)) &&
       (uVar14 = uVar15 & 0xfffffff0 | (uint)((uVar1 >> 0x1b & 1) != 0) << 3,
       (bool)((byte)(uVar14 >> 3) & 1))) {
LAB_000003d8:
      ECMPCMD1 = 0xa5;
      ECMESSTC2 = 0x8000000;
      ECMESSTC2 = 0xf7ffffff;
      ECMESSTC2 = 0x8000000;
      uVar3 = (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xffd62044u))));
      __synchronize();
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfff82c1cu)))) = 0xb4;
      uVar12 = (*((volatile int8_t *)camry_host_ptr((uint32_t)(0xfff82c04u))));
      __synchronize();
      ICCTRL = 0x10102;
      __synchronize();
      do {
        uVar15 = camry_sample_icctrl();
        uVar14 = uVar14 & 0xfffffff4 | (uint)((uVar15 >> 8 & 1) != 0) << 3;
      } while ((bool)((byte)(uVar14 >> 3) & 1));
      __synchronize();
      ICCTRL = 0x30002;
      __synchronize();
      do {
        uVar15 = uVar14;
        ICCTRL = 0x30003;
        __synchronize();
        iVar5 = camry_sample_icctrl();
        uVar14 = uVar15 & 0xfffffff0 | (uint)(iVar5 == 0x30003);
      } while (!(bool)((byte)uVar14 & 1));
      CDBCR = 3;
      __synchronize();
      if ((in_FPEC & 1) != 0) {
        uVar1 = in_FPIPR & 0x1f;
        if (0xf < uVar1) {
          uVar1 = 0x10;
        }
        uVar2 = uVar1;
        if (0xf < uVar1) {
          uVar2 = 0xf;
        }
        uVar4 = PMR;
        if ((((uVar4 & 1 << uVar2) == 0) && ((in_ISPR & (1 << uVar1 + 1) - 1U & 0xffff) == 0)) &&
           ((uVar15 & 0xa0) == 0)) {
          in_FPEC = 0;
          uVar14 = uVar15 & 0xbfffff90 | 0x20;
          uVar1 = in_RBASE;
          if ((uVar15 >> 0xf & 1) != 0) {
            uVar1 = camry_SR[1][3];
          }
          (*(int (*)())camry_indirect((uint32_t)((uVar1 & 0xfffffe00) + 0x70)))();
        }
      }
      __synchronize();
      if ((((in_FPEC & 1) != 0) && (uVar15 = PMR, (uVar15 & 0x8000) == 0)) &&
         (((in_ISPR & 0xffff) == 0 && ((uVar14 & 0xa0) == 0)))) {
        if (((uVar14 & 0xbfffffbf) >> 0xf & 1) != 0) {
          in_RBASE = camry_SR[1][3];
        }
        (*(int (*)())camry_indirect((uint32_t)((in_RBASE & 0xfffffe00) + 0x70)))();
      }
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      __synchronize();
      puVar13 = (undefined4 *)((undefined *)camry_host_ptr(0xfebe7000u));
      do {
        *puVar13 = 0;
        puVar13 = puVar13 + 1;
      } while (camry_host_addr(puVar13)<((uint32_t)(0xfebe8000u)));
      boot_hardware_ram_init_and_select_image();
      do {
                    /* WARNING: Do nothing block with infinite loop */
      } while( true );
    }
    uVar15 = ECMMESSTR2;
    uVar1 = ECMCESSTR2;
    if (((uVar15 >> 0x1b & 1) != 0) &&
       (uVar14 = uVar14 & 0xfffffff4 | (uint)((uVar1 >> 0x1b & 1) != 0) << 3,
       (bool)((byte)(uVar14 >> 3) & 1))) goto LAB_000003d8;
  }
LAB_000006b0:
  uVar14 = Ramffc0a000;
  uVar15 = Ramffc0a004;
  uVar1 = Ramffc0a008;
  if ((uVar15 == (uVar14 ^ 0x55555555)) && (uVar1 == (uVar14 ^ 0xaaaaaaaa))) {
    uVar14 = Ramffc0a00c;
    Ramffc0a00c = uVar14 | 0x5a000000;
  }
  else {
    Ramffc0a000 = 0x5a5a5a5a;
    Ramffc0a004 = 0xf0f0f0f;
    Ramffc0a008 = 0xf0f0f0f0;
    Ramffc0a00c = 0x5a000000;
  }
LAB_00000744:
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}

void boot_dispatch_eiic(uint eiic)

{
  int iVar1;
  
  iVar1 = 0;
  while( true ) {
    if (((*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)((camry_tp + 0x0u) + (uint32_t)(iVar1) * (uint32_t)sizeof(F33BootInterruptEntry)) + (uint32_t)(0) * (uint32_t)sizeof(F33BootInterruptEntry) + (uint32_t)offsetof(F33BootInterruptEntry, eiic))))) == 0xffffffff) ||
       ((*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)((camry_tp + 0x0u) + (uint32_t)(iVar1) * (uint32_t)sizeof(F33BootInterruptEntry)) + (uint32_t)(0) * (uint32_t)sizeof(F33BootInterruptEntry) + (uint32_t)offsetof(F33BootInterruptEntry, eiic))))) == eiic)) break;
    iVar1 = iVar1 + 1;
  }
  (*(int (*)())camry_indirect((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)((camry_tp + 0x0u) + (uint32_t)(iVar1) * (uint32_t)sizeof(F33BootInterruptEntry)) + (uint32_t)(0) * (uint32_t)sizeof(F33BootInterruptEntry) + (uint32_t)offsetof(F33BootInterruptEntry, handler))))))))(eiic);
  return;
}

void enable_and_initialize_boot_diagnostics_770(void)

{
  boot_diagnostic_enable_from_handoff();
  boot_diagnostic_initialize_from_handoff();
  return;
}

void service_boot_diagnostic_timers_780(void)

{
  boot_diagnostic_timer_services();
  return;
}

void run_boot_diagnostic_foreground_78c(void)

{
  boot_diagnostic_foreground();
  return;
}

void return_only_stub_798(void)

{
  return;
}

void initialize_ffc604_and_ffc614_register_pairs_79a(void)

{
  undefined4 uVar1;
  
  Ramffc60408 = 3;
  Ramffc6040c = 3;
  Ramffc61408 = 1;
  Ramffc6140c = 1;
  uVar1 = Ramffc61450;
  __synchronize();
  return;
}

void configure_ffc654_registers_and_poll_7b6(void)

{
  undefined4 uVar1;
  int iVar2;
  
  camry_write32(0xffc65408u, (int)0xffffffff);
  camry_write32(0xffc6540cu, 0xf);
  uVar1 = camry_read32(0xffc6540cu);
  __synchronize();
  camry_write32(0xffc65604u, 0x4000);
  uVar1 = camry_read32(0xffc65604u);
  __synchronize();
  do {
    camry_write32(0xffc65400u, 0x4000);
    uVar1 = camry_read32(0xffc65400u);
    __synchronize();
    iVar2 = camry_read32(0xffc65400u);
  } while (iVar2 != 0);
  do {
    camry_write32(0xffc65404u, 2);
    uVar1 = camry_read32(0xffc65404u);
    __synchronize();
    iVar2 = camry_read32(0xffc65404u);
  } while (iVar2 != 2);
  return;
}

void initialize_codeflash_ecc_controls_and_poll_802(void)

{
  uint uVar1;
  
  camry_write32(0xffc62004u, 0xf);
  camry_write32(0xffc62008u, 1);
  uVar1 = camry_read32(0xffc62008u);
  __synchronize();
  camry_write32(0xffc622f0u, 0x4000);
  camry_write32(0xffc624f0u, 0x4000);
  uVar1 = camry_read32(0xffc624f0u);
  __synchronize();
  do {
    camry_write32(0xffc62100u, 0x4000);
    uVar1 = camry_read32(0xffc62100u);
    __synchronize();
    uVar1 = camry_read32(0xffc62100u);
  } while (uVar1 != 0);
  do {
    camry_write32(0xffc62200u, 0x4000);
    uVar1 = camry_read32(0xffc62200u);
    __synchronize();
    uVar1 = camry_read32(0xffc62200u);
  } while (uVar1 != 0);
  do {
    camry_write32(0xffc62400u, 0x4000);
    uVar1 = camry_read32(0xffc62400u);
    __synchronize();
    uVar1 = camry_read32(0xffc62400u);
  } while (uVar1 != 0);
  do {
    camry_write32(0xffc62000u, 6);
    uVar1 = camry_read32(0xffc62000u);
    __synchronize();
    uVar1 = camry_read32(0xffc62000u);
  } while (uVar1 != 6);
  return;
}

void configure_ffc5b0_registers_and_poll_zero_880(void)

{
  uint uVar1;
  undefined4 uVar2;
  
  camry_write32(0xffc5b008u, 1);
  uVar1 = camry_read32(0xffc5b008u);
  __synchronize();
  camry_write32(0xffc5b010u, 1);
  uVar2 = camry_read32(0xffc5b010u);
  __synchronize();
  camry_write32(0xffc5b01cu, 0x4000);
  uVar1 = camry_read32(0xffc5b01cu);
  __synchronize();
  do {
    camry_write32(0xffc5b000u, 0x4000);
    uVar1 = camry_read32(0xffc5b000u);
    __synchronize();
    uVar1 = camry_read32(0xffc5b000u);
  } while (uVar1 != 0);
  do {
    camry_write32(0xffc5b014u, 0);
    uVar1 = camry_read32(0xffc5b014u);
    __synchronize();
    uVar1 = camry_read32(0xffc5b014u);
  } while (uVar1 != 0);
  return;
}

void configure_ffc640_registers_and_poll_8c8(void)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  camry_write32(0xffc64004u, (int)0xffffffff);
  camry_write32(0xffc64008u, 1);
  uVar1 = camry_read32(0xffc64008u);
  __synchronize();
  camry_write32(0xffc64104u, 0x4000);
  uVar1 = camry_read32(0xffc64104u);
  __synchronize();
  camry_write32(0xffc64100u, 0x4000);
  camry_write32(0xffc64200u, 0x4000);
  camry_write32(0xffc64e00u, 0x4000);
  uVar1 = camry_read32(0xffc64e00u);
  __synchronize();
  iVar2 = camry_read32(0xffc64100u);
  iVar4 = camry_read32(0xffc64200u);
  iVar3 = camry_read32(0xffc64e00u);
  while (iVar2 != 0) {
    camry_write32(0xffc64100u, 0x4000);
    uVar1 = camry_read32(0xffc64100u);
    __synchronize();
    iVar2 = camry_read32(0xffc64100u);
  }
  while (iVar4 != 0) {
    camry_write32(0xffc64200u, 0x4000);
    uVar1 = camry_read32(0xffc64200u);
    __synchronize();
    iVar4 = camry_read32(0xffc64200u);
  }
  while (iVar3 != 0) {
    camry_write32(0xffc64e00u, 0x4000);
    uVar1 = camry_read32(0xffc64e00u);
    iVar3 = camry_read32(0xffc64e00u);
  }
  do {
    camry_write32(0xffc64000u, 0x22);
    uVar1 = camry_read32(0xffc64000u);
    __synchronize();
    iVar2 = camry_read32(0xffc64000u);
  } while (iVar2 != 0x22);
  return;
}

void configure_and_poll_multiple_register_banks_96e(void)

{
  undefined4 uVar1;
  int iVar2;
  
  camry_write32(0xffc62c08u, 1);
  camry_write32(0xffc62c00u, 0x4000);
  camry_write32(0xffc62c04u, 0x20);
  camry_write32(0xffc63408u, 1);
  camry_write32(0xffc63400u, 0x4000);
  camry_write32(0xffc63404u, 2);
  camry_write32(0xffc66008u, 1);
  camry_write32(0xffc66000u, 0x4000);
  camry_write32(0xffc66004u, 0x22);
  camry_write32(0xffc66408u, 1);
  camry_write32(0xffc66400u, 0x4000);
  camry_write32(0xffc66404u, 2);
  camry_write32(0xffc67008u, 1);
  camry_write32(0xffc67004u, 2);
  camry_write32(0xffc67408u, 1);
  camry_write32(0xffc67404u, 2);
  camry_write32(0xffc67808u, 1);
  camry_write32(0xffc67804u, 2);
  camry_write32(0xffc68408u, 1);
  camry_write32(0xffc68404u, 2);
  camry_write32(0xffc6a008u, 1);
  camry_write32(0xffc6a000u, 0x4000);
  camry_write32(0xffc6a004u, 2);
  camry_write32(0xffc6c008u, 1);
  camry_write32(0xffc6c000u, 0x4000);
  camry_write32(0xffc6c004u, 0x22);
  __synchronize();
  camry_write32(0xffddd808u, 1);
  camry_write32(0xffddd800u, 0x4000);
  camry_write32(0xffddd804u, 0x22);
  uVar1 = camry_read32(0xffddd804u);
  __synchronize();
  camry_write32(0xfff94808u, 1);
  camry_write32(0xfff94800u, 0x4000);
  camry_write32(0xfff94804u, 0x22);
  uVar1 = camry_read32(0xfff94804u);
  __synchronize();
  camry_write32(0xffc40808u, 1);
  camry_write32(0xffc40800u, 0x4000);
  camry_write32(0xffc40804u, 0x22);
  uVar1 = camry_read32(0xffc40804u);
  __synchronize();
  camry_write32(0xffff80a0u, 0x40000000);
  uVar1 = camry_read32(0xffff80a0u);
  __synchronize();
  iVar2 = camry_read32(0xffc62c00u);
  while (iVar2 != 0) {
    camry_write32(0xffc62c00u, 0x4000);
    iVar2 = camry_read32(0xffc62c00u);
    __synchronize();
  }
  iVar2 = camry_read32(0xffc62c04u);
  while (iVar2 != 0x20) {
    camry_write32(0xffc62c04u, 0x20);
    iVar2 = camry_read32(0xffc62c04u);
    __synchronize();
  }
  iVar2 = camry_read32(0xffc63400u);
  while (iVar2 != 0) {
    camry_write32(0xffc63400u, 0x4000);
    iVar2 = camry_read32(0xffc63400u);
    __synchronize();
  }
  iVar2 = camry_read32(0xffc63404u);
  while (iVar2 != 2) {
    camry_write32(0xffc63404u, 2);
    iVar2 = camry_read32(0xffc63404u);
    __synchronize();
  }
  iVar2 = camry_read32(0xffc66000u);
  while (iVar2 != 0) {
    camry_write32(0xffc66000u, 0x4000);
    iVar2 = camry_read32(0xffc66000u);
    __synchronize();
  }
  iVar2 = camry_read32(0xffc66004u);
  while (iVar2 != 0x22) {
    camry_write32(0xffc66004u, 0x22);
    iVar2 = camry_read32(0xffc66004u);
    __synchronize();
  }
  iVar2 = camry_read32(0xffc66400u);
  while (iVar2 != 0) {
    camry_write32(0xffc66400u, 0x4000);
    iVar2 = camry_read32(0xffc66400u);
    __synchronize();
  }
  iVar2 = camry_read32(0xffc66404u);
  while (iVar2 != 2) {
    camry_write32(0xffc66404u, 2);
    iVar2 = camry_read32(0xffc66404u);
    __synchronize();
  }
  iVar2 = camry_read32(0xffc67004u);
  while (iVar2 != 2) {
    camry_write32(0xffc67004u, 2);
    iVar2 = camry_read32(0xffc67004u);
    __synchronize();
  }
  iVar2 = camry_read32(0xffc67404u);
  while (iVar2 != 2) {
    camry_write32(0xffc67404u, 2);
    iVar2 = camry_read32(0xffc67404u);
    __synchronize();
  }
  iVar2 = camry_read32(0xffc67804u);
  while (iVar2 != 2) {
    camry_write32(0xffc67804u, 2);
    iVar2 = camry_read32(0xffc67804u);
    __synchronize();
  }
  iVar2 = camry_read32(0xffc68404u);
  while (iVar2 != 2) {
    camry_write32(0xffc68404u, 2);
    iVar2 = camry_read32(0xffc68404u);
    __synchronize();
  }
  iVar2 = camry_read32(0xffc6a000u);
  while (iVar2 != 0) {
    camry_write32(0xffc6a000u, 0x4000);
    iVar2 = camry_read32(0xffc6a000u);
    __synchronize();
  }
  iVar2 = camry_read32(0xffc6a004u);
  while (iVar2 != 2) {
    camry_write32(0xffc6a004u, 2);
    iVar2 = camry_read32(0xffc6a004u);
    __synchronize();
  }
  iVar2 = camry_read32(0xffc6c000u);
  while (iVar2 != 0) {
    camry_write32(0xffc6c000u, 0x4000);
    iVar2 = camry_read32(0xffc6c000u);
    __synchronize();
  }
  iVar2 = camry_read32(0xffc6c004u);
  while (iVar2 != 0x22) {
    camry_write32(0xffc6c004u, 0x22);
    iVar2 = camry_read32(0xffc6c004u);
    __synchronize();
  }
  iVar2 = camry_read32(0xffddd800u);
  while (iVar2 != 0) {
    camry_write32(0xffddd800u, 0x4000);
    iVar2 = camry_read32(0xffddd800u);
    __synchronize();
  }
  iVar2 = camry_read32(0xffddd804u);
  while (iVar2 != 0x22) {
    camry_write32(0xffddd804u, 0x22);
    iVar2 = camry_read32(0xffddd804u);
    __synchronize();
  }
  iVar2 = camry_read32(0xfff94800u);
  while (iVar2 != 0) {
    camry_write32(0xfff94800u, 0x4000);
    iVar2 = camry_read32(0xfff94800u);
    __synchronize();
  }
  iVar2 = camry_read32(0xfff94804u);
  while (iVar2 != 0x22) {
    camry_write32(0xfff94804u, 0x22);
    iVar2 = camry_read32(0xfff94804u);
    __synchronize();
  }
  iVar2 = camry_read32(0xffc40800u);
  while (iVar2 != 0) {
    camry_write32(0xffc40800u, 0x4000);
    iVar2 = camry_read32(0xffc40800u);
    __synchronize();
  }
  iVar2 = camry_read32(0xffc40804u);
  while (iVar2 != 0x22) {
    camry_write32(0xffc40804u, 0x22);
    iVar2 = camry_read32(0xffc40804u);
    __synchronize();
  }
  return;
}

void initialize_six_610_8000_register_pairs_c52(void)

{
  undefined4 uVar1;
  
  Ramffc71100 = 0x610;
  Ramffc71104 = 0x8000;
  uVar1 = Ramffc71104;
  __synchronize();
  Ramffc71200 = 0x610;
  Ramffc71204 = 0x8000;
  uVar1 = Ramffc71204;
  __synchronize();
  Ramffc70000 = 0x610;
  Ramffc70004 = 0x8000;
  uVar1 = Ramffc70004;
  __synchronize();
  Ramffc70040 = 0x610;
  Ramffc70044 = 0x8000;
  uVar1 = Ramffc70044;
  __synchronize();
  Ramffc70080 = 0x610;
  Ramffc70084 = 0x8000;
  uVar1 = Ramffc70084;
  __synchronize();
  Ramffc700c0 = 0x610;
  Ramffc700c4 = 0x8000;
  uVar1 = Ramffc700c4;
  __synchronize();
  return;
}

void load_tp_configuration_into_ffc1_ffc2_ffc3_banks_c9a(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  
  iVar5 = 0;
  do {
    iVar4 = iVar5 * 0x40;
    iVar2 = iVar5 + 1;
    (*((undefined2 *)camry_host_ptr((uint32_t)(iVar4 + -0x3ebffc)))) = 0;
    (*((undefined2 *)camry_host_ptr((uint32_t)(iVar4 + -0x3ec000)))) = 0;
    iVar1 = iVar5 + -5;
    (*((undefined2 *)camry_host_ptr((uint32_t)(iVar4 + -0x3efff0)))) = (*((volatile uint16_t *)camry_host_ptr((uint32_t)((camry_tp + 0x104u) + (uint32_t)((short)iVar5 * 0x18) * 2u))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(iVar4 + -0x3effec)))) = 0;
    (*((undefined2 *)camry_host_ptr((uint32_t)(iVar4 + -0x3ebff8)))) = 0;
    iVar5 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  DAT_ffc24004 = 0;
  DAT_ffc24000 = 0;
  DAT_ffc20010 = (char)(*((volatile uint16_t *)camry_host_ptr((uint32_t)((camry_tp + 0x224u)))));
  DAT_ffc20014 = 0;
  DAT_ffc34000 = 0;
  DAT_ffc34020 = 0;
  DAT_ffc34024 = 0;
  DAT_ffc34028 = 0;
  DAT_ffc3402c = 0;
  DAT_ffc34030 = 0;
  DAT_ffc34034 = 0;
  DAT_ffc34038 = 0;
  DAT_ffc3403c = 0;
  DAT_ffc34040 = 0;
  DAT_ffc34044 = 0;
  DAT_ffc34048 = 0;
  DAT_ffc3404c = 0;
  DAT_ffc34050 = 0;
  DAT_ffc34060 = 0;
  DAT_ffc34064 = 0;
  DAT_ffc34068 = 0;
  DAT_ffc3406c = 0;
  DAT_ffc34070 = 0;
  DAT_ffc34074 = 0;
  DAT_ffc34080 = 0;
  DAT_ffc34084 = 0;
  iVar5 = 0;
  do {
    iVar2 = iVar5 + 1;
    (*((undefined1 *)camry_host_ptr((uint32_t)(iVar5 * 0x100 + -0x3d0000)))) = 0;
    iVar1 = iVar5 + -0x2b;
    (*((undefined2 *)camry_host_ptr((uint32_t)(iVar5 * 0x100 + -0x3cfffc)))) = 0;
    iVar5 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  iVar5 = 0;
  do {
    iVar2 = iVar5 + 1;
    *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfff89120u + (uint32_t)(iVar5 * 8) * 1u)))) = 2;
    iVar1 = iVar5 + -0xc;
    iVar5 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  iVar5 = 0;
  do {
    iVar1 = (int)(short)iVar5;
    iVar2 = iVar5 * 0x40;
    (*((undefined2 *)camry_host_ptr((uint32_t)(iVar2 + -0x3ebff4)))) = (*((volatile uint16_t *)camry_host_ptr((uint32_t)((camry_tp + 0x106u) + (uint32_t)(iVar1 * 0x18) * 2u))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(iVar2 + -0x3ebff0)))) = (*((volatile uint16_t *)camry_host_ptr((uint32_t)((camry_tp + 0x108u) + (uint32_t)(iVar1 * 0x18) * 2u))));
    if (iVar5 != 5) {
      (*((undefined2 *)camry_host_ptr((uint32_t)(iVar2 + -0x3ebfd4)))) = (*((volatile uint16_t *)camry_host_ptr((uint32_t)((camry_tp + 0x10au) + (uint32_t)(iVar1 * 0x18) * 2u))));
    }
    iVar3 = iVar5 + 1;
    iVar4 = iVar5 + -5;
    (*((undefined4 *)camry_host_ptr((uint32_t)(iVar2 + -0x3ebfe8)))) = (*((volatile uint32_t *)camry_host_ptr((uint32_t)((camry_tp + 0x10cu) + (uint32_t)(iVar1 * 0xc) * 4u))));
    (*((undefined4 *)camry_host_ptr((uint32_t)(iVar2 + -0x3ebfd8)))) = (*((volatile uint32_t *)camry_host_ptr((uint32_t)((camry_tp + 0x110u) + (uint32_t)(iVar1 * 0xc) * 4u))));
    (*((undefined4 *)camry_host_ptr((uint32_t)(iVar2 + -0x3ebfec)))) = (*((volatile uint32_t *)camry_host_ptr((uint32_t)((camry_tp + 0x114u) + (uint32_t)(iVar1 * 0xc) * 4u))));
    (*((undefined4 *)camry_host_ptr((uint32_t)(iVar2 + -0x3ebfc4)))) = (*((volatile uint32_t *)camry_host_ptr((uint32_t)((camry_tp + 0x118u) + (uint32_t)(iVar1 * 0xc) * 4u))));
    (*((undefined4 *)camry_host_ptr((uint32_t)(iVar2 + -0x3effd0)))) = (*((volatile uint32_t *)camry_host_ptr((uint32_t)((camry_tp + 0x11cu) + (uint32_t)(iVar1 * 0xc) * 4u))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(iVar2 + -0x3effe8)))) = (*((volatile uint16_t *)camry_host_ptr((uint32_t)((camry_tp + 0x120u) + (uint32_t)(iVar1 * 0x18) * 2u))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(iVar2 + -0x3effe4)))) = (*((volatile uint16_t *)camry_host_ptr((uint32_t)((camry_tp + 0x122u) + (uint32_t)(iVar1 * 0x18) * 2u))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(iVar2 + -0x3effd8)))) = (*((volatile uint16_t *)camry_host_ptr((uint32_t)((camry_tp + 0x124u) + (uint32_t)(iVar1 * 0x18) * 2u))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(iVar2 + -0x3ebff8)))) = (*((volatile uint16_t *)camry_host_ptr((uint32_t)((camry_tp + 0x126u) + (uint32_t)(iVar1 * 0x18) * 2u))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(iVar2 + -0x3f0000)))) = (*((volatile uint16_t *)camry_host_ptr((uint32_t)((camry_tp + 0x128u) + (uint32_t)(iVar1 * 0x18) * 2u))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(iVar2 + -0x3effec)))) = (*((volatile uint16_t *)camry_host_ptr((uint32_t)((camry_tp + 0x12au) + (uint32_t)(iVar1 * 0x18) * 2u))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(iVar2 + -0x3efff0)))) = (*((volatile uint16_t *)camry_host_ptr((uint32_t)((camry_tp + 0x12cu) + (uint32_t)(iVar1 * 0x18) * 2u))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(iVar2 + -0x3ec000)))) = (*((volatile uint16_t *)camry_host_ptr((uint32_t)((camry_tp + 0x12eu) + (uint32_t)(iVar1 * 0x18) * 2u))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(iVar2 + -0x3ebffc)))) = *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)((camry_tp + 0x130u) + (uint32_t)(iVar1 * 0x30) * 1u))));
    iVar5 = iVar3;
  } while (((iVar4 < 0) || (iVar3 < 0)));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffc2400cu)))) = (char)(*((volatile uint16_t *)camry_host_ptr((uint32_t)((camry_tp + 0x226u)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffc24010u)))) = (char)(*((volatile uint16_t *)camry_host_ptr((uint32_t)((camry_tp + 0x228u)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffc2402cu)))) = (char)(*((volatile uint16_t *)camry_host_ptr((uint32_t)((camry_tp + 0x22au)))));
  Ramffc24018 = (*((volatile int32_t *)camry_host_ptr((uint32_t)((camry_tp + 0x22cu)))));
  Ramffc24028 = (*((volatile int32_t *)camry_host_ptr((uint32_t)((camry_tp + 0x230u)))));
  Ramffc24014 = (*((volatile int32_t *)camry_host_ptr((uint32_t)((camry_tp + 0x234u)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffc2001cu)))) = (char)(*((volatile uint16_t *)camry_host_ptr((uint32_t)((camry_tp + 0x242u)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffc20000u)))) = (char)(*((volatile uint16_t *)camry_host_ptr((uint32_t)((camry_tp + 0x248u)))));
  DAT_ffc20014 = (char)(*((volatile uint16_t *)camry_host_ptr((uint32_t)((camry_tp + 0x24au)))));
  DAT_ffc20010 = (char)(*((volatile uint16_t *)camry_host_ptr((uint32_t)((camry_tp + 0x24cu)))));
  DAT_ffc24000 = (char)(*((volatile uint16_t *)camry_host_ptr((uint32_t)((camry_tp + 0x24eu)))));
  DAT_ffc24004 = (char)(*((volatile uint16_t *)camry_host_ptr((uint32_t)((camry_tp + 0x250u)))));
  return;
}

void snapshot_validated_ecm_status_and_clear_errors_e54(void)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  uchar uVar4;
  
  uVar1 = Ramffc0a000;
  DAT_febffc00 = 0;
  uVar2 = Ramffc0a004;
  DAT_febffc04 = 0;
  DAT_febffc08 = 0;
  DAT_febffc0c = 0;
  DAT_febffc10 = 0;
  DAT_febffc14 = 0;
  uVar3 = Ramffc0a008;
  if ((uVar2 == (uVar1 ^ 0x55555555)) && (uVar3 == (uVar1 ^ 0xaaaaaaaa))) {
    DAT_febffc00 = ECMMESSTR0;
    DAT_febffc04 = ECMCESSTR0;
    DAT_febffc08 = ECMMESSTR1;
    DAT_febffc0c = ECMCESSTR1;
    DAT_febffc10 = ECMMESSTR2;
    DAT_febffc14 = ECMCESSTR2;
  }
  ECMPCMD1 = 0xa5;
  ECMESSTC0 = 0xffffffff;
  ECMESSTC0 = 0;
  ECMESSTC0 = 0xffffffff;
  uVar4 = ECMPS;
  __synchronize();
  ECMPCMD1 = 0xa5;
  ECMESSTC1 = 0xffffffff;
  ECMESSTC1 = 0;
  ECMESSTC1 = 0xffffffff;
  uVar4 = ECMPS;
  __synchronize();
  ECMPCMD1 = 0xa5;
  ECMESSTC2 = 0x7fffffff;
  ECMESSTC2 = 0x80000000;
  ECMESSTC2 = 0x7fffffff;
  uVar4 = ECMPS;
  __synchronize();
  DAT_febffc80 = DAT_febffc00 ^ 0x55555555;
  DAT_febffc84 = DAT_febffc04 ^ 0x55555555;
  DAT_febffc88 = DAT_febffc08 ^ 0x55555555;
  DAT_febffc8c = DAT_febffc0c ^ 0x55555555;
  DAT_febffc90 = DAT_febffc10 ^ 0x55555555;
  DAT_febffd00 = DAT_febffc00 ^ 0xaaaaaaaa;
  DAT_febffd0c = DAT_febffc0c ^ 0xaaaaaaaa;
  DAT_febffc94 = DAT_febffc14 ^ 0x55555555;
  DAT_febffd04 = DAT_febffc04 ^ 0xaaaaaaaa;
  DAT_febffd08 = DAT_febffc08 ^ 0xaaaaaaaa;
  DAT_febffd10 = DAT_febffc10 ^ 0xaaaaaaaa;
  DAT_febffd14 = DAT_febffc14 ^ 0xaaaaaaaa;
  return;
}

void configure_ecm_masks_and_clear_error_outputs_f80(void)

{
  uchar uVar1;
  uint uVar2;
  uint uVar3;
  byte bVar4;
  
  ECMPEM = 3;
  ECMPCMD1 = 0xa5;
  ECMEMK0 = 0xffffffe1;
  ECMEMK0 = 0x1e;
  ECMEMK0 = 0xffffffe1;
  uVar1 = ECMPS;
  ECMPCMD1 = 0xa5;
  uVar2 = 0;
  ECMEMK1 = 0xffffffff;
  ECMEMK1 = 0;
  ECMEMK1 = 0xffffffff;
  uVar1 = ECMPS;
  ECMPCMD1 = 0xa5;
  ECMEMK2 = 0x3fffffff;
  ECMEMK2 = 0xc0000000;
  ECMEMK2 = 0x3fffffff;
  uVar1 = ECMPS;
  ECMPCMD1 = 0xa5;
  ECMMICFG0 = 0;
  ECMMICFG0 = 0xffffffff;
  ECMMICFG0 = 0;
  uVar1 = ECMPS;
  ECMPCMD1 = 0xa5;
  ECMMICFG1 = 0;
  ECMMICFG1 = 0xffffffff;
  ECMMICFG1 = 0;
  uVar1 = ECMPS;
  ECMPCMD1 = 0xa5;
  ECMMICFG2 = 0;
  ECMMICFG2 = 0xffffffff;
  ECMMICFG2 = 0;
  uVar1 = ECMPS;
  ECMPCMD1 = 0xa5;
  ECMNMICFG0 = 0;
  ECMNMICFG0 = 0xffffffff;
  ECMNMICFG0 = 0;
  uVar1 = ECMPS;
  ECMPCMD1 = 0xa5;
  ECMNMICFG1 = 0;
  ECMNMICFG1 = 0xffffffff;
  ECMNMICFG1 = 0;
  uVar1 = ECMPS;
  ECMPCMD1 = 0xa5;
  ECMNMICFG2 = 0;
  ECMNMICFG2 = 0xffffffff;
  ECMNMICFG2 = 0;
  uVar1 = ECMPS;
  ECMPCMD1 = 0xa5;
  ECMIRCFG0 = 0;
  ECMIRCFG0 = 0xffffffff;
  ECMIRCFG0 = 0;
  uVar1 = ECMPS;
  ECMPCMD1 = 0xa5;
  ECMIRCFG1 = 0;
  ECMIRCFG1 = 0xffffffff;
  ECMIRCFG1 = 0;
  uVar1 = ECMPS;
  ECMPCMD1 = 0xa5;
  ECMIRCFG2 = 0;
  ECMIRCFG2 = 0xffffffff;
  ECMIRCFG2 = 0;
  uVar1 = ECMPS;
  __synchronize();
  ECMMPCMD0 = 0xa5;
  ECMMECLR = '\x01';
  ECMMECLR = 0xfe;
  ECMMECLR = '\x01';
  uVar1 = ECMPS;
  __synchronize();
  bVar4 = 0;
  do {
    uVar3 = 0x80000000;
    if ((int)uVar2 < 0) break;
    uVar2 = ECMMESSTR2;
    bVar4 = bVar4 + 1;
  } while (bVar4 < 0x1f);
  ECMCPCMD0 = 0xa5;
  ECMCECLR = '\x01';
  ECMCECLR = 0xfe;
  ECMCECLR = '\x01';
  uVar1 = ECMPS;
  __synchronize();
  bVar4 = 0;
  do {
    if (-1 < (int)uVar3) break;
    uVar3 = ECMCESSTR2;
    bVar4 = bVar4 + 1;
  } while (bVar4 < 0x1f);
  ECMPEM = 0;
  __synchronize();
  return;
}
