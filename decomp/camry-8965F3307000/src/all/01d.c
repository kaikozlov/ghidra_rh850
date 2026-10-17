#include "common.h"


undefined4 FUN_00074040(undefined2 param_1,undefined4 param_2)

{
  int iVar1;
  undefined4 uVar2;
  
  uVar2 = 1;
  iVar1 = FUN_00074494((uint)(ushort)param_1, ((void *)camry_host_ptr((uint32_t)(param_2))));
  if (iVar1 == 0) {
    uVar2 = FUN_00072e2e((int)0xb9145954, param_1, ((void *)camry_host_ptr((uint32_t)(param_2))), 0);
  }
  return uVar2;
}



undefined4 FUN_00074074(undefined2 param_1)

{
  int iVar1;
  undefined4 uVar2;
  
  uVar2 = 1;
  iVar1 = FUN_000744de((uint)(ushort)param_1);
  if (iVar1 == 0) {
    uVar2 = FUN_00072e2e((int)0xb6e96af1,param_1,0,0);
  }
  return uVar2;
}



undefined4 FUN_0007409e(undefined2 param_1)

{
  int iVar1;
  undefined4 uVar2;
  
  uVar2 = 1;
  iVar1 = FUN_0007451e((uint)(ushort)param_1);
  if (iVar1 == 0) {
    uVar2 = FUN_00072e2e(0x1c646989,param_1,0,0);
  }
  return uVar2;
}



undefined4 FUN_000740c8(undefined2 param_1)

{
  int iVar1;
  undefined4 uVar2;
  
  uVar2 = 1;
  iVar1 = FUN_00074568((uint)(ushort)param_1);
  if (iVar1 == 0) {
    uVar2 = FUN_00072e2e((int)0x9c1f8709,param_1,0,0);
  }
  return uVar2;
}



void FUN_000740f2(void)

{
  int iVar1;
  
  iVar1 = f33_return_const_0_745b8();
  if (iVar1 == 0) {
    FUN_00072e2e(0x2ece2284,0,0,0);
  }
  return;
}



/* Require service14 and initialized-service gates. Enter service guards and classify direct mode.
   Mode0 selects callback766F4, services scheduler and74790; active direct mode skips ordinary
   scheduling. Publish classification predicate via79C42 and finish guards. Lower hardware
   completion is not inferred. */

void f33_nvm_service_application_cycle(void)

{
  uint uVar1;
  
  uVar1 = f33_nvm_driver_gate_rejected(0x14);
  if ((uVar1 == 0) && (uVar1 = f33_nvm_service_uninitialized(), uVar1 == 0)) {
    f33_nvm_enter_service_guard();
    uVar1 = f33_nvm_reconcile_probe_mode();
    if (uVar1 == 0) {
      f33_nvm_select_service_poll('\0');
      f33_nvm_service_scheduler();
      FUN_00074790();
    }
    FUN_00079c42(uVar1 != 0);
    f33_nvm_leave_service_guard();
  }
  return;
}



/* Far-call trampoline: prepare {lp},0 / jarl 0x72F84 / dispose 0,{lp},lp; byte-verified against the
   exact image. Forwards with registers and stack unchanged; marked as a thunk. Forwarding shape
   machine-verified; target semantics not recovered. */

void thunk_FUN_00072f84(void)

{
  FUN_00072f84();
  return;
}



/* Return if79470(14) or72148 rejects. Otherwise79A50,79C9E; only mode result0
   invokes73B2C(1),72EEA. Then79C4C(mode_result!=0),79A94. Native uninitialized exit, initialized
   quiet scan/wrap, mode blocking and explicit terminal phases8/10/20. Queued work is bounded
   at726C4; deferred notification at7990E. No physical flash progress claim. Reject on79470(14)
   or72148. Admitted branch calls79A50 then79C9E; mode result0 additionally runs73B2C(1),72EEA;
   afterward79C4C(mode!=0),79A94. Native state0 exit, initialized quiet scan/wrap, real
   classification-mode blocking and explicit terminal08/10/20. Admission stops before726C4; deferred
   guard before7990E. Terminal inputs do not prove physical programming. */

void f33_nvm_service_logical_and_physical_driver(void)

{
  uint uVar1;
  
  uVar1 = f33_nvm_driver_gate_rejected(0x14);
  if ((uVar1 == 0) && (uVar1 = f33_nvm_service_uninitialized(), uVar1 == 0)) {
    f33_nvm_enter_service_guard();
    uVar1 = f33_nvm_reconcile_probe_mode();
    if (uVar1 == 0) {
      f33_nvm_select_service_poll('\x01');
      f33_nvm_service_scheduler();
    }
    f33_nvm_store_service_mode_nonzero(uVar1 != 0);
    f33_nvm_leave_service_guard();
  }
  return;
}



undefined4 FUN_000741a0(void)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  undefined4 uVar4;
  undefined1 auStack_1c [16];
  
  iVar3 = 0;
  iVar1 = FUN_00073274();
  if (iVar1 == 0) {
    iVar3 = FUN_00073978(auStack_1c);
  }
  uVar2 = f33_nvm_service_uninitialized();
  if (uVar2 == 0) {
    if (iVar3 == 0) {
      uVar4 = 2;
    }
    else {
      uVar4 = 1;
    }
  }
  else {
    uVar4 = 4;
  }
  return uVar4;
}



void FUN_000741d0(void)

{
  FUN_00072f76(0);
  return;
}



void FUN_000741de(void)

{
  f33_nvm_cancel_physical_operation();
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_741ea(void)

{
  return;
}



/* Accept2..123, additionally0 iff allow_zero==1. Otherwise call 71D88(14,0,api,A), whose exact body
   returns0, then return1. No init gate. Accept low16 handle2..123, additionally0 iff allow_zero
   low8==1. Otherwise call71D88 then return1. No RAM initialization gate. Public read/write pass
   allow_zero0; invalid handles require no admin RAM. */

uint f33_nvm_check_logical_handle(ushort logical_handle,uchar api,uchar allow_zero)

{
  uint uVar1;
  
  uVar1 = 1;
  if (((logical_handle < 2) || ((ushort)(f33_nvm_logical_descriptor_count - 1) < logical_handle)) &&
     ((allow_zero != '\x01' || (logical_handle != 0)))) {
    ((void)(0x14), (void)(0), (void)(api), (void)(10), f33_return_const_0_71d88());
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}



bool FUN_00074228(char param_1)

{
  if (param_1 != '\x01') {
    return param_1 != '\0';
  }
  return false;
}



/* Reject exactly logical result2 with return1; other byte values return0. Read logical result byte
   and reject exactly2; return0 for other values. Independent of second-cell write-inhibit. */

uint f33_nvm_check_not_pending(ushort logical_handle,uchar api)

{
  bool bVar1;
  uchar uStack_d;
  
  uStack_d = '\x02';
  f33_nvm_read_logical_result(logical_handle,&uStack_d);
  bVar1 = uStack_d == '\x02';
  if (bVar1) {
    ((void)(0x14), (void)(0), (void)(api), (void)(0x15), f33_return_const_0_71d88());
  }
  return (uint)bVar1;
}



bool FUN_00074274(uint param_1,undefined1 param_2)

{
  bool bVar1;
  
  bVar1 = ((ushort)f33_nvm_logical_descriptors[param_1 & 0xffff].opaque_0a >> 0xb & 1) != 0;
  if (bVar1) {
    ((void)(0x14), (void)(0), (void)(param_2), (void)(0x18), f33_return_const_0_71d88());
  }
  return bVar1;
}



undefined4 FUN_000742a2(ushort param_1,undefined1 param_2)

{
  uint uVar1;
  int iVar2;
  undefined4 uVar3;
  
  uVar3 = 1;
  uVar1 = f33_nvm_check_logical_handle(param_1,'\x03','\0');
  iVar2 = FUN_00074228(param_2);
  if ((uVar1 == 0) && (iVar2 == 0)) {
    uVar1 = f33_nvm_check_not_pending(param_1,'\x03');
    iVar2 = FUN_00074274(param_1,3);
    if (uVar1 == 0) {
      if (iVar2 == 0) {
        uVar3 = 0;
      }
      else {
        uVar3 = 1;
      }
    }
  }
  return uVar3;
}



bool FUN_000742ea(int param_1,undefined1 param_2)

{
  if (param_1 == 0) {
    ((void)(0x14), (void)(0), (void)(param_2), (void)(0xe), f33_return_const_0_71d88());
  }
  return param_1 == 0;
}



undefined4 FUN_0007430c(ushort param_1,undefined4 param_2)

{
  uint uVar1;
  int iVar2;
  undefined4 uVar3;
  
  uVar3 = 1;
  uVar1 = f33_nvm_check_logical_handle(param_1,'\x04','\x01');
  iVar2 = FUN_000742ea(param_2,4);
  if (uVar1 == 0) {
    if (iVar2 == 0) {
      uVar3 = 0;
    }
    else {
      uVar3 = 1;
    }
  }
  return uVar3;
}



bool FUN_00074338(int param_1,undefined1 param_2)

{
  if (param_1 == 0) {
    ((void)(0x14), (void)(0), (void)(param_2), (void)(0xf), f33_return_const_0_71d88());
  }
  return param_1 == 0;
}



bool FUN_0007435a(undefined4 param_1)

{
  int iVar1;
  
  iVar1 = FUN_00074338(param_1,0xf);
  return iVar1 != 0;
}



bool FUN_0007436e(ushort param_1)

{
  uint uVar1;
  
  uVar1 = f33_nvm_check_logical_handle(param_1,'\x10','\0');
  return uVar1 != 0;
}



/* NonNULL passes without descriptor or pointee access. NULL passes only modes2/4; registered mode1
   rejects it. No alignment/extent validation. NonNULL buffer passes without descriptor/payload
   read. all registered rows mode1 reject. No alignment or extent check; uninitialized odd-address
   source admitted. */

uint f33_nvm_check_buffer_argument(ushort logical_handle,void *buffer,uchar api)

{
  uint uVar1;
  
  uVar1 = 0;
  if ((((uintptr_t)(buffer)==(uintptr_t)((void *)0x0)) &&
      (f33_nvm_logical_descriptors[logical_handle].buffer_mode != '\x04')) &&
     (f33_nvm_logical_descriptors[logical_handle].buffer_mode != '\x02')) {
    ((void)(0x14), (void)(0), (void)(api), (void)(0xd), f33_return_const_0_71d88());
    uVar1 = 1;
  }
  return uVar1;
}



/* Check handle with api6/allow_zero0. If valid, evaluate BOTH pending and buffer checks, even when
   pending; return0 iff both pass, else1. Validate handle api6/allow_zero0; if valid run both
   pending and buffer gates even if pending fails. Return0 only when both pass. No write-inhibit
   check. */

uint f33_nvm_check_read_request(ushort logical_handle,void *buffer)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  
  uVar3 = 1;
  uVar1 = f33_nvm_check_logical_handle(logical_handle,'\x06','\0');
  if (uVar1 == 0) {
    uVar1 = f33_nvm_check_not_pending(logical_handle,'\x06');
    uVar2 = f33_nvm_check_buffer_argument(logical_handle,buffer,'\x06');
    if (uVar1 == 0) {
      if (uVar2 == 0) {
        uVar3 = 0;
      }
      else {
        uVar3 = 1;
      }
    }
  }
  return uVar3;
}



/* Set service6 state1, reject exactly write_inhibit1 and set state2. Call ordinary service
   notifier; target747DE is JMP LP. No mutex or flash protection claim. Values0/2/FF pass. Set
   service6 byte6100=1; exactly second-cell value1 sets6100=2 and returns1, others return0. Ordinary
   notification reaches real747DE JMP LP. Not a mutex or physical flash-protection mechanism. */

uint f33_nvm_check_write_inhibit(ushort logical_handle)

{
  uint uVar1;
  
  FUN_000720bc();
  uVar1 = f33_nvm_get_write_inhibit(logical_handle);
  if (uVar1 == 1) {
    FUN_00072108(6);
  }
  FUN_000720c8();
  return (uint)(uVar1 == 1);
}



/* Api7 handle check, then pending and buffer checks; only when both pass evaluate write-inhibit.
   Return0 iff all pass. Api7 handle validation then both pending and buffer checks. Evaluate
   write-inhibit only when both pass. */

uint f33_nvm_check_write_request(ushort logical_handle,void *buffer)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  
  uVar3 = 1;
  uVar1 = f33_nvm_check_logical_handle(logical_handle,'\a','\0');
  if (uVar1 == 0) {
    uVar1 = f33_nvm_check_not_pending(logical_handle,'\a');
    uVar2 = f33_nvm_check_buffer_argument(logical_handle,buffer,'\a');
    if ((uVar1 == 0) && (uVar2 == 0)) {
      uVar3 = f33_nvm_check_write_inhibit(logical_handle);
      if (uVar3 == 0) {
        uVar3 = 0;
      }
      else {
        uVar3 = 1;
      }
    }
  }
  return uVar3;
}



bool FUN_00074468(undefined2 param_1,undefined1 param_2)

{
  int iVar1;
  
  iVar1 = ((void)(param_1), f33_return_const_0_745c4());
  if (iVar1 == 0) {
    ((void)(0x14), (void)(0), (void)(param_2), (void)(0x18), f33_return_const_0_71d88());
  }
  return iVar1 == 0;
}



undefined4 FUN_00074494(ushort param_1,void *param_2)

{
  uint uVar1;
  int iVar2;
  uint uVar3;
  undefined4 uVar4;
  
  uVar4 = 1;
  uVar1 = f33_nvm_check_logical_handle(param_1,'\b','\0');
  if (uVar1 == 0) {
    uVar1 = f33_nvm_check_not_pending(param_1,'\b');
    iVar2 = FUN_00074468(param_1,8);
    uVar3 = f33_nvm_check_buffer_argument(param_1,param_2,'\b');
    if ((uVar1 == 0) && (iVar2 == 0)) {
      if (uVar3 == 0) {
        uVar4 = 0;
      }
      else {
        uVar4 = 1;
      }
    }
  }
  return uVar4;
}



undefined4 FUN_000744de(ushort param_1)

{
  uint uVar1;
  uint uVar2;
  undefined4 uVar3;
  
  uVar3 = 1;
  uVar1 = f33_nvm_check_logical_handle(param_1,'\x16','\0');
  if (uVar1 == 0) {
    uVar1 = f33_nvm_check_not_pending(param_1,'\x16');
    uVar2 = f33_nvm_check_buffer_argument(param_1,(void *)0x0,'\x16');
    if (uVar1 == 0) {
      if (uVar2 == 0) {
        uVar3 = 0;
      }
      else {
        uVar3 = 1;
      }
    }
  }
  return uVar3;
}



undefined4 FUN_0007451e(ushort param_1)

{
  uint uVar1;
  uint uVar2;
  undefined4 uVar3;
  
  uVar3 = 1;
  uVar1 = f33_nvm_check_logical_handle(param_1,'\x17','\0');
  if (uVar1 == 0) {
    uVar1 = f33_nvm_check_not_pending(param_1,'\x17');
    uVar2 = f33_nvm_check_buffer_argument(param_1,(void *)0x0,'\x17');
    if ((uVar1 == 0) && (uVar2 == 0)) {
      uVar1 = f33_nvm_check_write_inhibit(param_1);
      if (uVar1 == 0) {
        uVar3 = 0;
      }
      else {
        uVar3 = 1;
      }
    }
  }
  return uVar3;
}



undefined4 FUN_00074568(ushort param_1)

{
  uint uVar1;
  int iVar2;
  uint uVar3;
  undefined4 uVar4;
  
  uVar4 = 1;
  uVar1 = f33_nvm_check_logical_handle(param_1,'\x18','\0');
  if (uVar1 == 0) {
    uVar1 = f33_nvm_check_not_pending(param_1,'\x18');
    iVar2 = FUN_00074468(param_1,0x18);
    uVar3 = f33_nvm_check_buffer_argument(param_1,(void *)0x0,'\x18');
    if ((uVar1 == 0) && (iVar2 == 0)) {
      if (uVar3 == 0) {
        uVar4 = 0;
      }
      else {
        uVar4 = 1;
      }
    }
  }
  return uVar4;
}



/* Constant source: return 0; shape-classified from the canonical corpus. Callers receive this
   literal directly; its meaning is not recovered. */

undefined4 f33_return_const_0_745b8(void)

{
  return 0;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_745bc(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_745be(void)

{
  return;
}



/* Constant source: return 1; shape-classified from the canonical corpus. Callers receive this
   literal directly; its meaning is not recovered. */

undefined4 f33_return_const_1_745c0(void)

{
  return 1;
}



/* Constant source: return 0; shape-classified from the canonical corpus. Callers receive this
   literal directly; its meaning is not recovered. */

undefined4 f33_return_const_0_745c4(void)

{
  return 0;
}



void FUN_000745c8(void)

{
  f33_nvm_read_buffer_override = 0;
  f33_nvm_write_buffer_override = 0;
  return;
}



/* WARNING: This is an inlined function */
/* Clear byteFEBF6B14; onlyr11 is clobbered. Preserve r6/r7 through the real p-code so the override
   setters retain their inputs. Clear byteFEBF6B14. Raw ten-byte body clobbers onlyr11 and
   preservesr6/r7; real p-code inlining repairs the setters' lost input-buffer dataflow. Counter is
   consumed on nonzero mode4 buffer callbacks by7463E; broader retry policy is not established. */

void f33_nvm_reset_buffer_retry(void)

{
  f33_nvm_buffer_retry = '\0';
  return;
}



undefined4 FUN_0007463e(void)

{
  if (f33_nvm_buffer_retry < DAT_00026bf4) {
    f33_nvm_buffer_retry = f33_nvm_buffer_retry + '\x01';
    return 2;
  }
  return 1;
}



void FUN_0007477a(void)

{
  uint uVar1;
  
  for (uVar1 = (uint)DAT_00027624; uVar1 != 0; uVar1 = uVar1 - 1) {
    DAT_febf6b18 = 0;
  }
  return;
}



void FUN_00074790(void)

{
  int iVar1;
  ushort uVar2;
  undefined8 uVar3;
  ushort uVar4;
  
  uVar2 = DAT_00027624;
  uVar3 = 0x23dfc00000000;
  for (uVar4 = 0; uVar4 < uVar2; uVar4 = uVar4 + 1) {
    iVar1 = DAT_febf6b18;
    if ((DAT_febf6b18 != 0) && (iVar1 = DAT_febf6b18 + -1, DAT_febf6b18 == 1)) {
      (*(int (*)())*(code **)((int)((ulonglong)uVar3 >> 0x20) + 0x382c))(uVar4);
    }
    DAT_febf6b18 = iVar1;
  }
  return;
}



void FUN_000747c8(undefined4 param_1,undefined4 param_2)

{
  DAT_febf6b18 = param_2;
  return;
}



/* Single constant publisher: DAT_febf6b18 = 0; Shape-classified from the canonical corpus; the
   target cell is not yet named, so the written state's meaning is unknown. */

void FUN_000747d2(void)

{
  DAT_febf6b18 = 0;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_747dc(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_747de(void)

{
  return;
}



/* Forward byte loop with full32-bit count. No validation, overlap-safe memmove guarantee or
   return-value contract. Forward byte copy with full32-bit count. Exact instructions establish
   unsigned loop width and source/destination order; composed post-read execution checks
   complete16/56-byte copies and surrounding canaries without replacing this helper. No bounds
   validation, overlap-safe memmove guarantee or return-value contract. */

void f33_copy_bytes_forward(uchar *destination,uchar *source,uint byte_count)

{
  uint uVar1;
  
  for (uVar1 = 0; uVar1 < byte_count; uVar1 = uVar1 + 1) {
    destination[uVar1] = source[uVar1];
  }
  return;
}



undefined4 FUN_0007484a(int param_1,int param_2,uint param_3)

{
  uint uVar1;
  undefined4 uVar2;
  
  uVar1 = 0;
  while( true ) {
    if (param_3 <= uVar1) {
      return 0;
    }
    if ((*((byte *)camry_host_ptr((uint32_t)(uVar1 + param_1)))) != (*((byte *)camry_host_ptr((uint32_t)(uVar1 + param_2))))) break;
    uVar1 = uVar1 + 1;
  }
  if ((*((byte *)camry_host_ptr((uint32_t)(uVar1 + param_1)))) < (*((byte *)camry_host_ptr((uint32_t)(uVar1 + param_2))))) {
    uVar2 = 0xffffffff;
  }
  else {
    uVar2 = 1;
  }
  return uVar2;
}



void FUN_00074872(int param_1,undefined1 param_2,uint param_3)

{
  uint uVar1;
  
  for (uVar1 = 0; uVar1 < param_3; uVar1 = uVar1 + 1) {
    (*((undefined1 *)camry_host_ptr((uint32_t)(uVar1 + param_1)))) = param_2;
  }
  return;
}



/* WARNING: This is an inlined function */
/* Return unsigned byte27638+6*handle. The registered123 descriptors all contain zero. No local
   handle bound check. LD.BU reads option byte27638+6*low16(handle), zero-extended inr10. All123
   registered options are zero. Raw field offset and full register preservation established;
   composed execution traverses the real getter. OEM option-bit meanings and nonzero registered
   configurations are not recovered. */

uint f33_nvm_descriptor_option(ushort handle)

{
  return (uint)f33_nvm_descriptors[handle].option;
}



undefined4 FUN_0007490a(undefined4 param_1)

{
  return param_1;
}



undefined4 FUN_0007490e(undefined4 param_1)

{
  return param_1;
}



undefined * FUN_00074960(void)

{
  undefined *puVar1;
  
  if (DAT_febf6b20 != 0) {
    if (DAT_febf6b20 == 1) {
      return ((undefined *)camry_host_ptr((uint32_t)(0x1)));
    }
    if (DAT_febf6b20 < 3) {
      puVar1 = (undefined *)f33_nvm_translate_saved_driver_result();
      return puVar1;
    }
    if (DAT_febf6b20 == 3) {
      return ((undefined *)camry_host_ptr(0xfffau));
    }
    if (DAT_febf6b20 < 6) {
      return ((undefined *)camry_host_ptr(0xfffbu));
    }
    if (DAT_febf6b20 == 0x11) {
      return ((undefined *)camry_host_ptr((uint32_t)(0xffff)));
    }
    if (DAT_febf6b20 == 0xff) {
      return (undefined *)0x0;
    }
  }
  return ((undefined *)camry_host_ptr((uint32_t)(0xffffffff)));
}



/* Paired constant publisher: DAT_febf6b20 = 0xff; and DAT_febf6b21 = 0xff;; shape-classified from
   the canonical corpus. Target cells not yet named. */

void FUN_000749ae(void)

{
  DAT_febf6b20 = 0xff;
  DAT_febf6b21 = 0xff;
  return;
}



void FUN_000749bc(undefined1 param_1)

{
  DAT_febf6b20 = param_1;
  return;
}



void FUN_000749c6(undefined1 param_1)

{
  DAT_febf6b21 = param_1;
  return;
}



void FUN_000749d0(void)

{
  f33_nvm_driver_phase = '\0';
  DAT_febf6b24 = 0;
  DAT_febf6b1c = 0;
  DAT_febf6b68 = 0xffffffff;
  DAT_febf6b6c = 0;
  return;
}



void FUN_000749e4(void)

{
  DAT_febf6c34 = 0;
  FUN_000749ae();
  FUN_000749d0();
  return;
}



void FUN_000749fc(void)

{
  DAT_febf6c5a = 0xff;
  DAT_febf6c59 = 0;
  DAT_febf6c30 = 0xffffffff;
  DAT_febf6c48 = 0;
  FUN_00074872(camry_host_addr(((undefined *)camry_host_ptr(0xfebf6bd0u))), 0, 0x40);
  return;
}



/* Return1 if6B22!=0; otherwise return whether lower status6CB1 equals80. The first branch does not
   read6CB1. Return1 if6B22!=0 without lower status read; otherwise compare6CB1 exactly80. Native
   block-latch and lower-status branches through real consumers. */

uint f33_nvm_sync_access_blocked(void)

{
  int iVar1;
  uint uVar2;
  
  uVar2 = 1;
  if (f33_nvm_driver_block_latch == '\0') {
    iVar1 = FUN_00078896();
    uVar2 = (uint)(iVar1 == 0x80);
  }
  return uVar2;
}



/* 74A36 true->FFFF0000; otherwise6B23==0->1, nonzero->0000FFF9. These are full32 results, not
   pointers. 74A36 blocked->FFFF0000; else6B23 zero->1/nonzero->0000FFF9. Full32 result words not
   pointers. Native admitted and both rejected read paths;74D78 collapses all non1 admissions
   toFFFF0000. */

uint f33_nvm_sync_admission_result(void)

{
  uint uVar1;
  undefined *puVar2;
  
  uVar1 = f33_nvm_sync_access_blocked();
  if (uVar1 == 1) {
    puVar2 = ((undefined *)camry_host_ptr((uint32_t)(0xffff0000)));
  }
  else if (f33_nvm_driver_phase == '\0') {
    puVar2 = ((undefined *)camry_host_ptr((uint32_t)(0x1)));
  }
  else {
    puVar2 = ((undefined *)camry_host_ptr(0xfff9u));
  }
  return (uint)camry_host_addr(puVar2);
}



void FUN_00074a82(undefined4 param_1)

{
  DAT_febf6c34 = param_1;
  return;
}



/* Require74A5A result1, reset diagnostics, decrement cursor by64 BEFORE7867A(cursor,64). Driver0
   installs completion callback and returns2; failure translates saved driver status. Native
   exact-family paths reach first opcode20 boundary with decreasing addresses. */

uint f33_nvm_submit_previous_erase_block(void)

{
  uint32_t puVar1;
  uint uVar2;
  int iVar3;
  
  puVar1 = 0x23dfcu;
  uVar2 = f33_nvm_sync_admission_result();
  if (uVar2 == 1) {
    FUN_000749ae();
    DAT_febf6c30 = DAT_febf6c30 + -0x40;
    iVar3 = FUN_0007867a(DAT_febf6c30,0x40);
    if (iVar3 == 0) {
      FUN_00074a82((*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x3b28)))));
      uVar2 = 2;
    }
    else {
      uVar2 = f33_nvm_translate_saved_driver_result();
    }
  }
  return uVar2;
}



void FUN_00074aca(uint param_1)

{
  uint32_t puVar1;
  int extraout_r6;
  uint uVar2;
  
  puVar1 = 0x23dfcu;
  uVar2 = (uint)DAT_febf6c5a;
  FUN_000749e4();
  if (uVar2 < 0xc) {
    if (DAT_febf6c59 == '\x01') {
      if ((extraout_r6 == 1) && (DAT_febf6c48 = DAT_febf6c48 + -1, DAT_febf6c48 != 0)) {
        param_1 = f33_nvm_submit_previous_erase_block();
      }
      if (param_1 == 2) {
        return;
      }
    }
    FUN_000749fc();
    (*(int (*)())*(code **)(puVar1 + uVar2 * 4 + 0x3be8))(param_1);
  }
  return;
}



void FUN_00074b20(void)

{
  int iVar1;
  
  iVar1 = camry_host_addr(FUN_00074960());
  if (iVar1 != 0) {
    FUN_00074aca(iVar1);
    FUN_000781aa(0);
  }
  return;
}



uint FUN_00074b3c(void)

{
  uint32_t puVar1;
  uint uVar2;
  
  puVar1 = 0x23dfcu;
  f33_nvm_driver_block_latch = '\0';
  FUN_000749e4();
  FUN_000749fc();
  ((void)(((undefined *)camry_host_ptr((uint32_t)(puVar1 + 0x3b34)))), FUN_00078500());
  uVar2 = f33_nvm_translate_saved_driver_result();
  FUN_000781aa(0);
  return uVar2;
}



/* Far-call trampoline: prepare {lp},0 / jarl 0x74B3C / dispose 0,{lp},lp; byte-verified against the
   exact image. Forwards with registers and stack unchanged; marked as a thunk. Forwarding shape
   machine-verified; target semantics not recovered. */

uint thunk_FUN_00074b3c(void)

{
  return FUN_00074b3c();
}



/* Store end cursor=offset+64*low16(count) before lower admission. Submit previous block. Only
   result2 publishes active1, remaining count and low8 callback selector; preserve driver result in
   R10. No completed erase proof. */

uint f33_nvm_start_reverse_erase(uint byte_offset,uint page_count,uint callback_selector)

{
  uint uVar1;
  
  DAT_febf6c30 = (page_count & 0xffff) * 0x40 + byte_offset;
  uVar1 = f33_nvm_submit_previous_erase_block();
  if (uVar1 == 2) {
    DAT_febf6c59 = 1;
    DAT_febf6c5a = (undefined1)callback_selector;
    DAT_febf6c48 = (undefined2)page_count;
  }
  return uVar1;
}



int FUN_00074bb4(uint param_1)

{
  return (int)(param_1 & 0xffff) >> 2;
}



uint FUN_00074bbc(undefined4 param_1,undefined2 param_2, undefined4 param_3)

{
  uint32_t puVar1;
  int iVar2;
  uint uVar3;
  
  puVar1 = 0x23dfcu;
  FUN_000749ae();
  iVar2 = FUN_00078566(param_1, param_3, (uint)(ushort)param_2);
  if (iVar2 == 0) {
    iVar2 = FUN_00074bb4(param_2);
    FUN_00074a82((*((int *)camry_host_ptr((uint32_t)(0x3b20u + (int)(puVar1 + 4))))) * iVar2);
    uVar3 = 2;
  }
  else {
    uVar3 = f33_nvm_translate_saved_driver_result();
  }
  return uVar3;
}



undefined4 FUN_00074bf2(void)

{
  if (DAT_febf6b24 < DAT_0002792d) {
    DAT_febf6b24 = DAT_febf6b24 + 1;
    DAT_febf6b1c = DAT_0002791c;
    f33_nvm_driver_phase = 0xaa;
    return 2;
  }
  return 0xffff;
}



int FUN_00074c20(undefined4 param_1,ushort param_2)

{
  undefined4 extraout_r6;
  uchar *source;
  int iVar1;
  
  DAT_febf6b24 = 0;
  iVar1 = FUN_00074bf2();
  if (iVar1 == 2) {
    DAT_febf6b68 = extraout_r6;
    DAT_febf6b6c = param_2;
    f33_copy_bytes_forward(((undefined *)camry_host_ptr(0xfebf6b28u)),source,(uint)param_2);
  }
  return iVar1;
}



uint FUN_00074c54(undefined4 param_1,uint param_2,uchar *param_3,undefined1 param_4,char param_5)

{
  uint uVar1;
  int iVar2;
  
  param_2 = param_2 & 0xffff;
  uVar1 = f33_nvm_sync_admission_result();
  if (uVar1 == 1) {
    f33_copy_bytes_forward(((undefined *)camry_host_ptr(0xfebf6bd0u)),param_3,param_2);
    if (param_5 == '\x01') {
      iVar2 = thunk_FUN_00079432();
      if (iVar2 == 0) {
        uVar1 = FUN_00074bbc(param_1, (uint)(ushort)param_2, (int)0xfebf6bd0);
        if (uVar1 == 2) {
          FUN_000781aa(1);
          DAT_febf6c59 = 2;
          DAT_febf6c5a = param_4;
          return 2;
        }
        return uVar1;
      }
      uVar1 = ((void)(((undefined *)camry_host_ptr(0xfebf6bd0u))), FUN_00074c20(param_1, param_2));
    }
    else {
      uVar1 = FUN_00074bbc(param_1, param_2, camry_host_addr(((undefined *)camry_host_ptr(0xfebf6bd0u))));
    }
  }
  if (uVar1 == 2) {
    DAT_febf6c5a = param_4;
    DAT_febf6c59 = 2;
    return 2;
  }
  return uVar1;
}



undefined4 FUN_00074cd2(char param_1)

{
  undefined4 uVar1;
  
  if (param_1 != '\t') {
    uVar1 = 0xff;
    if (param_1 == '\v') {
      uVar1 = 2;
    }
    return uVar1;
  }
  return 1;
}



void FUN_00074ce8(char param_1)

{
  undefined4 uVar1;
  
  if (param_1 == '\x01') {
    uVar1 = 0;
    f33_nvm_driver_block_latch = '\x01';
  }
  else {
    if (param_1 != '\x02') {
      return;
    }
    uVar1 = 1;
  }
  FUN_00076a8c(uVar1);
  return;
}



/* Actual7892A blank check: result2->3,7->4; other results translate through7494C and pass74CD2
   classification to74CE8 for side effects. Result4 here means continue into the reader, not a
   completed read. Real7892A returns2(blank)->3;7(nonblank)->4/read-next. Other results use7494C
   then74CD2/74CE8 side effects. Native normal classifications and lower driver-error branch;
   hardware completion/blankness remain explicit inputs. */

uint f33_nvm_map_blank_check_result(uint byte_offset,ushort byte_count)

{
  uint uVar1;
  undefined4 uVar2;
  uint uVar3;
  
  uVar1 = f33_dataflash_blank_check(byte_offset,(uint)byte_count);
  if (uVar1 == 2) {
    uVar3 = 3;
  }
  else {
    uVar3 = 4;
    if (uVar1 != 7) {
      uVar3 = f33_nvm_translate_read_driver_result((uchar)uVar1);
      uVar2 = FUN_00074cd2(uVar1);
      FUN_00074ce8(uVar2);
    }
  }
  return uVar3;
}



uint FUN_00074d40(uint param_1,uint param_2,uint *param_3)

{
  uint uVar1;
  undefined4 uVar2;
  uint uVar3;
  
  uVar1 = f33_dataflash_read_words(param_1,param_3,param_2 & 0xffff);
  if ((uVar1 == 2) || (uVar1 == 5)) {
    uVar3 = 1;
  }
  else {
    uVar3 = f33_nvm_translate_read_driver_result((uchar)uVar1);
    uVar2 = FUN_00074cd2(uVar1);
    FUN_00074ce8(uVar2);
  }
  return uVar3;
}



/* Only admission result1 proceeds; any other result collapses toFFFF0000. Then set6B20/6B21=FF.
   Exact low8 option1 calls74D0C; only its result4 proceeds to74D40 read, other results return
   without copy. Other option bytes read directly. Low16 count; native option2/high-bit truncation,
   blank no-copy, and both rejection gates. Admission1 only; otherwiseFFFF0000 before diagnostic
   reset/copy. Then6B20/21=FF. Exact low8 option1 calls74D0C and reads only on its4 result; other
   options read directly. Low16 length. Native64-byte identity-bound read with high input bits,
   blank no-copy, nonblank read and rejection canaries. */

uint f33_nvm_read_with_optional_blank_check
               (uint byte_offset,ushort byte_count,uchar *destination,uchar blank_option)

{
  uint uVar1;
  
  uVar1 = f33_nvm_sync_admission_result();
  if (uVar1 == 1) {
    FUN_000749ae();
    if ((blank_option != '\x01') ||
       (uVar1 = f33_nvm_map_blank_check_result(byte_offset,byte_count), uVar1 == 4)) {
      uVar1 = FUN_00074d40(byte_offset,byte_count,destination);
    }
  }
  else {
    uVar1 = 0xffff0000;
  }
  return uVar1;
}



void FUN_00074db8(void)

{
  undefined4 uVar1;
  int iVar2;
  
  if (f33_nvm_driver_phase == '\0') {
    return;
  }
  if (f33_nvm_driver_phase == 0xaa) {
    DAT_febf6b1c = DAT_febf6b1c + -1;
    if (0 < DAT_febf6b1c) {
      return;
    }
    iVar2 = thunk_FUN_00079432();
    if (iVar2 == 0) {
      iVar2 = FUN_00074bbc(DAT_febf6b68, DAT_febf6b6c, camry_host_addr(((undefined *)camry_host_ptr(0xfebf6b28u))));
      if (iVar2 == 2) {
        FUN_000781aa(1);
        goto LAB_00074e14;
      }
      uVar1 = 4;
    }
    else {
      iVar2 = FUN_00074bf2();
      if (iVar2 == 2) {
        return;
      }
      uVar1 = 0x11;
    }
    FUN_000749bc(uVar1);
  }
LAB_00074e14:
  FUN_000749d0();
  return;
}



void FUN_00074e1c(void)

{
  if (0 < DAT_febf6c34) {
    DAT_febf6c34 = DAT_febf6c34 - (uint)DAT_0002792a;
    if (DAT_febf6c34 < 1) {
      FUN_00078766();
      FUN_000749bc(3);
    }
  }
  return;
}



void FUN_00074e46(char param_1)

{
  uint uVar1;
  
  uVar1 = f33_nvm_sync_access_blocked();
  if (uVar1 == 0) {
    FUN_000787fa();
    if (param_1 == '\0') {
      FUN_00074db8();
      FUN_00074e1c();
    }
    FUN_00074b20();
  }
  return;
}



undefined4 FUN_00074e6e(void)

{
  uint uVar1;
  int iVar2;
  
  uVar1 = f33_nvm_sync_access_blocked();
  if (uVar1 != 1) {
    iVar2 = FUN_0007888c();
    if (iVar2 == 1) {
      return 0;
    }
    if (iVar2 == 2) {
      return 1;
    }
  }
  return 2;
}



uint FUN_00074e94(void)

{
  uint uVar1;
  
  uVar1 = f33_nvm_sync_access_blocked();
  if (uVar1 == 1) {
    uVar1 = 0xffff0000;
  }
  else {
    FUN_000749ae();
    FUN_00078766();
    uVar1 = f33_nvm_translate_saved_driver_result();
    if (uVar1 == 0) {
      uVar1 = 1;
    }
  }
  FUN_000749e4();
  return uVar1;
}



void FUN_00074ec2(void)

{
  FUN_000749bc(1);
  return;
}



void FUN_00074ed0(void)

{
  FUN_000749bc(2);
  return;
}



undefined4 FUN_00074ede(char param_1)

{
  undefined4 uVar1;
  
  if ((param_1 != '\x05') && (-0x7f < param_1)) {
    uVar1 = 0xff;
    if (param_1 == -0x7e) {
      uVar1 = 2;
    }
    return uVar1;
  }
  return 1;
}



undefined4 FUN_00074efe(short param_1,undefined4 param_2,undefined4 param_3,undefined1 param_4)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = FUN_000781da();
  if ((iVar1 != 1) && (param_1 == 0x5c)) {
    FUN_000749c6(param_4);
    uVar2 = FUN_00074ede((uint)(byte)param_4);
    FUN_00074ce8(uVar2);
  }
  return 0;
}



/* WARNING: Inlined function: f33_nvm_descriptor_option */

uchar FUN_00074f2e(uint param_1)

{
  uchar uVar1;
  
  if ((param_1 & 0xffff) < (uint)f33_nvm_descriptor_count) {
    uVar1 = f33_nvm_descriptors[param_1 & 0xffff].option;
  }
  else {
    uVar1 = 0xff;
  }
  return uVar1;
}



void FUN_00074f4a(void)

{
  undefined4 uVar1;
  int iVar2;
  
  uVar1 = FUN_00077c9e();
  iVar2 = FUN_00074f2e(uVar1);
  if (iVar2 == 0) {
    uVar1 = 1;
  }
  else {
    uVar1 = 0xff;
    if (iVar2 == 1) {
      uVar1 = 0;
    }
  }
  FUN_000783b6(uVar1);
  return;
}



/* Single constant publisher: DAT_febf6c51 = 1; Shape-classified from the canonical corpus; the
   target cell is not yet named, so the written state's meaning is unknown. */

void FUN_00074f72(void)

{
  DAT_febf6c51 = 1;
  return;
}



/* Single constant publisher: DAT_febf6c51 = 0; Shape-classified from the canonical corpus; the
   target cell is not yet named, so the written state's meaning is unknown. */

void FUN_00074f7e(void)

{
  DAT_febf6c51 = 0;
  return;
}



undefined4 FUN_00074f88(char param_1)

{
  undefined4 uVar1;
  
  uVar1 = 0;
  if ((param_1 == '\0') && (DAT_febf6c51 == '\x01')) {
    DAT_febf6c51 = '\x02';
    uVar1 = 1;
  }
  return uVar1;
}



/* Constant-block fill: 8 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_74fa2(void)

{
  DAT_febf6c55 = 0;
  DAT_febf6c54 = 0;
  DAT_febf6c53 = 0;
  DAT_febf6c52 = 0;
  DAT_febf6c51 = 0;
  DAT_febf6c50 = 0;
  DAT_febf6c3e = 0xffff;
  DAT_febf6c40 = 0xffff;
  return;
}



undefined4 FUN_00074fe6(void)

{
  f33_fill_constant_block_74fa2();
  thunk_FUN_000772f8();
  thunk_FUN_00077df2();
  return 1;
}



void FUN_00075008(undefined4 param_1)

{
  FUN_000783ca(param_1);
  FUN_000783c0(1);
  return;
}



void FUN_0007501a(undefined4 param_1)

{
  FUN_000783ca(param_1);
  FUN_000783c0(2);
  return;
}



void FUN_0007502c(undefined4 param_1)

{
  FUN_000783ca(param_1);
  DAT_febf6c55 = 1;
  return;
}



/* Sequential initializer chain: 4 unconditional calls and no other statements; shape-verified. The
   called sequence is the function's entire behavior; chain family members differ in callee sets. */

void f33_run_init_chain_75042(undefined4 param_1)

{
  FUN_00077ce8();
  FUN_00077d14(param_1);
  f33_nvm_finish_physical_result();
  f33_fill_constant_block_74fa2();
  return;
}



undefined4 FUN_0007505e(char param_1)

{
  undefined4 uVar1;
  
  if (param_1 == '\x01') {
    uVar1 = 10;
    DAT_febf6c52 = 0;
    FUN_00077d1e((uint)(byte)param_1);
  }
  else {
    uVar1 = 6;
  }
  return uVar1;
}



undefined4 FUN_00075080(undefined *param_1,undefined4 *param_2)

{
  undefined4 uVar1;
  
  if (DAT_febf6c52 < DAT_0002792b) {
    DAT_febf6c52 = DAT_febf6c52 + 1;
    uVar1 = 3;
  }
  else {
    *param_2 = camry_host_addr(param_1);
    uVar1 = 0;
    if ((uintptr_t)(param_1)==(uintptr_t)(((undefined *)camry_host_ptr(0xfffdu)))) {
      FUN_00076992();
    }
  }
  return uVar1;
}



undefined4 FUN_000750b2(undefined *param_1,undefined4 *param_2)

{
  int iVar1;
  
  iVar1 = FUN_00077c64();
  if (iVar1 == 1) {
    *param_2 = camry_host_addr(param_1);
    if ((uintptr_t)(param_1)==(uintptr_t)(((undefined *)camry_host_ptr(0xfffdu)))) {
      FUN_00076992();
    }
  }
  else if (iVar1 == 2) {
    FUN_0007699c();
    f33_nvm_mark_physical_attempt_error();
    if ((uintptr_t)(param_1)==(uintptr_t)(((undefined *)camry_host_ptr(0xfffdu)))) {
      FUN_00076992();
    }
    f33_run_init_chain_75042(1);
  }
  else {
    *param_2 = camry_host_addr(((undefined *)camry_host_ptr(0xfffbu)));
  }
  return 0;
}



undefined4 FUN_000750fe(undefined4 param_1, undefined4 param_2)

{
  undefined4 uVar1;
  
  if (DAT_febf6c52 < DAT_0002792b) {
    DAT_febf6c52 = DAT_febf6c52 + 1;
    uVar1 = 0xf;
  }
  else {
    uVar1 = FUN_000750b2(((undefined *)camry_host_ptr((uint32_t)(param_1))), ((undefined4 *)camry_host_ptr((uint32_t)(param_2))));
  }
  return uVar1;
}



undefined4 FUN_00075122(char param_1,ushort param_2,undefined4 *param_3)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = FUN_00077c64();
  if (param_1 == '\f') {
    DAT_febf6c3e = param_2 & 0xff;
    uVar2 = FUN_0007505e(iVar1);
  }
  else if (param_1 == '\x0e') {
    if (iVar1 == 1) {
      uVar2 = 0x13;
    }
    else {
      uVar2 = 0;
      if (iVar1 == 2) {
        *param_3 = 0xfffc;
        FUN_0007699c();
      }
      else {
        *param_3 = camry_host_addr(((undefined *)camry_host_ptr(0xfffbu)));
      }
    }
    FUN_00077d1e(2);
  }
  else {
    uVar2 = 0;
    *param_3 = camry_host_addr(((undefined *)camry_host_ptr(0xfffbu)));
  }
  return uVar2;
}



undefined4 FUN_00075282(char param_1,undefined4 *param_2)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = FUN_00077c64();
  if (param_1 == '\n') {
    if (iVar1 == 1) {
      uVar2 = 2;
      DAT_febf6c52 = 0;
    }
    else if (iVar1 == 2) {
      uVar2 = 6;
    }
    else {
      uVar2 = 0;
    }
  }
  else if (param_1 == '\v') {
    uVar2 = FUN_0007505e(iVar1);
  }
  else if (param_1 == '\r') {
    if (iVar1 == 1) {
      uVar2 = 0x12;
    }
    else {
      uVar2 = 0;
      if (iVar1 == 2) {
        *param_2 = 0xfffc;
        FUN_0007699c();
      }
      else {
        *param_2 = camry_host_addr(((undefined *)camry_host_ptr(0xfffbu)));
      }
    }
    FUN_00077d1e(2);
  }
  else {
    uVar2 = 0;
    *param_2 = camry_host_addr(((undefined *)camry_host_ptr(0xfffbu)));
  }
  return uVar2;
}



undefined4 FUN_000752fa(undefined4 param_1,int *param_2)

{
  uint32_t puVar1;
  int iVar2;
  uint uVar3;
  undefined4 uVar4;
  undefined1 uStack_e;
  byte bStack_d;
  
  puVar1 = 0x23dfcu;
  uVar4 = 0xff;
  iVar2 = FUN_00077c64();
  bStack_d = 0xff;
  uStack_e = 0xd;
  if (iVar2 != 0) {
    uVar3 = FUN_00077c9e();
    if (uVar3 < (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + 0x3b2c))))) {
      if (DAT_febf6c50 == '\x01') {
        DAT_febf6c53 = 2;
      }
      iVar2 = camry_host_addr(FUN_00077eba(uVar3,&uStack_e,&bStack_d));
      if (iVar2 == 1) {
        DAT_febf6c3e = (ushort)bStack_d;
        uVar4 = FUN_00075282(uStack_e,param_2);
        return uVar4;
      }
      *param_2 = iVar2;
    }
    else {
      *param_2 = (int)0xfffbu;
    }
    uVar4 = 0;
  }
  return uVar4;
}



undefined4 FUN_00075376(int param_1,int *param_2)

{
  undefined4 *puVar1;
  undefined4 uVar2;
  int iVar3;
  undefined4 uVar4;
  undefined4 *puVar5;
  undefined4 uVar6;
  undefined4 *puVar7;
  undefined4 local_28 [4];
  undefined1 uStack_18;
  
  puVar1 = local_28;
  uVar6 = 0xff;
  uVar2 = FUN_00077c9e();
  puVar7 = *(undefined4 **)(param_1 + 4);
  puVar5 = puVar7 + 5;
  do {
    uVar4 = *puVar7;
    puVar7 = puVar7 + 1;
    *puVar1 = uVar4;
    puVar1 = puVar1 + 1;
  } while ((uintptr_t)(puVar5)!=(uintptr_t)(puVar7));
  iVar3 = FUN_00074f88(uStack_18);
  if ((iVar3 != 0) && (iVar3 = camry_host_addr(FUN_0007808c(uVar2,DAT_febf6c3e,2)), iVar3 != 2)) {
    *param_2 = iVar3;
    uVar6 = 0;
  }
  return uVar6;
}



undefined4 FUN_000753cc(undefined4 param_1, undefined4 param_2)

{
  FUN_00074f72();
  return FUN_00075376(param_1, ((int *)camry_host_ptr((uint32_t)(param_2))));
}



/* Far-call trampoline: prepare {lp},0 / jarl 0x75376 / dispose 0,{lp},lp; byte-verified against the
   exact image. Forwards with registers and stack unchanged; marked as a thunk. Forwarding shape
   machine-verified; target semantics not recovered. */

undefined4 thunk_FUN_00075376(undefined4 param_1, undefined4 param_2)

{
  return FUN_00075376(param_1, ((int *)camry_host_ptr((uint32_t)(param_2))));
}



uint FUN_0007543c(uint param_1)

{
  return 1 << (param_1 & 0x1f) & 3;
}



undefined4 FUN_0007544a(undefined4 param_1,int *param_2)

{
  undefined4 uVar1;
  undefined4 uVar2;
  int iVar3;
  undefined4 uVar4;
  
  uVar4 = 0xff;
  uVar1 = FUN_00077c9e();
  uVar2 = FUN_0007543c(DAT_febf6c3e);
  iVar3 = camry_host_addr(FUN_00076e36(uVar1,uVar2));
  if (iVar3 != 2) {
    *param_2 = iVar3;
    uVar4 = 0;
  }
  return uVar4;
}



undefined4 FUN_0007547e(undefined4 param_1,int *param_2)

{
  uint32_t puVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  
  puVar1 = 0x23dfcu;
  iVar2 = FUN_000783d4();
  uVar3 = FUN_00077c9e();
  if (iVar2 == 1) {
    uVar3 = 4;
  }
  else {
    if (DAT_febf6c52 < (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x3b2f)))))) {
      DAT_febf6c52 = DAT_febf6c52 + 1;
      uVar4 = FUN_0007543c(DAT_febf6c3e);
      iVar2 = camry_host_addr(FUN_00076e36(uVar3,uVar4));
      if (iVar2 == 2) {
        return 0xff;
      }
    }
    *param_2 = iVar2;
    uVar3 = 0;
  }
  return uVar3;
}



undefined4 FUN_00075510(undefined4 param_1,undefined4 param_2)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = FUN_000783d4();
  if (iVar1 == 1) {
    uVar2 = 5;
  }
  else {
    uVar2 = FUN_00075080(((undefined *)camry_host_ptr((uint32_t)(iVar1))), ((undefined4 *)camry_host_ptr((uint32_t)(param_2))));
  }
  return uVar2;
}



undefined4 FUN_0007552e(int param_1,int *param_2)

{
  undefined4 *puVar1;
  undefined4 uVar2;
  int iVar3;
  undefined4 uVar4;
  undefined4 *puVar5;
  undefined4 uVar6;
  undefined4 *puVar7;
  undefined4 local_28 [4];
  undefined1 uStack_18;
  
  puVar1 = local_28;
  uVar6 = 0xff;
  uVar2 = FUN_00077c9e();
  puVar7 = *(undefined4 **)(param_1 + 4);
  puVar5 = puVar7 + 5;
  do {
    uVar4 = *puVar7;
    puVar7 = puVar7 + 1;
    *puVar1 = uVar4;
    puVar1 = puVar1 + 1;
  } while ((uintptr_t)(puVar5)!=(uintptr_t)(puVar7));
  iVar3 = FUN_00074f88(uStack_18);
  if ((iVar3 != 0) && (iVar3 = camry_host_addr(FUN_0007808c(uVar2,DAT_febf6c3e,1)), iVar3 != 2)) {
    *param_2 = iVar3;
    uVar6 = 0;
  }
  return uVar6;
}



undefined4 FUN_00075584(undefined4 param_1, undefined4 param_2)

{
  FUN_00074f72();
  return FUN_0007552e(param_1, ((int *)camry_host_ptr((uint32_t)(param_2))));
}



/* Far-call trampoline: prepare {lp},0 / jarl 0x7552E / dispose 0,{lp},lp; byte-verified against the
   exact image. Forwards with registers and stack unchanged; marked as a thunk. Forwarding shape
   machine-verified; target semantics not recovered. */

undefined4 thunk_FUN_0007552e(undefined4 param_1, undefined4 param_2)

{
  return FUN_0007552e(param_1, ((int *)camry_host_ptr((uint32_t)(param_2))));
}



undefined4 FUN_00075642(void)

{
  int iVar1;
  undefined4 uVar2;
  
  if (DAT_febf6c55 == '\x01') {
    iVar1 = FUN_000783d4();
    if (iVar1 == 1) {
      f33_run_init_chain_75042(1);
      uVar2 = 0;
    }
    else {
      uVar2 = 8;
      f33_nvm_mark_physical_attempt_error();
      FUN_0007699c();
    }
  }
  else {
    uVar2 = 7;
  }
  return uVar2;
}



uint FUN_00075678(uint param_1)

{
  return 1 << (1 << (param_1 & 0x1f) & 3U) & 3;
}



undefined4 FUN_0007568e(void)

{
  undefined4 uVar1;
  
  if (DAT_febf6c55 == '\x01') {
    uVar1 = FUN_000783d4();
    f33_run_init_chain_75042(uVar1);
    uVar1 = 0;
  }
  else {
    uVar1 = 9;
  }
  return uVar1;
}



void FUN_000756b2(void)

{
  undefined4 uVar1;
  undefined4 uVar2;
  int iVar3;
  undefined4 uVar4;
  
  uVar1 = FUN_00077c9e();
  uVar2 = FUN_00077cde();
  DAT_febf6c55 = 0;
  FUN_00076f4e(uVar1, DAT_febf6c3e, ((uchar *)camry_host_ptr((uint32_t)(uVar2))), 0);
  iVar3 = FUN_00075642();
  if (iVar3 == 8) {
    uVar4 = FUN_00075678(DAT_febf6c3e);
    DAT_febf6c55 = 0;
    FUN_00076f4e(uVar1, uVar4, ((uchar *)camry_host_ptr((uint32_t)(uVar2))), 0);
    FUN_0007568e();
  }
  return;
}



undefined4 FUN_00075708(void)

{
  thunk_FUN_00077824();
  return FUN_00075642();
}



undefined4 FUN_00075718(void)

{
  undefined4 uVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  
  uVar1 = FUN_00075678(DAT_febf6c3e);
  uVar2 = FUN_00077c9e();
  uVar3 = FUN_00077cde();
  DAT_febf6c55 = 0;
  FUN_00076f4e(uVar2, uVar1, ((uchar *)camry_host_ptr((uint32_t)(uVar3))), 0);
  return FUN_0007568e();
}



undefined4 FUN_00075750(void)

{
  thunk_FUN_00077824();
  return FUN_0007568e();
}



undefined4 FUN_00075760(void)

{
  int iVar1;
  undefined4 uVar2;
  
  if (DAT_febf6c55 == '\x01') {
    iVar1 = FUN_000783d4();
    if (iVar1 == 1) {
      DAT_febf6c54 = 1;
      uVar2 = 0xf;
      DAT_febf6c40 = DAT_febf6c3e;
    }
    else {
      uVar2 = 0xc;
      f33_nvm_mark_physical_attempt_error();
    }
  }
  else {
    uVar2 = 0xb;
  }
  return uVar2;
}



undefined4 FUN_000757a4(char param_1,undefined4 *param_2)

{
  int iVar1;
  undefined4 uVar2;
  
  if (DAT_febf6c55 == '\x01') {
    iVar1 = FUN_000783d4();
    if (iVar1 == 1) {
      DAT_febf6c54 = 2;
      DAT_febf6c40 = FUN_00075678(DAT_febf6c3e);
      uVar2 = 0xf;
    }
    else if (param_1 == '\x01') {
      uVar2 = 0x1d;
      f33_nvm_mark_physical_attempt_error();
    }
    else {
      uVar2 = 0;
      if (param_1 == '\x02') {
        *param_2 = 0xfffc;
        FUN_0007699c();
      }
      else {
        *param_2 = camry_host_addr(((undefined *)camry_host_ptr(0xfffbu)));
      }
    }
  }
  else {
    uVar2 = 0xd;
  }
  return uVar2;
}



void FUN_00075818(undefined4 param_1,undefined4 param_2)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  int iVar4;
  undefined4 uVar5;
  
  iVar1 = FUN_00077c64();
  uVar2 = FUN_00077c9e();
  uVar3 = FUN_00077cde();
  DAT_febf6c55 = 0;
  if (iVar1 == 1) {
    FUN_0007708c(uVar2,DAT_febf6c3e,0);
  }
  else {
    FUN_00076f4e(uVar2, DAT_febf6c3e, ((uchar *)camry_host_ptr((uint32_t)(uVar3))), 0);
  }
  iVar4 = FUN_00075760();
  if (iVar4 == 0xc) {
    uVar5 = FUN_00075678(DAT_febf6c3e);
    DAT_febf6c55 = 0;
    if (iVar1 == 1) {
      FUN_0007708c(uVar2,uVar5,0);
    }
    else {
      FUN_00076f4e(uVar2, uVar5, ((uchar *)camry_host_ptr((uint32_t)(uVar3))), 0);
    }
    FUN_000757a4(iVar1, ((undefined4 *)camry_host_ptr((uint32_t)(param_2))));
  }
  return;
}



undefined4 FUN_00075892(void)

{
  int iVar1;
  
  iVar1 = FUN_00077c64();
  if (iVar1 == 1) {
    FUN_0007712a();
  }
  else {
    thunk_FUN_00077824();
  }
  return FUN_00075760();
}



undefined4 FUN_000758b0(undefined4 param_1,undefined4 param_2)

{
  undefined4 uVar1;
  undefined4 uVar2;
  int iVar3;
  undefined4 uVar4;
  
  uVar1 = FUN_00075678(DAT_febf6c3e);
  uVar2 = FUN_00077c9e();
  iVar3 = FUN_00077c64();
  uVar4 = FUN_00077cde();
  DAT_febf6c55 = 0;
  if (iVar3 == 1) {
    FUN_0007708c(uVar2,uVar1,0);
  }
  else {
    FUN_00076f4e(uVar2, uVar1, ((uchar *)camry_host_ptr((uint32_t)(uVar4))), 0);
  }
  return FUN_000757a4(iVar3, ((undefined4 *)camry_host_ptr((uint32_t)(param_2))));
}



undefined4 FUN_00075902(undefined4 param_1,undefined4 param_2)

{
  int iVar1;
  
  iVar1 = FUN_00077c64();
  if (iVar1 == 1) {
    FUN_0007712a();
  }
  else {
    thunk_FUN_00077824();
  }
  return FUN_000757a4(iVar1, ((undefined4 *)camry_host_ptr((uint32_t)(param_2))));
}



undefined4 FUN_00075928(int param_1,undefined4 param_2)

{
  undefined4 *puVar1;
  undefined4 uVar2;
  int iVar3;
  undefined4 uVar4;
  undefined4 *puVar5;
  undefined4 uVar6;
  undefined4 *puVar7;
  undefined4 local_28 [4];
  undefined1 uStack_18;
  
  puVar1 = local_28;
  uVar6 = 0xff;
  uVar2 = FUN_00077c9e();
  puVar7 = *(undefined4 **)(param_1 + 4);
  puVar5 = puVar7 + 5;
  do {
    uVar4 = *puVar7;
    puVar7 = puVar7 + 1;
    *puVar1 = uVar4;
    puVar1 = puVar1 + 1;
  } while ((uintptr_t)(puVar5)!=(uintptr_t)(puVar7));
  iVar3 = FUN_00074f88(uStack_18);
  if ((iVar3 != 0) && (iVar3 = camry_host_addr(FUN_0007808c(uVar2,DAT_febf6c3e,2)), iVar3 != 2)) {
    uVar6 = FUN_000750b2(((undefined *)camry_host_ptr((uint32_t)(iVar3))), ((undefined4 *)camry_host_ptr((uint32_t)(param_2))));
  }
  return uVar6;
}



undefined4 FUN_00075982(undefined4 param_1, undefined4 param_2)

{
  FUN_00074f72();
  return FUN_00075928(param_1, param_2);
}



/* Far-call trampoline: prepare {lp},0 / jarl 0x75928 / dispose 0,{lp},lp; byte-verified against the
   exact image. Forwards with registers and stack unchanged; marked as a thunk. Forwarding shape
   machine-verified; target semantics not recovered. */

undefined4 thunk_FUN_00075928(undefined4 param_1, undefined4 param_2)

{
  return FUN_00075928(param_1, param_2);
}



undefined4 FUN_000759e2(undefined4 param_1,undefined4 param_2)

{
  undefined4 uVar1;
  undefined4 uVar2;
  int iVar3;
  undefined4 uVar4;
  
  uVar4 = 0xff;
  uVar1 = FUN_00077c9e();
  uVar2 = FUN_0007543c(DAT_febf6c3e);
  iVar3 = camry_host_addr(FUN_00076e36(uVar1,uVar2));
  if (iVar3 != 2) {
    uVar4 = FUN_000750b2(((undefined *)camry_host_ptr((uint32_t)(iVar3))), ((undefined4 *)camry_host_ptr((uint32_t)(param_2))));
  }
  return uVar4;
}



undefined4 FUN_00075a1a(undefined4 param_1,undefined4 param_2)

{
  uint32_t puVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  
  puVar1 = 0x23dfcu;
  iVar2 = FUN_000783d4();
  uVar3 = FUN_00077c9e();
  if (iVar2 == 1) {
    uVar3 = 0x10;
  }
  else {
    if (DAT_febf6c52 < (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x3b2f)))))) {
      DAT_febf6c52 = DAT_febf6c52 + 1;
      uVar4 = FUN_0007543c(DAT_febf6c3e);
      iVar2 = camry_host_addr(FUN_00076e36(uVar3,uVar4));
      if (iVar2 == 2) {
        return 0xff;
      }
    }
    uVar3 = FUN_000750b2(((undefined *)camry_host_ptr((uint32_t)(iVar2))), ((undefined4 *)camry_host_ptr((uint32_t)(param_2))));
  }
  return uVar3;
}



undefined4 FUN_00075a78(undefined4 param_1,undefined4 param_2)

{
  undefined4 uVar1;
  undefined4 uVar2;
  int iVar3;
  undefined4 uVar4;
  
  uVar4 = 0xff;
  uVar1 = FUN_00077c9e();
  uVar2 = FUN_0007543c(DAT_febf6c3e);
  iVar3 = camry_host_addr(FUN_0007723c(uVar1,uVar2,DAT_febf6c40));
  if (iVar3 != 2) {
    uVar4 = FUN_000750b2(((undefined *)camry_host_ptr((uint32_t)(iVar3))), ((undefined4 *)camry_host_ptr((uint32_t)(param_2))));
  }
  return uVar4;
}



undefined4 FUN_00075ab8(undefined4 param_1,undefined4 param_2)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = FUN_000783d4();
  if (iVar1 == 1) {
    uVar2 = 0x11;
  }
  else {
    uVar2 = FUN_000750fe(iVar1,param_2);
  }
  return uVar2;
}



undefined4 FUN_00075ad8(int param_1,undefined4 param_2)

{
  undefined4 *puVar1;
  undefined4 uVar2;
  int iVar3;
  undefined4 uVar4;
  undefined4 *puVar5;
  undefined4 uVar6;
  undefined4 *puVar7;
  undefined4 local_28 [4];
  undefined1 uStack_18;
  
  puVar1 = local_28;
  uVar6 = 0xff;
  uVar2 = FUN_00077c9e();
  puVar7 = *(undefined4 **)(param_1 + 4);
  puVar5 = puVar7 + 5;
  do {
    uVar4 = *puVar7;
    puVar7 = puVar7 + 1;
    *puVar1 = uVar4;
    puVar1 = puVar1 + 1;
  } while ((uintptr_t)(puVar5)!=(uintptr_t)(puVar7));
  iVar3 = FUN_00074f88(uStack_18);
  if ((iVar3 != 0) && (iVar3 = camry_host_addr(FUN_0007808c(uVar2,DAT_febf6c3e,1)), iVar3 != 2)) {
    uVar6 = FUN_000750b2(((undefined *)camry_host_ptr((uint32_t)(iVar3))), ((undefined4 *)camry_host_ptr((uint32_t)(param_2))));
  }
  return uVar6;
}



undefined4 FUN_00075b32(undefined4 param_1, undefined4 param_2)

{
  FUN_00074f72();
  return FUN_00075ad8(param_1, param_2);
}



/* Far-call trampoline: prepare {lp},0 / jarl 0x75AD8 / dispose 0,{lp},lp; byte-verified against the
   exact image. Forwards with registers and stack unchanged; marked as a thunk. Forwarding shape
   machine-verified; target semantics not recovered. */

undefined4 thunk_FUN_00075ad8(undefined4 param_1, undefined4 param_2)

{
  return FUN_00075ad8(param_1, param_2);
}



undefined1 FUN_00075b4e(undefined4 *param_1)

{
  char cVar1;
  undefined1 uVar2;
  int iVar3;
  
  cVar1 = DAT_febf6c54 + -1;
  DAT_febf6c54 = cVar1;
  DAT_febf6c3e = FUN_0007543c(DAT_febf6c3e);
  if (cVar1 == '\0') {
    DAT_febf6c53 = 2;
    iVar3 = FUN_00077c64();
    if (iVar3 == 1) {
      uVar2 = 2;
      DAT_febf6c52 = 0;
    }
    else if (iVar3 == 2) {
      uVar2 = 6;
    }
    else {
      *param_1 = camry_host_addr(((undefined *)camry_host_ptr(0xfffbu)));
      uVar2 = 0;
    }
  }
  else {
    uVar2 = 0xe;
    DAT_febf6c40 = DAT_febf6c3e;
  }
  return uVar2;
}



undefined * FUN_00075bfe(undefined2 param_1,undefined1 param_2)

{
  undefined4 uVar1;
  
  uVar1 = FUN_00077c9e();
  return FUN_0007808c(uVar1,param_1,param_2);
}



undefined * FUN_00075c1c(undefined2 param_1)

{
  undefined4 uVar1;
  
  uVar1 = FUN_00077c9e();
  return FUN_00076e36(uVar1,param_1);
}



void FUN_00075c34(undefined2 param_1)

{
  undefined4 uVar1;
  undefined4 uVar2;
  
  uVar1 = FUN_00077c9e();
  uVar2 = FUN_00077cbe();
  FUN_00076e6a(uVar1,param_1,uVar2);
  return;
}



undefined4 FUN_00075c76(undefined4 param_1,undefined4 *param_2)

{
  undefined *puVar1;
  undefined4 uVar2;
  
  puVar1 = (undefined *)FUN_000783d4();
  if ((uintptr_t)(puVar1)==(uintptr_t)(((undefined *)camry_host_ptr((uint32_t)(0x1))))) {
    uVar2 = 0x13;
  }
  else {
    *param_2 = camry_host_addr(puVar1);
    uVar2 = 0;
    if ((uintptr_t)(puVar1)==(uintptr_t)(((undefined *)camry_host_ptr(0xfffdu)))) {
      FUN_00076992();
    }
  }
  return uVar2;
}



undefined4 FUN_00075cc2(undefined4 param_1,undefined4 *param_2)

{
  undefined *puVar1;
  undefined4 uVar2;
  
  puVar1 = (undefined *)FUN_000783d4();
  if ((uintptr_t)(puVar1)==(uintptr_t)(((undefined *)camry_host_ptr((uint32_t)(0x1))))) {
    uVar2 = 0x14;
  }
  else {
    *param_2 = camry_host_addr(puVar1);
    uVar2 = 0;
    if ((uintptr_t)(puVar1)==(uintptr_t)(((undefined *)camry_host_ptr(0xfffdu)))) {
      FUN_00076992();
    }
  }
  return uVar2;
}



undefined4 FUN_00075d0c(undefined4 param_1,int *param_2)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = FUN_000783d4();
  if (iVar1 == 1) {
    uVar2 = 0x15;
  }
  else {
    *param_2 = iVar1;
    uVar2 = 0;
  }
  return uVar2;
}



undefined4 FUN_00075d4a(undefined4 param_1,int *param_2)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = FUN_000783d4();
  if (iVar1 == 1) {
    uVar2 = 0x16;
  }
  else {
    *param_2 = iVar1;
    uVar2 = 0;
  }
  return uVar2;
}



undefined4 FUN_00075d88(undefined4 param_1,int *param_2)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = FUN_000783d4();
  if (iVar1 == 1) {
    uVar2 = 0x17;
  }
  else {
    *param_2 = iVar1;
    uVar2 = 0;
  }
  return uVar2;
}



undefined4 FUN_00075dc6(undefined4 param_1,undefined4 *param_2)

{
  undefined *puVar1;
  undefined4 uVar2;
  
  puVar1 = (undefined *)FUN_000783d4();
  if ((uintptr_t)(puVar1)==(uintptr_t)(((undefined *)camry_host_ptr((uint32_t)(0x1))))) {
    uVar2 = 0x18;
  }
  else {
    *param_2 = camry_host_addr(puVar1);
    uVar2 = 0;
    if ((uintptr_t)(puVar1)==(uintptr_t)(((undefined *)camry_host_ptr(0xfffdu)))) {
      FUN_00076992();
    }
  }
  return uVar2;
}



undefined4 FUN_00075e10(undefined4 param_1,undefined4 *param_2)

{
  undefined *puVar1;
  undefined4 uVar2;
  
  puVar1 = (undefined *)FUN_000783d4();
  if ((uintptr_t)(puVar1)==(uintptr_t)(((undefined *)camry_host_ptr((uint32_t)(0x1))))) {
    uVar2 = 0x19;
  }
  else {
    *param_2 = camry_host_addr(puVar1);
    uVar2 = 0;
    if ((uintptr_t)(puVar1)==(uintptr_t)(((undefined *)camry_host_ptr(0xfffdu)))) {
      FUN_00076992();
    }
  }
  return uVar2;
}



undefined4 FUN_00075e5c(undefined4 param_1,undefined4 *param_2)

{
  undefined *puVar1;
  undefined4 uVar2;
  
  puVar1 = (undefined *)FUN_000783d4();
  if ((uintptr_t)(puVar1)==(uintptr_t)(((undefined *)camry_host_ptr((uint32_t)(0x1))))) {
    uVar2 = 0x1a;
  }
  else {
    *param_2 = camry_host_addr(puVar1);
    uVar2 = 0;
    if ((uintptr_t)(puVar1)==(uintptr_t)(((undefined *)camry_host_ptr(0xfffdu)))) {
      FUN_00076992();
    }
  }
  return uVar2;
}



undefined4 FUN_00075ea8(undefined4 param_1,undefined4 *param_2)

{
  undefined *puVar1;
  undefined4 uVar2;
  
  puVar1 = (undefined *)FUN_000783d4();
  if ((uintptr_t)(puVar1)==(uintptr_t)(((undefined *)camry_host_ptr((uint32_t)(0x1))))) {
    uVar2 = 0x1b;
  }
  else {
    *param_2 = camry_host_addr(puVar1);
    uVar2 = 0;
    if ((uintptr_t)(puVar1)==(uintptr_t)(((undefined *)camry_host_ptr(0xfffdu)))) {
      FUN_00076992();
    }
  }
  return uVar2;
}



undefined4 FUN_00075ef4(undefined4 param_1,undefined4 *param_2)

{
  undefined *puVar1;
  undefined4 uVar2;
  
  puVar1 = (undefined *)FUN_000783d4();
  if ((uintptr_t)(puVar1)==(uintptr_t)(((undefined *)camry_host_ptr((uint32_t)(0x1))))) {
    uVar2 = 0x1c;
  }
  else {
    *param_2 = camry_host_addr(puVar1);
    uVar2 = 0;
    if ((uintptr_t)(puVar1)==(uintptr_t)(((undefined *)camry_host_ptr(0xfffdu)))) {
      FUN_00076992();
    }
  }
  return uVar2;
}



undefined4 FUN_00075f64(undefined4 param_1, undefined4 param_2)

{
  FUN_00074f72();
  return FUN_00075f1e(param_1, ((int *)camry_host_ptr((uint32_t)(param_2))));
}



/* Far-call trampoline: prepare {lp},0 / jarl 0x75F1E / dispose 0,{lp},lp; byte-verified against the
   exact image. Forwards with registers and stack unchanged; marked as a thunk. Forwarding shape
   machine-verified; target semantics not recovered. */

undefined4 thunk_FUN_00075f1e(undefined4 param_1, undefined4 param_2)

{
  return FUN_00075f1e(param_1, ((int *)camry_host_ptr((uint32_t)(param_2))));
}



undefined4 FUN_00075fb0(undefined *param_1,undefined4 *param_2)

{
  undefined4 uVar1;
  
  if (DAT_febf6c52 < DAT_0002792b) {
    DAT_febf6c52 = DAT_febf6c52 + 1;
    uVar1 = 0x1d;
  }
  else {
    *param_2 = camry_host_addr(param_1);
    uVar1 = 0;
    if ((uintptr_t)(param_1)==(uintptr_t)(((undefined *)camry_host_ptr(0xfffdu)))) {
      FUN_00076992();
    }
  }
  return uVar1;
}



undefined4 FUN_00075fe4(undefined4 param_1,int *param_2)

{
  undefined4 uVar1;
  undefined4 uVar2;
  int iVar3;
  undefined4 uVar4;
  
  uVar4 = 0xff;
  uVar1 = FUN_00077c9e();
  uVar2 = FUN_0007543c(DAT_febf6c3e);
  iVar3 = camry_host_addr(FUN_00076e36(uVar1,uVar2));
  if (iVar3 != 2) {
    *param_2 = iVar3;
    uVar4 = 0;
  }
  return uVar4;
}



undefined4 FUN_00076018(undefined4 param_1,int *param_2)

{
  uint32_t puVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  
  puVar1 = 0x23dfcu;
  iVar2 = FUN_000783d4();
  uVar3 = FUN_00077c9e();
  if (iVar2 == 1) {
    uVar3 = 0x1e;
  }
  else {
    if (DAT_febf6c52 < (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x3b2f)))))) {
      DAT_febf6c52 = DAT_febf6c52 + 1;
      uVar4 = FUN_0007543c(DAT_febf6c3e);
      iVar2 = camry_host_addr(FUN_00076e36(uVar3,uVar4));
      if (iVar2 == 2) {
        return 0xff;
      }
    }
    *param_2 = iVar2;
    uVar3 = 0;
  }
  return uVar3;
}



undefined4 FUN_00076072(undefined4 param_1,int *param_2)

{
  undefined4 uVar1;
  undefined4 uVar2;
  int iVar3;
  undefined4 uVar4;
  
  uVar4 = 0xff;
  uVar1 = FUN_00077c9e();
  uVar2 = FUN_0007543c(DAT_febf6c3e);
  iVar3 = camry_host_addr(FUN_00076f04(uVar1,uVar2));
  if (iVar3 != 2) {
    *param_2 = iVar3;
    uVar4 = 0;
  }
  return uVar4;
}



undefined4 FUN_000760a6(undefined4 param_1,undefined4 param_2)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = FUN_000783d4();
  if (iVar1 == 1) {
    uVar2 = 0x1f;
  }
  else {
    uVar2 = FUN_00075fb0(((undefined *)camry_host_ptr((uint32_t)(iVar1))), ((undefined4 *)camry_host_ptr((uint32_t)(param_2))));
  }
  return uVar2;
}



undefined4 FUN_000760c6(int param_1,int *param_2)

{
  undefined4 *puVar1;
  undefined4 uVar2;
  int iVar3;
  undefined4 uVar4;
  undefined4 *puVar5;
  undefined4 uVar6;
  undefined4 *puVar7;
  undefined4 local_28 [4];
  undefined1 uStack_18;
  
  puVar1 = local_28;
  uVar6 = 0xff;
  uVar2 = FUN_00077c9e();
  puVar7 = *(undefined4 **)(param_1 + 4);
  puVar5 = puVar7 + 5;
  do {
    uVar4 = *puVar7;
    puVar7 = puVar7 + 1;
    *puVar1 = uVar4;
    puVar1 = puVar1 + 1;
  } while ((uintptr_t)(puVar5)!=(uintptr_t)(puVar7));
  iVar3 = FUN_00074f88(uStack_18);
  if ((iVar3 != 0) && (iVar3 = camry_host_addr(FUN_0007808c(uVar2,DAT_febf6c3e,1)), iVar3 != 2)) {
    *param_2 = iVar3;
    uVar6 = 0;
  }
  return uVar6;
}



undefined4 FUN_0007611c(undefined4 param_1, undefined4 param_2)

{
  FUN_00074f72();
  return FUN_000760c6(param_1, ((int *)camry_host_ptr((uint32_t)(param_2))));
}



/* Far-call trampoline: prepare {lp},0 / jarl 0x760C6 / dispose 0,{lp},lp; byte-verified against the
   exact image. Forwards with registers and stack unchanged; marked as a thunk. Forwarding shape
   machine-verified; target semantics not recovered. */

undefined4 thunk_FUN_000760c6(undefined4 param_1, undefined4 param_2)

{
  return FUN_000760c6(param_1, ((int *)camry_host_ptr((uint32_t)(param_2))));
}



undefined4 FUN_00076138(undefined4 *param_1)

{
  uint32_t puVar1;
  uint uVar2;
  int iVar3;
  
  puVar1 = 0x23dfcu;
  DAT_febf6c3e = FUN_0007543c(DAT_febf6c3e);
  uVar2 = FUN_00077c9e();
  if (uVar2 < (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + 0x3b2c))))) {
    DAT_febf6c53 = 2;
    iVar3 = FUN_00077c64();
    if (iVar3 == 1) {
      DAT_febf6c52 = 0;
      return 2;
    }
    if (iVar3 == 2) {
      return 6;
    }
  }
  *param_1 = camry_host_addr(((undefined *)camry_host_ptr(0xfffbu)));
  return 0;
}



void FUN_000761e6(void)

{
  DAT_febf6c56 = 0;
  DAT_febf6c57 = 0;
  DAT_febf6c58 = 0;
  thunk_FUN_000772f8();
  return;
}



undefined4 FUN_0007620a(void)

{
  FUN_000761e6();
  return 1;
}



void FUN_00076224(undefined4 param_1)

{
  FUN_000783ca(param_1);
  FUN_000783c0(1);
  return;
}



void FUN_00076236(undefined4 param_1)

{
  FUN_000783ca(param_1);
  FUN_000783c0(2);
  return;
}



void FUN_00076248(undefined4 param_1)

{
  FUN_000783ca(param_1);
  DAT_febf6c58 = 1;
  return;
}



undefined4 FUN_00076298(undefined *param_1,undefined4 *param_2)

{
  undefined4 uVar1;
  
  if (DAT_febf6c57 < DAT_0002792c) {
    DAT_febf6c57 = DAT_febf6c57 + 1;
    uVar1 = 1;
  }
  else {
    *param_2 = camry_host_addr(param_1);
    uVar1 = 0;
    if ((uintptr_t)(param_1)==(uintptr_t)(((undefined *)camry_host_ptr(0xfffdu)))) {
      FUN_00076992();
    }
  }
  return uVar1;
}



undefined4 FUN_000762ca(void)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = FUN_00077c64();
  if (iVar1 == 1) {
    DAT_febf6c57 = 0;
    uVar2 = 1;
  }
  else if (iVar1 == 2) {
    uVar2 = 4;
  }
  else {
    uVar2 = 0xff;
  }
  return uVar2;
}



undefined4 FUN_00076316(undefined4 param_1,undefined4 param_2)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = FUN_000783d4();
  if (iVar1 == 1) {
    uVar2 = 2;
  }
  else {
    uVar2 = FUN_0007625e(iVar1, ((int *)camry_host_ptr((uint32_t)(param_2))));
  }
  return uVar2;
}



undefined4 FUN_00076360(undefined4 param_1,undefined4 param_2)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = FUN_000783d4();
  if (iVar1 == 1) {
    uVar2 = 3;
  }
  else {
    uVar2 = FUN_00076298(((undefined *)camry_host_ptr((uint32_t)(iVar1))), ((undefined4 *)camry_host_ptr((uint32_t)(param_2))));
  }
  return uVar2;
}



/* Single constant publisher: DAT_febf6c56 = 1; Shape-classified from the canonical corpus; the
   target cell is not yet named, so the written state's meaning is unknown. */

void FUN_0007637e(void)

{
  DAT_febf6c56 = 1;
  return;
}



undefined4 FUN_0007638a(char param_1)

{
  undefined4 uVar1;
  
  uVar1 = 0;
  if ((param_1 == '\0') && (DAT_febf6c56 == '\x01')) {
    DAT_febf6c56 = '\x02';
    uVar1 = 1;
  }
  return uVar1;
}



undefined4 FUN_000763a4(int param_1,int *param_2)

{
  undefined4 *puVar1;
  undefined4 uVar2;
  int iVar3;
  undefined4 uVar4;
  undefined4 *puVar5;
  undefined4 uVar6;
  undefined4 *puVar7;
  undefined4 local_28 [4];
  undefined1 uStack_18;
  
  puVar1 = local_28;
  uVar6 = 0xff;
  uVar2 = FUN_00077c9e();
  puVar7 = *(undefined4 **)(param_1 + 4);
  puVar5 = puVar7 + 5;
  do {
    uVar4 = *puVar7;
    puVar7 = puVar7 + 1;
    *puVar1 = uVar4;
    puVar1 = puVar1 + 1;
  } while ((uintptr_t)(puVar5)!=(uintptr_t)(puVar7));
  iVar3 = FUN_0007638a(uStack_18);
  if ((iVar3 != 0) && (iVar3 = camry_host_addr(FUN_00077a36(uVar2)), iVar3 != 2)) {
    *param_2 = iVar3;
    uVar6 = 0;
  }
  return uVar6;
}



undefined4 FUN_000763f0(undefined4 param_1, undefined4 param_2)

{
  FUN_0007637e();
  return FUN_000763a4(param_1, ((int *)camry_host_ptr((uint32_t)(param_2))));
}



/* Far-call trampoline: prepare {lp},0 / jarl 0x763A4 / dispose 0,{lp},lp; byte-verified against the
   exact image. Forwards with registers and stack unchanged; marked as a thunk. Forwarding shape
   machine-verified; target semantics not recovered. */

undefined4 thunk_FUN_000763a4(undefined4 param_1, undefined4 param_2)

{
  return FUN_000763a4(param_1, ((int *)camry_host_ptr((uint32_t)(param_2))));
}



/* Single constant publisher: DAT_febf6c56 = 0; Shape-classified from the canonical corpus; the
   target cell is not yet named, so the written state's meaning is unknown. */

void FUN_0007640c(void)

{
  DAT_febf6c56 = 0;
  return;
}



undefined4 FUN_00076456(void)

{
  undefined4 uVar1;
  
  if (DAT_febf6c58 == '\x01') {
    uVar1 = FUN_000783d4();
    FUN_00077ce8();
    FUN_00077d14(uVar1);
    f33_nvm_finish_physical_result();
    FUN_000761e6();
    uVar1 = 0;
  }
  else {
    uVar1 = 0xff;
  }
  return uVar1;
}



undefined4 FUN_0007648a(void)

{
  ushort handle;
  uchar *destination;
  
  handle = FUN_00077c9e();
  destination = (uchar *)FUN_00077cde();
  DAT_febf6c58 = 0;
  f33_nvm_begin_record_read(handle,destination,'\0');
  return FUN_00076456();
}



undefined4 FUN_000764b2(void)

{
  thunk_FUN_00077824();
  return FUN_00076456();
}



/* Single constant publisher: DAT_febf6b77 = 1; Shape-classified from the canonical corpus; the
   target cell is not yet named, so the written state's meaning is unknown. */

void FUN_000764c2(void)

{
  DAT_febf6b77 = 1;
  return;
}



void FUN_000764ce(void)

{
  f33_nvm_physical_result_state = '\0';
  FUN_000764c2();
  return;
}



/* Sequential initializer chain: 8 unconditional calls and no other statements; shape-verified. The
   called sequence is the function's entire behavior; chain family members differ in callee sets. */

void f33_run_init_chain_764e2(void)

{
  f33_nvm_initialize_dataflash_read_controls();
  FUN_000764ce();
  thunk_FUN_00076782();
  FUN_000781a0();
  FUN_00077c32();
  thunk_FUN_00074b3c();
  FUN_000782de();
  f33_return_only_stub_7936c();
  return;
}



undefined2 FUN_0007650c(undefined2 param_1)

{
  return param_1;
}



undefined4 FUN_00076512(undefined2 param_1,undefined4 param_2)

{
  uint32_t puVar1;
  int iVar2;
  undefined4 uVar3;
  
  puVar1 = 0x23dfcu;
  uVar3 = 1;
  iVar2 = FUN_00077c64();
  if (iVar2 == 0) {
    iVar2 = camry_host_addr(FUN_00077c82(param_1));
    if ((iVar2 == 1) && (iVar2 = camry_host_addr(FUN_00077cc8(param_2)), iVar2 == 1)) {
      FUN_00077c5a(2);
      FUN_000783de((*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x3b1c)))));
      uVar3 = 0;
    }
    else {
      uVar3 = 2;
    }
  }
  return uVar3;
}



undefined4 FUN_00076572(undefined2 param_1,undefined4 param_2,undefined4 param_3)

{
  uchar result_class;
  undefined4 uVar1;
  int iVar2;
  
  FUN_00077c6e((uint)(ushort)param_1);
  uVar1 = FUN_0007650c(param_1);
  iVar2 = FUN_00076512(uVar1,param_3);
  if (iVar2 == 0) {
    f33_nvm_set_physical_result_state('\x02');
    FUN_00076af4();
    uVar1 = 0;
  }
  else {
    uVar1 = 1;
    if (iVar2 == 2) {
      result_class = '\"';
    }
    else {
      result_class = '!';
    }
    f33_nvm_report_physical_class(result_class);
  }
  return uVar1;
}



undefined4 FUN_000765ba(undefined2 param_1,undefined4 param_2)

{
  uint32_t puVar1;
  int iVar2;
  undefined4 uVar3;
  
  puVar1 = 0x23dfcu;
  uVar3 = 1;
  iVar2 = FUN_00077c64();
  if (iVar2 == 0) {
    iVar2 = camry_host_addr(FUN_00077c82(param_1));
    if ((iVar2 == 1) && (iVar2 = camry_host_addr(FUN_00077ca8(param_2)), iVar2 == 1)) {
      FUN_00077c5a(1);
      FUN_000783de((*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x3b1c)))));
      uVar3 = 0;
    }
    else {
      uVar3 = 2;
    }
  }
  return uVar3;
}



undefined4 FUN_000765fc(undefined2 param_1,undefined4 param_2)

{
  uchar result_class;
  undefined4 uVar1;
  int iVar2;
  
  FUN_00077c6e((uint)(ushort)param_1);
  uVar1 = FUN_0007650c(param_1);
  iVar2 = FUN_000765ba(uVar1,param_2);
  if (iVar2 == 0) {
    f33_nvm_set_physical_result_state('\x02');
    FUN_00076af4();
    uVar1 = 0;
  }
  else {
    uVar1 = 1;
    if (iVar2 == 2) {
      result_class = '\"';
    }
    else {
      result_class = '!';
    }
    f33_nvm_report_physical_class(result_class);
  }
  return uVar1;
}



/* Single constant publisher: DAT_febf6b77 = 0; Shape-classified from the canonical corpus; the
   target cell is not yet named, so the written state's meaning is unknown. */

void FUN_00076644(void)

{
  DAT_febf6b77 = 0;
  return;
}



/* Reset completion context77C32 and both registered banks782DE. Enter 79AAA, clear6B77; if6CD0==0
   call74E94 (actual lower cancellation) then set6B77=1, ignoring74E94's result. Leave79ABE; request
   primary state3 and secondary state5, then76ADA's no-op hook. Native explicit B3 completion and
   interference skip; B3 timeout reaches command-area halfword reads not yet modeled. Reset
   contexts/both registered banks, enter paired guard, clear6B77. If6CD0==0 run74E94 and set6B77=1
   ignoring its result. Leave guard; request primary3/secondary5 and no-op notification. Native
   explicit B3 completion and interference skip verify cleanup/transitions; B3-timeout command-area
   halfword reads remain a model boundary. */

void f33_nvm_cancel_physical_operation(void)

{
  int iVar1;
  
  FUN_00077c32();
  FUN_000782de();
  FUN_00079aaa();
  FUN_00076644();
  iVar1 = FUN_00079b0e();
  if (iVar1 == 0) {
    FUN_00074e94();
    FUN_000764c2();
  }
  FUN_00079abe();
  f33_nvm_set_physical_result_state('\x03');
  FUN_00076ae6();
  f33_return_only_stub_73ca2();
  return;
}



undefined4 FUN_00076688(void)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = FUN_00077c64();
  if (iVar1 == 1 || iVar1 == 2) {
    uVar2 = 2;
  }
  else if ((DAT_febf6b77 == '\0') || (iVar1 = FUN_00074e6e(), iVar1 != 1 && iVar1 != 2)) {
    uVar2 = 1;
  }
  else {
    uVar2 = 3;
  }
  return uVar2;
}



/* Far-call trampoline: prepare {lp},0 / jarl 0x76688 / dispose 0,{lp},lp; byte-verified against the
   exact image. Forwards with registers and stack unchanged; marked as a thunk. Forwarding shape
   machine-verified; target semantics not recovered. */

undefined4 thunk_FUN_00076688(void)

{
  return FUN_00076688();
}



uchar FUN_000766c6(void)

{
  return f33_nvm_physical_result_state;
}



void FUN_000766f4(void)

{
  int iVar1;
  
  FUN_00079aaa();
  iVar1 = FUN_00079c76();
  if (iVar1 == 0) {
    FUN_00079388();
    FUN_000781be();
    FUN_00074e46(0);
    FUN_00077c42();
    FUN_00078466();
  }
  FUN_00079abe();
  return;
}



/* Low8 class0 sets6B76=0 and calls76ACE. Class83 sets4; other nonzero classes set1, report the
   class and call76ADA. Their73CA0/73CA2 targets are JMPLP leaves, not logical publication. Extra
   r7/r8/r9 prepared by77D66 are not consumed in this implementation. Class0 sets result-state0;83
   sets4; other nonzero sets1 and reports class. Actual completion hooks terminate at
   JMPLP73CA0/73CA2; this is not logical/application publication. Extra prepared r7-r9 are unused.
    */

void f33_nvm_publish_physical_class(uchar result_class)

{
  uchar state;
  
  if (result_class == '\0') {
    f33_nvm_set_physical_result_state('\0');
    f33_return_only_stub_73ca0();
  }
  else {
    if (result_class == 0x83) {
      state = '\x04';
    }
    else {
      state = '\x01';
    }
    f33_nvm_set_physical_result_state(state);
    f33_nvm_report_physical_class(result_class);
    f33_return_only_stub_73ca2();
  }
  return;
}



/* Far-call trampoline: prepare {lp},0 / jarl 0x764C2 / dispose 0,{lp},lp; byte-verified against the
   exact image. Forwards with registers and stack unchanged; marked as a thunk. Forwarding shape
   machine-verified; target semantics not recovered. */

void thunk_FUN_000764c2(void)

{
  FUN_000764c2();
  return;
}



bool FUN_00076762(void)

{
  return DAT_febf6b77 != '\0';
}



void FUN_00076772(void)

{
  FUN_00074e94();
  FUN_000764c2();
  return;
}



void FUN_00076782(void)

{
  f33_nvm_secondary_result_state = '\0';
  f33_nvm_physical_attempt_flags = '\0';
  return;
}



void FUN_00076794(void)

{
  f33_nvm_physical_attempt_flags = '\0';
  return;
}



/* WARNING: Inlined function: f33_nvm_descriptor_option */

void FUN_0007679e(void)

{
  char cVar1;
  undefined1 uVar2;
  uint32_t puVar3;
  uint uVar4;
  int iVar5;
  
  puVar3 = 0x23dfcu;
  uVar4 = FUN_00077c9e();
  iVar5 = FUN_00077c64();
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)((uVar4 & 0xffff) * 6 + 0x383c)))));
  DAT_febf6b70 = FUN_00077c78();
  uVar2 = 0;
  if ((iVar5 == 2) || (uVar2 = 1, iVar5 == 1)) {
    DAT_febf6b74 = uVar2;
  }
  if ((cVar1 == '\0') || (cVar1 == '\x01')) {
    DAT_febf6b75 = cVar1;
  }
  return;
}



void FUN_000767ea(void)

{
  int iVar1;
  
  FUN_00079aaa();
  iVar1 = FUN_00079c76();
  if (iVar1 == 0) {
    FUN_00074e46(1);
    FUN_0007840c();
  }
  FUN_00079abe();
  return;
}



undefined4 FUN_0007682e(undefined4 param_1,undefined2 param_2,undefined4 param_3)

{
  int iVar1;
  undefined4 uVar2;
  
  FUN_00079aaa();
  iVar1 = FUN_00079b0e();
  if (iVar1 == 0) {
    iVar1 = FUN_00074c54(param_1, param_2, ((uchar *)camry_host_ptr((uint32_t)(param_3))), 0xb, 0);
    uVar2 = 8;
    if (iVar1 == 2) {
      uVar2 = 7;
      f33_nvm_set_secondary_result_state('\x01');
    }
  }
  else {
    uVar2 = 9;
  }
  FUN_00079abe();
  return uVar2;
}



/* Enter actual paired guards. Mirrored interference returns9; otherwise start reverse-block driver
   with low16 count and callback selector0B. Driver2 publishes secondary pending1 and returns7;
   other driver results return8. Always leave guard. Successful command submission remains a
   hardware dependency. */

uint f33_nvm_guarded_erase_admission(uint byte_offset,uint page_count)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  
  FUN_00079aaa();
  iVar1 = FUN_00079b0e();
  if (iVar1 == 0) {
    uVar2 = f33_nvm_start_reverse_erase(byte_offset,page_count & 0xffff,0xb);
    uVar3 = 8;
    if (uVar2 == 2) {
      uVar3 = 7;
      f33_nvm_set_secondary_result_state('\x01');
    }
  }
  else {
    uVar3 = 9;
  }
  FUN_00079abe();
  return uVar3;
}



/* Enter paired guards. If mirrored interference is clear, execute79388,781BE,74E46(1); publish the
   interference predicate through79C56 and leave guard. Physical sequencer completion remains
   separately bounded. */

void f33_nvm_guarded_direct_poll(void)

{
  int iVar1;
  
  FUN_00079aaa();
  iVar1 = FUN_00079b0e();
  if (iVar1 == 0) {
    FUN_00079388();
    FUN_000781be();
    FUN_00074e46(1);
  }
  FUN_00079c56(iVar1 != 0);
  FUN_00079abe();
  return;
}



undefined4 FUN_000768e8(uint param_1,ushort param_2,uchar *param_3)

{
  int iVar1;
  uint uVar2;
  undefined4 uVar3;
  
  FUN_00079aaa();
  iVar1 = FUN_00079b0e();
  if (iVar1 == 0) {
    uVar2 = f33_nvm_read_with_optional_blank_check(param_1,param_2,param_3,'\0');
    if (uVar2 == 1) {
      uVar3 = 0;
    }
    else if (uVar2 == 0xffff0000) {
      uVar3 = 6;
    }
    else {
      uVar3 = 4;
    }
  }
  else {
    uVar3 = 9;
  }
  FUN_00079abe();
  return uVar3;
}



/* Enter paired-call guard79AAA; nonzero6CD0 returns9 without reading. Otherwise
   call74D78(offset,low16 count,64-byte local buffer,1): result1->3, 3->2,FFFF0000->6,other->4.
   Always79ABE before return. 68A6C passes64; the surrounding region check is not a
   local-buffer-size check. Paired guard entry/exit;6CD0!=0 gives9. Otherwise74D78(offset,low16
   length,64-byte local buffer,1), map1->3/3->2/FFFF0000->6/other->4. All five result branches
   executed through real callees. Region guard does not enforce local-buffer size;68A6C uses64. */

uint f33_nvm_probe_storage_range(uint byte_offset,ushort byte_count)

{
  int iVar1;
  uint uVar2;
  uchar auStack_4c [64];
  
  FUN_00079aaa();
  iVar1 = FUN_00079b0e();
  if (iVar1 == 0) {
    uVar2 = f33_nvm_read_with_optional_blank_check(byte_offset,byte_count,auStack_4c,'\x01');
    if (uVar2 == 1) {
      uVar2 = 3;
    }
    else if (uVar2 == 3) {
      uVar2 = 2;
    }
    else if (uVar2 == 0xffff0000) {
      uVar2 = 6;
    }
    else {
      uVar2 = 4;
    }
  }
  else {
    uVar2 = 9;
  }
  FUN_00079abe();
  return uVar2;
}



/* SET1 bit0 of6B73; preserve other bits. Invoked before completion dispatch gates. SET1 bit0 of6B73
   preserves other bits. Real completion path exercises it before mode/handle dispatch gating. */

void f33_nvm_mark_physical_attempt_error(void)

{
  f33_nvm_physical_attempt_flags = f33_nvm_physical_attempt_flags | 1;
  return;
}



void FUN_00076988(void)

{
  f33_nvm_physical_attempt_flags = f33_nvm_physical_attempt_flags | 2;
  return;
}



void FUN_00076992(void)

{
  f33_nvm_physical_attempt_flags = f33_nvm_physical_attempt_flags | 4;
  return;
}



void FUN_0007699c(void)

{
  f33_nvm_physical_attempt_flags = f33_nvm_physical_attempt_flags | 8;
  return;
}



uchar FUN_000769a6(undefined2 *param_1,undefined1 *param_2,undefined1 *param_3)

{
  *param_1 = DAT_febf6b70;
  *param_2 = DAT_febf6b74;
  *param_3 = DAT_febf6b75;
  return f33_nvm_physical_attempt_flags;
}



/* ROM callback selector0B at27A10. Driver1 publishes secondary0, full32 FFFF0000 publishes6, all
   other values publish4 through7680C. Synthetic terminal-input execution is not physical erase
   completion. */

void f33_nvm_publish_erase_driver_result(uint driver_result)

{
  uchar state;
  
  if (driver_result == 1) {
    state = '\0';
  }
  else if (driver_result == 0xffff0000) {
    state = '\x06';
  }
  else {
    state = '\x04';
  }
  f33_nvm_set_secondary_result_state(state);
  return;
}



/* Zero-extend low8 then forward to76A3A; no independent event or callback semantics. Zero-extend
   low8 class and forward to76A3A. Actual composed native result reaches translated sticky mask; no
   independent event meaning assigned. */

void f33_nvm_report_class_byte(uchar result_class)

{
  f33_nvm_accumulate_result_class(result_class);
  return;
}



/* Far-call trampoline: prepare {lp},0 / jarl 0x79432 / dispose 0,{lp},lp; byte-verified against the
   exact image. Forwards with registers and stack unchanged; marked as a thunk. Forwarding shape
   machine-verified; target semantics not recovered. */

bool thunk_FUN_00079432(void)

{
  return FUN_00079432();
}



/* Far-call trampoline: prepare {lp},0 / jarl 0x79444 / dispose 0,{lp},lp; byte-verified against the
   exact image. Forwards with registers and stack unchanged; marked as a thunk. Forwarding shape
   machine-verified; target semantics not recovered. */

undefined4 thunk_FUN_00079444(void)

{
  return FUN_00079444();
}



void FUN_00076a8c(char param_1)

{
  if ((param_1 == '\0') || (param_1 == '\x01')) {
    FUN_000796be((uint)(byte)param_1);
  }
  return;
}



void FUN_00076aa2(char param_1)

{
  if (param_1 == '\0') {
    FUN_000796f4((uint)(byte)param_1);
  }
  return;
}



/* Far-call trampoline: prepare {lp},0 / jarl 0x76782 / dispose 0,{lp},lp; byte-verified against the
   exact image. Forwards with registers and stack unchanged; marked as a thunk. Forwarding shape
   machine-verified; target semantics not recovered. */

void thunk_FUN_00076782(void)

{
  FUN_00076782();
  return;
}



/* Zero-extend low8 and forward through769F6 to the class-mask mapper. Zero-extend low8 class
   then769F6. Verified within the complete physical result finalization path; no logical event
   callback here. */

void f33_nvm_report_physical_class(uchar result_class)

{
  f33_nvm_report_class_byte(result_class);
  return;
}



void FUN_00076ae6(void)

{
  f33_nvm_set_secondary_result_state('\x05');
  return;
}



void FUN_00076af4(void)

{
  FUN_00076794();
  FUN_0007679e();
  return;
}



undefined * FUN_00076b1c(void)

{
  undefined4 uVar1;
  int iVar2;
  undefined *puVar3;
  uchar auStack_c [4];
  
  puVar3 = ((undefined *)camry_host_ptr(0xfffbu));
  if ((DAT_febf6c44 < f33_nvm_descriptor_count) &&
     (puVar3 = (undefined *)f33_nvm_read_with_optional_blank_check(DAT_febf6c24,4,auStack_c,'\0'),(uintptr_t)(puVar3)==(uintptr_t)(((undefined *)camry_host_ptr((uint32_t)(0x1)))))) {
    uVar1 = thunk_FUN_0007490e((0xfebf6b80u));
    iVar2 = FUN_0007484a(uVar1, camry_host_addr(auStack_c), 2);
    if (iVar2 != 0) {
      puVar3 = ((undefined *)camry_host_ptr(0xfffdu));
    }
  }
  return puVar3;
}



undefined * FUN_00076b6e(void)

{
  ushort handle;
  uint32_t puVar1;
  undefined4 uVar2;
  uint uVar3;
  uint uVar4;
  int iVar5;
  undefined *puVar6;
  uchar auStack_54 [64];
  
  handle = DAT_febf6c44;
  iVar5 = DAT_febf6c24;
  puVar1 = 0x23dfcu;
  puVar6 = ((undefined *)camry_host_ptr(0xfffbu));
  uVar2 = FUN_000772b4((0xfebf6b80u));
  if (handle < (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + 0x3b2c))))) {
    uVar3 = f33_nvm_payload_page_count(handle);
    uVar3 = (uVar3 - f33_nvm_payload_chunks_remaining) * 0x40;
    uVar4 = f33_nvm_payload_chunk_length(handle,(ushort)uVar3);
    puVar6 = (undefined *)
             f33_nvm_read_with_optional_blank_check
                       (iVar5 + (uVar3 & 0xffff) + 4,(ushort)uVar4,auStack_54,'\0');
    if (((uintptr_t)(puVar6)==(uintptr_t)(((undefined *)camry_host_ptr((uint32_t)(0x1))))) && (iVar5 = FUN_0007484a(uVar2, camry_host_addr(auStack_54), uVar4), iVar5 != 0))
    {
      puVar6 = ((undefined *)camry_host_ptr(0xfffdu));
    }
  }
  return puVar6;
}



uint FUN_00076be8(ushort param_1)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  undefined1 auStack_4c [64];
  
  iVar1 = DAT_febf6c24;
  uVar2 = f33_nvm_payload_page_count(param_1);
  uVar2 = (uVar2 - f33_nvm_payload_chunks_remaining) * 0x40;
  uVar3 = f33_nvm_payload_chunk_length(param_1,(ushort)uVar2);
  FUN_00074872(camry_host_addr(auStack_4c), 0xff, uVar3);
  return FUN_00074c54(iVar1 + (uVar2 & 0xffff) + 4,uVar3,auStack_4c,5,0);
}



void FUN_00076c3e(int param_1)

{
  if ((param_1 == 1) && (param_1 = camry_host_addr(FUN_00076b1c()), param_1 == 1)) {
    param_1 = FUN_00076be8(DAT_febf6c44);
  }
  if (param_1 != 2) {
    FUN_0007849e();
    thunk_FUN_000772f8();
  }
  return;
}



/* WARNING: Inlined function: f33_nvm_payload_length */

uint FUN_00076c6e(ushort param_1)

{
  ushort uVar1;
  int iVar2;
  uint32_t puVar3;
  undefined4 uVar4;
  
  iVar2 = DAT_febf6c24;
  puVar3 = 0x23dfcu;
  uVar4 = FUN_000772ea((0xfebf6b80u));
  uVar1 = (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + (uint)param_1 * 6 + 0x383a))));
  FUN_000772e4((0xfebf6b80u),(int)0xffffffff);
  return FUN_00074c54(iVar2 + uVar1 + 4, 4, ((uchar *)camry_host_ptr((uint32_t)(uVar4))), 7, 0);
}



/* WARNING: Inlined function: f33_nvm_payload_length */

void FUN_00076cb2(int param_1)

{
  if (param_1 == 1) {
    f33_nvm_payload_chunks_remaining = f33_nvm_payload_chunks_remaining - 1;
    if (f33_nvm_payload_chunks_remaining == 0) {
      if (0x20 < f33_nvm_descriptors[DAT_febf6c44].payload_bytes) {
        param_1 = FUN_00076c6e(DAT_febf6c44);
      }
    }
    else {
      param_1 = FUN_00076be8((*((volatile uint16_t *)camry_host_ptr(0xfebf6c44u))));
    }
  }
  if (param_1 != 2) {
    ((void)(param_1), FUN_0007849e());
    thunk_FUN_000772f8();
  }
  return;
}



void FUN_00076d02(void)

{
  FUN_0007849e();
  thunk_FUN_000772f8();
  return;
}



void FUN_00076d12(ushort param_1)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  int iVar4;
  undefined4 uVar5;
  uint uVar6;
  
  iVar1 = DAT_febf6c24;
  uVar2 = f33_nvm_record_offset(param_1,DAT_febf6c42,0);
  uVar3 = f33_nvm_payload_page_count(param_1);
  uVar3 = (uVar3 - f33_nvm_payload_chunks_remaining) * 0x40;
  uVar6 = uVar3 & 0xffff;
  uVar3 = f33_nvm_payload_chunk_length(param_1,(ushort)uVar3);
  iVar4 = camry_host_addr(FUN_000776fa(uVar6 + 4 + uVar2,uVar3,((undefined *)camry_host_ptr(0xfebf6b90u)),0));
  if (iVar4 == 1) {
    uVar2 = f33_nvm_sum_bytes((ushort)uVar3,((undefined *)camry_host_ptr(0xfebf6b90u)));
    f33_nvm_checksum_accumulator = f33_nvm_checksum_accumulator + uVar2;
    FUN_000772ba((0xfebf6b80u), camry_host_addr(((undefined *)camry_host_ptr(0xfebf6b90u))));
    uVar5 = FUN_000772b4((0xfebf6b80u));
    FUN_00074c54(iVar1 + uVar6 + 4, uVar3, ((uchar *)camry_host_ptr((uint32_t)(uVar5))), 8, 0);
  }
  return;
}



/* WARNING: Inlined function: f33_nvm_allocation_pages */

undefined * FUN_00076e36(ushort param_1,ushort param_2)

{
  uint uVar1;
  int iVar2;
  uint uVar3;
  undefined *puVar4;
  uint uVar5;
  
  uVar5 = (uint)param_1;
  puVar4 = ((undefined *)camry_host_ptr(0x23dfcu));
  if (uVar5 < f33_nvm_descriptor_count) {
    uVar3 = f33_nvm_record_offset(param_1,param_2,0);
    uVar1 = (uint)*(ushort *)(puVar4 + uVar5 * 6 + 0x383a);
    if (0x20 < uVar1) {
      uVar1 = uVar1 + 4;
    }
    if (puVar4[uVar5 * 6 + 0x383c] == '\0') {
      iVar2 = uVar1 + 4;
    }
    else {
      iVar2 = uVar1 + 0xc;
    }
    puVar4 = (undefined *)FUN_00077650(uVar3,iVar2 + 0x40U >> 6);
  }
  else {
    puVar4 = ((undefined *)camry_host_ptr(0xfffbu));
  }
  return puVar4;
}



void FUN_00076e6a(ushort param_1,ushort param_2,int param_3)

{
  uint uVar1;
  
  if ((param_1 < f33_nvm_descriptor_count) && (param_3 != 0)) {
    DAT_febf6c44 = param_1;
    FUN_000772ba((0xfebf6b80u),param_3);
    uVar1 = f33_nvm_payload_page_count(param_1);
    f33_nvm_payload_chunks_remaining = (ushort)uVar1;
    DAT_febf6c24 = f33_nvm_record_offset(param_1,param_2,0);
    FUN_00077660(param_1);
  }
  return;
}



uint FUN_00076ec4(void)

{
  undefined4 uVar1;
  
  uVar1 = thunk_FUN_0007490e((0xfebf6b80u));
  FUN_000772a2(((undefined2 *)camry_host_ptr((uint32_t)((0xfebf6b80u)))), 0xffff);
  FUN_000772ae((0xfebf6b80u),0xffff);
  return FUN_00074c54(DAT_febf6c24, 4, ((uchar *)camry_host_ptr((uint32_t)(uVar1))), 6, 0);
}



undefined * FUN_00076f04(ushort param_1,ushort param_2)

{
  uint uVar1;
  undefined *puVar2;
  
  if (param_1 < f33_nvm_descriptor_count) {
    DAT_febf6c44 = param_1;
    uVar1 = f33_nvm_payload_page_count(param_1);
    f33_nvm_payload_chunks_remaining = (ushort)uVar1;
    DAT_febf6c24 = f33_nvm_record_offset(param_1,param_2,0);
    puVar2 = (undefined *)FUN_00076ec4();
  }
  else {
    puVar2 = ((undefined *)camry_host_ptr(0xfffbu));
  }
  return puVar2;
}



/* WARNING: Inlined function: f33_nvm_set_read_destination */
/* WARNING: Inlined function: f33_nvm_payload_length */

void FUN_00076f4e(ushort param_1,ushort param_2,uchar *param_3,uchar param_4)

{
  uint32_t puVar1;
  uint uVar2;
  uint uVar3;
  
  puVar1 = 0x23dfcu;
  uVar3 = (uint)param_1;
  if ((uVar3 < f33_nvm_descriptor_count) && ((uintptr_t)(param_3)!=(uintptr_t)((uchar *)0x0))) {
    f33_nvm_record_context.destination_buffer = camry_host_addr(param_3);
    DAT_febf6c44 = param_1;
    uVar2 = f33_nvm_payload_page_count(param_1);
    f33_nvm_payload_chunks_remaining = (ushort)uVar2;
    DAT_febf6c24 = f33_nvm_record_offset(param_1,param_2,0);
    uVar2 = FUN_0007786a(uVar3,DAT_febf6c24,0);
    if ((uVar2 == 1) &&
       (uVar2 = f33_nvm_read_payload_chunk(param_1,DAT_febf6c24,param_4), uVar2 == 1)) {
      if (f33_nvm_payload_chunks_remaining != 0) {
        return;
      }
      if (0x20 < (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + uVar3 * 6 + 0x383a))))) {
        uVar2 = f33_nvm_read_payload_checksum(param_1,DAT_febf6c24,param_4);
      }
    }
    ((void)(uVar2), FUN_00077640());
  }
  return;
}



/* WARNING: Inlined function: f33_nvm_payload_length */

int FUN_00076ff0(ushort param_1,int param_2,undefined1 param_3)

{
  ushort uVar1;
  uint uVar2;
  uint uVar3;
  int iVar4;
  uchar auStack_5c [64];
  
  uVar1 = f33_nvm_descriptors[param_1].payload_bytes;
  uVar2 = f33_nvm_payload_page_count(param_1);
  uVar2 = (uVar2 - f33_nvm_payload_chunks_remaining) * 0x40;
  uVar3 = f33_nvm_payload_chunk_length(param_1,(ushort)uVar2);
  iVar4 = camry_host_addr(FUN_000776fa(param_2 + (uVar2 & 0xffff) + 4,uVar3,auStack_5c,param_3));
  if (iVar4 == 1) {
    if (uVar1 < 0x21) {
      uVar2 = f33_nvm_sum_bytes((ushort)uVar3,auStack_5c);
      f33_nvm_checksum_accumulator = f33_nvm_checksum_accumulator + uVar2 + 0xc000;
      uVar2 = f33_nvm_header_checksum(((F33NvmRecordContext *)camry_host_ptr((uint32_t)((0xfebf6b80u)))));
      if (uVar2 != (f33_nvm_checksum_accumulator & 0xffff)) {
        iVar4 = 0xfffc;
      }
    }
    else {
      uVar2 = f33_nvm_sum_bytes((ushort)uVar3,auStack_5c);
      f33_nvm_checksum_accumulator = f33_nvm_checksum_accumulator + uVar2;
    }
    f33_nvm_payload_chunks_remaining = f33_nvm_payload_chunks_remaining - 1;
  }
  return iVar4;
}



/* WARNING: Inlined function: f33_nvm_payload_length */

void FUN_0007708c(ushort param_1,ushort param_2,uchar param_3)

{
  uint32_t puVar1;
  uint uVar2;
  uint uVar3;
  
  puVar1 = 0x23dfcu;
  uVar3 = (uint)param_1;
  if (uVar3 < f33_nvm_descriptor_count) {
    DAT_febf6c44 = param_1;
    uVar2 = f33_nvm_payload_page_count(param_1);
    f33_nvm_payload_chunks_remaining = (ushort)uVar2;
    DAT_febf6c24 = f33_nvm_record_offset(param_1,param_2,0);
    uVar2 = FUN_0007786a(uVar3,DAT_febf6c24,param_3);
    if ((uVar2 == 1) && (uVar2 = FUN_00076ff0(uVar3,DAT_febf6c24,param_3), uVar2 == 1)) {
      if (f33_nvm_payload_chunks_remaining != 0) {
        return;
      }
      if (0x20 < (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + uVar3 * 6 + 0x383a))))) {
        uVar2 = f33_nvm_read_payload_checksum(param_1,DAT_febf6c24,param_3);
      }
    }
    ((void)(uVar2), FUN_00077640());
  }
  return;
}



void FUN_0007712a(void)

{
  uint uVar1;
  
  uVar1 = FUN_00076ff0(DAT_febf6c44,DAT_febf6c24,0);
  if (uVar1 == 1) {
    if (f33_nvm_payload_chunks_remaining != 0) {
      return;
    }
    uVar1 = f33_nvm_read_payload_checksum(DAT_febf6c44,DAT_febf6c24,'\0');
  }
  ((void)(uVar1), FUN_00077640());
  return;
}



/* WARNING: Inlined function: f33_nvm_payload_length */

void FUN_00077170(ushort param_1)

{
  ushort uVar1;
  uint uVar2;
  undefined4 uVar3;
  int iVar4;
  uchar *puVar5;
  uint uVar6;
  
  uVar1 = f33_nvm_descriptors[param_1].payload_bytes;
  uVar2 = f33_nvm_record_offset(param_1,DAT_febf6c42,0);
  uVar3 = thunk_FUN_0007490e((0xfebf6b80u));
  FUN_000772a2(((undefined2 *)camry_host_ptr((uint32_t)((0xfebf6b80u)))), (uint)param_1);
  if (uVar1 < 0x21) {
    uVar1 = uVar1 + (uVar1 & 3);
    iVar4 = camry_host_addr(FUN_000776fa(uVar2 + 4,uVar1,((undefined *)camry_host_ptr(0xfebf6b90u)),0));
    if (iVar4 != 1) {
      return;
    }
    puVar5 = (uchar *)thunk_FUN_0007490e((0xfebf6b80u));
    uVar2 = f33_nvm_sum_bytes(2,puVar5);
    uVar6 = f33_nvm_sum_bytes(uVar1,((undefined *)camry_host_ptr(0xfebf6b90u)));
    f33_nvm_checksum_accumulator = f33_nvm_checksum_accumulator + uVar6 + uVar2 + 0xc000;
    FUN_000772ae((0xfebf6b80u),f33_nvm_checksum_accumulator & 0xffff);
  }
  else {
    FUN_000772ae((0xfebf6b80u),0);
    puVar5 = (uchar *)thunk_FUN_0007490e((0xfebf6b80u));
    uVar2 = f33_nvm_sum_bytes(2,puVar5);
    f33_nvm_checksum_accumulator = f33_nvm_checksum_accumulator + uVar2;
  }
  FUN_00074c54(DAT_febf6c24, 4, ((uchar *)camry_host_ptr((uint32_t)(uVar3))), 9, 0);
  return;
}



/* Far-call trampoline: prepare {lp},0 / jarl 0x7490E / dispose 0,{lp},lp; byte-verified against the
   exact image. Forwards with registers and stack unchanged; marked as a thunk. Forwarding shape
   machine-verified; target semantics not recovered. */

undefined4 thunk_FUN_0007490e(undefined4 param_1)

{
  return FUN_0007490e(param_1);
}



undefined2 FUN_0007729c(undefined2 *param_1)

{
  return *param_1;
}



void FUN_000772a2(undefined2 *param_1,undefined2 param_2)

{
  *param_1 = param_2;
  return;
}



/* Load context+2 as unsigned16 and zero-extend to r10. Six-byte getter loads context+2 as
   unsigned16 and zero-extends into r10. The real getter participates in post-read small-record
   checksum acceptance and rejection; high-bit-set checksum is not a signed return. */

uint f33_nvm_header_checksum(F33NvmRecordContext *context)

{
  return (uint)context->checksum16;
}



void FUN_000772ae(int param_1,undefined2 param_2)

{
  (*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 2)))) = param_2;
  return;
}



undefined4 FUN_000772b4(int param_1)

{
  return (*((undefined4 *)camry_host_ptr((uint32_t)(param_1 + 4))));
}



void FUN_000772ba(int param_1,undefined4 param_2)

{
  (*((undefined4 *)camry_host_ptr((uint32_t)(param_1 + 4)))) = param_2;
  return;
}



/* Copy low16(byte_count) bytes into context.destination_buffer +low16(payload_offset), through the
   real74830 byte loop. No local destination bound or checksum validation. Copy low16 byte count
   from explicit fourth-argument source into context+8 destination pointer plus low16 payload
   offset, through real74830. Native composed execution covers offset0 and final-chunk offset192
   with exact copy/canary checks. No local destination bound or checksum admission. */

void f33_nvm_copy_payload_chunk
               (F33NvmRecordContext *context,ushort payload_offset,ushort byte_count,uchar *source)

{
  f33_copy_bytes_forward(((uchar *)camry_host_ptr((uint32_t)(context->destination_buffer + payload_offset))), source, (uint)byte_count);
  return;
}



/* WARNING: This is an inlined function */
/* Store r7 at record-context+8; preserve r6/r7/r10. No destination bound or alignment validation.
   Typed destination pointer and real p-code inlining. Complete77B12 execution checks the entire
   copied payload against registered DataFlash without duplicating it in a golden fixture. */

void f33_nvm_set_read_destination(F33NvmRecordContext *context,uchar *destination)

{
  context->destination_buffer = camry_host_addr(destination);
  return;
}



/* Load full32-bit checksum from context+C; not a pointer read. Six-byte getter loads full32-bit
   checksum at record context+C. Native post-read comparison executes the actual getter with
   C0000000-prefixed values. This field is a checksum, not a second buffer pointer. */

uint f33_nvm_tail_checksum(F33NvmRecordContext *context)

{
  return context->checksum32;
}



void FUN_000772e4(int param_1,undefined4 param_2)

{
  (*((undefined4 *)camry_host_ptr((uint32_t)(param_1 + 0xc)))) = param_2;
  return;
}



undefined4 FUN_000772ea(int param_1)

{
  return FUN_0007490e(param_1 + 0xc);
}



void FUN_000772f8(void)

{
  f33_nvm_checksum_accumulator = 0;
  DAT_febf6c24 = 0xffffffff;
  DAT_febf6c44 = 0xffff;
  return;
}



void FUN_00077370(void)

{
  FUN_0007847c();
  FUN_000772f8();
  return;
}



undefined * FUN_00077380(void)

{
  ushort handle;
  uint32_t puVar1;
  int iVar2;
  uint uVar3;
  int iVar4;
  undefined *puVar5;
  uint uVar6;
  uchar auStack_58 [64];
  
  handle = DAT_febf6c44;
  iVar4 = DAT_febf6c24;
  puVar1 = 0x23dfcu;
  puVar5 = ((undefined *)camry_host_ptr(0xfffbu));
  iVar2 = FUN_000772b4((0xfebf6b80u));
  if (handle < (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + 0x3b2c))))) {
    uVar3 = f33_nvm_payload_page_count(handle);
    uVar3 = (uVar3 - f33_nvm_payload_chunks_remaining) * 0x40;
    uVar6 = uVar3 & 0xffff;
    uVar3 = f33_nvm_payload_chunk_length(handle,(ushort)uVar3);
    puVar5 = (undefined *)
             f33_nvm_read_with_optional_blank_check(iVar4 + uVar6 + 4,(ushort)uVar3,auStack_58,'\0')
    ;
    if (((uintptr_t)(puVar5)==(uintptr_t)(((undefined *)camry_host_ptr((uint32_t)(0x1))))) &&
       (iVar4 = FUN_0007484a(uVar6 + iVar2, camry_host_addr(auStack_58), uVar3), iVar4 != 0)) {
      puVar5 = ((undefined *)camry_host_ptr(0xfffdu));
    }
  }
  return puVar5;
}



/* WARNING: Inlined function: f33_nvm_payload_length */

uint FUN_000773fe(ushort param_1)

{
  ushort uVar1;
  int iVar2;
  uint uVar3;
  uchar *puVar4;
  int iVar5;
  uint uVar6;
  uint uVar7;
  
  iVar2 = DAT_febf6c24;
  uVar1 = f33_nvm_descriptors[param_1].payload_bytes;
  uVar3 = f33_nvm_payload_page_count(param_1);
  uVar3 = (uVar3 - f33_nvm_payload_chunks_remaining) * 0x40;
  uVar7 = uVar3 & 0xffff;
  uVar3 = f33_nvm_payload_chunk_length(param_1,(ushort)uVar3);
  if ((uVar1 & 3) != 0) {
    FUN_00074872(camry_host_addr(((undefined *)camry_host_ptr(0xfebf6b90u))), 0, uVar3);
    puVar4 = (uchar *)FUN_000772b4((0xfebf6b80u));
    f33_copy_bytes_forward(((undefined *)camry_host_ptr(0xfebf6b90u)),puVar4,(uint)uVar1);
    FUN_000772ba((0xfebf6b80u), camry_host_addr(((undefined *)camry_host_ptr(0xfebf6b90u))));
  }
  iVar5 = FUN_000772b4((0xfebf6b80u));
  puVar4 = ((uchar *)camry_host_ptr((uint32_t)(uVar7 + iVar5)));
  uVar6 = f33_nvm_sum_bytes((ushort)uVar3,puVar4);
  f33_nvm_checksum_accumulator = f33_nvm_checksum_accumulator + uVar6;
  return FUN_00074c54(iVar2 + uVar7 + 4,uVar3,puVar4,2,0);
}



/* WARNING: Inlined function: f33_nvm_payload_length */

void FUN_000774ee(int param_1)

{
  uint32_t puVar1;
  puVar1 = 0x23dfcu;
  if ((param_1 == 1) && (param_1 = camry_host_addr(FUN_00077380()), param_1 == 1)) {
    f33_nvm_payload_chunks_remaining = f33_nvm_payload_chunks_remaining - 1;
    if (f33_nvm_payload_chunks_remaining == 0) {
      if (0x20 < (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + (uint)DAT_febf6c44 * 6 + 0x383a))))) {
        param_1 = FUN_0007749e(DAT_febf6c44);
      }
    }
    else {
      param_1 = FUN_000773fe((*((volatile uint16_t *)camry_host_ptr(0xfebf6c44u))));
    }
  }
  if (param_1 != 2) {
    ((void)(param_1), FUN_0007849e());
    FUN_000772f8();
  }
  return;
}



undefined * FUN_00077548(void)

{
  undefined4 uVar1;
  int iVar2;
  undefined *puVar3;
  uchar auStack_c [4];
  
  puVar3 = ((undefined *)camry_host_ptr(0xfffbu));
  if ((DAT_febf6c44 < f33_nvm_descriptor_count) &&
     (puVar3 = (undefined *)f33_nvm_read_with_optional_blank_check(DAT_febf6c24,4,auStack_c,'\0'),(uintptr_t)(puVar3)==(uintptr_t)(((undefined *)camry_host_ptr((uint32_t)(0x1)))))) {
    uVar1 = thunk_FUN_0007490e((0xfebf6b80u));
    iVar2 = FUN_0007484a(uVar1, camry_host_addr(auStack_c), 4);
    if (iVar2 != 0) {
      puVar3 = ((undefined *)camry_host_ptr(0xfffdu));
    }
  }
  return puVar3;
}



void FUN_0007759a(int param_1)

{
  if ((param_1 == 1) && (param_1 = camry_host_addr(FUN_00077548()), param_1 == 1)) {
    param_1 = FUN_000773fe(DAT_febf6c44);
  }
  if (param_1 != 2) {
    FUN_0007849e();
    FUN_000772f8();
  }
  return;
}



/* WARNING: Inlined function: f33_nvm_payload_length */

undefined * FUN_000775ca(void)

{
  undefined4 uVar1;
  int iVar2;
  undefined *puVar3;
  uchar auStack_10 [4];
  
  puVar3 = ((undefined *)camry_host_ptr(0xfffbu));
  if (((uint)DAT_febf6c44 < (uint)f33_nvm_descriptor_count) &&
     (puVar3 = (undefined *)
               f33_nvm_read_with_optional_blank_check
                         (DAT_febf6c24 + f33_nvm_descriptors[DAT_febf6c44].payload_bytes + 4,4,
                          auStack_10,'\0'),(uintptr_t)(puVar3)==(uintptr_t)(((undefined *)camry_host_ptr((uint32_t)(0x1)))))) {
    uVar1 = FUN_000772ea((0xfebf6b80u));
    iVar2 = FUN_0007484a(uVar1, camry_host_addr(auStack_10), 4);
    if (iVar2 != 0) {
      puVar3 = ((undefined *)camry_host_ptr(0xfffdu));
    }
  }
  return puVar3;
}



void FUN_00077626(int param_1)

{
  if (param_1 == 1) {
    param_1 = camry_host_addr(FUN_000775ca());
  }
  ((void)(param_1), FUN_0007849e());
  FUN_000772f8();
  return;
}



void FUN_00077640(void)

{
  FUN_000784c0();
  FUN_000772f8();
  return;
}



uint FUN_00077650(uint param_1,uint param_2)

{
  return f33_nvm_start_reverse_erase(param_1,param_2 & 0xffff,1);
}



/* WARNING: Inlined function: f33_nvm_payload_length */

uint FUN_00077660(uint param_1)

{
  ushort byte_count;
  undefined4 uVar1;
  uchar *puVar2;
  uint uVar3;
  uint uVar4;
  
  byte_count = f33_nvm_descriptors[param_1 & 0xffff].payload_bytes;
  uVar1 = thunk_FUN_0007490e((0xfebf6b80u));
  FUN_000772a2(((undefined2 *)camry_host_ptr((uint32_t)((0xfebf6b80u)))), param_1 & 0xffff);
  if (byte_count < 0x21) {
    puVar2 = (uchar *)thunk_FUN_0007490e((int)0xfebf6b80);
    uVar3 = f33_nvm_sum_bytes(2,puVar2);
    puVar2 = (uchar *)FUN_000772b4((0xfebf6b80u));
    uVar4 = f33_nvm_sum_bytes(byte_count,puVar2);
    f33_nvm_checksum_accumulator = f33_nvm_checksum_accumulator + uVar4 + uVar3 + 0xc000;
    FUN_000772ae((0xfebf6b80u),f33_nvm_checksum_accumulator & 0xffff);
  }
  else {
    FUN_000772ae((int)0xfebf6b80, 0x0);
    puVar2 = (uchar *)thunk_FUN_0007490e((int)0xfebf6b80);
    uVar3 = f33_nvm_sum_bytes(2,puVar2);
    f33_nvm_checksum_accumulator = f33_nvm_checksum_accumulator + uVar3;
  }
  return FUN_00074c54(DAT_febf6c24, 4, ((uchar *)camry_host_ptr((uint32_t)(uVar1))), 3, 0);
}



undefined * FUN_000776fa(uint param_1,ushort param_2,uchar *param_3,uchar param_4)

{
  undefined *puVar1;
  uint uVar2;
  
  uVar2 = f33_nvm_read_with_optional_blank_check(param_1,param_2,param_3,param_4);
  puVar1 = ((undefined *)camry_host_ptr((uint32_t)(0x1)));
  if ((uVar2 != 1) && (puVar1 = ((undefined *)camry_host_ptr(0xfffbu)), uVar2 == 3)) {
    puVar1 = ((undefined *)camry_host_ptr((uint32_t)(0xfffc)));
  }
  return puVar1;
}



/* WARNING: Inlined function: f33_nvm_payload_length */
/* Read the next payload chunk through776FA. On success add its unsigned byte sum. For lengths<=32
   addC000 and compare low16 against context.checksum16 before copying; mismatch returnsFFFC without
   destination write or remaining-count decrement. Larger payloads copy before the later777CA
   checksum check. Native proof includes post-read7775E boundaries and a complete captured16-byte
   read through77B12 with explicit ICU-S/ECC/blank-check inputs. Full multi-chunk acquisition and
   application restoration remain separate. Raw full-body dataflow plus post-read7775E boundaries
   and complete captured16-byte read through77B12 with explicit hardware inputs. Small payload
   addsC000 and checks low16 before copying; mismatchFFFC preserves destination and remaining count.
   Large payload copies before777CA trailer validation. Full multi-chunk acquisition and application
   restoration remain outside this proof. */

uint f33_nvm_read_payload_chunk(ushort handle,uint record_offset,uchar read_option)

{
  ushort uVar1;
  ushort payload_offset;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  uchar auStack_64 [64];
  
  uVar1 = f33_nvm_descriptors[handle].payload_bytes;
  uVar2 = (uint)uVar1;
  uVar3 = f33_nvm_payload_page_count(handle);
  uVar3 = (uVar3 - f33_nvm_payload_chunks_remaining) * 0x40;
  payload_offset = (ushort)uVar3;
  uVar4 = f33_nvm_payload_chunk_length(handle,payload_offset);
  uVar3 = camry_host_addr(FUN_000776fa(record_offset + (uVar3 & 0xffff) + 4,uVar4,auStack_64,read_option));
  if (uVar3 == 1) {
    if (uVar2 < 0x21) {
      uVar5 = f33_nvm_sum_bytes((ushort)uVar4,auStack_64);
      uVar5 = f33_nvm_checksum_accumulator + uVar5 + 0xc000;
      f33_nvm_checksum_accumulator = uVar5;
      uVar6 = f33_nvm_header_checksum(((F33NvmRecordContext *)camry_host_ptr((uint32_t)((0xfebf6b80u)))));
      if (uVar6 != (uVar5 & 0xffff)) {
        return 0xfffc;
      }
    }
    else {
      uVar5 = f33_nvm_sum_bytes((ushort)uVar4,auStack_64);
      f33_nvm_checksum_accumulator = f33_nvm_checksum_accumulator + uVar5;
    }
    if ((uVar1 & 3) == 0) {
      uVar2 = uVar4;
    }
    f33_nvm_copy_payload_chunk(((F33NvmRecordContext *)camry_host_ptr((uint32_t)((0xfebf6b80u)))), payload_offset, (ushort)uVar2, auStack_64);
    f33_nvm_payload_chunks_remaining = f33_nvm_payload_chunks_remaining - 1;
  }
  return uVar3;
}



/* WARNING: Inlined function: f33_nvm_payload_length */
/* Read four bytes at record_offset+payload_length+4 into context.checksum32. Success addsC0000000
   to the accumulator and compares the full word; mismatch returnsFFFC. No rollback of earlier
   destination copies. Native proof starts at post-read777FC; not an end-to-end hardware read or
   application restoration proof. Raw dataflow reads a full word at record_offset+payload_length+4
   into context+C. Native post-read777FC boundary addsC0000000 and compares full32 bits;
   mismatchFFFC does not undo earlier payload copies. Hardware acquisition, logical copy consensus
   and application restoration remain outside this proof. */

uint f33_nvm_read_payload_checksum(ushort handle,uint record_offset,uchar read_option)

{
  uint32_t puVar1;
  undefined4 uVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  
  puVar1 = 0x23dfcu;
  uVar2 = FUN_000772ea((0xfebf6b80u));
  uVar3 = camry_host_addr(FUN_000776fa(camry_host_addr(((undefined *)camry_host_ptr((uint32_t)((*((ushort *)camry_host_ptr((uint32_t)(puVar1 + (uint)handle * 6 + 0x383a)))) + record_offset + 4)))),  4, ((uchar *)camry_host_ptr((uint32_t)(uVar2))),  
                       read_option));
  if (uVar3 == 1) {
    uVar5 = f33_nvm_checksum_accumulator + 0xc0000000;
    f33_nvm_checksum_accumulator = uVar5;
    uVar4 = f33_nvm_tail_checksum(((F33NvmRecordContext *)camry_host_ptr((uint32_t)((0xfebf6b80u)))));
    if (uVar4 != uVar5) {
      uVar3 = 0xfffc;
    }
  }
  return uVar3;
}



void FUN_00077824(void)

{
  uint uVar1;
  
  uVar1 = f33_nvm_read_payload_chunk(DAT_febf6c44,DAT_febf6c24,'\0');
  if (uVar1 == 1) {
    if (f33_nvm_payload_chunks_remaining != 0) {
      return;
    }
    uVar1 = f33_nvm_read_payload_checksum(DAT_febf6c44,DAT_febf6c24,'\0');
  }
  ((void)(uVar1), FUN_00077640());
  return;
}



int FUN_0007786a(uint param_1,undefined4 param_2,undefined1 param_3)

{
  uchar *source;
  int iVar1;
  uint uVar2;
  uint uVar3;
  
  source = (uchar *)thunk_FUN_0007490e((0xfebf6b80u));
  iVar1 = camry_host_addr(FUN_000776fa(param_2,4,source,param_3));
  if (iVar1 == 1) {
    uVar2 = FUN_0007729c(((undefined2 *)camry_host_ptr((uint32_t)((0xfebf6b80u)))));
    uVar3 = f33_nvm_sum_bytes(2,source);
    f33_nvm_checksum_accumulator = f33_nvm_checksum_accumulator + uVar3;
    if (uVar2 != (param_1 & 0xffff)) {
      iVar1 = 0xfffc;
      FUN_00076988();
    }
  }
  return iVar1;
}



/* WARNING: This is an inlined function */
/* Store r7 at context+0; preserve r6/r7/r10. Inline the real six-byte body so77B12 retains the
   record pointer for772D8. Store record pointer r7 at commit-context+0; Inline the real six-byte
   body to retain77B12's forwarding of r7 into772D8. Composed native execution validates the bound
   destination and complete payload. */

void f33_nvm_bind_record_context(F33NvmCommitContext *context,F33NvmRecordContext *record)

{
  context->record = camry_host_addr(record);
  return;
}



undefined4 FUN_000778cc(int param_1)

{
  return (*((undefined4 *)camry_host_ptr((uint32_t)(param_1 + 4))));
}



void FUN_000778d2(int param_1,undefined4 param_2)

{
  (*((undefined4 *)camry_host_ptr((uint32_t)(param_1 + 4)))) = param_2;
  return;
}



undefined4 FUN_000778d8(int param_1)

{
  return FUN_0007490e(param_1 + 4);
}



/* Far-call trampoline: prepare {lp},0 / jarl 0x772F8 / dispose 0,{lp},lp; byte-verified against the
   exact image. Forwards with registers and stack unchanged; marked as a thunk. Forwarding shape
   machine-verified; target semantics not recovered. */

void thunk_FUN_000772f8(void)

{
  FUN_000772f8();
  return;
}



undefined * FUN_00077910(void)

{
  int iVar1;
  undefined *puVar2;
  uint uVar3;
  uchar *destination;
  int local_c;
  
  iVar1 = DAT_febf6c24;
  puVar2 = ((undefined *)camry_host_ptr(0xfffbu));
  if (DAT_febf6c44 < f33_nvm_descriptor_count) {
    uVar3 = f33_nvm_trailer_offset(DAT_febf6c44);
    destination = (uchar *)FUN_0007490e(camry_host_addr(&local_c));
    puVar2 = (undefined *)f33_nvm_read_with_optional_blank_check(iVar1 + uVar3,4,destination,'\x01')
    ;
    if ((uintptr_t)(puVar2)==(uintptr_t)(((undefined *)camry_host_ptr((uint32_t)(0x1))))) {
      if (local_c == -0x55555556) {
        return ((undefined *)camry_host_ptr((uint32_t)(0x1)));
      }
    }
    else if ((uintptr_t)(puVar2)!=(uintptr_t)(((undefined *)camry_host_ptr((uint32_t)(0x3))))) {
      return puVar2;
    }
    puVar2 = ((undefined *)camry_host_ptr(0xfffdu));
  }
  return puVar2;
}



void FUN_00077968(int param_1)

{
  if (param_1 == 1) {
    param_1 = camry_host_addr(FUN_00077910());
  }
  ((void)(param_1), FUN_0007849e());
  thunk_FUN_000772f8();
  return;
}



/* WARNING: Inlined function: f33_nvm_bind_record_context */
/* WARNING: Inlined function: f33_nvm_base_offset */

void FUN_000779b2(ushort param_1,int param_2)

{
  uint32_t puVar1;
  uint uVar2;
  uchar *source;
  uint uVar3;
  undefined4 local_14 [2];
  
  puVar1 = 0x23dfcu;
  uVar3 = (uint)param_1;
  local_14[0] = 0xaaaaaaaa;
  if ((uVar3 < f33_nvm_descriptor_count) && (param_2 != 0)) {
    f33_nvm_commit_context.record = (0xfebf6b80u);
    DAT_febf6c44 = param_1;
    FUN_000772ba((0xfebf6b80u),param_2);
    uVar2 = f33_nvm_payload_page_count(param_1);
    f33_nvm_payload_chunks_remaining = (ushort)uVar2;
    DAT_febf6c24 = (uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar1 + uVar3 * 6 + 0x3838)))) << 6;
    source = (uchar *)FUN_0007490a(camry_host_addr(local_14));
    uVar2 = f33_nvm_sum_bytes(4,source);
    f33_nvm_checksum_accumulator = f33_nvm_checksum_accumulator + uVar2;
    FUN_00077660(uVar3);
  }
  return;
}



/* WARNING: Inlined function: f33_nvm_bind_record_context */
/* WARNING: Inlined function: f33_nvm_base_offset */

undefined * FUN_00077a36(ushort param_1)

{
  ushort uVar1;
  uint32_t puVar2;
  undefined4 uVar3;
  uint uVar4;
  undefined *puVar5;
  
  puVar2 = 0x23dfcu;
  puVar5 = ((undefined *)camry_host_ptr(0xfffbu));
  uVar3 = FUN_000778d8((0xfebf6b78u));
  if ((uint)param_1 < (uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0x3b2c))))) {
    f33_nvm_commit_context.record = (0xfebf6b80u);
    DAT_febf6c44 = param_1;
    FUN_000778d2((0xfebf6b78u),(int)0xaaaaaaaa);
    uVar1 = (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + (uint)param_1 * 6 + 0x3838))));
    DAT_febf6c24 = (uint)uVar1 * 0x40;
    uVar4 = f33_nvm_trailer_offset(param_1);
    puVar5 = (undefined *)FUN_00074c54(uVar4 + (uint)uVar1 * 0x40, 4, ((uchar *)camry_host_ptr((uint32_t)(uVar3))), 10, 1);
  }
  return puVar5;
}



uint FUN_00077aa8(ushort param_1,int param_2,uchar param_3)

{
  uchar *destination;
  uint uVar1;
  int iVar2;
  
  destination = (uchar *)FUN_000778d8((0xfebf6b78u));
  uVar1 = f33_nvm_trailer_offset(param_1);
  uVar1 = f33_nvm_read_with_optional_blank_check(uVar1 + param_2,4,destination,param_3);
  if (uVar1 == 1) {
    iVar2 = FUN_000778cc((0xfebf6b78u));
    if (iVar2 == -0x55555556) {
      uVar1 = f33_nvm_sum_bytes(4,destination);
      f33_nvm_checksum_accumulator = f33_nvm_checksum_accumulator + uVar1;
      return 1;
    }
  }
  else if (uVar1 != 3) {
    return uVar1;
  }
  return 0xfffc;
}



/* WARNING: Inlined function: f33_nvm_bind_record_context */
/* WARNING: Inlined function: f33_nvm_set_read_destination */
/* WARNING: Inlined function: f33_nvm_base_offset */
/* WARNING: Inlined function: f33_nvm_payload_length */
/* Reject low16(handle)>=123 or NULL destination before setup. Bind the contexts, set remaining
   chunks/base, then read marker with option1 regardless of caller option. Admit header and first
   payload chunk; return pending if chunks remain. Otherwise check the large checksum when length>32
   and publish status through77640. Entry does not reset the checksum accumulator. Complete
   captured16-byte record execution covers explicit blank/nonblank hardware results, destination
   canaries and completion cleanup; full multi-chunk and application request/notification closure
   remain separate. Begin physical record read for low16 handle<123 and nonNULL destination. Bind
   contexts; marker always uses read option1; header/payload use caller option. Return pending if
   chunks remain; otherwise publish status and clear active handle/base/accumulator. Complete
   captured16-byte paths cover blank rejection and nonblank copy with both completion banks.
   Explicit hardware outcomes; not complete multi-chunk or application notification/consensus proof.
    */

void f33_nvm_begin_record_read(ushort handle,uchar *destination,uchar read_option)

{
  uint32_t puVar1;
  uint uVar2;
  uint uVar3;
  
  puVar1 = 0x23dfcu;
  uVar3 = (uint)handle;
  if ((uVar3 < f33_nvm_descriptor_count) && ((uintptr_t)(destination)!=(uintptr_t)((uchar *)0x0))) {
    f33_nvm_commit_context.record = (0xfebf6b80u);
    f33_nvm_record_context.destination_buffer = camry_host_addr(destination);
    DAT_febf6c44 = handle;
    uVar2 = f33_nvm_payload_page_count(handle);
    f33_nvm_payload_chunks_remaining = (ushort)uVar2;
    DAT_febf6c24 = (uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar1 + uVar3 * 6 + 0x3838)))) << 6;
    uVar2 = FUN_00077aa8(uVar3,DAT_febf6c24,1);
    if ((uVar2 == 1) &&
       ((uVar2 = FUN_0007786a(uVar3,DAT_febf6c24,read_option), uVar2 == 1 &&
        (uVar2 = f33_nvm_read_payload_chunk(handle,DAT_febf6c24,read_option), uVar2 == 1)))) {
      if (f33_nvm_payload_chunks_remaining != 0) {
        return;
      }
      if (0x20 < (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + uVar3 * 6 + 0x383a))))) {
        uVar2 = f33_nvm_read_payload_checksum(handle,DAT_febf6c24,read_option);
      }
    }
    ((void)(uVar2), FUN_00077640());
  }
  return;
}



/* Far-call trampoline: prepare {lp},0 / jarl 0x77824 / dispose 0,{lp},lp; byte-verified against the
   exact image. Forwards with registers and stack unchanged; marked as a thunk. Forwarding shape
   machine-verified; target semantics not recovered. */

void thunk_FUN_00077824(void)

{
  FUN_00077824();
  return;
}



/* Paired constant publisher: DAT_febf6c4a = 0; and DAT_febf6c38 = 0xffff;; shape-classified from
   the canonical corpus. Target cells not yet named. */

void FUN_00077bd8(void)

{
  DAT_febf6c4a = 0;
  DAT_febf6c38 = 0xffff;
  return;
}



/* Zero6C4C,6C10,6C4B; set6C3C=FFFF; store identity(0) into6C14/6C18. Preserve published result6C1C,
   selector6C4A and unrelated fields. Native whole-context canaries verify cleanup after both
   dispatched and rejected results. Zero6C4C/6C10/6C4B and identity-zero6C14/6C18; set6C3CFFFF.
   Preserve published6C1C and selector6C4A. Whole-context native canaries cover dispatched and
   rejected completion cleanup. */

void f33_nvm_reset_completion_context(void)

{
  f33_nvm_completion_side_status = '\0';
  f33_nvm_completion_raw_result = 0;
  f33_nvm_completion_storage_handle = 0xffff;
  f33_nvm_completion_mode = '\0';
  DAT_febf6c14 = FUN_0007490a(0);
  DAT_febf6c18 = FUN_0007490e(0);
  return;
}



void FUN_00077c32(void)

{
  FUN_00077bd8();
  f33_nvm_reset_completion_context();
  return;
}



void FUN_00077c42(void)

{
  if (2 < DAT_febf6c4a) {
    FUN_00077bd8();
  }
  return;
}



void FUN_00077c5a(undefined1 param_1)

{
  DAT_febf6c4a = param_1;
  return;
}



undefined1 FUN_00077c64(void)

{
  return DAT_febf6c4a;
}



void FUN_00077c6e(undefined2 param_1)

{
  DAT_febf6c3a = param_1;
  return;
}



undefined2 FUN_00077c78(void)

{
  return DAT_febf6c3a;
}



undefined * FUN_00077c82(ushort param_1)

{
  if (param_1 < f33_nvm_descriptor_count) {
    DAT_febf6c38 = param_1;
    return ((undefined *)camry_host_ptr((uint32_t)(0x1)));
  }
  return ((undefined *)camry_host_ptr(0xfffbu));
}



undefined2 FUN_00077c9e(void)

{
  return DAT_febf6c38;
}



undefined * FUN_00077ca8(int param_1)

{
  if (param_1 != 0) {
    DAT_febf6c14 = param_1;
    return ((undefined *)camry_host_ptr((uint32_t)(0x1)));
  }
  return ((undefined *)camry_host_ptr(0xfffbu));
}



undefined4 FUN_00077cbe(void)

{
  return DAT_febf6c14;
}



undefined * FUN_00077cc8(int param_1)

{
  if (param_1 != 0) {
    DAT_febf6c18 = param_1;
    return ((undefined *)camry_host_ptr((uint32_t)(0x1)));
  }
  return ((undefined *)camry_host_ptr(0xfffbu));
}



undefined4 FUN_00077cde(void)

{
  return DAT_febf6c18;
}



void FUN_00077ce8(void)

{
  f33_nvm_completion_mode = DAT_febf6c4a;
  f33_nvm_completion_storage_handle = DAT_febf6c38;
  FUN_00077bd8();
  return;
}



void FUN_00077d14(uint param_1)

{
  f33_nvm_completion_raw_result = param_1;
  return;
}



void FUN_00077d1e(uchar param_1)

{
  if (param_1 != '\0') {
    f33_nvm_completion_side_status = param_1;
  }
  return;
}



/* Full32 completion result6C10!=1 sets6B73.bit0 through7697E; no other gate. Full32 current
   result6C10!=1 sets6B73.bit0. No mode/handle gate; exact result1 preserves the flags byte. */

void f33_nvm_mark_non_success_result(void)

{
  if (f33_nvm_completion_raw_result != 1) {
    f33_nvm_mark_physical_attempt_error();
  }
  return;
}



/* Side byte6C4C==1 calls76A1C(1);==2 calls76A1C(0); others do nothing. 77D66 calls this before
   validating completion mode/handle. Side byte6C4C1 calls76A1C(1);2 calls76A1C(0); otherwise no
   call. Native side diagnostics occur even when the later mode/handle dispatch gate rejects. */

void f33_nvm_report_completion_side_status(void)

{
  uint status;
  
  status = 0;
  if ((f33_nvm_completion_side_status == '\x02') ||
     (status = 1, f33_nvm_completion_side_status == '\x01')) {
    f33_nvm_accumulate_side_status(status);
  }
  return;
}



/* Mark non1 result, scan8 full32 rows at27C38, default classFD; report side status before dispatch
   gates. Modes1/2 and storage handle<123 call76722. Mode1 loads6C14 into r7; mode2 loads6C18; no
   pointee is read by the consumer. Always zero6C20 and reset completion context, even on invalid
   mode/handle. Native both columns, unknown fullword, last/invalid handle, side effects and
   preserved gaps. Eight full32 result rows at27C38; mode1 uses+4 else+5; unmatched classFD. Report
   side status before allowing only modes1/2 and handle<123 into76722. Always zero6C20/reset
   completion context. Both columns and all rows executed; no payload dereference or logical
   publication. */

void f33_nvm_finish_physical_result(void)

{
  int iVar1;
  uint *puVar2;
  int iVar3;
  int iVar4;
  uint32_t puVar5;
  uchar result_class;
  
  puVar5 = 0x23dfcu;
  f33_nvm_mark_non_success_result();
  result_class = 0xfd;
  iVar4 = 0;
  do {
    puVar2 = ((uint *)camry_host_ptr((uint32_t)(puVar5 + iVar4 * 8 + 0x3e3c)));
    if (*puVar2 == f33_nvm_completion_raw_result) {
      if (f33_nvm_completion_mode == '\x01') {
        result_class = (uchar)puVar2[1];
      }
      else {
        result_class = (*((uchar *)camry_host_ptr((uint32_t)((int)camry_host_addr(puVar2) + 5))));
      }
      break;
    }
    iVar3 = iVar4 + 1;
    iVar1 = iVar4 + -7;
    iVar4 = iVar3;
  } while (((iVar1 < 0) || (iVar3 < 0)));
  f33_nvm_report_completion_side_status();
  if (((f33_nvm_completion_mode == '\x01') || (f33_nvm_completion_mode == '\x02')) &&
     (f33_nvm_completion_storage_handle < (*((ushort *)camry_host_ptr((uint32_t)(puVar5 + 0x3b2c)))))) {
    f33_nvm_publish_physical_class(result_class);
  }
  FUN_000783de(0);
  f33_nvm_reset_completion_context();
  return;
}



/* Single constant publisher: DAT_febf6c2c = 0xffffffff; Shape-classified from the canonical corpus;
   the target cell is not yet named, so the written state's meaning is unknown. */

void FUN_00077df2(void)

{
  DAT_febf6c2c = 0xffffffff;
  return;
}



/* Far-call trampoline: prepare {lp},0 / jarl 0x77DF2 / dispose 0,{lp},lp; byte-verified against the
   exact image. Forwards with registers and stack unchanged; marked as a thunk. Forwarding shape
   machine-verified; target semantics not recovered. */

void thunk_FUN_00077df2(void)

{
  FUN_00077df2();
  return;
}



/* WARNING: Inlined function: f33_nvm_allocation_pages */

int FUN_00077e0a(uint param_1,uint param_2)

{
  uint uVar1;
  int iVar2;
  
  uVar1 = (uint)f33_nvm_descriptors[param_1 & 0xffff].payload_bytes;
  if (0x20 < uVar1) {
    uVar1 = uVar1 + 4;
  }
  if (f33_nvm_descriptors[param_1 & 0xffff].option == '\0') {
    iVar2 = uVar1 + 4;
  }
  else {
    iVar2 = uVar1 + 0xc;
  }
  return (iVar2 + 0x40U & 0xffffffc0) + (param_2 & 0xff) * -4;
}



void FUN_00077e22(char *param_1,undefined1 *param_2,undefined1 *param_3)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  *param_2 = 0xd;
  *param_3 = 0xff;
  iVar2 = 0;
  while (((iVar3 = (short)iVar2 * 5, (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x27c84u + (uint32_t)(iVar3) * 1u)))) != *param_1 ||
          ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x27c85u + (uint32_t)(iVar3) * 1u)))) != param_1[1])) || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x27c86u + (uint32_t)(iVar3) * 1u)))) != param_1[2]))) {
    iVar1 = iVar2 + 1;
    iVar3 = iVar2 + -0xb;
    iVar2 = iVar1;
    if (iVar3 < 0 == (iVar1 < 0 && -1 < iVar3)) {
      return;
    }
  }
  *param_2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x27c87u + (uint32_t)(iVar3) * 1u))));
  *param_3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x27c88u + (uint32_t)(iVar3) * 1u))));
  return;
}



uint FUN_00077e6e(uint param_1,undefined1 *param_2)

{
  undefined1 uVar1;
  uint uVar2;
  uchar auStack_10 [4];
  
  *param_2 = 0;
  uVar2 = f33_nvm_read_with_optional_blank_check(param_1 + 4,4,auStack_10,'\x01');
  if (uVar2 == 1) {
    uVar1 = 0xff;
  }
  else {
    if (uVar2 != 3) {
      return uVar2;
    }
    uVar2 = f33_nvm_read_with_optional_blank_check(param_1,4,auStack_10,'\x01');
    if (uVar2 != 1) {
      *param_2 = 0;
      if (uVar2 != 3) {
        return uVar2;
      }
      return 1;
    }
    uVar1 = 0xaa;
  }
  *param_2 = uVar1;
  return 1;
}



code * FUN_00077eba(ushort param_1,undefined1 *param_2,undefined1 *param_3)

{
  uint uVar1;
  code *pcVar2;
  uint uVar3;
  undefined1 auStack_1b [3];
  
  pcVar2 = (code *)((undefined *)camry_host_ptr(0xfffbu));
  if (((param_1 < f33_nvm_descriptor_count) && ((uintptr_t)(param_2)!=(uintptr_t)((undefined1 *)0x0))) &&
     ((uintptr_t)(param_3)!=(uintptr_t)((undefined1 *)0x0))) {
    *param_2 = 0xd;
    *param_3 = 0xff;
    uVar3 = 0;
    do {
      uVar1 = FUN_00077e0a(param_1,2);
      uVar1 = f33_nvm_record_offset(param_1,(ushort)uVar3,uVar1);
      pcVar2 = (code *)FUN_00077e6e(uVar1,auStack_1b + uVar3);
      if ((uintptr_t)(pcVar2)!=(uintptr_t)(((code *)camry_host_ptr((uint32_t)(0x1))))) {
        return pcVar2;
      }
      uVar3 = uVar3 + 1 & 0xffff;
    } while (uVar3 < 3);
    FUN_00077e22(auStack_1b,param_2,param_3);
    pcVar2 = ((code *)camry_host_ptr((uint32_t)(0x1)));
  }
  return pcVar2;
}



undefined * FUN_00077f26(ushort param_1,ushort param_2,undefined1 *param_3)

{
  undefined *puVar1;
  uint uVar2;
  uchar auStack_14 [4];
  
  puVar1 = ((undefined *)camry_host_ptr(0xfffbu));
  if (param_1 < f33_nvm_descriptor_count) {
    *param_3 = 0;
    uVar2 = FUN_00077e0a(param_1,3);
    uVar2 = f33_nvm_record_offset(param_1,param_2,uVar2);
    puVar1 = (undefined *)f33_nvm_read_with_optional_blank_check(uVar2,4,auStack_14,'\x01');
    if ((uintptr_t)(puVar1)==(uintptr_t)(((undefined *)camry_host_ptr((uint32_t)(0x1))))) {
      *param_3 = 0x55;
    }
    else if ((uintptr_t)(puVar1)==(uintptr_t)(((undefined *)camry_host_ptr((uint32_t)(0x3))))) {
      *param_3 = 0;
      puVar1 = ((undefined *)camry_host_ptr((uint32_t)(0x1)));
    }
  }
  return puVar1;
}



void FUN_00077f7e(ushort param_1,undefined1 *param_2,char *param_3)

{
  char *pcVar1;
  undefined8 uVar2;
  uint uVar3;
  int iVar4;
  uint uVar5;
  char acStack_17 [3];
  
  uVar2 = 0x23dfc00000000;
  if (param_1 < f33_nvm_descriptor_count) {
    *param_2 = 0xe;
    *param_3 = -1;
    uVar5 = 0;
    do {
      uVar3 = FUN_00077e0a(param_1,2);
      uVar3 = f33_nvm_record_offset(param_1,(ushort)uVar5,uVar3);
      iVar4 = FUN_00077e6e(uVar3,acStack_17 + uVar5);
      if (iVar4 != 1) {
        return;
      }
      uVar5 = uVar5 + 1 & 0xffff;
    } while (uVar5 < 3);
    uVar5 = 9;
    do {
      pcVar1 = ((char *)camry_host_ptr((uint32_t)((short)uVar5 * 5 + (int)((ulonglong)uVar2 >> 0x20) + 0x3e88)));
      if (((*pcVar1 == acStack_17[0]) && (pcVar1[1] == acStack_17[1])) &&
         (pcVar1[2] == acStack_17[2])) {
        *param_2 = 0xc;
        *param_3 = pcVar1[4];
        return;
      }
      uVar5 = uVar5 + 1;
    } while (uVar5 < 0xc);
  }
  return;
}


