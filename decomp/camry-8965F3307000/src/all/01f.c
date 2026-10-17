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



undefined4 FUN_0007c352(void)

{
  char cVar1;
  undefined1 uVar2;
  undefined *puVar3;
  undefined *puVar4;
  uint32_t puVar5;
  undefined4 uVar6;
  int iVar7;
  ushort uVar8;
  undefined4 uVar9;
  ushort uVar10;
  ushort uVar11;
  
  puVar3 = ((undefined *)camry_host_ptr(0xfebeb800u));
  puVar5 = 0x23dfcu;
  uVar8 = (ushort)DAT_0002183c;
  uVar9 = 0;
  uVar11 = 0;
  do {
    if (uVar8 <= uVar11) {
      return uVar9;
    }
    cVar1 = puVar3[(short)uVar11 * 6 + -0x7a1a];
    if (cVar1 != 'K') {
      puVar4 = puVar3;
      if (cVar1 == '\x1e') {
        uVar6 = 0;
LAB_0007c39e:
        iVar7 = FUN_0007c96c(uVar11,uVar6);
        if (iVar7 != 2) {
          uVar10 = (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x25bf))))) + uVar11 & 0xff;
          FUN_0007ead0(uVar10,1);
          puVar3[(short)uVar11 * 6 + -0x7a1a] = 0x4b;
          iVar7 = FUN_0007cd7c(uVar11);
          if (iVar7 == 0x40) {
            puVar3[(short)uVar11 * 6 + -0x7a19] = 1;
            puVar3[(short)uVar11 * 6 + -0x7a18] = 0xfe;
            FUN_0008132e(uVar11);
            FUN_000812be(uVar11);
            uVar6 = 1;
          }
          else if (iVar7 == 8) {
            puVar3[(short)uVar11 * 6 + -0x7a19] = 2;
            puVar3[(short)uVar11 * 6 + -0x7a18] = 0xfd;
            FUN_0008132e(uVar11);
            FUN_000812be(uVar11);
            uVar6 = 2;
          }
          else if (iVar7 == 0x10) {
            uVar6 = 3;
            puVar3[(short)uVar11 * 6 + -0x7a19] = 3;
            puVar3[(short)uVar11 * 6 + -0x7a18] = 0xfc;
          }
          else {
            puVar3[(short)uVar11 * 6 + -0x7a19] = 0;
            puVar3[(short)uVar11 * 6 + -0x7a18] = 0xff;
            puVar3 = puVar4;
            if (iVar7 != 0) goto LAB_0007c42e;
            uVar6 = 0;
          }
          ((void)(uVar10), (void)(uVar6), f33_return_only_stub_83280());
          puVar3 = puVar4;
          goto LAB_0007c42e;
        }
      }
      else {
        if (cVar1 == '-') {
          uVar6 = 1;
          goto LAB_0007c39e;
        }
        uVar2 = 0x2d;
        if (((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x25be)))))) == -1) {
          uVar2 = 0x1e;
        }
        puVar3[(short)uVar11 * 6 + -0x7a1a] = uVar2;
      }
      uVar9 = 1;
      puVar3 = puVar4;
    }
LAB_0007c42e:
    uVar11 = uVar11 + 1 & 0xff;
  } while( true );
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



undefined4 FUN_0007cda0(char param_1)

{
  undefined4 uVar1;
  int iVar2;
  
  iVar2 = ((void)(DAT_00021ba9 + param_1), f33_return_const_0_7cf74());
  uVar1 = 0;
  if (iVar2 != 0) {
    uVar1 = 0x80;
  }
  return uVar1;
}



void FUN_0007cdda(undefined1 param_1,uint param_2)

{
  if ((param_2 & 1) != 0) {
    ((void)(param_1), f33_return_only_stub_7cf6c());
  }
  if ((param_2 >> 1 & 1) != 0) {
    ((void)(param_1), f33_return_only_stub_7cf72());
  }
  if ((param_2 >> 2 & 1) != 0) {
    ((void)(param_1), f33_return_only_stub_7cf70());
  }
  if ((param_2 >> 5 & 1) != 0) {
    ((void)(param_1), f33_return_only_stub_7cf6e());
  }
  if ((param_2 & 0x300) != 0) {
    ((void)(param_1), f33_return_only_stub_7d014());
  }
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



void FUN_0007d01a(int param_1)

{
  int iVar1;
  undefined1 uVar2;
  undefined1 uVar3;
  undefined8 uVar4;
  undefined4 uVar5;
  uint uVar6;
  uint uVar7;
  uint uVar8;
  
  uVar4 = 0x23dfcfebeb800;
  uVar6 = (uint)DAT_00021c6e;
  uVar7 = uVar6;
  for (uVar8 = 0; uVar8 < uVar6; uVar8 = uVar8 + 1 & 0xff) {
    uVar2 = (*((undefined1 *)camry_host_ptr((uint32_t)(uVar8 + param_1))));
    uVar3 = (*((undefined1 *)camry_host_ptr((uint32_t)(uVar7 + param_1))));
    uVar5 = FUN_0007a2da();
    iVar1 = uVar8 + (int)uVar4;
    (*((undefined1 *)camry_host_ptr((uint32_t)(iVar1 + -0x6dc5)))) = uVar2;
    (*((undefined1 *)camry_host_ptr((uint32_t)(iVar1 + -0x6dbf)))) = uVar3;
    ((void)(uVar5), thunk_FUN_0006a4c4());
    uVar7 = uVar7 + 1 & 0xff;
  }
  return;
}



byte FUN_0007d0b8(uint param_1)

{
  ushort uVar1;
  byte bVar2;
  uint32_t puVar3;
  undefined4 uVar4;
  uint uVar5;
  
  puVar3 = 0xfebeb800u;
  uVar1 = *(ushort *)(((undefined *)camry_host_ptr(0x22488u)) + (param_1 & 0xffff) * 2);
  uVar5 = (uint)DAT_00021c54;
  uVar4 = FUN_0007a2da();
  bVar2 = 1;
  if (uVar1 < uVar5) {
    bVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(uVar1 - 0x6ec2)))));
  }
  ((void)(uVar4), thunk_FUN_0006a4c4());
  return bVar2 & 0x23;
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



undefined4
FUN_0007d12a(uint param_1,uint param_2,uint param_3,int param_4,char param_5,uint *param_6)

{
  byte *pbVar1;
  uint uVar2;
  byte bVar3;
  byte bVar4;
  byte bVar5;
  byte bVar6;
  char cVar7;
  ushort uVar8;
  uint32_t puVar9;
  undefined4 uVar10;
  uint uVar11;
  uint uVar12;
  
  puVar9 = 0xfebeb800u;
  uVar12 = param_3 & 0xff;
  uVar8 = *(ushort *)(((undefined *)camry_host_ptr(0x22488u)) + (param_1 & 0xffff) * 2);
  uVar10 = FUN_0007a2da();
  cVar7 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar9 + (uint32_t)(uVar8 - 0x6ec2)))));
  pbVar1 = ((undefined *)camry_host_ptr((uint32_t)(puVar9 + ((param_2 & 0xffff) - 0x6db8))));
  bVar3 = pbVar1[3];
  bVar4 = pbVar1[2];
  bVar5 = pbVar1[1];
  bVar6 = *pbVar1;
  ((void)(uVar10), thunk_FUN_0006a4c4());
  uVar10 = 0x20;
  if (cVar7 < '\0') {
    uVar10 = 0;
  }
  uVar11 = 0xffffffff;
  if (uVar12 < 0x20) {
    uVar11 = (1 << (param_3 & 0x1f)) - 1;
  }
  uVar11 = ((uint)bVar3 | (uint)bVar4 << 8 | (uint)bVar5 << 0x10 | (uint)bVar6 << 0x18) >>
           ((param_4 - (param_4 + uVar12 + 7 & 0xf8)) + 0x20 & 0x1f) & uVar11;
  if ((param_5 == '\x01') && (uVar2 = 1 << (uVar12 - 1 & 0x1f), (uVar2 & uVar11) != 0)) {
    uVar11 = uVar11 | ~(uVar2 - 1);
  }
  if (uVar12 < 9) {
    *(char *)param_6 = (char)uVar11;
  }
  else if (uVar12 < 0x11) {
    *(short *)param_6 = (short)uVar11;
  }
  else {
    *param_6 = uVar11;
  }
  return uVar10;
}



undefined4 FUN_0007d1dc(uint param_1,uint param_2,uint param_3,uint param_4,uint *param_5)

{
  byte *pbVar1;
  char cVar2;
  ushort uVar3;
  uint uVar4;
  uint32_t puVar5;
  undefined4 uVar6;
  char cVar7;
  uint uVar8;
  uint uVar9;
  uint uVar10;
  
  puVar5 = 0xfebeb800u;
  uVar8 = param_3 & 0xff;
  uVar9 = 0xffffffff;
  uVar3 = *(ushort *)(((undefined *)camry_host_ptr(0x22488u)) + (param_1 & 0xffff) * 2);
  cVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2236cu + (uint32_t)(param_1 & 0xffff) * 1u))));
  if (uVar8 < 0x20) {
    uVar9 = (1 << (param_3 & 0x1f)) - 1;
  }
  if (uVar8 < 9) {
    uVar10 = (uint)(byte)*param_5;
  }
  else if (uVar8 < 0x11) {
    uVar10 = (uint)(ushort)*param_5;
  }
  else {
    uVar10 = *param_5;
  }
  uVar6 = FUN_0007a2da();
  if (uVar8 == 1) {
    uVar8 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)((param_2 & 0xffff) - 0x6db8)))));
    uVar9 = (uVar9 & 0xff) << (param_4 & 0x1f) & 0xff;
    if ((*param_5 & 1) == 0) {
      cVar7 = '\x02';
      uVar9 = (uVar9 ^ 0xff) & uVar8;
    }
    else {
      uVar9 = uVar9 | uVar8;
      cVar7 = '\x01';
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)((param_2 & 0xffff) - 0x6db8))))) = (byte)uVar9;
    if ((cVar2 != '\x04') && ((uVar8 == uVar9 || ((cVar2 != cVar7 && (cVar2 != '\x03'))))))
    goto LAB_0007d304;
  }
  else {
    uVar4 = ((param_4 & 0xff) - ((param_4 & 0xff) + uVar8 + 7 & 0xf8)) + 0x20;
    uVar8 = uVar9 << (uVar4 & 0x1f);
    uVar9 = (uVar10 & uVar9) << (uVar4 & 0x1f);
    uVar10 = ~uVar8;
    pbVar1 = ((undefined *)camry_host_ptr((uint32_t)(puVar5 + ((param_2 & 0xffff) - 0x6db8))));
    if ((cVar2 == '\x03') &&
       ((uVar8 & ((uint)pbVar1[3] |
                 (uint)pbVar1[2] << 8 | (uint)pbVar1[1] << 0x10 | (uint)*pbVar1 << 0x18)) == uVar9))
    goto LAB_0007d304;
    *pbVar1 = *pbVar1 & (byte)(uVar10 >> 0x18) | (byte)(uVar9 >> 0x18);
    pbVar1[1] = pbVar1[1] & (byte)(uVar10 >> 0x10) | (byte)(uVar9 >> 0x10);
    pbVar1[2] = pbVar1[2] & (byte)(uVar10 >> 8) | (byte)(uVar9 >> 8);
    pbVar1[3] = pbVar1[3] & (byte)uVar10 | (byte)uVar9;
  }
  FUN_0007e196((uint)uVar3,0x80);
LAB_0007d304:
  cVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(uVar3 - 0x6ec2)))));
  ((void)(uVar6), thunk_FUN_0006a4c4());
  uVar6 = 0x20;
  if (cVar2 < '\0') {
    uVar6 = 0;
  }
  return uVar6;
}



undefined4 FUN_0007d31e(uint param_1,uint param_2,uint param_3,int param_4,uint *param_5)

{
  byte *pbVar1;
  int iVar2;
  char cVar3;
  uint uVar4;
  uint32_t puVar5;
  uint32_t puVar6;
  uint uVar7;
  undefined4 uVar8;
  uint uVar9;
  
  puVar5 = 0xfebeb800u;
  puVar6 = 0x23dfcu;
  uVar7 = param_3 & 0xff;
  uVar4 = 0xffffffff;
  if (uVar7 < 0x20) {
    uVar4 = (1 << (param_3 & 0x1f)) - 1;
  }
  if (uVar7 < 9) {
    uVar9 = (uint)(byte)*param_5;
  }
  else if (uVar7 < 0x11) {
    uVar9 = (uint)(ushort)*param_5;
  }
  else {
    uVar9 = *param_5;
  }
  uVar7 = (param_4 - (param_4 + uVar7 + 7 & 0xf8)) + 0x20;
  iVar2 = (uVar9 & uVar4) << (uVar7 & 0x1f);
  uVar4 = ~(uVar4 << (uVar7 & 0x1f));
  uVar8 = FUN_0007a2da();
  pbVar1 = ((undefined *)camry_host_ptr((uint32_t)(puVar5 + ((param_2 & 0xffff) - 0x6db8))));
  *pbVar1 = *pbVar1 & (byte)(uVar4 >> 0x18) | (byte)((uint)iVar2 >> 0x18);
  pbVar1[1] = pbVar1[1] & (byte)(uVar4 >> 0x10) | (byte)((uint)iVar2 >> 0x10);
  pbVar1[2] = pbVar1[2] & (byte)(uVar4 >> 8) | (byte)((uint)iVar2 >> 8);
  pbVar1[3] = pbVar1[3] & (byte)uVar4 | (byte)iVar2;
  cVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)((*((ushort *)camry_host_ptr((uint32_t)(puVar6 + (param_1 & 0xffff) * 2 + -0x1974)))) - 0x6ec2)))));
  ((void)(uVar8), thunk_FUN_0006a4c4());
  uVar8 = 0x20;
  if (cVar3 < '\0') {
    uVar8 = 0;
  }
  return uVar8;
}



void FUN_0007d3f0(uint param_1)

{
  ushort uVar1;
  uint uVar2;
  undefined1 uVar3;
  byte bVar4;
  byte bVar5;
  byte bVar6;
  byte bVar7;
  byte bVar8;
  short sVar9;
  byte bVar10;
  ushort uVar11;
  uint32_t puVar12;
  uint32_t puVar13;
  undefined4 uVar14;
  uint uVar15;
  uint uVar16;
  
  uVar11 = DAT_00021c56;
  puVar12 = 0xfebeb800u;
  puVar13 = 0x23dfcu;
  param_1 = param_1 & 0xff;
  uVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a43u + (uint32_t)(param_1) * 1u))));
  bVar4 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a42u + (uint32_t)(param_1) * 1u))));
  bVar5 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a41u + (uint32_t)(param_1) * 1u))));
  bVar6 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a46u + (uint32_t)(param_1) * 1u))));
  bVar7 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a45u + (uint32_t)(param_1) * 1u))));
  if ((bVar4 != bVar5) || (bVar6 != bVar7)) {
    uVar16 = (uint)*(ushort *)(((undefined *)camry_host_ptr(0x22144u)) + param_1 * 4);
    uVar2 = *(ushort *)(((undefined *)camry_host_ptr(0x22146u)) + param_1 * 4) + uVar16;
    for (; uVar16 < (uVar2 & 0xffff); uVar16 = uVar16 + 1 & 0xffff) {
      bVar8 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar13 + (uint32_t)(uVar16 - 0x1cb4)))));
      sVar9 = (*((short *)camry_host_ptr((uint32_t)(puVar13 + uVar16 * 8 + -0x173c))));
      uVar15 = uVar16 - uVar11 & 0xffff;
      if (((bVar7 & bVar8) != 0) && ((bVar6 & bVar8) == 0)) {
        uVar14 = FUN_0007a2da();
        if (sVar9 != 0) {
          uVar1 = sVar9 + (*((short *)camry_host_ptr((uint32_t)(puVar13 + uVar15 * 2 + -0x1504)))) + 1;
          if ((*((ushort *)camry_host_ptr((uint32_t)(puVar12 + uVar15 * 2 + -0x6e22)))) < uVar1) {
            (*((ushort *)camry_host_ptr((uint32_t)(puVar12 + uVar15 * 2 + -0x6e22)))) = uVar1;
          }
        }
        ((void)(uVar14), thunk_FUN_0006a4c4());
      }
      bVar10 = bVar4 & bVar8;
      if ((bVar5 & bVar8) == 0) {
        if (bVar10 != 0) {
          uVar14 = FUN_0007a2da();
          (*((undefined2 *)camry_host_ptr((uint32_t)(puVar12 + uVar15 * 2 + -0x6e22)))) = 0;
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar12 + (uint32_t)(uVar16 - 0x6ec2))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar12 + (uint32_t)(uVar16 - 0x6ec2))))) & 0x7f;
          ((void)(uVar14), thunk_FUN_0006a4c4());
          ((void)(uVar16), f33_return_only_stub_832f2());
        }
      }
      else if (bVar10 == 0) {
        uVar14 = FUN_0007a2da();
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar12 + (uint32_t)(uVar16 - 0x6ec2))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar12 + (uint32_t)(uVar16 - 0x6ec2))))) | 0x80;
        if (sVar9 != 0) {
          (*((short *)camry_host_ptr((uint32_t)(puVar12 + uVar15 * 2 + -0x6e22)))) =
               (*((short *)camry_host_ptr((uint32_t)(puVar13 + uVar15 * 2 + -0x155c)))) + sVar9 + 1;
        }
        ((void)(uVar14), thunk_FUN_0006a4c4());
        ((void)(uVar16), f33_return_only_stub_832f0());
      }
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a46u + (uint32_t)(param_1) * 1u)))) = bVar7;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a42u + (uint32_t)(param_1) * 1u)))) = bVar5;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar12 + (uint32_t)(param_1 - 0x6dbc))))) = uVar3;
  return;
}



void FUN_0007d52c(void)

{
  uint uVar1;
  byte bVar2;
  ushort uVar3;
  uint32_t puVar4;
  uint32_t puVar5;
  undefined4 uVar6;
  uint uVar7;
  uint uVar8;
  short *psVar9;
  uint uVar10;
  short sVar11;
  uint uVar12;
  uint uVar13;
  
  puVar4 = 0xfebeb800u;
  puVar5 = 0x23dfcu;
  uVar7 = (uint)DAT_00021c6e;
  uVar10 = 0;
  uVar12 = 0;
  do {
    if (uVar7 <= uVar12) {
      if (uVar10 != 0) {
        for (uVar7 = 0; uVar7 < uVar10; uVar7 = uVar7 + 1 & 0xffff) {
          FUN_0008e790((*((undefined2 *)camry_host_ptr((uint32_t)(puVar4 + uVar7 * 2 + -0x6e78)))));
        }
      }
      return;
    }
    FUN_0007d3f0(uVar12);
    bVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(uVar12 - 0x6dbc)))));
    uVar13 = (uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar5 + uVar12 * 4 + -0x1cb8))));
    uVar3 = (*((ushort *)camry_host_ptr((uint32_t)(puVar5 + -0x21a6))));
    uVar1 = (*((ushort *)camry_host_ptr((uint32_t)(puVar5 + uVar12 * 4 + -0x1cb6)))) + uVar13;
    for (; uVar13 < (uVar1 & 0xffff); uVar13 = uVar13 + 1 & 0xffff) {
      uVar8 = uVar13 - uVar3 & 0xffff;
      psVar9 = ((short *)camry_host_ptr((uint32_t)(puVar4 + uVar8 * 2 + -0x6e22)));
      if ((*((short *)camry_host_ptr((uint32_t)(puVar4 + uVar8 * 2 + -0x6e22)))) == 0) {
        if (((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(uVar13 - 0x1cb4))))) & bVar2) != 0) &&
            (((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(uVar13 - 0x6ec2))))) >> 1 & 1) == 0)) &&
           (sVar11 = (*((short *)camry_host_ptr((uint32_t)(puVar5 + uVar13 * 8 + -0x173c)))), sVar11 != 0)) goto LAB_0007d5d2;
      }
      else {
        sVar11 = (*((short *)camry_host_ptr((uint32_t)(puVar4 + uVar8 * 2 + -0x6e22)))) + -1;
        if ((sVar11 == 0) && (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(uVar13 - 0x1cb4))))) & bVar2) != 0)) {
          uVar6 = FUN_0007a2da();
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(uVar13 - 0x6ec2))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(uVar13 - 0x6ec2))))) | 2;
          ((void)(uVar6), thunk_FUN_0006a4c4());
          (*((short *)camry_host_ptr((uint32_t)(puVar4 + uVar10 * 2 + -0x6e78)))) = (short)uVar13;
          uVar10 = uVar10 + 1 & 0xffff;
        }
LAB_0007d5d2:
        *psVar9 = sVar11;
      }
    }
    uVar12 = uVar12 + 1 & 0xff;
  } while( true );
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



undefined4 FUN_0007d6e6(uint param_1,ushort param_2)

{
  ushort uVar1;
  uint32_t puVar2;
  uint32_t puVar3;
  undefined4 uVar4;
  
  puVar2 = 0xfebeb800u;
  puVar3 = 0x23dfcu;
  uVar4 = FUN_0007a2da();
  uVar1 = *(short *)(((undefined *)camry_host_ptr(0x226c0u)) + (param_1 & 0xffff) * 8) + param_2;
  if ((param_2 < uVar1) &&
     ((*((ushort *)camry_host_ptr((uint32_t)(puVar2 + ((param_1 & 0xffff) - (uint)*(ushort *)(puVar3 + -0x21a6) & 0xffff) * 2 + -0x6e22))))
      < uVar1)) {
    (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + ((param_1 & 0xffff) - (uint)*(ushort *)(puVar3 + -0x21a6) & 0xffff) * 2 + -0x6e22)))) =
         uVar1;
  }
  ((void)(uVar4), thunk_FUN_0006a4c4());
  return 0;
}



/* Constant source: return 1; shape-classified from the canonical corpus. Callers receive this
   literal directly; its meaning is not recovered. */

undefined4 f33_return_const_1_7d800(void)

{
  return 1;
}



void FUN_0007d804(short param_1)

{
  byte bVar1;
  uint uVar2;
  undefined8 uVar3;
  int iVar4;
  byte bVar5;
  undefined1 local_2c [32];
  
  bVar1 = DAT_00021c6e;
  uVar3 = 0x23dfc00000000;
  uVar2 = 0;
  do {
    local_2c[uVar2] = 0;
    uVar2 = uVar2 + 1;
  } while (uVar2 < 0x20);
  if (param_1 == 4) {
    FUN_0008317e(camry_host_addr(local_2c));
  }
  FUN_0007e380(camry_host_addr(local_2c));
  FUN_0007d646(camry_host_addr(local_2c));
  FUN_000832f4(param_1);
  FUN_000833cc();
  FUN_0007e312();
  for (bVar5 = 0; iVar4 = (int)((ulonglong)uVar3 >> 0x20), bVar5 < bVar1; bVar5 = bVar5 + 1) {
    FUN_0007e2ea(bVar5);
    FUN_0007d608(bVar5);
  }
  FUN_0007e364();
  (*(int (*)())*(code **)(iVar4 + -0x21fc))();
  (*(int (*)())*(code **)(iVar4 + -0x21f8))();
  (*(int (*)())*(code **)(iVar4 + -0x2200))();
  FUN_0007e33e();
  return;
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



/* Enable/disable clears pending classes and updates flags/countdowns; neither transition copies or
   clears live COM payload. */

void f33_apply_com_tx_group_transition(uchar group)

{
  uint uVar1;
  int iVar2;
  byte bVar3;
  byte bVar4;
  char cVar5;
  byte bVar6;
  short sVar7;
  short sVar8;
  short sVar9;
  byte bVar10;
  byte bVar11;
  uint32_t puVar12;
  uint32_t puVar13;
  uint uVar14;
  undefined4 uVar15;
  short *psVar16;
  uint uVar17;
  uint uVar18;
  
  puVar12 = 0xfebeb800u;
  puVar13 = 0x23dfcu;
  uVar14 = (uint)group;
  iVar2 = uVar14 * 2;
  bVar3 = f33_com_tx_pending_and_group_state[uVar14 + 3];
  bVar4 = f33_com_tx_pending_and_group_state[uVar14 + 2];
  sVar7 = *(short *)(((undefined *)camry_host_ptr(0xfebe4986u)) + iVar2);
  cVar5 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a3fu + (uint32_t)(uVar14) * 1u))));
  if ((bVar3 != bVar4) || (cVar5 == '\x01')) {
    uVar18 = (uint)*(ushort *)(((undefined *)camry_host_ptr(0x22140u)) + uVar14 * 4);
    uVar1 = *(ushort *)(((undefined *)camry_host_ptr(0x22142u)) + uVar14 * 4) + uVar18;
    sVar8 = *(short *)(((undefined *)camry_host_ptr(0x21c5cu)) + iVar2);
    for (; uVar18 < (uVar1 & 0xffff); uVar18 = uVar18 + 1 & 0xffff) {
      bVar6 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar13 + (uint32_t)(uVar18 * 8 + -0x1736)))));
      psVar16 = ((short *)camry_host_ptr((uint32_t)(puVar13 + uVar18 * 8 + -0x173c)));
      bVar10 = bVar4 & (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar13 + (uint32_t)(uVar18 - 0x1cb4)))));
      bVar11 = bVar3 & (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar13 + (uint32_t)(uVar18 - 0x1cb4)))));
      if (bVar10 == 0) {
        if (bVar11 != 0) {
          (*(int (*)())*(code **)(puVar13 + -0x21f0))(uVar18);
          uVar17 = uVar18 >> 3 & 0xff;
          bVar11 = (byte)(1 << (uVar18 & 7)) ^ 0xff;
          uVar15 = FUN_0007a2da();
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar12 + (uint32_t)(uVar17 - 0x6dc7))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar12 + (uint32_t)(uVar17 - 0x6dc7))))) & bVar11;
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar12 + (uint32_t)(uVar17 - 0x6dc6))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar12 + (uint32_t)(uVar17 - 0x6dc6))))) & bVar11;
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar12 + (uint32_t)(uVar18 - 0x6ec2))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar12 + (uint32_t)(uVar18 - 0x6ec2))))) & 0x3b;
          (*((undefined2 *)camry_host_ptr((uint32_t)(puVar12 + uVar18 * 2 + -0x6e92)))) = 0;
          (*((undefined2 *)camry_host_ptr((uint32_t)(puVar12 + uVar18 * 2 + -0x6e88)))) = 0;
          if ((bVar6 >> 3 & 1) != 0) {
            (*(int (*)())*(code **)(puVar13 + -0x21cc))(uVar18);
          }
          ((void)(uVar15), thunk_FUN_0006a4c4());
          ((void)(uVar18), f33_return_only_stub_832f2());
        }
      }
      else if (bVar11 == 0) {
        uVar17 = uVar18 >> 3 & 0xff;
        bVar11 = (byte)(1 << (uVar18 & 7)) ^ 0xff;
        uVar15 = FUN_0007a2da();
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar12 + (uint32_t)(uVar17 - 0x6dc7))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar12 + (uint32_t)(uVar17 - 0x6dc7))))) & bVar11;
        sVar9 = *psVar16;
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar12 + (uint32_t)(uVar17 - 0x6dc6))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar12 + (uint32_t)(uVar17 - 0x6dc6))))) & bVar11;
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar12 + (uint32_t)(uVar18 - 0x6ec2))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar12 + (uint32_t)(uVar18 - 0x6ec2))))) | 0x84;
        if (sVar9 != 0) {
          (*((short *)camry_host_ptr((uint32_t)(puVar12 + uVar18 * 2 + -0x6e92)))) =
               (*((short *)camry_host_ptr((uint32_t)(puVar13 + uVar18 * 2 + -0x1c84)))) + sVar8 + 1;
        }
        (*((short *)camry_host_ptr((uint32_t)(puVar12 + uVar18 * 2 + -0x6e88)))) = sVar8 + 1;
        if ((bVar6 >> 3 & 1) != 0) {
          (*(int (*)())*(code **)(puVar13 + -0x21cc))(uVar18);
        }
        ((void)(uVar15), thunk_FUN_0006a4c4());
        ((void)(uVar18), f33_return_only_stub_832f0());
      }
      if ((cVar5 == '\x01') && (bVar10 != 0)) {
        sVar9 = *psVar16;
        uVar15 = FUN_0007a2da();
        bVar6 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar12 + (uint32_t)(uVar18 - 0x6ec2)))));
        if ((sVar9 != 0) && ((bVar6 >> 2 & 1) == 0)) {
          (*((short *)camry_host_ptr((uint32_t)(puVar12 + uVar18 * 2 + -0x6e92)))) =
               (*((short *)camry_host_ptr((uint32_t)(puVar13 + uVar18 * 2 + -0x1c84)))) + sVar7 + 1;
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar12 + (uint32_t)(uVar18 - 0x6ec2))))) = bVar6 | 0x40;
        }
        ((void)(uVar15), thunk_FUN_0006a4c4());
      }
    }
  }
  f33_com_tx_pending_and_group_state[uVar14 + 3] = bVar4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a3fu + (uint32_t)(uVar14) * 1u)))) = 0;
  *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe4986u)) + iVar2) = 0;
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



/* Advance periodic and minimum-delay countdowns; due requests enter pending bitmaps separately from
   payload generation. Native periodic-due cases reload countdowns before successful or failed lower
   admission; this is invocation-state behavior, not measured timing. */

void f33_service_com_tx_countdowns(void)

{
  uint uVar1;
  byte bVar2;
  char cVar3;
  char cVar4;
  byte bVar5;
  uint32_t puVar6;
  uint32_t puVar7;
  short sVar8;
  undefined4 uVar9;
  uint uVar10;
  int iVar11;
  int iVar12;
  short *psVar13;
  short *psVar14;
  uint uVar15;
  uint uVar16;
  bool bVar17;
  
  cVar4 = DAT_00021c6f;
  puVar6 = 0xfebeb800u;
  puVar7 = 0x23dfcu;
  uVar10 = (uint)DAT_00021c6e;
  uVar15 = 0;
  do {
    if (uVar10 <= uVar15) {
      (*(int (*)())*(code **)(puVar7 + -0x21e0))();
      (*(int (*)())*(code **)(puVar7 + -0x21c8))();
      return;
    }
    uVar16 = (uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar7 + uVar15 * 4 + -0x1cbc))));
    uVar1 = (*((ushort *)camry_host_ptr((uint32_t)(puVar7 + uVar15 * 4 + -0x1cba)))) + uVar16;
    bVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(uVar15 - 0x6dc4)))));
    cVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(uVar15 - 0x6dc2)))));
    for (; uVar16 < (uVar1 & 0xffff); uVar16 = uVar16 + 1 & 0xffff) {
      iVar12 = uVar16 * 2;
      psVar13 = ((short *)camry_host_ptr((uint32_t)(puVar6 + iVar12 + -0x6e88)));
      if ((*((short *)camry_host_ptr((uint32_t)(puVar6 + iVar12 + -0x6e88)))) != 0) {
        sVar8 = (*((short *)camry_host_ptr((uint32_t)(puVar6 + iVar12 + -0x6e88)))) + -1;
        if (sVar8 == 0) {
          uVar9 = FUN_0007a2da();
          bVar5 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(uVar16 - 0x6ec2)))));
          if ((bVar5 >> 2 & 1) != 0) {
            bVar5 = bVar5 & 0xfb;
            if ((*((short *)camry_host_ptr((uint32_t)(puVar7 + uVar16 * 8 + -0x173c)))) != 0) {
              bVar5 = bVar5 | 0x40;
              (*((short *)camry_host_ptr((uint32_t)(puVar6 + iVar12 + -0x6e92)))) = (*((short *)camry_host_ptr((uint32_t)(puVar7 + iVar12 + -0x1c84)))) + 1;
            }
            (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(uVar16 - 0x6ec2))))) = bVar5;
          }
          ((void)(uVar9), thunk_FUN_0006a4c4());
          sVar8 = (*(int (*)())*(code **)(puVar7 + -0x21e4))(uVar16);
        }
        *psVar13 = sVar8;
      }
      sVar8 = (*((short *)camry_host_ptr((uint32_t)(puVar6 + iVar12 + -0x6e92))));
      psVar13 = ((short *)camry_host_ptr((uint32_t)(puVar6 + iVar12 + -0x6e92)));
      if (sVar8 != 0) {
        if (sVar8 == 1) {
          sVar8 = 0;
          if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(uVar16 - 0x1cb4))))) & bVar2) != 0) {
            iVar12 = -0xd;
            psVar14 = ((short *)camry_host_ptr((uint32_t)(puVar7 + uVar16 * 8 + -0x173c)));
            if (((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(uVar16 * 8 + -0x1736))))) >> 4 & 1) != 0) {
              iVar12 = (*(int (*)())*(code **)(puVar7 + -0x21bc))(uVar16);
            }
            sVar8 = *psVar14;
            uVar9 = FUN_0007a2da();
            bVar5 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(uVar16 - 0x6ec2)))));
            if ((bVar5 >> 6 & 1) == 0) {
              if ((bVar5 >> 2 & 1) == 0) {
                bVar17 = cVar3 == '\x01';
                goto LAB_0007dc2c;
              }
            }
            else {
              iVar11 = -0x15;
              if (cVar3 == '\x01') {
                iVar11 = 0;
              }
              (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(uVar16 - 0x6ec2))))) = bVar5 & 0xbf;
              bVar17 = iVar11 == 0;
LAB_0007dc2c:
              if ((bVar17) && (iVar12 == -0xd)) {
                FUN_0007dab6(uVar16,1);
              }
            }
            ((void)(uVar9), thunk_FUN_0006a4c4());
            if ((cVar4 == '\0') && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(uVar15 - 0x6dc9))))) == '\x01')) {
              sVar8 = (*((short *)camry_host_ptr((uint32_t)(puVar7 + uVar15 * 2 + -0x21a4))));
            }
            if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(uVar15 - 0x2186))))) == '\x03') {
              sVar8 = FUN_0007dae0(uVar15,uVar16,sVar8);
            }
          }
        }
        else {
          sVar8 = sVar8 + -1;
        }
        *psVar13 = sVar8;
      }
    }
    uVar15 = uVar15 + 1 & 0xff;
  } while( true );
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



void FUN_0007e046(uint param_1,uint param_2)

{
  uint uVar1;
  int iVar2;
  ushort uVar3;
  char cVar4;
  uint32_t puVar5;
  undefined4 uVar6;
  byte bVar7;
  uint uVar8;
  uint uVar9;
  uint uVar10;
  uint uVar11;
  
  puVar5 = 0xfebeb800u;
  uVar8 = param_2 & 0xff;
  iVar2 = (param_1 & 0xff) * 4;
  uVar3 = *(ushort *)(((undefined *)camry_host_ptr(0x22140u)) + iVar2);
  uVar10 = (uint)*(ushort *)(((undefined *)camry_host_ptr(0x22142u)) + iVar2);
  uVar9 = uVar3 & 7;
  uVar11 = uVar3 >> 3 & 0xff;
  if (uVar10 != 0) {
    uVar1 = uVar10 + uVar9;
    uVar6 = FUN_0007a2da();
    if ((uVar3 & 7) != 0) {
      cVar4 = -1;
      if ((uVar1 & 0xffff) < 8) {
        cVar4 = (char)(1 << (uVar1 & 0x1f)) + -1;
      }
      bVar7 = cVar4 - ((char)(1 << uVar9) + -1) ^ 0xff;
      if ((uVar8 >> 6 & 1) != 0) {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(uVar11 - 0x6dc7))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(uVar11 - 0x6dc7))))) & bVar7;
      }
      if (uVar8 >> 7 != 0) {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(uVar11 - 0x6dc6))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(uVar11 - 0x6dc6))))) & bVar7;
      }
      uVar11 = uVar11 + 1 & 0xff;
    }
    uVar10 = uVar10 + uVar3;
    uVar9 = uVar10 - 1 >> 3 & 0xff;
    if (uVar11 <= uVar9) {
      uVar10 = uVar10 & 7;
      bVar7 = 0;
      if (uVar10 != 0) {
        bVar7 = (char)(1 << uVar10) - 1U ^ 0xff;
      }
      if ((param_2 & 0x40) != 0) {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(uVar9 - 0x6dc7))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(uVar9 - 0x6dc7))))) & bVar7;
      }
      if ((param_2 & 0x80) != 0) {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(uVar9 - 0x6dc6))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(uVar9 - 0x6dc6))))) & bVar7;
      }
      for (; uVar11 < uVar9; uVar11 = uVar11 + 1 & 0xff) {
        if ((param_2 & 0x40) != 0) {
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(uVar11 - 0x6dc7))))) = 0;
        }
        if ((param_2 & 0x80) != 0) {
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(uVar11 - 0x6dc6))))) = 0;
        }
      }
    }
    ((void)(uVar6), thunk_FUN_0006a4c4());
  }
  ((void)(param_1 & 0xff), (void)(uVar8), f33_return_only_stub_7e718());
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



void FUN_0007e3e0(uint param_1,uint param_2)

{
  uint32_t puVar1;
  undefined4 uVar2;
  undefined1 uVar3;
  undefined1 uVar4;
  
  puVar1 = 0xfebeb800u;
  if ((param_2 & 1) == 0) {
    uVar3 = 2;
  }
  else {
    uVar3 = 1;
  }
  if ((param_2 >> 1 & 1) == 0) {
    uVar4 = 2;
  }
  else {
    uVar4 = 1;
  }
  uVar2 = FUN_0007a2da();
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)((param_1 & 0xff) - 0x6dc2))))) = uVar3;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)((param_1 & 0xff) - 0x6dc3))))) = uVar4;
  ((void)(uVar2), thunk_FUN_0006a4c4());
  return;
}



void FUN_0007e412(uint param_1,undefined2 param_2)

{
  uint32_t puVar1;
  undefined4 uVar2;
  
  puVar1 = 0xfebeb800u;
  uVar2 = FUN_0007a2da();
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)((param_1 & 0xff) - 0x6dc1))))) = 1;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + (param_1 & 0xff) * 2 + -0x6e7a)))) = param_2;
  ((void)(uVar2), thunk_FUN_0006a4c4());
  return;
}



void FUN_0007e46a(uint param_1,char param_2)

{
  byte bVar1;
  uint32_t puVar2;
  uint32_t puVar3;
  undefined4 uVar4;
  uint uVar5;
  uint uVar6;
  
  puVar2 = 0xfebeb800u;
  puVar3 = 0x23dfcu;
  uVar6 = param_1 & 0xffff;
  if (uVar6 < DAT_00021c56) {
    uVar5 = uVar6 >> 3 & 0xff;
    bVar1 = (byte)(1 << (param_1 & 7)) ^ 0xff;
    uVar4 = FUN_0007a2da();
    if (param_2 == -0x80) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(uVar5 - 0x6dc6))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(uVar5 - 0x6dc6))))) & bVar1;
      if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x226c6u + (uint32_t)(uVar6 * 8) * 1u)))) & 8) != 0) {
        (*(int (*)())*(code **)(puVar3 + -0x21cc))(uVar6);
      }
    }
    else {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(uVar5 - 0x6dc7))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(uVar5 - 0x6dc7))))) & bVar1;
    }
    ((void)(uVar4), thunk_FUN_0006a4c4());
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



void FUN_0007e4fe(uint param_1)

{
  uint uVar1;
  byte bVar2;
  byte bVar3;
  uint32_t puVar4;
  uint32_t puVar5;
  undefined4 uVar6;
  uint uVar7;
  
  puVar4 = 0xfebeb800u;
  puVar5 = 0x23dfcu;
  param_1 = param_1 & 0xff;
  if (param_1 < DAT_00021c6e) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a37u + (uint32_t)(param_1) * 1u)))) = 2;
    uVar7 = (uint)*(ushort *)(((undefined *)camry_host_ptr(0x22140u)) + param_1 * 4);
    uVar1 = *(ushort *)(((undefined *)camry_host_ptr(0x22142u)) + param_1 * 4) + uVar7;
    bVar3 = f33_com_tx_pending_and_group_state[param_1 + 3];
    for (; uVar7 < (uVar1 & 0xffff); uVar7 = uVar7 + 1 & 0xffff) {
      if (((*((short *)camry_host_ptr((uint32_t)(puVar5 + uVar7 * 8 + -0x173c)))) != 0) && (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(uVar7 - 0x1cb4))))) & bVar3) != 0)
         ) {
        uVar6 = FUN_0007a2da();
        bVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(uVar7 - 0x6ec2)))));
        if ((bVar2 >> 2 & 1) == 0) {
          (*((short *)camry_host_ptr((uint32_t)(puVar4 + uVar7 * 2 + -0x6e92)))) = (*((short *)camry_host_ptr((uint32_t)(puVar5 + uVar7 * 2 + -0x1c84)))) + 1;
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(uVar7 - 0x6ec2))))) = bVar2 | 0x40;
        }
        ((void)(uVar6), thunk_FUN_0006a4c4());
      }
    }
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



undefined4 FUN_0007e612(uint param_1)

{
  byte *pbVar1;
  uint uVar2;
  byte bVar3;
  byte bVar4;
  byte bVar5;
  uint32_t puVar6;
  undefined4 uVar7;
  undefined4 uVar8;
  uint uVar9;
  uint uVar10;
  uint uVar11;
  
  puVar6 = 0xfebeb800u;
  uVar10 = param_1 & 0xffff;
  uVar8 = 1;
  if (uVar10 < DAT_00021c56) {
    uVar2 = 1 << (param_1 & 7);
    uVar9 = uVar10 >> 3 & 0xff;
    uVar11 = uVar2 & 0xff;
    uVar7 = FUN_0007a2da();
    pbVar1 = ((undefined *)camry_host_ptr((uint32_t)(puVar6 + (uVar9 - 0x6dcb))));
    bVar3 = *pbVar1;
    bVar4 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(uVar9 - 0x6dcc)))));
    bVar5 = (byte)uVar2;
    if (((bVar3 ^ bVar4) & uVar11) == 0) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(uVar9 - 0x6dcc))))) = bVar5 | bVar4;
      *pbVar1 = bVar5 | bVar3;
      FUN_000833d6();
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(uVar10 - 0x6ec2))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(uVar10 - 0x6ec2))))) | 0x10;
    }
    else if ((uVar11 & bVar4) == 0) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(uVar9 - 0x6dcc))))) = bVar5 | bVar4;
      uVar8 = 0;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(uVar10 - 0x6ec2))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(uVar10 - 0x6ec2))))) | 0x10;
      *pbVar1 = (bVar5 ^ 0xff) & bVar3;
    }
    ((void)(uVar7), thunk_FUN_0006a4c4());
  }
  return uVar8;
}



undefined4 FUN_0007e696(uint param_1)

{
  byte *pbVar1;
  uint uVar2;
  byte bVar3;
  byte bVar4;
  byte bVar5;
  uint32_t puVar6;
  undefined4 uVar7;
  undefined4 uVar8;
  uint uVar9;
  uint uVar10;
  uint uVar11;
  
  puVar6 = 0xfebeb800u;
  uVar10 = param_1 & 0xffff;
  uVar8 = 1;
  if (uVar10 < DAT_00021c56) {
    uVar2 = 1 << (param_1 & 7);
    uVar9 = uVar10 >> 3 & 0xff;
    uVar11 = uVar2 & 0xff;
    uVar7 = FUN_0007a2da();
    pbVar1 = ((undefined *)camry_host_ptr((uint32_t)(puVar6 + (uVar9 - 0x6dcb))));
    bVar3 = *pbVar1;
    bVar4 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(uVar9 - 0x6dcc)))));
    bVar5 = (byte)uVar2;
    if (((bVar3 ^ bVar4) & uVar11) == 0) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(uVar9 - 0x6dcc))))) = bVar5 | bVar4;
      *pbVar1 = bVar5 | bVar3;
      FUN_000833d6();
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(uVar10 - 0x6ec2))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(uVar10 - 0x6ec2))))) | 0x10;
    }
    else if ((uVar11 & bVar4) != 0) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(uVar9 - 0x6dcc))))) = (bVar5 ^ 0xff) & bVar4;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(uVar10 - 0x6ec2))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(uVar10 - 0x6ec2))))) & 0xef;
      *pbVar1 = bVar5 | bVar3;
      uVar8 = 0;
    }
    ((void)(uVar7), thunk_FUN_0006a4c4());
  }
  return uVar8;
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



/* Far-call trampoline: prepare {lp},0 / jarl 0x7EF9C / dispose 0,{lp},lp; byte-verified against the
   exact image. Forwards with registers and stack unchanged; marked as a thunk. Forwarding shape
   machine-verified; target semantics not recovered. */

void thunk_FUN_0007ef9c(void)

{
  FUN_0007ef9c();
  return;
}



void FUN_0007ee8e(uint param_1)

{
  (*(int (*)())*(code **)(&PTR_PTR_00021ca0)[(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x21c7du + (uint32_t)(param_1 & 0xff) * 1u))))])();
  return;
}



void FUN_0007eeae(uint param_1)

{
  (*(int (*)())*(code **)((&PTR_PTR_00021ca0)[(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x21c7du + (uint32_t)(param_1 & 0xff) * 1u))))] + 4))();
  return;
}



void FUN_0007eece(uint param_1)

{
  (*(int (*)())*(code **)((&PTR_PTR_00021ca0)[(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x21c7du + (uint32_t)(param_1 & 0xff) * 1u))))] + 8))();
  return;
}



undefined4 FUN_0007eeee(uint param_1)

{
  undefined4 uVar1;
  
  if ((param_1 & 0xff) < (uint)DAT_00021c7c) {
    uVar1 = (*(int (*)())*(code **)((&PTR_PTR_00021ca0)[(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x21c7du + (uint32_t)(param_1 & 0xff) * 1u))))] + 0xc))();
  }
  else {
    uVar1 = 1;
  }
  return uVar1;
}



void FUN_0007ef9c(void)

{
  FUN_00083542();
  f33_return_only_stub_8356c();
  return;
}



/* Far-call trampoline: prepare {lp},0 / jarl 0x7A2DA / dispose 0,{lp},lp; byte-verified against the
   exact image. Forwards with registers and stack unchanged; marked as a thunk. Forwarding shape
   machine-verified; target semantics not recovered. */

void thunk_FUN_0007a2da(void)

{
  FUN_0007a2da();
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



undefined4 FUN_0007f052(uint param_1,undefined2 *param_2,undefined1 *param_3)

{
  undefined4 uVar1;
  undefined1 uVar2;
  undefined2 uVar3;
  
  if (*(short *)(((undefined *)camry_host_ptr(0xfebe4914u)) + (param_1 & 0xff) * 8) == 0x1fe) {
    uVar2 = 0;
    uVar3 = 0x1fe;
  }
  else {
    if (*(short *)(((undefined *)camry_host_ptr(0xfebe4914u)) + (param_1 & 0xff) * 8) != 0x2fd) {
      return 1;
    }
    uVar3 = 0x4fb;
    uVar2 = 3;
  }
  uVar1 = FUN_0007a2da();
  *param_2 = uVar3;
  *param_3 = uVar2;
  ((void)(uVar1), thunk_FUN_0006a4c4());
  return 0;
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



void FUN_0007f250(undefined4 param_1)

{
  undefined8 uVar1;
  uint uVar2;
  uint uVar3;
  
  uVar1 = 0x23dfc00000000;
  uVar2 = (uint)DAT_00021b09;
  for (uVar3 = 0; uVar3 < uVar2; uVar3 = uVar3 + 1 & 0xff) {
    (*(int (*)())**(undefined4 **)(uVar3 * 4 + (int)((ulonglong)uVar1 >> 0x20) + -0x228c))(param_1);
  }
  return;
}



void FUN_0007f27c(void)

{
  undefined8 uVar1;
  uint uVar2;
  uint uVar3;
  
  uVar1 = 0x23dfc00000000;
  uVar2 = (uint)DAT_00021b09;
  for (uVar3 = 0; uVar3 < uVar2; uVar3 = uVar3 + 1 & 0xff) {
    (*(int (*)())*(code **)((*((int *)camry_host_ptr((uint32_t)(uVar3 * 4 + (int)((ulonglong)uVar1 >> 0x20) + -0x228c)))) + 4))();
  }
  return;
}



void FUN_0007f2a4(int param_1)

{
  (*(int (*)())*(code **)((&PTR_PTR_00021b70)[(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x21b0bu + (uint32_t)(param_1 - (uint)DAT_00021b08 & 0xff) * 1u))))] +
              0x10))();
  return;
}



void FUN_0007f2ca(int param_1)

{
  (*(int (*)())*(code **)((&PTR_PTR_00021b70)[(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x21b0bu + (uint32_t)(param_1 - (uint)DAT_00021b08 & 0xff) * 1u))))] +
              0x14))();
  return;
}



void FUN_0007f2f0(int param_1)

{
  (*(int (*)())*(code **)((&PTR_PTR_00021b70)[(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x21b0bu + (uint32_t)(param_1 - (uint)DAT_00021b08 & 0xff) * 1u))))] +
              0x18))();
  return;
}



void FUN_0007f316(int param_1)

{
  (*(int (*)())*(code **)((&PTR_PTR_00021b70)[(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x21b0bu + (uint32_t)(param_1 - (uint)DAT_00021b08 & 0xff) * 1u))))] +
              0x1c))();
  return;
}



void FUN_0007f33c(void)

{
  undefined8 uVar1;
  uint uVar2;
  uint uVar3;
  
  uVar1 = 0x23dfc00000000;
  uVar2 = (uint)DAT_00021b0a;
  for (uVar3 = 0; uVar3 < uVar2; uVar3 = uVar3 + 1 & 0xff) {
    (*(int (*)())*(code **)((*((int *)camry_host_ptr((uint32_t)(uVar3 * 4 + (int)((ulonglong)uVar1 >> 0x20) + -0x22fc)))) + 8))();
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



void FUN_0007f366(uint param_1)

{
  (*(int (*)())*(code **)((&PTR_PTR_00021b70)[(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x21b0bu + (uint32_t)(param_1 & 0xff) * 1u))))] + 0xc))();
  return;
}



void FUN_0007f386(uint param_1)

{
  (*(int (*)())*(code **)((&PTR_PTR_00021b70)[(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x21b0bu + (uint32_t)(param_1 & 0xff) * 1u))))] + 0x24))();
  return;
}



void FUN_0007f3a6(uint param_1)

{
  (*(int (*)())*(code **)((&PTR_PTR_00021b70)[(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x21b0bu + (uint32_t)(param_1 & 0xff) * 1u))))] + 0x20))();
  return;
}



bool FUN_0007f4fe(uint param_1,char param_2)

{
  ushort uVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  
  param_1 = param_1 & 0xff;
  iVar4 = 1;
  uVar1 = f33_logical_controller_request_cache[param_1];
  if (param_2 == '\0') {
    if (uVar1 == 0x6b94) {
      iVar4 = ((void)(param_1), f33_return_const_1_8158a());
    }
  }
  else if ((param_2 == '\x02') && ((uVar1 == 0x57a8 || (uVar1 == 0x6b94)))) {
    uVar2 = FUN_0007a2f4();
    iVar3 = FUN_0007f6a4(param_1);
    iVar4 = ((void)(param_1), (void)(2), f33_return_const_1_8158a());
    if (iVar3 != 1) {
      FUN_000812be(param_1);
    }
    ((void)(uVar2), thunk_FUN_0006a4c4());
  }
  return iVar4 != 0;
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



int FUN_0007f5f0(uint param_1)

{
  int iVar1;
  byte bVar2;
  short sVar3;
  uint32_t puVar4;
  undefined4 uVar5;
  int iVar6;
  uint uVar7;
  
  puVar4 = 0x23dfcu;
  param_1 = param_1 & 0xff;
  iVar1 = param_1 * 2;
  iVar6 = 0;
  if ((((f33_logical_controller_request_cache[param_1] == 0x57a8) &&
       (*(short *)(((undefined *)camry_host_ptr(0xfebe48feu)) + iVar1) == 0x5555)) && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x21972u + (uint32_t)(param_1) * 1u)))) != '\0')) &&
     (*(short *)(((undefined *)camry_host_ptr(0x2196au)) + iVar1) != 0)) {
    bVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x21973u + (uint32_t)(param_1) * 1u))));
    uVar7 = 0;
    while ((uVar7 < bVar2 && (iVar6 == 0))) {
      uVar5 = FUN_0007a2da();
      sVar3 = (*((short *)camry_host_ptr((uint32_t)(*(int *)(puVar4 + param_1 * 4 + -0x24c8) + uVar7 * 2))));
      if (sVar3 != 0) {
        sVar3 = sVar3 + -1;
      }
      if (((*((char *)camry_host_ptr((uint32_t)(*(int *)(puVar4 + param_1 * 4 + -0x2514) + uVar7)))) != 'i') && (sVar3 == 0)) {
        iVar6 = 1;
        *(ushort *)(((undefined *)camry_host_ptr(0xfebe48feu)) + iVar1) = *(ushort *)(((undefined *)camry_host_ptr(0xfebe48feu)) + iVar1) & 0xfff3 | 8;
      }
      (*((short *)camry_host_ptr((uint32_t)(*(int *)(puVar4 + param_1 * 4 + -0x24c8) + uVar7 * 2)))) = sVar3;
      ((void)(uVar5), thunk_FUN_0006a4c4());
      uVar7 = uVar7 + 1 & 0xff;
    }
  }
  return iVar6;
}



undefined4 FUN_0007f6a4(char param_1)

{
  undefined8 uVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  
  uVar1 = 0x23dfc00000000;
  uVar3 = (uint)DAT_00021971;
  uVar4 = 0;
  while( true ) {
    if (uVar3 <= uVar4) {
      return 0;
    }
    if ((param_1 == (*((char *)camry_host_ptr((uint32_t)(uVar4 + (int)((ulonglong)uVar1 >> 0x20) + -0x2484))))) &&
       (iVar2 = ((void)(uVar4), f33_return_const_1_83598()), iVar2 == 0)) break;
    uVar4 = uVar4 + 1 & 0xff;
  }
  return 1;
}



char FUN_0007f7e4(char param_1,char param_2)

{
  undefined8 uVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  
  uVar1 = 0x23dfc00000000;
  if (param_2 == 'i') {
    uVar3 = (uint)DAT_00021971;
    uVar4 = 0;
    for (uVar5 = 0; uVar5 < uVar3; uVar5 = uVar5 + 1 & 0xff) {
      if (param_1 == (*((char *)camry_host_ptr((uint32_t)(uVar5 + (int)((ulonglong)uVar1 >> 0x20) + -0x2484))))) {
        uVar2 = ((void)(0), FUN_00083f9a(uVar5));
        uVar4 = uVar4 | uVar2;
      }
    }
    if (uVar4 == 0) {
      param_2 = -0x6a;
    }
    else {
      param_2 = -0x3d;
      if (uVar4 == 2) {
        param_2 = 'i';
      }
    }
  }
  return param_2;
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



void FUN_0007f882(uint param_1)

{
  uint32_t puVar1;
  uint32_t puVar2;
  uint uVar3;
  uint uVar4;
  code *pcVar5;
  
  puVar1 = 0xfebeb800u;
  puVar2 = 0x23dfcu;
  param_1 = param_1 & 0xff;
  uVar3 = (uint)DAT_00021971;
  for (uVar4 = 0; uVar4 < uVar3; uVar4 = uVar4 + 1 & 0xff) {
    if (param_1 == (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(uVar4 - 0x2484)))))) {
      f33_driver_request_channel_start_stop((uchar)uVar4,'\x01');
    }
  }
  pcVar5 = *(code **)(puVar2 + -0x2500);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(param_1 - 0x6efd))))) = 0x69;
  (*(int (*)())pcVar5)(param_1);
  return;
}



undefined4 FUN_0007f8c8(uint param_1,char param_2)

{
  byte *pbVar1;
  byte bVar2;
  byte bVar3;
  char cVar4;
  undefined8 uVar5;
  int iVar6;
  code *pcVar7;
  undefined4 uVar8;
  undefined1 uVar9;
  
  bVar3 = DAT_00021977;
  uVar5 = 0x23dfcfebeb800;
  param_1 = param_1 & 0xff;
  cVar4 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4912u + (uint32_t)(param_1) * 1u))));
  if ((*(ushort *)(((undefined *)camry_host_ptr(0xfebe48feu)) + param_1 * 2) & 3) != 1) {
    FUN_00080f5a(param_1,0x5a);
    return 1;
  }
  if (cVar4 == -0x4c) {
    return 8;
  }
  if (cVar4 == -0x5b) {
    return 9;
  }
  if (cVar4 == 'Z') {
    return 1;
  }
  iVar6 = FUN_0007f7e4(param_1,(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4900u + (uint32_t)(param_1) * 1u)))));
  if (param_2 == '\x01') {
    iVar6 = FUN_0007f838(param_1,iVar6);
  }
  else if (iVar6 == 0x5a) {
    iVar6 = 0xa5;
  }
  if ((iVar6 == 0x69) || (iVar6 == 0x5a)) {
    pbVar1 = ((byte *)camry_host_ptr((uint32_t)((int)uVar5 + -0x6eff + param_1)));
    bVar2 = *pbVar1 - 1;
    if ((bVar3 <= bVar2) || (bVar2 == 0)) {
      iVar6 = 0xc3;
    }
    *pbVar1 = bVar2;
LAB_0007f9a4:
    if ((iVar6 != 0x69) && (iVar6 != 0x5a)) {
LAB_0007f9b4:
      if ((iVar6 == 0x96) || (iVar6 == 0xa5)) {
        uVar8 = 0;
      }
      else if (iVar6 == 0x3c) {
        FUN_0007f882(param_1);
        FUN_00080f5a(param_1,0xb4);
        uVar8 = 8;
      }
      else if (iVar6 == 0x1e) {
        iVar6 = 0xa5;
        FUN_00080f5a(param_1,0xa5);
        uVar8 = 9;
      }
      else {
        FUN_0007f882(param_1);
        FUN_00080f5a(param_1,0x5a);
        uVar8 = 1;
      }
      uVar9 = (undefined1)iVar6;
      pcVar7 = *(code **)((int)((ulonglong)uVar5 >> 0x20) + -0x2508);
      (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + (int)uVar5 + -0x6efd)))) = 0x69;
      (*(int (*)())pcVar7)(param_1);
      iVar6 = (int)((ulonglong)uVar5 >> 0x20);
      FUN_00080c20(param_1);
      (*(int (*)())*(code **)(iVar6 + -0x24c0))(param_1);
      FUN_00080e32(param_1,1);
      goto LAB_0007fa30;
    }
  }
  else {
    if (((iVar6 != 0x3c) && (iVar6 != 0x1e)) && (iVar6 != 0xc3)) goto LAB_0007f9b4;
    pbVar1 = ((byte *)camry_host_ptr((uint32_t)((int)uVar5 + -0x6efe + param_1)));
    bVar3 = *pbVar1;
    if (bVar3 < 2) goto LAB_0007f9a4;
    iVar6 = 0x69;
    *pbVar1 = bVar3 - 1;
  }
  uVar9 = (undefined1)iVar6;
  uVar8 = 2;
LAB_0007fa30:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4900u + (uint32_t)(param_1) * 1u)))) = uVar9;
  return uVar8;
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



void FUN_0007fa80(void)

{
  uint32_t puVar1;
  uint32_t puVar2;
  uint uVar3;
  code *pcVar4;
  uint uVar5;
  
  puVar1 = 0xfebeb800u;
  puVar2 = 0x23dfcu;
  uVar3 = (uint)DAT_00021970;
  for (uVar5 = 0; uVar5 < uVar3; uVar5 = uVar5 + 1 & 0xff) {
    pcVar4 = *(code **)(puVar2 + -0x2508);
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(uVar5 - 0x6efd))))) = 0x69;
    (*(int (*)())pcVar4)(uVar5);
    FUN_00080c20(uVar5);
    (*(int (*)())*(code **)(puVar2 + -0x24c4))(uVar5);
    FUN_00080e32(uVar5,0);
  }
  return;
}



void FUN_0007fac6(void)

{
  uint uVar1;
  uint32_t puVar2;
  undefined4 uVar3;
  uint uVar4;
  
  puVar2 = 0xfebeb800u;
  uVar4 = (uint)DAT_00021970;
  uVar3 = FUN_0007a2da();
  for (uVar1 = 0; uVar1 < uVar4; uVar1 = uVar1 + 1 & 0xff) {
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + uVar1 * 2 + -0x6f28)))) = 0x6e91;
  }
  ((void)(uVar3), thunk_FUN_0006a4c4());
  FUN_0007fa80();
  return;
}



void FUN_0007fafa(uint param_1)

{
  uint32_t puVar1;
  uint32_t puVar2;
  uint uVar3;
  uint uVar4;
  code *pcVar5;
  
  puVar1 = 0xfebeb800u;
  puVar2 = 0x23dfcu;
  param_1 = param_1 & 0xff;
  uVar3 = (uint)DAT_00021971;
  f33_logical_controller_request_cache[param_1] = 0x6b94;
  for (uVar4 = 0; uVar4 < uVar3; uVar4 = uVar4 + 1 & 0xff) {
    if (param_1 == (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(uVar4 - 0x2484)))))) {
      ((void)(0), FUN_000841a6(uVar4));
    }
  }
  pcVar5 = *(code **)(puVar2 + -0x2500);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(param_1 - 0x6efd))))) = 0x69;
  (*(int (*)())pcVar5)(param_1);
  FUN_00080c20(param_1);
  FUN_00080e32(param_1,2);
  return;
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



/* Normal class first copies up to64 bytes into4FB2 and calls811BE, before controller/route/capacity
   admission. Queue-full2 preserves old queue but scratch already contains newer data. Native
   classic admission copies source into queued record; full queue preserves old
   header/payload/cursors while scratch receives newer source. Other controller/classes remain
   static. */

uint f33_snapshot_and_enqueue_can_tx(uchar controller,ushort route,F33CanIfTxRecord *record)

{
  ushort *puVar1;
  undefined4 *puVar2;
  uint *puVar3;
  ushort queue_index;
  ushort capacity_words;
  uchar *puVar4;
  uint uVar5;
  uint32_t puVar6;
  uint32_t puVar7;
  uint uVar8;
  undefined4 uVar9;
  int iVar10;
  uint uVar11;
  uint uVar12;
  uint uVar13;
  uint uVar14;
  uint uVar15;
  uint uVar16;
  uint uVar17;
  F33CanIfTxRecord local_28;
  
  uVar8 = (uint)controller;
  puVar6 = 0xfebeb800u;
  puVar7 = 0x23dfcu;
  uVar14 = 1;
  if (uVar8 < DAT_00021970) {
    local_28.length = record->length;
    uVar16 = (uint)local_28.length;
    uVar15 = record->class_flags | 0x80;
    local_28.raw_id = record->raw_id;
    local_28.class_flags = (uchar)uVar15;
    local_28.source_pdu = record->source_pdu;
    puVar4 = ((void *)camry_host_ptr((uint32_t)(record->data)));
    local_28.data = camry_host_addr(puVar4);
    if (uVar15 == 0x81) {
      if (0x40 < uVar16) {
        uVar16 = 0x40;
      }
      puVar6 = 0xfebeb800u;
      uVar9 = FUN_0007a2da();
      for (uVar5 = 0; uVar5 < uVar16; uVar5 = uVar5 + 1 & 0xff) {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(uVar5 - 0x684e))))) = puVar4[uVar5];
      }
      ((void)(uVar9), thunk_FUN_0006a4c4());
      local_28.data = puVar6 + -0x684e;
      iVar10 = (*(int (*)())*(code **)(puVar7 + uVar8 * 4 + -0x24fc))(uVar8,&local_28);
      uVar16 = (uint)local_28.length;
      if (iVar10 != 0) {
        return 1;
      }
    }
    iVar10 = FUN_0007fbdc(uVar8,route);
    uVar9 = FUN_0007a2da();
    if (((((*((short *)camry_host_ptr((uint32_t)(puVar6 + uVar8 * 2 + -0x6f28)))) == 0x57a8) && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(uVar8 - 0x6efd))))) == 'Z'))
        && ((*((short *)camry_host_ptr((uint32_t)(puVar6 + uVar8 * 2 + -0x6f02)))) == 0x5555)) && (iVar10 != 0xff)) {
      puVar1 = ((ushort *)camry_host_ptr((uint32_t)((short)iVar10 * 10 + *(int *)(puVar7 + uVar8 * 4 + -0x2518))));
      queue_index = puVar1[4];
      uVar5 = (uint)queue_index;
      capacity_words = *puVar1;
      uVar8 = (uint)capacity_words;
      if (uVar16 < 9) {
        uVar13 = (uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar6 + uVar5 * 6 + -0x6f26))));
        uVar12 = (uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar6 + uVar5 * 6 + -0x6f22))));
        if (((int)((uVar13 + 2) - uVar8) < 0 || uVar13 + 2 == uVar8) && (uVar12 <= uVar8)) {
          uVar11 = uVar8 - uVar13 & 0xffff;
          uVar14 = uVar13;
          uVar17 = uVar8;
          if (uVar11 < 7) {
            uVar12 = uVar12 + uVar11;
            uVar14 = 0;
            uVar17 = uVar13;
          }
          if (uVar8 < (uVar12 + 5 & 0xffff)) {
            uVar14 = 2;
          }
          else {
            if (uVar17 < uVar8) {
              puVar2 = ((undefined4 *)camry_host_ptr((uint32_t)(uVar17 * 4 + *(int *)(puVar7 + uVar5 * 4 + -0x23a8))));
              *puVar2 = 0xffffffff;
              puVar2[1] = 0;
            }
            iVar10 = (*((int *)camry_host_ptr((uint32_t)(puVar7 + uVar5 * 4 + -0x23a8))));
            (*((short *)camry_host_ptr((uint32_t)(puVar6 + uVar5 * 6 + -0x6f26)))) = (short)uVar14 + 5;
            (*((short *)camry_host_ptr((uint32_t)(puVar6 + uVar5 * 6 + -0x6f22)))) = (short)(uVar12 + 5);
            puVar3 = ((uint *)camry_host_ptr((uint32_t)(uVar14 * 4 + iVar10)));
            uVar8 = (uint)local_28.source_pdu * 0x10000 + uVar15 * 0x100 + uVar16;
            *puVar3 = uVar8;
            puVar3[1] = ~uVar8;
            puVar3[2] = local_28.raw_id;
            for (uVar8 = 0; uVar8 < uVar16; uVar8 = uVar8 + 1 & 0xff) {
              (*((uchar *)camry_host_ptr((uint32_t)((int)camry_host_addr(puVar3) + uVar8 + 0xc)))) = ((uint8_t *)camry_host_ptr((uint32_t)(local_28.data)))[uVar8];
            }
            uVar14 = 0;
          }
        }
      }
      else {
        uVar14 = f33_enqueue_large_can_tx(&local_28,queue_index,capacity_words);
      }
    }
    ((void)(uVar9), thunk_FUN_0006a4c4());
  }
  return uVar14;
}



/* Decode source namespace and construct transmit record. Real R10 return defaults1 and
   propagates7FD46 status; not void. */

uint f33_canif_transmit(ushort source_pdu,F33PduInfo *info)

{
  uint *puVar1;
  uint uVar2;
  uint uVar3;
  undefined *puVar4;
  F33CanIfTxRecord local_10;
  
  puVar4 = ((undefined *)camry_host_ptr((uint32_t)(source_pdu & 0xf800)));
  uVar3 = source_pdu & 0x7ff;
  if ((source_pdu & 0xf800) != 0) {
    if (puVar4 == ((undefined *)camry_host_ptr((uint32_t)(0x6000)))) {
      puVar4 = ((undefined *)camry_host_ptr((uint32_t)(0x1)));
    }
    else if (puVar4 == ((undefined *)camry_host_ptr((uint32_t)(0x800)))) {
      puVar4 = ((undefined *)camry_host_ptr((uint32_t)(0x2)));
    }
    else if (puVar4 == ((undefined *)camry_host_ptr(0xb800u))) {
      puVar4 = ((undefined *)camry_host_ptr((uint32_t)(0x3)));
    }
    else if (puVar4 == ((undefined *)camry_host_ptr((uint32_t)(0xc000)))) {
      puVar4 = ((undefined *)camry_host_ptr((uint32_t)(0x4)));
    }
    else if (puVar4 == ((undefined *)camry_host_ptr((uint32_t)(0xf800)))) {
      puVar4 = ((undefined *)camry_host_ptr((uint32_t)(0x5)));
    }
    else {
      puVar4 = ((undefined *)camry_host_ptr((uint32_t)(0xff)));
    }
  }
  uVar2 = 1;
  if ((puVar4 != ((undefined *)camry_host_ptr((uint32_t)(0xff)))) && (uVar3 < (ushort)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x21a48u + (uint32_t)((int)camry_host_addr(puVar4)) * 2u)))))) {
    puVar1 = ((uint *)camry_host_ptr((uint32_t)((&PTR_DAT_00021994)[(int)camry_host_addr(puVar4)] + uVar3 * 8)));
    local_10.raw_id = *puVar1;
    local_10.class_flags = (uchar)(1 << ((uint)camry_host_addr(puVar4) & 0x1f));
    local_10.length = (uchar)info->length;
    local_10.data = info->data;
    local_10.source_pdu = source_pdu;
    uVar2 = f33_snapshot_and_enqueue_can_tx
                      ((uchar)puVar1[1],(*((ushort *)camry_host_ptr((uint32_t)((int)camry_host_addr(puVar1) + 6)))) | (ushort)((int)camry_host_addr(puVar4) << 8),
                       &local_10);
  }
  return uVar2;
}


