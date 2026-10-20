#include "common.h"

void call_select_angle_controller_mode_cf04a(void)

{
  select_angle_controller_mode();
  return;
}

void initialize_angle_envelope_parameters_and_state_cf056(void)

{
  (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebecb20u + (uint32_t)(1) * 2u)))) = 1;
  (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebecb20u + (uint32_t)(2) * 2u)))) = 1;
  (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebecb20u + (uint32_t)(3) * 2u)))) = 1;
  (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebecb20u + (uint32_t)(5) * 2u)))) = 1;
  ((volatile uint16_t *)camry_host_ptr(0xfebecb20u))[0] = 0;
  (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebecb20u + (uint32_t)(4) * 2u)))) = 0;
  angle_controller_envelope_accumulator = 0;
  DAT_febecb08 = 0;
  DAT_febecb0c = 0;
  DAT_febecb10 = 0;
  (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebecb20u + (uint32_t)(6) * 2u)))) = 0;
  (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebecb20u + (uint32_t)(7) * 2u)))) = 0;
  DAT_febecb14 = 0;
  DAT_febecb18 = 0;
  DAT_febecb1c = 0;
  DAT_febecb38 = 0;
  DAT_febecb30 = 0;
  DAT_febecb32 = 0;
  DAT_febecb34 = 0x22;
  DAT_febecb35 = 0x22;
  DAT_febecb36 = 0;
  DAT_febecb3a = 0;
  return;
}

void select_envelope_status_with_previous_snapshot_cf0b6(void)

{
  DAT_febecb35 = DAT_febecb34;
  if ((DAT_febecab5 == '\x11') || (DAT_febec862 == '\x01')) {
    DAT_febecb34 = 0x11;
  }
  else {
    DAT_febecb34 = 0x22;
    if (DAT_febecab5 == 'D') {
      DAT_febecb34 = 0x33;
    }
  }
  return;
}

void load_angle_envelope_primary_parameters_cf0ea(void)

{
  int iVar1;
  
  iVar1 = (int)(short)((DAT_febecb00 & 7) + (DAT_febeac3c & 1) * 8);
  if ((DAT_febecb00 & 7) != 7) {
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebecb20u + (uint32_t)(1) * 2u)))) = *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xd3df4u + (uint32_t)(iVar1 * 0x15c) * 1u))));
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebecb20u + (uint32_t)(2) * 2u)))) = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3df8u + (uint32_t)(iVar1 * 0x57) * 4u)))))));
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebecb20u + (uint32_t)(3) * 2u)))) = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3dfcu + (uint32_t)(iVar1 * 0x57) * 4u)))))));
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebecb20u + (uint32_t)(4) * 2u)))) = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3df0u + (uint32_t)(iVar1 * 0x57) * 4u)))))));
  }
  return;
}

void update_angle_controller_retained_envelope(void)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  uint uVar7;
  
  uVar7 = (uint)((volatile uint16_t *)camry_host_ptr(0xfebecb20u))[0];
  uVar2 = (uint)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebecb20u + (uint32_t)(4) * 2u))));
  uVar5 = (uint)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebecb20u + (uint32_t)(1) * 2u))));
  uVar4 = (uint)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebecb20u + (uint32_t)(2) * 2u))));
  uVar3 = (uint)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebecb20u + (uint32_t)(3) * 2u))));
  uVar6 = (uint)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebecb20u + (uint32_t)(5) * 2u))));
  if (uVar5 < 2) {
    uVar5 = 1;
  }
  if (uVar4 < 2) {
    uVar4 = 1;
  }
  if (uVar3 < 2) {
    uVar3 = 1;
  }
  if (DAT_febecb34 == '\x11') {
    if (uVar5 != uVar6) {
      if (uVar6 == 0) {
        angle_controller_envelope_accumulator = uVar7 * uVar5;
      }
      else {
        angle_controller_envelope_accumulator =
             angle_controller_envelope_accumulator * uVar5;
        if (uVar6 != 0) {
          angle_controller_envelope_accumulator =
               angle_controller_envelope_accumulator / uVar6;
        }
      }
    }
    angle_controller_envelope_accumulator =
         (angle_controller_envelope_accumulator + 0x100) - uVar7;
    iVar1 = 0x100 - uVar2;
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebecb20u + (uint32_t)(5) * 2u)))) = (ushort)uVar5;
    uVar7 = angle_controller_envelope_accumulator;
    if (uVar5 != 0) {
      uVar7 = angle_controller_envelope_accumulator / uVar5;
    }
    uVar7 = uVar7 & 0xffff;
    if ((int)(uVar7 - iVar1) < 0 == (iVar1 < 0 && iVar1 < 0 == (int)(uVar7 - iVar1) < 0)) {
      uVar7 = 0x100;
      angle_controller_envelope_accumulator = uVar5 << 8;
    }
    goto LAB_000cf21e;
  }
  if (DAT_febecb34 == '\"') {
    if (uVar4 != uVar6) {
      if (uVar6 == 0) {
        angle_controller_envelope_accumulator = uVar7 * uVar4;
      }
      else {
        angle_controller_envelope_accumulator =
             angle_controller_envelope_accumulator * uVar4;
        if (uVar6 != 0) {
          angle_controller_envelope_accumulator =
               angle_controller_envelope_accumulator / uVar6;
        }
      }
    }
    angle_controller_envelope_accumulator = angle_controller_envelope_accumulator - uVar7;
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebecb20u + (uint32_t)(5) * 2u)))) = (ushort)uVar4;
    uVar7 = angle_controller_envelope_accumulator;
    if (uVar4 != 0) {
      uVar7 = angle_controller_envelope_accumulator / uVar4;
    }
    uVar7 = uVar7 & 0xffff;
    if (-1 < (int)(uVar7 - uVar2) && uVar7 != uVar2) goto LAB_000cf21e;
  }
  else {
    if (DAT_febecb34 != '3') goto LAB_000cf21e;
    if (uVar3 != uVar6) {
      if (uVar6 == 0) {
        angle_controller_envelope_accumulator = uVar7 * uVar3;
      }
      else {
        angle_controller_envelope_accumulator =
             angle_controller_envelope_accumulator * uVar3;
        if (uVar6 != 0) {
          angle_controller_envelope_accumulator =
               angle_controller_envelope_accumulator / uVar6;
        }
      }
    }
    angle_controller_envelope_accumulator = angle_controller_envelope_accumulator - uVar7;
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebecb20u + (uint32_t)(5) * 2u)))) = (ushort)uVar3;
    uVar7 = angle_controller_envelope_accumulator;
    if (uVar3 != 0) {
      uVar7 = angle_controller_envelope_accumulator / uVar3;
    }
    uVar7 = uVar7 & 0xffff;
    uVar4 = uVar3;
    if (uVar2 < uVar7) goto LAB_000cf21e;
  }
  (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebecb20u + (uint32_t)(5) * 2u)))) = (ushort)uVar4;
  uVar7 = 0;
  angle_controller_envelope_accumulator = 0;
LAB_000cf21e:
  ((volatile uint16_t *)camry_host_ptr(0xfebecb20u))[0] = (ushort)uVar7;
  return;
}

void vote_angle_target_and_update_fade_latch(void)

{
  int iVar1;
  
  iVar1 = (int)((volatile int16_t *)camry_host_ptr(0xfebecaa6u))[0];
  DAT_febecb08 = (int)(*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebecaa6u + (uint32_t)(1) * 2u))));
  if (((iVar1 == DAT_febecb08) || (iVar1 == (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebecaa6u + (uint32_t)(2) * 2u)))))) ||
     (DAT_febecb08 != (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebecaa6u + (uint32_t)(2) * 2u)))))) {
    DAT_febecb08 = iVar1;
  }
  if ((DAT_febecb00 & 7) == 7) {
    if (DAT_febecb36 == '\0') {
      DAT_febecb08 = 0;
    }
    else if (((volatile uint16_t *)camry_host_ptr(0xfebecb20u))[0] == 0) {
      DAT_febecb36 = '\0';
    }
  }
  else {
    DAT_febecb36 = '\x02';
  }
  return;
}

void load_angle_envelope_auxiliary_parameters_cf276(void)

{
  int iVar1;
  
  iVar1 = (int)(short)((DAT_febecb00 & 7) + (DAT_febeac3c & 1) * 8);
  if ((DAT_febecb00 & 7) != 7) {
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebecb20u + (uint32_t)(6) * 2u)))) = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3e00u + (uint32_t)(iVar1 * 0x57) * 4u)))))));
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebecb20u + (uint32_t)(7) * 2u)))) = (*((volatile ushort *)camry_host_ptr((*((volatile uint32_t *)(((undefined *)camry_host_ptr((uint32_t)(0xd3e04u + (uint32_t)(iVar1 * 0x15c) * 1u)))))))));
  }
  return;
}

void slew_and_clamp_angle_controller_contribution(void)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  int iVar4;
  
  iVar1 = (int)((int)(int16_t)DAT_febecb38);
  iVar4 = (int)((int)(int16_t)DAT_febecb30);
  uVar2 = (uint)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebecb20u + (uint32_t)(6) * 2u))));
  uVar3 = (uint)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebecb20u + (uint32_t)(7) * 2u))));
  if (((iVar1 == iVar4) || (iVar1 == ((int)(int16_t)DAT_febecb32))) || (iVar4 != ((int)(int16_t)DAT_febecb32))) {
    iVar4 = iVar1;
  }
  DAT_febecb18 = (int)(DAT_febecb08 * (uint)((volatile uint16_t *)camry_host_ptr(0xfebecb20u))[0]) / 0x100;
  DAT_febecb14 = DAT_febecb18 - iVar4;
  if ((int)(((int)(int32_t)DAT_febecb14) - uVar2) < 0 == ((int)DAT_febecb14 < 0 && -1 < (int)(((int)(int32_t)DAT_febecb14) - uVar2))
      && ((int)(int32_t)DAT_febecb14) != uVar2) {
    DAT_febecb1c = uVar2 + iVar4;
  }
  else {
    DAT_febecb1c = DAT_febecb18;
    if ((int)(((int)(int32_t)DAT_febecb14) + uVar2) < 0 !=
        ((int)DAT_febecb14 < 0 != (int)-uVar2 < 0 &&
        (int)-uVar2 < 0 == (int)(((int)(int32_t)DAT_febecb14) + uVar2) < 0)) {
      DAT_febecb1c = iVar4 - uVar2;
    }
  }
  if (((int)(((int)(int32_t)DAT_febecb1c) - uVar3) < 0 ==
       ((int)DAT_febecb1c < 0 && -1 < (int)(((int)(int32_t)DAT_febecb1c) - uVar3)) && ((int)(int32_t)DAT_febecb1c) != uVar3) ||
     (uVar2 = -uVar3, iVar4 = ((int)(int32_t)DAT_febecb1c) + uVar3, uVar3 = uVar2,
     iVar4 < 0 != ((int)DAT_febecb1c < 0 != (int)uVar2 < 0 && (int)uVar2 < 0 == iVar4 < 0))) {
    DAT_febecb3a = 1;
  }
  else {
    DAT_febecb3a = 0;
    uVar3 = ((int)(int32_t)DAT_febecb1c);
  }
  DAT_febecb38 = (short)uVar3;
  DAT_febecb30 = ((int)(int16_t)DAT_febecb38);
  DAT_febecb32 = ((int)(int16_t)DAT_febecb38);
  return;
}

void update_angle_controller_output_envelope(void)

{
  select_envelope_status_with_previous_snapshot_cf0b6();
  load_angle_envelope_primary_parameters_cf0ea();
  update_angle_controller_retained_envelope();
  vote_angle_target_and_update_fade_latch();
  load_angle_envelope_auxiliary_parameters_cf276();
  slew_and_clamp_angle_controller_contribution();
  return;
}

void fill_constant_block_cf35c(void)

{
  DAT_febecb57 = 0;
  DAT_febecb58 = 0;
  DAT_febecb54 = 0;
  DAT_febecb55 = 0;
  DAT_febecb56 = 0;
  return;
}

void clear_three_channel_event_markers_ages_and_counts_cf370(void)

{
  uint uVar1;
  int iVar2;
  uint uVar3;
  
  uVar3 = 0;
  do {
    iVar2 = uVar3 * 2;
    uVar1 = uVar3 + 1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebecb42u + (uint32_t)(iVar2) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebecb43u + (uint32_t)(iVar2) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebecb48u + (uint32_t)(iVar2) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebecb49u + (uint32_t)(iVar2) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebecb4eu + (uint32_t)(iVar2) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebecb4fu + (uint32_t)(iVar2) * 1u)))) = 0;
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebecb3cu + (uint32_t)(uVar3) * 2u)))) = 0;
    uVar3 = uVar1;
  } while (uVar1 < 3);
  return;
}

void copy_cell_block_cf3a2(void)

{
  DAT_febecb42 = DAT_febead64;
  DAT_febecb43 = DAT_febead61;
  DAT_febecb48 = DAT_febead66;
  DAT_febecb49 = DAT_febead63;
  DAT_febecb4e = DAT_febead65;
  DAT_febecb4f = DAT_febead62;
  DAT_febecb3c = DAT_febeae6a;
  DAT_febecb44 = DAT_febead6b;
  DAT_febecb45 = DAT_febead68;
  DAT_febecb4a = DAT_febead6d;
  DAT_febecb4b = DAT_febead6a;
  DAT_febecb50 = DAT_febead6c;
  DAT_febecb51 = DAT_febead69;
  DAT_febecb3e = DAT_febeae6c;
  DAT_febecb46 = DAT_febead02;
  DAT_febecb47 = DAT_febeacf4;
  DAT_febecb4c = DAT_febead01;
  DAT_febecb4d = DAT_febeacf3;
  DAT_febecb52 = DAT_febead00;
  DAT_febecb53 = DAT_febeacf2;
  DAT_febecb40 = DAT_febeae14;
  return;
}

void restore_event_pairs_and_increment_saturated_ages_cf442(void)

{
  char *pcVar1;
  int iVar2;
  uint32_t puVar3;
  uint uVar4;
  
  puVar3 = 0xfebeb800u;
  copy_cell_block_cf3a2();
  uVar4 = 0;
  do {
    iVar2 = uVar4 * 2;
    pcVar1 = ((undefined *)camry_host_ptr((uint32_t)(puVar3 + iVar2 + 0x1342)));
    if ((*pcVar1 == -0x5b) && (((int8_t)pcVar1[1]) != -1)) {
      pcVar1[1] = pcVar1[1] + '\x01';
    }
    pcVar1 = ((undefined *)camry_host_ptr((uint32_t)(puVar3 + iVar2 + 0x1348)));
    if ((*pcVar1 == -0x5b) && (((int8_t)pcVar1[1]) != -1)) {
      pcVar1[1] = pcVar1[1] + '\x01';
    }
    pcVar1 = ((undefined *)camry_host_ptr((uint32_t)(puVar3 + iVar2 + 0x134e)));
    if ((*pcVar1 == -0x5b) && (((int8_t)pcVar1[1]) != -1)) {
      pcVar1[1] = pcVar1[1] + '\x01';
    }
    uVar4 = uVar4 + 1;
  } while (uVar4 < 3);
  return;
}

void derive_mode_two_and_zero_event_enables_cf4a8(void)

{
  if ((DAT_febecab7 == '\x01') && ((DAT_febecb00 & 7) == 2)) {
    DAT_febecb57 = 1;
  }
  else {
    DAT_febecb57 = 0;
    if (DAT_febecab7 == '\x01') {
      DAT_febecb57 = 0;
      DAT_febecb58 = (DAT_febecb00 & 7) == 0;
      return;
    }
  }
  DAT_febecb58 = 0;
  return;
}

void mark_primary_channel_event_and_clear_age_cf4da(uint param_1,char param_2)

{
  int iVar1;
  
  if ((param_2 == '\x01') && ((param_1 & 0xff) < 3)) {
    iVar1 = (param_1 & 0xff) * 2;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebecb42u + (uint32_t)(iVar1) * 1u)))) = 0xa5;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebecb43u + (uint32_t)(iVar1) * 1u)))) = 0;
  }
  return;
}

void mark_dual_enabled_channel_event_and_clear_age_cf4f8(uint param_1,char param_2,char param_3)

{
  int iVar1;
  
  if (((param_2 == '\x01') && (param_3 == '\x01')) && ((param_1 & 0xff) < 3)) {
    iVar1 = (param_1 & 0xff) * 2;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebecb48u + (uint32_t)(iVar1) * 1u)))) = 0xa5;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebecb49u + (uint32_t)(iVar1) * 1u)))) = 0;
  }
  return;
}

void mark_channel_event_and_count_unlatched_occurrence_cf51c(uint param_1,char param_2,char param_3)

{
  ushort uVar1;
  char cVar2;
  
  param_1 = param_1 & 0xff;
  if (((param_2 == '\x01') && (param_3 == '\x01')) && (param_1 < 3)) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebecb4eu + (uint32_t)(param_1 * 2) * 1u)))) = 0xa5;
    cVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebecb54u + (uint32_t)(param_1) * 1u))));
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebecb4fu + (uint32_t)(param_1 * 2) * 1u)))) = 0;
    if (cVar2 == '\0') {
      uVar1 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebecb3cu + (uint32_t)(param_1) * 2u))));
      if (uVar1 < 0xff) {
        (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebecb3cu + (uint32_t)(param_1) * 2u)))) = uVar1 + 1;
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebecb54u + (uint32_t)(param_1) * 1u)))) = 0x5a;
      }
    }
  }
  return;
}

void update_three_channel_event_marker_groups_cf56a(void)

{
  undefined1 uVar1;
  undefined1 uVar2;
  undefined1 uVar3;
  undefined1 uVar4;
  undefined1 uVar5;
  undefined1 uVar6;
  
  uVar6 = DAT_febecb58;
  uVar5 = DAT_febecb57;
  uVar4 = DAT_febecb3a;
  uVar3 = DAT_febecafd;
  uVar2 = DAT_febec862;
  uVar1 = DAT_febec834;
  mark_primary_channel_event_and_clear_age_cf4da(0,DAT_febecb57);
  mark_dual_enabled_channel_event_and_clear_age_cf4f8(0,uVar5,uVar3);
  mark_channel_event_and_count_unlatched_occurrence_cf51c(0,uVar5,uVar4);
  mark_primary_channel_event_and_clear_age_cf4da(1,uVar6);
  mark_dual_enabled_channel_event_and_clear_age_cf4f8(1,uVar6,uVar3);
  mark_channel_event_and_count_unlatched_occurrence_cf51c(1,uVar6,uVar4);
  mark_primary_channel_event_and_clear_age_cf4da(2,uVar2);
  mark_dual_enabled_channel_event_and_clear_age_cf4f8(2,1,uVar1);
  mark_channel_event_and_count_unlatched_occurrence_cf51c(2,uVar2,uVar4);
  return;
}

void derive_event_enables_and_update_channel_markers_cf5de(void)

{
  derive_mode_two_and_zero_event_enables_cf4a8();
  update_three_channel_event_marker_groups_cf56a();
  return;
}

void copy_cell_block_cf5ee(void)

{
  DAT_febead64 = DAT_febecb42;
  DAT_febead61 = DAT_febecb43;
  DAT_febead66 = DAT_febecb48;
  DAT_febead63 = DAT_febecb49;
  DAT_febead65 = DAT_febecb4e;
  DAT_febead62 = DAT_febecb4f;
  DAT_febeae6a = DAT_febecb3c;
  DAT_febead6b = DAT_febecb44;
  DAT_febead68 = DAT_febecb45;
  DAT_febead6d = DAT_febecb4a;
  DAT_febead6a = DAT_febecb4b;
  DAT_febead6c = DAT_febecb50;
  DAT_febead69 = DAT_febecb51;
  DAT_febeae6c = DAT_febecb3e;
  DAT_febead02 = DAT_febecb46;
  DAT_febeacf4 = DAT_febecb47;
  DAT_febead01 = DAT_febecb4c;
  DAT_febeacf3 = DAT_febecb4d;
  DAT_febead00 = DAT_febecb52;
  DAT_febeacf2 = DAT_febecb53;
  DAT_febeae14 = DAT_febecb40;
  return;
}

void fill_constant_block_cf684(void)

{
  DAT_febecbb8 = 0;
  DAT_febecbb6 = 200;
  DAT_febecbc6 = 200;
  DAT_febecbd6 = 200;
  DAT_febecbc8 = 0;
  DAT_febecbd8 = 0;
  DAT_febecbba = 0;
  DAT_febecbca = 0;
  DAT_febecbda = 0;
  DAT_febecbbc = 0;
  DAT_febecbcc = 0;
  DAT_febecbdc = 0;
  DAT_febecbbe = 1;
  DAT_febecbce = 1;
  DAT_febecbde = 1;
  DAT_febecbc0 = 0;
  DAT_febecbd0 = 0;
  DAT_febecbe0 = 0;
  DAT_febecbc2 = 1;
  DAT_febecbd2 = 1;
  DAT_febecbe2 = 1;
  DAT_febecbec = 0;
  DAT_febecbb4 = 0;
  DAT_febecbd4 = 0;
  DAT_febecbe4 = 0;
  DAT_febecb68 = 0;
  DAT_febecb8c = 0;
  DAT_febecba0 = 0;
  DAT_febecb6c = 0;
  DAT_febecbea = 0;
  DAT_febecbeb = 0;
  DAT_febecb70 = 0;
  DAT_febecb90 = 0;
  DAT_febecba4 = 0;
  DAT_febecb74 = 0;
  DAT_febecb94 = 0;
  DAT_febecba8 = 0;
  DAT_febecb78 = 0;
  DAT_febecb5c = 0;
  DAT_febecb98 = 0;
  DAT_febecbac = 0;
  DAT_febecb7c = 0;
  DAT_febecb9c = 0;
  DAT_febecbb0 = 0;
  DAT_febecb60 = 0;
  DAT_febecb64 = 0;
  DAT_febecbe6 = 1;
  DAT_febecbe8 = 0;
  DAT_febecb84 = 0;
  DAT_febecb88 = 0;
  DAT_febecbc4 = 0;
  DAT_febecb80 = 0;
  return;
}

void fill_constant_block_cf75c(void)

{
  DAT_febecbb8 = 0;
  DAT_febecbb6 = 200;
  DAT_febecbc6 = 200;
  DAT_febecbd6 = 200;
  DAT_febecbc8 = 0;
  DAT_febecbd8 = 0;
  DAT_febecbba = 0;
  DAT_febecbca = 0;
  DAT_febecbda = 0;
  DAT_febecbbc = 0;
  DAT_febecbcc = 0;
  DAT_febecbdc = 0;
  DAT_febecbbe = 1;
  DAT_febecbce = 1;
  DAT_febecbde = 1;
  DAT_febecbc0 = 0;
  DAT_febecbd0 = 0;
  DAT_febecbe0 = 0;
  DAT_febecbc2 = 1;
  DAT_febecbd2 = 1;
  DAT_febecbe2 = 1;
  DAT_febecbec = 0;
  DAT_febecbb4 = 0;
  DAT_febecbd4 = 0;
  DAT_febecbe4 = 0;
  DAT_febecb68 = 0;
  DAT_febecb8c = 0;
  DAT_febecba0 = 0;
  DAT_febecb6c = 0;
  DAT_febecb70 = 0;
  DAT_febecb90 = 0;
  DAT_febecba4 = 0;
  DAT_febecb74 = 0;
  DAT_febecb94 = 0;
  DAT_febecba8 = 0;
  DAT_febecb78 = 0;
  DAT_febecb5c = 0;
  DAT_febecb98 = 0;
  DAT_febecbac = 0;
  DAT_febecb7c = 0;
  DAT_febecb9c = 0;
  DAT_febecbb0 = 0;
  DAT_febecb60 = 0;
  DAT_febecb64 = 0;
  DAT_febecbe6 = 1;
  DAT_febecbe8 = 0;
  DAT_febecb84 = 0;
  DAT_febecb88 = 0;
  DAT_febecbc4 = 0;
  DAT_febecb80 = 0;
  return;
}

void load_mode_selected_seven_word_triplicates_cf82c(void)

{
  uint32_t puVar1;
  
  if (DAT_febecbfe != DAT_febecbed) {
    puVar1 = ((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb148cu + (uint32_t)(DAT_febeac3c & 1) * 4u))))));
    if (DAT_febecbfe == '\x01') {
      DAT_febecbb6 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(puVar1 + 0xc))));
      DAT_febecbb8 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(puVar1 + 0xe))));
      DAT_febecbba = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(puVar1 + 0x10))));
      DAT_febecbbc = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(puVar1 + 0x12))));
      DAT_febecbbe = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(puVar1 + 0x14))));
      DAT_febecbc0 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(puVar1 + 0x16))));
      DAT_febecbc2 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(puVar1 + 0x18))));
      DAT_febecbc6 = DAT_febecbb6;
      DAT_febecbc8 = DAT_febecbb8;
      DAT_febecbca = DAT_febecbba;
      DAT_febecbcc = DAT_febecbbc;
      DAT_febecbce = DAT_febecbbe;
      DAT_febecbd0 = DAT_febecbc0;
      DAT_febecbd2 = DAT_febecbc2;
      DAT_febecbd6 = DAT_febecbb6;
      DAT_febecbd8 = DAT_febecbb8;
      DAT_febecbda = DAT_febecbba;
      DAT_febecbdc = DAT_febecbbc;
      DAT_febecbde = DAT_febecbbe;
      DAT_febecbe0 = DAT_febecbc0;
      DAT_febecbe2 = DAT_febecbc2;
    }
    else if (DAT_febecbfe == '\x02') {
      DAT_febecbb6 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(puVar1 + 0x1a))));
      DAT_febecbb8 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(puVar1 + 0x1c))));
      DAT_febecbba = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(puVar1 + 0x1e))));
      DAT_febecbbc = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(puVar1 + 0x20))));
      DAT_febecbbe = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(puVar1 + 0x22))));
      DAT_febecbc0 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(puVar1 + 0x24))));
      DAT_febecbc2 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(puVar1 + 0x26))));
      DAT_febecbc6 = DAT_febecbb6;
      DAT_febecbc8 = DAT_febecbb8;
      DAT_febecbca = DAT_febecbba;
      DAT_febecbcc = DAT_febecbbc;
      DAT_febecbce = DAT_febecbbe;
      DAT_febecbd0 = DAT_febecbc0;
      DAT_febecbd2 = DAT_febecbc2;
      DAT_febecbd6 = DAT_febecbb6;
      DAT_febecbd8 = DAT_febecbb8;
      DAT_febecbda = DAT_febecbba;
      DAT_febecbdc = DAT_febecbbc;
      DAT_febecbde = DAT_febecbbe;
      DAT_febecbe0 = DAT_febecbc0;
      DAT_febecbe2 = DAT_febecbc2;
    }
    else {
      DAT_febecbb6 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(puVar1 + 0x28))));
      DAT_febecbb8 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(puVar1 + 0x2a))));
      DAT_febecbba = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(puVar1 + 0x2c))));
      DAT_febecbbc = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(puVar1 + 0x2e))));
      DAT_febecbbe = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(puVar1 + 0x30))));
      DAT_febecbc0 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(puVar1 + 0x32))));
      DAT_febecbc2 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(puVar1 + 0x34))));
      DAT_febecbc6 = DAT_febecbb6;
      DAT_febecbc8 = DAT_febecbb8;
      DAT_febecbca = DAT_febecbba;
      DAT_febecbcc = DAT_febecbbc;
      DAT_febecbce = DAT_febecbbe;
      DAT_febecbd0 = DAT_febecbc0;
      DAT_febecbd2 = DAT_febecbc2;
      DAT_febecbd6 = DAT_febecbb6;
      DAT_febecbd8 = DAT_febecbb8;
      DAT_febecbda = DAT_febecbba;
      DAT_febecbdc = DAT_febecbbc;
      DAT_febecbde = DAT_febecbbe;
      DAT_febecbe0 = DAT_febecbc0;
      DAT_febecbe2 = DAT_febecbc2;
    }
  }
  return;
}

void derive_and_triplicate_waveform_timing_products_cf972(void)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  
  uVar2 = (uint)DAT_febecbb6;
  uVar1 = (uint)DAT_febecbc6;
  if (((uVar2 == uVar1) || (uVar2 == DAT_febecbd6)) || (uVar1 != DAT_febecbd6)) {
    uVar1 = uVar2;
  }
  uVar3 = (uint)DAT_febecbbc;
  uVar2 = (uint)DAT_febecbcc;
  if (((uVar3 == uVar2) || (uVar3 == DAT_febecbdc)) || (uVar2 != DAT_febecbdc)) {
    uVar2 = uVar3;
  }
  uVar4 = (uint)DAT_febecbbe;
  uVar3 = (uint)DAT_febecbce;
  if (((uVar4 == uVar3) || (uVar4 == DAT_febecbde)) || (uVar3 != DAT_febecbde)) {
    uVar3 = uVar4;
  }
  uVar5 = (uint)DAT_febecbc0;
  uVar4 = (uint)DAT_febecbd0;
  if (((uVar5 == uVar4) || (uVar5 == DAT_febecbe0)) || (uVar4 != DAT_febecbe0)) {
    uVar4 = uVar5;
  }
  uVar6 = (uint)DAT_febecbc2;
  uVar5 = (uint)DAT_febecbd2;
  if (((uVar6 == uVar5) || (uVar6 == DAT_febecbe2)) || (uVar5 != DAT_febecbe2)) {
    uVar5 = uVar6;
  }
  if (DAT_febecbfe != DAT_febecbed) {
    DAT_febecb68 = (uVar1 * uVar2 + 5000) / 10000;
    uVar2 = (uVar1 >> 1) + 10000;
    if (uVar1 == 0) {
      uVar2 = 10000;
    }
    else if (uVar2 == 0x80000000 && uVar1 == 0xffffffff) {
      uVar2 = 0;
    }
    else {
      uVar2 = uVar2 / uVar1;
    }
    DAT_febecbb4 = (undefined2)uVar2;
    DAT_febecb7c = uVar2 * DAT_febecb68;
    DAT_febecb5c = uVar3 + DAT_febecb7c;
    DAT_febecb74 = DAT_febecb5c * uVar4;
    DAT_febecb70 = uVar5 + DAT_febecb74;
    DAT_febecb8c = DAT_febecb68;
    DAT_febecb90 = DAT_febecb70;
    DAT_febecb94 = DAT_febecb74;
    DAT_febecb98 = DAT_febecb5c;
    DAT_febecb9c = DAT_febecb7c;
    DAT_febecba0 = DAT_febecb68;
    DAT_febecba4 = DAT_febecb70;
    DAT_febecba8 = DAT_febecb74;
    DAT_febecbac = DAT_febecb5c;
    DAT_febecbb0 = DAT_febecb7c;
    DAT_febecbd4 = DAT_febecbb4;
    DAT_febecbe4 = DAT_febecbb4;
  }
  return;
}

void advance_wrapping_waveform_timing_counter_cfa84(void)

{
  uint uVar1;
  
  if (((DAT_febecb70 == DAT_febecb90) || (DAT_febecb70 == DAT_febecba4)) ||
     (uVar1 = DAT_febecb90, DAT_febecb90 != DAT_febecba4)) {
    uVar1 = DAT_febecb70;
  }
  if (DAT_febecbfe != DAT_febecbed) {
    DAT_febecb6c = 0;
  }
  if (DAT_febecb6c < uVar1) {
    DAT_febecb6c = DAT_febecb6c + 1;
  }
  else {
    DAT_febecb6c = 0;
  }
  return;
}

void derive_modulo_waveform_window_enable_cfac2(void)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  
  if (((DAT_febecb5c == DAT_febecb98) || (DAT_febecb5c == DAT_febecbac)) ||
     (uVar1 = DAT_febecb98, DAT_febecb98 != DAT_febecbac)) {
    uVar1 = DAT_febecb5c;
  }
  if (((DAT_febecb70 == DAT_febecb90) || (DAT_febecb70 == DAT_febecba4)) ||
     (uVar2 = DAT_febecb90, DAT_febecb90 != DAT_febecba4)) {
    uVar2 = DAT_febecb70;
  }
  if (((DAT_febecb74 == DAT_febecb94) || (DAT_febecb74 == DAT_febecba8)) ||
     (uVar3 = DAT_febecb94, DAT_febecb94 != DAT_febecba8)) {
    uVar3 = DAT_febecb74;
  }
  if (((DAT_febecb7c == DAT_febecb9c) || (DAT_febecb7c == DAT_febecbb0)) ||
     (uVar4 = DAT_febecb9c, DAT_febecb9c != DAT_febecbb0)) {
    uVar4 = DAT_febecb7c;
  }
  if ((DAT_febecb6c < uVar3) || (uVar2 < DAT_febecb6c)) {
    if (uVar1 == 0) {
      DAT_febecbec = false;
    }
    else {
      if (uVar1 != 0) {
        DAT_febecb78 = DAT_febecb6c % uVar1;
      }
      DAT_febecbec = DAT_febecb78 < uVar4;
    }
  }
  else {
    DAT_febecbec = false;
    DAT_febecb78 = 0;
  }
  return;
}

int lookup_signed_four_quadrant_1440_phase_table_cfb62(int param_1)

{
  int iVar1;
  
  if (param_1 + -0x168 < 0 == (param_1 < 0 && -1 < param_1 + -0x168)) {
    if (param_1 + -0x2d0 < 0 == (param_1 < 0 && -1 < param_1 + -0x2d0)) {
      iVar1 = -1;
      if (param_1 + -0x438 < 0 == (param_1 < 0 && -1 < param_1 + -0x438)) {
        param_1 = 0x5a0 - param_1;
      }
      else {
        param_1 = param_1 + -0x2d0;
      }
      goto LAB_000cfb90;
    }
    param_1 = 0x2d0 - param_1;
  }
  iVar1 = 1;
LAB_000cfb90:
  if (param_1 + -0x168 < 0 == (param_1 < 0 && -1 < param_1 + -0x168)) {
    param_1 = 0x168;
  }
  else if (param_1 < 0) {
    param_1 = 0;
  }
  return iVar1 * *(short *)(((undefined *)camry_host_ptr((uint32_t)(0xd526cu + (uint32_t)(param_1 * 2) * 1u))));
}

void compute_gated_scaled_phase_table_waveform_cfbb4(void)

{
  uint uVar1;
  uint uVar2;
  int iVar3;
  uint32_t puVar4;
  int iVar5;
  uint uVar6;
  uint uVar7;
  int iVar8;
  int iVar9;
  uint uVar10;
  int iVar11;
  int iVar12;
  
  uVar1 = DAT_febecb78;
  puVar4 = 0xfebeb800u;
  if (((DAT_febecb68 == DAT_febecb8c) || (DAT_febecb68 == DAT_febecba0)) ||
     (iVar3 = DAT_febecb8c, DAT_febecb8c != DAT_febecba0)) {
    iVar3 = DAT_febecb68;
  }
  uVar10 = (uint)DAT_febecbd4;
  uVar2 = (uint)DAT_febecbb4;
  if (((uVar2 == uVar10) || (uVar2 == DAT_febecbe4)) || (uVar10 != DAT_febecbe4)) {
    uVar10 = uVar2;
  }
  uVar6 = (uint)DAT_febecbb8;
  uVar2 = (uint)DAT_febecbc8;
  iVar11 = (int)((int)(int8_t)DAT_febecbe6);
  if (((uVar6 == uVar2) || (uVar6 == DAT_febecbd8)) || (uVar2 != DAT_febecbd8)) {
    uVar2 = uVar6;
  }
  uVar7 = (uint)DAT_febecbba;
  uVar6 = (uint)DAT_febecbca;
  if (((uVar7 == uVar6) || (uVar7 == DAT_febecbda)) || (uVar6 != DAT_febecbda)) {
    uVar6 = uVar7;
  }
  if (DAT_febecbec == '\x01') {
    if (DAT_febecbee == '\0') {
      if (((int)(int16_t)DAT_febec172) < 0) {
        iVar11 = -1;
      }
      else {
        iVar11 = 1;
      }
    }
    DAT_febecb80 = DAT_febecb78;
    if (uVar10 != 0) {
      DAT_febecb80 = (int)DAT_febecb78 % (int)uVar10;
    }
    iVar12 = DAT_febecb80 * 0x5a0;
    if (uVar10 != 0) {
      if (iVar12 == -0x80000000 && uVar10 == 0xffffffff) {
        iVar12 = -0x80000000;
      }
      else {
        iVar12 = iVar12 / (int)uVar10;
      }
    }
    puVar4 = 0xfebeb800u;
    iVar5 = lookup_signed_four_quadrant_1440_phase_table_cfb62(iVar12);
    if ((uVar10 <= uVar1) && (uVar1 < uVar10 * (iVar3 + -1))) {
      uVar6 = uVar2;
    }
    iVar3 = (int)(iVar5 * iVar11 * uVar6) / 0x1000;
    iVar8 = (*((int *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb148cu + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0xbc4))))) & 1) * 4u)))) + 4))));
    iVar9 = iVar8;
    if ((iVar3 - iVar8 < 0 != (iVar3 < 0 != iVar8 < 0 && iVar8 < 0 == iVar3 - iVar8 < 0) ||
         iVar3 == iVar8) &&
       (iVar9 = -iVar8,
       iVar3 + iVar8 < 0 == (iVar3 < 0 != iVar9 < 0 && iVar9 < 0 == iVar3 + iVar8 < 0) &&
       iVar3 != iVar9)) {
      iVar9 = iVar3;
    }
  }
  else {
    DAT_febecb80 = 0;
    iVar3 = DAT_febecb88;
    iVar5 = DAT_febecb60;
    iVar9 = 0;
    iVar12 = DAT_febecb84;
  }
  (*((int *)camry_host_ptr((uint32_t)(puVar4 + 0x1360)))) = iVar5;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x13e6))))) = (char)iVar11;
  (*((int *)camry_host_ptr((uint32_t)(puVar4 + 0x1364)))) = iVar9;
  (*((int *)camry_host_ptr((uint32_t)(puVar4 + 0x1384)))) = iVar12;
  (*((int *)camry_host_ptr((uint32_t)(puVar4 + 5000)))) = iVar3;
  return;
}

void sum_waveform_and_filtered_term_with_symmetric_limit_cfcd4(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar1 = ((int)(int16_t)DAT_febecc22) + DAT_febecb64;
  iVar3 = (int)(*((short *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb148cu + (uint32_t)(DAT_febeac3c & 1) * 4u)))) + 10))));
  DAT_febecbe8 = (*((short *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb148cu + (uint32_t)(DAT_febeac3c & 1) * 4u)))) + 10))));
  if ((iVar1 - iVar3 < 0 != (iVar1 < 0 != iVar3 < 0 && iVar3 < 0 == iVar1 - iVar3 < 0) ||
       iVar1 == iVar3) &&
     (iVar2 = -iVar3, DAT_febecbe8 = (short)iVar1,
     iVar1 + iVar3 < 0 != (iVar1 < 0 != iVar2 < 0 && iVar2 < 0 == iVar1 + iVar3 < 0) ||
     iVar1 == iVar2)) {
    DAT_febecbe8 = (short)iVar2;
  }
  DAT_febecbc4 = (short)iVar1;
  return;
}

void clear_waveform_previous_mode_and_active_history_cfd0a(void)

{
  DAT_febecbed = 0;
  DAT_febecbee = 0;
  return;
}

void clear_or_reinitialize_waveform_output_state_cfd14(void)

{
  if (DAT_febecbed == '\0') {
    DAT_febecbe8 = 0;
  }
  else {
    fill_constant_block_cff78();
    fill_constant_block_cf75c();
  }
  return;
}

void run_init_chain_cfd32(void)

{
  load_mode_selected_seven_word_triplicates_cf82c();
  derive_and_triplicate_waveform_timing_products_cf972();
  advance_wrapping_waveform_timing_counter_cfa84();
  derive_modulo_waveform_window_enable_cfac2();
  compute_gated_scaled_phase_table_waveform_cfbb4();
  update_absolute_curve_and_bounded_error_integrator_d0120();
  sum_waveform_and_filtered_term_with_symmetric_limit_cfcd4();
  return;
}

void update_windowed_excitation(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if ((DAT_febecbeb == '\0') || (DAT_febecbfe == '\0')) {
    clear_or_reinitialize_waveform_output_state_cfd14();
  }
  else {
    run_init_chain_cfd32();
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x13ed))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x13fe)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x13ee))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x13ec)))));
  return;
}

void fill_constant_block_cfd88(void)

{
  DAT_febecbf3 = 0;
  DAT_febecbf4 = 1;
  DAT_febecbf5 = 0;
  DAT_febecbf0 = 0;
  DAT_febecbf2 = 0;
  return;
}

void capture_request_when_group26_status_allows_cfda0(void)

{
  uint32_t puVar1;
  uchar uVar2;
  
  puVar1 = 0xfebeb800u;
  uVar2 = get_application_grouped_status(0x1a);
  if ((uVar2 == 'Z') || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xa47))))) != '\0')) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x13f3))))) = 0;
  }
  else {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x13f3))))) = 0x5a;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x13f2))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xa27)))));
  }
  return;
}

char select_valid_request_mode_or_retained_mode_cfdd4(void)

{
  char cVar1;
  
  if (((DAT_febeadbf == '\x02' || DAT_febeadbf == '\x03') || (DAT_febeacbd != '\0')) ||
     (DAT_febecbf3 == '\0')) {
    DAT_febecbf4 = 1;
    cVar1 = DAT_febecbea;
  }
  else {
    DAT_febecbf4 = 0;
    cVar1 = DAT_febecbf2;
    if (((DAT_febecbf2 != '\x01') && (DAT_febecbf2 != '\x02')) && (DAT_febecbf2 != '\x03')) {
      cVar1 = '\0';
    }
  }
  return cVar1;
}

char update_mode_hold_timer_and_return_enable_cfe14(void)

{
  char cVar1;
  
  cVar1 = DAT_febecbeb;
  if (((((DAT_febecbeb == '\0') && (DAT_febecbf4 == '\0')) &&
       (cVar1 = DAT_febecbf5 == '\0', (bool)cVar1)) || (cVar1 == '\x01')) &&
     (DAT_febecbf4 == '\x01')) {
    cVar1 = '\0';
  }
  else if (DAT_febecbf5 != '\x01') {
    return cVar1;
  }
  DAT_febecbf5 = DAT_febecbf0 < DAT_000b115c;
  if ((bool)DAT_febecbf5) {
    DAT_febecbf0 = DAT_febecbf0 + 1;
  }
  else {
    DAT_febecbf0 = 0;
  }
  return cVar1;
}

undefined4 publish_request_mode_and_enable_under_priority_mask_cfe64(void)

{
  uint32_t puVar1;
  undefined1 uVar2;
  undefined1 uVar3;
  undefined4 uVar4;
  
  puVar1 = 0xfebeb800u;
  uVar2 = select_valid_request_mode_or_retained_mode_cfdd4();
  uVar3 = update_mode_hold_timer_and_return_enable_cfe14();
  uVar4 = raise_priority_mask_and_return_previous_d1da0(0xffc0);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x13ea))))) = uVar2;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x13eb))))) = uVar3;
  restore_priority_mask_preserving_interrupt_enable_d1dc6(uVar4);
  return uVar4;
}

void fill_constant_block_cfe8e(void)

{
  DAT_febecbfe = 0;
  DAT_febecbf6 = 0;
  DAT_febecbfa = 0;
  DAT_febecbfc = 0;
  DAT_febecbf8 = 0;
  return;
}

void reload_triplicate_mode_delay_on_mode_change_cfea4(char param_1,short *param_2)

{
  uint32_t puVar1;
  
  if (param_1 != DAT_febecbed) {
    *param_2 = 0;
    if (param_1 == '\0') {
      DAT_febecbf6 = 0;
      DAT_febecbfa = 0;
      DAT_febecbfc = 0;
      return;
    }
    puVar1 = ((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb148cu + (uint32_t)(DAT_febeac3c & 1) * 4u))))));
    if (param_1 == '\x01') {
      DAT_febecbf6 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(puVar1 + 0x36))));
    }
    else if (param_1 == '\x02') {
      DAT_febecbf6 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(puVar1 + 0x38))));
    }
    else {
      DAT_febecbf6 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(puVar1 + 0x3a))));
    }
    DAT_febecbfa = DAT_febecbf6;
    DAT_febecbfc = DAT_febecbf6;
    *param_2 = *param_2 + 1;
  }
  return;
}

void advance_mode_delay_and_commit_outside_active_window_cff04(void)

{
  undefined1 uVar1;
  ushort uVar2;
  uint32_t puVar3;
  undefined1 uVar4;
  ushort uStack_a;
  
  uVar1 = DAT_febecbea;
  puVar3 = 0xfebeb800u;
  uStack_a = DAT_febecbf8;
  if (((DAT_febecbf6 == DAT_febecbfa) || (DAT_febecbf6 == DAT_febecbfc)) ||
     (uVar2 = DAT_febecbfa, DAT_febecbfa != DAT_febecbfc)) {
    uVar2 = DAT_febecbf6;
  }
  if (DAT_febecbeb == '\x01') {
    uVar4 = DAT_febecbfe;
    if (DAT_febecbf8 < uVar2) {
      uStack_a = DAT_febecbf8 + 1;
    }
    else if (DAT_febecbec == '\0') {
      puVar3 = 0xfebeb800u;
      reload_triplicate_mode_delay_on_mode_change_cfea4(DAT_febecbea,&uStack_a);
      uVar4 = uVar1;
    }
  }
  else {
    uVar4 = 0;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x13fe))))) = uVar4;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + 0x13f8)))) = uStack_a;
  return;
}

void clear_waveform_curve_gain_pair_cff6e(void)

{
  DAT_febecc1a = 0;
  DAT_febecc1c = 0;
  return;
}

void fill_constant_block_cff78(void)

{
  DAT_febecc20 = 0;
  DAT_febecc18 = 0;
  DAT_febecc00 = 0;
  DAT_febecc04 = 0;
  DAT_febecc08 = 0;
  DAT_febecc0c = 0;
  DAT_febecc10 = 0;
  DAT_febecc1e = 0;
  DAT_febecc14 = 0;
  DAT_febecc22 = 0;
  return;
}

void interpolate_two_input_curves_and_scale_second_gain_cffa2(void)

{
  ushort input;
  uint32_t puVar1;
  int iVar2;
  
  input = DAT_febeadf6;
  puVar1 = 0xfebeb800u;
  iVar2 = interpolate_unsigned_axis_sentinel_curve
                    (((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb148cu + (uint32_t)(DAT_febeac3c & 1) * 4u)))) + 0x3c))),DAT_febeadf6);
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + 0x141a)))) = (short)iVar2;
  iVar2 = interpolate_unsigned_axis_sentinel_curve
                    (((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb148cu + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xbc4))))) & 1) * 4u)))) + 0x60))),input);
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + 0x141c)))) = (short)((int)(iVar2 * (uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x9c6))))) / 0x40000)
  ;
  return;
}

void map_absolute_input_to_waveform_gain_curve_cfffc(void)

{
  uint32_t puVar1;
  ushort input;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  input = abs_s16_wrapping(((int)(int16_t)DAT_febeac0e));
  iVar2 = interpolate_unsigned_axis_sentinel_curve
                    (((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb148cu + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xbc4))))) & 1) * 4u)))) + 0x84))),input);
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + 0x1418)))) = (short)iVar2;
  return;
}
