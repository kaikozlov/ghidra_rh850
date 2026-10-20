#include "common.h"

void poll_receive_capacity_and_send_flow_control_2046(uint param_1)

{
  int iVar1;
  byte bVar2;
  ushort uVar3;
  uint32_t puVar4;
  F33BootInterruptEntry *pFVar5;
  uint uVar6;
  short sVar7;
  ushort uStack_1a;
  F33BootPduInfo FStack_18;
  
  bVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff9132u)))));
  puVar4 = (camry_gp + 0x0u);
  pFVar5 = ((volatile F33BootInterruptEntry *)camry_host_ptr((camry_tp + 0x0u)));
  uStack_1a = 0;
  FStack_18.data = 0;
  FStack_18.length = 0;
  iVar1 = (int)(short)(ushort)(*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff9132u)))));
  uVar6 = boot_transport_request_append
                    (*(ushort *)(&(*((volatile uint32_t *)camry_host_ptr((camry_tp + 0x6cau)))) + iVar1 * 6),&FStack_18,&uStack_1a);
  if (uVar6 == 0) {
    uVar3 = 0;
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6bdu) + (uint32_t)(iVar1 * 0x18) * 1u)))) != 0) {
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6b7u) + (uint32_t)(iVar1 * 0x18) * 1u)))) == '\x04') {
        sVar7 = 6;
      }
      else {
        sVar7 = 7;
      }
      uVar3 = sVar7 * (ushort)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6bdu) + (uint32_t)(iVar1 * 0x18) * 1u))));
    }
    if ((uStack_1a < (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + -0x6ed4))))) && ((uVar3 == 0 || (uStack_1a < uVar3)))) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6ecf))))) = 0x54;
    }
    else {
      disarm_indexed_timer_slot_1d70((*((undefined1 *)((uint8_t *)&pFVar5[0xd6].eiic + ((param_1 & 0xff) * 2)))));
      send_transport_flow_control_continue_1f98(bVar2);
    }
  }
  else {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6ecf))))) = 0;
    disarm_indexed_timer_slot_1d70((*((undefined1 *)((uint8_t *)&pFVar5[0xd6].eiic + ((param_1 & 0xff) * 2)))));
    boot_transport_receive_complete(*(ushort *)(&(*((volatile uint32_t *)camry_host_ptr((camry_tp + 0x6cau)))) + iVar1 * 6),'\x01');
  }
  return;
}

void send_transport_consecutive_response_frame_20e4(uint param_1)

{
  uint8_t stack_record_2a[42];
  int iVar1;
  undefined1 uVar2;
  undefined2 uVar3;
  uint32_t puVar4;
  uint uVar5;
  int iVar6;
  byte bVar7;
  uint uVar8;
  F33BootPduInfo FStack_28;
  
  puVar4 = (camry_gp + 0x0u);
  param_1 = param_1 & 0xff;
  iVar1 = param_1 * 0x10;
  FStack_28.length = 7;
  uVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6e7u) + (uint32_t)(iVar1) * 1u))));
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6e4u) + (uint32_t)(iVar1) * 1u)))) == '\x04') {
    ((uint8_t *)((stack_record_2a + 10)))[0] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6e5u) + (uint32_t)(iVar1) * 1u))));
    FStack_28.length = 6;
  }
  uVar8 = (uint)((*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6e4u) + (uint32_t)(iVar1) * 1u)))) == '\x04');
  bVar7 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff9133u))))) + 1U & 0xf;
  ((uint8_t *)((stack_record_2a + 10)))[uVar8] = bVar7 + 0x20;
  FStack_28.data = camry_host_addr(((uint8_t *)((stack_record_2a + 10))) + uVar8 + 1);
  (*((uint16_t *)(stack_record_2a + 0))) = (*((volatile uint16_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff912cu)))));
  if ((*((volatile uint16_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff912cu))))) < FStack_28.length) {
    FStack_28.length = (*((volatile uint16_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff912cu)))));
  }
  uVar5 = boot_transport_response_copy((ushort)param_1,&FStack_28,0,stack_record_2a);
  if (uVar5 == 0) {
    for (uVar8 = uVar8 + 1 + (uint)FStack_28.length & 0xffff; uVar8 < 8; uVar8 = uVar8 + 1) {
      ((uint8_t *)((stack_record_2a + 10)))[uVar8] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6e6u) + (uint32_t)(iVar1) * 1u))));
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6ecd))))) = bVar7;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6ecc))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6ecc))))) + '\x01';
    (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + -0x6ed4)))) = (*((uint16_t *)(stack_record_2a + 0)));
    FStack_28.data = camry_host_addr(((uint8_t *)((stack_record_2a + 10))));
    FStack_28.length = 8;
    iVar6 = copy_pdu_descriptor_and_submit_1ec0((*((volatile uint16_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6f2u) + (uint32_t)(param_1 * 8) * 2u)))),&FStack_28);
    if (iVar6 == 0) {
      uVar3 = *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)((camry_tp + 0x6eau) + (uint32_t)(iVar1) * 1u))));
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6ecf))))) = 0x8c;
      increment_timer_generation_and_arm_transport_slot_1f60(uVar2,0,uVar3);
      return;
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6ecf))))) = 0;
  boot_transport_response_complete((ushort)param_1,'\x01');
  return;
}

void poll_response_capacity_and_send_consecutive_frame_21c2(uint param_1)

{
  byte bVar1;
  uint32_t puVar2;
  F33BootInterruptEntry *pFVar3;
  uint uVar4;
  ushort uVar5;
  ushort uVar6;
  ushort uStack_1a;
  F33BootPduInfo FStack_18;
  
  bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff9132u)))));
  puVar2 = (camry_gp + 0x0u);
  pFVar3 = ((volatile F33BootInterruptEntry *)camry_host_ptr((camry_tp + 0x0u)));
  uStack_1a = 0;
  FStack_18.data = 0;
  FStack_18.length = 0;
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6e4u))))) == '\x04') {
    uVar5 = 6;
  }
  else {
    uVar5 = 7;
  }
  uVar6 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff912cu)))));
  if (uVar5 <= (*((volatile uint16_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff912cu)))))) {
    uVar6 = uVar5;
  }
  uVar4 = boot_transport_response_copy((ushort)(*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff9132u))))),&FStack_18,0,&uStack_1a);
  if (uVar4 == 0) {
    if (uVar6 <= uStack_1a) {
      disarm_indexed_timer_slot_1d70((*((undefined1 *)((uint8_t *)&pFVar3[0xd6].eiic + ((param_1 & 0xff) * 2)))));
      if (((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6ecf)))))) == -0x5e) {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6ecf))))) = 0xa1;
      }
      else {
        send_transport_consecutive_response_frame_20e4(bVar1);
      }
    }
  }
  else if (uVar4 != 2) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6ecf))))) = 0;
    disarm_indexed_timer_slot_1d70((*((undefined1 *)((uint8_t *)&pFVar3[0xd6].eiic + ((param_1 & 0xff) * 2)))));
    boot_transport_response_complete((ushort)bVar1,'\x01');
  }
  return;
}

void service_pending_transport_capacity_states_2250(void)

{
  if ((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9130u)))) != '\0') {
    if ((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9131u)))) == 'T') {
      poll_receive_capacity_and_send_flow_control_2046(0);
    }
    else if ((((int8_t)(*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9131u))))) == -0x5e) || (((int8_t)(*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9131u))))) == -0x5c)) {
      poll_response_capacity_and_send_consecutive_frame_21c2(0);
    }
  }
  return;
}

uint find_receive_route_and_extract_frame_nibble_2284(uint param_1,byte *param_2,byte *param_3)

{
  byte bVar1;
  uint uVar2;
  int iVar3;
  
  uVar2 = param_1 & 0xff;
  do {
    if (1 < uVar2) {
      return uVar2;
    }
    iVar3 = (short)uVar2 * 0x18;
    if ((param_1 & 0xffff) <= (uint)*(ushort *)(((undefined *)camry_host_ptr((uint32_t)((camry_tp + 0x6b4u) + (uint32_t)(iVar3) * 1u))))) {
      if ((param_1 & 0xffff) < (uint)*(ushort *)(((undefined *)camry_host_ptr((uint32_t)((camry_tp + 0x6b4u) + (uint32_t)(iVar3) * 1u))))) {
        return 2;
      }
      bVar1 = *param_2;
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6b7u) + (uint32_t)(iVar3) * 1u)))) == '\x03') {
LAB_000022a8:
        *param_3 = bVar1 & 0xf0;
        return uVar2;
      }
      if (bVar1 == (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6b8u) + (uint32_t)(iVar3) * 1u))))) {
        bVar1 = param_2[1];
        goto LAB_000022a8;
      }
    }
    uVar2 = uVar2 + 1;
  } while( true );
}

undefined4 preempt_receive_if_same_or_higher_priority_route_22ca(uint param_1,ushort param_2)

{
  uint32_t puVar1;
  F33BootInterruptEntry *pFVar2;
  F33BootInterruptEntry *pFVar3;
  undefined4 uVar4;
  ushort uVar5;
  
  puVar1 = (camry_gp + 0x0u);
  pFVar2 = ((volatile F33BootInterruptEntry *)camry_host_ptr((camry_tp + 0x0u)));
  uVar4 = 0;
  uVar5 = (ushort)(*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff9132u)))));
  if (((param_2 & 0xff) == (ushort)(*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff9132u)))))) ||
     ((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6bbu) + (uint32_t)((short)(param_2 & 0xff) * 0x18) * 1u)))) <
      (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6bbu) + (uint32_t)((short)uVar5 * 0x18) * 1u)))))) {
    uVar4 = 1;
    if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff9131u))))) == 'J') || (((*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff9131u))))) == 'L' || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff9131u))))) == 'I')))) {
      cancel_mapped_transmit_and_return_zero_1ede((*((volatile uint16_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6f2u))))));
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6ecf))))) = 0;
    pFVar3 = pFVar2;
    disarm_indexed_timer_slot_1d70((*((undefined1 *)((uint8_t *)&pFVar2[0xd6].eiic + ((param_1 & 0xff) * 2)))));
    disarm_indexed_timer_slot_1d70((*((undefined1 *)((uint8_t *)&pFVar2[0xd6].eiic + ((param_1 & 0xff) * 2 + 1)))));
    boot_transport_receive_complete
              ((*((ushort *)((uint8_t *)&pFVar3[(short)uVar5 * 3 + 0xd9].eiic + (2)))),'\a');
  }
  return uVar4;
}

undefined4 preempt_response_for_higher_priority_receive_2350(uint param_1,ushort param_2)

{
  byte bVar1;
  uint32_t puVar2;
  F33BootInterruptEntry *pFVar3;
  undefined4 uVar4;
  
  bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff9132u)))));
  puVar2 = (camry_gp + 0x0u);
  pFVar3 = ((volatile F33BootInterruptEntry *)camry_host_ptr((camry_tp + 0x0u)));
  uVar4 = 0;
  if ((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6bbu) + (uint32_t)((short)(param_2 & 0xff) * 0x18) * 1u)))) < (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6e8u)))))) {
    uVar4 = 1;
    if (((((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff9131u)))))) == -0x76) || (((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff9131u)))))) == -0x77)) || (((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff9131u)))))) == -0x74)) {
      cancel_mapped_transmit_and_return_zero_1ede((*((volatile uint16_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6f2u))))));
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6ecf))))) = 0;
    disarm_indexed_timer_slot_1d70((*((undefined1 *)((uint8_t *)&pFVar3[0xd6].eiic + ((param_1 & 0xff) * 2)))));
    disarm_indexed_timer_slot_1d70((*((undefined1 *)((uint8_t *)&pFVar3[0xd6].eiic + ((param_1 & 0xff) * 2 + 1)))));
    boot_transport_response_complete((ushort)bVar1,'\a');
  }
  return uVar4;
}

void admit_append_and_complete_single_frame_request_23b8(ushort param_1,ushort param_2,uchar *param_3)

{
  camry_write32((camry_sp - 4u) & ~3u, camry_gpr[28]);
  camry_write32((camry_sp - 8u) & ~3u, camry_gpr[29]);
  camry_write32((camry_sp - 12u) & ~3u, camry_gpr[31]);
  camry_sp -= 24u;
  camry_gpr[3] = camry_sp;

  ushort channel;
  uint32_t puVar1;
  uchar status;
  uint uVar2;
  ushort uStack_16;
  F33BootPduInfo FStack_14;
  
  puVar1 = (camry_gp + 0x0u);
  channel = (*((ushort *)camry_host_ptr((uint32_t)((camry_tp + 0x6cau) + (uint32_t)((short)(param_1 & 0xff) * 6) * 4u))));
  uStack_16 = 0;
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9131u)))) = 0x54;
  FStack_14.data = camry_host_addr(param_3);
  FStack_14.length = param_2;
  uVar2 = (camry_gpr[28] = param_2, camry_gpr[29] = channel, camry_gpr[6] = channel, camry_r7 = camry_gpr[7] = camry_sp + 4u, camry_gpr[8] = param_2, camry_gpr[9] = camry_sp + 2u, camry_write32(camry_sp + 4u, camry_host_addr(param_3)), camry_write16(camry_sp + 8u, param_2), camry_write16(camry_sp + 2u, uStack_16), camry_gpr[31] = 0x23f0u, boot_transport_request_admit)(channel,&FStack_14,param_2,&uStack_16);
  if ((uVar2 == 0) && (param_2 <= uStack_16)) {
    uVar2 = (camry_gpr[6] = channel, camry_r7 = camry_gpr[7] = camry_sp + 4u, camry_gpr[8] = camry_sp + 2u, camry_write16(camry_sp + 2u, uStack_16), camry_gpr[31] = 0x240au, boot_transport_request_append)(channel,&FStack_14,&uStack_16);
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6ecf))))) = 0;
    status = uVar2 != 0;
  }
  else {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6ecf))))) = 0;
    if (uVar2 != 0) {
      { if (!camry_halted) { camry_gpr[28] = camry_read32((camry_sp + 20u) & ~3u); camry_gpr[29] = camry_read32((camry_sp + 16u) & ~3u); camry_gpr[31] = camry_read32((camry_sp + 12u) & ~3u); camry_sp += 24u; camry_gpr[3] = camry_sp; } return; }
    }
    status = '\t';
  }
  (camry_gpr[6] = channel, camry_r7 = camry_gpr[7] = status, camry_gpr[31] = 0x2426u, boot_transport_receive_complete)(channel,status);
  { if (!camry_halted) { camry_gpr[28] = camry_read32((camry_sp + 20u) & ~3u); camry_gpr[29] = camry_read32((camry_sp + 16u) & ~3u); camry_gpr[31] = camry_read32((camry_sp + 12u) & ~3u); camry_sp += 24u; camry_gpr[3] = camry_sp; } return; }
}

void validate_and_dispatch_transport_single_frame_242a(ushort param_1,uint param_2,int param_3)

{
  camry_write32((camry_sp - 4u) & ~3u, camry_gpr[26]);
  camry_write32((camry_sp - 8u) & ~3u, camry_gpr[27]);
  camry_write32((camry_sp - 12u) & ~3u, camry_gpr[28]);
  camry_write32((camry_sp - 16u) & ~3u, camry_gpr[29]);
  camry_write32((camry_sp - 20u) & ~3u, camry_gpr[31]);
  camry_sp -= 20u;
  camry_gpr[3] = camry_sp;

  byte bVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  
  param_1 = param_1 & 0xff;
  uVar5 = (uint)((*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6b7u) + (uint32_t)((short)param_1 * 0x18) * 1u)))) == '\x04');
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6b7u) + (uint32_t)((short)param_1 * 0x18) * 1u)))) == '\x04') {
    uVar3 = 6;
    iVar2 = 2;
  }
  else {
    uVar3 = 7;
    iVar2 = 1;
  }
  bVar1 = (*((byte *)camry_host_ptr((uint32_t)(uVar5 + param_3))));
  uVar4 = bVar1 & 0xf;
  if ((((bVar1 & 0xf) != 0) && (uVar4 <= uVar3)) &&
     (-1 < (int)((param_2 & 0xffff) - (iVar2 + uVar4)))) {
    iVar2 = 1;
    if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff9131u))))) == 'I' || (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff9131u))))) == 'J') || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff9131u))))) == 'L')) ||
       (((*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff9131u))))) == 'Q' || (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff9131u))))) == 'R' ||
        (((*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff9131u))))) == 'T' || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff9131u))))) == 'a')))))) {
      iVar2 = preempt_receive_if_same_or_higher_priority_route_22ca((*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6bau) + (uint32_t)((short)param_1 * 0x18) * 1u)))),param_1);
    }
    else if ((((((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff9131u)))))) == -0x77 || ((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff9131u)))))) == -0x76) || (((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff9131u)))))) == -0x74)) ||
             (((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff9131u)))))) == -0x6f || ((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff9131u)))))) == -0x6e)) ||
            ((((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff9131u)))))) == -0x5f || ((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff9131u)))))) == -0x5e || (((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff9131u)))))) == -0x5c)))) {
      iVar2 = preempt_response_for_higher_priority_receive_2350((*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6bau) + (uint32_t)((short)param_1 * 0x18) * 1u)))),param_1);
    }
    if (iVar2 == 1) {
      (camry_gpr[26] = ((uint32_t)((uint32_t)((uintptr_t)param_3))), camry_gpr[27] = param_1 & 0xffu, camry_gpr[28] = uVar4, camry_gpr[29] = uVar5 + 1u, camry_gpr[6] = param_1, camry_r7 = camry_gpr[7] = uVar4, camry_gpr[8] = camry_gpr[26] + uVar5 + 1u, camry_gpr[31] = 0x24ccu, admit_append_and_complete_single_frame_request_23b8)(param_1, uVar4, ((uchar *)camry_host_ptr((uint32_t)(uVar5 + 1 + param_3))));
    }
  }
  { if (!camry_halted) { camry_gpr[26] = camry_read32((camry_sp + 16u) & ~3u); camry_gpr[27] = camry_read32((camry_sp + 12u) & ~3u); camry_gpr[28] = camry_read32((camry_sp + 8u) & ~3u); camry_gpr[29] = camry_read32((camry_sp + 4u) & ~3u); camry_gpr[31] = camry_read32((camry_sp + 0u) & ~3u); camry_sp += 20u; camry_gpr[3] = camry_sp; } return; }
}

void send_transport_flow_control_wait_with_limit_24d0(ushort param_1)

{
  int iVar1;
  undefined1 uVar2;
  byte bVar3;
  undefined2 uVar4;
  byte bVar5;
  uint uVar6;
  uint uVar7;
  uint32_t puVar8;
  ushort channel;
  uchar status;
  int iVar9;
  undefined1 uVar10;
  int iVar11;
  F33BootPduInfo local_20;
  undefined1 auStack_18 [8];
  
  bVar5 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff9137u)))));
  puVar8 = (camry_gp + 0x0u);
  iVar1 = (int)(short)(param_1 & 0xff);
  iVar11 = iVar1 * 0x18;
  uVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6bau) + (uint32_t)(iVar11) * 1u))));
  bVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6bcu) + (uint32_t)(iVar11) * 1u))));
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff9137u))))) < (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6c8u) + (uint32_t)(iVar11) * 1u))))) {
    iVar9 = (uint)bVar3 * 0x10;
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6e4u) + (uint32_t)(iVar9) * 1u)))) == '\x04') {
      auStack_18[0] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6e5u) + (uint32_t)(iVar9) * 1u))));
    }
    uVar6 = (uint)((*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6e4u) + (uint32_t)(iVar9) * 1u)))) == '\x04');
    auStack_18[uVar6] = 0x31;
    uVar7 = uVar6 + 2;
    auStack_18[uVar6 + 1] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6bdu) + (uint32_t)(iVar11) * 1u))));
    uVar10 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6beu) + (uint32_t)(iVar11) * 1u))));
    while( true ) {
      auStack_18[uVar7] = uVar10;
      uVar7 = uVar7 + 1 & 0xffff;
      if (7 < uVar7) break;
      uVar10 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6e6u) + (uint32_t)(iVar9) * 1u))));
    }
    local_20.length = 8;
    local_20.data = camry_host_addr(auStack_18);
    iVar9 = copy_pdu_descriptor_and_submit_1ec0((*((volatile uint16_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6f2u) + (uint32_t)((uint)bVar3 * 8) * 2u)))),&local_20);
    if (iVar9 == 0) {
      uVar4 = *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)((camry_tp + 0x6c0u) + (uint32_t)(iVar11) * 1u))));
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar8 + (uint32_t)(-0x6ec9))))) = bVar5 + 1;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar8 + (uint32_t)(-0x6ecf))))) = 0x4c;
      increment_timer_generation_and_arm_transport_slot_1f60(uVar2,0,uVar4);
      return;
    }
    channel = *(ushort *)(&(*((volatile uint32_t *)camry_host_ptr((camry_tp + 0x6cau)))) + iVar1 * 6);
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar8 + (uint32_t)(-0x6ecf))))) = 0;
    status = '\x01';
  }
  else {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff9131u))))) = 0;
    status = '\b';
    channel = *(ushort *)(&(*((volatile uint32_t *)camry_host_ptr((camry_tp + 0x6cau)))) + iVar1 * 6);
  }
  boot_transport_receive_complete(channel,status);
  return;
}

void query_receive_capacity_or_schedule_flow_control_2594(undefined1 param_1,ushort param_2)

{
  int iVar1;
  byte bVar2;
  undefined2 uVar3;
  ushort uVar4;
  uint32_t puVar5;
  uint uVar6;
  short sVar7;
  int iVar8;
  ushort uStack_1a;
  F33BootPduInfo FStack_18;
  
  puVar5 = (camry_gp + 0x0u);
  param_2 = param_2 & 0xff;
  iVar1 = (int)(short)param_2;
  iVar8 = iVar1 * 0x18;
  uStack_1a = 0;
  FStack_18.data = 0;
  FStack_18.length = 0;
  uVar6 = boot_transport_request_append
                    (*(ushort *)(&(*((volatile uint32_t *)camry_host_ptr((camry_tp + 0x6cau)))) + iVar1 * 6),&FStack_18,&uStack_1a);
  if (uVar6 == 0) {
    bVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6bdu) + (uint32_t)(iVar8) * 1u))));
    uVar4 = 0;
    if (bVar2 != 0) {
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6b7u) + (uint32_t)(iVar8) * 1u)))) == '\x04') {
        sVar7 = 6;
      }
      else {
        sVar7 = 7;
      }
      uVar4 = sVar7 * (ushort)bVar2;
    }
    if ((uStack_1a < (*((ushort *)camry_host_ptr((uint32_t)(puVar5 + -0x6ed4))))) && ((bVar2 == 0 || (uStack_1a < uVar4)))) {
      if (*(short *)(((undefined *)camry_host_ptr((uint32_t)((camry_tp + 0x6c2u) + (uint32_t)(iVar8) * 1u)))) == 0) {
        send_transport_flow_control_wait_with_limit_24d0(param_2);
      }
      else {
        uVar3 = *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)((camry_tp + 0x6c2u) + (uint32_t)(iVar8) * 1u))));
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x6ecf))))) = 0x54;
        increment_timer_generation_and_arm_transport_slot_1f60(param_1,0,uVar3);
      }
    }
    else {
      send_transport_flow_control_continue_1f98(param_2);
    }
  }
  else {
    uVar4 = *(ushort *)(&(*((volatile uint32_t *)camry_host_ptr((camry_tp + 0x6cau)))) + iVar1 * 6);
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x6ecf))))) = 0;
    boot_transport_receive_complete(uVar4,'\x01');
  }
  return;
}

void send_transport_flow_control_overflow_2636(ushort param_1)

{
  undefined1 uVar1;
  byte bVar2;
  undefined2 uVar3;
  uint uVar4;
  uint uVar5;
  uint32_t puVar6;
  int iVar7;
  undefined1 uVar8;
  int iVar9;
  F33BootPduInfo local_1c;
  undefined1 auStack_14 [8];
  
  puVar6 = (camry_gp + 0x0u);
  iVar9 = (short)(param_1 & 0xff) * 0x18;
  uVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6bau) + (uint32_t)(iVar9) * 1u))));
  bVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6bcu) + (uint32_t)(iVar9) * 1u))));
  iVar7 = (uint)bVar2 * 0x10;
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6e4u) + (uint32_t)(iVar7) * 1u)))) == '\x04') {
    auStack_14[0] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6e5u) + (uint32_t)(iVar7) * 1u))));
  }
  uVar4 = (uint)((*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6e4u) + (uint32_t)(iVar7) * 1u)))) == '\x04');
  auStack_14[uVar4] = 0x32;
  uVar5 = uVar4 + 2;
  auStack_14[uVar4 + 1] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6bdu) + (uint32_t)(iVar9) * 1u))));
  uVar8 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6beu) + (uint32_t)(iVar9) * 1u))));
  while( true ) {
    auStack_14[uVar5] = uVar8;
    uVar5 = uVar5 + 1 & 0xffff;
    if (7 < uVar5) break;
    uVar8 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6e6u) + (uint32_t)(iVar7) * 1u))));
  }
  local_1c.length = 8;
  local_1c.data = camry_host_addr(auStack_14);
  iVar7 = copy_pdu_descriptor_and_submit_1ec0((*((volatile uint16_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6f2u) + (uint32_t)((uint)bVar2 * 8) * 2u)))),&local_1c);
  if (iVar7 == 0) {
    uVar3 = *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)((camry_tp + 0x6c0u) + (uint32_t)(iVar9) * 1u))));
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6ecf))))) = 0x4a;
    increment_timer_generation_and_arm_transport_slot_1f60(uVar1,0,uVar3);
  }
  else {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6ecf))))) = 0;
  }
  return;
}

void admit_first_request_frame_and_start_receive_state_26d2(byte param_1,ushort param_2,uchar *param_3)

{
  undefined1 uVar1;
  ushort channel;
  short sVar2;
  undefined2 uVar3;
  uint32_t puVar4;
  undefined4 uVar5;
  uint uVar6;
  int iVar7;
  ushort uStack_22;
  F33BootPduInfo FStack_20;
  
  puVar4 = (camry_gp + 0x0u);
  iVar7 = (short)(ushort)param_1 * 0x18;
  FStack_20.length = 6;
  uVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6bau) + (uint32_t)(iVar7) * 1u))));
  channel = (*((ushort *)camry_host_ptr((uint32_t)((camry_tp + 0x6cau) + (uint32_t)((short)(ushort)param_1 * 6) * 4u))));
  uStack_22 = 0;
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6b7u) + (uint32_t)(iVar7) * 1u)))) == '\x04') {
    FStack_20.length = 5;
  }
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9131u)))) = 0x54;
  FStack_20.data = camry_host_addr(param_3);
  uVar6 = boot_transport_request_admit(channel,&FStack_20,param_2,&uStack_22);
  if (uVar6 == 0) {
    if (FStack_20.length <= uStack_22) {
      uVar6 = boot_transport_request_append(channel,&FStack_20,&uStack_22);
      if (uVar6 != 0) {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6ecf))))) = 0;
        boot_transport_receive_complete(channel,'\x01');
        return;
      }
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6ec9))))) = 0;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6ecc))))) = 0;
      sVar2 = *(short *)(((undefined *)camry_host_ptr((uint32_t)((camry_tp + 0x6c4u) + (uint32_t)(iVar7) * 1u))));
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6ecd))))) = 0;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6ece))))) = param_1;
      (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + -0x6ed4)))) = param_2 - FStack_20.length;
      if (sVar2 == 0) {
        query_receive_capacity_or_schedule_flow_control_2594(uVar1,param_1);
        return;
      }
      uVar3 = *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)((camry_tp + 0x6c4u) + (uint32_t)(iVar7) * 1u))));
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6ecf))))) = 0x51;
      increment_timer_generation_and_arm_transport_slot_1f60(uVar1,1,uVar3);
      uVar3 = *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)((camry_tp + 0x6c2u) + (uint32_t)(iVar7) * 1u))));
      uVar5 = 0;
      goto LAB_000027c2;
    }
  }
  else if (uVar6 != 3) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6ecf))))) = 0;
    return;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6ece))))) = param_1;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6ecf))))) = 0x52;
  if (uVar6 == 0) {
    boot_transport_receive_complete(channel,'\t');
  }
  if (*(short *)(((undefined *)camry_host_ptr((uint32_t)((camry_tp + 0x6c4u) + (uint32_t)(iVar7) * 1u)))) == 0) {
    send_transport_flow_control_overflow_2636(param_1);
    return;
  }
  uVar3 = *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)((camry_tp + 0x6c4u) + (uint32_t)(iVar7) * 1u))));
  uVar5 = 1;
LAB_000027c2:
  increment_timer_generation_and_arm_transport_slot_1f60(uVar1,uVar5,uVar3);
  return;
}

void validate_and_dispatch_transport_first_frame_27d8(ushort param_1,short param_2,int param_3)

{
  uint uVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  int iVar5;
  
  param_1 = param_1 & 0xff;
  iVar5 = (short)param_1 * 0x18;
  uVar4 = (uint)((*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6b7u) + (uint32_t)(iVar5) * 1u)))) == '\x04');
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6b7u) + (uint32_t)(iVar5) * 1u)))) == '\x04') {
    uVar3 = 7;
  }
  else {
    uVar3 = 8;
  }
  uVar1 = ((*((byte *)camry_host_ptr((uint32_t)(uVar4 + param_3)))) & 0xf) * 0x100 + (uint)(*((byte *)camry_host_ptr((uint32_t)(uVar4 + 1 + param_3))));
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6b6u) + (uint32_t)(iVar5) * 1u)))) == '\x01') && (uVar3 <= uVar1)) && (param_2 == 8)) {
    if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff9131u))))) == 'I' || (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff9131u))))) == 'J') || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff9131u))))) == 'L')) ||
       (((*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff9131u))))) == 'Q' || (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff9131u))))) == 'R' ||
        (((*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff9131u))))) == 'T' || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff9131u))))) == 'a')))))) {
      iVar2 = preempt_receive_if_same_or_higher_priority_route_22ca((*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6bau) + (uint32_t)(iVar5) * 1u)))),param_1);
    }
    else if ((((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff9131u)))))) == -0x77 || ((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff9131u)))))) == -0x76) ||
            ((((((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff9131u)))))) == -0x74 || (((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff9131u)))))) == -0x6f || ((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff9131u)))))) == -0x6e)) ||
              (((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff9131u)))))) == -0x5f || ((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff9131u)))))) == -0x5e)) ||
             (iVar2 = 1, ((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff9131u)))))) == -0x5c)))) {
      iVar2 = preempt_response_for_higher_priority_receive_2350((*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6bau) + (uint32_t)(iVar5) * 1u)))),param_1);
    }
    if (iVar2 == 1) {
      admit_first_request_frame_and_start_receive_state_26d2(param_1, uVar1, ((uchar *)camry_host_ptr((uint32_t)(uVar4 + 2 + param_3))));
    }
  }
  return;
}

void append_consecutive_request_and_update_block_timers_2888(ushort param_1,ushort param_2,uchar *param_3)

{
  undefined1 uVar1;
  ushort channel;
  byte bVar2;
  undefined2 uVar3;
  uint32_t puVar4;
  uchar status;
  uint uVar5;
  int iVar6;
  ushort uStack_22;
  F33BootPduInfo FStack_20;
  
  puVar4 = (camry_gp + 0x0u);
  param_1 = param_1 & 0xff;
  iVar6 = (short)param_1 * 0x18;
  uVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6bau) + (uint32_t)(iVar6) * 1u))));
  channel = (*((ushort *)camry_host_ptr((uint32_t)((camry_tp + 0x6cau) + (uint32_t)((short)param_1 * 6) * 4u))));
  uStack_22 = 0;
  FStack_20.data = camry_host_addr(param_3);
  FStack_20.length = param_2;
  uVar5 = boot_transport_request_append(channel,&FStack_20,&uStack_22);
  if (uVar5 != 0) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6ecf))))) = 0;
    status = '\x01';
LAB_000028d8:
    boot_transport_receive_complete(channel,status);
    return;
  }
  if ((*((ushort *)camry_host_ptr((uint32_t)(puVar4 + -0x6ed4)))) <= param_2) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6ecf))))) = 0;
    status = '\0';
    goto LAB_000028d8;
  }
  (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + -0x6ed4)))) = (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + -0x6ed4)))) - param_2;
  bVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6bdu) + (uint32_t)(iVar6) * 1u))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6ecd))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6ecd))))) + 1 & 0xf;
  if (bVar2 != 0) {
    if (bVar2 <= (byte)((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6ecc))))) + 1)) {
      if (*(short *)(((undefined *)camry_host_ptr((uint32_t)((camry_tp + 0x6c4u) + (uint32_t)(iVar6) * 1u)))) == 0) {
        query_receive_capacity_or_schedule_flow_control_2594(uVar1,param_1);
        return;
      }
      uVar3 = *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)((camry_tp + 0x6c4u) + (uint32_t)(iVar6) * 1u))));
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6ecf))))) = 0x51;
      increment_timer_generation_and_arm_transport_slot_1f60(uVar1,1,uVar3);
      uVar3 = *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)((camry_tp + 0x6c2u) + (uint32_t)(iVar6) * 1u))));
      goto LAB_00002936;
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6ecc))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6ecc))))) + 1;
  }
  uVar3 = *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)((camry_tp + 0x6c6u) + (uint32_t)(iVar6) * 1u))));
LAB_00002936:
  increment_timer_generation_and_arm_transport_slot_1f60(uVar1,0,uVar3);
  return;
}

void validate_consecutive_request_sequence_and_dispatch_2946(ushort param_1,uint param_2,int param_3)

{
  byte bVar1;
  byte bVar2;
  ushort channel;
  uint uVar3;
  uint32_t puVar4;
  uint uVar5;
  uint uVar6;
  int iVar7;
  uint uVar8;
  
  puVar4 = (camry_gp + 0x0u);
  param_1 = param_1 & 0xff;
  iVar7 = (short)param_1 * 0x18;
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6b6u) + (uint32_t)(iVar7) * 1u)))) == '\x01') && ((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9131u)))) == 'a')) && (param_1 == (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9132u)))))) {
    uVar5 = (uint)(*((volatile uint16_t *)camry_host_ptr((camry_gp + 0xffff912cu))));
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6b7u) + (uint32_t)(iVar7) * 1u)))) == '\x04') {
      uVar6 = 6;
    }
    else {
      uVar6 = 7;
    }
    uVar3 = 8;
    uVar8 = (uint)((*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6b7u) + (uint32_t)(iVar7) * 1u)))) == '\x04');
    if (uVar5 < uVar6) {
      uVar3 = uVar8 + uVar5 + 1 & 0xffff;
      uVar6 = uVar5;
    }
    if (uVar3 <= (param_2 & 0xffff)) {
      bVar2 = (*((byte *)camry_host_ptr((uint32_t)(uVar8 + param_3))));
      bVar1 = (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9133u)))) + 1;
      disarm_indexed_timer_slot_1d70((*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6b0u) + (uint32_t)((uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6bau) + (uint32_t)(iVar7) * 1u)))) * 2) * 1u)))));
      if ((bVar2 & 0xf) == (bVar1 & 0xf)) {
        append_consecutive_request_and_update_block_timers_2888(param_1, uVar6, ((uchar *)camry_host_ptr((uint32_t)(uVar8 + 1 + param_3))));
      }
      else {
        channel = (*((ushort *)camry_host_ptr((uint32_t)(&(*((volatile uint32_t *)camry_host_ptr((camry_tp + 0x6cau)))) + (short)param_1 * 6))));
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6ecf))))) = 0;
        boot_transport_receive_complete(channel,'\x05');
      }
    }
  }
  return;
}

void store_block_size_and_normalize_separation_time_29e4(undefined4 param_1,undefined1 param_2,byte param_3)

{
  if (((((int8_t)(*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9131u))))) == -0x6f) && ((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9135u)))) = param_2, (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9136u)))) = param_3, 0x7f < param_3))
     && ((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9136u)))) = 1, 8 < param_3 - 0xf1)) {
    (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9136u)))) = 0x7f;
  }
  return;
}

void poll_response_capacity_and_schedule_next_frame_2a12(undefined1 param_1,uint param_2,short param_3)

{
  int iVar1;
  uint32_t puVar2;
  undefined4 uVar3;
  uint uVar4;
  ushort uVar5;
  ushort uVar6;
  ushort uStack_22;
  F33BootPduInfo FStack_20;
  
  puVar2 = (camry_gp + 0x0u);
  param_2 = param_2 & 0xff;
  iVar1 = param_2 * 0x10;
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6e4u) + (uint32_t)(iVar1) * 1u)))) == '\x04') {
    uVar5 = 6;
  }
  else {
    uVar5 = 7;
  }
  uStack_22 = 0;
  FStack_20.length = 0;
  uVar6 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff912cu)))));
  if (uVar5 <= (*((volatile uint16_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff912cu)))))) {
    uVar6 = uVar5;
  }
  FStack_20.data = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff9131u))))) = 0xa4;
  uVar4 = boot_transport_response_copy((ushort)param_2,&FStack_20,0,&uStack_22);
  if (uVar4 == 0) {
    if (uStack_22 < uVar6) {
LAB_00002a8e:
      if (*(short *)(((undefined *)camry_host_ptr((uint32_t)((camry_tp + 0x6eeu) + (uint32_t)(iVar1) * 1u)))) == 0) goto LAB_00002aba;
      if (param_3 != 0) {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6ecf))))) = 0xa2;
        increment_timer_generation_and_arm_transport_slot_1f60(param_1,1,param_3);
      }
      param_3 = *(short *)(((undefined *)camry_host_ptr((uint32_t)((camry_tp + 0x6eeu) + (uint32_t)(iVar1) * 1u))));
      uVar3 = 0;
    }
    else {
      if (param_3 == 0) {
        send_transport_consecutive_response_frame_20e4(param_2);
        return;
      }
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6ecf))))) = 0xa1;
      uVar3 = 1;
    }
    increment_timer_generation_and_arm_transport_slot_1f60(param_1,uVar3,param_3);
  }
  else {
    if (uVar4 == 2) goto LAB_00002a8e;
LAB_00002aba:
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6ecf))))) = 0;
    boot_transport_response_complete((ushort)param_2,'\x01');
  }
  return;
}

void reset_response_block_count_and_resume_2aca(undefined1 param_1)

{
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff9134u))))) = 0;
  poll_response_capacity_and_schedule_next_frame_2a12(param_1,(*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff9132u))))),(*((volatile uint16_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6f0u))))));
  return;
}

void handle_transport_flow_control_frame_2ae4(ushort param_1,ushort param_2,int param_3)

{
  byte bVar1;
  byte bVar2;
  ushort uVar3;
  uint32_t puVar4;
  F33BootInterruptEntry *pFVar5;
  uchar status;
  uint uVar6;
  uint uVar7;
  int iVar8;
  
  bVar2 = (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9132u))));
  puVar4 = (camry_gp + 0x0u);
  pFVar5 = ((volatile F33BootInterruptEntry *)camry_host_ptr((camry_tp + 0x0u)));
  iVar8 = (short)(param_1 & 0xff) * 0x18;
  uVar6 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6bau) + (uint32_t)(iVar8) * 1u))));
  if (((int8_t)(*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9131u))))) != -0x6f && ((int8_t)(*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9131u))))) != -0x6e) {
    return;
  }
  if ((param_1 & 0xff) != (ushort)(*((volatile uint8_t *)camry_host_ptr((camry_tp + 0x6e9u))))) {
    return;
  }
  uVar7 = (uint)((*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6b7u) + (uint32_t)(iVar8) * 1u)))) == '\x04');
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6b7u) + (uint32_t)(iVar8) * 1u)))) == '\x04') {
    uVar3 = 4;
  }
  else {
    uVar3 = 3;
  }
  if (param_2 < uVar3) {
    return;
  }
  disarm_indexed_timer_slot_1d70((*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6b0u) + (uint32_t)(uVar6 * 2) * 1u)))));
  bVar1 = (*((byte *)camry_host_ptr((uint32_t)(uVar7 + param_3))));
  if (0x2f < bVar1) {
    if (bVar1 == 0x30) {
      store_block_size_and_normalize_separation_time_29e4(uVar6,(*((undefined1 *)camry_host_ptr((uint32_t)(uVar7 + 1 + param_3)))),(*((undefined1 *)camry_host_ptr((uint32_t)(uVar7 + 2 + param_3)))));
      reset_response_block_count_and_resume_2aca(uVar6);
      return;
    }
    if (bVar1 < 0x32) {
      increment_timer_generation_and_arm_transport_slot_1f60(uVar6,0,*(undefined2 *)&pFVar5[0xdd].handler);
      return;
    }
    if (bVar1 == 0x32) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6ecf))))) = 0;
      status = '\t';
      goto LAB_00002b82;
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6ecf))))) = 0;
  status = '\x06';
LAB_00002b82:
  boot_transport_response_complete((ushort)bVar2,status);
  return;
}

void boot_transport_receive_frame(ushort selector,F33BootPduInfo *pdu)

{
  camry_write32((camry_sp - 4u) & ~3u, camry_gpr[28]);
  camry_write32((camry_sp - 8u) & ~3u, camry_gpr[29]);
  camry_write32((camry_sp - 12u) & ~3u, camry_gpr[31]);
  camry_sp -= 16u;
  camry_gpr[3] = camry_sp;

  F33BootInterruptEntry *pFVar1;
  uint uVar2;
  uint32_t puVar3;
  uint uVar4;
  char *camry_boot_frame_type = (char *)camry_host_ptr(camry_sp + 3u);
  
  pFVar1 = ((volatile F33BootInterruptEntry *)camry_host_ptr((camry_tp + 0x0u)));
  uVar4 = (uint)pdu->length;
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff9130u))))) != '\0') && (selector < 2)) && (uVar4 - 2 < 7)) {
    puVar3 = ((uint32_t)(pdu->data));
    (*camry_boot_frame_type) = -0x10;
    uVar2 = (camry_gpr[28] = (puVar3), camry_gpr[29] = uVar4, camry_gpr[6] = selector, camry_r7 = camry_gpr[7] = camry_gpr[28], camry_gpr[8] = camry_sp + 3u, camry_gpr[31] = 0x2bbau, find_receive_route_and_extract_frame_nibble_2284)(selector, ((byte *)camry_host_ptr((uint32_t)(puVar3))), &(*camry_boot_frame_type));
    if ((uVar2 < 2) &&
       (((*((char *)((uint8_t *)&pFVar1[(short)uVar2 * 3 + 0xd7].eiic + (1)))) == '\0' || (uVar4 == 8)))) {
      if ((*camry_boot_frame_type) == '\0') {
        (camry_gpr[6] = uVar2, camry_r7 = camry_gpr[7] = uVar4, camry_gpr[8] = (puVar3), camry_gpr[31] = 0x2bfeu, validate_and_dispatch_transport_single_frame_242a)(uVar2,uVar4,puVar3);
      }
      else if ((*camry_boot_frame_type) == '\x10') {
        (camry_gpr[6] = uVar2, camry_r7 = camry_gpr[7] = uVar4, camry_gpr[8] = (puVar3), camry_gpr[31] = 0x2c08u, validate_and_dispatch_transport_first_frame_27d8)(uVar2,uVar4,puVar3);
      }
      else if ((*camry_boot_frame_type) == ' ') {
        (camry_gpr[6] = uVar2, camry_r7 = camry_gpr[7] = uVar4, camry_gpr[8] = (puVar3), camry_gpr[31] = 0x2c12u, validate_consecutive_request_sequence_and_dispatch_2946)(uVar2,uVar4,puVar3);
      }
      else if ((*camry_boot_frame_type) == '0') {
        (camry_gpr[6] = uVar2, camry_r7 = camry_gpr[7] = uVar4, camry_gpr[8] = (puVar3), camry_gpr[31] = 0x2bf4u, handle_transport_flow_control_frame_2ae4)(uVar2,uVar4,puVar3);
      }
    }
  }
  { if (!camry_halted) { camry_gpr[28] = camry_read32((camry_sp + 12u) & ~3u); camry_gpr[29] = camry_read32((camry_sp + 8u) & ~3u); camry_gpr[31] = camry_read32((camry_sp + 4u) & ~3u); camry_sp += 16u; camry_gpr[3] = camry_sp; } return; }
}

int send_transport_first_response_frame_2c16(ushort param_1,undefined4 param_2)

{
  uint8_t stack_record_26[38];
  bool bVar1;
  int iVar2;
  undefined1 uVar3;
  uint32_t puVar4;
  uint uVar5;
  int iVar6;
  F33BootPduInfo FStack_24;
  
  puVar4 = (camry_gp + 0x0u);
  iVar2 = (uint)param_1 * 0x10;
  iVar6 = 1;
  uVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6e7u) + (uint32_t)(iVar2) * 1u))));
  bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6e4u) + (uint32_t)(iVar2) * 1u)))) == '\x04';
  if (bVar1) {
    ((uint8_t *)((stack_record_26 + 10)))[0] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6e5u) + (uint32_t)(iVar2) * 1u))));
  }
  ((uint8_t *)((stack_record_26 + 10)))[bVar1] = (char)((uint)param_2 >> 8) + '\x10';
  ((uint8_t *)((stack_record_26 + 10)))[bVar1 + 1] = (uchar)param_2;
  FStack_24.data = camry_host_addr(((uint8_t *)((stack_record_26 + 10))) + bVar1 + 2);
  FStack_24.length = 8 - (bVar1 + 2);
  (*((uint16_t *)(stack_record_26 + 0))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff9131u))))) = 0x89;
  uVar5 = boot_transport_response_copy(param_1,&FStack_24,0,stack_record_26);
  if ((uVar5 == 0) && ((*((uint16_t *)(stack_record_26 + 0))) != 0)) {
    FStack_24.data = camry_host_addr(((uint8_t *)((stack_record_26 + 10))));
    FStack_24.length = 8;
    iVar6 = copy_pdu_descriptor_and_submit_1ec0((*((volatile uint16_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6f2u) + (uint32_t)((uint)param_1 * 8) * 2u)))),&FStack_24);
    if (iVar6 == 0) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6ece))))) = (char)param_1;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6ecd))))) = 0;
      (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + -0x6ed4)))) = (*((uint16_t *)(stack_record_26 + 0)));
      increment_timer_generation_and_arm_transport_slot_1f60(uVar3,0,*(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)((camry_tp + 0x6eau) + (uint32_t)(iVar2) * 1u)))));
      return 0;
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6ecf))))) = 0;
  return iVar6;
}

int send_transport_single_response_frame_2cd4(ushort param_1,int param_2)

{
  uint8_t stack_record_2e[46];
  int iVar1;
  undefined1 uVar2;
  undefined2 uVar3;
  uint32_t puVar4;
  uint uVar5;
  int iVar6;
  uint uVar7;
  F33BootPduInfo FStack_2c;
  
  puVar4 = (camry_gp + 0x0u);
  iVar1 = (uint)param_1 * 0x10;
  iVar6 = 1;
  uVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6e7u) + (uint32_t)(iVar1) * 1u))));
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6e4u) + (uint32_t)(iVar1) * 1u)))) == '\x04') {
    ((uint8_t *)((stack_record_2e + 10)))[0] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6e5u) + (uint32_t)(iVar1) * 1u))));
  }
  uVar7 = (uint)((*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6e4u) + (uint32_t)(iVar1) * 1u)))) == '\x04');
  ((uint8_t *)((stack_record_2e + 10)))[uVar7] = (uchar)param_2;
  FStack_2c.length = (ushort)param_2;
  FStack_2c.data = camry_host_addr(((uint8_t *)((stack_record_2e + 10))) + uVar7 + 1);
  (*((uint16_t *)(stack_record_2e + 0))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff9131u))))) = 0x8a;
  uVar5 = boot_transport_response_copy(param_1,&FStack_2c,0,stack_record_2e);
  if ((uVar5 == 0) && ((*((uint16_t *)(stack_record_2e + 0))) == 0)) {
    for (uVar5 = uVar7 + 1 + param_2 & 0xffff; uVar5 < 8; uVar5 = uVar5 + 1) {
      ((uint8_t *)((stack_record_2e + 10)))[uVar5] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6e6u) + (uint32_t)(iVar1) * 1u))));
    }
    FStack_2c.data = camry_host_addr(((uint8_t *)((stack_record_2e + 10))));
    FStack_2c.length = 8;
    iVar6 = copy_pdu_descriptor_and_submit_1ec0((*((volatile uint16_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6f2u) + (uint32_t)((uint)param_1 * 8) * 2u)))),&FStack_2c);
    if (iVar6 == 0) {
      uVar3 = *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)((camry_tp + 0x6eau) + (uint32_t)(iVar1) * 1u))));
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6ece))))) = (char)param_1;
      increment_timer_generation_and_arm_transport_slot_1f60(uVar2,0,uVar3);
      return 0;
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6ecf))))) = 0;
  return iVar6;
}

undefined4 start_response_if_enabled_without_busy_state_2d88(short param_1,int param_2)

{
  char cVar1;
  uint uVar2;
  undefined4 uVar3;
  uint uVar4;
  
  uVar4 = (uint)(*((ushort *)camry_host_ptr((uint32_t)(param_2 + 4))));
  uVar3 = 1;
  if (((((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9130u)))) != '\0') && (param_1 == 0)) && (uVar4 - 1 < 0xfff)) &&
     ((cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff9131u) + (uint32_t)((*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6e7u)))))) * 1u)))), cVar1 == '\0' ||
      ((((cVar1 != 'I' && (cVar1 != 'J')) && ((cVar1 != 'L' && ((cVar1 != 'Q' && (cVar1 != 'R'))))))
       && ((cVar1 != 'T' &&
           ((((((cVar1 != 'a' && (((int8_t)cVar1) != -0x77)) && (((int8_t)cVar1) != -0x76)) &&
              ((((int8_t)cVar1) != -0x74 && (((int8_t)cVar1) != -0x6f)))) &&
             ((((int8_t)cVar1) != -0x6e && ((((int8_t)cVar1) != -0x5f && (((int8_t)cVar1) != -0x5e)))))) && (((int8_t)cVar1) != -0x5c)))))))
      ))) {
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6e4u))))) == '\x04') {
      uVar2 = 6;
    }
    else {
      uVar2 = 7;
    }
    if (uVar2 < uVar4) {
      uVar3 = send_transport_first_response_frame_2c16((uint)(ushort)param_1, (*((volatile uint16_t *)(((uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(param_2) + (uint32_t)((4)) * 1u)))))));
    }
    else {
      uVar3 = send_transport_single_response_frame_2cd4(0,uVar4);
    }
  }
  return uVar3;
}

undefined1 classify_transport_confirmation_route_2e32(short param_1)

{
  undefined1 uVar1;
  
  uVar1 = 1;
  if (((*((volatile uint16_t *)camry_host_ptr((camry_tp + 0x6f2u)))) == param_1) &&
     ((((((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9131u)))) != 'I' && ((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9131u)))) != 'J')) && ((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9131u)))) != 'L')) &&
       (((((int8_t)(*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9131u))))) != -0x76 && (((int8_t)(*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9131u))))) != -0x77)) && (((int8_t)(*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9131u))))) != -0x74)))) ||
      (uVar1 = (*((volatile uint8_t *)camry_host_ptr((camry_tp + 0x6e7u)))), param_1 != (*((volatile uint16_t *)camry_host_ptr((camry_tp + 0x6f2u)))))))) {
    uVar1 = 1;
  }
  return uVar1;
}

void resume_receive_after_wait_confirmation_2e86(undefined1 param_1)

{
  int iVar1;
  
  iVar1 = (short)(ushort)(*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9132u)))) * 0x18;
  if (*(short *)(((undefined *)camry_host_ptr((uint32_t)((camry_tp + 0x6c4u) + (uint32_t)(iVar1) * 1u)))) == 0) {
    query_receive_capacity_or_schedule_flow_control_2594(param_1, *((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9132u))));
  }
  else {
    (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9131u)))) = 0x51;
    increment_timer_generation_and_arm_transport_slot_1f60(param_1,1,*(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)((camry_tp + 0x6c4u) + (uint32_t)(iVar1) * 1u)))));
    increment_timer_generation_and_arm_transport_slot_1f60(param_1,0,*(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)((camry_tp + 0x6c2u) + (uint32_t)(iVar1) * 1u)))));
  }
  return;
}

void complete_or_continue_response_after_frame_2ecc(undefined1 param_1)

{
  if ((*((volatile uint16_t *)camry_host_ptr((camry_gp + 0xffff912cu)))) == 0) {
    (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9131u)))) = 0;
    boot_transport_response_complete((ushort)(*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9132u)))),'\0');
  }
  else if (((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9135u)))) == 0) || ((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9134u)))) < (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9135u)))))) {
    poll_response_capacity_and_schedule_next_frame_2a12(param_1,(*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9132u)))),(*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9136u)))));
  }
  else {
    (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9131u)))) = 0x92;
    increment_timer_generation_and_arm_transport_slot_1f60(param_1,0,(*((volatile uint16_t *)camry_host_ptr((camry_tp + 0x6ecu)))));
  }
  return;
}

void advance_transport_on_transmit_confirmation_2f1c(undefined2 param_1)

{
  char cVar1;
  undefined2 uVar2;
  uint32_t puVar3;
  F33BootInterruptEntry *pFVar4;
  int iVar5;
  
  puVar3 = (camry_gp + 0x0u);
  pFVar4 = ((volatile F33BootInterruptEntry *)camry_host_ptr((camry_tp + 0x0u)));
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff9130u))))) == '\0') {
    return;
  }
  iVar5 = classify_transport_confirmation_route_2e32(param_1);
  if (iVar5 != 0) {
    return;
  }
  disarm_indexed_timer_slot_1d70((char)pFVar4[0xd6].eiic);
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6ecf)))));
  if (cVar1 == 'I') {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6ecf))))) = 0x61;
    uVar2 = (*((undefined2 *)((uint8_t *)&pFVar4[(short)(ushort)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6ece))))) * 3 + 0xd8].handler + (2))));
  }
  else {
    if (cVar1 == 'J') {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6ecf))))) = 0;
      return;
    }
    if (cVar1 == 'L') {
      resume_receive_after_wait_confirmation_2e86(0);
      return;
    }
    if (((int8_t)cVar1) != -0x77) {
      if (((int8_t)cVar1) == -0x76) {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6ecf))))) = 0;
        boot_transport_response_complete((ushort)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6ece))))),'\0');
        return;
      }
      if (((int8_t)cVar1) != -0x74) {
        return;
      }
      complete_or_continue_response_after_frame_2ecc(0);
      return;
    }
    uVar2 = *(undefined2 *)&pFVar4[0xdd].handler;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6ecf))))) = 0x91;
  }
  increment_timer_generation_and_arm_transport_slot_1f60(0,0,uVar2);
  return;
}

void dispatch_transport_secondary_timer_event_2fb8(undefined1 param_1)

{
  if ((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9131u)))) == 'Q') {
    poll_receive_capacity_and_send_flow_control_2046(param_1);
  }
  else if ((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9131u)))) == 'R') {
    send_transport_flow_control_overflow_2636((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9132u)))));
  }
  else if (((int8_t)(*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9131u))))) == -0x5f) {
    send_transport_consecutive_response_frame_20e4((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9132u)))));
  }
  else if (((int8_t)(*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9131u))))) == -0x5e) {
    (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9131u)))) = -0x5c;
  }
  return;
}
