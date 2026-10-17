#include "common.h"


/* Hardware reset-vector stub: SYNCP then absolute JMP01B0 without changingLP. The destination owns
   CPU context/safety gates and first1404 call. Not an ordinary C-call/return ABI. Physical device
   vector selection is outside this static proof. */

void f33_reset_vector(void)

{
  __synchronize();
  f33_reset_context_and_startup();
  return;
}



/* Hardware EIINT entry: SYNCP then branch to 10C. Not a normal C call. Boot EIINT entry: SYNCP then
   branch to context-save body 10C. Executed through real state1 timer callback and EIRET; no normal
   C arguments or return contract. FPEC=0 and manually seeded architectural interrupt context; not
   physical interrupt acquisition or timing. */

void f33_boot_eiint_vector(void)

{
  __synchronize();
  f33_boot_eiint_context();
  return;
}



/* Save r6, EIPC and EIPSW; read EIIC into r6, enable interrupts, save r1..lp and call 748. Restore
   registers, disable interrupts, restore EIPSW/EIPC/r6, then EIRET. Exact execution with FPEC=0 and
   boot state1 preserves all 31 GPRs, restores PSW and clears ISPR. This does not establish physical
   interrupt timing or the pending-FPI path. Save r6/EIPC/EIPSW; read EIIC into r6; EI; save r1..lp;
   call 748; restore GPRs; DI; restore EIPSW/EIPC/r6; EIRET. Full execution preserves all 31 GPRs
   and stack canaries; restores PSW and clears ISPR. Pending-FPI and nested-interrupt behavior are
   not exercised. */

void f33_boot_eiint_context(void)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  undefined4 in_r6;
  uint extraout_r6;
  undefined4 in_r7;
  undefined4 extraout_r7;
  undefined4 in_r8;
  undefined4 extraout_r8;
  undefined4 in_r9;
  undefined4 extraout_r9;
  uint in_EIPSW;
  uint in_PSW;
  uint uVar4;
  uint in_FPEC;
  uint in_EIIC;
  uint in_RBASE;
  uint in_EBASE;
  uint in_FPIPR;
  uint in_ISPR;
  uint in_INTCFG;
  
  uVar4 = in_PSW & 0xffffffd0;
  if ((in_FPEC & 1) != 0) {
    uVar1 = in_FPIPR & 0x1f;
    if (0xf < uVar1) {
      uVar1 = 0x10;
    }
    uVar2 = uVar1;
    if (0xf < uVar1) {
      uVar2 = 0xf;
    }
    uVar3 = PMR;
    if ((((uVar3 & 1 << uVar2) == 0) && ((in_ISPR & (1 << uVar1 + 1) - 1U & 0xffff) == 0)) &&
       ((in_PSW & 0x80) == 0)) {
      in_FPEC = 0;
      uVar4 = 0x40;
      uVar1 = in_EBASE;
      if ((in_PSW & 0x8000) == 0) {
        uVar1 = in_RBASE;
      }
      (*(int (*)())camry_host_ptr((uint32_t)((uVar1 & 0xfffffe00) + 0x70)))();
      in_EIIC = extraout_r6;
      in_r7 = extraout_r7;
      in_r8 = extraout_r8;
      in_r9 = extraout_r9;
    }
  }
  __enable_irq();
  f33_boot_dispatch_eiic(in_EIIC);
  __disable_irq();
  if (((uVar4 >> 6 & 1) == 0) && ((in_INTCFG & 1) == 0)) {
    in_ISPR = in_ISPR & in_ISPR - 1;
  }
  if ((in_FPEC & 1) != 0) {
    uVar4 = in_FPIPR & 0x1f;
    if (0xf < uVar4) {
      uVar4 = 0x10;
    }
    uVar1 = uVar4;
    if (0xf < uVar4) {
      uVar1 = 0xf;
    }
    uVar2 = PMR;
    if ((((uVar2 & 1 << uVar1) == 0) && ((in_ISPR & (1 << uVar4 + 1) - 1U & 0xffff) == 0)) &&
       ((in_EIPSW & 0xa0) == 0)) {
      if (((in_EIPSW & 0xbfffffbf) >> 0xf & 1) == 0) {
        in_EBASE = in_RBASE;
      }
      (*(int (*)())camry_host_ptr((uint32_t)((in_EBASE & 0xfffffe00) + 0x70)))(in_r6,in_r7,in_r8,in_r9);
    }
  }
  return;
}



/* Traverse eight-byte records from TP; call the first handler whose cause equals eiic or FFFFFFFF.
   The sentinel terminates the search, not the end of the surrounding data region. Executed matches
   1087/10C1 and defaults 27F/FFFFFFFF against the exact image. Walk eight-byte EIIC/handler records
   from TP=869C until exact cause or FFFFFFFF sentinel; call selected handler. Eight records include
   the default. Cause27F selects default1EA4 despite a following 27F/32A0 pair; that pair is not
   part of this traversal. Boot timer1087 executes through 1E44. No physical interrupt routing
   experiment. */

void f33_boot_dispatch_eiic(uint eiic)

{
  int iVar1;
  
  iVar1 = 0;
  while( true ) {
    if ((f33_boot_interrupt_dispatch[iVar1].eiic == 0xffffffff) ||
       (f33_boot_interrupt_dispatch[iVar1].eiic == eiic)) break;
    iVar1 = iVar1 + 1;
  }
  (*(int (*)())f33_boot_interrupt_dispatch[iVar1].handler)();
  return;
}



void FUN_00000770(void)

{
  f33_boot_diagnostic_enable_from_handoff();
  f33_boot_diagnostic_initialize_from_handoff();
  return;
}



void FUN_00000780(void)

{
  f33_boot_diagnostic_timer_services();
  return;
}



void FUN_0000078c(void)

{
  f33_boot_diagnostic_foreground();
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_798(void)

{
  return;
}



void FUN_0000079a(void)

{
  undefined4 uVar1;
  
  Ramffc60408 = 3;
  Ramffc6040c = 3;
  Ramffc61408 = 1;
  Ramffc6140c = 1;
  uVar1 = Ramffc61450;
  __synchronize();
  return;
}



void FUN_000007b6(void)

{
  undefined4 uVar1;
  int iVar2;
  
  Ramffc65408 = 0xffffffff;
  Ramffc6540c = 0xf;
  uVar1 = Ramffc6540c;
  __synchronize();
  Ramffc65604 = 0x4000;
  uVar1 = Ramffc65604;
  __synchronize();
  do {
    Ramffc65400 = 0x4000;
    uVar1 = Ramffc65400;
    __synchronize();
    iVar2 = Ramffc65400;
  } while (iVar2 != 0);
  do {
    Ramffc65404 = 2;
    uVar1 = Ramffc65404;
    __synchronize();
    iVar2 = Ramffc65404;
  } while (iVar2 != 2);
  return;
}



void FUN_00000802(void)

{
  uint uVar1;
  
  UCFSERSTCLR = 0xf;
  UCFDERSTCLR = 1;
  uVar1 = UCFDERSTCLR;
  __synchronize();
  CFSTSTCTL_VCI2CFBA = 0x4000;
  CFSTSTCTL_PE1 = 0x4000;
  uVar1 = CFSTSTCTL_PE1;
  __synchronize();
  do {
    CFAPCTL = 0x4000;
    uVar1 = CFAPCTL;
    __synchronize();
    uVar1 = CFAPCTL;
  } while (uVar1 != 0);
  do {
    CFECCCTL_VCI2CFBA = 0x4000;
    uVar1 = CFECCCTL_VCI2CFBA;
    __synchronize();
    uVar1 = CFECCCTL_VCI2CFBA;
  } while (uVar1 != 0);
  do {
    CFECCCTL_PE1 = 0x4000;
    uVar1 = CFECCCTL_PE1;
    __synchronize();
    uVar1 = CFECCCTL_PE1;
  } while (uVar1 != 0);
  do {
    UCFERRINT = 6;
    uVar1 = UCFERRINT;
    __synchronize();
    uVar1 = UCFERRINT;
  } while (uVar1 != 6);
  return;
}



void FUN_00000880(void)

{
  uint uVar1;
  undefined4 uVar2;
  
  DFERSTC = 1;
  uVar1 = DFERSTC;
  __synchronize();
  DAT_ffc5b010 = 1;
  uVar2 = DAT_ffc5b010;
  __synchronize();
  DFTSTCTL = 0x4000;
  uVar1 = DFTSTCTL;
  __synchronize();
  do {
    DFECCCTL = 0x4000;
    uVar1 = DFECCCTL;
    __synchronize();
    uVar1 = DFECCCTL;
  } while (uVar1 != 0);
  do {
    DFERRINT = 0;
    uVar1 = DFERRINT;
    __synchronize();
    uVar1 = DFERRINT;
  } while (uVar1 != 0);
  return;
}



void FUN_000008c8(void)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  Ramffc64004 = 0xffffffff;
  Ramffc64008 = 1;
  uVar1 = Ramffc64008;
  __synchronize();
  Ramffc64104 = 0x4000;
  uVar1 = Ramffc64104;
  __synchronize();
  Ramffc64100 = 0x4000;
  Ramffc64200 = 0x4000;
  Ramffc64e00 = 0x4000;
  uVar1 = Ramffc64e00;
  __synchronize();
  iVar2 = Ramffc64100;
  iVar4 = Ramffc64200;
  iVar3 = Ramffc64e00;
  while (iVar2 != 0) {
    Ramffc64100 = 0x4000;
    uVar1 = Ramffc64100;
    __synchronize();
    iVar2 = Ramffc64100;
  }
  while (iVar4 != 0) {
    Ramffc64200 = 0x4000;
    uVar1 = Ramffc64200;
    __synchronize();
    iVar4 = Ramffc64200;
  }
  while (iVar3 != 0) {
    Ramffc64e00 = 0x4000;
    uVar1 = Ramffc64e00;
    iVar3 = Ramffc64e00;
  }
  do {
    Ramffc64000 = 0x22;
    uVar1 = Ramffc64000;
    __synchronize();
    iVar2 = Ramffc64000;
  } while (iVar2 != 0x22);
  return;
}



void FUN_0000096e(void)

{
  undefined4 uVar1;
  int iVar2;
  
  Ramffc62c08 = 1;
  Ramffc62c00 = 0x4000;
  Ramffc62c04 = 0x20;
  Ramffc63408 = 1;
  Ramffc63400 = 0x4000;
  Ramffc63404 = 2;
  Ramffc66008 = 1;
  Ramffc66000 = 0x4000;
  Ramffc66004 = 0x22;
  Ramffc66408 = 1;
  Ramffc66400 = 0x4000;
  Ramffc66404 = 2;
  Ramffc67008 = 1;
  Ramffc67004 = 2;
  Ramffc67408 = 1;
  Ramffc67404 = 2;
  Ramffc67808 = 1;
  Ramffc67804 = 2;
  Ramffc68408 = 1;
  Ramffc68404 = 2;
  Ramffc6a008 = 1;
  Ramffc6a000 = 0x4000;
  Ramffc6a004 = 2;
  Ramffc6c008 = 1;
  Ramffc6c000 = 0x4000;
  Ramffc6c004 = 0x22;
  __synchronize();
  Ramffddd808 = 1;
  Ramffddd800 = 0x4000;
  Ramffddd804 = 0x22;
  uVar1 = Ramffddd804;
  __synchronize();
  Ramfff94808 = 1;
  Ramfff94800 = 0x4000;
  Ramfff94804 = 0x22;
  uVar1 = Ramfff94804;
  __synchronize();
  Ramffc40808 = 1;
  Ramffc40800 = 0x4000;
  Ramffc40804 = 0x22;
  uVar1 = Ramffc40804;
  __synchronize();
  Ramffff80a0 = 0x40000000;
  uVar1 = Ramffff80a0;
  __synchronize();
  iVar2 = Ramffc62c00;
  while (iVar2 != 0) {
    Ramffc62c00 = 0x4000;
    iVar2 = Ramffc62c00;
    __synchronize();
  }
  iVar2 = Ramffc62c04;
  while (iVar2 != 0x20) {
    Ramffc62c04 = 0x20;
    iVar2 = Ramffc62c04;
    __synchronize();
  }
  iVar2 = Ramffc63400;
  while (iVar2 != 0) {
    Ramffc63400 = 0x4000;
    iVar2 = Ramffc63400;
    __synchronize();
  }
  iVar2 = Ramffc63404;
  while (iVar2 != 2) {
    Ramffc63404 = 2;
    iVar2 = Ramffc63404;
    __synchronize();
  }
  iVar2 = Ramffc66000;
  while (iVar2 != 0) {
    Ramffc66000 = 0x4000;
    iVar2 = Ramffc66000;
    __synchronize();
  }
  iVar2 = Ramffc66004;
  while (iVar2 != 0x22) {
    Ramffc66004 = 0x22;
    iVar2 = Ramffc66004;
    __synchronize();
  }
  iVar2 = Ramffc66400;
  while (iVar2 != 0) {
    Ramffc66400 = 0x4000;
    iVar2 = Ramffc66400;
    __synchronize();
  }
  iVar2 = Ramffc66404;
  while (iVar2 != 2) {
    Ramffc66404 = 2;
    iVar2 = Ramffc66404;
    __synchronize();
  }
  iVar2 = Ramffc67004;
  while (iVar2 != 2) {
    Ramffc67004 = 2;
    iVar2 = Ramffc67004;
    __synchronize();
  }
  iVar2 = Ramffc67404;
  while (iVar2 != 2) {
    Ramffc67404 = 2;
    iVar2 = Ramffc67404;
    __synchronize();
  }
  iVar2 = Ramffc67804;
  while (iVar2 != 2) {
    Ramffc67804 = 2;
    iVar2 = Ramffc67804;
    __synchronize();
  }
  iVar2 = Ramffc68404;
  while (iVar2 != 2) {
    Ramffc68404 = 2;
    iVar2 = Ramffc68404;
    __synchronize();
  }
  iVar2 = Ramffc6a000;
  while (iVar2 != 0) {
    Ramffc6a000 = 0x4000;
    iVar2 = Ramffc6a000;
    __synchronize();
  }
  iVar2 = Ramffc6a004;
  while (iVar2 != 2) {
    Ramffc6a004 = 2;
    iVar2 = Ramffc6a004;
    __synchronize();
  }
  iVar2 = Ramffc6c000;
  while (iVar2 != 0) {
    Ramffc6c000 = 0x4000;
    iVar2 = Ramffc6c000;
    __synchronize();
  }
  iVar2 = Ramffc6c004;
  while (iVar2 != 0x22) {
    Ramffc6c004 = 0x22;
    iVar2 = Ramffc6c004;
    __synchronize();
  }
  iVar2 = Ramffddd800;
  while (iVar2 != 0) {
    Ramffddd800 = 0x4000;
    iVar2 = Ramffddd800;
    __synchronize();
  }
  iVar2 = Ramffddd804;
  while (iVar2 != 0x22) {
    Ramffddd804 = 0x22;
    iVar2 = Ramffddd804;
    __synchronize();
  }
  iVar2 = Ramfff94800;
  while (iVar2 != 0) {
    Ramfff94800 = 0x4000;
    iVar2 = Ramfff94800;
    __synchronize();
  }
  iVar2 = Ramfff94804;
  while (iVar2 != 0x22) {
    Ramfff94804 = 0x22;
    iVar2 = Ramfff94804;
    __synchronize();
  }
  iVar2 = Ramffc40800;
  while (iVar2 != 0) {
    Ramffc40800 = 0x4000;
    iVar2 = Ramffc40800;
    __synchronize();
  }
  iVar2 = Ramffc40804;
  while (iVar2 != 0x22) {
    Ramffc40804 = 0x22;
    iVar2 = Ramffc40804;
    __synchronize();
  }
  return;
}



void FUN_00000c52(void)

{
  undefined4 uVar1;
  
  Ramffc71100 = 0x610;
  Ramffc71104 = 0x8000;
  uVar1 = Ramffc71104;
  __synchronize();
  Ramffc71200 = 0x610;
  Ramffc71204 = 0x8000;
  uVar1 = Ramffc71204;
  __synchronize();
  Ramffc70000 = 0x610;
  Ramffc70004 = 0x8000;
  uVar1 = Ramffc70004;
  __synchronize();
  Ramffc70040 = 0x610;
  Ramffc70044 = 0x8000;
  uVar1 = Ramffc70044;
  __synchronize();
  Ramffc70080 = 0x610;
  Ramffc70084 = 0x8000;
  uVar1 = Ramffc70084;
  __synchronize();
  Ramffc700c0 = 0x610;
  Ramffc700c4 = 0x8000;
  uVar1 = Ramffc700c4;
  __synchronize();
  return;
}



void FUN_00000c9a(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  
  iVar5 = 0;
  do {
    iVar4 = iVar5 * 0x40;
    iVar2 = iVar5 + 1;
    (*((undefined2 *)camry_host_ptr((uint32_t)(iVar4 + -0x3ebffc)))) = 0;
    (*((undefined2 *)camry_host_ptr((uint32_t)(iVar4 + -0x3ec000)))) = 0;
    iVar1 = iVar5 + -5;
    (*((undefined2 *)camry_host_ptr((uint32_t)(iVar4 + -0x3efff0)))) = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x87a0u + (uint32_t)((short)iVar5 * 0x18) * 2u))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(iVar4 + -0x3effec)))) = 0;
    (*((undefined2 *)camry_host_ptr((uint32_t)(iVar4 + -0x3ebff8)))) = 0;
    iVar5 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  DAT_ffc24004 = 0;
  DAT_ffc24000 = 0;
  DAT_ffc20010 = (char)DAT_000088c0;
  DAT_ffc20014 = 0;
  DAT_ffc34000 = 0;
  DAT_ffc34020 = 0;
  DAT_ffc34024 = 0;
  DAT_ffc34028 = 0;
  DAT_ffc3402c = 0;
  DAT_ffc34030 = 0;
  DAT_ffc34034 = 0;
  DAT_ffc34038 = 0;
  DAT_ffc3403c = 0;
  DAT_ffc34040 = 0;
  DAT_ffc34044 = 0;
  DAT_ffc34048 = 0;
  DAT_ffc3404c = 0;
  DAT_ffc34050 = 0;
  DAT_ffc34060 = 0;
  DAT_ffc34064 = 0;
  DAT_ffc34068 = 0;
  DAT_ffc3406c = 0;
  DAT_ffc34070 = 0;
  DAT_ffc34074 = 0;
  DAT_ffc34080 = 0;
  DAT_ffc34084 = 0;
  iVar5 = 0;
  do {
    iVar2 = iVar5 + 1;
    (*((undefined1 *)camry_host_ptr((uint32_t)(iVar5 * 0x100 + -0x3d0000)))) = 0;
    iVar1 = iVar5 + -0x2b;
    (*((undefined2 *)camry_host_ptr((uint32_t)(iVar5 * 0x100 + -0x3cfffc)))) = 0;
    iVar5 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  iVar5 = 0;
  do {
    iVar2 = iVar5 + 1;
    *(undefined4 *)(((undefined *)camry_host_ptr(0xfff89120u)) + iVar5 * 8) = 2;
    iVar1 = iVar5 + -0xc;
    iVar5 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  iVar5 = 0;
  do {
    iVar1 = (int)(short)iVar5;
    iVar2 = iVar5 * 0x40;
    (*((undefined2 *)camry_host_ptr((uint32_t)(iVar2 + -0x3ebff4)))) = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x87a2u + (uint32_t)(iVar1 * 0x18) * 2u))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(iVar2 + -0x3ebff0)))) = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x87a4u + (uint32_t)(iVar1 * 0x18) * 2u))));
    if (iVar5 != 5) {
      (*((undefined2 *)camry_host_ptr((uint32_t)(iVar2 + -0x3ebfd4)))) = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x87a6u + (uint32_t)(iVar1 * 0x18) * 2u))));
    }
    iVar3 = iVar5 + 1;
    iVar4 = iVar5 + -5;
    (*((undefined4 *)camry_host_ptr((uint32_t)(iVar2 + -0x3ebfe8)))) = (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x87a8u + (uint32_t)(iVar1 * 0xc) * 4u))));
    (*((undefined4 *)camry_host_ptr((uint32_t)(iVar2 + -0x3ebfd8)))) = (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x87acu + (uint32_t)(iVar1 * 0xc) * 4u))));
    (*((undefined4 *)camry_host_ptr((uint32_t)(iVar2 + -0x3ebfec)))) = (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x87b0u + (uint32_t)(iVar1 * 0xc) * 4u))));
    (*((undefined4 *)camry_host_ptr((uint32_t)(iVar2 + -0x3ebfc4)))) = (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x87b4u + (uint32_t)(iVar1 * 0xc) * 4u))));
    (*((undefined4 *)camry_host_ptr((uint32_t)(iVar2 + -0x3effd0)))) = (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x87b8u + (uint32_t)(iVar1 * 0xc) * 4u))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(iVar2 + -0x3effe8)))) = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x87bcu + (uint32_t)(iVar1 * 0x18) * 2u))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(iVar2 + -0x3effe4)))) = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x87beu + (uint32_t)(iVar1 * 0x18) * 2u))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(iVar2 + -0x3effd8)))) = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x87c0u + (uint32_t)(iVar1 * 0x18) * 2u))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(iVar2 + -0x3ebff8)))) = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x87c2u + (uint32_t)(iVar1 * 0x18) * 2u))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(iVar2 + -0x3f0000)))) = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x87c4u + (uint32_t)(iVar1 * 0x18) * 2u))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(iVar2 + -0x3effec)))) = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x87c6u + (uint32_t)(iVar1 * 0x18) * 2u))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(iVar2 + -0x3efff0)))) = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x87c8u + (uint32_t)(iVar1 * 0x18) * 2u))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(iVar2 + -0x3ec000)))) = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x87cau + (uint32_t)(iVar1 * 0x18) * 2u))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(iVar2 + -0x3ebffc)))) = *(undefined2 *)(((undefined *)camry_host_ptr(0x87ccu)) + iVar1 * 0x30);
    iVar5 = iVar3;
  } while (((iVar4 < 0) || (iVar3 < 0)));
  DAT_ffc2400c = (char)DAT_000088c2;
  DAT_ffc24010 = (char)DAT_000088c4;
  DAT_ffc2402c = (char)DAT_000088c6;
  Ramffc24018 = DAT_000088c8;
  Ramffc24028 = DAT_000088cc;
  Ramffc24014 = DAT_000088d0;
  DAT_ffc2001c = (char)DAT_000088de;
  DAT_ffc20000 = (char)DAT_000088e4;
  DAT_ffc20014 = (char)DAT_000088e6;
  DAT_ffc20010 = (char)DAT_000088e8;
  DAT_ffc24000 = (char)DAT_000088ea;
  DAT_ffc24004 = (char)DAT_000088ec;
  return;
}



void FUN_00000e54(void)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  uchar uVar4;
  
  uVar1 = Ramffc0a000;
  DAT_febffc00 = 0;
  uVar2 = Ramffc0a004;
  DAT_febffc04 = 0;
  DAT_febffc08 = 0;
  DAT_febffc0c = 0;
  DAT_febffc10 = 0;
  DAT_febffc14 = 0;
  uVar3 = Ramffc0a008;
  if ((uVar2 == (uVar1 ^ 0x55555555)) && (uVar3 == (uVar1 ^ 0xaaaaaaaa))) {
    DAT_febffc00 = ECMMESSTR0;
    DAT_febffc04 = ECMCESSTR0;
    DAT_febffc08 = ECMMESSTR1;
    DAT_febffc0c = ECMCESSTR1;
    DAT_febffc10 = ECMMESSTR2;
    DAT_febffc14 = ECMCESSTR2;
  }
  ECMPCMD1 = 0xa5;
  ECMESSTC0 = 0xffffffff;
  ECMESSTC0 = 0;
  ECMESSTC0 = 0xffffffff;
  uVar4 = ECMPS;
  __synchronize();
  ECMPCMD1 = 0xa5;
  ECMESSTC1 = 0xffffffff;
  ECMESSTC1 = 0;
  ECMESSTC1 = 0xffffffff;
  uVar4 = ECMPS;
  __synchronize();
  ECMPCMD1 = 0xa5;
  ECMESSTC2 = 0x7fffffff;
  ECMESSTC2 = 0x80000000;
  ECMESSTC2 = 0x7fffffff;
  uVar4 = ECMPS;
  __synchronize();
  DAT_febffc80 = DAT_febffc00 ^ 0x55555555;
  DAT_febffc84 = DAT_febffc04 ^ 0x55555555;
  DAT_febffc88 = DAT_febffc08 ^ 0x55555555;
  DAT_febffc8c = DAT_febffc0c ^ 0x55555555;
  DAT_febffc90 = DAT_febffc10 ^ 0x55555555;
  DAT_febffd00 = DAT_febffc00 ^ 0xaaaaaaaa;
  DAT_febffd0c = DAT_febffc0c ^ 0xaaaaaaaa;
  DAT_febffc94 = DAT_febffc14 ^ 0x55555555;
  DAT_febffd04 = DAT_febffc04 ^ 0xaaaaaaaa;
  DAT_febffd08 = DAT_febffc08 ^ 0xaaaaaaaa;
  DAT_febffd10 = DAT_febffc10 ^ 0xaaaaaaaa;
  DAT_febffd14 = DAT_febffc14 ^ 0xaaaaaaaa;
  return;
}



void FUN_00000f80(void)

{
  uchar uVar1;
  uint uVar2;
  uint uVar3;
  byte bVar4;
  
  ECMPEM = 3;
  ECMPCMD1 = 0xa5;
  ECMEMK0 = 0xffffffe1;
  ECMEMK0 = 0x1e;
  ECMEMK0 = 0xffffffe1;
  uVar1 = ECMPS;
  ECMPCMD1 = 0xa5;
  uVar2 = 0;
  ECMEMK1 = 0xffffffff;
  ECMEMK1 = 0;
  ECMEMK1 = 0xffffffff;
  uVar1 = ECMPS;
  ECMPCMD1 = 0xa5;
  ECMEMK2 = 0x3fffffff;
  ECMEMK2 = 0xc0000000;
  ECMEMK2 = 0x3fffffff;
  uVar1 = ECMPS;
  ECMPCMD1 = 0xa5;
  ECMMICFG0 = 0;
  ECMMICFG0 = 0xffffffff;
  ECMMICFG0 = 0;
  uVar1 = ECMPS;
  ECMPCMD1 = 0xa5;
  ECMMICFG1 = 0;
  ECMMICFG1 = 0xffffffff;
  ECMMICFG1 = 0;
  uVar1 = ECMPS;
  ECMPCMD1 = 0xa5;
  ECMMICFG2 = 0;
  ECMMICFG2 = 0xffffffff;
  ECMMICFG2 = 0;
  uVar1 = ECMPS;
  ECMPCMD1 = 0xa5;
  ECMNMICFG0 = 0;
  ECMNMICFG0 = 0xffffffff;
  ECMNMICFG0 = 0;
  uVar1 = ECMPS;
  ECMPCMD1 = 0xa5;
  ECMNMICFG1 = 0;
  ECMNMICFG1 = 0xffffffff;
  ECMNMICFG1 = 0;
  uVar1 = ECMPS;
  ECMPCMD1 = 0xa5;
  ECMNMICFG2 = 0;
  ECMNMICFG2 = 0xffffffff;
  ECMNMICFG2 = 0;
  uVar1 = ECMPS;
  ECMPCMD1 = 0xa5;
  ECMIRCFG0 = 0;
  ECMIRCFG0 = 0xffffffff;
  ECMIRCFG0 = 0;
  uVar1 = ECMPS;
  ECMPCMD1 = 0xa5;
  ECMIRCFG1 = 0;
  ECMIRCFG1 = 0xffffffff;
  ECMIRCFG1 = 0;
  uVar1 = ECMPS;
  ECMPCMD1 = 0xa5;
  ECMIRCFG2 = 0;
  ECMIRCFG2 = 0xffffffff;
  ECMIRCFG2 = 0;
  uVar1 = ECMPS;
  __synchronize();
  ECMMPCMD0 = 0xa5;
  ECMMECLR = '\x01';
  ECMMECLR = 0xfe;
  ECMMECLR = '\x01';
  uVar1 = ECMPS;
  __synchronize();
  bVar4 = 0;
  do {
    uVar3 = 0x80000000;
    if ((int)uVar2 < 0) break;
    uVar2 = ECMMESSTR2;
    bVar4 = bVar4 + 1;
  } while (bVar4 < 0x1f);
  ECMCPCMD0 = 0xa5;
  ECMCECLR = '\x01';
  ECMCECLR = 0xfe;
  ECMCECLR = '\x01';
  uVar1 = ECMPS;
  __synchronize();
  bVar4 = 0;
  do {
    if (-1 < (int)uVar3) break;
    uVar3 = ECMCESSTR2;
    bVar4 = bVar4 + 1;
  } while (bVar4 < 0x1f);
  ECMPEM = 0;
  __synchronize();
  return;
}



void FUN_000010c4(void)

{
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}



void FUN_000010c6(void)

{
  byte bVar1;
  uint uVar2;
  
  CLKD3DIV = 0;
  CKSC3C = 4;
  uVar2 = CKSC3C;
  __synchronize();
  uVar2 = CKSC3S;
  bVar1 = 0;
  while ((uVar2 != 4 && (bVar1 < 100))) {
    uVar2 = CKSC3S;
    bVar1 = bVar1 + 1;
    __synchronize();
  }
  uVar2 = CLKD3STAT;
  bVar1 = 0;
  while (((uVar2 & 2) == 0 && (bVar1 < 100))) {
    bVar1 = bVar1 + 1;
    __synchronize();
    uVar2 = CLKD3STAT;
  }
  if ((uVar2 & 2) == 2) {
    CLKD3DIV = 0x50;
    uVar2 = CLKD3DIV;
    __synchronize();
  }
  else {
    FUN_000010c4();
  }
  uVar2 = CLKD3STAT;
  bVar1 = 0;
  while (((uVar2 >> 1 & 1) == 0 && (bVar1 < 100))) {
    bVar1 = bVar1 + 1;
    __synchronize();
    uVar2 = CLKD3STAT;
  }
  return;
}



undefined4 FUN_0000115a(void)

{
  uint uVar1;
  uint uVar2;
  uchar uVar3;
  undefined4 uVar4;
  
  uVar2 = UCFDERSTR;
  UCFDERSTCLR = 1;
  uVar4 = 0;
  uVar1 = UCFDERSTCLR;
  __synchronize();
  ECMPCMD1 = 0xa5;
  ECMESSTC0 = 0x80000;
  ECMESSTC0 = 0xfff7ffff;
  ECMESSTC0 = 0x80000;
  uVar3 = ECMPS;
  __synchronize();
  if (((uVar2 & 1) != 0) || ((uVar2 >> 2 & 1) != 0)) {
    uVar4 = 1;
  }
  return uVar4;
}



/* Return0 only after a successful pair of descriptor-backed CRC checks481A(1),481A(0) plus115A
   CodeFlashECC snapshot/clear,then bothFFE00 and17E00 markerwords equal5AA5A55A. Each stage permits
   at most3 attempts;stage2 is reached only afterstage1 success. Return1 otherwise. HardwareCRC/ECC
   feedback is an external dependency;no fixed diagnostic startup interval is provided. */

uint f33_boot_validate_application_images(void)

{
  bool bVar1;
  uint uVar2;
  uint uVar3;
  int iVar4;
  int iVar5;
  uint uVar6;
  
  uVar6 = 0;
  while( true ) {
    uVar2 = f33_boot_validate_crc_region(1);
    uVar3 = f33_boot_validate_crc_region(0);
    if ((uVar2 == 0) && (uVar3 == 0)) {
      bVar1 = false;
    }
    else {
      bVar1 = true;
    }
    iVar4 = FUN_0000115a();
    if ((!bVar1) && (iVar4 == 0)) break;
    uVar6 = uVar6 + 1;
    if (2 < uVar6) {
      return 1;
    }
  }
  uVar6 = 0;
  while( true ) {
    iVar4 = FUN_00006c5a(((int *)camry_host_ptr((uint32_t)(0xffe00))));
    iVar5 = FUN_00006c5a(((undefined *)camry_host_ptr(0x17e00u)));
    if ((iVar4 == 0) && (iVar5 == 0)) break;
    uVar6 = uVar6 + 1;
    if (2 < uVar6) {
      return 1;
    }
  }
  return 0;
}



void FUN_00001206(void)

{
  undefined2 uVar1;
  
  Ramfffee982 = 0;
  Ramfffee988 = 0;
  Ramfffee980 = 0;
  uVar1 = Ramfffee980;
  __synchronize();
  __synchronize();
  return;
}



void FUN_0000121a(void)

{
  undefined4 uVar1;
  
  Ramffff8000 = 1;
  uVar1 = Ramffff8000;
  __synchronize();
  return;
}



void FUN_00001228(void)

{
  uchar uVar1;
  uint uVar2;
  
  ECMPEM = 3;
  uVar2 = ECMPEM;
  __synchronize();
  ECMPCMD1 = 0xa5;
  ECMEMK0 = 0xffffffe1;
  ECMEMK0 = 0x1e;
  ECMEMK0 = 0xffffffe1;
  uVar1 = ECMPS;
  ECMPCMD1 = 0xa5;
  ECMEMK1 = 0xffffffff;
  ECMEMK1 = 0;
  ECMEMK1 = 0xffffffff;
  uVar1 = ECMPS;
  ECMPCMD1 = 0xa5;
  ECMEMK2 = 0x3fffffff;
  ECMEMK2 = 0xc0000000;
  ECMEMK2 = 0x3fffffff;
  uVar1 = ECMPS;
  ECMPCMD1 = 0xa5;
  ECMMICFG0 = 0;
  ECMMICFG0 = 0xffffffff;
  ECMMICFG0 = 0;
  uVar1 = ECMPS;
  ECMPCMD1 = 0xa5;
  ECMMICFG1 = 0;
  ECMMICFG1 = 0xffffffff;
  ECMMICFG1 = 0;
  uVar1 = ECMPS;
  ECMPCMD1 = 0xa5;
  ECMMICFG2 = 0;
  ECMMICFG2 = 0xffffffff;
  ECMMICFG2 = 0;
  uVar1 = ECMPS;
  ECMPCMD1 = 0xa5;
  ECMNMICFG0 = 0;
  ECMNMICFG0 = 0xffffffff;
  ECMNMICFG0 = 0;
  uVar1 = ECMPS;
  ECMPCMD1 = 0xa5;
  ECMNMICFG1 = 0;
  ECMNMICFG1 = 0xffffffff;
  ECMNMICFG1 = 0;
  uVar1 = ECMPS;
  ECMPCMD1 = 0xa5;
  ECMNMICFG2 = 0;
  ECMNMICFG2 = 0xffffffff;
  ECMNMICFG2 = 0;
  uVar1 = ECMPS;
  ECMPCMD1 = 0xa5;
  ECMIRCFG0 = 0;
  ECMIRCFG0 = 0xffffffff;
  ECMIRCFG0 = 0;
  uVar1 = ECMPS;
  ECMPCMD1 = 0xa5;
  ECMIRCFG1 = 0;
  ECMIRCFG1 = 0xffffffff;
  ECMIRCFG1 = 0;
  uVar1 = ECMPS;
  ECMPCMD1 = 0xa5;
  ECMIRCFG2 = 0;
  ECMIRCFG2 = 0xffffffff;
  ECMIRCFG2 = 0;
  uVar1 = ECMPS;
  ECMPEM = 0;
  uVar2 = ECMPEM;
  __synchronize();
  ECMPCMD1 = 0xa5;
  ECMESSTC0 = 0xffffffff;
  ECMESSTC0 = 0;
  ECMESSTC0 = 0xffffffff;
  uVar1 = ECMPS;
  ECMPCMD1 = 0xa5;
  ECMESSTC1 = 0xffffffff;
  ECMESSTC1 = 0;
  ECMESSTC1 = 0xffffffff;
  uVar1 = ECMPS;
  ECMPCMD1 = 0xa5;
  ECMESSTC2 = 0x7fffffff;
  ECMESSTC2 = 0x80000000;
  ECMESSTC2 = 0x7fffffff;
  uVar1 = ECMPS;
  __synchronize();
  return;
}



/* Initialize resident diagnostic/service mode with stateFEBF2904=1 and2900=0,then orderedresident
   lower/service/flash/timer setup.1CA0 startsTAUJ0CH2. State1 prevents existing14A2 timer callback
   services until main137A publishesstate2. Does not validate or launch application. */

void f33_boot_resident_initialize(void)

{
  DAT_febf2904 = 1;
  DAT_febf2900 = 0;
  FUN_000016f2();
  FUN_0000121a();
  FUN_00001228();
  FUN_000017c8();
  FUN_00003b3c();
  FUN_000035bc();
  f33_boot_reset_flash_operation_queue();
  f33_fill_constant_block_1f24();
  FUN_000047ac();
  f33_boot_reset_region_crc_verification();
  FUN_00001ca0();
  FUN_00000770();
  return;
}



/* Publish resident stateFEBF2904=2 before invoking078C,4428,479A,4874 once. This is the body of1398
   resident loop and admits existingtimer callback14A2 services;it is not applicationCH3 foreground.
   Native bounded foreground runs with transport disabled verify queue completion/cancellation and
   independent invalid CRC retention; not full resident startup or live hardware. */

void f33_boot_resident_service_iteration(void)

{
  DAT_febf2904 = 2;
  FUN_0000078c();
  f33_boot_advance_flash_operation();
  FUN_0000479a();
  f33_boot_advance_region_crc_verification();
  return;
}



/* Nonreturning resident bootloader root reached by cold-start validation failure or explicit148E
   programming handoff. Run1338 initialization,restore priority mask with7244(0),EI,then
   repeatedly137A. Application66062 andapplicationvector/table ownership are not entered here. */

void f33_boot_resident_main(void)

{
  uint uVar1;
  uint uVar2;
  uint in_PSW;
  uint in_FPEC;
  uint in_RBASE;
  uint in_EBASE;
  uint in_FPIPR;
  uint in_ISPR;
  
  f33_boot_resident_initialize();
  FUN_00007244(0);
  if ((in_FPEC & 1) != 0) {
    in_FPIPR = in_FPIPR & 0x1f;
    if (0xf < in_FPIPR) {
      in_FPIPR = 0x10;
    }
    uVar1 = in_FPIPR;
    if (0xf < in_FPIPR) {
      uVar1 = 0xf;
    }
    uVar2 = PMR;
    if ((((uVar2 & 1 << uVar1) == 0) && ((in_ISPR & (1 << in_FPIPR + 1) - 1U & 0xffff) == 0)) &&
       ((in_PSW & 0x80) == 0)) {
      if (((in_PSW & 0xbfffffdf) >> 0xf & 1) == 0) {
        in_EBASE = in_RBASE;
      }
      (*(int (*)())camry_host_ptr((uint32_t)((in_EBASE & 0xfffffe00) + 0x70)))();
    }
  }
  __enable_irq();
  do {
    f33_boot_resident_service_iteration();
  } while( true );
}



/* Run port/config,retainedECM snapshot,ECM reset and boundedclock controls before119E validates
   both image regions/ECC/magic. Return0 calls the full-width application entry pointer atFFDB8
   (registered20880) with no diagnostic dwell or local pointer-range guard. Failure resetsINTC
   controls,sets2908=FF andeight subsequentwords=FFFFFFFF,then enters resident1398. Any application
   return halts1402. This branch is distinct from deliberate9F00 programming transfer. */

void f33_boot_select_application_or_resident(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint32_t puVar4;
  uint uVar5;
  
  puVar4 = 0xfebf9800u;
  FUN_00000c9a();
  FUN_00000e54();
  FUN_00000f80();
  FUN_000010c6();
  uVar5 = f33_boot_validate_application_images();
  if (uVar5 == 0) {
    (*(int (*)())camry_host_ptr((uint32_t)(PTR_f33_application_entry_000ffdb8)))();
  }
  else {
    FUN_00001206();
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar4 + -0x6ef8)))) = 0xff;
    iVar3 = 1;
    do {
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar4 + iVar3 * 4 + -0x6ef8)))) = 0xffffffff;
      iVar2 = iVar3 + 1;
      iVar1 = iVar3 + -8;
      iVar3 = iVar2;
    } while (((iVar1 < 0) || (iVar2 < 0)));
    f33_boot_resident_main();
  }
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}



/* Called directly by reset assembly067C after first7000..7FFF clear and CPU setup. Perform
   ordered79A/7B6/802/880/8C8/96E/C52 hardware controls;SYNCM;preserve the empty reversed-bound
   first loop;clear established upper LocalRAM andGlobalRAM intervals;setEEPRDCYCL3;call13B0.
   Earlier hardware readback loops have no software timeout. RAM-clear extents/tests remain77.17
   owner. */

void f33_boot_hardware_ram_init_and_select_image(void)

{
  undefined4 *puVar1;
  
  FUN_0000079a();
  FUN_000007b6();
  FUN_00000802();
  FUN_00000880();
  FUN_000008c8();
  FUN_0000096e();
  FUN_00000c52();
  __synchronize();
  for (puVar1 = ((undefined *)camry_host_ptr(0xfebf7c00u));(uintptr_t)(puVar1)<(uintptr_t)(((undefined *)camry_host_ptr(0xfebe7000u))); puVar1 = puVar1 + 1) {
    *puVar1 = 0;
  }
  for (puVar1 = (undefined4 *)((undefined *)camry_host_ptr(0xfebe8000u));(uintptr_t)(puVar1)<(uintptr_t)(((undefined4 *)camry_host_ptr((uint32_t)(0xfec00000)))); puVar1 = puVar1 + 1)
  {
    *puVar1 = 0;
  }
  for (puVar1 = ((undefined *)camry_host_ptr(0xfeef8000u));(uintptr_t)(puVar1)<(uintptr_t)(((undefined4 *)camry_host_ptr((uint32_t)(0xfef08000)))); puVar1 = puVar1 + 1) {
    *puVar1 = 0;
  }
  EEPRDCYCL = '\x03';
  f33_boot_select_application_or_resident();
  return;
}



void FUN_00001478(undefined4 *param_1,undefined4 *param_2,int param_3)

{
  undefined4 uVar1;
  
  if (0 < param_3) {
    do {
      uVar1 = *param_1;
      param_1 = param_1 + 1;
      *param_2 = uVar1;
      param_2 = param_2 + 1;
      param_3 = param_3 + -1;
    } while (param_3 != 0);
  }
  return;
}



/* Copy exactlyninewords from r6 toFEBF2908 through real1478 word-copy,then enter1398 resident
   bootloader. Requires bootGP/SP/context alreadyestablished by9F00;not an
   ordinaryapplication-callable initializationhelper. */

void f33_boot_resident_enter_with_record(uint *handoff_record)

{
  FUN_00001478(handoff_record, ((undefined4 *)camry_host_ptr((uint32_t)((0xfebf2908u)))), 9);
  f33_boot_resident_main();
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}



void FUN_000014a2(void)

{
  if (DAT_febf2904 == '\x02') {
    FUN_00001d9a();
    FUN_00000780();
    FUN_00002250();
  }
  return;
}



void FUN_000014be(uint param_1)

{
  uint32_t puVar1;
  undefined4 uVar2;
  
  puVar1 = 0xfebf9800u;
  uVar2 = FUN_0000721e(0xffff);
  (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x6f00)))) = (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x6f00)))) | 1 << (param_1 & 0x1f);
  FUN_00007244(uVar2);
  return;
}



void FUN_000014e8(uint param_1)

{
  uint32_t puVar1;
  undefined4 uVar2;
  
  puVar1 = 0xfebf9800u;
  uVar2 = FUN_0000721e(0xffff);
  (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x6f00)))) = (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x6f00)))) & ~(1 << (param_1 & 0x1f));
  FUN_00007244(uVar2);
  return;
}



void FUN_00001514(undefined4 param_1,undefined1 param_2)

{
  FUN_00001478(((undefined4 *)camry_host_ptr((uint32_t)((0xfebf2908u)))), ((undefined4 *)camry_host_ptr((uint32_t)(param_1))), param_2);
  return;
}



void FUN_0000152a(void)

{
  FUN_000036be();
  f33_return_only_stub_798();
  return;
}



void FUN_0000153a(undefined1 *param_1,undefined1 *param_2,int param_3)

{
  undefined1 uVar1;
  
  if (0 < param_3) {
    do {
      uVar1 = *param_1;
      param_1 = param_1 + 1;
      *param_2 = uVar1;
      param_2 = param_2 + 1;
      param_3 = param_3 + -1;
    } while (param_3 != 0);
  }
  return;
}



/* Single constant publisher: DAT_febf2904 = 3; Shape-classified from the canonical corpus; the
   target cell is not yet named, so the written state's meaning is unknown. */

void FUN_00001550(void)

{
  DAT_febf2904 = 3;
  return;
}



void FUN_00001560(void)

{
  ushort uVar1;
  uint uVar2;
  
  __disable_irq();
  uVar2 = CLKD3STAT;
  if ((uVar2 & 2) == 2) {
    CLKD3DIV = 0;
    uVar2 = CLKD3DIV;
    __synchronize();
  }
  uVar1 = Ramffc10100;
  Ramffc10100 = uVar1 & 0xffdf;
  uVar1 = Ramffc10114;
  Ramffc10114 = uVar1 & 0xffdf;
  uVar1 = Ramffc10110;
  Ramffc10110 = uVar1 & 0xffdf;
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}



void FUN_0000159e(void)

{
  FUN_0000721e(0xffff);
  FUN_00001550();
  FUN_00001560();
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}



/* Single constant publisher: DAT_ffd50020 = 0x22; Shape-classified from the canonical corpus; the
   target cell is not yet named, so the written state's meaning is unknown. */

void FUN_000015b4(void)

{
  DAT_ffd50020 = 0x22;
  return;
}



uint FUN_000015c0(ushort *param_1)

{
  uint uVar1;
  
  DAT_ffd50020 = 0x22;
  Ramffd50004 = 0xff;
  Ramffd50000 = (uint)(*param_1 >> 8);
  Ramffd50000 = *param_1 & 0xff;
  Ramffd50000 = (uint)(param_1[1] >> 8);
  Ramffd50000 = param_1[1] & 0xff;
  Ramffd50000 = (uint)(param_1[2] >> 8);
  Ramffd50000 = param_1[2] & 0xff;
  Ramffd50000 = (uint)(param_1[3] >> 8);
  uVar1 = Ramffd50004;
  return (uVar1 ^ 0xff) & 0xff;
}



undefined4 FUN_00001626(ushort *param_1)

{
  uint uVar1;
  
  uVar1 = Ramffd82004;
  if ((uVar1 & 0x80) == 0) {
    Ramffd83018 = 0;
    Ramffd83008 = *param_1 | 0x20fe0000;
    Ramffd83008 = param_1[1] | 0x20fe0000;
    Ramffd83008 = param_1[2] | 0x20fe0000;
    Ramffd83008 = param_1[3] | 0xfe0000;
    Ramffd83004 = 0x80040000;
    return 0;
  }
  return 0x5aa5;
}



undefined4 FUN_0000167c(int param_1)

{
  ushort uVar1;
  
  uVar1 = FUN_000015c0(((ushort *)camry_host_ptr((uint32_t)(param_1))));
  (*((ushort *)camry_host_ptr((uint32_t)(param_1 + 6)))) = (*((ushort *)camry_host_ptr((uint32_t)(param_1 + 6)))) & 0xff00 | uVar1;
  return FUN_00001626(((ushort *)camry_host_ptr((uint32_t)(param_1))));
}



undefined * FUN_0000169c(undefined2 *param_1)

{
  uint uVar1;
  undefined2 uVar2;
  
  uVar1 = Ramffd82004;
  if (((uVar1 >> 7 & 1) == 0) && (uVar1 = Ramffd83004, (uVar1 & 0x7f) == 4)) {
    uVar1 = Ramffd83018;
    if ((uVar1 & 0x7fffff) >> 0x10 != 0) {
      return ((undefined *)camry_host_ptr(0xa55au));
    }
    uVar2 = Ramffd83014;
    *param_1 = uVar2;
    uVar2 = Ramffd83014;
    param_1[1] = uVar2;
    uVar2 = Ramffd83014;
    param_1[2] = uVar2;
    uVar2 = Ramffd83014;
    param_1[3] = uVar2;
    return (undefined *)0x0;
  }
  return ((undefined *)camry_host_ptr((uint32_t)(0x5aa5)));
}



void FUN_000016f2(void)

{
  undefined1 uVar1;
  int iVar2;
  uint uVar3;
  byte bVar4;
  undefined2 local_1c;
  undefined2 uStack_1a;
  undefined2 uStack_18;
  undefined2 uStack_16;
  undefined2 uStack_14;
  undefined2 uStack_12;
  undefined2 uStack_10;
  undefined2 uStack_e;
  
  local_1c = 0;
  uStack_1a = 0;
  bVar4 = 0;
  uStack_18 = 0;
  uStack_16 = 0;
  DAT_ffd82000 = 0;
  uVar1 = DAT_ffd82000;
  __synchronize();
  Ramffd82010 = 0x90;
  Ramffd82014 = 0;
  Ramffd83040 = 0x100;
  Ramffd83018 = 0;
  Ramffd83044 = 0xe000;
  Ramffd83048 = 0x8e000;
  Ramffd8304c = 0x8e000;
  Ramffd83050 = 0x8e000;
  Ramffd83054 = 0x8e000;
  Ramffd83058 = 0x8e000;
  Ramffd8305c = 0x8e000;
  Ramffd83060 = 0x8e000;
  Ramffd83068 = 0x14;
  Ramffd8306c = 0x14;
  Ramffd83070 = 0x14;
  Ramffd83074 = 0x14;
  Ramffd82008 = 0xc10b;
  DAT_ffd82000 = 0xe0;
  FUN_000015b4();
  FUN_00007208(0x50);
  uStack_14 = 0x8c00;
  uStack_12 = 0;
  uStack_10 = 0xf000;
  uStack_e = 0x1f00;
  FUN_0000167c(camry_host_addr(&uStack_14));
  FUN_00007208(0x50);
  FUN_0000167c(camry_host_addr(&uStack_14));
  FUN_00007208(0x50);
  do {
    iVar2 = camry_host_addr(FUN_0000169c(&local_1c));
    FUN_00007208(1);
    bVar4 = bVar4 + 1;
    if (iVar2 == 0) break;
  } while (bVar4 < 0xc9);
  uVar3 = FUN_000015c0(&local_1c);
  if ((byte)uStack_16 != uVar3) {
    do {
                    /* WARNING: Do nothing block with infinite loop */
    } while( true );
  }
  return;
}



void FUN_00001c20(void)

{
  TAUJ0TT = '\x0f';
  TAUJ0TPS = 0xfff0;
  (*((volatile uint8_t *)camry_host_ptr(0xffe50094u))) = 0;
  TAUJ0CMUR0 = '\0';
  TAUJ0CMUR1 = '\0';
  TAUJ0CMUR2 = '\0';
  TAUJ0CMUR3 = '\0';
  TAUJ0CMOR0 = 0;
  TAUJ0CMOR1 = 0;
  TAUJ0CMOR2 = 0;
  TAUJ0CMOR3 = 0;
  TAUJ0CDR0 = 0;
  TAUJ0CDR1 = 0;
  TAUJ0CDR2 = 79999;
  TAUJ0CDR3 = 0;
  TAUJ0TOE = '\0';
  TAUJ0TO = '\0';
  TAUJ0RDE = '\0';
  TAUJ0RDM = '\0';
  return;
}



/* Constant-block fill: 19 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_1c60(void)

{
  DAT_ffe51058 = 0xf;
  DAT_ffe51090 = 0xfff2;
  DAT_ffe51094 = 0;
  DAT_ffe51020 = 0;
  DAT_ffe51024 = 0;
  DAT_ffe51028 = 0;
  DAT_ffe5102c = 0;
  DAT_ffe51080 = 0x156;
  DAT_ffe51084 = 0;
  DAT_ffe51088 = 0;
  DAT_ffe5108c = 0;
  DAT_ffe51000 = 0;
  DAT_ffe51004 = 0;
  DAT_ffe51008 = 0;
  DAT_ffe5100c = 0;
  DAT_ffe51060 = 0;
  DAT_ffe5105c = 0;
  DAT_ffe510a0 = 0;
  DAT_ffe510a4 = 0;
  return;
}



void FUN_00001ca0(void)

{
  Ramffe201c8 = 0xffff;
  Ramffe211c8 = 0xffff;
  Ramffe221c8 = 0xffff;
  FUN_00001c20();
  f33_fill_constant_block_1c60();
  DAT_ffe52058 = 0xf;
  DAT_ffe70034 = 1;
  DAT_ffe71034 = 1;
  TAUJ0TS = '\x04';
  DAT_ffe51054 = 1;
  return;
}



void FUN_00001d0e(byte *param_1,uint param_2)

{
  *param_1 = *param_1 | '\x01' << (param_2 & 7);
  return;
}



undefined4 FUN_00001d24(void)

{
  undefined4 uVar1;
  
  uVar1 = DAT_ffe51010;
  return uVar1;
}



void FUN_00001d2c(ushort param_1,uint param_2,int param_3,undefined1 param_4)

{
  int *piVar1;
  uint32_t puVar2;
  undefined4 uVar3;
  int iVar4;
  
  puVar2 = 0xfebf9800u;
  uVar3 = FUN_0000721e(0xffff);
  iVar4 = ((void)(uVar3), FUN_00001d24());
  piVar1 = ((int *)camry_host_ptr((uint32_t)(puVar2 + (short)(param_1 & 0xff) * 0xc + -0x6ec8)));
  piVar1[1] = param_3;
  (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(piVar1) + 9)))) = param_4;
  *piVar1 = (param_2 & 0xffff) * 20000 + iVar4;
  *(undefined1 *)(piVar1 + 2) = 1;
  FUN_00007244(uVar3);
  return;
}



void FUN_00001d70(ushort param_1)

{
  f33_boot_timer_slots[(short)(param_1 & 0xff)].armed = '\0';
  return;
}



void FUN_00001d9a(void)

{
  int iVar1;
  int *piVar2;
  undefined8 uVar3;
  int iVar4;
  undefined4 uVar5;
  int iVar6;
  int iVar7;
  int local_1c;
  int iStack_18;
  uint uStack_14;
  
  uVar3 = 0x869cfebf9800;
  uVar5 = FUN_0000721e(0xffff);
  iVar6 = FUN_00001d24();
  for (iVar7 = 0; iVar4 = (int)((ulonglong)uVar3 >> 0x20),
      iVar1 = iVar7 - (uint)(*((byte *)camry_host_ptr((uint32_t)(iVar4 + 0x278)))), ((iVar1 < 0) || (iVar7 < 0));
      iVar7 = iVar7 + 1) {
    piVar2 = ((int *)camry_host_ptr((uint32_t)(iVar7 * 0xc + (int)uVar3 + -0x6ec8)));
    if (((char)piVar2[2] != '\0') && (*piVar2 - iVar6 < 0 || *piVar2 == iVar6)) {
      iStack_18 = piVar2[1];
      *(undefined1 *)(piVar2 + 2) = 0;
      uStack_14 = (uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(piVar2) + 9))));
      local_1c = iVar7;
      FUN_00003460((*((undefined4 *)camry_host_ptr((uint32_t)(iVar7 * 4 + *(int *)(iVar4 + 0x274))))), camry_host_addr(&local_1c));
    }
  }
  FUN_00007244(uVar5);
  return;
}



/* Far-call trampoline: prepare {lp},0 / jarl 0x14A2 / dispose 0,{lp},lp; byte-verified against the
   exact image. Forwards with registers and stack unchanged; marked as a thunk. Forwarding shape
   machine-verified; target semantics not recovered. */

void thunk_FUN_000014a2(void)

{
  FUN_000014a2();
  return;
}



void FUN_00001e10(void)

{
  FUN_0000721e(0xffff);
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}



/* Far-call trampoline: prepare {lp},0 / jarl 0x1E10 / dispose 0,{lp},lp; byte-verified against the
   exact image. Forwards with registers and stack unchanged; marked as a thunk. Forwarding shape
   machine-verified; target semantics not recovered. */

void thunk_FUN_00001e10(void)

{
  FUN_00001e10();
  return;
}



void FUN_00001e36(void)

{
  FUN_0000721e(0xffff);
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}



/* Dispatch entry for EIIC 1087: TAUJ0 channel2 per P1M-E R01UH0585EJ0120 interrupt table, page284.
   Calls 1CE8, then 1E04, then 14A2; state byte FEBF2904 == 2 enters services, state1 returns. The
   full state1 interrupt return was executed without replacing callees. Boot callback for EIIC1087:
   TAUJ0 channel2 per P1M-E R01UH0585EJ0120 page284. Calls1CE8 ->1E04 ->14A2; state byteFEBF2904==2
   enters services while state1 returns. Exact state1 chain and interrupt return executed without
   callee replacement; state2 services and physical scheduling are not exercised. */

void f33_boot_tauj0_ch2_callback(void)

{
  thunk_FUN_000014a2();
  return;
}



void FUN_00001e50(void)

{
  FUN_00004048(0);
  return;
}



void FUN_00001e5e(void)

{
  FUN_00003ef2(0);
  return;
}



void FUN_00001e6c(void)

{
  FUN_00004048(1);
  return;
}



void FUN_00001e7a(void)

{
  FUN_00003ef2(1);
  return;
}



void FUN_00001e88(void)

{
  FUN_00004048(2);
  return;
}



void FUN_00001e96(void)

{
  FUN_00003ef2(2);
  return;
}



void FUN_00001ea4(void)

{
  FUN_0000721e(0xffff);
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}



undefined4 FUN_00001ec0(undefined2 param_1,undefined4 *param_2)

{
  undefined4 local_c;
  undefined2 uStack_8;
  
  local_c = *param_2;
  uStack_8 = *(undefined2 *)(param_2 + 1);
  return FUN_00004606(param_1,&local_c);
}



undefined4 FUN_00001ede(undefined2 param_1)

{
  FUN_000045b2(param_1);
  return 0;
}



/* ActualROM88FCcallback,buildsPDUandcalls2B8A.Record+4u16selector,+8u32length,+Cinlinebytes. */

void f33_boot_transport_rx_record_callback(void *record)

{
  F33BootPduInfo local_c;
  
  local_c.data = camry_host_addr(((uchar *)camry_host_ptr((uint32_t)((int)camry_host_addr(record) + 0xc))));
  local_c.length = (ushort)(*((undefined4 *)camry_host_ptr((uint32_t)((int)camry_host_addr(record) + 8))));
  f33_boot_transport_receive_frame((*((ushort *)camry_host_ptr((uint32_t)((int)camry_host_addr(record) + 4)))),&local_c);
  return;
}



void FUN_00001f0c(char *param_1)

{
  if (*param_1 == '\0') {
    FUN_00002f1c(*(uint *)(param_1 + 4) & 0xffff);
  }
  return;
}



/* Constant-block fill: 11 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_1f24(void)

{
  DAT_febf2937 = 0;
  DAT_febf2936 = 0;
  DAT_febf2935 = 0;
  DAT_febf2934 = 0;
  DAT_febf292c = 0;
  DAT_febf2933 = 0;
  DAT_febf2932 = 0;
  DAT_febf2931 = 0;
  DAT_febf2930 = 0xa5;
  DAT_febf292f = 0;
  DAT_febf292e = 0;
  return;
}



void FUN_00001f60(uint param_1,uint param_2,undefined2 param_3)

{
  int iVar1;
  byte bVar2;
  
  iVar1 = (param_2 & 0xff) + (param_1 & 0xff) * 2;
  bVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebf292eu + (uint32_t)(iVar1) * 1u)))) + 1;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebf292eu + (uint32_t)(iVar1) * 1u)))) = bVar2;
  FUN_00001d2c((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x8d4cu + (uint32_t)(iVar1) * 1u)))),param_3,(uint)bVar2 + (param_1 & 0xff) * 0x100,0);
  return;
}



void FUN_00001f98(ushort param_1)

{
  undefined1 uVar1;
  byte bVar2;
  undefined2 uVar3;
  ushort channel;
  uint uVar4;
  uint uVar5;
  uint32_t puVar6;
  int iVar7;
  undefined1 uVar8;
  int iVar9;
  undefined1 *local_1c;
  undefined2 uStack_18;
  undefined1 auStack_14 [8];
  
  puVar6 = 0xfebf9800u;
  iVar9 = (short)(param_1 & 0xff) * 0x18;
  uVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x8d56u + (uint32_t)(iVar9) * 1u))));
  bVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x8d58u + (uint32_t)(iVar9) * 1u))));
  iVar7 = (uint)bVar2 * 0x10;
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x8d80u + (uint32_t)(iVar7) * 1u)))) == '\x04') {
    auStack_14[0] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x8d81u + (uint32_t)(iVar7) * 1u))));
  }
  uVar4 = (uint)((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x8d80u + (uint32_t)(iVar7) * 1u)))) == '\x04');
  auStack_14[uVar4] = 0x30;
  uVar5 = uVar4 + 2;
  auStack_14[uVar4 + 1] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x8d59u + (uint32_t)(iVar9) * 1u))));
  uVar8 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x8d5au + (uint32_t)(iVar9) * 1u))));
  while( true ) {
    auStack_14[uVar5] = uVar8;
    uVar5 = uVar5 + 1 & 0xffff;
    if (7 < uVar5) break;
    uVar8 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x8d82u + (uint32_t)(iVar7) * 1u))));
  }
  uStack_18 = 8;
  local_1c = auStack_14;
  iVar7 = FUN_00001ec0((*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x8d8eu + (uint32_t)((uint)bVar2 * 8) * 2u)))),&local_1c);
  if (iVar7 == 0) {
    uVar3 = *(undefined2 *)(((undefined *)camry_host_ptr(0x8d5cu)) + iVar9);
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6ec9))))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6ecc))))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6ecf))))) = 0x49;
    FUN_00001f60(uVar1,0,uVar3);
  }
  else {
    channel = (*((ushort *)camry_host_ptr((uint32_t)(&PTR_DAT_00008d66 + (short)(param_1 & 0xff) * 6))));
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6ecf))))) = 0;
    f33_boot_transport_receive_complete(channel,'\x01');
  }
  return;
}



void FUN_00002046(uint param_1)

{
  int iVar1;
  byte bVar2;
  ushort uVar3;
  uint32_t puVar4;
  F33BootInterruptEntry *pFVar5;
  uint uVar6;
  short sVar7;
  ushort uStack_1a;
  F33BootPduInfo FStack_18;
  
  bVar2 = DAT_febf2932;
  puVar4 = 0xfebf9800u;
  pFVar5 = f33_boot_interrupt_dispatch;
  uStack_1a = 0;
  FStack_18.data = 0;
  FStack_18.length = 0;
  iVar1 = (int)(short)(ushort)DAT_febf2932;
  uVar6 = f33_boot_transport_request_append
                    ((*((ushort *)camry_host_ptr((uint32_t)(&PTR_DAT_00008d66 + iVar1 * 6)))),&FStack_18,&uStack_1a);
  if (uVar6 == 0) {
    uVar3 = 0;
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x8d59u + (uint32_t)(iVar1 * 0x18) * 1u)))) != 0) {
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x8d53u + (uint32_t)(iVar1 * 0x18) * 1u)))) == '\x04') {
        sVar7 = 6;
      }
      else {
        sVar7 = 7;
      }
      uVar3 = sVar7 * (ushort)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x8d59u + (uint32_t)(iVar1 * 0x18) * 1u))));
    }
    if ((uStack_1a < (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + -0x6ed4))))) && ((uVar3 == 0 || (uStack_1a < uVar3)))) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6ecf))))) = 0x54;
    }
    else {
      FUN_00001d70((*((undefined1 *)camry_host_ptr((uint32_t)((int)&pFVar5[0xd6].eiic + (param_1 & 0xff) * 2)))));
      FUN_00001f98(bVar2);
    }
  }
  else {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6ecf))))) = 0;
    FUN_00001d70((*((undefined1 *)camry_host_ptr((uint32_t)((int)&pFVar5[0xd6].eiic + (param_1 & 0xff) * 2)))));
    f33_boot_transport_receive_complete((*((ushort *)camry_host_ptr((uint32_t)(&PTR_DAT_00008d66 + iVar1 * 6)))),'\x01');
  }
  return;
}



void FUN_000020e4(uint param_1)

{
  int iVar1;
  undefined1 uVar2;
  undefined2 uVar3;
  uint32_t puVar4;
  uint uVar5;
  int iVar6;
  byte bVar7;
  uint uVar8;
  ushort uStack_2a;
  F33BootPduInfo FStack_28;
  uchar auStack_20 [8];
  
  puVar4 = 0xfebf9800u;
  param_1 = param_1 & 0xff;
  iVar1 = param_1 * 0x10;
  FStack_28.length = 7;
  uVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x8d83u + (uint32_t)(iVar1) * 1u))));
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x8d80u + (uint32_t)(iVar1) * 1u)))) == '\x04') {
    auStack_20[0] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x8d81u + (uint32_t)(iVar1) * 1u))));
    FStack_28.length = 6;
  }
  uVar8 = (uint)((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x8d80u + (uint32_t)(iVar1) * 1u)))) == '\x04');
  bVar7 = DAT_febf2933 + 1U & 0xf;
  auStack_20[uVar8] = bVar7 + 0x20;
  FStack_28.data = camry_host_addr(auStack_20 + uVar8 + 1);
  uStack_2a = DAT_febf292c;
  if (DAT_febf292c < FStack_28.length) {
    FStack_28.length = DAT_febf292c;
  }
  uVar5 = f33_boot_transport_response_copy((ushort)param_1,&FStack_28,0,&uStack_2a);
  if (uVar5 == 0) {
    for (uVar8 = uVar8 + 1 + (uint)FStack_28.length & 0xffff; uVar8 < 8; uVar8 = uVar8 + 1) {
      auStack_20[uVar8] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x8d82u + (uint32_t)(iVar1) * 1u))));
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6ecd))))) = bVar7;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6ecc))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6ecc))))) + '\x01';
    (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + -0x6ed4)))) = uStack_2a;
    FStack_28.data = camry_host_addr(auStack_20);
    FStack_28.length = 8;
    iVar6 = FUN_00001ec0((*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x8d8eu + (uint32_t)(param_1 * 8) * 2u)))),&FStack_28);
    if (iVar6 == 0) {
      uVar3 = *(undefined2 *)(((undefined *)camry_host_ptr(0x8d86u)) + iVar1);
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6ecf))))) = 0x8c;
      FUN_00001f60(uVar2,0,uVar3);
      return;
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6ecf))))) = 0;
  f33_boot_transport_response_complete((ushort)param_1,'\x01');
  return;
}



void FUN_000021c2(uint param_1)

{
  byte bVar1;
  uint32_t puVar2;
  F33BootInterruptEntry *pFVar3;
  uint uVar4;
  ushort uVar5;
  ushort uVar6;
  ushort uStack_1a;
  F33BootPduInfo FStack_18;
  
  bVar1 = DAT_febf2932;
  puVar2 = 0xfebf9800u;
  pFVar3 = f33_boot_interrupt_dispatch;
  uStack_1a = 0;
  FStack_18.data = 0;
  FStack_18.length = 0;
  if (DAT_00008d80 == '\x04') {
    uVar5 = 6;
  }
  else {
    uVar5 = 7;
  }
  uVar6 = DAT_febf292c;
  if (uVar5 <= DAT_febf292c) {
    uVar6 = uVar5;
  }
  uVar4 = f33_boot_transport_response_copy((ushort)DAT_febf2932,&FStack_18,0,&uStack_1a);
  if (uVar4 == 0) {
    if (uVar6 <= uStack_1a) {
      FUN_00001d70((*((undefined1 *)camry_host_ptr((uint32_t)((int)&pFVar3[0xd6].eiic + (param_1 & 0xff) * 2)))));
      if (((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6ecf)))))) == -0x5e) {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6ecf))))) = 0xa1;
      }
      else {
        FUN_000020e4(bVar1);
      }
    }
  }
  else if (uVar4 != 2) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6ecf))))) = 0;
    FUN_00001d70((*((undefined1 *)camry_host_ptr((uint32_t)((int)&pFVar3[0xd6].eiic + (param_1 & 0xff) * 2)))));
    f33_boot_transport_response_complete((ushort)bVar1,'\x01');
  }
  return;
}



void FUN_00002250(void)

{
  if (DAT_febf2930 != '\0') {
    if (DAT_febf2931 == 'T') {
      FUN_00002046(0);
    }
    else if ((((int8_t)DAT_febf2931) == -0x5e) || (((int8_t)DAT_febf2931) == -0x5c)) {
      FUN_000021c2(0);
    }
  }
  return;
}



uint FUN_00002284(uint param_1,byte *param_2,byte *param_3)

{
  byte bVar1;
  uint uVar2;
  int iVar3;
  
  uVar2 = param_1 & 0xff;
  do {
    if (1 < uVar2) {
      return uVar2;
    }
    iVar3 = (short)uVar2 * 0x18;
    if ((param_1 & 0xffff) <= (uint)*(ushort *)(((undefined *)camry_host_ptr(0x8d50u)) + iVar3)) {
      if ((param_1 & 0xffff) < (uint)*(ushort *)(((undefined *)camry_host_ptr(0x8d50u)) + iVar3)) {
        return 2;
      }
      bVar1 = *param_2;
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x8d53u + (uint32_t)(iVar3) * 1u)))) == '\x03') {
LAB_000022a8:
        *param_3 = bVar1 & 0xf0;
        return uVar2;
      }
      if (bVar1 == (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x8d54u + (uint32_t)(iVar3) * 1u))))) {
        bVar1 = param_2[1];
        goto LAB_000022a8;
      }
    }
    uVar2 = uVar2 + 1;
  } while( true );
}



undefined4 FUN_000022ca(uint param_1,ushort param_2)

{
  uint32_t puVar1;
  F33BootInterruptEntry *pFVar2;
  F33BootInterruptEntry *pFVar3;
  undefined4 uVar4;
  ushort uVar5;
  
  puVar1 = 0xfebf9800u;
  pFVar2 = f33_boot_interrupt_dispatch;
  uVar4 = 0;
  uVar5 = (ushort)DAT_febf2932;
  if (((param_2 & 0xff) == (ushort)DAT_febf2932) ||
     ((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x8d57u + (uint32_t)((short)(param_2 & 0xff) * 0x18) * 1u)))) <
      (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x8d57u + (uint32_t)((short)uVar5 * 0x18) * 1u)))))) {
    uVar4 = 1;
    if ((DAT_febf2931 == 'J') || ((DAT_febf2931 == 'L' || (DAT_febf2931 == 'I')))) {
      FUN_00001ede(DAT_00008d8e);
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6ecf))))) = 0;
    pFVar3 = pFVar2;
    FUN_00001d70((*((undefined1 *)camry_host_ptr((uint32_t)((int)&pFVar2[0xd6].eiic + (param_1 & 0xff) * 2)))));
    FUN_00001d70((*((undefined1 *)camry_host_ptr((uint32_t)((int)&pFVar2[0xd6].eiic + (param_1 & 0xff) * 2 + 1)))));
    f33_boot_transport_receive_complete
              ((*((ushort *)camry_host_ptr((uint32_t)((int)&pFVar3[(short)uVar5 * 3 + 0xd9].eiic + 2)))),'\a');
  }
  return uVar4;
}



undefined4 FUN_00002350(uint param_1,ushort param_2)

{
  byte bVar1;
  uint32_t puVar2;
  F33BootInterruptEntry *pFVar3;
  undefined4 uVar4;
  
  bVar1 = DAT_febf2932;
  puVar2 = 0xfebf9800u;
  pFVar3 = f33_boot_interrupt_dispatch;
  uVar4 = 0;
  if ((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x8d57u + (uint32_t)((short)(param_2 & 0xff) * 0x18) * 1u)))) < DAT_00008d84) {
    uVar4 = 1;
    if (((((int8_t)DAT_febf2931) == -0x76) || (((int8_t)DAT_febf2931) == -0x77)) || (((int8_t)DAT_febf2931) == -0x74)) {
      FUN_00001ede(DAT_00008d8e);
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6ecf))))) = 0;
    FUN_00001d70((*((undefined1 *)camry_host_ptr((uint32_t)((int)&pFVar3[0xd6].eiic + (param_1 & 0xff) * 2)))));
    FUN_00001d70((*((undefined1 *)camry_host_ptr((uint32_t)((int)&pFVar3[0xd6].eiic + (param_1 & 0xff) * 2 + 1)))));
    f33_boot_transport_response_complete((ushort)bVar1,'\a');
  }
  return uVar4;
}



void FUN_000023b8(ushort param_1,ushort param_2,uchar *param_3)

{
  ushort channel;
  uint32_t puVar1;
  uchar status;
  uint uVar2;
  ushort uStack_16;
  F33BootPduInfo FStack_14;
  
  puVar1 = 0xfebf9800u;
  channel = (*((ushort *)camry_host_ptr((uint32_t)(&PTR_DAT_00008d66 + (short)(param_1 & 0xff) * 6))));
  uStack_16 = 0;
  DAT_febf2931 = 0x54;
  FStack_14.data = camry_host_addr(param_3);
  FStack_14.length = param_2;
  uVar2 = f33_boot_transport_request_admit(channel,&FStack_14,param_2,&uStack_16);
  if ((uVar2 == 0) && (param_2 <= uStack_16)) {
    uVar2 = f33_boot_transport_request_append(channel,&FStack_14,&uStack_16);
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6ecf))))) = 0;
    status = uVar2 != 0;
  }
  else {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6ecf))))) = 0;
    if (uVar2 != 0) {
      return;
    }
    status = '\t';
  }
  f33_boot_transport_receive_complete(channel,status);
  return;
}



void FUN_0000242a(ushort param_1,uint param_2,int param_3)

{
  byte bVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  
  param_1 = param_1 & 0xff;
  uVar5 = (uint)((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x8d53u + (uint32_t)((short)param_1 * 0x18) * 1u)))) == '\x04');
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x8d53u + (uint32_t)((short)param_1 * 0x18) * 1u)))) == '\x04') {
    uVar3 = 6;
    iVar2 = 2;
  }
  else {
    uVar3 = 7;
    iVar2 = 1;
  }
  bVar1 = (*((byte *)camry_host_ptr((uint32_t)(uVar5 + param_3))));
  uVar4 = bVar1 & 0xf;
  if ((((bVar1 & 0xf) != 0) && (uVar4 <= uVar3)) &&
     (-1 < (int)((param_2 & 0xffff) - (iVar2 + uVar4)))) {
    iVar2 = 1;
    if (((DAT_febf2931 == 'I' || DAT_febf2931 == 'J') || (DAT_febf2931 == 'L')) ||
       ((DAT_febf2931 == 'Q' || DAT_febf2931 == 'R' ||
        ((DAT_febf2931 == 'T' || (DAT_febf2931 == 'a')))))) {
      iVar2 = FUN_000022ca((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x8d56u + (uint32_t)((short)param_1 * 0x18) * 1u)))),param_1);
    }
    else if ((((((int8_t)DAT_febf2931) == -0x77 || ((int8_t)DAT_febf2931) == -0x76) || (((int8_t)DAT_febf2931) == -0x74)) ||
             (((int8_t)DAT_febf2931) == -0x6f || ((int8_t)DAT_febf2931) == -0x6e)) ||
            ((((int8_t)DAT_febf2931) == -0x5f || ((int8_t)DAT_febf2931) == -0x5e || (((int8_t)DAT_febf2931) == -0x5c)))) {
      iVar2 = FUN_00002350((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x8d56u + (uint32_t)((short)param_1 * 0x18) * 1u)))),param_1);
    }
    if (iVar2 == 1) {
      FUN_000023b8(param_1, uVar4, ((uchar *)camry_host_ptr((uint32_t)(uVar5 + 1 + param_3))));
    }
  }
  return;
}



void FUN_000024d0(ushort param_1)

{
  int iVar1;
  undefined1 uVar2;
  byte bVar3;
  undefined2 uVar4;
  byte bVar5;
  uint uVar6;
  uint uVar7;
  uint32_t puVar8;
  ushort channel;
  uchar status;
  int iVar9;
  undefined1 uVar10;
  int iVar11;
  undefined1 *local_20;
  undefined2 uStack_1c;
  undefined1 auStack_18 [8];
  
  bVar5 = DAT_febf2937;
  puVar8 = 0xfebf9800u;
  iVar1 = (int)(short)(param_1 & 0xff);
  iVar11 = iVar1 * 0x18;
  uVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x8d56u + (uint32_t)(iVar11) * 1u))));
  bVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x8d58u + (uint32_t)(iVar11) * 1u))));
  if (DAT_febf2937 < (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x8d64u + (uint32_t)(iVar11) * 1u))))) {
    iVar9 = (uint)bVar3 * 0x10;
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x8d80u + (uint32_t)(iVar9) * 1u)))) == '\x04') {
      auStack_18[0] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x8d81u + (uint32_t)(iVar9) * 1u))));
    }
    uVar6 = (uint)((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x8d80u + (uint32_t)(iVar9) * 1u)))) == '\x04');
    auStack_18[uVar6] = 0x31;
    uVar7 = uVar6 + 2;
    auStack_18[uVar6 + 1] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x8d59u + (uint32_t)(iVar11) * 1u))));
    uVar10 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x8d5au + (uint32_t)(iVar11) * 1u))));
    while( true ) {
      auStack_18[uVar7] = uVar10;
      uVar7 = uVar7 + 1 & 0xffff;
      if (7 < uVar7) break;
      uVar10 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x8d82u + (uint32_t)(iVar9) * 1u))));
    }
    uStack_1c = 8;
    local_20 = auStack_18;
    iVar9 = FUN_00001ec0((*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x8d8eu + (uint32_t)((uint)bVar3 * 8) * 2u)))),&local_20);
    if (iVar9 == 0) {
      uVar4 = *(undefined2 *)(((undefined *)camry_host_ptr(0x8d5cu)) + iVar11);
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar8 + (uint32_t)(-0x6ec9))))) = bVar5 + 1;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar8 + (uint32_t)(-0x6ecf))))) = 0x4c;
      FUN_00001f60(uVar2,0,uVar4);
      return;
    }
    channel = (*((ushort *)camry_host_ptr((uint32_t)(&PTR_DAT_00008d66 + iVar1 * 6))));
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar8 + (uint32_t)(-0x6ecf))))) = 0;
    status = '\x01';
  }
  else {
    DAT_febf2931 = 0;
    status = '\b';
    channel = (*((ushort *)camry_host_ptr((uint32_t)(&PTR_DAT_00008d66 + iVar1 * 6))));
  }
  f33_boot_transport_receive_complete(channel,status);
  return;
}



void FUN_00002594(undefined1 param_1,ushort param_2)

{
  int iVar1;
  byte bVar2;
  undefined2 uVar3;
  ushort uVar4;
  uint32_t puVar5;
  uint uVar6;
  short sVar7;
  int iVar8;
  ushort uStack_1a;
  F33BootPduInfo FStack_18;
  
  puVar5 = 0xfebf9800u;
  param_2 = param_2 & 0xff;
  iVar1 = (int)(short)param_2;
  iVar8 = iVar1 * 0x18;
  uStack_1a = 0;
  FStack_18.data = 0;
  FStack_18.length = 0;
  uVar6 = f33_boot_transport_request_append
                    ((*((ushort *)camry_host_ptr((uint32_t)(&PTR_DAT_00008d66 + iVar1 * 6)))),&FStack_18,&uStack_1a);
  if (uVar6 == 0) {
    bVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x8d59u + (uint32_t)(iVar8) * 1u))));
    uVar4 = 0;
    if (bVar2 != 0) {
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x8d53u + (uint32_t)(iVar8) * 1u)))) == '\x04') {
        sVar7 = 6;
      }
      else {
        sVar7 = 7;
      }
      uVar4 = sVar7 * (ushort)bVar2;
    }
    if ((uStack_1a < (*((ushort *)camry_host_ptr((uint32_t)(puVar5 + -0x6ed4))))) && ((bVar2 == 0 || (uStack_1a < uVar4)))) {
      if (*(short *)(((undefined *)camry_host_ptr(0x8d5eu)) + iVar8) == 0) {
        FUN_000024d0(param_2);
      }
      else {
        uVar3 = *(undefined2 *)(((undefined *)camry_host_ptr(0x8d5eu)) + iVar8);
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x6ecf))))) = 0x54;
        FUN_00001f60(param_1,0,uVar3);
      }
    }
    else {
      FUN_00001f98(param_2);
    }
  }
  else {
    uVar4 = (*((ushort *)camry_host_ptr((uint32_t)(&PTR_DAT_00008d66 + iVar1 * 6))));
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x6ecf))))) = 0;
    f33_boot_transport_receive_complete(uVar4,'\x01');
  }
  return;
}



void FUN_00002636(ushort param_1)

{
  undefined1 uVar1;
  byte bVar2;
  undefined2 uVar3;
  uint uVar4;
  uint uVar5;
  uint32_t puVar6;
  int iVar7;
  undefined1 uVar8;
  int iVar9;
  undefined1 *local_1c;
  undefined2 uStack_18;
  undefined1 auStack_14 [8];
  
  puVar6 = 0xfebf9800u;
  iVar9 = (short)(param_1 & 0xff) * 0x18;
  uVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x8d56u + (uint32_t)(iVar9) * 1u))));
  bVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x8d58u + (uint32_t)(iVar9) * 1u))));
  iVar7 = (uint)bVar2 * 0x10;
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x8d80u + (uint32_t)(iVar7) * 1u)))) == '\x04') {
    auStack_14[0] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x8d81u + (uint32_t)(iVar7) * 1u))));
  }
  uVar4 = (uint)((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x8d80u + (uint32_t)(iVar7) * 1u)))) == '\x04');
  auStack_14[uVar4] = 0x32;
  uVar5 = uVar4 + 2;
  auStack_14[uVar4 + 1] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x8d59u + (uint32_t)(iVar9) * 1u))));
  uVar8 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x8d5au + (uint32_t)(iVar9) * 1u))));
  while( true ) {
    auStack_14[uVar5] = uVar8;
    uVar5 = uVar5 + 1 & 0xffff;
    if (7 < uVar5) break;
    uVar8 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x8d82u + (uint32_t)(iVar7) * 1u))));
  }
  uStack_18 = 8;
  local_1c = auStack_14;
  iVar7 = FUN_00001ec0((*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x8d8eu + (uint32_t)((uint)bVar2 * 8) * 2u)))),&local_1c);
  if (iVar7 == 0) {
    uVar3 = *(undefined2 *)(((undefined *)camry_host_ptr(0x8d5cu)) + iVar9);
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6ecf))))) = 0x4a;
    FUN_00001f60(uVar1,0,uVar3);
  }
  else {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6ecf))))) = 0;
  }
  return;
}



void FUN_000026d2(byte param_1,ushort param_2,uchar *param_3)

{
  undefined1 uVar1;
  ushort channel;
  short sVar2;
  undefined2 uVar3;
  uint32_t puVar4;
  undefined4 uVar5;
  uint uVar6;
  int iVar7;
  ushort uStack_22;
  F33BootPduInfo FStack_20;
  
  puVar4 = 0xfebf9800u;
  iVar7 = (short)(ushort)param_1 * 0x18;
  FStack_20.length = 6;
  uVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x8d56u + (uint32_t)(iVar7) * 1u))));
  channel = (*((ushort *)camry_host_ptr((uint32_t)(&PTR_DAT_00008d66 + (short)(ushort)param_1 * 6))));
  uStack_22 = 0;
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x8d53u + (uint32_t)(iVar7) * 1u)))) == '\x04') {
    FStack_20.length = 5;
  }
  DAT_febf2931 = 0x54;
  FStack_20.data = camry_host_addr(param_3);
  uVar6 = f33_boot_transport_request_admit(channel,&FStack_20,param_2,&uStack_22);
  if (uVar6 == 0) {
    if (FStack_20.length <= uStack_22) {
      uVar6 = f33_boot_transport_request_append(channel,&FStack_20,&uStack_22);
      if (uVar6 != 0) {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6ecf))))) = 0;
        f33_boot_transport_receive_complete(channel,'\x01');
        return;
      }
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6ec9))))) = 0;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6ecc))))) = 0;
      sVar2 = *(short *)(((undefined *)camry_host_ptr(0x8d60u)) + iVar7);
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6ecd))))) = 0;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6ece))))) = param_1;
      (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + -0x6ed4)))) = param_2 - FStack_20.length;
      if (sVar2 == 0) {
        FUN_00002594(uVar1,param_1);
        return;
      }
      uVar3 = *(undefined2 *)(((undefined *)camry_host_ptr(0x8d60u)) + iVar7);
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6ecf))))) = 0x51;
      FUN_00001f60(uVar1,1,uVar3);
      uVar3 = *(undefined2 *)(((undefined *)camry_host_ptr(0x8d5eu)) + iVar7);
      uVar5 = 0;
      goto LAB_000027c2;
    }
  }
  else if (uVar6 != 3) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6ecf))))) = 0;
    return;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6ece))))) = param_1;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6ecf))))) = 0x52;
  if (uVar6 == 0) {
    f33_boot_transport_receive_complete(channel,'\t');
  }
  if (*(short *)(((undefined *)camry_host_ptr(0x8d60u)) + iVar7) == 0) {
    FUN_00002636(param_1);
    return;
  }
  uVar3 = *(undefined2 *)(((undefined *)camry_host_ptr(0x8d60u)) + iVar7);
  uVar5 = 1;
LAB_000027c2:
  FUN_00001f60(uVar1,uVar5,uVar3);
  return;
}



void FUN_000027d8(ushort param_1,short param_2,int param_3)

{
  uint uVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  int iVar5;
  
  param_1 = param_1 & 0xff;
  iVar5 = (short)param_1 * 0x18;
  uVar4 = (uint)((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x8d53u + (uint32_t)(iVar5) * 1u)))) == '\x04');
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x8d53u + (uint32_t)(iVar5) * 1u)))) == '\x04') {
    uVar3 = 7;
  }
  else {
    uVar3 = 8;
  }
  uVar1 = ((*((byte *)camry_host_ptr((uint32_t)(uVar4 + param_3)))) & 0xf) * 0x100 + (uint)(*((byte *)camry_host_ptr((uint32_t)(uVar4 + 1 + param_3))));
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x8d52u + (uint32_t)(iVar5) * 1u)))) == '\x01') && (uVar3 <= uVar1)) && (param_2 == 8)) {
    if (((DAT_febf2931 == 'I' || DAT_febf2931 == 'J') || (DAT_febf2931 == 'L')) ||
       ((DAT_febf2931 == 'Q' || DAT_febf2931 == 'R' ||
        ((DAT_febf2931 == 'T' || (DAT_febf2931 == 'a')))))) {
      iVar2 = FUN_000022ca((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x8d56u + (uint32_t)(iVar5) * 1u)))),param_1);
    }
    else if ((((int8_t)DAT_febf2931) == -0x77 || ((int8_t)DAT_febf2931) == -0x76) ||
            ((((((int8_t)DAT_febf2931) == -0x74 || (((int8_t)DAT_febf2931) == -0x6f || ((int8_t)DAT_febf2931) == -0x6e)) ||
              (((int8_t)DAT_febf2931) == -0x5f || ((int8_t)DAT_febf2931) == -0x5e)) ||
             (iVar2 = 1, ((int8_t)DAT_febf2931) == -0x5c)))) {
      iVar2 = FUN_00002350((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x8d56u + (uint32_t)(iVar5) * 1u)))),param_1);
    }
    if (iVar2 == 1) {
      FUN_000026d2(param_1, uVar1, ((uchar *)camry_host_ptr((uint32_t)(uVar4 + 2 + param_3))));
    }
  }
  return;
}



void FUN_00002888(ushort param_1,ushort param_2,uchar *param_3)

{
  undefined1 uVar1;
  ushort channel;
  byte bVar2;
  undefined2 uVar3;
  uint32_t puVar4;
  uchar status;
  uint uVar5;
  int iVar6;
  ushort uStack_22;
  F33BootPduInfo FStack_20;
  
  puVar4 = 0xfebf9800u;
  param_1 = param_1 & 0xff;
  iVar6 = (short)param_1 * 0x18;
  uVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x8d56u + (uint32_t)(iVar6) * 1u))));
  channel = (*((ushort *)camry_host_ptr((uint32_t)(&PTR_DAT_00008d66 + (short)param_1 * 6))));
  uStack_22 = 0;
  FStack_20.data = camry_host_addr(param_3);
  FStack_20.length = param_2;
  uVar5 = f33_boot_transport_request_append(channel,&FStack_20,&uStack_22);
  if (uVar5 != 0) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6ecf))))) = 0;
    status = '\x01';
LAB_000028d8:
    f33_boot_transport_receive_complete(channel,status);
    return;
  }
  if ((*((ushort *)camry_host_ptr((uint32_t)(puVar4 + -0x6ed4)))) <= param_2) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6ecf))))) = 0;
    status = '\0';
    goto LAB_000028d8;
  }
  (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + -0x6ed4)))) = (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + -0x6ed4)))) - param_2;
  bVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x8d59u + (uint32_t)(iVar6) * 1u))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6ecd))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6ecd))))) + 1 & 0xf;
  if (bVar2 != 0) {
    if (bVar2 <= (byte)((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6ecc))))) + 1)) {
      if (*(short *)(((undefined *)camry_host_ptr(0x8d60u)) + iVar6) == 0) {
        FUN_00002594(uVar1,param_1);
        return;
      }
      uVar3 = *(undefined2 *)(((undefined *)camry_host_ptr(0x8d60u)) + iVar6);
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6ecf))))) = 0x51;
      FUN_00001f60(uVar1,1,uVar3);
      uVar3 = *(undefined2 *)(((undefined *)camry_host_ptr(0x8d5eu)) + iVar6);
      goto LAB_00002936;
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6ecc))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6ecc))))) + 1;
  }
  uVar3 = *(undefined2 *)(((undefined *)camry_host_ptr(0x8d62u)) + iVar6);
LAB_00002936:
  FUN_00001f60(uVar1,0,uVar3);
  return;
}



void FUN_00002946(ushort param_1,uint param_2,int param_3)

{
  byte bVar1;
  byte bVar2;
  ushort channel;
  uint uVar3;
  uint32_t puVar4;
  uint uVar5;
  uint uVar6;
  int iVar7;
  uint uVar8;
  
  puVar4 = 0xfebf9800u;
  param_1 = param_1 & 0xff;
  iVar7 = (short)param_1 * 0x18;
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x8d52u + (uint32_t)(iVar7) * 1u)))) == '\x01') && (DAT_febf2931 == 'a')) && (param_1 == DAT_febf2932)) {
    uVar5 = (uint)DAT_febf292c;
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x8d53u + (uint32_t)(iVar7) * 1u)))) == '\x04') {
      uVar6 = 6;
    }
    else {
      uVar6 = 7;
    }
    uVar3 = 8;
    uVar8 = (uint)((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x8d53u + (uint32_t)(iVar7) * 1u)))) == '\x04');
    if (uVar5 < uVar6) {
      uVar3 = uVar8 + uVar5 + 1 & 0xffff;
      uVar6 = uVar5;
    }
    if (uVar3 <= (param_2 & 0xffff)) {
      bVar2 = (*((byte *)camry_host_ptr((uint32_t)(uVar8 + param_3))));
      bVar1 = DAT_febf2933 + 1;
      FUN_00001d70((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x8d4cu + (uint32_t)((uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x8d56u + (uint32_t)(iVar7) * 1u)))) * 2) * 1u)))));
      if ((bVar2 & 0xf) == (bVar1 & 0xf)) {
        FUN_00002888(param_1, uVar6, ((uchar *)camry_host_ptr((uint32_t)(uVar8 + 1 + param_3))));
      }
      else {
        channel = (*((ushort *)camry_host_ptr((uint32_t)(&PTR_DAT_00008d66 + (short)param_1 * 6))));
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6ecf))))) = 0;
        f33_boot_transport_receive_complete(channel,'\x05');
      }
    }
  }
  return;
}



void FUN_000029e4(undefined4 param_1,undefined1 param_2,byte param_3)

{
  if (((((int8_t)DAT_febf2931) == -0x6f) && (DAT_febf2935 = param_2, DAT_febf2936 = param_3, 0x7f < param_3))
     && (DAT_febf2936 = 1, 8 < param_3 - 0xf1)) {
    DAT_febf2936 = 0x7f;
  }
  return;
}



void FUN_00002a12(undefined1 param_1,uint param_2,short param_3)

{
  int iVar1;
  uint32_t puVar2;
  undefined4 uVar3;
  uint uVar4;
  ushort uVar5;
  ushort uVar6;
  ushort uStack_22;
  F33BootPduInfo FStack_20;
  
  puVar2 = 0xfebf9800u;
  param_2 = param_2 & 0xff;
  iVar1 = param_2 * 0x10;
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x8d80u + (uint32_t)(iVar1) * 1u)))) == '\x04') {
    uVar5 = 6;
  }
  else {
    uVar5 = 7;
  }
  uStack_22 = 0;
  FStack_20.length = 0;
  uVar6 = DAT_febf292c;
  if (uVar5 <= DAT_febf292c) {
    uVar6 = uVar5;
  }
  FStack_20.data = 0;
  DAT_febf2931 = 0xa4;
  uVar4 = f33_boot_transport_response_copy((ushort)param_2,&FStack_20,0,&uStack_22);
  if (uVar4 == 0) {
    if (uStack_22 < uVar6) {
LAB_00002a8e:
      if (*(short *)(((undefined *)camry_host_ptr(0x8d8au)) + iVar1) == 0) goto LAB_00002aba;
      if (param_3 != 0) {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6ecf))))) = 0xa2;
        FUN_00001f60(param_1,1,param_3);
      }
      param_3 = *(short *)(((undefined *)camry_host_ptr(0x8d8au)) + iVar1);
      uVar3 = 0;
    }
    else {
      if (param_3 == 0) {
        FUN_000020e4(param_2);
        return;
      }
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6ecf))))) = 0xa1;
      uVar3 = 1;
    }
    FUN_00001f60(param_1,uVar3,param_3);
  }
  else {
    if (uVar4 == 2) goto LAB_00002a8e;
LAB_00002aba:
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6ecf))))) = 0;
    f33_boot_transport_response_complete((ushort)param_2,'\x01');
  }
  return;
}



void FUN_00002aca(undefined1 param_1)

{
  DAT_febf2934 = 0;
  FUN_00002a12(param_1,DAT_febf2932,DAT_00008d8c);
  return;
}



/* Checksresidenttransportenabled,selector<2,length2..8;routesPCI0/10/20/30usingexact8D50config.PDUisnotcompletedrequestdata.
   Native real SF admission copies10 02 without padding, preserving the live capacity pointer; stops
   before timer capture/service dispatch. */

void f33_boot_transport_receive_frame(ushort selector,F33BootPduInfo *pdu)

{
  F33BootInterruptEntry *pFVar1;
  uint uVar2;
  uchar *puVar3;
  uint uVar4;
  char cStack_d;
  
  pFVar1 = f33_boot_interrupt_dispatch;
  uVar4 = (uint)pdu->length;
  if (((DAT_febf2930 != '\0') && (selector < 2)) && (uVar4 - 2 < 7)) {
    puVar3 = ((void *)camry_host_ptr((uint32_t)(pdu->data)));
    cStack_d = -0x10;
    uVar2 = FUN_00002284(selector,puVar3,&cStack_d);
    if ((uVar2 < 2) &&
       (((*((char *)camry_host_ptr((uint32_t)((int)&pFVar1[(short)uVar2 * 3 + 0xd7].eiic + 1)))) == '\0' || (uVar4 == 8)))) {
      if (cStack_d == '\0') {
        FUN_0000242a(uVar2, uVar4, camry_host_addr(puVar3));
      }
      else if (cStack_d == '\x10') {
        FUN_000027d8(uVar2, uVar4, camry_host_addr(puVar3));
      }
      else if (cStack_d == ' ') {
        FUN_00002946(uVar2, uVar4, camry_host_addr(puVar3));
      }
      else if (cStack_d == '0') {
        FUN_00002ae4(uVar2, uVar4, camry_host_addr(puVar3));
      }
    }
  }
  return;
}



int FUN_00002c16(ushort param_1,undefined4 param_2)

{
  bool bVar1;
  int iVar2;
  undefined1 uVar3;
  uint32_t puVar4;
  uint uVar5;
  int iVar6;
  ushort uStack_26;
  F33BootPduInfo FStack_24;
  uchar auStack_1c [8];
  
  puVar4 = 0xfebf9800u;
  iVar2 = (uint)param_1 * 0x10;
  iVar6 = 1;
  uVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x8d83u + (uint32_t)(iVar2) * 1u))));
  bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x8d80u + (uint32_t)(iVar2) * 1u)))) == '\x04';
  if (bVar1) {
    auStack_1c[0] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x8d81u + (uint32_t)(iVar2) * 1u))));
  }
  auStack_1c[bVar1] = (char)((uint)param_2 >> 8) + '\x10';
  auStack_1c[bVar1 + 1] = (uchar)param_2;
  FStack_24.data = camry_host_addr(auStack_1c + bVar1 + 2);
  FStack_24.length = 8 - (bVar1 + 2);
  uStack_26 = 0;
  DAT_febf2931 = 0x89;
  uVar5 = f33_boot_transport_response_copy(param_1,&FStack_24,0,&uStack_26);
  if ((uVar5 == 0) && (uStack_26 != 0)) {
    FStack_24.data = camry_host_addr(auStack_1c);
    FStack_24.length = 8;
    iVar6 = FUN_00001ec0((*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x8d8eu + (uint32_t)((uint)param_1 * 8) * 2u)))),&FStack_24);
    if (iVar6 == 0) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6ece))))) = (char)param_1;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6ecd))))) = 0;
      (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + -0x6ed4)))) = uStack_26;
      FUN_00001f60(uVar3,0,*(undefined2 *)(((undefined *)camry_host_ptr(0x8d86u)) + iVar2));
      return 0;
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6ecf))))) = 0;
  return iVar6;
}



int FUN_00002cd4(ushort param_1,int param_2)

{
  int iVar1;
  undefined1 uVar2;
  undefined2 uVar3;
  uint32_t puVar4;
  uint uVar5;
  int iVar6;
  uint uVar7;
  ushort uStack_2e;
  F33BootPduInfo FStack_2c;
  uchar auStack_24 [8];
  
  puVar4 = 0xfebf9800u;
  iVar1 = (uint)param_1 * 0x10;
  iVar6 = 1;
  uVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x8d83u + (uint32_t)(iVar1) * 1u))));
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x8d80u + (uint32_t)(iVar1) * 1u)))) == '\x04') {
    auStack_24[0] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x8d81u + (uint32_t)(iVar1) * 1u))));
  }
  uVar7 = (uint)((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x8d80u + (uint32_t)(iVar1) * 1u)))) == '\x04');
  auStack_24[uVar7] = (uchar)param_2;
  FStack_2c.length = (ushort)param_2;
  FStack_2c.data = camry_host_addr(auStack_24 + uVar7 + 1);
  uStack_2e = 0;
  DAT_febf2931 = 0x8a;
  uVar5 = f33_boot_transport_response_copy(param_1,&FStack_2c,0,&uStack_2e);
  if ((uVar5 == 0) && (uStack_2e == 0)) {
    for (uVar5 = uVar7 + 1 + param_2 & 0xffff; uVar5 < 8; uVar5 = uVar5 + 1) {
      auStack_24[uVar5] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x8d82u + (uint32_t)(iVar1) * 1u))));
    }
    FStack_2c.data = camry_host_addr(auStack_24);
    FStack_2c.length = 8;
    iVar6 = FUN_00001ec0((*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x8d8eu + (uint32_t)((uint)param_1 * 8) * 2u)))),&FStack_2c);
    if (iVar6 == 0) {
      uVar3 = *(undefined2 *)(((undefined *)camry_host_ptr(0x8d86u)) + iVar1);
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6ece))))) = (char)param_1;
      FUN_00001f60(uVar2,0,uVar3);
      return 0;
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6ecf))))) = 0;
  return iVar6;
}



undefined1 FUN_00002e32(short param_1)

{
  undefined1 uVar1;
  
  uVar1 = 1;
  if ((DAT_00008d8e == param_1) &&
     (((((DAT_febf2931 != 'I' && (DAT_febf2931 != 'J')) && (DAT_febf2931 != 'L')) &&
       (((((int8_t)DAT_febf2931) != -0x76 && (((int8_t)DAT_febf2931) != -0x77)) && (((int8_t)DAT_febf2931) != -0x74)))) ||
      (uVar1 = DAT_00008d83, param_1 != DAT_00008d8e)))) {
    uVar1 = 1;
  }
  return uVar1;
}



void FUN_00002ecc(undefined1 param_1)

{
  if (DAT_febf292c == 0) {
    DAT_febf2931 = 0;
    f33_boot_transport_response_complete((ushort)DAT_febf2932,'\0');
  }
  else if ((DAT_febf2935 == 0) || (DAT_febf2934 < DAT_febf2935)) {
    FUN_00002a12(param_1,DAT_febf2932,DAT_febf2936);
  }
  else {
    DAT_febf2931 = 0x92;
    FUN_00001f60(param_1,0,DAT_00008d88);
  }
  return;
}



void FUN_00002f1c(undefined2 param_1)

{
  char cVar1;
  undefined2 uVar2;
  uint32_t puVar3;
  F33BootInterruptEntry *pFVar4;
  int iVar5;
  
  puVar3 = 0xfebf9800u;
  pFVar4 = f33_boot_interrupt_dispatch;
  if (DAT_febf2930 == '\0') {
    return;
  }
  iVar5 = FUN_00002e32(param_1);
  if (iVar5 != 0) {
    return;
  }
  FUN_00001d70((char)pFVar4[0xd6].eiic);
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6ecf)))));
  if (cVar1 == 'I') {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6ecf))))) = 0x61;
    uVar2 = (*((undefined2 *)camry_host_ptr((uint32_t)((int)&pFVar4[(short)(ushort)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6ece))))) * 3 + 0xd8].handler + 2))));
  }
  else {
    if (cVar1 == 'J') {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6ecf))))) = 0;
      return;
    }
    if (cVar1 == 'L') {
      FUN_00002e86(0);
      return;
    }
    if (((int8_t)cVar1) != -0x77) {
      if (((int8_t)cVar1) == -0x76) {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6ecf))))) = 0;
        f33_boot_transport_response_complete((ushort)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6ece))))),'\0');
        return;
      }
      if (((int8_t)cVar1) != -0x74) {
        return;
      }
      FUN_00002ecc(0);
      return;
    }
    uVar2 = *(undefined2 *)&pFVar4[0xdd].handler;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6ecf))))) = 0x91;
  }
  FUN_00001f60(0,0,uVar2);
  return;
}



void FUN_00002fb8(undefined1 param_1)

{
  if (DAT_febf2931 == 'Q') {
    FUN_00002046(param_1);
  }
  else if (DAT_febf2931 == 'R') {
    FUN_00002636(DAT_febf2932);
  }
  else if (((int8_t)DAT_febf2931) == -0x5f) {
    FUN_000020e4(DAT_febf2932);
  }
  else if (((int8_t)DAT_febf2931) == -0x5e) {
    DAT_febf2931 = -0x5c;
  }
  return;
}



void FUN_00003000(void)

{
  char cVar1;
  byte bVar2;
  uint32_t puVar3;
  uchar uVar4;
  ushort uVar5;
  
  bVar2 = DAT_febf2932;
  cVar1 = DAT_febf2931;
  puVar3 = 0xfebf9800u;
  uVar5 = (ushort)DAT_febf2932;
  if (((DAT_febf2931 == 'J') || (DAT_febf2931 == 'L')) || (DAT_febf2931 == 'I')) {
    FUN_00001ede((*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x8d8eu + (uint32_t)((uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x8d58u + (uint32_t)((short)uVar5 * 0x18) * 1u)))) * 8) * 2u)))));
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6ecf))))) = 0;
    if (cVar1 == 'J') {
      return;
    }
    uVar5 = (*((ushort *)camry_host_ptr((uint32_t)(&PTR_DAT_00008d66 + (short)uVar5 * 6))));
    uVar4 = '\x02';
  }
  else {
    if ((DAT_febf2931 == 'Q') || (DAT_febf2931 == 'T')) {
      FUN_000024d0(DAT_febf2932);
      return;
    }
    if (DAT_febf2931 != 'a') {
      if (((((int8_t)DAT_febf2931) == -0x76) || (((int8_t)DAT_febf2931) == -0x77)) || (((int8_t)DAT_febf2931) == -0x74)) {
        FUN_00001ede(DAT_00008d8e);
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6ecf))))) = 0;
        uVar4 = '\x02';
      }
      else if (((int8_t)DAT_febf2931) == -0x6f || ((int8_t)DAT_febf2931) == -0x6e) {
        DAT_febf2931 = '\0';
        uVar4 = '\x03';
      }
      else {
        if (((((int8_t)DAT_febf2931) != -0x5f) && (((int8_t)DAT_febf2931) != -0x5e)) && (((int8_t)DAT_febf2931) != -0x5c)) {
          return;
        }
        DAT_febf2931 = '\0';
        uVar4 = '\x01';
      }
      f33_boot_transport_response_complete((ushort)bVar2,uVar4);
      return;
    }
    uVar4 = '\x04';
    DAT_febf2931 = '\0';
    uVar5 = (*((ushort *)camry_host_ptr((uint32_t)(&PTR_DAT_00008d66 + (short)uVar5 * 6))));
  }
  f33_boot_transport_receive_complete(uVar5,uVar4);
  return;
}



undefined4 FUN_00003124(short param_1)

{
  byte bVar1;
  uint32_t puVar2;
  F33BootInterruptEntry *pFVar3;
  undefined4 uVar4;
  
  bVar1 = DAT_00008d83;
  puVar2 = 0xfebf9800u;
  pFVar3 = f33_boot_interrupt_dispatch;
  uVar4 = 1;
  if ((DAT_febf2930 != '\0') && (param_1 == 0)) {
    if ((((int8_t)DAT_febf2931) == -0x77 || ((int8_t)DAT_febf2931) == -0x76) || (((int8_t)DAT_febf2931) == -0x74)) {
      FUN_00001ede(DAT_00008d8e);
    }
    else if (((((int8_t)DAT_febf2931) != -0x6f && ((int8_t)DAT_febf2931) != -0x6e) &&
             (((int8_t)DAT_febf2931) != -0x5f && ((int8_t)DAT_febf2931) != -0x5e)) && (((int8_t)DAT_febf2931) != -0x5c)) {
      return 1;
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6ecf))))) = 0;
    FUN_00001d70((*((undefined1 *)camry_host_ptr((uint32_t)((int)&pFVar3[0xd6].eiic + (uint)bVar1 * 2)))));
    FUN_00001d70((*((undefined1 *)camry_host_ptr((uint32_t)((int)&pFVar3[0xd6].eiic + (uint)bVar1 * 2 + 1)))));
    f33_boot_transport_response_complete(0,'\x01');
    uVar4 = 0;
  }
  return uVar4;
}



undefined4 FUN_0000318c(ushort param_1)

{
  byte bVar1;
  uint uVar2;
  uint32_t puVar3;
  F33BootInterruptEntry *pFVar4;
  
  puVar3 = 0xfebf9800u;
  pFVar4 = f33_boot_interrupt_dispatch;
  uVar2 = 0;
  if (DAT_febf2930 != '\0') {
    do {
      if ((*((ushort *)camry_host_ptr((uint32_t)(&PTR_DAT_00008d66 + (short)uVar2 * 6)))) == param_1) {
        bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x8d56u + (uint32_t)((short)uVar2 * 0x18) * 1u))));
        if ((DAT_febf2931 == 'I' || DAT_febf2931 == 'J') || (DAT_febf2931 == 'L')) {
          FUN_00001ede(DAT_00008d8e);
        }
        else if (((DAT_febf2931 != 'Q' && DAT_febf2931 != 'R') && (DAT_febf2931 != 'T')) &&
                (DAT_febf2931 != 'a')) {
          return 1;
        }
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6ecf))))) = 0;
        FUN_00001d70((*((undefined1 *)camry_host_ptr((uint32_t)((int)&pFVar4[0xd6].eiic + (uint)bVar1 * 2)))));
        FUN_00001d70((*((undefined1 *)camry_host_ptr((uint32_t)((int)&pFVar4[0xd6].eiic + (uint)bVar1 * 2 + 1)))));
        f33_boot_transport_receive_complete(param_1,'\x01');
        return 0;
      }
      uVar2 = uVar2 + 1;
    } while (uVar2 < 2);
  }
  return 1;
}



void FUN_00003256(char *param_1)

{
  char cVar1;
  uint uVar2;
  int iVar3;
  
  cVar1 = *param_1;
  uVar2 = 0;
  do {
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x8d90u + (uint32_t)(uVar2 * 8) * 1u)))) == cVar1) {
      iVar3 = FUN_00003460((uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x8d91u + (uint32_t)(uVar2 * 8) * 1u)))) * 8 + 0x86dc, camry_host_addr(param_1));
      if (iVar3 == 0) {
        return;
      }
      FUN_00001d2c(cVar1,0,*(undefined2 *)(param_1 + 4),0);
      return;
    }
    uVar2 = uVar2 + 1;
  } while (uVar2 < 2);
  return;
}



void FUN_000032a0(char *param_1)

{
  uint uVar1;
  
  uVar1 = 0;
  do {
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x8d90u + (uint32_t)(uVar1 * 8) * 1u)))) == *param_1) {
      (*(int (*)())camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x8d94u + (uint32_t)(uVar1 * 2) * 4u))))))(*param_1,*(undefined2 *)(param_1 + 4));
      return;
    }
    uVar1 = uVar1 + 1;
  } while (uVar1 < 2);
  return;
}



/* Return0/write class byte for first permitted8DA0 range, else1/output unchanged. Require nonzero
   length and unsigned start<=end after modulo32 end=start+length-1. Check kind-mask bit(kind&31)
   and inclusive bounds. Actual classes:0 CodeFlash windows10000..17DFF/18000..FFDFF;1 RAM
   FEBF0000..0FFF. All rows mask33. Used by download, transfer and routine admission. */

uint f33_boot_classify_service_range(uint start,uint length,uchar kind,uchar *storage_class)

{
  uint uVar1;
  uint uVar2;
  
  if ((length != 0) && (uVar2 = (length + start) - 1, start <= uVar2)) {
    uVar1 = 0;
    do {
      if ((((f33_boot_service_range_policy[uVar1].kind_mask & 1 << (kind & 0x1f)) != 0) &&
          (f33_boot_service_range_policy[uVar1].lower <= start)) &&
         (uVar2 <= f33_boot_service_range_policy[uVar1].upper)) {
        *storage_class = f33_boot_service_range_policy[uVar1].storage_class;
        return 0;
      }
      uVar1 = uVar1 + 1;
    } while (uVar1 < 3);
  }
  return 1;
}



/* Same nonzero/no-wrap/kind-mask/inclusive predicates as32D2, but output8DA0 row byte+13.
   Return0/write output on match, else1/output unchanged. All current selector bytes are0;567E
   stores this as2B68 for completion bit updates. This is not the storage class or descriptor index.
    */

uint f33_boot_service_range_completion_selector
               (uint start,uint length,uchar kind,uchar *completion_selector)

{
  uint uVar1;
  uint uVar2;
  
  if ((length != 0) && (uVar2 = (length + start) - 1, start <= uVar2)) {
    uVar1 = 0;
    do {
      if ((((f33_boot_service_range_policy[uVar1].kind_mask & 1 << (kind & 0x1f)) != 0) &&
          (f33_boot_service_range_policy[uVar1].lower <= start)) &&
         (uVar2 <= f33_boot_service_range_policy[uVar1].upper)) {
        *completion_selector = f33_boot_service_range_policy[uVar1].completion_selector;
        return 0;
      }
      uVar1 = uVar1 + 1;
    } while (uVar1 < 3);
  }
  return 1;
}



/* Reject zero length; scan three28-byte8E00 records. First unsigned address>=lower and
   modulo32(address+length-1)<=upper wins; write selector. No separate overflow or address<=upper
   guard. Returns0found/1missing. Native zero-length CRC request stays pending unchanged while a
   separate stream completes; no hardware CRC acceptance claim. */

uint f33_boot_select_region_for_range(uint address,uint length,uint *region)

{
  uint uVar1;
  
  if (length != 0) {
    uVar1 = 0;
    do {
      if ((f33_boot_regions[(short)uVar1].lower <= address) &&
         ((length + address) - 1 <= f33_boot_regions[(short)uVar1].upper)) {
        *region = uVar1;
        return 0;
      }
      uVar1 = uVar1 + 1;
    } while (uVar1 < 3);
  }
  return 1;
}



/* Return0/write nonzero8E00 descriptor+8 pointer for nonzero length with lower<=start and modulo32
   end<=upper; else1/output unchanged. No explicit start<=end or start<=upper check. Current
   outputs17DF0/FFDF0/FEBF0FF0.7122 stores the pointer for7170 final16-byte comparison; lookup alone
   does not verify CRC or authentication. */

uint f33_boot_lookup_authentication_trailer(uint start,uint length,uint *trailer_address)

{
  short sVar1;
  uint uVar2;
  
  if (length != 0) {
    uVar2 = 0;
    do {
      sVar1 = (short)uVar2;
      if (((f33_boot_regions[sVar1].lower <= start) &&
          ((length + start) - 1 <= f33_boot_regions[sVar1].upper)) &&
         (f33_boot_regions[sVar1].authentication_trailer != 0)) {
        *trailer_address = f33_boot_regions[sVar1].authentication_trailer;
        return 0;
      }
      uVar2 = uVar2 + 1;
    } while (uVar2 < 3);
  }
  return 1;
}



/* Return0/write8E00 descriptor+12 marker address for nonzero length with lower<=start and modulo32
   end<=upper; else1/output unchanged. No explicit no-wrap check and no null-marker rejection:
   current outputs17E00/FFE00/0.5A04 caller is already kind4/class0 admitted before5286
   queues5AA5A55A at the marker. */

uint f33_boot_lookup_completion_marker(uint start,uint length,uint *marker_address)

{
  short sVar1;
  uint uVar2;
  
  if (length != 0) {
    uVar2 = 0;
    do {
      sVar1 = (short)uVar2;
      if ((f33_boot_regions[sVar1].lower <= start) &&
         ((length + start) - 1 <= f33_boot_regions[sVar1].upper)) {
        *marker_address = f33_boot_regions[sVar1].marker_block;
        return 0;
      }
      uVar2 = uVar2 + 1;
    } while (uVar2 < 3);
  }
  return 1;
}



/* Same inclusive modulo32 region search as335E, but output descriptor+16 counter-block address.
   Zero for RAM region2; no implicit overflow guard. */

uint f33_boot_select_counter_block_for_range(uint address,uint length,uint *counter_block)

{
  short sVar1;
  uint uVar2;
  
  if (length != 0) {
    uVar2 = 0;
    do {
      sVar1 = (short)uVar2;
      if ((f33_boot_regions[sVar1].lower <= address) &&
         ((length + address) - 1 <= f33_boot_regions[sVar1].upper)) {
        *counter_block = f33_boot_regions[sVar1].counter_block;
        return 0;
      }
      uVar2 = uVar2 + 1;
    } while (uVar2 < 3);
  }
  return 1;
}



/* Unsigned selector<3 returns region record+20 count; otherwise0. All exact records contain1. */

uint f33_boot_crc_descriptor_count(uint region)

{
  if (region < 3) {
    return f33_boot_regions[(short)region].crc_count;
  }
  return 0;
}



undefined4 FUN_00003460(int param_1,undefined4 param_2)

{
  (*(int (*)())*(code **)(param_1 + 4))(param_2);
  return 0;
}



/* Search38 half-open intervals in39-word86EC boundary array. Write containing lower bound
   andreturn0; otherwisewriteF8000 andreturn1. */

uint f33_boot_find_flash_block_start(uint address,uint *block_start)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  uint uVar5;
  
  uVar5 = 0xf8000;
  uVar4 = 1;
  iVar3 = 0;
  while( true ) {
    if ((f33_boot_flash_block_boundaries[iVar3] <= address) &&
       (address < f33_boot_flash_block_boundaries[iVar3 + 1])) break;
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -0x25;
    iVar3 = iVar2;
    if (iVar1 < 0 == (iVar2 < 0 && -1 < iVar1)) {
LAB_000034a2:
      *block_start = uVar5;
      return uVar4;
    }
  }
  uVar4 = 0;
  uVar5 = f33_boot_flash_block_boundaries[iVar3];
  goto LAB_000034a2;
}



/* Search same38 half-open intervals. Write containing upper bound andreturn0; otherwisewrite100000
   andreturn1. */

uint f33_boot_find_flash_block_end(uint address,uint *block_end)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  uint uVar5;
  
  uVar5 = 0x100000;
  uVar4 = 1;
  iVar3 = 0;
  while ((address < f33_boot_flash_block_boundaries[iVar3] ||
         (f33_boot_flash_block_boundaries[iVar3 + 1] <= address))) {
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -0x25;
    iVar3 = iVar2;
    if (iVar1 < 0 == (iVar2 < 0 && -1 < iVar1)) {
LAB_000034d4:
      *block_end = uVar5;
      return uVar4;
    }
  }
  uVar4 = 0;
  uVar5 = f33_boot_flash_block_boundaries[iVar3 + 1];
  goto LAB_000034d4;
}



/* Return zero-extended2954[containing block index], or0 outside38 intervals.4332 skips lower erase
   only for exact flag1. Do not infer a physical erased-state witness. */

uint f33_boot_get_flash_block_skip_flag(uint address)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = 0;
  while ((address < f33_boot_flash_block_boundaries[iVar3] ||
         (f33_boot_flash_block_boundaries[iVar3 + 1] <= address))) {
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -0x25;
    iVar3 = iVar2;
    if (iVar1 < 0 == (iVar2 < 0 && -1 < iVar1)) {
      return 0;
    }
  }
  return (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebf2954u + (uint32_t)(iVar3) * 1u))));
}



/* Invoke ROM86E4 pointerFEBF11F0, copied fromCF8560 by35E4, forwardingR6/R7 andreturningR10. This
   ECC-backed blank check is distinct from programming callback[FEBF0FD0]. */

uint f33_boot_check_relocated_blank_words(uint address,uint word_count)

{
  uint uVar1;
  
  uVar1 = (*(int (*)())f33_boot_relocated_blank_check_entry)(address,word_count);
  return uVar1;
}



/* Round nonzero byte length up256 with32-bit arithmetic, divideby4,
   andcall3552(address,word_count); normalize nonzero resultto1. Length0 reaches wrapped arithmetic
   andzero wordcount; do not add absent validation. Hardware ECC/test-mode feedback remains bounded.
    */

uint f33_boot_check_rounded_program_span_blank(uint address,uint length)

{
  uint uVar1;
  
  uVar1 = f33_boot_check_relocated_blank_words(address,(length - 1 & 0xffffff00) + 0x100 >> 2);
  return (uint)(uVar1 != 0);
}



void FUN_00003584(void)

{
  byte bVar1;
  undefined2 local_c;
  undefined2 uStack_a;
  undefined2 uStack_8;
  undefined2 uStack_6;
  
  while (bVar1 = FPMON, (bVar1 & 0x80) == 0) {
    local_c = 0x8800;
    uStack_a = 0;
    uStack_8 = 0xf000;
    uStack_6 = 0x1f00;
    FUN_0000167c(camry_host_addr(&local_c));
    FUN_00007208(0x50);
  }
  return;
}



void FUN_000035bc(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = 0;
  do {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebf2954u + (uint32_t)(iVar3) * 1u)))) = 0;
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -0x25;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  DAT_febf297a = 0;
  DAT_febf297b = 1;
  FUN_00003584();
  return;
}



/* Boot-phase relocation: copies 0xCB words from CodeFlash 0x8370..0x869B into RAM
   0xFEBF1000..0xFEBF132B, reads the last word back, then executes SYNCM and SYNCI. Exact CodeFlash
   execution checks the complete copied span and both canaries. The callback at 0xFEBF12B8
   corresponds to ROM 0x8628 in this phase; application crypto subsequently reuses the same RAM.
   This is not permanent RAM code. Boot phase: copies exactly 0xCB words from CodeFlash
   0x8370..0x869B to RAM 0xFEBF1000..0xFEBF132B, reads back the last word, SYNCM/SYNCI. Full copied
   span and both canaries executed. RAM callback FEBF12B8 maps to ROM 8628 only in this phase;
   application crypto reuses the RAM. Physical cache timing is not established. */

void f33_boot_copy_flash_driver_to_ram(void)

{
  int iVar1;
  undefined4 uVar2;
  uchar *puVar3;
  code *pcVar4;
  
  puVar3 = f33_nvm_family0_read_record + 0x378;
  pcVar4 = f33_boot_ram_dispatch;
  iVar1 = 0xcb;
  do {
    uVar2 = *(undefined4 *)pcVar4;
    pcVar4 = pcVar4 + 4;
    *(undefined4 *)puVar3 = uVar2;
    puVar3 = puVar3 + 4;
    iVar1 = iVar1 + -1;
  } while (iVar1 != 0);
  __synchronize();
  __synchronize();
  return;
}



void FUN_0000369c(void)

{
  uint uVar1;
  ushort uVar2;
  
  do {
    uVar1 = FSTATR;
  } while ((uVar1 >> 0xf & 1) == 0);
  FPCKAR = 0x1e28;
  FECCTMD = 0xa630;
  uVar2 = FECCTMD;
  __synchronize();
  return;
}



void FUN_000036be(void)

{
  F33BootInterruptEntry *pFVar1;
  
  pFVar1 = f33_boot_interrupt_dispatch;
  f33_boot_copy_flash_driver_to_ram();
  f33_boot_cache_set_enabled('\0');
  FUN_0000369c();
  (*(int (*)())pFVar1[9].handler)();
  return;
}



undefined4 FUN_000036de(int param_1,int param_2,int param_3,char param_4,byte param_5,uint *param_6)

{
  uint uVar1;
  undefined4 uVar2;
  
  uVar2 = 1;
  uVar1 = (param_1 * 0x10 + param_2) - 3U & 0xff;
  if ((((*((byte *)camry_host_ptr((uint32_t)((int)(0xffd202d0u) + uVar1)))) >> 3 & 1) == 0) &&
     (((*((byte *)camry_host_ptr((uint32_t)((int)(0xffd202d0u) + uVar1)))) & 6) == 0)) {
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xffd24000u + (uint32_t)(uVar1) * 32u)))) = param_3 + (uint)(param_4 != '\0') * -0x80000000;
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xffd24000u + (uint32_t)(uVar1) * 32u + 4u)))) = (uint)param_5 << 0x1c;
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xffd24000u + (uint32_t)(uVar1) * 32u + 12u)))) = *param_6;
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xffd24000u + (uint32_t)(uVar1) * 32u + 16u)))) = param_6[1];
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xffd24000u + (uint32_t)(uVar1) * 32u + 8u)))) = 0;
    FUN_00001d0e(((byte *)camry_host_ptr((uint32_t)((int)(0xffd20250u) + uVar1))), 0);
    uVar2 = 0;
  }
  return uVar2;
}



undefined4 FUN_0000374e(uint param_1,undefined4 *param_2)

{
  uint uVar1;
  uint32_t puVar2;
  uint uVar3;
  undefined4 uVar4;
  int iVar5;
  undefined4 uVar6;
  undefined1 auStack_1c [8];
  
  puVar2 = 0xfebf9800u;
  uVar6 = 2;
  uVar4 = FUN_0000721e(0xffff);
  uVar3 = (param_1 & 0x7f) >> 4;
  uVar1 = 0;
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(uVar3 - 0x6e83))))) == '\0') {
    for (; uVar1 < (*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 9)))); uVar1 = uVar1 + 1 & 0xff) {
      auStack_1c[uVar1] = *(undefined1 *)(param_2[1] + uVar1);
    }
    iVar5 = FUN_000036de(uVar3,param_1 & 0xf,*param_2,*(undefined1 *)(param_2 + 2),
                         (uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 9)))),auStack_1c);
    if (iVar5 == 0) {
      uVar6 = 0;
    }
    else {
      uVar6 = 2;
    }
  }
  FUN_00007244(uVar4);
  return uVar6;
}



void FUN_000037bc(int param_1,int param_2)

{
  uint uVar1;
  
  uVar1 = (param_1 * 0x10 + param_2) - 3U & 0xff;
  if (((*((byte *)camry_host_ptr((uint32_t)((int)(0xffd20250u) + uVar1)))) & 1) != 0) {
    FUN_00001d0e(((byte *)camry_host_ptr((uint32_t)((int)(0xffd20250u) + uVar1))), 1);
  }
  return;
}



void FUN_000037e4(uint param_1)

{
  uint32_t puVar1;
  uint uVar2;
  undefined4 uVar3;
  
  puVar1 = 0xfebf9800u;
  uVar3 = FUN_0000721e(0xffff);
  uVar2 = (param_1 & 0x7f) >> 4;
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(uVar2 - 0x6e83))))) == '\0') {
    FUN_000037bc(uVar2,param_1 & 0xf);
  }
  FUN_00007244(uVar3);
  return;
}



void FUN_00003818(void)

{
  uint uVar1;
  
  do {
    uVar1 = GSTS;
  } while ((uVar1 >> 3 & 1) != 0);
  return;
}



void FUN_00003824(void)

{
  uint uVar1;
  
  uVar1 = GCTR;
  if ((uVar1 & 4) == 4) {
    uVar1 = GCTR;
    uVar1 = uVar1 & 0xfffffffb;
  }
  else {
    uVar1 = GCTR;
    if ((uVar1 & 3) != 0) {
      return;
    }
    uVar1 = GCTR;
    uVar1 = uVar1 & 0xfffffffc | 1;
  }
  GCTR = uVar1;
  __synchronize();
  FUN_00007208(8);
  return;
}



void FUN_0000386c(void)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  RSCFD_TxMessageBuffer *pRVar4;
  int iVar5;
  
  DAT_ffd20500 = 0;
  DAT_ffd20520 = 0;
  DAT_ffd20540 = 0;
  DAT_ffd20504 = 0;
  DAT_ffd20524 = 0;
  DAT_ffd20544 = 0;
  DAT_ffd20508 = 0;
  DAT_ffd20528 = 0;
  DAT_ffd20548 = 0;
  DAT_ffd2050c = 0;
  DAT_ffd2052c = 0;
  DAT_ffd2054c = 0;
  iVar5 = 0;
  do {
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xffd24000u + (uint32_t)(iVar5) * 32u + 8u)))) = 0;
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xffd24000u + (uint32_t)(iVar5) * 32u)))) = 0;
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xffd24000u + (uint32_t)(iVar5) * 32u + 4u)))) = 0;
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xffd24000u + (uint32_t)(iVar5) * 32u + 12u)))) = 0;
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xffd24000u + (uint32_t)(iVar5) * 32u + 16u)))) = 0;
    pRVar4 = ((RSCFD_TxMessageBuffer *)camry_host_ptr((uint32_t)(0xffd24000u + (uint32_t)(iVar5) * 32u)));
    pRVar4->reserved_14_1f[0] = '\0';
    pRVar4->reserved_14_1f[1] = '\0';
    pRVar4->reserved_14_1f[2] = '\0';
    pRVar4->reserved_14_1f[3] = '\0';
    pRVar4 = ((RSCFD_TxMessageBuffer *)camry_host_ptr((uint32_t)(0xffd24000u + (uint32_t)(iVar5) * 32u)));
    pRVar4->reserved_14_1f[4] = '\0';
    pRVar4->reserved_14_1f[5] = '\0';
    pRVar4->reserved_14_1f[6] = '\0';
    pRVar4->reserved_14_1f[7] = '\0';
    iVar2 = iVar5 + 1;
    pRVar4 = ((RSCFD_TxMessageBuffer *)camry_host_ptr((uint32_t)(0xffd24000u + (uint32_t)(iVar5) * 32u)));
    pRVar4->reserved_14_1f[8] = '\0';
    pRVar4->reserved_14_1f[9] = '\0';
    pRVar4->reserved_14_1f[10] = '\0';
    pRVar4->reserved_14_1f[0xb] = '\0';
    iVar1 = iVar5 + -0x2f;
    iVar5 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  DAT_ffd20098 = 0x100;
  uVar3 = DAT_ffd20098;
  __synchronize();
  iVar5 = 0;
  do {
    iVar1 = iVar5 * 0x10;
    *(undefined4 *)(((undefined *)camry_host_ptr(0xffd21000u)) + iVar1) = 0;
    *(undefined4 *)(((undefined *)camry_host_ptr(0xffd21004u)) + iVar1) = 0;
    *(undefined4 *)(((undefined *)camry_host_ptr(0xffd21008u)) + iVar1) = 0;
    iVar2 = iVar5 + 1;
    *(undefined4 *)(((undefined *)camry_host_ptr(0xffd2100cu)) + iVar1) = 0;
    iVar1 = iVar5 + -0xf;
    iVar5 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  DAT_ffd20098 = 0;
  uVar3 = DAT_ffd20098;
  __synchronize();
  return;
}



void FUN_00003908(void)

{
  undefined4 uVar1;
  
  DAT_ffd204fc = 1;
  uVar1 = DAT_ffd204fc;
  __synchronize();
  return;
}



void FUN_00003918(uint param_1)

{
  int iVar1;
  
  iVar1 = (param_1 & 0xff) * 0x10;
  *(uint *)(((undefined *)camry_host_ptr(0xffd20004u)) + iVar1) = *(uint *)(((undefined *)camry_host_ptr(0xffd20004u)) + iVar1) & 0xfffffffb;
  __synchronize();
  FUN_00007208(8);
  return;
}



void FUN_00003942(void)

{
  DAT_ffd20474 = 0;
  DAT_ffd200a4 = 0;
  DAT_ffd20118 = 0;
  DAT_ffd2011c = 0;
  DAT_ffd20120 = 0;
  CFCC3 = 0;
  DAT_ffd20128 = 0;
  CFCC5 = 0;
  DAT_ffd20130 = 0;
  DAT_ffd20134 = 0;
  DAT_ffd20138 = 0;
  DAT_ffd20394 = 0;
  return;
}



void FUN_0000396c(void)

{
  GCFG = 0xffff0000;
  return;
}



void FUN_00003978(uint param_1)

{
  *(undefined4 *)(((undefined *)camry_host_ptr(0xffd20000u)) + (param_1 & 0xff) * 0x10) = 0xf3e7800;
  (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xffd20500u + (uint32_t)((param_1 & 0xff) * 8) * 4u)))) = 0x55c0000;
  return;
}



void FUN_00003998(uint param_1,undefined1 param_2)

{
  (*((undefined1 *)camry_host_ptr((uint32_t)((int)0xffd2009cu + (3 - (param_1 & 0xff)))))) = param_2;
  return;
}



void FUN_000039a6(uint param_1)

{
  uint uVar1;
  undefined4 uVar2;
  
  uVar1 = DAT_ffd20098;
  DAT_ffd20098 = uVar1 & 0xfffffeff | (param_1 & 0xff) << 8;
  uVar2 = DAT_ffd20098;
  __synchronize();
  return;
}



void FUN_000039c0(uint param_1)

{
  uint uVar1;
  undefined4 uVar2;
  
  uVar1 = DAT_ffd20098;
  DAT_ffd20098 = param_1 & 0xff | uVar1 & 0xffffffe0;
  uVar2 = DAT_ffd20098;
  __synchronize();
  return;
}



void FUN_000039d6(short param_1,int param_2,uint param_3,int param_4,char param_5,int param_6)

{
  int iVar1;
  
  iVar1 = (param_3 & 0xff) * 0x10;
  *(uint *)(((undefined *)camry_host_ptr(0xffd21000u)) + iVar1) = param_4 + (uint)(param_5 != '\0') * -0x80000000;
  *(int *)(((undefined *)camry_host_ptr(0xffd21004u)) + iVar1) = param_6 + -0x40000000;
  *(undefined4 *)(((undefined *)camry_host_ptr(0xffd21008u)) + iVar1) = 0;
  *(int *)(((undefined *)camry_host_ptr(0xffd2100cu)) + iVar1) = (1 << (param_2 + param_1 * 3 & 0x1fU)) << 8;
  return;
}



void FUN_00003a18(short param_1,int param_2,char param_3)

{
  (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xffd20118u + (uint32_t)(param_2 + param_1 * 3 & 0xff) * 4u)))) = (uint)(param_3 != '\0') * 2 + 0x1100;
  return;
}



void FUN_00003a36(int param_1,int param_2,char param_3)

{
  uint uVar1;
  uint *puVar2;
  
  uVar1 = (param_2 + param_1 * 0x10) - 3U & 0xff;
  if (uVar1 < 0x20) {
    puVar2 = ((undefined *)camry_host_ptr(0xffd20390u));
  }
  else {
    puVar2 = ((undefined *)camry_host_ptr(0xffd20394u));
    uVar1 = uVar1 - 0x20;
  }
  *puVar2 = *puVar2 | (uint)(param_3 != '\0') << (uVar1 & 0x1f);
  return;
}



void FUN_00003a6a(uint param_1,short param_2)

{
  int iVar1;
  
  iVar1 = (param_1 & 0xff) * 0x10;
  *(uint *)(((undefined *)camry_host_ptr(0xffd20004u)) + iVar1) =
       *(uint *)(((undefined *)camry_host_ptr(0xffd20004u)) + iVar1) & 0x781000f7 | (uint)(param_2 != 0) << 0x10;
  return;
}



void FUN_00003a8e(uint param_1)

{
  (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xffd20504u + (uint32_t)((param_1 & 0xff) * 8) * 4u)))) = 0x20000000;
  return;
}



void FUN_00003a9e(uint param_1,short param_2)

{
  FUN_00001bbe(*(undefined2 *)(((undefined *)camry_host_ptr(0x878cu)) + (param_1 & 0xff) * 2),param_2 != 0);
  return;
}



void FUN_00003aba(uint param_1,short param_2)

{
  FUN_00001bbe(*(undefined2 *)(((undefined *)camry_host_ptr(0x8792u)) + (param_1 & 0xff) * 2),param_2 != 0);
  return;
}



void FUN_00003ad6(void)

{
  uint uVar1;
  
  uVar1 = GCTR;
  GCTR = uVar1 & 0xfffffffc;
  uVar1 = GCTR;
  __synchronize();
  FUN_00007208(1);
  return;
}



void FUN_00003af4(uint param_1)

{
  int iVar1;
  
  iVar1 = (param_1 & 0xff) * 0x10;
  *(uint *)(((undefined *)camry_host_ptr(0xffd20004u)) + iVar1) = *(uint *)(((undefined *)camry_host_ptr(0xffd20004u)) + iVar1) & 0xfffffffc;
  __synchronize();
  FUN_00007208(0x10);
  return;
}



void FUN_00003b20(short param_1,int param_2)

{
  uint uVar1;
  
  uVar1 = param_1 * 3 + param_2 & 0xff;
  (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xffd20118u + (uint32_t)(uVar1) * 4u)))) = (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xffd20118u + (uint32_t)(uVar1) * 4u)))) | 1;
  return;
}



int FUN_00003e1c(uint param_1)

{
  uint *puVar1;
  
  if ((param_1 & 0xff) < 2) {
    puVar1 = ((undefined *)camry_host_ptr(0xffd20370u));
  }
  else {
    puVar1 = ((undefined *)camry_host_ptr(0xffd20374u));
  }
  return ((puVar1[4] | *puVar1) >> ((param_1 & 1) << 4) & 0x1fff) << 3;
}



int FUN_00003e48(int param_1,int param_2)

{
  return (int)((*((byte *)camry_host_ptr((uint32_t)((int)(0xffd202d0u) + ((param_2 + param_1 * 0x10) - 3U & 0xff))))) & 6) >> 1;
}



void FUN_00003e5e(int param_1,int param_2)

{
  uint uVar1;
  
  uVar1 = (param_2 + param_1 * 0x10) - 3U & 0xff;
  (*((byte *)camry_host_ptr((uint32_t)((int)(0xffd202d0u) + uVar1)))) = (*((byte *)camry_host_ptr((uint32_t)((int)(0xffd202d0u) + uVar1)))) & 0xf9;
  __synchronize();
  return;
}



void FUN_00003e80(int param_1,int param_2,uint *param_3,byte *param_4)

{
  uint uVar1;
  
  uVar1 = (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xffd24000u + (uint32_t)((param_2 + param_1 * 0x10) - 3U & 0xff) * 32u))));
  *param_4 = (byte)(uVar1 >> 0x1f);
  *param_3 = uVar1 & 0x1fffffff;
  return;
}



uint FUN_00003f4a(ushort param_1)

{
  uint uVar1;
  
  uVar1 = DAT_ffd20248;
  return uVar1 >> ((short)(param_1 & 0xff) * 3 & 0x1fU) & 7;
}



uint FUN_00003f60(short param_1,int param_2)

{
  return ((((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xffd20178u + (uint32_t)(param_2 + param_1 * 3 & 0xff) * 4u))))) >> 3) & 1u);
}



void FUN_00003f78(short param_1,int param_2)

{
  RSCFD_CFSTS *pRVar1;
  
  pRVar1 = ((RSCFD_CFSTS *)camry_host_ptr((uint32_t)(0xffd20178u + (uint32_t)((param_1 * 3 + param_2 & 0xff)) * 4u)));
  pRVar1->reserved_0_2 = 4;
  pRVar1->reserved_4_31 = 1;
  pRVar1->status_b3 = 0;
  __synchronize();
  return;
}



bool FUN_00003f96(undefined1 param_1,uint param_2,undefined4 param_3,undefined4 param_4,
                 byte *param_5,uint *param_6)

{
  short extraout_r6;
  uint *extraout_r8;
  byte *extraout_r9;
  int iVar1;
  uint uVar2;
  uint uVar3;
  
  iVar1 = FUN_00003f60(param_1, (uint)(byte)param_2);
  if (iVar1 != 0) {
    FUN_00003f78((uint)(byte)param_1, (uint)(byte)param_2);
    uVar3 = (param_2 & 0xff) + extraout_r6 * 3 & 0xff;
    uVar2 = (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xffd23400u + (uint32_t)(uVar3 * 4) * 32u))));
    *extraout_r9 = (byte)(uVar2 >> 0x1f);
    *extraout_r8 = uVar2 & 0x1fffffff;
    *param_5 = (byte)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xffd23400u + (uint32_t)(uVar3 * 4) * 32u + 4u)))) >> 0x1c);
    *param_6 = (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xffd23400u + (uint32_t)(uVar3 * 4) * 32u + 12u))));
    param_6[1] = (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xffd23400u + (uint32_t)(uVar3 * 4) * 32u + 16u))));
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xffd201d8u + (uint32_t)(uVar3) * 4u)))) = 0xff;
  }
  return iVar1 == 0;
}


