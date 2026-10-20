#include "common.h"

void return_only_stub_3a008(void)

{
  return;
}

int update_ecu_source2_thermal_branch1(short upper,short lower,uchar alternate_gains)

{
  uint8_t stack_record_30[48];
  short gain;
  int iVar1;
  uint32_t puVar2;
  uint divisor;
  uint divisor_00;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  short gain_00;
  
  iVar4 = DAT_febe70b8;
  iVar3 = DAT_febe6f64;
  iVar5 = DAT_febe6f60;
  puVar2 = 0xfebeb800u;
  iVar7 = (int)lower;
  iVar8 = (int)upper;
  iVar1 = (int)((int)(int16_t)DAT_febe64e2);
  (*((int16_t *)(stack_record_30 + 2))) = ((int)(int16_t)DAT_febe6f54);
  gain = DAT_0002b3aa;
  gain_00 = DAT_0002b3a8;
  if (alternate_gains != '\0') {
    gain = DAT_0002b3ae;
    gain_00 = DAT_0002b3ac;
  }
  if (iVar1 + 0x7fff < 0 == (-1 < iVar1 && iVar1 + 0x7fff < 0) && iVar1 != -0x7fff) {
    if (iVar1 < 0) {
      iVar1 = (int)-((int)(int16_t)DAT_febe64e2);
    }
  }
  else {
    iVar1 = 0x7fff;
  }
  iVar6 = (int)DAT_0002b3b8;
  if (iVar1 > iVar6 && (int)DAT_febe70b8 > (int)DAT_0002b3c0) {
    (*((uint16_t *)(stack_record_30 + 0))) = DAT_0002b3b6;
  }
  else {
    puVar2 = 0xfebeb800u;
    interpolate_u16_axis_u16_values_70304(((undefined *)camry_host_ptr(0x2b36cu)),((int)(int16_t)DAT_febe6694) & 0x7fff,stack_record_30);
  }
  divisor = scale_thermal_divisor((uint)DAT_0002b3b2,(uint)(*((uint16_t *)(stack_record_30 + 0))));
  divisor_00 = scale_thermal_divisor((uint)DAT_0002b3b4,(uint)(*((uint16_t *)(stack_record_30 + 0))));
  iVar1 = update_nonnegative_thermal_pole(iVar5,iVar4,divisor);
  iVar3 = update_nonnegative_thermal_pole(iVar3,iVar4,divisor_00);
  iVar4 = scale_thermal_contribution(iVar1,gain_00,upper,lower);
  iVar6 = scale_thermal_contribution(iVar3,gain,upper,lower);
  iVar5 = (int)DAT_0002b3b0 + iVar4 + iVar6;
  if (iVar5 - iVar8 < 0 != (iVar5 < 0 != iVar8 < 0 && iVar8 < 0 == iVar5 - iVar8 < 0) ||
      iVar5 == iVar8) {
    iVar8 = iVar5;
  }
  if (iVar8 - iVar7 < 0 == (iVar8 < 0 != iVar7 < 0 && iVar7 < 0 == iVar8 - iVar7 < 0)) {
    iVar7 = iVar8;
  }
  iVar5 = apply_thermal_offset_and_following(1,(short)iVar7,(*((int16_t *)(stack_record_30 + 2))));
  (*((short *)camry_host_ptr((uint32_t)((0xffffb75eu + (uint32_t)((int)puVar2)))))) = (short)iVar7;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb754u + (uint32_t)((int)puVar2)))))) = (short)iVar5;
  (*((int *)camry_host_ptr((uint32_t)((0xffffb760u + (uint32_t)((int)puVar2)))))) = iVar1;
  (*((int *)camry_host_ptr((uint32_t)((0xffffb764u + (uint32_t)((int)puVar2)))))) = iVar3;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb75au + (uint32_t)((int)puVar2)))))) = (short)divisor;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb75cu + (uint32_t)((int)puVar2)))))) = (short)divisor_00;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb756u + (uint32_t)((int)puVar2)))))) = (short)iVar4;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb758u + (uint32_t)((int)puVar2)))))) = (short)iVar6;
  return iVar5;
}

int compute_signed_ratio_q19_saturating_3a110(short param_1,short param_2)

{
  int iVar1;
  int iVar2;
  
  iVar2 = (int)param_2;
  if (iVar2 == 0) {
    return 0;
  }
  iVar1 = (int)param_1 << 0xc;
  if (iVar2 != 0) {
    if (iVar1 == -0x80000000 && iVar2 == -1) {
      iVar1 = -0x80000000;
    }
    else {
      iVar1 = (int)iVar1 / (int)iVar2;
    }
  }
  if (iVar1 < 0) {
    iVar2 = (int)((ulonglong)((longlong)iVar1 * 0x80) >> 0x20) + 1;
    if ((iVar2 < 0 != (-1 < (longlong)iVar1 * 0x80 && iVar2 < 0)) ||
       ((uint)(iVar1 * 0x80) < 0x80000001)) {
      return -0x7fffffff;
    }
  }
  else {
    if (iVar1 == 0) {
      return 0;
    }
    if ((-1 < (longlong)iVar1 * 0x80 && (int)((ulonglong)((longlong)iVar1 * 0x80) >> 0x20) != 0) ||
       (0x7fffffff < (uint)(iVar1 * 0x80))) {
      return 0x7fffffff;
    }
  }
  return iVar1 * 0x80;
}

void initialize_6f60_mode_selected_ratio_pair_3a160(short param_1,short param_2,char param_3)

{
  short sVar1;
  uint32_t puVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  short sVar2;
  
  puVar3 = 0xfebeb800u;
  sVar1 = DAT_0002b3a8;
  sVar2 = DAT_0002b3aa;
  if (param_3 != '\0') {
    sVar1 = DAT_0002b3ac;
    sVar2 = DAT_0002b3ae;
  }
  uVar4 = compute_signed_ratio_q19_saturating_3a110((int)param_1,(int)sVar1);
  uVar5 = compute_signed_ratio_q19_saturating_3a110((int)param_2,(int)sVar2);
  (*((undefined4 *)camry_host_ptr((uint32_t)((0xffffb760u + (uint32_t)((int)puVar3)))))) = uVar4;
  (*((undefined4 *)camry_host_ptr((uint32_t)((0xffffb764u + (uint32_t)((int)puVar3)))))) = uVar5;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb754u + (uint32_t)((int)puVar3)))))) = 0x3480;
  return;
}

void rebase_ecu_source2_thermal_branch1(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  iVar2 = 0x7fffffff;
  iVar4 = (int)DAT_0002b3ac;
  iVar3 = (int)DAT_0002b3ae;
  if (iVar4 == 0) {
LAB_0003a1d4:
    iVar2 = 0;
  }
  else {
    iVar1 = ((int)DAT_febe6f60 / 0x800) * (int)DAT_0002b3a8;
    if (iVar4 != 0) {
      if (iVar1 == -0x80000000 && iVar4 == -1) {
        iVar1 = -0x80000000;
      }
      else {
        iVar1 = (int)iVar1 / (int)iVar4;
      }
    }
    if (iVar1 < 0) {
      iVar2 = (int)((ulonglong)((longlong)iVar1 * 0x800) >> 0x20) + 1;
      if ((iVar2 < 0 != (-1 < (longlong)iVar1 * 0x800 && iVar2 < 0)) ||
         ((uint)(iVar1 * 0x800) < 0x80000001)) {
        iVar2 = -0x7fffffff;
        goto LAB_0003a204;
      }
    }
    else {
      if (iVar1 == 0) goto LAB_0003a1d4;
      if ((-1 < (longlong)iVar1 * 0x800 && (int)((ulonglong)((longlong)iVar1 * 0x800) >> 0x20) != 0)
         || (0x7fffffff < (uint)(iVar1 * 0x800))) goto LAB_0003a204;
    }
    iVar2 = iVar1 * 0x800;
  }
LAB_0003a204:
  if (iVar3 != 0) {
    iVar4 = ((int)DAT_febe6f64 / 0x800) * (int)DAT_0002b3aa;
    if (iVar3 != 0) {
      if (iVar4 == -0x80000000 && iVar3 == -1) {
        iVar4 = -0x80000000;
      }
      else {
        iVar4 = (int)iVar4 / (int)iVar3;
      }
    }
    if (iVar4 < 0) {
      iVar3 = (int)((ulonglong)((longlong)iVar4 * 0x800) >> 0x20) + 1;
      if ((iVar3 < 0 == (-1 < (longlong)iVar4 * 0x800 && iVar3 < 0)) &&
         (0x80000000 < (uint)(iVar4 * 0x800))) {
        DAT_febe6f60 = iVar2;
        DAT_febe6f64 = iVar4 * 0x800;
        return;
      }
      DAT_febe6f60 = iVar2;
      DAT_febe6f64 = 0x80000001;
      return;
    }
    if (iVar4 != 0) {
      if (((longlong)iVar4 * 0x800 < 0 || (int)((ulonglong)((longlong)iVar4 * 0x800) >> 0x20) == 0)
         && ((uint)(iVar4 * 0x800) < 0x80000000)) {
        DAT_febe6f60 = iVar2;
        DAT_febe6f64 = iVar4 * 0x800;
        return;
      }
      DAT_febe6f60 = iVar2;
      DAT_febe6f64 = 0x7fffffff;
      return;
    }
  }
  DAT_febe6f60 = iVar2;
  DAT_febe6f64 = 0;
  return;
}

void clear_6f56_pair_and_6f60_ratio_states_3a25c(void)

{
  DAT_febe6f56 = 0;
  DAT_febe6f58 = 0;
  DAT_febe6f60 = 0;
  DAT_febe6f64 = 0;
  return;
}

void return_only_stub_3a26a(void)

{
  return;
}

void initialize_6f68_half_ratio_constants_3a26c(void)

{
  DAT_febe6f68 = 0x569a;
  DAT_febe6f6a = 0x2b4d;
  return;
}

void publish_ecu_source2_thermal_limit_maps(void)

{
  uint8_t stack_record_c[12];
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  iVar2 = (int)((int)(int16_t)DAT_febe6f36);
  interpolate_s16_axis_u16_values_7025c(ecu_source2_current_curve_bank0,iVar2,((uint16_t *)(stack_record_c)));
  interpolate_s16_axis_u16_values_7025c(ecu_source2_current_curve_bank1,iVar2,((uint16_t *)((stack_record_c + 2))));
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb768u + (uint32_t)((int)puVar1)))))) = (*((uint16_t *)(stack_record_c + 0)));
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb76au + (uint32_t)((int)puVar1)))))) = (*((uint16_t *)(stack_record_c + 2)));
  return;
}

void return_only_stub_3a2b6(void)

{
  return;
}

void fill_constant_block_3a2b8(void)

{
  DAT_febe6f6e = 0x569a;
  DAT_febe6f70 = 0x569a;
  DAT_febe6f72 = 0x2b4d;
  DAT_febe6f74 = 0x569a;
  DAT_febe6f76 = 0x569a;
  DAT_febe6f78 = 0x2b4d;
  return;
}

uint choose_thermal_limit_source
               (ushort current,ushort candidate,uchar *source,uchar candidate_source)

{
  uint uVar1;
  
  uVar1 = (uint)current;
  if ((camry_host_addr((source))!= 0) && (candidate <= uVar1)) {
    *source = candidate_source;
    uVar1 = (uint)candidate;
  }
  return uVar1;
}

uint select_ecu_thermal_limit(uchar *source,uchar bank)

{
  uint32_t puVar1;
  uint32_t puVar2;
  ushort uVar3;
  ushort uVar4;
  uint uVar5;
  
  uVar4 = DAT_febe6f6a;
  uVar3 = DAT_febe6f68;
  puVar2 = 0xfebeb800u;
  puVar1 = 0xfebeb800u;
  if (camry_host_addr((source))== 0) {
    if (bank == '\0') {
      uVar5 = 0x569a;
    }
    else {
      uVar5 = 0x2b4d;
    }
  }
  else {
    if (bank == '\0') {
      *source = '\x02';
      uVar4 = DAT_febe6f30;
      if ((camry_host_addr((source))!= 0) && (DAT_febe6f30 <= uVar3)) {
        *source = '\x04';
        uVar3 = uVar4;
      }
                    /* WARNING: Could not inline here */
      uVar5 = choose_thermal_limit_source(uVar3,DAT_febe6ee0,source,'\x05');
      uVar4 = (ushort)uVar5;
      uVar3 = (*((ushort *)camry_host_ptr((uint32_t)((0xffffb80cu + (uint32_t)((int)puVar1))))));
    }
    else {
      *source = '\x02';
      uVar5 = choose_thermal_limit_source(uVar4,DAT_febe6f32,source,'\x04');
      uVar5 = choose_thermal_limit_source
                        ((ushort)uVar5,(*((ushort *)camry_host_ptr((uint32_t)((0xffffb6e2u + (uint32_t)((int)puVar2)))))),source,'\x05');
      uVar4 = (ushort)uVar5;
      uVar3 = (*((ushort *)camry_host_ptr((uint32_t)((0xffffb80eu + (uint32_t)((int)puVar2))))));
    }
    uVar5 = choose_thermal_limit_source(uVar4,uVar3,source,'\x03');
  }
  return uVar5;
}

int select_ecu_thermal_diagnostic(ushort limit,uchar source,uchar *active_source,uchar bank)

{
  ushort uVar1;
  int iVar2;
  
  if (camry_host_addr((active_source))== 0) {
    return 0;
  }
  uVar1 = 0x2b4d;
  if (bank == '\0') {
    uVar1 = 0x569a;
  }
  if (uVar1 <= limit) {
switchD_0003a386_default:
    *active_source = '\0';
    return 0;
  }
  switch(source) {
  case '\x02':
    iVar2 = (int)((int)(int16_t)DAT_febe6f36);
    break;
  case '\x03':
    iVar2 = (int)((int)(int16_t)DAT_febe6fe2);
    break;
  case '\x04':
    iVar2 = (int)((int)(int16_t)DAT_febe6f12);
    break;
  case '\x05':
    iVar2 = (int)((int)(int16_t)DAT_febe6eae);
    break;
  default:
    goto switchD_0003a386_default;
  }
  *active_source = source;
  return iVar2;
}

void select_motor_thermal_diagnostic
               (ushort limit,ushort nominal,uchar *active,short *temperature)

{
  short sVar1;
  
  if (limit < nominal) {
    *active = '\x01';
    sVar1 = ((int)(int16_t)DAT_febe6f82);
  }
  else {
    *active = '\0';
    sVar1 = 0;
  }
  *temperature = sVar1;
  return;
}

int select_smaller_magnitude_s16(short first,short second)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  iVar2 = (int)first;
  iVar3 = (int)second;
  if (iVar2 + 0x7fff < 0 == (-1 < iVar2 && iVar2 + 0x7fff < 0) && iVar2 != -0x7fff) {
    iVar1 = iVar2;
    if (iVar2 < 0) {
      iVar1 = (int)-first;
    }
  }
  else {
    iVar1 = 0x7fff;
  }
  if (iVar3 + 0x7fff < 0 == (-1 < iVar3 && iVar3 + 0x7fff < 0) && iVar3 != -0x7fff) {
    iVar4 = iVar3;
    if (iVar3 < 0) {
      iVar4 = (int)-second;
    }
  }
  else {
    iVar4 = 0x7fff;
  }
  if (iVar1 - iVar4 < 0 != (iVar1 < 0 != iVar4 < 0 && iVar4 < 0 == iVar1 - iVar4 < 0) ||
      iVar1 == iVar4) {
    iVar3 = iVar2;
  }
  return iVar3;
}

void map_thermal_current_floor(ushort current_limit)

{
  uint8_t stack_record_c[12];
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  interpolate_s16_axis_s16_values_70208(((undefined *)camry_host_ptr(0x2b420u)),(int)((int)(int16_t)DAT_febe6f36),((int16_t *)(stack_record_c)));
  interpolate_s16_axis_s16_values_70208(((undefined *)camry_host_ptr(0x2b43cu)),(int)(*((short *)camry_host_ptr((uint32_t)((0xffffb712u + (uint32_t)((int)puVar1)))))),((int16_t *)((stack_record_c + 2))));
  iVar2 = select_smaller_magnitude_s16((*((int16_t *)(stack_record_c + 0))),(*((int16_t *)(stack_record_c + 2))));
  (*((int16_t *)(stack_record_c + 0))) = (short)iVar2;
  interpolate_s16_axis_s16_values_70208(((undefined *)camry_host_ptr(0x2b458u)),(int)(*((short *)camry_host_ptr((uint32_t)((0xffffb6aeu + (uint32_t)((int)puVar1)))))),((int16_t *)((stack_record_c + 2))));
  iVar2 = select_smaller_magnitude_s16((*((int16_t *)(stack_record_c + 0))),(*((int16_t *)(stack_record_c + 2))));
  (*((int16_t *)(stack_record_c + 0))) = (short)iVar2;
  interpolate_s16_axis_s16_values_70208(((undefined *)camry_host_ptr(0x2b474u)),(int)(*((short *)camry_host_ptr((uint32_t)((0xffffb7e2u + (uint32_t)((int)puVar1)))))),((int16_t *)((stack_record_c + 2))));
  iVar2 = select_smaller_magnitude_s16((*((int16_t *)(stack_record_c + 0))),(*((int16_t *)(stack_record_c + 2))));
  (*((int16_t *)(stack_record_c + 0))) = (short)iVar2;
  interpolate_u16_axis_s16_values_702b0(((undefined *)camry_host_ptr(0x2b3fcu)),current_limit,((int16_t *)((stack_record_c + 2))));
  iVar2 = select_smaller_magnitude_s16((*((int16_t *)(stack_record_c + 0))),(*((int16_t *)(stack_record_c + 2))));
  (*((short *)camry_host_ptr((uint32_t)((0xffffb77eu + (uint32_t)((int)puVar1)))))) = (short)iVar2;
  return;
}

void arbitrate_thermal_current_limits(void)

{
  uint8_t stack_record_2a[42];
  ushort uVar1;
  ushort uVar2;
  uint32_t puVar3;
  ushort limit;
  ushort nominal;
  undefined2 uVar4;
  uint uVar5;
  uint uVar6;
  ushort uVar8;
  ushort limit_00;
  int iVar7;
  uint uVar9;
  
  uVar8 = DAT_febe6764;
  puVar3 = 0xfebeb800u;
  stack_record_2a[2] = '\0';
  stack_record_2a[3] = '\0';
  uVar5 = select_ecu_thermal_limit(((uint8_t *)((stack_record_2a + 2))),'\0');
  uVar1 = (*((ushort *)camry_host_ptr((uint32_t)((0xffffb7acu + (uint32_t)((int)puVar3))))));
  iVar7 = uVar1 - uVar5;
  uVar9 = uVar5;
  if (iVar7 < 0 != ((int)uVar5 < 0 && (int)uVar5 < 0 == iVar7 < 0)) {
    uVar9 = (uint)uVar1;
  }
  limit_00 = (ushort)uVar9;
  uVar6 = select_ecu_thermal_limit(((uint8_t *)((stack_record_2a + 3))),'\x01');
  uVar2 = (*((ushort *)camry_host_ptr((uint32_t)((0xffffb7aeu + (uint32_t)((int)puVar3))))));
  iVar7 = uVar2 - uVar6;
  uVar9 = uVar6;
  if (iVar7 < 0 != ((int)uVar6 < 0 && (int)uVar6 < 0 == iVar7 < 0)) {
    uVar9 = (uint)uVar2;
  }
  limit = (ushort)uVar5;
  if ((uVar8 & 3) == 0) {
    iVar7 = select_ecu_thermal_diagnostic(limit,stack_record_2a[2],((uint8_t *)(stack_record_2a)),(byte)uVar8 & 3);
    uVar4 = (undefined2)iVar7;
    nominal = 0x569a;
    uVar8 = uVar1;
  }
  else {
    iVar7 = select_ecu_thermal_diagnostic((ushort)uVar6,stack_record_2a[3],((uint8_t *)(stack_record_2a)),'\x01');
    uVar4 = (undefined2)iVar7;
    nominal = 0x2b4d;
    uVar5 = uVar6;
    uVar8 = uVar2;
    limit_00 = (ushort)uVar9;
  }
  select_motor_thermal_diagnostic(uVar8,nominal,((uint8_t *)((stack_record_2a + 1))),((int16_t *)((stack_record_2a + 4))));
  set_current_limit_request(0,limit_00);
  map_thermal_current_floor(limit_00);
  (*((short *)camry_host_ptr((uint32_t)((0xffffb76eu + (uint32_t)((int)puVar3)))))) = (short)uVar5;
  (*((ushort *)camry_host_ptr((uint32_t)((0xffffb770u + (uint32_t)((int)puVar3)))))) = limit;
  (*((ushort *)camry_host_ptr((uint32_t)((0xffffb772u + (uint32_t)((int)puVar3)))))) = (ushort)uVar6;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb76cu + (uint32_t)((int)puVar3) * 1u)))) = stack_record_2a[0];
  (*((ushort *)camry_host_ptr((uint32_t)((0xffffb774u + (uint32_t)((int)puVar3)))))) = uVar8;
  (*((ushort *)camry_host_ptr((uint32_t)((0xffffb776u + (uint32_t)((int)puVar3)))))) = uVar1;
  (*((ushort *)camry_host_ptr((uint32_t)((0xffffb778u + (uint32_t)((int)puVar3)))))) = uVar2;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb76du + (uint32_t)((int)puVar3) * 1u)))) = stack_record_2a[1];
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb77au + (uint32_t)((int)puVar3)))))) = uVar4;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb77cu + (uint32_t)((int)puVar3)))))) = (*((int16_t *)(stack_record_2a + 4)));
  return;
}

void return_only_stub_3a558(void)

{
  return;
}

int clear_6f80_if_588b6_returns_zero_3a55a(void)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  iVar2 = test_redundant_status_a5_or_vote_error13_588b6();
  if (iVar2 == 0) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb780u + (uint32_t)((int)puVar1) * 1u)))) = 0;
  }
  return iVar2;
}

uint should_zero_motor_thermal_seed(ushort record_marker)

{
  int iVar1;
  int threshold;
  uint uVar2;
  
  if ((DAT_febe7bf8 & 0xff) == 0) {
    if ((DAT_febe7bf8 & 0xff00) != 0) {
      DAT_febe6f84 = (int)((int)(int16_t)DAT_febe7dd0) - (int)((int)(int16_t)DAT_febe7dce);
      iVar1 = (int)DAT_febe6f84;
      goto LAB_0003a5b6;
    }
  }
  else if ((DAT_febe7bf8 & 0xff00) == 0) {
    DAT_febe6f88 = (int)((int)(int16_t)DAT_febe7dd8) - (int)((int)(int16_t)DAT_febe7dd6);
    iVar1 = (int)DAT_febe6f88;
    goto LAB_0003a5b6;
  }
  DAT_febe6f84 = (int)((int)(int16_t)DAT_febe7dd0) - (int)((int)(int16_t)DAT_febe7dce);
  DAT_febe6f88 = (int)((int)(int16_t)DAT_febe7dd8) - (int)((int)(int16_t)DAT_febe7dd6);
  iVar1 = (int)DAT_febe6f84;
  if ((int)DAT_febe6f88 - iVar1 < 0 !=
      ((int)DAT_febe6f88 < 0 != iVar1 < 0 && iVar1 < 0 == (int)DAT_febe6f88 - iVar1 < 0))
  {
    iVar1 = (int)DAT_febe6f88;
  }
LAB_0003a5b6:
  threshold = (int)DAT_0002b4b8;
  if ((iVar1 - threshold < 0 ==
       (iVar1 < 0 != threshold < 0 && threshold < 0 == iVar1 - threshold < 0) &&
       iVar1 != threshold) && (record_marker == 0)) {
    uVar2 = 0x5a;
  }
  else {
    uVar2 = 0;
  }
  return uVar2;
}

void restore_motor_thermal_model(void)

{
  uint8_t stack_record_4c[76];
  undefined4 *puVar1;
  uint32_t puVar2;
  uint uVar3;
  undefined4 uVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  undefined4 *puVar9;
  
  puVar2 = 0xfebeb800u;
  puVar1 = ((uint32_t *)(stack_record_4c));
  puVar9 = ((undefined *)camry_host_ptr(0x211e8u));
  do {
    uVar4 = *puVar9;
    puVar9 = puVar9 + 1;
    *puVar1 = uVar4;
    puVar1 = puVar1 + 1;
  } while (camry_host_addr(puVar9)!=((uint32_t)(0x21220u)));
  uVar3 = nvm_get_record(6, camry_host_addr(((uint32_t *)(stack_record_4c))));
  iVar8 = (int)(short)(*((uint32_t *)(stack_record_4c + 0)));
  iVar7 = (int)(*((int16_t *)(stack_record_4c + 4)));
  iVar6 = (int)(*((uint16_t *)((uint8_t *)((uint32_t *)(stack_record_4c)) + 2u)));
  iVar5 = (int)(*((int16_t *)(stack_record_4c + 6)));
  if ((uVar3 == 0x10) && ((*((uint16_t *)(stack_record_4c + 50))) != 0xa55a)) {
    if ((((((*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x3c08)))) & 0xff) == 0) ||
         (((*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x3c08)))) & 0xff00) == 0)) && ((*((uint16_t *)(stack_record_4c + 50))) != 0x5aa5)) &&
       (uVar3 = should_zero_motor_thermal_seed((*((uint16_t *)(stack_record_4c + 50)))), uVar3 == 0x5a)) {
      iVar8 = 0;
      iVar5 = 0;
      iVar7 = 0;
      iVar6 = 0;
    }
  }
  else {
    iVar8 = (int)DAT_0002b4b6;
    iVar5 = (int)DAT_0002b4b4;
    iVar7 = iVar8;
    iVar6 = iVar5;
  }
  initialize_6f94_calibrated_ratio_3a808(iVar8);
  initialize_6fa4_calibrated_ratio_3a94a(iVar7);
  store_6f98_calibrated_ratio_3a82a(iVar6);
  store_6fa8_calibrated_ratio_3a96c(iVar5);
  return;
}

void update_motor_thermal_estimate(void)

{
  short upper;
  short lower;
  uint32_t puVar1;
  undefined2 uVar2;
  undefined *puVar3;
  int iVar5;
  int iVar6;
  char cVar7;
  uint32_t puVar4;
  puVar4 = 0xfebeb800u;
  puVar3 = ((undefined *)camry_host_ptr(0xfebeb800u));
  cVar7 = DAT_febe6f80;
  puVar1 = (0xfebeb800u);
  if (DAT_febe6f80 == '\0') {
    if ((DAT_febe7dcc != 'Z') || (DAT_febe7bf6 != 'Z')) goto LAB_0003a6be;
    restore_motor_thermal_model();
    cVar7 = 'Z';
    puVar1 = ((uint32_t)(puVar4));
  }
  puVar3 = ((void *)camry_host_ptr((uint32_t)(puVar1)));
  lower = DAT_0002b4b2;
  upper = DAT_0002b4b0;
  iVar5 = update_motor_thermal_branch0(DAT_0002b4b0,DAT_0002b4b2);
  iVar6 = update_motor_thermal_branch1(upper,lower);
  if (iVar6 - iVar5 < 0 == (iVar6 < 0 != iVar5 < 0 && iVar5 < 0 == iVar6 - iVar5 < 0) &&
      iVar6 != iVar5) {
    uVar2 = (undefined2)iVar6;
  }
  else {
    uVar2 = (undefined2)iVar5;
  }
  *(undefined2 *)camry_host_ptr((uint32_t)(0xffffb782u + (uint32_t)camry_host_addr(puVar3))) = uVar2;
LAB_0003a6be:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb780u + (uint32_t)((int)camry_host_addr(puVar3)) * 1u)))) = cVar7;
  return;
}

int compute_signed_ratio_q19_saturating_3a6c6(short param_1,short param_2)

{
  int iVar1;
  int iVar2;
  
  iVar2 = (int)param_2;
  if (iVar2 == 0) {
    return 0;
  }
  iVar1 = (int)param_1 << 0xc;
  if (iVar2 != 0) {
    if (iVar1 == -0x80000000 && iVar2 == -1) {
      iVar1 = -0x80000000;
    }
    else {
      iVar1 = (int)iVar1 / (int)iVar2;
    }
  }
  if (iVar1 < 0) {
    iVar2 = (int)((ulonglong)((longlong)iVar1 * 0x80) >> 0x20) + 1;
    if ((iVar2 < 0 != (-1 < (longlong)iVar1 * 0x80 && iVar2 < 0)) ||
       ((uint)(iVar1 * 0x80) < 0x80000001)) {
      return -0x7fffffff;
    }
  }
  else {
    if (iVar1 == 0) {
      return 0;
    }
    if ((-1 < (longlong)iVar1 * 0x80 && (int)((ulonglong)((longlong)iVar1 * 0x80) >> 0x20) != 0) ||
       (0x7fffffff < (uint)(iVar1 * 0x80))) {
      return 0x7fffffff;
    }
  }
  return iVar1 * 0x80;
}

void return_only_stub_3a716(void)

{
  return;
}

int update_motor_thermal_branch0(short upper,short lower)

{
  short previous;
  int iVar1;
  uint32_t puVar2;
  uint divisor;
  uint divisor_00;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  ushort uStack_2a;
  
  iVar4 = ((int)(int32_t)DAT_febe70b4);
  iVar3 = DAT_febe6f98;
  iVar5 = DAT_febe6f94;
  previous = ((int)(int16_t)DAT_febe6f8c);
  puVar2 = 0xfebeb800u;
  iVar7 = (int)lower;
  iVar8 = (int)upper;
  iVar1 = (int)((int)(int16_t)DAT_febe64e2);
  iVar6 = (int)DAT_0002b4c8;
  if (iVar1 + 0x7fff < 0 == (-1 < iVar1 && iVar1 + 0x7fff < 0) && iVar1 != -0x7fff) {
    if (iVar1 < 0) {
      iVar1 = (int)-((int)(int16_t)DAT_febe64e2);
    }
  }
  else {
    iVar1 = 0x7fff;
  }
  if ((iVar1 - iVar6 < 0 == (iVar1 < 0 != iVar6 < 0 && iVar6 < 0 == iVar1 - iVar6 < 0) &&
       iVar1 != iVar6) &&
     (((int)(int32_t)DAT_febe70b4) - DAT_0002b4cc < 0 ==
      (((int)(int32_t)DAT_febe70b4) < 0 != DAT_0002b4cc < 0 && DAT_0002b4cc < 0 == ((int)(int32_t)DAT_febe70b4) - DAT_0002b4cc < 0)
      && ((int)(int32_t)DAT_febe70b4) != DAT_0002b4cc)) {
    uStack_2a = DAT_0002b4c6;
  }
  else {
    puVar2 = 0xfebeb800u;
    interpolate_u16_axis_u16_values_70304(((undefined *)camry_host_ptr(0x2b490u)),((int)(int16_t)DAT_febe668a) & 0x7fff,&uStack_2a);
  }
  divisor = scale_thermal_divisor((uint)DAT_0002b4c2,(uint)uStack_2a);
  divisor_00 = scale_thermal_divisor((uint)DAT_0002b4c4,(uint)uStack_2a);
  iVar1 = update_nonnegative_thermal_pole(iVar5,iVar4,divisor);
  iVar3 = update_nonnegative_thermal_pole(iVar3,iVar4,divisor_00);
  iVar4 = scale_thermal_contribution(iVar1,DAT_0002b4bc,upper,lower);
  iVar6 = scale_thermal_contribution(iVar3,DAT_0002b4be,upper,lower);
  iVar5 = (int)DAT_0002b4c0 + iVar6 + iVar4;
  if (iVar5 - iVar8 < 0 != (iVar5 < 0 != iVar8 < 0 && iVar8 < 0 == iVar5 - iVar8 < 0) ||
      iVar5 == iVar8) {
    iVar8 = iVar5;
  }
  if (iVar8 - iVar7 < 0 == (iVar8 < 0 != iVar7 < 0 && iVar7 < 0 == iVar8 - iVar7 < 0)) {
    iVar7 = iVar8;
  }
  iVar5 = apply_thermal_offset_and_following(6,(short)iVar7,previous);
  (*((short *)camry_host_ptr((uint32_t)((0xffffb792u + (uint32_t)((int)puVar2)))))) = (short)iVar7;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb78cu + (uint32_t)((int)puVar2)))))) = (short)iVar5;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb78eu + (uint32_t)((int)puVar2)))))) = (short)iVar4;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb790u + (uint32_t)((int)puVar2)))))) = (short)iVar6;
  (*((int *)camry_host_ptr((uint32_t)((0xffffb794u + (uint32_t)((int)puVar2)))))) = iVar1;
  (*((int *)camry_host_ptr((uint32_t)((0xffffb798u + (uint32_t)((int)puVar2)))))) = iVar3;
  return iVar5;
}

undefined4 initialize_6f94_calibrated_ratio_3a808(short param_1)

{
  uint32_t puVar1;
  undefined4 uVar2;
  
  puVar1 = 0xfebeb800u;
  uVar2 = compute_signed_ratio_q19_saturating_3a6c6((int)param_1,(int)DAT_0002b4bc);
  (*((undefined4 *)camry_host_ptr((uint32_t)((0xffffb794u + (uint32_t)((int)puVar1)))))) = uVar2;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb78cu + (uint32_t)((int)puVar1)))))) = 0x3480;
  return uVar2;
}

void store_6f98_calibrated_ratio_3a82a(short param_1)

{
  uint32_t puVar1;
  undefined4 uVar2;
  
  puVar1 = 0xfebeb800u;
  uVar2 = compute_signed_ratio_q19_saturating_3a6c6((int)param_1,(int)DAT_0002b4be);
  (*((undefined4 *)camry_host_ptr((uint32_t)((0xffffb798u + (uint32_t)((int)puVar1)))))) = uVar2;
  return;
}

void clear_6f8e_and_6f94_states_3a844(void)

{
  DAT_febe6f8e = 0;
  DAT_febe6f94 = 0;
  return;
}

void clear_6f90_and_6f98_states_3a84e(void)

{
  DAT_febe6f90 = 0;
  DAT_febe6f98 = 0;
  return;
}

void return_only_stub_3a858(void)

{
  return;
}

int update_motor_thermal_branch1(short upper,short lower)

{
  short previous;
  int iVar1;
  uint32_t puVar2;
  uint divisor;
  uint divisor_00;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  ushort uStack_2a;
  
  iVar4 = ((int)(int32_t)DAT_febe70b8);
  iVar3 = DAT_febe6fa8;
  iVar5 = DAT_febe6fa4;
  previous = ((int)(int16_t)DAT_febe6f9c);
  puVar2 = 0xfebeb800u;
  iVar7 = (int)lower;
  iVar8 = (int)upper;
  iVar1 = (int)((int)(int16_t)DAT_febe64e2);
  iVar6 = (int)DAT_0002b4dc;
  if (iVar1 + 0x7fff < 0 == (-1 < iVar1 && iVar1 + 0x7fff < 0) && iVar1 != -0x7fff) {
    if (iVar1 < 0) {
      iVar1 = (int)-((int)(int16_t)DAT_febe64e2);
    }
  }
  else {
    iVar1 = 0x7fff;
  }
  if ((iVar1 - iVar6 < 0 == (iVar1 < 0 != iVar6 < 0 && iVar6 < 0 == iVar1 - iVar6 < 0) &&
       iVar1 != iVar6) &&
     (((int)(int32_t)DAT_febe70b8) - DAT_0002b4e0 < 0 ==
      (((int)(int32_t)DAT_febe70b8) < 0 != DAT_0002b4e0 < 0 && DAT_0002b4e0 < 0 == ((int)(int32_t)DAT_febe70b8) - DAT_0002b4e0 < 0)
      && ((int)(int32_t)DAT_febe70b8) != DAT_0002b4e0)) {
    uStack_2a = DAT_0002b4da;
  }
  else {
    puVar2 = 0xfebeb800u;
    interpolate_u16_axis_u16_values_70304(((undefined *)camry_host_ptr(0x2b490u)),((int)(int16_t)DAT_febe6694) & 0x7fff,&uStack_2a);
  }
  divisor = scale_thermal_divisor((uint)DAT_0002b4d6,(uint)uStack_2a);
  divisor_00 = scale_thermal_divisor((uint)DAT_0002b4d8,(uint)uStack_2a);
  iVar1 = update_nonnegative_thermal_pole(iVar5,iVar4,divisor);
  iVar3 = update_nonnegative_thermal_pole(iVar3,iVar4,divisor_00);
  iVar4 = scale_thermal_contribution(iVar1,DAT_0002b4d0,upper,lower);
  iVar6 = scale_thermal_contribution(iVar3,DAT_0002b4d2,upper,lower);
  iVar5 = (int)DAT_0002b4d4 + iVar6 + iVar4;
  if (iVar5 - iVar8 < 0 != (iVar5 < 0 != iVar8 < 0 && iVar8 < 0 == iVar5 - iVar8 < 0) ||
      iVar5 == iVar8) {
    iVar8 = iVar5;
  }
  if (iVar8 - iVar7 < 0 == (iVar8 < 0 != iVar7 < 0 && iVar7 < 0 == iVar8 - iVar7 < 0)) {
    iVar7 = iVar8;
  }
  iVar5 = apply_thermal_offset_and_following(7,(short)iVar7,previous);
  (*((short *)camry_host_ptr((uint32_t)((0xffffb7a2u + (uint32_t)((int)puVar2)))))) = (short)iVar7;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb79cu + (uint32_t)((int)puVar2)))))) = (short)iVar5;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb79eu + (uint32_t)((int)puVar2)))))) = (short)iVar4;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb7a0u + (uint32_t)((int)puVar2)))))) = (short)iVar6;
  (*((int *)camry_host_ptr((uint32_t)((0xffffb7a4u + (uint32_t)((int)puVar2)))))) = iVar1;
  (*((int *)camry_host_ptr((uint32_t)((0xffffb7a8u + (uint32_t)((int)puVar2)))))) = iVar3;
  return iVar5;
}

undefined4 initialize_6fa4_calibrated_ratio_3a94a(short param_1)

{
  uint32_t puVar1;
  undefined4 uVar2;
  
  puVar1 = 0xfebeb800u;
  uVar2 = compute_signed_ratio_q19_saturating_3a6c6((int)param_1,(int)DAT_0002b4d0);
  (*((undefined4 *)camry_host_ptr((uint32_t)((0xffffb7a4u + (uint32_t)((int)puVar1)))))) = uVar2;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb79cu + (uint32_t)((int)puVar1)))))) = 0x3480;
  return uVar2;
}

void store_6fa8_calibrated_ratio_3a96c(short param_1)

{
  uint32_t puVar1;
  undefined4 uVar2;
  
  puVar1 = 0xfebeb800u;
  uVar2 = compute_signed_ratio_q19_saturating_3a6c6((int)param_1,(int)DAT_0002b4d2);
  (*((undefined4 *)camry_host_ptr((uint32_t)((0xffffb7a8u + (uint32_t)((int)puVar1)))))) = uVar2;
  return;
}

void clear_6f9e_and_6fa4_states_3a986(void)

{
  DAT_febe6f9e = 0;
  DAT_febe6fa4 = 0;
  return;
}

void clear_6fa0_and_6fa8_states_3a990(void)

{
  DAT_febe6fa0 = 0;
  DAT_febe6fa8 = 0;
  return;
}

void return_only_stub_3a99a(void)

{
  return;
}

void initialize_6fac_half_ratio_constants_3a99c(void)

{
  DAT_febe6fac = 0x569a;
  DAT_febe6fae = 0x2b4d;
  return;
}

void publish_motor_thermal_limit_maps(void)

{
  uint8_t stack_record_c[12];
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  iVar2 = (int)((int)(int16_t)DAT_febe6f82);
  interpolate_s16_axis_u16_values_7025c(((undefined *)camry_host_ptr(0x2b4e4u)),iVar2,((uint16_t *)(stack_record_c)));
  interpolate_s16_axis_u16_values_7025c(((undefined *)camry_host_ptr(0x2b500u)),iVar2,((uint16_t *)((stack_record_c + 2))));
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb7acu + (uint32_t)((int)puVar1)))))) = (*((uint16_t *)(stack_record_c + 0)));
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb7aeu + (uint32_t)((int)puVar1)))))) = (*((uint16_t *)(stack_record_c + 2)));
  return;
}

void return_only_stub_3a9e6(void)

{
  return;
}

void return_only_stub_3a9e8(void)

{
  return;
}

uint check_thermal_raw_estimate_margin(void)

{
  uint8_t stack_record_26[38];
  int iVar1;
  uint32_t puVar2;
  uint uVar3;
  uint uVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  
  puVar2 = 0xfebeb800u;
  iVar1 = (int)((int)(int16_t)DAT_febe6fa2);
  iVar8 = (int)((int)(int16_t)DAT_febe6f92);
  iVar5 = (int)DAT_0002fb54;
  iVar7 = (int)((int)(int16_t)DAT_febe6f4a);
  iVar6 = (int)((int)(int16_t)DAT_febe6fee);
  if (iVar1 - iVar8 < 0 == (iVar1 < 0 != iVar8 < 0 && iVar8 < 0 == iVar1 - iVar8 < 0) &&
      iVar1 != iVar8) {
    iVar8 = iVar1;
  }
  iVar8 = iVar8 + iVar5 + (int)DAT_0002fb56;
  iVar1 = (int)((int)(int16_t)DAT_febe6f5e);
  if (iVar1 - iVar7 < 0 == (iVar1 < 0 != iVar7 < 0 && iVar7 < 0 == iVar1 - iVar7 < 0) &&
      iVar1 != iVar7) {
    iVar7 = iVar1;
  }
  iVar7 = iVar7 + iVar5 + (int)DAT_0002fb58;
  iVar1 = (int)((int)(int16_t)DAT_febe6ffe);
  if (iVar1 - iVar6 < 0 == (iVar1 < 0 != iVar6 < 0 && iVar6 < 0 == iVar1 - iVar6 < 0) &&
      iVar1 != iVar6) {
    iVar6 = iVar1;
  }
  iVar6 = iVar6 + iVar5 + (int)DAT_0002fb5a;
  iVar1 = (int)DAT_0002fb5c + ((int)(int16_t)DAT_febe6f14) + iVar5;
  iVar5 = (int)DAT_0002fb5e + ((int)(int16_t)DAT_febe6eb0) + iVar5;
  if (iVar8 + 0x7fff < 0 == (-1 < iVar8 && iVar8 + 0x7fff < 0) && iVar8 != -0x7fff) {
    if (iVar8 + -0x7fff < 0 == (iVar8 < 0 && -1 < iVar8 + -0x7fff) && iVar8 != 0x7fff) {
      iVar8 = 0x7fff;
    }
    else {
      iVar8 = (int)(short)iVar8;
    }
  }
  else {
    iVar8 = -0x7fff;
  }
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
  if (iVar1 + 0x7fff < 0 == (-1 < iVar1 && iVar1 + 0x7fff < 0) && iVar1 != -0x7fff) {
    if (iVar1 + -0x7fff < 0 == (iVar1 < 0 && -1 < iVar1 + -0x7fff) && iVar1 != 0x7fff) {
      iVar1 = 0x7fff;
    }
    else {
      iVar1 = (int)(short)iVar1;
    }
  }
  else {
    iVar1 = -0x7fff;
  }
  if (iVar5 + 0x7fff < 0 == (-1 < iVar5 && iVar5 + 0x7fff < 0) && iVar5 != -0x7fff) {
    if (iVar5 + -0x7fff < 0 == (iVar5 < 0 && -1 < iVar5 + -0x7fff) && iVar5 != 0x7fff) {
      iVar5 = 0x7fff;
    }
    else {
      iVar5 = (int)(short)iVar5;
    }
  }
  else {
    iVar5 = -0x7fff;
  }
  interpolate_s16_axis_u16_values_7025c(((undefined *)camry_host_ptr(0x2b4e4u)),iVar8,((uint16_t *)(stack_record_26)));
  interpolate_s16_axis_u16_values_7025c(ecu_source2_current_curve_bank0,iVar7,((uint16_t *)((stack_record_26 + 2))));
  interpolate_s16_axis_u16_values_7025c(((undefined *)camry_host_ptr(0x2b554u)),iVar6,((uint16_t *)((stack_record_26 + 4))));
  interpolate_s16_axis_u16_values_7025c(ecu_source4_current_curve_bank0,iVar1,((uint16_t *)((stack_record_26 + 6))));
  interpolate_s16_axis_u16_values_7025c(ecu_source5_current_curve_bank0,iVar5,((uint16_t *)((stack_record_26 + 8))));
  uVar4 = (uint)(*((uint16_t *)(stack_record_26 + 0)));
  uVar3 = 0x5a;
  if ((int)((*((uint16_t *)(stack_record_26 + 2))) - uVar4) < 0) {
    uVar4 = (uint)(*((uint16_t *)(stack_record_26 + 2)));
  }
  if ((int)((*((uint16_t *)(stack_record_26 + 4))) - uVar4) < 0) {
    uVar4 = (uint)(*((uint16_t *)(stack_record_26 + 4)));
  }
  if ((int)((*((uint16_t *)(stack_record_26 + 6))) - uVar4) < 0) {
    uVar4 = (uint)(*((uint16_t *)(stack_record_26 + 6)));
  }
  if ((int)((*((uint16_t *)(stack_record_26 + 8))) - uVar4) < 0) {
    uVar4 = (uint)(*((uint16_t *)(stack_record_26 + 8)));
  }
  if (DAT_0002fb60 <= uVar4) {
    uVar3 = 0xa5;
  }
  (*((short *)camry_host_ptr((uint32_t)((0xffffb7b4u + (uint32_t)((int)puVar2)))))) = (short)iVar8;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb7b6u + (uint32_t)((int)puVar2)))))) = (short)iVar7;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb7b8u + (uint32_t)((int)puVar2)))))) = (short)iVar6;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb7bau + (uint32_t)((int)puVar2)))))) = (short)iVar1;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb7bcu + (uint32_t)((int)puVar2)))))) = (short)iVar5;
  (*((ushort *)camry_host_ptr((uint32_t)((0xffffb7beu + (uint32_t)((int)puVar2)))))) = (*((uint16_t *)(stack_record_26 + 0)));
  (*((ushort *)camry_host_ptr((uint32_t)((0xffffb7c0u + (uint32_t)((int)puVar2)))))) = (*((uint16_t *)(stack_record_26 + 2)));
  (*((ushort *)camry_host_ptr((uint32_t)((0xffffb7c2u + (uint32_t)((int)puVar2)))))) = (*((uint16_t *)(stack_record_26 + 4)));
  (*((ushort *)camry_host_ptr((uint32_t)((0xffffb7c4u + (uint32_t)((int)puVar2)))))) = (*((uint16_t *)(stack_record_26 + 6)));
  (*((ushort *)camry_host_ptr((uint32_t)((0xffffb7c6u + (uint32_t)((int)puVar2)))))) = (*((uint16_t *)(stack_record_26 + 8)));
  (*((short *)camry_host_ptr((uint32_t)((0xffffb7c8u + (uint32_t)((int)puVar2)))))) = (short)uVar4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb7b1u + (uint32_t)((int)puVar2) * 1u)))) = (char)uVar3;
  return uVar3;
}

uint check_thermal_contribution_count(void)

{
  uint8_t stack_record_26[38];
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  uint32_t puVar6;
  uint uVar7;
  uint uVar8;
  uint uVar9;
  uint uVar10;
  uint uVar11;
  int iVar12;
  uint uVar13;
  uint uVar14;
  
  puVar6 = 0xfebeb800u;
  iVar12 = (int)((int)(int16_t)DAT_febe6f90);
  iVar1 = (int)((int)(int16_t)DAT_febe6fa0);
  uVar14 = (uint)thermal_shutdown_count;
  if (iVar1 - iVar12 < 0 == (iVar1 < 0 != iVar12 < 0 && iVar12 < 0 == iVar1 - iVar12 < 0) &&
      iVar1 != iVar12) {
    iVar12 = iVar1;
  }
  iVar2 = (int)((int)(int16_t)DAT_febe6f8e);
  iVar1 = (int)((int)(int16_t)DAT_febe6f42);
  if (iVar2 - iVar12 < 0 == (iVar2 < 0 != iVar12 < 0 && iVar12 < 0 == iVar2 - iVar12 < 0) &&
      iVar2 != iVar12) {
    iVar12 = iVar2;
  }
  iVar2 = (int)((int)(int16_t)DAT_febe6f9e);
  if (iVar2 - iVar12 < 0 == (iVar2 < 0 != iVar12 < 0 && iVar12 < 0 == iVar2 - iVar12 < 0) &&
      iVar2 != iVar12) {
    iVar12 = iVar2;
  }
  iVar2 = (int)((int)(int16_t)DAT_febe6f56);
  if (iVar2 - iVar1 < 0 == (iVar2 < 0 != iVar1 < 0 && iVar1 < 0 == iVar2 - iVar1 < 0) &&
      iVar2 != iVar1) {
    iVar1 = iVar2;
  }
  iVar3 = (int)((int)(int16_t)DAT_febe6f44);
  iVar2 = (int)((int)(int16_t)DAT_febe6ff0);
  if (iVar3 - iVar1 < 0 == (iVar3 < 0 != iVar1 < 0 && iVar1 < 0 == iVar3 - iVar1 < 0) &&
      iVar3 != iVar1) {
    iVar1 = iVar3;
  }
  iVar3 = (int)((int)(int16_t)DAT_febe6f58);
  if (iVar3 - iVar1 < 0 == (iVar3 < 0 != iVar1 < 0 && iVar1 < 0 == iVar3 - iVar1 < 0) &&
      iVar3 != iVar1) {
    iVar1 = iVar3;
  }
  iVar3 = (int)((int)(int16_t)DAT_febe7000);
  if (iVar3 - iVar2 < 0 == (iVar3 < 0 != iVar2 < 0 && iVar2 < 0 == iVar3 - iVar2 < 0) &&
      iVar3 != iVar2) {
    iVar2 = iVar3;
  }
  iVar3 = (int)((int)(int16_t)DAT_febe6ff2);
  if (iVar3 - iVar2 < 0 == (iVar3 < 0 != iVar2 < 0 && iVar2 < 0 == iVar3 - iVar2 < 0) &&
      iVar3 != iVar2) {
    iVar2 = iVar3;
  }
  iVar4 = (int)((int)(int16_t)DAT_febe7002);
  iVar3 = (int)((int)(int16_t)DAT_febe6f16);
  if (iVar4 - iVar2 < 0 == (iVar4 < 0 != iVar2 < 0 && iVar2 < 0 == iVar4 - iVar2 < 0) &&
      iVar4 != iVar2) {
    iVar2 = iVar4;
  }
  iVar4 = (int)((int)(int16_t)DAT_febe6f18);
  if (iVar4 - iVar3 < 0 == (iVar4 < 0 != iVar3 < 0 && iVar3 < 0 == iVar4 - iVar3 < 0) &&
      iVar4 != iVar3) {
    iVar3 = iVar4;
  }
  iVar5 = (int)((int)(int16_t)DAT_febe6eb4);
  iVar4 = (int)((int)(int16_t)DAT_febe6eb2);
  if (iVar5 - iVar4 < 0 == (iVar5 < 0 != iVar4 < 0 && iVar4 < 0 == iVar5 - iVar4 < 0) &&
      iVar5 != iVar4) {
    iVar4 = iVar5;
  }
  iVar5 = (int)((int)(int16_t)DAT_febe6eb6);
  if (iVar5 - iVar4 < 0 == (iVar5 < 0 != iVar4 < 0 && iVar4 < 0 == iVar5 - iVar4 < 0) &&
      iVar5 != iVar4) {
    iVar4 = iVar5;
  }
  iVar5 = (int)((int)(int16_t)DAT_febe6eb8);
  if (iVar5 - iVar4 < 0 == (iVar5 < 0 != iVar4 < 0 && iVar4 < 0 == iVar5 - iVar4 < 0) &&
      iVar5 != iVar4) {
    iVar4 = iVar5;
  }
  iVar5 = (int)((int)(int16_t)DAT_febe6eba);
  if (iVar5 - iVar4 < 0 == (iVar5 < 0 != iVar4 < 0 && iVar4 < 0 == iVar5 - iVar4 < 0) &&
      iVar5 != iVar4) {
    iVar4 = iVar5;
  }
  iVar5 = (int)((int)(int16_t)DAT_febe6ebc);
  if (iVar5 - iVar4 < 0 == (iVar5 < 0 != iVar4 < 0 && iVar4 < 0 == iVar5 - iVar4 < 0) &&
      iVar5 != iVar4) {
    iVar4 = iVar5;
  }
  interpolate_s16_axis_u16_values_7025c(((undefined *)camry_host_ptr(0x2fb64u)),iVar12,((uint16_t *)(stack_record_26)));
  interpolate_s16_axis_u16_values_7025c(((undefined *)camry_host_ptr(0x2fb78u)),iVar1,((uint16_t *)((stack_record_26 + 2))));
  interpolate_s16_axis_u16_values_7025c(((undefined *)camry_host_ptr(0x2fb8cu)),iVar2,((uint16_t *)((stack_record_26 + 4))));
  interpolate_s16_axis_u16_values_7025c(((undefined *)camry_host_ptr(0x2fba0u)),iVar3,((uint16_t *)((stack_record_26 + 6))));
  interpolate_s16_axis_u16_values_7025c(((undefined *)camry_host_ptr(0x2fbb4u)),iVar4,((uint16_t *)((stack_record_26 + 8))));
  uVar8 = (uint)(*((uint16_t *)(stack_record_26 + 0)));
  uVar9 = (uint)(*((uint16_t *)(stack_record_26 + 2)));
  uVar7 = 0x5a;
  uVar10 = (uint)(*((uint16_t *)(stack_record_26 + 4)));
  uVar11 = (uint)(*((uint16_t *)(stack_record_26 + 6)));
  uVar13 = (uint)(*((uint16_t *)(stack_record_26 + 8)));
  if (-1 < (int)(uVar9 - uVar8) && uVar9 != uVar8) {
    uVar8 = uVar9;
  }
  if (-1 < (int)(uVar10 - uVar8) && uVar10 != uVar8) {
    uVar8 = uVar10;
  }
  if (-1 < (int)(uVar11 - uVar8) && uVar11 != uVar8) {
    uVar8 = uVar11;
  }
  if (-1 < (int)(uVar13 - uVar8) && uVar13 != uVar8) {
    uVar8 = uVar13;
  }
  if (uVar8 < (uint)((int)uVar14 >> 1)) {
    uVar7 = 0xa5;
  }
  (*((short *)camry_host_ptr((uint32_t)((0xffffb7cau + (uint32_t)((int)puVar6)))))) = (short)iVar12;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb7ccu + (uint32_t)((int)puVar6)))))) = (short)iVar1;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb7ceu + (uint32_t)((int)puVar6)))))) = (short)iVar2;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb7d0u + (uint32_t)((int)puVar6)))))) = (short)iVar3;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb7d2u + (uint32_t)((int)puVar6)))))) = (short)iVar4;
  (*((ushort *)camry_host_ptr((uint32_t)((0xffffb7d4u + (uint32_t)((int)puVar6)))))) = (*((uint16_t *)(stack_record_26 + 0)));
  (*((ushort *)camry_host_ptr((uint32_t)((0xffffb7d6u + (uint32_t)((int)puVar6)))))) = (*((uint16_t *)(stack_record_26 + 2)));
  (*((ushort *)camry_host_ptr((uint32_t)((0xffffb7d8u + (uint32_t)((int)puVar6)))))) = (*((uint16_t *)(stack_record_26 + 4)));
  (*((ushort *)camry_host_ptr((uint32_t)((0xffffb7dau + (uint32_t)((int)puVar6)))))) = (*((uint16_t *)(stack_record_26 + 6)));
  (*((ushort *)camry_host_ptr((uint32_t)((0xffffb7dcu + (uint32_t)((int)puVar6)))))) = (*((uint16_t *)(stack_record_26 + 8)));
  (*((short *)camry_host_ptr((uint32_t)((0xffffb7deu + (uint32_t)((int)puVar6)))))) = (short)uVar8;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb7b2u + (uint32_t)((int)puVar6) * 1u)))) = (char)uVar7;
  return uVar7;
}

void return_only_stub_3acf6(void)

{
  return;
}

int clear_6fe0_if_588b6_returns_zero_3acf8(void)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  iVar2 = test_redundant_status_a5_or_vote_error13_588b6();
  if (iVar2 == 0) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb7e0u + (uint32_t)((int)puVar1) * 1u)))) = 0;
  }
  return iVar2;
}

uint should_zero_ecu_source3_thermal_seed(ushort record_marker)

{
  int iVar1;
  int threshold;
  uint uVar2;
  
  if ((DAT_febe7bf8 & 0xff) == 0) {
    if ((DAT_febe7bf8 & 0xff00) != 0) {
      DAT_febe6fe4 = (int)((int)(int16_t)DAT_febe7dd0) - (int)((int)(int16_t)DAT_febe7dce);
      iVar1 = (int)DAT_febe6fe4;
      goto LAB_0003ad54;
    }
  }
  else if ((DAT_febe7bf8 & 0xff00) == 0) {
    DAT_febe6fe8 = (int)((int)(int16_t)DAT_febe7dd8) - (int)((int)(int16_t)DAT_febe7dd6);
    iVar1 = (int)DAT_febe6fe8;
    goto LAB_0003ad54;
  }
  DAT_febe6fe4 = (int)((int)(int16_t)DAT_febe7dd0) - (int)((int)(int16_t)DAT_febe7dce);
  DAT_febe6fe8 = (int)((int)(int16_t)DAT_febe7dd8) - (int)((int)(int16_t)DAT_febe7dd6);
  iVar1 = (int)DAT_febe6fe4;
  if ((int)DAT_febe6fe8 - iVar1 < 0 !=
      ((int)DAT_febe6fe8 < 0 != iVar1 < 0 && iVar1 < 0 == (int)DAT_febe6fe8 - iVar1 < 0))
  {
    iVar1 = (int)DAT_febe6fe8;
  }
LAB_0003ad54:
  threshold = (int)DAT_0002b520;
  if ((iVar1 - threshold < 0 ==
       (iVar1 < 0 != threshold < 0 && threshold < 0 == iVar1 - threshold < 0) &&
       iVar1 != threshold) && (record_marker == 0)) {
    uVar2 = 0x5a;
  }
  else {
    uVar2 = 0;
  }
  return uVar2;
}

void restore_ecu_source3_thermal_model(void)

{
  uint8_t stack_record_4c[76];
  uint *puVar1;
  uint32_t puVar2;
  uint uVar3;
  undefined4 uVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  uchar *puVar9;
  
  puVar2 = 0xfebeb800u;
  puVar1 = ((uint32_t *)(stack_record_4c));
  puVar9 = (undefined *)camry_host_ptr(0x21220u);
  do {
    uVar4 = *(undefined4 *)puVar9;
    puVar9 = puVar9 + 4;
    *puVar1 = uVar4;
    puVar1 = puVar1 + 1;
  } while (camry_host_addr(puVar9)!=((uint32_t)(0x21258u)));
  uVar3 = nvm_get_record(6, camry_host_addr(((uint32_t *)(stack_record_4c))));
  iVar8 = (int)(*((int16_t *)(stack_record_4c + 36)));
  iVar6 = (int)(*((int16_t *)(stack_record_4c + 40)));
  iVar7 = (int)(*((int16_t *)(stack_record_4c + 38)));
  iVar5 = (int)(*((int16_t *)(stack_record_4c + 42)));
  if ((uVar3 == 0x10) && ((*((uint16_t *)(stack_record_4c + 50))) != 0xa55a)) {
    if ((((((*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x3c08)))) & 0xff) == 0) ||
         (((*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x3c08)))) & 0xff00) == 0)) && ((*((uint16_t *)(stack_record_4c + 50))) != 0x5aa5)) &&
       (uVar3 = should_zero_ecu_source3_thermal_seed((*((uint16_t *)(stack_record_4c + 50)))), uVar3 == 0x5a)) {
      iVar8 = 0;
      iVar6 = 0;
      iVar7 = 0;
      iVar5 = 0;
    }
  }
  else {
    iVar8 = (int)DAT_0002b532;
    iVar6 = (int)DAT_0002b54a;
    iVar7 = (int)DAT_0002b534;
    iVar5 = (int)DAT_0002b54c;
  }
  initialize_6ff4_calibrated_ratio_pair_3af8a(iVar8,iVar7);
  initialize_7004_calibrated_ratio_pair_3b0a2(iVar6,iVar5);
  return;
}

void update_ecu_source3_thermal_estimate(void)

{
  short upper;
  short lower;
  uint32_t puVar1;
  undefined2 uVar2;
  undefined *puVar3;
  int iVar5;
  int iVar6;
  char cVar7;
  uint32_t puVar4;
  puVar4 = 0xfebeb800u;
  puVar3 = ((undefined *)camry_host_ptr(0xfebeb800u));
  cVar7 = DAT_febe6fe0;
  puVar1 = (0xfebeb800u);
  if (DAT_febe6fe0 == '\0') {
    if ((DAT_febe7dcc != 'Z') || (DAT_febe7bf6 != 'Z')) goto LAB_0003ae5e;
    restore_ecu_source3_thermal_model();
    cVar7 = 'Z';
    puVar1 = ((uint32_t)(puVar4));
  }
  puVar3 = ((void *)camry_host_ptr((uint32_t)(puVar1)));
  lower = DAT_0002b51e;
  upper = DAT_0002b51c;
  iVar5 = update_ecu_source3_thermal_branch0(DAT_0002b51c,DAT_0002b51e);
  iVar6 = update_ecu_source3_thermal_branch1(upper,lower);
  if (iVar6 - iVar5 < 0 == (iVar6 < 0 != iVar5 < 0 && iVar5 < 0 == iVar6 - iVar5 < 0) &&
      iVar6 != iVar5) {
    uVar2 = (undefined2)iVar6;
  }
  else {
    uVar2 = (undefined2)iVar5;
  }
  *(undefined2 *)camry_host_ptr((uint32_t)(0xffffb7e2u + (uint32_t)camry_host_addr(puVar3))) = uVar2;
LAB_0003ae5e:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb7e0u + (uint32_t)((int)camry_host_addr(puVar3)) * 1u)))) = cVar7;
  return;
}

int compute_signed_ratio_q19_saturating_3ae66(short param_1,short param_2)

{
  int iVar1;
  int iVar2;
  
  iVar2 = (int)param_2;
  if (iVar2 == 0) {
    return 0;
  }
  iVar1 = (int)param_1 << 0xc;
  if (iVar2 != 0) {
    if (iVar1 == -0x80000000 && iVar2 == -1) {
      iVar1 = -0x80000000;
    }
    else {
      iVar1 = (int)iVar1 / (int)iVar2;
    }
  }
  if (iVar1 < 0) {
    iVar2 = (int)((ulonglong)((longlong)iVar1 * 0x80) >> 0x20) + 1;
    if ((iVar2 < 0 != (-1 < (longlong)iVar1 * 0x80 && iVar2 < 0)) ||
       ((uint)(iVar1 * 0x80) < 0x80000001)) {
      return -0x7fffffff;
    }
  }
  else {
    if (iVar1 == 0) {
      return 0;
    }
    if ((-1 < (longlong)iVar1 * 0x80 && (int)((ulonglong)((longlong)iVar1 * 0x80) >> 0x20) != 0) ||
       (0x7fffffff < (uint)(iVar1 * 0x80))) {
      return 0x7fffffff;
    }
  }
  return iVar1 * 0x80;
}

void return_only_stub_3aeb6(void)

{
  return;
}

int update_ecu_source3_thermal_branch0(short upper,short lower)

{
  short previous;
  int iVar1;
  uint32_t puVar2;
  uint base;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  uint scale;
  uint base_00;
  int iVar7;
  int iVar8;
  
  iVar4 = DAT_febe6ff8;
  iVar3 = DAT_febe6ff4;
  previous = ((int)(int16_t)DAT_febe6fec);
  iVar5 = ((int)(int32_t)DAT_febe6ef4);
  puVar2 = 0xfebeb800u;
  iVar7 = (int)lower;
  iVar8 = (int)upper;
  iVar1 = (int)((int)(int16_t)DAT_febe64e2);
  if (iVar1 + 0x7fff < 0 == (-1 < iVar1 && iVar1 + 0x7fff < 0) && iVar1 != -0x7fff) {
    if (iVar1 < 0) {
      iVar1 = (int)-((int)(int16_t)DAT_febe64e2);
    }
  }
  else {
    iVar1 = 0x7fff;
  }
  iVar6 = (int)DAT_0002b530;
  base = (uint)DAT_0002b52a;
  base_00 = (uint)DAT_0002b52c;
  if ((iVar1 - iVar6 < 0 == (iVar1 < 0 != iVar6 < 0 && iVar6 < 0 == iVar1 - iVar6 < 0) &&
       iVar1 != iVar6) &&
     (((int)(int32_t)DAT_febe6ef4) - DAT_0002b538 < 0 ==
      (((int)(int32_t)DAT_febe6ef4) < 0 != DAT_0002b538 < 0 && DAT_0002b538 < 0 == ((int)(int32_t)DAT_febe6ef4) - DAT_0002b538 < 0)
      && ((int)(int32_t)DAT_febe6ef4) != DAT_0002b538)) {
    scale = (uint)DAT_0002b52e;
    puVar2 = 0xfebeb800u;
    base = scale_thermal_divisor(base,scale);
    base_00 = scale_thermal_divisor(base_00,scale);
  }
  iVar3 = update_nonnegative_thermal_pole(iVar3,iVar5,base);
  iVar4 = update_nonnegative_thermal_pole(iVar4,iVar5,base_00);
  iVar1 = scale_thermal_contribution(iVar3,DAT_0002b524,upper,lower);
  iVar6 = scale_thermal_contribution(iVar4,DAT_0002b526,upper,lower);
  iVar5 = (int)DAT_0002b528 + iVar6 + iVar1;
  if (iVar5 - iVar8 < 0 != (iVar5 < 0 != iVar8 < 0 && iVar8 < 0 == iVar5 - iVar8 < 0) ||
      iVar5 == iVar8) {
    iVar8 = iVar5;
  }
  if (iVar8 - iVar7 < 0 == (iVar8 < 0 != iVar7 < 0 && iVar7 < 0 == iVar8 - iVar7 < 0)) {
    iVar7 = iVar8;
  }
  iVar5 = apply_thermal_offset_and_following(4,(short)iVar7,previous);
  (*((short *)camry_host_ptr((uint32_t)((0xffffb7eeu + (uint32_t)((int)puVar2)))))) = (short)iVar7;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb7ecu + (uint32_t)((int)puVar2)))))) = (short)iVar5;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb7f0u + (uint32_t)((int)puVar2)))))) = (short)iVar1;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb7f2u + (uint32_t)((int)puVar2)))))) = (short)iVar6;
  (*((int *)camry_host_ptr((uint32_t)((0xffffb7f4u + (uint32_t)((int)puVar2)))))) = iVar3;
  (*((int *)camry_host_ptr((uint32_t)((0xffffb7f8u + (uint32_t)((int)puVar2)))))) = iVar4;
  return iVar5;
}

void initialize_6ff4_calibrated_ratio_pair_3af8a(short param_1,short param_2)

{
  uint32_t puVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  
  puVar1 = 0xfebeb800u;
  uVar2 = compute_signed_ratio_q19_saturating_3ae66((int)param_1,(int)DAT_0002b524);
  uVar3 = compute_signed_ratio_q19_saturating_3ae66((int)param_2,(int)DAT_0002b526);
  (*((undefined4 *)camry_host_ptr((uint32_t)((0xffffb7f4u + (uint32_t)((int)puVar1)))))) = uVar2;
  (*((undefined4 *)camry_host_ptr((uint32_t)((0xffffb7f8u + (uint32_t)((int)puVar1)))))) = uVar3;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb7ecu + (uint32_t)((int)puVar1)))))) = 0x3480;
  return;
}

void clear_6ff0_pair_and_6ff4_ratio_states_3afc0(void)

{
  DAT_febe6ff0 = 0;
  DAT_febe6ff2 = 0;
  DAT_febe6ff4 = 0;
  DAT_febe6ff8 = 0;
  return;
}

void return_only_stub_3afce(void)

{
  return;
}

int update_ecu_source3_thermal_branch1(short upper,short lower)

{
  short previous;
  int iVar1;
  uint32_t puVar2;
  uint base;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  uint scale;
  uint base_00;
  int iVar7;
  int iVar8;
  
  iVar4 = DAT_febe7008;
  iVar3 = DAT_febe7004;
  previous = ((int)(int16_t)DAT_febe6ffc);
  iVar5 = ((int)(int32_t)DAT_febe6ef8);
  puVar2 = 0xfebeb800u;
  iVar7 = (int)lower;
  iVar8 = (int)upper;
  iVar1 = (int)((int)(int16_t)DAT_febe64e2);
  if (iVar1 + 0x7fff < 0 == (-1 < iVar1 && iVar1 + 0x7fff < 0) && iVar1 != -0x7fff) {
    if (iVar1 < 0) {
      iVar1 = (int)-((int)(int16_t)DAT_febe64e2);
    }
  }
  else {
    iVar1 = 0x7fff;
  }
  iVar6 = (int)DAT_0002b548;
  base = (uint)DAT_0002b542;
  base_00 = (uint)DAT_0002b544;
  if ((iVar1 - iVar6 < 0 == (iVar1 < 0 != iVar6 < 0 && iVar6 < 0 == iVar1 - iVar6 < 0) &&
       iVar1 != iVar6) &&
     (((int)(int32_t)DAT_febe6ef8) - DAT_0002b550 < 0 ==
      (((int)(int32_t)DAT_febe6ef8) < 0 != DAT_0002b550 < 0 && DAT_0002b550 < 0 == ((int)(int32_t)DAT_febe6ef8) - DAT_0002b550 < 0)
      && ((int)(int32_t)DAT_febe6ef8) != DAT_0002b550)) {
    scale = (uint)DAT_0002b546;
    puVar2 = 0xfebeb800u;
    base = scale_thermal_divisor(base,scale);
    base_00 = scale_thermal_divisor(base_00,scale);
  }
  iVar3 = update_nonnegative_thermal_pole(iVar3,iVar5,base);
  iVar4 = update_nonnegative_thermal_pole(iVar4,iVar5,base_00);
  iVar1 = scale_thermal_contribution(iVar3,DAT_0002b53c,upper,lower);
  iVar6 = scale_thermal_contribution(iVar4,DAT_0002b53e,upper,lower);
  iVar5 = (int)DAT_0002b540 + iVar6 + iVar1;
  if (iVar5 - iVar8 < 0 != (iVar5 < 0 != iVar8 < 0 && iVar8 < 0 == iVar5 - iVar8 < 0) ||
      iVar5 == iVar8) {
    iVar8 = iVar5;
  }
  if (iVar8 - iVar7 < 0 == (iVar8 < 0 != iVar7 < 0 && iVar7 < 0 == iVar8 - iVar7 < 0)) {
    iVar7 = iVar8;
  }
  iVar5 = apply_thermal_offset_and_following(5,(short)iVar7,previous);
  (*((short *)camry_host_ptr((uint32_t)((0xffffb7feu + (uint32_t)((int)puVar2)))))) = (short)iVar7;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb7fcu + (uint32_t)((int)puVar2)))))) = (short)iVar5;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb800u + (uint32_t)((int)puVar2)))))) = (short)iVar1;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb802u + (uint32_t)((int)puVar2)))))) = (short)iVar6;
  (*((int *)camry_host_ptr((uint32_t)((0xffffb804u + (uint32_t)((int)puVar2)))))) = iVar3;
  (*((int *)camry_host_ptr((uint32_t)((0xffffb808u + (uint32_t)((int)puVar2)))))) = iVar4;
  return iVar5;
}
