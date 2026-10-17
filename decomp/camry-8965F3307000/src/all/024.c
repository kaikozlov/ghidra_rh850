#include "common.h"


/* Protected lower-route forwarding preserves R7 descriptor; application snapshot admission remains
   distinct from MAC/lower transmission completion. */

uint f33_secoc_lower_tx(ushort pdu,F33PduInfo *info)

{
  uint uVar1;
  
  uVar1 = f33_route_secured_lower_tx(pdu,info);
  if (uVar1 == 2) {
    uVar1 = 0x20;
  }
  return uVar1;
}



void FUN_000901e8(undefined2 param_1)

{
  FUN_0008160c(param_1);
  return;
}



void FUN_000901f6(undefined2 param_1)

{
  FUN_00081640(param_1);
  return;
}



void FUN_00090204(undefined2 param_1)

{
  FUN_00081ca6(param_1);
  return;
}



void FUN_00090212(void)

{
  DAT_febe55b8 = 0;
  DAT_febe55ba = 0;
  DAT_febe55bc = 0;
  FUN_00090502();
  return;
}



undefined4 FUN_0009022a(short param_1,undefined2 *param_2)

{
  undefined4 uVar1;
  
  uVar1 = 0;
  if ((DAT_0002583e == 0) && (param_1 == DAT_0002583c)) {
    *param_2 = 0;
    uVar1 = 1;
    param_2[1] = 0;
  }
  return uVar1;
}



undefined4
FUN_000903f6(undefined2 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4,
            undefined4 param_5)

{
  int iVar1;
  undefined4 uVar2;
  undefined1 auStack_1c [4];
  undefined4 uStack_18;
  undefined4 uStack_14;
  undefined4 uStack_10;
  undefined4 uStack_c;
  
  uVar2 = 1;
  uStack_14 = param_5;
  uStack_18 = param_4;
  uStack_10 = param_2;
  uStack_c = param_3;
  iVar1 = FUN_000902b0(param_1,auStack_1c);
  if (iVar1 == 1) {
    uVar2 = FUN_000908ba(auStack_1c,&uStack_10,&uStack_18);
  }
  return uVar2;
}



uint FUN_000904c0(void)

{
  uint32_t puVar1;
  uint uVar2;
  
  puVar1 = 0xfebeb800u;
  if (DAT_febe55b8 != 0) {
    DAT_febe55b8 = 0;
  }
  uVar2 = FUN_000904a6();
  if (uVar2 != 0) {
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x6246)))) = 1;
    (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x6244)))) = (short)uVar2;
  }
  if ((*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x6246)))) != 0) {
    uVar2 = (uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x6244))));
    (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x6246)))) = (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x6246)))) + -1;
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x6248)))) = (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x6248)))) + 1;
  return uVar2;
}



void FUN_00090502(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  f33_memzero(((undefined *)camry_host_ptr(0xfebe55c0u)),8);
  f33_memzero(((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x6238))), 8);
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x6228)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6226))))) = 0;
  (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x6230)))) = ~(*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x6240))));
  (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x622c)))) = ~(*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x623c))));
  f33_memzero(((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x61f4))), 0xc);
  f33_memzero(((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x61e8))), 0xc);
  f33_memzero(((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x6224))), 0x18);
  f33_memzero(((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x620c))), 0x18);
  return;
}



void FUN_000906a4(undefined4 *param_1,undefined1 *param_2,uint *param_3)

{
  uint uVar1;
  
  if ((byte)*param_3 < (*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb))))) {
    uVar1 = 0;
  }
  else {
    *param_2 = (char)((uint)*param_1 >> 8);
    param_2[1] = (char)*param_1;
    param_2[2] = (char)((uint)param_1[1] >> 0xc);
    param_2[3] = (char)((uint)param_1[1] >> 4);
    param_2[4] = (char)(param_1[1] << 4);
    uVar1 = (uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb))));
  }
  *param_3 = uVar1;
  return;
}



void FUN_00090ee6(void)

{
  FUN_000913b6();
  FUN_000912b2();
  return;
}



/* Configured second policy hook uses fourth argument R9 only; map nonzero8B0FC result to8,
   otherwise0. Return8 selects silent-drop disposition, not a fabricated NRC. */

uint f33_dcm_application_policy_hook
               (uchar service_id,uchar *request,ushort request_length,uchar addressing_flags,
               ushort service_list_selector,uchar *negative_response)

{
  uint uVar1;
  
  uVar1 = f33_check_diagnostic_addressing_admission(addressing_flags);
  if (uVar1 == 0) {
    uVar1 = 0;
  }
  else {
    uVar1 = 8;
  }
  return uVar1;
}



/* Null list allows; nonnull list requires current595C session in count bytes. Nonnull zero-count
   rejects. Return0 allowed,1 rejected. */

uint f33_dcm_check_session_list(uchar *allowed,uchar count)

{
  uint uVar1;
  uint uVar2;
  uchar uStack_11;
  
  uVar2 = 1;
  uStack_11 = '\x01';
  if (allowed == (uchar *)0x0) {
LAB_00090f50:
    uVar2 = 0;
  }
  else {
    f33_dcm_get_session(&uStack_11);
    for (uVar1 = 0; uVar1 < count; uVar1 = uVar1 + 1 & 0xff) {
      if (uStack_11 == allowed[uVar1]) goto LAB_00090f50;
    }
  }
  return uVar2;
}



/* Null list allows; otherwise match current security getter result against count bytes. Nonnull
   zero-count rejects. Separate from application/group admission. */

uint f33_dcm_check_security_list(uchar *allowed,uchar count)

{
  uint uVar1;
  uint uVar2;
  uchar uStack_11;
  
  uStack_11 = '\0';
  uVar2 = 1;
  if (allowed == (uchar *)0x0) {
LAB_00090f90:
    uVar2 = 0;
  }
  else {
    f33_dcm_get_security_level(&uStack_11);
    for (uVar1 = 0; uVar1 < count; uVar1 = uVar1 + 1 & 0xff) {
      if (uStack_11 == allowed[uVar1]) goto LAB_00090f90;
    }
  }
  return uVar2;
}



void FUN_000912b2(void)

{
  f33_dcm_final_nrc = '\0';
  return;
}



void FUN_000912b8(void)

{
  f33_dcm_final_nrc = '\0';
  return;
}



void FUN_000913b6(void)

{
  f33_dcm_clear_active_service();
  return;
}



void FUN_000913ea(undefined1 param_1)

{
  DAT_febe562c = param_1;
  return;
}



/* Return the retained28-byte message context5630; not an opaque scalar. */

F33DcmMessageContext * f33_dcm_get_message_context(void)

{
  return ((undefined *)camry_host_ptr(0xfebe5630u));
}



undefined1 FUN_0009168e(void)

{
  return DAT_febe562c;
}



undefined1 FUN_00091694(undefined1 *param_1)

{
  return *param_1;
}



undefined1 FUN_000916a6(void)

{
  return DAT_febe562d;
}



bool FUN_000916c6(char param_1,undefined4 *param_2)

{
  bool bVar1;
  
  bVar1 = false;
  if (((param_1 == '\x01') && (*(short *)(param_2 + 1) == 2)) && (*(char *)*param_2 == '>')) {
    bVar1 = ((char *)*param_2)[1] == -0x80;
  }
  return bVar1;
}



undefined4 FUN_000916ec(char param_1,ushort param_2,char param_3)

{
  short *psVar1;
  uint uVar2;
  uint32_t puVar3;
  uint uVar4;
  
  puVar3 = 0x23dfcu;
  uVar4 = f33_dcm_select_service_list(param_2);
  uVar2 = 0;
  while( true ) {
    if ((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x1e10u + (uint32_t)((int)(puVar3 + uVar4 * 8 + 2)))))) <= uVar2) {
      return 1;
    }
    psVar1 = ((short *)camry_host_ptr((uint32_t)(uVar2 * 2 + *(int *)(puVar3 + uVar4 * 8 + 0x1e14))));
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(*psVar1 * 0x18 + 0x1e68))))) == param_1) break;
    uVar2 = uVar2 + 1 & 0xff;
  }
  uVar2 = 0;
  if ((*((int *)camry_host_ptr((uint32_t)(puVar3 + *psVar1 * 0x18 + 0x1e60)))) != 0) {
    while( true ) {
      if ((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(*psVar1 * 0x18 + 0x1e6b))))) <= uVar2) {
        return 1;
      }
      if ((*((char *)camry_host_ptr((uint32_t)(*(int *)(puVar3 + *psVar1 * 0x18 + 0x1e60) + uVar2)))) == param_3) break;
      uVar2 = uVar2 + 1 & 0xff;
    }
  }
  return 0;
}



void FUN_00091788(undefined1 param_1)

{
  FUN_00092094(param_1);
  return;
}



void FUN_00091796(undefined1 param_1)

{
  FUN_000920a2(param_1);
  return;
}



void FUN_000917a4(undefined1 param_1)

{
  FUN_000920b0(param_1);
  return;
}



void FUN_000917b2(void)

{
  int iVar1;
  uint uVar2;
  
  uVar2 = 0;
  do {
    iVar1 = uVar2 * 2;
    uVar2 = uVar2 + 1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe564cu + (uint32_t)(iVar1) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe564du + (uint32_t)(iVar1) * 1u)))) = 0;
  } while (uVar2 < 2);
  DAT_febe5650 = 1;
  return;
}



undefined4 FUN_00091826(undefined1 param_1)

{
  FUN_000917d0(param_1,0);
  return 0;
}



undefined4 FUN_00091838(undefined1 param_1)

{
  FUN_000917d0(param_1,1);
  return 0;
}



undefined4 FUN_0009184a(undefined1 param_1)

{
  FUN_000917d0(param_1,2);
  return 0;
}



void FUN_00091ab8(void)

{
  return;
}



void FUN_00091ac2(undefined1 param_1)

{
  FUN_0007ed16(param_1);
  return;
}



void FUN_00091ad0(undefined1 param_1)

{
  FUN_0007ed2e(param_1);
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_91ade(void)

{
  return;
}



/* Null output returns0 without a read; otherwise return9240E status and its byte output. */

uint f33_dcm_get_security_level(uchar *level)

{
  uint uVar1;
  
  if (level == (uchar *)0x0) {
    uVar1 = 0;
  }
  else {
    uVar1 = f33_dcm_read_security_bitmap_level(level);
  }
  return uVar1;
}



/* Null output returns0 without a read; otherwise return924FC status and its byte output. */

uint f33_dcm_get_session(uchar *session)

{
  uint uVar1;
  
  if (session == (uchar *)0x0) {
    uVar1 = 0;
  }
  else {
    uVar1 = f33_dcm_read_session_snapshot(session);
  }
  return uVar1;
}



void FUN_00091b08(uchar param_1,uchar param_2)

{
  f33_dcm_stage_or_publish_session(param_1,param_2);
  return;
}



undefined4 FUN_00091b50(void)

{
  ushort uVar1;
  uint uVar2;
  undefined4 uVar3;
  
  uVar3 = 1;
  uVar2 = FUN_00092624();
  if ((uVar2 < 2) && (uVar1 = f33_dcm_count_receiving_slots(), uVar1 == 0)) {
    f33_dcm_cancel_software_timer('\x05');
    f33_dcm_restore_default_session();
    uVar3 = 0;
  }
  return uVar3;
}



void FUN_00091b78(void)

{
  f33_dcm_restore_default_session();
  return;
}



void FUN_00091c82(uchar param_1,uchar param_2)

{
  f33_dcm_deliver_response_notification(param_1,param_2);
  return;
}



/* Consume latched queue result/pending flag. Final notification resets queue transport state and
   finishes staged-session notifications before observers; pending flag preserves callback and
   invokes operation3. */

void f33_dcm_run_queued_response_notification(void)

{
  int iVar1;
  uchar uStack_6;
  uchar uStack_5;
  
  uStack_6 = '\0';
  uStack_5 = '\0';
  f33_dcm_snapshot_response_notification(&uStack_6,&uStack_5);
  if (uStack_5 != '\x01') {
    FUN_00092a9c();
    iVar1 = FUN_00092624();
    if (iVar1 == 2) {
      FUN_00092b4a();
    }
  }
  f33_dcm_finish_staged_session_notifications();
  f33_dcm_deliver_response_notification(uStack_6,uStack_5);
  return;
}



void FUN_00091cd2(undefined1 param_1,undefined1 param_2)

{
  FUN_00093162(param_1,param_2);
  return;
}



void FUN_00091de4(void)

{
  int iVar1;
  
  iVar1 = FUN_00092624();
  if (iVar1 == 2) {
    FUN_00093230();
  }
  return;
}



void FUN_00091df8(uchar param_1)

{
  int iVar1;
  
  iVar1 = FUN_00092624();
  if (iVar1 == 2) {
    f33_dcm_request_explicit_pending_response(param_1);
  }
  return;
}



void FUN_00091e12(uchar param_1)

{
  f33_dcm_publish_security_level(param_1);
  return;
}



void FUN_00091e6e(void)

{
  f33_dcm_cancel_active_service();
  return;
}



void FUN_00091f0e(void)

{
  int iVar1;
  
  iVar1 = FUN_00092d72();
  if (iVar1 != 1) {
    f33_dcm_cancel_active_service();
  }
  FUN_0009338e();
  return;
}



void FUN_00091f26(uint param_1,char param_2)

{
  int iVar1;
  uint uVar2;
  
  iVar1 = FUN_00092624();
  if (iVar1 == 1) {
    uVar2 = 0;
    do {
      iVar1 = FUN_00093f5a(uVar2);
      if ((iVar1 == 1) && (uVar2 != (param_1 & 0xffff))) {
        return;
      }
      uVar2 = uVar2 + 1;
    } while (uVar2 < 3);
    if (param_2 == '\x01') {
      uVar2 = FUN_00093b18();
      f33_dcm_arm_software_timer('\x05',uVar2);
    }
  }
  return;
}



void FUN_00091f64(uchar param_1)

{
  f33_dcm_commit_or_discard_staged_session(param_1);
  return;
}



void FUN_00091f72(undefined1 param_1)

{
  uint uVar1;
  
  uVar1 = FUN_00092624();
  if (uVar1 < 2) {
    FUN_00092610(param_1);
    FUN_00092b4a();
  }
  return;
}



void FUN_00091f90(void)

{
  f33_dcm_finish_staged_session_notifications();
  return;
}



void FUN_00091f9c(undefined1 param_1)

{
  FUN_000925a0(param_1);
  return;
}



/* Sequential initializer chain: 10 unconditional calls and no other statements; shape-verified. The
   called sequence is the function's entire behavior; chain family members differ in callee sets. */

void f33_run_init_chain_91ffa(void)

{
  f33_return_only_stub_9262a();
  f33_return_only_stub_922e8();
  FUN_000917b2();
  FUN_000924e8();
  FUN_000923ec();
  FUN_00092616();
  FUN_00092b24();
  FUN_00093ab2();
  FUN_00093aba();
  f33_return_only_stub_91ade();
  return;
}



undefined4 FUN_0009202a(undefined1 param_1,undefined1 param_2)

{
  FUN_0008b0de(param_1,param_2);
  return 0;
}



/* Constant source: return 0; shape-classified from the canonical corpus. Callers receive this
   literal directly; its meaning is not recovered. */

undefined4 f33_return_const_0_9203c(void)

{
  return 0;
}



/* Constant source: return 0; shape-classified from the canonical corpus. Callers receive this
   literal directly; its meaning is not recovered. */

undefined4 f33_return_const_0_92040(void)

{
  return 0;
}



void FUN_00092044(undefined1 param_1,undefined1 param_2)

{
  FUN_0009202a(param_1,param_2);
  return;
}



void FUN_00092094(undefined1 param_1)

{
  FUN_00091826(param_1);
  return;
}



void FUN_000920a2(undefined1 param_1)

{
  FUN_00091838(param_1);
  return;
}



void FUN_000920b0(undefined1 param_1)

{
  FUN_0009184a(param_1);
  return;
}



/* Only active mapped slots participate. Success with permission arbitrates ownership; selected
   codes10..13 claim pending-dispatch slot, phase2, P2/overall timers and deferred event0 scheduling
   via timer6. Failure releases slot and considers S3 restart. */

void f33_dcm_receive_indication(ushort receive_id,uchar result)

{
  uint32_t puVar1;
  uchar timer_slot;
  ushort uVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  undefined4 uVar6;
  
  puVar1 = 0x23dfcu;
  iVar3 = FUN_00093f0e(receive_id);
  if (iVar3 == 0xffff) {
    return;
  }
  iVar4 = FUN_00093e32(iVar3);
  if (iVar4 != 1) {
    return;
  }
  f33_dcm_cancel_software_timer('\0');
  iVar4 = FUN_0009185c(iVar3,1);
  if ((iVar4 == 1) && (result == '\0')) {
    uVar5 = f33_dcm_arbitrate_completed_receive((ushort)iVar3);
    if (uVar5 - 0x10 < 4) {
      FUN_00091938(iVar3,0);
      FUN_00094008(iVar3);
      FUN_00091f72(2);
      FUN_00093c94(0);
      uVar2 = f33_dcm_select_response_deadline('\0',uVar5 != 0x13);
      f33_dcm_arm_software_timer('\x04',(uint)uVar2);
      uVar5 = f33_dcm_get_overall_request_timeout();
      f33_dcm_arm_software_timer('\x02',uVar5);
      iVar4 = FUN_00093a8c();
      if (iVar4 == 1) {
        f33_dcm_arm_software_timer('\0',(*((uint *)camry_host_ptr((uint32_t)(puVar1 + 0x2088)))));
      }
      timer_slot = '\x06';
      uVar5 = (uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar1 + *(short *)(puVar1 + (short)(ushort)iVar3 * 0xc + 0x20ec) * 0x14 +
                               0x20ce))));
      goto LAB_000922a2;
    }
  }
  else {
    uVar6 = FUN_00093f5a(iVar3);
    FUN_00093c9a(iVar3,1);
    FUN_00091f26(iVar3,uVar6);
  }
  iVar3 = FUN_00093a8c();
  if (iVar3 != 1) {
    return;
  }
  uVar5 = (*((uint *)camry_host_ptr((uint32_t)(puVar1 + 0x2088))));
  timer_slot = '\0';
LAB_000922a2:
  f33_dcm_arm_software_timer(timer_slot,uVar5);
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_922e8(void)

{
  return;
}



/* Timer6 callback tombstones all pending event0 slots then appends one fresh event0. Occupancy is
   not compacted and both statuses are discarded, so a full ring can reject the fresh append. */

void f33_dcm_post_receive_dispatch_after_delay(void)

{
  f33_dcm_invalidate_queued_event('\0','\0');
  f33_dcm_enqueue_event('\0');
  return;
}



void FUN_000923de(undefined2 param_1)

{
  FUN_00081e90(param_1);
  return;
}



void FUN_00092602(void)

{
  return;
}



/* Constant source: return 0; shape-classified from the canonical corpus. Callers receive this
   literal directly; its meaning is not recovered. */

undefined4 f33_return_const_0_9260c(void)

{
  return 0;
}



void FUN_00092610(uchar param_1)

{
  f33_dcm_request_phase = param_1;
  return;
}



void FUN_00092616(void)

{
  FUN_00092610(0);
  return;
}



uchar FUN_00092624(void)

{
  return f33_dcm_request_phase;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_9262a(void)

{
  return;
}



undefined4 FUN_0009262c(int *param_1,char *param_2,int *param_3)

{
  ushort uVar1;
  uint uVar2;
  
  uVar1 = *(ushort *)(param_2 + 2);
  uVar2 = (uint)uVar1 + (uint)*(ushort *)(param_3 + 1);
  if (-1 < (int)(*(ushort *)(param_1 + 1) - uVar2) && *(ushort *)(param_1 + 1) != uVar2) {
    return 2;
  }
  uVar2 = 0;
  if (*param_2 == '\0') {
    for (; uVar2 < *(ushort *)(param_1 + 1); uVar2 = uVar2 + 1 & 0xffff) {
      (*((undefined1 *)camry_host_ptr((uint32_t)(*param_1 + uVar2)))) = (*((undefined1 *)camry_host_ptr((uint32_t)(*param_3 + uVar2))));
    }
  }
  else {
    uVar2 = 0;
    if (*param_2 != '\x01') {
      for (; uVar2 < *(ushort *)(param_1 + 1); uVar2 = uVar2 + 1 & 0xffff) {
        (*((undefined1 *)camry_host_ptr((uint32_t)(*param_1 + uVar2)))) = (*((undefined1 *)camry_host_ptr((uint32_t)(*param_3 + uVar2))));
      }
      return 0;
    }
    *(ushort *)(param_3 + 1) = uVar1 + *(ushort *)(param_3 + 1);
    *param_3 = *param_3 - (uint)uVar1;
    for (; uVar2 < *(ushort *)(param_1 + 1); uVar2 = uVar2 + 1 & 0xffff) {
      (*((undefined1 *)camry_host_ptr((uint32_t)(*param_1 + uVar2)))) = (*((undefined1 *)camry_host_ptr((uint32_t)(*param_3 + uVar2))));
    }
  }
  *(short *)(param_3 + 1) = (short)param_3[1] - (short)uVar2;
  *param_3 = *param_3 + uVar2;
  return 0;
}



/* Positive0 maps success/failure0/1; negative1 maps2/3; suppressed positive2 always0; other
   dispositions including silent3 and pending10 map2. Return is four-valued, not bool. */

uint f33_dcm_map_response_delivery_result(uchar disposition,uchar transport_result)

{
  if (disposition == '\0') {
    return (uint)(transport_result != '\0');
  }
  if (disposition == '\x01') {
    if (transport_result != '\0') {
      return 3;
    }
  }
  else if (disposition == '\x02') {
    return 0;
  }
  return 2;
}



undefined4 FUN_000927cc(char param_1,char param_2)

{
  undefined4 uVar1;
  int iVar2;
  uint uVar3;
  
  if (param_2 == '\0') {
    return 0;
  }
  iVar2 = FUN_00092b66();
  if (iVar2 != 0) {
    return 0;
  }
  f33_dcm_cancel_software_timer('\x03');
  f33_dcm_cancel_software_timer('\x04');
  f33_dcm_cancel_software_timer('\x02');
  FUN_00093676();
  if (param_1 == '0') {
    uVar3 = f33_dcm_enqueue_event('(');
    if (uVar3 != 0) {
LAB_00092828:
      f33_dcm_arm_software_timer('\x01',0);
      return 0;
    }
    uVar1 = 0x25;
  }
  else {
    uVar3 = f33_dcm_enqueue_event(')');
    if (uVar3 != 0) goto LAB_00092828;
    uVar1 = 0x50;
  }
  FUN_00092a86(uVar1);
  return 1;
}



void FUN_00092946(uint param_1)

{
  uint uVar1;
  
  uVar1 = FUN_00093ebc();
  if (uVar1 == (param_1 & 0xffff)) {
    FUN_00092a74(0,0);
    f33_dcm_enqueue_event(')');
  }
  return;
}



void FUN_00092a52(undefined2 param_1)

{
  FUN_00081b92(param_1);
  return;
}



void FUN_00092a60(undefined2 param_1)

{
  FUN_00081bac(param_1);
  return;
}



/* WARNING: This is an inlined function */
/* Return5970 inR10 while preserving incomingR6/R7. Inline exact leaf p-code where callers forward
   pointer arguments through this getter. */

F33DcmResponseQueue * f33_dcm_get_response_queue(void)

{
  return ((undefined *)camry_host_ptr(0xfebe5970u));
}



void FUN_00092b24(void)

{
  FUN_00092a9c();
  f33_dcm_reset_response_queue();
  return;
}



void FUN_00092b4a(void)

{
  int iVar1;
  
  iVar1 = FUN_00092b34();
  if (iVar1 == 0) {
    f33_dcm_reset_response_queue();
    FUN_00092a86(0x10);
  }
  return;
}



undefined4 FUN_00092bc2(undefined4 *param_1)

{
  undefined4 uVar1;
  
  uVar1 = 0;
  if ((param_1 != (undefined4 *)0x0) && ((undefined4 *)*param_1 != (undefined4 *)0x0)) {
    uVar1 = *(undefined4 *)*param_1;
  }
  return uVar1;
}



/* WARNING: Inlined function: f33_dcm_get_response_queue */

void FUN_00092c1e(uchar param_1)

{
  uchar disposition;
  int iVar1;
  
  iVar1 = FUN_00092bc2(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe5970u)))));
  disposition = 0xff;
  if (iVar1 != 0) {
    disposition = (*((uchar *)camry_host_ptr((uint32_t)(iVar1 + 0xc))));
  }
  f33_dcm_map_response_delivery_result(disposition,param_1);
  return;
}



undefined4 FUN_00092c46(uint param_1)

{
  uint uVar1;
  undefined4 uVar2;
  
  uVar1 = (param_1 & 0xff) - 0x30;
  uVar2 = 0;
  if ((uVar1 < 3) || (uVar1 == 0x10)) {
    uVar2 = 1;
  }
  return uVar2;
}



undefined4 FUN_00092d72(void)

{
  int iVar1;
  undefined4 uVar2;
  
  uVar2 = 0;
  iVar1 = FUN_00092b34();
  if ((((iVar1 == 0) || (iVar1 == 0x21 || iVar1 == 0x22)) || (iVar1 == 0x31 || iVar1 == 0x32)) ||
     ((iVar1 == 0x40 || (iVar1 == 0x50)))) {
    uVar2 = 1;
  }
  return uVar2;
}



void FUN_00092dd2(undefined1 param_1)

{
  FUN_00092da0(param_1);
  f33_dcm_reset_response_queue();
  FUN_00092a9c();
  return;
}



void FUN_00092de8(undefined1 param_1)

{
  FUN_00091f64(0);
  FUN_00092dd2(param_1);
  return;
}



void FUN_00092eae(ushort param_1,F33PduInfo *param_2)

{
  int iVar1;
  uint uVar2;
  
  iVar1 = FUN_00092b66();
  uVar2 = f33_dcm_submit_transport_response(param_1,param_2,'\x11');
  if (uVar2 == 0) {
    if (iVar1 == 0) {
      FUN_00091b08(1,1);
    }
    else {
      FUN_00091f64(0);
    }
  }
  else {
    if ((uVar2 == 0x83) || (iVar1 != 0)) {
      FUN_00091f64(0);
    }
    else {
      FUN_00091b08(1,0);
    }
    FUN_00092dd2(3);
  }
  return;
}



uchar FUN_00092f6a(void)

{
  return f33_dcm_explicit_pending_notification;
}



void FUN_00092f70(uchar param_1)

{
  f33_dcm_explicit_pending_notification = param_1;
  return;
}



void FUN_00093154(undefined1 *param_1,undefined1 param_2,undefined1 param_3)

{
  param_1[1] = param_2;
  *param_1 = 0x7f;
  param_1[2] = param_3;
  return;
}



void FUN_00093162(undefined1 param_1,undefined1 param_2)

{
  FUN_00093154(f33_dcm_final_negative_response,param_1,param_2);
  return;
}



void FUN_0009338e(void)

{
  undefined4 uVar1;
  int iVar2;
  
  uVar1 = FUN_000940ca();
  FUN_00093c94(0);
  iVar2 = FUN_00092b34();
  if (iVar2 == 0x25) {
    FUN_00091f90();
    FUN_00092a9c();
  }
  else {
    if (((iVar2 == 0x10 || iVar2 == 0x11) || (iVar2 == 0x23)) || (iVar2 == 0x30)) {
      FUN_00092a86(0x10);
      FUN_00091f64(0);
    }
    else {
      if (iVar2 != 0x24) {
        return;
      }
      FUN_00092a86(0x10);
      FUN_00091f64(0);
      FUN_00092a1e(uVar1);
    }
    f33_dcm_reset_response_queue();
  }
  return;
}



void FUN_0009364a(char param_1)

{
  undefined4 uVar1;
  int iVar2;
  
  if (param_1 != '\0') {
    iVar2 = FUN_00092b66();
    if (iVar2 != 0) {
      uVar1 = 0;
      goto LAB_0009366a;
    }
    FUN_00091b08(1,1);
  }
  uVar1 = 1;
LAB_0009366a:
  FUN_00091f64(uVar1);
  FUN_0009362c();
  return;
}



void FUN_00093676(void)

{
  FUN_00091b08(1,1);
  FUN_00091f64(1);
  FUN_0009362c();
  return;
}



/* Constant source: return 0xfebe5978; shape-classified from the canonical corpus. Callers receive
   this literal directly; its meaning is not recovered. */

undefined4 f33_return_const_febe5978_93690(void)

{
  return 0xfebe5978;
}



/* WARNING: Inlined function: f33_dcm_get_response_queue */

int FUN_00093696(undefined1 *param_1)

{
  int iVar1;
  int iVar2;
  
  iVar1 = camry_host_addr(FUN_00092b98(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe5970u))))));
  if (iVar1 == 0) {
    *param_1 = 0xff;
    iVar2 = 0;
  }
  else {
    iVar2 = iVar1 + 4;
    *param_1 = (*((undefined1 *)camry_host_ptr((uint32_t)(iVar1 + 0xc))));
    FUN_00092bd8();
  }
  return iVar2;
}



undefined4 FUN_00093a8c(void)

{
  ushort uVar1;
  int iVar2;
  
  iVar2 = FUN_00092624();
  uVar1 = f33_dcm_count_receiving_slots();
  if (iVar2 == 2) {
    if (uVar1 < 2) {
      return 0;
    }
  }
  else if (uVar1 == 0) {
    return 0;
  }
  return 1;
}



/* Single constant publisher: DAT_febe59d4 = 0xff; Shape-classified from the canonical corpus; the
   target cell is not yet named, so the written state's meaning is unknown. */

void FUN_00093ab2(void)

{
  DAT_febe59d4 = 0xff;
  return;
}



/* Return configured protocol timeout or selected functional override, and publish zero-time
   flag59EC. Real R10 return is used by timer2 admission; not void. */

uint f33_dcm_get_overall_request_timeout(void)

{
  int *piVar1;
  int iVar2;
  int iVar3;
  uint32_t puVar4;
  uint32_t puVar5;
  uint uVar6;
  short sStack_a;
  ushort uStack_8;
  ushort uStack_6;
  
  puVar4 = 0xfebeb800u;
  puVar5 = 0x23dfcu;
  sStack_a = 0;
  uStack_8 = 0;
  uStack_6 = 0;
  FUN_00093b32(f33_dcm_pending_dispatch_receive_slot,&sStack_a,&uStack_8,&uStack_6);
  iVar3 = (uint)uStack_8 * 4;
  piVar1 = ((int *)camry_host_ptr((uint32_t)(puVar5 + sStack_a * 0x14 + 0x20c4)));
  iVar2 = (uint)uStack_6 * 0xc;
  if (((*((char *)camry_host_ptr((uint32_t)(*(int *)(*(int *)(*piVar1 + iVar3) + 4) + iVar2 + 9)))) == '\x01') &&
     ((*((char *)camry_host_ptr((uint32_t)(*(int *)(*(int *)(*piVar1 + iVar3) + 4) + iVar2 + 8)))) == '\x01')) {
    uVar6 = (*((uint *)camry_host_ptr((uint32_t)(*(int *)(*(int *)(*piVar1 + iVar3) + 4) + iVar2))));
  }
  else {
    uVar6 = piVar1[1];
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x5e14))))) = uVar6 == 0;
  return uVar6;
}



ushort FUN_00093c5a(void)

{
  return f33_dcm_pending_spacing_raw;
}



void FUN_00093c66(ushort param_1)

{
  f33_dcm_current_dispatch_receive_slot = param_1;
  return;
}



uchar FUN_00093c8e(void)

{
  return f33_dcm_pending_transport_accepted;
}



void FUN_00093c94(uchar param_1)

{
  f33_dcm_pending_transport_accepted = param_1;
  return;
}



void FUN_00093ce6(undefined4 *param_1)

{
  uint32_t puVar1;
  uint32_t puVar2;
  short local_c;
  ushort uStack_a;
  
  puVar1 = 0xfebeb800u;
  puVar2 = 0x23dfcu;
  local_c = 0;
  uStack_a = 0;
  FUN_00093cce(f33_dcm_current_dispatch_receive_slot,&local_c,&uStack_a);
  *param_1 = puVar1 + -0x5de0;
  *(short *)(param_1 + 1) =
       (short)**(undefined4 **)
                ((*((int *)camry_host_ptr((uint32_t)((uint)uStack_a * 4 + *(int *)(puVar2 + local_c * 0x14 + 0x20c4))))) + 8);
  return;
}



undefined1 FUN_00093d2e(void)

{
  uint32_t puVar1;
  undefined1 uVar2;
  short sStack_e;
  ushort uStack_c;
  ushort uStack_a;
  
  puVar1 = 0x23dfcu;
  sStack_e = 0;
  uVar2 = 0;
  uStack_c = 0;
  uStack_a = 0;
  FUN_00093b32(f33_dcm_current_dispatch_receive_slot,&sStack_e,&uStack_c,&uStack_a);
  if ((*((char *)camry_host_ptr((uint32_t)(*(int *)(*(int *)(*(int *)(puVar1 + sStack_e * 0x14 + 0x20c4) + (uint)uStack_c * 4)
                        + 4) + (uint)uStack_a * 0xc + 9)))) == '\x01') {
    if ((*((char *)camry_host_ptr((uint32_t)(*(int *)(*(int *)(*(int *)(puVar1 + sStack_e * 0x14 + 0x20c4) + (uint)uStack_c * 4
                                   ) + 4) + (uint)uStack_a * 0xc + 8)))) == '\x01') {
      uVar2 = 1;
    }
    else {
      uVar2 = 0;
    }
  }
  return uVar2;
}



undefined2 FUN_00093e82(void)

{
  uint32_t puVar1;
  short local_8;
  ushort uStack_6;
  
  puVar1 = 0x23dfcu;
  local_8 = 0;
  uStack_6 = 0;
  FUN_00093cce(f33_dcm_current_dispatch_receive_slot,&local_8,&uStack_6);
  return (*((undefined2 *)camry_host_ptr((uint32_t)(*(int *)(*(int *)((uint)uStack_6 * 4 + *(int *)(puVar1 + local_8 * 0x14 + 0x20c4)) + 8) +
          6))));
}



undefined2 FUN_00093ebc(void)

{
  uint32_t puVar1;
  short local_8;
  ushort uStack_6;
  
  puVar1 = 0x23dfcu;
  local_8 = 0;
  uStack_6 = 0;
  FUN_00093cce(f33_dcm_current_dispatch_receive_slot,&local_8,&uStack_6);
  return (*((undefined2 *)camry_host_ptr((uint32_t)(*(int *)(*(int *)((uint)uStack_6 * 4 + *(int *)(puVar1 + local_8 * 0x14 + 0x20c4)) + 8) +
          4))));
}



void FUN_00093f66(int param_1,ushort *param_2,char param_3)

{
  undefined *puVar1;
  undefined *puVar2;
  uint32_t puVar3;
  uint uVar4;
  short sStack_1e;
  ushort uStack_1c;
  ushort uStack_1a;
  
  puVar3 = 0x23dfcu;
  sStack_1e = 0;
  uStack_1c = 0;
  uVar4 = 0;
  uStack_1a = 0;
  *param_2 = 0;
  puVar1 = ((undefined *)camry_host_ptr(0xfebeb800u));
  do {
    puVar2 = puVar1;
    if ((puVar1[uVar4 * 0x10 + -0x5e06] == '\x01') &&
       ((param_3 != '\x02' || (uVar4 != *(ushort *)(puVar1 + -0x5e1e))))) {
      FUN_00093b32(uVar4,&sStack_1e,&uStack_1c,&uStack_1a);
      (*((undefined2 *)camry_host_ptr((uint32_t)((uint)*param_2 * 4 + param_1)))) =
           (*((undefined2 *)camry_host_ptr((uint32_t)((uint)uStack_1a * 0xc +
             *(int *)(*(int *)((uint)uStack_1c * 4 + *(int *)(puVar3 + sStack_1e * 0x14 + 0x20c4)) +
                     4) + 6))));
      (*((short *)camry_host_ptr((uint32_t)((uint)*param_2 * 4 + param_1 + 2)))) = (short)uVar4;
      *param_2 = *param_2 + 1;
      puVar1[uVar4 * 0x10 + -0x5e05] = 1;
    }
    uVar4 = uVar4 + 1;
    puVar1 = puVar2;
  } while (uVar4 < 3);
  return;
}


