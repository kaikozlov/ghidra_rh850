#include "common.h"


int FUN_00078010(undefined2 param_1,undefined1 *param_2)

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
  return iVar2;
}



void FUN_0007805e(undefined *param_1)

{
  uchar auStack_8 [4];
  
  if (((uintptr_t)(param_1)!=(uintptr_t)(((undefined *)camry_host_ptr((uint32_t)(0xffff))))) &&
     (param_1 = (undefined *)f33_nvm_read_with_optional_blank_check(DAT_febf6c2c,4,auStack_8,'\x01')
     ,(uintptr_t)(param_1)==(uintptr_t)(((undefined *)camry_host_ptr((uint32_t)(0x3)))))) {
    param_1 = ((undefined *)camry_host_ptr(0xfffdu));
  }
  ((void)(param_1), FUN_0007849e());
  return;
}



undefined * FUN_0007808c(ushort param_1,ushort param_2,char param_3)

{
  uint byte_offset;
  undefined4 uVar1;
  undefined *puVar2;
  undefined4 uVar3;
  
  puVar2 = ((undefined *)camry_host_ptr(0x23dfcu));
  FUN_0007490a(0);
  if (param_3 == '\x02') {
    byte_offset = FUN_00077e0a(param_1,2);
    uVar1 = FUN_0007490a(camry_host_addr(puVar2 + 0x3e7c));
    uVar3 = 1;
  }
  else if (param_3 == '\x01') {
    byte_offset = FUN_00077e0a(param_1,1);
    uVar1 = FUN_0007490a(0x3e80u + (int)camry_host_addr(puVar2));
    uVar3 = 1;
  }
  else {
    if (param_3 != '\x03') {
      return ((undefined *)camry_host_ptr(0xfffbu));
    }
    byte_offset = FUN_00077e0a(param_1,3);
    uVar1 = FUN_0007490a(camry_host_addr(puVar2 + 0x3e84));
    uVar3 = 0;
  }
  if (param_1 < *(ushort *)(puVar2 + 0x3b2c)) {
    DAT_febf6c2c = f33_nvm_record_offset(param_1,param_2,byte_offset);
    puVar2 = (undefined *)FUN_00074c54(DAT_febf6c2c, 4, ((uchar *)camry_host_ptr((uint32_t)(uVar1))), 0, uVar3);
  }
  else {
    puVar2 = ((undefined *)camry_host_ptr(0xfffbu));
  }
  return puVar2;
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



uint FUN_00078212(int param_1,undefined4 param_2,undefined4 param_3,uint param_4,byte param_5)

{
  uint uVar1;
  uint uVar2;
  
  param_4 = param_4 & 0xff;
  uVar1 = (*(int (*)())camry_indirect((uint32_t)(((code *)(uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint)param_5 * 4 + (*((int *)camry_host_ptr((uint32_t)(param_1 + 0xc))))))))))))(param_2,param_3);
  if ((((uVar1 != 0xff) && (param_4 != uVar1)) &&
      (uVar2 = (uint)(*((byte *)camry_host_ptr((uint32_t)(*(int *)(param_1 + 8) + uVar1)))), param_4 = uVar1, uVar2 != 0xff)) &&
     (uVar1 = (*(int (*)())camry_indirect((uint32_t)(((code *)(uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(uVar2 * 4 + (*((int *)camry_host_ptr((uint32_t)(param_1 + 0xc))))))))))))(param_2,param_3), uVar1 != 0xff)) {
    param_4 = uVar1;
  }
  return param_4;
}



undefined1 FUN_000782b2(void)

{
  return DAT_febf6c4d;
}



undefined4 FUN_000782bc(void)

{
  int iVar1;
  int iVar2;
  undefined8 uVar3;
  int iVar4;
  
  uVar3 = 0x23dfc00000000;
  iVar4 = 0;
  do {
    (*(int (*)())camry_indirect((uint32_t)(((code *)(uintptr_t)(*((volatile uint32_t *)((*((int *)camry_host_ptr((uint32_t)(iVar4 * 4 + (int)((ulonglong)uVar3 >> 0x20) + 0x3ec4)))) + 0x14)))))))();
    iVar2 = iVar4 + 1;
    iVar1 = iVar4 + -1;
    iVar4 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  return 1;
}



undefined4 FUN_000782de(void)

{
  int iVar1;
  int iVar2;
  undefined8 uVar3;
  int iVar4;
  
  uVar3 = 0x23dfc00000000;
  f33_fill_constant_block_781e4();
  iVar4 = 0;
  do {
    (*(int (*)())camry_indirect((uint32_t)(((code *)(uintptr_t)(*((volatile uint32_t *)((*((int *)camry_host_ptr((uint32_t)(iVar4 * 4 + (int)((ulonglong)uVar3 >> 0x20) + 0x3ec4)))) + 0x10)))))))();
    iVar2 = iVar4 + 1;
    iVar1 = iVar4 + -1;
    iVar4 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  return 1;
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
    uVar2 = FUN_00078276(((byte *)camry_host_ptr((uint32_t)((*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + uVar3 * 4 + 0x3ec4))))))), &uStack_1c, camry_host_addr(local_34));
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



void FUN_0007841e(void)

{
  if (0 < DAT_febf6c20) {
    DAT_febf6c20 = DAT_febf6c20 - (uint)DAT_0002792a;
    if (0 < DAT_febf6c20) {
      return;
    }
    FUN_00077ce8();
    FUN_00077d14(0xfffa);
    f33_nvm_finish_physical_result();
    if (0 < DAT_febf6c20) {
      return;
    }
  }
  f33_fill_constant_block_781e4();
  FUN_000782de();
  FUN_00074e94();
  return;
}



void FUN_00078466(void)

{
  FUN_000783e8();
  ((void)(0), FUN_00078304());
  FUN_0007841e();
  return;
}



void FUN_0007847c(void)

{
  if (DAT_febf6c4d < 2) {
    (*(int (*)())camry_indirect((uint32_t)(((code *)(uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x27cc0u + (uint32_t)(DAT_febf6c4d) * 4u)))) + 0x18))))))))();
  }
  return;
}



void FUN_0007849e(void)

{
  if (DAT_febf6c4d < 2) {
    (*(int (*)())camry_indirect((uint32_t)(((code *)(uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x27cc0u + (uint32_t)(DAT_febf6c4d) * 4u)))) + 0x1c))))))))();
  }
  return;
}



void FUN_000784c0(void)

{
  if (DAT_febf6c4d < 2) {
    (*(int (*)())camry_indirect((uint32_t)(((code *)(uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x27cc0u + (uint32_t)(DAT_febf6c4d) * 4u)))) + 0x20))))))))();
  }
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



int FUN_00078566(int param_1,int param_2,uint param_3)

{
  undefined4 uVar1;
  uint uVar2;
  int iVar3;
  int iVar4;
  
  uVar2 = f33_icus20_second_read_bit0();
  if (uVar2 == 0) {
    if (DAT_febf6cb0 == '\x01') {
      if (DAT_febf6cb2 == '\x0e') {
        iVar3 = FUN_00078d80(param_2);
        if (iVar3 != 0) {
          uVar1 = 4;
          goto LAB_00078668;
        }
        iVar3 = FUN_00078d88(param_1,4);
        if (iVar3 != 0) {
          uVar1 = 2;
          goto LAB_00078668;
        }
        iVar3 = FUN_00078d9e(param_1,param_3,4);
        if (iVar3 != 0) {
          uVar1 = 3;
          goto LAB_00078668;
        }
        f33_return_only_stub_79d32();
        FUN_00078bc6();
        iVar4 = FUN_00078c70(0x80);
        iVar3 = 1;
        if (iVar4 != 0) {
          f33_return_only_stub_79d34();
          FUN_00078c70(0);
          uVar1 = 8;
          goto LAB_00078668;
        }
        f33_flash_set_software_enables(1);
        for (uVar2 = 0; uVar2 < param_3 >> 2; uVar2 = uVar2 + 1) {
          *(undefined4 *)(((undefined *)camry_host_ptr(0xfebf6c6cu)) + uVar2 * 4) = (*((undefined4 *)camry_host_ptr((uint32_t)(uVar2 * 4 + param_2))));
        }
        iVar3 = FUN_00078e2a(((undefined *)camry_host_ptr(0xfebf6c6cu)),param_1,4);
        f33_return_only_stub_79d34();
        if (iVar3 == 1) {
          DAT_febf6c60 = param_1 + 4;
          DAT_febf6c64 = camry_host_addr(((undefined *)camry_host_ptr(0xfebf6c70u)));
          DAT_febf6c68 = param_3 + param_1 + -1;
          DAT_febf6cac = 2;
          DAT_febf6cb0 = 2;
          DAT_febf6cb1 = 2;
          return 0;
        }
        FUN_00078f7a();
        f33_flash_set_software_enables(0);
        FUN_00078c70(0);
        uVar1 = 8;
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
LAB_00078668:
  FUN_0007939c(0x5c,0,2,uVar1);
  return iVar3;
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



/* Ordered admission: second ICU-S offset20 bit0 set returnsB; FEBF6CB0!=1 returns4; FEBF6CB2!=E
   returnsC. Require nonNULL destination, aligned offset<8000, nonzero aligned length<=64 and
   inclusive source end<=7FFF; invalid arguments return3. No local destination bounds/alignment
   check. Run78F28 and map zero to2, nonzero to5. Return5 does not undo destination stores.
   Conditional native execution is not a hardware readiness or complete application NvM restoration
   claim. Ordered read admission: second ICUSREG20 bit0 set returnsB; software bytes6CB0!=1
   or6CB2!=E return4/C. Require nonNULL destination and aligned bounded DataFlash offset/count; Copy
   result0 maps2 and nonzero maps5 without rollback. Destination alignment is not checked here.
   Explicit modeled hardware inputs; not a readiness or full NvM restoration claim. */

uint f33_dataflash_read_words(uint dataflash_offset,uint *destination,uint byte_count)

{
  uint uVar1;
  int iVar2;
  
  uVar1 = f33_icus20_second_read_bit0();
  if (uVar1 == 0) {
    if (DAT_febf6cb0 == '\x01') {
      if (DAT_febf6cb2 == '\x0e') {
        iVar2 = FUN_00078d80(camry_host_addr(destination));
        if (((iVar2 == 0) && (iVar2 = FUN_00078d88(dataflash_offset,4), iVar2 == 0)) &&
           (iVar2 = FUN_00078d9e(dataflash_offset,byte_count,4), iVar2 == 0)) {
          uVar1 = f33_dataflash_copy_words_ecc(dataflash_offset, camry_host_addr(destination), byte_count);
          if (uVar1 == 0) {
            uVar1 = 2;
          }
          else {
            uVar1 = 5;
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

int FUN_00078c12(void)

{
  int iVar1;
  
  iVar1 = FUN_00078bfa();
  if (iVar1 == 1) {
    FSUINITR = 0x2d00;
  }
  return iVar1;
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
  if (0x7fff < (int)uVar1 + 3) {
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

int FUN_000792c0(void)

{
  int iVar1;
  
  iVar1 = FUN_000792a6();
  if (iVar1 == 1) {
    FACI_COMMAND_AREA = 0xd0;
  }
  return iVar1;
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



undefined4 FUN_0007939c(undefined2 param_1,undefined1 param_2,undefined1 param_3,undefined1 param_4)

{
  return FUN_00074efe(param_1,param_2,param_3,param_4);
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



undefined4 FUN_00079780(uint param_1,undefined2 *param_2)

{
  int iVar1;
  undefined4 uVar2;
  
  param_1 = param_1 & 0xff;
  uVar2 = 1;
  iVar1 = FUN_00079848((uint)(byte)param_1, camry_host_addr(param_2));
  if ((iVar1 == 0) &&
     (((param_1 - 6 < 3 || (param_1 == 0xc || param_1 == 0xd)) || (param_1 - 0x16 < 3)))) {
    *param_2 = DAT_febf6cbc;
    *(uint *)(param_2 + 2) = f33_nvm_service_diagnostic_mask;
    uVar2 = 0;
  }
  return uVar2;
}



undefined4 FUN_000797c2(char param_1,undefined2 *param_2)

{
  int iVar1;
  undefined4 uVar2;
  
  uVar2 = 1;
  iVar1 = FUN_00079848((uint)(byte)param_1, camry_host_addr(param_2));
  if ((iVar1 == 0) && (param_1 == '\f' || param_1 == '\r')) {
    *param_2 = DAT_febf6cc4;
    *(uint *)(param_2 + 2) = f33_nvm_service_cd_diagnostic_mask;
    uVar2 = 0;
  }
  return uVar2;
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



void FUN_0007995c(void)

{
  if ((f33_nvm_service_guards.service == '\0') || (f33_nvm_service_guards.paired_call == '\0')) {
    f33_nvm_service_guards.deferred = '\0';
    FUN_00079d38(1);
  }
  else {
    FUN_0007990e();
  }
  return;
}



void FUN_0007998a(undefined1 param_1)

{
  if (DAT_febf6cd2 == '\0') {
    DAT_febf6cd3 = 1;
    DAT_febf6cd4 = param_1;
  }
  else {
    FUN_000798ca((uint)(byte)param_1);
  }
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



void FUN_00079a0e(void)

{
  DAT_febf6cd4 = 0xff;
  DAT_febf6cd3 = 0xff;
  DAT_febf6cd2 = 1;
  f33_nvm_service_guards.deferred = 0xff;
  f33_nvm_service_guards.paired_call = '\x01';
  f33_nvm_service_guards.service = '\x01';
  FUN_0007987e(0);
  return;
}



/* Only when6CCD==1 AND6CCE==1, set6CCF=FF; otherwise preserve it. Set6CCFFF only if6CCD==1
   and6CCE==1. Native all-exact-one consumption and either guard zero preservation. No inferred
   mutex or interrupt behavior. */

void f33_nvm_consume_deferred_guard(void)

{
  if ((f33_nvm_service_guards.service == '\x01') && (f33_nvm_service_guards.paired_call == '\x01'))
  {
    f33_nvm_service_guards.deferred = 0xff;
  }
  return;
}



/* Call79A32 BEFORE storing6CCD=0. No lock or interrupt semantics inferred. Call79A32 before
   clearing6CCD. Native quiet and admission boundary expose ordering and service guard0, with real
   downstream calls. */

void f33_nvm_enter_service_guard(void)

{
  f33_nvm_consume_deferred_guard();
  f33_nvm_service_guards.service = '\0';
  return;
}



/* Only when6CCD==1 AND6CCE==1: call7990E if6CCF==0, then storeFF. Native non-notifying branches and
   exact7990E entry; its body is a separate dependency, not a substituted callback. Require both
   guard bytes exactly1. Under that condition call real7990E only for pending6CCF0, then set6CCFFF.
   Native no-notification branches and boundary at7990E before its body; no replacement callback. */

void f33_nvm_finish_deferred_guard(void)

{
  if ((f33_nvm_service_guards.service == '\x01') && (f33_nvm_service_guards.paired_call == '\x01'))
  {
    if (f33_nvm_service_guards.deferred == '\0') {
      FUN_0007990e();
    }
    f33_nvm_service_guards.deferred = 0xff;
  }
  return;
}



/* Store6CCD=1 then call79A64. Deferred7990E branch remains bounded at entry. Set6CCD1 then
   call79A64. Native second guard0 prevents notification/latch consumption; both1 plus pending0
   reaches real7990E. Deferred dependency body remains outside this proof. */

void f33_nvm_leave_service_guard(void)

{
  f33_nvm_service_guards.service = '\x01';
  f33_nvm_finish_deferred_guard();
  return;
}



void FUN_00079aaa(void)

{
  f33_nvm_consume_deferred_guard();
  f33_nvm_service_guards.paired_call = '\0';
  return;
}



void FUN_00079abe(void)

{
  f33_nvm_service_guards.paired_call = '\x01';
  f33_nvm_finish_deferred_guard();
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



undefined4 FUN_00079b70(void)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = FUN_000741a0();
  if (iVar1 == 2) {
    uVar2 = 0x1e;
  }
  else if ((iVar1 == 4) ||
          ((iVar1 = FUN_00079c94(), iVar1 == 0 && (iVar1 = thunk_FUN_00076688(), iVar1 != 1)))) {
    uVar2 = 0xf0;
  }
  else {
    uVar2 = 0xf;
  }
  return uVar2;
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



void FUN_00079be8(undefined1 param_1)

{
  DAT_febf6cd8 = param_1;
  FUN_0007969a((uint)(byte)param_1);
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



uint FUN_00079dcc(undefined2 param_1)

{
  return FUN_0007a38c(param_1);
}



undefined4 FUN_00079dda(undefined2 param_1,undefined1 param_2,undefined2 param_3)

{
  return FUN_00081fa6(param_1,param_2,param_3);
}



uint FUN_00079dec(undefined2 param_1)

{
  return FUN_0007a3ca(param_1);
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



undefined4 FUN_00079f5c(void)

{
  byte bVar1;
  uint32_t puVar2;
  int iVar3;
  undefined4 uVar4;
  byte bVar5;
  
  puVar2 = 0x23dfcu;
  if (((int16_t)DAT_febe3df2) == -0x1ff) {
    f33_return_only_stub_7be40();
    bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x2597)))));
    for (bVar5 = 0; bVar5 < bVar1; bVar5 = bVar5 + 1) {
      iVar3 = FUN_0007e804(bVar5);
      if (iVar3 != 0) {
        return 0xff;
      }
    }
    uVar4 = FUN_0007c58c();
  }
  else {
    uVar4 = 0;
  }
  return uVar4;
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



void FUN_0007a232(void)

{
  if (((int16_t)DAT_febe3df2) == -0x1ff) {
    f33_return_only_stub_7be4e();
    FUN_00079eba();
    FUN_00079eca();
    f33_return_only_stub_7be50();
  }
  return;
}



void FUN_0007a254(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (((int16_t)DAT_febe3df2) == -0x1ff) {
    f33_return_only_stub_7be3c();
    FUN_0007bbc2();
    FUN_0007c43c();
    FUN_00079ede();
    FUN_0007bf60();
    ((void)(1), FUN_0007d01a(camry_host_addr(((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x7a16))))));
    FUN_0007d6c2(camry_host_addr(((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x7a12)))));
    FUN_0007d69e(camry_host_addr(((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x7a14)))));
    f33_return_only_stub_7be52();
    FUN_0007d52c();
    f33_return_only_stub_7be38();
    f33_return_only_stub_7be3a();
    f33_return_only_stub_7be40();
    thunk_FUN_0007ef9c();
    FUN_0007eb32();
    f33_run_init_chain_79f16();
    f33_service_com_tx_publication();
    FUN_0006a410();
    FUN_00082e32();
    thunk_FUN_00079d7a();
    f33_return_only_stub_7be3e();
  }
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



uint FUN_0007a334(ushort param_1,uint param_2)

{
  F33CanTpConfiguration *configuration;
  uint uVar1;
  
  uVar1 = 1;
  if ((((((int8_t)DAT_febe4f3d) == -0x56) &&
       (configuration = (F33CanTpConfiguration *)FUN_0007a32e(),(uintptr_t)(configuration)!=(uintptr_t)((F33CanTpConfiguration *)0x0))) &&
      ((uint)configuration->first_transmit_id <= (uint)param_1)) &&
     ((int)((uint)param_1 -
           ((uint)configuration->transmit_count + (uint)configuration->first_transmit_id)) < 0)) {
    uVar1 = f33_cantp_accept_transmit_length(configuration,param_1,param_2);
  }
  return uVar1;
}



/* Read response length at+4 and pass to7A334; propagate real R10 result. Does not copy payload. */

uint f33_cantp_transmit_descriptor(ushort transmit_id,F33PduInfo *response)

{
  uint uVar1;
  
  uVar1 = FUN_0007a334(transmit_id,response->length);
  return uVar1;
}



uint FUN_0007a38c(ushort param_1)

{
  F33CanTpConfiguration *configuration;
  uint uVar1;
  
  uVar1 = 1;
  if ((((((int8_t)DAT_febe4f3d) == -0x56) &&
       (configuration = (F33CanTpConfiguration *)FUN_0007a32e(),(uintptr_t)(configuration)!=(uintptr_t)((F33CanTpConfiguration *)0x0))) &&
      ((uint)configuration->first_transmit_id <= (uint)param_1)) &&
     ((int)((uint)param_1 -
           ((uint)configuration->transmit_count + (uint)configuration->first_transmit_id)) < 0)) {
    uVar1 = f33_cantp_cancel_transmit_owner(configuration,param_1);
  }
  return uVar1;
}



uint FUN_0007a3ca(ushort param_1)

{
  F33CanTpConfiguration *configuration;
  uint uVar1;
  
  uVar1 = 1;
  if ((((((int8_t)DAT_febe4f3d) == -0x56) &&
       (configuration = (F33CanTpConfiguration *)FUN_0007a32e(),(uintptr_t)(configuration)!=(uintptr_t)((F33CanTpConfiguration *)0x0))) &&
      ((uint)configuration->first_receive_id <= (uint)param_1)) &&
     ((int)((uint)param_1 -
           ((uint)configuration->receive_count + (uint)configuration->first_receive_id)) < 0)) {
    uVar1 = f33_cantp_cancel_receive_owner(configuration,param_1);
  }
  return uVar1;
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



void FUN_0007a4e4(F33CanTpConfiguration *param_1,F33CanTpFrameInfo *param_2,ushort param_3)

{
  byte bVar1;
  uint32_t puVar2;
  F33CanTpConfiguration *configuration;
  F33CanTpRxConnection *connection;
  F33CanTpTxConnection *connection_00;
  
  puVar2 = 0x23dfcu;
  if (param_2->length < 2) {
    return;
  }
  connection = f33_cantp_find_receive_frame_connection(param_1, param_3, ((uchar *)camry_host_ptr((uint32_t)(param_2->data))));
  if ((uintptr_t)(connection)!=(uintptr_t)((F33CanTpRxConnection *)0x0)) {
    bVar1 = ((uint8_t *)camry_host_ptr((uint32_t)(param_2->data)))[(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(connection->addressing_format - 0x1264)))))] & 0xf0;
    if ((((uint8_t *)camry_host_ptr((uint32_t)(param_2->data)))[(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(connection->addressing_format - 0x1264)))))] & 0xf0) == 0) {
      FUN_0007adf8(param_1, connection, param_2);
      return;
    }
    if (bVar1 == 0x10) {
      FUN_0007af76(param_1, connection, param_2);
      return;
    }
    if (bVar1 == 0x20) {
      f33_cantp_handle_consecutive_receive(connection,param_2);
      return;
    }
  }
  connection_00 = f33_cantp_find_flow_control_connection(configuration, param_3, ((uchar *)camry_host_ptr((uint32_t)(param_2->data))));
  if (((uintptr_t)(connection_00)!=(uintptr_t)((F33CanTpTxConnection *)0x0)) &&
     ((((uint8_t *)camry_host_ptr((uint32_t)(param_2->data)))[(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(connection_00->addressing_format - 0x1264)))))] & 0xf0) == 0x30)) {
    f33_cantp_handle_flow_control(connection_00,param_2);
  }
  return;
}



/* Require initialized markerAA and configured CanIf receive range0804..0806. Widen descriptor
   length16 into internal frame length32 and dispatch SF/FF/CF or flow control; frame bytes remain
   caller-owned during this call. */

void f33_cantp_receive_can_frame(ushort canif_receive_id,F33PduInfo *pdu)

{
  uint uVar1;
  undefined4 *extraout_r7;
  int iVar2;
  undefined4 local_14;
  uint uStack_10;
  
  uVar1 = (uint)canif_receive_id;
  if ((((((int8_t)DAT_febe4f3d) == -0x56) && (iVar2 = camry_host_addr(FUN_0007a32e()), iVar2 != 0)) &&
      ((*((ushort *)camry_host_ptr((uint32_t)(iVar2 + 8)))) <= uVar1)) &&
     ((int)(uVar1 - ((uint)(*((byte *)camry_host_ptr((uint32_t)(iVar2 + 0xf)))) + (uint)(*((ushort *)camry_host_ptr((uint32_t)(iVar2 + 8)))))) < 0)) {
    local_14 = *extraout_r7;
    uStack_10 = (uint)*(ushort *)(extraout_r7 + 1);
    FUN_0007a4e4(((F33CanTpConfiguration *)camry_host_ptr((uint32_t)(iVar2))), &local_14, uVar1);
  }
  return;
}



/* Require initialized marker and configured confirmation range0800..0803; prefer matching active Tx
   connection, else active receive FC owner. Per-frame progression and aggregate application
   completion remain distinct. */

void f33_cantp_confirm_can_frame(ushort canif_confirmation_id)

{
  F33CanTpConfiguration *configuration;
  F33CanTpConfiguration *configuration_00;
  F33CanTpTxConnection *connection;
  F33CanTpRxConnection *connection_00;
  
  if ((((((int8_t)DAT_febe4f3d) == -0x56) &&
       (configuration_00 = (F33CanTpConfiguration *)FUN_0007a32e(),(uintptr_t)(configuration_00)!=(uintptr_t)((F33CanTpConfiguration *)0x0))) &&
      ((uint)configuration_00->first_canif_confirmation_id <= (uint)canif_confirmation_id)) &&
     ((int)((uint)canif_confirmation_id -
           ((uint)configuration_00->canif_confirmation_count +
           (uint)configuration_00->first_canif_confirmation_id)) < 0)) {
    connection = f33_cantp_find_active_transmit_confirmation(configuration_00,canif_confirmation_id)
    ;
    if ((uintptr_t)(connection)==(uintptr_t)((F33CanTpTxConnection *)0x0)) {
      connection_00 =
           f33_cantp_find_active_receive_confirmation(configuration,canif_confirmation_id);
      if ((uintptr_t)(connection_00)!=(uintptr_t)((F33CanTpRxConnection *)0x0)) {
        f33_cantp_confirm_receive_flow_control(connection_00);
      }
    }
    else {
      f33_cantp_handle_frame_confirmation(connection);
    }
  }
  return;
}



/* Release retained receive ID, remaining bytes, countdown, wait count, sequence and FC state.
   Preserve admission generation byte+0F; it qualifies a surrounding foreground reset. */

void f33_cantp_reset_receive_owner(F33CanTpRxState *state)

{
  state->receive_id = 0xffff;
  state->remaining_length = 0;
  state->state = 0xe1;
  state->expected_sequence_number = 0xff;
  state->timeout_ticks = 0;
  state->wait_frame_count = 0;
  state->first_frame_dlc = '\0';
  state->block_remaining = '\0';
  state->flow_status_marker = 0xf0;
  return;
}



void FUN_0007a79e(undefined2 param_1,undefined1 param_2)

{
  FUN_00081a00(param_1,param_2);
  return;
}



/* Reset transport receive owner before forwarding the supplied aggregate result through PduR to the
   configured upper receive indication. Result0 is aggregate software receive success, not service
   completion. */

void f33_cantp_finish_receive_aggregate
               (F33CanTpRxConnection *connection,F33CanTpRxState *state,uchar result)

{
  undefined4 extraout_r8;
  
  f33_cantp_reset_receive_owner(state);
  FUN_0007a79e(connection->upper_receive_id,extraout_r8);
  return;
}



/* Cancel matching active receive work in FC/wait states, but refuse state4B when remaining bytes
   fit one final CF. Exact lower cancel hook7B246 is a no-op; upper failure/reset is separate. */

uint f33_cantp_cancel_receive_owner(F33CanTpConfiguration *configuration,ushort receive_id)

{
  int iVar1;
  char cVar2;
  uint32_t puVar3;
  uint32_t puVar4;
  F33CanTpRxConnection *connection;
  uint uVar5;
  F33CanTpRxState *state;
  
  puVar3 = 0xfebeb800u;
  puVar4 = 0x23dfcu;
  uVar5 = 1;
  connection = f33_cantp_find_receive_connection(configuration,receive_id);
  iVar1 = (uint)connection->channel_state_index * 0x20;
  state = ((F33CanTpRxState *)camry_host_ptr((uint32_t)(puVar3 + iVar1 + -0x68b0)));
  if (receive_id == (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + iVar1 + -0x68ac))))) {
    cVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(iVar1 + -0x68a6)))));
    if (cVar2 == 'K') {
      if (state->remaining_length <=
          (8 - ((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(connection->addressing_format - 0x1264))))) + 1) & 0xff)) {
        return 1;
      }
    }
    else if (cVar2 == 'Z') {
      ((void)(connection->canif_fc_transmit_id), f33_return_only_stub_7b246());
    }
    else if (cVar2 != 'i') {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x68c4))))) = 0xf;
      f33_cantp_reset_receive_owner(state);
      return 1;
    }
    f33_cantp_finish_receive_aggregate(connection,state,'\x01');
    uVar5 = 0;
  }
  return uVar5;
}



void FUN_0007a84c(byte *param_1,ushort param_2)

{
  f33_cantp_rx_flow_parameters_with_complements[*param_1][0] = param_2 | (param_2 ^ 0xff) << 8;
  return;
}



uint FUN_0007a862(byte *param_1)

{
  uint uVar1;
  
  uVar1 = (uint)f33_cantp_rx_flow_parameters_with_complements[*param_1][0];
  if ((uVar1 & 0xff ^ (int)uVar1 >> 8) != 0xff) {
    uVar1 = (uint)param_1[0x16];
    DAT_febe4f3c = 0xf;
    FUN_0007a84c(param_1,uVar1);
  }
  return uVar1 & 0xff;
}



void FUN_0007a89a(byte *param_1,ushort param_2)

{
  f33_cantp_rx_flow_parameters_with_complements[*param_1][1] = param_2 | (param_2 ^ 0xff) << 8;
  return;
}



uint FUN_0007a8b0(byte *param_1)

{
  uint uVar1;
  
  uVar1 = (uint)f33_cantp_rx_flow_parameters_with_complements[*param_1][1];
  if ((uVar1 & 0xff ^ (int)uVar1 >> 8) != 0xff) {
    uVar1 = (uint)param_1[0x17];
    DAT_febe4f3c = 0xf;
    FUN_0007a89a(param_1,uVar1);
  }
  return uVar1 & 0xff;
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



/* Construct PCI30|status plus BS/STmin in shared frame scratch and submit actual CanIf route. Exact
   physical rows pad to8 with00; return actual software enqueue status. */

uint f33_cantp_queue_receive_flow_control
               (F33CanTpRxConnection *connection,uchar flow_status,uchar block_size,uchar stmin)

{
  uint uVar1;
  F33CanTpFrameInfo local_c;
  
  f33_cantp_shared_frame_scratch[3] = DAT_00022c46;
  f33_cantp_shared_frame_scratch[4] = DAT_00022c46;
  f33_cantp_shared_frame_scratch[5] = DAT_00022c46;
  f33_cantp_shared_frame_scratch[6] = DAT_00022c46;
  f33_cantp_shared_frame_scratch[7] = DAT_00022c46;
  uVar1 = (uint)connection->addressing_format;
  if (uVar1 == 4) {
    f33_cantp_shared_frame_scratch[0] = connection->flow_control_address_byte;
  }
  else if (uVar1 == 2 || uVar1 == 3) {
    f33_cantp_shared_frame_scratch[0] = connection->extended_flow_address_byte;
  }
  uVar1 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22b98u + (uint32_t)(uVar1) * 1u))));
  f33_cantp_shared_frame_scratch[uVar1] = flow_status | 0x30;
  f33_cantp_shared_frame_scratch[uVar1 + 1] = block_size;
  local_c.length = 8;
  f33_cantp_shared_frame_scratch[uVar1 + 2] = stmin;
  if (connection->pad_flow_control_to_eight == '\0') {
    local_c.length = uVar1 + 3 & 0xff;
  }
  local_c.data = camry_host_addr(f33_cantp_shared_frame_scratch);
  uVar1 = f33_cantp_submit_can_frame(connection->canif_fc_transmit_id,&local_c);
  return uVar1;
}



/* Query upper capacity with a zero-length copy, choose CTS or timed WAIT, and enforce configured
   wait-frame limit. Upper overflow stateD2 queues FC32. State5A/countdownN_Ar+2 precedes lower
   frame confirmation. */

void f33_cantp_poll_receive_capacity_and_flow
               (F33CanTpRxConnection *connection,F33CanTpRxState *state)

{
  ushort uVar1;
  uint32_t puVar2;
  uint32_t puVar3;
  F33CanTpRxConnection *connection_00;
  int extraout_r6;
  uchar block_size;
  uchar stmin;
  ushort uVar4;
  uint uVar5;
  uint local_28;
  F33CanTpFrameInfo FStack_24;
  
  puVar2 = 0xfebeb800u;
  puVar3 = 0x23dfcu;
  uVar4 = state->wait_frame_count;
  uVar5 = (uint)state->flow_status_marker;
  block_size = FUN_0007a862(connection);
  stmin = FUN_0007a8b0(connection);
  if (uVar5 == 0xe1) {
    FStack_24.length = 0;
    FStack_24.data = 0;
    local_28 = 0;
    uVar5 = f33_cantp_copy_upper_receive_bytes((*((ushort *)camry_host_ptr((uint32_t)(extraout_r6 + 8)))),&FStack_24,&local_28);
    if (uVar5 != 0) goto LAB_0007aa86;
    uVar5 = f33_cantp_select_receive_flow_status
                      (state->remaining_length,local_28,
                       '\a' - (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(connection_00->addressing_format - 0x1264))))),block_size);
    if (uVar5 == 0xf0) goto LAB_0007aa5c;
    if (state->timeout_ticks != 0) {
      return;
    }
    if (connection_00->wait_frame_limit <= uVar4) goto LAB_0007aa86;
    uVar4 = uVar4 + 1;
  }
  else {
    if (uVar5 != 0xd2) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x68c4))))) = 0xf;
      f33_cantp_reset_receive_owner(state);
      return;
    }
LAB_0007aa5c:
    uVar4 = 0;
  }
  state->state = 'Z';
  uVar1 = connection_00->frame_confirmation_timeout_raw;
  state->flow_status_marker = (byte)uVar5;
  state->wait_frame_count = uVar4;
  state->block_remaining = block_size;
  state->timeout_ticks = uVar1 + 2;
  uVar5 = f33_cantp_queue_receive_flow_control(connection_00,(byte)uVar5 & 0xf,block_size,stmin);
  if (uVar5 == 0) {
    return;
  }
LAB_0007aa86:
  f33_cantp_finish_receive_aggregate(connection_00,state,'\x01');
  return;
}



void FUN_0007aaa2(int param_1,F33CanTpRxState *param_2)

{
  if (param_2->state == 'Z') {
    f33_cantp_reset_receive_owner(param_2);
    ((void)((*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 10))))), f33_return_only_stub_7b246());
    FUN_0007a79e((*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 8)))),1);
  }
  return;
}



void FUN_0007aace(int param_1,F33CanTpRxState *param_2)

{
  if (param_2->state == 'K') {
    f33_cantp_reset_receive_owner(param_2);
    FUN_0007a79e((*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 8)))),1);
  }
  return;
}



/* Return0 only for nonzero SF length within7-addressOffset, physical extent<=8 and enough supplied
   bytes. Exact rows require an eight-byte padded CAN frame; rejected length does not copy payload.
    */

uint f33_cantp_reject_single_frame_extent(F33CanTpRxConnection *connection,F33CanTpFrameInfo *frame)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  
  uVar3 = 1;
  uVar5 = frame->length;
  uVar4 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22b98u + (uint32_t)(connection->addressing_format) * 1u))));
  if (((uVar5 < 9) && (uVar2 = ((uint8_t *)camry_host_ptr((uint32_t)(frame->data)))[uVar4] & 0xf, (((uint8_t *)camry_host_ptr((uint32_t)(frame->data)))[uVar4] & 0xf) != 0)) &&
     (uVar1 = 7 - uVar4,
     (int)(uVar2 - uVar1) < 0 != ((int)uVar1 < 0 && (int)uVar1 < 0 == (int)(uVar2 - uVar1) < 0) ||
     uVar2 == uVar1)) {
    if (connection->require_padded_receive == '\x01') {
      if (uVar5 != 8) {
        return uVar3;
      }
    }
    else if (uVar5 < (uVar2 + uVar4 + 1 & 0xff)) {
      return uVar3;
    }
    uVar3 = 0;
  }
  return uVar3;
}



/* WARNING: Inlined function: f33_cantp_reset_transmit_owner */

undefined4 FUN_0007abe6(F33CanTpConfiguration *param_1,int param_2)

{
  uint uVar1;
  uint32_t puVar2;
  uchar uVar3;
  F33CanTpTxConnection *connection;
  F33CanTpTxStatePrefix *state;
  
  puVar2 = 0xfebeb800u;
  uVar1 = (uint)(*((byte *)camry_host_ptr((uint32_t)(param_2 + 1))));
  state = ((void *)camry_host_ptr((uint32_t)((0xfebe4f40u) + uVar1 * 2)));
  connection = f33_cantp_find_transmit_connection
                         (param_1,((volatile F33CanTpTxStatePrefix *)camry_host_ptr(0xfebe4f40u))[uVar1 * 2].transmit_id);
  if ((uintptr_t)(connection)==(uintptr_t)((F33CanTpTxConnection *)0x0)) {
LAB_0007ac88:
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x68c4))))) = 0xf;
    ((volatile F33CanTpTxStatePrefix *)camry_host_ptr(0xfebe4f40u))[uVar1 * 2].transmit_id = 0xffff;
    state->remaining_or_accepted_length = 0;
    ((volatile F33CanTpTxStatePrefix *)camry_host_ptr(0xfebe4f40u))[uVar1 * 2].state = 0xe1;
    ((volatile F33CanTpTxStatePrefix *)camry_host_ptr(0xfebe4f40u))[uVar1 * 2].timeout_ticks = 0;
    ((volatile F33CanTpTxStatePrefix *)camry_host_ptr(0xfebe4f40u))[uVar1 * 2].sequence_number = 0xff;
    ((volatile F33CanTpTxStatePrefix *)camry_host_ptr(0xfebe4f40u))[uVar1 * 2].block_remaining = '\0';
    ((volatile F33CanTpTxStatePrefix *)camry_host_ptr(0xfebe4f40u))[uVar1 * 2].block_size = '\0';
    ((volatile F33CanTpTxStatePrefix *)camry_host_ptr(0xfebe4f40u))[uVar1 * 2].spacing_ticks = '\0';
    return 0;
  }
  uVar3 = ((volatile F33CanTpTxStatePrefix *)camry_host_ptr(0xfebe4f40u))[uVar1 * 2].state;
  if ((uVar3 == 0xc3) || ((uVar3 == 0x87 && (state->remaining_or_accepted_length == 0)))) {
    if (connection->overlap_final_confirmation_policy == '\0') goto LAB_0007ac40;
    if (connection->overlap_final_confirmation_policy == '\x01') {
      uVar3 = '\0';
      goto LAB_0007ac82;
    }
LAB_0007ac4c:
    ((void)(connection->canif_frame_id), f33_return_only_stub_7b246());
  }
  else {
    if ((uVar3 == 0xb4) || (uVar3 == 0x87)) {
LAB_0007ac40:
      if (connection->preemption_rank <= (*((byte *)camry_host_ptr((uint32_t)(param_2 + 0x1d))))) {
        return 1;
      }
      goto LAB_0007ac4c;
    }
    if ((((uVar3 != 'x') && (uVar3 != 0x96)) && (uVar3 != 0xa5)) && (uVar3 != 0xd2))
    goto LAB_0007ac88;
    if (connection->preemption_rank <= (*((byte *)camry_host_ptr((uint32_t)(param_2 + 0x1d))))) {
      return 1;
    }
  }
  uVar3 = '\x01';
LAB_0007ac82:
  f33_cantp_finish_transmit_aggregate(connection,state,uVar3);
  return 0;
}



undefined4 FUN_0007ac9c(F33CanTpConfiguration *param_1,int param_2)

{
  uchar uVar1;
  uchar uVar2;
  ushort receive_id;
  uint uVar3;
  undefined *puVar4;
  F33CanTpRxConnection *connection;
  
  puVar4 = ((undefined *)camry_host_ptr(0xfebeb800u));
  uVar3 = (uint)(*((byte *)camry_host_ptr((uint32_t)(param_2 + 1))));
  uVar1 = ((volatile F33CanTpRxState *)camry_host_ptr(0xfebe4f50u))[uVar3 * 2].state;
  uVar2 = ((volatile F33CanTpRxState *)camry_host_ptr(0xfebe4f50u))[uVar3 * 2].flow_status_marker;
  if (uVar1 == 0xe1) {
    return 0;
  }
  if ((uVar1 == 'i') || (uVar1 == 'K')) {
    receive_id = ((volatile F33CanTpRxState *)camry_host_ptr(0xfebe4f50u))[uVar3 * 2].receive_id;
    puVar4 = ((undefined *)camry_host_ptr(0xfebeb800u));
    connection = f33_cantp_find_receive_connection(param_1,receive_id);
    if ((uintptr_t)(connection)!=(uintptr_t)((F33CanTpRxConnection *)0x0)) {
      if ((receive_id != (*((ushort *)camry_host_ptr((uint32_t)(param_2 + 2))))) &&
         (connection->preemption_rank <= (*((byte *)camry_host_ptr((uint32_t)(param_2 + 0x1d)))))) {
        return 1;
      }
LAB_0007ad36:
      f33_cantp_finish_receive_aggregate(connection, ((F33CanTpRxState *)camry_host_ptr((uint32_t)((0xfebe4f50u) + uVar3 * 2))), '\x01');
      return 0;
    }
  }
  else if ((uVar1 == 'Z') &&
          (puVar4 = ((undefined *)camry_host_ptr(0xfebeb800u)),
          connection = f33_cantp_find_receive_connection
                                 (param_1,((volatile F33CanTpRxState *)camry_host_ptr(0xfebe4f50u))[uVar3 * 2].receive_id),(uintptr_t)(connection)!=(uintptr_t)((F33CanTpRxConnection *)0x0))) {
    if ((uVar2 == 0xf0) || (uVar2 == 0xe1)) {
      if ((((volatile F33CanTpRxState *)camry_host_ptr(0xfebe4f50u))[uVar3 * 2].receive_id != (*((ushort *)camry_host_ptr((uint32_t)(param_2 + 2))))) &&
         (connection->preemption_rank <= (*((byte *)camry_host_ptr((uint32_t)(param_2 + 0x1d)))))) {
        return 1;
      }
      ((void)(connection->canif_fc_transmit_id), f33_return_only_stub_7b246());
      goto LAB_0007ad36;
    }
    if (uVar2 == 0xd2) {
      ((void)(connection->canif_fc_transmit_id), f33_return_only_stub_7b246());
      goto LAB_0007ad56;
    }
  }
  puVar4[-0x68c4] = 0xf;
LAB_0007ad56:
  f33_cantp_reset_receive_owner(((F33CanTpRxState *)camry_host_ptr((uint32_t)((0xfebe4f50u) + uVar3 * 2))));
  return 0;
}



/* Strip PCI/address prefix, claim upper buffer for SF extent, copy exactly that extent when
   capacity suffices, then report aggregate result. Padding never enters the upper buffer. */

void f33_cantp_deliver_single_frame(F33CanTpRxConnection *connection,F33CanTpFrameInfo *frame)

{
  ushort upper_id;
  uint uVar1;
  undefined4 uVar2;
  uint uVar3;
  uint local_1c;
  F33CanTpFrameInfo FStack_18;
  
  upper_id = connection->upper_receive_id;
  FStack_18.data = frame->data + (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22b98u + (uint32_t)(connection->addressing_format) * 1u)))) + 1;
  local_1c = 0;
  uVar3 = ((uint8_t *)camry_host_ptr((uint32_t)(frame->data)))[(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22b98u + (uint32_t)(connection->addressing_format) * 1u))))] & 0xf;
  FStack_18.length = uVar3;
  uVar1 = f33_cantp_start_upper_receive(upper_id,&FStack_18,(ushort)uVar3,&local_1c);
  if (uVar1 == 0) {
    uVar2 = 1;
    if (uVar3 <= local_1c) {
      uVar1 = f33_cantp_copy_upper_receive_bytes(upper_id,&FStack_18,&local_1c);
      if (uVar1 == 0) {
        uVar2 = 0;
      }
      else {
        uVar2 = 1;
      }
    }
    FUN_0007a79e(upper_id,uVar2);
  }
  return;
}



void FUN_0007adf8(int *param_1,F33CanTpRxConnection *param_2,F33CanTpFrameInfo *param_3)

{
  byte bVar1;
  uint32_t puVar2;
  int extraout_r8;
  uint uVar3;
  int iVar4;
  
  puVar2 = 0xfebeb800u;
  uVar3 = f33_cantp_reject_single_frame_extent(param_2,param_3);
  if ((uVar3 == 0) &&
     (iVar4 = ((void)(param_2->receive_id), (void)(param_2->canif_receive_id), (void)((*((undefined1 *)camry_host_ptr((uint32_t)(extraout_r8 + 4))))), (void)(param_3->data), f33_return_const_0_81f62()), iVar4 == 0)) {
    bVar1 = param_2->channel_state_index;
    if (((*((char *)camry_host_ptr((uint32_t)((short)(ushort)bVar1 * 0xc + *param_1 + 8)))) == '\x01') &&
       (((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)((uint)bVar1 * 0x20 + -0x68b8)))))) != -0x1f)) {
      iVar4 = FUN_0007abe6(param_1, camry_host_addr(param_2));
    }
    else {
      iVar4 = FUN_0007ac9c(param_1, camry_host_addr(param_2));
    }
    if (iVar4 == 0) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)((uint)bVar1 * 0x20 + -0x68a1))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)((uint)bVar1 * 0x20 + -0x68a1))))) + '\x01';
      f33_cantp_deliver_single_frame(param_2,param_3);
    }
  }
  return;
}



/* Retain remaining total minus first-frame payload, expected SN1, DLC and capacity-poll state69.
   Start upper receive before copying the first6 configured bytes; upper return3 records
   FC-overflowD2, other refusal resets. */

void f33_cantp_begin_first_frame_receive
               (F33CanTpRxConnection *connection,F33CanTpFrameInfo *frame,F33CanTpRxState *state)

{
  byte *pbVar1;
  byte bVar2;
  ushort uVar3;
  uint uVar4;
  uint uVar5;
  uint local_20;
  F33CanTpFrameInfo FStack_1c;
  
  bVar2 = (byte)frame->length;
  state->state = 'i';
  uVar3 = connection->buffer_wait_timeout_raw;
  state->first_frame_dlc = bVar2;
  state->timeout_ticks = uVar3 - 3;
  uVar3 = connection->receive_id;
  state->wait_frame_count = 0;
  state->receive_id = uVar3;
  state->expected_sequence_number = '\x01';
  state->flow_status_marker = 0xe1;
  uVar3 = connection->upper_receive_id;
  pbVar1 = ((void *)camry_host_ptr((uint32_t)(frame->data + (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22b98u + (uint32_t)(connection->addressing_format) * 1u)))))));
  uVar5 = (uint)bVar2 - ((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22b98u + (uint32_t)(connection->addressing_format) * 1u)))) + 2) & 0xff;
  FStack_1c.data = camry_host_addr(pbVar1 + 2);
  local_20 = 0;
  uVar4 = (uint)pbVar1[1] | (*pbVar1 & 0xf) << 8;
  state->remaining_length = uVar4 - uVar5;
  FStack_1c.length = uVar5;
  uVar4 = f33_cantp_start_upper_receive(uVar3,&FStack_1c,(ushort)uVar4,&local_20);
  if (uVar4 == 0) {
    if ((local_20 < uVar5) ||
       (uVar4 = f33_cantp_copy_upper_receive_bytes(uVar3,&FStack_1c,&local_20), uVar4 != 0)) {
      f33_cantp_finish_receive_aggregate(connection,state,'\x01');
    }
  }
  else if (uVar4 == 3) {
    state->flow_status_marker = 0xd2;
  }
  else {
    f33_cantp_reset_receive_owner(state);
  }
  return;
}



void FUN_0007af76(int *param_1,F33CanTpRxConnection *param_2,F33CanTpFrameInfo *param_3)

{
  byte bVar1;
  uint32_t puVar2;
  int extraout_r8;
  uint uVar3;
  int iVar4;
  
  puVar2 = 0xfebeb800u;
  uVar3 = f33_cantp_reject_first_frame_extent(param_2,param_3);
  if ((uVar3 == 0) &&
     (iVar4 = ((void)(param_2->receive_id), (void)(param_2->canif_receive_id), (void)((*((undefined1 *)camry_host_ptr((uint32_t)(extraout_r8 + 4))))), (void)(param_3->data), f33_return_const_0_81f62()), iVar4 == 0)) {
    bVar1 = param_2->channel_state_index;
    if (((*((char *)camry_host_ptr((uint32_t)((short)(ushort)bVar1 * 0xc + *param_1 + 8)))) == '\x01') &&
       (((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)((uint)bVar1 * 0x20 + -0x68b8)))))) != -0x1f)) {
      iVar4 = FUN_0007abe6(param_1, camry_host_addr(param_2));
    }
    else {
      iVar4 = FUN_0007ac9c(param_1, camry_host_addr(param_2));
    }
    if (iVar4 == 0) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)((uint)bVar1 * 0x20 + -0x68a1))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)((uint)bVar1 * 0x20 + -0x68a1))))) + '\x01';
      f33_cantp_begin_first_frame_receive
                (param_2,param_3,((F33CanTpRxState *)camry_host_ptr((uint32_t)(puVar2 + (uint)bVar1 * 0x20 + -0x68b0))));
    }
  }
  return;
}



/* Require configured padded extent and expected low-nibble sequence. Wrong sequence or short
   required-padding final frame aborts upper reception; other malformed extents may be ignored
   without resetting the owner. */

uint f33_cantp_reject_consecutive_frame
               (F33CanTpRxConnection *connection,F33CanTpFrameInfo *frame,F33CanTpRxState *state)

{
  bool bVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  
  uVar4 = 1;
  if (connection->single_frame_only != '\0') {
    return 1;
  }
  uVar2 = frame->length;
  uVar3 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22b98u + (uint32_t)(connection->addressing_format) * 1u))));
  if ((7 - uVar3 & 0xff) < state->remaining_length) {
    if (uVar2 != 8) {
      return 1;
    }
  }
  else {
    if (8 < uVar2) {
      return 1;
    }
    if (connection->require_padded_receive == '\x01') {
      if (uVar2 != 8) goto LAB_0007b05c;
    }
    else if (uVar2 < (state->remaining_length + uVar3 + 1 & 0xff)) {
      return 1;
    }
  }
  bVar1 = (((uint8_t *)camry_host_ptr((uint32_t)(frame->data)))[uVar3] & 0xf) == state->expected_sequence_number;
  uVar4 = (uint)!bVar1;
  if (bVar1) {
    return 0;
  }
LAB_0007b05c:
  f33_cantp_finish_receive_aggregate(connection,state,(uchar)uVar4);
  return uVar4;
}



/* Copy min(remaining,frameDLC-addressOffset-1) bytes to upper owner. Advance modulo16 sequence and
   block countdown for nonfinal CF; block exhaustion schedules another FC. Zero remaining completes
   aggregate reception, excluding CAN padding. */

void f33_cantp_append_consecutive_receive
               (F33CanTpRxConnection *connection,F33CanTpFrameInfo *frame,F33CanTpRxState *state)

{
  ushort uVar1;
  F33CanTpRxConnection *extraout_r6;
  F33CanTpRxConnection *pFVar2;
  F33CanTpRxState *extraout_r8;
  F33CanTpRxState *pFVar3;
  int iVar4;
  uint uVar5;
  uint uVar6;
  uchar uVar7;
  uint uVar8;
  uint local_2c;
  F33CanTpFrameInfo FStack_28;
  
  uVar8 = state->remaining_length;
  uVar6 = (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22b98u + (uint32_t)(connection->addressing_format) * 1u)))) + 1 & 0xff;
  uVar5 = (byte)frame->length - uVar6 & 0xff;
  pFVar2 = connection;
  pFVar3 = state;
  FStack_28.length = uVar8 & 0xff;
  if (uVar5 < uVar8) {
    uVar7 = state->block_remaining;
    state->expected_sequence_number =
         ((uint8_t *)camry_host_ptr((uint32_t)(frame->data)))[(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22b98u + (uint32_t)(connection->addressing_format) * 1u))))] + 1 & 0xf;
    if (uVar7 != '\0') {
      uVar7 = uVar7 + 0xff;
    }
    iVar4 = FUN_0007a862(connection);
    if ((iVar4 == 0) || (uVar7 != '\0')) {
      extraout_r8->state = 'K';
      uVar1 = extraout_r6->consecutive_receive_timeout_raw + 2;
    }
    else {
      extraout_r8->state = 'i';
      uVar1 = extraout_r6->buffer_wait_timeout_raw;
      extraout_r8->flow_status_marker = 0xe1;
      uVar1 = uVar1 - 3;
    }
    extraout_r8->timeout_ticks = uVar1;
    extraout_r8->block_remaining = uVar7;
    pFVar2 = extraout_r6;
    pFVar3 = extraout_r8;
    FStack_28.length = uVar5;
  }
  FStack_28.data = frame->data;
  uVar8 = uVar8 - FStack_28.length;
  uVar1 = pFVar2->upper_receive_id;
  pFVar3->remaining_length = uVar8;
  local_2c = 0;
  FStack_28.data = FStack_28.data + uVar6;
  uVar5 = f33_cantp_copy_upper_receive_bytes(uVar1,&FStack_28,&local_2c);
  uVar7 = '\x01';
  if ((uVar5 != 0) || (uVar7 = '\0', uVar8 == 0)) {
    f33_cantp_finish_receive_aggregate(connection,state,uVar7);
  }
  return;
}



/* Accept matching RxID in4B or early5A/F0, validate extent/sequence and append payload. Early CF
   may consume a CTS before its lower confirmation; exact cancel hook is no-op. */

void f33_cantp_handle_consecutive_receive(F33CanTpRxConnection *connection,F33CanTpFrameInfo *frame)

{
  uchar uVar1;
  uint uVar2;
  uint uVar3;
  
  uVar2 = (uint)connection->channel_state_index;
  uVar1 = ((volatile F33CanTpRxState *)camry_host_ptr(0xfebe4f50u))[uVar2 * 2].state;
  if ((((uVar1 == 'Z') && (((volatile F33CanTpRxState *)camry_host_ptr(0xfebe4f50u))[uVar2 * 2].flow_status_marker == 0xf0)) ||
      (uVar1 == 'K')) &&
     ((connection->receive_id == ((volatile F33CanTpRxState *)camry_host_ptr(0xfebe4f50u))[uVar2 * 2].receive_id &&
      (uVar3 = f33_cantp_reject_consecutive_frame
                         (connection, frame, ((F33CanTpRxState *)camry_host_ptr((uint32_t)((0xfebe4f50u) + uVar2 * 2)))), uVar3 == 0)))) {
    if (uVar1 != 'K') {
      ((void)(connection->canif_fc_transmit_id), f33_return_only_stub_7b246());
    }
    f33_cantp_append_consecutive_receive(connection, frame, ((F33CanTpRxState *)camry_host_ptr((uint32_t)((0xfebe4f50u) + uVar2 * 2))));
  }
  return;
}



/* CTS confirmation moves5A/F0 to4B with N_Cr+2; WAIT moves5A/E1 to69 with N_Br-3. Overflow5A/D2
   retires local state without inventing an upper receive claim. */

void f33_cantp_confirm_receive_flow_control(F33CanTpRxConnection *connection)

{
  uchar uVar1;
  uint uVar2;
  
  uVar2 = (uint)connection->channel_state_index;
  uVar1 = ((volatile F33CanTpRxState *)camry_host_ptr(0xfebe4f50u))[uVar2 * 2].state;
  if (uVar1 == 'K') {
    return;
  }
  if (uVar1 == 'Z') {
    uVar1 = ((volatile F33CanTpRxState *)camry_host_ptr(0xfebe4f50u))[uVar2 * 2].flow_status_marker;
    if (uVar1 == 0xf0) {
      ((volatile F33CanTpRxState *)camry_host_ptr(0xfebe4f50u))[uVar2 * 2].state = 'K';
      ((volatile F33CanTpRxState *)camry_host_ptr(0xfebe4f50u))[uVar2 * 2].timeout_ticks =
           connection->consecutive_receive_timeout_raw + 2;
      return;
    }
    if (uVar1 == 0xe1) {
      ((volatile F33CanTpRxState *)camry_host_ptr(0xfebe4f50u))[uVar2 * 2].state = 'i';
      ((volatile F33CanTpRxState *)camry_host_ptr(0xfebe4f50u))[uVar2 * 2].timeout_ticks = connection->buffer_wait_timeout_raw - 3;
      ((volatile F33CanTpRxState *)camry_host_ptr(0xfebe4f50u))[uVar2 * 2].flow_status_marker = 0xe1;
      return;
    }
    if (uVar1 == 0xd2) goto LAB_0007b1fc;
  }
  else if (uVar1 == 'i') {
    return;
  }
  DAT_febe4f3c = 0xf;
LAB_0007b1fc:
  f33_cantp_reset_receive_owner(((F33CanTpRxState *)camry_host_ptr((uint32_t)((0xfebe4f50u) + uVar2 * 2))));
  return;
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



/* Build F33PduInfo, run exact no-op81FFA then existing CanIf7FEF8 snapshot/enqueue.0 means software
   lower acceptance only; driver/controller and physical network remain separate. */

uint f33_cantp_submit_can_frame(ushort canif_id,F33CanTpFrameInfo *frame)

{
  int iVar1;
  uint uVar2;
  bool bVar3;
  F33PduInfo local_14;
  
  local_14.data = frame->data;
  local_14.length = (ushort)frame->length;
  iVar1 = ((void)(canif_id), (void)(&local_14), f33_return_const_0_81ffa());
  if (iVar1 == 0) {
    uVar2 = f33_canif_transmit(canif_id,&local_14);
    bVar3 = uVar2 == 0;
  }
  else {
    bVar3 = iVar1 == 1;
  }
  return (uint)!bVar3;
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



void FUN_0007b2c4(int *param_1)

{
  byte bVar1;
  byte bVar2;
  int iVar3;
  undefined8 uVar4;
  uint uVar5;
  ushort uVar6;
  uint uVar7;
  
  uVar4 = 0x23dfcfebeb800;
  uVar5 = (uint)DAT_00022c48;
  for (uVar7 = 0; uVar7 < uVar5; uVar7 = uVar7 + 1 & 0xff) {
    ((volatile F33CanTpTxStatePrefix *)camry_host_ptr(0xfebe4f40u))[uVar7 * 2].transmit_id = 0xffff;
    ((volatile F33CanTpTxStatePrefix *)camry_host_ptr(0xfebe4f40u))[uVar7 * 2].sequence_number = 0xff;
    ((volatile F33CanTpRxState *)camry_host_ptr(0xfebe4f50u))[uVar7 * 2].receive_id = 0xffff;
    ((volatile F33CanTpRxState *)camry_host_ptr(0xfebe4f50u))[uVar7 * 2].expected_sequence_number = 0xff;
    ((volatile F33CanTpTxStatePrefix *)camry_host_ptr(0xfebe4f40u))[uVar7 * 2].remaining_or_accepted_length = 0;
    ((volatile F33CanTpTxStatePrefix *)camry_host_ptr(0xfebe4f40u))[uVar7 * 2].timeout_ticks = 0;
    ((volatile F33CanTpTxStatePrefix *)camry_host_ptr(0xfebe4f40u))[uVar7 * 2].state = 0xe1;
    ((volatile F33CanTpTxStatePrefix *)camry_host_ptr(0xfebe4f40u))[uVar7 * 2].block_remaining = '\0';
    ((volatile F33CanTpTxStatePrefix *)camry_host_ptr(0xfebe4f40u))[uVar7 * 2].block_size = '\0';
    ((volatile F33CanTpTxStatePrefix *)camry_host_ptr(0xfebe4f40u))[uVar7 * 2].spacing_ticks = '\0';
    ((volatile F33CanTpTxStatePrefix *)camry_host_ptr(0xfebe4f40u))[uVar7 * 2].opaque_0d[0] = '\0';
    ((volatile F33CanTpTxStatePrefix *)camry_host_ptr(0xfebe4f40u))[uVar7 * 2].opaque_0d[1] = '\0';
    ((volatile F33CanTpTxStatePrefix *)camry_host_ptr(0xfebe4f40u))[uVar7 * 2].opaque_0d[2] = '\0';
    ((volatile F33CanTpRxState *)camry_host_ptr(0xfebe4f50u))[uVar7 * 2].remaining_length = 0;
    ((volatile F33CanTpRxState *)camry_host_ptr(0xfebe4f50u))[uVar7 * 2].timeout_ticks = 0;
    ((volatile F33CanTpRxState *)camry_host_ptr(0xfebe4f50u))[uVar7 * 2].wait_frame_count = 0;
    ((volatile F33CanTpRxState *)camry_host_ptr(0xfebe4f50u))[uVar7 * 2].state = 0xe1;
    ((volatile F33CanTpRxState *)camry_host_ptr(0xfebe4f50u))[uVar7 * 2].first_frame_dlc = '\0';
    ((volatile F33CanTpRxState *)camry_host_ptr(0xfebe4f50u))[uVar7 * 2].block_remaining = '\0';
    ((volatile F33CanTpRxState *)camry_host_ptr(0xfebe4f50u))[uVar7 * 2].flow_status_marker = 0xf0;
    ((volatile F33CanTpRxState *)camry_host_ptr(0xfebe4f50u))[uVar7 * 2].admission_generation = '\0';
  }
  uVar5 = (uint)DAT_00022c47;
  for (uVar7 = 0; uVar7 < uVar5; uVar7 = uVar7 + 1 & 0xff) {
    f33_cantp_rx_flow_parameters_with_complements[uVar7][0] = 0;
    f33_cantp_rx_flow_parameters_with_complements[uVar7][1] = 0;
  }
  bVar2 = *(byte *)(param_1 + 3);
  uVar6 = 0;
  while( true ) {
    iVar3 = (int)uVar4;
    uVar5 = 0;
    if (bVar2 <= uVar6) break;
    bVar1 = (*((byte *)camry_host_ptr((uint32_t)(*param_1 + (short)uVar6 * 0xc + 9))));
    for (uVar5 = 0; uVar5 < bVar1; uVar5 = uVar5 + 1 & 0xff) {
      iVar3 = uVar5 * 0x20 + (*((int *)camry_host_ptr((uint32_t)(*param_1 + (short)uVar6 * 0xc))));
      FUN_0007a84c(((byte *)camry_host_ptr((uint32_t)(iVar3))), (*((undefined1 *)camry_host_ptr((uint32_t)(iVar3 + 0x16)))));
      FUN_0007a89a(((byte *)camry_host_ptr((uint32_t)(iVar3))), (*((undefined1 *)camry_host_ptr((uint32_t)(iVar3 + 0x17)))));
    }
    uVar6 = uVar6 + 1 & 0xff;
  }
  do {
    (*((undefined1 *)camry_host_ptr((uint32_t)(uVar5 + iVar3 + -0x6904)))) = 0;
    uVar5 = uVar5 + 1;
  } while (uVar5 < 0x40);
  (*((undefined1 *)camry_host_ptr((uint32_t)(iVar3 + -0x68c4)))) = 0xf0;
  f33_return_only_stub_7b208();
  (*((undefined1 *)camry_host_ptr((uint32_t)(iVar3 + -0x68c3)))) = 0xaa;
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



/* Require1..4095, configured connection, idleE1 and half-duplex peer qualification. Store
   TxID,length and stateD2 in0x20-byte channel stride;0 means accepted length only, not copied or
   emitted. */

uint f33_cantp_accept_transmit_length
               (F33CanTpConfiguration *configuration,ushort transmit_id,uint length)

{
  byte bVar1;
  uint32_t puVar2;
  F33CanTpTxConnection *pFVar3;
  int iVar4;
  uint uVar5;
  
  puVar2 = 0xfebeb800u;
  uVar5 = 1;
  if ((length != 0) && (length <= DAT_00022c40)) {
    pFVar3 = f33_cantp_find_transmit_connection(configuration,transmit_id);
    iVar4 = FUN_0007b3b6(camry_host_addr(pFVar3), length);
    if ((iVar4 != 0x10) || (pFVar3->single_frame_only == '\0')) {
      bVar1 = pFVar3->channel_state_index;
      if ((((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)((uint)bVar1 * 0x20 + -0x68b8)))))) == -0x1f) &&
         ((((F33CanTpChannelConfiguration *)camry_host_ptr((uint32_t)(configuration->channel_rows)))[(short)(ushort)bVar1].half_duplex == '\0' ||
          ((((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)((uint)bVar1 * 0x20 + -0x68a6)))))) == -0x1f &&
           (((F33CanTpChannelConfiguration *)camry_host_ptr((uint32_t)(configuration->channel_rows)))[(short)(ushort)bVar1].half_duplex == '\x01')))))) {
        (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + (uint)bVar1 * 0x20 + -0x68bc)))) = transmit_id;
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)((uint)bVar1 * 0x20 + -0x68b8))))) = 0xd2;
        uVar5 = 0;
        (*((uint *)camry_host_ptr((uint32_t)(puVar2 + (uint)bVar1 * 0x20 + -0x68c0)))) = length;
      }
    }
  }
  return uVar5;
}



/* WARNING: This is an inlined function */
/* Clear remaining length, timeout, block fields and spacing, set TxIDFFFF/SNFF/stateE1. No lower
   queue drain or upper notification is implied by this reset alone. Exact leaf changes only R1/EP
   and flags; preserve R8 carrying the aggregate completion result through the real inline p-code.
    */

void f33_cantp_reset_transmit_owner(F33CanTpTxStatePrefix *state)

{
  state->transmit_id = 0xffff;
  state->remaining_or_accepted_length = 0;
  state->state = 0xe1;
  state->timeout_ticks = 0;
  state->sequence_number = 0xff;
  state->block_remaining = '\0';
  state->block_size = '\0';
  state->spacing_ticks = '\0';
  return;
}



void FUN_0007b46e(undefined2 param_1,undefined1 param_2)

{
  FUN_00081a4c(param_1,param_2);
  return;
}



/* WARNING: Inlined function: f33_cantp_reset_transmit_owner */
/* Require configured cancellation support and matching TxID. Refuse queued SF C3, final
   CF87/remaining0 and SF-sized D2; revoke segmented work, reset owner and report upper failure in
   allowed states. Lower cancel hook does not remove queued frames. */

uint f33_cantp_cancel_transmit_owner(F33CanTpConfiguration *configuration,ushort transmit_id)

{
  char cVar1;
  byte bVar2;
  uint32_t puVar3;
  F33CanTpTxConnection *pFVar4;
  int iVar5;
  uint uVar6;
  int *piVar7;
  
  puVar3 = 0xfebeb800u;
  uVar6 = 1;
  pFVar4 = f33_cantp_find_transmit_connection(configuration,transmit_id);
  if (pFVar4->cancel_supported != '\x01') {
    return 1;
  }
  bVar2 = pFVar4->channel_state_index;
  piVar7 = ((int *)camry_host_ptr((uint32_t)(puVar3 + (uint)bVar2 * 0x20 + -0x68c0)));
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)((uint)bVar2 * 0x20 + -0x68b8)))));
  if ((*((ushort *)camry_host_ptr((uint32_t)(puVar3 + (uint)bVar2 * 0x20 + -0x68bc)))) != transmit_id) {
    return 1;
  }
  if (cVar1 == 'x') {
LAB_0007b4ec:
    uVar6 = 0;
  }
  else {
    if (((int8_t)cVar1) == -0x79) {
      if (*piVar7 == 0) goto LAB_0007b4fc;
      goto LAB_0007b4ec;
    }
    if (((((int8_t)cVar1) == -0x6a) || (((int8_t)cVar1) == -0x5b)) || (((int8_t)cVar1) == -0x4c)) goto LAB_0007b4ec;
    if (((int8_t)cVar1) == -0x3d) goto LAB_0007b4fc;
    if (((int8_t)cVar1) == -0x2e) {
      iVar5 = FUN_0007b3b6(camry_host_addr(pFVar4), *piVar7);
      if (iVar5 != 0x10) goto LAB_0007b4fc;
      goto LAB_0007b4ec;
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x68c4))))) = 0xf;
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + (uint)bVar2 * 0x20 + -0x68bc)))) = 0xffff;
  *piVar7 = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)((uint)bVar2 * 0x20 + -0x68b8))))) = 0xe1;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + (uint)bVar2 * 0x20 + -0x68ba)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)((uint)bVar2 * 0x20 + -0x68b7))))) = 0xff;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)((uint)bVar2 * 0x20 + -0x68b6))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)((uint)bVar2 * 0x20 + -0x68b5))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)((uint)bVar2 * 0x20 + -0x68b4))))) = 0;
LAB_0007b4fc:
  if (uVar6 == 0) {
    if ((((int8_t)cVar1) == -0x4c) || (((int8_t)cVar1) == -0x79)) {
      ((void)(pFVar4->canif_frame_id), f33_return_only_stub_7b246());
    }
    FUN_0007b46e(pFVar4->upper_response_id,1);
  }
  return uVar6;
}



/* WARNING: This is an inlined function */
/* Mode+0C==4 writes connection+0E to frame[0]; modes2/3 use+1B; other modes leave frame unchanged.
   Exact leaf preserves R6 and R8 used by SF/FF construction; inline actual p-code, not a
   replacement. Transmit address prefix: mode+0C==4 copies+0E; modes2/3 copy+1B; others do not
   write. Exact7B524..7B53F changes onlyR1/EP and flags; preserves connectionR6 and FF extentR8.
   Real p-code inlining reconnects SF/FF construction without inventing extra outputs. Static
   instruction/dataflow proof; no separate native claim for alternative address modes. */

void f33_cantp_write_transmit_address_byte(F33CanTpTxConnection *connection,uchar *frame)

{
  uchar uVar1;
  
  uVar1 = connection->addressing_format;
  if (uVar1 == '\x04') {
    uVar1 = connection->address_byte;
  }
  else {
    if (uVar1 != '\x02' && uVar1 != '\x03') {
      return;
    }
    uVar1 = connection->extended_transmit_address_byte;
  }
  *frame = uVar1;
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



/* WARNING: Inlined function: f33_cantp_write_transmit_address_byte */
/* Obtain upper bytes into shared frame scratch, add SF PCI/padding and claim C3/countdownN_As+2
   before CanIf enqueue. Any upper copy refusal or lower enqueue refusal finishes aggregate with
   failure. */

void f33_cantp_build_and_queue_single_frame
               (F33CanTpTxConnection *connection,F33CanTpTxStatePrefix *state,uchar payload_length)

{
  uchar uVar1;
  ushort uVar2;
  uint32_t puVar3;
  undefined4 uVar4;
  uint uVar5;
  uint uVar6;
  uint uVar7;
  uint uVar8;
  uint local_28;
  F33CanTpFrameInfo FStack_24;
  
  puVar3 = 0x23dfcu;
  uVar6 = (uint)payload_length;
  uVar1 = connection->addressing_format;
  if (uVar1 == '\x04') {
    f33_cantp_shared_frame_scratch[0] = connection->address_byte;
  }
  else if (uVar1 == '\x02' || uVar1 == '\x03') {
    f33_cantp_shared_frame_scratch[0] = connection->extended_transmit_address_byte;
  }
  uVar8 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22b98u + (uint32_t)(connection->addressing_format) * 1u))));
  f33_cantp_shared_frame_scratch[uVar8] = payload_length;
  uVar7 = uVar8 + uVar6 + 1 & 0xff;
  uVar8 = uVar8 + 1 & 0xff;
  local_28 = 0;
  if (connection->pad_frames_to_eight == '\x01') {
    uVar7 = 8;
  }
  FStack_24.data = camry_host_addr(f33_cantp_shared_frame_scratch + uVar8);
  FStack_24.length = uVar6;
  uVar5 = f33_cantp_copy_upper_transmit_bytes(connection->upper_response_id,&FStack_24,&local_28);
  uVar4 = 0xd2;
  if (uVar5 == 0) {
    uVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x11b6)))));
    while (uVar8 = uVar8 + uVar6 & 0xff, uVar8 < uVar7) {
      f33_cantp_shared_frame_scratch[uVar8] = uVar1;
      uVar6 = 1;
    }
    FStack_24.data = camry_host_addr(f33_cantp_shared_frame_scratch);
    if (state->state == 0xd2) {
      state->state = 0xc3;
      uVar2 = connection->frame_confirmation_timeout_raw;
      state->remaining_or_accepted_length = 0;
      state->timeout_ticks = uVar2 + 2;
    }
    FStack_24.length = uVar7;
    uVar6 = f33_cantp_submit_can_frame(connection->canif_frame_id,&FStack_24);
    uVar4 = 0xc3;
    if (uVar6 == 0) {
      return;
    }
  }
  FUN_0007b572(camry_host_addr(connection), state, uVar4);
  return;
}



/* WARNING: Inlined function: f33_cantp_write_transmit_address_byte */
/* Encode12-bit FF extent, obtain first6 configured payload bytes, retain remaining and
   stateB4/SNFF/N_As+2, then queue8-byte frame. State ownership updates precede lower enqueue. */

void f33_cantp_build_and_queue_first_frame
               (F33CanTpTxConnection *connection,F33CanTpTxStatePrefix *state,uint total_length)

{
  uchar uVar1;
  byte bVar2;
  ushort uVar3;
  uint uVar4;
  undefined4 uVar5;
  uint uVar6;
  uint local_28;
  F33CanTpFrameInfo FStack_24;
  
  uVar1 = connection->addressing_format;
  if (uVar1 == '\x04') {
    f33_cantp_shared_frame_scratch[0] = connection->address_byte;
  }
  else if (uVar1 == '\x02' || uVar1 == '\x03') {
    f33_cantp_shared_frame_scratch[0] = connection->extended_transmit_address_byte;
  }
  uVar4 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22b98u + (uint32_t)(connection->addressing_format) * 1u))));
  f33_cantp_shared_frame_scratch[uVar4 + 1] = (uchar)total_length;
  f33_cantp_shared_frame_scratch[uVar4] = (byte)(total_length >> 8) | 0x10;
  bVar2 = connection->frame_capacity;
  uVar4 = uVar4 + 2 & 0xff;
  local_28 = 0;
  FStack_24.data = camry_host_addr(f33_cantp_shared_frame_scratch + uVar4);
  uVar6 = bVar2 - uVar4 & 0xff;
  FStack_24.length = uVar6;
  uVar4 = f33_cantp_copy_upper_transmit_bytes(connection->upper_response_id,&FStack_24,&local_28);
  uVar5 = 0xd2;
  if (uVar4 == 0) {
    FStack_24.data = camry_host_addr(f33_cantp_shared_frame_scratch);
    if (state->state == 0xd2) {
      state->state = 0xb4;
      uVar3 = connection->frame_confirmation_timeout_raw;
      state->remaining_or_accepted_length = total_length - uVar6;
      state->timeout_ticks = uVar3 + 2;
      state->sequence_number = 0xff;
    }
    FStack_24.length = (uint)bVar2;
    uVar4 = f33_cantp_submit_can_frame(connection->canif_frame_id,&FStack_24);
    uVar5 = 0xb4;
    if (uVar4 == 0) {
      return;
    }
  }
  FUN_0007b572(camry_host_addr(connection), state, uVar5);
  return;
}



/* WARNING: Inlined function: f33_cantp_reset_transmit_owner */

void FUN_0007b6f2(int param_1,undefined4 *param_2)

{
  char cVar1;
  
  cVar1 = *(char *)(param_2 + 2);
  if (((((int8_t)cVar1) == -0x3d) || (((int8_t)cVar1) == -0x4c)) || (((int8_t)cVar1) == -0x79)) {
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



/* WARNING: Inlined function: f33_cantp_write_transmit_address_byte */
/* Acquire up to7 configured bytes and build modulo16 CF; pad only final frame to8. Success consumes
   remaining and block allowance before enqueue in87/N_As+2. Upper busy2 preserves96 for retry;
   other copy/enqueue refusal reports aggregate failure. */

void f33_cantp_build_and_queue_consecutive_frame
               (F33CanTpTxConnection *connection,F33CanTpTxStatePrefix *state)

{
  byte bVar1;
  ushort uVar2;
  uchar uVar3;
  uint uVar4;
  uint32_t puVar5;
  undefined4 uVar6;
  uint uVar7;
  uint uVar8;
  uint uVar9;
  uint uVar10;
  byte bVar11;
  uint local_30;
  F33CanTpFrameInfo FStack_2c;
  
  puVar5 = 0x23dfcu;
  uVar3 = connection->addressing_format;
  if (uVar3 == '\x04') {
    f33_cantp_shared_frame_scratch[0] = connection->address_byte;
  }
  else if (uVar3 == '\x02' || uVar3 == '\x03') {
    f33_cantp_shared_frame_scratch[0] = connection->extended_transmit_address_byte;
  }
  bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22b98u + (uint32_t)(connection->addressing_format) * 1u))));
  if (state->sequence_number == 0xff) {
    bVar11 = 1;
  }
  else {
    bVar11 = state->sequence_number + 1 & 0xf;
  }
  f33_cantp_shared_frame_scratch[bVar1] = bVar11 | 0x20;
  uVar9 = (uint)connection->frame_capacity;
  uVar8 = state->remaining_or_accepted_length;
  uVar10 = bVar1 + 1 & 0xff;
  uVar4 = uVar9 - uVar10 & 0xff;
  if (uVar4 < uVar8) {
    uVar8 = uVar8 - uVar4;
  }
  else {
    uVar4 = uVar8 & 0xff;
    uVar8 = 0;
    uVar9 = uVar10 + uVar4 & 0xff;
    if (connection->pad_frames_to_eight == '\x01') {
      uVar9 = 8;
    }
  }
  FStack_2c.data = camry_host_addr(f33_cantp_shared_frame_scratch + uVar10);
  local_30 = 0;
  FStack_2c.length = uVar4;
  uVar7 = f33_cantp_copy_upper_transmit_bytes(connection->upper_response_id,&FStack_2c,&local_30);
  if (uVar7 == 0) {
    uVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x11b6)))));
    while (uVar10 = uVar10 + uVar4 & 0xff, uVar10 < uVar9) {
      f33_cantp_shared_frame_scratch[uVar10] = uVar3;
      uVar4 = 1;
    }
    FStack_2c.data = camry_host_addr(f33_cantp_shared_frame_scratch);
    if (state->state == 0x96) {
      state->state = 0x87;
      uVar2 = connection->frame_confirmation_timeout_raw;
      state->sequence_number = bVar11;
      state->remaining_or_accepted_length = uVar8;
      state->timeout_ticks = uVar2 + 2;
      uVar3 = state->block_remaining;
      if (uVar3 != '\0') {
        uVar3 = uVar3 + 0xff;
      }
      state->block_remaining = uVar3;
    }
    FStack_2c.length = uVar9;
    uVar8 = f33_cantp_submit_can_frame(connection->canif_frame_id,&FStack_2c);
    uVar6 = 0x87;
    if (uVar8 == 0) {
      return;
    }
  }
  else {
    uVar6 = 0x96;
    if (uVar7 == 2) {
      return;
    }
  }
  FUN_0007b572(camry_host_addr(connection), state, uVar6);
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



/* When spacing state78 expires, enter96 with max(N_Cs-(spacingTicks+3),0) countdown. The foreground
   then attempts actual upper copying; this is not a hardware send delay. */

void f33_cantp_open_consecutive_copy_window
               (F33CanTpTxConnection *connection,F33CanTpTxStatePrefix *state)

{
  ushort uVar1;
  ushort uVar2;
  
  uVar2 = 0;
  uVar1 = state->spacing_ticks + 3;
  if (uVar1 <= connection->consecutive_copy_timeout_raw) {
    uVar2 = connection->consecutive_copy_timeout_raw - uVar1;
  }
  if (state->state == 'x') {
    state->timeout_ticks = uVar2;
    state->state = 0x96;
  }
  return;
}



/* WARNING: Inlined function: f33_cantp_reset_transmit_owner */
/* Scheduled task resolves acceptedD2 to single/first-frame construction, obtains upper bytes,
   submits CanIf frame and advances segmented transport states. Timeout paths clear channel and
   report upper failure. */

void f33_cantp_run_transmit_channels(void)

{
  char cVar1;
  short sVar2;
  byte bVar3;
  undefined8 uVar4;
  F33CanTpTxConnection *connection;
  F33CanTpTxConnection *connection_00;
  F33CanTpTxStatePrefix *state;
  F33CanTpConfiguration *configuration;
  int iVar5;
  uint total_length;
  uint uVar6;
  F33CanTpTxConnection *unaff_r27;
  F33CanTpTxStatePrefix *state_00;
  
  uVar4 = 0xfebeb800;
  if ((((int8_t)DAT_febe4f3d) == -0x56) &&
     (configuration = (F33CanTpConfiguration *)FUN_0007a32e(),(uintptr_t)(configuration)!=(uintptr_t)((F33CanTpConfiguration *)0x0))) {
    bVar3 = configuration->channel_count;
    for (uVar6 = 0; uVar6 < bVar3; uVar6 = uVar6 + 1 & 0xff) {
      iVar5 = uVar6 * 0x20 + (int)uVar4;
      state_00 = ((F33CanTpTxStatePrefix *)camry_host_ptr((uint32_t)(iVar5 + -0x68c0)));
      cVar1 = (*((char *)camry_host_ptr((uint32_t)(iVar5 + -0x68b8))));
      total_length = state_00->remaining_or_accepted_length;
      sVar2 = (*((short *)camry_host_ptr((uint32_t)(iVar5 + -0x68ba))));
      if (((((cVar1 == 'x') || (((int8_t)cVar1) == -0x79)) || (((int8_t)cVar1) == -0x6a)) ||
          ((((int8_t)cVar1) == -0x5b || (((int8_t)cVar1) == -0x4c)))) || ((((int8_t)cVar1) == -0x3d || (((int8_t)cVar1) == -0x2e)))) {
        unaff_r27 = f33_cantp_find_transmit_connection(configuration,(*((ushort *)camry_host_ptr((uint32_t)(iVar5 + -0x68bc)))));
        if ((uintptr_t)(unaff_r27)!=(uintptr_t)((F33CanTpTxConnection *)0x0)) goto LAB_0007b916;
LAB_0007b908:
        (*((undefined1 *)camry_host_ptr((uint32_t)((int)uVar4 + -0x68c4)))) = 0xf;
        (*((undefined2 *)camry_host_ptr((uint32_t)(iVar5 + -0x68bc)))) = 0xffff;
        state_00->remaining_or_accepted_length = 0;
        (*((undefined1 *)camry_host_ptr((uint32_t)(iVar5 + -0x68b8)))) = 0xe1;
        (*((undefined2 *)camry_host_ptr((uint32_t)(iVar5 + -0x68ba)))) = 0;
        (*((undefined1 *)camry_host_ptr((uint32_t)(iVar5 + -0x68b7)))) = 0xff;
        (*((undefined1 *)camry_host_ptr((uint32_t)(iVar5 + -0x68b6)))) = 0;
        (*((undefined1 *)camry_host_ptr((uint32_t)(iVar5 + -0x68b5)))) = 0;
        (*((undefined1 *)camry_host_ptr((uint32_t)(iVar5 + -0x68b4)))) = 0;
      }
      else {
        if (((int8_t)cVar1) != -0x1f) goto LAB_0007b908;
LAB_0007b916:
        if (((int8_t)cVar1) != -0x1f) {
          if (((int8_t)cVar1) == -0x2e) {
            iVar5 = FUN_0007b3b6(camry_host_addr(unaff_r27), total_length);
            if (iVar5 == 0) {
              f33_cantp_build_and_queue_single_frame(connection,state_00,(uchar)total_length);
            }
            else {
              f33_cantp_build_and_queue_first_frame(connection,state_00,total_length);
            }
          }
          else if (((((int8_t)cVar1) == -0x3d) || (((int8_t)cVar1) == -0x4c)) || (((int8_t)cVar1) == -0x79)) {
            if (sVar2 == 0) {
              FUN_0007b6f2(camry_host_addr(unaff_r27), state_00);
            }
          }
          else if (((int8_t)cVar1) == -0x5b) {
            if (sVar2 == 0) {
              FUN_0007b72a(camry_host_addr(unaff_r27), state_00);
            }
          }
          else if (((int8_t)cVar1) == -0x6a) {
            f33_cantp_build_and_queue_consecutive_frame(unaff_r27,state_00);
            if (sVar2 == 0) {
              FUN_0007b848(camry_host_addr(unaff_r27), state_00);
            }
          }
          else if (sVar2 == 0) {
            f33_cantp_open_consecutive_copy_window(unaff_r27,state_00);
            f33_cantp_build_and_queue_consecutive_frame(connection_00,state);
          }
        }
      }
    }
  }
  return;
}



/* WARNING: Inlined function: f33_cantp_reset_transmit_owner */
/* Release aggregate Tx owner before forwarding supplied result through PduR to DCM. Intermediate
   lower confirmations must not call this until all remaining bytes have completed. */

void f33_cantp_finish_transmit_aggregate
               (F33CanTpTxConnection *connection,F33CanTpTxStatePrefix *state,uchar result)

{
  state->transmit_id = 0xffff;
  state->remaining_or_accepted_length = 0;
  state->state = 0xe1;
  state->timeout_ticks = 0;
  state->sequence_number = 0xff;
  state->block_remaining = '\0';
  state->block_size = '\0';
  state->spacing_ticks = '\0';
  FUN_0007b46e(connection->upper_response_id,result);
  return;
}



/* Require multiframe-capable connection, sufficient FC bytes and status0..2. Exact rows require
   length8 when frame is shorter than8; status>2 or short padded FC aborts aggregate, other short
   nonpadded forms may only be ignored. */

uint f33_cantp_reject_flow_control_frame
               (F33CanTpTxConnection *connection,F33CanTpFrameInfo *frame,
               F33CanTpTxStatePrefix *state)

{
  byte bVar1;
  uint uVar2;
  
  uVar2 = 1;
  if (connection->single_frame_only != '\0') {
    return 1;
  }
  if (frame->length < 8) {
    if (connection->require_padded_flow_control == '\x01') goto LAB_0007ba0c;
    if (frame->length < ((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22b98u + (uint32_t)(connection->addressing_format) * 1u)))) + 3 & 0xff)) {
      return 1;
    }
  }
  bVar1 = ((uint8_t *)camry_host_ptr((uint32_t)(frame->data)))[(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22b98u + (uint32_t)(connection->addressing_format) * 1u))))] & 0xf;
  uVar2 = (uint)(2 < bVar1);
  if (bVar1 < 3) {
    return uVar2;
  }
LAB_0007ba0c:
  f33_cantp_finish_transmit_aggregate(connection,state,(uchar)uVar2);
  return uVar2;
}



/* Only while SNFF, retain received BS and map STmin byte through exact256-entry22C84 table. Later
   CTS reloads retained BS and does not replace initial flow parameters. */

void f33_cantp_capture_initial_flow_parameters
               (F33CanTpTxStatePrefix *state,uchar block_size,uchar stmin_encoding)

{
  uchar uVar1;
  
  if (state->sequence_number == 0xff) {
    uVar1 = "\x01\x03\x03\x03\x03\x03\x04\x04\x04\x04\x04\x05\x05\x05\x05\x05\x06\x06\x06\x06\x06\a\a\a\a\a\b\b\b\b\b\t\t\t\t\t\n\n\n\n\n\v\v\v\v\v\f\f\f\f\f\r\r\r\r\r\x0e\x0e\x0e\x0e\x0e\x0f\x0f\x0f\x0f\x0f\x10\x10\x10\x10\x10\x11\x11\x11\x11\x11\x12\x12\x12\x12\x12\x13\x13\x13\x13\x13\x14\x14\x14\x14\x14\x15\x15\x15\x15\x15\x16\x16\x16\x16\x16\x17\x17\x17\x17\x17\x18\x18\x18\x18\x18\x19\x19\x19\x19\x19\x1a\x1a\x1a\x1a\x1a\x1b\x1b\x1b\x1b\x1b\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x03\x03\x03\x03\x03\x03\x03\x03\x03\x1c\x1c\x1c\x1c\x1c\x1c"
            [stmin_encoding];
    state->block_size = block_size;
    state->spacing_ticks = uVar1;
  }
  return;
}



/* CTS reloads block remaining and enters96/N_Cs-3; WAIT entersA5/N_Bs+2; OVERFLOW aborts aggregate.
   No received-WAIT counter is imposed on transmit work. */

void f33_cantp_apply_flow_control(F33CanTpTxConnection *connection,F33CanTpFrameInfo *frame)

{
  byte *pbVar1;
  uint uVar2;
  ushort uVar3;
  
  uVar2 = (uint)connection->channel_state_index;
  pbVar1 = ((void *)camry_host_ptr((uint32_t)(frame->data + (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22b98u + (uint32_t)(connection->addressing_format) * 1u)))))));
  if ((*pbVar1 & 0xf) == 0) {
    f33_cantp_capture_initial_flow_parameters
              (((F33CanTpTxStatePrefix *)camry_host_ptr((uint32_t)((0xfebe4f40u) + uVar2 * 2))), pbVar1[1], pbVar1[2]);
    ((volatile F33CanTpTxStatePrefix *)camry_host_ptr(0xfebe4f40u))[uVar2 * 2].block_remaining =
         ((volatile F33CanTpTxStatePrefix *)camry_host_ptr(0xfebe4f40u))[uVar2 * 2].block_size;
    ((volatile F33CanTpTxStatePrefix *)camry_host_ptr(0xfebe4f40u))[uVar2 * 2].state = 0x96;
    uVar3 = connection->consecutive_copy_timeout_raw - 3;
  }
  else {
    if ((*pbVar1 & 0xf) != 1) {
      f33_cantp_finish_transmit_aggregate
                (connection, ((F33CanTpTxStatePrefix *)camry_host_ptr((uint32_t)((0xfebe4f40u) + uVar2 * 2))), '\x01');
      return;
    }
    ((volatile F33CanTpTxStatePrefix *)camry_host_ptr(0xfebe4f40u))[uVar2 * 2].state = 0xa5;
    uVar3 = connection->flow_control_timeout_raw + 2;
  }
  ((volatile F33CanTpTxStatePrefix *)camry_host_ptr(0xfebe4f40u))[uVar2 * 2].timeout_ticks = uVar3;
  return;
}



/* Accept matching TxID whileB4/A5 or87 at a nonfinal exhausted nonzero block. Valid FC can advance
   an unconfirmed FF/CF; exact lower cancellation is no-op. Ignore FC outside those qualified
   ownership states. */

void f33_cantp_handle_flow_control(F33CanTpTxConnection *connection,F33CanTpFrameInfo *frame)

{
  uchar uVar1;
  uint uVar2;
  
  uVar2 = (uint)connection->channel_state_index;
  uVar1 = ((volatile F33CanTpTxStatePrefix *)camry_host_ptr(0xfebe4f40u))[uVar2 * 2].state;
  if ((((uVar1 == 0xb4) || (uVar1 == 0xa5)) ||
      ((uVar1 == 0x87 &&
       (((((volatile F33CanTpTxStatePrefix *)camry_host_ptr(0xfebe4f40u))[uVar2 * 2].block_remaining == '\0' &&
         (((volatile F33CanTpTxStatePrefix *)camry_host_ptr(0xfebe4f40u))[uVar2 * 2].block_size != '\0')) &&
        (((volatile F33CanTpTxStatePrefix *)camry_host_ptr(0xfebe4f40u))[uVar2 * 2].remaining_or_accepted_length != 0)))))) &&
     ((((volatile F33CanTpTxStatePrefix *)camry_host_ptr(0xfebe4f40u))[uVar2 * 2].transmit_id == connection->transmit_id &&
      (uVar2 = f33_cantp_reject_flow_control_frame
                         (connection, frame, ((F33CanTpTxStatePrefix *)camry_host_ptr((uint32_t)((0xfebe4f40u) + uVar2 * 2)))), uVar2 == 0))))
  {
    if (uVar1 != 0xa5) {
      ((void)(connection->canif_frame_id), f33_return_only_stub_7b246());
    }
    f33_cantp_apply_flow_control(connection,frame);
  }
  return;
}



/* WARNING: Inlined function: f33_cantp_reset_transmit_owner */
/* CanIf software confirmation advances single/multi-frame state. Only completed aggregate transport
   clears channel and reports upper result0; intermediate frames may wait for flow-control or
   spacing. */

void f33_cantp_handle_frame_confirmation(F33CanTpTxConnection *connection)

{
  uchar uVar1;
  uint uVar2;
  F33CanTpTxStatePrefix *state;
  
  uVar2 = (uint)connection->channel_state_index;
  uVar1 = ((volatile F33CanTpTxStatePrefix *)camry_host_ptr(0xfebe4f40u))[uVar2 * 2].state;
  state = ((void *)camry_host_ptr((uint32_t)((0xfebe4f40u) + uVar2 * 2)));
  if (uVar1 == 'x') {
    return;
  }
  if (uVar1 == 0x87) {
    if (state->remaining_or_accepted_length != 0) {
      if ((((volatile F33CanTpTxStatePrefix *)camry_host_ptr(0xfebe4f40u))[uVar2 * 2].block_remaining != '\0') ||
         (((volatile F33CanTpTxStatePrefix *)camry_host_ptr(0xfebe4f40u))[uVar2 * 2].block_size == '\0')) {
        ((volatile F33CanTpTxStatePrefix *)camry_host_ptr(0xfebe4f40u))[uVar2 * 2].state = 'x';
        ((volatile F33CanTpTxStatePrefix *)camry_host_ptr(0xfebe4f40u))[uVar2 * 2].timeout_ticks =
             (ushort)((volatile F33CanTpTxStatePrefix *)camry_host_ptr(0xfebe4f40u))[uVar2 * 2].spacing_ticks;
        return;
      }
      goto LAB_0007bb80;
    }
  }
  else {
    if (uVar1 == 0x96) {
      return;
    }
    if (uVar1 == 0xa5) {
      return;
    }
    if (uVar1 == 0xb4) {
LAB_0007bb80:
      ((volatile F33CanTpTxStatePrefix *)camry_host_ptr(0xfebe4f40u))[uVar2 * 2].state = 0xa5;
      ((volatile F33CanTpTxStatePrefix *)camry_host_ptr(0xfebe4f40u))[uVar2 * 2].timeout_ticks =
           connection->flow_control_timeout_raw + 2;
      return;
    }
    if (uVar1 != 0xc3) {
      if (uVar1 == 0xd2) {
        return;
      }
      DAT_febe4f3c = 0xf;
      ((volatile F33CanTpTxStatePrefix *)camry_host_ptr(0xfebe4f40u))[uVar2 * 2].transmit_id = 0xffff;
      state->remaining_or_accepted_length = 0;
      ((volatile F33CanTpTxStatePrefix *)camry_host_ptr(0xfebe4f40u))[uVar2 * 2].state = 0xe1;
      ((volatile F33CanTpTxStatePrefix *)camry_host_ptr(0xfebe4f40u))[uVar2 * 2].timeout_ticks = 0;
      ((volatile F33CanTpTxStatePrefix *)camry_host_ptr(0xfebe4f40u))[uVar2 * 2].sequence_number = 0xff;
      ((volatile F33CanTpTxStatePrefix *)camry_host_ptr(0xfebe4f40u))[uVar2 * 2].block_remaining = '\0';
      ((volatile F33CanTpTxStatePrefix *)camry_host_ptr(0xfebe4f40u))[uVar2 * 2].block_size = '\0';
      ((volatile F33CanTpTxStatePrefix *)camry_host_ptr(0xfebe4f40u))[uVar2 * 2].spacing_ticks = '\0';
      return;
    }
  }
  f33_cantp_finish_transmit_aggregate(connection,state,'\0');
  return;
}



byte FUN_0007bb9c(void)

{
  uint32_t puVar1;
  byte bVar2;
  
  puVar1 = 0xfebeb800u;
  bVar2 = FUN_0007be2e(DAT_00021866);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6853))))) = 0xff;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6854))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6852))))) = bVar2;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6851))))) = bVar2 ^ 0xff;
  return bVar2;
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



undefined4 FUN_0007bc12(byte param_1,byte param_2)

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
  return uVar2;
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



undefined4 FUN_0007bc56(uint param_1)

{
  undefined4 uVar1;
  
  param_1 = param_1 & 0xff;
  uVar1 = 0x11;
  if ((param_1 < DAT_00021865) && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x21869u + (uint32_t)(param_1) * 1u)))) != '\0')) {
    uVar1 = (*(int (*)())camry_indirect((uint32_t)(((code *)(uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x2186cu + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x21867u + (uint32_t)(param_1) * 1u))))) * 4u)))))))))))();
  }
  return uVar1;
}



undefined4 FUN_0007bc8a(uint param_1)

{
  undefined4 uVar1;
  
  param_1 = param_1 & 0xff;
  uVar1 = 0x11;
  if ((param_1 < DAT_00021865) && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x21869u + (uint32_t)(param_1) * 1u)))) != '\0')) {
    uVar1 = (*(int (*)())camry_indirect((uint32_t)(((code *)(uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x2186cu + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x21867u + (uint32_t)(param_1) * 1u))))) * 4u)))) + 4))))))))();
  }
  return uVar1;
}



undefined1 FUN_0007bcde(uint param_1)

{
  if ((param_1 & 0xff) < (uint)DAT_00021865) {
    return (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x21869u + (uint32_t)(param_1 & 0xff) * 1u))));
  }
  return 0;
}



void FUN_0007bcf4(byte param_1)

{
  if (param_1 < DAT_00021865) {
    FUN_0007e4ea((uint)(byte)param_1);
  }
  return;
}



void FUN_0007bd0a(byte param_1)

{
  if (param_1 < DAT_00021865) {
    FUN_0007e4fe((uint)(byte)param_1);
  }
  return;
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



void FUN_0007be58(undefined2 param_1,undefined4 param_2,undefined2 param_3)

{
  (*(int (*)())camry_indirect((uint32_t)(PTR_f33_dcm_start_of_reception_0002188c)))(param_1,param_2,param_3);
  return;
}



void FUN_0007be6c(undefined2 param_1)

{
  (*(int (*)())camry_indirect((uint32_t)(PTR_f33_dcm_copy_receive_data_00021890)))(param_1);
  return;
}



void FUN_0007be7e(undefined2 param_1)

{
  (*(int (*)())camry_indirect((uint32_t)(PTR_f33_dcm_copy_transmit_data_00021894)))(param_1);
  return;
}



void FUN_0007be90(undefined2 param_1,undefined1 param_2)

{
  (*(int (*)())camry_indirect((uint32_t)(PTR_f33_dcm_receive_indication_00021898)))(param_1,param_2);
  return;
}



void FUN_0007bea4(undefined2 param_1,undefined1 param_2)

{
  (*(int (*)())camry_indirect((uint32_t)(PTR_f33_dcm_transmit_confirmation_0002189c)))(param_1,param_2);
  return;
}



void FUN_0007beb8(undefined2 param_1)

{
  (*(int (*)())camry_indirect((uint32_t)(PTR_FUN_000218a0)))(param_1);
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



void FUN_0007bf60(void)

{
  char *pcVar1;
  byte bVar2;
  byte bVar3;
  uint32_t puVar4;
  uint32_t puVar5;
  uint uVar6;
  int iVar7;
  undefined4 uVar8;
  uint uVar9;
  uint uVar10;
  ushort uVar11;
  ushort uVar12;
  char cStack_27;
  undefined2 uStack_26;
  
  puVar4 = 0xfebeb800u;
  puVar5 = 0x23dfcu;
  uVar6 = FUN_0007bc42();
  bVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x25c0)))));
  bVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x25bf)))));
  for (uVar12 = 0; uVar12 < bVar2; uVar12 = uVar12 + 1 & 0xff) {
    uVar11 = bVar3 + uVar12 & 0xff;
    pcVar1 = ((undefined *)camry_host_ptr((uint32_t)(puVar4 + (short)uVar12 * 6 + -0x7a1c)));
    FUN_000831be(uVar11,uVar6,uVar6);
    iVar7 = FUN_0007e998(uVar11);
    uVar9 = 0;
    uVar10 = 0;
    if (iVar7 == 2 || iVar7 == 3) {
      uStack_26 = 0xff;
      cStack_27 = -1;
      ((void)(&uStack_26), (void)(&cStack_27), FUN_0007f316(uVar11));
      uVar9 = uVar6;
      if (cStack_27 != '\x03') {
        uVar9 = 0;
      }
      if (*pcVar1 == '\x0f') {
        uVar10 = FUN_0007eb62(uVar11);
        uVar10 = (uVar10 ^ 0xff) & uVar6;
      }
    }
    uVar8 = (*(int (*)())camry_indirect((uint32_t)(((code *)(uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar5 + -0x25cc))))))))(uVar12,uVar9);
    FUN_000831dc(uVar11,uVar8);
    FUN_000831f0(uVar11,uVar10);
    (*(int (*)())camry_indirect((uint32_t)(((code *)(uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar5 + -0x25d8))))))))(uVar12);
    FUN_0007bf10(uVar12,0);
  }
  return;
}


/* Scan configured channel Rx rows by+4 CanIf ID and optional address byte; return first matching
   row or null. Exact configuration uses normal addressing. */

F33CanTpRxConnection *
f33_cantp_find_receive_frame_connection
          (F33CanTpConfiguration *configuration,ushort canif_receive_id,uchar *frame_bytes)

{
  F33CanTpRxConnection *pFVar1;
  uchar uVar2;
  ushort uVar3;
  F33CanTpRxConnection *pFVar4;
  uint uVar5;
  
  pFVar4 = (F33CanTpRxConnection *)0x0;
  uVar3 = 0;
  do {
    if ((configuration->channel_count <= uVar3) || ((uintptr_t)(pFVar4)!=(uintptr_t)((F33CanTpRxConnection *)0x0))) {
      return pFVar4;
    }
    uVar5 = 0;
    while ((uVar5 < ((F33CanTpChannelConfiguration *)camry_host_ptr((uint32_t)(configuration->channel_rows)))[(short)uVar3].receive_count &&
           ((uintptr_t)(pFVar4)==(uintptr_t)((F33CanTpRxConnection *)0x0)))) {
      pFVar1 = ((F33CanTpRxConnection *)camry_host_ptr((uint32_t)(((F33CanTpChannelConfiguration *)camry_host_ptr((uint32_t)(configuration->channel_rows)))[(short)uVar3].receive_rows))) + uVar5;
      if (canif_receive_id == pFVar1->canif_receive_id) {
        if (1 < pFVar1->addressing_format) {
          if (pFVar1->addressing_format == 4) {
            uVar2 = pFVar1->receive_address_byte;
          }
          else {
            uVar2 = pFVar1->extended_flow_address_byte;
          }
          if (*frame_bytes != uVar2) goto LAB_0007a466;
        }
        pFVar4 = pFVar1;
      }
LAB_0007a466:
      uVar5 = uVar5 + 1 & 0xff;
    }
    uVar3 = uVar3 + 1 & 0xff;
  } while( true );
}


/* Scan configured Tx rows by+6 flow-control receive ID and optional address byte; return matching
   connection or null. */

F33CanTpTxConnection *
f33_cantp_find_flow_control_connection
          (F33CanTpConfiguration *configuration,ushort canif_receive_id,uchar *frame_bytes)

{
  F33CanTpTxConnection *pFVar1;
  uchar uVar2;
  ushort uVar3;
  F33CanTpTxConnection *pFVar4;
  uint uVar5;
  
  pFVar4 = (F33CanTpTxConnection *)0x0;
  uVar3 = 0;
  do {
    if ((configuration->channel_count <= uVar3) || ((uintptr_t)(pFVar4)!=(uintptr_t)((F33CanTpTxConnection *)0x0))) {
      return pFVar4;
    }
    uVar5 = 0;
    while ((uVar5 < ((F33CanTpChannelConfiguration *)camry_host_ptr((uint32_t)(configuration->channel_rows)))[(short)uVar3].transmit_count &&
           ((uintptr_t)(pFVar4)==(uintptr_t)((F33CanTpTxConnection *)0x0)))) {
      pFVar1 = ((F33CanTpTxConnection *)camry_host_ptr((uint32_t)(((F33CanTpChannelConfiguration *)camry_host_ptr((uint32_t)(configuration->channel_rows)))[(short)uVar3].transmit_rows))) + uVar5;
      if (canif_receive_id == pFVar1->flow_control_receive_id) {
        if (1 < pFVar1->addressing_format) {
          if (pFVar1->addressing_format == 4) {
            uVar2 = pFVar1->flow_control_address_byte;
          }
          else {
            uVar2 = pFVar1->extended_transmit_address_byte;
          }
          if (*frame_bytes != uVar2) goto LAB_0007a4ca;
        }
        pFVar4 = pFVar1;
      }
LAB_0007a4ca:
      uVar5 = uVar5 + 1 & 0xff;
    }
    uVar3 = uVar3 + 1 & 0xff;
  } while( true );
}


/* Find connection whose+4 confirmation ID matches and whose+2 TxID owns that channel. An unclaimed
   channel never receives aggregate transmit completion. */

F33CanTpTxConnection *
f33_cantp_find_active_transmit_confirmation
          (F33CanTpConfiguration *configuration,ushort canif_confirmation_id)

{
  F33CanTpTxConnection *pFVar1;
  F33CanTpTxConnection *pFVar2;
  uint uVar3;
  uint uVar4;
  
  uVar4 = 0;
  pFVar2 = (F33CanTpTxConnection *)0x0;
  while ((uVar4 < configuration->channel_count && ((uintptr_t)(pFVar2)==(uintptr_t)((F33CanTpTxConnection *)0x0)))) {
    pFVar1 = pFVar2;
    if (((volatile F33CanTpTxStatePrefix *)camry_host_ptr(0xfebe4f40u))[uVar4 * 2].transmit_id != 0xffff) {
      for (uVar3 = 0;
          (pFVar1 = pFVar2, uVar3 < ((F33CanTpChannelConfiguration *)camry_host_ptr((uint32_t)(configuration->channel_rows)))[(short)uVar4].transmit_count &&
          ((pFVar1 = ((F33CanTpTxConnection *)camry_host_ptr((uint32_t)(((F33CanTpChannelConfiguration *)camry_host_ptr((uint32_t)(configuration->channel_rows)))[(short)uVar4].transmit_rows))) + uVar3,
           canif_confirmation_id != pFVar1->canif_confirmation_id ||
           (((volatile F33CanTpTxStatePrefix *)camry_host_ptr(0xfebe4f40u))[uVar4 * 2].transmit_id != pFVar1->transmit_id))));
          uVar3 = uVar3 + 1 & 0xff) {
      }
    }
    uVar4 = uVar4 + 1 & 0xff;
    pFVar2 = pFVar1;
  }
  return pFVar2;
}


/* Find configured Rx FC-confirmation row matching+6 ID and the channel retained receive ID. */

F33CanTpRxConnection *
f33_cantp_find_active_receive_confirmation
          (F33CanTpConfiguration *configuration,ushort canif_confirmation_id)

{
  F33CanTpRxConnection *pFVar1;
  F33CanTpRxConnection *pFVar2;
  uint uVar3;
  uint uVar4;
  
  uVar4 = 0;
  pFVar2 = (F33CanTpRxConnection *)0x0;
  while ((uVar4 < configuration->channel_count && ((uintptr_t)(pFVar2)==(uintptr_t)((F33CanTpRxConnection *)0x0)))) {
    pFVar1 = pFVar2;
    if (((volatile F33CanTpRxState *)camry_host_ptr(0xfebe4f50u))[uVar4 * 2].receive_id != 0xffff) {
      for (uVar3 = 0;
          (pFVar1 = pFVar2, uVar3 < ((F33CanTpChannelConfiguration *)camry_host_ptr((uint32_t)(configuration->channel_rows)))[(short)uVar4].receive_count &&
          ((pFVar1 = ((F33CanTpRxConnection *)camry_host_ptr((uint32_t)(((F33CanTpChannelConfiguration *)camry_host_ptr((uint32_t)(configuration->channel_rows)))[(short)uVar4].receive_rows))) + uVar3,
           canif_confirmation_id != pFVar1->canif_fc_confirmation_id ||
           (((volatile F33CanTpRxState *)camry_host_ptr(0xfebe4f50u))[uVar4 * 2].receive_id != pFVar1->receive_id))));
          uVar3 = uVar3 + 1 & 0xff) {
      }
    }
    uVar4 = uVar4 + 1 & 0xff;
    pFVar2 = pFVar1;
  }
  return pFVar2;
}


/* Range-check namespaced receive ID0802..0804 and scan configured Rx rows by+2 ID; return matching
   pointer or null. */

F33CanTpRxConnection *
f33_cantp_find_receive_connection(F33CanTpConfiguration *configuration,ushort receive_id)

{
  uint uVar1;
  uint uVar2;
  F33CanTpRxConnection *pFVar3;
  F33CanTpRxConnection *pFVar4;
  ushort uVar5;
  
  uVar2 = (uint)receive_id;
  pFVar3 = (F33CanTpRxConnection *)0x0;
  if ((configuration->first_receive_id <= uVar2) &&
     ((int)(uVar2 - ((uint)configuration->receive_count + (uint)configuration->first_receive_id)) <
      0)) {
    uVar5 = 0;
    while ((uVar5 < configuration->channel_count && ((uintptr_t)(pFVar3)==(uintptr_t)((F33CanTpRxConnection *)0x0)))) {
      uVar1 = 0;
      while ((pFVar4 = pFVar3, uVar1 < ((F33CanTpChannelConfiguration *)camry_host_ptr((uint32_t)(configuration->channel_rows)))[(short)uVar5].receive_count &&
             (pFVar4 = ((F33CanTpRxConnection *)camry_host_ptr((uint32_t)(((F33CanTpChannelConfiguration *)camry_host_ptr((uint32_t)(configuration->channel_rows)))[(short)uVar5].receive_rows))) + uVar1,
             uVar2 != pFVar4->receive_id))) {
        uVar1 = uVar1 + 1 & 0xff;
      }
      uVar5 = uVar5 + 1 & 0xff;
      pFVar3 = pFVar4;
    }
  }
  return pFVar3;
}


/* Range-check namespaced ID then scan configured channel Tx rows by+2 ID; return matching pointer
   or null. Exact instructions preserve R10=0 until match. */

F33CanTpTxConnection *
f33_cantp_find_transmit_connection(F33CanTpConfiguration *configuration,ushort transmit_id)

{
  uint uVar1;
  uint uVar2;
  F33CanTpTxConnection *pFVar3;
  F33CanTpTxConnection *pFVar4;
  ushort uVar5;
  
  uVar2 = (uint)transmit_id;
  pFVar3 = (F33CanTpTxConnection *)0x0;
  if ((configuration->first_transmit_id <= uVar2) &&
     ((int)(uVar2 - ((uint)configuration->transmit_count + (uint)configuration->first_transmit_id))
      < 0)) {
    uVar5 = 0;
    while ((uVar5 < configuration->channel_count && ((uintptr_t)(pFVar3)==(uintptr_t)((F33CanTpTxConnection *)0x0)))) {
      uVar1 = 0;
      while ((pFVar4 = pFVar3, uVar1 < ((F33CanTpChannelConfiguration *)camry_host_ptr((uint32_t)(configuration->channel_rows)))[(short)uVar5].transmit_count &&
             (pFVar4 = ((F33CanTpTxConnection *)camry_host_ptr((uint32_t)(((F33CanTpChannelConfiguration *)camry_host_ptr((uint32_t)(configuration->channel_rows)))[(short)uVar5].transmit_rows))) + uVar1,
             uVar2 != pFVar4->transmit_id))) {
        uVar1 = uVar1 + 1 & 0xff;
      }
      uVar5 = uVar5 + 1 & 0xff;
      pFVar3 = pFVar4;
    }
  }
  return pFVar3;
}

