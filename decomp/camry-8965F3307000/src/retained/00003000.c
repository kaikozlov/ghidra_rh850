#include "common.h"

void handle_transport_primary_timeout_3000(void)

{
  char cVar1;
  byte bVar2;
  uint32_t puVar3;
  uchar uVar4;
  ushort uVar5;
  
  bVar2 = (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9132u))));
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9131u))));
  puVar3 = (camry_gp + 0x0u);
  uVar5 = (ushort)(*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9132u))));
  if ((((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9131u)))) == 'J') || ((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9131u)))) == 'L')) || ((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9131u)))) == 'I')) {
    cancel_mapped_transmit_and_return_zero_1ede((*((volatile uint16_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6f2u) + (uint32_t)((uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6bcu) + (uint32_t)((short)uVar5 * 0x18) * 1u)))) * 8) * 2u)))));
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6ecf))))) = 0;
    if (cVar1 == 'J') {
      return;
    }
    uVar5 = (*((ushort *)camry_host_ptr((uint32_t)(&(*((volatile uint32_t *)camry_host_ptr((camry_tp + 0x6cau)))) + (short)uVar5 * 6))));
    uVar4 = '\x02';
  }
  else {
    if (((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9131u)))) == 'Q') || ((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9131u)))) == 'T')) {
      send_transport_flow_control_wait_with_limit_24d0((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9132u)))));
      return;
    }
    if ((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9131u)))) != 'a') {
      if (((((int8_t)(*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9131u))))) == -0x76) || (((int8_t)(*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9131u))))) == -0x77)) || (((int8_t)(*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9131u))))) == -0x74)) {
        cancel_mapped_transmit_and_return_zero_1ede((*((volatile uint16_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6f2u))))));
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6ecf))))) = 0;
        uVar4 = '\x02';
      }
      else if (((int8_t)(*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9131u))))) == -0x6f || ((int8_t)(*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9131u))))) == -0x6e) {
        (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9131u)))) = '\0';
        uVar4 = '\x03';
      }
      else {
        if (((((int8_t)(*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9131u))))) != -0x5f) && (((int8_t)(*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9131u))))) != -0x5e)) && (((int8_t)(*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9131u))))) != -0x5c)) {
          return;
        }
        (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9131u)))) = '\0';
        uVar4 = '\x01';
      }
      boot_transport_response_complete((ushort)bVar2,uVar4);
      return;
    }
    uVar4 = '\x04';
    (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9131u)))) = '\0';
    uVar5 = (*((ushort *)camry_host_ptr((uint32_t)(&(*((volatile uint32_t *)camry_host_ptr((camry_tp + 0x6cau)))) + (short)uVar5 * 6))));
  }
  boot_transport_receive_complete(uVar5,uVar4);
  return;
}

void dispatch_current_generation_transport_timer_30d2(char param_1,uint param_2)

{
  int iVar1;
  
  if ((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9130u)))) != '\0') {
    iVar1 = ((int)(param_2 & 0xffff) >> 8) * 2;
    if ((param_1 == (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6b1u) + (uint32_t)(iVar1) * 1u))))) &&
       ((param_2 & 0xff) == (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebf292fu + (uint32_t)(iVar1) * 1u)))))) {
      dispatch_transport_secondary_timer_event_2fb8(param_2 & 0xffff);
    }
    else if ((param_1 == (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6b0u) + (uint32_t)(iVar1) * 1u))))) &&
            ((param_2 & 0xff) == (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff912eu) + (uint32_t)(iVar1) * 1u)))))) {
      handle_transport_primary_timeout_3000();
    }
  }
  return;
}

undefined4 cancel_active_response_channel_zero_3124(short param_1)

{
  byte bVar1;
  uint32_t puVar2;
  F33BootInterruptEntry *pFVar3;
  undefined4 uVar4;
  
  bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6e7u)))));
  puVar2 = (camry_gp + 0x0u);
  pFVar3 = ((volatile F33BootInterruptEntry *)camry_host_ptr((camry_tp + 0x0u)));
  uVar4 = 1;
  if (((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9130u)))) != '\0') && (param_1 == 0)) {
    if ((((int8_t)(*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9131u))))) == -0x77 || ((int8_t)(*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9131u))))) == -0x76) || (((int8_t)(*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9131u))))) == -0x74)) {
      cancel_mapped_transmit_and_return_zero_1ede((*((volatile uint16_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6f2u))))));
    }
    else if (((((int8_t)(*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9131u))))) != -0x6f && ((int8_t)(*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9131u))))) != -0x6e) &&
             (((int8_t)(*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9131u))))) != -0x5f && ((int8_t)(*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9131u))))) != -0x5e)) && (((int8_t)(*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9131u))))) != -0x5c)) {
      return 1;
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6ecf))))) = 0;
    disarm_indexed_timer_slot_1d70((*((undefined1 *)((uint8_t *)&pFVar3[0xd6].eiic + ((uint)bVar1 * 2)))));
    disarm_indexed_timer_slot_1d70((*((undefined1 *)((uint8_t *)&pFVar3[0xd6].eiic + ((uint)bVar1 * 2 + 1)))));
    boot_transport_response_complete(0,'\x01');
    uVar4 = 0;
  }
  return uVar4;
}

undefined4 cancel_receive_by_configured_channel_318c(ushort param_1)

{
  byte bVar1;
  uint uVar2;
  uint32_t puVar3;
  F33BootInterruptEntry *pFVar4;
  
  puVar3 = (camry_gp + 0x0u);
  pFVar4 = ((volatile F33BootInterruptEntry *)camry_host_ptr((camry_tp + 0x0u)));
  uVar2 = 0;
  if ((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9130u)))) != '\0') {
    do {
      if ((*((ushort *)camry_host_ptr((uint32_t)((camry_tp + 0x6cau) + (uint32_t)((short)uVar2 * 6) * 4u)))) == param_1) {
        bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6bau) + (uint32_t)((short)uVar2 * 0x18) * 1u))));
        if (((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9131u)))) == 'I' || (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9131u)))) == 'J') || ((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9131u)))) == 'L')) {
          cancel_mapped_transmit_and_return_zero_1ede((*((volatile uint16_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6f2u))))));
        }
        else if ((((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9131u)))) != 'Q' && (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9131u)))) != 'R') && ((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9131u)))) != 'T')) &&
                ((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9131u)))) != 'a')) {
          return 1;
        }
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6ecf))))) = 0;
        disarm_indexed_timer_slot_1d70((*((undefined1 *)((uint8_t *)&pFVar4[0xd6].eiic + ((uint)bVar1 * 2)))));
        disarm_indexed_timer_slot_1d70((*((undefined1 *)((uint8_t *)&pFVar4[0xd6].eiic + ((uint)bVar1 * 2 + 1)))));
        boot_transport_receive_complete(param_1,'\x01');
        return 0;
      }
      uVar2 = uVar2 + 1;
    } while (uVar2 < 2);
  }
  return 1;
}

void dispatch_matching_timer_event_with_zero_delay_retry_3256(char *param_1)

{
  char cVar1;
  uint uVar2;
  int iVar3;
  
  cVar1 = *param_1;
  uVar2 = 0;
  do {
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6f4u) + (uint32_t)(uVar2 * 8) * 1u)))) == cVar1) {
      iVar3 = invoke_descriptor_callback_and_return_zero_3460((uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6f5u) + (uint32_t)(uVar2 * 8) * 1u)))) * 8 + (camry_tp + 0x40u), camry_host_addr(param_1));
      if (iVar3 == 0) {
        return;
      }
      arm_timer_slot_from_tick_with_callback_data_1d2c(cVar1,0,*(undefined2 *)(param_1 + 4),0);
      return;
    }
    uVar2 = uVar2 + 1;
  } while (uVar2 < 2);
  return;
}

void call_matching_timer_callback_32a0(char *param_1)

{
  uint uVar1;
  
  uVar1 = 0;
  do {
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6f4u) + (uint32_t)(uVar1 * 8) * 1u)))) == *param_1) {
      (*(int (*)())camry_indirect((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6f8u) + (uint32_t)(uVar1 * 2) * 4u))))))(*param_1,*(undefined2 *)(param_1 + 4));
      return;
    }
    uVar1 = uVar1 + 1;
  } while (uVar1 < 2);
  return;
}

uint boot_classify_service_range(uint start,uint length,uchar kind,uchar *storage_class)

{
  uint uVar1;
  uint uVar2;
  
  if ((length != 0) && (uVar2 = (length + start) - 1, start <= uVar2)) {
    uVar1 = 0;
    do {
      if (((((*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)((camry_tp + 0x704u) + (uint32_t)(uVar1) * (uint32_t)sizeof(F33BootRangePolicyEntry)) + (uint32_t)(0) * (uint32_t)sizeof(F33BootRangePolicyEntry) + (uint32_t)offsetof(F33BootRangePolicyEntry, kind_mask))))) & 1 << (kind & 0x1f)) != 0) &&
          ((*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)((camry_tp + 0x704u) + (uint32_t)(uVar1) * (uint32_t)sizeof(F33BootRangePolicyEntry)) + (uint32_t)(0) * (uint32_t)sizeof(F33BootRangePolicyEntry) + (uint32_t)offsetof(F33BootRangePolicyEntry, lower))))) <= start)) &&
         (uVar2 <= (*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)((camry_tp + 0x704u) + (uint32_t)(uVar1) * (uint32_t)sizeof(F33BootRangePolicyEntry)) + (uint32_t)(0) * (uint32_t)sizeof(F33BootRangePolicyEntry) + (uint32_t)offsetof(F33BootRangePolicyEntry, upper))))))) {
        *storage_class = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)((camry_tp + 0x704u) + (uint32_t)(uVar1) * (uint32_t)sizeof(F33BootRangePolicyEntry)) + (uint32_t)(0) * (uint32_t)sizeof(F33BootRangePolicyEntry) + (uint32_t)offsetof(F33BootRangePolicyEntry, storage_class)))));
        return 0;
      }
      uVar1 = uVar1 + 1;
    } while (uVar1 < 3);
  }
  return 1;
}

uint boot_service_range_completion_selector
               (uint start,uint length,uchar kind,uchar *completion_selector)

{
  uint uVar1;
  uint uVar2;
  
  if ((length != 0) && (uVar2 = (length + start) - 1, start <= uVar2)) {
    uVar1 = 0;
    do {
      if (((((*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)((camry_tp + 0x704u) + (uint32_t)(uVar1) * (uint32_t)sizeof(F33BootRangePolicyEntry)) + (uint32_t)(0) * (uint32_t)sizeof(F33BootRangePolicyEntry) + (uint32_t)offsetof(F33BootRangePolicyEntry, kind_mask))))) & 1 << (kind & 0x1f)) != 0) &&
          ((*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)((camry_tp + 0x704u) + (uint32_t)(uVar1) * (uint32_t)sizeof(F33BootRangePolicyEntry)) + (uint32_t)(0) * (uint32_t)sizeof(F33BootRangePolicyEntry) + (uint32_t)offsetof(F33BootRangePolicyEntry, lower))))) <= start)) &&
         (uVar2 <= (*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)((camry_tp + 0x704u) + (uint32_t)(uVar1) * (uint32_t)sizeof(F33BootRangePolicyEntry)) + (uint32_t)(0) * (uint32_t)sizeof(F33BootRangePolicyEntry) + (uint32_t)offsetof(F33BootRangePolicyEntry, upper))))))) {
        *completion_selector = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)((camry_tp + 0x704u) + (uint32_t)(uVar1) * (uint32_t)sizeof(F33BootRangePolicyEntry)) + (uint32_t)(0) * (uint32_t)sizeof(F33BootRangePolicyEntry) + (uint32_t)offsetof(F33BootRangePolicyEntry, completion_selector)))));
        return 0;
      }
      uVar1 = uVar1 + 1;
    } while (uVar1 < 3);
  }
  return 1;
}

uint boot_select_region_for_range(uint address,uint length,uint *region)

{
  uint uVar1;
  
  if (length != 0) {
    uVar1 = 0;
    do {
      if (((*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)((camry_tp + 0x764u) + (uint32_t)((short)uVar1) * (uint32_t)sizeof(F33BootRegionDescriptor)) + (uint32_t)(0) * (uint32_t)sizeof(F33BootRegionDescriptor) + (uint32_t)offsetof(F33BootRegionDescriptor, lower))))) <= address) &&
         ((length + address) - 1 <= (*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)((camry_tp + 0x764u) + (uint32_t)((short)uVar1) * (uint32_t)sizeof(F33BootRegionDescriptor)) + (uint32_t)(0) * (uint32_t)sizeof(F33BootRegionDescriptor) + (uint32_t)offsetof(F33BootRegionDescriptor, upper))))))) {
        *region = uVar1;
        return 0;
      }
      uVar1 = uVar1 + 1;
    } while (uVar1 < 3);
  }
  return 1;
}

uint boot_lookup_authentication_trailer(uint start,uint length,uint *trailer_address)

{
  short sVar1;
  uint uVar2;
  
  if (length != 0) {
    uVar2 = 0;
    do {
      sVar1 = (short)uVar2;
      if ((((*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)((camry_tp + 0x764u) + (uint32_t)(sVar1) * (uint32_t)sizeof(F33BootRegionDescriptor)) + (uint32_t)(0) * (uint32_t)sizeof(F33BootRegionDescriptor) + (uint32_t)offsetof(F33BootRegionDescriptor, lower))))) <= start) &&
          ((length + start) - 1 <= (*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)((camry_tp + 0x764u) + (uint32_t)(sVar1) * (uint32_t)sizeof(F33BootRegionDescriptor)) + (uint32_t)(0) * (uint32_t)sizeof(F33BootRegionDescriptor) + (uint32_t)offsetof(F33BootRegionDescriptor, upper))))))) &&
         ((*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)((camry_tp + 0x764u) + (uint32_t)(sVar1) * (uint32_t)sizeof(F33BootRegionDescriptor)) + (uint32_t)(0) * (uint32_t)sizeof(F33BootRegionDescriptor) + (uint32_t)offsetof(F33BootRegionDescriptor, authentication_trailer))))) != 0)) {
        *trailer_address = (*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)((camry_tp + 0x764u) + (uint32_t)(sVar1) * (uint32_t)sizeof(F33BootRegionDescriptor)) + (uint32_t)(0) * (uint32_t)sizeof(F33BootRegionDescriptor) + (uint32_t)offsetof(F33BootRegionDescriptor, authentication_trailer)))));
        return 0;
      }
      uVar2 = uVar2 + 1;
    } while (uVar2 < 3);
  }
  return 1;
}

uint boot_lookup_completion_marker(uint start,uint length,uint *marker_address)

{
  short sVar1;
  uint uVar2;
  
  if (length != 0) {
    uVar2 = 0;
    do {
      sVar1 = (short)uVar2;
      if (((*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)((camry_tp + 0x764u) + (uint32_t)(sVar1) * (uint32_t)sizeof(F33BootRegionDescriptor)) + (uint32_t)(0) * (uint32_t)sizeof(F33BootRegionDescriptor) + (uint32_t)offsetof(F33BootRegionDescriptor, lower))))) <= start) &&
         ((length + start) - 1 <= (*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)((camry_tp + 0x764u) + (uint32_t)(sVar1) * (uint32_t)sizeof(F33BootRegionDescriptor)) + (uint32_t)(0) * (uint32_t)sizeof(F33BootRegionDescriptor) + (uint32_t)offsetof(F33BootRegionDescriptor, upper))))))) {
        *marker_address = (*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)((camry_tp + 0x764u) + (uint32_t)(sVar1) * (uint32_t)sizeof(F33BootRegionDescriptor)) + (uint32_t)(0) * (uint32_t)sizeof(F33BootRegionDescriptor) + (uint32_t)offsetof(F33BootRegionDescriptor, marker_block)))));
        return 0;
      }
      uVar2 = uVar2 + 1;
    } while (uVar2 < 3);
  }
  return 1;
}

uint boot_select_counter_block_for_range(uint address,uint length,uint *counter_block)

{
  short sVar1;
  uint uVar2;
  
  if (length != 0) {
    uVar2 = 0;
    do {
      sVar1 = (short)uVar2;
      if (((*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)((camry_tp + 0x764u) + (uint32_t)(sVar1) * (uint32_t)sizeof(F33BootRegionDescriptor)) + (uint32_t)(0) * (uint32_t)sizeof(F33BootRegionDescriptor) + (uint32_t)offsetof(F33BootRegionDescriptor, lower))))) <= address) &&
         ((length + address) - 1 <= (*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)((camry_tp + 0x764u) + (uint32_t)(sVar1) * (uint32_t)sizeof(F33BootRegionDescriptor)) + (uint32_t)(0) * (uint32_t)sizeof(F33BootRegionDescriptor) + (uint32_t)offsetof(F33BootRegionDescriptor, upper))))))) {
        *counter_block = (*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)((camry_tp + 0x764u) + (uint32_t)(sVar1) * (uint32_t)sizeof(F33BootRegionDescriptor)) + (uint32_t)(0) * (uint32_t)sizeof(F33BootRegionDescriptor) + (uint32_t)offsetof(F33BootRegionDescriptor, counter_block)))));
        return 0;
      }
      uVar2 = uVar2 + 1;
    } while (uVar2 < 3);
  }
  return 1;
}

uint boot_crc_descriptor_count(uint region)

{
  if (region < 3) {
    return (*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x8e00u + (uint32_t)((short)region) * (uint32_t)sizeof(F33BootRegionDescriptor)) + (uint32_t)(0) * (uint32_t)sizeof(F33BootRegionDescriptor) + (uint32_t)offsetof(F33BootRegionDescriptor, crc_count)))));
  }
  return 0;
}

F33BootCrcDescriptor * boot_crc_descriptors(uint region)

{
  if (region < 3) {
    return ((void *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x8e00u + (uint32_t)((short)region) * (uint32_t)sizeof(F33BootRegionDescriptor)) + (uint32_t)(0) * (uint32_t)sizeof(F33BootRegionDescriptor) + (uint32_t)offsetof(F33BootRegionDescriptor, crc_descriptors))))))));
  }
  return (F33BootCrcDescriptor *)0x0;
}

undefined4 invoke_descriptor_callback_and_return_zero_3460(int param_1,undefined4 param_2)

{
  (*(int (*)())camry_indirect((uint32_t)(*((code * *)camry_host_ptr((uint32_t)(param_1 + 4))))))(param_2, param_2);
  return 0;
}

uint boot_get_flash_block_skip_flag(uint address)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = 0;
  while ((address < (*((volatile uint32_t *)camry_host_ptr((uint32_t)((camry_tp + 0x50u) + (uint32_t)(iVar3) * 4u)))) ||
         ((*((volatile uint32_t *)camry_host_ptr((uint32_t)((camry_tp + 0x50u) + (uint32_t)(iVar3 + 1) * 4u)))) <= address))) {
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -0x25;
    iVar3 = iVar2;
    if (iVar1 < 0 == (iVar2 < 0 && -1 < iVar1)) {
      return 0;
    }
  }
  return (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff9154u) + (uint32_t)(iVar3) * 1u))));
}

void boot_clear_flash_block_skip_flags(uint first_block,uint last_block)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint32_t puVar4;
  F33BootInterruptEntry *pFVar5;
  undefined4 uVar6;
  uint pFVar7;
  
  puVar4 = (camry_gp + 0x0u);
  pFVar5 = ((volatile F33BootInterruptEntry *)camry_host_ptr((camry_tp + 0x0u)));
  if (first_block <= last_block) {
    uVar6 = raise_pmr_and_return_previous_mask_721e(0xffff);
    iVar3 = 0;
    do {
      if ((((uint )(&pFVar5[10].eiic)[iVar3] <= first_block) &&
          (pFVar7 = (uint )(&pFVar5[10].eiic + iVar3)[1], first_block < pFVar7)
          ) && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(iVar3 + -0x6eac))))) = 0, first_block = (uint)pFVar7, last_block < pFVar7))
      break;
      iVar2 = iVar3 + 1;
      iVar1 = iVar3 + -0x25;
      iVar3 = iVar2;
    } while (((iVar1 < 0) || (iVar2 < 0)));
    restore_pmr_preserving_interrupt_disable_state_7244(uVar6);
  }
  return;
}

uint boot_check_relocated_blank_words(uint address,uint word_count)

{
  uint uVar1;
  
  uVar1 = (*(int (*)())camry_indirect((uint32_t)((*((volatile int32_t *)camry_host_ptr((camry_tp + 0x48u)))))))(address, word_count);
  return uVar1;
}

uint boot_check_rounded_program_span_blank(uint address,uint length)

{
  uint uVar1;
  
  uVar1 = boot_check_relocated_blank_words(address,(length - 1 & 0xffffff00) + 0x100 >> 2);
  return (uint)(uVar1 != 0);
}

void repeat_8800_record_until_ffa10000_bit7_3584(void)

{
  uint8_t stack_record_c[12];
  camry_fill_bytes(stack_record_c, sizeof stack_record_c);
  byte bVar1;
  
  while (bVar1 = camry_read8(0xffa10000u), (bVar1 & 0x80) == 0) {
    (*((uint16_t *)(stack_record_c + 0))) = 0x8800;
    (*((uint16_t *)(stack_record_c + 2))) = 0;
    (*((uint16_t *)(stack_record_c + 4))) = 0xf000;
    (*((uint16_t *)(stack_record_c + 6))) = 0x1f00;
    insert_seven_byte_check_and_submit_halfwords_167c(camry_host_addr(((uint16_t *)(stack_record_c))));
    busy_wait_155_decrements_per_unit_7208(0x50);
  }
  return;
}

void clear_driver_state_and_wait_for_ffa10000_ready_35bc(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = 0;
  do {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff9154u) + (uint32_t)(iVar3) * 1u)))) = 0;
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -0x25;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff917au))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff917bu))))) = 1;
  repeat_8800_record_until_ffa10000_bit7_3584();
  return;
}

void boot_copy_flash_driver_to_ram(void)

{
  int iVar1;
  undefined4 uVar2;
  uint8_t *puVar3;
  code *pcVar4;
  
  puVar3 = ((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebf0c88u + (uint32_t)(0x378) * 1u)));
  pcVar4 = ((void *)camry_host_ptr((uint32_t)(0x8370u)));
  iVar1 = 0xcb;
  do {
    uVar2 = *(undefined4 *)pcVar4;
    pcVar4 = pcVar4 + 4;
    *(undefined4 *)puVar3 = uVar2;
    puVar3 = puVar3 + 4;
    iVar1 = iVar1 + -1;
  } while (iVar1 != 0);
  __synchronize();
  __synchronize();
  return;
}

void boot_cache_set_enabled(uchar enabled)

{
  uint uVar1;
  undefined4 uVar2;
  
  uVar1 = CDBCR;
  if (enabled == '\0') {
    CDBCR = uVar1 & 0xfffffffc;
    uVar1 = camry_sample_icctrl();
    ICCTRL = uVar1 & 0xfffffffe;
    uVar1 = CDBCR;
    CDBCR = uVar1 & 0xfffffffd | 2;
    uVar2 = CDBCR;
    uVar1 = camry_sample_icctrl();
    ICCTRL = uVar1 | 0x100;
    do {
      uVar1 = camry_sample_icctrl();
    } while ((uVar1 >> 8 & 1) != 0);
  }
  else {
    CDBCR = uVar1 & 0xfffffffd | 2;
    uVar2 = CDBCR;
    uVar1 = camry_sample_icctrl();
    ICCTRL = uVar1 | 0x100;
    do {
      uVar1 = camry_sample_icctrl();
    } while ((uVar1 >> 8 & 1) != 0);
    uVar1 = CDBCR;
    CDBCR = uVar1 & 0xfffffffd | 1;
    uVar1 = camry_sample_icctrl();
    ICCTRL = uVar1 | 1;
  }
  uVar2 = camry_sample_icctrl();
  __synchronize();
  return;
}

void wait_ffa10080_bit15_and_write_halfword_constants_369c(void)

{
  uint uVar1;
  ushort uVar2;
  
  do {
    uVar1 = camry_read32(0xffa10080u);
  } while ((uVar1 >> 0xf & 1) == 0);
  camry_write16(0xffa100e4u, 0x1e28);
  camry_write16(0xffa10104u, 0xa630);
  uVar2 = camry_read16(0xffa10104u);
  __synchronize();
  return;
}

void copy_flash_driver_disable_cache_and_call_ram_entry_36be(void)

{
  boot_copy_flash_driver_to_ram();
  boot_cache_set_enabled('\0');
  wait_ffa10080_bit15_and_write_halfword_constants_369c();
  boot_relocated_8628();
  return;
}

undefined4 load_tx_buffer_and_set_request_if_idle_36de(int param_1,int param_2,int param_3,char param_4,byte param_5,uint *param_6)

{
  uint uVar1;
  undefined4 uVar2;
  
  uVar2 = 1;
  uVar1 = (param_1 * 0x10 + param_2) - 3U & 0xff;
  if ((((*((byte *)camry_host_ptr((uint32_t)((int)(0xffd202d0u) + uVar1)))) >> 3 & 1) == 0) &&
     (((*((byte *)camry_host_ptr((uint32_t)((int)(0xffd202d0u) + uVar1)))) & 6) == 0)) {
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xffd24000u + (uint32_t)(uVar1) * 32u)))) = param_3 + (uint)(param_4 != '\0') * -0x80000000;
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xffd24000u + (uint32_t)(uVar1) * 32u + 4u)))) = (uint)param_5 << 0x1c;
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xffd24000u + (uint32_t)(uVar1) * 32u + 12u)))) = *param_6;
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xffd24000u + (uint32_t)(uVar1) * 32u + 16u)))) = param_6[1];
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xffd24000u + (uint32_t)(uVar1) * 32u + 8u)))) = 0;
    set_indexed_byte_bit_1d0e(((byte *)camry_host_ptr((uint32_t)((int)(0xffd20250u) + uVar1))), 0);
    uVar2 = 0;
  }
  return uVar2;
}

undefined4 guarded_submit_tx_buffer_from_descriptor_374e(uint param_1,undefined4 *param_2)

{
  uint uVar1;
  uint32_t puVar2;
  uint uVar3;
  undefined4 uVar4;
  int iVar5;
  undefined4 uVar6;
  undefined1 auStack_1c [8];
  camry_fill_bytes(auStack_1c, sizeof auStack_1c);
  
  puVar2 = (camry_gp + 0x0u);
  uVar6 = 2;
  uVar4 = raise_pmr_and_return_previous_mask_721e(0xffff);
  uVar3 = (param_1 & 0x7f) >> 4;
  uVar1 = 0;
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(uVar3 - 0x6e83))))) == '\0') {
    for (; uVar1 < (*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 9)))); uVar1 = uVar1 + 1 & 0xff) {
      auStack_1c[uVar1] = (*((undefined1 *)camry_host_ptr((uint32_t)(param_2[1] + uVar1))));
    }
    iVar5 = load_tx_buffer_and_set_request_if_idle_36de(uVar3,param_1 & 0xf,*param_2,*(undefined1 *)(param_2 + 2),
                         (uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 9)))),auStack_1c);
    if (iVar5 == 0) {
      uVar6 = 0;
    }
    else {
      uVar6 = 2;
    }
  }
  restore_pmr_preserving_interrupt_disable_state_7244(uVar4);
  return uVar6;
}

void set_tx_cancel_request_when_pending_37bc(int param_1,int param_2)

{
  uint uVar1;
  
  uVar1 = (param_1 * 0x10 + param_2) - 3U & 0xff;
  if (((*((byte *)camry_host_ptr((uint32_t)((int)(0xffd20250u) + uVar1)))) & 1) != 0) {
    set_indexed_byte_bit_1d0e(((byte *)camry_host_ptr((uint32_t)((int)(0xffd20250u) + uVar1))), 1);
  }
  return;
}

undefined4 guarded_cancel_tx_buffer_if_channel_ready_37e4(uint param_1)

{
  uint32_t puVar1;
  uint uVar2;
  undefined4 uVar3;
  
  puVar1 = (camry_gp + 0x0u);
  uVar3 = raise_pmr_and_return_previous_mask_721e(0xffff);
  uVar2 = (param_1 & 0x7f) >> 4;
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(uVar2 - 0x6e83))))) == '\0') {
    set_tx_cancel_request_when_pending_37bc(uVar2,param_1 & 0xf);
  }
  restore_pmr_preserving_interrupt_disable_state_7244(uVar3);
  return uVar3;
}

void wait_global_status_bit3_clear_3818(void)

{
  uint uVar1;
  
  do {
    uVar1 = GSTS;
  } while ((uVar1 >> 3 & 1) != 0);
  return;
}

void clear_global_stop_or_request_reset_with_delay_3824(void)

{
  uint uVar1;
  
  uVar1 = GCTR;
  if ((uVar1 & 4) == 4) {
    uVar1 = GCTR;
    uVar1 = uVar1 & 0xfffffffb;
  }
  else {
    uVar1 = GCTR;
    if ((uVar1 & 3) != 0) {
      return;
    }
    uVar1 = GCTR;
    uVar1 = uVar1 & 0xfffffffc | 1;
  }
  GCTR = uVar1;
  __synchronize();
  busy_wait_155_decrements_per_unit_7208(8);
  return;
}

void clear_tx_buffers_and_sixteen_filter_entries_386c(void)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  RSCFD_TxMessageBuffer *pRVar4;
  int iVar5;
  
  DAT_ffd20500 = 0;
  DAT_ffd20520 = 0;
  DAT_ffd20540 = 0;
  DAT_ffd20504 = 0;
  DAT_ffd20524 = 0;
  DAT_ffd20544 = 0;
  DAT_ffd20508 = 0;
  DAT_ffd20528 = 0;
  DAT_ffd20548 = 0;
  DAT_ffd2050c = 0;
  DAT_ffd2052c = 0;
  DAT_ffd2054c = 0;
  iVar5 = 0;
  do {
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xffd24000u + (uint32_t)(iVar5) * 32u + 8u)))) = 0;
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xffd24000u + (uint32_t)(iVar5) * 32u)))) = 0;
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xffd24000u + (uint32_t)(iVar5) * 32u + 4u)))) = 0;
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xffd24000u + (uint32_t)(iVar5) * 32u + 12u)))) = 0;
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xffd24000u + (uint32_t)(iVar5) * 32u + 16u)))) = 0;
    pRVar4 = ((RSCFD_TxMessageBuffer *)camry_host_ptr((uint32_t)(0xffd24000u + (uint32_t)(iVar5) * 32u)));
    pRVar4->reserved_14_1f[0] = '\0';
    pRVar4->reserved_14_1f[1] = '\0';
    pRVar4->reserved_14_1f[2] = '\0';
    pRVar4->reserved_14_1f[3] = '\0';
    pRVar4 = ((RSCFD_TxMessageBuffer *)camry_host_ptr((uint32_t)(0xffd24000u + (uint32_t)(iVar5) * 32u)));
    pRVar4->reserved_14_1f[4] = '\0';
    pRVar4->reserved_14_1f[5] = '\0';
    pRVar4->reserved_14_1f[6] = '\0';
    pRVar4->reserved_14_1f[7] = '\0';
    iVar2 = iVar5 + 1;
    pRVar4 = ((RSCFD_TxMessageBuffer *)camry_host_ptr((uint32_t)(0xffd24000u + (uint32_t)(iVar5) * 32u)));
    pRVar4->reserved_14_1f[8] = '\0';
    pRVar4->reserved_14_1f[9] = '\0';
    pRVar4->reserved_14_1f[10] = '\0';
    pRVar4->reserved_14_1f[0xb] = '\0';
    iVar1 = iVar5 + -0x2f;
    iVar5 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  DAT_ffd20098 = 0x100;
  uVar3 = DAT_ffd20098;
  __synchronize();
  iVar5 = 0;
  do {
    iVar1 = iVar5 * 0x10;
    *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xffd21000u + (uint32_t)(iVar1) * 1u)))) = 0;
    *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xffd21004u + (uint32_t)(iVar1) * 1u)))) = 0;
    *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xffd21008u + (uint32_t)(iVar1) * 1u)))) = 0;
    iVar2 = iVar5 + 1;
    *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xffd2100cu + (uint32_t)(iVar1) * 1u)))) = 0;
    iVar1 = iVar5 + -0xf;
    iVar5 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  DAT_ffd20098 = 0;
  uVar3 = DAT_ffd20098;
  __synchronize();
  return;
}

void set_ffd204fc_one_and_synchronize_3908(void)

{
  undefined4 uVar1;
  
  DAT_ffd204fc = 1;
  uVar1 = DAT_ffd204fc;
  __synchronize();
  return;
}

void clear_channel_control_bit2_and_delay_3918(uint param_1)

{
  int iVar1;
  
  iVar1 = (param_1 & 0xff) * 0x10;
  *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xffd20004u + (uint32_t)(iVar1) * 1u)))) = *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xffd20004u + (uint32_t)(iVar1) * 1u)))) & 0xfffffffb;
  __synchronize();
  busy_wait_155_decrements_per_unit_7208(8);
  return;
}

void clear_fifo_and_receive_control_registers_3942(void)

{
  DAT_ffd20474 = 0;
  DAT_ffd200a4 = 0;
  DAT_ffd20118 = 0;
  DAT_ffd2011c = 0;
  DAT_ffd20120 = 0;
  CFCC3 = 0;
  DAT_ffd20128 = 0;
  CFCC5 = 0;
  DAT_ffd20130 = 0;
  DAT_ffd20134 = 0;
  DAT_ffd20138 = 0;
  DAT_ffd20394 = 0;
  return;
}

void set_global_configuration_ffff0000_396c(void)

{
  GCFG = 0xffff0000;
  return;
}

void set_channel_timing_and_data_configuration_3978(uint param_1)

{
  *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xffd20000u + (uint32_t)((param_1 & 0xff) * 0x10) * 1u)))) = 0xf3e7800;
  (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xffd20500u + (uint32_t)((param_1 & 0xff) * 8) * 4u)))) = 0x55c0000;
  return;
}

void store_reverse_indexed_rule_count_byte_3998(uint param_1,undefined1 param_2)

{
  (*((undefined1 *)camry_host_ptr((uint32_t)((int)0xffd2009cu + (3 - (param_1 & 0xff)))))) = param_2;
  return;
}

void update_ffd20098_bit8_from_shifted_byte_39a6(uint param_1)

{
  uint uVar1;
  undefined4 uVar2;
  
  uVar1 = DAT_ffd20098;
  DAT_ffd20098 = uVar1 & 0xfffffeff | (param_1 & 0xff) << 8;
  uVar2 = DAT_ffd20098;
  __synchronize();
  return;
}

void update_filter_selector_low_bits_39c0(uint param_1)

{
  uint uVar1;
  undefined4 uVar2;
  
  uVar1 = DAT_ffd20098;
  DAT_ffd20098 = param_1 & 0xff | uVar1 & 0xffffffe0;
  uVar2 = DAT_ffd20098;
  __synchronize();
  return;
}

void write_filter_identifier_mask_and_fifo_destination_39d6(short param_1,int param_2,uint param_3,int param_4,char param_5,int param_6)

{
  int iVar1;
  
  iVar1 = (param_3 & 0xff) * 0x10;
  *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xffd21000u + (uint32_t)(iVar1) * 1u)))) = param_4 + (uint)(param_5 != '\0') * -0x80000000;
  *(int *)(((undefined *)camry_host_ptr((uint32_t)(0xffd21004u + (uint32_t)(iVar1) * 1u)))) = param_6 + -0x40000000;
  *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xffd21008u + (uint32_t)(iVar1) * 1u)))) = 0;
  *(int *)(((undefined *)camry_host_ptr((uint32_t)(0xffd2100cu + (uint32_t)(iVar1) * 1u)))) = (1 << (param_2 + param_1 * 3 & 0x1fU)) << 8;
  return;
}

void configure_indexed_fifo_control_1100_3a18(short param_1,int param_2,char param_3)

{
  (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xffd20118u + (uint32_t)(param_2 + param_1 * 3 & 0xff) * 4u)))) = (uint)(param_3 != '\0') * 2 + 0x1100;
  return;
}

void or_indexed_tx_interrupt_enable_bit_3a36(int param_1,int param_2,char param_3)

{
  uint uVar1;
  uint *puVar2;
  
  uVar1 = (param_2 + param_1 * 0x10) - 3U & 0xff;
  if (uVar1 < 0x20) {
    puVar2 = ((undefined *)camry_host_ptr(0xffd20390u));
  }
  else {
    puVar2 = ((undefined *)camry_host_ptr(0xffd20394u));
    uVar1 = uVar1 - 0x20;
  }
  *puVar2 = *puVar2 | (uint)(param_3 != '\0') << (uVar1 & 0x1f);
  return;
}

void mask_channel_control_and_set_boolean_bit16_3a6a(uint param_1,short param_2)

{
  int iVar1;
  
  iVar1 = (param_1 & 0xff) * 0x10;
  *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xffd20004u + (uint32_t)(iVar1) * 1u)))) =
       *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xffd20004u + (uint32_t)(iVar1) * 1u)))) & 0x781000f7 | (uint)(param_2 != 0) << 0x10;
  return;
}

void set_channel_data_control_bit29_word_3a8e(uint param_1)

{
  (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xffd20504u + (uint32_t)((param_1 & 0xff) * 8) * 4u)))) = 0x20000000;
  return;
}

undefined4 set_channel_eic_mask_from_tp_f0_table_3a9e(uint param_1,short param_2)

{
  return set_selected_eic_mask_bit_guarded_1bbe(*(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)((camry_tp + 0xf0u) + (uint32_t)((param_1 & 0xff) * 2) * 1u)))),param_2 != 0);
}

undefined4 set_channel_eic_mask_from_tp_f6_table_3aba(uint param_1,short param_2)

{
  return set_selected_eic_mask_bit_guarded_1bbe(*(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)((camry_tp + 0xf6u) + (uint32_t)((param_1 & 0xff) * 2) * 1u)))),param_2 != 0);
}

void clear_global_control_mode_bits_and_delay_3ad6(void)

{
  uint uVar1;
  
  uVar1 = GCTR;
  GCTR = uVar1 & 0xfffffffc;
  uVar1 = GCTR;
  __synchronize();
  busy_wait_155_decrements_per_unit_7208(1);
  return;
}

void clear_channel_control_mode_bits_and_delay_3af4(uint param_1)

{
  int iVar1;
  
  iVar1 = (param_1 & 0xff) * 0x10;
  *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xffd20004u + (uint32_t)(iVar1) * 1u)))) = *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xffd20004u + (uint32_t)(iVar1) * 1u)))) & 0xfffffffc;
  __synchronize();
  busy_wait_155_decrements_per_unit_7208(0x10);
  return;
}

void enable_indexed_fifo_control_bit0_3b20(short param_1,int param_2)

{
  uint uVar1;
  
  uVar1 = param_1 * 3 + param_2 & 0xff;
  (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xffd20118u + (uint32_t)(uVar1) * 4u)))) = (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xffd20118u + (uint32_t)(uVar1) * 4u)))) | 1;
  return;
}

void initialize_configured_channels_buffers_and_filter_routes_3b3c(void)

{
  byte *pbVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  uint uVar5;
  undefined8 uVar6;
  int iVar7;
  undefined4 *puVar8;
  uint uVar9;
  int iVar10;
  int iVar11;
  uint uVar12;
  uint uVar13;
  uint uVar14;
  uint camry_type3_count;
  
  uVar6 = 0x869cfebf9800;
  uVar9 = 0;
  iVar7 = 0;
  do {
    iVar11 = iVar7 + 1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff917du) + (uint32_t)(iVar7) * 1u)))) = 1;
    iVar10 = iVar7 + -2;
    iVar7 = iVar11;
  } while (((iVar10 < 0) || (iVar11 < 0)));
  wait_global_status_bit3_clear_3818();
  clear_global_stop_or_request_reset_with_delay_3824();
  clear_tx_buffers_and_sixteen_filter_entries_386c();
  set_ffd204fc_one_and_synchronize_3908();
  iVar7 = 0;
  do {
    iVar10 = (*((int *)camry_host_ptr((uint32_t)((int)((ulonglong)uVar6 >> 0x20) + 0x2d0))));
    if (((*((byte *)camry_host_ptr((uint32_t)(iVar7 * 6 + iVar10 + 1)))) & 0x80) != 0) {
      clear_channel_control_bit2_and_delay_3918(iVar7);
    }
    iVar2 = iVar7 + 1;
    iVar11 = iVar7 + -2;
    iVar7 = iVar2;
  } while (((iVar11 < 0) || (iVar2 < 0)));
  clear_fifo_and_receive_control_registers_3942();
  set_global_configuration_ffff0000_396c();
  iVar7 = 0;
  do {
    if (((*((byte *)camry_host_ptr((uint32_t)(iVar7 * 6 + iVar10 + 1)))) & 0x80) != 0) {
      set_channel_timing_and_data_configuration_3978(iVar7);
    }
    iVar2 = iVar7 + 1;
    iVar11 = iVar7 + -2;
    iVar7 = iVar2;
  } while (((iVar11 < 0) || (iVar2 < 0)));
  iVar7 = 0;
  do {
    (*((undefined1 *)camry_host_ptr((uint32_t)((int)0xffd2009cu + iVar7)))) = 0;
    iVar2 = iVar7 + 1;
    iVar11 = iVar7 + -3;
    iVar7 = iVar2;
  } while (((iVar11 < 0) || (iVar2 < 0)));
  iVar7 = 0;
  do {
    if (((*((byte *)camry_host_ptr((uint32_t)(iVar7 * 6 + iVar10 + 1)))) & 0x80) != 0) {
      iVar11 = 0;
      camry_type3_count = 0;
      do {
        if ((*((byte *)camry_host_ptr((uint32_t)(((iVar7 << 4) | (iVar11 & 15)) * 12 +
            (*((volatile int32_t *)camry_host_ptr((uint32_t)((int)((ulonglong)uVar6 >> 32) + 0x2d4)))))))) >> 5 == 3) {
          camry_type3_count = (camry_type3_count + 1) & 0xff;
        }
        iVar3 = iVar11 + 1;
        iVar2 = iVar11 + -0xf;
        iVar11 = iVar3;
      } while (((iVar2 < 0) || (iVar3 < 0)));
      store_reverse_indexed_rule_count_byte_3998(iVar7,camry_type3_count);
    }
    iVar2 = iVar7 + 1;
    iVar11 = iVar7 + -2;
    iVar7 = iVar2;
  } while (((iVar11 < 0) || (iVar2 < 0)));
  update_ffd20098_bit8_from_shifted_byte_39a6(1);
  uVar14 = 0;
  do {
    if (((*((byte *)camry_host_ptr((uint32_t)(uVar14 * 6 + iVar10 + 1)))) & 0x80) != 0) {
      uVar13 = 0;
      uVar5 = (uVar14 & 7) << 4;
      do {
        uVar12 = uVar5 & 0xfffffff0 | uVar13 & 0xf;
        if ((uVar9 & 0xf) == 0) {
          update_filter_selector_low_bits_39c0(uVar9 >> 4);
        }
        iVar7 = (int)((ulonglong)uVar6 >> 0x20);
        pbVar1 = ((byte *)camry_host_ptr((uint32_t)(uVar12 * 0xc + (*((volatile int32_t *)camry_host_ptr((uint32_t)(iVar7 + 0x2d4)))))));
        if (*pbVar1 >> 5 == 3) {
          puVar8 = ((undefined4 *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(((uint)pbVar1[1] * 4 + (*((int *)camry_host_ptr((uint32_t)(iVar7 + 0x2d8))))))))))));
          write_filter_identifier_mask_and_fifo_destination_39d6(uVar5 >> 4,uVar13 & 0xf,uVar9 & 0xf,*puVar8,*(undefined1 *)(puVar8 + 2),
                       *(undefined4 *)(pbVar1 + 4));
          uVar9 = uVar9 + 1;
        }
        uVar4 = uVar13 + 1;
        iVar7 = uVar13 - 0xf;
        uVar13 = uVar4;
        uVar5 = uVar12;
      } while (iVar7 < 0 != ((int)uVar4 < 0 && -1 < iVar7));
    }
    uVar13 = uVar14 + 1;
    iVar7 = uVar14 - 2;
    uVar14 = uVar13;
  } while (iVar7 < 0 != ((int)uVar13 < 0 && -1 < iVar7));
  update_ffd20098_bit8_from_shifted_byte_39a6(0);
  DAT_ffd200a4 = 0;
  iVar7 = 0;
  do {
    iVar2 = iVar7 + 1;
    *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xffd200b8u + (uint32_t)(iVar7 * 4) * 1u)))) = 0;
    iVar11 = iVar7 + -7;
    iVar7 = iVar2;
  } while (((iVar11 < 0) || (iVar2 < 0)));
  uVar9 = 0;
  do {
    if (((*((byte *)camry_host_ptr((uint32_t)(uVar9 * 6 + iVar10 + 1)))) & 0x80) != 0) {
      uVar14 = 0;
      uVar13 = (uVar9 & 7) << 4;
      do {
        uVar12 = uVar13;
        uVar5 = uVar14 & 0xf;
        uVar13 = uVar12 & 0xfffffff0 | uVar5;
        pbVar1 = ((byte *)camry_host_ptr((uint32_t)(uVar13 * 0xc + (*((volatile int32_t *)camry_host_ptr((uint32_t)((int)((ulonglong)uVar6 >> 0x20) + 0x2d4)))))));
        if (*pbVar1 >> 5 == 3) {
          configure_indexed_fifo_control_1100_3a18(uVar12 >> 4,uVar5,pbVar1[8]);
        }
        else if (*pbVar1 >> 5 == 0) {
          or_indexed_tx_interrupt_enable_bit_3a36(uVar12 >> 4,uVar5,pbVar1[8]);
        }
        uVar5 = uVar14 + 1;
        iVar7 = uVar14 - 0xf;
        uVar14 = uVar5;
      } while (iVar7 < 0 != ((int)uVar5 < 0 && -1 < iVar7));
      mask_channel_control_and_set_boolean_bit16_3a6a(uVar12 >> 4,(*((undefined2 *)camry_host_ptr((uint32_t)((uVar12 >> 4) * 6 + iVar10 + 4)))));
    }
    uVar14 = uVar9 + 1;
    iVar7 = uVar9 - 2;
    uVar9 = uVar14;
  } while (iVar7 < 0 != ((int)uVar14 < 0 && -1 < iVar7));
  iVar7 = 0;
  do {
    if (((*((byte *)camry_host_ptr((uint32_t)(iVar7 * 6 + iVar10 + 1)))) & 0x80) != 0) {
      set_channel_data_control_bit29_word_3a8e(iVar7);
    }
    iVar2 = iVar7 + 1;
    iVar11 = iVar7 + -2;
    iVar7 = iVar2;
  } while (((iVar11 < 0) || (iVar2 < 0)));
  iVar7 = 0;
  do {
    iVar11 = iVar7 * 6 + iVar10;
    if (((*((byte *)camry_host_ptr((uint32_t)(iVar11 + 1)))) & 0x80) != 0) {
      set_channel_eic_mask_from_tp_f0_table_3a9e(iVar7,(*((undefined2 *)camry_host_ptr((uint32_t)(iVar11 + 2)))));
      set_channel_eic_mask_from_tp_f6_table_3aba(iVar7,(*((undefined2 *)camry_host_ptr((uint32_t)(iVar11 + 4)))));
    }
    iVar2 = iVar7 + 1;
    iVar11 = iVar7 + -2;
    iVar7 = iVar2;
  } while (((iVar11 < 0) || (iVar2 < 0)));
  clear_global_control_mode_bits_and_delay_3ad6();
  iVar7 = 0;
  do {
    if (((*((byte *)camry_host_ptr((uint32_t)(iVar7 * 6 + iVar10 + 1)))) & 0x80) != 0) {
      clear_channel_control_mode_bits_and_delay_3af4(iVar7);
    }
    iVar2 = iVar7 + 1;
    iVar11 = iVar7 + -2;
    iVar7 = iVar2;
  } while (((iVar11 < 0) || (iVar2 < 0)));
  uVar9 = 0;
  do {
    if (((*((byte *)camry_host_ptr((uint32_t)(uVar9 * 6 + iVar10 + 1)))) & 0x80) != 0) {
      uVar14 = (uVar9 & 7) << 4;
      uVar13 = 0;
      do {
        uVar14 = uVar14 & 0xfffffff0 | uVar13 & 0xf;
        if ((*((byte *)camry_host_ptr((uint32_t)(uVar14 * 0xc + (*((volatile int32_t *)camry_host_ptr((uint32_t)((int)((ulonglong)uVar6 >> 0x20) + 0x2d4)))))))) >> 5 == 3) {
          enable_indexed_fifo_control_bit0_3b20(uVar14 >> 4,uVar14 & 15);
        }
        uVar5 = uVar13 + 1;
        iVar7 = uVar13 - 0xf;
        uVar13 = uVar5;
      } while (iVar7 < 0 != ((int)uVar5 < 0 && -1 < iVar7));
    }
    uVar14 = uVar9 + 1;
    iVar7 = uVar9 - 2;
    uVar9 = uVar14;
  } while (iVar7 < 0 != ((int)uVar14 < 0 && -1 < iVar7));
  iVar7 = 0;
  do {
    if (((*((byte *)camry_host_ptr((uint32_t)(iVar7 * 6 + iVar10 + 1)))) & 0x80) != 0) {
      (*((undefined1 *)camry_host_ptr((uint32_t)(iVar7 + (int)uVar6 + -0x6e83)))) = 0;
    }
    iVar2 = iVar7 + 1;
    iVar11 = iVar7 + -2;
    iVar7 = iVar2;
  } while (((iVar11 < 0) || (iVar2 < 0)));
  return;
}

int read_combined_channel_tx_pending_bits_3e1c(uint param_1)

{
  uint *puVar1;
  
  if ((param_1 & 0xff) < 2) {
    puVar1 = ((undefined *)camry_host_ptr(0xffd20370u));
  }
  else {
    puVar1 = ((undefined *)camry_host_ptr(0xffd20374u));
  }
  return ((puVar1[4] | *puVar1) >> ((param_1 & 1) << 4) & 0x1fff) << 3;
}

int get_tx_buffer_status_bits1_2_3e48(int param_1,int param_2)

{
  return (int)((*((byte *)camry_host_ptr((uint32_t)((int)(0xffd202d0u) + ((param_2 + param_1 * 0x10) - 3U & 0xff))))) & 6) >> 1;
}

void clear_tx_buffer_status_bits1_2_3e5e(int param_1,int param_2)

{
  uint uVar1;
  
  uVar1 = (param_2 + param_1 * 0x10) - 3U & 0xff;
  (*((byte *)camry_host_ptr((uint32_t)((int)(0xffd202d0u) + uVar1)))) = (*((byte *)camry_host_ptr((uint32_t)((int)(0xffd202d0u) + uVar1)))) & 0xf9;
  __synchronize();
  return;
}

void read_tx_buffer_identifier_and_extended_flag_3e80(int param_1,int param_2,uint *param_3,byte *param_4)

{
  uint uVar1;
  
  uVar1 = (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xffd24000u + (uint32_t)((param_2 + param_1 * 0x10) - 3U & 0xff) * 32u))));
  *param_4 = (byte)(uVar1 >> 0x1f);
  *param_3 = uVar1 & 0x1fffffff;
  return;
}

void acknowledge_tx_status_and_dispatch_result_3ea4(uint param_1)

{
  uint8_t stack_record_19[25];
  int iVar1;
  uint uVar2;
  uint uVar3;
  
  uVar2 = (param_1 & 0x7f) >> 4;
  uVar3 = param_1 & 0xf;
  iVar1 = get_tx_buffer_status_bits1_2_3e48(uVar2,uVar3);
  clear_tx_buffer_status_bits1_2_3e5e(uVar2,uVar3);
  read_tx_buffer_identifier_and_extended_flag_3e80(uVar2,uVar3,((uint32_t *)((stack_record_19 + 1))),((uint8_t *)(stack_record_19)));
  if (iVar1 == 2 || iVar1 == 3) {
    dispatch_transmit_route_event_zero_4744(param_1 & 0xffff, ((uint32_t *)((stack_record_19 + 1)))[0], stack_record_19[0]);
  }
  else {
    dispatch_transmit_route_event_two_475c(param_1 & 0xffff,((uint32_t *)((stack_record_19 + 1)))[0],stack_record_19[0]);
  }
  return;
}

void dispatch_pending_type0_tx_buffer_events_3ef2(uint param_1)

{
  int iVar1;
  uint uVar2;
  undefined8 uVar3;
  int iVar4;
  uint uVar5;
  uint uVar6;
  
  uVar3 = 0x869c00000000;
  uVar6 = (param_1 & 7) << 4;
  iVar4 = read_combined_channel_tx_pending_bits_3e1c(param_1 & 7);
  uVar5 = 0;
  do {
    uVar6 = uVar6 & 0xfffffff0 | uVar5 & 0xf;
    if ((((*((byte *)camry_host_ptr((uint32_t)(uVar6 * 0xc + (*((volatile int32_t *)camry_host_ptr((uint32_t)((int)((ulonglong)uVar3 >> 0x20) + 0x2d4)))))))) & 0xe0) == 0)
       && ((iVar4 >> (uVar5 & 0xf) & 1U) != 0)) {
      acknowledge_tx_status_and_dispatch_result_3ea4(uVar6);
    }
    uVar2 = uVar5 + 1;
    iVar1 = uVar5 - 0xf;
    uVar5 = uVar2;
  } while (iVar1 < 0 != ((int)uVar2 < 0 && -1 < iVar1));
  return;
}

uint read_channel_three_fifo_status_bits_3f4a(ushort param_1)

{
  uint uVar1;
  
  uVar1 = DAT_ffd20248;
  return uVar1 >> ((short)(param_1 & 0xff) * 3 & 0x1fU) & 7;
}

uint read_indexed_fifo_status_bit3_3f60(short param_1,int param_2)

{
  return ((((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xffd20178u + (uint32_t)(param_2 + param_1 * 3 & 0xff) * 4u))))) >> 3) & 1u);
}

void acknowledge_fifo_status_with_14_3f78(short param_1,int param_2)

{
  RSCFD_CFSTS *pRVar1;
  
  pRVar1 = ((RSCFD_CFSTS *)camry_host_ptr((uint32_t)(0xffd20178u + (uint32_t)((param_1 * 3 + param_2 & 0xff)) * 4u)));
  pRVar1->reserved_0_2 = 4;
  pRVar1->reserved_4_31 = 1;
  pRVar1->status_b3 = 0;
  __synchronize();
  return;
}

bool read_and_advance_fifo_frame_if_status_bit3_3f96(undefined1 param_1,uint param_2,undefined4 param_3,undefined4 param_4,
                 byte *param_5,uint *param_6)

{
  short extraout_r6;
  uint *extraout_r8;
  byte *extraout_r9;
  int iVar1;
  uint uVar2;
  uint uVar3;
  
  iVar1 = read_indexed_fifo_status_bit3_3f60(param_1, (uint)(byte)param_2);
  if (iVar1 != 0) {
    acknowledge_fifo_status_with_14_3f78((extraout_r6 = (uint)(byte)param_1), (uint)(byte)param_2);
    uVar3 = (param_2 & 0xff) + ((short)((uint)(byte)param_1)) * 3 & 0xff;
    uVar2 = (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xffd23400u + (uint32_t)(uVar3 * 4) * 32u))));
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(param_4)))) = (byte)(uVar2 >> 0x1f);
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(param_3)))) = uVar2 & 0x1fffffff;
    *param_5 = (byte)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xffd23400u + (uint32_t)(uVar3 * 4) * 32u + 4u)))) >> 0x1c);
    *param_6 = (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xffd23400u + (uint32_t)(uVar3 * 4) * 32u + 12u))));
    param_6[1] = (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xffd23400u + (uint32_t)(uVar3 * 4) * 32u + 16u))));
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xffd201d8u + (uint32_t)(uVar3) * 4u)))) = 0xff;
  }
  return iVar1 == 0;
}
