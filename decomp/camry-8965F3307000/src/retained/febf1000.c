#include "common.h"

void boot_relocated_8370(int param_1)
{
  uint32_t slot = 0xfebf0f00u;
  uint32_t key;
  camry_write32((camry_sp - 4u) & ~3u, camry_gpr[29]);
  camry_write32((camry_sp - 8u) & ~3u, camry_gpr[31]);
  camry_sp -= 8u;
  camry_gpr[3] = camry_sp;
  camry_gpr[1] = 0;
  for (;;) {
    key = camry_read32(slot);
    if (key == 0xffffffffu || key == (uint32_t)param_1) break;
    slot += 8u;
    camry_gpr[1] += 1u;
  }
  camry_gpr[19] = key;
  camry_gpr[30] = slot;
  camry_gpr[29] = camry_read32(slot + 4u);
  camry_gpr[6] = (uint32_t)param_1;
  camry_gpr[31] = 0xfebf1026u;
  camry_gpr[10] = ((uint32_t (*)(uint32_t, uint32_t, uint32_t, uint32_t))
      camry_indirect(camry_gpr[29]))
      (camry_gpr[6], camry_gpr[7], camry_gpr[8], camry_gpr[9]);
  if (camry_halted) return;
  camry_gpr[31] = camry_read32(camry_sp & ~3u);
  camry_gpr[29] = camry_read32((camry_sp + 4u) & ~3u);
  camry_sp += 8u;
  camry_gpr[3] = camry_sp;
  return;
}

void boot_relocated_84f8(uint param_1)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  uint in_FPEC = camry_SR[0][11];
  uint in_RBASE = camry_SR[1][2];
  uint in_FPIPR = camry_SR[1][7];
  uint in_ISPR = camry_SR[2][10];
  
  if ((camry_psw & 0x20) == 0) {
    __disable_irq();
    camry_SR[1][3] = param_1 | 1;
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
      uVar3 = PMR;
      if ((((uVar3 & 1 << uVar2) == 0) && ((in_ISPR & (1 << uVar1 + 1) - 1U & 0xffff) == 0)) &&
         ((camry_psw & 0x80) == 0)) {
        if (((camry_psw & 0xbfffffd0) >> 0xf & 1) != 0) {
          in_RBASE = camry_SR[1][3];
        }
        (*(int (*)())camry_indirect((uint32_t)((in_RBASE & 0xfffffe00) + 0x70)))();
      }
    }
    __enable_irq();
  }
  else {
    camry_SR[1][3] = param_1 | 1;
    __synchronize();
  }
  return;
}

uint boot_relocated_851c(int param_1)

{
  uint uVar1;
  uint uVar2;
  int iVar3;
  undefined4 uVar4;
  uint uVar5;
  uint in_FPEC = camry_SR[0][11];
  uint in_RBASE = camry_SR[1][2];
  uint in_FPIPR = camry_SR[1][7];
  uint in_ISPR = camry_SR[2][10];
  
  iVar3 = PMR;
  if (iVar3 - param_1 < 0 != (iVar3 < 0 != param_1 < 0 && param_1 < 0 == iVar3 - param_1 < 0)) {
    if ((camry_psw & 0x20) == 0) {
      __disable_irq();
      PMR = param_1;
      if ((in_FPEC & 1) != 0) {
        uVar4 = PMR;
      }
      if ((in_FPEC & 1) != 0) {
        uVar1 = in_FPIPR & 0x1f;
        if (0xf < uVar1) {
          uVar1 = 0x10;
        }
        uVar2 = uVar1;
        if (0xf < uVar1) {
          uVar2 = 0xf;
        }
        uVar5 = PMR;
        if ((((uVar5 & 1 << uVar2) == 0) && ((in_ISPR & (1 << uVar1 + 1) - 1U & 0xffff) == 0)) &&
           ((camry_psw & 0x80) == 0)) {
          if (((camry_psw & 0xbfffffd0) >> 0xf & 1) != 0) {
            in_RBASE = camry_SR[1][3];
          }
          (*(int (*)())camry_indirect((uint32_t)((in_RBASE & 0xfffffe00) + 0x70)))();
        }
      }
      __enable_irq();
    }
    else {
      PMR = param_1;
      if ((in_FPEC & 1) != 0) {
        uVar1 = in_FPIPR & 0x1f;
        if (0xf < uVar1) {
          uVar1 = 0x10;
        }
        uVar2 = uVar1;
        if (0xf < uVar1) {
          uVar2 = 0xf;
        }
        uVar5 = PMR;
        if ((((uVar5 & 1 << uVar2) == 0) && ((in_ISPR & (1 << uVar1 + 1) - 1U & 0xffff) == 0)) &&
           ((camry_psw & 0xa0) == 0)) {
          if (((camry_psw & 0xbfffffb0) >> 0xf & 1) != 0) {
            in_RBASE = camry_SR[1][3];
          }
          (*(int (*)())camry_indirect((uint32_t)((in_RBASE & 0xfffffe00) + 0x70)))();
        }
      }
    }
    __synchronize();
  }
  return iVar3;
}

void boot_relocated_8542(undefined4 param_1)

{
  uint uVar1;
  uint uVar2;
  undefined4 uVar3;
  uint uVar4;
  uint in_FPEC = camry_SR[0][11];
  uint in_RBASE = camry_SR[1][2];
  uint in_FPIPR = camry_SR[1][7];
  uint in_ISPR = camry_SR[2][10];
  
  if ((camry_psw >> 5 & 1) == 0) {
    __disable_irq();
    PMR = param_1;
    if ((in_FPEC & 1) != 0) {
      uVar3 = PMR;
    }
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
         ((camry_psw & 0x80) == 0)) {
        if (((camry_psw & 0xbfffffd0) >> 0xf & 1) != 0) {
          in_RBASE = camry_SR[1][3];
        }
        (*(int (*)())camry_indirect((uint32_t)((in_RBASE & 0xfffffe00) + 0x70)))();
      }
    }
    __enable_irq();
  }
  else {
    PMR = param_1;
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
         ((camry_psw & 0xa0) == 0)) {
        if (((camry_psw & 0xbfffffb0) >> 0xf & 1) != 0) {
          in_RBASE = camry_SR[1][3];
        }
        (*(int (*)())camry_indirect((uint32_t)((in_RBASE & 0xfffffe00) + 0x70)))();
      }
    }
  }
  __synchronize();
  return;
}

undefined4 boot_relocated_8560(int *param_1,uint param_2)

{
  uint uVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  int *piVar5;
  
  uVar3 = boot_relocated_851c(0xffff);
  boot_relocated_84f8((int)((uint32_t)(0xfebf102cu)));
  camry_write32(0xffc62400u, 0x4001);
  camry_write32(0xffc62200u, 0x4001);
  uVar4 = 0;
  uVar1 = camry_read32(0xffc62200u);
  __synchronize();
  __synchronize();
  piVar5 = param_1;
  for (iVar2 = 0;
      (int)(iVar2 - param_2) < 0 !=
      (iVar2 < 0 != (int)param_2 < 0 && (int)param_2 < 0 == (int)(iVar2 - param_2) < 0);
      iVar2 = iVar2 + 1) {
    if (*piVar5 != -1) {
      uVar4 = 1;
      goto LAB_F33BootFlashDriver__febf128a;
    }
    piVar5 = piVar5 + 1;
  }
  camry_write32(0xffc624f0u, 0x4001);
  camry_write32(0xffc622f0u, 0x4001);
  uVar1 = camry_read32(0xffc622f0u);
  __synchronize();
  __synchronize();
  param_2 = param_2 >> 2;
  do {
    if (param_2 == 0) {
LAB_F33BootFlashDriver__febf1272:
      camry_write32(0xffc624f0u, 0x4000);
      camry_write32(0xffc622f0u, 0x4000);
      uVar1 = camry_read32(0xffc622f0u);
      __synchronize();
      __synchronize();
LAB_F33BootFlashDriver__febf128a:
      camry_write32(0xffc62400u, 0x4000);
      camry_write32(0xffc62200u, 0x4000);
      uVar1 = camry_read32(0xffc62200u);
      __synchronize();
      __synchronize();
      boot_relocated_84f8(0);
      boot_relocated_8542(uVar3);
      return uVar4;
    }
    if (*param_1 != 0x3ff) {
      uVar4 = 1;
      goto LAB_F33BootFlashDriver__febf1272;
    }
    param_1 = param_1 + 4;
    param_2 = param_2 - 1;
  } while( true );
}

void boot_relocated_8628(void)

{
  uint uVar1;
  undefined1 uVar2;
  undefined4 uVar3;
  
  uVar3 = boot_relocated_851c(0xffff);
  boot_relocated_84f8((int)((uint32_t)(0xfebf102cu)));
  (*((volatile uint8_t *)camry_host_ptr(0xffc59008u))) = 1;
  uVar2 = (*((volatile uint8_t *)camry_host_ptr(0xffc59008u)));
  __synchronize();
  __synchronize();
  SELFID0 = (*((volatile int32_t *)camry_host_ptr(0xff300050u)));
  SELFID1 = (*((volatile int32_t *)camry_host_ptr(0xff300054u)));
  SELFID2 = (*((volatile int32_t *)camry_host_ptr(0xff300058u)));
  SELFID3 = (*((volatile int32_t *)camry_host_ptr(0xff30005cu)));
  uVar1 = SELFID3;
  __synchronize();
  (*((volatile uint8_t *)camry_host_ptr(0xffc59008u))) = 0;
  uVar2 = (*((volatile uint8_t *)camry_host_ptr(0xffc59008u)));
  __synchronize();
  __synchronize();
  boot_relocated_84f8(0);
  boot_relocated_8542(uVar3);
  return;
}
