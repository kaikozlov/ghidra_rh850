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



undefined4 FUN_0008813c(void)

{
  uint32_t puVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  
  puVar1 = 0xfebeb800u;
  uVar4 = 1;
  if (((int8_t)DAT_febf1190) == -0x3d) {
    DAT_febf1194 = camry_host_addr(FUN_000880e0);
    DAT_febf1198 = 0xfff77f1f;
    DAT_febf1190 = -0x4c;
    iVar2 = FUN_0008aa6a(((undefined *)camry_host_ptr(0xfebf10f4u)));
    if (iVar2 == 0) {
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x5978)))) = 0;
      uVar4 = 0;
    }
    else {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x5990))))) = 0xc3;
      uVar3 = FUN_0008afea();
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x5984)))) = uVar3;
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x5994)))) = 0;
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x5998)))) = 0xffffffff;
    }
  }
  return uVar4;
}



int FUN_00088198(uint param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4,
                undefined4 param_5,undefined4 param_6)

{
  char cVar1;
  uint32_t puVar2;
  int iVar3;
  
  puVar2 = 0xfebeb800u;
  if (DAT_febf1190 == '\0') {
    return 1;
  }
  iVar3 = FUN_00088362();
  if (iVar3 != 1) {
    return 2;
  }
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x5990)))));
  if (((int8_t)cVar1) == -0x1f) {
    iVar3 = FUN_00087f52(((void *)camry_host_ptr((uint32_t)(param_2))), param_3, param_4, param_5, ((uint *)camry_host_ptr((uint32_t)(param_6))));
    if (iVar3 != 0) goto LAB_0008827e;
    (*((uint *)camry_host_ptr((uint32_t)(puVar2 + 0x58e8)))) = param_1;
    (*((uint *)camry_host_ptr((uint32_t)(puVar2 + 0x58ec)))) = ~param_1;
    *(code **)(puVar2 + 0x597c) = FUN_0008813c;
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0x5988)))) = 0xfff77ec3;
    *(code **)(puVar2 + 0x5980) = FUN_00088086;
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0x598c)))) = 0xfff77f79;
    thunk_FUN_0007995c();
    cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x5990)))));
    if (((int8_t)cVar1) == -0x3d) {
LAB_00088256:
      iVar3 = FUN_0008813c();
      if (iVar3 == 0) goto LAB_0008827e;
      goto LAB_00088260;
    }
    if ((((int8_t)cVar1) == -0x2e) || (((int8_t)cVar1) == -0x4c)) goto LAB_0008827e;
  }
  else {
    if (((int8_t)cVar1) == -0x3d) {
      iVar3 = FUN_00087f52(((void *)camry_host_ptr((uint32_t)(param_2))), param_3, param_4, param_5, ((uint *)camry_host_ptr((uint32_t)(param_6))));
      if (iVar3 == 0) {
        (*((uint *)camry_host_ptr((uint32_t)(puVar2 + 0x58e8)))) = param_1;
        (*((uint *)camry_host_ptr((uint32_t)(puVar2 + 0x58ec)))) = ~param_1;
        *(code **)(puVar2 + 0x5980) = FUN_00088086;
        (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0x598c)))) = 0xfff77f79;
        goto LAB_00088256;
      }
LAB_00088260:
      FUN_00087edc(0);
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x5990))))) = 0xe1;
      goto LAB_0008827e;
    }
    if ((((int8_t)cVar1) == -0x2e) || (((int8_t)cVar1) == -0x4c)) {
      iVar3 = 2;
      goto LAB_0008827e;
    }
  }
  iVar3 = 1;
LAB_0008827e:
  FUN_00088436();
  return iVar3;
}



void FUN_00088290(void)

{
  uint uVar1;
  uint uVar2;
  char cVar3;
  uint32_t puVar4;
  int iVar5;
  
  puVar4 = 0xfebeb800u;
  if (((int8_t)DAT_febf10f0) == -0x1f) {
    puVar4 = 0xfebeb800u;
    FUN_00087fd8(DAT_febf10f1);
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x58f0))))) = 0xd2;
  }
  cVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x5990)))));
  if (((int8_t)cVar3) == -0x2e) {
    uVar1 = (*((uint *)camry_host_ptr((uint32_t)(puVar4 + 0x5970)))) + 1;
    (*((uint *)camry_host_ptr((uint32_t)(puVar4 + 0x5970)))) = uVar1;
    if (uVar1 < 7) {
      return;
    }
    thunk_FUN_000799da();
  }
  else {
    if (((int8_t)cVar3) != -0x3d) {
      if (((int8_t)cVar3) != -0x4c) {
        return;
      }
      uVar1 = (*((uint *)camry_host_ptr((uint32_t)(puVar4 + 0x5978)))) + 1;
      (*((uint *)camry_host_ptr((uint32_t)(puVar4 + 0x5978)))) = uVar1;
      uVar2 = (*((uint *)camry_host_ptr((uint32_t)(puVar4 + 0x5974)))) + 1;
      (*((uint *)camry_host_ptr((uint32_t)(puVar4 + 0x5974)))) = uVar2;
      if ((uVar1 < 0xc) && (uVar2 < 0xc)) {
        return;
      }
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar4 + 0x5998)))) = 0xffffffff;
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar4 + 0x5994)))) = 0;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x5990))))) = 0xa5;
      iVar5 = FUN_00088574();
      FUN_00087edc(iVar5 != 1);
      goto LAB_00088340;
    }
    uVar1 = (*((uint *)camry_host_ptr((uint32_t)(puVar4 + 0x5974)))) + 1;
    (*((uint *)camry_host_ptr((uint32_t)(puVar4 + 0x5974)))) = uVar1;
    if (uVar1 < 0xc) {
      return;
    }
    FUN_00087edc(0);
  }
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar4 + 0x5998)))) = 0xffffffff;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar4 + 0x5994)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x5990))))) = 0xa5;
LAB_00088340:
  FUN_00088086(1);
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



bool FUN_00088362(void)

{
  char cVar1;
  uint32_t puVar2;
  puVar2 = 0xfebeb800u;
  thunk_FUN_0006a45e();
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x596c)))));
  if (((int8_t)cVar1) == -0x2e) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x596c))))) = 0xe1;
  }
  thunk_FUN_0006a4c4();
  return cVar1 == -0x2e;
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



void FUN_000883a2(undefined1 param_1)

{
  if (((int8_t)DAT_febf1190) == -0x2e) {
    thunk_FUN_000799da();
  }
  else if ((((int8_t)DAT_febf1190) == -0x3d) || (((int8_t)DAT_febf1190) == -0x4c)) {
    FUN_00087edc(param_1);
  }
  return;
}



int FUN_000883cc(undefined4 param_1)

{
  int iVar1;
  int iVar2;
  
  iVar1 = FUN_0008ae2e(((undefined4 *)camry_host_ptr((uint32_t)(param_1))));
  iVar2 = 0x9c4;
  do {
    if (iVar1 != 0) {
      return iVar1;
    }
    iVar1 = FUN_0008af10();
    iVar2 = iVar2 + -1;
  } while (iVar2 != 0);
  return iVar1;
}



bool FUN_000883e8(void)

{
  int iVar1;
  bool bVar2;
  int local_18;
  uint32_t puStack_14;
  undefined1 *puStack_10;
  undefined4 uStack_c;
  
  puStack_10 = (undefined1 *)&local_18;
  uStack_c = 0;
  puStack_14 = 0x27d6cu;
  local_18 = 0;
  bVar2 = true;
  local_18 = FUN_000883cc(camry_host_addr(&puStack_10));
  if (local_18 == 1) {
    puStack_10 = (undefined1 *)&local_18;
    iVar1 = FUN_000883cc(camry_host_addr(&puStack_10));
    if (iVar1 == 1) {
      local_18 = 2;
      puStack_10 = (undefined1 *)&local_18;
      iVar1 = FUN_000883cc(camry_host_addr(&puStack_10));
      bVar2 = iVar1 != 1;
    }
  }
  return bVar2;
}



void FUN_00088436(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  thunk_FUN_0006a45e();
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x596c))))) = 0xd2;
  thunk_FUN_0006a4c4();
  return;
}



undefined4 FUN_0008844e(void)

{
  uint32_t puVar1;
  int iVar2;
  undefined4 uVar3;
  
  puVar1 = 0xfebeb800u;
  FUN_0008a22c(0);
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x5998)))) = 0xffffffff;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x5988)))) = 0xffffffff;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x598c)))) = 0xffffffff;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x5994)))) = 0;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x597c)))) = 0;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x5980)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x5991))))) = 0;
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x5990))))) == '\x0f') {
    uVar3 = 1;
  }
  else {
    FUN_00088362();
    f33_run_init_chain_8838a();
    iVar2 = FUN_0008a4ce();
    if (iVar2 == 1) {
      FUN_000883a2(0);
      iVar2 = FUN_000883e8();
      if (iVar2 == 0) {
        (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x5978)))) = 0;
        (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x5974)))) = 0;
        (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x5970)))) = 0;
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x5990))))) = 0xe1;
        FUN_0008a22c(1);
        uVar3 = 0;
      }
      else {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x5990))))) = 0xf;
        uVar3 = 1;
      }
    }
    else {
      uVar3 = 1;
      if (iVar2 == 2) {
        FUN_000883a2(1);
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x5990))))) = 0xf;
      }
      else {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x5990))))) = 0;
      }
    }
    FUN_00088436();
  }
  return uVar3;
}



undefined4 FUN_000884ea(void)

{
  uint32_t puVar1;
  int iVar2;
  undefined4 uVar3;
  
  puVar1 = 0xfebeb800u;
  FUN_0008a22c(0);
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x5998)))) = 0xffffffff;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x5988)))) = 0xffffffff;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x598c)))) = 0xffffffff;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x5994)))) = 0;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x597c)))) = 0;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x5980)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x5991))))) = 0;
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x5990))))) == '\x0f') {
    uVar3 = 1;
  }
  else {
    FUN_00088362();
    f33_run_init_chain_8838a();
    iVar2 = FUN_0008a4ce();
    if (iVar2 == 1) {
      FUN_000883a2(0);
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x5970)))) = 0;
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x5974)))) = 0;
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x5978)))) = 0;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x5990))))) = 0xe1;
      FUN_0008a22c(1);
      uVar3 = 0;
    }
    else {
      uVar3 = 1;
      if (iVar2 == 2) {
        FUN_000883a2(1);
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x5990))))) = 0xf;
      }
      else {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x5990))))) = 0;
      }
    }
    FUN_00088436();
  }
  return uVar3;
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



void FUN_000885b2(char param_1)

{
  code *pcVar1;
  uint uVar2;
  uint32_t puVar3;
  int iVar4;
  uint uVar5;
  
  uVar2 = DAT_febf118c;
  pcVar1 = ((void *)camry_host_ptr((uint32_t)(DAT_febf1180)));
  puVar3 = 0xfebeb800u;
  if (((int8_t)DAT_febf1190) == -0x1f) {
    if (param_1 == '\0') {
      DAT_febf1174 = 0;
      DAT_febf1190 = 0xc3;
      return;
    }
    if (param_1 != '\x01') {
      return;
    }
    DAT_febf1170 = 0;
    DAT_febf1190 = 0xd2;
    return;
  }
  uVar5 = ~(uint)DAT_febf1180;
  if (((int8_t)DAT_febf1190) != -0x2e) {
    return;
  }
  if (param_1 == '\0') {
    DAT_febf1174 = 0;
    DAT_febf1190 = -0x3d;
    if (DAT_febf117c == 0x0u) {
      DAT_febf1174 = 0;
      DAT_febf1190 = 0xc3;
      return;
    }
    if (~(uint)DAT_febf117c == DAT_febf1188) {
      puVar3 = 0xfebeb800u;
      iVar4 = (*(int (*)())DAT_febf117c)();
      if (iVar4 == 0) {
        return;
      }
      if ((uintptr_t)(pcVar1)==(uintptr_t)(f33_reset_vector)) {
        return;
      }
      if (uVar5 == uVar2) goto LAB_0008863e;
    }
  }
  else {
    if (param_1 == '\x01') {
      return;
    }
    if (DAT_febf1180 == 0x0u) {
      return;
    }
    if (uVar5 == DAT_febf118c) {
      iVar4 = 1;
      DAT_febf1190 = -0x1f;
LAB_0008863e:
      (*(int (*)())pcVar1)(iVar4);
      return;
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x5991))))) = 1;
  return;
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



undefined4 FUN_000886e0(void)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = FUN_0008b026();
  if (iVar1 == 1) {
    uVar2 = FUN_0008864e();
  }
  else if (iVar1 == 0x1000) {
    uVar2 = 1;
  }
  else {
    uVar2 = 2;
  }
  return uVar2;
}



void FUN_00088700(void)

{
  if (DAT_febf1194 != 0x0u) {
    if (~(uint)DAT_febf1194 == DAT_febf1198) {
      (*(int (*)())DAT_febf1194)();
    }
    else {
      DAT_febf1191 = 1;
    }
  }
  return;
}



void FUN_00088726(void)

{
  if (DAT_febf1194 != 0x0u) {
    if (~(uint)DAT_febf1194 == DAT_febf1198) {
      (*(int (*)())DAT_febf1194)();
    }
    else {
      DAT_febf1191 = 1;
    }
  }
  return;
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



undefined4 FUN_0008877e(int *param_1,void *param_2,int param_3,uint param_4,uint *param_5)

{
  byte bVar1;
  uint32_t puVar2;
  undefined4 uVar3;
  
  puVar2 = 0xfebeb800u;
  if (((((uintptr_t)(param_1)==(uintptr_t)((int *)0x0)) || ((uintptr_t)(param_2)==(uintptr_t)((void *)0x0))) || (param_4 == 0)) ||
     ((((uintptr_t)(param_5)==(uintptr_t)((uint *)0x0)|| (*param_1 != 1)) || (param_3 != 0x10)))) {
    uVar3 = 1;
  }
  else if (*param_5 < 0x10) {
    uVar3 = 3;
  }
  else {
    uVar3 = 0;
    DAT_febf11d4 = camry_host_addr(param_5);
    DAT_febf119c = ~param_4;
    DAT_febf11a0 = ~(uint)camry_host_addr(param_5);
    DAT_febf11c0 = param_4;
    f33_memcpy_forward(((undefined *)camry_host_ptr(0xfebf11b0u)),param_2,0x10);
    *(undefined **)(puVar2 + 0x59dc) = ((void *)camry_host_ptr((uint32_t)(puVar2 + 0x59f0)));
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0x59e4)))) = 1;
    bVar1 = *(byte *)(param_1 + 1);
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0x59ec)))) = 0;
    *(undefined **)(puVar2 + 0x59e0) = ((undefined *)camry_host_ptr(0xfebf11b0u));
    (*((uint *)camry_host_ptr((uint32_t)(puVar2 + 0x59e8)))) = (uint)bVar1;
    *(undefined **)(puVar2 + 23000) = ((void *)camry_host_ptr((uint32_t)(puVar2 + 0x59e0)));
    *(undefined **)(puVar2 + 0x59f0) = ((undefined *)camry_host_ptr(0xfebf11c4u));
  }
  return uVar3;
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



undefined4 FUN_0008892c(void)

{
  uint32_t puVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  
  puVar1 = 0xfebeb800u;
  uVar4 = 1;
  if (((int8_t)DAT_febf1190) == -0x3d) {
    DAT_febf1194 = camry_host_addr(FUN_000888d0);
    DAT_febf1198 = 0xfff7772f;
    DAT_febf1190 = -0x4c;
    iVar2 = FUN_0008a63c(((undefined *)camry_host_ptr(0xfebf11d8u)));
    if (iVar2 == 0) {
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x5978)))) = 0;
      uVar4 = 0;
    }
    else {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x5990))))) = 0xc3;
      uVar3 = FUN_0008afea();
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x5984)))) = uVar3;
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x5994)))) = 0;
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x5998)))) = 0xffffffff;
    }
  }
  return uVar4;
}



int FUN_00088988(uint param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4,
                undefined4 param_5,undefined4 param_6)

{
  char cVar1;
  uint32_t puVar2;
  int iVar3;
  
  puVar2 = 0xfebeb800u;
  if (DAT_febf1190 == '\0') {
    return 1;
  }
  iVar3 = FUN_00088362();
  if (iVar3 != 1) {
    return 2;
  }
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x5990)))));
  if (((int8_t)cVar1) == -0x1f) {
    iVar3 = FUN_0008877e(((int *)camry_host_ptr((uint32_t)(param_2))), ((void *)camry_host_ptr((uint32_t)(param_3))), param_4, param_5, ((uint *)camry_host_ptr((uint32_t)(param_6))));
    if (iVar3 != 0) goto LAB_00088a6e;
    (*((uint *)camry_host_ptr((uint32_t)(puVar2 + 0x59a4)))) = param_1;
    (*((uint *)camry_host_ptr((uint32_t)(puVar2 + 0x59a8)))) = ~param_1;
    *(code **)(puVar2 + 0x597c) = FUN_0008892c;
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0x5988)))) = 0xfff776d3;
    *(code **)(puVar2 + 0x5980) = FUN_00088876;
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0x598c)))) = 0xfff77789;
    thunk_FUN_0007995c();
    cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x5990)))));
    if (((int8_t)cVar1) == -0x3d) {
LAB_00088a46:
      iVar3 = FUN_0008892c();
      if (iVar3 == 0) goto LAB_00088a6e;
      goto LAB_00088a50;
    }
    if ((((int8_t)cVar1) == -0x2e) || (((int8_t)cVar1) == -0x4c)) goto LAB_00088a6e;
  }
  else {
    if (((int8_t)cVar1) == -0x3d) {
      iVar3 = FUN_0008877e(((int *)camry_host_ptr((uint32_t)(param_2))), ((void *)camry_host_ptr((uint32_t)(param_3))), param_4, param_5, ((uint *)camry_host_ptr((uint32_t)(param_6))));
      if (iVar3 == 0) {
        (*((uint *)camry_host_ptr((uint32_t)(puVar2 + 0x59a4)))) = param_1;
        (*((uint *)camry_host_ptr((uint32_t)(puVar2 + 0x59a8)))) = ~param_1;
        *(code **)(puVar2 + 0x5980) = FUN_00088876;
        (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0x598c)))) = 0xfff77789;
        goto LAB_00088a46;
      }
LAB_00088a50:
      FUN_00087edc(0);
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x5990))))) = 0xe1;
      goto LAB_00088a6e;
    }
    if ((((int8_t)cVar1) == -0x2e) || (((int8_t)cVar1) == -0x4c)) {
      iVar3 = 2;
      goto LAB_00088a6e;
    }
  }
  iVar3 = 1;
LAB_00088a6e:
  FUN_00088436();
  return iVar3;
}



void FUN_00088a80(void)

{
  uint uVar1;
  uint uVar2;
  char cVar3;
  uint32_t puVar4;
  int iVar5;
  
  puVar4 = 0xfebeb800u;
  if (((int8_t)DAT_febf11ac) == -0x1f) {
    puVar4 = 0xfebeb800u;
    FUN_00088802(DAT_febf11ad);
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x59ac))))) = 0xd2;
  }
  cVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x5990)))));
  if (((int8_t)cVar3) == -0x2e) {
    uVar1 = (*((uint *)camry_host_ptr((uint32_t)(puVar4 + 0x5970)))) + 1;
    (*((uint *)camry_host_ptr((uint32_t)(puVar4 + 0x5970)))) = uVar1;
    if (uVar1 < 7) {
      return;
    }
    thunk_FUN_000799da();
  }
  else {
    if (((int8_t)cVar3) != -0x3d) {
      if (((int8_t)cVar3) != -0x4c) {
        return;
      }
      uVar1 = (*((uint *)camry_host_ptr((uint32_t)(puVar4 + 0x5978)))) + 1;
      (*((uint *)camry_host_ptr((uint32_t)(puVar4 + 0x5978)))) = uVar1;
      uVar2 = (*((uint *)camry_host_ptr((uint32_t)(puVar4 + 0x5974)))) + 1;
      (*((uint *)camry_host_ptr((uint32_t)(puVar4 + 0x5974)))) = uVar2;
      if ((uVar1 < 0xc) && (uVar2 < 0xc)) {
        return;
      }
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar4 + 0x5998)))) = 0xffffffff;
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar4 + 0x5994)))) = 0;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x5990))))) = 0xa5;
      iVar5 = FUN_00088574();
      FUN_00087edc(iVar5 != 1);
      goto LAB_00088b30;
    }
    uVar1 = (*((uint *)camry_host_ptr((uint32_t)(puVar4 + 0x5974)))) + 1;
    (*((uint *)camry_host_ptr((uint32_t)(puVar4 + 0x5974)))) = uVar1;
    if (uVar1 < 0xc) {
      return;
    }
    FUN_00087edc(0);
  }
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar4 + 0x5998)))) = 0xffffffff;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar4 + 0x5994)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x5990))))) = 0xa5;
LAB_00088b30:
  FUN_00088876(1);
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



undefined4 FUN_00088d60(void)

{
  uint32_t puVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  
  puVar1 = 0xfebeb800u;
  uVar4 = 1;
  if (((int8_t)DAT_febf1190) == -0x3d) {
    DAT_febf1194 = camry_host_addr(FUN_00088d04);
    DAT_febf1198 = 0xfff772fb;
    DAT_febf1190 = -0x4c;
    iVar2 = FUN_0008a720(((undefined *)camry_host_ptr(0xfebf1208u)));
    if (iVar2 == 0) {
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x5978)))) = 0;
      uVar4 = 0;
    }
    else {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x5990))))) = 0xc3;
      uVar3 = FUN_0008afea();
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x5984)))) = uVar3;
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x5994)))) = 0;
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x5998)))) = 0xffffffff;
    }
  }
  return uVar4;
}



int FUN_00088dbc(uint param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4,
                undefined4 param_5,undefined4 param_6,undefined1 param_7)

{
  char cVar1;
  uint32_t puVar2;
  int iVar3;
  
  puVar2 = 0xfebeb800u;
  if (DAT_febf1190 == '\0') {
    return 1;
  }
  iVar3 = FUN_00088362();
  if (iVar3 != 1) {
    return 2;
  }
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x5990)))));
  if (((int8_t)cVar1) == -0x1f) {
    iVar3 = FUN_00088b84(((int *)camry_host_ptr((uint32_t)(param_2))), ((void *)camry_host_ptr((uint32_t)(param_3))), param_4, param_5, ((uint *)camry_host_ptr((uint32_t)(param_6))), param_7);
    if (iVar3 != 0) goto LAB_00088eae;
    (*((uint *)camry_host_ptr((uint32_t)(puVar2 + 0x59fc)))) = param_1;
    (*((uint *)camry_host_ptr((uint32_t)(puVar2 + 0x5a00)))) = ~param_1;
    *(code **)(puVar2 + 0x597c) = FUN_00088d60;
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0x5988)))) = 0xfff7729f;
    *(code **)(puVar2 + 0x5980) = FUN_00088caa;
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0x598c)))) = 0xfff77355;
    thunk_FUN_0007995c();
    cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x5990)))));
    if (((int8_t)cVar1) == -0x3d) {
LAB_00088e86:
      iVar3 = FUN_00088d60();
      if (iVar3 == 0) goto LAB_00088eae;
      goto LAB_00088e90;
    }
    if ((((int8_t)cVar1) == -0x2e) || (((int8_t)cVar1) == -0x4c)) goto LAB_00088eae;
  }
  else {
    if (((int8_t)cVar1) == -0x3d) {
      iVar3 = FUN_00088b84(((int *)camry_host_ptr((uint32_t)(param_2))), ((void *)camry_host_ptr((uint32_t)(param_3))), param_4, param_5, ((uint *)camry_host_ptr((uint32_t)(param_6))), param_7);
      if (iVar3 == 0) {
        (*((uint *)camry_host_ptr((uint32_t)(puVar2 + 0x59fc)))) = param_1;
        (*((uint *)camry_host_ptr((uint32_t)(puVar2 + 0x5a00)))) = ~param_1;
        *(code **)(puVar2 + 0x5980) = FUN_00088caa;
        (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0x598c)))) = 0xfff77355;
        goto LAB_00088e86;
      }
LAB_00088e90:
      FUN_00087edc(0);
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x5990))))) = 0xe1;
      goto LAB_00088eae;
    }
    if ((((int8_t)cVar1) == -0x2e) || (((int8_t)cVar1) == -0x4c)) {
      iVar3 = 2;
      goto LAB_00088eae;
    }
  }
  iVar3 = 1;
LAB_00088eae:
  FUN_00088436();
  return iVar3;
}



void FUN_00088ec0(void)

{
  uint uVar1;
  uint uVar2;
  char cVar3;
  uint32_t puVar4;
  int iVar5;
  
  puVar4 = 0xfebeb800u;
  if (((int8_t)DAT_febf1204) == -0x1f) {
    puVar4 = 0xfebeb800u;
    FUN_00088c36(DAT_febf1205);
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x5a04u + (uint32_t)((int)puVar4))))) = (code)0xd2;
  }
  cVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x5990)))));
  if (((int8_t)cVar3) == -0x2e) {
    uVar1 = (*((uint *)camry_host_ptr((uint32_t)(puVar4 + 0x5970)))) + 1;
    (*((uint *)camry_host_ptr((uint32_t)(puVar4 + 0x5970)))) = uVar1;
    if (uVar1 < 7) {
      return;
    }
    thunk_FUN_000799da();
  }
  else {
    if (((int8_t)cVar3) != -0x3d) {
      if (((int8_t)cVar3) != -0x4c) {
        return;
      }
      uVar1 = (*((uint *)camry_host_ptr((uint32_t)(puVar4 + 0x5978)))) + 1;
      (*((uint *)camry_host_ptr((uint32_t)(puVar4 + 0x5978)))) = uVar1;
      uVar2 = (*((uint *)camry_host_ptr((uint32_t)(puVar4 + 0x5974)))) + 1;
      (*((uint *)camry_host_ptr((uint32_t)(puVar4 + 0x5974)))) = uVar2;
      if ((uVar1 < 0xc) && (uVar2 < 0xc)) {
        return;
      }
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar4 + 0x5998)))) = 0xffffffff;
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar4 + 0x5994)))) = 0;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x5990))))) = 0xa5;
      iVar5 = FUN_00088574();
      FUN_00087edc(iVar5 != 1);
      goto LAB_00088f70;
    }
    uVar1 = (*((uint *)camry_host_ptr((uint32_t)(puVar4 + 0x5974)))) + 1;
    (*((uint *)camry_host_ptr((uint32_t)(puVar4 + 0x5974)))) = uVar1;
    if (uVar1 < 0xc) {
      return;
    }
    FUN_00087edc(0);
  }
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar4 + 0x5998)))) = 0xffffffff;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar4 + 0x5994)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x5990))))) = 0xa5;
LAB_00088f70:
  FUN_00088caa(1);
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



undefined4
FUN_00088fc0(int *param_1,void *param_2,uint param_3,void *param_4,uint param_5,uint param_6)

{
  uint32_t puVar1;
  uint byte_count;
  undefined4 uVar2;
  
  puVar1 = 0xfebeb800u;
  if ((((((uintptr_t)(param_1)==(uintptr_t)((int *)0x0)) || ((uintptr_t)(param_2)==(uintptr_t)((void *)0x0))) || ((uintptr_t)(param_4)==(uintptr_t)((void *)0x0))) ||
      ((param_6 == 0 || (*param_1 != 1)))) ||
     ((0x50 < param_3 || ((param_5 == 0 || (0x80 < param_5)))))) {
    uVar2 = 1;
  }
  else {
    uVar2 = 0;
    DAT_febf1318 = param_6;
    DAT_febf128c = ~param_6;
    f33_memcpy_forward(FUN_febf12b8,param_2,param_3);
    byte_count = ~param_3 + 1 & 0xf;
    if (byte_count != 0) {
      f33_memzero(((void *)camry_host_ptr((uint32_t)(0xfebf12b8u + param_3))), byte_count);
    }
    f33_memcpy_forward(((undefined *)camry_host_ptr(0xfebf1308u)),param_4,param_5 + 7 >> 3);
    *(undefined **)(puVar1 + 0x5a9c) = ((void *)camry_host_ptr((uint32_t)(puVar1 + 0x5ab4)));
    *(undefined **)(puVar1 + 0x5a98) = ((void *)camry_host_ptr((uint32_t)(puVar1 + 0x5aa0)));
    *(code **)(puVar1 + 0x5aa0) = FUN_febf12b8;
    (*((uint *)camry_host_ptr((uint32_t)(puVar1 + 0x5aa4)))) = param_3 << 3;
    *(undefined **)(puVar1 + 0x5aa8) = ((undefined *)camry_host_ptr(0xfebf1308u));
    (*((uint *)camry_host_ptr((uint32_t)(puVar1 + 0x5aac)))) = param_5 & 0x7f;
    (*((uint *)camry_host_ptr((uint32_t)(puVar1 + 0x5ab0)))) = (uint)*(byte *)(param_1 + 1);
  }
  return uVar2;
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



undefined4 FUN_00089170(void)

{
  uint32_t puVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  
  puVar1 = 0xfebeb800u;
  uVar4 = 1;
  if (((int8_t)DAT_febf1190) == -0x3d) {
    DAT_febf1194 = camry_host_addr(FUN_00089114);
    DAT_febf1198 = 0xfff76eeb;
    DAT_febf1190 = -0x4c;
    iVar2 = FUN_0008a8e4(((undefined *)camry_host_ptr(0xfebf1298u)));
    if (iVar2 == 0) {
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x5978)))) = 0;
      uVar4 = 0;
    }
    else {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x5990))))) = 0xc3;
      uVar3 = FUN_0008afea();
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x5984)))) = uVar3;
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x5994)))) = 0;
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x5998)))) = 0xffffffff;
    }
  }
  return uVar4;
}



int FUN_000891cc(uint param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4,
                undefined4 param_5,undefined4 param_6,undefined4 param_7)

{
  char cVar1;
  uint32_t puVar2;
  int iVar3;
  
  puVar2 = 0xfebeb800u;
  if (DAT_febf1190 == '\0') {
    return 1;
  }
  iVar3 = FUN_00088362();
  if (iVar3 != 1) {
    return 2;
  }
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x5990)))));
  if (((int8_t)cVar1) == -0x1f) {
    iVar3 = FUN_00088fc0(((int *)camry_host_ptr((uint32_t)(param_2))), ((void *)camry_host_ptr((uint32_t)(param_3))), param_4, ((void *)camry_host_ptr((uint32_t)(param_5))), param_6, param_7);
    if (iVar3 != 0) goto LAB_000892ba;
    (*((uint *)camry_host_ptr((uint32_t)(puVar2 + 0x5a88)))) = param_1;
    (*((uint *)camry_host_ptr((uint32_t)(puVar2 + 0x5a90)))) = ~param_1;
    *(code **)(puVar2 + 0x597c) = FUN_00089170;
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0x5988)))) = 0xfff76e8f;
    *(code **)(puVar2 + 0x5980) = FUN_000890ba;
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0x598c)))) = 0xfff76f45;
    thunk_FUN_0007995c();
    cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x5990)))));
    if (((int8_t)cVar1) == -0x3d) {
LAB_00089292:
      iVar3 = FUN_00089170();
      if (iVar3 == 0) goto LAB_000892ba;
      goto LAB_0008929c;
    }
    if ((((int8_t)cVar1) == -0x2e) || (((int8_t)cVar1) == -0x4c)) goto LAB_000892ba;
  }
  else {
    if (((int8_t)cVar1) == -0x3d) {
      iVar3 = FUN_00088fc0(((int *)camry_host_ptr((uint32_t)(param_2))), ((void *)camry_host_ptr((uint32_t)(param_3))), param_4, ((void *)camry_host_ptr((uint32_t)(param_5))), param_6, param_7);
      if (iVar3 == 0) {
        (*((uint *)camry_host_ptr((uint32_t)(puVar2 + 0x5a88)))) = param_1;
        (*((uint *)camry_host_ptr((uint32_t)(puVar2 + 0x5a90)))) = ~param_1;
        *(code **)(puVar2 + 0x5980) = FUN_000890ba;
        (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0x598c)))) = 0xfff76f45;
        goto LAB_00089292;
      }
LAB_0008929c:
      FUN_00087edc(0);
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x5990))))) = 0xe1;
      goto LAB_000892ba;
    }
    if ((((int8_t)cVar1) == -0x2e) || (((int8_t)cVar1) == -0x4c)) {
      iVar3 = 2;
      goto LAB_000892ba;
    }
  }
  iVar3 = 1;
LAB_000892ba:
  FUN_00088436();
  return iVar3;
}



void FUN_000892cc(void)

{
  uint uVar1;
  uint uVar2;
  char cVar3;
  uint32_t puVar4;
  int iVar5;
  
  puVar4 = 0xfebeb800u;
  if (((int8_t)DAT_febf1294) == -0x1f) {
    puVar4 = 0xfebeb800u;
    FUN_0008906c(DAT_febf1295);
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x5a94))))) = 0xd2;
  }
  cVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x5990)))));
  if (((int8_t)cVar3) == -0x2e) {
    uVar1 = (*((uint *)camry_host_ptr((uint32_t)(puVar4 + 0x5970)))) + 1;
    (*((uint *)camry_host_ptr((uint32_t)(puVar4 + 0x5970)))) = uVar1;
    if (uVar1 < 7) {
      return;
    }
    thunk_FUN_000799da();
  }
  else {
    if (((int8_t)cVar3) != -0x3d) {
      if (((int8_t)cVar3) != -0x4c) {
        return;
      }
      uVar1 = (*((uint *)camry_host_ptr((uint32_t)(puVar4 + 0x5978)))) + 1;
      (*((uint *)camry_host_ptr((uint32_t)(puVar4 + 0x5978)))) = uVar1;
      uVar2 = (*((uint *)camry_host_ptr((uint32_t)(puVar4 + 0x5974)))) + 1;
      (*((uint *)camry_host_ptr((uint32_t)(puVar4 + 0x5974)))) = uVar2;
      if ((uVar1 < 0xc) && (uVar2 < 0xc)) {
        return;
      }
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar4 + 0x5998)))) = 0xffffffff;
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar4 + 0x5994)))) = 0;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x5990))))) = 0xa5;
      iVar5 = FUN_00088574();
      FUN_00087edc(iVar5 != 1);
      goto LAB_0008937c;
    }
    uVar1 = (*((uint *)camry_host_ptr((uint32_t)(puVar4 + 0x5974)))) + 1;
    (*((uint *)camry_host_ptr((uint32_t)(puVar4 + 0x5974)))) = uVar1;
    if (uVar1 < 0xc) {
      return;
    }
    FUN_00087edc(0);
  }
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar4 + 0x5998)))) = 0xffffffff;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar4 + 0x5994)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x5990))))) = 0xa5;
LAB_0008937c:
  FUN_000890ba(1);
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



void FUN_0008939e(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  thunk_FUN_0006a45e();
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x5b74)))) = 0xffffffff;
  (*((undefined4 *)camry_host_ptr((uint32_t)(0x5b70u + (int)puVar1)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x5b7a))))) = 0xd2;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x5b79))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x5b78))))) = 0xe1;
  thunk_FUN_0006a4c4();
  return;
}



bool FUN_000893ca(void)

{
  char cVar1;
  uint32_t puVar2;
  puVar2 = 0xfebeb800u;
  thunk_FUN_0006a45e();
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x5b7a)))));
  if (((int8_t)cVar1) == -0x2e) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x5b7a))))) = 0xe1;
  }
  thunk_FUN_0006a4c4();
  return cVar1 == -0x2e;
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



void FUN_00089428(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  thunk_FUN_0006a45e();
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x5b7a))))) = 0xd2;
  thunk_FUN_0006a4c4();
  return;
}



int FUN_00089440(undefined2 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4,
                undefined4 param_5,undefined4 param_6,undefined1 param_7)

{
  char cVar1;
  uint32_t puVar2;
  undefined4 uVar3;
  int iVar4;
  uint uVar5;
  code *pcVar6;
  
  puVar2 = 0xfebeb800u;
  iVar4 = FUN_000893ca();
  if (iVar4 == 1) {
    cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x5b78)))));
    if (((int8_t)cVar1) == -0x1f) {
      uVar5 = camry_host_addr(FUN_000893f2(param_1));
      if ((uVar5 == 0) || (pcVar6 = *(code **)(uVar5 + 0x14),(uintptr_t)(pcVar6)==(uintptr_t)(f33_reset_vector))) {
        FUN_00089414();
        iVar4 = 1;
      }
      else {
        uVar3 = (*((undefined4 *)camry_host_ptr((uint32_t)(uVar5 + 0x1c))));
        (*((uint *)camry_host_ptr((uint32_t)(puVar2 + 0x5b74)))) = ~uVar5;
        (*((uint *)camry_host_ptr((uint32_t)(0x5b70u + (int)puVar2)))) = uVar5;
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x5b78))))) = 0xa5;
        iVar4 = (*(int (*)())pcVar6)(uVar3,param_2,param_3,param_4,param_5,param_6,param_7);
        if (iVar4 != 0) {
          FUN_00089414();
        }
      }
    }
    else if (((int8_t)cVar1) == -0x5b) {
      iVar4 = 2;
    }
    else {
      iVar4 = 1;
      if (cVar1 != '\0') {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x5b78))))) = 0;
      }
    }
    FUN_00089428();
  }
  else {
    iVar4 = 2;
  }
  return iVar4;
}



void FUN_000894dc(undefined1 param_1)

{
  uint uVar1;
  
  uVar1 = DAT_febf1370;
  if (((int8_t)DAT_febf1378) == -0x5b) {
    if (DAT_febf1370 == ~DAT_febf1374) {
      if ((DAT_febf1370 != 0) && ((*((int *)camry_host_ptr((uint32_t)(DAT_febf1370 + 4)))) != 0)) {
        FUN_00089414();
        (*(int (*)())*(code **)(uVar1 + 4))(param_1);
      }
    }
    else {
      DAT_febf1379 = 1;
      FUN_00089414();
    }
  }
  return;
}



undefined4 FUN_00089526(void)

{
  char cVar1;
  uint uVar2;
  uint32_t puVar3;
  uint uVar4;
  
  puVar3 = 0xfebeb800u;
  thunk_FUN_0006a45e();
  uVar2 = (*((uint *)camry_host_ptr((uint32_t)(puVar3 + 0x5b74))));
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x5b78)))));
  uVar4 = (*((uint *)camry_host_ptr((uint32_t)(0x5b70u + (int)puVar3))));
  thunk_FUN_0006a4c4();
  if (((int8_t)cVar1) == -0x5b) {
    if (uVar4 == ~uVar2) {
      if ((uVar4 != 0) && ((uintptr_t)(*(code **)(uVar4 + 0x18))!=(uintptr_t)(f33_reset_vector))) {
        (*(int (*)())*(code **)(uVar4 + 0x18))();
      }
    }
    else {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x5b79))))) = 1;
      FUN_00089414();
    }
  }
  return 0;
}



void FUN_000895a4(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  thunk_FUN_0006a45e();
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x5b80)))) = 0xffffffff;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x5b7c)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x5b86))))) = 0xd2;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x5b85))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x5b84))))) = 0xe1;
  thunk_FUN_0006a4c4();
  return;
}



bool FUN_000895d0(void)

{
  char cVar1;
  uint32_t puVar2;
  puVar2 = 0xfebeb800u;
  thunk_FUN_0006a45e();
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x5b86)))));
  if (((int8_t)cVar1) == -0x2e) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x5b86))))) = 0xe1;
  }
  thunk_FUN_0006a4c4();
  return cVar1 == -0x2e;
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



void FUN_0008962e(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  thunk_FUN_0006a45e();
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x5b86))))) = 0xd2;
  thunk_FUN_0006a4c4();
  return;
}



int FUN_00089646(undefined2 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4,
                undefined4 param_5,undefined4 param_6,undefined4 param_7)

{
  char cVar1;
  uint32_t puVar2;
  undefined4 uVar3;
  int iVar4;
  uint uVar5;
  code *pcVar6;
  
  puVar2 = 0xfebeb800u;
  iVar4 = FUN_000895d0();
  if (iVar4 == 1) {
    cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x5b84)))));
    if (((int8_t)cVar1) == -0x1f) {
      uVar5 = camry_host_addr(FUN_000895f8(param_1));
      if ((uVar5 == 0) || (pcVar6 = *(code **)(uVar5 + 0x14),(uintptr_t)(pcVar6)==(uintptr_t)(f33_reset_vector))) {
        FUN_0008961a();
        iVar4 = 1;
      }
      else {
        uVar3 = (*((undefined4 *)camry_host_ptr((uint32_t)(uVar5 + 0x1c))));
        (*((uint *)camry_host_ptr((uint32_t)(puVar2 + 0x5b80)))) = ~uVar5;
        (*((uint *)camry_host_ptr((uint32_t)(puVar2 + 0x5b7c)))) = uVar5;
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x5b84))))) = 0xa5;
        iVar4 = (*(int (*)())pcVar6)(uVar3,param_2,param_3,param_4,param_5,param_6,param_7);
        if (iVar4 != 0) {
          FUN_0008961a();
        }
      }
    }
    else if (((int8_t)cVar1) == -0x5b) {
      iVar4 = 2;
    }
    else {
      iVar4 = 1;
      if (cVar1 != '\0') {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x5b84))))) = 0;
      }
    }
    FUN_0008962e();
  }
  else {
    iVar4 = 2;
  }
  return iVar4;
}



void FUN_000896e0(undefined1 param_1)

{
  uint uVar1;
  
  uVar1 = DAT_febf137c;
  if (((int8_t)DAT_febf1384) == -0x5b) {
    if (DAT_febf137c == ~DAT_febf1380) {
      if ((DAT_febf137c != 0) && ((*((int *)camry_host_ptr((uint32_t)(DAT_febf137c + 4)))) != 0)) {
        FUN_0008961a();
        (*(int (*)())*(code **)(uVar1 + 4))(param_1);
      }
    }
    else {
      DAT_febf1385 = 1;
      FUN_0008961a();
    }
  }
  return;
}



undefined4 FUN_0008972a(void)

{
  char cVar1;
  uint uVar2;
  uint32_t puVar3;
  uint uVar4;
  
  puVar3 = 0xfebeb800u;
  thunk_FUN_0006a45e();
  uVar2 = (*((uint *)camry_host_ptr((uint32_t)(puVar3 + 0x5b80))));
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x5b84)))));
  uVar4 = (*((uint *)camry_host_ptr((uint32_t)(puVar3 + 0x5b7c))));
  thunk_FUN_0006a4c4();
  if (((int8_t)cVar1) == -0x5b) {
    if (uVar4 == ~uVar2) {
      if ((uVar4 != 0) && ((uintptr_t)(*(code **)(uVar4 + 0x18))!=(uintptr_t)(f33_reset_vector))) {
        (*(int (*)())*(code **)(uVar4 + 0x18))();
      }
    }
    else {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x5b85))))) = 1;
      FUN_0008961a();
    }
  }
  return 0;
}



void FUN_000897a8(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  thunk_FUN_0006a45e();
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x5b8c)))) = 0xffffffff;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x5b88)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x5b92))))) = 0xd2;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x5b91))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x5b90))))) = 0xe1;
  thunk_FUN_0006a4c4();
  return;
}



bool FUN_000897d4(void)

{
  char cVar1;
  uint32_t puVar2;
  puVar2 = 0xfebeb800u;
  thunk_FUN_0006a45e();
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x5b92)))));
  if (((int8_t)cVar1) == -0x2e) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x5b92))))) = 0xe1;
  }
  thunk_FUN_0006a4c4();
  return cVar1 == -0x2e;
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



void FUN_00089820(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  thunk_FUN_0006a45e();
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x5b92))))) = 0xd2;
  thunk_FUN_0006a4c4();
  return;
}



int FUN_00089838(undefined2 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4,
                undefined4 param_5,undefined4 param_6)

{
  char cVar1;
  uint32_t puVar2;
  undefined4 uVar3;
  int iVar4;
  uint uVar5;
  code *pcVar6;
  
  puVar2 = 0xfebeb800u;
  iVar4 = FUN_000897d4();
  if (iVar4 == 1) {
    cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x5b90)))));
    if (((int8_t)cVar1) == -0x1f) {
      uVar5 = camry_host_addr(FUN_000897fc(param_1));
      if ((uVar5 == 0) || (pcVar6 = *(code **)(uVar5 + 0x14),(uintptr_t)(pcVar6)==(uintptr_t)(f33_reset_vector))) {
        FUN_0008980c();
        iVar4 = 1;
      }
      else {
        uVar3 = (*((undefined4 *)camry_host_ptr((uint32_t)(uVar5 + 0x1c))));
        (*((uint *)camry_host_ptr((uint32_t)(puVar2 + 0x5b8c)))) = ~uVar5;
        (*((uint *)camry_host_ptr((uint32_t)(puVar2 + 0x5b88)))) = uVar5;
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x5b90))))) = 0xa5;
        iVar4 = (*(int (*)())pcVar6)(uVar3,param_2,param_3,param_4,param_5,param_6);
        if (iVar4 != 0) {
          FUN_0008980c();
        }
      }
    }
    else if (((int8_t)cVar1) == -0x5b) {
      iVar4 = 2;
    }
    else {
      iVar4 = 1;
      if (cVar1 != '\0') {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x5b90))))) = 0;
      }
    }
    FUN_00089820();
  }
  else {
    iVar4 = 2;
  }
  return iVar4;
}



void FUN_000898ce(undefined1 param_1)

{
  uint uVar1;
  
  uVar1 = DAT_febf1388;
  if (((int8_t)DAT_febf1390) == -0x5b) {
    if (DAT_febf1388 == ~DAT_febf138c) {
      if ((DAT_febf1388 != 0) && ((*((int *)camry_host_ptr((uint32_t)(DAT_febf1388 + 4)))) != 0)) {
        FUN_0008980c();
        (*(int (*)())*(code **)(uVar1 + 4))(param_1);
      }
    }
    else {
      DAT_febf1391 = 1;
      FUN_0008980c();
    }
  }
  return;
}



undefined4 FUN_00089918(void)

{
  char cVar1;
  uint uVar2;
  uint32_t puVar3;
  uint uVar4;
  
  puVar3 = 0xfebeb800u;
  thunk_FUN_0006a45e();
  uVar2 = (*((uint *)camry_host_ptr((uint32_t)(puVar3 + 0x5b8c))));
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x5b90)))));
  uVar4 = (*((uint *)camry_host_ptr((uint32_t)(puVar3 + 0x5b88))));
  thunk_FUN_0006a4c4();
  if (((int8_t)cVar1) == -0x5b) {
    if (uVar4 == ~uVar2) {
      if ((uVar4 != 0) && ((uintptr_t)(*(code **)(uVar4 + 0x18))!=(uintptr_t)(f33_reset_vector))) {
        (*(int (*)())*(code **)(uVar4 + 0x18))();
      }
    }
    else {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x5b91))))) = 1;
      FUN_0008980c();
    }
  }
  return 0;
}



void FUN_00089996(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  thunk_FUN_0006a45e();
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x5b98)))) = 0xffffffff;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x5b94)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x5b9e))))) = 0xd2;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x5b9d))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x5b9c))))) = 0xe1;
  thunk_FUN_0006a4c4();
  return;
}



bool FUN_000899c2(void)

{
  char cVar1;
  uint32_t puVar2;
  puVar2 = 0xfebeb800u;
  thunk_FUN_0006a45e();
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x5b9e)))));
  if (((int8_t)cVar1) == -0x2e) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x5b9e))))) = 0xe1;
  }
  thunk_FUN_0006a4c4();
  return cVar1 == -0x2e;
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



void FUN_00089a0e(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  thunk_FUN_0006a45e();
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x5b9e))))) = 0xd2;
  thunk_FUN_0006a4c4();
  return;
}



int FUN_00089a26(undefined2 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4,
                undefined4 param_5,undefined4 param_6)

{
  char cVar1;
  uint32_t puVar2;
  undefined4 uVar3;
  int iVar4;
  uint uVar5;
  code *pcVar6;
  
  puVar2 = 0xfebeb800u;
  iVar4 = FUN_000899c2();
  if (iVar4 != 1) {
    return 2;
  }
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x5b9c)))));
  if (((int8_t)cVar1) == -0x1f) {
    uVar5 = camry_host_addr(FUN_000899ea(param_1));
    if ((uVar5 != 0) && (pcVar6 = *(code **)(uVar5 + 0x14),(uintptr_t)(pcVar6)!=(uintptr_t)(f33_reset_vector))) {
      uVar3 = (*((undefined4 *)camry_host_ptr((uint32_t)(uVar5 + 0x1c))));
      (*((uint *)camry_host_ptr((uint32_t)(puVar2 + 0x5b98)))) = ~uVar5;
      (*((uint *)camry_host_ptr((uint32_t)(puVar2 + 0x5b94)))) = uVar5;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x5b9c))))) = 0xa5;
      iVar4 = (*(int (*)())pcVar6)(uVar3,param_2,param_3,param_4,param_5,param_6);
      if (iVar4 != 0) {
        FUN_000899fa();
      }
      goto LAB_00089aa8;
    }
    FUN_000899fa();
  }
  else if (cVar1 != '\0') {
    if (((int8_t)cVar1) == -0x5b) {
      iVar4 = 2;
    }
    else {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x5b9c))))) = 0;
      iVar4 = 1;
    }
    goto LAB_00089aa8;
  }
  iVar4 = 1;
LAB_00089aa8:
  FUN_00089a0e();
  return iVar4;
}



/* Only activeA5 with valid complemented retained descriptor and nonnull callback+4 delivers. Reset
   channel before invoking saved callback(result). Pointer mismatch sets error1 and resets without
   callback. Explicit software callback input is not an ICU-S hardware result. */

void f33_crypto_key_job_deliver_completion(uchar result)

{
  uint uVar1;
  
  uVar1 = DAT_febf1394;
  if (((int8_t)DAT_febf139c) == -0x5b) {
    if (DAT_febf1394 == ~DAT_febf1398) {
      if ((DAT_febf1394 != 0) && ((*((int *)camry_host_ptr((uint32_t)(DAT_febf1394 + 4)))) != 0)) {
        FUN_000899fa();
        (*(int (*)())*(code **)(uVar1 + 4))(result);
      }
    }
    else {
      DAT_febf139d = 1;
      FUN_000899fa();
    }
  }
  return;
}



undefined4 FUN_00089b06(void)

{
  char cVar1;
  uint uVar2;
  uint32_t puVar3;
  uint uVar4;
  
  puVar3 = 0xfebeb800u;
  thunk_FUN_0006a45e();
  uVar2 = (*((uint *)camry_host_ptr((uint32_t)(puVar3 + 0x5b98))));
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x5b9c)))));
  uVar4 = (*((uint *)camry_host_ptr((uint32_t)(puVar3 + 0x5b94))));
  thunk_FUN_0006a4c4();
  if (((int8_t)cVar1) == -0x5b) {
    if (uVar4 == ~uVar2) {
      if ((uVar4 != 0) && ((uintptr_t)(*(code **)(uVar4 + 0x18))!=(uintptr_t)(f33_reset_vector))) {
        (*(int (*)())*(code **)(uVar4 + 0x18))();
      }
    }
    else {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x5b9d))))) = 1;
      FUN_000899fa();
    }
  }
  return 0;
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



int FUN_00089bc2(undefined2 param_1,undefined4 param_2,undefined4 *param_3,undefined1 param_4)

{
  char cVar1;
  uint uVar2;
  uint32_t puVar3;
  int iVar4;
  undefined4 *puVar5;
  
  DAT_febf13bc = 0;
  DAT_febf13bd = 1;
  puVar3 = 0xfebeb800u;
  if ((uintptr_t)(param_3)==(uintptr_t)((undefined4 *)0x0)) {
    puVar5 = (undefined4 *)0x0;
  }
  else {
    DAT_febf13ac = *param_3;
    puVar5 = ((undefined *)camry_host_ptr(0xfebf13acu));
  }
  iVar4 = FUN_00089440(param_1, DAT_febf13a0, DAT_febf13a4, DAT_febf13a8, param_2, camry_host_addr(puVar5), param_4);
  if (iVar4 == 0) {
    uVar2 = 0;
    do {
      cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x5bbc)))));
      if (cVar1 == '\x01') {
        if ((uintptr_t)(param_3)!=(uintptr_t)((undefined4 *)0x0)) {
          *param_3 = (*((undefined4 *)camry_host_ptr((uint32_t)(puVar3 + 0x5bac))));
          iVar4 = 0;
          if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x5bbd))))) == '\0') break;
        }
        iVar4 = 1;
        break;
      }
      uVar2 = uVar2 + 1;
    } while (uVar2 < 0xe07);
    if (cVar1 == '\0') {
      iVar4 = 2;
    }
  }
  else if (iVar4 != 2 && iVar4 != 3) {
    iVar4 = 1;
  }
  return iVar4;
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
  if ((uintptr_t)(param_1)!=(uintptr_t)((undefined2 *)0x0)) {
    *param_1 = 0;
    return 0;
  }
  return 1;
}



void FUN_00089d18(void)

{
  undefined8 uVar1;
  int iVar2;
  uint uVar3;
  
  uVar1 = 0x23dfc00000000;
  for (uVar3 = 0; iVar2 = (int)((ulonglong)uVar1 >> 0x20), uVar3 < (*((uint *)camry_host_ptr((uint32_t)(iVar2 + 0x4078))));
      uVar3 = uVar3 + 1) {
    (*(int (*)())*(code **)(uVar3 * 4 + iVar2 + 0x4094))();
  }
  return;
}



int FUN_00089d3c(void)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  iVar2 = thunk_FUN_0008844e();
  if (iVar2 == 0) {
    FUN_00089d18();
  }
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x5bc0)))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + 0x5bc8)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x5bca))))) = 1;
  return iVar2;
}



int FUN_00089d5e(void)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  iVar2 = thunk_FUN_000884ea();
  if (iVar2 == 0) {
    FUN_00089d18();
  }
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x5bc0)))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + 0x5bc8)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x5bca))))) = 1;
  return iVar2;
}



int FUN_00089d80(void)

{
  uint32_t puVar1;
  uint32_t puVar2;
  int iVar3;
  uint uVar4;
  
  puVar1 = 0xfebeb800u;
  puVar2 = 0x23dfcu;
  if (DAT_febf13ca == '\x01') {
    DAT_febf13ca = '\0';
    DAT_febf13c4 = 0;
  }
  uVar4 = DAT_febf13c0;
  if (DAT_00027e7c <= DAT_febf13c0) {
    uVar4 = 0;
  }
  iVar3 = (*(int (*)())camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x27eb0u + (uint32_t)(uVar4) * 4u))))))();
  if (iVar3 == 2) {
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x5bc4)))) = (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0x4080))));
  }
  if ((*((int *)camry_host_ptr((uint32_t)(puVar1 + 0x5bc4)))) != 0) {
    iVar3 = 2;
    (*((int *)camry_host_ptr((uint32_t)(puVar1 + 0x5bc4)))) = (*((int *)camry_host_ptr((uint32_t)(puVar1 + 0x5bc4)))) + -1;
  }
  (*((uint *)camry_host_ptr((uint32_t)(puVar1 + 0x5bc0)))) = uVar4 + 1;
  return iVar3;
}



void FUN_00089dec(void)

{
  undefined8 uVar1;
  int iVar2;
  uint uVar3;
  
  uVar1 = 0x23dfcfebeb800;
  iVar2 = thunk_FUN_000886e0();
  if (iVar2 == 0) {
    iVar2 = ((void)(0), FUN_00089d80());
  }
  (*((short *)camry_host_ptr((uint32_t)((int)uVar1 + 0x5bc8)))) = (short)iVar2;
  if (iVar2 != 0) {
    FUN_00089dd6(iVar2);
  }
  for (uVar3 = 0; iVar2 = (int)((ulonglong)uVar1 >> 0x20), uVar3 < (*((uint *)camry_host_ptr((uint32_t)(iVar2 + 0x4074))));
      uVar3 = uVar3 + 1) {
    (*(int (*)())*(code **)(uVar3 * 4 + iVar2 + 0x4084))();
  }
  return;
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



undefined4 FUN_00089e72(undefined1 *param_1)

{
  undefined1 uVar1;
  undefined8 uVar2;
  int iVar3;
  undefined4 uVar4;
  uint uVar5;
  int local_20;
  int iStack_1c;
  int iStack_18;
  int iStack_14;
  
  uVar2 = 0x23dfc00000000;
  if ((uintptr_t)(param_1)==(uintptr_t)((undefined1 *)0x0)) {
    return 1;
  }
  iStack_1c = 0;
  local_20 = 0;
  iStack_14 = 0;
  iStack_18 = 0;
  for (uVar5 = 0; iVar3 = (int)((ulonglong)uVar2 >> 0x20), uVar5 < (*((uint *)camry_host_ptr((uint32_t)(iVar3 + 0x407c))));
      uVar5 = uVar5 + 1) {
    uVar4 = (*(int (*)())*(code **)(0x40a2u + uVar5 * 4 + iVar3 + 2))();
    FUN_00089e2c(uVar4,&local_20);
  }
  if (iStack_18 != 0) {
    uVar1 = 2;
    goto LAB_00089eda;
  }
  if (iStack_14 == 0) {
    if (local_20 == 0) {
      if (iStack_1c != 0) {
        uVar1 = 1;
        goto LAB_00089eda;
      }
    }
    else {
      uVar1 = 0;
      if (iStack_1c == 0) goto LAB_00089eda;
    }
  }
  uVar1 = 3;
LAB_00089eda:
  *param_1 = uVar1;
  return 0;
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



/* Far-call trampoline: prepare {lp},0 / jarl 0x8B060 / dispose 0,{lp},lp; byte-verified against the
   exact image. Forwards with registers and stack unchanged; marked as a thunk. Forwarding shape
   machine-verified; target semantics not recovered. */

void thunk_FUN_0008b060(void)

{
  FUN_0008b060();
  return;
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
  
  iVar2 = FUN_0008a2e4((int)0xaaaaaaaa);
  if ((((iVar2 == 1) && (iVar2 = FUN_0008a2e4(0x55555555), iVar2 == 1)) &&
      (iVar2 = FUN_0008a332((int)0xaaaaaaaa), iVar2 == 1)) &&
     ((iVar2 = FUN_0008a332(0x55555555), iVar2 == 1 &&
      (iVar2 = FUN_0008a378((int)0xaaaaaaaa), iVar2 == 1)))) {
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



undefined4 FUN_0008a538(void)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  uint32_t puVar4;
  uVar3 = DAT_febf1350;
  uVar2 = DAT_febf1340;
  uVar1 = DAT_febf1330;
  puVar4 = 0xfebeb800u;
  ICUSCTL = 1;
  if (~DAT_febf1340 == DAT_febf1350) {
    if (DAT_febf1330 < DAT_febf132c) {
      FUN_0008a514(((uint *)camry_host_ptr((uint32_t)(DAT_febf1340))));
      (*((uint *)camry_host_ptr((uint32_t)(puVar4 + 0x5b40)))) = uVar2 + 0x10;
      (*((uint *)camry_host_ptr((uint32_t)(puVar4 + 0x5b50)))) = uVar3 - 0x10;
      (*((uint *)camry_host_ptr((uint32_t)(puVar4 + 0x5b30)))) = uVar1 + 1;
      return 0;
    }
  }
  else {
    DAT_febf136d = 1;
  }
  return 0x12;
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



undefined4 FUN_0008a5ae(void)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  uint32_t puVar4;
  uVar3 = DAT_febf1354;
  uVar2 = DAT_febf1344;
  uVar1 = DAT_febf1338;
  puVar4 = 0xfebeb800u;
  ICUSCTL = 2;
  if (~DAT_febf1344 == DAT_febf1354) {
    if (DAT_febf1338 < DAT_febf1334) {
      FUN_0008a58a(((uint *)camry_host_ptr((uint32_t)(DAT_febf1344))));
      (*((uint *)camry_host_ptr((uint32_t)(puVar4 + 0x5b44)))) = uVar2 + 0x10;
      (*((uint *)camry_host_ptr((uint32_t)(puVar4 + 0x5b54)))) = uVar3 - 0x10;
      (*((uint *)camry_host_ptr((uint32_t)(puVar4 + 0x5b38)))) = uVar1 + 1;
      return 0;
    }
  }
  else {
    DAT_febf136d = 1;
  }
  return 0x12;
}



undefined4 FUN_0008a63c(undefined4 *param_1)

{
  ICUS_Status IVar1;
  uint uVar2;
  undefined4 uVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  uint *puVar7;
  uint uVar8;
  
  if (DAT_febf136c == '\0') {
    return 0x10;
  }
  if ((((uintptr_t)(param_1)!=(uintptr_t)((undefined4 *)0x0)) && (puVar7 = (uint *)*param_1,(uintptr_t)(puVar7)!=(uintptr_t)((uint *)0x0))) &&
     ((uintptr_t)((uint *)param_1[1])!=(uintptr_t)((uint *)0x0))) {
    uVar8 = puVar7[1];
    uVar6 = puVar7[3];
    if ((((uVar8 != 0) && (puVar7[2] < 0xf)) &&
        ((uVar4 = *puVar7, uVar4 != 0 && (uVar5 = *(uint *)param_1[1], uVar5 != 0)))) &&
       ((uVar6 == 0 || (uVar6 == 1)))) {
      if (uVar6 == 0) {
        uVar6 = 1;
      }
      else {
        uVar6 = 3;
      }
      uVar3 = 2;
      if (((((int8_t)DAT_febf136c) == -0x1f) && (IVar1.raw = ICUSSTS, IVar1.BUSY == 0)) &&
         (uVar2 = ICUSSTS2, (uVar2 & 3) == 0)) {
        DAT_febf1350 = ~uVar4;
        uVar3 = 0;
        ICUSPARAM = uVar8;
        DAT_febf131c = camry_host_addr(FUN_0008a538);
        DAT_febf1354 = ~uVar5;
        DAT_febf1360 = 0xfff75ac7;
        DAT_febf1330 = 0;
        DAT_febf1364 = 0xfff75a51;
        DAT_febf1338 = 0;
        DAT_febf1368 = 0xfff759ff;
        DAT_febf1320 = camry_host_addr(FUN_0008a5ae);
        DAT_febf1324 = camry_host_addr(((undefined *)camry_host_ptr(0x8a600u)));
        DAT_febf136c = -0x2e;
        DAT_febf1328 = uVar6;
        DAT_febf132c = uVar8;
        DAT_febf1334 = uVar8;
        DAT_febf1340 = uVar4;
        DAT_febf1344 = uVar5;
      }
      ICUSCMD = (uint32_t)(uVar6 | puVar7[2] << 0x10);
      return uVar3;
    }
  }
  return 0x11;
}



undefined4 FUN_0008a720(undefined4 *param_1)

{
  ICUS_Status IVar1;
  uint uVar2;
  uint uVar3;
  undefined4 uVar4;
  uint uVar5;
  uint uVar6;
  uint *puVar7;
  
  if (DAT_febf136c == '\0') {
    return 0x10;
  }
  if ((((uintptr_t)(param_1)!=(uintptr_t)((undefined4 *)0x0)) && (puVar7 = (uint *)*param_1,(uintptr_t)(puVar7)!=(uintptr_t)((uint *)0x0))) &&
     ((uintptr_t)((uint *)param_1[1])!=(uintptr_t)((uint *)0x0))) {
    uVar3 = puVar7[1];
    if (((puVar7[2] < 0xf) && ((uVar5 = *puVar7, uVar5 != 0 || (uVar3 == 0)))) &&
       (uVar6 = *(uint *)param_1[1], uVar6 != 0)) {
      uVar4 = 2;
      if (((((int8_t)DAT_febf136c) == -0x1f) && (IVar1.raw = ICUSSTS, IVar1.BUSY == 0)) &&
         (uVar2 = ICUSSTS2, (uVar2 & 3) == 0)) {
        DAT_febf132c = 0x2000000;
        if (uVar3 < 0xffffff81) {
          DAT_febf132c = uVar3 + 0x7f >> 7;
        }
        DAT_febf1334 = 1;
        DAT_febf1350 = ~uVar5;
        uVar4 = 0;
        DAT_febf1330 = 0;
        DAT_febf1354 = ~uVar6;
        DAT_febf1328 = 5;
        ICUSDAT = 0;
        DAT_febf131c = camry_host_addr(FUN_0008a538);
        ICUSDAT = uVar3 >> 0x18 | uVar3 >> 8 & 0xff00 | (uVar3 & 0xff00) << 8 | uVar3 << 0x18;
        DAT_febf1360 = 0xfff75ac7;
        ICUSDAT = 0;
        DAT_febf1364 = 0xfff75a51;
        DAT_febf1338 = 0;
        DAT_febf1368 = 0xfff759ff;
        ICUSDAT = 0;
        DAT_febf1320 = camry_host_addr(FUN_0008a5ae);
        DAT_febf1324 = camry_host_addr(((undefined *)camry_host_ptr(0x8a600u)));
        DAT_febf136c = -0x2e;
        DAT_febf1340 = uVar5;
        DAT_febf1344 = uVar6;
      }
      ICUSCMD = (uint32_t)(puVar7[2] << 0x10 | 5);
      return uVar4;
    }
  }
  return 0x11;
}



undefined4 FUN_0008a832(void)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  uint32_t puVar4;
  uint uVar5;
  
  uVar3 = DAT_febf1350;
  uVar2 = DAT_febf1340;
  uVar1 = DAT_febf1330;
  puVar4 = 0xfebeb800u;
  ICUSCTL = 1;
  if ((~DAT_febf1340 == DAT_febf1350) && (~DAT_febf1348 == DAT_febf1358)) {
    if (DAT_febf1330 < DAT_febf132c) {
      uVar5 = DAT_febf1348;
      if (DAT_febf1330 != DAT_febf132c - 1) {
        uVar5 = DAT_febf1340;
      }
      FUN_0008a514(((uint *)camry_host_ptr((uint32_t)(uVar5))));
      (*((uint *)camry_host_ptr((uint32_t)(puVar4 + 0x5b40)))) = uVar2 + 0x10;
      (*((uint *)camry_host_ptr((uint32_t)(puVar4 + 0x5b50)))) = uVar3 - 0x10;
      (*((uint *)camry_host_ptr((uint32_t)(puVar4 + 0x5b30)))) = uVar1 + 1;
      return 0;
    }
  }
  else {
    DAT_febf136d = 1;
  }
  return 0x12;
}



undefined4 FUN_0008a898(void)

{
  uint uVar1;
  undefined4 *puVar2;
  uint32_t puVar3;
  undefined4 local_1c [4];
  
  puVar2 = ((void *)camry_host_ptr((uint32_t)(DAT_febf1344)));
  uVar1 = DAT_febf1338;
  puVar3 = 0xfebeb800u;
  ICUSCTL = 2;
  if (~(uint)DAT_febf1344 == DAT_febf1354) {
    if (DAT_febf1338 < DAT_febf1334) {
      FUN_0008a58a(local_1c);
      *puVar2 = local_1c[0];
      (*((uint *)camry_host_ptr((uint32_t)(puVar3 + 0x5b38)))) = uVar1 + 1;
      return 0;
    }
  }
  else {
    DAT_febf136d = 1;
  }
  return 0x12;
}



undefined4 FUN_0008a8e4(int *param_1)

{
  ICUS_Status IVar1;
  uint *puVar2;
  uint uVar3;
  undefined4 uVar4;
  uint uVar5;
  uint uVar6;
  uint uVar7;
  uint uVar8;
  
  if (DAT_febf136c == '\0') {
    return 0x10;
  }
  if ((((uintptr_t)(param_1)!=(uintptr_t)((int *)0x0)) && (puVar2 = (uint *)*param_1,(uintptr_t)(puVar2)!=(uintptr_t)((uint *)0x0))) &&
     (uVar5 = param_1[1], uVar5 != 0)) {
    uVar3 = puVar2[1];
    if ((((puVar2[4] < 0xf) && (puVar2[3] < 0x80)) &&
        ((uVar6 = *puVar2, uVar6 != 0 || (uVar3 == 0)))) && (uVar7 = puVar2[2], uVar7 != 0)) {
      IVar1.raw = ICUSSTS;
      uVar4 = 2;
      uVar8 = ICUSSTS2;
      if (((((int8_t)DAT_febf136c) == -0x1f) && (IVar1.BUSY == 0)) && ((uVar8 & 3) == 0)) {
        uVar8 = 0x2000000;
        if (uVar3 < 0xffffff81) {
          uVar8 = uVar3 + 0x7f >> 7;
        }
        ICUSDAT = 0;
        DAT_febf1334 = 1;
        DAT_febf132c = uVar8 + 1;
        ICUSDAT = uVar3 >> 0x18 | uVar3 >> 8 & 0xff00 | (uVar3 & 0xff00) << 8 | uVar3 << 0x18;
        DAT_febf1350 = ~uVar6;
        DAT_febf1338 = 0;
        DAT_febf1358 = ~uVar7;
        DAT_febf1330 = 0;
        DAT_febf1354 = ~uVar5;
        DAT_febf1328 = 7;
        DAT_febf131c = camry_host_addr(FUN_0008a832);
        DAT_febf1320 = camry_host_addr(FUN_0008a898);
        DAT_febf1360 = 0xfff757cd;
        ICUSDAT = puVar2[3];
        DAT_febf1364 = 0xfff75767;
        DAT_febf1324 = camry_host_addr(((undefined *)camry_host_ptr(0x8a600u)));
        DAT_febf1368 = 0xfff759ff;
        ICUSDAT = 0;
        DAT_febf136c = -0x2e;
        uVar4 = 0;
        DAT_febf1340 = uVar6;
        DAT_febf1344 = uVar5;
        DAT_febf1348 = uVar7;
      }
      ICUSCMD = (uint32_t)(puVar2[4] << 0x10 | 7);
      return uVar4;
    }
  }
  return 0x11;
}



void FUN_0008aa04(uint *param_1)

{
  uint uVar1;
  
  if ((uintptr_t)(param_1)!=(uintptr_t)((uint *)0x0)) {
    uVar1 = FHVE3;
    *param_1 = uVar1;
    uVar1 = FHVE15;
    param_1[1] = uVar1;
  }
  return;
}



void FUN_0008aa1c(uint *param_1)

{
  uint uVar1;
  
  if ((uintptr_t)(param_1)!=(uintptr_t)((uint *)0x0)) {
    FHVE3 = *param_1 & 1;
    FHVE15 = param_1[1] & 1;
    uVar1 = FHVE15;
    thunk_FUN_0008b060();
  }
  return;
}



void FUN_0008aa4a(void)

{
  uint local_c;
  uint uStack_8;
  
  local_c = 0;
  uStack_8 = 0;
  FUN_0008aa04(&local_c);
  local_c = local_c | 1;
  uStack_8 = uStack_8 | 1;
  FUN_0008aa1c(&local_c);
  return;
}



undefined4 FUN_0008aa6a(uint *param_1)

{
  ICUS_Status IVar1;
  uint uVar2;
  uint32_t puVar3;
  undefined4 uVar4;
  uint uVar5;
  uint uVar6;
  
  puVar3 = 0xfebeb800u;
  if (DAT_febf136c == '\0') {
    uVar4 = 0x10;
  }
  else if ((((uintptr_t)(param_1)==(uintptr_t)((uint *)0x0)) || (uVar6 = *param_1, uVar6 == 0)) ||
          (uVar5 = param_1[1], uVar5 == 0)) {
    uVar4 = 2;
  }
  else {
    uVar4 = 2;
    if (((((int8_t)DAT_febf136c) == -0x1f) && (IVar1.raw = ICUSSTS, IVar1.BUSY == 0)) &&
       (uVar2 = ICUSSTS2, (uVar2 & 3) == 0)) {
      FUN_0008aa4a();
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar3 + 0x5b2c)))) = 4;
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar3 + 0x5b34)))) = 3;
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar3 + 0x5b30)))) = 0;
      (*((uint *)camry_host_ptr((uint32_t)(puVar3 + 0x5b50)))) = ~uVar6;
      uVar4 = 0;
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar3 + 0x5b38)))) = 0;
      (*((uint *)camry_host_ptr((uint32_t)(puVar3 + 0x5b54)))) = ~uVar5;
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar3 + 0x5b28)))) = 8;
      *(code **)(puVar3 + 0x5b1c) = FUN_0008a538;
      (*((uint *)camry_host_ptr((uint32_t)(puVar3 + 0x5b40)))) = uVar6;
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar3 + 0x5b60)))) = 0xfff75ac7;
      (*((uint *)camry_host_ptr((uint32_t)(puVar3 + 0x5b44)))) = uVar5;
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar3 + 0x5b64)))) = 0xfff75a51;
      *(code **)(puVar3 + 0x5b20) = FUN_0008a5ae;
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar3 + 0x5b68)))) = 0xfff759ff;
      *(undefined1 **)(puVar3 + 0x5b24) = ((undefined *)camry_host_ptr(0x8a600u));
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x5b6c))))) = 0xd2;
    }
    ICUSCMD = (uint32_t)0x8;
  }
  return uVar4;
}



undefined4 FUN_0008ab82(void)

{
  uint uVar1;
  uint32_t puVar2;
  uint uVar3;
  
  uVar1 = DAT_febf1338;
  puVar2 = 0xfebeb800u;
  ICUSCTL = 2;
  if ((~DAT_febf1344 == DAT_febf1354) && (~DAT_febf134c == DAT_febf135c)) {
    if (DAT_febf1338 < DAT_febf1334) {
      uVar3 = DAT_febf1344;
      if (DAT_febf1338 != 0) {
        uVar3 = DAT_febf134c;
      }
      FUN_0008a58a(((uint *)camry_host_ptr((uint32_t)(uVar3))));
      (*((uint *)camry_host_ptr((uint32_t)(puVar2 + 0x5b38)))) = uVar1 + 1;
      return 0;
    }
  }
  else {
    DAT_febf136d = 1;
  }
  return 0x12;
}



undefined4 FUN_0008aca8(void)

{
  ICUS_Status IVar1;
  
  IVar1.raw = ICUSSTS;
  if (DAT_febf136c == '\0') {
    return 0x10;
  }
  if ((((int8_t)DAT_febf136c) != -0x1f) && (((int8_t)DAT_febf136c) != -0x3d)) {
    if (((int8_t)DAT_febf136c) != -0x2e) {
      return 2;
    }
    if (IVar1.BUSY != 0) {
      DAT_febf1320 = 0;
      DAT_febf131c = 0;
      ICUSCMD = (uint32_t)0x3f;
      DAT_febf1364 = 0xffffffff;
      DAT_febf1324 = camry_host_addr(((undefined *)camry_host_ptr(0x8a600u)));
      DAT_febf1360 = 0xffffffff;
      DAT_febf1368 = 0xfff759ff;
      DAT_febf1328 = 0x3f;
      DAT_febf136c = 0xc3;
      return 0;
    }
  }
  return 1;
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



undefined4 FUN_0008ada8(void)

{
  ICUS_Command IVar1;
  int iVar2;
  undefined4 uVar3;
  uint32_t puVar4;
  int iVar5;
  
  iVar2 = DAT_febf133c;
  puVar4 = 0xfebeb800u;
  IVar1.raw = ICUSCMD;
  if ((((IVar1.raw & 0xffff) == 0x7000) && (DAT_febf133c == 1)) ||
     (((IVar1.raw & 0xffff) == 0x7100 && (DAT_febf133c == 2)))) {
    ICUSCTL = 3;
    iVar5 = FUN_0008ad7a();
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x5b6c))))) = 0xe1;
    uVar3 = 1;
    if (((iVar2 == 1) && (iVar5 != 0)) || ((iVar2 == 2 && (iVar5 != 0x100c)))) {
      uVar3 = 2;
    }
  }
  else {
    uVar3 = 0x12;
  }
  return uVar3;
}



void FUN_0008ae02(undefined4 *param_1)

{
  DAT_febf131c = 0;
  DAT_febf1320 = 0;
  DAT_febf1360 = 0xffffffff;
  DAT_febf1328 = *param_1;
  DAT_febf1324 = camry_host_addr(FUN_0008ada8);
  DAT_febf1364 = 0xffffffff;
  DAT_febf1368 = 0xfff75257;
  return;
}



undefined4 FUN_0008aed6(uint param_1)

{
  ICUS_Command IVar1;
  
  IVar1.raw = ICUSCMD;
  if ((DAT_febf136c == '\0') || (((int8_t)DAT_febf136c) == -0x1f)) {
    return 0x10;
  }
  if ((((int8_t)DAT_febf136c) != -0x2e) && (((int8_t)DAT_febf136c) != -0x3d)) {
    return 2;
  }
  if ((IVar1.raw & 0xffff) != param_1) {
    return 0x12;
  }
  return 0;
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



void FUN_0008b120(void)

{
  undefined1 uStack_5;
  
  uStack_5 = 0;
  ((void)(&uStack_5), FUN_00098898());
  return;
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



/* Far-call trampoline: prepare {lp},0 / jarl 0x8B134 / dispose 0,{lp},lp; byte-verified against the
   exact image. Forwards with registers and stack unchanged; marked as a thunk. Forwarding shape
   machine-verified; target semantics not recovered. */

void thunk_FUN_0008b134(void)

{
  FUN_0008b134();
  return;
}



int FUN_0008b17e(void)

{
  int iVar1;
  
  if (f33_app_programming_admission_latched == '\0') {
    iVar1 = FUN_0004d5d8();
    if (iVar1 == 0) {
      ((void)(0), FUN_0004d5fe());
      f33_app_programming_admission_latched = 'Z';
    }
  }
  else {
    iVar1 = 0;
  }
  return iVar1;
}



/* WARNING: Inlined function: f33_diag_routine_local_dispatch_enabled */
/* Lower8B10C/8B110return0 exactly; application8B17E\u21924D5D8 rejectsE81F==11,66BA<0A00,or819A!=0.
   Successclears81AE onceandsets3B18=5A.
   Genericmergedstatusandstageownershipremainseparatefrommode9request. application8B17E→4D5D8
   rejectsE81F==11,66BA<0A00,or819A!=0. */

uint f33_app_programming_admit_and_stage(void)

{
  uint uVar1;
  uchar lower_status;
  uchar application_status;
  uint uVar2;
  uchar uVar3;
  undefined1 uStack_1d;
  undefined1 auStack_1c [8];
  
  application_status = DAT_febf3b1b;
  uStack_1d = DAT_febf3b1d;
  if (DAT_febf3b1a == '\0') {
    uVar2 = 0;
    do {
      uVar1 = uVar2 + 1;
      auStack_1c[uVar2] = 0;
      uVar2 = uVar1;
    } while (uVar1 < 8);
    lower_status = ((void)(0x8000200), (void)(10), (void)(0), (void)(auStack_1c), (void)(&uStack_1d), f33_return_const_0_8b10c());
  }
  else {
    if (DAT_febf3b1a != '\x01') {
      return 0;
    }
    lower_status = DAT_febf3b1c;
    if (DAT_febf3b1c == '\n') {
      lower_status = ((void)(0), (void)(10), f33_return_const_0_8b110());
    }
    if (application_status != '\n') goto LAB_0008b232;
  }
  application_status = ((void)(uStack_1d), FUN_0008b17e());
LAB_0008b232:
  uVar3 = '\x01';
  uVar2 = f33_merge_two_diagnostic_statuses(application_status,lower_status,'\0','\n');
  if ((uVar2 != 10) && (application_status = uVar3, lower_status = uVar3, uVar2 != 0)) {
    uVar3 = '\0';
  }
  DAT_febf3b1b = application_status;
  DAT_febf3b1c = lower_status;
  DAT_febf3b1a = uVar3;
  DAT_febf3b1d = uStack_1d;
  return uVar2;
}



/* WARNING: Inlined function: f33_diag_routine_local_dispatch_enabled */
/* WARNING: Removing unreachable block (ram,0x0008b2d2) */
/* R10 returns merged status. Stage1 formats4 bytes big-endian fromlocalword for
   exactno-oplower8B10C(08000201,10,...), then4D604; stage2 polls exactno-oplower8B110.
   Own3B1A/B/C/D stage/status state; initial8B334passesownzero3B14, not5D4C record.
   Actualr10returnsmergedstatus thoughcorpusvoid. */

uint f33_app_programming_submit_local_word(uint *param_1)

{
  bool bVar1;
  uint uVar2;
  uchar lower_status;
  char cVar3;
  uchar application_status;
  undefined1 uStack_21;
  undefined1 auStack_20 [8];
  
  application_status = DAT_febf3b1b;
  cVar3 = DAT_febf3b1a;
  uVar2 = 0;
  uStack_21 = DAT_febf3b1d;
  do {
    auStack_20[uVar2] = 0;
    uVar2 = uVar2 + 1;
  } while (uVar2 < 8);
  if (DAT_febf3b1a == '\x01') {
    uVar2 = *param_1;
    cVar3 = '\x02';
    auStack_20[0] = (undefined1)(uVar2 >> 0x18);
    auStack_20[1] = (undefined1)(uVar2 >> 0x10);
    auStack_20[3] = (undefined1)uVar2;
    auStack_20[2] = (undefined1)(uVar2 >> 8);
    lower_status = ((void)(0x8000201), (void)(10), (void)(4), (void)(auStack_20), (void)(&uStack_21), f33_return_const_0_8b10c());
  }
  else {
    if (DAT_febf3b1a != '\x02') {
      application_status = '\x01';
      lower_status = '\x01';
      goto LAB_0008b308;
    }
    lower_status = DAT_febf3b1c;
    if (DAT_febf3b1c == '\n') {
      lower_status = ((void)(0), (void)(10), f33_return_const_0_8b110());
    }
    if (application_status != '\n') goto LAB_0008b308;
  }
  f33_app_request_programming_transition();
  application_status = '\0';
LAB_0008b308:
  uVar2 = f33_merge_two_diagnostic_statuses(application_status,lower_status,'\0','\n');
  bVar1 = uVar2 != 10;
  if (bVar1) {
    application_status = '\x01';
  }
  DAT_febf3b1b = application_status;
  if (bVar1) {
    lower_status = '\x01';
  }
  DAT_febf3b1c = lower_status;
  if (bVar1) {
    cVar3 = '\0';
  }
  DAT_febf3b1a = cVar3;
  DAT_febf3b1d = uStack_21;
  return uVar2;
}



/* Exact wrapper ignores incomingr6 record pointer constructedby95B88; no consumed formal
   arguments.8B1B2 admissionthen8B262 submissionusing ownzeroedword3B14. Successsets3B19=5A
   andreturns10; anynonzero3B19 laterreturns10 withoutpollingcompletion. Constructed5D4C data
   isnotdirectresidenthandoffrecord;65F5E usesfixedROM31788. No
   completedprogramming/sessionpublication implied. */

uint f33_app_programming_handoff_pending_join(void)

{
  uint uVar1;
  uchar uVar2;
  
  uVar2 = f33_app_programming_pending_latch;
  if (f33_app_programming_pending_latch == '\0') {
    uVar1 = f33_app_programming_admit_and_stage();
    if (uVar1 == 0) {
      f33_app_programming_local_word = 0;
      uVar1 = f33_app_programming_submit_local_word(((uint *)camry_host_ptr((uint32_t)((0xfebf3b14u)))));
      if (uVar1 == 0) {
        uVar1 = 10;
        uVar2 = 'Z';
      }
    }
  }
  else {
    uVar1 = 10;
  }
  f33_app_programming_pending_latch = uVar2;
  return uVar1;
}



uint FUN_0008b36e(uchar param_1,uchar *param_2)

{
  uint uVar1;
  uchar uStack_d;
  
  f33_dcm_get_session(&uStack_d);
  uVar1 = f33_app_session_transition_precondition(uStack_d,param_1);
  return f33_diagnostic_status_to_nrc((uchar)uVar1,param_2);
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



/* Far-call trampoline: prepare {lp},0 / jarl 0x8B3D4 / dispose 0,{lp},lp; byte-verified against the
   exact image. Forwards with registers and stack unchanged; marked as a thunk. Forwarding shape
   machine-verified; target semantics not recovered. */

void thunk_FUN_0008b3d4(void)

{
  FUN_0008b3d4();
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



/* Retain metadata-selected payload length and choose local kind0 serializer or kind1 side route.
   Direct metadata reader returns application status, mapped through8B41A. Pending state3B26..2B is
   adapter state, not source-sampling atomicity. */

uint f33_did_read_application_adapter(uchar *output,ushort *length,uchar *nrc,ushort did)

{
  char cVar1;
  uchar uVar2;
  undefined4 uVar3;
  uint uVar4;
  uint uVar5;
  undefined1 uStack_43;
  undefined1 uStack_42;
  undefined1 uStack_41;
  uchar *apuStack_40 [3];
  uchar *puStack_34;
  undefined1 auStack_30 [2];
  ushort uStack_2e;
  undefined4 uStack_2c;
  
  cVar1 = DAT_febf3b26;
  uVar5 = (uint)DAT_febf3b27;
  uVar4 = (uint)DAT_febf3b28;
  uVar2 = f33_get_did_metadata_route_kind(did);
  f33_dcm_selected_did_payload_length(length);
  uStack_41 = (undefined1)did;
  uStack_43 = DAT_febf3b29;
  uStack_42 = (undefined1)(did >> 8);
  if (cVar1 == '\0') {
    if (uVar2 == '\0') {
      uVar5 = f33_read_selected_did_payload(output,*length);
      did = CONCAT11(uStack_42,uStack_41);
LAB_0008b4b4:
      uVar4 = 1;
LAB_0008b514:
      if (uVar5 != 2) goto LAB_0008b518;
    }
    else {
      uVar5 = 1;
      if (uVar2 != '\x01') goto LAB_0008b4b4;
      uVar4 = ((void)(0x40000000), (void)(2), (void)(2), (void)(&uStack_42), (void)(&uStack_43), f33_return_const_0_8b10c());
      did = CONCAT11(uStack_42,uStack_41);
LAB_0008b518:
      auStack_30[0] = (undefined1)uVar5;
      if (uVar4 != 2) goto LAB_0008b51c;
    }
    DAT_febf3b26 = 2;
    DAT_febf3b28 = (byte)uVar4;
    DAT_febf3b27 = (byte)uVar5;
    *length = 0;
  }
  else {
    if (cVar1 == '\x02') {
      if (uVar2 == '\0') {
        if (uVar5 == 2) {
          uVar5 = f33_read_selected_did_payload(output,*length);
          did = CONCAT11(uStack_42,uStack_41);
        }
      }
      else {
        uVar5 = 1;
      }
      uStack_42 = (undefined1)(did >> 8);
      uStack_41 = (undefined1)did;
      if (uVar2 != '\x01') goto LAB_0008b4b4;
      if (uVar4 == 2) {
        uVar4 = ((void)(5), (void)(2), (void)(uStack_43), f33_return_const_0_8b110());
        did = CONCAT11(uStack_42,uStack_41);
      }
      goto LAB_0008b514;
    }
    auStack_30[0] = 1;
    uVar4 = 1;
LAB_0008b51c:
    uStack_42 = (undefined1)(did >> 8);
    uStack_41 = (undefined1)did;
    if (uVar2 == '\x01') {
      auStack_30[0] = (undefined1)uVar4;
    }
    uVar3 = 0x5a;
    if (uVar2 == '\x01') {
      uVar3 = 0;
    }
    uStack_2e = *length;
    uStack_2c = 0;
    apuStack_40[0] = output;
    puStack_34 = nrc;
    uVar5 = FUN_0008b41a(uVar3,auStack_30,apuStack_40);
    DAT_febf3b27 = 1;
    DAT_febf3b28 = 1;
    DAT_febf3b26 = 0;
    uStack_43 = 0xff;
    if (uVar5 != 2) {
      DAT_febf3b26 = 0;
      DAT_febf3b27 = 1;
      DAT_febf3b28 = 1;
      DAT_febf3b29 = 0xff;
      DAT_febf3b2a = uVar2;
      return uVar5;
    }
  }
  DAT_febf3b29 = uStack_43;
  DAT_febf3b2a = uVar2;
  return 10;
}



/* WARNING: Inlined function: f33_diag_routine_local_dispatch_enabled */
/* Lifecycle3B21=0/1 andlowerstatus merge; consumes8E4BC status, emitsbyte-normalized meaningfulr10.
    */

uint f33_write_did_precondition_phase(ushort *matched_index,ushort did)

{
  uint uVar1;
  uchar lower_status;
  uint uVar2;
  uchar uVar3;
  uchar application_status;
  undefined1 uStack_25;
  undefined1 auStack_24 [8];
  
  application_status = DAT_febf3b22;
  uStack_25 = DAT_febf3b24;
  if (DAT_febf3b21 == '\0') {
    uVar2 = 0;
    do {
      uVar1 = uVar2 + 1;
      auStack_24[uVar2] = 0;
      uVar2 = uVar1;
    } while (uVar1 < 8);
    auStack_24[0] = (undefined1)(did >> 8);
    auStack_24[1] = (undefined1)did;
    lower_status = ((void)(0x78000000), (void)(2), (void)(2), (void)(auStack_24), (void)(&uStack_25), f33_return_const_0_8b10c());
  }
  else {
    if (DAT_febf3b21 != '\x01') {
      return 0;
    }
    lower_status = DAT_febf3b23;
    if (DAT_febf3b23 == '\x02') {
      lower_status = ((void)(5), (void)(2), f33_return_const_0_8b110());
    }
    if (application_status != '\x02') goto LAB_0008b602;
  }
  uVar2 = f33_find_write_did_and_check_precondition(matched_index,did);
  application_status = (uchar)uVar2;
LAB_0008b602:
  uVar3 = '\x01';
  uVar2 = f33_merge_two_diagnostic_statuses(application_status,lower_status,'\0','\x02');
  if ((uVar2 != 2) && (application_status = uVar3, lower_status = uVar3, uVar2 != 0)) {
    uVar3 = '\0';
  }
  DAT_febf3b22 = application_status;
  DAT_febf3b23 = lower_status;
  DAT_febf3b21 = uVar3;
  DAT_febf3b24 = uStack_25;
  return uVar2;
}



/* WARNING: Inlined function: f33_diag_routine_local_dispatch_enabled */
/* WARNING: Removing unreachable block (ram,0x0008b6b8) */
/* 8B66C cmp8,66E unsigned guard for7-byte staging; originalpointer/length still passed8E506
   at6E0..6E8.8B6FC merge result survives stores through71C and consumedcaller758. NOTvoid. */

uint f33_write_did_payload_phase(ushort matched_index,uchar *payload,ushort length)

{
  bool bVar1;
  uchar completion_status;
  uint uVar2;
  uchar lower_status;
  uint uVar3;
  char cVar4;
  uchar application_status;
  undefined1 uStack_2d;
  uchar auStack_2c [8];
  
  application_status = DAT_febf3b22;
  cVar4 = DAT_febf3b21;
  completion_status = DAT_febf3b20;
  uVar3 = (uint)length;
  uVar2 = 0;
  uStack_2d = DAT_febf3b24;
  do {
    auStack_2c[uVar2] = '\0';
    uVar2 = uVar2 + 1;
  } while (uVar2 < 8);
  if (DAT_febf3b21 == '\x01') {
    cVar4 = '\x02';
    if (uVar3 < 8) {
      for (uVar2 = 0; uVar2 < uVar3; uVar2 = uVar2 + 1 & 0xffff) {
        auStack_2c[uVar2] = payload[uVar2];
      }
      lower_status = ((void)(0x78000001), (void)(2), (void)(uVar3), (void)(auStack_2c), (void)(&uStack_2d), f33_return_const_0_8b10c());
    }
    else {
      lower_status = '\x04';
    }
  }
  else {
    if (DAT_febf3b21 != '\x02') {
      application_status = '\t';
      lower_status = '\t';
      goto LAB_0008b6f4;
    }
    lower_status = DAT_febf3b23;
    if (DAT_febf3b23 == '\x02') {
      lower_status = ((void)(5), (void)(2), f33_return_const_0_8b110());
    }
    if (application_status != '\x02') goto LAB_0008b6f4;
  }
  uVar2 = f33_dispatch_or_poll_write_did_action(completion_status,matched_index,payload,length);
  application_status = (uchar)uVar2;
LAB_0008b6f4:
  uVar2 = f33_merge_two_diagnostic_statuses(application_status,lower_status,'\0','\x02');
  bVar1 = uVar2 != 2;
  if (bVar1) {
    application_status = '\x01';
  }
  DAT_febf3b22 = application_status;
  if (bVar1) {
    lower_status = '\x01';
  }
  DAT_febf3b23 = lower_status;
  if (bVar1) {
    cVar4 = '\0';
  }
  DAT_febf3b21 = cVar4;
  DAT_febf3b24 = uStack_2d;
  return uVar2;
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



/* WARNING: Inlined function: f33_diag_routine_local_dispatch_enabled */

uint FUN_0008b880(void)

{
  uint uVar1;
  uchar lower_status;
  uchar application_status;
  uint uVar2;
  uchar uVar3;
  undefined1 uStack_1d;
  undefined1 auStack_1c [8];
  
  application_status = DAT_febf3b31;
  uStack_1d = DAT_febf3b33;
  if (DAT_febf3b30 == '\0') {
    uVar2 = 0;
    do {
      uVar1 = uVar2 + 1;
      auStack_1c[uVar2] = 0;
      uVar2 = uVar1;
    } while (uVar1 < 8);
    lower_status = ((void)((int)0x88101030), (void)(2), (void)(0), (void)(auStack_1c), (void)(&uStack_1d), f33_return_const_0_8b10c());
  }
  else {
    if (DAT_febf3b30 != '\x01') {
      return 0;
    }
    lower_status = DAT_febf3b32;
    if (DAT_febf3b32 == '\x02') {
      lower_status = ((void)(5), (void)(2), f33_return_const_0_8b110());
    }
    if (application_status != '\x02') goto LAB_0008b900;
  }
  application_status = ((void)(uStack_1d), f33_return_const_0_8b854());
LAB_0008b900:
  uVar3 = '\x01';
  uVar2 = f33_merge_two_diagnostic_statuses(application_status,lower_status,'\0','\x02');
  if ((uVar2 != 2) && (application_status = uVar3, lower_status = uVar3, uVar2 != 0)) {
    uVar3 = '\0';
  }
  DAT_febf3b31 = application_status;
  DAT_febf3b32 = lower_status;
  DAT_febf3b30 = uVar3;
  DAT_febf3b33 = uStack_1d;
  return uVar2;
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



/* WARNING: Inlined function: f33_diag_routine_local_dispatch_enabled */
/* WARNING: Removing unreachable block (ram,0x0008b9ba) */

void FUN_0008b950(undefined4 param_1,ushort param_2)

{
  uint uVar1;
  undefined1 uVar2;
  undefined1 uVar3;
  uchar lower_status;
  uint uVar4;
  char cVar5;
  uchar application_status;
  undefined1 uStack_31;
  undefined1 auStack_30 [12];
  
  uVar3 = DAT_febf3b35;
  uVar2 = DAT_febf3b34;
  application_status = DAT_febf3b31;
  cVar5 = DAT_febf3b30;
  uStack_31 = DAT_febf3b33;
  uVar4 = 0;
  do {
    uVar1 = uVar4 + 1;
    auStack_30[uVar4] = 0;
    uVar4 = uVar1;
  } while (uVar1 < 8);
  if (DAT_febf3b30 == '\x01') {
    cVar5 = '\x02';
    auStack_30[0] = (undefined1)(param_2 >> 8);
    auStack_30[1] = (undefined1)param_2;
    lower_status = ((void)((int)0x88101031), (void)(2), (void)(2), (void)(auStack_30), (void)(&uStack_31), f33_return_const_0_8b10c());
  }
  else {
    if (DAT_febf3b30 != '\x02') {
      application_status = '\x01';
      lower_status = '\x01';
      goto LAB_0008b9f4;
    }
    lower_status = DAT_febf3b32;
    if (DAT_febf3b32 == '\x02') {
      lower_status = ((void)(5), (void)(2), f33_return_const_0_8b110());
    }
    if (application_status != '\x02') goto LAB_0008b9f4;
  }
  uVar4 = f33_crypto_bank_read_direct_result(((undefined *)camry_host_ptr(0xfebf3b56u)),param_2);
  application_status = (uchar)uVar4;
LAB_0008b9f4:
  uVar4 = f33_merge_two_diagnostic_statuses(application_status,lower_status,'\0','\x02');
  if (uVar4 != 2) {
    application_status = '\x01';
    lower_status = '\x01';
    cVar5 = '\0';
    FUN_0008b930(param_1, camry_host_addr(((undefined *)camry_host_ptr(0xfebf3b56u))), param_2);
  }
  DAT_febf3b31 = application_status;
  DAT_febf3b32 = lower_status;
  DAT_febf3b30 = cVar5;
  DAT_febf3b34 = uVar2;
  DAT_febf3b35 = uVar3;
  DAT_febf3b33 = uStack_31;
  return;
}



/* WARNING: Inlined function: f33_diag_routine_local_dispatch_enabled */

uint FUN_0008ba5e(void)

{
  uint uVar1;
  uchar lower_status;
  uchar application_status;
  uint uVar2;
  uchar uVar3;
  undefined1 uStack_1d;
  undefined1 auStack_1c [8];
  
  application_status = DAT_febf3b31;
  uStack_1d = DAT_febf3b33;
  if (DAT_febf3b30 == '\0') {
    uVar2 = 0;
    do {
      uVar1 = uVar2 + 1;
      auStack_1c[uVar2] = 0;
      uVar2 = uVar1;
    } while (uVar1 < 8);
    lower_status = ((void)((int)0x88101010), (void)(2), (void)(7), (void)(auStack_1c), (void)(&uStack_1d), f33_return_const_0_8b10c());
  }
  else {
    if (DAT_febf3b30 != '\x01') {
      return 0;
    }
    lower_status = DAT_febf3b32;
    if (DAT_febf3b32 == '\x02') {
      lower_status = ((void)(5), (void)(2), f33_return_const_0_8b110());
    }
    if (application_status != '\x02') goto LAB_0008bade;
  }
  application_status = ((void)(uStack_1d), f33_return_const_0_8b854());
LAB_0008bade:
  uVar3 = '\x01';
  uVar2 = f33_merge_two_diagnostic_statuses(application_status,lower_status,'\0','\x02');
  if ((uVar2 != 2) && (application_status = uVar3, lower_status = uVar3, uVar2 != 0)) {
    uVar3 = '\0';
  }
  DAT_febf3b31 = application_status;
  DAT_febf3b32 = lower_status;
  DAT_febf3b30 = uVar3;
  DAT_febf3b33 = uStack_1d;
  return uVar2;
}



/* WARNING: Inlined function: f33_diag_routine_local_dispatch_enabled */
/* WARNING: Removing unreachable block (ram,0x0008bbc2) */

void FUN_0008bb0e(uchar *param_1,uint param_2,int param_3,uint param_4)

{
  uint uVar1;
  undefined1 uVar2;
  undefined1 uVar3;
  uint uVar4;
  uchar lower_status;
  char cVar5;
  uchar application_status;
  undefined1 uStack_2d;
  
  uVar3 = DAT_febf3b35;
  uVar2 = DAT_febf3b34;
  lower_status = DAT_febf3b32;
  application_status = DAT_febf3b31;
  cVar5 = DAT_febf3b30;
  param_2 = param_2 & 0xffff;
  param_4 = param_4 & 0xffff;
  uStack_2d = DAT_febf3b33;
  if (0x31 < param_4) {
    param_4 = 0x31;
  }
  if (0x40 < param_2) {
    param_2 = 0x40;
  }
  uVar4 = 0;
  do {
    uVar1 = uVar4 + 1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebf3b87u + (uint32_t)(uVar4) * 1u)))) = 0;
    uVar4 = uVar1;
  } while (uVar1 < 0x44);
  if (cVar5 == '\x01') {
    DAT_febf3b87 = (undefined1)(param_2 >> 8);
    DAT_febf3b88 = (undefined1)param_2;
    cVar5 = '\x02';
    for (uVar4 = 0; uVar4 < param_2; uVar4 = uVar4 + 1 & 0xffff) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebf3b89u + (uint32_t)(uVar4) * 1u)))) = param_1[uVar4];
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebf3b89u + (uint32_t)(param_2) * 1u)))) = (char)(param_4 >> 8);
    (*((char *)camry_host_ptr((uint32_t)(param_2 + 0xfebf3b8a)))) = (char)param_4;
    lower_status = ((void)((int)0x88101011), (void)(2), (void)(0x44), (void)(((undefined *)camry_host_ptr(0xfebf3b87u))), (void)(&uStack_2d), f33_return_const_0_8b10c());
  }
  else {
    if (cVar5 != '\x02') {
      application_status = '\x01';
      lower_status = '\x01';
      goto LAB_0008bc00;
    }
    if (lower_status == '\x02') {
      lower_status = ((void)(5), (void)(2), f33_return_const_0_8b110());
    }
    if (application_status != '\x02') goto LAB_0008bc00;
  }
  uVar4 = f33_crypto_bank_stage_direct_request
                    (param_1,(ushort)param_2,((undefined *)camry_host_ptr(0xfebf3b56u)),(ushort)param_4);
  application_status = (uchar)uVar4;
LAB_0008bc00:
  uVar4 = f33_merge_two_diagnostic_statuses(application_status,lower_status,'\0','\x02');
  if (uVar4 != 2) {
    for (uVar4 = 0; uVar4 < param_4; uVar4 = uVar4 + 1 & 0xffff) {
      (*((undefined1 *)camry_host_ptr((uint32_t)(uVar4 + param_3)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebf3b56u + (uint32_t)(uVar4) * 1u))));
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebf3b56u + (uint32_t)(uVar4) * 1u)))) = 0;
    }
    application_status = '\x01';
    lower_status = '\x01';
    cVar5 = '\0';
  }
  DAT_febf3b31 = application_status;
  DAT_febf3b32 = lower_status;
  DAT_febf3b30 = cVar5;
  DAT_febf3b34 = uVar2;
  DAT_febf3b35 = uVar3;
  DAT_febf3b33 = uStack_2d;
  return;
}



/* WARNING: Inlined function: f33_diag_routine_local_dispatch_enabled */
/* Stages7bytes sideevent88000010,selectsprecondition via8E562,persists3B30..33;pendingstatus2
   retained. */

uint f33_diag_routine_begin_admission
               (ushort rid,uchar control_type,ushort *callback_index,uchar *encoded_input,
               ushort input_length)

{
  uint uVar1;
  uchar lower_status;
  uchar uVar2;
  uchar application_status;
  undefined1 uStack_2d;
  uchar auStack_2c [8];
  
  application_status = DAT_febf3b31;
  uStack_2d = DAT_febf3b33;
  if (DAT_febf3b30 == '\0') {
    uVar1 = 0;
    do {
      auStack_2c[uVar1] = '\0';
      uVar1 = uVar1 + 1;
    } while (uVar1 < 8);
    auStack_2c[0] = (uchar)(rid >> 8);
    auStack_2c[3] = *encoded_input;
    auStack_2c[1] = (uchar)rid;
    auStack_2c[4] = encoded_input[1];
    auStack_2c[6] = (uchar)input_length;
    auStack_2c[5] = (uchar)(input_length >> 8);
    auStack_2c[2] = control_type;
    lower_status = ((void)((int)0x88000010), (void)(2), (void)(7), (void)(auStack_2c), (void)(&uStack_2d), f33_return_const_0_8b10c());
  }
  else {
    if (DAT_febf3b30 != '\x01') {
      return 0;
    }
    lower_status = DAT_febf3b32;
    if (DAT_febf3b32 == '\x02') {
      lower_status = ((void)(5), (void)(2), f33_return_const_0_8b110());
    }
    if (application_status != '\x02') goto LAB_0008bd42;
  }
  uVar1 = f33_diag_routine_select_precondition
                    (callback_index,rid,control_type,encoded_input,input_length);
  application_status = (uchar)uVar1;
LAB_0008bd42:
  uVar2 = '\x01';
  uVar1 = f33_merge_two_diagnostic_statuses(application_status,lower_status,'\0','\x02');
  if ((uVar1 != 2) && (application_status = uVar2, lower_status = uVar2, uVar1 != 0)) {
    uVar2 = '\0';
  }
  DAT_febf3b31 = application_status;
  DAT_febf3b32 = lower_status;
  DAT_febf3b30 = uVar2;
  DAT_febf3b33 = uStack_2d;
  return uVar1;
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



/* WARNING: Inlined function: f33_diag_routine_local_dispatch_enabled */
/* WARNING: Removing unreachable block (ram,0x0008be54) */
/* Sideevent88000011,8E5BCcall8BE1A/8BE8E,captures32maxoutputorresultbyte,merges8E602,clearsstateonterminal.
    */

uint f33_diag_routine_run_action_phase
               (uchar control_type,ushort callback_index,uchar *encoded_input,ushort input_length,
               uchar *output,ushort *output_length)

{
  uint uVar1;
  uint uVar2;
  uchar lower_status;
  uchar uVar3;
  uchar uVar4;
  char cVar5;
  uint uVar6;
  uint uVar7;
  undefined2 uVar8;
  uint uVar9;
  undefined1 uStack_38;
  undefined1 uStack_37;
  ushort uStack_36;
  uchar auStack_34 [8];
  
  uVar4 = DAT_febf3b34;
  cVar5 = DAT_febf3b30;
  uVar9 = (uint)DAT_febf3b2e;
  uVar6 = (uint)DAT_febf3b32;
  uVar7 = (uint)DAT_febf3b31;
  uStack_38 = DAT_febf3b33;
  uStack_37 = DAT_febf3b35;
  uVar2 = 0;
  do {
    uVar1 = uVar2 + 1;
    auStack_34[uVar2] = '\0';
    uVar2 = uVar1;
  } while (uVar1 < 8);
  uStack_36 = callback_index;
  if (DAT_febf3b30 == '\x01') {
    auStack_34[1] = *encoded_input;
    cVar5 = '\x02';
    auStack_34[4] = (uchar)input_length;
    auStack_34[2] = encoded_input[1];
    auStack_34[3] = (uchar)(input_length >> 8);
    auStack_34[0] = control_type;
    uVar6 = ((void)((int)0x88000011), (void)(2), (void)(5), (void)(auStack_34), (void)(&uStack_38), f33_return_const_0_8b10c());
    uVar7 = f33_diag_routine_dispatch_action
                      (uStack_36,control_type,encoded_input,input_length,output,output_length);
    if (uVar7 == 0) {
      if (control_type == '\x03') {
LAB_0008be9c:
        uVar4 = *output;
      }
      else {
        uVar9 = (uint)*output_length;
        if (0x20 < uVar9) {
          uVar9 = 0x20;
        }
        for (uVar2 = 0; uVar2 < uVar9; uVar2 = uVar2 + 1 & 0xffff) {
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebf3b36u + (uint32_t)(uVar2) * 1u)))) = output[uVar2];
        }
      }
    }
  }
  else {
    if (DAT_febf3b30 != '\x02') {
      uVar6 = 1;
      uVar3 = '\x01';
      goto LAB_0008beae;
    }
    if (uVar6 == 2) {
      uVar6 = ((void)(5), (void)(2), f33_return_const_0_8b110());
    }
    if ((uVar7 == 2) &&
       (uVar7 = f33_diag_routine_dispatch_action
                          (uStack_36,control_type,encoded_input,input_length,output,output_length),
       uVar7 == 0)) {
      if (control_type == '\x03') goto LAB_0008be9c;
      uVar9 = (uint)*output_length;
      if (0x20 < uVar9) {
        uVar9 = 0x20;
      }
      for (uVar2 = 0; uVar2 < uVar9; uVar2 = uVar2 + 1 & 0xffff) {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebf3b36u + (uint32_t)(uVar2) * 1u)))) = output[uVar2];
      }
    }
  }
  uVar3 = (uchar)uVar7;
  if (uVar6 == 0) {
    uStack_37 = f33_return_const_2_8bd72();
  }
LAB_0008beae:
  uVar8 = (undefined2)uVar9;
  lower_status = (uchar)uVar6;
  uVar2 = f33_merge_two_diagnostic_statuses(uVar3,lower_status,'\0','\x02');
  if (uVar2 != 2) {
    if (control_type == '\x03') {
      uVar3 = ((void)(uStack_37), FUN_0008bd76(uVar4));
      *output = uVar3;
    }
    else {
      if (0x20 < uVar9) {
        uVar9 = 0x20;
      }
      for (uVar6 = 0; uVar6 < uVar9; uVar6 = uVar6 + 1 & 0xffff) {
        output[uVar6] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebf3b36u + (uint32_t)(uVar6) * 1u))));
      }
      *output_length = (ushort)uVar9;
    }
    uVar3 = '\x01';
    cVar5 = '\0';
    lower_status = '\x01';
    uVar8 = 0;
  }
  DAT_febf3b31 = uVar3;
  DAT_febf3b32 = lower_status;
  DAT_febf3b30 = cVar5;
  DAT_febf3b35 = uStack_37;
  DAT_febf3b34 = uVar4;
  DAT_febf3b2e = uVar8;
  DAT_febf3b33 = uStack_38;
  return uVar2;
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


