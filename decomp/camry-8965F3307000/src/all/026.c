#include "common.h"


/* UDS routine wrapper: guards on the two valid routine-control subfunctions, delegates to the
   application-class routine helper with a fixed class literal, and diverts other subfunctions to
   the negative-response path (8B83C). Shape-verified. */

uint f33_diag_routine_class01_98034(byte param_1,uchar *param_2)

{
  uint uVar1;
  uchar uStack_b;
  ushort uStack_a;
  
  uStack_b = '\0';
  uStack_a = 0;
  if (param_1 < 2) {
    uVar1 = f33_diag_routine_application_class('\x01',8,0,&uStack_b,&uStack_a,param_2);
  }
  else {
    uVar1 = 0;
    FUN_0008b83c();
  }
  return uVar1;
}



undefined4
FUN_0009806a(undefined4 param_1,char param_2,undefined4 param_3,undefined4 param_4,
            undefined4 param_5)

{
  undefined4 uVar1;
  
  if (param_2 == '\0') {
    uVar1 = FUN_0008bc4a(param_1, 0x40, param_3, 0x31, ((uchar *)camry_host_ptr((uint32_t)(param_5))));
  }
  else {
    uVar1 = 0;
    FUN_0008b83c();
  }
  return uVar1;
}



/* UDS routine wrapper: guards on the two valid routine-control subfunctions, delegates to the
   application-class routine helper with a fixed class literal, and diverts other subfunctions to
   the negative-response path (8B83C). Shape-verified. */

uint f33_diag_routine_class01_98094(byte param_1,uchar *param_2,ushort *param_3,uchar *param_4)

{
  uint uVar1;
  
  if (param_1 < 2) {
    uVar1 = f33_diag_routine_application_class('\x01',10,0,param_2,param_3,param_4);
  }
  else {
    uVar1 = 0;
    FUN_0008b83c();
  }
  return uVar1;
}



/* UDS routine wrapper: guards on the two valid routine-control subfunctions, delegates to the
   application-class routine helper with a fixed class literal, and diverts other subfunctions to
   the negative-response path (8B83C). Shape-verified. */

uint f33_diag_routine_class01_980c0(byte param_1,uchar *param_2)

{
  uint uVar1;
  uchar uStack_b;
  ushort uStack_a;
  
  uStack_b = '\0';
  uStack_a = 0;
  if (param_1 < 2) {
    uVar1 = f33_diag_routine_application_class('\x01',0xb,0,&uStack_b,&uStack_a,param_2);
  }
  else {
    uVar1 = 0;
    FUN_0008b83c();
  }
  return uVar1;
}



/* UDS routine wrapper: guards on the two valid routine-control subfunctions, delegates to the
   application-class routine helper with a fixed class literal, and diverts other subfunctions to
   the negative-response path (8B83C). Shape-verified. */

uint f33_diag_routine_class01_980f6(byte param_1,uchar *param_2)

{
  uint uVar1;
  uchar uStack_b;
  ushort uStack_a;
  
  uStack_b = '\0';
  uStack_a = 0;
  if (param_1 < 2) {
    uVar1 = f33_diag_routine_application_class('\x01',0xc,0,&uStack_b,&uStack_a,param_2);
  }
  else {
    uVar1 = 0;
    FUN_0008b83c();
  }
  return uVar1;
}



/* UDS routine wrapper: guards on the two valid routine-control subfunctions, delegates to the
   application-class routine helper with a fixed class literal, and diverts other subfunctions to
   the negative-response path (8B83C). Shape-verified. */

uint f33_diag_routine_class01_9812c(byte param_1,uchar *param_2)

{
  uint uVar1;
  uchar uStack_b;
  ushort uStack_a;
  
  uStack_b = '\0';
  uStack_a = 0;
  if (param_1 < 2) {
    uVar1 = f33_diag_routine_application_class('\x01',0xd,0,&uStack_b,&uStack_a,param_2);
  }
  else {
    uVar1 = 0;
    FUN_0008b83c();
  }
  return uVar1;
}



/* UDS routine wrapper: guards on the two valid routine-control subfunctions, delegates to the
   application-class routine helper with a fixed class literal, and diverts other subfunctions to
   the negative-response path (8B83C). Shape-verified. */

uint f33_diag_routine_class01_98162(byte param_1,uchar *param_2)

{
  uint uVar1;
  uchar uStack_b;
  ushort uStack_a;
  
  uStack_b = '\0';
  uStack_a = 0;
  if (param_1 < 2) {
    uVar1 = f33_diag_routine_application_class('\x01',0xe,0,&uStack_b,&uStack_a,param_2);
  }
  else {
    uVar1 = 0;
    FUN_0008b83c();
  }
  return uVar1;
}



/* UDS routine wrapper: guards on the two valid routine-control subfunctions, delegates to the
   application-class routine helper with a fixed class literal, and diverts other subfunctions to
   the negative-response path (8B83C). Shape-verified. */

uint f33_diag_routine_class01_98198(byte param_1,uchar *param_2)

{
  uint uVar1;
  uchar uStack_b;
  ushort uStack_a;
  
  uStack_b = '\0';
  uStack_a = 0;
  if (param_1 < 2) {
    uVar1 = f33_diag_routine_application_class('\x01',0xf,0,&uStack_b,&uStack_a,param_2);
  }
  else {
    uVar1 = 0;
    FUN_0008b83c();
  }
  return uVar1;
}



/* UDS routine wrapper: guards on the two valid routine-control subfunctions, delegates to the
   application-class routine helper with a fixed class literal, and diverts other subfunctions to
   the negative-response path (8B83C). Shape-verified. */

uint f33_diag_routine_class01_981ce(byte param_1,uchar *param_2)

{
  uint uVar1;
  uchar uStack_b;
  ushort uStack_a;
  
  uStack_b = '\0';
  uStack_a = 0;
  if (param_1 < 2) {
    uVar1 = f33_diag_routine_application_class('\x01',0x10,0,&uStack_b,&uStack_a,param_2);
  }
  else {
    uVar1 = 0;
    FUN_0008b83c();
  }
  return uVar1;
}



/* UDS routine wrapper: guards on the two valid routine-control subfunctions, delegates to the
   application-class routine helper with a fixed class literal, and diverts other subfunctions to
   the negative-response path (8B83C). Shape-verified. */

uint f33_diag_routine_class01_98206(byte param_1,uchar *param_2)

{
  uint uVar1;
  uchar uStack_b;
  ushort uStack_a;
  
  uStack_b = '\0';
  uStack_a = 0;
  if (param_1 < 2) {
    uVar1 = f33_diag_routine_application_class('\x01',0x11,0,&uStack_b,&uStack_a,param_2);
  }
  else {
    uVar1 = 0;
    FUN_0008b83c();
  }
  return uVar1;
}



/* UDS routine wrapper: guards on the two valid routine-control subfunctions, delegates to the
   application-class routine helper with a fixed class literal, and diverts other subfunctions to
   the negative-response path (8B83C). Shape-verified. */

uint f33_diag_routine_class01_9823e(byte param_1,uchar *param_2)

{
  uint uVar1;
  uchar uStack_b;
  ushort uStack_a;
  
  uStack_b = '\0';
  uStack_a = 0;
  if (param_1 < 2) {
    uVar1 = f33_diag_routine_application_class('\x01',0x12,0,&uStack_b,&uStack_a,param_2);
  }
  else {
    uVar1 = 0;
    FUN_0008b83c();
  }
  return uVar1;
}



/* UDS routine wrapper: guards on the two valid routine-control subfunctions, delegates to the
   application-class routine helper with a fixed class literal, and diverts other subfunctions to
   the negative-response path (8B83C). Shape-verified. */

uint f33_diag_routine_class02_98276(byte param_1,uchar *param_2)

{
  uint uVar1;
  uchar uStack_b;
  ushort uStack_a;
  
  uStack_b = '\0';
  uStack_a = 0;
  if (param_1 < 2) {
    uVar1 = f33_diag_routine_application_class('\x02',0xf,0,&uStack_b,&uStack_a,param_2);
  }
  else {
    uVar1 = 0;
    FUN_0008b83c();
  }
  return uVar1;
}



/* UDS routine wrapper: guards on the two valid routine-control subfunctions, delegates to the
   application-class routine helper with a fixed class literal, and diverts other subfunctions to
   the negative-response path (8B83C). Shape-verified. */

uint f33_diag_routine_class02_982ac(byte param_1,uchar *param_2)

{
  uint uVar1;
  uchar uStack_b;
  ushort uStack_a;
  
  uStack_b = '\0';
  uStack_a = 0;
  if (param_1 < 2) {
    uVar1 = f33_diag_routine_application_class('\x02',0x12,0,&uStack_b,&uStack_a,param_2);
  }
  else {
    uVar1 = 0;
    FUN_0008b83c();
  }
  return uVar1;
}



undefined4 FUN_00098590(short param_1,undefined4 param_2,undefined1 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  
  if (param_1 == 0xf) {
    uVar1 = f33_diag_routine_class02_98276(param_3, ((uchar *)camry_host_ptr((uint32_t)(param_4))));
  }
  else {
    uVar1 = 0;
    if (param_1 == 0x12) {
      uVar1 = f33_diag_routine_class02_982ac(param_3, ((uchar *)camry_host_ptr((uint32_t)(param_4))));
    }
  }
  return uVar1;
}



void FUN_00098712(undefined1 param_1)

{
  int iVar1;
  
  iVar1 = FUN_000955bc();
  if (iVar1 == 1) {
    FUN_00098850(2,param_1,0xffff,0xffff);
    FUN_000955b6(0);
  }
  f33_dcm_invalidate_queued_event('\x16','\0');
  FUN_0009560e(1);
  return;
}



uint FUN_0009874a(char param_1,F33DcmMessageContext *param_2)

{
  uint uVar1;
  
  if (param_1 == '\0') {
    uVar1 = f33_dcm_begin_proprietary_event_read(param_2,'\x01');
  }
  else {
    uVar1 = 0;
    FUN_00098712(1);
  }
  return uVar1;
}



uint FUN_0009876c(char param_1,F33DcmMessageContext *param_2)

{
  uint uVar1;
  
  if (param_1 == '\0') {
    uVar1 = f33_dcm_begin_proprietary_event_read(param_2,'\x02');
  }
  else {
    uVar1 = 0;
    FUN_00098712(2);
  }
  return uVar1;
}



uint FUN_0009878e(char param_1,F33DcmMessageContext *param_2)

{
  uint uVar1;
  
  if (param_1 == '\0') {
    uVar1 = f33_dcm_begin_proprietary_event_read(param_2,'\x03');
  }
  else {
    uVar1 = 0;
    FUN_00098712(3);
  }
  return uVar1;
}



uint FUN_000987b0(char param_1,F33DcmMessageContext *param_2)

{
  uint uVar1;
  
  if (param_1 == '\0') {
    uVar1 = f33_dcm_begin_proprietary_event_read(param_2,'\x11');
  }
  else {
    uVar1 = 0;
    FUN_00098712(0x11);
  }
  return uVar1;
}



uint FUN_000987d6(char param_1,F33DcmMessageContext *param_2)

{
  uint uVar1;
  
  if (param_1 == '\0') {
    uVar1 = f33_dcm_begin_proprietary_event_read(param_2,'\x12');
  }
  else {
    uVar1 = 0;
    FUN_00098712(0x12);
  }
  return uVar1;
}



uint FUN_000987fc(char param_1,F33DcmMessageContext *param_2)

{
  uint uVar1;
  
  if (param_1 == '\0') {
    uVar1 = f33_dcm_begin_proprietary_event_read(param_2,'\x13');
  }
  else {
    uVar1 = 0;
    FUN_00098712(0x13);
  }
  return uVar1;
}



void FUN_00098822(void)

{
  uint32_t puVar1;
  int iVar2;
  uchar uStack_5;
  
  puVar1 = 0xfebeb800u;
  uStack_5 = '\0';
  iVar2 = FUN_000985bc(&uStack_5);
  if (((iVar2 != 0) && (iVar2 != 10)) && (uStack_5 != '\x14')) {
    f33_dcm_report_negative_or_pending(((F33DcmMessageContext *)camry_host_ptr((uint32_t)(puVar1 + -0x59cc))),uStack_5);
  }
  return;
}



uint FUN_00098850(uchar param_1,uchar param_2,ushort param_3,ushort param_4)

{
  uint uVar1;
  
  if (param_1 == '\x02') {
    f33_fill_constant_block_8de1a();
    uVar1 = 0;
  }
  else {
    uVar1 = f33_begin_proprietary_event_selection(param_1,param_2,param_3,param_4);
  }
  return uVar1;
}



/* Sequential initializer chain: 5 unconditional calls and no other statements; shape-verified. The
   called sequence is the function's entire behavior; chain family members differ in callee sets. */

void f33_run_init_chain_9887c(void)

{
  f33_dcm_reset_timer_slots();
  f33_dcm_reset_event_ring();
  FUN_00095590();
  FUN_00090ee6();
  f33_run_init_chain_91ffa();
  return;
}



/* Only when5E50==A5 run DCM worker91FBE, timers98AE4 and event queue98946 in that order. SecOC
   processing belongs upstream inside7A254. Timer expiry uses remaining<quantum, and the queue
   worker snapshots its entry event count. DCM main/timers/event queue gated by5E50==A5; not SecOC.
   Timer equality waits another invocation and queue drain snapshots entry count. Static exact
   instructions/dataflow. */

void f33_dcm_foreground_cycle(void)

{
  if (f33_dcm_foreground_enabled == 0xa5) {
    FUN_00091fbe();
    f33_dcm_advance_software_timers();
    f33_dcm_dispatch_entry_event_generation();
  }
  return;
}



/* Constant source: return 1; shape-classified from the canonical corpus. Callers receive this
   literal directly; its meaning is not recovered. */

undefined4 f33_return_const_1_988e4(void)

{
  return 1;
}



undefined4 FUN_000988e8(int param_1)

{
  undefined4 uVar1;
  
  if (param_1 == 0) {
    uVar1 = 1;
  }
  else {
    uVar1 = f33_return_const_1_988e4();
  }
  return uVar1;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_98900(void)

{
  return;
}



void FUN_00098902(void)

{
  int iVar1;
  
  iVar1 = FUN_00091e2c();
  if ((iVar1 == 1) && (iVar1 = FUN_0009177c(), iVar1 == 1)) {
    FUN_000955e4();
  }
  return;
}



void FUN_0009891e(char param_1)

{
  if (param_1 == '\x01') {
    FUN_00091e2c();
  }
  else {
    FUN_00091e52();
  }
  return;
}



/* Constant source: return 0; shape-classified from the canonical corpus. Callers receive this
   literal directly; its meaning is not recovered. */

undefined4 f33_return_const_0_98936(void)

{
  return 0;
}



/* Return0 for IDs00..2B or EB..F1 using configured extended count7; return1 otherwise. Validation
   does not check whether the selected ROM callback pointer is nonnull. */

uint f33_dcm_validate_event_id(uchar event_id)

{
  uint uVar1;
  uint uVar2;
  
  uVar1 = (uint)event_id;
  uVar2 = 1;
  if ((uVar1 < 0x2c) ||
     ((0xea < uVar1 && ((int)(uVar1 - (f33_dcm_extended_event_count + 0xeb)) < 0)))) {
    uVar2 = 0;
  }
  return uVar2;
}



/* Validate low8 event ID, append one byte to the31-slot counted ring and wrap producer30 to0.
   Return0 accepted,1 invalid,2 full. Duplicates are retained; tombstones still occupy capacity. No
   inline callback or init-marker gate. */

uint f33_dcm_enqueue_event(uchar event_id)

{
  byte bVar1;
  byte bVar2;
  uint32_t puVar3;
  uint uVar4;
  char cVar5;
  uint uVar6;
  
  puVar3 = 0xfebeb800u;
  uVar6 = 1;
  uVar4 = f33_dcm_validate_event_id(event_id);
  if (uVar4 == 0) {
    thunk_FUN_0006a45e();
    bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x59ad)))));
    if (bVar1 < 0x1f) {
      bVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x59af)))));
      uVar4 = (uint)bVar2;
      uVar6 = 0;
      if (uVar4 < 0x1f) {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(uVar4 - 0x59ac))))) = event_id;
      }
      cVar5 = '\0';
      if (uVar4 < 0x1e) {
        cVar5 = bVar2 + 1;
      }
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x59af))))) = cVar5;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x59ad))))) = bVar1 + 1;
    }
    else {
      uVar6 = 2;
    }
    thunk_FUN_0006a4c4();
  }
  return uVar6;
}



/* Scan current occupied slots from consumer and replace matching bytes withFF under the existing
   critical pair. Only first_only==1 stops at first match; other values invalidate all. Return0
   matched,1 invalid ID,3 absent. Indices and occupancy are unchanged. */

uint f33_dcm_invalidate_queued_event(uchar event_id,uchar first_only)

{
  byte bVar1;
  bool bVar2;
  uint32_t puVar3;
  uint uVar4;
  uint uVar5;
  byte bVar6;
  
  puVar3 = 0xfebeb800u;
  bVar6 = 0;
  bVar2 = false;
  uVar5 = 1;
  uVar4 = f33_dcm_validate_event_id(event_id);
  if (uVar4 == 0) {
    uVar5 = 3;
    thunk_FUN_0006a45e();
    bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x59ad)))));
    uVar4 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x59ae)))));
    do {
      if (bVar1 <= bVar6) break;
      bVar6 = bVar6 + 1;
      if ((uVar4 < 0x1f) && (event_id == (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(uVar4 - 0x59ac))))))) {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(uVar4 - 0x59ac))))) = 0xff;
        if (first_only == '\x01') {
          bVar2 = true;
        }
        uVar5 = 0;
      }
      if (uVar4 < 0x1e) {
        uVar4 = uVar4 + 1 & 0xff;
      }
      else {
        uVar4 = 0;
      }
    } while (!bVar2);
    thunk_FUN_0006a4c4();
  }
  return uVar5;
}



/* Forward low8 event ID to989EC; callers discard enqueue status. No retry, coalescing or callback
   execution is added. */

void f33_dcm_post_service_event(uchar event_id)

{
  f33_dcm_enqueue_event(event_id);
  return;
}



/* Forward low8 arguments to98A44; cancellation tombstones entries without reclaiming occupied
   slots. */

void f33_dcm_cancel_service_events(uchar event_id,uchar first_only)

{
  f33_dcm_invalidate_queued_event(event_id,first_only);
  return;
}



/* Zero remaining and active fields for nine8-byte software timers; padding is untouched. */

void f33_dcm_reset_timer_slots(void)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = 0;
  do {
    uVar1 = uVar2 + 1;
    f33_dcm_software_timers[uVar2].remaining = 0;
    f33_dcm_software_timers[uVar2].active = '\0';
    uVar2 = uVar1;
  } while (uVar1 < 9);
  return;
}



/* For low8 slot<9 write remaining=(duration+quantum5-1) modulo32 and active1 under the existing
   priority-mask pair. Rearming overwrites rather than accumulates; zero duration arms remaining4.
    */

void f33_dcm_arm_software_timer(uchar timer_slot,uint duration)

{
  uint32_t puVar1;
  uint32_t puVar2;
  uint uVar3;
  
  uVar3 = (uint)timer_slot;
  puVar1 = 0xfebeb800u;
  puVar2 = 0x23dfcu;
  if (uVar3 < 9) {
    thunk_FUN_0006a45e();
    (*((uint *)camry_host_ptr((uint32_t)(puVar1 + uVar3 * 8 + -0x598c)))) = (*((int *)camry_host_ptr((uint32_t)(puVar2 + 0x2cf0)))) + -1 + duration;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(uVar3 * 8 + -0x5988))))) = 1;
    thunk_FUN_0006a4c4();
  }
  return;
}



/* For low8 slot<9 clear only active under the existing priority-mask pair. Leave remaining and
   already queued events unchanged; inactive or invalid slots have no callback. */

void f33_dcm_cancel_software_timer(uchar timer_slot)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (timer_slot < 9) {
    thunk_FUN_0006a45e();
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)((uint)timer_slot * 8 + -0x5988))))) = 0;
    thunk_FUN_0006a4c4();
  }
  return;
}



/* Far-call trampoline: prepare {lp},0 / jarl 0x6A45E / dispose 0,{lp},lp; byte-verified against the
   exact image. Forwards with registers and stack unchanged; marked as a thunk. Forwarding shape
   machine-verified; target semantics not recovered. */

void thunk_FUN_0006a45e(void)

{
  FUN_0006a45e();
  return;
}



/* Far-call trampoline: prepare {lp},0 / jarl 0x6A4C4 / dispose 0,{lp},lp; byte-verified against the
   exact image. Forwards with registers and stack unchanged; marked as a thunk. Forwarding shape
   machine-verified; target semantics not recovered. */

void thunk_FUN_0006a4c4(void)

{
  FUN_0006a4c4();
  return;
}



/* Constant source: return 5; shape-classified from the canonical corpus. Callers receive this
   literal directly; its meaning is not recovered. */

undefined4 f33_return_const_5_98eee(void)

{
  return 5;
}



void FUN_00098f4c(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = 0;
  do {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5ebcu + (uint32_t)(iVar3) * 1u)))) = 0;
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -7;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  DAT_febe5ec4 = 1;
  DAT_febe5ec5 = 0;
  DAT_febe5ec6 = 0;
  return;
}



void FUN_00098f6e(int param_1,char param_2,undefined1 param_3)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  if (param_2 == 'Z') {
    DAT_febe5ebc = 0xff;
    iVar3 = 1;
    do {
      iVar2 = iVar3 + 1;
      iVar1 = iVar3 + -7;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5ebcu + (uint32_t)(iVar3) * 1u)))) = (*((undefined1 *)camry_host_ptr((uint32_t)(iVar3 + param_1))));
      iVar3 = iVar2;
    } while (((iVar1 < 0) || (iVar2 < 0)));
    return;
  }
  DAT_febe5ebc = 0xfe;
  iVar3 = 2;
  DAT_febe5ebd = param_3;
  do {
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -7;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5ebcu + (uint32_t)(iVar3) * 1u)))) = (*((undefined1 *)camry_host_ptr((uint32_t)(iVar3 + param_1))));
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  return;
}



undefined4 FUN_00098fba(undefined4 param_1,short param_2)

{
  int iVar1;
  int iVar2;
  int iVar3;
  undefined4 uVar4;
  undefined1 local_c [4];
  undefined1 uStack_8;
  undefined1 uStack_7;
  undefined1 uStack_6;
  undefined1 uStack_5;
  
  uVar4 = 0xa5;
  iVar3 = 0;
  do {
    local_c[iVar3] = 0;
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -7;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  if (param_2 == 8) {
    uStack_8 = 1;
    uStack_6 = 1;
    uVar4 = 0x5a;
    local_c[2] = 0;
    uStack_7 = 0x32;
    uStack_5 = 0x11;
  }
  FUN_00098f6e(camry_host_addr(local_c), uVar4, 0x21);
  return 0x5a;
}



void FUN_00099004(undefined4 param_1,undefined1 *param_2)

{
  param_2[1] = (char)((uint)param_1 >> 8);
  *param_2 = (char)param_1;
  param_2[2] = (char)((uint)param_1 >> 0x10);
  param_2[3] = (char)((uint)param_1 >> 0x18);
  return;
}



undefined4 FUN_0009901a(int param_1,short param_2)

{
  int iVar1;
  int iVar2;
  int iVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  uint uVar6;
  undefined1 local_18 [4];
  undefined1 auStack_14 [4];
  
  uVar5 = 0xa5;
  uVar4 = 0x21;
  iVar3 = 0;
  do {
    local_18[iVar3] = 0;
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -7;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  if (param_2 == 8) {
    uVar6 = (uint)(*((byte *)camry_host_ptr((uint32_t)(param_1 + 1))));
    if (uVar6 < 5) {
      uVar5 = 0x5a;
      local_18[1] = 0;
      FUN_00099004(*(undefined4 *)(((undefined *)camry_host_ptr(0x2b22cu)) + uVar6 * 8),auStack_14);
      ((void)((&PTR_DAT_0002b228)[uVar6 * 2]), thunk_FUN_00082288());
    }
    else {
      uVar4 = 0x22;
    }
  }
  FUN_00098f6e(camry_host_addr(local_18), uVar5, uVar4);
  return 0x5a;
}



void FUN_00099126(int param_1,uint param_2,int param_3)

{
  uint uVar1;
  
  for (uVar1 = 0; uVar1 < (param_2 & 0xff); uVar1 = uVar1 + 1) {
    (*((undefined1 *)camry_host_ptr((uint32_t)(uVar1 + param_3)))) = (*((undefined1 *)camry_host_ptr((uint32_t)(uVar1 + param_1))));
  }
  ((void)((param_2 & 0xff) + param_1), thunk_FUN_00082288());
  return;
}



void FUN_000991b6(undefined4 *param_1,undefined4 *param_2)

{
  *param_2 = *param_1;
  return;
}



uint FUN_00099226(int param_1,uint param_2)

{
  int iVar1;
  uint uVar2;
  
  DCRA1CTL = '\0';
  DCRA1COUT = 0xffffffff;
  uVar2 = 0;
  while (uVar2 < param_2 >> 2) {
    iVar1 = uVar2 * 4;
    uVar2 = uVar2 + 1;
    DCRA1CIN = (*((uint *)camry_host_ptr((uint32_t)(iVar1 + param_1))));
  }
  ((void)(uVar2 * 4 + param_1), thunk_FUN_00082288());
  uVar2 = DCRA1COUT;
  return ~uVar2;
}



undefined4 FUN_0009930e(int param_1,short param_2)

{
  int iVar1;
  int iVar2;
  byte bVar3;
  byte bVar4;
  undefined4 uVar5;
  undefined4 uVar6;
  int iVar7;
  undefined1 local_c [8];
  
  uVar5 = 0xa5;
  uVar6 = 0x21;
  iVar7 = 0;
  do {
    local_c[iVar7] = 0;
    iVar2 = iVar7 + 1;
    iVar1 = iVar7 + -7;
    iVar7 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  if (param_2 == 8) {
    if ((*((char *)camry_host_ptr((uint32_t)(param_1 + 2)))) == '\0') {
      bVar3 = (*((byte *)camry_host_ptr((uint32_t)(param_1 + 3))));
      bVar4 = (*((byte *)camry_host_ptr((uint32_t)(param_1 + 1))));
      if ((bVar3 < 2) && ((bVar3 == 1 || ((bVar4 & 1) == 0)))) {
        if ((bVar4 & 3) == 0) {
          uVar6 = 0x27;
        }
        else {
          uVar5 = 0x5a;
          if ((bVar4 >> 1 & 1) != 0) {
            DAT_febe5ec5 = bVar3;
          }
          if ((bVar4 & 1) != 0) {
            DAT_febe5ec4 = bVar3;
          }
        }
      }
      else {
        uVar6 = 0x26;
      }
    }
    else {
      uVar6 = 0x28;
    }
  }
  FUN_00098f6e(camry_host_addr(local_c), uVar5, uVar6);
  return 0x5a;
}



undefined4 FUN_00099388(int param_1,short param_2)

{
  int iVar1;
  int iVar2;
  undefined1 uVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  int iVar6;
  undefined1 local_c [8];
  
  uVar4 = 0xa5;
  uVar5 = 0x21;
  iVar6 = 0;
  do {
    local_c[iVar6] = 0;
    iVar2 = iVar6 + 1;
    iVar1 = iVar6 + -7;
    iVar6 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  if (param_2 == 8) {
    if ((*((char *)camry_host_ptr((uint32_t)(param_1 + 2)))) == '\0') {
      uVar3 = DAT_febe5ec4;
      if (((*((char *)camry_host_ptr((uint32_t)(param_1 + 1)))) == '\x01') ||
         (uVar3 = DAT_febe5ec5, (*((char *)camry_host_ptr((uint32_t)(param_1 + 1)))) == '\x02')) {
        uVar4 = 0x5a;
        local_c[3] = uVar3;
      }
      else {
        uVar5 = 0x27;
      }
    }
    else {
      uVar5 = 0x28;
    }
  }
  FUN_00098f6e(camry_host_addr(local_c), uVar4, uVar5);
  return 0x5a;
}



undefined4 FUN_00099414(int param_1,short param_2)

{
  int iVar1;
  int iVar2;
  int iVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  undefined1 local_14 [8];
  
  uVar4 = 0xa5;
  uVar5 = 0x21;
  iVar3 = 0;
  do {
    local_14[iVar3] = 0;
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -7;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  if (param_2 == 8) {
    if (((*((char *)camry_host_ptr((uint32_t)(param_1 + 1)))) == '\0') && ((*((char *)camry_host_ptr((uint32_t)(param_1 + 3)))) == '\0')) {
      if (((*((byte *)camry_host_ptr((uint32_t)(param_1 + 2)))) < 2) && ((*((byte *)camry_host_ptr((uint32_t)(param_1 + 4)))) < 2)) {
        if ((*((byte *)camry_host_ptr((uint32_t)(param_1 + 4)))) == 1) {
          uVar4 = 0x5a;
          if ((*((byte *)camry_host_ptr((uint32_t)(param_1 + 2)))) == 0) {
            FUN_000993f0();
          }
        }
        else {
          uVar5 = 0x23;
        }
      }
      else {
        uVar5 = 0x26;
      }
    }
    else {
      uVar5 = 0x28;
    }
  }
  FUN_00098f6e(camry_host_addr(local_14), uVar4, uVar5);
  return 0x5a;
}


