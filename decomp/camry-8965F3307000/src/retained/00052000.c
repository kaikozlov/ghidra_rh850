#include "common.h"

void poll_diagnostic_record_completion(void)

{
  uint32_t puVar1;
  uint uVar2;
  uint uVar3;
  undefined1 uVar4;
  char cVar5;
  char cVar6;
  
  cVar5 = DAT_febe5f86;
  uVar4 = DAT_febe5f85;
  cVar6 = DAT_febe5f83;
  puVar1 = 0xfebeb800u;
  if ((DAT_febe5f83 != '\0') || (DAT_febe5f86 != '\0')) {
    puVar1 = 0xfebeb800u;
    uVar2 = nvm_get_record_status(0);
    uVar3 = nvm_get_record_status(10);
    if ((cVar6 == '\x01') && ((uVar2 & 0xf0) != 0x20)) {
      if ((uVar2 & 0xf0) == 0x10) {
        cVar6 = '\x02';
      }
      else {
        cVar6 = '\x03';
      }
    }
    if ((cVar5 == '\x01') && ((uVar3 & 0xf0) != 0x20)) {
      if ((uVar3 & 0xf0) == 0x10) {
        cVar5 = '\x02';
      }
      else {
        cVar5 = '\x03';
      }
    }
    if ((cVar6 != '\x01') && (cVar5 != '\x01')) {
      if ((cVar6 == '\x03') || (cVar5 == '\x03')) {
        uVar4 = 0x55;
      }
      else {
        uVar4 = 0;
      }
      cVar6 = '\0';
      cVar5 = '\0';
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x587d))))) = cVar6;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x587a))))) = cVar5;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x587b))))) = uVar4;
  return;
}

uint32_t stage_diagnostic_history_record(void)

{
  uint32_t camry_r10_result;
  uint8_t stack_record_ac[172];
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  uint saved_mask;
  
  saved_mask = (camry_r10_result = priority_mask_enter(0xff00));
  iVar4 = 0;
  do {
    iVar3 = iVar4 * 4;
    iVar2 = iVar4 + 1;
    iVar1 = iVar4 + -0xb;
    ((uint32_t *)((stack_record_ac + 16)))[iVar4] = *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe60c0u + (uint32_t)(iVar3) * 1u))));
    ((uint32_t *)((stack_record_ac + 64)))[iVar4] = *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe60f0u + (uint32_t)(iVar3) * 1u))));
    ((uint32_t *)((stack_record_ac + 112)))[iVar4] = *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe6120u + (uint32_t)(iVar3) * 1u))));
    iVar4 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  iVar4 = 0;
  do {
    iVar2 = iVar4 + 1;
    iVar1 = iVar4 + -7;
    (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(((uint32_t *)(stack_record_ac))) + iVar4)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5f71u + (uint32_t)(iVar4) * 1u))));
    ((uint8_t *)((stack_record_ac + 8)))[iVar4] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5f79u + (uint32_t)(iVar4) * 1u))));
    iVar4 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  (camry_r10_result = nvm_set_record(0,((uint32_t *)(stack_record_ac))));
  priority_mask_restore(saved_mask);
  return camry_r10_result;
}

void stage_diagnostic_invocation_record(void)

{
  uint8_t stack_record_10[16];
  uint32_t puVar1;
  uint saved_mask;
  
  puVar1 = 0xfebeb800u;
  saved_mask = priority_mask_enter(0xff00);
  (*((uint16_t *)(stack_record_10 + 0))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x57d8))));
  (*((uint32_t *)(stack_record_10 + 4))) = 0;
  (*((uint16_t *)(stack_record_10 + 2))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x57d6))));
  nvm_set_record(10,(uint *)stack_record_10);
  priority_mask_restore(saved_mask);
  return;
}

void publish_dirty_diagnostic_records(void)

{
  byte bVar1;
  byte bVar2;
  uint32_t puVar3;
  uint saved_mask;
  undefined1 uVar4;
  undefined1 uVar5;
  
  uVar4 = DAT_febe5f86;
  bVar2 = DAT_febe5f84;
  uVar5 = DAT_febe5f83;
  puVar3 = 0xfebeb800u;
  if ((((DAT_febee821 == 'Z') || ((DAT_febe5f84 >> 3 & 1) != 0)) || ((DAT_febe5f84 >> 4 & 1) != 0))
     && (DAT_febe5f84 != 0)) {
    bVar1 = ~DAT_febe5f84;
    puVar3 = 0xfebeb800u;
    saved_mask = priority_mask_enter(0xff00);
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x587c))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x587c))))) & bVar1;
    priority_mask_restore(saved_mask);
    if ((bVar2 & 0xba) != 0) {
      stage_diagnostic_history_record();
    }
    if ((bVar2 & 0x52) != 0) {
      stage_diagnostic_invocation_record();
    }
    if ((bVar2 >> 3 & 1) != 0) {
      uVar5 = 1;
    }
    if ((bVar2 >> 4 & 1) != 0) {
      uVar5 = 1;
      uVar4 = 1;
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x587d))))) = uVar5;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x587a))))) = uVar4;
  return;
}

void service_diagnostic_record_transaction(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint32_t puVar4;
  uchar generation_selector;
  
  puVar4 = 0xfebeb800u;
  generation_selector = 0xa5;
  if ((DAT_febe5f81 == 'Z') || (generation_selector = DAT_febe5f82, DAT_febe5f82 == 'Z')) {
    puVar4 = 0xfebeb800u;
    rebuild_derived_diagnostic_banks(generation_selector);
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x5890))))) = 0;
  iVar3 = 0;
  do {
    if ((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebe602cu + (uint32_t)(iVar3) * 4u)))) != 0) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x5890))))) = 1;
    }
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -4;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  poll_diagnostic_record_completion();
  publish_dirty_diagnostic_records();
  return;
}

void mark_diagnostic_event_failed(uint event,uchar prior_qualification)

{
  int iVar1;
  byte bVar2;
  byte bVar3;
  uint uVar4;
  uint32_t puVar5;
  uint saved_mask;
  byte bVar6;
  uint uVar7;
  
  puVar5 = 0xfebeb800u;
  iVar1 = (event & 0xffff) * 8;
  bVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2fc50u + (uint32_t)(iVar1) * 1u))));
  bVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2fc52u + (uint32_t)(iVar1) * 1u))));
  uVar7 = (uint)bVar3;
  if (((int8_t)DAT_febe5f85) != -0x56) {
    saved_mask = priority_mask_enter(0xff00);
    iVar1 = ((event & 0xffff) >> 5) * 4;
    if ((*(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe6090u + (uint32_t)(iVar1) * 1u)))) >> (event & 0x1f) & 1) == 0) {
      uVar4 = 1 << (event & 0x1f);
      *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe6090u + (uint32_t)(iVar1) * 1u)))) = uVar4 | *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe6090u + (uint32_t)(iVar1) * 1u))));
      *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe60c0u + (uint32_t)(iVar1) * 1u)))) = *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe60c0u + (uint32_t)(iVar1) * 1u)))) | uVar4;
      *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe60f0u + (uint32_t)(iVar1) * 1u)))) = *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe60f0u + (uint32_t)(iVar1) * 1u)))) | uVar4;
      DAT_febe5f81 = 0x5a;
      DAT_febe5f82 = 0x5a;
      uVar4 = 0;
      if (uVar7 < 0xa0) {
        uVar4 = *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x30850u + (uint32_t)(uVar7 * 8) * 1u))));
      }
      if (prior_qualification == 'Z') {
        bVar6 = 6;
      }
      else {
        bVar6 = 2;
      }
      if ((uVar4 != 0) && ((bVar6 & bVar2) != 0)) {
        if ((uVar4 & 0xc00000) != 0xc00000) {
          uVar4 = 0;
          do {
            if (((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5f71u + (uint32_t)(uVar4) * 1u)))) == uVar7) || ((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5f71u + (uint32_t)(uVar4) * 1u)))) == 0)) {
              if (((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5f79u + (uint32_t)(uVar4) * 1u))))) != -1) {
                (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5f79u + (uint32_t)(uVar4) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5f79u + (uint32_t)(uVar4) * 1u)))) + '\x01';
              }
              (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5f71u + (uint32_t)(uVar4) * 1u)))) = bVar3;
              break;
            }
            uVar4 = uVar4 + 1;
          } while (uVar4 < 8);
        }
        if ((*((short *)camry_host_ptr((uint32_t)(puVar5 + -0x57d6)))) != -0x5aa6) {
          (*((undefined2 *)camry_host_ptr((uint32_t)(puVar5 + -0x57d6)))) = 0xa55a;
        }
        (*((undefined2 *)camry_host_ptr((uint32_t)(puVar5 + -0x57d8)))) = 0;
      }
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x587c))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x587c))))) | 2;
    }
    priority_mask_restore(saved_mask);
  }
  return;
}

void mark_diagnostic_event_passed(uint event)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint32_t puVar4;
  uint saved_mask;
  uint uVar5;
  uint uVar6;
  int iVar7;
  uint uVar8;
  
  puVar4 = 0xfebeb800u;
  uVar8 = event & 0xffff;
  if (((uVar8 != 0) && (uVar8 < 0x180)) && (((int8_t)DAT_febe5f85) != -0x56)) {
    iVar7 = 0;
    iVar3 = 0;
    do {
      if (*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x2fc44u + (uint32_t)(iVar3 * 2) * 1u)))) == uVar8) {
        iVar7 = 0x5a;
      }
      iVar2 = iVar3 + 1;
      iVar1 = iVar3 + -5;
      iVar3 = iVar2;
    } while (((iVar1 < 0) || (iVar2 < 0)));
    saved_mask = priority_mask_enter(0xff00);
    iVar3 = (uVar8 >> 5) * 4;
    uVar6 = event & 0x1f;
    uVar5 = *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe6090u + (uint32_t)(iVar3) * 1u))));
    uVar8 = uVar5 >> uVar6 & 1;
    if (iVar7 == 0x5a) {
      if (((uVar8 != 0) || ((*(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe60c0u + (uint32_t)(iVar3) * 1u)))) >> uVar6 & 1) != 0)) ||
         ((*(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe60f0u + (uint32_t)(iVar3) * 1u)))) >> uVar6 & 1) != 0)) {
        uVar8 = ~(1 << uVar6);
        *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe6090u + (uint32_t)(iVar3) * 1u)))) = uVar8 & uVar5;
        *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe60c0u + (uint32_t)(iVar3) * 1u)))) = *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe60c0u + (uint32_t)(iVar3) * 1u)))) & uVar8;
        *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe60f0u + (uint32_t)(iVar3) * 1u)))) = *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe60f0u + (uint32_t)(iVar3) * 1u)))) & uVar8;
        DAT_febe5f81 = 0x5a;
        DAT_febe5f82 = 0x5a;
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x587c))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x587c))))) | 0x20;
      }
    }
    else if (uVar8 != 0) {
      *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe6090u + (uint32_t)(iVar3) * 1u)))) = ~(1 << uVar6) & uVar5;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x587f))))) = 0x5a;
    }
    priority_mask_restore(saved_mask);
  }
  return;
}

void clear_event_bit_from_three_bitmaps_and_mark_dirty_524be(uint param_1)

{
  int iVar1;
  uint32_t puVar2;
  uint saved_mask;
  uint uVar3;
  
  puVar2 = 0xfebeb800u;
  uVar3 = param_1 & 0xffff;
  if (((uVar3 != 0) && (uVar3 < 0x180)) && (((int8_t)DAT_febe5f85) != -0x56)) {
    saved_mask = priority_mask_enter(0xff00);
    iVar1 = (uVar3 >> 5) * 4;
    param_1 = param_1 & 0x1f;
    if ((((*(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe6090u + (uint32_t)(iVar1) * 1u)))) >> param_1 & 1) != 0) ||
        ((*(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe60c0u + (uint32_t)(iVar1) * 1u)))) >> param_1 & 1) != 0)) ||
       ((*(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe60f0u + (uint32_t)(iVar1) * 1u)))) >> param_1 & 1) != 0)) {
      uVar3 = ~(1 << param_1);
      *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe6090u + (uint32_t)(iVar1) * 1u)))) = uVar3 & *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe6090u + (uint32_t)(iVar1) * 1u))));
      *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe60c0u + (uint32_t)(iVar1) * 1u)))) = *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe60c0u + (uint32_t)(iVar1) * 1u)))) & uVar3;
      *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe60f0u + (uint32_t)(iVar1) * 1u)))) = *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe60f0u + (uint32_t)(iVar1) * 1u)))) & uVar3;
      DAT_febe5f81 = 0x5a;
      DAT_febe5f82 = 0x5a;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x587c))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x587c))))) | 0x80;
    }
    priority_mask_restore(saved_mask);
  }
  return;
}

void clear_current_and_first_event_history(void)

{
  int iVar1;
  uint uVar2;
  uint32_t puVar3;
  puVar3 = 0xfebeb800u;
  DAT_febe5f85 = 0xaa;
  uVar2 = 0;
  do {
    iVar1 = uVar2 * 4;
    uVar2 = uVar2 + 1;
    *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe6090u + (uint32_t)(iVar1) * 1u)))) = 0;
    *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe60c0u + (uint32_t)(iVar1) * 1u)))) = 0;
    *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe6120u + (uint32_t)(iVar1) * 1u)))) = 0;
  } while (uVar2 < 0xc);
  rebuild_event_descriptor_bitmap();
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x587f))))) = 0x5a;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x587e))))) = 0x5a;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x587c))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x587c))))) | 8;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x587b))))) = 0xa5;
  return;
}

void clear_second_event_history(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  
  uVar4 = 0;
  do {
    iVar3 = uVar4 * 4;
    uVar4 = uVar4 + 1;
    *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe60f0u + (uint32_t)(iVar3) * 1u)))) = 0;
  } while (uVar4 < 0xc);
  iVar3 = 0;
  do {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5f71u + (uint32_t)(iVar3) * 1u)))) = 0;
    iVar2 = iVar3 + 1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5f79u + (uint32_t)(iVar3) * 1u)))) = 0;
    iVar1 = iVar3 + -7;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  DAT_febe602a = 0;
  DAT_febe6028 = 0;
  DAT_febe5f84 = DAT_febe5f84 | 0x10;
  DAT_febe5f85 = 0xa5;
  return;
}

void set_event_bit_in_three_bitmaps_525e0(uint param_1)

{
  int iVar1;
  uint uVar2;
  
  uVar2 = param_1 & 0xffff;
  if ((uVar2 != 0) && (uVar2 < 0x180)) {
    iVar1 = (uVar2 >> 5) * 4;
    uVar2 = 1 << (param_1 & 0x1f);
    *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe6090u + (uint32_t)(iVar1) * 1u)))) = *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe6090u + (uint32_t)(iVar1) * 1u)))) | uVar2;
    *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe60f0u + (uint32_t)(iVar1) * 1u)))) = *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe60f0u + (uint32_t)(iVar1) * 1u)))) | uVar2;
    *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe60c0u + (uint32_t)(iVar1) * 1u)))) = *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe60c0u + (uint32_t)(iVar1) * 1u)))) | uVar2;
  }
  return;
}

void build_dtc_status_snapshot(uchar *status)

{
  byte bVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  
  uVar4 = 0;
  do {
    bVar1 = 0;
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x30854u + (uint32_t)(uVar4 * 8) * 1u)))) == '\x01') {
      uVar3 = uVar4 >> 5;
      uVar2 = uVar4 & 0x1f;
      bVar1 = ((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebe602cu + (uint32_t)(uVar3) * 4u)))) >> uVar2 & 1) != 0;
      if (((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebe6040u + (uint32_t)(uVar3) * 4u)))) >> uVar2 & 1) != 0) {
        bVar1 = bVar1 | 0x28;
      }
      if (((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebe6054u + (uint32_t)(uVar3) * 4u)))) >> uVar2 & 1) != 0) {
        bVar1 = bVar1 | 0x80;
      }
    }
    status[uVar4] = bVar1;
    uVar4 = uVar4 + 1;
  } while (uVar4 < 0xa0);
  uVar4 = 0;
  do {
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x30854u + (uint32_t)((uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2fc52u + (uint32_t)(uVar4 * 8) * 1u)))) * 8) * 1u)))) == '\x01') {
      bVar1 = status[(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2fc52u + (uint32_t)(uVar4 * 8) * 1u))))];
      if (((*(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe6120u + (uint32_t)((uVar4 >> 5) * 4) * 1u)))) >> (uVar4 & 0x1f) & 1) == 0) &&
         ((bVar1 >> 3 & 1) == 0)) {
        status[(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2fc52u + (uint32_t)(uVar4 * 8) * 1u))))] = bVar1 | 0x10;
      }
    }
    uVar4 = uVar4 + 1;
  } while (uVar4 < 0x180);
  return;
}

uint count_nonzero_dtcs_matching_status_mask_526cc(byte param_1)

{
  uint uVar1;
  uint uVar2;
  byte local_a8 [160];
  
  build_dtc_status_snapshot(local_a8);
  uVar2 = 0;
  uVar1 = 0;
  do {
    if (((param_1 & local_a8[uVar1]) != 0) &&
       (*(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x30850u + (uint32_t)(uVar1 * 8) * 1u)))) != 0)) {
      uVar2 = (uVar2 + 1) & 0xffff;
    }
    uVar1 = uVar1 + 1;
  } while (uVar1 < 0xa0);
  return uVar2;
}

void list_active_mapped_bytes_from_first64_bitmap_bits_52710(int param_1,uint param_2)

{
  uint *puVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  uint auStack_14 [5];
  
  uVar3 = 0;
  do {
    iVar2 = uVar3 * 4;
    puVar1 = auStack_14 + uVar3;
    uVar3 = uVar3 + 1;
    *puVar1 = *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe6068u + (uint32_t)(iVar2) * 1u)))) | *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe607cu + (uint32_t)(iVar2) * 1u))));
  } while (uVar3 < 5);
  uVar4 = 0;
  uVar3 = 0;
  do {
    if (((((auStack_14[uVar3 >> 5] >> (uVar3 & 0x1f) & 1) != 0) && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2fc04u + (uint32_t)(uVar3) * 1u)))) != '\0'))
        && (param_1 != 0)) && ((param_2 & 0xff) != 0)) {
      (*((undefined1 *)camry_host_ptr((uint32_t)(uVar4 + param_1)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2fc04u + (uint32_t)(uVar3) * 1u))));
      uVar4 = uVar4 + 1 & 0xff;
      if ((param_2 & 0xff) <= uVar4) {
        return;
      }
    }
    uVar3 = uVar3 + 1;
  } while (uVar3 < 0x40);
  return;
}

uint scan_dtc_status_snapshot(uchar mask,uint *dtc,uchar *status,ushort start_index)

{
  byte bVar1;
  uint32_t extraout_r7;
  uint32_t extraout_r8;
  uint uVar2;
  
  uVar2 = (uint)start_index;
  if (uVar2 == 1) {
    build_dtc_status_snapshot(dtc_status_iteration_snapshot);
    
    
  }
  while( true ) {
    if (0x9f < uVar2) {
      return 0;
    }
    bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5f87u + (uint32_t)(uVar2) * 1u))));
    if (((mask & bVar1) != 0) && (*(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x30850u + (uint32_t)(uVar2 * 8) * 1u)))) != 0)) break;
    uVar2 = uVar2 + 1;
  }
  *dtc = *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x30850u + (uint32_t)(uVar2 * 8) * 1u))));
  *status = bVar1;
  return uVar2;
}

undefined4 test_dtc_retention_or_all_mapped_event_bits_set_52830(int param_1)

{
  uint uVar1;
  uint uVar2;
  
  uVar1 = 0;
  while (param_1 != *(int *)(((undefined *)camry_host_ptr((uint32_t)(0x30850u + (uint32_t)(uVar1 * 8) * 1u))))) {
    uVar1 = uVar1 + 1 & 0xff;
    if (0x9f < uVar1) {
      return 0;
    }
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x30854u + (uint32_t)(uVar1 * 8) * 1u)))) == '\x01') {
    uVar2 = 0;
    if ((1 << (uVar1 & 0x1f) & (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebe6040u + (uint32_t)(uVar1 >> 5) * 4u))))) != 0) {
      return 0x5a;
    }
    do {
      if (((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2fc52u + (uint32_t)(uVar2 * 8) * 1u)))) == uVar1) &&
         ((1 << (uVar2 & 0x1f) & *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe6120u + (uint32_t)((uVar2 >> 5) * 4) * 1u))))) == 0)) {
        return 0;
      }
      uVar2 = uVar2 + 1 & 0xffff;
    } while (uVar2 < 0x180);
  }
  return 0x5a;
}

byte compose_dtc_status_from_bitmaps_and_mapping_coverage_528bc(uint param_1)

{
  uint uVar1;
  int iVar2;
  uint uVar3;
  byte bVar4;
  
  uVar1 = (param_1 & 0xff) >> 5;
  uVar3 = param_1 & 0x1f;
  bVar4 = ((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebe602cu + (uint32_t)(uVar1) * 4u)))) >> uVar3 & 1) != 0;
  if (((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebe6040u + (uint32_t)(uVar1) * 4u)))) >> uVar3 & 1) != 0) {
    bVar4 = bVar4 | 0x28;
  }
  if (((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebe6054u + (uint32_t)(uVar1) * 4u)))) >> uVar3 & 1) != 0) {
    bVar4 = bVar4 | 0x80;
  }
  iVar2 = test_dtc_retention_or_all_mapped_event_bits_set_52830(*(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0x30850u + (uint32_t)((param_1 & 0xff) * 8) * 1u)))));
  if (iVar2 == 0) {
    bVar4 = bVar4 | 0x10;
  }
  return bVar4;
}

undefined4 lookup_dtc_code_and_store_composed_status_52922(int param_1,int param_2)

{
  uint uVar1;
  byte bVar2;
  undefined1 uVar3;
  
  if ((param_2 != 0) && (param_1 != 0)) {
    uVar1 = 1;
    do {
      bVar2 = *((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2fc52u + (uint32_t)(uVar1 * 8) * 1u)));
      if (*(int *)(((undefined *)camry_host_ptr((uint32_t)(0x30850u + (uint32_t)((uint)bVar2 * 8) * 1u)))) == param_1) {
        uVar3 = compose_dtc_status_from_bitmaps_and_mapping_coverage_528bc(bVar2);
        *((undefined1 *)camry_host_ptr((uint32_t)param_2)) = uVar3;
        return 0x5a;
      }
      uVar1 = uVar1 + 1;
    } while (uVar1 < 0x180);
  }
  return 0;
}

void serialize_eight_dtc_history_code_status_pairs_52972(int param_1,uint param_2)

{
  uint8_t stack_record_20[32];
  int iVar1;
  undefined1 *puVar2;
  undefined1 uVar3;
  int iVar4;
  uint uVar5;
  undefined4 uVar6;
  uint uVar7;
  uint uVar8;
  
  for (iVar4 = 0; iVar1 = iVar4 - (param_2 & 0xffff), ((iVar1 < 0) || (iVar4 < 0));
      iVar4 = iVar4 + 1) {
    (*((undefined1 *)camry_host_ptr((uint32_t)(iVar4 + param_1)))) = 0;
  }
  uVar5 = priority_mask_enter(0xff00);
  uVar8 = 0;
  do {
    uVar7 = uVar8 + 1;
    ((uint8_t *)((stack_record_20 + 8)))[uVar8] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5f71u + (uint32_t)(uVar8) * 1u))));
    ((uint8_t *)(stack_record_20))[uVar8] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5f79u + (uint32_t)(uVar8) * 1u))));
    uVar8 = uVar7;
  } while (uVar7 < 8);
  priority_mask_restore(uVar5);
  uVar5 = 0;
  uVar8 = 0;
  do {
    uVar7 = (uint)((uint8_t *)((stack_record_20 + 8)))[uVar8];
    uVar3 = ((uint8_t *)(stack_record_20))[uVar8];
    if (-1 < (int)((uVar5 + 3) - (param_2 & 0xffff))) {
      return;
    }
    if ((uVar7 != 0) && (uVar7 < 0xa0)) {
      uVar6 = *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0x30850u + (uint32_t)(uVar7 * 8) * 1u))));
      puVar2 = ((undefined1 *)camry_host_ptr((uint32_t)(uVar5 + param_1)));
      uVar5 = uVar5 + 3 & 0xff;
      puVar2[2] = (char)uVar6;
      *puVar2 = (char)((uint)uVar6 >> 0x10);
      puVar2[1] = (char)((uint)uVar6 >> 8);
      (*((undefined1 *)camry_host_ptr((uint32_t)(uVar5 + param_1)))) = uVar3;
      uVar5 = uVar5 + 1 & 0xff;
    }
    uVar8 = uVar8 + 1;
  } while (uVar8 < 8);
  return;
}

uint set_event_state_dirty_bit1_under_priority_mask_52a10(void)

{
  uint32_t puVar1;
  uint saved_mask;
  
  puVar1 = 0xfebeb800u;
  saved_mask = priority_mask_enter(0xff00);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x587c))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x587c))))) | 2;
  priority_mask_restore(saved_mask);
  return saved_mask;
}

void mark_diagnostic_healthy_observed(uint event)

{
  int iVar1;
  uint saved_mask;
  
  if ((event & 0xffff) - 1 < 0x17f) {
    iVar1 = ((event & 0xffff) >> 5) * 4;
    if ((*(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe6120u + (uint32_t)(iVar1) * 1u)))) >> (event & 0x1f) & 1) == 0) {
      saved_mask = priority_mask_enter(0xff00);
      *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe6120u + (uint32_t)(iVar1) * 1u)))) = *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe6120u + (uint32_t)(iVar1) * 1u)))) | 1 << (event & 0x1f);
      priority_mask_restore(saved_mask);
    }
  }
  return;
}

void clear_diagnostic_supplement(uchar *destination)

{
  uchar *puVar1;
  uint uVar2;
  
  uVar2 = 0;
  do {
    puVar1 = destination + uVar2 * 4;
    uVar2 = uVar2 + 1;
    puVar1[0] = '\0';
    puVar1[1] = '\0';
    puVar1[2] = '\0';
    puVar1[3] = '\0';
  } while (uVar2 < 0x12);
  return;
}

void 
copy_diagnostic_capture(F33DiagnosticCapture *destination,F33DiagnosticCapture *source)

{
  int iVar1;
  uint uVar2;
  
  uVar2 = 0;
  do {
    iVar1 = uVar2 * 4;
    uVar2 = uVar2 + 1;
    *(undefined4 *)(destination->profile_prefix + iVar1) =
         *(undefined4 *)(source->profile_prefix + iVar1);
  } while (uVar2 < 0x3c);
  return;
}

void reset_supplement_and_three_capture_slots_from_template_52aa6(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  clear_diagnostic_supplement((uchar *)((undefined *)camry_host_ptr(0xfebe85acu)));
  copy_diagnostic_capture
            (((F33DiagnosticCapture *)camry_host_ptr((uint32_t)(puVar1 + -0x3524))),(F33DiagnosticCapture *)((undefined *)camry_host_ptr(0x2a1f4u)));
  copy_diagnostic_capture
            (((F33DiagnosticCapture *)camry_host_ptr((uint32_t)(puVar1 + -0x3434))),(F33DiagnosticCapture *)((undefined *)camry_host_ptr(0x2a1f4u)));
  copy_diagnostic_capture
            (((F33DiagnosticCapture *)camry_host_ptr((uint32_t)(puVar1 + -0x3344))),(F33DiagnosticCapture *)((undefined *)camry_host_ptr(0x2a1f4u)));
  return;
}

uint restore_three_nvm_capture_slots_and_validity_bytes_52ad4(void)

{
  bool bVar1;
  uint32_t puVar2;
  uint uVar3;
  
  puVar2 = 0xfebeb800u;
  uVar3 = nvm_get_record(1, ((uint32_t)((uint32_t)(camry_host_addr(diagnostic_capture_slots)))));
  bVar1 = false;
  if (uVar3 != 0x11) {
    bVar1 = (*((short *)camry_host_ptr((uint32_t)(puVar2 + -0x3492)))) != 0;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x56af))))) = bVar1;
  uVar3 = nvm_get_record(2, ((uint32_t)((uint32_t)(puVar2 + -0x3434))));
  bVar1 = false;
  if (uVar3 == 0x10) {
    bVar1 = (*((short *)camry_host_ptr((uint32_t)(puVar2 + -0x33a2)))) != 0;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x56ae))))) = bVar1;
  uVar3 = nvm_get_record(3, ((uint32_t)((uint32_t)(puVar2 + -0x3344))));
  bVar1 = false;
  if (uVar3 == 0x10) {
    bVar1 = (*((short *)camry_host_ptr((uint32_t)(puVar2 + -0x32b2)))) != 0;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x56ad))))) = bVar1;
  return uVar3;
}

void poll_diagnostic_capture_completion(void)

{
  uint32_t puVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  undefined1 uVar5;
  char cVar6;
  char cVar7;
  char cVar8;
  
  cVar6 = DAT_febe6159;
  cVar7 = DAT_febe6158;
  cVar8 = DAT_febe6157;
  uVar5 = DAT_febe6150;
  puVar1 = 0xfebeb800u;
  if (((DAT_febe6157 != '\0') || (DAT_febe6158 != '\0')) || (DAT_febe6159 != '\0')) {
    puVar1 = 0xfebeb800u;
    uVar2 = nvm_get_record_status(1);
    uVar3 = nvm_get_record_status(2);
    uVar4 = nvm_get_record_status(3);
    if ((cVar8 == '\x01') && ((uVar2 & 0xf0) != 0x20)) {
      if ((uVar2 & 0xf0) == 0x10) {
        cVar8 = '\x02';
      }
      else {
        cVar8 = '\x03';
      }
    }
    if ((cVar7 == '\x01') && ((uVar3 & 0xf0) != 0x20)) {
      if ((uVar3 & 0xf0) == 0x10) {
        cVar7 = '\x02';
      }
      else {
        cVar7 = '\x03';
      }
    }
    if ((cVar6 == '\x01') && ((uVar4 & 0xf0) != 0x20)) {
      if ((uVar4 & 0xf0) == 0x10) {
        cVar6 = '\x02';
      }
      else {
        cVar6 = '\x03';
      }
    }
    if (((cVar8 != '\x01') && (cVar7 != '\x01')) && (cVar6 != '\x01')) {
      if (((cVar8 == '\x03') || (cVar7 == '\x03')) || (cVar6 == '\x03')) {
        uVar5 = 0x55;
      }
      else {
        uVar5 = 0;
      }
      cVar8 = '\0';
      cVar7 = '\0';
      cVar6 = '\0';
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x56a9))))) = cVar8;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x56a8))))) = cVar7;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x56a7))))) = cVar6;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x56b0))))) = uVar5;
  return;
}

void publish_dirty_diagnostic_captures(void)

{
  byte bVar1;
  byte bVar2;
  byte bVar3;
  byte bVar4;
  uint32_t puVar5;
  uint saved_mask;
  undefined1 uVar6;
  undefined1 uVar7;
  undefined1 uVar8;
  
  uVar6 = DAT_febe6159;
  uVar7 = DAT_febe6158;
  uVar8 = DAT_febe6157;
  bVar4 = DAT_febe6156;
  bVar3 = DAT_febe6155;
  bVar2 = DAT_febe6154;
  puVar5 = 0xfebeb800u;
  bVar1 = DAT_febe6156 | DAT_febe6155 | DAT_febe6154;
  if (((DAT_febee821 == 'Z') || ((bVar1 >> 2 & 1) != 0)) && ((bVar1 & 6) != 0)) {
    puVar5 = 0xfebeb800u;
    saved_mask = priority_mask_enter(0xff00);
    if ((bVar2 & 6) != 0) {
      nvm_set_record(1,((uint *)camry_host_ptr((uint32_t)(puVar5 + -0x3524))));
    }
    if ((bVar3 & 6) != 0) {
      nvm_set_record(2,((uint *)camry_host_ptr((uint32_t)(puVar5 + -0x3434))));
    }
    if ((bVar4 & 6) != 0) {
      nvm_set_record(3,((uint *)camry_host_ptr((uint32_t)(puVar5 + -0x3344))));
    }
    if ((bVar2 >> 2 & 1) != 0) {
      uVar8 = 1;
    }
    if ((bVar3 >> 2 & 1) != 0) {
      uVar7 = 1;
    }
    if ((bVar4 >> 2 & 1) != 0) {
      uVar6 = 1;
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x56ac))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x56ac))))) & ~bVar2;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x56ab))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x56ab))))) & ~bVar3;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x56aa))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x56aa))))) & ~bVar4;
    priority_mask_restore(saved_mask);
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x56a9))))) = uVar8;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x56a8))))) = uVar7;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x56a7))))) = uVar6;
  return;
}

void snapshot_application_supplement_when_eleven_flags_clear_52ca0(void)

{
  byte *pbVar1;
  byte bVar2;
  uint32_t puVar3;
  uint uVar4;
  F33DiagnosticApplicationSample local_3c;
  
  puVar3 = 0xfebeb800u;
  bVar2 = 0;
  uVar4 = 0;
  do {
    pbVar1 = ((undefined *)camry_host_ptr((uint32_t)(0xfebe615bu + (uint32_t)(uVar4) * 1u)));
    uVar4 = uVar4 + 1;
    bVar2 = bVar2 | *pbVar1;
  } while (uVar4 < 0xb);
  if (bVar2 == 0) {
    snapshot_diagnostic_application(&local_3c,0x32);
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x320e)))) = 0;
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar3 + -0x3254)))) = (*((undefined4 *)camry_host_ptr((uint32_t)(puVar3 + -0x517c))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x324c)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x515c))));
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3212))))) = local_3c.raw[0];
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3250)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x50f2))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x324e)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x50dc))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x324a)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x5148))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3248)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x5158))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3246)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x50f4))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3244)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x5188))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3242)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x5186))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3240)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x5184))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x323e)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x5182))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x323c)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x5180))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x323a)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x517e))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3238)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x51ac))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3236)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x51aa))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3234)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x51a8))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3232)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x51a6))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3230)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x51a4))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x322e)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x51a2))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x322c)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x535e))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x322a)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x535c))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3228)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x535a))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3226)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x5358))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3224)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x5356))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3222)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x5354))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3220)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x5152))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x321e)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x5150))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x321c)))) = (*((uint16_t *)((uint8_t *)&local_3c + 10u)));
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x321a)))) = (*((uint16_t *)((uint8_t *)&local_3c + 12u)));
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3218)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x50da))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3216)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x5146))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3214)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3aba))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3210)))) = (*((uint16_t *)((uint8_t *)&local_3c + 24u)));
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3211))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3814)))));
  }
  return;
}

void increment_capture_age_or_latch_threshold_wrap_52da4(void)

{
  short sVar1;
  uint32_t puVar2;
  uint saved_mask;
  
  puVar2 = 0xfebeb800u;
  if (DAT_febe615a == '\0') {
    saved_mask = priority_mask_enter(0xff00);
    if ((*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x569a)))) < DAT_00030e4c) {
      sVar1 = (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x569a)))) + 1;
    }
    else {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x56a6))))) = 0x5a;
      sVar1 = 0;
    }
    (*((short *)camry_host_ptr((uint32_t)(puVar2 + -0x569a)))) = sVar1;
    priority_mask_restore(saved_mask);
  }
  return;
}

void run_init_chain_52de4(void)

{
  poll_diagnostic_capture_completion();
  publish_dirty_diagnostic_captures();
  snapshot_application_supplement_when_eleven_flags_clear_52ca0();
  increment_capture_age_or_latch_threshold_wrap_52da4();
  return;
}

void copy_diagnostic_supplement(uchar *destination,uchar *source)

{
  int iVar1;
  uint uVar2;
  
  uVar2 = 0;
  do {
    iVar1 = uVar2 * 4;
    uVar2 = uVar2 + 1;
    *(undefined4 *)(destination + iVar1) = *(undefined4 *)(source + iVar1);
  } while (uVar2 < 0x12);
  return;
}

void capture_diagnostic_event(ushort event,ushort capture_kind,uchar qualified)

{
  uint32_t puVar1;
  uint saved_mask;
  int iVar2;
  int iVar3;
  int iVar4;
  F33DiagnosticCapture FStack_108;
  
  puVar1 = 0xfebeb800u;
  if (capture_kind == 4) {
    build_diagnostic_capture_kind4(&FStack_108);
  }
  else if (capture_kind == 10) {
    build_diagnostic_capture_kind10(&FStack_108);
  }
  else {
    build_diagnostic_capture_default(&FStack_108);
  }
  FStack_108.event = event;
  FStack_108.event_copy = event;
  if (qualified == '\x01') {
    clear_diagnostic_supplement(FStack_108.supplemental);
  }
  else {
    copy_diagnostic_supplement(FStack_108.supplemental, ((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x3254))));
  }
  iVar3 = 0;
  iVar4 = *(int *)(((undefined *)camry_host_ptr((uint32_t)(0x30850u + (uint32_t)((uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2fc52u + (uint32_t)((uint)event * 8) * 1u)))) * 8) * 1u))));
  if ((*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x3494)))) < 0x180) {
    iVar3 = *(int *)(((undefined *)camry_host_ptr((uint32_t)(0x30850u + (uint32_t)((uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2fc52u + (uint32_t)((uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x3494)))) * 8) * 1u)))) * 8) * 1u))));
  }
  iVar2 = 0;
  if ((*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x33a4)))) < 0x180) {
    iVar2 = *(int *)(((undefined *)camry_host_ptr((uint32_t)(0x30850u + (uint32_t)((uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2fc52u + (uint32_t)((uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x33a4)))) * 8) * 1u)))) * 8) * 1u))));
  }
  if (((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x56b0)))))) == -0x56) {
    return;
  }
  saved_mask = priority_mask_enter(0xff00);
  if (qualified != '\x01') {
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x56af))))) == '\0') {
      copy_diagnostic_capture(((F33DiagnosticCapture *)camry_host_ptr((uint32_t)(puVar1 + -0x3524))),&FStack_108);
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x56af))))) = 1;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x56ac))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x56ac))))) | 2;
    }
    if (((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x56a6))))) != 'Z') || (iVar4 == iVar3)) || (iVar4 == iVar2)) || (iVar4 == 0))
    goto LAB_00052f22;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x56a6))))) = 0;
  if (qualified == '\x01') {
    copy_diagnostic_capture(((F33DiagnosticCapture *)camry_host_ptr((uint32_t)(puVar1 + -0x3344))),&FStack_108);
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x56ad))))) = 1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x56aa))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x56aa))))) | 2;
  }
  else {
    copy_diagnostic_capture(((F33DiagnosticCapture *)camry_host_ptr((uint32_t)(puVar1 + -0x3434))),&FStack_108);
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x56ae))))) = 1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x56ab))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x56ab))))) | 2;
  }
LAB_00052f22:
  priority_mask_restore(saved_mask);
  return;
}

void selectively_reset_marked_capture_slots_and_mark_dirty_52f32(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe6150 = 0xaa;
  DAT_febe615a = 0x5a;
  DAT_febe6166 = 0;
  if (((volatile F33DiagnosticCapture *)camry_host_ptr(0xfebe82dcu))[0].extended_prefix[0x23] == '\"') {
    DAT_febe6151 = 0;
    puVar1 = 0xfebeb800u;
    copy_diagnostic_capture(diagnostic_capture_slots,(F33DiagnosticCapture *)((undefined *)camry_host_ptr(0x2a1f4u)));
  }
  else {
    ((volatile F33DiagnosticCapture *)camry_host_ptr(0xfebe82dcu))[0].extended_prefix[0x23] = 'D';
  }
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
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x328d))))) == '\"') {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x56ad))))) = 0;
    copy_diagnostic_capture
              (((F33DiagnosticCapture *)camry_host_ptr((uint32_t)(puVar1 + -0x3344))),(F33DiagnosticCapture *)((undefined *)camry_host_ptr(0x2a1f4u)));
  }
  else {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x328d))))) = 0x44;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x56aa))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x56aa))))) | 4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x56b0))))) = 0xa5;
  return;
}

void mark_capture_slots_for_clear(void)

{
  undefined1 uVar1;
  uint32_t puVar2;
  uint32_t puVar3;
  
  uVar1 = DAT_febe6150;
  puVar2 = 0xfebeb800u;
  puVar3 = (0xfebeb800u);
  DAT_febe6150 = 0xaa;
  DAT_febe615a = 0x5a;
  DAT_febe6166 = 0;
  if (DAT_febe6151 == '\x01') {
    if (((volatile F33DiagnosticCapture *)camry_host_ptr(0xfebe82dcu))[0].extended_prefix[0x23] == 'D') {
      DAT_febe6151 = '\0';
      copy_diagnostic_capture
                (diagnostic_capture_slots,(F33DiagnosticCapture *)((undefined *)camry_host_ptr(0x2a1f4u)));
      puVar3 = ((uint32_t)(puVar2));
    }
    else {
      (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(0) * (uint32_t)sizeof(F33DiagnosticCapture) + (uint32_t)offsetof(F33DiagnosticCapture, event))))) = 0;
      ((volatile F33DiagnosticCapture *)camry_host_ptr(0xfebe82dcu))[0].extended_prefix[0x23] = '\"';
      puVar3 = (0xfebeb800u);
    }
    (*((volatile undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(-0x56ac) * 1u)))) = (*((volatile undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(-0x56ac) * 1u)))) | 4;
    uVar1 = 0xa5;
  }
  if ((*((volatile undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(-0x56ae) * 1u)))) == '\x01') {
    if ((*((volatile undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(-0x337d) * 1u)))) == 'D') {
      (*((volatile undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(-0x56ae) * 1u)))) = 0;
      copy_diagnostic_capture
                ((F33DiagnosticCapture *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(-0x3434) * 1u)))),(F33DiagnosticCapture *)((undefined *)camry_host_ptr(0x2a1f4u)));
    }
    else {
      *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(-0x33a4) * 1u)))) = 0;
      (*((volatile undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(-0x337d) * 1u)))) = 0x22;
    }
    (*((volatile undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(-0x56ab) * 1u)))) = (*((volatile undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(-0x56ab) * 1u)))) | 4;
    uVar1 = 0xa5;
  }
  if ((*((volatile undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(-0x56ad) * 1u)))) == '\x01') {
    if ((*((volatile undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(-0x328d) * 1u)))) == 'D') {
      (*((volatile undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(-0x56ad) * 1u)))) = 0;
      copy_diagnostic_capture
                ((F33DiagnosticCapture *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(-0x3344) * 1u)))),(F33DiagnosticCapture *)((undefined *)camry_host_ptr(0x2a1f4u)));
    }
    else {
      *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(-0x32b4) * 1u)))) = 0;
      (*((volatile undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(-0x328d) * 1u)))) = 0x22;
    }
    (*((volatile undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(-0x56aa) * 1u)))) = (*((volatile undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(-0x56aa) * 1u)))) | 4;
    uVar1 = 0xa5;
  }
  (*((volatile undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(-0x56b0) * 1u)))) = uVar1;
  return;
}
