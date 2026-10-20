#include "common.h"

void crypto_bank_initialize_work(void)

{
  uint uVar1;
  int iVar2;
  uint uVar3;
  uint32_t puVar4;
  puVar4 = 0xfebeb800u;
  crypto_direct_activation = '\0';
  crypto_direct_phase = '\0';
  crypto_direct_elapsed_calls = 0;
  crypto_direct_failure_count = '\0';
  crypto_direct_inhibited = '\0';
  crypto_direct_abort_request = '\0';
  crypto_collected_activation = '\0';
  crypto_collected_phase = '\0';
  crypto_collected_elapsed_calls = 0;
  crypto_bank_clear_fragment_history();
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
  crypto_bank_clear_key_material('\x01');
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6765))))) = 0;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar4 + -0x679c)))) = 0x30;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6763))))) = 1;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6764))))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar4 + -0x677a)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x675d))))) = 0;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar4 + -0x6798)))) = 0x10;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar4 + -0x6794)))) = 0x10;
  crypto_bank_clear_test_material();
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

void crypto_bank_initialize_mode(void)

{
  crypto_mode = 'Z';
  crypto_previous_mode = 'Z';
  return;
}

uint crypto_bank_profile_count(void)

{
  uint uVar1;
  
  uVar1 = (uint)crypto_config_profile_count;
  if (2 < uVar1) {
    uVar1 = 2;
  }
  return uVar1;
}

void crypto_bank_reset_configured_profiles(void)

{
  uint uVar1;
  uint uVar2;
  
  uVar1 = (uint)crypto_config_profile_count;
  if (2 < uVar1) {
    uVar1 = 2;
  }
  for (uVar2 = 0; uVar2 < uVar1; uVar2 = uVar2 + 1) {
    reset_matching_secoc_freshness_and_age_8f0a8(uVar2);
    reset_matching_secoc_age_8f0d4(uVar2);
  }
  return;
}

uint crypto_bank_run_startup_verification(void)

{
  uint8_t stack_record_21[33];
  uint uVar1;
  uint uVar2;
  uint32_t puVar3;
  int iVar4;
  undefined4 uVar5;
  uint uVar6;
  uint in_FPEC = 0;
  uint in_RBASE = 0;
  uint in_EBASE = 0;
  uint in_FPIPR = 0;
  uint in_ISPR = 0;
  
  puVar3 = 0x23dfcu;
  stack_record_21[0] = '\x01';
  uVar6 = camry_psw & 0xfffffff0 | (uint)(crypto_config_fixed_verification_enable == 'Z');
  if ((bool)((byte)uVar6 & 1)) {
    iVar4 = set_word13b0_when_status_one_89c5a(0, ((uint32_t)(0x21604u)));
    uVar6 = uVar6 & 0xfffffff0 | (uint)(iVar4 == 0);
    if ((bool)((byte)uVar6 & 1)) {
      iVar4 = set_words13b4_and13b8_89c8c(iVar4, ((uint32_t)((uint32_t)(puVar3 + -0x2818))),  0x10);
      uVar6 = uVar6 & 0xfffffff0 | (uint)(iVar4 == 0);
      if ((bool)((byte)uVar6 & 1)) {
        uVar5 = read_priority_mask_701a0();
        priority_mask_restore(0);
        if ((in_FPEC & 1) != 0) {
          in_FPIPR = in_FPIPR & 0x1f;
          if (0xf < in_FPIPR) {
            in_FPIPR = 0x10;
          }
          uVar1 = in_FPIPR;
          if (0xf < in_FPIPR) {
            uVar1 = 0xf;
          }
          uVar2 = PMR;
          if ((((uVar2 & 1 << uVar1) == 0) && ((in_ISPR & (1 << in_FPIPR + 1) - 1U & 0xffff) == 0))
             && ((uVar6 & 0x80) == 0)) {
            if (((uVar6 & 0xbfffffdf) >> 0xf & 1) == 0) {
              in_EBASE = in_RBASE;
            }
            (*(int (*)())camry_indirect((uint32_t)((in_EBASE & 0xfffffe00) + 0x70)))();
          }
        }
        __enable_irq();
        iVar4 = submit_89646_and_poll_completion13be_89c98(0, ((uint32_t)((uint32_t)(puVar3 + -0x2808))),  0x10, camry_host_addr(((int8_t *)(stack_record_21))));
        __disable_irq();
        write_priority_mask_preserving_irq_disable_701a6(uVar5);
        if (iVar4 == 0) goto LAB_000691fe;
      }
    }
    stack_record_21[0] = '\x01';
  }
LAB_000691fe:
  (*((uint32_t *)(stack_record_21 + 1))) = 1;
  stack_record_21[5] = stack_record_21[0] == '\0';
  return set_secoc_key_or_crypto_qualification_8ee16(0xff, camry_host_addr(((uint32_t *)((stack_record_21 + 1)))));
}

void crypto_bank_initialize_verification_report(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  crypto_bank_run_startup_verification();
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x67a4)))) = 0;
  return;
}

void crypto_bank_advance_profile_qualification(void)

{
  ushort uVar1;
  uint uVar2;
  uint uVar3;
  uchar uVar4;
  
  uVar3 = (uint)crypto_config_profile_count;
  if (2 < uVar3) {
    uVar3 = 2;
  }
  for (uVar2 = 0; uVar2 < uVar3; uVar2 = uVar2 + 1 & 0xff) {
    uVar4 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe507cu + (uint32_t)(uVar2) * 1u))));
    if (uVar4 == '\x11') {
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe507eu + (uint32_t)(uVar2) * 1u)))) < 3) {
        uVar1 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe5060u + (uint32_t)(uVar2) * 2u))));
        if (uVar1 < crypto_config_profile_wait_calls) {
          (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe5060u + (uint32_t)(uVar2) * 2u)))) = uVar1 + 1;
        }
        else if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe507eu + (uint32_t)(uVar2) * 1u)))) == 0) &&
                ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5080u + (uint32_t)(uVar2) * 1u)))) != '\0')) {
          uVar4 = 0x88;
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe507au + (uint32_t)(uVar2) * 1u)))) = 'Z';
        }
        else {
          uVar4 = '\"';
        }
      }
      else {
        uVar4 = 'D';
      }
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe507cu + (uint32_t)(uVar2) * 1u)))) = uVar4;
  }
  return;
}

uint crypto_bank_publish_verification_result(void)

{
  uint8_t stack_record_18[24];
  
  (*((uint32_t *)(stack_record_18 + 0))) = 1;
  stack_record_18[4] = crypto_verification_result == '\0';
  return set_secoc_key_or_crypto_qualification_8ee16(0xff, camry_host_addr(((uint32_t *)(stack_record_18))));
}

uint crypto_bank_submit_key_material(uchar slot)

{
  uint32_t puVar1;
  int iVar2;
  uint uVar3;
  
  puVar1 = 0xfebeb800u;
  if (slot < 2) {
    iVar2 = nvm_encode_service_readiness_status_79b70();
    uVar3 = nvm_get_direct_operation_result();
    if ((iVar2 != 0xf) || (uVar3 == 1)) {
      return 0x22;
    }
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x679c)))) = 0x30;
    iVar2 = start_locked_descriptor1394_operation_89a26(0, ((uint32_t)((uint32_t)(puVar1 + (uint)slot * 0x40 + -0x663a))),  0x40,  0, ((uint32_t)((uint32_t)(puVar1 + (short)(ushort)slot * 0x30 + -0x65ba))), ((uint32_t)((uint32_t)(puVar1 + -0x679c))));
    if (iVar2 == 0) {
      return 0x33;
    }
  }
  return 0x66;
}

uint crypto_bank_begin_post_update_verification(void)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  crypto_verification_result = '\x01';
  if (crypto_config_fixed_verification_enable == 'Z') {
    iVar2 = dispatch_tag_verification_service_by_id_when_idle_89646(1, ((uint32_t)(0x21604u)), ((uint32_t)(0x215e4u)), 0x10, ((uint32_t)(0x215f4u)), 0x10, 
                         (0xfebe509du));
    if (iVar2 == 0) {
      return 0x45;
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6763))))) = 1;
  }
  return 0x46;
}

void crypto_bank_advance_direct_update(void)

{
  uint32_t puVar1;
  uint uVar2;
  ushort uVar3;
  
  puVar1 = (0xfebeb800u);
  uVar2 = (uint)crypto_direct_phase;
  uVar3 = crypto_direct_elapsed_calls;
  if (crypto_direct_elapsed_calls != 0xffff) {
    uVar3 = crypto_direct_elapsed_calls + 1;
  }
  if (crypto_config_direct_timeout_calls < uVar3) {
    if (uVar2 == 0x45) {
      crypto_verification_result = '\x01';
      puVar1 = (0xfebeb800u);
      crypto_bank_publish_verification_result();
    }
    uVar2 = 0x66;
  }
  else {
    if ((uVar2 == 0x11) || (puVar1 = (0xfebeb800u), uVar2 == 0x22)) {
      puVar1 = (0xfebeb800u);
      uVar2 = crypto_bank_submit_key_material('\0');
    }
    if (uVar2 == 0x44) {
      uVar2 = crypto_bank_begin_post_update_verification();
    }
    if (uVar2 == 0x46) {
      crypto_bank_publish_verification_result();
      uVar2 = 0x55;
    }
  }
  (*((volatile undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(-0x676e) * 1u)))) = (char)uVar2;
  *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(-0x677e) * 1u)))) = uVar3;
  return;
}

uint crypto_bank_collect_key_fragments(void)

{
  int iVar1;
  uchar uVar2;
  char cVar3;
  uint32_t puVar4;
  byte bVar5;
  uint uVar6;
  uint uVar7;
  uint uVar8;
  char acStack_54 [72];
  camry_fill_bytes(acStack_54, sizeof acStack_54);
  
  puVar4 = 0xfebeb800u;
  uVar8 = 0x11;
  uVar7 = 0;
  do {
    uVar6 = 0;
    do {
      iVar1 = uVar6 + uVar7 * 8;
      uVar6 = uVar6 + 1;
      acStack_54[iVar1] = '\0';
    } while (uVar6 < 8);
    acStack_54[uVar7 + 0x40] = '\0';
    uVar7 = uVar7 + 1;
  } while (uVar7 < 8);
  uVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5338u + (uint32_t)(((volatile uint16_t *)camry_host_ptr(0x257c0u))[0]) * 1u))));
  if (uVar2 != ((volatile uint8_t *)camry_host_ptr(0xfebe5044u))[0]) {
    puVar4 = 0xfebeb800u;
    copy_tx_buffer_range_return_flag_status_7e72a(((volatile uint16_t *)camry_host_ptr(0x257dau))[0], ((volatile uint16_t *)camry_host_ptr(0x257f6u))[0], 8
                 , camry_host_addr(acStack_54));
    acStack_54[0x40] = 0x5a;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x67bc))))) = uVar2;
  cVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)((*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x257c0u + (uint32_t)(1) * 2u)))) - 0x64c8)))));
  if (cVar3 != (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x67bb)))))) {
    copy_tx_buffer_range_return_flag_status_7e72a((*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x257dau + (uint32_t)(1) * 2u)))), (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x257f6u + (uint32_t)(1) * 2u)))), 8
                 , camry_host_addr(acStack_54 + 8));
    acStack_54[0x41] = 0x5a;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x67bb))))) = cVar3;
  cVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)((*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x257c0u + (uint32_t)(2) * 2u)))) - 0x64c8)))));
  if (cVar3 != (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x67ba)))))) {
    copy_tx_buffer_range_return_flag_status_7e72a((*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x257dau + (uint32_t)(2) * 2u)))), (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x257f6u + (uint32_t)(2) * 2u)))), 8
                 , camry_host_addr(acStack_54 + 0x10));
    acStack_54[0x42] = 0x5a;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x67ba))))) = cVar3;
  cVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)((*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x257c0u + (uint32_t)(3) * 2u)))) - 0x64c8)))));
  if (cVar3 != (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x67b9)))))) {
    copy_tx_buffer_range_return_flag_status_7e72a((*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x257dau + (uint32_t)(3) * 2u)))), (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x257f6u + (uint32_t)(3) * 2u)))), 8
                 , camry_host_addr(acStack_54 + 0x18));
    acStack_54[0x43] = 0x5a;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x67b9))))) = cVar3;
  cVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)((*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x257c0u + (uint32_t)(4) * 2u)))) - 0x64c8)))));
  if (cVar3 != (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x67b8)))))) {
    copy_tx_buffer_range_return_flag_status_7e72a((*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x257dau + (uint32_t)(4) * 2u)))), (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x257f6u + (uint32_t)(4) * 2u)))), 8
                 , camry_host_addr(acStack_54 + 0x20));
    acStack_54[0x44] = 0x5a;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x67b8))))) = cVar3;
  cVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)((*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x257c0u + (uint32_t)(5) * 2u)))) - 0x64c8)))));
  if (cVar3 != (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x67b7)))))) {
    copy_tx_buffer_range_return_flag_status_7e72a((*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x257dau + (uint32_t)(5) * 2u)))), (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x257f6u + (uint32_t)(5) * 2u)))), 8
                 , camry_host_addr(acStack_54 + 0x28));
    acStack_54[0x45] = 0x5a;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x67b7))))) = cVar3;
  cVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)((*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x257c0u + (uint32_t)(6) * 2u)))) - 0x64c8)))));
  if (cVar3 != (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x67b6)))))) {
    copy_tx_buffer_range_return_flag_status_7e72a((*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x257dau + (uint32_t)(6) * 2u)))), (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x257f6u + (uint32_t)(6) * 2u)))), 8
                 , camry_host_addr(acStack_54 + 0x30));
    acStack_54[0x46] = 0x5a;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x67b6))))) = cVar3;
  cVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)((*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x257c0u + (uint32_t)(7) * 2u)))) - 0x64c8)))));
  if (cVar3 != (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x67b5)))))) {
    copy_tx_buffer_range_return_flag_status_7e72a((*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x257dau + (uint32_t)(7) * 2u)))), (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x257f6u + (uint32_t)(7) * 2u)))), 8
                 , camry_host_addr(acStack_54 + 0x38));
    acStack_54[0x47] = 0x5a;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x67b5))))) = cVar3;
  uVar7 = 0;
  do {
    bVar5 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(uVar7 - 0x67c4)))));
    if (acStack_54[uVar7 + 0x40] == 'Z') {
      if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(uVar7 - 0x67b4))))) == '\0') ||
         (((((iVar1 = uVar7 * 8, acStack_54[iVar1] == (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(iVar1 + -0x673a))))) &&
             (acStack_54[iVar1 + 1] == (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(iVar1 + -0x6739))))))) &&
            (acStack_54[iVar1 + 2] == (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(iVar1 + -0x6738))))))) &&
           ((acStack_54[iVar1 + 3] == (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(iVar1 + -0x6737))))) &&
            (acStack_54[iVar1 + 4] == (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(iVar1 + -0x6736))))))))) &&
          ((acStack_54[iVar1 + 5] == (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(iVar1 + -0x6735))))) &&
           ((acStack_54[iVar1 + 6] == (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(iVar1 + -0x6734))))) &&
            (acStack_54[iVar1 + 7] == (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(iVar1 + -0x6733))))))))))))) {
        bVar5 = bVar5 + 1;
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(uVar7 - 0x67b4))))) = 0x5a;
        if (crypto_config_fragment_repeat_threshold <= bVar5) {
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6768))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6768))))) | (byte)(1 << (uVar7 & 0x1f));
          uVar6 = 0;
          do {
            iVar1 = uVar6 + uVar7 * 8;
            uVar6 = uVar6 + 1;
            (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(iVar1 + -0x66fa))))) = acStack_54[iVar1];
          } while (uVar6 < 8);
        }
      }
      else {
        bVar5 = 1;
      }
      uVar6 = 0;
      do {
        iVar1 = uVar6 + uVar7 * 8;
        uVar6 = uVar6 + 1;
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(iVar1 + -0x673a))))) = acStack_54[iVar1];
      } while (uVar6 < 8);
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(uVar7 - 0x67c4))))) = bVar5;
    uVar7 = uVar7 + 1;
  } while (uVar7 < 8);
  if (((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6768)))))) == -1) {
    uVar7 = 0;
    do {
      uVar8 = 0;
      do {
        iVar1 = uVar8 + uVar7 * 8;
        uVar8 = uVar8 + 1;
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(iVar1 + -0x65fa))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(iVar1 + -0x66fa)))));
      } while (uVar8 < 8);
      uVar7 = uVar7 + 1;
    } while (uVar7 < 8);
    uVar8 = 0x22;
  }
  return uVar8;
}

void crypto_bank_advance_collected_update(void)

{
  uint32_t puVar1;
  uint uVar2;
  ushort uVar3;
  
  puVar1 = 0xfebeb800u;
  uVar2 = (uint)crypto_collected_phase;
  uVar3 = crypto_collected_elapsed_calls;
  if (crypto_collected_elapsed_calls != 0xffff) {
    uVar3 = crypto_collected_elapsed_calls + 1;
  }
  if (crypto_config_collected_timeout_calls < uVar3) {
    if (uVar2 == 0x45) {
      crypto_verification_result = '\x01';
      puVar1 = 0xfebeb800u;
      crypto_bank_publish_verification_result();
    }
    uVar2 = 0x66;
  }
  else {
    puVar1 = 0xfebeb800u;
    if (uVar2 == 0x11) {
      puVar1 = 0xfebeb800u;
      uVar2 = crypto_bank_collect_key_fragments();
    }
    if (uVar2 == 0x22) {
      uVar2 = crypto_bank_submit_key_material('\x01');
    }
    if (uVar2 == 0x44) {
      uVar2 = crypto_bank_begin_post_update_verification();
    }
    if (uVar2 == 0x46) {
      crypto_bank_publish_verification_result();
      uVar2 = 0x55;
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6769))))) = (char)uVar2;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x677c)))) = uVar3;
  return;
}

uint crypto_bank_collect_test_vector(void)

{
  int iVar1;
  uchar uVar2;
  char cVar3;
  byte bVar4;
  uint uVar5;
  uint32_t puVar6;
  uint uVar7;
  uint uVar8;
  undefined4 uStack_38;
  char acStack_34 [40];
  camry_fill_bytes(acStack_34, sizeof acStack_34);
  
  puVar6 = 0xfebeb800u;
  uVar8 = 0x11;
  acStack_34[1] = '\0';
  uVar5 = 0;
  acStack_34[2] = '\0';
  do {
    acStack_34[uVar5 + 0x23] = '\0';
    uVar5 = uVar5 + 1;
  } while (uVar5 < 5);
  uVar5 = 0;
  do {
    uVar7 = 0;
    do {
      iVar1 = uVar7 + uVar5 * 8;
      uVar7 = uVar7 + 1;
      acStack_34[iVar1 + 3] = '\0';
    } while (uVar7 < 8);
    uVar5 = uVar5 + 1;
  } while (uVar5 < 4);
  uVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5338u + (uint32_t)(DAT_000257d0) * 1u))));
  if (uVar2 != ((volatile uint8_t *)camry_host_ptr(0xfebe50abu))[0]) {
    uStack_38 = camry_host_addr(acStack_34 + 1);
    puVar6 = 0xfebeb800u;
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(DAT_000257ea,DAT_00025806,DAT_00025812,DAT_00025814,DAT_00025816, ((uint8_t *)acStack_34 + 1));
    uStack_38 = camry_host_addr(acStack_34 + 2);
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(DAT_000257ec,DAT_00025808,DAT_00025813,DAT_00025815,DAT_00025817, ((uint8_t *)acStack_34 + 2));
    acStack_34[0x23] = 'Z';
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6755))))) = uVar2;
  cVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(DAT_000257d2 - 0x64c8)))));
  if (cVar3 != (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6754)))))) {
    copy_tx_buffer_range_return_flag_status_7e72a(DAT_000257ee, DAT_0002580a, 8, camry_host_addr(acStack_34 + 3));
    acStack_34[0x24] = 0x5a;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6754))))) = cVar3;
  cVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(DAT_000257d4 - 0x64c8)))));
  if (cVar3 != (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6753)))))) {
    copy_tx_buffer_range_return_flag_status_7e72a(DAT_000257f0, DAT_0002580c, 8, camry_host_addr(acStack_34 + 0xb));
    acStack_34[0x25] = 0x5a;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6753))))) = cVar3;
  cVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(DAT_000257d6 - 0x64c8)))));
  if (cVar3 != (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6752)))))) {
    copy_tx_buffer_range_return_flag_status_7e72a(DAT_000257f2, DAT_0002580e, 8, camry_host_addr(acStack_34 + 0x13));
    acStack_34[0x26] = 0x5a;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6752))))) = cVar3;
  cVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(DAT_000257d8 - 0x64c8)))));
  if (cVar3 != (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6751)))))) {
    copy_tx_buffer_range_return_flag_status_7e72a(DAT_000257f4, DAT_00025810, 8, camry_host_addr(acStack_34 + 0x1b));
    acStack_34[0x27] = 0x5a;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6751))))) = cVar3;
  bVar4 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x675a)))));
  if (acStack_34[0x23] == 'Z') {
    if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6750))))) == '\0') ||
       ((acStack_34[1] == (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6762))))) && (acStack_34[2] == (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x675f))))))))) {
      bVar4 = bVar4 + 1;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6750))))) = 0x5a;
      if (crypto_config_fragment_repeat_threshold <= bVar4) {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x675e))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x675e))))) | 1;
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6761))))) = acStack_34[1];
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6760))))) = acStack_34[2];
      }
    }
    else {
      bVar4 = 1;
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6762))))) = acStack_34[1];
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x675f))))) = acStack_34[2];
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x675a))))) = bVar4;
  uVar5 = 1;
  do {
    bVar4 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(uVar5 - 0x675a)))));
    if (acStack_34[uVar5 + 0x23] == 'Z') {
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(uVar5 - 0x6750))))) == '\0') {
LAB_00069afa:
        bVar4 = bVar4 + 1;
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(uVar5 - 0x6750))))) = 'Z';
        if (crypto_config_fragment_repeat_threshold <= bVar4) {
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x675e))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x675e))))) | (byte)(1 << (uVar5 & 0x1f));
          uVar7 = 0;
          do {
            iVar1 = uVar7 + uVar5 * 8;
            uVar7 = uVar7 + 1;
            (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(iVar1 + -0x66a2))))) = acStack_34[iVar1 + -5];
          } while (uVar7 < 8);
        }
      }
      else {
        iVar1 = uVar5 * 8;
        if (((((acStack_34[iVar1 + -5] == (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(iVar1 + -0x66c2)))))) &&
              (acStack_34[iVar1 + -4] == (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(iVar1 + -0x66c1))))))) &&
             (acStack_34[iVar1 + -3] == (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(iVar1 + -0x66c0))))))) &&
            ((acStack_34[iVar1 + -2] == (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(iVar1 + -0x66bf))))) &&
             (acStack_34[iVar1 + -1] == (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(iVar1 + -0x66be))))))))) &&
           ((acStack_34[iVar1] == (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(iVar1 + -0x66bd))))) &&
            ((acStack_34[iVar1 + 1] == (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(iVar1 + -0x66bc))))) &&
             (acStack_34[iVar1 + 2] == (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(iVar1 + -0x66bb))))))))))) goto LAB_00069afa;
        bVar4 = 1;
      }
      uVar7 = 0;
      do {
        iVar1 = uVar7 + uVar5 * 8;
        uVar7 = uVar7 + 1;
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(iVar1 + -0x66c2))))) = acStack_34[iVar1 + -5];
      } while (uVar7 < 8);
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(uVar5 - 0x675a))))) = bVar4;
    uVar5 = uVar5 + 1;
    if (4 < uVar5) {
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x675e))))) == '\x1f') {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x675c))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6761)))));
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x675b))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6760)))));
        uVar5 = 0;
        do {
          uVar8 = 0;
          do {
            iVar1 = uVar8 + uVar5 * 8;
            uVar8 = uVar8 + 1;
            (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(iVar1 + -0x667a))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(iVar1 + -0x669a)))));
          } while (uVar8 < 8);
          uVar5 = uVar5 + 1;
        } while (uVar5 < 2);
        uVar5 = 0;
        do {
          uVar8 = 0;
          do {
            iVar1 = uVar8 + uVar5 * 8;
            uVar8 = uVar8 + 1;
            (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(iVar1 + -0x666a))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(iVar1 + -0x668a)))));
          } while (uVar8 < 8);
          uVar5 = uVar5 + 1;
        } while (uVar5 < 2);
        uVar8 = 0x22;
      }
      return uVar8;
    }
  } while( true );
}

uint crypto_bank_submit_test_vector(void)

{
  uint8_t stack_record_18[24];
  int iVar1;
  
  (*((uint32_t *)(stack_record_18 + 0))) = (uint)crypto_test_mode;
  if ((*((uint32_t *)(stack_record_18 + 0))) == 0) {
    (*((uint32_t *)(stack_record_18 + 0))) = 1;
    crypto_aes_result_capacity = 0x10;
    stack_record_18[4] = crypto_test_selector;
    iVar1 = dispatch_single_block_crypto_service_by_id_when_idle_89838(0, camry_host_addr(((uint32_t *)(stack_record_18))), camry_host_addr(crypto_test_input), 0x10, camry_host_addr(crypto_aes_result), 
                         (0xfebe5068u));
  }
  else {
    if ((*((uint32_t *)(stack_record_18 + 0))) != 1) {
      return 0x44;
    }
    crypto_mac_result_capacity = 0x10;
    stack_record_18[4] = crypto_test_selector;
    iVar1 = dispatch_tag_generation_service_by_id_when_idle_89440(1, camry_host_addr(((uint32_t *)(stack_record_18))), camry_host_addr(crypto_test_input), 0x10, camry_host_addr(crypto_mac_result), 
                         (0xfebe506cu), 1);
  }
  if (iVar1 != 0) {
    return 0x44;
  }
  return 0x23;
}

void crypto_bank_advance_test_operation(void)

{
  uint32_t puVar1;
  uint uVar2;
  ushort uVar3;
  
  puVar1 = 0xfebeb800u;
  uVar2 = (uint)crypto_test_phase;
  uVar3 = crypto_test_elapsed_calls;
  if (crypto_test_elapsed_calls != 0xffff) {
    uVar3 = crypto_test_elapsed_calls + 1;
  }
  if (crypto_config_test_timeout_calls < uVar3) {
    uVar2 = 0x44;
  }
  else {
    puVar1 = 0xfebeb800u;
    if (uVar2 == 0x11) {
      puVar1 = 0xfebeb800u;
      uVar2 = crypto_bank_collect_test_vector();
    }
    if (uVar2 == 0x22) {
      uVar2 = crypto_bank_submit_test_vector();
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6764))))) = (char)uVar2;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x677a)))) = uVar3;
  return;
}

void crypto_bank_foreground_cycle(void)

{
  uint uVar1;
  uchar uVar2;
  uint uVar3;
  uint32_t puVar4;
  uVar2 = crypto_mode;
  puVar4 = 0xfebeb800u;
  if (crypto_mode == 0xa5) {
    puVar4 = 0xfebeb800u;
    crypto_bank_initialize_work();
  }
  else if (crypto_previous_mode == 0xa5) {
    puVar4 = 0xfebeb800u;
    crypto_bank_reset_configured_profiles();
  }
  crypto_bank_advance_profile_qualification();
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
    crypto_bank_advance_direct_update();
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x676a))))) == '\x01') {
    crypto_bank_advance_collected_update();
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6765))))) == '\x01') {
    crypto_bank_advance_test_operation();
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6766))))) = uVar2;
  return;
}

void crypto_bank_retire_direct_update(void)

{
  if (crypto_direct_phase == 'U') {
    crypto_direct_activation = '\x02';
  }
  if (((crypto_direct_phase == 'f') &&
      (crypto_direct_activation = 0xff, crypto_direct_failure_count != 0xff)) &&
     (crypto_direct_failure_count = crypto_direct_failure_count + 1,
     crypto_config_direct_failure_limit <= crypto_direct_failure_count)) {
    crypto_direct_inhibited = 'Z';
  }
  return;
}

void crypto_bank_retire_collected_update(void)

{
  uint uVar1;
  uchar uVar2;
  uint uVar3;
  uint32_t puVar4;
  uchar uVar5;
  
  uVar2 = crypto_collected_phase;
  puVar4 = 0xfebeb800u;
  uVar5 = crypto_collected_activation;
  if (crypto_collected_phase == 'U') {
    uVar5 = '\x02';
    puVar4 = 0xfebeb800u;
    crypto_bank_clear_fragment_history();
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
    crypto_bank_clear_fragment_history();
                    /* WARNING: Could not inline here */
    crypto_bank_clear_key_material('\x01');
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x676a))))) = uVar5;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6769))))) = uVar2;
  return;
}

void crypto_bank_retire_test_operation(void)

{
  if (crypto_test_phase == '3') {
    crypto_test_failed = '\0';
    crypto_test_activation = '\x02';
  }
  if (crypto_test_phase == 'D') {
    crypto_test_activation = 0xff;
    crypto_test_failed = 'Z';
  }
  return;
}

void crypto_bank_publish_observation_window(void)

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

void crypto_bank_maintain_terminal_states(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (crypto_direct_activation == '\x01') {
    puVar1 = 0xfebeb800u;
    crypto_bank_retire_direct_update();
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x676a))))) == '\x01') {
    crypto_bank_retire_collected_update();
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6765))))) == '\x01') {
    crypto_bank_retire_test_operation();
  }
  crypto_bank_publish_observation_window();
  return;
}

uint crypto_bank_stage_direct_request
               (uchar *input,ushort input_length,uchar *output,ushort output_length)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  
  uVar3 = (uint)input_length;
  uVar4 = (uint)output_length;
  if (0x31 < uVar4) {
    uVar4 = 0x31;
  }
  if (0x40 < uVar3) {
    uVar3 = 0x40;
  }
  if (crypto_direct_inhibited == '\0') {
    if (crypto_direct_activation == '\x01') {
      uVar2 = 8;
    }
    else {
      crypto_direct_activation = '\x01';
      crypto_direct_elapsed_calls = 0;
      crypto_direct_phase = '\"';
      uVar2 = 0;
      do {
        uVar1 = uVar2 + 1;
        crypto_key_request[0][uVar2] = '\0';
        uVar2 = uVar1;
      } while (uVar1 < 0x40);
      uVar2 = 0;
      do {
        uVar1 = uVar2 + 1;
        crypto_key_result[0][uVar2] = '\0';
        uVar2 = uVar1;
      } while (uVar1 < 0x30);
      uVar2 = 0;
    }
  }
  else {
    uVar2 = 5;
  }
  for (uVar1 = 0; uVar1 < uVar3; uVar1 = uVar1 + 1 & 0xffff) {
    crypto_key_request[0][uVar1] = input[uVar1];
  }
  if (uVar4 != 0) {
    *output = crypto_direct_activation;
    for (uVar3 = 1; uVar3 < uVar4; uVar3 = uVar3 + 1 & 0xffff) {
      output[uVar3] = '\0';
    }
  }
  return uVar2;
}

uint crypto_bank_read_direct_result(uchar *output,ushort length)

{
  uchar uVar1;
  uint uVar2;
  uint uVar3;
  
  uVar1 = crypto_direct_activation;
  uVar3 = (uint)length;
  if (uVar3 < 0x32) {
    if (uVar3 == 0) goto LAB_00069f8c;
  }
  else {
    uVar3 = 0x31;
  }
  *output = crypto_direct_activation;
  uVar2 = 1;
  if (uVar1 == '\x02') {
    for (; uVar2 < uVar3; uVar2 = uVar2 + 1 & 0xffff) {
      output[uVar2] = crypto_key_request[1][uVar2 + 0x3f];
    }
  }
  else {
    for (; uVar2 < uVar3; uVar2 = uVar2 + 1 & 0xffff) {
      output[uVar2] = '\0';
    }
  }
LAB_00069f8c:
  if ((uVar1 == '\x02') || (uVar1 == 0xff)) {
    uVar3 = 0;
    do {
      uVar2 = uVar3 + 1;
      crypto_key_request[0][uVar3] = '\0';
      uVar3 = uVar2;
    } while (uVar2 < 0x40);
    uVar3 = 0;
    do {
      uVar2 = uVar3 + 1;
      crypto_key_result[0][uVar3] = '\0';
      uVar3 = uVar2;
    } while (uVar2 < 0x30);
  }
  return 0;
}

void crypto_bank_snapshot_key_generations(void)

{
  ((volatile uint8_t *)camry_host_ptr(0xfebe5044u))[0] =
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5338u + (uint32_t)(((volatile uint16_t *)camry_host_ptr(0x257c0u))[0]) * 1u))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5044u + (uint32_t)(1) * 1u)))) =
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5338u + (uint32_t)((*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x257c0u + (uint32_t)(1) * 2u))))) * 1u))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5044u + (uint32_t)(2) * 1u)))) =
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5338u + (uint32_t)((*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x257c0u + (uint32_t)(2) * 2u))))) * 1u))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5044u + (uint32_t)(3) * 1u)))) =
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5338u + (uint32_t)((*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x257c0u + (uint32_t)(3) * 2u))))) * 1u))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5044u + (uint32_t)(4) * 1u)))) =
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5338u + (uint32_t)((*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x257c0u + (uint32_t)(4) * 2u))))) * 1u))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5044u + (uint32_t)(5) * 1u)))) =
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5338u + (uint32_t)((*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x257c0u + (uint32_t)(5) * 2u))))) * 1u))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5044u + (uint32_t)(6) * 1u)))) =
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5338u + (uint32_t)((*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x257c0u + (uint32_t)(6) * 2u))))) * 1u))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5044u + (uint32_t)(7) * 1u)))) =
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5338u + (uint32_t)((*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x257c0u + (uint32_t)(7) * 2u))))) * 1u))));
  return;
}
