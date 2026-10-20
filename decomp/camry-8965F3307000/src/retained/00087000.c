#include "common.h"

undefined4 expand_aes128_key_and_mark_context_initialized_876c4(uint *param_1,char param_2,uint *param_3)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  
  if (param_2 == '\x10') {
    param_3[0x2c] = 0;
    param_3[0x2d] = 0;
    param_3[0x2e] = 0;
    param_3[0x2f] = 0;
    if ((((uint)camry_host_addr(param_3) & 3) == 0) && (((uint)camry_host_addr(param_1) & 3) == 0)) {
      *param_3 = *param_1;
      param_3[1] = param_1[1];
      param_3[2] = param_1[2];
      param_3[3] = param_1[3];
    }
    else {
      *(char *)param_3 = (char)*param_1;
      (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 1)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 1))));
      (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 2)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 2))));
      (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 3)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 3))));
      *(char *)(param_3 + 1) = (char)param_1[1];
      (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 5)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 5))));
      (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 6)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 6))));
      (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 7)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 7))));
      *(char *)(param_3 + 2) = (char)param_1[2];
      (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 9)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 9))));
      (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 10)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 10))));
      (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0xb)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb))));
      *(char *)(param_3 + 3) = (char)param_1[3];
      (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0xd)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xd))));
      (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0xe)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xe))));
      (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0xf)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xf))));
    }
    (*((undefined *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x13)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uint)(byte)param_3[3] * 4) * 1u))));
    (*((undefined *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x12)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0xf)))) * 4) * 1u))));
    (*((undefined *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x11)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0xe)))) * 4) * 1u))));
    *(byte *)(param_3 + 4) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0xd)))) * 4) * 1u)))) ^ DAT_000234ed
    ;
    uVar5 = param_3[4] ^ *param_3;
    uVar3 = param_3[1] ^ uVar5;
    param_3[4] = uVar5;
    uVar4 = param_3[2] ^ uVar3;
    param_3[5] = uVar3;
    uVar2 = param_3[3] ^ uVar4;
    param_3[6] = uVar4;
    param_3[7] = uVar2;
    (*((undefined *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x23)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uVar2 & 0xff) * 4) * 1u))));
    (*((undefined *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x22)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x1f)))) * 4) * 1u))));
    (*((undefined *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x21)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x1e)))) * 4) * 1u))));
    *(byte *)(param_3 + 8) =
         (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x1d)))) * 4) * 1u)))) ^ DAT_000234ee;
    uVar5 = param_3[8] ^ uVar5;
    uVar3 = uVar5 ^ uVar3;
    param_3[8] = uVar5;
    param_3[9] = uVar3;
    uVar4 = uVar3 ^ uVar4;
    uVar2 = uVar4 ^ uVar2;
    param_3[10] = uVar4;
    param_3[0xb] = uVar2;
    (*((undefined *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x33)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uVar2 & 0xff) * 4) * 1u))));
    (*((undefined *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x32)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x2f)))) * 4) * 1u))));
    (*((undefined *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x31)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x2e)))) * 4) * 1u))));
    *(byte *)(param_3 + 0xc) =
         (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x2d)))) * 4) * 1u)))) ^ DAT_000234ef;
    uVar5 = param_3[0xc] ^ uVar5;
    uVar3 = uVar5 ^ uVar3;
    param_3[0xc] = uVar5;
    param_3[0xd] = uVar3;
    uVar4 = uVar3 ^ uVar4;
    uVar2 = uVar4 ^ uVar2;
    param_3[0xe] = uVar4;
    param_3[0xf] = uVar2;
    (*((undefined *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x43)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uVar2 & 0xff) * 4) * 1u))));
    (*((undefined *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x42)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x3f)))) * 4) * 1u))));
    (*((undefined *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x41)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x3e)))) * 4) * 1u))));
    *(byte *)(param_3 + 0x10) =
         (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x3d)))) * 4) * 1u)))) ^ DAT_000234f0;
    uVar5 = param_3[0x10] ^ uVar5;
    param_3[0x10] = uVar5;
    uVar3 = uVar5 ^ uVar3;
    param_3[0x11] = uVar3;
    uVar4 = uVar3 ^ uVar4;
    uVar2 = uVar4 ^ uVar2;
    param_3[0x12] = uVar4;
    param_3[0x13] = uVar2;
    (*((undefined *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x53)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uVar2 & 0xff) * 4) * 1u))));
    (*((undefined *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x52)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x4f)))) * 4) * 1u))));
    (*((undefined *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x51)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x4e)))) * 4) * 1u))));
    *(byte *)(param_3 + 0x14) =
         (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x4d)))) * 4) * 1u)))) ^ DAT_000234f1;
    uVar5 = param_3[0x14] ^ uVar5;
    param_3[0x14] = uVar5;
    uVar3 = uVar5 ^ uVar3;
    param_3[0x15] = uVar3;
    uVar4 = uVar3 ^ uVar4;
    uVar2 = uVar4 ^ uVar2;
    param_3[0x16] = uVar4;
    param_3[0x17] = uVar2;
    (*((undefined *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 99)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uVar2 & 0xff) * 4) * 1u))));
    (*((undefined *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x62)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x5f)))) * 4) * 1u))));
    (*((undefined *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x61)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x5e)))) * 4) * 1u))));
    *(byte *)(param_3 + 0x18) =
         (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x5d)))) * 4) * 1u)))) ^ DAT_000234f2;
    uVar5 = param_3[0x18] ^ uVar5;
    param_3[0x18] = uVar5;
    uVar3 = uVar5 ^ uVar3;
    param_3[0x19] = uVar3;
    uVar4 = uVar3 ^ uVar4;
    uVar2 = uVar4 ^ uVar2;
    param_3[0x1a] = uVar4;
    param_3[0x1b] = uVar2;
    (*((undefined *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x73)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uVar2 & 0xff) * 4) * 1u))));
    (*((undefined *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x72)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x6f)))) * 4) * 1u))));
    (*((undefined *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x71)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x6e)))) * 4) * 1u))));
    *(byte *)(param_3 + 0x1c) =
         (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x6d)))) * 4) * 1u)))) ^ DAT_000234f3;
    uVar5 = param_3[0x1c] ^ uVar5;
    param_3[0x1c] = uVar5;
    uVar3 = uVar5 ^ uVar3;
    param_3[0x1d] = uVar3;
    uVar4 = uVar3 ^ uVar4;
    uVar2 = uVar4 ^ uVar2;
    param_3[0x1e] = uVar4;
    param_3[0x1f] = uVar2;
    (*((undefined *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x83)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uVar2 & 0xff) * 4) * 1u))));
    (*((undefined *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x82)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x7f)))) * 4) * 1u))));
    (*((undefined *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x81)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x7e)))) * 4) * 1u))));
    *(byte *)(param_3 + 0x20) =
         (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x7d)))) * 4) * 1u)))) ^ DAT_000234f4;
    uVar5 = param_3[0x20] ^ uVar5;
    uVar3 = uVar5 ^ uVar3;
    param_3[0x20] = uVar5;
    param_3[0x21] = uVar3;
    uVar4 = uVar3 ^ uVar4;
    uVar2 = uVar4 ^ uVar2;
    param_3[0x22] = uVar4;
    param_3[0x23] = uVar2;
    (*((undefined *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x93)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uVar2 & 0xff) * 4) * 1u))));
    (*((undefined *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x92)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x8f)))) * 4) * 1u))));
    (*((undefined *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x91)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x8e)))) * 4) * 1u))));
    *(byte *)(param_3 + 0x24) =
         (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x8d)))) * 4) * 1u)))) ^ DAT_000234f5;
    uVar5 = param_3[0x24] ^ uVar5;
    uVar3 = uVar5 ^ uVar3;
    param_3[0x24] = uVar5;
    param_3[0x25] = uVar3;
    uVar4 = uVar3 ^ uVar4;
    uVar2 = uVar4 ^ uVar2;
    param_3[0x26] = uVar4;
    param_3[0x27] = uVar2;
    (*((undefined *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0xa3)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uVar2 & 0xff) * 4) * 1u))));
    (*((undefined *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0xa2)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x9f)))) * 4) * 1u))));
    (*((undefined *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0xa1)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x9e)))) * 4) * 1u))));
    *(byte *)(param_3 + 0x28) =
         (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x9d)))) * 4) * 1u)))) ^ DAT_000234f6;
    uVar1 = param_3[0x28];
    param_3[0x28] = uVar1 ^ uVar5;
    uVar3 = uVar1 ^ uVar5 ^ uVar3;
    param_3[0x29] = uVar3;
    uVar3 = uVar3 ^ uVar4;
    param_3[0x2a] = uVar3;
    param_3[0x2b] = uVar3 ^ uVar2;
    *(undefined1 *)(param_3 + 0x30) = 1;
    return 0;
  }
  return 0xff;
}

void clear_aes128_block_context_196_bytes_87ac2(undefined4 *param_1)

{
  int iVar1;
  undefined4 *puVar2;
  
  *param_1 = 0;
  param_1[1] = 0;
  param_1[2] = 0;
  param_1[3] = 0;
  param_1[4] = 0;
  param_1[5] = 0;
  param_1[6] = 0;
  param_1[7] = 0;
  param_1[8] = 0;
  param_1[9] = 0;
  param_1[10] = 0;
  param_1[0xb] = 0;
  param_1[0xc] = 0;
  param_1[0xd] = 0;
  param_1[0xe] = 0;
  param_1[0xf] = 0;
  param_1[0x10] = 0;
  param_1[0x11] = 0;
  param_1[0x12] = 0;
  param_1[0x13] = 0;
  param_1[0x14] = 0;
  param_1[0x15] = 0;
  param_1[0x16] = 0;
  param_1[0x17] = 0;
  param_1[0x18] = 0;
  param_1[0x19] = 0;
  param_1[0x1a] = 0;
  param_1[0x1b] = 0;
  param_1[0x1c] = 0;
  param_1[0x1d] = 0;
  param_1[0x1e] = 0;
  param_1[0x1f] = 0;
  param_1[0x20] = 0;
  param_1[0x21] = 0;
  param_1[0x22] = 0;
  param_1[0x23] = 0;
  param_1[0x24] = 0;
  param_1[0x25] = 0;
  param_1[0x26] = 0;
  param_1[0x27] = 0;
  param_1[0x28] = 0;
  param_1[0x29] = 0;
  param_1[0x2a] = 0;
  param_1[0x2b] = 0;
  param_1[0x2c] = 0;
  param_1[0x2d] = 0;
  param_1[0x2e] = 0;
  param_1[0x2f] = 0;
  puVar2 = param_1 + 0x30;
  for (iVar1 = 4; iVar1 + -0x20 < 0 == (iVar1 < 0 && -1 < iVar1 + -0x20); iVar1 = iVar1 + -0x20) {
    *puVar2 = 0;
    puVar2[1] = 0;
    puVar2[2] = 0;
    puVar2[3] = 0;
    puVar2[4] = 0;
    puVar2[5] = 0;
    puVar2[6] = 0;
    puVar2[7] = 0;
    puVar2 = puVar2 + 8;
  }
  for (; iVar1 + -0x10 < 0 == (iVar1 < 0 && -1 < iVar1 + -0x10); iVar1 = iVar1 + -0x10) {
    *puVar2 = 0;
    puVar2[1] = 0;
    puVar2[2] = 0;
    puVar2[3] = 0;
    puVar2 = puVar2 + 4;
  }
  for (; 0 < iVar1; iVar1 = iVar1 + -4) {
    *puVar2 = 0;
    puVar2 = puVar2 + 1;
  }
  *(undefined1 *)(param_1 + 0x30) = 0;
  return;
}

int initialize_aes128_counter_context_and_iv_87b74(undefined4 param_1,undefined1 param_2,undefined4 *param_3,char param_4,uint param_5
                )

{
  int iVar1;
  bool bVar2;
  
  if (param_4 == '\x10') {
    (*((undefined4 *)camry_host_ptr((uint32_t)(param_5 + 0xc4)))) = 0;
    (*((undefined4 *)camry_host_ptr((uint32_t)(param_5 + 200)))) = 0;
    (*((undefined4 *)camry_host_ptr((uint32_t)(param_5 + 0xcc)))) = 0;
    (*((undefined4 *)camry_host_ptr((uint32_t)(param_5 + 0xd0)))) = 0;
    if (((param_5 & 3) == 0) && (((uint)camry_host_addr(param_3) & 3) == 0)) {
      (*((undefined4 *)camry_host_ptr((uint32_t)(param_5 + 0xd4)))) = *param_3;
      (*((undefined4 *)camry_host_ptr((uint32_t)(param_5 + 0xd8)))) = param_3[1];
      (*((undefined4 *)camry_host_ptr((uint32_t)(param_5 + 0xdc)))) = param_3[2];
      (*((undefined4 *)camry_host_ptr((uint32_t)(param_5 + 0xe0)))) = param_3[3];
    }
    else {
      (*((undefined1 *)camry_host_ptr((uint32_t)(param_5 + 0xd4)))) = *(undefined1 *)param_3;
      (*((undefined1 *)camry_host_ptr((uint32_t)(param_5 + 0xd5)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 1))));
      (*((undefined1 *)camry_host_ptr((uint32_t)(param_5 + 0xd6)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 2))));
      (*((undefined1 *)camry_host_ptr((uint32_t)(param_5 + 0xd7)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 3))));
      (*((undefined1 *)camry_host_ptr((uint32_t)(param_5 + 0xd8)))) = *(undefined1 *)(param_3 + 1);
      (*((undefined1 *)camry_host_ptr((uint32_t)(param_5 + 0xd9)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 5))));
      (*((undefined1 *)camry_host_ptr((uint32_t)(param_5 + 0xda)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 6))));
      (*((undefined1 *)camry_host_ptr((uint32_t)(param_5 + 0xdb)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 7))));
      (*((undefined1 *)camry_host_ptr((uint32_t)(param_5 + 0xdc)))) = *(undefined1 *)(param_3 + 2);
      (*((undefined1 *)camry_host_ptr((uint32_t)(param_5 + 0xdd)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 9))));
      (*((undefined1 *)camry_host_ptr((uint32_t)(param_5 + 0xde)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 10))));
      (*((undefined1 *)camry_host_ptr((uint32_t)(param_5 + 0xdf)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0xb))));
      (*((undefined1 *)camry_host_ptr((uint32_t)(param_5 + 0xe0)))) = *(undefined1 *)(param_3 + 3);
      (*((undefined1 *)camry_host_ptr((uint32_t)(param_5 + 0xe1)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0xd))));
      (*((undefined1 *)camry_host_ptr((uint32_t)(param_5 + 0xe2)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0xe))));
      (*((undefined1 *)camry_host_ptr((uint32_t)(param_5 + 0xe3)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0xf))));
    }
    iVar1 = expand_aes128_key_and_mark_context_initialized_876c4(((uint *)camry_host_ptr((uint32_t)(param_1))), param_2, ((uint *)camry_host_ptr((uint32_t)(param_5))));
    bVar2 = iVar1 == 0;
  }
  else {
    bVar2 = false;
    iVar1 = 0xff;
  }
  (*((bool *)camry_host_ptr((uint32_t)(param_5 + 0xc0)))) = bVar2;
  return iVar1;
}

undefined4 aes128_counter_xor_block_and_increment_big_endian_counter_87c40(uint *param_1,uint *param_2,undefined1 param_3,int param_4)

{
  uint8_t stack_record_20[32];
  int iVar1;
  char cVar2;
  int iVar3;
  undefined4 uVar4;
  char *pcVar5;
  
  if ((((((*((int *)camry_host_ptr((uint32_t)(param_4 + 0xd4)))) == -1) && ((*((int *)camry_host_ptr((uint32_t)(param_4 + 0xd8)))) == -1)) &&
       ((*((int *)camry_host_ptr((uint32_t)(param_4 + 0xdc)))) == -1)) && ((*((int *)camry_host_ptr((uint32_t)(param_4 + 0xe0)))) == -1)) ||
     (iVar3 = aes128_encrypt_16byte_block_with_initialized_context_863a0(((undefined4 *)camry_host_ptr((uint32_t)(param_4 + 0xd4))), ((uint32_t *)(stack_record_20)), param_3,  param_4), iVar3 != 0)) {
    uVar4 = 0xff;
  }
  else {
    if ((((uint)camry_host_addr(param_2) & 3) == 0) && (((uint)camry_host_addr(param_1) & 3) == 0)) {
      *param_2 = *param_1 ^ (*((uint32_t *)(stack_record_20 + 0)));
      param_2[1] = param_1[1] ^ (*((uint32_t *)(stack_record_20 + 4)));
      param_2[2] = param_1[2] ^ (*((uint32_t *)(stack_record_20 + 8)));
      param_2[3] = param_1[3] ^ (*((uint32_t *)(stack_record_20 + 12)));
    }
    else {
      *(byte *)param_2 = (byte)*param_1 ^ (byte)(*((uint32_t *)(stack_record_20 + 0)));
      (*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 1)))) = (*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 1)))) ^ (*((uint8_t *)((uint8_t *)((uint32_t *)(stack_record_20)) + 1u)));
      (*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 2)))) = (*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 2)))) ^ (*((uint8_t *)((uint8_t *)((uint32_t *)(stack_record_20)) + 2u)));
      (*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 3)))) = (*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 3)))) ^ (*((uint8_t *)((uint8_t *)((uint32_t *)(stack_record_20)) + 3u)));
      *(byte *)(param_2 + 1) = (byte)param_1[1] ^ (byte)(*((uint32_t *)(stack_record_20 + 4)));
      (*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 5)))) = (*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 5)))) ^ (*((uint8_t *)((uint8_t *)((uint32_t *)((stack_record_20 + 4))) + 1u)));
      (*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 6)))) = (*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 6)))) ^ (*((uint8_t *)((uint8_t *)((uint32_t *)((stack_record_20 + 4))) + 2u)));
      (*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 7)))) = (*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 7)))) ^ (*((uint8_t *)((uint8_t *)((uint32_t *)((stack_record_20 + 4))) + 3u)));
      *(byte *)(param_2 + 2) = (byte)param_1[2] ^ (byte)(*((uint32_t *)(stack_record_20 + 8)));
      (*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 9)))) = (*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 9)))) ^ (*((uint8_t *)((uint8_t *)((uint32_t *)((stack_record_20 + 8))) + 1u)));
      (*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 10)))) = (*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 10)))) ^ (*((uint8_t *)((uint8_t *)((uint32_t *)((stack_record_20 + 8))) + 2u)));
      (*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 0xb)))) = (*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb)))) ^ (*((uint8_t *)((uint8_t *)((uint32_t *)((stack_record_20 + 8))) + 3u)));
      *(byte *)(param_2 + 3) = (byte)param_1[3] ^ (byte)(*((uint32_t *)(stack_record_20 + 12)));
      (*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 0xd)))) = (*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xd)))) ^ (*((uint8_t *)((uint8_t *)((uint32_t *)((stack_record_20 + 12))) + 1u)));
      (*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 0xe)))) = (*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xe)))) ^ (*((uint8_t *)((uint8_t *)((uint32_t *)((stack_record_20 + 12))) + 2u)));
      (*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 0xf)))) = (*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xf)))) ^ (*((uint8_t *)((uint8_t *)((uint32_t *)((stack_record_20 + 12))) + 3u)));
    }
    iVar3 = 3;
    do {
      iVar1 = iVar3 * 4 + param_4;
      pcVar5 = ((char *)camry_host_ptr((uint32_t)(iVar1 + 0xd7)));
      cVar2 = *pcVar5 + '\x01';
      *pcVar5 = cVar2;
      if ((cVar2 == '\0') &&
         (pcVar5 = ((char *)camry_host_ptr((uint32_t)(iVar1 + 0xd6))), cVar2 = *pcVar5 + '\x01', *pcVar5 = cVar2, cVar2 == '\0')
         ) {
        iVar1 = iVar3 * 4 + param_4;
        cVar2 = (*((char *)camry_host_ptr((uint32_t)(iVar1 + 0xd5)))) + '\x01';
        (*((char *)camry_host_ptr((uint32_t)(iVar1 + 0xd5)))) = cVar2;
        if (cVar2 == '\0') {
          (*((char *)camry_host_ptr((uint32_t)(iVar1 + 0xd4)))) = (*((char *)camry_host_ptr((uint32_t)(iVar1 + 0xd4)))) + '\x01';
        }
      }
    } while (((*((int *)camry_host_ptr((uint32_t)(iVar3 * 4 + param_4 + 0xd4)))) == 0) &&
            (iVar1 = iVar3 + -1, iVar3 = iVar3 + -1, -1 < iVar1));
    uVar4 = 0;
  }
  return uVar4;
}

undefined4 thunk_initialize_crypto_scheduler_with_three_step_check_8844e(void)

{
  return initialize_crypto_scheduler_with_three_step_check_8844e();
}

undefined4 thunk_initialize_crypto_scheduler_without_three_step_check_884ea(void)

{
  return initialize_crypto_scheduler_without_three_step_check_884ea();
}

undefined4 thunk_combine_icus_readiness_with_crypto_scheduler_status_886e0(void)

{
  return combine_icus_readiness_with_crypto_scheduler_status_886e0();
}

void thunk_nvm_request_suspend_with_service_guards_7995c(void)

{
  nvm_request_suspend_with_service_guards_7995c();
  return;
}

void thunk_nvm_cancel_or_resume_suspend_and_clear_state_799da(void)

{
  nvm_cancel_or_resume_suspend_and_clear_state_799da();
  return;
}

void release_icus_request_and_notify_crypto_scheduler_87edc(undefined1 param_1)

{
  write_fhve3_and_fhve15_bit_zero_8aa1c(((undefined *)camry_host_ptr(0xfebf10d0u)));
  ((void)(param_1), thunk_nvm_resume_completed_suspend_and_clear_state_799b0());
  return;
}

void translate_icus_scheduler_result_and_update_crypto_state_87ef6(char param_1)

{
  undefined1 uVar1;
  
  if (param_1 == '\0') {
    DAT_febf10d0 = 0;
    DAT_febf10d4 = 0;
    read_fhve3_and_fhve15_if_nonnull_8aa04(((undefined *)camry_host_ptr(0xfebf10d0u)));
    uVar1 = 0;
  }
  else {
    uVar1 = 1;
    if (param_1 != '\x01') {
      uVar1 = 0xff;
    }
  }
  advance_crypto_scheduler_and_invoke_guarded_callbacks_885b2(uVar1);
  return;
}

void reset_key_job_buffers_and_completion_state_87f22(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  memzero(((undefined *)camry_host_ptr(0xfebf10f4u)),0x78);
  memzero(((undefined *)camry_host_ptr((uint32_t)(puVar1 + 0x58d8))), 8);
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x58e4)))) = 0xffffffff;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x58e0)))) = 0xffffffff;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x58f0))))) = 0xd2;
  return;
}

undefined4 prepare_64byte_key_request_with_48byte_output_87f52(void *param_1,int param_2,undefined4 param_3,uint param_4,uint *param_5)

{
  undefined4 uVar1;
  
  if ((((camry_host_addr((param_1))== 0) || (param_4 == 0)) || (camry_host_addr((param_5))== 0)) ||
     (param_2 != 0x40)) {
    uVar1 = 1;
  }
  else if (*param_5 < 0x30) {
    uVar1 = 3;
  }
  else {
    uVar1 = 0;
    DAT_febf10d8 = camry_host_addr(param_5);
    DAT_febf10e0 = ~(uint)camry_host_addr(param_5);
    DAT_febf10e4 = ~param_4;
    DAT_febf10f4 = ((uint32_t)(0xfebf10fcu));
    DAT_febf10f8 = ((uint32_t)(0xfebf113cu));
    DAT_febf10dc = param_4;
    memcpy_forward(((undefined *)camry_host_ptr(0xfebf10fcu)),param_1,0x10);
    memcpy_forward(((undefined *)camry_host_ptr(0xfebf110cu)),((void *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0x10))),0x20);
    memcpy_forward(((undefined *)camry_host_ptr(0xfebf112cu)),((void *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0x30))),0x10);
  }
  return uVar1;
}

void complete_key_job_copy_48bytes_or_clear_output_87fd8(uchar param_1)

{
  uint *puVar1;
  uint32_t pvVar2;
  uint32_t puVar3;
  uint32_t puVar4;
  
  pvVar2 = (uint32_t)((uint32_t)(DAT_febf10dc));
  puVar1 = ((void *)camry_host_ptr((uint32_t)(DAT_febf10d8)));
  puVar3 = 0xfebeb800u;
  puVar4 = (0xfebeb800u);
  if ((DAT_febf10dc == 0) || (DAT_febf10d8 == 0)) {
    param_1 = '\x01';
  }
  else if ((~(uint)DAT_febf10dc == DAT_febf10e4) && (~(uint)DAT_febf10d8 == DAT_febf10e0)) {
    if (param_1 == '\0') {
      puVar3 = 0xfebeb800u;
      memcpy_forward(((void *)camry_host_ptr((uint32_t)(DAT_febf10dc))), ((undefined *)camry_host_ptr(0xfebf113cu)), 0x20);
      memcpy_forward(((void *)camry_host_ptr((uint32_t)((int)pvVar2 + 0x20))),((undefined *)camry_host_ptr(0xfebf115cu)),0x10);
      *puVar1 = 0x30;
    }
    else {
      memzero(((void *)camry_host_ptr((uint32_t)(DAT_febf10dc))), (*((volatile uint32_t *)camry_host_ptr((uint32_t)(DAT_febf10d8)))));
    }
    puVar4 = ((uint32_t)(puVar3));
    memzero(((undefined *)camry_host_ptr((uint32_t)(puVar3 + 0x58fc))), 0x40);
    memzero(((undefined *)camry_host_ptr((uint32_t)(0x5936u + (int)(puVar3 + 6)))), 0x30);
  }
  else {
    param_1 = '\x01';
    DAT_febf1191 = 1;
  }
  crypto_key_job_deliver_completion(param_1);
  if (((int8_t)(*((volatile undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(0x5990) * 1u))))) == -0x3d) {
    release_icus_request_and_notify_crypto_scheduler_87edc(0);
    (*((volatile undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(0x5990) * 1u)))) = 0xe1;
  }
  return;
}
