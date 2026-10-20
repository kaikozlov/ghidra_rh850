#include "common.h"

void flush_dirty_dual_capture_bitmap_and_bank_records_55040(void)

{
  uint8_t stack_record_48[72];
  uint8_t stack_record_40[64];
  uint uVar1;
  byte bVar2;
  char cVar3;
  byte bVar4;
  byte bVar5;
  uint uVar6;
  uint32_t puVar7;
  undefined1 uVar8;
  undefined1 uVar9;
  undefined1 uVar10;
  undefined1 uVar11;
  uint uVar12;
  
  uVar9 = DAT_febe89d7;
  bVar5 = DAT_febe89d1;
  bVar4 = DAT_febe89d0;
  uVar10 = DAT_febe89cb;
  uVar11 = DAT_febe89ca;
  cVar3 = DAT_febe89c5;
  puVar7 = 0xfebeb800u;
  uVar6 = 0;
  uVar12 = 0;
  do {
    uVar1 = uVar12 + 1;
    ((uint8_t *)((stack_record_48 + 4)))[uVar12] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe89ccu + (uint32_t)(uVar12) * 1u))));
    bVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe89d2u + (uint32_t)(uVar12) * 1u))));
    ((uint8_t *)(stack_record_48))[uVar12] = bVar2;
    uVar6 = uVar6 | bVar2;
    uVar12 = uVar1;
  } while (uVar1 < 4);
  uVar6 = uVar6 | (DAT_febe89d1 | DAT_febe89d0);
  if (((DAT_febee821 == 'Z') || ((uVar6 >> 2 & 1) != 0)) && ((uVar6 & 6) != 0)) {
    uVar8 = choose_primary_secondary_nvm12_13_record_order_54f6e(DAT_febe89c5,stack_record_40,(stack_record_40 + 2));
    uVar6 = priority_mask_enter(0xff00);
    uVar12 = 0;
    do {
      uVar1 = uVar12 + 1;
      ((uint32_t *)((stack_record_40 + 4)))[uVar12] = *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe89f4u + (uint32_t)(uVar12 * 4) * 1u))));
      uVar12 = uVar1;
    } while (uVar1 < 2);
    uVar12 = 0;
    do {
      uVar1 = uVar12 + 1;
      ((uint32_t *)((stack_record_40 + 4)))[uVar12 + 2] = *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe89fcu + (uint32_t)(uVar12 * 4) * 1u))));
      uVar12 = uVar1;
    } while (uVar1 < 2);
    nvm_set_record(0x11,((uint32_t *)((stack_record_40 + 4))));
    if ((bVar4 & 6) != 0) {
      nvm_set_record((uint)(*((uint16_t *)(stack_record_40 + 0))),((uint *)camry_host_ptr((uint32_t)(puVar7 + -0x317c))));
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(-0x2e3b))))) = uVar8;
    }
    if ((bVar5 & 6) != 0) {
      nvm_set_record((uint)(*((uint16_t *)(stack_record_40 + 2))),((uint *)camry_host_ptr((uint32_t)(puVar7 + -0x311c))));
    }
    uVar12 = 0;
    do {
      if (((((uint8_t *)(stack_record_48))[uVar12] & 0xe) != 0) && (serialize_five_entry_bank_cursor_and_accumulator_to_nvm_54fda(uVar12), (((uint8_t *)(stack_record_48))[uVar12] & 4) != 0)) {
        ((uint8_t *)((stack_record_48 + 4)))[uVar12] = 1;
      }
      uVar12 = uVar12 + 1;
    } while (uVar12 < 4);
    if ((bVar4 >> 2 & 1) != 0) {
      uVar9 = 1;
      if (cVar3 == '\x02') {
        uVar10 = 1;
      }
      else {
        uVar11 = 1;
      }
    }
    if ((bVar5 >> 2 & 1) != 0) {
      uVar9 = 1;
      if (cVar3 == '\x02') {
        uVar11 = 1;
      }
      else {
        uVar10 = 1;
      }
    }
    DAT_febe89d6 = 0;
    DAT_febe89d0 = DAT_febe89d0 & ~bVar4;
    DAT_febe89d1 = DAT_febe89d1 & ~bVar5;
    uVar12 = 0;
    do {
      uVar1 = uVar12 + 1;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe89d2u + (uint32_t)(uVar12) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe89d2u + (uint32_t)(uVar12) * 1u)))) & ~((uint8_t *)(stack_record_48))[uVar12];
      uVar12 = uVar1;
    } while (uVar1 < 4);
    priority_mask_restore(uVar6);
  }
  uVar12 = 0;
  DAT_febe89ca = uVar11;
  DAT_febe89cb = uVar10;
  DAT_febe89d7 = uVar9;
  do {
    uVar6 = uVar12 + 1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe89ccu + (uint32_t)(uVar12) * 1u)))) = ((uint8_t *)((stack_record_48 + 4)))[uVar12];
    uVar12 = uVar6;
  } while (uVar6 < 4);
  return;
}

void poll_and_flush_capture_record_persistence_551bc(void)

{
  poll_dual_record_bitmap_and_bank_write_completion_54e28();
  flush_dirty_dual_capture_bitmap_and_bank_records_55040();
  return;
}

void record_indexed_event_bitmaps_and_rotate_dual_capture_551cc(uint param_1,short param_2)

{
  uint camry_r10_0;

  uint8_t stack_record_70[112];
  int iVar1;
  ushort uVar2;
  uint uVar3;
  uint32_t puVar4;
  undefined4 extraout_r7;
  uint uVar5;
  uint uVar6;
  uint uVar7;
  
  puVar4 = 0xfebeb800u;
  if (param_2 == 10) {
    populate_extended_capture_record_mode10_56336(camry_host_addr(((uint8_t *)stack_record_70 + 0)));
  }
  else {
    populate_extended_capture_record_mode50_564ce(camry_host_addr(((uint16_t *)(stack_record_70))));
  }
  if (((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x2e3c)))))) != -0x56) {
    (camry_r10_0 = priority_mask_enter(0xff00));
    uVar7 = (param_1 & 0xff) >> 5;
    iVar1 = uVar7 * 4;
    uVar5 = 1 << (param_1 & 0x1f);
    uVar3 = (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebe8a0cu + (uint32_t)(uVar7) * 4u))));
    *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe89f4u + (uint32_t)(iVar1) * 1u)))) = *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe89f4u + (uint32_t)(iVar1) * 1u)))) | uVar5;
    uVar6 = *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe89fcu + (uint32_t)(iVar1) * 1u))));
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebe8a0cu + (uint32_t)(uVar7) * 4u)))) = uVar3 | uVar5;
    *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe89fcu + (uint32_t)(iVar1) * 1u)))) = uVar6 | uVar5;
    uVar2 = *(ushort *)(&PTR_DAT_0002aace + (param_1 & 0xff));
    ((uint16_t *)(stack_record_70))[0] = *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0x2ab70u + (uint32_t)((uint)uVar2 * 8) * 1u))));
    iVar1 = (uint)(uVar2 >> 5) * 4;
    *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe8a04u + (uint32_t)(iVar1) * 1u)))) = *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe8a04u + (uint32_t)(iVar1) * 1u)))) | 1 << (uVar2 & 0x1f);
    (*((int16_t *)(stack_record_70 + 70))) = 1;
    if ((*((ushort *)camry_host_ptr((uint32_t)(puVar4 + -0x2e28)))) < 0xff) {
      (*((int16_t *)(stack_record_70 + 70))) = (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + -0x2e28)))) + 1;
    }
    (*((short *)camry_host_ptr((uint32_t)(puVar4 + -0x2e28)))) = (*((int16_t *)(stack_record_70 + 70)));
    __v850_copy_words_24(((uint32_t)((uint32_t)(puVar4 + -0x311c))), ((uint32_t)((uint32_t)(puVar4 + -0x317c))));
    uVar5 = (__v850_copy_words_24(((uint32_t)((uint32_t)(puVar4 + -0x317c))), camry_host_addr(((uint16_t *)(stack_record_70)))), (uint)(uintptr_t)camry_r10_0);
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x2e30))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x2e30))))) | 2;
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x2e2a))))) != '\0') {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x2e2f))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x2e2f))))) | 2;
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x2e2a))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x2e2a))))) + '\x01';
    priority_mask_restore(uVar5);
  }
  return;
}

void append_event_to_five_slot_capture_ring_552a4(uint param_1,short param_2,uint param_3)

{
  uint camry_r10_0;

  uint8_t stack_record_38[56];
  int iVar1;
  ushort uVar2;
  uint uVar3;
  uint32_t puVar4;
  uint uVar5;
  undefined1 uVar6;
  uint uVar7;
  uint uVar8;
  
  puVar4 = 0xfebeb800u;
  param_3 = param_3 & 0xff;
  if (param_2 == 10) {
    populate_compact_capture_record_mode10_56458(camry_host_addr(((uint8_t *)stack_record_38 + 0)));
  }
  else {
    populate_compact_capture_record_mode50_565f2(camry_host_addr(stack_record_38));
  }
  if ((((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x2e3c)))))) != -0x56) && (param_3 < 4)) {
    (camry_r10_0 = priority_mask_enter(0xff00));
    uVar8 = (param_1 & 0xff) >> 5;
    iVar1 = uVar8 * 4;
    uVar7 = 1 << (param_1 & 0x1f);
    uVar3 = (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebe8a0cu + (uint32_t)(uVar8) * 4u))));
    *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe89f4u + (uint32_t)(iVar1) * 1u)))) = *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe89f4u + (uint32_t)(iVar1) * 1u)))) | uVar7;
    uVar5 = *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe89fcu + (uint32_t)(iVar1) * 1u))));
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebe8a0cu + (uint32_t)(uVar8) * 4u)))) = uVar3 | uVar7;
    *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe89fcu + (uint32_t)(iVar1) * 1u)))) = uVar5 | uVar7;
    uVar2 = *(ushort *)(&PTR_DAT_0002aace + (param_1 & 0xff));
    (*((uint16_t *)(stack_record_38 + 0))) = *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0x2ab70u + (uint32_t)((uint)uVar2 * 8) * 1u))));
    iVar1 = (uint)(uVar2 >> 5) * 4;
    *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe8a04u + (uint32_t)(iVar1) * 1u)))) = *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe8a04u + (uint32_t)(iVar1) * 1u)))) | 1 << (uVar2 & 0x1f);
    uVar7 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe89c6u + (uint32_t)(param_3) * 1u))));
    if (*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe89dau + (uint32_t)(param_3 * 2) * 1u)))) < 0xff) {
      (*((int16_t *)(stack_record_38 + 2))) = *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe89dau + (uint32_t)(param_3 * 2) * 1u)))) + 1;
    }
    else {
      (*((int16_t *)(stack_record_38 + 2))) = 1;
    }
    if (4 < uVar7) {
      uVar7 = 0;
    }
    *(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe89dau + (uint32_t)(param_3 * 2) * 1u)))) = (*((int16_t *)(stack_record_38 + 2)));
    uVar3 = (__v850_copy_words_8(((uint32_t)((uint32_t)(puVar4 + ((short)param_3 * 5 + uVar7) * 0x20 + -0x30bc))), camry_host_addr(stack_record_38)), (uint)(uintptr_t)camry_r10_0);
    uVar6 = (undefined1)(uVar7 + 1);
    if (4 < (uVar7 + 1 & 0xff)) {
      uVar6 = 0;
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe89c6u + (uint32_t)(param_3) * 1u)))) = uVar6;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe89d2u + (uint32_t)(param_3) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe89d2u + (uint32_t)(param_3) * 1u)))) | 8;
    priority_mask_restore(uVar3);
  }
  return;
}

void dispatch_event_capture_by_descriptor_class_55398(uint param_1,undefined2 param_2)

{
  char cVar1;
  undefined4 uVar2;
  
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2ab74u + (uint32_t)((uint)*(ushort *)(&PTR_DAT_0002aace + (param_1 & 0xff)) * 8) * 1u))));
  if (cVar1 == '\x11') {
    record_indexed_event_bitmaps_and_rotate_dual_capture_551cc((uint)(byte)param_1, (uint)(ushort)param_2);
  }
  else {
    if (cVar1 == '\"') {
      uVar2 = 0;
    }
    else if (cVar1 == 'D') {
      uVar2 = 3;
    }
    else {
      if (cVar1 != 'U') {
        return;
      }
      uVar2 = 2;
    }
    append_event_to_five_slot_capture_ring_552a4(param_1 & 0xff,param_2,uVar2);
  }
  return;
}

void reinitialize_marked_4444_capture_pair_553ea(void)

{
  int iVar1;
  undefined2 uVar2;
  short sVar3;
  uint uVar4;
  uint32_t puVar5;
  puVar5 = 0xfebeb800u;
  uVar4 = 0;
  do {
    iVar1 = uVar4 * 4;
    uVar4 = uVar4 + 1;
    *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe89f4u + (uint32_t)(iVar1) * 1u)))) = 0;
    *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe8a04u + (uint32_t)(iVar1) * 1u)))) = 0;
  } while (uVar4 < 2);
  if (DAT_febe8686 == 0x4444) {
    puVar5 = 0xfebeb800u;
    __v850_copy_words_24((int)((uint32_t)(0xfebe8684u)), ((uint32_t)(0x2a304u)));
    uVar2 = 0x1111;
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar5 + -0x3136)))) = 1;
  }
  else {
    uVar2 = 0x2222;
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar5 + -0x317a)))) = uVar2;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x2e30))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x2e30))))) | 4;
  if ((*((short *)camry_host_ptr((uint32_t)(puVar5 + -0x311a)))) == 0x4444) {
    __v850_copy_words_24(((uint32_t)((uint32_t)(puVar5 + -0x311c))), ((uint32_t)(0x2a304u)));
    sVar3 = 0x1111;
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar5 + -0x30d6)))) = 1;
  }
  else {
    sVar3 = 0x2222;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x2e2f))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x2e2f))))) | 4;
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + -0x311a)))) = sVar3;
  if (((*((short *)camry_host_ptr((uint32_t)(puVar5 + -0x317a)))) == 0x1111) && (sVar3 == 0x1111)) {
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar5 + -0x2e28)))) = 0x100;
  }
  DAT_febe8a0c = DAT_febe8a0c & 0x3ff;
  DAT_febe8a10 = DAT_febe8a10 & 0xffffffef;
  return;
}

void reinitialize_marked_4444_capture_bank_55492(uint param_1)

{
  int iVar1;
  undefined8 uVar2;
  uint uVar3;
  
  uVar2 = 0xfebeb800;
  param_1 = param_1 & 0xff;
  if (param_1 < 4) {
    uVar3 = 0;
    do {
      iVar1 = ((short)param_1 * 5 + uVar3) * 0x20 + (int)uVar2;
      if ((*((short *)camry_host_ptr((uint32_t)(iVar1 + -0x30b8)))) == 0x4444) {
        __v850_copy_words_8(iVar1 + -0x30bc, ((uint32_t)(0x2a2e4u)));
        (*((undefined2 *)camry_host_ptr((uint32_t)(iVar1 + -0x30b8)))) = 0x1111;
        (*((undefined2 *)camry_host_ptr((uint32_t)(iVar1 + -0x30ba)))) = 0;
      }
      else if ((*((short *)camry_host_ptr((uint32_t)(iVar1 + -0x30b8)))) != 0x1111) {
        (*((undefined2 *)camry_host_ptr((uint32_t)(iVar1 + -0x30b8)))) = 0x2222;
      }
      uVar3 = uVar3 + 1;
    } while (uVar3 < 5);
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebe89e4u + (uint32_t)(param_1) * 4u)))) = 0;
    *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe89dau + (uint32_t)(param_1 * 2) * 1u)))) = 0x100;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe89c6u + (uint32_t)(param_1) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe89d2u + (uint32_t)(param_1) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe89d2u + (uint32_t)(param_1) * 1u)))) | 4;
    if (param_1 == 0) {
      clear_febe505c_word_6a17a();
    }
    if (param_1 == 2) {
      reset_event27_occurrence_counter_56fbc();
    }
  }
  return;
}

void initialize_capture_storage_from_4444_markers_5551a(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe89c4 = 0xaa;
  reinitialize_marked_4444_capture_pair_553ea();
  reinitialize_marked_4444_capture_bank_55492(0);
  reinitialize_marked_4444_capture_bank_55492(3);
  reinitialize_marked_4444_capture_bank_55492(2);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x2e3c))))) = 0xa5;
  return;
}

void reinitialize_marked_2222_capture_pair_55548(void)

{
  int iVar1;
  undefined2 uVar2;
  short sVar3;
  uint uVar4;
  uint32_t puVar5;
  puVar5 = 0xfebeb800u;
  uVar4 = 0;
  do {
    iVar1 = uVar4 * 4;
    uVar4 = uVar4 + 1;
    *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe89fcu + (uint32_t)(iVar1) * 1u)))) = 0;
  } while (uVar4 < 2);
  if (DAT_febe8686 == 0x2222) {
    puVar5 = 0xfebeb800u;
    __v850_copy_words_24((int)((uint32_t)(0xfebe8684u)), ((uint32_t)(0x2a304u)));
    uVar2 = 0x1111;
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar5 + -0x3136)))) = 1;
  }
  else {
    uVar2 = 0x4444;
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar5 + -0x317a)))) = uVar2;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x2e30))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x2e30))))) | 4;
  if ((*((short *)camry_host_ptr((uint32_t)(puVar5 + -0x311a)))) == 0x2222) {
    __v850_copy_words_24(((uint32_t)((uint32_t)(puVar5 + -0x311c))), ((uint32_t)(0x2a304u)));
    sVar3 = 0x1111;
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar5 + -0x30d6)))) = 1;
  }
  else {
    sVar3 = 0x4444;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x2e2f))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x2e2f))))) | 4;
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + -0x311a)))) = sVar3;
  if (((*((short *)camry_host_ptr((uint32_t)(puVar5 + -0x317a)))) == 0x1111) && (sVar3 == 0x1111)) {
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar5 + -0x2e28)))) = 0x100;
  }
  return;
}

void reinitialize_marked_2222_capture_bank_555da(uint param_1)

{
  int iVar1;
  undefined8 uVar2;
  int iVar3;
  uint uVar4;
  
  uVar2 = 0xfebeb800;
  param_1 = param_1 & 0xff;
  iVar3 = 0x5a;
  if (param_1 < 4) {
    uVar4 = 0;
    do {
      iVar1 = ((short)param_1 * 5 + uVar4) * 0x20 + (int)uVar2;
      if ((*((short *)camry_host_ptr((uint32_t)(iVar1 + -0x30b8)))) == 0x2222) {
        __v850_copy_words_8(iVar1 + -0x30bc, ((uint32_t)(0x2a2e4u)));
        (*((undefined2 *)camry_host_ptr((uint32_t)(iVar1 + -0x30b8)))) = 0x1111;
        (*((undefined2 *)camry_host_ptr((uint32_t)(iVar1 + -0x30ba)))) = 0;
      }
      else if ((*((short *)camry_host_ptr((uint32_t)(iVar1 + -0x30b8)))) != 0x1111) {
        iVar3 = 0;
        (*((undefined2 *)camry_host_ptr((uint32_t)(iVar1 + -0x30b8)))) = 0x4444;
      }
      uVar4 = uVar4 + 1;
    } while (uVar4 < 5);
    if (iVar3 == 0x5a) {
      *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe89dau + (uint32_t)(param_1 * 2) * 1u)))) = 0x100;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe89c6u + (uint32_t)(param_1) * 1u)))) = 0;
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe89d2u + (uint32_t)(param_1) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe89d2u + (uint32_t)(param_1) * 1u)))) | 4;
  }
  return;
}

void initialize_capture_storage_from_2222_markers_55658(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe89c4 = 0xaa;
  reinitialize_marked_2222_capture_pair_55548();
  reinitialize_marked_2222_capture_bank_555da(0);
  reinitialize_marked_2222_capture_bank_555da(3);
  reinitialize_marked_2222_capture_bank_555da(2);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x2e3c))))) = 0xa5;
  return;
}

void reset_capture_pair_and_event_bitmaps_55686(void)

{
  int iVar1;
  uint uVar2;
  uint32_t puVar3;
  int extraout_r6;
  int extraout_r6_00;
  
  puVar3 = 0xfebeb800u;
  uVar2 = 0;
  do {
    iVar1 = uVar2 * 4;
    uVar2 = uVar2 + 1;
    *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe89f4u + (uint32_t)(iVar1) * 1u)))) = 0;
    *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe8a04u + (uint32_t)(iVar1) * 1u)))) = 0;
    *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe89fcu + (uint32_t)(iVar1) * 1u)))) = 0;
  } while (uVar2 < 2);
  __v850_copy_words_24((extraout_r6 = ((uint32_t)(0xfebe8684u))), ((uint32_t)(0x2a304u)));
  (*((undefined2 *)camry_host_ptr((uint32_t)(extraout_r6 + 2)))) = 0x1111;
  (*((undefined2 *)camry_host_ptr((uint32_t)(extraout_r6 + 0x46)))) = 1;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x2e30))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x2e30))))) | 4;
  __v850_copy_words_24((extraout_r6_00 = puVar3 + -0x311c), 0x2a304);
  (*((undefined2 *)camry_host_ptr((uint32_t)(extraout_r6_00 + 2)))) = 0x1111;
  (*((undefined2 *)camry_host_ptr((uint32_t)(extraout_r6_00 + 0x46)))) = 1;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x2e2f))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x2e2f))))) | 4;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x2e28)))) = 0x100;
  DAT_febe8a0c = DAT_febe8a0c & 0x3ff;
  DAT_febe8a10 = DAT_febe8a10 & 0xffffffef;
  return;
}

void reset_five_slot_capture_bank_556f2(uint param_1)

{
  undefined8 uVar1;
  int extraout_r6;
  uint uVar2;
  
  uVar1 = 0xfebeb800;
  param_1 = param_1 & 0xff;
  if (param_1 < 4) {
    uVar2 = 0;
    do {
      __v850_copy_words_8((extraout_r6 = ((short)param_1 * 5 + uVar2) * 0x20 + (int)uVar1 + -0x30bc), ((uint32_t)(0x2a2e4u)));
      (*((undefined2 *)camry_host_ptr((uint32_t)(extraout_r6 + 4)))) = 0x1111;
      uVar2 = uVar2 + 1;
      (*((undefined2 *)camry_host_ptr((uint32_t)(extraout_r6 + 2)))) = 0;
    } while (uVar2 < 5);
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebe89e4u + (uint32_t)(param_1) * 4u)))) = 0;
    *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe89dau + (uint32_t)(param_1 * 2) * 1u)))) = 0x100;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe89c6u + (uint32_t)(param_1) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe89d2u + (uint32_t)(param_1) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe89d2u + (uint32_t)(param_1) * 1u)))) | 4;
    if (param_1 == 0) {
      clear_febe505c_word_6a17a();
    }
    if (param_1 == 2) {
      reset_event27_occurrence_counter_56fbc();
    }
  }
  return;
}

void reset_all_enabled_capture_storage_5575e(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe89c4 = 0xaa;
  reset_capture_pair_and_event_bitmaps_55686();
  reset_five_slot_capture_bank_556f2(0);
  reset_five_slot_capture_bank_556f2(3);
  reset_five_slot_capture_bank_556f2(2);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x2e3c))))) = 0xa5;
  return;
}

undefined4 test_event_capture_exempt_or_not_latched_5578c(uint param_1)

{
  undefined4 uVar1;
  
  uVar1 = 0;
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2aacdu + (uint32_t)((param_1 & 0xff) * 4) * 1u)))) == 'Z') ||
     (((uint)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebe8a0cu + (uint32_t)((param_1 & 0xff) >> 5) * 4u)))) >> (param_1 & 0x1f) & 1) == 0)) {
    uVar1 = 0x5a;
  }
  return uVar1;
}

uint serialize_latched_event_identifiers_be16_557c4(int param_1,uint param_2)

{
  uint *puVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  uint auStack_1c [2];
  
  uVar4 = 0;
  if (param_1 != 0) {
    uVar3 = 0;
    do {
      iVar2 = uVar3 * 4;
      puVar1 = auStack_1c + uVar3;
      uVar3 = uVar3 + 1;
      *puVar1 = *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe8a04u + (uint32_t)(iVar2) * 1u))));
    } while (uVar3 < 2);
    uVar3 = 0;
    do {
      if (((auStack_1c[uVar3 >> 5] >> (uVar3 & 0x1f) & 1) != 0) &&
         (*(short *)(((undefined *)camry_host_ptr((uint32_t)(0x2ab70u + (uint32_t)(uVar3 * 8) * 1u)))) != 0)) {
        store_low_u16_big_endian_bytes_6a574(*(short *)(((undefined *)camry_host_ptr((uint32_t)(0x2ab70u + (uint32_t)(uVar3 * 8) * 1u)))), ((undefined1 *)camry_host_ptr((uint32_t)(uVar4 + param_1))));
        uVar4 = uVar4 + 2;
      }
      uVar3 = uVar3 + 1;
    } while (uVar3 < 0x40);
  }
  iVar2 = uVar4 - (param_2 & 0xffff);
  if (iVar2 < 0 == ((int)uVar4 < 0 && -1 < iVar2) && uVar4 != (param_2 & 0xffff)) {
    uVar4 = 0xffffffff;
  }
  return uVar4;
}

undefined4 serialize_matching_capture_sequence_be16_55836(short param_1,int param_2,short *param_3)

{
  undefined4 uVar1;
  
  uVar1 = 0;
  if ((param_2 != 0) && (param_1 == *param_3)) {
    store_low_u16_big_endian_bytes_6a574(param_3[0x23], ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
    uVar1 = 2;
  }
  return uVar1;
}

uint serialize_active_capture_pair_sequences_55858(undefined2 param_1,int param_2,uint param_3)

{
  uint32_t puVar1;
  int iVar2;
  uint uVar3;
  
  puVar1 = 0xfebeb800u;
  uVar3 = 0;
  if ((DAT_febe86e6 != 0x1111) && (DAT_febe86e6 != 0x2222)) {
    puVar1 = 0xfebeb800u;
    uVar3 = serialize_matching_capture_sequence_be16_55836(param_1,param_2,((undefined *)camry_host_ptr(0xfebe86e4u)));
  }
  if (((*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x317a)))) != 0x1111) && ((*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x317a)))) != 0x2222)) {
    iVar2 = serialize_matching_capture_sequence_be16_55836(param_1, uVar3 + param_2, ((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x317c))));
    uVar3 = uVar3 + iVar2;
  }
  iVar2 = uVar3 - (param_3 & 0xffff);
  if (iVar2 < 0 == ((int)uVar3 < 0 && -1 < iVar2) && uVar3 != (param_3 & 0xffff)) {
    uVar3 = 0xffffffff;
  }
  return uVar3;
}

uint serialize_capture_bank_record_numbers_558ae(short param_1,int param_2,uint param_3,ushort param_4)

{
  short *psVar1;
  undefined8 uVar2;
  int iVar3;
  uint uVar4;
  uint uVar5;
  
  uVar2 = 0xfebeb800;
  uVar5 = 0;
  iVar3 = 0;
  if ((param_4 & 0xff) < 4) {
    uVar4 = 0;
    do {
      psVar1 = ((short *)camry_host_ptr((uint32_t)(((short)(param_4 & 0xff) * 5 + uVar4) * 0x20 + (int)uVar2 + -0x30bc)));
      if (((psVar1[2] != 0x1111) && (psVar1[2] != 0x2222)) && (*psVar1 == param_1)) {
        if ((param_3 & 0xffff) < (uVar5 + 2 & 0xffff)) {
          iVar3 = 0x5a;
        }
        else {
          store_low_u16_big_endian_bytes_6a574(((ushort)psVar1[1] + 4) % 5 + 1, ((undefined1 *)camry_host_ptr((uint32_t)(uVar5 + param_2))));
          uVar5 = uVar5 + 2 & 0xffff;
        }
      }
      uVar4 = uVar4 + 1;
    } while (uVar4 < 5);
    if (iVar3 != 0) {
      uVar5 = 0xffffffff;
    }
  }
  return uVar5;
}

undefined4 dispatch_capture_record_number_serialization_5592c(short param_1,undefined4 param_2,undefined2 param_3)

{
  char cVar1;
  undefined4 uVar2;
  uint uVar3;
  
  uVar3 = 0;
  cVar1 = '\0';
  do {
    if (param_1 == *(short *)(((undefined *)camry_host_ptr((uint32_t)(0x2ab70u + (uint32_t)(uVar3 * 8) * 1u))))) {
      cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2ab74u + (uint32_t)(uVar3 * 8) * 1u))));
      break;
    }
    uVar3 = uVar3 + 1 & 0xff;
  } while (uVar3 < 0x40);
  if (cVar1 == '\x11') {
    uVar2 = serialize_active_capture_pair_sequences_55858((uint)(ushort)param_1, param_2, (uint)(ushort)param_3);
  }
  else {
    if (cVar1 == '\"') {
      uVar2 = 0;
    }
    else if (cVar1 == 'D') {
      uVar2 = 3;
    }
    else {
      if (cVar1 != 'U') {
        return 0xfffffffc;
      }
      uVar2 = 2;
    }
    uVar2 = serialize_capture_bank_record_numbers_558ae(param_1,param_2,param_3,uVar2);
  }
  return uVar2;
}

int serialize_matching_capture_pair_fields_5598c(short param_1,short param_2,int param_3,char param_4)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  int iVar4;
  ushort uVar5;
  undefined1 uVar6;
  ushort uVar7;
  short *psVar8;
  int iVar9;
  ushort uStack_2a;
  
  uVar7 = 0;
  iVar9 = 0;
  uVar5 = 0;
  psVar8 = (short *)((undefined *)camry_host_ptr(0xfebe86e4u));
  if (param_4 == '\0') {
    psVar8 = ((undefined *)camry_host_ptr(0xfebe8684u));
  }
  if ((param_3 != 0) && (iVar3 = camry_host_addr(get_capture_field_descriptors_and_count_56664(&uStack_2a)), iVar3 != 0)) {
    if ((param_1 == *psVar8) && ((param_2 == psVar8[0x23] || (param_2 == 0)))) {
      uVar2 = 0;
      do {
        if (param_1 == *(short *)(((undefined *)camry_host_ptr((uint32_t)(0x2ab70u + (uint32_t)(uVar2 * 8) * 1u))))) {
          uVar5 = *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x2ab72u + (uint32_t)(uVar2 * 8) * 1u))));
          break;
        }
        uVar2 = uVar2 + 1;
      } while (uVar2 < 0x40);
    }
    if (uVar5 != 0) {
      store_low_u16_big_endian_bytes_6a574(psVar8[0x23], ((undefined1 *)camry_host_ptr((uint32_t)(param_3))));
      iVar9 = 3;
      for (uVar2 = 0; uVar2 < uStack_2a; uVar2 = uVar2 + 1 & 0xffff) {
        iVar1 = uVar2 * 0x18 + iVar3;
        if ((((*((ushort *)camry_host_ptr((uint32_t)(iVar1 + 0x14)))) & uVar5) != 0) &&
           (iVar4 = test_capture_field_descriptor_and_availability_53190(uVar2,1), iVar4 == 0x5a)) {
          uVar7 = uVar7 + 1;
          store_low_u16_big_endian_bytes_6a574((*((undefined2 *)camry_host_ptr((uint32_t)(iVar1 + 8)))), ((undefined1 *)camry_host_ptr((uint32_t)(iVar9 + param_3))));
          (*((undefined1 *)camry_host_ptr((uint32_t)(iVar9 + 2 + param_3)))) = (*((undefined1 *)camry_host_ptr((uint32_t)(iVar1 + 0x16))));
          (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(iVar1 + 0xc))))))))))))(param_4,iVar9 + 3 + param_3);
          iVar9 = iVar9 + 3 + (uint)(*((byte *)camry_host_ptr((uint32_t)(iVar1 + 0x16))));
        }
      }
      if (uVar7 < 0x100) {
        uVar6 = (undefined1)uVar7;
      }
      else {
        uVar6 = 0;
      }
      (*((undefined1 *)camry_host_ptr((uint32_t)(param_3 + 2)))) = uVar6;
    }
  }
  return iVar9;
}

uint serialize_active_capture_pair_fields_55a76(undefined2 param_1,undefined2 param_2,int param_3,uint param_4)

{
  uint32_t puVar1;
  int iVar2;
  uint uVar3;
  
  puVar1 = 0xfebeb800u;
  uVar3 = 0;
  if ((DAT_febe86e6 != 0x1111) && (DAT_febe86e6 != 0x2222)) {
    puVar1 = 0xfebeb800u;
    uVar3 = serialize_matching_capture_pair_fields_5598c(param_1,param_2,param_3,1);
  }
  if (((*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x317a)))) != 0x1111) && ((*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x317a)))) != 0x2222)) {
    iVar2 = serialize_matching_capture_pair_fields_5598c(param_1,param_2,uVar3 + param_3,0);
    uVar3 = uVar3 + iVar2;
  }
  iVar2 = uVar3 - (param_4 & 0xffff);
  if (iVar2 < 0 == ((int)uVar3 < 0 && -1 < iVar2) && uVar3 != (param_4 & 0xffff)) {
    uVar3 = 0xffffffff;
  }
  return uVar3;
}

undefined2 lookup_capture_identifier_field_mask_55ad0(short param_1)

{
  uint uVar1;
  
  uVar1 = 0;
  do {
    if (param_1 == *(short *)(((undefined *)camry_host_ptr((uint32_t)(0x2ab70u + (uint32_t)(uVar1 * 8) * 1u))))) {
      return *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0x2ab72u + (uint32_t)(uVar1 * 8) * 1u))));
    }
    uVar1 = uVar1 + 1 & 0xff;
  } while (uVar1 < 0x40);
  return 0;
}

uint serialize_capture_ring_slot_fields_55afa(int param_1,ushort param_2,int param_3,uint param_4)

{
  uint8_t stack_record_30[48];
  undefined2 *puVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  ushort uVar6;
  uint uVar7;
  
  iVar4 = 0;
  (*((uint16_t *)(stack_record_30 + 0))) = 0;
  if (param_1 == 0) {
    return 0;
  }
  if (param_3 == 0) {
    return 0;
  }
  if (2 < (param_4 & 0xffff)) {
    (*((uint16_t *)(stack_record_30 + 2))) = param_2;
    store_low_u16_big_endian_bytes_6a574(((*((ushort *)camry_host_ptr((uint32_t)(param_1 + 2)))) + 4) % 5 + 1, ((undefined1 *)camry_host_ptr((uint32_t)(param_3))));
    uVar7 = 3;
    iVar2 = camry_host_addr(get_ring_capture_field_descriptors_and_count_56674(stack_record_30));
    if (iVar2 == 0) {
      return 3;
    }
    uVar6 = 0;
    uVar5 = 0;
    while ((uVar5 < (*((uint16_t *)(stack_record_30 + 0))) && (iVar4 != 0x5a))) {
      puVar1 = ((undefined2 *)camry_host_ptr((uint32_t)(uVar5 * 0x10 + iVar2)));
      if (((puVar1[6] & (*((uint16_t *)(stack_record_30 + 2)))) != 0) &&
         (((uint32_t)((*((volatile uint32_t *)(puVar1 + 4)))) == 0u||
          (iVar3 = (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)(puVar1 + 4)))))))))))(), iVar3 == 0x5a)))) {
        if ((param_4 & 0xffff) < (*(byte *)(puVar1 + 7) + uVar7 + 3 & 0xffff)) {
          iVar4 = 0x5a;
        }
        else {
          store_low_u16_big_endian_bytes_6a574(*puVar1, (undefined1 *)camry_host_ptr((uint32_t)(uVar7 + param_3)));
          (*((undefined1 *)camry_host_ptr((uint32_t)(uVar7 + param_3 + 2)))) = *(undefined1 *)(puVar1 + 7);
          (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)(puVar1 + 2)))))))))))(param_1,uVar7 + param_3 + 3);
          uVar6 = uVar6 + 1;
          uVar7 = uVar7 + *(byte *)(puVar1 + 7) + 3 & 0xffff;
        }
      }
      uVar5 = uVar5 + 1 & 0xffff;
    }
    if (0xff < uVar6) {
      uVar6 = 0;
    }
    (*((char *)camry_host_ptr((uint32_t)(param_3 + 2)))) = (char)uVar6;
    if (iVar4 != 0x5a) {
      return uVar7;
    }
  }
  return 0xffffffff;
}

int serialize_matching_capture_bank_slots_55bde(short param_1,uint param_2,int param_3,undefined2 param_4,byte param_5)

{
  undefined8 uVar1;
  undefined4 uVar2;
  int iVar3;
  uint uVar4;
  int iVar5;
  
  uVar1 = 0xfebeb800;
  iVar5 = 0;
  if (param_5 < 4) {
    uVar2 = lookup_capture_identifier_field_mask_55ad0(param_1);
    uVar4 = 0;
    do {
      iVar3 = ((short)(ushort)param_5 * 5 + uVar4) * 0x20 + (int)uVar1;
      if (((((*((short *)camry_host_ptr((uint32_t)(iVar3 + -0x30b8)))) != 0x1111) && ((*((short *)camry_host_ptr((uint32_t)(iVar3 + -0x30b8)))) != 0x2222)) &&
          ((*((short *)camry_host_ptr((uint32_t)(iVar3 + -0x30bc)))) == param_1)) &&
         (((param_2 & 0xffff) == ((*((ushort *)camry_host_ptr((uint32_t)(iVar3 + -0x30ba)))) + 4) % 5 + 1 ||
          ((param_2 & 0xffff) == 0)))) {
        iVar3 = serialize_capture_ring_slot_fields_55afa(((uint32_t)((uint32_t)(iVar3 + -0x30bc))), uVar2, iVar5 + param_3, param_4);
        if (iVar3 < 0) {
          iVar5 = -1;
        }
        else {
          iVar5 = iVar5 + iVar3;
        }
      }
      uVar4 = uVar4 + 1 & 0xff;
    } while ((uVar4 < 5) && (-1 < iVar5));
  }
  return iVar5;
}

undefined4 dispatch_capture_field_serialization_55c6e(short param_1,ushort param_2, undefined4 param_3, undefined4 param_4)

{
  int iVar1;
  char cVar2;
  undefined4 uVar3;
  uint uVar4;
  
  uVar4 = 0;
  cVar2 = '\0';
  do {
    iVar1 = uVar4 * 8;
    if (param_1 == *(short *)(((undefined *)camry_host_ptr((uint32_t)(0x2ab70u + (uint32_t)(iVar1) * 1u))))) {
      cVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2ab74u + (uint32_t)(iVar1) * 1u))));
      if (((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2ab75u + (uint32_t)(iVar1) * 1u)))) < param_2) && ((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2ab75u + (uint32_t)(iVar1) * 1u)))) != 0))
      goto LAB_00055cda;
      break;
    }
    uVar4 = uVar4 + 1 & 0xff;
  } while (uVar4 < 0x40);
  if (cVar2 == '\x11') {
    uVar3 = serialize_active_capture_pair_fields_55a76((uint)(ushort)param_1, (uint)(ushort)param_2, param_3, (uint)(ushort)param_4);
  }
  else if (cVar2 == '\"') {
    uVar3 = serialize_matching_capture_bank_slots_55bde((uint)(ushort)param_1, (uint)(ushort)param_2, param_3, (uint)(ushort)param_4, 0);
  }
  else if (cVar2 == 'D') {
    uVar3 = serialize_matching_capture_bank_slots_55bde((uint)(ushort)param_1, (uint)(ushort)param_2, param_3, (uint)(ushort)param_4, 3);
  }
  else if (cVar2 == 'U') {
    uVar3 = serialize_matching_capture_bank_slots_55bde((uint)(ushort)param_1, (uint)(ushort)param_2, param_3, (uint)(ushort)param_4, 2);
  }
  else {
LAB_00055cda:
    uVar3 = 0xfffffffc;
  }
  return uVar3;
}

void serialize_capture_pair_time_and_presence_55ce0(char param_1,int param_2)

{
  char cVar1;
  ushort uVar2;
  int iVar3;
  undefined2 *puVar4;
  
  puVar4 = (undefined2 *)((undefined *)camry_host_ptr(0xfebe86e4u));
  if (param_1 == '\0') {
    puVar4 = ((undefined *)camry_host_ptr(0xfebe8684u));
  }
  uVar2 = puVar4[3];
  iVar3 = *(int *)(puVar4 + 4);
  cVar1 = *(char *)(puVar4 + 2);
  if (0xfffe < uVar2) {
    uVar2 = 0xffff;
  }
  if (iVar3 == -1) {
    iVar3 = -1;
  }
  store_low_u16_big_endian_bytes_6a574(uVar2, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  store_u32_big_endian_bytes_6a55c(iVar3, ((undefined1 *)camry_host_ptr((uint32_t)(param_2 + 2))));
  (*((bool *)camry_host_ptr((uint32_t)(param_2 + 6)))) = cVar1 != '\0';
  return;
}

void serialize_capture_pair_bounded_word_with_count_prefix_55d24(char param_1,byte *param_2)

{
  uint base;
  uint value;
  uint count;

  base = 0xfebe86e4u;
  if (param_1 == '\0') {
    base = 0xfebe8684u;
  }
  value = *(volatile uint32_t *)camry_host_ptr(base + 12u);
  count = *(volatile uint8_t *)camry_host_ptr(base + 5u);
  if (value > 0xf423fu) {
    value = 0;
  }
  if (count >= 2u) {
    count = 2;
  }
  store_u32_big_endian_bytes_6a55c(value, param_2);
  *param_2 = (byte)count;
  return;
}

void serialize_capture_pair_field10_scaled_10_over_128_55d86(char param_1, undefined4 param_2)

{
  uint uVar1;
  undefined2 *puVar2;
  
  puVar2 = (undefined2 *)((undefined *)camry_host_ptr(0xfebe86e4u));
  if (param_1 == '\0') {
    puVar2 = ((undefined *)camry_host_ptr(0xfebe8684u));
  }
  uVar1 = (uint)(ushort)puVar2[8] * 10 >> 7;
  if (2999 < uVar1) {
    uVar1 = 3000;
  }
  store_low_u16_big_endian_bytes_6a574(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}

void serialize_capture_pair_field12_capped_12800_55db4(char param_1, undefined4 param_2)

{
  ushort uVar1;
  undefined2 *puVar2;
  
  puVar2 = (undefined2 *)((undefined *)camry_host_ptr(0xfebe86e4u));
  if (param_1 == '\0') {
    puVar2 = ((undefined *)camry_host_ptr(0xfebe8684u));
  }
  uVar1 = puVar2[9];
  if (0x31ff < uVar1) {
    uVar1 = 0x3200;
  }
  store_low_u16_big_endian_bytes_6a574(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}

void serialize_capture_pair_field14_scaled_100_over_256_55df6(char param_1, undefined4 param_2)

{
  uint uVar1;
  undefined2 *puVar2;
  
  puVar2 = (undefined2 *)((undefined *)camry_host_ptr(0xfebe86e4u));
  if (param_1 == '\0') {
    puVar2 = ((undefined *)camry_host_ptr(0xfebe8684u));
  }
  uVar1 = (uint)(ushort)puVar2[10] * 100 >> 8;
  if (0x9c3 < uVar1) {
    uVar1 = 0x9c4;
  }
  store_low_u16_big_endian_bytes_6a574(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}

void serialize_capture_pair_field18_scaled_signed_1000_over_256_55e24(char param_1, undefined4 param_2)

{
  int iVar1;
  undefined2 *puVar2;
  
  puVar2 = (undefined2 *)((undefined *)camry_host_ptr(0xfebe86e4u));
  if (param_1 == '\0') {
    puVar2 = ((undefined *)camry_host_ptr(0xfebe8684u));
  }
  iVar1 = ((short)puVar2[0xc] * 1000) / 0x100;
  if (iVar1 + -25000 < 0 == (iVar1 < 0 && -1 < iVar1 + -25000)) {
    iVar1 = 25000;
  }
  if (iVar1 + 25000 < 0 != (-1 < iVar1 && iVar1 + 25000 < 0)) {
    iVar1 = -25000;
  }
  store_low_u16_big_endian_bytes_6a5ac((int)(short)iVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}

void serialize_capture_pair_field1a_scaled_signed_360_over_1024_55e62(char param_1, undefined4 param_2)

{
  int iVar1;
  undefined2 *puVar2;
  
  puVar2 = (undefined2 *)((undefined *)camry_host_ptr(0xfebe86e4u));
  if (param_1 == '\0') {
    puVar2 = ((undefined *)camry_host_ptr(0xfebe8684u));
  }
  iVar1 = (int)(short)(((short)puVar2[0xd] * 0x168) / 0x400);
  if (iVar1 + -0x7fff < 0 == (iVar1 < 0 && -1 < iVar1 + -0x7fff)) {
    iVar1 = 0x7fff;
  }
  if (iVar1 + 0x7fff < 0 != (-1 < iVar1 && iVar1 + 0x7fff < 0)) {
    iVar1 = -0x7fff;
  }
  store_low_u16_big_endian_bytes_6a5ac(iVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}

void serialize_capture_pair_field1c_clamped_signed12_55ea0(char param_1, undefined4 param_2)

{
  int iVar1;
  undefined2 *puVar2;
  
  puVar2 = (undefined2 *)((undefined *)camry_host_ptr(0xfebe86e4u));
  if (param_1 == '\0') {
    puVar2 = ((undefined *)camry_host_ptr(0xfebe8684u));
  }
  iVar1 = (int)(short)puVar2[0xe];
  if (iVar1 + -0x7ff < 0 == (iVar1 < 0 && -1 < iVar1 + -0x7ff)) {
    iVar1 = 0x7ff;
  }
  if (iVar1 + 0x800 < 0 != (-1 < iVar1 && iVar1 + 0x800 < 0)) {
    iVar1 = -0x800;
  }
  store_low_u16_big_endian_bytes_6a5ac(iVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}

void serialize_capture_pair_field1e_scaled_100_over_256_55ed0(char param_1, undefined4 param_2)

{
  uint uVar1;
  undefined2 *puVar2;
  
  puVar2 = (undefined2 *)((undefined *)camry_host_ptr(0xfebe86e4u));
  if (param_1 == '\0') {
    puVar2 = ((undefined *)camry_host_ptr(0xfebe8684u));
  }
  uVar1 = (uint)(ushort)puVar2[0xf] * 100 >> 8;
  if (0x9c3 < uVar1) {
    uVar1 = 0x9c4;
  }
  store_low_u16_big_endian_bytes_6a574(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}

void serialize_capture_pair_field20_scaled_100_over_256_55efe(char param_1, undefined4 param_2)

{
  uint uVar1;
  undefined2 *puVar2;
  
  puVar2 = (undefined2 *)((undefined *)camry_host_ptr(0xfebe86e4u));
  if (param_1 == '\0') {
    puVar2 = ((undefined *)camry_host_ptr(0xfebe8684u));
  }
  uVar1 = (uint)(ushort)puVar2[0x10] * 100 >> 8;
  if (0x9c3 < uVar1) {
    uVar1 = 0x9c4;
  }
  store_low_u16_big_endian_bytes_6a574(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}

undefined4 serialize_capture_pair_field22_scaled_signed_10_over_128_55f2e(char param_1,undefined4 param_2)

{
  undefined4 uVar1;
  undefined2 *puVar2;
  
  puVar2 = (undefined2 *)((undefined *)camry_host_ptr(0xfebe86e4u));
  if (param_1 == '\0') {
    puVar2 = ((undefined *)camry_host_ptr(0xfebe8684u));
  }
  uVar1 = scale_s16_by10_over128_clamp_minus500_to2000_53532((int)(short)puVar2[0x11]);
  store_low_u16_big_endian_bytes_6a5ac(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return uVar1;
}

void serialize_capture_pair_field40_or_invalid_sentinel_55f52(char param_1,undefined4 param_2)

{
  undefined4 uVar1;
  undefined2 *puVar2;
  
  puVar2 = (undefined2 *)((undefined *)camry_host_ptr(0xfebe86e4u));
  if (param_1 == '\0') {
    puVar2 = ((undefined *)camry_host_ptr(0xfebe8684u));
  }
  uVar1 = 0x7fff;
  if (*(char *)(puVar2 + 0x22) != '\0') {
    uVar1 = scale_s16_by10_over128_clamp_minus500_to2000_53532((int)(short)puVar2[0x20]);
  }
  store_low_u16_big_endian_bytes_6a5ac(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}

void serialize_capture_pair_field42_or_invalid_sentinel_55f82(char param_1,undefined4 param_2)

{
  undefined4 uVar1;
  undefined2 *puVar2;
  
  puVar2 = (undefined2 *)((undefined *)camry_host_ptr(0xfebe86e4u));
  if (param_1 == '\0') {
    puVar2 = ((undefined *)camry_host_ptr(0xfebe8684u));
  }
  uVar1 = 0x7fff;
  if ((*((char *)camry_host_ptr((uint32_t)((int)camry_host_addr(puVar2) + 0x45)))) != '\0') {
    uVar1 = scale_s16_by10_over128_clamp_minus500_to2000_53532((int)(short)puVar2[0x21]);
  }
  store_low_u16_big_endian_bytes_6a5ac(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}
