#include "common.h"


void FUN_0006008e(ushort param_1,ushort param_2)

{
  byte bVar1;
  int iVar2;
  
  iVar2 = (short)((param_1 & 0xff) * 5 + (param_2 & 0xff)) * 0x28;
  bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x310a8u + (uint32_t)(iVar2) * 1u))));
  if (bVar1 < 0x10) {
    FUN_000607fe(bVar1);
    FUN_0006082c(((undefined *)camry_host_ptr(0x310a8u)) + iVar2);
    FUN_0006080e(bVar1);
  }
  return;
}



void FUN_000600ca(void)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  
  uVar3 = 0;
  do {
    iVar1 = uVar3 * 0x1000;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfff91400u + (uint32_t)(iVar1) * 1u)))) = 1;
    f33_spin_wait(1);
    FUN_0006008e(uVar3,0);
    iVar2 = (short)uVar3 * 0x28;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfff91490u + (uint32_t)(iVar1) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfff91490u + (uint32_t)(iVar1) * 1u)))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x3105cu + (uint32_t)(iVar2) * 1u))));
    FUN_0006008e(uVar3,1);
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfff91510u + (uint32_t)(iVar1) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfff91510u + (uint32_t)(iVar1) * 1u)))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x31064u + (uint32_t)(iVar2) * 1u))));
    FUN_0006008e(uVar3,2);
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfff91590u + (uint32_t)(iVar1) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfff91590u + (uint32_t)(iVar1) * 1u)))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x3106cu + (uint32_t)(iVar2) * 1u))));
    FUN_0006008e(uVar3,3);
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfff91610u + (uint32_t)(iVar1) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfff91610u + (uint32_t)(iVar1) * 1u)))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x31074u + (uint32_t)(iVar2) * 1u))));
    FUN_0006008e(uVar3,4);
    uVar3 = uVar3 + 1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfff91690u + (uint32_t)(iVar1) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfff91690u + (uint32_t)(iVar1) * 1u)))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x3107cu + (uint32_t)(iVar2) * 1u))));
  } while (uVar3 < 2);
  return;
}



/* Sequential initializer chain: 5 unconditional calls and no other statements; shape-verified. The
   called sequence is the function's entire behavior; chain family members differ in callee sets. */

void f33_run_init_chain_60178(void)

{
  FUN_0005face();
  f33_fill_constant_block_5fafe();
  FUN_0005ff08();
  FUN_0005ff98();
  FUN_000600ca();
  return;
}



void FUN_00060194(void)

{
  byte bVar1;
  char cVar2;
  uint uVar3;
  int iVar4;
  ushort uVar5;
  
  bVar1 = DAT_fff91420;
  DAT_fff91420 = bVar1 & 0x23;
  bVar1 = DAT_fff92420;
  DAT_fff92420 = bVar1 & 0x23;
  bVar1 = DAT_fff91424;
  DAT_fff91424 = bVar1 & 0x23;
  bVar1 = DAT_fff92424;
  DAT_fff92424 = bVar1 & 0x23;
  uVar3 = 0;
  do {
    iVar4 = uVar3 * 0x80;
    uVar3 = uVar3 + 1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfff91490u + (uint32_t)(iVar4) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfff91490u + (uint32_t)(iVar4) * 1u)))) & 0x30;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfff92490u + (uint32_t)(iVar4) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfff92490u + (uint32_t)(iVar4) * 1u)))) & 0x30;
  } while (uVar3 < 5);
  iVar4 = 0;
  uVar5 = 0;
  do {
    if (DAT_00030f2a < uVar5) break;
    cVar2 = DAT_fff914a4;
    if ((((((cVar2 == '\0') && (cVar2 = DAT_fff91524, cVar2 == '\0')) &&
          (cVar2 = DAT_fff915a4, cVar2 == '\0')) &&
         ((cVar2 = DAT_fff91624, cVar2 == '\0' && (cVar2 = DAT_fff916a4, cVar2 == '\0')))) &&
        ((cVar2 = DAT_fff924a4, cVar2 == '\0' &&
         ((cVar2 = DAT_fff92524, cVar2 == '\0' && (cVar2 = DAT_fff925a4, cVar2 == '\0')))))) &&
       ((cVar2 = DAT_fff92624, cVar2 == '\0' && (cVar2 = DAT_fff926a4, cVar2 == '\0')))) {
      iVar4 = 0x5a;
    }
    else {
      f33_spin_wait(1);
    }
    uVar5 = uVar5 + 1;
  } while (iVar4 != 0x5a);
  DAT_fff91380 = 1;
  DAT_fff92380 = 1;
  DAT_fff91404 = 1;
  DAT_fff92404 = 1;
  DAT_fff91430 = 0;
  DAT_fff92430 = 0;
  return;
}



void FUN_000602ac(void)

{
  uint uVar1;
  int iVar2;
  byte bVar3;
  undefined1 uVar4;
  uint uVar5;
  
  DAT_fff91430 = 0x1a;
  DAT_fff92430 = 0xe;
  DAT_fff91400 = 1;
  DAT_fff92400 = 1;
  f33_spin_wait(1);
  uVar5 = 0;
  do {
    uVar1 = uVar5 + 1;
    iVar2 = uVar5 * 0x80;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfff91490u + (uint32_t)(iVar2) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfff91490u + (uint32_t)(iVar2) * 1u)))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x3105cu + (uint32_t)(uVar5 * 8) * 1u))));
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfff92490u + (uint32_t)(iVar2) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfff92490u + (uint32_t)(iVar2) * 1u)))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x31084u + (uint32_t)(uVar5 * 8) * 1u))));
    uVar5 = uVar1;
  } while (uVar1 < 5);
  bVar3 = DAT_fff91420;
  DAT_fff91420 = bVar3 | 0x32;
  bVar3 = DAT_fff92420;
  DAT_fff92420 = bVar3 | 0x32;
  uVar4 = DAT_fff91424;
  DAT_fff91424 = uVar4;
  uVar4 = DAT_fff92424;
  DAT_fff92424 = uVar4;
  return;
}



undefined4 FUN_0006033a(uint param_1)

{
  int iVar1;
  undefined4 uVar2;
  uint uVar3;
  int iVar4;
  int iVar5;
  uint uVar6;
  
  param_1 = param_1 & 0xff;
  iVar5 = 0;
  iVar4 = 0;
  uVar2 = 0;
  if (param_1 < 2) {
    uVar6 = 0;
    do {
      iVar1 = param_1 * 0x1000;
      uVar3 = *(uint *)(((undefined *)camry_host_ptr(0x30f98u)) + ((short)param_1 * 0x18 + uVar6) * 4);
      if ((*(uint *)(((undefined *)camry_host_ptr(0xfff91000u)) + uVar6 * 4 + iVar1) & 0x3e03f) != uVar3) {
        FUN_00060194();
        *(uint *)(((undefined *)camry_host_ptr(0xfff91000u)) + uVar6 * 4 + iVar1) = uVar3;
        iVar5 = 0x5a;
        FUN_000602ac();
      }
      uVar6 = uVar6 + 1;
    } while (uVar6 < 0x18);
    if ((char)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfff913e8u + (uint32_t)(iVar1) * 1u)))) < '\0') {
      iVar4 = 0x5a;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfff913d8u + (uint32_t)(iVar1) * 1u)))) = 1;
    }
    if ((iVar5 == 0x5a) || (iVar4 == 0x5a)) {
      uVar2 = 0x5a;
    }
    else {
      uVar2 = 0;
    }
  }
  return uVar2;
}



void FUN_000603c8(void)

{
  uint32_t puVar1;
  undefined1 uVar2;
  
  puVar1 = 0xfebeb800u;
  uVar2 = FUN_0006033a(0);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x7ff6))))) = uVar2;
  uVar2 = FUN_0006033a(1);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x7ff5))))) = uVar2;
  return;
}



void FUN_000603e4(char param_1,char param_2,char param_3)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  
  if (param_1 == 'Z') {
    DAT_fff89110 = 2;
    DAT_fff91340 = 0;
    DAT_fff92340 = 0;
  }
  if (param_2 == 'Z') {
    uVar3 = 0;
    do {
      iVar1 = uVar3 * 8;
      iVar2 = uVar3 * 0x80;
      uVar3 = uVar3 + 1;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfff91494u + (uint32_t)(iVar2) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x31059u + (uint32_t)(iVar1) * 1u))));
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfff92494u + (uint32_t)(iVar2) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x31081u + (uint32_t)(iVar1) * 1u))));
    } while (uVar3 < 5);
  }
  if (param_3 == 'Z') {
    uVar3 = 0;
    do {
      iVar1 = uVar3 * 8;
      iVar2 = uVar3 * 0x80;
      uVar3 = uVar3 + 1;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfff91498u + (uint32_t)(iVar2) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x3105au + (uint32_t)(iVar1) * 1u))));
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfff92498u + (uint32_t)(iVar2) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x31082u + (uint32_t)(iVar1) * 1u))));
    } while (uVar3 < 5);
  }
  return;
}



void FUN_00060462(void)

{
  short sVar1;
  char cVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  uint uVar6;
  
  iVar4 = DAT_fff89110;
  iVar5 = 0;
  if (((iVar4 != 2) || (sVar1 = DAT_fff91340, sVar1 != 0)) || (sVar1 = DAT_fff92340, sVar1 != 0)) {
    iVar5 = 0x5a;
  }
  iVar4 = 0;
  cVar2 = DAT_fff91494;
  if ((((cVar2 != DAT_00031059) || (cVar2 = DAT_fff91514, cVar2 != DAT_00031061)) ||
      ((cVar2 = DAT_fff91594, cVar2 != DAT_00031069 ||
       ((cVar2 = DAT_fff91614, cVar2 != DAT_00031071 ||
        (cVar2 = DAT_fff91694, cVar2 != DAT_00031079)))))) ||
     ((cVar2 = DAT_fff92494, cVar2 != DAT_00031081 ||
      ((((cVar2 = DAT_fff92514, cVar2 != DAT_00031089 ||
         (cVar2 = DAT_fff92594, cVar2 != DAT_00031091)) ||
        (cVar2 = DAT_fff92614, cVar2 != DAT_00031099)) ||
       (cVar2 = DAT_fff92694, cVar2 != DAT_000310a1)))))) {
    iVar4 = 0x5a;
  }
  iVar3 = 0;
  cVar2 = DAT_fff91498;
  if ((((cVar2 != DAT_0003105a) || (cVar2 = DAT_fff91518, cVar2 != DAT_00031062)) ||
      ((((cVar2 = DAT_fff91598, cVar2 != DAT_0003106a ||
         ((cVar2 = DAT_fff91618, cVar2 != DAT_00031072 ||
          (cVar2 = DAT_fff91698, cVar2 != DAT_0003107a)))) ||
        (cVar2 = DAT_fff92498, cVar2 != DAT_00031082)) ||
       (((cVar2 = DAT_fff92518, cVar2 != (char)PTR_DAT_0003108a ||
         (cVar2 = DAT_fff92598, cVar2 != DAT_00031092)) ||
        (cVar2 = DAT_fff92618, cVar2 != (char)PTR_DAT_0003109a)))))) ||
     (cVar2 = DAT_fff92698, cVar2 != DAT_000310a2)) {
    iVar3 = 0x5a;
  }
  if (((iVar5 == 0x5a) || (iVar4 == 0x5a)) || (iVar3 == 0x5a)) {
    FUN_00060194();
    FUN_000603e4(iVar5,iVar4,iVar3);
    FUN_000602ac();
  }
  uVar6 = 0;
  do {
    if (((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x310a8u + (uint32_t)((short)uVar6 * 0x28) * 1u))))) != -1) {
      FUN_00060a6a(((undefined *)camry_host_ptr(0x310a8u)) + (short)uVar6 * 0x28);
    }
    iVar4 = (short)uVar6 * 0x28;
    if (((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x31170u + (uint32_t)(iVar4) * 1u))))) != -1) {
      FUN_00060a6a(((undefined *)camry_host_ptr(0x31170u)) + iVar4);
    }
    uVar6 = uVar6 + 1;
  } while (uVar6 < 5);
  return;
}



int FUN_00060630(uint param_1)

{
  uint uVar1;
  
  if (0x4f < (param_1 & 0xffff)) {
    return 0;
  }
  uVar1 = *(uint *)(((undefined *)camry_host_ptr(0xfeef80a0u)) + (param_1 & 0xffff) * 4);
  *(uint *)(((undefined *)camry_host_ptr(0xfeef80a0u)) + (param_1 & 0xffff) * 4) = uVar1 & 0xffff0000;
  return (uVar1 & 0x7ff8) << 1;
}



int FUN_000606da(uint param_1)

{
  uint uVar1;
  
  if (0x5f < (param_1 & 0xffff)) {
    return 0;
  }
  uVar1 = *(uint *)(((undefined *)camry_host_ptr(0xfeef88a0u)) + (param_1 & 0xffff) * 4);
  *(uint *)(((undefined *)camry_host_ptr(0xfeef88a0u)) + (param_1 & 0xffff) * 4) = uVar1 & 0xffff0000;
  return (uVar1 & 0x7ff8) << 1;
}



void FUN_00060766(void)

{
  int iVar1;
  uint uVar2;
  
  DM00CM = 0x200c;
  DAT_ffff8104 = 0x2018;
  DAT_ffff8108 = 0x200c;
  DAT_ffff810c = 0x2010;
  DAT_ffff8110 = 0x200c;
  DAT_ffff8114 = 0x2014;
  DAT_ffff8118 = 0x200c;
  DAT_ffff811c = 0x207c;
  DM10CM = 0x200c;
  DAT_ffff8124 = 0x2018;
  DAT_ffff8128 = 0x200c;
  DAT_ffff812c = 0x2010;
  DAT_ffff8130 = 0x200c;
  DAT_ffff8134 = 0x2014;
  DAT_ffff8138 = 0x200c;
  DAT_ffff813c = 0x207c;
  uVar2 = 0;
  do {
    iVar1 = uVar2 * 2;
    uVar2 = uVar2 + 1;
    *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe380cu)) + iVar1) = 0;
  } while (uVar2 < 0x10);
  return;
}



void FUN_000607fe(uint param_1)

{
  if ((param_1 & 0xff) < 0x10) {
    (*((undefined4 *)camry_host_ptr((uint32_t)((param_1 & 0xff) * 0x40 + -0x7be0)))) = 0;
  }
  return;
}



void FUN_0006080e(uint param_1)

{
  int iVar1;
  
  if ((param_1 & 0xff) < 0x10) {
    iVar1 = (param_1 & 0xff) * 0x40;
    (*((undefined4 *)camry_host_ptr((uint32_t)(iVar1 + -0x7bc8)))) = 3;
    (*((undefined4 *)camry_host_ptr((uint32_t)(iVar1 + -0x7bd4)))) = 0xb1;
    (*((undefined4 *)camry_host_ptr((uint32_t)(iVar1 + -0x7be0)))) = 1;
  }
  return;
}



/* Read u32 at FFFF8404+64*low8(channel). R6-scaled signed displacement, NOT GP-relative FEBE3C00.
   No local channel bound; physical descriptor-block identity remains separate. Zero-extend channel
   and load FFFF8404+channel*64. Descriptor base is FFFF8400; GP is not an operand. Physical
   acquisition freshness is not established. */

uint f33_read_transfer_descriptor_head(uchar channel)

{
  return (*((uint *)camry_host_ptr((uint32_t)((uint)channel * 0x40 + -0x7bfc))));
}



/* Return low16 of u32[FFFF8408+64*low8(channel)]. No<16 bounds gate here;62488 supplies ROM
   channels2/10. Distinct from60940 combined-count calculation. This SFR is an explicit native model
   boundary, not ordinary RAM. */

uint f33_read_transfer_primary_count_low(uchar channel)

{
  return (*((uint *)camry_host_ptr((uint32_t)((uint)channel * 0x40 + -0x7bf8)))) & 0xffff;
}



/* Channels<16 combine descriptor+08/+18 halfwords with low16 arithmetic; otherwise return0.
   BaseFFFF8400 is independent of GP. Ring consumers select six entries without per-offset modulo:
   counts2/4 produce zero tails. Count and low16 payload acknowledgments do not establish sample
   age. For channel<16 combine low/high descriptor halfwords with low16 arithmetic at
   FFFF8408+channel*64. Address and count arithmetic are instruction-verified; not a hardware
   completion model. Ring consumers select six offsets without modulo432; counts2/4 produce zero
   tails. No sample-age or completion claim. */

ushort f33_count_transfer_entries(uchar channel)

{
  uint uVar1;
  int iVar2;
  ushort uVar3;
  uint uVar4;
  uint uVar5;
  
  uVar3 = 0;
  if (channel < 0x10) {
    iVar2 = (uint)channel * 0x40;
    uVar4 = (*((uint *)camry_host_ptr((uint32_t)(iVar2 + -0x7be8))));
    uVar5 = (*((uint *)camry_host_ptr((uint32_t)(iVar2 + -0x7bf8))));
    uVar1 = uVar4 - (uVar4 >> 0x10);
    uVar3 = (ushort)uVar1;
    uVar5 = ((uVar5 >> 0x10) + (uVar1 & 0xffff)) - uVar5;
    if (uVar4 >> 0x10 <= (uVar5 & 0xffff)) {
      uVar3 = (short)uVar5 - (short)(uVar4 >> 0x10);
    }
  }
  return uVar3;
}



/* For channel<16 snapshot flags&30 atFFFF8424+40*channel, acknowledge at+2C, compute
   low16(total-remaining), save atFEBE380C+2*channel and subtract previous, adding total on wrap.
   Both flag bits select total/2 instead. Invalid channel returns0. Ordered SFR reads are a hardware
   boundary, not an atomic RAM sample. */

uint f33_read_dma_progress_delta(uchar channel)

{
  uint uVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  uint uVar7;
  
  uVar3 = (uint)channel;
  uVar4 = 0;
  if (uVar3 < 0x10) {
    iVar2 = uVar3 * 0x40;
    uVar6 = (*((uint *)camry_host_ptr((uint32_t)(iVar2 + -0x7bdc)))) & 0x30;
    (*((uint *)camry_host_ptr((uint32_t)(iVar2 + -0x7bd4)))) = uVar6;
    uVar7 = (uint)*(ushort *)(((undefined *)camry_host_ptr(0xfebe380cu)) + uVar3 * 2);
    uVar5 = (*((uint *)camry_host_ptr((uint32_t)(iVar2 + -0x7be8)))) & 0xffff;
    uVar1 = uVar5 - (*((int *)camry_host_ptr((uint32_t)(iVar2 + -0x7bf8))));
    uVar4 = uVar1 & 0xffff;
    *(ushort *)(((undefined *)camry_host_ptr(0xfebe380cu)) + uVar3 * 2) = (ushort)uVar1;
    if (uVar4 < uVar7) {
      uVar4 = uVar5 + uVar4;
    }
    uVar4 = uVar4 - uVar7;
    if ((uVar6 >> 5 != 0) && ((uVar6 >> 4 & 1) != 0)) {
      uVar4 = uVar5 >> 1;
    }
  }
  return uVar4;
}



void FUN_00060a6a(byte *param_1)

{
  int iVar1;
  byte bVar2;
  undefined2 uVar3;
  uint *puVar4;
  
  if (*param_1 < 0x10) {
    iVar1 = (uint)*param_1 * 0x40;
    uVar3 = *(undefined2 *)(param_1 + 0x14);
    (*((undefined4 *)camry_host_ptr((uint32_t)(iVar1 + -0x7bf0)))) = *(undefined4 *)(param_1 + 0x18);
    (*((undefined4 *)camry_host_ptr((uint32_t)(iVar1 + -0x7bec)))) = *(undefined4 *)(param_1 + 0x1c);
    (*((uint *)camry_host_ptr((uint32_t)(iVar1 + -0x7be8)))) = CONCAT22(*(undefined2 *)(param_1 + 0x16),uVar3);
    bVar2 = param_1[3];
    if ((*((uint *)camry_host_ptr((uint32_t)(iVar1 + -0x7bd0)))) != (uint)bVar2) {
      puVar4 = ((uint *)camry_host_ptr((uint32_t)(iVar1 + -0x7bd0)));
      *puVar4 = *puVar4 & 0xfe;
      *puVar4 = (uint)bVar2;
    }
  }
  return;
}



void FUN_00060aa8(void)

{
  uint uVar1;
  uint uVar2;
  int iVar3;
  
  uVar2 = 0;
  do {
    uVar1 = 0;
    do {
      iVar3 = (short)((short)uVar1 + (short)(uVar2 << 1)) * 0x18;
      uVar1 = uVar1 + 1;
      *(undefined4 *)(((undefined *)camry_host_ptr(0xfeef90f8u)) + iVar3) = 0;
      *(undefined4 *)(((undefined *)camry_host_ptr(0xfeef90fcu)) + iVar3) = 0;
      *(undefined4 *)(((undefined *)camry_host_ptr(0xfeef9100u)) + iVar3) = 0;
      *(undefined4 *)(((undefined *)camry_host_ptr(0xfeef9104u)) + iVar3) = 0;
      *(undefined4 *)(((undefined *)camry_host_ptr(0xfeef9108u)) + iVar3) = 0;
      *(undefined4 *)(((undefined *)camry_host_ptr(0xfeef910cu)) + iVar3) = 0x800800;
    } while (uVar1 < 2);
    uVar2 = uVar2 + 1;
  } while (uVar2 < 2);
  return;
}



void FUN_00060ae0(uint param_1,int param_2)

{
  byte bVar1;
  ushort uVar2;
  
  if ((param_1 & 0xff) < 2) {
    bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x3125au + (uint32_t)(param_1 & 0xff) * 1u))));
    (*((int *)camry_host_ptr((uint32_t)((uint)bVar1 * 0x1000 + -0x1fafe4)))) = param_2;
    for (uVar2 = 0;
        ((*((int *)camry_host_ptr((uint32_t)((uint)bVar1 * 0x1000 + -0x1fafdc)))) != param_2 && (uVar2 < DAT_00031258));
        uVar2 = uVar2 + 1) {
      f33_spin_wait(1);
    }
  }
  return;
}



void FUN_00060b26(uint param_1)

{
  int iVar1;
  int iVar2;
  
  param_1 = param_1 & 0xff;
  if (param_1 < 2) {
    iVar1 = param_1 * 4;
    iVar2 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x3125au + (uint32_t)(param_1) * 1u)))) * 0x1000;
    (*((undefined4 *)camry_host_ptr((uint32_t)(iVar2 + -0x1fafec)))) = *(undefined4 *)(((undefined *)camry_host_ptr(0x31248u)) + iVar1);
    (*((undefined4 *)camry_host_ptr((uint32_t)(iVar2 + -0x1fb000)))) = *(undefined4 *)(((undefined *)camry_host_ptr(0x31238u)) + iVar1);
    (*((undefined4 *)camry_host_ptr((uint32_t)(iVar2 + -0x1faff0)))) = *(undefined4 *)(((undefined *)camry_host_ptr(0x31240u)) + iVar1);
    (*((undefined4 *)camry_host_ptr((uint32_t)(iVar2 + -0x1fafe8)))) = 1;
  }
  return;
}



void FUN_00060b76(ushort param_1)

{
  undefined1 uVar1;
  int iVar2;
  
  if ((param_1 & 0xff) < 2) {
    iVar2 = (short)(param_1 & 0xff) * 0x28;
    uVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x3125cu + (uint32_t)(iVar2) * 1u))));
    FUN_000607fe(uVar1);
    FUN_0006082c(((undefined *)camry_host_ptr(0x3125cu)) + iVar2);
    FUN_0006080e(uVar1);
  }
  return;
}



void FUN_00060ba8(ushort param_1)

{
  undefined1 uVar1;
  int iVar2;
  
  if ((param_1 & 0xff) < 2) {
    iVar2 = (short)(param_1 & 0xff) * 0x28;
    uVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x312acu + (uint32_t)(iVar2) * 1u))));
    FUN_000607fe(uVar1);
    FUN_0006082c(((undefined *)camry_host_ptr(0x312acu)) + iVar2);
    FUN_0006080e(uVar1);
  }
  return;
}



/* Sequential initializer chain: 5 unconditional calls and no other statements; shape-verified. The
   called sequence is the function's entire behavior; chain family members differ in callee sets. */

void f33_run_init_chain_60bda(undefined1 param_1)

{
  FUN_00060ae0(param_1,1);
  FUN_00060b26(param_1);
  FUN_00060ae0(param_1,5);
  FUN_00060b76(param_1);
  FUN_00060ba8(param_1);
  return;
}



void FUN_00060c06(void)

{
  uint uVar1;
  
  FUN_00060aa8();
  uVar1 = 0;
  do {
    f33_run_init_chain_60bda(uVar1);
    uVar1 = uVar1 + 1;
  } while (uVar1 < 2);
  return;
}



void FUN_00060c20(void)

{
  int iVar1;
  uint uVar2;
  
  uVar2 = 0;
  do {
    iVar1 = (short)uVar2 * 0x28;
    (*((undefined4 *)camry_host_ptr((uint32_t)((uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x3125au + (uint32_t)(uVar2) * 1u)))) * 0x1000 + -0x1fafe8)))) = 1;
    FUN_00060a6a(((undefined *)camry_host_ptr(0x3125cu)) + iVar1);
    FUN_00060a6a(((undefined *)camry_host_ptr(0x312acu)) + iVar1);
    uVar2 = uVar2 + 1;
  } while (uVar2 < 2);
  return;
}



void FUN_00060c60(uint param_1,ushort param_2,ushort *param_3)

{
  uint uVar1;
  uint uVar2;
  int iVar3;
  undefined4 uVar4;
  
  param_1 = param_1 & 0xff;
  if (((param_2 & 0xff) < 2) && (param_1 < 2)) {
    iVar3 = (short)((param_2 & 0xff) + (short)param_1 * 2) * 0x18;
    uVar2 = (*((uint *)camry_host_ptr((uint32_t)((uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x3125au + (uint32_t)(param_1) * 1u)))) * 0x1000 + -0x1fafd8)))) & 0x7fe;
    (*((uint *)camry_host_ptr((uint32_t)((uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x3125au + (uint32_t)(param_1) * 1u)))) * 0x1000 + -0x1fafd4)))) = uVar2;
    uVar1 = *(uint *)(((undefined *)camry_host_ptr(0xfeef910cu)) + iVar3);
    *(uint *)(((undefined *)camry_host_ptr(0xfeef910cu)) + iVar3) = uVar1 & 0xbfffffff;
    uVar4 = *(undefined4 *)(((undefined *)camry_host_ptr(0xfeef90fcu)) + iVar3);
    *param_3 = (ushort)uVar2 | ((ushort)(uVar1 >> 0x10) & 0x4000) >> 0xe;
    param_3[1] = (ushort)uVar4 & 0xf;
    param_3[2] = (ushort)((uVar1 & 0xfff000) >> 0xc);
    param_3[3] = (ushort)uVar1 & 0xfff;
  }
  return;
}



void FUN_00060cd4(void)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  
  uVar3 = 0;
  do {
    iVar1 = uVar3 * 0x10;
    iVar2 = uVar3 * 0x40;
    uVar3 = uVar3 + 1;
    (*((undefined4 *)camry_host_ptr((uint32_t)(iVar2 + -0x3ebfe8)))) = *(undefined4 *)(((undefined *)camry_host_ptr(0x31394u)) + iVar1);
    (*((undefined4 *)camry_host_ptr((uint32_t)(iVar2 + -0x3ebfd8)))) = *(undefined4 *)(((undefined *)camry_host_ptr(0x31398u)) + iVar1);
    (*((undefined4 *)camry_host_ptr((uint32_t)(iVar2 + -0x3ebfec)))) = *(undefined4 *)(((undefined *)camry_host_ptr(0x3139cu)) + iVar1);
    (*((undefined4 *)camry_host_ptr((uint32_t)(iVar2 + -0x3ebfc4)))) = *(undefined4 *)(((undefined *)camry_host_ptr(0x313a0u)) + iVar1);
  } while (uVar3 < 6);
  return;
}



void FUN_00060d0e(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  
  FUN_00060cd4();
  iVar5 = 0;
  do {
    iVar4 = iVar5 * 8;
    iVar3 = iVar5 + 1;
    iVar2 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x31311u + (uint32_t)(iVar4) * 1u)))) * 4 + (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x31310u + (uint32_t)(iVar4) * 1u)))) * 0x40;
    iVar1 = iVar5 + -0xf;
    (*((uint *)camry_host_ptr((uint32_t)(iVar2 + -0x3ee000)))) =
         *(uint *)(((undefined *)camry_host_ptr(0x3130cu)) + iVar4) | (*((uint *)camry_host_ptr((uint32_t)(iVar2 + -0x3ee000)))) & 0xfffeff88;
    iVar5 = iVar3;
  } while (((iVar1 < 0) || (iVar3 < 0)));
  return;
}



void FUN_00060d52(uint param_1)

{
  uint uVar1;
  
  param_1 = param_1 & 0xff;
  if (param_1 < 2) {
    for (uVar1 = 0; uVar1 < (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x31411u + (uint32_t)((short)param_1 * 0x50) * 1u)))); uVar1 = uVar1 + 1 & 0xff)
    {
      (*((undefined2 *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x313fcu + (uint32_t)(param_1) * 4u)))) + uVar1 * 2)))) = 0;
    }
  }
  return;
}



void FUN_00060d8c(ushort param_1)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  if ((param_1 & 0xff) < 2) {
    iVar1 = (int)(short)(param_1 & 0xff);
    iVar3 = iVar1 * 0x50;
    iVar2 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x3140cu + (uint32_t)(iVar3) * 1u)))) * 0x2000;
    (*((undefined1 *)camry_host_ptr((uint32_t)(iVar2 + -0x280000)))) = 0;
    *(undefined **)(iVar2 + -0x27fff0) = ((void *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x31424u + (uint32_t)(iVar1 * 0x14) * 4u)))))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(iVar2 + -0x27ffec)))) = *(undefined2 *)(((undefined *)camry_host_ptr(0x31428u)) + iVar3);
    (*((undefined2 *)camry_host_ptr((uint32_t)(iVar2 + -0x27efc0)))) = *(undefined2 *)(((undefined *)camry_host_ptr(0x3142cu)) + iVar3);
    *(undefined **)(iVar2 + -0x27efbc) = ((void *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x31434u + (uint32_t)(iVar1 * 0x14) * 4u)))))));
    (*((undefined4 *)camry_host_ptr((uint32_t)(iVar2 + -0x27efb8)))) = *(undefined4 *)(((undefined *)camry_host_ptr(0x31438u)) + iVar3);
    (*((undefined4 *)camry_host_ptr((uint32_t)(iVar2 + -0x27efb4)))) = *(undefined4 *)(((undefined *)camry_host_ptr(0x3143cu)) + iVar3);
    (*((undefined4 *)camry_host_ptr((uint32_t)(iVar2 + -0x27efb0)))) = *(undefined4 *)(((undefined *)camry_host_ptr(0x31440u)) + iVar3);
    (*((undefined4 *)camry_host_ptr((uint32_t)(iVar2 + -0x27efac)))) = *(undefined4 *)(((undefined *)camry_host_ptr(0x31444u)) + iVar3);
    (*((undefined4 *)camry_host_ptr((uint32_t)(iVar2 + -0x27efa8)))) = *(undefined4 *)(((undefined *)camry_host_ptr(0x31448u)) + iVar3);
    (*((undefined4 *)camry_host_ptr((uint32_t)(iVar2 + -0x27efa4)))) = *(undefined4 *)(((undefined *)camry_host_ptr(0x3144cu)) + iVar3);
    (*((undefined4 *)camry_host_ptr((uint32_t)(iVar2 + -0x27efa0)))) = *(undefined4 *)(((undefined *)camry_host_ptr(0x31450u)) + iVar3);
    (*((undefined2 *)camry_host_ptr((uint32_t)(iVar2 + -0x27ef98)))) = *(undefined2 *)(((undefined *)camry_host_ptr(0x31454u)) + iVar3);
    (*((undefined2 *)camry_host_ptr((uint32_t)(iVar2 + -0x27ef94)))) = *(undefined2 *)(((undefined *)camry_host_ptr(0x31456u)) + iVar3);
    (*((undefined2 *)camry_host_ptr((uint32_t)(iVar2 + -0x27ef90)))) = *(undefined2 *)(((undefined *)camry_host_ptr(0x31458u)) + iVar3);
    (*((undefined2 *)camry_host_ptr((uint32_t)(iVar2 + -0x27ef8c)))) = *(undefined2 *)(((undefined *)camry_host_ptr(0x3145au)) + iVar3);
    (*((undefined2 *)camry_host_ptr((uint32_t)(iVar2 + -0x27fff8)))) = *(undefined2 *)(((undefined *)camry_host_ptr(0x3142au)) + iVar3);
    (*((undefined *)camry_host_ptr((uint32_t)(iVar2 + -0x280000)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x31420u + (uint32_t)(iVar3) * 1u))));
  }
  return;
}



void FUN_00060e3e(void)

{
  uint uVar1;
  
  uVar1 = 0;
  do {
    FUN_00060d52(uVar1);
    FUN_00060d8c(uVar1);
    uVar1 = uVar1 + 1;
  } while (uVar1 < 2);
  return;
}



void FUN_00060e5a(void)

{
  undefined1 uVar1;
  int iVar2;
  short sVar3;
  uint uVar4;
  
  uVar4 = 0;
  do {
    sVar3 = (short)uVar4;
    iVar2 = sVar3 * 0x50;
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x31414u + (uint32_t)(iVar2) * 1u)))) == '\0') {
      uVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x314acu + (uint32_t)(sVar3 * 0x28) * 1u))));
      FUN_000607fe(uVar1);
      FUN_0006082c(((undefined *)camry_host_ptr(0x314acu)) + sVar3 * 0x28);
      FUN_0006080e(uVar1);
    }
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x31415u + (uint32_t)(iVar2) * 1u)))) == '\0') {
      uVar1 = (*((undefined1 *)camry_host_ptr((uint32_t)(&PTR_DAT_000314fc + sVar3 * 10))));
      FUN_000607fe(uVar1);
      FUN_0006082c(&PTR_DAT_000314fc + sVar3 * 10);
      FUN_0006080e(uVar1);
    }
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x31416u + (uint32_t)(iVar2) * 1u)))) == '\0') {
      uVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x3154cu + (uint32_t)(sVar3 * 0x28) * 1u))));
      FUN_000607fe(uVar1);
      FUN_0006082c(((undefined *)camry_host_ptr(0x3154cu)) + sVar3 * 0x28);
      FUN_0006080e(uVar1);
    }
    uVar4 = uVar4 + 1;
  } while (uVar4 < 2);
  return;
}



undefined4 FUN_00060efa(ushort param_1,int param_2)

{
  int iVar1;
  byte bVar2;
  byte bVar3;
  uint uVar4;
  int iVar5;
  ushort uVar6;
  uint uVar7;
  int iVar8;
  
  if ((param_1 & 0xff) < 2) {
    iVar8 = (short)(param_1 & 0xff) * 0x50;
    bVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x3140eu + (uint32_t)(iVar8) * 1u))));
    bVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x3140fu + (uint32_t)(iVar8) * 1u))));
    iVar1 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x3140cu + (uint32_t)(iVar8) * 1u)))) * 0x2000;
    if ((((*((uint *)camry_host_ptr((uint32_t)(iVar1 + -0x27fffc)))) >> 7 & 1) == 0) && (bVar2 != 0)) {
      (*((undefined2 *)camry_host_ptr((uint32_t)(iVar1 + -0x27fff8)))) = 0x100;
      for (uVar6 = 0; uVar6 < bVar3; uVar6 = uVar6 + 1 & 0xff) {
        for (uVar7 = 0; iVar5 = bVar2 - 1,
            uVar4 = (uint)(*((ushort *)camry_host_ptr((uint32_t)(((int)(short)(ushort)bVar2 * (int)(short)uVar6 + uVar7) * 2 + param_2)))),
            (int)(uVar7 - iVar5) < 0 != (iVar5 < 0 && iVar5 < 0 == (int)(uVar7 - iVar5) < 0);
            uVar7 = uVar7 + 1 & 0xff) {
          (*((uint *)camry_host_ptr((uint32_t)(iVar1 + -0x27eff8)))) = uVar4 | *(uint *)(((undefined *)camry_host_ptr(0x31418u)) + iVar8) & 0xffff0000;
        }
        (*((uint *)camry_host_ptr((uint32_t)(iVar1 + -0x27eff8)))) = uVar4 | *(uint *)(((undefined *)camry_host_ptr(0x3141cu)) + iVar8) & 0xffff0000;
      }
      return 0;
    }
  }
  return 0x5a;
}



undefined4 FUN_00060f7c(ushort param_1,uint param_2)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  
  if ((param_1 & 0xff) < 2) {
    iVar3 = (short)(param_1 & 0xff) * 0x50;
    uVar2 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x31410u + (uint32_t)(iVar3) * 1u)))) - (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x3140eu + (uint32_t)(iVar3) * 1u))));
    iVar1 = (param_2 & 0xff) - uVar2;
    if (iVar1 < 0 != ((int)uVar2 < 0 && (int)uVar2 < 0 == iVar1 < 0) || (param_2 & 0xff) == uVar2) {
      (*((uint *)camry_host_ptr((uint32_t)((uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x3140cu + (uint32_t)(iVar3) * 1u)))) * 0x2000 + -0x27effc)))) =
           *(uint *)(((undefined *)camry_host_ptr(0x31430u)) + iVar3) | param_2 & 0x3f;
      return 0;
    }
  }
  return 0x5a;
}



/* Channel<2 and offset<=configured_capacity-count: copy countu16 words from ROM313FC[channel] FIFO;
   caller uses capacity20 and count5. No wrap, clear, cursor advance, status check or return
   verdict; rejected bounds leave destination unchanged. Native evidence covers explicit software
   continuations and a synthetic post-getter publication join, not descriptor acquisition or the
   intact fast task. */

void f33_copy_serial_fifo_words(uchar channel,ushort *output,uchar offset,uchar count)

{
  uint uVar1;
  uint uVar2;
  undefined *puVar3;
  
  uVar2 = (uint)offset;
  if (channel < 2) {
    puVar3 = ((void *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x313fcu + (uint32_t)(channel) * 4u)))))));
    uVar1 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x31411u + (uint32_t)((short)(ushort)channel * 0x50) * 1u)))) - (uint)count;
    if ((int)(uVar2 - uVar1) < 0 != ((int)uVar1 < 0 && (int)uVar1 < 0 == (int)(uVar2 - uVar1) < 0)
        || uVar2 == uVar1) {
      for (uVar1 = 0; uVar1 < count; uVar1 = uVar1 + 1 & 0xff) {
        output[uVar1] = *(ushort *)(puVar3 + (uVar2 + uVar1) * 2);
      }
    }
  }
  return;
}



/* Physical channel<2: ROM3140C+50*channel selects controller block. Snapshot status bits8/7/3 and
   three7-bit counts into six bytes, then acknowledge with halfword(ack&100)|(status&8).62576 uses
   byte2==0 and byte3==10; other status bytes do not gate decoding there. This is register contract,
   not current sample age. */

void f33_read_serial_controller_status
               (uchar channel,ushort acknowledgment,F33SerialControllerStatus *output)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  uint uVar4;
  
  if (channel < 2) {
    iVar1 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x3140cu + (uint32_t)((short)(ushort)channel * 0x50) * 1u)))) * 0x2000;
    uVar4 = (*((uint *)camry_host_ptr((uint32_t)(iVar1 + -0x27fffc))));
    uVar2 = (*((undefined4 *)camry_host_ptr((uint32_t)(iVar1 + -0x27effc))));
    uVar3 = (*((undefined4 *)camry_host_ptr((uint32_t)(iVar1 + -0x27efe8))));
    output->status_bit8 = (byte)(uVar4 >> 8) & 1;
    output->status_bit7 = (uchar)((uVar4 & 0x80) >> 7);
    output->status_bit3 = (uchar)((uVar4 & 8) >> 3);
    output->count0_7bit = (byte)uVar2 & 0x7f;
    output->count1_7bit = (byte)((uint)uVar3 >> 0x10) & 0x7f;
    output->count2_7bit = (byte)uVar3 & 0x7f;
    (*((ushort *)camry_host_ptr((uint32_t)(iVar1 + -0x27fff8)))) = acknowledgment & 0x100 | (ushort)(uVar4 & 8);
  }
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_610bc(void)

{
  return;
}



/* Single constant publisher: DAT_ffd50020 = 0x22; Shape-classified from the canonical corpus; the
   target cell is not yet named, so the written state's meaning is unknown. */

void FUN_000611ee(void)

{
  DAT_ffd50020 = 0x22;
  return;
}



/* 389E5A admits local four-halfword MMIO read, CRC and6000 header check. At25 failed admitted
   updates latch3840; healthy publication does not clear an already latched fault. Hardware packet
   availability remains an explicit boundary. Local four-halfword MMIO packet, seven-byte CRC
   and6000 header admission;25 failed admitted updates latch3840, healthy publication does not clear
   latch. Real hardware availability unexecuted. */

void f33_update_local_status_packet(void)

{
  ushort uVar1;
  uint32_t puVar2;
  int iVar3;
  uint uVar4;
  char cVar5;
  char cVar6;
  
  puVar2 = 0xfebeb800u;
  if (DAT_febe389e == 'Z') {
    iVar3 = camry_host_addr(FUN_0006131c(((undefined *)camry_host_ptr(0xfebe382cu))));
    cVar6 = 'D';
    if (iVar3 == 0) {
      uVar4 = FUN_000611fa(((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x7fd4))));
      if ((byte)(*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x7fce)))) == uVar4) {
        uVar1 = (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x7fd4)))) & 0xe000;
        if (uVar1 == 0x6000) {
          (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x7fc8)))) = (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x7fd4))));
          (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x7fc2)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x7fce))));
          cVar6 = '\0';
          (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x7fc6)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x7fd2))));
          (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x7fc4)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x7fd0))));
        }
        else {
          cVar6 = '3';
          if (uVar1 == 0x8000) {
            cVar6 = '\"';
          }
        }
      }
      else {
        cVar6 = '\x11';
      }
    }
    cVar5 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x7fc0)))));
    uVar1 = (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x7fcc))));
    if (cVar5 != 'Z') {
      if (cVar6 == '\0') {
        uVar1 = 0;
        cVar5 = '\0';
      }
      else if ((DAT_000315c8 <= uVar1) || (uVar1 = uVar1 + 1, DAT_000315c8 <= uVar1)) {
        cVar5 = 'Z';
      }
    }
    (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x7fcc)))) = uVar1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x7fc0))))) = cVar5;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x7fca))))) = cVar6;
  }
  return;
}



byte FUN_000614b0(void)

{
  return (DAT_febe383e >> 0xd & 1) != 0 | ((DAT_febe383e >> 0xe & 1) != 0) << 1 |
         ((short)DAT_febe383e < 0) << 2;
}



void FUN_000614d4(void)

{
  int iVar1;
  undefined8 uVar2;
  int iVar3;
  uint uVar4;
  byte bVar5;
  undefined2 local_14;
  undefined2 uStack_12;
  undefined2 uStack_10;
  undefined2 uStack_e;
  
  uVar2 = 0xfebeb800;
  bVar5 = 0;
  do {
    iVar3 = camry_host_addr(FUN_0006131c(&local_14));
    f33_spin_wait(1);
    iVar1 = (int)uVar2;
    if (iVar3 == 0) {
      uVar4 = FUN_000611fa(&local_14);
      if ((byte)uStack_e != uVar4) {
        return;
      }
      (*((undefined2 *)camry_host_ptr((uint32_t)(iVar1 + -0x7fc8)))) = local_14;
      (*((undefined2 *)camry_host_ptr((uint32_t)(iVar1 + -0x7fc6)))) = uStack_12;
      (*((undefined2 *)camry_host_ptr((uint32_t)(iVar1 + -0x7fc2)))) = uStack_e;
      (*((undefined2 *)camry_host_ptr((uint32_t)(iVar1 + -0x7fc4)))) = uStack_10;
      return;
    }
    bVar5 = bVar5 + 1;
  } while (bVar5 < 0xc9);
  return;
}



void FUN_00061526(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe3841 = 0;
  DAT_febe3842 = 0;
  DAT_febe3843 = 0;
  DAT_febe3844 = 0;
  f33_publish_redundant_u8('\0',((undefined *)camry_host_ptr(0xfebe3845u)),((undefined *)camry_host_ptr(0xfebe8de0u)),((undefined *)camry_host_ptr(0xfebe8df4u)));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x7fba))))) = 0;
  return;
}



void FUN_00061554(void)

{
  if (DAT_febe3842 < DAT_000315cb) {
    DAT_febe388e = 0xff;
    DAT_febe3842 = DAT_febe3842 + 1;
  }
  else {
    DAT_febe3887 = 0;
    DAT_febe3886 = 0;
    if (DAT_febe3843 < DAT_000315cc) {
      DAT_febe3843 = DAT_febe3843 + 1;
    }
    else {
      if (DAT_000315cd <= DAT_febe3844) {
        FUN_00062be8();
                    /* WARNING: Subroutine does not return */
        f33_enter_terminal_hardware_sequence();
      }
      DAT_febe388e = 0;
      DAT_febe3844 = DAT_febe3844 + 1;
    }
  }
  return;
}



void FUN_000615be(void)

{
  int iVar1;
  uchar uStack_5;
  
  iVar1 = f33_vote_redundant_u8(((undefined *)camry_host_ptr(0xfebe3845u)),((undefined *)camry_host_ptr(0xfebe8de0u)),((undefined *)camry_host_ptr(0xfebe8df4u)),&uStack_5);
  if (iVar1 == -0xd) {
    uStack_5 = '\0';
  }
  if (uStack_5 == 'Z') {
    FUN_00061554();
  }
  return;
}



/* Count published3838.bit10; exact BYTE315CA==20 latches3846. Removing bit resets byte counter, not
   latch;61526 initializes it. Published3838.bit10 counts against byte315CA=20 and latches3846.
   Removing bit resets byte counter but not latch; initialization is separate. */

void f33_update_local_status_bit_latch(void)

{
  char cVar1;
  
  if (DAT_febe389e == 'Z') {
    cVar1 = '\0';
    if ((DAT_febe3839 & 4) != 0) {
      cVar1 = 'Z';
    }
    if (cVar1 == '\0') {
      DAT_febe3841 = 0;
    }
    else if ((DAT_000315ca <= DAT_febe3841) ||
            (DAT_febe3841 = DAT_febe3841 + 1, DAT_000315ca <= DAT_febe3841)) {
      DAT_febe3846 = 0x5a;
    }
  }
  FUN_000615be();
  return;
}



void FUN_0006163e(void)

{
  f33_publish_redundant_u8('Z',((undefined *)camry_host_ptr(0xfebe3845u)),((undefined *)camry_host_ptr(0xfebe8de0u)),((undefined *)camry_host_ptr(0xfebe8df4u)));
  return;
}



/* Paired constant publisher: DAT_febe3847 = 0; and DAT_febe3848 = 0;; shape-classified from the
   canonical corpus. Target cells not yet named. */

void FUN_0006165a(void)

{
  DAT_febe3847 = 0;
  DAT_febe3848 = 0;
  return;
}



void FUN_00061664(void)

{
  int iVar1;
  char cVar2;
  
  iVar1 = 0;
  if ((DAT_febe3839 & 4) != 0) {
    iVar1 = 0x5a;
  }
  if (iVar1 == 0) {
    cVar2 = '\0';
    if ((DAT_febe383e >> 8 & 1) != 0) {
      cVar2 = 'Z';
    }
    if (cVar2 != DAT_febe3847) {
      DAT_febe3848 = ~DAT_febe3848;
    }
    if ((DAT_febe383e >> 0xc & 1) == 0) {
      DAT_febe385d = 0xff;
    }
    else {
      DAT_febe385d = 0;
    }
    if ((DAT_febe383e >> 0xb & 1) == 0) {
      DAT_febe385e = 0xff;
    }
    else {
      DAT_febe385e = 0;
    }
    if ((DAT_febe383e >> 10 & 1) == 0) {
      DAT_febe385f = 0xff;
    }
    else {
      DAT_febe385f = 0;
    }
    DAT_febe3847 = cVar2;
    DAT_febe385c = DAT_febe3848;
    if ((DAT_febe383e >> 9 & 1) == 0) {
      DAT_febe3860 = 0xff;
    }
    else {
      DAT_febe3860 = 0;
    }
  }
  else {
    DAT_febe385d = 0xff;
    DAT_febe385e = 0xff;
    DAT_febe385f = 0xff;
    DAT_febe3860 = 0xff;
    DAT_febe385c = 0;
    FUN_0006165a();
  }
  return;
}



void FUN_000616fc(void)

{
  uint uVar1;
  uint32_t puVar2;
  ushort uVar3;
  
  puVar2 = 0xfebeb800u;
  uVar1 = 0;
  do {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe3854u + (uint32_t)(uVar1) * 1u)))) = 0;
    uVar1 = uVar1 + 1;
  } while (uVar1 < 0x40);
  DAT_febe384a = 0x8000;
  DAT_febe384c = 0;
  DAT_febe384e = 0x5098;
  DAT_febe3850 = 0x1e00;
  uVar3 = FUN_000611fa(((undefined *)camry_host_ptr(0xfebe384au)));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x7f62))))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x7fae)))) = 0;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x7fb0)))) = (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x7fb0)))) & 0xff00 | uVar3;
  return;
}



void FUN_0006174a(void)

{
  byte *pbVar1;
  undefined1 uVar2;
  uint uVar3;
  uint32_t puVar4;
  ushort uVar5;
  int iVar6;
  uint uVar7;
  uint uVar8;
  
  puVar4 = 0xfebeb800u;
  DAT_febe384a = 0x8000;
  DAT_febe384c = 0;
  DAT_febe384e = 0x98;
  DAT_febe3850 = 0;
  uVar3 = 8;
  do {
    pbVar1 = ((undefined *)camry_host_ptr(0xfebe3854u)) + uVar3;
    uVar7 = uVar3 & 0xf;
    uVar8 = uVar3 >> 4;
    uVar3 = uVar3 + 1;
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe3850u + (uint32_t)(-uVar8) * 2u)))) = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe3850u + (uint32_t)(-uVar8) * 2u)))) | (ushort)((*pbVar1 & 1) << uVar7);
  } while (uVar3 < 0x3d);
  if (DAT_00031e80 == 'Z') {
    DAT_febe384a = DAT_00031e78 & (DAT_febe384a | DAT_00031e70);
    DAT_febe384c = DAT_00031e7a & (DAT_febe384c | DAT_00031e72);
    DAT_febe384e = DAT_00031e7c & (DAT_febe384e | DAT_00031e74);
    DAT_febe3850 = DAT_00031e7e & (DAT_febe3850 | DAT_00031e76);
  }
  uVar5 = FUN_000611fa(((undefined *)camry_host_ptr(0xfebe384au)));
  (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + -0x7fb0)))) = (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + -0x7fb0)))) & 0xff00 | uVar5;
  iVar6 = FUN_00061372(((undefined *)camry_host_ptr((uint32_t)(puVar4 + -0x7fb6))));
  uVar2 = 0;
  if (iVar6 == 0) {
    uVar2 = 0x5a;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x7f62))))) = uVar2;
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + -0x7fae)))) = (short)iVar6;
  return;
}



undefined4 FUN_00061874(uint param_1)

{
  byte bVar1;
  undefined4 uVar2;
  uint uVar3;
  
  CKSC3C = 4;
  uVar3 = CKSC3C;
  __synchronize();
  uVar3 = CKSC3S;
  bVar1 = 0;
  while ((uVar3 != 4 && (bVar1 < 100))) {
    uVar3 = CKSC3S;
    bVar1 = bVar1 + 1;
    __synchronize();
  }
  uVar3 = CLKD3STAT;
  bVar1 = 0;
  while (((uVar3 & 2) == 0 && (bVar1 < 100))) {
    bVar1 = bVar1 + 1;
    __synchronize();
    uVar3 = CLKD3STAT;
  }
  if ((uVar3 & 2) == 2) {
    CLKD3DIV = param_1;
    uVar3 = CLKD3DIV;
    __synchronize();
  }
  uVar3 = CLKD3STAT;
  bVar1 = 0;
  while (((uVar3 & 2) == 0 && (bVar1 < 100))) {
    bVar1 = bVar1 + 1;
    __synchronize();
    uVar3 = CLKD3STAT;
  }
  uVar2 = 0x11;
  if (((uVar3 & 2) == 2) && (uVar3 = CLKD3DIV, uVar3 == param_1)) {
    uVar2 = 0;
  }
  return uVar2;
}



undefined4 FUN_00061906(char param_1)

{
  undefined4 uVar1;
  
  if (param_1 == -1) {
    uVar1 = 0;
  }
  else if (param_1 == '\x01') {
    uVar1 = 0x50;
  }
  else if (param_1 == '\x02') {
    uVar1 = 0x3d;
  }
  else {
    if (param_1 != '\0') {
      return 0x11;
    }
    uVar1 = 0x73;
  }
  uVar1 = FUN_00061874(uVar1);
  return uVar1;
}



void FUN_000619c0(void)

{
  uint uVar1;
  
  uVar1 = CLKD3DIV;
  if (uVar1 != 0x50) {
    uVar1 = f33_priority_mask_enter(0xffff);
    FUN_00061874(0x50);
    f33_priority_mask_restore(uVar1);
  }
  return;
}



void FUN_000619ec(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  
  iVar5 = 0;
  do {
    iVar2 = iVar5 + 1;
    iVar3 = (uint)(ushort)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x315e8u + (uint32_t)((short)iVar5 * 0xe) * 2u)))) << 0x10;
    iVar4 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x315dbu + (uint32_t)((short)iVar5 * 0x1c) * 1u)))) * 0x40;
    iVar1 = iVar5 + -1;
    (*((int *)camry_host_ptr((uint32_t)(iVar4 + -0x3efffc)))) = iVar3;
    (*((int *)camry_host_ptr((uint32_t)(iVar4 + -0x3effdc)))) = iVar3;
    (*((int *)camry_host_ptr((uint32_t)(iVar4 + -0x3effe0)))) = iVar3;
    iVar5 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  return;
}



void FUN_00061a1c(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  iVar4 = 0;
  do {
    iVar2 = iVar4 + 1;
    iVar3 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x315d0u + (uint32_t)(iVar4) * 1u)))) * 0x1000;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffe70034u + (uint32_t)(iVar3) * 1u)))) = 1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffe70208u + (uint32_t)(iVar3) * 1u)))) = 1;
    *(undefined2 *)(((undefined *)camry_host_ptr(0xffe7020cu)) + iVar3) = 0;
    *(undefined4 *)(((undefined *)camry_host_ptr(0xffe70078u)) + iVar3) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffe70004u + (uint32_t)(iVar3) * 1u)))) = 0;
    *(undefined4 *)(((undefined *)camry_host_ptr(0xffe7007cu)) + iVar3) = 0x80;
    *(undefined2 *)(((undefined *)camry_host_ptr(0xffe70008u)) + iVar3) = 0x808;
    iVar1 = iVar4 + -1;
    *(undefined2 *)(((undefined *)camry_host_ptr(0xffe7000cu)) + iVar3) = 0x810;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffe70200u + (uint32_t)(iVar3) * 1u)))) = 0;
    *(undefined2 *)(((undefined *)camry_host_ptr(0xffe70000u)) + iVar3) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffe70200u + (uint32_t)(iVar3) * 1u)))) = 0x7e;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffe70204u + (uint32_t)(iVar3) * 1u)))) = 0;
    *(undefined4 *)(((undefined *)camry_host_ptr(0xffe70074u)) + iVar3) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffe70020u + (uint32_t)(iVar3) * 1u)))) = 0;
    iVar4 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  return;
}



void FUN_00061a76(uint param_1,uint param_2,uint param_3)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  uint uVar5;
  int iVar6;
  
  param_1 = param_1 & 0xffff;
  param_2 = param_2 & 0xffff;
  param_3 = param_3 & 0xffff;
  uVar4 = (uint)DAT_00031670;
  iVar6 = 0;
  do {
    iVar2 = iVar6 + 1;
    uVar5 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x315d0u + (uint32_t)(iVar6) * 1u))));
    iVar3 = uVar5 * 0x1000;
    iVar1 = iVar6 + -1;
    *(undefined2 *)(((undefined *)camry_host_ptr(0xffe70210u)) + iVar3) = 0;
    *(uint *)(((undefined *)camry_host_ptr(0xffe7006cu)) + iVar3) = param_1;
    *(uint *)(((undefined *)camry_host_ptr(0xffe70070u)) + iVar3) = param_1;
    *(undefined2 *)(((undefined *)camry_host_ptr(0xffe70210u)) + iVar3) = 0xda5a;
    *(uint *)(((undefined *)camry_host_ptr(0xffe7014cu)) + iVar3) = param_2;
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xffe70184u + (uint32_t)(uVar5 * 0x400) * 4u)))) = param_3;
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xffe70180u + (uint32_t)(uVar5 * 0x400) * 4u)))) = param_3;
    *(uint *)(((undefined *)camry_host_ptr(0xffe70148u)) + iVar3) = param_2 + uVar4 * -2 & 0xffff;
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xffe70144u + (uint32_t)(uVar5 * 0x400) * 4u)))) = param_1 * 2 + param_2 & 0xffff;
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xffe70188u + (uint32_t)(uVar5 * 0x400) * 4u)))) = param_3;
    iVar6 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  return;
}



void FUN_00061b22(void)

{
  int iVar1;
  undefined1 uVar2;
  int iVar3;
  int iVar4;
  
  iVar4 = 0;
  do {
    iVar3 = (short)iVar4 * 0x28;
    uVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x3161cu + (uint32_t)(iVar3) * 1u))));
    FUN_000607fe(uVar2);
    FUN_0006082c(((undefined *)camry_host_ptr(0x3161cu)) + iVar3);
    FUN_0006080e(uVar2);
    iVar1 = iVar4 + 1;
    iVar3 = iVar4 + -1;
    iVar4 = iVar1;
  } while (((iVar3 < 0) || (iVar1 < 0)));
  return;
}



void FUN_00061b90(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  byte bVar4;
  uint uVar5;
  uint uVar6;
  uint saved_mask;
  int iVar7;
  uint uVar8;
  uint uVar9;
  
  uVar8 = (uint)f33_pwm_compare_span;
  uVar9 = (uint)DAT_00031672;
  uVar5 = (uint)f33_pwm_compare_offset;
  uVar6 = (uint)DAT_00031670;
  saved_mask = f33_priority_mask_enter(0xffc0);
  iVar7 = 0;
  do {
    bVar4 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x315d0u + (uint32_t)(iVar7) * 1u))));
    iVar2 = iVar7 + 1;
    iVar3 = (uint)bVar4 * 0x1000;
    iVar1 = iVar7 + -1;
    *(undefined4 *)(((undefined *)camry_host_ptr(0xffe70078u)) + iVar3) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffe70004u + (uint32_t)(iVar3) * 1u)))) = 0;
    *(undefined4 *)(((undefined *)camry_host_ptr(0xffe7007cu)) + iVar3) = 0x80;
    *(undefined4 *)(((undefined *)camry_host_ptr(0xffe70074u)) + iVar3) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffe70020u + (uint32_t)(iVar3) * 1u)))) = 0;
    *(uint *)(((undefined *)camry_host_ptr(0xffe7014cu)) + iVar3) = uVar8;
    *(uint *)(((undefined *)camry_host_ptr(0xffe70148u)) + iVar3) = uVar8 + uVar6 * -2 & 0xffff;
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xffe70144u + (uint32_t)((uint)bVar4 * 0x400) * 4u)))) = uVar9 * 2 + uVar5 * 2 & 0xffff;
    iVar7 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  f33_priority_mask_restore(saved_mask);
  uVar9 = 0;
  do {
    if (((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x3161cu + (uint32_t)((short)uVar9 * 0x28) * 1u))))) != -1) {
      FUN_00060a6a(((undefined *)camry_host_ptr(0x3161cu)) + (short)uVar9 * 0x28);
    }
    uVar9 = uVar9 + 1;
  } while (uVar9 < 2);
  return;
}



/* For absent input bits0/3/1/4/2/5, OR descriptor315D4+bank*1C halfwords+8/A/C/E/10/12 into the
   software PWM port_mask. No peripheral write here; later commit owner is separate. Recovered
   callers pass bank0/1; no local bank bound. */

void f33_stage_configured_phase_mask(uint bank,uint mask)

{
  ushort uVar1;
  int iVar2;
  
  iVar2 = (short)bank * 0x1c;
  uVar1 = 0;
  if ((mask & 1) == 0) {
    uVar1 = *(ushort *)(((undefined *)camry_host_ptr(0x315dcu)) + iVar2);
  }
  if ((mask >> 3 & 1) == 0) {
    uVar1 = uVar1 | *(ushort *)(((undefined *)camry_host_ptr(0x315deu)) + iVar2);
  }
  if ((mask >> 1 & 1) == 0) {
    uVar1 = uVar1 | *(ushort *)(((undefined *)camry_host_ptr(0x315e0u)) + iVar2);
  }
  if ((mask >> 4 & 1) == 0) {
    uVar1 = uVar1 | *(ushort *)(((undefined *)camry_host_ptr(0x315e2u)) + iVar2);
  }
  if ((mask >> 2 & 1) == 0) {
    uVar1 = uVar1 | *(ushort *)(((undefined *)camry_host_ptr(0x315e4u)) + iVar2);
  }
  if ((mask >> 5 & 1) == 0) {
    uVar1 = uVar1 | *(ushort *)(((undefined *)camry_host_ptr(0x315e6u)) + iVar2);
  }
  f33_pwm_halfword_stages[bank].port_mask = uVar1;
  return;
}



void FUN_00061dfa(short param_1,ushort param_2)

{
  int iVar1;
  ushort uVar2;
  ushort uVar3;
  ushort uVar4;
  ushort uVar5;
  ushort uVar6;
  int iVar7;
  
  iVar7 = param_1 * 0x1c;
  uVar6 = ~((*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x315e8u + (uint32_t)(param_1 * 0xe) * 2u)))) & param_2);
  iVar1 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x315dbu + (uint32_t)(iVar7) * 1u)))) * 0x40;
  uVar2 = *(ushort *)(((undefined *)camry_host_ptr(0x315eeu)) + iVar7);
  uVar5 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x315e8u + (uint32_t)(param_1 * 0xe) * 2u)))) & uVar6;
  uVar3 = *(ushort *)(((undefined *)camry_host_ptr(0x315ecu)) + iVar7);
  uVar4 = ~uVar5;
  (*((ushort *)camry_host_ptr((uint32_t)(iVar1 + -0x3effe8)))) =
       *(ushort *)(((undefined *)camry_host_ptr(0x315eau)) + iVar7) & uVar5 | (*((ushort *)camry_host_ptr((uint32_t)(iVar1 + -0x3effe8)))) & uVar4;
  (*((ushort *)camry_host_ptr((uint32_t)(iVar1 + -0x3effe4)))) = uVar5 & uVar3 | (*((ushort *)camry_host_ptr((uint32_t)(iVar1 + -0x3effe4)))) & uVar4;
  (*((ushort *)camry_host_ptr((uint32_t)(iVar1 + -0x3effd8)))) = uVar5 & uVar2 | uVar4 & (*((ushort *)camry_host_ptr((uint32_t)(iVar1 + -0x3effd8))));
  (*((ushort *)camry_host_ptr((uint32_t)(iVar1 + -0x3ebff8)))) = (*((ushort *)camry_host_ptr((uint32_t)(iVar1 + -0x3ebff8)))) | uVar5;
  (*((ushort *)camry_host_ptr((uint32_t)(iVar1 + -0x3f0000)))) = (*((ushort *)camry_host_ptr((uint32_t)(iVar1 + -0x3f0000)))) & uVar6;
  (*((ushort *)camry_host_ptr((uint32_t)(iVar1 + -0x3effec)))) = (*((ushort *)camry_host_ptr((uint32_t)(iVar1 + -0x3effec)))) | uVar5;
  (*((ushort *)camry_host_ptr((uint32_t)(iVar1 + -0x3effec)))) = (*((ushort *)camry_host_ptr((uint32_t)(iVar1 + -0x3effec)))) & uVar6;
  (*((ushort *)camry_host_ptr((uint32_t)(iVar1 + -0x3efff0)))) = (*((ushort *)camry_host_ptr((uint32_t)(iVar1 + -0x3efff0)))) & uVar6;
  return;
}



void FUN_00061e72(void)

{
  int iVar1;
  undefined2 *puVar2;
  int iVar3;
  undefined2 uVar4;
  uint uVar5;
  undefined8 uVar6;
  int iVar7;
  
  uVar6 = 0xfebeb800;
  iVar7 = 0;
  do {
    puVar2 = (undefined2 *)(((undefined *)camry_host_ptr(0xffff80a0u)) + iVar7 * 8 + (int)uVar6);
    uVar4 = *puVar2;
    uVar5 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x315d0u + (uint32_t)(iVar7) * 1u))));
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xffe70184u + (uint32_t)(uVar5 * 0x400) * 4u)))) = (uint)(ushort)puVar2[2];
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xffe70180u + (uint32_t)(uVar5 * 0x400) * 4u)))) = (uint)(ushort)puVar2[3];
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xffe70188u + (uint32_t)(uVar5 * 0x400) * 4u)))) = (uint)(ushort)puVar2[1];
    FUN_00061dfa(iVar7,uVar4);
    iVar3 = iVar7 + 1;
    iVar1 = iVar7 + -1;
    iVar7 = iVar3;
  } while (((iVar1 < 0) || (iVar3 < 0)));
  return;
}



void FUN_00061eb8(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  
  iVar5 = 0;
  do {
    iVar2 = iVar5 + 1;
    iVar3 = (uint)(ushort)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x315e8u + (uint32_t)((short)iVar5 * 0xe) * 2u)))) << 0x10;
    iVar4 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x315dbu + (uint32_t)((short)iVar5 * 0x1c) * 1u)))) * 0x40;
    iVar1 = iVar5 + -1;
    (*((int *)camry_host_ptr((uint32_t)(iVar4 + -0x3efffc)))) = iVar3;
    (*((int *)camry_host_ptr((uint32_t)(iVar4 + -0x3effdc)))) = iVar3;
    (*((int *)camry_host_ptr((uint32_t)(iVar4 + -0x3effe0)))) = iVar3;
    iVar5 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  return;
}



void FUN_00061ee8(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  int iVar5;
  
  iVar5 = 0;
  do {
    uVar4 = (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x315d4u + (uint32_t)((short)iVar5 * 7) * 4u)))) & 0xf;
    iVar2 = (((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x315d4u + (uint32_t)((short)iVar5 * 7) * 4u)))) & 0xff00) >> 8) * 0x40;
    (*((uint *)camry_host_ptr((uint32_t)(iVar2 + -0x3efffc)))) =
         ((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x315d9u + (uint32_t)((short)iVar5 * 0x1c) * 1u)))) & 1 | 0x10000) << uVar4;
    iVar1 = iVar5 + 1;
    iVar3 = 0x10000 << uVar4;
    (*((int *)camry_host_ptr((uint32_t)(iVar2 + -0x3effdc)))) = iVar3;
    (*((int *)camry_host_ptr((uint32_t)(iVar2 + -0x3effe0)))) = iVar3;
    iVar2 = iVar5 + -1;
    iVar5 = iVar1;
  } while (((iVar2 < 0) || (iVar1 < 0)));
  return;
}



/* Use descriptor315D4+bank*1C: port group bits8..15, pin low4 and level byte+4. Write
   ((level&1)|10000)<<pin to FFC10004+group*40. Exact banks0/1 targetFFC100C4 bit6 andFFC10084 bit4;
   level-a is1 and level-b0. No local bank bound, GPIO readback or physical bridge-state proof. */

void f33_write_configured_output_port_level_a(uint bank)

{
  (*((uint *)camry_host_ptr((uint32_t)((((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x315d4u + (uint32_t)((short)bank * 7) * 4u)))) & 0xff00) >> 8) * 0x40 + -0x3efffc)))) =
       ((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x315d8u + (uint32_t)((short)bank * 0x1c) * 1u)))) & 1 | 0x10000) <<
       ((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x315d4u + (uint32_t)((short)bank * 7) * 4u)))) & 0xf);
  return;
}



/* Use descriptor315D4+bank*1C: port group bits8..15, pin low4 and level byte+5. Write
   ((level&1)|10000)<<pin to FFC10004+group*40. Exact banks0/1 targetFFC100C4 bit6 andFFC10084 bit4;
   level-a is1 and level-b0. No local bank bound, GPIO readback or physical bridge-state proof. */

void f33_write_configured_output_port_level_b(uint bank)

{
  (*((uint *)camry_host_ptr((uint32_t)((((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x315d4u + (uint32_t)((short)bank * 7) * 4u)))) & 0xff00) >> 8) * 0x40 + -0x3efffc)))) =
       ((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x315d9u + (uint32_t)((short)bank * 0x1c) * 1u)))) & 1 | 0x10000) <<
       ((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x315d4u + (uint32_t)((short)bank * 7) * 4u)))) & 0xf);
  return;
}



void FUN_00061f96(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  
  iVar5 = 0;
  do {
    iVar2 = iVar5 + 1;
    iVar3 = 0x10000 << ((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x315d4u + (uint32_t)((short)iVar5 * 7) * 4u)))) & 0xf);
    iVar4 = (((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x315d4u + (uint32_t)((short)iVar5 * 7) * 4u)))) & 0xff00) >> 8) * 0x40;
    iVar1 = iVar5 + -1;
    (*((int *)camry_host_ptr((uint32_t)(iVar4 + -0x3effdc)))) = iVar3;
    (*((int *)camry_host_ptr((uint32_t)(iVar4 + -0x3effe0)))) = iVar3;
    iVar5 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  return;
}



void FUN_00061fce(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  int iVar5;
  
  iVar5 = 0;
  do {
    uVar4 = f33_channel_ports[iVar5].output_selector & 0xf;
    iVar2 = ((f33_channel_ports[iVar5].output_selector & 0xff00) >> 8) * 0x40;
    (*((uint *)camry_host_ptr((uint32_t)(iVar2 + -0x3efffc)))) = (f33_channel_ports[iVar5].requested_level & 1 | 0x10000) << uVar4
    ;
    iVar1 = iVar5 + 1;
    iVar3 = 0x10000 << uVar4;
    (*((int *)camry_host_ptr((uint32_t)(iVar2 + -0x3effdc)))) = iVar3;
    (*((int *)camry_host_ptr((uint32_t)(iVar2 + -0x3effe0)))) = iVar3;
    iVar2 = iVar5 + -1;
    iVar5 = iVar1;
  } while (((iVar2 < 0) || (iVar1 < 0)));
  return;
}



void FUN_00062018(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  
  iVar5 = 0;
  do {
    iVar2 = iVar5 + 1;
    iVar3 = 0x10000 << (f33_channel_ports[iVar5].output_selector & 0xf);
    iVar4 = ((f33_channel_ports[iVar5].output_selector & 0xff00) >> 8) * 0x40;
    iVar1 = iVar5 + -1;
    (*((int *)camry_host_ptr((uint32_t)(iVar4 + -0x3effdc)))) = iVar3;
    (*((int *)camry_host_ptr((uint32_t)(iVar4 + -0x3effe0)))) = iVar3;
    iVar5 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  return;
}



/* Descriptor-driven masked port write using reference_level; no local index validation.
   Descriptor-indexed masked port write using reference level and output selector. Two reviewed
   channels are port0bit10 and port3bit5; generic helper has no local index check. */

void f33_write_channel_reference_level(uint channel)

{
  (*((uint *)camry_host_ptr((uint32_t)(((f33_channel_ports[channel].output_selector & 0xff00) >> 8) * 0x40 + -0x3efffc)))) =
       (f33_channel_ports[channel].reference_level & 1 | 0x10000) <<
       (f33_channel_ports[channel].output_selector & 0xf);
  return;
}



/* Descriptor-driven masked port write using requested_level; no local index validation.
   Descriptor-indexed masked port write using requested rather than reference level. Exact reviewed
   rows select level0 versus reference1; no inferred OEM actuator identity. */

void f33_write_channel_requested_level(uint channel)

{
  (*((uint *)camry_host_ptr((uint32_t)(((f33_channel_ports[channel].output_selector & 0xff00) >> 8) * 0x40 + -0x3efffc)))) =
       (f33_channel_ports[channel].requested_level & 1 | 0x10000) <<
       (f33_channel_ports[channel].output_selector & 0xf);
  return;
}



/* Read the descriptor-selected halfword port input, isolate its bit, return zero-extended level. No
   local index validation; the two reviewed wrappers pass0/1. Read descriptor-selected halfword port
   input and isolate its bit into zero-extended R10. Input observation is separate from
   output-register writes and physical response. */

uint f33_read_channel_input_level(uint channel)

{
  return (int)((uint)(*((ushort *)camry_host_ptr((uint32_t)((uint)f33_channel_ports[channel].input_port * 0x40 + -0x3efff4)))) &
              1 << (f33_channel_ports[channel].input_bit & 0x1f)) >>
         (f33_channel_ports[channel].input_bit & 0x1f) & 0xff;
}



/* Odd count selects count-3; even selects count-6 with one capacity addition only when count<6.
   Return low16; caller does not modulo-wrap each following offset. Boundary counts2/4 yield
   out-of-range zero tails, not ring wrap. No freshness/reachability claim. Native evidence covers
   explicit software continuations and a synthetic post-getter publication join, not descriptor
   acquisition or the intact fast task. */

ushort f33_select_acquisition_six_entry_base(ushort count,ushort capacity)

{
  ushort uVar1;
  
  if ((count & 1) == 0) {
    if (count < 6) {
      uVar1 = (capacity + count) - 6;
    }
    else {
      uVar1 = count - 6;
    }
  }
  else {
    uVar1 = count - 3;
  }
  return uVar1;
}



/* Real R6 is the output pointer, not an unused integer. Read descriptor count for channel0, select
   six-entry base with capacity432, consume offsets0..5 from30F2C through60676. Store six u16 at
   output+0. No software cursor advancement, per-entry validity check or retained-value fallback;
   out-of-range returns0. Native evidence covers explicit software continuations and a synthetic
   post-getter publication join, not descriptor acquisition or the intact fast task. */

void f33_copy_acquisition_group0_samples(F33AcquisitionGroupPair *output)

{
  int iVar1;
  int iVar2;
  ushort uVar3;
  uint uVar4;
  int iVar5;
  
  uVar3 = f33_count_transfer_entries('\0');
  uVar3 = f33_select_acquisition_six_entry_base(uVar3,0x1b0);
  iVar5 = 0;
  do {
    uVar4 = f33_consume_acquisition_group0_entry(""[iVar5] + uVar3);
    output->group0[iVar5] = (ushort)uVar4;
    iVar2 = iVar5 + 1;
    iVar1 = iVar5 + -5;
    iVar5 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  return;
}



/* Real R6 is the output pointer, not an unused integer. Read descriptor count for channel8, select
   six-entry base with capacity432, consume offsets0..5 from30F34 through60720. Store six u16 at
   output+12. No software cursor advancement, per-entry validity check or retained-value fallback;
   out-of-range returns0. Native evidence covers explicit software continuations and a synthetic
   post-getter publication join, not descriptor acquisition or the intact fast task. */

void f33_copy_acquisition_group8_samples(F33AcquisitionGroupPair *output)

{
  int iVar1;
  int iVar2;
  ushort uVar3;
  uint uVar4;
  int iVar5;
  
  uVar3 = f33_count_transfer_entries('\b');
  uVar3 = f33_select_acquisition_six_entry_base(uVar3,0x1b0);
  iVar5 = 0;
  do {
    uVar4 = f33_consume_acquisition_group8_entry(""[iVar5] + uVar3);
    output->group8[iVar5] = (ushort)uVar4;
    iVar2 = iVar5 + 1;
    iVar1 = iVar5 + -5;
    iVar5 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  return;
}



/* Call620FE then6213E with the SAME real R6 pointer, saved inR29. Produces group0[6],group8[6] at
   offsets0/12. Fix auto-decompiler missing620FE argument; native62182/62188 explicitly
   preserve/restore it. Descriptor counts are separate reads, not one producer epoch. */

void f33_copy_acquisition_group_pair(F33AcquisitionGroupPair *output)

{
  f33_copy_acquisition_group0_samples(output);
  f33_copy_acquisition_group8_samples(output);
  return;
}



/* Channel<2: clear driver buffers/flags/four-slot mask arrays/cursor and published occurrence
   counters; seed prior sequence3 and numeric triplet{0,0,0800}. First valid incoming sequence0
   qualifies. No acquisition completed by initialization. */

void f33_initialize_serial_acquisition_channel(uchar channel)

{
  undefined2 *puVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  ushort uVar5;
  int iVar6;
  int iVar7;
  
  if (channel < 2) {
    uVar5 = (ushort)channel;
    iVar7 = (short)uVar5 * 0x5a;
    iVar6 = (short)(ushort)channel * 6;
    uVar3 = 0;
    do {
      puVar1 = (undefined2 *)(((undefined *)camry_host_ptr(0xfebe3900u)) + uVar3 * 2 + iVar7);
      uVar3 = uVar3 + 1;
      *puVar1 = 0;
      puVar1[10] = 0;
    } while (uVar3 < 10);
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe3928u + (uint32_t)(iVar7) * 1u)))) = 3;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe3929u + (uint32_t)(iVar7) * 1u)))) = 0;
    uVar3 = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe392au + (uint32_t)(iVar7) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe392bu + (uint32_t)(iVar7) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe392cu + (uint32_t)(iVar7) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe392du + (uint32_t)(iVar7) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe392eu + (uint32_t)(iVar7) * 1u)))) = 0;
    do {
      iVar2 = uVar3 * 2 + iVar7;
      uVar3 = uVar3 + 1;
      *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe3900u)) + iVar2 + 0x30) = 0;
      *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe3900u)) + iVar2 + 0x38) = 0;
    } while (uVar3 < 4);
    uVar3 = 0;
    do {
      iVar2 = uVar3 + (uint)channel * 2;
      uVar3 = uVar3 + 1;
      *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe38c8u)) + iVar2 * 2) = 0;
    } while (uVar3 < 2);
    uVar3 = 0;
    do {
      (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe3900u + (uint32_t)(uVar3 + iVar7 + 0x40) * 2u)))) = 0;
      *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe3900u)) + uVar3 * 2 + iVar7 + 0x42) = 0;
      uVar4 = 0;
      do {
        iVar2 = (short)uVar3 * 5 + uVar4;
        uVar4 = uVar4 + 1;
        *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe3900u)) + iVar2 * 2 + iVar7 + 0x46) = 0;
      } while (uVar4 < 5);
      uVar3 = uVar3 + 1;
    } while (uVar3 < 2);
    f33_serial_acquisition_retained_records[(short)uVar5].sequence_failures = '\0';
    f33_serial_acquisition_retained_records[(short)uVar5].crc_failures = '\0';
    f33_serial_acquisition_retained_records[(short)uVar5].rx_or_tx_failures = '\0';
    f33_serial_acquisition_retained_records[(short)uVar5].rx_count_failures = '\0';
    f33_serial_acquisition_retained_records[(short)uVar5].field12 = 0x800;
    f33_serial_acquisition_retained_records[(short)uVar5].field14_1 = 0;
    f33_serial_acquisition_retained_records[(short)uVar5].field14_0 = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe38edu + (uint32_t)(iVar6) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe38ecu + (uint32_t)(iVar6) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe38ebu + (uint32_t)(iVar6) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe38eau + (uint32_t)(iVar6) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe38e9u + (uint32_t)(iVar6) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe38e8u + (uint32_t)(iVar6) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe38f9u + (uint32_t)(iVar6) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe38f8u + (uint32_t)(iVar6) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe38f7u + (uint32_t)(iVar6) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe38f6u + (uint32_t)(iVar6) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe38f5u + (uint32_t)(iVar6) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe38f4u + (uint32_t)(iVar6) * 1u)))) = 0;
  }
  return;
}



void FUN_00062274(uint param_1,int param_2)

{
  undefined1 uVar1;
  int iVar2;
  uint uVar3;
  int iVar4;
  
  param_1 = param_1 & 0xff;
  if (param_1 < 2) {
    iVar4 = (short)param_1 * 0x5a;
    uVar3 = 0;
    do {
      iVar2 = uVar3 * 2;
      uVar3 = uVar3 + 1;
      (*((undefined2 *)camry_host_ptr((uint32_t)(iVar2 + iVar4 + -0x141c6ec)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(iVar2 + param_2))));
    } while (uVar3 < 5);
    *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe3926u)) + iVar4) = 0;
    *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe3924u)) + iVar4) = 0;
    *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe3922u)) + iVar4) = 0;
    *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe3920u)) + iVar4) = 0;
    *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe391eu)) + iVar4) = 0xe700;
    iVar2 = FUN_00060efa(""[param_1],iVar4 + -0x141c6ec);
    uVar1 = 0;
    if (iVar2 != 0) {
      uVar1 = 0x5a;
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe392cu + (uint32_t)(iVar4) * 1u)))) = uVar1;
  }
  return;
}



void FUN_000622d2(undefined1 param_1,uint param_2)

{
  uint uVar1;
  ushort auStack_e [5];
  
  uVar1 = param_2 & 0xff | 0x13;
  auStack_e[1] = 0;
  auStack_e[2] = 0;
  auStack_e[3] = 0;
  auStack_e[4] = 0;
  auStack_e[0] = (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2b118u + (uint32_t)(uVar1 ^ 0xff) * 1u)))) ^ 0xff | (ushort)(uVar1 << 8);
  FUN_00062274(param_1, camry_host_addr(auStack_e));
  return;
}



void FUN_0006230e(uint param_1)

{
  int iVar1;
  uchar uVar2;
  int iVar3;
  undefined8 uVar4;
  uint uVar5;
  
  uVar4 = 0xfebeb800;
  param_1 = param_1 & 0xff;
  if (param_1 < 2) {
    uVar2 = "\x02\n"[param_1];
    FUN_000607fe(uVar2);
    iVar3 = (int)uVar4;
    for (uVar5 = (uint)DAT_00031e8c; uVar5 != 0; uVar5 = uVar5 - 1) {
      FUN_000622d2(param_1,0xe0);
      FUN_00060f7c(param_1,0);
      f33_spin_wait((uint)DAT_00031e8d);
      f33_read_serial_controller_status
                (""[param_1],0x100,(F33SerialControllerStatus *)(((undefined *)camry_host_ptr(0xfebe38f4u)) + (short)param_1 * 6)
                );
      iVar3 = (int)uVar4;
    }
    uVar5 = 0;
    iVar3 = (short)param_1 * 0x5a + iVar3;
    do {
      iVar1 = uVar5 * 2;
      uVar5 = uVar5 + 1;
      (*((undefined2 *)camry_host_ptr((uint32_t)((int)(0xffff8100u) + iVar1 + iVar3 + 0x14)))) = 0;
    } while (uVar5 < 10);
    (*((undefined1 *)camry_host_ptr((uint32_t)((int)(0xffff8100u) + iVar3 + 0x2c)))) = 0;
    FUN_0006080e(uVar2);
  }
  return;
}



void FUN_0006239e(undefined1 param_1)

{
  undefined2 uStack_e;
  undefined2 uStack_c;
  undefined2 uStack_a;
  undefined2 uStack_8;
  undefined2 uStack_6;
  
  uStack_6 = 0;
  uStack_8 = 0;
  uStack_a = 0;
  uStack_c = 0;
  uStack_e = 0xe700;
  FUN_00062274(param_1, camry_host_addr(&uStack_e));
  return;
}



void FUN_000623c0(void)

{
  uint uVar1;
  
  uVar1 = 0;
  do {
    f33_initialize_serial_acquisition_channel((uchar)uVar1);
    FUN_0006230e(uVar1);
    FUN_0006239e(uVar1);
    uVar1 = uVar1 + 1;
  } while (uVar1 < 2);
  f33_spin_wait((uint)DAT_00031e88);
  return;
}



undefined4 FUN_000623ee(byte *param_1)

{
  undefined4 uVar1;
  
  uVar1 = 0x5a;
  if (param_1[8] ==
      ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2b118u + (uint32_t)(param_1[9] ^
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2b118u + (uint32_t)(param_1[6] ^
         (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2b118u + (uint32_t)(param_1[7] ^
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2b118u + (uint32_t)(param_1[4] ^
           (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2b118u + (uint32_t)(param_1[5] ^
            (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2b118u + (uint32_t)(param_1[2] ^ (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2b118u + (uint32_t)(param_1[3] ^ (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2b118u + (uint32_t)(*param_1 ^ 0xff) * 1u))))) * 1u))))) * 1u))))) * 1u))))) * 1u))))) * 1u))))) * 1u))))) * 1u)))) ^
      0xff)) {
    uVar1 = 0;
  }
  return uVar1;
}



/* Channel<2: OR accepted11-bit frame masks into scratch+30/+38 arrays using(cursor+2E&3). Does not
   advance cursor, clear prior slot or publish application masks.6294E owns cursor advancement and
   previous-slot clear. Native evidence covers explicit software continuations and a synthetic
   post-getter publication join, not descriptor acquisition or the intact fast task. */

void f33_accumulate_serial_acquisition_masks(uchar channel,ushort first_mask,ushort second_mask)

{
  int iVar1;
  
  if (channel < 2) {
    iVar1 = ((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe392eu + (uint32_t)((short)(ushort)channel * 0x5a) * 1u)))) & 3) * 2 +
            (short)(ushort)channel * 0x5a;
    *(ushort *)(((undefined *)camry_host_ptr(0xfebe3900u)) + iVar1 + 0x30) =
         *(ushort *)(((undefined *)camry_host_ptr(0xfebe3900u)) + iVar1 + 0x30) | first_mask;
    *(ushort *)(((undefined *)camry_host_ptr(0xfebe3900u)) + iVar1 + 0x38) =
         *(ushort *)(((undefined *)camry_host_ptr(0xfebe3900u)) + iVar1 + 0x38) | second_mask;
  }
  return;
}



/* Caller62576 guarantees channel<2 and initializes verdicts0. Use descriptor low
   count31676[channel] to select two five-u16 FIFO blocks; validate second with623EE. Bad CRC
   retains sequence/triplet/masks. CRC-valid incoming sequence is stored BEFORE next-sequence
   comparison; mismatch sets5A and retains triplet/masks while resynchronizing. Accepted14/14/12-bit
   fields write38D0+12*channel and OR two11-bit masks through6245A. No FIFO acknowledgment. Native
   evidence covers explicit software continuations and a synthetic post-getter publication join, not
   descriptor acquisition or the intact fast task. */

void f33_decode_serial_acquisition_frame
               (uchar channel,uchar fifo,uchar *crc_failure,uchar *sequence_failure)

{
  ushort uVar1;
  ushort uVar2;
  ushort uVar3;
  byte bVar4;
  uchar offset;
  uint uVar5;
  int iVar6;
  uchar offset_00;
  ushort uVar7;
  int iVar8;
  
  uVar7 = (ushort)channel;
  iVar8 = (short)uVar7 * 0x5a;
  uVar5 = f33_read_transfer_primary_count_low("\x02\n"[channel]);
  if (uVar5 < 0xb) {
    if (uVar5 < 6) {
      offset_00 = '\n';
      offset = '\x05';
    }
    else {
      offset_00 = '\x05';
      offset = '\0';
    }
  }
  else if (uVar5 < 0x10) {
    offset_00 = '\0';
    offset = '\x0f';
  }
  else {
    offset_00 = '\x0f';
    offset = '\n';
  }
  f33_copy_serial_fifo_words(fifo,(ushort *)(((undefined *)camry_host_ptr(0xfebe3900u)) + iVar8),offset,'\x05');
  f33_copy_serial_fifo_words(fifo,(ushort *)(((undefined *)camry_host_ptr(0xfebe390au)) + iVar8),offset_00,'\x05');
  iVar6 = FUN_000623ee(((undefined *)camry_host_ptr(0xfebe390au)) + iVar8);
  *crc_failure = (uchar)iVar6;
  if (iVar6 == 0) {
    bVar4 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe3928u + (uint32_t)(iVar8) * 1u))));
    uVar5 = (int)(*(ushort *)(((undefined *)camry_host_ptr(0xfebe390au)) + iVar8) & 0xc0) >> 6;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe3928u + (uint32_t)(iVar8) * 1u)))) = (char)uVar5;
    if (uVar5 == (bVar4 + 1 & 3)) {
      uVar1 = *(ushort *)(((undefined *)camry_host_ptr(0xfebe390cu)) + iVar8);
      f33_serial_acquisition_retained_records[(short)uVar7].field14_0 =
           (ushort)((*(ushort *)(((undefined *)camry_host_ptr(0xfebe390au)) + iVar8) & 0x3f) << 8) | uVar1 >> 8;
      uVar2 = *(ushort *)(((undefined *)camry_host_ptr(0xfebe390eu)) + iVar8);
      uVar3 = *(ushort *)(((undefined *)camry_host_ptr(0xfebe3910u)) + iVar8);
      f33_serial_acquisition_retained_records[(short)uVar7].field14_1 =
           (uVar1 & 0xff) << 6 | uVar2 >> 10;
      f33_serial_acquisition_retained_records[(short)uVar7].field12 =
           (uVar2 & 0x3ff) << 2 | uVar3 >> 0xe;
      f33_accumulate_serial_acquisition_masks
                (channel,(ushort)((int)(uVar3 & 0x3ff8) >> 3),
                 (ushort)((uVar3 & 7) << 8) | *(ushort *)(((undefined *)camry_host_ptr(0xfebe3912u)) + iVar8) >> 8);
    }
    else {
      *sequence_failure = 'Z';
    }
  }
  return;
}



/* Channel<2: snapshot61054 into38E8+6*channel. Only status.byte2==0 and byte3==10 decode62488.
   Otherwise retain decoded sample and set RX/count failure. CRC/sequence local flags reset0 on
   every call before admission; publish scratch+29/+2A/+2B/+2D verdicts, not counters. */

void f33_sample_serial_acquisition_channel(uchar channel)

{
  uchar channel_00;
  undefined1 uVar1;
  undefined1 uVar2;
  int iVar3;
  int iVar4;
  uchar uStack_1e;
  uchar uStack_1d;
  
  if (channel < 2) {
    iVar4 = (short)(ushort)channel * 0x5a;
    uStack_1e = '\0';
    uStack_1d = '\0';
    uVar2 = 0;
    iVar3 = (short)(ushort)channel * 6;
    channel_00 = ""[channel];
    f33_read_serial_controller_status
              (channel_00,0,(F33SerialControllerStatus *)(((undefined *)camry_host_ptr(0xfebe38e8u)) + iVar3));
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe38eau + (uint32_t)(iVar3) * 1u)))) == '\0') {
      uVar1 = 0;
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe38ebu + (uint32_t)(iVar3) * 1u)))) == '\n') {
        f33_decode_serial_acquisition_frame(channel,channel_00,&uStack_1e,&uStack_1d);
      }
      else {
        uVar2 = 0x5a;
      }
    }
    else {
      uVar1 = 0x5a;
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe392au + (uint32_t)(iVar4) * 1u)))) = uVar1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe3929u + (uint32_t)(iVar4) * 1u)))) = uVar2;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe392bu + (uint32_t)(iVar4) * 1u)))) = uStack_1e;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe392du + (uint32_t)(iVar4) * 1u)))) = uStack_1d;
  }
  return;
}



byte FUN_000625f6(byte *param_1)

{
  return (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2b118u + (uint32_t)(param_1[5] ^
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2b118u + (uint32_t)(param_1[2] ^
           (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2b118u + (uint32_t)(param_1[3] ^ (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2b118u + (uint32_t)(*param_1 ^ (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2b118u + (uint32_t)(param_1[1] ^ 0xff) * 1u))))) * 1u))))) * 1u))))) * 1u))))) * 1u)))) ^ 0xff;
}



void FUN_00062636(uint param_1,uint param_2)

{
  ushort uVar1;
  ushort uVar2;
  int iVar3;
  ushort uStack_16;
  ushort uStack_14;
  undefined2 uStack_12;
  undefined2 uStack_10;
  undefined2 uStack_e;
  
  param_1 = param_1 & 0xff;
  param_2 = param_2 & 0xff;
  if ((param_1 < 2) && (param_2 < 2)) {
    iVar3 = (short)param_1 * 0x5a;
    iVar3 = ((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe392eu + (uint32_t)(iVar3) * 1u)))) & 3) * 2 + iVar3;
    if (param_2 == 0) {
      uVar1 = *(ushort *)(((undefined *)camry_host_ptr(0xfebe3900u)) + iVar3 + 0x30);
      uVar2 = 0x20;
    }
    else {
      uVar1 = *(ushort *)(((undefined *)camry_host_ptr(0xfebe3900u)) + iVar3 + 0x38);
      uVar2 = 0xff81;
    }
    uStack_14 = (uVar1 & 0x7ff | (ushort)((uVar1 & 0x70) << 7) | (ushort)((uVar1 & 0x40) << 8)) &
                DAT_00031e86;
    uVar1 = *(ushort *)(((undefined *)camry_host_ptr(0xfebe38c8u)) + (param_2 + param_1 * 2) * 2);
    *(ushort *)(((undefined *)camry_host_ptr(0xfebe38c8u)) + (param_2 + param_1 * 2) * 2) = 0;
    uStack_12 = 0;
    uStack_14 = uStack_14 | uVar1;
    uStack_16 = (uVar2 | 1) << 8 | 0x10;
    uStack_12 = FUN_000625f6(&uStack_16);
    uStack_10 = 0;
    uStack_e = 0;
    FUN_00062274(param_1, camry_host_addr(&uStack_16));
  }
  return;
}



void FUN_000626d6(ushort param_1,char param_2)

{
  bool bVar1;
  undefined2 *puVar2;
  int iVar3;
  
  if ((param_1 & 0xff) < 2) {
    iVar3 = (short)(param_1 & 0xff) * 0x5a;
    puVar2 = (undefined2 *)(((undefined *)camry_host_ptr(0xfebe3900u)) + iVar3);
    bVar1 = param_2 != '\0';
    puVar2[(short)(ushort)bVar1 * 5 + 0x23] = *puVar2;
    puVar2[(short)(ushort)bVar1 * 5 + 0x24] = *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe3902u)) + iVar3);
    puVar2[(short)(ushort)bVar1 * 5 + 0x25] = *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe3904u)) + iVar3);
    puVar2[(short)(ushort)bVar1 * 5 + 0x26] = *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe3906u)) + iVar3);
    puVar2[(short)(ushort)bVar1 * 5 + 0x27] = *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe3908u)) + iVar3);
  }
  return;
}



void FUN_00062714(undefined1 param_1,char param_2,char param_3)

{
  int iVar1;
  undefined2 uStack_e;
  undefined2 uStack_c;
  undefined2 uStack_a;
  undefined2 uStack_8;
  undefined2 uStack_6;
  
  if (param_3 == 'Z') {
    iVar1 = (short)(ushort)(param_2 != '\0') * 10;
    uStack_e = *(undefined2 *)(((undefined *)camry_host_ptr(0x31e8eu)) + iVar1);
    uStack_c = *(undefined2 *)(((undefined *)camry_host_ptr(0x31e90u)) + iVar1);
    uStack_a = *(undefined2 *)(((undefined *)camry_host_ptr(0x31e92u)) + iVar1);
    uStack_8 = *(undefined2 *)(((undefined *)camry_host_ptr(0x31e94u)) + iVar1);
    uStack_6 = *(undefined2 *)(((undefined *)camry_host_ptr(0x31e96u)) + iVar1);
  }
  else {
    uStack_8 = 0;
    uStack_a = 0;
    uStack_c = 0;
    uStack_e = 0;
    uStack_6 = 0;
  }
  FUN_00062274(param_1, camry_host_addr(&uStack_e));
  return;
}



void FUN_0006276c(ushort param_1,char param_2)

{
  int iVar1;
  char cVar2;
  int iVar3;
  uint uVar4;
  undefined2 uVar5;
  short sVar6;
  
  param_1 = param_1 & 0xff;
  if (param_1 < 2) {
    uVar4 = (uint)(param_2 != '\0');
    iVar3 = uVar4 + (short)param_1 * 0x5a;
    cVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x31e8au + (uint32_t)(uVar4) * 1u))));
    iVar1 = uVar4 * 2;
    if (cVar2 == (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe3900u + (uint32_t)(iVar3 + 0x40) * 2u))))) {
      sVar6 = *(short *)(((undefined *)camry_host_ptr(0xfebe3900u)) + iVar1 + (short)param_1 * 0x5a + 0x42);
    }
    else {
      sVar6 = *(short *)(((undefined *)camry_host_ptr(0x31e82u)) + iVar1);
    }
    if (sVar6 == 0) {
      uVar5 = 0;
    }
    else {
      if (sVar6 != -1) {
        sVar6 = sVar6 + -1;
      }
      uVar5 = 0x5a;
    }
    FUN_00062714(param_1,uVar4,uVar5);
    *(short *)(((undefined *)camry_host_ptr(0xfebe3900u)) + iVar1 + (short)param_1 * 0x5a + 0x42) = sVar6;
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe3900u + (uint32_t)(iVar3 + 0x40) * 2u)))) = cVar2;
  }
  return;
}



/* Channel<2: increment wrappingu8 counters38D6..D9+12*channel for missing/wrong RX count, combined
   RX-status or TX-submission failure, software CRC failure, sequence failure. Equality5A only.
   Numeric retention and sequence acceptance are separate; zero after wrap is not healthy/fresh
   proof. */

void f33_accumulate_serial_acquisition_failures(uchar channel)

{
  int iVar1;
  ushort uVar2;
  
  if (channel < 2) {
    uVar2 = (ushort)channel;
    iVar1 = (short)uVar2 * 0x5a;
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe3929u + (uint32_t)(iVar1) * 1u)))) == 'Z') {
      f33_serial_acquisition_retained_records[(short)uVar2].rx_count_failures =
           f33_serial_acquisition_retained_records[(short)uVar2].rx_count_failures + '\x01';
    }
    if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe392au + (uint32_t)(iVar1) * 1u)))) == 'Z') || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe392cu + (uint32_t)(iVar1) * 1u)))) == 'Z')) {
      f33_serial_acquisition_retained_records[(short)uVar2].rx_or_tx_failures =
           f33_serial_acquisition_retained_records[(short)uVar2].rx_or_tx_failures + '\x01';
    }
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe392bu + (uint32_t)(iVar1) * 1u)))) == 'Z') {
      f33_serial_acquisition_retained_records[(short)uVar2].crc_failures =
           f33_serial_acquisition_retained_records[(short)uVar2].crc_failures + '\x01';
    }
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe392du + (uint32_t)(iVar1) * 1u)))) == 'Z') {
      f33_serial_acquisition_retained_records[(short)uVar2].sequence_failures =
           f33_serial_acquisition_retained_records[(short)uVar2].sequence_failures + '\x01';
    }
  }
  return;
}



/* Run62576, then command/reply branch selected by
   entry39D8&3:0->62636(0),626D6(1);1->6276C(0);2->62636(1),626D6(0);3->6276C(1).
   Call60F7C(channel,0), then627E0. Sample decoding can fail/retain while a current command error
   updates counters. Task advances39D8 only after both channels and application dispatch. */

void f33_service_serial_acquisition_channel(uchar channel)

{
  byte bVar1;
  uint32_t puVar2;
  undefined4 uVar3;
  
  puVar2 = 0xfebeb800u;
  f33_sample_serial_acquisition_channel(channel);
  bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x7e28))))) & 3;
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x7e28))))) & 3) == 0) {
    FUN_00062636(channel,bVar1);
    uVar3 = 1;
LAB_00062880:
    FUN_000626d6(channel,uVar3);
  }
  else {
    if (bVar1 == 1) {
      uVar3 = 0;
    }
    else {
      uVar3 = 1;
      if (bVar1 == 2) {
        FUN_00062636(channel,1);
        uVar3 = 0;
        goto LAB_00062880;
      }
    }
    FUN_0006276c(channel,uVar3);
  }
  FUN_00060f7c(channel,0);
  f33_accumulate_serial_acquisition_failures(channel);
  return;
}



/* Service logical channels0 then1 through62846, without incrementing task phase between them.66786
   invokes this before66824 caches serial samples/counters. No ADC or serial timing guarantee. */

void f33_service_serial_acquisition_pair(void)

{
  uint uVar1;
  
  uVar1 = 0;
  do {
    f33_service_serial_acquisition_channel((uchar)uVar1);
    uVar1 = uVar1 + 1;
  } while (uVar1 < 2);
  return;
}



/* For channels0/1: clear mask arrays at previous(cursor-1)&3, read current first mask, advance
   cursor(cursor+1)&3, publish first mask then read/publish current second mask. Output two4-byte
   mask pairs. Current slot is not cleared in this call.66932 publication5F18/1A/22/24 belongs to
   another task generation than66824 numeric/counters. */

void f33_rotate_and_copy_serial_acquisition_masks(F33SerialAcquisitionMasks *output)

{
  F33SerialAcquisitionMasks *pFVar1;
  ushort uVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  uint uVar6;
  
  uVar5 = 0;
  do {
    iVar4 = (short)uVar5 * 0x5a;
    uVar6 = (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe392eu + (uint32_t)(iVar4) * 1u)))) & 3;
    iVar3 = (uVar6 - 1 & 3) * 2 + iVar4;
    *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe3900u)) + iVar3 + 0x30) = 0;
    *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe3900u)) + iVar3 + 0x38) = 0;
    uVar2 = *(ushort *)(((undefined *)camry_host_ptr(0xfebe3930u)) + uVar6 * 2 + iVar4);
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe392eu + (uint32_t)(iVar4) * 1u)))) = (char)uVar6 + 1U & 3;
    pFVar1 = output + uVar5;
    uVar5 = uVar5 + 1;
    pFVar1->first = uVar2;
    pFVar1->second = *(ushort *)(((undefined *)camry_host_ptr(0xfebe3900u)) + uVar6 * 2 + iVar4 + 0x38);
  } while (uVar5 < 2);
  return;
}



/* Write two12-byte-stride records: threeu16 plus fouru8 occurrence counters; offsets10/11 remain
   untouched. Types ROM31678={0,11}: second record negates modulo14/14/12 bits; first copies raw.
   Does not acquire, validate, clear counters, copy ancillary masks or distinguish current/retained
   sample. Native evidence covers explicit software continuations and a synthetic post-getter
   publication join, not descriptor acquisition or the intact fast task. */

void f33_copy_cached_serial_acquisition_records(F33SerialAcquisitionRecord *output)

{
  F33SerialAcquisitionRecord *pFVar1;
  ushort uVar2;
  short sVar3;
  uint uVar4;
  
  uVar4 = 0;
  do {
    sVar3 = (short)uVar4;
    pFVar1 = output + sVar3;
    if (""[uVar4] == '\x11') {
      pFVar1->field14_0 = -f33_serial_acquisition_retained_records[sVar3].field14_0 & 0x3fff;
      pFVar1->field14_1 = -f33_serial_acquisition_retained_records[sVar3].field14_1 & 0x3fff;
      uVar2 = -f33_serial_acquisition_retained_records[sVar3].field12 & 0xfff;
    }
    else {
      pFVar1->field14_0 = f33_serial_acquisition_retained_records[sVar3].field14_0;
      pFVar1->field14_1 = f33_serial_acquisition_retained_records[sVar3].field14_1;
      uVar2 = f33_serial_acquisition_retained_records[sVar3].field12;
    }
    pFVar1->field12 = uVar2;
    uVar4 = uVar4 + 1;
    pFVar1->rx_count_failures = f33_serial_acquisition_retained_records[sVar3].rx_count_failures;
    pFVar1->rx_or_tx_failures = f33_serial_acquisition_retained_records[sVar3].rx_or_tx_failures;
    pFVar1->crc_failures = f33_serial_acquisition_retained_records[sVar3].crc_failures;
    pFVar1->sequence_failures = f33_serial_acquisition_retained_records[sVar3].sequence_failures;
  } while (uVar4 < 2);
  return;
}



void FUN_00062a16(uint param_1,uint param_2,ushort param_3)

{
  uint32_t puVar1;
  uint saved_mask;
  
  puVar1 = 0xfebeb800u;
  if (((param_1 & 0xff) < 2) && ((param_2 & 0xff) < 2)) {
    saved_mask = f33_priority_mask_enter(0xffc0);
    (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + ((param_2 & 0xff) + (param_1 & 0xff) * 2) * 2 + -0x7f38)))) =
         (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + ((param_2 & 0xff) + (param_1 & 0xff) * 2) * 2 + -0x7f38)))) | param_3;
    f33_priority_mask_restore(saved_mask);
  }
  return;
}



/* Write four destination halfwords using group6 count/base plus four ROM30F20 byte indices and60630
   getter. No physical channel identity or freshness is added. */

void f33_copy_transfer_group6_samples(ushort *destination)

{
  int iVar1;
  int iVar2;
  ushort uVar3;
  ushort uVar4;
  int iVar5;
  
  uVar3 = f33_count_transfer_entries('\x06');
  iVar5 = 0;
  do {
    uVar4 = FUN_00060630((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x30f20u + (uint32_t)(iVar5) * 1u)))) + uVar3);
    destination[iVar5] = uVar4;
    iVar2 = iVar5 + 1;
    iVar1 = iVar5 + -3;
    iVar5 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  return;
}



/* Write five halfwords at destination+8 using group14 count/base plus ROM30F44 indices and606DA
   getter. The first four halfwords are preserved. */

void f33_copy_transfer_group14_samples(ushort *destination)

{
  int iVar1;
  int iVar2;
  ushort uVar3;
  ushort uVar4;
  int iVar5;
  
  uVar3 = f33_count_transfer_entries('\x0e');
  iVar5 = 0;
  do {
    uVar4 = FUN_000606da((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x30f44u + (uint32_t)(iVar5) * 1u)))) + uVar3);
    destination[iVar5 + 4] = uVar4;
    iVar2 = iVar5 + 1;
    iVar1 = iVar5 + -4;
    iVar5 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  return;
}



/* Copy four halfwords through62A50 then five through62A86 into the same destination; retain the
   original destination across the first call. Firmware transfer groups6/14 are structural indices.
    */

void f33_copy_acquisition_diagnostic_samples(ushort *destination)

{
  f33_copy_transfer_group6_samples(destination);
  f33_copy_transfer_group14_samples(destination);
  return;
}



void FUN_00062ad0(undefined2 *param_1)

{
  ushort uVar1;
  undefined2 uVar2;
  
  uVar1 = f33_count_transfer_entries('\x06');
  uVar2 = FUN_00060630(DAT_00030f3f + uVar1);
  *param_1 = uVar2;
  return;
}



void FUN_00062af4(int param_1)

{
  ushort uVar1;
  undefined2 uVar2;
  
  uVar1 = f33_count_transfer_entries('\x0e');
  uVar2 = FUN_000606da(DAT_00030f40 + uVar1);
  (*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 2)))) = uVar2;
  return;
}



void FUN_00062b32(int param_1)

{
  int iVar1;
  undefined2 *puVar2;
  int iVar3;
  uint uVar4;
  int iVar5;
  undefined2 local_14;
  undefined2 uStack_12;
  undefined2 uStack_10;
  undefined2 uStack_e;
  
  iVar5 = 0;
  do {
    uVar4 = f33_read_transfer_descriptor_head((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x3125cu + (uint32_t)((short)iVar5 * 0x28) * 1u)))));
    FUN_00060c60(iVar5,uVar4 < iVar5 * 0x30 + 0xfeef9110U,&local_14);
    iVar3 = iVar5 + 1;
    puVar2 = ((undefined2 *)camry_host_ptr((uint32_t)(iVar5 * 8 + param_1)));
    iVar1 = iVar5 + -1;
    *puVar2 = uStack_10;
    puVar2[1] = uStack_e;
    puVar2[2] = uStack_12;
    puVar2[3] = local_14;
    iVar5 = iVar3;
  } while (((iVar1 < 0) || (iVar3 < 0)));
  return;
}



/* Clear39BC..39BF;recognize exactprotected prior token9B9B9B9B,3E3E3E3E,6D6D6D6D,5A5A5A5A,setting
   correspondingflag5A. Lasttoken additionallyrequires39B8.highbyte5A. Thenpublish7C7C7C7C
   withXORcopies through62B90 andclearPowerOnResetflag viaRESFC=1. OEM tokenmeaning isnot
   assigned;thisdoesnot establish physicalresetretention. */

void f33_startup_classify_retained_token(void)

{
  DAT_febe39bf = 0;
  DAT_febe39be = 0;
  DAT_febe39bd = 0;
  DAT_febe39bc = 0;
  if (((DAT_febe39b4 == -0x64646465) && (DAT_febe8de4 == -0x31313132)) &&
     (DAT_febe8df8 == 0x31313131)) {
    DAT_febe39bc = 0x5a;
  }
  if (((DAT_febe39b4 == 0x3e3e3e3e) && (DAT_febe8de4 == 0x6b6b6b6b)) &&
     (DAT_febe8df8 == -0x6b6b6b6c)) {
    DAT_febe39bd = 0x5a;
  }
  if (((DAT_febe39b4 == 0x6d6d6d6d) && (DAT_febe8de4 == 0x38383838)) &&
     (DAT_febe8df8 == -0x38383839)) {
    DAT_febe39be = 0x5a;
  }
  if ((((DAT_febe39b4 == 0x5a5a5a5a) && (DAT_febe8de4 == 0xf0f0f0f)) && (DAT_febe8df8 == -0xf0f0f10)
      ) && ((DAT_febe39b8 & 0xff000000) == 0x5a000000)) {
    DAT_febe39bf = 0x5a;
  }
  FUN_00062b90(0x7c7c7c7c);
  DAT_fff81008 = 1;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_62d54(void)

{
  return;
}



undefined4 FUN_00062d56(undefined2 *param_1)

{
  *param_1 = 0;
  return 0;
}



void FUN_00062df0(void)

{
  int iVar1;
  undefined1 auStack_8 [4];
  
  iVar1 = FUN_00070822(((undefined *)camry_host_ptr(0xfebf0668u)),((undefined *)camry_host_ptr(0xfebf10a4u)),((undefined *)camry_host_ptr(0xfebf10c8u)),auStack_8);
  if (iVar1 != 0) {
    f33_startup_publish_image_identity_check();
  }
  return;
}



undefined4 FUN_00062e12(void)

{
  return DAT_febf0668;
}



undefined1 FUN_00062e18(void)

{
  return DAT_febf066c;
}



void FUN_00062e44(ushort *param_1,ushort param_2)

{
  byte bVar1;
  
  bVar1 = 0;
  do {
    *param_1 = param_2;
    bVar1 = bVar1 + 1;
    __synchronize();
    if (((*param_1 ^ param_2) & 0xf) == 0) {
      return;
    }
  } while (bVar1 < 10);
                    /* WARNING: Subroutine does not return */
  f33_enter_terminal_hardware_sequence();
}



/* Sequential initializer chain: 6 unconditional calls and no other statements; shape-verified. The
   called sequence is the function's entire behavior; chain family members differ in callee sets. */

void f33_run_init_chain_632c8(void)

{
  FUN_00065458();
  FUN_000654aa();
  FUN_000657fa();
  FUN_00065852();
  FUN_0006586a();
  FUN_0006595e();
  return;
}



void FUN_00063324(void)

{
  f33_spin_wait(1000);
                    /* WARNING: Subroutine does not return */
  f33_enter_terminal_hardware_sequence();
}



void FUN_00063338(void)

{
  uchar uVar1;
  uint uVar2;
  byte bVar3;
  
  bVar3 = 0;
  ECMPEM = 3;
  while( true ) {
    ECMPCMD1 = 0xa5;
    bVar3 = bVar3 + 1;
    ECMEMK0 = 0xffffffe1;
    ECMEMK0 = 0x1e;
    ECMEMK0 = 0xffffffe1;
    uVar1 = ECMPS;
    if (uVar1 == '\0') break;
    if (2 < bVar3) {
      FUN_00063324();
    }
  }
  bVar3 = 0;
  while( true ) {
    bVar3 = bVar3 + 1;
    ECMPCMD1 = 0xa5;
    ECMEMK1 = 0xffffffff;
    ECMEMK1 = 0;
    ECMEMK1 = 0xffffffff;
    uVar1 = ECMPS;
    if (uVar1 == '\0') break;
    if (2 < bVar3) {
      FUN_00063324();
    }
  }
  bVar3 = 0;
  while( true ) {
    ECMPCMD1 = 0xa5;
    bVar3 = bVar3 + 1;
    ECMEMK2 = 0x3fffffff;
    ECMEMK2 = 0xc0000000;
    ECMEMK2 = 0x3fffffff;
    uVar1 = ECMPS;
    if (uVar1 == '\0') break;
    if (2 < bVar3) {
      FUN_00063324();
    }
  }
  bVar3 = 0;
  while( true ) {
    ECMPCMD1 = 0xa5;
    bVar3 = bVar3 + 1;
    ECMMICFG0 = 0;
    ECMMICFG0 = 0xffffffff;
    ECMMICFG0 = 0;
    uVar1 = ECMPS;
    if (uVar1 == '\0') break;
    if (2 < bVar3) {
      FUN_00063324();
    }
  }
  bVar3 = 0;
  while( true ) {
    ECMPCMD1 = 0xa5;
    bVar3 = bVar3 + 1;
    ECMMICFG1 = 0;
    ECMMICFG1 = 0xffffffff;
    ECMMICFG1 = 0;
    uVar1 = ECMPS;
    if (uVar1 == '\0') break;
    if (2 < bVar3) {
      FUN_00063324();
    }
  }
  bVar3 = 0;
  while( true ) {
    ECMPCMD1 = 0xa5;
    bVar3 = bVar3 + 1;
    ECMMICFG2 = 0;
    ECMMICFG2 = 0xffffffff;
    ECMMICFG2 = 0;
    uVar1 = ECMPS;
    if (uVar1 == '\0') break;
    if (2 < bVar3) {
      FUN_00063324();
    }
  }
  bVar3 = 0;
  while( true ) {
    ECMPCMD1 = 0xa5;
    bVar3 = bVar3 + 1;
    ECMNMICFG0 = 0;
    ECMNMICFG0 = 0xffffffff;
    ECMNMICFG0 = 0;
    uVar1 = ECMPS;
    if (uVar1 == '\0') break;
    if (2 < bVar3) {
      FUN_00063324();
    }
  }
  bVar3 = 0;
  while( true ) {
    ECMPCMD1 = 0xa5;
    bVar3 = bVar3 + 1;
    ECMNMICFG1 = 0;
    ECMNMICFG1 = 0xffffffff;
    ECMNMICFG1 = 0;
    uVar1 = ECMPS;
    if (uVar1 == '\0') break;
    if (2 < bVar3) {
      FUN_00063324();
    }
  }
  bVar3 = 0;
  while( true ) {
    ECMPCMD1 = 0xa5;
    bVar3 = bVar3 + 1;
    ECMNMICFG2 = 0;
    ECMNMICFG2 = 0xffffffff;
    ECMNMICFG2 = 0;
    uVar1 = ECMPS;
    if (uVar1 == '\0') break;
    if (2 < bVar3) {
      FUN_00063324();
    }
  }
  bVar3 = 0;
  while( true ) {
    ECMPCMD1 = 0xa5;
    bVar3 = bVar3 + 1;
    ECMIRCFG0 = 0;
    ECMIRCFG0 = 0xffffffff;
    ECMIRCFG0 = 0;
    uVar1 = ECMPS;
    if (uVar1 == '\0') break;
    if (2 < bVar3) {
      FUN_00063324();
    }
  }
  bVar3 = 0;
  while( true ) {
    ECMPCMD1 = 0xa5;
    bVar3 = bVar3 + 1;
    ECMIRCFG1 = 0;
    ECMIRCFG1 = 0xffffffff;
    ECMIRCFG1 = 0;
    uVar1 = ECMPS;
    if (uVar1 == '\0') break;
    if (2 < bVar3) {
      FUN_00063324();
    }
  }
  bVar3 = 0;
  while( true ) {
    ECMPCMD1 = 0xa5;
    bVar3 = bVar3 + 1;
    ECMIRCFG2 = 0;
    ECMIRCFG2 = 0xffffffff;
    ECMIRCFG2 = 0;
    uVar1 = ECMPS;
    if (uVar1 == '\0') break;
    if (2 < bVar3) {
      FUN_00063324();
    }
  }
  bVar3 = 0;
  while( true ) {
    ECMMPCMD0 = 0xa5;
    ECMMECLR = '\x01';
    ECMMECLR = 0xfe;
    bVar3 = bVar3 + 1;
    ECMMECLR = '\x01';
    uVar1 = ECMPS;
    if (uVar1 == '\0') break;
    if (2 < bVar3) {
      FUN_00063324();
    }
  }
  bVar3 = 0;
  uVar2 = 0;
  do {
    if ((int)uVar2 < 0) break;
    uVar2 = ECMMESSTR2;
    bVar3 = bVar3 + 1;
  } while (bVar3 < 0x1f);
  bVar3 = 0;
  while( true ) {
    ECMCPCMD0 = 0xa5;
    ECMCECLR = '\x01';
    ECMCECLR = 0xfe;
    ECMCECLR = '\x01';
    uVar1 = ECMPS;
    if (uVar1 == '\0') break;
    bVar3 = bVar3 + 1;
    if (2 < bVar3) {
      FUN_00063324();
    }
  }
  uVar2 = 0x80000000;
  bVar3 = 0;
  do {
    if (-1 < (int)uVar2) break;
    uVar2 = ECMCESSTR2;
    bVar3 = bVar3 + 1;
  } while (bVar3 < 0x1f);
  ECMPEM = 0;
  return;
}



void FUN_000636f8(void)

{
  char *pcVar1;
  int iVar2;
  uint uVar3;
  
  uVar3 = 0;
  do {
    iVar2 = uVar3 + 0x10;
    pcVar1 = ((undefined *)camry_host_ptr(0xfebf7b50u)) + uVar3;
    uVar3 = uVar3 + 1;
    *pcVar1 = "APP INFO AREA   PVSDKS5A@"[iVar2];
  } while (uVar3 < 0x40);
  return;
}



void FUN_00063738(void)

{
  uint uVar1;
  uchar uVar2;
  byte bVar3;
  
  FUN_00071610();
  FUN_00065c64();
  FUN_00065d4a();
  FUN_00065e58();
  bVar3 = 0;
  do {
    ECMPCMD1 = 0xa5;
    ECMMICFG0 = 0x100b001e;
    ECMMICFG0 = 0xeff4ffe1;
    ECMMICFG0 = 0x100b001e;
    uVar1 = ECMMICFG0;
    __synchronize();
    uVar2 = ECMPS;
    if (uVar2 == '\0') {
      return;
    }
    bVar3 = bVar3 + 1;
  } while (bVar3 < 3);
                    /* WARNING: Subroutine does not return */
  f33_enter_terminal_hardware_sequence();
}



/* Before releasingapplicationtimers,feedall10240wordsat0000..9FFF intoDCRA1 withCTL0/seedFFFFFFFF.
   AcceptonlyCOUTFFFFFFFF;retryup tothree times,thenenter61940 fatalhandling. Areturned initializer
   meanssoftwaregatepassedagainst suppliedhardwareCRCfeedback,not aphysicalCRCmodelproof. */

void f33_startup_validate_resident_boot_crc(void)

{
  uint *puVar1;
  byte bVar2;
  uint uVar3;
  
  bVar2 = 0;
  while( true ) {
    uVar3 = 0;
    DCRA1CTL = '\0';
    DCRA1COUT = 0xffffffff;
    while (uVar3 < 0x2800) {
      puVar1 = ((uint *)camry_host_ptr((uint32_t)(uVar3 * 4)));
      uVar3 = uVar3 + 1;
      DCRA1CIN = *puVar1;
    }
    uVar3 = DCRA1COUT;
    bVar2 = bVar2 + 1;
    if (uVar3 == 0xffffffff) break;
    if (2 < bVar2) {
                    /* WARNING: Subroutine does not return */
      f33_enter_terminal_hardware_sequence();
    }
  }
  return;
}



/* Sequential initializer chain: 4 unconditional calls and no other statements; shape-verified. The
   called sequence is the function's entire behavior; chain family members differ in callee sets. */

void f33_run_init_chain_6385c(void)

{
  FUN_00063874();
  FUN_00063d4a();
  f33_run_init_chain_6484e();
  FUN_00064c00();
  return;
}



void FUN_00063874(void)

{
  uint outer_iterations;
  char cVar1;
  undefined8 uVar2;
  int iVar3;
  byte bVar4;
  undefined2 local_38;
  undefined2 uStack_36;
  undefined2 uStack_34;
  undefined2 uStack_32;
  undefined2 uStack_30;
  undefined2 uStack_2e;
  undefined2 uStack_2c;
  undefined2 uStack_2a;
  undefined2 uStack_28;
  undefined2 uStack_26;
  undefined2 uStack_24;
  undefined2 uStack_22;
  
  uVar2 = 0xfebeb800;
  bVar4 = 0;
  iVar3 = 0xff;
  FUN_000613c8();
  FUN_000616fc();
  uStack_28 = 0x8200;
  uStack_26 = 0;
  uStack_24 = 0x5018;
  uStack_22 = 0x1f00;
  FUN_00061836(&uStack_28);
  outer_iterations = DAT_00030d7c;
  f33_spin_wait(DAT_00030d7c);
  do {
    uStack_2a = 0x1f00;
    uStack_2c = 0x5018;
    uStack_2e = 0;
    uStack_30 = 0x8200;
    FUN_00061836(&uStack_30);
    f33_spin_wait(outer_iterations);
    uStack_32 = 0x1f00;
    uStack_34 = 0x5018;
    uStack_36 = 0;
    local_38 = 0x8200;
    FUN_00061836(&local_38);
    f33_spin_wait(outer_iterations);
    FUN_000614d4();
    cVar1 = '\0';
    if (((*((byte *)camry_host_ptr((uint32_t)((int)uVar2 + -0x7fc6)))) & 1) != 0) {
      cVar1 = 'Z';
    }
    (*((char *)camry_host_ptr((uint32_t)((int)uVar2 + -0x8000)))) = cVar1;
    if (cVar1 == 'Z') {
      iVar3 = 0;
    }
    else if (1 < bVar4) {
                    /* WARNING: Subroutine does not return */
      f33_enter_terminal_hardware_sequence();
    }
    bVar4 = bVar4 + 1;
  } while (iVar3 == 0xff);
  return;
}



int FUN_00063922(void)

{
  int iVar1;
  undefined8 uVar2;
  int iVar3;
  byte bVar4;
  undefined2 local_14;
  undefined2 uStack_12;
  undefined2 uStack_10;
  undefined2 uStack_e;
  
  uVar2 = 0xfebeb800;
  bVar4 = 0;
  iVar3 = 0xff;
  do {
    local_14 = 0x8200;
    uStack_12 = 0;
    uStack_10 = 0x5018;
    uStack_e = 0x1f00;
    FUN_00061836(&local_14);
    f33_spin_wait(DAT_00030d80);
    FUN_000614d4();
    iVar1 = 0;
    if (((*((byte *)camry_host_ptr((uint32_t)((int)uVar2 + -0x7fc8)))) & 0x80) != 0) {
      iVar1 = 0x5a;
    }
    if (iVar1 == 0) {
      iVar3 = 0;
    }
    else if (1 < bVar4) {
      iVar3 = 0x11;
    }
    bVar4 = bVar4 + 1;
  } while (iVar3 == 0xff);
  return iVar3;
}



void FUN_00063984(char param_1)

{
  uint outer_iterations;
  undefined2 *puVar1;
  undefined2 local_24;
  undefined2 uStack_22;
  undefined2 uStack_20;
  undefined2 uStack_1e;
  undefined2 uStack_1c;
  undefined2 uStack_1a;
  undefined2 uStack_18;
  undefined2 uStack_16;
  
  if (param_1 == '3') {
    f33_publish_redundant_u16
              (0xa55a,(ushort *)((undefined *)camry_host_ptr(0xfebe39c6u)),(ushort *)((undefined *)camry_host_ptr(0xfebe8de8u)),(ushort *)((undefined *)camry_host_ptr(0xfebe8dfcu)));
    return;
  }
  puVar1 = ((undefined *)camry_host_ptr(0xfebe39c2u));
  if (((param_1 == '\"') || (puVar1 = ((undefined *)camry_host_ptr(0xfebe39c0u)), param_1 == '\x11')) ||
     (puVar1 = ((undefined *)camry_host_ptr(0xfebe39c4u)), param_1 == 'D')) {
    *puVar1 = 0xa55a;
  }
  uStack_16 = 0x1f00;
  uStack_18 = 0x5018;
  uStack_1a = 0;
  uStack_1c = 0x8380;
  FUN_00061836(&uStack_1c);
  outer_iterations = DAT_00030d80;
  f33_spin_wait(DAT_00030d80);
  uStack_1e = 0x1f00;
  uStack_20 = 0x5018;
  uStack_22 = 0;
  local_24 = 0x8000;
  FUN_00061836(&local_24);
  f33_spin_wait(outer_iterations);
                    /* WARNING: Subroutine does not return */
  f33_enter_terminal_hardware_sequence();
}



undefined4 FUN_00063a18(undefined1 param_1)

{
  uint outer_iterations;
  undefined8 uVar1;
  int iVar2;
  byte bVar3;
  int iVar4;
  undefined2 local_2c;
  undefined2 uStack_2a;
  undefined2 uStack_28;
  undefined2 uStack_26;
  undefined2 uStack_24;
  undefined2 uStack_22;
  undefined2 uStack_20;
  undefined2 uStack_1e;
  undefined2 uStack_1c;
  undefined2 uStack_1a;
  undefined2 uStack_18;
  undefined2 uStack_16;
  
  uVar1 = 0xfebeb800;
  bVar3 = 0;
  iVar4 = 0xff;
  iVar2 = FUN_00061906(param_1);
  if (iVar2 == 0) {
    f33_spin_wait(DAT_00030d88);
    uStack_1c = 0x8200;
    uStack_1a = 0;
    uStack_18 = 0x5018;
    uStack_16 = 0x1f00;
    FUN_00061836(&uStack_1c);
    outer_iterations = DAT_00030d80;
    f33_spin_wait(DAT_00030d80);
    do {
      uStack_24 = 0x8200;
      uStack_22 = 0;
      uStack_20 = 0x5018;
      uStack_1e = 0x1f00;
      FUN_00061836(&uStack_24);
      f33_spin_wait(outer_iterations);
      FUN_000614d4();
      iVar2 = 0;
      if (((*((byte *)camry_host_ptr((uint32_t)((int)uVar1 + -0x7fc8)))) & 0x80) != 0) {
        iVar2 = 0x5a;
      }
      if (iVar2 == 0) {
        iVar4 = 0;
      }
      else if (1 < bVar3) {
        iVar4 = 0x11;
      }
      bVar3 = bVar3 + 1;
    } while (iVar4 == 0xff);
    if (iVar4 == 0x11) {
      return 0x11;
    }
    f33_spin_wait(f33_startup_spin_iteration_count);
    for (bVar3 = 0; bVar3 <= DAT_00030d94; bVar3 = bVar3 + 1) {
      if (iVar2 == 0x5a) {
        return 0;
      }
      local_2c = 0x8200;
      uStack_2a = 0;
      uStack_28 = 0x5018;
      uStack_26 = 0x1f00;
      FUN_00061836(&local_2c);
      f33_spin_wait(DAT_00030d90);
      FUN_000614d4();
      iVar2 = 0;
      if (((*((byte *)camry_host_ptr((uint32_t)((int)uVar1 + -0x7fc8)))) & 0x80) != 0) {
        iVar2 = 0x5a;
      }
    }
  }
  return 0x11;
}



int FUN_00063b24(void)

{
  int iVar1;
  undefined8 uVar2;
  int iVar3;
  byte bVar4;
  undefined2 local_14;
  undefined2 uStack_12;
  undefined2 uStack_10;
  undefined2 uStack_e;
  
  uVar2 = 0xfebeb800;
  bVar4 = 0;
  iVar3 = 0xff;
  do {
    local_14 = 0x8200;
    uStack_12 = 0;
    uStack_10 = 0x5018;
    uStack_e = 0x1f00;
    FUN_00061836(&local_14);
    f33_spin_wait(DAT_00030d80);
    FUN_000614d4();
    iVar1 = 0;
    if (((*((byte *)camry_host_ptr((uint32_t)((int)uVar2 + -0x7fc7)))) & 8) != 0) {
      iVar1 = 0x5a;
    }
    if (iVar1 == 0x5a) {
      iVar3 = 0;
    }
    else if (1 < bVar4) {
      iVar3 = 0x11;
    }
    bVar4 = bVar4 + 1;
  } while (iVar3 == 0xff);
  return iVar3;
}



int FUN_00063b88(void)

{
  ushort uVar1;
  uint outer_iterations;
  int iVar2;
  undefined8 uVar3;
  int iVar4;
  byte bVar5;
  int iVar6;
  undefined2 local_38;
  undefined2 uStack_36;
  undefined2 uStack_34;
  undefined2 uStack_32;
  undefined2 uStack_30;
  undefined2 uStack_2e;
  undefined2 uStack_2c;
  undefined2 uStack_2a;
  undefined2 uStack_28;
  undefined2 uStack_26;
  undefined2 uStack_24;
  undefined2 uStack_22;
  
  uVar3 = 0xfebeb800;
  bVar5 = 0;
  iVar6 = 0xff;
  iVar4 = FUN_00061906(1);
  f33_spin_wait(DAT_00030d84);
  uStack_28 = 0x8380;
  uStack_26 = 0;
  uStack_24 = 0x5018;
  uStack_22 = 0x1f00;
  FUN_00061836(&uStack_28);
  outer_iterations = DAT_00030d80;
  f33_spin_wait(DAT_00030d80);
  if (iVar4 == 0) {
    do {
      uStack_2a = 0x1f00;
      uStack_2c = 0x5018;
      uStack_2e = 0;
      uStack_30 = 0x8380;
      FUN_00061836(&uStack_30);
      f33_spin_wait(outer_iterations);
      uStack_32 = 0x1f00;
      uStack_34 = 0x5018;
      uStack_36 = 0;
      local_38 = 0x8380;
      FUN_00061836(&local_38);
      f33_spin_wait(outer_iterations);
      FUN_000614d4();
      uVar1 = (*((ushort *)camry_host_ptr((uint32_t)((int)uVar3 + -0x7fc8))));
      iVar4 = 0;
      if ((uVar1 >> 7 & 1) != 0) {
        iVar4 = 0x5a;
      }
      iVar2 = 0;
      if ((uVar1 >> 0xb & 1) != 0) {
        iVar2 = 0x5a;
      }
      if ((iVar4 == 0) && (iVar2 == 0)) {
        iVar6 = 0;
      }
      else if (1 < bVar5) {
        iVar6 = 0x11;
      }
      bVar5 = bVar5 + 1;
    } while (iVar6 == 0xff);
  }
  else {
    iVar6 = 0x11;
  }
  return iVar6;
}



void FUN_00063c5c(undefined1 param_1)

{
  int iVar1;
  int iVar2;
  int iVar3;
  undefined *puVar4;
  int iVar5;
  undefined2 local_1c;
  undefined2 uStack_1a;
  undefined2 uStack_18;
  undefined2 uStack_16;
  
  iVar2 = DAT_febe8df8;
  iVar1 = DAT_febe8de4;
  iVar5 = DAT_febe39b4;
  puVar4 = ((undefined *)camry_host_ptr(0xfebeb800u));
  iVar3 = 0;
  if ((DAT_febe3838 & 0x80) != 0) {
    iVar3 = 0x5a;
  }
  if ((iVar3 != 0) && (puVar4 = ((undefined *)camry_host_ptr(0xfebeb800u)), iVar3 = FUN_00063922(), iVar3 == 0x11)) {
    FUN_00063984(0x11);
  }
  iVar3 = 0;
  if ((puVar4[-0x7fc7] & 8) != 0) {
    iVar3 = 0x5a;
  }
  if (iVar3 == 0x5a) {
    if (((iVar5 == 0x7c7c7c7c) && (iVar1 == 0x29292929)) && (iVar2 == -0x2929292a)) {
      f33_publish_redundant_u16
                (0xa55a,(ushort *)(puVar4 + -0x7e38),(ushort *)(puVar4 + -0x2a16),
                 (ushort *)(puVar4 + -0x2a02));
    }
    local_1c = 0x8380;
    uStack_1a = 0;
    uStack_18 = 0x5018;
    uStack_16 = 0x1f00;
    FUN_00061836(&local_1c);
    f33_spin_wait(DAT_00030d80);
  }
  iVar5 = FUN_00063a18(param_1);
  if (iVar5 == 0x11) {
    FUN_00063984(0x22);
  }
  iVar5 = 0;
  if ((puVar4[-0x7fc7] & 8) != 0) {
    iVar5 = 0x5a;
  }
  if ((iVar5 != 0x5a) && (iVar5 = FUN_00063b24(), iVar5 == 0x11)) {
    FUN_00063984(0x33);
  }
  iVar5 = FUN_00063b88();
  if (iVar5 == 0x11) {
    FUN_00063984(0x44);
  }
  return;
}



void FUN_00063d4a(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  f33_publish_redundant_u16
            (0,(ushort *)((undefined *)camry_host_ptr(0xfebe39c6u)),(ushort *)((undefined *)camry_host_ptr(0xfebe8de8u)),(ushort *)((undefined *)camry_host_ptr(0xfebe8dfcu)));
  f33_publish_redundant_u16
            (0,((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x7e38))),((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x2a16))),
             ((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x2a02))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x7e40)))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x7e3e)))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x7e3c)))) = 0;
  FUN_00063c5c(2);
  FUN_00063c5c(0);
  return;
}



short FUN_00063d8e(void)

{
  int iVar1;
  short sStack_6;
  
  iVar1 = FUN_000707ac(((undefined *)camry_host_ptr(0xfebe39c8u)),((undefined *)camry_host_ptr(0xfebe8deau)),((undefined *)camry_host_ptr(0xfebe8dfeu)),&sStack_6);
  if ((iVar1 != 0) || (sStack_6 != -0x5aa6)) {
    sStack_6 = 0;
  }
  return sStack_6;
}



void FUN_00063dba(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  f33_publish_redundant_u16
            (0,(ushort *)((undefined *)camry_host_ptr(0xfebe39cau)),(ushort *)((undefined *)camry_host_ptr(0xfebe8decu)),(ushort *)((undefined *)camry_host_ptr(0xfebe8e00u)));
  f33_publish_redundant_u16
            (0,((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x7e34))),((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x2a12))),
             ((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x29fe))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x7e32))))) = 0;
  return;
}



void FUN_00063dea(void)

{
  uint uVar1;
  int iVar2;
  uint32_t puVar3;
  undefined1 uVar4;
  undefined2 local_18;
  undefined2 uStack_16;
  undefined2 uStack_14;
  undefined2 uStack_12;
  undefined2 uStack_10;
  undefined2 uStack_e;
  undefined2 uStack_c;
  undefined2 uStack_a;
  
  puVar3 = 0xfebeb800u;
  iVar2 = 0;
  uVar1 = DAT_fff81000;
  if ((DAT_febe3839 & 1) != 0) {
    iVar2 = 0x5a;
  }
  if (iVar2 == 0x5a) {
    puVar3 = 0xfebeb800u;
    if ((((DAT_febe39b4 == 0x7c7c7c7c) && (DAT_febe8de4 == 0x29292929)) &&
        (DAT_febe8df8 == -0x2929292a)) && ((uVar1 & 1) == 0)) {
      puVar3 = 0xfebeb800u;
      f33_publish_redundant_u16
                (0xa55a,(ushort *)((undefined *)camry_host_ptr(0xfebe39ccu)),(ushort *)((undefined *)camry_host_ptr(0xfebe8deeu)),(ushort *)((undefined *)camry_host_ptr(0xfebe8e02u)));
    }
    uStack_10 = 0x8250;
    uStack_e = 0;
    uStack_c = 0x5018;
    uStack_a = 0x1f00;
    FUN_00061836(&uStack_10);
    f33_spin_wait(DAT_00030d98);
  }
  uVar4 = FUN_000614b0();
  local_18 = 0x8210;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x7e32))))) = uVar4;
  uStack_14 = 0x5018;
  uStack_16 = 0;
  uStack_12 = 0x1f00;
  FUN_00061836(&local_18);
  f33_spin_wait(DAT_00030d98);
  return;
}



void FUN_00063ea4(char param_1)

{
  uint outer_iterations;
  undefined2 local_24;
  undefined2 uStack_22;
  undefined2 uStack_20;
  undefined2 uStack_1e;
  undefined2 uStack_1c;
  undefined2 uStack_1a;
  undefined2 uStack_18;
  undefined2 uStack_16;
  
  if (param_1 == '3') {
    f33_publish_redundant_u16
              (0xa55a,(ushort *)((undefined *)camry_host_ptr(0xfebe39cau)),(ushort *)((undefined *)camry_host_ptr(0xfebe8decu)),(ushort *)((undefined *)camry_host_ptr(0xfebe8e00u)));
    return;
  }
  if (param_1 == '\"') {
    FUN_00062b90(0x3e3e3e3e);
  }
  uStack_16 = 0x1f00;
  uStack_18 = 0x5018;
  uStack_1a = 0;
  uStack_1c = 0x8250;
  FUN_00061836(&uStack_1c);
  outer_iterations = DAT_00030d98;
  f33_spin_wait(DAT_00030d98);
  uStack_1e = 0x1f00;
  uStack_20 = 0x5018;
  uStack_22 = 0;
  local_24 = 0x8000;
  FUN_00061836(&local_24);
  f33_spin_wait(outer_iterations);
                    /* WARNING: Subroutine does not return */
  f33_enter_terminal_hardware_sequence();
}



void FUN_00063f24(void)

{
  uchar uVar1;
  byte bVar2;
  
  bVar2 = 0;
  do {
    bVar2 = bVar2 + 1;
    if (3 < bVar2) {
      FUN_00063ea4(0x11);
    }
    ECMPCMD1 = 0xa5;
    ECMESSTC0 = 4;
    ECMESSTC0 = 0xfffffffb;
    ECMESSTC0 = 4;
    uVar1 = ECMPS;
  } while (uVar1 != '\0');
  return;
}



undefined4 FUN_00063f94(void)

{
  uchar uVar1;
  uint uVar2;
  uint uVar3;
  byte bVar4;
  
  bVar4 = 0;
  do {
    bVar4 = bVar4 + 1;
    if (3 < bVar4) {
      FUN_00063ea4(0x11);
    }
    ECMMPCMD0 = 0xa5;
    ECMMECLR = '\x01';
    ECMMECLR = 0xfe;
    ECMMECLR = '\x01';
    uVar1 = ECMPS;
  } while (uVar1 != '\0');
  bVar4 = 0;
  do {
    bVar4 = bVar4 + 1;
    if (3 < bVar4) {
      FUN_00063ea4(0x11);
    }
    ECMCPCMD0 = 0xa5;
    ECMCECLR = '\x01';
    ECMCECLR = 0xfe;
    ECMCECLR = '\x01';
    uVar1 = ECMPS;
  } while (uVar1 != '\0');
  bVar4 = 0;
  do {
    bVar4 = bVar4 + 1;
    if (3 < bVar4) {
      FUN_00063ea4(0x11);
    }
    ECMPCMD1 = 0xa5;
    ECMESSTC2 = 0x10000000;
    ECMESSTC2 = 0xefffffff;
    ECMESSTC2 = 0x10000000;
    uVar1 = ECMPS;
  } while (uVar1 != '\0');
  uVar2 = 0x80000000;
  bVar4 = 0;
  uVar3 = 0;
  while ((-1 < (int)uVar3 || ((int)uVar2 < 0))) {
    uVar3 = ECMMESSTR2;
    bVar4 = bVar4 + 1;
    uVar2 = ECMCESSTR2;
    if (0x1e < bVar4) {
      return 0x11;
    }
  }
  return 0;
}


