#include "common.h"

void reconcile_c1f8_c1fc_filter_states_and_latch_flags_c6038(void)

{
  ushort uVar4;
  int delta;
  int scaled;
  int product;
  int bound;
  
  uVar4 = 0;
  delta = (int)(short)DAT_febec21e - (int)(short)DAT_febec220;
  scaled = (int)(DAT_febec1f8 << 10);
  if (delta > -(int)DAT_000afaf8 && delta < (int)DAT_000afaf8) {
    product = (int)(short)DAT_febec220 * (int)DAT_000af82c;
    bound = (int)DAT_000afafc * (int)DAT_000af82c;
    delta = product - scaled;
    if (delta <= -bound || delta >= bound) {
      DAT_febec1f8 = (uint)(product / 0x400);
      uVar4 = 0x10;
    }
  }
  else {
    if ((int)DAT_000af82c != 0) {
      if (scaled == (int)0x80000000 && (int)DAT_000af82c == -1) {
        scaled = 0;
      }
      else {
        scaled = scaled / (int)DAT_000af82c;
      }
    }
    uVar4 = 0x20;
    DAT_febec220 = (short)scaled;
  }
  delta = (int)(short)DAT_febec226 - (int)(short)DAT_febec224;
  scaled = (int)(DAT_febec1fc << 10);
  if (delta > -(int)DAT_000afb00 && delta < (int)DAT_000afb00) {
    product = (int)(short)DAT_febec224 * (int)DAT_000af830;
    bound = (int)DAT_000afb04 * (int)DAT_000af830;
    delta = product - scaled;
    if (delta <= -bound || delta >= bound) {
      DAT_febec1fc = (uint)(product / 0x400);
      uVar4 = uVar4 | 0x40;
    }
  }
  else {
    if ((int)DAT_000af830 != 0) {
      if (scaled == (int)0x80000000 && (int)DAT_000af830 == -1) {
        scaled = 0;
      }
      else {
        scaled = scaled / (int)DAT_000af830;
      }
    }
    uVar4 = uVar4 | 0x80;
    DAT_febec224 = (short)scaled;
  }
  DAT_febec230 = DAT_febec230 | uVar4;
  DAT_febec232 = DAT_febec232 | uVar4;
  return;
}

void reconcile_both_two_stage_filter_state_pairs_c6128(void)

{
  reconcile_c1f0_c1f4_filter_states_and_latch_flags_c5f52();
  reconcile_c1f8_c1fc_filter_states_and_latch_flags_c6038();
  return;
}

void fill_constant_block_c6138(void)

{
  DAT_febec24c = 0;
  DAT_febec24e = 0;
  DAT_febec240 = 0;
  DAT_febec254 = 0;
  DAT_febec266 = 0;
  DAT_febec258 = 0;
  DAT_febec244 = 0;
  DAT_febec248 = 0;
  DAT_febec256 = 0;
  DAT_febec25a = 0;
  DAT_febec264 = 0;
  DAT_febec250 = 0;
  DAT_febec252 = 0;
  DAT_febec25c = 0;
  DAT_febec25e = 0;
  DAT_febec265 = 0;
  DAT_febec260 = 0;
  DAT_febec262 = 0;
  return;
}

void update_assist_torque_input_delta(void)

{
  int iVar1;
  
  iVar1 = 0;
  DAT_febec265 = DAT_febec264;
  DAT_febec252 = ((int)(int16_t)DAT_febec24c);
  if (DAT_febec264 == '\0') {
    DAT_febec264 = '\x01';
  }
  else if (DAT_febec12a != '\x01') {
    iVar1 = (int)((int)(int16_t)DAT_febec150) - (int)((int)(int16_t)DAT_febec24c);
  }
  DAT_febec250 = (short)iVar1;
  DAT_febec240 = (iVar1 * 0x4e2) / 0x10;
  if ((int)DAT_febec240 + -0x7fff < 0 == ((int)DAT_febec240 < 0 && -1 < (int)DAT_febec240 + -0x7fff) &&
      ((int)(int32_t)DAT_febec240) != 0x7fff) {
    DAT_febec24e = 0x7fff;
  }
  else {
    DAT_febec24e = (undefined2)((int)(int32_t)DAT_febec240);
    if ((int)DAT_febec240 + 0x7fff < 0 != (-1 < (int)DAT_febec240 && (int)DAT_febec240 + 0x7fff < 0)) {
      DAT_febec24e = 0x8001;
    }
  }
  DAT_febec24c = ((int)(int16_t)DAT_febec150);
  return;
}

void filter_torque_rate_compensation_input(void)

{
  bool bVar1;
  int iVar2;
  int iVar3;
  
  DAT_febec25e = ((int)(int16_t)DAT_febec258);
  DAT_febec244 = (((int)(int16_t)DAT_febec24e) + DAT_febec244) - (int)((int)(int16_t)DAT_febec256);
  iVar3 = DAT_febec244 * 0x400;
  if (DAT_000af860 != 0) {
    if (iVar3 == -0x80000000 && DAT_000af860 == -1) {
      iVar3 = 0;
    }
    else {
      iVar3 = iVar3 / (int)DAT_000af860;
    }
  }
  iVar2 = (int)DAT_000af868;
  DAT_febec256 = (short)iVar3;
  DAT_febec25c = ((int)(int16_t)DAT_febec254);
  DAT_febec248 = (DAT_febec248 + ((int)(int16_t)DAT_febec256)) - (int)((int)(int16_t)DAT_febec25a);
  iVar3 = DAT_febec248 * 0x400;
  if (DAT_000af864 != 0) {
    if (iVar3 == -0x80000000 && DAT_000af864 == -1) {
      iVar3 = 0;
    }
    else {
      iVar3 = iVar3 / (int)DAT_000af864;
    }
  }
  DAT_febec25a = (short)iVar3;
  iVar3 = (int)((int)(int16_t)DAT_febec25a);
  DAT_febec266 = DAT_000af868;
  if ((iVar3 - iVar2 < 0 != (iVar3 < 0 != iVar2 < 0 && iVar2 < 0 == iVar3 - iVar2 < 0) ||
       iVar3 == iVar2) &&
     (iVar2 = iVar3 + DAT_000af868, bVar1 = -(int)DAT_000af868 < 0, DAT_febec266 = ((int)(int16_t)DAT_febec25a),
     iVar2 < 0 != (iVar3 < 0 != bVar1 && bVar1 == iVar2 < 0))) {
    DAT_febec266 = -DAT_000af868;
  }
  DAT_febec254 = ((int)(int16_t)DAT_febec256);
  DAT_febec258 = ((int)(int16_t)DAT_febec25a);
  return;
}

void repair_torque_rate_filter_state(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  DAT_febec260 = 0;
  iVar1 = (int)((int)(int16_t)DAT_febec254) - (int)((int)(int16_t)DAT_febec256);
  iVar4 = DAT_febec244 * 0x400;
  iVar2 = -DAT_000afb24;
  if (-(int)DAT_000afb24 < iVar1 && iVar1 < (int)DAT_000afb24) {
    iVar4 = ((int)(int16_t)DAT_febec256) * DAT_000af860;
    iVar1 = iVar4 + DAT_febec244 * -0x400;
    iVar2 = DAT_000afb28 * DAT_000af860;
    iVar3 = -iVar2;
    if ((iVar1 + iVar2 < 0 != (iVar1 < 0 != iVar3 < 0 && iVar3 < 0 == iVar1 + iVar2 < 0) ||
         iVar1 == iVar3) ||
       (iVar1 - iVar2 < 0 == (iVar1 < 0 != iVar2 < 0 && iVar2 < 0 == iVar1 - iVar2 < 0))) {
      DAT_febec244 = iVar4 / 0x400;
      DAT_febec260 = 1;
    }
  }
  else {
    if (DAT_000af860 != 0) {
      if (iVar4 == -0x80000000 && DAT_000af860 == -1) {
        iVar4 = 0;
      }
      else {
        iVar4 = (int)iVar4 / (int)DAT_000af860;
      }
    }
    DAT_febec260 = 2;
    DAT_febec256 = (short)iVar4;
  }
  iVar1 = (int)((int)(int16_t)DAT_febec258) - (int)((int)(int16_t)DAT_febec25a);
  iVar4 = DAT_febec248 * 0x400;
  iVar2 = -DAT_000afb2c;
  if (-(int)DAT_000afb2c < iVar1 && iVar1 < (int)DAT_000afb2c) {
    iVar4 = ((int)(int16_t)DAT_febec25a) * DAT_000af864;
    iVar1 = iVar4 + DAT_febec248 * -0x400;
    iVar2 = DAT_000afb30 * DAT_000af864;
    iVar3 = -iVar2;
    if ((iVar1 + iVar2 < 0 != (iVar1 < 0 != iVar3 < 0 && iVar3 < 0 == iVar1 + iVar2 < 0) ||
         iVar1 == iVar3) ||
       (iVar1 - iVar2 < 0 == (iVar1 < 0 != iVar2 < 0 && iVar2 < 0 == iVar1 - iVar2 < 0))) {
      DAT_febec248 = iVar4 / 0x400;
      DAT_febec260 = DAT_febec260 | 4;
    }
  }
  else {
    if (DAT_000af864 != 0) {
      if (iVar4 == -0x80000000 && DAT_000af864 == -1) {
        iVar4 = 0;
      }
      else {
        iVar4 = (int)iVar4 / (int)DAT_000af864;
      }
    }
    DAT_febec260 = DAT_febec260 | 8;
    DAT_febec25a = (short)iVar4;
  }
  DAT_febec262 = DAT_febec262 | DAT_febec260;
  return;
}

void fill_constant_block_c635a(void)

{
  DAT_febec280 = 0;
  DAT_febec268 = 0;
  DAT_febec282 = 0;
  DAT_febec26c = 0;
  DAT_febec284 = 0;
  DAT_febec270 = 0;
  DAT_febec286 = 0;
  DAT_febec288 = 0;
  DAT_febec28a = 0;
  DAT_febec274 = 0;
  DAT_febec28c = 0;
  DAT_febec278 = 0;
  DAT_febec28e = 0;
  DAT_febec27c = 0;
  DAT_febec290 = 0;
  DAT_febec292 = 0;
  DAT_febec294 = 0;
  DAT_febec296 = 0;
  DAT_febec298 = 0;
  DAT_febec29a = 0;
  return;
}

void seed_four_stage_filter_history_from_ac44_c63ac(void)

{
  int iVar1;
  
  iVar1 = (int)((int)(int16_t)DAT_febeac44);
  DAT_febec280 = ((int)(int16_t)DAT_febeac44);
  DAT_febec282 = ((int)(int16_t)DAT_febeac44);
  DAT_febec286 = ((int)(int16_t)DAT_febeac44);
  DAT_febec288 = ((int)(int16_t)DAT_febeac44);
  DAT_febec28a = ((int)(int16_t)DAT_febeac44);
  DAT_febec28c = ((int)(int16_t)DAT_febeac44);
  DAT_febec290 = ((int)(int16_t)DAT_febeac44);
  DAT_febec268 = ((int)DAT_000af86c * iVar1) / 0x400;
  DAT_febec292 = ((int)(int16_t)DAT_febeac44);
  DAT_febec270 = (iVar1 * (int)DAT_000af874) / 0x400;
  DAT_febec274 = (iVar1 * (int)PTR_DAT_000af878) / 0x400;
  DAT_febec27c = (iVar1 * (int)DAT_000af880) / 0x400;
  return;
}

void step_first_two_ac44_filter_stages_with_blend_c642c(void)

{
  int iVar1;
  int iVar2;
  
  iVar1 = (int)((int)(int16_t)DAT_febec280);
  DAT_febec280 = ((int)(int16_t)DAT_febeac44);
  DAT_febec268 = iVar1 + DAT_febec268 + ((int)(int16_t)DAT_febeac44) + ((int)(int16_t)DAT_febec282) * -2;
  iVar1 = DAT_febec268 * 0x400;
  if (DAT_000af86c != 0) {
    if (iVar1 == -0x80000000 && DAT_000af86c == -1) {
      iVar1 = 0;
    }
    else {
      iVar1 = (int)iVar1 / (int)DAT_000af86c;
    }
  }
  DAT_febec282 = (short)iVar1;
  DAT_febec26c = (int)((int)(int16_t)DAT_febec282) +
                 (DAT_000af870 * ((int)((int)(int16_t)DAT_febeac44) - (int)((int)(int16_t)DAT_febec282))) / 0x400;
  if ((int)DAT_febec26c + -0x7fff < 0 == ((int)DAT_febec26c < 0 && -1 < (int)DAT_febec26c + -0x7fff) &&
      ((int)(int32_t)DAT_febec26c) != 0x7fff) {
    iVar1 = 0x7fff;
  }
  else {
    iVar1 = -0x7fff;
    if ((int)DAT_febec26c + 0x7fff < 0 == (-1 < (int)DAT_febec26c && (int)DAT_febec26c + 0x7fff < 0)) {
      iVar1 = (int)(short)((int)(int32_t)DAT_febec26c);
    }
  }
  iVar2 = (int)((int)(int16_t)DAT_febec286);
  DAT_febec284 = (short)iVar1;
  DAT_febec286 = (short)iVar1;
  DAT_febec270 = iVar2 + DAT_febec270 + iVar1 + ((int)(int16_t)DAT_febec288) * -2;
  iVar1 = DAT_febec270 * 0x400;
  if (DAT_000af874 != 0) {
    if (iVar1 == -0x80000000 && DAT_000af874 == -1) {
      iVar1 = 0;
    }
    else {
      iVar1 = (int)iVar1 / (int)DAT_000af874;
    }
  }
  DAT_febec288 = (short)iVar1;
  return;
}

void step_last_two_filter_stages_with_blend_c64cc(void)

{
  int iVar1;
  int iVar2;
  
  iVar1 = (int)((int)(int16_t)DAT_febec28a);
  DAT_febec28a = ((int)(int16_t)DAT_febec288);
  DAT_febec274 = iVar1 + DAT_febec274 + ((int)(int16_t)DAT_febec288) + ((int)(int16_t)DAT_febec28c) * -2;
  iVar1 = DAT_febec274 * 0x400;
  if (PTR_DAT_000af878 != 0) {
    if (iVar1 == -0x80000000 && PTR_DAT_000af878 == 0xffffffffu) {
      iVar1 = 0;
    }
    else {
      iVar1 = iVar1 / (int)PTR_DAT_000af878;
    }
  }
  DAT_febec28c = (short)iVar1;
  DAT_febec278 = (int)((int)(int16_t)DAT_febec28c) +
                 ((int)DAT_000af87c * ((int)((int)(int16_t)DAT_febec288) - (int)((int)(int16_t)DAT_febec28c))) / 0x400;
  if ((int)DAT_febec278 + -0x7fff < 0 == ((int)DAT_febec278 < 0 && -1 < (int)DAT_febec278 + -0x7fff) &&
      ((int)(int32_t)DAT_febec278) != 0x7fff) {
    iVar1 = 0x7fff;
  }
  else {
    iVar1 = -0x7fff;
    if ((int)DAT_febec278 + 0x7fff < 0 == (-1 < (int)DAT_febec278 && (int)DAT_febec278 + 0x7fff < 0)) {
      iVar1 = (int)(short)((int)(int32_t)DAT_febec278);
    }
  }
  iVar2 = (int)((int)(int16_t)DAT_febec290);
  DAT_febec28e = (short)iVar1;
  DAT_febec290 = (short)iVar1;
  DAT_febec27c = iVar2 + DAT_febec27c + iVar1 + ((int)(int16_t)DAT_febec292) * -2;
  iVar1 = DAT_febec27c * 0x400;
  if (DAT_000af880 != 0) {
    if (iVar1 == -0x80000000 && DAT_000af880 == -1) {
      iVar1 = 0;
    }
    else {
      iVar1 = (int)iVar1 / (int)DAT_000af880;
    }
  }
  DAT_febec292 = (short)iVar1;
  return;
}

void slew_and_saturate_c292_into_c29a_c656c(void)

{
  bool bVar1;
  int iVar2;
  short sVar3;
  int iVar4;
  int iVar5;
  
  iVar5 = (int)DAT_000af884;
  iVar4 = (int)(short)(((int)(int16_t)DAT_febec292) - ((int)(int16_t)DAT_febec29a));
  DAT_febec294 = ((int)(int16_t)DAT_febec292) - ((int)(int16_t)DAT_febec29a);
  sVar3 = DAT_000af884;
  if (iVar4 - iVar5 < 0 != (iVar4 < 0 != iVar5 < 0 && iVar5 < 0 == iVar4 - iVar5 < 0)) {
    iVar2 = -(int)DAT_000af884;
    iVar5 = iVar4 + DAT_000af884;
    DAT_febec296 = ((int)(int16_t)DAT_febec292);
    if (iVar5 < 0 == (iVar4 < 0 != iVar2 < 0 && iVar2 < 0 == iVar5 < 0) && iVar4 != iVar2)
    goto LAB_000c65a2;
    sVar3 = -DAT_000af884;
  }
  DAT_febec296 = sVar3 + ((int)(int16_t)DAT_febec29a);
LAB_000c65a2:
  iVar4 = (int)(int16_t)DAT_febec296;
  iVar5 = (int)(short)DAT_000af886;
  if (iVar4 > iVar5) {
    DAT_febec29a = (short)iVar5;
  }
  else if (iVar4 <= -iVar5) {
    DAT_febec29a = (short)(-iVar5);
  }
  else {
    DAT_febec29a = (short)iVar4;
  }
  return;
}

void initialize_and_step_four_stage_ac44_filter_c65c8(void)

{
  uint32_t puVar1;
  char cVar2;
  
  puVar1 = 0xfebeb800u;
  cVar2 = DAT_febec298;
  if (DAT_febec298 == '\0') {
    puVar1 = 0xfebeb800u;
    seed_four_stage_filter_history_from_ac44_c63ac();
    cVar2 = 'Z';
  }
  step_first_two_ac44_filter_stages_with_blend_c642c();
  step_last_two_filter_stages_with_blend_c64cc();
  slew_and_saturate_c292_into_c29a_c656c();
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0xa98))))) = cVar2;
  return;
}

void fill_constant_block_c65f0(void)

{
  DAT_febec2a6 = 0;
  DAT_febec29c = 0x400;
  DAT_febec29e = 0x400;
  DAT_febec2a0 = 0x400;
  DAT_febec2a2 = 0x400;
  DAT_febec2a4 = 0x400;
  return;
}

void prepare_gain_parameters_c2a4(F33GainSlewState *state,uint mode)

{
  int iVar1;
  ushort uVar2;
  uchar uVar3;
  ushort uVar4;
  ushort uVar5;
  ushort uVar6;
  
  if ((mode & 0xff) < 7) {
    uVar3 = '\x02';
    iVar1 = (short)(DAT_febeac3c & 1) * 7 + (mode & 0xff);
    uVar2 = *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xd3130u + (uint32_t)(iVar1 * 0x10) * 1u))));
    uVar6 = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd312cu + (uint32_t)(iVar1 * 4) * 4u)))))));
    uVar5 = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3134u + (uint32_t)(iVar1 * 4) * 4u)))))));
    uVar4 = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3128u + (uint32_t)(iVar1 * 4) * 4u)))))));
  }
  else {
    uVar3 = '\x01';
    uVar2 = DAT_febec29c;
    uVar6 = DAT_febec2a0;
    uVar5 = DAT_febec2a2;
    uVar4 = DAT_febec29e;
  }
  state->down_step = uVar6;
  state->up_step = uVar5;
  state->down_target = uVar4;
  state->up_target = uVar2;
  state->direction = uVar3;
  return;
}

void prepare_and_step_unsigned_gain_c2a4_c666c(void)

{
  int iVar1;
  uint32_t puVar2;
  uint uVar3;
  F33GainSlewState local_10;
  
  puVar2 = 0xfebeb800u;
  uVar3 = 7;
  if (DAT_febecab7 == '\x01') {
    uVar3 = (uint)DAT_febecb00;
  }
  local_10.current = DAT_febec2a4;
  if (uVar3 < 7) {
    local_10.direction = '\x02';
    iVar1 = (short)(DAT_febeac3c & 1) * 7 + uVar3;
    local_10.up_target = *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xd3130u + (uint32_t)(iVar1 * 0x10) * 1u))));
    local_10.down_step = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd312cu + (uint32_t)(iVar1 * 4) * 4u)))))));
    local_10.up_step = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3134u + (uint32_t)(iVar1 * 4) * 4u)))))));
    local_10.down_target = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3128u + (uint32_t)(iVar1 * 4) * 4u)))))));
  }
  else {
    local_10.direction = '\x01';
    local_10.up_target = DAT_febec29c;
    local_10.down_step = DAT_febec2a0;
    local_10.up_step = DAT_febec2a2;
    local_10.down_target = DAT_febec29e;
  }
  step_retained_unsigned_gain(&local_10);
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xaa0)))) = local_10.down_step;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xaa2)))) = local_10.up_step;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xa9e)))) = local_10.down_target;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xa9c)))) = local_10.up_target;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xaa4)))) = local_10.current;
  return;
}

uint scale_signed_sample_by_c2a4_store_and_return_c2a6_c66b4(short param_1)

{
  DAT_febec2a6 = (short)((int)((uint)DAT_febec2a4 * (int)param_1) / 0x400);
  return DAT_febec2a6;
}

void reset_c2a8_curve_filter_filter_and_gain_state_c66ce(void)

{
  DAT_febec2d4 = 0;
  DAT_febec2e0 = 0;
  DAT_febeabac = 0;
  DAT_febec2bc = 0;
  DAT_febec2de = 0;
  DAT_febec2b0 = 0;
  DAT_febec2ac = 0;
  DAT_febec2d0 = 0;
  DAT_febec2d2 = 0;
  DAT_febec2a8 = 0;
  DAT_febec2ce = 0;
  DAT_febec2cc = 0;
  DAT_febec2ca = 0;
  DAT_febec2df = 0x5a;
  DAT_febec2c8 = 0;
  DAT_febec2c6 = 0;
  DAT_febec2c4 = 0;
  DAT_febec2c2 = 0;
  DAT_febec2b4 = PTR_DAT_000b1180;
  DAT_febec2c0 = 0;
  DAT_febec2be = 0;
  DAT_febec2e2 = 0;
  DAT_febec2da = DAT_000b11a8;
  DAT_febec2d8 = 0x400;
  DAT_febec2d6 = 0x400;
  DAT_febec2dc = DAT_000b11a8;
  DAT_febec2b8 = ((int)DAT_000b11a8 << 10) / 0x400;
  return;
}

void blend_signed_curve_pair_slew_gain_and_filter_c2d2_c675c(ushort param_1,short param_2,char param_3)

{
  char cVar1;
  short sVar2;
  uint32_t puVar3;
  short sVar4;
  short sVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  int iVar10;
  ushort uVar11;
  short sVar12;
  
  puVar3 = 0xfebeb800u;
  iVar10 = (int)param_2;
  iVar8 = (int)((int)(int16_t)DAT_febec1a6);
  iVar7 = (int)((int)(int16_t)DAT_febec1a4) + (DAT_febec156 & 3) * 8;
  iVar9 = (int)DAT_000b118e;
  iVar6 = interpolate_unsigned_axis_sentinel_curve
                    (((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb144cu + (uint32_t)(DAT_febeac3c & 1) * 4u)))) + iVar7 * 0x28 + 0xa54)))
                     ,param_1);
  iVar7 = interpolate_unsigned_axis_sentinel_curve
                    (((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb144cu + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xbc4))))) & 1) * 4u)))) + iVar7 * 0x28 + 0xa7c))),
                     param_1);
  sVar2 = (short)(((iVar7 - iVar6) * iVar8) / 0x400) + (short)iVar6;
  if (iVar10 < 0) {
    sVar2 = -sVar2;
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0xac0)))) = (short)iVar6;
  cVar1 = DAT_000b11aa;
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0xac2)))) = (short)iVar7;
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0xac4)))) = sVar2;
  if (param_3 == cVar1) {
    iVar7 = (int)DAT_000b1188;
  }
  else if (param_3 == DAT_000b11ab) {
    iVar7 = (int)DAT_000b118a;
  }
  else {
    iVar7 = (int)DAT_000b118c;
  }
  sVar5 = (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0xace))));
  iVar6 = (int)sVar5;
  sVar12 = (short)iVar7;
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0xacc)))) = sVar12;
  if ((iVar10 - iVar9 < 0 == (iVar10 < 0 != iVar9 < 0 && iVar9 < 0 == iVar10 - iVar9 < 0)) ||
     (iVar8 = -iVar9,
     iVar10 + iVar9 < 0 != (iVar10 < 0 != iVar8 < 0 && iVar8 < 0 == iVar10 + iVar9 < 0) ||
     iVar10 == iVar8)) {
    uVar11 = 0;
  }
  else {
    uVar11 = (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0xaca)))) + 1;
    if (DAT_000b1190 <= uVar11) {
      uVar11 = 0;
      iVar8 = iVar6;
      if ((iVar6 - iVar7 < 0 == (iVar6 < 0 != iVar7 < 0 && iVar7 < 0 == iVar6 - iVar7 < 0) &&
           iVar6 != iVar7) &&
         (sVar4 = abs_s16_wrapping(sVar5 - sVar12), iVar9 = (int)DAT_000b1192,
         iVar6 = sVar4 - iVar9, iVar8 = iVar7,
         iVar6 < 0 == (sVar4 < 0 != iVar9 < 0 && iVar9 < 0 == iVar6 < 0))) {
        iVar8 = (int)(short)(sVar5 - DAT_000b1192);
      }
      iVar6 = iVar8;
      if ((iVar8 - iVar7 < 0 != (iVar8 < 0 != iVar7 < 0 && iVar7 < 0 == iVar8 - iVar7 < 0)) &&
         (sVar5 = abs_s16_wrapping((short)iVar8 - sVar12), iVar10 = (int)DAT_000b1192,
         iVar9 = sVar5 - iVar10, iVar6 = iVar7,
         iVar9 < 0 == (sVar5 < 0 != iVar10 < 0 && iVar10 < 0 == iVar9 < 0))) {
        iVar6 = iVar8 + DAT_000b1192;
      }
    }
  }
  sVar5 = DAT_000b1194;
  iVar8 = (int)DAT_000b1194;
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0xace)))) = (short)iVar6;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + 0xaca)))) = uVar11;
  sVar2 = (short)(((int)(short)iVar6 * (int)sVar2) / 0x400);
  iVar7 = (int)sVar2;
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0xac6)))) = sVar2;
  if ((iVar7 - iVar8 < 0 != (iVar7 < 0 != iVar8 < 0 && iVar8 < 0 == iVar7 - iVar8 < 0) ||
       iVar7 == iVar8) &&
     (iVar6 = -iVar8, sVar5 = sVar2,
     iVar7 + iVar8 < 0 != (iVar7 < 0 != iVar6 < 0 && iVar6 < 0 == iVar7 + iVar8 < 0) ||
     iVar7 == iVar6)) {
    sVar5 = (short)iVar6;
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0xac8)))) = sVar5;
  iVar7 = ((*((int *)camry_host_ptr((uint32_t)(puVar3 + 0xaa8)))) + (int)sVar5) - (int)(*((short *)camry_host_ptr((uint32_t)(puVar3 + 0xad2))));
  (*((int *)camry_host_ptr((uint32_t)(puVar3 + 0xaa8)))) = iVar7;
  iVar7 = iVar7 * 0x400;
  if (DAT_000b117c != 0) {
    if (iVar7 == -0x80000000 && DAT_000b117c == -1) {
      iVar7 = 0;
    }
    else {
      iVar7 = (int)iVar7 / (int)DAT_000b117c;
    }
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0xad2)))) = (short)iVar7;
  return;
}

void step_c2d0_enable_envelope_with_hysteresis_c68fa(short param_1,char param_2)

{
  bool bVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  iVar2 = (int)param_1;
  iVar4 = (int)((int)(int16_t)DAT_febec2d0);
  iVar3 = (int)DAT_000b1198;
  if (((param_2 == '\0') || (DAT_febead18 != '\x11')) || (DAT_febead41 == 'Z')) {
    DAT_febec2ac = DAT_febec2b0 * (int)PTR_DAT_000b1180;
    if (DAT_febec2b4 != 0) {
      if (DAT_febec2ac == -0x80000000 && DAT_febec2b4 == 0xffffffffu) {
        DAT_febec2ac = -0x80000000;
      }
      else {
        DAT_febec2ac = DAT_febec2ac / (int)DAT_febec2b4;
      }
    }
    DAT_febec2b0 = DAT_febec2ac - iVar4;
    iVar2 = DAT_febec2b0 * 0x400;
    if (PTR_DAT_000b1180 != 0) {
      if (iVar2 == -0x80000000 && PTR_DAT_000b1180 == 0xffffffffu) {
        iVar2 = 0;
      }
      else {
        iVar2 = iVar2 / (int)PTR_DAT_000b1180;
      }
    }
    iVar4 = (int)(short)iVar2;
    DAT_febec2b4 = PTR_DAT_000b1180;
  }
  else {
    if (DAT_febec2de == '\0') {
      if (iVar2 - iVar3 < 0 != (iVar2 < 0 != iVar3 < 0 && iVar3 < 0 == iVar2 - iVar3 < 0) ||
          iVar2 == iVar3) {
        DAT_febec2ac = DAT_febec2b0 * (int)PTR_DAT_000b1184;
        if (DAT_febec2b4 != 0) {
          if (DAT_febec2ac == -0x80000000 && DAT_febec2b4 == 0xffffffffu) {
            DAT_febec2ac = -0x80000000;
          }
          else {
            DAT_febec2ac = DAT_febec2ac / (int)DAT_febec2b4;
          }
        }
        DAT_febec2b0 = (DAT_febec2ac + 0x100) - iVar4;
        iVar2 = DAT_febec2b0 * 0x400;
        if (PTR_DAT_000b1184 != 0) {
          if (iVar2 == -0x80000000 && PTR_DAT_000b1184 == 0xffffffffu) {
            iVar2 = 0;
          }
          else {
            iVar2 = iVar2 / (int)PTR_DAT_000b1184;
          }
        }
        iVar4 = (int)(short)iVar2;
        DAT_febec2b4 = PTR_DAT_000b1184;
      }
    }
    else {
      DAT_febec2ac = DAT_febec2b0 * (int)PTR_DAT_000b1180;
      if (DAT_febec2b4 != 0) {
        if (DAT_febec2ac == -0x80000000 && DAT_febec2b4 == 0xffffffffu) {
          DAT_febec2ac = -0x80000000;
        }
        else {
          DAT_febec2ac = DAT_febec2ac / (int)DAT_febec2b4;
        }
      }
      DAT_febec2b0 = DAT_febec2ac - iVar4;
      iVar2 = DAT_febec2b0 * 0x400;
      if (PTR_DAT_000b1180 != 0) {
        if (iVar2 == -0x80000000 && PTR_DAT_000b1180 == 0xffffffffu) {
          iVar2 = 0;
        }
        else {
          iVar2 = iVar2 / (int)PTR_DAT_000b1180;
        }
      }
      iVar4 = (int)(short)iVar2;
      DAT_febec2b4 = PTR_DAT_000b1180;
    }
    if (DAT_febec2de != '\x01') {
      iVar2 = (int)DAT_000b119c;
      if (iVar4 - iVar2 < 0 == (iVar4 < 0 != iVar2 < 0 && iVar2 < 0 == iVar4 - iVar2 < 0)) {
        iVar4 = 0x100;
        DAT_febec2b0 = ((int)PTR_DAT_000b1184 << 8) / 0x400;
        DAT_febec2ac = DAT_febec2b0;
      }
      goto LAB_000c69d6;
    }
  }
  iVar3 = (int)DAT_000b119a;
  iVar2 = iVar4 - iVar3;
  bVar1 = iVar4 < 0 != iVar3 < 0 && iVar3 < 0 == iVar2 < 0;
  DAT_febec2de = iVar2 < 0 == bVar1 && iVar4 != iVar3;
  if (iVar2 < 0 != bVar1 || iVar4 == iVar3) {
    iVar4 = 0;
    DAT_febec2ac = 0;
    DAT_febec2b0 = 0;
  }
LAB_000c69d6:
  DAT_febec2d0 = (short)iVar4;
  return;
}

undefined2 apply_c2d0_envelope_and_c2d6_c2a4_gains_c69ec(char param_1)

{
  uint32_t puVar1;
  int iVar2;
  undefined2 uVar3;
  char cVar4;
  
  puVar1 = 0xfebeb800u;
  iVar2 = ((int)((int)(int16_t)DAT_febec2d0) * (int)((int)(int16_t)DAT_febec2d2)) / 0x100;
  if (iVar2 + -0x7fff < 0 == (iVar2 < 0 && -1 < iVar2 + -0x7fff) && iVar2 != 0x7fff) {
    iVar2 = 0x7fff;
  }
  else if (iVar2 + 0x7fff < 0 != (-1 < iVar2 && iVar2 + 0x7fff < 0)) {
    iVar2 = -0x7fff;
  }
  DAT_febec2bc = (short)iVar2;
  if (param_1 == '\0') {
    cVar4 = 'Z';
  }
  else {
    DAT_febeabac = DAT_febec2bc;
    if (DAT_febec2de == '\0') {
      cVar4 = '\0';
      goto LAB_000c6a44;
    }
    cVar4 = DAT_febec2df;
    if (DAT_febec2df != 'Z') goto LAB_000c6a44;
  }
  DAT_febeabac = 0;
LAB_000c6a44:
  uVar3 = scale_signed_sample_by_c2a4_store_and_return_c2a6_c66b4((int)(short)(((int)(int16_t)DAT_febec2d6 * (int)(int16_t)DAT_febeabac) / 0x400));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + 0xabe)))) = uVar3;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0xadf))))) = cVar4;
  return uVar3;
}

void bound_c2be_by_b1196_into_c2e2_c6a68(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = (int)((int)(int16_t)DAT_febec2be);
  iVar2 = (int)DAT_000b1196;
  DAT_febec2e2 = DAT_000b1196;
  if ((iVar3 - iVar2 < 0 != (iVar3 < 0 != iVar2 < 0 && iVar2 < 0 == iVar3 - iVar2 < 0) ||
       iVar3 == iVar2) &&
     (iVar1 = -iVar2, DAT_febec2e2 = ((int)(int16_t)DAT_febec2be),
     iVar3 + iVar2 < 0 != (iVar3 < 0 != iVar1 < 0 && iVar1 < 0 == iVar3 + iVar2 < 0) ||
     iVar3 == iVar1)) {
    DAT_febec2e2 = (short)iVar1;
  }
  return;
}

void update_c2d0_envelope_scaled_output_and_final_bound_c6a88(short param_1,undefined1 param_2)

{
  step_c2d0_enable_envelope_with_hysteresis_c68fa((int)param_1, (uint)(byte)param_2);
  apply_c2d0_envelope_and_c2d6_c2a4_gains_c69ec(param_2);
  bound_c2be_by_b1196_into_c2e2_c6a68();
  return;
}

void snapshot_c084_and_run_c2a8_curve_curve_filter_c6aa4(void)

{
  undefined1 uVar1;
  uint32_t puVar2;
  short sVar3;
  undefined4 uVar4;
  int iVar5;
  int iVar6;
  
  puVar2 = 0xfebeb800u;
  uVar4 = raise_priority_mask_and_return_previous_d1da0(0xffc0);
  uVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x88e)))));
  iVar6 = (*((int *)camry_host_ptr((uint32_t)(puVar2 + 0x884))));
  restore_priority_mask_preserving_interrupt_enable_d1dc6(uVar4);
  if (iVar6 + -0x7fff < 0 == (iVar6 < 0 && -1 < iVar6 + -0x7fff) && iVar6 != 0x7fff) {
    iVar5 = 0x7fff;
  }
  else {
    iVar5 = (int)(short)iVar6;
    if (iVar6 + 0x7fff < 0 != (-1 < iVar6 && iVar6 + 0x7fff < 0)) {
      iVar5 = -0x7fff;
    }
  }
  sVar3 = abs_s16_wrapping((short)iVar5);
  blend_signed_curve_pair_slew_gain_and_filter_c2d2_c675c((int)sVar3,iVar5,uVar1);
  update_c2d0_envelope_scaled_output_and_final_bound_c6a88((int)sVar3,uVar1);
  return;
}

void debounce_c5ec_status_and_filter_c2d6_gain_c6af6(void)

{
  char cVar1;
  ushort uVar2;
  uint32_t puVar3;
  short sVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  char cVar8;
  int iVar9;
  short *psVar10;
  
  cVar1 = DAT_febec5f4;
  uVar2 = DAT_febeadf6;
  puVar3 = 0xfebeb800u;
  sVar4 = abs_s16_wrapping(((int)(int16_t)DAT_febec5ec));
  iVar5 = (int)sVar4;
  cVar8 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0xae0)))));
  iVar9 = (int)DAT_000b11a0;
  iVar6 = (int)DAT_000b11a2;
  if (cVar8 == '\0') {
    if (((cVar1 != '\x01') ||
        (iVar5 - iVar9 < 0 != (iVar5 < 0 != iVar9 < 0 && iVar9 < 0 == iVar5 - iVar9 < 0) ||
         iVar5 == iVar9)) || (uVar2 <= DAT_000b119e)) goto LAB_000c6b74;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0xae0))))) = 1;
    cVar8 = '\x01';
  }
  else if (((cVar1 == '\0') ||
           (iVar5 - iVar6 < 0 != (iVar5 < 0 != iVar6 < 0 && iVar6 < 0 == iVar5 - iVar6 < 0) ||
            iVar5 == iVar6)) || (uVar2 <= DAT_000b119e)) {
    uVar2 = (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + 0xad4))));
    if (uVar2 <= DAT_000b11a4) {
      sVar4 = uVar2 + 1;
      uVar2 = uVar2 + 1;
      (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0xad4)))) = sVar4;
    }
    if (DAT_000b11a4 < uVar2) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0xae0))))) = 0;
      cVar8 = '\0';
    }
    goto LAB_000c6b74;
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + 0xad4)))) = 0;
LAB_000c6b74:
  iVar5 = (int)(*((short *)camry_host_ptr((uint32_t)(puVar3 + 0xadc))));
  if (cVar8 == '\x01') {
    psVar10 = ((undefined *)camry_host_ptr(0xb11a6u));
    iVar6 = 0;
  }
  else {
    psVar10 = ((undefined *)camry_host_ptr(0xb11a8u));
    iVar6 = 0x400;
  }
  iVar7 = (int)*psVar10;
  iVar9 = (*((int *)camry_host_ptr((uint32_t)(puVar3 + 0xab8)))) * (int)*psVar10;
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0xada)))) = *psVar10;
  sVar4 = *psVar10;
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0xad8)))) = (short)iVar6;
  if (iVar5 != 0) {
    if (iVar9 == -0x80000000 && iVar5 == -1) {
      iVar9 = -0x80000000;
    }
    else {
      iVar9 = (int)iVar9 / (int)iVar5;
    }
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0xadc)))) = sVar4;
  iVar5 = (iVar6 + iVar9) - (int)(*((short *)camry_host_ptr((uint32_t)(puVar3 + 0xad6))));
  (*((int *)camry_host_ptr((uint32_t)(puVar3 + 0xab8)))) = iVar5;
  iVar5 = iVar5 * 0x400;
  if (iVar7 != 0) {
    if (iVar5 == -0x80000000 && iVar7 == -1) {
      iVar5 = 0;
    }
    else {
      iVar5 = (int)iVar5 / (int)iVar7;
    }
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0xad6)))) = (short)iVar5;
  sVar4 = abs_s16_wrapping((short)iVar5 - (short)iVar6);
  iVar5 = (int)sVar4;
  if (iVar5 + -0x14 < 0 != (iVar5 < 0 && -1 < iVar5 + -0x14) || iVar5 == 0x14) {
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + 0xad6)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + 0xad8))));
  }
  return;
}

void initialize_seven_c2f8_gain_slots_to_unity_c6be0(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  DAT_febec2e4 = 0;
  DAT_febec2ee = 0x400;
  DAT_febec2ec = 0x400;
  DAT_febec2f0 = 0x400;
  DAT_febec2f2 = 0x400;
  DAT_febec2f4 = 0x400;
  iVar3 = 0;
  do {
    *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebec300u + (uint32_t)(iVar3 * 2) * 1u)))) = 0x400;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebec2f8u + (uint32_t)(iVar3) * 1u)))) = 0;
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -6;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  DAT_febec2f6 = 0x400;
  DAT_febec2e8 = 0;
  return;
}

void prepare_gain_parameters_c2f4(F33GainSlewState *state,uint mode)

{
  int iVar1;
  ushort uVar2;
  uchar uVar3;
  ushort uVar4;
  ushort uVar5;
  ushort uVar6;
  
  if ((mode & 0xff) < 7) {
    uVar3 = '\x02';
    iVar1 = (short)(DAT_febeac3c & 1) * 7 + (mode & 0xff);
    uVar2 = *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xd3210u + (uint32_t)(iVar1 * 0x10) * 1u))));
    uVar6 = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd320cu + (uint32_t)(iVar1 * 4) * 4u)))))));
    uVar5 = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3214u + (uint32_t)(iVar1 * 4) * 4u)))))));
    uVar4 = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3208u + (uint32_t)(iVar1 * 4) * 4u)))))));
  }
  else {
    uVar3 = '\x01';
    uVar2 = DAT_febec2ec;
    uVar6 = DAT_febec2f0;
    uVar5 = DAT_febec2f2;
    uVar4 = DAT_febec2ee;
  }
  state->down_step = uVar6;
  state->up_step = uVar5;
  state->down_target = uVar4;
  state->up_target = uVar2;
  state->direction = uVar3;
  return;
}

void prepare_and_step_unsigned_gain_c2f4_c6c82(void)

{
  int iVar1;
  uint32_t puVar2;
  uint uVar3;
  F33GainSlewState local_10;
  
  puVar2 = 0xfebeb800u;
  uVar3 = 7;
  if (DAT_febecab7 == '\x01') {
    uVar3 = (uint)DAT_febecb00;
  }
  local_10.current = DAT_febec2f4;
  if (uVar3 < 7) {
    local_10.direction = '\x02';
    iVar1 = (short)(DAT_febeac3c & 1) * 7 + uVar3;
    local_10.up_target = *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xd3210u + (uint32_t)(iVar1 * 0x10) * 1u))));
    local_10.down_step = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd320cu + (uint32_t)(iVar1 * 4) * 4u)))))));
    local_10.up_step = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3214u + (uint32_t)(iVar1 * 4) * 4u)))))));
    local_10.down_target = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3208u + (uint32_t)(iVar1 * 4) * 4u)))))));
  }
  else {
    local_10.direction = '\x01';
    local_10.up_target = DAT_febec2ec;
    local_10.down_step = DAT_febec2f0;
    local_10.up_step = DAT_febec2f2;
    local_10.down_target = DAT_febec2ee;
  }
  step_retained_unsigned_gain(&local_10);
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xaf0)))) = local_10.down_step;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xaf2)))) = local_10.up_step;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xaee)))) = local_10.down_target;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xaec)))) = local_10.up_target;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xaf4)))) = local_10.current;
  return;
}

void update_seven_mode_curve_gains_and_multiply_c2f6_c6cca(void)

{
  uint8_t stack_record_2c[44];
  char *pcVar1;
  int iVar2;
  int iVar3;
  ushort uVar4;
  undefined8 uVar5;
  uint uVar6;
  int iVar7;
  
  uVar5 = 0xfebeb800;
  uVar6 = 0x400;
  (*((uint16_t *)(stack_record_2c + 16))) = ((int)(int16_t)DAT_febec1a2);
  uVar4 = (ushort)DAT_febeac3c;
  iVar7 = 0;
  do {
    pcVar1 = ((undefined *)camry_host_ptr((uint32_t)(0xd32e8u + (uint32_t)(iVar7 * 0xc + (short)(uVar4 & 1) * 0x54) * 1u)));
    ((int8_t *)(stack_record_2c))[0] = *pcVar1;
    if (((int8_t *)(stack_record_2c))[0] != '\a') {
      (*((uint32_t *)(stack_record_2c + 4))) = *(undefined4 *)(pcVar1 + 4);
      iVar2 = iVar7 + (int)uVar5;
      iVar3 = iVar7 * 2 + (int)uVar5;
      (*((uint32_t *)(stack_record_2c + 8))) = *(undefined4 *)(pcVar1 + 8);
      stack_record_2c[12] = (*((undefined1 *)camry_host_ptr((uint32_t)(iVar2 + 0xaf8))));
      (*((uint16_t *)(stack_record_2c + 14))) = (*((ushort *)camry_host_ptr((uint32_t)(iVar3 + 0xb00))));
      update_retained_mode_gain_below_magnitude_threshold_ce912(((int8_t *)(stack_record_2c)));
      (*((ushort *)camry_host_ptr((uint32_t)(iVar3 + 0xb00)))) = (*((uint16_t *)(stack_record_2c + 14)));
      (*((undefined1 *)camry_host_ptr((uint32_t)(iVar2 + 0xaf8)))) = stack_record_2c[12];
      uVar6 = uVar6 * (*((uint16_t *)(stack_record_2c + 14))) >> 10 & 0xffff;
    }
    iVar3 = iVar7 + 1;
    iVar2 = iVar7 + -6;
    iVar7 = iVar3;
  } while (((iVar2 < 0) || (iVar3 < 0)));
  (*((short *)camry_host_ptr((uint32_t)((int)uVar5 + 0xaf6)))) = (short)uVar6;
  return;
}

void update_c2f4_slew_and_seven_curve_gain_product_c6d4e(void)

{
  prepare_and_step_unsigned_gain_c2f4_c6c82();
  update_seven_mode_curve_gains_and_multiply_c2f6_c6cca();
  return;
}

int apply_internal_assist_attenuation(int value)

{
  DAT_febec2e4 = (int)((uint)DAT_febec2f4 * value) / 0x400;
  DAT_febec2e8 = (int)((uint)DAT_febec2f6 * DAT_febec2e4) / 0x400;
  return DAT_febec2e8;
}

void reset_c310_curve_state_and_select_banked_tables_c6d84(void)

{
  DAT_febec35c = 0;
  DAT_febec386 = 0x400;
  DAT_febec35e = 0;
  DAT_febec360 = 0;
  DAT_febec362 = 0;
  DAT_febec364 = 0;
  DAT_febec366 = 0;
  DAT_febec368 = 0;
  DAT_febec310 = 0;
  DAT_febec36a = 0;
  DAT_febec398 = 0;
  DAT_febec399 = 0;
  DAT_febec34c = (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb144cu + (uint32_t)(DAT_febeac3c & 1) * 4u)))) + 0xf54;
  DAT_febec36c = 0;
  DAT_febec36e = 0;
  DAT_febec314 = 0;
  DAT_febec318 = 0;
  DAT_febec31c = 0;
  DAT_febec320 = 0;
  DAT_febec324 = 0;
  DAT_febec328 = 0;
  DAT_febec370 = 0;
  DAT_febec372 = 0;
  DAT_febec374 = 0;
  DAT_febec376 = 0;
  DAT_febec378 = 0;
  DAT_febec37a = 0;
  DAT_febec39a = 0;
  DAT_febec32c = 0;
  DAT_febec37c = 0;
  DAT_febec37e = 0;
  DAT_febec380 = 0;
  DAT_febec330 = 0;
  DAT_febec334 = 0;
  DAT_febec382 = 0;
  DAT_febec338 = 0;
  DAT_febec33c = 0;
  DAT_febec340 = 0;
  DAT_febec384 = 0;
  DAT_febec344 = 0;
  DAT_febec348 = 0;
  DAT_febec3a0 = 0;
  DAT_febec39c = 0;
  DAT_febec388 = 0;
  DAT_febec38a = 0;
  DAT_febec38c = 0;
  DAT_febec38e = 0;
  DAT_febec390 = 0;
  DAT_febec350 = (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb144cu + (uint32_t)(DAT_febeac3c & 1) * 4u)))) + 0xf70;
  DAT_febec354 = 0;
  DAT_febec358 = 0;
  DAT_febec392 = 0;
  DAT_febec394 = 0;
  DAT_febec396 = 0;
  return;
}

void blend_signed_curve_pair_for_c1a2_into_c362_c6e7e(void)

{
  short *points;
  short sVar1;
  short sVar2;
  uint uVar3;
  uint32_t puVar4;
  short sVar5;
  int iVar6;
  int iVar7;
  
  sVar2 = ((int)(int16_t)DAT_febec1a2);
  puVar4 = 0xfebeb800u;
  uVar3 = (uint)DAT_febec156;
  sVar5 = abs_s16_wrapping(((int)(int16_t)DAT_febec1a2));
  sVar1 = (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0xb66))));
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0xb8c)))) = (short)(uVar3 & 3);
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0xb92)))) = (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0xb64))));
  points = ((short *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb144cu + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0xbc4))))) & 1) * 4u)))) +
                    ((int)(*((volatile int16_t *)camry_host_ptr((uint32_t)(puVar4 + 0xb64)))) + (uVar3 & 3) * 8) * 0x1c + 0xf54)));
  iVar6 = interpolate_signed_sentinel_curve(points,sVar5);
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0xb5c)))) = (short)iVar6;
  iVar7 = interpolate_signed_sentinel_curve(points + 0xe,sVar5);
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0xb5e)))) = (short)iVar7;
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0xb90)))) = sVar5;
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0xb88)))) = sVar2;
  (*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar4 + 0xb4c)))) = camry_host_addr(points);
  (*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar4 + 0xb50)))) = camry_host_addr(points + 0xe);
  sVar1 = (short)(((iVar7 - iVar6) * (int)sVar1) / 0x400) + (short)iVar6;
  sVar5 = sVar1;
  if (sVar2 < 0) {
    sVar5 = -sVar1;
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0xb60)))) = sVar1;
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0xb62)))) = sVar5;
  return;
}

int scale_c362_by_c386_c376_and_internal_attenuation_c6f1e(void)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  DAT_febec344 = ((int)((int)(int16_t)DAT_febec386) * (int)((int)(int16_t)DAT_febec362)) / 0x400;
  iVar2 = apply_internal_assist_attenuation( (int)((DAT_febec344 * ((int)(int16_t)DAT_febec376))) / (int)0x400);
  (*((int *)camry_host_ptr((uint32_t)(puVar1 + 0xb48)))) = iVar2;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + 0xb96)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + 0xb76))));
  return iVar2;
}

void sum_nonlinear_and_moving_assist(void)

{
  DAT_febec358 = DAT_febec348 + ((int)(int16_t)DAT_febec5f0);
  return;
}

void bound_nonlinear_and_moving_assist(void)

{
  int value;
  int limit;

  value = (int)DAT_febec358;
  limit = nonlinear_moving_assist_limit;
  if (value > limit) {
    DAT_febec39c = (uint)limit;
  }
  else if (value <= -limit) {
    DAT_febec39c = (uint)(-limit);
  }
  else {
    DAT_febec39c = DAT_febec358;
  }
  return;
}

undefined4 lookup_c364_axis_index_and_fraction_from_bank_c6f86(void)

{
  uint8_t stack_record_8[8];
  uint32_t puVar1;
  undefined4 uVar2;
  
  puVar1 = 0xfebeb800u;
  locate_unsigned16_axis_interval_and_q10_fraction_d097a(((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb144cu + (uint32_t)(DAT_febeac3c & 1) * 4u)))) + (DAT_febec156 & 3) * 0x12 + 0x12d4))), 
               DAT_febeadf6, ((uint16_t *)(stack_record_8)), ((uint16_t *)((stack_record_8 + 2))));
  uVar2 = raise_priority_mask_and_return_previous_d1da0(0xffc0);
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + 0xb64)))) = (*((uint16_t *)(stack_record_8 + 0)));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + 0xb66)))) = (*((uint16_t *)(stack_record_8 + 2)));
  restore_priority_mask_preserving_interrupt_enable_d1dc6(uVar2);
  return uVar2;
}

void step_c36a_enable_envelope_and_bound_c0cc_c6fde(void)

{
  bool bVar1;
  short sVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  
  if ((DAT_febec0d0 == '\0') || (DAT_febeac0a == 'Z')) {
    DAT_febec398 = '\x01';
  }
  else if (DAT_febec398 == '\0') {
    iVar3 = 0x400 - ((int)(int16_t)DAT_febec36a);
    sVar2 = DAT_000b00f4;
    goto LAB_000c7020;
  }
  iVar3 = -(int)((int)(int16_t)DAT_febec36a);
  sVar2 = DAT_000b00f6;
LAB_000c7020:
  DAT_febec310 = iVar3 * sVar2 + DAT_febec310;
  DAT_febec36a = (short)((int)DAT_febec310 / 0x4000);
  iVar3 = (int)((int)(int16_t)DAT_febec36a);
  if (DAT_febec398 == '\x01') {
    iVar4 = (int)DAT_000b00d6;
    iVar5 = iVar3 - iVar4;
    bVar1 = iVar3 < 0 != iVar4 < 0 && iVar4 < 0 == iVar5 < 0;
    DAT_febec398 = iVar5 < 0 == bVar1 && iVar3 != iVar4;
    if (iVar5 < 0 != bVar1 || iVar3 == iVar4) {
      DAT_febec36a = 0;
      DAT_febec310 = 0;
    }
  }
  else {
    iVar5 = (int)DAT_000b00d4;
    if (iVar3 - iVar5 < 0 == (iVar3 < 0 != iVar5 < 0 && iVar5 < 0 == iVar3 - iVar5 < 0)) {
      DAT_febec36a = 0x400;
      DAT_febec310 = 0x1000000;
    }
  }
  iVar3 = ((int)(int16_t)DAT_febec36a * (int)DAT_000b00f0) / 0x400;
  DAT_febec368 = (short)iVar3;
  iVar4 = (int)DAT_febec0cc;
  if (iVar4 <= iVar3) {
    iVar5 = -iVar3;
    if (iVar4 <= iVar5) {
      iVar3 = iVar5;
    }
    else {
      iVar3 = iVar4;
    }
  }
  DAT_febec36c = (short)iVar3;
  return;
}
