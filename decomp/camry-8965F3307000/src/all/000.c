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



void FUN_000014a2(void)

{
  if (DAT_febf2904 == '\x02') {
    FUN_00001d9a();
    FUN_00000780();
    FUN_00002250();
  }
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



void FUN_00001e10(void)

{
  FUN_0000721e(0xffff);
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}



void FUN_00001e36(void)

{
  FUN_0000721e(0xffff);
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
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



void FUN_00001ec0(undefined2 param_1,undefined4 *param_2)

{
  undefined4 local_c;
  undefined2 uStack_8;
  
  local_c = *param_2;
  uStack_8 = *(undefined2 *)(param_2 + 1);
  FUN_00004606(param_1,&local_c);
  return;
}



undefined4 FUN_00001ede(undefined2 param_1)

{
  FUN_000045b2(param_1);
  return 0;
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



void FUN_000029e4(undefined4 param_1,undefined1 param_2,byte param_3)

{
  if (((((int8_t)DAT_febf2931) == -0x6f) && (DAT_febf2935 = param_2, DAT_febf2936 = param_3, 0x7f < param_3))
     && (DAT_febf2936 = 1, 8 < param_3 - 0xf1)) {
    DAT_febf2936 = 0x7f;
  }
  return;
}



void FUN_00002aca(undefined1 param_1)

{
  DAT_febf2934 = 0;
  FUN_00002a12(param_1,DAT_febf2932,DAT_00008d8c);
  return;
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



uint FUN_00003f4a(ushort param_1)

{
  uint uVar1;
  
  uVar1 = DAT_ffd20248;
  return uVar1 >> ((short)(param_1 & 0xff) * 3 & 0x1fU) & 7;
}


