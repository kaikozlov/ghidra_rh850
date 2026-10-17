#include "common.h"


void FUN_0007c082(ushort param_1)

{
  ushort uVar1;
  
  param_1 = param_1 & 0xff;
  uVar1 = (ushort)DAT_0002183d;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe3de5u + (uint32_t)((short)param_1 * 6) * 1u)))) = 0xf;
  FUN_0007bf10(param_1,0);
  FUN_0007c010(param_1);
  FUN_0007a02c(uVar1 + param_1 & 0xff);
  return;
}



void FUN_0007c0b4(ushort param_1)

{
  ushort uVar1;
  
  param_1 = param_1 & 0xff;
  uVar1 = (ushort)DAT_0002183d;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe3de5u + (uint32_t)((short)param_1 * 6) * 1u)))) = 0x1e;
  FUN_0007a050(uVar1 + param_1 & 0xff);
  FUN_0007bf10(param_1,0);
  FUN_0007c010(param_1);
  return;
}



void FUN_0007c43c(void)

{
  uint32_t puVar1;
  int iVar2;
  char cVar3;
  
  puVar1 = 0xfebeb800u;
  if (DAT_febe4fb0 == 'K') {
    return;
  }
  cVar3 = DAT_febe4fb0;
  if (DAT_febe4fb0 == '\x1e') {
LAB_0007c45a:
    puVar1 = 0xfebeb800u;
    iVar2 = FUN_00083172();
    if (iVar2 == 0) goto LAB_0007c470;
    cVar3 = cVar3 + '\x0f';
  }
  else if (DAT_febe4fb0 != '-') {
    cVar3 = '\x1e';
    goto LAB_0007c45a;
  }
  iVar2 = FUN_0007c352();
  if (iVar2 == 0) {
    cVar3 = 'K';
  }
LAB_0007c470:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6850))))) = cVar3;
  return;
}



void FUN_0007c478(void)

{
  byte bVar1;
  byte bVar2;
  
  bVar1 = DAT_0002183c;
  for (bVar2 = 0; bVar2 < bVar1; bVar2 = bVar2 + 1) {
    FUN_00081290(bVar2);
    FUN_0008132e(bVar2);
    FUN_000812be(bVar2);
  }
  return;
}



void FUN_0007c4a2(void)

{
  byte bVar1;
  byte bVar2;
  
  bVar1 = DAT_0002183c;
  for (bVar2 = 0; bVar2 < bVar1; bVar2 = bVar2 + 1) {
    FUN_0008132e(bVar2);
    FUN_000812be(bVar2);
  }
  return;
}



void FUN_0007c50a(void)

{
  char cVar1;
  ushort uVar2;
  ushort uVar3;
  undefined1 uVar4;
  int iVar5;
  
  cVar1 = DAT_0002183e;
  uVar3 = (ushort)DAT_0002183c;
  if (((DAT_febe4fb0 == '\x1e') || (DAT_febe4fb0 == '-')) || (DAT_febe4fb0 == 'K')) {
    for (uVar2 = 0; uVar2 < uVar3; uVar2 = uVar2 + 1 & 0xff) {
      iVar5 = (short)uVar2 * 6;
      if (cVar1 == -1) {
LAB_0007c550:
        uVar4 = 0x1e;
      }
      else {
        uVar4 = 0x2d;
        if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe3de8u + (uint32_t)(iVar5) * 1u)))) ^ (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe3de7u + (uint32_t)(iVar5) * 1u))))) == 0xff) &&
           ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe3de7u + (uint32_t)(iVar5) * 1u)))) == 0)) goto LAB_0007c550;
      }
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe3de6u + (uint32_t)(iVar5) * 1u)))) = uVar4;
    }
  }
  else {
    uVar4 = 0x2d;
    if (((int8_t)DAT_0002183e) == -1) {
      uVar4 = 0x1e;
    }
    for (uVar2 = 0; uVar2 < uVar3; uVar2 = uVar2 + 1 & 0xff) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe3de6u + (uint32_t)((short)uVar2 * 6) * 1u)))) = uVar4;
    }
  }
  DAT_febe4fb0 = 0x2d;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_7c600(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_7c602(void)

{
  return;
}



undefined1 FUN_0007c604(undefined4 param_1,undefined1 param_2)

{
  return param_2;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_7c60a(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_7c60c(void)

{
  return;
}



uint FUN_0007c60e(uint param_1)

{
  uint uVar1;
  
  uVar1 = (uint)((param_1 & 1) != 0);
  if ((param_1 >> 1 & 1) != 0) {
    uVar1 = uVar1 | 2;
  }
  if ((param_1 >> 2 & 1) != 0) {
    uVar1 = uVar1 | 4;
  }
  if ((param_1 >> 5 & 1) != 0) {
    uVar1 = uVar1 | 0x20;
  }
  if ((param_1 >> 7 & 1) != 0) {
    uVar1 = uVar1 | 0x80;
  }
  if ((param_1 >> 8 & 1) != 0) {
    uVar1 = uVar1 | 0x100;
  }
  if ((param_1 >> 9 & 1) != 0) {
    uVar1 = uVar1 | 0x200;
  }
  return uVar1;
}



uint FUN_0007c6c4(undefined2 param_1)

{
  uint32_t puVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  
  puVar1 = 0x23dfcu;
  uVar3 = (uint)DAT_0002183c;
  uVar4 = 0xff;
  uVar2 = FUN_0008144e(param_1);
  if (uVar2 < uVar3) {
    uVar4 = (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x25bf))))) + uVar2 & 0xff;
  }
  return uVar4;
}



uint FUN_0007c6e8(undefined2 param_1)

{
  uint32_t puVar1;
  uint uVar2;
  
  puVar1 = 0x23dfcu;
  uVar2 = FUN_000813e4(param_1);
  if (uVar2 < (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x25c0)))))) {
    uVar2 = (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x25bf))))) + uVar2 & 0xff;
  }
  else {
    uVar2 = 0xff;
  }
  return uVar2;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_7c70e(void)

{
  return;
}



void FUN_0007c830(uchar param_1)

{
  char cVar1;
  
  cVar1 = DAT_00021ba9 + param_1;
  f33_request_logical_controller_run_stop(param_1,'\x02');
  FUN_0007eaf2(cVar1,1);
  FUN_000832da(cVar1,1);
  return;
}



void FUN_0007c880(char param_1)

{
  char cVar1;
  
  cVar1 = DAT_00021ba9 + param_1;
  FUN_00080f6c(param_1,3);
  FUN_0007eaf2(cVar1,2);
  FUN_000832da(cVar1,2);
  return;
}



int FUN_0007c96c(undefined1 param_1,undefined1 param_2)

{
  int iVar1;
  
  iVar1 = FUN_0007fa3a(param_1,param_2);
  if (iVar1 != 2) {
    FUN_0007cd60(param_1);
  }
  return iVar1;
}



void FUN_0007cc60(byte param_1,char param_2)

{
  uint32_t puVar1;
  uint32_t puVar2;
  uint uVar3;
  undefined4 uVar4;
  uint uVar5;
  
  puVar1 = 0xfebeb800u;
  puVar2 = 0x23dfcu;
  uVar3 = (uint)param_1;
  f33_request_logical_controller_run_stop(param_1,'\x03');
  FUN_0007c082(uVar3);
  FUN_0007fafa(uVar3);
  if ((*((short *)camry_host_ptr((uint32_t)(puVar1 + uVar3 * 4 + -0x6edc)))) == 0x2fd) {
    uVar5 = (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x2253))))) + uVar3 & 0xff;
    if (param_2 == '\x01') {
      uVar4 = 3;
    }
    else {
      uVar4 = 5;
    }
    FUN_000832da(uVar5,uVar4);
    if ((*((short *)camry_host_ptr((uint32_t)(puVar1 + uVar3 * 8 + -0x6ee4)))) == 0xff) {
      FUN_0007eaf2(uVar5,1);
    }
  }
  return;
}



void FUN_0007cce4(char param_1,undefined2 param_2)

{
  char cVar1;
  
  cVar1 = DAT_00021ba9 + param_1;
  FUN_00080066(param_1,0x100);
  FUN_0008156c(param_1);
  FUN_0007cdda(cVar1,param_2);
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_7cf6c(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_7cf6e(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_7cf70(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_7cf72(void)

{
  return;
}



/* Constant source: return 0; shape-classified from the canonical corpus. Callers receive this
   literal directly; its meaning is not recovered. */

undefined4 f33_return_const_0_7cf74(void)

{
  return 0;
}



int FUN_0007cf78(undefined4 param_1,short param_2)

{
  return (int)param_2;
}



/* Constant source: return 0; shape-classified from the canonical corpus. Callers receive this
   literal directly; its meaning is not recovered. */

undefined4 f33_return_const_0_7cf7e(void)

{
  return 0;
}



uint FUN_0007cf86(uint param_1)

{
  uint uVar1;
  
  uVar1 = (uint)((param_1 & 1) != 0);
  if ((param_1 >> 1 & 1) != 0) {
    uVar1 = uVar1 | 2;
  }
  if ((param_1 >> 2 & 1) != 0) {
    uVar1 = uVar1 | 4;
  }
  if ((param_1 >> 5 & 1) != 0) {
    uVar1 = uVar1 | 0x20;
  }
  if ((param_1 >> 7 & 1) != 0) {
    uVar1 = uVar1 | 0x80;
  }
  if ((param_1 & 0x300) != 0) {
    uVar1 = uVar1 | 0x200;
  }
  if ((param_1 >> 3 & 1) == 0) {
    if ((param_1 >> 4 & 1) == 0) {
      if ((param_1 >> 6 & 1) != 0) {
        uVar1 = uVar1 | 0x40;
      }
      return uVar1;
    }
    return uVar1 | 0x10;
  }
  return uVar1 | 8;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_7d014(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_7d016(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_7d018(void)

{
  return;
}



byte FUN_0007d0ea(uint param_1)

{
  uchar *puVar1;
  byte bVar2;
  
  param_1 = param_1 & 0xffff;
  bVar2 = f33_com_tx_pdu_flags[param_1] & 0x33;
  if (param_1 < DAT_00021c56) {
    puVar1 = f33_com_tx_pending_and_group_state + 3;
  }
  else {
    puVar1 = ((undefined *)camry_host_ptr(0xfebe4a42u));
  }
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22148u + (uint32_t)(param_1) * 1u)))) & puVar1[(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x226c2u + (uint32_t)(param_1 * 8) * 1u))))]) != 0) {
    bVar2 = bVar2 | 0x80;
  }
  return bVar2;
}



void FUN_0007d608(uint param_1)

{
  ushort uVar1;
  int iVar2;
  short sVar3;
  ushort uVar4;
  
  sVar3 = DAT_00021c56;
  iVar2 = (param_1 & 0xff) * 4;
  uVar4 = *(ushort *)(((undefined *)camry_host_ptr(0x22144u)) + iVar2);
  uVar1 = *(short *)(((undefined *)camry_host_ptr(0x22146u)) + iVar2) + uVar4;
  for (; uVar4 < uVar1; uVar4 = uVar4 + 1) {
    iVar2 = (uint)(ushort)(uVar4 - sVar3) * 2;
    *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe49deu)) + iVar2) = 0;
    *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe4988u)) + iVar2) = 0;
  }
  return;
}



void FUN_0007d646(int param_1)

{
  undefined1 uVar1;
  uint uVar2;
  uint uVar3;
  
  uVar3 = (uint)DAT_00021c6e;
  for (uVar2 = 0; uVar2 < uVar3; uVar2 = uVar2 + 1 & 0xff) {
    uVar1 = (*((undefined1 *)camry_host_ptr((uint32_t)(uVar2 + uVar3 + param_1))));
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a43u + (uint32_t)(uVar2) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a44u + (uint32_t)(uVar2) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a41u + (uint32_t)(uVar2) * 1u)))) = uVar1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a42u + (uint32_t)(uVar2) * 1u)))) = uVar1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a45u + (uint32_t)(uVar2) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a46u + (uint32_t)(uVar2) * 1u)))) = 0;
  }
  return;
}



void FUN_0007d67c(void)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = (uint)DAT_00021c6e;
  for (uVar1 = 0; uVar1 < uVar2; uVar1 = uVar1 + 1 & 0xff) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a42u + (uint32_t)(uVar1) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a44u + (uint32_t)(uVar1) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a46u + (uint32_t)(uVar1) * 1u)))) = 0;
  }
  return;
}



void FUN_0007d69e(int param_1)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = (uint)DAT_00021c6e;
  for (uVar1 = 0; uVar1 < uVar2; uVar1 = uVar1 + 1 & 0xff) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a43u + (uint32_t)(uVar1) * 1u)))) = (*((undefined1 *)camry_host_ptr((uint32_t)(uVar2 + uVar1 + param_1))));
  }
  return;
}



void FUN_0007d6c2(int param_1)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = (uint)DAT_00021c6e;
  for (uVar1 = 0; uVar1 < uVar2; uVar1 = uVar1 + 1 & 0xff) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a45u + (uint32_t)(uVar1) * 1u)))) = (*((undefined1 *)camry_host_ptr((uint32_t)(uVar2 + uVar1 + param_1))));
  }
  return;
}



/* Constant source: return 1; shape-classified from the canonical corpus. Callers receive this
   literal directly; its meaning is not recovered. */

undefined4 f33_return_const_1_7d800(void)

{
  return 1;
}



void FUN_0007d880(void)

{
  FUN_0007d804(1);
  return;
}



void FUN_0007d88e(void)

{
  FUN_0007e3bc();
  FUN_0007d67c();
  return;
}



void FUN_0007d89e(void)

{
  FUN_0007d804(0x20);
  return;
}



undefined4 FUN_0007dab6(uint param_1,char param_2)

{
  uchar *puVar1;
  
  if (param_2 == '\0') {
    puVar1 = f33_com_tx_pending_and_group_state + 1;
  }
  else {
    puVar1 = f33_com_tx_pending_and_group_state;
  }
  puVar1[param_1 >> 3 & 0xff] = puVar1[param_1 >> 3 & 0xff] | (byte)(1 << (param_1 & 7));
  return 0;
}



/* Select admitted event before periodic request, zero minimum delay, active group and valid clear
   inhibit pair. Return2 event,1 periodic,-20 none. */

int f33_select_admissible_com_tx(uchar group,ushort *selected_pdu)

{
  short sVar1;
  ushort uVar2;
  byte bVar3;
  uchar uVar4;
  uchar uVar5;
  uint32_t puVar6;
  uint32_t puVar7;
  uint uVar8;
  int iVar9;
  uint uVar10;
  undefined1 uVar11;
  uint uVar12;
  
  puVar6 = 0xfebeb800u;
  puVar7 = 0x23dfcu;
  uVar8 = (uint)group;
  iVar9 = -0x14;
  uVar11 = 0;
  uVar12 = (uint)*(ushort *)(((undefined *)camry_host_ptr(0x22140u)) + uVar8 * 4);
  sVar1 = *(short *)(((undefined *)camry_host_ptr(0x22142u)) + uVar8 * 4);
  uVar2 = *(ushort *)(((undefined *)camry_host_ptr(0x22140u)) + uVar8 * 4);
  bVar3 = f33_com_tx_pending_and_group_state[uVar8 + 3];
  uVar4 = f33_com_tx_pending_and_group_state[uVar8 + 4];
  uVar5 = f33_com_tx_pending_and_group_state[uVar8 + 5];
  do {
    if ((ushort)(sVar1 + uVar2) <= uVar12) {
      return iVar9;
    }
    uVar8 = uVar12 >> 3 & 0xff;
    uVar10 = 1 << (uVar12 & 7) & 0xff;
    if ((uVar5 == '\x01') && (((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(uVar8 - 0x6dc7))))) & uVar10) != 0)) {
      uVar11 = 0x40;
      iVar9 = 1;
    }
    if ((uVar4 == '\x01') && (((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(uVar8 - 0x6dc6))))) & uVar10) != 0)) {
      uVar11 = 0x80;
      iVar9 = 2;
LAB_0007dd18:
      if (((*((short *)camry_host_ptr((uint32_t)(puVar6 + uVar12 * 2 + -0x6e88)))) == 0) &&
         (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(uVar12 - 0x1cb4))))) & bVar3) != 0)) {
        if (((byte)((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(uVar8 - 0x6dcb))))) ^ (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(uVar8 - 0x6dcc)))))) & uVar10) == 0) {
          FUN_000833d6();
        }
        else if ((uVar10 & (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(uVar8 - 0x6dcc)))))) == 0) {
          *selected_pdu = (ushort)uVar12;
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x684f))))) = uVar11;
          return iVar9;
        }
      }
      iVar9 = -0x14;
    }
    else if (iVar9 != -0x14) goto LAB_0007dd18;
    uVar12 = uVar12 + 1 & 0xffff;
  } while( true );
}



void FUN_0007dd64(uint param_1,char param_2)

{
  ushort uVar1;
  
  param_1 = param_1 & 0xffff;
  uVar1 = 0;
  if ((DAT_00021c74 != '\0') || (uVar1 = *(ushort *)(((undefined *)camry_host_ptr(0x21c64u)) + param_1 * 2), uVar1 == 0)) {
    if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x226c6u + (uint32_t)(param_1 * 8) * 1u)))) & 1) == 0) {
      return;
    }
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x21c77u + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x226c2u + (uint32_t)(param_1 * 8) * 1u))))) * 1u)))) != '\x01') {
      return;
    }
    if (((param_2 == -0x80) || ((param_2 == '@' && (DAT_00021c71 == '\0')))) &&
       (uVar1 = DAT_00021c5a, DAT_00021c72 != '\x01')) {
      uVar1 = *(ushort *)(((undefined *)camry_host_ptr(0x21c60u)) + param_1 * 2);
    }
    if (uVar1 == 0) {
      return;
    }
  }
  f33_com_tx_minimum_delay_countdowns[param_1] = uVar1;
  return;
}



void FUN_0007de52(uint param_1,char param_2)

{
  char cVar1;
  short sVar2;
  
  param_1 = param_1 & 0xffff;
  sVar2 = 0;
  if (param_2 == '@') {
    cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x21c76u + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x226c2u + (uint32_t)(param_1 * 8) * 1u))))) * 1u))));
  }
  else {
    cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x21c78u + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x226c2u + (uint32_t)(param_1 * 8) * 1u))))) * 1u))));
  }
  if (cVar1 != '\x01') {
    if (cVar1 != '\x02') {
      return;
    }
    sVar2 = *(short *)(((undefined *)camry_host_ptr(0x21c64u)) + param_1 * 2);
  }
  FUN_0007ddd8(param_1,sVar2,sVar2 == 0);
  return;
}



void FUN_0007dee6(uint param_1)

{
  byte bVar1;
  uint uVar2;
  
  uVar2 = param_1 >> 3 & 0xff;
  bVar1 = (byte)(1 << (param_1 & 7)) ^ 0xff;
  f33_com_tx_pending_and_group_state[uVar2] = f33_com_tx_pending_and_group_state[uVar2] & bVar1;
  f33_com_tx_pending_and_group_state[uVar2 + 1] =
       f33_com_tx_pending_and_group_state[uVar2 + 1] & bVar1;
  return;
}



/* Apply group transitions, service countdowns, then bounded dispatch. Exact21C5E allows one attempt
   per group per invocation. Native periodic scheduler cases reach real classic and protected
   snapshot admission. Queue-full preserves COM pending; occupied SecOC generation consumes it.
   Group enable/disable transitions remain static. */

void f33_service_com_tx_publication(void)

{
  ushort uVar1;
  undefined8 uVar2;
  int iVar3;
  uint uVar4;
  ushort uVar5;
  uint uVar6;
  
  uVar2 = 0x23dfc00000000;
  uVar4 = (uint)DAT_00021c6e;
  for (uVar6 = 0; uVar6 < uVar4; uVar6 = uVar6 + 1 & 0xff) {
    f33_apply_com_tx_group_transition((uchar)uVar6);
  }
  f33_service_com_tx_countdowns();
  uVar6 = 0;
  do {
    if (uVar4 <= uVar6) {
      return;
    }
    uVar5 = 0;
    uVar1 = (*((ushort *)camry_host_ptr((uint32_t)(uVar6 * 2 + (int)((ulonglong)uVar2 >> 0x20) + -0x219e))));
    do {
      if (uVar1 <= uVar5) break;
      iVar3 = f33_dispatch_one_com_tx((uchar)uVar6);
      uVar5 = uVar5 + 1;
    } while (iVar3 != -0x14);
    if (uVar5 == 0) {
      FUN_0007e046(uVar6,0xc0);
    }
    uVar6 = uVar6 + 1 & 0xff;
  } while( true );
}



void FUN_0007e2ea(uint param_1)

{
  uint uVar1;
  int iVar2;
  uint uVar3;
  
  iVar2 = (param_1 & 0xff) * 4;
  uVar3 = (uint)*(ushort *)(((undefined *)camry_host_ptr(0x22140u)) + iVar2);
  uVar1 = *(ushort *)(((undefined *)camry_host_ptr(0x22142u)) + iVar2) + uVar3;
  for (; uVar3 < (uVar1 & 0xffff); uVar3 = uVar3 + 1 & 0xffff) {
    f33_com_tx_periodic_countdowns[uVar3] = 0;
  }
  return;
}



void FUN_0007e312(void)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = (uint)DAT_00021c70;
  for (uVar1 = 0; uVar1 < uVar2; uVar1 = uVar1 + 1 & 0xff) {
    f33_com_tx_inhibit_pair[uVar1 + 1] = 0xff;
    f33_com_tx_inhibit_pair[uVar1] = '\0';
    f33_com_tx_pending_and_group_state[uVar1 + 1] = '\0';
    f33_com_tx_pending_and_group_state[uVar1] = '\0';
  }
  DAT_febe4fb1 = 0;
  return;
}



void FUN_0007e33e(void)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = 1;
  if (DAT_00021c6f == '\0') {
    uVar2 = (uint)DAT_00021c6e;
  }
  for (uVar1 = 0; uVar1 < uVar2; uVar1 = uVar1 + 1 & 0xff) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a37u + (uint32_t)(uVar1) * 1u)))) = 2;
  }
  return;
}



void FUN_0007e364(void)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = (uint)DAT_00021c56;
  for (uVar1 = 0; uVar1 < uVar2; uVar1 = uVar1 + 1 & 0xffff) {
    f33_com_tx_minimum_delay_countdowns[uVar1] = 0;
  }
  return;
}



void FUN_0007e380(int param_1)

{
  uchar uVar1;
  uint uVar2;
  uint uVar3;
  
  uVar3 = (uint)DAT_00021c6e;
  for (uVar2 = 0; uVar2 < uVar3; uVar2 = uVar2 + 1 & 0xff) {
    uVar1 = (*((uchar *)camry_host_ptr((uint32_t)(uVar2 + param_1))));
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a3fu + (uint32_t)(uVar2) * 1u)))) = 0;
    f33_com_tx_pending_and_group_state[uVar2 + 2] = uVar1;
    f33_com_tx_pending_and_group_state[uVar2 + 3] = uVar1;
    f33_com_tx_pending_and_group_state[uVar2 + 4] = '\x02';
    f33_com_tx_pending_and_group_state[uVar2 + 5] = '\x02';
    *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe4986u)) + uVar2 * 2) = 0;
  }
  return;
}



void FUN_0007e3bc(void)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = (uint)DAT_00021c6e;
  for (uVar1 = 0; uVar1 < uVar2; uVar1 = uVar1 + 1 & 0xff) {
    f33_com_tx_pending_and_group_state[uVar1 + 5] = '\x02';
    f33_com_tx_pending_and_group_state[uVar1 + 4] = '\x02';
    f33_com_tx_pending_and_group_state[uVar1 + 3] = '\0';
  }
  return;
}



/* Constant source: return 1; shape-classified from the canonical corpus. Callers receive this
   literal directly; its meaning is not recovered. */

undefined4 f33_return_const_1_7e4dc(void)

{
  return 1;
}



undefined2 FUN_0007e4e0(undefined4 param_1,undefined4 param_2,undefined2 param_3)

{
  return param_3;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_7e4e6(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_7e4e8(void)

{
  return;
}



void FUN_0007e4ea(uint param_1)

{
  if ((param_1 & 0xff) < (uint)DAT_00021c6e) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a37u + (uint32_t)(param_1 & 0xff) * 1u)))) = 1;
  }
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_7e588(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_7e58a(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_7e58e(void)

{
  return;
}



/* Constant source: return 0xfffffff3; shape-classified from the canonical corpus. Callers receive
   this literal directly; its meaning is not recovered. */

undefined4 f33_return_const_fffffff3_7e590(void)

{
  return 0xfffffff3;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_7e594(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_7e596(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_7e598(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_7e59c(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_7e59e(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_7e5a0(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_7e5a2(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_7e718(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_7e71a(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_7e71c(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_7e71e(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_7e720(void)

{
  return;
}



/* Constant source: return 0; shape-classified from the canonical corpus. Callers receive this
   literal directly; its meaning is not recovered. */

undefined4 f33_return_const_0_7e722(void)

{
  return 0;
}



/* Constant source: return 0; shape-classified from the canonical corpus. Callers receive this
   literal directly; its meaning is not recovered. */

undefined4 f33_return_const_0_7e726(void)

{
  return 0;
}



/* Constant source: return 1; shape-classified from the canonical corpus. Callers receive this
   literal directly; its meaning is not recovered. */

undefined4 f33_return_const_1_7e77e(void)

{
  return 1;
}



/* Single constant publisher: DAT_febe4938 = 0xff; Shape-classified from the canonical corpus; the
   target cell is not yet named, so the written state's meaning is unknown. */

void FUN_0007e7da(void)

{
  DAT_febe4938 = 0xff;
  return;
}



bool FUN_0007e7e4(uint param_1)

{
  if ((param_1 & 0xff) < (uint)DAT_00021be1) {
    return ((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x21be2u + (uint32_t)(param_1 & 0xff) * 1u)))) & DAT_febe493a) != 0;
  }
  return false;
}



undefined4 FUN_0007e88c(uint param_1,undefined1 *param_2)

{
  short sVar1;
  int iVar2;
  undefined1 uVar3;
  
  param_1 = param_1 & 0xff;
  if (DAT_febe4938 != 0x1fe) {
    return 1;
  }
  if (DAT_00021be1 <= param_1) {
    return 1;
  }
  sVar1 = *(short *)(((undefined *)camry_host_ptr(0xfebe492au)) + param_1 * 0x10);
  if (sVar1 == 0xff) {
    uVar3 = 0;
    iVar2 = FUN_0007e7e4(param_1);
    if ((iVar2 == 1) &&
       ((iVar2 = FUN_0007e804(param_1), iVar2 != 0 ||
        (*(short *)(((undefined *)camry_host_ptr(0xfebe4928u)) + param_1 * 0x10) != 0)))) {
      uVar3 = 1;
    }
    goto LAB_0007e8d6;
  }
  if (sVar1 != 0x1fe) {
    if (sVar1 == 0x2fd) {
      uVar3 = 3;
      goto LAB_0007e8d6;
    }
    if (sVar1 == 0x3fc) {
      uVar3 = 4;
      goto LAB_0007e8d6;
    }
    if (sVar1 != 0x5fa) {
      return 1;
    }
  }
  uVar3 = 2;
LAB_0007e8d6:
  *param_2 = uVar3;
  return 0;
}



undefined4 FUN_0007e998(uint param_1)

{
  short sVar1;
  int iVar2;
  undefined4 uVar3;
  
  param_1 = param_1 & 0xff;
  uVar3 = 5;
  if ((DAT_febe4938 == 0x1fe) && (param_1 < DAT_00021be1)) {
    sVar1 = *(short *)(((undefined *)camry_host_ptr(0xfebe492au)) + param_1 * 0x10);
    if (sVar1 == 0xff) {
      uVar3 = 0;
      iVar2 = FUN_0007e7e4(param_1);
      if ((iVar2 == 1) &&
         ((iVar2 = FUN_0007e912(param_1), iVar2 != 0 ||
          (*(short *)(((undefined *)camry_host_ptr(0xfebe4928u)) + param_1 * 0x10) != 0)))) {
        uVar3 = 1;
      }
    }
    else {
      if (sVar1 != 0x1fe) {
        if (sVar1 == 0x2fd) {
          return 3;
        }
        if (sVar1 == 0x3fc) {
          return 4;
        }
        if (sVar1 != 0x5fa) {
          return 5;
        }
      }
      uVar3 = 2;
    }
  }
  return uVar3;
}



void FUN_0007ead0(uint param_1,char param_2)

{
  undefined2 uVar1;
  
  if ((param_1 & 0xff) < (uint)DAT_00021be1) {
    uVar1 = 0x1fe;
    if (param_2 == '\0') {
      uVar1 = 0xff;
    }
    *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe492cu)) + (param_1 & 0xff) * 0x10) = uVar1;
  }
  return;
}



undefined1 FUN_0007eb4c(uint param_1)

{
  if ((param_1 & 0xff) < (uint)DAT_00021be1) {
    return (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x21be2u + (uint32_t)(param_1 & 0xff) * 1u))));
  }
  return 0;
}



undefined1 FUN_0007eb62(uint param_1)

{
  if ((param_1 & 0xff) < (uint)DAT_00021be1) {
    return (char)*(undefined2 *)(((undefined *)camry_host_ptr(0x21bdcu)) + (param_1 & 0xff) * 2);
  }
  return 0;
}



bool FUN_0007eb7c(uint param_1)

{
  uint32_t puVar1;
  int iVar2;
  bool bVar3;
  
  puVar1 = 0xfebeb800u;
  param_1 = param_1 & 0xff;
  bVar3 = false;
  if ((param_1 < DAT_00021be1) && (iVar2 = FUN_0007e7e4(param_1), iVar2 == 1)) {
    bVar3 = (*((short *)camry_host_ptr((uint32_t)(puVar1 + param_1 * 0x10 + -0x6ed4)))) == 0x1fe;
  }
  return bVar3;
}



undefined4 FUN_0007ec96(undefined1 param_1,uint param_2,char param_3)

{
  undefined4 uVar1;
  
  uVar1 = 0x2fd;
  if ((param_3 == '\x01') && ((param_2 & 0xc) != 0)) {
    FUN_0007eeae(param_1);
    uVar1 = 0x1fe;
  }
  return uVar1;
}



void FUN_0007ed16(uint param_1)

{
  if ((param_1 & 0xff) < (uint)DAT_00021be1) {
    *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe492eu)) + (param_1 & 0xff) * 0x10) = 0x1fe;
  }
  return;
}



void FUN_0007ed2e(uint param_1)

{
  if ((param_1 & 0xff) < (uint)DAT_00021be1) {
    *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe492eu)) + (param_1 & 0xff) * 0x10) = 0xff;
  }
  return;
}



void FUN_0007ed4e(uint param_1)

{
  if ((param_1 & 0xff) < (uint)DAT_00021be1) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4937u + (uint32_t)((param_1 & 0xff) * 0x10) * 1u)))) = 0xe1;
  }
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_7ed66(void)

{
  return;
}



/* Constant source: return 0; shape-classified from the canonical corpus. Callers receive this
   literal directly; its meaning is not recovered. */

undefined4 f33_return_const_0_7ed68(void)

{
  return 0;
}



/* Constant source: return 0; shape-classified from the canonical corpus. Callers receive this
   literal directly; its meaning is not recovered. */

undefined4 f33_return_const_0_7ed6c(void)

{
  return 0;
}



/* Constant source: return 0; shape-classified from the canonical corpus. Callers receive this
   literal directly; its meaning is not recovered. */

undefined4 f33_return_const_0_7ed70(void)

{
  return 0;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_7ed74(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_7ed7a(void)

{
  return;
}



/* Constant source: return 1; shape-classified from the canonical corpus. Callers receive this
   literal directly; its meaning is not recovered. */

undefined4 f33_return_const_1_7ed7c(void)

{
  return 1;
}



void FUN_0007ed80(void)

{
  short sVar1;
  short sVar2;
  uint uVar3;
  uint uVar4;
  
  uVar3 = (uint)DAT_00021be1;
  for (uVar4 = 0; uVar4 < uVar3; uVar4 = uVar4 + 1 & 0xff) {
    sVar1 = *(short *)(((undefined *)camry_host_ptr(0xfebe4928u)) + uVar4 * 0x10);
    if (sVar1 != 0) {
      sVar2 = sVar1 + -1;
      if (*(ushort *)(((undefined *)camry_host_ptr(0x21bdeu)) + uVar4 * 2) < (ushort)(sVar1 - 1U)) {
        sVar2 = 0;
      }
      *(short *)(((undefined *)camry_host_ptr(0xfebe4928u)) + uVar4 * 0x10) = sVar2;
    }
  }
  return;
}



void FUN_0007edb8(void)

{
  int iVar1;
  undefined1 uVar2;
  undefined8 uVar3;
  short sVar4;
  int iVar5;
  undefined4 uVar6;
  uint uVar7;
  uint uVar8;
  
  uVar3 = 0x23dfcfebeb800;
  uVar7 = (uint)DAT_00021be1;
  for (uVar8 = 0; uVar8 < uVar7; uVar8 = uVar8 + 1 & 0xff) {
    iVar1 = uVar8 * 0x10 + (int)uVar3;
    sVar4 = (*((short *)camry_host_ptr((uint32_t)(iVar1 + -0x6ed6))));
    if (((int8_t)(*((char *)camry_host_ptr((uint32_t)(iVar1 + -0x6ecb))))) == -0x1f) {
      uVar2 = 0x1e;
      if (sVar4 == 0xff) {
        uVar2 = 0xe1;
      }
      (*((undefined1 *)camry_host_ptr((uint32_t)(iVar1 + -0x6ecc)))) = uVar2;
      (*((undefined1 *)camry_host_ptr((uint32_t)(iVar1 + -0x6ecb)))) = 0x1e;
    }
    iVar5 = FUN_0007e7e4(uVar8);
    if (iVar5 == 0) {
      (*((undefined1 *)camry_host_ptr((uint32_t)(iVar1 + -0x6ec9)))) = 0x1e;
      (*((undefined1 *)camry_host_ptr((uint32_t)(iVar1 + -0x6ecc)))) = 0x1e;
    }
    uVar6 = FUN_0007e912(uVar8);
    if (sVar4 == 0xff) {
      sVar4 = FUN_0007ebae(uVar8,uVar6,iVar5);
    }
    else if (sVar4 == 0x1fe) {
      sVar4 = FUN_0007ec40(uVar8,uVar6,iVar5);
    }
    else if (sVar4 == 0x2fd) {
      sVar4 = FUN_0007ec96(uVar8,uVar6,iVar5);
    }
    else if (sVar4 == 0x3fc) {
      sVar4 = FUN_0007ecb8(uVar8,uVar6,iVar5);
    }
    else if (sVar4 == 0x5fa) {
      sVar4 = FUN_0007ec70(uVar8,uVar6,iVar5);
    }
    (*((short *)camry_host_ptr((uint32_t)(iVar1 + -0x6ed6)))) = sVar4;
  }
  return;
}



void FUN_0007ee6e(void)

{
  FUN_0007ed80();
  FUN_0007edb8();
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_7ee7e(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_7ee80(void)

{
  return;
}



void FUN_0007ef9c(void)

{
  FUN_00083542();
  f33_return_only_stub_8356c();
  return;
}



void FUN_0007eff2(void)

{
  uint32_t puVar1;
  uint32_t puVar2;
  uint uVar3;
  uint uVar4;
  
  puVar1 = 0xfebeb800u;
  puVar2 = 0x23dfcu;
  uVar3 = (uint)DAT_00021b8e;
  for (uVar4 = 0; uVar4 < uVar3; uVar4 = uVar4 + 1 & 0xff) {
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + uVar4 * 8 + -0x6eec)))) = 0xff00;
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(uVar4 - 0x226c))))) == '\0') {
      FUN_00083282(uVar4);
      FUN_000832ae(uVar4);
    }
  }
  return;
}



void FUN_0007f098(uint param_1)

{
  int iVar1;
  int iVar2;
  ushort uVar3;
  
  iVar1 = (param_1 & 0xff) * 8;
  uVar3 = *(ushort *)(((undefined *)camry_host_ptr(0xfebe4916u)) + iVar1);
  if (uVar3 != 0) {
    iVar2 = (param_1 & 0xff) * 2;
    uVar3 = uVar3 - 1;
    if (*(ushort *)(((undefined *)camry_host_ptr(0x21b8cu)) + iVar2) < uVar3) {
      uVar3 = *(ushort *)(((undefined *)camry_host_ptr(0x21b8cu)) + iVar2);
    }
  }
  *(ushort *)(((undefined *)camry_host_ptr(0xfebe4916u)) + iVar1) = uVar3;
  return;
}



void FUN_0007f0c6(uint param_1)

{
  int iVar1;
  
  param_1 = param_1 & 0xff;
  iVar1 = param_1 * 8;
  if ((*(short *)(((undefined *)camry_host_ptr(0xfebe4916u)) + iVar1) == 0) &&
     ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe491bu + (uint32_t)(iVar1) * 1u)))) = 0xe1, ((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4918u + (uint32_t)(iVar1) * 1u))))) != -0x10)) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4918u + (uint32_t)(iVar1) * 1u)))) = 0xf0;
    FUN_0007c060(param_1);
    FUN_00083298(param_1);
  }
  return;
}



void FUN_0007f100(uint param_1)

{
  int iVar1;
  char cVar2;
  uint uVar3;
  
  param_1 = param_1 & 0xff;
  iVar1 = param_1 * 8;
  uVar3 = (uint)DAT_00021b8f;
  if (((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4919u + (uint32_t)(iVar1) * 1u))))) == -0x1f) {
    FUN_0007f0c6(param_1);
  }
  else {
    cVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe491bu + (uint32_t)(iVar1) * 1u))));
    *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe4916u)) + iVar1) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe491au + (uint32_t)(iVar1) * 1u)))) = 0xf0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4918u + (uint32_t)(iVar1) * 1u)))) = 0xf0;
    *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe4914u)) + iVar1) = 0x1fe;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe491bu + (uint32_t)(iVar1) * 1u)))) = 0xf0;
    if (cVar2 != -0x10) {
      FUN_0007c060(param_1);
      FUN_00083282(param_1);
    }
    FUN_000832ae(param_1);
    FUN_0007ef5c(uVar3 + param_1 & 0xff);
  }
  return;
}



void FUN_0007f15e(uint param_1)

{
  int iVar1;
  char cVar2;
  undefined2 uVar3;
  uint32_t puVar4;
  int iVar5;
  uint uVar6;
  char cVar7;
  
  puVar4 = 0x23dfcu;
  param_1 = param_1 & 0xff;
  iVar1 = param_1 * 8;
  cVar7 = -0x10;
  cVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe491au + (uint32_t)(iVar1) * 1u))));
  uVar6 = DAT_00021b8f + param_1 & 0xff;
  iVar5 = FUN_0007e7e4(uVar6);
  if (iVar5 == 1) {
    cVar7 = -0x1f;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe491au + (uint32_t)(iVar1) * 1u)))) = cVar7;
  if (cVar2 != cVar7) {
    if (cVar7 == -0x1f) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4918u + (uint32_t)(iVar1) * 1u)))) = 0xe1;
      uVar3 = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar4 + param_1 * 2 + -0x2270))));
    }
    else {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4918u + (uint32_t)(iVar1) * 1u)))) = 0xf0;
      uVar3 = 0;
    }
    *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe4916u)) + iVar1) = uVar3;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe491bu + (uint32_t)(iVar1) * 1u)))) = 0xf0;
  if (((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4919u + (uint32_t)(iVar1) * 1u))))) == -0x1f) {
    FUN_0007ef30(uVar6);
    FUN_000832c4(param_1);
    FUN_0007f0c6(param_1);
    *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe4914u)) + iVar1) = 0x2fd;
  }
  return;
}



void FUN_0007f20c(void)

{
  undefined8 uVar1;
  uint uVar2;
  uint uVar3;
  
  uVar1 = 0x23dfc00000000;
  uVar2 = (uint)DAT_00021b8e;
  for (uVar3 = 0; uVar3 < uVar2; uVar3 = uVar3 + 1 & 0xff) {
    if ((*((char *)camry_host_ptr((uint32_t)(uVar3 + (int)((ulonglong)uVar1 >> 0x20) + -0x226c)))) == '\0') {
      FUN_0007f098(uVar3);
      FUN_0007f1e2(uVar3);
    }
  }
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_7f364(void)

{
  return;
}



undefined4 FUN_0007f56a(uint param_1)

{
  uint32_t puVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  
  puVar1 = 0x23dfcu;
  if ((f33_logical_controller_request_cache[param_1 & 0xff] == 0x57a8) ||
     (f33_logical_controller_request_cache[param_1 & 0xff] == 0x6b94)) {
    uVar3 = (uint)DAT_00021971;
    for (uVar4 = 0; uVar4 < uVar3; uVar4 = uVar4 + 1 & 0xff) {
      if (((param_1 & 0xff) == (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(uVar4 - 0x2484)))))) &&
         (iVar2 = FUN_000841fc(uVar4), iVar2 != 0)) {
        return 1;
      }
    }
  }
  return 0;
}



void FUN_0007f5ba(uint param_1,uint param_2)

{
  (*((undefined2 *)camry_host_ptr((uint32_t)((&PTR_DAT_00021934)[param_1 & 0xff] + (param_2 & 0xff) * 2)))) =
       *(undefined2 *)(((undefined *)camry_host_ptr(0x2196au)) + (param_1 & 0xff) * 2);
  return;
}



void FUN_0007f5da(uint param_1,uint param_2)

{
  (*((undefined2 *)camry_host_ptr((uint32_t)((&PTR_DAT_00021934)[param_1 & 0xff] + (param_2 & 0xff) * 2)))) = 0;
  return;
}



char FUN_0007f838(undefined1 param_1,char param_2)

{
  int iVar1;
  
  if ((param_2 == -0x6a) || (param_2 == 'Z')) {
    iVar1 = FUN_00080eb0(param_1);
    if (iVar1 == 0) {
      param_2 = -0x5b;
    }
    else if (iVar1 == 2) {
      param_2 = 'Z';
    }
    else if (iVar1 == 1) {
      param_2 = '<';
    }
    else {
      param_2 = -0x3d;
      if (iVar1 == 3) {
        param_2 = '\x1e';
      }
    }
  }
  return param_2;
}



undefined4 FUN_0007fa3a(uint param_1,undefined1 param_2)

{
  int iVar1;
  undefined4 uVar2;
  
  param_1 = param_1 & 0xff;
  uVar2 = 1;
  if (f33_logical_controller_request_cache[param_1] == 0x6d92) {
    f33_logical_controller_request_cache[param_1] = 0x6d92;
    iVar1 = FUN_0007f8c8(param_1,param_2);
    if ((iVar1 == 0) || (iVar1 == 9)) {
      uVar2 = 0;
      f33_logical_controller_request_cache[param_1] = 0x6b94;
    }
    else if (iVar1 == 2) {
      uVar2 = 2;
    }
    else {
      uVar2 = 1;
    }
  }
  return uVar2;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_7fb5c(void)

{
  return;
}



undefined4 FUN_0007fbb0(uint param_1)

{
  ushort uVar1;
  
  uVar1 = f33_logical_controller_request_cache[param_1 & 0xff];
  if (uVar1 == 0x57a8) {
    return 3;
  }
  if (uVar1 != 0x6b94) {
    if (uVar1 != 0x6d92) {
      return 0;
    }
    return 1;
  }
  return 2;
}



uint FUN_0007fbdc(uint param_1,uint param_2)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = 0xff;
  if (((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2195cu + (uint32_t)((short)(param_1 & 0xff) * 6 + ((int)(param_2 & 0xffff) >> 8)) * 1u)))) != 0xff)
     && (uVar1 = (param_2 & 0xff) +
                 (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2195cu + (uint32_t)((short)(param_1 & 0xff) * 6 + ((int)(param_2 & 0xffff) >> 8)) * 1u)))),
        uVar1 < (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x21972u + (uint32_t)(param_1 & 0xff) * 1u)))))) {
    uVar2 = uVar1 & 0xff;
  }
  return uVar2;
}


