#include "common.h"


void FUN_00078010(undefined2 param_1,undefined1 *param_2)

{
  undefined1 uVar1;
  int iVar2;
  char cStack_e;
  char cStack_d;
  
  *param_2 = 0xd;
  iVar2 = camry_host_addr(FUN_00077f26(param_1,2,&cStack_d));
  if (((iVar2 == 1) && (cStack_d == 'U')) && (iVar2 = camry_host_addr(FUN_00077f26(param_1,1,&cStack_e)), iVar2 == 1)
     ) {
    if (cStack_e == 'U') {
      uVar1 = 0xf;
    }
    else {
      uVar1 = 0xff;
    }
    *param_2 = uVar1;
  }
  return;
}



undefined4 FUN_0007812a(void)

{
  undefined4 uVar1;
  
  uVar1 = FUN_000789e2();
  thunk_FUN_000764c2();
  return uVar1;
}



void FUN_0007813e(undefined1 param_1)

{
  FUN_0007998a(param_1);
  return;
}



undefined4 FUN_0007814c(void)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = FUN_00076762();
  if (iVar1 == 0) {
    DAT_febf6c5c = 1;
    FUN_00076772();
    DAT_febf6c5c = 0;
    uVar2 = 2;
  }
  else {
    uVar2 = FUN_00078a56();
  }
  return uVar2;
}



void FUN_00078176(void)

{
  int iVar1;
  
  iVar1 = FUN_00076762();
  DAT_febf6c5c = 1;
  if (iVar1 == 0) {
    FUN_00076772();
  }
  else {
    FUN_00078766();
  }
  DAT_febf6c5c = 0;
  return;
}



/* Single constant publisher: DAT_febf6c5c = 0; Shape-classified from the canonical corpus; the
   target cell is not yet named, so the written state's meaning is unknown. */

void FUN_000781a0(void)

{
  DAT_febf6c5c = 0;
  return;
}



void FUN_000781aa(undefined1 param_1)

{
  DAT_febf6c5b = param_1;
  return;
}



undefined1 FUN_000781b4(void)

{
  return DAT_febf6c5b;
}



void FUN_000781be(void)

{
  int iVar1;
  
  DAT_febf6c5c = 0;
  iVar1 = FUN_00078aca();
  if (iVar1 != 0xe) {
    FUN_00078766();
  }
  return;
}



undefined1 FUN_000781da(void)

{
  return DAT_febf6c5c;
}



/* Constant-block fill: 5 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_781e4(void)

{
  DAT_febf6c20 = 0;
  DAT_febf6c4f = 0xff;
  DAT_febf6c4e = 0;
  DAT_febf6c4d = 0xff;
  DAT_febf6c1c = 1;
  return;
}



undefined1 FUN_000782b2(void)

{
  return DAT_febf6c4d;
}



/* WARNING: Type propagation algorithm not settling */

void FUN_00078304(void)

{
  uint32_t puVar1;
  undefined1 uVar2;
  uint uVar3;
  int local_34 [2];
  undefined2 uStack_2c;
  undefined2 uStack_2a;
  undefined4 uStack_28;
  undefined4 uStack_24;
  undefined1 uStack_1c;
  char cStack_1b;
  int *piStack_18;
  
  puVar1 = 0x23dfcu;
  local_34[0] = 1;
  uVar3 = FUN_000782b2();
  if (uVar3 < 2) {
    uStack_24 = 0;
    uStack_28 = 0;
    uStack_2a = 0xffff;
    uStack_2c = 0;
    local_34[1] = 0xffffffff;
    FUN_000782bc();
    if (((int8_t)DAT_febf6c4f) == -1) {
      DAT_febf6c4f = '\0';
    }
    uStack_1c = DAT_febf6c4e;
    piStack_18 = local_34 + 1;
    cStack_1b = DAT_febf6c4f;
    uVar2 = ((void)(local_34), FUN_00078276(((byte *)camry_host_ptr((uint32_t)((*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + uVar3 * 4 + 0x3ec4))))))), &uStack_1c));
    DAT_febf6c4f = 0xff;
    if (local_34[0] != 1) {
      FUN_00077ce8();
      FUN_00077d14(local_34[0]);
      f33_nvm_finish_physical_result();
      f33_fill_constant_block_781e4();
      FUN_000782de();
      uVar2 = DAT_febf6c4e;
    }
  }
  else {
    DAT_febf6c4f = 0xff;
    DAT_febf6c4d = 0xff;
    DAT_febf6c4e = 0;
    DAT_febf6c1c = 1;
    uVar2 = DAT_febf6c4e;
  }
  DAT_febf6c4e = uVar2;
  return;
}



void FUN_000783b6(undefined1 param_1)

{
  DAT_febf6c4d = param_1;
  return;
}



void FUN_000783c0(undefined1 param_1)

{
  DAT_febf6c4f = param_1;
  return;
}



void FUN_000783ca(undefined4 param_1)

{
  DAT_febf6c1c = param_1;
  return;
}



undefined4 FUN_000783d4(void)

{
  return DAT_febf6c1c;
}



void FUN_000783de(undefined4 param_1)

{
  DAT_febf6c20 = param_1;
  return;
}



void FUN_000783e8(void)

{
  int iVar1;
  
  iVar1 = FUN_00077c64();
  if ((iVar1 == 0) || (iVar1 != 1 && iVar1 != 2)) {
    FUN_000783b6(0xff);
  }
  else {
    FUN_00074f4a();
  }
  return;
}



void FUN_0007840c(void)

{
  FUN_000783e8();
  ((void)(1), FUN_00078304());
  return;
}



void FUN_00078466(void)

{
  FUN_000783e8();
  ((void)(0), FUN_00078304());
  FUN_0007841e();
  return;
}



void FUN_00078500(void)

{
  bool bVar1;
  uint uVar2;
  int iVar3;
  undefined4 unaff_r27;
  
  f33_return_only_stub_79d32();
  uVar2 = f33_icus20_second_read_bit0();
  if (uVar2 == 0) {
    FUN_00078b90();
    FUN_00078c12();
    iVar3 = FUN_00078d3e();
    if (iVar3 == 0) {
      FUN_00078b1c();
      FUN_00078b60();
      bVar1 = false;
      goto LAB_00078542;
    }
    unaff_r27 = 5;
  }
  else {
    unaff_r27 = 0x82;
  }
  bVar1 = true;
  DAT_febf6cb1 = 1;
LAB_00078542:
  f33_return_only_stub_79d34();
  if (bVar1) {
    FUN_0007939c(0x5c,0,0,unaff_r27);
  }
  else {
    FUN_00078bb0();
    DAT_febf6cb1 = 0;
  }
  return;
}



int FUN_0007867a(uint param_1,uint param_2)

{
  undefined4 uVar1;
  uint uVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  
  uVar2 = f33_icus20_second_read_bit0();
  if (uVar2 == 0) {
    if (DAT_febf6cb0 == '\x01') {
      if (DAT_febf6cb2 == '\x0e') {
        iVar3 = FUN_00078d88(param_1,0x40);
        if (iVar3 != 0) {
          uVar1 = 2;
          goto LAB_00078754;
        }
        iVar3 = FUN_00078dca(param_1,param_2);
        if (iVar3 != 0) {
          uVar1 = 3;
          goto LAB_00078754;
        }
        f33_return_only_stub_79d32();
        FUN_00078bc6();
        iVar4 = FUN_00078c70(0x80);
        iVar3 = 1;
        if (iVar4 != 0) {
          f33_return_only_stub_79d34();
          FUN_00078c70(0);
          uVar1 = 7;
          goto LAB_00078754;
        }
        f33_flash_set_software_enables(1);
        uVar2 = param_2 >> 6;
        if ((param_2 & 0x3f) != 0) {
          uVar2 = uVar2 + 1;
        }
        uVar5 = f33_faci_submit_range_command(param_1,param_1 + 0x3f,' ');
        f33_return_only_stub_79d34();
        if (uVar5 == 1) {
          DAT_febf6c60 = param_1 + 0x40;
          DAT_febf6c68 = uVar2 * 0x40 + param_1 + -1;
          DAT_febf6cac = 1;
          DAT_febf6cb0 = 2;
          DAT_febf6cb1 = 2;
          return 0;
        }
        FUN_00078f7a();
        f33_flash_set_software_enables(0);
        FUN_00078c70(0);
        uVar1 = 7;
      }
      else {
        uVar1 = 0x83;
      }
    }
    else {
      uVar1 = 6;
    }
  }
  else {
    uVar1 = 0x82;
  }
  iVar3 = 1;
LAB_00078754:
  FUN_0007939c(0x5c,0,1,uVar1);
  return iVar3;
}



void FUN_00078766(void)

{
  uint uVar1;
  int iVar2;
  undefined4 unaff_r27;
  undefined1 uStack_11;
  
  uVar1 = f33_icus20_second_read_bit0();
  if (uVar1 == 0) {
    f33_return_only_stub_79d32();
    FUN_00078b90();
    f33_return_only_stub_79d34();
    iVar2 = FUN_00078d3e();
    if (iVar2 == 0) {
      if (DAT_febf6cb1 == '\x02') {
        DAT_febf6cb1 = '\x03';
        FUN_00074ed0();
      }
      FUN_00078af8();
      DAT_febf6cb0 = 1;
      if (DAT_febf6cb2 == '\x0f') {
        uStack_11 = 5;
        FUN_000793dc(&uStack_11);
      }
      DAT_febf6cb3 = 0;
      DAT_febf6cb2 = '\x0e';
    }
    else {
      unaff_r27 = 6;
      DAT_febf6cb1 = '\x01';
    }
    f33_flash_set_software_enables(0);
    if (iVar2 == 0) {
      return;
    }
  }
  else {
    unaff_r27 = 0x82;
    DAT_febf6cb1 = '\x01';
  }
  FUN_0007939c(0x5c,0,3,unaff_r27);
  return;
}



undefined1 FUN_0007888c(void)

{
  return DAT_febf6cb0;
}



undefined1 FUN_00078896(void)

{
  return DAT_febf6cb1;
}



/* Ordered ICU-S/software-state/range gates match788B6 except there is no destination argument.
   Enter DataFlash P/E, enable both FHVE controls, set operation3 and submit71,D0. Poll status,
   leave P/E and disable enables on the completed path. Return2 for blank, 7 for nonblank,8 for
   completion/setup failure; admissionB/4/C/3. Native blank/nonblank results are explicit hardware
   inputs. Timeout reaches realB3 forced-stop; its completion is also an explicit hardware input.
   Ordered ICU-S/software/range gates; DataFlash P/E setup and both FHVE enables; operation3;
   submit71,D0; poll and classify completion; restore read mode and disable enables on completed
   path. Explicit blank/nonblank inputs return2/7 at the final DataFlash word. No completion is
   synthesized. B3 is now modeled with explicit completion, but full blank-check timeout recovery
   and physical timing remain bounded. */

uint f33_dataflash_blank_check(uint dataflash_offset,uint byte_count)

{
  uint uVar1;
  int iVar2;
  
  uVar1 = f33_icus20_second_read_bit0();
  if (uVar1 == 0) {
    if (DAT_febf6cb0 == '\x01') {
      if (DAT_febf6cb2 == '\x0e') {
        iVar2 = FUN_00078d88(dataflash_offset,4);
        if ((iVar2 == 0) && (iVar2 = FUN_00078d9e(dataflash_offset,byte_count,4), iVar2 == 0)) {
          f33_return_only_stub_79d32();
          FUN_00078bc6();
          iVar2 = FUN_00078c70(0x80);
          if (iVar2 == 0) {
            f33_flash_set_software_enables(1);
            DAT_febf6cac = 3;
            uVar1 = f33_faci_submit_range_command
                              (dataflash_offset,(byte_count + dataflash_offset) - 1,'q');
            f33_return_only_stub_79d34();
            if (uVar1 == 1) {
              uVar1 = FUN_000791b2();
            }
            else {
              FUN_00078f7a();
              FUN_00078c70(0);
              uVar1 = 8;
            }
            f33_flash_set_software_enables(0);
          }
          else {
            f33_return_only_stub_79d34();
            FUN_00078c70(0);
            uVar1 = 8;
          }
        }
        else {
          uVar1 = 3;
        }
      }
      else {
        uVar1 = 0xc;
      }
    }
    else {
      uVar1 = 4;
    }
  }
  else {
    uVar1 = 0xb;
  }
  return uVar1;
}



int FUN_000789e2(void)

{
  uint uVar1;
  int iVar2;
  undefined1 uStack_d;
  
  uVar1 = f33_icus20_second_read_bit0();
  if (uVar1 == 0) {
    if (DAT_febf6cb2 == '\x0e') {
      if (DAT_febf6cb0 == '\x02') {
        FUN_000793c8(&uStack_d);
        iVar2 = FUN_0007922c(uStack_d);
        if (iVar2 == 2) {
          DAT_febf6cb2 = 0xf;
          f33_return_only_stub_79d32();
          FUN_000792dc();
          f33_return_only_stub_79d34();
          return 2;
        }
        if (iVar2 != 10) {
          return iVar2;
        }
        iVar2 = FUN_0007927e();
        if (iVar2 != 0) {
          return 8;
        }
      }
      iVar2 = 10;
      DAT_febf6cb2 = '\x10';
    }
    else {
      iVar2 = 0xc;
    }
  }
  else {
    iVar2 = 0xb;
  }
  return iVar2;
}



undefined4 FUN_00078a56(void)

{
  uint uVar1;
  int iVar2;
  
  uVar1 = f33_icus20_second_read_bit0();
  if (uVar1 != 0) {
    return 0xb;
  }
  if (DAT_febf6cb2 != '\x10') {
    return 0xc;
  }
  if (DAT_febf6cb0 == '\x02') {
    f33_return_only_stub_79d32();
    FUN_00078bc6();
    f33_return_only_stub_79d34();
    iVar2 = FUN_00078c70(0x80);
    if (iVar2 != 0) {
LAB_00078ab8:
      FUN_00078c70(0);
      return 8;
    }
    f33_flash_set_software_enables(1);
    if (DAT_febf6cb3 == '\x01') {
      FUN_000792c0();
    }
    else {
      iVar2 = FUN_000792a6();
      if (iVar2 != 0) goto LAB_00078ab8;
    }
  }
  DAT_febf6cb2 = 0xe;
  return 2;
}



undefined1 FUN_00078aca(void)

{
  return DAT_febf6cb2;
}



/* WARNING: This is an inlined function */
/* MOV r6,EP; SLD.W [EP],r10; JMP LP. Preserve r6/r7/r8. Inline the real p-code so repeated ICU-S
   reads and the DataFlash ECC-clear pointer/value retain their actual register dataflow. Read the
   full word throughr6 into r10 using EP. Real p-code inlining recovers both ICU-S reads and the
   later ECC-clear pointer/value instead of inferred extraout arguments. Native scenarios execute
   the actual repeated loads and DataFlash copy. */

uint f33_load_u32(uint *source)

{
  return *source;
}



void FUN_00078af8(void)

{
  int iVar1;
  uint uVar2;
  
  DAT_febf6c64 = 0;
  uVar2 = 0;
  DAT_febf6c60 = 0;
  DAT_febf6c68 = 0;
  DAT_febf6cac = 0;
  do {
    iVar1 = uVar2 * 4;
    uVar2 = uVar2 + 1;
    *(undefined4 *)(((undefined *)camry_host_ptr(0xfebf6c6cu)) + iVar1) = 0;
  } while (uVar2 < 0x10);
  return;
}



void FUN_00078b1c(void)

{
  FUN_00078af8();
  DAT_febf6cb1 = 1;
  DAT_febf6cb3 = 0;
  DAT_febf6cb2 = 0xe;
  DAT_febf6cb0 = 1;
  return;
}



/* WARNING: Inlined function: f33_store_u32 */
/* WARNING: Inlined function: f33_load_u32 */
/* WARNING: Inlined function: f33_syncp */
/* Write full32 input to FHVE15 atFFF8A430 then FHVE3 atFFF82410; read back FHVE3 and SYNCP.
   Hardware exposes only bit0; both enables are required for programming/erasure/blank checking.
   This function does not validate the input or verify both values. Write full input to FHVE15 then
   FHVE3; Hardware exposes bit0 and requires both enables. Native completed record path enables both
   before command submission and disables both afterward; no local argument validation or
   verification of both values. */

void f33_flash_set_software_enables(uint value)

{
  uint uVar1;
  
  FHVE15 = value;
  FHVE3 = value;
  uVar1 = FHVE3;
  __synchronize();
  return;
}



/* WARNING: Inlined function: f33_store_u8 */
/* WARNING: Inlined function: f33_store_u16 */

void FUN_00078b60(void)

{
  FAEINT = '\0';
  FSUINITR = 0x2d00;
  FRTEINT = '\0';
  f33_flash_set_software_enables(0);
  return;
}



/* WARNING: Inlined function: f33_load_u8 */
/* WARNING: Inlined function: f33_store_u8 */
/* WARNING: Inlined function: f33_syncp */

undefined1 FUN_00078b90(void)

{
  byte bVar1;
  undefined1 uVar2;
  
  bVar1 = (*((volatile uint8_t *)camry_host_ptr(0xffffb2f6u)));
  (*((volatile uint8_t *)camry_host_ptr(0xffffb2f6u))) = bVar1 | 0x80;
  uVar2 = (*((volatile uint8_t *)camry_host_ptr(0xffffb2f6u)));
  __synchronize();
  return uVar2;
}



/* WARNING: Inlined function: f33_store_u16 */

void FUN_00078bb0(void)

{
  FPCKAR = 0x1e28;
  return;
}



/* WARNING: Inlined function: f33_store_u16 */
/* WARNING: Inlined function: f33_store_u8 */

void FUN_00078bc6(void)

{
  FUN_00078b90();
  FSUINITR = 0x2d00;
  FECCTMD = 0xa630;
  FLEMU = '\0';
  FUN_00078bb0();
  return;
}



/* WARNING: Inlined function: f33_load_u32 */

uint FUN_00078bfa(void)

{
  uint uVar1;
  
  uVar1 = FSTATR;
  return (uVar1 & 0x8000) >> 0xf;
}



/* WARNING: Inlined function: f33_store_u16 */

void FUN_00078c12(void)

{
  int iVar1;
  
  iVar1 = FUN_00078bfa();
  if (iVar1 == 1) {
    FSUINITR = 0x2d00;
  }
  return;
}



/* WARNING: Inlined function: f33_load_u32 */
/* WARNING: Inlined function: f33_load_u8 */
/* WARNING: Inlined function: f33_store_u8 */

void FUN_00078c30(void)

{
  uchar uVar1;
  uint uVar2;
  
  uVar2 = FSTATR;
  if (((uVar2 & 0x4000) == 0x4000) && (uVar1 = FASTAT, uVar1 != '\x10')) {
    FASTAT = '\x10';
  }
  FACI_COMMAND_AREA = 'P';
  return;
}



/* WARNING: Inlined function: f33_load_u32 */
/* WARNING: Inlined function: f33_store_u16 */
/* WARNING: Inlined function: f33_load_u16 */
/* WARNING: Inlined function: f33_store_u32 */

undefined4 FUN_00078c70(ushort param_1)

{
  uint uVar1;
  ushort uVar2;
  undefined4 uVar3;
  
  if (param_1 == 0) {
    uVar1 = FSTATR;
    if ((uVar1 & 0x7000) != 0) {
      FUN_00078c30();
    }
    FENTRYR = 0xaa00;
  }
  else {
    uVar2 = FENTRYR;
    if (param_1 != (uVar2 & 0x81)) {
      FENTRYR = 0xaa80;
      FSADDR = 0;
      FEADDR = 0;
    }
  }
  uVar2 = FENTRYR;
  uVar2 = FENTRYR;
  if (param_1 == (uVar2 & 0x81)) {
    uVar3 = 0;
  }
  else {
    uVar3 = 7;
  }
  return uVar3;
}



/* WARNING: Inlined function: f33_load_u32 */
/* WARNING: Inlined function: f33_load_u8 */
/* WARNING: Inlined function: f33_store_u8 */
/* If FSTATR.ILGLERR and FASTAT!=10, write FASTAT10. IssueB3, then793F0(FSTATR,8000,8000,E5);
   return0 for poll0/1, else8. Actual mask precedence makes poll1 unreachable for these identical
   masks. No P/E entry/exit or automatic completion; native timeout1859 instructions and explicit
   hypothetical completion111 instructions. If ILGLERR and FASTAT!=10 write10; issueB3 then
   poll(FSTATR,8000,8000,E5). Poll0/1 maps0 and timeout2 maps8. Identical masks make poll1
   unreachable here. Native111-instruction explicit completion and1859-instruction timeout; P/E
   transition and physical completion are not synthesized. */

uint f33_faci_force_stop_and_poll(void)

{
  uchar uVar1;
  uint uVar2;
  
  uVar2 = FSTATR;
  if (((uVar2 & 0x4000) == 0x4000) && (uVar1 = FASTAT, uVar1 != '\x10')) {
    FASTAT = '\x10';
  }
  FACI_COMMAND_AREA = 0xb3;
  uVar2 = f33_poll_word_masks((0xffa10080u),0x8000,0x8000,0xe5);
  if (uVar2 < 2) {
    uVar2 = 0;
  }
  else {
    uVar2 = 8;
  }
  return uVar2;
}



bool FUN_00078d80(int param_1)

{
  return param_1 == 0;
}



undefined4 FUN_00078d88(uint param_1,int param_2)

{
  if ((param_1 < 0x8000) && ((param_2 - 1U & param_1) == 0)) {
    return 0;
  }
  return 1;
}



bool FUN_00078d9e(uint param_1,uint param_2,int param_3)

{
  if ((((param_2 != 0) && (param_2 < 0x41)) && ((param_3 - 1U & param_1) == 0)) &&
     ((param_3 - 1U & param_2) == 0)) {
    return 0x7fff < (param_2 + param_1) - 1;
  }
  return true;
}



bool FUN_00078dca(int param_1,int param_2)

{
  if (param_2 != 0) {
    return 0x7fff < (param_2 + param_1) - 1U;
  }
  return true;
}



/* WARNING: Inlined function: f33_load_u32 */
/* Return1 when full FSADDR<8000 and unsigned(FEADDR+3)<=7FFF, else7. No start<=end or span check.
   Real address-register writes discard low two bits; the final-word end input7FFF reads as7FFC.
   Return1 iff full FSADDR<8000 and unsigned(FEADDR+3)<=7FFF; else7. Does not check start<=end or
   span. Native last-word readback, invalid start and reversed-range submission distinguish software
   checks from the sequencer's range requirements. */

uint f33_faci_check_dataflash_addresses(void)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = FSADDR;
  if (uVar2 < 0x8000) {
    uVar2 = 1;
  }
  else {
    uVar2 = 7;
  }
  uVar1 = FEADDR;
  if (0x7fff < uVar1 + 3) {
    uVar2 = 7;
  }
  return uVar2;
}



/* WARNING: Inlined function: f33_store_u8 */
/* WARNING: Inlined function: f33_load_u8 */
/* WARNING: Inlined function: f33_syncp */

undefined1 FUN_00078e10(void)

{
  undefined1 uVar1;
  
  (*((volatile uint8_t *)camry_host_ptr(0xffffb2f7u))) = 0;
  uVar1 = (*((volatile uint8_t *)camry_host_ptr(0xffffb2f7u)));
  __synchronize();
  return uVar1;
}



/* WARNING: Inlined function: f33_store_u8 */
/* WARNING: Inlined function: f33_store_u16 */
/* WARNING: Inlined function: f33_store_u32 */
/* Clear EIC379 request, set FBCCNT=0 only for command71, write FCPSR=0, FSADDR, FEADDR, then
   command byte. Check address readback through78DE2; appendD0 only for result1. Preserve that
   result through the final store helper. Result7 leaves a prefix without D0; this is submission,
   not hardware completion. Clear EIC379 request; command71 alone clears FBCCNT. Set
   FCPSR=0/start/end, write command, check address readback, appendD0 only for result1. Return
   checker result preserved through actual store helper. Result7 leaves a prefix; successful
   submission clears FRDY but does not manufacture completion or blankness. */

uint f33_faci_submit_range_command(uint start_offset,uint end_offset,uchar command)

{
  uint uVar1;
  
  FUN_00078e10();
  if (command == 'q') {
    FBCCNT = '\0';
  }
  FCPSR = 0;
  FSADDR = start_offset;
  FEADDR = end_offset;
  FACI_COMMAND_AREA = command;
  uVar1 = f33_faci_check_dataflash_addresses();
  if (uVar1 == 1) {
    FACI_COMMAND_AREA = 0xd0;
  }
  return uVar1;
}



undefined4 FUN_00078f92(char *param_1)

{
  char cVar1;
  uint uVar2;
  undefined4 uVar3;
  
  if (DAT_febf6c60 < DAT_febf6c68) {
    if (DAT_febf6cac == '\x02') {
      f33_return_only_stub_79d32();
      cVar1 = FUN_00078e2a(((undefined4 *)camry_host_ptr((uint32_t)(DAT_febf6c64))), DAT_febf6c60, 4);
      *param_1 = cVar1;
      f33_return_only_stub_79d34();
      DAT_febf6c60 = DAT_febf6c60 + 4;
      DAT_febf6c64 = DAT_febf6c64 + 4;
    }
    else if (DAT_febf6cac == '\x01') {
      f33_return_only_stub_79d32();
      uVar2 = f33_faci_submit_range_command(DAT_febf6c60,DAT_febf6c60 + 0x3f,' ');
      *param_1 = (char)uVar2;
      f33_return_only_stub_79d34();
      DAT_febf6c60 = DAT_febf6c60 + 0x40;
    }
    else {
      *param_1 = '\a';
    }
    if (*param_1 != '\x01') {
      FUN_00078f7a();
      FUN_00078c70(0);
    }
    uVar3 = 0;
  }
  else {
    uVar3 = 1;
  }
  return uVar3;
}



/* WARNING: Inlined function: f33_load_u32 */

undefined4 FUN_00079026(void)

{
  uint uVar1;
  undefined4 uVar2;
  
  uVar1 = FSTATR;
  if ((uVar1 & 0x24068) == 0) {
    uVar2 = 0;
  }
  else {
    uVar2 = 7;
  }
  return uVar2;
}



bool FUN_00079084(char *param_1)

{
  char cVar1;
  uint uVar2;
  
  uVar2 = f33_faci_decode_completion_status();
  *param_1 = (char)uVar2;
  FUN_00078c30();
  cVar1 = *param_1;
  if (cVar1 != '\0') {
    FUN_00078c70(0);
  }
  return cVar1 == '\0';
}



bool FUN_000790ae(undefined1 *param_1)

{
  int iVar1;
  
  iVar1 = FUN_00079026();
  if (iVar1 != 0) {
    f33_faci_force_stop_and_poll();
    FUN_00078c70(0);
    *param_1 = (char)iVar1;
  }
  return iVar1 == 0;
}



void FUN_000790d6(undefined1 *param_1)

{
  int iVar1;
  undefined1 uStack_9;
  
  uStack_9 = 1;
  iVar1 = FUN_00078bfa();
  if ((iVar1 == 1) && (iVar1 = FUN_000790ae(&uStack_9), iVar1 == 1)) {
    FUN_00079084(&uStack_9);
  }
  *param_1 = uStack_9;
  return;
}



void FUN_0007910a(undefined1 *param_1)

{
  uint uVar1;
  int iVar2;
  undefined1 uStack_9;
  
  uStack_9 = 1;
  uVar1 = f33_poll_word_masks((0xffa10080u),0x8000,0x8000,0x393);
  if (uVar1 < 2) {
    iVar2 = FUN_000790ae(&uStack_9);
    if (iVar2 == 1) {
      FUN_00079084(&uStack_9);
    }
  }
  else {
    uStack_9 = 8;
    f33_faci_force_stop_and_poll();
    FUN_00078c70(0);
  }
  *param_1 = uStack_9;
  FUN_00078af8();
  return;
}



void FUN_00079164(char param_1)

{
  undefined4 uVar1;
  
  if (param_1 == '\0') {
    DAT_febf6cb1 = 0;
    DAT_febf6cb0 = 1;
    DAT_febf6cb3 = 0;
    FUN_00074ec2();
    FUN_00078af8();
  }
  else {
    DAT_febf6cb3 = 0;
    DAT_febf6cb0 = 1;
    DAT_febf6cb1 = 1;
    if (DAT_febf6cac == '\x01') {
      uVar1 = 7;
    }
    else {
      uVar1 = 8;
    }
    FUN_00074ed0();
    FUN_00078af8();
    FUN_0007939c(0x5c,0,6,uVar1);
  }
  return;
}



undefined4 FUN_000791b2(void)

{
  int iVar1;
  char cStack_5;
  
  FUN_0007910a(&cStack_5);
  if (cStack_5 == '\0') {
    iVar1 = FUN_00078c70(0);
    if (iVar1 == 0) {
      return 2;
    }
  }
  else if (cStack_5 == '\x05') {
    return 7;
  }
  return 8;
}



/* WARNING: Inlined function: f33_load_u32 */
/* WARNING: Inlined function: f33_store_u8 */

undefined4 FUN_000791e2(void)

{
  uint uVar1;
  undefined4 uVar2;
  
  uVar1 = FSTATR;
  if ((uVar1 >> 0xf & 1) == 0) {
    if ((uVar1 >> 0xb & 1) == 0) {
      uVar1 = f33_poll_word_masks((0xffa10080u),0x8000,0x800,0x73);
      if (uVar1 == 0) goto LAB_00079210;
      if (uVar1 != 1) {
        return 8;
      }
    }
    FACI_COMMAND_AREA = 0xb0;
    uVar2 = 2;
  }
  else {
LAB_00079210:
    uVar2 = 10;
  }
  return uVar2;
}



undefined4 FUN_0007922c(char param_1)

{
  undefined4 uVar1;
  int iVar2;
  
  if (param_1 == '\x01') {
    iVar2 = FUN_00078bfa();
    if (iVar2 == 1) {
      uVar1 = 10;
    }
    else {
      uVar1 = 2;
    }
  }
  else {
    uVar1 = FUN_000791e2();
  }
  return uVar1;
}



/* WARNING: Inlined function: f33_load_u32 */

uint FUN_00079250(void)

{
  uint uVar1;
  
  uVar1 = FSTATR;
  if ((uVar1 & 0x300) == 0) {
    uVar1 = FUN_00079026();
    if ((uVar1 == 0) && (uVar1 = f33_faci_decode_completion_status(), uVar1 == 0)) {
      uVar1 = 2;
    }
  }
  else {
    uVar1 = 1;
  }
  return uVar1;
}



undefined4 FUN_0007927e(void)

{
  int iVar1;
  undefined4 uVar2;
  
  DAT_febf6cb3 = FUN_00079250();
  iVar1 = FUN_00078c70(0);
  if (iVar1 == 0) {
    uVar2 = 0;
  }
  else {
    uVar2 = 4;
  }
  f33_flash_set_software_enables(0);
  return uVar2;
}



/* WARNING: Inlined function: f33_load_u32 */

bool FUN_000792a6(void)

{
  uint uVar1;
  
  uVar1 = FSTATR;
  return (uVar1 & 0x300) != 0;
}



/* WARNING: Inlined function: f33_store_u8 */

void FUN_000792c0(void)

{
  int iVar1;
  
  iVar1 = FUN_000792a6();
  if (iVar1 == 1) {
    FACI_COMMAND_AREA = 0xd0;
  }
  return;
}



/* WARNING: Inlined function: f33_load_u8 */
/* WARNING: Inlined function: f33_store_u8 */
/* WARNING: Inlined function: f33_syncp */

undefined1 FUN_000792dc(void)

{
  byte bVar1;
  undefined1 uVar2;
  
  bVar1 = (*((volatile uint8_t *)camry_host_ptr(0xffffb2f6u)));
  (*((volatile uint8_t *)camry_host_ptr(0xffffb2f6u))) = bVar1 & 0x7f;
  uVar2 = (*((volatile uint8_t *)camry_host_ptr(0xffffb2f6u)));
  __synchronize();
  return uVar2;
}



/* WARNING: Inlined function: f33_load_u32 */
/* Read FFC5D020 twice through78AE0; return bit0 of the second word. The first result is discarded,
   not the first access. Explicit external transitions between the reads execute both directions. No
   recovered OEM bit name, reset or completion semantics. Read FFC5D020 twice through78AE0 and
   return bit0 of the second word. Native external transitions between the two samples prove the
   first result is discarded; the first access remains. No OEM bit name, reset, busy/ready or
   completion interpretation. */

uint f33_icus20_second_read_bit0(void)

{
  uint uVar1;
  
  uVar1 = ICUSREG20;
  uVar1 = ICUSREG20;
  return uVar1 & 1;
}



void FUN_00079316(void)

{
  uint uVar1;
  int iVar2;
  undefined1 uStack_9;
  
  FUN_00078b90();
  uVar1 = f33_icus20_second_read_bit0();
  if (uVar1 == 0) {
    iVar2 = FUN_00078bfa();
    if (iVar2 == 1) {
      if (DAT_febf6cb2 == '\x0f') {
        iVar2 = FUN_0007927e();
        uStack_9 = (undefined1)iVar2;
        if (iVar2 == 0) {
          DAT_febf6cb2 = '\x10';
        }
      }
      else {
        uStack_9 = 3;
      }
    }
    else {
      uStack_9 = 2;
    }
  }
  else {
    uStack_9 = 1;
  }
  FUN_000793dc(&uStack_9);
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_7936c(void)

{
  return;
}



/* Write EEPRDCYCL=F, DFECCCTL=4000, DFERRINT=0, DFTSTCTL=4000. Manual PROT01 keys are not retained:
   normal ECC enabled, ECC test disabled, notification enables cleared. Eight native instructions
   from nonzero control state; no physical timing or ECM delivery proof. Eight instructions write
   EEPRDCYCL F; DFECCCTL4000; DFERRINT0; DFTSTCTL4000. Manual-keyed control semantics restore normal
   ECC and disable test/notification; key reads zero. No physical timing or ECM-delivery proof. */

void f33_nvm_initialize_dataflash_read_controls(void)

{
  EEPRDCYCL = '\x0f';
  DFECCCTL = 0x4000;
  DFERRINT = 0;
  DFTSTCTL = 0x4000;
  return;
}



void FUN_00079388(void)

{
  f33_nvm_initialize_dataflash_read_controls();
  return;
}



void FUN_0007939c(undefined2 param_1,undefined1 param_2,undefined1 param_3,undefined1 param_4)

{
  FUN_00074efe(param_1,param_2,param_3,param_4);
  return;
}



undefined4 FUN_000793c8(undefined1 *param_1)

{
  undefined1 uVar1;
  
  uVar1 = FUN_000781b4();
  *param_1 = uVar1;
  return 0;
}



void FUN_000793dc(undefined1 *param_1)

{
  FUN_0007813e(*param_1);
  return;
}



/* WARNING: This is an inlined function */
/* SYNCP; JMP LP. Inline the actual ordering operation; no GPR modification or physical
   completion/timing claim. SYNCP followed by JMP LP; no GPR modification. Real inline p-code
   preserves the ordering operation and caller registers. Native FHVE publication executes readback
   then this barrier; no hardware-completion or elapsed-time inference. */

void f33_syncp(void)

{
  __synchronize();
  return;
}



bool FUN_00079420(void)

{
  int iVar1;
  
  iVar1 = FUN_00079d12();
  return iVar1 != 0;
}



bool FUN_00079432(void)

{
  int iVar1;
  
  iVar1 = f33_return_const_0_79d24();
  return iVar1 != 0;
}



undefined4 FUN_00079444(void)

{
  int iVar1;
  undefined4 uVar2;
  
  uVar2 = 1;
  iVar1 = FUN_00079b5c();
  if (iVar1 != 0xc) {
    iVar1 = f33_return_const_0_79d28();
    if (iVar1 == 0) {
      uVar2 = 0;
    }
    else {
      uVar2 = 1;
    }
  }
  return uVar2;
}



void FUN_00079462(undefined2 param_1)

{
  ((void)(param_1), f33_return_only_stub_79d2c());
  return;
}



/* Mask input16, call79D2E and normalize nonzero to1. Exact target hook always returns0, so this is
   not an additional live readiness check. Mask input16, call real79D2E and normalize nonzero to1.
   Exact hook always returns0; repeated native scheduler calls therefore pass this gate and reach
   the separate6102 check. Not an additional live hardware-readiness check. */

uint f33_nvm_driver_gate_rejected(ushort ignored_service)

{
  uint uVar1;
  
  uVar1 = f33_nvm_driver_gate_hook();
  return (uint)(uVar1 != 0);
}



int FUN_0007949c(undefined4 param_1,uint param_2,undefined4 param_3,uint param_4)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  
  iVar1 = FUN_00079c94();
  iVar3 = 8;
  if ((((iVar1 != 0) && (uVar2 = f33_nvm_probe_range_rejected(param_2,param_4), uVar2 == 0)) &&
      (iVar1 = FUN_0007682e(param_2,param_4,param_3), iVar3 = iVar1, iVar1 != 7)) &&
     (iVar3 = 8, iVar1 == 9)) {
    iVar3 = iVar1;
  }
  return iVar3;
}



/* Require nonzero direct-operation classification. Compute low16((byte_count+63 mod2^32)>>6),
   check79608, then guarded76872 admission. Preserve7 and9, normalize other outcomes to8. R6 is
   unused. Bounds use wrapped page arithmetic, not a generic nonzero-length test. */

uint f33_nvm_request_erase_span(uint unused_selector,uint byte_offset,uint byte_count)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  uint page_count;
  
  iVar1 = FUN_00079c94();
  uVar3 = 8;
  if (iVar1 != 0) {
    page_count = byte_count + 0x3f >> 6 & 0xffff;
    uVar2 = f33_nvm_erase_span_outside_region(byte_offset,page_count);
    if (((uVar2 == 0) &&
        (uVar2 = f33_nvm_guarded_erase_admission(byte_offset,page_count), uVar3 = uVar2, uVar2 != 7)
        ) && (uVar3 = 8, uVar2 == 9)) {
      uVar3 = uVar2;
    }
  }
  return uVar3;
}



/* Dispatch guarded lower polling only when direct-operation classification6CDC is nonzero. Does not
   itself normalize result or release application ownership. */

void f33_nvm_poll_direct_operation(void)

{
  int iVar1;
  
  iVar1 = FUN_00079c94();
  if (iVar1 != 0) {
    f33_nvm_guarded_direct_poll();
  }
  return;
}



int FUN_00079554(undefined4 param_1,uint param_2,undefined4 param_3,uint param_4)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  int iVar4;
  
  iVar4 = 4;
  iVar1 = FUN_00079c94();
  iVar3 = iVar4;
  if ((((iVar1 != 0) && (uVar2 = f33_nvm_probe_range_rejected(param_2,param_4), uVar2 == 0)) &&
      (iVar3 = FUN_000768e8(param_2, param_4, ((uchar *)camry_host_ptr((uint32_t)(param_3)))), iVar3 != 0)) && ((iVar3 != 6 && (iVar3 != 9)))
     ) {
    iVar3 = iVar4;
  }
  return iVar3;
}



/* First ABI input unused. Return4 if6CDC==0 or795D4 rejects. Otherwise call76930 and preserve
   only2/3/6/9; map other results to4. This performs synchronous classification, not a queue
   submission. Unused first ABI input;6CDC zero or range rejection returns4. Otherwise actual76930;
   preserve2/3/6/9 else4. Noncanonical nonzero mode1 accepted. This is synchronous classification
   not enqueueing. */

uint f33_nvm_classify_storage_range(uint ignored_selector,uint byte_offset,uint byte_count)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  
  uVar4 = 4;
  iVar1 = FUN_00079c94();
  uVar3 = uVar4;
  if ((((iVar1 != 0) && (uVar2 = f33_nvm_probe_range_rejected(byte_offset,byte_count), uVar2 == 0))
      && (uVar3 = f33_nvm_probe_storage_range(byte_offset,(ushort)byte_count), uVar3 != 2)) &&
     (((uVar3 != 3 && (uVar3 != 6)) && (uVar3 != 9)))) {
    uVar3 = uVar4;
  }
  return uVar3;
}



/* Return1 unless registered first_page!=FFFF, low16(byte_offset>>6)>=first_page, and
   low16(page+page_count-1)<=low16(first_page+region_count-1). Exact region0/480 pages. No alignment
   or independent nonzero-count check; wrapped arithmetic is intentional reconstruction, not
   strengthened validation. */

uint f33_nvm_erase_span_outside_region(uint byte_offset,uint page_count)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = 1;
  if (f33_nvm_region_first_page != 0xffff) {
    uVar1 = byte_offset >> 6 & 0xffff;
    if (f33_nvm_region_first_page <= uVar1) {
      uVar2 = (uint)((((uint)f33_nvm_region_page_count + (uint)f33_nvm_region_first_page) - 1 &
                     0xffff) < ((page_count + uVar1) - 1 & 0xffff));
    }
  }
  return uVar2;
}



void FUN_00079638(void)

{
  f33_nvm_service_diagnostic_mask = 0;
  DAT_febf6cbc = 0xffff;
  f33_nvm_service_cd_diagnostic_mask = 0;
  DAT_febf6cc4 = 0xffff;
  DAT_febf6cb4 = 0;
  DAT_febf6cb8 = 0;
  f33_nvm_diagnostic_service = 0xff;
  return;
}



void FUN_00079662(uint param_1)

{
  param_1 = param_1 & 0xff;
  if (2 < param_1 - 6) {
    if (param_1 == 0xc || param_1 == 0xd) goto LAB_00079686;
    if (2 < param_1 - 0x16) {
      param_1 = 0xffffffff;
    }
  }
  f33_nvm_diagnostic_service = (uchar)param_1;
LAB_00079686:
  DAT_febf6cbc = FUN_00079b66();
  f33_nvm_service_diagnostic_mask = 0;
  return;
}



void FUN_0007969a(uchar param_1)

{
  f33_nvm_service_cd_diagnostic_mask = 0;
  DAT_febf6cc4 = 0;
  if (param_1 != '\f' && param_1 != '\r') {
    param_1 = 0xff;
  }
  f33_nvm_diagnostic_service = param_1;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_796ba(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_796bc(void)

{
  return;
}



void FUN_000796be(uint param_1)

{
  uint uVar1;
  
  uVar1 = DAT_febf6cb4;
  if ((param_1 & 0xff) < 3) {
    DAT_febf6cb4 = *(uint *)(((undefined *)camry_host_ptr(0x27cccu)) + (param_1 & 0xff) * 8) | DAT_febf6cb4;
    FUN_000797f6();
    if (uVar1 != DAT_febf6cb4) {
      ((void)(((undefined *)camry_host_ptr(0xfebf6cb4u))), f33_return_only_stub_79d36());
    }
  }
  return;
}



void FUN_000796f4(uint param_1)

{
  if ((param_1 & 0xff) < 3) {
    DAT_febf6cb4 = DAT_febf6cb4 & ~*(uint *)(((undefined *)camry_host_ptr(0x27cccu)) + (param_1 & 0xff) * 8);
    FUN_000797f6();
  }
  return;
}



void FUN_000797f6(void)

{
  uint uVar1;
  uint uVar2;
  
  DAT_febf6cb8 = 0;
  uVar1 = 0;
  uVar2 = 0;
  do {
    if ((*(uint *)(((undefined *)camry_host_ptr(0x27cccu)) + uVar2 * 8) & DAT_febf6cb4) != 0) {
      uVar1 = uVar1 | *(uint *)(((undefined *)camry_host_ptr(0x27cd0u)) + uVar2 * 8);
      DAT_febf6cb8 = uVar1;
    }
    uVar2 = uVar2 + 1;
  } while (uVar2 < 3);
  return;
}



bool FUN_00079848(uchar param_1,int param_2)

{
  if (param_2 != 0) {
    return param_1 != f33_nvm_diagnostic_service;
  }
  return true;
}



void FUN_00079862(void)

{
  DAT_febf6cd2 = 0;
  DAT_febf6cd4 = 0xff;
  DAT_febf6cd3 = 0xff;
  return;
}



void FUN_0007987e(undefined1 param_1)

{
  DAT_febf6cd0 = param_1;
  DAT_febf6cd1 = param_1;
  return;
}



void FUN_0007988a(void)

{
  if (DAT_febf6cd0 == '\x01') {
    FUN_0007987e(2);
    FUN_00079d38(0);
  }
  return;
}



void FUN_000798aa(void)

{
  if (DAT_febf6cd0 == '\x01') {
    FUN_0007987e(0);
    FUN_00079d38(2);
  }
  return;
}



void FUN_000798ca(char param_1)

{
  if (param_1 == '\0') {
    FUN_0007988a();
  }
  else if (param_1 != '\x05') {
    FUN_000798aa();
  }
  return;
}



void FUN_000798e6(void)

{
  DAT_febf6cd2 = 1;
  if (DAT_febf6cd3 == '\x01') {
    FUN_000798ca(DAT_febf6cd4);
  }
  DAT_febf6cd3 = 0xff;
  DAT_febf6cd4 = 0xff;
  return;
}



void FUN_000799b0(void)

{
  if (DAT_febf6cd0 == '\x02') {
    FUN_0007814c();
  }
  FUN_0007987e(0);
  return;
}



/* Far-call trampoline: prepare {lp},0 / jarl 0x799B0 / dispose 0,{lp},lp; byte-verified against the
   exact image. Forwards with registers and stack unchanged; marked as a thunk. Forwarding shape
   machine-verified; target semantics not recovered. */

void thunk_FUN_000799b0(void)

{
  FUN_000799b0();
  return;
}



void FUN_000799da(void)

{
  if (DAT_febf6cd0 == '\x01') {
    FUN_00078176();
  }
  else if (DAT_febf6cd0 == '\x02') {
    FUN_0007814c();
  }
  FUN_0007987e(0);
  return;
}



/* Far-call trampoline: prepare {lp},0 / jarl 0x799DA / dispose 0,{lp},lp; byte-verified against the
   exact image. Forwards with registers and stack unchanged; marked as a thunk. Forwarding shape
   machine-verified; target semantics not recovered. */

void thunk_FUN_000799da(void)

{
  FUN_000799da();
  return;
}



undefined1 FUN_00079ad4(void)

{
  if (DAT_febf6cd0 != DAT_febf6cd1) {
    return 1;
  }
  return 0;
}



undefined1 FUN_00079af0(void)

{
  int iVar1;
  
  iVar1 = FUN_00079ad4();
  if (iVar1 != 0) {
    FUN_0007987e(0);
  }
  return DAT_febf6cd0;
}



bool FUN_00079b0e(void)

{
  return DAT_febf6cd0 != '\0';
}



void FUN_00079b1e(void)

{
  DAT_febf6cdb = 0;
  f33_nvm_service_mode_nonzero = '\0';
  DAT_febf6cd9 = 0;
  DAT_febf6cd6 = 0xffff;
  DAT_febf6cd8 = 0xff;
  FUN_00079c6c();
  FUN_00079638();
  FUN_00079a0e();
  return;
}



undefined1 FUN_00079b5c(void)

{
  return DAT_febf6cd8;
}



undefined2 FUN_00079b66(void)

{
  return DAT_febf6cd6;
}



void FUN_00079bc0(undefined2 param_1,char param_2)

{
  if ((param_2 != '\f') && (param_2 != '\r')) {
    DAT_febf6cd8 = param_2;
  }
  DAT_febf6cd6 = param_1;
  FUN_00079662(param_2);
  return;
}



void FUN_00079bfe(undefined4 param_1,char param_2)

{
  if ((param_2 != '\f') && (param_2 != '\r')) {
    DAT_febf6cd8 = 0xff;
  }
  DAT_febf6cd6 = 0xffff;
  ((void)(param_2), f33_return_only_stub_796ba());
  return;
}



void FUN_00079c2a(undefined1 param_1)

{
  DAT_febf6cd8 = 0xff;
  ((void)(param_1), f33_return_only_stub_796bc());
  return;
}



void FUN_00079c42(undefined1 param_1)

{
  DAT_febf6cd9 = param_1;
  return;
}



/* Only store low8 to6CDA. This is NOT a driver pump. Exact byte store of low8 input to6CDA.
   Initialized74164 publishes0 after scheduling,1 after real0693=5A mode recomputation suppresses
   scheduling. Not a driver pump or a separate permission gate. */

void f33_nvm_store_service_mode_nonzero(uchar value)

{
  f33_nvm_service_mode_nonzero = value;
  return;
}



void FUN_00079c56(undefined1 param_1)

{
  DAT_febf6cdb = param_1;
  return;
}



/* Real wrapper of74164, not a replacement readiness callback. Native polling/budget cases exercise
   its service-state rejection; 74164 also has initialized scheduler/terminal-state proofs, not a
   whole physical-acquisition proof. Real wrapper invokes74164 and returns. Native repeated calls
   exercise actual uninitialized-service rejection, not a replaced readiness callback.
   Initialized74164 body now has separate scheduler/terminal-state proofs, not whole physical
   acquisition. */

void f33_nvm_service_acquisition_driver(void)

{
  f33_nvm_service_logical_and_physical_driver();
  return;
}



void FUN_00079c6c(void)

{
  f33_nvm_direct_operation_mode = '\0';
  return;
}



uchar FUN_00079c76(void)

{
  uchar uVar1;
  int iVar2;
  
  iVar2 = FUN_00079af0();
  uVar1 = 'U';
  if (iVar2 == 0) {
    uVar1 = f33_nvm_direct_operation_mode;
  }
  return uVar1;
}



uchar FUN_00079c94(void)

{
  return f33_nvm_direct_operation_mode;
}



/* Sample79AF0 (including its redundant-state check), then refresh79CE2. If sampled6CD0!=0 return55
   even when stored6CDC becomes0; otherwise return the refreshed mode. Native exact5A/non5A and
   interference-with-cancellation cases. Sample79AF0 then refresh79CE2; nonzero sampled6CD0
   overrides return to55 even when stored6CDC is now0. Native return/state divergence and
   cancellation side effects; matched interference bytes avoid conflating the independent
   mismatch-repair path. */

uint f33_nvm_reconcile_probe_mode(void)

{
  int iVar1;
  uint uVar2;
  
  iVar1 = FUN_00079af0();
  uVar2 = f33_nvm_refresh_direct_probe_mode();
  if (iVar1 != 0) {
    uVar2 = 0x55;
  }
  return uVar2;
}



/* Preserve79C9E's return through the real call. 68A6C invokes this at68AA0 and68B24, around the
   whole classifier, not around each of its three page probes. Real call preserves79C9E result.
   Classifier calls at68AA0/68B24 bracket the entire probe sequence. Composed native scenarios
   include mode-entry and actual mode-exit cancellation; not a side-effect-free poll. */

uint f33_nvm_poll_probe_mode(void)

{
  uint uVar1;
  
  uVar1 = f33_nvm_reconcile_probe_mode();
  return uVar1;
}



bool FUN_00079cc4(void)

{
  bool bVar1;
  
  bVar1 = f33_nvm_direct_operation_mode == '\0';
  if (!bVar1) {
    FUN_000741de();
  }
  return bVar1;
}



/* Request0693 exactly5A stores/returns55. Otherwise, if old6CDC!=0, call741D0->72248->73C4A->7664E
   before storing/returning0. This exit can perform real cancellation/B3; it is not a pure flag
   refresh. Otherwise old6CDC!=0 invokes741D0 cancellation before storing/returning0. Native non5A
   request remains disabled and real shutdown mutates physical/active logical states. */

uint f33_nvm_refresh_direct_probe_mode(void)

{
  int iVar1;
  uint uVar2;
  
  iVar1 = ((void)(0), FUN_00079d46());
  if (iVar1 == 0) {
    if (f33_nvm_direct_operation_mode != '\0') {
      FUN_000741d0();
    }
    uVar2 = 0;
  }
  else {
    uVar2 = 0x55;
  }
  f33_nvm_direct_operation_mode = (uchar)uVar2;
  return uVar2;
}



bool FUN_00079d12(void)

{
  int iVar1;
  
  iVar1 = FUN_0006a192();
  return iVar1 != 0;
}



/* Constant source: return 0; shape-classified from the canonical corpus. Callers receive this
   literal directly; its meaning is not recovered. */

undefined4 f33_return_const_0_79d24(void)

{
  return 0;
}



/* Constant source: return 0; shape-classified from the canonical corpus. Callers receive this
   literal directly; its meaning is not recovered. */

undefined4 f33_return_const_0_79d28(void)

{
  return 0;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_79d2c(void)

{
  return;
}



/* Exact MOV0,r10;JMPLP. No argument reads or hardware access. Exact four-byte MOV0,r10;JMPLP,
   executed by real scheduler gate. No argument reads, hardware access or changing readiness state.
    */

uint f33_nvm_driver_gate_hook(void)

{
  return 0;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_79d32(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_79d34(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_79d36(void)

{
  return;
}



void FUN_00079d38(undefined1 param_1)

{
  FUN_00087ef6(param_1);
  return;
}



bool FUN_00079d46(void)

{
  int iVar1;
  
  iVar1 = FUN_00068f64();
  return iVar1 == 0x5a;
}



void FUN_00079d60(void)

{
  ((void)(0), FUN_0007a30e());
  return;
}



void FUN_00079d7a(void)

{
  f33_cantp_foreground_cycle();
  return;
}



void FUN_00079d86(undefined1 param_1)

{
  ((void)(param_1), f33_return_only_stub_7b204());
  return;
}



void FUN_00079d94(undefined1 param_1)

{
  ((void)(param_1), f33_return_only_stub_7b206());
  return;
}



void FUN_00079da2(ushort param_1)

{
  f33_cantp_confirm_can_frame(param_1);
  return;
}



void FUN_00079db0(ushort param_1,F33PduInfo *param_2)

{
  f33_cantp_receive_can_frame(param_1,param_2);
  return;
}



/* Forward to7A376; only descriptor16-bit length is consumed by CanTp admission. Payload remains at
   upper owner. */

uint f33_pdur_cantp_transmit_adapter(ushort transmit_id,F33PduInfo *response)

{
  uint uVar1;
  
  uVar1 = f33_cantp_transmit_descriptor(transmit_id,response);
  return uVar1;
}



void FUN_00079dcc(undefined2 param_1)

{
  FUN_0007a38c(param_1);
  return;
}



void FUN_00079dda(undefined2 param_1,undefined1 param_2,undefined2 param_3)

{
  FUN_00081fa6(param_1,param_2,param_3);
  return;
}



void FUN_00079dec(undefined2 param_1)

{
  FUN_0007a3ca(param_1);
  return;
}



/* Sequential initializer chain: 8 unconditional calls and no other statements; shape-verified. The
   called sequence is the function's entire behavior; chain family members differ in callee sets. */

void f33_run_init_chain_79dfa(void)

{
  FUN_0007c2ee();
  ((void)(0), f33_return_only_stub_81588());
  ((void)(0), FUN_00083f3e());
  ((void)(0), FUN_0007f75a());
  FUN_0007c478();
  FUN_0007f250(0);
  ((void)(0), FUN_0007c710());
  FUN_00079d60();
  return;
}



void FUN_00079e2c(void)

{
  byte bVar1;
  uint32_t puVar2;
  byte logical_controller;
  
  puVar2 = 0x23dfcu;
  FUN_0007c4a2();
  bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x25c0)))));
  for (logical_controller = 0; logical_controller < bVar1;
      logical_controller = logical_controller + 1) {
    f33_request_logical_controller_run_stop(logical_controller,'\x03');
  }
  FUN_0007fac6();
  FUN_0007f27c();
  FUN_0007c748();
  thunk_FUN_0007b3a6();
  return;
}



/* Sequential initializer chain: 7 unconditional calls and no other statements; shape-verified. The
   called sequence is the function's entire behavior; chain family members differ in callee sets. */

void f33_run_init_chain_79e60(void)

{
  FUN_0007c4a2();
  FUN_00084160();
  f33_return_only_stub_8158e();
  FUN_0007fac6();
  FUN_0007f27c();
  FUN_0007c748();
  thunk_FUN_0007b3a6();
  return;
}



/* Sequential initializer chain: 9 unconditional calls and no other statements; shape-verified. The
   called sequence is the function's entire behavior; chain family members differ in callee sets. */

void f33_run_init_chain_79e84(void)

{
  FUN_0007c4c6();
  ((void)(0), f33_return_only_stub_81588());
  ((void)(0), FUN_00083f3e());
  ((void)(0), FUN_0007f75a());
  FUN_0007c478();
  FUN_0007f250(0);
  ((void)(0), FUN_0007c710());
  FUN_00079d60();
  FUN_0007c50a();
  return;
}



void FUN_00079eba(void)

{
  FUN_000851b8();
  FUN_00083ce4();
  return;
}



void FUN_00079eca(void)

{
  f33_return_only_stub_7f364();
  f33_return_only_stub_7c60c();
  FUN_000802ee();
  return;
}



void FUN_00079ede(void)

{
  char cVar1;
  byte bVar2;
  uint32_t puVar3;
  int iVar4;
  byte bVar5;
  
  puVar3 = 0x23dfcu;
  f33_return_only_stub_7c60a();
  FUN_000809fe();
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x25bf)))));
  bVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x25c0)))));
  for (bVar5 = 0; bVar5 < bVar2; bVar5 = bVar5 + 1) {
    iVar4 = FUN_0007f6a4(bVar5);
    if (iVar4 == 1) {
      FUN_0007ed4e(cVar1 + bVar5);
    }
  }
  return;
}



/* Sequential initializer chain: 6 unconditional calls and no other statements; shape-verified. The
   called sequence is the function's entire behavior; chain family members differ in callee sets. */

void f33_run_init_chain_79f16(void)

{
  f33_driver_poll_pending_channel_modes();
  FUN_000835d4();
  FUN_00083724();
  FUN_00080c88();
  FUN_0007c93e();
  FUN_0007f33c();
  return;
}



/* Far-call trampoline: prepare {lp},0 / jarl 0x79D7A / dispose 0,{lp},lp; byte-verified against the
   exact image. Forwards with registers and stack unchanged; marked as a thunk. Forwarding shape
   machine-verified; target semantics not recovered. */

void thunk_FUN_00079d7a(void)

{
  FUN_00079d7a();
  return;
}



void FUN_00079f42(void)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = (uint)DAT_00021865;
  for (uVar1 = 0; uVar1 < uVar2; uVar1 = uVar1 + 1 & 0xff) {
    f33_upper_network_software_indication[uVar1] = '\0';
  }
  return;
}



void FUN_00079f9a(uint param_1)

{
  if ((param_1 & 0xff) < (uint)DAT_00021865) {
    f33_upper_network_software_indication[param_1 & 0xff] = '\x01';
    f33_return_only_stub_7be4c();
  }
  return;
}



void FUN_00079fba(uint param_1)

{
  if ((param_1 & 0xff) < (uint)DAT_00021865) {
    f33_upper_network_software_indication[param_1 & 0xff] = '\x03';
    f33_return_only_stub_7be4a();
  }
  return;
}



void FUN_00079fda(uint param_1)

{
  param_1 = param_1 & 0xff;
  if (param_1 < DAT_00021865) {
    f33_upper_network_software_indication[param_1] = '\0';
    FUN_00082eb0(param_1);
    ((void)(param_1), f33_return_only_stub_7be48());
  }
  return;
}



void FUN_0007a002(uint param_1)

{
  param_1 = param_1 & 0xff;
  if (param_1 < DAT_00021865) {
    f33_upper_network_software_indication[param_1] = '\x01';
    FUN_00082e94(param_1);
    ((void)(param_1), f33_return_only_stub_7be46());
  }
  return;
}



void FUN_0007a02c(byte param_1)

{
  if (param_1 < DAT_00021865) {
    FUN_0007e29c(param_1,0xc0);
    FUN_00082ef0(param_1);
  }
  return;
}



void FUN_0007a050(byte param_1)

{
  if (param_1 < DAT_00021865) {
    FUN_0007e29c(param_1,0xc0);
    FUN_00082ef0(param_1);
  }
  return;
}



void FUN_0007a074(byte param_1,uint param_2)

{
  uint uVar1;
  
  if (param_1 < DAT_00021865) {
    if ((param_2 >> 1 & 1) == 0) {
      uVar1 = 0;
    }
    else {
      uVar1 = 2;
    }
    if ((param_2 & 1) != 0) {
      uVar1 = uVar1 | 1;
    }
    FUN_0007e3e0(param_1,uVar1);
  }
  return;
}



void FUN_0007a09c(byte param_1,undefined2 param_2)

{
  if (param_1 < DAT_00021865) {
    FUN_0007e412(param_1,param_2);
  }
  return;
}



void FUN_0007a0ba(byte param_1,char param_2)

{
  if (param_1 < DAT_00021865) {
    FUN_00082f18(param_1,param_2 == -1);
  }
  return;
}



void FUN_0007a0dc(void)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = (uint)DAT_00021864;
  for (uVar1 = 0; uVar1 < uVar2; uVar1 = uVar1 + 1 & 0xff) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe3deau + (uint32_t)(uVar1) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe3decu + (uint32_t)(uVar1) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe3deeu + (uint32_t)(uVar1) * 1u)))) = 0;
  }
  return;
}



void FUN_0007a0fe(void)

{
  undefined8 uVar1;
  uint uVar2;
  uint uVar3;
  
  uVar1 = 0x23dfc00000000;
  uVar2 = (uint)DAT_00021865;
  for (uVar3 = 0; uVar3 < uVar2; uVar3 = uVar3 + 1 & 0xff) {
    if ((*((char *)camry_host_ptr((uint32_t)(uVar3 + (int)((ulonglong)uVar1 >> 0x20) + -0x2594)))) != '\0') {
      FUN_0007e412(uVar3,0);
      FUN_0007e3e0(uVar3,3);
    }
  }
  return;
}



void FUN_0007a132(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe3df2 = 0xfd02;
  FUN_0007a0dc();
  FUN_00079f42();
  FUN_0007bb9c();
  f33_run_init_chain_79dfa();
  ((void)(0), FUN_0007e782());
  f33_return_only_stub_7be36();
  f33_return_only_stub_7ee7e();
  ((void)(0), FUN_0007d880());
  FUN_0007a0fe();
  ((void)(0), FUN_00082c9e());
  ((void)(0), f33_return_only_stub_81590());
  f33_return_only_stub_7be34();
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x7a0c))))) = 0xf;
  FUN_0007c43c();
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x7a0e)))) = 0xfe01;
  return;
}



void FUN_0007a18c(void)

{
  DAT_febe3df2 = 0xfd02;
  FUN_00079e2c();
  FUN_0007e7da();
  FUN_0007d88e();
  f33_return_only_stub_7ee80();
  FUN_00082d38();
  f33_return_only_stub_81592();
  return;
}



void FUN_0007a1b4(void)

{
  DAT_febe3df2 = 0xfd02;
  f33_run_init_chain_79e60();
  FUN_0007e7da();
  FUN_0007d88e();
  f33_return_only_stub_7ee80();
  FUN_00082d38();
  f33_return_only_stub_81592();
  return;
}



void FUN_0007a1dc(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe3df2 = 0xfd02;
  FUN_0007a0dc();
  FUN_00079f42();
  FUN_0007bb9c();
  f33_run_init_chain_79e84();
  ((void)(0), FUN_0007e782());
  f33_return_only_stub_7be36();
  f33_return_only_stub_7ee7e();
  ((void)(0), FUN_0007d89e());
  FUN_0007a0fe();
  ((void)(0), FUN_00082c9e());
  ((void)(0), f33_return_only_stub_81590());
  f33_return_only_stub_7be34();
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x7a0c))))) = 0xf;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x7a0e)))) = 0xfe01;
  return;
}



undefined4 FUN_0007a2da(void)

{
  thunk_FUN_0006a45e();
  return 0;
}



undefined4 FUN_0007a2f4(void)

{
  thunk_FUN_0006a45e();
  return 0;
}



void FUN_0007a30e(void)

{
  uint32_t puVar1;
  puVar1 = 0x23dfcu;
  FUN_0007b3a6();
  FUN_0007b2c4(((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x118c))));
  return;
}



/* Far-call trampoline: prepare {lp},0 / jarl 0x7B3A6 / dispose 0,{lp},lp; byte-verified against the
   exact image. Forwards with registers and stack unchanged; marked as a thunk. Forwarding shape
   machine-verified; target semantics not recovered. */

void thunk_FUN_0007b3a6(void)

{
  FUN_0007b3a6();
  return;
}



F33CanTpConfiguration * FUN_0007a32e(void)

{
  return ((undefined *)camry_host_ptr(0x22c70u));
}



/* Decrement bounded16-bit channel timers, advance receive FC/timeout work, then acquire and queue
   transmit segments. This software cycle does not poll RSCFD or supply lower frame confirmation. */

void f33_cantp_foreground_cycle(void)

{
  f33_cantp_tick_channel_timeouts();
  f33_cantp_run_receive_channels();
  f33_cantp_run_transmit_channels();
  return;
}



void FUN_0007a79e(undefined2 param_1,undefined1 param_2)

{
  FUN_00081a00(param_1,param_2);
  return;
}



/* Accumulate capacity shifted by each set bit of block_size, truncating the sum to16 bits. This
   computes configured CF payload capacity times BS; it is not an empty delay loop. */

uint f33_cantp_multiply_receive_block_capacity(uchar cf_payload_capacity,uchar block_size)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = 0;
  uVar1 = 0;
  do {
    if ((1 << (uVar1 & 0x1f) & 0xffU & (uint)block_size) != 0) {
      uVar2 = uVar2 + ((uint)cf_payload_capacity << (uVar1 & 0x1f)) & 0xffff;
    }
    uVar1 = uVar1 + 1;
  } while (uVar1 < 8);
  return uVar2;
}



/* Return F0 CTS when upper capacity covers remaining bytes, or min(remaining,CFcapacity*BS) for
   nonzero BS. Otherwise return E1 WAIT. No physical timing unit is implied. */

uint f33_cantp_select_receive_flow_status
               (uint remaining,uint available,uchar cf_payload_capacity,uchar block_size)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = 0xe1;
  uVar1 = remaining;
  if ((block_size != '\0') &&
     (uVar1 = f33_cantp_multiply_receive_block_capacity(cf_payload_capacity,block_size),
     remaining <= uVar1)) {
    uVar1 = remaining;
  }
  if (uVar1 <= available) {
    uVar2 = 0xf0;
  }
  return uVar2;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_7b204(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_7b206(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_7b208(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_7b246(void)

{
  return;
}



/* For all configured channels, decrement nonzero Rx/Tx16-bit countdowns. Values above exact sanity
   limit1000 latch error0F and become0, not a wrapping long timeout. */

void f33_cantp_tick_channel_timeouts(void)

{
  byte bVar1;
  ushort uVar2;
  ushort uVar3;
  uint32_t puVar4;
  uint32_t puVar5;
  int iVar6;
  uint uVar7;
  ushort uVar8;
  
  puVar4 = 0xfebeb800u;
  puVar5 = 0x23dfcu;
  if (((int8_t)DAT_febe4f3d) == -0x56) {
    iVar6 = camry_host_addr(FUN_0007a32e());
    if (iVar6 != 0) {
      bVar1 = (*((byte *)camry_host_ptr((uint32_t)(iVar6 + 0xc))));
      uVar2 = (*((ushort *)camry_host_ptr((uint32_t)(puVar5 + -0x11b8))));
      for (uVar7 = 0; uVar7 < bVar1; uVar7 = uVar7 + 1 & 0xff) {
        iVar6 = uVar7 * 0x20;
        uVar3 = (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + iVar6 + -0x68aa))));
        uVar8 = (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + iVar6 + -0x68ba))));
        if (uVar2 < uVar3) {
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x68c4))))) = 0xf;
          uVar3 = 0;
        }
        else if (uVar3 != 0) {
          uVar3 = uVar3 - 1;
        }
        if (uVar2 < uVar8) {
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x68c4))))) = 0xf;
          uVar8 = 0;
        }
        else if (uVar8 != 0) {
          uVar8 = uVar8 - 1;
        }
        (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + iVar6 + -0x68aa)))) = uVar3;
        (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + iVar6 + -0x68ba)))) = uVar8;
      }
    }
  }
  else if (DAT_febe4f3d != 'U') {
    DAT_febe4f3c = 0xf;
  }
  return;
}



/* Paired constant publisher: DAT_febe4f3c = 0xf0; and DAT_febe4f3d = 0x55;; shape-classified from
   the canonical corpus. Target cells not yet named. */

void FUN_0007b3a6(void)

{
  DAT_febe4f3c = 0xf0;
  DAT_febe4f3d = 0x55;
  return;
}



undefined4 FUN_0007b3b6(int param_1,int param_2)

{
  undefined4 uVar1;
  
  uVar1 = 0x10;
  if ((uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22b98u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xc))))) * 1u)))) + param_2 + 1 < 9) {
    uVar1 = 0;
  }
  return uVar1;
}



void FUN_0007b46e(undefined2 param_1,undefined1 param_2)

{
  FUN_00081a4c(param_1,param_2);
  return;
}



/* WARNING: Inlined function: f33_cantp_reset_transmit_owner */

void FUN_0007b572(int param_1,undefined4 *param_2,char param_3)

{
  if (*(char *)(param_2 + 2) == param_3) {
    *(undefined2 *)(param_2 + 1) = 0xffff;
    *param_2 = 0;
    *(undefined1 *)(param_2 + 2) = 0xe1;
    (*((undefined2 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 6)))) = 0;
    (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 9)))) = 0xff;
    (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 10)))) = 0;
    (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 0xb)))) = 0;
    *(undefined1 *)(param_2 + 3) = 0;
    FUN_0007b46e((*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 8)))),1);
  }
  return;
}



/* WARNING: Inlined function: f33_cantp_reset_transmit_owner */

void FUN_0007b6f2(int param_1,undefined4 *param_2)

{
  char cVar1;
  
  cVar1 = *(char *)(param_2 + 2);
  if (((cVar1 == -0x3d) || (cVar1 == -0x4c)) || (cVar1 == -0x79)) {
    *(undefined2 *)(param_2 + 1) = 0xffff;
    *param_2 = 0;
    *(undefined1 *)(param_2 + 2) = 0xe1;
    (*((undefined2 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 6)))) = 0;
    (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 9)))) = 0xff;
    (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 10)))) = 0;
    (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 0xb)))) = 0;
    *(undefined1 *)(param_2 + 3) = 0;
    ((void)((*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 10))))), f33_return_only_stub_7b246());
    FUN_0007b46e((*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 8)))),1);
  }
  return;
}



/* WARNING: Inlined function: f33_cantp_reset_transmit_owner */

void FUN_0007b72a(int param_1,undefined4 *param_2)

{
  if (*(char *)(param_2 + 2) == -0x5b) {
    *(undefined2 *)(param_2 + 1) = 0xffff;
    *param_2 = 0;
    *(undefined1 *)(param_2 + 2) = 0xe1;
    (*((undefined2 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 6)))) = 0;
    (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 9)))) = 0xff;
    (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 10)))) = 0;
    (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 0xb)))) = 0;
    *(undefined1 *)(param_2 + 3) = 0;
    FUN_0007b46e((*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 8)))),1);
  }
  return;
}



/* WARNING: Inlined function: f33_cantp_reset_transmit_owner */

void FUN_0007b848(int param_1,undefined4 *param_2)

{
  if (*(char *)(param_2 + 2) == -0x6a) {
    *(undefined2 *)(param_2 + 1) = 0xffff;
    *param_2 = 0;
    *(undefined1 *)(param_2 + 2) = 0xe1;
    (*((undefined2 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 6)))) = 0;
    (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 9)))) = 0xff;
    (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 10)))) = 0;
    (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 0xb)))) = 0;
    *(undefined1 *)(param_2 + 3) = 0;
    FUN_0007b46e((*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 8)))),1);
  }
  return;
}



void FUN_0007bb9c(void)

{
  uint32_t puVar1;
  byte bVar2;
  
  puVar1 = 0xfebeb800u;
  bVar2 = FUN_0007be2e(DAT_00021866);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6853))))) = 0xff;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6854))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6852))))) = bVar2;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6851))))) = bVar2 ^ 0xff;
  return;
}



void FUN_0007bbc2(void)

{
  byte bVar1;
  undefined1 uVar2;
  uint32_t puVar3;
  undefined4 uVar4;
  uint uVar5;
  
  puVar3 = 0xfebeb800u;
  uVar5 = (uint)DAT_febe4fac;
  uVar4 = FUN_0007a2da();
  bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6852)))));
  uVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6851)))));
  ((void)(uVar4), thunk_FUN_0006a4c4());
  if (uVar5 != bVar1) {
    uVar4 = FUN_0007a2da();
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6854))))) = bVar1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6853))))) = uVar2;
    ((void)(uVar4), thunk_FUN_0006a4c4());
    uVar5 = 0;
    do {
      if ((1 << (uVar5 & 0x1f) & 0xffU & (uint)bVar1) == 0) {
        uVar4 = 0;
      }
      else {
        uVar4 = 2;
      }
      FUN_0007ea26(uVar5,uVar4);
      uVar5 = uVar5 + 1;
    } while (uVar5 < 8);
  }
  return;
}



void FUN_0007bc12(byte param_1,byte param_2)

{
  uint32_t puVar1;
  undefined4 uVar2;
  byte bVar3;
  
  puVar1 = 0xfebeb800u;
  uVar2 = FUN_0007a2da();
  bVar3 = (param_1 ^ 0xff) & (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6852))))) | param_1 & param_2;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6852))))) = bVar3;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6851))))) = bVar3 ^ 0xff;
  ((void)(uVar2), thunk_FUN_0006a4c4());
  return;
}



byte FUN_0007bc42(void)

{
  byte bVar1;
  
  bVar1 = DAT_febe4fac;
  if ((DAT_febe4fad ^ DAT_febe4fac) != 0xff) {
    bVar1 = 0;
  }
  return bVar1;
}



undefined1 FUN_0007bcde(uint param_1)

{
  if ((param_1 & 0xff) < (uint)DAT_00021865) {
    return (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x21869u + (uint32_t)(param_1 & 0xff) * 1u))));
  }
  return 0;
}



byte FUN_0007bd3a(uint param_1)

{
  byte bVar1;
  byte bVar2;
  
  bVar2 = 0;
  if (((param_1 & 0xff) < (uint)DAT_00021865) &&
     ((bVar1 = f33_upper_network_software_indication[param_1 & 0xff], bVar1 < 2 || (bVar1 == 3)))) {
    bVar2 = bVar1;
  }
  return bVar2;
}



uint FUN_0007bd58(short param_1,undefined2 param_2)

{
  byte bVar1;
  uint32_t puVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  
  puVar2 = 0x23dfcu;
  uVar5 = 0xff;
  uVar4 = uVar5;
  if ((param_1 == 0x1800) || (param_1 == 0x2000)) {
    uVar3 = FUN_00081f30(param_1,param_2);
    if ((((uVar3 & 0xf800) == 0) || ((uVar3 & 0xf800) == 0x800)) &&
       (bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x2597))))), uVar4 = FUN_0007c6c4(uVar3), bVar1 <= uVar4)) {
      uVar4 = uVar5;
    }
  }
  return uVar4;
}



uint FUN_0007bd96(short param_1,undefined2 param_2)

{
  byte bVar1;
  uint32_t puVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  
  puVar2 = 0x23dfcu;
  if (((param_1 != 0) && (param_1 != 0x1800)) && (param_1 != 0x2000)) {
    param_1 = -1;
  }
  uVar5 = 0xff;
  uVar4 = uVar5;
  if (param_1 != -1) {
    uVar3 = FUN_00081f30(param_1,param_2);
    if ((((uVar3 & 0xf800) == 0) || ((uVar3 & 0xf800) == 0x800)) &&
       (bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x2597))))), uVar4 = FUN_0007c6e8(uVar3), bVar1 <= uVar4)) {
      uVar4 = uVar5;
    }
  }
  return uVar4;
}



void FUN_0007bde2(uint param_1)

{
  uint uVar1;
  uint uVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  
  iVar4 = 0x1e;
  iVar3 = 0x11;
  uVar5 = ((param_1 & 0xffff) * 1000 + (uint)DAT_00021860) - 1;
  uVar2 = (uint)DAT_00021860 << 0x10;
  do {
    uVar1 = uVar2;
    if (iVar4 == 0x1e) {
      uVar1 = -uVar2;
    }
    uVar5 = uVar5 + uVar1;
    if ((uVar5 & 0x80000000) == 0) {
      iVar4 = 0x1e;
    }
    else {
      iVar4 = 0xe1;
    }
    uVar2 = uVar2 >> 1;
    iVar3 = iVar3 + -1;
  } while (iVar3 != 0);
  return;
}



undefined1 FUN_0007be2e(undefined1 param_1)

{
  return param_1;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_7be34(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_7be36(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_7be38(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_7be3a(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_7be3c(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_7be3e(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_7be40(void)

{
  return;
}



/* Constant source: return 0; shape-classified from the canonical corpus. Callers receive this
   literal directly; its meaning is not recovered. */

undefined4 f33_return_const_0_7be42(void)

{
  return 0;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_7be46(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_7be48(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_7be4a(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_7be4c(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_7be4e(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_7be50(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_7be52(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_7be56(void)

{
  return;
}



void FUN_0007bed0(char param_1,undefined1 param_2,char param_3)

{
  undefined4 uVar1;
  
  param_1 = DAT_0002183d + param_1;
  if (param_3 == '\x01') {
    uVar1 = FUN_0007a2da();
    FUN_0007a09c(param_1,0);
    FUN_0007a074(param_1,param_2);
    ((void)(uVar1), thunk_FUN_0006a4c4());
  }
  else {
    FUN_0007a074(param_1,param_2);
  }
  return;
}


