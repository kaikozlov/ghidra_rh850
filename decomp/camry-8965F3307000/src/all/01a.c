#include "common.h"


bool FUN_0006805e(void)

{
  undefined1 uVar1;
  uint32_t puVar2;
  uchar uStack_6;
  uchar uStack_5;
  
  puVar2 = 0xfebeb800u;
  f33_nvm_recover_family1_request_indices(&uStack_6,&uStack_5);
  if (uStack_6 == uStack_5) {
    uVar1 = 0x5a;
  }
  else {
    uVar1 = 0xff;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x4e88))))) = uVar1;
  return uStack_6 == uStack_5;
}



undefined4 FUN_0006808e(void)

{
  int iVar1;
  undefined8 uVar2;
  undefined4 uVar3;
  int iVar4;
  
  uVar2 = 0xfebeb800;
  uVar3 = 0;
  if (f33_nvm_family1_span_request == 0xa5) {
    for (iVar4 = 0; iVar1 = (int)uVar2,
        (int)(iVar4 - (uint)f33_nvm_family1_object_count) < 0 !=
        (iVar4 < 0 && -1 < (int)(iVar4 - (uint)f33_nvm_family1_object_count)); iVar4 = iVar4 + 1) {
      f33_publish_redundant_u8
                ('\x11',((uchar *)camry_host_ptr((uint32_t)(iVar1 + 0x4b28 + iVar4))),((uchar *)camry_host_ptr((uint32_t)(iVar1 + 0x5888 + iVar4))),
                 ((uchar *)camry_host_ptr((uint32_t)(iVar1 + 0x58ac + iVar4))));
    }
    (*((undefined1 *)camry_host_ptr((uint32_t)(iVar1 + 0x4e88)))) = 0;
    uVar3 = 1;
  }
  else if (f33_nvm_family1_span_request == 0xff) {
    for (iVar4 = 0; iVar1 = (int)uVar2,
        (int)(iVar4 - (uint)f33_nvm_family1_object_count) < 0 !=
        (iVar4 < 0 && -1 < (int)(iVar4 - (uint)f33_nvm_family1_object_count)); iVar4 = iVar4 + 1) {
      f33_publish_redundant_u8
                ('1',((uchar *)camry_host_ptr((uint32_t)(iVar1 + 0x4b28 + iVar4))),((uchar *)camry_host_ptr((uint32_t)(iVar1 + 0x5888 + iVar4))),
                 ((uchar *)camry_host_ptr((uint32_t)(iVar1 + 0x58ac + iVar4))));
    }
    (*((undefined1 *)camry_host_ptr((uint32_t)(iVar1 + 0x4e88)))) = 0;
    uVar3 = 0xffffffff;
  }
  return uVar3;
}



/* Return zero-extended byte0689; snapshot precedes hold decoding. Exact LDBU0689 into full32r10
   thenJMPLP. Native work-selection calls snapshot this family1 phase before hold repair and prefer
   it when both phases are active. */

uint f33_nvm_get_family1_phase(void)

{
  return (uint)f33_nvm_family1_phase;
}



/* Always call74114 first. If either family busy byte equalsA5, poll and normalize result. Retain
   both flags and direct-operation request only for result1; any other result clears both busy bytes
   and request, then performs real mode-exit cancellation/reconciliation. */

void f33_nvm_service_and_release_erase_span(void)

{
  uint32_t puVar1;
  uint uVar2;
  
  puVar1 = 0xfebeb800u;
  f33_nvm_service_application_cycle();
  if ((((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x4e90)))))) == -0x5b) || (((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x4e91)))))) == -0x5b)) {
    f33_nvm_poll_direct_operation();
    uVar2 = f33_nvm_get_direct_operation_result();
    if (uVar2 != 1) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x4e90))))) = 0;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x4e91))))) = 0;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x4e92u + (uint32_t)((int)(puVar1 + 1)))))) = (code)0x0;
      f33_nvm_poll_probe_mode();
    }
  }
  return;
}



void FUN_00068318(void)

{
  f33_nvm_service_acquisition_driver();
  return;
}



/* Store only5A to0692; does not submit or complete any request. Exact three instructions store5A
   only to0692. Real bounded bootstrap then consumes that arm token; the store itself does not
   submit or complete requests. */

void f33_nvm_arm_initial_read_acquisition(void)

{
  f33_nvm_initial_read_token = 'Z';
  return;
}



/* Truncate page/count independently to16 bits and shift by6. Set direct-operation request5A and
   reconcile. Call794DA; return0 and retain mode only for result7. Otherwise clear request, perform
   real cancellation/reconciliation and returnFF. Native admitted path is bounded before opcode20,
   not erased data. */

uint f33_nvm_begin_page_erase_span(uint first_page,uint page_count)

{
  uint32_t puVar1;
  uint uVar2;
  
  puVar1 = 0xfebeb800u;
  f33_nvm_direct_operation_request = 'Z';
  f33_nvm_poll_probe_mode();
  uVar2 = f33_nvm_request_erase_span(0,(first_page & 0xffff) << 6,(page_count & 0xffff) << 6);
  if (uVar2 == 7) {
    uVar2 = 0;
  }
  else {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x4e92u + (uint32_t)((int)(puVar1 + 1)))))) = (code)0x0;
    f33_nvm_poll_probe_mode();
    uVar2 = 0xff;
  }
  return uVar2;
}



uchar FUN_00068924(void)

{
  return f33_nvm_family0_busy;
}



undefined4 FUN_000689f2(uint param_1,undefined4 param_2,uint param_3)

{
  uint32_t puVar1;
  uint uVar2;
  int iVar3;
  undefined4 uVar4;
  
  puVar1 = 0xfebeb800u;
  f33_nvm_direct_operation_request = 'Z';
  f33_nvm_poll_probe_mode();
  uVar2 = f33_nvm_classify_storage_range(0,param_1 & 0xffff,param_3);
  if (uVar2 == 3) {
    iVar3 = FUN_00079554(0,param_1 & 0xffff,param_2,param_3);
    uVar4 = 0;
    if (iVar3 == 0) goto LAB_00068a3a;
  }
  else if (uVar2 == 2) {
    uVar4 = 0x5a;
    goto LAB_00068a3a;
  }
  uVar4 = 0xff;
LAB_00068a3a:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x4e92u + (uint32_t)((int)(puVar1 + 1)))))) = (code)0x0;
  f33_nvm_poll_probe_mode();
  return uVar4;
}



uchar FUN_00068a4a(void)

{
  return f33_nvm_family1_busy;
}



uchar FUN_00068f64(void)

{
  return f33_nvm_direct_operation_request;
}



/* Constant source: return 0; shape-classified from the canonical corpus. Callers receive this
   literal directly; its meaning is not recovered. */

undefined4 f33_return_const_0_68f6a(void)

{
  return 0;
}



/* Constant source: return 0; shape-classified from the canonical corpus. Callers receive this
   literal directly; its meaning is not recovered. */

undefined4 f33_return_const_0_68f6e(void)

{
  return 0;
}



/* Clear eight repeat/generation/seen bytes, previous/qualified64-byte banks and qualified mask.
   Does not by itself release an application operation. */

void f33_crypto_bank_clear_fragment_history(void)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  
  uVar2 = 0;
  do {
    uVar3 = 0;
    do {
      iVar1 = uVar3 + uVar2 * 8;
      uVar3 = uVar3 + 1;
      f33_crypto_key_fragment_previous[iVar1] = '\0';
      f33_crypto_key_fragment_qualified[iVar1] = '\0';
    } while (uVar3 < 8);
    f33_crypto_key_fragment_repeat_count[uVar2] = '\0';
    uVar3 = uVar2 + 1;
    f33_crypto_key_fragment_previous_generation[uVar2] = '\0';
    f33_crypto_key_fragment_seen[uVar2] = '\0';
    uVar2 = uVar3;
  } while (uVar3 < 8);
  f33_crypto_key_fragment_qualified_mask = '\0';
  return;
}



/* Clear five qualification histories, scalar pair, four8-byte previous/qualified groups and
   fixed16-byte input/expected/AES/MAC buffers. No hardware cancellation. */

void f33_crypto_bank_clear_test_material(void)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  
  uVar2 = 0;
  do {
    uVar3 = 0;
    do {
      iVar1 = uVar3 + uVar2 * 8;
      uVar3 = uVar3 + 1;
      f33_crypto_test_fragment_previous[iVar1] = '\0';
      f33_crypto_test_fragment_qualified[iVar1] = '\0';
    } while (uVar3 < 8);
    uVar2 = uVar2 + 1;
  } while (uVar2 < 4);
  uVar2 = 0;
  do {
    f33_crypto_test_repeat_count[uVar2] = '\0';
    uVar3 = uVar2 + 1;
    f33_crypto_test_previous_generation[uVar2] = '\0';
    f33_crypto_test_seen[uVar2] = '\0';
    uVar2 = uVar3;
  } while (uVar3 < 5);
  uVar2 = 0;
  do {
    f33_crypto_test_input[uVar2] = '\0';
    uVar2 = uVar2 + 1;
  } while (uVar2 < 0x10);
  uVar2 = 0;
  do {
    f33_crypto_test_expected[uVar2] = '\0';
    uVar3 = uVar2 + 1;
    f33_crypto_aes_result[uVar2] = '\0';
    f33_crypto_mac_result[uVar2] = '\0';
    uVar2 = uVar3;
  } while (uVar3 < 0x10);
  f33_crypto_test_selector = '\0';
  DAT_febe509f = 0;
  f33_crypto_test_mode = '\0';
  DAT_febe50a0 = 0;
  DAT_febe509e = 0;
  DAT_febe50a1 = 0;
  f33_crypto_test_qualified_mask = '\0';
  return;
}



/* WARNING: Inlined function: f33_crypto_bank_clear_key_material */
/* Clear direct/collected/test activation, timers, qualification histories and outputs. Initialize
   result lengths48/16/16, verification result1, two profile states11 and observation counters. Mode
   bytes5099/509A are separately owned. */

void f33_crypto_bank_initialize_work(void)

{
  uint uVar1;
  int iVar2;
  uint uVar3;
  uint32_t puVar4;
  puVar4 = 0xfebeb800u;
  f33_crypto_direct_activation = '\0';
  f33_crypto_direct_phase = '\0';
  f33_crypto_direct_elapsed_calls = 0;
  f33_crypto_direct_failure_count = '\0';
  f33_crypto_direct_inhibited = '\0';
  f33_crypto_direct_abort_request = '\0';
  f33_crypto_collected_activation = '\0';
  f33_crypto_collected_phase = '\0';
  f33_crypto_collected_elapsed_calls = 0;
  f33_crypto_bank_clear_fragment_history();
  uVar3 = 0;
  do {
    uVar1 = uVar3 + 1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(uVar3 - 0x663a))))) = 0;
    uVar3 = uVar1;
  } while (uVar1 < 0x40);
  uVar3 = 0;
  do {
    uVar1 = uVar3 + 1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(uVar3 - 0x65ba))))) = 0;
    uVar3 = uVar1;
  } while (uVar1 < 0x30);
                    /* WARNING: Could not inline here */
  f33_crypto_bank_clear_key_material('\x01');
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6765))))) = 0;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar4 + -0x679c)))) = 0x30;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6763))))) = 1;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6764))))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar4 + -0x677a)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x675d))))) = 0;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar4 + -0x6798)))) = 0x10;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar4 + -0x6794)))) = 0x10;
  f33_crypto_bank_clear_test_material();
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar4 + -0x67ac)))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar4 + -0x67aa)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6770))))) = 0x5a;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar4 + -0x67a8)))) = 0;
  uVar3 = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar4 + -0x67a6)))) = 0;
  do {
    iVar2 = uVar3 * 2;
    uVar3 = uVar3 + 1;
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar4 + iVar2 + -0x674a)))) = 0;
  } while (uVar3 < 8);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6776))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6775))))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar4 + -0x678e)))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar4 + -0x678c)))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar4 + -0x678a)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6773))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6772))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6771))))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar4 + -0x6788)))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar4 + -0x6778)))) = 0;
  uVar3 = 0;
  do {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(uVar3 - 0x6786))))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(uVar3 - 0x6784))))) = 0x11;
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar4 + uVar3 * 2 + -0x67a0)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(uVar3 - 0x6782))))) = 0;
    uVar1 = uVar3 + 1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(uVar3 - 0x6780))))) = 0;
    uVar3 = uVar1;
  } while (uVar1 < 2);
  return;
}



/* Initialize current and previous mode bytes5099/509A to5A; startup also invokes69064. */

void f33_crypto_bank_initialize_mode(void)

{
  f33_crypto_mode = 'Z';
  f33_crypto_previous_mode = 'Z';
  return;
}



/* WARNING: This is an inlined function */
/* Return min(unsigned ROM2597C,2); exact value1. Five-instruction leaf preservesR6, including
   packed callback high16 consumed by6A1B2. Inline real p-code. */

uint f33_crypto_bank_profile_count(void)

{
  uint uVar1;
  
  uVar1 = (uint)f33_crypto_config_profile_count;
  if (2 < uVar1) {
    uVar1 = 2;
  }
  return uVar1;
}



/* WARNING: Inlined function: f33_crypto_bank_profile_count */
/* For bounded configured profile count invoke8F0A8 then8F0D4, discarding statuses. Root invokes
   this on the first non-A5 cycle after modeA5; lower freshness/profile reset semantics remain
   separate. */

void f33_crypto_bank_reset_configured_profiles(void)

{
  uint uVar1;
  uint uVar2;
  
  uVar1 = (uint)f33_crypto_config_profile_count;
  if (2 < uVar1) {
    uVar1 = 2;
  }
  for (uVar2 = 0; uVar2 < uVar1; uVar2 = uVar2 + 1) {
    FUN_0008f0a8(uVar2);
    FUN_0008f0d4(uVar2);
  }
  return;
}



/* Run startup verification publication then clear accumulated observation count505C. Exact gate0
   does not issue a crypto command. */

void f33_crypto_bank_initialize_verification_report(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  f33_crypto_bank_run_startup_verification();
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x67a4)))) = 0;
  return;
}



/* WARNING: Inlined function: f33_crypto_bank_profile_count */
/* For state11: three zero-status observations select44 immediately. Otherwise increment16-bit count
   while below620; a later call at620 selects88/status5A only for zero good and nonzero bad, else22.
   No physical-time conversion. */

void f33_crypto_bank_advance_profile_qualification(void)

{
  ushort uVar1;
  uint uVar2;
  uint uVar3;
  uchar uVar4;
  
  uVar3 = (uint)f33_crypto_config_profile_count;
  if (2 < uVar3) {
    uVar3 = 2;
  }
  for (uVar2 = 0; uVar2 < uVar3; uVar2 = uVar2 + 1 & 0xff) {
    uVar4 = f33_crypto_profile_phase[uVar2];
    if (uVar4 == '\x11') {
      if (f33_crypto_profile_zero_status_count[uVar2] < 3) {
        uVar1 = f33_crypto_profile_elapsed_calls[uVar2];
        if (uVar1 < f33_crypto_config_profile_wait_calls) {
          f33_crypto_profile_elapsed_calls[uVar2] = uVar1 + 1;
        }
        else if ((f33_crypto_profile_zero_status_count[uVar2] == 0) &&
                (f33_crypto_profile_nonzero_status_count[uVar2] != '\0')) {
          uVar4 = 0x88;
          f33_crypto_profile_failed[uVar2] = 'Z';
        }
        else {
          uVar4 = '\"';
        }
      }
      else {
        uVar4 = 'D';
      }
    }
    f33_crypto_profile_phase[uVar2] = uVar4;
  }
  return;
}



/* Increment saturating16-bit timer. Above120 choose66; timeout while45 also publishes result1.
   States11/22 submit;44 starts optional verification;46 publishes result and becomes55. Store phase
   and timer after sequential transitions. */

void f33_crypto_bank_advance_direct_update(void)

{
  undefined *puVar1;
  uint uVar2;
  ushort uVar3;
  
  puVar1 = ((undefined *)camry_host_ptr(0xfebeb800u));
  uVar2 = (uint)f33_crypto_direct_phase;
  uVar3 = f33_crypto_direct_elapsed_calls;
  if (f33_crypto_direct_elapsed_calls != 0xffff) {
    uVar3 = f33_crypto_direct_elapsed_calls + 1;
  }
  if (f33_crypto_config_direct_timeout_calls < uVar3) {
    if (uVar2 == 0x45) {
      f33_crypto_verification_result = '\x01';
      puVar1 = ((undefined *)camry_host_ptr(0xfebeb800u));
      f33_crypto_bank_publish_verification_result();
    }
    uVar2 = 0x66;
  }
  else {
    if ((uVar2 == 0x11) || (puVar1 = ((undefined *)camry_host_ptr(0xfebeb800u)), uVar2 == 0x22)) {
      puVar1 = ((undefined *)camry_host_ptr(0xfebeb800u));
      uVar2 = f33_crypto_bank_submit_key_material('\0');
    }
    if (uVar2 == 0x44) {
      uVar2 = f33_crypto_bank_begin_post_update_verification();
    }
    if (uVar2 == 0x46) {
      f33_crypto_bank_publish_verification_result();
      uVar2 = 0x55;
    }
  }
  puVar1[-0x676e] = (char)uVar2;
  *(ushort *)(puVar1 + -0x677e) = uVar3;
  return;
}



/* Increment saturating timer; strict >1200 gives66. State11 collects;22 submits;44 starts optional
   verification;46 publishes then55, with sequential transitions possible in one invocation.
   Physical submission readiness remains distinct. */

void f33_crypto_bank_advance_collected_update(void)

{
  uint32_t puVar1;
  uint uVar2;
  ushort uVar3;
  
  puVar1 = 0xfebeb800u;
  uVar2 = (uint)f33_crypto_collected_phase;
  uVar3 = f33_crypto_collected_elapsed_calls;
  if (f33_crypto_collected_elapsed_calls != 0xffff) {
    uVar3 = f33_crypto_collected_elapsed_calls + 1;
  }
  if (f33_crypto_config_collected_timeout_calls < uVar3) {
    if (uVar2 == 0x45) {
      f33_crypto_verification_result = '\x01';
      puVar1 = 0xfebeb800u;
      f33_crypto_bank_publish_verification_result();
    }
    uVar2 = 0x66;
  }
  else {
    puVar1 = 0xfebeb800u;
    if (uVar2 == 0x11) {
      puVar1 = 0xfebeb800u;
      uVar2 = f33_crypto_bank_collect_key_fragments();
    }
    if (uVar2 == 0x22) {
      uVar2 = f33_crypto_bank_submit_key_material('\x01');
    }
    if (uVar2 == 0x44) {
      uVar2 = f33_crypto_bank_begin_post_update_verification();
    }
    if (uVar2 == 0x46) {
      f33_crypto_bank_publish_verification_result();
      uVar2 = 0x55;
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6769))))) = (char)uVar2;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x677c)))) = uVar3;
  return;
}



/* Increment saturating timer; strict >1160 selects44. State11 collects then may submit22 in the
   same call; accepted job waits in23. Completion callback separately compares output and
   publishes33 or44. */

void f33_crypto_bank_advance_test_operation(void)

{
  uint32_t puVar1;
  uint uVar2;
  ushort uVar3;
  
  puVar1 = 0xfebeb800u;
  uVar2 = (uint)f33_crypto_test_phase;
  uVar3 = f33_crypto_test_elapsed_calls;
  if (f33_crypto_test_elapsed_calls != 0xffff) {
    uVar3 = f33_crypto_test_elapsed_calls + 1;
  }
  if (f33_crypto_config_test_timeout_calls < uVar3) {
    uVar2 = 0x44;
  }
  else {
    puVar1 = 0xfebeb800u;
    if (uVar2 == 0x11) {
      puVar1 = 0xfebeb800u;
      uVar2 = f33_crypto_bank_collect_test_vector();
    }
    if (uVar2 == 0x22) {
      uVar2 = f33_crypto_bank_submit_test_vector();
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6764))))) = (char)uVar2;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x677a)))) = uVar3;
  return;
}



/* WARNING: Inlined function: f33_crypto_bank_clear_key_material */
/* Before normal receive/DCM: modeA5 reinitializes work each cycle; priorA5 on departure resets
   configured profiles. Advance profile qualification, consume direct abort5A, then active
   direct/collected/test workers in order. Save old current mode as previous. Hardware completion is
   not performed by this aggregate. */

void f33_crypto_bank_foreground_cycle(void)

{
  uint uVar1;
  uchar uVar2;
  uint uVar3;
  uint32_t puVar4;
  uVar2 = f33_crypto_mode;
  puVar4 = 0xfebeb800u;
  if (f33_crypto_mode == 0xa5) {
    puVar4 = 0xfebeb800u;
    f33_crypto_bank_initialize_work();
  }
  else if (f33_crypto_previous_mode == 0xa5) {
    puVar4 = 0xfebeb800u;
    f33_crypto_bank_reset_configured_profiles();
  }
  f33_crypto_bank_advance_profile_qualification();
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x676f))))) != '\0') && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x676b))))) == 'Z')) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x676f))))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x676e))))) = 0;
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar4 + -0x677e)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x676b))))) = 0;
    uVar3 = 0;
    do {
      uVar1 = uVar3 + 1;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(uVar3 - 0x663a))))) = 0;
      uVar3 = uVar1;
    } while (uVar1 < 0x40);
    uVar3 = 0;
    do {
      uVar1 = uVar3 + 1;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(uVar3 - 0x65ba))))) = 0;
      uVar3 = uVar1;
    } while (uVar1 < 0x30);
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x676f))))) == '\x01') {
    f33_crypto_bank_advance_direct_update();
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x676a))))) == '\x01') {
    f33_crypto_bank_advance_collected_update();
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6765))))) == '\x01') {
    f33_crypto_bank_advance_test_operation();
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6766))))) = uVar2;
  return;
}



/* Phase55 sets activation2;66 setsFF and saturating failure count, latching inhibition5A at
   configured5 failures. Preserve material until result read or later reset. */

void f33_crypto_bank_retire_direct_update(void)

{
  if (f33_crypto_direct_phase == 'U') {
    f33_crypto_direct_activation = '\x02';
  }
  if (((f33_crypto_direct_phase == 'f') &&
      (f33_crypto_direct_activation = 0xff, f33_crypto_direct_failure_count != 0xff)) &&
     (f33_crypto_direct_failure_count = f33_crypto_direct_failure_count + 1,
     f33_crypto_config_direct_failure_limit <= f33_crypto_direct_failure_count)) {
    f33_crypto_direct_inhibited = 'Z';
  }
  return;
}



/* WARNING: Inlined function: f33_crypto_bank_clear_key_material */
/* Phase55/66 sets activation2/FF and clears fragment history plus slot1 request/result material.
   Restore terminal phase after clearing; completion does not retain slot1 response bytes. */

void f33_crypto_bank_retire_collected_update(void)

{
  uint uVar1;
  uchar uVar2;
  uint uVar3;
  uint32_t puVar4;
  uchar uVar5;
  
  uVar2 = f33_crypto_collected_phase;
  puVar4 = 0xfebeb800u;
  uVar5 = f33_crypto_collected_activation;
  if (f33_crypto_collected_phase == 'U') {
    uVar5 = '\x02';
    puVar4 = 0xfebeb800u;
    f33_crypto_bank_clear_fragment_history();
    uVar3 = 0;
    do {
      uVar1 = uVar3 + 1;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(uVar3 - 0x65fa))))) = 0;
      uVar3 = uVar1;
    } while (uVar1 < 0x40);
    uVar3 = 0;
    do {
      uVar1 = uVar3 + 1;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(uVar3 - 0x658a))))) = 0;
      uVar3 = uVar1;
    } while (uVar1 < 0x30);
  }
  if (uVar2 == 'f') {
    uVar5 = 0xff;
    f33_crypto_bank_clear_fragment_history();
                    /* WARNING: Could not inline here */
    f33_crypto_bank_clear_key_material('\x01');
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x676a))))) = uVar5;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6769))))) = uVar2;
  return;
}



/* Phase33 sets activation2 and failure flag0;44 sets activationFF and failure flag5A. Other phases
   remain active. */

void f33_crypto_bank_retire_test_operation(void)

{
  if (f33_crypto_test_phase == '3') {
    f33_crypto_test_failed = '\0';
    f33_crypto_test_activation = '\x02';
  }
  if (f33_crypto_test_phase == 'D') {
    f33_crypto_test_activation = 0xff;
    f33_crypto_test_failed = 'Z';
  }
  return;
}



/* Reduce callback observation counts using exact30D62/30D64 thresholds, saturating total505C,
   wrapping byte interval/index and sixteen-bit counters. Preserve raw count semantics; no inferred
   milliseconds or steering authority. */

void f33_crypto_bank_publish_observation_window(void)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  byte bVar4;
  uint uVar5;
  
  uVar3 = (uint)DAT_00030d62;
  bVar4 = 0;
  uVar2 = (uint)DAT_febe508a;
  if (((uVar3 == 0) || (DAT_febe5072 < uVar3)) || ((uint)DAT_febe5072 <= (uint)DAT_febe5074)) {
    DAT_febe508f = 0;
  }
  else {
    DAT_febe508f = 0x5a;
    uVar5 = DAT_febe5074 + 1 & 0xffff;
    bVar4 = 0;
    if (uVar5 < uVar3) {
      iVar1 = uVar3 - uVar5;
      bVar4 = (byte)iVar1;
      uVar2 = uVar2 - iVar1 & 0xff;
    }
    if (~uVar2 < DAT_febe505c) {
      DAT_febe505c = 0xffffffff;
    }
    else {
      DAT_febe505c = DAT_febe505c + uVar2;
    }
  }
  DAT_febe508b = (char)uVar2;
  DAT_febe508c = bVar4 & 7;
  DAT_febe508a = 0;
  if (0x13 < (byte)(DAT_febe508d - DAT_febe508e)) {
    DAT_febe508e = DAT_febe508d;
    if ((DAT_00030d64 != 0) && (DAT_00030d64 <= DAT_febe5076)) {
      DAT_febe5072 = 0;
      DAT_febe5076 = 0;
    }
    DAT_febe5076 = DAT_febe5076 + 1;
  }
  DAT_febe5074 = DAT_febe5072;
  DAT_febe508d = DAT_febe508d + '\x01';
  return;
}



/* After DCM in667E6: retire each active application bank then publish observation window. Separate
   from69CA2 advance before receive; neither is a CAN-controller lifecycle manager. */

void f33_crypto_bank_maintain_terminal_states(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (f33_crypto_direct_activation == '\x01') {
    puVar1 = 0xfebeb800u;
    f33_crypto_bank_retire_direct_update();
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x676a))))) == '\x01') {
    f33_crypto_bank_retire_collected_update();
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6765))))) == '\x01') {
    f33_crypto_bank_retire_test_operation();
  }
  f33_crypto_bank_publish_observation_window();
  return;
}



/* Snapshot configured generation indices10..17 into prior-generation bytes. Activation does not
   treat already-present material as a new generation. */

void f33_crypto_bank_snapshot_key_generations(void)

{
  f33_crypto_key_fragment_previous_generation[0] =
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5338u + (uint32_t)(f33_crypto_key_fragment_generation_indices[0]) * 1u))));
  f33_crypto_key_fragment_previous_generation[1] =
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5338u + (uint32_t)(f33_crypto_key_fragment_generation_indices[1]) * 1u))));
  f33_crypto_key_fragment_previous_generation[2] =
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5338u + (uint32_t)(f33_crypto_key_fragment_generation_indices[2]) * 1u))));
  f33_crypto_key_fragment_previous_generation[3] =
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5338u + (uint32_t)(f33_crypto_key_fragment_generation_indices[3]) * 1u))));
  f33_crypto_key_fragment_previous_generation[4] =
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5338u + (uint32_t)(f33_crypto_key_fragment_generation_indices[4]) * 1u))));
  f33_crypto_key_fragment_previous_generation[5] =
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5338u + (uint32_t)(f33_crypto_key_fragment_generation_indices[5]) * 1u))));
  f33_crypto_key_fragment_previous_generation[6] =
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5338u + (uint32_t)(f33_crypto_key_fragment_generation_indices[6]) * 1u))));
  f33_crypto_key_fragment_previous_generation[7] =
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5338u + (uint32_t)(f33_crypto_key_fragment_generation_indices[7]) * 1u))));
  return;
}



/* WARNING: Inlined function: f33_crypto_bank_clear_key_material */
/* Only activation0 becomes1/state11/timer0; clear fragment/material state and snapshot current
   eight generations. Existing nonzero activation is not restarted. */

void f33_crypto_bank_activate_collected_update(void)

{
  uint uVar1;
  uint uVar2;
  uint32_t puVar3;
  puVar3 = 0xfebeb800u;
  if (f33_crypto_collected_activation == '\0') {
    f33_crypto_collected_activation = '\x01';
    f33_crypto_collected_elapsed_calls = 0;
    f33_crypto_collected_phase = '\x11';
    f33_crypto_bank_clear_fragment_history();
    uVar2 = 0;
    do {
      uVar1 = uVar2 + 1;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(uVar2 - 0x65fa))))) = 0;
      uVar2 = uVar1;
    } while (uVar1 < 0x40);
    uVar2 = 0;
    do {
      uVar1 = uVar2 + 1;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(uVar2 - 0x658a))))) = 0;
      uVar2 = uVar1;
    } while (uVar1 < 0x30);
    f33_crypto_bank_snapshot_key_generations();
  }
  return;
}



/* Snapshot five configured source generations before collection; scalar pair and four byte groups
   have independent histories. */

void f33_crypto_bank_snapshot_test_generations(void)

{
  f33_crypto_test_previous_generation[0] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5338u + (uint32_t)(DAT_000257d0) * 1u))));
  f33_crypto_test_previous_generation[1] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5338u + (uint32_t)(DAT_000257d2) * 1u))));
  f33_crypto_test_previous_generation[2] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5338u + (uint32_t)(DAT_000257d4) * 1u))));
  f33_crypto_test_previous_generation[3] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5338u + (uint32_t)(DAT_000257d6) * 1u))));
  f33_crypto_test_previous_generation[4] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5338u + (uint32_t)(DAT_000257d8) * 1u))));
  return;
}



/* RID100F action reaches this gate. Only activation0 becomes1/state11/timer0; clear test
   material/history and snapshot generations. CAN bytes alone do not arm it. */

void f33_crypto_bank_activate_test_operation(void)

{
  if (f33_crypto_test_activation == '\0') {
    f33_crypto_test_activation = '\x01';
    f33_crypto_test_elapsed_calls = 0;
    f33_crypto_test_phase = '\x11';
    f33_crypto_bank_clear_test_material();
    f33_crypto_bank_snapshot_test_generations();
  }
  return;
}



/* Compare16 fixed expected bytes5196 with AES result51A6; mismatch44, complete equality33. Not a
   hardware implementation of AES. */

uint f33_crypto_bank_compare_aes_result(void)

{
  uint uVar1;
  
  uVar1 = 0;
  do {
    if (f33_crypto_test_expected[uVar1] != f33_crypto_aes_result[uVar1]) {
      return 0x44;
    }
    uVar1 = uVar1 + 1;
  } while (uVar1 < 0x10);
  return 0x33;
}



/* Compare16 fixed expected bytes5196 with MAC result51B6; mismatch44, complete equality33. No
   arbitrary message or output length. */

uint f33_crypto_bank_compare_mac_result(void)

{
  uint uVar1;
  
  uVar1 = 0;
  do {
    if (f33_crypto_test_expected[uVar1] != f33_crypto_mac_result[uVar1]) {
      return 0x44;
    }
    uVar1 = uVar1 + 1;
  } while (uVar1 < 0x10);
  return 0x33;
}



undefined1 FUN_0006a12a(void)

{
  return DAT_febe508f;
}



undefined4 FUN_0006a130(void)

{
  return DAT_febe505c;
}



undefined2 FUN_0006a136(uint param_1)

{
  return *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe50b6u)) + (param_1 & 7) * 2);
}



undefined1 FUN_0006a144(void)

{
  return DAT_febe508b;
}



undefined1 FUN_0006a14a(void)

{
  return DAT_febe508c;
}



uchar FUN_0006a150(void)

{
  return f33_crypto_test_failed;
}



void FUN_0006a156(undefined4 param_1,char param_2)

{
  if (((param_2 == '\x01') || (param_2 == '@')) && (f33_crypto_direct_activation != '\0')) {
    f33_crypto_direct_abort_request = 'Z';
  }
  return;
}



void FUN_0006a174(uchar param_1)

{
  f33_crypto_mode = param_1;
  return;
}



/* Single constant publisher: DAT_febe505c = 0; Shape-classified from the canonical corpus; the
   target cell is not yet named, so the written state's meaning is unknown. */

void FUN_0006a17a(void)

{
  DAT_febe505c = 0;
  return;
}



uchar FUN_0006a180(uint param_1)

{
  if ((param_1 & 0xff) < 2) {
    return f33_crypto_profile_failed[param_1 & 0xff];
  }
  return '\0';
}



undefined4 FUN_0006a192(void)

{
  if ((f33_crypto_direct_activation != '\x01') && (f33_crypto_collected_activation != '\x01')) {
    return 0;
  }
  return 0x5a;
}



void FUN_0006a1ac(undefined2 param_1)

{
  DAT_febe5070 = param_1;
  return;
}



/* WARNING: Inlined function: f33_crypto_bank_profile_count */
/* Store low/high16 at5054/5056. For state11 and configured low ID0, saturating-increment
   zero-status507E or nonzero-status5080. High16 remains inR6 across exact6915A leaf; no extra
   callback argument. */

void f33_crypto_bank_record_profile_status(uint packed_status)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  uchar uVar4;
  uint uVar5;
  uchar *puVar6;
  
  uVar5 = packed_status & 0xffff;
  uVar2 = packed_status >> 0x10;
  uVar3 = (uint)f33_crypto_config_profile_count;
  if (2 < uVar3) {
    uVar3 = 2;
  }
  uVar1 = 0;
  while( true ) {
    DAT_febe5056 = (undefined2)(packed_status >> 0x10);
    DAT_febe5054 = (undefined2)packed_status;
    if (uVar3 <= uVar1) break;
    if ((f33_crypto_profile_phase[uVar1] == '\x11') && (uVar5 == DAT_00025840)) {
      if (uVar2 == 0) {
        puVar6 = f33_crypto_profile_zero_status_count + uVar1;
        uVar4 = *puVar6;
        if (uVar4 != 0xff) {
          uVar4 = uVar4 + '\x01';
        }
      }
      else {
        puVar6 = f33_crypto_profile_nonzero_status_count + uVar1;
        uVar4 = *puVar6;
        if (uVar4 != 0xff) {
          uVar4 = uVar4 + '\x01';
        }
      }
      *puVar6 = uVar4;
      packed_status = CONCAT22(DAT_febe5056,DAT_febe5054);
    }
    uVar1 = uVar1 + 1 & 0xff;
  }
  return;
}



void FUN_0006a280(undefined2 param_1)

{
  uint uVar1;
  
  if (DAT_febe5090 == '\0') {
    uVar1 = (uint)DAT_febe508a;
    DAT_febe508a = DAT_febe508a + 1;
    *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe50b6u)) + (uVar1 & 7) * 2) = param_1;
  }
  return;
}



/* Configured command8 callback27E54: low8 result0 selects44 else66. Route to direct phase5092 only
   if direct activation5091==1; otherwise write collected phase5097 without its activation check.
   Routing uses current activation, not a retained submission-bank token. Return0. */

uint f33_crypto_bank_key_update_completed(uchar result)

{
  uchar uVar1;
  
  uVar1 = 'f';
  if (result == '\0') {
    uVar1 = 'D';
  }
  if (f33_crypto_direct_activation == '\x01') {
    f33_crypto_direct_phase = uVar1;
    uVar1 = f33_crypto_collected_phase;
  }
  f33_crypto_collected_phase = uVar1;
  return 0;
}



/* Configured AES callback: nonzero result sets test phase44; zero compares fixed16-byte output and
   sets33/44. No active-generation check here; return0. */

uint f33_crypto_bank_aes_completed(uchar result)

{
  uint32_t puVar1;
  undefined1 uVar2;
  uint uVar3;
  
  puVar1 = 0xfebeb800u;
  uVar2 = 0x44;
  if (result == '\0') {
    puVar1 = 0xfebeb800u;
    uVar3 = f33_crypto_bank_compare_aes_result();
    uVar2 = (undefined1)uVar3;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6764))))) = uVar2;
  return 0;
}



/* Configured MAC job1 callback: nonzero result sets44; zero compares fixed16-byte output and
   sets33/44. Return0, no local active-generation check. */

uint f33_crypto_bank_mac_completed(uchar result)

{
  uint32_t puVar1;
  undefined1 uVar2;
  uint uVar3;
  
  puVar1 = 0xfebeb800u;
  uVar2 = 0x44;
  if (result == '\0') {
    puVar1 = 0xfebeb800u;
    uVar3 = f33_crypto_bank_compare_mac_result();
    uVar2 = (undefined1)uVar3;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6764))))) = uVar2;
  return 0;
}



undefined4 FUN_0006a31a(undefined2 param_1)

{
  DAT_febe5088 = param_1;
  return 0;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_6a322(void)

{
  return;
}



/* Constant source: return 0; shape-classified from the canonical corpus. Callers receive this
   literal directly; its meaning is not recovered. */

undefined4 f33_return_const_0_6a328(void)

{
  return 0;
}



undefined4 FUN_0006a32c(ushort param_1,uint *param_2)

{
  byte *pbVar1;
  int iVar2;
  undefined8 uVar3;
  undefined4 uVar4;
  uint uVar5;
  uint uVar6;
  uint uVar7;
  uint uVar8;
  
  uVar3 = 0x23dfc00000000;
  uVar6 = (uint)DAT_00028fd4;
  uVar4 = 0;
  iVar2 = 0;
  uVar7 = 0;
  while ((uVar7 < uVar6 && (iVar2 == 0))) {
    pbVar1 = ((byte *)camry_host_ptr((uint32_t)(uVar7 * 8 + (int)((ulonglong)uVar3 >> 0x20) + 0x51e8)));
    if ((ushort)*pbVar1 == (param_1 & 0xff)) {
      if ((((pbVar1[7] == 0x5a) && (param_2 != (uint *)0x0)) && (uVar8 = param_2[2], uVar8 != 0)) &&
         (7 < (*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 7)))))) {
        iVar2 = 0;
        uVar5 = 0;
        do {
          pbVar1 = ((byte *)camry_host_ptr((uint32_t)(uVar5 + uVar8)));
          uVar5 = uVar5 + 1;
          iVar2 = iVar2 + (uint)*pbVar1;
        } while (uVar5 < 7);
        if ((iVar2 + *param_2 + ((*param_2 & 0x700) >> 8) + 8 & 0xff) == (uint)(*((byte *)camry_host_ptr((uint32_t)(uVar8 + 7)))))
        {
          uVar4 = 0;
        }
        else {
          FUN_0008e7ba(param_1);
          uVar4 = 1;
        }
      }
      iVar2 = 0x5a;
    }
    uVar7 = uVar7 + 1 & 0xff;
  }
  return uVar4;
}



/* Constant source: return 0; shape-classified from the canonical corpus. Callers receive this
   literal directly; its meaning is not recovered. */

undefined4 f33_return_const_0_6a3f0(void)

{
  return 0;
}



void FUN_0006a410(void)

{
  FUN_0008eff8();
  FUN_00089dec();
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_6a420(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_6a434(void)

{
  return;
}



void FUN_0006a440(void)

{
  uint uVar1;
  
  DAT_febe39dc = 0;
  uVar1 = 0;
  do {
    *(undefined4 *)(((undefined *)camry_host_ptr(0xfebe39e0u)) + uVar1 * 4) = 0xffff;
    uVar1 = uVar1 + 1;
  } while (uVar1 < 0x100);
  return;
}



void FUN_0006a522(short param_1,short *param_2)

{
  int iVar1;
  
  iVar1 = (int)param_1;
  if (iVar1 + 0x7fff < 0 == (-1 < iVar1 && iVar1 + 0x7fff < 0) && iVar1 != -0x7fff) {
    if (iVar1 < 0) {
      param_1 = -param_1;
    }
  }
  else {
    param_1 = 0x7fff;
  }
  *param_2 = param_1;
  return;
}



void FUN_0006a53e(int param_1,int *param_2)

{
  if (param_1 + 0x7fffffff < 0 == (-1 < param_1 && param_1 + 0x7fffffff < 0) &&
      param_1 != -0x7fffffff) {
    if (param_1 < 0) {
      param_1 = -param_1;
    }
  }
  else {
    param_1 = 0x7fffffff;
  }
  *param_2 = param_1;
  return;
}



void FUN_0006a55c(undefined4 param_1,undefined1 *param_2)

{
  *param_2 = (char)((uint)param_1 >> 0x18);
  param_2[1] = (char)((uint)param_1 >> 0x10);
  param_2[2] = (char)((uint)param_1 >> 8);
  param_2[3] = (char)param_1;
  return;
}



void FUN_0006a574(undefined4 param_1,undefined1 *param_2)

{
  *param_2 = (char)((uint)param_1 >> 8);
  param_2[1] = (char)param_1;
  return;
}



void FUN_0006a594(undefined4 param_1,undefined1 *param_2)

{
  *param_2 = (char)((uint)param_1 >> 0x18);
  param_2[1] = (char)((uint)param_1 >> 0x10);
  param_2[2] = (char)((uint)param_1 >> 8);
  param_2[3] = (char)param_1;
  return;
}



void FUN_0006a5ac(undefined4 param_1,undefined1 *param_2)

{
  *param_2 = (char)((uint)param_1 >> 8);
  param_2[1] = (char)param_1;
  return;
}



void FUN_0006a5cc(short param_1,undefined1 *param_2)

{
  undefined1 uVar1;
  int iVar2;
  
  iVar2 = (int)param_1;
  if (iVar2 + 0x7f < 0 == (-1 < iVar2 && iVar2 + 0x7f < 0)) {
    if (iVar2 + -0x7f < 0 == (iVar2 < 0 && -1 < iVar2 + -0x7f) && iVar2 != 0x7f) {
      uVar1 = 0x7f;
    }
    else {
      if (iVar2 + 0x80 < 0 != (-1 < iVar2 && iVar2 + 0x80 < 0) || iVar2 == -0x80) {
        iVar2 = -0x80;
      }
      uVar1 = (undefined1)iVar2;
    }
  }
  else {
    uVar1 = 0x81;
  }
  *param_2 = uVar1;
  return;
}



void FUN_0006a5fa(int param_1,undefined2 *param_2)

{
  undefined2 uVar1;
  
  if (param_1 + 0x7fff < 0 == (-1 < param_1 && param_1 + 0x7fff < 0)) {
    if (param_1 + -0x7fff < 0 == (param_1 < 0 && -1 < param_1 + -0x7fff) && param_1 != 0x7fff) {
      uVar1 = 0x7fff;
    }
    else {
      if (param_1 + 0x8000 < 0 != (-1 < param_1 && param_1 + 0x8000 < 0) || param_1 == -0x8000) {
        param_1 = -0x8000;
      }
      uVar1 = (undefined2)param_1;
    }
  }
  else {
    uVar1 = 0x8001;
  }
  *param_2 = uVar1;
  return;
}



void FUN_0006a624(uint param_1,undefined1 *param_2)

{
  undefined1 uVar1;
  
  uVar1 = 0;
  if (-1 < (int)param_1) {
    if (param_1 < 0xff) {
      uVar1 = (undefined1)param_1;
    }
    else {
      uVar1 = 0xff;
    }
  }
  *param_2 = uVar1;
  return;
}



void FUN_0006a678(ushort *param_1,int param_2,undefined2 *param_3,int *param_4)

{
  int iVar1;
  
  if (0xfffe < param_2 - 1U) {
    param_2 = 0x10000;
  }
  iVar1 = (uint)param_1[1] * param_2 + (*(int *)(param_1 + 2) - (uint)*param_1 * param_2);
  *param_3 = (short)((uint)iVar1 >> 0x10);
  *param_4 = iVar1;
  return;
}



void FUN_0006ae48(undefined4 *param_1,ushort *param_2)

{
  undefined4 uVar1;
  
  if (param_2[2] < *(ushort *)(param_1 + 2)) {
    uVar1 = 0x22;
  }
  else {
    if ((*(ushort *)(param_1 + 2) == 0) && (*param_2 < *(ushort *)(param_1 + 1))) {
      uVar1 = 0x2200;
    }
    else {
      *(undefined2 *)(param_1 + 1) = 0;
      uVar1 = 0;
      (*((undefined2 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 6)))) = 0;
    }
    *(undefined2 *)(param_1 + 2) = 0;
    (*((undefined2 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 10)))) = 0;
  }
  *param_1 = uVar1;
  return;
}



void FUN_0006b7d2(undefined1 *param_1)

{
  *param_1 = 0;
  *(undefined2 *)(param_1 + 2) = 0;
  *(undefined2 *)(param_1 + 4) = 0;
  *(undefined2 *)(param_1 + 6) = 0;
  return;
}



void FUN_0006b98a(undefined4 *param_1)

{
  *param_1 = 0;
  *(undefined2 *)(param_1 + 1) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 6)))) = 0;
  *(undefined2 *)(param_1 + 2) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 10)))) = 0;
  *(undefined2 *)(param_1 + 3) = 0;
  return;
}


