#include "common.h"

undefined4 update_total_and_event11_counters_checked_71014(char param_1,undefined2 *param_2,ushort *param_3)

{
  ushort uVar1;
  ushort uVar2;
  
  if ((camry_host_addr((param_2))== 0) || (camry_host_addr((param_3))== 0)) {
    return 0xffff;
  }
  if (param_1 == 'D') {
    param_2[5] = 0;
    param_2[8] = 0;
  }
  else {
    uVar1 = param_2[8];
    uVar2 = param_3[1];
    if ((uVar2 < uVar1) || (param_2[8] = uVar1 + 1, uVar2 < (ushort)(uVar1 + 1))) {
      return 0x44;
    }
    if (param_1 == '\x11') {
      uVar1 = param_2[5];
      uVar2 = *param_3;
      if ((uVar1 <= uVar2) && (param_2[5] = uVar1 + 1, (ushort)(uVar1 + 1) <= uVar2)) {
        return 0x44000022;
      }
      *param_2 = 0;
      param_2[1] = 0;
      param_2[2] = 0;
      param_2[4] = 0;
      param_2[5] = 0;
      param_2[6] = 0;
      param_2[8] = 0;
      return 0;
    }
  }
  return 0x22;
}

undefined4 update_event11_event22_counters_and_peak_71086(char param_1,undefined2 *param_2,ushort *param_3)

{
  short sVar1;
  ushort uVar2;
  ushort uVar3;
  
  if ((camry_host_addr((param_2))== 0) || (camry_host_addr((param_3))== 0)) {
    return 0xffff;
  }
  if (param_1 != '\x11') {
    if (param_1 != '\"') {
      if (param_1 != 'D') {
        return 0x22;
      }
      param_2[5] = 0;
      param_2[6] = 0;
      return 0x22;
    }
    uVar3 = param_2[6];
    uVar2 = param_3[1];
    if (uVar3 <= uVar2) {
      sVar1 = uVar3 + 1;
      uVar3 = uVar3 + 1;
      param_2[6] = sVar1;
    }
    if ((ushort)param_2[7] < uVar3) {
      param_2[7] = uVar3;
    }
    if (uVar2 < uVar3) {
      return 0x44;
    }
    return 0x220022;
  }
  uVar3 = param_2[5];
  uVar2 = *param_3;
  if ((uVar3 <= uVar2) && (param_2[5] = uVar3 + 1, (ushort)(uVar3 + 1) <= uVar2)) {
    return 0x44000022;
  }
  *param_2 = 0;
  param_2[1] = 0;
  param_2[2] = 0;
  param_2[4] = 0;
  param_2[5] = 0;
  param_2[6] = 0;
  param_2[8] = 0;
  return 0;
}

undefined4 update_consecutive_event11_and_event22_peak_7110c(char param_1,undefined2 *param_2,ushort *param_3)

{
  short sVar1;
  ushort uVar2;
  ushort uVar3;
  
  if ((camry_host_addr((param_2))== 0) || (camry_host_addr((param_3))== 0)) {
    return 0xffff;
  }
  if (param_1 != '\x11') {
    if (param_1 != '\"') {
      if (param_1 != 'D') {
        return 0x22;
      }
      param_2[5] = 0;
      param_2[6] = 0;
      return 0x22;
    }
    param_2[5] = 0;
    uVar3 = param_2[6];
    uVar2 = param_3[1];
    if (uVar3 <= uVar2) {
      sVar1 = uVar3 + 1;
      uVar3 = uVar3 + 1;
      param_2[6] = sVar1;
    }
    if ((ushort)param_2[7] < uVar3) {
      param_2[7] = uVar3;
    }
    if (uVar2 < uVar3) {
      return 0x44;
    }
    return 0x220022;
  }
  uVar3 = param_2[5];
  uVar2 = *param_3;
  if ((uVar3 <= uVar2) && (param_2[5] = uVar3 + 1, (ushort)(uVar3 + 1) <= uVar2)) {
    return 0x44000022;
  }
  *param_2 = 0;
  param_2[1] = 0;
  param_2[2] = 0;
  param_2[4] = 0;
  param_2[5] = 0;
  param_2[6] = 0;
  param_2[8] = 0;
  return 0;
}

undefined4 update_total_and_consecutive_event_counters_with_peak_71194(char param_1,undefined2 *param_2,ushort *param_3)

{
  short sVar1;
  ushort uVar2;
  ushort uVar3;
  
  if ((camry_host_addr((param_2))== 0) || (camry_host_addr((param_3))== 0)) {
    return 0xffff;
  }
  if (param_1 == 'D') {
    param_2[5] = 0;
    param_2[8] = 0;
    param_2[6] = 0;
    return 0x22;
  }
  uVar3 = param_2[8];
  uVar2 = param_3[2];
  if ((uVar3 <= uVar2) && (param_2[8] = uVar3 + 1, (ushort)(uVar3 + 1) <= uVar2)) {
    if (param_1 == '\x11') {
      uVar3 = param_2[5];
      uVar2 = *param_3;
      if ((uVar3 <= uVar2) && (param_2[5] = uVar3 + 1, (ushort)(uVar3 + 1) <= uVar2)) {
        return 0x44000022;
      }
      *param_2 = 0;
      param_2[1] = 0;
      param_2[2] = 0;
      param_2[4] = 0;
      param_2[5] = 0;
      param_2[6] = 0;
      param_2[8] = 0;
      return 0;
    }
    if (param_1 != '\"') {
      return 0x22;
    }
    param_2[5] = 0;
    uVar3 = param_2[6];
    uVar2 = param_3[1];
    if (uVar3 <= uVar2) {
      sVar1 = uVar3 + 1;
      uVar3 = uVar3 + 1;
      param_2[6] = sVar1;
    }
    if ((ushort)param_2[7] < uVar3) {
      param_2[7] = uVar3;
    }
    if (uVar3 <= uVar2) {
      return 0x220022;
    }
  }
  return 0x44;
}

undefined4 update_event_counters_reset_event22_on_event11_71232(char param_1,undefined2 *param_2,ushort *param_3)

{
  short sVar1;
  ushort uVar2;
  ushort uVar3;
  
  if ((camry_host_addr((param_2))== 0) || (camry_host_addr((param_3))== 0)) {
    return 0xffff;
  }
  if (param_1 != '\x11') {
    if (param_1 != '\"') {
      if (param_1 != 'D') {
        return 0x22;
      }
      param_2[5] = 0;
      param_2[6] = 0;
      return 0x22;
    }
    uVar3 = param_2[6];
    uVar2 = param_3[1];
    if (uVar3 <= uVar2) {
      sVar1 = uVar3 + 1;
      uVar3 = uVar3 + 1;
      param_2[6] = sVar1;
    }
    if ((ushort)param_2[7] < uVar3) {
      param_2[7] = uVar3;
    }
    if (uVar2 < uVar3) {
      return 0x44;
    }
    return 0x220022;
  }
  param_2[6] = 0;
  uVar3 = param_2[5];
  uVar2 = *param_3;
  if ((uVar3 <= uVar2) && (param_2[5] = uVar3 + 1, (ushort)(uVar3 + 1) <= uVar2)) {
    return 0x44000022;
  }
  *param_2 = 0;
  param_2[1] = 0;
  param_2[2] = 0;
  param_2[4] = 0;
  param_2[5] = 0;
  param_2[6] = 0;
  param_2[8] = 0;
  return 0;
}

void save_registers_and_callt_state_to_ep_frame_712ce(undefined4 param_1, undefined4 param_2, undefined4 param_3, undefined4 param_4)
{
  camry_gpr_import_aliases();
  camry_gpr[6] = param_1;
  camry_gpr[7] = param_2;
  camry_gpr[8] = param_3;
  camry_gpr[9] = param_4;
  camry_write32(camry_gpr[30] + 100u, camry_gpr[19]);
  camry_write32(camry_gpr[30] + 96u, camry_gpr[18]);
  camry_write32(camry_gpr[30] + 92u, camry_gpr[17]);
  camry_write32(camry_gpr[30] + 88u, camry_gpr[16]);
  camry_write32(camry_gpr[30] + 84u, camry_gpr[15]);
  camry_write32(camry_gpr[30] + 80u, camry_gpr[14]);
  camry_write32(camry_gpr[30] + 76u, camry_gpr[13]);
  camry_write32(camry_gpr[30] + 72u, camry_gpr[12]);
  camry_write32(camry_gpr[30] + 68u, camry_gpr[11]);
  camry_write32(camry_gpr[30] + 64u, camry_gpr[10]);
  camry_write32(camry_gpr[30] + 60u, camry_gpr[9]);
  camry_write32(camry_gpr[30] + 56u, camry_gpr[8]);
  camry_write32(camry_gpr[30] + 52u, camry_gpr[7]);
  camry_write32(camry_gpr[30] + 48u, camry_gpr[6]);
  camry_write32(camry_gpr[30] + 36u, camry_gpr[2]);
  camry_gpr[1] = camry_SR[0][17];
  camry_write32(camry_gpr[30] + 16u, camry_gpr[1]);
  camry_gpr[1] = camry_SR[0][16];
  camry_write32(camry_gpr[30] + 12u, camry_gpr[1]);
  camry_gpr_export_aliases();
  return;
}

uint32_t restore_ep_exception_frame_and_eiret_71322(void)
{
  camry_gpr_import_aliases();
  camry_gpr[30] = camry_sp;
  camry_gpr[19] = camry_read32(camry_sp + 100u);
  camry_gpr[18] = camry_read32(camry_sp + 96u);
  camry_gpr[17] = camry_read32(camry_sp + 92u);
  camry_gpr[16] = camry_read32(camry_sp + 88u);
  camry_gpr[15] = camry_read32(camry_sp + 84u);
  camry_gpr[14] = camry_read32(camry_sp + 80u);
  camry_gpr[11] = camry_read32(camry_sp + 68u);
  camry_gpr[10] = camry_read32(camry_sp + 64u);
  camry_gpr[9] = camry_read32(camry_sp + 60u);
  camry_gpr[8] = camry_read32(camry_sp + 56u);
  camry_gpr[7] = camry_read32(camry_sp + 52u);
  camry_gpr[6] = camry_read32(camry_sp + 48u);
  camry_gpr[1] = camry_read32(camry_sp + 12u);
  camry_gpr[12] = camry_read32(camry_sp + 16u);
  camry_SR[0][16] = camry_gpr[1];
  camry_SR[0][17] = camry_gpr[12];
  __disable_irq();
  camry_gpr[1] = camry_read32(camry_sp);
  camry_gpr[12] = camry_read32(camry_sp + 20u);
  camry_gpr[13] = camry_read32(camry_sp + 24u);
  camry_SR[0][13] = camry_gpr[1];
  camry_SR[0][0] = camry_gpr[12];
  camry_SR[0][1] = camry_gpr[13];
  camry_gpr[13] = camry_read32(camry_sp + 76u);
  camry_gpr[12] = camry_read32(camry_sp + 72u);
  camry_gpr[1] = camry_read32(camry_sp + 32u);
  camry_gpr[30] = camry_read32(camry_sp + 28u);
  camry_gpr[31] = (uint32_t)(int32_t)(int16_t)camry_read16(camry_gpr[31]);
  camry_sp += camry_gpr[31];
  camry_gpr[31] = camry_read32(camry_sp);
  camry_sp += 4u;
  camry_gpr[3] = camry_sp;
  camry_gpr_export_aliases();
  if (!(camry_psw & 0x40u) && !(camry_SR[2][13] & 1u))
    camry_SR[2][10] &= camry_SR[2][10] - 1u;
  camry_psw = camry_SR[0][1];
  camry_gpr_import_aliases();
  camry_SR[2][12] &= ~2u;
  if ((camry_SR[0][11] & 1u) != 0) {
    uint32_t priority = camry_SR[1][7] & 31u;
    if (priority > 16u) priority = 16u;
    unsigned mask_priority = priority > 15u ? 15u : priority;
    uint32_t masked = (camry_pmr >> mask_priority) & 1u;
    camry_SR[2][12] |= masked << 1;
    if (!masked && !(camry_SR[2][10] & ((1u << (priority + 1u)) - 1u) & 0xffffu)
        && !(camry_psw & 0xa0u)) {
      uint32_t vector = (camry_SR[1][(camry_psw & 0x8000u) ? 3 : 2] & 0xfffffe00u) + 0x70u;
      camry_SR[0][11] = 0;
      camry_SR[0][0] = camry_SR[0][0];
      camry_SR[0][1] = camry_psw;
      camry_SR[0][13] = 0x72u;
      camry_psw = (camry_psw & 0xbfffffffu) | 0x60u;
      camry_gpr_export_aliases();
      camry_gpr[10] = ((uint32_t (*)(uint32_t, uint32_t, uint32_t, uint32_t))camry_indirect(vector))
          (camry_gpr[6], camry_gpr[7], camry_gpr[8], camry_gpr[9]);
      camry_gpr_import_aliases();
    }
  }
  camry_gpr_import_aliases();
  return camry_gpr[10];
}

uint32_t save_registers_switch_stack_apply_mpu_profile_71378(void)
{
  uint32_t cursor;
  unsigned int reg;
  camry_gpr_import_aliases();
  cursor = camry_gpr[3];
  for (reg = 1; reg <= 30; ++reg) {
    cursor -= 4u;
    camry_write32(cursor & ~3u, camry_gpr[reg]);
  }
  camry_gpr[3] = cursor;
  camry_gpr[2] = cursor;
  camry_gpr[3] = 0xfebe2800u;
  camry_gpr[20] = camry_gpr[31];
  camry_gpr[6] = camry_read8(0x31684u);
  camry_gpr[31] = 0x71394u;
  camry_gpr_export_aliases();
  apply_mpu_attribute_profile((uchar)camry_gpr[6]);
  camry_gpr[31] = camry_gpr[20];
  camry_gpr_export_aliases();
  return camry_gpr[10];
}

uint32_t apply_mpu_profile_restore_stack_and_registers_71398(void)
{
  uint32_t cursor;
  unsigned int reg;
  camry_gpr_import_aliases();
  camry_gpr[20] = camry_gpr[31];
  camry_gpr[6] = camry_read8(0x31683u);
  camry_gpr[31] = 0x713a6u;
  camry_gpr_export_aliases();
  apply_mpu_attribute_profile((uchar)camry_gpr[6]);
  cursor = camry_gpr[2];
  camry_gpr[31] = camry_gpr[20];
  for (reg = 30; reg != 0; --reg) {
    if (reg != 3) camry_gpr[reg] = camry_read32(cursor & ~3u);
    cursor += 4u;
  }
  camry_gpr[3] = cursor;
  camry_gpr_export_aliases();
  return camry_gpr[10];
}

void run_ch2_task_with_saved_exception_context_71508(void)
{
  uint32_t cursor;
  camry_gpr_import_aliases();
  __synchronize();
  camry_sp -= 28u;
  camry_write32(camry_sp + 24u, camry_gpr[10]);
  camry_gpr[10] = camry_SR[0][0];
  camry_write32(camry_sp + 20u, camry_gpr[10]);
  camry_gpr[10] = camry_SR[0][1];
  camry_write32(camry_sp + 16u, camry_gpr[10]);
  camry_gpr[10] = camry_SR[0][13];
  camry_write32(camry_sp + 12u, camry_gpr[10]);
  camry_gpr[10] = camry_SR[0][28];
  camry_write32(camry_sp + 8u, camry_gpr[10]);
  camry_gpr[10] = camry_SR[0][16];
  camry_write32(camry_sp + 4u, camry_gpr[10]);
  camry_gpr[10] = camry_SR[0][17];
  camry_write32(camry_sp + 0u, camry_gpr[10]);
  camry_psw = (camry_psw & ~15u) | 10u;
  __enable_irq();
  camry_gpr_import_aliases();
  camry_SR[2][12] &= ~2u;
  if ((camry_SR[0][11] & 1u) != 0) {
    uint32_t priority = camry_SR[1][7] & 31u;
    if (priority > 16u) priority = 16u;
    unsigned mask_priority = priority > 15u ? 15u : priority;
    uint32_t masked = (camry_pmr >> mask_priority) & 1u;
    camry_SR[2][12] |= masked << 1;
    if (!masked && !(camry_SR[2][10] & ((1u << (priority + 1u)) - 1u) & 0xffffu)
        && !(camry_psw & 0xa0u)) {
      uint32_t vector = (camry_SR[1][(camry_psw & 0x8000u) ? 3 : 2] & 0xfffffe00u) + 0x70u;
      camry_SR[0][11] = 0;
      camry_SR[0][0] = 0x71546u;
      camry_SR[0][1] = camry_psw;
      camry_SR[0][13] = 0x72u;
      camry_psw = (camry_psw & 0xbfffffffu) | 0x60u;
      camry_gpr_export_aliases();
      camry_gpr[10] = ((uint32_t (*)(uint32_t, uint32_t, uint32_t, uint32_t))camry_indirect(vector))
          (camry_gpr[6], camry_gpr[7], camry_gpr[8], camry_gpr[9]);
      camry_gpr_import_aliases();
    }
  }
  camry_gpr_import_aliases();
  cursor = camry_sp;
  for (unsigned reg = 1; reg <= 31; ++reg) {
    cursor -= 4u;
    camry_write32(cursor & ~3u, camry_gpr[reg]);
  }
  camry_sp = cursor;
  camry_gpr[31] = 0x7154eu;
  camry_gpr[10] = push_sixteen_mpu_attributes_65ac0();
  camry_gpr[31] = 0x7155au;
  apply_mpu_attribute_profile(camry_read8(0x31682u));
  camry_gpr[2] = camry_sp;
  camry_gpr[6] = 0xfebe0000u;
  camry_sp = camry_gpr[3] = 0xfebe1800u;
  camry_gpr[31] = 0x71568u;
  run_ch2_application_task();
  camry_sp = camry_gpr[2];
  camry_gpr[31] = 0x7156eu;
  camry_gpr[10] = pop_sixteen_mpu_attributes_65b4a();
  cursor = camry_sp;
  for (unsigned reg = 31; reg != 0; --reg) {
    if (reg != 3) camry_gpr[reg] = camry_read32(cursor & ~3u);
    cursor += 4u;
  }
  camry_gpr[3] = cursor;
  camry_gpr_export_aliases();
  __disable_irq();
  camry_gpr[10] = camry_read32(camry_sp + 0u);
  camry_SR[0][17] = camry_gpr[10];
  camry_gpr[10] = camry_read32(camry_sp + 4u);
  camry_SR[0][16] = camry_gpr[10];
  camry_gpr[10] = camry_read32(camry_sp + 8u);
  camry_SR[0][28] = camry_gpr[10];
  camry_gpr[10] = camry_read32(camry_sp + 12u);
  camry_SR[0][13] = camry_gpr[10];
  camry_gpr[10] = camry_read32(camry_sp + 16u);
  camry_SR[0][1] = camry_gpr[10];
  camry_gpr[10] = camry_read32(camry_sp + 20u);
  camry_SR[0][0] = camry_gpr[10];
  camry_gpr[10] = camry_read32(camry_sp + 24u);
  camry_sp += 28u;
  camry_gpr[3] = camry_sp;
  camry_gpr_export_aliases();
  if (!(camry_psw & 0x40u) && !(camry_SR[2][13] & 1u))
    camry_SR[2][10] &= camry_SR[2][10] - 1u;
  camry_psw = camry_SR[0][1];
  camry_gpr_import_aliases();
  camry_SR[2][12] &= ~2u;
  if ((camry_SR[0][11] & 1u) != 0) {
    uint32_t priority = camry_SR[1][7] & 31u;
    if (priority > 16u) priority = 16u;
    unsigned mask_priority = priority > 15u ? 15u : priority;
    uint32_t masked = (camry_pmr >> mask_priority) & 1u;
    camry_SR[2][12] |= masked << 1;
    if (!masked && !(camry_SR[2][10] & ((1u << (priority + 1u)) - 1u) & 0xffffu)
        && !(camry_psw & 0xa0u)) {
      uint32_t vector = (camry_SR[1][(camry_psw & 0x8000u) ? 3 : 2] & 0xfffffe00u) + 0x70u;
      camry_SR[0][11] = 0;
      camry_SR[0][0] = camry_SR[0][0];
      camry_SR[0][1] = camry_psw;
      camry_SR[0][13] = 0x72u;
      camry_psw = (camry_psw & 0xbfffffffu) | 0x60u;
      camry_gpr_export_aliases();
      camry_gpr[10] = ((uint32_t (*)(uint32_t, uint32_t, uint32_t, uint32_t))camry_indirect(vector))
          (camry_gpr[6], camry_gpr[7], camry_gpr[8], camry_gpr[9]);
      camry_gpr_import_aliases();
    }
  }
  camry_gpr_import_aliases();
  return;
}

void application_context_init(void)
{
  camry_SR[1][4] = 0x20200u;
  camry_SR[1][3] = 0x20000u;
  camry_gp = camry_gpr[4] = 0xfebeb800u;
  camry_tp = camry_gpr[5] = 0x23dfcu;
  camry_sp = camry_gpr[3] = 0xfebe2000u;
  camry_gpr[11] = 0x20000u;
  return;
}

void clear_fffee980_control_registers_715e0(void)

{
  undefined2 uVar1;
  
  Ramfffee982 = 0;
  Ramfffee988 = 0;
  Ramfffee980 = 0;
  uVar1 = Ramfffee980;
  __synchronize();
  __synchronize();
  return;
}

void clear_febf3401_under_sr26_sel6_control_71610(void)

{
  __synchronize();
  __synchronize();
  DAT_febf3401 = 0;
  __synchronize();
  __synchronize();
  return;
}

void clear_ecm_error_latches_once_or_terminate_7162e(void)

{
  uint uVar1;
  uchar uVar2;
  int iVar3;
  int iVar4;
  uint in_EIPSW = camry_SR[0][1];
  uint uVar5;
  uint uVar6;
  uint in_FPEC = camry_SR[0][11];
  uint in_RBASE = camry_SR[1][2];
  uint in_EBASE = camry_SR[1][3];
  uint in_FPIPR = camry_SR[1][7];
  uint in_ISPR = camry_SR[2][10];
  uint in_INTCFG = camry_SR[2][13];
  
  uVar5 = camry_psw & 0xfffffff0 | (uint)(DAT_febf3401 == 'Z');
  if (!(bool)((byte)uVar5 & 1)) {
    iVar3 = 8;
    do {
      iVar4 = 0x9b;
      do {
        uVar6 = uVar5;
        uVar5 = uVar6 & 0xfffffff0 | (uint)(iVar4 == 1);
        iVar4 = iVar4 + -1;
      } while (!(bool)((byte)uVar5 & 1));
      uVar5 = uVar6 & 0xfffffff0 | (uint)(iVar3 == 1);
      iVar3 = iVar3 + -1;
    } while (!(bool)((byte)uVar5 & 1));
    ECMPCMD1 = 0xa5;
    ECMESSTC0 = 0x1e;
    ECMESSTC0 = 0xffffffe1;
    ECMESSTC0 = 0x1e;
    __synchronize();
    uVar2 = ECMPS;
    uVar5 = uVar6 & 0xfffffff0 | (uint)(uVar2 == '\0');
    if (!(bool)((byte)uVar5 & 1)) {
      ECMPCMD1 = 0xa5;
      ECMESSTC0 = 0x1e;
      ECMESSTC0 = 0xffffffe1;
      ECMESSTC0 = 0x1e;
      __synchronize();
      uVar2 = ECMPS;
      uVar5 = uVar6 & 0xfffffff0 | (uint)(uVar2 == '\0');
      if (!(bool)((byte)uVar5 & 1)) {
        ECMPCMD1 = 0xa5;
        ECMESSTC0 = 0x1e;
        ECMESSTC0 = 0xffffffe1;
        ECMESSTC0 = 0x1e;
        __synchronize();
        uVar2 = ECMPS;
        uVar5 = uVar6 & 0xfffffff0 | (uint)(uVar2 == '\0');
        if (!(bool)((byte)uVar5 & 1)) goto LAB_00071ac4;
      }
    }
    ECMMPCMD0 = 0xa5;
    ECMMECLR = '\x01';
    ECMMECLR = 0xfe;
    ECMMECLR = '\x01';
    __synchronize();
    uVar2 = ECMPS;
    uVar6 = uVar5 & 0xfffffff0 | (uint)(uVar2 == '\0');
    if (!(bool)((byte)uVar6 & 1)) {
      ECMMPCMD0 = 0xa5;
      ECMMECLR = '\x01';
      ECMMECLR = 0xfe;
      ECMMECLR = '\x01';
      __synchronize();
      uVar2 = ECMPS;
      uVar6 = uVar5 & 0xfffffff0 | (uint)(uVar2 == '\0');
      if (!(bool)((byte)uVar6 & 1)) {
        ECMMPCMD0 = 0xa5;
        ECMMECLR = '\x01';
        ECMMECLR = 0xfe;
        ECMMECLR = '\x01';
        __synchronize();
        uVar2 = ECMPS;
        uVar6 = uVar5 & 0xfffffff0 | (uint)(uVar2 == '\0');
        if (!(bool)((byte)uVar6 & 1)) goto LAB_00071ac4;
      }
    }
    ECMCPCMD0 = 0xa5;
    ECMCECLR = '\x01';
    ECMCECLR = 0xfe;
    ECMCECLR = '\x01';
    __synchronize();
    uVar2 = ECMPS;
    uVar5 = uVar6 & 0xfffffff0 | (uint)(uVar2 == '\0');
    if (!(bool)((byte)uVar5 & 1)) {
      ECMCPCMD0 = 0xa5;
      ECMCECLR = '\x01';
      ECMCECLR = 0xfe;
      ECMCECLR = '\x01';
      __synchronize();
      uVar2 = ECMPS;
      uVar5 = uVar6 & 0xfffffff0 | (uint)(uVar2 == '\0');
      if (!(bool)((byte)uVar5 & 1)) {
        ECMCPCMD0 = 0xa5;
        ECMCECLR = '\x01';
        ECMCECLR = 0xfe;
        ECMCECLR = '\x01';
        __synchronize();
        uVar2 = ECMPS;
        uVar5 = uVar6 & 0xfffffff0 | (uint)(uVar2 == '\0');
        if (!(bool)((byte)uVar5 & 1)) goto LAB_00071ac4;
      }
    }
    ECMPCMD1 = 0xa5;
    ECMESSTC2 = 0x10000000;
    ECMESSTC2 = 0xefffffff;
    ECMESSTC2 = 0x10000000;
    __synchronize();
    uVar2 = ECMPS;
    uVar6 = uVar5 & 0xfffffff0 | (uint)(uVar2 == '\0');
    if (!(bool)((byte)uVar6 & 1)) {
      ECMPCMD1 = 0xa5;
      ECMESSTC2 = 0x10000000;
      ECMESSTC2 = 0xefffffff;
      ECMESSTC2 = 0x10000000;
      __synchronize();
      uVar2 = ECMPS;
      uVar6 = uVar5 & 0xfffffff0 | (uint)(uVar2 == '\0');
      if (!(bool)((byte)uVar6 & 1)) {
        ECMPCMD1 = 0xa5;
        ECMESSTC2 = 0x10000000;
        ECMESSTC2 = 0xefffffff;
        ECMESSTC2 = 0x10000000;
        __synchronize();
        uVar2 = ECMPS;
        uVar6 = uVar5 & 0xfffffff0 | (uint)(uVar2 == '\0');
        if (!(bool)((byte)uVar6 & 1)) goto LAB_00071ac4;
      }
    }
    DAT_febf3401 = 'Z';
    __synchronize();
    __synchronize();
    if (((uVar6 >> 6 & 1) == 0) && ((in_INTCFG & 1) == 0)) {
      in_ISPR = in_ISPR & in_ISPR - 1;
    camry_SR[2][10] = in_ISPR;
    }
    camry_psw = in_EIPSW;
  camry_SR[2][12] &= ~2u;
  if ((in_FPEC & 1) != 0) {
    uint camry_fpi_priority = in_FPIPR & 31u;
    if (camry_fpi_priority > 15u) camry_fpi_priority = 15u;
    camry_SR[2][12] |= ((camry_pmr >> camry_fpi_priority) & 1u) << 1;
      uVar5 = in_FPIPR & 0x1f;
      if (0xf < uVar5) {
        uVar5 = 0x10;
      }
      uVar6 = uVar5;
      if (0xf < uVar5) {
        uVar6 = 0xf;
      }
      uVar1 = PMR;
      if ((((uVar1 & 1 << uVar6) == 0) && ((in_ISPR & (1 << uVar5 + 1) - 1U & 0xffff) == 0)) &&
         ((in_EIPSW & 0xa0) == 0)) {
        if (((in_EIPSW & 0xbfffffbf) >> 0xf & 1) == 0) {
          in_EBASE = in_RBASE;
        }
        (*(int (*)())camry_indirect((uint32_t)((in_EBASE & 0xfffffe00) + 0x70)))();
      }
    }
    camry_psw = camry_SR[0][1];
    return;
  }
  Ramffc0a000 = 0x9b9b9b9b;
  Ramffc0a004 = 0xcececece;
  Ramffc0a008 = 0x31313131;
LAB_00071ac4:
  __synchronize();
  __synchronize();
                    /* WARNING: Subroutine does not return */
  enter_terminal_hardware_sequence();
}

void dispatch_ecm_status_exception_71ae4(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  uint uVar1;
  uint in_EIPSW = camry_SR[0][1];
  uint uVar3;
  uint in_FPEC = camry_SR[0][11];
  uint in_RBASE = camry_SR[1][2];
  uint in_EBASE = camry_SR[1][3];
  uint in_FPIPR = camry_SR[1][7];
  uint in_ISPR = camry_SR[2][10];
  uint in_INTCFG = camry_SR[2][13];
  
  __synchronize();
  __synchronize();
  __synchronize();
  uVar3 = ECMMESSTR0;
  if (((uVar3 & 0x1e) != 0) || (uVar3 = ECMCESSTR0, (uVar3 & 0x1e) != 0)) {
    clear_ecm_error_latches_once_or_terminate_7162e();
    return;
  }
  uVar3 = ECMMESSTR0;
  uVar3 = camry_psw & 0xfffffff8 | (uint)((uVar3 & 0x10000) == 0);
  if ((bool)((byte)uVar3 & 1)) {
    uVar3 = ECMCESSTR0;
    uVar3 = camry_psw & 0xfffffff8 | (uint)((uVar3 & 0x10000) == 0);
    if ((bool)((byte)uVar3 & 1)) {
      uVar3 = ECMMESSTR0;
      uVar3 = camry_psw & 0xfffffff8 | (uint)((uVar3 & 0x20000) == 0);
      if ((bool)((byte)uVar3 & 1)) {
        uVar3 = ECMCESSTR0;
        uVar3 = camry_psw & 0xfffffff8 | (uint)((uVar3 & 0x20000) == 0);
        if ((bool)((byte)uVar3 & 1)) {
          uVar3 = ECMMESSTR0;
          uVar3 = camry_psw & 0xfffffff8 | (uint)((uVar3 & 0x80000) == 0);
          if ((bool)((byte)uVar3 & 1)) {
            uVar3 = ECMCESSTR0;
            uVar3 = camry_psw & 0xfffffff8 | (uint)((uVar3 & 0x80000) == 0);
            if ((bool)((byte)uVar3 & 1)) {
              uVar3 = ECMMESSTR0;
              uVar3 = camry_psw & 0xfffffff8 | (uint)((uVar3 & 0x10000000) == 0);
              if ((bool)((byte)uVar3 & 1)) {
                uVar3 = ECMCESSTR0;
                uVar3 = camry_psw & 0xfffffff8 | (uint)((uVar3 & 0x10000000) == 0);
                if ((bool)((byte)uVar3 & 1)) {
                    /* WARNING: Subroutine does not return */
                  enter_terminal_hardware_sequence();
                }
              }
              count_register_fault_and_clear_or_terminate_65f24();
              __synchronize();
              __synchronize();
              goto LAB_00071c32;
            }
          }
          handle_ucf_error_address_or_count_fault_65dd6();
          __synchronize();
          __synchronize();
          goto LAB_00071c32;
        }
      }
    }
  }
  count_ffc654_fault_and_clear_or_terminate_65cda();
  __synchronize();
  __synchronize();
LAB_00071c32:
  if (((uVar3 >> 6 & 1) == 0) && ((in_INTCFG & 1) == 0)) {
    in_ISPR = in_ISPR & in_ISPR - 1;
    camry_SR[2][10] = in_ISPR;
  }
  camry_psw = in_EIPSW;
  camry_SR[2][12] &= ~2u;
  if ((in_FPEC & 1) != 0) {
    uint camry_fpi_priority = in_FPIPR & 31u;
    if (camry_fpi_priority > 15u) camry_fpi_priority = 15u;
    camry_SR[2][12] |= ((camry_pmr >> camry_fpi_priority) & 1u) << 1;
    in_FPIPR = in_FPIPR & 0x1f;
    if (0xf < in_FPIPR) {
      in_FPIPR = 0x10;
    }
    uVar3 = in_FPIPR;
    if (0xf < in_FPIPR) {
      uVar3 = 0xf;
    }
    uVar1 = PMR;
    if ((((uVar1 & 1 << uVar3) == 0) && ((in_ISPR & (1 << in_FPIPR + 1) - 1U & 0xffff) == 0)) &&
       ((in_EIPSW & 0xa0) == 0)) {
      if (((in_EIPSW & 0xbfffffbf) >> 0xf & 1) == 0) {
        in_EBASE = in_RBASE;
      }
      (*(int (*)())camry_indirect((uint32_t)((in_EBASE & 0xfffffe00) + 0x70)))(param_1,param_2,param_3,param_4);
    }
  }
  camry_psw = camry_SR[0][1];
    return;
}

void configure_debug_cache_and_invalidate_instruction_cache_71c48(void)

{
  uint uVar1;
  
  CDBCR = 3;
  __synchronize();
  ICCTRL = 0x30103;
  do {
    uVar1 = camry_sample_icctrl();
  } while ((uVar1 >> 8 & 1) != 0);
  return;
}

void spin_wait(uint outer_iterations)

{
  bool bVar1;
  int iVar2;
  
  if (outer_iterations != 0) {
    do {
      iVar2 = 0x9b;
      do {
        bVar1 = iVar2 != 1;
        iVar2 = iVar2 + -1;
      } while (bVar1);
      bVar1 = outer_iterations != 1;
      outer_iterations = outer_iterations - 1;
    } while (bVar1);
  }
  return;
}

void nvm_initialize_logical_cells(void)

{
  uint uVar1;
  uint uVar2;
  uchar uVar3;
  
  uVar2 = 0;
  do {
    if ((((ushort)(*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x26c0cu + (uint32_t)(uVar2) * (uint32_t)sizeof(F33NvmLogicalDescriptor)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmLogicalDescriptor) + (uint32_t)offsetof(F33NvmLogicalDescriptor, opaque_0a))))) >> 0xb & 1) == 0) &&
       (((*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x26c0cu + (uint32_t)(uVar2) * (uint32_t)sizeof(F33NvmLogicalDescriptor)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmLogicalDescriptor) + (uint32_t)offsetof(F33NvmLogicalDescriptor, opaque_0a))))) & 0x10) != 0)) {
      uVar3 = '\x01';
    }
    else {
      uVar3 = '\x02';
    }
    uVar1 = uVar2 + 1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebf6000u + (uint32_t)(uVar2) * (uint32_t)sizeof(F33NvmLogicalResultCell)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmLogicalResultCell) + (uint32_t)offsetof(F33NvmLogicalResultCell, write_inhibit))))) = uVar3;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebf6000u + (uint32_t)(uVar2) * (uint32_t)sizeof(F33NvmLogicalResultCell)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmLogicalResultCell) + (uint32_t)offsetof(F33NvmLogicalResultCell, result))))) = '\0';
    uVar2 = uVar1;
  } while (uVar1 < 0x7c);
  DAT_febf60f8 = 0;
  return;
}

void return_only_stub_71ce0(void)

{
  return;
}

void set_nvm_logical_write_inhibit_71ce2(uint param_1,uchar param_2)

{
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebf6000u + (uint32_t)(param_1 & 0xffff) * (uint32_t)sizeof(F33NvmLogicalResultCell)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmLogicalResultCell) + (uint32_t)offsetof(F33NvmLogicalResultCell, write_inhibit))))) = param_2;
  return;
}

undefined4 return_const_1_71cf4(void)

{
  return 1;
}

uint nvm_get_write_inhibit(ushort logical_handle)

{
  return (uint)(*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebf6000u + (uint32_t)(logical_handle) * (uint32_t)sizeof(F33NvmLogicalResultCell)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmLogicalResultCell) + (uint32_t)offsetof(F33NvmLogicalResultCell, write_inhibit)))));
}

uint nvm_read_logical_result(ushort logical_handle,uchar *output)

{
  *output = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebf6000u + (uint32_t)(logical_handle) * (uint32_t)sizeof(F33NvmLogicalResultCell)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmLogicalResultCell) + (uint32_t)offsetof(F33NvmLogicalResultCell, result)))));
  return 0;
}

void scan_five_nvm_pending_results_for_fault_71d3e(void)

{
  uint uVar1;
  int iVar2;
  uint uVar3;
  
  uVar3 = (uint)DAT_febf60f8;
  iVar2 = 5;
  do {
    if (0x7b < uVar3) {
      uVar3 = 0;
    }
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebf6000u + (uint32_t)(uVar3) * (uint32_t)sizeof(F33NvmLogicalResultCell)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmLogicalResultCell) + (uint32_t)offsetof(F33NvmLogicalResultCell, result))))) == '\x02') {
      record_nvm_integrity_fault_72130();
    }
    uVar1 = uVar3 + 1;
    uVar3 = uVar1 & 0xffff;
    iVar2 = iVar2 + -1;
  } while (iVar2 != 0);
  DAT_febf60f8 = (short)uVar1;
  return;
}

void set_nvm_diagnostic_state_f0_71d7c(void)

{
  DAT_febf6102 = 0xf0;
  return;
}

undefined4 return_const_0_71d88(void)

{
  return 0;
}

uint nvm_notify_zero_handle_result(uint operation,uchar result)

{
  uint32_t puVar1;
  uint uVar2;
  
  puVar1 = 0x23dfcu;
  uVar2 = lookup_u32_value_by_key(operation,0xff,(0x275ccu));
  if ((result != '\x02') && ((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar1 + 0x2dfc))))) != 0u)) {
    (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar1 + 0x2dfc))))))))))))(uVar2 & 0xff,result);
  }
  return uVar2;
}

void nvm_notify_logical_result(ushort logical_handle,uint operation,uchar result)

{
  uint32_t pFVar1;
  uint32_t puVar2;
  uint uVar3;
  
  pFVar1 = (uint32_t)((uint32_t)(nvm_application_result_callback));
  puVar2 = 0x23dfcu;
  if (((ushort)(*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x26c0cu + (uint32_t)(logical_handle) * (uint32_t)sizeof(F33NvmLogicalDescriptor)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmLogicalDescriptor) + (uint32_t)offsetof(F33NvmLogicalDescriptor, opaque_0a))))) >> 5 & 1) != 0) {
    puVar2 = 0x23dfcu;
    ((void)((uint)logical_handle), (void)(result), return_only_stub_747dc());
  }
  if ((result != '\x02') && ((uint32_t)(pFVar1) != 0u)) {
    uVar3 = lookup_u32_value_by_key(operation, 0xff, camry_host_addr(((F33U32LookupTable *)camry_host_ptr((uint32_t)(puVar2 + 0x37d0)))));
    (*(int (*)())camry_indirect((uint32_t)(pFVar1)))((uchar)uVar3,logical_handle,result);
  }
  return;
}

void nvm_route_logical_result(ushort logical_handle,uint operation,uchar result)

{
  if (logical_handle == 0) {
    nvm_notify_zero_handle_result(operation,result);
  }
  else {
    nvm_notify_logical_result(logical_handle,operation,result);
  }
  return;
}

void begin_nvm_operation_event_and_mark_categories_71e26(short param_1,uint param_2)

{
  uint uVar1;
  
  uVar1 = lookup_u32_value_by_key(param_2,0xff,(0x275ccu));
  uVar1 = uVar1 & 0xff;
  if (param_1 == 0) {
    nvm_set_service_and_begin_cd_diagnostics_79be8(uVar1);
  }
  else {
    nvm_set_record_and_begin_diagnostic_service_79bc0(param_1,uVar1);
    if ((uVar1 == 6) || (uVar1 == 0x16)) {
      DAT_febf60fa = 4;
      DAT_febf60fb = 4;
      DAT_febf60fe = 4;
      DAT_febf6101 = 4;
      DAT_febf60fc = 4;
    }
    else if ((uVar1 == 7) || (uVar1 == 0x17)) {
      DAT_febf60fa = 4;
      DAT_febf60fe = 4;
      DAT_febf60ff = 4;
    }
  }
  return;
}

void notify_nvm_category_state_one_or_two_71e88(uint param_1)

{
  undefined4 uVar1;
  
  uVar1 = 0;
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebf60fau + (uint32_t)(param_1 & 0xff) * 1u)))) == '\x01') ||
     (uVar1 = 1, (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebf60fau + (uint32_t)(param_1 & 0xff) * 1u)))) == '\x02')) {
    ((void)((*((undefined2 *)((uint8_t *)&PTR_DAT_000273cc + ((param_1 & 0xff) * 2))))), (void)(uVar1), return_only_stub_747de())
    ;
  }
  return;
}

void finish_nvm_operation_event_and_notify_categories_71eb4(short param_1,uint param_2)

{
  undefined4 uVar1;
  uint uVar2;
  
  uVar2 = lookup_u32_value_by_key(param_2,0xff,(0x275ccu));
  uVar2 = uVar2 & 0xff;
  if (param_1 == 0) {
    nvm_clear_current_service_byte_79c2a(uVar2);
  }
  else {
    nvm_clear_record_and_non_cd_service_79bfe(param_1,uVar2);
    if ((uVar2 == 6) || (uVar2 == 0x16)) {
      notify_nvm_category_state_one_or_two_71e88(0);
      notify_nvm_category_state_one_or_two_71e88(1);
      notify_nvm_category_state_one_or_two_71e88(4);
      notify_nvm_category_state_one_or_two_71e88(7);
      uVar1 = 2;
    }
    else {
      if ((uVar2 != 7) && (uVar2 != 0x17)) {
        return;
      }
      notify_nvm_category_state_one_or_two_71e88(0);
      notify_nvm_category_state_one_or_two_71e88(4);
      uVar1 = 5;
    }
    notify_nvm_category_state_one_or_two_71e88(uVar1);
  }
  return;
}

void begin_nvm_batch_item_event_and_mark_categories_71f28(undefined2 param_1,uint param_2)

{
  uint uVar1;
  int iVar2;
  
  uVar1 = lookup_u32_value_by_key(param_2,0xff,(0x275ccu));
  if ((uVar1 & 0xff) == 0xc) {
    nvm_set_record_and_begin_diagnostic_service_79bc0(param_1,0xc);
    DAT_febf60fb = 4;
    iVar2 = 2;
    DAT_febf6101 = 4;
  }
  else {
    if ((uVar1 & 0xff) != 0xd) {
      return;
    }
    nvm_set_record_and_begin_diagnostic_service_79bc0(param_1,0xd);
    iVar2 = 5;
  }
  DAT_febf60fa = 4;
  DAT_febf60fe = 4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebf60fau + (uint32_t)(iVar2) * 1u)))) = 4;
  return;
}

void finish_nvm_batch_item_event_and_notify_categories_71f82(undefined2 param_1,uint param_2)

{
  undefined4 uVar1;
  uint uVar2;
  
  uVar2 = lookup_u32_value_by_key(param_2,0xff,(0x275ccu));
  if ((uVar2 & 0xff) == 0xc) {
    nvm_clear_record_and_non_cd_service_79bfe(param_1,0xc);
    notify_nvm_category_state_one_or_two_71e88(0);
    notify_nvm_category_state_one_or_two_71e88(1);
    notify_nvm_category_state_one_or_two_71e88(4);
    notify_nvm_category_state_one_or_two_71e88(7);
    uVar1 = 2;
  }
  else {
    if ((uVar2 & 0xff) != 0xd) {
      return;
    }
    nvm_clear_record_and_non_cd_service_79bfe(param_1,0xd);
    notify_nvm_category_state_one_or_two_71e88(0);
    notify_nvm_category_state_one_or_two_71e88(4);
    uVar1 = 5;
  }
  notify_nvm_category_state_one_or_two_71e88(uVar1);
  return;
}

void set_nvm_read_buffer_wrapper_71fe4(ushort param_1,void *param_2)

{
  nvm_set_read_buffer(param_1, camry_host_addr(param_2));
  return;
}

int call_nvm_status_stub_70_without_read_override_71ff2(undefined2 param_1)

{
  int iVar1;
  
  iVar1 = nvm_has_read_buffer_override_7475a();
  if (iVar1 == 0) {
    ((void)(param_1), (void)(0x70), return_only_stub_71ce0());
  }
  return iVar1;
}
