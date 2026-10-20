#include "common.h"

void deliver_or_defer_key_job_completion_88086(undefined1 param_1)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_febf10e8 != 0) {
    if (~(uint)DAT_febf10e8 == DAT_febf10ec) {
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(DAT_febf10e8)))) == '\x01') {
        complete_key_job_copy_48bytes_or_clear_output_87fd8((uint)(byte)param_1);
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x58f0))))) = 0xd2;
        return;
      }
    }
    else {
      DAT_febf1191 = 1;
    }
  }
  DAT_febf10f0 = 0xe1;
  DAT_febf10f1 = param_1;
  if (((int8_t)DAT_febf1190) == -0x3d) {
    release_icus_request_and_notify_crypto_scheduler_87edc(0);
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x5990))))) = 0xe1;
  }
  return;
}

void poll_icus_key_request_and_route_completion_880e0(void)

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
    deliver_or_defer_key_job_completion_88086(uVar3);
  }
  return;
}

undefined4 start_prepared_icus_key_request_from_state_c3_8813c(void)

{
  uint32_t puVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  
  puVar1 = 0xfebeb800u;
  uVar4 = 1;
  if (((int8_t)DAT_febf1190) == -0x3d) {
    DAT_febf1194 = 0x880e0u;
    DAT_febf1198 = 0xfff77f1f;
    DAT_febf1190 = -0x4c;
    iVar2 = prepare_icus_command_eight_four_in_three_out_8aa6a(((undefined *)camry_host_ptr(0xfebf10f4u)));
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

int schedule_64byte_key_job_with_guarded_callbacks_88198(uint param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4,
                undefined4 param_5,undefined4 param_6)

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
    iVar3 = prepare_64byte_key_request_with_48byte_output_87f52(((void *)camry_host_ptr((uint32_t)(param_2))), param_3, param_4, param_5, ((uint *)camry_host_ptr((uint32_t)(param_6))));
    if (iVar3 != 0) goto LAB_0008827e;
    (*((uint *)camry_host_ptr((uint32_t)(puVar2 + 0x58e8)))) = param_1;
    (*((uint *)camry_host_ptr((uint32_t)(puVar2 + 0x58ec)))) = ~param_1;
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar2 + 0x597c)))) = 0x8813cu;
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0x5988)))) = 0xfff77ec3;
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar2 + 0x5980)))) = 0x88086u;
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0x598c)))) = 0xfff77f79;
    thunk_nvm_request_suspend_with_service_guards_7995c();
    cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x5990)))));
    if (((int8_t)cVar1) == -0x3d) {
LAB_00088256:
      iVar3 = start_prepared_icus_key_request_from_state_c3_8813c();
      if (iVar3 == 0) goto LAB_0008827e;
      goto LAB_00088260;
    }
    if ((((int8_t)cVar1) == -0x2e) || (((int8_t)cVar1) == -0x4c)) goto LAB_0008827e;
  }
  else {
    if (((int8_t)cVar1) == -0x3d) {
      iVar3 = prepare_64byte_key_request_with_48byte_output_87f52(((void *)camry_host_ptr((uint32_t)(param_2))), param_3, param_4, param_5, ((uint *)camry_host_ptr((uint32_t)(param_6))));
      if (iVar3 == 0) {
        (*((uint *)camry_host_ptr((uint32_t)(puVar2 + 0x58e8)))) = param_1;
        (*((uint *)camry_host_ptr((uint32_t)(puVar2 + 0x58ec)))) = ~param_1;
        (*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar2 + 0x5980)))) = 0x88086u;
        (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0x598c)))) = 0xfff77f79;
        goto LAB_00088256;
      }
LAB_00088260:
      release_icus_request_and_notify_crypto_scheduler_87edc(0);
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x5990))))) = 0xe1;
      goto LAB_0008827e;
    }
    if ((((int8_t)cVar1) == -0x2e) || (((int8_t)cVar1) == -0x4c)) {
      iVar3 = 2;
      goto LAB_0008827e;
    }
  }
  iVar3 = 1;
LAB_0008827e:
  release_crypto_job_lock_88436();
  return iVar3;
}

void service_key_job_deferred_completion_and_timeouts_88290(void)

{
  uint uVar1;
  uint uVar2;
  char cVar3;
  uint32_t puVar4;
  int iVar5;
  
  puVar4 = 0xfebeb800u;
  if (((int8_t)DAT_febf10f0) == -0x1f) {
    puVar4 = 0xfebeb800u;
    complete_key_job_copy_48bytes_or_clear_output_87fd8(DAT_febf10f1);
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x58f0))))) = 0xd2;
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
      goto LAB_00088340;
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
LAB_00088340:
  deliver_or_defer_key_job_completion_88086(1);
  return;
}

undefined4 check_key_completion_state_encoding_8834a(void)

{
  undefined4 uVar1;
  
  if (((int8_t)DAT_febf10f0) != -0x1f) {
    if (((int8_t)DAT_febf10f0) == -0x2e) {
      uVar1 = 0;
    }
    else {
      uVar1 = 2;
    }
    return uVar1;
  }
  return 0;
}

bool try_acquire_crypto_job_lock_88362(void)

{
  char cVar1;
  uint32_t puVar2;
  puVar2 = 0xfebeb800u;
  thunk_push_priority_mask_and_raise_to_ff00_6a45e();
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x596c)))));
  if (((int8_t)cVar1) == -0x2e) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x596c))))) = 0xe1;
  }
  thunk_pop_and_restore_priority_mask_stack_6a4c4();
  return cVar1 == -0x2e;
}

void run_init_chain_8838a(void)

{
  reset_tag_generation_job_buffers_88b52();
  reset_tag_verification_job_buffers_88f92();
  reset_single_block_crypto_job_buffers_8874c();
  reset_key_job_buffers_and_completion_state_87f22();
  return;
}

void release_or_cancel_crypto_scheduler_by_state_883a2(undefined1 param_1)

{
  if (((int8_t)DAT_febf1190) == -0x2e) {
    thunk_nvm_cancel_or_resume_suspend_and_clear_state_799da();
  }
  else if ((((int8_t)DAT_febf1190) == -0x3d) || (((int8_t)DAT_febf1190) == -0x4c)) {
    release_icus_request_and_notify_crypto_scheduler_87edc(param_1);
  }
  return;
}

int submit_icus_sequence_step_and_poll_up_to_2500_883cc(undefined4 param_1)

{
  int iVar1;
  int iVar2;
  
  iVar1 = load_icus_parameters_or_start_mode_check_8ae2e(((undefined4 *)camry_host_ptr((uint32_t)(param_1))));
  iVar2 = 0x9c4;
  do {
    if (iVar1 != 0) {
      return iVar1;
    }
    iVar1 = service_icus_feed_drain_and_completion_callbacks_8af10();
    iVar2 = iVar2 + -1;
  } while (iVar2 != 0);
  return iVar1;
}

bool run_three_icus_sequence_steps_returns_failure_883e8(void)
{
  uint32_t record[4];
  int result;
  record[0] = 0;
  record[1] = camry_tp + 0x3f70u;
  record[2] = camry_host_addr(record);
  record[3] = 0;
  result = submit_icus_sequence_step_and_poll_up_to_2500_883cc(camry_host_addr(record + 2));
  if (result != 1) return true;
  record[0] = 1;
  record[2] = camry_host_addr(record);
  result = submit_icus_sequence_step_and_poll_up_to_2500_883cc(camry_host_addr(record + 2));
  if (result != 1) return true;
  record[0] = 2;
  record[2] = camry_host_addr(record);
  result = submit_icus_sequence_step_and_poll_up_to_2500_883cc(camry_host_addr(record + 2));
  return result != 1;
}

void release_crypto_job_lock_88436(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  thunk_push_priority_mask_and_raise_to_ff00_6a45e();
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x596c))))) = 0xd2;
  thunk_pop_and_restore_priority_mask_stack_6a4c4();
  return;
}

undefined4 initialize_crypto_scheduler_with_three_step_check_8844e(void)

{
  uint32_t puVar1;
  int iVar2;
  undefined4 uVar3;
  
  puVar1 = 0xfebeb800u;
  set_eic292_293_mask_from_boolean_8a22c(0);
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x5998)))) = 0xffffffff;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x5988)))) = 0xffffffff;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x598c)))) = 0xffffffff;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x5994)))) = 0;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x597c)))) = 0;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x5980)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x5991))))) = 0;
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x5990))))) == '\x0f') {
    uVar3 = 1;
  }
  else {
    try_acquire_crypto_job_lock_88362();
    run_init_chain_8838a();
    iVar2 = initialize_icus_unless_irq_pending_8a4ce();
    if (iVar2 == 1) {
      release_or_cancel_crypto_scheduler_by_state_883a2(0);
      iVar2 = run_three_icus_sequence_steps_returns_failure_883e8();
      if (iVar2 == 0) {
        (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x5978)))) = 0;
        (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x5974)))) = 0;
        (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x5970)))) = 0;
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x5990))))) = 0xe1;
        set_eic292_293_mask_from_boolean_8a22c(1);
        uVar3 = 0;
      }
      else {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x5990))))) = 0xf;
        uVar3 = 1;
      }
    }
    else {
      uVar3 = 1;
      if (iVar2 == 2) {
        release_or_cancel_crypto_scheduler_by_state_883a2(1);
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x5990))))) = 0xf;
      }
      else {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x5990))))) = 0;
      }
    }
    release_crypto_job_lock_88436();
  }
  return uVar3;
}

undefined4 initialize_crypto_scheduler_without_three_step_check_884ea(void)

{
  uint32_t puVar1;
  int iVar2;
  undefined4 uVar3;
  
  puVar1 = 0xfebeb800u;
  set_eic292_293_mask_from_boolean_8a22c(0);
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x5998)))) = 0xffffffff;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x5988)))) = 0xffffffff;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x598c)))) = 0xffffffff;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x5994)))) = 0;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x597c)))) = 0;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x5980)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x5991))))) = 0;
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x5990))))) == '\x0f') {
    uVar3 = 1;
  }
  else {
    try_acquire_crypto_job_lock_88362();
    run_init_chain_8838a();
    iVar2 = initialize_icus_unless_irq_pending_8a4ce();
    if (iVar2 == 1) {
      release_or_cancel_crypto_scheduler_by_state_883a2(0);
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x5970)))) = 0;
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x5974)))) = 0;
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x5978)))) = 0;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x5990))))) = 0xe1;
      set_eic292_293_mask_from_boolean_8a22c(1);
      uVar3 = 0;
    }
    else {
      uVar3 = 1;
      if (iVar2 == 2) {
        release_or_cancel_crypto_scheduler_by_state_883a2(1);
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x5990))))) = 0xf;
      }
      else {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x5990))))) = 0;
      }
    }
    release_crypto_job_lock_88436();
  }
  return uVar3;
}

undefined4 recover_icus_request_with_bounded_poll_and_reinitialization_88574(void)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  undefined4 uVar4;
  
  iVar1 = request_abort_for_busy_icus_operation_8aca8();
  iVar3 = 0x9c4;
  do {
    if (iVar1 != 0) break;
    iVar1 = service_icus_feed_drain_and_completion_callbacks_8af10();
    iVar3 = iVar3 + -1;
  } while (iVar3 != 0);
  if (((iVar1 == 0x20) || (iVar1 == 1)) ||
     ((iVar1 != 0 && (uVar2 = icus20_read_bit0(), uVar2 != 1)))) {
    uVar4 = 1;
  }
  else {
    uVar4 = 2;
  }
  run_init_chain_8838a();
  return uVar4;
}

void advance_crypto_scheduler_and_invoke_guarded_callbacks_885b2(char param_1)

{
  uint32_t pcVar1;
  uint uVar2;
  uint32_t puVar3;
  int iVar4;
  uint uVar5;
  
  uVar2 = DAT_febf118c;
  pcVar1 = (uint32_t)((uint32_t)(DAT_febf1180));
  puVar3 = 0xfebeb800u;
  if (((int8_t)DAT_febf1190) == -0x1f) {
    if (param_1 == '\0') {
      DAT_febf1174 = 0;
      DAT_febf1190 = 0xc3;
      return;
    }
    if (param_1 != '\x01') {
      return;
    }
    DAT_febf1170 = 0;
    DAT_febf1190 = 0xd2;
    return;
  }
  uVar5 = ~(uint)DAT_febf1180;
  if (((int8_t)DAT_febf1190) != -0x2e) {
    return;
  }
  if (param_1 == '\0') {
    DAT_febf1174 = 0;
    DAT_febf1190 = -0x3d;
    if (DAT_febf117c == 0x0u) {
      DAT_febf1174 = 0;
      DAT_febf1190 = 0xc3;
      return;
    }
    if (~(uint)DAT_febf117c == DAT_febf1188) {
      puVar3 = 0xfebeb800u;
      iVar4 = (*(int (*)())camry_indirect((uint32_t)(DAT_febf117c)))((uint)(byte)param_1);
      if (iVar4 == 0) {
        return;
      }
      if ((uint32_t)(pcVar1) == 0u) {
        return;
      }
      if (uVar5 == uVar2) goto LAB_0008863e;
    }
  }
  else {
    if (param_1 == '\x01') {
      return;
    }
    if (DAT_febf1180 == 0x0u) {
      return;
    }
    if (uVar5 == DAT_febf118c) {
      iVar4 = 1;
      DAT_febf1190 = -0x1f;
LAB_0008863e:
      (*(int (*)())camry_indirect((uint32_t)(pcVar1)))(iVar4);
      return;
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x5991))))) = 1;
  return;
}

int aggregate_crypto_scheduler_state_and_integrity_status_8864e(void)

{
  int iVar1;
  
  if ((((((int8_t)DAT_febf1190) == -0x4c) || (((int8_t)DAT_febf1190) == -0x3d)) || (((int8_t)DAT_febf1190) == -0x2e)) ||
     (((int8_t)DAT_febf1190) == -0x1f)) {
    if (((((int8_t)DAT_febf116c) == -0x2e) || (((int8_t)DAT_febf116c) == -0x1f)) && (DAT_febf1191 == '\0')) {
      iVar1 = check_tag_generation_completion_state_encoding_88f7a();
      if (((iVar1 == 0) && (iVar1 = check_tag_verification_completion_state_encoding_89386(), iVar1 == 0)) &&
         (iVar1 = check_single_block_crypto_completion_state_encoding_88b3a(), iVar1 == 0)) {
        iVar1 = check_key_completion_state_encoding_8834a();
      }
    }
    else {
      iVar1 = 2;
    }
  }
  else if (((int8_t)DAT_febf1190) == -0x5b) {
    if (DAT_febf1170 < 7) {
      iVar1 = 0x21;
      if (0xb < DAT_febf1178) {
        iVar1 = 0x22;
      }
    }
    else {
      iVar1 = 0x20;
    }
  }
  else if (DAT_febf1190 == '\x0f') {
    iVar1 = 3;
  }
  else if (DAT_febf1190 == '\0') {
    iVar1 = 1;
  }
  else {
    iVar1 = 2;
  }
  return iVar1;
}

undefined4 combine_icus_readiness_with_crypto_scheduler_status_886e0(void)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = get_icus_state_integrity_code_8b026();
  if (iVar1 == 1) {
    uVar2 = aggregate_crypto_scheduler_state_and_integrity_status_8864e();
  }
  else if (iVar1 == 0x1000) {
    uVar2 = 1;
  }
  else {
    uVar2 = 2;
  }
  return uVar2;
}

void invoke_guarded_active_crypto_poll_callback_88700(void)

{
  if (DAT_febf1194 != 0x0u) {
    if (~(uint)DAT_febf1194 == DAT_febf1198) {
      (*(int (*)())camry_indirect((uint32_t)(DAT_febf1194)))();
    }
    else {
      DAT_febf1191 = 1;
    }
  }
  return;
}

void invoke_guarded_crypto_poll_callback_alternate_entry_88726(void)

{
  if (DAT_febf1194 != 0x0u) {
    if (~(uint)DAT_febf1194 == DAT_febf1198) {
      (*(int (*)())camry_indirect((uint32_t)(DAT_febf1194)))();
    }
    else {
      DAT_febf1191 = 1;
    }
  }
  return;
}

void reset_single_block_crypto_job_buffers_8874c(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  memzero(((undefined *)camry_host_ptr(0xfebf11d8u)),0x1c);
  memzero(((undefined *)camry_host_ptr((uint32_t)(puVar1 + 0x59b0))), 0x28);
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x599c)))) = 0xffffffff;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x59a0)))) = 0xffffffff;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x59ac))))) = 0xd2;
  return;
}

undefined4 prepare_single_block_crypto_request_8877e(int *param_1,void *param_2,int param_3,uint param_4,uint *param_5)

{
  byte bVar1;
  uint32_t puVar2;
  undefined4 uVar3;
  
  puVar2 = 0xfebeb800u;
  if ((((camry_host_addr((param_1))== 0) || (camry_host_addr((param_2))== 0)) || (param_4 == 0)) ||
     (((camry_host_addr((param_5))== 0|| (*param_1 != 1)) || (param_3 != 0x10)))) {
    uVar3 = 1;
  }
  else if (*param_5 < 0x10) {
    uVar3 = 3;
  }
  else {
    uVar3 = 0;
    DAT_febf11d4 = camry_host_addr(param_5);
    DAT_febf119c = ~param_4;
    DAT_febf11a0 = ~(uint)camry_host_addr(param_5);
    DAT_febf11c0 = param_4;
    memcpy_forward(((undefined *)camry_host_ptr(0xfebf11b0u)),param_2,0x10);
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(0x59dc) * 1u)))) = ((uint32_t)((uint32_t)(puVar2 + 0x59f0)));
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0x59e4)))) = 1;
    bVar1 = *(byte *)(param_1 + 1);
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0x59ec)))) = 0;
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(0x59e0) * 1u)))) = ((uint32_t)(0xfebf11b0u));
    (*((uint *)camry_host_ptr((uint32_t)(puVar2 + 0x59e8)))) = (uint)bVar1;
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(23000) * 1u)))) = ((uint32_t)((uint32_t)(puVar2 + 0x59e0)));
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(0x59f0) * 1u)))) = ((uint32_t)(0xfebf11c4u));
  }
  return uVar3;
}

void complete_single_block_crypto_job_copy_bounded_output_88802(char param_1)

{
  void *destination;
  uint32_t puVar1;
  uint byte_count;
  
  destination = ((void *)camry_host_ptr((uint32_t)(DAT_febf11c0)));
  puVar1 = 0xfebeb800u;
  if ((DAT_febf11c0 == 0) || ((uintptr_t)(DAT_febf11d4)== 0)) {
    param_1 = '\x01';
  }
  else if ((~(uint)DAT_febf11c0 == DAT_febf119c) && (~(uint)DAT_febf11d4 == DAT_febf11a0)) {
    if (param_1 == '\0') {
      byte_count = (*((volatile uint32_t *)camry_host_ptr((uint32_t)(DAT_febf11d4))));
      if (0x10 < byte_count) {
        byte_count = 0x10;
      }
      (*((volatile uint32_t *)camry_host_ptr((uint32_t)(DAT_febf11d4)))) = byte_count;
      puVar1 = 0xfebeb800u;
      memcpy_forward(destination,((undefined *)camry_host_ptr(0xfebf11c4u)),byte_count);
    }
  }
  else {
    param_1 = '\x01';
    DAT_febf1191 = 1;
  }
  reset_then_dispatch_validated_slot4_callback_898ce(param_1);
  if (((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x5990)))))) == -0x3d) {
    release_icus_request_and_notify_crypto_scheduler_87edc(0);
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x5990))))) = 0xe1;
  }
  return;
}

void deliver_or_defer_single_block_crypto_completion_88876(undefined1 param_1)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_febf11a4 != 0) {
    if (~(uint)DAT_febf11a4 == DAT_febf11a8) {
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(DAT_febf11a4)))) == '\x01') {
        complete_single_block_crypto_job_copy_bounded_output_88802((uint)(byte)param_1);
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x59ac))))) = 0xd2;
        return;
      }
    }
    else {
      DAT_febf1191 = 1;
    }
  }
  DAT_febf11ac = 0xe1;
  DAT_febf11ad = param_1;
  if (((int8_t)DAT_febf1190) == -0x3d) {
    release_icus_request_and_notify_crypto_scheduler_87edc(0);
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x5990))))) = 0xe1;
  }
  return;
}

void poll_icus_single_block_job_and_route_completion_888d0(void)

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
    deliver_or_defer_single_block_crypto_completion_88876(uVar3);
  }
  return;
}

undefined4 start_prepared_single_block_icus_request_8892c(void)

{
  uint32_t puVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  
  puVar1 = 0xfebeb800u;
  uVar4 = 1;
  if (((int8_t)DAT_febf1190) == -0x3d) {
    DAT_febf1194 = 0x888d0u;
    DAT_febf1198 = 0xfff7772f;
    DAT_febf1190 = -0x4c;
    iVar2 = prepare_icus_command_one_or_three_8a63c(((undefined *)camry_host_ptr(0xfebf11d8u)));
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

int schedule_single_block_crypto_job_with_guarded_callbacks_88988(uint param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4,
                undefined4 param_5,undefined4 param_6)

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
    iVar3 = prepare_single_block_crypto_request_8877e(((int *)camry_host_ptr((uint32_t)(param_2))), ((void *)camry_host_ptr((uint32_t)(param_3))), param_4, param_5, ((uint *)camry_host_ptr((uint32_t)(param_6))));
    if (iVar3 != 0) goto LAB_00088a6e;
    (*((uint *)camry_host_ptr((uint32_t)(puVar2 + 0x59a4)))) = param_1;
    (*((uint *)camry_host_ptr((uint32_t)(puVar2 + 0x59a8)))) = ~param_1;
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar2 + 0x597c)))) = 0x8892cu;
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0x5988)))) = 0xfff776d3;
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar2 + 0x5980)))) = 0x88876u;
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0x598c)))) = 0xfff77789;
    thunk_nvm_request_suspend_with_service_guards_7995c();
    cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x5990)))));
    if (((int8_t)cVar1) == -0x3d) {
LAB_00088a46:
      iVar3 = start_prepared_single_block_icus_request_8892c();
      if (iVar3 == 0) goto LAB_00088a6e;
      goto LAB_00088a50;
    }
    if ((((int8_t)cVar1) == -0x2e) || (((int8_t)cVar1) == -0x4c)) goto LAB_00088a6e;
  }
  else {
    if (((int8_t)cVar1) == -0x3d) {
      iVar3 = prepare_single_block_crypto_request_8877e(((int *)camry_host_ptr((uint32_t)(param_2))), ((void *)camry_host_ptr((uint32_t)(param_3))), param_4, param_5, ((uint *)camry_host_ptr((uint32_t)(param_6))));
      if (iVar3 == 0) {
        (*((uint *)camry_host_ptr((uint32_t)(puVar2 + 0x59a4)))) = param_1;
        (*((uint *)camry_host_ptr((uint32_t)(puVar2 + 0x59a8)))) = ~param_1;
        (*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar2 + 0x5980)))) = 0x88876u;
        (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0x598c)))) = 0xfff77789;
        goto LAB_00088a46;
      }
LAB_00088a50:
      release_icus_request_and_notify_crypto_scheduler_87edc(0);
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x5990))))) = 0xe1;
      goto LAB_00088a6e;
    }
    if ((((int8_t)cVar1) == -0x2e) || (((int8_t)cVar1) == -0x4c)) {
      iVar3 = 2;
      goto LAB_00088a6e;
    }
  }
  iVar3 = 1;
LAB_00088a6e:
  release_crypto_job_lock_88436();
  return iVar3;
}

void service_single_block_crypto_completion_and_timeouts_88a80(void)

{
  uint uVar1;
  uint uVar2;
  char cVar3;
  uint32_t puVar4;
  int iVar5;
  
  puVar4 = 0xfebeb800u;
  if (((int8_t)DAT_febf11ac) == -0x1f) {
    puVar4 = 0xfebeb800u;
    complete_single_block_crypto_job_copy_bounded_output_88802(DAT_febf11ad);
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x59ac))))) = 0xd2;
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
      goto LAB_00088b30;
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
LAB_00088b30:
  deliver_or_defer_single_block_crypto_completion_88876(1);
  return;
}

undefined4 check_single_block_crypto_completion_state_encoding_88b3a(void)

{
  undefined4 uVar1;
  
  if (((int8_t)DAT_febf11ac) != -0x1f) {
    if (((int8_t)DAT_febf11ac) == -0x2e) {
      uVar1 = 0;
    }
    else {
      uVar1 = 2;
    }
    return uVar1;
  }
  return 0;
}

void reset_tag_generation_job_buffers_88b52(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  memzero(((undefined *)camry_host_ptr(0xfebf1208u)),0x18);
  memzero(((undefined *)camry_host_ptr((uint32_t)(puVar1 + 0x5a20))), 0x68);
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x59f8)))) = 0xffffffff;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x59f4)))) = 0xffffffff;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x5a04u + (uint32_t)((int)puVar1))))) = (code)0xd2;
  return;
}

undefined4
prepare_tag_generation_request_with_optional_truncation_88b84(int *param_1,void *param_2,uint param_3,uint param_4,uint *param_5,char param_6)

{
  byte bVar1;
  uint32_t puVar2;
  uint byte_count;
  
  puVar2 = 0xfebeb800u;
  if ((((camry_host_addr((param_1))!= 0) && (camry_host_addr((param_2))!= 0)) && (param_4 != 0)) &&
     (((camry_host_addr((param_5))!= 0&& (*param_1 == 1)) && (param_3 < 0x51)))) {
    if (param_6 == '\x01') {
      if (*param_5 != 0) {
LAB_00088bda:
        DAT_febf1220 = camry_host_addr(param_5);
        DAT_febf11f4 = ~(uint)camry_host_addr(param_5);
        DAT_febf11f8 = ~param_4;
        DAT_febf1284 = param_4;
        memcpy_forward(((undefined *)camry_host_ptr(0xfebf1224u)),param_2,param_3);
        byte_count = ~param_3 + 1 & 0xf;
        if (byte_count != 0) {
          memzero(((undefined *)camry_host_ptr((uint32_t)(0xfebf1224u + (uint32_t)(param_3) * 1u))),byte_count);
        }
        (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(0x5a0c) * 1u)))) = ((uint32_t)((uint32_t)(puVar2 + 0x5a1c)));
        bVar1 = *(byte *)(param_1 + 1);
        (*((volatile uint32_t *)camry_host_ptr((uint32_t)((0x5a04u + (int)(puVar2 + 4)))))) = ((uint32_t)((uint32_t)(puVar2 + 0x5a10)));
        (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(0x5a10) * 1u)))) = ((uint32_t)(0xfebf1224u));
        (*((uint *)camry_host_ptr((uint32_t)(puVar2 + 0x5a14)))) = param_3 << 3;
        (*((uint *)camry_host_ptr((uint32_t)(puVar2 + 0x5a18)))) = (uint)bVar1;
        (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(0x5a1c) * 1u)))) = ((uint32_t)((uint32_t)(puVar2 + 0x5a74)));
        return 0;
      }
    }
    else if (param_6 == '\0') {
      if (*param_5 < 0x10) {
        return 3;
      }
      goto LAB_00088bda;
    }
  }
  return 1;
}

void complete_tag_generation_job_copy_up_to_16bytes_88c36(char param_1)

{
  void *destination;
  uint32_t puVar1;
  uint byte_count;
  
  destination = ((void *)camry_host_ptr((uint32_t)(DAT_febf1284)));
  puVar1 = 0xfebeb800u;
  if ((DAT_febf1284 == 0) || ((uintptr_t)(DAT_febf1220)== 0)) {
    param_1 = '\x01';
  }
  else if ((~(uint)DAT_febf1284 == DAT_febf11f8) && (~(uint)DAT_febf1220 == DAT_febf11f4)) {
    if (param_1 == '\0') {
      byte_count = (*((volatile uint32_t *)camry_host_ptr((uint32_t)(DAT_febf1220))));
      if (0x10 < byte_count) {
        byte_count = 0x10;
      }
      (*((volatile uint32_t *)camry_host_ptr((uint32_t)(DAT_febf1220)))) = byte_count;
      puVar1 = 0xfebeb800u;
      memcpy_forward(destination,((undefined *)camry_host_ptr(0xfebf1274u)),byte_count);
    }
  }
  else {
    param_1 = '\x01';
    DAT_febf1191 = 1;
  }
  finish_tag_generation_service_with_guarded_callback_894dc(param_1);
  if (((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x5990)))))) == -0x3d) {
    release_icus_request_and_notify_crypto_scheduler_87edc(0);
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x5990))))) = 0xe1;
  }
  return;
}

void deliver_or_defer_tag_generation_completion_88caa(undefined1 param_1)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_febf11fc != 0) {
    if (~(uint)DAT_febf11fc == DAT_febf1200) {
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(DAT_febf11fc)))) == '\x01') {
        complete_tag_generation_job_copy_up_to_16bytes_88c36((uint)(byte)param_1);
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x5a04u + (uint32_t)((int)puVar1))))) = (code)0xd2;
        return;
      }
    }
    else {
      DAT_febf1191 = 1;
    }
  }
  DAT_febf1204 = 0xe1;
  DAT_febf1205 = param_1;
  if (((int8_t)DAT_febf1190) == -0x3d) {
    release_icus_request_and_notify_crypto_scheduler_87edc(0);
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x5990))))) = 0xe1;
  }
  return;
}

void poll_icus_tag_generation_and_route_completion_88d04(void)

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
    deliver_or_defer_tag_generation_completion_88caa(uVar3);
  }
  return;
}

undefined4 start_prepared_icus_tag_generation_request_88d60(void)

{
  uint32_t puVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  
  puVar1 = 0xfebeb800u;
  uVar4 = 1;
  if (((int8_t)DAT_febf1190) == -0x3d) {
    DAT_febf1194 = 0x88d04u;
    DAT_febf1198 = 0xfff772fb;
    DAT_febf1190 = -0x4c;
    iVar2 = prepare_icus_command_five_with_bit_length_8a720(((undefined *)camry_host_ptr(0xfebf1208u)));
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

int schedule_tag_generation_job_with_guarded_callbacks_88dbc(uint param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4,
                undefined4 param_5,undefined4 param_6,undefined1 param_7)

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
    iVar3 = prepare_tag_generation_request_with_optional_truncation_88b84(((int *)camry_host_ptr((uint32_t)(param_2))), ((void *)camry_host_ptr((uint32_t)(param_3))), param_4, param_5, ((uint *)camry_host_ptr((uint32_t)(param_6))), param_7);
    if (iVar3 != 0) goto LAB_00088eae;
    (*((uint *)camry_host_ptr((uint32_t)(puVar2 + 0x59fc)))) = param_1;
    (*((uint *)camry_host_ptr((uint32_t)(puVar2 + 0x5a00)))) = ~param_1;
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar2 + 0x597c)))) = 0x88d60u;
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0x5988)))) = 0xfff7729f;
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar2 + 0x5980)))) = 0x88caau;
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0x598c)))) = 0xfff77355;
    thunk_nvm_request_suspend_with_service_guards_7995c();
    cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x5990)))));
    if (((int8_t)cVar1) == -0x3d) {
LAB_00088e86:
      iVar3 = start_prepared_icus_tag_generation_request_88d60();
      if (iVar3 == 0) goto LAB_00088eae;
      goto LAB_00088e90;
    }
    if ((((int8_t)cVar1) == -0x2e) || (((int8_t)cVar1) == -0x4c)) goto LAB_00088eae;
  }
  else {
    if (((int8_t)cVar1) == -0x3d) {
      iVar3 = prepare_tag_generation_request_with_optional_truncation_88b84(((int *)camry_host_ptr((uint32_t)(param_2))), ((void *)camry_host_ptr((uint32_t)(param_3))), param_4, param_5, ((uint *)camry_host_ptr((uint32_t)(param_6))), param_7);
      if (iVar3 == 0) {
        (*((uint *)camry_host_ptr((uint32_t)(puVar2 + 0x59fc)))) = param_1;
        (*((uint *)camry_host_ptr((uint32_t)(puVar2 + 0x5a00)))) = ~param_1;
        (*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar2 + 0x5980)))) = 0x88caau;
        (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0x598c)))) = 0xfff77355;
        goto LAB_00088e86;
      }
LAB_00088e90:
      release_icus_request_and_notify_crypto_scheduler_87edc(0);
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x5990))))) = 0xe1;
      goto LAB_00088eae;
    }
    if ((((int8_t)cVar1) == -0x2e) || (((int8_t)cVar1) == -0x4c)) {
      iVar3 = 2;
      goto LAB_00088eae;
    }
  }
  iVar3 = 1;
LAB_00088eae:
  release_crypto_job_lock_88436();
  return iVar3;
}

void service_tag_generation_completion_and_timeouts_88ec0(void)

{
  uint uVar1;
  uint uVar2;
  char cVar3;
  uint32_t puVar4;
  int iVar5;
  
  puVar4 = 0xfebeb800u;
  if (((int8_t)DAT_febf1204) == -0x1f) {
    puVar4 = 0xfebeb800u;
    complete_tag_generation_job_copy_up_to_16bytes_88c36(DAT_febf1205);
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x5a04u + (uint32_t)((int)puVar4))))) = (code)0xd2;
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
      goto LAB_00088f70;
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
LAB_00088f70:
  deliver_or_defer_tag_generation_completion_88caa(1);
  return;
}

undefined4 check_tag_generation_completion_state_encoding_88f7a(void)

{
  undefined4 uVar1;
  
  if (((int8_t)DAT_febf1204) != -0x1f) {
    if (((int8_t)DAT_febf1204) == -0x2e) {
      uVar1 = 0;
    }
    else {
      uVar1 = 2;
    }
    return uVar1;
  }
  return 0;
}

void reset_tag_verification_job_buffers_88f92(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  memzero(((undefined *)camry_host_ptr(0xfebf1298u)),0x20);
  memzero(((undefined *)camry_host_ptr((uint32_t)(puVar1 + 0x5ab8))), 100);
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x5a8c)))) = 0xffffffff;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x5a94))))) = 0xd2;
  return;
}

undefined4
prepare_tag_verification_request_and_bit_lengths_88fc0(int *param_1,void *param_2,uint param_3,void *param_4,uint param_5,uint param_6)

{
  uint32_t puVar1;
  uint byte_count;
  undefined4 uVar2;
  
  puVar1 = 0xfebeb800u;
  if (((((camry_host_addr((param_1))== 0) || (camry_host_addr((param_2))== 0)) || (camry_host_addr((param_4))== 0)) ||
      ((param_6 == 0 || (*param_1 != 1)))) ||
     ((0x50 < param_3 || ((param_5 == 0 || (0x80 < param_5)))))) {
    uVar2 = 1;
  }
  else {
    uVar2 = 0;
    DAT_febf1318 = param_6;
    DAT_febf128c = ~param_6;
    memcpy_forward(boot_relocated_8628,param_2,param_3);
    byte_count = ~param_3 + 1 & 0xf;
    if (byte_count != 0) {
      memzero(((void *)camry_host_ptr((uint32_t)(0xfebf12b8u + param_3))), byte_count);
    }
    memcpy_forward(((undefined *)camry_host_ptr(0xfebf1308u)),param_4,param_5 + 7 >> 3);
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(0x5a9c) * 1u)))) = ((uint32_t)((uint32_t)(puVar1 + 0x5ab4)));
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(0x5a98) * 1u)))) = ((uint32_t)((uint32_t)(puVar1 + 0x5aa0)));
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar1 + 0x5aa0)))) = 0xfebf12b8u;
    (*((uint *)camry_host_ptr((uint32_t)(puVar1 + 0x5aa4)))) = param_3 << 3;
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(0x5aa8) * 1u)))) = ((uint32_t)(0xfebf1308u));
    (*((uint *)camry_host_ptr((uint32_t)(puVar1 + 0x5aac)))) = param_5 & 0x7f;
    (*((uint *)camry_host_ptr((uint32_t)(puVar1 + 0x5ab0)))) = (uint)*(byte *)(param_1 + 1);
  }
  return uVar2;
}
