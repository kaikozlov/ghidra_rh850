#include "common.h"


/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_5423e(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_54240(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_54242(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_54486(void)

{
  return;
}



void FUN_0005450e(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint saved_mask;
  uint auStack_44 [9];
  undefined2 auStack_20 [10];
  
  saved_mask = f33_priority_mask_enter(0xff00);
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -0x11;
    (*((undefined2 *)camry_host_ptr((uint32_t)((int)camry_host_addr(auStack_44) + iVar3 * 2)))) = *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe860au)) + iVar3 * 2);
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -9;
    auStack_20[iVar3] = *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe862eu)) + iVar3 * 2);
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  f33_nvm_set_record(4,auStack_44);
  f33_priority_mask_restore(saved_mask);
  return;
}



void FUN_00054566(void)

{
  byte bVar1;
  byte bVar2;
  undefined1 uVar3;
  uint32_t puVar4;
  uint uVar5;
  undefined1 uVar6;
  char cVar7;
  
  uVar6 = DAT_febe8608;
  bVar2 = DAT_febe8607;
  cVar7 = DAT_febe8606;
  puVar4 = 0xfebeb800u;
  if (((DAT_febee821 == 'Z') || ((DAT_febe8607 >> 2 & 1) != 0)) && (DAT_febe8607 != 0)) {
    bVar1 = ~DAT_febe8607;
    puVar4 = 0xfebeb800u;
    uVar5 = f33_priority_mask_enter(0xff00);
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x31f9))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x31f9))))) & bVar1;
    f33_priority_mask_restore(uVar5);
    FUN_0005450e();
    if ((bVar2 >> 2 & 1) == 0) goto LAB_000545ae;
    cVar7 = '\x01';
  }
  else {
LAB_000545ae:
    if (cVar7 == '\0') goto LAB_000545d2;
  }
  uVar5 = f33_nvm_get_record_status(4);
  uVar3 = 0;
  if (((uVar5 & 0xf0) == 0x10) || (uVar3 = 0x55, (uVar5 & 0xf0) == 0x30)) {
    uVar6 = uVar3;
    cVar7 = '\0';
  }
LAB_000545d2:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x31f8))))) = uVar6;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x31fa))))) = cVar7;
  return;
}



void FUN_000545de(uint param_1)

{
  uint32_t puVar1;
  uint saved_mask;
  
  puVar1 = 0xfebeb800u;
  param_1 = param_1 & 0xff;
  if (param_1 < 0x12) {
    saved_mask = f33_priority_mask_enter(0xff00);
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe85f4u + (uint32_t)(param_1) * 1u)))) == '\0') {
      if (*(short *)(((undefined *)camry_host_ptr(0xfebe860au)) + param_1 * 2) != -1) {
        *(short *)(((undefined *)camry_host_ptr(0xfebe860au)) + param_1 * 2) = *(short *)(((undefined *)camry_host_ptr(0xfebe860au)) + param_1 * 2) + 1;
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x31f9))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x31f9))))) | 2;
      }
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe85f4u + (uint32_t)(param_1) * 1u)))) = 'Z';
    f33_priority_mask_restore(saved_mask);
  }
  return;
}



void FUN_00054632(uint param_1,undefined2 param_2)

{
  uint32_t puVar1;
  uint saved_mask;
  
  puVar1 = 0xfebeb800u;
  if ((param_1 & 0xff) < 10) {
    saved_mask = f33_priority_mask_enter(0xff00);
    *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe862eu)) + (param_1 & 0xff) * 2) = param_2;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x31f9))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x31f9))))) | 2;
    f33_priority_mask_restore(saved_mask);
  }
  return;
}



void FUN_00054662(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint32_t puVar4;
  uint saved_mask;
  
  puVar4 = 0xfebeb800u;
  DAT_febe8608 = 0xaa;
  saved_mask = f33_priority_mask_enter(0xff00);
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe860au)) + iVar3 * 2) = 0;
    iVar1 = iVar3 + -0x11;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x31f9))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x31f9))))) | 4;
  f33_priority_mask_restore(saved_mask);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x31f8))))) = 0xa5;
  return;
}



void FUN_000546a2(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint32_t puVar4;
  uint saved_mask;
  
  puVar4 = 0xfebeb800u;
  DAT_febe8608 = 0xaa;
  saved_mask = f33_priority_mask_enter(0xff00);
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe860au)) + iVar3 * 2) = 0;
    iVar1 = iVar3 + -0x11;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe862eu)) + iVar3 * 2) = 0;
    iVar1 = iVar3 + -9;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x31f9))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x31f9))))) | 4;
  f33_priority_mask_restore(saved_mask);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x31f8))))) = 0xa5;
  return;
}



undefined2 FUN_000546f2(uint param_1)

{
  if ((param_1 & 0xff) < 0x12) {
    return *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe860au)) + (param_1 & 0xff) * 2);
  }
  return 0;
}



undefined2 FUN_0005470c(uint param_1)

{
  if ((param_1 & 0xff) < 10) {
    return *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe862eu)) + (param_1 & 0xff) * 2);
  }
  return 0;
}



void FUN_00054724(uint param_1)

{
  uint32_t puVar1;
  uint saved_mask;
  
  puVar1 = 0xfebeb800u;
  saved_mask = f33_priority_mask_enter(0xff00);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)((param_1 & 0xff) - 0x320c))))) = 0;
  f33_priority_mask_restore(saved_mask);
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_54744(void)

{
  return;
}



void FUN_00054818(byte param_1,undefined1 *param_2)

{
  int iVar1;
  ushort uVar2;
  undefined1 uVar3;
  undefined2 uVar4;
  undefined4 uVar5;
  undefined1 uVar6;
  ushort uVar7;
  int iVar8;
  int iVar9;
  char cVar10;
  int iVar11;
  
  uVar5 = DAT_febee90c;
  uVar4 = DAT_febee896;
  uVar3 = DAT_febee815;
  if (DAT_febee920 == 0x55aaaa55) {
    iVar9 = 4;
    uVar7 = DAT_febee890;
  }
  else {
    uVar7 = (ushort)DAT_febee811;
    iVar9 = 5;
  }
  if (param_1 < 2) goto LAB_00054876;
  if (param_1 == 2) {
    iVar11 = 0;
    iVar9 = 1;
    uVar7 = 0;
    goto LAB_000548b8;
  }
  if (param_1 < 4) {
    iVar9 = 1;
    iVar11 = iVar9;
LAB_0005487c:
    uVar7 = (ushort)iVar9;
  }
  else {
    uVar2 = DAT_febe66ba;
    if (param_1 == 4) {
      iVar9 = 2;
      iVar11 = iVar9;
    }
    else {
      if (param_1 < 9) {
LAB_00054876:
        iVar9 = 0;
        iVar11 = 0xff;
        goto LAB_0005487c;
      }
      if (param_1 == 9) {
        iVar9 = 3;
        iVar11 = iVar9;
      }
      else {
        if (param_1 < 0xb) {
          iVar11 = 5;
          iVar9 = 6;
          uVar7 = (ushort)((uint)DAT_febee892 * 100 >> 7);
          goto LAB_000548b8;
        }
        if (param_1 != 0xb) {
          if (param_1 == 0xf) {
            iVar11 = 4;
            goto LAB_000548b8;
          }
          goto LAB_00054876;
        }
        iVar9 = 8;
        iVar11 = 7;
        uVar2 = DAT_febe66b8;
      }
    }
    uVar7 = (ushort)((uint)uVar2 * 10 >> 8);
  }
LAB_000548b8:
  if (((DAT_febee825 == 'Z') || (DAT_febee827 == 'Z')) || (DAT_febee824 == 'Z')) {
    uVar6 = 2;
  }
  else {
    uVar6 = 1;
  }
  if (iVar11 != 0xff) {
    iVar8 = 2;
    do {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe8662u + (uint32_t)(iVar8) * 1u)))) = (*((undefined1 *)camry_host_ptr((uint32_t)(iVar8 + -0x141799f))));
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe8665u + (uint32_t)(iVar8) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe8664u + (uint32_t)(iVar8) * 1u))));
      (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe866cu + (uint32_t)(iVar8) * 2u)))) = *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe866au)) + iVar8 * 2);
      (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebe8678u + (uint32_t)(iVar8) * 4u)))) = *(undefined4 *)(((undefined *)camry_host_ptr(0xfebe8674u)) + iVar8 * 2);
      (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe8672u + (uint32_t)(iVar8) * 2u)))) = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe8670u + (uint32_t)(iVar8) * 2u))));
      iVar1 = iVar8 + -1;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe8668u + (uint32_t)(iVar8) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe8667u + (uint32_t)(iVar8) * 1u))));
      iVar8 = iVar1;
    } while (0 < iVar1);
    cVar10 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe8644u + (uint32_t)(iVar11) * 1u))));
    if (cVar10 != -1) {
      cVar10 = cVar10 + '\x01';
    }
    DAT_febe8672 = uVar7;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe8644u + (uint32_t)(iVar11) * 1u)))) = cVar10;
    DAT_febe8662 = (undefined1)iVar9;
    DAT_febe8665 = uVar3;
    DAT_febe866c = uVar4;
    DAT_febe8678 = uVar5;
    DAT_febe8668 = uVar6;
    *param_2 = 0x5a;
  }
  return;
}



void FUN_00054950(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  undefined1 uVar4;
  int iVar5;
  uint local_34 [3];
  undefined1 auStack_28 [2];
  undefined2 uStack_26;
  undefined4 uStack_24;
  undefined2 uStack_20;
  undefined1 auStack_1e [26];
  
  iVar5 = 0;
  do {
    iVar2 = iVar5 + 1;
    iVar1 = iVar5 + -0xb;
    (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(local_34) + iVar5)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe8644u + (uint32_t)(iVar5) * 1u))));
    iVar5 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  iVar5 = 0;
  do {
    iVar3 = iVar5 * 0xc;
    auStack_28[iVar3] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe8662u + (uint32_t)(iVar5) * 1u))));
    auStack_28[iVar3 + 1] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe8665u + (uint32_t)(iVar5) * 1u))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(auStack_28 + iVar3 + 2)))) = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe866cu + (uint32_t)(iVar5) * 2u))));
    (*((undefined4 *)camry_host_ptr((uint32_t)(auStack_28 + iVar3 + 4)))) = (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebe8678u + (uint32_t)(iVar5) * 4u))));
    (&uStack_20)[iVar5 * 6] = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe8672u + (uint32_t)(iVar5) * 2u))));
    uVar4 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe8668u + (uint32_t)(iVar5) * 1u))));
    iVar2 = iVar5 + 1;
    auStack_1e[iVar3 + 1] = 0;
    iVar1 = iVar5 + -2;
    auStack_1e[iVar3] = uVar4;
    iVar5 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  f33_nvm_set_record(0xe,local_34);
  return;
}



void FUN_000549c8(void)

{
  char cVar1;
  undefined8 uVar2;
  uint uVar3;
  char cStack_15;
  
  uVar2 = 0xfebeb800;
  if (DAT_febee820 == 'Z') {
    cStack_15 = '\0';
    uVar3 = 0;
    do {
      cVar1 = (*((char *)camry_host_ptr((uint32_t)(uVar3 + (int)uVar2 + -0x320c))));
      if ((cVar1 == 'Z') && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe8650u + (uint32_t)(uVar3) * 1u)))) == '\0')) {
        FUN_00054818(uVar3,&cStack_15);
      }
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe8650u + (uint32_t)(uVar3) * 1u)))) = cVar1;
      uVar3 = uVar3 + 1;
    } while (uVar3 < 0x12);
    if (cStack_15 == 'Z') {
      FUN_00054950();
    }
  }
  return;
}



void FUN_00054a24(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  uint local_34 [3];
  undefined1 auStack_28 [2];
  undefined2 uStack_26;
  undefined4 uStack_24;
  undefined2 uStack_20;
  undefined1 auStack_1e [26];
  
  iVar4 = 0;
  do {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe8644u + (uint32_t)(iVar4) * 1u)))) = 0;
    (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(local_34) + iVar4)))) = 0;
    iVar2 = iVar4 + 1;
    iVar1 = iVar4 + -0xb;
    iVar4 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  iVar4 = 0;
  do {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe8662u + (uint32_t)(iVar4) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe8665u + (uint32_t)(iVar4) * 1u)))) = 0;
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe866cu + (uint32_t)(iVar4) * 2u)))) = 0;
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe8672u + (uint32_t)(iVar4) * 2u)))) = 0;
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebe8678u + (uint32_t)(iVar4) * 4u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe8668u + (uint32_t)(iVar4) * 1u)))) = 0;
    iVar3 = iVar4 * 0xc;
    iVar2 = iVar4 + 1;
    iVar1 = iVar4 + -2;
    auStack_28[iVar3] = 0;
    auStack_28[iVar3 + 1] = 0;
    (*((undefined2 *)camry_host_ptr((uint32_t)(auStack_28 + iVar3 + 2)))) = 0;
    (*((undefined4 *)camry_host_ptr((uint32_t)(auStack_28 + iVar3 + 4)))) = 0;
    (&uStack_20)[iVar4 * 6] = 0;
    auStack_1e[iVar3] = 0;
    auStack_1e[iVar3 + 1] = 0;
    iVar4 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  f33_nvm_set_record(0xe,local_34);
  return;
}



void FUN_00054a90(int param_1,int param_2)

{
  int iVar1;
  uint uVar2;
  
  uVar2 = 0;
  do {
    iVar1 = uVar2 * 4;
    uVar2 = uVar2 + 1;
    (*((undefined4 *)camry_host_ptr((uint32_t)(iVar1 + param_1)))) = (*((undefined4 *)camry_host_ptr((uint32_t)(iVar1 + param_2))));
  } while (uVar2 < 0x18);
  return;
}



void FUN_00054aac(int param_1,int param_2)

{
  int iVar1;
  uint uVar2;
  
  uVar2 = 0;
  do {
    iVar1 = uVar2 * 4;
    uVar2 = uVar2 + 1;
    (*((undefined4 *)camry_host_ptr((uint32_t)(iVar1 + param_1)))) = (*((undefined4 *)camry_host_ptr((uint32_t)(iVar1 + param_2))));
  } while (uVar2 < 8);
  return;
}



undefined4 FUN_00054bec(char param_1)

{
  undefined4 uVar1;
  
  uVar1 = 0x20;
  if (param_1 == '\0') {
    uVar1 = 0x14;
  }
  if (param_1 == '\x03') {
    uVar1 = 0x15;
  }
  if (param_1 == '\x02') {
    uVar1 = 0x17;
  }
  return uVar1;
}



undefined4 FUN_00054df2(undefined1 param_1)

{
  uint uVar1;
  undefined4 uVar2;
  
  uVar1 = FUN_00054bec(param_1);
  if (uVar1 == 0x20) {
    uVar2 = 0;
  }
  else {
    uVar1 = f33_nvm_get_record_status(uVar1);
    if ((uVar1 & 0xf0) == 0x20) {
      uVar2 = 1;
    }
    else if ((uVar1 & 0xf0) == 0x10) {
      uVar2 = 2;
    }
    else {
      uVar2 = 3;
    }
  }
  return uVar2;
}



void FUN_00054e28(void)

{
  char cVar1;
  bool bVar2;
  undefined *puVar3;
  uint uVar5;
  uint uVar6;
  int iVar7;
  undefined1 uVar8;
  int iVar9;
  char cVar10;
  char cVar11;
  char cVar12;
  uint uVar13;
  char local_28 [4];
  undefined8 uVar4;
  
  cVar10 = DAT_febe89d7;
  cVar11 = DAT_febe89cb;
  cVar12 = DAT_febe89ca;
  uVar8 = DAT_febe89c4;
  uVar4 = 0xfebeb800;
  puVar3 = ((undefined *)camry_host_ptr(0xfebeb800u));
  bVar2 = false;
  uVar13 = 0;
  do {
    cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe89ccu + (uint32_t)(uVar13) * 1u))));
    local_28[uVar13] = cVar1;
    if (cVar1 != '\0') {
      bVar2 = true;
    }
    uVar13 = uVar13 + 1;
  } while (uVar13 < 4);
  if ((((DAT_febe89ca != '\0') || (DAT_febe89cb != '\0')) || (DAT_febe89d7 != '\0')) || (bVar2)) {
    uVar13 = f33_nvm_get_record_status(0x12);
    uVar5 = f33_nvm_get_record_status(0x13);
    uVar6 = f33_nvm_get_record_status(0x11);
    if ((cVar12 == '\x01') && ((uVar13 & 0xf0) != 0x20)) {
      if ((uVar13 & 0xf0) == 0x10) {
        cVar12 = '\x02';
      }
      else {
        cVar12 = '\x03';
      }
    }
    if ((cVar11 == '\x01') && ((uVar5 & 0xf0) != 0x20)) {
      if ((uVar5 & 0xf0) == 0x10) {
        cVar11 = '\x02';
      }
      else {
        cVar11 = '\x03';
      }
    }
    if ((cVar10 == '\x01') && ((uVar6 & 0xf0) != 0x20)) {
      if ((uVar6 & 0xf0) == 0x10) {
        cVar10 = '\x02';
      }
      else {
        cVar10 = '\x03';
      }
    }
    iVar9 = 0;
    uVar13 = 0;
    do {
      if (local_28[uVar13] == '\x01') {
        iVar7 = FUN_00054df2(uVar13);
        local_28[uVar13] = (char)iVar7;
        if (iVar7 == 1) {
          iVar9 = 1;
        }
      }
      puVar3 = ((undefined *)camry_host_ptr((uint32_t)(uVar4)));
      uVar13 = uVar13 + 1;
    } while (uVar13 < 4);
    if (iVar9 != 1) {
      uVar13 = 0;
      do {
        if (local_28[uVar13] == '\x03') {
          iVar9 = 3;
        }
        uVar13 = uVar13 + 1;
      } while (uVar13 < 4);
    }
    DAT_febe89d7 = cVar10;
    DAT_febe89cb = cVar11;
    DAT_febe89ca = cVar12;
    if ((((cVar12 != '\x01') && (cVar11 != '\x01')) && (cVar10 != '\x01')) && (iVar9 != 1)) {
      if (((cVar12 == '\x03') || (cVar11 == '\x03')) || ((cVar10 == '\x03' || (iVar9 == 3)))) {
        uVar8 = 0x55;
      }
      else {
        uVar8 = 0;
      }
      DAT_febe89ca = '\0';
      DAT_febe89cb = '\0';
      DAT_febe89d7 = '\0';
      uVar13 = 0;
      do {
        local_28[uVar13] = '\0';
        uVar13 = uVar13 + 1;
      } while (uVar13 < 4);
    }
  }
  uVar13 = 0;
  do {
    uVar5 = uVar13 + 1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe89ccu + (uint32_t)(uVar13) * 1u)))) = local_28[uVar13];
    uVar13 = uVar5;
  } while (uVar5 < 4);
  puVar3[-0x2e3c] = uVar8;
  return;
}



undefined4 FUN_00054f6e(char param_1,undefined2 *param_2,undefined2 *param_3)

{
  undefined2 uVar1;
  undefined4 uVar2;
  undefined2 uVar3;
  
  if (DAT_febe89d8 == DAT_febe86ca) {
    if (param_1 == '\x02') {
LAB_00054f92:
      uVar1 = 0x12;
      uVar3 = 0x13;
      uVar2 = 1;
      goto LAB_00054f9c;
    }
  }
  else if (param_1 != '\x02') goto LAB_00054f92;
  uVar1 = 0x13;
  uVar3 = 0x12;
  uVar2 = 2;
LAB_00054f9c:
  *param_2 = uVar1;
  *param_3 = uVar3;
  return uVar2;
}



int FUN_00054fa4(char param_1)

{
  uint uVar1;
  uint32_t puVar2;
  uint uVar3;
  int iVar4;
  uint uVar5;
  
  uVar1 = DAT_febe89e4;
  puVar2 = 0xfebeb800u;
  uVar3 = 0;
  uVar5 = 0;
  if (param_1 == '\0') {
    puVar2 = 0xfebeb800u;
    uVar3 = FUN_0006a130();
    uVar5 = uVar1;
  }
  if (param_1 == '\x02') {
    uVar3 = (*((uint *)camry_host_ptr((uint32_t)(puVar2 + -0x2d04))));
    uVar5 = DAT_febe89ec;
  }
  if (~uVar5 < uVar3) {
    iVar4 = -1;
  }
  else {
    iVar4 = uVar3 + uVar5;
  }
  return iVar4;
}



void FUN_00055040(void)

{
  uint uVar1;
  byte bVar2;
  char cVar3;
  byte bVar4;
  byte bVar5;
  uint uVar6;
  uint32_t puVar7;
  undefined1 uVar8;
  undefined1 uVar9;
  undefined1 uVar10;
  undefined1 uVar11;
  uint uVar12;
  byte local_48 [4];
  undefined1 auStack_44 [4];
  ushort uStack_40;
  ushort uStack_3e;
  uint auStack_3c [4];
  
  uVar9 = DAT_febe89d7;
  bVar5 = DAT_febe89d1;
  bVar4 = DAT_febe89d0;
  uVar10 = DAT_febe89cb;
  uVar11 = DAT_febe89ca;
  cVar3 = DAT_febe89c5;
  puVar7 = 0xfebeb800u;
  uVar6 = 0;
  uVar12 = 0;
  do {
    uVar1 = uVar12 + 1;
    auStack_44[uVar12] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe89ccu + (uint32_t)(uVar12) * 1u))));
    bVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe89d2u + (uint32_t)(uVar12) * 1u))));
    local_48[uVar12] = bVar2;
    uVar6 = uVar6 | bVar2;
    uVar12 = uVar1;
  } while (uVar1 < 4);
  uVar6 = uVar6 | (DAT_febe89d1 | DAT_febe89d0);
  if (((DAT_febee821 == 'Z') || ((uVar6 >> 2 & 1) != 0)) && ((uVar6 & 6) != 0)) {
    uVar8 = FUN_00054f6e(DAT_febe89c5,&uStack_40,&uStack_3e);
    uVar6 = f33_priority_mask_enter(0xff00);
    uVar12 = 0;
    do {
      uVar1 = uVar12 + 1;
      auStack_3c[uVar12] = *(uint *)(((undefined *)camry_host_ptr(0xfebe89f4u)) + uVar12 * 4);
      uVar12 = uVar1;
    } while (uVar1 < 2);
    uVar12 = 0;
    do {
      uVar1 = uVar12 + 1;
      auStack_3c[uVar12 + 2] = *(uint *)(((undefined *)camry_host_ptr(0xfebe89fcu)) + uVar12 * 4);
      uVar12 = uVar1;
    } while (uVar1 < 2);
    f33_nvm_set_record(0x11,auStack_3c);
    if ((bVar4 & 6) != 0) {
      f33_nvm_set_record((uint)uStack_40,((uint *)camry_host_ptr((uint32_t)(puVar7 + -0x317c))));
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(-0x2e3b))))) = uVar8;
    }
    if ((bVar5 & 6) != 0) {
      f33_nvm_set_record((uint)uStack_3e,((uint *)camry_host_ptr((uint32_t)(puVar7 + -0x311c))));
    }
    uVar12 = 0;
    do {
      if (((local_48[uVar12] & 0xe) != 0) && (FUN_00054fda(uVar12), (local_48[uVar12] & 4) != 0)) {
        auStack_44[uVar12] = 1;
      }
      uVar12 = uVar12 + 1;
    } while (uVar12 < 4);
    if ((bVar4 >> 2 & 1) != 0) {
      uVar9 = 1;
      if (cVar3 == '\x02') {
        uVar10 = 1;
      }
      else {
        uVar11 = 1;
      }
    }
    if ((bVar5 >> 2 & 1) != 0) {
      uVar9 = 1;
      if (cVar3 == '\x02') {
        uVar11 = 1;
      }
      else {
        uVar10 = 1;
      }
    }
    DAT_febe89d6 = 0;
    DAT_febe89d0 = DAT_febe89d0 & ~bVar4;
    DAT_febe89d1 = DAT_febe89d1 & ~bVar5;
    uVar12 = 0;
    do {
      uVar1 = uVar12 + 1;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe89d2u + (uint32_t)(uVar12) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe89d2u + (uint32_t)(uVar12) * 1u)))) & ~local_48[uVar12];
      uVar12 = uVar1;
    } while (uVar1 < 4);
    f33_priority_mask_restore(uVar6);
  }
  uVar12 = 0;
  DAT_febe89ca = uVar11;
  DAT_febe89cb = uVar10;
  DAT_febe89d7 = uVar9;
  do {
    uVar6 = uVar12 + 1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe89ccu + (uint32_t)(uVar12) * 1u)))) = auStack_44[uVar12];
    uVar12 = uVar6;
  } while (uVar6 < 4);
  return;
}



void FUN_000551bc(void)

{
  FUN_00054e28();
  FUN_00055040();
  return;
}



void FUN_0005551a(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe89c4 = 0xaa;
  FUN_000553ea();
  FUN_00055492(0);
  FUN_00055492(3);
  FUN_00055492(2);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x2e3c))))) = 0xa5;
  return;
}



void FUN_00055658(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe89c4 = 0xaa;
  FUN_00055548();
  FUN_000555da(0);
  FUN_000555da(3);
  FUN_000555da(2);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x2e3c))))) = 0xa5;
  return;
}



void FUN_0005575e(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe89c4 = 0xaa;
  FUN_00055686();
  FUN_000556f2(0);
  FUN_000556f2(3);
  FUN_000556f2(2);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x2e3c))))) = 0xa5;
  return;
}



undefined4 FUN_0005578c(uint param_1)

{
  undefined4 uVar1;
  
  uVar1 = 0;
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2aacdu + (uint32_t)((param_1 & 0xff) * 4) * 1u)))) == 'Z') ||
     (((uint)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebe8a0cu + (uint32_t)((param_1 & 0xff) >> 5) * 4u)))) >> (param_1 & 0x1f) & 1) == 0)) {
    uVar1 = 0x5a;
  }
  return uVar1;
}



uint FUN_000557c4(int param_1,uint param_2)

{
  uint *puVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  uint auStack_1c [2];
  
  uVar4 = 0;
  if (param_1 != 0) {
    uVar3 = 0;
    do {
      iVar2 = uVar3 * 4;
      puVar1 = auStack_1c + uVar3;
      uVar3 = uVar3 + 1;
      *puVar1 = *(uint *)(((undefined *)camry_host_ptr(0xfebe8a04u)) + iVar2);
    } while (uVar3 < 2);
    uVar3 = 0;
    do {
      if (((auStack_1c[uVar3 >> 5] >> (uVar3 & 0x1f) & 1) != 0) &&
         (*(short *)(((undefined *)camry_host_ptr(0x2ab70u)) + uVar3 * 8) != 0)) {
        FUN_0006a574(*(short *)(((undefined *)camry_host_ptr(0x2ab70u)) + uVar3 * 8), ((undefined1 *)camry_host_ptr((uint32_t)(uVar4 + param_1))));
        uVar4 = uVar4 + 2;
      }
      uVar3 = uVar3 + 1;
    } while (uVar3 < 0x40);
  }
  iVar2 = uVar4 - (param_2 & 0xffff);
  if (iVar2 < 0 == ((int)uVar4 < 0 && -1 < iVar2) && uVar4 != (param_2 & 0xffff)) {
    uVar4 = 0xffffffff;
  }
  return uVar4;
}



uint FUN_00055858(undefined2 param_1,int param_2,uint param_3)

{
  uint32_t puVar1;
  int iVar2;
  uint uVar3;
  
  puVar1 = 0xfebeb800u;
  uVar3 = 0;
  if ((DAT_febe86e6 != 0x1111) && (DAT_febe86e6 != 0x2222)) {
    puVar1 = 0xfebeb800u;
    uVar3 = FUN_00055836(param_1,param_2,((undefined *)camry_host_ptr(0xfebe86e4u)));
  }
  if (((*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x317a)))) != 0x1111) && ((*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x317a)))) != 0x2222)) {
    iVar2 = FUN_00055836(param_1, uVar3 + param_2, ((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x317c))));
    uVar3 = uVar3 + iVar2;
  }
  iVar2 = uVar3 - (param_3 & 0xffff);
  if (iVar2 < 0 == ((int)uVar3 < 0 && -1 < iVar2) && uVar3 != (param_3 & 0xffff)) {
    uVar3 = 0xffffffff;
  }
  return uVar3;
}



/* WARNING: Removing unreachable block (ram,0x00055900) */

uint FUN_000558ae(short param_1,int param_2,uint param_3,ushort param_4)

{
  short *psVar1;
  undefined8 uVar2;
  int iVar3;
  uint uVar4;
  uint uVar5;
  
  uVar2 = 0xfebeb800;
  uVar5 = 0;
  iVar3 = 0;
  if ((param_4 & 0xff) < 4) {
    uVar4 = 0;
    do {
      psVar1 = ((short *)camry_host_ptr((uint32_t)(((short)(param_4 & 0xff) * 5 + uVar4) * 0x20 + (int)uVar2 + -0x30bc)));
      if (((psVar1[2] != 0x1111) && (psVar1[2] != 0x2222)) && (*psVar1 == param_1)) {
        if ((param_3 & 0xffff) < (uVar5 + 2 & 0xffff)) {
          iVar3 = 0x5a;
        }
        else {
          FUN_0006a574(((ushort)psVar1[1] + 4) % 5 + 1, ((undefined1 *)camry_host_ptr((uint32_t)(uVar5 + param_2))));
          uVar5 = uVar5 + 2 & 0xffff;
        }
      }
      uVar4 = uVar4 + 1;
    } while (uVar4 < 5);
    if (iVar3 != 0) {
      uVar5 = 0xffffffff;
    }
  }
  return uVar5;
}



int FUN_0005598c(short param_1,short param_2,int param_3,char param_4)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  int iVar4;
  ushort uVar5;
  undefined1 uVar6;
  ushort uVar7;
  short *psVar8;
  int iVar9;
  ushort uStack_2a;
  
  uVar7 = 0;
  iVar9 = 0;
  uVar5 = 0;
  psVar8 = (short *)((undefined *)camry_host_ptr(0xfebe86e4u));
  if (param_4 == '\0') {
    psVar8 = ((undefined *)camry_host_ptr(0xfebe8684u));
  }
  if ((param_3 != 0) && (iVar3 = camry_host_addr(FUN_00056664(&uStack_2a)), iVar3 != 0)) {
    if ((param_1 == *psVar8) && ((param_2 == psVar8[0x23] || (param_2 == 0)))) {
      uVar2 = 0;
      do {
        if (param_1 == *(short *)(((undefined *)camry_host_ptr(0x2ab70u)) + uVar2 * 8)) {
          uVar5 = *(ushort *)(((undefined *)camry_host_ptr(0x2ab72u)) + uVar2 * 8);
          break;
        }
        uVar2 = uVar2 + 1;
      } while (uVar2 < 0x40);
    }
    if (uVar5 != 0) {
      FUN_0006a574(psVar8[0x23], ((undefined1 *)camry_host_ptr((uint32_t)(param_3))));
      iVar9 = 3;
      for (uVar2 = 0; uVar2 < uStack_2a; uVar2 = uVar2 + 1 & 0xffff) {
        iVar1 = uVar2 * 0x18 + iVar3;
        if ((((*((ushort *)camry_host_ptr((uint32_t)(iVar1 + 0x14)))) & uVar5) != 0) &&
           (iVar4 = FUN_00053190(uVar2,1), iVar4 == 0x5a)) {
          uVar7 = uVar7 + 1;
          FUN_0006a574((*((undefined2 *)camry_host_ptr((uint32_t)(iVar1 + 8)))), ((undefined1 *)camry_host_ptr((uint32_t)(iVar9 + param_3))));
          (*((undefined1 *)camry_host_ptr((uint32_t)(iVar9 + 2 + param_3)))) = (*((undefined1 *)camry_host_ptr((uint32_t)(iVar1 + 0x16))));
          (*(int (*)())*(code **)(iVar1 + 0xc))(param_4,iVar9 + 3 + param_3);
          iVar9 = iVar9 + 3 + (uint)(*((byte *)camry_host_ptr((uint32_t)(iVar1 + 0x16))));
        }
      }
      if (uVar7 < 0x100) {
        uVar6 = (undefined1)uVar7;
      }
      else {
        uVar6 = 0;
      }
      (*((undefined1 *)camry_host_ptr((uint32_t)(param_3 + 2)))) = uVar6;
    }
  }
  return iVar9;
}



uint FUN_00055a76(undefined2 param_1,undefined2 param_2,int param_3,uint param_4)

{
  uint32_t puVar1;
  int iVar2;
  uint uVar3;
  
  puVar1 = 0xfebeb800u;
  uVar3 = 0;
  if ((DAT_febe86e6 != 0x1111) && (DAT_febe86e6 != 0x2222)) {
    puVar1 = 0xfebeb800u;
    uVar3 = FUN_0005598c(param_1,param_2,param_3,1);
  }
  if (((*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x317a)))) != 0x1111) && ((*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x317a)))) != 0x2222)) {
    iVar2 = FUN_0005598c(param_1,param_2,uVar3 + param_3,0);
    uVar3 = uVar3 + iVar2;
  }
  iVar2 = uVar3 - (param_4 & 0xffff);
  if (iVar2 < 0 == ((int)uVar3 < 0 && -1 < iVar2) && uVar3 != (param_4 & 0xffff)) {
    uVar3 = 0xffffffff;
  }
  return uVar3;
}



undefined2 FUN_00055ad0(short param_1)

{
  uint uVar1;
  
  uVar1 = 0;
  do {
    if (param_1 == *(short *)(((undefined *)camry_host_ptr(0x2ab70u)) + uVar1 * 8)) {
      return *(undefined2 *)(((undefined *)camry_host_ptr(0x2ab72u)) + uVar1 * 8);
    }
    uVar1 = uVar1 + 1 & 0xff;
  } while (uVar1 < 0x40);
  return 0;
}



void FUN_00055f2e(char param_1,undefined4 param_2)

{
  undefined4 uVar1;
  undefined2 *puVar2;
  
  puVar2 = (undefined2 *)((undefined *)camry_host_ptr(0xfebe86e4u));
  if (param_1 == '\0') {
    puVar2 = ((undefined *)camry_host_ptr(0xfebe8684u));
  }
  uVar1 = FUN_00053532((int)(short)puVar2[0x11]);
  FUN_0006a5ac(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}



void FUN_00055f52(char param_1,undefined4 param_2)

{
  undefined4 uVar1;
  undefined2 *puVar2;
  
  puVar2 = (undefined2 *)((undefined *)camry_host_ptr(0xfebe86e4u));
  if (param_1 == '\0') {
    puVar2 = ((undefined *)camry_host_ptr(0xfebe8684u));
  }
  uVar1 = 0x7fff;
  if (*(char *)(puVar2 + 0x22) != '\0') {
    uVar1 = FUN_00053532((int)(short)puVar2[0x20]);
  }
  FUN_0006a5ac(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}



void FUN_00055f82(char param_1,undefined4 param_2)

{
  undefined4 uVar1;
  undefined2 *puVar2;
  
  puVar2 = (undefined2 *)((undefined *)camry_host_ptr(0xfebe86e4u));
  if (param_1 == '\0') {
    puVar2 = ((undefined *)camry_host_ptr(0xfebe8684u));
  }
  uVar1 = 0x7fff;
  if ((*((char *)camry_host_ptr((uint32_t)((int)camry_host_addr(puVar2) + 0x45)))) != '\0') {
    uVar1 = FUN_00053532((int)(short)puVar2[0x21]);
  }
  FUN_0006a5ac(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}



void FUN_0005602e(char param_1,undefined4 param_2)

{
  undefined4 uVar1;
  undefined2 *puVar2;
  
  puVar2 = (undefined2 *)((undefined *)camry_host_ptr(0xfebe86e4u));
  if (param_1 == '\0') {
    puVar2 = ((undefined *)camry_host_ptr(0xfebe8684u));
  }
  uVar1 = FUN_00053608((int)(short)puVar2[0x13]);
  FUN_0006a5ac(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}



void FUN_00056052(char param_1,undefined4 param_2)

{
  undefined4 uVar1;
  undefined2 *puVar2;
  
  puVar2 = (undefined2 *)((undefined *)camry_host_ptr(0xfebe86e4u));
  if (param_1 == '\0') {
    puVar2 = ((undefined *)camry_host_ptr(0xfebe8684u));
  }
  uVar1 = FUN_00053608((int)(short)puVar2[0x14]);
  FUN_0006a5ac(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}



void FUN_00056076(char param_1,undefined4 param_2)

{
  undefined4 uVar1;
  undefined2 *puVar2;
  
  puVar2 = (undefined2 *)((undefined *)camry_host_ptr(0xfebe86e4u));
  if (param_1 == '\0') {
    puVar2 = ((undefined *)camry_host_ptr(0xfebe8684u));
  }
  uVar1 = FUN_00053608((int)(short)puVar2[0x15]);
  FUN_0006a5ac(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}



void FUN_0005609a(char param_1,undefined4 param_2)

{
  undefined4 uVar1;
  undefined2 *puVar2;
  
  puVar2 = (undefined2 *)((undefined *)camry_host_ptr(0xfebe86e4u));
  if (param_1 == '\0') {
    puVar2 = ((undefined *)camry_host_ptr(0xfebe8684u));
  }
  uVar1 = FUN_00053608((int)(short)puVar2[0x16]);
  FUN_0006a5ac(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}



void FUN_000560be(char param_1,undefined4 param_2)

{
  undefined4 uVar1;
  undefined2 *puVar2;
  
  puVar2 = (undefined2 *)((undefined *)camry_host_ptr(0xfebe86e4u));
  if (param_1 == '\0') {
    puVar2 = ((undefined *)camry_host_ptr(0xfebe8684u));
  }
  uVar1 = FUN_00053686((int)(short)puVar2[0x17]);
  FUN_0006a5ac(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}



void FUN_000560e2(char param_1,undefined4 param_2)

{
  undefined4 uVar1;
  undefined2 *puVar2;
  
  puVar2 = (undefined2 *)((undefined *)camry_host_ptr(0xfebe86e4u));
  if (param_1 == '\0') {
    puVar2 = ((undefined *)camry_host_ptr(0xfebe8684u));
  }
  uVar1 = FUN_00053686((int)(short)puVar2[0x18]);
  FUN_0006a5ac(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}



void FUN_00056106(char param_1,undefined4 param_2)

{
  undefined4 uVar1;
  undefined2 *puVar2;
  
  puVar2 = (undefined2 *)((undefined *)camry_host_ptr(0xfebe86e4u));
  if (param_1 == '\0') {
    puVar2 = ((undefined *)camry_host_ptr(0xfebe8684u));
  }
  uVar1 = FUN_00053686((int)(short)puVar2[0x19]);
  FUN_0006a5ac(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}



void FUN_0005612a(char param_1,undefined4 param_2)

{
  undefined4 uVar1;
  undefined2 *puVar2;
  
  puVar2 = (undefined2 *)((undefined *)camry_host_ptr(0xfebe86e4u));
  if (param_1 == '\0') {
    puVar2 = ((undefined *)camry_host_ptr(0xfebe8684u));
  }
  uVar1 = FUN_00053686((int)(short)puVar2[0x1a]);
  FUN_0006a5ac(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}



/* WARNING: Removing unreachable block (ram,0x000561a4) */

void FUN_0005617e(char param_1,undefined4 param_2)

{
  undefined2 *puVar1;
  short sStack_a;
  
  puVar1 = (undefined2 *)((undefined *)camry_host_ptr(0xfebe86e4u));
  if (param_1 == '\0') {
    puVar1 = ((undefined *)camry_host_ptr(0xfebe8684u));
  }
  sStack_a = (short)(((short)puVar1[0x1b] * 100) / 0x80);
  FUN_00070110((int)sStack_a,0x7fff,0,&sStack_a);
  FUN_0006a5ac((int)sStack_a, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}



void FUN_000562fa(void)

{
  byte bVar1;
  uint saved_mask;
  uint uVar2;
  
  saved_mask = f33_priority_mask_enter(0xff00);
  uVar2 = 0;
  do {
    bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe89d2u + (uint32_t)(uVar2) * 1u))));
    if ((bVar1 >> 3 & 1) != 0) {
      bVar1 = bVar1 | 2;
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe89d2u + (uint32_t)(uVar2) * 1u)))) = bVar1;
    uVar2 = uVar2 + 1;
  } while (uVar2 < 4);
  f33_priority_mask_restore(saved_mask);
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_56330(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_56332(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_56334(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_564c8(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_564ca(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_564cc(void)

{
  return;
}



F33CaptureFieldDescriptor * FUN_00056664(undefined2 *param_1)

{
  *param_1 = 0x4b;
  return f33_capture_field_descriptor;
}



undefined * FUN_00056674(undefined2 *param_1)

{
  *param_1 = 6;
  return ((undefined *)camry_host_ptr(0x2aa6cu));
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_56682(void)

{
  return;
}



/* Single constant publisher: DAT_febe8a14 = 0; Shape-classified from the canonical corpus; the
   target cell is not yet named, so the written state's meaning is unknown. */

void FUN_00056684(void)

{
  DAT_febe8a14 = 0;
  return;
}



void FUN_0005668a(void)

{
  uint32_t puVar1;
  uint uVar2;
  
  puVar1 = 0xfebeb800u;
  uVar2 = FUN_00058c8a();
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x2dec))))) = (uVar2 & 1) == 0;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_566a0(void)

{
  return;
}



/* Paired constant publisher: DAT_febe8a18 = 0; and DAT_febe8a19 = 0;; shape-classified from the
   canonical corpus. Target cells not yet named. */

void FUN_000566a2(void)

{
  DAT_febe8a18 = 0;
  DAT_febe8a19 = 0;
  return;
}



void FUN_000566ac(void)

{
  undefined1 uVar1;
  uint32_t puVar2;
  char cVar3;
  
  puVar2 = 0xfebeb800u;
  cVar3 = FUN_00058c90();
  if ((byte)(cVar3 - (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x2de7)))))) < 5) {
    uVar1 = 0;
  }
  else {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x2de7))))) = cVar3;
    uVar1 = 0x5a;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x2de8))))) = uVar1;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_566d4(void)

{
  return;
}



/* Single constant publisher: DAT_febe8a1c = 0; Shape-classified from the canonical corpus; the
   target cell is not yet named, so the written state's meaning is unknown. */

void FUN_000566d6(void)

{
  DAT_febe8a1c = 0;
  return;
}



void FUN_000566dc(void)

{
  DAT_febe8a1c = 0;
  if ((DAT_febe5f28 & 1) == 0) {
    DAT_febe8a1c = 0x5a;
  }
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_566ee(void)

{
  return;
}



/* Paired constant publisher: DAT_febe8a20 = 0; and DAT_febe8a21 = 0;; shape-classified from the
   canonical corpus. Target cells not yet named. */

void FUN_000566f0(void)

{
  DAT_febe8a20 = 0;
  DAT_febe8a21 = 0;
  return;
}



void FUN_000566fa(void)

{
  bool bVar1;
  uint32_t puVar2;
  char cVar3;
  
  puVar2 = 0xfebeb800u;
  cVar3 = FUN_00058c8a();
  bVar1 = 3 < (byte)(cVar3 - (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x2ddf))))));
  if (bVar1) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x2ddf))))) = cVar3;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x2de0))))) = bVar1;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_56720(void)

{
  return;
}



/* Paired constant publisher: DAT_febe8a24 = 0; and DAT_febe8a25 = 0;; shape-classified from the
   canonical corpus. Target cells not yet named. */

void FUN_00056722(void)

{
  DAT_febe8a24 = 0;
  DAT_febe8a25 = 0;
  return;
}



void FUN_0005672c(void)

{
  undefined1 uVar1;
  uint32_t puVar2;
  char cVar3;
  
  puVar2 = 0xfebeb800u;
  cVar3 = FUN_00058c90();
  if ((byte)(cVar3 - (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x2ddb)))))) < 5) {
    uVar1 = 0;
  }
  else {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x2ddb))))) = cVar3;
    uVar1 = 0x5a;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x2ddc))))) = uVar1;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_56754(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_56756(void)

{
  return;
}



void FUN_00056758(void)

{
  uint uVar1;
  
  uVar1 = FUN_00067874();
  if ((uVar1 & 1) != 0) {
    f33_report_diagnostic_event_failure(0x94,0x32);
  }
  if ((uVar1 >> 1 & 1) != 0) {
    f33_report_diagnostic_event_failure(0x93,0x32);
  }
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_56786(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_56788(void)

{
  return;
}



void FUN_0005678a(void)

{
  int iVar1;
  
  iVar1 = FUN_00066f10();
  if (iVar1 == 0) {
    ((void)(0x12), thunk_FUN_000b15ac());
  }
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_567a2(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_567a4(void)

{
  return;
}



void FUN_000567a6(void)

{
  uint uVar1;
  
  uVar1 = f33_application_nvm_is_ready();
  if (uVar1 == 1) {
    ((void)(0x28), thunk_FUN_000b15ac());
  }
  return;
}



F33MonitorCurrentRecord * FUN_000567be(void)

{
  return ((undefined *)camry_host_ptr(0xa000u));
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_567c6(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_567c8(void)

{
  return;
}



void FUN_000567ca(void)

{
  undefined *puVar1;
  int iVar2;
  char cVar3;
  
  cVar3 = DAT_febe8a28;
  puVar1 = ((undefined *)camry_host_ptr(0xfebeb800u));
  if ((DAT_febe8a28 == '\0') &&
     (puVar1 = ((undefined *)camry_host_ptr(0xfebeb800u)), iVar2 = FUN_00062e12(), iVar2 == -0x5aa55aa6)) {
    FUN_00051cf6(0x20,0x32);
    cVar3 = 'Z';
  }
  puVar1[-0x2dd8] = cVar3;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_567fc(void)

{
  return;
}



void FUN_000567fe(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    *(undefined4 *)(((undefined *)camry_host_ptr(0xfebe8a2cu)) + iVar3 * 4) = 0;
    iVar1 = iVar3 + -4;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  return;
}



void FUN_00056814(uint param_1)

{
  undefined4 uVar1;
  
  if ((param_1 >> 2 & 1) == 0) {
    if ((param_1 >> 3 & 1) == 0) {
      if ((param_1 & 0x10) == 0) {
        DAT_febe3866 = 0;
        DAT_febe3873 = 0;
        if ((param_1 >> 5 & 1) == 0) {
          DAT_febe3872 = 0xff;
        }
        else {
          DAT_febe3872 = 0;
        }
        uVar1 = 0;
        goto LAB_00056854;
      }
      DAT_febe3873 = 0xff;
      goto LAB_0005683e;
    }
    DAT_febe3873 = 0xff;
    DAT_febe3872 = 0;
  }
  else {
    DAT_febe3873 = 0;
LAB_0005683e:
    DAT_febe3872 = 0xff;
  }
  DAT_febe3866 = 0xff;
  uVar1 = 2;
LAB_00056854:
  FUN_00056b78(0,uVar1);
  return;
}



void FUN_0005685e(uint param_1)

{
  undefined4 uVar1;
  
  if ((param_1 >> 0x12 & 1) == 0) {
    if ((param_1 >> 0x13 & 1) == 0) {
      if ((param_1 & 0x100000) == 0) {
        DAT_febe3865 = 0;
        DAT_febe3871 = 0;
        if ((param_1 >> 0x15 & 1) == 0) {
          DAT_febe3870 = 0xff;
        }
        else {
          DAT_febe3870 = 0;
        }
        uVar1 = 0;
        goto LAB_000568a2;
      }
      DAT_febe3871 = 0xff;
      goto LAB_0005688a;
    }
    DAT_febe3871 = 0xff;
    DAT_febe3870 = 0;
  }
  else {
    DAT_febe3871 = 0;
LAB_0005688a:
    DAT_febe3870 = 0xff;
  }
  DAT_febe3865 = 0xff;
  uVar1 = 0x20000;
LAB_000568a2:
  FUN_00056b78(1,uVar1);
  return;
}



void FUN_000568ac(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint32_t puVar4;
  uint uVar5;
  
  puVar4 = 0xfebeb800u;
  uVar5 = 0;
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    uVar5 = uVar5 | *(uint *)(((undefined *)camry_host_ptr(0xfebe8a2cu)) + iVar3 * 4);
    iVar1 = iVar3 + -4;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  FUN_00056814(uVar5);
  FUN_0005685e(uVar5);
  (*((uint *)camry_host_ptr((uint32_t)(puVar4 + -0x2dc0)))) = uVar5;
  return;
}



void FUN_000568dc(uint param_1,undefined4 param_2)

{
  if ((param_1 & 0xff) < 5) {
    *(undefined4 *)(((undefined *)camry_host_ptr(0xfebe8a2cu)) + (param_1 & 0xff) * 4) = param_2;
  }
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_568f0(void)

{
  return;
}



void FUN_000568f2(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    *(undefined4 *)(((undefined *)camry_host_ptr(0xfebe8a48u)) + iVar3 * 4) = 0;
    iVar1 = iVar3 + -1;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  return;
}



void FUN_00056908(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  DAT_febe8a44 = 0;
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    DAT_febe8a44 = DAT_febe8a44 | *(uint *)(((undefined *)camry_host_ptr(0xfebe8a48u)) + iVar3 * 4);
    iVar1 = iVar3 + -1;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  if ((DAT_febe8a44 & 1) == 0) {
    DAT_febe3877 = 0;
  }
  else {
    DAT_febe3877 = 0xff;
  }
  if ((DAT_febe8a44 >> 1 & 1) == 0) {
    DAT_febe3876 = 0;
  }
  else {
    DAT_febe3876 = 0xff;
  }
  return;
}



void FUN_0005693e(uint param_1,undefined4 param_2)

{
  if ((param_1 & 0xff) < 2) {
    *(undefined4 *)(((undefined *)camry_host_ptr(0xfebe8a48u)) + (param_1 & 0xff) * 4) = param_2;
  }
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_56952(void)

{
  return;
}



void FUN_00056954(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    *(undefined4 *)(((undefined *)camry_host_ptr(0xfebe8a50u)) + iVar3 * 4) = 0;
    iVar1 = iVar3 + -4;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  return;
}



void FUN_0005696a(uint param_1)

{
  if ((param_1 >> 1 & 1) == 0) {
    DAT_febe386f = 0;
  }
  else {
    DAT_febe386f = 0xff;
  }
  if ((param_1 >> 0x11 & 1) == 0) {
    DAT_febe386e = 0;
  }
  else {
    DAT_febe386e = 0xff;
  }
  return;
}



void FUN_00056982(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint32_t puVar4;
  uint uVar5;
  
  puVar4 = 0xfebeb800u;
  uVar5 = 0;
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    uVar5 = uVar5 | *(uint *)(((undefined *)camry_host_ptr(0xfebe8a50u)) + iVar3 * 4);
    iVar1 = iVar3 + -4;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  FUN_0005696a(uVar5);
  (*((uint *)camry_host_ptr((uint32_t)(puVar4 + -0x2d9c)))) = uVar5;
  return;
}



void FUN_000569ac(uint param_1,undefined4 param_2)

{
  if ((param_1 & 0xff) < 5) {
    *(undefined4 *)(((undefined *)camry_host_ptr(0xfebe8a50u)) + (param_1 & 0xff) * 4) = param_2;
  }
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_569c0(void)

{
  return;
}



/* Consume full R6. Bits1/17 select the requested rather than reference level for channels0/1. Both
   bits set, or the entire mask zero, also performs an early paired write before the per-channel
   writes. Preserve those repeated effects and their order; no physical channel identity is
   assigned. Consume full R6 mask; bits1/17 select two requested/reference port levels. Both bits
   set or whole mask zero adds early paired writes before individual writes. Repeated effects and
   order are real. */

void f33_apply_channel_request_mask(uint request_mask)

{
  if (((undefined1 *)camry_host_ptr((uint32_t)(request_mask & 0x20002))) == ((undefined *)camry_host_ptr(0x20002u))) {
    FUN_00066aa2();
    FUN_00066ada();
  }
  else if (request_mask == 0) {
    FUN_00066a94();
    FUN_00066acc();
  }
  if ((request_mask >> 1 & 1) == 0) {
    FUN_00066a94();
  }
  else {
    FUN_00066aa2();
  }
  if ((request_mask >> 0x11 & 1) == 0) {
    FUN_00066acc();
  }
  else {
    FUN_00066ada();
  }
  return;
}



/* Return bit1/17 when the corresponding GPIO input differs from its ROM reference level. This is
   readback, not a copy of the requested mask or proof of actuator response. Build mismatch bits1/17
   from descriptor-selected input levels differing from reference1. Return is full R10 and is not an
   echo of the requested mask. */

uint f33_read_channel_mismatch_mask(void)

{
  uint uVar1;
  uint uVar2;
  
  uVar1 = f33_channel0_matches_reference();
  if (uVar1 == 0) {
    uVar1 = 2;
  }
  else {
    uVar1 = 0;
  }
  uVar2 = f33_channel1_matches_reference();
  if (uVar2 == 0) {
    uVar1 = uVar1 | 0x20000;
  }
  return uVar1;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_56b1a(void)

{
  return;
}



void FUN_00056b1c(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    *(undefined4 *)(((undefined *)camry_host_ptr(0xfebe8a88u)) + iVar3 * 4) = 0;
    iVar1 = iVar3 + -3;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  return;
}



void FUN_00056b32(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  DAT_febe8a98 = 0;
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    DAT_febe8a98 = DAT_febe8a98 | *(uint *)(((undefined *)camry_host_ptr(0xfebe8a88u)) + iVar3 * 4);
    iVar1 = iVar3 + -3;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  if (((DAT_febe8a98 >> 1 & 1) != 0) ||
     (DAT_febe3864 = (byte)DAT_febe71ec & 1, (DAT_febe71ec & 1) != 0)) {
    DAT_febe3864 = 0xff;
  }
  if (((DAT_febe8a98 >> 0x11 & 1) != 0) ||
     (DAT_febe3863 = (byte)DAT_febe71ec & 2, (DAT_febe71ec & 2) != 0)) {
    DAT_febe3863 = 0xff;
  }
  return;
}



void FUN_00056b78(uint param_1,undefined4 param_2)

{
  if ((param_1 & 0xff) < 4) {
    *(undefined4 *)(((undefined *)camry_host_ptr(0xfebe8a88u)) + (param_1 & 0xff) * 4) = param_2;
  }
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_56b8c(void)

{
  return;
}



/* Paired constant publisher: DAT_febe8a9c = 4; and DAT_febe8aa0 = 0x40000;; shape-classified from
   the canonical corpus. Target cells not yet named. */

void FUN_00056b8e(void)

{
  DAT_febe8a9c = 4;
  DAT_febe8aa0 = 0x40000;
  return;
}



void FUN_00056b9e(uint param_1)

{
  if ((param_1 >> 2 & 1) == 0) {
    if ((param_1 >> 1 & 1) == 0) {
      DAT_febe3882 = 0xff;
    }
    else {
      DAT_febe3882 = 0;
    }
    DAT_febe3883 = 0xff;
  }
  else {
    DAT_febe3882 = 0xff;
    DAT_febe3883 = 0;
  }
  return;
}



void FUN_00056bc0(uint param_1)

{
  if ((param_1 >> 0x12 & 1) == 0) {
    if ((param_1 >> 0x11 & 1) == 0) {
      DAT_febe3880 = 0xff;
    }
    else {
      DAT_febe3880 = 0;
    }
    DAT_febe3881 = 0xff;
  }
  else {
    DAT_febe3880 = 0xff;
    DAT_febe3881 = 0;
  }
  return;
}



void FUN_00056c26(uint param_1,undefined4 param_2)

{
  if ((param_1 & 0xff) < 2) {
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebe8a9cu + (uint32_t)(param_1 & 0xff) * 4u)))) = param_2;
  }
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_56c3a(void)

{
  return;
}



/* Constant-block fill: 6 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_56c3c(void)

{
  DAT_febe8aa8 = 0xc;
  DAT_febe8ab0 = 0;
  DAT_febe8aac = 0xc0000;
  DAT_febe8ab4 = 0;
  DAT_febe8ab8 = 0;
  DAT_febe8abc = 0;
  return;
}



void FUN_00056c54(uint param_1)

{
  if (DAT_000318fc != 'Z') {
    if (((param_1 >> 2 & 1) == 0) && ((param_1 & 2) != 0)) {
      DAT_febe3875 = 0xff;
    }
    else {
      DAT_febe3875 = 0;
    }
    if (((param_1 >> 0x12 & 1) == 0) && ((param_1 & 0x20000) != 0)) {
      DAT_febe3874 = 0xff;
    }
    else {
      DAT_febe3874 = 0;
    }
    if ((param_1 >> 3 & 1) == 0) {
      DAT_febe386d = 0;
    }
    else {
      DAT_febe386d = 0xff;
    }
    if ((param_1 >> 0x13 & 1) == 0) {
      DAT_febe386c = 0;
    }
    else {
      DAT_febe386c = 0xff;
    }
    return;
  }
  DAT_febe3875 = 0;
  DAT_febe3874 = 0;
  return;
}



void FUN_00056cb0(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint32_t puVar4;
  uint uVar5;
  
  puVar4 = 0xfebeb800u;
  uVar5 = 0;
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    uVar5 = uVar5 | (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebe8aa8u + (uint32_t)(iVar3) * 4u))));
    iVar1 = iVar3 + -5;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  FUN_00056c54(uVar5);
  (*((uint *)camry_host_ptr((uint32_t)(puVar4 + -0x2d40)))) = uVar5;
  return;
}



void FUN_00056cda(uint param_1,undefined4 param_2)

{
  if ((param_1 & 0xff) < 6) {
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebe8aa8u + (uint32_t)(param_1 & 0xff) * 4u)))) = param_2;
  }
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_56cee(void)

{
  return;
}



/* Single constant publisher: DAT_febe8ac4 = 0; Shape-classified from the canonical corpus; the
   target cell is not yet named, so the written state's meaning is unknown. */

void FUN_00056cf0(void)

{
  DAT_febe8ac4 = 0;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_56d78(void)

{
  return;
}



void FUN_00056d92(uint param_1)

{
  if ((param_1 >> 1 & 1) == 0) {
    DAT_febe3885 = 0xff;
  }
  else {
    DAT_febe3885 = 0;
  }
  if ((param_1 >> 0x11 & 1) == 0) {
    DAT_febe3884 = 0xff;
  }
  else {
    DAT_febe3884 = 0;
  }
  return;
}



void FUN_00056daa(void)

{
  if ((DAT_febe8ae4 & 2) == 0) {
    DAT_febe8aca = 0;
    if (DAT_febe8ac9 < DAT_00031900) {
      DAT_febe8ac9 = DAT_febe8ac9 + 1;
      DAT_febe8ac8 = 3;
    }
    else {
      DAT_febe8ac8 = 2;
    }
  }
  else {
    DAT_febe8ac9 = 0;
    if (DAT_febe8aca < DAT_00031901) {
      DAT_febe8aca = DAT_febe8aca + 1;
      DAT_febe8ac8 = 1;
    }
    else {
      DAT_febe8ac8 = 0;
    }
  }
  return;
}



void FUN_00056dee(void)

{
  if ((DAT_febe8ae4 & 0x20000) == 0) {
    DAT_febe8acd = 0;
    if (DAT_febe8acc < DAT_00031900) {
      DAT_febe8acc = DAT_febe8acc + 1;
      DAT_febe8acb = 3;
    }
    else {
      DAT_febe8acb = 2;
    }
  }
  else {
    DAT_febe8acc = 0;
    if (DAT_febe8acd < DAT_00031901) {
      DAT_febe8acd = DAT_febe8acd + 1;
      DAT_febe8acb = 1;
    }
    else {
      DAT_febe8acb = 0;
    }
  }
  return;
}



void FUN_00056e34(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint32_t puVar4;
  uint uVar5;
  
  puVar4 = 0xfebeb800u;
  uVar5 = 0;
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    uVar5 = uVar5 | (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebe8ad0u + (uint32_t)(iVar3) * 4u))));
    iVar1 = iVar3 + -4;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  FUN_00056d92(uVar5);
  (*((uint *)camry_host_ptr((uint32_t)(puVar4 + -0x2d1c)))) = uVar5;
  FUN_00056daa();
  FUN_00056dee();
  return;
}



void FUN_00056e66(uint param_1,undefined4 param_2)

{
  if ((param_1 & 0xff) < 5) {
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebe8ad0u + (uint32_t)(param_1 & 0xff) * 4u)))) = param_2;
  }
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_56e7a(void)

{
  return;
}



/* Paired constant publisher: DAT_febe8ae8 = 4; and DAT_febe8aec = 0x40000;; shape-classified from
   the canonical corpus. Target cells not yet named. */

void FUN_00056e7c(void)

{
  DAT_febe8ae8 = 4;
  DAT_febe8aec = 0x40000;
  return;
}



void FUN_00056e8c(uint param_1)

{
  if ((param_1 >> 2 & 1) == 0) {
    if ((param_1 >> 1 & 1) == 0) {
      DAT_febe387e = 0xff;
    }
    else {
      DAT_febe387e = 0;
    }
    DAT_febe387f = 0xff;
  }
  else {
    DAT_febe387e = 0xff;
    DAT_febe387f = 0;
  }
  return;
}



void FUN_00056eae(uint param_1)

{
  if ((param_1 >> 0x12 & 1) == 0) {
    if ((param_1 >> 0x11 & 1) == 0) {
      DAT_febe387c = 0xff;
    }
    else {
      DAT_febe387c = 0;
    }
    DAT_febe387d = 0xff;
  }
  else {
    DAT_febe387c = 0xff;
    DAT_febe387d = 0;
  }
  return;
}



void FUN_00056ed0(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint32_t puVar4;
  uint uVar5;
  
  puVar4 = 0xfebeb800u;
  if ((DAT_febe8ae4 >> 1 & 1) == 0) {
    uVar5 = 0;
  }
  else {
    uVar5 = 4;
  }
  if ((DAT_febe8ae4 >> 0x11 & 1) != 0) {
    uVar5 = uVar5 | 0x40000;
  }
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    uVar5 = uVar5 | (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebe8ae8u + (uint32_t)(iVar3) * 4u))));
    iVar1 = iVar3 + -1;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  FUN_00056e8c(uVar5);
  FUN_00056eae(uVar5);
  (*((uint *)camry_host_ptr((uint32_t)(puVar4 + -0x2d10)))) = uVar5;
  return;
}



void FUN_00056f14(uint param_1,undefined4 param_2)

{
  if ((param_1 & 0xff) < 2) {
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebe8ae8u + (uint32_t)(param_1 & 0xff) * 4u)))) = param_2;
  }
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_56f28(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_56f2a(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_56f2c(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_56f2e(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_56f30(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_56f8a(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_56f8c(void)

{
  return;
}



void FUN_00056f8e(void)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  iVar2 = FUN_0008d9a2();
  if (iVar2 == 0xb) {
    FUN_00051cf6(0x27,0x32);
    if ((*((int *)camry_host_ptr((uint32_t)(puVar1 + -0x2d04)))) != -1) {
      (*((int *)camry_host_ptr((uint32_t)(puVar1 + -0x2d04)))) = (*((int *)camry_host_ptr((uint32_t)(puVar1 + -0x2d04)))) + 1;
    }
    FUN_0008d9ac();
  }
  return;
}



/* Single constant publisher: DAT_febe8afc = 0; Shape-classified from the canonical corpus; the
   target cell is not yet named, so the written state's meaning is unknown. */

void FUN_00056fbc(void)

{
  DAT_febe8afc = 0;
  return;
}



/* Single constant publisher: DAT_febe8b00 = 0; Shape-classified from the canonical corpus; the
   target cell is not yet named, so the written state's meaning is unknown. */

void FUN_00056fc2(void)

{
  DAT_febe8b00 = 0;
  return;
}



/* Single constant publisher: DAT_febe8b00 = 0; Shape-classified from the canonical corpus; the
   target cell is not yet named, so the written state's meaning is unknown. */

void FUN_00056fc8(void)

{
  DAT_febe8b00 = 0;
  return;
}



void FUN_00056fce(void)

{
  undefined *puVar1;
  int iVar2;
  char cVar3;
  
  cVar3 = DAT_febe8b00;
  puVar1 = ((undefined *)camry_host_ptr(0xfebeb800u));
  if ((DAT_febe8b00 != 'Z') && (puVar1 = ((undefined *)camry_host_ptr(0xfebeb800u)), iVar2 = FUN_0006a150(), iVar2 == 0x5a)) {
    f33_report_diagnostic_event_failure(0xcc,0x32);
    cVar3 = 'Z';
  }
  puVar1[-0x2d00] = cVar3;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_56ffe(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_57000(void)

{
  return;
}



/* WARNING: Inlined function: f33_crypto_bank_profile_count */

void FUN_00057002(void)

{
  undefined *puVar1;
  byte bVar3;
  int iVar4;
  int iVar5;
  char cVar6;
  byte bVar7;
  undefined8 uVar2;
  
  cVar6 = DAT_febe8b04;
  uVar2 = 0xfebeb800;
  puVar1 = ((undefined *)camry_host_ptr(0xfebeb800u));
  if (DAT_febe8b04 != 'Z') {
    bVar3 = f33_crypto_config_profile_count;
    if (2 < f33_crypto_config_profile_count) {
      bVar3 = 2;
    }
    iVar5 = 0;
    for (bVar7 = 0; puVar1 = ((undefined *)camry_host_ptr((uint32_t)(uVar2))), bVar7 < bVar3; bVar7 = bVar7 + 1) {
      iVar4 = FUN_0006a180(bVar7);
      if (iVar4 == 0x5a) {
        iVar5 = 0x5a;
      }
    }
    if (iVar5 == 0x5a) {
      FUN_00051cf6(0x28,0x32);
      cVar6 = 'Z';
    }
  }
  puVar1[-0x2cfc] = cVar6;
  return;
}



/* Single constant publisher: DAT_febe8b04 = 0; Shape-classified from the canonical corpus; the
   target cell is not yet named, so the written state's meaning is unknown. */

void FUN_0005704e(void)

{
  DAT_febe8b04 = 0;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_57054(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_57056(void)

{
  return;
}



void FUN_00057058(void)

{
  uint32_t puVar1;
  int iVar2;
  int iVar3;
  undefined1 uVar4;
  short sStack_e;
  
  puVar1 = 0xfebeb800u;
  iVar2 = FUN_00062d56(&sStack_e);
  f33_return_only_stub_62d54();
  iVar3 = FUN_000546f2(1);
  if ((iVar2 == 0) && ((sStack_e == 0x5aa5 || (sStack_e == -0x55ab)))) {
    iVar3 = iVar3 + 1;
    if (sStack_e == 0x5aa5) {
      uVar4 = 1;
    }
    else {
      uVar4 = 3;
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x2cf8))))) = uVar4;
    FUN_000545de(1);
  }
  (*((int *)camry_host_ptr((uint32_t)(puVar1 + -0x2cf4)))) = iVar3;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_570a6(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_570a8(void)

{
  return;
}



void FUN_000570aa(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  DAT_febe8b17 = 0x5a;
  iVar3 = 0;
  DAT_febe8b10 = DAT_febe8b17;
  do {
    iVar2 = iVar3 + 1;
    DAT_febe8b10 = DAT_febe8b10 & (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe8b11u + (uint32_t)(iVar3) * 1u))));
    iVar1 = iVar3 + -2;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    DAT_febe8b17 = DAT_febe8b17 & (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe8b14u + (uint32_t)(iVar3) * 1u))));
    iVar1 = iVar3 + -2;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  if (DAT_febe8b10 == 0x5a) {
    DAT_febe3887 = 0xff;
  }
  else {
    DAT_febe3887 = 0;
  }
  if (DAT_febe8b17 == 0x5a) {
    DAT_febe3886 = 0xff;
  }
  else {
    DAT_febe3886 = 0;
  }
  return;
}



void FUN_000570f4(uint param_1,undefined1 param_2)

{
  if ((param_1 & 0xff) < 3) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe8b11u + (uint32_t)(param_1 & 0xff) * 1u)))) = param_2;
  }
  return;
}



void FUN_00057106(uint param_1,undefined1 param_2)

{
  if ((param_1 & 0xff) < 3) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe8b14u + (uint32_t)(param_1 & 0xff) * 1u)))) = param_2;
  }
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_57118(void)

{
  return;
}



void FUN_0005711a(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    *(undefined4 *)(((undefined *)camry_host_ptr(0xfebe8b1cu)) + iVar3 * 4) = 0;
    iVar1 = iVar3 + -1;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  return;
}



void FUN_0005719c(uint param_1,undefined4 param_2)

{
  if ((param_1 & 0xff) < 2) {
    *(undefined4 *)(((undefined *)camry_host_ptr(0xfebe8b1cu)) + (param_1 & 0xff) * 4) = param_2;
  }
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_571b0(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_571b2(void)

{
  return;
}



/* Map request bit0/16 to configured port-level callbacks and return only those bits. If prior8B28
   has both bit1/17 set, perform preliminary paired writes for both-new-set or both-new-clear before
   normal per-bank writes. No GPIO feedback or software permission is derived. */

uint f33_apply_output_request_port_levels(uint request)

{
  bool bVar1;
  uint uVar2;
  
  if (((undefined1 *)camry_host_ptr((uint32_t)(f33_output_request_status & 0x20002))) == ((undefined *)camry_host_ptr(0x20002u))) {
    if ((request & 0x10001) == 0x10001) {
      f33_write_output_bank0_port_level_b();
      f33_write_output_bank1_port_level_b();
    }
    else if ((request & 0x10001) == 0) {
      f33_write_output_bank0_port_level_a();
      f33_write_output_bank1_port_level_a();
    }
  }
  bVar1 = (request & 1) == 0;
  if (bVar1) {
    f33_write_output_bank0_port_level_a();
  }
  else {
    f33_write_output_bank0_port_level_b();
  }
  uVar2 = (uint)!bVar1;
  if ((request >> 0x10 & 1) == 0) {
    f33_write_output_bank1_port_level_a();
  }
  else {
    f33_write_output_bank1_port_level_b();
    uVar2 = uVar2 | 0x10000;
  }
  return uVar2;
}



/* Per bank start6-bit mask3F; requestbit2 selects38, bits12/13/14 AND F6/ED/1B and echo their
   status bits. All three phase bits add statusbit1; otherwise low3 mask zero addsbit2. Repeat
   at+16. Stage masks through61C40 and publish8B24/25. Masking alone40004 does not activate neutral
   slot3. */

uint f33_stage_output_request_phase_masks(uint request)

{
  uint uVar1;
  uint32_t puVar2;
  byte mask;
  byte mask_00;
  uint uVar3;
  
  puVar2 = 0xfebeb800u;
  mask = 0x3f;
  uVar3 = 0;
  mask_00 = mask;
  if ((request >> 2 & 1) != 0) {
    mask_00 = 0x38;
  }
  if ((request >> 0xc & 1) != 0) {
    mask_00 = mask_00 & 0xf6;
    uVar3 = 0x1000;
  }
  if ((request >> 0xd & 1) != 0) {
    uVar3 = uVar3 | 0x2000;
    mask_00 = mask_00 & 0xed;
  }
  if ((request >> 0xe & 1) != 0) {
    mask_00 = mask_00 & 0x1b;
    uVar3 = uVar3 | 0x4000;
  }
  if ((request & 0x7000) == 0x7000) {
    uVar3 = uVar3 | 2;
  }
  else if ((mask_00 & 7) == 0) {
    uVar3 = uVar3 | 4;
  }
  if ((request >> 0x12 & 1) != 0) {
    mask = 0x38;
  }
  if ((request >> 0x1c & 1) != 0) {
    mask = mask & 0xf6;
    uVar3 = uVar3 | 0x10000000;
  }
  if ((request >> 0x1d & 1) != 0) {
    mask = mask & 0xed;
    uVar3 = uVar3 | 0x20000000;
  }
  if ((request >> 0x1e & 1) != 0) {
    mask = mask & 0x1b;
    uVar3 = uVar3 | 0x40000000;
  }
  if ((request & 0x7fffffff) >> 0x1c == 7) {
    uVar1 = 0x20000;
  }
  else {
    if ((mask & 7) != 0) goto LAB_000572cc;
    uVar1 = 0x40000;
  }
  uVar3 = uVar3 | uVar1;
LAB_000572cc:
  f33_stage_output_bank0_phase_mask(mask_00);
  f33_stage_output_bank1_phase_mask(mask);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x2cdc))))) = mask_00;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x2cdb))))) = mask;
  return uVar3;
}



/* OR eight owner words8B2C; apply configured GPIO levels571B4 and phase-mask staging5721C, OR
   returned status. Per-bank status&3 activates slot3 with three exact31908=4000 codes; otherwise
   release slot3. Finally publish8B28. This does not select a winner. Full native entry stops at
   unmapped GPIOFFC100C4;57308..57376 continuation has explicit R28/R10 handoff, not physical-output
   proof. */

void f33_publish_aggregate_output_requests(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint32_t puVar4;
  uint uVar5;
  uint uVar6;
  ushort uStack_12;
  ushort uStack_10;
  ushort uStack_e;
  
  puVar4 = 0xfebeb800u;
  uVar6 = 0;
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    uVar6 = uVar6 | f33_output_request_words[iVar3];
    iVar1 = iVar3 + -7;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  uVar5 = f33_apply_output_request_port_levels(uVar6);
  uVar6 = f33_stage_output_request_phase_masks(uVar6);
  uVar5 = uVar5 | uVar6;
  if ((uVar5 & 3) == 0) {
    f33_release_phase_output_slot_bank0('\x03');
  }
  else {
    uStack_12 = DAT_00031908;
    uStack_10 = DAT_00031908;
    uStack_e = DAT_00031908;
    f33_write_phase_output_slot_bank0(10,'\x03',&uStack_12);
    f33_activate_phase_output_slot_bank0('\x03');
  }
  if ((uVar5 & 0x30000) == 0) {
    f33_release_phase_output_slot_bank1('\x03');
  }
  else {
    uStack_12 = DAT_00031908;
    uStack_10 = DAT_00031908;
    uStack_e = DAT_00031908;
    f33_write_phase_output_slot_bank1(10,'\x03',&uStack_12);
    f33_activate_phase_output_slot_bank1('\x03');
  }
  (*((uint *)camry_host_ptr((uint32_t)(puVar4 + -0x2cd8)))) = uVar5;
  return;
}



/* Low8 owner<8 replaces one u32 at8B2C. No reduction, physical port write or slot arbitration here.
    */

void f33_set_output_request_word(uchar owner,uint request)

{
  if (owner < 8) {
    f33_output_request_words[owner] = request;
  }
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_5738e(void)

{
  return;
}



/* Clear request enables8B4C/D and initialize both retained triplets8B4E..58 to4000. Called on
   crossing into mode>0100; unlike573FE it also resets codes. */

void f33_initialize_direct_output_requests(void)

{
  f33_direct_output_request_enables[1] = '\0';
  f33_direct_output_request_enables[0] = '\0';
  f33_direct_output_codes_bank1[2] = 0x4000;
  f33_direct_output_codes_bank1[1] = 0x4000;
  f33_direct_output_codes_bank1[0] = 0x4000;
  f33_direct_output_codes_bank0[2] = 0x4000;
  f33_direct_output_codes_bank0[1] = 0x4000;
  f33_direct_output_codes_bank0[0] = 0x4000;
  return;
}



/* Each nonzero request byte8B4C/D copies its retained triplet to slot4 with context10 and activates
   that bank. Zero releases slot4 without erasing its codes. Flags dirty selection only on change.
   Native composition verifies independent activation/release then real arbitration, including slot1
   clamp exemption. */

void f33_publish_direct_output_requests(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (f33_direct_output_request_enables[0] == '\0') {
    f33_release_phase_output_slot_bank0('\x04');
  }
  else {
    puVar1 = 0xfebeb800u;
    f33_write_phase_output_slot_bank0(10,'\x04',f33_direct_output_codes_bank0);
    f33_activate_phase_output_slot_bank0('\x04');
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x2cb3))))) == '\0') {
    f33_release_phase_output_slot_bank1('\x04');
  }
  else {
    f33_write_phase_output_slot_bank1(10,'\x04',f33_direct_output_codes_bank1);
    f33_activate_phase_output_slot_bank1('\x04');
  }
  return;
}



/* Clear8B4C/8B4D only.
   Majorarbitercallsbeforeeveryhandledfamilyexcept0200;stageandexitcallersalsoexplicitlyclear.
   Doesnotclearownerrequestarraysorprovephysicalzerooutput. */

void f33_clear_direct_output_enables(void)

{
  f33_direct_output_request_enables[0] = '\0';
  f33_direct_output_request_enables[1] = '\0';
  return;
}



/* Store0 to request byte8B4C only. Publication/release of slot4 occurs later in573AE; retained
   triplet is unchanged. */

void f33_clear_direct_output_bank0(void)

{
  f33_direct_output_request_enables[0] = '\0';
  return;
}



/* Store0 to request byte8B4D only. Publication/release of slot4 occurs later in573AE; retained
   triplet is unchanged. */

void f33_clear_direct_output_bank1(void)

{
  f33_direct_output_request_enables[1] = '\0';
  return;
}



/* Store5A to request byte8B4C only. Publication/release of slot4 occurs later in573AE; retained
   triplet is unchanged. */

void f33_request_direct_output_bank0(void)

{
  f33_direct_output_request_enables[0] = 'Z';
  return;
}



/* Store5A to request byte8B4D only. Publication/release of slot4 occurs later in573AE; retained
   triplet is unchanged. */

void f33_request_direct_output_bank1(void)

{
  f33_direct_output_request_enables[1] = 'Z';
  return;
}



/* Copy three halfwords into retained direct request at8B4E; do not activate the request or publish
   slot4. No local pointer or code-range validation. */

void f33_set_direct_output_codes_bank0(ushort *codes)

{
  f33_direct_output_codes_bank0[0] = *codes;
  f33_direct_output_codes_bank0[1] = codes[1];
  f33_direct_output_codes_bank0[2] = codes[2];
  return;
}



/* Copy three halfwords into retained direct request at8B54; do not activate the request or publish
   slot4. No local pointer or code-range validation. */

void f33_set_direct_output_codes_bank1(ushort *codes)

{
  f33_direct_output_codes_bank1[0] = *codes;
  f33_direct_output_codes_bank1[1] = codes[1];
  f33_direct_output_codes_bank1[2] = codes[2];
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_57458(void)

{
  return;
}



/* Constant-block fill: 16 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_5745a(void)

{
  DAT_febe8b5c = 0;
  DAT_febe8b5d = 0;
  DAT_febe8b5e = 0;
  DAT_febe8b5f = 0;
  DAT_febe8b6c = 0x4000;
  DAT_febe8b6e = 0x4000;
  DAT_febe8b70 = 0x4000;
  DAT_febe8b72 = 0x4000;
  DAT_febe8b74 = 0x4000;
  DAT_febe8b76 = 0x4000;
  DAT_febe8b78 = 0x4000;
  DAT_febe8b7a = 0x4000;
  DAT_febe8b7c = 0x4000;
  DAT_febe8b7e = 0x4000;
  DAT_febe8b80 = 0x4000;
  DAT_febe8b82 = 0x4000;
  return;
}



/* Paired constant publisher: DAT_febe8b84 = 0x7fff; and DAT_febe8b86 = 0x7fff;; shape-classified
   from the canonical corpus. Target cells not yet named. */

void FUN_000575ac(void)

{
  DAT_febe8b84 = 0x7fff;
  DAT_febe8b86 = 0x7fff;
  return;
}



/* Set all three requested limits per bank and cached minima to8000; complements7FFF. Published
   limits/flags are separate575F6 outputs. */

void f33_initialize_output_code_limit_requests(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = 0;
  do {
    *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe8b8au)) + iVar3 * 2) = 0x8000;
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -2;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe8b94u)) + iVar3 * 2) = 0x8000;
    iVar1 = iVar3 + -2;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  DAT_febe8b90 = 0x8000;
  DAT_febe8b9a = 0x8000;
  DAT_febe8b84 = 0x7fff;
  DAT_febe8b86 = 0x7fff;
  return;
}



/* Per bank, reduce three unsigned requested limits from nominal8000 only when cached
   minimum/complement disagree. Publish minimum8B92/9C and flag8B88/89=5A exactly when below8000.
   Thus ordinary reduced limits also force mode0 in37C4C. Self-consistent caches are retained; not
   an independent bridge-disable permission. */

void f33_reduce_phase_output_code_limits(void)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  int iVar4;
  uint uVar5;
  
  uVar3 = (uint)DAT_febe8b90;
  uVar5 = (uint)DAT_febe8b9a;
  if (uVar3 != (ushort)~DAT_febe8b84) {
    uVar3 = 0x8000;
    iVar4 = 0;
    do {
      if ((int)(*(ushort *)(((undefined *)camry_host_ptr(0xfebe8b8au)) + iVar4 * 2) - uVar3) < 0) {
        uVar3 = (uint)*(ushort *)(((undefined *)camry_host_ptr(0xfebe8b8au)) + iVar4 * 2);
      }
      iVar2 = iVar4 + 1;
      iVar1 = iVar4 + -2;
      iVar4 = iVar2;
    } while (((iVar1 < 0) || (iVar2 < 0)));
    DAT_febe8b90 = (ushort)uVar3;
    DAT_febe8b84 = ~DAT_febe8b90;
  }
  if (uVar5 != (ushort)~DAT_febe8b86) {
    uVar5 = 0x8000;
    iVar4 = 0;
    do {
      if ((int)(*(ushort *)(((undefined *)camry_host_ptr(0xfebe8b94u)) + iVar4 * 2) - uVar5) < 0) {
        uVar5 = (uint)*(ushort *)(((undefined *)camry_host_ptr(0xfebe8b94u)) + iVar4 * 2);
      }
      iVar2 = iVar4 + 1;
      iVar1 = iVar4 + -2;
      iVar4 = iVar2;
    } while (((iVar1 < 0) || (iVar2 < 0)));
    DAT_febe8b9a = (ushort)uVar5;
    DAT_febe8b86 = ~DAT_febe8b9a;
  }
  DAT_febe8b88 = 0;
  if (uVar3 < 0x8000) {
    DAT_febe8b88 = 0x5a;
  }
  DAT_febe8b89 = 0;
  if (uVar5 < 0x8000) {
    DAT_febe8b89 = 0x5a;
  }
  DAT_febe8b92 = (short)uVar3;
  DAT_febe8b9c = (short)uVar5;
  return;
}



/* Low8 owner<3 stores requested u16 limit; reduce all three from nominal8000 and update
   minimum/complement. Unchanged request may return early when cache is already no greater. Only
   owner1 has a recovered requester,3C6A8. Published limits/flags wait for575F6. */

void f33_set_output_code_limit_bank0(uchar owner,ushort limit)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  int iVar4;
  
  if (owner < 3) {
    iVar4 = (uint)owner * 2;
    if (*(ushort *)(((undefined *)camry_host_ptr(0xfebe8b8au)) + iVar4) == limit) {
      if (DAT_febe8b90 <= limit) {
        return;
      }
      uVar3 = 0x8000;
      iVar4 = 0;
      do {
        if ((int)(*(ushort *)(((undefined *)camry_host_ptr(0xfebe8b8au)) + iVar4 * 2) - uVar3) < 0) {
          uVar3 = (uint)*(ushort *)(((undefined *)camry_host_ptr(0xfebe8b8au)) + iVar4 * 2);
        }
        iVar2 = iVar4 + 1;
        iVar1 = iVar4 + -2;
        iVar4 = iVar2;
      } while (((iVar1 < 0) || (iVar2 < 0)));
      DAT_febe8b90 = (ushort)uVar3;
    }
    else {
      *(ushort *)(((undefined *)camry_host_ptr(0xfebe8b8au)) + iVar4) = limit;
      uVar3 = 0x8000;
      iVar4 = 0;
      do {
        if ((int)(*(ushort *)(((undefined *)camry_host_ptr(0xfebe8b8au)) + iVar4 * 2) - uVar3) < 0) {
          uVar3 = (uint)*(ushort *)(((undefined *)camry_host_ptr(0xfebe8b8au)) + iVar4 * 2);
        }
        iVar2 = iVar4 + 1;
        iVar1 = iVar4 + -2;
        iVar4 = iVar2;
      } while (((iVar1 < 0) || (iVar2 < 0)));
      DAT_febe8b90 = (ushort)uVar3;
    }
    DAT_febe8b84 = ~(ushort)uVar3;
  }
  return;
}



/* Low8 owner<3 stores requested u16 limit; reduce all three from nominal8000 and update
   minimum/complement. Unchanged request may return early when cache is already no greater. Only
   owner1 has a recovered requester,3C6A8. Published limits/flags wait for575F6. */

void f33_set_output_code_limit_bank1(uchar owner,ushort limit)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  int iVar4;
  
  if (owner < 3) {
    iVar4 = (uint)owner * 2;
    if (*(ushort *)(((undefined *)camry_host_ptr(0xfebe8b94u)) + iVar4) == limit) {
      if (DAT_febe8b9a <= limit) {
        return;
      }
      uVar3 = 0x8000;
      iVar4 = 0;
      do {
        if ((int)(*(ushort *)(((undefined *)camry_host_ptr(0xfebe8b94u)) + iVar4 * 2) - uVar3) < 0) {
          uVar3 = (uint)*(ushort *)(((undefined *)camry_host_ptr(0xfebe8b94u)) + iVar4 * 2);
        }
        iVar2 = iVar4 + 1;
        iVar1 = iVar4 + -2;
        iVar4 = iVar2;
      } while (((iVar1 < 0) || (iVar2 < 0)));
      DAT_febe8b9a = (ushort)uVar3;
    }
    else {
      *(ushort *)(((undefined *)camry_host_ptr(0xfebe8b94u)) + iVar4) = limit;
      uVar3 = 0x8000;
      iVar4 = 0;
      do {
        if ((int)(*(ushort *)(((undefined *)camry_host_ptr(0xfebe8b94u)) + iVar4 * 2) - uVar3) < 0) {
          uVar3 = (uint)*(ushort *)(((undefined *)camry_host_ptr(0xfebe8b94u)) + iVar4 * 2);
        }
        iVar2 = iVar4 + 1;
        iVar1 = iVar4 + -2;
        iVar4 = iVar2;
      } while (((iVar1 < 0) || (iVar2 < 0)));
      DAT_febe8b9a = (ushort)uVar3;
    }
    DAT_febe8b86 = ~(ushort)uVar3;
  }
  return;
}



/* Low8 owner<3 restores requested limit8000; reduce all three from nominal8000 and update
   minimum/complement. Unchanged request may return early when cache is already no greater. Only
   owner1 has a recovered requester,3C6A8. Published limits/flags wait for575F6. */

void f33_release_output_code_limit_bank0(uchar owner)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  
  if (owner < 3) {
    iVar3 = (uint)owner * 2;
    uVar4 = 0x8000;
    if (*(short *)(((undefined *)camry_host_ptr(0xfebe8b8au)) + iVar3) == -0x8000) {
      if (DAT_febe8b90 < 0x8001) {
        return;
      }
      iVar3 = 0;
      do {
        if ((int)(*(ushort *)(((undefined *)camry_host_ptr(0xfebe8b8au)) + iVar3 * 2) - uVar4) < 0) {
          uVar4 = (uint)*(ushort *)(((undefined *)camry_host_ptr(0xfebe8b8au)) + iVar3 * 2);
        }
        iVar2 = iVar3 + 1;
        iVar1 = iVar3 + -2;
        iVar3 = iVar2;
      } while (((iVar1 < 0) || (iVar2 < 0)));
      DAT_febe8b90 = (ushort)uVar4;
    }
    else {
      *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe8b8au)) + iVar3) = 0x8000;
      uVar4 = 0x8000;
      iVar3 = 0;
      do {
        if ((int)(*(ushort *)(((undefined *)camry_host_ptr(0xfebe8b8au)) + iVar3 * 2) - uVar4) < 0) {
          uVar4 = (uint)*(ushort *)(((undefined *)camry_host_ptr(0xfebe8b8au)) + iVar3 * 2);
        }
        iVar2 = iVar3 + 1;
        iVar1 = iVar3 + -2;
        iVar3 = iVar2;
      } while (((iVar1 < 0) || (iVar2 < 0)));
      DAT_febe8b90 = (ushort)uVar4;
    }
    DAT_febe8b84 = ~(ushort)uVar4;
  }
  return;
}



/* Low8 owner<3 restores requested limit8000; reduce all three from nominal8000 and update
   minimum/complement. Unchanged request may return early when cache is already no greater. Only
   owner1 has a recovered requester,3C6A8. Published limits/flags wait for575F6. */

void f33_release_output_code_limit_bank1(uchar owner)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  
  if (owner < 3) {
    iVar3 = (uint)owner * 2;
    uVar4 = 0x8000;
    if (*(short *)(((undefined *)camry_host_ptr(0xfebe8b94u)) + iVar3) == -0x8000) {
      if (DAT_febe8b9a < 0x8001) {
        return;
      }
      iVar3 = 0;
      do {
        if ((int)(*(ushort *)(((undefined *)camry_host_ptr(0xfebe8b94u)) + iVar3 * 2) - uVar4) < 0) {
          uVar4 = (uint)*(ushort *)(((undefined *)camry_host_ptr(0xfebe8b94u)) + iVar3 * 2);
        }
        iVar2 = iVar3 + 1;
        iVar1 = iVar3 + -2;
        iVar3 = iVar2;
      } while (((iVar1 < 0) || (iVar2 < 0)));
      DAT_febe8b9a = (ushort)uVar4;
    }
    else {
      *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe8b94u)) + iVar3) = 0x8000;
      uVar4 = 0x8000;
      iVar3 = 0;
      do {
        if ((int)(*(ushort *)(((undefined *)camry_host_ptr(0xfebe8b94u)) + iVar3 * 2) - uVar4) < 0) {
          uVar4 = (uint)*(ushort *)(((undefined *)camry_host_ptr(0xfebe8b94u)) + iVar3 * 2);
        }
        iVar2 = iVar3 + 1;
        iVar1 = iVar3 + -2;
        iVar3 = iVar2;
      } while (((iVar1 < 0) || (iVar2 < 0)));
      DAT_febe8b9a = (ushort)uVar4;
    }
    DAT_febe8b86 = ~(ushort)uVar4;
  }
  return;
}



/* Paired constant publisher: DAT_febe8ba0 = 0xff; and DAT_febe8ba1 = 0xff;; shape-classified from
   the canonical corpus. Target cells not yet named. */

void FUN_000579e8(void)

{
  DAT_febe8ba0 = 0xff;
  DAT_febe8ba1 = 0xff;
  return;
}



/* Clear both five-slot enable banks and dirty flags; initialize all triplets4000. Select index0,
   complementFF and enable slot0 in both banks. Does not overwrite selected output triplets8BEE..F8.
    */

void f33_initialize_phase_output_slots(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  DAT_febe8ba7 = 0;
  iVar3 = 0;
  do {
    f33_output_slot_enables_bank0[iVar3] = '\0';
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -4;
    f33_output_slot_codes_bank0[iVar3 * 3] = 0x4000;
    f33_output_slot_codes_bank0[iVar3 * 3 + 1] = 0x4000;
    f33_output_slot_codes_bank0[iVar3 * 3 + 2] = 0x4000;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  DAT_febe8bad = 0;
  iVar3 = 0;
  do {
    f33_output_slot_enables_bank1[iVar3] = '\0';
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -4;
    f33_output_slot_codes_bank1[iVar3 * 3] = 0x4000;
    f33_output_slot_codes_bank1[iVar3 * 3 + 1] = 0x4000;
    f33_output_slot_codes_bank1[iVar3 * 3 + 2] = 0x4000;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  DAT_febe8baf = 0;
  DAT_febe8bae = 0;
  DAT_febe8ba1 = 0xff;
  f33_output_slot_enables_bank1[0] = 'Z';
  DAT_febe8ba0 = 0xff;
  f33_output_slot_enables_bank0[0] = 'Z';
  return;
}



/* Scan slots0..4 and choose the highest enabled slot for each bank. Publish selected
   index/complement and triplets8BEE..8BF8. Optional code clamp uses [8000-L,L], L
   bounded4000..8000. Selected indices are not boolean bridge-disable flags; slot4 can outrank
   aggregate-request neutral slot3. Highest enabled slot0..4 wins per bank. Native nonzero tail
   verifies slots4/3 outrank freshly published slot0 and bounded output; staging-only case verifies
   slot1 exemption from the code clamp. Cached index/complement and dirty flag control rescan. Slot
   indices are not physical-disable booleans. Native direct-owner composition additionally checks
   activation/release dirtying despite consistent caches and independent first-slot4/second-slot1
   selection. */

void f33_select_phase_output_slots(void)

{
  int iVar1;
  ushort uVar2;
  uint uVar3;
  ushort uVar4;
  ushort uVar5;
  ushort uVar6;
  uint uVar7;
  uint uVar8;
  uint uVar9;
  
  uVar8 = (uint)DAT_febe8bae;
  uVar5 = DAT_febe8b92;
  if (0x7fff < DAT_febe8b92) {
    uVar5 = 0x8000;
  }
  if (uVar5 < 0x4000) {
    uVar5 = 0x4000;
  }
  uVar2 = 0x8000 - uVar5;
  if ((uVar8 != (byte)~DAT_febe8ba0) || (DAT_febe8ba7 != '\0')) {
    DAT_febe8ba7 = '\0';
    uVar7 = 0;
    uVar9 = 0;
    do {
      uVar8 = uVar7;
      if (f33_output_slot_enables_bank0[uVar7] != 'Z') {
        uVar8 = uVar9;
      }
      uVar3 = uVar7 + 1;
      iVar1 = uVar7 - 4;
      uVar7 = uVar3;
      uVar9 = uVar8;
    } while (iVar1 < 0 != ((int)uVar3 < 0 && -1 < iVar1));
    DAT_febe8bae = (byte)uVar8;
    DAT_febe8ba0 = ~DAT_febe8bae;
  }
  iVar1 = (int)(short)uVar8;
  DAT_febe8bee = f33_output_slot_codes_bank0[iVar1 * 3];
  DAT_febe8bf0 = f33_output_slot_codes_bank0[iVar1 * 3 + 1];
  uVar6 = f33_output_slot_codes_bank0[iVar1 * 3 + 2];
  DAT_febe8bf2 = uVar6;
  if ((*(uint *)(((undefined *)camry_host_ptr(0x30d6cu)) + (uVar8 >> 5) * 4) >> (uVar8 & 0x1f) & 1) != 0) {
    if (uVar5 < DAT_febe8bee) {
      DAT_febe8bee = uVar5;
    }
    uVar4 = uVar2;
    if (uVar2 <= DAT_febe8bee) {
      uVar4 = DAT_febe8bee;
    }
    DAT_febe8bee = uVar4;
    if (uVar5 < DAT_febe8bf0) {
      DAT_febe8bf0 = uVar5;
    }
    uVar4 = uVar2;
    if (uVar2 <= DAT_febe8bf0) {
      uVar4 = DAT_febe8bf0;
    }
    DAT_febe8bf0 = uVar4;
    if (uVar5 < uVar6) {
      uVar6 = uVar5;
    }
    DAT_febe8bf2 = uVar2;
    if (uVar2 <= uVar6) {
      DAT_febe8bf2 = uVar6;
    }
  }
  DAT_febe8bb0 = DAT_febe8b88;
  uVar8 = (uint)DAT_febe8baf;
  uVar5 = DAT_febe8b9c;
  if (0x7fff < DAT_febe8b9c) {
    uVar5 = 0x8000;
  }
  if (uVar5 < 0x4000) {
    uVar5 = 0x4000;
  }
  uVar2 = 0x8000 - uVar5;
  if ((uVar8 != (byte)~DAT_febe8ba1) || (DAT_febe8bad != '\0')) {
    DAT_febe8bad = '\0';
    uVar7 = 0;
    uVar9 = 0;
    do {
      uVar8 = uVar7;
      if (f33_output_slot_enables_bank1[uVar7] != 'Z') {
        uVar8 = uVar9;
      }
      uVar3 = uVar7 + 1;
      iVar1 = uVar7 - 4;
      uVar7 = uVar3;
      uVar9 = uVar8;
    } while (iVar1 < 0 != ((int)uVar3 < 0 && -1 < iVar1));
    DAT_febe8baf = (byte)uVar8;
    DAT_febe8ba1 = ~DAT_febe8baf;
  }
  iVar1 = (int)(short)uVar8;
  DAT_febe8bf4 = f33_output_slot_codes_bank1[iVar1 * 3];
  DAT_febe8bf6 = f33_output_slot_codes_bank1[iVar1 * 3 + 1];
  uVar6 = f33_output_slot_codes_bank1[iVar1 * 3 + 2];
  DAT_febe8bf8 = uVar6;
  if ((*(uint *)(((undefined *)camry_host_ptr(0x30d6cu)) + (uVar8 >> 5) * 4) >> (uVar8 & 0x1f) & 1) != 0) {
    if (uVar5 < DAT_febe8bf4) {
      DAT_febe8bf4 = uVar5;
    }
    uVar4 = uVar2;
    if (uVar2 <= DAT_febe8bf4) {
      uVar4 = DAT_febe8bf4;
    }
    DAT_febe8bf4 = uVar4;
    if (uVar5 < DAT_febe8bf6) {
      DAT_febe8bf6 = uVar5;
    }
    uVar4 = uVar2;
    if (uVar2 <= DAT_febe8bf6) {
      uVar4 = DAT_febe8bf6;
    }
    DAT_febe8bf6 = uVar4;
    if (uVar5 < uVar6) {
      uVar6 = uVar5;
    }
    DAT_febe8bf8 = uVar2;
    if (uVar2 <= uVar6) {
      DAT_febe8bf8 = uVar6;
    }
  }
  DAT_febe8bb1 = DAT_febe8b89;
  return;
}



/* Low8 slot<5 copies three u16 codes per bank; does not activate slot. Context low16<3 writes
   directly, otherwise uses existing FFC0 priority mask pair. No code clamp here. */

void f33_write_phase_output_slot_pair(ushort context,uchar slot,ushort *first,ushort *second)

{
  int iVar1;
  uint saved_mask;
  
  if (slot < 5) {
    iVar1 = (int)(short)(ushort)slot;
    if (context < 3) {
      f33_output_slot_codes_bank0[iVar1 * 3] = *first;
      f33_output_slot_codes_bank0[iVar1 * 3 + 1] = first[1];
      f33_output_slot_codes_bank0[iVar1 * 3 + 2] = first[2];
      f33_output_slot_codes_bank1[iVar1 * 3] = *second;
      f33_output_slot_codes_bank1[iVar1 * 3 + 1] = second[1];
      f33_output_slot_codes_bank1[iVar1 * 3 + 2] = second[2];
    }
    else {
      saved_mask = f33_priority_mask_enter(0xffc0);
      f33_output_slot_codes_bank0[iVar1 * 3] = *first;
      f33_output_slot_codes_bank0[iVar1 * 3 + 1] = first[1];
      f33_output_slot_codes_bank0[iVar1 * 3 + 2] = first[2];
      f33_output_slot_codes_bank1[iVar1 * 3] = *second;
      f33_output_slot_codes_bank1[iVar1 * 3 + 1] = second[1];
      f33_output_slot_codes_bank1[iVar1 * 3 + 2] = second[2];
      f33_priority_mask_restore(saved_mask);
    }
  }
  return;
}



/* Low8 slot<5 writes enable5A in both banks. Only changed flags dirty that bank selector; triplets
   and current selected index remain retained until57A5A. */

void f33_activate_phase_output_slot_pair(uchar slot)

{
  uint uVar1;
  uchar uVar2;
  
  uVar1 = (uint)slot;
  if (uVar1 < 5) {
    uVar2 = f33_output_slot_enables_bank0[uVar1];
    if (uVar2 != 'Z') {
      uVar2 = 'Z';
      f33_output_slot_enables_bank0[uVar1] = 'Z';
      DAT_febe8ba7 = 0x5a;
    }
    if (f33_output_slot_enables_bank1[uVar1] != 'Z') {
      f33_output_slot_enables_bank1[uVar1] = uVar2;
      DAT_febe8bad = uVar2;
    }
  }
  return;
}



/* Low8 slot<5 writes enable0 in both banks. Only changed flags dirty that bank selector; triplets
   and current selected index remain retained until57A5A. */

void f33_release_phase_output_slot_pair(uchar slot)

{
  uint uVar1;
  
  uVar1 = (uint)slot;
  if (uVar1 < 5) {
    if (f33_output_slot_enables_bank0[uVar1] != '\0') {
      f33_output_slot_enables_bank0[uVar1] = '\0';
      DAT_febe8ba7 = 0x5a;
    }
    if (f33_output_slot_enables_bank1[uVar1] != '\0') {
      f33_output_slot_enables_bank1[uVar1] = '\0';
      DAT_febe8bad = 0x5a;
    }
  }
  return;
}



/* Low8 slot<5 copies three u16 codes in this bank without activation. Context low16<3 writes
   directly, otherwise existing FFC0 priority mask pair; no clamp or all-interrupt atomicity claim.
    */

void f33_write_phase_output_slot_bank0(ushort context,uchar slot,ushort *codes)

{
  int iVar1;
  uint saved_mask;
  
  if (slot < 5) {
    iVar1 = (int)(short)(ushort)slot;
    if (context < 3) {
      f33_output_slot_codes_bank0[iVar1 * 3] = *codes;
      f33_output_slot_codes_bank0[iVar1 * 3 + 1] = codes[1];
      f33_output_slot_codes_bank0[iVar1 * 3 + 2] = codes[2];
    }
    else {
      saved_mask = f33_priority_mask_enter(0xffc0);
      f33_output_slot_codes_bank0[iVar1 * 3] = *codes;
      f33_output_slot_codes_bank0[iVar1 * 3 + 1] = codes[1];
      f33_output_slot_codes_bank0[iVar1 * 3 + 2] = codes[2];
      f33_priority_mask_restore(saved_mask);
    }
  }
  return;
}



/* Low8 slot<5 writes enable5A in first bank. Only changed flags dirty that bank selector; triplets
   and current selected index remain retained until57A5A. */

void f33_activate_phase_output_slot_bank0(uchar slot)

{
  if ((slot < 5) && (f33_output_slot_enables_bank0[slot] != 'Z')) {
    f33_output_slot_enables_bank0[slot] = 'Z';
    DAT_febe8ba7 = 0x5a;
  }
  return;
}



/* Low8 slot<5 writes enable0 in first bank. Only changed flags dirty that bank selector; triplets
   and current selected index remain retained until57A5A. */

void f33_release_phase_output_slot_bank0(uchar slot)

{
  if ((slot < 5) && (f33_output_slot_enables_bank0[slot] != '\0')) {
    f33_output_slot_enables_bank0[slot] = '\0';
    DAT_febe8ba7 = 0x5a;
  }
  return;
}



/* Low8 slot<5 copies three u16 codes in this bank without activation. Context low16<3 writes
   directly, otherwise existing FFC0 priority mask pair; no clamp or all-interrupt atomicity claim.
    */

void f33_write_phase_output_slot_bank1(ushort context,uchar slot,ushort *codes)

{
  int iVar1;
  uint saved_mask;
  
  if (slot < 5) {
    iVar1 = (int)(short)(ushort)slot;
    if (context < 3) {
      f33_output_slot_codes_bank1[iVar1 * 3] = *codes;
      f33_output_slot_codes_bank1[iVar1 * 3 + 1] = codes[1];
      f33_output_slot_codes_bank1[iVar1 * 3 + 2] = codes[2];
    }
    else {
      saved_mask = f33_priority_mask_enter(0xffc0);
      f33_output_slot_codes_bank1[iVar1 * 3] = *codes;
      f33_output_slot_codes_bank1[iVar1 * 3 + 1] = codes[1];
      f33_output_slot_codes_bank1[iVar1 * 3 + 2] = codes[2];
      f33_priority_mask_restore(saved_mask);
    }
  }
  return;
}



/* Low8 slot<5 writes enable5A in second bank. Only changed flags dirty that bank selector; triplets
   and current selected index remain retained until57A5A. */

void f33_activate_phase_output_slot_bank1(uchar slot)

{
  uint uVar1;
  
  uVar1 = (uint)slot;
  if ((uVar1 < 5) && (f33_output_slot_enables_bank1[uVar1] != 'Z')) {
    f33_output_slot_enables_bank1[uVar1] = 'Z';
    DAT_febe8bad = 0x5a;
  }
  return;
}



/* Low8 slot<5 writes enable0 in second bank. Only changed flags dirty that bank selector; triplets
   and current selected index remain retained until57A5A. */

void f33_release_phase_output_slot_bank1(uchar slot)

{
  uint uVar1;
  
  uVar1 = (uint)slot;
  if ((uVar1 < 5) && (f33_output_slot_enables_bank1[uVar1] != '\0')) {
    f33_output_slot_enables_bank1[uVar1] = '\0';
    DAT_febe8bad = 0x5a;
  }
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_57dec(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_57dee(void)

{
  return;
}



/* Forward selected triplets8BEE/F0/F2 and8BF4/F6/F8 through669DA and66A40 into halfword compare
   staging. No arbitration, recomputation or hardware commit here. Native nonzero tail from5E280 and
   full staging-only5E202(2,0101) verify scoped transform, retention and arbitration effects. No
   fresh acquisition, upstream nonzero regulation or physical PWM claim. */

void f33_stage_live_phase_halfword_compares(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  FUN_000669da(DAT_febe8bee,DAT_febe8bf0,DAT_febe8bf2);
  FUN_00066a40((*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x2c0c)))),(*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x2c0a)))),
               (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x2c08)))));
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_57e14(void)

{
  return;
}



void FUN_00057e16(void)

{
  DAT_febe8bfa = 1;
  DAT_febe8bfb = 2;
  DAT_febe8bfc = 0;
  return;
}



void FUN_00057e26(void)

{
  char cVar1;
  
  cVar1 = DAT_febe8bfc;
  switch(DAT_febe8bfa) {
  case 0:
    if (DAT_febee8cc == 0x600) {
      DAT_febe8bfa = 3;
      DAT_febe8bfb = '\x02';
    }
    else {
      cVar1 = '\0';
    }
    break;
  case 1:
    if (DAT_febee8cc == 0x600) {
      DAT_febe8bfa = 2;
      DAT_febe8bfb = '\x02';
    }
    else {
      cVar1 = '\x01';
    }
    break;
  case 2:
    if (DAT_febee8cc != 0x600) {
      DAT_febe8bfa = 1;
      DAT_febe8bfc = 1;
      return;
    }
    goto LAB_00057e80;
  case 3:
    if (DAT_febee8cc != 0x600) {
      DAT_febe8bfa = 0;
      DAT_febe8bfc = 0;
      return;
    }
LAB_00057e80:
    cVar1 = DAT_febe8bfb;
    if (DAT_febe8bfb == '\x02') {
      cVar1 = DAT_febe8bfc;
    }
    break;
  default:
    DAT_febe8bfa = 1;
  }
  DAT_febe8bfc = cVar1;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_57eb2(void)

{
  return;
}



/* Single constant publisher: DAT_febe5f48 = 1; Shape-classified from the canonical corpus; the
   target cell is not yet named, so the written state's meaning is unknown. */

void FUN_00057eb4(void)

{
  DAT_febe5f48 = 1;
  return;
}



void FUN_00057ebc(void)

{
  if (((DAT_00030d74 < DAT_febe7da6) || (DAT_febe7da6 < DAT_00030d76)) &&
     ((DAT_00030d74 < DAT_febe7da8 || (DAT_febe7da8 < DAT_00030d76)))) {
    DAT_febe5f48 = true;
    if (DAT_febe7db0 <= DAT_00030d70) {
      DAT_febe5f48 = DAT_febe7db0 < DAT_00030d72;
    }
  }
  else {
    DAT_febe5f48 = false;
  }
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_57efc(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_57fce(void)

{
  return;
}


