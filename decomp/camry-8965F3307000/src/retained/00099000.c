#include "common.h"

void store_u32_little_endian_bytes_99004(undefined4 param_1,undefined1 *param_2)

{
  param_2[1] = (char)((uint)param_1 >> 8);
  *param_2 = (char)param_1;
  param_2[2] = (char)((uint)param_1 >> 0x10);
  param_2[3] = (char)((uint)param_1 >> 0x18);
  return;
}

undefined4 select_memory_cursor_window_and_reply_length_9901a(int param_1,short param_2)

{
  uint8_t stack_record_18[24];
  int iVar1;
  int iVar2;
  int iVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  uint uVar6;
  
  uVar5 = 0xa5;
  uVar4 = 0x21;
  iVar3 = 0;
  do {
    ((uint8_t *)(stack_record_18))[iVar3] = 0;
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -7;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  if (param_2 == 8) {
    uVar6 = (uint)(*((byte *)camry_host_ptr((uint32_t)(param_1 + 1))));
    if (uVar6 < 5) {
      uVar5 = 0x5a;
      ((uint8_t *)(stack_record_18))[1] = 0;
      store_u32_little_endian_bytes_99004(*(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0x2b22cu + (uint32_t)(uVar6 * 8) * 1u)))),((uint8_t *)((stack_record_18 + 4))));
      thunk_set_memory_cursor_u32_82288((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x2b228u + (uint32_t)(uVar6 * 2) * 4u)))));
    }
    else {
      uVar4 = 0x22;
    }
  }
  build_ff_success_or_fe_error_reply_98f6e(camry_host_addr(((uint8_t *)(stack_record_18))), uVar5, uVar4);
  return 0x5a;
}

undefined4 reject_disallowed_memory_span_9907a(undefined *param_1,int param_2)

{
  int iVar1;
  int iVar2;
  undefined *puVar3;
  undefined4 uVar4;
  int iVar5;
  
  puVar3 = param_1;
  if ((param_2 != 0) && (puVar3 = ((undefined *)camry_host_ptr((uint32_t)(0xffffffff))),camry_host_addr(param_1)<(uint32_t)(~(param_2 - 1U))))
  {
    puVar3 = param_1 + param_2 + -1;
  }
  if ((0xfebdffffu <camry_host_addr(param_1)) && (camry_host_addr(puVar3)< 0xfec00000u)) {
    iVar5 = 0;
    while( true ) {
      if (iVar5 - (*((volatile int32_t *)camry_host_ptr(0x2b218u))) < 0 ==
          (iVar5 < 0 != (*((volatile int32_t *)camry_host_ptr(0x2b218u))) < 0 && (*((volatile int32_t *)camry_host_ptr(0x2b218u))) < 0 == iVar5 - (*((volatile int32_t *)camry_host_ptr(0x2b218u))) < 0)) {
        return 0;
      }
      if ((camry_host_addr(param_1)<= (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x29258u + (uint32_t)(iVar5 * 2) * 4u))))) && ((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x29254u + (uint32_t)(iVar5 * 2) * 4u)))) <=camry_host_addr(puVar3)))
      break;
      iVar5 = iVar5 + 1;
    }
    return 1;
  }
  if (((param_2 == 0x7dec) && (0xffff <camry_host_addr(param_1))) && (camry_host_addr(puVar3)<((uint32_t)(0x17df0u)))) {
    return 0;
  }
  uVar4 = 1;
  iVar5 = 0;
  do {
    if (((*(int *)(((undefined *)camry_host_ptr((uint32_t)(0x2b22cu + (uint32_t)(iVar5 * 8) * 1u)))) != 0) && ((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x2b228u + (uint32_t)(iVar5 * 2) * 4u)))) <=camry_host_addr(param_1)))
       && (camry_host_addr(puVar3)<= (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x2b228u + (uint32_t)(iVar5 * 2) * 4u)))) + *(int *)(((undefined *)camry_host_ptr((uint32_t)(0x2b22cu + (uint32_t)(iVar5 * 8) * 1u)))) + -1)) {
      uVar4 = 0;
    }
    iVar2 = iVar5 + 1;
    iVar1 = iVar5 + -4;
    iVar5 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  return uVar4;
}

void copy_u8_length_bytes_and_advance_memory_cursor_99126(int param_1,uint param_2,int param_3)

{
  uint uVar1;
  
  for (uVar1 = 0; uVar1 < (param_2 & 0xff); uVar1 = uVar1 + 1) {
    (*((undefined1 *)camry_host_ptr((uint32_t)(uVar1 + param_3)))) = (*((undefined1 *)camry_host_ptr((uint32_t)(uVar1 + param_1))));
  }
  thunk_set_memory_cursor_u32_82288((param_2 & 0xff) + param_1);
  return;
}

undefined4 read_memory_cursor_bytes_and_build_reply_99152(int param_1,short param_2)

{
  int iVar1;
  int iVar2;
  byte bVar3;
  undefined4 uVar4;
  int iVar5;
  undefined4 uVar6;
  undefined4 uVar7;
  undefined1 local_1c [12];
  
  uVar6 = 0xa5;
  uVar7 = 0x21;
  iVar5 = 0;
  do {
    local_1c[iVar5] = 0;
    iVar2 = iVar5 + 1;
    iVar1 = iVar5 + -7;
    iVar5 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  if (param_2 == 8) {
    bVar3 = (*((byte *)camry_host_ptr((uint32_t)(param_1 + 1))));
    if ((bVar3 == 0) || (7 < bVar3)) {
      uVar7 = 0x22;
    }
    else {
      uVar4 = thunk_get_memory_cursor_u32_8228e();
      iVar5 = reject_disallowed_memory_span_9907a(((undefined *)camry_host_ptr((uint32_t)(uVar4))), bVar3);
      if (iVar5 == 0) {
        uVar6 = 0x5a;
        copy_u8_length_bytes_and_advance_memory_cursor_99126(uVar4, bVar3, camry_host_addr(local_1c + 1));
      }
      else {
        uVar7 = 0x24;
      }
    }
  }
  build_ff_success_or_fe_error_reply_98f6e(camry_host_addr(local_1c), uVar6, uVar7);
  return 0x5a;
}

void load_little_endian_u32_to_output_991b6(undefined4 *param_1,undefined4 *param_2)

{
  *param_2 = *param_1;
  return;
}

undefined * translate_memory_cursor_between_image_and_snapshot_991d2(char param_1)

{
  undefined *puVar1;
  
  puVar1 = ((undefined *)camry_host_ptr((uint32_t)(thunk_get_memory_cursor_u32_8228e())));
  if (param_1 == '\0') {
    if ((camry_host_addr(puVar1)< 0x10000) || (((uint32_t)(0x17defu))<camry_host_addr(puVar1))) {
      if ((0xfebf7bffu <camry_host_addr(puVar1)) &&
         ((camry_host_addr(puVar1)< 0xfebff9edu && (DAT_febe5ec5 == '\0')))) {
        puVar1 = puVar1 + 0x1418400;
      }
    }
    else if (DAT_febe5ec5 == '\x01') {
      puVar1 = ((undefined *)camry_host_ptr((uint32_t)((int)0xfebe7c00u + (int)camry_host_addr(puVar1))));
    }
  }
  return puVar1;
}

uint compute_inverted_dcra1_crc_and_advance_cursor_99226(int param_1,uint param_2)

{
  int iVar1;
  uint uVar2;
  
  camry_write8(0xffd51020u, '\0');
  camry_write32(0xffd51004u, (int)0xffffffff);
  uVar2 = 0;
  while (uVar2 < param_2 >> 2) {
    iVar1 = uVar2 * 4;
    uVar2 = uVar2 + 1;
    camry_write32(0xffd51000u, (*((uint *)camry_host_ptr((uint32_t)(iVar1 + param_1)))));
  }
  thunk_set_memory_cursor_u32_82288(uVar2 * 4 + param_1);
  uVar2 = camry_read32(0xffd51004u);
  return ~uVar2;
}

undefined4 validate_cursor_crc_request_and_build_reply_99266(int param_1,short param_2)

{
  uint8_t stack_record_20[32];
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  uint uVar4;
  int iVar5;
  undefined4 uVar6;
  undefined4 uVar7;
  
  uVar6 = 0xa5;
  uVar7 = 0x21;
  (*((uint32_t *)(stack_record_20 + 0))) = 0;
  iVar5 = 0;
  do {
    ((uint8_t *)((stack_record_20 + 4)))[iVar5] = 0;
    iVar2 = iVar5 + 1;
    iVar1 = iVar5 + -7;
    iVar5 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  if (param_2 == 8) {
    load_little_endian_u32_to_output_991b6(((undefined4 *)camry_host_ptr((uint32_t)(param_1 + 4))), stack_record_20);
    if ((((*((uint32_t *)(stack_record_20 + 0))) == 0) || (0x7dec < (*((uint32_t *)(stack_record_20 + 0))))) || (((*((uint32_t *)(stack_record_20 + 0))) & 3) != 0)) {
      uVar7 = 0x22;
      uVar3 = 0x7dec;
    }
    else {
      uVar4 = camry_host_addr(translate_memory_cursor_between_image_and_snapshot_991d2(0));
      iVar5 = reject_disallowed_memory_span_9907a(((undefined *)camry_host_ptr((uint32_t)(uVar4))), (*((uint32_t *)(stack_record_20 + 0))));
      if ((iVar5 != 0) || ((uVar4 & 3) != 0)) {
        uVar7 = 0x24;
        goto LAB_000992fa;
      }
      uVar6 = 0x5a;
      uVar3 = compute_inverted_dcra1_crc_and_advance_cursor_99226(uVar4,(*((uint32_t *)(stack_record_20 + 0))));
      ((uint8_t *)((stack_record_20 + 4)))[1] = 0xff;
    }
    store_u32_little_endian_bytes_99004(uVar3,((uint8_t *)((stack_record_20 + 8))));
  }
LAB_000992fa:
  build_ff_success_or_fe_error_reply_98f6e(camry_host_addr(((uint8_t *)((stack_record_20 + 4)))), uVar6, uVar7);
  return 0x5a;
}

undefined4 set_selected_memory_mode_flags_and_build_reply_9930e(int param_1,short param_2)

{
  int iVar1;
  int iVar2;
  byte bVar3;
  byte bVar4;
  undefined4 uVar5;
  undefined4 uVar6;
  int iVar7;
  undefined1 local_c [8];
  
  uVar5 = 0xa5;
  uVar6 = 0x21;
  iVar7 = 0;
  do {
    local_c[iVar7] = 0;
    iVar2 = iVar7 + 1;
    iVar1 = iVar7 + -7;
    iVar7 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  if (param_2 == 8) {
    if ((*((char *)camry_host_ptr((uint32_t)(param_1 + 2)))) == '\0') {
      bVar3 = (*((byte *)camry_host_ptr((uint32_t)(param_1 + 3))));
      bVar4 = (*((byte *)camry_host_ptr((uint32_t)(param_1 + 1))));
      if ((bVar3 < 2) && ((bVar3 == 1 || ((bVar4 & 1) == 0)))) {
        if ((bVar4 & 3) == 0) {
          uVar6 = 0x27;
        }
        else {
          uVar5 = 0x5a;
          if ((bVar4 >> 1 & 1) != 0) {
            DAT_febe5ec5 = bVar3;
          }
          if ((bVar4 & 1) != 0) {
            DAT_febe5ec4 = bVar3;
          }
        }
      }
      else {
        uVar6 = 0x26;
      }
    }
    else {
      uVar6 = 0x28;
    }
  }
  build_ff_success_or_fe_error_reply_98f6e(camry_host_addr(local_c), uVar5, uVar6);
  return 0x5a;
}

undefined4 get_selected_memory_mode_flag_and_build_reply_99388(int param_1,short param_2)

{
  int iVar1;
  int iVar2;
  undefined1 uVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  int iVar6;
  undefined1 local_c [8];
  
  uVar4 = 0xa5;
  uVar5 = 0x21;
  iVar6 = 0;
  do {
    local_c[iVar6] = 0;
    iVar2 = iVar6 + 1;
    iVar1 = iVar6 + -7;
    iVar6 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  if (param_2 == 8) {
    if ((*((char *)camry_host_ptr((uint32_t)(param_1 + 2)))) == '\0') {
      uVar3 = DAT_febe5ec4;
      if (((*((char *)camry_host_ptr((uint32_t)(param_1 + 1)))) == '\x01') ||
         (uVar3 = DAT_febe5ec5, (*((char *)camry_host_ptr((uint32_t)(param_1 + 1)))) == '\x02')) {
        uVar4 = 0x5a;
        local_c[3] = uVar3;
      }
      else {
        uVar5 = 0x27;
      }
    }
    else {
      uVar5 = 0x28;
    }
  }
  build_ff_success_or_fe_error_reply_98f6e(camry_host_addr(local_c), uVar4, uVar5);
  return 0x5a;
}

void copy_image_window_to_snapshot_words_993f0(void)

{
  undefined4 *puVar1;
  undefined4 *puVar2;
  
  puVar2 = ((undefined *)camry_host_ptr(0xfebf7c00u));
  for (puVar1 = ((undefined *)camry_host_ptr(0x10000u));camry_host_addr(puVar1)<((uint32_t)(0x17df0u)); puVar1 = ((undefined *)camry_host_ptr((uint32_t)(0x10000u + (uint32_t)(1) * 1u)))) {
    *puVar2 = *puVar1;
    puVar2 = puVar2 + 1;
  }
  return;
}

undefined4 conditionally_copy_snapshot_and_build_reply_99414(int param_1,short param_2)

{
  int iVar1;
  int iVar2;
  int iVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  undefined1 local_14 [8];
  
  uVar4 = 0xa5;
  uVar5 = 0x21;
  iVar3 = 0;
  do {
    local_14[iVar3] = 0;
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -7;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  if (param_2 == 8) {
    if (((*((char *)camry_host_ptr((uint32_t)(param_1 + 1)))) == '\0') && ((*((char *)camry_host_ptr((uint32_t)(param_1 + 3)))) == '\0')) {
      if (((*((byte *)camry_host_ptr((uint32_t)(param_1 + 2)))) < 2) && ((*((byte *)camry_host_ptr((uint32_t)(param_1 + 4)))) < 2)) {
        if ((*((byte *)camry_host_ptr((uint32_t)(param_1 + 4)))) == 1) {
          uVar4 = 0x5a;
          if ((*((byte *)camry_host_ptr((uint32_t)(param_1 + 2)))) == 0) {
            copy_image_window_to_snapshot_words_993f0();
          }
        }
        else {
          uVar5 = 0x23;
        }
      }
      else {
        uVar5 = 0x26;
      }
    }
    else {
      uVar5 = 0x28;
    }
  }
  build_ff_success_or_fe_error_reply_98f6e(camry_host_addr(local_14), uVar4, uVar5);
  return 0x5a;
}
