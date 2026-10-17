#include "common.h"


/* Preserve group/message, call8C018(message,group), and on success8C104(message,group). Return
   consequentialR10 from last phase without manufacturing success;8C2A8 retains it. */

uint f33_dcm_join_clear_diagnostic_phases(uint group,F33DcmMessageContext *message)

{
  uint uVar1;
  
  uVar1 = FUN_0008c018(message,group);
  if (uVar1 == 0) {
    uVar1 = FUN_0008c104(message,group);
  }
  return uVar1;
}



void FUN_0008c2c4(void)

{
  f33_fill_constant_block_8bfea();
  f33_dcm_cancel_service_events(0xeb,'\0');
  FUN_0009560e(1);
  return;
}



/* Clear service operation callback. Retain advanced message for operation0; nonzero operations
   reset/cancel module state. Response submission is not acknowledgement or durable completion. */

uint f33_dcm_clear_diagnostic_service(uchar operation,F33DcmMessageContext *message)

{
  uint uVar1;
  
  if (operation == '\0') {
    uVar1 = f33_dcm_begin_clear_diagnostic_request(message);
  }
  else {
    uVar1 = 0;
    FUN_0008c2c4();
  }
  return uVar1;
}



void FUN_0008c318(void)

{
  uint uVar1;
  
  DAT_febf3bf8 = 0xff;
  DAT_febf3bf7 = 0;
  DAT_febf3bf2 = 0;
  DAT_febf3bf6 = 0;
  DAT_febf3bf5 = 0;
  DAT_febf3bf4 = 0;
  uVar1 = 0;
  do {
    f33_dtc_count_local_tuple_scratch[uVar1] = '\0';
    uVar1 = uVar1 + 1;
  } while (uVar1 < 0x300);
  DAT_febf3bf9 = 0;
  return;
}



void FUN_0008c368(void)

{
  FUN_0008c318();
  f33_dcm_cancel_service_events(0xec,'\0');
  FUN_0009560e(1);
  return;
}



/* Forward status mask to4D69C and retain unmasked byte3BF5. Preserve returnedR10 through final
   store/dispose; caller8C66A checks it. */

uint f33_begin_dtc_count_iteration(uchar mask)

{
  uint uVar1;
  
  uVar1 = f33_begin_filtered_dtc_iteration(mask);
  DAT_febf3bf5 = mask;
  return uVar1;
}



bool FUN_0008c3c0(int param_1,ushort *param_2,undefined1 *param_3)

{
  uint uVar1;
  uchar uStack_15;
  uint uStack_14;
  
  uVar1 = f33_next_filtered_dtc(&uStack_14,&uStack_15);
  if (uVar1 == 0) {
    (*((char *)camry_host_ptr((uint32_t)((uint)*param_2 + param_1)))) = (char)(uStack_14 >> 0x10);
    (*((char *)camry_host_ptr((uint32_t)((uint)*param_2 + param_1 + 1)))) = (char)(uStack_14 >> 8);
    (*((char *)camry_host_ptr((uint32_t)((uint)*param_2 + param_1 + 2)))) = (char)uStack_14;
    (*((uchar *)camry_host_ptr((uint32_t)((uint)*param_2 + param_1 + 3)))) = uStack_15;
    *param_2 = *param_2 + 4;
  }
  *param_3 = (char)uVar1;
  return uVar1 != 0;
}



bool FUN_0008c790(int param_1,ushort *param_2,undefined1 *param_3)

{
  uint uVar1;
  uchar uStack_15;
  uint uStack_14;
  
  uVar1 = f33_next_filtered_dtc(&uStack_14,&uStack_15);
  if (uVar1 == 0) {
    (*((char *)camry_host_ptr((uint32_t)((uint)*param_2 + param_1)))) = (char)(uStack_14 >> 0x10);
    (*((char *)camry_host_ptr((uint32_t)((uint)*param_2 + param_1 + 1)))) = (char)(uStack_14 >> 8);
    (*((char *)camry_host_ptr((uint32_t)((uint)*param_2 + param_1 + 2)))) = (char)uStack_14;
    (*((uchar *)camry_host_ptr((uint32_t)((uint)*param_2 + param_1 + 3)))) = uStack_15;
    *param_2 = *param_2 + 4;
  }
  *param_3 = (char)uVar1;
  return uVar1 != 0;
}



/* Reset DTC-list scratch/phase/yield state, tombstone all queuedED slots and release shared
   diagnostic continuation token through9560E(1). Ring occupancy is retained until dispatch pops
   tombstones. */

void f33_dcm_cancel_retained_dtc_list(void)

{
  FUN_0008c70c();
  f33_dcm_cancel_service_events(0xed,'\0');
  FUN_0009560e(1);
  return;
}



/* Constant-block fill: 6 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_8cb8c(void)

{
  DAT_febf4247 = 0xff;
  DAT_febf4246 = 0;
  DAT_febf4242 = 0;
  DAT_febf4240 = 0;
  DAT_febf4245 = 0;
  DAT_febf4244 = 0;
  return;
}



/* Constant source: return 0; shape-classified from the canonical corpus. Callers receive this
   literal directly; its meaning is not recovered. */

undefined4 f33_return_const_0_8cbc0(void)

{
  return 0;
}



undefined4 FUN_0008cbc4(int param_1,ushort *param_2,undefined1 *param_3)

{
  undefined1 *puVar1;
  ushort uVar2;
  uint uVar3;
  undefined4 uVar4;
  uchar uStack_19;
  uint uStack_18;
  
  uVar2 = *param_2;
  uVar3 = f33_next_snapshot_identifier_tuple(&uStack_18,&uStack_19);
  if (uVar3 == 0) {
    puVar1 = ((undefined1 *)camry_host_ptr((uint32_t)((uint)uVar2 + param_1)));
    puVar1[2] = (char)uStack_18;
    *puVar1 = (char)(uStack_18 >> 0x10);
    puVar1[1] = (char)(uStack_18 >> 8);
    puVar1[3] = uStack_19;
    *param_2 = uVar2 + 4;
    uVar4 = 0;
  }
  else {
    uVar4 = 0x5a;
  }
  *param_3 = (char)uVar3;
  return uVar4;
}



void FUN_0008ce68(void)

{
  f33_dcm_cancel_service_events(0xee,'\0');
  FUN_0009560e(1);
  f33_fill_constant_block_8cb8c();
  return;
}



/* EventEE re-enters8CCB8 using that module's retained state and existing message4248. */

void f33_dcm_resume_queued_snapshot_identifiers(void)

{
  FUN_0008ccb8();
  return;
}



/* Constant-block fill: 19 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_8cef0(void)

{
  DAT_febf4571 = 0;
  DAT_febf4570 = 0;
  DAT_febf456f = 0;
  DAT_febf456e = 0;
  DAT_febf456a = 0;
  DAT_febf4568 = 0;
  DAT_febf456d = 1;
  DAT_febf456c = 1;
  DAT_febf4577 = 0;
  DAT_febf4576 = 0;
  DAT_febf4575 = 0;
  DAT_febf4574 = 0;
  DAT_febf4573 = 0;
  DAT_febf4564 = 0;
  DAT_febf4572 = 0xff;
  DAT_febf457b = 0;
  DAT_febf457a = 0;
  DAT_febf4579 = 0;
  DAT_febf4578 = 0;
  return;
}



bool FUN_0008cf8e(undefined4 param_1,int *param_2)

{
  int iVar1;
  undefined1 uStack_9;
  
  uStack_9 = 0;
  iVar1 = FUN_0004d79a(param_1,0,&uStack_9);
  if (iVar1 == 0) {
    *(undefined1 *)param_2[2] = *(undefined1 *)*param_2;
    *(undefined1 *)(param_2[2] + 1) = (*((undefined1 *)camry_host_ptr((uint32_t)(*param_2 + 1))));
    *(undefined1 *)(param_2[2] + 2) = (*((undefined1 *)camry_host_ptr((uint32_t)(*param_2 + 2))));
    *(undefined1 *)(param_2[2] + 3) = uStack_9;
    param_2[3] = 4;
  }
  return iVar1 != 0;
}



undefined1 FUN_0008cfe8(char param_1,undefined1 *param_2,undefined1 *param_3,byte *param_4)

{
  byte bVar1;
  undefined1 uVar2;
  undefined1 uVar3;
  undefined1 uVar4;
  
  bVar1 = *param_4;
  uVar4 = *param_2;
  if (bVar1 < 0xfe) {
    bVar1 = bVar1 + 1;
    uVar2 = *param_3;
    uVar3 = 0;
    if (param_1 == -1) {
      uVar4 = 0x5a;
      uVar3 = uVar4;
    }
  }
  else {
    uVar2 = 0x5a;
    uVar3 = uVar2;
  }
  *param_4 = bVar1;
  *param_2 = uVar4;
  *param_3 = uVar2;
  return uVar3;
}



undefined4 FUN_0008d0e6(char *param_1,int param_2,int *param_3)

{
  uint uVar1;
  uint uVar2;
  
  uVar1 = (uint)(*((ushort *)camry_host_ptr((uint32_t)(param_2 + 2))));
  if ((*param_1 != 'Z') || (*(ushort *)param_3[1] < 5)) {
    if ((param_1[3] != 'Z') || (uVar1 < 8)) {
      if (*param_1 == 'Z') {
        return 0;
      }
      if (param_1[3] != 'Z') {
        *(char *)param_3[3] = param_1[2];
        return 1;
      }
    }
    if ((*((int *)camry_host_ptr((uint32_t)(param_2 + 4)))) != 0) {
      uVar2 = 0;
      if (3 < uVar1) {
        uVar2 = uVar1 - 3 & 0xffff;
      }
      for (uVar1 = 0; uVar1 < uVar2; uVar1 = uVar1 + 1 & 0xffff) {
        (*((undefined1 *)camry_host_ptr((uint32_t)(*param_3 + uVar1)))) = (*((undefined1 *)camry_host_ptr((uint32_t)(*(int *)(param_2 + 4) + uVar1 + 3))));
      }
      *(short *)param_3[1] = (short)uVar2;
    }
  }
  return 0;
}



void FUN_0008d3fa(void)

{
  f33_dcm_cancel_service_events(0xef,'\0');
  FUN_0009560e(1);
  f33_fill_constant_block_8cef0();
  return;
}



/* EventEF polls8D15E with retained4564/4573/4574. Result10 retains them; other results reset the
   snapshot module through8CEF0 and clear those retained inputs. */

void f33_dcm_resume_queued_snapshot_record(void)

{
  int iVar1;
  undefined4 uVar2;
  undefined1 uVar3;
  undefined1 uVar4;
  
  uVar3 = DAT_febf4574;
  uVar4 = DAT_febf4573;
  uVar2 = DAT_febf4564;
  iVar1 = FUN_0008d15e(DAT_febf4564,DAT_febf4573,DAT_febf4574);
  if (iVar1 != 10) {
    f33_fill_constant_block_8cef0();
    uVar2 = 0;
    uVar4 = 0;
    uVar3 = 0;
  }
  DAT_febf4564 = uVar2;
  DAT_febf4573 = uVar4;
  DAT_febf4574 = uVar3;
  return;
}



void FUN_0008d4ae(void)

{
  DAT_febf459a = 0;
  DAT_febf4599 = 1;
  DAT_febf4598 = 1;
  DAT_febf459b = 0xff;
  return;
}



undefined4 FUN_0008d4e0(char param_1)

{
  if ((param_1 != '\x01') && (param_1 != '\x03' && param_1 != '\x04')) {
    return 0;
  }
  return 0x31;
}



/* Zerochallenge495A[16],copy496A[16],client497A[16],active4958/result4959. Calledstartup, every
   session notification4D582 and fullapplicationdiagnostic reset8E62A.
   Genericdelaybits/failures/securitybitmap areseparate. */

void f33_app_security_reset_challenge_material(void)

{
  uint uVar1;
  
  uVar1 = 0;
  do {
    f33_app_security_challenge[uVar1] = '\0';
    f33_app_security_challenge_duplicate[uVar1] = '\0';
    f33_app_security_client_material[uVar1] = '\0';
    uVar1 = uVar1 + 1;
  } while (uVar1 < 0x10);
  f33_app_security_challenge_active = '\0';
  f33_app_security_comparison_result = '\0';
  return;
}



void FUN_0008d6a4(void)

{
  f33_app_security_reset_challenge_material();
  return;
}



/* WARNING: Inlined function: f33_read_inverted_profile_counter */
/* For floor(low8(length)/2) iterations sample64E2A and write low16 big-endian; leave an odd
   trailing byte untouched.8D74A uses16 bytes as candidate challenge material. Same counter as
   profiler, independent of31910 profiling gate. No entropy-quality or hardware-timer execution
   claim. */

void f33_fill_counter_sample_pairs(uchar *output,uchar length)

{
  uint uVar1;
  uint uVar2;
  
  for (uVar2 = (uint)(length >> 1); uVar2 != 0; uVar2 = uVar2 - 1) {
    uVar1 = DAT_ffe51010;
    *output = (uchar)(~uVar1 >> 8);
    output[1] = (uchar)~uVar1;
    output = output + 2;
  }
  return;
}



/* Always copy16 client bytes to497A. If4958==0 or retainedchallenge allzero generate8D74A;
   failureNRC22. Otherwise copyexisting challenge495A toseed_out unchanged. Delay/current-security
   gating occurs later96692. No CMAC or ICU-S ownership. */

uint f33_app_security_prepare_seed(uchar *client_material,uchar *seed_out,uchar *negative_response)

{
  uchar *puVar1;
  uchar *puVar2;
  uint uVar3;
  uchar uVar4;
  int iVar5;
  uint uVar6;
  
  uVar4 = f33_app_security_challenge_active;
  uVar6 = 0;
  do {
    uVar3 = uVar6 + 1;
    f33_app_security_client_material[uVar6] = client_material[uVar6];
    uVar6 = uVar3;
  } while (uVar3 < 0x10);
  if (uVar4 == '\0') {
LAB_0008d872:
    uVar6 = f33_app_security_generate_challenge(seed_out);
    if (uVar6 == 0x5a) {
LAB_0008d8a6:
      uVar6 = 0;
    }
    else {
      uVar6 = 1;
      *negative_response = '\"';
    }
    return uVar6;
  }
  iVar5 = 0x5a;
  uVar6 = 0;
LAB_0008d856:
  if (f33_app_security_challenge[uVar6] != '\0') {
    iVar5 = 0;
  }
  if (iVar5 == 0x5a) goto code_r0x0008d868;
  uVar6 = 0;
  do {
    puVar1 = f33_app_security_challenge + uVar6;
    puVar2 = seed_out + uVar6;
    uVar6 = uVar6 + 1;
    *puVar2 = *puVar1;
  } while (uVar6 < 0x10);
  goto LAB_0008d8a6;
code_r0x0008d868:
  uVar6 = uVar6 + 1 & 0xff;
  if (0xf < uVar6) goto LAB_0008d872;
  goto LAB_0008d856;
}



/* Require active4958==5A; derive intermediate=AES128_DECRYPT(ROM20840,497A),
   expected=AES128_ENCRYPT(intermediate,495A). Early-exit16-byte compare returnsB on firstmismatch.
   Success clears495A/496A andactive4958, retains497A; publishesresult4959. Doesnotpublish security
   itself, which96788 doesnext. Stackintermediate/expected notwiped. */

uint f33_app_security_compare_key(uchar *submitted_key)

{
  uint uVar1;
  uint uVar2;
  uchar auStack_34 [16];
  uchar auStack_24 [16];
  
  uVar2 = 0xb;
  if ((f33_app_security_challenge_active == 'Z') &&
     (uVar1 = f33_app_security_decrypt_client_material(f33_app_security_client_material,auStack_24),
     uVar1 == 0)) {
    uVar2 = f33_app_security_encrypt_challenge(auStack_24,f33_app_security_challenge,auStack_34);
    if (uVar2 == 0) {
      uVar1 = 0;
      uVar2 = 0;
      do {
        if (submitted_key[uVar1] != auStack_34[uVar1]) {
          uVar2 = 0xb;
        }
        uVar1 = uVar1 + 1 & 0xff;
        if (uVar2 != 0) goto LAB_0008d998;
      } while (uVar1 < 0x10);
      uVar1 = 0;
      do {
        f33_app_security_challenge[uVar1] = '\0';
        f33_app_security_challenge_duplicate[uVar1] = '\0';
        uVar1 = uVar1 + 1;
      } while (uVar1 < 0x10);
      f33_app_security_challenge_active = '\0';
    }
    else {
      uVar2 = 0xb;
    }
  }
LAB_0008d998:
  f33_app_security_comparison_result = (uchar)uVar2;
  return uVar2;
}



uchar FUN_0008d9a2(void)

{
  return f33_app_security_comparison_result;
}



void FUN_0008d9ac(void)

{
  f33_app_security_comparison_result = '\0';
  return;
}



uchar FUN_0008d9b6(void)

{
  uchar uStack_5;
  
  f33_dcm_get_security_level(&uStack_5);
  return uStack_5;
}



/* Constant-block fill: 9 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_8db22(void)

{
  DAT_febf45ae = 1;
  DAT_febf45ad = 1;
  DAT_febf45ac = 0;
  DAT_febf45ab = 0;
  DAT_febf45aa = 0;
  DAT_febf45a8 = 0;
  DAT_febf45a9 = 0xff;
  DAT_febf45b0 = 1;
  DAT_febf45af = 1;
  return;
}



void FUN_0008db70(void)

{
  f33_dcm_cancel_service_events(0xf0,'\0');
  FUN_0009560e(1);
  f33_fill_constant_block_8db22();
  return;
}



undefined4 FUN_0008dc60(void)

{
  uchar selection;
  
  if (DAT_febf45a8 == '\x01') {
    selection = '\x01';
  }
  else {
    selection = '\x02';
  }
  f33_publish_dtc_setting_request(selection);
  return 0;
}



/* EventF0 re-enters8DD54 with retained28-byte message45B4. */

void f33_dcm_resume_queued_dtc_setting(void)

{
  FUN_0008dd54((0xfebf45b4u));
  return;
}



/* Constant-block fill: 13 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_8de1a(void)

{
  DAT_febf45d6 = 0x300;
  DAT_febf45d4 = 0;
  DAT_febf45dd = 1;
  DAT_febf45d2 = 0;
  DAT_febf45d0 = 0;
  DAT_febf45dc = 0;
  DAT_febf45e3 = 1;
  DAT_febf45e2 = 0xff;
  DAT_febf45e1 = 0;
  DAT_febf45e0 = 0;
  DAT_febf45d8 = 0;
  DAT_febf45df = 1;
  DAT_febf45de = 0;
  return;
}



undefined4 FUN_0008debe(char param_1)

{
  if (param_1 == '\x04') {
    return 0x31;
  }
  if (param_1 != '\x06') {
    if (param_1 != '\n') {
      return 0;
    }
    return 0x10;
  }
  return 0x14;
}



undefined4 FUN_0008dff6(byte *param_1,byte *param_2,int *param_3)

{
  ushort uVar1;
  uint uVar2;
  undefined4 uVar3;
  uint uVar4;
  ushort uVar5;
  
  uVar2 = (uint)*param_1;
  uVar4 = (uint)*param_2;
  uVar1 = *(ushort *)(param_1 + 2);
  uVar5 = *(ushort *)(param_2 + 2);
  if ((uVar2 == 0) && (uVar1 != 0)) {
LAB_0008e038:
    for (; uVar5 = uVar1, uVar2 < uVar1; uVar2 = uVar2 + 1 & 0xffff) {
      (*((undefined1 *)camry_host_ptr((uint32_t)(*param_3 + uVar2)))) = (*((undefined1 *)camry_host_ptr((uint32_t)(*(int *)(param_1 + 4) + uVar2))));
    }
  }
  else {
    if ((uVar4 != 0) || (uVar5 == 0)) {
      if (uVar2 == 0) goto LAB_0008e038;
      if (uVar4 != 0) {
        uVar3 = 1;
        *(byte *)param_3[3] = param_1[1];
        uVar5 = *(ushort *)(param_1 + 2);
        goto LAB_0008e06c;
      }
    }
    for (; uVar4 < uVar5; uVar4 = uVar4 + 1 & 0xffff) {
      (*((undefined1 *)camry_host_ptr((uint32_t)(*param_3 + uVar4)))) = (*((undefined1 *)camry_host_ptr((uint32_t)(*(int *)(param_2 + 4) + uVar4))));
    }
  }
  uVar3 = 0;
LAB_0008e06c:
  *(ushort *)param_3[1] = uVar5;
  return uVar3;
}



/* Tombstone all queuedF1 slots and reset selected index, phase and module result bytes
   through8E1E0. Does not revoke BA application/requester ownership or undo an earlier record
   request. */

void f33_dcm_cancel_retained_proprietary_operation(void)

{
  f33_dcm_cancel_service_events(0xf1,'\0');
  FUN_0008e1e0();
  return;
}



/* ZXB R6/R7/R8/R9 at8E602..608; choose pending if either input is pending, otherwise local failure
   or nonzero side result after local success. MOV R9,R10 at8E620 and JMP LP guarantee full
   zero-extended32 result0..255. */

uint f33_merge_two_diagnostic_statuses
               (uchar application_status,uchar lower_status,uchar success_status,
               uchar pending_status)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  
  uVar1 = (uint)application_status;
  uVar2 = (uint)lower_status;
  uVar3 = (uint)pending_status;
  if ((((uVar2 != uVar3) && (uVar1 != uVar3)) && (uVar3 = uVar1, uVar1 == success_status)) &&
     (uVar2 != success_status)) {
    uVar3 = uVar2;
  }
  return uVar3;
}



/* WARNING: This is an inlined function */
/* Exactfunctionreturns5Aunconditionally;nominalside-statusargumentisignored. No status-dependent
   admission inferred. */

uint f33_diag_routine_local_dispatch_enabled(void)

{
  return 0x5a;
}



/* Sequential initializer chain: 16 unconditional calls and no other statements; shape-verified. The
   called sequence is the function's entire behavior; chain family members differ in callee sets. */

void f33_run_init_chain_8e62a(void)

{
  FUN_0008b070();
  FUN_0008b134();
  f33_fill_constant_block_8bfea();
  FUN_0008c318();
  FUN_0008c70c();
  f33_fill_constant_block_8cb8c();
  f33_fill_constant_block_8cef0();
  FUN_0008b3d4();
  FUN_0008d4ae();
  f33_app_security_reset_challenge_material();
  FUN_0008d9ca();
  f33_reset_write_did_transaction();
  f33_diag_reset_routine_class_state();
  f33_fill_constant_block_8db22();
  f33_fill_constant_block_8de1a();
  FUN_0008e1e0();
  return;
}



/* Use incomingR7 NRC to stage and complete the enclosing52BC DCM context. IncomingR6 operation-view
   pointer is not consumed. */

void f33_dcm_reject_proprietary_message(F33DiagProprietaryMessage *ignored_message,uchar nrc)

{
  f33_dcm_stage_negative_response((F33DcmMessageContext *)((undefined *)camry_host_ptr(0xfebe52bcu)),nrc);
  f33_dcm_complete_service_response((F33DcmMessageContext *)((undefined *)camry_host_ptr(0xfebe52bcu)));
  return;
}



/* status0 =>0,NRC0;other =>1 andconfigured byte mapping, no pending scheduling itself. */

uint f33_diagnostic_status_to_nrc(uchar status,uchar *nrc)

{
  uchar uVar1;
  
  switch(status) {
  case '\0':
    *nrc = '\0';
    return 0;
  default:
    uVar1 = '\x10';
    break;
  case '\x02':
    uVar1 = 'x';
    break;
  case '\x03':
  case '\x04':
    uVar1 = '1';
    break;
  case '\x05':
    uVar1 = '\"';
    break;
  case '\x06':
    uVar1 = '\x14';
    break;
  case '\a':
    uVar1 = '\x12';
    break;
  case '\b':
    uVar1 = '$';
    break;
  case '\t':
    uVar1 = 'r';
    break;
  case '\v':
    uVar1 = 0x88;
  }
  *nrc = uVar1;
  return 1;
}



void FUN_0008e74e(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = 0;
  do {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5338u + (uint32_t)(iVar3) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5398u + (uint32_t)(iVar3) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe52d8u + (uint32_t)(iVar3) * 1u)))) = 0x5a;
    iVar2 = iVar3 + 1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe53f8u + (uint32_t)(iVar3) * 1u)))) = 0x5a;
    iVar1 = iVar3 + -0x5f;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  return;
}



void FUN_0008e772(uint param_1)

{
  param_1 = param_1 & 0xffff;
  if (param_1 < 0x60) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe52d8u + (uint32_t)(param_1) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5338u + (uint32_t)(param_1) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5338u + (uint32_t)(param_1) * 1u)))) + '\x01';
  }
  return;
}



void FUN_0008e790(uint param_1)

{
  if ((param_1 & 0xffff) < 0x60) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe52d8u + (uint32_t)(param_1 & 0xffff) * 1u)))) = 0x5a;
  }
  return;
}



void FUN_0008e7a4(uint param_1)

{
  if ((param_1 & 0xffff) < 0x60) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5338u + (uint32_t)(param_1 & 0xffff) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5338u + (uint32_t)(param_1 & 0xffff) * 1u)))) + '\x01';
  }
  return;
}



void FUN_0008e7ba(uint param_1)

{
  if ((param_1 & 0xffff) < 0x60) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5398u + (uint32_t)(param_1 & 0xffff) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5398u + (uint32_t)(param_1 & 0xffff) * 1u)))) + '\x01';
  }
  return;
}



void FUN_0008e7d0(uint param_1,undefined1 param_2)

{
  if ((param_1 & 0xffff) < 0x60) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe53f8u + (uint32_t)(param_1 & 0xffff) * 1u)))) = param_2;
  }
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_8e7e0(void)

{
  return;
}



void FUN_0008e82c(void)

{
  uint uVar1;
  uint32_t puVar2;
  puVar2 = 0xfebeb800u;
  FUN_0008e7e2();
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x63a0)))) = 0xffff;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x63a6)))) = 0xffff;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x639c)))) = 0xffff;
  uVar1 = 0;
  do {
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + uVar1 * 8 + -0x6394)))) = 0xffff;
    uVar1 = uVar1 + 1;
  } while (uVar1 < 3);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6398))))) = 0x5a;
  return;
}



undefined2 FUN_0008e912(short param_1,ushort param_2,undefined4 *param_3,undefined4 *param_4)

{
  undefined2 uVar1;
  
  uVar1 = 1;
  if ((param_1 == 0) && (param_2 == 0)) {
    *param_3 = DAT_00025954;
    *param_4 = DAT_00025958;
    uVar1 = 0;
  }
  if ((param_1 == 1) && (param_2 < 3)) {
    uVar1 = 0;
    *param_3 = *(undefined4 *)(((undefined *)camry_host_ptr(0x2586cu)) + (short)param_2 * 0x50);
    *param_4 = *(undefined4 *)(((undefined *)camry_host_ptr(0x25870u)) + (short)param_2 * 0x50);
  }
  return uVar1;
}



undefined2 FUN_0008e954(short param_1,ushort *param_2)

{
  undefined2 uVar1;
  
  uVar1 = 1;
  if (param_1 == 0) {
    if (f33_secoc_tx_queue_head_pair[0] == (ushort)~f33_secoc_tx_queue_head_pair[1]) {
      *param_2 = f33_secoc_tx_queue_head_pair[0];
      uVar1 = 0;
    }
    else {
      DAT_febe5468 = 0xa5;
    }
  }
  if (param_1 == 1) {
    if (DAT_febe5464 == (ushort)~DAT_febe5466) {
      *param_2 = DAT_febe5464;
      return 0;
    }
    DAT_febe5468 = 0xa5;
  }
  return uVar1;
}



bool FUN_0008e9a0(ushort param_1,ushort param_2)

{
  if (param_1 == 0) {
    f33_secoc_tx_queue_head_pair[1] = ~param_2;
    f33_secoc_tx_queue_head_pair[0] = param_2;
  }
  if (param_1 == 1) {
    DAT_febe5466 = ~param_2;
    DAT_febe5464 = param_2;
  }
  return 1 < param_1;
}



void FUN_0008ecb2(undefined4 *param_1,undefined1 *param_2,uint *param_3)

{
  int iVar1;
  
  if ((((param_1 != (undefined4 *)0x0) && (param_2 != (undefined1 *)0x0)) &&
      (param_3 != (uint *)0x0)) &&
     ((uint)*(ushort *)(param_1 + 3) + (uint)(*((ushort *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 10)))) + 2 <= *param_3)) {
    *param_2 = (char)((ushort)*(undefined2 *)(param_1 + 2) >> 8);
    param_2[1] = *(undefined1 *)(param_1 + 2);
    f33_memcpy_forward(param_2 + 2,(void *)*param_1,(uint)(*((ushort *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 10)))));
    iVar1 = (*((ushort *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 10)))) + 2;
    f33_memcpy_forward(param_2 + iVar1,(void *)param_1[1],(uint)*(ushort *)(param_1 + 3));
    *param_3 = (uint)*(ushort *)(param_1 + 3) + iVar1;
  }
  return;
}



short FUN_0008eee8(void)

{
  short sStack_6;
  
  sStack_6 = 0;
  FUN_00089d08(&sStack_6);
  if ((sStack_6 != 0) && (sStack_6 != 1)) {
    sStack_6 = 2;
  }
  return sStack_6;
}



void FUN_0008ef3a(void)

{
  int iVar1;
  
  iVar1 = FUN_0008eee8();
  if ((((iVar1 == 0) && (iVar1 = FUN_0008ef0c(), iVar1 == 0)) &&
      (iVar1 = FUN_0008f9c6(), iVar1 == 0)) &&
     (((iVar1 = FUN_00090146(), iVar1 == 0 && (iVar1 = FUN_0008f210(), iVar1 == 0)) &&
      (iVar1 = FUN_0008ec66(), iVar1 == 0)))) {
    FUN_000904c0();
  }
  return;
}



undefined4 FUN_0008ef84(void)

{
  uint32_t puVar1;
  uint32_t puVar2;
  int iVar3;
  int iVar4;
  
  puVar1 = 0xfebeb800u;
  puVar2 = 0x23dfcu;
  while( true ) {
    iVar3 = FUN_0008fc58();
    iVar3 = (uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0x1a28)))) - iVar3;
    iVar4 = (uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x6308)))) - iVar3;
    if (iVar4 < 0 == (iVar3 < 0 && iVar3 < 0 == iVar4 < 0)) {
      return 0;
    }
    (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x6308)))) = (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x6308)))) + 1;
    iVar4 = FUN_0008f98c();
    if (iVar4 == 0x300) {
      (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x6308)))) = (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x6308)))) + -1;
    }
    if (iVar4 == 0x202) break;
    if (iVar4 == 0x300) {
      return 0;
    }
  }
  return 0;
}



undefined4 FUN_0008efc6(void)

{
  uint32_t puVar1;
  uint32_t puVar2;
  int iVar3;
  
  puVar1 = 0xfebeb800u;
  puVar2 = 0x23dfcu;
  do {
    if ((*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0x1a28)))) <= (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x6308))))) {
      return 0;
    }
    (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x6308)))) = (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x6308)))) + 1;
    iVar3 = FUN_000900ea();
    if (iVar3 == 0x202) {
      return 0;
    }
    if (iVar3 == 0x203) {
      return 0;
    }
  } while (iVar3 != 0x300);
  return 0;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_8f106(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_8f108(void)

{
  return;
}



/* Constant source: return 1; shape-classified from the canonical corpus. Callers receive this
   literal directly; its meaning is not recovered. */

undefined4 f33_return_const_1_8f10e(void)

{
  return 1;
}



/* Constant source: return 1; shape-classified from the canonical corpus. Callers receive this
   literal directly; its meaning is not recovered. */

undefined4 f33_return_const_1_8f112(void)

{
  return 1;
}



/* Constant source: return 1; shape-classified from the canonical corpus. Callers receive this
   literal directly; its meaning is not recovered. */

undefined4 f33_return_const_1_8f116(void)

{
  return 1;
}



void FUN_0008f11a(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  f33_memzero(((undefined *)camry_host_ptr(0xfebe5504u)),0x14);
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x6300)))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x6302)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x62fe))))) = 0xe1;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6303))))) = 0xff;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6304))))) = 0xff;
  return;
}



/* Return1 only for5502==D2. RX recovery8F596 and completion8F906 combine this with per-profile
   configuration; do not interpret it as universal successful authentication. */

uint f33_secoc_crypto_qualification_reported(void)

{
  return (uint)(f33_secoc_crypto_qualification == 0xd2);
}



undefined4 FUN_0008f2b0(short param_1,char param_2,ushort *param_3)

{
  ushort uVar1;
  
  if (param_3 != (ushort *)0x0) {
    uVar1 = 0;
    if (param_2 == '\0') {
      while (param_1 != (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x2587cu + (uint32_t)((short)uVar1 * 0x28) * 2u))))) {
        uVar1 = uVar1 + 1;
        if (2 < uVar1) {
          return 1;
        }
      }
LAB_0008f2ec:
      *param_3 = uVar1;
      return 0;
    }
    if (param_2 == '\x01') {
      uVar1 = 0;
      do {
        if (param_1 == (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x2587eu + (uint32_t)((short)uVar1 * 0x28) * 2u))))) goto LAB_0008f2ec;
        uVar1 = uVar1 + 1;
      } while (uVar1 < 3);
    }
  }
  return 1;
}



/* Single constant publisher: DAT_febe551c = 0; Shape-classified from the canonical corpus; the
   target cell is not yet named, so the written state's meaning is unknown. */

void FUN_0008f3ec(void)

{
  DAT_febe551c = 0;
  return;
}



undefined4 FUN_0008f906(ushort param_1)

{
  bool bVar1;
  bool bVar2;
  uint uVar3;
  undefined4 uVar4;
  uint uVar5;
  
  uVar5 = (uint)param_1;
  if (((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5524u + (uint32_t)(uVar5) * 1u))))) == -0x3d) {
    bVar1 = DAT_febe5564 != '\0';
    uVar3 = f33_secoc_crypto_qualification_reported();
    bVar2 = bVar1;
    if ((uVar3 == 1) && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x25851u + (uint32_t)((short)param_1 * 0x50) * 1u)))) == '\x01')) {
      bVar2 = false;
    }
    FUN_0008f8d2(uVar5,bVar2);
    if (bVar1) {
      uVar4 = FUN_0008f60e(uVar5,0x200);
    }
    else {
      FUN_0008f4d0(uVar5,0);
      uVar4 = FUN_0008f546(uVar5,0);
    }
  }
  else {
    uVar4 = 0x103;
  }
  if (((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5524u + (uint32_t)(uVar5) * 1u))))) != -0x4c) {
    FUN_0008f70e(uVar5);
  }
  return uVar4;
}



int FUN_0008f98c(void)

{
  int iVar1;
  int iVar2;
  undefined2 uStack_a;
  
  iVar2 = 0x300;
  uStack_a = 0;
  iVar1 = FUN_0008e8a0(1,0,&uStack_a);
  if ((iVar1 == 0) && (iVar2 = FUN_0008f746(uStack_a), iVar2 == 0)) {
    iVar2 = FUN_0008f906(uStack_a);
  }
  return iVar2;
}



undefined4 FUN_0008f9c6(void)

{
  char cVar1;
  undefined4 uVar2;
  uint uVar3;
  
  uVar3 = (uint)DAT_febe5520;
  uVar2 = 2;
  if (2 < uVar3) {
    uVar3 = 0;
  }
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5524u + (uint32_t)(uVar3) * 1u))));
  if ((((cVar1 == -0x6a) || (cVar1 == -0x5b)) || (cVar1 == -0x4c)) ||
     (((cVar1 == -0x3d || (cVar1 == -0x2e)) || (cVar1 == -0x1f)))) {
    uVar2 = 0;
  }
  else {
    DAT_febe5522 = 3;
  }
  if (DAT_febe5522 != 0) {
    DAT_febe5522 = DAT_febe5522 + -1;
    uVar2 = 2;
  }
  DAT_febe5520 = (short)uVar3 + 1;
  return uVar2;
}



undefined4 FUN_0008fa5a(short param_1,char param_2,undefined2 *param_3)

{
  short sVar1;
  undefined4 uVar2;
  
  uVar2 = 1;
  if (param_3 != (undefined2 *)0x0) {
    sVar1 = DAT_00025964;
    if (((param_2 != '\0') && (sVar1 = DAT_00025966, param_2 != '\x01')) || (param_1 != sVar1)) {
      return uVar2;
    }
    *param_3 = 0;
    uVar2 = 0;
  }
  return uVar2;
}



ushort FUN_0008fc58(void)

{
  ushort uVar1;
  
  uVar1 = DAT_00025826;
  if (DAT_febe556a < DAT_00025826) {
    uVar1 = DAT_febe556a;
  }
  return uVar1;
}



void FUN_0008fed0(short param_1,int param_2,uint *param_3)

{
  undefined1 *puVar1;
  byte bVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  uint uVar7;
  uint uVar8;
  byte *pbVar9;
  
  uVar3 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2594du + (uint32_t)(param_1 * 0x44) * 1u))));
  if (DAT_febe5570 <= uVar3) {
    uVar3 = DAT_febe5570;
  }
  for (uVar4 = 0; uVar4 < (uVar3 + 7 >> 3 & 0xffff); uVar4 = uVar4 + 1 & 0xffff) {
    (*((undefined1 *)camry_host_ptr((uint32_t)(uVar4 + param_2)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5574u + (uint32_t)(uVar4) * 1u))));
  }
  uVar7 = uVar3 & 7;
  uVar5 = (uint)*(ushort *)(((undefined *)camry_host_ptr(0x2593au)) + param_1 * 0x44);
  if ((uint)(DAT_febe55a4 * 8) <= uVar5) {
    uVar5 = DAT_febe55a4 * 8;
  }
  uVar8 = uVar5 >> 3 & 0xffff;
  uVar6 = 0;
  if (uVar7 == 0) {
    for (; uVar6 < uVar8; uVar6 = uVar6 + 1 & 0xffff) {
      puVar1 = ((undefined1 *)camry_host_ptr((uint32_t)(uVar4 + param_2)));
      uVar4 = uVar4 + 1 & 0xffff;
      *puVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe55a8u + (uint32_t)(uVar6) * 1u))));
    }
    if ((uVar5 & 7) == 0) goto LAB_0008ffce;
    uVar7 = 8 - (uVar5 & 7);
    pbVar9 = ((byte *)camry_host_ptr((uint32_t)(uVar4 + param_2)));
    bVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe55a8u + (uint32_t)(uVar6) * 1u)))) & (byte)((0xff >> (uVar7 & 0x1f)) << (uVar7 & 0x1f));
  }
  else {
    uVar4 = uVar4 - 1 & 0xffff;
    for (; uVar6 < uVar8; uVar6 = uVar6 + 1 & 0xffff) {
      pbVar9 = ((byte *)camry_host_ptr((uint32_t)(uVar4 + param_2)));
      uVar4 = uVar4 + 1 & 0xffff;
      *pbVar9 = *pbVar9 | (byte)((int)(uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe55a8u + (uint32_t)(uVar6) * 1u)))) >> uVar7);
      (*((undefined1 *)camry_host_ptr((uint32_t)(uVar4 + param_2)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe55a8u + (uint32_t)(uVar6) * 1u)))) << (8 - uVar7 & 0x1f);
    }
    if ((uVar5 & 7) == 0) goto LAB_0008ffce;
    uVar8 = 8 - (uVar5 & 7);
    pbVar9 = ((byte *)camry_host_ptr((uint32_t)(uVar4 + param_2)));
    bVar2 = *pbVar9 | (byte)((int)((uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe55a8u + (uint32_t)(uVar6) * 1u)))) &
                                  (0xff >> (uVar8 & 0x1f)) << (uVar8 & 0x1f)) >> uVar7);
  }
  *pbVar9 = bVar2;
LAB_0008ffce:
  *param_3 = uVar3 + uVar5 + 7 >> 3;
  return;
}


