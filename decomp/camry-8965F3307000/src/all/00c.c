#include "common.h"


void FUN_00031ed0(uchar param_1)

{
  f33_publish_redundant_u8(param_1,((undefined *)camry_host_ptr(0xfebe6884u)),((undefined *)camry_host_ptr(0xfebe6880u)),((undefined *)camry_host_ptr(0xfebe6882u)));
  return;
}



void FUN_00031eea(uchar param_1)

{
  f33_publish_redundant_u8(param_1,((undefined *)camry_host_ptr(0xfebe6885u)),((undefined *)camry_host_ptr(0xfebe6881u)),((undefined *)camry_host_ptr(0xfebe6883u)));
  return;
}



void FUN_00031f04(void)

{
  FUN_00031ed0(0);
  FUN_00031eea(0);
  return;
}



void FUN_00031f18(void)

{
  DAT_febe6886 = 0;
  DAT_febe6888 = 0;
  FUN_00031ed0(0);
  FUN_00031eea(0);
  return;
}



void FUN_00031f36(void)

{
  ushort uVar1;
  uint32_t puVar2;
  int iVar3;
  uchar uStack_5;
  
  puVar2 = 0xfebeb800u;
  iVar3 = f33_vote_redundant_u8(((undefined *)camry_host_ptr(0xfebe6884u)),((undefined *)camry_host_ptr(0xfebe6880u)),((undefined *)camry_host_ptr(0xfebe6882u)),&uStack_5);
  uVar1 = (*((ushort *)camry_host_ptr((uint32_t)((int)(0xffffb086u + (uint32_t)((int)puVar2))))));
  if (iVar3 != 0) {
    if ((iVar3 != -0xb) && (iVar3 != -0xc)) {
      if (uVar1 <= DAT_0002bcfc) {
        uVar1 = uVar1 + 1;
      }
      goto LAB_00031f78;
    }
    FUN_00031ed0(uStack_5);
  }
  uVar1 = 0;
LAB_00031f78:
  (*((ushort *)camry_host_ptr((uint32_t)((int)(0xffffb086u + (uint32_t)((int)puVar2)))))) = uVar1;
  return;
}



void FUN_00031f80(void)

{
  ushort uVar1;
  uint32_t puVar2;
  int iVar3;
  uchar uStack_5;
  
  puVar2 = 0xfebeb800u;
  iVar3 = f33_vote_redundant_u8(((undefined *)camry_host_ptr(0xfebe6885u)),((undefined *)camry_host_ptr(0xfebe6881u)),((undefined *)camry_host_ptr(0xfebe6883u)),&uStack_5);
  uVar1 = (*((ushort *)camry_host_ptr((uint32_t)((int)(0xffffb088u + (uint32_t)((int)puVar2))))));
  if (iVar3 != 0) {
    if ((iVar3 != -0xb) && (iVar3 != -0xc)) {
      if (uVar1 <= DAT_0002bcfc) {
        uVar1 = uVar1 + 1;
      }
      goto LAB_00031fc2;
    }
    FUN_00031eea(uStack_5);
  }
  uVar1 = 0;
LAB_00031fc2:
  (*((ushort *)camry_host_ptr((uint32_t)((int)(0xffffb088u + (uint32_t)((int)puVar2)))))) = uVar1;
  return;
}



/* Use PUBLISHED E8CC family0200 and redundant6884/6885 readiness, with6764 channel bypassbits.
   Compute low8(E8CC+0x15), admit<0x23, pass that ID inr6 toFDFFC, then clearbothreadinessflags.
   Live/published generation skew may emit an older retainedphase request. */

void f33_request_published_mode200_phase(void)

{
  ushort uVar1;
  ushort uVar2;
  uint32_t puVar3;
  uVar2 = DAT_febee8cc;
  uVar1 = DAT_febe6764;
  puVar3 = 0xfebeb800u;
  if ((DAT_febee8cc & 0xff00) == 0x200) {
    FUN_00031f36();
    FUN_00031f80();
    if ((((((*((char *)camry_host_ptr((uint32_t)((int)(0xffffb084u + (uint32_t)((int)puVar3)))))) == 'Z') &&
          ((*((char *)camry_host_ptr((uint32_t)((int)0xffffb084u + (int)(puVar3 + 1))))) == 'Z')) ||
         (((uVar1 & 1) != 0 && ((*((char *)camry_host_ptr((uint32_t)((int)0xffffb084u + (int)(puVar3 + 1))))) == 'Z')))) ||
        (((uVar1 >> 1 & 1) != 0 && ((*((char *)camry_host_ptr((uint32_t)((int)(0xffffb084u + (uint32_t)((int)puVar3)))))) == 'Z')))) &&
       ((uVar2 + 0x15 & 0xff) < 0x23)) {
      thunk_FUN_000b15ac();
      FUN_00031ed0(0);
      FUN_00031eea(0);
    }
  }
  return;
}



void FUN_00032036(uint param_1)

{
  if ((param_1 & 0xff) - 0x15 < 0xe) {
    FUN_00031ed0(0x5a);
  }
  return;
}



void FUN_00032050(uint param_1)

{
  if ((param_1 & 0xff) - 0x15 < 0xe) {
    FUN_00031eea(0x5a);
  }
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_3206a(void)

{
  return;
}



/* Clear688C; map30E78 at constant input0 to set688E=15000 invocations. Initialize shutdown count0
   and limit15000 by actual30E78 map at constant input0; no wall-clock unit inferred. */

void f33_initialize_thermal_shutdown_counter(void)

{
  uint32_t puVar1;
  undefined2 uStack_6;
  
  puVar1 = 0xfebeb800u;
  FUN_0007025c(((undefined *)camry_host_ptr(0x30e78u)),0,&uStack_6);
  (*((undefined2 *)camry_host_ptr((uint32_t)((int)(0xffffb08cu + (uint32_t)((int)puVar1)))))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)((int)(0xffffb08eu + (uint32_t)((int)puVar1)))))) = uStack_6;
  return;
}



/* Increment688C while below688E and previous6FB0!=A5; otherwise request event27. Schedulers call
   this before the current thermal qualification publication. Increment while count below limit and
   previous6FB0!=A5; Scheduler consumes prior qualification before current model work. */

void f33_step_thermal_shutdown_request(void)

{
  if ((f33_thermal_shutdown_count < f33_thermal_shutdown_count_limit) &&
     (f33_thermal_history_qualification[0] != 0xa5)) {
    f33_thermal_shutdown_count = f33_thermal_shutdown_count + 1;
  }
  else {
    ((void)(0x27), thunk_FUN_000b15ac());
  }
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_320be(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_320c0(void)

{
  return;
}



void FUN_000320c2(void)

{
  uint uVar1;
  uint uVar2;
  
  if ((DAT_febe6890 == '\0') && (DAT_febe68b4 != -1)) {
    uVar2 = 0;
    do {
      uVar1 = uVar2 + 1;
      (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe689au + (uint32_t)(uVar2) * 2u)))) = *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe68aau)) + uVar2 * 2);
      (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe68a0u + (uint32_t)(uVar2) * 2u)))) = *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe68b0u)) + uVar2 * 2);
      uVar2 = uVar1;
    } while (uVar1 < 2);
    DAT_febe6890 = 'Z';
  }
  return;
}



void FUN_000320fe(uint param_1,undefined2 param_2)

{
  (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe689au + (uint32_t)(param_1 & 0xff) * 2u)))) = param_2;
  return;
}



/* Only while6899==0: report event12E with capture kind10, retain slot23, merge action kind1, mark
   current and latch6899=5A. Diagnostic admission failure does not suppress the fault record or
   cause a later retry. Exact event maps to packed45D604/C05D604. One-shot6899 monitor reports
   event12E then retains/merges/selects control-fault slot23 even when diagnostic lifecycle rejects
   reporting. Preserve both stride tails. Event joins packed45D604/C05D604; not a physical fault
   observation. */

void f33_publish_record_coherence_fault(void)

{
  char cVar1;
  uint32_t puVar2;
  puVar2 = 0xfebeb800u;
  cVar1 = DAT_febe6899;
  if (DAT_febe6899 == '\0') {
    puVar2 = 0xfebeb800u;
    f33_report_diagnostic_event_failure(0x12e,10);
    f33_retain_and_clear_fault_record(0x17);
    f33_encode_fault_action_kind('\x17','\x01');
    f33_select_current_fault_record(0x17);
    cVar1 = 'Z';
  }
  (*((char *)camry_host_ptr((uint32_t)((int)0xffffb098u + (int)(puVar2 + 1))))) = cVar1;
  return;
}



void FUN_00032146(uint param_1,undefined2 param_2)

{
  (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe68a0u + (uint32_t)(param_1 & 0xff) * 2u)))) = param_2;
  return;
}



void FUN_00032152(uint param_1)

{
  short sVar1;
  short sVar2;
  short sVar3;
  char cVar4;
  int iVar5;
  char cVar6;
  char cVar7;
  char cVar8;
  char cVar9;
  
  iVar5 = DAT_febe68b4;
  param_1 = param_1 & 0xff;
  cVar8 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe6891u + (uint32_t)(param_1) * 1u))));
  cVar9 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe6893u + (uint32_t)(param_1) * 1u))));
  cVar7 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe6895u + (uint32_t)(param_1) * 1u))));
  cVar6 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe6897u + (uint32_t)(param_1) * 1u))));
  cVar4 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe68a7u + (uint32_t)(param_1) * 1u))));
  sVar1 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe689au + (uint32_t)(param_1) * 2u))));
  sVar2 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe68a0u + (uint32_t)(param_1) * 2u))));
  sVar3 = *(short *)(((undefined *)camry_host_ptr(0xfebe68b0u)) + param_1 * 2);
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe68a5u + (uint32_t)(param_1) * 1u)))) == '\0') {
    if ((int)sVar1 == (int)*(short *)(((undefined *)camry_host_ptr(0xfebe68aau)) + param_1 * 2)) {
      cVar8 = '\0';
      cVar7 = '\0';
    }
    else {
      cVar7 = 'Z';
      if (DAT_febe68b4 == -0x5aa5a55b) {
        FUN_000320fe(param_1,(int)sVar2);
        cVar8 = cVar7;
      }
      else {
        f33_publish_record_coherence_fault();
      }
    }
  }
  if (cVar4 == '\0') {
    if (iVar5 == -0x5aa5a55b) {
      if ((int)sVar2 == (int)sVar3) {
        cVar9 = '\0';
        cVar6 = '\0';
        goto LAB_00032226;
      }
      FUN_00032146(param_1,(int)sVar1);
      cVar9 = 'Z';
      cVar6 = cVar9;
    }
    else {
      cVar9 = '\0';
    }
  }
  if ((cVar8 == 'Z') && (cVar9 == 'Z')) {
    f33_publish_record_coherence_fault();
  }
LAB_00032226:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe6891u + (uint32_t)(param_1) * 1u)))) = cVar8;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe6893u + (uint32_t)(param_1) * 1u)))) = cVar9;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe6895u + (uint32_t)(param_1) * 1u)))) = cVar7;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe6897u + (uint32_t)(param_1) * 1u)))) = cVar6;
  return;
}



void FUN_00032240(void)

{
  int iVar1;
  
  iVar1 = DAT_febe68b4;
  if ((DAT_febe8a18 == 'Z') && (FUN_000320c2(), iVar1 != -1)) {
    FUN_00032152(0);
    FUN_00032152(1);
  }
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_3226a(void)

{
  return;
}



/* Far-call trampoline: prepare {lp},0 / jarl 0x32398 / dispose 0,{lp},lp; byte-verified against the
   exact image. Forwards with registers and stack unchanged; marked as a thunk. Forwarding shape
   machine-verified; target semantics not recovered. */

void thunk_FUN_00032398(void)

{
  FUN_00032398();
  return;
}



void FUN_000324d6(int param_1)

{
  if ((DAT_febe68b4 != 0x5aa5a55a) && (param_1 == 0x5aa5a55a)) {
    f33_report_diagnostic_event_failure(0x123,0x32);
  }
  return;
}



void FUN_00032580(void)

{
  FUN_000324fc(0);
  FUN_000324fc(1);
  return;
}



/* Selector0 copies both raw halfwords to68AA/AC, writes software markerA55A5AA5, returns0; other
   selector returns-6. Existing32454 record projection can independently replace these slots; no
   calibration durability claim. */

int f33_stage_pair_correction(uchar selector,short *values)

{
  short *psVar1;
  int iVar2;
  uint uVar3;
  
  uVar3 = 0;
  if (selector == '\0') {
    do {
      iVar2 = uVar3 * 2;
      psVar1 = values + uVar3;
      uVar3 = uVar3 + 1 & 0xff;
      *(short *)(((undefined *)camry_host_ptr(0xfebe68aau)) + iVar2) = *psVar1;
    } while (uVar3 < 2);
    DAT_febe68b4 = 0xa55a5aa5;
    return 0;
  }
  return -6;
}



/* Build marker+pair records and request setters0208/0209; ignore returns and write RAM
   markerA55A5AA5 immediately. Persistence/physical copy consensus remain existing NvM boundary. */

void f33_queue_pair_correction_records(void)

{
  uint uVar1;
  undefined2 uVar2;
  uint32_t puVar3;
  uint uVar4;
  uint local_14;
  undefined2 auStack_10 [2];
  uint uStack_c;
  undefined2 auStack_8 [2];
  
  puVar3 = 0xfebeb800u;
  uStack_c = 0xa55a5aa5;
  local_14 = 0xa55a5aa5;
  uVar4 = 0;
  do {
    uVar2 = *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe68aau)) + uVar4 * 2);
    uVar1 = uVar4 + 1;
    auStack_8[uVar4] = uVar2;
    auStack_10[uVar4] = uVar2;
    uVar4 = uVar1;
  } while (uVar1 < 2);
  f33_nvm_set_record(0x208,&uStack_c);
  f33_nvm_set_record(0x209,&local_14);
  (*((undefined4 *)camry_host_ptr((uint32_t)((int)(0xffffb0b4u + (uint32_t)((int)puVar3)))))) = 0xa55a5aa5;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_32620(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_32622(void)

{
  return;
}



void FUN_00032624(void)

{
  int iVar1;
  ushort uVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  ushort local_18 [4];
  undefined2 uStack_10;
  undefined2 uStack_e;
  ushort auStack_c [4];
  undefined2 uStack_4;
  undefined2 uStack_2;
  
  if (DAT_febeeba6 == 0x600) {
    auStack_c[0] = DAT_febe622c;
    auStack_c[1] = DAT_febe622e;
    auStack_c[2] = DAT_febe6230;
    auStack_c[3] = DAT_febe6232;
    uStack_4 = DAT_febe6234;
    uStack_2 = DAT_febe6236;
    local_18[0] = DAT_febe6238;
    local_18[1] = DAT_febe623a;
    local_18[2] = DAT_febe623c;
    local_18[3] = DAT_febe623e;
    uStack_10 = DAT_febe6240;
    uStack_e = DAT_febe6242;
    iVar3 = 0;
    if (DAT_febe68b8 < 0x7f) {
      do {
        iVar1 = iVar3 * 4;
        uVar2 = local_18[iVar3];
        iVar4 = iVar3 + 1;
        *(uint *)(((undefined *)camry_host_ptr(0xfebe68d4u)) + iVar1) = *(int *)(((undefined *)camry_host_ptr(0xfebe68d4u)) + iVar1) + (uint)auStack_c[iVar3];
        *(uint *)(((undefined *)camry_host_ptr(0xfebe68ecu)) + iVar1) = *(int *)(((undefined *)camry_host_ptr(0xfebe68ecu)) + iVar1) + (uint)uVar2;
        iVar1 = iVar3 + -5;
        iVar3 = iVar4;
      } while (((iVar1 < 0) || (iVar4 < 0)));
      DAT_febe68b8 = DAT_febe68b8 + 1;
      return;
    }
    do {
      iVar1 = iVar3 * 4;
      uVar2 = auStack_c[iVar3];
      iVar4 = *(int *)(((undefined *)camry_host_ptr(0xfebe68d4u)) + iVar1);
      *(undefined4 *)(((undefined *)camry_host_ptr(0xfebe68d4u)) + iVar1) = 0;
      uVar5 = iVar4 + (uint)uVar2 >> 7;
      if (0xffff < uVar5) {
        uVar5 = 0xffff;
      }
      *(short *)(((undefined *)camry_host_ptr(0xfebe68bau)) + iVar3 * 2) = (short)uVar5;
      uVar2 = local_18[iVar3];
      iVar4 = *(int *)(((undefined *)camry_host_ptr(0xfebe68ecu)) + iVar1);
      *(undefined4 *)(((undefined *)camry_host_ptr(0xfebe68ecu)) + iVar1) = 0;
      uVar5 = iVar4 + (uint)uVar2 >> 7;
      if (0xffff < uVar5) {
        uVar5 = 0xffff;
      }
      *(short *)(((undefined *)camry_host_ptr(0xfebe68c6u)) + iVar3 * 2) = (short)uVar5;
      iVar4 = iVar3 + 1;
      iVar1 = iVar3 + -5;
      iVar3 = iVar4;
    } while (((iVar1 < 0) || (iVar4 < 0)));
  }
  DAT_febe68b8 = 0;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_32720(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_32722(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_328d2(void)

{
  return;
}



/* WARNING: Inlined function: f33_reset_staged_monitor_current_coefficients */
/* Return original range-validation status0/5A. On5A reset staged coefficients through32A48, without
   converting the failed result into success. */

uint f33_validate_or_reset_staged_monitor_current_coefficients(void)

{
  uint32_t puVar1;
  uint uVar2;
  
  puVar1 = 0xfebeb800u;
  uVar2 = f33_validate_staged_monitor_current_coefficients();
  if (uVar2 == 0x5a) {
    (*((undefined2 *)camry_host_ptr((uint32_t)((int)(0xffffb12eu + (uint32_t)((int)puVar1)))))) = 0xbe36;
    (*((undefined2 *)camry_host_ptr((uint32_t)((int)(0xffffb130u + (uint32_t)((int)puVar1)))))) = 0xbe36;
    (*((undefined2 *)camry_host_ptr((uint32_t)((int)(0xffffb132u + (uint32_t)((int)puVar1)))))) = 0xbe36;
    (*((undefined2 *)camry_host_ptr((uint32_t)((int)(0xffffb134u + (uint32_t)((int)puVar1)))))) = 0xbe36;
    (*((undefined2 *)camry_host_ptr((uint32_t)((int)(0xffffb136u + (uint32_t)((int)puVar1)))))) = 0xbe36;
    (*((undefined2 *)camry_host_ptr((uint32_t)((int)(0xffffb138u + (uint32_t)((int)puVar1)))))) = 0xbe36;
    (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb13au + (uint32_t)((int)puVar1)))))) = 0xbe36;
    (*((undefined2 *)camry_host_ptr((uint32_t)((int)(0xffffb13cu + (uint32_t)((int)puVar1)))))) = 0xbe36;
    (*((undefined2 *)camry_host_ptr((uint32_t)((int)(0xffffb13eu + (uint32_t)((int)puVar1)))))) = 0xbe36;
    (*((undefined2 *)camry_host_ptr((uint32_t)((int)(0xffffb140u + (uint32_t)((int)puVar1)))))) = 0xbe36;
    (*((undefined2 *)camry_host_ptr((uint32_t)((int)(0xffffb142u + (uint32_t)((int)puVar1)))))) = 0xbe36;
    (*((undefined2 *)camry_host_ptr((uint32_t)((int)(0xffffb144u + (uint32_t)((int)puVar1)))))) = 0xbe36;
    (*((undefined2 *)camry_host_ptr((uint32_t)((int)(0xffffb146u + (uint32_t)((int)puVar1)))))) = 0;
    (*((undefined2 *)camry_host_ptr((uint32_t)((int)(0xffffb148u + (uint32_t)((int)puVar1)))))) = 0;
    (*((undefined2 *)camry_host_ptr((uint32_t)((int)(0xffffb14au + (uint32_t)((int)puVar1)))))) = 0;
    (*((undefined2 *)camry_host_ptr((uint32_t)((int)(0xffffb14cu + (uint32_t)((int)puVar1)))))) = 0;
    (*((undefined2 *)camry_host_ptr((uint32_t)((int)(0xffffb14eu + (uint32_t)((int)puVar1)))))) = 0;
    (*((undefined2 *)camry_host_ptr((uint32_t)((int)(0xffffb150u + (uint32_t)((int)puVar1)))))) = 0;
  }
  return uVar2;
}



/* Forward32972 range result inR10; no additional gate or transformation. */

uint f33_get_staged_monitor_current_range_status(void)

{
  uint uVar1;
  
  uVar1 = f33_validate_staged_monitor_current_coefficients();
  return uVar1;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_32c84(void)

{
  return;
}



void FUN_00032c86(void)

{
  DAT_febe6958 = 0;
  DAT_febe6959 = 0;
  DAT_febe695c = 0;
  DAT_febe695a = 0;
  return;
}



/* Far-call trampoline: prepare {lp},0 / jarl 0x32C86 / dispose 0,{lp},lp; byte-verified against the
   exact image. Forwards with registers and stack unchanged; marked as a thunk. Forwarding shape
   machine-verified; target semantics not recovered. */

void thunk_FUN_00032c86(void)

{
  FUN_00032c86();
  return;
}



/* When695A==5A, state0 requests6A5C and moves1; nonzero completion state starts
   request6959=5A/valueROM30EA8 and moves2; completion22/44 clears stimulus and moves3/4; next
   terminal pass clears695A. This is distinct from34028 worker active6A61. */

void f33_step_mode600_fit_request(void)

{
  char cVar1;
  uint32_t puVar2;
  undefined1 uVar3;
  undefined2 uVar4;
  undefined1 uVar5;
  
  uVar4 = DAT_febe695c;
  uVar5 = DAT_febe6959;
  puVar2 = 0xfebeb800u;
  if (DAT_febe695a == 'Z') {
    uVar3 = 0x5a;
    if (DAT_febe6958 == '\0') {
      puVar2 = 0xfebeb800u;
      f33_request_six_channel_fit();
      cVar1 = '\x01';
    }
    else {
      cVar1 = DAT_febe6958;
      if (DAT_febe6958 == '\x01') {
        if (DAT_febe6a5d != '\0') {
          uVar5 = 0x5a;
          uVar4 = DAT_00030ea8;
          cVar1 = '\x02';
        }
      }
      else if (DAT_febe6958 == '\x02') {
        if (DAT_febe6a5d == '\"') {
          uVar5 = 0;
          uVar4 = 0;
          cVar1 = '\x03';
        }
        else if (DAT_febe6a5d == 'D') {
          uVar5 = 0;
          uVar4 = 0;
          cVar1 = '\x04';
        }
      }
      else {
        uVar3 = 0;
      }
    }
    (*((char *)camry_host_ptr((uint32_t)((int)(0xffffb158u + (uint32_t)((int)puVar2)))))) = cVar1;
    (*((undefined1 *)camry_host_ptr((uint32_t)((int)0xffffb158u + (int)(puVar2 + 1))))) = uVar5;
    (*((undefined2 *)camry_host_ptr((uint32_t)((int)(0xffffb15cu + (uint32_t)((int)puVar2)))))) = uVar4;
    (*((undefined1 *)camry_host_ptr((uint32_t)((int)(0xffffb15au + (uint32_t)((int)puVar2)))))) = uVar3;
  }
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_32d22(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_32d24(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_33ab2(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_33ab4(void)

{
  return;
}



/* Only on8A18==5A: require6ABC markerA55A5AA5; compare27 halfwords against last publication.
   Unchanged skips validation; changed+valid retained bounds copies, invalid marker/bounds resets
   published arrays to defaults.6A24/25 retain comparison and validation statuses. */

void f33_step_retained_fit_coherence(void)

{
  uint32_t puVar1;
  uint uVar2;
  uint uVar3;
  
  puVar1 = 0xfebeb800u;
  if (DAT_febe8a18 != 'Z') {
    return;
  }
  uVar3 = (uint)DAT_febe6a24;
  uVar2 = (uint)DAT_febe6a25;
  if (DAT_febe6abc == -0x5aa5a55b) {
    puVar1 = 0xfebeb800u;
    uVar3 = f33_compare_retained_fit_coefficients();
    if (uVar3 != 0x5a) {
      uVar2 = 0;
      goto LAB_00033d24;
    }
    uVar2 = f33_check_fit_record_admission();
    if (uVar2 == 0) {
      f33_copy_retained_fit_coefficients();
      goto LAB_00033d24;
    }
  }
  f33_reset_published_fit_coefficients();
LAB_00033d24:
  (*((char *)camry_host_ptr((uint32_t)((int)(0xffffb224u + (uint32_t)((int)puVar1)))))) = (char)uVar3;
  (*((char *)camry_host_ptr((uint32_t)((int)0xffffb224u + (int)(puVar1 + 1))))) = (char)uVar2;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_33d30(void)

{
  return;
}



/* Paired constant publisher: DAT_febe6a5c = 0; and DAT_febe6a5d = 0;; shape-classified from the
   canonical corpus. Target cells not yet named. */

void FUN_00033d32(void)

{
  DAT_febe6a5c = 0;
  DAT_febe6a5d = 0;
  return;
}



/* Report event52/capture-kind50,then independently retain/clear slot17,encodekind1,select current.
   Called on terminal failure in33F14; diagnostic reporting inhibition does not veto the control
   action. */

void f33_publish_application_record_path_fault(void)

{
  f33_report_diagnostic_event_failure(0x52,0x32);
  f33_retain_and_clear_fault_record(0x11);
  f33_encode_fault_action_kind('\x11','\x01');
  f33_select_current_fault_record(0x11);
  return;
}



/* Active6A5C=5A starts worker then watches cached foreground6528.55 plus snapshot bounds stages0202
   and state22;66 or failed check reports existing52/slot17 and state44. Later22 responds0;44
   responds-9. Does not await physical NvM completion. */

void f33_step_fit_completion(void)

{
  undefined *puVar1;
  undefined *puVar2;
  uint uVar3;
  char cVar4;
  char cVar5;
  
  cVar4 = DAT_febe6a5d;
  cVar5 = DAT_febe6a5c;
  puVar2 = ((undefined *)camry_host_ptr(0xfebeb800u));
  if (DAT_febe6a5c == 'Z') {
    if (DAT_febe6a5d == '\0') {
      puVar2 = ((undefined *)camry_host_ptr(0xfebeb800u));
      f33_begin_six_channel_fit();
      cVar4 = '\x11';
    }
    else if (DAT_febe6a5d == '\x11') {
      if (DAT_febe6528 == 'U') {
        puVar2 = ((undefined *)camry_host_ptr(0xfebeb800u));
        uVar3 = f33_check_foreground_fit_bounds();
        puVar1 = puVar2;
        if (uVar3 == 0x5a) {
          f33_publish_fit_candidate_record();
          cVar4 = '\"';
          goto LAB_00033f90;
        }
      }
      else {
        puVar1 = ((undefined *)camry_host_ptr(0xfebeb800u));
        if (DAT_febe6528 != 'f') goto LAB_00033f90;
      }
      puVar2 = puVar1;
      f33_publish_application_record_path_fault();
      cVar4 = 'D';
    }
    else if (DAT_febe6a5d == '\"') {
      puVar2 = ((undefined *)camry_host_ptr(0xfebeb800u));
      FUN_00034ea4(0,0);
      cVar5 = '\0';
    }
    else {
      cVar5 = '\0';
      puVar2 = ((undefined *)camry_host_ptr(0xfebeb800u));
      if (DAT_febe6a5d != 'D') {
        puVar2 = ((undefined *)camry_host_ptr(0xfebeb800u));
        f33_publish_application_record_path_fault();
      }
      FUN_00034ea4(0,0xfffffff7);
    }
  }
LAB_00033f90:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb25cu + (uint32_t)((int)camry_host_addr(puVar2)) * 1u)))) = cVar5;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb25du + (uint32_t)((int)camry_host_addr(puVar2)) * 1u)))) = cVar4;
  return;
}



/* Set6A5C=5A and return0; retains6A5D. Only recovered direct caller32CA0; this helper alone does
   not guarantee a fresh run. */

uint f33_request_six_channel_fit(void)

{
  DAT_febe6a5c = 0x5a;
  return 0;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_33fa8(void)

{
  return;
}



/* Clear passed active/request/stimulus/hold/means, set state10; stage zero pair, respond-6, cancel
   worker. Does not clear sample count or accumulators. Last three pointer arguments at entry
   SP+0/+4/+8. */

void f33_abort_mode600_stimulus_fit
               (uchar *active,uchar *request_valid,short *stimulus,ushort *hold_count,
               short *positive_mean,short *negative_mean,uchar *state)

{
  short *psVar1;
  uint uVar2;
  short asStack_8 [2];
  
  *stimulus = 0;
  *hold_count = 0;
  *active = '\0';
  *request_valid = '\0';
  *positive_mean = 0;
  *negative_mean = 0;
  *state = '\x10';
  uVar2 = 0;
  do {
    psVar1 = asStack_8 + uVar2;
    uVar2 = uVar2 + 1;
    *psVar1 = 0;
  } while (uVar2 < 2);
  f33_stage_pair_correction('\0',asStack_8);
  FUN_00034ea4(0,0xfffffffa);
  f33_cancel_mode600_stimulus_fit();
  return;
}


