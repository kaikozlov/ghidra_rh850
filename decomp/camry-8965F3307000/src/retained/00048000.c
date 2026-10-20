#include "common.h"

void filter_scaled_pair_820c_820e_48026(void)

{
  uint8_t stack_record_20[32];
  uint uVar1;
  uint32_t puVar2;
  uint uVar3;
  struct {
    undefined2 previous;
    undefined2 sample;
    undefined4 accumulator;
  } staged;
  
  puVar2 = 0xfebeb800u;
  uVar3 = (uint)DAT_0002fbe2;
  staged.previous = DAT_febe7da6;
  staged.accumulator = DAT_febe7db8;
  (*((uint16_t *)(stack_record_20 + 0))) = (undefined2)(DAT_febe820c * uVar3 >> 0x10);
  uVar1 = (uint)DAT_0002fbd8;
  staged.sample = (*((uint16_t *)(stack_record_20 + 0)));
  update_u16_q16_delta_accumulator_6a678(&staged.previous,uVar1 * 10,((uint16_t *)(stack_record_20)),((uint32_t *)((stack_record_20 + 4))));
  staged.previous = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x3a58))));
  staged.accumulator = (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + -0x3a44))));
  (*((uint16_t *)(stack_record_20 + 2))) = (undefined2)((*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x35f2)))) * uVar3 >> 0x10);
  staged.sample = (*((uint16_t *)(stack_record_20 + 2)));
  update_u16_q16_delta_accumulator_6a678(&staged.previous,uVar1 * 10,((uint16_t *)((stack_record_20 + 2))),((uint32_t *)((stack_record_20 + 8))));
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + -0x3a48)))) = (*((uint32_t *)(stack_record_20 + 4)));
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + -0x3a44)))) = (*((uint32_t *)(stack_record_20 + 8)));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x3a5a)))) = (*((uint16_t *)(stack_record_20 + 0)));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x3a58)))) = (*((uint16_t *)(stack_record_20 + 2)));
  return;
}

void filter_scaled_pair_8220_8222_480b4(void)

{
  uint8_t stack_record_20[32];
  uint uVar1;
  uint32_t puVar2;
  struct {
    undefined2 previous;
    undefined2 sample;
    undefined4 accumulator;
  } staged;
  
  puVar2 = 0xfebeb800u;
  staged.previous = DAT_febe7daa;
  staged.accumulator = DAT_febe7dc0;
  (*((uint16_t *)(stack_record_20 + 0))) = (undefined2)((uint)DAT_febe8220 * (uint)DAT_0002fbe4 >> 0x10);
  uVar1 = (uint)DAT_0002fbda;
  staged.sample = (*((uint16_t *)(stack_record_20 + 0)));
  update_u16_q16_delta_accumulator_6a678(&staged.previous,uVar1 * 10,((uint16_t *)(stack_record_20)),((uint32_t *)((stack_record_20 + 4))));
  staged.previous = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x3a54))));
  staged.accumulator = (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + -0x3a3c))));
  (*((uint16_t *)(stack_record_20 + 2))) = (undefined2)((uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x35de)))) * (uint)DAT_0002fbe6 >> 0x10);
  staged.sample = (*((uint16_t *)(stack_record_20 + 2)));
  update_u16_q16_delta_accumulator_6a678(&staged.previous,uVar1 * 10,((uint16_t *)((stack_record_20 + 2))),((uint32_t *)((stack_record_20 + 8))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x3a56)))) = (*((uint16_t *)(stack_record_20 + 0)));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x3a54)))) = (*((uint16_t *)(stack_record_20 + 2)));
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + -0x3a40)))) = (*((uint32_t *)(stack_record_20 + 4)));
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + -0x3a3c)))) = (*((uint32_t *)(stack_record_20 + 8)));
  return;
}

void filter_scaled_sample_8210_48146(void)

{
  uint8_t stack_record_12[18];
  uint32_t puVar1;
  struct {
    undefined2 previous;
    undefined2 sample;
    undefined4 accumulator;
  } staged;
  
  puVar1 = 0xfebeb800u;
  (*((uint16_t *)(stack_record_12 + 0))) = (undefined2)((uint)DAT_febe8210 * (uint)DAT_0002fbe8 >> 0x10);
  staged.previous = DAT_febe7db0;
  staged.accumulator = DAT_febe7dc8;
  staged.sample = (*((uint16_t *)(stack_record_12 + 0)));
  update_u16_q16_delta_accumulator_6a678(&staged.previous,(uint)DAT_0002fbdc * 10,((uint16_t *)(stack_record_12)),((uint32_t *)((stack_record_12 + 2))));
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x3a38)))) = (*((uint32_t *)(stack_record_12 + 2)));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x3a50)))) = (*((uint16_t *)(stack_record_12 + 0)));
  return;
}

void scale_unsigned_pair_8226_8228_4819a(void)

{
  DAT_febe7db4 = (short)((uint)DAT_febe8226 * (uint)DAT_0002fbea >> 0x10);
  DAT_febe7db6 = (short)((uint)DAT_febe8228 * (uint)DAT_0002fbea >> 0x10);
  return;
}

void select_scaled_pair_sample_by_mask_and_threshold_481c0(void)

{
  if ((DAT_febe71ec & 1) == 0) {
    if ((DAT_febe71ec & 2) != 0) {
      DAT_febe7dae = DAT_febe7da6;
      return;
    }
  }
  else if ((DAT_febe71ec & 2) == 0) {
    DAT_febe7dae = DAT_febe7da8;
    return;
  }
  if (DAT_febe7da8 < DAT_febe7da6) {
    if (DAT_febe7da6 <= DAT_0002fbde) {
      DAT_febe7dae = DAT_febe7da6;
      return;
    }
  }
  else if (DAT_0002fbde < DAT_febe7da8) {
    DAT_febe7dae = DAT_febe7da6;
    return;
  }
  DAT_febe7dae = DAT_febe7da8;
  return;
}

void select_scaled_sample_and_mark_valid_48200(void)

{
  if (DAT_febe7dae < DAT_febe7db0) {
    if (DAT_febe7db0 <= DAT_0002fbe0) {
      DAT_febe7da4 = 0x5a;
      DAT_febe7db2 = DAT_febe7db0;
      return;
    }
  }
  else if (DAT_0002fbde < DAT_febe7dae) {
    DAT_febe7da4 = 0x5a;
    DAT_febe7db2 = DAT_febe7db0;
    return;
  }
  DAT_febe7db2 = DAT_febe7dae;
  DAT_febe7da4 = 0x5a;
  return;
}

void update_scaled_sample_filters_and_selection_48230(void)

{
  ushort uVar1;
  
  uVar1 = DAT_febeeba6;
  filter_scaled_pair_820c_820e_48026();
  filter_scaled_pair_8220_8222_480b4();
  filter_scaled_sample_8210_48146();
  if (uVar1 < 0x300) {
    scale_unsigned_pair_8226_8228_4819a();
  }
  select_scaled_pair_sample_by_mask_and_threshold_481c0();
  select_scaled_sample_and_mark_valid_48200();
  return;
}

void return_only_stub_4825a(void)

{
  return;
}

uint initialize_record5_pair_and_sample_accumulators_4825c(void)

{
  uint8_t stack_record_c[12];
  uint32_t puVar1;
  uint uVar2;
  undefined1 uVar3;
  
  puVar1 = 0xfebeb800u;
  (*((uint32_t *)(stack_record_c + 0))) = DAT_000212c8;
  (*((uint32_t *)(stack_record_c + 4))) = DAT_000212cc;
  uVar2 = nvm_get_record(5, camry_host_addr(stack_record_c));
  if (uVar2 == 0x10) {
    if (((short)(*((uint32_t *)(stack_record_c + 0))) == 32000) || ((*((uint16_t *)((uint8_t *)stack_record_c + 2u))) == 32000)) {
      uVar3 = 0x5a;
      goto LAB_000482a4;
    }
  }
  else {
    (*((uint16_t *)((uint8_t *)stack_record_c + 0u))) = 32000;
    (*((uint16_t *)((uint8_t *)stack_record_c + 2u))) = (short)(*((uint32_t *)(stack_record_c + 0)));
  }
  uVar3 = 0;
LAB_000482a4:
  (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x3a2e)))) = (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x536e))));
  (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x3a2c)))) = (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x5368))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3a33))))) = uVar3;
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x3a30)))) = (short)(*((uint32_t *)(stack_record_c + 0)));
  (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x3a24)))) = (uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x536e)))) << 0x10;
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x3a28)))) = (*((uint16_t *)((uint8_t *)stack_record_c + 2u)));
  (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x3a20)))) = (uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x5368)))) << 0x10;
  return uVar2;
}

void filter_thermistor_channel0(void)

{
  uint8_t stack_record_16[22];
  uint32_t puVar1;
  struct {
    ushort previous;
    ushort sample;
    uint accumulator;
  } staged;
  
  puVar1 = 0xfebeb800u;
  staged.sample = DAT_febe6492;
  (*((uint32_t *)(stack_record_16 + 2))) = DAT_febe7ddc;
  staged.accumulator = DAT_febe7ddc;
  (*((uint16_t *)(stack_record_16 + 0))) = DAT_febe7dd2;
  staged.previous = DAT_febe7dd2;
  if (DAT_febe7ddc >> 0x10 != (uint)DAT_febe7dd2) {
    staged.previous = DAT_febe6492;
    staged.accumulator = (uint)DAT_febe6492 << 0x10;
  }
  update_u16_q16_delta_accumulator_6a678(&staged.previous,DAT_00031804,((uint16_t *)(stack_record_16)),((uint32_t *)((stack_record_16 + 2))));
  interpolate_u16_axis_s16_values_702b0(((undefined *)camry_host_ptr(0x31808u)),(*((uint16_t *)(stack_record_16 + 0))),((undefined *)camry_host_ptr(0xfebe7dceu)));
  (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x3a2e)))) = (*((uint16_t *)(stack_record_16 + 0)));
  (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x3a24)))) = (*((uint32_t *)(stack_record_16 + 2)));
  return;
}

void filter_thermistor_channel1(void)

{
  uint8_t stack_record_16[22];
  uint32_t puVar1;
  struct {
    ushort previous;
    ushort sample;
    uint accumulator;
  } staged;
  
  puVar1 = 0xfebeb800u;
  staged.sample = DAT_febe6498;
  (*((uint32_t *)(stack_record_16 + 2))) = DAT_febe7de0;
  staged.accumulator = DAT_febe7de0;
  (*((uint16_t *)(stack_record_16 + 0))) = DAT_febe7dd4;
  staged.previous = DAT_febe7dd4;
  if (DAT_febe7de0 >> 0x10 != (uint)DAT_febe7dd4) {
    staged.previous = DAT_febe6498;
    staged.accumulator = (uint)DAT_febe6498 << 0x10;
  }
  update_u16_q16_delta_accumulator_6a678(&staged.previous,DAT_00031804,((uint16_t *)(stack_record_16)),((uint32_t *)((stack_record_16 + 2))));
  interpolate_u16_axis_s16_values_702b0(((undefined *)camry_host_ptr(0x31808u)),(*((uint16_t *)(stack_record_16 + 0))),((undefined *)camry_host_ptr(0xfebe7dd6u)));
  (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x3a2c)))) = (*((uint16_t *)(stack_record_16 + 0)));
  (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x3a20)))) = (*((uint32_t *)(stack_record_16 + 2)));
  return;
}

void update_thermistor_channels(void)

{
  short sVar1;
  int iVar2;
  uint32_t puVar3;
  int iVar4;
  
  puVar3 = 0xfebeb800u;
  filter_thermistor_channel0();
  filter_thermistor_channel1();
  iVar2 = (int)(*((short *)camry_host_ptr((uint32_t)(puVar3 + -0x3a2a))));
  sVar1 = (*((short *)camry_host_ptr((uint32_t)(puVar3 + -0x3a32))));
  iVar4 = (int)sVar1;
  if (iVar2 - iVar4 < 0 == (iVar2 < 0 != iVar4 < 0 && iVar4 < 0 == iVar2 - iVar4 < 0) &&
      iVar2 != iVar4) {
    sVar1 = (*((short *)camry_host_ptr((uint32_t)(puVar3 + -0x3a2a))));
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + -0x3a26)))) = sVar1;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3a34))))) = 0x5a;
  return;
}

void return_only_stub_483b4(void)

{
  return;
}

void clear_record5_write_state_483b6(void)

{
  DAT_febe7de4 = 0;
  return;
}

void poll_record5_write_state_483bc(void)

{
  uint32_t puVar1;
  uint uVar2;
  char cVar3;
  
  cVar3 = DAT_febe7de4;
  puVar1 = 0xfebeb800u;
  if (DAT_febe7de4 == '\x01') {
    puVar1 = 0xfebeb800u;
    uVar2 = nvm_get_record_status(5);
    if (uVar2 == 0x10) {
      cVar3 = -1;
    }
    else if ((uVar2 & 0xf0) == 0x30) {
      cVar3 = -2;
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3a1c))))) = cVar3;
  return;
}

uint write_record5_pair_sentinels_4841e(void)

{
  uint8_t stack_record_c[12];
  
  (*((uint16_t *)(stack_record_c + 0))) = 32000;
  (*((uint16_t *)(stack_record_c + 2))) = 32000;
  (*((uint32_t *)(stack_record_c + 4))) = 0;
  return nvm_set_record(5,(uint *)stack_record_c);
}

void return_only_stub_4843a(void)

{
  return;
}

void fill_constant_block_4843c(void)

{
  DAT_febe7dea = 0;
  DAT_febe7dfc = 0;
  DAT_febe7e00 = 0;
  DAT_febe7e04 = 0;
  DAT_febe7e08 = 0;
  DAT_febe7dec = 0;
  DAT_febe7dee = 0;
  DAT_febe7df0 = 0;
  DAT_febe7df2 = 0;
  DAT_febe7df4 = 0;
  DAT_febe7df6 = 0;
  DAT_febe7df8 = 0;
  DAT_febe7dfa = 0;
  DAT_febe7de8 = 0;
  return;
}

short select_torque_pair_differences(short first_pair,short second_pair)

{
  short sVar1;
  
  DAT_febe7de8 = DAT_febe7cb7;
  if ((DAT_febe71ec & 0x60) != 0) {
    if ((DAT_febe71ec >> 5 & 1) == 0) {
      DAT_febe7de8 = 2;
    }
    else {
      DAT_febe7de8 = 1;
    }
  }
  if (1 < DAT_febe7de8) {
    return first_pair;
  }
  if (DAT_febe7de8 == 0) {
    sVar1 = (short)(((int)first_pair - (int)second_pair) / 2);
  }
  else {
    sVar1 = -second_pair;
  }
  return sVar1;
}

short bound_torque_tracking_step(short value,short previous)

{
  int iVar1;
  int iVar2;
  int iVar3;
  short sVar4;
  
  iVar2 = (int)value;
  iVar3 = (int)previous;
  if (iVar3 + -0x1400 < 0 == (iVar3 < 0 && -1 < iVar3 + -0x1400)) {
    iVar3 = 0x1400;
  }
  if (iVar3 + 0x1400 < 0 != (-1 < iVar3 && iVar3 + 0x1400 < 0)) {
    iVar3 = -0x1400;
  }
  iVar1 = iVar3 - (uint)DAT_00030e50;
  iVar3 = (uint)DAT_00030e50 + iVar3;
  if (iVar2 - iVar3 < 0 != (iVar2 < 0 != iVar3 < 0 && iVar3 < 0 == iVar2 - iVar3 < 0)) {
    iVar3 = iVar2;
  }
  if (iVar3 - iVar1 < 0 == (iVar3 < 0 != iVar1 < 0 && iVar1 < 0 == iVar3 - iVar1 < 0)) {
    sVar4 = (short)iVar3;
  }
  else {
    sVar4 = (short)iVar1;
  }
  return sVar4;
}

short clamp_decoded_torque(short value)

{
  int iVar1;
  int iVar2;
  short sVar3;
  int iVar4;
  
  iVar2 = (int)value;
  iVar1 = (int)DAT_00030e52;
  sVar3 = -DAT_00030e52;
  iVar4 = (int)sVar3;
  if (iVar2 - iVar1 < 0 != (iVar2 < 0 != iVar1 < 0 && iVar1 < 0 == iVar2 - iVar1 < 0)) {
    iVar1 = iVar2;
  }
  if (iVar1 - iVar4 < 0 == (iVar1 < 0 != iVar4 < 0 && iVar4 < 0 == iVar1 - iVar4 < 0)) {
    sVar3 = (short)iVar1;
  }
  return sVar3;
}

void decode_torque_sensor_channels(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint32_t puVar4;
  short value;
  short sVar5;
  int iVar6;
  int iVar7;
  
  sVar5 = ((int)(int16_t)DAT_febe7dfa);
  puVar4 = 0xfebeb800u;
  if (DAT_febe8a1c == 'Z') {
    DAT_febe7dfc = (uint)DAT_febe81e6 - (uint)DAT_febe6ad2;
    DAT_febe7e00 = (uint)DAT_febe81e8 - (uint)DAT_febe6ad4;
    DAT_febe7e04 = (uint)DAT_febe81ea - (uint)DAT_febe6ad6;
    DAT_febe7e08 = (uint)DAT_febe81ec - (uint)DAT_febe6ad8;
    iVar7 = (int)((DAT_febe7dfc * DAT_00030e54)) / (int)0x800;
    iVar6 = (int)((DAT_febe7e00 * DAT_00030e54)) / (int)0x800;
    iVar3 = (int)((DAT_febe7e04 * DAT_00030e56)) / (int)0x800;
    iVar1 = (int)((DAT_febe7e08 * DAT_00030e56)) / (int)0x800;
    if (iVar7 + 0x7fff < 0 == (-1 < iVar7 && iVar7 + 0x7fff < 0) && iVar7 != -0x7fff) {
      if (iVar7 + -0x7fff < 0 == (iVar7 < 0 && -1 < iVar7 + -0x7fff) && iVar7 != 0x7fff) {
        iVar7 = 0x7fff;
      }
      else {
        iVar7 = (int)(short)iVar7;
      }
    }
    else {
      iVar7 = -0x7fff;
    }
    if (iVar6 + 0x7fff < 0 == (-1 < iVar6 && iVar6 + 0x7fff < 0) && iVar6 != -0x7fff) {
      if (iVar6 + -0x7fff < 0 == (iVar6 < 0 && -1 < iVar6 + -0x7fff) && iVar6 != 0x7fff) {
        iVar6 = 0x7fff;
      }
      else {
        iVar6 = (int)(short)iVar6;
      }
    }
    else {
      iVar6 = -0x7fff;
    }
    if (iVar3 + 0x7fff < 0 == (-1 < iVar3 && iVar3 + 0x7fff < 0) && iVar3 != -0x7fff) {
      iVar2 = (int)(short)iVar3;
      if (iVar3 + -0x7fff < 0 == (iVar3 < 0 && -1 < iVar3 + -0x7fff) && iVar3 != 0x7fff) {
        iVar2 = 0x7fff;
      }
    }
    else {
      iVar2 = -0x7fff;
    }
    if (iVar1 + 0x7fff < 0 == (-1 < iVar1 && iVar1 + 0x7fff < 0) && iVar1 != -0x7fff) {
      iVar3 = (int)(short)iVar1;
      if (iVar1 + -0x7fff < 0 == (iVar1 < 0 && -1 < iVar1 + -0x7fff) && iVar1 != 0x7fff) {
        iVar3 = 0x7fff;
      }
    }
    else {
      iVar3 = -0x7fff;
    }
    DAT_febe7dec = (undefined2)(iVar7 / 2);
    DAT_febe7dee = (undefined2)(iVar6 / 2);
    DAT_febe7df0 = (undefined2)(iVar2 / 2);
    iVar7 = iVar7 - iVar6;
    DAT_febe7df2 = (undefined2)(iVar3 / 2);
    if (iVar7 + 0x7fff < 0 == (-1 < iVar7 && iVar7 + 0x7fff < 0) && iVar7 != -0x7fff) {
      if (iVar7 + -0x7fff < 0 == (iVar7 < 0 && -1 < iVar7 + -0x7fff) && iVar7 != 0x7fff) {
        iVar6 = 0x7fff;
      }
      else {
        iVar6 = -0x8000;
        if (iVar7 + 0x8000 < 0 == (-1 < iVar7 && iVar7 + 0x8000 < 0)) {
          iVar6 = (int)(short)iVar7;
        }
      }
    }
    else {
      iVar6 = -0x7fff;
    }
    iVar2 = iVar2 - iVar3;
    if (iVar2 + 0x7fff < 0 == (-1 < iVar2 && iVar2 + 0x7fff < 0) && iVar2 != -0x7fff) {
      if (iVar2 + -0x7fff < 0 == (iVar2 < 0 && -1 < iVar2 + -0x7fff) && iVar2 != 0x7fff) {
        iVar7 = 0x7fff;
      }
      else {
        iVar7 = -0x8000;
        if (iVar2 + 0x8000 < 0 == (-1 < iVar2 && iVar2 + 0x8000 < 0)) {
          iVar7 = (int)(short)iVar2;
        }
      }
    }
    else {
      iVar7 = -0x7fff;
    }
    DAT_febe7df4 = (undefined2)(iVar6 / 2);
    DAT_febe7df6 = (undefined2)(iVar7 / 2);
    value = select_torque_pair_differences((short)iVar6,(short)iVar7);
    (*((short *)camry_host_ptr((uint32_t)(puVar4 + -0x3a08)))) = value;
    sVar5 = bound_torque_tracking_step(value,sVar5);
    (*((short *)camry_host_ptr((uint32_t)(puVar4 + -0x3a06)))) = sVar5;
    sVar5 = clamp_decoded_torque(sVar5);
    (*((short *)camry_host_ptr((uint32_t)(puVar4 + -0x3a16)))) = sVar5;
  }
  return;
}

void return_only_stub_4867c(void)

{
  return;
}

void clear_halfword_7e0c_4867e(void)

{
  DAT_febe7e0c = 0;
  return;
}

void publish_selected_torque_feedback(void)

{
  if ((DAT_febe8a1c == 'Z') && (DAT_febe7e0c = ((int)(int16_t)DAT_febe6870), DAT_febe686c != 'Z')) {
    DAT_febe7e0c = ((int)(int16_t)DAT_febe7dea);
  }
  return;
}

void return_only_stub_486a8(void)

{
  return;
}

void fill_constant_block_486aa(void)

{
  DAT_febe7e2e = 0x8000;
  DAT_febe7e30 = 0x8000;
  DAT_febe7e32 = 0x8000;
  DAT_febe7e34 = 0x8000;
  DAT_febe7e36 = 0x8000;
  DAT_febe7e38 = 0x8000;
  DAT_febe7e10 = 0x8000;
  DAT_febe7e12 = 0x8000;
  DAT_febe7e14 = 0x8000;
  DAT_febe7e16 = 0x8000;
  DAT_febe7e18 = 0x8000;
  DAT_febe7e1a = 0x8000;
  return;
}

void condition_measured_phase_currents(void)

{
  ushort uVar1;
  short sVar2;
  uint uVar3;
  int iVar4;
  uint uVar5;
  int iVar6;
  int iVar7;
  
  iVar4 = (int)DAT_00031e54;
  iVar6 = (int)((int)(int16_t)DAT_febe6d7c);
  iVar7 = -iVar4;
  if ((iVar6 + iVar4 < 0 == (iVar6 < 0 != iVar7 < 0 && iVar7 < 0 == iVar6 + iVar4 < 0) &&
       iVar6 != iVar7) &&
     (iVar6 - iVar4 < 0 != (iVar6 < 0 != iVar4 < 0 && iVar4 < 0 == iVar6 - iVar4 < 0))) {
    DAT_febe7e2c = 'Z';
  }
  else {
    DAT_febe7e2c = '\0';
  }
  if (DAT_febe7e2e != DAT_febe7e10) {
    DAT_febe7e2e = 0x8000;
  }
  if (DAT_febe7e30 != DAT_febe7e12) {
    DAT_febe7e30 = 0x8000;
  }
  if (DAT_febe7e32 != DAT_febe7e14) {
    DAT_febe7e32 = 0x8000;
  }
  DAT_febe7e20 = '\0';
  uVar1 = 0x8000 - DAT_00031e56;
  if (uVar1 <= DAT_febe8b60) {
    DAT_febe7e20 = 'Z';
  }
  DAT_febe7e21 = '\0';
  if (uVar1 <= DAT_febe8b62) {
    DAT_febe7e21 = 'Z';
  }
  DAT_febe7e22 = '\0';
  if (uVar1 <= DAT_febe8b64) {
    DAT_febe7e22 = 'Z';
  }
  if (((DAT_febe7e20 == 'Z') && (DAT_febe7e21 == 'Z')) && (DAT_febe7e22 == 'Z')) {
    DAT_febe7e1e = 'Z';
  }
  else {
    DAT_febe7e1e = '\0';
  }
  if (((DAT_00031e56 < DAT_febe8b60) || (DAT_00031e56 < DAT_febe8b62)) ||
     (DAT_00031e56 < DAT_febe8b64)) {
    DAT_febe7e1c = '\0';
  }
  else {
    DAT_febe7e1c = 'Z';
  }
  if ((DAT_febe7e2c == 'Z') && (DAT_febe7e1e == 'Z')) {
    DAT_febe7e10 = (ushort)((uint)DAT_febe8238 + (uint)DAT_febe7e2e >> 1);
    DAT_febe7e12 = (ushort)((uint)DAT_febe823a + (uint)DAT_febe7e30 >> 1);
    DAT_febe7e14 = (ushort)((uint)DAT_febe823c + (uint)DAT_febe7e32 >> 1);
    DAT_febe7e2e = DAT_febe7e10;
    DAT_febe7e30 = DAT_febe7e12;
    DAT_febe7e32 = DAT_febe7e14;
  }
  DAT_febe7e54 = ((uint)DAT_febe822c - (uint)DAT_febe7e2e) -
                 (int)monitor_current_active_calibration.coefficients.bias[0];
  sVar2 = monitor_current_active_calibration.coefficients.negative_residual_gain[0];
  if (-1 < (int)(((uint)DAT_febe822c - (uint)DAT_febe7e2e) -
                (int)monitor_current_active_calibration.coefficients.bias[0])) {
    sVar2 = monitor_current_active_calibration.coefficients.nonnegative_residual_gain[0];
  }
  iVar7 = (int)sVar2;
  uVar5 = 0x7fffffff;
  if ((((int)(int32_t)DAT_febe7e54) == 0) || (iVar7 == 0)) {
    uVar3 = 0;
  }
  else {
    if (((int)(int32_t)DAT_febe7e54) < 0) {
      if (-1 < iVar7) goto LAB_0004882a;
    }
    else if (iVar7 < 0) {
LAB_0004882a:
      iVar4 = (int)((ulonglong)((longlong)iVar7 * (longlong)((int)(int32_t)DAT_febe7e54)) >> 0x20) + 1;
      if ((iVar4 < 0 != (-1 < (longlong)iVar7 * (longlong)((int)(int32_t)DAT_febe7e54) && iVar4 < 0)) ||
         (uVar3 = ((int)(int32_t)DAT_febe7e54) * iVar7, uVar3 < 0x80000001)) {
        uVar3 = 0x80000001;
      }
      goto LAB_00048844;
    }
    if ((-1 < (longlong)iVar7 * (longlong)((int)(int32_t)DAT_febe7e54) &&
         (int)((ulonglong)((longlong)iVar7 * (longlong)((int)(int32_t)DAT_febe7e54)) >> 0x20) != 0) ||
       (uVar3 = ((int)(int32_t)(int)DAT_febe7e54) * iVar7, 0x7fffffff < (uint)(((int)(int32_t)(int)DAT_febe7e54) * iVar7))) {
      uVar3 = uVar5;
    }
  }
LAB_00048844:
  iVar7 = (int)uVar3 / 0x4000;
  if (iVar7 + 0x7fff < 0 == (-1 < iVar7 && iVar7 + 0x7fff < 0) && iVar7 != -0x7fff) {
    if (iVar7 + -0x7fff < 0 == (iVar7 < 0 && -1 < iVar7 + -0x7fff) && iVar7 != 0x7fff) {
      iVar7 = 0x7fff;
    }
    DAT_febe7e46 = (short)iVar7;
  }
  else {
    DAT_febe7e46 = -0x7fff;
  }
  DAT_febe7e3a = ((int)(int16_t)DAT_febe7e46);
  DAT_febe7e58 = ((uint)DAT_febe822e - (uint)DAT_febe7e30) -
                 (int)monitor_current_active_calibration.coefficients.bias[1];
  sVar2 = monitor_current_active_calibration.coefficients.negative_residual_gain[1];
  if (-1 < (int)(((uint)DAT_febe822e - (uint)DAT_febe7e30) -
                (int)monitor_current_active_calibration.coefficients.bias[1])) {
    sVar2 = monitor_current_active_calibration.coefficients.nonnegative_residual_gain[1];
  }
  iVar7 = (int)sVar2;
  if ((((int)(int32_t)DAT_febe7e58) == 0) || (iVar7 == 0)) {
    uVar3 = 0;
  }
  else {
    if (((int)(int32_t)DAT_febe7e58) < 0) {
      if (-1 < iVar7) goto LAB_000488b4;
    }
    else if (iVar7 < 0) {
LAB_000488b4:
      iVar4 = (int)((ulonglong)((longlong)iVar7 * (longlong)((int)(int32_t)DAT_febe7e58)) >> 0x20) + 1;
      if ((iVar4 < 0 != (-1 < (longlong)iVar7 * (longlong)((int)(int32_t)DAT_febe7e58) && iVar4 < 0)) ||
         (uVar3 = ((int)(int32_t)DAT_febe7e58) * iVar7, uVar3 < 0x80000001)) {
        uVar3 = 0x80000001;
      }
      goto LAB_000488ce;
    }
    if ((-1 < (longlong)iVar7 * (longlong)((int)(int32_t)DAT_febe7e58) &&
         (int)((ulonglong)((longlong)iVar7 * (longlong)((int)(int32_t)DAT_febe7e58)) >> 0x20) != 0) ||
       (uVar3 = ((int)(int32_t)(int)DAT_febe7e58) * iVar7, 0x7fffffff < (uint)(((int)(int32_t)(int)DAT_febe7e58) * iVar7))) {
      uVar3 = uVar5;
    }
  }
LAB_000488ce:
  iVar7 = (int)uVar3 / 0x4000;
  if (iVar7 + 0x7fff < 0 == (-1 < iVar7 && iVar7 + 0x7fff < 0) && iVar7 != -0x7fff) {
    if (iVar7 + -0x7fff < 0 == (iVar7 < 0 && -1 < iVar7 + -0x7fff) && iVar7 != 0x7fff) {
      iVar7 = 0x7fff;
    }
    DAT_febe7e48 = (short)iVar7;
  }
  else {
    DAT_febe7e48 = -0x7fff;
  }
  DAT_febe7e3c = ((int)(int16_t)DAT_febe7e48);
  DAT_febe7e5c = ((uint)DAT_febe8230 - (uint)DAT_febe7e32) -
                 (int)monitor_current_active_calibration.coefficients.bias[2];
  sVar2 = monitor_current_active_calibration.coefficients.negative_residual_gain[2];
  if (-1 < (int)(((uint)DAT_febe8230 - (uint)DAT_febe7e32) -
                (int)monitor_current_active_calibration.coefficients.bias[2])) {
    sVar2 = monitor_current_active_calibration.coefficients.nonnegative_residual_gain[2];
  }
  iVar7 = (int)sVar2;
  if ((((int)(int32_t)DAT_febe7e5c) == 0) || (iVar7 == 0)) {
    uVar3 = 0;
  }
  else {
    if (((int)(int32_t)DAT_febe7e5c) < 0) {
      if (-1 < iVar7) goto LAB_0004893e;
    }
    else if (iVar7 < 0) {
LAB_0004893e:
      iVar4 = (int)((ulonglong)((longlong)iVar7 * (longlong)((int)(int32_t)DAT_febe7e5c)) >> 0x20) + 1;
      if ((iVar4 < 0 != (-1 < (longlong)iVar7 * (longlong)((int)(int32_t)DAT_febe7e5c) && iVar4 < 0)) ||
         (uVar3 = ((int)(int32_t)DAT_febe7e5c) * iVar7, uVar3 < 0x80000001)) {
        uVar3 = 0x80000001;
      }
      goto LAB_00048958;
    }
    if ((-1 < (longlong)iVar7 * (longlong)((int)(int32_t)DAT_febe7e5c) &&
         (int)((ulonglong)((longlong)iVar7 * (longlong)((int)(int32_t)DAT_febe7e5c)) >> 0x20) != 0) ||
       (uVar3 = ((int)(int32_t)(int)DAT_febe7e5c) * iVar7, 0x7fffffff < (uint)(((int)(int32_t)(int)DAT_febe7e5c) * iVar7))) {
      uVar3 = uVar5;
    }
  }
LAB_00048958:
  iVar7 = (int)uVar3 / 0x4000;
  if (iVar7 + 0x7fff < 0 == (-1 < iVar7 && iVar7 + 0x7fff < 0) && iVar7 != -0x7fff) {
    if (iVar7 + -0x7fff < 0 == (iVar7 < 0 && -1 < iVar7 + -0x7fff) && iVar7 != 0x7fff) {
      iVar7 = 0x7fff;
    }
    DAT_febe7e4a = (short)iVar7;
  }
  else {
    DAT_febe7e4a = -0x7fff;
  }
  DAT_febe7e26 = 0;
  DAT_febe7e3e = ((int)(int16_t)DAT_febe7e4a);
  DAT_febe7e27 = 0;
  DAT_febe7e28 = 0;
  if (DAT_febe7e1c == '\0') {
    if ((DAT_febe8b62 < DAT_febe8b60) && (DAT_febe8b64 < DAT_febe8b60)) {
      iVar7 = (int)((int)(int16_t)DAT_febe7e4a) + (int)((int)(int16_t)DAT_febe7e48);
      iVar4 = -iVar7;
      if (iVar4 + 0x7fff < 0 == (-1 < iVar4 && iVar4 + 0x7fff < 0) && iVar7 != 0x7fff) {
        if (iVar4 + -0x7fff < 0 == (iVar4 < 0 && -1 < iVar4 + -0x7fff) && iVar7 != -0x7fff) {
          iVar4 = 0x7fff;
        }
      }
      else {
        iVar4 = -0x7fff;
      }
      DAT_febe7e46 = (short)iVar4;
      DAT_febe7e26 = 0x5a;
    }
    else if (DAT_febe8b64 < DAT_febe8b62) {
      iVar7 = (int)((int)(int16_t)DAT_febe7e46) + (int)((int)(int16_t)DAT_febe7e4a);
      iVar4 = -iVar7;
      if (iVar4 + 0x7fff < 0 == (-1 < iVar4 && iVar4 + 0x7fff < 0) && iVar7 != 0x7fff) {
        if (iVar4 + -0x7fff < 0 == (iVar4 < 0 && -1 < iVar4 + -0x7fff) && iVar7 != -0x7fff) {
          iVar4 = 0x7fff;
        }
      }
      else {
        iVar4 = -0x7fff;
      }
      DAT_febe7e48 = (short)iVar4;
      DAT_febe7e27 = 0x5a;
    }
    else {
      iVar7 = (int)((int)(int16_t)DAT_febe7e48) + (int)((int)(int16_t)DAT_febe7e46);
      iVar4 = -iVar7;
      if (iVar4 + 0x7fff < 0 == (-1 < iVar4 && iVar4 + 0x7fff < 0) && iVar7 != 0x7fff) {
        if (iVar4 + -0x7fff < 0 == (iVar4 < 0 && -1 < iVar4 + -0x7fff) && iVar7 != -0x7fff) {
          iVar4 = 0x7fff;
        }
      }
      else {
        iVar4 = -0x7fff;
      }
      DAT_febe7e4a = (short)iVar4;
      DAT_febe7e28 = 0x5a;
    }
  }
  if (DAT_febe7e34 != DAT_febe7e16) {
    DAT_febe7e34 = 0x8000;
  }
  if (DAT_febe7e36 != DAT_febe7e18) {
    DAT_febe7e36 = 0x8000;
  }
  if (DAT_febe7e38 != DAT_febe7e1a) {
    DAT_febe7e38 = 0x8000;
  }
  uVar1 = 0x8000 - DAT_00031e56;
  DAT_febe7e23 = '\0';
  if (uVar1 <= DAT_febe8b66) {
    DAT_febe7e23 = 'Z';
  }
  DAT_febe7e24 = '\0';
  if (uVar1 <= DAT_febe8b68) {
    DAT_febe7e24 = 'Z';
  }
  DAT_febe7e25 = '\0';
  if (uVar1 <= DAT_febe8b6a) {
    DAT_febe7e25 = 'Z';
  }
  if (((DAT_febe7e23 == 'Z') && (DAT_febe7e24 == 'Z')) && (DAT_febe7e25 == 'Z')) {
    DAT_febe7e1f = 'Z';
  }
  else {
    DAT_febe7e1f = '\0';
  }
  if (((DAT_00031e56 < DAT_febe8b66) || (DAT_00031e56 < DAT_febe8b68)) ||
     (DAT_00031e56 < DAT_febe8b6a)) {
    DAT_febe7e1d = '\0';
  }
  else {
    DAT_febe7e1d = 'Z';
  }
  if ((DAT_febe7e2c == 'Z') && (DAT_febe7e1f == 'Z')) {
    DAT_febe7e16 = (ushort)((uint)DAT_febe823e + (uint)DAT_febe7e34 >> 1);
    DAT_febe7e18 = (ushort)((uint)DAT_febe8240 + (uint)DAT_febe7e36 >> 1);
    DAT_febe7e1a = (ushort)((uint)DAT_febe8242 + (uint)DAT_febe7e38 >> 1);
    DAT_febe7e34 = DAT_febe7e16;
    DAT_febe7e36 = DAT_febe7e18;
    DAT_febe7e38 = DAT_febe7e1a;
  }
  DAT_febe7e60 = ((uint)DAT_febe8232 - (uint)DAT_febe7e34) -
                 (int)monitor_current_active_calibration.coefficients.bias[3];
  sVar2 = monitor_current_active_calibration.coefficients.negative_residual_gain[3];
  if (-1 < (int)(((uint)DAT_febe8232 - (uint)DAT_febe7e34) -
                (int)monitor_current_active_calibration.coefficients.bias[3])) {
    sVar2 = monitor_current_active_calibration.coefficients.nonnegative_residual_gain[3];
  }
  iVar7 = (int)sVar2;
  if ((((int)(int32_t)DAT_febe7e60) == 0) || (iVar7 == 0)) {
    uVar3 = 0;
  }
  else {
    if (((int)(int32_t)DAT_febe7e60) < 0) {
      if (-1 < iVar7) goto LAB_00048b40;
    }
    else if (iVar7 < 0) {
LAB_00048b40:
      iVar4 = (int)((ulonglong)((longlong)iVar7 * (longlong)((int)(int32_t)DAT_febe7e60)) >> 0x20) + 1;
      if ((iVar4 < 0 != (-1 < (longlong)iVar7 * (longlong)((int)(int32_t)DAT_febe7e60) && iVar4 < 0)) ||
         (uVar3 = ((int)(int32_t)DAT_febe7e60) * iVar7, uVar3 < 0x80000001)) {
        uVar3 = 0x80000001;
      }
      goto LAB_00048b5a;
    }
    if ((-1 < (longlong)iVar7 * (longlong)((int)(int32_t)DAT_febe7e60) &&
         (int)((ulonglong)((longlong)iVar7 * (longlong)((int)(int32_t)DAT_febe7e60)) >> 0x20) != 0) ||
       (uVar3 = ((int)(int32_t)(int)DAT_febe7e60) * iVar7, 0x7fffffff < (uint)(((int)(int32_t)(int)DAT_febe7e60) * iVar7))) {
      uVar3 = uVar5;
    }
  }
LAB_00048b5a:
  iVar7 = (int)uVar3 / 0x4000;
  if (iVar7 + 0x7fff < 0 == (-1 < iVar7 && iVar7 + 0x7fff < 0) && iVar7 != -0x7fff) {
    if (iVar7 + -0x7fff < 0 == (iVar7 < 0 && -1 < iVar7 + -0x7fff) && iVar7 != 0x7fff) {
      iVar7 = 0x7fff;
    }
    DAT_febe7e4c = (short)iVar7;
  }
  else {
    DAT_febe7e4c = -0x7fff;
  }
  DAT_febe7e40 = ((int)(int16_t)DAT_febe7e4c);
  DAT_febe7e64 = ((uint)DAT_febe8234 - (uint)DAT_febe7e36) -
                 (int)monitor_current_active_calibration.coefficients.bias[4];
  sVar2 = monitor_current_active_calibration.coefficients.negative_residual_gain[4];
  if (-1 < (int)(((uint)DAT_febe8234 - (uint)DAT_febe7e36) -
                (int)monitor_current_active_calibration.coefficients.bias[4])) {
    sVar2 = monitor_current_active_calibration.coefficients.nonnegative_residual_gain[4];
  }
  iVar7 = (int)sVar2;
  if ((((int)(int32_t)DAT_febe7e64) == 0) || (iVar7 == 0)) {
    uVar3 = 0;
  }
  else {
    if (((int)(int32_t)DAT_febe7e64) < 0) {
      if (-1 < iVar7) goto LAB_00048bca;
    }
    else if (iVar7 < 0) {
LAB_00048bca:
      iVar4 = (int)((ulonglong)((longlong)iVar7 * (longlong)((int)(int32_t)DAT_febe7e64)) >> 0x20) + 1;
      if ((iVar4 < 0 != (-1 < (longlong)iVar7 * (longlong)((int)(int32_t)DAT_febe7e64) && iVar4 < 0)) ||
         (uVar3 = ((int)(int32_t)DAT_febe7e64) * iVar7, uVar3 < 0x80000001)) {
        uVar3 = 0x80000001;
      }
      goto LAB_00048be4;
    }
    if ((-1 < (longlong)iVar7 * (longlong)((int)(int32_t)DAT_febe7e64) &&
         (int)((ulonglong)((longlong)iVar7 * (longlong)((int)(int32_t)DAT_febe7e64)) >> 0x20) != 0) ||
       (uVar3 = ((int)(int32_t)(int)DAT_febe7e64) * iVar7, 0x7fffffff < (uint)(((int)(int32_t)(int)DAT_febe7e64) * iVar7))) {
      uVar3 = uVar5;
    }
  }
LAB_00048be4:
  iVar7 = (int)uVar3 / 0x4000;
  if (iVar7 + 0x7fff < 0 == (-1 < iVar7 && iVar7 + 0x7fff < 0) && iVar7 != -0x7fff) {
    if (iVar7 + -0x7fff < 0 == (iVar7 < 0 && -1 < iVar7 + -0x7fff) && iVar7 != 0x7fff) {
      iVar7 = 0x7fff;
    }
    DAT_febe7e4e = (short)iVar7;
  }
  else {
    DAT_febe7e4e = -0x7fff;
  }
  DAT_febe7e42 = ((int)(int16_t)DAT_febe7e4e);
  DAT_febe7e68 = ((uint)DAT_febe8236 - (uint)DAT_febe7e38) -
                 (int)monitor_current_active_calibration.coefficients.bias[5];
  sVar2 = monitor_current_active_calibration.coefficients.negative_residual_gain[5];
  if (-1 < (int)(((uint)DAT_febe8236 - (uint)DAT_febe7e38) -
                (int)monitor_current_active_calibration.coefficients.bias[5])) {
    sVar2 = monitor_current_active_calibration.coefficients.nonnegative_residual_gain[5];
  }
  iVar7 = (int)sVar2;
  if ((((int)(int32_t)DAT_febe7e68) == 0) || (iVar7 == 0)) {
    uVar3 = 0;
    goto LAB_00048c70;
  }
  if (((int)(int32_t)DAT_febe7e68) < 0) {
    if (-1 < iVar7) goto LAB_00048c54;
  }
  else if (iVar7 < 0) {
LAB_00048c54:
    iVar4 = (int)((ulonglong)((longlong)iVar7 * (longlong)((int)(int32_t)DAT_febe7e68)) >> 0x20) + 1;
    if ((iVar4 < 0 != (-1 < (longlong)iVar7 * (longlong)((int)(int32_t)DAT_febe7e68) && iVar4 < 0)) ||
       (uVar3 = ((int)(int32_t)DAT_febe7e68) * iVar7, uVar3 < 0x80000001)) {
      uVar3 = 0x80000001;
    }
    goto LAB_00048c70;
  }
  if ((-1 < (longlong)iVar7 * (longlong)((int)(int32_t)DAT_febe7e68) &&
       (int)((ulonglong)((longlong)iVar7 * (longlong)((int)(int32_t)DAT_febe7e68)) >> 0x20) != 0) ||
     (uVar3 = ((int)(int32_t)(int)DAT_febe7e68) * iVar7, 0x7fffffff < (uint)(((int)(int32_t)(int)DAT_febe7e68) * iVar7))) {
    uVar3 = uVar5;
  }
LAB_00048c70:
  iVar7 = (int)uVar3 / 0x4000;
  if (iVar7 + 0x7fff < 0 == (-1 < iVar7 && iVar7 + 0x7fff < 0) && iVar7 != -0x7fff) {
    if (iVar7 + -0x7fff < 0 == (iVar7 < 0 && -1 < iVar7 + -0x7fff) && iVar7 != 0x7fff) {
      iVar7 = 0x7fff;
    }
    DAT_febe7e50 = (short)iVar7;
  }
  else {
    DAT_febe7e50 = -0x7fff;
  }
  DAT_febe7e29 = 0;
  DAT_febe7e44 = ((int)(int16_t)DAT_febe7e50);
  DAT_febe7e2a = 0;
  DAT_febe7e2b = 0;
  if (DAT_febe7e1d == '\0') {
    if ((DAT_febe8b68 < DAT_febe8b66) && (DAT_febe8b6a < DAT_febe8b66)) {
      iVar7 = (int)((int)(int16_t)DAT_febe7e50) + (int)((int)(int16_t)DAT_febe7e4e);
      iVar4 = -iVar7;
      if (iVar4 + 0x7fff < 0 == (-1 < iVar4 && iVar4 + 0x7fff < 0) && iVar7 != 0x7fff) {
        if (iVar4 + -0x7fff < 0 == (iVar4 < 0 && -1 < iVar4 + -0x7fff) && iVar7 != -0x7fff) {
          iVar4 = 0x7fff;
        }
      }
      else {
        iVar4 = -0x7fff;
      }
      DAT_febe7e4c = (short)iVar4;
      DAT_febe7e29 = 0x5a;
    }
    else if (DAT_febe8b6a < DAT_febe8b68) {
      iVar7 = (int)((int)(int16_t)DAT_febe7e4c) + (int)((int)(int16_t)DAT_febe7e50);
      iVar4 = -iVar7;
      if (iVar4 + 0x7fff < 0 == (-1 < iVar4 && iVar4 + 0x7fff < 0) && iVar7 != 0x7fff) {
        if (iVar4 + -0x7fff < 0 == (iVar4 < 0 && -1 < iVar4 + -0x7fff) && iVar7 != -0x7fff) {
          iVar4 = 0x7fff;
        }
      }
      else {
        iVar4 = -0x7fff;
      }
      DAT_febe7e4e = (short)iVar4;
      DAT_febe7e2a = 0x5a;
    }
    else {
      iVar7 = (int)((int)(int16_t)DAT_febe7e4e) + (int)((int)(int16_t)DAT_febe7e4c);
      iVar4 = -iVar7;
      if (iVar4 + 0x7fff < 0 == (-1 < iVar4 && iVar4 + 0x7fff < 0) && iVar7 != 0x7fff) {
        if (iVar4 + -0x7fff < 0 == (iVar4 < 0 && -1 < iVar4 + -0x7fff) && iVar7 != -0x7fff) {
          iVar4 = 0x7fff;
        }
      }
      else {
        iVar4 = -0x7fff;
      }
      DAT_febe7e50 = (short)iVar4;
      DAT_febe7e2b = 0x5a;
    }
  }
  return;
}

void return_only_stub_48d30(void)

{
  return;
}

void initialize_six_retained_current_references_to_8000_48d32(void)

{
  ((volatile uint16_t *)camry_host_ptr(0xfebe7e6cu))[0] = 0x8000;
  (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7e6cu + (uint32_t)(1) * 2u)))) = 0x8000;
  (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7e6cu + (uint32_t)(2) * 2u)))) = 0x8000;
  (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7e6cu + (uint32_t)(3) * 2u)))) = 0x8000;
  (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7e6cu + (uint32_t)(4) * 2u)))) = 0x8000;
  (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7e6cu + (uint32_t)(5) * 2u)))) = 0x8000;
  return;
}

void refresh_monitor_current_reference_banks(void)

{
  if (DAT_00031e58 == '\x01') {
    if (DAT_febe636a == 'Z') {
      ((volatile uint16_t *)camry_host_ptr(0xfebe7e6cu))[0] = DAT_febe6238;
      (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7e6cu + (uint32_t)(1) * 2u)))) = DAT_febe623a;
      (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7e6cu + (uint32_t)(2) * 2u)))) = DAT_febe623c;
    }
    if (DAT_febe636b != 'Z') {
      return;
    }
  }
  else {
    ((volatile uint16_t *)camry_host_ptr(0xfebe7e6cu))[0] = DAT_febe6238;
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7e6cu + (uint32_t)(1) * 2u)))) = DAT_febe623a;
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7e6cu + (uint32_t)(2) * 2u)))) = DAT_febe623c;
  }
  (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7e6cu + (uint32_t)(5) * 2u)))) = DAT_febe6242;
  (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7e6cu + (uint32_t)(4) * 2u)))) = DAT_febe6240;
  (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7e6cu + (uint32_t)(3) * 2u)))) = DAT_febe623e;
  return;
}

void condition_monitor_current_planes(void)

{
  uint8_t stack_record_24[36];
  int iVar1;
  ushort uVar2;
  undefined2 uVar3;
  uint uVar4;
  uint32_t puVar5;
  uint32_t puVar6;
  int iVar7;
  int iVar8;
  uint uVar9;
  int iVar10;
  int iVar11;
  int iVar12;
  
  puVar5 = 0xfebeb800u;
  refresh_monitor_current_reference_banks();
  iVar12 = (int)(*((short *)camry_host_ptr((uint32_t)((int)(0xffffb11eu + (uint32_t)((int)puVar5))))));
  iVar11 = (int)(*((short *)camry_host_ptr((uint32_t)((int)(0xffffb106u + (uint32_t)((int)puVar5))))));
  iVar10 = (int)(*((short *)camry_host_ptr((uint32_t)((int)(0xffffb112u + (uint32_t)((int)puVar5))))));
  uVar9 = (uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar5 + -0x55d4))));
  iVar8 = (uVar9 - (*((ushort *)camry_host_ptr((uint32_t)(puVar5 + -0x3994))))) - iVar12;
  iVar7 = iVar10;
  if ((int)((uVar9 - (*((ushort *)camry_host_ptr((uint32_t)(puVar5 + -0x3994))))) - iVar12) < 0) {
    iVar7 = iVar11;
  }
  if ((iVar8 == 0) || (iVar7 == 0)) {
    uVar4 = 0;
  }
  else {
    if (iVar8 < 0) {
      if (iVar7 < 0) goto LAB_00048dee;
    }
    else if (-1 < iVar7) {
LAB_00048dee:
      if ((-1 < (longlong)iVar7 * (longlong)iVar8 &&
           (int)((ulonglong)((longlong)iVar7 * (longlong)iVar8) >> 0x20) != 0) ||
         (uVar4 = iVar8 * iVar7, 0x7fffffff < (int)uVar4)) {
        uVar4 = 0x7fffffff;
      }
      goto LAB_00048e22;
    }
    iVar1 = (int)((ulonglong)((longlong)iVar7 * (longlong)iVar8) >> 0x20) + 1;
    if ((iVar1 < 0 != (-1 < (longlong)iVar7 * (longlong)iVar8 && iVar1 < 0)) ||
       (uVar4 = iVar8 * iVar7, uVar4 < 0x80000001)) {
      uVar4 = 0x80000001;
    }
  }
LAB_00048e22:
  iVar8 = (int)uVar4 / 0x4000;
  if (iVar8 + 0x7fff < 0 == (-1 < iVar8 && iVar8 + 0x7fff < 0) && iVar8 != -0x7fff) {
    if (iVar8 + -0x7fff < 0 == (iVar8 < 0 && -1 < iVar8 + -0x7fff) && iVar8 != 0x7fff) {
      iVar8 = 0x7fff;
    }
    uVar3 = (undefined2)iVar8;
  }
  else {
    uVar3 = 0x8001;
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar5 + -0x3988)))) = uVar3;
  uVar4 = iVar12 + 0x8000;
  iVar8 = uVar9 - uVar4;
  if (uVar9 == uVar4) {
LAB_00048e5c:
    uVar9 = 0;
  }
  else {
    iVar7 = iVar10;
    if ((int)(uVar9 - uVar4) < 0) {
      iVar7 = iVar11;
    }
    if (iVar7 == 0) goto LAB_00048e5c;
    if (iVar8 < 0) {
      if (iVar7 < 0) goto LAB_00048e6e;
LAB_00048e86:
      iVar12 = (int)((ulonglong)((longlong)iVar7 * (longlong)iVar8) >> 0x20) + 1;
      if ((iVar12 < 0 != (-1 < (longlong)iVar7 * (longlong)iVar8 && iVar12 < 0)) ||
         (uVar9 = iVar8 * iVar7, uVar9 < 0x80000001)) {
        uVar9 = 0x80000001;
      }
    }
    else {
      if (iVar7 < 0) goto LAB_00048e86;
LAB_00048e6e:
      if ((-1 < (longlong)iVar7 * (longlong)iVar8 &&
           (int)((ulonglong)((longlong)iVar7 * (longlong)iVar8) >> 0x20) != 0) ||
         (uVar9 = iVar8 * iVar7, 0x7fffffff < (int)uVar9)) {
        uVar9 = 0x7fffffff;
      }
    }
  }
  (*((int32_t *)(stack_record_24 + 0))) = (int)uVar9 / 0x4000;
  if ((*((int32_t *)(stack_record_24 + 0))) + 0x7fff < 0 == (-1 < (*((int32_t *)(stack_record_24 + 0))) && (*((int32_t *)(stack_record_24 + 0))) + 0x7fff < 0) && (*((int32_t *)(stack_record_24 + 0))) != -0x7fff) {
    iVar8 = (*((int32_t *)(stack_record_24 + 0)));
    if ((*((int32_t *)(stack_record_24 + 0))) + -0x7fff < 0 == ((*((int32_t *)(stack_record_24 + 0))) < 0 && -1 < (*((int32_t *)(stack_record_24 + 0))) + -0x7fff) && (*((int32_t *)(stack_record_24 + 0))) != 0x7fff) {
      iVar8 = 0x7fff;
    }
    uVar3 = (undefined2)iVar8;
  }
  else {
    uVar3 = 0x8001;
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar5 + -0x3970)))) = uVar3;
  if ((int)((*((ushort *)camry_host_ptr((uint32_t)(puVar5 + -0x55c8)))) - uVar4) < 0) {
    iVar10 = iVar11;
  }
  puVar6 = (uint32_t)((uint32_t)(puVar5));
  store_symmetric_saturating_s32_product_706ae(((uint32_t)((uint32_t)((*((ushort *)camry_host_ptr((uint32_t)(puVar5 + -0x55c8)))) - uVar4))),  iVar10,  stack_record_24);
  (*((int32_t *)(stack_record_24 + 0))) = (*((int32_t *)(stack_record_24 + 0))) / 0x4000;
  if ((*((int32_t *)(stack_record_24 + 0))) + 0x7fff < 0 == (-1 < (*((int32_t *)(stack_record_24 + 0))) && (*((int32_t *)(stack_record_24 + 0))) + 0x7fff < 0) && (*((int32_t *)(stack_record_24 + 0))) != -0x7fff) {
    iVar8 = (*((int32_t *)(stack_record_24 + 0)));
    if ((*((int32_t *)(stack_record_24 + 0))) + -0x7fff < 0 == ((*((int32_t *)(stack_record_24 + 0))) < 0 && -1 < (*((int32_t *)(stack_record_24 + 0))) + -0x7fff) && (*((int32_t *)(stack_record_24 + 0))) != 0x7fff) {
      iVar8 = 0x7fff;
    }
    uVar3 = (undefined2)iVar8;
  }
  else {
    uVar3 = 0x8001;
  }
  uVar9 = (uint)*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(-0x55d2) * 1u))));
  iVar12 = (int)(*((short *)camry_host_ptr((uint32_t)((int)0xffffb120u + (int)puVar6))));
  iVar11 = (int)(*((short *)camry_host_ptr((uint32_t)((int)0xffffb108u + (int)puVar6))));
  iVar10 = (int)(*((short *)camry_host_ptr((uint32_t)((int)0xffffb114u + (int)puVar6))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar5 + -0x397c)))) = uVar3;
  uVar2 = *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(-0x55c6) * 1u))));
  iVar8 = (uVar9 - (*((ushort *)camry_host_ptr((uint32_t)(puVar5 + -0x3992))))) - iVar12;
  iVar7 = iVar10;
  if ((int)((uVar9 - (*((ushort *)camry_host_ptr((uint32_t)(puVar5 + -0x3992))))) - iVar12) < 0) {
    iVar7 = iVar11;
  }
  if ((iVar8 == 0) || (iVar7 == 0)) {
    uVar4 = 0;
  }
  else {
    if (iVar8 < 0) {
      if (iVar7 < 0) goto LAB_00048f3e;
    }
    else if (-1 < iVar7) {
LAB_00048f3e:
      if ((-1 < (longlong)iVar7 * (longlong)iVar8 &&
           (int)((ulonglong)((longlong)iVar7 * (longlong)iVar8) >> 0x20) != 0) ||
         (uVar4 = iVar8 * iVar7, 0x7fffffff < (int)uVar4)) {
        uVar4 = 0x7fffffff;
      }
      goto LAB_00048f72;
    }
    iVar1 = (int)((ulonglong)((longlong)iVar7 * (longlong)iVar8) >> 0x20) + 1;
    if ((iVar1 < 0 != (-1 < (longlong)iVar7 * (longlong)iVar8 && iVar1 < 0)) ||
       (uVar4 = iVar8 * iVar7, uVar4 < 0x80000001)) {
      uVar4 = 0x80000001;
    }
  }
LAB_00048f72:
  iVar8 = (int)uVar4 / 0x4000;
  if (iVar8 + 0x7fff < 0 == (-1 < iVar8 && iVar8 + 0x7fff < 0) && iVar8 != -0x7fff) {
    if (iVar8 + -0x7fff < 0 == (iVar8 < 0 && -1 < iVar8 + -0x7fff) && iVar8 != 0x7fff) {
      iVar8 = 0x7fff;
    }
    uVar3 = (undefined2)iVar8;
  }
  else {
    uVar3 = 0x8001;
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar5 + -0x3986)))) = uVar3;
  uVar4 = iVar12 + 0x8000;
  iVar8 = uVar9 - uVar4;
  if (uVar9 == uVar4) {
LAB_00048fac:
    uVar9 = 0;
  }
  else {
    iVar7 = iVar10;
    if ((int)(uVar9 - uVar4) < 0) {
      iVar7 = iVar11;
    }
    if (iVar7 == 0) goto LAB_00048fac;
    if (iVar8 < 0) {
      if (iVar7 < 0) goto LAB_00048fbe;
LAB_00048fd6:
      iVar12 = (int)((ulonglong)((longlong)iVar7 * (longlong)iVar8) >> 0x20) + 1;
      if ((iVar12 < 0 != (-1 < (longlong)iVar7 * (longlong)iVar8 && iVar12 < 0)) ||
         (uVar9 = iVar8 * iVar7, uVar9 < 0x80000001)) {
        uVar9 = 0x80000001;
      }
    }
    else {
      if (iVar7 < 0) goto LAB_00048fd6;
LAB_00048fbe:
      if ((-1 < (longlong)iVar7 * (longlong)iVar8 &&
           (int)((ulonglong)((longlong)iVar7 * (longlong)iVar8) >> 0x20) != 0) ||
         (uVar9 = iVar8 * iVar7, 0x7fffffff < (int)uVar9)) {
        uVar9 = 0x7fffffff;
      }
    }
  }
  (*((int32_t *)(stack_record_24 + 4))) = (int)uVar9 / 0x4000;
  if ((*((int32_t *)(stack_record_24 + 4))) + 0x7fff < 0 == (-1 < (*((int32_t *)(stack_record_24 + 4))) && (*((int32_t *)(stack_record_24 + 4))) + 0x7fff < 0) && (*((int32_t *)(stack_record_24 + 4))) != -0x7fff)
  {
    iVar8 = (*((int32_t *)(stack_record_24 + 4)));
    if ((*((int32_t *)(stack_record_24 + 4))) + -0x7fff < 0 == ((*((int32_t *)(stack_record_24 + 4))) < 0 && -1 < (*((int32_t *)(stack_record_24 + 4))) + -0x7fff) &&
        (*((int32_t *)(stack_record_24 + 4))) != 0x7fff) {
      iVar8 = 0x7fff;
    }
    uVar3 = (undefined2)iVar8;
  }
  else {
    uVar3 = 0x8001;
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar5 + -0x396e)))) = uVar3;
  if ((int)(uVar2 - uVar4) < 0) {
    iVar10 = iVar11;
  }
  store_symmetric_saturating_s32_product_706ae(uVar2 - uVar4,iVar10,(stack_record_24 + 4));
  (*((int32_t *)(stack_record_24 + 4))) = (*((int32_t *)(stack_record_24 + 4))) / 0x4000;
  if ((*((int32_t *)(stack_record_24 + 4))) + 0x7fff < 0 == (-1 < (*((int32_t *)(stack_record_24 + 4))) && (*((int32_t *)(stack_record_24 + 4))) + 0x7fff < 0) && (*((int32_t *)(stack_record_24 + 4))) != -0x7fff)
  {
    iVar8 = (*((int32_t *)(stack_record_24 + 4)));
    if ((*((int32_t *)(stack_record_24 + 4))) + -0x7fff < 0 == ((*((int32_t *)(stack_record_24 + 4))) < 0 && -1 < (*((int32_t *)(stack_record_24 + 4))) + -0x7fff) &&
        (*((int32_t *)(stack_record_24 + 4))) != 0x7fff) {
      iVar8 = 0x7fff;
    }
    uVar3 = (undefined2)iVar8;
  }
  else {
    uVar3 = 0x8001;
  }
  uVar9 = (uint)*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(-0x55d0) * 1u))));
  iVar12 = (int)(*((short *)camry_host_ptr((uint32_t)((int)0xffffb122u + (int)puVar6))));
  iVar11 = (int)(*((short *)camry_host_ptr((uint32_t)((0xffffb10au) + (int)puVar6))));
  iVar10 = (int)(*((short *)camry_host_ptr((uint32_t)((int)0xffffb116u + (int)puVar6))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar5 + -0x397a)))) = uVar3;
  uVar2 = *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(-0x55c4) * 1u))));
  iVar8 = (uVar9 - (*((ushort *)camry_host_ptr((uint32_t)(puVar5 + -0x3990))))) - iVar12;
  iVar7 = iVar10;
  if ((int)((uVar9 - (*((ushort *)camry_host_ptr((uint32_t)(puVar5 + -0x3990))))) - iVar12) < 0) {
    iVar7 = iVar11;
  }
  if ((iVar8 == 0) || (iVar7 == 0)) {
    uVar4 = 0;
  }
  else {
    if (iVar8 < 0) {
      if (iVar7 < 0) goto LAB_00049090;
    }
    else if (-1 < iVar7) {
LAB_00049090:
      if ((-1 < (longlong)iVar7 * (longlong)iVar8 &&
           (int)((ulonglong)((longlong)iVar7 * (longlong)iVar8) >> 0x20) != 0) ||
         (uVar4 = iVar8 * iVar7, 0x7fffffff < (int)uVar4)) {
        uVar4 = 0x7fffffff;
      }
      goto LAB_000490c4;
    }
    iVar1 = (int)((ulonglong)((longlong)iVar7 * (longlong)iVar8) >> 0x20) + 1;
    if ((iVar1 < 0 != (-1 < (longlong)iVar7 * (longlong)iVar8 && iVar1 < 0)) ||
       (uVar4 = iVar8 * iVar7, uVar4 < 0x80000001)) {
      uVar4 = 0x80000001;
    }
  }
LAB_000490c4:
  iVar8 = (int)uVar4 / 0x4000;
  if (iVar8 + 0x7fff < 0 == (-1 < iVar8 && iVar8 + 0x7fff < 0) && iVar8 != -0x7fff) {
    if (iVar8 + -0x7fff < 0 == (iVar8 < 0 && -1 < iVar8 + -0x7fff) && iVar8 != 0x7fff) {
      iVar8 = 0x7fff;
    }
    uVar3 = (undefined2)iVar8;
  }
  else {
    uVar3 = 0x8001;
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar5 + -0x3984)))) = uVar3;
  uVar4 = iVar12 + 0x8000;
  iVar8 = uVar9 - uVar4;
  if (uVar9 == uVar4) {
LAB_000490fe:
    uVar9 = 0;
  }
  else {
    iVar7 = iVar10;
    if ((int)(uVar9 - uVar4) < 0) {
      iVar7 = iVar11;
    }
    if (iVar7 == 0) goto LAB_000490fe;
    if (iVar8 < 0) {
      if (iVar7 < 0) goto LAB_00049110;
LAB_00049128:
      iVar12 = (int)((ulonglong)((longlong)iVar7 * (longlong)iVar8) >> 0x20) + 1;
      if ((iVar12 < 0 != (-1 < (longlong)iVar7 * (longlong)iVar8 && iVar12 < 0)) ||
         (uVar9 = iVar8 * iVar7, uVar9 < 0x80000001)) {
        uVar9 = 0x80000001;
      }
    }
    else {
      if (iVar7 < 0) goto LAB_00049128;
LAB_00049110:
      if ((-1 < (longlong)iVar7 * (longlong)iVar8 &&
           (int)((ulonglong)((longlong)iVar7 * (longlong)iVar8) >> 0x20) != 0) ||
         (uVar9 = iVar8 * iVar7, 0x7fffffff < (int)uVar9)) {
        uVar9 = 0x7fffffff;
      }
    }
  }
  (*((int32_t *)(stack_record_24 + 8))) = (int)uVar9 / 0x4000;
  if ((*((int32_t *)(stack_record_24 + 8))) + 0x7fff < 0 == (-1 < (*((int32_t *)(stack_record_24 + 8))) && (*((int32_t *)(stack_record_24 + 8))) + 0x7fff < 0) && (*((int32_t *)(stack_record_24 + 8))) != -0x7fff)
  {
    iVar8 = (*((int32_t *)(stack_record_24 + 8)));
    if ((*((int32_t *)(stack_record_24 + 8))) + -0x7fff < 0 == ((*((int32_t *)(stack_record_24 + 8))) < 0 && -1 < (*((int32_t *)(stack_record_24 + 8))) + -0x7fff) &&
        (*((int32_t *)(stack_record_24 + 8))) != 0x7fff) {
      iVar8 = 0x7fff;
    }
    uVar3 = (undefined2)iVar8;
  }
  else {
    uVar3 = 0x8001;
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar5 + -0x396c)))) = uVar3;
  if ((int)(uVar2 - uVar4) < 0) {
    iVar10 = iVar11;
  }
  store_symmetric_saturating_s32_product_706ae(uVar2 - uVar4,iVar10,(stack_record_24 + 8));
  (*((int32_t *)(stack_record_24 + 8))) = (*((int32_t *)(stack_record_24 + 8))) / 0x4000;
  if ((*((int32_t *)(stack_record_24 + 8))) + 0x7fff < 0 == (-1 < (*((int32_t *)(stack_record_24 + 8))) && (*((int32_t *)(stack_record_24 + 8))) + 0x7fff < 0) && (*((int32_t *)(stack_record_24 + 8))) != -0x7fff)
  {
    iVar8 = (*((int32_t *)(stack_record_24 + 8)));
    if ((*((int32_t *)(stack_record_24 + 8))) + -0x7fff < 0 == ((*((int32_t *)(stack_record_24 + 8))) < 0 && -1 < (*((int32_t *)(stack_record_24 + 8))) + -0x7fff) &&
        (*((int32_t *)(stack_record_24 + 8))) != 0x7fff) {
      iVar8 = 0x7fff;
    }
    uVar3 = (undefined2)iVar8;
  }
  else {
    uVar3 = 0x8001;
  }
  uVar9 = (uint)*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(-0x55ce) * 1u))));
  iVar12 = (int)(*((short *)camry_host_ptr((uint32_t)((int)0xffffb124u + (int)puVar6))));
  iVar11 = (int)(*((short *)camry_host_ptr((uint32_t)((0xffffb10cu) + (int)puVar6))));
  iVar10 = (int)(*((short *)camry_host_ptr((uint32_t)((int)0xffffb118u + (int)puVar6))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar5 + -0x3978)))) = uVar3;
  uVar2 = *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(-0x55c2) * 1u))));
  iVar8 = (uVar9 - (*((ushort *)camry_host_ptr((uint32_t)(puVar5 + -0x398e))))) - iVar12;
  iVar7 = iVar10;
  if ((int)((uVar9 - (*((ushort *)camry_host_ptr((uint32_t)(puVar5 + -0x398e))))) - iVar12) < 0) {
    iVar7 = iVar11;
  }
  if ((iVar8 == 0) || (iVar7 == 0)) {
    uVar4 = 0;
  }
  else {
    if (iVar8 < 0) {
      if (iVar7 < 0) goto LAB_000491e2;
    }
    else if (-1 < iVar7) {
LAB_000491e2:
      if ((-1 < (longlong)iVar7 * (longlong)iVar8 &&
           (int)((ulonglong)((longlong)iVar7 * (longlong)iVar8) >> 0x20) != 0) ||
         (uVar4 = iVar8 * iVar7, 0x7fffffff < (int)uVar4)) {
        uVar4 = 0x7fffffff;
      }
      goto LAB_00049216;
    }
    iVar1 = (int)((ulonglong)((longlong)iVar7 * (longlong)iVar8) >> 0x20) + 1;
    if ((iVar1 < 0 != (-1 < (longlong)iVar7 * (longlong)iVar8 && iVar1 < 0)) ||
       (uVar4 = iVar8 * iVar7, uVar4 < 0x80000001)) {
      uVar4 = 0x80000001;
    }
  }
LAB_00049216:
  iVar8 = (int)uVar4 / 0x4000;
  if (iVar8 + 0x7fff < 0 == (-1 < iVar8 && iVar8 + 0x7fff < 0) && iVar8 != -0x7fff) {
    if (iVar8 + -0x7fff < 0 == (iVar8 < 0 && -1 < iVar8 + -0x7fff) && iVar8 != 0x7fff) {
      iVar8 = 0x7fff;
    }
    uVar3 = (undefined2)iVar8;
  }
  else {
    uVar3 = 0x8001;
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar5 + -0x3982)))) = uVar3;
  uVar4 = iVar12 + 0x8000;
  iVar8 = uVar9 - uVar4;
  if (uVar9 == uVar4) {
LAB_00049250:
    uVar9 = 0;
  }
  else {
    iVar7 = iVar10;
    if ((int)(uVar9 - uVar4) < 0) {
      iVar7 = iVar11;
    }
    if (iVar7 == 0) goto LAB_00049250;
    if (iVar8 < 0) {
      if (iVar7 < 0) goto LAB_00049262;
LAB_0004927a:
      iVar12 = (int)((ulonglong)((longlong)iVar7 * (longlong)iVar8) >> 0x20) + 1;
      if ((iVar12 < 0 != (-1 < (longlong)iVar7 * (longlong)iVar8 && iVar12 < 0)) ||
         (uVar9 = iVar8 * iVar7, uVar9 < 0x80000001)) {
        uVar9 = 0x80000001;
      }
    }
    else {
      if (iVar7 < 0) goto LAB_0004927a;
LAB_00049262:
      if ((-1 < (longlong)iVar7 * (longlong)iVar8 &&
           (int)((ulonglong)((longlong)iVar7 * (longlong)iVar8) >> 0x20) != 0) ||
         (uVar9 = iVar8 * iVar7, 0x7fffffff < (int)uVar9)) {
        uVar9 = 0x7fffffff;
      }
    }
  }
  (*((int32_t *)(stack_record_24 + 12))) = (int)uVar9 / 0x4000;
  if ((*((int32_t *)(stack_record_24 + 12))) + 0x7fff < 0 == (-1 < (*((int32_t *)(stack_record_24 + 12))) && (*((int32_t *)(stack_record_24 + 12))) + 0x7fff < 0) && (*((int32_t *)(stack_record_24 + 12))) != -0x7fff)
  {
    iVar8 = (*((int32_t *)(stack_record_24 + 12)));
    if ((*((int32_t *)(stack_record_24 + 12))) + -0x7fff < 0 == ((*((int32_t *)(stack_record_24 + 12))) < 0 && -1 < (*((int32_t *)(stack_record_24 + 12))) + -0x7fff) &&
        (*((int32_t *)(stack_record_24 + 12))) != 0x7fff) {
      iVar8 = 0x7fff;
    }
    uVar3 = (undefined2)iVar8;
  }
  else {
    uVar3 = 0x8001;
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar5 + -0x396a)))) = uVar3;
  if ((int)(uVar2 - uVar4) < 0) {
    iVar10 = iVar11;
  }
  store_symmetric_saturating_s32_product_706ae(uVar2 - uVar4,iVar10,(stack_record_24 + 12));
  (*((int32_t *)(stack_record_24 + 12))) = (*((int32_t *)(stack_record_24 + 12))) / 0x4000;
  if ((*((int32_t *)(stack_record_24 + 12))) + 0x7fff < 0 == (-1 < (*((int32_t *)(stack_record_24 + 12))) && (*((int32_t *)(stack_record_24 + 12))) + 0x7fff < 0) && (*((int32_t *)(stack_record_24 + 12))) != -0x7fff)
  {
    iVar8 = (*((int32_t *)(stack_record_24 + 12)));
    if ((*((int32_t *)(stack_record_24 + 12))) + -0x7fff < 0 == ((*((int32_t *)(stack_record_24 + 12))) < 0 && -1 < (*((int32_t *)(stack_record_24 + 12))) + -0x7fff) &&
        (*((int32_t *)(stack_record_24 + 12))) != 0x7fff) {
      iVar8 = 0x7fff;
    }
    uVar3 = (undefined2)iVar8;
  }
  else {
    uVar3 = 0x8001;
  }
  uVar9 = (uint)*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(-0x55cc) * 1u))));
  iVar12 = (int)(*((short *)camry_host_ptr((uint32_t)((int)0xffffb126u + (int)puVar6))));
  iVar11 = (int)(*((short *)camry_host_ptr((uint32_t)((0xffffb10eu) + (int)puVar6))));
  iVar10 = (int)(*((short *)camry_host_ptr((uint32_t)((int)0xffffb11au + (int)puVar6))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar5 + -0x3976)))) = uVar3;
  uVar2 = *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(-0x55c0) * 1u))));
  iVar8 = (uVar9 - (*((ushort *)camry_host_ptr((uint32_t)(puVar5 + -0x398c))))) - iVar12;
  iVar7 = iVar10;
  if ((int)((uVar9 - (*((ushort *)camry_host_ptr((uint32_t)(puVar5 + -0x398c))))) - iVar12) < 0) {
    iVar7 = iVar11;
  }
  if ((iVar8 == 0) || (iVar7 == 0)) {
    uVar4 = 0;
  }
  else {
    if (iVar8 < 0) {
      if (iVar7 < 0) goto LAB_00049334;
    }
    else if (-1 < iVar7) {
LAB_00049334:
      if ((-1 < (longlong)iVar7 * (longlong)iVar8 &&
           (int)((ulonglong)((longlong)iVar7 * (longlong)iVar8) >> 0x20) != 0) ||
         (uVar4 = iVar8 * iVar7, 0x7fffffff < (int)uVar4)) {
        uVar4 = 0x7fffffff;
      }
      goto LAB_00049368;
    }
    iVar1 = (int)((ulonglong)((longlong)iVar7 * (longlong)iVar8) >> 0x20) + 1;
    if ((iVar1 < 0 != (-1 < (longlong)iVar7 * (longlong)iVar8 && iVar1 < 0)) ||
       (uVar4 = iVar8 * iVar7, uVar4 < 0x80000001)) {
      uVar4 = 0x80000001;
    }
  }
LAB_00049368:
  iVar8 = (int)uVar4 / 0x4000;
  if (iVar8 + 0x7fff < 0 == (-1 < iVar8 && iVar8 + 0x7fff < 0) && iVar8 != -0x7fff) {
    if (iVar8 + -0x7fff < 0 == (iVar8 < 0 && -1 < iVar8 + -0x7fff) && iVar8 != 0x7fff) {
      iVar8 = 0x7fff;
    }
    uVar3 = (undefined2)iVar8;
  }
  else {
    uVar3 = 0x8001;
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar5 + -0x3980)))) = uVar3;
  uVar4 = iVar12 + 0x8000;
  iVar8 = uVar9 - uVar4;
  if (uVar9 == uVar4) {
LAB_000493a2:
    uVar9 = 0;
  }
  else {
    iVar7 = iVar10;
    if ((int)(uVar9 - uVar4) < 0) {
      iVar7 = iVar11;
    }
    if (iVar7 == 0) goto LAB_000493a2;
    if (iVar8 < 0) {
      if (iVar7 < 0) goto LAB_000493b4;
LAB_000493cc:
      iVar12 = (int)((ulonglong)((longlong)iVar7 * (longlong)iVar8) >> 0x20) + 1;
      if ((iVar12 < 0 != (-1 < (longlong)iVar7 * (longlong)iVar8 && iVar12 < 0)) ||
         (uVar9 = iVar8 * iVar7, uVar9 < 0x80000001)) {
        uVar9 = 0x80000001;
      }
    }
    else {
      if (iVar7 < 0) goto LAB_000493cc;
LAB_000493b4:
      if ((-1 < (longlong)iVar7 * (longlong)iVar8 &&
           (int)((ulonglong)((longlong)iVar7 * (longlong)iVar8) >> 0x20) != 0) ||
         (uVar9 = iVar8 * iVar7, 0x7fffffff < (int)uVar9)) {
        uVar9 = 0x7fffffff;
      }
    }
  }
  (*((int32_t *)(stack_record_24 + 16))) = (int)uVar9 / 0x4000;
  if ((*((int32_t *)(stack_record_24 + 16))) + 0x7fff < 0 == (-1 < (*((int32_t *)(stack_record_24 + 16))) && (*((int32_t *)(stack_record_24 + 16))) + 0x7fff < 0) && (*((int32_t *)(stack_record_24 + 16))) != -0x7fff)
  {
    iVar8 = (*((int32_t *)(stack_record_24 + 16)));
    if ((*((int32_t *)(stack_record_24 + 16))) + -0x7fff < 0 == ((*((int32_t *)(stack_record_24 + 16))) < 0 && -1 < (*((int32_t *)(stack_record_24 + 16))) + -0x7fff) &&
        (*((int32_t *)(stack_record_24 + 16))) != 0x7fff) {
      iVar8 = 0x7fff;
    }
    uVar3 = (undefined2)iVar8;
  }
  else {
    uVar3 = 0x8001;
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar5 + -0x3968)))) = uVar3;
  if ((int)(uVar2 - uVar4) < 0) {
    iVar10 = iVar11;
  }
  store_symmetric_saturating_s32_product_706ae(uVar2 - uVar4,iVar10,(stack_record_24 + 16));
  (*((int32_t *)(stack_record_24 + 16))) = (*((int32_t *)(stack_record_24 + 16))) / 0x4000;
  if ((*((int32_t *)(stack_record_24 + 16))) + 0x7fff < 0 == (-1 < (*((int32_t *)(stack_record_24 + 16))) && (*((int32_t *)(stack_record_24 + 16))) + 0x7fff < 0) && (*((int32_t *)(stack_record_24 + 16))) != -0x7fff)
  {
    iVar8 = (*((int32_t *)(stack_record_24 + 16)));
    if ((*((int32_t *)(stack_record_24 + 16))) + -0x7fff < 0 == ((*((int32_t *)(stack_record_24 + 16))) < 0 && -1 < (*((int32_t *)(stack_record_24 + 16))) + -0x7fff) &&
        (*((int32_t *)(stack_record_24 + 16))) != 0x7fff) {
      iVar8 = 0x7fff;
    }
    uVar3 = (undefined2)iVar8;
  }
  else {
    uVar3 = 0x8001;
  }
  uVar9 = (uint)*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(-0x55ca) * 1u))));
  iVar12 = (int)(*((short *)camry_host_ptr((uint32_t)((int)0xffffb128u + (int)puVar6))));
  iVar11 = (int)(*((short *)camry_host_ptr((uint32_t)((0xffffb110u) + (int)puVar6))));
  iVar10 = (int)(*((short *)camry_host_ptr((uint32_t)((int)0xffffb11cu + (int)puVar6))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar5 + -0x3974)))) = uVar3;
  uVar2 = *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(-0x55be) * 1u))));
  iVar8 = (uVar9 - (*((ushort *)camry_host_ptr((uint32_t)(puVar5 + -0x398a))))) - iVar12;
  iVar7 = iVar10;
  if ((int)((uVar9 - (*((ushort *)camry_host_ptr((uint32_t)(puVar5 + -0x398a))))) - iVar12) < 0) {
    iVar7 = iVar11;
  }
  if ((iVar8 == 0) || (iVar7 == 0)) {
    uVar4 = 0;
  }
  else {
    if (iVar8 < 0) {
      if (iVar7 < 0) goto LAB_00049486;
    }
    else if (-1 < iVar7) {
LAB_00049486:
      if ((-1 < (longlong)iVar7 * (longlong)iVar8 &&
           (int)((ulonglong)((longlong)iVar7 * (longlong)iVar8) >> 0x20) != 0) ||
         (uVar4 = iVar8 * iVar7, 0x7fffffff < (int)uVar4)) {
        uVar4 = 0x7fffffff;
      }
      goto LAB_000494ba;
    }
    iVar1 = (int)((ulonglong)((longlong)iVar7 * (longlong)iVar8) >> 0x20) + 1;
    if ((iVar1 < 0 != (-1 < (longlong)iVar7 * (longlong)iVar8 && iVar1 < 0)) ||
       (uVar4 = iVar8 * iVar7, uVar4 < 0x80000001)) {
      uVar4 = 0x80000001;
    }
  }
LAB_000494ba:
  iVar8 = (int)uVar4 / 0x4000;
  if (iVar8 + 0x7fff < 0 == (-1 < iVar8 && iVar8 + 0x7fff < 0) && iVar8 != -0x7fff) {
    if (iVar8 + -0x7fff < 0 == (iVar8 < 0 && -1 < iVar8 + -0x7fff) && iVar8 != 0x7fff) {
      iVar8 = 0x7fff;
    }
    uVar3 = (undefined2)iVar8;
  }
  else {
    uVar3 = 0x8001;
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar5 + -0x397e)))) = uVar3;
  uVar4 = iVar12 + 0x8000;
  iVar8 = uVar9 - uVar4;
  if (uVar9 != uVar4) {
    iVar7 = iVar10;
    if ((int)(uVar9 - uVar4) < 0) {
      iVar7 = iVar11;
    }
    if (iVar7 != 0) {
      if (iVar8 < 0) {
        if (iVar7 < 0) goto LAB_00049506;
      }
      else if (-1 < iVar7) {
LAB_00049506:
        if ((-1 < (longlong)iVar7 * (longlong)iVar8 &&
             (int)((ulonglong)((longlong)iVar7 * (longlong)iVar8) >> 0x20) != 0) ||
           (uVar9 = iVar8 * iVar7, 0x7fffffff < (int)uVar9)) {
          uVar9 = 0x7fffffff;
        }
        goto LAB_0004953a;
      }
      iVar12 = (int)((ulonglong)((longlong)iVar7 * (longlong)iVar8) >> 0x20) + 1;
      if ((iVar12 < 0 != (-1 < (longlong)iVar7 * (longlong)iVar8 && iVar12 < 0)) ||
         (uVar9 = iVar8 * iVar7, uVar9 < 0x80000001)) {
        uVar9 = 0x80000001;
      }
      goto LAB_0004953a;
    }
  }
  uVar9 = 0;
LAB_0004953a:
  (*((int32_t *)(stack_record_24 + 20))) = (int)uVar9 / 0x4000;
  if ((*((int32_t *)(stack_record_24 + 20))) + 0x7fff < 0 == (-1 < (*((int32_t *)(stack_record_24 + 20))) && (*((int32_t *)(stack_record_24 + 20))) + 0x7fff < 0) && (*((int32_t *)(stack_record_24 + 20))) != -0x7fff)
  {
    iVar8 = (*((int32_t *)(stack_record_24 + 20)));
    if ((*((int32_t *)(stack_record_24 + 20))) + -0x7fff < 0 == ((*((int32_t *)(stack_record_24 + 20))) < 0 && -1 < (*((int32_t *)(stack_record_24 + 20))) + -0x7fff) &&
        (*((int32_t *)(stack_record_24 + 20))) != 0x7fff) {
      iVar8 = 0x7fff;
    }
    uVar3 = (undefined2)iVar8;
  }
  else {
    uVar3 = 0x8001;
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar5 + -0x3966)))) = uVar3;
  if ((int)(uVar2 - uVar4) < 0) {
    iVar10 = iVar11;
  }
  store_symmetric_saturating_s32_product_706ae(uVar2 - uVar4,iVar10,(stack_record_24 + 20));
  (*((int32_t *)(stack_record_24 + 20))) = (*((int32_t *)(stack_record_24 + 20))) / 0x4000;
  if ((*((int32_t *)(stack_record_24 + 20))) + 0x7fff < 0 == (-1 < (*((int32_t *)(stack_record_24 + 20))) && (*((int32_t *)(stack_record_24 + 20))) + 0x7fff < 0) && (*((int32_t *)(stack_record_24 + 20))) != -0x7fff)
  {
    if ((*((int32_t *)(stack_record_24 + 20))) + -0x7fff < 0 == ((*((int32_t *)(stack_record_24 + 20))) < 0 && -1 < (*((int32_t *)(stack_record_24 + 20))) + -0x7fff) &&
        (*((int32_t *)(stack_record_24 + 20))) != 0x7fff) {
      (*((int32_t *)(stack_record_24 + 20))) = 0x7fff;
    }
    uVar3 = (undefined2)(*((int32_t *)(stack_record_24 + 20)));
  }
  else {
    uVar3 = 0x8001;
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar5 + -0x3972)))) = uVar3;
  return;
}
