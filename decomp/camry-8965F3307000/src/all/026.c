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



void FUN_00099004(undefined4 param_1,undefined1 *param_2)

{
  param_2[1] = (char)((uint)param_1 >> 8);
  *param_2 = (char)param_1;
  param_2[2] = (char)((uint)param_1 >> 0x10);
  param_2[3] = (char)((uint)param_1 >> 0x18);
  return;
}



void FUN_000991b6(undefined4 *param_1,undefined4 *param_2)

{
  *param_2 = *param_1;
  return;
}


