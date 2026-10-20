#include "common.h"

void integrate_control_profile_unsigned_source(uchar slot)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  undefined2 uVar4;
  undefined2 uVar5;
  
  iVar1 = (uint)slot * 2;
  iVar2 = (uint)slot * 4;
  uVar5 = *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb868u + (uint32_t)(iVar1) * 1u))));
  uVar4 = *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb872u + (uint32_t)(iVar1) * 1u))));
  uVar3 = *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebebbdcu + (uint32_t)(iVar2) * 1u))));
  if ((((DAT_febef093 == '\0') && (published_internal_source_admission_state < 2)) &&
      (DAT_febef094 == '\0')) && (400 < DAT_febef1b6)) {
    uVar3 = uVar3 + DAT_febef1b6;
    if (899999999 < uVar3) {
      uVar3 = 900000000;
    }
    uVar4 = (undefined2)(uVar3 / 36000);
    uVar5 = uVar4;
  }
  *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb872u + (uint32_t)(iVar1) * 1u)))) = uVar4;
  *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb868u + (uint32_t)(iVar1) * 1u)))) = uVar5;
  *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebebbdcu + (uint32_t)(iVar2) * 1u)))) = uVar3;
  return;
}

void refresh_control_profile_packed_metadata(uchar slot)

{
  uchar uVar1;
  uchar uVar2;
  uchar uVar3;
  uchar uVar4;
  uchar uVar5;
  uchar uVar6;
  
  uVar6 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb6b2u + (uint32_t)(slot) * 1u))));
  uVar5 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb6b7u + (uint32_t)(slot) * 1u))));
  uVar4 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb6bcu + (uint32_t)(slot) * 1u))));
  uVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb6c1u + (uint32_t)(slot) * 1u))));
  uVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb6c6u + (uint32_t)(slot) * 1u))));
  uVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb6cbu + (uint32_t)(slot) * 1u))));
  if ((DAT_febef0f8 == '\0') && (published_internal_source_admission_state < 2)) {
    uVar6 = ((volatile uint8_t *)camry_host_ptr(0xfebebe66u))[0];
    uVar5 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebebe66u + (uint32_t)(1) * 1u))));
    uVar4 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebebe66u + (uint32_t)(2) * 1u))));
    uVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebebe66u + (uint32_t)(3) * 1u))));
    uVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebebe66u + (uint32_t)(4) * 1u))));
    uVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebebe66u + (uint32_t)(5) * 1u))));
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb6b2u + (uint32_t)(slot) * 1u)))) = uVar6;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb6b7u + (uint32_t)(slot) * 1u)))) = uVar5;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb6bcu + (uint32_t)(slot) * 1u)))) = uVar4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb6c1u + (uint32_t)(slot) * 1u)))) = uVar3;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb6c6u + (uint32_t)(slot) * 1u)))) = uVar2;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb6cbu + (uint32_t)(slot) * 1u)))) = uVar1;
  return;
}

void refresh_control_profile_scalar_metadata(uchar slot)

{
  undefined1 uVar1;
  uint uVar2;
  uint uVar3;
  
  uVar3 = (uint)slot;
  uVar2 = *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebebbf0u + (uint32_t)(uVar3 * 4) * 1u))));
  uVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb6d0u + (uint32_t)(uVar3) * 1u))));
  if ((DAT_febef065 == '\0') && (published_internal_source_admission_state < 2)) {
    uVar2 = published_route31_numeric_scalar;
    uVar1 = DAT_febef067;
  }
  *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebebbf0u + (uint32_t)(uVar3 * 4) * 1u)))) = uVar2;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb6d0u + (uint32_t)(uVar3) * 1u)))) = uVar1;
  return;
}

void stage_control_profile(uchar slot,short capture_value)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  
  iVar2 = DAT_febebbd8;
  uVar3 = (uint)slot;
  iVar1 = uVar3 * 2;
  (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeb890u + (uint32_t)(uVar3) * 2u)))) = capture_value;
  (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeb89au + (uint32_t)(uVar3) * 2u)))) = ((int)(int16_t)DAT_febeb852);
  (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebeb8aeu + (uint32_t)(uVar3) * 2u)))) = *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb868u + (uint32_t)(iVar1) * 1u))));
  (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebeb8a4u + (uint32_t)(uVar3) * 2u)))) = *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb854u + (uint32_t)(iVar1) * 1u))));
  (*((volatile int32_t *)camry_host_ptr((uint32_t)(0xfebebc04u + (uint32_t)(uVar3) * 4u)))) = iVar2;
  (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebeb8b8u + (uint32_t)(uVar3) * 2u)))) = *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb78au + (uint32_t)(iVar1) * 1u))));
  (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebeb8c2u + (uint32_t)(uVar3) * 2u)))) = *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb780u + (uint32_t)(iVar1) * 1u))));
  (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeb8ccu + (uint32_t)(uVar3) * 2u)))) = *(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb7bcu + (uint32_t)(iVar1) * 1u))));
  (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeb8d6u + (uint32_t)(uVar3) * 2u)))) = *(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb7b2u + (uint32_t)(iVar1) * 1u))));
  (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeb8e0u + (uint32_t)(uVar3) * 2u)))) = *(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb7e4u + (uint32_t)(iVar1) * 1u))));
  (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeb8eau + (uint32_t)(uVar3) * 2u)))) = *(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb7dau + (uint32_t)(iVar1) * 1u))));
  (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeb8f4u + (uint32_t)(uVar3) * 2u)))) = *(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb80cu + (uint32_t)(iVar1) * 1u))));
  (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeb8feu + (uint32_t)(uVar3) * 2u)))) = *(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb802u + (uint32_t)(iVar1) * 1u))));
  (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeb908u + (uint32_t)(uVar3) * 2u)))) = *(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb83eu + (uint32_t)(iVar1) * 1u))));
  (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeb912u + (uint32_t)(uVar3) * 2u)))) = *(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb848u + (uint32_t)(iVar1) * 1u))));
  (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeb91cu + (uint32_t)(uVar3) * 2u)))) = *(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb834u + (uint32_t)(iVar1) * 1u))));
  (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeb926u + (uint32_t)(uVar3) * 2u)))) = *(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb82au + (uint32_t)(iVar1) * 1u))));
  (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebebc18u + (uint32_t)(uVar3) * 4u)))) = *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebebbf0u + (uint32_t)(uVar3 * 4) * 1u))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb6e4u + (uint32_t)(uVar3) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb6d0u + (uint32_t)(uVar3) * 1u))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb6e9u + (uint32_t)(uVar3) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb6b2u + (uint32_t)(uVar3) * 1u))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb6eeu + (uint32_t)(uVar3) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb6b7u + (uint32_t)(uVar3) * 1u))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb6f3u + (uint32_t)(uVar3) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb6bcu + (uint32_t)(uVar3) * 1u))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb6f8u + (uint32_t)(uVar3) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb6c1u + (uint32_t)(uVar3) * 1u))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb6fdu + (uint32_t)(uVar3) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb6c6u + (uint32_t)(uVar3) * 1u))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb702u + (uint32_t)(uVar3) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb6cbu + (uint32_t)(uVar3) * 1u))));
  return;
}

void select_and_stage_control_profile(uchar slot)

{
  short capture_value;
  
  capture_value = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeb504u + (uint32_t)(slot) * 2u))));
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb6dfu + (uint32_t)(slot) * 1u)))) != 'Z') &&
     (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb6dfu + (uint32_t)(slot) * 1u)))) != '\0' || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb4adu + (uint32_t)(slot) * 1u)))) != 'Z'))
     )) {
    capture_value = 0x7fff;
  }
  stage_control_profile(slot,capture_value);
  return;
}

void refresh_control_profile_working(uchar slot)

{
  age_control_profile_source_latch(slot);
  integrate_control_profile_unsigned_source(slot);
  refresh_control_profile_packed_metadata(slot);
  refresh_control_profile_scalar_metadata(slot);
  select_and_stage_control_profile(slot);
  return;
}

void retain_first_control_profile(uchar slot)

{
  (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeb930u + (uint32_t)(slot) * 2u)))) = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeb890u + (uint32_t)(slot) * 2u))));
  (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeb94eu + (uint32_t)(slot) * 2u)))) = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeb89au + (uint32_t)(slot) * 2u))));
  (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebeb98au + (uint32_t)(slot) * 2u)))) = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebeb8aeu + (uint32_t)(slot) * 2u))));
  (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebeb96cu + (uint32_t)(slot) * 2u)))) = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebeb8a4u + (uint32_t)(slot) * 2u))));
  (*((volatile int32_t *)camry_host_ptr((uint32_t)(0xfebebc2cu + (uint32_t)(slot) * 4u)))) = (*((volatile int32_t *)camry_host_ptr((uint32_t)(0xfebebc04u + (uint32_t)(slot) * 4u))));
  (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebeb9a8u + (uint32_t)(slot) * 2u)))) = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebeb8b8u + (uint32_t)(slot) * 2u))));
  (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebeb9c6u + (uint32_t)(slot) * 2u)))) = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebeb8c2u + (uint32_t)(slot) * 2u))));
  (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeb9e4u + (uint32_t)(slot) * 2u)))) = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeb8ccu + (uint32_t)(slot) * 2u))));
  (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeba02u + (uint32_t)(slot) * 2u)))) = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeb8d6u + (uint32_t)(slot) * 2u))));
  (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeba20u + (uint32_t)(slot) * 2u)))) = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeb8e0u + (uint32_t)(slot) * 2u))));
  (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeba3eu + (uint32_t)(slot) * 2u)))) = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeb8eau + (uint32_t)(slot) * 2u))));
  (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeba5cu + (uint32_t)(slot) * 2u)))) = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeb8f4u + (uint32_t)(slot) * 2u))));
  (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeba7au + (uint32_t)(slot) * 2u)))) = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeb8feu + (uint32_t)(slot) * 2u))));
  (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeba98u + (uint32_t)(slot) * 2u)))) = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeb908u + (uint32_t)(slot) * 2u))));
  (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebebab6u + (uint32_t)(slot) * 2u)))) = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeb912u + (uint32_t)(slot) * 2u))));
  (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebebad4u + (uint32_t)(slot) * 2u)))) = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeb91cu + (uint32_t)(slot) * 2u))));
  (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebebaf2u + (uint32_t)(slot) * 2u)))) = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeb926u + (uint32_t)(slot) * 2u))));
  (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebebc68u + (uint32_t)(slot) * 4u)))) = (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebebc18u + (uint32_t)(slot) * 4u))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb707u + (uint32_t)(slot) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb6e4u + (uint32_t)(slot) * 1u))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb716u + (uint32_t)(slot) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb6e9u + (uint32_t)(slot) * 1u))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb725u + (uint32_t)(slot) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb6eeu + (uint32_t)(slot) * 1u))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb734u + (uint32_t)(slot) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb6f3u + (uint32_t)(slot) * 1u))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb743u + (uint32_t)(slot) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb6f8u + (uint32_t)(slot) * 1u))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb752u + (uint32_t)(slot) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb6fdu + (uint32_t)(slot) * 1u))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb761u + (uint32_t)(slot) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb702u + (uint32_t)(slot) * 1u))));
  return;
}

void update_first_control_profile_retention(uchar slot)

{
  uchar uVar1;
  byte bVar2;
  byte bVar3;
  uchar uVar4;
  
  uVar4 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb6dfu + (uint32_t)(slot) * 1u))));
  uVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb4adu + (uint32_t)(slot) * 1u))));
  bVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb6d5u + (uint32_t)(slot) * 1u))));
  bVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb6dau + (uint32_t)(slot) * 1u))));
  if (uVar4 == '\0') {
    if ((bVar2 < 100) && (uVar1 != 'Z')) {
      bVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb6dau + (uint32_t)(slot) * 1u)))) + 1;
      bVar3 = bVar2;
    }
    else {
      retain_first_control_profile(slot);
      if (uVar1 == 'Z') {
        uVar4 = 'Z';
      }
      else {
        uVar4 = '\0';
      }
      bVar2 = 0;
      bVar3 = 0;
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb6d5u + (uint32_t)(slot) * 1u)))) = bVar2;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb6dau + (uint32_t)(slot) * 1u)))) = bVar3;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb6dfu + (uint32_t)(slot) * 1u)))) = uVar4;
  return;
}

void promote_ranked_control_profile(uchar slot)

{
  uint uVar1;
  
  uVar1 = (uint)slot;
  (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeb930u + (uint32_t)(uVar1 + 10) * 2u)))) = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeb930u + (uint32_t)(uVar1 + 5) * 2u))));
  (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeb94eu + (uint32_t)(uVar1 + 10) * 2u)))) =
       (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeb94eu + (uint32_t)(uVar1 + 5) * 2u))));
  (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebeb98au + (uint32_t)(uVar1 + 10) * 2u)))) =
       (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebeb98au + (uint32_t)(uVar1 + 5) * 2u))));
  (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebeb96cu + (uint32_t)(uVar1 + 10) * 2u)))) = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebeb96cu + (uint32_t)(uVar1 + 5) * 2u))));
  (*((volatile int32_t *)camry_host_ptr((uint32_t)(0xfebebc2cu + (uint32_t)(uVar1 + 10) * 4u)))) = (*((volatile int32_t *)camry_host_ptr((uint32_t)(0xfebebc2cu + (uint32_t)(uVar1 + 5) * 4u))));
  (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebeb9a8u + (uint32_t)(uVar1 + 10) * 2u)))) = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebeb9a8u + (uint32_t)(uVar1 + 5) * 2u))));
  (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebeb9c6u + (uint32_t)(uVar1 + 10) * 2u)))) = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebeb9c6u + (uint32_t)(uVar1 + 5) * 2u))))
  ;
  (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeb9e4u + (uint32_t)(uVar1 + 10) * 2u)))) = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeb9e4u + (uint32_t)(uVar1 + 5) * 2u))));
  (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeba02u + (uint32_t)(uVar1 + 10) * 2u)))) = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeba02u + (uint32_t)(uVar1 + 5) * 2u))));
  (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeba20u + (uint32_t)(uVar1 + 10) * 2u)))) = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeba20u + (uint32_t)(uVar1 + 5) * 2u))));
  (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeba3eu + (uint32_t)(uVar1 + 10) * 2u)))) = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeba3eu + (uint32_t)(uVar1 + 5) * 2u))));
  (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeba5cu + (uint32_t)(uVar1 + 10) * 2u)))) = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeba5cu + (uint32_t)(uVar1 + 5) * 2u))));
  (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeba7au + (uint32_t)(uVar1 + 10) * 2u)))) = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeba7au + (uint32_t)(uVar1 + 5) * 2u))));
  (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeba98u + (uint32_t)(uVar1 + 10) * 2u)))) = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeba98u + (uint32_t)(uVar1 + 5) * 2u))))
  ;
  (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebebab6u + (uint32_t)(uVar1 + 10) * 2u)))) = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebebab6u + (uint32_t)(uVar1 + 5) * 2u))))
  ;
  (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebebad4u + (uint32_t)(uVar1 + 10) * 2u)))) = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebebad4u + (uint32_t)(uVar1 + 5) * 2u))))
  ;
  (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebebaf2u + (uint32_t)(uVar1 + 10) * 2u)))) =
       (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebebaf2u + (uint32_t)(uVar1 + 5) * 2u))));
  (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebebc68u + (uint32_t)(uVar1 + 10) * 4u)))) = (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebebc68u + (uint32_t)(uVar1 + 5) * 4u))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb707u + (uint32_t)(uVar1 + 10) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb707u + (uint32_t)(uVar1 + 5) * 1u))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb716u + (uint32_t)(uVar1 + 10) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb716u + (uint32_t)(uVar1 + 5) * 1u))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb725u + (uint32_t)(uVar1 + 10) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb725u + (uint32_t)(uVar1 + 5) * 1u))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb734u + (uint32_t)(uVar1 + 10) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb734u + (uint32_t)(uVar1 + 5) * 1u))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb743u + (uint32_t)(uVar1 + 10) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb743u + (uint32_t)(uVar1 + 5) * 1u))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb752u + (uint32_t)(uVar1 + 10) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb752u + (uint32_t)(uVar1 + 5) * 1u))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb761u + (uint32_t)(uVar1 + 10) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb761u + (uint32_t)(uVar1 + 5) * 1u))));
  (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeb930u + (uint32_t)(uVar1 + 5) * 2u)))) = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeb890u + (uint32_t)(uVar1) * 2u))));
  (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeb94eu + (uint32_t)(uVar1 + 5) * 2u)))) = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeb89au + (uint32_t)(uVar1) * 2u))))
  ;
  (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebeb98au + (uint32_t)(uVar1 + 5) * 2u)))) = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebeb8aeu + (uint32_t)(uVar1) * 2u))));
  (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebeb96cu + (uint32_t)(uVar1 + 5) * 2u)))) = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebeb8a4u + (uint32_t)(uVar1) * 2u))));
  (*((volatile int32_t *)camry_host_ptr((uint32_t)(0xfebebc2cu + (uint32_t)(uVar1 + 5) * 4u)))) = (*((volatile int32_t *)camry_host_ptr((uint32_t)(0xfebebc04u + (uint32_t)(uVar1) * 4u))));
  (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebeb9a8u + (uint32_t)(uVar1 + 5) * 2u)))) = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebeb8b8u + (uint32_t)(uVar1) * 2u))));
  (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebeb9c6u + (uint32_t)(uVar1 + 5) * 2u)))) = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebeb8c2u + (uint32_t)(uVar1) * 2u))));
  (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeb9e4u + (uint32_t)(uVar1 + 5) * 2u)))) = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeb8ccu + (uint32_t)(uVar1) * 2u))));
  (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeba02u + (uint32_t)(uVar1 + 5) * 2u)))) = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeb8d6u + (uint32_t)(uVar1) * 2u))));
  (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeba20u + (uint32_t)(uVar1 + 5) * 2u)))) = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeb8e0u + (uint32_t)(uVar1) * 2u))));
  (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeba3eu + (uint32_t)(uVar1 + 5) * 2u)))) = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeb8eau + (uint32_t)(uVar1) * 2u))));
  (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeba5cu + (uint32_t)(uVar1 + 5) * 2u)))) = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeb8f4u + (uint32_t)(uVar1) * 2u))));
  (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeba7au + (uint32_t)(uVar1 + 5) * 2u)))) = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeb8feu + (uint32_t)(uVar1) * 2u))));
  (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeba98u + (uint32_t)(uVar1 + 5) * 2u)))) = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeb908u + (uint32_t)(uVar1) * 2u))));
  (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebebab6u + (uint32_t)(uVar1 + 5) * 2u)))) = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeb912u + (uint32_t)(uVar1) * 2u))));
  (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebebad4u + (uint32_t)(uVar1 + 5) * 2u)))) = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeb91cu + (uint32_t)(uVar1) * 2u))));
  (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebebaf2u + (uint32_t)(uVar1 + 5) * 2u)))) = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeb926u + (uint32_t)(uVar1) * 2u))));
  (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebebc68u + (uint32_t)(uVar1 + 5) * 4u)))) = (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebebc18u + (uint32_t)(uVar1) * 4u))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb707u + (uint32_t)(uVar1 + 5) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb6e4u + (uint32_t)(uVar1) * 1u))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb716u + (uint32_t)(uVar1 + 5) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb6e9u + (uint32_t)(uVar1) * 1u))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb725u + (uint32_t)(uVar1 + 5) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb6eeu + (uint32_t)(uVar1) * 1u))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb734u + (uint32_t)(uVar1 + 5) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb6f3u + (uint32_t)(uVar1) * 1u))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb743u + (uint32_t)(uVar1 + 5) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb6f8u + (uint32_t)(uVar1) * 1u))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb752u + (uint32_t)(uVar1 + 5) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb6fdu + (uint32_t)(uVar1) * 1u))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb761u + (uint32_t)(uVar1 + 5) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb702u + (uint32_t)(uVar1) * 1u))));
  return;
}

void replace_second_ranked_control_profile(uchar slot)

{
  uint uVar1;
  
  uVar1 = (uint)slot;
  (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeb930u + (uint32_t)(uVar1 + 10) * 2u)))) = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeb890u + (uint32_t)(uVar1) * 2u))));
  (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeb94eu + (uint32_t)(uVar1 + 10) * 2u)))) =
       (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeb89au + (uint32_t)(uVar1) * 2u))));
  (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebeb98au + (uint32_t)(uVar1 + 10) * 2u)))) = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebeb8aeu + (uint32_t)(uVar1) * 2u))));
  (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebeb96cu + (uint32_t)(uVar1 + 10) * 2u)))) = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebeb8a4u + (uint32_t)(uVar1) * 2u))));
  (*((volatile int32_t *)camry_host_ptr((uint32_t)(0xfebebc2cu + (uint32_t)(uVar1 + 10) * 4u)))) = (*((volatile int32_t *)camry_host_ptr((uint32_t)(0xfebebc04u + (uint32_t)(uVar1) * 4u))));
  (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebeb9a8u + (uint32_t)(uVar1 + 10) * 2u)))) = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebeb8b8u + (uint32_t)(uVar1) * 2u))));
  (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebeb9c6u + (uint32_t)(uVar1 + 10) * 2u)))) = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebeb8c2u + (uint32_t)(uVar1) * 2u))));
  (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeb9e4u + (uint32_t)(uVar1 + 10) * 2u)))) = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeb8ccu + (uint32_t)(uVar1) * 2u))));
  (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeba02u + (uint32_t)(uVar1 + 10) * 2u)))) = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeb8d6u + (uint32_t)(uVar1) * 2u))));
  (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeba20u + (uint32_t)(uVar1 + 10) * 2u)))) = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeb8e0u + (uint32_t)(uVar1) * 2u))));
  (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeba3eu + (uint32_t)(uVar1 + 10) * 2u)))) = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeb8eau + (uint32_t)(uVar1) * 2u))));
  (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeba5cu + (uint32_t)(uVar1 + 10) * 2u)))) = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeb8f4u + (uint32_t)(uVar1) * 2u))));
  (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeba7au + (uint32_t)(uVar1 + 10) * 2u)))) = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeb8feu + (uint32_t)(uVar1) * 2u))));
  (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeba98u + (uint32_t)(uVar1 + 10) * 2u)))) = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeb908u + (uint32_t)(uVar1) * 2u))));
  (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebebab6u + (uint32_t)(uVar1 + 10) * 2u)))) = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeb912u + (uint32_t)(uVar1) * 2u))));
  (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebebad4u + (uint32_t)(uVar1 + 10) * 2u)))) = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeb91cu + (uint32_t)(uVar1) * 2u))));
  (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebebaf2u + (uint32_t)(uVar1 + 10) * 2u)))) = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeb926u + (uint32_t)(uVar1) * 2u))));
  (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebebc68u + (uint32_t)(uVar1 + 10) * 4u)))) = (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebebc18u + (uint32_t)(uVar1) * 4u))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb707u + (uint32_t)(uVar1 + 10) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb6e4u + (uint32_t)(uVar1) * 1u))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb716u + (uint32_t)(uVar1 + 10) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb6e9u + (uint32_t)(uVar1) * 1u))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb725u + (uint32_t)(uVar1 + 10) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb6eeu + (uint32_t)(uVar1) * 1u))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb734u + (uint32_t)(uVar1 + 10) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb6f3u + (uint32_t)(uVar1) * 1u))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb743u + (uint32_t)(uVar1 + 10) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb6f8u + (uint32_t)(uVar1) * 1u))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb752u + (uint32_t)(uVar1 + 10) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb6fdu + (uint32_t)(uVar1) * 1u))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb761u + (uint32_t)(uVar1 + 10) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb702u + (uint32_t)(uVar1) * 1u))));
  return;
}

void rank_control_profile_magnitude(uchar slot)

{
  short sVar1;
  short sVar2;
  short sVar3;
  int iVar4;
  int iVar5;
  short sVar6;
  int iVar7;
  
  sVar2 = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeb504u + (uint32_t)(slot) * 2u))));
  iVar5 = (int)sVar2;
  sVar1 = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeb87cu + (uint32_t)(slot) * 2u))));
  iVar7 = (int)sVar1;
  sVar3 = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeb886u + (uint32_t)(slot) * 2u))));
  iVar4 = (int)sVar3;
  if (iVar5 + 0x7fff < 0 == (-1 < iVar5 && iVar5 + 0x7fff < 0) && iVar5 != -0x7fff) {
    if (iVar5 < 0) {
      iVar5 = (int)-sVar2;
    }
  }
  else {
    iVar5 = 0x7fff;
  }
  if (iVar7 + 0x7fff < 0 == (-1 < iVar7 && iVar7 + 0x7fff < 0) && iVar7 != -0x7fff) {
    if (iVar7 < 0) {
      iVar7 = (int)-sVar1;
    }
  }
  else {
    iVar7 = 0x7fff;
  }
  if (iVar4 + 0x7fff < 0 == (-1 < iVar4 && iVar4 + 0x7fff < 0) && iVar4 != -0x7fff) {
    if (iVar4 < 0) {
      iVar4 = (int)-sVar3;
    }
  }
  else {
    iVar4 = 0x7fff;
  }
  sVar6 = sVar1;
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb4adu + (uint32_t)(slot) * 1u)))) == 'Z') {
    if (iVar7 - iVar5 < 0 == (iVar7 < 0 != iVar5 < 0 && iVar5 < 0 == iVar7 - iVar5 < 0)) {
      if (iVar4 - iVar5 < 0 != (iVar4 < 0 != iVar5 < 0 && iVar5 < 0 == iVar4 - iVar5 < 0)) {
        replace_second_ranked_control_profile(slot);
        sVar3 = sVar2;
      }
    }
    else {
      promote_ranked_control_profile(slot);
      sVar6 = sVar2;
      sVar3 = sVar1;
    }
  }
  (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeb87cu + (uint32_t)(slot) * 2u)))) = sVar6;
  (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeb886u + (uint32_t)(slot) * 2u)))) = sVar3;
  return;
}

void run_control_profile_retention(void)

{
  uchar slot;
  uint uVar1;
  
  refresh_profile_scaled_word();
  refresh_profile_received_composite();
  uVar1 = 0;
  do {
    slot = (uchar)uVar1;
    update_control_profile_aggregates(slot);
    refresh_control_profile_working(slot);
    update_first_control_profile_retention(slot);
    rank_control_profile_magnitude(slot);
    uVar1 = uVar1 + 1;
  } while (uVar1 < 5);
  return;
}

void return_only_stub_ba8ac(void)

{
  return;
}

void return_only_stub_ba8ae(void)

{
  return;
}

void update_saturated_afe8_ratio_and_range_admission_ba8b0(void)

{
  int iVar1;
  uint uVar2;
  
  iVar1 = -DAT_febeafe8;
  uVar2 = (uint)(DAT_febeb138 >> 2);
  if (uVar2 != 0) {
    if (iVar1 + -0x7fffff < 0 == (iVar1 < 0 && -1 < iVar1 + -0x7fffff)) {
      iVar1 = 0x7fffff;
    }
    if (iVar1 + 0x7fffff < 0 != (-1 < iVar1 && iVar1 + 0x7fffff < 0)) {
      iVar1 = -0x7fffff;
    }
    iVar1 = iVar1 << 8;
    if (uVar2 != 0) {
      if (iVar1 == -0x80000000 && uVar2 == 0xffffffff) {
        iVar1 = -0x80000000;
      }
      else {
        iVar1 = iVar1 / (int)uVar2;
      }
    }
    iVar1 = ((iVar1 / 4) * 0x188b) / 0x4000;
    if (iVar1 + -0x7fff < 0 == (iVar1 < 0 && -1 < iVar1 + -0x7fff)) {
      iVar1 = 0x7fff;
    }
    if (iVar1 + 0x8000 < 0 == (-1 < iVar1 && iVar1 + 0x8000 < 0)) {
      DAT_febebca6 = (undefined2)iVar1;
    }
    else {
      DAT_febebca6 = 0x8000;
    }
  }
  if ((DAT_febeb1a4 == '\x11') && (DAT_febeb079 == '\0')) {
    if (((DAT_000aee28 <= DAT_febeb080) && (DAT_febeb080 <= DAT_000aee2a)) ||
       ((DAT_000aee2c <= DAT_febeb086 && (DAT_febeb086 <= DAT_000aee2e)))) {
      DAT_febebca4 = 0;
      return;
    }
    if (DAT_000aee2c <= DAT_febeb088) {
      DAT_febebca4 = DAT_000aee2e < DAT_febeb088;
      return;
    }
  }
  DAT_febebca4 = 1;
  return;
}

void return_only_stub_ba960(void)

{
  return;
}

void reset_owner5_release_state(void)

{
  DAT_febebca8 = 0;
  DAT_febebcac = 0;
  DAT_febebcb8 = 0;
  DAT_febebca9 = 0;
  DAT_febebcae = 0;
  DAT_febebcb0 = 0;
  DAT_febebcb4 = 0;
  DAT_febebcaa = 0;
  DAT_febebcab = 0x5a;
  return;
}

uint decay_owner5_limit_request(void)

{
  uint8_t stack_record_22[34];
  ushort uVar1;
  char cVar2;
  uint32_t puVar3;
  uint uVar4;
  char cVar5;
  uint coefficient;
  
  cVar2 = DAT_febeb20f;
  puVar3 = 0xfebeb800u;
  ((uint16_t *)((stack_record_22 + 6)))[0] = DAT_febebcb0;
  ((uint16_t *)((stack_record_22 + 6)))[1] = 0;
  (*((int32_t *)(stack_record_22 + 10))) = DAT_febebcb4;
  coefficient = DAT_febebcb8;
  cVar5 = DAT_febebca9;
  if (DAT_febebca9 == '\0') {
    uVar1 = DAT_000af030;
    if (DAT_febebee2 <= DAT_000af032) {
      uVar1 = DAT_000af02e;
    }
    (*((uint16_t *)(stack_record_22 + 0))) = DAT_febebccc;
    ((uint16_t *)((stack_record_22 + 6)))[0] = DAT_febebccc;
    cVar5 = 'Z';
    coefficient = (uint)uVar1 * 0x32;
    (*((int32_t *)(stack_record_22 + 10))) = (uint)DAT_febebccc << 0x10;
  }
  filter_unsigned_sample_accumulator(((uint16_t *)((stack_record_22 + 6))),coefficient,((uint16_t *)(stack_record_22)),((uint32_t *)((stack_record_22 + 2))));
  uVar1 = DAT_000af02a;
  if (cVar2 == 'Z') {
    uVar1 = DAT_000af02c;
  }
  uVar4 = (uint)(*((uint16_t *)(stack_record_22 + 0)));
  if (uVar4 <= uVar1) {
    (*((uint32_t *)(stack_record_22 + 2))) = 0;
    uVar4 = 0;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x4a8))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x4a9))))) = cVar5;
  (*((uint *)camry_host_ptr((uint32_t)(puVar3 + 0x4b8)))) = coefficient;
  (*((uint *)camry_host_ptr((uint32_t)(puVar3 + 0x4b4)))) = (*((uint32_t *)(stack_record_22 + 2)));
  return uVar4;
}

uint release_owner5_limit_request(uint target)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  char cVar7;
  uint uVar8;
  
  uVar2 = target & 0xffff;
  iVar1 = (int)((int)(int16_t)DAT_febeb054);
  uVar8 = (uint)DAT_febebcb0;
  uVar5 = (uint)DAT_febebcae;
  uVar6 = (uint)DAT_febebcac;
  if (iVar1 + 0x7fff < 0 == (-1 < iVar1 && iVar1 + 0x7fff < 0) && iVar1 != -0x7fff) {
    if (iVar1 < 0) {
      iVar1 = (int)-((int)(int16_t)DAT_febeb054);
    }
  }
  else {
    iVar1 = 0x7fff;
  }
  if (uVar8 < uVar2) {
    iVar3 = (int)DAT_000af026;
    if (((DAT_febebede < DAT_000af028) && (DAT_febebef0 == '\x11')) || (DAT_febeb118 == 'Z')) {
      cVar7 = '\x02';
      uVar4 = owner5_fast_release_coefficient;
    }
    else {
      if ((iVar1 - iVar3 < 0 != (iVar1 < 0 != iVar3 < 0 && iVar3 < 0 == iVar1 - iVar3 < 0) ||
           iVar1 == iVar3) && (uVar8 <= DAT_000af024)) {
        cVar7 = '\0';
        uVar2 = uVar8;
        goto LAB_000baac4;
      }
      cVar7 = '\x01';
      uVar4 = owner5_normal_release_coefficient;
    }
    if (cVar7 != DAT_febebca8) {
      uVar6 = 0;
      uVar5 = uVar8;
    }
    if (uVar6 < 0xffff) {
      uVar6 = uVar6 + 1 & 0xffff;
    }
    if (((int)((ulonglong)uVar4 * (ulonglong)(uVar6 * uVar6) >> 0x20) == 0) &&
       (uVar8 = (uVar6 * uVar6 * uVar4 >> 0x10) + uVar5, (int)(uVar8 - uVar2) < 0 || uVar8 == uVar2)
       ) {
      uVar2 = uVar8 & 0xffff;
    }
  }
  else {
    cVar7 = '\0';
  }
LAB_000baac4:
  DAT_febebca8 = cVar7;
  DAT_febebcac = (short)uVar6;
  DAT_febebcae = (short)uVar5;
  DAT_febebcb4 = uVar2 << 0x10;
  DAT_febebca9 = 0;
  return uVar2;
}

void publish_owner5_limit_request(void)

{
  uint32_t puVar1;
  undefined1 uVar2;
  undefined1 uVar3;
  uint uVar4;
  
  puVar1 = (0xfebeb800u);
  uVar2 = 0;
  uVar4 = (uint)DAT_febebcb0;
  if (((DAT_febeb20e == '\x11') || (DAT_febeb20e == '\"')) || (DAT_febeb1bc == 'Z')) {
    if (((DAT_febeb11a & 0xff00) != 0x500) || (puVar1 = (0xfebeb800u), uVar4 != 0)) {
      puVar1 = (0xfebeb800u);
      uVar4 = decay_owner5_limit_request();
    }
    uVar2 = 0x5a;
    uVar3 = uVar2;
  }
  else {
    uVar3 = DAT_febebcab;
    if (DAT_febeb1a4 == '\x11') {
      puVar1 = (0xfebeb800u);
      uVar4 = release_owner5_limit_request(0x569a);
      uVar3 = 0xa5;
    }
  }
  if (0x5699 < uVar4) {
    uVar3 = 0;
  }
  set_current_limit_request(5,(ushort)uVar4);
  *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(0x4b0) * 1u)))) = (ushort)uVar4;
  (*((volatile undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(0x4ab) * 1u)))) = uVar3;
  (*((volatile undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(0x4aa) * 1u)))) = uVar2;
  return;
}

void return_only_stub_bab56(void)

{
  return;
}

void reset_owner4_release_state(void)

{
  DAT_febebcc0 = 0x569a;
  DAT_febebcc2 = 0x569a;
  DAT_febebcbc = 0;
  DAT_febebcbd = 0;
  DAT_febebcbe = 0;
  DAT_febebcc4 = 0x569a0000;
  return;
}

uint release_owner4_limit_request(void)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  char cVar6;
  uint uVar7;
  
  iVar1 = (int)((int)(int16_t)DAT_febeb054);
  uVar7 = (uint)DAT_febebcc2;
  uVar4 = (uint)DAT_febebcc0;
  uVar5 = (uint)DAT_febebcbe;
  if (iVar1 + 0x7fff < 0 == (-1 < iVar1 && iVar1 + 0x7fff < 0) && iVar1 != -0x7fff) {
    if (iVar1 < 0) {
      iVar1 = (int)-((int)(int16_t)DAT_febeb054);
    }
  }
  else {
    iVar1 = 0x7fff;
  }
  if (uVar7 < 0x569a) {
    iVar2 = (int)DAT_000af03e;
    if ((DAT_febebee2 < DAT_000af040) && (DAT_febebef0 == '\x11')) {
      cVar6 = '\x02';
      uVar3 = owner4_fast_release_coefficient;
    }
    else {
      if ((iVar1 - iVar2 < 0 != (iVar1 < 0 != iVar2 < 0 && iVar2 < 0 == iVar1 - iVar2 < 0) ||
           iVar1 == iVar2) && (uVar7 <= DAT_000af03c)) {
        cVar6 = '\0';
        goto LAB_000bac1e;
      }
      cVar6 = '\x01';
      uVar3 = owner4_normal_release_coefficient;
    }
    if (cVar6 != DAT_febebcbc) {
      uVar5 = 0;
      uVar4 = uVar7;
    }
    if (uVar5 < 0xffff) {
      uVar5 = uVar5 + 1 & 0xffff;
    }
    if (((int)((ulonglong)uVar3 * (ulonglong)(uVar5 * uVar5) >> 0x20) == 0) &&
       (uVar7 = (uVar5 * uVar5 * uVar3 >> 0x10) + uVar4,
       (int)(uVar7 - 0x569a) < 0 || uVar7 == 0x569a)) {
      uVar7 = uVar7 & 0xffff;
    }
    else {
      uVar7 = 0x569a;
    }
  }
  else {
    cVar6 = '\0';
    uVar7 = 0x569a;
  }
LAB_000bac1e:
  DAT_febebcc4 = 0;
  DAT_febebcbc = cVar6;
  DAT_febebcbe = (short)uVar5;
  DAT_febebcc0 = (short)uVar4;
  return uVar7;
}

uint force_owner4_nominal_request(void)

{
  DAT_febebcbc = 0;
  DAT_febebcc4 = 0;
  return 0x569a;
}

uint decay_owner4_limit_request(uint coefficient)

{
  uint8_t stack_record_12[18];
  uint32_t puVar1;
  uint uVar2;
  ushort auStack_c [2];
  
  puVar1 = 0xfebeb800u;
  auStack_c[1] = 0;
  (*((uint32_t *)(stack_record_12 + 10))) = DAT_febebcc4;
  auStack_c[0] = DAT_febebcc2;
  if (DAT_febebcc4 >> 0x10 != (uint)DAT_febebcc2) {
    auStack_c[0] = DAT_febebccc;
    (*((uint32_t *)(stack_record_12 + 10))) = (uint)DAT_febebccc << 0x10;
  }
  filter_unsigned_sample_accumulator
            (auStack_c,(coefficient & 0xffff) * 0x32,stack_record_12,(stack_record_12 + 2));
  uVar2 = (uint)(*((uint16_t *)(stack_record_12 + 0)));
  if (uVar2 <= DAT_000af042) {
    (*((uint32_t *)(stack_record_12 + 2))) = 0;
    uVar2 = 0;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x4bc))))) = 0;
  (*((uint *)camry_host_ptr((uint32_t)(puVar1 + 0x4c4)))) = (*((uint32_t *)(stack_record_12 + 2)));
  return uVar2;
}

uint force_owner4_zero_request(void)

{
  DAT_febebcbc = 0;
  DAT_febebcc4 = 0;
  return 0;
}

uint publish_owner4_limit_request(void)

{
  uint32_t puVar1;
  ushort uVar2;
  uint uVar3;
  
  puVar1 = 0xfebeb800u;
  if (DAT_febebcbd != '\0') {
    if (DAT_febebcbd == '\x01') {
      uVar3 = force_owner4_nominal_request();
      uVar2 = (ushort)uVar3;
      goto LAB_000bace6;
    }
    uVar2 = DAT_000af044;
    if ((DAT_febebcbd == '\x02') || (uVar2 = DAT_000af046, DAT_febebcbd == '\x03')) {
      uVar3 = decay_owner4_limit_request((uint)uVar2);
      uVar2 = (ushort)uVar3;
      goto LAB_000bace6;
    }
    if (DAT_febebcbd == '\x04') {
      uVar3 = force_owner4_zero_request();
      uVar2 = (ushort)uVar3;
      goto LAB_000bace6;
    }
  }
  uVar3 = release_owner4_limit_request();
  uVar2 = (ushort)uVar3;
LAB_000bace6:
  set_current_limit_request(4,uVar2);
  (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + 0x4c2)))) = uVar2;
  return uVar3;
}

void return_only_stub_bacfe(void)

{
  return;
}

void return_only_stub_bad00(void)

{
  return;
}

void stage_absolute_limit_seeds(void)

{
  int iVar1;
  int iVar2;
  
  iVar1 = (int)((int)(int16_t)DAT_febeafe2);
  iVar2 = (int)((int)(int16_t)DAT_febeafe0);
  if (iVar1 + 0x7fff < 0 == (-1 < iVar1 && iVar1 + 0x7fff < 0) && iVar1 != -0x7fff) {
    if (iVar1 < 0) {
      iVar1 = (int)-((int)(int16_t)DAT_febeafe2);
    }
  }
  else {
    iVar1 = 0x7fff;
  }
  if (iVar2 + 0x7fff < 0 == (-1 < iVar2 && iVar2 + 0x7fff < 0) && iVar2 != -0x7fff) {
    if (iVar2 < 0) {
      iVar2 = (int)-((int)(int16_t)DAT_febeafe0);
    }
  }
  else {
    iVar2 = 0x7fff;
  }
  DAT_febebccc = (undefined2)iVar1;
  DAT_febebcc8 = DAT_febebccc;
  DAT_febebcca = (short)iVar2;
  if (iVar2 - iVar1 < 0 != (iVar2 < 0 != iVar1 < 0 && iVar1 < 0 == iVar2 - iVar1 < 0)) {
    DAT_febebccc = (short)iVar2;
  }
  return;
}

void return_only_stub_bad44(void)

{
  return;
}

void reset_owner8_release_state(void)

{
  DAT_febebcd4 = 0x569a;
  DAT_febebcd6 = 0x569a;
  DAT_febebcd0 = 0;
  DAT_febebcd2 = 0;
  DAT_febebcdc = 0x569a0000;
  return;
}

uint follow_owner8_qualification_floor(uint coefficient)

{
  uint8_t stack_record_1e[30];
  uint32_t puVar1;
  uint uVar2;
  uint uVar3;
  ushort uVar4;
  
  uVar4 = DAT_febebcd8;
  puVar1 = 0xfebeb800u;
  if (DAT_febebcd8 < DAT_000aef9c) {
    uVar2 = (uint)DAT_febebcd6;
    uVar4 = DAT_febebcd8 + 1;
  }
  else {
    uVar3 = (uint)DAT_febeb08a;
    (*((uint32_t *)(stack_record_1e + 10))) = DAT_febebcdc;
    (*((uint16_t *)(stack_record_1e + 8))) = DAT_febeb08a;
    (*((uint16_t *)(stack_record_1e + 6))) = DAT_febebcd6;
    if (DAT_febebcdc >> 0x10 != (uint)DAT_febebcd6) {
      (*((uint16_t *)(stack_record_1e + 6))) = DAT_febebcc8;
      (*((uint32_t *)(stack_record_1e + 10))) = (uint)DAT_febebcc8 << 0x10;
    }
    puVar1 = 0xfebeb800u;
    filter_unsigned_sample_accumulator
              (((uint16_t *)((stack_record_1e + 6))),(coefficient & 0xffff) * 0x32,((uint16_t *)(stack_record_1e)),((uint32_t *)((stack_record_1e + 2))));
    uVar2 = (uint)(*((uint16_t *)(stack_record_1e + 0)));
    if ((uint)(*((uint16_t *)(stack_record_1e + 0))) < DAT_000aef96 + uVar3) {
      (*((uint32_t *)(stack_record_1e + 2))) = uVar3 << 0x10;
      uVar2 = uVar3;
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x4d0))))) = 0;
    (*((uint *)camry_host_ptr((uint32_t)(puVar1 + 0x4dc)))) = (*((uint32_t *)(stack_record_1e + 2)));
  }
  (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + 0x4d8)))) = uVar4;
  return uVar2;
}

uint release_owner8_limit_request(void)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  char cVar5;
  int iVar6;
  uint uVar7;
  
  iVar1 = (int)((int)(int16_t)DAT_febeb054);
  uVar7 = (uint)DAT_febebcd6;
  uVar3 = (uint)DAT_febebcd4;
  uVar4 = (uint)DAT_febebcd2;
  if (iVar1 + 0x7fff < 0 == (-1 < iVar1 && iVar1 + 0x7fff < 0) && iVar1 != -0x7fff) {
    if (iVar1 < 0) {
      iVar1 = (int)-((int)(int16_t)DAT_febeb054);
    }
  }
  else {
    iVar1 = 0x7fff;
  }
  if (uVar7 < 0x569a) {
    if ((DAT_febebee2 < DAT_000aef94) && (DAT_febebef0 == '\x11')) {
      cVar5 = '\x02';
      uVar2 = owner8_fast_release_coefficient;
    }
    else {
      iVar6 = (int)DAT_000aef92;
      if ((iVar1 - iVar6 < 0 != (iVar1 < 0 != iVar6 < 0 && iVar6 < 0 == iVar1 - iVar6 < 0) ||
           iVar1 == iVar6) && (uVar7 <= DAT_000aef90)) {
        cVar5 = '\0';
        goto LAB_000bae8e;
      }
      cVar5 = '\x01';
      uVar2 = owner8_normal_release_coefficient;
    }
    if (cVar5 != DAT_febebcd0) {
      uVar4 = 0;
      uVar3 = uVar7;
    }
    if (uVar4 < 0xffff) {
      uVar4 = uVar4 + 1 & 0xffff;
    }
    if (((int)((ulonglong)uVar2 * (ulonglong)(uVar4 * uVar4) >> 0x20) == 0) &&
       (uVar7 = (uVar4 * uVar4 * uVar2 >> 0x10) + uVar3,
       (int)(uVar7 - 0x569a) < 0 || uVar7 == 0x569a)) {
      uVar7 = uVar7 & 0xffff;
    }
    else {
      uVar7 = 0x569a;
    }
  }
  else {
    cVar5 = '\0';
    uVar7 = 0x569a;
  }
LAB_000bae8e:
  DAT_febebcdc = 0;
  DAT_febebcd0 = cVar5;
  DAT_febebcd2 = (short)uVar4;
  DAT_febebcd4 = (short)uVar3;
  DAT_febebcd8 = 0;
  return uVar7;
}

uint publish_owner8_limit_request(void)

{
  uint32_t puVar1;
  ushort limit;
  uint uVar2;
  
  puVar1 = 0xfebeb800u;
  if ((DAT_febeb082 & 3) == 0) {
    uVar2 = release_owner8_limit_request();
    limit = (ushort)uVar2;
  }
  else {
    uVar2 = follow_owner8_qualification_floor((uint)DAT_000aef98);
    limit = (ushort)uVar2;
  }
  set_current_limit_request(8,limit);
  (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + 0x4d6)))) = limit;
  return uVar2;
}

void return_only_stub_baee4(void)

{
  return;
}

void reset_owner1_qualification_state(void)

{
  DAT_febebce2 = 0x5a;
  DAT_febebce0 = 0;
  DAT_febebce4 = 0;
  DAT_febebce5 = 0;
  DAT_febebce1 = 0;
  DAT_febebce3 = 0;
  DAT_febebce8 = 0x569a;
  DAT_febebce6 = 0;
  DAT_febebcec = 0;
  return;
}

void initialize_owner1_persisted_admission(void)

{
  int iVar1;
  int iVar2;
  
  if (DAT_febef027 == 'Z') {
    if ((DAT_febef1e0 == 0) &&
       (iVar2 = (int)DAT_000af060, iVar1 = ((int)(int16_t)DAT_febef182) - iVar2,
       iVar1 < 0 != (((int)(int16_t)DAT_febef182) < 0 != iVar2 < 0 && iVar2 < 0 == iVar1 < 0))) {
      DAT_febebce2 = 0x5a;
    }
    else {
      DAT_febebce2 = 0;
    }
    DAT_febebce3 = 0x5a;
  }
  return;
}

void qualify_owner1_limit_state(void)

{
  uint8_t stack_record_4a[74];
  short sVar1;
  ushort uVar2;
  int iVar3;
  uint32_t puVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  short sVar8;
  int iVar9;
  char cVar10;
  byte bVar11;
  byte bVar12;
  char cVar13;
  
  puVar4 = 0xfebeb800u;
  if (DAT_febebce3 == '\0') {
    puVar4 = 0xfebeb800u;
    initialize_owner1_persisted_admission();
  }
  (*((int16_t *)(stack_record_4a + 22))) = (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x3974))));
  (*((int32_t *)(stack_record_4a + 18))) = (*((int *)camry_host_ptr((uint32_t)(puVar4 + -0x80c))));
  iVar9 = 0;
  (*((uint16_t *)(stack_record_4a + 24))) = (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + -0x77e))));
  (*((int16_t *)(stack_record_4a + 26))) = (*((short *)camry_host_ptr((uint32_t)(puVar4 + -0x820))));
  (*((int16_t *)(stack_record_4a + 28))) = (*((short *)camry_host_ptr((uint32_t)(puVar4 + -0x824))));
  (*((int16_t *)(stack_record_4a + 6))) = (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x4e8))));
  cVar13 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x4e0)))));
  bVar12 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x4e4)))));
  bVar11 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x4e5)))));
  cVar10 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x4e1)))));
  uVar2 = (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + 0x6e2))));
  sVar1 = (*((short *)camry_host_ptr((uint32_t)(puVar4 + -0x7ac))));
  iVar3 = (int)(*((short *)camry_host_ptr((uint32_t)(puVar4 + -0x7f4))));
  sVar8 = (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x4e6))));
  iVar7 = (*((int *)camry_host_ptr((uint32_t)(puVar4 + 0x4ec))));
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x65c))))) == '\x11') && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x658))))) == '\0')) {
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6ee))))) == 'Z') {
LAB_000bafde:
      cVar10 = '\0';
      cVar13 = '\0';
      bVar11 = 0;
      bVar12 = 0;
      goto LAB_000baff6;
    }
    if (cVar10 != 'Z') {
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x4e2))))) != '\0') {
        iVar6 = (int)DAT_000af05a;
        iVar5 = (int)(*((int16_t *)(stack_record_4a + 22)));
        if (iVar5 - iVar6 < 0 != (iVar5 < 0 != iVar6 < 0 && iVar6 < 0 == iVar5 - iVar6 < 0) ||
            iVar5 == iVar6) goto LAB_000bafde;
      }
      cVar10 = 'Z';
    }
    if (DAT_000af056 < uVar2) goto LAB_000baff6;
  }
  else {
    cVar10 = '\0';
    cVar13 = '3';
    bVar12 = 0;
    bVar11 = 0;
    iVar3 = 0x569a;
LAB_000baff6:
    iVar5 = (int)DAT_000af0c6;
    if (iVar3 - iVar5 < 0 == (iVar3 < 0 != iVar5 < 0 && iVar5 < 0 == iVar3 - iVar5 < 0)) {
      cVar13 = '3';
      goto LAB_000bb150;
    }
  }
  if ((int)sVar8 * (int)sVar1 < 0) {
    iVar9 = 0x5a;
  }
  (*((int32_t *)(stack_record_4a + 2))) = (*((int32_t *)(stack_record_4a + 18))) - iVar7;
  store_saturated_signed32_absolute_d1194((*((int32_t *)(stack_record_4a + 2))),((int32_t *)((stack_record_4a + 2))));
  store_saturated_signed16_absolute_d1178((int)sVar1,((int16_t *)(stack_record_4a)));
  store_saturated_signed16_absolute_d1178((int)(*((int16_t *)(stack_record_4a + 28))),((int16_t *)((stack_record_4a + 10))));
  store_saturated_signed16_absolute_d1178((int)(*((int16_t *)(stack_record_4a + 26))),((int16_t *)((stack_record_4a + 8))));
  sVar8 = DAT_000af066;
  if (((*((uint16_t *)(stack_record_4a + 24))) & 3) == 0) {
    sVar8 = DAT_000af064;
  }
  iVar3 = (int)sVar8;
  if ((cVar13 == '\0') || (cVar13 == '3')) {
    iVar6 = (int)DAT_000af05e;
    iVar5 = (*((int16_t *)(stack_record_4a + 0))) - iVar6;
    if (iVar5 < 0 != ((*((int16_t *)(stack_record_4a + 0))) < 0 != iVar6 < 0 && iVar6 < 0 == iVar5 < 0)) {
LAB_000bb0ae:
      bVar12 = 0;
      goto LAB_000bb0b0;
    }
    if (bVar12 == 0) {
      bVar12 = 1;
      iVar7 = (*((int32_t *)(stack_record_4a + 18)));
      goto LAB_000bb0b0;
    }
    iVar5 = (int)DAT_000af058;
    if (((*((int32_t *)(stack_record_4a + 2))) - iVar5 < 0 == ((*((int32_t *)(stack_record_4a + 2))) < 0 != iVar5 < 0 && iVar5 < 0 == (*((int32_t *)(stack_record_4a + 2))) - iVar5 < 0)
        ) && ((iVar6 = (int)DAT_000af062, iVar5 = (*((int16_t *)(stack_record_4a + 10))) - iVar6,
              iVar5 < 0 == ((*((int16_t *)(stack_record_4a + 10))) < 0 != iVar6 < 0 && iVar6 < 0 == iVar5 < 0) ||
              (iVar5 = (*((int16_t *)(stack_record_4a + 8))) - iVar3,
              iVar5 < 0 != ((*((int16_t *)(stack_record_4a + 8))) < 0 != iVar3 < 0 && iVar3 < 0 == iVar5 < 0)))))
    goto LAB_000bb0ae;
    if (bVar12 < DAT_000af054) {
      bVar12 = bVar12 + 1;
      goto LAB_000bb0b0;
    }
    cVar13 = '\x11';
LAB_000bb0b6:
    if ((*((int32_t *)(stack_record_4a + 2))) - DAT_000af068 < 0 ==
        ((*((int32_t *)(stack_record_4a + 2))) < 0 != DAT_000af068 < 0 && DAT_000af068 < 0 == (*((int32_t *)(stack_record_4a + 2))) - DAT_000af068 < 0)) {
      cVar13 = '\"';
    }
LAB_000bb0ce:
    iVar5 = (int)DAT_000af05c;
    iVar3 = (*((int16_t *)(stack_record_4a + 0))) - iVar5;
    if (iVar3 < 0 == ((*((int16_t *)(stack_record_4a + 0))) < 0 != iVar5 < 0 && iVar5 < 0 == iVar3 < 0)) {
      bVar11 = 0;
    }
    else if (bVar11 < DAT_000af055) {
      bVar11 = bVar11 + 1;
    }
    else {
      bVar12 = 0;
      bVar11 = 0;
      cVar13 = '\0';
    }
    if (iVar9 == 0x5a) {
      bVar12 = 0;
      bVar11 = 0;
      cVar13 = '\0';
    }
  }
  else {
LAB_000bb0b0:
    if (cVar13 == '\x11') goto LAB_000bb0b6;
    if (cVar13 == '\"') goto LAB_000bb0ce;
  }
  sVar8 = sVar1;
  if (cVar13 == '\"') {
    interpolate_signed16_pairs_to_output_d1de4(((undefined *)camry_host_ptr(0xaf06cu)),(int)(*((int16_t *)(stack_record_4a + 22))),((int16_t *)((stack_record_4a + 6))));
    interpolate_unsigned16_pairs_to_output_d1ee0(((undefined *)camry_host_ptr(0xaf084u)),uVar2,((uint16_t *)((stack_record_4a + 12))));
    (*((int32_t *)(stack_record_4a + 14))) = (int)((int)(*((int16_t *)(stack_record_4a + 6))) * (uint)(*((uint16_t *)(stack_record_4a + 12)))) / 0x400;
    store_signed32_minimum_d1d4e((*((int32_t *)(stack_record_4a + 14))),0x569a,((int32_t *)((stack_record_4a + 14))));
    (*((int16_t *)(stack_record_4a + 6))) = (short)(*((int32_t *)(stack_record_4a + 14)));
  }
LAB_000bb150:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x4e4))))) = bVar12;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x4e5))))) = bVar11;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x4e1))))) = cVar10;
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x4e8)))) = (*((int16_t *)(stack_record_4a + 6)));
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x4e6)))) = sVar8;
  (*((int *)camry_host_ptr((uint32_t)(puVar4 + 0x4ec)))) = iVar7;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x4e0))))) = cVar13;
  return;
}
