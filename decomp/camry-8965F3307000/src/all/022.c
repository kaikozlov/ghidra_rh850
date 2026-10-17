#include "common.h"


void FUN_000880e0(void)

{
  undefined1 uVar1;
  uint32_t puVar2;
  undefined4 uVar3;
  int iVar4;
  
  puVar2 = 0xfebeb800u;
  if (((int8_t)DAT_febf1190) == -0x4c) {
    iVar4 = FUN_0008af10();
    if (iVar4 == 1) {
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0x5998)))) = 0xffffffff;
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0x5994)))) = 0;
      uVar1 = 0xc3;
      uVar3 = 0;
    }
    else {
      if (iVar4 == 0) {
        return;
      }
      if (iVar4 == 0x12) {
        return;
      }
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0x5994)))) = 0;
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0x5998)))) = 0xffffffff;
      uVar3 = FUN_0008afea();
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0x5984)))) = uVar3;
      FUN_00087edc(0);
      uVar1 = 0xe1;
      uVar3 = 1;
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x5990))))) = uVar1;
    FUN_00088086(uVar3);
  }
  return;
}



undefined4 FUN_0008834a(void)

{
  undefined4 uVar1;
  
  if (((int8_t)DAT_febf10f0) != -0x1f) {
    if (((int8_t)DAT_febf10f0) == -0x2e) {
      uVar1 = 0;
    }
    else {
      uVar1 = 2;
    }
    return uVar1;
  }
  return 0;
}



/* Sequential initializer chain: 4 unconditional calls and no other statements; shape-verified. The
   called sequence is the function's entire behavior; chain family members differ in callee sets. */

void f33_run_init_chain_8838a(void)

{
  FUN_00088b52();
  FUN_00088f92();
  FUN_0008874c();
  FUN_00087f22();
  return;
}



undefined4 FUN_00088574(void)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  undefined4 uVar4;
  
  iVar1 = FUN_0008aca8();
  iVar3 = 0x9c4;
  do {
    if (iVar1 != 0) break;
    iVar1 = FUN_0008af10();
    iVar3 = iVar3 + -1;
  } while (iVar3 != 0);
  if (((iVar1 == 0x20) || (iVar1 == 1)) ||
     ((iVar1 != 0 && (uVar2 = f33_icus20_read_bit0(), uVar2 != 1)))) {
    uVar4 = 1;
  }
  else {
    uVar4 = 2;
  }
  f33_run_init_chain_8838a();
  return uVar4;
}



int FUN_0008864e(void)

{
  int iVar1;
  
  if ((((((int8_t)DAT_febf1190) == -0x4c) || (((int8_t)DAT_febf1190) == -0x3d)) || (((int8_t)DAT_febf1190) == -0x2e)) ||
     (((int8_t)DAT_febf1190) == -0x1f)) {
    if (((((int8_t)DAT_febf116c) == -0x2e) || (((int8_t)DAT_febf116c) == -0x1f)) && (DAT_febf1191 == '\0')) {
      iVar1 = FUN_00088f7a();
      if (((iVar1 == 0) && (iVar1 = FUN_00089386(), iVar1 == 0)) &&
         (iVar1 = FUN_00088b3a(), iVar1 == 0)) {
        iVar1 = FUN_0008834a();
      }
    }
    else {
      iVar1 = 2;
    }
  }
  else if (((int8_t)DAT_febf1190) == -0x5b) {
    if (DAT_febf1170 < 7) {
      iVar1 = 0x21;
      if (0xb < DAT_febf1178) {
        iVar1 = 0x22;
      }
    }
    else {
      iVar1 = 0x20;
    }
  }
  else if (DAT_febf1190 == '\x0f') {
    iVar1 = 3;
  }
  else if (DAT_febf1190 == '\0') {
    iVar1 = 1;
  }
  else {
    iVar1 = 2;
  }
  return iVar1;
}



void FUN_0008874c(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  f33_memzero(((undefined *)camry_host_ptr(0xfebf11d8u)),0x1c);
  f33_memzero(((undefined *)camry_host_ptr((uint32_t)(puVar1 + 0x59b0))), 0x28);
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x599c)))) = 0xffffffff;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x59a0)))) = 0xffffffff;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x59ac))))) = 0xd2;
  return;
}



void FUN_000888d0(void)

{
  undefined1 uVar1;
  uint32_t puVar2;
  undefined4 uVar3;
  int iVar4;
  
  puVar2 = 0xfebeb800u;
  if (((int8_t)DAT_febf1190) == -0x4c) {
    iVar4 = FUN_0008af10();
    if (iVar4 == 1) {
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0x5998)))) = 0xffffffff;
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0x5994)))) = 0;
      uVar1 = 0xc3;
      uVar3 = 0;
    }
    else {
      if (iVar4 == 0) {
        return;
      }
      if (iVar4 == 0x12) {
        return;
      }
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0x5994)))) = 0;
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0x5998)))) = 0xffffffff;
      uVar3 = FUN_0008afea();
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0x5984)))) = uVar3;
      FUN_00087edc(0);
      uVar1 = 0xe1;
      uVar3 = 1;
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x5990))))) = uVar1;
    FUN_00088876(uVar3);
  }
  return;
}



undefined4 FUN_00088b3a(void)

{
  undefined4 uVar1;
  
  if (((int8_t)DAT_febf11ac) != -0x1f) {
    if (((int8_t)DAT_febf11ac) == -0x2e) {
      uVar1 = 0;
    }
    else {
      uVar1 = 2;
    }
    return uVar1;
  }
  return 0;
}



void FUN_00088b52(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  f33_memzero(((undefined *)camry_host_ptr(0xfebf1208u)),0x18);
  f33_memzero(((undefined *)camry_host_ptr((uint32_t)(puVar1 + 0x5a20))), 0x68);
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x59f8)))) = 0xffffffff;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x59f4)))) = 0xffffffff;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x5a04u + (uint32_t)((int)puVar1))))) = (code)0xd2;
  return;
}



void FUN_00088d04(void)

{
  undefined1 uVar1;
  uint32_t puVar2;
  undefined4 uVar3;
  int iVar4;
  
  puVar2 = 0xfebeb800u;
  if (((int8_t)DAT_febf1190) == -0x4c) {
    iVar4 = FUN_0008af10();
    if (iVar4 == 1) {
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0x5998)))) = 0xffffffff;
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0x5994)))) = 0;
      uVar1 = 0xc3;
      uVar3 = 0;
    }
    else {
      if (iVar4 == 0) {
        return;
      }
      if (iVar4 == 0x12) {
        return;
      }
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0x5994)))) = 0;
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0x5998)))) = 0xffffffff;
      uVar3 = FUN_0008afea();
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0x5984)))) = uVar3;
      FUN_00087edc(0);
      uVar1 = 0xe1;
      uVar3 = 1;
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x5990))))) = uVar1;
    FUN_00088caa(uVar3);
  }
  return;
}



undefined4 FUN_00088f7a(void)

{
  undefined4 uVar1;
  
  if (((int8_t)DAT_febf1204) != -0x1f) {
    if (((int8_t)DAT_febf1204) == -0x2e) {
      uVar1 = 0;
    }
    else {
      uVar1 = 2;
    }
    return uVar1;
  }
  return 0;
}



void FUN_00088f92(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  f33_memzero(((undefined *)camry_host_ptr(0xfebf1298u)),0x20);
  f33_memzero(((undefined *)camry_host_ptr((uint32_t)(puVar1 + 0x5ab8))), 100);
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x5a8c)))) = 0xffffffff;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x5a94))))) = 0xd2;
  return;
}



void FUN_00089114(void)

{
  undefined1 uVar1;
  uint32_t puVar2;
  undefined4 uVar3;
  int iVar4;
  
  puVar2 = 0xfebeb800u;
  if (((int8_t)DAT_febf1190) == -0x4c) {
    iVar4 = FUN_0008af10();
    if (iVar4 == 1) {
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0x5998)))) = 0xffffffff;
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0x5994)))) = 0;
      uVar1 = 0xc3;
      uVar3 = 0;
    }
    else {
      if (iVar4 == 0) {
        return;
      }
      if (iVar4 == 0x12) {
        return;
      }
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0x5994)))) = 0;
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0x5998)))) = 0xffffffff;
      uVar3 = FUN_0008afea();
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0x5984)))) = uVar3;
      FUN_00087edc(0);
      uVar1 = 0xe1;
      uVar3 = 1;
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x5990))))) = uVar1;
    FUN_000890ba(uVar3);
  }
  return;
}



undefined4 FUN_00089386(void)

{
  undefined4 uVar1;
  
  if (((int8_t)DAT_febf1294) != -0x1f) {
    if (((int8_t)DAT_febf1294) == -0x2e) {
      uVar1 = 0;
    }
    else {
      uVar1 = 2;
    }
    return uVar1;
  }
  return 0;
}



short * FUN_000893f2(short param_1)

{
  uint uVar1;
  
  uVar1 = 0;
  do {
    if (*(short *)(((undefined *)camry_host_ptr(0x27da4u)) + uVar1 * 0x20) == param_1) {
      return (short *)(((undefined *)camry_host_ptr(0x27da4u)) + uVar1 * 0x20);
    }
    uVar1 = uVar1 + 1;
  } while (uVar1 < 2);
  return (short *)0x0;
}



void FUN_00089414(void)

{
  DAT_febf1370 = 0;
  DAT_febf1378 = 0xe1;
  DAT_febf1374 = 0xffffffff;
  return;
}



short * FUN_000895f8(short param_1)

{
  uint uVar1;
  
  uVar1 = 0;
  do {
    if (*(short *)(((undefined *)camry_host_ptr(0x27de8u)) + uVar1 * 0x20) == param_1) {
      return (short *)(((undefined *)camry_host_ptr(0x27de8u)) + uVar1 * 0x20);
    }
    uVar1 = uVar1 + 1;
  } while (uVar1 < 2);
  return (short *)0x0;
}



void FUN_0008961a(void)

{
  DAT_febf137c = 0;
  DAT_febf1384 = 0xe1;
  DAT_febf1380 = 0xffffffff;
  return;
}



undefined2 * FUN_000897fc(short param_1)

{
  undefined2 *puVar1;
  
  puVar1 = ((undefined *)camry_host_ptr(0x27e2cu));
  if (DAT_00027e2c != param_1) {
    puVar1 = (undefined2 *)0x0;
  }
  return puVar1;
}



void FUN_0008980c(void)

{
  DAT_febf1388 = 0;
  DAT_febf1390 = 0xe1;
  DAT_febf138c = 0xffffffff;
  return;
}



undefined2 * FUN_000899ea(short param_1)

{
  undefined2 *puVar1;
  
  puVar1 = ((undefined *)camry_host_ptr(0x27e50u));
  if (DAT_00027e50 != param_1) {
    puVar1 = (undefined2 *)0x0;
  }
  return puVar1;
}



void FUN_000899fa(void)

{
  DAT_febf1394 = 0;
  DAT_febf139c = 0xe1;
  DAT_febf1398 = 0xffffffff;
  return;
}



undefined4 FUN_00089b84(undefined4 param_1,undefined4 param_2)

{
  uint32_t puVar1;
  int iVar2;
  byte bStack_9;
  
  puVar1 = 0xfebeb800u;
  bStack_9 = 3;
  iVar2 = FUN_00089e72(&bStack_9);
  if (iVar2 == 0) {
    if (bStack_9 == 1) {
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x5ba0)))) = param_2;
      return 0;
    }
    if (bStack_9 == 2) {
      return 2;
    }
  }
  return 1;
}



undefined4 FUN_00089bb6(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  DAT_febf13a4 = param_2;
  DAT_febf13a8 = param_3;
  return 0;
}



undefined4 FUN_00089c5a(undefined4 param_1,undefined4 param_2)

{
  uint32_t puVar1;
  int iVar2;
  byte bStack_9;
  
  puVar1 = 0xfebeb800u;
  bStack_9 = 3;
  iVar2 = FUN_00089e72(&bStack_9);
  if (iVar2 == 0) {
    if (bStack_9 == 1) {
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x5bb0)))) = param_2;
      return 0;
    }
    if (bStack_9 == 2) {
      return 2;
    }
  }
  return 1;
}



undefined4 FUN_00089c8c(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  DAT_febf13b4 = param_2;
  DAT_febf13b8 = param_3;
  return 0;
}



uint FUN_00089c98(undefined2 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  uint uVar1;
  uint32_t puVar2;
  uint uVar3;
  
  puVar2 = 0xfebeb800u;
  DAT_febf13be = 0;
  DAT_febf13bf = 1;
  uVar3 = FUN_00089646(param_1,DAT_febf13b0,DAT_febf13b4,DAT_febf13b8,param_2,param_3,param_4);
  if (uVar3 == 0) {
    uVar1 = 0;
    do {
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x5bbe))))) == '\x01') {
        uVar3 = (uint)((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x5bbf))))) != '\0');
        break;
      }
      uVar1 = uVar1 + 1;
    } while (uVar1 < 0xe07);
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x5bbe))))) == '\0') {
      uVar3 = 2;
    }
  }
  else if (uVar3 != 2) {
    uVar3 = 1;
  }
  return uVar3;
}



undefined4 FUN_00089d08(undefined2 *param_1)

{
  if (param_1 != (undefined2 *)0x0) {
    *param_1 = 0;
    return 0;
  }
  return 1;
}



void FUN_00089e2c(char param_1,int *param_2)

{
  if (param_1 == '\0') {
    *param_2 = *param_2 + 1;
    return;
  }
  if (param_1 == -0x1f) {
    param_2[1] = param_2[1] + 1;
    return;
  }
  if ((((param_1 != -0x5b) && (param_1 != -0x4c)) && (param_1 != -0x3d)) && (param_1 != -0x2e)) {
    param_2[3] = param_2[3] + 1;
    return;
  }
  param_2[2] = param_2[2] + 1;
  return;
}



/* Forward byte-counted copy; returns the original destination. Uses word transfers only when both
   pointers are four-byte aligned, otherwise byte transfers. Not an overlap-safe memmove contract.
   Exact CodeFlash execution covers zero length, alignment combinations, bulk/tail boundaries,
   source preservation and destination canaries. Forward byte-counted copy: r6 destination, r7
   source, r8 byte count; returns original destination in r10. Word path requires both pointers
   four-byte aligned; otherwise byte path. Exact firmware execution covers aligned bulk/tail and
   unaligned copies, unchanged source, destination canaries and stack restoration. */

void * f33_memcpy_forward(void *destination,void *source,uint byte_count)

{
  undefined1 uVar1;
  undefined4 *puVar2;
  undefined4 uVar3;
  undefined4 *puVar4;
  
  puVar4 = destination;
  if ((((uint)camry_host_addr(destination) & 3) == 0) && (((uint)camry_host_addr(source) & 3) == 0)) {
    for (; 0x1f < byte_count; byte_count = byte_count - 0x20) {
      *puVar4 = *(undefined4 *)source;
      puVar4[1] = (*((undefined4 *)camry_host_ptr((uint32_t)((int)camry_host_addr(source) + 4))));
      puVar4[2] = (*((undefined4 *)camry_host_ptr((uint32_t)((int)camry_host_addr(source) + 8))));
      puVar4[3] = (*((undefined4 *)camry_host_ptr((uint32_t)((int)camry_host_addr(source) + 0xc))));
      puVar4[4] = (*((undefined4 *)camry_host_ptr((uint32_t)((int)camry_host_addr(source) + 0x10))));
      puVar4[5] = (*((undefined4 *)camry_host_ptr((uint32_t)((int)camry_host_addr(source) + 0x14))));
      puVar4[6] = (*((undefined4 *)camry_host_ptr((uint32_t)((int)camry_host_addr(source) + 0x18))));
      puVar2 = ((undefined4 *)camry_host_ptr((uint32_t)((int)camry_host_addr(source) + 0x1c)));
      source = ((void *)camry_host_ptr((uint32_t)((int)camry_host_addr(source) + 0x20)));
      puVar4[7] = *puVar2;
      puVar4 = puVar4 + 8;
    }
    if (0xf < byte_count) {
      *puVar4 = *(undefined4 *)source;
      puVar4[1] = (*((undefined4 *)camry_host_ptr((uint32_t)((int)camry_host_addr(source) + 4))));
      puVar4[2] = (*((undefined4 *)camry_host_ptr((uint32_t)((int)camry_host_addr(source) + 8))));
      puVar2 = ((undefined4 *)camry_host_ptr((uint32_t)((int)camry_host_addr(source) + 0xc)));
      source = ((void *)camry_host_ptr((uint32_t)((int)camry_host_addr(source) + 0x10)));
      puVar4[3] = *puVar2;
      puVar4 = puVar4 + 4;
      byte_count = byte_count - 0x10;
    }
    for (; 3 < byte_count; byte_count = byte_count - 4) {
      uVar3 = *(undefined4 *)source;
      source = ((void *)camry_host_ptr((uint32_t)((int)camry_host_addr(source) + 4)));
      *puVar4 = uVar3;
      puVar4 = puVar4 + 1;
    }
  }
  for (; byte_count != 0; byte_count = byte_count - 1) {
    uVar1 = *(undefined1 *)source;
    source = ((void *)camry_host_ptr((uint32_t)((int)camry_host_addr(source) + 1)));
    *(undefined1 *)puVar4 = uVar1;
    puVar4 = ((undefined4 *)camry_host_ptr((uint32_t)((int)camry_host_addr(puVar4) + 1)));
  }
  return destination;
}



undefined4 FUN_0008a2e4(uint param_1)

{
  uint uVar1;
  
  DAT_ffc5d0e0 = param_1 & 1;
  DAT_ffc5d0f0 = param_1;
  DAT_ffc5d0f4 = param_1;
  DAT_ffc5d0f8 = param_1;
  DAT_ffc5d0fc = param_1;
  uVar1 = DAT_ffc5d0e0;
  if (((((uVar1 & 1) == (param_1 & 1)) && (uVar1 = DAT_ffc5d0f0, uVar1 == param_1)) &&
      (uVar1 = DAT_ffc5d0f4, uVar1 == param_1)) &&
     ((uVar1 = DAT_ffc5d0f8, uVar1 == param_1 && (uVar1 = DAT_ffc5d0fc, uVar1 == param_1)))) {
    return 1;
  }
  return 2;
}



undefined4 FUN_0008a332(uint param_1)

{
  uint uVar1;
  
  ICUSPARAM = param_1;
  DAT_ffc5d090 = param_1;
  DAT_ffc5d094 = param_1;
  DAT_ffc5d098 = param_1;
  DAT_ffc5d09c = param_1;
  uVar1 = ICUSPARAM;
  if ((((uVar1 == param_1) && (uVar1 = DAT_ffc5d090, uVar1 == param_1)) &&
      (uVar1 = DAT_ffc5d094, uVar1 == param_1)) &&
     ((uVar1 = DAT_ffc5d098, uVar1 == param_1 && (uVar1 = DAT_ffc5d09c, uVar1 == param_1)))) {
    return 1;
  }
  return 2;
}



undefined4 FUN_0008a378(int param_1)

{
  int iVar1;
  
  DAT_ffc5d0a0 = param_1;
  DAT_ffc5d0a4 = param_1;
  DAT_ffc5d0a8 = param_1;
  DAT_ffc5d0ac = param_1;
  DAT_ffc5d0b0 = param_1;
  DAT_ffc5d0b4 = param_1;
  DAT_ffc5d0b8 = param_1;
  DAT_ffc5d0bc = param_1;
  iVar1 = DAT_ffc5d0a0;
  if (((((iVar1 == param_1) && (iVar1 = DAT_ffc5d0a4, iVar1 == param_1)) &&
       (iVar1 = DAT_ffc5d0a8, iVar1 == param_1)) &&
      ((iVar1 = DAT_ffc5d0ac, iVar1 == param_1 && (iVar1 = DAT_ffc5d0b0, iVar1 == param_1)))) &&
     ((iVar1 = DAT_ffc5d0b4, iVar1 == param_1 &&
      ((iVar1 = DAT_ffc5d0b8, iVar1 == param_1 && (iVar1 = DAT_ffc5d0bc, iVar1 == param_1)))))) {
    return 1;
  }
  return 2;
}



void FUN_0008a3e2(void)

{
  uint uVar1;
  int iVar2;
  
  iVar2 = FUN_0008a2e4(0xaaaaaaaa);
  if ((((iVar2 == 1) && (iVar2 = FUN_0008a2e4(0x55555555), iVar2 == 1)) &&
      (iVar2 = FUN_0008a332(0xaaaaaaaa), iVar2 == 1)) &&
     ((iVar2 = FUN_0008a332(0x55555555), iVar2 == 1 &&
      (iVar2 = FUN_0008a378(0xaaaaaaaa), iVar2 == 1)))) {
    FUN_0008a378(0x55555555);
  }
  uVar1 = DAT_ffc5d0e0;
  DAT_ffc5d0e0 = uVar1 & 0xfffffffe;
  DAT_ffc5d0f0 = 0;
  DAT_ffc5d0f4 = 0;
  DAT_ffc5d0f8 = 0;
  DAT_ffc5d0fc = 0;
  return;
}



/* Constant-block fill: 21 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_8a450(void)

{
  DAT_febf131c = 0;
  DAT_febf1320 = 0;
  DAT_febf1324 = 0;
  DAT_febf1328 = 0;
  DAT_febf132c = 0;
  DAT_febf1330 = 0;
  DAT_febf1334 = 0;
  DAT_febf1338 = 0;
  DAT_febf133c = 0;
  DAT_febf1340 = 0;
  DAT_febf1344 = 0;
  DAT_febf1348 = 0;
  DAT_febf134c = 0;
  DAT_febf136d = 0;
  DAT_febf1360 = 0xffffffff;
  DAT_febf1364 = 0xffffffff;
  DAT_febf1368 = 0xffffffff;
  DAT_febf1350 = 0xffffffff;
  DAT_febf1354 = 0xffffffff;
  DAT_febf1358 = 0xffffffff;
  DAT_febf135c = 0xffffffff;
  return;
}



void FUN_0008a4a8(void)

{
  uint uVar1;
  
  uVar1 = DAT_ffc5d0e0;
  DAT_ffc5d0e0 = uVar1 & 0xfffffffe;
  DAT_ffc5d0f0 = 0;
  DAT_ffc5d0f4 = 0;
  DAT_ffc5d0f8 = 0;
  DAT_ffc5d0fc = 0;
  DAT_ffc5d0c0 = 0x600;
  ICUSCTL = 3;
  DAT_ffc5d0e4 = 1;
  return;
}



void FUN_0008a514(uint *param_1)

{
  ICUSDAT = *param_1;
  ICUSDAT = param_1[1];
  ICUSDAT = param_1[2];
  ICUSDAT = param_1[3];
  return;
}



void FUN_0008a58a(uint *param_1)

{
  uint uVar1;
  
  uVar1 = ICUSOUT;
  *param_1 = uVar1;
  uVar1 = ICUSOUT;
  param_1[1] = uVar1;
  uVar1 = ICUSOUT;
  param_1[2] = uVar1;
  uVar1 = ICUSOUT;
  param_1[3] = uVar1;
  return;
}



void FUN_0008aa04(uint *param_1)

{
  uint uVar1;
  
  if (param_1 != (uint *)0x0) {
    uVar1 = FHVE3;
    *param_1 = uVar1;
    uVar1 = FHVE15;
    param_1[1] = uVar1;
  }
  return;
}



void FUN_0008ad16(undefined4 *param_1)

{
  DAT_ffc5d090 = *param_1;
  DAT_ffc5d094 = param_1[1];
  DAT_ffc5d098 = param_1[2];
  DAT_ffc5d09c = param_1[3];
  DAT_ffc5d0a0 = param_1[4];
  DAT_ffc5d0a4 = param_1[5];
  DAT_ffc5d0a8 = param_1[6];
  DAT_ffc5d0ac = param_1[7];
  DAT_ffc5d0b0 = param_1[8];
  DAT_ffc5d0b4 = param_1[9];
  DAT_ffc5d0b8 = param_1[10];
  DAT_ffc5d0bc = param_1[0xb];
  return;
}



uint FUN_0008ad7a(void)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  
  uVar1 = DAT_ffc5d010;
  uVar3 = 0;
  if ((uVar1 & 0xfff) != 0) {
    uVar2 = 0;
    do {
      if (((1 << (uVar2 & 0x1f) & uVar1 & 0xfff) != 0) && (uVar3 = uVar2 + 1 | 0x1000, uVar2 != 9))
      {
        return uVar3;
      }
      uVar2 = uVar2 + 1;
    } while (uVar2 < 0xc);
  }
  return uVar3;
}



undefined4 FUN_0008afea(void)

{
  undefined4 uVar1;
  
  if (DAT_febf136c == '\0') {
    uVar1 = 0;
  }
  else {
    uVar1 = FUN_0008ad7a();
  }
  return uVar1;
}



undefined4 FUN_0008b026(void)

{
  if (((((int8_t)DAT_febf136c) == -0x1f) || (((int8_t)DAT_febf136c) == -0x2e)) || (((int8_t)DAT_febf136c) == -0x3d)) {
    if (DAT_febf136d == '\0') {
      return 1;
    }
  }
  else if (DAT_febf136c == '\0') {
    return 0x1000;
  }
  return 0x2000;
}



void FUN_0008b060(void)

{
  __synchronize();
  return;
}



void FUN_0008b070(void)

{
  uint uVar1;
  
  DAT_febf380a = 0;
  DAT_febf3810 = 0;
  DAT_febf380f = 0;
  DAT_febf380e = 0;
  DAT_febf3806 = 0;
  DAT_febf3804 = 0;
  DAT_febf380d = 0;
  DAT_febf380c = 0;
  DAT_febf3800 = 0;
  DAT_febf3808 = 0;
  DAT_febf3811 = 0;
  uVar1 = 0;
  do {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebf3812u + (uint32_t)(uVar1) * 1u)))) = 0;
    uVar1 = uVar1 + 1;
  } while (uVar1 < 0x300);
  return;
}



void FUN_0008b0de(uchar param_1,uchar param_2)

{
  f33_diagnostic_session_changed_application(param_1,param_2);
  FUN_0006a156(param_1,param_2);
  return;
}



/* Pass bit0 to4D17A and preserve its consequential full R10 result; not void. */

uint f33_check_diagnostic_addressing_admission(uchar addressing_flags)

{
  uint uVar1;
  
  uVar1 = f33_check_diagnostic_application_admission(addressing_flags & 1);
  return uVar1;
}



/* Constant source: return 0; shape-classified from the canonical corpus. Callers receive this
   literal directly; its meaning is not recovered. */

undefined4 f33_return_const_0_8b10c(void)

{
  return 0;
}



/* Constant source: return 0; shape-classified from the canonical corpus. Callers receive this
   literal directly; its meaning is not recovered. */

undefined4 f33_return_const_0_8b110(void)

{
  return 0;
}



void FUN_0008b134(void)

{
  f33_app_programming_local_word = 0;
  DAT_febf3b1c = 1;
  DAT_febf3b1b = 1;
  DAT_febf3b1a = 0;
  f33_app_programming_pending_latch = '\0';
  f33_app_programming_admission_latched = '\0';
  DAT_febf3b1d = 0xff;
  return;
}



void FUN_0008b36e(uchar param_1,uchar *param_2)

{
  uint uVar1;
  uchar uStack_d;
  
  f33_dcm_get_session(&uStack_d);
  uVar1 = f33_app_session_transition_precondition(uStack_d,param_1);
  f33_diagnostic_status_to_nrc((uchar)uVar1,param_2);
  return;
}



/* Clearsindex3B1E/completion3B20/lifecycle3B21/actionstatus3B25; sidestatus1,opaqueFF. */

void f33_reset_write_did_transaction(void)

{
  DAT_febf3b25 = 0;
  DAT_febf3b20 = 0;
  DAT_febf3b1e = 0;
  DAT_febf3b23 = 1;
  DAT_febf3b22 = 1;
  DAT_febf3b21 = 0;
  DAT_febf3b24 = 0xff;
  return;
}



void FUN_0008b3d4(void)

{
  DAT_febf3b27 = 1;
  DAT_febf3b28 = 1;
  DAT_febf3b26 = 0;
  DAT_febf3b29 = 0xff;
  return;
}



void FUN_0008b3e8(void)

{
  f33_reset_write_did_transaction();
  return;
}



/* Transparent call4D36E; r10 result consumed951DA/9521E despite former void. */

uint f33_dcm_probe_did_metadata(ushort did)

{
  uint uVar1;
  
  uVar1 = f33_select_available_did_metadata(did);
  return uVar1;
}



/* Transparent call4D492; pointerr6 must be preserved in ABI. */

void f33_dcm_selected_did_payload_length(ushort *length)

{
  f33_get_selected_did_payload_length(length);
  return;
}



uint FUN_0008b41a(char param_1,uchar *param_2,int *param_3)

{
  uint uVar1;
  
  if (*param_2 == '\0') {
    if ((param_1 == '\0') && (uVar1 = 0, *(int *)(param_2 + 4) != 0)) {
      for (; uVar1 < *(ushort *)(param_2 + 2); uVar1 = uVar1 + 1 & 0xffff) {
        (*((undefined1 *)camry_host_ptr((uint32_t)(*param_3 + uVar1)))) = (*((undefined1 *)camry_host_ptr((uint32_t)(*(int *)(param_2 + 4) + uVar1))));
      }
    }
    uVar1 = 0;
  }
  else {
    uVar1 = f33_diagnostic_status_to_nrc(*param_2,(uchar *)param_3[3]);
  }
  return uVar1;
}



/* 8B742 prephase;746/754/758 r10 dataflow.2->adapter10 andcompletionFF,else8E6EC translatesNRC.
   Native class compositions verify record103 staging without live replacement, accepted2010 alias2
   with immediate success, and80A5 receive-status rejection independent of80A4 generation. Other
   inputs and asynchronous persistence remain static/bounded. */

uint f33_write_did_request_adapter(ushort did,uchar *payload,ushort length,uchar *nrc)

{
  uint uVar1;
  ushort uStack_16;
  
  uStack_16 = DAT_febf3b1e;
  uVar1 = f33_write_did_precondition_phase(&uStack_16,did);
  if (uVar1 == 0) {
    uVar1 = f33_write_did_payload_phase(uStack_16,payload,length);
  }
  if (uVar1 == 2) {
    uVar1 = 10;
    DAT_febf3b20 = 0xff;
  }
  else {
    uVar1 = f33_diagnostic_status_to_nrc((uchar)uVar1,nrc);
  }
  DAT_febf3b1e = uStack_16;
  return uVar1;
}



uint FUN_0008b77a(uchar *param_1)

{
  uint uVar1;
  
  if (DAT_febf3b20 == 0xff) {
    uVar1 = 10;
  }
  else {
    uVar1 = f33_diagnostic_status_to_nrc(DAT_febf3b20,param_1);
  }
  return uVar1;
}



void FUN_0008b79a(undefined1 param_1)

{
  DAT_febf3b20 = param_1;
  return;
}



undefined1 FUN_0008b7a4(void)

{
  return DAT_febf3b25;
}



void FUN_0008b7ae(undefined1 param_1)

{
  DAT_febf3b25 = param_1;
  return;
}



/* Resets3B2C..35
   andbuffers3B36[32],3B56[49],3B87[68];noapplicationservicecancelorresultpublication.
   Configuredwrapperoperation/status>=2\u21928B83C\u2192thisreset,distinctfromcontrol-type2stop.
   Configuredwrapperoperation/status>=2→8B83C→thisreset,distinctfromcontrol-type2stop. */

void f33_diag_reset_routine_class_state(void)

{
  uint uVar1;
  
  DAT_febf3b2c = 0;
  DAT_febf3b32 = 1;
  DAT_febf3b31 = 1;
  DAT_febf3b35 = 2;
  DAT_febf3b34 = 2;
  DAT_febf3b33 = 0xff;
  DAT_febf3b30 = 0;
  DAT_febf3b2e = 0;
  uVar1 = 0;
  do {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebf3b36u + (uint32_t)(uVar1) * 1u)))) = 0;
    uVar1 = uVar1 + 1;
  } while (uVar1 < 0x20);
  uVar1 = 0;
  do {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebf3b56u + (uint32_t)(uVar1) * 1u)))) = 0;
    uVar1 = uVar1 + 1;
  } while (uVar1 < 0x31);
  uVar1 = 0;
  do {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebf3b87u + (uint32_t)(uVar1) * 1u)))) = 0;
    uVar1 = uVar1 + 1;
  } while (uVar1 < 0x44);
  return;
}



void FUN_0008b83c(void)

{
  f33_diag_reset_routine_class_state();
  return;
}



void FUN_0008b848(void)

{
  f33_diag_reset_routine_class_state();
  return;
}



/* Constant source: return 0; shape-classified from the canonical corpus. Callers receive this
   literal directly; its meaning is not recovered. */

undefined4 f33_return_const_0_8b854(void)

{
  return 0;
}



/* 8B85Ccalls8B854whichmov0,R10;jmpLP. */

uint f33_diag_routine_crypto_admit(void)

{
  uint uVar1;
  
  uVar1 = f33_return_const_0_8b854();
  return uVar1;
}



/* 6A028activatesonly5096==0;callbackreturns0,nooutput/lengthaccess. */

uint f33_diag_routine_100e_activate_fixed_crypto_bank0(void)

{
  f33_crypto_bank_activate_collected_update();
  return 0;
}



/* 6A0AEactivatesonly509B==0;callbackreturns0;fixed16bytecommand5boundarymaintained. */

uint f33_diag_routine_100f_activate_fixed_crypto_bank1(void)

{
  f33_crypto_bank_activate_test_operation();
  return 0;
}



void FUN_0008b930(int param_1,int param_2,uint param_3)

{
  uint uVar1;
  
  for (uVar1 = 0; uVar1 < (param_3 & 0xffff); uVar1 = uVar1 + 1 & 0xffff) {
    (*((undefined1 *)camry_host_ptr((uint32_t)(uVar1 + param_1)))) = (*((undefined1 *)camry_host_ptr((uint32_t)(uVar1 + param_2))));
    (*((undefined1 *)camry_host_ptr((uint32_t)(uVar1 + param_2)))) = 0;
  }
  return;
}



/* Constant source: return 2; shape-classified from the canonical corpus. Callers receive this
   literal directly; its meaning is not recovered. */

undefined4 f33_return_const_2_8bd72(void)

{
  return 2;
}



undefined1 FUN_0008bd76(undefined1 param_1)

{
  return param_1;
}



/* 8BC86\u21928BD7C;2-byteinputfromu32high/low;constantlength7;selectedindex3B2C;pending2mapsreturn10;8E6ECmapsotherreturns.
   Fifthargumentunused.
   8BC86→8BD7C;2-byteinputfromu32high/low;constantlength7;selectedindex3B2C;pending2mapsreturn10;8E6ECmapsotherreturns.
    */

uint f33_diag_routine_application_class
               (uchar control_type,ushort configured_index,uint encoded_input,uchar *output,
               ushort *unused_length,uchar *nrc)

{
  uint uVar1;
  ushort uStack_16;
  uchar uStack_14;
  undefined1 uStack_13;
  ushort uStack_12;
  
  uStack_16 = DAT_febf3b2c;
  if (configured_index < 0x14) {
    uStack_14 = (uchar)(encoded_input >> 8);
    uStack_13 = (undefined1)encoded_input;
    uStack_12 = 0;
    uVar1 = f33_diag_routine_begin_admission
                      ((*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x26918u + (uint32_t)((uint)configured_index * 4) * 2u)))),control_type,&uStack_16,
                       &uStack_14,7);
    if (uVar1 == 0) {
      uVar1 = f33_diag_routine_run_action_phase
                        (control_type,uStack_16,&uStack_14,7,output,&uStack_12);
    }
    if (uVar1 == 2) {
      DAT_febf3b2c = uStack_16;
      return 10;
    }
  }
  else {
    uVar1 = 5;
  }
  uVar1 = f33_diagnostic_status_to_nrc((uchar)uVar1,nrc);
  DAT_febf3b2c = uStack_16;
  return uVar1;
}



/* Constant-block fill: 5 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_8bfea(void)

{
  DAT_febf3bd2 = 1;
  DAT_febf3bd1 = 1;
  DAT_febf3bd0 = 0;
  DAT_febf3bcc = 0;
  DAT_febf3bd3 = 0xff;
  return;
}


