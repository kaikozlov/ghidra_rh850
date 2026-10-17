#include "common.h"


int FUN_00031ed0(uchar param_1)

{
  return f33_publish_redundant_u8(param_1,((undefined *)camry_host_ptr(0xfebe6884u)),((undefined *)camry_host_ptr(0xfebe6880u)),((undefined *)camry_host_ptr(0xfebe6882u)));
}



int FUN_00031eea(uchar param_1)

{
  return f33_publish_redundant_u8(param_1,((undefined *)camry_host_ptr(0xfebe6885u)),((undefined *)camry_host_ptr(0xfebe6881u)),((undefined *)camry_host_ptr(0xfebe6883u)));
}



int FUN_00031f04(void)

{
  FUN_00031ed0(0);
  return FUN_00031eea(0);
}



int FUN_00031f18(void)

{
  DAT_febe6886 = 0;
  DAT_febe6888 = 0;
  FUN_00031ed0(0);
  return FUN_00031eea(0);
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



void FUN_0003226c(char param_1)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  uint local_20;
  undefined4 uStack_1c;
  uint uStack_18;
  undefined4 uStack_14;
  
  uStack_18 = DAT_00021000;
  uStack_14 = DAT_00021004;
  local_20 = DAT_00021008;
  uStack_1c = DAT_0002100c;
  if (param_1 == '\0') {
    uVar2 = f33_nvm_get_record(0x208, camry_host_addr(&uStack_18));
    uVar3 = f33_nvm_get_record(0x209, camry_host_addr(&local_20));
  }
  else {
    if (param_1 == '\x11') {
      uVar2 = 0x208;
    }
    else {
      if (param_1 != '\"') goto LAB_0003230e;
      uVar2 = 0x209;
    }
    uVar2 = f33_nvm_get_record(uVar2, camry_host_addr(&uStack_18));
    uVar3 = 0x10;
  }
  if ((uVar2 == 0x10) && (uVar3 == 0x10)) {
    uVar2 = 0;
    do {
      iVar1 = uVar2 * 2;
      *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe68aau)) + iVar1) = (*((undefined2 *)((uint8_t *)&uStack_14 + (iVar1))));
      if (param_1 == '\0') {
        *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe68b0u)) + iVar1) = (*((undefined2 *)((uint8_t *)&uStack_1c + (iVar1))));
      }
      uVar2 = uVar2 + 1;
    } while (uVar2 < 2);
    return;
  }
LAB_0003230e:
  f33_publish_record_coherence_fault();
  return;
}



int FUN_00032316(void)

{
  uint uVar1;
  uint uVar2;
  int iVar3;
  uint local_1c;
  undefined4 uStack_18;
  uint uStack_14;
  undefined4 uStack_10;
  
  uStack_14 = DAT_00021010;
  uStack_10 = DAT_00021014;
  local_1c = DAT_00021018;
  uStack_18 = DAT_0002101c;
  uVar1 = f33_nvm_get_record(0x208, camry_host_addr(&local_1c));
  uVar2 = f33_nvm_get_record(0x209, camry_host_addr(&uStack_14));
  iVar3 = 0;
  if ((uVar1 == 0x10) && (uVar2 == 0x10)) {
    uVar1 = 0;
    do {
      if ((*((short *)((uint8_t *)&uStack_18 + (uVar1 * 2)))) != (*((short *)((uint8_t *)&uStack_10 + (uVar1 * 2))))) {
        iVar3 = 0x5a;
      }
      uVar1 = uVar1 + 1;
    } while (uVar1 < 2);
    if (iVar3 == 0) {
      FUN_0003226c(0);
    }
  }
  else {
    iVar3 = 0x5a;
  }
  return iVar3;
}



void FUN_00032398(void)

{
  uint32_t puVar1;
  uint uVar2;
  uint uVar3;
  int iVar4;
  undefined4 uVar5;
  undefined1 uVar6;
  uint local_1c [2];
  uint auStack_14 [2];
  
  puVar1 = 0xfebeb800u;
  uVar2 = f33_nvm_get_record(0x208, camry_host_addr(auStack_14));
  uVar3 = f33_nvm_get_record(0x209, camry_host_addr(local_1c));
  if ((uVar2 == 0x10) && (auStack_14[0] == 0xa55a5aa5)) {
    if ((uVar3 != 0x10) || (local_1c[0] != 0xa55a5aa5)) {
      uVar5 = 0x11;
LAB_00032412:
      FUN_0003226c(uVar5);
      uVar5 = 0x5aa5a55a;
      uVar6 = 0x22;
      f33_report_diagnostic_event_failure(0x123,0x32);
      goto LAB_0003243c;
    }
    iVar4 = FUN_00032316();
    if (iVar4 == 0) {
      uVar5 = 0xa55a5aa5;
      uVar6 = 0x44;
      f33_report_diagnostic_healthy_observed(0x123);
      f33_report_diagnostic_healthy_observed(0x12e);
      goto LAB_0003243c;
    }
  }
  else if ((uVar3 == 0x10) && (local_1c[0] == 0xa55a5aa5)) {
    uVar5 = 0x22;
    goto LAB_00032412;
  }
  uVar5 = 0x5aa5a55a;
  uVar6 = 0x22;
  f33_publish_record_coherence_fault();
LAB_0003243c:
  (*((undefined4 *)camry_host_ptr((uint32_t)((int)(0xffffb0b4u + (uint32_t)((int)puVar1)))))) = uVar5;
  (*((undefined1 *)camry_host_ptr((uint32_t)((int)(0xffffb0a4u + (uint32_t)((int)puVar1)))))) = uVar6;
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



/* Get selector0208 into an eight-byte stack record. Success10 selects halfword at
   record+4+2*low8(index); otherwise use FEBE66CE+2*index. Publish to FEBE68AA+2*index. No local
   index bound. Native index0 proves ROM source despite conflicting setter-like RAM; OEM meaning
   unnamed. */

uint f33_publish_family2_group8_halfword(uint index)

{
  int iVar1;
  undefined2 uVar2;
  uint32_t puVar3;
  uint uVar4;
  uint local_14;
  undefined4 uStack_10;
  
  puVar3 = 0xfebeb800u;
  local_14 = DAT_00021020;
  uStack_10 = DAT_00021024;
  uVar4 = f33_nvm_get_record(0x208, camry_host_addr(&local_14));
  iVar1 = (index & 0xff) * 2;
  if (uVar4 == 0x10) {
    uVar2 = (*((undefined2 *)((uint8_t *)&uStack_10 + (iVar1))));
  }
  else {
    uVar2 = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + iVar1 + -0x5132))));
  }
  *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe68aau)) + (index & 0xff) * 2) = uVar2;
  return uVar4;
}



uint FUN_0003249a(uint param_1)

{
  int iVar1;
  uint32_t puVar2;
  uint uVar3;
  uint local_14;
  undefined4 uStack_10;
  
  puVar2 = 0xfebeb800u;
  local_14 = DAT_00021028;
  uStack_10 = DAT_0002102c;
  uVar3 = f33_nvm_get_record(0x209, camry_host_addr(&local_14));
  if (uVar3 == 0x10) {
    iVar1 = (param_1 & 0xff) * 2;
    (*((undefined2 *)camry_host_ptr((uint32_t)((int)0xffffb0b0u + (int)(puVar2 + iVar1))))) =
         (*((undefined2 *)((uint8_t *)&uStack_10 + (iVar1))));
  }
  return uVar3;
}



void FUN_000324d6(int param_1)

{
  if ((DAT_febe68b4 != 0x5aa5a55a) && (param_1 == 0x5aa5a55a)) {
    f33_report_diagnostic_event_failure(0x123,0x32);
  }
  return;
}



void FUN_000324fc(uint param_1)

{
  char cVar1;
  uint32_t puVar2;
  int extraout_r10;
  int iVar3;
  undefined1 uVar4;
  undefined1 uVar5;
  undefined4 uVar6;
  
  puVar2 = 0xfebeb800u;
  param_1 = param_1 & 0xff;
  uVar5 = 0;
  uVar4 = 0;
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe66c2u + (uint32_t)(param_1) * 1u))));
  uVar6 = DAT_febe68b4;
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe66c0u + (uint32_t)(param_1) * 1u)))) == 'Z') {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe68a5u + (uint32_t)(param_1) * 1u)))) = 0x5a;
    puVar2 = 0xfebeb800u;
    f33_publish_family2_group8_halfword(param_1);
    uVar6 = 0x5aa5a55a;
    uVar5 = 0x5a;
    if (extraout_r10 == 0x10) {
      uVar6 = 0xa55a5aa5;
      uVar5 = 0;
    }
  }
  if (cVar1 == 'Z') {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe68a7u + (uint32_t)(param_1) * 1u)))) = 0x5a;
    iVar3 = FUN_0003249a(param_1);
    uVar6 = 0x5aa5a55a;
    uVar4 = 0x5a;
    if (iVar3 == 0x10) {
      uVar6 = 0xa55a5aa5;
      uVar4 = 0;
    }
  }
  FUN_000324d6(uVar6);
  (*((undefined4 *)camry_host_ptr((uint32_t)((int)(0xffffb0b4u + (uint32_t)((int)puVar2)))))) = uVar6;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe68a5u + (uint32_t)(param_1) * 1u)))) = uVar5;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe68a7u + (uint32_t)(param_1) * 1u)))) = uVar4;
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



/* Compare all18 active/staged signed halfwords; return5A iff any differ, else0. Comparison precedes
   range validation in32876. */

uint f33_monitor_current_coefficients_differ(void)

{
  uint uVar1;
  
  if (((((((f33_monitor_current_active_calibration.coefficients.negative_residual_gain[0] ==
            f33_monitor_current_staged_calibration.coefficients.negative_residual_gain[0]) &&
          (f33_monitor_current_active_calibration.coefficients.negative_residual_gain[1] ==
           f33_monitor_current_staged_calibration.coefficients.negative_residual_gain[1])) &&
         (f33_monitor_current_active_calibration.coefficients.negative_residual_gain[2] ==
          f33_monitor_current_staged_calibration.coefficients.negative_residual_gain[2])) &&
        ((f33_monitor_current_active_calibration.coefficients.negative_residual_gain[3] ==
          f33_monitor_current_staged_calibration.coefficients.negative_residual_gain[3] &&
         (f33_monitor_current_active_calibration.coefficients.negative_residual_gain[4] ==
          f33_monitor_current_staged_calibration.coefficients.negative_residual_gain[4])))) &&
       ((f33_monitor_current_active_calibration.coefficients.negative_residual_gain[5] ==
         f33_monitor_current_staged_calibration.coefficients.negative_residual_gain[5] &&
        ((f33_monitor_current_active_calibration.coefficients.nonnegative_residual_gain[0] ==
          f33_monitor_current_staged_calibration.coefficients.nonnegative_residual_gain[0] &&
         (f33_monitor_current_active_calibration.coefficients.nonnegative_residual_gain[1] ==
          f33_monitor_current_staged_calibration.coefficients.nonnegative_residual_gain[1])))))) &&
      (f33_monitor_current_active_calibration.coefficients.nonnegative_residual_gain[2] ==
       f33_monitor_current_staged_calibration.coefficients.nonnegative_residual_gain[2])) &&
     (((((f33_monitor_current_active_calibration.coefficients.nonnegative_residual_gain[3] ==
          f33_monitor_current_staged_calibration.coefficients.nonnegative_residual_gain[3] &&
         (f33_monitor_current_active_calibration.coefficients.nonnegative_residual_gain[4] ==
          f33_monitor_current_staged_calibration.coefficients.nonnegative_residual_gain[4])) &&
        (f33_monitor_current_active_calibration.coefficients.nonnegative_residual_gain[5] ==
         f33_monitor_current_staged_calibration.coefficients.nonnegative_residual_gain[5])) &&
       (((f33_monitor_current_active_calibration.coefficients.bias[0] ==
          f33_monitor_current_staged_calibration.coefficients.bias[0] &&
         (f33_monitor_current_active_calibration.coefficients.bias[1] ==
          f33_monitor_current_staged_calibration.coefficients.bias[1])) &&
        ((f33_monitor_current_active_calibration.coefficients.bias[2] ==
          f33_monitor_current_staged_calibration.coefficients.bias[2] &&
         ((f33_monitor_current_active_calibration.coefficients.bias[3] ==
           f33_monitor_current_staged_calibration.coefficients.bias[3] &&
          (f33_monitor_current_active_calibration.coefficients.bias[4] ==
           f33_monitor_current_staged_calibration.coefficients.bias[4])))))))) &&
      (f33_monitor_current_active_calibration.coefficients.bias[5] ==
       f33_monitor_current_staged_calibration.coefficients.bias[5])))) {
    uVar1 = 0;
  }
  else {
    uVar1 = 0x5a;
  }
  return uVar1;
}



/* Copy staged negative/nonnegative gain arrays and biases into active6906/6912/691E. Does not
   publish source marker or changed/error bytes. */

void f33_adopt_monitor_current_coefficients(void)

{
  f33_monitor_current_active_calibration.coefficients.negative_residual_gain[0] =
       f33_monitor_current_staged_calibration.coefficients.negative_residual_gain[0];
  f33_monitor_current_active_calibration.coefficients.negative_residual_gain[1] =
       f33_monitor_current_staged_calibration.coefficients.negative_residual_gain[1];
  f33_monitor_current_active_calibration.coefficients.negative_residual_gain[2] =
       f33_monitor_current_staged_calibration.coefficients.negative_residual_gain[2];
  f33_monitor_current_active_calibration.coefficients.negative_residual_gain[3] =
       f33_monitor_current_staged_calibration.coefficients.negative_residual_gain[3];
  f33_monitor_current_active_calibration.coefficients.negative_residual_gain[4] =
       f33_monitor_current_staged_calibration.coefficients.negative_residual_gain[4];
  f33_monitor_current_active_calibration.coefficients.negative_residual_gain[5] =
       f33_monitor_current_staged_calibration.coefficients.negative_residual_gain[5];
  f33_monitor_current_active_calibration.coefficients.nonnegative_residual_gain[0] =
       f33_monitor_current_staged_calibration.coefficients.nonnegative_residual_gain[0];
  f33_monitor_current_active_calibration.coefficients.nonnegative_residual_gain[1] =
       f33_monitor_current_staged_calibration.coefficients.nonnegative_residual_gain[1];
  f33_monitor_current_active_calibration.coefficients.nonnegative_residual_gain[2] =
       f33_monitor_current_staged_calibration.coefficients.nonnegative_residual_gain[2];
  f33_monitor_current_active_calibration.coefficients.nonnegative_residual_gain[3] =
       f33_monitor_current_staged_calibration.coefficients.nonnegative_residual_gain[3];
  f33_monitor_current_active_calibration.coefficients.nonnegative_residual_gain[4] =
       f33_monitor_current_staged_calibration.coefficients.nonnegative_residual_gain[4];
  f33_monitor_current_active_calibration.coefficients.nonnegative_residual_gain[5] =
       f33_monitor_current_staged_calibration.coefficients.nonnegative_residual_gain[5];
  f33_monitor_current_active_calibration.coefficients.bias[0] =
       f33_monitor_current_staged_calibration.coefficients.bias[0];
  f33_monitor_current_active_calibration.coefficients.bias[1] =
       f33_monitor_current_staged_calibration.coefficients.bias[1];
  f33_monitor_current_active_calibration.coefficients.bias[2] =
       f33_monitor_current_staged_calibration.coefficients.bias[2];
  f33_monitor_current_active_calibration.coefficients.bias[3] =
       f33_monitor_current_staged_calibration.coefficients.bias[3];
  f33_monitor_current_active_calibration.coefficients.bias[4] =
       f33_monitor_current_staged_calibration.coefficients.bias[4];
  f33_monitor_current_active_calibration.coefficients.bias[5] =
       f33_monitor_current_staged_calibration.coefficients.bias[5];
  return;
}



/* Set all12 active gains to signedBE36=-16842 and all six biases0. Does not clear6904/6905 status
   bytes. */

void f33_reset_active_monitor_current_coefficients(void)

{
  f33_monitor_current_active_calibration.coefficients.negative_residual_gain[0] = -0x41ca;
  f33_monitor_current_active_calibration.coefficients.negative_residual_gain[1] = -0x41ca;
  f33_monitor_current_active_calibration.coefficients.negative_residual_gain[2] = -0x41ca;
  f33_monitor_current_active_calibration.coefficients.negative_residual_gain[3] = -0x41ca;
  f33_monitor_current_active_calibration.coefficients.negative_residual_gain[4] = -0x41ca;
  f33_monitor_current_active_calibration.coefficients.negative_residual_gain[5] = -0x41ca;
  f33_monitor_current_active_calibration.coefficients.nonnegative_residual_gain[0] = -0x41ca;
  f33_monitor_current_active_calibration.coefficients.nonnegative_residual_gain[1] = -0x41ca;
  f33_monitor_current_active_calibration.coefficients.nonnegative_residual_gain[2] = -0x41ca;
  f33_monitor_current_active_calibration.coefficients.nonnegative_residual_gain[3] = -0x41ca;
  f33_monitor_current_active_calibration.coefficients.nonnegative_residual_gain[4] = -0x41ca;
  f33_monitor_current_active_calibration.coefficients.nonnegative_residual_gain[5] = -0x41ca;
  f33_monitor_current_active_calibration.coefficients.bias[0] = 0;
  f33_monitor_current_active_calibration.coefficients.bias[1] = 0;
  f33_monitor_current_active_calibration.coefficients.bias[2] = 0;
  f33_monitor_current_active_calibration.coefficients.bias[3] = 0;
  f33_monitor_current_active_calibration.coefficients.bias[4] = 0;
  f33_monitor_current_active_calibration.coefficients.bias[5] = 0;
  return;
}



/* Only8A18==5A acts. Valid6954=A55A5AA5 and busy692D=0: compare; equal skips validation and
   publishes statuses0/0; changed validates, adopts on0 or resets active defaults on5A. Invalid
   marker/busy resets active coefficients but retains previous changed/error bytes. Stage and source
   marker are not invalidated by range rejection. */

void f33_update_active_monitor_current_calibration(void)

{
  uint32_t puVar1;
  uint uVar2;
  uint uVar3;
  
  puVar1 = 0xfebeb800u;
  if (DAT_febe8a18 != 'Z') {
    return;
  }
  uVar3 = (uint)f33_monitor_current_active_calibration.changed;
  uVar2 = (uint)f33_monitor_current_active_calibration.range_error;
  if ((f33_monitor_current_staged_calibration.marker == 0xa55a5aa5) &&
     (f33_monitor_current_staged_calibration.busy == '\0')) {
    puVar1 = 0xfebeb800u;
    uVar3 = f33_monitor_current_coefficients_differ();
    if (uVar3 != 0x5a) {
      uVar2 = 0;
      goto LAB_000328c6;
    }
    uVar2 = f33_get_staged_monitor_current_range_status();
    if (uVar2 == 0) {
      f33_adopt_monitor_current_coefficients();
      goto LAB_000328c6;
    }
  }
  f33_reset_active_monitor_current_coefficients();
LAB_000328c6:
  (*((char *)camry_host_ptr((uint32_t)((int)(0xffffb104u + (uint32_t)((int)puVar1)))))) = (char)uVar3;
  (*((char *)camry_host_ptr((uint32_t)((int)0xffffb104u + (int)(puVar1 + 1))))) = (char)uVar2;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_328d2(void)

{
  return;
}



/* Makes its own40-byte family2 record0200 getter call, separate from caller marker read. Copy
   coefficients only on status10; serialized bank1 precedes bank0, while RAM arrays group both banks
   by sign/bias. Getter reads immutable ROMA000, not setter RAMF5D0; no atomic two-read claim. */

uint f33_copy_monitor_calibration_from_rom_record(void)

{
  uint *puVar1;
  uint32_t puVar2;
  uint uVar3;
  undefined4 uVar4;
  undefined4 *puVar5;
  uint local_30;
  undefined2 uStack_2c;
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
  undefined2 uStack_14;
  undefined2 uStack_12;
  undefined2 uStack_10;
  undefined2 uStack_e;
  undefined2 uStack_c;
  undefined2 uStack_a;
  
  puVar2 = 0xfebeb800u;
  puVar1 = &local_30;
  puVar5 = ((undefined *)camry_host_ptr(0x21030u));
  do {
    uVar4 = *puVar5;
    puVar5 = puVar5 + 1;
    *puVar1 = uVar4;
    puVar1 = puVar1 + 1;
  } while ((uintptr_t)(puVar5)!=(uintptr_t)(((undefined *)camry_host_ptr(0x21058u))));
  uVar3 = f33_nvm_get_record(0x200, camry_host_addr(&local_30));
  if (uVar3 == 0x10) {
    (*((undefined2 *)camry_host_ptr((uint32_t)((int)(0xffffb12eu + (uint32_t)((int)puVar2)))))) = uStack_1a;
    (*((undefined2 *)camry_host_ptr((uint32_t)((int)(0xffffb130u + (uint32_t)((int)puVar2)))))) = uStack_18;
    (*((undefined2 *)camry_host_ptr((uint32_t)((int)(0xffffb132u + (uint32_t)((int)puVar2)))))) = uStack_16;
    (*((undefined2 *)camry_host_ptr((uint32_t)((int)(0xffffb134u + (uint32_t)((int)puVar2)))))) = uStack_2c;
    (*((undefined2 *)camry_host_ptr((uint32_t)((int)(0xffffb136u + (uint32_t)((int)puVar2)))))) = uStack_2a;
    (*((undefined2 *)camry_host_ptr((uint32_t)((int)(0xffffb138u + (uint32_t)((int)puVar2)))))) = uStack_28;
    (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb13au + (uint32_t)((int)puVar2)))))) = uStack_14;
    (*((undefined2 *)camry_host_ptr((uint32_t)((int)(0xffffb13cu + (uint32_t)((int)puVar2)))))) = uStack_12;
    (*((undefined2 *)camry_host_ptr((uint32_t)((int)(0xffffb13eu + (uint32_t)((int)puVar2)))))) = uStack_10;
    (*((undefined2 *)camry_host_ptr((uint32_t)((int)(0xffffb140u + (uint32_t)((int)puVar2)))))) = uStack_26;
    (*((undefined2 *)camry_host_ptr((uint32_t)((int)(0xffffb142u + (uint32_t)((int)puVar2)))))) = uStack_24;
    (*((undefined2 *)camry_host_ptr((uint32_t)((int)(0xffffb144u + (uint32_t)((int)puVar2)))))) = uStack_22;
    (*((undefined2 *)camry_host_ptr((uint32_t)((int)(0xffffb146u + (uint32_t)((int)puVar2)))))) = uStack_e;
    (*((undefined2 *)camry_host_ptr((uint32_t)((int)(0xffffb148u + (uint32_t)((int)puVar2)))))) = uStack_c;
    (*((undefined2 *)camry_host_ptr((uint32_t)((int)(0xffffb14au + (uint32_t)((int)puVar2)))))) = uStack_a;
    (*((undefined2 *)camry_host_ptr((uint32_t)((int)(0xffffb14cu + (uint32_t)((int)puVar2)))))) = uStack_20;
    (*((undefined2 *)camry_host_ptr((uint32_t)((int)(0xffffb14eu + (uint32_t)((int)puVar2)))))) = uStack_1e;
    (*((undefined2 *)camry_host_ptr((uint32_t)((int)(0xffffb150u + (uint32_t)((int)puVar2)))))) = uStack_1c;
  }
  return uVar3;
}



/* Return0 iff all12 gains are inclusively[-20912,-14080] and all six biases
   inclusively[-1835,1835]; otherwise5A. Signed16 calibration bounds30EA0..30EA6; no state mutation.
    */

uint f33_validate_staged_monitor_current_coefficients(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  uint uVar7;
  int iVar8;
  int iVar9;
  int iVar10;
  int iVar11;
  int iVar12;
  int iVar13;
  int iVar14;
  int iVar15;
  int iVar16;
  int iVar17;
  int iVar18;
  int iVar19;
  int iVar20;
  int iVar21;
  
  iVar15 = (int)f33_monitor_current_staged_calibration.coefficients.negative_residual_gain[0];
  iVar14 = (int)f33_monitor_current_staged_calibration.coefficients.negative_residual_gain[1];
  iVar13 = (int)f33_monitor_current_staged_calibration.coefficients.negative_residual_gain[2];
  iVar12 = (int)f33_monitor_current_staged_calibration.coefficients.nonnegative_residual_gain[0];
  iVar11 = (int)f33_monitor_current_staged_calibration.coefficients.nonnegative_residual_gain[1];
  iVar10 = (int)f33_monitor_current_staged_calibration.coefficients.nonnegative_residual_gain[2];
  iVar5 = (int)f33_monitor_current_staged_calibration.coefficients.negative_residual_gain[3];
  iVar4 = (int)f33_monitor_current_staged_calibration.coefficients.negative_residual_gain[4];
  iVar3 = (int)f33_monitor_current_staged_calibration.coefficients.negative_residual_gain[5];
  iVar2 = (int)f33_monitor_current_staged_calibration.coefficients.nonnegative_residual_gain[3];
  iVar21 = (int)f33_monitor_current_staged_calibration.coefficients.nonnegative_residual_gain[4];
  iVar20 = (int)f33_monitor_current_staged_calibration.coefficients.nonnegative_residual_gain[5];
  iVar9 = (int)f33_monitor_current_staged_calibration.coefficients.bias[0];
  iVar8 = (int)f33_monitor_current_staged_calibration.coefficients.bias[1];
  iVar6 = (int)f33_monitor_current_staged_calibration.coefficients.bias[2];
  iVar19 = (int)f33_monitor_current_staged_calibration.coefficients.bias[3];
  iVar18 = (int)f33_monitor_current_staged_calibration.coefficients.bias[4];
  iVar17 = (int)f33_monitor_current_staged_calibration.coefficients.bias[5];
  iVar1 = (int)f33_monitor_current_gain_bias_bounds[0];
  if (((((((iVar15 - iVar1 < 0 == (iVar15 < 0 != iVar1 < 0 && iVar1 < 0 == iVar15 - iVar1 < 0) &&
            iVar15 != iVar1) ||
          (iVar16 = (int)f33_monitor_current_gain_bias_bounds[1],
          iVar15 - iVar16 < 0 != (iVar15 < 0 != iVar16 < 0 && iVar16 < 0 == iVar15 - iVar16 < 0)))
         || (iVar12 - iVar1 < 0 == (iVar12 < 0 != iVar1 < 0 && iVar1 < 0 == iVar12 - iVar1 < 0) &&
             iVar12 != iVar1)) ||
        ((iVar12 - iVar16 < 0 != (iVar12 < 0 != iVar16 < 0 && iVar16 < 0 == iVar12 - iVar16 < 0) ||
         (iVar14 - iVar1 < 0 == (iVar14 < 0 != iVar1 < 0 && iVar1 < 0 == iVar14 - iVar1 < 0) &&
          iVar14 != iVar1)))) ||
       ((iVar14 - iVar16 < 0 != (iVar14 < 0 != iVar16 < 0 && iVar16 < 0 == iVar14 - iVar16 < 0) ||
        ((iVar11 - iVar1 < 0 == (iVar11 < 0 != iVar1 < 0 && iVar1 < 0 == iVar11 - iVar1 < 0) &&
          iVar11 != iVar1 ||
         (iVar11 - iVar16 < 0 != (iVar11 < 0 != iVar16 < 0 && iVar16 < 0 == iVar11 - iVar16 < 0)))))
       )) || (iVar13 - iVar1 < 0 == (iVar13 < 0 != iVar1 < 0 && iVar1 < 0 == iVar13 - iVar1 < 0) &&
              iVar13 != iVar1)) ||
     ((((((iVar13 - iVar16 < 0 != (iVar13 < 0 != iVar16 < 0 && iVar16 < 0 == iVar13 - iVar16 < 0) ||
          (iVar10 - iVar1 < 0 == (iVar10 < 0 != iVar1 < 0 && iVar1 < 0 == iVar10 - iVar1 < 0) &&
           iVar10 != iVar1)) ||
         (iVar10 - iVar16 < 0 != (iVar10 < 0 != iVar16 < 0 && iVar16 < 0 == iVar10 - iVar16 < 0)))
        || (((iVar5 - iVar1 < 0 == (iVar5 < 0 != iVar1 < 0 && iVar1 < 0 == iVar5 - iVar1 < 0) &&
              iVar5 != iVar1 ||
             (iVar5 - iVar16 < 0 != (iVar5 < 0 != iVar16 < 0 && iVar16 < 0 == iVar5 - iVar16 < 0)))
            || ((iVar2 - iVar1 < 0 == (iVar2 < 0 != iVar1 < 0 && iVar1 < 0 == iVar2 - iVar1 < 0) &&
                 iVar2 != iVar1 ||
                ((iVar2 - iVar16 < 0 !=
                  (iVar2 < 0 != iVar16 < 0 && iVar16 < 0 == iVar2 - iVar16 < 0) ||
                 (iVar4 - iVar1 < 0 == (iVar4 < 0 != iVar1 < 0 && iVar1 < 0 == iVar4 - iVar1 < 0) &&
                  iVar4 != iVar1)))))))) ||
       ((((iVar4 - iVar16 < 0 != (iVar4 < 0 != iVar16 < 0 && iVar16 < 0 == iVar4 - iVar16 < 0) ||
          (((iVar21 - iVar1 < 0 == (iVar21 < 0 != iVar1 < 0 && iVar1 < 0 == iVar21 - iVar1 < 0) &&
             iVar21 != iVar1 ||
            (iVar21 - iVar16 < 0 != (iVar21 < 0 != iVar16 < 0 && iVar16 < 0 == iVar21 - iVar16 < 0))
            ) || (iVar3 - iVar1 < 0 == (iVar3 < 0 != iVar1 < 0 && iVar1 < 0 == iVar3 - iVar1 < 0) &&
                  iVar3 != iVar1)))) ||
         (((iVar3 - iVar16 < 0 != (iVar3 < 0 != iVar16 < 0 && iVar16 < 0 == iVar3 - iVar16 < 0) ||
           (iVar20 - iVar1 < 0 == (iVar20 < 0 != iVar1 < 0 && iVar1 < 0 == iVar20 - iVar1 < 0) &&
            iVar20 != iVar1)) ||
          (((iVar20 - iVar16 < 0 != (iVar20 < 0 != iVar16 < 0 && iVar16 < 0 == iVar20 - iVar16 < 0)
            || ((iVar1 = (int)f33_monitor_current_gain_bias_bounds[2],
                iVar9 - iVar1 < 0 == (iVar9 < 0 != iVar1 < 0 && iVar1 < 0 == iVar9 - iVar1 < 0) &&
                iVar9 != iVar1 ||
                (iVar2 = (int)f33_monitor_current_gain_bias_bounds[3],
                iVar9 - iVar2 < 0 != (iVar9 < 0 != iVar2 < 0 && iVar2 < 0 == iVar9 - iVar2 < 0)))))
           || (iVar8 - iVar1 < 0 == (iVar8 < 0 != iVar1 < 0 && iVar1 < 0 == iVar8 - iVar1 < 0) &&
               iVar8 != iVar1)))))) ||
        ((((iVar8 - iVar2 < 0 != (iVar8 < 0 != iVar2 < 0 && iVar2 < 0 == iVar8 - iVar2 < 0) ||
           (iVar6 - iVar1 < 0 == (iVar6 < 0 != iVar1 < 0 && iVar1 < 0 == iVar6 - iVar1 < 0) &&
            iVar6 != iVar1)) ||
          (iVar6 - iVar2 < 0 != (iVar6 < 0 != iVar2 < 0 && iVar2 < 0 == iVar6 - iVar2 < 0))) ||
         ((iVar19 - iVar1 < 0 == (iVar19 < 0 != iVar1 < 0 && iVar1 < 0 == iVar19 - iVar1 < 0) &&
           iVar19 != iVar1 ||
          (iVar19 - iVar2 < 0 != (iVar19 < 0 != iVar2 < 0 && iVar2 < 0 == iVar19 - iVar2 < 0))))))))
       ) || (((iVar18 - iVar1 < 0 == (iVar18 < 0 != iVar1 < 0 && iVar1 < 0 == iVar18 - iVar1 < 0) &&
               iVar18 != iVar1 ||
              ((iVar18 - iVar2 < 0 != (iVar18 < 0 != iVar2 < 0 && iVar2 < 0 == iVar18 - iVar2 < 0)
               || (iVar17 - iVar1 < 0 ==
                   (iVar17 < 0 != iVar1 < 0 && iVar1 < 0 == iVar17 - iVar1 < 0) && iVar17 != iVar1))
              )) || (iVar17 - iVar2 < 0 !=
                     (iVar17 < 0 != iVar2 < 0 && iVar2 < 0 == iVar17 - iVar2 < 0))))))) {
    uVar7 = 0x5a;
  }
  else {
    uVar7 = 0;
  }
  return uVar7;
}



/* WARNING: This is an inlined function */
/* Set staged12 gains to-16842 and six biases0. Exact leaf changesR1/EP and preservesR10, which32A76
   returns from preceding validation. Inline real p-code to preserve this ABI fact. */

void f33_reset_staged_monitor_current_coefficients(void)

{
  f33_monitor_current_staged_calibration.coefficients.negative_residual_gain[0] = -0x41ca;
  f33_monitor_current_staged_calibration.coefficients.negative_residual_gain[1] = -0x41ca;
  f33_monitor_current_staged_calibration.coefficients.negative_residual_gain[2] = -0x41ca;
  f33_monitor_current_staged_calibration.coefficients.negative_residual_gain[3] = -0x41ca;
  f33_monitor_current_staged_calibration.coefficients.negative_residual_gain[4] = -0x41ca;
  f33_monitor_current_staged_calibration.coefficients.negative_residual_gain[5] = -0x41ca;
  f33_monitor_current_staged_calibration.coefficients.nonnegative_residual_gain[0] = -0x41ca;
  f33_monitor_current_staged_calibration.coefficients.nonnegative_residual_gain[1] = -0x41ca;
  f33_monitor_current_staged_calibration.coefficients.nonnegative_residual_gain[2] = -0x41ca;
  f33_monitor_current_staged_calibration.coefficients.nonnegative_residual_gain[3] = -0x41ca;
  f33_monitor_current_staged_calibration.coefficients.nonnegative_residual_gain[4] = -0x41ca;
  f33_monitor_current_staged_calibration.coefficients.nonnegative_residual_gain[5] = -0x41ca;
  f33_monitor_current_staged_calibration.coefficients.bias[0] = 0;
  f33_monitor_current_staged_calibration.coefficients.bias[1] = 0;
  f33_monitor_current_staged_calibration.coefficients.bias[2] = 0;
  f33_monitor_current_staged_calibration.coefficients.bias[3] = 0;
  f33_monitor_current_staged_calibration.coefficients.bias[4] = 0;
  f33_monitor_current_staged_calibration.coefficients.bias[5] = 0;
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



/* First0200 getter must return10 with markerA55A5AA5;328D4 separately gets/copies coefficients,
   then validation may reset them. Success sets markerA55A5AA5/source44 and diagnostic0124 healthy;
   failure sets complementary marker5AA5A55A/source22 and event0124/failure32. No persistence or
   two-read atomicity claim. */

void f33_restore_monitor_current_calibration(void)

{
  uint32_t puVar1;
  uint uVar2;
  undefined4 uVar3;
  undefined1 uVar4;
  uint local_34 [10];
  
  puVar1 = 0xfebeb800u;
  uVar2 = f33_nvm_get_record(0x200, camry_host_addr(local_34));
  if ((uVar2 == 0x10) && (local_34[0] == 0xa55a5aa5)) {
    f33_copy_monitor_calibration_from_rom_record();
    uVar2 = f33_validate_or_reset_staged_monitor_current_coefficients();
    if (uVar2 == 0) {
      uVar3 = 0xa55a5aa5;
      uVar4 = 0x44;
      f33_report_diagnostic_healthy_observed(0x124);
      goto LAB_00032ae4;
    }
  }
  uVar3 = 0x5aa5a55a;
  uVar4 = 0x22;
  f33_report_diagnostic_event_failure(0x124,0x32);
LAB_00032ae4:
  (*((undefined4 *)camry_host_ptr((uint32_t)((int)(0xffffb154u + (uint32_t)((int)puVar1)))))) = uVar3;
  (*((undefined1 *)camry_host_ptr((uint32_t)((int)(0xffffb12cu + (uint32_t)((int)puVar1)))))) = uVar4;
  return;
}



/* First0200 getter checks status10/marker; second independent getter through328D4 copies
   coefficients;32A76 validates/resets stage. ReturnA55A5AA5 on success, complementary5AA5A55A on
   failure. Reads ROM, not the setter RAM mirror. */

uint f33_reload_monitor_current_calibration_marker(void)

{
  uint uVar1;
  uint local_2c [10];
  
  uVar1 = f33_nvm_get_record(0x200, camry_host_addr(local_2c));
  if ((uVar1 == 0x10) && (local_2c[0] == 0xa55a5aa5)) {
    f33_copy_monitor_calibration_from_rom_record();
    uVar1 = f33_validate_or_reset_staged_monitor_current_coefficients();
    if (uVar1 == 0) {
      return 0xa55a5aa5;
    }
  }
  return 0x5aa5a55a;
}



/* When6501==5A and source marker valid, set busy5A, reload via32AF0 and clear busy only on valid
   return; invalid return reports0124/failure32. Other admission states clear busy and retain
   marker. Active coefficients are adopted separately later. */

void f33_refresh_monitor_current_calibration(void)

{
  uint32_t puVar1;
  uint uVar2;
  undefined1 uVar3;
  
  puVar1 = 0xfebeb800u;
  uVar3 = 0;
  uVar2 = f33_monitor_current_staged_calibration.marker;
  if ((DAT_febe6501 == 'Z') && (f33_monitor_current_staged_calibration.marker == 0xa55a5aa5)) {
    uVar3 = 0x5a;
    f33_monitor_current_staged_calibration.busy = 'Z';
    puVar1 = 0xfebeb800u;
    uVar2 = f33_reload_monitor_current_calibration_marker();
    if (uVar2 == 0xa55a5aa5) {
      uVar3 = 0;
    }
    else {
      f33_report_diagnostic_event_failure(0x124,0x32);
    }
  }
  (*((uint *)camry_host_ptr((uint32_t)((int)(0xffffb154u + (uint32_t)((int)puVar1)))))) = uVar2;
  (*((undefined1 *)camry_host_ptr((uint32_t)((int)0xffffb12cu + (int)(puVar1 + 1))))) = uVar3;
  return;
}



/* Serialize bank1 then bank0 coefficients after valid record marker and call setter0200. Ignore
   setter admission result; unconditionally publish valid6954 afterward. This marker is neither
   setter acceptance nor durability, and later getter still reads ROMA000. */

void f33_submit_monitor_current_calibration_record(void)

{
  uint32_t puVar1;
  uint local_30;
  short sStack_2c;
  short sStack_2a;
  short sStack_28;
  short sStack_26;
  short sStack_24;
  short sStack_22;
  short sStack_20;
  short sStack_1e;
  short sStack_1c;
  short sStack_1a;
  short sStack_18;
  short sStack_16;
  short sStack_14;
  short sStack_12;
  short sStack_10;
  short sStack_e;
  short sStack_c;
  short sStack_a;
  
  puVar1 = 0xfebeb800u;
  local_30 = 0xa55a5aa5;
  sStack_1a = f33_monitor_current_staged_calibration.coefficients.negative_residual_gain[0];
  sStack_18 = f33_monitor_current_staged_calibration.coefficients.negative_residual_gain[1];
  sStack_16 = f33_monitor_current_staged_calibration.coefficients.negative_residual_gain[2];
  sStack_2c = f33_monitor_current_staged_calibration.coefficients.negative_residual_gain[3];
  sStack_2a = f33_monitor_current_staged_calibration.coefficients.negative_residual_gain[4];
  sStack_28 = f33_monitor_current_staged_calibration.coefficients.negative_residual_gain[5];
  sStack_14 = f33_monitor_current_staged_calibration.coefficients.nonnegative_residual_gain[0];
  sStack_12 = f33_monitor_current_staged_calibration.coefficients.nonnegative_residual_gain[1];
  sStack_10 = f33_monitor_current_staged_calibration.coefficients.nonnegative_residual_gain[2];
  sStack_26 = f33_monitor_current_staged_calibration.coefficients.nonnegative_residual_gain[3];
  sStack_24 = f33_monitor_current_staged_calibration.coefficients.nonnegative_residual_gain[4];
  sStack_22 = f33_monitor_current_staged_calibration.coefficients.nonnegative_residual_gain[5];
  sStack_e = f33_monitor_current_staged_calibration.coefficients.bias[0];
  sStack_c = f33_monitor_current_staged_calibration.coefficients.bias[1];
  sStack_a = f33_monitor_current_staged_calibration.coefficients.bias[2];
  sStack_20 = f33_monitor_current_staged_calibration.coefficients.bias[3];
  sStack_1e = f33_monitor_current_staged_calibration.coefficients.bias[4];
  sStack_1c = f33_monitor_current_staged_calibration.coefficients.bias[5];
  f33_nvm_set_record(0x200,&local_30);
  (*((undefined4 *)camry_host_ptr((uint32_t)((int)(0xffffb154u + (uint32_t)((int)puVar1)))))) = 0xa55a5aa5;
  return;
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



/* Wrapped signed16 angle delta accumulates signed32 directional extrema; max-min>=65536 increments
   wrapping byte span count. Return0/5A/A5; does not update previous-angle itself. */

uint f33_track_fit_angular_coverage(short angle,uchar required_spans)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  int iVar4;
  
  iVar1 = (int)(short)(angle - f33_six_channel_fit_work.previous_angle);
  f33_six_channel_fit_work.coverage_sum = f33_six_channel_fit_work.coverage_sum + iVar1;
  iVar3 = f33_six_channel_fit_work.coverage_max;
  if ((((-1 < iVar1) || (-1 < f33_six_channel_fit_work.coverage_sum)) ||
      (iVar4 = f33_six_channel_fit_work.coverage_sum,
      f33_six_channel_fit_work.coverage_sum - f33_six_channel_fit_work.coverage_min < 0 ==
      (f33_six_channel_fit_work.coverage_sum < 0 != f33_six_channel_fit_work.coverage_min < 0 &&
      f33_six_channel_fit_work.coverage_min < 0 ==
      f33_six_channel_fit_work.coverage_sum - f33_six_channel_fit_work.coverage_min < 0))) &&
     (((iVar4 = f33_six_channel_fit_work.coverage_min, 0 < iVar1 &&
       (0 < f33_six_channel_fit_work.coverage_sum)) &&
      (iVar3 = f33_six_channel_fit_work.coverage_sum,
      f33_six_channel_fit_work.coverage_sum - f33_six_channel_fit_work.coverage_max < 0 !=
      (f33_six_channel_fit_work.coverage_sum < 0 != f33_six_channel_fit_work.coverage_max < 0 &&
      f33_six_channel_fit_work.coverage_max < 0 ==
      f33_six_channel_fit_work.coverage_sum - f33_six_channel_fit_work.coverage_max < 0) ||
      f33_six_channel_fit_work.coverage_sum == f33_six_channel_fit_work.coverage_max)))) {
    iVar3 = f33_six_channel_fit_work.coverage_max;
  }
  uVar2 = 0;
  iVar1 = (iVar3 - iVar4) + -0x10000;
  if (iVar1 < 0 == (iVar3 - iVar4 < 0 && -1 < iVar1)) {
    f33_six_channel_fit_work.coverage_sum = 0;
    f33_six_channel_fit_work.coverage_count = f33_six_channel_fit_work.coverage_count + 1;
    iVar4 = 0;
    iVar3 = 0;
    uVar2 = 0x5a;
    if (required_spans <= f33_six_channel_fit_work.coverage_count) {
      uVar2 = 0xa5;
    }
  }
  f33_six_channel_fit_work.coverage_min = iVar4;
  f33_six_channel_fit_work.coverage_max = iVar3;
  return uVar2;
}



/* Admission gates from raw retained5F36 and7DB0; invalid gate clears phase-init only. Six unsigned
   Q16 recurrences track literal32768, seed all extrema/outputs32768 and use exact gain11258. Calls
   angular coverage threshold5; final coverage changes root state11->22. */

void f33_step_unsigned_literal_fit_sweep(short angle)

{
  ushort uVar1;
  ushort uVar2;
  ushort uVar3;
  int iVar4;
  uint32_t puVar5;
  uint uVar6;
  uint uVar7;
  int iVar8;
  uint uVar9;
  uint uVar10;
  uint uVar11;
  uint uVar12;
  uint uVar13;
  uint uVar14;
  uint uVar15;
  uint uVar16;
  uchar local_4c;
  uchar uStack_4b;
  ushort uStack_4a;
  ushort uStack_48;
  ushort uStack_46;
  ushort uStack_44;
  ushort uStack_42;
  ushort uStack_40;
  ushort uStack_3e;
  ushort uStack_3c;
  ushort uStack_3a;
  ushort uStack_38;
  ushort uStack_36;
  ushort uStack_34;
  ushort uStack_32;
  ushort uStack_30;
  ushort uStack_2e;
  
  puVar5 = 0xfebeb800u;
  iVar4 = (int)DAT_febe5f36;
  uStack_2e = f33_six_channel_fit_work.unsigned_min[5];
  uStack_4a = f33_six_channel_fit_work.unsigned_previous[3];
  uStack_48 = f33_six_channel_fit_work.unsigned_previous[4];
  uStack_46 = f33_six_channel_fit_work.unsigned_previous[5];
  uStack_38 = f33_six_channel_fit_work.unsigned_min[0];
  uStack_36 = f33_six_channel_fit_work.unsigned_min[1];
  uStack_34 = f33_six_channel_fit_work.unsigned_min[2];
  uStack_32 = f33_six_channel_fit_work.unsigned_min[3];
  uStack_30 = f33_six_channel_fit_work.unsigned_min[4];
  local_4c = f33_six_channel_fit_work.unsigned_initialized;
  uStack_4b = f33_six_channel_fit_work.state;
  uStack_44 = f33_six_channel_fit_work.unsigned_max[0];
  uStack_42 = f33_six_channel_fit_work.unsigned_max[1];
  uStack_40 = f33_six_channel_fit_work.unsigned_max[2];
  uStack_3e = f33_six_channel_fit_work.unsigned_max[3];
  uStack_3c = f33_six_channel_fit_work.unsigned_max[4];
  uStack_3a = f33_six_channel_fit_work.unsigned_max[5];
  if (iVar4 + 0x7fff < 0 == (-1 < iVar4 && iVar4 + 0x7fff < 0) && iVar4 != -0x7fff) {
    if (iVar4 < 0) {
      iVar4 = (int)-DAT_febe5f36;
    }
  }
  else {
    iVar4 = 0x7fff;
  }
  if (((DAT_febe7db0 < f33_fit_parameters.qualifier_lower) ||
      (f33_fit_parameters.qualifier_upper < DAT_febe7db0)) ||
     (iVar8 = (int)f33_fit_parameters.magnitude_upper,
     iVar4 - iVar8 < 0 == (iVar4 < 0 != iVar8 < 0 && iVar8 < 0 == iVar4 - iVar8 < 0) &&
     iVar4 != iVar8)) {
    local_4c = '\0';
  }
  else {
    uVar7 = 0x80000000;
    if (f33_six_channel_fit_work.unsigned_initialized == '\0') {
      uVar16 = 0x8000;
      uStack_4a = 0x8000;
      uStack_48 = 0x8000;
      uStack_46 = 0x8000;
      uVar10 = 0x8000;
      uStack_44 = 0x8000;
      uVar9 = 0x8000;
      uStack_42 = 0x8000;
      uStack_40 = 0x8000;
      uStack_3e = 0x8000;
      uStack_3c = 0x8000;
      uStack_3a = 0x8000;
      uStack_38 = 0x8000;
      uStack_36 = 0x8000;
      uStack_34 = 0x8000;
      uStack_32 = 0x8000;
      uStack_30 = 0x8000;
      uStack_2e = 0x8000;
      f33_six_channel_fit_work.coverage_count = '\0';
      f33_six_channel_fit_work.coverage_sum = 0;
      f33_six_channel_fit_work.coverage_min = 0;
      f33_six_channel_fit_work.coverage_max = 0;
      local_4c = 'Z';
      uVar11 = uVar7;
      uVar12 = uVar7;
      uVar13 = uVar7;
      uVar14 = uVar7;
      uVar15 = uVar7;
    }
    else {
      iVar4 = (uint)f33_fit_parameters.unsigned_filter_half_gain * 2;
      uVar6 = iVar4 - 1;
      if (uVar6 < 0xffff) {
        uVar15 = (uint)f33_fit_parameters.unsigned_filter_half_gain * 0x10000 +
                 (f33_six_channel_fit_work.unsigned_q16[0] -
                 (uint)f33_six_channel_fit_work.unsigned_previous[0] * iVar4);
      }
      else {
        uVar15 = f33_six_channel_fit_work.unsigned_q16[0] +
                 (uint)f33_six_channel_fit_work.unsigned_previous[0] * -0x10000 + 0x80000000;
      }
      uVar16 = uVar15 >> 0x10;
      if (uVar6 < 0xffff) {
        uVar14 = (uint)f33_fit_parameters.unsigned_filter_half_gain * 0x10000 +
                 (f33_six_channel_fit_work.unsigned_q16[1] -
                 (uint)f33_six_channel_fit_work.unsigned_previous[1] * iVar4);
      }
      else {
        uVar14 = f33_six_channel_fit_work.unsigned_q16[1] +
                 (uint)f33_six_channel_fit_work.unsigned_previous[1] * -0x10000 + 0x80000000;
      }
      uVar10 = uVar14 >> 0x10;
      if (uVar6 < 0xffff) {
        uVar13 = (uint)f33_fit_parameters.unsigned_filter_half_gain * 0x10000 +
                 (f33_six_channel_fit_work.unsigned_q16[2] -
                 (uint)f33_six_channel_fit_work.unsigned_previous[2] * iVar4);
      }
      else {
        uVar13 = f33_six_channel_fit_work.unsigned_q16[2] +
                 (uint)f33_six_channel_fit_work.unsigned_previous[2] * -0x10000 + 0x80000000;
      }
      uVar9 = uVar13 >> 0x10;
      if (uVar6 < 0xffff) {
        uVar12 = (uint)f33_fit_parameters.unsigned_filter_half_gain * 0x10000 +
                 (f33_six_channel_fit_work.unsigned_q16[3] -
                 (uint)f33_six_channel_fit_work.unsigned_previous[3] * iVar4);
      }
      else {
        uVar12 = f33_six_channel_fit_work.unsigned_q16[3] +
                 (uint)f33_six_channel_fit_work.unsigned_previous[3] * -0x10000 + 0x80000000;
      }
      uStack_4a = (ushort)(uVar12 >> 0x10);
      if (uVar6 < 0xffff) {
        uVar11 = (uint)f33_fit_parameters.unsigned_filter_half_gain * 0x10000 +
                 (f33_six_channel_fit_work.unsigned_q16[4] -
                 (uint)f33_six_channel_fit_work.unsigned_previous[4] * iVar4);
      }
      else {
        uVar11 = f33_six_channel_fit_work.unsigned_q16[4] +
                 (uint)f33_six_channel_fit_work.unsigned_previous[4] * -0x10000 + 0x80000000;
      }
      uStack_48 = (ushort)(uVar11 >> 0x10);
      if (uVar6 < 0xffff) {
        iVar8 = (uint)f33_fit_parameters.unsigned_filter_half_gain << 0x10;
        uVar7 = f33_six_channel_fit_work.unsigned_q16[5] -
                (uint)f33_six_channel_fit_work.unsigned_previous[5] * iVar4;
      }
      else {
        iVar8 = f33_six_channel_fit_work.unsigned_q16[5] +
                (uint)f33_six_channel_fit_work.unsigned_previous[5] * -0x10000;
      }
      uVar7 = iVar8 + uVar7;
      uVar6 = uVar7 >> 0x10;
      uStack_46 = (ushort)(uVar7 >> 0x10);
      uVar1 = (ushort)(uVar15 >> 0x10);
      if (-1 < (int)(uVar16 - f33_six_channel_fit_work.unsigned_max[0]) &&
          uVar16 != f33_six_channel_fit_work.unsigned_max[0]) {
        uStack_44 = uVar1;
      }
      uVar2 = (ushort)(uVar14 >> 0x10);
      if (-1 < (int)(uVar10 - f33_six_channel_fit_work.unsigned_max[1]) &&
          uVar10 != f33_six_channel_fit_work.unsigned_max[1]) {
        uStack_42 = uVar2;
      }
      uVar3 = (ushort)(uVar13 >> 0x10);
      if (-1 < (int)(uVar9 - f33_six_channel_fit_work.unsigned_max[2]) &&
          uVar9 != f33_six_channel_fit_work.unsigned_max[2]) {
        uStack_40 = uVar3;
      }
      if (-1 < (int)((uint)uStack_4a - (uint)f33_six_channel_fit_work.unsigned_max[3]) &&
          (uint)uStack_4a != (uint)f33_six_channel_fit_work.unsigned_max[3]) {
        uStack_3e = uStack_4a;
      }
      if (-1 < (int)((uint)uStack_48 - (uint)f33_six_channel_fit_work.unsigned_max[4]) &&
          (uint)uStack_48 != (uint)f33_six_channel_fit_work.unsigned_max[4]) {
        uStack_3c = uStack_48;
      }
      if (-1 < (int)(uVar6 - f33_six_channel_fit_work.unsigned_max[5]) &&
          uVar6 != f33_six_channel_fit_work.unsigned_max[5]) {
        uStack_3a = uStack_46;
      }
      if ((int)(uVar16 - f33_six_channel_fit_work.unsigned_min[0]) < 0) {
        uStack_38 = uVar1;
      }
      if ((int)(uVar10 - f33_six_channel_fit_work.unsigned_min[1]) < 0) {
        uStack_36 = uVar2;
      }
      if ((int)(uVar9 - f33_six_channel_fit_work.unsigned_min[2]) < 0) {
        uStack_34 = uVar3;
      }
      if ((int)((uint)uStack_4a - (uint)f33_six_channel_fit_work.unsigned_min[3]) < 0) {
        uStack_32 = uStack_4a;
      }
      if ((int)((uint)uStack_48 - (uint)f33_six_channel_fit_work.unsigned_min[4]) < 0) {
        uStack_30 = uStack_48;
      }
      if ((int)(uVar6 - f33_six_channel_fit_work.unsigned_min[5]) < 0) {
        uStack_2e = uStack_46;
      }
    }
    puVar5 = 0xfebeb800u;
    uVar6 = f33_track_fit_angular_coverage(angle,f33_fit_parameters.unsigned_coverage_spans);
    f33_six_channel_fit_work.unsigned_q16[5] = uVar7;
    f33_six_channel_fit_work.unsigned_q16[4] = uVar11;
    f33_six_channel_fit_work.unsigned_q16[3] = uVar12;
    f33_six_channel_fit_work.unsigned_q16[2] = uVar13;
    f33_six_channel_fit_work.unsigned_q16[1] = uVar14;
    f33_six_channel_fit_work.unsigned_q16[0] = uVar15;
    f33_six_channel_fit_work.unsigned_previous[0] = (ushort)uVar16;
    f33_six_channel_fit_work.unsigned_previous[1] = (ushort)uVar10;
    f33_six_channel_fit_work.unsigned_previous[2] = (ushort)uVar9;
    if (uVar6 == 0xa5) {
      uStack_4b = '\"';
    }
  }
  (*((uchar *)camry_host_ptr((uint32_t)((int)(0xffffb162u + (uint32_t)((int)puVar5)))))) = local_4c;
  (*((uchar *)camry_host_ptr((uint32_t)((int)(0xffffb160u + (uint32_t)((int)puVar5)))))) = uStack_4b;
  f33_six_channel_fit_work.unsigned_max[0] = uStack_44;
  f33_six_channel_fit_work.unsigned_max[1] = uStack_42;
  f33_six_channel_fit_work.unsigned_max[2] = uStack_40;
  f33_six_channel_fit_work.unsigned_max[3] = uStack_3e;
  f33_six_channel_fit_work.unsigned_max[4] = uStack_3c;
  f33_six_channel_fit_work.unsigned_max[5] = uStack_3a;
  f33_six_channel_fit_work.unsigned_min[0] = uStack_38;
  f33_six_channel_fit_work.unsigned_min[1] = uStack_36;
  f33_six_channel_fit_work.unsigned_min[2] = uStack_34;
  f33_six_channel_fit_work.unsigned_min[3] = uStack_32;
  f33_six_channel_fit_work.unsigned_min[4] = uStack_30;
  f33_six_channel_fit_work.unsigned_min[5] = uStack_2e;
  f33_six_channel_fit_work.unsigned_previous[3] = uStack_4a;
  f33_six_channel_fit_work.unsigned_previous[5] = uStack_46;
  f33_six_channel_fit_work.unsigned_previous[4] = uStack_48;
  return;
}



/* WARNING: Removing unreachable block (ram,0x000335a0) */
/* WARNING: Removing unreachable block (ram,0x0003356a) */
/* WARNING: Removing unreachable block (ram,0x00033538) */
/* WARNING: Removing unreachable block (ram,0x00033504) */
/* WARNING: Removing unreachable block (ram,0x000334de) */
/* WARNING: Removing unreachable block (ram,0x000334b8) */
/* WARNING: Removing unreachable block (ram,0x00033354) */
/* WARNING: Removing unreachable block (ram,0x00033350) */
/* WARNING: Removing unreachable block (ram,0x0003334c) */
/* WARNING: Removing unreachable block (ram,0x00033348) */
/* WARNING: Removing unreachable block (ram,0x00033344) */
/* WARNING: Removing unreachable block (ram,0x00033340) */
/* WARNING: Removing unreachable block (ram,0x000331b6) */
/* WARNING: Removing unreachable block (ram,0x000331b2) */
/* WARNING: Removing unreachable block (ram,0x000331ae) */
/* WARNING: Removing unreachable block (ram,0x000331aa) */
/* WARNING: Removing unreachable block (ram,0x000331a6) */
/* WARNING: Removing unreachable block (ram,0x000331a2) */
/* Derive six signed channels from retained first gains/centers and literal32768, not live sample
   channels. Symmetric saturation, signed division and six Q16 recurrences use truncation toward
   zero. Same input gates and coverage threshold5 advance33->44. */

void f33_step_signed_constant_fit_sweep(short angle)

{
  longlong lVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  uint32_t puVar5;
  uint uVar6;
  uint uVar7;
  uint uVar8;
  uint uVar9;
  uint uVar10;
  uint uVar11;
  int iVar12;
  int iVar13;
  int iVar14;
  int iVar15;
  int iVar16;
  int iVar17;
  int iVar18;
  int iVar19;
  int iVar20;
  short sVar21;
  short sVar22;
  short sVar23;
  short sVar24;
  short sVar25;
  short sVar26;
  uchar uStack_52;
  uchar uStack_51;
  int iStack_50;
  int iStack_4c;
  int iStack_48;
  short sStack_44;
  short sStack_42;
  short sStack_40;
  short sStack_3e;
  short sStack_3c;
  short sStack_3a;
  short sStack_38;
  short sStack_36;
  short sStack_34;
  short sStack_32;
  short sStack_30;
  short sStack_2e;
  
  puVar5 = 0xfebeb800u;
  iVar2 = (int)((int)(int16_t)DAT_febe5f36);
  uStack_52 = f33_six_channel_fit_work.signed_initialized;
  uStack_51 = f33_six_channel_fit_work.state;
  sStack_44 = f33_six_channel_fit_work.signed_max[0];
  sStack_38 = f33_six_channel_fit_work.signed_min[0];
  sStack_36 = f33_six_channel_fit_work.signed_min[1];
  sStack_34 = f33_six_channel_fit_work.signed_min[2];
  sStack_32 = f33_six_channel_fit_work.signed_min[3];
  sStack_30 = f33_six_channel_fit_work.signed_min[4];
  sStack_2e = f33_six_channel_fit_work.signed_min[5];
  sStack_40 = f33_six_channel_fit_work.signed_max[2];
  sStack_3e = f33_six_channel_fit_work.signed_max[3];
  sStack_3c = f33_six_channel_fit_work.signed_max[4];
  sStack_3a = f33_six_channel_fit_work.signed_max[5];
  iStack_50 = f33_six_channel_fit_work.signed_q16[3];
  iStack_4c = f33_six_channel_fit_work.signed_q16[4];
  iStack_48 = f33_six_channel_fit_work.signed_q16[5];
  sStack_42 = f33_six_channel_fit_work.signed_max[1];
  uVar11 = (uint)f33_six_channel_fit_work.first_gain[0];
  uVar10 = (uint)f33_six_channel_fit_work.first_gain[1];
  uVar9 = (uint)f33_six_channel_fit_work.first_gain[2];
  uVar8 = (uint)f33_six_channel_fit_work.first_gain[3];
  uVar7 = (uint)f33_six_channel_fit_work.first_gain[4];
  uVar6 = (uint)f33_six_channel_fit_work.first_gain[5];
  if (iVar2 + 0x7fff < 0 == (-1 < iVar2 && iVar2 + 0x7fff < 0) && iVar2 != -0x7fff) {
    if (iVar2 < 0) {
      iVar2 = (int)-((int)(int16_t)DAT_febe5f36);
    }
  }
  else {
    iVar2 = 0x7fff;
  }
  if (((DAT_febe7db0 < f33_fit_parameters.qualifier_lower) ||
      (f33_fit_parameters.qualifier_upper < DAT_febe7db0)) ||
     (iVar17 = (int)f33_fit_parameters.magnitude_upper,
     iVar2 - iVar17 < 0 == (iVar2 < 0 != iVar17 < 0 && iVar17 < 0 == iVar2 - iVar17 < 0) &&
     iVar2 != iVar17)) {
    uStack_52 = '\0';
    goto LAB_00033638;
  }
  iVar2 = (int)(0x8000 - (uint)f33_six_channel_fit_work.first_center[0]) / 4;
  iVar17 = (int)(0x8000 - (uint)f33_six_channel_fit_work.first_center[1]) / 4;
  iVar15 = (int)(0x8000 - (uint)f33_six_channel_fit_work.first_center[2]) / 4;
  iVar14 = (int)(0x8000 - (uint)f33_six_channel_fit_work.first_center[3]) / 4;
  iVar3 = (int)(0x8000 - (uint)f33_six_channel_fit_work.first_center[4]) / 4;
  iVar12 = (int)(0x8000 - (uint)f33_six_channel_fit_work.first_center[5]) / 4;
  if ((uVar11 == 0) || (iVar2 == 0)) {
    iVar2 = 0;
  }
  else {
    lVar1 = (longlong)iVar2 * (longlong)(int)uVar11;
    iVar4 = (int)((ulonglong)lVar1 >> 0x20);
    if (iVar2 < 0) {
      iVar4 = iVar4 + 1;
      if ((iVar4 < 0 == (-1 < lVar1 && iVar4 < 0)) && (0x80000000 < uVar11 * iVar2))
      goto LAB_000331fe;
      iVar2 = -0x7fffffff;
    }
    else if ((lVar1 < 0 || iVar4 == 0) && (uVar11 * iVar2 < 0x80000000)) {
LAB_000331fe:
      iVar2 = uVar11 * iVar2;
    }
    else {
      iVar2 = 0x7fffffff;
    }
  }
  if ((uVar10 == 0) || (iVar17 == 0)) {
    iVar17 = 0;
  }
  else {
    lVar1 = (longlong)iVar17 * (longlong)(int)uVar10;
    iVar4 = (int)((ulonglong)lVar1 >> 0x20);
    if (iVar17 < 0) {
      iVar4 = iVar4 + 1;
      if ((iVar4 < 0 == (-1 < lVar1 && iVar4 < 0)) && (0x80000000 < uVar10 * iVar17))
      goto LAB_0003323e;
      iVar17 = -0x7fffffff;
    }
    else if ((lVar1 < 0 || iVar4 == 0) && (uVar10 * iVar17 < 0x80000000)) {
LAB_0003323e:
      iVar17 = uVar10 * iVar17;
    }
    else {
      iVar17 = 0x7fffffff;
    }
  }
  if ((uVar9 == 0) || (iVar15 == 0)) {
    iVar15 = 0;
  }
  else {
    lVar1 = (longlong)iVar15 * (longlong)(int)uVar9;
    iVar4 = (int)((ulonglong)lVar1 >> 0x20);
    if (iVar15 < 0) {
      iVar4 = iVar4 + 1;
      if ((iVar4 < 0 == (-1 < lVar1 && iVar4 < 0)) && (0x80000000 < uVar9 * iVar15))
      goto LAB_0003327e;
      iVar15 = -0x7fffffff;
    }
    else if ((lVar1 < 0 || iVar4 == 0) && (uVar9 * iVar15 < 0x80000000)) {
LAB_0003327e:
      iVar15 = uVar9 * iVar15;
    }
    else {
      iVar15 = 0x7fffffff;
    }
  }
  if ((uVar8 == 0) || (iVar14 == 0)) {
    iVar14 = 0;
  }
  else {
    lVar1 = (longlong)iVar14 * (longlong)(int)uVar8;
    iVar4 = (int)((ulonglong)lVar1 >> 0x20);
    if (iVar14 < 0) {
      iVar4 = iVar4 + 1;
      if ((iVar4 < 0 == (-1 < lVar1 && iVar4 < 0)) && (0x80000000 < uVar8 * iVar14))
      goto LAB_000332be;
      iVar14 = -0x7fffffff;
    }
    else if ((lVar1 < 0 || iVar4 == 0) && (uVar8 * iVar14 < 0x80000000)) {
LAB_000332be:
      iVar14 = uVar8 * iVar14;
    }
    else {
      iVar14 = 0x7fffffff;
    }
  }
  if ((uVar7 == 0) || (iVar3 == 0)) {
    iVar3 = 0;
  }
  else {
    lVar1 = (longlong)iVar3 * (longlong)(int)uVar7;
    iVar4 = (int)((ulonglong)lVar1 >> 0x20);
    if (iVar3 < 0) {
      iVar4 = iVar4 + 1;
      if ((iVar4 < 0 == (-1 < lVar1 && iVar4 < 0)) && (0x80000000 < uVar7 * iVar3))
      goto LAB_000332fe;
      iVar3 = -0x7fffffff;
    }
    else if ((lVar1 < 0 || iVar4 == 0) && (uVar7 * iVar3 < 0x80000000)) {
LAB_000332fe:
      iVar3 = uVar7 * iVar3;
    }
    else {
      iVar3 = 0x7fffffff;
    }
  }
  if ((uVar6 == 0) || (iVar12 == 0)) {
    uVar6 = 0;
  }
  else {
    lVar1 = (longlong)iVar12 * (longlong)(int)uVar6;
    iVar4 = (int)((ulonglong)lVar1 >> 0x20);
    if (iVar12 < 0) {
      iVar4 = iVar4 + 1;
      if ((iVar4 < 0 != (-1 < lVar1 && iVar4 < 0)) || (uVar6 = uVar6 * iVar12, uVar6 < 0x80000001))
      {
        uVar6 = 0x80000001;
      }
    }
    else if ((-1 < lVar1 && iVar4 != 0) || (uVar6 = (int)uVar6 * iVar12, 0x7fffffff < (int)uVar6)) {
      uVar6 = 0x7fffffff;
    }
  }
  iVar4 = iVar3 / 0x8000 + iVar2 / 0x8000;
  iVar20 = (int)uVar6 / 0x8000 + iVar17 / 0x8000;
  iVar12 = iVar4 - iVar20;
  iVar20 = iVar20 + iVar4;
  iVar3 = iVar3 / 0x8000 + iVar15 / 0x8000;
  iVar15 = iVar15 / 0x8000 + iVar2 / 0x8000;
  iVar4 = iVar14 / 0x8000 + iVar17 / 0x8000;
  iVar14 = (int)uVar6 / 0x8000 + iVar14 / 0x8000;
  iVar2 = iVar15 - iVar4;
  iVar17 = iVar3 - iVar14;
  iVar4 = iVar4 + iVar15;
  iVar14 = iVar14 + iVar3;
  if (iVar12 + 0x7fff < 0 == (-1 < iVar12 && iVar12 + 0x7fff < 0) && iVar12 != -0x7fff) {
    if (iVar12 + -0x7fff < 0 == (iVar12 < 0 && -1 < iVar12 + -0x7fff) && iVar12 != 0x7fff) {
      iVar15 = 0x7fff;
    }
    else {
      iVar15 = (int)(short)iVar12;
    }
  }
  else {
    iVar15 = -0x7fff;
  }
  if (iVar20 + 0x7fff < 0 == (-1 < iVar20 && iVar20 + 0x7fff < 0) && iVar20 != -0x7fff) {
    if (iVar20 + -0x7fff < 0 == (iVar20 < 0 && -1 < iVar20 + -0x7fff) && iVar20 != 0x7fff) {
      iVar3 = 0x7fff;
    }
    else {
      iVar3 = (int)(short)iVar20;
    }
  }
  else {
    iVar3 = -0x7fff;
  }
  if (iVar2 + 0x7fff < 0 == (-1 < iVar2 && iVar2 + 0x7fff < 0) && iVar2 != -0x7fff) {
    if (iVar2 + -0x7fff < 0 == (iVar2 < 0 && -1 < iVar2 + -0x7fff) && iVar2 != 0x7fff) {
      iVar2 = 0x7fff;
    }
    else {
      iVar2 = (int)(short)iVar2;
    }
  }
  else {
    iVar2 = -0x7fff;
  }
  if (iVar4 + 0x7fff < 0 == (-1 < iVar4 && iVar4 + 0x7fff < 0) && iVar4 != -0x7fff) {
    if (iVar4 + -0x7fff < 0 == (iVar4 < 0 && -1 < iVar4 + -0x7fff) && iVar4 != 0x7fff) {
      iVar12 = 0x7fff;
    }
    else {
      iVar12 = (int)(short)iVar4;
    }
  }
  else {
    iVar12 = -0x7fff;
  }
  if (iVar17 + 0x7fff < 0 == (-1 < iVar17 && iVar17 + 0x7fff < 0) && iVar17 != -0x7fff) {
    iVar4 = (int)(short)iVar17;
    if (iVar17 + -0x7fff < 0 == (iVar17 < 0 && -1 < iVar17 + -0x7fff) && iVar17 != 0x7fff) {
      iVar4 = 0x7fff;
    }
  }
  else {
    iVar4 = -0x7fff;
  }
  if (iVar14 + 0x7fff < 0 == (-1 < iVar14 && iVar14 + 0x7fff < 0) && iVar14 != -0x7fff) {
    iVar17 = (int)(short)iVar14;
    if (iVar14 + -0x7fff < 0 == (iVar14 < 0 && -1 < iVar14 + -0x7fff) && iVar14 != 0x7fff) {
      iVar17 = 0x7fff;
    }
  }
  else {
    iVar17 = -0x7fff;
  }
  if (f33_six_channel_fit_work.signed_initialized == '\0') {
    sStack_3a = (short)iVar17;
    sStack_3c = (short)iVar4;
    sStack_3e = (short)iVar12;
    sStack_40 = (short)iVar2;
    sStack_42 = (short)iVar3;
    sStack_44 = (short)iVar15;
    iStack_50 = iVar12 << 0x10;
    iVar18 = iVar2 << 0x10;
    iVar19 = iVar3 << 0x10;
    iVar20 = iVar15 << 0x10;
    iStack_4c = iVar4 << 0x10;
    iStack_48 = iVar17 << 0x10;
    f33_six_channel_fit_work.coverage_max = 0;
    f33_six_channel_fit_work.coverage_min = 0;
    f33_six_channel_fit_work.coverage_sum = 0;
    f33_six_channel_fit_work.coverage_count = '\0';
    uStack_52 = 'Z';
    sStack_38 = sStack_44;
    sStack_36 = sStack_42;
    sStack_34 = sStack_40;
    sStack_32 = sStack_3e;
    sStack_30 = sStack_3c;
    sStack_2e = sStack_3a;
  }
  else {
    iVar14 = (uint)f33_fit_parameters.signed_filter_half_gain * 2;
    uVar6 = iVar14 - 1;
    if (uVar6 < 0xffff) {
      iVar20 = f33_six_channel_fit_work.signed_previous[0] * iVar14;
      iVar15 = iVar15 * iVar14;
    }
    else {
      iVar20 = (int)f33_six_channel_fit_work.signed_previous[0] << 0x10;
      iVar15 = iVar15 << 0x10;
    }
    iVar20 = iVar15 + (f33_six_channel_fit_work.signed_q16[0] - iVar20);
    sVar26 = (short)(iVar20 / 0x10000);
    iVar15 = (int)sVar26;
    if (uVar6 < 0xffff) {
      iVar19 = f33_six_channel_fit_work.signed_previous[1] * iVar14;
      iVar3 = iVar3 * iVar14;
    }
    else {
      iVar19 = (int)f33_six_channel_fit_work.signed_previous[1] << 0x10;
      iVar3 = iVar3 << 0x10;
    }
    iVar19 = iVar3 + (f33_six_channel_fit_work.signed_q16[1] - iVar19);
    sVar25 = (short)(iVar19 / 0x10000);
    iVar3 = (int)sVar25;
    if (uVar6 < 0xffff) {
      iVar18 = f33_six_channel_fit_work.signed_previous[2] * iVar14;
      iVar2 = iVar2 * iVar14;
    }
    else {
      iVar18 = (int)f33_six_channel_fit_work.signed_previous[2] << 0x10;
      iVar2 = iVar2 << 0x10;
    }
    iVar18 = iVar2 + (f33_six_channel_fit_work.signed_q16[2] - iVar18);
    sVar24 = (short)(iVar18 / 0x10000);
    iVar2 = (int)sVar24;
    if (uVar6 < 0xffff) {
      iVar16 = f33_six_channel_fit_work.signed_previous[3] * iVar14;
      iVar12 = iVar12 * iVar14;
    }
    else {
      iVar16 = (int)f33_six_channel_fit_work.signed_previous[3] << 0x10;
      iVar12 = iVar12 << 0x10;
    }
    iStack_50 = iVar12 + (f33_six_channel_fit_work.signed_q16[3] - iVar16);
    sVar23 = (short)(iStack_50 / 0x10000);
    iVar12 = (int)sVar23;
    if (uVar6 < 0xffff) {
      iVar16 = f33_six_channel_fit_work.signed_previous[4] * iVar14;
      iVar4 = iVar4 * iVar14;
    }
    else {
      iVar16 = (int)f33_six_channel_fit_work.signed_previous[4] << 0x10;
      iVar4 = iVar4 << 0x10;
    }
    iStack_4c = iVar4 + (f33_six_channel_fit_work.signed_q16[4] - iVar16);
    sVar22 = (short)(iStack_4c / 0x10000);
    iVar4 = (int)sVar22;
    if (uVar6 < 0xffff) {
      iVar16 = f33_six_channel_fit_work.signed_previous[5] * iVar14;
      iVar17 = iVar17 * iVar14;
    }
    else {
      iVar16 = (int)f33_six_channel_fit_work.signed_previous[5] << 0x10;
      iVar17 = iVar17 << 0x10;
    }
    iVar14 = (int)f33_six_channel_fit_work.signed_max[0];
    iVar13 = (int)f33_six_channel_fit_work.signed_max[1];
    iStack_48 = iVar17 + (f33_six_channel_fit_work.signed_q16[5] - iVar16);
    iVar16 = (int)f33_six_channel_fit_work.signed_max[2];
    if (iVar15 - iVar14 < 0 == (iVar15 < 0 != iVar14 < 0 && iVar14 < 0 == iVar15 - iVar14 < 0) &&
        iVar15 != iVar14) {
      sStack_44 = sVar26;
    }
    sVar21 = (short)(iStack_48 / 0x10000);
    iVar17 = (int)sVar21;
    iVar14 = (int)f33_six_channel_fit_work.signed_max[3];
    if (iVar3 - iVar13 < 0 == (iVar3 < 0 != iVar13 < 0 && iVar13 < 0 == iVar3 - iVar13 < 0) &&
        iVar3 != iVar13) {
      sStack_42 = sVar25;
    }
    iVar13 = (int)f33_six_channel_fit_work.signed_max[4];
    if (iVar2 - iVar16 < 0 == (iVar2 < 0 != iVar16 < 0 && iVar16 < 0 == iVar2 - iVar16 < 0) &&
        iVar2 != iVar16) {
      sStack_40 = sVar24;
    }
    iVar16 = (int)f33_six_channel_fit_work.signed_max[5];
    if (iVar12 - iVar14 < 0 == (iVar12 < 0 != iVar14 < 0 && iVar14 < 0 == iVar12 - iVar14 < 0) &&
        iVar12 != iVar14) {
      sStack_3e = sVar23;
    }
    iVar14 = (int)f33_six_channel_fit_work.signed_min[0];
    if (iVar4 - iVar13 < 0 == (iVar4 < 0 != iVar13 < 0 && iVar13 < 0 == iVar4 - iVar13 < 0) &&
        iVar4 != iVar13) {
      sStack_3c = sVar22;
    }
    iVar13 = (int)f33_six_channel_fit_work.signed_min[1];
    if (iVar17 - iVar16 < 0 == (iVar17 < 0 != iVar16 < 0 && iVar16 < 0 == iVar17 - iVar16 < 0) &&
        iVar17 != iVar16) {
      sStack_3a = sVar21;
    }
    iVar16 = (int)f33_six_channel_fit_work.signed_min[2];
    if (iVar15 - iVar14 < 0 != (iVar15 < 0 != iVar14 < 0 && iVar14 < 0 == iVar15 - iVar14 < 0)) {
      sStack_38 = sVar26;
    }
    iVar14 = (int)f33_six_channel_fit_work.signed_min[3];
    if (iVar3 - iVar13 < 0 != (iVar3 < 0 != iVar13 < 0 && iVar13 < 0 == iVar3 - iVar13 < 0)) {
      sStack_36 = sVar25;
    }
    iVar13 = (int)f33_six_channel_fit_work.signed_min[4];
    if (iVar2 - iVar16 < 0 != (iVar2 < 0 != iVar16 < 0 && iVar16 < 0 == iVar2 - iVar16 < 0)) {
      sStack_34 = sVar24;
    }
    iVar16 = (int)f33_six_channel_fit_work.signed_min[5];
    if (iVar12 - iVar14 < 0 != (iVar12 < 0 != iVar14 < 0 && iVar14 < 0 == iVar12 - iVar14 < 0)) {
      sStack_32 = sVar23;
    }
    if (iVar4 - iVar13 < 0 != (iVar4 < 0 != iVar13 < 0 && iVar13 < 0 == iVar4 - iVar13 < 0)) {
      sStack_30 = sVar22;
    }
    if (iVar17 - iVar16 < 0 != (iVar17 < 0 != iVar16 < 0 && iVar16 < 0 == iVar17 - iVar16 < 0)) {
      sStack_2e = sVar21;
    }
  }
  puVar5 = 0xfebeb800u;
  uVar6 = f33_track_fit_angular_coverage(angle,f33_fit_parameters.signed_coverage_spans);
  f33_six_channel_fit_work.signed_q16[2] = iVar18;
  f33_six_channel_fit_work.signed_q16[1] = iVar19;
  f33_six_channel_fit_work.signed_q16[0] = iVar20;
  f33_six_channel_fit_work.signed_previous[0] = (short)iVar15;
  f33_six_channel_fit_work.signed_previous[1] = (short)iVar3;
  f33_six_channel_fit_work.signed_previous[2] = (short)iVar2;
  f33_six_channel_fit_work.signed_previous[3] = (short)iVar12;
  f33_six_channel_fit_work.signed_previous[4] = (short)iVar4;
  f33_six_channel_fit_work.signed_previous[5] = (short)iVar17;
  if (uVar6 == 0xa5) {
    uStack_51 = 'D';
  }
LAB_00033638:
  (*((uchar *)camry_host_ptr((uint32_t)((int)0xffffb162u + (int)(puVar5 + 1))))) = uStack_52;
  (*((uchar *)camry_host_ptr((uint32_t)((int)(0xffffb160u + (uint32_t)((int)puVar5)))))) = uStack_51;
  f33_six_channel_fit_work.signed_max[0] = sStack_44;
  f33_six_channel_fit_work.signed_max[1] = sStack_42;
  f33_six_channel_fit_work.signed_max[2] = sStack_40;
  f33_six_channel_fit_work.signed_max[3] = sStack_3e;
  f33_six_channel_fit_work.signed_max[4] = sStack_3c;
  f33_six_channel_fit_work.signed_max[5] = sStack_3a;
  f33_six_channel_fit_work.signed_min[0] = sStack_38;
  f33_six_channel_fit_work.signed_min[1] = sStack_36;
  f33_six_channel_fit_work.signed_min[2] = sStack_34;
  f33_six_channel_fit_work.signed_min[3] = sStack_32;
  f33_six_channel_fit_work.signed_min[4] = sStack_30;
  f33_six_channel_fit_work.signed_min[5] = sStack_2e;
  f33_six_channel_fit_work.signed_q16[3] = iStack_50;
  f33_six_channel_fit_work.signed_q16[4] = iStack_4c;
  f33_six_channel_fit_work.signed_q16[5] = iStack_48;
  return;
}



/* WARNING: Removing unreachable block (ram,0x00033962) */
/* WARNING: Removing unreachable block (ram,0x0003395e) */
/* WARNING: Removing unreachable block (ram,0x0003395a) */
/* WARNING: Removing unreachable block (ram,0x00033956) */
/* WARNING: Removing unreachable block (ram,0x00033952) */
/* WARNING: Removing unreachable block (ram,0x0003394e) */
/* WARNING: Removing unreachable block (ram,0x0003394a) */
/* WARNING: Removing unreachable block (ram,0x00033946) */
/* WARNING: Removing unreachable block (ram,0x00033942) */
/* WARNING: Removing unreachable block (ram,0x00033936) */
/* WARNING: Removing unreachable block (ram,0x00033932) */
/* WARNING: Removing unreachable block (ram,0x0003390a) */
/* Mode0512/0600 six-channel numerical-fit controller; active6961=5A, states0/11/22/33/44/55/66.
   Prior-angle update occurs even while inactive or phase-admission fails. First sweep follows
   literal0x8000, not acquired samples; numerical success is not physical calibration. Terminal flag
   clears on next invocation. Interior33966 shares this function frame; it is not an independent
   ABI. Interior33966 shares this frame, not an independent ABI. */

void f33_step_six_channel_fit(void)

{
  short sVar1;
  uint uVar2;
  uint uVar3;
  undefined *puVar4;
  uint32_t puVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  uint uVar10;
  uint uVar11;
  uint uVar12;
  int iVar13;
  uint uVar14;
  int iVar15;
  int iVar16;
  uint uVar17;
  uint uVar18;
  uint uVar19;
  uchar uVar20;
  int iVar21;
  int iVar22;
  int iVar23;
  int iVar24;
  int iVar25;
  ushort local_44;
  ushort uStack_42;
  ushort uStack_40;
  short sStack_3e;
  short sStack_3c;
  short sStack_3a;
  ushort uStack_38;
  ushort uStack_36;
  ushort uStack_34;
  ushort uStack_32;
  ushort uStack_30;
  ushort uStack_2e;
  
  sVar1 = (short)DAT_febe7d94;
  uVar20 = f33_six_channel_fit_work.active;
  puVar5 = 0xfebeb800u;
  puVar4 = ((undefined *)camry_host_ptr(0xfebeb800u));
  if (f33_six_channel_fit_work.active == 'Z') {
    if (f33_six_channel_fit_work.state == '\0') {
      f33_six_channel_fit_work.unsigned_initialized = '\0';
      f33_six_channel_fit_work.state = '\x11';
      f33_six_channel_fit_work.signed_initialized = '\0';
      f33_six_channel_fit_work.coverage_count = '\0';
      f33_six_channel_fit_work.coverage_sum = 0;
      f33_six_channel_fit_work.coverage_min = 0;
      f33_six_channel_fit_work.coverage_max = 0;
    }
    else if (f33_six_channel_fit_work.state == '\x11') {
      puVar4 = ((undefined *)camry_host_ptr(0xfebeb800u));
      f33_step_unsigned_literal_fit_sweep((short)DAT_febe7d94);
    }
    else if (f33_six_channel_fit_work.state == '\"') {
      iVar6 = (uint)f33_six_channel_fit_work.unsigned_max[0] -
              (uint)f33_six_channel_fit_work.unsigned_min[0];
      uStack_38 = f33_six_channel_fit_work.first_gain[0];
      uStack_36 = f33_six_channel_fit_work.first_gain[1];
      uStack_34 = f33_six_channel_fit_work.first_gain[2];
      uStack_32 = f33_six_channel_fit_work.first_gain[3];
      iVar7 = (uint)f33_six_channel_fit_work.unsigned_max[1] -
              (uint)f33_six_channel_fit_work.unsigned_min[1];
      uStack_30 = f33_six_channel_fit_work.first_gain[4];
      iVar8 = (uint)f33_six_channel_fit_work.unsigned_max[2] -
              (uint)f33_six_channel_fit_work.unsigned_min[2];
      uStack_2e = f33_six_channel_fit_work.first_gain[5];
      iVar9 = (uint)f33_six_channel_fit_work.unsigned_max[3] -
              (uint)f33_six_channel_fit_work.unsigned_min[3];
      iVar13 = (uint)f33_six_channel_fit_work.unsigned_max[4] -
               (uint)f33_six_channel_fit_work.unsigned_min[4];
      iVar15 = (uint)f33_six_channel_fit_work.unsigned_max[5] -
               (uint)f33_six_channel_fit_work.unsigned_min[5];
      if ((((iVar6 < 1) || (iVar7 < 1)) || (iVar8 < 1)) ||
         (((iVar9 < 1 || (iVar13 < 1)) || (iVar15 < 1)))) {
        f33_six_channel_fit_work.state = 'f';
      }
      else {
        uVar18 = (uint)f33_fit_parameters.first_gain_numerator;
        uVar17 = uVar18 << 0xf;
        uVar11 = uVar17;
        if (iVar8 != 0) {
          if (uVar18 == 0x10000 && iVar8 == -1) {
            uVar11 = 0x80000000;
          }
          else {
            uVar11 = (int)uVar17 / iVar8;
          }
        }
        uVar3 = uVar17;
        if (iVar9 != 0) {
          if (uVar18 == 0x10000 && iVar9 == -1) {
            uVar3 = 0x80000000;
          }
          else {
            uVar3 = (int)uVar17 / iVar9;
          }
        }
        uVar19 = uVar17;
        if (iVar6 != 0) {
          if (uVar18 == 0x10000 && iVar6 == -1) {
            uVar19 = 0x80000000;
          }
          else {
            uVar19 = (int)uVar17 / iVar6;
          }
        }
        uVar2 = (uint)f33_fit_parameters.gain_upper;
        uVar14 = uVar17;
        if (iVar7 != 0) {
          if (uVar18 == 0x10000 && iVar7 == -1) {
            uVar14 = 0x80000000;
          }
          else {
            uVar14 = (int)uVar17 / iVar7;
          }
        }
        uVar10 = uVar17;
        if (iVar13 != 0) {
          if (uVar18 == 0x10000 && iVar13 == -1) {
            uVar10 = 0x80000000;
          }
          else {
            uVar10 = (int)uVar17 / iVar13;
          }
        }
        if (iVar15 != 0) {
          if (uVar18 == 0x10000 && iVar15 == -1) {
            uVar17 = 0x80000000;
          }
          else {
            uVar17 = (int)uVar17 / iVar15;
          }
        }
        uVar18 = (uint)f33_fit_parameters.gain_lower;
        if ((int)(uVar2 - uVar19) < 0 !=
            ((int)uVar19 < 0 && (int)uVar19 < 0 == (int)(uVar2 - uVar19) < 0)) {
          uVar19 = uVar2;
        }
        uVar12 = uVar18;
        if ((int)(uVar19 - uVar18) < 0 == ((int)uVar19 < 0 && -1 < (int)(uVar19 - uVar18))) {
          uVar12 = uVar19;
        }
        uStack_38 = (ushort)uVar12;
        if ((int)(uVar2 - uVar14) < 0 !=
            ((int)uVar14 < 0 && (int)uVar14 < 0 == (int)(uVar2 - uVar14) < 0)) {
          uVar14 = uVar2;
        }
        uVar19 = uVar18;
        if ((int)(uVar14 - uVar18) < 0 == ((int)uVar14 < 0 && -1 < (int)(uVar14 - uVar18))) {
          uVar19 = uVar14;
        }
        uStack_36 = (ushort)uVar19;
        if ((int)(uVar2 - uVar11) < 0 !=
            ((int)uVar11 < 0 && (int)uVar11 < 0 == (int)(uVar2 - uVar11) < 0)) {
          uVar11 = uVar2;
        }
        uVar19 = uVar18;
        if ((int)(uVar11 - uVar18) < 0 == ((int)uVar11 < 0 && -1 < (int)(uVar11 - uVar18))) {
          uVar19 = uVar11;
        }
        uStack_34 = (ushort)uVar19;
        if ((int)(uVar2 - uVar3) < 0 !=
            ((int)uVar3 < 0 && (int)uVar3 < 0 == (int)(uVar2 - uVar3) < 0)) {
          uVar3 = uVar2;
        }
        uVar11 = uVar18;
        if ((int)(uVar3 - uVar18) < 0 == ((int)uVar3 < 0 && -1 < (int)(uVar3 - uVar18))) {
          uVar11 = uVar3;
        }
        uStack_32 = (ushort)uVar11;
        if ((int)(uVar2 - uVar10) < 0 !=
            ((int)uVar10 < 0 && (int)uVar10 < 0 == (int)(uVar2 - uVar10) < 0)) {
          uVar10 = uVar2;
        }
        uVar11 = uVar18;
        if ((int)(uVar10 - uVar18) < 0 == ((int)uVar10 < 0 && -1 < (int)(uVar10 - uVar18))) {
          uVar11 = uVar10;
        }
        uStack_30 = (ushort)uVar11;
        if ((int)(uVar2 - uVar17) < 0 !=
            ((int)uVar17 < 0 && (int)uVar17 < 0 == (int)(uVar2 - uVar17) < 0)) {
          uVar17 = uVar2;
        }
        if ((int)(uVar17 - uVar18) < 0 == ((int)uVar17 < 0 && -1 < (int)(uVar17 - uVar18))) {
          uVar18 = uVar17;
        }
        uStack_2e = (ushort)uVar18;
        f33_six_channel_fit_work.first_center[0] =
             (ushort)((uint)f33_six_channel_fit_work.unsigned_min[0] +
                      (uint)f33_six_channel_fit_work.unsigned_max[0] >> 1);
        f33_six_channel_fit_work.first_center[1] =
             (ushort)((uint)f33_six_channel_fit_work.unsigned_min[1] +
                      (uint)f33_six_channel_fit_work.unsigned_max[1] >> 1);
        f33_six_channel_fit_work.first_center[2] =
             (ushort)((uint)f33_six_channel_fit_work.unsigned_min[2] +
                      (uint)f33_six_channel_fit_work.unsigned_max[2] >> 1);
        f33_six_channel_fit_work.first_center[3] =
             (ushort)((uint)f33_six_channel_fit_work.unsigned_min[3] +
                      (uint)f33_six_channel_fit_work.unsigned_max[3] >> 1);
        f33_six_channel_fit_work.first_center[4] =
             (ushort)((uint)f33_six_channel_fit_work.unsigned_min[4] +
                      (uint)f33_six_channel_fit_work.unsigned_max[4] >> 1);
        f33_six_channel_fit_work.first_center[5] =
             (ushort)((uint)f33_six_channel_fit_work.unsigned_min[5] +
                      (uint)f33_six_channel_fit_work.unsigned_max[5] >> 1);
        f33_six_channel_fit_work.state = '3';
      }
      f33_six_channel_fit_work.first_gain[0] = uStack_38;
      f33_six_channel_fit_work.first_gain[3] = uStack_32;
      f33_six_channel_fit_work.first_gain[4] = uStack_30;
      f33_six_channel_fit_work.first_gain[1] = uStack_36;
      f33_six_channel_fit_work.first_gain[2] = uStack_34;
      f33_six_channel_fit_work.first_gain[5] = uStack_2e;
    }
    else if (f33_six_channel_fit_work.state == '3') {
      puVar4 = ((undefined *)camry_host_ptr(0xfebeb800u));
      f33_step_signed_constant_fit_sweep((short)DAT_febe7d94);
    }
    else if (f33_six_channel_fit_work.state == 'D') {
      iVar8 = (int)f33_six_channel_fit_work.signed_max[0];
      iVar6 = (int)f33_six_channel_fit_work.signed_max[1];
      iVar24 = (int)f33_six_channel_fit_work.signed_max[2];
      iVar16 = (int)f33_six_channel_fit_work.signed_min[0];
      iVar15 = (int)f33_six_channel_fit_work.signed_min[1];
      iVar13 = (int)f33_six_channel_fit_work.signed_min[2];
      local_44 = f33_six_channel_fit_work.component_angle[0];
      uStack_42 = f33_six_channel_fit_work.component_angle[1];
      uStack_36 = f33_six_channel_fit_work.second_gain[1];
      uStack_40 = f33_six_channel_fit_work.component_angle[2];
      uStack_30 = f33_six_channel_fit_work.second_gain[4];
      uStack_2e = f33_six_channel_fit_work.second_gain[5];
      uStack_34 = f33_six_channel_fit_work.second_gain[2];
      uStack_32 = f33_six_channel_fit_work.second_gain[3];
      sStack_3e = (short)(((int)f33_six_channel_fit_work.signed_min[3] +
                          (int)f33_six_channel_fit_work.signed_max[3]) / 2);
      uStack_38 = f33_six_channel_fit_work.second_gain[0];
      sStack_3a = (short)(((int)f33_six_channel_fit_work.signed_min[5] +
                          (int)f33_six_channel_fit_work.signed_max[5]) / 2);
      iVar9 = (int)(short)((iVar8 - iVar16) / 2);
      sStack_3c = (short)(((int)f33_six_channel_fit_work.signed_min[4] +
                          (int)f33_six_channel_fit_work.signed_max[4]) / 2);
      iVar7 = (int)(short)((iVar6 - iVar15) / 2);
      iVar25 = (int)(short)((iVar24 - iVar13) / 2);
      iVar23 = (int)(short)(((int)f33_six_channel_fit_work.signed_max[3] -
                            (int)f33_six_channel_fit_work.signed_min[3]) / 2);
      iVar22 = (int)(short)(((int)f33_six_channel_fit_work.signed_max[4] -
                            (int)f33_six_channel_fit_work.signed_min[4]) / 2);
      iVar21 = (int)(short)(((int)f33_six_channel_fit_work.signed_max[5] -
                            (int)f33_six_channel_fit_work.signed_min[5]) / 2);
      if (((iVar9 < 1) || (iVar7 < 1)) ||
         ((iVar25 < 1 || (((iVar23 < 1 || (iVar22 < 1)) || (iVar21 < 1)))))) {
        f33_six_channel_fit_work.state = 'f';
        puVar4 = ((undefined *)camry_host_ptr(0xfebeb800u));
      }
      else {
        uVar3 = (uint)f33_fit_parameters.gain_upper;
        uVar19 = (uint)f33_fit_parameters.gain_lower;
        uVar18 = (uint)f33_fit_parameters.second_gain_numerator;
        uVar17 = uVar18 << 0xf;
        uVar11 = uVar17;
        if (iVar9 != 0) {
          if (uVar18 == 0x10000 && iVar9 == -1) {
            uVar11 = 0x80000000;
          }
          else {
            uVar11 = (int)uVar17 / iVar9;
          }
        }
        uVar14 = uVar17;
        if (iVar7 != 0) {
          if (uVar18 == 0x10000 && iVar7 == -1) {
            uVar14 = 0x80000000;
          }
          else {
            uVar14 = (int)uVar17 / iVar7;
          }
        }
        uVar2 = uVar17;
        if (iVar25 != 0) {
          if (uVar18 == 0x10000 && iVar25 == -1) {
            uVar2 = 0x80000000;
          }
          else {
            uVar2 = (int)uVar17 / iVar25;
          }
        }
        uVar10 = uVar17;
        if (iVar23 != 0) {
          if (uVar18 == 0x10000 && iVar23 == -1) {
            uVar10 = 0x80000000;
          }
          else {
            uVar10 = (int)uVar17 / iVar23;
          }
        }
        uVar12 = uVar17;
        if (iVar22 != 0) {
          if (uVar18 == 0x10000 && iVar22 == -1) {
            uVar12 = 0x80000000;
          }
          else {
            uVar12 = (int)uVar17 / iVar22;
          }
        }
        if (iVar21 != 0) {
          if (uVar18 == 0x10000 && iVar21 == -1) {
            uVar17 = 0x80000000;
          }
          else {
            uVar17 = (int)uVar17 / iVar21;
          }
        }
        if ((int)(uVar3 - uVar11) < 0 !=
            ((int)uVar11 < 0 && (int)uVar11 < 0 == (int)(uVar3 - uVar11) < 0)) {
          uVar11 = uVar3;
        }
        uVar18 = uVar19;
        if ((int)(uVar11 - uVar19) < 0 == ((int)uVar11 < 0 && -1 < (int)(uVar11 - uVar19))) {
          uVar18 = uVar11;
        }
        uStack_38 = (ushort)uVar18;
        if ((int)(uVar3 - uVar14) < 0 !=
            ((int)uVar14 < 0 && (int)uVar14 < 0 == (int)(uVar3 - uVar14) < 0)) {
          uVar14 = uVar3;
        }
        uVar18 = uVar19;
        if ((int)(uVar14 - uVar19) < 0 == ((int)uVar14 < 0 && -1 < (int)(uVar14 - uVar19))) {
          uVar18 = uVar14;
        }
        uStack_36 = (ushort)uVar18;
        if ((int)(uVar3 - uVar2) < 0 !=
            ((int)uVar2 < 0 && (int)uVar2 < 0 == (int)(uVar3 - uVar2) < 0)) {
          uVar2 = uVar3;
        }
        uVar18 = uVar19;
        if ((int)(uVar2 - uVar19) < 0 == ((int)uVar2 < 0 && -1 < (int)(uVar2 - uVar19))) {
          uVar18 = uVar2;
        }
        uStack_34 = (ushort)uVar18;
        if ((int)(uVar3 - uVar10) < 0 !=
            ((int)uVar10 < 0 && (int)uVar10 < 0 == (int)(uVar3 - uVar10) < 0)) {
          uVar10 = uVar3;
        }
        uVar18 = uVar19;
        if ((int)(uVar10 - uVar19) < 0 == ((int)uVar10 < 0 && -1 < (int)(uVar10 - uVar19))) {
          uVar18 = uVar10;
        }
        uStack_32 = (ushort)uVar18;
        if ((int)(uVar3 - uVar12) < 0 !=
            ((int)uVar12 < 0 && (int)uVar12 < 0 == (int)(uVar3 - uVar12) < 0)) {
          uVar12 = uVar3;
        }
        uVar18 = uVar19;
        if ((int)(uVar12 - uVar19) < 0 == ((int)uVar12 < 0 && -1 < (int)(uVar12 - uVar19))) {
          uVar18 = uVar12;
        }
        uStack_30 = (ushort)uVar18;
        if ((int)(uVar3 - uVar17) < 0 !=
            ((int)uVar17 < 0 && (int)uVar17 < 0 == (int)(uVar3 - uVar17) < 0)) {
          uVar17 = uVar3;
        }
        uStack_2e = f33_fit_parameters.gain_lower;
        if ((int)(uVar17 - uVar19) < 0 == ((int)uVar17 < 0 && -1 < (int)(uVar17 - uVar19))) {
          uStack_2e = (ushort)uVar17;
        }
        FUN_00070be0(iVar7,iVar9,&local_44);
        FUN_00070be0(iVar23,iVar25,&uStack_42);
        FUN_00070be0(iVar21,iVar22,&uStack_40);
        f33_six_channel_fit_work.state = 'U';
        puVar4 = ((undefined *)camry_host_ptr((uint32_t)(puVar5)));
      }
      f33_six_channel_fit_work.second_gain[5] = uStack_2e;
      f33_six_channel_fit_work.second_center[0] = (short)((iVar16 + iVar8) / 2);
      f33_six_channel_fit_work.second_center[1] = (short)((iVar15 + iVar6) / 2);
      f33_six_channel_fit_work.second_center[2] = (short)((iVar13 + iVar24) / 2);
      f33_six_channel_fit_work.second_gain[0] = uStack_38;
      f33_six_channel_fit_work.second_gain[1] = uStack_36;
      f33_six_channel_fit_work.second_center[3] = sStack_3e;
      f33_six_channel_fit_work.second_gain[2] = uStack_34;
      f33_six_channel_fit_work.second_gain[3] = uStack_32;
      f33_six_channel_fit_work.second_gain[4] = uStack_30;
      f33_six_channel_fit_work.second_center[4] = sStack_3c;
      f33_six_channel_fit_work.component_angle[0] = local_44;
      f33_six_channel_fit_work.second_center[5] = sStack_3a;
      f33_six_channel_fit_work.component_angle[1] = uStack_42;
      f33_six_channel_fit_work.component_angle[2] = uStack_40;
    }
    else if ((f33_six_channel_fit_work.state == 'U') || (f33_six_channel_fit_work.state == 'f')) {
      uVar20 = '\0';
    }
    else {
      f33_six_channel_fit_work.state = 'f';
    }
  }
  (*((short *)camry_host_ptr((uint32_t)((int)0xffffb166u + (int)camry_host_addr(puVar4))))) = sVar1;
  (*((uchar *)camry_host_ptr((uint32_t)((int)0xffffb160u + (int)camry_host_addr((puVar4 + 1)))))) = uVar20;
  return;
}



/* Set state6960=0 and active6961=5A only; does not erase prior fits before subsequent phase
   initialization. */

void f33_begin_six_channel_fit(void)

{
  f33_six_channel_fit_work.state = '\0';
  f33_six_channel_fit_work.active = 'Z';
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



/* Compare all27 halfwords of6A26 publication with6A84 retained candidate. Return0 identical,5A
   changed; not a calibration-health verdict. */

uint f33_compare_retained_fit_coefficients(void)

{
  uint uVar1;
  
  if (((((((f33_published_fit_coefficients.first_center[0] ==
            f33_retained_fit_coefficients.first_center[0]) &&
          (f33_published_fit_coefficients.first_center[1] ==
           f33_retained_fit_coefficients.first_center[1])) &&
         (f33_published_fit_coefficients.first_center[2] ==
          f33_retained_fit_coefficients.first_center[2])) &&
        ((f33_published_fit_coefficients.first_center[3] ==
          f33_retained_fit_coefficients.first_center[3] &&
         (f33_published_fit_coefficients.first_center[4] ==
          f33_retained_fit_coefficients.first_center[4])))) &&
       (f33_published_fit_coefficients.first_center[5] ==
        f33_retained_fit_coefficients.first_center[5])) &&
      (((((f33_published_fit_coefficients.first_gain[0] ==
           f33_retained_fit_coefficients.first_gain[0] &&
          (f33_published_fit_coefficients.first_gain[1] ==
           f33_retained_fit_coefficients.first_gain[1])) &&
         ((f33_published_fit_coefficients.first_gain[2] ==
           f33_retained_fit_coefficients.first_gain[2] &&
          (((f33_published_fit_coefficients.first_gain[3] ==
             f33_retained_fit_coefficients.first_gain[3] &&
            (f33_published_fit_coefficients.first_gain[4] ==
             f33_retained_fit_coefficients.first_gain[4])) &&
           (f33_published_fit_coefficients.first_gain[5] ==
            f33_retained_fit_coefficients.first_gain[5])))))) &&
        (((f33_published_fit_coefficients.second_center[0] ==
           f33_retained_fit_coefficients.second_center[0] &&
          (f33_published_fit_coefficients.second_center[1] ==
           f33_retained_fit_coefficients.second_center[1])) &&
         ((f33_published_fit_coefficients.second_center[2] ==
           f33_retained_fit_coefficients.second_center[2] &&
          ((((f33_published_fit_coefficients.second_center[3] ==
              f33_retained_fit_coefficients.second_center[3] &&
             (f33_published_fit_coefficients.second_center[4] ==
              f33_retained_fit_coefficients.second_center[4])) &&
            ((f33_published_fit_coefficients.second_center[5] ==
              f33_retained_fit_coefficients.second_center[5] &&
             (((f33_published_fit_coefficients.second_gain[0] ==
                f33_retained_fit_coefficients.second_gain[0] &&
               (f33_published_fit_coefficients.second_gain[1] ==
                f33_retained_fit_coefficients.second_gain[1])) &&
              (f33_published_fit_coefficients.second_gain[2] ==
               f33_retained_fit_coefficients.second_gain[2])))))) &&
           ((f33_published_fit_coefficients.second_gain[3] ==
             f33_retained_fit_coefficients.second_gain[3] &&
            (f33_published_fit_coefficients.second_gain[4] ==
             f33_retained_fit_coefficients.second_gain[4])))))))))) &&
       (f33_published_fit_coefficients.second_gain[5] ==
        f33_retained_fit_coefficients.second_gain[5])))) &&
     (((f33_published_fit_coefficients.component_angle[0] ==
        f33_retained_fit_coefficients.component_angle[0] &&
       (f33_published_fit_coefficients.component_angle[1] ==
        f33_retained_fit_coefficients.component_angle[1])) &&
      (f33_published_fit_coefficients.component_angle[2] ==
       f33_retained_fit_coefficients.component_angle[2])))) {
    uVar1 = 0;
  }
  else {
    uVar1 = 0x5a;
  }
  return uVar1;
}



/* Copy grouped centers/gains/angles6A84..6AB8 to6A26..6A5A after coherence admission; no physical
   calibration transformation. */

void f33_copy_retained_fit_coefficients(void)

{
  f33_published_fit_coefficients.first_center[0] = f33_retained_fit_coefficients.first_center[0];
  f33_published_fit_coefficients.first_center[1] = f33_retained_fit_coefficients.first_center[1];
  f33_published_fit_coefficients.first_center[2] = f33_retained_fit_coefficients.first_center[2];
  f33_published_fit_coefficients.first_center[3] = f33_retained_fit_coefficients.first_center[3];
  f33_published_fit_coefficients.first_center[4] = f33_retained_fit_coefficients.first_center[4];
  f33_published_fit_coefficients.first_center[5] = f33_retained_fit_coefficients.first_center[5];
  f33_published_fit_coefficients.first_gain[0] = f33_retained_fit_coefficients.first_gain[0];
  f33_published_fit_coefficients.first_gain[1] = f33_retained_fit_coefficients.first_gain[1];
  f33_published_fit_coefficients.first_gain[2] = f33_retained_fit_coefficients.first_gain[2];
  f33_published_fit_coefficients.first_gain[3] = f33_retained_fit_coefficients.first_gain[3];
  f33_published_fit_coefficients.first_gain[4] = f33_retained_fit_coefficients.first_gain[4];
  f33_published_fit_coefficients.first_gain[5] = f33_retained_fit_coefficients.first_gain[5];
  f33_published_fit_coefficients.second_center[0] = f33_retained_fit_coefficients.second_center[0];
  f33_published_fit_coefficients.second_center[1] = f33_retained_fit_coefficients.second_center[1];
  f33_published_fit_coefficients.second_center[2] = f33_retained_fit_coefficients.second_center[2];
  f33_published_fit_coefficients.second_center[3] = f33_retained_fit_coefficients.second_center[3];
  f33_published_fit_coefficients.second_center[4] = f33_retained_fit_coefficients.second_center[4];
  f33_published_fit_coefficients.second_center[5] = f33_retained_fit_coefficients.second_center[5];
  f33_published_fit_coefficients.second_gain[0] = f33_retained_fit_coefficients.second_gain[0];
  f33_published_fit_coefficients.second_gain[1] = f33_retained_fit_coefficients.second_gain[1];
  f33_published_fit_coefficients.second_gain[2] = f33_retained_fit_coefficients.second_gain[2];
  f33_published_fit_coefficients.second_gain[3] = f33_retained_fit_coefficients.second_gain[3];
  f33_published_fit_coefficients.second_gain[4] = f33_retained_fit_coefficients.second_gain[4];
  f33_published_fit_coefficients.second_gain[5] = f33_retained_fit_coefficients.second_gain[5];
  f33_published_fit_coefficients.component_angle[0] =
       f33_retained_fit_coefficients.component_angle[0];
  f33_published_fit_coefficients.component_angle[1] =
       f33_retained_fit_coefficients.component_angle[1];
  f33_published_fit_coefficients.component_angle[2] =
       f33_retained_fit_coefficients.component_angle[2];
  return;
}



/* Default published first centers/gains and second gains to8000, second centers0, angles2000.
   Retained source6A84 and marker remain independent. */

void f33_reset_published_fit_coefficients(void)

{
  f33_published_fit_coefficients.first_center[0] = 0x8000;
  f33_published_fit_coefficients.first_center[1] = 0x8000;
  f33_published_fit_coefficients.first_center[2] = 0x8000;
  f33_published_fit_coefficients.first_center[3] = 0x8000;
  f33_published_fit_coefficients.first_center[4] = 0x8000;
  f33_published_fit_coefficients.first_center[5] = 0x8000;
  f33_published_fit_coefficients.first_gain[0] = 0x8000;
  f33_published_fit_coefficients.first_gain[1] = 0x8000;
  f33_published_fit_coefficients.first_gain[2] = 0x8000;
  f33_published_fit_coefficients.first_gain[3] = 0x8000;
  f33_published_fit_coefficients.first_gain[4] = 0x8000;
  f33_published_fit_coefficients.first_gain[5] = 0x8000;
  f33_published_fit_coefficients.second_gain[0] = 0x8000;
  f33_published_fit_coefficients.second_gain[1] = 0x8000;
  f33_published_fit_coefficients.second_gain[2] = 0x8000;
  f33_published_fit_coefficients.second_gain[3] = 0x8000;
  f33_published_fit_coefficients.second_gain[4] = 0x8000;
  f33_published_fit_coefficients.second_gain[5] = 0x8000;
  f33_published_fit_coefficients.second_center[0] = 0;
  f33_published_fit_coefficients.second_center[1] = 0;
  f33_published_fit_coefficients.second_center[2] = 0;
  f33_published_fit_coefficients.second_center[3] = 0;
  f33_published_fit_coefficients.second_center[4] = 0;
  f33_published_fit_coefficients.second_center[5] = 0;
  f33_published_fit_coefficients.component_angle[0] = 0x2000;
  f33_published_fit_coefficients.component_angle[1] = 0x2000;
  f33_published_fit_coefficients.component_angle[2] = 0x2000;
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



/* Check foreground snapshot, not mutable worker arrays. Returns5A for accepted and0 otherwise.
   Exact configured unsigned bounds are full0..65535 and signed centers full-32768..32767; therefore
   not a meaningful physical calibration validation. */

uint f33_check_foreground_fit_bounds(void)

{
  uint uVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  
  uVar1 = 0;
  iVar6 = (int)((int)(int16_t)DAT_febe6566);
  iVar5 = (int)((int)(int16_t)DAT_febe6568);
  iVar4 = (int)((int)(int16_t)DAT_febe656a);
  iVar3 = (int)(short)f33_fit_parameters.candidate_bound_words[7];
  iVar2 = (int)(short)f33_fit_parameters.candidate_bound_words[6];
  if (((((((((f33_fit_parameters.candidate_bound_words[1] <= DAT_febe6542) &&
            (DAT_febe6542 <= f33_fit_parameters.candidate_bound_words[0])) &&
           (f33_fit_parameters.candidate_bound_words[1] <= DAT_febe6544)) &&
          ((DAT_febe6544 <= f33_fit_parameters.candidate_bound_words[0] &&
           (f33_fit_parameters.candidate_bound_words[1] <= DAT_febe6546)))) &&
         (DAT_febe6546 <= f33_fit_parameters.candidate_bound_words[0])) &&
        (((f33_fit_parameters.candidate_bound_words[1] <= DAT_febe6548 &&
          (DAT_febe6548 <= f33_fit_parameters.candidate_bound_words[0])) &&
         ((f33_fit_parameters.candidate_bound_words[1] <= DAT_febe654a &&
          (((DAT_febe654a <= f33_fit_parameters.candidate_bound_words[0] &&
            (f33_fit_parameters.candidate_bound_words[1] <= DAT_febe654c)) &&
           (DAT_febe654c <= f33_fit_parameters.candidate_bound_words[0])))))))) &&
       (((((f33_fit_parameters.candidate_bound_words[3] <= DAT_febe654e &&
           (DAT_febe654e <= f33_fit_parameters.candidate_bound_words[2])) &&
          ((f33_fit_parameters.candidate_bound_words[3] <= DAT_febe6550 &&
           (((DAT_febe6550 <= f33_fit_parameters.candidate_bound_words[2] &&
             (f33_fit_parameters.candidate_bound_words[3] <= DAT_febe6552)) &&
            ((DAT_febe6552 <= f33_fit_parameters.candidate_bound_words[2] &&
             (((f33_fit_parameters.candidate_bound_words[3] <= DAT_febe6554 &&
               (DAT_febe6554 <= f33_fit_parameters.candidate_bound_words[2])) &&
              (f33_fit_parameters.candidate_bound_words[3] <= DAT_febe6556)))))))))) &&
         ((DAT_febe6556 <= f33_fit_parameters.candidate_bound_words[2] &&
          (f33_fit_parameters.candidate_bound_words[3] <= DAT_febe6558)))) &&
        (DAT_febe6558 <= f33_fit_parameters.candidate_bound_words[2])))) &&
      (((((f33_fit_parameters.candidate_bound_words[5] <= DAT_febe655a &&
          (DAT_febe655a <= f33_fit_parameters.candidate_bound_words[4])) &&
         ((f33_fit_parameters.candidate_bound_words[5] <= DAT_febe655c &&
          ((((DAT_febe655c <= f33_fit_parameters.candidate_bound_words[4] &&
             (f33_fit_parameters.candidate_bound_words[5] <= DAT_febe655e)) &&
            (DAT_febe655e <= f33_fit_parameters.candidate_bound_words[4])) &&
           ((f33_fit_parameters.candidate_bound_words[5] <= DAT_febe6560 &&
            (DAT_febe6560 <= f33_fit_parameters.candidate_bound_words[4])))))))) &&
        (f33_fit_parameters.candidate_bound_words[5] <= DAT_febe6562)) &&
       (((DAT_febe6562 <= f33_fit_parameters.candidate_bound_words[4] &&
         (f33_fit_parameters.candidate_bound_words[5] <= DAT_febe6564)) &&
        ((DAT_febe6564 <= f33_fit_parameters.candidate_bound_words[4] &&
         (((iVar6 - iVar3 < 0 == (iVar6 < 0 != iVar3 < 0 && iVar3 < 0 == iVar6 - iVar3 < 0) &&
           (iVar6 - iVar2 < 0 != (iVar6 < 0 != iVar2 < 0 && iVar2 < 0 == iVar6 - iVar2 < 0) ||
            iVar6 == iVar2)) &&
          (iVar5 - iVar3 < 0 == (iVar5 < 0 != iVar3 < 0 && iVar3 < 0 == iVar5 - iVar3 < 0)))))))))))
     && ((((iVar5 - iVar2 < 0 != (iVar5 < 0 != iVar2 < 0 && iVar2 < 0 == iVar5 - iVar2 < 0) ||
            iVar5 == iVar2 &&
           (iVar4 - iVar3 < 0 == (iVar4 < 0 != iVar3 < 0 && iVar3 < 0 == iVar4 - iVar3 < 0))) &&
          (iVar4 - iVar2 < 0 != (iVar4 < 0 != iVar2 < 0 && iVar2 < 0 == iVar4 - iVar2 < 0) ||
           iVar4 == iVar2)) &&
         ((((iVar4 = (int)((int)(int16_t)DAT_febe656c),
            iVar4 - iVar3 < 0 == (iVar4 < 0 != iVar3 < 0 && iVar3 < 0 == iVar4 - iVar3 < 0) &&
            (iVar4 - iVar2 < 0 != (iVar4 < 0 != iVar2 < 0 && iVar2 < 0 == iVar4 - iVar2 < 0) ||
             iVar4 == iVar2)) &&
           ((((iVar4 = (int)((int)(int16_t)DAT_febe656e),
              iVar4 - iVar3 < 0 == (iVar4 < 0 != iVar3 < 0 && iVar3 < 0 == iVar4 - iVar3 < 0) &&
              (((iVar4 - iVar2 < 0 != (iVar4 < 0 != iVar2 < 0 && iVar2 < 0 == iVar4 - iVar2 < 0) ||
                 iVar4 == iVar2 &&
                (iVar4 = (int)((int)(int16_t)DAT_febe6570),
                iVar4 - iVar3 < 0 == (iVar4 < 0 != iVar3 < 0 && iVar3 < 0 == iVar4 - iVar3 < 0))) &&
               (iVar4 - iVar2 < 0 != (iVar4 < 0 != iVar2 < 0 && iVar2 < 0 == iVar4 - iVar2 < 0) ||
                iVar4 == iVar2)))) &&
             ((f33_fit_parameters.candidate_bound_words[9] <= DAT_febe6572 &&
              (DAT_febe6572 <= f33_fit_parameters.candidate_bound_words[8])))) &&
            (f33_fit_parameters.candidate_bound_words[9] <= DAT_febe6574)))) &&
          (((DAT_febe6574 <= f33_fit_parameters.candidate_bound_words[8] &&
            (f33_fit_parameters.candidate_bound_words[9] <= DAT_febe6576)) &&
           (DAT_febe6576 <= f33_fit_parameters.candidate_bound_words[8])))))))) {
    uVar1 = 0x5a;
  }
  return uVar1;
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
      FUN_00034ea4(0,(int)0xfffffff7);
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



/* State10; clear request-valid, means, stimulus, timer, sample count and both32-bit sums. Retain
   active6A61;343F0 sets it5A before calling here. */

void f33_initialize_mode600_stimulus_fit(void)

{
  f33_mode600_stimulus_fit_work.state = '\x10';
  f33_mode600_stimulus_fit_work.stimulus_valid = '\0';
  f33_mode600_stimulus_fit_work.positive_mean = 0;
  f33_mode600_stimulus_fit_work.negative_mean = 0;
  f33_mode600_stimulus_fit_work.stimulus = 0;
  f33_mode600_stimulus_fit_work.hold_count = 0;
  f33_mode600_stimulus_fit_work.sample_count = 0;
  f33_mode600_stimulus_fit_work.folded_angle_sum = 0;
  f33_mode600_stimulus_fit_work.signed_component_sum = 0;
  return;
}



/* Only clear6A61/6A62 and set state6A60=10. Preserve remaining means/stimulus/counters/sums.
   Existing mode0600 exit owner calls this and retains its name/contract. */

void f33_cancel_mode600_stimulus_fit(void)

{
  f33_mode600_stimulus_fit_work.active = '\0';
  f33_mode600_stimulus_fit_work.stimulus_valid = '\0';
  f33_mode600_stimulus_fit_work.state = '\x10';
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
  FUN_00034ea4(0,(int)0xfffffffa);
  f33_cancel_mode600_stimulus_fit();
  return;
}


