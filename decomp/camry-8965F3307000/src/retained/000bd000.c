#include "common.h"

int load_record8_fields_and_mark_initialized_bd81e(void)

{
  uint8_t stack_record_c[12];
  undefined1 uVar1;
  uint32_t puVar2;
  int iVar3;
  
  puVar2 = 0xfebeb800u;
  (*((uint32_t *)(stack_record_c + 0))) = DAT_0001be74;
  (*((uint32_t *)(stack_record_c + 4))) = DAT_0001be78;
  iVar3 = call_nvm_get_record_with_u16_selector_ff0b0(8,stack_record_c);
  if (iVar3 == 0x10) {
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + -0x8fc)))) = (*((uint32_t *)(stack_record_c + 0)));
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x9f2)))) = (undefined2)(*((uint32_t *)(stack_record_c + 4)));
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0xb14))))) = (*((uint8_t *)((uint8_t *)(stack_record_c + 4) + 2u)));
    uVar1 = (*((uint8_t *)((uint8_t *)(stack_record_c + 4) + 2u)));
  }
  else {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0xb14))))) = 0;
    uVar1 = 0;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0xb13))))) = uVar1;
  call_snapshot_retained_estimator_projection_d1160();
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0xb12))))) = 0x5a;
  return iVar3;
}

void set_acec_and_refresh_d1160_bd86e(undefined1 param_1)

{
  DAT_febeacec = param_1;
  call_snapshot_retained_estimator_projection_d1160();
  return;
}

undefined4 write_record8_current_fields_when_initialized_bd87e(void)

{
  uint8_t stack_record_c[12];
  uint32_t puVar1;
  
  puVar1 = 0xfebeb800u;
  if (DAT_febeacee != '\0') {
    call_publish_retained_estimator_projection_d1154();
    (*((uint32_t *)(stack_record_c + 0))) = (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x8fc))));
    stack_record_c[7] = 0;
    (*((uint16_t *)(stack_record_c + 4))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x9f2))));
    stack_record_c[6] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xb14)))));
    call_nvm_set_record_with_u16_selector_ff09c(8,stack_record_c);
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xb15))))) = 0x5a;
  }
  return 1;
}

undefined4 clear_acec_and_write_record8_when_initialized_bd8ba(void)

{
  uint8_t stack_record_c[12];
  
  if (DAT_febeacee != '\0') {
    DAT_febeacec = 0;
    stack_record_c[6] = 0;
    stack_record_c[7] = 0;
    (*((uint32_t *)(stack_record_c + 0))) = DAT_febeaf04;
    (*((uint16_t *)(stack_record_c + 4))) = DAT_febeae0e;
    call_nvm_set_record_with_u16_selector_ff09c(8,stack_record_c);
  }
  return 1;
}

undefined4 pack_and_write_record9_configuration_fields_bd8ea(void)

{
  uint8_t stack_record_2c[44];
  uint32_t puVar1;
  
  puVar1 = 0xfebeb800u;
  thunk_publish_retained_cell_and_event_channel_snapshots_d0d6c();
  stack_record_2c[4] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xb0b)))));
  stack_record_2c[3] = 0;
  stack_record_2c[31] = 0;
  stack_record_2c[0] = (undefined1)(*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x9f0))));
  stack_record_2c[1] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xb11)))));
  stack_record_2c[39] = 0;
  stack_record_2c[5] = (undefined1)(*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x9ec))));
  stack_record_2c[6] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xb0e)))));
  stack_record_2c[2] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xb10)))));
  stack_record_2c[7] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xb0d)))));
  stack_record_2c[8] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xb0c)))));
  stack_record_2c[9] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xb00)))));
  stack_record_2c[10] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xaff)))));
  stack_record_2c[11] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xafe)))));
  (*((uint16_t *)(stack_record_2c + 20))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x9ea))));
  stack_record_2c[12] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xaf6)))));
  stack_record_2c[13] = (undefined1)(*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x9d4))));
  stack_record_2c[14] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xaf4)))));
  stack_record_2c[15] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xaf3)))));
  stack_record_2c[16] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xaf2)))));
  stack_record_2c[17] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xaf1)))));
  stack_record_2c[18] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xaf0)))));
  stack_record_2c[19] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xaef)))));
  (*((uint16_t *)(stack_record_2c + 22))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x9ca))));
  stack_record_2c[24] = (undefined1)(*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x996))));
  stack_record_2c[25] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xa9e)))));
  stack_record_2c[26] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xa9d)))));
  stack_record_2c[27] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xa9f)))));
  stack_record_2c[28] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xa9b)))));
  stack_record_2c[29] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xa9a)))));
  stack_record_2c[30] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xa9c)))));
  stack_record_2c[32] = (undefined1)(*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x994))));
  stack_record_2c[33] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xa97)))));
  stack_record_2c[34] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xa96)))));
  stack_record_2c[35] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xa98)))));
  stack_record_2c[36] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xa94)))));
  stack_record_2c[37] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xa93)))));
  stack_record_2c[38] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xa95)))));
  call_nvm_set_record_with_u16_selector_ff09c(9,stack_record_2c);
  return 1;
}

uint32_t load_or_clear_record9_configuration_fields_bd9da(void)

{
  uint32_t camry_r10_result;
  uint8_t stack_record_2c[44];
  undefined2 uVar1;
  byte *pbVar2;
  uint32_t puVar3;
  int iVar4;
  undefined4 *puVar5;
  
  puVar3 = 0xfebeb800u;
  pbVar2 = ((uint8_t *)(stack_record_2c));
  puVar5 = (undefined4 *)((undefined *)camry_host_ptr(0x1be7cu));
  do {
    uVar1 = *(undefined2 *)puVar5;
    puVar5 = ((undefined4 *)camry_host_ptr((uint32_t)((int)camry_host_addr(puVar5) + 2)));
    *(undefined2 *)pbVar2 = uVar1;
    pbVar2 = ((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(pbVar2) + 2)));
  } while (camry_host_addr(puVar5)!=((uint32_t)(0x1bea4u)));
  iVar4 = (camry_r10_result = call_nvm_get_record_with_u16_selector_ff0b0(9,((uint8_t *)(stack_record_2c))));
  if (iVar4 == 0x11) {
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x9f0)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xb11))))) = 0;
    stack_record_2c[38] = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xb10))))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xb0b))))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xb0e))))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xb0d))))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xb0c))))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xb00))))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xaff))))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xafe))))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xaf6))))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xaf4))))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xaf3))))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xaf2))))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xaf1))))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xaf0))))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xaef))))) = 0;
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x9ec)))) = 0;
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x9ca)))) = 0;
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x996)))) = 0;
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x9ea)))) = 0;
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x9d4)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xa9e))))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xa9d))))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xa9f))))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xa9b))))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xa9a))))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xa9c))))) = 0;
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x994)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xa97))))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xa96))))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xa98))))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xa94))))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xa93))))) = 0;
  }
  else {
    (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x9f0)))) = (ushort)stack_record_2c[0];
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xb11))))) = stack_record_2c[1];
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xb10))))) = stack_record_2c[2];
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xb0b))))) = stack_record_2c[4];
    (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x9ec)))) = (ushort)stack_record_2c[5];
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xb0e))))) = stack_record_2c[6];
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xb0d))))) = stack_record_2c[7];
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xb0c))))) = stack_record_2c[8];
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xb00))))) = stack_record_2c[9];
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xaff))))) = stack_record_2c[10];
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xafe))))) = stack_record_2c[11];
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x9ea)))) = (*((uint16_t *)(stack_record_2c + 20)));
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xaf6))))) = stack_record_2c[12];
    (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x9d4)))) = (ushort)stack_record_2c[13];
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xaf4))))) = stack_record_2c[14];
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xaf3))))) = stack_record_2c[15];
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xaf2))))) = stack_record_2c[16];
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xaf1))))) = stack_record_2c[17];
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xaf0))))) = stack_record_2c[18];
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xaef))))) = stack_record_2c[19];
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x9ca)))) = (*((uint16_t *)(stack_record_2c + 22)));
    (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x996)))) = (ushort)stack_record_2c[24];
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xa9e))))) = stack_record_2c[25];
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xa9d))))) = stack_record_2c[26];
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xa9f))))) = stack_record_2c[27];
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xa9b))))) = stack_record_2c[28];
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xa9a))))) = stack_record_2c[29];
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xa9c))))) = stack_record_2c[30];
    (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x994)))) = (ushort)stack_record_2c[32];
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xa97))))) = stack_record_2c[33];
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xa96))))) = stack_record_2c[34];
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xa98))))) = stack_record_2c[35];
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xa94))))) = stack_record_2c[36];
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xa93))))) = stack_record_2c[37];
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xa95))))) = stack_record_2c[38];
  return camry_r10_result;
}

undefined4 prepare_d113c_and_write_record9_configuration_bdb48(void)

{
  thunk_clear_retained_cell_and_event_channel_state_d10e4();
  return pack_and_write_record9_configuration_fields_bd8ea();
}

void report_diagnostic_event_failure_ffff_32_bdb64(uint param_1)

{
  report_diagnostic_event_failure(param_1 & 0xffff,0x32);
  return;
}

uchar get_application_grouped_status(uint selector)

{
  uchar uVar1;
  
  uVar1 = get_grouped_status_byte(selector & 0xff);
  return uVar1;
}

void return_only_stub_bdb84(void)

{
  return;
}

void return_only_stub_bdb86(void)

{
  return;
}

void return_only_stub_bdb88(void)

{
  return;
}

void return_only_stub_bdb8a(void)

{
  return;
}

void return_only_stub_bdb8c(void)

{
  return;
}

void clear_byte_febebe1c_bdb8e(void)

{
  DAT_febebe1c = 0;
  return;
}

void return_only_stub_bdb94(void)

{
  return;
}

void return_only_stub_bdb96(void)

{
  return;
}

void clear_four_bytes_febebe20_to_be23_bdb98(void)

{
  DAT_febebe20 = 0;
  DAT_febebe21 = 0;
  DAT_febebe22 = 0;
  DAT_febebe23 = 0;
  return;
}

void return_only_stub_bdba6(void)

{
  return;
}

void fill_constant_block_bdba8(void)

{
  DAT_febebe28 = 0;
  DAT_febebe2a = 0;
  DAT_febebe2c = 0;
  DAT_febebe2e = 0;
  DAT_febebe30 = 0;
  DAT_febebe24 = 0;
  DAT_febebe25 = 0;
  DAT_febebe26 = 0;
  return;
}

uint write_record11_be28_be2a_snapshot_bdbbe(void)

{
  uint8_t stack_record_c[12];
  
  (*((uint16_t *)(stack_record_c + 0))) = DAT_febebe28;
  (*((uint32_t *)(stack_record_c + 4))) = 0;
  (*((uint16_t *)(stack_record_c + 2))) = DAT_febebe2a;
  return call_nvm_set_record_with_u16_selector_ff09c(0xb,stack_record_c);
}

void debounce_three_states_and_persist_b11a_b080_bdbe0(void)

{
  ushort uVar1;
  uint32_t puVar2;
  char cVar3;
  char cVar4;
  char cVar5;
  ushort uVar6;
  ushort uVar7;
  ushort uVar8;
  
  uVar6 = DAT_febebe30;
  uVar7 = DAT_febebe2e;
  uVar8 = DAT_febebe2c;
  cVar3 = DAT_febebe26;
  cVar4 = DAT_febebe25;
  cVar5 = DAT_febebe24;
  puVar2 = 0xfebeb800u;
  uVar1 = DAT_febeb11a & 0xff00;
  if (DAT_febeb20e == '\0') {
    if ((uVar1 == 0x100) || (uVar1 == 0x200)) {
      if (((DAT_000af0f4 < DAT_febebe2c) || (uVar8 = DAT_febebe2c + 1, DAT_000af0f4 < uVar8)) &&
         (DAT_febebe24 != 'Z')) {
        DAT_febebe28 = DAT_febeb11a;
        DAT_febebe2a = DAT_febeb080;
        puVar2 = 0xfebeb800u;
        write_record11_be28_be2a_snapshot_bdbbe();
        cVar5 = 'Z';
      }
      goto LAB_000bdca4;
    }
  }
  else {
    if (DAT_febeb20e != '\x11') {
      if ((DAT_febeb20e == '\"') &&
         (((DAT_000af0f8 < DAT_febebe30 || (uVar6 = DAT_febebe30 + 1, DAT_000af0f8 < uVar6)) &&
          (DAT_febebe26 != 'Z')))) {
        DAT_febebe28 = DAT_febeb11a;
        DAT_febebe2a = DAT_febeb080;
        puVar2 = 0xfebeb800u;
        write_record11_be28_be2a_snapshot_bdbbe();
        cVar3 = 'Z';
      }
      goto LAB_000bdca4;
    }
    if (uVar1 != 0x700) {
      if (((DAT_000af0f6 < DAT_febebe2e) || (uVar7 = DAT_febebe2e + 1, DAT_000af0f6 < uVar7)) &&
         (DAT_febebe25 != 'Z')) {
        DAT_febebe28 = DAT_febeb11a;
        DAT_febebe2a = DAT_febeb080;
        puVar2 = 0xfebeb800u;
        write_record11_be28_be2a_snapshot_bdbbe();
        cVar4 = 'Z';
      }
      goto LAB_000bdca4;
    }
  }
  uVar8 = 0;
  uVar7 = 0;
  uVar6 = 0;
LAB_000bdca4:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x624))))) = cVar5;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x625))))) = cVar4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x626))))) = cVar3;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0x62c)))) = uVar8;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0x62e)))) = uVar7;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0x630)))) = uVar6;
  return;
}

undefined4 read_record11_and_encode_big_endian_halfwords_bdcb8(undefined4 param_1)

{
  uint8_t stack_record_10[16];
  uint uVar1;
  uint uVar2;
  int iVar3;
  
  (*((uint32_t *)(stack_record_10 + 0))) = DAT_0001bea4;
  (*((uint32_t *)(stack_record_10 + 4))) = DAT_0001bea8;
  iVar3 = call_nvm_get_record_with_u16_selector_ff0b0(0xb,stack_record_10);
  if (iVar3 == 0x10) {
    uVar1 = (*((uint32_t *)(stack_record_10 + 0))) & 0xffff;
    uVar2 = (*((uint32_t *)(stack_record_10 + 0))) >> 0x10;
  }
  else {
    if (iVar3 != 0x11) {
      return 0xfffffff7;
    }
    uVar1 = 0;
    uVar2 = uVar1;
  }
  pack_two_low_words_as_big_endian_bytes_d11d6(uVar1, uVar2, ((undefined1 *)camry_host_ptr((uint32_t)(param_1))));
  return 4;
}

uint clear_be28_be2a_and_write_zero_record11_bdcfe(void)

{
  uint8_t stack_record_c[12];
  
  DAT_febebe28 = 0;
  DAT_febebe2a = 0;
  (*((uint16_t *)(stack_record_c + 0))) = 0;
  (*((uint16_t *)(stack_record_c + 2))) = 0;
  (*((uint32_t *)(stack_record_c + 4))) = 0;
  return call_nvm_set_record_with_u16_selector_ff09c(0xb,stack_record_c);
}

void return_only_stub_bdd20(void)

{
  return;
}

int load_or_clear_record15_paired_snapshots_bdd22(void)

{
  uint8_t stack_record_20[32];
  undefined4 *puVar1;
  uint32_t puVar2;
  int iVar3;
  undefined4 uVar4;
  undefined4 *puVar5;
  
  puVar2 = 0xfebeb800u;
  puVar1 = stack_record_20;
  puVar5 = ((undefined *)camry_host_ptr(0x1beacu));
  do {
    uVar4 = *puVar5;
    puVar5 = puVar5 + 1;
    *puVar1 = uVar4;
    puVar1 = puVar1 + 1;
  } while (camry_host_addr(puVar5)!=((uint32_t)(0x1bec4u)));
  iVar3 = call_nvm_get_record_with_u16_selector_ff0b0(0xf,stack_record_20);
  if (iVar3 == 0x11) {
    DAT_febebe36 = 0;
    DAT_febebe34 = 0;
    (*((uint16_t *)(stack_record_20 + 22))) = 0;
    DAT_febebe42 = 0;
    DAT_febebe4c = 0;
    DAT_febebe3a = 0;
    DAT_febebe3e = 0;
    DAT_febebe37 = 0;
    DAT_febebe35 = 0;
    DAT_febebe44 = 0;
    DAT_febebe50 = 0;
    DAT_febebe3c = 0;
  }
  else {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x636))))) = (undefined1)(*((uint32_t *)(stack_record_20 + 0)));
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x634))))) = (*((uint8_t *)((uint8_t *)stack_record_20 + 1u)));
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + 0x642)))) = (*((uint16_t *)((uint8_t *)stack_record_20 + 2u)));
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0x64c)))) = (*((uint32_t *)(stack_record_20 + 4)));
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + 0x63a)))) = (*((uint16_t *)(stack_record_20 + 8)));
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + 0x63e)))) = (*((uint16_t *)(stack_record_20 + 10)));
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x637))))) = stack_record_20[12];
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x635))))) = stack_record_20[13];
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + 0x644)))) = (*((uint16_t *)(stack_record_20 + 14)));
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0x650)))) = (*((uint32_t *)(stack_record_20 + 16)));
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + 0x63c)))) = (*((uint16_t *)(stack_record_20 + 20)));
  }
  DAT_febebe40 = (*((uint16_t *)(stack_record_20 + 22)));
  return iVar3;
}

uint pack_and_write_record15_paired_snapshots_bddba(void)

{
  uint8_t stack_record_1c[28];
  
  stack_record_1c[0] = DAT_febebe36;
  stack_record_1c[1] = DAT_febebe34;
  (*((uint16_t *)(stack_record_1c + 2))) = DAT_febebe42;
  (*((uint32_t *)(stack_record_1c + 4))) = DAT_febebe4c;
  (*((uint16_t *)(stack_record_1c + 8))) = DAT_febebe3a;
  (*((uint16_t *)(stack_record_1c + 10))) = DAT_febebe3e;
  stack_record_1c[12] = DAT_febebe37;
  stack_record_1c[13] = DAT_febebe35;
  (*((uint16_t *)(stack_record_1c + 14))) = DAT_febebe44;
  (*((uint32_t *)(stack_record_1c + 16))) = DAT_febebe50;
  (*((uint16_t *)(stack_record_1c + 20))) = DAT_febebe3c;
  (*((uint16_t *)(stack_record_1c + 22))) = DAT_febebe40;
  return call_nvm_set_record_with_u16_selector_ff09c(0xf,stack_record_1c);
}

void capture_two_debounced_received_word_snapshots_bde16(void)

{
  char cVar1;
  char cVar2;
  ushort uVar3;
  ushort uVar4;
  
  uVar3 = DAT_febebe48;
  uVar4 = DAT_febebe46;
  cVar2 = DAT_febebe39;
  cVar1 = DAT_febebe38;
  if (DAT_febeb20e == '\0') {
    if (((DAT_febeb11a & 0xff00) != 0x100) && ((DAT_febeb11a & 0xff00) != 0x200)) {
      DAT_febebe48 = 0;
      return;
    }
  }
  else {
    if (DAT_febeb20e == '\x11') {
      if (DAT_febeb1d3 != 'Z') {
        DAT_febebe46 = 0;
        return;
      }
      if ((DAT_febeb072 != '\x02') && (DAT_febeb074 != '\x02')) {
        DAT_febebe46 = 0;
        return;
      }
      if (DAT_febeb202 <= DAT_000aef84) {
        DAT_febebe46 = 0;
        return;
      }
      if (DAT_febeb1d2 != '\x11') {
        DAT_febebe46 = 0;
        return;
      }
      if (DAT_febebe48 < DAT_000aef82) {
        DAT_febebe46 = 0;
        DAT_febebe48 = DAT_febebe48 + 1;
        return;
      }
      if (DAT_febebe39 == 'Z') {
        DAT_febebe46 = 0;
        return;
      }
      if (((int8_t)DAT_febebe37) != -1) {
        DAT_febebe37 = DAT_febebe37 + '\x01';
      }
      DAT_febebe3c = DAT_febeb11a;
      DAT_febebe35 = DAT_febebe60;
      DAT_febebe44 = received_retained_word;
      DAT_febebe50 = received_word_unchanged_age;
      DAT_febebe40 = DAT_febeb080;
      pack_and_write_record15_paired_snapshots_bddba();
      DAT_febebe38 = cVar1;
      DAT_febebe39 = 0x5a;
      DAT_febebe46 = 0;
      DAT_febebe48 = uVar3;
      return;
    }
    if (DAT_febeb20e != '\"') {
      DAT_febebe38 = 0;
      DAT_febebe46 = 0;
      DAT_febebe48 = 0;
      return;
    }
  }
  if (DAT_febebe46 < DAT_000aef80) {
    uVar4 = DAT_febebe46 + 1;
  }
  else if (DAT_febebe38 != 'Z') {
    if (((int8_t)DAT_febebe36) != -1) {
      DAT_febebe36 = DAT_febebe36 + '\x01';
    }
    DAT_febebe3a = DAT_febeb11a;
    DAT_febebe34 = DAT_febebe60;
    DAT_febebe42 = received_retained_word;
    DAT_febebe4c = received_word_unchanged_age;
    DAT_febebe3e = DAT_febeb080;
    pack_and_write_record15_paired_snapshots_bddba();
    DAT_febebe38 = 'Z';
  }
  DAT_febebe39 = cVar2;
  DAT_febebe46 = uVar4;
  DAT_febebe48 = 0;
  return;
}

uint clear_paired_snapshot_fields_and_write_zero_record15_bdf24(void)

{
  uint8_t stack_record_1c[28];
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = 0;
  do {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebebe34u + (uint32_t)(iVar3) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebebe36u + (uint32_t)(iVar3) * 1u)))) = 0;
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebebe42u + (uint32_t)(iVar3) * 2u)))) = 0;
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebebe3eu + (uint32_t)(iVar3) * 2u)))) = 0;
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebebe3au + (uint32_t)(iVar3) * 2u)))) = 0;
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebebe4cu + (uint32_t)(iVar3) * 4u)))) = 0;
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -1;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  stack_record_1c[0] = 0;
  stack_record_1c[1] = 0;
  (*((uint16_t *)(stack_record_1c + 2))) = 0;
  (*((uint32_t *)(stack_record_1c + 4))) = 0;
  (*((uint16_t *)(stack_record_1c + 8))) = 0;
  (*((uint16_t *)(stack_record_1c + 10))) = 0;
  stack_record_1c[12] = 0;
  stack_record_1c[13] = 0;
  (*((uint16_t *)(stack_record_1c + 14))) = 0;
  (*((uint32_t *)(stack_record_1c + 16))) = 0;
  (*((uint16_t *)(stack_record_1c + 20))) = 0;
  (*((uint16_t *)(stack_record_1c + 22))) = 0;
  return call_nvm_set_record_with_u16_selector_ff09c(0xf,stack_record_1c);
}

void return_only_stub_bdf7e(void)

{
  return;
}

void return_only_stub_bdf80(void)

{
  return;
}

void return_only_stub_bdf82(void)

{
  return;
}

void return_only_stub_bdfa6(void)

{
  return;
}

void return_only_stub_bdfa8(void)

{
  return;
}

void return_only_stub_bdfaa(void)

{
  return;
}

void snapshot_diagnostic_application_kind10(F33DiagnosticApplicationSample *output)

{
  uchar uVar1;
  undefined2 uVar2;
  undefined2 uVar3;
  short sVar4;
  ushort uVar5;
  uint uVar6;
  
  output->raw[0] = DAT_febebe78;
  *(undefined2 *)(output->raw + 10) = DAT_febebee2;
  *(undefined2 *)(output->raw + 0xc) = DAT_febebe82;
  sVar4 = ((int)(int16_t)DAT_febeaf40);
  *(short *)(output->raw + 0x18) = ((int)(int16_t)DAT_febeaf40);
  uVar2 = DAT_febeb11a;
  output->raw[1] = 0 < sVar4;
  uVar3 = ((int)(int16_t)DAT_febeae6e);
  uVar1 = DAT_febeacf1;
  *(undefined2 *)(output->raw + 0xe) = uVar2;
  output->raw[2] = uVar1;
  uVar2 = ((int)(int16_t)DAT_febeae12);
  *(undefined2 *)(output->raw + 0x14) = uVar3;
  *(undefined2 *)(output->raw + 0x12) = uVar2;
  output->raw[3] = DAT_febeacf5;
  output->raw[4] = DAT_febead0a;
  *(undefined2 *)(output->raw + 0x16) = ((int)(int16_t)DAT_febeae36);
  output->raw[5] = DAT_febeb1c4;
  *(undefined2 *)(output->raw + 0x1a) = ((int)(int16_t)DAT_febeafa4);
  uVar5 = received_retained_word;
  *(undefined2 *)(output->raw + 0x1c) = uVar3;
  *(undefined2 *)(output->raw + 0x1e) = uVar3;
  *(ushort *)(output->raw + 0x10) = uVar5;
  *(uint *)(output->raw + 0x20) = received_word_unchanged_age;
  output->raw[6] = DAT_febebe60;
  output->raw[7] = DAT_febebe62;
  uVar6 = received_typed_scalar;
  output->raw[0x34] = '\0';
  output->raw[0x35] = '\0';
  output->raw[0x36] = '\0';
  output->raw[0x37] = '\0';
  *(uint *)(output->raw + 0x24) = uVar6;
  output->raw[0x28] = ((volatile uint8_t *)camry_host_ptr(0xfebebe66u))[0];
  output->raw[0x29] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebebe66u + (uint32_t)(1) * 1u))));
  output->raw[0x2a] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebebe66u + (uint32_t)(2) * 1u))));
  output->raw[0x2b] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebebe66u + (uint32_t)(3) * 1u))));
  output->raw[0x2c] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebebe66u + (uint32_t)(4) * 1u))));
  output->raw[0x2d] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebebe66u + (uint32_t)(5) * 1u))));
  output->raw[8] = DAT_febead60;
  output->raw[9] = DAT_febead67;
  uVar1 = DAT_febead39;
  output->raw[0x31] = '\0';
  output->raw[0x30] = uVar1;
  uVar2 = ((int)(int16_t)DAT_febeae58);
  output->raw[0x32] = '\0';
  output->raw[0x33] = '\0';
  *(undefined2 *)(output->raw + 0x2e) = uVar2;
  return;
}
