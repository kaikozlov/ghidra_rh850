#include "common.h"


/* WARNING: Removing unreachable block (ram,0x0004c0de) */
/* WARNING: Removing unreachable block (ram,0x0004c0aa) */

void FUN_0004c000(void)

{
  ushort uVar1;
  int iVar2;
  ushort uVar3;
  
  uVar1 = DAT_febee8cc & 0xff00;
  DAT_febe80dd = 0;
  if (((uVar1 != 0x400) && ((uVar1 != 0x500 || (DAT_febee81f != '\x11')))) ||
     (uVar3 = DAT_febe6764 & 0x1ff, (DAT_febe6764 & 0x1ff) != 0)) {
    uVar3 = 1;
  }
  DAT_febe80e1 = (char)uVar3;
  if (((uVar1 != 0x400) && ((uVar1 != 0x500 || (DAT_febee81f != '\x11')))) ||
     ((DAT_febee887 != '\0' || (uVar1 = DAT_febe6764 & 0x1ff, (DAT_febe6764 & 0x1ff) != 0)))) {
    uVar1 = 1;
  }
  DAT_febe80e2 = (char)uVar1;
  if ((((DAT_febe82ba == 0) && (DAT_febe82c2 == 0)) && (DAT_febe82c4 == 0)) &&
     ((DAT_febee857 != '\"' && (DAT_febee858 != '\"')))) {
    DAT_febe80de = DAT_febee859 == '\"';
  }
  else {
    DAT_febe80de = true;
  }
  if (uVar1 == 1) {
    DAT_febe8152 = 0;
  }
  else {
    DAT_febe8152 = (short)((DAT_febe66a8 * 100) / 0x100);
    iVar2 = (int)DAT_febe8152;
    if (iVar2 + -1000 < 0 == (iVar2 < 0 && -1 < iVar2 + -1000) && iVar2 != 1000) {
      DAT_febe8152 = 1000;
    }
    else if (iVar2 + 1000 < 0 != (-1 < iVar2 && iVar2 + 1000 < 0)) {
      DAT_febe8152 = -1000;
    }
  }
  DAT_febe8158 = 0;
  if (uVar3 != 1) {
    DAT_febe8158 = (undefined2)((DAT_febe6718 * -100) / 0x80);
  }
  return;
}



void FUN_0004c142(void)

{
  DAT_febe8103 = 0;
  DAT_febe8104 = 0;
  DAT_febe8108 = 0;
  return;
}



char FUN_0004c1c0(void)

{
  char cVar1;
  
  if ((DAT_febe8100 == '\x01') && (DAT_febee82b == '\0')) {
    DAT_febe812c = 'Z';
    DAT_febe812b = 0;
    cVar1 = DAT_febee82b;
  }
  else {
    cVar1 = DAT_febe8100;
    if (DAT_febe812c != 'Z') {
      DAT_febe812a = DAT_febe5339;
      return DAT_febee82b;
    }
  }
  if ((DAT_febe812b < DAT_0002fbf8) && (DAT_febe812a == DAT_febe5339)) {
    DAT_febe812b = DAT_febe812b + 1;
  }
  else {
    DAT_febe812b = '\0';
    DAT_febe812c = '\0';
    cVar1 = DAT_febee82b;
  }
  DAT_febe812a = DAT_febe5339;
  return cVar1;
}



void FUN_0004c216(undefined1 param_1)

{
  if (((DAT_febe6764 & 3) == 0) || (DAT_febe8143 == '\0')) {
    DAT_febe8101 = 0;
  }
  else {
    param_1 = 7;
    DAT_febe8101 = 1;
  }
  DAT_febe8100 = param_1;
  return;
}



void FUN_0004c238(void)

{
  undefined4 uVar1;
  
  uVar1 = FUN_0004c1c0();
  FUN_0004c216(uVar1);
  return;
}



void FUN_0004c24a(void)

{
  uint uVar1;
  
  uVar1 = DAT_febe82a0 - 1;
  if (3 < uVar1) {
    if (uVar1 == 4) {
      DAT_febe8102 = DAT_febe82ae;
      DAT_febe8105 = DAT_febe82ad;
      DAT_febe8106 = DAT_febe82aa;
      DAT_febe8107 = DAT_febe82ab;
      DAT_febe8109 = DAT_febe82ac;
      DAT_febe810a = 1;
      return;
    }
    if (0xd < uVar1) {
      if (uVar1 == 0xe) {
        DAT_febe8102 = DAT_febe82ae;
        DAT_febe8105 = DAT_febe82ad;
        DAT_febe8106 = DAT_febe82aa;
        DAT_febe8107 = DAT_febe82ab;
        DAT_febe8109 = DAT_febe82ac;
        DAT_febe810a = 2;
        return;
      }
      if (uVar1 != 0xf) {
        DAT_febe8102 = DAT_febe82ae;
        DAT_febe8105 = DAT_febe82ad;
        DAT_febe8106 = DAT_febe82aa;
        DAT_febe8107 = DAT_febe82ab;
        DAT_febe8109 = DAT_febe82ac;
        DAT_febe810a = 0;
        return;
      }
    }
  }
  DAT_febe810a = 3;
  DAT_febe8102 = DAT_febe82ae;
  DAT_febe8105 = DAT_febe82ad;
  DAT_febe8106 = DAT_febe82aa;
  DAT_febe8107 = DAT_febe82ab;
  DAT_febe8109 = DAT_febe82ac;
  return;
}



void FUN_0004c294(void)

{
  DAT_febe80e3 = DAT_febee848;
  return;
}



/* Constant-block fill: 8 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_4c29e(void)

{
  DAT_febe80e4 = 0;
  DAT_febe80e5 = 0;
  DAT_febe80fc = 0;
  DAT_febe80e6 = 0;
  DAT_febe80e7 = 0;
  DAT_febe80e8 = 0;
  DAT_febe80e9 = 0;
  DAT_febe80ea = 0;
  return;
}



/* Paired constant publisher: DAT_febe80fa = 0xff; and DAT_febe80fb = 0xff;; shape-classified from
   the canonical corpus. Target cells not yet named. */

void FUN_0004c2b4(void)

{
  DAT_febe80fa = 0xff;
  DAT_febe80fb = 0xff;
  return;
}



/* Constant-block fill: 5 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_4c2c0(void)

{
  DAT_febe80f3 = 0;
  DAT_febe80eb = 0;
  DAT_febe80ed = 0;
  DAT_febe80ef = 0;
  DAT_febe80f1 = 0;
  return;
}



/* Paired constant publisher: DAT_febe8154 = 0; and DAT_febe80df = 1;; shape-classified from the
   canonical corpus. Target cells not yet named. */

void FUN_0004c2d0(void)

{
  DAT_febe8154 = 0;
  DAT_febe80df = 1;
  return;
}



/* Constant-block fill: 11 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_4c2dc(void)

{
  DAT_febe80ee = 0;
  DAT_febe80f0 = 0;
  DAT_febe80f2 = 0;
  DAT_febe80ec = DAT_febee834;
  DAT_febe80f4 = 0;
  DAT_febe80f6 = DAT_febee82f;
  DAT_febe80f7 = DAT_febee83d;
  DAT_febe80f8 = DAT_febee83b;
  DAT_febe80f9 = DAT_febee83c;
  DAT_febe80e0 = DAT_febee83a;
  DAT_febe8156 = DAT_febee8bc;
  return;
}



void FUN_0004c314(void)

{
  DAT_febe80dc = DAT_febee830;
  return;
}



/* Constant-block fill: 5 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_4c31e(void)

{
  DAT_febe8113 = 0;
  DAT_febe8114 = 0;
  DAT_febe8115 = 0;
  DAT_febe8116 = 0;
  DAT_febe8117 = 0;
  return;
}



void FUN_0004c32e(void)

{
  DAT_febe8170 = 0;
  DAT_febe815c = 0;
  DAT_febe8118 = 0;
  DAT_febe8119 = 0;
  return;
}



void FUN_0004c33c(void)

{
  DAT_febe815a = 0;
  DAT_febe811a = 0;
  DAT_febe811b = 0;
  DAT_febe812d = 0;
  return;
}



/* Constant-block fill: 16 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_4c34a(void)

{
  DAT_febe811d = 0;
  DAT_febe811e = 0;
  DAT_febe811f = 0;
  DAT_febe8121 = 0;
  DAT_febe8123 = 0;
  DAT_febe8120 = 0;
  DAT_febe8122 = 0;
  DAT_febe8124 = 0;
  DAT_febe8126 = 0;
  DAT_febe8135 = 0;
  DAT_febe8131 = 0;
  DAT_febe815e = 0;
  DAT_febe8125 = 0;
  DAT_febe8132 = 0;
  DAT_febe8133 = 0;
  DAT_febe811c = 0;
  return;
}



/* Constant-block fill: 5 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_4c370(void)

{
  DAT_febe8160 = 0;
  DAT_febe8127 = 0;
  DAT_febe8128 = 0;
  DAT_febe8129 = 0;
  DAT_febe8134 = 0;
  return;
}



/* WARNING: Removing unreachable block (ram,0x0004c3b4) */
/* WARNING: Removing unreachable block (ram,0x0004c388) */

void FUN_0004c380(void)

{
  int iVar1;
  
  iVar1 = (int)(DAT_febe6776 / 8);
  if (iVar1 + -0x708 < 0 == (iVar1 < 0 && -1 < iVar1 + -0x708)) {
    iVar1 = 0x708;
  }
  if (iVar1 + 0x708 < 0 != (-1 < iVar1 && iVar1 + 0x708 < 0)) {
    iVar1 = -0x708;
  }
  DAT_febe8166 = (short)iVar1;
  iVar1 = (DAT_febe6776 * 0x652e) / 0x2000;
  if (iVar1 + -0x7fff < 0 == (iVar1 < 0 && -1 < iVar1 + -0x7fff)) {
    iVar1 = 0x7fff;
  }
  if (iVar1 + 0x8000 < 0 == (-1 < iVar1 && iVar1 + 0x8000 < 0)) {
    DAT_febe816a = (undefined2)iVar1;
  }
  else {
    DAT_febe816a = 0x8000;
  }
  return;
}



/* WARNING: Removing unreachable block (ram,0x0004c454) */
/* WARNING: Removing unreachable block (ram,0x0004c442) */
/* WARNING: Removing unreachable block (ram,0x0004c430) */
/* WARNING: Removing unreachable block (ram,0x0004c40a) */
/* WARNING: Removing unreachable block (ram,0x0004c3fe) */

void FUN_0004c3d2(void)

{
  int iVar1;
  int iVar2;
  
  DAT_febe8174 = 0x1ffff;
  if (DAT_febee94c + -0x1ffff < 0 != (DAT_febee94c < 0 && -1 < DAT_febee94c + -0x1ffff)) {
    DAT_febe8174 = DAT_febee94c;
  }
  if (DAT_febe8174 + 0x20000 < 0 != (-1 < DAT_febe8174 && DAT_febe8174 + 0x20000 < 0)) {
    DAT_febe8174 = -0x20000;
  }
  DAT_febe8178 = (((DAT_febee948 * 0x168) / 0x10) * 10) / 0x1000;
  if (DAT_febe8178 + -0x77f8 < 0 == (DAT_febe8178 < 0 && -1 < DAT_febe8178 + -0x77f8)) {
    DAT_febe8178 = 0x77f8;
  }
  if (DAT_febe8178 + 0x7807 < 0 != (-1 < DAT_febe8178 && DAT_febe8178 + 0x7807 < 0)) {
    DAT_febe8178 = -0x7807;
  }
  iVar1 = (int)(char)((int)camry_host_addr((((undefined *)camry_host_ptr(0x182b8u)) + DAT_febe8178)) % 0xf);
  if (iVar1 + -8 < 0 == (iVar1 < 0 && -1 < iVar1 + -8)) {
    iVar1 = iVar1 + -0xf;
  }
  iVar2 = (int)(short)((DAT_febee954 * 36000) / 0x10000);
  if (iVar2 + -0x7ff < 0 == (iVar2 < 0 && -1 < iVar2 + -0x7ff)) {
    iVar2 = 0x7ff;
  }
  if (iVar2 + 0x800 < 0 != (-1 < iVar2 && iVar2 + 0x800 < 0)) {
    iVar2 = -0x800;
  }
  DAT_febe813d = DAT_febee888 == 'Z';
  DAT_febe816e = (short)iVar2;
  DAT_febe8138 = (char)iVar1;
  DAT_febe8164 = (undefined2)((DAT_febe8178 - iVar1) / 0xf);
  DAT_febe8168 = DAT_febe8164;
  DAT_febe8139 = DAT_febe813d;
  DAT_febe813b = DAT_febe813d;
  return;
}



/* WARNING: Removing unreachable block (ram,0x0004c578) */
/* WARNING: Removing unreachable block (ram,0x0004c56a) */
/* WARNING: Removing unreachable block (ram,0x0004c518) */
/* WARNING: Removing unreachable block (ram,0x0004c4fe) */
/* WARNING: Removing unreachable block (ram,0x0004c4e6) */
/* WARNING: Removing unreachable block (ram,0x0004c4b2) */

void FUN_0004c490(void)

{
  char cVar1;
  ushort uVar2;
  char cVar3;
  uint32_t puVar5;
  undefined1 uVar6;
  int iVar7;
  int iVar8;
  undefined1 uStack_11;
  int iVar4;
  
  puVar5 = 0xfebeb800u;
  FUN_0004c380();
  FUN_0004c3d2();
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x58ad))))) == 'Z') {
    iVar8 = (int)(short)(((*((short *)camry_host_ptr((uint32_t)(puVar5 + -0x5158)))) * 100) / 0x100);
    if (iVar8 + -1000 < 0 == (iVar8 < 0 && -1 < iVar8 + -1000) && iVar8 != 1000) {
      iVar8 = 1000;
    }
    else if (iVar8 + 1000 < 0 != (-1 < iVar8 && iVar8 + 1000 < 0)) {
      iVar8 = -1000;
    }
  }
  else {
    iVar8 = (int)(*((short *)camry_host_ptr((uint32_t)(puVar5 + -0x36ae))));
  }
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x522d)))));
  FUN_0006a5cc((int)(short)(iVar8 / 10),&uStack_11);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x36ca))))) = uStack_11;
  cVar3 = (char)((iVar8 + 1000) % 10);
  iVar4 = (int)cVar3;
  if (iVar8 < 0) {
    iVar7 = 6;
  }
  else {
    iVar7 = 5;
  }
  if (iVar4 - iVar7 < 0 == (iVar4 < 0 && -1 < iVar4 - iVar7)) {
    iVar4 = (int)(char)(cVar3 + -10);
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x36be))))) = (char)iVar4;
  uVar6 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x37b0)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x36c6))))) = (char)((iVar8 - iVar4) / 10);
  cVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x36bc)))));
  if (cVar3 == '\0') {
    if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x37af))))) == (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x36bb)))))) || (1 < (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3898))))))) {
      uVar6 = 1;
    }
    else {
      cVar3 = 'Z';
    }
  }
  uVar2 = (*((ushort *)camry_host_ptr((uint32_t)(0x30d2u + (int)(puVar5 + 6)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x36bc))))) = cVar3;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x36bb))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x37af)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x36c2))))) = uVar6;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-13999))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-14000))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x36c9))))) = cVar1 != '\0';
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x36c4))))) = cVar1 != '\0';
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + -0x3694)))) =
       (short)((((int)(-(int)(*((short *)camry_host_ptr((uint32_t)(puVar5 + -0x50e8)))) * (uint)uVar2) / 0x100) * 100) / 0x2000);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x36c0))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3719)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x36bf))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x371a)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x36c1))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbc75u + (uint32_t)((int)puVar5) * 1u))));
  return;
}



/* Sequential initializer chain: 19 unconditional calls and no other statements; shape-verified. The
   called sequence is the function's entire behavior; chain family members differ in callee sets. */

void f33_run_init_chain_4c590(void)

{
  FUN_0004c000();
  FUN_0004c0e8();
  FUN_0004c142();
  FUN_0004c14e();
  FUN_0004c238();
  FUN_0004c24a();
  FUN_0004c294();
  f33_fill_constant_block_4c29e();
  FUN_0004c2b4();
  f33_fill_constant_block_4c2c0();
  FUN_0004c2d0();
  f33_fill_constant_block_4c2dc();
  FUN_0004c314();
  f33_fill_constant_block_4c31e();
  FUN_0004c32e();
  FUN_0004c33c();
  f33_fill_constant_block_4c34a();
  f33_fill_constant_block_4c370();
  FUN_0004c490();
  return;
}



void FUN_0004c5e8(undefined1 param_1)

{
  DAT_febe8143 = param_1;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4c5ee(void)

{
  return;
}



void FUN_0004c5f0(void)

{
  DAT_febe8190 = DAT_0002fbfc;
  return;
}



void FUN_0004c5fe(void)

{
  if (DAT_febee82a == '\0') {
    if (DAT_febe8190 <= DAT_0002fbfc) {
      DAT_febe8190 = DAT_febe8190 + 1;
    }
  }
  else {
    DAT_febe8190 = 0;
  }
  if ((DAT_febee82a == 'Z') || (DAT_febe8190 <= DAT_0002fbfc)) {
    DAT_febe818c = 0x5a;
  }
  else {
    DAT_febe818c = 0;
  }
  return;
}



void FUN_0004c63c(void)

{
  DAT_febe8187 = 0;
  if (DAT_febee836 == '\x01') {
    DAT_febe8187 = 0x5a;
  }
  return;
}



void FUN_0004c650(void)

{
  int iVar1;
  byte bVar2;
  uchar uVar3;
  char cVar4;
  char cVar5;
  char cVar6;
  byte bVar7;
  uint uVar8;
  byte bVar9;
  int iVar10;
  int iVar11;
  uint uVar12;
  
  cVar6 = DAT_febee87e;
  cVar5 = DAT_febee812;
  cVar4 = DAT_febe818c;
  bVar9 = DAT_febe80c9;
  uVar3 = f33_internal_source_admission_state;
  uVar8 = (uint)DAT_febee8cc;
  iVar11 = (int)DAT_febee8dc;
  iVar10 = (int)DAT_febe6790;
  bVar7 = 0;
  uVar12 = 0;
  do {
    bVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe817du + (uint32_t)(uVar12) * 1u))));
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe817du + (uint32_t)(uVar12) * 1u)))) = 0;
    uVar12 = uVar12 + 1;
    bVar7 = bVar7 | bVar2;
  } while (uVar12 < 10);
  if ((((((uVar8 & 0xff00) - 0x100 < 0x201) || (cVar6 == 'Z')) ||
       (iVar1 = iVar11 + -0x569a, ((iVar1 < 0) || (iVar11 < 0)))) ||
      (iVar11 = iVar10 + -0x569a, ((iVar11 < 0) || (iVar10 < 0)))) ||
     (((uVar3 != '\0' && (uVar3 != '\x01')) ||
      ((cVar5 != '\x11' || ((DAT_febe8188 = bVar9 & 1, (bVar9 & 1) != 0 || (bVar7 == 0x5a)))))))) {
    DAT_febe8188 = 0x5a;
  }
  bVar9 = DAT_febe8188;
  if ((DAT_febe818a != 'Z') && (cVar4 != '\0')) {
    bVar9 = 0;
  }
  DAT_febe818a = bVar9;
  return;
}



void FUN_0004c6e6(void)

{
  DAT_febe8189 = DAT_febe80c9 & 2;
  if ((((((DAT_febe80c9 & 2) != 0) || ((DAT_febe6764 & 0x1ff) != 0)) || (DAT_febe82ba != 0)) ||
      ((DAT_febe82c2 != 0 || (DAT_febe82c4 != 0)))) ||
     ((DAT_febee857 == '\"' || ((DAT_febee858 == '\"' || (DAT_febee859 == '\"')))))) {
    DAT_febe8189 = 0x5a;
  }
  return;
}



void FUN_0004c772(void)

{
  DAT_febe818d = DAT_febee88c;
  DAT_febe818e = DAT_febee88d;
  return;
}



void FUN_0004c784(void)

{
  FUN_0004c738();
  FUN_0004c772();
  return;
}



/* Store low8(status) at817D+low8(index) only for index<10. Does not itself report a diagnostic
   event or select a fault-action record. */

void f33_set_monitor_pending_projection(uchar index,uchar status)

{
  if (index < 10) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe817du + (uint32_t)(index) * 1u)))) = status;
  }
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4c7a6(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4c7a8(void)

{
  return;
}



void FUN_0004c7aa(void)

{
  char cVar1;
  uint32_t puVar2;
  uint uVar3;
  
  puVar2 = 0xfebeb800u;
  DAT_febe8c53 = DAT_febe810b;
  DAT_febe8c54 = DAT_febe810c;
  DAT_febe8c55 = DAT_febe810d;
  DAT_febe8c56 = DAT_febe810e;
  DAT_febe8c57 = DAT_febe810f;
  DAT_febe8c58 = DAT_febe8110;
  DAT_febe8c59 = DAT_febe8111;
  DAT_febe8c5a = DAT_febe8112;
  FUN_0007d31e(0x2c,0x27,8,0,((undefined *)camry_host_ptr(0xfebe8c53u)));
  FUN_0007d31e(0x2d, 0x28, 8, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x2bac))));
  FUN_0007d31e(0x2e, 0x29, 8, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x2bab))));
  FUN_0007d31e(0x2f, 0x2a, 8, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x2baa))));
  FUN_0007d31e(0x30, 0x2b, 8, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x2ba9))));
  FUN_0007d31e(0x31, 0x2c, 8, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x2ba8))));
  FUN_0007d31e(0x32, 0x2d, 8, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x2ba7))));
  FUN_0007d31e(0x33, 0x2e, 8, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x2ba6))));
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x386a)))));
  uVar3 = FUN_0007d0ea(3);
  if ((cVar1 == 'Z') && ((uVar3 >> 4 & 1) == 0)) {
    FUN_0007e612(3);
  }
  else if ((cVar1 == '\0') && ((uVar3 >> 4 & 1) != 0)) {
    FUN_0007e46a(3,0x40);
    FUN_0007e696(3);
  }
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4c8dc(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4c8de(void)

{
  return;
}



void FUN_0004c8e0(void)

{
  char cVar1;
  uint32_t puVar2;
  uint uVar3;
  
  puVar2 = 0xfebeb800u;
  DAT_febe8c5d = 9;
  DAT_febe8c5e = 0;
  DAT_febe8c30 = 0;
  FUN_0007d31e(0x34,0x2f,8,0,((undefined *)camry_host_ptr(0xfebe8c5du)));
  FUN_0007d31e(0x35, 0x30, 1, 7, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x2ba2))));
  FUN_0007d31e(0x36, 0x31, 0x10, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x2bd0))));
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x386a)))));
  uVar3 = FUN_0007d0ea(4);
  if ((cVar1 == 'Z') && ((uVar3 >> 4 & 1) == 0)) {
    FUN_0007e612(4);
  }
  else if ((cVar1 == '\0') && ((uVar3 >> 4 & 1) != 0)) {
    FUN_0007e46a(4,0x40);
    FUN_0007e696(4);
  }
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4c976(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4c978(void)

{
  return;
}



void FUN_0004c97a(void)

{
  uint uVar1;
  char *pcVar2;
  uint uVar3;
  uint32_t puVar4;
  char cVar5;
  char acStack_28 [32];
  
  puVar4 = 0xfebeb800u;
  DAT_febe8c4c = 0;
  DAT_febe8c32 = DAT_febe8136;
  DAT_febe8c33 = DAT_febe8137;
  DAT_febe8c24 = DAT_febe8164;
  DAT_febe8c34 = DAT_febe8138;
  DAT_febe8c26 = DAT_febe8166;
  DAT_febe8c49 = DAT_febe8139;
  DAT_febe8c35 = DAT_febe80de;
  DAT_febe8c36 = DAT_febe80e3;
  DAT_febe8c37 = DAT_febe80e2;
  DAT_febe8c38 = DAT_febe813a;
  DAT_febe8c28 = DAT_febe8168;
  DAT_febe8c39 = DAT_febe813b;
  DAT_febe8c20 = DAT_febe8174;
  DAT_febe8c3a = DAT_febe813c;
  DAT_febe8c3b = DAT_febe813d;
  DAT_febe8c3c = DAT_febe813e;
  DAT_febe8c3d = DAT_febe813f;
  DAT_febe8c3e = DAT_febe817c;
  DAT_febe8c2a = DAT_febe816a;
  DAT_febe8c3f = DAT_febe80f6;
  DAT_febe8c40 = DAT_febe80f7;
  DAT_febe8c41 = DAT_febe80f8;
  DAT_febe8c42 = DAT_febe80f9;
  DAT_febe8c43 = DAT_febe80ec;
  DAT_febe8c44 = DAT_febe8140;
  DAT_febe8c45 = DAT_febe8141;
  DAT_febe8c4a = DAT_febe818e;
  DAT_febe8c4b = DAT_febe818d;
  DAT_febe8c46 = DAT_febe8142;
  DAT_febe8c47 = DAT_febe80e0;
  DAT_febe8c2c = DAT_febe8156;
  DAT_febe8c2e = DAT_febe816c;
  DAT_febe8c4d = DAT_febe8150;
  DAT_febe8c4e = DAT_febe8151;
  FUN_0007d31e(0,0,8,0,((undefined *)camry_host_ptr(0xfebe8c32u)));
  FUN_0007d31e(1, 2, 1, 1, ((undefined *)camry_host_ptr((uint32_t)(puVar4 + -0x2bb4))));
  FUN_0007d31e(2, 2, 1, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar4 + -0x2bcd))));
  FUN_0007d31e(3, 3, 0xc, 4, ((undefined *)camry_host_ptr((uint32_t)(puVar4 + -0x2bdc))));
  FUN_0007d31e(4, 4, 4, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar4 + -0x2bcc))));
  FUN_0007d31e(5, 5, 0xc, 4, ((undefined *)camry_host_ptr((uint32_t)(puVar4 + -0x2bda))));
  FUN_0007d31e(6, 6, 1, 3, ((undefined *)camry_host_ptr((uint32_t)(puVar4 + -0x2bb7))));
  FUN_0007d31e(7, 6, 1, 2, ((undefined *)camry_host_ptr((uint32_t)(puVar4 + -0x2bcb))));
  FUN_0007d31e(8, 6, 1, 1, ((undefined *)camry_host_ptr((uint32_t)(puVar4 + -0x2bca))));
  FUN_0007d31e(9, 6, 1, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar4 + -0x2bc9))));
  FUN_0007d31e(0xb, 8, 8, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar4 + -0x2bc8))));
  FUN_0007d31e(0xc, 9, 0xc, 4, ((undefined *)camry_host_ptr((uint32_t)(puVar4 + -0x2bd8))));
  FUN_0007d31e(0xd, 10, 1, 3, ((undefined *)camry_host_ptr((uint32_t)(puVar4 + -0x2bc7))));
  FUN_0007d31e(0xe, 0xb, 0x12, 6, ((undefined *)camry_host_ptr((uint32_t)(puVar4 + -0x2be0))));
  FUN_0007d31e(0xf, 0xd, 1, 5, ((undefined *)camry_host_ptr((uint32_t)(puVar4 + -0x2bc6))));
  FUN_0007d31e(0x10, 0xd, 1, 4, ((undefined *)camry_host_ptr((uint32_t)(puVar4 + -0x2bc5))));
  FUN_0007d31e(0x11, 0xd, 1, 3, ((undefined *)camry_host_ptr((uint32_t)(puVar4 + -0x2bc4))));
  FUN_0007d31e(0x12, 0xd, 1, 2, ((undefined *)camry_host_ptr((uint32_t)(puVar4 + -0x2bc3))));
  FUN_0007d31e(0x13, 0xd, 2, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar4 + -0x2bc2))));
  FUN_0007d31e(0x14, 0xe, 0x10, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar4 + -0x2bd6))));
  FUN_0007d31e(0x15, 0x10, 1, 5, ((undefined *)camry_host_ptr((uint32_t)(puVar4 + -0x2bc1))));
  FUN_0007d31e(0x16, 0x10, 1, 4, ((undefined *)camry_host_ptr((uint32_t)(puVar4 + -0x2bc0))));
  FUN_0007d31e(0x17, 0x10, 1, 3, ((undefined *)camry_host_ptr((uint32_t)(puVar4 + -0x2bbf))));
  FUN_0007d31e(0x18, 0x10, 2, 1, ((undefined *)camry_host_ptr((uint32_t)(puVar4 + -0x2bbe))));
  FUN_0007d31e(0x19, 0x10, 1, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar4 + -0x2bbd))));
  FUN_0007d31e(0x1a, 0x11, 1, 7, ((undefined *)camry_host_ptr((uint32_t)(puVar4 + -0x2bbc))));
  FUN_0007d31e(0x1b, 0x11, 1, 6, ((undefined *)camry_host_ptr((uint32_t)(puVar4 + -0x2bbb))));
  FUN_0007d31e(0x1c, 0x11, 1, 5, ((undefined *)camry_host_ptr((uint32_t)(puVar4 + -0x2bb6))));
  FUN_0007d31e(0x1d, 0x11, 1, 4, ((undefined *)camry_host_ptr((uint32_t)(puVar4 + -0x2bb5))));
  FUN_0007d31e(0x1e, 0x11, 4, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar4 + -0x2bba))));
  FUN_0007d31e(0x1f, 0x13, 1, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar4 + -0x2bb9))));
  FUN_0007d31e(0x20, 0x14, 0x10, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar4 + -0x2bd4))));
  FUN_0007d31e(0x21, 0x16, 0x10, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar4 + -0x2bd2))));
  FUN_0007d31e(0x22, 0x1b, 1, 1, ((undefined *)camry_host_ptr((uint32_t)(puVar4 + -0x2bb3))));
  FUN_0007d31e(0x23, 0x1b, 1, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar4 + -0x2bb2))));
  cVar5 = '\0';
  uVar3 = 0;
  do {
    uVar1 = uVar3 + 1;
    acStack_28[uVar3] = '\0';
    uVar3 = uVar1;
  } while (uVar1 < 0x20);
  FUN_0007d05c(0, camry_host_addr(acStack_28));
  uVar3 = 0;
  do {
    pcVar2 = acStack_28 + uVar3;
    uVar3 = uVar3 + 1;
    cVar5 = cVar5 + *pcVar2;
  } while (uVar3 < 7);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x2bb8))))) = cVar5 + '8';
  FUN_0007d31e(10, 7, 8, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar4 + -0x2bb8))));
  cVar5 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x386a)))));
  uVar3 = FUN_0007d0ea(0);
  if ((cVar5 == 'Z') && ((uVar3 & 0x10) == 0)) {
    FUN_0007e612(0);
  }
  else if ((cVar5 == '\0') && ((uVar3 >> 4 & 1) != 0)) {
    FUN_0007e46a(0,0x40);
    FUN_0007e696(0);
  }
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4ce04(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4ce06(void)

{
  return;
}



void FUN_0004ce08(void)

{
  char cVar1;
  uint32_t puVar2;
  uint uVar3;
  
  puVar2 = 0xfebeb800u;
  DAT_febe8c4f = DAT_febe8105;
  DAT_febe8c50 = DAT_febe8106;
  DAT_febe8c51 = DAT_febe8107;
  DAT_febe8c52 = DAT_febe8109;
  FUN_0007d1dc(0x28,0x25,2,6,((undefined *)camry_host_ptr(0xfebe8c4fu)));
  FUN_0007d1dc(0x29, 0x25, 3, 3, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x2bb0))));
  FUN_0007d1dc(0x2a, 0x26, 3, 1, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x2baf))));
  FUN_0007d1dc(0x2b, 0x26, 1, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x2bae))));
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x386a)))));
  uVar3 = FUN_0007d0ea(2);
  if ((cVar1 == 'Z') && ((uVar3 >> 4 & 1) == 0)) {
    FUN_0007e612(2);
  }
  else if ((cVar1 == '\0') && ((uVar3 >> 4 & 1) != 0)) {
    FUN_0007e46a(2,0x40);
    FUN_0007e46a(2,0x80);
    FUN_0007e696(2);
  }
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4cecc(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4cece(void)

{
  return;
}



void FUN_0004ced0(void)

{
  char cVar1;
  uint32_t puVar2;
  uint uVar3;
  
  puVar2 = 0xfebeb800u;
  DAT_febe8c5b = DAT_febe8100;
  DAT_febe8c5c = DAT_febe8101;
  FUN_0007d1dc(0x26,0x22,3,5,((undefined *)camry_host_ptr(0xfebe8c5bu)));
  FUN_0007d1dc(0x27, 0x22, 1, 4, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x2ba4))));
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x386a)))));
  uVar3 = FUN_0007d0ea(1);
  if ((cVar1 == 'Z') && ((uVar3 >> 4 & 1) == 0)) {
    FUN_0007e612(1);
  }
  else if ((cVar1 == '\0') && ((uVar3 >> 4 & 1) != 0)) {
    FUN_0007e46a(1,0x40);
    FUN_0007e46a(1,0x80);
    FUN_0007e696(1);
  }
  return;
}



/* Far-call trampoline: prepare {lp},0 / jarl 0x4D4BC / dispose 0,{lp},lp; byte-verified against the
   exact image. Forwards with registers and stack unchanged; marked as a thunk. Forwarding shape
   machine-verified; target semantics not recovered. */

void thunk_FUN_0004d4bc(void)

{
  FUN_0004d4bc();
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4cf64(void)

{
  return;
}



/* Constant source: return 0x5a; shape-classified from the canonical corpus. Callers receive this
   literal directly; its meaning is not recovered. */

undefined4 f33_return_const_5a_4cf66(void)

{
  return 0x5a;
}



void FUN_0004cf6c(void)

{
  uint uVar1;
  
  uVar1 = 0;
  DAT_febe81b2 = 0;
  DAT_febe8194 = 0;
  DAT_febe8195 = 0;
  DAT_febe81c0 = 0;
  f33_diagnostic_normal_tx_policy_request = '\0';
  f33_dtc_setting_inhibit_request = '\0';
  f33_dtc_requested_status_mask = '\0';
  f33_dtc_iteration_result_count = 0;
  f33_dtc_iteration_catalogue_cursor = 0;
  f33_snapshot_identifier_cached_dtc = 0;
  DAT_febe8199 = 0;
  DAT_febe819a = 0;
  DAT_febe81b8 = 0;
  DAT_febe81ad = 0;
  DAT_febe81ba = 0;
  DAT_febe81bc = 0;
  f33_app_programming_mode_request_latched = '\0';
  DAT_febe81af = 0;
  do {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe819bu + (uint32_t)(uVar1) * 1u)))) = 0;
    uVar1 = uVar1 + 1;
  } while (uVar1 < 0x10);
  return;
}



/* Publish81AC from captured E826, published E8CC and4CF66. Specified transitions clear diagnostic
   service/security state and event88; retained prior E826/7F97 detect transitions. Not atomic with
   foreground DCM. */

void f33_refresh_mode_diagnostic_admission(void)

{
  char cVar1;
  char cVar2;
  char cVar3;
  char cVar4;
  undefined1 uVar5;
  uint32_t puVar6;
  int iVar7;
  uint uVar8;
  
  cVar4 = DAT_febee826;
  cVar3 = DAT_febe81b0;
  cVar2 = DAT_febe81ab;
  cVar1 = DAT_febe7f97;
  puVar6 = 0xfebeb800u;
  uVar8 = (uint)DAT_febee8cc;
  iVar7 = f33_return_const_5a_4cf66();
  if ((((cVar4 == '\x11') || (cVar4 == '\"')) || (uVar8 < 0x104)) ||
     ((iVar7 != 0x5a && ((iVar7 != 0xa5 || (2 < uVar8 - 0x700)))))) {
    uVar5 = 0;
  }
  else {
    uVar5 = 0x5a;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x3654))))) = uVar5;
  if (((cVar4 == '\"') || ((cVar4 == '\0' && (cVar2 == '3')))) ||
     ((cVar1 == '\0' && (cVar3 == 'Z')))) {
    FUN_0008b120();
    FUN_00091b50();
    FUN_000917a4(0);
    f33_run_init_chain_8e62a();
    ((void)(0x88), thunk_FUN_000b9320());
    FUN_0004cf6c();
    FUN_0004d4bc();
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x3655))))) = cVar4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x3650))))) = cVar1;
  return;
}



void FUN_0004d03e(void)

{
  ushort uVar1;
  uint32_t puVar2;
  ushort uVar3;
  
  puVar2 = 0xfebeb800u;
  uVar3 = DAT_febe81b2 & 0xff00;
  uVar1 = DAT_febe81b2 & 0xff;
  if (uVar3 != 0x1400) {
    if (uVar3 == 0x2e00) {
      if (uVar1 == 0x10) {
        f33_start_pending_write_mode_request();
        return;
      }
      if ((DAT_febe81b2 & 0xff) != 0) {
        uVar1 = 9;
      }
      puVar2 = 0xfebeb800u;
      FUN_00050094(uVar1);
    }
    else if (uVar3 == 0xba00) {
      if (uVar1 == 0x10) {
        return;
      }
      puVar2 = 0xfebeb800u;
      FUN_0004d4c4();
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x366b))))) != '\0') {
        return;
      }
    }
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x364e)))) = 0;
  }
  return;
}



void FUN_0004d094(void)

{
  f33_refresh_mode_diagnostic_admission();
  FUN_0004d03e();
  return;
}



void FUN_0004d0a4(byte param_1,byte param_2)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (param_1 < 0x10) {
    f33_diag_routine_publish_terminal_result(param_1,param_2);
  }
  else {
    if (param_1 == 0x12) {
      puVar1 = 0xfebeb800u;
      f33_finish_pending_write_mode_request();
    }
    if ((((*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x364e)))) & 0xff) == 0x10) && (param_2 != 0x10)) {
      (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x364e)))) = (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x364e)))) & 0xff00 | (ushort)param_2;
    }
  }
  return;
}



void FUN_0004d0e8(undefined2 param_1)

{
  if (DAT_febe819e == '\x01') {
    FUN_0004d0a4(3,param_1);
  }
  if (DAT_febe81a5 == '\x01') {
    FUN_0004d0a4(10,param_1);
  }
  return;
}



/* 0\u21920,-12\u21924,-7\u21928,-6\u21925,-1\u21922,other\u21929;negativeapplicationstatusesmuststay32-bit.
   0→0,-12→4,-7→8,-6→5,-1→2,other→9;negativeapplicationstatusesmuststay32-bit. */

uint f33_diag_translate_application_request_status(int application_status)

{
  if (application_status == 0) {
    return 0;
  }
  if (application_status == -0xc) {
    return 4;
  }
  if (application_status == -7) {
    return 8;
  }
  if (application_status != -6) {
    if (application_status != -1) {
      return 9;
    }
    return 2;
  }
  return 5;
}



void FUN_0004d144(int param_1,undefined1 *param_2)

{
  undefined1 uVar1;
  
  if ((param_1 == -3) || (param_1 == -5)) {
    uVar1 = 0x12;
  }
  else if (param_1 == -6) {
    uVar1 = 0x22;
  }
  else if (param_1 == -0xd) {
    uVar1 = 0x11;
  }
  else if (param_1 == -0xe) {
    uVar1 = 0x33;
  }
  else {
    uVar1 = 0x10;
  }
  *param_2 = uVar1;
  return;
}



/* Always publish addressing kind819A. Return0 only for81CC=5A,81AC=5A and7F97!=5A; otherwise1. Does
   not test delayed COM inhibit7F96. */

uint f33_check_diagnostic_application_admission(uchar addressing_kind)

{
  uint uVar1;
  
  if ((DAT_febe81cc == 'Z') && (DAT_febe81ac == 'Z')) {
    uVar1 = (uint)(DAT_febe7f97 == 'Z');
  }
  else {
    uVar1 = 1;
  }
  DAT_febe819a = addressing_kind;
  return uVar1;
}



void FUN_0004d222(int param_1,uint param_2)

{
  byte *pbVar1;
  ushort uVar2;
  uint uVar3;
  int iVar4;
  
  for (uVar3 = 0; uVar3 < (param_2 & 0xffff); uVar3 = uVar3 + 1 & 0xffff) {
    (*((undefined1 *)camry_host_ptr((uint32_t)(uVar3 + param_1)))) = 0;
  }
  for (iVar4 = 0;
      (int)(iVar4 - (uint)DAT_00026492) < 0 != (iVar4 < 0 && -1 < (int)(iVar4 - (uint)DAT_00026492))
      ; iVar4 = iVar4 + 1) {
    uVar2 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x26918u + (uint32_t)(iVar4 * 4) * 2u))));
    if ((uVar2 & 0xff) == 0) {
      uVar3 = (int)(uint)uVar2 >> 0xb;
      if (uVar3 < (param_2 & 0xff)) {
        pbVar1 = ((byte *)camry_host_ptr((uint32_t)(uVar3 + param_1)));
        *pbVar1 = *pbVar1 | (byte)(0x80 >> ((int)(uint)uVar2 >> 8 & 7U));
      }
    }
  }
  return;
}



void FUN_0004d308(uint param_1,int param_2,uint param_3)

{
  byte *pbVar1;
  uint uVar2;
  int iVar3;
  uint uVar4;
  
  for (uVar2 = 0; uVar2 < (param_3 & 0xffff); uVar2 = uVar2 + 1 & 0xffff) {
    (*((undefined1 *)camry_host_ptr((uint32_t)(uVar2 + param_2)))) = 0;
  }
  for (iVar3 = 0;
      (int)(iVar3 - (uint)DAT_00026492) < 0 != (iVar3 < 0 && -1 < (int)(iVar3 - (uint)DAT_00026492))
      ; iVar3 = iVar3 + 1) {
    param_1 = param_1 & 0xff00;
    uVar2 = (uint)(ushort)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x26918u + (uint32_t)(iVar3 * 4) * 2u))));
    if ((param_1 < uVar2) && (uVar2 < (param_1 + 0x100 & 0xffff))) {
      uVar4 = (int)(uVar2 - 1 & 0xff) >> 3;
      if (uVar4 < (param_3 & 0xff)) {
        pbVar1 = ((byte *)camry_host_ptr((uint32_t)(uVar4 + param_2)));
        *pbVar1 = *pbVar1 | (byte)(0x80 >> (uVar2 - 1 & 7));
      }
    }
  }
  return;
}



/* 0x5A when expression holds; otherwise 0 for u32[FEBEE91C] == 0xAA5555AA. BF3AA: FEBEB314 ->
   FEBEE91C. */

uint f33_did_available_4d3be(void)

{
  if (DAT_febee91c == -0x55aaaa56) {
    return 0x5a;
  }
  return 0;
}



/* 0x5A when expression holds; otherwise 0 for u8[FEBEE802] == 0x5A. BF3AA: FEBEBE9C -> FEBEE802. */

uint f33_did_available_4d3d6(void)

{
  uint uVar1;
  
  if (DAT_febee802 == 'Z') {
    uVar1 = 0x5a;
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}



/* 0x5A when expression holds; otherwise 0 for u8[FEBEE804] == 0x5A. BF3AA: FEBEBE9A -> FEBEE804. */

uint f33_did_available_4d3e4(void)

{
  uint uVar1;
  
  if (DAT_febee804 == 'Z') {
    uVar1 = 0x5a;
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}



/* 0x5A when expression holds; otherwise 0 for u8[FEBEE803] == 0x5A. BF3AA: FEBEBE99 -> FEBEE803. */

uint f33_did_available_4d3f2(void)

{
  uint uVar1;
  
  if (DAT_febee803 == 'Z') {
    uVar1 = 0x5a;
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}



/* 0x5A when expression holds; otherwise 0 for u8[FEBEE870] != 0x5A. BF3AA: FEBEBE9D -> FEBEE870. */

uint f33_did_available_4d400(void)

{
  uint uVar1;
  
  uVar1 = 0x5a;
  if (DAT_febee870 == 'Z') {
    uVar1 = 0;
  }
  return uVar1;
}



/* 0x5A when expression holds; otherwise 0 for u8[FEBEE870] == 0x5A. BF3AA: FEBEBE9D -> FEBEE870. */

uint f33_did_available_4d412(void)

{
  uint uVar1;
  
  if (DAT_febee870 == 'Z') {
    uVar1 = 0x5a;
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}



/* 0x5A when expression holds; otherwise 0 for u8[FEBEE805] == 0x5A. BF3AA: FEBEBE9F -> FEBEE805. */

uint f33_did_available_4d420(void)

{
  uint uVar1;
  
  if (DAT_febee805 == 'Z') {
    uVar1 = 0x5a;
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}



/* 0x5A when expression holds; otherwise 0 for u8[FEBEE806] == 0x5A. BF3AA: FEBEBEA0 -> FEBEE806. */

uint f33_did_available_4d42e(void)

{
  uint uVar1;
  
  if (DAT_febee806 == 'Z') {
    uVar1 = 0x5a;
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}



/* 4D47E movea5A,r0,r10;4D482jmplp;usedmetadata2013/14. */

uint f33_did_metadata_always_available(void)

{
  return 0x5a;
}



/* Exact MOVEA5A,R10;JMP LP leaf. Configured profile metadata uses this availability callback;
   payload projection separately masks invalid or unavailable fields. */

uint f33_did_always_available(void)

{
  return 0x5a;
}



/* Metadata index81B8, readsu16record+2, writes0 if out of range. */

void f33_get_selected_did_payload_length(ushort *length)

{
  ushort uVar1;
  uint32_t puVar2;
  F33DidPublicationMetadata *pFVar3;
  ushort uStack_a;
  
  puVar2 = 0xfebeb800u;
  pFVar3 = f33_get_did_publication_metadata(&uStack_a);
  uVar1 = 0;
  if ((uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x3648)))) < (uint)uStack_a) {
    uVar1 = pFVar3[(*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x3648))))].payload_length;
  }
  *length = uVar1;
  return;
}



/* Single constant publisher: DAT_febe81c8 = 0; Shape-classified from the canonical corpus; the
   target cell is not yet named, so the written state's meaning is unknown. */

void FUN_0004d4bc(void)

{
  DAT_febe81c8 = 0;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4d4c2(void)

{
  return;
}



/* Single constant publisher: DAT_febe8195 = 0; Shape-classified from the canonical corpus; the
   target cell is not yet named, so the written state's meaning is unknown. */

void FUN_0004d4c4(void)

{
  DAT_febe8195 = 0;
  return;
}



undefined1 FUN_0004d4f2(int param_1)

{
  undefined1 uStack_5;
  
  uStack_5 = 0;
  if (param_1 == 0) {
    uStack_5 = 0;
  }
  else if (param_1 == -1) {
    uStack_5 = 2;
  }
  else {
    FUN_0004d144(param_1,&uStack_5);
  }
  return uStack_5;
}



/* Invoke fixed finish callback34E66(index,length), update BA10/BA00 owner, and return
   translated4D4F2 status inR10. Both second argument and result are consumed by8E2DE; not a void
   one-argument notifier. */

uchar f33_finish_proprietary_operation(uchar selected_index,uint *response_length)

{
  undefined2 uVar1;
  uint32_t puVar2;
  uchar uVar3;
  int iVar4;
  
  puVar2 = 0xfebeb800u;
  iVar4 = f33_dispatch_ba_configured_finish(selected_index,response_length);
  uVar1 = 0xba10;
  if (iVar4 != -1) {
    uVar1 = 0xba00;
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x364e)))) = uVar1;
  uVar3 = FUN_0004d4f2(iVar4);
  return uVar3;
}



/* Always8D66A clears app-SA active/result/challenge/copy/client. Only new1 or old1\u2192new40
   clears8196/8197, requests event88 and clears nonrunning routine results. Network uses8196; do not
   claim every session clears it. Only new1 or old1→new40 clears8196/8197, requests event88 and
   clears nonrunning routine results. */

void f33_diagnostic_session_changed_application(uchar old_session,uchar new_session)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  f33_app_security_reset_challenge_material();
  if ((new_session == '\x01') || ((old_session == '\x01' && (new_session == '@')))) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x366a))))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3669))))) = 0;
    ((void)(0x88), thunk_FUN_000b9320());
    f33_diag_routine_clear_nonrunning_results('\0');
  }
  return;
}



/* Onlytarget2 rejectsunsignedE892>ROM318B0=384 withapplicationstatus0B\u2192NRC88 via8E6EC;
   equalityadmitted. Other targets admitted; the E892 load still occurs before target selection.
   r6current snapshotpassedby8B36E butnotreadhere. Onlytarget2 rejectsunsignedE892>ROM318B0=384
   withapplicationstatus0B→NRC88 via8E6EC; */

uint f33_app_session_transition_precondition(uchar current_session_ignored,uchar target)

{
  if ((target == '\x02') && (f33_communication_control_admission_limit < DAT_febee892)) {
    return 0xb;
  }
  return 0;
}



undefined1 FUN_0004d5d8(void)

{
  undefined1 uVar1;
  
  if (((DAT_febee81f == '\x11') || (DAT_febe66ba < DAT_000318b2)) ||
     (uVar1 = 0, DAT_febe819a != '\0')) {
    uVar1 = 1;
  }
  return uVar1;
}



void FUN_0004d5fe(void)

{
  f33_app_programming_mode_request_latched = '\0';
  return;
}



/* Addressing819A==0 and81AE==0 requestsmajor9 viaB15AC thenlatches81AE=5A. Nonzeroaddressing branch
   resets diagnostic owners; admission4D5D8 normally rejectsnonzerobeforethisstage, but
   globaladdressing isretained/non-atomic. No directresident transfer, flashprogramming or
   securityunlock here. */

void f33_app_request_programming_transition(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_febe819a == '\0') {
    if (f33_app_programming_mode_request_latched == '\0') {
      ((void)(9), thunk_FUN_000b15ac());
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3652))))) = 0x5a;
    }
  }
  else {
    FUN_0008b120();
    FUN_00091b50();
    FUN_000917a4(0);
    f33_run_init_chain_8e62a();
  }
  return;
}



/* Idle81B2 publishes1410 and requests operation1, returning pending4. Matching family14 with low10
   stays pending; terminal low0 returns0 and other terminal lows return6, clearing81B2. Other
   families return6 without stealing their state. RAM reset is not durable completion. Idle callback
   publishes1410 and composes real selective RAM clear while returning pending4. Matching terminal
   status clears request; other families are not stolen. No durable completion. */

ushort f33_diagnostic_clear_request_callback(void)

{
  ushort uVar1;
  ushort uVar2;
  
  if (DAT_febe81b2 == 0) {
    DAT_febe81b2 = 0x1410;
    f33_request_diagnostic_clear();
    uVar2 = 4;
  }
  else if ((DAT_febe81b2 & 0xff00) == 0x1400) {
    uVar1 = DAT_febe81b2 & 0xff;
    uVar2 = DAT_febe81b2 & 0xff;
    if (uVar2 == 0x10) {
      uVar2 = 4;
    }
    else {
      DAT_febe81b2 = 0;
      if (uVar1 != 0) {
        uVar2 = 6;
      }
    }
  }
  else {
    uVar2 = 6;
  }
  return uVar2;
}



/* Return0 only for24-bit groupFFFFFF; other groups return1. No configured per-DTC selective-clear
   API is implied. */

uint f33_validate_clear_all_diagnostic_group(uint group)

{
  return (uint)(group != 0xffffff);
}



/* StoreB9 and return0. Status availability is not event-history bitmap layout. */

uint f33_get_dtc_status_availability_mask(uchar *mask)

{
  *mask = 0xb9;
  return 0;
}



/* Retain mask&B9 at8198 and reset u16 result count81B4 and cursor81B6. Actual derived-status
   snapshot is deferred until first527D6 scan. */

uint f33_begin_filtered_dtc_iteration(uchar mask)

{
  f33_dtc_requested_status_mask = mask & 0xb9;
  f33_dtc_iteration_result_count = 0;
  f33_dtc_iteration_catalogue_cursor = 0;
  return 0;
}



/* Advance through snapshot status5F87 and DTC catalogue30850. Return0 for next matching tuple,1 for
   exhausted/invalid; retain cursor and limit successful results to1023. DTC index is not event
   number. */

uint f33_next_filtered_dtc(uint *dtc,uchar *status)

{
  ushort uVar1;
  uint32_t puVar2;
  uint uVar3;
  uchar uStack_15;
  uint uStack_14;
  
  uVar1 = f33_dtc_iteration_result_count;
  puVar2 = 0xfebeb800u;
  if ((((dtc == (uint *)0x0) || (status == (uchar *)0x0)) ||
      (uVar3 = f33_scan_dtc_status_snapshot
                         (f33_dtc_requested_status_mask,&uStack_14,&uStack_15,
                          f33_dtc_iteration_catalogue_cursor + 1), uVar3 == 0)) ||
     (0x3ff < (ushort)(uVar1 + 1))) {
    uVar3 = 1;
  }
  else {
    (*((short *)camry_host_ptr((uint32_t)(puVar2 + -0x364a)))) = (short)uVar3;
    (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x364c)))) = uVar1 + 1;
    uVar3 = 0;
    *dtc = uStack_14;
    *status = uStack_15;
  }
  return uVar3;
}



/* Retain slot1 DTC at81C4 and record mask8199; emit record1 then10, then clear cached pair on
   exhaustion. Record numbers are not DTC status bytes. */

uint f33_next_snapshot_identifier_tuple(uint *dtc,uchar *record_number)

{
  uint32_t puVar1;
  byte bVar2;
  uint uVar3;
  uchar uVar4;
  uint local_10;
  
  puVar1 = 0xfebeb800u;
  uVar3 = (uint)DAT_febe8199;
  local_10 = f33_snapshot_identifier_cached_dtc;
  if ((dtc == (uint *)0x0) || (record_number == (uchar *)0x0)) {
LAB_0004d786:
    local_10 = 0;
    bVar2 = 0;
    uVar3 = 1;
  }
  else {
    puVar1 = 0xfebeb800u;
    if (f33_snapshot_identifier_cached_dtc == 0) {
      puVar1 = 0xfebeb800u;
      uVar3 = f33_get_secondary_capture_record_mask(&local_10);
    }
    if ((uVar3 & 1) == 0) {
      if ((uVar3 >> 1 & 1) == 0) goto LAB_0004d786;
      bVar2 = (byte)uVar3 & 0xfd;
      uVar4 = '\x10';
      *dtc = local_10;
    }
    else {
      bVar2 = (byte)uVar3 & 0xfe;
      uVar4 = '\x01';
      *dtc = local_10;
    }
    *record_number = uVar4;
    uVar3 = 0;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3667))))) = bVar2;
  (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x363c)))) = local_10;
  return uVar3;
}



/* Use selected metadata index81B8 and invoke fixed record+4 reader; out-of-range returns3. Length
   and availability selection are separate operations. */

uint f33_read_selected_did_payload(uchar *output,ushort length)

{
  uint32_t puVar1;
  F33DidPublicationMetadata *pFVar2;
  uint uVar3;
  ushort uStack_e;
  
  puVar1 = 0xfebeb800u;
  pFVar2 = f33_get_did_publication_metadata(&uStack_e);
  if ((uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x3648)))) < (uint)uStack_e) {
    uVar3 = (*(int (*)())pFVar2[(*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x3648))))].reader)(output,length);
  }
  else {
    uVar3 = 3;
  }
  return uVar3;
}



/* Scan all242 metadata records and return matching record kind orFF. Kind is a route discriminator,
   not an arbitrary memory-access class. */

uchar f33_get_did_metadata_route_kind(ushort did)

{
  uint uVar1;
  F33DidPublicationMetadata *pFVar2;
  uchar uVar3;
  ushort uStack_e;
  
  uVar3 = 0xff;
  pFVar2 = f33_get_did_publication_metadata(&uStack_e);
  for (uVar1 = 0; (int)(uVar1 - uStack_e) < 0 != ((int)uVar1 < 0 && -1 < (int)(uVar1 - uStack_e));
      uVar1 = uVar1 + 1) {
    if (pFVar2[uVar1].did == did) {
      uVar3 = pFVar2[uVar1 & 0xffff].route_kind;
    }
  }
  return uVar3;
}



undefined4 f33_rdbi_0102_callback(int param_1)

{
  undefined1 uStack_f;
  undefined2 uStack_e;
  undefined4 uStack_c;
  
  if (DAT_febee813 == 'Z') {
    uStack_c = DAT_febee90c;
    uStack_e = DAT_febee896;
    uStack_f = DAT_febee815;
    FUN_00070180(DAT_febee896,0xfffe,&uStack_e);
    FUN_00070192(uStack_c,0xfffffffe,&uStack_c);
    FUN_0007016e(uStack_f,1,&uStack_f);
  }
  else {
    uStack_e = 0xffff;
    uStack_c = 0xffffffff;
    uStack_f = 0;
  }
  FUN_0006a574(uStack_e, ((undefined1 *)camry_host_ptr((uint32_t)(param_1))));
  FUN_0006a55c(uStack_c, ((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 2))));
  (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 6)))) = uStack_f;
  return 0;
}



undefined4 f33_rdbi_0109_callback(undefined1 *param_1)

{
  undefined1 uVar1;
  undefined1 uVar2;
  undefined1 uVar3;
  undefined1 uVar4;
  undefined1 uVar5;
  undefined1 uVar6;
  
  uVar1 = DAT_febee867;
  uVar6 = DAT_febee868;
  uVar5 = DAT_febee869;
  uVar4 = DAT_febee86a;
  uVar3 = DAT_febee86b;
  uVar2 = DAT_febee86c;
  if (DAT_febee813 != 'Z') {
    uVar1 = 0xff;
    uVar6 = 0xff;
    uVar5 = 0xff;
    uVar4 = 0xff;
    uVar3 = 0xff;
    uVar2 = 0xff;
  }
  *param_1 = uVar1;
  param_1[1] = uVar6;
  param_1[2] = uVar5;
  param_1[3] = uVar4;
  param_1[4] = uVar3;
  param_1[5] = uVar2;
  return 0;
}



undefined4 f33_rdbi_0110_callback(undefined4 param_1)

{
  uint32_t puVar1;
  int iVar2;
  uint uVar3;
  
  puVar1 = 0xfebeb800u;
  uVar3 = FUN_0006a130();
  if (~(*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x2e1c)))) < uVar3) {
    iVar2 = -1;
  }
  else {
    iVar2 = uVar3 + (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x2e1c))));
  }
  FUN_0006a55c(iVar2, ((undefined1 *)camry_host_ptr((uint32_t)(param_1))));
  return 0;
}



undefined4 f33_rdbi_0111_callback(void)

{
  return 0;
}



undefined4 f33_rdbi_0112_callback(undefined4 param_1)

{
  int iVar1;
  
  if (~DAT_febe89ec < DAT_febe8afc) {
    iVar1 = -1;
  }
  else {
    iVar1 = DAT_febe8afc + DAT_febe89ec;
  }
  FUN_0006a55c(iVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_1))));
  return 0;
}



undefined4 f33_rdbi_0204_callback(undefined1 *param_1)

{
  char cVar1;
  undefined1 uVar2;
  
  cVar1 = DAT_febee856;
  *param_1 = 0x80;
  uVar2 = 0;
  if (cVar1 == '\x11') {
    uVar2 = 0x80;
  }
  param_1[1] = uVar2;
  return 0;
}



undefined4 f33_rdbi_1031_callback(undefined4 param_1)

{
  uint uVar1;
  undefined2 uStack_a;
  
  uVar1 = (uint)DAT_febee894 * 10 >> 7;
  uStack_a = (undefined2)uVar1;
  FUN_00070180(uVar1,3000,&uStack_a);
  FUN_0006a574(uStack_a, ((undefined1 *)camry_host_ptr((uint32_t)(param_1))));
  return 0;
}



undefined4 f33_rdbi_1032_callback(undefined4 param_1)

{
  undefined2 uStack_a;
  
  uStack_a = DAT_febee890;
  FUN_00070180(DAT_febee890,0x3200,&uStack_a);
  FUN_0006a574(uStack_a, ((undefined1 *)camry_host_ptr((uint32_t)(param_1))));
  return 0;
}



undefined4 f33_rdbi_1033_callback(undefined1 *param_1)

{
  undefined1 uStack_9;
  
  uStack_9 = DAT_febee811;
  FUN_0007016e(DAT_febee811,1,&uStack_9);
  *param_1 = uStack_9;
  return 0;
}



/* RDBI1034/1039 aliases: scale unsigned66BA by100/256, cap2500, encode BE16, return0. Current
   EMPS_P5 names these battery voltage, with wire units0.01V. Exact table rows2937C/293CC bind
   DID1034/1039 to the same callback and unsigned66BA source. Scale100/256 then cap2500 and
   encodeBE16; current EMPS_P5 diagnostic units0.01V. */

uint f33_rdbi_1034_callback(uchar *output)

{
  undefined2 uStack_a;
  
  uStack_a = (undefined2)((uint)DAT_febe66ba * 100 >> 8);
  FUN_00070180((uint)DAT_febe66ba * 100 >> 8,0x9c4,&uStack_a);
  FUN_0006a574(uStack_a,output);
  return 0;
}



/* WARNING: Removing unreachable block (ram,0x0004dba0) */

undefined4 did_1035_steering_wheel_torque(undefined4 param_1)

{
  int iVar1;
  int local_c;
  
  if (DAT_febe6af0 == -0x5aa5a55b) {
    local_c = (DAT_febe66a8 * 1000) / 0x100;
    FUN_0007012a(local_c,25000,0xffff9e58,&local_c);
    iVar1 = (int)(short)local_c;
  }
  else {
    iVar1 = -0x8000;
  }
  FUN_0006a5ac(iVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_1))));
  return 0;
}



undefined4 f33_rdbi_1038_callback(byte *param_1)

{
  *param_1 = DAT_febe7fec & 0xf;
  return 0;
}



undefined4 f33_rdbi_1061_callback(undefined4 param_1)

{
  undefined2 uStack_a;
  
  uStack_a = (undefined2)((uint)DAT_febe66b8 * 100 >> 8);
  FUN_00070180((uint)DAT_febe66b8 * 100 >> 8,0x9c4,&uStack_a);
  FUN_0006a574(uStack_a, ((undefined1 *)camry_host_ptr((uint32_t)(param_1))));
  return 0;
}



undefined4 f33_rdbi_1062_callback(undefined4 param_1)

{
  undefined2 uStack_a;
  
  uStack_a = (undefined2)((uint)DAT_febe66ae * 100 >> 8);
  FUN_00070180((uint)DAT_febe66ae * 100 >> 8,0x9c4,&uStack_a);
  FUN_0006a574(uStack_a, ((undefined1 *)camry_host_ptr((uint32_t)(param_1))));
  return 0;
}



undefined4 f33_rdbi_1064_callback(undefined1 *param_1)

{
  undefined1 uStack_9;
  
  uStack_9 = DAT_febee829;
  FUN_0007016e(DAT_febee829,2,&uStack_9);
  *param_1 = uStack_9;
  return 0;
}



undefined4 f33_rdbi_1065_callback(undefined1 *param_1)

{
  undefined1 uStack_9;
  
  uStack_9 = 0 < DAT_febe678c;
  FUN_0007016e(uStack_9,1,&uStack_9);
  *param_1 = uStack_9;
  return 0;
}



undefined4 f33_rdbi_1066_callback(void)

{
  return 0;
}



undefined4 f33_rdbi_106a_callback(void)

{
  return 0;
}



undefined4 f33_rdbi_106b_callback(undefined4 param_1)

{
  undefined2 uStack_a;
  
  uStack_a = (undefined2)((uint)DAT_febe66b2 * 100 >> 8);
  FUN_00070180((uint)DAT_febe66b2 * 100 >> 8,0x9c4,&uStack_a);
  FUN_0006a574(uStack_a, ((undefined1 *)camry_host_ptr((uint32_t)(param_1))));
  return 0;
}



/* WARNING: Removing unreachable block (ram,0x0004dd7e) */

undefined4 f33_rdbi_1091_callback(undefined4 param_1)

{
  int local_c;
  
  local_c = (DAT_febe64f2 * 1000) / 0x100;
  FUN_0007012a(local_c,25000,0xffff9e58,&local_c);
  FUN_0006a5ac((int)(short)local_c, ((undefined1 *)camry_host_ptr((uint32_t)(param_1))));
  return 0;
}



/* WARNING: Removing unreachable block (ram,0x0004ddb6) */

undefined4 f33_rdbi_1092_callback(undefined4 param_1)

{
  int local_c;
  
  local_c = (DAT_febe64f4 * 1000) / 0x100;
  FUN_0007012a(local_c,25000,0xffff9e58,&local_c);
  FUN_0006a5ac((int)(short)local_c, ((undefined1 *)camry_host_ptr((uint32_t)(param_1))));
  return 0;
}



/* WARNING: Removing unreachable block (ram,0x0004ddee) */

undefined4 f33_rdbi_1093_callback(undefined4 param_1)

{
  int local_c;
  
  local_c = (DAT_febe64f6 * 1000) / 0x100;
  FUN_0007012a(local_c,25000,0xffff9e58,&local_c);
  FUN_0006a5ac((int)(short)local_c, ((undefined1 *)camry_host_ptr((uint32_t)(param_1))));
  return 0;
}



/* WARNING: Removing unreachable block (ram,0x0004de26) */

undefined4 f33_rdbi_1094_callback(undefined4 param_1)

{
  int local_c;
  
  local_c = (DAT_febe64f8 * 1000) / 0x100;
  FUN_0007012a(local_c,25000,0xffff9e58,&local_c);
  FUN_0006a5ac((int)(short)local_c, ((undefined1 *)camry_host_ptr((uint32_t)(param_1))));
  return 0;
}



undefined4 f33_rdbi_1095_callback(undefined4 param_1)

{
  undefined2 uStack_a;
  
  uStack_a = DAT_febe66d6;
  FUN_00070180(DAT_febe66d6,0xffff,&uStack_a);
  FUN_0006a574(uStack_a, ((undefined1 *)camry_host_ptr((uint32_t)(param_1))));
  return 0;
}



undefined4 f33_rdbi_1096_callback(undefined4 param_1)

{
  undefined2 uStack_a;
  
  uStack_a = DAT_febe66d8;
  FUN_00070180(DAT_febe66d8,0xffff,&uStack_a);
  FUN_0006a574(uStack_a, ((undefined1 *)camry_host_ptr((uint32_t)(param_1))));
  return 0;
}



undefined4 f33_rdbi_1097_callback(undefined4 param_1)

{
  undefined2 uStack_a;
  
  uStack_a = DAT_febe66da;
  FUN_00070180(DAT_febe66da,0xffff,&uStack_a);
  FUN_0006a574(uStack_a, ((undefined1 *)camry_host_ptr((uint32_t)(param_1))));
  return 0;
}



undefined4 f33_rdbi_1098_callback(undefined4 param_1)

{
  undefined2 uStack_a;
  
  uStack_a = DAT_febe66dc;
  FUN_00070180(DAT_febe66dc,0xffff,&uStack_a);
  FUN_0006a574(uStack_a, ((undefined1 *)camry_host_ptr((uint32_t)(param_1))));
  return 0;
}



undefined4 f33_rdbi_10c4_callback(undefined4 param_1)

{
  uint uVar1;
  undefined2 uStack_a;
  
  uVar1 = (uint)DAT_febe64a2 * 0x271 >> 0xb;
  uStack_a = (undefined2)uVar1;
  FUN_00070180(uVar1,10000,&uStack_a);
  FUN_0006a574(uStack_a, ((undefined1 *)camry_host_ptr((uint32_t)(param_1))));
  return 0;
}



undefined4 f33_rdbi_10c5_callback(undefined4 param_1)

{
  uint uVar1;
  undefined2 uStack_a;
  
  uVar1 = (uint)DAT_febe64a4 * 0x271 >> 0xb;
  uStack_a = (undefined2)uVar1;
  FUN_00070180(uVar1,10000,&uStack_a);
  FUN_0006a574(uStack_a, ((undefined1 *)camry_host_ptr((uint32_t)(param_1))));
  return 0;
}



undefined4 f33_rdbi_10c6_callback(undefined4 param_1)

{
  uint uVar1;
  undefined2 uStack_a;
  
  uVar1 = (uint)DAT_febe64a6 * 0x271 >> 0xb;
  uStack_a = (undefined2)uVar1;
  FUN_00070180(uVar1,10000,&uStack_a);
  FUN_0006a574(uStack_a, ((undefined1 *)camry_host_ptr((uint32_t)(param_1))));
  return 0;
}



undefined4 f33_rdbi_10c7_callback(void)

{
  return 0;
}



undefined4 f33_rdbi_10c8_callback(void)

{
  return 0;
}



undefined4 f33_rdbi_10c9_callback(void)

{
  return 0;
}



undefined4 f33_rdbi_10ca_callback(undefined4 param_1)

{
  undefined2 uStack_a;
  
  uStack_a = (undefined2)((uint)DAT_febe66ae * 100 >> 8);
  FUN_00070180((uint)DAT_febe66ae * 100 >> 8,0x9c4,&uStack_a);
  FUN_0006a574(uStack_a, ((undefined1 *)camry_host_ptr((uint32_t)(param_1))));
  return 0;
}



undefined4 f33_rdbi_10f4_callback(undefined4 param_1)

{
  uint uVar1;
  undefined2 uStack_a;
  
  uVar1 = (uint)DAT_febe64a8 * 0x271 >> 0xb;
  uStack_a = (undefined2)uVar1;
  FUN_00070180(uVar1,10000,&uStack_a);
  FUN_0006a574(uStack_a, ((undefined1 *)camry_host_ptr((uint32_t)(param_1))));
  return 0;
}



undefined4 f33_rdbi_10f5_callback(undefined4 param_1)

{
  uint uVar1;
  undefined2 uStack_a;
  
  uVar1 = (uint)DAT_febe64aa * 0x271 >> 0xb;
  uStack_a = (undefined2)uVar1;
  FUN_00070180(uVar1,10000,&uStack_a);
  FUN_0006a574(uStack_a, ((undefined1 *)camry_host_ptr((uint32_t)(param_1))));
  return 0;
}



undefined4 f33_rdbi_10f6_callback(undefined4 param_1)

{
  uint uVar1;
  undefined2 uStack_a;
  
  uVar1 = (uint)DAT_febe64ac * 0x271 >> 0xb;
  uStack_a = (undefined2)uVar1;
  FUN_00070180(uVar1,10000,&uStack_a);
  FUN_0006a574(uStack_a, ((undefined1 *)camry_host_ptr((uint32_t)(param_1))));
  return 0;
}



undefined4 f33_rdbi_10f7_callback(void)

{
  return 0;
}



undefined4 f33_rdbi_10f8_callback(void)

{
  return 0;
}



undefined4 f33_rdbi_10f9_callback(void)

{
  return 0;
}



undefined4 f33_rdbi_10fa_callback(undefined4 param_1)

{
  undefined2 uStack_a;
  
  uStack_a = (undefined2)((uint)DAT_febe66b0 * 100 >> 8);
  FUN_00070180((uint)DAT_febe66b0 * 100 >> 8,0x9c4,&uStack_a);
  FUN_0006a574(uStack_a, ((undefined1 *)camry_host_ptr((uint32_t)(param_1))));
  return 0;
}



undefined4 f33_rdbi_1121_callback(undefined4 param_1)

{
  undefined2 uStack_a;
  
  uStack_a = (undefined2)((uint)DAT_febe6600 * 36000 >> 0x10);
  FUN_00070180((uint)DAT_febe6600 * 36000 >> 0x10, camry_host_addr(((undefined *)camry_host_ptr(0x8ca0u))), &uStack_a);
  FUN_0006a574(uStack_a, ((undefined1 *)camry_host_ptr((uint32_t)(param_1))));
  return 0;
}



undefined4 f33_rdbi_1122_callback(undefined4 param_1)

{
  undefined2 uStack_a;
  
  uStack_a = (undefined2)((uint)DAT_febe6602 * 36000 >> 0x10);
  FUN_00070180((uint)DAT_febe6602 * 36000 >> 0x10, camry_host_addr(((undefined *)camry_host_ptr(0x8ca0u))), &uStack_a);
  FUN_0006a574(uStack_a, ((undefined1 *)camry_host_ptr((uint32_t)(param_1))));
  return 0;
}



undefined4 f33_rdbi_1124_callback(void)

{
  return 0;
}



undefined4 f33_rdbi_1125_callback(void)

{
  return 0;
}



undefined4 f33_rdbi_1126_callback(void)

{
  return 0;
}



undefined4 f33_rdbi_1127_callback(void)

{
  return 0;
}



undefined4 f33_rdbi_1128_callback(void)

{
  return 0;
}



undefined4 f33_rdbi_1129_callback(void)

{
  return 0;
}



undefined4 f33_rdbi_112b_callback(undefined4 param_1)

{
  undefined2 uStack_a;
  
  uStack_a = DAT_febe6608;
  FUN_00070180(DAT_febe6608,0x1000,&uStack_a);
  FUN_0006a574(uStack_a, ((undefined1 *)camry_host_ptr((uint32_t)(param_1))));
  return 0;
}



/* WARNING: Removing unreachable block (ram,0x0004e2dc) */

undefined4 f33_rdbi_112d_callback(undefined4 param_1)

{
  int local_c;
  
  local_c = (DAT_febee938 * 4000) / 0x1000;
  FUN_0007012a(local_c,0x1ffff,0xfffe0000,&local_c);
  FUN_0006a594(local_c, ((undefined1 *)camry_host_ptr((uint32_t)(param_1))));
  return 0;
}



undefined4 f33_rdbi_112e_callback(undefined4 param_1)

{
  short sStack_a;
  
  sStack_a = DAT_febee8e0;
  if (DAT_febee885 == '\x02') {
    FUN_00070110((int)DAT_febee8e0, 0x4957, camry_host_addr(((undefined *)camry_host_ptr(0xffffb6a9u))), &sStack_a);
  }
  else {
    sStack_a = 19999;
  }
  FUN_0006a5ac((int)sStack_a, ((undefined1 *)camry_host_ptr((uint32_t)(param_1))));
  return 0;
}



undefined4 f33_rdbi_112f_callback(void)

{
  return 0;
}



undefined4 f33_rdbi_1130_callback(void)

{
  return 0;
}



undefined4 f33_rdbi_1131_callback(void)

{
  return 0;
}



undefined4 f33_rdbi_1132_callback(undefined4 param_1)

{
  uint local_c;
  
  local_c = DAT_febee950;
  FUN_0007012a(DAT_febee950,0xffff,0,&local_c);
  FUN_0006a574(local_c & 0xffff, ((undefined1 *)camry_host_ptr((uint32_t)(param_1))));
  return 0;
}



undefined4 f33_rdbi_1133_callback(undefined1 *param_1)

{
  undefined1 uStack_9;
  
  uStack_9 = DAT_febee88b;
  FUN_0007016e(DAT_febee88b,3,&uStack_9);
  *param_1 = uStack_9;
  return 0;
}



undefined4 did_1155_motor_rotation_angle(undefined4 param_1)

{
  uint uVar1;
  uint uVar2;
  undefined2 uStack_e;
  
  uVar2 = (uint)(ushort)DAT_febe6684;
  uVar1 = f33_get_diagnostic_event_state(0x52);
  if ((uVar1 & 1) == 0) {
    uVar1 = uVar2 * 0x465 >> 0xb;
    uStack_e = (undefined2)uVar1;
    FUN_00070180(uVar1, camry_host_addr(((undefined *)camry_host_ptr(0x8ca0u))), &uStack_e);
  }
  else {
    uStack_e = 0xffff;
  }
  FUN_0006a574(uStack_e, ((undefined1 *)camry_host_ptr((uint32_t)(param_1))));
  return 0;
}



/* WARNING: Removing unreachable block (ram,0x0004e4ea) */

undefined4 did_1156_final_motor_current_limited_q_axis(undefined4 param_1)

{
  short sStack_a;
  
  sStack_a = (short)((DAT_febe678c * 100) / 0x80);
  FUN_00070110((int)sStack_a,0x7fff,0,&sStack_a);
  FUN_0006a5ac((int)sStack_a, ((undefined1 *)camry_host_ptr((uint32_t)(param_1))));
  return 0;
}



undefined4 f33_rdbi_1181_callback(undefined1 *param_1)

{
  undefined1 uStack_9;
  
  uStack_9 = DAT_febe7d44;
  FUN_0007016e(DAT_febe7d44,3,&uStack_9);
  *param_1 = uStack_9;
  return 0;
}



undefined4 f33_rdbi_1182_callback(byte *param_1)

{
  byte bVar1;
  
  bVar1 = DAT_febe8006;
  if (4 < DAT_febe8006) {
    bVar1 = 1;
  }
  *param_1 = bVar1;
  return 0;
}



/* WARNING: Removing unreachable block (ram,0x0004e558) */

undefined4 f33_rdbi_1183_callback(undefined1 *param_1)

{
  short sStack_a;
  
  sStack_a = DAT_febe8060 / 100;
  FUN_00070110((int)sStack_a,0xff,0,&sStack_a);
  *param_1 = (char)sStack_a;
  return 0;
}



/* WARNING: Removing unreachable block (ram,0x0004e58c) */

undefined4 f33_rdbi_1184_callback(undefined1 *param_1)

{
  short sStack_a;
  
  sStack_a = DAT_febe8062 / 100;
  FUN_00070110((int)sStack_a,0xff,0,&sStack_a);
  *param_1 = (char)sStack_a;
  return 0;
}



undefined4 did_1185_can_vehicle_speed_sp1(undefined4 param_1)

{
  undefined2 uStack_a;
  
  uStack_a = DAT_febe809a;
  FUN_00070180(DAT_febe809a,30000,&uStack_a);
  FUN_0006a574(uStack_a, ((undefined1 *)camry_host_ptr((uint32_t)(param_1))));
  return 0;
}



undefined4 f33_rdbi_11b1_callback(undefined1 *param_1)

{
  undefined4 uVar1;
  undefined2 uStack_a;
  
  uVar1 = FUN_000546f2(0);
  uStack_a = (undefined2)uVar1;
  FUN_00070180(uVar1,0xff,&uStack_a);
  *param_1 = (char)uStack_a;
  return 0;
}



undefined4 f33_rdbi_11b3_callback(undefined1 *param_1)

{
  undefined4 uVar1;
  undefined2 uStack_a;
  
  uVar1 = FUN_000546f2(5);
  uStack_a = (undefined2)uVar1;
  FUN_00070180(uVar1,0xff,&uStack_a);
  *param_1 = (char)uStack_a;
  return 0;
}



undefined4 f33_rdbi_11b4_callback(undefined1 *param_1)

{
  undefined4 uVar1;
  undefined2 uStack_a;
  
  uVar1 = FUN_000546f2(6);
  uStack_a = (undefined2)uVar1;
  FUN_00070180(uVar1,0xff,&uStack_a);
  *param_1 = (char)uStack_a;
  return 0;
}



undefined4 f33_rdbi_11b5_callback(undefined1 *param_1)

{
  undefined4 uVar1;
  undefined2 uStack_a;
  
  uVar1 = FUN_000546f2(7);
  uStack_a = (undefined2)uVar1;
  FUN_00070180(uVar1,0xff,&uStack_a);
  *param_1 = (char)uStack_a;
  return 0;
}



undefined4 f33_rdbi_11b6_callback(undefined1 *param_1)

{
  short sStack_a;
  
  sStack_a = (ushort)DAT_febe8645 + (ushort)DAT_febe8644;
  FUN_00070180(sStack_a,0xff,&sStack_a);
  *param_1 = (char)sStack_a;
  return 0;
}



undefined4 f33_rdbi_11b7_callback(undefined1 *param_1)

{
  undefined1 uStack_9;
  
  uStack_9 = DAT_febe8646;
  FUN_0007016e(DAT_febe8646,0xff,&uStack_9);
  *param_1 = uStack_9;
  return 0;
}



undefined4 f33_rdbi_11b8_callback(undefined1 *param_1)

{
  undefined1 uStack_9;
  
  uStack_9 = DAT_febe8647;
  FUN_0007016e(DAT_febe8647,0xff,&uStack_9);
  *param_1 = uStack_9;
  return 0;
}



undefined4 f33_rdbi_11b9_callback(undefined1 *param_1)

{
  undefined1 uStack_9;
  
  uStack_9 = DAT_febe8648;
  FUN_0007016e(DAT_febe8648,0xff,&uStack_9);
  *param_1 = uStack_9;
  return 0;
}



undefined4 f33_rdbi_11ba_callback(undefined1 *param_1)

{
  undefined1 uStack_9;
  
  uStack_9 = DAT_febe8649;
  FUN_0007016e(DAT_febe8649,0xff,&uStack_9);
  *param_1 = uStack_9;
  return 0;
}



undefined4 f33_rdbi_11bb_callback(undefined1 *param_1)

{
  undefined1 uStack_9;
  
  uStack_9 = DAT_febe864b;
  FUN_0007016e(DAT_febe864b,0xff,&uStack_9);
  *param_1 = uStack_9;
  return 0;
}



undefined4 f33_rdbi_11bc_callback(void)

{
  return 0;
}



undefined4 f33_rdbi_11bd_callback(undefined1 *param_1)

{
  undefined4 uVar1;
  undefined2 uStack_a;
  
  uVar1 = FUN_000546f2(0xe);
  uStack_a = (undefined2)uVar1;
  FUN_00070180(uVar1,0xff,&uStack_a);
  *param_1 = (char)uStack_a;
  return 0;
}



/* WARNING: Removing unreachable block (ram,0x0004e802) */
/* WARNING: Removing unreachable block (ram,0x0004e7f6) */

undefined4 did_1c02_command_value_torque(undefined4 param_1)

{
  int local_c;
  
  local_c = (((int)((int)DAT_febe6772 * (uint)DAT_febee8a6) / 0x2000) * 100) / 0x100;
  FUN_0007012a(local_c, 20000, camry_host_addr(((undefined *)camry_host_ptr(0xffffb1e0u))), &local_c);
  FUN_0006a5ac((int)(short)local_c, ((undefined1 *)camry_host_ptr((uint32_t)(param_1))));
  return 0;
}



undefined4 did_1c03_control_state_information(undefined4 param_1)

{
  undefined2 uStack_a;
  
  uStack_a = DAT_febee8cc;
  FUN_00070180(DAT_febee8cc,0xffff,&uStack_a);
  FUN_0006a574(uStack_a, ((undefined1 *)camry_host_ptr((uint32_t)(param_1))));
  return 0;
}



undefined4 did_1c05_1c0c_asic_state_information(int param_1)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  FUN_0006a55c(DAT_febe8298, ((undefined1 *)camry_host_ptr((uint32_t)(param_1))));
  FUN_0006a55c((*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x3564)))), ((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 4))));
  return 0;
}



undefined4 f33_rdbi_1c08_callback(undefined1 *param_1)

{
  undefined1 uStack_9;
  
  uStack_9 = DAT_febe6f6c;
  FUN_0007016e(DAT_febe6f6c,0xff,&uStack_9);
  *param_1 = uStack_9;
  return 0;
}



undefined4 f33_rdbi_1c09_callback(undefined1 *param_1)

{
  undefined1 uStack_9;
  
  uStack_9 = DAT_febe6f6d;
  FUN_0007016e(DAT_febe6f6d,0xff,&uStack_9);
  *param_1 = uStack_9;
  return 0;
}



undefined4 f33_rdbi_1c31_callback(undefined1 *param_1)

{
  undefined1 uStack_9;
  
  uStack_9 = DAT_febee840;
  FUN_0007016e(DAT_febee840,1,&uStack_9);
  *param_1 = uStack_9;
  return 0;
}



undefined4 f33_rdbi_1c33_callback(undefined1 *param_1)

{
  undefined2 uStack_a;
  
  uStack_a = DAT_febee8c4;
  FUN_00070180(DAT_febee8c4,0xff,&uStack_a);
  *param_1 = (char)uStack_a;
  return 0;
}



undefined4 f33_rdbi_1c37_callback(undefined1 *param_1)

{
  undefined1 uStack_9;
  
  uStack_9 = DAT_febee842;
  FUN_0007016e(DAT_febee842,1,&uStack_9);
  *param_1 = uStack_9;
  return 0;
}



undefined4 f33_rdbi_1c39_callback(undefined1 *param_1)

{
  undefined2 uStack_a;
  
  uStack_a = DAT_febee8c8;
  FUN_00070180(DAT_febee8c8,0xff,&uStack_a);
  *param_1 = (char)uStack_a;
  return 0;
}



undefined4 f33_rdbi_1c3d_callback(undefined1 *param_1)

{
  undefined1 uStack_9;
  
  uStack_9 = DAT_febee82d;
  FUN_0007016e(DAT_febee82d,1,&uStack_9);
  *param_1 = uStack_9;
  return 0;
}



undefined4 f33_rdbi_1c3f_callback(undefined1 *param_1)

{
  undefined2 uStack_a;
  
  uStack_a = DAT_febee8b8;
  FUN_00070180(DAT_febee8b8,0xff,&uStack_a);
  *param_1 = (char)uStack_a;
  return 0;
}



undefined4 f33_rdbi_1c43_callback(undefined1 *param_1)

{
  undefined1 uStack_9;
  
  uStack_9 = DAT_febee831;
  FUN_0007016e(DAT_febee831,1,&uStack_9);
  *param_1 = uStack_9;
  return 0;
}



undefined4 f33_rdbi_1c49_callback(undefined1 *param_1)

{
  undefined1 uStack_9;
  
  uStack_9 = DAT_febee83e;
  FUN_0007016e(DAT_febee83e,1,&uStack_9);
  *param_1 = uStack_9;
  return 0;
}



undefined4 f33_rdbi_1c4b_callback(undefined1 *param_1)

{
  undefined2 uStack_a;
  
  uStack_a = DAT_febee8be;
  FUN_00070180(DAT_febee8be,0xff,&uStack_a);
  *param_1 = (char)uStack_a;
  return 0;
}



undefined4 f33_rdbi_1c4f_callback(undefined1 *param_1)

{
  undefined1 uStack_9;
  
  uStack_9 = DAT_febee83f;
  FUN_0007016e(DAT_febee83f,1,&uStack_9);
  *param_1 = uStack_9;
  return 0;
}



undefined4 f33_rdbi_1c51_callback(undefined1 *param_1)

{
  undefined2 uStack_a;
  
  uStack_a = DAT_febee8c0;
  FUN_00070180(DAT_febee8c0,0xff,&uStack_a);
  *param_1 = (char)uStack_a;
  return 0;
}



undefined4 f33_rdbi_1c52_callback(undefined1 *param_1)

{
  undefined1 uStack_9;
  
  uStack_9 = DAT_febee860;
  FUN_0007016e(DAT_febee860,0xf,&uStack_9);
  *param_1 = uStack_9;
  return 0;
}



undefined4 f33_rdbi_1c81_callback(undefined1 *param_1)

{
  undefined4 uVar1;
  undefined2 uStack_a;
  
  uVar1 = FUN_000546f2(8);
  uStack_a = (undefined2)uVar1;
  FUN_00070180(uVar1,0xff,&uStack_a);
  *param_1 = (char)uStack_a;
  return 0;
}



undefined4 f33_rdbi_1c82_callback(undefined1 *param_1)

{
  undefined4 uVar1;
  undefined2 uStack_a;
  
  uVar1 = FUN_000546f2(2);
  uStack_a = (undefined2)uVar1;
  FUN_00070180(uVar1,0xff,&uStack_a);
  *param_1 = (char)uStack_a;
  return 0;
}



undefined4 f33_rdbi_1c83_callback(undefined1 *param_1)

{
  undefined4 uVar1;
  undefined2 uStack_a;
  
  uVar1 = FUN_000546f2(3);
  uStack_a = (undefined2)uVar1;
  FUN_00070180(uVar1,0xff,&uStack_a);
  *param_1 = (char)uStack_a;
  return 0;
}



undefined4 f33_rdbi_1c84_callback(undefined1 *param_1)

{
  undefined4 uVar1;
  undefined2 uStack_a;
  
  uVar1 = FUN_000546f2(0xd);
  uStack_a = (undefined2)uVar1;
  FUN_00070180(uVar1,0xff,&uStack_a);
  *param_1 = (char)uStack_a;
  return 0;
}



undefined4 f33_rdbi_1c86_callback(undefined1 *param_1)

{
  undefined2 uStack_a;
  
  uStack_a = DAT_febe7bcc;
  FUN_00070180(DAT_febe7bcc,0xff,&uStack_a);
  *param_1 = (char)uStack_a;
  return 0;
}



undefined4 f33_rdbi_1c87_callback(int param_1)

{
  undefined1 uStack_f;
  undefined2 uStack_e;
  undefined4 uStack_c;
  
  uStack_c = DAT_febe7bd4;
  uStack_e = DAT_febe7bd0;
  uStack_f = DAT_febe7bc9;
  FUN_00070180(DAT_febe7bd0,0xfffe,&uStack_e);
  FUN_00070192(uStack_c,0xfffffffe,&uStack_c);
  FUN_0007016e(uStack_f,1,&uStack_f);
  FUN_0006a574(uStack_e, ((undefined1 *)camry_host_ptr((uint32_t)(param_1))));
  FUN_0006a55c(uStack_c, ((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 2))));
  (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 6)))) = uStack_f;
  return 0;
}



undefined4 f33_rdbi_1c99_callback(void)

{
  return 0;
}



undefined4 f33_rdbi_1c9a_callback(void)

{
  return 0;
}



undefined4 f33_rdbi_1c9b_callback(void)

{
  return 0;
}



undefined4 f33_rdbi_1c9c_callback(void)

{
  return 0;
}



undefined4 f33_rdbi_1c9d_callback(void)

{
  return 0;
}



undefined4 f33_rdbi_1c9e_callback(void)

{
  return 0;
}



undefined4 f33_rdbi_1c9f_callback(void)

{
  return 0;
}



undefined4 f33_rdbi_1ca0_callback(void)

{
  return 0;
}



undefined4 f33_rdbi_1ca1_callback(undefined1 *param_1)

{
  undefined1 uStack_9;
  
  uStack_9 = DAT_febee816;
  FUN_0007016e(DAT_febee816,0xff,&uStack_9);
  *param_1 = uStack_9;
  return 0;
}



undefined4 f33_rdbi_1ca2_callback(int param_1)

{
  undefined1 uStack_f;
  undefined2 uStack_e;
  undefined4 uStack_c;
  
  uStack_c = DAT_febee914;
  uStack_e = DAT_febee898;
  uStack_f = DAT_febee818;
  FUN_00070180(DAT_febee898,0xfffe,&uStack_e);
  FUN_00070192(uStack_c,0xfffffffe,&uStack_c);
  FUN_0007016e(uStack_f,1,&uStack_f);
  FUN_0006a574(uStack_e, ((undefined1 *)camry_host_ptr((uint32_t)(param_1))));
  FUN_0006a55c(uStack_c, ((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 2))));
  (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 6)))) = uStack_f;
  return 0;
}



undefined4 f33_rdbi_1ca3_callback(undefined4 param_1)

{
  undefined2 uStack_a;
  
  uStack_a = DAT_febee8a0;
  FUN_00070180(DAT_febee8a0,0xffff,&uStack_a);
  FUN_0006a574(uStack_a, ((undefined1 *)camry_host_ptr((uint32_t)(param_1))));
  return 0;
}



undefined4 f33_rdbi_1ca4_callback(undefined4 param_1)

{
  undefined2 uStack_a;
  
  uStack_a = (undefined2)((uint)DAT_febee89c * 100 >> 8);
  FUN_00070180((uint)DAT_febee89c * 100 >> 8,0x9c4,&uStack_a);
  FUN_0006a574(uStack_a, ((undefined1 *)camry_host_ptr((uint32_t)(param_1))));
  return 0;
}



undefined4 f33_rdbi_1ca5_callback(undefined1 *param_1)

{
  undefined1 uStack_9;
  
  uStack_9 = DAT_febee817;
  FUN_0007016e(DAT_febee817,0xff,&uStack_9);
  *param_1 = uStack_9;
  return 0;
}



undefined4 f33_rdbi_1ca6_callback(int param_1)

{
  undefined1 uStack_f;
  undefined2 uStack_e;
  undefined4 uStack_c;
  
  uStack_c = DAT_febee918;
  uStack_e = DAT_febee89a;
  uStack_f = DAT_febee819;
  FUN_00070180(DAT_febee89a,0xfffe,&uStack_e);
  FUN_00070192(uStack_c,0xfffffffe,&uStack_c);
  FUN_0007016e(uStack_f,1,&uStack_f);
  FUN_0006a574(uStack_e, ((undefined1 *)camry_host_ptr((uint32_t)(param_1))));
  FUN_0006a55c(uStack_c, ((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 2))));
  (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 6)))) = uStack_f;
  return 0;
}



undefined4 f33_rdbi_1ca7_callback(undefined4 param_1)

{
  undefined2 uStack_a;
  
  uStack_a = DAT_febee8a2;
  FUN_00070180(DAT_febee8a2,0xffff,&uStack_a);
  FUN_0006a574(uStack_a, ((undefined1 *)camry_host_ptr((uint32_t)(param_1))));
  return 0;
}



undefined4 f33_rdbi_1ca8_callback(undefined4 param_1)

{
  undefined2 uStack_a;
  
  uStack_a = (undefined2)((uint)DAT_febee89e * 100 >> 8);
  FUN_00070180((uint)DAT_febee89e * 100 >> 8,0x9c4,&uStack_a);
  FUN_0006a574(uStack_a, ((undefined1 *)camry_host_ptr((uint32_t)(param_1))));
  return 0;
}



/* WARNING: Removing unreachable block (ram,0x0004f01c) */

undefined4 f33_rdbi_1ca9_callback(undefined4 param_1)

{
  short sStack_a;
  
  sStack_a = (short)((DAT_febe6f00 * 100) / 0x80);
  FUN_00070110((int)sStack_a,25000,0,&sStack_a);
  FUN_0006a574(sStack_a, ((undefined1 *)camry_host_ptr((uint32_t)(param_1))));
  return 0;
}



/* WARNING: Removing unreachable block (ram,0x0004f056) */

undefined4 f33_rdbi_1caa_callback(undefined4 param_1)

{
  short sStack_a;
  
  sStack_a = (short)((DAT_febe6f02 * 100) / 0x80);
  FUN_00070110((int)sStack_a,25000,0,&sStack_a);
  FUN_0006a574(sStack_a, ((undefined1 *)camry_host_ptr((uint32_t)(param_1))));
  return 0;
}



undefined4 f33_rdbi_1cab_callback(undefined4 param_1,undefined2 param_2)

{
  FUN_00052972(param_1,param_2);
  return 0;
}



/* Gather bank0 into52-byte stack envelope; currentB770!=5A hides integral/age fields,
   currentB6DF!=5A masks numerical observation groups with capture sentinel32767, and
   publishedE813!=5A replaces six packed bytesFF. Then serialize45 bytes; retained RAM is unchanged.
    */

void f33_read_first_control_profile(uchar *output,uchar slot)

{
  uint32_t puVar1;
  F33RetainedControlProfile FStack_3c;
  
  puVar1 = 0xfebeb800u;
  f33_gather_first_control_profile(&FStack_3c,slot);
  if (FStack_3c.current_elapsed_source_validity != 'Z') {
    FStack_3c.integrated_source = 0;
    FStack_3c.elapsed_groups = 0;
  }
  if (FStack_3c.current_first_profile_validity != 'Z') {
    FStack_3c.scaled_b054_mean = 0;
    FStack_3c.scaled_b054_max = 0;
    FStack_3c.scaled_ae5c_min = 0;
    FStack_3c.scaled_ae5c_max = 0;
    FStack_3c.f1ca_mean = 0;
    FStack_3c.f1ca_max = 0;
    FStack_3c.f1c8_mean = 0;
    FStack_3c.f1c8_max = 0;
    FStack_3c.f1c6_mean = 0;
    FStack_3c.f1c6_max = 0;
    FStack_3c.source_u16_mean = 0;
    FStack_3c.source_u16_max = 0;
    FStack_3c.capture_value = 0x7fff;
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x3013))))) != 'Z') {
    FStack_3c.packed_metadata[0] = 0xff;
    FStack_3c.packed_metadata[1] = 0xff;
    FStack_3c.packed_metadata[2] = 0xff;
    FStack_3c.packed_metadata[3] = 0xff;
    FStack_3c.packed_metadata[4] = 0xff;
    FStack_3c.packed_metadata[5] = 0xff;
  }
  f33_serialize_retained_control_profile(output,&FStack_3c);
  return;
}



/* Configured45-byte read of first profile, slot0; apply current validity/publication gates without
   mutating retained RAM. Return0; supplied length is ignored by this fixed callback. DID1D00 is a
   separate bitmap, not a profile. */

uint f33_rdbi_1cf4_callback(uchar *output,ushort length)

{
  f33_read_first_control_profile(output,'\0');
  return 0;
}



/* Configured45-byte read of first profile, slot1; apply current validity/publication gates without
   mutating retained RAM. Return0; supplied length is ignored by this fixed callback. DID1D00 is a
   separate bitmap, not a profile. */

uint f33_rdbi_1cf5_callback(uchar *output,ushort length)

{
  f33_read_first_control_profile(output,'\x01');
  return 0;
}



/* Configured45-byte read of first profile, slot2; apply current validity/publication gates without
   mutating retained RAM. Return0; supplied length is ignored by this fixed callback. DID1D00 is a
   separate bitmap, not a profile. */

uint f33_rdbi_1cf6_callback(uchar *output,ushort length)

{
  f33_read_first_control_profile(output,'\x02');
  return 0;
}



/* Configured45-byte read of first profile, slot3; apply current validity/publication gates without
   mutating retained RAM. Return0; supplied length is ignored by this fixed callback. DID1D00 is a
   separate bitmap, not a profile. */

uint f33_rdbi_1cf7_callback(uchar *output,ushort length)

{
  f33_read_first_control_profile(output,'\x03');
  return 0;
}



/* Configured45-byte read of first profile, slot4; apply current validity/publication gates without
   mutating retained RAM. Return0; supplied length is ignored by this fixed callback. DID1D00 is a
   separate bitmap, not a profile. */

uint f33_rdbi_1cf8_callback(uchar *output,ushort length)

{
  f33_read_first_control_profile(output,'\x04');
  return 0;
}



/* Gather bank1 into52-byte stack envelope; currentB770!=5A hides integral/age fields,
   currentB6DF!=5A masks numerical observation groups with capture sentinel32767, and
   publishedE813!=5A replaces six packed bytesFF. Then serialize45 bytes; retained RAM is unchanged.
    */

void f33_read_first_ranked_control_profile(uchar *output,uchar slot)

{
  uint32_t puVar1;
  F33RetainedControlProfile FStack_3c;
  
  puVar1 = 0xfebeb800u;
  f33_gather_first_ranked_control_profile(&FStack_3c,slot);
  if (FStack_3c.current_elapsed_source_validity != 'Z') {
    FStack_3c.integrated_source = 0;
    FStack_3c.elapsed_groups = 0;
  }
  if (FStack_3c.current_first_profile_validity != 'Z') {
    FStack_3c.scaled_b054_mean = 0;
    FStack_3c.scaled_b054_max = 0;
    FStack_3c.scaled_ae5c_min = 0;
    FStack_3c.scaled_ae5c_max = 0;
    FStack_3c.f1ca_mean = 0;
    FStack_3c.f1ca_max = 0;
    FStack_3c.f1c8_mean = 0;
    FStack_3c.f1c8_max = 0;
    FStack_3c.f1c6_mean = 0;
    FStack_3c.f1c6_max = 0;
    FStack_3c.source_u16_mean = 0;
    FStack_3c.source_u16_max = 0;
    FStack_3c.capture_value = 0x7fff;
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x3013))))) != 'Z') {
    FStack_3c.packed_metadata[0] = 0xff;
    FStack_3c.packed_metadata[1] = 0xff;
    FStack_3c.packed_metadata[2] = 0xff;
    FStack_3c.packed_metadata[3] = 0xff;
    FStack_3c.packed_metadata[4] = 0xff;
    FStack_3c.packed_metadata[5] = 0xff;
  }
  f33_serialize_retained_control_profile(output,&FStack_3c);
  return;
}



/* Configured45-byte read of magnitude-rank1 profile, slot0; apply current validity/publication
   gates without mutating retained RAM. Return0; supplied length is ignored by this fixed callback.
   DID1D00 is a separate bitmap, not a profile. */

uint f33_rdbi_1cf9_callback(uchar *output,ushort length)

{
  f33_read_first_ranked_control_profile(output,'\0');
  return 0;
}



/* Gather bank2 into52-byte stack envelope; currentB770!=5A hides integral/age fields,
   currentB6DF!=5A masks numerical observation groups with capture sentinel32767, and
   publishedE813!=5A replaces six packed bytesFF. Then serialize45 bytes; retained RAM is unchanged.
    */

void f33_read_second_ranked_control_profile(uchar *output,uchar slot)

{
  uint32_t puVar1;
  F33RetainedControlProfile FStack_3c;
  
  puVar1 = 0xfebeb800u;
  f33_gather_second_ranked_control_profile(&FStack_3c,slot);
  if (FStack_3c.current_elapsed_source_validity != 'Z') {
    FStack_3c.integrated_source = 0;
    FStack_3c.elapsed_groups = 0;
  }
  if (FStack_3c.current_first_profile_validity != 'Z') {
    FStack_3c.scaled_b054_mean = 0;
    FStack_3c.scaled_b054_max = 0;
    FStack_3c.scaled_ae5c_min = 0;
    FStack_3c.scaled_ae5c_max = 0;
    FStack_3c.f1ca_mean = 0;
    FStack_3c.f1ca_max = 0;
    FStack_3c.f1c8_mean = 0;
    FStack_3c.f1c8_max = 0;
    FStack_3c.f1c6_mean = 0;
    FStack_3c.f1c6_max = 0;
    FStack_3c.source_u16_mean = 0;
    FStack_3c.source_u16_max = 0;
    FStack_3c.capture_value = 0x7fff;
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x3013))))) != 'Z') {
    FStack_3c.packed_metadata[0] = 0xff;
    FStack_3c.packed_metadata[1] = 0xff;
    FStack_3c.packed_metadata[2] = 0xff;
    FStack_3c.packed_metadata[3] = 0xff;
    FStack_3c.packed_metadata[4] = 0xff;
    FStack_3c.packed_metadata[5] = 0xff;
  }
  f33_serialize_retained_control_profile(output,&FStack_3c);
  return;
}



/* Configured45-byte read of magnitude-rank2 profile, slot0; apply current validity/publication
   gates without mutating retained RAM. Return0; supplied length is ignored by this fixed callback.
   DID1D00 is a separate bitmap, not a profile. */

uint f33_rdbi_1cfa_callback(uchar *output,ushort length)

{
  f33_read_second_ranked_control_profile(output,'\0');
  return 0;
}



/* Configured45-byte read of magnitude-rank1 profile, slot1; apply current validity/publication
   gates without mutating retained RAM. Return0; supplied length is ignored by this fixed callback.
   DID1D00 is a separate bitmap, not a profile. */

uint f33_rdbi_1cfb_callback(uchar *output,ushort length)

{
  f33_read_first_ranked_control_profile(output,'\x01');
  return 0;
}



/* Configured45-byte read of magnitude-rank2 profile, slot1; apply current validity/publication
   gates without mutating retained RAM. Return0; supplied length is ignored by this fixed callback.
   DID1D00 is a separate bitmap, not a profile. */

uint f33_rdbi_1cfc_callback(uchar *output,ushort length)

{
  f33_read_second_ranked_control_profile(output,'\x01');
  return 0;
}



/* Configured45-byte read of magnitude-rank1 profile, slot2; apply current validity/publication
   gates without mutating retained RAM. Return0; supplied length is ignored by this fixed callback.
   DID1D00 is a separate bitmap, not a profile. */

uint f33_rdbi_1cfd_callback(uchar *output,ushort length)

{
  f33_read_first_ranked_control_profile(output,'\x02');
  return 0;
}



/* Configured45-byte read of magnitude-rank2 profile, slot2; apply current validity/publication
   gates without mutating retained RAM. Return0; supplied length is ignored by this fixed callback.
   DID1D00 is a separate bitmap, not a profile. */

uint f33_rdbi_1cfe_callback(uchar *output,ushort length)

{
  f33_read_second_ranked_control_profile(output,'\x02');
  return 0;
}



/* Configured45-byte read of magnitude-rank1 profile, slot3; apply current validity/publication
   gates without mutating retained RAM. Return0; supplied length is ignored by this fixed callback.
   DID1D00 is a separate bitmap, not a profile. */

uint f33_rdbi_1cff_callback(uchar *output,ushort length)

{
  f33_read_first_ranked_control_profile(output,'\x03');
  return 0;
}



/* Configured45-byte read of magnitude-rank2 profile, slot3; apply current validity/publication
   gates without mutating retained RAM. Return0; supplied length is ignored by this fixed callback.
   DID1D00 is a separate bitmap, not a profile. */

uint f33_rdbi_1d01_callback(uchar *output,ushort length)

{
  f33_read_second_ranked_control_profile(output,'\x03');
  return 0;
}



/* Configured45-byte read of magnitude-rank1 profile, slot4; apply current validity/publication
   gates without mutating retained RAM. Return0; supplied length is ignored by this fixed callback.
   DID1D00 is a separate bitmap, not a profile. */

uint f33_rdbi_1d02_callback(uchar *output,ushort length)

{
  f33_read_first_ranked_control_profile(output,'\x04');
  return 0;
}



/* Configured45-byte read of magnitude-rank2 profile, slot4; apply current validity/publication
   gates without mutating retained RAM. Return0; supplied length is ignored by this fixed callback.
   DID1D00 is a separate bitmap, not a profile. */

uint f33_rdbi_1d03_callback(uchar *output,ushort length)

{
  f33_read_second_ranked_control_profile(output,'\x04');
  return 0;
}



undefined4 f33_rdbi_1f03_callback(void)

{
  return 0;
}



undefined4 f33_rdbi_1f04_callback(void)

{
  return 0;
}



undefined4 f33_rdbi_2001_callback(undefined1 *param_1)

{
  undefined1 uVar1;
  
  uVar1 = 0xff;
  if (DAT_febee849 == 'D') {
    uVar1 = f33_return_const_1_b5ed0();
  }
  *param_1 = uVar1;
  return 0;
}



undefined4 f33_rdbi_2002_callback(undefined1 *param_1)

{
  undefined1 uVar1;
  
  if (DAT_febee91c == 0x55aaaa55) {
    uVar1 = 0;
  }
  else if (DAT_febee91c == -0x55aaaa56) {
    uVar1 = 1;
  }
  else {
    uVar1 = 0xff;
  }
  *param_1 = uVar1;
  return 0;
}



undefined4 f33_rdbi_2003_callback(undefined1 *param_1)

{
  undefined4 uVar1;
  undefined1 uStack_9;
  
  if (DAT_febee849 == 'D') {
    uVar1 = ((void)(7), f33_return_const_ff_b5ed4());
    uStack_9 = (undefined1)uVar1;
    FUN_0007016e(uVar1,0xff,&uStack_9);
  }
  else {
    uStack_9 = 0xff;
  }
  *param_1 = uStack_9;
  return 0;
}



undefined4 f33_rdbi_2004_callback(undefined1 *param_1)

{
  undefined4 uVar1;
  undefined1 uStack_9;
  
  if (DAT_febee849 == 'D') {
    uVar1 = ((void)(8), f33_return_const_ff_b5ed4());
    uStack_9 = (undefined1)uVar1;
    FUN_0007016e(uVar1,0xff,&uStack_9);
  }
  else {
    uStack_9 = 0xff;
  }
  *param_1 = uStack_9;
  return 0;
}



undefined4 f33_rdbi_2005_callback(undefined1 *param_1)

{
  undefined1 uStack_9;
  
  uStack_9 = DAT_febee84d;
  if (DAT_febee84a == 'Z') {
    FUN_0007016e(DAT_febee84d,0xff,&uStack_9);
  }
  else {
    uStack_9 = 0xff;
  }
  *param_1 = uStack_9;
  return 0;
}



undefined4 f33_rdbi_2006_callback(undefined1 *param_1)

{
  undefined1 uStack_9;
  
  uStack_9 = DAT_febee84e;
  if (DAT_febee84a == 'Z') {
    FUN_0007016e(DAT_febee84e,0xff,&uStack_9);
  }
  else {
    uStack_9 = 0xff;
  }
  *param_1 = uStack_9;
  return 0;
}



undefined4 f33_rdbi_2007_callback(undefined1 *param_1)

{
  undefined1 uStack_9;
  
  uStack_9 = DAT_febee84f;
  if (DAT_febee84a == 'Z') {
    FUN_0007016e(DAT_febee84f,0xff,&uStack_9);
  }
  else {
    uStack_9 = 0xff;
  }
  *param_1 = uStack_9;
  return 0;
}



undefined4 f33_rdbi_2008_callback(undefined1 *param_1)

{
  undefined1 uStack_9;
  
  uStack_9 = DAT_febee850;
  if (DAT_febee84a == 'Z') {
    FUN_0007016e(DAT_febee850,0xff,&uStack_9);
  }
  else {
    uStack_9 = 0xff;
  }
  *param_1 = uStack_9;
  return 0;
}



undefined4 f33_rdbi_2009_callback(undefined1 *param_1)

{
  undefined1 uStack_9;
  
  uStack_9 = DAT_febee851;
  if (DAT_febee84a == 'Z') {
    FUN_0007016e(DAT_febee851,0xff,&uStack_9);
  }
  else {
    uStack_9 = 0xff;
  }
  *param_1 = uStack_9;
  return 0;
}



undefined4 f33_rdbi_200a_callback(undefined1 *param_1)

{
  undefined1 uStack_b;
  undefined1 uStack_a;
  undefined1 uStack_9;
  
  if (DAT_febee849 == 'D') {
    uStack_b = ((void)(9), f33_return_const_ff_b5ed4());
    uStack_a = ((void)(10), f33_return_const_ff_b5ed4());
    uStack_9 = ((void)(0xb), f33_return_const_ff_b5ed4());
    FUN_0007016e(uStack_b,0xff,&uStack_b);
    FUN_0007016e(uStack_a,0xff,&uStack_a);
    FUN_0007016e(uStack_9,0xff,&uStack_9);
    *param_1 = uStack_b;
    param_1[1] = uStack_a;
  }
  else {
    uStack_9 = 0xff;
    *param_1 = 0xff;
    param_1[1] = 0xff;
  }
  param_1[2] = uStack_9;
  return 0;
}



undefined4 f33_rdbi_200b_callback(undefined1 *param_1)

{
  undefined1 local_c;
  undefined1 uStack_b;
  undefined1 uStack_a;
  undefined1 uStack_9;
  
  if (DAT_febee849 == 'D') {
    local_c = ((void)(0), f33_return_const_ff_b5ed4());
    uStack_b = ((void)(1), f33_return_const_ff_b5ed4());
    uStack_a = ((void)(2), f33_return_const_ff_b5ed4());
    uStack_9 = ((void)(3), f33_return_const_ff_b5ed4());
    FUN_0007016e(local_c,0xff,&local_c);
    FUN_0007016e(uStack_b,0xff,&uStack_b);
    FUN_0007016e(uStack_a,0xff,&uStack_a);
    FUN_0007016e(uStack_9,0xff,&uStack_9);
    *param_1 = local_c;
    param_1[1] = uStack_b;
    param_1[2] = uStack_a;
  }
  else {
    uStack_9 = 0xff;
    *param_1 = 0xff;
    param_1[1] = 0xff;
    param_1[2] = 0xff;
  }
  param_1[3] = uStack_9;
  return 0;
}



undefined4 f33_rdbi_200c_callback(undefined1 *param_1)

{
  undefined4 uVar1;
  undefined1 uStack_9;
  
  if (DAT_febee849 == 'D') {
    uVar1 = ((void)(4), f33_return_const_ff_b5ed4());
    uStack_9 = (undefined1)uVar1;
    FUN_0007016e(uVar1,0xff,&uStack_9);
  }
  else {
    uStack_9 = 0xff;
  }
  *param_1 = uStack_9;
  return 0;
}



undefined4 f33_rdbi_200d_callback(undefined1 *param_1)

{
  undefined1 uStack_9;
  
  uStack_9 = DAT_febee852;
  if (DAT_febee84a == 'Z') {
    FUN_0007016e(DAT_febee852,0xff,&uStack_9);
  }
  else {
    uStack_9 = 0xff;
  }
  *param_1 = uStack_9;
  return 0;
}



undefined4 f33_rdbi_200e_callback(undefined1 *param_1)

{
  undefined4 uVar1;
  undefined1 uStack_9;
  
  if (DAT_febee849 == 'D') {
    uVar1 = ((void)(6), f33_return_const_ff_b5ed4());
    uStack_9 = (undefined1)uVar1;
    FUN_0007016e(uVar1,0xff,&uStack_9);
  }
  else {
    uStack_9 = 0xff;
  }
  *param_1 = uStack_9;
  return 0;
}



undefined4 f33_rdbi_200f_callback(undefined1 *param_1)

{
  undefined4 uVar1;
  undefined1 uStack_9;
  
  if (DAT_febee849 == 'D') {
    uVar1 = ((void)(0xc), f33_return_const_ff_b5ed4());
    uStack_9 = (undefined1)uVar1;
    FUN_0007016e(uVar1,0xff,&uStack_9);
  }
  else {
    uStack_9 = 0xff;
  }
  *param_1 = uStack_9;
  return 0;
}



undefined4 f33_rdbi_2010_callback(undefined1 *param_1)

{
  undefined1 uVar1;
  
  if ((DAT_febee924 == 0x55aaaa55) && (DAT_febee92c == 0x55aaaa55)) {
    uVar1 = 0;
    goto LAB_0004f976;
  }
  if (DAT_febee924 == -0x55aaaa56) {
    if (DAT_febee92c == 0x55aaaa55) {
      uVar1 = 1;
      goto LAB_0004f976;
    }
    if (DAT_febee92c == -0x55aaaa56) {
      uVar1 = 2;
      goto LAB_0004f976;
    }
  }
  if ((DAT_febee924 == 0x55aaaa55) && (DAT_febee92c == -0x55aaaa56)) {
    uVar1 = 3;
  }
  else {
    uVar1 = 0xff;
  }
LAB_0004f976:
  *param_1 = uVar1;
  return 0;
}



undefined4 f33_rdbi_2012_callback(undefined4 param_1)

{
  (*((bool *)camry_host_ptr((uint32_t)(param_1)))) = DAT_febee81e == 'Z';
  return 0;
}



undefined4 f33_rdbi_2013_callback(undefined4 param_1)

{
  FUN_0006a574(DAT_febee8e2, ((undefined1 *)camry_host_ptr((uint32_t)(param_1))));
  return 0;
}



undefined4 f33_rdbi_2014_callback(undefined4 param_1)

{
  (*((bool *)camry_host_ptr((uint32_t)(param_1)))) = DAT_febee886 != '\0';
  return 0;
}



undefined4 f33_rdbi_2030_callback(int param_1)

{
  undefined1 *puVar1;
  undefined1 *puVar2;
  uint uVar3;
  
  uVar3 = 0;
  do {
    puVar1 = ((undefined1 *)camry_host_ptr((uint32_t)(uVar3 + param_1)));
    *puVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x20850u + (uint32_t)(uVar3) * 1u))));
    puVar2 = ((undefined *)camry_host_ptr(0x17da0u)) + uVar3;
    uVar3 = uVar3 + 1;
    puVar1[8] = *puVar2;
  } while (uVar3 < 8);
  return 0;
}



undefined4 f33_rdbi_2032_callback(undefined1 *param_1)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  *param_1 = 1;
  iVar3 = FUN_00062e18();
  iVar2 = 0;
  if (iVar3 == 0) {
    do {
      iVar1 = iVar2 + 1;
      iVar3 = iVar2 + -0xf;
      param_1[iVar2 + 1] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x17d80u + (uint32_t)(iVar2) * 1u))));
      iVar2 = iVar1;
    } while (((iVar3 < 0) || (iVar1 < 0)));
  }
  else {
    do {
      iVar1 = iVar2 + 1;
      param_1[iVar2 + 1] = 0x21;
      iVar3 = iVar2 + -0xf;
      iVar2 = iVar1;
    } while (((iVar3 < 0) || (iVar1 < 0)));
  }
  return 0;
}



undefined4 f33_rdbi_f181_callback(undefined1 *param_1)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  *param_1 = 2;
  iVar3 = FUN_00062e18();
  iVar2 = 0;
  if (iVar3 == 0) {
    do {
      param_1[iVar2 + 1] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x20860u + (uint32_t)(iVar2) * 1u))));
      iVar1 = iVar2 + 1;
      iVar3 = iVar2 + -0xf;
      param_1[iVar2 + 0x11] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x17dc0u + (uint32_t)(iVar2) * 1u))));
      iVar2 = iVar1;
    } while (((iVar3 < 0) || (iVar1 < 0)));
  }
  else {
    do {
      iVar1 = iVar2 + 1;
      param_1[iVar2 + 1] = 0x21;
      iVar3 = iVar2 + -0xf;
      param_1[iVar2 + 0x11] = 0x21;
      iVar2 = iVar1;
    } while (((iVar3 < 0) || (iVar1 < 0)));
  }
  return 0;
}



undefined4 f33_rdbi_f186_callback(uchar *param_1)

{
  f33_dcm_get_session(param_1);
  return 0;
}



undefined4 f33_rdbi_f18c_callback(int param_1,uint param_2)

{
  int iVar1;
  uint *puVar2;
  int iVar3;
  uint uVar4;
  undefined4 uVar5;
  undefined4 *puVar6;
  uint local_34;
  undefined1 local_30 [36];
  
  puVar2 = &local_34;
  puVar6 = ((undefined *)camry_host_ptr(0x21320u));
  do {
    uVar5 = *puVar6;
    puVar6 = puVar6 + 1;
    *puVar2 = uVar5;
    puVar2 = puVar2 + 1;
  } while (puVar6 != (undefined4 *)((undefined *)camry_host_ptr(0x21348u)));
  uVar4 = f33_nvm_get_record(0x207, camry_host_addr(&local_34));
  if ((uVar4 == 0x10) && (local_34 == 0xa55a5aa5)) {
    for (iVar3 = 0; iVar1 = iVar3 - (param_2 & 0xffff), ((iVar1 < 0) || (iVar3 < 0));
        iVar3 = iVar3 + 1) {
      (*((undefined1 *)camry_host_ptr((uint32_t)(iVar3 + param_1)))) = local_30[iVar3];
    }
  }
  else {
    for (iVar3 = 0; iVar1 = iVar3 - (param_2 & 0xffff), ((iVar1 < 0) || (iVar3 < 0));
        iVar3 = iVar3 + 1) {
      (*((undefined1 *)camry_host_ptr((uint32_t)(iVar3 + param_1)))) = 0x3f;
    }
  }
  return 0;
}



undefined4 f33_rdbi_0101_callback(undefined4 param_1,undefined2 param_2)

{
  FUN_0004d1a4(param_1,param_2);
  return 0;
}



undefined4 f33_rdbi_0100_callback(uchar *param_1,ushort param_2)

{
  f33_serialize_available_did_bitmap(0x100,param_1,param_2);
  return 0;
}



undefined4 f33_rdbi_0200_callback(uchar *param_1,ushort param_2)

{
  f33_serialize_available_did_bitmap(0x200,param_1,param_2);
  return 0;
}



undefined4 f33_rdbi_1000_callback(uchar *param_1,ushort param_2)

{
  f33_serialize_available_did_bitmap(0x1000,param_1,param_2);
  return 0;
}



undefined4 f33_rdbi_1100_callback(uchar *param_1,ushort param_2)

{
  f33_serialize_available_did_bitmap(0x1100,param_1,param_2);
  return 0;
}



undefined4 f33_rdbi_1c00_callback(uchar *param_1,ushort param_2)

{
  f33_serialize_available_did_bitmap(0x1c00,param_1,param_2);
  return 0;
}



undefined4 f33_rdbi_1d00_callback(uchar *param_1,ushort param_2)

{
  f33_serialize_available_did_bitmap(0x1d00,param_1,param_2);
  return 0;
}



undefined4 f33_rdbi_1f00_callback(uchar *param_1,ushort param_2)

{
  f33_serialize_available_did_bitmap(0x1f00,param_1,param_2);
  return 0;
}



undefined4 f33_rdbi_2000_callback(uchar *param_1,ushort param_2)

{
  f33_serialize_available_did_bitmap(0x2000,param_1,param_2);
  return 0;
}



undefined4 f33_rdbi_f100_callback(uchar *param_1,ushort param_2)

{
  f33_serialize_available_did_bitmap(0xf100,param_1,param_2);
  return 0;
}



void FUN_0004fc2c(uint param_1,int param_2,int param_3)

{
  int iVar1;
  int iVar2;
  
  for (iVar2 = 0; iVar1 = iVar2 - (param_1 & 0xffff), ((iVar1 < 0) || (iVar2 < 0));
      iVar2 = iVar2 + 1) {
    (*((undefined1 *)camry_host_ptr((uint32_t)(iVar2 + param_3)))) = (*((undefined1 *)camry_host_ptr((uint32_t)(iVar2 + param_2))));
  }
  return;
}



/* CompareunsignedE892toROM318B0=384,returnstrictgreater. Do notaddnominalarguments
   merelybecausecallerspopulateR6/R7. */

uint f33_communication_request_sample_above_limit(void)

{
  return (uint)(f33_communication_control_admission_limit < DAT_febee892);
}



/* R6ignored;R7=0stores8196=00,R7=1stores11;otherlowbytesretain. Not7F97andnotphysicaldisable. */

void f33_publish_diagnostic_normal_tx_policy_request(uchar network_selector,uchar disable_tx)

{
  uchar uVar1;
  
  uVar1 = '\0';
  if ((disable_tx == '\0') || (uVar1 = '\x11', disable_tx == '\x01')) {
    f33_diagnostic_normal_tx_policy_request = uVar1;
  }
  return;
}



/* 81AF11 ->35AA2,B9320(11),12;21->B9320(22),22. Invokedwhile81B2=2E10. */

void f33_start_pending_write_mode_request(void)

{
  undefined1 uVar1;
  uint32_t puVar2;
  puVar2 = 0xfebeb800u;
  if (DAT_febe81af == '\x11') {
    puVar2 = 0xfebeb800u;
    FUN_00035aa2();
    ((void)(0x11), thunk_FUN_000b9320());
    uVar1 = 0x12;
  }
  else {
    if (DAT_febe81af != '!') {
      return;
    }
    ((void)(0x22), thunk_FUN_000b9320());
    uVar1 = 0x22;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x3651))))) = uVar1;
  return;
}



/* 81AF12->clear;22->5199E(operation6diagnosticqueue),clear;otherunchanged. */

void f33_finish_pending_write_mode_request(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_febe81af != '\x12') {
    if (DAT_febe81af != '\"') {
      return;
    }
    puVar1 = 0xfebeb800u;
    FUN_0005199e();
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3651))))) = 0;
  return;
}



/* UnsignedE892>ROM318AE512 =>5 else0;LDHU/CMP/CMOVH4FD88..4FD9A. */

uint f33_write_0204_precondition(void)

{
  uint uVar1;
  
  if (DAT_000318ae < DAT_febee892) {
    uVar1 = 5;
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}



/* 4FDA0 tst1bit7,1[r6];81AF=11/21,81B2=2E10,r10=2. Byte0 ignored. */

uint f33_write_0204_stage_mode_persistence(uchar *payload,ushort unused_length)

{
  DAT_febe81af = 0x21;
  if ((payload[1] & 0x80) != 0) {
    DAT_febe81af = 0x11;
  }
  DAT_febe81b2 = 0x2e10;
  return 2;
}



/* Exact20-byte identity to4FD88. */

uint f33_write_2001_precondition(void)

{
  uint uVar1;
  
  if (DAT_000318ae < DAT_febee892) {
    uVar1 = 5;
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}



/* Exact20-byte identity to4FD88. */

uint f33_write_2002_precondition(void)

{
  uint uVar1;
  
  if (DAT_000318ae < DAT_febee892) {
    uVar1 = 5;
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}



/* Byte0/1->55AAAA55/AA5555AA B7092;2/pending. Other4 clearsowner only. */

uint f33_write_2002_stage_record102_mode(uchar *payload,ushort unused_length)

{
  uint32_t puVar1;
  uint encoded_mode;
  undefined2 uVar2;
  uint uVar3;
  
  puVar1 = 0xfebeb800u;
  uVar2 = 0x2e10;
  uVar3 = 2;
  if (*payload == '\0') {
    encoded_mode = 0x55aaaa55;
  }
  else {
    if (*payload != '\x01') {
      uVar3 = 4;
      uVar2 = 0;
      goto LAB_0004fe44;
    }
    encoded_mode = 0xaa5555aa;
  }
  puVar1 = 0xfebeb800u;
  f33_stage_record102_mode_write(encoded_mode);
LAB_0004fe44:
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x364e)))) = uVar2;
  return uVar3;
}



/* Exact20-byte identity to4FD88. */

uint f33_write_2005_precondition(void)

{
  uint uVar1;
  
  if (DAT_000318ae < DAT_febee892) {
    uVar1 = 5;
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}



/* Byte readtor7,selector3r6 at4FE78..7C; B69A8 staging,2E10,status2. */

uint f33_write_2005_stage_record103_slot3(uchar *payload,ushort unused_length)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  f33_record103_byte_write_thunk('\x03',*payload);
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x364e)))) = 0x2e10;
  return 2;
}



/* Exact20-byte identity to4FD88. */

uint f33_write_2006_precondition(void)

{
  uint uVar1;
  
  if (DAT_000318ae < DAT_febee892) {
    uVar1 = 5;
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}



/* Byte readtor7,selector4;B69A8 staging,2E10,status2. */

uint f33_write_2006_stage_record103_slot4(uchar *payload,ushort unused_length)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  f33_record103_byte_write_thunk('\x04',*payload);
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x364e)))) = 0x2e10;
  return 2;
}



/* Exact20-byte identity to4FD88. */

uint f33_write_2007_precondition(void)

{
  uint uVar1;
  
  if (DAT_000318ae < DAT_febee892) {
    uVar1 = 5;
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}



/* Byte readtor7,selector5;B69A8 staging,2E10,status2. */

uint f33_write_2007_stage_record103_slot5(uchar *payload,ushort unused_length)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  f33_record103_byte_write_thunk('\x05',*payload);
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x364e)))) = 0x2e10;
  return 2;
}



/* Exact20-byte identity to4FD88. */

uint f33_write_2008_precondition(void)

{
  uint uVar1;
  
  if (DAT_000318ae < DAT_febee892) {
    uVar1 = 5;
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}



/* Byte readtor7,selector6;B69A8 staging,2E10,status2. */

uint f33_write_2008_stage_record103_slot6(uchar *payload,ushort unused_length)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  f33_record103_byte_write_thunk('\x06',*payload);
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x364e)))) = 0x2e10;
  return 2;
}



/* Exact20-byte identity to4FD88. */

uint f33_write_2009_precondition(void)

{
  uint uVar1;
  
  if (DAT_000318ae < DAT_febee892) {
    uVar1 = 5;
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}



/* Byte readtor7,selector7;B69A8 staging,2E10,status2. */

uint f33_write_2009_stage_record103_slot7(uchar *payload,ushort unused_length)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  f33_record103_byte_write_thunk('\a',*payload);
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x364e)))) = 0x2e10;
  return 2;
}



/* Exact20-byte identity to4FD88. */

uint f33_write_200d_precondition(void)

{
  uint uVar1;
  
  if (DAT_000318ae < DAT_febee892) {
    uVar1 = 5;
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}



/* Byte readtor7,selector8;B69A8 staging,2E10,status2. */

uint f33_write_200d_stage_record103_slot8(uchar *payload,ushort unused_length)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  f33_record103_byte_write_thunk('\b',*payload);
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x364e)))) = 0x2e10;
  return 2;
}



/* Exact20-byte identity to4FD88. */

uint f33_write_2010_precondition(void)

{
  uint uVar1;
  
  if (DAT_000318ae < DAT_febee892) {
    uVar1 = 5;
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}



/* 4FFB0 subtract1,4FFB4 cmp1,4FFB6 unsignedbh accepts1 AND2 aliases;0 alternatepair. B8FB2
   returns0.4FFCA4D118 returns0/4;4FFD8 storedoesnotclobberr10. NOTvoid. */

uint f33_write_2010_stage_mode_pair(uchar *payload,ushort unused_length)

{
  uchar uVar1;
  undefined2 uVar2;
  uint32_t puVar3;
  uint uVar4;
  
  puVar3 = 0xfebeb800u;
  uVar1 = *payload;
  if (uVar1 == '\0') {
    uVar4 = 0x55aaaa55;
  }
  else {
    uVar4 = 0xfffffff4;
    if (uVar1 != '\x01' && uVar1 != '\x02') goto LAB_0004ffca;
    uVar4 = 0xaa5555aa;
  }
  puVar3 = 0xfebeb800u;
  uVar4 = f33_stage_encoded_mode_pair_thunk(uVar4,0x55aaaa55);
LAB_0004ffca:
  uVar4 = f33_diag_translate_application_request_status(uVar4);
  uVar2 = 0;
  if (uVar4 == 2) {
    uVar2 = 0x2e10;
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x364e)))) = uVar2;
  return uVar4;
}



/* 00527f00=mov0,r10;jmplp, unconditional. */

uint f33_write_2012_precondition(void)

{
  return 0;
}



/* Byte1->B41A4/latchB18F5A,status0;else4. Doesnotclear81B2. */

uint f33_write_2012_latch_availability_override(uchar *payload,ushort unused_length)

{
  uint uVar1;
  
  if (*payload == '\x01') {
    f33_latch_availability_override();
    uVar1 = 0;
  }
  else {
    uVar1 = 4;
  }
  return uVar1;
}



/* GNU exact40bytes:80A5!=0 OR80A0!=0 ORu16E892>512=>5 else0. a497a5c8 displacementc8a5 loads80A5,
   NOT80A4. Seeded from the exact callback pointer. Live address unanalysed. */

uint f33_write_2013_precondition(void)

{
  if (((DAT_febe80a5 == '\0') && (DAT_febe80a0 == '\0')) && (DAT_febee892 <= DAT_000318ae)) {
    return 0;
  }
  return 5;
}


