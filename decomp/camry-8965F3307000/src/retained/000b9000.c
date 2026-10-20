#include "common.h"

void monitor_pending_learned_record_updates(void)

{
  undefined4 uVar1;
  bool bVar2;
  
  if (DAT_febeb494 == 'Z') {
    if (DAT_febeb495 == 'Z') {
      if ((DAT_febef011 != 'D') || (DAT_febef00f != 'D')) {
        if (DAT_febef011 == '\0') {
          return;
        }
        goto LAB_000b90b8;
      }
    }
    else if (DAT_febef011 != 'D') {
      bVar2 = DAT_febef011 == '\0';
      goto LAB_000b90bc;
    }
  }
  else {
    if (DAT_febeb495 != 'Z') {
      return;
    }
    if (DAT_febef00f != 'D') {
LAB_000b90b8:
      bVar2 = DAT_febef00f == '\x11';
LAB_000b90bc:
      if (bVar2) {
        return;
      }
      uVar1 = 0x22;
      goto LAB_000b90c2;
    }
  }
  uVar1 = 0x11;
LAB_000b90c2:
  finish_pending_b496_requests_with_status_b8fee(uVar1);
  return;
}

undefined4 coordinate_two_masked_requests_and_return_status_b90ca(uint param_1,byte param_2)

{
  int iVar1;
  uint32_t puVar2;
  int iVar4;
  char cVar5;
  undefined4 uVar6;
  char cVar7;
  byte bVar8;
  uint32_t puVar3;
  iVar1 = DAT_febef208;
  bVar8 = DAT_febeb496;
  cVar7 = DAT_febeb495;
  puVar3 = 0xfebeb800u;
  puVar2 = (0xfebeb800u);
  iVar4 = 0;
  cVar5 = DAT_febeb494;
  if (((DAT_febeb11a & 0xff00) == 0x100) || ((DAT_febeb11a & 0xff00) == 0x900)) {
    uVar6 = 0xfffffffa;
    goto LAB_000b917c;
  }
  if (DAT_febeb495 == 'Z') {
    if (DAT_febef00f == 'D') {
      uVar6 = 0;
      cVar7 = '\0';
      goto LAB_000b917c;
    }
    uVar6 = 0xffffffff;
    if (DAT_febef00f == '\x11') goto LAB_000b917c;
    uVar6 = 0xfffffff7;
    cVar7 = '\0';
    puVar2 = (0xfebeb800u);
LAB_000b916e:
    if (iVar4 != 0x5a) goto LAB_000b917c;
  }
  else {
    uVar6 = 0xffffffff;
    puVar2 = (0xfebeb800u);
    if ((param_1 & 0x11) == 0x11) {
      if (DAT_febef210 == 0) {
        iVar4 = 0x5a;
      }
      else {
        if (DAT_febeb494 == '\0') {
          puVar3 = 0xfebeb800u;
          thunk_invalidate_fit_record_202_header_34bce();
          cVar5 = 'Z';
        }
        iVar4 = 0;
        puVar2 = ((uint32_t)(puVar3));
        bVar8 = bVar8 | param_2;
      }
    }
    if ((param_1 & 0x22) != 0x22) goto LAB_000b916e;
    if (iVar1 != 0) {
      if (cVar7 == '\0') {
        thunk_invalidate_learned_quad_record_with_default_payload_3599e();
        cVar7 = 'Z';
        (*((volatile undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(-0x369) * 1u)))) = 0x5a;
        (*((volatile undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(-0x368) * 1u)))) = param_2;
      }
      bVar8 = bVar8 | param_2;
      goto LAB_000b917c;
    }
  }
  if (param_2 == 1 || param_2 == 2) {
    uVar6 = 0;
  }
LAB_000b917c:
  (*((volatile undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(-0x36c) * 1u)))) = cVar5;
  (*((volatile undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(-0x36b) * 1u)))) = cVar7;
  (*((volatile undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(-0x36a) * 1u)))) = bVar8;
  return uVar6;
}

void return_only_stub_b918c(void)

{
  return;
}

int load_nvm_seven_lifecycle_marker_b918e(void)

{
  undefined1 uVar1;
  uint32_t puVar2;
  int iVar3;
  char local_c [8];
  
  puVar2 = 0xfebeb800u;
  DAT_febeaf46 = 0;
  iVar3 = call_nvm_get_record_with_u16_selector_ff0b0(7,local_c);
  if (iVar3 == 0x11) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x8bc))))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x8b7))))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x8b6))))) = 0;
  }
  else {
    if ((iVar3 == 0x10) && (local_c[0] == '\x11')) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x8bc))))) = 1;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x8b7))))) = 0x11;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x8b6))))) = 0x11;
      uVar1 = 0;
      goto LAB_000b91e6;
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x8bc))))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x8b7))))) = 0x22;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x8b6))))) = 0x22;
  }
  uVar1 = 0x5a;
LAB_000b91e6:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x8bb))))) = uVar1;
  return iVar3;
}

void write_nvm_seven_marker_and_save_request_kind_b91ee(undefined1 param_1)

{
  uint8_t stack_record_10[16];
  uint32_t puVar1;
  
  puVar1 = 0xfebeb800u;
  stack_record_10[1] = 0;
  (*((uint16_t *)(stack_record_10 + 2))) = 0;
  (*((uint32_t *)(stack_record_10 + 4))) = 0;
  stack_record_10[0] = DAT_febeaf49;
  call_nvm_set_record_with_u16_selector_ff09c(7,stack_record_10);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x8b8))))) = param_1;
  return;
}

void consume_lifecycle_normalization_request(void)

{
  char cVar1;
  char cVar2;
  uint32_t puVar3;
  int iVar4;
  undefined4 uVar5;
  undefined1 uVar6;
  char cVar7;
  
  cVar1 = DAT_febeaf47;
  uVar6 = DAT_febeaf45;
  puVar3 = (0xfebeb800u);
  DAT_febeaf4a = DAT_febeaf49;
  if (DAT_febeaf47 != '\0') {
    cVar7 = DAT_febeaf49;
    cVar2 = DAT_febeaf46;
    if ((DAT_febeaf47 == '\x11') && (cVar7 = DAT_febeaf47, DAT_febeaf49 != '\x11')) {
      uVar6 = 0;
      iVar4 = 3;
    }
    else if ((DAT_febeaf47 == '\"') && (cVar7 == '\x11')) {
      uVar6 = 0x5a;
      iVar4 = 4;
      cVar7 = DAT_febeaf47;
    }
    else if (DAT_febeaf47 == 'D') {
      puVar3 = (0xfebeb800u);
      if ((DAT_febeaf46 != 'Z') && (puVar3 = (0xfebeb800u), iVar4 = check_selected_pair_of_lifecycle_states_idle_b8d9c(1), iVar4 == 0x5a))
      {
        start_selected_b438_or_b439_lifecycle_group_b8dda(1);
      }
      iVar4 = 0;
      cVar2 = 'Z';
    }
    else {
      iVar4 = 0;
      if (((int8_t)DAT_febeaf47) == -0x78) {
        cVar2 = '\0';
      }
    }
    (*((volatile undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(-0x8b7) * 1u)))) = cVar7;
    (*((volatile undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(-0x8bb) * 1u)))) = uVar6;
    (*((volatile undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(-0x8ba) * 1u)))) = cVar2;
    if ((cVar7 == '\x11') || (uVar6 = 0, cVar2 != '\0')) {
      uVar6 = 1;
    }
    (*((volatile undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(-0x8bc) * 1u)))) = uVar6;
    if (iVar4 == 0) {
      if ((cVar1 == '\x11') || (cVar1 == '\"')) {
        uVar5 = 0x12;
      }
      else {
        uVar5 = 2;
      }
      thunk_publish_routine_or_pending_write_terminal_result_4d0a4(uVar5,0);
    }
    else {
      write_nvm_seven_marker_and_save_request_kind_b91ee(iVar4);
    }
    (*((volatile undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(-0x8b9) * 1u)))) = 0;
  }
  return;
}

void complete_kind_three_or_four_request_12_b92c8(char param_1,char param_2)

{
  undefined4 uVar1;
  
  if (param_1 == '\x03' || param_1 == '\x04') {
    uVar1 = 0x20;
    if (param_2 == '\x10') {
      uVar1 = 0;
    }
    thunk_publish_routine_or_pending_write_terminal_result_4d0a4(0x12,uVar1);
  }
  return;
}

void poll_nvm_seven_and_complete_pending_request_b92f0(void)

{
  uint32_t puVar1;
  uint uVar2;
  
  puVar1 = 0xfebeb800u;
  consume_lifecycle_normalization_request();
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x8b8))))) != '\0') {
    uVar2 = call_nvm_record_status_with_u16_selector_ff0c4(7);
    if ((uVar2 & 0xf0) != 0x20) {
      complete_kind_three_or_four_request_12_b92c8((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x8b8))))), uVar2 & 0xf0);
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x8b8))))) = 0;
    }
  }
  return;
}

void set_byte_febeaf47_b9320(undefined1 param_1)

{
  DAT_febeaf47 = param_1;
  return;
}

void return_only_stub_b9326(void)

{
  return;
}

void return_only_stub_b9328(void)

{
  return;
}

void publish_b078_nonzero_as_5a_b932a(void)

{
  DAT_febeb49c = 0;
  if (DAT_febeb078 != '\0') {
    DAT_febeb49c = 0x5a;
  }
  return;
}

void publish_b067_group_or_f208_magic_inhibit_b933c(void)

{
  if (((((((DAT_febeb067 == '\0') && (DAT_febeb068 == '\0')) && (DAT_febeb069 == '\0')) &&
        ((DAT_febeb06a == '\0' && (DAT_febeb06b == '\0')))) &&
       (((DAT_febeb06c == '\0' && ((DAT_febeb06d == '\0' && (DAT_febeb06e == '\0')))) &&
        (DAT_febeb06f == '\0')))) &&
      (((DAT_febeb070 == '\0' && (DAT_febeb071 == '\0')) &&
       ((DAT_febeb358 == '\0' || (DAT_febeb358 == '\x02')))))) && (DAT_febef208 == -0x5aa5a55b)) {
    DAT_febeb49d = 0;
  }
  else {
    DAT_febeb49d = 0x5a;
  }
  return;
}

void qualify_control_profile_observation(uchar slot)

{
  uchar uVar1;
  short sVar2;
  short sVar3;
  short sVar4;
  short sVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  
  iVar7 = (int)((int)(int16_t)DAT_febef1ca);
  iVar8 = (int)((int)(int16_t)DAT_febef1c6);
  iVar6 = (int)((int)(int16_t)DAT_febeb054);
  if (iVar6 + 0x7fff < 0 == (-1 < iVar6 && iVar6 + 0x7fff < 0) && iVar6 != -0x7fff) {
    sVar2 = ((int)(int16_t)DAT_febeb054);
    if (iVar6 < 0) {
      sVar2 = -((int)(int16_t)DAT_febeb054);
    }
  }
  else {
    sVar2 = 0x7fff;
  }
  if (iVar7 + 0x7fff < 0 == (-1 < iVar7 && iVar7 + 0x7fff < 0) && iVar7 != -0x7fff) {
    sVar3 = ((int)(int16_t)DAT_febef1ca);
    if (iVar7 < 0) {
      sVar3 = -((int)(int16_t)DAT_febef1ca);
    }
  }
  else {
    sVar3 = 0x7fff;
  }
  if (iVar8 + 0x7fff < 0 == (-1 < iVar8 && iVar8 + 0x7fff < 0) && iVar8 != -0x7fff) {
    sVar4 = ((int)(int16_t)DAT_febef1c6);
    if (iVar8 < 0) {
      sVar4 = -((int)(int16_t)DAT_febef1c6);
    }
  }
  else {
    sVar4 = 0x7fff;
  }
  iVar6 = (int)((int)(int16_t)DAT_febef1c8);
  if (iVar6 + 0x7fff < 0 == (-1 < iVar6 && iVar6 + 0x7fff < 0) && iVar6 != -0x7fff) {
    sVar5 = ((int)(int16_t)DAT_febef1c8);
    if (iVar6 < 0) {
      sVar5 = -((int)(int16_t)DAT_febef1c8);
    }
  }
  else {
    sVar5 = 0x7fff;
  }
  iVar7 = (int)(*((volatile int16_t *)camry_host_ptr((uint32_t)(0xaed7eu + (uint32_t)(slot) * 2u))));
  iVar6 = sVar2 - iVar7;
  if (iVar6 < 0 != (sVar2 < 0 != iVar7 < 0 && iVar7 < 0 == iVar6 < 0)) {
    iVar7 = (int)(*((volatile int16_t *)camry_host_ptr((uint32_t)(0xaed88u + (uint32_t)(slot) * 2u))));
    iVar6 = sVar3 - iVar7;
    if (iVar6 < 0 != (sVar3 < 0 != iVar7 < 0 && iVar7 < 0 == iVar6 < 0)) {
      iVar7 = (int)(*((volatile int16_t *)camry_host_ptr((uint32_t)(0xaed92u + (uint32_t)(slot) * 2u))));
      iVar6 = sVar4 - iVar7;
      if (iVar6 < 0 != (sVar4 < 0 != iVar7 < 0 && iVar7 < 0 == iVar6 < 0)) {
        iVar7 = (int)(*((volatile int16_t *)camry_host_ptr((uint32_t)(0xaed9cu + (uint32_t)(slot) * 2u))));
        iVar6 = sVar5 - iVar7;
        if (((((((((iVar6 < 0 != (sVar5 < 0 != iVar7 < 0 && iVar7 < 0 == iVar6 < 0)) &&
                  (DAT_febef159 < "ddddd"[slot])) && ((*((volatile int16_t *)camry_host_ptr((uint32_t)(0xaeda6u + (uint32_t)(slot) * 2u)))) != 0))
                && ((DAT_febef1b6 < (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xaedbau + (uint32_t)(slot) * 2u)))) &&
                    ((*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xaedb0u + (uint32_t)(slot) * 2u)))) < DAT_febef1b6)))) &&
               (DAT_febef091 == '\0')) &&
              (((DAT_febef0a2 == '\0' && (DAT_febef08e == '\0')) &&
               ((DAT_febef084 == '\0' &&
                (((DAT_febef083 == '\0' && (DAT_febef086 == '\0')) && (DAT_febef085 == '\0'))))))))
             && ((DAT_febeb49c == '\0' && (DAT_febeb49d == '\0')))) &&
            (((DAT_febef09e == '\0' &&
              (((DAT_febef0a6 == '\0' && (DAT_febef0a7 == '\0')) &&
               ((DAT_febef094 == '\0' &&
                (((DAT_febef15a == '\0' &&
                  ((*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xaedc4u + (uint32_t)(slot) * 2u)))) <= DAT_febeb084)) &&
                 (DAT_febef161 == '\0')))))))) &&
             (((DAT_febef087 == '\0' && (DAT_febef0c2 == '\0')) && (DAT_febef0a9 == '\0')))))) &&
           ((DAT_febef093 == '\0' && (DAT_febef165 == '\0')))) {
          uVar1 = 'Z';
          goto LAB_000b9570;
        }
      }
    }
  }
  uVar1 = '\0';
LAB_000b9570:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb49eu + (uint32_t)(slot) * 1u)))) = uVar1;
  return;
}

void accumulate_profile_counter_first_a(uchar slot)

{
  int iVar1;
  int iVar2;
  int iVar3;
  short sVar4;
  int iVar5;
  int iVar6;
  uint uVar7;
  
  uVar7 = (uint)slot;
  iVar2 = uVar7 * 2;
  iVar3 = uVar7 * 4;
  sVar4 = *(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb4b2u + (uint32_t)(iVar2) * 1u))));
  iVar5 = *(int *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb554u + (uint32_t)(iVar3) * 1u))));
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb49eu + (uint32_t)(uVar7) * 1u)))) == 'Z') {
    iVar1 = (uint)DAT_febef15b - (int)sVar4;
    iVar6 = iVar1 + iVar5;
    if ((short)iVar1 < 0) {
      iVar6 = iVar6 + 0x100;
    }
  }
  else {
    iVar5 = 0;
    iVar6 = 0;
  }
  *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb4b2u + (uint32_t)(iVar2) * 1u)))) = (ushort)DAT_febef15b;
  if (iVar6 + -0x7fff < 0 == (iVar6 < 0 && -1 < iVar6 + -0x7fff)) {
    iVar6 = 0x7fff;
  }
  if (iVar6 + 0x8000 < 0 != (-1 < iVar6 && iVar6 + 0x8000 < 0)) {
    iVar6 = -0x8000;
  }
  *(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb518u + (uint32_t)(iVar2) * 1u)))) = sVar4;
  *(int *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb554u + (uint32_t)(iVar3) * 1u)))) = iVar6;
  *(int *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb540u + (uint32_t)(iVar3) * 1u)))) = iVar5;
  return;
}

void accumulate_profile_counter_first_b(uchar slot)

{
  int iVar1;
  int iVar2;
  int iVar3;
  short sVar4;
  int iVar5;
  int iVar6;
  uint uVar7;
  
  uVar7 = (uint)slot;
  iVar2 = uVar7 * 2;
  iVar3 = uVar7 * 4;
  sVar4 = *(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb4c6u + (uint32_t)(iVar2) * 1u))));
  iVar5 = *(int *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb57cu + (uint32_t)(iVar3) * 1u))));
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb49eu + (uint32_t)(uVar7) * 1u)))) == 'Z') {
    iVar1 = (uint)DAT_febef15c - (int)sVar4;
    iVar6 = iVar1 + iVar5;
    if ((short)iVar1 < 0) {
      iVar6 = iVar6 + 0x100;
    }
  }
  else {
    iVar5 = 0;
    iVar6 = 0;
  }
  *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb4c6u + (uint32_t)(iVar2) * 1u)))) = (ushort)DAT_febef15c;
  if (iVar6 + -0x7fff < 0 == (iVar6 < 0 && -1 < iVar6 + -0x7fff)) {
    iVar6 = 0x7fff;
  }
  if (iVar6 + 0x8000 < 0 != (-1 < iVar6 && iVar6 + 0x8000 < 0)) {
    iVar6 = -0x8000;
  }
  *(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb52cu + (uint32_t)(iVar2) * 1u)))) = sVar4;
  *(int *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb57cu + (uint32_t)(iVar3) * 1u)))) = iVar6;
  *(int *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb568u + (uint32_t)(iVar3) * 1u)))) = iVar5;
  return;
}

void accumulate_profile_counter_second_a(uchar slot)

{
  int iVar1;
  int iVar2;
  int iVar3;
  short sVar4;
  int iVar5;
  int iVar6;
  uint uVar7;
  
  uVar7 = (uint)slot;
  iVar2 = uVar7 * 2;
  iVar3 = uVar7 * 4;
  sVar4 = *(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb4bcu + (uint32_t)(iVar2) * 1u))));
  iVar5 = *(int *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb5a4u + (uint32_t)(iVar3) * 1u))));
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb49eu + (uint32_t)(uVar7) * 1u)))) == 'Z') {
    iVar1 = (uint)DAT_febef15d - (int)sVar4;
    iVar6 = iVar1 + iVar5;
    if ((short)iVar1 < 0) {
      iVar6 = iVar6 + 0x100;
    }
  }
  else {
    iVar5 = 0;
    iVar6 = 0;
  }
  *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb4bcu + (uint32_t)(iVar2) * 1u)))) = (ushort)DAT_febef15d;
  if (iVar6 + -0x7fff < 0 == (iVar6 < 0 && -1 < iVar6 + -0x7fff)) {
    iVar6 = 0x7fff;
  }
  if (iVar6 + 0x8000 < 0 != (-1 < iVar6 && iVar6 + 0x8000 < 0)) {
    iVar6 = -0x8000;
  }
  *(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb522u + (uint32_t)(iVar2) * 1u)))) = sVar4;
  *(int *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb5a4u + (uint32_t)(iVar3) * 1u)))) = iVar6;
  *(int *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb590u + (uint32_t)(iVar3) * 1u)))) = iVar5;
  return;
}

void accumulate_profile_counter_second_b(uchar slot)

{
  int iVar1;
  int iVar2;
  int iVar3;
  short sVar4;
  int iVar5;
  int iVar6;
  uint uVar7;
  
  uVar7 = (uint)slot;
  iVar2 = uVar7 * 2;
  iVar3 = uVar7 * 4;
  sVar4 = *(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb4d0u + (uint32_t)(iVar2) * 1u))));
  iVar5 = *(int *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb5ccu + (uint32_t)(iVar3) * 1u))));
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb49eu + (uint32_t)(uVar7) * 1u)))) == 'Z') {
    iVar1 = (uint)DAT_febef15e - (int)sVar4;
    iVar6 = iVar1 + iVar5;
    if ((short)iVar1 < 0) {
      iVar6 = iVar6 + 0x100;
    }
  }
  else {
    iVar5 = 0;
    iVar6 = 0;
  }
  *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb4d0u + (uint32_t)(iVar2) * 1u)))) = (ushort)DAT_febef15e;
  if (iVar6 + -0x7fff < 0 == (iVar6 < 0 && -1 < iVar6 + -0x7fff)) {
    iVar6 = 0x7fff;
  }
  if (iVar6 + 0x8000 < 0 != (-1 < iVar6 && iVar6 + 0x8000 < 0)) {
    iVar6 = -0x8000;
  }
  *(int *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb5ccu + (uint32_t)(iVar3) * 1u)))) = iVar6;
  *(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb536u + (uint32_t)(iVar2) * 1u)))) = sVar4;
  *(int *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb5b8u + (uint32_t)(iVar3) * 1u)))) = iVar5;
  return;
}

void run_init_chain_b975a(uchar param_1)

{
  accumulate_profile_counter_first_a(param_1);
  accumulate_profile_counter_first_b(param_1);
  accumulate_profile_counter_second_a(param_1);
  accumulate_profile_counter_second_b(param_1);
  return;
}

void qualify_control_profile_counter_pairs(uchar slot)

{
  uint uVar1;
  int iVar2;
  uchar uVar3;
  int iVar4;
  int iVar5;
  
  uVar1 = (uint)slot;
  iVar4 = uVar1 * 4;
  iVar5 = *(int *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb554u + (uint32_t)(iVar4) * 1u)))) - *(int *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb57cu + (uint32_t)(iVar4) * 1u))));
  iVar4 = *(int *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb5a4u + (uint32_t)(iVar4) * 1u)))) - *(int *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb5ccu + (uint32_t)(iVar4) * 1u))));
  if (iVar5 + 0x7fffffff < 0 == (-1 < iVar5 && iVar5 + 0x7fffffff < 0) && iVar5 != -0x7fffffff) {
    if (iVar5 < 0) {
      iVar5 = -iVar5;
    }
  }
  else {
    iVar5 = 0x7fffffff;
  }
  if (iVar4 + 0x7fffffff < 0 == (-1 < iVar4 && iVar4 + 0x7fffffff < 0) && iVar4 != -0x7fffffff) {
    if (iVar4 < 0) {
      iVar4 = -iVar4;
    }
  }
  else {
    iVar4 = 0x7fffffff;
  }
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb49eu + (uint32_t)(uVar1) * 1u)))) == 'Z') &&
      (iVar2 = (*((volatile int32_t *)camry_host_ptr((uint32_t)(0xaee00u + (uint32_t)(uVar1) * 4u)))),
      iVar5 - iVar2 < 0 != (iVar5 < 0 != iVar2 < 0 && iVar2 < 0 == iVar5 - iVar2 < 0))) &&
     (iVar5 = (*((volatile int32_t *)camry_host_ptr((uint32_t)(0xaee14u + (uint32_t)(uVar1) * 4u)))),
     iVar4 - iVar5 < 0 != (iVar4 < 0 != iVar5 < 0 && iVar5 < 0 == iVar4 - iVar5 < 0))) {
    uVar3 = 'Z';
  }
  else {
    uVar3 = '\0';
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb4a3u + (uint32_t)(uVar1) * 1u)))) = uVar3;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb49eu + (uint32_t)(uVar1) * 1u)))) = uVar3;
  return;
}

void select_control_profile_counter_floor(uchar slot)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  
  iVar1 = (uint)slot * 4;
  iVar2 = *(int *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb554u + (uint32_t)(iVar1) * 1u))));
  iVar9 = *(int *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb57cu + (uint32_t)(iVar1) * 1u))));
  iVar8 = *(int *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb5a4u + (uint32_t)(iVar1) * 1u))));
  iVar7 = *(int *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb5ccu + (uint32_t)(iVar1) * 1u))));
  if (iVar2 + 0x7fffffff < 0 == (-1 < iVar2 && iVar2 + 0x7fffffff < 0) && iVar2 != -0x7fffffff) {
    iVar3 = iVar2;
    if (iVar2 < 0) {
      iVar3 = -iVar2;
    }
  }
  else {
    iVar3 = 0x7fffffff;
  }
  if (iVar9 + 0x7fffffff < 0 == (-1 < iVar9 && iVar9 + 0x7fffffff < 0) && iVar9 != -0x7fffffff) {
    iVar4 = iVar9;
    if (iVar9 < 0) {
      iVar4 = -iVar9;
    }
  }
  else {
    iVar4 = 0x7fffffff;
  }
  if (iVar8 + 0x7fffffff < 0 == (-1 < iVar8 && iVar8 + 0x7fffffff < 0) && iVar8 != -0x7fffffff) {
    iVar5 = iVar8;
    if (iVar8 < 0) {
      iVar5 = -iVar8;
    }
  }
  else {
    iVar5 = 0x7fffffff;
  }
  if (iVar7 + 0x7fffffff < 0 == (-1 < iVar7 && iVar7 + 0x7fffffff < 0) && iVar7 != -0x7fffffff) {
    iVar6 = iVar7;
    if (iVar7 < 0) {
      iVar6 = -iVar7;
    }
  }
  else {
    iVar6 = 0x7fffffff;
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb4a3u + (uint32_t)(slot) * 1u)))) == 'Z') {
    if (iVar3 - iVar4 < 0 != (iVar3 < 0 != iVar4 < 0 && iVar4 < 0 == iVar3 - iVar4 < 0)) {
      iVar9 = iVar2;
    }
    if (iVar5 - iVar6 < 0 != (iVar5 < 0 != iVar6 < 0 && iVar6 < 0 == iVar5 - iVar6 < 0)) {
      iVar7 = iVar8;
    }
    if (iVar9 + 0x7fffffff < 0 == (-1 < iVar9 && iVar9 + 0x7fffffff < 0) && iVar9 != -0x7fffffff) {
      iVar8 = iVar9;
      if (iVar9 < 0) {
        iVar8 = -iVar9;
      }
    }
    else {
      iVar8 = 0x7fffffff;
    }
    if (iVar7 + 0x7fffffff < 0 == (-1 < iVar7 && iVar7 + 0x7fffffff < 0) && iVar7 != -0x7fffffff) {
      iVar3 = iVar7;
      if (iVar7 < 0) {
        iVar3 = -iVar7;
      }
    }
    else {
      iVar3 = 0x7fffffff;
    }
    iVar2 = iVar7;
    if (iVar8 - iVar3 < 0 != (iVar8 < 0 != iVar3 < 0 && iVar3 < 0 == iVar8 - iVar3 < 0)) {
      iVar2 = iVar9;
    }
  }
  else {
    iVar9 = 0;
    iVar7 = 0;
    iVar2 = 0;
  }
  *(int *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb61cu + (uint32_t)(iVar1) * 1u)))) = iVar2;
  *(int *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb608u + (uint32_t)(iVar1) * 1u)))) = iVar2;
  *(int *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb5e0u + (uint32_t)(iVar1) * 1u)))) = iVar9;
  *(int *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb5f4u + (uint32_t)(iVar1) * 1u)))) = iVar7;
  return;
}

void update_control_profile_threshold(uchar slot)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  
  uVar3 = (uint)slot;
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb4a3u + (uint32_t)(uVar3) * 1u)))) == 'Z') {
    uVar5 = (uint)DAT_febef1b6;
    if (uVar5 <= *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb4dau + (uint32_t)(uVar3 * 2) * 1u))))) {
      uVar5 = (uint)*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb4dau + (uint32_t)(uVar3 * 2) * 1u))));
    }
    uVar6 = (uint)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xaedd8u + (uint32_t)(uVar3) * 2u))));
    uVar4 = (uint)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xaedceu + (uint32_t)(uVar3) * 2u))));
    uVar2 = (uVar4 - uVar6) * (uVar5 - (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xaedecu + (uint32_t)(uVar3) * 2u)))));
    uVar1 = (uint)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xaede2u + (uint32_t)(uVar3) * 2u)))) - (uint)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xaedecu + (uint32_t)(uVar3) * 2u))));
    if (uVar1 != 0) {
      uVar2 = (int)uVar2 / (int)uVar1;
    }
    uVar2 = uVar6 + uVar2;
    if ((uVar2 < uVar4) && (uVar4 = uVar2, uVar2 < uVar6)) {
      uVar4 = uVar6;
    }
  }
  else {
    uVar2 = 0;
    uVar5 = 0;
    uVar4 = (uint)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xaedd8u + (uint32_t)(uVar3) * 2u))));
  }
  *(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb4dau + (uint32_t)(uVar3 * 2) * 1u)))) = (short)uVar5;
  *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb630u + (uint32_t)(uVar3 * 4) * 1u)))) = uVar2;
  *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb644u + (uint32_t)(uVar3 * 4) * 1u)))) = uVar4;
  return;
}

void publish_control_profile_threshold_result(uchar slot)

{
  int iVar1;
  uchar uVar2;
  int iVar3;
  uint uVar4;
  
  uVar4 = (uint)slot;
  iVar3 = *(int *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb644u + (uint32_t)(uVar4 * 4) * 1u))));
  uVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb4a8u + (uint32_t)(uVar4) * 1u))));
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb4a3u + (uint32_t)(uVar4) * 1u)))) == 'Z') {
    iVar1 = *(int *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb61cu + (uint32_t)(uVar4 * 4) * 1u)))) - iVar3;
    if (iVar1 < 0 ==
        (*(int *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb61cu + (uint32_t)(uVar4 * 4) * 1u)))) < 0 != iVar3 < 0 && iVar3 < 0 == iVar1 < 0)) {
      uVar2 = 'Z';
    }
    else {
      uVar2 = '\0';
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb4a8u + (uint32_t)(uVar4) * 1u)))) = uVar2;
  return;
}

void run_init_chain_b997e(uchar param_1)

{
  qualify_control_profile_counter_pairs(param_1);
  select_control_profile_counter_floor(param_1);
  update_control_profile_threshold(param_1);
  publish_control_profile_threshold_result(param_1);
  return;
}

void track_control_profile_source_extrema(uchar slot)

{
  int iVar1;
  short sVar2;
  int iVar3;
  short sVar4;
  int iVar5;
  int iVar6;
  
  iVar1 = (uint)slot * 2;
  iVar5 = (int)*(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb4e6u + (uint32_t)(iVar1) * 1u))));
  sVar2 = *(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb4f0u + (uint32_t)(iVar1) * 1u))));
  iVar3 = (int)sVar2;
  DAT_febeb4e4 = (short)((((int)(int16_t)DAT_febeae5c) * 0x92ad) / 0x10000);
  iVar6 = (int)DAT_febeb4e4;
  sVar4 = DAT_febeb4e4;
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb4a3u + (uint32_t)(slot) * 1u)))) == 'Z') {
    if (iVar6 - iVar5 < 0 != (iVar6 < 0 != iVar5 < 0 && iVar5 < 0 == iVar6 - iVar5 < 0) ||
        iVar6 == iVar5) {
      sVar4 = *(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb4e6u + (uint32_t)(iVar1) * 1u))));
    }
    if (iVar6 - iVar3 < 0 == (iVar6 < 0 != iVar3 < 0 && iVar3 < 0 == iVar6 - iVar3 < 0))
    goto LAB_000b99ec;
  }
  sVar2 = DAT_febeb4e4;
LAB_000b99ec:
  *(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb4e6u + (uint32_t)(iVar1) * 1u)))) = sVar4;
  *(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb4f0u + (uint32_t)(iVar1) * 1u)))) = sVar2;
  return;
}

void reset_control_profile_interval(uchar slot)

{
  int iVar1;
  undefined2 uVar2;
  
  uVar2 = ((int)(int16_t)DAT_febeb4e4);
  iVar1 = (uint)slot * 2;
  *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb4e6u + (uint32_t)(iVar1) * 1u)))) = ((int)(int16_t)DAT_febeb4e4);
  *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb4f0u + (uint32_t)(iVar1) * 1u)))) = uVar2;
  iVar1 = (uint)slot * 4;
  *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb554u + (uint32_t)(iVar1) * 1u)))) = 0;
  *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb57cu + (uint32_t)(iVar1) * 1u)))) = 0;
  *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb5a4u + (uint32_t)(iVar1) * 1u)))) = 0;
  *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb5ccu + (uint32_t)(iVar1) * 1u)))) = 0;
  *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb540u + (uint32_t)(iVar1) * 1u)))) = 0;
  *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb568u + (uint32_t)(iVar1) * 1u)))) = 0;
  *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb590u + (uint32_t)(iVar1) * 1u)))) = 0;
  *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb5b8u + (uint32_t)(iVar1) * 1u)))) = 0;
  return;
}

void average_control_profile_source_interval(uchar slot)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  undefined2 uVar5;
  int iVar6;
  uint uVar7;
  int iVar8;
  uchar uStack_31;
  
  uVar4 = (uint)slot;
  iVar2 = uVar4 * 4;
  uStack_31 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb49eu + (uint32_t)(uVar4) * 1u))));
  iVar6 = *(int *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb680u + (uint32_t)(iVar2) * 1u))));
  iVar3 = uVar4 * 2;
  iVar8 = (int)((int)(int16_t)DAT_febeb4e4);
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb4a3u + (uint32_t)(uVar4) * 1u)))) == 'Z') {
    iVar1 = ((int)*(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb4e6u + (uint32_t)(iVar3) * 1u)))) - (int)*(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb4f0u + (uint32_t)(iVar3) * 1u))))) -
            (uint)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xaedf6u + (uint32_t)(uVar4) * 2u))));
    if (iVar1 < 0 !=
        ((int)*(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb4e6u + (uint32_t)(iVar3) * 1u)))) - (int)*(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb4f0u + (uint32_t)(iVar3) * 1u)))) < 0 &&
        -1 < iVar1)) {
      uVar7 = *(int *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb658u + (uint32_t)(iVar2) * 1u)))) + 1;
      if (0xffff < uVar7) {
        uVar7 = 0x10000;
      }
      if (iVar6 < 0) {
        iVar1 = -0x80000000 - iVar6;
        if (iVar1 - iVar8 < 0 != (iVar1 < 0 != iVar8 < 0 && iVar8 < 0 == iVar1 - iVar8 < 0) ||
            iVar1 == iVar8) goto LAB_000b9ac0;
        iVar8 = -0x80000000;
      }
      else {
        iVar1 = (0x7fffffff - iVar6) - iVar8;
        if (iVar1 < 0 == (0x7fffffff - iVar6 < 0 != iVar8 < 0 && iVar8 < 0 == iVar1 < 0)) {
LAB_000b9ac0:
          iVar8 = iVar8 + iVar6;
        }
        else {
          iVar8 = 0x7fffffff;
        }
      }
      iVar6 = iVar8;
      if (uVar7 != 0) {
        if (iVar8 == -0x80000000 && uVar7 == 0xffffffff) {
          iVar6 = 0;
        }
        else {
          iVar6 = iVar8 / (int)uVar7;
        }
      }
      uVar5 = (undefined2)iVar6;
      goto LAB_000b9ade;
    }
    uStack_31 = '\0';
  }
  iVar8 = 0;
  uVar7 = 0;
  uVar5 = 0;
  reset_control_profile_interval(slot);
LAB_000b9ade:
  *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb658u + (uint32_t)(iVar2) * 1u)))) = uVar7;
  *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb66cu + (uint32_t)(iVar2) * 1u)))) = uVar7;
  *(int *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb680u + (uint32_t)(iVar2) * 1u)))) = iVar8;
  *(int *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb694u + (uint32_t)(iVar2) * 1u)))) = iVar8;
  *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb4fau + (uint32_t)(iVar3) * 1u)))) = uVar5;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb49eu + (uint32_t)(uVar4) * 1u)))) = uStack_31;
  return;
}

void publish_control_profile_interval(uchar slot)

{
  int iVar1;
  int iVar2;
  uchar uVar3;
  short sVar4;
  uint uVar5;
  
  uVar5 = (uint)slot;
  iVar1 = uVar5 * 2;
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb4a8u + (uint32_t)(uVar5) * 1u)))) == 'Z') {
    sVar4 = *(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb4fau + (uint32_t)(iVar1) * 1u))));
    iVar2 = uVar5 * 4;
    *(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb50eu + (uint32_t)(iVar1) * 1u)))) = sVar4;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb49eu + (uint32_t)(uVar5) * 1u)))) = '\0';
    *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb4fau + (uint32_t)(iVar1) * 1u)))) = 0;
    *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb694u + (uint32_t)(iVar2) * 1u)))) = 0;
    *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb680u + (uint32_t)(iVar2) * 1u)))) = 0;
    *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb66cu + (uint32_t)(iVar2) * 1u)))) = 0;
    *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb658u + (uint32_t)(iVar2) * 1u)))) = 0;
    reset_control_profile_interval(slot);
    uVar3 = 'Z';
  }
  else {
    sVar4 = *(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb50eu + (uint32_t)(iVar1) * 1u))));
    uVar3 = '\0';
  }
  (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeb504u + (uint32_t)(uVar5) * 2u)))) = sVar4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb4adu + (uint32_t)(uVar5) * 1u)))) = uVar3;
  return;
}

void track_average_and_publish_profile_source_interval_b9b72(uchar param_1)

{
  track_control_profile_source_extrema(param_1);
  average_control_profile_source_interval(param_1);
  publish_control_profile_interval(param_1);
  return;
}

void run_control_profile_qualification(void)

{
  uint uVar1;
  
  publish_b078_nonzero_as_5a_b932a();
  publish_b067_group_or_f208_magic_inhibit_b933c();
  uVar1 = 0;
  do {
    qualify_control_profile_observation((uchar)uVar1);
    run_init_chain_b975a(uVar1);
    run_init_chain_b997e(uVar1);
    track_average_and_publish_profile_source_interval_b9b72(uVar1);
    uVar1 = uVar1 + 1;
  } while (uVar1 < 5);
  return;
}

void return_only_stub_b9bbe(void)

{
  return;
}

void return_only_stub_b9bc0(void)

{
  return;
}

void refresh_profile_scaled_word(void)

{
  if ((DAT_febef0c0 == '\0') && (published_internal_source_admission_state < 2)) {
    DAT_febebbd8 = (int)((DAT_febef228 * 0x24ab)) / (int)0x10000;
  }
  return;
}

void refresh_profile_received_composite(void)

{
  if ((((DAT_febef069 == '\0') && (published_internal_source_admission_state < 2)) &&
      (DAT_febef154 == '\x02')) && (DAT_febef06b == '\0')) {
    DAT_febeb852 = (short)((int)(int8_t)DAT_febef06f) + ((int)(int16_t)DAT_febef1a0) * 0xf;
  }
  return;
}

void accumulate_profile_unsigned_source(uchar slot)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  ushort uVar4;
  undefined2 uVar5;
  uint32_t puVar7;
  uint uVar6;
  
  uVar3 = (uint)slot;
  iVar1 = uVar3 * 2;
  iVar2 = uVar3 * 4;
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb4a3u + (uint32_t)(uVar3) * 1u)))) == 'Z') {
    puVar7 = ((uint32_t)((uint)(ushort)(*(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb776u + (uint32_t)(iVar1) * 1u)))) + 1)));
    if (((uint32_t)(0xea5fu))<(puVar7)) {
      puVar7 = (0xea60u);
    }
    uVar3 = (uint)DAT_febef1b6 + *(int *)(((undefined *)camry_host_ptr((uint32_t)(0xfebebb24u + (uint32_t)(iVar2) * 1u))));
    if (899999999 < uVar3) {
      uVar3 = 900000000;
    }
    uVar6 = uVar3;
    if ((uintptr_t)(puVar7)!= 0) {
      uVar6 = uVar3 / (uint)(puVar7);
    }
    uVar5 = (undefined2)uVar6;
    uVar4 = DAT_febef1b6;
    if ((uint)DAT_febef1b6 <= (uint)*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb78au + (uint32_t)(iVar1) * 1u))))) {
      uVar4 = *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb78au + (uint32_t)(iVar1) * 1u))));
    }
  }
  else {
    puVar7 = (0x0);
    uVar3 = 0;
    uVar5 = 0;
    uVar4 = 0;
  }
  *(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb794u + (uint32_t)(iVar1) * 1u)))) = (short)puVar7;
  *(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb776u + (uint32_t)(iVar1) * 1u)))) = (short)puVar7;
  *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebebb10u + (uint32_t)(iVar2) * 1u)))) = uVar3;
  *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb780u + (uint32_t)(iVar1) * 1u)))) = uVar5;
  *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebebb24u + (uint32_t)(iVar2) * 1u)))) = uVar3;
  *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb78au + (uint32_t)(iVar1) * 1u)))) = uVar4;
  return;
}

void accumulate_profile_signed_source1(uchar slot)

{
  int iVar1;
  int iVar2;
  int iVar3;
  short sVar4;
  uint32_t puVar5;
  uint uVar6;
  int iVar7;
  short sVar8;
  undefined2 uVar9;
  uint32_t puVar11;
  uint32_t puVar10;
  
  uVar6 = (uint)slot;
  iVar2 = uVar6 * 2;
  iVar3 = uVar6 * 4;
  sVar4 = *(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb7bcu + (uint32_t)(iVar2) * 1u))));
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb4a3u + (uint32_t)(uVar6) * 1u)))) == 'Z') {
    iVar7 = (int)((int)(int16_t)DAT_febef1c6);
    puVar11 = ((uint32_t)((uint)(ushort)(*(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb7a8u + (uint32_t)(iVar2) * 1u)))) + 1)));
    if (((uint32_t)(0xea5fu))<(puVar11)) {
      puVar11 = (0xea60u);
    }
    puVar5 = ((uint32_t)(iVar7 + *(int *)(((undefined *)camry_host_ptr((uint32_t)(0xfebebb4cu + (uint32_t)(iVar3) * 1u))))));
    if ((int)((uint32_t)((uint32_t)(0xffe7003du + (uint32_t)((int)puVar5) * 1u))) < 0 ==
        ((int)(puVar5) < 0 && -1 < (int)((uint32_t)((uint32_t)(0xffe7003du + (uint32_t)((int)puVar5) * 1u))))) {
      puVar5 = ((uint32_t)(0x18ffc3));
    }
    if ((int)((uint32_t)(puVar5 + 0x18ffc3)) < 0 != (-1 < (int)(puVar5) && (int)((uint32_t)(puVar5 + 0x18ffc3)) < 0)) {
      puVar5 = (0xffe7003du);
    }
    puVar10 = ((uint32_t)(puVar5));
    if ((uintptr_t)(puVar11)!= 0) {
      if ((puVar5)== 0x80000000u &&(puVar11)== 0xffffffffu) {
        puVar10 = (0x0);
      }
      else {
        puVar10 = ((uint32_t)((int)(puVar5) / (int)(puVar11)));
      }
    }
    uVar9 = SUB42(puVar10,0);
    iVar1 = sVar4 - iVar7;
    sVar8 = ((int)(int16_t)DAT_febef1c6);
    if (iVar1 < 0 == (sVar4 < 0 != iVar7 < 0 && iVar7 < 0 == iVar1 < 0)) {
      sVar8 = sVar4;
    }
  }
  else {
    puVar11 = (0x0);
    puVar5 = (0x0);
    uVar9 = 0;
    sVar8 = 0;
  }
  *(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb79eu + (uint32_t)(iVar2) * 1u)))) = (short)puVar11;
  *(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb7a8u + (uint32_t)(iVar2) * 1u)))) = (short)puVar11;
  (*((volatile uint32_t *)((((undefined *)camry_host_ptr((uint32_t)(0xfebebb38u + (uint32_t)(iVar3) * 1u))))))) = (puVar5);
  *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb7b2u + (uint32_t)(iVar2) * 1u)))) = uVar9;
  (*((volatile uint32_t *)((((undefined *)camry_host_ptr((uint32_t)(0xfebebb4cu + (uint32_t)(iVar3) * 1u))))))) = (puVar5);
  *(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb7bcu + (uint32_t)(iVar2) * 1u)))) = sVar8;
  return;
}

void accumulate_profile_signed_source2(uchar slot)

{
  int iVar1;
  int iVar2;
  int iVar3;
  short sVar4;
  uint32_t puVar5;
  uint uVar6;
  int iVar7;
  short sVar8;
  undefined2 uVar9;
  uint32_t puVar11;
  uint32_t puVar10;
  
  uVar6 = (uint)slot;
  iVar2 = uVar6 * 2;
  iVar3 = uVar6 * 4;
  sVar4 = *(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb7e4u + (uint32_t)(iVar2) * 1u))));
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb4a3u + (uint32_t)(uVar6) * 1u)))) == 'Z') {
    iVar7 = (int)((int)(int16_t)DAT_febef1c8);
    puVar11 = ((uint32_t)((uint)(ushort)(*(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb7d0u + (uint32_t)(iVar2) * 1u)))) + 1)));
    if (((uint32_t)(0xea5fu))<(puVar11)) {
      puVar11 = (0xea60u);
    }
    puVar5 = ((uint32_t)(iVar7 + *(int *)(((undefined *)camry_host_ptr((uint32_t)(0xfebebb74u + (uint32_t)(iVar3) * 1u))))));
    if ((int)((uint32_t)((uint32_t)(0xffe7003du + (uint32_t)((int)puVar5) * 1u))) < 0 ==
        ((int)(puVar5) < 0 && -1 < (int)((uint32_t)((uint32_t)(0xffe7003du + (uint32_t)((int)puVar5) * 1u))))) {
      puVar5 = ((uint32_t)(0x18ffc3));
    }
    if ((int)((uint32_t)(puVar5 + 0x18ffc3)) < 0 != (-1 < (int)(puVar5) && (int)((uint32_t)(puVar5 + 0x18ffc3)) < 0)) {
      puVar5 = (0xffe7003du);
    }
    puVar10 = ((uint32_t)(puVar5));
    if ((uintptr_t)(puVar11)!= 0) {
      if ((puVar5)== 0x80000000u &&(puVar11)== 0xffffffffu) {
        puVar10 = (0x0);
      }
      else {
        puVar10 = ((uint32_t)((int)(puVar5) / (int)(puVar11)));
      }
    }
    uVar9 = SUB42(puVar10,0);
    iVar1 = sVar4 - iVar7;
    sVar8 = ((int)(int16_t)DAT_febef1c8);
    if (iVar1 < 0 == (sVar4 < 0 != iVar7 < 0 && iVar7 < 0 == iVar1 < 0)) {
      sVar8 = sVar4;
    }
  }
  else {
    puVar11 = (0x0);
    puVar5 = (0x0);
    uVar9 = 0;
    sVar8 = 0;
  }
  *(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb7c6u + (uint32_t)(iVar2) * 1u)))) = (short)puVar11;
  *(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb7d0u + (uint32_t)(iVar2) * 1u)))) = (short)puVar11;
  (*((volatile uint32_t *)((((undefined *)camry_host_ptr((uint32_t)(0xfebebb60u + (uint32_t)(iVar3) * 1u))))))) = (puVar5);
  *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb7dau + (uint32_t)(iVar2) * 1u)))) = uVar9;
  (*((volatile uint32_t *)((((undefined *)camry_host_ptr((uint32_t)(0xfebebb74u + (uint32_t)(iVar3) * 1u))))))) = (puVar5);
  *(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb7e4u + (uint32_t)(iVar2) * 1u)))) = sVar8;
  return;
}

void accumulate_profile_scaled_feedback(uchar slot)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  int iVar5;
  undefined2 uVar6;
  int iVar7;
  undefined2 uVar9;
  uint32_t puVar11;
  int iVar8;
  int iVar10;
  
  uVar4 = (uint)slot;
  iVar1 = uVar4 * 2;
  iVar2 = uVar4 * 4;
  iVar8 = (((int)(int16_t)DAT_febeb054) * 1000) / 0x100;
  iVar7 = (int)*(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb834u + (uint32_t)(iVar1) * 1u))));
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb4a3u + (uint32_t)(uVar4) * 1u)))) == 'Z') {
    puVar11 = ((uint32_t)((uint)(ushort)(*(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb820u + (uint32_t)(iVar1) * 1u)))) + 1)));
    iVar5 = (int)(short)iVar8;
    if (((uint32_t)(0xea5fu))<(puVar11)) {
      puVar11 = (0xea60u);
    }
    iVar3 = iVar8 + *(int *)(((undefined *)camry_host_ptr((uint32_t)(0xfebebbc4u + (uint32_t)(iVar2) * 1u))));
    if (iVar3 + -75000000 < 0 == (iVar3 < 0 && -1 < iVar3 + -75000000)) {
      iVar3 = 75000000;
    }
    if (iVar3 + 75000000 < 0 != (-1 < iVar3 && iVar3 + 75000000 < 0)) {
      iVar3 = -75000000;
    }
    iVar10 = iVar3;
    if ((uintptr_t)(puVar11)!= 0) {
      if (iVar3 == -0x80000000 &&(puVar11)==((uint32_t)((uint32_t)(0xffffffff)))) {
        iVar10 = 0;
      }
      else {
        iVar10 = iVar3 / (int)(puVar11);
      }
    }
    uVar9 = (undefined2)iVar10;
    if (iVar7 - iVar5 < 0 == (iVar7 < 0 != iVar5 < 0 && iVar5 < 0 == iVar7 - iVar5 < 0)) {
      iVar8 = iVar7;
    }
    uVar6 = (undefined2)iVar8;
  }
  else {
    puVar11 = (0x0);
    iVar3 = 0;
    uVar9 = 0;
    uVar6 = 0;
  }
  *(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb816u + (uint32_t)(iVar1) * 1u)))) = (short)puVar11;
  *(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb820u + (uint32_t)(iVar1) * 1u)))) = (short)puVar11;
  *(int *)(((undefined *)camry_host_ptr((uint32_t)(0xfebebbb0u + (uint32_t)(iVar2) * 1u)))) = iVar3;
  *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb82au + (uint32_t)(iVar1) * 1u)))) = uVar9;
  *(int *)(((undefined *)camry_host_ptr((uint32_t)(0xfebebbc4u + (uint32_t)(iVar2) * 1u)))) = iVar3;
  *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb834u + (uint32_t)(iVar1) * 1u)))) = uVar6;
  return;
}

void accumulate_profile_signed_source3(uchar slot)

{
  int iVar1;
  int iVar2;
  short sVar3;
  int iVar4;
  uint uVar5;
  int iVar6;
  short sVar7;
  undefined2 uVar8;
  uint32_t puVar10;
  int iVar9;
  
  uVar5 = (uint)slot;
  iVar1 = uVar5 * 2;
  iVar2 = uVar5 * 4;
  sVar3 = *(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb80cu + (uint32_t)(iVar1) * 1u))));
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb4a3u + (uint32_t)(uVar5) * 1u)))) == 'Z') {
    iVar6 = (int)((int)(int16_t)DAT_febef1ca);
    puVar10 = ((uint32_t)((uint)(ushort)(*(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb7f8u + (uint32_t)(iVar1) * 1u)))) + 1)));
    if (((uint32_t)(0xea5fu))<(puVar10)) {
      puVar10 = (0xea60u);
    }
    iVar4 = iVar6 + *(int *)(((undefined *)camry_host_ptr((uint32_t)(0xfebebb9cu + (uint32_t)(iVar2) * 1u))));
    if (iVar4 + -0x5a0d4 < 0 == (iVar4 < 0 && -1 < iVar4 + -0x5a0d4)) {
      iVar4 = 0x5a0d4;
    }
    if (iVar4 + 0x5a0d4 < 0 != (-1 < iVar4 && iVar4 + 0x5a0d4 < 0)) {
      iVar4 = -0x5a0d4;
    }
    iVar9 = iVar4;
    if ((uintptr_t)(puVar10)!= 0) {
      if (iVar4 == -0x80000000 &&(puVar10)==((uint32_t)((uint32_t)(0xffffffff)))) {
        iVar9 = 0;
      }
      else {
        iVar9 = iVar4 / (int)(puVar10);
      }
    }
    uVar8 = (undefined2)iVar9;
    iVar9 = sVar3 - iVar6;
    sVar7 = ((int)(int16_t)DAT_febef1ca);
    if (iVar9 < 0 == (sVar3 < 0 != iVar6 < 0 && iVar6 < 0 == iVar9 < 0)) {
      sVar7 = sVar3;
    }
  }
  else {
    puVar10 = (0x0);
    iVar4 = 0;
    uVar8 = 0;
    sVar7 = 0;
  }
  *(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb7eeu + (uint32_t)(iVar1) * 1u)))) = (short)puVar10;
  *(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb7f8u + (uint32_t)(iVar1) * 1u)))) = (short)puVar10;
  *(int *)(((undefined *)camry_host_ptr((uint32_t)(0xfebebb88u + (uint32_t)(iVar2) * 1u)))) = iVar4;
  *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb802u + (uint32_t)(iVar1) * 1u)))) = uVar8;
  *(int *)(((undefined *)camry_host_ptr((uint32_t)(0xfebebb9cu + (uint32_t)(iVar2) * 1u)))) = iVar4;
  *(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb80cu + (uint32_t)(iVar1) * 1u)))) = sVar7;
  return;
}

void select_profile_source_extrema(uchar slot)

{
  undefined2 uVar1;
  uint uVar2;
  undefined2 uVar3;
  
  uVar2 = (uint)slot;
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb4a3u + (uint32_t)(uVar2) * 1u)))) == 'Z') {
    uVar1 = *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb4e6u + (uint32_t)(uVar2 * 2) * 1u))));
    uVar3 = *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb4f0u + (uint32_t)(uVar2 * 2) * 1u))));
  }
  else {
    uVar1 = ((int)(int16_t)DAT_febeb4e4);
    uVar3 = ((int)(int16_t)DAT_febeb4e4);
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb6dfu + (uint32_t)(uVar2) * 1u)))) != 'Z') {
      uVar1 = 0;
      uVar3 = 0;
    }
  }
  *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb83eu + (uint32_t)(uVar2 * 2) * 1u)))) = uVar1;
  *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb848u + (uint32_t)(uVar2 * 2) * 1u)))) = uVar3;
  return;
}

void update_control_profile_aggregates(uchar slot)

{
  accumulate_profile_unsigned_source(slot);
  accumulate_profile_signed_source1(slot);
  accumulate_profile_signed_source2(slot);
  accumulate_profile_scaled_feedback(slot);
  accumulate_profile_signed_source3(slot);
  select_profile_source_extrema(slot);
  return;
}

void age_control_profile_source_latch(uchar slot)

{
  int iVar1;
  uint uVar2;
  uchar uVar3;
  ushort uVar4;
  byte bVar5;
  byte bVar6;
  ushort uVar7;
  
  uVar2 = (uint)slot;
  iVar1 = uVar2 * 2;
  uVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb770u + (uint32_t)(uVar2) * 1u))));
  uVar4 = *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb85eu + (uint32_t)(iVar1) * 1u))));
  uVar7 = *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb854u + (uint32_t)(iVar1) * 1u))));
  bVar6 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb6adu + (uint32_t)(uVar2) * 1u))));
  if ((((DAT_febef093 == '\0') && (published_internal_source_admission_state < 2)) &&
      (DAT_febef094 == '\0')) && (400 < DAT_febef1b6)) {
    uVar3 = 'Z';
  }
  else if (uVar3 != 'Z') {
    bVar5 = 0;
    goto LAB_000ba03c;
  }
  bVar5 = bVar6 + 1;
  bVar6 = bVar5;
  if (9 < bVar5) {
    uVar7 = uVar4 + 1;
    if (5999 < uVar7) {
      uVar7 = 6000;
    }
    bVar6 = 0;
    uVar4 = uVar7;
  }
LAB_000ba03c:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb770u + (uint32_t)(uVar2) * 1u)))) = uVar3;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb6a8u + (uint32_t)(uVar2) * 1u)))) = bVar5;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb6adu + (uint32_t)(uVar2) * 1u)))) = bVar6;
  *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb854u + (uint32_t)(iVar1) * 1u)))) = uVar7;
  *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb85eu + (uint32_t)(iVar1) * 1u)))) = uVar4;
  return;
}
