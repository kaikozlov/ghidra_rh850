#include "common.h"


void FUN_000b149c(void)

{
  uint uVar1;
  
  uVar1 = 0;
  do {
    *(undefined4 *)(((undefined *)camry_host_ptr(0xfebeb090u)) + uVar1 * 4) = 0xffffffff;
    uVar1 = uVar1 + 1;
  } while (uVar1 < 2);
  return;
}



void FUN_000b14b2(void)

{
  int iVar1;
  uint uVar2;
  
  uVar2 = 0;
  do {
    iVar1 = uVar2 * 4;
    *(undefined4 *)(((undefined *)camry_host_ptr(0xfebeb098u)) + iVar1) = 0;
    uVar2 = uVar2 + 1;
    *(undefined4 *)(((undefined *)camry_host_ptr(0xfebeb090u)) + iVar1) = 0xffffffff;
  } while (uVar2 < 2);
  return;
}



undefined4 FUN_000b14d2(uint param_1)

{
  uint *puVar1;
  int iVar2;
  uint32_t puVar3;
  undefined4 uVar4;
  uint uVar5;
  
  puVar3 = 0xfebeb800u;
  uVar5 = param_1 & 0xff;
  if (uVar5 < 0x32) {
    iVar2 = (uVar5 >> 5) * 4;
    puVar1 = (uint *)(((undefined *)camry_host_ptr(0xfebeb098u)) + iVar2);
    param_1 = param_1 & 0x1f;
    if (((*puVar1 >> param_1 & 1) != 0) || ((*(uint *)(((undefined *)camry_host_ptr(0xfebeb090u)) + iVar2) >> param_1 & 1) == 0))
    {
      uVar4 = FUN_000d1da0(0xffc0);
      *puVar1 = *puVar1 & ~(1 << param_1);
      (*((uint *)camry_host_ptr((uint32_t)(puVar3 + iVar2 + -0x770)))) = (*((uint *)camry_host_ptr((uint32_t)(puVar3 + iVar2 + -0x770)))) | 1 << param_1;
      FUN_000d1dc6(uVar4);
    }
    uVar4 = FUN_000b1c34(uVar5);
  }
  else {
    uVar4 = 0xffff;
  }
  return uVar4;
}



/* Reconcile request and cancellation bitmaps for IDs0..49 into status slotsB0A8. Materialize
   requested/not-cancelled slots throughB1BFE; acknowledged5AA5 causes request cancellation but
   clears only on a later reconciliation. Cancelled pendingA55A is NOT revoked. Native mixed-state
   pass covers both bitmap words and the domain boundary. Reconcile50 bitmap requests and
   cancellations with pending A55A/acknowledged5AA5 slots. Native composed pass covers request
   precedence, acknowledged clearing, pending cancellation retention, PMR restoration and slot50
   canary. */

void f33_reconcile_mode_requests(void)

{
  int iVar1;
  undefined8 uVar2;
  uint uVar3;
  uint request_id;
  
  uVar2 = 0xfebeb800;
  request_id = 0;
  do {
    iVar1 = (request_id >> 5) * 4;
    uVar3 = request_id & 0x1f;
    if ((*(uint *)(((undefined *)camry_host_ptr(0xfebeb098u)) + iVar1) >> uVar3 & 1) == 0) {
      if (((*((uint *)camry_host_ptr((uint32_t)(iVar1 + (int)uVar2 + -0x770)))) >> uVar3 & 1) != 0) {
        f33_clear_acknowledged_mode_request(request_id);
      }
    }
    else if ((((*((uint *)camry_host_ptr((uint32_t)(iVar1 + (int)uVar2 + -0x770)))) >> uVar3 & 1) == 0) &&
            (uVar3 = f33_materialize_mode_request(request_id), uVar3 == 0x5aa5)) {
      FUN_000b14d2(request_id);
    }
    request_id = request_id + 1;
  } while (request_id < 0x32);
  return;
}



undefined4 FUN_000b15ac(uint param_1)

{
  uint *puVar1;
  int iVar2;
  uint32_t puVar3;
  undefined4 uVar4;
  uint uVar5;
  
  puVar3 = 0xfebeb800u;
  uVar5 = param_1 & 0xff;
  if (uVar5 < 0x32) {
    iVar2 = (uVar5 >> 5) * 4;
    puVar1 = (uint *)(((undefined *)camry_host_ptr(0xfebeb098u)) + iVar2);
    param_1 = param_1 & 0x1f;
    if (((*puVar1 >> param_1 & 1) == 0) || ((*(uint *)(((undefined *)camry_host_ptr(0xfebeb090u)) + iVar2) >> param_1 & 1) != 0))
    {
      uVar4 = FUN_000d1da0(0xffc0);
      *puVar1 = *puVar1 | 1 << param_1;
      (*((uint *)camry_host_ptr((uint32_t)(puVar3 + iVar2 + -0x770)))) = (*((uint *)camry_host_ptr((uint32_t)(puVar3 + iVar2 + -0x770)))) & ~(1 << param_1);
      FUN_000d1dc6(uVar4);
    }
    uVar4 = FUN_000b1c34(uVar5);
  }
  else {
    uVar4 = 0xffff;
  }
  return uVar4;
}



/* Commit liveB11A with XOR5555/B0A0 and XORAAAA/B0A4 throughD26D0 priority-protected redundant
   publisher. Does not publishE8CC. */

undefined4 f33_publish_live_application_mode(ushort mode)

{
  return FUN_000d26d0(mode,((undefined *)camry_host_ptr(0xfebeb11au)),((undefined *)camry_host_ptr(0xfebeb0a0u)),((undefined *)camry_host_ptr(0xfebeb0a4u)));
}



undefined4 FUN_000b163a(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    *(undefined2 *)(((undefined *)camry_host_ptr(0xfebeb0a8u)) + iVar3 * 2) = 0;
    iVar1 = iVar3 + -0x31;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  DAT_febeb10c = 0;
  DAT_febeb0a6 = 0xff;
  DAT_febeb11c = 0;
  DAT_febeb0a2 = 0xffff;
  return f33_publish_live_application_mode(DAT_febeb11a);
}



/* Clear retainedB114 then call empty0100 entryhook. Separate reset path; normal familyexit does not
   clear the readinesscounter. */

void f33_reset_mode_readiness_counter(void)

{
  DAT_febeb114 = 0;
  f33_return_only_stub_b1d9e();
  return;
}



/* Vote liveB11A and redundantB0A0/B0A4; republish voted value only on repairable statuses-12/-11.
   No automatic invalid-to-zero fallback. */

void f33_repair_live_application_mode(void)

{
  int iVar1;
  undefined2 uStack_12;
  
  iVar1 = FUN_000d242e(((undefined *)camry_host_ptr(0xfebeb11au)),((undefined *)camry_host_ptr(0xfebeb0a0u)),((undefined *)camry_host_ptr(0xfebeb0a4u)),&uStack_12);
  if ((iVar1 != 0) && (iVar1 == -0xc || iVar1 == -0xb)) {
    FUN_000d26d0(uStack_12,((undefined *)camry_host_ptr(0xfebeb11au)),((undefined *)camry_host_ptr(0xfebeb0a0u)),((undefined *)camry_host_ptr(0xfebeb0a4u)));
  }
  return;
}



/* Return1 exactly when request slotB0A8+2*ID isA55A. Pending IDs<16 capture
   selectedB10C/complementB0A6 and old liveB11C/complementB0A2. Internal IDs>=16 do not replace
   selected metadata. Failed probes retain metadata. Caller must provide valid slot ID. */

uint f33_probe_pending_mode_request(uchar request_id)

{
  uint uVar1;
  
  if (*(short *)(((undefined *)camry_host_ptr(0xfebeb0a8u)) + (uint)request_id * 2) == -0x5aa6) {
    uVar1 = 1;
    if (request_id < 0x10) {
      DAT_febeb0a6 = ~request_id;
      DAT_febeb10c = request_id;
      DAT_febeb11c = DAT_febeb11a;
      DAT_febeb0a2 = ~DAT_febeb11a;
      return uVar1;
    }
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}



/* If old and new mode<0A00, run AEB00 old-family exit then new-family entry before redundant live
   commitB11A/B0A0/B0A4. Hooks see old live mode. No same-mode/family short circuit and no E8CC
   publication. */

void f33_transition_application_mode(ushort new_mode)

{
  if ((DAT_febeb11a < 0xa00) && (new_mode < 0xa00)) {
    (*(int (*)())f33_mode_family_hooks[DAT_febeb11a >> 8].exit)();
    (*(int (*)())f33_mode_family_hooks[new_mode >> 8].entry)();
    f33_publish_live_application_mode(new_mode);
  }
  return;
}



/* Change pendingA55A to5AA5 only for matching selectedID/complement, or internalID>16. Does not
   clear request bitmap or losing low pending slots. ID16 is not unconditional. */

void f33_acknowledge_selected_mode_request(uchar request_id)

{
  uint uVar1;
  
  uVar1 = (uint)request_id;
  if ((((uVar1 == DAT_febeb10c) && ((~uVar1 & 0xff) == (uint)DAT_febeb0a6)) || (0x10 < uVar1)) &&
     (*(short *)(((undefined *)camry_host_ptr(0xfebeb0a8u)) + uVar1 * 2) == -0x5aa6)) {
    *(short *)(((undefined *)camry_host_ptr(0xfebeb0a8u)) + uVar1 * 2) = 0x5aa5;
  }
  return;
}



/* Require66F1E NvM readiness first. Then return5A/resetB114 when all sampledB072..B075 zero or
   retainedcount>=20. Otherwise replace8A70/8AD0 owners0/1 with20002 and increment;19\u219220 still
   returns0. NvM not ready freezes counter even above20 and with zero snapshots. Counts are
   invocations, not measuredtime. Native readiness compositions distinguish entry19 from20 and
   verify busy NvM freezes the retained counter while a lower-priority mode request remains blocked.
   Counts are invocations,not elapsed time. */

uint f33_qualify_mode_restart_readiness(void)

{
  char cVar1;
  char cVar2;
  char cVar3;
  char cVar4;
  uint32_t puVar5;
  uint uVar6;
  byte bVar7;
  
  bVar7 = DAT_febeb114;
  cVar4 = DAT_febeb075;
  cVar3 = DAT_febeb074;
  cVar2 = DAT_febeb073;
  cVar1 = DAT_febeb072;
  puVar5 = 0xfebeb800u;
  uVar6 = f33_query_application_nvm_readiness();
  if (uVar6 == 1) {
    if (((((cVar1 == '\0') && (cVar3 == '\0')) && (cVar2 == '\0')) && (cVar4 == '\0')) ||
       (DAT_000af3dc <= bVar7)) {
      bVar7 = 0;
      uVar6 = 0x5a;
      goto LAB_000b17e6;
    }
    f33_set_channel_owner_request('\0',0x20002);
    f33_set_channel_owner_request('\x01',0x20002);
    thunk_FUN_00056e66(0, camry_host_addr(((undefined *)camry_host_ptr(0x20002u))));
    thunk_FUN_00056e66(1, camry_host_addr(((undefined *)camry_host_ptr(0x20002u))));
    bVar7 = bVar7 + 1;
  }
  uVar6 = 0;
LAB_000b17e6:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x6ec))))) = bVar7;
  return uVar6;
}



/* Clear redundantNvM gates0671/0672 viaFF010/FF024, transition0000 through realhooks, then publish
   foreground request8C08=A55A throughFEFC0/5889A. Not an immediate CPU reset or mode snapshot
   publish. Native0701 readiness branch takes the exact constant-zero selector, publishes mode0000
   and redundant foreground restart,without transition0800 or hardware reset. */

int f33_request_foreground_restart_from_mode(void)

{
  thunk_FUN_00066f84();
  thunk_FUN_00066fba();
  f33_transition_application_mode(0);
  return thunk_FUN_0005889a();
}



/* Repair live mode, run at most one current-family internal transition, then family-prioritized
   major requests. Low IDs acknowledge only selected/complement-qualified pending winner; losing low
   pending requests retain.0701 pending2 can suppress10/7 until NvM/output snapshot readiness;
   exactFF038 constant0 then requests foreground restart through mode0000, not0800. All families
   except0200 clear direct-enable8B4C/4D. Mode publicationE8CC is separate. Native major-mode
   compositions verify programming before lower service,0701 wait at19/software restart at20,and0800
   pending2 suppressing7 during NvM busy. Remaining major/submode branches are static
   reconstruction. */

void f33_advance_application_mode(void)

{
  uint32_t puVar1;
  uchar uVar2;
  ushort uVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  
  puVar1 = 0xfebeb800u;
  f33_repair_live_application_mode();
  uVar3 = (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x6e6)))) & 0xff00;
  if (uVar3 == 0x100) {
    f33_clear_direct_output_enables();
    f33_advance_mode100_substate();
    uVar6 = f33_probe_pending_mode_request('\0');
    if (uVar6 == 1) {
      uVar3 = 0x700;
LAB_000b1894:
      f33_transition_application_mode(uVar3);
    }
    else {
      uVar6 = f33_probe_pending_mode_request('\t');
      if (uVar6 == 1) {
        uVar3 = 0x900;
        goto LAB_000b1894;
      }
      uVar6 = f33_probe_pending_mode_request('\x05');
      if (uVar6 == 1) {
        uVar3 = 0x200;
        goto LAB_000b1894;
      }
    }
    f33_acknowledge_selected_mode_request('\0');
    uVar2 = '\x05';
  }
  else {
    if (uVar3 == 0x200) {
      f33_advance_mode200_output_sequence();
      uVar6 = f33_probe_pending_mode_request('\0');
      if ((uVar6 == 1) || (uVar6 = f33_probe_pending_mode_request('\x01'), uVar6 == 1)) {
        uVar3 = 0x700;
LAB_000b18e0:
        f33_transition_application_mode(uVar3);
      }
      else {
        uVar6 = f33_probe_pending_mode_request('\t');
        if (uVar6 == 1) {
          uVar3 = 0x900;
          goto LAB_000b18e0;
        }
        uVar6 = f33_probe_pending_mode_request('\x03');
        if (uVar6 == 1) {
          uVar3 = 0x300;
          goto LAB_000b18e0;
        }
      }
      f33_acknowledge_selected_mode_request('\0');
      f33_acknowledge_selected_mode_request('\x01');
      f33_acknowledge_selected_mode_request('\t');
      uVar2 = '\x03';
      goto LAB_000b1bf6;
    }
    if (uVar3 == 0x300) {
      f33_clear_direct_output_enables();
      f33_advance_mode300_substate();
      uVar6 = f33_probe_pending_mode_request('\0');
      if ((uVar6 == 1) || (uVar6 = f33_probe_pending_mode_request('\x01'), uVar6 == 1)) {
        uVar3 = 0x700;
LAB_000b194c:
        f33_transition_application_mode(uVar3);
      }
      else {
        uVar6 = f33_probe_pending_mode_request('\t');
        if (uVar6 == 1) {
          uVar3 = 0x900;
          goto LAB_000b194c;
        }
        uVar6 = f33_probe_pending_mode_request('\x06');
        if (uVar6 == 1) {
          uVar3 = 0x500;
          goto LAB_000b194c;
        }
        uVar6 = f33_probe_pending_mode_request('\f');
        if (uVar6 == 1) {
          uVar3 = 0x400;
          goto LAB_000b194c;
        }
      }
      f33_acknowledge_selected_mode_request('\0');
      f33_acknowledge_selected_mode_request('\x01');
      f33_acknowledge_selected_mode_request('\t');
      f33_acknowledge_selected_mode_request('\f');
      uVar2 = '\x06';
      goto LAB_000b1bf6;
    }
    if (uVar3 == 0x400) {
      f33_clear_direct_output_enables();
      f33_apply_mode400_output_requests();
      uVar6 = f33_probe_pending_mode_request('\0');
      if ((uVar6 == 1) || (uVar6 = f33_probe_pending_mode_request('\x01'), uVar6 == 1)) {
LAB_000b19b4:
        uVar3 = 0x700;
LAB_000b19c8:
        f33_transition_application_mode(uVar3);
      }
      else {
        uVar6 = f33_probe_pending_mode_request('\t');
        if (uVar6 == 1) {
          uVar3 = 0x900;
          goto LAB_000b19c8;
        }
        uVar6 = f33_probe_pending_mode_request('\x06');
        if (uVar6 == 1) {
          uVar3 = 0x500;
          goto LAB_000b19c8;
        }
        uVar6 = f33_probe_pending_mode_request('\v');
        if (uVar6 == 1) goto LAB_000b19b4;
        uVar6 = f33_probe_pending_mode_request('\a');
        if (uVar6 == 1) {
          uVar3 = 0x600;
          goto LAB_000b19c8;
        }
      }
      f33_acknowledge_selected_mode_request('\0');
      f33_acknowledge_selected_mode_request('\x01');
      f33_acknowledge_selected_mode_request('\t');
      f33_acknowledge_selected_mode_request('\x06');
      uVar2 = '\v';
LAB_000b19e6:
      f33_acknowledge_selected_mode_request(uVar2);
      uVar2 = '\a';
      goto LAB_000b1bf6;
    }
    if (uVar3 == 0x500) {
      f33_clear_direct_output_enables();
      f33_advance_service_family();
      uVar6 = f33_probe_pending_mode_request('\0');
      if ((uVar6 == 1) || (uVar6 = f33_probe_pending_mode_request('\x01'), uVar6 == 1)) {
        uVar3 = 0x700;
LAB_000b1b5a:
        f33_transition_application_mode(uVar3);
      }
      else {
        uVar6 = f33_probe_pending_mode_request('\t');
        if (uVar6 == 1) {
          uVar3 = 0x900;
          goto LAB_000b1b5a;
        }
        uVar6 = f33_probe_pending_mode_request('\x04');
        if (uVar6 == 1) {
          uVar3 = 0x300;
          if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x65c))))) != '\0') {
            uVar3 = 0x400;
          }
          goto LAB_000b1b5a;
        }
        uVar6 = f33_probe_pending_mode_request('\a');
        if (uVar6 == 1) {
          uVar3 = 0x600;
          goto LAB_000b1b5a;
        }
      }
      f33_acknowledge_selected_mode_request('\0');
      f33_acknowledge_selected_mode_request('\x01');
      f33_acknowledge_selected_mode_request('\t');
      uVar2 = '\x04';
      goto LAB_000b19e6;
    }
    if (uVar3 != 0x600) {
      if (uVar3 == 0x700) {
        f33_clear_direct_output_enables();
        uVar6 = f33_advance_mode700_substate();
        uVar4 = f33_probe_pending_mode_request('\x02');
        uVar5 = f33_probe_pending_mode_request('\0');
        if (uVar5 == 1) {
LAB_000b1a64:
          uVar3 = 0x800;
LAB_000b1a78:
          f33_transition_application_mode(uVar3);
        }
        else {
          uVar5 = f33_probe_pending_mode_request('\t');
          if (uVar5 == 1) {
            uVar3 = 0x900;
            goto LAB_000b1a78;
          }
          if ((uVar6 == 0) && (uVar4 == 1)) {
            if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6eb))))) != 'Z') {
              thunk_FUN_000515e6();
              (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6eb))))) = 0x5a;
            }
            uVar6 = f33_qualify_mode_restart_readiness();
            if (uVar6 == 0x5a) {
              uVar6 = f33_get_mode_restart_hardware_selector();
              if (uVar6 == 0x5a) goto LAB_000b1a64;
              f33_request_foreground_restart_from_mode();
              f33_acknowledge_selected_mode_request('\x02');
            }
          }
          else {
            uVar6 = f33_probe_pending_mode_request('\n');
            if (uVar6 == 1) goto LAB_000b1a64;
            uVar6 = f33_probe_pending_mode_request('\a');
            if (uVar6 == 1) {
              uVar3 = 0x600;
              goto LAB_000b1a78;
            }
          }
        }
        f33_acknowledge_selected_mode_request('\0');
        f33_acknowledge_selected_mode_request('\t');
        f33_acknowledge_selected_mode_request('\a');
        uVar2 = '\n';
        goto LAB_000b1bf6;
      }
      if (uVar3 != 0x800) {
        if (uVar3 != 0x900) {
          return;
        }
        f33_clear_direct_output_enables();
        f33_return_only_stub_b33d8();
        uVar6 = f33_probe_pending_mode_request('\x0e');
        if (uVar6 == 1) {
          f33_transition_application_mode(0x800);
        }
        uVar2 = '\x0e';
        goto LAB_000b1bf6;
      }
      f33_clear_direct_output_enables();
      f33_apply_mode800_ready_output_requests();
      uVar6 = f33_probe_pending_mode_request('\x0f');
      if (uVar6 == 1) {
        FUN_000ff0d8();
      }
      else {
        uVar6 = f33_probe_pending_mode_request('\t');
        if (uVar6 == 1) {
          uVar3 = 0x900;
LAB_000b1aee:
          f33_transition_application_mode(uVar3);
        }
        else {
          uVar6 = f33_probe_pending_mode_request('\x02');
          if (uVar6 == 1) {
            thunk_FUN_000515d4();
            uVar6 = f33_qualify_mode_restart_readiness();
            if (uVar6 == 0x5a) {
              thunk_FUN_0006163e();
              f33_acknowledge_selected_mode_request('\x02');
            }
          }
          else {
            uVar6 = f33_probe_pending_mode_request('\a');
            if (uVar6 == 1) {
              uVar3 = 0x600;
              goto LAB_000b1aee;
            }
          }
        }
      }
      f33_acknowledge_selected_mode_request('\x0f');
      uVar2 = '\t';
      goto LAB_000b19e6;
    }
    f33_clear_direct_output_enables();
    f33_return_only_stub_b32f2();
    uVar6 = f33_probe_pending_mode_request('\0');
    if (uVar6 == 1) {
LAB_000b1bc4:
      uVar3 = 0x700;
LAB_000b1bd8:
      f33_transition_application_mode(uVar3);
    }
    else {
      uVar6 = f33_probe_pending_mode_request('\r');
      if (uVar6 == 1) {
LAB_000b1bd4:
        uVar3 = 0x900;
        goto LAB_000b1bd8;
      }
      uVar6 = f33_probe_pending_mode_request('\b');
      if ((uVar6 == 1) || (uVar6 = f33_probe_pending_mode_request('\x01'), uVar6 == 1))
      goto LAB_000b1bc4;
      uVar6 = f33_probe_pending_mode_request('\t');
      if (uVar6 == 1) goto LAB_000b1bd4;
    }
    f33_acknowledge_selected_mode_request('\0');
    f33_acknowledge_selected_mode_request('\b');
    f33_acknowledge_selected_mode_request('\x01');
    uVar2 = '\r';
  }
  f33_acknowledge_selected_mode_request(uVar2);
  uVar2 = '\t';
LAB_000b1bf6:
  f33_acknowledge_selected_mode_request(uVar2);
  return;
}



/* Index by low8(request_id), without a local bounds check. Preserve acknowledged5AA5, otherwise
   publish pendingA55A. Return the zero-extended status in full R10; this return is consumed byB1546
   and is not void. Materialize low-byte request slot asA55A unless already5AA5, returning full
   zero-extended status in r10. Native reconciliation consumes the real result; correcting false
   void prototype restores caller dataflow. */

uint f33_materialize_mode_request(uint request_id)

{
  undefined *puVar1;
  
  puVar1 = ((undefined *)camry_host_ptr((uint32_t)((uint)*(ushort *)(((undefined *)camry_host_ptr(0xfebeb0a8u)) + (request_id & 0xff) * 2))));
  if ((uintptr_t)(puVar1)!=(uintptr_t)(((undefined *)camry_host_ptr((uint32_t)(0x5aa5))))) {
    puVar1 = ((undefined *)camry_host_ptr(0xa55au));
    *(ushort *)(((undefined *)camry_host_ptr(0xfebeb0a8u)) + (request_id & 0xff) * 2) = 0xa55a;
  }
  return (uint)camry_host_addr(puVar1);
}



/* Index low8(request_id), without a local bounds check. Clear only5AA5; preserve pendingA55A and
   every other value. Cancellation after materialization therefore does not revoke an unaccepted
   request. Clear only acknowledged5AA5 slots. Cancellation does not revoke an already materialized
   pendingA55A request. Native composed reconciliation distinguishes both statuses. */

void f33_clear_acknowledged_mode_request(uint request_id)

{
  if (*(short *)(((undefined *)camry_host_ptr(0xfebeb0a8u)) + (request_id & 0xff) * 2) == 0x5aa5) {
    *(short *)(((undefined *)camry_host_ptr(0xfebeb0a8u)) + (request_id & 0xff) * 2) = 0;
  }
  return;
}



/* JMP LP with no state change; AEB00 table 0x0 entry, 0x0 exit. Exact-image hook, not a missing
   implementation. */

void f33_mode_hook_b1c32(void)

{
  return;
}



undefined2 FUN_000b1c34(uint param_1)

{
  return *(undefined2 *)(((undefined *)camry_host_ptr(0xfebeb0a8u)) + (param_1 & 0xff) * 2);
}



bool FUN_000b1c40(void)

{
  return DAT_febeb0a6 == (byte)~DAT_febeb10c;
}



/* After common warm reinitialization and all task input snapshots, transition live mode to0100
   through real entry/exit hooks. Not directE8CC publication; subsequent foreground dispatch owns
   the published generation. */

void f33_start_mode100_after_foreground_restart(void)

{
  f33_transition_application_mode(0x100);
  return;
}



undefined2 FUN_000b1c64(void)

{
  undefined2 uStack_6;
  
  FUN_000d242e(((undefined *)camry_host_ptr(0xfebeb11au)),((undefined *)camry_host_ptr(0xfebeb0a0u)),((undefined *)camry_host_ptr(0xfebeb0a4u)),&uStack_6);
  return uStack_6;
}



undefined4 FUN_000b1c84(void)

{
  return FUN_000b15ac(0x11);
}



int FUN_000b1c96(void)

{
  int iVar1;
  
  thunk_FUN_00066fd4();
  iVar1 = thunk_FUN_000588b6();
  if (iVar1 != 0) {
    thunk_FUN_00066ef4();
  }
  return iVar1;
}



void FUN_000b1cae(void)

{
  thunk_FUN_00045d98();
  FUN_000bd9da();
  FUN_000bd81e();
  return;
}



undefined4 FUN_000b1cc2(void)

{
  return FUN_000b15ac(0x13);
}



undefined4 FUN_000b1ce0(void)

{
  return FUN_000b15ac(0x14);
}



undefined4 FUN_000b1cf2(void)

{
  return FUN_000b15ac(5);
}



/* Exact0100\u21920101(event17)\u21920102(18)\u21920103(19);0103 event20 requests major5. Internal
   events acknowledge independently of selected majorID.0100/0103 self-request their next
   internalevent;0101 waits NvM acquisition phase0 via5678A.
   Exact0100→0101(event17)→0102(18)→0103(19);0103 event20 requests major5. */

void f33_advance_mode100_substate(void)

{
  uchar request_id;
  uint uVar1;
  
  switch(DAT_febeb11a) {
  case 0x100:
    FUN_000b1c84();
    uVar1 = f33_probe_pending_mode_request('\x11');
    if (uVar1 == 1) {
      FUN_000b1c96();
      f33_publish_live_application_mode(0x101);
    }
    request_id = '\x11';
    break;
  case 0x101:
    uVar1 = f33_probe_pending_mode_request('\x12');
    if (uVar1 == 1) {
      FUN_000b1cae();
      FUN_000b1cc2();
      f33_publish_live_application_mode(0x102);
    }
    request_id = '\x12';
    break;
  case 0x102:
    uVar1 = f33_probe_pending_mode_request('\x13');
    if (uVar1 == 1) {
      thunk_FUN_000d10d4();
      f33_publish_live_application_mode(0x103);
    }
    request_id = '\x13';
    break;
  case 0x103:
    FUN_000b1ce0();
    uVar1 = f33_probe_pending_mode_request('\x14');
    if (uVar1 == 1) {
      FUN_000b1cf2();
    }
    request_id = '\x14';
    break;
  default:
    goto switchD_000b1d10_default;
  }
  f33_acknowledge_selected_mode_request(request_id);
switchD_000b1d10_default:
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_b1d9e(void)

{
  return;
}



/* JMP LP with no state change; AEB00 table 0x100 exit. Exact-image hook, not a missing
   implementation. */

void f33_mode_hook_b1da0(void)

{
  return;
}



/* Apply per-channel output-owner bundle for transition0200\u21920201;
   onlychannelswithclearB082bitarechanged.
   Channel1masksshift16except50C82Boolean;shared5693Eowner0writtenlast. Exactbundle inphase_table.
   Directenable: 0. Apply per-channel output-owner bundle for transition0200→0201; */

void f33_apply_mode0201_entry_requests(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if ((DAT_febeb082 & 1) == 0) {
    puVar1 = 0xfebeb800u;
    f33_set_output_request_word((byte)DAT_febeb082 & 1,0x7001);
    f33_clear_direct_output_bank0();
    f33_set_channel_owner_request('\0',2);
    thunk_FUN_00056c26(0,4);
    thunk_FUN_00056e66(0,2);
    thunk_FUN_00056f14(0,4);
    thunk_FUN_000569ac(0,0);
    thunk_FUN_000568dc(0,0x20);
    thunk_FUN_00050c82(0,0);
    thunk_FUN_00056cda(0,0xc);
  }
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x77e))))) & 2) == 0) {
    f33_set_output_request_word('\x01',0x70010000);
    f33_clear_direct_output_bank1();
    f33_set_channel_owner_request('\x01',0x20000);
    thunk_FUN_00056c26(1,0x40000);
    thunk_FUN_00056e66(1,0x20000);
    thunk_FUN_00056f14(1,0x40000);
    thunk_FUN_000569ac(1,0);
    thunk_FUN_000568dc(1,0x200000);
    thunk_FUN_00050c82(1,0);
    thunk_FUN_00056cda(1,0xc0000);
  }
  thunk_FUN_0005693e(0,3);
  return;
}



/* Apply per-channel output-owner bundle for transition0201\u21920202;
   onlychannelswithclearB082bitarechanged.
   Channel1masksshift16except50C82Boolean;shared5693Eowner0writtenlast. Exactbundle inphase_table.
   Directenable: 0. Apply per-channel output-owner bundle for transition0201→0202; */

void f33_apply_mode0202_entry_requests(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if ((DAT_febeb082 & 1) == 0) {
    puVar1 = 0xfebeb800u;
    f33_set_output_request_word((byte)DAT_febeb082 & 1,0x7001);
    f33_clear_direct_output_bank0();
    f33_set_channel_owner_request('\0',2);
    thunk_FUN_00056c26(0,4);
    thunk_FUN_00056e66(0,2);
    thunk_FUN_00056f14(0,4);
    thunk_FUN_000569ac(0,0);
    thunk_FUN_000568dc(0,2);
    thunk_FUN_00050c82(0,0);
    thunk_FUN_00056cda(0,0xc);
  }
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x77e))))) & 2) == 0) {
    f33_set_output_request_word('\x01',0x70010000);
    f33_clear_direct_output_bank1();
    f33_set_channel_owner_request('\x01',0x20000);
    thunk_FUN_00056c26(1,0x40000);
    thunk_FUN_00056e66(1,0x20000);
    thunk_FUN_00056f14(1,0x40000);
    thunk_FUN_000569ac(1,0);
    thunk_FUN_000568dc(1,0x20000);
    thunk_FUN_00050c82(1,0);
    thunk_FUN_00056cda(1,0xc0000);
  }
  thunk_FUN_0005693e(0,0);
  return;
}



/* Apply per-channel output-owner bundle for transition0202\u21920203;
   onlychannelswithclearB082bitarechanged.
   Channel1masksshift16except50C82Boolean;shared5693Eowner0writtenlast. Exactbundle inphase_table.
   Directenable: 0. Apply per-channel output-owner bundle for transition0202→0203; */

void f33_apply_mode0203_entry_requests(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if ((DAT_febeb082 & 1) == 0) {
    puVar1 = 0xfebeb800u;
    f33_set_output_request_word((byte)DAT_febeb082 & 1,0x7001);
    f33_clear_direct_output_bank0();
    f33_set_channel_owner_request('\0',2);
    thunk_FUN_00056c26(0,4);
    thunk_FUN_00056e66(0,2);
    thunk_FUN_00056f14(0,4);
    thunk_FUN_000569ac(0,0);
    thunk_FUN_000568dc(0,2);
    thunk_FUN_00050c82(0,1);
    thunk_FUN_00056cda(0,0xc);
  }
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x77e))))) & 2) == 0) {
    f33_set_output_request_word('\x01',0x70010000);
    f33_clear_direct_output_bank1();
    f33_set_channel_owner_request('\x01',0x20000);
    thunk_FUN_00056c26(1,0x40000);
    thunk_FUN_00056e66(1,0x20000);
    thunk_FUN_00056f14(1,0x40000);
    thunk_FUN_000569ac(1,0);
    thunk_FUN_000568dc(1,0x20000);
    thunk_FUN_00050c82(1,1);
    thunk_FUN_00056cda(1,0xc0000);
  }
  thunk_FUN_0005693e(0,0);
  return;
}



/* Apply per-channel output-owner bundle for transition0203\u21920204;
   onlychannelswithclearB082bitarechanged.
   Channel1masksshift16except50C82Boolean;shared5693Eowner0writtenlast. Exactbundle inphase_table.
   Directenable: 5A with AF3DE triplet. Apply per-channel output-owner bundle for
   transition0203→0204; */

void f33_apply_mode0204_entry_requests(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if ((DAT_febeb082 & 1) == 0) {
    puVar1 = 0xfebeb800u;
    f33_set_output_request_word((uchar)(DAT_febeb082 & 1),DAT_febeb082 & 1);
    f33_set_direct_output_codes_bank0((ushort *)((undefined *)camry_host_ptr(0xaf3deu)));
    f33_request_direct_output_bank0();
    f33_set_channel_owner_request('\0',2);
    thunk_FUN_00056c26(0,4);
    thunk_FUN_00056e66(0,2);
    thunk_FUN_00056f14(0,4);
    thunk_FUN_000569ac(0,0);
    thunk_FUN_000568dc(0,2);
    thunk_FUN_00050c82(0,1);
    thunk_FUN_00056cda(0,0xc);
  }
  if (((*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x77e)))) & 2) == 0) {
    f33_set_output_request_word('\x01',(*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x77e)))) & 2);
    f33_set_direct_output_codes_bank1((ushort *)((undefined *)camry_host_ptr(0xaf3deu)));
    f33_request_direct_output_bank1();
    f33_set_channel_owner_request('\x01',0x20000);
    thunk_FUN_00056c26(1,0x40000);
    thunk_FUN_00056e66(1,0x20000);
    thunk_FUN_00056f14(1,0x40000);
    thunk_FUN_000569ac(1,0);
    thunk_FUN_000568dc(1,0x20000);
    thunk_FUN_00050c82(1,1);
    thunk_FUN_00056cda(1,0xc0000);
  }
  thunk_FUN_0005693e(0,0);
  return;
}



/* Apply per-channel output-owner bundle for transition0204\u21920205;
   onlychannelswithclearB082bitarechanged.
   Channel1masksshift16except50C82Boolean;shared5693Eowner0writtenlast. Exactbundle inphase_table.
   Directenable: 0. Apply per-channel output-owner bundle for transition0204→0205; */

void f33_apply_mode0205_entry_requests(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if ((DAT_febeb082 & 1) == 0) {
    puVar1 = 0xfebeb800u;
    f33_set_output_request_word((byte)DAT_febeb082 & 1,0x7001);
    f33_clear_direct_output_bank0();
    f33_set_channel_owner_request('\0',2);
    thunk_FUN_00056c26(0,4);
    thunk_FUN_00056e66(0,2);
    thunk_FUN_00056f14(0,4);
    thunk_FUN_000569ac(0,0);
    thunk_FUN_000568dc(0,2);
    thunk_FUN_00050c82(0,1);
    thunk_FUN_00056cda(0,0xc);
  }
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x77e))))) & 2) == 0) {
    f33_set_output_request_word('\x01',0x70010000);
    f33_clear_direct_output_bank1();
    f33_set_channel_owner_request('\x01',0x20000);
    thunk_FUN_00056c26(1,0x40000);
    thunk_FUN_00056e66(1,0x20000);
    thunk_FUN_00056f14(1,0x40000);
    thunk_FUN_000569ac(1,0);
    thunk_FUN_000568dc(1,0x20000);
    thunk_FUN_00050c82(1,1);
    thunk_FUN_00056cda(1,0xc0000);
  }
  thunk_FUN_0005693e(0,0);
  return;
}



/* Apply per-channel output-owner bundle for transition0205\u21920206;
   onlychannelswithclearB082bitarechanged.
   Channel1masksshift16except50C82Boolean;shared5693Eowner0writtenlast. Exactbundle inphase_table.
   Directenable: 0. Apply per-channel output-owner bundle for transition0205→0206; */

void f33_apply_mode0206_entry_requests(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if ((DAT_febeb082 & 1) == 0) {
    puVar1 = 0xfebeb800u;
    f33_set_output_request_word((byte)DAT_febeb082 & 1,0x7001);
    f33_clear_direct_output_bank0();
    f33_set_channel_owner_request('\0',2);
    thunk_FUN_00056c26(0,4);
    thunk_FUN_00056e66(0,2);
    thunk_FUN_00056f14(0,4);
    thunk_FUN_000569ac(0,0);
    thunk_FUN_000568dc(0,2);
    thunk_FUN_00050c82(0,1);
    thunk_FUN_00056cda(0,0xc);
  }
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x77e))))) & 2) == 0) {
    f33_set_output_request_word('\x01',0x70010000);
    f33_clear_direct_output_bank1();
    f33_set_channel_owner_request('\x01',0x20000);
    thunk_FUN_00056c26(1,0x40000);
    thunk_FUN_00056e66(1,0x20000);
    thunk_FUN_00056f14(1,0x40000);
    thunk_FUN_000569ac(1,0);
    thunk_FUN_000568dc(1,0x20000);
    thunk_FUN_00050c82(1,1);
    thunk_FUN_00056cda(1,0xc0000);
  }
  thunk_FUN_0005693e(0,0);
  return;
}



/* Apply per-channel output-owner bundle for transition0206\u21920207;
   onlychannelswithclearB082bitarechanged.
   Channel1masksshift16except50C82Boolean;shared5693Eowner0writtenlast. Exactbundle inphase_table.
   Directenable: 0. Apply per-channel output-owner bundle for transition0206→0207; */

void f33_apply_mode0207_entry_requests(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if ((DAT_febeb082 & 1) == 0) {
    puVar1 = 0xfebeb800u;
    f33_set_output_request_word((byte)DAT_febeb082 & 1,0x7001);
    f33_clear_direct_output_bank0();
    f33_set_channel_owner_request('\0',2);
    thunk_FUN_00056c26(0,4);
    thunk_FUN_00056e66(0,0);
    thunk_FUN_00056f14(0,0);
    thunk_FUN_000569ac(0,0);
    thunk_FUN_000568dc(0,2);
    thunk_FUN_00050c82(0,0);
    thunk_FUN_00056cda(0,0xc);
  }
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x77e))))) & 2) == 0) {
    f33_set_output_request_word('\x01',0x70010000);
    f33_clear_direct_output_bank1();
    f33_set_channel_owner_request('\x01',0x20000);
    thunk_FUN_00056c26(1,0x40000);
    thunk_FUN_00056e66(1,0);
    thunk_FUN_00056f14(1,0);
    thunk_FUN_000569ac(1,0);
    thunk_FUN_000568dc(1,0x20000);
    thunk_FUN_00050c82(1,0);
    thunk_FUN_00056cda(1,0xc0000);
  }
  thunk_FUN_0005693e(0,0);
  return;
}



/* Apply per-channel output-owner bundle for transition0207\u21920208;
   onlychannelswithclearB082bitarechanged.
   Channel1masksshift16except50C82Boolean;shared5693Eowner0writtenlast. Exactbundle inphase_table.
   Directenable: 0. Apply per-channel output-owner bundle for transition0207→0208; */

void f33_apply_mode0208_entry_requests(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if ((DAT_febeb082 & 1) == 0) {
    puVar1 = 0xfebeb800u;
    f33_set_output_request_word((byte)DAT_febeb082 & 1,0x7001);
    f33_clear_direct_output_bank0();
    f33_set_channel_owner_request('\0',0);
    thunk_FUN_00056c26(0,0);
    thunk_FUN_00056e66(0,0);
    thunk_FUN_00056f14(0,2);
    thunk_FUN_000569ac(0,2);
    thunk_FUN_000568dc(0,2);
    thunk_FUN_00050c82(0,0);
    thunk_FUN_00056cda(0,0xc);
  }
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x77e))))) & 2) == 0) {
    f33_set_output_request_word('\x01',0x70010000);
    f33_clear_direct_output_bank1();
    f33_set_channel_owner_request('\x01',0);
    thunk_FUN_00056c26(1,0);
    thunk_FUN_00056e66(1,0);
    thunk_FUN_00056f14(1,0x20000);
    thunk_FUN_000569ac(1,0x20000);
    thunk_FUN_000568dc(1,0x20000);
    thunk_FUN_00050c82(1,0);
    thunk_FUN_00056cda(1,0xc0000);
  }
  thunk_FUN_0005693e(0,0);
  return;
}



/* Apply per-channel output-owner bundle for transition0208\u21920209;
   onlychannelswithclearB082bitarechanged.
   Channel1masksshift16except50C82Boolean;shared5693Eowner0writtenlast. Exactbundle inphase_table.
   Directenable: 0. Apply per-channel output-owner bundle for transition0208→0209; */

void f33_apply_mode0209_entry_requests(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if ((DAT_febeb082 & 1) == 0) {
    puVar1 = 0xfebeb800u;
    f33_set_output_request_word((byte)DAT_febeb082 & 1,0x7001);
    f33_clear_direct_output_bank0();
    f33_set_channel_owner_request('\0',0);
    thunk_FUN_00056c26(0,2);
    thunk_FUN_00056e66(0,2);
    thunk_FUN_00056f14(0,4);
    thunk_FUN_000569ac(0,2);
    thunk_FUN_000568dc(0,2);
    thunk_FUN_00050c82(0,0);
    thunk_FUN_00056cda(0,0xc);
  }
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x77e))))) & 2) == 0) {
    f33_set_output_request_word('\x01',0x70010000);
    f33_clear_direct_output_bank1();
    f33_set_channel_owner_request('\x01',0);
    thunk_FUN_00056c26(1,0x20000);
    thunk_FUN_00056e66(1,0x20000);
    thunk_FUN_00056f14(1,0x40000);
    thunk_FUN_000569ac(1,0x20000);
    thunk_FUN_000568dc(1,0x20000);
    thunk_FUN_00050c82(1,0);
    thunk_FUN_00056cda(1,0xc0000);
  }
  thunk_FUN_0005693e(0,0);
  return;
}



/* Apply per-channel output-owner bundle for transition0209\u2192020A;
   onlychannelswithclearB082bitarechanged.
   Channel1masksshift16except50C82Boolean;shared5693Eowner0writtenlast. Exactbundle inphase_table.
   Directenable: 0. Apply per-channel output-owner bundle for transition0209→020A; */

void f33_apply_mode020a_entry_requests(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if ((DAT_febeb082 & 1) == 0) {
    puVar1 = 0xfebeb800u;
    f33_set_output_request_word((byte)DAT_febeb082 & 1,0x7001);
    f33_clear_direct_output_bank0();
    f33_set_channel_owner_request('\0',0);
    thunk_FUN_00056c26(0,0);
    thunk_FUN_00056e66(0,0);
    thunk_FUN_00056f14(0,4);
    thunk_FUN_000569ac(0,0);
    thunk_FUN_000568dc(0,2);
    thunk_FUN_00050c82(0,0);
    thunk_FUN_00056cda(0,0xc);
  }
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x77e))))) & 2) == 0) {
    f33_set_output_request_word('\x01',0x70010000);
    f33_clear_direct_output_bank1();
    f33_set_channel_owner_request('\x01',0);
    thunk_FUN_00056c26(1,0);
    thunk_FUN_00056e66(1,0);
    thunk_FUN_00056f14(1,0x40000);
    thunk_FUN_000569ac(1,0);
    thunk_FUN_000568dc(1,0x20000);
    thunk_FUN_00050c82(1,0);
    thunk_FUN_00056cda(1,0xc0000);
  }
  thunk_FUN_0005693e(0,3);
  return;
}



/* Apply per-channel output-owner bundle for transition020A\u2192020B;
   onlychannelswithclearB082bitarechanged.
   Channel1masksshift16except50C82Boolean;shared5693Eowner0writtenlast. Exactbundle inphase_table.
   Directenable: 0. Apply per-channel output-owner bundle for transition020A→020B; */

void f33_apply_mode020b_entry_requests(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if ((DAT_febeb082 & 1) == 0) {
    puVar1 = 0xfebeb800u;
    f33_set_output_request_word((byte)DAT_febeb082 & 1,0x7001);
    f33_clear_direct_output_bank0();
    f33_set_channel_owner_request('\0',0);
    thunk_FUN_00056c26(0,4);
    thunk_FUN_00056e66(0,0);
    thunk_FUN_00056f14(0,4);
    thunk_FUN_000569ac(0,0);
    thunk_FUN_000568dc(0,2);
    thunk_FUN_00050c82(0,0);
    thunk_FUN_00056cda(0,2);
  }
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x77e))))) & 2) == 0) {
    f33_set_output_request_word('\x01',0x70010000);
    f33_clear_direct_output_bank1();
    f33_set_channel_owner_request('\x01',0);
    thunk_FUN_00056c26(1,0x40000);
    thunk_FUN_00056e66(1,0);
    thunk_FUN_00056f14(1,0x40000);
    thunk_FUN_000569ac(1,0);
    thunk_FUN_000568dc(1,0x20000);
    thunk_FUN_00050c82(1,0);
    thunk_FUN_00056cda(1,0x20000);
  }
  thunk_FUN_0005693e(0,3);
  return;
}



/* Apply per-channel output-owner bundle for transition020B\u2192020C;
   onlychannelswithclearB082bitarechanged.
   Channel1masksshift16except50C82Boolean;shared5693Eowner0writtenlast. Exactbundle inphase_table.
   Directenable: 5A with AF3DE triplet. Apply per-channel output-owner bundle for
   transition020B→020C; */

void f33_apply_mode020c_entry_requests(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if ((DAT_febeb082 & 1) == 0) {
    puVar1 = 0xfebeb800u;
    f33_set_output_request_word((byte)DAT_febeb082 & 1,1);
    f33_set_direct_output_codes_bank0((ushort *)((undefined *)camry_host_ptr(0xaf3deu)));
    f33_request_direct_output_bank0();
    f33_set_channel_owner_request('\0',0);
    thunk_FUN_00056c26(0,4);
    thunk_FUN_00056e66(0,0);
    thunk_FUN_00056f14(0,4);
    thunk_FUN_000569ac(0,0);
    thunk_FUN_000568dc(0,2);
    thunk_FUN_00050c82(0,0);
    thunk_FUN_00056cda(0,2);
  }
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x77e))))) & 2) == 0) {
    f33_set_output_request_word('\x01',0x10000);
    f33_set_direct_output_codes_bank1((ushort *)((undefined *)camry_host_ptr(0xaf3deu)));
    f33_request_direct_output_bank1();
    f33_set_channel_owner_request('\x01',0);
    thunk_FUN_00056c26(1,0x40000);
    thunk_FUN_00056e66(1,0);
    thunk_FUN_00056f14(1,0x40000);
    thunk_FUN_000569ac(1,0);
    thunk_FUN_000568dc(1,0x20000);
    thunk_FUN_00050c82(1,0);
    thunk_FUN_00056cda(1,0x20000);
  }
  thunk_FUN_0005693e(0,3);
  return;
}



/* Apply per-channel output-owner bundle for transition020C\u2192020D;
   onlychannelswithclearB082bitarechanged.
   Channel1masksshift16except50C82Boolean;shared5693Eowner0writtenlast. Exactbundle inphase_table.
   Directenable: 5A with AF3E4 triplet. Apply per-channel output-owner bundle for
   transition020C→020D; */

void f33_apply_mode020d_entry_requests(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if ((DAT_febeb082 & 1) == 0) {
    puVar1 = 0xfebeb800u;
    f33_set_output_request_word((byte)DAT_febeb082 & 1,1);
    f33_set_direct_output_codes_bank0((ushort *)((undefined *)camry_host_ptr(0xaf3e4u)));
    f33_request_direct_output_bank0();
    f33_set_channel_owner_request('\0',0);
    thunk_FUN_00056c26(0,4);
    thunk_FUN_00056e66(0,0);
    thunk_FUN_00056f14(0,4);
    thunk_FUN_000569ac(0,0);
    thunk_FUN_000568dc(0,2);
    thunk_FUN_00050c82(0,0);
    thunk_FUN_00056cda(0,2);
  }
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x77e))))) & 2) == 0) {
    f33_set_output_request_word('\x01',0x10000);
    f33_set_direct_output_codes_bank1((ushort *)((undefined *)camry_host_ptr(0xaf3e4u)));
    f33_request_direct_output_bank1();
    f33_set_channel_owner_request('\x01',0);
    thunk_FUN_00056c26(1,0x40000);
    thunk_FUN_00056e66(1,0);
    thunk_FUN_00056f14(1,0x40000);
    thunk_FUN_000569ac(1,0);
    thunk_FUN_000568dc(1,0x20000);
    thunk_FUN_00050c82(1,0);
    thunk_FUN_00056cda(1,0x20000);
  }
  thunk_FUN_0005693e(0,3);
  return;
}



/* Clear direct-enable bytes8B4C/8B4D, setB10F throughB32E0; when returnedselector!=1 request6, then
   alwaysrequest3.0200 takes3\u21920300 first; retained6 may subsequentlyjoin0500 unless
   higher-priorityrequests win. when returnedselector!=1 request6, then alwaysrequest3.0200
   takes3→0300 first; */

undefined4 f33_complete_mode200_output_sequence(void)

{
  uint uVar1;
  
  f33_clear_direct_output_enables();
  uVar1 = f33_select_service_join_after_mode200();
  if (uVar1 != 1) {
    FUN_000b15ac(6);
  }
  return FUN_000b15ac(3);
}



/* Advance exactly one0200..020D stage using matching IDs21..34. Each admitted channel gets
   stage-specific owner masks; disabled B082 channels retain. Direct-output stages0203/020B/020C
   load triplets then enable5A. Terminal020D requests3 plus6 only ifB32E0 selector!=1, clears direct
   enables; major arbiter runs afterward. */

void f33_advance_mode200_output_sequence(void)

{
  uchar request_id;
  uint uVar1;
  
  switch(DAT_febeb11a) {
  case 0x200:
    uVar1 = f33_probe_pending_mode_request('\x15');
    if (uVar1 == 1) {
      f33_apply_mode0201_entry_requests();
      f33_publish_live_application_mode(0x201);
    }
    request_id = '\x15';
    break;
  case 0x201:
    uVar1 = f33_probe_pending_mode_request('\x16');
    if (uVar1 == 1) {
      f33_apply_mode0202_entry_requests();
      f33_publish_live_application_mode(0x202);
    }
    request_id = '\x16';
    break;
  case 0x202:
    uVar1 = f33_probe_pending_mode_request('\x17');
    if (uVar1 == 1) {
      f33_apply_mode0203_entry_requests();
      f33_publish_live_application_mode(0x203);
    }
    request_id = '\x17';
    break;
  case 0x203:
    uVar1 = f33_probe_pending_mode_request('\x18');
    if (uVar1 == 1) {
      f33_apply_mode0204_entry_requests();
      f33_publish_live_application_mode(0x204);
    }
    request_id = '\x18';
    break;
  case 0x204:
    uVar1 = f33_probe_pending_mode_request('\x19');
    if (uVar1 == 1) {
      f33_apply_mode0205_entry_requests();
      f33_publish_live_application_mode(0x205);
    }
    request_id = '\x19';
    break;
  case 0x205:
    uVar1 = f33_probe_pending_mode_request('\x1a');
    if (uVar1 == 1) {
      f33_apply_mode0206_entry_requests();
      f33_publish_live_application_mode(0x206);
    }
    request_id = '\x1a';
    break;
  case 0x206:
    uVar1 = f33_probe_pending_mode_request('\x1b');
    if (uVar1 == 1) {
      f33_apply_mode0207_entry_requests();
      f33_publish_live_application_mode(0x207);
    }
    request_id = '\x1b';
    break;
  case 0x207:
    uVar1 = f33_probe_pending_mode_request('\x1c');
    if (uVar1 == 1) {
      f33_apply_mode0208_entry_requests();
      f33_publish_live_application_mode(0x208);
    }
    request_id = '\x1c';
    break;
  case 0x208:
    uVar1 = f33_probe_pending_mode_request('\x1d');
    if (uVar1 == 1) {
      f33_apply_mode0209_entry_requests();
      f33_publish_live_application_mode(0x209);
    }
    request_id = '\x1d';
    break;
  case 0x209:
    uVar1 = f33_probe_pending_mode_request('\x1e');
    if (uVar1 == 1) {
      f33_apply_mode020a_entry_requests();
      f33_publish_live_application_mode(0x20a);
    }
    request_id = '\x1e';
    break;
  case 0x20a:
    uVar1 = f33_probe_pending_mode_request('\x1f');
    if (uVar1 == 1) {
      f33_apply_mode020b_entry_requests();
      f33_publish_live_application_mode(0x20b);
    }
    request_id = '\x1f';
    break;
  case 0x20b:
    uVar1 = f33_probe_pending_mode_request(' ');
    if (uVar1 == 1) {
      f33_apply_mode020c_entry_requests();
      f33_publish_live_application_mode(0x20c);
    }
    request_id = ' ';
    break;
  case 0x20c:
    uVar1 = f33_probe_pending_mode_request('!');
    if (uVar1 == 1) {
      f33_apply_mode020d_entry_requests();
      f33_publish_live_application_mode(0x20d);
    }
    request_id = '!';
    break;
  case 0x20d:
    uVar1 = f33_probe_pending_mode_request('\"');
    if (uVar1 == 1) {
      f33_complete_mode200_output_sequence();
    }
    request_id = '\"';
    break;
  default:
    goto switchD_000b2830_default;
  }
  f33_acknowledge_selected_mode_request(request_id);
switchD_000b2830_default:
  return;
}



void FUN_000b29fa(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if ((DAT_febeb082 & 1) == 0) {
    puVar1 = 0xfebeb800u;
    f33_set_output_request_word((byte)DAT_febeb082 & 1,0x7001);
    f33_clear_direct_output_bank0();
    f33_set_channel_owner_request('\0',2);
    thunk_FUN_00056c26(0,4);
    thunk_FUN_00056e66(0,2);
    thunk_FUN_00056f14(0,4);
    thunk_FUN_000569ac(0,0);
    thunk_FUN_000568dc(0,2);
    thunk_FUN_00050c82(0,0);
    thunk_FUN_00056cda(0,0xc);
  }
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x77e))))) & 2) == 0) {
    f33_set_output_request_word('\x01',0x70010000);
    f33_clear_direct_output_bank1();
    f33_set_channel_owner_request('\x01',0x20000);
    thunk_FUN_00056c26(1,0x40000);
    thunk_FUN_00056e66(1,0x20000);
    thunk_FUN_00056f14(1,0x40000);
    thunk_FUN_000569ac(1,0);
    thunk_FUN_000568dc(1,0x20000);
    thunk_FUN_00050c82(1,0);
    thunk_FUN_00056cda(1,0xc0000);
  }
  thunk_FUN_0005693e(0,0);
  return;
}



/* Far-call trampoline: prepare {lp},0 / jarl 0xB29FA / dispose 0,{lp},lp; byte-verified against the
   exact image. Forwards with registers and stack unchanged; marked as a thunk. Forwarding shape
   machine-verified; target semantics not recovered. */

void thunk_FUN_000b29fa(void)

{
  FUN_000b29fa();
  return;
}



/* Sequential initializer chain: 6 unconditional calls and no other statements; shape-verified. The
   called sequence is the function's entire behavior; chain family members differ in callee sets. */

void f33_run_init_chain_b2ace(void)

{
  f33_set_output_request_word('\0',0x7001);
  f33_set_output_request_word('\x01',0x70010000);
  f33_clear_direct_output_enables();
  thunk_FUN_0005693e(0,3);
  thunk_FUN_000568dc(0,2);
  thunk_FUN_000568dc(1,0x20000);
  return;
}



undefined4 FUN_000b2b0a(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  f33_set_output_request_word('\0',0x70017001);
  f33_set_output_request_word('\x01',0x70017001);
  f33_set_channel_owner_request('\0',0);
  f33_set_channel_owner_request('\x01',0);
  thunk_FUN_00056e66(0,0);
  thunk_FUN_00056e66(1,0);
  if (((*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x77e)))) & 1) == 0) {
    thunk_FUN_00056cda((*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x77e)))) & 1,2);
  }
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x77e))))) & 2) == 0) {
    thunk_FUN_00056cda(1,0x20000);
  }
  return FUN_000bd8ea();
}



/* If retainedB10D<5 increment; otherwise request36/0x24 andretaincounter. The invocationentering5
   doesnotrequest; no measuredtimeclaim. */

void f33_step_mode301_invocation_counter(void)

{
  uint32_t puVar1;
  byte bVar2;
  
  bVar2 = DAT_febeb10d;
  puVar1 = 0xfebeb800u;
  if (DAT_febeb10d < 5) {
    bVar2 = DAT_febeb10d + 1;
  }
  else {
    puVar1 = 0xfebeb800u;
    FUN_000b15ac(0x24);
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6f3))))) = bVar2;
  return;
}



undefined4 FUN_000b2b90(void)

{
  return FUN_000b15ac(0xc);
}



/* 0300 matchingevent35/0x23 appliesB2B0A output/record actions then commits0301.0301 increments
   retainedB10D to5, then requests36/0x24; accepting36 requestsmajor12\u21920400 without
   changing0301. Counter is not reset on0300 entry/exit. accepting36 requestsmajor12→0400 without
   changing0301. */

void f33_advance_mode300_substate(void)

{
  uchar request_id;
  uint uVar1;
  
  if (DAT_febeb11a == 0x300) {
    uVar1 = f33_probe_pending_mode_request('#');
    if (uVar1 == 1) {
      FUN_000b2b0a();
      f33_publish_live_application_mode(0x301);
    }
    request_id = '#';
  }
  else {
    if (DAT_febeb11a != 0x301) {
      return;
    }
    f33_step_mode301_invocation_counter();
    uVar1 = f33_probe_pending_mode_request('$');
    if (uVar1 == 1) {
      FUN_000b2b90();
    }
    request_id = '$';
  }
  f33_acknowledge_selected_mode_request(request_id);
  return;
}



/* JMP LP with no state change; AEB00 table 0x300 entry. Exact-image hook, not a missing
   implementation. */

void f33_mode_hook_b2bf4(void)

{
  return;
}



/* JMP LP with no state change; AEB00 table 0x300 exit. Exact-image hook, not a missing
   implementation. */

void f33_mode_hook_b2bf6(void)

{
  return;
}



/* Clear owners0/1 of8B2C/8A9C/8AE8/8A50/8A2C/8260, conditionally write8AA8=2/20000
   forclearB082channelbits. Doesnotclear8A70/8AD0; top-level573FE separatelyclearsdirectenables. */

void f33_apply_mode400_output_requests(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  f33_set_output_request_word('\0',0);
  f33_set_output_request_word('\x01',0);
  thunk_FUN_00056c26(0,0);
  thunk_FUN_00056c26(1,0);
  thunk_FUN_00056f14(0,0);
  thunk_FUN_00056f14(1,0);
  thunk_FUN_000569ac(0,0);
  thunk_FUN_000569ac(1,0);
  thunk_FUN_000568dc(0,0);
  thunk_FUN_000568dc(1,0);
  thunk_FUN_00050c82(0,0);
  thunk_FUN_00050c82(1,0);
  if (((*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x77e)))) & 1) == 0) {
    thunk_FUN_00056cda((*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x77e)))) & 1,2);
  }
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x77e))))) & 2) == 0) {
    thunk_FUN_00056cda(1,0x20000);
  }
  return;
}



/* Finalize diagnosticlog45CFC, clear8B2Cowners0/1, setclassifier82A9=5A. Oldlive mode
   remainsvisible until callercommitsnewmode. */

void f33_enter_mode400(void)

{
  thunk_FUN_00045cfc();
  f33_set_output_request_word('\0',0);
  f33_set_output_request_word('\x01',0);
  thunk_FUN_000515ca();
  return;
}



/* JMP LP with no state change; AEB00 table 0x400 exit. Exact-image hook, not a missing
   implementation. */

void f33_mode_hook_b2ca2(void)

{
  return;
}



void FUN_000b2ca6(void)

{
  thunk_FUN_00056b78(2,2);
  thunk_FUN_00056b78(3,0x20000);
  return;
}



/* Compose record5, record6 and gated estimator record8 publications. Called by B2CFE on
   mode0701/event27 before B1620(0702), not itself an AEB00 family hook. Separate
   admission/queues/trackers, not an atomic or durable snapshot. Mode0701/event27 helper composes
   independent record5/6 and gated estimator8 publications. Native scenarios distinguish real queue
   admission from tracker arming; record8 explicitly disabled. */

undefined4 f33_snapshot_retained_control_records(void)

{
  f33_publish_thermal_reference_record();
  f33_publish_thermal_history_record();
  return FUN_000bd87e();
}



undefined4 FUN_000b2cd6(void)

{
  return FUN_000b15ac(10);
}



/* Return0 onlyfor exactlive0701, otherwise5A including0700/0702. Thisispost-submode
   readinessbranchselector, not an independentlyqualified hardware readiness. */

uint f33_get_mode700_progress_marker(void)

{
  if ((DAT_febeb11a != 0x702) && (DAT_febeb11a == 0x701)) {
    return 0;
  }
  return 0x5a;
}



/* Advance atmostone0700\u21920701(event38/0x26),0701\u21920702(39/0x27 retainedrecordsnapshot),
   or0702 event40/0x28 requestsmajor10. ReturnB2CE4 r10:0onlywhilepost-worker live0701;5Aotherwise.
   ParentB1808 usesreturnfor event2 restartbranch. Advance
   atmostone0700→0701(event38/0x26),0701→0702(39/0x27 retainedrecordsnapshot), or0702
   event40/0x28 requestsmajor10. */

uint f33_advance_mode700_substate(void)

{
  uchar request_id;
  uint uVar1;
  
  if (0x6ff < DAT_febeb11a) {
    if (DAT_febeb11a == 0x700) {
      uVar1 = f33_probe_pending_mode_request('&');
      if (uVar1 == 1) {
        FUN_000b2ca6();
        f33_publish_live_application_mode(0x701);
      }
      request_id = '&';
    }
    else if (DAT_febeb11a < 0x702) {
      uVar1 = f33_probe_pending_mode_request('\'');
      if (uVar1 == 1) {
        f33_snapshot_retained_control_records();
        f33_publish_live_application_mode(0x702);
      }
      request_id = '\'';
    }
    else {
      if (DAT_febeb11a != 0x702) goto LAB_000b2d6c;
      uVar1 = f33_probe_pending_mode_request('(');
      if (uVar1 == 1) {
        FUN_000b2cd6();
      }
      request_id = '(';
    }
    f33_acknowledge_selected_mode_request(request_id);
  }
LAB_000b2d6c:
  uVar1 = f33_get_mode700_progress_marker();
  return uVar1;
}



/* Request39/0x27 unless selectedID/complementisvalidandID1. Calledin0700entrywhileoldlive mode
   remains; health-selected1 delaysretainedsnapshotrequest for laterthermalproducer. */

void f33_request_mode701_snapshot_unless_health_selected(void)

{
  char cVar1;
  int iVar2;
  
  cVar1 = DAT_febeb10c;
  iVar2 = FUN_000b1c40();
  if ((iVar2 != 1) || (cVar1 != '\x01')) {
    FUN_000b15ac(0x27);
  }
  return;
}



/* Request38/0x26 andfinalize diagnosticlog45CFC. Doesnotmaterializeslotdirectly;
   reconciliationlaterruns. */

void f33_request_mode700_initial_step(void)

{
  FUN_000b15ac(0x26);
  thunk_FUN_00045cfc();
  return;
}



/* Reportserviceaborts;publishretained thermal/records8,9,D and
   conditionalrecords18/105;mark5F84.bit1
   andqualified89D2[].bit1;setB250=5A;request38andconditionally39;finalizelog.
   Set8A48owner0=3,8B2Cowners0/1=70017001, clear8AD0/8AE8/8A50/8A2C/8260owners0/1,8AA8=4/40000.
   Doesnotclear8A70owners. */

void f33_enter_mode700(void)

{
  f33_report_pending_service_aborts();
  f33_publish_thermal_reference_record();
  f33_publish_thermal_history_record();
  FUN_000bd87e();
  FUN_000bd8ea();
  f33_stage_received_word_age_record13();
  thunk_FUN_00052a10();
  thunk_FUN_000562fa();
  f33_consume_ba_retained_admission_count();
  FUN_000b5eb0();
  f33_request_mode701_snapshot_unless_health_selected();
  f33_request_mode700_initial_step();
  thunk_FUN_0005693e(0,3);
  f33_set_output_request_word('\0',0x70017001);
  f33_set_output_request_word('\x01',0x70017001);
  thunk_FUN_00056e66(0,0);
  thunk_FUN_00056e66(1,0);
  thunk_FUN_00056f14(0,0);
  thunk_FUN_00056f14(1,0);
  thunk_FUN_000569ac(0,0);
  thunk_FUN_000569ac(1,0);
  thunk_FUN_000568dc(0,0);
  thunk_FUN_000568dc(1,0);
  thunk_FUN_00050c82(0,0);
  thunk_FUN_00050c82(1,0);
  thunk_FUN_00056cda(0,4);
  thunk_FUN_00056cda(1,0x40000);
  return;
}



/* JMP LP with no state change; AEB00 table 0x700 exit. Exact-image hook, not a missing
   implementation. */

void f33_mode_hook_b2e62(void)

{
  return;
}



/* Onlyif66F1E==1replace8A70owners0/1=20002,8A9C=4/40000,8AD0/8AE8=0,8AA8=4/40000,8A88owners2/3=2/20000.
   NvMbusy leavesmaskstateunchanged; top-leveldirectenableclearstilloccurs. */

uint f33_apply_mode800_ready_output_requests(void)

{
  uint uVar1;
  
  uVar1 = f33_query_application_nvm_readiness();
  if (uVar1 == 1) {
    f33_set_channel_owner_request('\0',0x20002);
    f33_set_channel_owner_request('\x01',0x20002);
    thunk_FUN_00056c26(0,4);
    thunk_FUN_00056c26(1,0x40000);
    thunk_FUN_00056e66(0,0);
    thunk_FUN_00056e66(1,0);
    thunk_FUN_00056f14(0,0);
    thunk_FUN_00056f14(1,0);
    thunk_FUN_00056cda(0,4);
    thunk_FUN_00056cda(1,0x40000);
    thunk_FUN_00056b78(2,2);
    thunk_FUN_00056b78(3,0x20000);
  }
  return uVar1;
}



/* JMP LP with no state change; AEB00 table 0x800 entry. Exact-image hook, not a missing
   implementation. */

void f33_mode_hook_b2ee2(void)

{
  return;
}



/* JMP LP with no state change; AEB00 table 0x800 exit. Exact-image hook, not a missing
   implementation. */

void f33_mode_hook_b2ee4(void)

{
  return;
}



void FUN_000b2ee6(void)

{
  undefined4 uVar1;
  
  if (((DAT_febeb10e & 1) == 0) || (DAT_febef176 != 0)) {
    if (((DAT_febeb10e >> 1 & 1) == 0) || ((DAT_febef172 != 0 || (DAT_febef208 != 0)))) {
      if (((DAT_febeb10e >> 2 & 1) == 0) &&
         (((DAT_febeb10e >> 3 & 1) == 0 && ((DAT_febeb10e >> 4 & 1) == 0)))) {
        if (DAT_febef208 != -0x5aa5a55b) {
          return;
        }
        if ((DAT_febeb10e >> 1 & 1) != 0) {
          return;
        }
        uVar1 = 4;
      }
      else {
        uVar1 = 0x2e;
      }
    }
    else {
      uVar1 = 0x2c;
    }
  }
  else {
    uVar1 = 0x2a;
  }
  FUN_000b15ac(uVar1);
  return;
}



/* Far-call trampoline: prepare {lp},0 / jarl 0xB77F4 / dispose 0,{lp},lp; byte-verified against the
   exact image. Forwards with registers and stack unchanged; marked as a thunk. Forwarding shape
   machine-verified; target semantics not recovered. */

void thunk_FUN_000b77f4(void)

{
  FUN_000b77f4();
  return;
}



void FUN_000b2f5e(void)

{
  uchar kind;
  
  if ((DAT_febeb10e >> 2 & 1) == 0) {
    if ((DAT_febeb10e >> 3 & 1) != 0) {
      kind = '\x02';
      FUN_000b794e();
      goto LAB_000b2f82;
    }
    kind = '\x03';
  }
  else {
    kind = '\x01';
  }
  FUN_000b78ee();
LAB_000b2f82:
  f33_initialize_service_engine(kind);
  return;
}



void FUN_000b2f8c(void)

{
  if ((DAT_febef012 == 'D') && (DAT_febef210 == -0x5aa5a55b)) {
    FUN_000b15ac(0x2b);
  }
  return;
}



void FUN_000b2fb4(void)

{
  DAT_febeb10e = DAT_febeb10e & 0xfe;
  thunk_FUN_00032c86();
  return;
}



void FUN_000b2fc6(void)

{
  if ((DAT_febef010 == 'D') && (DAT_febef208 == -0x5aa5a55b)) {
    FUN_000b15ac(0x2d);
  }
  return;
}



void FUN_000b2fee(void)

{
  uint32_t puVar1;
  undefined4 uVar2;
  
  puVar1 = 0xfebeb800u;
  if (DAT_febef208 == -0x5aa5a55b) {
    uVar2 = 0;
  }
  else {
    puVar1 = 0xfebeb800u;
    thunk_FUN_00035ad6();
    uVar2 = 0x20;
  }
  thunk_FUN_0004d0a4(8,uVar2);
  FUN_000b7810();
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6f2))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6f2))))) & 0xfd;
  return;
}



void FUN_000b301e(void)

{
  if (((DAT_febeb3cb == '\x02') || (DAT_febeb3cb == '\x03')) || (DAT_febeb3cb == '\0')) {
    FUN_000b15ac(0x2f);
  }
  return;
}



void FUN_000b303e(void)

{
  uint32_t puVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  byte bVar4;
  
  puVar1 = 0xfebeb800u;
  if (DAT_febeb3d5 == '\x01') {
    uVar2 = 0xc;
    bVar4 = 4;
  }
  else {
    bVar4 = 0x10;
    if (DAT_febeb3d5 == '\x02') {
      bVar4 = 8;
      uVar2 = 0xe;
    }
    else {
      uVar2 = 0xf;
    }
  }
  if (DAT_febeb3cb == '\x02') {
    uVar3 = 0;
  }
  else {
    uVar3 = 0x20;
    if (DAT_febeb3cb == '\0') {
      uVar3 = 0x30;
    }
  }
  thunk_FUN_0004d0a4(uVar2,uVar3);
  FUN_000b856a();
  FUN_000b83f2(0);
  FUN_000b85a8(0);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6f2))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6f2))))) & ~bVar4;
  return;
}



void FUN_000b3182(void)

{
  if ((DAT_febeb10e & 2) != 0) {
    thunk_FUN_0003599e();
  }
  return;
}



/* For pending IDs1/3 report failure; IDs2/4 report cancellation only with their stop latch5A,
   otherwise failure. Clear ID1 internal88 state. Does NOT clear pending bitsB10E. Report failure
   for pending IDs1/3 and cancel-or-failure for IDs2/4 using their stop latches. Clear ID1
   internal88 state but never clear pending bitmapB10E. */

void f33_report_pending_service_aborts(void)

{
  byte bVar1;
  byte bVar2;
  byte bVar3;
  char cVar4;
  char cVar5;
  undefined4 uVar6;
  
  cVar5 = DAT_febeb3dd;
  cVar4 = DAT_febeb3dc;
  bVar1 = DAT_febeb10e & 4;
  bVar2 = DAT_febeb10e & 8;
  bVar3 = DAT_febeb10e & 0x10;
  if ((DAT_febeb10e >> 1 & 1) != 0) {
    thunk_FUN_00035ad6();
    thunk_FUN_0004d0a4(8,0x20);
  }
  if (bVar1 != 0) {
    uVar6 = 0x20;
    if (cVar5 == 'Z') {
      uVar6 = 0x30;
    }
    thunk_FUN_0004d0a4(0xc,uVar6);
  }
  if (bVar2 != 0) {
    thunk_FUN_0004d0a4(0xe,0x20);
  }
  if (bVar3 != 0) {
    uVar6 = 0x20;
    if (cVar4 == 'Z') {
      uVar6 = 0x30;
    }
    thunk_FUN_0004d0a4(0xf,uVar6);
  }
  return;
}



/* Report pending aborts, clean engine/output state, clear admission latches, conditionally restore
   output masks. Pending bitsB10E survive; do not describe this as dequeue-all. Native full
   family-exit composition reports ID2 cancellation and other pending-service failures; clears
   engine substitution and admission state; restores only service-owned masks; preserves pending
   B10E. No physical service execution or persistence claim. */

void f33_exit_service_family(void)

{
  f33_report_pending_service_aborts();
  FUN_000b856a();
  FUN_000b83f2(0);
  FUN_000b85a8(0);
  FUN_000b7810();
  return;
}



/* Set and returnB10F=1 if32-bitF208nonzero, otherwise2. CallerB27FE uses r10 to decide whether to
   request6; do not typevoid. */

uint f33_select_service_join_after_mode200(void)

{
  uint uVar1;
  
  if (DAT_febef208 == 0) {
    uVar1 = 2;
  }
  else {
    uVar1 = 1;
  }
  DAT_febeb10f = (char)uVar1;
  return uVar1;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_b32f2(void)

{
  return;
}



/* ClearB110 on0600entry. Nootheraction; separateexitclearsB111 andresets6A60..6A62. */

void f33_enter_mode600(void)

{
  DAT_febeb110 = 0;
  return;
}



/* ClearB111, call33FC6 toclear6A61/6A62 andset6A60=10 before newfamilyentry andlivecommit. */

void f33_exit_mode600(void)

{
  DAT_febeb111 = 0;
  f33_cancel_mode600_stimulus_fit();
  return;
}



/* Selectors3/5/6/7 admit only modes0400/0500/0700..0702/0800. Selector4 clearsB112; selector1
   additionally needs11294C43 andsetsB110=1;selector2 in0600 setsB111=1. Reuse existing mode
   ownership. */

int f33_admit_internal_ba_selector(uint selector,uint authorization)

{
  uint uVar1;
  
  uVar1 = (uint)DAT_febeb11a;
  if ((selector == 3) || (selector - 5 < 3)) {
    if (((uVar1 == 0x400) || (uVar1 == 0x500)) || ((uVar1 - 0x700 < 3 || (uVar1 - 0x700 == 0x100))))
    {
      return 0;
    }
  }
  else {
    if (selector == 4) {
      DAT_febeb112 = 0;
      return 0;
    }
    if (selector == 1) {
      if (((((uVar1 == 0x400) || (uVar1 == 0x500)) || (uVar1 - 0x700 < 3)) ||
          (uVar1 - 0x700 == 0x100)) && (authorization == 0x11294c43)) {
        DAT_febeb110 = 1;
        return 0;
      }
    }
    else if ((selector == 2) && (uVar1 == 0x600)) {
      DAT_febeb111 = 1;
      return 0;
    }
  }
  return -6;
}



/* SetB113=22/44/88 for selectors5/6/7,otherwise11; setB112=5A,return0. Scheduled BCBD8 copies them
   toAC2B/AC2C. */

int f33_latch_internal_ba_selector(uint selector)

{
  if (selector == 5) {
    DAT_febeb113 = 0x22;
  }
  else if (selector == 6) {
    DAT_febeb113 = 0x44;
  }
  else {
    DAT_febeb113 = 0x88;
    if (selector != 7) {
      DAT_febeb113 = 0x11;
    }
  }
  DAT_febeb112 = 0x5a;
  return 0;
}



/* SetB116=5A andB117=value,return0; no timeout/cancellation in this API. */

int f33_latch_ba_unsigned_override(uchar value)

{
  DAT_febeb116 = 0x5a;
  DAT_febeb117 = value;
  return 0;
}



/* SetB118=5A,return0. Consumed by owner5 release predicate; no local reset. */

int f33_latch_ba_owner5_fast_release(void)

{
  DAT_febeb118 = 0x5a;
  return 0;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_b33d8(void)

{
  return;
}



/* Set8B2Cowners0/1=70017001,8A70owners0/1=20002,8AD0owners0/1=20002.
   Thisrequestsoutput-ownerstate,notphysicalpowerconfirmation.0900exitandsteadyworkersareempty. */

void f33_enter_mode900(void)

{
  f33_set_output_request_word('\0',0x70017001);
  f33_set_output_request_word('\x01',0x70017001);
  f33_set_channel_owner_request('\0',0x20002);
  f33_set_channel_owner_request('\x01',0x20002);
  thunk_FUN_00056e66(0, camry_host_addr(((undefined *)camry_host_ptr(0x20002u))));
  thunk_FUN_00056e66(1, camry_host_addr(((undefined *)camry_host_ptr(0x20002u))));
  return;
}



/* JMP LP with no state change; AEB00 table 0x900 exit. Exact-image hook, not a missing
   implementation. */

void f33_mode_hook_b342a(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_b342c(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_b342e(void)

{
  return;
}



void FUN_000b3430(void)

{
  char cVar1;
  char cVar2;
  char cVar3;
  ushort uVar4;
  ushort uVar5;
  uint32_t puVar6;
  uchar uVar7;
  uchar uVar8;
  char cVar9;
  char cVar10;
  char cVar11;
  char cVar12;
  ushort uVar13;
  
  puVar6 = 0xfebeb800u;
  uVar7 = f33_get_grouped_status_byte(0xc);
  uVar8 = f33_get_grouped_status_byte(0x1d);
  cVar11 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(0x3956)))));
  cVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(0x3850)))));
  uVar5 = (*((ushort *)camry_host_ptr((uint32_t)(puVar6 + -0x6ce))));
  cVar9 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6d1)))));
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6d2)))));
  cVar10 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6dc)))));
  cVar12 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6de)))));
  uVar13 = (ushort)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6e0)))));
  if (((((uVar7 == '\0' && uVar8 == '\0') && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(0x3800))))) == '\0')) && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(0x384f))))) == '\0'))
      && (cVar12 == cVar2)) &&
     ((cVar3 = cVar9, uVar4 = DAT_000aef40, cVar2 != '\a' ||
      ((cVar2 = cVar12, (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(0x3957))))) == '\0' &&
       (cVar3 = cVar1, uVar4 = DAT_000aef42, cVar1 == cVar11)))))) {
    cVar11 = cVar1;
    if (uVar13 == 0) {
      if (uVar5 < uVar4) {
        uVar5 = uVar5 + 1;
      }
      else {
        cVar10 = cVar12;
        cVar9 = cVar3;
        uVar13 = 0x5a;
      }
    }
    else {
      uVar5 = 0;
    }
  }
  else {
    cVar12 = cVar2;
    uVar5 = 0;
    uVar13 = uVar5;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6e0))))) = (char)uVar13;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6de))))) = cVar12;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6dc))))) = cVar10;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6d2))))) = cVar11;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6d1))))) = cVar9;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar6 + -0x6ce)))) = uVar5;
  return;
}



void FUN_000b34d4(void)

{
  char cVar1;
  ushort uVar2;
  uint32_t puVar3;
  uchar uVar4;
  char cVar5;
  char cVar6;
  char cVar7;
  
  puVar3 = 0xfebeb800u;
  uVar4 = f33_get_grouped_status_byte(0xc);
  cVar6 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x3941)))));
  cVar7 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6da)))));
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6d9)))));
  cVar5 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6d8)))));
  uVar2 = (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x6cc))));
  if ((((uVar4 == '\0') && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x3800))))) == '\0')) && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x384f))))) == '\0')) &&
     (cVar1 == cVar6)) {
    cVar6 = cVar1;
    if (cVar7 == '\0') {
      if (uVar2 < DAT_000aef44) {
        uVar2 = uVar2 + 1;
      }
      else {
        cVar7 = 'Z';
        cVar5 = cVar1;
      }
    }
    else {
      uVar2 = 0;
    }
  }
  else {
    uVar2 = 0;
    cVar7 = '\0';
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6da))))) = cVar7;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6d9))))) = cVar6;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6d8))))) = cVar5;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x6cc)))) = uVar2;
  return;
}



void FUN_000b3538(void)

{
  char cVar1;
  char cVar2;
  char cVar3;
  ushort uVar4;
  ushort uVar5;
  uint32_t puVar6;
  uchar uVar7;
  uchar uVar8;
  char cVar9;
  char cVar10;
  char cVar11;
  char cVar12;
  ushort uVar13;
  
  puVar6 = 0xfebeb800u;
  uVar7 = f33_get_grouped_status_byte(0xc);
  uVar8 = f33_get_grouped_status_byte(0x15);
  cVar11 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(0x394b)))));
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(0x394a)))));
  uVar5 = (*((ushort *)camry_host_ptr((uint32_t)(puVar6 + -0x6ca))));
  cVar9 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6d3)))));
  cVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6d4)))));
  cVar10 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6d5)))));
  cVar12 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6d6)))));
  uVar13 = (ushort)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6d7)))));
  if (((((uVar7 == '\0' && uVar8 == '\0') && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(0x3800))))) == '\0')) && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(0x384f))))) == '\0'))
      && (cVar12 == cVar1)) &&
     ((cVar3 = cVar9, uVar4 = DAT_000aef46, cVar1 != '\t' ||
      ((cVar1 = cVar12, (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(0x38c2))))) == '\0' &&
       (cVar3 = cVar2, uVar4 = DAT_000aef48, cVar2 == cVar11)))))) {
    cVar11 = cVar2;
    if (uVar13 == 0) {
      if (uVar5 < uVar4) {
        uVar5 = uVar5 + 1;
      }
      else {
        cVar10 = cVar12;
        cVar9 = cVar3;
        uVar13 = 0x5a;
      }
    }
    else {
      uVar5 = 0;
    }
  }
  else {
    cVar12 = cVar1;
    uVar5 = 0;
    uVar13 = uVar5;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6d7))))) = (char)uVar13;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6d6))))) = cVar12;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6d5))))) = cVar10;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6d4))))) = cVar11;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6d3))))) = cVar9;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar6 + -0x6ca)))) = uVar5;
  return;
}



void FUN_000b35dc(char param_1,char param_2,char param_3)

{
  uint uVar1;
  
  uVar1 = (uint)DAT_febeb124;
  if (((DAT_febeb120 != 'Z') || (param_1 != '\0')) && ((DAT_febeb126 != 'Z' || (param_2 != '\0'))))
  {
    if (DAT_febeb129 != 'Z') {
      return;
    }
    if (param_3 != '\0') {
      return;
    }
  }
  if (uVar1 == 0) {
    if (DAT_febeb128 == '\0') {
      if ((DAT_febeb12b == '\0') || ((DAT_febeb12b == '\t' && (DAT_febeb12d == '\0'))))
      goto LAB_000b367e;
    }
    else if (DAT_febeb128 != '\x01' && DAT_febeb128 != '\x02') {
      return;
    }
    DAT_febeb121 = 0x22;
  }
  else {
    if (((uVar1 == 2) || (uVar1 == 4)) || ((uVar1 == 7 && (DAT_febeb12f == '\x01')))) {
      DAT_febeb121 = 0x11;
      return;
    }
    if ((((uVar1 != 1) && (uVar1 != 3)) && (1 < uVar1 - 5)) &&
       ((uVar1 - 5 != 2 || (DAT_febeb12f != '\x02')))) {
      if (uVar1 == 7) {
        if (DAT_febeb12f != '\x03') {
          return;
        }
      }
      else if ((uVar1 != 8) && (uVar1 != 10 && uVar1 != 0xb)) {
        return;
      }
      DAT_febeb121 = 0x33;
      return;
    }
LAB_000b367e:
    DAT_febeb121 = 0;
  }
  return;
}



void FUN_000b3686(void)

{
  char cVar1;
  char cVar2;
  char cVar3;
  ushort uVar4;
  ushort uVar5;
  uint32_t puVar6;
  uchar uVar7;
  uchar uVar8;
  char cVar9;
  char cVar10;
  char cVar11;
  char cVar12;
  ushort uVar13;
  
  puVar6 = 0xfebeb800u;
  uVar7 = f33_get_grouped_status_byte(0xc);
  uVar8 = f33_get_grouped_status_byte(0x1c);
  cVar11 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(0x38a1)))));
  cVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(0x3850)))));
  uVar5 = (*((ushort *)camry_host_ptr((uint32_t)(puVar6 + -0x6ce))));
  cVar9 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6db)))));
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6dd)))));
  cVar10 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6dc)))));
  cVar12 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6de)))));
  uVar13 = (ushort)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6e0)))));
  if (((((uVar7 == '\0' && uVar8 == '\0') && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(0x3800))))) == '\0')) && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(0x384f))))) == '\0'))
      && (cVar12 == cVar2)) &&
     ((cVar3 = cVar9, uVar4 = DAT_000aef40, cVar2 != '\a' ||
      ((cVar2 = cVar12, (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(0x38a0))))) == '\0' &&
       (cVar3 = cVar1, uVar4 = DAT_000aef42, cVar1 == cVar11)))))) {
    cVar11 = cVar1;
    if (uVar13 == 0) {
      if (uVar5 < uVar4) {
        uVar5 = uVar5 + 1;
      }
      else {
        cVar10 = cVar12;
        cVar9 = cVar3;
        uVar13 = 0x5a;
      }
    }
    else {
      uVar5 = 0;
    }
  }
  else {
    cVar12 = cVar2;
    uVar5 = 0;
    uVar13 = uVar5;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6e0))))) = (char)uVar13;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6de))))) = cVar12;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6dc))))) = cVar10;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6dd))))) = cVar11;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6db))))) = cVar9;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar6 + -0x6ce)))) = uVar5;
  return;
}



void FUN_000b372a(char param_1,char param_2,char param_3)

{
  uint uVar1;
  
  uVar1 = (uint)DAT_febeb124;
  if (((DAT_febeb120 != 'Z') || (param_1 != '\0')) && ((DAT_febeb126 != 'Z' || (param_2 != '\0'))))
  {
    if (DAT_febeb129 != 'Z') {
      return;
    }
    if (param_3 != '\0') {
      return;
    }
  }
  if (uVar1 == 0) {
    if (DAT_febeb128 == '\0') {
      if ((DAT_febeb12b == '\0') || ((DAT_febeb12b == '\t' && (DAT_febeb12d == '\0'))))
      goto LAB_000b37d2;
    }
    else if (DAT_febeb128 != '\x01' && DAT_febeb128 != '\x02') {
      return;
    }
    DAT_febeb121 = 0x22;
  }
  else {
    if (((uVar1 == 2) || (uVar1 == 4)) ||
       ((uVar1 == 7 &&
        (((DAT_febeb125 == '\x01' || (DAT_febeb125 == '\x03')) || (DAT_febeb125 == '\x05')))))) {
      DAT_febeb121 = 0x11;
      return;
    }
    if ((((uVar1 != 1) && (uVar1 != 3)) && (1 < uVar1 - 5)) &&
       ((uVar1 - 5 != 2 ||
        (((DAT_febeb125 != '\x02' && (DAT_febeb125 != '\x04')) && (DAT_febeb125 != '\b')))))) {
      if ((uVar1 != 8) && (uVar1 != 10 && uVar1 != 0xb)) {
        return;
      }
      DAT_febeb121 = 0x33;
      return;
    }
LAB_000b37d2:
    DAT_febeb121 = 0;
  }
  return;
}



void FUN_000b37da(void)

{
  undefined1 uVar1;
  undefined1 uVar2;
  undefined1 uVar3;
  char cVar4;
  uint32_t puVar5;
  uchar uVar6;
  uchar uVar7;
  char cVar8;
  
  cVar4 = DAT_febeb130;
  uVar3 = DAT_febeb129;
  uVar2 = DAT_febeb126;
  uVar1 = DAT_febeb120;
  puVar5 = 0xfebeb800u;
  uVar6 = f33_get_grouped_status_byte(0x1c);
  uVar7 = f33_get_grouped_status_byte(0x1d);
  if ((uVar6 == '\0' && uVar7 == '\0') && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(0x3800))))) == '\0')) {
    if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(0x38a0))))) == '\0') && (cVar8 = '\0', (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(0x3968))))) != '\x03')) goto LAB_000b3844;
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(0x3957))))) != '\0') goto LAB_000b3826;
    cVar8 = '\x01';
  }
  else {
LAB_000b3826:
    cVar8 = cVar4;
    if (cVar4 != '\x01') {
LAB_000b3844:
      FUN_000b3686();
      FUN_000b34d4();
      FUN_000b3538();
      FUN_000b372a(uVar1,uVar2,uVar3);
      goto LAB_000b385a;
    }
  }
  FUN_000b3430();
  FUN_000b34d4();
  FUN_000b3538();
  FUN_000b35dc(uVar1,uVar2,uVar3);
LAB_000b385a:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x6d0))))) = cVar8;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x6cf))))) = cVar4;
  return;
}



/* WARNING: Removing unreachable block (ram,0x000b388e) */

void FUN_000b3866(void)

{
  uint uVar1;
  
  DAT_febeb13a = 0;
  uVar1 = (uint)DAT_000aef4c;
  if (uVar1 != 0) {
    DAT_febeb13a = (undefined2)(0x10000000 / uVar1);
  }
  DAT_febeb138 = DAT_000aef4c;
  DAT_febeb13c = 0x564e;
  if (uVar1 != 0) {
    DAT_febeb13c = (undefined2)(0x2774564e / uVar1);
  }
  DAT_febeb140 = DAT_febeb13c;
  DAT_febeb13e = (undefined2)((uVar1 << 0xe) / 0x9dd1);
  DAT_febeb142 = DAT_febeb13e;
  return;
}



/* WARNING: Removing unreachable block (ram,0x000b38c4) */

void FUN_000b389c(void)

{
  uint uVar1;
  
  DAT_febeb13a = 0;
  uVar1 = (uint)DAT_000aef4c;
  if (uVar1 != 0) {
    DAT_febeb13a = (undefined2)(0x10000000 / uVar1);
  }
  DAT_febeb138 = DAT_000aef4c;
  DAT_febeb13c = 0x564e;
  if (uVar1 != 0) {
    DAT_febeb13c = (undefined2)(0x2774564e / uVar1);
  }
  DAT_febeb140 = DAT_febeb13c;
  DAT_febeb13e = (undefined2)((uVar1 << 0xe) / 0x9dd1);
  DAT_febeb142 = DAT_febeb13e;
  return;
}



/* WARNING: Removing unreachable block (ram,0x000b3906) */

undefined4 FUN_000b38d2(void)

{
  ushort uVar1;
  uint32_t puVar2;
  undefined4 uVar3;
  undefined2 uVar4;
  undefined2 uVar5;
  uint uVar6;
  
  uVar1 = DAT_000aef4c;
  puVar2 = 0xfebeb800u;
  uVar6 = (uint)DAT_000aef4c;
  uVar3 = FUN_000d1da0(0xffc0);
  uVar5 = 0;
  uVar4 = 0x564e;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x6c8)))) = uVar1;
  if (uVar6 != 0) {
    uVar5 = (undefined2)(0x10000000 / uVar6);
    uVar4 = (undefined2)(0x2774564e / uVar6);
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x6c6)))) = uVar5;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x6c4)))) = uVar4;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x6c0)))) = uVar4;
  uVar5 = (undefined2)((uVar6 << 0xe) / 0x9dd1);
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x6c2)))) = uVar5;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x6be)))) = uVar5;
  FUN_000d1dc6(uVar3);
  return uVar3;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_b391c(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_b391e(void)

{
  return;
}



/* WARNING: Removing unreachable block (ram,0x000b392a) */

int FUN_000b3920(int param_1,int param_2,int param_3)

{
  int iVar1;
  int in_r17;
  int iVar2;
  
  if (param_3 == 0) {
    return 0;
  }
  iVar2 = (param_1 / 0x10000) * 0x10000;
  if (param_3 != 0) {
    if (iVar2 == -0x80000000 && param_3 == -1) {
      iVar2 = -0x80000000;
      in_r17 = 0;
    }
    else {
      in_r17 = iVar2 % param_3;
      iVar2 = iVar2 / param_3;
    }
  }
  iVar1 = (param_1 % 0x10000 + in_r17) * param_2;
  if (param_3 != 0) {
    if (iVar1 == -0x80000000 && param_3 == -1) {
      iVar1 = -0x80000000;
    }
    else {
      iVar1 = iVar1 / param_3;
    }
  }
  return iVar1 + iVar2 * param_2;
}



/* WARNING: Removing unreachable block (ram,0x000b39c0) */

void FUN_000b394c(void)

{
  int iVar1;
  uint32_t puVar2;
  undefined4 uVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int local_10;
  
  puVar2 = 0xfebeb800u;
  iVar5 = (int)DAT_febeb054;
  iVar1 = DAT_febeb150;
  uVar3 = DAT_febeb158;
  iVar4 = DAT_febeb14c;
  iVar6 = DAT_febeb148;
  if ((DAT_febeb168 == 'Z') && (DAT_febeb16a == 'Z')) {
    puVar2 = 0xfebeb800u;
    local_10 = FUN_000b3920(DAT_febeb178,0x400,DAT_febeb138);
    FUN_000d1cf6(local_10,0x5b05b0,(int)0xffa4fa50,&local_10);
    iVar6 = local_10;
    uVar3 = FUN_000b3920(local_10, 0x4507, camry_host_addr(((undefined *)camry_host_ptr(0xb400u))));
    iVar1 = (DAT_000af100 * iVar5) / 0x4000;
    iVar4 = iVar1 + iVar6;
  }
  (*((int *)camry_host_ptr((uint32_t)(puVar2 + -0x6b0)))) = iVar1;
  (*((int *)camry_host_ptr((uint32_t)(puVar2 + -0x6b8)))) = iVar6;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + -0x6a8)))) = uVar3;
  (*((int *)camry_host_ptr((uint32_t)(puVar2 + -0x6b4)))) = iVar4;
  return;
}



/* WARNING: Removing unreachable block (ram,0x000b39f8) */

void FUN_000b39d8(void)

{
  char cVar1;
  char cVar2;
  uchar uVar3;
  char cVar4;
  char cVar5;
  uint32_t puVar6;
  undefined1 uVar7;
  int local_1c;
  
  cVar5 = DAT_febef154;
  cVar4 = DAT_febef069;
  uVar3 = f33_published_internal_source_admission_state;
  cVar2 = DAT_febeb16a;
  cVar1 = DAT_febeb078;
  puVar6 = 0xfebeb800u;
  FUN_000d1194(DAT_febeb14c - ((int)DAT_febeb16c << 0x10) / 0xe10,&local_1c);
  if ((((cVar2 == '\0') || (cVar5 != '\x02')) ||
      ((local_1c - DAT_000af0fc < 0 ==
        (local_1c < 0 != DAT_000af0fc < 0 && DAT_000af0fc < 0 == local_1c - DAT_000af0fc < 0) &&
       ((uVar3 < 2 && (cVar4 == '\0')))))) || (uVar7 = 0, cVar1 != '\0')) {
    uVar7 = 0x5a;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6bc))))) = uVar7;
  (*((int *)camry_host_ptr((uint32_t)(puVar6 + -0x6ac)))) = local_1c;
  return;
}



void FUN_000b3a42(void)

{
  FUN_000b394c();
  FUN_000b39d8();
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_b3a52(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_b3a54(void)

{
  return;
}



void FUN_000b3a56(void)

{
  if (((((((DAT_febeb067 == '\0') && (DAT_febeb068 == '\0')) && (DAT_febeb069 == '\0')) &&
        ((DAT_febeb06a == '\0' && (DAT_febeb06b == '\0')))) &&
       (((DAT_febeb06c == '\0' && ((DAT_febeb06d == '\0' && (DAT_febeb06e == '\0')))) &&
        (DAT_febeb06f == '\0')))) &&
      (((DAT_febeb070 == '\0' && (DAT_febeb071 == '\0')) &&
       ((DAT_febeb358 == '\0' || (DAT_febeb358 == '\x02')))))) && (DAT_febef208 == -0x5aa5a55b)) {
    DAT_febeb16b = 0;
  }
  else {
    DAT_febeb16b = 0x5a;
  }
  return;
}



void FUN_000b3ac4(void)

{
  DAT_febeb168 = 0;
  if (DAT_febeb078 == '\0') {
    DAT_febeb168 = 0x5a;
  }
  return;
}



void FUN_000b3ad8(void)

{
  if ((((DAT_febef06b == '\0') && (DAT_febef069 == '\0')) && (DAT_febef154 == '\x02')) &&
     (f33_published_internal_source_admission_state < 2)) {
    DAT_febeb169 = 0x5a;
  }
  else {
    DAT_febeb169 = 0;
  }
  return;
}



void FUN_000b3b06(void)

{
  if ((DAT_febef069 == '\0') && (f33_published_internal_source_admission_state < 2)) {
    DAT_febeb16c = DAT_febef1a0 * 0xf + (short)DAT_febef06f;
  }
  return;
}



/* WARNING: Removing unreachable block (ram,0x000b3b56) */

void FUN_000b3b2e(void)

{
  int iVar1;
  int iVar2;
  uint32_t puVar3;
  int iVar4;
  
  iVar2 = DAT_febeafe8;
  puVar3 = 0xfebeb800u;
  iVar1 = (int)DAT_febeb16c - (DAT_000af104 * DAT_febeb054) / 0x4000;
  iVar4 = FUN_000b3920(iVar1 * (uint)DAT_febeb138,4,0xe1);
  (*((int *)camry_host_ptr((uint32_t)(puVar3 + -0x690)))) = iVar1;
  (*((int *)camry_host_ptr((uint32_t)(puVar3 + -0x68c)))) = -iVar4 - iVar2;
  (*((int *)camry_host_ptr((uint32_t)(puVar3 + -0x684)))) = iVar4;
  return;
}



void FUN_000b3b7a(void)

{
  char cVar1;
  char cVar2;
  uint32_t puVar3;
  char cVar4;
  
  cVar4 = DAT_febeb16a;
  cVar2 = DAT_febeb169;
  cVar1 = DAT_febeb168;
  puVar3 = 0xfebeb800u;
  FUN_000b3b06();
  if (((cVar1 == 'Z') && (cVar2 == 'Z')) && (cVar4 == '\0')) {
    FUN_000b3b2e();
    cVar4 = 'Z';
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x696))))) = cVar4;
  return;
}



void FUN_000b3baa(void)

{
  if ((DAT_febeb168 == 'Z') && (DAT_febeb16a == 'Z')) {
    DAT_febeb178 = -DAT_febeb174 - DAT_febeafe8;
  }
  return;
}



/* Sequential initializer chain: 5 unconditional calls and no other statements; shape-verified. The
   called sequence is the function's entire behavior; chain family members differ in callee sets. */

void f33_run_init_chain_b3bd2(void)

{
  FUN_000b3a56();
  FUN_000b3ac4();
  FUN_000b3ad8();
  FUN_000b3b7a();
  FUN_000b3baa();
  return;
}



void FUN_000b3bee(uint *param_1,uint param_2,uint *param_3)

{
  uint uVar1;
  uint uVar2;
  undefined8 uVar3;
  uint uVar4;
  uint uVar5;
  int iVar6;
  
  iVar6 = 0;
  if ((*param_1 == 0xffffffff) || (param_2 <= *param_1)) {
    uVar1 = param_1[1];
  }
  else {
    uVar2 = 0;
    while( true ) {
      uVar4 = param_1[uVar2 * 2];
      if ((param_2 < uVar4) || (uVar4 == 0xffffffff)) break;
      uVar2 = uVar2 + 1;
    }
    if (1 < uVar2) {
      iVar6 = uVar2 - 1;
    }
    uVar1 = (param_1 + iVar6 * 2)[1];
    if (uVar4 != 0xffffffff) {
      uVar5 = param_1[iVar6 * 2];
      uVar2 = (param_1 + uVar2 * 2)[1];
      uVar3 = FUN_000d2834(param_2 - uVar5,-(uint)(param_2 < uVar5),uVar2 - uVar1,
                           -(uint)(uVar2 < uVar1));
      iVar6 = FUN_000d28ea((int)uVar3,(int)((ulonglong)uVar3 >> 0x20),uVar4 - uVar5,
                           -(uint)(uVar4 < uVar5));
      uVar1 = uVar1 + iVar6;
    }
  }
  *param_3 = uVar1;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_b3c68(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_b3c6a(void)

{
  return;
}



/* Rebuild slot19 with kind16 unless B218/B21C bothA55A5AA5,B20E!=33,B215=0,B252=44,B253=0. Select
   current even when clear. This checks staged health/coherence fields; no new diagnostic event is
   reported here. */

void f33_publish_health_coherence_fault_actions(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  f33_retain_and_clear_fault_record(0x13);
  if (((((*((int *)camry_host_ptr((uint32_t)(puVar1 + -0x5e8)))) != -0x5aa5a55b) || ((*((int *)camry_host_ptr((uint32_t)(puVar1 + -0x5e4)))) != -0x5aa5a55b)) ||
      ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5f2))))) == '3')) ||
     ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5eb))))) != '\0' || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5ae))))) != 'D')) || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5ad))))) != '\0')))) {
    f33_encode_fault_action_kind('\x13','\x16');
  }
  f33_select_current_fault_record(0x13);
  return;
}



/* Initialize only redundant B18E to0; preserve receive-generation B195/B196 and counters. Not a
   cold application reset. */

undefined4 f33_initialize_source_coherence_history(void)

{
  return FUN_000d268c(0, ((byte *)camry_host_ptr((uint32_t)((0xfebeb18eu)))), ((byte *)camry_host_ptr((uint32_t)((0xfebeb18cu)))), ((undefined *)camry_host_ptr(0xfebeb18du)));
}



/* Clear B198/B19A/B19C,B190/B191 and redundant summary; preserveB195/B196 and
   separateB193/B194/B19E/B1A0. */

undefined4 f33_reset_current_source_coherence_observations(void)

{
  DAT_febeb198 = 0;
  DAT_febeb19a = 0;
  DAT_febeb19c = 0;
  DAT_febeb190 = 0;
  f33_current_source_coherence_observations = '\0';
  return FUN_000d268c(0, ((byte *)camry_host_ptr((uint32_t)((0xfebeb18eu)))), ((byte *)camry_host_ptr((uint32_t)((0xfebeb18cu)))), ((undefined *)camry_host_ptr(0xfebeb18du)));
}



/* R6 counter; R7 packed byte status,byte qualifier,uint16 threshold; R8 current tag; R9 expected;
   fifth argument low byte at incomingSP. Armed!=5A preserves count and returns0. Otherwise
   exactA5/status0/B084>=2304/tag match or33333333/FFFFFFFF; strict uint16 count>limit. FullR10=0/1.
   Native packed register/stack ABI crosses strict channel threshold and preserves a disabled
   counter; receive-edge admission and sticky/current separation remain distinct. */

uint f33_qualify_packed_channel_zero_status
               (ushort *count,uint packed_status_qualifier_limit,uint current_tag,uint expected_tag,
               uchar generation_armed)

{
  ushort uVar1;
  uint uVar2;
  undefined1 uStack_c;
  undefined1 uStack_b;
  undefined2 uStack_a;
  
  uVar2 = 0;
  if (generation_armed == 'Z') {
    uStack_b = (char)(packed_status_qualifier_limit >> 8);
    if ((((((int8_t)uStack_b) == -0x5b) && (DAT_000aefa8 <= DAT_febeb084)) &&
        (uStack_c = (char)packed_status_qualifier_limit, uStack_c == '\0')) &&
       (((current_tag == 0x33333333 || (current_tag == 0xffffffff)) || (current_tag == expected_tag)
        ))) {
      uVar1 = *count;
      uStack_a = (ushort)(packed_status_qualifier_limit >> 0x10);
      if ((uStack_a < uVar1) || (*count = uVar1 + 1, uStack_a < (ushort)(uVar1 + 1))) {
        uVar2 = 1;
      }
    }
    else {
      *count = 0;
    }
  }
  return uVar2;
}



/* BEDD5A,BEDE>=512,B084>=2304; strictB19C>200, otherwise reset0. Independent ofB196. */

uint f33_qualify_secondary_received_status_delay(void)

{
  uint uVar1;
  
  uVar1 = 0;
  if (((DAT_febebedd == 'Z') && (DAT_000aefae <= DAT_febebede)) && (DAT_000aefa8 <= DAT_febeb084)) {
    if ((DAT_000aefb0 < DAT_febeb19c) ||
       (DAT_febeb19c = DAT_febeb19c + 1, DAT_000aefb0 < DAT_febeb19c)) {
      uVar1 = 1;
    }
  }
  else {
    DAT_febeb19c = 0;
  }
  return uVar1;
}



/* Only called byB3F44 under entryB1D1==5A; recomputeB192. Unlike summarybit3, standalonebit1 is not
   direct trigger; selected-problem branch acceptsbit1 orF093bit1. */

void f33_refresh_gated_source_coherence_indicator(uint source_history)

{
  DAT_febeb192 = 0;
  if ((DAT_000aefa8 <= DAT_febeb084) &&
     (((((source_history & 1) != 0 || (DAT_febeb18f == 'Z')) || ((DAT_febef16a & 0x1010) != 0)) ||
      ((((((DAT_febebe7c == '\"' && (DAT_febeb314 == 0x55aaaa55)) ||
          ((DAT_febebe7d == '\"' && (DAT_febeb314 == -0x55aaaa56)))) ||
         ((DAT_febebe89 == '\"' || (DAT_febeb314 == -1)))) ||
        ((DAT_febeb314 == 0x33333333 || (DAT_febeb300 == '\"')))) &&
       (((source_history >> 1 & 1) != 0 || ((DAT_febef093 >> 1 & 1) != 0)))))))) {
    DAT_febeb192 = 0x5a;
  }
  return;
}



/* FullR10=1 onlyB20E==11 orB190==5A; numeric state22 alone does not assert this predicate. */

uint f33_is_health_or_command_completion_observed(void)

{
  uint uVar1;
  
  uVar1 = 0;
  if ((DAT_febeb20e == '\x11') || (DAT_febeb190 == 'Z')) {
    uVar1 = 1;
  }
  return uVar1;
}


