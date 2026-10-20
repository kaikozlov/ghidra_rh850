#include "common.h"

void nvm_refresh_family2_status(void)

{
  int iVar1;
  undefined8 uVar2;
  uint uVar3;
  uint uVar4;
  
  uVar2 = 0xfebeb800;
  for (uVar4 = 0; uVar4 < nvm_family2_object_count; uVar4 = uVar4 + 1 & 0xffff) {
    iVar1 = (int)uVar2;
    uVar3 = read_repair_redundant_u8
                      (((uint32_t)((uint32_t)(uVar4 + iVar1 + 0x4e50))), ((uint32_t)((uint32_t)(uVar4 + iVar1 + 0x5898))), ((uint32_t)((uint32_t)(uVar4 + iVar1 + 0x58bc))), '0');
    if (uVar3 != 0x10) {
      uVar3 = nvm_check_family2_rom_crc((ushort)uVar4);
      if (uVar3 != 0x10) {
        uVar3 = nvm_check_family2_rom_crc((ushort)uVar4);
      }
      publish_redundant_u8
                ((uchar)uVar3,((uchar *)camry_host_ptr((uint32_t)(uVar4 + iVar1 + 0x4e50))),((uchar *)camry_host_ptr((uint32_t)(uVar4 + iVar1 + 0x5898))),
                 ((uchar *)camry_host_ptr((uint32_t)(uVar4 + iVar1 + 0x58bc))));
    }
  }
  return;
}

uint nvm_set_family2_record(uint object,uint *source)

{
  uint uVar1;
  uint32_t puVar2;
  uint uVar3;
  
  puVar2 = 0xfebeb800u;
  uVar3 = object & 0xffff;
  uVar1 = (uint)nvm_family2_object_count;
  if (uVar3 < uVar1) {
    copy_whole_words
              (((uint32_t *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x2af8cu + (uint32_t)(uVar3) * (uint32_t)sizeof(F33NvmFamily2Descriptor)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmFamily2Descriptor) + (uint32_t)offsetof(F33NvmFamily2Descriptor, ram_buffer)))))))), source, 
               (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x2af8cu + (uint32_t)(uVar3) * (uint32_t)sizeof(F33NvmFamily2Descriptor)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmFamily2Descriptor) + (uint32_t)offsetof(F33NvmFamily2Descriptor, payload_bytes))))));
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(uVar3 + 0x4e5b))))) = 0x5a;
    publish_redundant_u8
              ('\x10', ((undefined *)camry_host_ptr((uint32_t)(puVar2 + uVar3 + 0x4e50))), ((undefined *)camry_host_ptr((uint32_t)(puVar2 + uVar3 + 0x5898))), ((undefined *)camry_host_ptr((uint32_t)(puVar2 + uVar3 + 0x58bc))));
  }
  return (uint)(uVar3 < uVar1);
}

void select_flmd0_internal_pulldown(void)

{
  uint saved_mask;
  uint uVar1;
  byte bVar2;
  
  uVar1 = camry_read32(0xffa00000u);
  if ((uVar1 & 1) != 0) {
    uVar1 = 1;
    saved_mask = priority_mask_enter(0xffff);
    for (bVar2 = 0; ((uVar1 & 1) != 0 && (bVar2 < 3)); bVar2 = bVar2 + 1) {
      camry_write32(0xffa00004u, 0xa5);
      camry_write32(0xffa00000u, 0);
      camry_write32(0xffa00000u, (int)0xffffffff);
      camry_write32(0xffa00000u, 0);
      uVar1 = camry_read32(0xffa00000u);
      __synchronize();
      uVar1 = camry_read32(0xffa00008u);
    }
    priority_mask_restore(saved_mask);
  }
  return;
}

void initialize_nvm_family0_requests_buffers_and_cursors_672c0(void)

{
  uchar *puVar1;
  ushort uVar2;
  int iVar3;
  uint32_t puVar4;
  uint uVar5;
  
  for (iVar3 = 0;
      (int)(iVar3 - (uint)nvm_family0_request_cell_count) < 0 !=
      (iVar3 < 0 && -1 < (int)(iVar3 - (uint)nvm_family0_request_cell_count)); iVar3 = iVar3 + 1
      ) {
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebf0488u + (uint32_t)(iVar3) * (uint32_t)sizeof(F33NvmRequestCell)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmRequestCell) + (uint32_t)offsetof(F33NvmRequestCell, object))))) = 0xffff;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebf0488u + (uint32_t)(iVar3) * (uint32_t)sizeof(F33NvmRequestCell)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmRequestCell) + (uint32_t)offsetof(F33NvmRequestCell, state))))) = 0xff;
  }
  for (iVar3 = 0;
      (int)(iVar3 - (uint)nvm_family0_object_count) < 0 !=
      (iVar3 < 0 && -1 < (int)(iVar3 - (uint)nvm_family0_object_count)); iVar3 = iVar3 + 1) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebf0308u + (uint32_t)(iVar3) * 1u)))) = '\0';
    uVar2 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x2ad8cu + (uint32_t)(iVar3) * (uint32_t)sizeof(F33NvmFamily0RamDescriptor)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmFamily0RamDescriptor) + (uint32_t)offsetof(F33NvmFamily0RamDescriptor, payload_bytes)))));
    puVar4 = ((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x2ad8cu + (uint32_t)(iVar3) * (uint32_t)sizeof(F33NvmFamily0RamDescriptor)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmFamily0RamDescriptor) + (uint32_t)offsetof(F33NvmFamily0RamDescriptor, buffer)))))));
    for (uVar5 = 0; uVar5 < uVar2 >> 2; uVar5 = uVar5 + 1 & 0xffff) {
      puVar1 = ((void *)camry_host_ptr((uint32_t)(puVar4 + uVar5 * 4)));
      puVar1[0] = '\0';
      puVar1[1] = '\0';
      puVar1[2] = '\0';
      puVar1[3] = '\0';
    }
  }
  nvm_family0_probe_offset = 0;
  nvm_family0_scan_cursor = 0;
  DAT_febf0684 = 0;
  nvm_family0_active_object = 0xffff;
  nvm_family0_phase = '\0';
  DAT_febf067f = 0;
  nvm_family0_span_request = '\0';
  nvm_family0_classification_latch = '\0';
  DAT_febf067c = 0;
  nvm_family0_request_consumer = '\0';
  nvm_family0_request_producer = '\0';
  return;
}

void reset_nvm_family0_scan_and_probe_cursors_67346(void)

{
  nvm_family0_scan_cursor = 0;
  nvm_family0_probe_offset = 0;
  return;
}

uint nvm_family0_has_request_cell(ushort object)

{
  uint uVar1;
  
  uVar1 = 0;
  while( true ) {
    if (nvm_family0_request_cell_count <= uVar1) {
      return 0;
    }
    if ((*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebf0488u + (uint32_t)(uVar1) * (uint32_t)sizeof(F33NvmRequestCell)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmRequestCell) + (uint32_t)offsetof(F33NvmRequestCell, object))))) == object) break;
    uVar1 = uVar1 + 1 & 0xff;
  }
  return 1;
}

uint nvm_select_family0_request(void)

{
  uint8_t stack_record_16[22];
  char *pcVar1;
  char cVar2;
  ushort object;
  uint32_t puVar3;
  uint uVar4;
  uint uVar5;
  undefined1 uVar6;
  undefined1 uVar7;
  
  puVar3 = 0xfebeb800u;
  nvm_recover_family0_request_indices(((uint8_t *)(stack_record_16)),((uint8_t *)((stack_record_16 + 1))));
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x4e7e))))) == 'Z') {
    nvm_dispatch_family0_page_span();
    uVar6 = 0x11;
    uVar5 = 1;
    goto LAB_000674ca;
  }
  uVar6 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x4e80)))));
  uVar5 = 0;
  if ((uint)stack_record_16[0] == (uint)stack_record_16[1]) goto LAB_000674ca;
  pcVar1 = ((undefined *)camry_host_ptr((uint32_t)(puVar3 + (uint)stack_record_16[1] * 4 + 0x4c88)));
  object = *(ushort *)(pcVar1 + 2);
  cVar2 = *pcVar1;
  pcVar1[2] = -1;
  pcVar1[3] = -1;
  *pcVar1 = -1;
  uVar4 = nvm_advance_family0_request_index(stack_record_16[1]);
  stack_record_16[1] = (byte)uVar4;
  if ((uint)nvm_family0_object_count <= (uint)object) goto LAB_000674ca;
  if (cVar2 == '\x11') {
    nvm_arm_family0_read(object);
    uVar6 = 0x22;
LAB_000674aa:
    uVar7 = 0x21;
    (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + 0x4e82)))) = object;
    uVar5 = 1;
  }
  else {
    if ((cVar2 == '\"') || (cVar2 == '3')) {
      uVar5 = nvm_get_family0_completion(object);
      if ((cVar2 == '\"') || (uVar5 != 0x5a)) {
        nvm_arm_family0_write(object);
      }
      uVar6 = 0x33;
      goto LAB_000674aa;
    }
    uVar7 = 0x32;
  }
  uVar4 = nvm_family0_has_request_cell(object);
  if (uVar4 == 1) {
    uVar7 = 0x20;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(object + 0x4b08))))) = uVar7;
LAB_000674ca:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x4e80))))) = uVar6;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x4e7b))))) = stack_record_16[1];
  return uVar5;
}

void handle_nvm_family0_operation_completion_674dc(void)

{
  uchar uVar1;
  ushort object;
  uint32_t puVar2;
  uint uVar3;
  undefined1 uVar4;
  uint uVar5;
  
  object = nvm_family0_active_object;
  uVar1 = nvm_family0_phase;
  puVar2 = 0xfebeb800u;
  uVar5 = (uint)nvm_family0_active_object;
  uVar3 = nvm_get_family0_completion(nvm_family0_active_object);
  if (uVar1 == '\x11') {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x4e7e))))) = 0xa5;
  }
  else {
    if (uVar1 == '\"') {
      if (nvm_family0_object_count <= uVar5) goto LAB_00067596;
      if (uVar3 == 0x5a) {
        uVar4 = 0x10;
      }
      else {
        uVar3 = nvm_family0_chunk_cost((*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x2ad8cu + (uint32_t)(uVar5) * (uint32_t)sizeof(F33NvmFamily0RamDescriptor)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmFamily0RamDescriptor) + (uint32_t)offsetof(F33NvmFamily0RamDescriptor, payload_bytes))))));
        uVar3 = nvm_classify_family0_chunks
                          (object,0,(short)uVar3 *
                                    (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x2ad8cu + (uint32_t)(uVar5) * (uint32_t)sizeof(F33NvmFamily0RamDescriptor)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmFamily0RamDescriptor) + (uint32_t)offsetof(F33NvmFamily0RamDescriptor, logical_count))))));
        uVar4 = 0x11;
        if (uVar3 == 0) {
          uVar4 = 0x30;
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x4e7d))))) = 0x5a;
        }
      }
    }
    else {
      if ((uVar1 != '3') || (nvm_family0_object_count <= uVar5)) goto LAB_00067596;
      uVar4 = 0x10;
      if (uVar3 != 0x5a) {
        uVar4 = 0x31;
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x4e7c))))) = 0x5a;
      }
    }
    uVar3 = nvm_family0_has_request_cell(object);
    if (uVar3 == 1) {
      uVar4 = 0x20;
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(uVar5 + 0x4b08))))) = uVar4;
  }
LAB_00067596:
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + 0x4e82)))) = 0xffff;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x4e80))))) = 0;
  return;
}

uint nvm_classify_family0_pass(ushort *charged_out)

{
  undefined1 uVar1;
  int iVar2;
  uint uVar3;
  undefined8 uVar4;
  ushort chunk_offset;
  uint uVar5;
  uint uVar6;
  uint uVar7;
  uint uVar8;
  ushort object;
  uint uVar9;
  
  uVar4 = 0xfebeb800;
  uVar9 = (uint)nvm_family0_scan_cursor;
  uVar6 = 0;
  iVar2 = 0x5a;
  uVar7 = 0;
  uVar8 = 0;
  do {
    while( true ) {
      uVar5 = (uint)nvm_family0_object_count;
      object = (ushort)uVar9;
      if ((uVar5 <= uVar9) || (iVar2 == 0)) {
        (*((ushort *)camry_host_ptr((uint32_t)((int)uVar4 + 0x4e76)))) = object;
        (*((short *)camry_host_ptr((uint32_t)((int)uVar4 + 0x4e78)))) = (short)uVar8;
        *charged_out = (ushort)uVar7;
        if (uVar5 <= uVar9) {
          uVar6 = 0x5a;
        }
        return uVar6;
      }
      uVar5 = nvm_get_family0_completion(object);
      if (uVar5 != 0x5a) break;
      uVar1 = 0x10;
LAB_0006764c:
      (*((undefined1 *)camry_host_ptr((uint32_t)(uVar9 + (int)uVar4 + 0x4b08)))) = uVar1;
      iVar2 = 0x5a;
      uVar9 = uVar9 + 1 & 0xffff;
    }
    uVar8 = nvm_family0_chunk_cost((*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x2ad8cu + (uint32_t)(uVar9) * (uint32_t)sizeof(F33NvmFamily0RamDescriptor)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmFamily0RamDescriptor) + (uint32_t)offsetof(F33NvmFamily0RamDescriptor, payload_bytes))))));
    uVar3 = (uint)nvm_classification_budget;
    uVar5 = (int)(short)(*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x2ad8cu + (uint32_t)(uVar9) * (uint32_t)sizeof(F33NvmFamily0RamDescriptor)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmFamily0RamDescriptor) + (uint32_t)offsetof(F33NvmFamily0RamDescriptor, logical_count))))) * (int)(short)uVar8 &
            0xffff;
    if ((int)((uVar5 + uVar7) - uVar3) < 0 || uVar5 + uVar7 == uVar3) {
      uVar8 = 0;
      chunk_offset = 0;
      uVar3 = uVar5;
LAB_00067628:
      uVar7 = uVar7 + uVar3 & 0xffff;
      uVar5 = nvm_classify_family0_chunks(object,chunk_offset,(ushort)uVar3);
      if (uVar5 == 0) {
        uVar1 = 0x30;
        (*((undefined1 *)camry_host_ptr((uint32_t)((int)uVar4 + 0x4e7d)))) = 0x5a;
      }
      else {
        if (uVar8 != 0) goto LAB_0006765e;
        uVar1 = 0x11;
      }
      goto LAB_0006764c;
    }
    if (uVar7 == 0) {
      chunk_offset = (*((ushort *)camry_host_ptr((uint32_t)((int)uVar4 + 0x4e78))));
      uVar5 = uVar5 - chunk_offset;
      if ((int)(uVar5 - uVar3) < 0 == ((int)uVar5 < 0 && -1 < (int)(uVar5 - uVar3)) &&
          uVar5 != uVar3) {
        uVar8 = uVar3 + chunk_offset & 0xffff;
      }
      else {
        uVar3 = uVar5 & 0xffff;
        uVar8 = 0;
      }
      goto LAB_00067628;
    }
    uVar8 = 0;
LAB_0006765e:
    iVar2 = 0;
  } while( true );
}

uint nvm_family0_request_full(uint producer,uint consumer)

{
  uint uVar1;
  
  uVar1 = consumer & 0xff;
  if (uVar1 == 0) {
    uVar1 = (uint)nvm_family0_request_cell_count;
  }
  return (uint)((producer & 0xff) + 1 == uVar1);
}

uint nvm_previous_family0_request(uint index)

{
  uint uVar1;
  
  uVar1 = index & 0xff;
  if (uVar1 == 0) {
    uVar1 = (uint)nvm_family0_request_cell_count;
  }
  return uVar1 - 1 & 0xff;
}

byte consume_nvm_family0_classification_flags_67874(void)

{
  byte bVar1;
  
  bVar1 = DAT_febf067c == 'Z';
  if (nvm_family0_classification_latch == 'Z') {
    bVar1 = bVar1 | 2;
  }
  DAT_febf067c = 0;
  nvm_family0_classification_latch = '\0';
  return bVar1;
}

bool refresh_nvm_family0_queue_empty_flag_67894(void)

{
  uint8_t stack_record_6[6];
  undefined1 uVar1;
  uint32_t puVar2;
  
  puVar2 = 0xfebeb800u;
  nvm_recover_family0_request_indices(((uint8_t *)(stack_record_6)),((uint8_t *)((stack_record_6 + 1))));
  if ((uintptr_t)(((stack_record_6[0])))==(uintptr_t)(((stack_record_6[1])))) {
    uVar1 = 0x5a;
  }
  else {
    uVar1 = 0xff;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x4e7e))))) = uVar1;
  return (uintptr_t)(((stack_record_6[0])))==(uintptr_t)(((stack_record_6[1])));
}

uint nvm_get_family0_record(uint object,uint *destination)

{
  uint32_t puVar1;
  uint uVar2;
  
  puVar1 = 0xfebeb800u;
  uVar2 = object & 0xffff;
  if (uVar2 < nvm_family0_object_count) {
    copy_whole_words
              (destination,
               (uint32_t *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x2ad8cu + (uint32_t)(uVar2) * (uint32_t)sizeof(F33NvmFamily0RamDescriptor)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmFamily0RamDescriptor) + (uint32_t)offsetof(F33NvmFamily0RamDescriptor, buffer)))))),
               (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x2ad8cu + (uint32_t)(uVar2) * (uint32_t)sizeof(F33NvmFamily0RamDescriptor)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmFamily0RamDescriptor) + (uint32_t)offsetof(F33NvmFamily0RamDescriptor, payload_bytes))))));
    uVar2 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(uVar2 + 0x4b08)))));
  }
  else {
    uVar2 = 0xff;
  }
  return uVar2;
}

undefined4 check_no_nvm_family0_status_class20_67984(void)

{
  uint uVar1;
  
  uVar1 = 0;
  while( true ) {
    if (nvm_family0_object_count <= uVar1) {
      return 1;
    }
    if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebf0308u + (uint32_t)(uVar1) * 1u)))) & 0xf0) == 0x20) break;
    uVar1 = uVar1 + 1 & 0xffff;
  }
  return 0;
}

uint nvm_get_family0_phase(void)

{
  return (uint)nvm_family0_phase;
}

void reset_nvm_family1_scan_cursor_67a52(void)

{
  nvm_family1_scan_cursor = 0;
  return;
}

uint nvm_family1_has_request_cell(ushort object)

{
  uint uVar1;
  
  uVar1 = 0;
  while( true ) {
    if (nvm_family1_request_cell_count <= uVar1) {
      return 0;
    }
    if ((*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebf058cu + (uint32_t)(uVar1) * (uint32_t)sizeof(F33NvmRequestCell)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmRequestCell) + (uint32_t)offsetof(F33NvmRequestCell, object))))) == object) break;
    uVar1 = uVar1 + 1 & 0xff;
  }
  return 1;
}

uint nvm_select_family1_request(void)

{
  uint8_t stack_record_1a[26];
  code *pcVar1;
  code cVar2;
  ushort object;
  int iVar3;
  undefined8 uVar4;
  uint uVar5;
  int iVar6;
  uint uVar7;
  undefined1 uVar8;
  uchar value;
  uint uVar9;
  int iVar10;
  
  uVar4 = 0xfebeb800;
  nvm_recover_family1_request_indices(((uint8_t *)(stack_record_1a)),((uint8_t *)((stack_record_1a + 1))));
  iVar3 = (int)uVar4;
  if ((*((char *)camry_host_ptr((uint32_t)(iVar3 + 0x4e88)))) == 'Z') {
    nvm_dispatch_family1_page_span();
    uVar8 = 0x11;
    uVar7 = 1;
    goto LAB_00067c7a;
  }
  uVar8 = (*((undefined1 *)camry_host_ptr((uint32_t)(iVar3 + 0x4e89))));
  uVar7 = 0;
  if ((uint)stack_record_1a[0] == (uint)stack_record_1a[1]) {
    for (iVar10 = 0; iVar3 = (int)uVar4,
        (int)(iVar10 - (uint)nvm_family1_object_count) < 0 !=
        (iVar10 < 0 && -1 < (int)(iVar10 - (uint)nvm_family1_object_count)); iVar10 = iVar10 + 1
        ) {
      uVar5 = read_repair_redundant_u8
                        (((uint32_t)((uint32_t)(iVar3 + 0x4b28 + iVar10))), ((uint32_t)((uint32_t)(iVar3 + 0x5888 + iVar10))), ((uint32_t)((uint32_t)(iVar3 + 0x58ac + iVar10))), '\x12');
      if (uVar5 == 0x10) {
        iVar6 = nvm_check_family1_checksum((ushort)iVar10);
        iVar3 = (int)uVar4;
        if (iVar6 != 1) {
          nvm_submit_family1_read_copies((ushort)iVar10);
          break;
        }
      }
    }
    goto LAB_00067c7a;
  }
  pcVar1 = ((void *)camry_host_ptr((uint32_t)(0x4d8cu + (uint)stack_record_1a[1] * 4 + iVar3)));
  object = *(ushort *)(pcVar1 + 2);
  uVar9 = (uint)object;
  cVar2 = *pcVar1;
  *(undefined2 *)(pcVar1 + 2) = 0xffff;
  *pcVar1 = (code)0xff;
  uVar5 = nvm_advance_family1_request_index(stack_record_1a[1]);
  stack_record_1a[1] = (byte)uVar5;
  if (nvm_family1_object_count <= uVar9) goto LAB_00067c7a;
  if (cVar2 == (code)0x11) {
    nvm_submit_family1_read_copies(object);
    uVar8 = 0x22;
    (*((ushort *)camry_host_ptr((uint32_t)(iVar3 + 0x4e8c)))) = object;
LAB_00067c06:
    value = '!';
    uVar7 = 1;
  }
  else {
    if ((cVar2 == (code)0x22) || (cVar2 == (code)0x33)) {
      uVar7 = nvm_get_family1_completion(object);
      if ((cVar2 == (code)0x22) || (uVar7 != 0x5a)) {
        nvm_submit_family1_write_copies(object);
      }
      (*((ushort *)camry_host_ptr((uint32_t)(iVar3 + 0x4e8c)))) = object;
      uVar8 = 0x33;
      (*((undefined1 *)camry_host_ptr((uint32_t)(iVar3 + 0x4e8a)))) = 0;
      goto LAB_00067c06;
    }
    value = '2';
  }
  uVar5 = nvm_family1_has_request_cell(object);
  if (uVar5 == 1) {
    value = ' ';
  }
  publish_redundant_u8
            (value,((uchar *)camry_host_ptr((uint32_t)(iVar3 + 0x4b28 + uVar9))),((uchar *)camry_host_ptr((uint32_t)(iVar3 + 0x5888 + uVar9))),
             ((uchar *)camry_host_ptr((uint32_t)(iVar3 + 0x58ac + uVar9))));
LAB_00067c7a:
  (*((undefined1 *)camry_host_ptr((uint32_t)(iVar3 + 0x4e89)))) = uVar8;
  (*((byte *)camry_host_ptr((uint32_t)(iVar3 + 0x4e87)))) = stack_record_1a[1];
  return uVar7;
}

uint32_t nvm_handle_family1_completion(void)

{
  uint32_t camry_r10_result;
  uint8_t stack_record_e[16];
  camry_fill_bytes(stack_record_e, sizeof stack_record_e);
  uint8_t uVar1;
  uint16_t object;
  uint32_t puVar2;
  uint uVar3;
  uchar value;
  uint uVar4;
  
  object = nvm_family1_active_object;
  uVar1 = nvm_family1_phase;
  puVar2 = 0xfebeb800u;
  uVar4 = (uint)nvm_family1_active_object;
  nvm_recover_family1_request_indices(((uint8_t *)(stack_record_e)),((uint8_t *)((stack_record_e + 1))));
  uVar3 = (camry_r10_result = nvm_get_family1_completion(object));
  if (uVar1 == '\x11') {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x4e88))))) = 0xa5;
    goto LAB_00067d82;
  }
  if (uVar1 == '\"') {
    if (nvm_family1_object_count <= uVar4) goto LAB_00067d82;
    if (uVar3 == 0x5a) goto LAB_00067d38;
    uVar3 = (camry_r10_result = nvm_classify_family1_pages(object));
    value = '\x11';
    if (uVar3 == 0) {
      value = '0';
    }
  }
  else {
    if ((uVar1 != '3') || (nvm_family1_object_count <= uVar4)) goto LAB_00067d82;
    if (uVar3 == 0x5a) {
LAB_00067d38:
      value = '\x10';
      nvm_publish_family1_checksum(object);
    }
    else {
      if ((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x4e8a))))) < 2) {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x4e8a))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x4e8a))))) + 1;
        (camry_r10_result = nvm_submit_family1_write_copies(object));
        return camry_r10_result;
      }
      value = '1';
    }
  }
  uVar3 = (camry_r10_result = nvm_family1_has_request_cell(object));
  if (uVar3 == 1) {
    value = ' ';
  }
  (camry_r10_result = publish_redundant_u8
            (value, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + uVar4 + 0x4b28))), ((undefined *)camry_host_ptr((uint32_t)(puVar2 + uVar4 + 0x5888))), ((undefined *)camry_host_ptr((uint32_t)(puVar2 + uVar4 + 0x58ac)))));
LAB_00067d82:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x4e89))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x4e86))))) = stack_record_e[0];
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + 0x4e8c)))) = 0xffff;
  return camry_r10_result;
}

uint nvm_classify_family1_pass(ushort already_charged)

{
  int iVar1;
  undefined8 uVar2;
  uint uVar3;
  uint uVar4;
  uchar value;
  uint uVar5;
  ushort object;
  uint uVar6;
  
  uVar2 = 0xfebeb800;
  uVar6 = (uint)nvm_family1_scan_cursor;
  uVar4 = 0;
  while( true ) {
    iVar1 = (int)uVar2;
    uVar5 = (uint)nvm_family1_object_count;
    object = (ushort)uVar6;
    if (uVar5 <= uVar6) break;
    uVar3 = nvm_get_family1_completion(object);
    iVar1 = (int)uVar2;
    if (uVar3 == 0x5a) {
      value = '\x10';
      nvm_publish_family1_checksum(object);
    }
    else {
      already_charged = already_charged + 3;
      if (nvm_classification_budget < already_charged) break;
      uVar5 = nvm_classify_family1_pages(object);
      value = '\x11';
      if (uVar5 == 0) {
        value = '0';
      }
    }
    iVar1 = (int)uVar2;
    publish_redundant_u8
              (value,((uchar *)camry_host_ptr((uint32_t)(iVar1 + 0x4b28 + uVar6))),((uchar *)camry_host_ptr((uint32_t)(iVar1 + 0x5888 + uVar6))),
               ((uchar *)camry_host_ptr((uint32_t)(iVar1 + 0x58ac + uVar6))));
    uVar6 = uVar6 + 1 & 0xffff;
  }
  (*((ushort *)camry_host_ptr((uint32_t)(iVar1 + 0x4e8e)))) = object;
  if (uVar5 <= uVar6) {
    uVar4 = 0x5a;
  }
  return uVar4;
}

uint nvm_set_family1_record(uint object,uint *source)

{
  uint8_t stack_record_3a[58];
  int iVar1;
  int iVar2;
  code cVar3;
  int iVar4;
  undefined8 uVar5;
  uint uVar6;
  uint uVar7;
  uint uVar8;
  uint uVar9;
  code cVar10;
  uint uVar11;
  uint uVar12;
  uint uVar13;
  uchar *puStack_38;
  uchar *puStack_34;
  uint *puStack_30;
  
  uVar5 = 0xfebeb800;
  uVar12 = object & 0xffff;
  if (uVar12 < nvm_family1_object_count) {
    puStack_34 = nvm_family1_status;
    puStack_38 = app_nvm_family1_status_xor55;
    puStack_30 = source;
    uVar6 = read_repair_redundant_u8
                      (camry_host_addr(((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebf0328u + (uint32_t)(uVar12) * 1u)))), camry_host_addr(((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebf1088u + (uint32_t)(uVar12) * 1u)))), camry_host_addr(((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebf10acu + (uint32_t)(uVar12) * 1u)))), '\x12');
    nvm_recover_family1_request_indices(stack_record_3a,(stack_record_3a + 1));
    uVar11 = (uint)stack_record_3a[0];
    uVar13 = (uint)stack_record_3a[1];
    uVar7 = nvm_family1_request_full(uVar11,uVar13);
    iVar4 = (int)uVar5;
    if ((uVar7 == 1) || (uVar6 == 0x21)) {
      uVar12 = 0;
    }
    else {
      uVar8 = nvm_previous_family1_request(uVar11);
      cVar10 = (code)0xff;
      uVar9 = (uint)nvm_family1_request_cell_count;
      for (uVar7 = uVar9; uVar7 != 0; uVar7 = uVar7 - 1) {
        iVar4 = uVar13 * 4 + (int)uVar5;
        cVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x4d8cu + (uint32_t)(iVar4)))));
        if (((*((ushort *)camry_host_ptr((uint32_t)(iVar4 + 0x4d8e)))) == uVar12) &&
           ((cVar3 == (code)0x22 || (cVar3 == (code)0x33)))) {
          cVar10 = cVar3;
        }
        if ((uVar13 == uVar11) || (cVar10 != (code)0xff)) break;
        uVar13 = nvm_advance_family1_request_index((uchar)uVar13);
        stack_record_3a[1] = (byte)uVar13;
      }
      uVar13 = update_whole_words
                         (((uint32_t *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x2af0cu + (uint32_t)(uVar12) * (uint32_t)sizeof(F33NvmFamily1RamDescriptor)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmFamily1RamDescriptor) + (uint32_t)offsetof(F33NvmFamily1RamDescriptor, buffer)))))))), puStack_30, 
                          (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x2af0cu + (uint32_t)(uVar12) * (uint32_t)sizeof(F33NvmFamily1RamDescriptor)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmFamily1RamDescriptor) + (uint32_t)offsetof(F33NvmFamily1RamDescriptor, payload_bytes))))));
      iVar4 = (int)uVar5;
      if ((uVar13 == 1) || (cVar10 == (code)0x22)) {
        cVar10 = (code)0x22;
      }
      else {
        cVar10 = (code)0x33;
      }
      uVar13 = (uint)stack_record_3a[1];
      if (uVar13 == uVar8) {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x4d8cu + (uint32_t)(uVar13 * 4 + iVar4))))) = cVar10;
      }
      else {
        uVar6 = (uint)stack_record_3a[0];
        uVar7 = uVar6;
        if (uVar13 != uVar6) {
          for (; uVar7 = uVar6, uVar9 != 0; uVar9 = uVar9 - 1) {
            uVar11 = nvm_advance_family1_request_index((uchar)uVar13);
            iVar4 = (int)uVar5;
            uVar7 = uVar13;
            if (uVar13 == uVar8) break;
            iVar2 = uVar11 * 4 + iVar4;
            iVar1 = uVar13 * 4 + iVar4;
            cVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x4d8cu + (uint32_t)(iVar2)))));
            stack_record_3a[1] = (byte)uVar11;
            (*((undefined2 *)camry_host_ptr((uint32_t)(iVar1 + 0x4d8e)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(iVar2 + 0x4d8e))));
            (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x4d8cu + (uint32_t)(iVar1))))) = cVar3;
            uVar13 = uVar11;
          }
        }
        iVar2 = uVar7 * 4 + iVar4;
        uVar6 = 0x20;
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x4d8cu + (uint32_t)(iVar2))))) = cVar10;
        (*((short *)camry_host_ptr((uint32_t)(iVar2 + 0x4d8e)))) = (short)object;
        uVar13 = nvm_advance_family1_request_index((uchar)uVar7);
        stack_record_3a[0] = (byte)uVar13;
      }
      publish_redundant_u8
                ((uchar)uVar6,puStack_34 + uVar12,puStack_38 + uVar12,
                 ((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebf10acu + (uint32_t)(uVar12) * 1u))));
      uVar12 = 1;
    }
    (*((byte *)camry_host_ptr((uint32_t)(iVar4 + 0x4e86)))) = stack_record_3a[0];
  }
  else {
    uVar12 = 0;
  }
  return uVar12;
}
