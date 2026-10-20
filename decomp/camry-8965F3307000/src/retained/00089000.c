#include "common.h"

void complete_tag_verification_job_store_result_byte_8906c(char param_1)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_febf1318 == 0) {
    param_1 = '\x01';
  }
  else if (~(uint)DAT_febf1318 == DAT_febf128c) {
    if (param_1 == '\0') {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(DAT_febf1318)))) = (char)DAT_febf12b4;
    }
  }
  else {
    param_1 = '\x01';
    DAT_febf1191 = 1;
  }
  finish_tag_verification_service_with_guarded_callback_896e0(param_1);
  if (((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x5990)))))) == -0x3d) {
    release_icus_request_and_notify_crypto_scheduler_87edc(0);
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x5990))))) = 0xe1;
  }
  return;
}

void deliver_or_defer_tag_verification_completion_890ba(undefined1 param_1)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_febf1288 != 0) {
    if (~(uint)DAT_febf1288 == DAT_febf1290) {
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(DAT_febf1288)))) == '\x01') {
        complete_tag_verification_job_store_result_byte_8906c((uint)(byte)param_1);
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x5a94))))) = 0xd2;
        return;
      }
    }
    else {
      DAT_febf1191 = 1;
    }
  }
  DAT_febf1294 = 0xe1;
  DAT_febf1295 = param_1;
  if (((int8_t)DAT_febf1190) == -0x3d) {
    release_icus_request_and_notify_crypto_scheduler_87edc(0);
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x5990))))) = 0xe1;
  }
  return;
}

void poll_icus_tag_verification_and_route_completion_89114(void)

{
  undefined1 uVar1;
  uint32_t puVar2;
  undefined4 uVar3;
  int iVar4;
  
  puVar2 = 0xfebeb800u;
  if (((int8_t)DAT_febf1190) == -0x4c) {
    iVar4 = service_icus_feed_drain_and_completion_callbacks_8af10();
    if (iVar4 == 1) {
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0x5998)))) = 0xffffffff;
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0x5994)))) = 0;
      uVar1 = 0xc3;
      uVar3 = 0;
    }
    else {
      if (iVar4 == 0) {
        return;
      }
      if (iVar4 == 0x12) {
        return;
      }
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0x5994)))) = 0;
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0x5998)))) = 0xffffffff;
      uVar3 = get_icus_error_code_if_initialized_8afea();
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0x5984)))) = uVar3;
      release_icus_request_and_notify_crypto_scheduler_87edc(0);
      uVar1 = 0xe1;
      uVar3 = 1;
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x5990))))) = uVar1;
    deliver_or_defer_tag_verification_completion_890ba(uVar3);
  }
  return;
}

undefined4 start_prepared_icus_tag_verification_request_89170(void)

{
  uint32_t puVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  
  puVar1 = 0xfebeb800u;
  uVar4 = 1;
  if (((int8_t)DAT_febf1190) == -0x3d) {
    DAT_febf1194 = 0x89114u;
    DAT_febf1198 = 0xfff76eeb;
    DAT_febf1190 = -0x4c;
    iVar2 = prepare_icus_command_seven_with_final_block_8a8e4(((undefined *)camry_host_ptr(0xfebf1298u)));
    if (iVar2 == 0) {
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x5978)))) = 0;
      uVar4 = 0;
    }
    else {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x5990))))) = 0xc3;
      uVar3 = get_icus_error_code_if_initialized_8afea();
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x5984)))) = uVar3;
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x5994)))) = 0;
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x5998)))) = 0xffffffff;
    }
  }
  return uVar4;
}

int schedule_tag_verification_job_with_guarded_callbacks_891cc(uint param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4,
                undefined4 param_5,undefined4 param_6,undefined4 param_7)

{
  char cVar1;
  uint32_t puVar2;
  int iVar3;
  
  puVar2 = 0xfebeb800u;
  if (DAT_febf1190 == '\0') {
    return 1;
  }
  iVar3 = try_acquire_crypto_job_lock_88362();
  if (iVar3 != 1) {
    return 2;
  }
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x5990)))));
  if (((int8_t)cVar1) == -0x1f) {
    iVar3 = prepare_tag_verification_request_and_bit_lengths_88fc0(((int *)camry_host_ptr((uint32_t)(param_2))), ((void *)camry_host_ptr((uint32_t)(param_3))), param_4, ((void *)camry_host_ptr((uint32_t)(param_5))), param_6, param_7);
    if (iVar3 != 0) goto LAB_000892ba;
    (*((uint *)camry_host_ptr((uint32_t)(puVar2 + 0x5a88)))) = param_1;
    (*((uint *)camry_host_ptr((uint32_t)(puVar2 + 0x5a90)))) = ~param_1;
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar2 + 0x597c)))) = 0x89170u;
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0x5988)))) = 0xfff76e8f;
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar2 + 0x5980)))) = 0x890bau;
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0x598c)))) = 0xfff76f45;
    thunk_nvm_request_suspend_with_service_guards_7995c();
    cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x5990)))));
    if (((int8_t)cVar1) == -0x3d) {
LAB_00089292:
      iVar3 = start_prepared_icus_tag_verification_request_89170();
      if (iVar3 == 0) goto LAB_000892ba;
      goto LAB_0008929c;
    }
    if ((((int8_t)cVar1) == -0x2e) || (((int8_t)cVar1) == -0x4c)) goto LAB_000892ba;
  }
  else {
    if (((int8_t)cVar1) == -0x3d) {
      iVar3 = prepare_tag_verification_request_and_bit_lengths_88fc0(((int *)camry_host_ptr((uint32_t)(param_2))), ((void *)camry_host_ptr((uint32_t)(param_3))), param_4, ((void *)camry_host_ptr((uint32_t)(param_5))), param_6, param_7);
      if (iVar3 == 0) {
        (*((uint *)camry_host_ptr((uint32_t)(puVar2 + 0x5a88)))) = param_1;
        (*((uint *)camry_host_ptr((uint32_t)(puVar2 + 0x5a90)))) = ~param_1;
        (*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar2 + 0x5980)))) = 0x890bau;
        (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0x598c)))) = 0xfff76f45;
        goto LAB_00089292;
      }
LAB_0008929c:
      release_icus_request_and_notify_crypto_scheduler_87edc(0);
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x5990))))) = 0xe1;
      goto LAB_000892ba;
    }
    if ((((int8_t)cVar1) == -0x2e) || (((int8_t)cVar1) == -0x4c)) {
      iVar3 = 2;
      goto LAB_000892ba;
    }
  }
  iVar3 = 1;
LAB_000892ba:
  release_crypto_job_lock_88436();
  return iVar3;
}

void service_tag_verification_completion_and_timeouts_892cc(void)

{
  uint uVar1;
  uint uVar2;
  char cVar3;
  uint32_t puVar4;
  int iVar5;
  
  puVar4 = 0xfebeb800u;
  if (((int8_t)DAT_febf1294) == -0x1f) {
    puVar4 = 0xfebeb800u;
    complete_tag_verification_job_store_result_byte_8906c(DAT_febf1295);
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x5a94))))) = 0xd2;
  }
  cVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x5990)))));
  if (((int8_t)cVar3) == -0x2e) {
    uVar1 = (*((uint *)camry_host_ptr((uint32_t)(puVar4 + 0x5970)))) + 1;
    (*((uint *)camry_host_ptr((uint32_t)(puVar4 + 0x5970)))) = uVar1;
    if (uVar1 < 7) {
      return;
    }
    thunk_nvm_cancel_or_resume_suspend_and_clear_state_799da();
  }
  else {
    if (((int8_t)cVar3) != -0x3d) {
      if (((int8_t)cVar3) != -0x4c) {
        return;
      }
      uVar1 = (*((uint *)camry_host_ptr((uint32_t)(puVar4 + 0x5978)))) + 1;
      (*((uint *)camry_host_ptr((uint32_t)(puVar4 + 0x5978)))) = uVar1;
      uVar2 = (*((uint *)camry_host_ptr((uint32_t)(puVar4 + 0x5974)))) + 1;
      (*((uint *)camry_host_ptr((uint32_t)(puVar4 + 0x5974)))) = uVar2;
      if ((uVar1 < 0xc) && (uVar2 < 0xc)) {
        return;
      }
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar4 + 0x5998)))) = 0xffffffff;
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar4 + 0x5994)))) = 0;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x5990))))) = 0xa5;
      iVar5 = recover_icus_request_with_bounded_poll_and_reinitialization_88574();
      release_icus_request_and_notify_crypto_scheduler_87edc(iVar5 != 1);
      goto LAB_0008937c;
    }
    uVar1 = (*((uint *)camry_host_ptr((uint32_t)(puVar4 + 0x5974)))) + 1;
    (*((uint *)camry_host_ptr((uint32_t)(puVar4 + 0x5974)))) = uVar1;
    if (uVar1 < 0xc) {
      return;
    }
    release_icus_request_and_notify_crypto_scheduler_87edc(0);
  }
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar4 + 0x5998)))) = 0xffffffff;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar4 + 0x5994)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x5990))))) = 0xa5;
LAB_0008937c:
  deliver_or_defer_tag_verification_completion_890ba(1);
  return;
}

undefined4 check_tag_verification_completion_state_encoding_89386(void)

{
  undefined4 uVar1;
  
  if (((int8_t)DAT_febf1294) != -0x1f) {
    if (((int8_t)DAT_febf1294) == -0x2e) {
      uVar1 = 0;
    }
    else {
      uVar1 = 2;
    }
    return uVar1;
  }
  return 0;
}

void initialize_tag_generation_service_slot_and_lock_8939e(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  thunk_push_priority_mask_and_raise_to_ff00_6a45e();
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x5b74)))) = 0xffffffff;
  (*((undefined4 *)camry_host_ptr((uint32_t)(0x5b70u + (int)puVar1)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x5b7a))))) = 0xd2;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x5b79))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x5b78))))) = 0xe1;
  thunk_pop_and_restore_priority_mask_stack_6a4c4();
  return;
}

bool try_acquire_tag_generation_service_lock_893ca(void)

{
  char cVar1;
  uint32_t puVar2;
  puVar2 = 0xfebeb800u;
  thunk_push_priority_mask_and_raise_to_ff00_6a45e();
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x5b7a)))));
  if (((int8_t)cVar1) == -0x2e) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x5b7a))))) = 0xe1;
  }
  thunk_pop_and_restore_priority_mask_stack_6a4c4();
  return cVar1 == -0x2e;
}

short * find_tag_generation_service_descriptor_by_u16_id_893f2(short param_1)

{
  uint uVar1;
  
  uVar1 = 0;
  do {
    if (*(short *)(((undefined *)camry_host_ptr((uint32_t)(0x27da4u + (uint32_t)(uVar1 * 0x20) * 1u)))) == param_1) {
      return (short *)(((undefined *)camry_host_ptr((uint32_t)(0x27da4u + (uint32_t)(uVar1 * 0x20) * 1u))));
    }
    uVar1 = uVar1 + 1;
  } while (uVar1 < 2);
  return (short *)0x0;
}

void reset_tag_generation_service_selection_89414(void)

{
  DAT_febf1370 = 0;
  DAT_febf1378 = 0xe1;
  DAT_febf1374 = 0xffffffff;
  return;
}

void release_tag_generation_service_lock_89428(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  thunk_push_priority_mask_and_raise_to_ff00_6a45e();
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x5b7a))))) = 0xd2;
  thunk_pop_and_restore_priority_mask_stack_6a4c4();
  return;
}

int dispatch_tag_generation_service_by_id_when_idle_89440(undefined2 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4,
                undefined4 param_5,undefined4 param_6,undefined1 param_7)

{
  char cVar1;
  uint32_t puVar2;
  undefined4 uVar3;
  int iVar4;
  uint uVar5;
  uint32_t pcVar6;
  
  puVar2 = 0xfebeb800u;
  iVar4 = try_acquire_tag_generation_service_lock_893ca();
  if (iVar4 == 1) {
    cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x5b78)))));
    if (((int8_t)cVar1) == -0x1f) {
      uVar5 = camry_host_addr(find_tag_generation_service_descriptor_by_u16_id_893f2(param_1));
      if ((uVar5 == 0) || (pcVar6 = (uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(uVar5 + 0x14))))),(uint32_t)(pcVar6) == 0u)) {
        reset_tag_generation_service_selection_89414();
        iVar4 = 1;
      }
      else {
        uVar3 = (*((undefined4 *)camry_host_ptr((uint32_t)(uVar5 + 0x1c))));
        (*((uint *)camry_host_ptr((uint32_t)(puVar2 + 0x5b74)))) = ~uVar5;
        (*((uint *)camry_host_ptr((uint32_t)(0x5b70u + (int)puVar2)))) = uVar5;
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x5b78))))) = 0xa5;
        iVar4 = (*(int (*)())camry_indirect((uint32_t)(pcVar6)))(uVar3,param_2,param_3,param_4,param_5,param_6,param_7);
        if (iVar4 != 0) {
          reset_tag_generation_service_selection_89414();
        }
      }
    }
    else if (((int8_t)cVar1) == -0x5b) {
      iVar4 = 2;
    }
    else {
      iVar4 = 1;
      if (cVar1 != '\0') {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x5b78))))) = 0;
      }
    }
    release_tag_generation_service_lock_89428();
  }
  else {
    iVar4 = 2;
  }
  return iVar4;
}

void finish_tag_generation_service_with_guarded_callback_894dc(undefined1 param_1)

{
  uint uVar1;
  
  uVar1 = DAT_febf1370;
  if (((int8_t)DAT_febf1378) == -0x5b) {
    if (DAT_febf1370 == ~DAT_febf1374) {
      if ((DAT_febf1370 != 0) && ((*((int *)camry_host_ptr((uint32_t)(DAT_febf1370 + 4)))) != 0)) {
        reset_tag_generation_service_selection_89414();
        (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(uVar1 + 4))))))))))))(param_1);
      }
    }
    else {
      DAT_febf1379 = 1;
      reset_tag_generation_service_selection_89414();
    }
  }
  return;
}

undefined4 poll_selected_tag_generation_service_with_guard_89526(void)

{
  char cVar1;
  uint uVar2;
  uint32_t puVar3;
  uint uVar4;
  
  puVar3 = 0xfebeb800u;
  thunk_push_priority_mask_and_raise_to_ff00_6a45e();
  uVar2 = (*((uint *)camry_host_ptr((uint32_t)(puVar3 + 0x5b74))));
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x5b78)))));
  uVar4 = (*((uint *)camry_host_ptr((uint32_t)(0x5b70u + (int)puVar3))));
  thunk_pop_and_restore_priority_mask_stack_6a4c4();
  if (((int8_t)cVar1) == -0x5b) {
    if (uVar4 == ~uVar2) {
      if ((uVar4 != 0) && ((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(uVar4 + 0x18))))) != 0u)) {
        (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(uVar4 + 0x18))))))))))))();
      }
    }
    else {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x5b79))))) = 1;
      reset_tag_generation_service_selection_89414();
    }
  }
  return 0;
}

void initialize_tag_verification_service_slot_and_lock_895a4(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  thunk_push_priority_mask_and_raise_to_ff00_6a45e();
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x5b80)))) = 0xffffffff;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x5b7c)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x5b86))))) = 0xd2;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x5b85))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x5b84))))) = 0xe1;
  thunk_pop_and_restore_priority_mask_stack_6a4c4();
  return;
}

bool try_acquire_tag_verification_service_lock_895d0(void)

{
  char cVar1;
  uint32_t puVar2;
  puVar2 = 0xfebeb800u;
  thunk_push_priority_mask_and_raise_to_ff00_6a45e();
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x5b86)))));
  if (((int8_t)cVar1) == -0x2e) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x5b86))))) = 0xe1;
  }
  thunk_pop_and_restore_priority_mask_stack_6a4c4();
  return cVar1 == -0x2e;
}

short * find_tag_verification_service_descriptor_by_u16_id_895f8(short param_1)

{
  uint uVar1;
  
  uVar1 = 0;
  do {
    if (*(short *)(((undefined *)camry_host_ptr((uint32_t)(0x27de8u + (uint32_t)(uVar1 * 0x20) * 1u)))) == param_1) {
      return (short *)(((undefined *)camry_host_ptr((uint32_t)(0x27de8u + (uint32_t)(uVar1 * 0x20) * 1u))));
    }
    uVar1 = uVar1 + 1;
  } while (uVar1 < 2);
  return (short *)0x0;
}

void reset_tag_verification_service_selection_8961a(void)

{
  DAT_febf137c = 0;
  DAT_febf1384 = 0xe1;
  DAT_febf1380 = 0xffffffff;
  return;
}

void release_tag_verification_service_lock_8962e(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  thunk_push_priority_mask_and_raise_to_ff00_6a45e();
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x5b86))))) = 0xd2;
  thunk_pop_and_restore_priority_mask_stack_6a4c4();
  return;
}

int dispatch_tag_verification_service_by_id_when_idle_89646(undefined2 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4,
                undefined4 param_5,undefined4 param_6,undefined4 param_7)

{
  char cVar1;
  uint32_t puVar2;
  undefined4 uVar3;
  int iVar4;
  uint uVar5;
  uint32_t pcVar6;
  
  puVar2 = 0xfebeb800u;
  iVar4 = try_acquire_tag_verification_service_lock_895d0();
  if (iVar4 == 1) {
    cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x5b84)))));
    if (((int8_t)cVar1) == -0x1f) {
      uVar5 = camry_host_addr(find_tag_verification_service_descriptor_by_u16_id_895f8(param_1));
      if ((uVar5 == 0) || (pcVar6 = (uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(uVar5 + 0x14))))),(uint32_t)(pcVar6) == 0u)) {
        reset_tag_verification_service_selection_8961a();
        iVar4 = 1;
      }
      else {
        uVar3 = (*((undefined4 *)camry_host_ptr((uint32_t)(uVar5 + 0x1c))));
        (*((uint *)camry_host_ptr((uint32_t)(puVar2 + 0x5b80)))) = ~uVar5;
        (*((uint *)camry_host_ptr((uint32_t)(puVar2 + 0x5b7c)))) = uVar5;
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x5b84))))) = 0xa5;
        iVar4 = (*(int (*)())camry_indirect((uint32_t)(pcVar6)))(uVar3,param_2,param_3,param_4,param_5,param_6,param_7);
        if (iVar4 != 0) {
          reset_tag_verification_service_selection_8961a();
        }
      }
    }
    else if (((int8_t)cVar1) == -0x5b) {
      iVar4 = 2;
    }
    else {
      iVar4 = 1;
      if (cVar1 != '\0') {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x5b84))))) = 0;
      }
    }
    release_tag_verification_service_lock_8962e();
  }
  else {
    iVar4 = 2;
  }
  return iVar4;
}

void finish_tag_verification_service_with_guarded_callback_896e0(undefined1 param_1)

{
  uint uVar1;
  
  uVar1 = DAT_febf137c;
  if (((int8_t)DAT_febf1384) == -0x5b) {
    if (DAT_febf137c == ~DAT_febf1380) {
      if ((DAT_febf137c != 0) && ((*((int *)camry_host_ptr((uint32_t)(DAT_febf137c + 4)))) != 0)) {
        reset_tag_verification_service_selection_8961a();
        (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(uVar1 + 4))))))))))))(param_1);
      }
    }
    else {
      DAT_febf1385 = 1;
      reset_tag_verification_service_selection_8961a();
    }
  }
  return;
}

undefined4 poll_selected_tag_verification_service_with_guard_8972a(void)

{
  char cVar1;
  uint uVar2;
  uint32_t puVar3;
  uint uVar4;
  
  puVar3 = 0xfebeb800u;
  thunk_push_priority_mask_and_raise_to_ff00_6a45e();
  uVar2 = (*((uint *)camry_host_ptr((uint32_t)(puVar3 + 0x5b80))));
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x5b84)))));
  uVar4 = (*((uint *)camry_host_ptr((uint32_t)(puVar3 + 0x5b7c))));
  thunk_pop_and_restore_priority_mask_stack_6a4c4();
  if (((int8_t)cVar1) == -0x5b) {
    if (uVar4 == ~uVar2) {
      if ((uVar4 != 0) && ((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(uVar4 + 0x18))))) != 0u)) {
        (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(uVar4 + 0x18))))))))))))();
      }
    }
    else {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x5b85))))) = 1;
      reset_tag_verification_service_selection_8961a();
    }
  }
  return 0;
}

void initialize_single_block_crypto_service_slot_and_lock_897a8(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  thunk_push_priority_mask_and_raise_to_ff00_6a45e();
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x5b8c)))) = 0xffffffff;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x5b88)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x5b92))))) = 0xd2;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x5b91))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x5b90))))) = 0xe1;
  thunk_pop_and_restore_priority_mask_stack_6a4c4();
  return;
}

bool try_acquire_single_block_crypto_service_lock_897d4(void)

{
  char cVar1;
  uint32_t puVar2;
  puVar2 = 0xfebeb800u;
  thunk_push_priority_mask_and_raise_to_ff00_6a45e();
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x5b92)))));
  if (((int8_t)cVar1) == -0x2e) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x5b92))))) = 0xe1;
  }
  thunk_pop_and_restore_priority_mask_stack_6a4c4();
  return cVar1 == -0x2e;
}

undefined2 * match_single_block_crypto_service_u16_id_897fc(short param_1)

{
  undefined2 *puVar1;
  
  puVar1 = ((undefined *)camry_host_ptr(0x27e2cu));
  if (DAT_00027e2c != param_1) {
    puVar1 = (undefined2 *)0x0;
  }
  return puVar1;
}

void reset_single_block_crypto_service_selection_8980c(void)

{
  DAT_febf1388 = 0;
  DAT_febf1390 = 0xe1;
  DAT_febf138c = 0xffffffff;
  return;
}

void release_single_block_crypto_service_lock_89820(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  thunk_push_priority_mask_and_raise_to_ff00_6a45e();
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x5b92))))) = 0xd2;
  thunk_pop_and_restore_priority_mask_stack_6a4c4();
  return;
}

int dispatch_single_block_crypto_service_by_id_when_idle_89838(undefined2 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4,
                undefined4 param_5,undefined4 param_6)

{
  char cVar1;
  uint32_t puVar2;
  undefined4 uVar3;
  int iVar4;
  uint uVar5;
  uint32_t pcVar6;
  
  puVar2 = 0xfebeb800u;
  iVar4 = try_acquire_single_block_crypto_service_lock_897d4();
  if (iVar4 == 1) {
    cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x5b90)))));
    if (((int8_t)cVar1) == -0x1f) {
      uVar5 = camry_host_addr(match_single_block_crypto_service_u16_id_897fc(param_1));
      if ((uVar5 == 0) || (pcVar6 = (uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(uVar5 + 0x14))))),(uint32_t)(pcVar6) == 0u)) {
        reset_single_block_crypto_service_selection_8980c();
        iVar4 = 1;
      }
      else {
        uVar3 = (*((undefined4 *)camry_host_ptr((uint32_t)(uVar5 + 0x1c))));
        (*((uint *)camry_host_ptr((uint32_t)(puVar2 + 0x5b8c)))) = ~uVar5;
        (*((uint *)camry_host_ptr((uint32_t)(puVar2 + 0x5b88)))) = uVar5;
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x5b90))))) = 0xa5;
        iVar4 = (*(int (*)())camry_indirect((uint32_t)(pcVar6)))(uVar3,param_2,param_3,param_4,param_5,param_6);
        if (iVar4 != 0) {
          reset_single_block_crypto_service_selection_8980c();
        }
      }
    }
    else if (((int8_t)cVar1) == -0x5b) {
      iVar4 = 2;
    }
    else {
      iVar4 = 1;
      if (cVar1 != '\0') {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x5b90))))) = 0;
      }
    }
    release_single_block_crypto_service_lock_89820();
  }
  else {
    iVar4 = 2;
  }
  return iVar4;
}

void reset_then_dispatch_validated_slot4_callback_898ce(undefined1 param_1)

{
  uint uVar1;
  
  uVar1 = DAT_febf1388;
  if (((int8_t)DAT_febf1390) == -0x5b) {
    if (DAT_febf1388 == ~DAT_febf138c) {
      if ((DAT_febf1388 != 0) && ((*((int *)camry_host_ptr((uint32_t)(DAT_febf1388 + 4)))) != 0)) {
        reset_single_block_crypto_service_selection_8980c();
        (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(uVar1 + 4))))))))))))(param_1);
      }
    }
    else {
      DAT_febf1391 = 1;
      reset_single_block_crypto_service_selection_8980c();
    }
  }
  return;
}

undefined4 dispatch_validated_slot18_callback_return_zero_89918(void)

{
  char cVar1;
  uint uVar2;
  uint32_t puVar3;
  uint uVar4;
  
  puVar3 = 0xfebeb800u;
  thunk_push_priority_mask_and_raise_to_ff00_6a45e();
  uVar2 = (*((uint *)camry_host_ptr((uint32_t)(puVar3 + 0x5b8c))));
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x5b90)))));
  uVar4 = (*((uint *)camry_host_ptr((uint32_t)(puVar3 + 0x5b88))));
  thunk_pop_and_restore_priority_mask_stack_6a4c4();
  if (((int8_t)cVar1) == -0x5b) {
    if (uVar4 == ~uVar2) {
      if ((uVar4 != 0) && ((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(uVar4 + 0x18))))) != 0u)) {
        (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(uVar4 + 0x18))))))))))))();
      }
    }
    else {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x5b91))))) = 1;
      reset_single_block_crypto_service_selection_8980c();
    }
  }
  return 0;
}

void initialize_descriptor1394_and_lock_markers_89996(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  thunk_push_priority_mask_and_raise_to_ff00_6a45e();
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x5b98)))) = 0xffffffff;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x5b94)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x5b9e))))) = 0xd2;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x5b9d))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x5b9c))))) = 0xe1;
  thunk_pop_and_restore_priority_mask_stack_6a4c4();
  return;
}

bool try_acquire_marker139e_899c2(void)

{
  char cVar1;
  uint32_t puVar2;
  puVar2 = 0xfebeb800u;
  thunk_push_priority_mask_and_raise_to_ff00_6a45e();
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x5b9e)))));
  if (((int8_t)cVar1) == -0x2e) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x5b9e))))) = 0xe1;
  }
  thunk_pop_and_restore_priority_mask_stack_6a4c4();
  return cVar1 == -0x2e;
}

undefined2 * lookup_descriptor27e50_by_u16_key_899ea(short param_1)

{
  undefined2 *puVar1;
  
  puVar1 = ((undefined *)camry_host_ptr(0x27e50u));
  if (DAT_00027e50 != param_1) {
    puVar1 = (undefined2 *)0x0;
  }
  return puVar1;
}

void reset_descriptor1394_899fa(void)

{
  DAT_febf1394 = 0;
  DAT_febf139c = 0xe1;
  DAT_febf1398 = 0xffffffff;
  return;
}

void release_marker139e_89a0e(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  thunk_push_priority_mask_and_raise_to_ff00_6a45e();
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x5b9e))))) = 0xd2;
  thunk_pop_and_restore_priority_mask_stack_6a4c4();
  return;
}

int start_locked_descriptor1394_operation_89a26(undefined2 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4,
                undefined4 param_5,undefined4 param_6)

{
  char cVar1;
  uint32_t puVar2;
  undefined4 uVar3;
  int iVar4;
  uint uVar5;
  uint32_t pcVar6;
  
  puVar2 = 0xfebeb800u;
  iVar4 = try_acquire_marker139e_899c2();
  if (iVar4 != 1) {
    return 2;
  }
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x5b9c)))));
  if (((int8_t)cVar1) == -0x1f) {
    uVar5 = camry_host_addr(lookup_descriptor27e50_by_u16_key_899ea(param_1));
    if ((uVar5 != 0) && (pcVar6 = (uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(uVar5 + 0x14))))),(uint32_t)(pcVar6) != 0u)) {
      uVar3 = (*((undefined4 *)camry_host_ptr((uint32_t)(uVar5 + 0x1c))));
      (*((uint *)camry_host_ptr((uint32_t)(puVar2 + 0x5b98)))) = ~uVar5;
      (*((uint *)camry_host_ptr((uint32_t)(puVar2 + 0x5b94)))) = uVar5;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x5b9c))))) = 0xa5;
      iVar4 = (*(int (*)())camry_indirect((uint32_t)(pcVar6)))(uVar3,param_2,param_3,param_4,param_5,param_6);
      if (iVar4 != 0) {
        reset_descriptor1394_899fa();
      }
      goto LAB_00089aa8;
    }
    reset_descriptor1394_899fa();
  }
  else if (cVar1 != '\0') {
    if (((int8_t)cVar1) == -0x5b) {
      iVar4 = 2;
    }
    else {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x5b9c))))) = 0;
      iVar4 = 1;
    }
    goto LAB_00089aa8;
  }
  iVar4 = 1;
LAB_00089aa8:
  release_marker139e_89a0e();
  return iVar4;
}

void crypto_key_job_deliver_completion(uchar result)

{
  uint uVar1;
  
  uVar1 = DAT_febf1394;
  if (((int8_t)DAT_febf139c) == -0x5b) {
    if (DAT_febf1394 == ~DAT_febf1398) {
      if ((DAT_febf1394 != 0) && ((*((int *)camry_host_ptr((uint32_t)(DAT_febf1394 + 4)))) != 0)) {
        reset_descriptor1394_899fa();
        (*(int (*)())camry_indirect((uint32_t)(*((code * *)camry_host_ptr((uint32_t)(uVar1 + 4))))))(result);
      }
    }
    else {
      DAT_febf139d = 1;
      reset_descriptor1394_899fa();
    }
  }
  return;
}

undefined4 dispatch_validated_descriptor1394_slot18_89b06(void)

{
  char cVar1;
  uint uVar2;
  uint32_t puVar3;
  uint uVar4;
  
  puVar3 = 0xfebeb800u;
  thunk_push_priority_mask_and_raise_to_ff00_6a45e();
  uVar2 = (*((uint *)camry_host_ptr((uint32_t)(puVar3 + 0x5b98))));
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x5b9c)))));
  uVar4 = (*((uint *)camry_host_ptr((uint32_t)(puVar3 + 0x5b94))));
  thunk_pop_and_restore_priority_mask_stack_6a4c4();
  if (((int8_t)cVar1) == -0x5b) {
    if (uVar4 == ~uVar2) {
      if ((uVar4 != 0) && ((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(uVar4 + 0x18))))) != 0u)) {
        (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(uVar4 + 0x18))))))))))))();
      }
    }
    else {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x5b9d))))) = 1;
      reset_descriptor1394_899fa();
    }
  }
  return 0;
}

undefined4 set_word13a0_when_status_one_89b84(undefined4 param_1,undefined4 param_2)

{
  uint32_t puVar1;
  int iVar2;
  byte bStack_9;
  
  puVar1 = 0xfebeb800u;
  bStack_9 = 3;
  iVar2 = aggregate_callback_marker_status_89e72(&bStack_9);
  if (iVar2 == 0) {
    if (bStack_9 == 1) {
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x5ba0)))) = param_2;
      return 0;
    }
    if (bStack_9 == 2) {
      return 2;
    }
  }
  return 1;
}

undefined4 set_words13a4_and13a8_89bb6(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  DAT_febf13a4 = param_2;
  DAT_febf13a8 = param_3;
  return 0;
}

int submit_89440_and_poll_completion13bc_89bc2(undefined2 param_1,undefined4 param_2,undefined4 *param_3,undefined1 param_4)

{
  char cVar1;
  uint uVar2;
  uint32_t puVar3;
  int iVar4;
  uint32_t puVar5;
  
  DAT_febf13bc = 0;
  DAT_febf13bd = 1;
  puVar3 = 0xfebeb800u;
  if (camry_host_addr((param_3))== 0) {
    puVar5 = (0x0);
  }
  else {
    DAT_febf13ac = *param_3;
    puVar5 = (0xfebf13acu);
  }
  iVar4 = dispatch_tag_generation_service_by_id_when_idle_89440(param_1, DAT_febf13a0, DAT_febf13a4, DAT_febf13a8, param_2, (puVar5), param_4);
  if (iVar4 == 0) {
    uVar2 = 0;
    do {
      cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x5bbc)))));
      if (cVar1 == '\x01') {
        if (camry_host_addr((param_3))!= 0) {
          *param_3 = (*((undefined4 *)camry_host_ptr((uint32_t)(puVar3 + 0x5bac))));
          iVar4 = 0;
          if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x5bbd))))) == '\0') break;
        }
        iVar4 = 1;
        break;
      }
      uVar2 = uVar2 + 1;
    } while (uVar2 < 0xe07);
    if (cVar1 == '\0') {
      iVar4 = 2;
    }
  }
  else if (iVar4 != 2 && iVar4 != 3) {
    iVar4 = 1;
  }
  return iVar4;
}

undefined4 set_word13b0_when_status_one_89c5a(undefined4 param_1,undefined4 param_2)

{
  uint32_t puVar1;
  int iVar2;
  byte bStack_9;
  
  puVar1 = 0xfebeb800u;
  bStack_9 = 3;
  iVar2 = aggregate_callback_marker_status_89e72(&bStack_9);
  if (iVar2 == 0) {
    if (bStack_9 == 1) {
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x5bb0)))) = param_2;
      return 0;
    }
    if (bStack_9 == 2) {
      return 2;
    }
  }
  return 1;
}

undefined4 set_words13b4_and13b8_89c8c(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  DAT_febf13b4 = param_2;
  DAT_febf13b8 = param_3;
  return 0;
}

uint submit_89646_and_poll_completion13be_89c98(undefined2 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  uint uVar1;
  uint32_t puVar2;
  uint uVar3;
  
  puVar2 = 0xfebeb800u;
  DAT_febf13be = 0;
  DAT_febf13bf = 1;
  uVar3 = dispatch_tag_verification_service_by_id_when_idle_89646(param_1,DAT_febf13b0,DAT_febf13b4,DAT_febf13b8,param_2,param_3,param_4);
  if (uVar3 == 0) {
    uVar1 = 0;
    do {
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x5bbe))))) == '\x01') {
        uVar3 = (uint)((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x5bbf))))) != '\0');
        break;
      }
      uVar1 = uVar1 + 1;
    } while (uVar1 < 0xe07);
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x5bbe))))) == '\0') {
      uVar3 = 2;
    }
  }
  else if (uVar3 != 2) {
    uVar3 = 1;
  }
  return uVar3;
}

undefined4 write_zero_u16_if_nonnull_89d08(undefined2 *param_1)

{
  if (camry_host_addr((param_1))!= 0) {
    *param_1 = 0;
    return 0;
  }
  return 1;
}

void invoke_callback_array27e90_89d18(void)

{
  undefined8 uVar1;
  int iVar2;
  uint uVar3;
  
  uVar1 = 0x23dfc00000000;
  for (uVar3 = 0; iVar2 = (int)((ulonglong)uVar1 >> 0x20), uVar3 < (*((uint *)camry_host_ptr((uint32_t)(iVar2 + 0x4078))));
      uVar3 = uVar3 + 1) {
    (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(uVar3 * 4 + iVar2 + 0x4094))))))))))))();
  }
  return;
}

void initialize_round_robin_after_8844e_89d3c(void)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  iVar2 = thunk_initialize_crypto_scheduler_with_three_step_check_8844e();
  if (iVar2 == 0) {
    invoke_callback_array27e90_89d18();
  }
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x5bc0)))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + 0x5bc8)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x5bca))))) = 1;
  return;
}

void initialize_round_robin_after_884ea_89d5e(void)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  iVar2 = thunk_initialize_crypto_scheduler_without_three_step_check_884ea();
  if (iVar2 == 0) {
    invoke_callback_array27e90_89d18();
  }
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x5bc0)))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + 0x5bc8)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x5bca))))) = 1;
  return;
}

int run_round_robin_callback_with_busy_holdoff_89d80(void)

{
  uint32_t puVar1;
  uint32_t puVar2;
  int iVar3;
  uint uVar4;
  
  puVar1 = 0xfebeb800u;
  puVar2 = 0x23dfcu;
  if (DAT_febf13ca == '\x01') {
    DAT_febf13ca = '\0';
    DAT_febf13c4 = 0;
  }
  uVar4 = DAT_febf13c0;
  if (DAT_00027e7c <= DAT_febf13c0) {
    uVar4 = 0;
  }
  iVar3 = (*(int (*)())camry_indirect((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x27eb0u + (uint32_t)(uVar4) * 4u))))))();
  if (iVar3 == 2) {
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x5bc4)))) = (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0x4080))));
  }
  if ((*((int *)camry_host_ptr((uint32_t)(puVar1 + 0x5bc4)))) != 0) {
    iVar3 = 2;
    (*((int *)camry_host_ptr((uint32_t)(puVar1 + 0x5bc4)))) = (*((int *)camry_host_ptr((uint32_t)(puVar1 + 0x5bc4)))) + -1;
  }
  (*((uint *)camry_host_ptr((uint32_t)(puVar1 + 0x5bc0)))) = uVar4 + 1;
  return iVar3;
}

void invoke_optional_callback27d9c_u16_89dd6(undefined2 param_1)

{
  if (PTR_FUN_00027d9c != 0) {
    (*(int (*)())camry_indirect((uint32_t)(PTR_FUN_00027d9c)))(param_1);
  }
  return;
}

void run_round_robin_and_postcycle_callbacks_89dec(void)

{
  undefined8 uVar1;
  int iVar2;
  uint uVar3;
  
  uVar1 = 0x23dfcfebeb800;
  iVar2 = thunk_combine_icus_readiness_with_crypto_scheduler_status_886e0();
  if (iVar2 == 0) {
    iVar2 = ((void)(0), run_round_robin_callback_with_busy_holdoff_89d80());
  }
  (*((short *)camry_host_ptr((uint32_t)((int)uVar1 + 0x5bc8)))) = (short)iVar2;
  if (iVar2 != 0) {
    invoke_optional_callback27d9c_u16_89dd6(iVar2);
  }
  for (uVar3 = 0; iVar2 = (int)((ulonglong)uVar1 >> 0x20), uVar3 < (*((uint *)camry_host_ptr((uint32_t)(iVar2 + 0x4074))));
      uVar3 = uVar3 + 1) {
    (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(uVar3 * 4 + iVar2 + 0x4084))))))))))))();
  }
  return;
}

void count_marker_in_four_categories_89e2c(char param_1,int *param_2)

{
  if (param_1 == '\0') {
    *param_2 = *param_2 + 1;
    return;
  }
  if (param_1 == -0x1f) {
    param_2[1] = param_2[1] + 1;
    return;
  }
  if ((((param_1 != -0x5b) && (param_1 != -0x4c)) && (param_1 != -0x3d)) && (param_1 != -0x2e)) {
    param_2[3] = param_2[3] + 1;
    return;
  }
  param_2[2] = param_2[2] + 1;
  return;
}

undefined4 aggregate_callback_marker_status_89e72(undefined1 *param_1)

{
  uint8_t stack_record_20[32];
  undefined1 uVar1;
  undefined8 uVar2;
  int iVar3;
  undefined4 uVar4;
  uint uVar5;
  
  uVar2 = 0x23dfc00000000;
  if (camry_host_addr((param_1))== 0) {
    return 1;
  }
  (*((int32_t *)(stack_record_20 + 4))) = 0;
  (*((int32_t *)(stack_record_20 + 0))) = 0;
  (*((int32_t *)(stack_record_20 + 12))) = 0;
  (*((int32_t *)(stack_record_20 + 8))) = 0;
  for (uVar5 = 0; iVar3 = (int)((ulonglong)uVar2 >> 0x20), uVar5 < (*((uint *)camry_host_ptr((uint32_t)(iVar3 + 0x407c))));
      uVar5 = uVar5 + 1) {
    uVar4 = (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x40a2u + uVar5 * 4 + iVar3 + 2))))))))))))();
    count_marker_in_four_categories_89e2c(uVar4,stack_record_20);
  }
  if ((*((int32_t *)(stack_record_20 + 8))) != 0) {
    uVar1 = 2;
    goto LAB_00089eda;
  }
  if ((*((int32_t *)(stack_record_20 + 12))) == 0) {
    if ((*((int32_t *)(stack_record_20 + 0))) == 0) {
      if ((*((int32_t *)(stack_record_20 + 4))) != 0) {
        uVar1 = 1;
        goto LAB_00089eda;
      }
    }
    else {
      uVar1 = 0;
      if ((*((int32_t *)(stack_record_20 + 4))) == 0) goto LAB_00089eda;
    }
  }
  uVar1 = 3;
LAB_00089eda:
  *param_1 = uVar1;
  return 0;
}
