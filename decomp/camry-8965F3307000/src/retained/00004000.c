#include "common.h"

void read_fifo_and_dispatch_frame_without_status_check_400a(uint param_1)

{
  uint8_t stack_record_1a[28];
  
  read_and_advance_fifo_frame_if_status_bit3_3f96((param_1 & 0x7f) >> 4, param_1 & 0xf, camry_host_addr(((uint32_t *)((stack_record_1a + 2)))), camry_host_addr(((uint8_t *)(stack_record_1a))), ((uint8_t *)((stack_record_1a + 1))), ((uint8_t *)((stack_record_1a + 6))));
  dispatch_matching_receive_routes_with_payload_4678(param_1 & 0xffff,(*((uint32_t *)(stack_record_1a + 2))),stack_record_1a[0],stack_record_1a[1],((uint8_t *)((stack_record_1a + 6))));
  return;
}

void dispatch_pending_type3_fifo_frames_4048(uint param_1)

{
  int iVar1;
  uint uVar2;
  undefined8 uVar3;
  int iVar4;
  uint uVar5;
  uint uVar6;
  
  uVar3 = 0x869c00000000;
  uVar6 = (param_1 & 7) << 4;
  iVar4 = read_channel_three_fifo_status_bits_3f4a(param_1 & 7);
  uVar5 = 0;
  do {
    uVar6 = uVar6 & 0xfffffff0 | uVar5 & 0xf;
    if (((*((byte *)camry_host_ptr((uint32_t)(uVar6 * 0xc + (*((volatile int32_t *)camry_host_ptr((uint32_t)((int)((ulonglong)uVar3 >> 0x20) + 0x2d4)))))))) >> 5 == 3) &&
       ((iVar4 >> (uVar5 & 0xf) & 1U) != 0)) {
      read_fifo_and_dispatch_frame_without_status_check_400a(uVar6);
    }
    uVar2 = uVar5 + 1;
    iVar1 = uVar5 - 0xf;
    uVar5 = uVar2;
  } while (iVar1 < 0 != ((int)uVar2 < 0 && -1 < iVar1));
  return;
}

uint boot_prepare_aligned_input_ring
               (uint address,uint length,uint *aligned_address,uint *padded_length)

{
  int iVar1;
  uint uVar2;
  
  if (length != 0) {
    uVar2 = address & 0x1ff;
    *aligned_address = address & 0xfffffe00;
    *padded_length = uVar2 + length;
    for (iVar1 = 0; (int)(iVar1 - uVar2) < 0 != (iVar1 < 0 && -1 < (int)(iVar1 - uVar2));
        iVar1 = iVar1 + 1) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff8000u) + (uint32_t)(iVar1) * 1u)))) = 0xff;
    }
    (*((volatile uint16_t *)camry_host_ptr((camry_gp + 0xffff9198u)))) = (short)uVar2;
    (*((volatile uint16_t *)camry_host_ptr((camry_gp + 0xffff919au)))) = 0;
    return 0;
  }
  return 1;
}

uint boot_submit_program_stream(uint address,uint length)

{
  bool bVar1;
  int iVar2;
  uint32_t puVar3;
  uint uVar4;
  uint uVar5;
  uint local_10;
  uint uStack_c;
  
  puVar3 = (camry_gp + 0x0u);
  uVar5 = 1;
  if ((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff92a1u)))) == '\0') {
    if (length == 0) {
      bVar1 = true;
    }
    else {
      local_10 = address & 0xfffffe00;
      uVar4 = address & 0x1ff;
      uStack_c = uVar4 + length;
      for (iVar2 = 0; (int)(iVar2 - uVar4) < 0 != (iVar2 < 0 && -1 < (int)(iVar2 - uVar4));
          iVar2 = iVar2 + 1) {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebf1800u + (uint32_t)(iVar2) * 1u)))) = 0xff;
      }
      DAT_febf2998 = (undefined2)uVar4;
      bVar1 = false;
      DAT_febf299a = 0;
    }
    if ((!bVar1) &&
       (uVar4 = boot_check_rounded_program_span_blank(local_10,uStack_c), uVar4 == 0)) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6e64))))) = 1;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-28000))))) = 1;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-27999))))) = 1;
      (*((uint *)camry_host_ptr((uint32_t)(puVar3 + -0x6e74)))) = local_10;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6e63))))) = 0;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6e62))))) = 0;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6e61))))) = 0;
      (*((uint *)camry_host_ptr((uint32_t)(puVar3 + -0x6e70)))) = uStack_c;
      uVar5 = 0;
    }
  }
  return uVar5;
}

uint boot_submit_block_erase(uint address,uint length)

{
  uint8_t stack_record_20[32];
  uint32_t puVar1;
  uint uVar2;
  uint uVar3;
  
  puVar1 = (camry_gp + 0x0u);
  uVar3 = 1;
  if ((((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff92a1u)))) == '\0') &&
      (uVar2 = boot_select_operation_blocks(address,length,((uint32_t *)(stack_record_20)),((uint32_t *)((stack_record_20 + 4)))), uVar2 == 0))
     && (uVar2 = boot_select_counter_block_for_range(address,length,((uint32_t *)((stack_record_20 + 12)))), uVar2 == 0)) {
    boot_clear_flash_block_skip_flags((*((uint32_t *)(stack_record_20 + 0))),(*((uint32_t *)(stack_record_20 + 4))));
    (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x6e80)))) = (*((uint32_t *)(stack_record_20 + 0)));
    (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x6e7c)))) = (*((uint32_t *)(stack_record_20 + 4)));
    boot_find_flash_block_end((*((uint32_t *)(stack_record_20 + 0))),((uint32_t *)((stack_record_20 + 8))));
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-28000))))) = 1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-27999))))) = 1;
    (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x6e78)))) = (*((uint32_t *)(stack_record_20 + 8)));
    uVar3 = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6e64))))) = 2;
    (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x6e6c)))) = (*((uint32_t *)(stack_record_20 + 12)));
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6e63))))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6e62))))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6e61))))) = 0;
  }
  return uVar3;
}

void boot_set_flash_worker_pause(uchar paused)

{
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff919fu)))) = paused;
  return;
}

void boot_request_flash_worker_cancel(void)

{
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff919eu)))) = 1;
  return;
}

void boot_append_program_input(uchar *source,ushort length)

{
  uchar uVar1;
  uint uVar2;
  uint uVar3;
  
  uVar3 = (uint)(*((volatile uint16_t *)camry_host_ptr((camry_gp + 0xffff9198u))));
  for (; length != 0; length = length - 1) {
    uVar1 = *source;
    uVar2 = uVar3 + 1 & 0xffff;
    source = source + 1;
    if (0x10ff < uVar2) {
      uVar2 = 0;
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff8000u) + (uint32_t)(uVar3) * 1u)))) = uVar1;
    uVar3 = uVar2;
  }
  (*((volatile uint16_t *)camry_host_ptr((camry_gp + 0xffff9198u)))) = (short)uVar3;
  return;
}

uint boot_program_input_occupancy(void)

{
  ushort uVar1;
  uint32_t puVar2;
  undefined4 uVar3;
  ushort uVar4;
  
  puVar2 = (camry_gp + 0x0u);
  uVar3 = raise_pmr_and_return_previous_mask_721e(0xffff);
  uVar4 = (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x6e68))));
  uVar1 = (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x6e66))));
  if (uVar4 < uVar1) {
    uVar4 = 0x1100 - (uVar1 - uVar4);
  }
  else {
    uVar4 = uVar4 - uVar1;
  }
  restore_pmr_preserving_interrupt_disable_state_7244(uVar3);
  return (uint)uVar4;
}

uint boot_program_input_has_insufficient_space(ushort requested_length)

{
  int iVar1;
  uint uVar2;
  
  uVar2 = boot_program_input_occupancy();
  iVar1 = (0x1100 - uVar2) - (requested_length + 1);
  return (uint)(iVar1 < 0 != ((int)(0x1100 - uVar2) < 0 && -1 < iVar1));
}

uint boot_stage_preserved_program_counter(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  
  uVar4 = 1;
  if ((((*((volatile uint32_t *)camry_host_ptr((camry_gp + 0xffff9194u)))) != 0) && ((*((volatile uint32_t *)camry_host_ptr((camry_gp + 0xffff9180u)))) <= (*((volatile uint32_t *)camry_host_ptr((camry_gp + 0xffff9194u)))))) &&
     ((*((volatile uint32_t *)camry_host_ptr((camry_gp + 0xffff9194u)))) < (*((volatile uint32_t *)camry_host_ptr((camry_gp + 0xffff9188u)))))) {
    (*((volatile uint32_t *)camry_host_ptr((camry_gp + 0xffff91a0u)))) = (*((volatile int32_t *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((camry_gp + 0xffff9194u)))))))) + 1;
    iVar3 = 1;
    do {
      (*((volatile uint32_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff91a0u) + (uint32_t)(iVar3) * 4u)))) = 0xffffffff;
      iVar2 = iVar3 + 1;
      iVar1 = iVar3 + -0x3f;
      iVar3 = iVar2;
    } while (((iVar1 < 0) || (iVar2 < 0)));
    uVar4 = 0;
  }
  return uVar4;
}

uint boot_erase_current_block_preserving_counter(void)

{
  undefined4 uVar1;
  uint32_t puVar2;
  uint uVar3;
  uint uVar4;
  char cStack_11;
  camry_fill_bytes(&cStack_11, sizeof cStack_11);
  
  puVar2 = (camry_gp + 0x0u);
  uVar4 = 0;
  uVar3 = boot_get_flash_block_skip_flag((*((volatile uint32_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff9180u))))));
  if (uVar3 != 1) {
    uVar3 = boot_stage_preserved_program_counter();
    uVar1 = (*((volatile uint32_t *)camry_host_ptr(0xfebf0fd0u)));
    (*(int (*)())camry_indirect((uint32_t)(*((volatile uint32_t *)camry_host_ptr(0xfebf0fd0u)))))((*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + -0x6e80)))),0,1,camry_host_addr(&cStack_11))
    ;
    if ((cStack_11 != '\0') ||
       ((uVar3 == 0 &&
        ((*(int (*)())camry_indirect((uint32_t)(uVar1)))((*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + -0x6e6c)))),puVar2 + -0x6e60,0,camry_host_addr(&cStack_11)),
        cStack_11 != '\0')))) {
      uVar4 = 1;
    }
  }
  return uVar4;
}

void boot_consume_program_input(uchar *destination,ushort length)

{
  uchar *puVar1;
  uint uVar2;
  
  uVar2 = (uint)(*((volatile uint16_t *)camry_host_ptr((camry_gp + 0xffff919au))));
  for (; length != 0; length = length - 1) {
    puVar1 = ((undefined *)camry_host_ptr((uint32_t)((camry_gp + 0xffff8000u) + (uint32_t)(uVar2) * 1u)));
    uVar2 = uVar2 + 1 & 0xffff;
    *destination = *puVar1;
    destination = destination + 1;
    if (0x10ff < uVar2) {
      uVar2 = 0;
    }
  }
  (*((volatile uint16_t *)camry_host_ptr((camry_gp + 0xffff919au)))) = (short)uVar2;
  return;
}

uint boot_stage_and_program_input_chunk(uint length)

{
  uint32_t puVar1;
  uint uVar2;
  uint uVar3;
  uchar *destination;
  char cStack_11;
  
  puVar1 = (camry_gp + 0x0u);
  uVar3 = 2;
  uVar2 = boot_program_input_occupancy();
  if ((length & 0xffff) <= uVar2) {
    destination = ((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x6e60)));
    boot_consume_program_input(destination,(ushort)length);
    for (; (int)(length - 0x100) < 0 != ((int)length < 0 && -1 < (int)(length - 0x100));
        length = length + 1) {
      destination[length] = 0xff;
    }
    if ((*((int *)camry_host_ptr((uint32_t)(puVar1 + -0x6e74)))) == (*((int *)camry_host_ptr((uint32_t)(puVar1 + -0x6e6c))))) {
      cStack_11 = '\0';
    }
    else {
      (*(int (*)())camry_indirect((uint32_t)(*((volatile uint32_t *)camry_host_ptr(0xfebf0fd0u)))))((*((int *)camry_host_ptr((uint32_t)(puVar1 + -0x6e74)))),camry_host_addr(destination),0,camry_host_addr(&cStack_11));
    }
    uVar3 = (uint)(cStack_11 != '\0');
  }
  return uVar3;
}

void boot_advance_flash_operation(void)

{
  char cVar1;
  bool bVar2;
  uint32_t puVar3;
  undefined4 uVar4;
  uint uVar5;
  uint uVar6;
  undefined1 uVar7;
  char cVar8;
  uint local_18;
  
  puVar3 = (camry_gp + 0x0u);
  uVar4 = raise_pmr_and_return_previous_mask_721e(0xffff);
  cVar8 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-27999)))));
  if (cVar8 == '\0') goto LAB_00004586;
  uVar7 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-28000)))));
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6e61))))) != '\0') goto LAB_0000456c;
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6e64)))));
  if (cVar1 == '\0') {
    bVar2 = false;
    if ((*((uint *)camry_host_ptr((uint32_t)(puVar3 + -0x6e78)))) <= (*((uint *)camry_host_ptr((uint32_t)(puVar3 + -0x6e74))))) {
      uVar6 = boot_program_input_occupancy();
      if (uVar6 == 0) {
        bVar2 = true;
      }
      else {
        (*((uint *)camry_host_ptr((uint32_t)(puVar3 + -0x6e80)))) = (*((uint *)camry_host_ptr((uint32_t)(puVar3 + -0x6e78))));
        boot_find_flash_block_end((*((uint *)camry_host_ptr((uint32_t)(puVar3 + -0x6e78)))),&local_18);
        (*((uint *)camry_host_ptr((uint32_t)(puVar3 + -0x6e78)))) = local_18;
      }
    }
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6e63))))) == '\x01') {
      uVar6 = boot_program_input_occupancy();
      (*((uint *)camry_host_ptr((uint32_t)(puVar3 + -0x6e70)))) = uVar6;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6e63))))) = 0;
    }
    if (!bVar2) {
      uVar6 = boot_erase_current_block_preserving_counter();
      if (uVar6 == 1) {
LAB_000044ce:
        cVar8 = '\0';
      }
      else {
        uVar6 = (*((uint *)camry_host_ptr((uint32_t)(puVar3 + -0x6e70))));
        if (uVar6 != 0) {
          if (0xff < uVar6) {
            uVar6 = 0x100;
          }
          uVar5 = boot_stage_and_program_input_chunk(uVar6);
          if (uVar5 == 1) goto LAB_000044ce;
          if (uVar5 == 0) {
            (*((uint *)camry_host_ptr((uint32_t)(puVar3 + -0x6e74)))) = (*((int *)camry_host_ptr((uint32_t)(puVar3 + -0x6e74)))) + uVar6;
            (*((uint *)camry_host_ptr((uint32_t)(puVar3 + -0x6e70)))) = (*((int *)camry_host_ptr((uint32_t)(puVar3 + -0x6e70)))) - uVar6;
          }
        }
      }
    }
    uVar6 = (*((uint *)camry_host_ptr((uint32_t)(puVar3 + -0x6e70))));
LAB_00004534:
    if (uVar6 == 0) {
LAB_00004550:
      uVar7 = 0;
      cVar8 = '\0';
    }
  }
  else if (cVar1 == '\x01') {
    uVar6 = (*((uint *)camry_host_ptr((uint32_t)(puVar3 + -0x6e70))));
    if (0xff < uVar6) {
      uVar6 = 0x100;
    }
    uVar5 = boot_stage_and_program_input_chunk(uVar6);
    if (uVar5 == 1) {
LAB_00004540:
      cVar8 = '\0';
    }
    else if (uVar5 == 0) {
      (*((uint *)camry_host_ptr((uint32_t)(puVar3 + -0x6e74)))) = (*((int *)camry_host_ptr((uint32_t)(puVar3 + -0x6e74)))) + uVar6;
      uVar5 = (*((uint *)camry_host_ptr((uint32_t)(puVar3 + -0x6e70))));
      (*((uint *)camry_host_ptr((uint32_t)(puVar3 + -0x6e70)))) = uVar5 - uVar6;
      if (uVar5 == uVar6) goto LAB_00004550;
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6e63))))) != '\x01') goto LAB_0000456c;
      uVar6 = boot_program_input_occupancy();
      goto LAB_00004534;
    }
  }
  else if (cVar1 == '\x02') {
    uVar6 = boot_erase_current_block_preserving_counter();
    if (uVar6 == 1) goto LAB_00004540;
    if ((*((int *)camry_host_ptr((uint32_t)(puVar3 + -0x6e80)))) == (*((int *)camry_host_ptr((uint32_t)(puVar3 + -0x6e7c))))) goto LAB_00004550;
    (*((uint *)camry_host_ptr((uint32_t)(puVar3 + -0x6e80)))) = (*((uint *)camry_host_ptr((uint32_t)(puVar3 + -0x6e78))));
    boot_find_flash_block_end((*((uint *)camry_host_ptr((uint32_t)(puVar3 + -0x6e78)))),&local_18);
    (*((uint *)camry_host_ptr((uint32_t)(puVar3 + -0x6e78)))) = local_18;
  }
LAB_0000456c:
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6e62))))) == '\x01') {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6e62))))) = 0;
    cVar8 = '\0';
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6e61))))) = 0;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-28000))))) = uVar7;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-27999))))) = cVar8;
LAB_00004586:
  restore_pmr_preserving_interrupt_disable_state_7244(uVar4);
  return;
}

void boot_reset_flash_operation_queue(void)

{
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff92a1u)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff919fu)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff919eu)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff919du)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff92a0u)))) = 1;
  (*((volatile uint16_t *)camry_host_ptr((camry_gp + 0xffff9198u)))) = 0;
  (*((volatile uint16_t *)camry_host_ptr((camry_gp + 0xffff919au)))) = 0;
  return;
}

void cancel_transmit_by_pdu_mapping_45b2(int param_1)

{
  uint8_t stack_record_10[16];
  uint uVar1;
  
  uVar1 = 0;
  while( true ) {
    if ((*((volatile uint16_t *)camry_host_ptr((camry_tp + 0x2a8u)))) <= uVar1) {
      return;
    }
    if (param_1 == (*((int *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((camry_tp + 0x2a0u)))) + uVar1 * 0xc))))) break;
    uVar1 = uVar1 + 1 & 0xffff;
  }
  ((uint32_t *)(stack_record_10))[0] = (*((undefined4 *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((camry_tp + 0x2a0u)))) + uVar1 * 0xc + 4))));
  stack_record_10[8] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((camry_tp + 0x2a0u)))) + (uint32_t)(uVar1 * 0xc + 8)))));
  ((void)(((uint32_t *)(stack_record_10))), guarded_cancel_tx_buffer_if_channel_ready_37e4((*((undefined2 *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((camry_tp + 0x2a0u)))) + uVar1 * 0xc + 10))))));
  return;
}

undefined4 submit_at_most_eight_byte_mapped_pdu_4606(int param_1,undefined4 *param_2)

{
  uint8_t stack_record_14[20];
  uint uVar1;
  int iVar2;
  
  if (*(ushort *)(param_2 + 1) < 9) {
    for (uVar1 = 0; uVar1 < (*((volatile uint16_t *)camry_host_ptr((camry_tp + 0x2a8u)))); uVar1 = uVar1 + 1 & 0xffff) {
      if (param_1 == (*((int *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((camry_tp + 0x2a0u)))) + uVar1 * 0xc))))) {
        (*((uint32_t *)(stack_record_14 + 0))) = (*((undefined4 *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((camry_tp + 0x2a0u)))) + uVar1 * 0xc + 4))));
        stack_record_14[8] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((camry_tp + 0x2a0u)))) + (uint32_t)(uVar1 * 0xc + 8)))));
        stack_record_14[9] = (undefined1)*(ushort *)(param_2 + 1);
        (*((uint32_t *)(stack_record_14 + 4))) = *param_2;
        iVar2 = guarded_submit_tx_buffer_from_descriptor_374e((*((undefined2 *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((camry_tp + 0x2a0u)))) + uVar1 * 0xc + 10)))),stack_record_14);
        if (iVar2 == 0) {
          return 0;
        }
        return 1;
      }
    }
  }
  return 1;
}

void dispatch_matching_receive_routes_with_payload_4678(uint param_1,int param_2,char param_3,uint param_4,undefined4 *param_5)

{
  uint8_t stack_record_34[52];
  undefined4 *puVar1;
  undefined4 *puVar2;
  bool bVar3;
  bool bVar4;
  undefined8 uVar5;
  uint uVar6;
  ushort uVar7;
  
  uVar5 = 0x869c00000000;
  puVar1 = ((undefined4 *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((camry_tp + 0x2a4u)))) + (param_1 & 0xffff) * 8)));
  uVar6 = (uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(puVar1) + 6))));
  uVar7 = *(ushort *)(puVar1 + 1);
  bVar4 = false;
  do {
    if (uVar6 == 0) {
      return;
    }
    puVar2 = ((undefined4 *)camry_host_ptr((uint32_t)((uint)uVar7 * 0xc + (*((volatile int32_t *)camry_host_ptr((uint32_t)((int)((ulonglong)uVar5 >> 0x20) + 0x29c)))))));
    if ((param_2 == puVar2[1]) && (param_3 == *(char *)(puVar2 + 2))) {
      bVar3 = true;
      (*((uint32_t *)(stack_record_34 + 0))) = 1;
      (*((uint32_t *)(stack_record_34 + 4))) = *puVar2;
      (*((uint32_t *)(stack_record_34 + 12))) = *param_5;
      (*((uint32_t *)(stack_record_34 + 16))) = param_5[1];
      (*((uint32_t *)(stack_record_34 + 8))) = param_4 & 0xff;
      invoke_descriptor_callback_and_return_zero_3460(*puVar1, camry_host_addr(stack_record_34));
    }
    else {
      bVar3 = false;
      if (bVar4) {
        return;
      }
    }
    uVar7 = uVar7 + 1;
    uVar6 = uVar6 - 1;
    bVar4 = bVar3;
  } while( true );
}

void dispatch_first_matching_transmit_route_event_46ee(uint param_1,uint param_2,int param_3,char param_4)

{
  uint8_t stack_record_c[12];
  undefined4 *puVar1;
  undefined4 *puVar2;
  ushort uVar3;
  uint uVar4;
  
  (*((uint32_t *)(stack_record_c + 0))) = param_1 & 0xff;
  puVar1 = ((undefined4 *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((camry_tp + 0x2a4u)))) + (param_2 & 0xffff) * 8)));
  uVar4 = (uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(puVar1) + 6))));
  uVar3 = *(ushort *)(puVar1 + 1);
  while( true ) {
    if (uVar4 == 0) {
      return;
    }
    puVar2 = ((undefined4 *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((camry_tp + 0x2a0u)))) + (uint)uVar3 * 0xc)));
    if ((param_3 == puVar2[1]) && (param_4 == *(char *)(puVar2 + 2))) break;
    uVar3 = uVar3 + 1;
    uVar4 = uVar4 - 1;
  }
  (*((uint32_t *)(stack_record_c + 4))) = *puVar2;
  invoke_descriptor_callback_and_return_zero_3460(*puVar1, camry_host_addr(stack_record_c));
  return;
}

void dispatch_transmit_route_event_zero_4744(undefined2 param_1,undefined4 param_2,undefined1 param_3)

{
  dispatch_first_matching_transmit_route_event_46ee(0,param_1,param_2,param_3);
  return;
}

void dispatch_transmit_route_event_two_475c(undefined2 param_1,undefined4 param_2,undefined1 param_3)

{
  dispatch_first_matching_transmit_route_event_46ee(2,param_1,param_2,param_3);
  return;
}

bool latch_initialization_once_and_set_state_two_4776(void)

{
  bool bVar1;
  
  bVar1 = (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff92a3u)))) != '\0';
  if (!bVar1) {
    (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff92a3u)))) = '\x01';
    (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff92a2u)))) = 2;
  }
  return bVar1;
}

undefined1 get_gp_state_byte_92a2_478e(void)

{
  return (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff92a2u))));
}

undefined1 get_gp_initialization_latch_byte_92a3_4794(void)

{
  return (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff92a3u))));
}

void clear_result_2aa2_if_flag_2aa3_set_479a(void)

{
  if ((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff92a3u)))) != '\0') {
    (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff92a2u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff92a3u)))) = '\0';
  }
  return;
}

void set_result_2aa2_two_and_clear_flag_2aa3_47ac(void)

{
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff92a2u)))) = 2;
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff92a3u)))) = 0;
  return;
}

uint boot_submit_region_crc_verification(uint address,uint length,uchar opaque_tag)

{
  bool bVar1;
  
  bVar1 = (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff92adu)))) != '\0';
  if (!bVar1) {
    (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff92adu)))) = '\x01';
    (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff92acu)))) = 2;
    (*((volatile uint32_t *)camry_host_ptr((camry_gp + 0xffff92a4u)))) = address;
    (*((volatile uint32_t *)camry_host_ptr((camry_gp + 0xffff92a8u)))) = length;
    (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff92aeu)))) = opaque_tag;
  }
  return (uint)bVar1;
}

uint boot_region_crc_result(void)

{
  return (uint)(*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff92acu))));
}

uint boot_region_crc_pending(void)

{
  return (uint)(*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff92adu))));
}

uint feed_dcra1_words_and_return_complement_47ea(int param_1,uint param_2,uint param_3)

{
  int iVar1;
  uint uVar2;
  
  camry_write8(0xffd51020u, '\0');
  uVar2 = 0;
  camry_write32(0xffd51004u, param_3);
  while (uVar2 < param_2 >> 2) {
    iVar1 = uVar2 * 4;
    uVar2 = uVar2 + 1;
    camry_write32(0xffd51000u, (*((uint *)camry_host_ptr((uint32_t)(iVar1 + param_1)))));
  }
  uVar2 = camry_read32(0xffd51004u);
  return ~uVar2;
}

uint boot_validate_crc_region(uint region)

{
  F33BootCrcDescriptor *pFVar1;
  F33BootCrcDescriptor *pFVar2;
  uint uVar3;
  int iVar4;
  uint uVar5;
  uint uVar6;
  
  if (region < 3) {
    pFVar2 = ((void *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x8e00u + (uint32_t)((short)region) * (uint32_t)sizeof(F33BootRegionDescriptor)) + (uint32_t)(0) * (uint32_t)sizeof(F33BootRegionDescriptor) + (uint32_t)offsetof(F33BootRegionDescriptor, crc_descriptors))))))));
  }
  else {
    pFVar2 = (F33BootCrcDescriptor *)0x0;
  }
  uVar3 = boot_crc_descriptor_count(region);
  if ((uVar3 == 0) || (camry_host_addr((pFVar2))== 0)) {
LAB_0000486c:
    uVar5 = 0xffffffff;
  }
  else {
    for (uVar6 = 0; uVar5 = 0, uVar6 < uVar3; uVar6 = uVar6 + 1) {
      pFVar1 = pFVar2 + uVar6;
      if (((pFVar1->base != *((uint32_t *)camry_host_ptr((uint32_t)(pFVar1->base_metadata)))) || (pFVar1->length != *((uint32_t *)camry_host_ptr((uint32_t)(pFVar1->length_metadata)))))
         || (iVar4 = feed_dcra1_words_and_return_complement_47ea(pFVar1->base,pFVar1->length,(int)0xffffffff), iVar4 != 0))
      goto LAB_0000486c;
    }
  }
  return uVar5;
}

void boot_advance_region_crc_verification(void)

{
  uint32_t puVar1;
  uint uVar2;
  undefined4 uVar3;
  uint local_c;
  
  puVar1 = (camry_gp + 0x0u);
  if (((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff92adu)))) == '\x01') &&
     (uVar2 = boot_select_region_for_range((*((volatile uint32_t *)camry_host_ptr((camry_gp + 0xffff92a4u)))),(*((volatile uint32_t *)camry_host_ptr((camry_gp + 0xffff92a8u)))),&local_c), uVar2 == 0)) {
    uVar2 = boot_validate_crc_region(local_c);
    uVar3 = raise_pmr_and_return_previous_mask_721e(0xffff);
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6d53))))) = 0;
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x6d58)))) = 0;
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x6d5c)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6d54))))) = uVar2 != 0;
    restore_pmr_preserving_interrupt_disable_state_7244(uVar3);
  }
  return;
}

void boot_reset_region_crc_verification(void)

{
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff92acu)))) = 2;
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff92adu)))) = 0;
  return;
}

void fill_buffer_with_register_samples_be16_48d2(undefined1 *param_1,uint param_2)

{
  undefined2 uVar1;
  uint uVar2;
  
  for (uVar2 = (param_2 & 0xff) >> 1; uVar2 != 0; uVar2 = uVar2 - 1) {
    uVar1 = read_ffe51010_word_1d24();
    *param_1 = (char)((ushort)uVar1 >> 8);
    param_1[1] = (char)uVar1;
    param_1 = param_1 + 2;
  }
  return;
}

void boot_write_data_negative_response_4900(uchar param_1)

{
  boot_negative_response('.',param_1);
  return;
}

void boot_write_data_positive_identifier_response_4914(void)

{
  ushort identifier;
  identifier = *(volatile uint16_t *)camry_host_ptr((uint32_t)((camry_tp + 0x87eu) + (int)(int16_t)(*(volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff92b0u))) * 12));
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff92d0u)))) = 0x6e;
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff92d2u)))) = (undefined1)identifier;
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff92d1u)))) = (undefined1)(identifier >> 8);
  boot_response_submit('\x01',((undefined *)camry_host_ptr((camry_gp + 0xffff92d0u))),3);
  return;
}

void boot_service_write_did(ushort request_length)

{
  uint8_t stack_record_1b[27];
  int iVar1;
  char cVar2;
  uint32_t puVar3;
  F33BootInterruptEntry *pFVar4;
  undefined4 uVar5;
  ushort uVar6;
  int iVar7;
  short sVar8;
  int iVar9;
  bool bVar10;
  
  puVar3 = (camry_gp + 0x0u);
  pFVar4 = ((volatile F33BootInterruptEntry *)camry_host_ptr((camry_tp + 0x0u)));
  boot_copy_request_bytes_and_clear_append_index_67b0(((uint8_t *)(stack_record_1b)),0x13);
  uVar6 = read_variable_width_big_endian_u32_52a6(((uint8_t *)((stack_record_1b + 1))),2);
  cVar2 = *(char *)&pFVar4[0x10b].handler;
  bVar10 = true;
  sVar8 = 0;
  iVar7 = 0;
  do {
    iVar9 = (short)iVar7 * 0xc;
    if ((uVar6 == (*((ushort *)camry_host_ptr((uint32_t)((int)camry_host_addr(pFVar4) + iVar9 + 0x87e))))) &&
       (((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(pFVar4) + iVar9 + 0x880)))) & 2) != 0)) {
      sVar8 = (*((short *)camry_host_ptr((uint32_t)((int)camry_host_addr(pFVar4) + iVar9 + 0x87c))));
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6d50))))) = (char)iVar7;
      bVar10 = false;
      break;
    }
    iVar1 = iVar7 + 1;
    iVar9 = iVar7 + -3;
    iVar7 = iVar1;
  } while (((iVar9 < 0) || (iVar1 < 0)));
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6cf2))))) != cVar2) {
    uVar5 = 0x7f;
    goto LAB_000049aa;
  }
  if (request_length < 4) {
LAB_000049c0:
    uVar5 = 0x13;
    goto LAB_000049aa;
  }
  if (bVar10) {
LAB_00004a0c:
    uVar5 = 0x31;
    goto LAB_000049aa;
  }
  if (request_length != (ushort)(sVar8 + 3U)) goto LAB_000049c0;
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6cf1))))) != '\x02') {
    uVar5 = 0x33;
    goto LAB_000049aa;
  }
  if (uVar6 < 0x201) goto LAB_00004a0c;
  if (uVar6 == 0x201) {
    bVar10 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6d4e))))) == '\x01';
LAB_00004a04:
    if (!bVar10) {
LAB_00004a06:
      uVar5 = 0x22;
LAB_000049aa:
      boot_write_data_negative_response_4900(uVar5);
      return;
    }
  }
  else {
    if (uVar6 < 0x203) {
      bVar10 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6d4e))))) == '\x02';
      goto LAB_00004a04;
    }
    if (uVar6 != 0x203) goto LAB_00004a0c;
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6d4e))))) != '\0') goto LAB_00004a06;
  }
  if (uVar6 < 0x201) {
LAB_00004a80:
    uVar5 = 0x31;
  }
  else {
    if (uVar6 == 0x201) {
      iVar7 = boot_submit_program_or_memory_write_when_idle_6d5e(((undefined4 *)camry_host_ptr((uint32_t)((int)camry_host_addr(pFVar4) + (short)(ushort)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6d50))))) * 0xc + 0x878))), camry_host_addr(((uint8_t *)((stack_record_1b + 3)))));
      if (iVar7 == 0) {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6d4e))))) = 2;
LAB_00004a7c:
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6d4f))))) = 1;
        return;
      }
    }
    else {
      if (0x202 < uVar6) {
        if (uVar6 == 0x203) {
          boot_write_data_positive_identifier_response_4914();
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6d4e))))) = 1;
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6d4f))))) = 0;
          return;
        }
        goto LAB_00004a80;
      }
      iVar7 = boot_submit_program_or_memory_write_when_idle_6d5e(((undefined4 *)camry_host_ptr((uint32_t)((int)camry_host_addr(pFVar4) + (short)(ushort)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6d50))))) * 0xc + 0x878))), camry_host_addr(((uint8_t *)((stack_record_1b + 3)))));
      if (iVar7 == 0) {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6cea))))) = 1;
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6d4e))))) = 0;
        goto LAB_00004a7c;
      }
    }
    uVar5 = 0x72;
  }
  boot_write_data_negative_response_4900(uVar5);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6d4f))))) = 0;
  return;
}

void clear_write_data_status_bytes_4a90(void)

{
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff92b2u)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff92b1u)))) = 0;
  return;
}

void boot_write_did_progress(void)

{
  uint32_t puVar1;
  undefined4 uVar2;
  int iVar3;
  
  puVar1 = (camry_gp + 0x0u);
  if ((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff92b1u)))) != '\x01') {
    return;
  }
  if ((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff93bcu)))) == '\x01') {
    return;
  }
  iVar3 = boot_get_combined_request_response_state_67f6();
  if (iVar3 == 6) {
    uVar2 = 0x10;
  }
  else {
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6c05))))) != '\0') {
      return;
    }
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6c06))))) == '\0') {
      boot_write_data_positive_identifier_response_4914();
      goto LAB_00004ada;
    }
    uVar2 = 0x72;
  }
  boot_write_data_negative_response_4900(uVar2);
LAB_00004ada:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6d4f))))) = 0;
  return;
}

undefined4 classify_transfer_block_sequence_and_record_counter_4ae2(void)

{
  uint32_t puVar1;
  undefined1 uVar2;
  undefined4 uVar3;
  
  puVar1 = (camry_gp + 0x0u);
  if ((*((char *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((camry_gp + 0xffff92b4u)))) + 1)))) == (char)((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff92c8u)))) + '\x01')) {
    (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff92c7u)))) = 0;
    uVar3 = 0;
  }
  else if (((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff92c9u)))) == '\x01') && ((*((char *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((camry_gp + 0xffff92b4u)))) + 1)))) == (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff92c8u)))))) {
    puVar1 = (camry_gp + 0x0u);
    uVar2 = saturating_increment_u8_7262((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff92c7u)))));
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6d39))))) = uVar2;
    uVar3 = 1;
  }
  else {
    (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff92c7u)))) = 0;
    uVar3 = 2;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6d37))))) = 1;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6d38))))) = (*((undefined1 *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)(puVar1 + -0x6d4c)))) + 1))));
  return uVar3;
}

void boot_transfer_data_negative_and_mark_download_failed_4b38(uchar param_1)

{
  uint32_t puVar1;
  puVar1 = (camry_gp + 0x0u);
  boot_negative_response('6',param_1);
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6ced))))) != '\0') {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6ced))))) = 0xf;
  }
  return;
}

void boot_transfer_data_positive_counter_response_4b5a(void)

{
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff92d0u)))) = 0x76;
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff92d1u)))) = (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff92c8u))));
  boot_response_submit('\x01',((undefined *)camry_host_ptr((camry_gp + 0xffff92d0u))),2);
  return;
}

void boot_admit_program_transfer_chunk(ushort request_length)

{
  uchar *source;
  uint32_t puVar1;
  F33BootInterruptEntry *pFVar2;
  uint length;
  undefined4 uVar3;
  int iVar4;
  ushort length_00;
  uint uVar5;
  uchar uStack_d;
  
  puVar1 = (camry_gp + 0x0u);
  pFVar2 = ((volatile F33BootInterruptEntry *)camry_host_ptr((camry_tp + 0x0u)));
  uVar3 = camry_host_addr(boot_get_request_buffer_and_clear_append_index_67d0());
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x6d4c)))) = uVar3;
  iVar4 = classify_transfer_block_sequence_and_record_counter_4ae2();
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6cf2))))) != (*((char *)((uint8_t *)&pFVar2[0x10b].handler + (3))))) {
    boot_request_flash_worker_cancel();
    uVar3 = 0x7f;
    goto LAB_00004ba8;
  }
  length_00 = request_length - 2;
  uVar5 = (uint)length_00;
  if (request_length < 3) goto LAB_00004c1a;
  length = (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x6d44))));
  if (length == 0) {
    boot_request_flash_worker_cancel();
    uVar3 = 0x24;
    goto LAB_00004ba8;
  }
  if (length < uVar5) {
    boot_request_flash_worker_cancel();
    uVar3 = 0x71;
    goto LAB_00004ba8;
  }
  if ((iVar4 == 2) || (iVar4 == 3)) {
    boot_request_flash_worker_cancel();
    uVar3 = 0x73;
    goto LAB_00004ba8;
  }
  if (iVar4 != 0) {
    boot_transfer_data_positive_counter_response_4b5a();
    return;
  }
  if (length == uVar5) {
    if (0x400 < uVar5) goto LAB_00004c0a;
    if (request_length < 0x403) goto LAB_00004c24;
  }
  else {
    if (uVar5 != 0x400) {
LAB_00004c0a:
      boot_request_flash_worker_cancel();
      uVar3 = 0x31;
      goto LAB_00004ba8;
    }
    if (request_length == 0x402) {
LAB_00004c24:
      boot_classify_service_range((*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x6d48)))),length,'\0',&uStack_d);
      (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x6d44)))) = (*((int *)camry_host_ptr((uint32_t)(puVar1 + -0x6d44)))) - uVar5;
      if (uStack_d == '\0') {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6d36))))) = 2;
        boot_set_flash_worker_pause('\0');
      }
      else {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6d36))))) = 1;
      }
      (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x6d3c)))) = length_00;
      source = ((uchar *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)(puVar1 + -0x6d4c)))) + 2)));
      (*((volatile uint32_t *)camry_host_ptr((uint32_t)((puVar1 + -0x6d40))))) = camry_host_addr(source);
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6ceb))))) != '\0') {
        uVar5 = boot_block_transform_submit(length_00,source,source);
        if (uVar5 != 0) {
          boot_transfer_data_negative_and_mark_download_failed_4b38(0x72);
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6d3a))))) = 0;
          return;
        }
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6d3a))))) = 1;
        return;
      }
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6d35))))) = 1;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6d3a))))) = 2;
      return;
    }
  }
LAB_00004c1a:
  boot_request_flash_worker_cancel();
  uVar3 = 0x13;
LAB_00004ba8:
  boot_transfer_data_negative_and_mark_download_failed_4b38(uVar3);
  return;
}

void boot_admit_compare_transfer_chunk(ushort request_length)

{
  uchar *left;
  undefined1 uVar1;
  uint uVar2;
  uint32_t puVar3;
  F33BootInterruptEntry *pFVar4;
  ushort length;
  uint uVar5;
  undefined4 uVar6;
  int iVar7;
  
  puVar3 = (camry_gp + 0x0u);
  pFVar4 = ((volatile F33BootInterruptEntry *)camry_host_ptr((camry_tp + 0x0u)));
  uVar6 = camry_host_addr(boot_get_request_buffer_and_clear_append_index_67d0());
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar3 + -0x6d4c)))) = uVar6;
  iVar7 = classify_transfer_block_sequence_and_record_counter_4ae2();
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6cf2))))) != (*((char *)((uint8_t *)&pFVar4[0x10b].handler + (3))))) {
    uVar6 = 0x7f;
    goto LAB_00004cca;
  }
  length = request_length - 2;
  uVar5 = (uint)length;
  if (request_length < 3) goto LAB_00004d2a;
  uVar2 = (*((uint *)camry_host_ptr((uint32_t)(puVar3 + -0x6d44))));
  if (uVar2 == 0) {
    uVar6 = 0x24;
    goto LAB_00004cca;
  }
  if (uVar2 < uVar5) {
    uVar6 = 0x71;
    goto LAB_00004cca;
  }
  if ((iVar7 == 2) || (iVar7 == 3)) {
    uVar6 = 0x73;
    goto LAB_00004cca;
  }
  if (iVar7 != 0) {
    boot_transfer_data_positive_counter_response_4b5a();
    return;
  }
  if (uVar2 == uVar5) {
    if (0x400 < uVar5) goto LAB_00004d1e;
    if (request_length < 0x403) goto LAB_00004d30;
  }
  else {
    if (uVar5 != 0x400) {
LAB_00004d1e:
      uVar6 = 0x31;
      goto LAB_00004cca;
    }
    if (request_length == 0x402) {
LAB_00004d30:
      (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x6d3c)))) = length;
      left = ((uchar *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)(puVar3 + -0x6d4c)))) + 2)));
      (*((volatile uint32_t *)camry_host_ptr((uint32_t)((puVar3 + -0x6d40))))) = camry_host_addr(left);
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6ceb))))) == '\0') {
        if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6ce9))))) != '\x01' && (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6ce9))))) != '\x02') {
          return;
        }
        uVar5 = boot_compare_submit(left,((uchar *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)((puVar3 + -0x6d48)))))))),uVar5);
        if (uVar5 != 0) goto LAB_00004d6e;
        uVar1 = 2;
      }
      else {
        uVar5 = boot_block_transform_submit(length,left,left);
        if (uVar5 != 0) {
LAB_00004d6e:
          boot_transfer_data_negative_and_mark_download_failed_4b38(0x72);
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6d3a))))) = 0;
          return;
        }
        uVar1 = 1;
      }
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6d3a))))) = uVar1;
      return;
    }
  }
LAB_00004d2a:
  uVar6 = 0x13;
LAB_00004cca:
  boot_transfer_data_negative_and_mark_download_failed_4b38(uVar6);
  return;
}

void boot_reject_transfer_state(ushort request_length)

{
  undefined4 uVar1;
  
  if ((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff930eu)))) == (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x8ef4u + (uint32_t)(7) * 1u))))) {
    uVar1 = 0x24;
    if (request_length < 3) {
      uVar1 = 0x13;
    }
  }
  else {
    uVar1 = 0x7f;
  }
  boot_transfer_data_negative_and_mark_download_failed_4b38(uVar1);
  return;
}

void boot_service_transfer_data(ushort request_length)

{
  uchar uVar1;
  
  uVar1 = '\x02';
  if (((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9313u)))) == '\x01') || (uVar1 = '\n', (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9313u)))) == '\t')) {
    (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9313u)))) = uVar1;
  }
  if ((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9313u)))) == '\x02') {
    boot_admit_program_transfer_chunk(request_length);
  }
  else if ((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9313u)))) == '\n') {
    boot_admit_compare_transfer_chunk(request_length);
  }
  else {
    boot_reject_transfer_state(request_length);
  }
  return;
}

void boot_advance_program_transfer_response_4df2(void)

{
  byte bVar1;
  undefined1 uVar2;
  uint32_t puVar3;
  undefined4 uVar4;
  int iVar5;
  uint uVar6;
  
  puVar3 = (camry_gp + 0x0u);
  if ((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9317u)))) != '\x01' && (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9317u)))) != '\x02') {
    return;
  }
  iVar5 = boot_get_combined_request_response_state_67f6();
  if (iVar5 == 6) {
    boot_request_flash_worker_cancel();
    uVar4 = 0x10;
LAB_00004e84:
    boot_transfer_data_negative_and_mark_download_failed_4b38(uVar4);
  }
  else {
    bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6d3a)))));
    if (bVar1 != 0) {
      if (bVar1 == 1) {
        if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6c22))))) != '\0') {
          return;
        }
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6d35))))) = 1;
        uVar2 = 2;
        goto LAB_00004e8a;
      }
      if (bVar1 < 3) {
        if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6d35))))) != '\0') {
          return;
        }
        if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6d36))))) == '\x02') {
          if ((*((int *)camry_host_ptr((uint32_t)(puVar3 + -0x6d44)))) == 0) {
            if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-27999))))) != '\0') {
              return;
            }
            if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-28000))))) != '\0') {
LAB_00004e5c:
              uVar4 = 0x72;
              goto LAB_00004e84;
            }
          }
          else {
            if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-27999))))) == '\0') goto LAB_00004e5c;
            uVar6 = boot_program_input_has_insufficient_space(0x400);
            if (uVar6 != 0) {
              return;
            }
            boot_set_flash_worker_pause('\x01');
          }
        }
        uVar2 = 3;
        goto LAB_00004e8a;
      }
      if (bVar1 == 3) {
        boot_transfer_data_positive_counter_response_4b5a();
      }
    }
  }
  uVar2 = 0;
LAB_00004e8a:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6d3a))))) = uVar2;
  return;
}

void boot_advance_compare_transfer_response_4e92(void)

{
  byte bVar1;
  undefined1 uVar2;
  uint32_t puVar3;
  undefined4 uVar4;
  int iVar5;
  uint uVar6;
  
  puVar3 = (camry_gp + 0x0u);
  if ((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9317u)))) != '\x01' && (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9317u)))) != '\x02') {
    return;
  }
  iVar5 = boot_get_combined_request_response_state_67f6();
  if (iVar5 == 6) {
LAB_00004f0a:
    uVar4 = 0x10;
LAB_00004f0e:
    boot_transfer_data_negative_and_mark_download_failed_4b38(uVar4);
  }
  else {
    bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6d3a)))));
    if (bVar1 != 0) {
      if (bVar1 == 1) {
        if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6c22))))) != '\0') {
          return;
        }
        uVar6 = boot_compare_submit
                          (((uchar *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)((puVar3 + -0x6d40)))))))),((uchar *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)((puVar3 + -0x6d48)))))))),
                           (uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x6d3c)))));
        if (uVar6 == 0) {
          uVar2 = 2;
          goto LAB_00004f14;
        }
        uVar4 = 0x72;
        goto LAB_00004f0e;
      }
      if (bVar1 < 3) {
        if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6c13))))) != '\0') {
          return;
        }
        (*((uint *)camry_host_ptr((uint32_t)(puVar3 + -0x6d44)))) =
             (*((int *)camry_host_ptr((uint32_t)(puVar3 + -0x6d44)))) - (uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x6d3c))));
        (*((uint *)camry_host_ptr((uint32_t)(puVar3 + -0x6d48)))) =
             (*((int *)camry_host_ptr((uint32_t)(puVar3 + -0x6d48)))) + (uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x6d3c))));
        if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6c14))))) == '\0') {
          uVar2 = 3;
          goto LAB_00004f14;
        }
        goto LAB_00004f0a;
      }
      if (bVar1 == 3) {
        boot_transfer_data_positive_counter_response_4b5a();
      }
    }
  }
  uVar2 = 0;
LAB_00004f14:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6d3a))))) = uVar2;
  return;
}

void boot_transfer_timer_progress(void)

{
  if (((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff92c6u)))) != '\0') && ((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff93bcu)))) != '\x01')) {
    if ((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9313u)))) == '\x02') {
      boot_advance_program_transfer_response_4df2();
    }
    else if ((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9313u)))) == '\n') {
      boot_advance_compare_transfer_response_4e92();
    }
    else {
      (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff92c6u)))) = '\0';
    }
  }
  return;
}

void boot_transfer_foreground_consume(void)

{
  uint32_t puVar1;
  uint uVar2;
  
  puVar1 = (camry_gp + 0x0u);
  if (((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9317u)))) == '\x01' || (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9317u)))) == '\x02') &&
     ((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff92cbu)))) == '\x01')) {
    uVar2 = (uint)(*((volatile uint16_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff92c4u)))));
    if ((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff92cau)))) == '\x02') {
      boot_append_program_input(((uchar *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff92c0u)))))))), (*((volatile uint16_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff92c4u))))));
    }
    else {
      copy_positive_count_bytes_forward_153a(((undefined1 *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff92c0u)))))))), ((undefined1 *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((camry_gp + 0xffff92b8u))))))), uVar2);
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6d35))))) = 0;
    (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x6d48)))) = (*((int *)camry_host_ptr((uint32_t)(puVar1 + -0x6d48)))) + uVar2;
  }
  return;
}

undefined4 get_transfer_remaining_u32_4f98(void)

{
  return (*((volatile uint32_t *)camry_host_ptr((camry_gp + 0xffff92bcu))));
}

void fill_constant_block_4f9e(void)

{
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff92c6u)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff92c7u)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff92c8u)))) = 0;
  (*((volatile uint32_t *)camry_host_ptr((camry_gp + 0xffff92b8u)))) = (*((volatile uint32_t *)camry_host_ptr((camry_gp + 0xffff9300u))));
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff92c9u)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff92cbu)))) = 0;
  (*((volatile uint32_t *)camry_host_ptr((camry_gp + 0xffff92bcu)))) = (*((volatile uint32_t *)camry_host_ptr((camry_gp + 0xffff9304u))));
  return;
}

void boot_tester_present_negative_response_4fba(uchar param_1)

{
  boot_negative_response('>',param_1);
  return;
}

void boot_tester_present_positive_response_4fce(void)

{
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff92d0u)))) = 0x7e;
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff92d1u)))) = (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff92ccu)))) & 0x7f;
  boot_response_submit((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff92ccu)))) >> 7 ^ 1,((undefined *)camry_host_ptr((camry_gp + 0xffff92d0u))),2);
  return;
}

void boot_service_tester_present(ushort request_length)

{
  uint8_t stack_record_e[14];
  int iVar1;
  int iVar2;
  uint32_t puVar3;
  F33BootInterruptEntry *pFVar4;
  undefined4 uVar5;
  int iVar6;
  
  puVar3 = (camry_gp + 0x0u);
  pFVar4 = ((volatile F33BootInterruptEntry *)camry_host_ptr((camry_tp + 0x0u)));
  stack_record_e[0] = 0;
  stack_record_e[1] = '\0';
  boot_copy_request_bytes_and_clear_append_index_67b0(((uint8_t *)(stack_record_e)),2);
  iVar6 = 0;
  do {
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6cf2))))) == (*((char *)((uint8_t *)&pFVar4[0x10c].eiic + (iVar6 + 1))))) {
      if (1 < request_length) {
        if ((stack_record_e[1] != '\0') && (((int8_t)stack_record_e[1]) != -0x80)) {
          uVar5 = 0x12;
          goto LAB_0000502c;
        }
        if (request_length == 2) {
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6d34))))) = stack_record_e[1];
          boot_tester_present_positive_response_4fce();
          return;
        }
      }
      uVar5 = 0x13;
      goto LAB_0000502c;
    }
    iVar2 = iVar6 + 1;
    iVar1 = iVar6 + -2;
    iVar6 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  uVar5 = 0x7f;
LAB_0000502c:
  boot_tester_present_negative_response_4fba(uVar5);
  return;
}
