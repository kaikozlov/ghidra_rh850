#include "common.h"

bool refresh_nvm_family1_queue_empty_flag_6805e(void)

{
  uint8_t stack_record_6[6];
  undefined1 uVar1;
  uint32_t puVar2;
  
  puVar2 = 0xfebeb800u;
  nvm_recover_family1_request_indices(((uint8_t *)(stack_record_6)),((uint8_t *)((stack_record_6 + 1))));
  if ((uintptr_t)(((stack_record_6[0])))==(uintptr_t)(((stack_record_6[1])))) {
    uVar1 = 0x5a;
  }
  else {
    uVar1 = 0xff;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x4e88))))) = uVar1;
  return (uintptr_t)(((stack_record_6[0])))==(uintptr_t)(((stack_record_6[1])));
}

undefined4 apply_nvm_family1_span_request_statuses_6808e(void)

{
  int iVar1;
  undefined8 uVar2;
  undefined4 uVar3;
  int iVar4;
  
  uVar2 = 0xfebeb800;
  uVar3 = 0;
  if (nvm_family1_span_request == 0xa5) {
    for (iVar4 = 0; iVar1 = (int)uVar2,
        (int)(iVar4 - (uint)nvm_family1_object_count) < 0 !=
        (iVar4 < 0 && -1 < (int)(iVar4 - (uint)nvm_family1_object_count)); iVar4 = iVar4 + 1) {
      publish_redundant_u8
                ('\x11',((uchar *)camry_host_ptr((uint32_t)(iVar1 + 0x4b28 + iVar4))),((uchar *)camry_host_ptr((uint32_t)(iVar1 + 0x5888 + iVar4))),
                 ((uchar *)camry_host_ptr((uint32_t)(iVar1 + 0x58ac + iVar4))));
    }
    (*((undefined1 *)camry_host_ptr((uint32_t)(iVar1 + 0x4e88)))) = 0;
    uVar3 = 1;
  }
  else if (nvm_family1_span_request == 0xff) {
    for (iVar4 = 0; iVar1 = (int)uVar2,
        (int)(iVar4 - (uint)nvm_family1_object_count) < 0 !=
        (iVar4 < 0 && -1 < (int)(iVar4 - (uint)nvm_family1_object_count)); iVar4 = iVar4 + 1) {
      publish_redundant_u8
                ('1',((uchar *)camry_host_ptr((uint32_t)(iVar1 + 0x4b28 + iVar4))),((uchar *)camry_host_ptr((uint32_t)(iVar1 + 0x5888 + iVar4))),
                 ((uchar *)camry_host_ptr((uint32_t)(iVar1 + 0x58ac + iVar4))));
    }
    (*((undefined1 *)camry_host_ptr((uint32_t)(iVar1 + 0x4e88)))) = 0;
    uVar3 = 0xffffffff;
  }
  return uVar3;
}

undefined4 check_no_nvm_family1_status_class20_681aa(void)

{
  int iVar1;
  undefined8 uVar2;
  uint uVar3;
  uint uVar4;
  
  uVar2 = 0xfebeb800;
  uVar4 = 0;
  while( true ) {
    if (nvm_family1_object_count <= uVar4) {
      return 1;
    }
    iVar1 = (int)uVar2;
    uVar3 = read_repair_redundant_u8
                      (((uint32_t)((uint32_t)(iVar1 + 0x4b28 + uVar4))), ((uint32_t)((uint32_t)(iVar1 + 0x5888 + uVar4))), ((uint32_t)((uint32_t)(iVar1 + 0x58ac + uVar4))), '\x12');
    if ((uVar3 & 0xf0) == 0x20) break;
    uVar4 = uVar4 + 1 & 0xffff;
  }
  return 0;
}

uint nvm_get_family1_phase(void)

{
  return (uint)nvm_family1_phase;
}

uint32_t nvm_initialize_acquisition(void)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  short sVar4;
  
  nvm_family0_busy = '\0';
  nvm_family1_busy = '\0';
  uVar2 = 0;
  do {
    uVar3 = uVar2 + 1;
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebf0698u + (uint32_t)(uVar2) * 4u)))) = 0;
    uVar2 = uVar3;
  } while (uVar3 < 4);
  for (uVar2 = 0; uVar2 < nvm_family0_object_count; uVar2 = uVar2 + 1 & 0xffff) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebf0338u + (uint32_t)(uVar2) * 1u)))) = '\0';
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebf0368u + (uint32_t)(uVar2) * 2u)))) = 0xffff;
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebf03a8u + (uint32_t)(uVar2) * 4u)))) = 0;
  }
  for (uVar2 = 0; uVar2 < nvm_family1_object_count; uVar2 = uVar2 + 1 & 0xffff) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebf0358u + (uint32_t)(uVar2) * 1u)))) = '\0';
  }
  uVar2 = 0;
  do {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebf0708u + (uint32_t)(uVar2) * 1u)))) = '\0';
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebf0c88u + (uint32_t)(uVar2) * 1u)))) = '\0';
    uVar2 = uVar2 + 1;
  } while (uVar2 < 0x400);
  uVar2 = 0;
  do {
    uVar3 = 0;
    do {
      sVar4 = (short)uVar2;
      uVar1 = uVar3 + 1;
      ((volatile F33NvmCopyStage *)camry_host_ptr((uint32_t)(0xfebf0b08u + (uint32_t)(sVar4) * (uint32_t)sizeof(F33NvmCopyStage))))[0].raw[uVar3] = '\0';
      ((volatile F33NvmCopyStage *)camry_host_ptr((uint32_t)(0xfebf0b08u + (uint32_t)(sVar4) * (uint32_t)sizeof(F33NvmCopyStage))))[0].xor55[uVar3] = '\0';
      ((volatile F33NvmCopyStage *)camry_host_ptr((uint32_t)(0xfebf0b08u + (uint32_t)(sVar4) * (uint32_t)sizeof(F33NvmCopyStage))))[0].xorAA[uVar3] = '\0';
      uVar3 = uVar1;
    } while (uVar1 < 0x20);
    uVar2 = uVar2 + 1;
  } while (uVar2 < 4);
  uVar2 = 0;
  do {
    nvm_family1_write_stage.raw[uVar2] = '\0';
    uVar3 = uVar2 + 1;
    nvm_family1_write_stage.xor55[uVar2] = '\0';
    nvm_family1_write_stage.xorAA[uVar2] = '\0';
    uVar2 = uVar3;
  } while (uVar3 < 0x20);
  nvm_initial_read_token = '\0';
  nvm_direct_operation_request = '\0';
  nvm_copy_read_retry = '\0';
  nvm_initialize_service_diagnostics_and_suspend_state_79b1e();
  nvm_initialize_logical_module();
  return run_init_chain_764e2();
}

void nvm_service_and_release_erase_span(void)

{
  uint32_t puVar1;
  uint uVar2;
  
  puVar1 = 0xfebeb800u;
  nvm_service_application_cycle();
  if ((((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x4e90)))))) == -0x5b) || (((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x4e91)))))) == -0x5b)) {
    nvm_poll_direct_operation();
    uVar2 = nvm_get_direct_operation_result();
    if (uVar2 != 1) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x4e90))))) = 0;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x4e91))))) = 0;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x4e92u + (uint32_t)((int)(puVar1 + 1)))))) = (code)0x0;
      nvm_poll_probe_mode();
    }
  }
  return;
}

void service_nvm_acquisition_driver_wrapper_68318(void)

{
  nvm_service_acquisition_driver();
  return;
}

void nvm_arm_initial_read_acquisition(void)

{
  nvm_initial_read_token = 'Z';
  return;
}

uint nvm_begin_page_erase_span(uint first_page,uint page_count)

{
  uint32_t puVar1;
  uint uVar2;
  
  puVar1 = 0xfebeb800u;
  nvm_direct_operation_request = 'Z';
  nvm_poll_probe_mode();
  uVar2 = nvm_request_erase_span(0,(first_page & 0xffff) << 6,(page_count & 0xffff) << 6);
  if (uVar2 == 7) {
    uVar2 = 0;
  }
  else {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x4e92u + (uint32_t)((int)(puVar1 + 1)))))) = (code)0x0;
    nvm_poll_probe_mode();
    uVar2 = 0xff;
  }
  return uVar2;
}

uint nvm_dispatch_family0_page_span(void)

{
  camry_write32((camry_sp - 4u) & ~3u, camry_gpr[24]);
  camry_write32((camry_sp - 8u) & ~3u, camry_gpr[25]);
  camry_write32((camry_sp - 12u) & ~3u, camry_gpr[26]);
  camry_write32((camry_sp - 16u) & ~3u, camry_gpr[27]);
  camry_write32((camry_sp - 20u) & ~3u, camry_gpr[28]);
  camry_write32((camry_sp - 24u) & ~3u, camry_gpr[29]);
  camry_write32((camry_sp - 28u) & ~3u, camry_gpr[31]);
  camry_sp -= 32u;
  camry_gpr[3] = camry_sp;

  uint uVar1;
  uint uVar2;
  int iVar3;
  undefined8 uVar4;
  uint uVar5;
  uint uVar6;
  uint unaff_r24;
  uint uVar7;
  uint first_page;
  uint uVar8;
  uint uVar9;

  
  uVar4 = 0xfebeb800;
  if (nvm_family0_busy == '\0') {
    first_page = 0xffff;
    uVar6 = 0;
    for (uVar2 = 0; iVar3 = (int)uVar4, uVar2 < nvm_family0_object_count;
        uVar2 = uVar2 + 1 & 0xffff) {
      uVar9 = (uint)(*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x2ad8cu + (uint32_t)(uVar2) * (uint32_t)sizeof(F33NvmFamily0RamDescriptor)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmFamily0RamDescriptor) + (uint32_t)offsetof(F33NvmFamily0RamDescriptor, first_logical_handle)))));
      if (uVar9 != 0xffff) {
        iVar3 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x2ad8cu + (uint32_t)(uVar2) * (uint32_t)sizeof(F33NvmFamily0RamDescriptor)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmFamily0RamDescriptor) + (uint32_t)offsetof(F33NvmFamily0RamDescriptor, logical_count))))) + uVar9;
        for (; uVar9 <= (iVar3 - 1U & 0xffff); uVar9 = uVar9 + 1 & 0xffff) {
          uVar5 = nvm_get_logical_storage_page((ushort)uVar9,&(*((ushort *)camry_host_ptr(camry_sp + 2u))));
          uVar7 = unaff_r24;
          uVar1 = uVar6;
          uVar8 = first_page;
          if (uVar5 == 0) {
            uVar1 = (uint)(*((ushort *)camry_host_ptr(camry_sp + 2u)));
            uVar8 = uVar1;
            if (first_page <= uVar1) {
              uVar8 = first_page;
            }
            uVar7 = uVar9;
            if (uVar1 <= uVar6) {
              uVar7 = unaff_r24;
              uVar1 = uVar6;
            }
          }
          unaff_r24 = uVar7;
          uVar6 = uVar1;
          first_page = uVar8;
        }
      }
    }
    uVar2 = (ushort)((*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x2ad8cu + (uint32_t)((*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0x2b010u + (uint32_t)(unaff_r24) * (uint32_t)sizeof(F33NvmApplicationRoute)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmApplicationRoute) + (uint32_t)offsetof(F33NvmApplicationRoute, object)))))) * (uint32_t)sizeof(F33NvmFamily0RamDescriptor)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmFamily0RamDescriptor) + (uint32_t)offsetof(F33NvmFamily0RamDescriptor, payload_bytes))))) + 0x14) +
            0x3f >> 6;
    if (uVar2 < 2) {
      uVar2 = 2;
    }
    uVar6 = (camry_gpr[24] = unaff_r24, camry_gpr[26] = uVar6, camry_gpr[27] = first_page, camry_gpr[29] = nvm_family0_object_count, camry_gpr[6] = first_page, camry_r7 = camry_gpr[7] = (uVar2 + uVar6 - first_page) & 0xffffu, camry_gpr[31] = 0x68884u, nvm_begin_page_erase_span)(first_page,(uVar2 + uVar6) - first_page & 0xffff);
    if (uVar6 == 0) {
      (*((undefined1 *)camry_host_ptr((uint32_t)(iVar3 + 0x4e90)))) = 0xa5;
    }
  }
  else {
    uVar6 = 0xff;
  }
  { uint32_t camry_return_value = (uVar6); if (camry_halted) return 0; camry_gpr[24] = camry_read32((camry_sp + 28u) & ~3u); camry_gpr[25] = camry_read32((camry_sp + 24u) & ~3u); camry_gpr[26] = camry_read32((camry_sp + 20u) & ~3u); camry_gpr[27] = camry_read32((camry_sp + 16u) & ~3u); camry_gpr[28] = camry_read32((camry_sp + 12u) & ~3u); camry_gpr[29] = camry_read32((camry_sp + 8u) & ~3u); camry_gpr[31] = camry_read32((camry_sp + 4u) & ~3u); camry_sp += 32u; camry_gpr[3] = camry_sp; return camry_return_value; }
}

uint nvm_dispatch_family1_page_span(void)

{
  camry_write32((camry_sp - 4u) & ~3u, camry_gpr[25]);
  camry_write32((camry_sp - 8u) & ~3u, camry_gpr[26]);
  camry_write32((camry_sp - 12u) & ~3u, camry_gpr[27]);
  camry_write32((camry_sp - 16u) & ~3u, camry_gpr[28]);
  camry_write32((camry_sp - 20u) & ~3u, camry_gpr[29]);
  camry_write32((camry_sp - 24u) & ~3u, camry_gpr[31]);
  camry_sp -= 28u;
  camry_gpr[3] = camry_sp;

  ushort uVar1;
  int iVar2;
  undefined8 uVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  uint first_page;
  uint uVar7;
  uint uVar8;
  uint uVar9;

  
  uVar3 = 0xfebeb800;
  if (nvm_family1_busy == '\0') {
    first_page = 0xffff;
    uVar5 = 0;
    for (uVar9 = 0; iVar2 = (int)uVar3, uVar9 < nvm_family1_object_count;
        uVar9 = uVar9 + 1 & 0xffff) {
      uVar1 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x2af0cu + (uint32_t)(uVar9) * (uint32_t)sizeof(F33NvmFamily1RamDescriptor)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmFamily1RamDescriptor) + (uint32_t)offsetof(F33NvmFamily1RamDescriptor, first_logical_handle)))));
      if (uVar1 != 0xffff) {
        uVar8 = 0;
        uVar6 = uVar5;
        uVar7 = first_page;
        do {
          uVar4 = nvm_get_logical_storage_page((short)uVar8 * 4 + uVar1,&(*((ushort *)camry_host_ptr(camry_sp + 2u))));
          uVar5 = uVar6;
          first_page = uVar7;
          if (uVar4 == 0) {
            uVar5 = (uint)(*((ushort *)camry_host_ptr(camry_sp + 2u)));
            first_page = uVar5;
            if (uVar7 <= uVar5) {
              first_page = uVar7;
            }
            if (uVar5 <= uVar6) {
              uVar5 = uVar6;
            }
          }
          uVar8 = uVar8 + 1;
          uVar6 = uVar5;
          uVar7 = first_page;
        } while (uVar8 < 3);
      }
    }
    uVar5 = (camry_gpr[26] = uVar5, camry_gpr[27] = first_page, camry_gpr[29] = uVar9, camry_gpr[6] = first_page, camry_r7 = camry_gpr[7] = (uVar5 + 1u - first_page) & 0xffffu, camry_gpr[31] = 0x6890eu, nvm_begin_page_erase_span)(first_page,(uVar5 + 1) - first_page & 0xffff);
    if (uVar5 == 0) {
      (*((undefined1 *)camry_host_ptr((uint32_t)(iVar2 + 0x4e91)))) = 0xa5;
    }
  }
  else {
    uVar5 = 0xff;
  }
  { uint32_t camry_return_value = (uVar5); if (camry_halted) return 0; camry_gpr[25] = camry_read32((camry_sp + 24u) & ~3u); camry_gpr[26] = camry_read32((camry_sp + 20u) & ~3u); camry_gpr[27] = camry_read32((camry_sp + 16u) & ~3u); camry_gpr[28] = camry_read32((camry_sp + 12u) & ~3u); camry_gpr[29] = camry_read32((camry_sp + 8u) & ~3u); camry_gpr[31] = camry_read32((camry_sp + 4u) & ~3u); camry_sp += 28u; camry_gpr[3] = camry_sp; return camry_return_value; }
}

uchar get_nvm_family0_busy_byte_68924(void)

{
  return nvm_family0_busy;
}

uint nvm_get_family0_completion(ushort object)

{
  if ((uint)object < (uint)nvm_family0_object_count) {
    return (uint)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebf0338u + (uint32_t)(object) * 1u))));
  }
  return 0xa5;
}

uint nvm_classify_family0_chunks(ushort object,ushort chunk_offset,ushort chunk_count)

{
  undefined8 uVar1;
  uint uVar2;
  uint uVar3;
  ushort uVar4;
  uint uVar5;
  ushort uStack_16;
  camry_fill_bytes(&uStack_16, sizeof uStack_16);
  
  uVar1 = 0xfebeb800;
  uVar2 = (uint)object;
  uVar5 = 0xff;
  if (uVar2 < nvm_family0_object_count) {
    if (((*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x2ad8cu + (uint32_t)(uVar2) * (uint32_t)sizeof(F33NvmFamily0RamDescriptor) + (uint32_t)offsetof(F33NvmFamily0RamDescriptor, first_logical_handle))))) != 0xffff) &&
       (uVar2 = nvm_get_logical_storage_page
                          (((*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x2ad8cu + (uint32_t)(uVar2) * (uint32_t)sizeof(F33NvmFamily0RamDescriptor) + (uint32_t)offsetof(F33NvmFamily0RamDescriptor, logical_count))))) +
                           (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x2ad8cu + (uint32_t)(uVar2) * (uint32_t)sizeof(F33NvmFamily0RamDescriptor) + (uint32_t)offsetof(F33NvmFamily0RamDescriptor, first_logical_handle)))))) - 1,
                           &uStack_16), uVar2 == 0)) {
      uVar5 = 0x5a;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x4e92u + (uint32_t)((int)uVar1 + 1))))) = (code)0x5a;
      uVar2 = (uint)(ushort)(chunk_offset + uStack_16) << 6;
      nvm_poll_probe_mode();
      uVar4 = 0;
      while ((uVar4 < chunk_count && (uVar5 == 0x5a))) {
        uVar3 = nvm_classify_storage_range(0,uVar2,0x40);
        if (uVar3 != 2) {
          uVar5 = 0;
        }
        uVar4 = uVar4 + 1;
        uVar2 = uVar2 + 0x40;
      }
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x4e92u + (uint32_t)((int)uVar1 + 1))))) = (code)0x0;
      nvm_poll_probe_mode();
    }
  }
  return uVar5;
}

undefined4 read_nvm_family0_range_with_direct_request_689f2(uint param_1,undefined4 param_2,uint param_3)

{
  uint32_t puVar1;
  uint uVar2;
  int iVar3;
  undefined4 uVar4;
  
  puVar1 = 0xfebeb800u;
  nvm_direct_operation_request = 'Z';
  nvm_poll_probe_mode();
  uVar2 = nvm_classify_storage_range(0,param_1 & 0xffff,param_3);
  if (uVar2 == 3) {
    iVar3 = nvm_direct_read_if_mode_and_range_allowed_79554(0,param_1 & 0xffff,param_2,param_3);
    uVar4 = 0;
    if (iVar3 == 0) goto LAB_00068a3a;
  }
  else if (uVar2 == 2) {
    uVar4 = 0x5a;
    goto LAB_00068a3a;
  }
  uVar4 = 0xff;
LAB_00068a3a:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x4e92u + (uint32_t)((int)(puVar1 + 1)))))) = (code)0x0;
  nvm_poll_probe_mode();
  return uVar4;
}

uchar get_nvm_family1_busy_byte_68a4a(void)

{
  return nvm_family1_busy;
}

uint nvm_classify_family1_pages(ushort object)

{
  ushort logical_handle;
  uint32_t puVar1;
  uint uVar2;
  uint uVar3;
  ushort uStack_e;
  camry_fill_bytes(&uStack_e, sizeof uStack_e);
  
  puVar1 = 0xfebeb800u;
  uVar3 = 0xff;
  if ((uint)nvm_family1_object_count <= (uint)object) {
    return 0xff;
  }
  logical_handle = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x2af0cu + (uint32_t)(object) * (uint32_t)sizeof(F33NvmFamily1RamDescriptor) + (uint32_t)offsetof(F33NvmFamily1RamDescriptor, first_logical_handle)))));
  if (logical_handle == 0xffff) {
    return 0xff;
  }
  nvm_direct_operation_request = 'Z';
  nvm_poll_probe_mode();
  uVar2 = nvm_get_logical_storage_page(logical_handle,&uStack_e);
  if (uVar2 != 0) goto LAB_00068b1e;
  uVar2 = nvm_classify_storage_range(0,(uint)uStack_e << 6,0x40);
  if (uVar2 == 2) {
    uVar2 = nvm_get_logical_storage_page(logical_handle + 4,&uStack_e);
    if (uVar2 != 0) goto LAB_00068b1e;
    uVar2 = nvm_classify_storage_range(0,(uint)uStack_e << 6,0x40);
    if (uVar2 == 2) {
      uVar2 = nvm_get_logical_storage_page(logical_handle + 8,&uStack_e);
      if (uVar2 != 0) goto LAB_00068b1e;
      uVar2 = nvm_classify_storage_range(0,(uint)uStack_e << 6,0x40);
      if (uVar2 == 2) {
        uVar3 = 0x5a;
        goto LAB_00068b1e;
      }
    }
  }
  if (uVar2 == 3) {
    uVar3 = 0;
  }
LAB_00068b1e:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x4e92u + (uint32_t)((int)(puVar1 + 1)))))) = (code)0x0;
  nvm_poll_probe_mode();
  return uVar3;
}

uint nvm_handle_family0_read_result(uchar result,ushort logical_handle,uchar *record)

{
  ushort uVar1;
  ushort uVar2;
  uint uVar3;
  uchar uVar4;
  int iVar5;
  uint32_t puVar6;
  uchar *puVar7;
  int iVar8;
  uint uVar9;
  uint uVar10;
  code cVar11;
  uint uVar12;
  
  uVar4 = nvm_copy_read_retry;
  puVar6 = 0xfebeb800u;
  iVar8 = 0x5a;
  uVar10 = (uint)(*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0x2b010u + (uint32_t)(logical_handle) * (uint32_t)sizeof(F33NvmApplicationRoute)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmApplicationRoute) + (uint32_t)offsetof(F33NvmApplicationRoute, object)))));
  uVar1 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x2ad8cu + (uint32_t)(uVar10) * (uint32_t)sizeof(F33NvmFamily0RamDescriptor)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmFamily0RamDescriptor) + (uint32_t)offsetof(F33NvmFamily0RamDescriptor, logical_count)))));
  uVar2 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x2ad8cu + (uint32_t)(uVar10) * (uint32_t)sizeof(F33NvmFamily0RamDescriptor)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmFamily0RamDescriptor) + (uint32_t)offsetof(F33NvmFamily0RamDescriptor, first_logical_handle)))));
  uVar9 = (uint)(*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x2ad8cu + (uint32_t)(uVar10) * (uint32_t)sizeof(F33NvmFamily0RamDescriptor)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmFamily0RamDescriptor) + (uint32_t)offsetof(F33NvmFamily0RamDescriptor, payload_bytes)))));
  iVar5 = 0;
  if (result == '\0') {
    cVar11 = (code)0x0;
    iVar8 = 0;
  }
  else if (nvm_copy_read_retry < 2) {
    puVar6 = 0xfebeb800u;
    nvm_enqueue_read(logical_handle, camry_host_addr(record));
    cVar11 = (code)(uVar4 + '\x01');
    iVar5 = iVar8;
  }
  else {
    cVar11 = (code)0x0;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x4e92u + (uint32_t)((int)(puVar6 + 2)))))) = cVar11;
  if (iVar5 != 0x5a) {
    if (iVar8 != 0x5a) {
      uVar3 = (*((uint *)camry_host_ptr((uint32_t)(puVar6 + 0x5488))));
      uVar12 = 0x3c;
      if (0x38 < uVar9) {
        uVar12 = uVar9 + 4 & 0xffff;
      }
      if ((*(uint *)(record + uVar12) ^ uVar3) == 0xffffffff) {
        if (((*((short *)camry_host_ptr((uint32_t)(puVar6 + uVar10 * 2 + 0x4b68)))) == -1) ||
           (uVar3 - (*((int *)camry_host_ptr((uint32_t)(puVar6 + uVar10 * 4 + 0x4ba8)))) < 0xc0000001)) {
          puVar7 = ((void *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x2ad8cu + (uint32_t)(uVar10) * (uint32_t)sizeof(F33NvmFamily0RamDescriptor)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmFamily0RamDescriptor) + (uint32_t)offsetof(F33NvmFamily0RamDescriptor, buffer))))))));
          for (iVar5 = 0; (int)(iVar5 - uVar9) < 0 != (iVar5 < 0 && -1 < (int)(iVar5 - uVar9));
              iVar5 = iVar5 + 1) {
            puVar7[iVar5] = record[iVar5 + 4];
          }
          (*((uint *)camry_host_ptr((uint32_t)(puVar6 + uVar10 * 4 + 0x4ba8)))) = uVar3;
          (*((ushort *)camry_host_ptr((uint32_t)(puVar6 + uVar10 * 2 + 0x4b68)))) = logical_handle;
        }
      }
    }
    if ((uint)(ushort)((uVar1 + uVar2) - 1) <= (uint)logical_handle) {
      cVar11 = (code)0xa5;
      if ((*((short *)camry_host_ptr((uint32_t)(puVar6 + uVar10 * 2 + 0x4b68)))) != -1) {
        cVar11 = (code)0x5a;
      }
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x4b38u + (uint32_t)((int)(puVar6 + uVar10)))))) = cVar11;
      return 0x5a;
    }
  }
  return 0;
}

uint nvm_handle_family0_write_result(uchar result,ushort logical_handle)

{
  byte bVar1;
  uint uVar2;
  uchar uVar3;
  
  bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0x2b010u + (uint32_t)(logical_handle) * (uint32_t)sizeof(F33NvmApplicationRoute)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmApplicationRoute) + (uint32_t)offsetof(F33NvmApplicationRoute, object)))));
  uVar2 = (uint)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebf0368u + (uint32_t)(bVar1) * 2u))));
  if ((uVar2 == 0xffff) ||
     (uVar2 = uVar2 + 1 & 0xffff,
     (((uint)(*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x2ad8cu + (uint32_t)(bVar1) * (uint32_t)sizeof(F33NvmFamily0RamDescriptor)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmFamily0RamDescriptor) + (uint32_t)offsetof(F33NvmFamily0RamDescriptor, logical_count))))) +
      (uint)(*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x2ad8cu + (uint32_t)(bVar1) * (uint32_t)sizeof(F33NvmFamily0RamDescriptor)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmFamily0RamDescriptor) + (uint32_t)offsetof(F33NvmFamily0RamDescriptor, first_logical_handle)))))) - 1 & 0xffff) < uVar2)) {
    uVar2 = (uint)(*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x2ad8cu + (uint32_t)(bVar1) * (uint32_t)sizeof(F33NvmFamily0RamDescriptor)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmFamily0RamDescriptor) + (uint32_t)offsetof(F33NvmFamily0RamDescriptor, first_logical_handle)))));
  }
  if ((result == '\0') && (uVar2 == logical_handle)) {
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebf0368u + (uint32_t)(bVar1) * 2u)))) = (ushort)uVar2;
    uVar3 = 'Z';
  }
  else {
    uVar3 = 0xa5;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebf0338u + (uint32_t)(bVar1) * 1u)))) = uVar3;
  return 0x5a;
}

uint nvm_handle_family1_read_result(uchar result,ushort logical_handle)

{
  byte *pbVar1;
  ushort uVar2;
  uchar uVar3;
  undefined1 uVar4;
  uint uVar5;
  uint32_t puVar6;
  uint uVar7;
  uint32_t puVar8;
  byte bVar9;
  int iVar10;
  int iVar11;
  uint uVar12;
  short sVar13;
  uint uVar14;
  code cVar15;
  uint uVar16;
  
  uVar3 = nvm_copy_read_retry;
  puVar6 = 0xfebeb800u;
  uVar7 = (uint)logical_handle;
  uVar12 = (uint)(*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0x2b010u + (uint32_t)(uVar7) * (uint32_t)sizeof(F33NvmApplicationRoute)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmApplicationRoute) + (uint32_t)offsetof(F33NvmApplicationRoute, object)))));
  uVar14 = uVar12 & 3;
  uVar5 = (uint)(*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x2af0cu + (uint32_t)(uVar12) * (uint32_t)sizeof(F33NvmFamily1RamDescriptor)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmFamily1RamDescriptor) + (uint32_t)offsetof(F33NvmFamily1RamDescriptor, first_logical_handle)))));
  uVar16 = (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebf0698u + (uint32_t)(uVar14) * 4u))));
  iVar10 = 0;
  uVar2 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x2af0cu + (uint32_t)(uVar12) * (uint32_t)sizeof(F33NvmFamily1RamDescriptor)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmFamily1RamDescriptor) + (uint32_t)offsetof(F33NvmFamily1RamDescriptor, payload_bytes)))));
  if (uVar7 == uVar5) {
    iVar11 = 0;
    uVar16 = 0;
LAB_00068d34:
    sVar13 = (short)uVar14;
    if (result == '\0') {
      cVar15 = (code)0x0;
    }
    else if (nvm_copy_read_retry < 2) {
      puVar6 = 0xfebeb800u;
      nvm_enqueue_read(logical_handle, camry_host_addr(((volatile F33NvmCopyStage *)camry_host_ptr((uint32_t)(0xfebf0b08u + (uint32_t)(sVar13) * (uint32_t)sizeof(F33NvmCopyStage))))[0].raw + iVar11 * 0x20));
      cVar15 = (code)(uVar3 + '\x01');
      iVar10 = 0x5a;
    }
    else {
      cVar15 = (code)0x0;
      uVar16 = uVar16 | 0x5a << (iVar11 << 3);
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x4e92u + (uint32_t)((int)(puVar6 + 2)))))) = cVar15;
    if ((iVar10 != 0x5a) && (iVar11 == 2)) {
      iVar10 = 0;
      for (uVar5 = 0; uVar5 < uVar2; uVar5 = uVar5 + 1 & 0xffff) {
        pbVar1 = ((void *)camry_host_ptr((uint32_t)(puVar6 + sVar13 * 0x60 + uVar5 + 0x5308)));
        bVar9 = pbVar1[0x20] ^ 0x55;
        if (((*pbVar1 != (pbVar1[0x40] ^ 0xaa)) || ((uVar16 & 0x5a005a) != 0)) &&
           ((*pbVar1 != bVar9 || ((uVar16 & 0x5a5a) != 0)))) {
          if ((bVar9 == (pbVar1[0x40] ^ 0xaa)) && ((uVar16 & 0x5a5a00) == 0)) {
            *pbVar1 = bVar9;
          }
          else {
            iVar10 = 0x5a;
          }
        }
      }
      if (iVar10 == 0) {
        puVar8 = (*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x2af0cu + (uint32_t)(uVar12) * (uint32_t)sizeof(F33NvmFamily1RamDescriptor)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmFamily1RamDescriptor) + (uint32_t)offsetof(F33NvmFamily1RamDescriptor, buffer)))));
        for (iVar10 = 0; iVar11 = iVar10 - (uint)uVar2, ((iVar11 < 0) || (iVar10 < 0));
            iVar10 = iVar10 + 1) {
          (*((undefined *)camry_host_ptr((uint32_t)(iVar10 + (int)puVar8)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(iVar10 + sVar13 * 0x60 + 0x5308)))));
        }
        uVar4 = 0x5a;
      }
      else {
        uVar4 = 0xa5;
      }
      uVar5 = 0x5a;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(uVar12 + 0x4b58))))) = uVar4;
      goto LAB_00068e0e;
    }
  }
  else {
    if (uVar7 == uVar5 + 4) {
      iVar11 = 1;
      goto LAB_00068d34;
    }
    if (uVar7 == uVar5 + 8) {
      iVar11 = 2;
      goto LAB_00068d34;
    }
    uVar16 = 0x5a5a5a;
  }
  uVar5 = 0;
LAB_00068e0e:
  (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebf0698u + (uint32_t)(uVar14) * 4u)))) = uVar16;
  return uVar5;
}

uint nvm_handle_family1_write_result(uchar result,ushort logical_handle)

{
  uint uVar1;
  uint uVar2;
  uchar uVar3;
  uint uVar4;
  int iVar5;
  uint uVar6;
  
  uVar2 = (uint)logical_handle;
  uVar6 = (uint)(*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0x2b010u + (uint32_t)(uVar2) * (uint32_t)sizeof(F33NvmApplicationRoute)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmApplicationRoute) + (uint32_t)offsetof(F33NvmApplicationRoute, object)))));
  uVar4 = (uint)(*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x2af0cu + (uint32_t)(uVar6) * (uint32_t)sizeof(F33NvmFamily1RamDescriptor)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmFamily1RamDescriptor) + (uint32_t)offsetof(F33NvmFamily1RamDescriptor, first_logical_handle)))));
  if (uVar2 == uVar4) {
    iVar5 = 0;
    uVar1 = 0;
LAB_00068e6e:
    if (result != '\0') {
      uVar1 = uVar1 | 0x5a << (iVar5 << 3);
    }
    if (iVar5 == 2) {
      uVar3 = 0xa5;
      if (uVar1 == 0) {
        uVar3 = 'Z';
      }
      uVar2 = 0x5a;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebf0358u + (uint32_t)(uVar6) * 1u)))) = uVar3;
      goto LAB_00068e9a;
    }
  }
  else {
    uVar1 = (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebf0698u + (uint32_t)(uVar6 & 3) * 4u))));
    if (uVar2 == uVar4 + 4) {
      iVar5 = 1;
      goto LAB_00068e6e;
    }
    if (uVar2 == uVar4 + 8) {
      iVar5 = 2;
      goto LAB_00068e6e;
    }
    uVar1 = 0x5a5a5a;
  }
  uVar2 = 0;
LAB_00068e9a:
  (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebf0698u + (uint32_t)(uVar6 & 3) * 4u)))) = uVar1;
  return uVar2;
}

uint nvm_route_application_result(uchar event,ushort logical_handle,uchar result)

{
  F33NvmApplicationRoute FVar1;
  uint32_t puVar2;
  uint uVar3;
  uint uVar4;
  
  puVar2 = 0xfebeb800u;
  FVar1 = ((volatile F33NvmApplicationRoute *)camry_host_ptr((uint32_t)(0x2b010u + (uint32_t)(logical_handle) * (uint32_t)sizeof(F33NvmApplicationRoute))))[0];
  uVar4 = FVar1.object;
  if (FVar1.family == 0) {
    uVar3 = nvm_get_family0_completion((ushort)uVar4);
    if ((uVar3 == 0xff) && ((*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x2ad8cu + (uint32_t)(uVar4) * (uint32_t)sizeof(F33NvmFamily0RamDescriptor)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmFamily0RamDescriptor) + (uint32_t)offsetof(F33NvmFamily0RamDescriptor, first_logical_handle))))) != 0xffff))
    {
      if (event == '\x06') {
        uVar4 = nvm_handle_family0_read_result(result, logical_handle, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + 0x5488))));
      }
      else {
        if (event != '\a') {
          return 0;
        }
        uVar4 = nvm_handle_family0_write_result(result,logical_handle);
      }
      if (uVar4 == 0x5a) {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x4e90))))) = 0;
      }
    }
  }
  else if (((FVar1.family == 1) &&
           (uVar3 = nvm_get_family1_completion((ushort)uVar4), uVar3 == 0xff)) &&
          ((*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x2af0cu + (uint32_t)(uVar4) * (uint32_t)sizeof(F33NvmFamily1RamDescriptor)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmFamily1RamDescriptor) + (uint32_t)offsetof(F33NvmFamily1RamDescriptor, first_logical_handle))))) != 0xffff)) {
    if (event == '\x06') {
      uVar4 = nvm_handle_family1_read_result(result,logical_handle);
    }
    else {
      if (event != '\a') {
        return 0;
      }
      uVar4 = nvm_handle_family1_write_result(result,logical_handle);
    }
    if (uVar4 == 0x5a) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x4e91))))) = 0;
    }
  }
  return 0;
}

uchar get_nvm_direct_operation_request_byte_68f64(void)

{
  return nvm_direct_operation_request;
}

undefined4 return_const_0_68f6a(void)

{
  return 0;
}

undefined4 return_const_0_68f6e(void)

{
  return 0;
}

void crypto_bank_clear_fragment_history(void)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  
  uVar2 = 0;
  do {
    uVar3 = 0;
    do {
      iVar1 = uVar3 + uVar2 * 8;
      uVar3 = uVar3 + 1;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe50c6u + (uint32_t)(iVar1) * 1u)))) = '\0';
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5106u + (uint32_t)(iVar1) * 1u)))) = '\0';
    } while (uVar3 < 8);
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe503cu + (uint32_t)(uVar2) * 1u)))) = '\0';
    uVar3 = uVar2 + 1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5044u + (uint32_t)(uVar2) * 1u)))) = '\0';
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe504cu + (uint32_t)(uVar2) * 1u)))) = '\0';
    uVar2 = uVar3;
  } while (uVar3 < 8);
  crypto_key_fragment_qualified_mask = '\0';
  return;
}

void crypto_bank_clear_key_material(uchar slot)

{
  uint uVar1;
  uint uVar2;
  
  if (slot < 2) {
    uVar2 = 0;
    do {
      uVar1 = uVar2 + 1;
      crypto_key_request[slot][uVar2] = '\0';
      uVar2 = uVar1;
    } while (uVar1 < 0x40);
    uVar2 = 0;
    do {
      uVar1 = uVar2 + 1;
      crypto_key_result[(short)(ushort)slot][uVar2] = '\0';
      uVar2 = uVar1;
    } while (uVar1 < 0x30);
  }
  return;
}

void crypto_bank_clear_test_material(void)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  
  uVar2 = 0;
  do {
    uVar3 = 0;
    do {
      iVar1 = uVar3 + uVar2 * 8;
      uVar3 = uVar3 + 1;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5146u + (uint32_t)(iVar1) * 1u)))) = '\0';
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5166u + (uint32_t)(iVar1) * 1u)))) = '\0';
    } while (uVar3 < 8);
    uVar2 = uVar2 + 1;
  } while (uVar2 < 4);
  uVar2 = 0;
  do {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe50a6u + (uint32_t)(uVar2) * 1u)))) = '\0';
    uVar3 = uVar2 + 1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe50abu + (uint32_t)(uVar2) * 1u)))) = '\0';
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe50b0u + (uint32_t)(uVar2) * 1u)))) = '\0';
    uVar2 = uVar3;
  } while (uVar3 < 5);
  uVar2 = 0;
  do {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5186u + (uint32_t)(uVar2) * 1u)))) = '\0';
    uVar2 = uVar2 + 1;
  } while (uVar2 < 0x10);
  uVar2 = 0;
  do {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5196u + (uint32_t)(uVar2) * 1u)))) = '\0';
    uVar3 = uVar2 + 1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe51a6u + (uint32_t)(uVar2) * 1u)))) = '\0';
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe51b6u + (uint32_t)(uVar2) * 1u)))) = '\0';
    uVar2 = uVar3;
  } while (uVar3 < 0x10);
  crypto_test_selector = '\0';
  DAT_febe509f = 0;
  crypto_test_mode = '\0';
  DAT_febe50a0 = 0;
  DAT_febe509e = 0;
  DAT_febe50a1 = 0;
  crypto_test_qualified_mask = '\0';
  return;
}
