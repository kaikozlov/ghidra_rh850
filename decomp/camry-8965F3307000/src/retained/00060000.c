#include "common.h"

void apply_indexed_capture_configuration_6008e(ushort param_1,ushort param_2)

{
  byte bVar1;
  int iVar2;
  
  iVar2 = (short)((param_1 & 0xff) * 5 + (param_2 & 0xff)) * 0x28;
  bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x310a8u + (uint32_t)(iVar2) * 1u))));
  if (bVar1 < 0x10) {
    disable_indexed_dma_channel_607fe(bVar1);
    program_dma_channel_from_descriptor_6082c(((undefined *)camry_host_ptr((uint32_t)(0x310a8u + (uint32_t)(iVar2) * 1u))));
    enable_indexed_dma_channel_6080e(bVar1);
  }
  return;
}

void enable_paired_adc_scan_capture_channels_600ca(void)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  
  uVar3 = 0;
  do {
    iVar1 = uVar3 * 0x1000;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfff91400u + (uint32_t)(iVar1) * 1u)))) = 1;
    spin_wait(1);
    apply_indexed_capture_configuration_6008e(uVar3,0);
    iVar2 = (short)uVar3 * 0x28;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfff91490u + (uint32_t)(iVar1) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfff91490u + (uint32_t)(iVar1) * 1u)))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x3105cu + (uint32_t)(iVar2) * 1u))));
    apply_indexed_capture_configuration_6008e(uVar3,1);
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfff91510u + (uint32_t)(iVar1) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfff91510u + (uint32_t)(iVar1) * 1u)))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x31064u + (uint32_t)(iVar2) * 1u))));
    apply_indexed_capture_configuration_6008e(uVar3,2);
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfff91590u + (uint32_t)(iVar1) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfff91590u + (uint32_t)(iVar1) * 1u)))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x3106cu + (uint32_t)(iVar2) * 1u))));
    apply_indexed_capture_configuration_6008e(uVar3,3);
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfff91610u + (uint32_t)(iVar1) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfff91610u + (uint32_t)(iVar1) * 1u)))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x31074u + (uint32_t)(iVar2) * 1u))));
    apply_indexed_capture_configuration_6008e(uVar3,4);
    uVar3 = uVar3 + 1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfff91690u + (uint32_t)(iVar1) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfff91690u + (uint32_t)(iVar1) * 1u)))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x3107cu + (uint32_t)(iVar2) * 1u))));
  } while (uVar3 < 2);
  return;
}

void run_init_chain_60178(void)

{
  reset_adc_sample_rings_and_check_counters_5face();
  fill_constant_block_5fafe();
  configure_adc_channels_and_run_threshold_checks_5ff08();
  load_adc_scan_group_configuration_5ff98();
  enable_paired_adc_scan_capture_channels_600ca();
  return;
}

void stop_paired_adc_scan_groups_and_wait_60194(void)

{
  byte bVar1;
  char cVar2;
  uint uVar3;
  int iVar4;
  ushort uVar5;
  
  bVar1 = DAT_fff91420;
  DAT_fff91420 = bVar1 & 0x23;
  bVar1 = DAT_fff92420;
  DAT_fff92420 = bVar1 & 0x23;
  bVar1 = DAT_fff91424;
  DAT_fff91424 = bVar1 & 0x23;
  bVar1 = DAT_fff92424;
  DAT_fff92424 = bVar1 & 0x23;
  uVar3 = 0;
  do {
    iVar4 = uVar3 * 0x80;
    uVar3 = uVar3 + 1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfff91490u + (uint32_t)(iVar4) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfff91490u + (uint32_t)(iVar4) * 1u)))) & 0x30;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfff92490u + (uint32_t)(iVar4) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfff92490u + (uint32_t)(iVar4) * 1u)))) & 0x30;
  } while (uVar3 < 5);
  iVar4 = 0;
  uVar5 = 0;
  do {
    if (DAT_00030f2a < uVar5) break;
    cVar2 = DAT_fff914a4;
    if ((((((cVar2 == '\0') && (cVar2 = DAT_fff91524, cVar2 == '\0')) &&
          (cVar2 = DAT_fff915a4, cVar2 == '\0')) &&
         ((cVar2 = DAT_fff91624, cVar2 == '\0' && (cVar2 = DAT_fff916a4, cVar2 == '\0')))) &&
        ((cVar2 = DAT_fff924a4, cVar2 == '\0' &&
         ((cVar2 = DAT_fff92524, cVar2 == '\0' && (cVar2 = DAT_fff925a4, cVar2 == '\0')))))) &&
       ((cVar2 = DAT_fff92624, cVar2 == '\0' && (cVar2 = DAT_fff926a4, cVar2 == '\0')))) {
      iVar4 = 0x5a;
    }
    else {
      spin_wait(1);
    }
    uVar5 = uVar5 + 1;
  } while (iVar4 != 0x5a);
  DAT_fff91380 = 1;
  DAT_fff92380 = 1;
  DAT_fff91404 = 1;
  DAT_fff92404 = 1;
  DAT_fff91430 = 0;
  DAT_fff92430 = 0;
  return;
}

void restart_paired_adc_scan_groups_602ac(void)

{
  uint uVar1;
  int iVar2;
  byte bVar3;
  undefined1 uVar4;
  uint uVar5;
  
  DAT_fff91430 = 0x1a;
  DAT_fff92430 = 0xe;
  DAT_fff91400 = 1;
  DAT_fff92400 = 1;
  spin_wait(1);
  uVar5 = 0;
  do {
    uVar1 = uVar5 + 1;
    iVar2 = uVar5 * 0x80;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfff91490u + (uint32_t)(iVar2) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfff91490u + (uint32_t)(iVar2) * 1u)))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x3105cu + (uint32_t)(uVar5 * 8) * 1u))));
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfff92490u + (uint32_t)(iVar2) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfff92490u + (uint32_t)(iVar2) * 1u)))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x31084u + (uint32_t)(uVar5 * 8) * 1u))));
    uVar5 = uVar1;
  } while (uVar1 < 5);
  bVar3 = DAT_fff91420;
  DAT_fff91420 = bVar3 | 0x32;
  bVar3 = DAT_fff92420;
  DAT_fff92420 = bVar3 | 0x32;
  uVar4 = DAT_fff91424;
  DAT_fff91424 = uVar4;
  uVar4 = DAT_fff92424;
  DAT_fff92424 = uVar4;
  return;
}

undefined4 repair_adc_channel_configuration_and_report_error_6033a(uint param_1)

{
  int iVar1;
  undefined4 uVar2;
  uint uVar3;
  int iVar4;
  int iVar5;
  uint uVar6;
  
  param_1 = param_1 & 0xff;
  iVar5 = 0;
  iVar4 = 0;
  uVar2 = 0;
  if (param_1 < 2) {
    uVar6 = 0;
    do {
      iVar1 = param_1 * 0x1000;
      uVar3 = *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x30f98u + (uint32_t)(((short)param_1 * 0x18 + uVar6) * 4) * 1u))));
      if ((*(volatile uint32_t *)camry_host_ptr(0xfff91000u + (uint32_t)iVar1 + uVar6 * 4u) & 0x3e03f) != uVar3) {
        stop_paired_adc_scan_groups_and_wait_60194();
        *(volatile uint32_t *)camry_host_ptr(0xfff91000u + (uint32_t)iVar1 + uVar6 * 4u) = uVar3;
        iVar5 = 0x5a;
        restart_paired_adc_scan_groups_602ac();
      }
      uVar6 = uVar6 + 1;
    } while (uVar6 < 0x18);
    if ((char)(*((volatile uint8_t *)camry_host_ptr(0xfff913e8u + (uint32_t)iVar1))) < '\0') {
      iVar4 = 0x5a;
      (*((volatile uint8_t *)camry_host_ptr(0xfff913d8u + (uint32_t)iVar1))) = 1;
    }
    if ((iVar5 == 0x5a) || (iVar4 == 0x5a)) {
      uVar2 = 0x5a;
    }
    else {
      uVar2 = 0;
    }
  }
  return uVar2;
}

void store_paired_adc_configuration_check_results_603c8(void)

{
  uint32_t puVar1;
  undefined1 uVar2;
  
  puVar1 = 0xfebeb800u;
  uVar2 = repair_adc_channel_configuration_and_report_error_6033a(0);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x7ff6))))) = uVar2;
  uVar2 = repair_adc_channel_configuration_and_report_error_6033a(1);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x7ff5))))) = uVar2;
  return;
}

void restore_selected_adc_control_register_groups_603e4(char param_1,char param_2,char param_3)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  
  if (param_1 == 'Z') {
    DAT_fff89110 = 2;
    DAT_fff91340 = 0;
    DAT_fff92340 = 0;
  }
  if (param_2 == 'Z') {
    uVar3 = 0;
    do {
      iVar1 = uVar3 * 8;
      iVar2 = uVar3 * 0x80;
      uVar3 = uVar3 + 1;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfff91494u + (uint32_t)(iVar2) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x31059u + (uint32_t)(iVar1) * 1u))));
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfff92494u + (uint32_t)(iVar2) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x31081u + (uint32_t)(iVar1) * 1u))));
    } while (uVar3 < 5);
  }
  if (param_3 == 'Z') {
    uVar3 = 0;
    do {
      iVar1 = uVar3 * 8;
      iVar2 = uVar3 * 0x80;
      uVar3 = uVar3 + 1;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfff91498u + (uint32_t)(iVar2) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x3105au + (uint32_t)(iVar1) * 1u))));
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfff92498u + (uint32_t)(iVar2) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x31082u + (uint32_t)(iVar1) * 1u))));
    } while (uVar3 < 5);
  }
  return;
}

void check_repair_adc_scan_configuration_and_refresh_dma_60462(void)

{
  short sVar1;
  char cVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  uint uVar6;
  
  iVar4 = DAT_fff89110;
  iVar5 = 0;
  if (((iVar4 != 2) || (sVar1 = DAT_fff91340, sVar1 != 0)) || (sVar1 = DAT_fff92340, sVar1 != 0)) {
    iVar5 = 0x5a;
  }
  iVar4 = 0;
  cVar2 = DAT_fff91494;
  if ((((cVar2 != DAT_00031059) || (cVar2 = DAT_fff91514, cVar2 != DAT_00031061)) ||
      ((cVar2 = DAT_fff91594, cVar2 != DAT_00031069 ||
       ((cVar2 = DAT_fff91614, cVar2 != DAT_00031071 ||
        (cVar2 = DAT_fff91694, cVar2 != DAT_00031079)))))) ||
     ((cVar2 = DAT_fff92494, cVar2 != DAT_00031081 ||
      ((((cVar2 = DAT_fff92514, cVar2 != DAT_00031089 ||
         (cVar2 = DAT_fff92594, cVar2 != DAT_00031091)) ||
        (cVar2 = DAT_fff92614, cVar2 != DAT_00031099)) ||
       (cVar2 = DAT_fff92694, cVar2 != DAT_000310a1)))))) {
    iVar4 = 0x5a;
  }
  iVar3 = 0;
  cVar2 = DAT_fff91498;
  if ((((cVar2 != DAT_0003105a) || (cVar2 = DAT_fff91518, cVar2 != DAT_00031062)) ||
      ((((cVar2 = DAT_fff91598, cVar2 != DAT_0003106a ||
         ((cVar2 = DAT_fff91618, cVar2 != DAT_00031072 ||
          (cVar2 = DAT_fff91698, cVar2 != DAT_0003107a)))) ||
        (cVar2 = DAT_fff92498, cVar2 != DAT_00031082)) ||
       (((cVar2 = DAT_fff92518, cVar2 != (char)PTR_DAT_0003108a ||
         (cVar2 = DAT_fff92598, cVar2 != DAT_00031092)) ||
        (cVar2 = DAT_fff92618, cVar2 != (char)PTR_DAT_0003109a)))))) ||
     (cVar2 = DAT_fff92698, cVar2 != DAT_000310a2)) {
    iVar3 = 0x5a;
  }
  if (((iVar5 == 0x5a) || (iVar4 == 0x5a)) || (iVar3 == 0x5a)) {
    stop_paired_adc_scan_groups_and_wait_60194();
    restore_selected_adc_control_register_groups_603e4(iVar5,iVar4,iVar3);
    restart_paired_adc_scan_groups_602ac();
  }
  uVar6 = 0;
  do {
    if (((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x310a8u + (uint32_t)((short)uVar6 * 0x28) * 1u))))) != -1) {
      refresh_dma_reload_descriptor_and_selector_60a6a(((undefined *)camry_host_ptr((uint32_t)(0x310a8u + (uint32_t)((short)uVar6 * 0x28) * 1u))));
    }
    iVar4 = (short)uVar6 * 0x28;
    if (((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x31170u + (uint32_t)(iVar4) * 1u))))) != -1) {
      refresh_dma_reload_descriptor_and_selector_60a6a(((undefined *)camry_host_ptr((uint32_t)(0x31170u + (uint32_t)(iVar4) * 1u))));
    }
    uVar6 = uVar6 + 1;
  } while (uVar6 < 5);
  return;
}

int consume_adc0_ring_sample_u16_60630(uint param_1)

{
  uint uVar1;
  
  if (0x4f < (param_1 & 0xffff)) {
    return 0;
  }
  uVar1 = *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfeef80a0u + (uint32_t)((param_1 & 0xffff) * 4) * 1u))));
  *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfeef80a0u + (uint32_t)((param_1 & 0xffff) * 4) * 1u)))) = uVar1 & 0xffff0000;
  return (uVar1 & 0x7ff8) << 1;
}

uint consume_acquisition_group0_entry(ushort index)

{
  uint uVar1;
  
  if (0x1af < index) {
    return 0;
  }
  uVar1 = (*((uint *)camry_host_ptr((uint32_t)((0xfeef81e0u) + (uint)index * 4))));
  (*((uint *)camry_host_ptr((uint32_t)((0xfeef81e0u) + (uint)index * 4)))) = uVar1 & 0xffff0000;
  return (uVar1 & 0x7ff8) << 1;
}

int consume_adc1_ring_sample_u16_606da(uint param_1)

{
  uint uVar1;
  
  if (0x5f < (param_1 & 0xffff)) {
    return 0;
  }
  uVar1 = *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfeef88a0u + (uint32_t)((param_1 & 0xffff) * 4) * 1u))));
  *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfeef88a0u + (uint32_t)((param_1 & 0xffff) * 4) * 1u)))) = uVar1 & 0xffff0000;
  return (uVar1 & 0x7ff8) << 1;
}

uint consume_acquisition_group8_entry(ushort index)

{
  uint uVar1;
  
  if (0x1af < index) {
    return 0;
  }
  uVar1 = (*((uint *)camry_host_ptr((uint32_t)((0xfeef8a20u) + (uint)index * 4))));
  (*((uint *)camry_host_ptr((uint32_t)((0xfeef8a20u) + (uint)index * 4)))) = uVar1 & 0xffff0000;
  return (uVar1 & 0x7ff8) << 1;
}

void initialize_dma_channel_modes_and_counters_60766(void)

{
  int iVar1;
  uint uVar2;
  
  DM00CM = 0x200c;
  DAT_ffff8104 = 0x2018;
  DAT_ffff8108 = 0x200c;
  DAT_ffff810c = 0x2010;
  DAT_ffff8110 = 0x200c;
  DAT_ffff8114 = 0x2014;
  DAT_ffff8118 = 0x200c;
  DAT_ffff811c = 0x207c;
  DM10CM = 0x200c;
  DAT_ffff8124 = 0x2018;
  DAT_ffff8128 = 0x200c;
  DAT_ffff812c = 0x2010;
  DAT_ffff8130 = 0x200c;
  DAT_ffff8134 = 0x2014;
  DAT_ffff8138 = 0x200c;
  DAT_ffff813c = 0x207c;
  uVar2 = 0;
  do {
    iVar1 = uVar2 * 2;
    uVar2 = uVar2 + 1;
    *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe380cu + (uint32_t)(iVar1) * 1u)))) = 0;
  } while (uVar2 < 0x10);
  return;
}

void enable_dma_and_reset_sixteen_channel_controls_607d0(void)

{
  int iVar1;
  uint uVar2;
  
  Ramffff8000 = 1;
  uVar2 = 0;
  do {
    iVar1 = uVar2 * 0x40;
    uVar2 = uVar2 + 1;
    (*((uint *)camry_host_ptr((uint32_t)(iVar1 + -0x7bd0)))) = (*((uint *)camry_host_ptr((uint32_t)(iVar1 + -0x7bd0)))) & 0xfffffffe;
    (*((undefined4 *)camry_host_ptr((uint32_t)(iVar1 + -0x7bc8)))) = 1;
    (*((undefined4 *)camry_host_ptr((uint32_t)(iVar1 + -0x7bd4)))) = 1;
  } while (uVar2 < 0x10);
  return;
}

void disable_dma_global_control_607f8(void)

{
  Ramffff8000 = 0;
  return;
}

void disable_indexed_dma_channel_607fe(uint param_1)

{
  if ((param_1 & 0xff) < 0x10) {
    (*((undefined4 *)camry_host_ptr((uint32_t)((param_1 & 0xff) * 0x40 + -0x7be0)))) = 0;
  }
  return;
}

void enable_indexed_dma_channel_6080e(uint param_1)

{
  int iVar1;
  
  if ((param_1 & 0xff) < 0x10) {
    iVar1 = (param_1 & 0xff) * 0x40;
    (*((undefined4 *)camry_host_ptr((uint32_t)(iVar1 + -0x7bc8)))) = 3;
    (*((undefined4 *)camry_host_ptr((uint32_t)(iVar1 + -0x7bd4)))) = 0xb1;
    (*((undefined4 *)camry_host_ptr((uint32_t)(iVar1 + -0x7be0)))) = 1;
  }
  return;
}

void program_dma_channel_from_descriptor_6082c(byte *param_1)

{
  int iVar1;
  byte bVar2;
  undefined2 uVar3;
  ushort uVar4;
  uint uVar5;
  uint uVar6;
  
  bVar2 = param_1[1];
  if (*param_1 < 0x10) {
    iVar1 = (uint)*param_1 * 0x40;
    uVar3 = *(undefined2 *)(param_1 + 4);
    (*((undefined4 *)camry_host_ptr((uint32_t)(iVar1 + -0x7c00)))) = *(undefined4 *)(param_1 + 8);
    (*((undefined4 *)camry_host_ptr((uint32_t)(iVar1 + -0x7bfc)))) = *(undefined4 *)(param_1 + 0xc);
    (*((uint *)camry_host_ptr((uint32_t)(iVar1 + -0x7bf8)))) = CONCAT22(*(undefined2 *)(param_1 + 6),uVar3);
    uVar5 = (uint)param_1[3];
    uVar6 = (uint)param_1[2] << 2 |
            (uint)param_1[0x13] << 0xd |
            (uint)param_1[0x12] << 0xe |
            (uint)param_1[0x11] << 0xf |
            (uint)param_1[0x10] << 0x1b | *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x315a4u + (uint32_t)((uint)bVar2 * 4) * 1u))));
    if (uVar5 != 0) {
      uVar6 = uVar6 | 0x4000000;
    }
    (*((uint *)camry_host_ptr((uint32_t)(iVar1 + -0x7bf4)))) = uVar6;
    uVar3 = *(undefined2 *)(param_1 + 0x14);
    (*((undefined4 *)camry_host_ptr((uint32_t)(iVar1 + -0x7bf0)))) = *(undefined4 *)(param_1 + 0x18);
    (*((undefined4 *)camry_host_ptr((uint32_t)(iVar1 + -0x7bec)))) = *(undefined4 *)(param_1 + 0x1c);
    uVar4 = *(ushort *)(param_1 + 0x20);
    (*((uint *)camry_host_ptr((uint32_t)(iVar1 + -0x7be8)))) = CONCAT22(*(undefined2 *)(param_1 + 0x16),uVar3);
    (*((uint *)camry_host_ptr((uint32_t)(iVar1 + -0x7be4)))) = (uint)uVar4;
    if ((uVar5 & 0xfe) - 0x1a < 0x15) {
      uVar6 = Ramfff99000;
      Ramfff99000 = uVar6 & ~(uint)*(ushort *)(param_1 + 0x24);
      uVar6 = Ramfff99000;
      Ramfff99000 = uVar6 | *(ushort *)(param_1 + 0x22);
    }
    if ((uVar5 & 0xfe) - 0x44 < 0x15) {
      uVar6 = Ramfff99004;
      Ramfff99004 = uVar6 & ~(uint)*(ushort *)(param_1 + 0x24);
      uVar6 = Ramfff99004;
      Ramfff99004 = uVar6 | *(ushort *)(param_1 + 0x22);
    }
    (*((uint *)camry_host_ptr((uint32_t)(iVar1 + -0x7bd0)))) = uVar5;
  }
  return;
}

uint read_transfer_descriptor_head(uchar channel)

{
  return (*((uint *)camry_host_ptr((uint32_t)((uint)channel * 0x40 + -0x7bfc))));
}

uint read_transfer_primary_count_low(uchar channel)

{
  return (*((uint *)camry_host_ptr((uint32_t)((uint)channel * 0x40 + -0x7bf8)))) & 0xffff;
}

ushort count_transfer_entries(uchar channel)

{
  uint uVar1;
  int iVar2;
  ushort uVar3;
  uint uVar4;
  uint uVar5;
  
  uVar3 = 0;
  if (channel < 0x10) {
    iVar2 = (uint)channel * 0x40;
    uVar4 = (*((uint *)camry_host_ptr((uint32_t)(iVar2 + -0x7be8))));
    uVar5 = (*((uint *)camry_host_ptr((uint32_t)(iVar2 + -0x7bf8))));
    uVar1 = uVar4 - (uVar4 >> 0x10);
    uVar3 = (ushort)uVar1;
    uVar5 = ((uVar5 >> 0x10) + (uVar1 & 0xffff)) - uVar5;
    if (uVar4 >> 0x10 <= (uVar5 & 0xffff)) {
      uVar3 = (short)uVar5 - (short)(uVar4 >> 0x10);
    }
  }
  return uVar3;
}

uint read_dma_progress_delta(uchar channel)

{
  uint uVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  uint uVar7;
  
  uVar3 = (uint)channel;
  uVar4 = 0;
  if (uVar3 < 0x10) {
    iVar2 = uVar3 * 0x40;
    uVar6 = (*((uint *)camry_host_ptr((uint32_t)(iVar2 + -0x7bdc)))) & 0x30;
    (*((uint *)camry_host_ptr((uint32_t)(iVar2 + -0x7bd4)))) = uVar6;
    uVar7 = (uint)*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe380cu + (uint32_t)(uVar3 * 2) * 1u))));
    uVar5 = (*((uint *)camry_host_ptr((uint32_t)(iVar2 + -0x7be8)))) & 0xffff;
    uVar1 = uVar5 - (*((int *)camry_host_ptr((uint32_t)(iVar2 + -0x7bf8))));
    uVar4 = uVar1 & 0xffff;
    *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe380cu + (uint32_t)(uVar3 * 2) * 1u)))) = (ushort)uVar1;
    if (uVar4 < uVar7) {
      uVar4 = uVar5 + uVar4;
    }
    uVar4 = uVar4 - uVar7;
    if ((uVar6 >> 5 != 0) && ((uVar6 >> 4 & 1) != 0)) {
      uVar4 = uVar5 >> 1;
    }
  }
  return uVar4;
}

void disable_dma_and_restore_channel_modes_60a10(void)

{
  Ramffff8000 = 0;
  DM00CM = 0x200c;
  DAT_ffff8104 = 0x2018;
  DAT_ffff8108 = 0x200c;
  DAT_ffff810c = 0x2010;
  DAT_ffff8110 = 0x200c;
  DAT_ffff8114 = 0x2014;
  DAT_ffff8118 = 0x200c;
  DAT_ffff811c = 0x207c;
  DM10CM = 0x200c;
  DAT_ffff8124 = 0x2018;
  DAT_ffff8128 = 0x200c;
  DAT_ffff812c = 0x2010;
  DAT_ffff8130 = 0x200c;
  DAT_ffff8134 = 0x2014;
  DAT_ffff8138 = 0x200c;
  DAT_ffff813c = 0x207c;
  return;
}

void refresh_dma_reload_descriptor_and_selector_60a6a(byte *param_1)

{
  int iVar1;
  byte bVar2;
  undefined2 uVar3;
  uint *puVar4;
  
  if (*param_1 < 0x10) {
    iVar1 = (uint)*param_1 * 0x40;
    uVar3 = *(undefined2 *)(param_1 + 0x14);
    (*((undefined4 *)camry_host_ptr((uint32_t)(iVar1 + -0x7bf0)))) = *(undefined4 *)(param_1 + 0x18);
    (*((undefined4 *)camry_host_ptr((uint32_t)(iVar1 + -0x7bec)))) = *(undefined4 *)(param_1 + 0x1c);
    (*((uint *)camry_host_ptr((uint32_t)(iVar1 + -0x7be8)))) = CONCAT22(*(undefined2 *)(param_1 + 0x16),uVar3);
    bVar2 = param_1[3];
    if ((*((uint *)camry_host_ptr((uint32_t)(iVar1 + -0x7bd0)))) != (uint)bVar2) {
      puVar4 = ((uint *)camry_host_ptr((uint32_t)(iVar1 + -0x7bd0)));
      *puVar4 = *puVar4 & 0xfe;
      *puVar4 = (uint)bVar2;
    }
  }
  return;
}

void reset_four_capture_status_records_60aa8(void)

{
  uint uVar1;
  uint uVar2;
  int iVar3;
  
  uVar2 = 0;
  do {
    uVar1 = 0;
    do {
      iVar3 = (short)((short)uVar1 + (short)(uVar2 << 1)) * 0x18;
      uVar1 = uVar1 + 1;
      *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfeef90f8u + (uint32_t)(iVar3) * 1u)))) = 0;
      *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfeef90fcu + (uint32_t)(iVar3) * 1u)))) = 0;
      *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfeef9100u + (uint32_t)(iVar3) * 1u)))) = 0;
      *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfeef9104u + (uint32_t)(iVar3) * 1u)))) = 0;
      *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfeef9108u + (uint32_t)(iVar3) * 1u)))) = 0;
      *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfeef910cu + (uint32_t)(iVar3) * 1u)))) = 0x800800;
    } while (uVar1 < 2);
    uVar2 = uVar2 + 1;
  } while (uVar2 < 2);
  return;
}

void write_indexed_capture_control_and_wait_echo_60ae0(uint param_1,int param_2)

{
  byte bVar1;
  ushort uVar2;
  
  if ((param_1 & 0xff) < 2) {
    bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x3125au + (uint32_t)(param_1 & 0xff) * 1u))));
    (*((int *)camry_host_ptr((uint32_t)((uint)bVar1 * 0x1000 + -0x1fafe4)))) = param_2;
    for (uVar2 = 0;
        ((*((int *)camry_host_ptr((uint32_t)((uint)bVar1 * 0x1000 + -0x1fafdc)))) != param_2 && (uVar2 < DAT_00031258));
        uVar2 = uVar2 + 1) {
      spin_wait(1);
    }
  }
  return;
}

void configure_indexed_capture_register_block_60b26(uint param_1)

{
  int iVar1;
  int iVar2;
  
  param_1 = param_1 & 0xff;
  if (param_1 < 2) {
    iVar1 = param_1 * 4;
    iVar2 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x3125au + (uint32_t)(param_1) * 1u)))) * 0x1000;
    (*((undefined4 *)camry_host_ptr((uint32_t)(iVar2 + -0x1fafec)))) = *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0x31248u + (uint32_t)(iVar1) * 1u))));
    (*((undefined4 *)camry_host_ptr((uint32_t)(iVar2 + -0x1fb000)))) = *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0x31238u + (uint32_t)(iVar1) * 1u))));
    (*((undefined4 *)camry_host_ptr((uint32_t)(iVar2 + -0x1faff0)))) = *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0x31240u + (uint32_t)(iVar1) * 1u))));
    (*((undefined4 *)camry_host_ptr((uint32_t)(iVar2 + -0x1fafe8)))) = 1;
  }
  return;
}

void configure_primary_capture_dma_descriptor_60b76(ushort param_1)

{
  undefined1 uVar1;
  int iVar2;
  
  if ((param_1 & 0xff) < 2) {
    iVar2 = (short)(param_1 & 0xff) * 0x28;
    uVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x3125cu + (uint32_t)(iVar2) * 1u))));
    disable_indexed_dma_channel_607fe(uVar1);
    program_dma_channel_from_descriptor_6082c(((undefined *)camry_host_ptr((uint32_t)(0x3125cu + (uint32_t)(iVar2) * 1u))));
    enable_indexed_dma_channel_6080e(uVar1);
  }
  return;
}

void configure_secondary_capture_dma_descriptor_60ba8(ushort param_1)

{
  undefined1 uVar1;
  int iVar2;
  
  if ((param_1 & 0xff) < 2) {
    iVar2 = (short)(param_1 & 0xff) * 0x28;
    uVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x312acu + (uint32_t)(iVar2) * 1u))));
    disable_indexed_dma_channel_607fe(uVar1);
    program_dma_channel_from_descriptor_6082c(((undefined *)camry_host_ptr((uint32_t)(0x312acu + (uint32_t)(iVar2) * 1u))));
    enable_indexed_dma_channel_6080e(uVar1);
  }
  return;
}

void run_init_chain_60bda(undefined1 param_1)

{
  write_indexed_capture_control_and_wait_echo_60ae0(param_1,1);
  configure_indexed_capture_register_block_60b26(param_1);
  write_indexed_capture_control_and_wait_echo_60ae0(param_1,5);
  configure_primary_capture_dma_descriptor_60b76(param_1);
  configure_secondary_capture_dma_descriptor_60ba8(param_1);
  return;
}

void initialize_four_capture_records_and_both_channels_60c06(void)

{
  uint uVar1;
  
  reset_four_capture_status_records_60aa8();
  uVar1 = 0;
  do {
    run_init_chain_60bda(uVar1);
    uVar1 = uVar1 + 1;
  } while (uVar1 < 2);
  return;
}

void rearm_both_capture_registers_and_dma_reload_60c20(void)

{
  int iVar1;
  uint uVar2;
  
  uVar2 = 0;
  do {
    iVar1 = (short)uVar2 * 0x28;
    (*((undefined4 *)camry_host_ptr((uint32_t)((uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x3125au + (uint32_t)(uVar2) * 1u)))) * 0x1000 + -0x1fafe8)))) = 1;
    refresh_dma_reload_descriptor_and_selector_60a6a(((undefined *)camry_host_ptr((uint32_t)(0x3125cu + (uint32_t)(iVar1) * 1u))));
    refresh_dma_reload_descriptor_and_selector_60a6a(((undefined *)camry_host_ptr((uint32_t)(0x312acu + (uint32_t)(iVar1) * 1u))));
    uVar2 = uVar2 + 1;
  } while (uVar2 < 2);
  return;
}

void read_capture_status_and_consume_overrun_bit_60c60(uint param_1,ushort param_2,ushort *param_3)

{
  uint uVar1;
  uint uVar2;
  int iVar3;
  undefined4 uVar4;
  
  param_1 = param_1 & 0xff;
  if (((param_2 & 0xff) < 2) && (param_1 < 2)) {
    iVar3 = (short)((param_2 & 0xff) + (short)param_1 * 2) * 0x18;
    uVar2 = (*((uint *)camry_host_ptr((uint32_t)((uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x3125au + (uint32_t)(param_1) * 1u)))) * 0x1000 + -0x1fafd8)))) & 0x7fe;
    (*((uint *)camry_host_ptr((uint32_t)((uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x3125au + (uint32_t)(param_1) * 1u)))) * 0x1000 + -0x1fafd4)))) = uVar2;
    uVar1 = *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfeef910cu + (uint32_t)(iVar3) * 1u))));
    *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfeef910cu + (uint32_t)(iVar3) * 1u)))) = uVar1 & 0xbfffffff;
    uVar4 = *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfeef90fcu + (uint32_t)(iVar3) * 1u))));
    *param_3 = (ushort)uVar2 | ((ushort)(uVar1 >> 0x10) & 0x4000) >> 0xe;
    param_3[1] = (ushort)uVar4 & 0xf;
    param_3[2] = (ushort)((uVar1 & 0xfff000) >> 0xc);
    param_3[3] = (ushort)uVar1 & 0xfff;
  }
  return;
}

void load_six_port_configuration_records_60cd4(void)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  
  uVar3 = 0;
  do {
    iVar1 = uVar3 * 0x10;
    iVar2 = uVar3 * 0x40;
    uVar3 = uVar3 + 1;
    (*((undefined4 *)camry_host_ptr((uint32_t)(iVar2 + -0x3ebfe8)))) = *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0x31394u + (uint32_t)(iVar1) * 1u))));
    (*((undefined4 *)camry_host_ptr((uint32_t)(iVar2 + -0x3ebfd8)))) = *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0x31398u + (uint32_t)(iVar1) * 1u))));
    (*((undefined4 *)camry_host_ptr((uint32_t)(iVar2 + -0x3ebfec)))) = *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0x3139cu + (uint32_t)(iVar1) * 1u))));
    (*((undefined4 *)camry_host_ptr((uint32_t)(iVar2 + -0x3ebfc4)))) = *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0x313a0u + (uint32_t)(iVar1) * 1u))));
  } while (uVar3 < 6);
  return;
}

void initialize_port_configuration_and_mux_fields_60d0e(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  
  load_six_port_configuration_records_60cd4();
  iVar5 = 0;
  do {
    iVar4 = iVar5 * 8;
    iVar3 = iVar5 + 1;
    iVar2 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x31311u + (uint32_t)(iVar4) * 1u)))) * 4 + (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x31310u + (uint32_t)(iVar4) * 1u)))) * 0x40;
    iVar1 = iVar5 + -0xf;
    (*((uint *)camry_host_ptr((uint32_t)(iVar2 + -0x3ee000)))) =
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x3130cu + (uint32_t)(iVar4) * 1u)))) | (*((uint *)camry_host_ptr((uint32_t)(iVar2 + -0x3ee000)))) & 0xfffeff88;
    iVar5 = iVar3;
  } while (((iVar1 < 0) || (iVar3 < 0)));
  return;
}

void clear_indexed_serial_halfword_buffer_60d52(uint param_1)

{
  uint uVar1;
  
  param_1 = param_1 & 0xff;
  if (param_1 < 2) {
    for (uVar1 = 0; uVar1 < (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x31411u + (uint32_t)((short)param_1 * 0x50) * 1u)))); uVar1 = uVar1 + 1 & 0xff)
    {
      (*((undefined2 *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x313fcu + (uint32_t)(param_1) * 4u)))) + uVar1 * 2)))) = 0;
    }
  }
  return;
}

void load_indexed_serial_register_configuration_60d8c(ushort param_1)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  if ((param_1 & 0xff) < 2) {
    iVar1 = (int)(short)(param_1 & 0xff);
    iVar3 = iVar1 * 0x50;
    iVar2 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x3140cu + (uint32_t)(iVar3) * 1u)))) * 0x2000;
    (*((undefined1 *)camry_host_ptr((uint32_t)(iVar2 + -0x280000)))) = 0;
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)((iVar2 + -0x27fff0))))) = (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x31424u + (uint32_t)(iVar1 * 0x14) * 4u))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(iVar2 + -0x27ffec)))) = *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0x31428u + (uint32_t)(iVar3) * 1u))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(iVar2 + -0x27efc0)))) = *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0x3142cu + (uint32_t)(iVar3) * 1u))));
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)((iVar2 + -0x27efbc))))) = (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x31434u + (uint32_t)(iVar1 * 0x14) * 4u))));
    (*((undefined4 *)camry_host_ptr((uint32_t)(iVar2 + -0x27efb8)))) = *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0x31438u + (uint32_t)(iVar3) * 1u))));
    (*((undefined4 *)camry_host_ptr((uint32_t)(iVar2 + -0x27efb4)))) = *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0x3143cu + (uint32_t)(iVar3) * 1u))));
    (*((undefined4 *)camry_host_ptr((uint32_t)(iVar2 + -0x27efb0)))) = *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0x31440u + (uint32_t)(iVar3) * 1u))));
    (*((undefined4 *)camry_host_ptr((uint32_t)(iVar2 + -0x27efac)))) = *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0x31444u + (uint32_t)(iVar3) * 1u))));
    (*((undefined4 *)camry_host_ptr((uint32_t)(iVar2 + -0x27efa8)))) = *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0x31448u + (uint32_t)(iVar3) * 1u))));
    (*((undefined4 *)camry_host_ptr((uint32_t)(iVar2 + -0x27efa4)))) = *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0x3144cu + (uint32_t)(iVar3) * 1u))));
    (*((undefined4 *)camry_host_ptr((uint32_t)(iVar2 + -0x27efa0)))) = *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0x31450u + (uint32_t)(iVar3) * 1u))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(iVar2 + -0x27ef98)))) = *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0x31454u + (uint32_t)(iVar3) * 1u))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(iVar2 + -0x27ef94)))) = *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0x31456u + (uint32_t)(iVar3) * 1u))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(iVar2 + -0x27ef90)))) = *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0x31458u + (uint32_t)(iVar3) * 1u))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(iVar2 + -0x27ef8c)))) = *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0x3145au + (uint32_t)(iVar3) * 1u))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(iVar2 + -0x27fff8)))) = *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0x3142au + (uint32_t)(iVar3) * 1u))));
    (*((undefined *)camry_host_ptr((uint32_t)(iVar2 + -0x280000)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x31420u + (uint32_t)(iVar3) * 1u))));
  }
  return;
}

void initialize_both_serial_buffers_and_registers_60e3e(void)

{
  uint uVar1;
  
  uVar1 = 0;
  do {
    clear_indexed_serial_halfword_buffer_60d52(uVar1);
    load_indexed_serial_register_configuration_60d8c(uVar1);
    uVar1 = uVar1 + 1;
  } while (uVar1 < 2);
  return;
}

void configure_enabled_serial_dma_descriptors_60e5a(void)

{
  undefined1 uVar1;
  int iVar2;
  short sVar3;
  uint uVar4;
  
  uVar4 = 0;
  do {
    sVar3 = (short)uVar4;
    iVar2 = sVar3 * 0x50;
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x31414u + (uint32_t)(iVar2) * 1u)))) == '\0') {
      uVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x314acu + (uint32_t)(sVar3 * 0x28) * 1u))));
      disable_indexed_dma_channel_607fe(uVar1);
      program_dma_channel_from_descriptor_6082c(((undefined *)camry_host_ptr((uint32_t)(0x314acu + (uint32_t)(sVar3 * 0x28) * 1u))));
      enable_indexed_dma_channel_6080e(uVar1);
    }
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x31415u + (uint32_t)(iVar2) * 1u)))) == '\0') {
      uVar1 = (*((undefined1 *)camry_host_ptr((uint32_t)(&PTR_DAT_000314fc + sVar3 * 10))));
      disable_indexed_dma_channel_607fe(uVar1);
      program_dma_channel_from_descriptor_6082c(&PTR_DAT_000314fc + sVar3 * 10);
      enable_indexed_dma_channel_6080e(uVar1);
    }
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x31416u + (uint32_t)(iVar2) * 1u)))) == '\0') {
      uVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x3154cu + (uint32_t)(sVar3 * 0x28) * 1u))));
      disable_indexed_dma_channel_607fe(uVar1);
      program_dma_channel_from_descriptor_6082c(((undefined *)camry_host_ptr((uint32_t)(0x3154cu + (uint32_t)(sVar3 * 0x28) * 1u))));
      enable_indexed_dma_channel_6080e(uVar1);
    }
    uVar4 = uVar4 + 1;
  } while (uVar4 < 2);
  return;
}

undefined4 write_serial_halfword_matrix_when_idle_60efa(ushort param_1,int param_2)

{
  int iVar1;
  byte bVar2;
  byte bVar3;
  uint uVar4;
  int iVar5;
  ushort uVar6;
  uint uVar7;
  int iVar8;
  
  if ((param_1 & 0xff) < 2) {
    iVar8 = (short)(param_1 & 0xff) * 0x50;
    bVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x3140eu + (uint32_t)(iVar8) * 1u))));
    bVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x3140fu + (uint32_t)(iVar8) * 1u))));
    iVar1 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x3140cu + (uint32_t)(iVar8) * 1u)))) * 0x2000;
    if ((((*((uint *)camry_host_ptr((uint32_t)(iVar1 + -0x27fffc)))) >> 7 & 1) == 0) && (bVar2 != 0)) {
      (*((undefined2 *)camry_host_ptr((uint32_t)(iVar1 + -0x27fff8)))) = 0x100;
      for (uVar6 = 0; uVar6 < bVar3; uVar6 = uVar6 + 1 & 0xff) {
        for (uVar7 = 0; iVar5 = bVar2 - 1,
            uVar4 = (uint)(*((ushort *)camry_host_ptr((uint32_t)(((int)(short)(ushort)bVar2 * (int)(short)uVar6 + uVar7) * 2 + param_2)))),
            (int)(uVar7 - iVar5) < 0 != (iVar5 < 0 && iVar5 < 0 == (int)(uVar7 - iVar5) < 0);
            uVar7 = uVar7 + 1 & 0xff) {
          (*((uint *)camry_host_ptr((uint32_t)(iVar1 + -0x27eff8)))) = uVar4 | *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x31418u + (uint32_t)(iVar8) * 1u)))) & 0xffff0000;
        }
        (*((uint *)camry_host_ptr((uint32_t)(iVar1 + -0x27eff8)))) = uVar4 | *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x3141cu + (uint32_t)(iVar8) * 1u)))) & 0xffff0000;
      }
      return 0;
    }
  }
  return 0x5a;
}

undefined4 set_bounded_serial_transfer_count_60f7c(ushort param_1,uint param_2)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  
  if ((param_1 & 0xff) < 2) {
    iVar3 = (short)(param_1 & 0xff) * 0x50;
    uVar2 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x31410u + (uint32_t)(iVar3) * 1u)))) - (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x3140eu + (uint32_t)(iVar3) * 1u))));
    iVar1 = (param_2 & 0xff) - uVar2;
    if (iVar1 < 0 != ((int)uVar2 < 0 && (int)uVar2 < 0 == iVar1 < 0) || (param_2 & 0xff) == uVar2) {
      (*((uint *)camry_host_ptr((uint32_t)((uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x3140cu + (uint32_t)(iVar3) * 1u)))) * 0x2000 + -0x27effc)))) =
           *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x31430u + (uint32_t)(iVar3) * 1u)))) | param_2 & 0x3f;
      return 0;
    }
  }
  return 0x5a;
}
