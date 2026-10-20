#include "common.h"

undefined4 aes128_encrypt_16byte_block_with_initialized_context_863a0(undefined4 *param_1,undefined4 *param_2,char param_3,int param_4)

{
  undefined4 uVar1;
  undefined4 *puVar2;
  
  uVar1 = 0xff;
  if ((param_3 == '\x10') && ((*((char *)camry_host_ptr((uint32_t)(param_4 + 0xc0)))) == '\x01')) {
    puVar2 = ((undefined4 *)camry_host_ptr((uint32_t)(param_4 + 0xb0)));
    if ((((uint)camry_host_addr(puVar2) & 3) == 0) && (((uint)camry_host_addr(param_1) & 3) == 0)) {
      *puVar2 = *param_1;
      (*((undefined4 *)camry_host_ptr((uint32_t)(param_4 + 0xb4)))) = param_1[1];
      (*((undefined4 *)camry_host_ptr((uint32_t)(param_4 + 0xb8)))) = param_1[2];
      (*((undefined4 *)camry_host_ptr((uint32_t)(param_4 + 0xbc)))) = param_1[3];
    }
    else {
      *(undefined1 *)puVar2 = *(undefined1 *)param_1;
      (*((undefined1 *)camry_host_ptr((uint32_t)(param_4 + 0xb1)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 1))));
      (*((undefined1 *)camry_host_ptr((uint32_t)(param_4 + 0xb2)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 2))));
      (*((undefined1 *)camry_host_ptr((uint32_t)(param_4 + 0xb3)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 3))));
      (*((undefined1 *)camry_host_ptr((uint32_t)(param_4 + 0xb4)))) = *(undefined1 *)(param_1 + 1);
      (*((undefined1 *)camry_host_ptr((uint32_t)(param_4 + 0xb5)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 5))));
      (*((undefined1 *)camry_host_ptr((uint32_t)(param_4 + 0xb6)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 6))));
      (*((undefined1 *)camry_host_ptr((uint32_t)(param_4 + 0xb7)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 7))));
      (*((undefined1 *)camry_host_ptr((uint32_t)(param_4 + 0xb8)))) = *(undefined1 *)(param_1 + 2);
      (*((undefined1 *)camry_host_ptr((uint32_t)(param_4 + 0xb9)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 9))));
      (*((undefined1 *)camry_host_ptr((uint32_t)(param_4 + 0xba)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 10))));
      (*((undefined1 *)camry_host_ptr((uint32_t)(param_4 + 0xbb)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb))));
      (*((undefined1 *)camry_host_ptr((uint32_t)(param_4 + 0xbc)))) = *(undefined1 *)(param_1 + 3);
      (*((undefined1 *)camry_host_ptr((uint32_t)(param_4 + 0xbd)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xd))));
      (*((undefined1 *)camry_host_ptr((uint32_t)(param_4 + 0xbe)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xe))));
      (*((undefined1 *)camry_host_ptr((uint32_t)(param_4 + 0xbf)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xf))));
    }
    aes128_encrypt_context_block_in_place_85a5c(((uint *)camry_host_ptr((uint32_t)(param_4))));
    if ((((uint)camry_host_addr(param_2) & 3) == 0) && (((uint)camry_host_addr(puVar2) & 3) == 0)) {
      *param_2 = *puVar2;
      param_2[1] = (*((undefined4 *)camry_host_ptr((uint32_t)(param_4 + 0xb4))));
      param_2[2] = (*((undefined4 *)camry_host_ptr((uint32_t)(param_4 + 0xb8))));
      param_2[3] = (*((undefined4 *)camry_host_ptr((uint32_t)(param_4 + 0xbc))));
    }
    else {
      *(undefined1 *)param_2 = *(undefined1 *)puVar2;
      (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 1)))) = (*((undefined1 *)camry_host_ptr((uint32_t)(param_4 + 0xb1))));
      (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 2)))) = (*((undefined1 *)camry_host_ptr((uint32_t)(param_4 + 0xb2))));
      (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 3)))) = (*((undefined1 *)camry_host_ptr((uint32_t)(param_4 + 0xb3))));
      *(undefined1 *)(param_2 + 1) = (*((undefined1 *)camry_host_ptr((uint32_t)(param_4 + 0xb4))));
      (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 5)))) = (*((undefined1 *)camry_host_ptr((uint32_t)(param_4 + 0xb5))));
      (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 6)))) = (*((undefined1 *)camry_host_ptr((uint32_t)(param_4 + 0xb6))));
      (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 7)))) = (*((undefined1 *)camry_host_ptr((uint32_t)(param_4 + 0xb7))));
      *(undefined1 *)(param_2 + 2) = (*((undefined1 *)camry_host_ptr((uint32_t)(param_4 + 0xb8))));
      (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 9)))) = (*((undefined1 *)camry_host_ptr((uint32_t)(param_4 + 0xb9))));
      (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 10)))) = (*((undefined1 *)camry_host_ptr((uint32_t)(param_4 + 0xba))));
      (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 0xb)))) = (*((undefined1 *)camry_host_ptr((uint32_t)(param_4 + 0xbb))));
      *(undefined1 *)(param_2 + 3) = (*((undefined1 *)camry_host_ptr((uint32_t)(param_4 + 0xbc))));
      (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 0xd)))) = (*((undefined1 *)camry_host_ptr((uint32_t)(param_4 + 0xbd))));
      (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 0xe)))) = (*((undefined1 *)camry_host_ptr((uint32_t)(param_4 + 0xbe))));
      (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 0xf)))) = (*((undefined1 *)camry_host_ptr((uint32_t)(param_4 + 0xbf))));
    }
    uVar1 = 0;
  }
  return uVar1;
}

undefined4 aes128_decrypt_16byte_block_with_initialized_context_864de(uint *param_1,uint *param_2,char param_3,uint *param_4)

{
  uint8_t stack_record_10[16];
  byte bVar1;
  byte bVar2;
  byte bVar3;
  byte bVar4;
  byte bVar5;
  uint uVar6;
  undefined4 uVar7;
  uint uVar8;
  uint uVar9;
  uint uVar10;
  
  uVar7 = 0xff;
  if ((param_3 == '\x10') && ((char)param_4[0x30] == '\x01')) {
    if ((((uint)camry_host_addr(param_4) & 3) == 0) && (((uint)camry_host_addr(param_1) & 3) == 0)) {
      param_4[0x2c] = *param_1;
      param_4[0x2d] = param_1[1];
      param_4[0x2e] = param_1[2];
      param_4[0x2f] = param_1[3];
    }
    else {
      *(char *)(param_4 + 0x2c) = (char)*param_1;
      (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xb1)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 1))));
      (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xb2)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 2))));
      (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xb3)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 3))));
      *(char *)(param_4 + 0x2d) = (char)param_1[1];
      (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xb5)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 5))));
      (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xb6)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 6))));
      (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xb7)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 7))));
      *(char *)(param_4 + 0x2e) = (char)param_1[2];
      (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xb9)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 9))));
      (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xba)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 10))));
      (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xbb)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb))));
      *(char *)(param_4 + 0x2f) = (char)param_1[3];
      (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xbd)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xd))));
      (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xbe)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xe))));
      (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xbf)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xf))));
    }
    uVar9 = param_4[0x2e];
    uVar6 = param_4[0x2c];
    uVar8 = param_4[0x2f];
    uVar10 = param_4[0x2d];
    param_4[0x2e] = uVar9 ^ param_4[0x2a];
    param_4[0x2c] = uVar6 ^ param_4[0x28];
    param_4[0x2f] = uVar8 ^ param_4[0x2b];
    param_4[0x2d] = uVar10 ^ param_4[0x29];
    (*((uint16_t *)((uint8_t *)stack_record_10 + 0u))) =
         CONCAT11((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xbd))))) * 1u)))),
                  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((uVar6 ^ param_4[0x28]) & 0xff) * 1u)))));
    (*((uint32_t *)(stack_record_10 + 0))) = ((*((uint32_t *)(stack_record_10 + 0))) & ~0xffffffu) | ((uint32_t)(CONCAT12((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xba))))) * 1u)))),
                  (undefined2)(*((uint32_t *)(stack_record_10 + 0))))) & 0xffffffu);
    (*((uint16_t *)((uint8_t *)(stack_record_10 + 4) + 0u))) =
         CONCAT11((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xb1))))) * 1u)))),
                  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((uVar10 ^ param_4[0x29]) & 0xff) * 1u)))));
    (*((uint32_t *)(stack_record_10 + 4))) = ((*((uint32_t *)(stack_record_10 + 4))) & ~0xffffffu) | ((uint32_t)(CONCAT12((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xbe))))) * 1u)))),
                  (undefined2)(*((uint32_t *)(stack_record_10 + 4))))) & 0xffffffu);
    (*((uint32_t *)(stack_record_10 + 4))) = CONCAT13((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xbb))))) * 1u)))),
                        ((uint32_t)((*((uint32_t *)(stack_record_10 + 4)))) & 0xffffffu));
    (*((uint16_t *)((uint8_t *)(stack_record_10 + 12) + 0u))) =
         CONCAT11((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xb9))))) * 1u)))),
                  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((uVar8 ^ param_4[0x2b]) & 0xff) * 1u)))));
    (*((uint32_t *)(stack_record_10 + 0))) = CONCAT13((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xb7))))) * 1u)))),
                        ((uint32_t)((*((uint32_t *)(stack_record_10 + 0)))) & 0xffffffu));
    (*((uint16_t *)((uint8_t *)(stack_record_10 + 8) + 0u))) =
         CONCAT11((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xb5))))) * 1u)))),
                  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((uVar9 ^ param_4[0x2a]) & 0xff) * 1u)))));
    (*((uint32_t *)(stack_record_10 + 8))) = CONCAT13((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xbf))))) * 1u)))),
                        CONCAT12((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xb2))))) * 1u)))),
                                 (undefined2)(*((uint32_t *)(stack_record_10 + 8)))));
    (*((uint32_t *)(stack_record_10 + 12))) = ((*((uint32_t *)(stack_record_10 + 12))) & ~0xffffffu) | ((uint32_t)(CONCAT12((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xb6))))) * 1u)))),
                  (undefined2)(*((uint32_t *)(stack_record_10 + 12))))) & 0xffffffu);
    (*((uint32_t *)(stack_record_10 + 12))) = CONCAT13((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xb3))))) * 1u)))),
                        ((uint32_t)((*((uint32_t *)(stack_record_10 + 12)))) & 0xffffffu));
    (*((uint32_t *)(stack_record_10 + 8))) = (*((uint32_t *)(stack_record_10 + 8))) ^ param_4[0x26];
    (*((uint32_t *)(stack_record_10 + 0))) = (*((uint32_t *)(stack_record_10 + 0))) ^ param_4[0x24];
    (*((uint32_t *)(stack_record_10 + 4))) = (*((uint32_t *)(stack_record_10 + 4))) ^ param_4[0x25];
    (*((uint32_t *)(stack_record_10 + 12))) = (*((uint32_t *)(stack_record_10 + 12))) ^ param_4[0x27];
    uVar9 = *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x25100u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 0))) >> 0x18) * 4) * 1u)))) ^
            *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24d00u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 0))) >> 0x10 & 0xff) * 4) * 1u)))) ^
            *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24900u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 0))) >> 8 & 0xff) * 4) * 1u)))) ^
            *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24500u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 0))) & 0xff) * 4) * 1u))));
    param_4[0x2c] = uVar9;
    uVar8 = *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x25100u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 4))) >> 0x18) * 4) * 1u)))) ^
            *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24d00u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 4))) >> 0x10 & 0xff) * 4) * 1u)))) ^
            *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24900u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 4))) >> 8 & 0xff) * 4) * 1u)))) ^
            *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24500u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 4))) & 0xff) * 4) * 1u))));
    param_4[0x2d] = uVar8;
    uVar10 = *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x25100u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 8))) >> 0x18) * 4) * 1u)))) ^
             *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24d00u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 8))) >> 0x10 & 0xff) * 4) * 1u)))) ^
             *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24900u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 8))) >> 8 & 0xff) * 4) * 1u)))) ^
             *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24500u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 8))) & 0xff) * 4) * 1u))));
    param_4[0x2e] = uVar10;
    uVar6 = *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x25100u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 12))) >> 0x18) * 4) * 1u)))) ^
            *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24d00u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 12))) >> 0x10 & 0xff) * 4) * 1u)))) ^
            *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24900u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 12))) >> 8 & 0xff) * 4) * 1u)))) ^
            *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24500u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 12))) & 0xff) * 4) * 1u))));
    param_4[0x2f] = uVar6;
    (*((uint16_t *)((uint8_t *)stack_record_10 + 0u))) =
         CONCAT11((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xbd))))) * 1u)))),
                  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)(uVar9 & 0xff) * 1u)))));
    (*((uint32_t *)(stack_record_10 + 0))) = ((*((uint32_t *)(stack_record_10 + 0))) & ~0xffffffu) | ((uint32_t)(CONCAT12((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xba))))) * 1u)))),
                  (undefined2)(*((uint32_t *)(stack_record_10 + 0))))) & 0xffffffu);
    (*((uint32_t *)(stack_record_10 + 0))) = CONCAT13((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xb7))))) * 1u)))),
                        ((uint32_t)((*((uint32_t *)(stack_record_10 + 0)))) & 0xffffffu));
    (*((uint16_t *)((uint8_t *)(stack_record_10 + 4) + 0u))) =
         CONCAT11((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xb1))))) * 1u)))),
                  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)(uVar8 & 0xff) * 1u)))));
    (*((uint32_t *)(stack_record_10 + 4))) = ((*((uint32_t *)(stack_record_10 + 4))) & ~0xffffffu) | ((uint32_t)(CONCAT12((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xbe))))) * 1u)))),
                  (undefined2)(*((uint32_t *)(stack_record_10 + 4))))) & 0xffffffu);
    (*((uint32_t *)(stack_record_10 + 4))) = CONCAT13((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xbb))))) * 1u)))),
                        ((uint32_t)((*((uint32_t *)(stack_record_10 + 4)))) & 0xffffffu));
    (*((uint16_t *)((uint8_t *)(stack_record_10 + 12) + 0u))) =
         CONCAT11((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xb9))))) * 1u)))),
                  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)(uVar6 & 0xff) * 1u)))));
    (*((uint32_t *)(stack_record_10 + 12))) = ((*((uint32_t *)(stack_record_10 + 12))) & ~0xffffffu) | ((uint32_t)(CONCAT12((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xb6))))) * 1u)))),
                  (undefined2)(*((uint32_t *)(stack_record_10 + 12))))) & 0xffffffu);
    (*((uint32_t *)(stack_record_10 + 12))) = CONCAT13((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xb3))))) * 1u)))),
                        ((uint32_t)((*((uint32_t *)(stack_record_10 + 12)))) & 0xffffffu));
    (*((uint32_t *)(stack_record_10 + 0))) = (*((uint32_t *)(stack_record_10 + 0))) ^ param_4[0x20];
    (*((uint16_t *)((uint8_t *)(stack_record_10 + 8) + 0u))) =
         CONCAT11((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xb5))))) * 1u)))),
                  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)(uVar10 & 0xff) * 1u)))));
    (*((uint32_t *)(stack_record_10 + 8))) = CONCAT22(CONCAT11((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xbf))))) * 1u)))),
                                 (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xb2))))) * 1u))))),
                        (undefined2)(*((uint32_t *)(stack_record_10 + 8))));
    (*((uint32_t *)(stack_record_10 + 4))) = (*((uint32_t *)(stack_record_10 + 4))) ^ param_4[0x21];
    (*((uint32_t *)(stack_record_10 + 8))) = (*((uint32_t *)(stack_record_10 + 8))) ^ param_4[0x22];
    (*((uint32_t *)(stack_record_10 + 12))) = (*((uint32_t *)(stack_record_10 + 12))) ^ param_4[0x23];
    uVar9 = *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x25100u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 0))) >> 0x18) * 4) * 1u)))) ^
            *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24d00u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 0))) >> 0x10 & 0xff) * 4) * 1u)))) ^
            *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24900u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 0))) >> 8 & 0xff) * 4) * 1u)))) ^
            *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24500u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 0))) & 0xff) * 4) * 1u))));
    param_4[0x2c] = uVar9;
    uVar8 = *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x25100u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 4))) >> 0x18) * 4) * 1u)))) ^
            *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24d00u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 4))) >> 0x10 & 0xff) * 4) * 1u)))) ^
            *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24900u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 4))) >> 8 & 0xff) * 4) * 1u)))) ^
            *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24500u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 4))) & 0xff) * 4) * 1u))));
    param_4[0x2d] = uVar8;
    uVar10 = *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x25100u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 8))) >> 0x18) * 4) * 1u)))) ^
             *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24d00u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 8))) >> 0x10 & 0xff) * 4) * 1u)))) ^
             *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24900u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 8))) >> 8 & 0xff) * 4) * 1u)))) ^
             *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24500u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 8))) & 0xff) * 4) * 1u))));
    param_4[0x2e] = uVar10;
    uVar6 = *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x25100u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 12))) >> 0x18) * 4) * 1u)))) ^
            *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24d00u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 12))) >> 0x10 & 0xff) * 4) * 1u)))) ^
            *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24900u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 12))) >> 8 & 0xff) * 4) * 1u)))) ^
            *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24500u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 12))) & 0xff) * 4) * 1u))));
    param_4[0x2f] = uVar6;
    (*((uint16_t *)((uint8_t *)stack_record_10 + 0u))) =
         CONCAT11((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xbd))))) * 1u)))),
                  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)(uVar9 & 0xff) * 1u)))));
    (*((uint32_t *)(stack_record_10 + 0))) = ((*((uint32_t *)(stack_record_10 + 0))) & ~0xffffffu) | ((uint32_t)(CONCAT12((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xba))))) * 1u)))),
                  (undefined2)(*((uint32_t *)(stack_record_10 + 0))))) & 0xffffffu);
    (*((uint32_t *)(stack_record_10 + 0))) = CONCAT13((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xb7))))) * 1u)))),
                        ((uint32_t)((*((uint32_t *)(stack_record_10 + 0)))) & 0xffffffu));
    (*((uint16_t *)((uint8_t *)(stack_record_10 + 4) + 0u))) =
         CONCAT11((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xb1))))) * 1u)))),
                  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)(uVar8 & 0xff) * 1u)))));
    (*((uint32_t *)(stack_record_10 + 4))) = ((*((uint32_t *)(stack_record_10 + 4))) & ~0xffffffu) | ((uint32_t)(CONCAT12((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xbe))))) * 1u)))),
                  (undefined2)(*((uint32_t *)(stack_record_10 + 4))))) & 0xffffffu);
    (*((uint32_t *)(stack_record_10 + 4))) = CONCAT13((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xbb))))) * 1u)))),
                        ((uint32_t)((*((uint32_t *)(stack_record_10 + 4)))) & 0xffffffu));
    (*((uint16_t *)((uint8_t *)(stack_record_10 + 12) + 0u))) =
         CONCAT11((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xb9))))) * 1u)))),
                  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)(uVar6 & 0xff) * 1u)))));
    (*((uint32_t *)(stack_record_10 + 12))) = ((*((uint32_t *)(stack_record_10 + 12))) & ~0xffffffu) | ((uint32_t)(CONCAT12((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xb6))))) * 1u)))),
                  (undefined2)(*((uint32_t *)(stack_record_10 + 12))))) & 0xffffffu);
    (*((uint32_t *)(stack_record_10 + 12))) = CONCAT13((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xb3))))) * 1u)))),
                        ((uint32_t)((*((uint32_t *)(stack_record_10 + 12)))) & 0xffffffu));
    (*((uint32_t *)(stack_record_10 + 0))) = (*((uint32_t *)(stack_record_10 + 0))) ^ param_4[0x1c];
    (*((uint16_t *)((uint8_t *)(stack_record_10 + 8) + 0u))) =
         CONCAT11((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xb5))))) * 1u)))),
                  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)(uVar10 & 0xff) * 1u)))));
    (*((uint32_t *)(stack_record_10 + 8))) = CONCAT22(CONCAT11((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xbf))))) * 1u)))),
                                 (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xb2))))) * 1u))))),
                        (undefined2)(*((uint32_t *)(stack_record_10 + 8))));
    (*((uint32_t *)(stack_record_10 + 4))) = (*((uint32_t *)(stack_record_10 + 4))) ^ param_4[0x1d];
    (*((uint32_t *)(stack_record_10 + 8))) = (*((uint32_t *)(stack_record_10 + 8))) ^ param_4[0x1e];
    (*((uint32_t *)(stack_record_10 + 12))) = (*((uint32_t *)(stack_record_10 + 12))) ^ param_4[0x1f];
    uVar9 = *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x25100u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 0))) >> 0x18) * 4) * 1u)))) ^
            *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24d00u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 0))) >> 0x10 & 0xff) * 4) * 1u)))) ^
            *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24900u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 0))) >> 8 & 0xff) * 4) * 1u)))) ^
            *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24500u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 0))) & 0xff) * 4) * 1u))));
    param_4[0x2c] = uVar9;
    uVar8 = *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x25100u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 4))) >> 0x18) * 4) * 1u)))) ^
            *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24d00u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 4))) >> 0x10 & 0xff) * 4) * 1u)))) ^
            *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24900u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 4))) >> 8 & 0xff) * 4) * 1u)))) ^
            *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24500u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 4))) & 0xff) * 4) * 1u))));
    param_4[0x2d] = uVar8;
    uVar10 = *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x25100u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 8))) >> 0x18) * 4) * 1u)))) ^
             *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24d00u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 8))) >> 0x10 & 0xff) * 4) * 1u)))) ^
             *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24900u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 8))) >> 8 & 0xff) * 4) * 1u)))) ^
             *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24500u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 8))) & 0xff) * 4) * 1u))));
    param_4[0x2e] = uVar10;
    uVar6 = *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x25100u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 12))) >> 0x18) * 4) * 1u)))) ^
            *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24d00u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 12))) >> 0x10 & 0xff) * 4) * 1u)))) ^
            *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24900u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 12))) >> 8 & 0xff) * 4) * 1u)))) ^
            *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24500u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 12))) & 0xff) * 4) * 1u))));
    param_4[0x2f] = uVar6;
    (*((uint16_t *)((uint8_t *)stack_record_10 + 0u))) =
         CONCAT11((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xbd))))) * 1u)))),
                  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)(uVar9 & 0xff) * 1u)))));
    (*((uint32_t *)(stack_record_10 + 0))) = ((*((uint32_t *)(stack_record_10 + 0))) & ~0xffffffu) | ((uint32_t)(CONCAT12((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xba))))) * 1u)))),
                  (undefined2)(*((uint32_t *)(stack_record_10 + 0))))) & 0xffffffu);
    (*((uint32_t *)(stack_record_10 + 0))) = CONCAT13((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xb7))))) * 1u)))),
                        ((uint32_t)((*((uint32_t *)(stack_record_10 + 0)))) & 0xffffffu));
    (*((uint16_t *)((uint8_t *)(stack_record_10 + 4) + 0u))) =
         CONCAT11((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xb1))))) * 1u)))),
                  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)(uVar8 & 0xff) * 1u)))));
    (*((uint32_t *)(stack_record_10 + 4))) = ((*((uint32_t *)(stack_record_10 + 4))) & ~0xffffffu) | ((uint32_t)(CONCAT12((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xbe))))) * 1u)))),
                  (undefined2)(*((uint32_t *)(stack_record_10 + 4))))) & 0xffffffu);
    (*((uint16_t *)((uint8_t *)(stack_record_10 + 8) + 0u))) =
         CONCAT11((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xb5))))) * 1u)))),
                  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)(uVar10 & 0xff) * 1u)))));
    (*((uint32_t *)(stack_record_10 + 8))) = ((*((uint32_t *)(stack_record_10 + 8))) & ~0xffffffu) | ((uint32_t)(CONCAT12((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xb2))))) * 1u)))),
                  (undefined2)(*((uint32_t *)(stack_record_10 + 8))))) & 0xffffffu);
    (*((uint32_t *)(stack_record_10 + 8))) = CONCAT13((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xbf))))) * 1u)))),
                        ((uint32_t)((*((uint32_t *)(stack_record_10 + 8)))) & 0xffffffu));
    (*((uint16_t *)((uint8_t *)(stack_record_10 + 12) + 0u))) =
         CONCAT11((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xb9))))) * 1u)))),
                  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)(uVar6 & 0xff) * 1u)))));
    (*((uint32_t *)(stack_record_10 + 12))) = ((*((uint32_t *)(stack_record_10 + 12))) & ~0xffffffu) | ((uint32_t)(CONCAT12((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xb6))))) * 1u)))),
                  (undefined2)(*((uint32_t *)(stack_record_10 + 12))))) & 0xffffffu);
    (*((uint32_t *)(stack_record_10 + 4))) = CONCAT13((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xbb))))) * 1u)))),
                        ((uint32_t)((*((uint32_t *)(stack_record_10 + 4)))) & 0xffffffu));
    (*((uint32_t *)(stack_record_10 + 12))) = CONCAT13((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xb3))))) * 1u)))),
                        ((uint32_t)((*((uint32_t *)(stack_record_10 + 12)))) & 0xffffffu));
    (*((uint32_t *)(stack_record_10 + 0))) = (*((uint32_t *)(stack_record_10 + 0))) ^ param_4[0x18];
    (*((uint32_t *)(stack_record_10 + 4))) = (*((uint32_t *)(stack_record_10 + 4))) ^ param_4[0x19];
    (*((uint32_t *)(stack_record_10 + 8))) = (*((uint32_t *)(stack_record_10 + 8))) ^ param_4[0x1a];
    (*((uint32_t *)(stack_record_10 + 12))) = (*((uint32_t *)(stack_record_10 + 12))) ^ param_4[0x1b];
    param_4[0x2c] =
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x25100u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 0))) >> 0x18) * 4) * 1u)))) ^
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24d00u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 0))) >> 0x10 & 0xff) * 4) * 1u)))) ^
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24900u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 0))) >> 8 & 0xff) * 4) * 1u)))) ^
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24500u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 0))) & 0xff) * 4) * 1u))));
    param_4[0x2d] =
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x25100u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 4))) >> 0x18) * 4) * 1u)))) ^
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24d00u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 4))) >> 0x10 & 0xff) * 4) * 1u)))) ^
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24900u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 4))) >> 8 & 0xff) * 4) * 1u)))) ^
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24500u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 4))) & 0xff) * 4) * 1u))));
    param_4[0x2e] =
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x25100u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 8))) >> 0x18) * 4) * 1u)))) ^
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24d00u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 8))) >> 0x10 & 0xff) * 4) * 1u)))) ^
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24900u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 8))) >> 8 & 0xff) * 4) * 1u)))) ^
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24500u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 8))) & 0xff) * 4) * 1u))));
    param_4[0x2f] =
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x25100u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 12))) >> 0x18) * 4) * 1u)))) ^
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24d00u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 12))) >> 0x10 & 0xff) * 4) * 1u)))) ^
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24900u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 12))) >> 8 & 0xff) * 4) * 1u)))) ^
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24500u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 12))) & 0xff) * 4) * 1u))));
    (*((uint16_t *)((uint8_t *)stack_record_10 + 0u))) =
         CONCAT11((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xbd))))) * 1u)))),
                  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((byte)param_4[0x2c]) * 1u)))));
    (*((uint32_t *)(stack_record_10 + 0))) = ((*((uint32_t *)(stack_record_10 + 0))) & ~0xffffffu) | ((uint32_t)(CONCAT12((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xba))))) * 1u)))),
                  (undefined2)(*((uint32_t *)(stack_record_10 + 0))))) & 0xffffffu);
    (*((uint32_t *)(stack_record_10 + 0))) = CONCAT13((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xb7))))) * 1u)))),
                        ((uint32_t)((*((uint32_t *)(stack_record_10 + 0)))) & 0xffffffu));
    (*((uint16_t *)((uint8_t *)(stack_record_10 + 4) + 0u))) =
         CONCAT11((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xb1))))) * 1u)))),
                  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((byte)param_4[0x2d]) * 1u)))));
    (*((uint32_t *)(stack_record_10 + 4))) = ((*((uint32_t *)(stack_record_10 + 4))) & ~0xffffffu) | ((uint32_t)(CONCAT12((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xbe))))) * 1u)))),
                  (undefined2)(*((uint32_t *)(stack_record_10 + 4))))) & 0xffffffu);
    (*((uint32_t *)(stack_record_10 + 4))) = CONCAT13((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xbb))))) * 1u)))),
                        ((uint32_t)((*((uint32_t *)(stack_record_10 + 4)))) & 0xffffffu));
    (*((uint16_t *)((uint8_t *)(stack_record_10 + 8) + 0u))) =
         CONCAT11((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xb5))))) * 1u)))),
                  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((byte)param_4[0x2e]) * 1u)))));
    (*((uint32_t *)(stack_record_10 + 8))) = ((*((uint32_t *)(stack_record_10 + 8))) & ~0xffffffu) | ((uint32_t)(CONCAT12((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xb2))))) * 1u)))),
                  (undefined2)(*((uint32_t *)(stack_record_10 + 8))))) & 0xffffffu);
    (*((uint32_t *)(stack_record_10 + 8))) = CONCAT13((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xbf))))) * 1u)))),
                        ((uint32_t)((*((uint32_t *)(stack_record_10 + 8)))) & 0xffffffu));
    (*((uint16_t *)((uint8_t *)(stack_record_10 + 12) + 0u))) =
         CONCAT11((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xb9))))) * 1u)))),
                  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((byte)param_4[0x2f]) * 1u)))));
    (*((uint32_t *)(stack_record_10 + 12))) = ((*((uint32_t *)(stack_record_10 + 12))) & ~0xffffffu) | ((uint32_t)(CONCAT12((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xb6))))) * 1u)))),
                  (undefined2)(*((uint32_t *)(stack_record_10 + 12))))) & 0xffffffu);
    (*((uint32_t *)(stack_record_10 + 12))) = CONCAT13((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xb3))))) * 1u)))),
                        ((uint32_t)((*((uint32_t *)(stack_record_10 + 12)))) & 0xffffffu));
    (*((uint32_t *)(stack_record_10 + 0))) = (*((uint32_t *)(stack_record_10 + 0))) ^ param_4[0x14];
    (*((uint32_t *)(stack_record_10 + 4))) = (*((uint32_t *)(stack_record_10 + 4))) ^ param_4[0x15];
    (*((uint32_t *)(stack_record_10 + 8))) = (*((uint32_t *)(stack_record_10 + 8))) ^ param_4[0x16];
    (*((uint32_t *)(stack_record_10 + 12))) = (*((uint32_t *)(stack_record_10 + 12))) ^ param_4[0x17];
    param_4[0x2c] =
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x25100u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 0))) >> 0x18) * 4) * 1u)))) ^
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24d00u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 0))) >> 0x10 & 0xff) * 4) * 1u)))) ^
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24900u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 0))) >> 8 & 0xff) * 4) * 1u)))) ^
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24500u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 0))) & 0xff) * 4) * 1u))));
    param_4[0x2d] =
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x25100u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 4))) >> 0x18) * 4) * 1u)))) ^
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24d00u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 4))) >> 0x10 & 0xff) * 4) * 1u)))) ^
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24900u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 4))) >> 8 & 0xff) * 4) * 1u)))) ^
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24500u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 4))) & 0xff) * 4) * 1u))));
    param_4[0x2e] =
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x25100u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 8))) >> 0x18) * 4) * 1u)))) ^
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24d00u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 8))) >> 0x10 & 0xff) * 4) * 1u)))) ^
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24900u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 8))) >> 8 & 0xff) * 4) * 1u)))) ^
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24500u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 8))) & 0xff) * 4) * 1u))));
    param_4[0x2f] =
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x25100u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 12))) >> 0x18) * 4) * 1u)))) ^
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24d00u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 12))) >> 0x10 & 0xff) * 4) * 1u)))) ^
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24900u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 12))) >> 8 & 0xff) * 4) * 1u)))) ^
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24500u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 12))) & 0xff) * 4) * 1u))));
    (*((uint16_t *)((uint8_t *)stack_record_10 + 0u))) =
         CONCAT11((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xbd))))) * 1u)))),
                  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((byte)param_4[0x2c]) * 1u)))));
    (*((uint32_t *)(stack_record_10 + 0))) = ((*((uint32_t *)(stack_record_10 + 0))) & ~0xffffffu) | ((uint32_t)(CONCAT12((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xba))))) * 1u)))),
                  (undefined2)(*((uint32_t *)(stack_record_10 + 0))))) & 0xffffffu);
    (*((uint32_t *)(stack_record_10 + 0))) = CONCAT13((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xb7))))) * 1u)))),
                        ((uint32_t)((*((uint32_t *)(stack_record_10 + 0)))) & 0xffffffu));
    (*((uint16_t *)((uint8_t *)(stack_record_10 + 4) + 0u))) =
         CONCAT11((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xb1))))) * 1u)))),
                  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((byte)param_4[0x2d]) * 1u)))));
    (*((uint32_t *)(stack_record_10 + 4))) = ((*((uint32_t *)(stack_record_10 + 4))) & ~0xffffffu) | ((uint32_t)(CONCAT12((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xbe))))) * 1u)))),
                  (undefined2)(*((uint32_t *)(stack_record_10 + 4))))) & 0xffffffu);
    (*((uint32_t *)(stack_record_10 + 4))) = CONCAT13((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xbb))))) * 1u)))),
                        ((uint32_t)((*((uint32_t *)(stack_record_10 + 4)))) & 0xffffffu));
    (*((uint16_t *)((uint8_t *)(stack_record_10 + 8) + 0u))) =
         CONCAT11((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xb5))))) * 1u)))),
                  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((byte)param_4[0x2e]) * 1u)))));
    (*((uint32_t *)(stack_record_10 + 8))) = ((*((uint32_t *)(stack_record_10 + 8))) & ~0xffffffu) | ((uint32_t)(CONCAT12((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xb2))))) * 1u)))),
                  (undefined2)(*((uint32_t *)(stack_record_10 + 8))))) & 0xffffffu);
    (*((uint32_t *)(stack_record_10 + 8))) = CONCAT13((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xbf))))) * 1u)))),
                        ((uint32_t)((*((uint32_t *)(stack_record_10 + 8)))) & 0xffffffu));
    (*((uint16_t *)((uint8_t *)(stack_record_10 + 12) + 0u))) =
         CONCAT11((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xb9))))) * 1u)))),
                  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((byte)param_4[0x2f]) * 1u)))));
    (*((uint32_t *)(stack_record_10 + 12))) = ((*((uint32_t *)(stack_record_10 + 12))) & ~0xffffffu) | ((uint32_t)(CONCAT12((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xb6))))) * 1u)))),
                  (undefined2)(*((uint32_t *)(stack_record_10 + 12))))) & 0xffffffu);
    (*((uint32_t *)(stack_record_10 + 12))) = CONCAT13((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xb3))))) * 1u)))),
                        ((uint32_t)((*((uint32_t *)(stack_record_10 + 12)))) & 0xffffffu));
    (*((uint32_t *)(stack_record_10 + 0))) = (*((uint32_t *)(stack_record_10 + 0))) ^ param_4[0x10];
    (*((uint32_t *)(stack_record_10 + 4))) = (*((uint32_t *)(stack_record_10 + 4))) ^ param_4[0x11];
    (*((uint32_t *)(stack_record_10 + 8))) = (*((uint32_t *)(stack_record_10 + 8))) ^ param_4[0x12];
    (*((uint32_t *)(stack_record_10 + 12))) = (*((uint32_t *)(stack_record_10 + 12))) ^ param_4[0x13];
    param_4[0x2c] =
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x25100u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 0))) >> 0x18) * 4) * 1u)))) ^
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24d00u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 0))) >> 0x10 & 0xff) * 4) * 1u)))) ^
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24900u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 0))) >> 8 & 0xff) * 4) * 1u)))) ^
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24500u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 0))) & 0xff) * 4) * 1u))));
    param_4[0x2d] =
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x25100u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 4))) >> 0x18) * 4) * 1u)))) ^
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24d00u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 4))) >> 0x10 & 0xff) * 4) * 1u)))) ^
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24900u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 4))) >> 8 & 0xff) * 4) * 1u)))) ^
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24500u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 4))) & 0xff) * 4) * 1u))));
    param_4[0x2e] =
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x25100u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 8))) >> 0x18) * 4) * 1u)))) ^
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24d00u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 8))) >> 0x10 & 0xff) * 4) * 1u)))) ^
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24900u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 8))) >> 8 & 0xff) * 4) * 1u)))) ^
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24500u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 8))) & 0xff) * 4) * 1u))));
    param_4[0x2f] =
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x25100u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 12))) >> 0x18) * 4) * 1u)))) ^
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24d00u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 12))) >> 0x10 & 0xff) * 4) * 1u)))) ^
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24900u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 12))) >> 8 & 0xff) * 4) * 1u)))) ^
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24500u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 12))) & 0xff) * 4) * 1u))));
    (*((uint16_t *)((uint8_t *)stack_record_10 + 0u))) =
         CONCAT11((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xbd))))) * 1u)))),
                  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((byte)param_4[0x2c]) * 1u)))));
    (*((uint32_t *)(stack_record_10 + 0))) = ((*((uint32_t *)(stack_record_10 + 0))) & ~0xffffffu) | ((uint32_t)(CONCAT12((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xba))))) * 1u)))),
                  (undefined2)(*((uint32_t *)(stack_record_10 + 0))))) & 0xffffffu);
    (*((uint32_t *)(stack_record_10 + 0))) = CONCAT13((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xb7))))) * 1u)))),
                        ((uint32_t)((*((uint32_t *)(stack_record_10 + 0)))) & 0xffffffu));
    (*((uint16_t *)((uint8_t *)(stack_record_10 + 4) + 0u))) =
         CONCAT11((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xb1))))) * 1u)))),
                  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((byte)param_4[0x2d]) * 1u)))));
    (*((uint32_t *)(stack_record_10 + 4))) = ((*((uint32_t *)(stack_record_10 + 4))) & ~0xffffffu) | ((uint32_t)(CONCAT12((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xbe))))) * 1u)))),
                  (undefined2)(*((uint32_t *)(stack_record_10 + 4))))) & 0xffffffu);
    (*((uint32_t *)(stack_record_10 + 4))) = CONCAT13((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xbb))))) * 1u)))),
                        ((uint32_t)((*((uint32_t *)(stack_record_10 + 4)))) & 0xffffffu));
    (*((uint16_t *)((uint8_t *)(stack_record_10 + 12) + 0u))) =
         CONCAT11((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xb9))))) * 1u)))),
                  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((byte)param_4[0x2f]) * 1u)))));
    (*((uint16_t *)((uint8_t *)(stack_record_10 + 8) + 0u))) =
         CONCAT11((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xb5))))) * 1u)))),
                  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((byte)param_4[0x2e]) * 1u)))));
    (*((uint32_t *)(stack_record_10 + 8))) = CONCAT22(CONCAT11((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xbf))))) * 1u)))),
                                 (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xb2))))) * 1u))))),
                        (undefined2)(*((uint32_t *)(stack_record_10 + 8))));
    (*((uint32_t *)(stack_record_10 + 0))) = (*((uint32_t *)(stack_record_10 + 0))) ^ param_4[0xc];
    (*((uint32_t *)(stack_record_10 + 4))) = (*((uint32_t *)(stack_record_10 + 4))) ^ param_4[0xd];
    (*((uint32_t *)(stack_record_10 + 12))) = ((*((uint32_t *)(stack_record_10 + 12))) & ~0xffffffu) | ((uint32_t)(CONCAT12((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xb6))))) * 1u)))),
                  (undefined2)(*((uint32_t *)(stack_record_10 + 12))))) & 0xffffffu);
    (*((uint32_t *)(stack_record_10 + 12))) = CONCAT13((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xb3))))) * 1u)))),
                        ((uint32_t)((*((uint32_t *)(stack_record_10 + 12)))) & 0xffffffu));
    (*((uint32_t *)(stack_record_10 + 8))) = (*((uint32_t *)(stack_record_10 + 8))) ^ param_4[0xe];
    (*((uint32_t *)(stack_record_10 + 12))) = (*((uint32_t *)(stack_record_10 + 12))) ^ param_4[0xf];
    param_4[0x2c] =
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x25100u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 0))) >> 0x18) * 4) * 1u)))) ^
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24d00u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 0))) >> 0x10 & 0xff) * 4) * 1u)))) ^
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24900u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 0))) >> 8 & 0xff) * 4) * 1u)))) ^
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24500u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 0))) & 0xff) * 4) * 1u))));
    param_4[0x2d] =
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x25100u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 4))) >> 0x18) * 4) * 1u)))) ^
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24d00u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 4))) >> 0x10 & 0xff) * 4) * 1u)))) ^
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24900u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 4))) >> 8 & 0xff) * 4) * 1u)))) ^
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24500u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 4))) & 0xff) * 4) * 1u))));
    param_4[0x2e] =
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x25100u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 8))) >> 0x18) * 4) * 1u)))) ^
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24d00u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 8))) >> 0x10 & 0xff) * 4) * 1u)))) ^
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24900u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 8))) >> 8 & 0xff) * 4) * 1u)))) ^
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24500u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 8))) & 0xff) * 4) * 1u))));
    param_4[0x2f] =
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x25100u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 12))) >> 0x18) * 4) * 1u)))) ^
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24d00u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 12))) >> 0x10 & 0xff) * 4) * 1u)))) ^
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24900u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 12))) >> 8 & 0xff) * 4) * 1u)))) ^
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24500u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 12))) & 0xff) * 4) * 1u))));
    (*((uint16_t *)((uint8_t *)(stack_record_10 + 12) + 0u))) =
         CONCAT11((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xb9))))) * 1u)))),
                  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((byte)param_4[0x2f]) * 1u)))));
    (*((uint32_t *)(stack_record_10 + 12))) = ((*((uint32_t *)(stack_record_10 + 12))) & ~0xffffffu) | ((uint32_t)(CONCAT12((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xb6))))) * 1u)))),
                  (undefined2)(*((uint32_t *)(stack_record_10 + 12))))) & 0xffffffu);
    (*((uint16_t *)((uint8_t *)stack_record_10 + 0u))) =
         CONCAT11((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xbd))))) * 1u)))),
                  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((byte)param_4[0x2c]) * 1u)))));
    (*((uint32_t *)(stack_record_10 + 0))) = CONCAT22(CONCAT11((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xb7))))) * 1u)))),
                                 (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xba))))) * 1u))))),
                        (undefined2)(*((uint32_t *)(stack_record_10 + 0))));
    (*((uint32_t *)(stack_record_10 + 0))) = (*((uint32_t *)(stack_record_10 + 0))) ^ param_4[8];
    (*((uint32_t *)(stack_record_10 + 12))) = CONCAT13((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xb3))))) * 1u)))),
                        ((uint32_t)((*((uint32_t *)(stack_record_10 + 12)))) & 0xffffffu));
    (*((uint16_t *)((uint8_t *)(stack_record_10 + 8) + 0u))) =
         CONCAT11((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xb5))))) * 1u)))),
                  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((byte)param_4[0x2e]) * 1u)))));
    (*((uint32_t *)(stack_record_10 + 8))) = CONCAT22(CONCAT11((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xbf))))) * 1u)))),
                                 (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xb2))))) * 1u))))),
                        (undefined2)(*((uint32_t *)(stack_record_10 + 8))));
    uVar6 = CONCAT13((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xbb))))) * 1u)))),
                     CONCAT21(CONCAT11((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xbe))))) * 1u)))),
                                       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xb1))))) * 1u))))),
                              (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((byte)param_4[0x2d]) * 1u)))))) ^ param_4[9];
    (*((uint32_t *)(stack_record_10 + 8))) = (*((uint32_t *)(stack_record_10 + 8))) ^ param_4[10];
    (*((uint32_t *)(stack_record_10 + 12))) = (*((uint32_t *)(stack_record_10 + 12))) ^ param_4[0xb];
    param_4[0x2c] =
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x25100u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 0))) >> 0x18) * 4) * 1u)))) ^
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24d00u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 0))) >> 0x10 & 0xff) * 4) * 1u)))) ^
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24900u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 0))) >> 8 & 0xff) * 4) * 1u)))) ^
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24500u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 0))) & 0xff) * 4) * 1u))));
    param_4[0x2d] =
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x25100u + (uint32_t)((uVar6 >> 0x18) * 4) * 1u)))) ^
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24d00u + (uint32_t)((uVar6 >> 0x10 & 0xff) * 4) * 1u)))) ^
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24900u + (uint32_t)((uVar6 >> 8 & 0xff) * 4) * 1u)))) ^
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24500u + (uint32_t)((uVar6 & 0xff) * 4) * 1u))));
    param_4[0x2e] =
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x25100u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 8))) >> 0x18) * 4) * 1u)))) ^
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24d00u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 8))) >> 0x10 & 0xff) * 4) * 1u)))) ^
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24900u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 8))) >> 8 & 0xff) * 4) * 1u)))) ^
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24500u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 8))) & 0xff) * 4) * 1u))));
    param_4[0x2f] =
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x25100u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 12))) >> 0x18) * 4) * 1u)))) ^
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24d00u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 12))) >> 0x10 & 0xff) * 4) * 1u)))) ^
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24900u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 12))) >> 8 & 0xff) * 4) * 1u)))) ^
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24500u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 12))) & 0xff) * 4) * 1u))));
    (*((uint16_t *)((uint8_t *)(stack_record_10 + 12) + 0u))) =
         CONCAT11((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xb9))))) * 1u)))),
                  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((byte)param_4[0x2f]) * 1u)))));
    (*((uint32_t *)(stack_record_10 + 12))) = ((*((uint32_t *)(stack_record_10 + 12))) & ~0xffffffu) | ((uint32_t)(CONCAT12((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xb6))))) * 1u)))),
                  (undefined2)(*((uint32_t *)(stack_record_10 + 12))))) & 0xffffffu);
    (*((uint16_t *)((uint8_t *)stack_record_10 + 0u))) =
         CONCAT11((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xbd))))) * 1u)))),
                  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((byte)param_4[0x2c]) * 1u)))));
    (*((uint32_t *)(stack_record_10 + 0))) = CONCAT22(CONCAT11((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xb7))))) * 1u)))),
                                 (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xba))))) * 1u))))),
                        (undefined2)(*((uint32_t *)(stack_record_10 + 0))));
    (*((uint32_t *)(stack_record_10 + 4))) = CONCAT31(CONCAT12((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xbb))))) * 1u)))),
                                 CONCAT11((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xbe))))) * 1u)))),
                                          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xb1))))) * 1u)))))),
                        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((byte)param_4[0x2d]) * 1u)))));
    (*((uint32_t *)(stack_record_10 + 0))) = (*((uint32_t *)(stack_record_10 + 0))) ^ param_4[4];
    (*((uint32_t *)(stack_record_10 + 12))) = CONCAT13((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xb3))))) * 1u)))),
                        ((uint32_t)((*((uint32_t *)(stack_record_10 + 12)))) & 0xffffffu));
    (*((uint16_t *)((uint8_t *)(stack_record_10 + 8) + 0u))) =
         CONCAT11((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xb5))))) * 1u)))),
                  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((byte)param_4[0x2e]) * 1u)))));
    (*((uint32_t *)(stack_record_10 + 8))) = CONCAT22(CONCAT11((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xbf))))) * 1u)))),
                                 (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xb2))))) * 1u))))),
                        (undefined2)(*((uint32_t *)(stack_record_10 + 8))));
    (*((uint32_t *)(stack_record_10 + 4))) = (*((uint32_t *)(stack_record_10 + 4))) ^ param_4[5];
    (*((uint32_t *)(stack_record_10 + 8))) = (*((uint32_t *)(stack_record_10 + 8))) ^ param_4[6];
    (*((uint32_t *)(stack_record_10 + 12))) = (*((uint32_t *)(stack_record_10 + 12))) ^ param_4[7];
    param_4[0x2c] =
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x25100u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 0))) >> 0x18) * 4) * 1u)))) ^
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24d00u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 0))) >> 0x10 & 0xff) * 4) * 1u)))) ^
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24900u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 0))) >> 8 & 0xff) * 4) * 1u)))) ^
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24500u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 0))) & 0xff) * 4) * 1u))));
    param_4[0x2d] =
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x25100u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 4))) >> 0x18) * 4) * 1u)))) ^
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24d00u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 4))) >> 0x10 & 0xff) * 4) * 1u)))) ^
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24900u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 4))) >> 8 & 0xff) * 4) * 1u)))) ^
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24500u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 4))) & 0xff) * 4) * 1u))));
    param_4[0x2e] =
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x25100u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 8))) >> 0x18) * 4) * 1u)))) ^
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24d00u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 8))) >> 0x10 & 0xff) * 4) * 1u)))) ^
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24900u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 8))) >> 8 & 0xff) * 4) * 1u)))) ^
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24500u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 8))) & 0xff) * 4) * 1u))));
    param_4[0x2f] =
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x25100u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 12))) >> 0x18) * 4) * 1u)))) ^
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24d00u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 12))) >> 0x10 & 0xff) * 4) * 1u)))) ^
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24900u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 12))) >> 8 & 0xff) * 4) * 1u)))) ^
         *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24500u + (uint32_t)(((*((uint32_t *)(stack_record_10 + 12))) & 0xff) * 4) * 1u))));
    bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((byte)param_4[0x2e]) * 1u))));
    bVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xb5))))) * 1u))));
    bVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xb2))))) * 1u))));
    bVar4 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xbf))))) * 1u))));
    (*((uint16_t *)((uint8_t *)(stack_record_10 + 12) + 0u))) =
         CONCAT11((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xb9))))) * 1u)))),
                  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((byte)param_4[0x2f]) * 1u)))));
    (*((uint16_t *)((uint8_t *)stack_record_10 + 0u))) =
         CONCAT11((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xbd))))) * 1u)))),
                  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((byte)param_4[0x2c]) * 1u)))));
    (*((uint32_t *)(stack_record_10 + 0))) = CONCAT22(CONCAT11((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xb7))))) * 1u)))),
                                 (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xba))))) * 1u))))),
                        (undefined2)(*((uint32_t *)(stack_record_10 + 0))));
    (*((uint32_t *)(stack_record_10 + 12))) = ((*((uint32_t *)(stack_record_10 + 12))) & ~0xffffffu) | ((uint32_t)(CONCAT12((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xb6))))) * 1u)))),
                  (undefined2)(*((uint32_t *)(stack_record_10 + 12))))) & 0xffffffu);
    bVar5 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xb3))))) * 1u))));
    (*((uint32_t *)(stack_record_10 + 4))) = CONCAT31(CONCAT12((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xbb))))) * 1u)))),
                                 CONCAT11((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xbe))))) * 1u)))),
                                          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xb1))))) * 1u)))))),
                        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x90f1u + (uint32_t)((byte)param_4[0x2d]) * 1u)))));
    param_4[0x2c] = *param_4 ^ (*((uint32_t *)(stack_record_10 + 0)));
    (*((uint32_t *)(stack_record_10 + 12))) = CONCAT13(bVar5,((uint32_t)((*((uint32_t *)(stack_record_10 + 12)))) & 0xffffffu));
    (*((uint16_t *)((uint8_t *)(stack_record_10 + 8) + 0u))) = CONCAT11(bVar2,bVar1);
    (*((uint32_t *)(stack_record_10 + 8))) = CONCAT22(CONCAT11(bVar4,bVar3),(undefined2)(*((uint32_t *)(stack_record_10 + 8))));
    param_4[0x2d] = param_4[1] ^ (*((uint32_t *)(stack_record_10 + 4)));
    param_4[0x2e] = param_4[2] ^ (*((uint32_t *)(stack_record_10 + 8)));
    param_4[0x2f] = param_4[3] ^ (*((uint32_t *)(stack_record_10 + 12)));
    if ((((uint)camry_host_addr(param_2) & 3) == 0) && (((uint)camry_host_addr(param_4) & 3) == 0)) {
      *param_2 = param_4[0x2c];
      param_2[1] = param_4[0x2d];
      param_2[2] = param_4[0x2e];
      param_2[3] = param_4[0x2f];
    }
    else {
      *(char *)param_2 = (char)param_4[0x2c];
      (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 1)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xb1))));
      (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 2)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xb2))));
      (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 3)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xb3))));
      *(char *)(param_2 + 1) = (char)param_4[0x2d];
      (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 5)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xb5))));
      (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 6)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xb6))));
      (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 7)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xb7))));
      *(char *)(param_2 + 2) = (char)param_4[0x2e];
      (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 9)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xb9))));
      (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 10)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xba))));
      (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 0xb)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xbb))));
      *(char *)(param_2 + 3) = (char)param_4[0x2f];
      (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 0xd)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xbd))));
      (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 0xe)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xbe))));
      (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 0xf)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_4) + 0xbf))));
    }
    uVar7 = 0;
  }
  return uVar7;
}
