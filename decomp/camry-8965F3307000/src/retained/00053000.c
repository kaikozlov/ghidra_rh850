#include "common.h"

void reset_first_third_captures_and_selectively_reset_second_53092(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe6150 = 0xaa;
  DAT_febe615a = 0x5a;
  DAT_febe6166 = 0;
  DAT_febe6151 = 0;
  copy_diagnostic_capture(diagnostic_capture_slots,(F33DiagnosticCapture *)((undefined *)camry_host_ptr(0x2a1f4u)));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x56ac))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x56ac))))) | 4;
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x337d))))) == '\"') {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x56ae))))) = 0;
    copy_diagnostic_capture
              (((F33DiagnosticCapture *)camry_host_ptr((uint32_t)(puVar1 + -0x3434))),(F33DiagnosticCapture *)((undefined *)camry_host_ptr(0x2a1f4u)));
  }
  else {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x337d))))) = 0x44;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x56ab))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x56ab))))) | 4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x56ad))))) = 0;
  copy_diagnostic_capture
            (((F33DiagnosticCapture *)camry_host_ptr((uint32_t)(puVar1 + -0x3344))),(F33DiagnosticCapture *)((undefined *)camry_host_ptr(0x2a1f4u)));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x56aa))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x56aa))))) | 4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x56b0))))) = 0xa5;
  return;
}

void set_diagnostic_cache_blocker(uchar index,uchar status)

{
  if (index < 0xb) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe615bu + (uint32_t)(index) * 1u)))) = status;
  }
  return;
}

uint get_secondary_capture_record_mask(uint *dtc)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  
  uVar2 = 0;
  if ((camry_host_addr((dtc))!= 0) && (DAT_febe6152 == '\x01')) {
    uVar1 = 0;
    if ((*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe82dcu + (uint32_t)(1) * (uint32_t)sizeof(F33DiagnosticCapture)) + (uint32_t)(0) * (uint32_t)sizeof(F33DiagnosticCapture) + (uint32_t)offsetof(F33DiagnosticCapture, event))))) < 0x180) {
      uVar1 = *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x30850u + (uint32_t)((uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2fc52u + (uint32_t)((uint)(*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe82dcu + (uint32_t)(1) * (uint32_t)sizeof(F33DiagnosticCapture)) + (uint32_t)(0) * (uint32_t)sizeof(F33DiagnosticCapture) + (uint32_t)offsetof(F33DiagnosticCapture, event))))) * 8) * 1u))))
                       * 8) * 1u))));
    }
    uVar3 = 0;
    if ((*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe82dcu + (uint32_t)(1) * (uint32_t)sizeof(F33DiagnosticCapture)) + (uint32_t)(0) * (uint32_t)sizeof(F33DiagnosticCapture) + (uint32_t)offsetof(F33DiagnosticCapture, event_copy))))) < 0x180) {
      uVar3 = *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x30850u + (uint32_t)((uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2fc52u + (uint32_t)((uint)(*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe82dcu + (uint32_t)(1) * (uint32_t)sizeof(F33DiagnosticCapture)) + (uint32_t)(0) * (uint32_t)sizeof(F33DiagnosticCapture) + (uint32_t)offsetof(F33DiagnosticCapture, event_copy))))) * 8) * 1u)))) * 8) * 1u))));
    }
    if ((uVar1 == uVar3) && (uVar1 != 0)) {
      *dtc = uVar1;
      uVar2 = 3;
    }
  }
  return uVar2;
}

undefined4 validate_retained_capture_read_arguments_53168(int param_1,int param_2,ushort param_3,undefined1 *param_4)

{
  undefined1 uVar1;
  undefined4 uVar2;
  
  uVar2 = 0;
  if (((param_2 == 0) || (DAT_febe6152 != '\x01')) || (param_1 == 0)) {
    uVar1 = 1;
  }
  else if (param_3 < 2) {
    uVar1 = 2;
    uVar2 = 0xffffffff;
  }
  else {
    uVar1 = 0;
    uVar2 = 0;
  }
  *param_4 = uVar1;
  return uVar2;
}

undefined4 test_capture_field_descriptor_and_availability_53190(uint param_1,char param_2)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  ushort uStack_12;
  
  uVar2 = 0;
  iVar1 = camry_host_addr(get_capture_field_descriptors_and_count_56664(&uStack_12));
  if ((param_1 & 0xffff) < (uint)uStack_12) {
    iVar1 = (param_1 & 0xffff) * 0x18 + iVar1;
    iVar3 = iVar1;
    if (param_2 != '\0') {
      iVar3 = iVar1 + 8;
    }
    if ((*((int *)camry_host_ptr((uint32_t)(iVar3 + 4)))) != 0) {
      uVar2 = 0x5a;
      if ((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(iVar1 + 0x10))))) != 0u) {
        uVar2 = (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(iVar1 + 0x10))))))))))))();
      }
    }
  }
  return uVar2;
}

int serialize_retained_capture_record(uchar record_view,uchar *output,ushort capacity)

{
  undefined2 *puVar1;
  uchar *puVar2;
  uchar uVar3;
  int iVar4;
  int iVar5;
  uchar uVar6;
  uint uVar7;
  int iVar8;
  ushort uStack_2a;
  
  iVar8 = 0;
  uVar6 = '\0';
  if (((record_view < 2) && (camry_host_addr((output))!= 0)) &&
     (iVar4 = camry_host_addr(get_capture_field_descriptors_and_count_56664(&uStack_2a)), iVar4 != 0)) {
    uVar3 = '\x10';
    if (record_view == '\0') {
      uVar3 = '\x01';
    }
    iVar8 = 2;
    *output = uVar3;
    for (uVar7 = 0; uVar7 < uStack_2a; uVar7 = uVar7 + 1 & 0xffff) {
      if ((record_view == '\0') || ((*((char *)camry_host_ptr((uint32_t)(uVar7 * 0x18 + iVar4 + 2)))) == '\0')) {
        puVar1 = ((undefined2 *)camry_host_ptr((uint32_t)(uVar7 * 0x18 + iVar4)));
        iVar5 = (uint)*(byte *)(puVar1 + 0xb) + iVar8 + 3;
        if ((int)((uint)capacity - iVar5) < 0 !=
            (iVar5 < 0 && iVar5 < 0 == (int)((uint)capacity - iVar5) < 0)) {
          iVar8 = -1;
          break;
        }
        iVar5 = test_capture_field_descriptor_and_availability_53190(uVar7,0);
        if (iVar5 == 0x5a) {
          puVar2 = output + iVar8;
          uVar6 = uVar6 + '\x01';
          store_low_u16_big_endian_bytes_6a574(*puVar1,puVar2);
          puVar2[2] = *(uchar *)(puVar1 + 0xb);
          (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)(puVar1 + 2)))))))))))(record_view,camry_host_addr(puVar2 + 3));
          iVar8 = iVar8 + (uint)*(byte *)(puVar1 + 0xb) + 3;
        }
      }
    }
    output[1] = uVar6;
  }
  return iVar8;
}

uint32_t serialize_matching_retained_capture_record_view_53298(undefined4 param_1,char param_2,undefined4 param_3,ushort param_4)

{
  uint32_t camry_r10_result;
  int iVar1;
  uint32_t puVar2;
  uchar record_view;
  int extraout_r6;
  uchar *output;
  int iVar3;
  char acStack_15 [9];
  
  puVar2 = 0xfebeb800u;
  (camry_r10_result = validate_retained_capture_read_arguments_53168((extraout_r6 = param_1),param_3,param_4,acStack_15));
  if (acStack_15[0] == '\0') {
    iVar1 = 0;
    if ((*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x33a4)))) < 0x180) {
      iVar1 = *(int *)(((undefined *)camry_host_ptr((uint32_t)(0x30850u + (uint32_t)((uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2fc52u + (uint32_t)((uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x33a4)))) * 8) * 1u)))) * 8) * 1u))));
    }
    iVar3 = 0;
    if ((*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x33a2)))) < 0x180) {
      iVar3 = *(int *)(((undefined *)camry_host_ptr((uint32_t)(0x30850u + (uint32_t)((uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2fc52u + (uint32_t)((uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x33a2)))) * 8) * 1u)))) * 8) * 1u))));
    }
    if ((iVar1 == iVar3) && (((int)(param_1)) == iVar1)) {
      if (param_2 == '\x01') {
        record_view = '\0';
      }
      else {
        if (param_2 != '\x10') {
          return camry_r10_result;
        }
        record_view = '\x01';
      }
      (camry_r10_result = serialize_retained_capture_record(record_view, ((uchar *)camry_host_ptr((uint32_t)(param_3))), param_4));
    }
  }
  return camry_r10_result;
}

void capture_slot_dispatch_53316(undefined4 param_1,int param_2)

{
  bool bVar1;
  undefined2 uVar2;
  undefined4 uVar3;
  
  uVar2 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * 240u + 186u))));
  if (0xfffe < (ushort)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * 240u + 186u))))) {
    (*((uint8_t *)((uint8_t *)&uVar2 + 0u))) = 0xff;
    (*((uint8_t *)((uint8_t *)&uVar2 + 1u))) = 0xff;
  }
  uVar3 = (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * 240u + 188u))));
  if ((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * 240u + 188u)))) == -1) {
    (*((uint8_t *)((uint8_t *)&uVar3 + 0u))) = 0xff;
    (*((uint8_t *)((uint8_t *)&uVar3 + 1u))) = 0xff;
    (*((uint8_t *)((uint8_t *)&uVar3 + 2u))) = 0xff;
    (*((uint8_t *)((uint8_t *)&uVar3 + 3u))) = 0xff;
  }
  bVar1 = ((volatile F33DiagnosticCapture *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * (uint32_t)sizeof(F33DiagnosticCapture))))[0].extended_middle[6] != '\0';
  store_low_u16_big_endian_bytes_6a574(uVar2, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  store_u32_big_endian_bytes_6a55c(uVar3, ((undefined1 *)camry_host_ptr((uint32_t)(param_2 + 2))));
  (*((bool *)camry_host_ptr((uint32_t)(param_2 + 6)))) = bVar1;
  return;
}

void capture_slot_dispatch_53354(undefined4 param_1,uchar *param_2)

{
  undefined4 uVar1;
  uchar uVar2;
  
  uVar1 = (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * 240u + 200u))));
  if (0xf423fu < (uint)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * 240u + 200u))))) {
    (*((uint8_t *)((uint8_t *)&uVar1 + 0u))) = '\0';
    (*((uint8_t *)((uint8_t *)&uVar1 + 1u))) = '\0';
    (*((uint8_t *)((uint8_t *)&uVar1 + 2u))) = '\0';
    (*((uint8_t *)((uint8_t *)&uVar1 + 3u))) = '\0';
  }
  uVar2 = ((volatile F33DiagnosticCapture *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * (uint32_t)sizeof(F33DiagnosticCapture))))[0].extended_middle[7];
  if (1 < ((volatile F33DiagnosticCapture *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * (uint32_t)sizeof(F33DiagnosticCapture))))[0].extended_middle[7]) {
    uVar2 = '\x02';
  }
  store_u32_big_endian_bytes_6a55c(uVar1, param_2);
  *param_2 = uVar2;
  return;
}

void capture_slot_dispatch_533a0(ushort param_1, undefined4 param_2)

{
  uint uVar1;
  
  uVar1 = (uint)(*((ushort *)camry_host_ptr((uint32_t)(camry_host_addr(((volatile F33DiagnosticCapture *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * (uint32_t)sizeof(F33DiagnosticCapture))))[0].profile_prefix) + (short)(param_1 & 0xff) * 0x48 + 0x38)))) * 10 >> 7;
  if (2999 < uVar1) {
    uVar1 = 3000;
  }
  store_low_u16_big_endian_bytes_6a574(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}

void capture_slot_dispatch_533cc(ushort param_1, undefined4 param_2)

{
  ushort uVar1;
  
  uVar1 = (*((ushort *)camry_host_ptr((uint32_t)(camry_host_addr(((volatile F33DiagnosticCapture *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * (uint32_t)sizeof(F33DiagnosticCapture))))[0].profile_prefix) + (short)(param_1 & 0xff) * 0x48 + 0x3a))));
  if (0x31ff < uVar1) {
    uVar1 = 0x3200;
  }
  store_low_u16_big_endian_bytes_6a574(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}

void capture_slot_dispatch_53408(ushort param_1, undefined4 param_2)

{
  uint uVar1;
  
  uVar1 = (uint)(*((ushort *)camry_host_ptr((uint32_t)(camry_host_addr(((volatile F33DiagnosticCapture *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * (uint32_t)sizeof(F33DiagnosticCapture))))[0].profile_prefix) + (short)(param_1 & 0xff) * 0x48 + 0x3e)))) * 100 >> 8;
  if (0x9c3 < uVar1) {
    uVar1 = 0x9c4;
  }
  store_low_u16_big_endian_bytes_6a574(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}

void capture_slot_dispatch_53434(ushort param_1, undefined4 param_2)

{
  int iVar1;
  
  iVar1 = ((*((short *)camry_host_ptr((uint32_t)(camry_host_addr(((volatile F33DiagnosticCapture *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * (uint32_t)sizeof(F33DiagnosticCapture))))[0].profile_prefix) + (short)(param_1 & 0xff) * 0x48 + 0xc)))) * 1000) / 0x100;
  if (iVar1 + -25000 < 0 == (iVar1 < 0 && -1 < iVar1 + -25000)) {
    iVar1 = 25000;
  }
  if (iVar1 + 25000 < 0 != (-1 < iVar1 && iVar1 + 25000 < 0)) {
    iVar1 = -25000;
  }
  store_low_u16_big_endian_bytes_6a5ac((int)(short)iVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}

void capture_slot_dispatch_53470(ushort param_1, undefined4 param_2)

{
  int iVar1;
  
  iVar1 = (int)(short)(((*((short *)camry_host_ptr((uint32_t)(camry_host_addr(((volatile F33DiagnosticCapture *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * (uint32_t)sizeof(F33DiagnosticCapture))))[0].profile_prefix) + (short)(param_1 & 0xff) * 0x48 + 8)))) * 0x168) / 0x400);
  if (iVar1 + -0x7fff < 0 == (iVar1 < 0 && -1 < iVar1 + -0x7fff)) {
    iVar1 = 0x7fff;
  }
  if (iVar1 + 0x7fff < 0 != (-1 < iVar1 && iVar1 + 0x7fff < 0)) {
    iVar1 = -0x7fff;
  }
  store_low_u16_big_endian_bytes_6a5ac(iVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}

void capture_slot_dispatch_534ac(ushort param_1, undefined4 param_2)

{
  int iVar1;
  
  iVar1 = (int)(*((short *)camry_host_ptr((uint32_t)(camry_host_addr(((volatile F33DiagnosticCapture *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * (uint32_t)sizeof(F33DiagnosticCapture))))[0].profile_prefix) + (short)(param_1 & 0xff) * 0x48 + 0x40))));
  if (iVar1 + -0x7ff < 0 == (iVar1 < 0 && -1 < iVar1 + -0x7ff)) {
    iVar1 = 0x7ff;
  }
  if (iVar1 + 0x800 < 0 != (-1 < iVar1 && iVar1 + 0x800 < 0)) {
    iVar1 = -0x800;
  }
  store_low_u16_big_endian_bytes_6a5ac(iVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}

void capture_slot_dispatch_534da(ushort param_1, undefined4 param_2)

{
  uint uVar1;
  
  uVar1 = (uint)(*((ushort *)camry_host_ptr((uint32_t)(camry_host_addr(((volatile F33DiagnosticCapture *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * (uint32_t)sizeof(F33DiagnosticCapture))))[0].profile_prefix) + (short)(param_1 & 0xff) * 0x48 + 10)))) * 100 >> 8;
  if (0x9c3 < uVar1) {
    uVar1 = 0x9c4;
  }
  store_low_u16_big_endian_bytes_6a574(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}

void capture_slot_dispatch_53506(ushort param_1, undefined4 param_2)

{
  uint uVar1;
  
  uVar1 = (uint)(*((ushort *)camry_host_ptr((uint32_t)(camry_host_addr(((volatile F33DiagnosticCapture *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * (uint32_t)sizeof(F33DiagnosticCapture))))[0].profile_prefix) + (short)(param_1 & 0xff) * 0x48 + 0x36)))) * 100 >> 8;
  if (0x9c3 < uVar1) {
    uVar1 = 0x9c4;
  }
  store_low_u16_big_endian_bytes_6a574(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}

int scale_s16_by10_over128_clamp_minus500_to2000_53532(short param_1)

{
  int iVar1;
  
  iVar1 = (int)(short)((param_1 * 10) / 0x80);
  if (iVar1 + -2000 < 0 == (iVar1 < 0 && -1 < iVar1 + -2000)) {
    iVar1 = 2000;
  }
  if (iVar1 + 500 < 0 != (-1 < iVar1 && iVar1 + 500 < 0)) {
    iVar1 = -500;
  }
  return iVar1;
}

undefined4 capture_slot_dispatch_53558(undefined4 param_1, undefined4 param_2)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  
  iVar1 = (int)(short)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * 240u + 222u))));
  iVar3 = (int)(short)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * 240u + 150u))));
  if (iVar1 - iVar3 < 0 == (iVar1 < 0 != iVar3 < 0 && iVar3 < 0 == iVar1 - iVar3 < 0) &&
      iVar1 != iVar3) {
    iVar3 = iVar1;
  }
  uVar2 = scale_s16_by10_over128_clamp_minus500_to2000_53532(iVar3);
  store_low_u16_big_endian_bytes_6a5ac(uVar2, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return uVar2;
}

void capture_slot_dispatch_53578(undefined4 param_1, undefined4 param_2)

{
  undefined4 uVar1;
  
  uVar1 = 0x7fff;
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe82dcu + (uint32_t)(1) * (uint32_t)sizeof(F33DiagnosticCapture)) + (uint32_t)(0) * (uint32_t)sizeof(F33DiagnosticCapture) + (uint32_t)offsetof(F33DiagnosticCapture, ecu_thermal_source))))) != '\0') {
    uVar1 = scale_s16_by10_over128_clamp_minus500_to2000_53532((int)(*((volatile int16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe82dcu + (uint32_t)(1) * (uint32_t)sizeof(F33DiagnosticCapture)) + (uint32_t)(0) * (uint32_t)sizeof(F33DiagnosticCapture) + (uint32_t)offsetof(F33DiagnosticCapture, ecu_thermal_estimate))))));
  }
  store_low_u16_big_endian_bytes_6a5ac(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}

void capture_slot_dispatch_5359a(undefined4 param_1, undefined4 param_2)

{
  undefined4 uVar1;
  
  uVar1 = 0x7fff;
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe82dcu + (uint32_t)(1) * (uint32_t)sizeof(F33DiagnosticCapture)) + (uint32_t)(0) * (uint32_t)sizeof(F33DiagnosticCapture) + (uint32_t)offsetof(F33DiagnosticCapture, motor_thermal_active))))) != '\0') {
    uVar1 = scale_s16_by10_over128_clamp_minus500_to2000_53532((int)(*((volatile int16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe82dcu + (uint32_t)(1) * (uint32_t)sizeof(F33DiagnosticCapture)) + (uint32_t)(0) * (uint32_t)sizeof(F33DiagnosticCapture) + (uint32_t)offsetof(F33DiagnosticCapture, motor_thermal_estimate))))));
  }
  store_low_u16_big_endian_bytes_6a5ac(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}

int scale_s16_by1000_over256_clamp_25000_53608(short param_1)

{
  int iVar1;
  
  iVar1 = (param_1 * 1000) / 0x100;
  if (iVar1 + -25000 < 0 == (iVar1 < 0 && -1 < iVar1 + -25000)) {
    iVar1 = 25000;
  }
  if (iVar1 + 25000 < 0 != (-1 < iVar1 && iVar1 + 25000 < 0)) {
    iVar1 = -25000;
  }
  return (int)(short)iVar1;
}

undefined4 capture_slot_dispatch_5362e(undefined4 param_1, undefined4 param_2)

{
  undefined4 uVar1;
  
  uVar1 = scale_s16_by1000_over256_clamp_25000_53608((int)(short)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * 240u + 164u)))));
  store_low_u16_big_endian_bytes_6a5ac(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return uVar1;
}

undefined4 capture_slot_dispatch_53644(undefined4 param_1, undefined4 param_2)

{
  undefined4 uVar1;
  
  uVar1 = scale_s16_by1000_over256_clamp_25000_53608((int)(short)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * 240u + 166u)))));
  store_low_u16_big_endian_bytes_6a5ac(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return uVar1;
}

undefined4 capture_slot_dispatch_5365a(undefined4 param_1, undefined4 param_2)

{
  undefined4 uVar1;
  
  uVar1 = scale_s16_by1000_over256_clamp_25000_53608((int)(short)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * 240u + 168u)))));
  store_low_u16_big_endian_bytes_6a5ac(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return uVar1;
}

undefined4 capture_slot_dispatch_53670(undefined4 param_1, undefined4 param_2)

{
  undefined4 uVar1;
  
  uVar1 = scale_s16_by1000_over256_clamp_25000_53608((int)(short)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * 240u + 170u)))));
  store_low_u16_big_endian_bytes_6a5ac(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return uVar1;
}

int scale_s16_by100_over128_clamp_symmetric32767_53686(short param_1)

{
  int iVar1;
  
  iVar1 = (int)(short)((param_1 * 100) / 0x80);
  if (iVar1 + -0x7fff < 0 == (iVar1 < 0 && -1 < iVar1 + -0x7fff)) {
    iVar1 = 0x7fff;
  }
  if (iVar1 + 0x7fff < 0 != (-1 < iVar1 && iVar1 + 0x7fff < 0)) {
    iVar1 = -0x7fff;
  }
  return iVar1;
}

undefined4 capture_slot_dispatch_536ac(ushort param_1, undefined4 param_2)

{
  undefined4 uVar1;
  
  uVar1 = scale_s16_by100_over128_clamp_symmetric32767_53686((int)(*((short *)camry_host_ptr((uint32_t)(camry_host_addr(((volatile F33DiagnosticCapture *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * (uint32_t)sizeof(F33DiagnosticCapture))))[0].profile_prefix) + (short)(param_1 & 0xff) * 0x48 + 0x1c)))));
  store_low_u16_big_endian_bytes_6a5ac(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return uVar1;
}

undefined4 capture_slot_dispatch_536ca(ushort param_1, undefined4 param_2)

{
  undefined4 uVar1;
  
  uVar1 = scale_s16_by100_over128_clamp_symmetric32767_53686((int)(*((short *)camry_host_ptr((uint32_t)(camry_host_addr(((volatile F33DiagnosticCapture *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * (uint32_t)sizeof(F33DiagnosticCapture))))[0].profile_prefix) + (short)(param_1 & 0xff) * 0x48 + 0x1e)))));
  store_low_u16_big_endian_bytes_6a5ac(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return uVar1;
}

undefined4 capture_slot_dispatch_536e8(ushort param_1, undefined4 param_2)

{
  undefined4 uVar1;
  
  uVar1 = scale_s16_by100_over128_clamp_symmetric32767_53686((int)(*((short *)camry_host_ptr((uint32_t)(camry_host_addr(((volatile F33DiagnosticCapture *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * (uint32_t)sizeof(F33DiagnosticCapture))))[0].profile_prefix) + (short)(param_1 & 0xff) * 0x48 + 0x20)))));
  store_low_u16_big_endian_bytes_6a5ac(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return uVar1;
}

uint scale_u16_by625_over2048_cap10000_53706(uint param_1)

{
  uint uVar1;
  
  uVar1 = (param_1 & 0xffff) * 0x271 >> 0xb;
  if (9999 < uVar1) {
    uVar1 = 10000;
  }
  return uVar1;
}

undefined4 capture_slot_dispatch_53722(ushort param_1, undefined4 param_2)

{
  undefined4 uVar1;
  
  uVar1 = scale_u16_by625_over2048_cap10000_53706((*((undefined2 *)camry_host_ptr((uint32_t)(camry_host_addr(((volatile F33DiagnosticCapture *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * (uint32_t)sizeof(F33DiagnosticCapture))))[0].profile_prefix) + (short)(param_1 & 0xff) * 0x48 + 0x28)))));
  store_low_u16_big_endian_bytes_6a574(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return uVar1;
}

undefined4 capture_slot_dispatch_53740(ushort param_1, undefined4 param_2)

{
  undefined4 uVar1;
  
  uVar1 = scale_u16_by625_over2048_cap10000_53706((*((undefined2 *)camry_host_ptr((uint32_t)(camry_host_addr(((volatile F33DiagnosticCapture *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * (uint32_t)sizeof(F33DiagnosticCapture))))[0].profile_prefix) + (short)(param_1 & 0xff) * 0x48 + 0x2a)))));
  store_low_u16_big_endian_bytes_6a574(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return uVar1;
}

undefined4 capture_slot_dispatch_5375e(ushort param_1, undefined4 param_2)

{
  undefined4 uVar1;
  
  uVar1 = scale_u16_by625_over2048_cap10000_53706((*((undefined2 *)camry_host_ptr((uint32_t)(camry_host_addr(((volatile F33DiagnosticCapture *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * (uint32_t)sizeof(F33DiagnosticCapture))))[0].profile_prefix) + (short)(param_1 & 0xff) * 0x48 + 0x2c)))));
  store_low_u16_big_endian_bytes_6a574(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return uVar1;
}

uint scale_u16_by100_over256_cap10000_5377c(uint param_1)

{
  uint uVar1;
  
  uVar1 = (param_1 & 0xffff) * 100 >> 8;
  if (9999 < uVar1) {
    uVar1 = 10000;
  }
  return uVar1;
}

undefined4 capture_slot_dispatch_53794(ushort param_1, undefined4 param_2)

{
  undefined4 uVar1;
  
  uVar1 = scale_u16_by100_over256_cap10000_5377c((*((undefined2 *)camry_host_ptr((uint32_t)(camry_host_addr(((volatile F33DiagnosticCapture *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * (uint32_t)sizeof(F33DiagnosticCapture))))[0].profile_prefix) + (short)(param_1 & 0xff) * 0x48 + 0x10)))));
  store_low_u16_big_endian_bytes_6a574(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return uVar1;
}

undefined4 capture_slot_dispatch_537b2(ushort param_1, undefined4 param_2)

{
  undefined4 uVar1;
  
  uVar1 = scale_u16_by100_over256_cap10000_5377c((*((undefined2 *)camry_host_ptr((uint32_t)(camry_host_addr(((volatile F33DiagnosticCapture *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * (uint32_t)sizeof(F33DiagnosticCapture))))[0].profile_prefix) + (short)(param_1 & 0xff) * 0x48 + 0x12)))));
  store_low_u16_big_endian_bytes_6a574(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return uVar1;
}

undefined4 capture_slot_dispatch_537d0(ushort param_1, undefined4 param_2)

{
  undefined4 uVar1;
  
  uVar1 = scale_u16_by100_over256_cap10000_5377c((*((undefined2 *)camry_host_ptr((uint32_t)(camry_host_addr(((volatile F33DiagnosticCapture *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * (uint32_t)sizeof(F33DiagnosticCapture))))[0].profile_prefix) + (short)(param_1 & 0xff) * 0x48 + 0x14)))));
  store_low_u16_big_endian_bytes_6a574(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return uVar1;
}

void capture_slot_dispatch_537ee(ushort param_1, undefined4 param_2)

{
  uint uVar1;
  
  uVar1 = (uint)(*((ushort *)camry_host_ptr((uint32_t)(camry_host_addr(((volatile F33DiagnosticCapture *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * (uint32_t)sizeof(F33DiagnosticCapture))))[0].profile_prefix) + (short)(param_1 & 0xff) * 0x48 + 0x34)))) * 100 >> 8;
  if (0x9c3 < uVar1) {
    uVar1 = 0x9c4;
  }
  store_low_u16_big_endian_bytes_6a574(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}

undefined4 capture_slot_dispatch_5381a(ushort param_1, undefined4 param_2)

{
  undefined4 uVar1;
  
  uVar1 = scale_s16_by100_over128_clamp_symmetric32767_53686((int)(*((short *)camry_host_ptr((uint32_t)(camry_host_addr(((volatile F33DiagnosticCapture *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * (uint32_t)sizeof(F33DiagnosticCapture))))[0].profile_prefix) + (short)(param_1 & 0xff) * 0x48 + 0x22)))));
  store_low_u16_big_endian_bytes_6a5ac(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return uVar1;
}

undefined4 capture_slot_dispatch_53838(ushort param_1, undefined4 param_2)

{
  undefined4 uVar1;
  
  uVar1 = scale_s16_by100_over128_clamp_symmetric32767_53686((int)(*((short *)camry_host_ptr((uint32_t)(camry_host_addr(((volatile F33DiagnosticCapture *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * (uint32_t)sizeof(F33DiagnosticCapture))))[0].profile_prefix) + (short)(param_1 & 0xff) * 0x48 + 0x24)))));
  store_low_u16_big_endian_bytes_6a5ac(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return uVar1;
}

undefined4 capture_slot_dispatch_53856(ushort param_1, undefined4 param_2)

{
  undefined4 uVar1;
  
  uVar1 = scale_s16_by100_over128_clamp_symmetric32767_53686((int)(*((short *)camry_host_ptr((uint32_t)(camry_host_addr(((volatile F33DiagnosticCapture *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * (uint32_t)sizeof(F33DiagnosticCapture))))[0].profile_prefix) + (short)(param_1 & 0xff) * 0x48 + 0x26)))));
  store_low_u16_big_endian_bytes_6a5ac(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return uVar1;
}

undefined4 capture_slot_dispatch_53874(ushort param_1, undefined4 param_2)

{
  undefined4 uVar1;
  
  uVar1 = scale_u16_by625_over2048_cap10000_53706((*((undefined2 *)camry_host_ptr((uint32_t)(camry_host_addr(((volatile F33DiagnosticCapture *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * (uint32_t)sizeof(F33DiagnosticCapture))))[0].profile_prefix) + (short)(param_1 & 0xff) * 0x48 + 0x2e)))));
  store_low_u16_big_endian_bytes_6a574(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return uVar1;
}

undefined4 capture_slot_dispatch_53892(ushort param_1, undefined4 param_2)

{
  undefined4 uVar1;
  
  uVar1 = scale_u16_by625_over2048_cap10000_53706((*((undefined2 *)camry_host_ptr((uint32_t)(camry_host_addr(((volatile F33DiagnosticCapture *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * (uint32_t)sizeof(F33DiagnosticCapture))))[0].profile_prefix) + (short)(param_1 & 0xff) * 0x48 + 0x30)))));
  store_low_u16_big_endian_bytes_6a574(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return uVar1;
}

undefined4 capture_slot_dispatch_538b0(ushort param_1, undefined4 param_2)

{
  undefined4 uVar1;
  
  uVar1 = scale_u16_by625_over2048_cap10000_53706((*((undefined2 *)camry_host_ptr((uint32_t)(camry_host_addr(((volatile F33DiagnosticCapture *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * (uint32_t)sizeof(F33DiagnosticCapture))))[0].profile_prefix) + (short)(param_1 & 0xff) * 0x48 + 0x32)))));
  store_low_u16_big_endian_bytes_6a574(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return uVar1;
}

undefined4 capture_slot_dispatch_538ce(ushort param_1, undefined4 param_2)

{
  undefined4 uVar1;
  
  uVar1 = scale_u16_by100_over256_cap10000_5377c((*((undefined2 *)camry_host_ptr((uint32_t)(camry_host_addr(((volatile F33DiagnosticCapture *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * (uint32_t)sizeof(F33DiagnosticCapture))))[0].profile_prefix) + (short)(param_1 & 0xff) * 0x48 + 0x16)))));
  store_low_u16_big_endian_bytes_6a574(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return uVar1;
}

undefined4 capture_slot_dispatch_538ec(ushort param_1, undefined4 param_2)

{
  undefined4 uVar1;
  
  uVar1 = scale_u16_by100_over256_cap10000_5377c((*((undefined2 *)camry_host_ptr((uint32_t)(camry_host_addr(((volatile F33DiagnosticCapture *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * (uint32_t)sizeof(F33DiagnosticCapture))))[0].profile_prefix) + (short)(param_1 & 0xff) * 0x48 + 0x18)))));
  store_low_u16_big_endian_bytes_6a574(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return uVar1;
}

undefined4 capture_slot_dispatch_5390a(ushort param_1, undefined4 param_2)

{
  undefined4 uVar1;
  
  uVar1 = scale_u16_by100_over256_cap10000_5377c((*((undefined2 *)camry_host_ptr((uint32_t)(camry_host_addr(((volatile F33DiagnosticCapture *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * (uint32_t)sizeof(F33DiagnosticCapture))))[0].profile_prefix) + (short)(param_1 & 0xff) * 0x48 + 0x1a)))));
  store_low_u16_big_endian_bytes_6a574(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return uVar1;
}

undefined4 capture_slot_dispatch_53928(ushort param_1, undefined4 param_2)

{
  undefined4 uVar1;
  
  uVar1 = scale_s16_by100_over128_clamp_symmetric32767_53686((int)(*((short *)camry_host_ptr((uint32_t)(camry_host_addr(((volatile F33DiagnosticCapture *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * (uint32_t)sizeof(F33DiagnosticCapture))))[0].profile_prefix) + (short)(param_1 & 0xff) * 0x48 + 4)))));
  store_low_u16_big_endian_bytes_6a5ac(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return uVar1;
}

undefined4 capture_slot_dispatch_53946(ushort param_1, undefined4 param_2)

{
  undefined4 uVar1;
  
  uVar1 = scale_s16_by100_over128_clamp_symmetric32767_53686((int)(*((short *)camry_host_ptr((uint32_t)(camry_host_addr(((volatile F33DiagnosticCapture *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * (uint32_t)sizeof(F33DiagnosticCapture))))[0].profile_prefix) + (short)(param_1 & 0xff) * 0x48 + 6)))));
  store_low_u16_big_endian_bytes_6a5ac(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return uVar1;
}

undefined4 capture_slot_dispatch_53964(ushort param_1, undefined4 param_2)

{
  undefined4 uVar1;
  
  uVar1 = scale_s16_by100_over128_clamp_symmetric32767_53686((int)(*((short *)camry_host_ptr((uint32_t)(camry_host_addr(((volatile F33DiagnosticCapture *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * (uint32_t)sizeof(F33DiagnosticCapture))))[0].profile_prefix) + (short)(param_1 & 0xff) * 0x48 + 0xe)))));
  store_low_u16_big_endian_bytes_6a5ac(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return uVar1;
}

undefined4 capture_slot_dispatch_53982(ushort param_1, undefined4 param_2)

{
  undefined4 uVar1;
  
  uVar1 = scale_s16_by100_over128_clamp_symmetric32767_53686((int)(*((short *)camry_host_ptr((uint32_t)(camry_host_addr(((volatile F33DiagnosticCapture *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * (uint32_t)sizeof(F33DiagnosticCapture))))[0].profile_prefix) + (short)(param_1 & 0xff) * 0x48 + 0x3c)))));
  store_low_u16_big_endian_bytes_6a5ac(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return uVar1;
}

void capture_slot_dispatch_539a0(ushort param_1, undefined4 param_2)

{
  uint32_t puVar1;
  
  puVar1 = ((uint32_t)((uint)*(ushort *)
                   (((volatile F33DiagnosticCapture *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * (uint32_t)sizeof(F33DiagnosticCapture))))[0].profile_prefix + (short)(param_1 & 0xff) * 0x48)
            * 36000 >> 0x10));
  if (((uint32_t)(0x8c9fu))<(puVar1)) {
    puVar1 = (0x8ca0u);
  }
  store_low_u16_big_endian_bytes_6a574((puVar1), ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}

void capture_slot_dispatch_539cc(ushort param_1,undefined4 param_2)

{
  short sStack_a;
  
  sStack_a = (short)(((*((short *)camry_host_ptr((uint32_t)(((volatile F33DiagnosticCapture *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * (uint32_t)sizeof(F33DiagnosticCapture))))[0].profile_prefix +
                                (short)(param_1 & 0xff) * 0x48 + 0x44)))) * 100) / 0x80);
  store_s16_max_third_min_first_two_70110((int)sStack_a,0x7fff,0,&sStack_a);
  store_low_u16_big_endian_bytes_6a5ac((int)sStack_a, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}

uint divide_s16_by100_and_clamp_to_u8_53a2c(short param_1)

{
  uint uVar1;
  
  uVar1 = (uint)(param_1 / 100);
  if ((int)(uVar1 - 0xff) < 0 == ((int)uVar1 < 0 && -1 < (int)(uVar1 - 0xff))) {
    uVar1 = 0xff;
  }
  if ((int)uVar1 < 0) {
    uVar1 = 0;
  }
  return uVar1 & 0xff;
}

uint32_t encode_retained_capture_offset30_as_scaled_u8_53a4e(void)

{
  uint32_t camry_r10_result;
  undefined1 *extraout_r7;
  undefined1 uVar1;
  
  uVar1 = (camry_r10_result = divide_s16_by100_and_clamp_to_u8_53a2c((int)(short)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * 240u + 178u))))));
  *extraout_r7 = uVar1;
  return camry_r10_result;
}

uint32_t encode_retained_capture_offset32_as_scaled_u8_53a62(void)

{
  uint32_t camry_r10_result;
  undefined1 *extraout_r7;
  undefined1 uVar1;
  
  uVar1 = (camry_r10_result = divide_s16_by100_and_clamp_to_u8_53a2c((int)(short)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * 240u + 180u))))));
  *extraout_r7 = uVar1;
  return camry_r10_result;
}

void capture_slot_dispatch_53a76(undefined4 param_1, undefined4 param_2)

{
  undefined2 uVar1;
  
  uVar1 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * 240u + 174u))));
  if (29999 < (ushort)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * 240u + 174u))))) {
    (*((uint8_t *)((uint8_t *)&uVar1 + 0u))) = '0';
    (*((uint8_t *)((uint8_t *)&uVar1 + 1u))) = 'u';
  }
  store_low_u16_big_endian_bytes_6a574(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}

void capture_slot_dispatch_53a92(undefined4 param_1, undefined4 param_2)

{
  int iVar1;
  
  iVar1 = (int)(short)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * 240u + 176u))));
  if (iVar1 + -0x7fff < 0 == (iVar1 < 0 && -1 < iVar1 + -0x7fff)) {
    iVar1 = 0x7fff;
  }
  if (iVar1 + 0x7fff < 0 != (-1 < iVar1 && iVar1 + 0x7fff < 0)) {
    iVar1 = -0x7fff;
  }
  store_low_u16_big_endian_bytes_6a5ac(iVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}

void capture_slot_dispatch_53ab8(undefined4 param_1, undefined4 param_2)

{
  uint32_t puVar1;
  
  puVar1 = ((uint32_t)((((int)((int)(short)(*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe82dcu + (uint32_t)(1) * (uint32_t)sizeof(F33DiagnosticCapture)) + (uint32_t)(0) * (uint32_t)sizeof(F33DiagnosticCapture) + (uint32_t)offsetof(F33DiagnosticCapture, selected_sample))))) * (uint)DAT_febee8a6
                   ) / 0x2000) * 100) / 0x100));
  if ((int)0xffffb1e0u + (int)(puVar1) < 0 ==
      ((int)(puVar1) < 0 && -1 < (int)0xffffb1e0u + (int)(puVar1))) {
    puVar1 = ((uint32_t)(0x4e20));
  }
  if ((int)((uint32_t)(puVar1 + 10000)) < 0 != (-1 < (int)(puVar1) && (int)((uint32_t)(puVar1 + 10000)) < 0)) {
    puVar1 = (0xffffb1e0u);
  }
  store_low_u16_big_endian_bytes_6a5ac((int)(short)puVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}

void capture_slot_dispatch_53afc(undefined4 param_1, undefined4 param_2)

{
  store_low_u16_big_endian_bytes_6a574((*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * 240u + 148u)))), ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}

int scale_s16_by100_over128_clamp_symmetric32767_53b1c(short param_1)

{
  int iVar1;
  
  iVar1 = (int)(short)((param_1 * 100) / 0x80);
  if (iVar1 + -0x7fff < 0 == (iVar1 < 0 && -1 < iVar1 + -0x7fff)) {
    iVar1 = 0x7fff;
  }
  if (iVar1 + 0x7fff < 0 != (-1 < iVar1 && iVar1 + 0x7fff < 0)) {
    iVar1 = -0x7fff;
  }
  return iVar1;
}

undefined4 capture_slot_dispatch_53b42(undefined4 param_1, undefined4 param_2)

{
  undefined4 uVar1;
  
  uVar1 = scale_s16_by100_over128_clamp_symmetric32767_53b1c((int)(short)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * 240u + 162u)))));
  store_low_u16_big_endian_bytes_6a5ac(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return uVar1;
}

undefined4 capture_slot_dispatch_53b68(undefined4 param_1, undefined4 param_2)

{
  undefined4 uVar1;
  
  uVar1 = scale_s16_by100_over128_clamp_symmetric32767_53b1c((int)(short)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * 240u + 158u)))));
  store_low_u16_big_endian_bytes_6a5ac(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return uVar1;
}

undefined4 capture_slot_dispatch_53b8e(undefined4 param_1, undefined4 param_2)

{
  undefined4 uVar1;
  
  uVar1 = scale_s16_by100_over128_clamp_symmetric32767_53b1c((int)(short)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * 240u + 154u)))));
  store_low_u16_big_endian_bytes_6a5ac(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return uVar1;
}

undefined4 capture_slot_dispatch_53bb4(undefined4 param_1, undefined4 param_2)

{
  undefined4 uVar1;
  
  uVar1 = scale_s16_by100_over128_clamp_symmetric32767_53b1c((int)(short)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * 240u + 172u)))));
  store_low_u16_big_endian_bytes_6a5ac(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return uVar1;
}

undefined4 capture_slot_dispatch_53bda(undefined4 param_1, undefined4 param_2)

{
  undefined4 uVar1;
  
  uVar1 = scale_s16_by100_over128_clamp_symmetric32767_53b1c((int)(short)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * 240u + 194u)))));
  store_low_u16_big_endian_bytes_6a5ac(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return uVar1;
}

undefined4 capture_slot_dispatch_53c00(undefined4 param_1, undefined4 param_2)

{
  undefined4 uVar1;
  
  uVar1 = scale_s16_by100_over128_clamp_symmetric32767_53b1c((int)(short)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * 240u + 198u)))));
  store_low_u16_big_endian_bytes_6a5ac(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return uVar1;
}

void capture_slot_dispatch_53c16(undefined4 param_1,int param_2)

{
  undefined4 uVar1;
  
  uVar1 = (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * 240u + 228u))));
  store_u32_big_endian_bytes_6a55c((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * 240u + 224u)))), ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  store_u32_big_endian_bytes_6a55c(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2 + 4))));
  return;
}

void capture_slot_dispatch_53c36(undefined4 param_1,undefined4 param_2)

{
  undefined2 uStack_a;
  
  uStack_a = (undefined2)
             ((uint)(ushort)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * 240u + 204u)))) * 36000 >> 0x10);
  store_min_u16_70180((uint)(ushort)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * 240u + 204u)))) * 36000 >> 0x10, ((uint32_t)(0x8ca0u)), &uStack_a);
  store_low_u16_big_endian_bytes_6a574(uStack_a, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}

void capture_slot_dispatch_53c68(undefined4 param_1,undefined4 param_2)

{
  undefined2 uStack_a;
  
  uStack_a = (undefined2)
             ((uint)(ushort)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * 240u + 206u)))) * 36000 >> 0x10);
  store_min_u16_70180((uint)(ushort)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * 240u + 206u)))) * 36000 >> 0x10, ((uint32_t)(0x8ca0u)), &uStack_a);
  store_low_u16_big_endian_bytes_6a574(uStack_a, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}

void capture_slot_dispatch_53c9a(undefined4 param_1, undefined4 param_2)

{
  store_low_u16_big_endian_bytes_6a574((*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * 240u + 208u)))), ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}

void capture_slot_dispatch_53caa(undefined4 param_1, undefined4 param_2)

{
  store_low_u16_big_endian_bytes_6a574((*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * 240u + 210u)))), ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}

void capture_slot_dispatch_53cba(undefined4 param_1, undefined4 param_2)

{
  store_low_u16_big_endian_bytes_6a574((*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * 240u + 212u)))), ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}

void capture_slot_dispatch_53cca(undefined4 param_1, undefined4 param_2)

{
  store_low_u16_big_endian_bytes_6a574((*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * 240u + 214u)))), ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}

void return_only_stub_53db2(void)

{
  return;
}

void return_only_stub_53db4(void)

{
  return;
}

void return_only_stub_53db6(void)

{
  return;
}

void build_diagnostic_capture_kind10(F33DiagnosticCapture *output)

{
  undefined2 uVar1;
  uchar uVar2;
  uint32_t puVar3;
  F33DiagnosticApplicationSample local_40;
  
  puVar3 = 0xfebeb800u;
  snapshot_diagnostic_application(&local_40,10);
  *(undefined4 *)output->profile_prefix = (*((undefined4 *)camry_host_ptr((uint32_t)(puVar3 + -0x544c))));
  *(undefined2 *)(output->profile_prefix + 8) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x542c))));
  output->profile_prefix[0x42] = local_40.raw[0];
  *(undefined2 *)(output->profile_prefix + 4) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x53f2))));
  *(undefined2 *)(output->profile_prefix + 6) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x53e0))));
  *(undefined2 *)(output->profile_prefix + 10) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3a50))));
  *(undefined2 *)(output->profile_prefix + 0xc) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x5428))));
  *(undefined2 *)(output->profile_prefix + 0xe) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x53f4))));
  *(undefined2 *)(output->profile_prefix + 0x10) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3964))));
  *(undefined2 *)(output->profile_prefix + 0x12) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3962))));
  *(undefined2 *)(output->profile_prefix + 0x14) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3960))));
  *(undefined2 *)(output->profile_prefix + 0x16) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x395e))));
  *(undefined2 *)(output->profile_prefix + 0x18) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x395c))));
  *(undefined2 *)(output->profile_prefix + 0x1a) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x395a))));
  *(undefined2 *)(output->profile_prefix + 0x1c) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x5470))));
  *(undefined2 *)(output->profile_prefix + 0x1e) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x546e))));
  *(undefined2 *)(output->profile_prefix + 0x20) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x546c))));
  *(undefined2 *)(output->profile_prefix + 0x22) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x546a))));
  *(undefined2 *)(output->profile_prefix + 0x24) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x5468))));
  *(undefined2 *)(output->profile_prefix + 0x26) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x5466))));
  *(undefined2 *)(output->profile_prefix + 0x28) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x55a2))));
  *(undefined2 *)(output->profile_prefix + 0x2a) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x55a0))));
  *(undefined2 *)(output->profile_prefix + 0x2c) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x559e))));
  *(undefined2 *)(output->profile_prefix + 0x2e) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x559c))));
  *(undefined2 *)(output->profile_prefix + 0x30) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x559a))));
  *(undefined2 *)(output->profile_prefix + 0x32) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x5598))));
  *(undefined2 *)(output->profile_prefix + 0x34) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3a5a))));
  *(undefined2 *)(output->profile_prefix + 0x36) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3a58))));
  *(undefined2 *)(output->profile_prefix + 0x38) = (*((uint16_t *)((uint8_t *)&local_40 + 10u)));
  *(undefined2 *)(output->profile_prefix + 0x3a) = (*((uint16_t *)((uint8_t *)&local_40 + 12u)));
  *(undefined2 *)(output->profile_prefix + 0x3c) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x53de))));
  *(undefined2 *)(output->profile_prefix + 0x3e) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3a4e))));
  uVar1 = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3aba))));
  output->profile_prefix[0x46] = '\0';
  output->profile_prefix[0x47] = '\0';
  *(undefined2 *)(output->profile_prefix + 0x40) = uVar1;
  *(undefined2 *)(output->profile_prefix + 0x44) = (*((uint16_t *)((uint8_t *)&local_40 + 24u)));
  output->profile_prefix[0x43] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3814)))));
  output->extended_prefix[5] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x37fa)))));
  *(undefined2 *)output->extended_prefix = (*((uint16_t *)((uint8_t *)&local_40 + 14u)));
  *(undefined2 *)(output->extended_prefix + 2) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3a32))));
  output->extended_prefix[4] = local_40.raw[1];
  output->extended_prefix[0xc] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3abc)))));
  output->extended_prefix[8] = local_40.raw[2];
  *(undefined2 *)(output->extended_prefix + 6) = (*((uint16_t *)((uint8_t *)&local_40 + 18u)));
  output->extended_prefix[9] = local_40.raw[3];
  *(undefined2 *)(output->extended_prefix + 10) = (*((uint16_t *)((uint8_t *)&local_40 + 20u)));
  output->extended_prefix[0xd] = local_40.raw[4];
  *(undefined2 *)(output->extended_prefix + 0xe) = (*((uint16_t *)((uint8_t *)&local_40 + 22u)));
  *(undefined2 *)(output->extended_prefix + 0x10) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x5552))));
  *(undefined2 *)(output->extended_prefix + 0x12) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x5550))));
  *(undefined2 *)(output->extended_prefix + 0x14) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x554e))));
  *(undefined2 *)(output->extended_prefix + 0x16) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x554c))));
  *(undefined2 *)(output->extended_prefix + 0x1a) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3766))));
  *(undefined2 *)(output->extended_prefix + 0x1c) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x37b6))));
  *(undefined2 *)(output->extended_prefix + 0x1e) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x37a0))));
  *(undefined2 *)(output->extended_prefix + 0x20) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x379e))));
  output->extended_prefix[0x22] = local_40.raw[5];
  output->selected_sample = (*((uint16_t *)((uint8_t *)&local_40 + 26u)));
  output->extended_prefix[0x23] = '\x11';
  *(undefined2 *)output->extended_middle = (*((uint16_t *)((uint8_t *)&local_40 + 16u)));
  *(undefined4 *)(output->extended_middle + 2) = (*((uint32_t *)((uint8_t *)&local_40 + 32u)));
  output->extended_middle[6] = local_40.raw[6];
  output->extended_middle[7] = local_40.raw[7];
  *(undefined4 *)(output->extended_middle + 0xe) = (*((uint32_t *)((uint8_t *)&local_40 + 36u)));
  output->extended_tail[10] = local_40.raw[0x28];
  output->extended_tail[0xb] = local_40.raw[0x29];
  output->extended_tail[0xc] = local_40.raw[0x2a];
  output->extended_tail[0xd] = local_40.raw[0x2b];
  output->extended_tail[0xe] = local_40.raw[0x2c];
  output->extended_tail[0xf] = local_40.raw[0x2d];
  output->extended_middle[10] = local_40.raw[8];
  *(undefined2 *)(output->extended_middle + 8) = (*((uint16_t *)((uint8_t *)&local_40 + 28u)));
  output->extended_middle[0xb] = local_40.raw[9];
  *(undefined2 *)(output->extended_middle + 0xc) = (*((uint16_t *)((uint8_t *)&local_40 + 30u)));
  output->extended_tail[0x10] = local_40.raw[0x30];
  *(undefined2 *)(output->extended_prefix + 0x18) = (*((uint16_t *)((uint8_t *)&local_40 + 46u)));
  *(undefined2 *)(output->extended_middle + 0x12) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x54ac))));
  *(undefined2 *)(output->extended_middle + 0x14) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x54aa))));
  *(undefined2 *)(output->extended_middle + 0x16) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x54a4))));
  *(undefined2 *)(output->extended_middle + 0x18) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x54a8))));
  *(undefined2 *)(output->extended_middle + 0x1a) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x54a6))));
  *(undefined2 *)(output->extended_middle + 0x1c) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x54a2))));
  output->ecu_thermal_estimate = (*((short *)camry_host_ptr((uint32_t)((0xffffb77au + (uint32_t)((int)puVar3))))));
  output->motor_thermal_estimate = (*((short *)camry_host_ptr((uint32_t)((0xffffb77cu + (uint32_t)((int)puVar3))))));
  output->ecu_thermal_source = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb76cu + (uint32_t)((int)puVar3) * 1u))));
  uVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb76du + (uint32_t)((int)puVar3) * 1u))));
  output->extended_tail[0x11] = '\0';
  output->motor_thermal_active = uVar2;
  *(undefined2 *)output->extended_tail = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3a2a))));
  *(undefined4 *)(output->extended_tail + 2) = (*((undefined4 *)camry_host_ptr((uint32_t)(puVar3 + -0x3568))));
  *(undefined4 *)(output->extended_tail + 6) = (*((undefined4 *)camry_host_ptr((uint32_t)(puVar3 + -0x3564))));
  return;
}

void return_only_stub_53ff8(void)

{
  return;
}

void return_only_stub_53ffa(void)

{
  return;
}

void return_only_stub_53ffc(void)

{
  return;
}

void build_diagnostic_capture_kind4(F33DiagnosticCapture *output)

{
  undefined2 uVar1;
  uchar uVar2;
  uint32_t puVar3;
  F33DiagnosticApplicationSample local_40;
  
  puVar3 = 0xfebeb800u;
  snapshot_diagnostic_application(&local_40,4);
  *(undefined4 *)output->profile_prefix = (*((undefined4 *)camry_host_ptr((uint32_t)(puVar3 + -0x55f8))));
  *(undefined2 *)(output->profile_prefix + 8) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x55f4))));
  output->profile_prefix[0x42] = local_40.raw[0];
  *(undefined2 *)(output->profile_prefix + 4) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x55ea))));
  *(undefined2 *)(output->profile_prefix + 6) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x55d8))));
  *(undefined2 *)(output->profile_prefix + 10) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3a50))));
  *(undefined2 *)(output->profile_prefix + 0xc) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x39f4))));
  *(undefined2 *)(output->profile_prefix + 0xe) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x55ec))));
  *(undefined2 *)(output->profile_prefix + 0x10) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3964))));
  *(undefined2 *)(output->profile_prefix + 0x12) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3962))));
  *(undefined2 *)(output->profile_prefix + 0x14) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3960))));
  *(undefined2 *)(output->profile_prefix + 0x16) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x395e))));
  *(undefined2 *)(output->profile_prefix + 0x18) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x395c))));
  *(undefined2 *)(output->profile_prefix + 0x1a) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x395a))));
  *(undefined2 *)(output->profile_prefix + 0x1c) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x561c))));
  *(undefined2 *)(output->profile_prefix + 0x1e) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x561a))));
  *(undefined2 *)(output->profile_prefix + 0x20) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x5618))));
  *(undefined2 *)(output->profile_prefix + 0x22) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x5616))));
  *(undefined2 *)(output->profile_prefix + 0x24) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x5614))));
  *(undefined2 *)(output->profile_prefix + 0x26) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x5612))));
  *(undefined2 *)(output->profile_prefix + 0x28) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x5696))));
  *(undefined2 *)(output->profile_prefix + 0x2a) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x5694))));
  *(undefined2 *)(output->profile_prefix + 0x2c) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x5692))));
  *(undefined2 *)(output->profile_prefix + 0x2e) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x5690))));
  *(undefined2 *)(output->profile_prefix + 0x30) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x568e))));
  *(undefined2 *)(output->profile_prefix + 0x32) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x568c))));
  *(undefined2 *)(output->profile_prefix + 0x34) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3a5a))));
  *(undefined2 *)(output->profile_prefix + 0x36) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3a58))));
  *(undefined2 *)(output->profile_prefix + 0x38) = (*((uint16_t *)((uint8_t *)&local_40 + 10u)));
  *(undefined2 *)(output->profile_prefix + 0x3a) = (*((uint16_t *)((uint8_t *)&local_40 + 12u)));
  *(undefined2 *)(output->profile_prefix + 0x3c) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x55d6))));
  *(undefined2 *)(output->profile_prefix + 0x3e) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3a4e))));
  uVar1 = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3aba))));
  output->profile_prefix[0x46] = '\0';
  output->profile_prefix[0x47] = '\0';
  *(undefined2 *)(output->profile_prefix + 0x40) = uVar1;
  *(undefined2 *)(output->profile_prefix + 0x44) = (*((uint16_t *)((uint8_t *)&local_40 + 24u)));
  output->profile_prefix[0x43] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3814)))));
  output->extended_prefix[5] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x37fa)))));
  *(undefined2 *)output->extended_prefix = (*((uint16_t *)((uint8_t *)&local_40 + 14u)));
  *(undefined2 *)(output->extended_prefix + 2) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3a32))));
  output->extended_prefix[4] = local_40.raw[1];
  output->extended_prefix[0xc] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3abc)))));
  output->extended_prefix[8] = local_40.raw[2];
  *(undefined2 *)(output->extended_prefix + 6) = (*((uint16_t *)((uint8_t *)&local_40 + 18u)));
  output->extended_prefix[9] = local_40.raw[3];
  *(undefined2 *)(output->extended_prefix + 10) = (*((uint16_t *)((uint8_t *)&local_40 + 20u)));
  output->extended_prefix[0xd] = local_40.raw[4];
  *(undefined2 *)(output->extended_prefix + 0xe) = (*((uint16_t *)((uint8_t *)&local_40 + 22u)));
  *(undefined2 *)(output->extended_prefix + 0x10) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3a14))));
  *(undefined2 *)(output->extended_prefix + 0x12) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3a12))));
  *(undefined2 *)(output->extended_prefix + 0x14) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3a10))));
  *(undefined2 *)(output->extended_prefix + 0x16) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3a0e))));
  *(undefined2 *)(output->extended_prefix + 0x1a) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3766))));
  *(undefined2 *)(output->extended_prefix + 0x1c) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x37b6))));
  *(undefined2 *)(output->extended_prefix + 0x1e) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x37a0))));
  *(undefined2 *)(output->extended_prefix + 0x20) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x379e))));
  output->extended_prefix[0x22] = local_40.raw[5];
  output->selected_sample = (*((uint16_t *)((uint8_t *)&local_40 + 26u)));
  output->extended_prefix[0x23] = '\x11';
  *(undefined2 *)output->extended_middle = (*((uint16_t *)((uint8_t *)&local_40 + 16u)));
  *(undefined4 *)(output->extended_middle + 2) = (*((uint32_t *)((uint8_t *)&local_40 + 32u)));
  output->extended_middle[6] = local_40.raw[6];
  output->extended_middle[7] = local_40.raw[7];
  *(undefined4 *)(output->extended_middle + 0xe) = (*((uint32_t *)((uint8_t *)&local_40 + 36u)));
  output->extended_tail[10] = local_40.raw[0x28];
  output->extended_tail[0xb] = local_40.raw[0x29];
  output->extended_tail[0xc] = local_40.raw[0x2a];
  output->extended_tail[0xd] = local_40.raw[0x2b];
  output->extended_tail[0xe] = local_40.raw[0x2c];
  output->extended_tail[0xf] = local_40.raw[0x2d];
  output->extended_middle[10] = local_40.raw[8];
  *(undefined2 *)(output->extended_middle + 8) = (*((uint16_t *)((uint8_t *)&local_40 + 28u)));
  output->extended_middle[0xb] = local_40.raw[9];
  *(undefined2 *)(output->extended_middle + 0xc) = (*((uint16_t *)((uint8_t *)&local_40 + 30u)));
  output->extended_tail[0x10] = local_40.raw[0x30];
  *(undefined2 *)(output->extended_prefix + 0x18) = (*((uint16_t *)((uint8_t *)&local_40 + 46u)));
  *(undefined2 *)(output->extended_middle + 0x12) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x5658))));
  *(undefined2 *)(output->extended_middle + 0x14) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x5656))));
  *(undefined2 *)(output->extended_middle + 0x16) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x5650))));
  *(undefined2 *)(output->extended_middle + 0x18) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x5654))));
  *(undefined2 *)(output->extended_middle + 0x1a) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x5652))));
  *(undefined2 *)(output->extended_middle + 0x1c) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x564e))));
  output->ecu_thermal_estimate = (*((short *)camry_host_ptr((uint32_t)((0xffffb77au + (uint32_t)((int)puVar3))))));
  output->motor_thermal_estimate = (*((short *)camry_host_ptr((uint32_t)((0xffffb77cu + (uint32_t)((int)puVar3))))));
  output->ecu_thermal_source = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb76cu + (uint32_t)((int)puVar3) * 1u))));
  uVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb76du + (uint32_t)((int)puVar3) * 1u))));
  output->extended_tail[0x11] = '\0';
  output->motor_thermal_active = uVar2;
  *(undefined2 *)output->extended_tail = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3a2a))));
  *(undefined4 *)(output->extended_tail + 2) = (*((undefined4 *)camry_host_ptr((uint32_t)(puVar3 + -0x3568))));
  *(undefined4 *)(output->extended_tail + 6) = (*((undefined4 *)camry_host_ptr((uint32_t)(puVar3 + -0x3564))));
  return;
}
