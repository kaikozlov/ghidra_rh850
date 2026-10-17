#include "common.h"


void FUN_00094008(ushort param_1)

{
  f33_dcm_pending_dispatch_receive_slot = param_1;
  return;
}



ushort FUN_0009400e(void)

{
  return f33_dcm_pending_dispatch_receive_slot;
}



void FUN_0009405c(undefined2 param_1)

{
  uint uVar1;
  
  uVar1 = DAT_febe59e6 + 1;
  *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe59dcu)) + (uint)DAT_febe59e6 * 2) = param_1;
  DAT_febe59e6 = (ushort)uVar1;
  if (1 < (uVar1 & 0xffff)) {
    DAT_febe59e6 = 0;
  }
  return;
}



undefined2 FUN_0009407c(void)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  
  uVar2 = (uint)DAT_febe59e4;
  uVar1 = uVar2 + 1;
  uVar3 = uVar1 & 0xffff;
  DAT_febe59e4 = (ushort)uVar1;
  if (1 < uVar3) {
    DAT_febe59e4 = 0;
    uVar3 = 0;
  }
  if (uVar3 == DAT_febe59e6) {
    DAT_febe59e4 = 0;
    DAT_febe59e6 = 0;
  }
  return *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe59dcu)) + uVar2 * 2);
}



void FUN_000940ba(void)

{
  uint32_t puVar1;
  undefined2 uVar2;
  
  puVar1 = 0xfebeb800u;
  uVar2 = FUN_00093e82();
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x5e18)))) = uVar2;
  return;
}



ushort FUN_000940ca(void)

{
  return f33_dcm_displaced_transmit_id;
}



void FUN_000940d0(uchar param_1,char param_2)

{
  if (param_2 == '\0') {
    f33_dcm_zero_p2_deadline = param_1;
    return;
  }
  if (param_2 == '\x01') {
    f33_dcm_zero_overall_timeout = param_1;
  }
  return;
}



uchar FUN_000940e6(char param_1)

{
  uchar uVar1;
  
  if (param_1 == '\0') {
    return f33_dcm_zero_p2_deadline;
  }
  uVar1 = '\0';
  if (param_1 == '\x01') {
    uVar1 = f33_dcm_zero_overall_timeout;
  }
  return uVar1;
}



undefined4 FUN_000942ac(char param_1,char param_2,int *param_3)

{
  byte bVar1;
  uint uVar2;
  uint uVar3;
  int iVar4;
  
  if (param_3 == (int *)0x0) {
    return 1;
  }
  if (param_1 == '\x01' || param_1 == '\x02') {
    if (*param_3 == 0) {
      return 1;
    }
    if (param_1 != '\x01') {
      uVar2 = (uint)(*((byte *)camry_host_ptr((uint32_t)(*param_3 + 8))));
      iVar4 = *(int *)*param_3;
      goto LAB_0009432c;
    }
    uVar2 = (uint)(*((byte *)camry_host_ptr((uint32_t)(*param_3 + 9))));
    iVar4 = *param_3;
  }
  else if (param_1 == '\x11' || param_1 == '\x12') {
    if (param_3[1] == 0) {
      return 1;
    }
    if (param_1 == '\x11') {
      bVar1 = *(byte *)(param_3[1] + 0xd);
      iVar4 = param_3[1];
LAB_00094320:
      uVar2 = (uint)bVar1;
      iVar4 = (*((int *)camry_host_ptr((uint32_t)(iVar4 + 8))));
      goto LAB_0009432c;
    }
    uVar2 = (uint)*(byte *)(param_3[1] + 0xc);
    iVar4 = param_3[1];
  }
  else {
    if (param_1 != '!' && param_1 != '\"') {
      return 1;
    }
    if (param_3[2] == 0) {
      return 1;
    }
    if (param_1 == '!') {
      bVar1 = *(byte *)(param_3[2] + 0xd);
      iVar4 = param_3[2];
      goto LAB_00094320;
    }
    uVar2 = (uint)*(byte *)(param_3[2] + 0xc);
    iVar4 = param_3[2];
  }
  iVar4 = (*((int *)camry_host_ptr((uint32_t)(iVar4 + 4))));
LAB_0009432c:
  if (uVar2 != 0) {
    if (iVar4 == 0) {
      return 1;
    }
    uVar3 = 0;
    while( true ) {
      if (uVar2 <= uVar3) {
        return 1;
      }
      if ((*((char *)camry_host_ptr((uint32_t)(uVar3 + iVar4)))) == param_2) break;
      uVar3 = uVar3 + 1 & 0xff;
    }
  }
  return 0;
}



undefined4 FUN_00094350(undefined2 param_1,undefined1 param_2,undefined1 param_3)

{
  undefined8 uVar1;
  int iVar2;
  uint uVar3;
  undefined4 uVar4;
  byte bVar5;
  byte local_20;
  uchar uStack_1f;
  ushort uStack_1e;
  ushort auStack_1c [2];
  
  uVar1 = 0x23dfc00000000;
  uVar4 = 0;
  iVar2 = FUN_00095514(param_1,&local_20);
  if ((iVar2 == 0) && (local_20 != 0)) {
    for (bVar5 = 0; bVar5 < local_20; bVar5 = bVar5 + 1) {
      iVar2 = ((void)(auStack_1c), FUN_0009552a(param_1, bVar5));
      if (((iVar2 != 0) ||
          (uVar3 = f33_dcm_resolve_did_group(auStack_1c[0],'\x01',&uStack_1e,&uStack_1f), uVar3 != 0
          )) || (iVar2 = FUN_000942ac(param_2, param_3, ((int *)camry_host_ptr((uint32_t)((*((undefined4 *)camry_host_ptr((uint32_t)(0x2250u +
                                       (short)uStack_1e * 0x1c + (int)((ulonglong)uVar1 >> 0x20))))))))),
                iVar2 != 0)) goto LAB_000943c6;
    }
  }
  else {
LAB_000943c6:
    uVar4 = 1;
  }
  return uVar4;
}



undefined4 FUN_0009456e(byte param_1,uint param_2,short param_3,undefined1 *param_4)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = (param_2 & 0xff) - 1;
  uVar2 = 0;
  if (((int)((uint)param_1 - iVar1) < 0 !=
       (iVar1 < 0 && iVar1 < 0 == (int)((uint)param_1 - iVar1) < 0)) && (param_3 == 0)) {
    DAT_febe5d20 = param_1 + 1;
    uVar2 = 10;
    *param_4 = 1;
  }
  return uVar2;
}



undefined4 FUN_00094d9c(ushort param_1,undefined2 *param_2)

{
  uint uVar1;
  undefined4 uVar2;
  uint uVar3;
  uint uVar4;
  
  uVar2 = 1;
  if (DAT_00026018 != '\0') {
    uVar4 = 0;
    if (param_1 < DAT_00025fec) {
      return uVar2;
    }
    if (DAT_00025fec != param_1) {
      uVar3 = (uint)(byte)(DAT_00026018 - 1);
      if (DAT_00025fec < param_1) {
        return uVar2;
      }
      do {
        if (uVar3 <= uVar4) {
          return uVar2;
        }
        uVar1 = (int)(uVar4 + uVar3) >> 1;
        if (DAT_00025fec < param_1) {
          uVar4 = uVar1 + 1 & 0xff;
          uVar1 = uVar3;
        }
        uVar3 = uVar1;
      } while (DAT_00025fec != param_1);
    }
    *param_2 = (short)uVar4;
    uVar2 = 0;
  }
  return uVar2;
}



undefined4 FUN_00094e6a(undefined2 param_1,int param_2,uint param_3)

{
  int iVar1;
  undefined4 uVar2;
  uint uVar3;
  byte bStack_19;
  undefined2 uStack_18;
  undefined1 uStack_16;
  undefined1 uStack_15;
  
  iVar1 = FUN_00095514(param_1,&bStack_19);
  uVar3 = 0;
  if (iVar1 == 0) {
    for (; uVar3 < (param_3 & 0xff); uVar3 = uVar3 + 1 & 0xff) {
      iVar1 = uVar3 * 4;
      uStack_18 = CONCAT11((*((undefined1 *)camry_host_ptr((uint32_t)(iVar1 + 2 + param_2)))),(*((undefined1 *)camry_host_ptr((uint32_t)(iVar1 + 3 + param_2))))
                          );
      uStack_16 = (*((undefined1 *)camry_host_ptr((uint32_t)(iVar1 + param_2 + 4))));
      uStack_15 = (*((undefined1 *)camry_host_ptr((uint32_t)(iVar1 + param_2 + 5))));
      iVar1 = ((void)(&uStack_18), FUN_00095474(param_1, bStack_19 + uVar3 & 0xff));
      if (iVar1 != 0) goto LAB_00094e86;
    }
    uVar2 = FUN_000954dc(param_1,(param_3 & 0xff) + (uint)bStack_19 & 0xff);
  }
  else {
LAB_00094e86:
    uVar2 = 1;
  }
  return uVar2;
}



undefined4 FUN_00094f3a(undefined2 param_1)

{
  int iVar1;
  undefined4 uVar2;
  undefined2 uStack_a;
  
  uVar2 = 1;
  iVar1 = FUN_00094d9c(param_1,&uStack_a);
  if (iVar1 == 0) {
    uVar2 = FUN_000954ee(uStack_a);
  }
  return uVar2;
}



/* Far-call trampoline: prepare {lp},0 / jarl 0x95500 / dispose 0,{lp},lp; byte-verified against the
   exact image. Forwards with registers and stack unchanged; marked as a thunk. Forwarding shape
   machine-verified; target semantics not recovered. */

void thunk_FUN_00095500(void)

{
  FUN_00095500();
  return;
}



int FUN_0009502a(undefined2 param_1,undefined1 param_2,undefined1 *param_3)

{
  undefined8 uVar1;
  int iVar2;
  uint uVar3;
  byte bVar4;
  byte bStack_1d;
  uchar uStack_1c;
  undefined1 uStack_1b;
  ushort uStack_1a;
  ushort auStack_18 [2];
  
  uVar1 = 0x23dfc00000000;
  *param_3 = 0;
  uStack_1b = 0;
  iVar2 = FUN_00095514(param_1,&bStack_1d);
  if ((iVar2 == 0) && (bStack_1d != 0)) {
    for (bVar4 = 0; iVar2 = 0, bVar4 < bStack_1d; bVar4 = bVar4 + 1) {
      iVar2 = ((void)(auStack_18), FUN_0009552a(param_1, bVar4));
      if ((iVar2 != 0) ||
         (uVar3 = f33_dcm_resolve_did_group(auStack_18[0],'\x01',&uStack_1a,&uStack_1c), uVar3 != 0)
         ) goto LAB_000950ba;
      iVar2 = FUN_00094f94(param_2, ((int *)camry_host_ptr((uint32_t)((*((undefined4 *)camry_host_ptr((uint32_t)(0x2250u +
                                    (short)uStack_1a * 0x1c + (int)((ulonglong)uVar1 >> 0x20)))))))), 
                           auStack_18[0], &uStack_1b);
      if (iVar2 != 0) {
        if (iVar2 != 1) {
          return iVar2;
        }
        *param_3 = uStack_1b;
        return 1;
      }
    }
  }
  else {
LAB_000950ba:
    iVar2 = 1;
  }
  return iVar2;
}



int FUN_000950c0(short param_1,undefined1 param_2,undefined1 *param_3)

{
  ushort uVar1;
  char cVar2;
  uint32_t puVar3;
  uint uVar4;
  int iVar5;
  uchar uStack_1c;
  undefined1 uStack_1b;
  ushort uStack_1a;
  
  puVar3 = 0x23dfcu;
  *param_3 = 0;
  cVar2 = DAT_00026019;
  uVar1 = DAT_00025fec;
  if ((param_1 != 0) ||
     (uVar4 = f33_dcm_resolve_did_group(DAT_00025fec,'\0',&uStack_1a,&uStack_1c), uVar4 != 0)) {
    return 1;
  }
  iVar5 = FUN_00094f94(param_2, ((int *)camry_host_ptr((uint32_t)((*((undefined4 *)camry_host_ptr((uint32_t)(puVar3 + 0x2220))))))), uVar1, &uStack_1b);
  if (iVar5 != 0) {
    if (iVar5 != 1) {
      return iVar5;
    }
    *param_3 = uStack_1b;
    return 1;
  }
  if (cVar2 != '\x01') {
    return 0;
  }
  iVar5 = FUN_0009502a(0,param_2,param_3);
  return iVar5;
}



void FUN_0009512c(void)

{
  DAT_febe5d20 = 0;
  DAT_febe5d21 = 0;
  FUN_00095500();
  return;
}



undefined4 FUN_000951b8(ushort param_1,byte param_2,undefined4 param_3)

{
  uint uVar1;
  
  if (param_2 < 2) {
    uVar1 = f33_dcm_probe_did_metadata(param_1);
    (*((bool *)camry_host_ptr((uint32_t)(param_3)))) = uVar1 != 0;
  }
  return 0;
}



undefined4 FUN_000951da(ushort param_1,byte param_2,undefined4 param_3)

{
  uint uVar1;
  
  if (param_2 < 2) {
    uVar1 = f33_dcm_probe_did_metadata(param_1);
    (*((bool *)camry_host_ptr((uint32_t)(param_3)))) = uVar1 != 0;
  }
  return 0;
}



undefined4 FUN_000951fc(ushort param_1,byte param_2,undefined4 param_3)

{
  uint uVar1;
  
  if (param_2 < 2) {
    uVar1 = f33_dcm_probe_did_metadata(param_1);
    (*((bool *)camry_host_ptr((uint32_t)(param_3)))) = uVar1 != 0;
  }
  return 0;
}



undefined4 FUN_0009521e(ushort param_1,byte param_2,undefined4 param_3)

{
  uint uVar1;
  
  if (param_2 < 2) {
    uVar1 = f33_dcm_probe_did_metadata(param_1);
    (*((bool *)camry_host_ptr((uint32_t)(param_3)))) = uVar1 != 0;
  }
  return 0;
}



undefined4 FUN_00095240(ushort param_1,byte param_2,undefined4 param_3)

{
  uint uVar1;
  
  if (param_2 < 2) {
    uVar1 = f33_dcm_probe_did_metadata(param_1);
    (*((bool *)camry_host_ptr((uint32_t)(param_3)))) = uVar1 != 0;
  }
  return 0;
}



undefined4 FUN_00095262(undefined4 param_1,byte param_2,ushort *param_3)

{
  if (param_2 < 2) {
    f33_dcm_selected_did_payload_length(param_3);
  }
  return 0;
}



undefined4 FUN_00095278(undefined4 param_1,byte param_2,ushort *param_3)

{
  if (param_2 < 2) {
    f33_dcm_selected_did_payload_length(param_3);
  }
  return 0;
}



undefined4 FUN_0009528e(undefined4 param_1,byte param_2,ushort *param_3)

{
  if (param_2 < 2) {
    f33_dcm_selected_did_payload_length(param_3);
  }
  return 0;
}



undefined4 FUN_000952a4(undefined4 param_1,byte param_2,ushort *param_3)

{
  if (param_2 < 2) {
    f33_dcm_selected_did_payload_length(param_3);
  }
  return 0;
}



undefined4 FUN_000952ba(undefined4 param_1,byte param_2,ushort *param_3)

{
  if (param_2 < 2) {
    f33_dcm_selected_did_payload_length(param_3);
  }
  return 0;
}



uint FUN_000952d0(ushort param_1,uchar *param_2,byte param_3,ushort *param_4,uchar *param_5)

{
  uint uVar1;
  
  if (param_3 < 2) {
    uVar1 = f33_did_read_application_adapter(param_2,param_4,param_5,param_1);
  }
  else {
    uVar1 = 0;
    if (param_3 == 2) {
      thunk_FUN_0008b3d4();
    }
  }
  return uVar1;
}



uint FUN_00095300(ushort param_1,uchar *param_2,byte param_3,ushort *param_4,uchar *param_5)

{
  uint uVar1;
  
  if (param_3 < 2) {
    uVar1 = f33_did_read_application_adapter(param_2,param_4,param_5,param_1);
  }
  else {
    uVar1 = 0;
    if (param_3 == 2) {
      thunk_FUN_0008b3d4();
    }
  }
  return uVar1;
}



uint FUN_00095330(ushort param_1,uchar *param_2,byte param_3,ushort *param_4,uchar *param_5)

{
  uint uVar1;
  
  if (param_3 < 2) {
    uVar1 = f33_did_read_application_adapter(param_2,param_4,param_5,param_1);
  }
  else {
    uVar1 = 0;
    if (param_3 == 2) {
      thunk_FUN_0008b3d4();
    }
  }
  return uVar1;
}



uint FUN_00095360(ushort param_1,uchar *param_2,byte param_3,ushort *param_4,uchar *param_5)

{
  uint uVar1;
  
  if (param_3 < 2) {
    uVar1 = f33_did_read_application_adapter(param_2,param_4,param_5,param_1);
  }
  else {
    uVar1 = 0;
    if (param_3 == 2) {
      thunk_FUN_0008b3d4();
    }
  }
  return uVar1;
}



uint FUN_00095390(ushort param_1,uchar *param_2,byte param_3,ushort *param_4,uchar *param_5)

{
  uint uVar1;
  
  if (param_3 < 2) {
    uVar1 = f33_did_read_application_adapter(param_2,param_4,param_5,param_1);
  }
  else {
    uVar1 = 0;
    if (param_3 == 2) {
      thunk_FUN_0008b3d4();
    }
  }
  return uVar1;
}



uint FUN_000953c0(ushort param_1,uchar *param_2,byte param_3,ushort param_4,uchar *param_5)

{
  uint uVar1;
  
  if (param_3 < 2) {
    uVar1 = f33_write_did_request_adapter(param_1,param_2,param_4,param_5);
  }
  else {
    uVar1 = 0;
    if (param_3 == 2) {
      FUN_0008b3e8();
    }
  }
  return uVar1;
}



uint FUN_000953ec(ushort param_1,uchar *param_2,byte param_3,ushort param_4,uchar *param_5)

{
  uint uVar1;
  
  if (param_3 < 2) {
    uVar1 = f33_write_did_request_adapter(param_1,param_2,param_4,param_5);
  }
  else {
    uVar1 = 0;
    if (param_3 == 2) {
      FUN_0008b3e8();
    }
  }
  return uVar1;
}



undefined4 FUN_00095418(ushort param_1,undefined2 *param_2)

{
  uint uVar1;
  undefined4 uVar2;
  uint uVar3;
  uint uVar4;
  
  uVar2 = 1;
  if (DAT_00026014 != 0) {
    uVar4 = 0;
    if (param_1 < DAT_00026028) {
      return uVar2;
    }
    if (DAT_00026028 != param_1) {
      uVar3 = (uint)(ushort)(DAT_00026014 - 1);
      if (DAT_00026028 < param_1) {
        return uVar2;
      }
      do {
        if (uVar3 <= uVar4) {
          return uVar2;
        }
        uVar1 = (int)(uVar4 + uVar3) >> 1;
        if (DAT_00026028 < param_1) {
          uVar4 = uVar1 + 1 & 0xffff;
          uVar1 = uVar3;
        }
        uVar3 = uVar1;
      } while (DAT_00026028 != param_1);
    }
    *param_2 = (short)uVar4;
    uVar2 = 0;
  }
  return uVar2;
}



bool FUN_000954dc(short param_1,undefined1 param_2)

{
  if (param_1 == 0) {
    DAT_febe5d23 = param_2;
  }
  return param_1 != 0;
}



bool FUN_000954ee(short param_1)

{
  if (param_1 == 0) {
    DAT_febe5d23 = 0;
  }
  return param_1 != 0;
}



undefined4 FUN_00095500(void)

{
  uint uVar1;
  
  for (uVar1 = (uint)DAT_00026018; uVar1 != 0; uVar1 = uVar1 - 1) {
    DAT_febe5d23 = 0;
  }
  return 0;
}



bool FUN_00095514(short param_1,undefined1 *param_2)

{
  if (param_1 == 0) {
    *param_2 = DAT_febe5d23;
  }
  return param_1 != 0;
}



void FUN_000955b6(uchar param_1)

{
  f33_app_dcm_callback_pending = param_1;
  return;
}



uchar FUN_000955bc(void)

{
  return f33_app_dcm_callback_pending;
}



void FUN_0009560e(char param_1)

{
  if (param_1 == '\x01') {
    DAT_febe5d24 = 0;
  }
  else {
    DAT_febe5d24 = 0xa5a5a5a5;
  }
  return;
}



/* Constant source: return 1; shape-classified from the canonical corpus. Callers receive this
   literal directly; its meaning is not recovered. */

undefined4 f33_return_const_1_95622(void)

{
  return 1;
}



/* Stage NRC;78 leaves service pending and does not finalize message. Other NRCs complete
   through9126A/disposition queue. */

void f33_dcm_report_negative_or_pending(F33DcmMessageContext *message,uchar nrc)

{
  f33_dcm_stage_negative_response(message,nrc);
  if (nrc != 'x') {
    f33_dcm_complete_service_response(message);
  }
  return;
}



/* Forward handler-retained body length/routing through9126A. This is response readiness, not
   delivery. */

void f33_dcm_report_positive_response(F33DcmMessageContext *message)

{
  f33_dcm_complete_service_response(message);
  return;
}



undefined4 FUN_00095674(undefined1 param_1)

{
  int iVar1;
  uint32_t puVar2;
  uint32_t puVar3;
  int iVar4;
  undefined4 uVar5;
  uchar uStack_11;
  
  puVar2 = 0xfebeb800u;
  puVar3 = 0x23dfcu;
  uVar5 = 0;
  iVar1 = DAT_febe5d30 + 2;
  iVar4 = FUN_00094786(DAT_febe5d2c, DAT_febe5d2e, ((uchar *)camry_host_ptr((uint32_t)(iVar1))), param_1, DAT_febe5d34 - 2U & 0xffff, &uStack_11
                      );
  if (iVar4 == 0) {
    FUN_000955b6(0);
    if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x2cf5))))) == '\x01') && ((*((short *)camry_host_ptr((uint32_t)(puVar3 + 0x2cf6)))) == (*((short *)camry_host_ptr((uint32_t)(puVar2 + -0x5ad2))))))
    {
      ((void)(iVar1), f33_return_only_stub_98900());
    }
    if (1 < (*((uint *)camry_host_ptr((uint32_t)(puVar2 + -0x5abc))))) {
      **(undefined1 **)(puVar2 + -0x5ac8) = **(undefined1 **)(puVar2 + -0x5ad0);
      (*((undefined1 *)camry_host_ptr((uint32_t)(*(int *)(puVar2 + -0x5ac8) + 1)))) =
           (*((undefined1 *)camry_host_ptr((uint32_t)(*(int *)(puVar2 + -0x5ad0) + 1))));
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + -0x5ac4)))) = 2;
      f33_dcm_report_positive_response(((F33DcmMessageContext *)camry_host_ptr((uint32_t)(puVar2 + -0x5ad0))));
    }
  }
  else if (iVar4 == 10) {
    FUN_000955b6(1);
    f33_dcm_enqueue_event('\x13');
    uVar5 = 10;
  }
  else {
    FUN_000955b6(0);
    if ((iVar4 == 1) && (uStack_11 != '\0')) {
      f33_dcm_report_negative_or_pending(((F33DcmMessageContext *)camry_host_ptr((uint32_t)(puVar2 + -0x5ad0))),uStack_11);
    }
  }
  return uVar5;
}



undefined4 FUN_00095734(undefined1 param_1)

{
  uint32_t puVar1;
  uchar nrc;
  int iVar2;
  undefined4 uVar3;
  uchar uStack_b;
  ushort uStack_a;
  
  puVar1 = 0xfebeb800u;
  uVar3 = 0;
  iVar2 = FUN_0009449e(DAT_febe5d2c,DAT_febe5d2e,param_1,&uStack_a);
  if (iVar2 == 0) {
    FUN_000955b6(0);
    if ((uint)uStack_a == (*((int *)camry_host_ptr((uint32_t)(puVar1 + -0x5acc)))) - 2U) {
      f33_dcm_get_security_level(&uStack_b);
      iVar2 = FUN_000943ce((*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x5ad4)))),1,0x22,uStack_b);
      if (iVar2 == 0) {
        uVar3 = FUN_00095674(0);
        return uVar3;
      }
      nrc = '3';
    }
    else {
      nrc = '\x13';
    }
    f33_dcm_report_negative_or_pending(((F33DcmMessageContext *)camry_host_ptr((uint32_t)(puVar1 + -0x5ad0))),nrc);
  }
  else if (iVar2 == 10) {
    FUN_000955b6(1);
    f33_dcm_enqueue_event('\x12');
    uVar3 = 10;
  }
  else {
    FUN_000955b6(0);
  }
  return uVar3;
}



undefined4 FUN_000957c8(void)

{
  uint32_t puVar1;
  int iVar2;
  undefined4 uVar3;
  uchar uStack_9;
  
  puVar1 = 0xfebeb800u;
  f33_dcm_get_session(&uStack_9);
  iVar2 = FUN_000943ce((*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x5ad4)))),1,0x21,uStack_9);
  if (iVar2 == 0) {
    uVar3 = FUN_00095734(0);
  }
  else {
    uVar3 = 0;
    f33_dcm_report_negative_or_pending(((F33DcmMessageContext *)camry_host_ptr((uint32_t)(puVar1 + -0x5ad0))),'1');
  }
  return uVar3;
}



undefined4 FUN_00095808(undefined1 param_1)

{
  uint32_t puVar1;
  int iVar2;
  undefined4 uVar3;
  char cStack_9;
  
  puVar1 = 0xfebeb800u;
  uVar3 = 0;
  iVar2 = FUN_0009445a(DAT_febe5d2c,DAT_febe5d2e,param_1,&cStack_9);
  if (iVar2 == 0) {
    FUN_000955b6(0);
    if (cStack_9 == '\0') {
      uVar3 = FUN_000957c8();
    }
    else {
      f33_dcm_report_negative_or_pending(((F33DcmMessageContext *)camry_host_ptr((uint32_t)(puVar1 + -0x5ad0))),'1');
    }
  }
  else if (iVar2 == 10) {
    FUN_000955b6(1);
    f33_dcm_enqueue_event('\x11');
    uVar3 = 10;
  }
  else {
    FUN_000955b6(0);
  }
  return uVar3;
}



undefined4 FUN_0009586c(undefined4 *param_1)

{
  undefined4 *puVar1;
  uint32_t puVar2;
  ushort did;
  uchar nrc;
  uint uVar3;
  undefined4 uVar4;
  undefined4 *puVar5;
  byte bStack_d;
  
  puVar2 = 0xfebeb800u;
  FUN_0009560e(0);
  puVar1 = ((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + -0x5ad0)));
  puVar5 = param_1 + 7;
  do {
    uVar4 = *param_1;
    param_1 = param_1 + 1;
    *puVar1 = uVar4;
    puVar1 = puVar1 + 1;
  } while (puVar5 != param_1);
  FUN_000955b6(0);
  if ((*((uint *)camry_host_ptr((uint32_t)(puVar2 + -0x5acc)))) < 3) {
    nrc = '\x13';
  }
  else {
    did = CONCAT11(**(undefined1 **)(puVar2 + -0x5ad0),(*(undefined1 **)(puVar2 + -0x5ad0))[1]);
    (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x5ad2)))) = did;
    uVar3 = f33_dcm_resolve_did_group(did,'\x01',((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x5ad4))),&bStack_d);
    if (uVar3 == 0) {
      if ((bStack_d >> 2 & 1) != 0) {
        uVar4 = FUN_00095808(0);
        return uVar4;
      }
    }
    else if (uVar3 != 1) {
      return 0;
    }
    nrc = '1';
  }
  f33_dcm_report_negative_or_pending(((F33DcmMessageContext *)camry_host_ptr((uint32_t)(puVar2 + -0x5ad0))),nrc);
  return 0;
}



/* 0 starts9586C,2 cancels958F4; all paths meaningful r10. */

uint f33_dcm_write_did_service(uchar operation,F33DcmMessageContext *message)

{
  uint uVar1;
  
  if (operation == '\0') {
    uVar1 = FUN_0009586c(message);
  }
  else {
    uVar1 = 0;
    if (operation == '\x02') {
      uVar1 = FUN_000958f4(((undefined *)camry_host_ptr(0xfebe5d30u)));
    }
  }
  return uVar1;
}



void FUN_0009599c(void)

{
  FUN_00095808(1);
  return;
}



void FUN_000959aa(void)

{
  FUN_00095734(1);
  return;
}



void FUN_000959b8(void)

{
  FUN_00095674(1);
  return;
}



void FUN_00095a06(void)

{
  FUN_0009560e(1);
  return;
}



uint FUN_00095a14(char param_1,F33DcmMessageContext *param_2)

{
  uint uVar1;
  
  if (param_1 == '\0') {
    uVar1 = f33_dcm_tester_present_request(param_2);
  }
  else {
    uVar1 = 0;
    if (param_1 == '\x02') {
      FUN_00095a06();
    }
  }
  return uVar1;
}



/* Operation0\u219295A3E admission;2\u219295B48 cancellation;3\u219295B88 pending-response
   notification. Other operations no action. Operation0→95A3E admission;2→95B48
   cancellation;3→95B88 pending-response notification. */

uint f33_dcm_session_operation(uchar operation,F33DcmMessageContext *message,uchar target)

{
  uint uVar1;
  
  if (operation == '\0') {
    uVar1 = f33_dcm_session_request(message,target);
  }
  else {
    uVar1 = 0;
    if (operation == '\x02') {
      f33_dcm_session_cancel();
    }
    else if (operation == '\x03') {
      uVar1 = f33_dcm_programming_pending_response_join(target);
    }
  }
  return uVar1;
}



void FUN_00095cf2(void)

{
  f33_app_programming_handoff_pending_join();
  return;
}



/* Configured SID10 operation callback for target0x01; forwards operation/message plus fixed target
   inr8 to95C52. Callback return is ignored by existing F33DcmServiceCallback dispatcher. No direct
   hardware transition. */

uint f33_dcm_session_1_callback(uchar operation,F33DcmMessageContext *message)

{
  uint uVar1;
  
  uVar1 = f33_dcm_session_operation(operation,message,'\x01');
  return uVar1;
}



/* Configured SID10 operation callback for target0x02; forwards operation/message plus fixed target
   inr8 to95C52. Callback return is ignored by existing F33DcmServiceCallback dispatcher. No direct
   hardware transition. */

uint f33_dcm_session_2_callback(uchar operation,F33DcmMessageContext *message)

{
  uint uVar1;
  
  uVar1 = f33_dcm_session_operation(operation,message,'\x02');
  return uVar1;
}



/* Configured SID10 operation callback for target0x03; forwards operation/message plus fixed target
   inr8 to95C52. Callback return is ignored by existing F33DcmServiceCallback dispatcher. No direct
   hardware transition. */

uint f33_dcm_session_3_callback(uchar operation,F33DcmMessageContext *message)

{
  uint uVar1;
  
  uVar1 = f33_dcm_session_operation(operation,message,'\x03');
  return uVar1;
}



/* Configured SID10 operation callback for target0x40; forwards operation/message plus fixed target
   inr8 to95C52. Callback return is ignored by existing F33DcmServiceCallback dispatcher. No direct
   hardware transition. */

uint f33_dcm_session_64_callback(uchar operation,F33DcmMessageContext *message)

{
  uint uVar1;
  
  uVar1 = f33_dcm_session_operation(operation,message,'@');
  return uVar1;
}



undefined4 FUN_00095d4e(char param_1)

{
  if (param_1 == '\0') {
    thunk_FUN_0008b134();
  }
  return 0;
}



int FUN_00095d60(undefined1 param_1)

{
  uint32_t puVar1;
  int iVar2;
  ushort uStack_a;
  
  puVar1 = 0xfebeb800u;
  if (f33_dcm_read_route_kind == '\x01') {
    iVar2 = FUN_0009449e(f33_dcm_read_selected_class,f33_dcm_read_current_did,param_1,&uStack_a);
  }
  else {
    iVar2 = FUN_000944cc(f33_dcm_read_selected_class,&uStack_a);
  }
  if (iVar2 == 0) {
    FUN_000955b6(0);
    (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x5a8c)))) = (*((int *)camry_host_ptr((uint32_t)(puVar1 + -0x5a8c)))) + uStack_a + 2;
  }
  else if ((iVar2 == 1) || (iVar2 != 10)) {
    FUN_000955b6(0);
  }
  else {
    FUN_000955b6(1);
    f33_dcm_enqueue_event('\x1f');
  }
  return iVar2;
}



/* Read current session/security snapshots, apply class policy, then fixed local callback and length
   callback. Session rejection31 and security33 are distinct from metadata absence31 and whole-body
   capacity14. */

uint f33_dcm_check_read_did_policy_and_length(void)

{
  ushort uVar1;
  uint32_t puVar2;
  F33DcmMessageContext *message;
  uchar uVar3;
  int iVar4;
  uint uVar5;
  uchar uStack_13;
  uchar uStack_12;
  uchar uStack_11;
  
  uVar3 = f33_dcm_read_route_kind;
  uVar1 = f33_dcm_read_selected_class;
  puVar2 = 0xfebeb800u;
  uStack_11 = '\0';
  uStack_12 = '\0';
  uStack_13 = '\x01';
  f33_dcm_get_session(&uStack_13);
  iVar4 = FUN_000943ce(uVar1,uVar3,0x11,uStack_13);
  if (iVar4 == 0) {
    f33_dcm_get_security_level(&uStack_12);
    iVar4 = FUN_000943ce(uVar1,uVar3,0x12,uStack_12);
    if (iVar4 == 0) {
      if (uVar3 == '\x01') {
        iVar4 = FUN_00094fea(uVar1,0x10,(*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x5a84)))),&uStack_11);
      }
      else {
        iVar4 = FUN_000950c0(uVar1,0x10,&uStack_11);
      }
      if (iVar4 == 0) {
        uVar5 = FUN_00095d60(0);
        return uVar5;
      }
      if (iVar4 != 1) {
        return 1;
      }
      if (uStack_11 == '\0') {
        return 1;
      }
      message = ((F33DcmMessageContext *)camry_host_ptr((uint32_t)(puVar2 + -0x5a7c)));
      uVar3 = uStack_11;
    }
    else {
      message = ((F33DcmMessageContext *)camry_host_ptr((uint32_t)(puVar2 + -0x5a7c)));
      uVar3 = '3';
    }
  }
  else {
    message = ((F33DcmMessageContext *)camry_host_ptr((uint32_t)(puVar2 + -0x5a7c)));
    uVar3 = '1';
  }
  f33_dcm_report_negative_or_pending(message,uVar3);
  return 1;
}



uint FUN_00095e76(undefined1 param_1)

{
  uint32_t puVar1;
  int iVar2;
  uint uVar3;
  char cStack_9;
  
  puVar1 = 0xfebeb800u;
  uVar3 = 1;
  cStack_9 = '\x01';
  iVar2 = FUN_0009445a(f33_dcm_read_selected_class,f33_dcm_read_current_did,param_1,&cStack_9);
  if (iVar2 == 0) {
    FUN_000955b6(0);
    if (cStack_9 == '\0') {
      uVar3 = f33_dcm_check_read_did_policy_and_length();
    }
    else {
      f33_dcm_report_negative_or_pending(((F33DcmMessageContext *)camry_host_ptr((uint32_t)(puVar1 + -0x5a7c))),'1');
    }
  }
  else if (iVar2 == 10) {
    FUN_000955b6(1);
    f33_dcm_enqueue_event('\x04');
    uVar3 = 10;
  }
  else {
    FUN_000955b6(0);
  }
  return uVar3;
}



uint FUN_00095f78(void)

{
  uint32_t puVar1;
  uint uVar2;
  uint uVar3;
  
  puVar1 = 0xfebeb800u;
  uVar2 = f33_dcm_resolve_read_did_route();
  if (uVar2 == 0) {
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5a86))))) == '\x02') {
      uVar3 = f33_dcm_check_read_did_policy_and_length();
    }
    else {
      uVar3 = FUN_00095e76(0);
    }
  }
  else {
    uVar3 = 1;
    if (uVar2 == 1) {
      f33_dcm_report_negative_or_pending(((F33DcmMessageContext *)camry_host_ptr((uint32_t)(puVar1 + -0x5a7c))),'1');
    }
  }
  return uVar3;
}



/* Operation0 admits configured SID22;2 cancels retained read continuation. Other operations
   return0. Message snapshot, read preparation and serialization are separate from response
   delivery. */

uint f33_dcm_read_did_service(uchar operation,F33DcmMessageContext *message)

{
  uint uVar1;
  
  if (operation == '\0') {
    uVar1 = f33_dcm_begin_read_did_request(message);
  }
  else {
    uVar1 = 0;
    if (operation == '\x02') {
      uVar1 = FUN_00096244();
    }
  }
  return uVar1;
}



void FUN_00096312(void)

{
  f33_dcm_preflight_read_did_body('\x01');
  return;
}



void FUN_00096320(char param_1)

{
  f33_dcm_serialize_read_did_body(param_1 != '$');
  return;
}



void FUN_00096336(void)

{
  f33_dcm_preflight_read_did_body('\x02');
  return;
}



bool FUN_00096344(uint param_1,uint param_2)

{
  uint uVar1;
  
  for (uVar1 = 0; uVar1 < (param_2 & 0xff); uVar1 = uVar1 + 1 & 0xff) {
    DAT_febe5da4 = (uint)(*((byte *)camry_host_ptr((uint32_t)(uVar1 + (param_1 & 0xff) + DAT_febe5dac + 1)))) +
                   DAT_febe5da4 * 0x100;
  }
  return DAT_febe5da4 == 0 || (uint)(DAT_febe5dc0 - DAT_febe5db8) < DAT_febe5da4;
}



undefined4 FUN_00096388(uint param_1)

{
  uint uVar1;
  uint32_t puVar2;
  undefined4 uVar3;
  int iVar4;
  undefined4 uVar5;
  
  puVar2 = 0xfebeb800u;
  uVar5 = 1;
  if (DAT_00026154 == '\x01') {
    uVar3 = 0;
    DAT_febe5da8 = (*((undefined1 *)camry_host_ptr((uint32_t)(DAT_febe5dac + 1))));
    uVar1 = 1;
  }
  else {
    uVar1 = 0;
    uVar3 = 1;
  }
  for (; uVar1 < (param_1 & 0xff); uVar1 = uVar1 + 1 & 0xff) {
    DAT_febe5da0 = (uint)(*((byte *)camry_host_ptr((uint32_t)(DAT_febe5dac + uVar1 + 1)))) + DAT_febe5da0 * 0x100;
  }
  iVar4 = FUN_00094be2(0,DAT_febe5da0,uVar3,DAT_febe5da8,((undefined *)camry_host_ptr(0xfebe5da9u)),((undefined *)camry_host_ptr(0xfebe5daau)));
  if (iVar4 == 0) {
    iVar4 = FUN_00094cc4(0,(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x5a57))))),(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x5a56))))),(*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + -0x5a60)))),
                         (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + -0x5a5c)))));
    if (iVar4 == 0) {
      uVar5 = 0;
    }
    else {
      uVar5 = 1;
    }
  }
  return uVar5;
}



void FUN_00096582(void)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  iVar2 = FUN_000955bc();
  if (iVar2 == 1) {
    FUN_000965fc(2,(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5a58))))),(*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x5a60)))),
                 (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x5a5c)))),0,0);
    FUN_000955b6(0);
  }
  f33_dcm_invalidate_queued_event('#','\0');
  FUN_0009560e(1);
  return;
}



void FUN_000965ee(void)

{
  FUN_00096410(1);
  return;
}



undefined4
FUN_000965fc(char param_1,undefined1 param_2,undefined4 param_3,undefined4 param_4,
            undefined4 param_5,undefined4 param_6)

{
  undefined4 uVar1;
  
  if (param_1 == '\x02') {
    thunk_FUN_0008d4ae();
    uVar1 = 0;
  }
  else {
    uVar1 = FUN_0008d546(param_1, param_2, param_3, param_4, ((uchar *)camry_host_ptr((uint32_t)(param_5))), ((undefined1 *)camry_host_ptr((uint32_t)(param_6))));
  }
  return uVar1;
}



void FUN_00096622(uint param_1,char param_2)

{
  uint uVar1;
  
  if ((param_1 & 0xff) < 2) {
    uVar1 = 1 << (param_1 & 0x1f);
    if (param_2 == '\x01') {
      f33_app_security_delay_bits = f33_app_security_delay_bits | uVar1;
    }
    else {
      f33_app_security_delay_bits = f33_app_security_delay_bits & ~uVar1;
    }
  }
  return;
}



/* Cold module initializer clearsdelaymask andboth failures, arms configured initial10000 delays on
   timers7/8 and setsbits, then token/issuedflag0. Actual95590 init table26104 selects it. Does not
   itself clear application crypto buffers8D66A. */

void f33_dcm_security_initialize_delays(void)

{
  uint32_t puVar1;
  uint32_t puVar2;
  uint uVar3;
  int iVar4;
  
  puVar1 = 0xfebeb800u;
  puVar2 = 0x23dfcu;
  f33_app_security_delay_bits = 0;
  uVar3 = 0;
  do {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(uVar3 - 0x5a31))))) = 0;
    iVar4 = (short)uVar3 * 0x18;
    if ((*((int *)camry_host_ptr((uint32_t)(puVar2 + iVar4 + 0x2370)))) != 0) {
      f33_dcm_arm_software_timer((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(uVar3 * 2 + 0x235d))))),(*((uint *)camry_host_ptr((uint32_t)(puVar2 + iVar4 + 0x2370)))));
      FUN_00096622(uVar3,1);
    }
    uVar3 = uVar3 + 1;
  } while (uVar3 < 2);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5a33))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5a32))))) = 0;
  return;
}



/* Timer callback7/8 matches26159/2615B and clears respective5DC8 bit only;
   attempts/challenge/client/security/token unchanged. */

void f33_dcm_security_delay_expired(uchar timer_slot)

{
  uint uVar1;
  
  uVar1 = 0;
  do {
    if (timer_slot == (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x26159u + (uint32_t)(uVar1 * 2) * 1u))))) {
      FUN_00096622(uVar1,0);
      return;
    }
    uVar1 = uVar1 + 1;
  } while (uVar1 < 2);
  return;
}



void FUN_000968c6(void)

{
  f33_app_security_issued_level = '\0';
  return;
}



/* ROM25F48-selected application session callback. Exact instructions ignore both args: if5DCE==1
   clear5DCD and5DCE; otherwise retain token. No delay/failure reset and no challenge clear
   here;4D582 later owns application crypto reset. */

void f33_dcm_security_session_notification(uchar old_session,uchar new_session)

{
  if (f33_app_security_seed_callback_succeeded == '\x01') {
    f33_app_security_issued_level = '\0';
    f33_app_security_seed_callback_succeeded = '\0';
  }
  return;
}



/* Constant source: return 1; shape-classified from the canonical corpus. Callers receive this
   literal directly; its meaning is not recovered. */

undefined4 f33_return_const_1_968de(void)

{
  return 1;
}



/* Operation0\u2192968E2 seed admission,2\u219296990 cancellation; others return0. Actual third
   argument retained inr8 and consumed by968E2. Operation0→968E2 seed admission,2→96990
   cancellation; */

uint f33_dcm_security_seed_operation
               (uchar subfunction,uchar operation,F33DcmMessageContext *message)

{
  uint uVar1;
  
  if (operation == '\0') {
    uVar1 = f33_dcm_security_seed_request(subfunction,'\0',message);
  }
  else {
    uVar1 = 0;
    if (operation == '\x02') {
      uVar1 = f33_dcm_security_cancel_seed(subfunction,'\x02');
    }
  }
  return uVar1;
}



/* Operation0\u219296A04 key admission,2\u219296AB6 cancellation; others return0. Actual third
   argument retained inr8. Operation0→96A04 key admission,2→96AB6 cancellation; */

uint f33_dcm_security_key_operation(uchar subfunction,uchar operation,F33DcmMessageContext *message)

{
  uint uVar1;
  
  if (operation == '\0') {
    uVar1 = f33_dcm_security_key_request(subfunction,'\0',message);
  }
  else {
    uVar1 = 0;
    if (operation == '\x02') {
      uVar1 = f33_dcm_security_cancel_key(subfunction,'\x02');
    }
  }
  return uVar1;
}



/* Constant source: return 1; shape-classified from the canonical corpus. Callers receive this
   literal directly; its meaning is not recovered. */

undefined4 f33_return_const_1_96b24(void)

{
  return 1;
}



void FUN_00096b28(uchar *param_1,undefined4 param_2,uchar *param_3,uchar *param_4)

{
  f33_app_security_prepare_seed(param_1,param_3,param_4);
  return;
}



/* Constant source: return 1; shape-classified from the canonical corpus. Callers receive this
   literal directly; its meaning is not recovered. */

undefined4 f33_return_const_1_96b38(void)

{
  return 1;
}



void FUN_00096b3c(uchar *param_1)

{
  f33_app_security_compare_key(param_1);
  return;
}



/* Configured SID27 sub1; wrapper preserves message inr8, moves operation tor7 and fixedsubfunction
   tor6. Level=(sub+1)>>1. Odd seed dispatch969E4, even key96B04; r8 carries the consumed message
   pointer. r8 message is real despite missing corpus parameters. */

uint f33_dcm_security_sub1_callback(uchar operation,F33DcmMessageContext *message)

{
  uint uVar1;
  
  uVar1 = f33_dcm_security_seed_operation('\x01',operation,message);
  return uVar1;
}



/* Configured SID27 sub2; wrapper preserves message inr8, moves operation tor7 and fixedsubfunction
   tor6. Level=(sub+1)>>1. Odd seed dispatch969E4, even key96B04; r8 carries the consumed message
   pointer. r8 message is real despite missing corpus parameters. */

uint f33_dcm_security_sub2_callback(uchar operation,F33DcmMessageContext *message)

{
  uint uVar1;
  
  uVar1 = f33_dcm_security_key_operation('\x02',operation,message);
  return uVar1;
}



/* Configured SID27 sub3; wrapper preserves message inr8, moves operation tor7 and fixedsubfunction
   tor6. Level=(sub+1)>>1. Odd seed dispatch969E4, even key96B04; r8 carries the consumed message
   pointer. r8 message is real despite missing corpus parameters. */

uint f33_dcm_security_sub3_callback(uchar operation,F33DcmMessageContext *message)

{
  uint uVar1;
  
  uVar1 = f33_dcm_security_seed_operation('\x03',operation,message);
  return uVar1;
}



/* Configured SID27 sub4; wrapper preserves message inr8, moves operation tor7 and fixedsubfunction
   tor6. Level=(sub+1)>>1. Odd seed dispatch969E4, even key96B04; r8 carries the consumed message
   pointer. r8 message is real despite missing corpus parameters. */

uint f33_dcm_security_sub4_callback(uchar operation,F33DcmMessageContext *message)

{
  uint uVar1;
  
  uVar1 = f33_dcm_security_key_operation('\x04',operation,message);
  return uVar1;
}



/* Invalidateallqueued26hentriesandclear5D24sentinel;no8196rollbackorcontrollerstop/start. */

void f33_dcm_cancel_communication_continuation(void)

{
  f33_dcm_invalidate_queued_event('&','\0');
  FUN_0009560e(1);
  return;
}



/* Operation0 starts96E6A;2 removes queued26h continuation and clears diagnostic sentinel, not
   retained policy; otheroperationsreturn0. */

uint f33_dcm_dispatch_communication_control_lifetime
               (uchar operation,F33DcmMessageContext *message,uchar subfunction)

{
  uint uVar1;
  
  if (operation == '\0') {
    uVar1 = f33_dcm_begin_configured_communication_request(message,subfunction);
  }
  else {
    uVar1 = 0;
    if (operation == '\x02') {
      f33_dcm_cancel_communication_continuation();
    }
  }
  return uVar1;
}



/* Forward the fourth R9 NRC pointer to8DA10 and return its meaningful R10 admission result.
   Preserve fourth R9argumentandmeaningfulreturn from8DA10;currentvoid/3args hides NRCwrite. */

uint f33_dcm_check_communication_application_admission
               (uchar subfunction,uchar communication_type,ushort node,uchar *nrc)

{
  uint uVar1;
  
  uVar1 = f33_admit_application_communication_request(subfunction,communication_type,node,nrc);
  return uVar1;
}



void FUN_00097128(uchar param_1,uchar param_2)

{
  f33_apply_and_complete_communication_policy_request(param_1,param_2);
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_97138(void)

{
  return;
}



/* Constant source: return 0; shape-classified from the canonical corpus. Callers receive this
   literal directly; its meaning is not recovered. */

undefined4 f33_return_const_0_9713a(void)

{
  return 0;
}



/* Constant source: return 0xb; shape-classified from the canonical corpus. Callers receive this
   literal directly; its meaning is not recovered. */

undefined4 f33_return_const_b_9713e(void)

{
  return 0xb;
}



/* ConfiguredSID28sub0/session3 wrapper; shared9701C lifetime, only communicationByte01 admitted by
   image. */

uint f33_dcm_communication_enable_rx_tx(uchar operation,F33DcmMessageContext *message)

{
  uint uVar1;
  
  uVar1 = f33_dcm_dispatch_communication_control_lifetime(operation,message,'\0');
  return uVar1;
}



/* ConfiguredSID28sub1/session3; application effect is retained8196Tx-policy request, not controller
   confirmation or7F97. */

uint f33_dcm_communication_enable_rx_disable_tx(uchar operation,F33DcmMessageContext *message)

{
  uint uVar1;
  
  uVar1 = f33_dcm_dispatch_communication_control_lifetime(operation,message,'\x01');
  return uVar1;
}



/* Configuredsub3 name describes request only; actual local actionusesmappedmodebit0 and does not
   independently implement Rxdisable. */

uint f33_dcm_communication_disable_rx_tx_request(uchar operation,F33DcmMessageContext *message)

{
  uint uVar1;
  
  uVar1 = f33_dcm_dispatch_communication_control_lifetime(operation,message,'\x03');
  return uVar1;
}



bool FUN_00097172(ushort param_1,undefined2 *param_2)

{
  ushort uVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  
  if (DAT_00026492 != 0) {
    uVar4 = 0;
    uVar3 = (uint)(ushort)(DAT_00026492 - 1);
    if ((DAT_00026918 <= param_1) && (uVar1 = DAT_00026918, param_1 <= (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x26918u + (uint32_t)(uVar3 * 4) * 2u))))))
    {
      while( true ) {
        if (uVar1 == param_1) {
          *param_2 = (short)uVar4;
          return (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2691bu + (uint32_t)(uVar4 * 8) * 1u)))) != '\x01';
        }
        if (uVar3 <= uVar4) break;
        uVar2 = uVar3 + uVar4 >> 1;
        if ((*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x26918u + (uint32_t)(uVar2 * 4) * 2u)))) < param_1) {
          uVar4 = uVar2 + 1 & 0xffff;
          uVar2 = uVar3;
        }
        uVar3 = uVar2;
        uVar1 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x26918u + (uint32_t)(uVar4 * 4) * 2u))));
      }
    }
  }
  return true;
}



undefined4 FUN_000971e8(ushort param_1)

{
  int iVar1;
  uint uVar2;
  uint32_t puVar3;
  uint uVar4;
  uchar uStack_11;
  
  puVar3 = 0x23dfcu;
  uVar4 = (uint)param_1;
  if (DAT_00026492 <= uVar4) {
    return 1;
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x269b9u + (uint32_t)((short)param_1 * 0xf) * 1u)))) != '\0') {
    if (1 < *(ushort *)(((undefined *)camry_host_ptr(0x264bcu)) + uVar4 * 2)) {
      return 1;
    }
    iVar1 = (uint)*(ushort *)(((undefined *)camry_host_ptr(0x264bcu)) + uVar4 * 2) * 2;
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2624du + (uint32_t)(iVar1) * 1u)))) != '\0') {
      uStack_11 = '\0';
      f33_dcm_get_session(&uStack_11);
      uVar2 = 0;
      while( true ) {
        if ((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2624du + (uint32_t)(iVar1) * 1u)))) <= uVar2) {
          return 1;
        }
        if ((*((uchar *)camry_host_ptr((uint32_t)(*(int *)(uVar2 * 4 + *(int *)(*(int *)(puVar3 + uVar4 * 8 + 0x2b20) + 4)) + 1
                      )))) == uStack_11) break;
        uVar2 = uVar2 + 1 & 0xffff;
      }
    }
  }
  return 0;
}



undefined4 FUN_0009726c(ushort param_1)

{
  int iVar1;
  uint uVar2;
  uint32_t puVar3;
  uint uVar4;
  uchar uStack_11;
  
  puVar3 = 0x23dfcu;
  uVar4 = (uint)param_1;
  if (DAT_00026492 <= uVar4) {
    return 1;
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x269b9u + (uint32_t)((short)param_1 * 0xf) * 1u)))) != '\0') {
    if (1 < *(ushort *)(((undefined *)camry_host_ptr(0x264bcu)) + uVar4 * 2)) {
      return 1;
    }
    iVar1 = (uint)*(ushort *)(((undefined *)camry_host_ptr(0x264bcu)) + uVar4 * 2) * 2;
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2624cu + (uint32_t)(iVar1) * 1u)))) != '\0') {
      uStack_11 = '\0';
      f33_dcm_get_security_level(&uStack_11);
      uVar2 = 0;
      while( true ) {
        if ((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2624cu + (uint32_t)(iVar1) * 1u)))) <= uVar2) {
          return 1;
        }
        if ((*((uchar *)camry_host_ptr((uint32_t)(*(int *)(uVar2 * 4 + **(int **)(puVar3 + uVar4 * 8 + 0x2b20)) + 0x14)))) ==
            uStack_11) break;
        uVar2 = uVar2 + 1 & 0xffff;
      }
    }
  }
  return 0;
}



/* 269B9+15*index offsets4/9/1 forcontrols1/2/3;0supported,1rejected;indexbound26492. */

uint f33_diag_routine_control_type_supported(ushort configured_index,uchar control_type)

{
  char cVar1;
  uint uVar2;
  
  uVar2 = 1;
  if (configured_index < DAT_00026492) {
    if (control_type == '\x01') {
      cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x269bdu + (uint32_t)((short)configured_index * 0xf) * 1u))));
    }
    else if (control_type == '\x02') {
      cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x269c2u + (uint32_t)((short)configured_index * 0xf) * 1u))));
    }
    else {
      if (control_type != '\x03') {
        return uVar2;
      }
      cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x269bau + (uint32_t)((short)configured_index * 0xf) * 1u))));
    }
    if (cVar1 == '\0') {
      return uVar2;
    }
    uVar2 = 0;
  }
  return uVar2;
}



bool FUN_0009733a(int param_1,ushort param_2,char param_3)

{
  undefined **ppuVar1;
  uint uVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  undefined *puVar6;
  undefined *puVar7;
  
  uVar5 = (uint)param_2;
  if (DAT_00026492 <= uVar5) {
    return true;
  }
  uVar2 = 0;
  if (param_3 == '\x01') {
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x269bfu + (uint32_t)((short)param_2 * 0xf) * 1u)))) == 0) goto LAB_000973ce;
    ppuVar1 = &PTR_DAT_00026698 + uVar5;
    iVar3 = (short)(ushort)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x269bfu + (uint32_t)((short)param_2 * 0xf) * 1u)))) * 6;
    iVar4 = iVar3 + -6;
    puVar6 = *ppuVar1;
    puVar7 = *ppuVar1;
    if ((*ppuVar1)[iVar3 + -5] == '\a') goto LAB_000973be;
LAB_000973b0:
    puVar6 = puVar6 + iVar4;
    uVar5 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x261d8u + (uint32_t)((byte)puVar7[iVar4 + 1]) * 1u))));
  }
  else {
    if ((param_3 != '\x02') || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x269c4u + (uint32_t)((short)param_2 * 0xf) * 1u)))) == 0)) goto LAB_000973ce;
    ppuVar1 = &PTR_DAT_000267d8 + uVar5;
    iVar3 = (short)(ushort)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x269c4u + (uint32_t)((short)param_2 * 0xf) * 1u)))) * 6;
    iVar4 = iVar3 + -6;
    puVar6 = *ppuVar1;
    puVar7 = *ppuVar1;
    if ((*ppuVar1)[iVar3 + -5] != '\a') goto LAB_000973b0;
LAB_000973be:
    puVar6 = puVar6 + iVar4;
    uVar5 = (uint)*(ushort *)(puVar7 + iVar4 + 2);
  }
  uVar2 = uVar5 + *(ushort *)(puVar6 + 4) + 7 >> 3;
LAB_000973ce:
  return uVar2 + 3 != (*((int *)camry_host_ptr((uint32_t)(param_1 + 4))));
}



bool FUN_000973dc(int param_1,ushort param_2,char param_3)

{
  undefined **ppuVar1;
  char cVar2;
  uint uVar3;
  int iVar4;
  uint uVar5;
  undefined *puVar6;
  undefined *puVar7;
  
  uVar5 = (uint)param_2;
  if (DAT_00026492 <= uVar5) {
    return true;
  }
  uVar3 = 0;
  if (param_3 == '\x01') {
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x269c1u + (uint32_t)((short)param_2 * 0xf) * 1u)))) == 0) goto LAB_000974a2;
    ppuVar1 = &PTR_DAT_000266e8 + uVar5;
    iVar4 = (short)(ushort)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x269c1u + (uint32_t)((short)param_2 * 0xf) * 1u)))) * 6;
    cVar2 = (*ppuVar1)[iVar4 + -5];
    puVar6 = *ppuVar1;
    puVar7 = *ppuVar1;
  }
  else if (param_3 == '\x02') {
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x269c6u + (uint32_t)((short)param_2 * 0xf) * 1u)))) == 0) goto LAB_000974a2;
    ppuVar1 = &PTR_DAT_00026828 + uVar5;
    iVar4 = (short)(ushort)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x269c6u + (uint32_t)((short)param_2 * 0xf) * 1u)))) * 6;
    cVar2 = (*ppuVar1)[iVar4 + -5];
    puVar6 = *ppuVar1;
    puVar7 = *ppuVar1;
  }
  else {
    if ((param_3 != '\x03') || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x269bcu + (uint32_t)((short)param_2 * 0xf) * 1u)))) == 0)) goto LAB_000974a2;
    ppuVar1 = &PTR_DAT_000265f8 + uVar5;
    iVar4 = (short)(ushort)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x269bcu + (uint32_t)((short)param_2 * 0xf) * 1u)))) * 6;
    cVar2 = (*ppuVar1)[iVar4 + -5];
    puVar6 = *ppuVar1;
    puVar7 = *ppuVar1;
  }
  if (cVar2 == '\a') {
    uVar5 = (uint)*(ushort *)(puVar7 + iVar4 + -4);
  }
  else {
    uVar5 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x261d8u + (uint32_t)((byte)puVar7[iVar4 + -5]) * 1u))));
  }
  uVar3 = uVar5 + *(ushort *)(puVar6 + iVar4 + -2) + 7 >> 3;
LAB_000974a2:
  return (*((uint *)camry_host_ptr((uint32_t)(param_1 + 0x14)))) < uVar3 + 3;
}



void FUN_0009767c(ushort param_1,char param_2,int param_3)

{
  char *pcVar1;
  undefined2 uVar2;
  undefined **ppuVar3;
  uint uVar4;
  undefined *puVar5;
  undefined *puVar6;
  char cVar7;
  short sVar8;
  uint uVar9;
  undefined1 uVar10;
  uint uVar11;
  undefined1 uVar12;
  undefined **ppuVar13;
  int iVar14;
  
  uVar4 = (uint)param_1;
  if (uVar4 < DAT_00026492) {
    iVar14 = (short)param_1 * 0xf;
    if (param_2 == '\x01') {
      uVar9 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x269c1u + (uint32_t)(iVar14) * 1u))));
      ppuVar3 = &PTR_DAT_000266e8;
      ppuVar13 = &PTR_DAT_00026788;
    }
    else if (param_2 == '\x02') {
      uVar9 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x269c6u + (uint32_t)(iVar14) * 1u))));
      ppuVar3 = &PTR_DAT_00026828;
      ppuVar13 = &PTR_DAT_000268c8;
    }
    else {
      uVar9 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x269bcu + (uint32_t)(iVar14) * 1u))));
      ppuVar3 = &PTR_DAT_000265f8;
      ppuVar13 = &PTR_DAT_00026648;
    }
    puVar6 = ppuVar3[uVar4];
    puVar5 = ppuVar13[uVar4];
    for (uVar4 = 0; uVar4 < uVar9; uVar4 = uVar4 + 1 & 0xff) {
      pcVar1 = puVar6 + (short)uVar4 * 6;
      iVar14 = ((int)(uint)*(ushort *)(pcVar1 + 4) >> 3) + 3;
      if (pcVar1[1] != '\a') {
        if (pcVar1[1] == '\0') {
          (*((byte *)camry_host_ptr((uint32_t)(DAT_febe5e20 + iVar14)))) =
               (*((byte *)camry_host_ptr((uint32_t)(DAT_febe5e20 + iVar14)))) |
               (byte)((*((int *)camry_host_ptr((uint32_t)(uVar4 * 4 + param_3)))) << (*(ushort *)(pcVar1 + 4) & 7));
        }
        else if ((pcVar1[1] == '\x06') || (pcVar1[1] == '\x03')) {
          (*((char *)camry_host_ptr((uint32_t)(DAT_febe5e20 + iVar14)))) = (char)(*((undefined4 *)camry_host_ptr((uint32_t)(uVar4 * 4 + param_3))));
        }
        else {
          if ((puVar5[uVar4 * 2] == '\0') || (*pcVar1 == '\x02')) {
            cVar7 = '\x01';
          }
          else {
            cVar7 = *pcVar1;
          }
          if ((pcVar1[1] == '\x04') || (pcVar1[1] == '\x01')) {
            uVar2 = (*((undefined2 *)camry_host_ptr((uint32_t)(uVar4 * 4 + param_3))));
            uVar12 = (undefined1)((ushort)uVar2 >> 8);
            uVar10 = (undefined1)uVar2;
            if (cVar7 == '\x01') {
              (*((undefined1 *)camry_host_ptr((uint32_t)(DAT_febe5e20 + iVar14)))) = uVar10;
              (*((undefined1 *)camry_host_ptr((uint32_t)(DAT_febe5e20 + iVar14 + 1)))) = uVar12;
            }
            else {
              (*((undefined1 *)camry_host_ptr((uint32_t)(DAT_febe5e20 + iVar14)))) = uVar12;
              (*((undefined1 *)camry_host_ptr((uint32_t)(DAT_febe5e20 + iVar14 + 1)))) = uVar10;
            }
          }
          else {
            uVar11 = (*((uint *)camry_host_ptr((uint32_t)(uVar4 * 4 + param_3))));
            uVar10 = (undefined1)(uVar11 >> 0x10);
            uVar12 = (undefined1)(uVar11 >> 8);
            if (cVar7 == '\x01') {
              (*((undefined1 *)camry_host_ptr((uint32_t)(DAT_febe5e20 + iVar14)))) = (char)uVar11;
              uVar11 = uVar11 >> 0x18;
              (*((undefined1 *)camry_host_ptr((uint32_t)(DAT_febe5e20 + iVar14 + 1)))) = uVar12;
              (*((undefined1 *)camry_host_ptr((uint32_t)(DAT_febe5e20 + iVar14 + 2)))) = uVar10;
            }
            else {
              (*((undefined1 *)camry_host_ptr((uint32_t)(DAT_febe5e20 + iVar14)))) = (char)(uVar11 >> 0x18);
              (*((undefined1 *)camry_host_ptr((uint32_t)(DAT_febe5e20 + iVar14 + 1)))) = uVar10;
              (*((undefined1 *)camry_host_ptr((uint32_t)(DAT_febe5e20 + iVar14 + 2)))) = uVar12;
            }
            (*((char *)camry_host_ptr((uint32_t)(DAT_febe5e20 + iVar14 + 3)))) = (char)uVar11;
          }
        }
      }
    }
    if (uVar9 != 0) {
      sVar8 = (short)uVar9;
      if (puVar6[sVar8 * 6 + -5] == '\a') {
        uVar4 = (uint)*(ushort *)(puVar6 + sVar8 * 6 + -4);
      }
      else {
        uVar4 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x261d8u + (uint32_t)((byte)puVar6[sVar8 * 6 + -5]) * 1u))));
      }
      DAT_febe5e24 = DAT_febe5e24 + (uVar4 + *(ushort *)(puVar6 + sVar8 * 6 + -2) + 7 >> 3);
    }
  }
  return;
}



/* UDS routine wrapper: guards on the two valid routine-control subfunctions, delegates to the
   application-class routine helper with a fixed class literal, and diverts other subfunctions to
   the negative-response path (8B83C). Shape-verified. */

uint f33_diag_routine_class03_97b2c(byte param_1,uchar *param_2,uchar *param_3)

{
  uint uVar1;
  ushort uStack_a;
  
  uStack_a = 0;
  if (param_1 < 2) {
    uVar1 = f33_diag_routine_application_class('\x03',0,0,param_2,&uStack_a,param_3);
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

uint f33_diag_routine_class03_97b60(byte param_1,uchar *param_2,uchar *param_3)

{
  uint uVar1;
  ushort uStack_a;
  
  uStack_a = 0;
  if (param_1 < 2) {
    uVar1 = f33_diag_routine_application_class('\x03',1,0,param_2,&uStack_a,param_3);
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

uint f33_diag_routine_class03_97b94(byte param_1,uchar *param_2,uchar *param_3)

{
  uint uVar1;
  ushort uStack_a;
  
  uStack_a = 0;
  if (param_1 < 2) {
    uVar1 = f33_diag_routine_application_class('\x03',2,0,param_2,&uStack_a,param_3);
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

uint f33_diag_routine_class03_97bc8(byte param_1,uchar *param_2,uchar *param_3)

{
  uint uVar1;
  ushort uStack_a;
  
  uStack_a = 0;
  if (param_1 < 2) {
    uVar1 = f33_diag_routine_application_class('\x03',3,0,param_2,&uStack_a,param_3);
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

uint f33_diag_routine_class03_97bfc(byte param_1,uchar *param_2,uchar *param_3)

{
  uint uVar1;
  ushort uStack_a;
  
  uStack_a = 0;
  if (param_1 < 2) {
    uVar1 = f33_diag_routine_application_class('\x03',4,0,param_2,&uStack_a,param_3);
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

uint f33_diag_routine_class03_97c30(byte param_1,uchar *param_2,uchar *param_3)

{
  uint uVar1;
  ushort uStack_a;
  
  uStack_a = 0;
  if (param_1 < 2) {
    uVar1 = f33_diag_routine_application_class('\x03',5,0,param_2,&uStack_a,param_3);
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

uint f33_diag_routine_class03_97c64(byte param_1,uchar *param_2,uchar *param_3)

{
  uint uVar1;
  ushort uStack_a;
  
  uStack_a = 0;
  if (param_1 < 2) {
    uVar1 = f33_diag_routine_application_class('\x03',6,0,param_2,&uStack_a,param_3);
  }
  else {
    uVar1 = 0;
    FUN_0008b83c();
  }
  return uVar1;
}



undefined4 FUN_00097c98(char param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  
  if (param_1 == '\0') {
    uVar1 = FUN_0008ba2c(param_2, 0x31, ((uchar *)camry_host_ptr((uint32_t)(param_4))));
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

uint f33_diag_routine_class03_97cbc(byte param_1,uchar *param_2,uchar *param_3)

{
  uint uVar1;
  ushort uStack_a;
  
  uStack_a = 0;
  if (param_1 < 2) {
    uVar1 = f33_diag_routine_application_class('\x03',10,0,param_2,&uStack_a,param_3);
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

uint f33_diag_routine_class03_97cf0(byte param_1,uchar *param_2,uchar *param_3)

{
  uint uVar1;
  ushort uStack_a;
  
  uStack_a = 0;
  if (param_1 < 2) {
    uVar1 = f33_diag_routine_application_class('\x03',0xb,0,param_2,&uStack_a,param_3);
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

uint f33_diag_routine_class03_97d24(byte param_1,uchar *param_2,uchar *param_3)

{
  uint uVar1;
  ushort uStack_a;
  
  uStack_a = 0;
  if (param_1 < 2) {
    uVar1 = f33_diag_routine_application_class('\x03',0xc,0,param_2,&uStack_a,param_3);
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

uint f33_diag_routine_class03_97d58(byte param_1,uchar *param_2,uchar *param_3)

{
  uint uVar1;
  ushort uStack_a;
  
  uStack_a = 0;
  if (param_1 < 2) {
    uVar1 = f33_diag_routine_application_class('\x03',0xd,0,param_2,&uStack_a,param_3);
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

uint f33_diag_routine_class03_97d8c(byte param_1,uchar *param_2,uchar *param_3)

{
  uint uVar1;
  ushort uStack_a;
  
  uStack_a = 0;
  if (param_1 < 2) {
    uVar1 = f33_diag_routine_application_class('\x03',0xe,0,param_2,&uStack_a,param_3);
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

uint f33_diag_routine_class03_97dc0(byte param_1,uchar *param_2,uchar *param_3)

{
  uint uVar1;
  ushort uStack_a;
  
  uStack_a = 0;
  if (param_1 < 2) {
    uVar1 = f33_diag_routine_application_class('\x03',0xf,0,param_2,&uStack_a,param_3);
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

uint f33_diag_routine_class03_97df4(byte param_1,uchar *param_2,uchar *param_3)

{
  uint uVar1;
  ushort uStack_a;
  
  uStack_a = 0;
  if (param_1 < 2) {
    uVar1 = f33_diag_routine_application_class('\x03',0x10,0,param_2,&uStack_a,param_3);
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

uint f33_diag_routine_class03_97e2a(byte param_1,uchar *param_2,uchar *param_3)

{
  uint uVar1;
  ushort uStack_a;
  
  uStack_a = 0;
  if (param_1 < 2) {
    uVar1 = f33_diag_routine_application_class('\x03',0x11,0,param_2,&uStack_a,param_3);
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

uint f33_diag_routine_class03_97e60(byte param_1,uchar *param_2,uchar *param_3)

{
  uint uVar1;
  ushort uStack_a;
  
  uStack_a = 0;
  if (param_1 < 2) {
    uVar1 = f33_diag_routine_application_class('\x03',0x12,0,param_2,&uStack_a,param_3);
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

uint f33_diag_routine_class01_97e96(byte param_1,uchar *param_2,ushort *param_3,uchar *param_4)

{
  uint uVar1;
  
  if (param_1 < 2) {
    uVar1 = f33_diag_routine_application_class('\x01',0,0,param_2,param_3,param_4);
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

uint f33_diag_routine_class01_97ec2(byte param_1,uchar *param_2,ushort *param_3,uchar *param_4)

{
  uint uVar1;
  
  if (param_1 < 2) {
    uVar1 = f33_diag_routine_application_class('\x01',1,0,param_2,param_3,param_4);
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

uint f33_diag_routine_class01_97eee(byte param_1,uchar *param_2)

{
  uint uVar1;
  uchar uStack_b;
  ushort uStack_a;
  
  uStack_b = '\0';
  uStack_a = 0;
  if (param_1 < 2) {
    uVar1 = f33_diag_routine_application_class('\x01',2,0,&uStack_b,&uStack_a,param_2);
  }
  else {
    uVar1 = 0;
    FUN_0008b83c();
  }
  return uVar1;
}



uint FUN_00097f24(uint param_1,byte param_2,uchar *param_3)

{
  uint uVar1;
  uchar uStack_b;
  ushort uStack_a;
  
  uStack_b = '\0';
  uStack_a = 0;
  if (param_2 < 2) {
    uVar1 = f33_diag_routine_application_class
                      ('\x01',3,param_1 & 0xffff,&uStack_b,&uStack_a,param_3);
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

uint f33_diag_routine_class01_97f5c(byte param_1,uchar *param_2)

{
  uint uVar1;
  uchar uStack_b;
  ushort uStack_a;
  
  uStack_b = '\0';
  uStack_a = 0;
  if (param_1 < 2) {
    uVar1 = f33_diag_routine_application_class('\x01',4,0,&uStack_b,&uStack_a,param_2);
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

uint f33_diag_routine_class01_97f92(byte param_1,uchar *param_2)

{
  uint uVar1;
  uchar uStack_b;
  ushort uStack_a;
  
  uStack_b = '\0';
  uStack_a = 0;
  if (param_1 < 2) {
    uVar1 = f33_diag_routine_application_class('\x01',5,0,&uStack_b,&uStack_a,param_2);
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

uint f33_diag_routine_class01_97fc8(byte param_1,uchar *param_2)

{
  uint uVar1;
  uchar uStack_b;
  ushort uStack_a;
  
  uStack_b = '\0';
  uStack_a = 0;
  if (param_1 < 2) {
    uVar1 = f33_diag_routine_application_class('\x01',6,0,&uStack_b,&uStack_a,param_2);
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

uint f33_diag_routine_class01_97ffe(byte param_1,uchar *param_2)

{
  uint uVar1;
  uchar uStack_b;
  ushort uStack_a;
  
  uStack_b = '\0';
  uStack_a = 0;
  if (param_1 < 2) {
    uVar1 = f33_diag_routine_application_class('\x01',7,0,&uStack_b,&uStack_a,param_2);
  }
  else {
    uVar1 = 0;
    FUN_0008b83c();
  }
  return uVar1;
}


