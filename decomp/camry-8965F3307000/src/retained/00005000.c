#include "common.h"

undefined1 reject_unless_suppressed_tester_present_5060(char *param_1,char param_2,char param_3)

{
  undefined1 uVar1;
  
  uVar1 = 1;
  if (((param_3 == '\0') && (param_2 == '\x02')) && (*param_1 == '>')) {
    if (((int8_t)param_1[1]) == -0x80) {
      uVar1 = 0;
    }
    else {
      uVar1 = 1;
    }
  }
  return uVar1;
}

void return_only_stub_5084(void)

{
  return;
}

void boot_initialize_default_session_and_service_state_5086(void)

{
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff930eu)))) = '\x01';
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff930fu)))) = '\x01';
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9313u)))) = '\0';
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9310u)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9311u)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9312u)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9314u)))) = 2;
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9315u)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9316u)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9317u)))) = '\0';
  clear_session_transition_bytes_6300();
  return_only_stub_6134();
  boot_security_initialize_handshake();
  return_only_stub_68fa();
  return_only_stub_699a();
  return_only_stub_5084();
  return_only_stub_6082();
  clear_write_data_status_bytes_4a90();
  clear_routine_state_and_completion_mask_5c4a();
  return_only_stub_5f3c();
  fill_constant_block_4f9e();
  return_only_stub_5d2a();
  return;
}

void boot_initialize_programming_session_service_state_50ea(void)

{
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff930eu)))) = '\x02';
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9313u)))) = '\0';
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9310u)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9311u)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9312u)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9314u)))) = 2;
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9315u)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9316u)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9317u)))) = '\0';
  clear_session_transition_bytes_6300();
  return_only_stub_6134();
  boot_security_initialize_handshake();
  return_only_stub_68fa();
  return_only_stub_699a();
  return_only_stub_5084();
  return_only_stub_6082();
  clear_write_data_status_bytes_4a90();
  clear_routine_state_and_completion_mask_5c4a();
  return_only_stub_5f3c();
  fill_constant_block_4f9e();
  return_only_stub_5d2a();
  return;
}

uint32_t boot_publish_session_three_and_cancel_security_delay_5148(void)

{
  uint32_t camry_r10_result;
  (camry_r10_result = boot_flag_transition_and_publish_session_three_630c());
  boot_security_cancel_delay();
  return camry_r10_result;
}

void set_boot_flag_2b10_5158(void)

{
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9310u)))) = 1;
  return;
}

void update_authentication_enable_from_presence_bytes_5160(void)

{
  char cVar1;
  bool bVar2;
  uint32_t puVar3;
  int local_c;
  
  cVar1 = DAT_0000bff8;
  puVar3 = (camry_gp + 0x0u);
  copy_gp_words_to_destination_u8_count_1514(camry_host_addr(&local_c), 1);
  if ((local_c == 0xff) || (((int8_t)DAT_000ffdb0) == -1)) {
    bVar2 = cVar1 != -1;
  }
  else {
    bVar2 = true;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6ceb))))) = bVar2;
  return;
}

void refresh_authentication_enable_and_clear_verified_mask_519c(void)

{
  uint32_t puVar1;
  puVar1 = (camry_gp + 0x0u);
  update_authentication_enable_from_presence_bytes_5160();
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6cef))))) = 0;
  return;
}

void boot_diagnostic_timer_progress(void)

{
  boot_session_progress();
  boot_security_delay_progress();
  boot_write_did_progress();
  boot_routine_timer_progress();
  boot_transfer_timer_progress();
  return;
}

void boot_join_session_and_consume_transfer_foreground_51c8(void)

{
  boot_session_foreground_join();
  boot_transfer_foreground_consume();
  return;
}

uint32_t boot_session_publish(uchar session)

{
  uint32_t camry_r10_result;
  uint32_t puVar1;
  undefined4 uVar2;
  
  puVar1 = (camry_gp + 0x0u);
  uVar2 = (camry_r10_result = raise_pmr_and_return_previous_mask_721e(0xffff));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6cf2))))) = session;
  boot_security_invalidate_handshake();
  restore_pmr_preserving_interrupt_disable_state_7244(uVar2);
  return camry_r10_result;
}

void boot_negative_response(uchar sid,uchar nrc)

{
  camry_write32((camry_sp - 4u) & ~3u, camry_gpr[31]);
  camry_sp -= 4u;
  camry_gpr[3] = camry_sp;

  uchar mode;
  
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff92d0u)))) = 0x7f;
  if ((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff98bfu)))) == '\0') {
    mode = '\0';
  }
  else {
    mode = '\x02';
  }
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff92d1u)))) = sid;
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff92d2u)))) = nrc;
  (camry_gpr[6] = mode, camry_r7 = camry_gpr[7] = camry_gp - 0x6d30u, camry_gpr[8] = 3u, camry_gpr[31] = 0x521eu, boot_response_submit)(mode,((undefined *)camry_host_ptr((camry_gp + 0xffff92d0u))),3);
  { if (!camry_halted) { camry_gpr[31] = camry_read32((camry_sp + 0u) & ~3u); camry_sp += 4u; camry_gpr[3] = camry_sp; } return; }
}

void boot_dispatch_diagnostic_service(uchar sid,ushort request_length)

{
  camry_write32((camry_sp - 4u) & ~3u, camry_gpr[29]);
  camry_write32((camry_sp - 8u) & ~3u, camry_gpr[31]);
  camry_sp -= 8u;
  camry_gpr[3] = camry_sp;

  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = 0;
  do {
    if (sid == (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x7b8u) + (uint32_t)(iVar3) * (uint32_t)sizeof(F33BootServiceEntry) + (uint32_t)offsetof(F33BootServiceEntry, sid)))))) {
      if (((uint)(*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x7b8u) + (uint32_t)(iVar3) * (uint32_t)sizeof(F33BootServiceEntry) + (uint32_t)offsetof(F33BootServiceEntry, address_mode_mask))))) &
          1 << ((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff98bfu)))) & 0x1f)) != 0) {
        (*(int (*)())camry_indirect((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)((camry_tp + 0x7b8u) + (uint32_t)(iVar3) * (uint32_t)sizeof(F33BootServiceEntry) + (uint32_t)offsetof(F33BootServiceEntry, handler))))))))(request_length, (uint)(ushort)request_length);
        { if (!camry_halted) { camry_gpr[29] = camry_read32((camry_sp + 4u) & ~3u); camry_gpr[31] = camry_read32((camry_sp + 0u) & ~3u); camry_sp += 8u; camry_gpr[3] = camry_sp; } return; }
      }
      break;
    }
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -0x13;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  (camry_gpr[6] = sid, camry_r7 = camry_gpr[7] = 0x11u, camry_gpr[31] = 0x5266u, boot_negative_response)(sid,'\x11');
  { if (!camry_halted) { camry_gpr[29] = camry_read32((camry_sp + 4u) & ~3u); camry_gpr[31] = camry_read32((camry_sp + 0u) & ~3u); camry_sp += 8u; camry_gpr[3] = camry_sp; } return; }
}

bool is_suppressed_tester_present_526a(undefined4 param_1,undefined1 param_2,undefined1 param_3)

{
  int iVar1;
  
  iVar1 = reject_unless_suppressed_tester_present_5060(((char *)camry_host_ptr((uint32_t)(param_1))), param_2, param_3);
  return iVar1 == 0;
}

void return_only_stub_5280(void)

{
  return;
}

void return_only_stub_5282(void)

{
  return;
}

void return_only_stub_5284(void)

{
  return;
}

uint32_t boot_program_completion_marker_word_5286(uint param_1)

{
  uint32_t camry_r10_result;
  uchar local_8 [4];
  camry_fill_bytes(local_8, sizeof local_8);
  
  local_8[0] = 'Z';
  local_8[1] = 0xa5;
  local_8[2] = 0xa5;
  local_8[3] = 'Z';
  (camry_r10_result = boot_submit_program_stream(param_1,4));
  boot_append_program_input(local_8,4);
  return camry_r10_result;
}

int read_variable_width_big_endian_u32_52a6(byte *param_1,uint param_2)

{
  byte bVar1;
  int iVar2;
  
  iVar2 = 0;
  for (param_2 = param_2 & 0xff; param_2 != 0; param_2 = param_2 - 1) {
    bVar1 = *param_1;
    param_1 = param_1 + 1;
    iVar2 = iVar2 * 0x100 + (uint)bVar1;
  }
  return iVar2;
}

bool is_boot_flag_2b12_not_one_52be(void)

{
  return (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9312u)))) != '\x01';
}

void boot_security_access_negative_response_52ca(uchar param_1)

{
  camry_write32((camry_sp - 4u) & ~3u, camry_gpr[31]);
  camry_sp -= 4u;
  camry_gpr[3] = camry_sp;

  (camry_r7 = camry_gpr[7] = param_1, camry_gpr[6] = 0x27u, camry_gpr[31] = 0x52dau, boot_negative_response)('\'',param_1);
  { if (!camry_halted) { camry_gpr[31] = camry_read32((camry_sp + 0u) & ~3u); camry_sp += 4u; camry_gpr[3] = camry_sp; } return; }
}

void boot_security_access_positive_challenge_response_52de(void)

{
  camry_write32((camry_sp - 4u) & ~3u, camry_gpr[31]);
  camry_sp -= 4u;
  camry_gpr[3] = camry_sp;

  int iVar1;
  int iVar2;
  uchar uVar3;
  int iVar4;
  ushort length;
  
  uVar3 = (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9354u))));
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff92d0u)))) = 0x67;
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff92d1u)))) = (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9354u))));
  if (((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9354u)))) & 1) == 0) {
    length = 2;
  }
  else {
    length = 0x12;
    iVar4 = 0;
    do {
      iVar2 = iVar4 + 1;
      iVar1 = iVar4 + -0xf;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff92d2u) + (uint32_t)(iVar4) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff9344u) + (uint32_t)(iVar4) * 1u))));
      iVar4 = iVar2;
    } while (((iVar1 < 0) || (iVar2 < 0)));
  }
  (camry_gpr[6] = (uVar3 >> 7) ^ 1u, camry_r7 = camry_gpr[7] = camry_gp - 0x6d30u, camry_gpr[8] = length, camry_gpr[31] = 0x5324u, boot_response_submit)(uVar3 >> 7 ^ 1,((undefined *)camry_host_ptr((camry_gp + 0xffff92d0u))),length);
  { if (!camry_halted) { camry_gpr[31] = camry_read32((camry_sp + 0u) & ~3u); camry_sp += 4u; camry_gpr[3] = camry_sp; } return; }
}

void boot_security_seed_request(ushort request_length)

{
  camry_write32((camry_sp - 4u) & ~3u, camry_gpr[29]);
  camry_write32((camry_sp - 8u) & ~3u, camry_gpr[31]);
  camry_sp -= 8u;
  camry_gpr[3] = camry_sp;

  int iVar1;
  int iVar2;
  int iVar3;
  undefined *puVar4;
  undefined4 uVar6;
  uchar uVar7;
  uint32_t puVar5;
  uVar7 = (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9355u))));
  puVar5 = (camry_gp + 0x0u);
  puVar4 = ((undefined *)camry_host_ptr((camry_gp + 0x0u)));
  if ((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9356u)))) == '\x01') {
    uVar6 = 0x37;
  }
  else {
    if (request_length == 0x12) {
      iVar3 = 0;
      if ((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9355u)))) == '\0') {
LAB_0000535e:
        uVar7 = '\x01';
      }
      else {
        if ((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9355u)))) == '\x01') {
          do {
            iVar2 = iVar3 + 1;
            iVar1 = iVar3 + -0xf;
            (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff9334u) + (uint32_t)(iVar3) * 1u)))) = (*((uchar *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((camry_gp + 0xffff9318u)))) + iVar3 + 2))));
            iVar3 = iVar2;
          } while (((iVar1 < 0) || (iVar2 < 0)));
          (camry_gpr[6] = camry_gp - 0x6cdcu, camry_gpr[31] = 0x5384u, boot_security_generate_challenge)(((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9324u))));
          iVar3 = 0;
          do {
            iVar2 = iVar3 + 1;
            iVar1 = iVar3 + -0xf;
            (*((volatile uint8_t *)camry_host_ptr((uint32_t)((puVar5 + iVar3 + -0x6cdc) + (uint32_t)(0x20))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(iVar3 + -0x6cdc)))));
            iVar3 = iVar2;
          } while (((iVar1 < 0) || (iVar2 < 0)));
          uVar7 = '\x02';
          puVar4 = ((undefined *)camry_host_ptr((uint32_t)(puVar5)));
        }
        else if ((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9355u)))) < 3) {
          do {
            iVar2 = iVar3 + 1;
            iVar1 = iVar3 + -0xf;
            (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff9334u) + (uint32_t)(iVar3) * 1u)))) = (*((uchar *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((camry_gp + 0xffff9318u)))) + iVar3 + 2))));
            iVar3 = iVar2;
          } while (((iVar1 < 0) || (iVar2 < 0)));
          iVar3 = 0;
          do {
            iVar2 = iVar3 + 1;
            iVar1 = iVar3 + -0xf;
            (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff9344u) + (uint32_t)(iVar3) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff9324u) + (uint32_t)(iVar3) * 1u))));
            iVar3 = iVar2;
            puVar4 = ((undefined *)camry_host_ptr((camry_gp + 0x0u)));
          } while (((iVar1 < 0) || (iVar2 < 0)));
        }
        else {
          if ((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9355u)))) != '\x03') goto LAB_0000535e;
          do {
            (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff9344u) + (uint32_t)(iVar3) * 1u)))) = '\0';
            iVar2 = iVar3 + 1;
            iVar1 = iVar3 + -0xf;
            iVar3 = iVar2;
            puVar4 = ((undefined *)camry_host_ptr((camry_gp + 0x0u)));
          } while (((iVar1 < 0) || (iVar2 < 0)));
        }
        puVar4[-0x6cac] = (*((undefined1 *)camry_host_ptr((uint32_t)(*(int *)(puVar4 + -0x6ce8) + 1))));
        (camry_gpr[29] = uVar7, camry_gpr[31] = 0x53eau, boot_security_access_positive_challenge_response_52de)();
      }
      goto LAB_000053ea;
    }
    uVar6 = 0x13;
  }
  puVar4 = ((undefined *)camry_host_ptr((camry_gp + 0x0u)));
  (camry_gpr[29] = uVar7, camry_gpr[6] = uVar6, camry_gpr[31] = 0x534eu, boot_security_access_negative_response_52ca)(uVar6);
LAB_000053ea:
  puVar4[-0x6cab] = uVar7;
  { if (!camry_halted) { camry_gpr[29] = camry_read32((camry_sp + 4u) & ~3u); camry_gpr[31] = camry_read32((camry_sp + 0u) & ~3u); camry_sp += 8u; camry_gpr[3] = camry_sp; } return; }
}

void boot_security_key_request(ushort request_length)

{
  camry_write32((camry_sp - 4u) & ~3u, camry_gpr[29]);
  camry_write32((camry_sp - 8u) & ~3u, camry_gpr[31]);
  camry_sp -= 24u;
  camry_gpr[3] = camry_sp;

  int iVar1;
  int iVar2;
  int iVar3;
  undefined *puVar4;
  undefined *puVar5;
  undefined4 uVar6;
  int iVar7;
  uchar uVar8;
  uchar *local_18 = (uchar *)camry_host_ptr(camry_sp);
  
  puVar5 = ((undefined *)camry_host_ptr((camry_gp + 0x0u)));
  puVar4 = ((undefined *)camry_host_ptr((camry_gp + 0x0u)));
  if ((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9355u)))) == '\0') {
LAB_0000550c:
    uVar8 = '\x01';
  }
  else {
    if ((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9355u)))) == '\x01') {
LAB_00005506:
      uVar6 = 0x24;
      uVar8 = (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9355u))));
      puVar4 = ((undefined *)camry_host_ptr((camry_gp + 0x0u)));
    }
    else {
      if (3 < (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9355u))))) goto LAB_0000550c;
      if (2 < (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9355u))))) goto LAB_00005506;
      if (request_length == 0x12) {
        puVar4 = ((undefined *)camry_host_ptr((camry_gp + 0x0u)));
        (camry_gpr[6] = camry_gp - 0x6cccu, camry_r7 = camry_gpr[7] = camry_gp - 0x6cdcu, camry_gpr[8] = camry_sp, camry_gpr[31] = 0x546cu, boot_security_derive_expected_key)
                  (boot_security_client_material,((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9324u))),local_18);
        iVar3 = 0;
LAB_0000546e:
        iVar7 = *(int *)(puVar4 + -0x6ce8);
        if (local_18[iVar3] == (*((uchar *)camry_host_ptr((uint32_t)(iVar3 + iVar7 + 2))))) goto code_r0x00005484;
        if (-1 < (int)((byte)puVar4[-0x6ca9] - 1)) {
          puVar5 = puVar4;
          uVar6 = read_ffe51010_word_1d24();
          *(undefined4 *)(puVar5 + -0x6ce4) = 200000000;
          puVar5[-0x6caa] = 1;
          *(undefined4 *)(puVar5 + -0x6ce0) = uVar6;
          puVar5[-0x6ca9] = 0;
          iVar3 = 0;
          do {
            puVar5[iVar3 + -0x6cdc] = 0;
            iVar1 = iVar3 + 1;
            iVar7 = iVar3 + -0xf;
            iVar3 = iVar1;
          } while (((iVar7 < 0) || (iVar1 < 0)));
          goto LAB_000054c6;
        }
        puVar4[-0x6ca9] = puVar4[-0x6ca9] + 1;
        uVar6 = 0x35;
        uVar8 = '\x01';
        goto LAB_00005428;
      }
      if ((int)((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9357u)))) - 1) < 0) {
        uVar6 = 0x13;
        uVar8 = '\x01';
        puVar4 = ((undefined *)camry_host_ptr((camry_gp + 0x0u)));
        (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9357u)))) = (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9357u)))) + '\x01';
      }
      else {
        uVar6 = read_ffe51010_word_1d24();
        *(undefined4 *)(puVar5 + -0x6ce4) = 200000000;
        puVar5[-0x6caa] = 1;
        *(undefined4 *)(puVar5 + -0x6ce0) = uVar6;
        puVar5[-0x6ca9] = 0;
        iVar3 = 0;
        do {
          puVar5[iVar3 + -0x6cdc] = 0;
          iVar1 = iVar3 + 1;
          iVar7 = iVar3 + -0xf;
          iVar3 = iVar1;
        } while (((iVar7 < 0) || (iVar1 < 0)));
LAB_000054c6:
        uVar6 = 0x36;
        uVar8 = '\x01';
        puVar4 = puVar5;
      }
    }
LAB_00005428:
    (camry_gpr[29] = uVar8, camry_gpr[6] = uVar6, camry_gpr[31] = 0x542cu, boot_security_access_negative_response_52ca)(uVar6);
  }
LAB_0000550e:
  puVar4[-0x6cab] = uVar8;
  { if (!camry_halted) { camry_gpr[29] = camry_read32((camry_sp + 20u) & ~3u); camry_gpr[31] = camry_read32((camry_sp + 16u) & ~3u); camry_sp += 24u; camry_gpr[3] = camry_sp; } return; }
code_r0x00005484:
  iVar2 = iVar3 + 1;
  iVar1 = iVar3 + -0xf;
  iVar3 = iVar2;
  if (iVar1 < 0 == (iVar2 < 0 && -1 < iVar1)) goto LAB_000054da;
  goto LAB_0000546e;
LAB_000054da:
  puVar4[-0x6cf1] = 2;
  puVar4[-0x6ca9] = 0;
  iVar3 = 0;
  do {
    puVar4[iVar3 + -0x6cdc] = 0;
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -0xf;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  uVar8 = '\x03';
  puVar4[-0x6cac] = (*((undefined1 *)camry_host_ptr((uint32_t)(iVar7 + 1))));
  (camry_gpr[29] = uVar8, camry_gpr[31] = 0x5504u, boot_security_access_positive_challenge_response_52de)();
  goto LAB_0000550e;
}

void boot_service_security_access(ushort request_length)

{
  camry_write32((camry_sp - 4u) & ~3u, camry_gpr[29]);
  camry_write32((camry_sp - 8u) & ~3u, camry_gpr[31]);
  camry_sp -= 8u;
  camry_gpr[3] = camry_sp;

  char cVar1;
  byte bVar2;
  uint32_t puVar3;
  F33BootInterruptEntry *pFVar4;
  undefined4 uVar5;
  int iVar6;
  byte bVar7;
  
  puVar3 = (camry_gp + 0x0u);
  pFVar4 = ((volatile F33BootInterruptEntry *)camry_host_ptr((camry_tp + 0x0u)));
  iVar6 = camry_host_addr((camry_gpr[29] = request_length, camry_gpr[31] = 0x5522u, boot_get_request_buffer_and_clear_append_index_67d0)());
  cVar1 = (*((char *)((uint8_t *)&pFVar4[0x10b].eiic + (1))));
  (*((int *)camry_host_ptr((uint32_t)(puVar3 + -0x6ce8)))) = iVar6;
  bVar2 = (*((byte *)camry_host_ptr((uint32_t)(iVar6 + 1)))) & 0x7f;
  if ((bVar2 == 1) || (bVar7 = 3, bVar2 == 2)) {
    bVar7 = bVar2;
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6cf2))))) == cVar1) {
    if (request_length < 2) {
      uVar5 = 0x13;
    }
    else {
      if (bVar7 != 3) {
        if (bVar7 == 1) {
          (camry_gpr[6] = request_length, camry_gpr[31] = 0x556au, boot_security_seed_request)(request_length);
          { if (!camry_halted) { camry_gpr[29] = camry_read32((camry_sp + 4u) & ~3u); camry_gpr[31] = camry_read32((camry_sp + 0u) & ~3u); camry_sp += 8u; camry_gpr[3] = camry_sp; } return; }
        }
        if (bVar7 == 2) {
          (camry_gpr[6] = request_length, camry_gpr[31] = 0x5576u, boot_security_key_request)(request_length);
          { if (!camry_halted) { camry_gpr[29] = camry_read32((camry_sp + 4u) & ~3u); camry_gpr[31] = camry_read32((camry_sp + 0u) & ~3u); camry_sp += 8u; camry_gpr[3] = camry_sp; } return; }
        }
      }
      uVar5 = 0x12;
    }
  }
  else {
    uVar5 = 0x7f;
  }
  (camry_gpr[6] = uVar5, camry_gpr[31] = 0x5580u, boot_security_access_negative_response_52ca)(uVar5);
  { if (!camry_halted) { camry_gpr[29] = camry_read32((camry_sp + 4u) & ~3u); camry_gpr[31] = camry_read32((camry_sp + 0u) & ~3u); camry_sp += 8u; camry_gpr[3] = camry_sp; } return; }
}

void boot_security_delay_progress(void)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = (camry_gp + 0x0u);
  if (((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9356u)))) == '\x01') &&
     (iVar2 = read_ffe51010_word_1d24(),
     (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x6ce4)))) < (uint)(iVar2 - (*((int *)camry_host_ptr((uint32_t)(puVar1 + -0x6ce0))))))) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6caa))))) = 0;
  }
  return;
}

undefined4 boot_security_initialize_handshake(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint32_t puVar4;
  undefined4 uVar5;
  
  puVar4 = (camry_gp + 0x0u);
  (*((volatile uint32_t *)camry_host_ptr((camry_gp + 0xffff931cu)))) = 200000000;
  uVar5 = read_ffe51010_word_1d24();
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6caa))))) = 1;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar4 + -0x6ce0)))) = uVar5;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6ca9))))) = 0;
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(iVar3 + -0x6cdc))))) = 0;
    iVar1 = iVar3 + -0xf;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)((puVar4 + iVar3 + -0x6cdc) + (uint32_t)(0x20))))) = 0;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  iVar3 = 0;
  do {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(iVar3 + -0x6ccc))))) = 0;
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -0xf;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6cac))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6cab))))) = 1;
  return uVar5;
}

void boot_security_cancel_delay(void)

{
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9356u)))) = '\0';
  return;
}

void boot_routine_control_negative_response_5630(uchar param_1)

{
  boot_negative_response('1',param_1);
  return;
}

void boot_routine_control_positive_response_5644(void)

{
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff92d0u)))) = 0x71;
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff92d1u)))) = (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9366u)))) & 0x7f;
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff92d2u)))) = (undefined1)((ushort)(*((volatile uint16_t *)camry_host_ptr((camry_gp + 0xffff9364u)))) >> 8);
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff92d3u)))) = (undefined1)(*((volatile uint16_t *)camry_host_ptr((camry_gp + 0xffff9364u))));
  boot_response_submit((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9366u)))) >> 7 ^ 1,((undefined *)camry_host_ptr((camry_gp + 0xffff92d0u))),(*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9367u)))) + 4);
  return;
}

void boot_service_routine_control(ushort request_length)

{
  uint8_t stack_record_2c[44];
  int iVar1;
  undefined4 *puVar2;
  int iVar3;
  bool bVar4;
  int iVar5;
  uint32_t puVar6;
  uint32_t puVar7;
  F33BootInterruptEntry *pFVar8;
  undefined4 uVar9;
  ushort uVar10;
  uint uVar11;
  ushort uVar12;
  undefined4 unaff_r25;
  undefined1 uVar13;
  uint uVar14;
  uint length;
  uint start;
  
  puVar7 = (camry_gp + 0x0u);
  pFVar8 = ((volatile F33BootInterruptEntry *)camry_host_ptr((camry_tp + 0x0u)));
  stack_record_2c[3] = 0;
  ((uint8_t *)((stack_record_2c + 1)))[1] = 0;
  iVar5 = 0;
  do {
    ((int8_t *)((stack_record_2c + 4)))[iVar5] = '\0';
    iVar3 = iVar5 + 1;
    iVar1 = iVar5 + -1;
    iVar5 = iVar3;
  } while (((iVar1 < 0) || (iVar3 < 0)));
  iVar5 = 0;
  do {
    ((int8_t *)((stack_record_2c + 4)))[iVar5 + 2] = '\0';
    iVar3 = iVar5 + 1;
    iVar1 = iVar5 + -9;
    iVar5 = iVar3;
  } while (((iVar1 < 0) || (iVar3 < 0)));
  boot_copy_request_bytes_and_clear_append_index_67b0(((uint8_t *)((stack_record_2c + 1))) + 1,0xe);
  uVar10 = read_variable_width_big_endian_u32_52a6(((int8_t *)((stack_record_2c + 4))),2);
  bVar4 = true;
  uVar12 = 0;
  uVar14 = (uint)uVar10;
  ((uint8_t *)((stack_record_2c + 1)))[0] = '\x01';
  uVar13 = 0;
  iVar5 = 0;
  do {
    puVar2 = ((undefined4 *)camry_host_ptr((uint32_t)((int)camry_host_addr(pFVar8) + (short)iVar5 * 0xc + 0x8a8)));
    if (uVar14 == *(ushort *)(puVar2 + 1)) {
      uVar13 = *(undefined1 *)(puVar2 + 2);
      bVar4 = false;
      uVar12 = (ushort)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(puVar2) + 7))));
      unaff_r25 = *puVar2;
      break;
    }
    iVar3 = iVar5 + 1;
    iVar1 = iVar5 + -4;
    iVar5 = iVar3;
  } while (((iVar1 < 0) || (iVar3 < 0)));
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(-0x6cf2))))) != (*((char *)((uint8_t *)&pFVar8[0x10b].handler + (1))))) {
    uVar9 = 0x7f;
    goto LAB_00005706;
  }
  if (request_length < 4) {
LAB_0000573c:
    uVar9 = 0x13;
  }
  else {
    if (!bVar4) {
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(-0x6cf1))))) != '\x02') {
        uVar9 = 0x33;
        goto LAB_00005706;
      }
      if ((stack_record_2c[3] & 0x7f) != 1) {
        uVar9 = 0x12;
        goto LAB_00005706;
      }
      if (request_length != (ushort)(uVar12 + 4)) goto LAB_0000573c;
      start = 0;
      puVar6 = ((uint32_t)(uVar14 - 0x10f0));
      length = 0;
      if ((puVar6)<((uint32_t)((uint32_t)(0x2)))) {
        if ((((int8_t *)((stack_record_2c + 4)))[2] == 'E') && (((int8_t *)((stack_record_2c + 4)))[3] == '\0')) {
          start = read_variable_width_big_endian_u32_52a6(((int8_t *)((stack_record_2c + 4))) + 4,4);
          length = read_variable_width_big_endian_u32_52a6(((uint8_t *)((stack_record_2c + 12))),4);
          uVar11 = boot_classify_service_range(start,length,'\x04',((uint8_t *)(stack_record_2c)));
          if ((uVar11 == 0) &&
             (((stack_record_2c[0] != '\0' && (stack_record_2c[0] == '\x01')) &&
              (uVar11 = boot_service_range_completion_selector(start,length,'\x04',((uint8_t *)((stack_record_2c + 1)))),
              uVar11 == 0)))) {
            uVar11 = boot_submit_region_crc_verification(start,length,stack_record_2c[0]);
            if (uVar11 == 0) {
              (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(-0x6ce9))))) = 1;
              goto LAB_000058da;
            }
LAB_000058d2:
            uVar9 = 0x22;
            goto LAB_00005706;
          }
        }
      }
      else if ((puVar6)==((uint32_t)((uint32_t)(0x2)))) {
        if ((((int8_t *)((stack_record_2c + 4)))[2] == 'E') && (((int8_t *)((stack_record_2c + 4)))[3] == '\0')) {
          start = read_variable_width_big_endian_u32_52a6(((int8_t *)((stack_record_2c + 4))) + 4,4);
          length = read_variable_width_big_endian_u32_52a6(((uint8_t *)((stack_record_2c + 12))),4);
          uVar11 = boot_classify_service_range(start,length,'\x04',((uint8_t *)(stack_record_2c)));
          if ((uVar11 == 0) &&
             ((stack_record_2c[0] == '\0' &&
              (uVar11 = boot_service_range_completion_selector(start,length,'\x04',((uint8_t *)((stack_record_2c + 1)))),
              uVar11 == 0)))) {
            uVar11 = boot_submit_region_crc_verification(start,length,stack_record_2c[0]);
            if (uVar11 == 0) {
              (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(-0x6ce9))))) = 2;
              (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(-0x6cef))))) = 0;
              goto LAB_000058da;
            }
            goto LAB_000058d2;
          }
        }
      }
      else {
        if ((puVar6)==((uint32_t)((uint32_t)(0x3)))) {
LAB_000058da:
          (*((ushort *)camry_host_ptr((uint32_t)(puVar7 + -0x6c9c)))) = uVar10;
          (*((uint *)camry_host_ptr((uint32_t)(puVar7 + -0x6ca8)))) = start;
          puVar6 = ((uint32_t)(uVar14 - 0x10f0));
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(-0x6c9a))))) = stack_record_2c[3];
          (*((uint *)camry_host_ptr((uint32_t)(puVar7 + -0x6ca4)))) = length;
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(-0x6c99))))) = uVar13;
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(-0x6c98))))) = ((uint8_t *)((stack_record_2c + 1)))[0];
          if ((puVar6)<((uint32_t)((uint32_t)(0x3)))) {
            (*((undefined4 *)camry_host_ptr((uint32_t)(puVar7 + -0x6ca0)))) = unaff_r25;
            (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(-0x6c97))))) = 1;
            return;
          }
          if ((puVar6)==((uint32_t)((uint32_t)(0x3)))) {
            (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(-0x6ced))))) = 8;
            boot_routine_control_positive_response_5644();
          }
          else {
            if ((puVar6)==((uint32_t)(0xee10u))) {
              (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(-0x6c97))))) = 1;
              return;
            }
            boot_routine_control_negative_response_5630(0x31);
          }
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(-0x6c97))))) = 0;
          return;
        }
        if ((((puVar6)==((uint32_t)(0xee10u))) && (((int8_t *)((stack_record_2c + 4)))[2] == 'E')) && (((int8_t *)((stack_record_2c + 4)))[3] == '\0')) {
          start = read_variable_width_big_endian_u32_52a6(((int8_t *)((stack_record_2c + 4))) + 4,4);
          length = read_variable_width_big_endian_u32_52a6(((uint8_t *)((stack_record_2c + 12))),4);
          uVar11 = boot_classify_service_range(start,length,'\x01',((uint8_t *)(stack_record_2c)));
          if (((uVar11 == 0) && (stack_record_2c[0] == '\0')) &&
             (uVar11 = boot_service_range_completion_selector(start,length,'\x01',((uint8_t *)((stack_record_2c + 1)))),
             uVar11 == 0)) {
            if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(-0x6cef))))) == '\x01') || (((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(-0x6cef)))))) == -0x7f)) &&
               (uVar11 = boot_submit_block_erase(start,length), uVar11 == 0)) {
              (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(-0x6cef))))) = 0x81;
              (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(-0x6ce9))))) = 2;
              boot_set_flash_worker_pause('\x01');
              goto LAB_000058da;
            }
            goto LAB_000058d2;
          }
        }
      }
    }
    uVar9 = 0x31;
  }
LAB_00005706:
  boot_routine_control_negative_response_5630(uVar9);
  return;
}

void boot_advance_crc_authentication_routine_5936(void)

{
  camry_write32((camry_sp - 4u) & ~3u, camry_gpr[31]);
  camry_sp -= 4u;
  camry_gpr[3] = camry_sp;

  char cVar1;
  undefined1 uVar2;
  uint32_t puVar3;
  undefined4 uVar4;
  int iVar5;
  uint uVar6;
  
  puVar3 = (camry_gp + 0x0u);
  iVar5 = (camry_gpr[31] = 0x593eu, boot_get_combined_request_response_state_67f6)();
  if (iVar5 == 6) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6cef))))) = 0;
    uVar4 = 0x10;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6ce9))))) = 0;
  }
  else {
    cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6c97)))));
    if (cVar1 != '\x01') {
      if (cVar1 == '\x02') {
        if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6c03))))) != '\0') {
          { if (!camry_halted) { camry_gpr[31] = camry_read32((camry_sp + 0u) & ~3u); camry_sp += 4u; camry_gpr[3] = camry_sp; } return; }
        }
        if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6c04))))) == '\0') {
          uVar2 = 4;
        }
        else {
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6ce9))))) = 0;
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6cef))))) = 0;
          boot_routine_control_negative_response_5630(0x72);
          uVar2 = 0;
        }
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6c97))))) = uVar2;
        (camry_gpr[31] = 0x59ccu, boot_region_authentication_clear_contexts)();
        goto LAB_00005a00;
      }
      if (cVar1 == '\x04') {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6ce9))))) = 0;
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6cef))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6cef))))) | (byte)(1 << ((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6c98))))) & 0x1f));
        boot_routine_control_positive_response_5644();
      }
      goto LAB_000059fc;
    }
    uVar6 = boot_region_crc_pending();
    if (uVar6 != 0) {
      { if (!camry_halted) { camry_gpr[31] = camry_read32((camry_sp + 0u) & ~3u); camry_sp += 4u; camry_gpr[3] = camry_sp; } return; }
    }
    uVar6 = boot_region_crc_result();
    if (uVar6 == 0) {
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6ceb))))) == '\0') {
        uVar2 = 4;
LAB_00005986:
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6c97))))) = uVar2;
        { if (!camry_halted) { camry_gpr[31] = camry_read32((camry_sp + 0u) & ~3u); camry_sp += 4u; camry_gpr[3] = camry_sp; } return; }
      }
      boot_authentication_crypto_initialize();
      uVar6 = boot_region_authentication_submit
                        ((*((uint *)camry_host_ptr((uint32_t)(puVar3 + -0x6ca8)))),(*((uint *)camry_host_ptr((uint32_t)(puVar3 + -0x6ca4)))));
      if (uVar6 == 0) {
        uVar2 = 2;
        goto LAB_00005986;
      }
      (camry_gpr[31] = 0x5990u, boot_region_authentication_clear_contexts)();
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6ce9))))) = 0;
    uVar4 = 0x72;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6cef))))) = 0;
  }
  boot_routine_control_negative_response_5630(uVar4);
LAB_000059fc:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6c97))))) = 0;
  LAB_00005a00:
  { if (!camry_halted) { camry_gpr[31] = camry_read32((camry_sp + 0u) & ~3u); camry_sp += 4u; camry_gpr[3] = camry_sp; } return; }
}

void boot_advance_crc_authentication_marker_routine_5a04(void)

{
  undefined1 uVar1;
  byte bVar2;
  uint32_t puVar3;
  undefined4 uVar4;
  int iVar5;
  uint uVar6;
  uint local_8;
  
  puVar3 = (camry_gp + 0x0u);
  if ((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9317u)))) != '\x02') {
    return;
  }
  iVar5 = boot_get_combined_request_response_state_67f6();
  if (iVar5 == 6) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6c96))))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6ce9))))) = 0;
    boot_request_flash_worker_cancel();
    uVar4 = 0x10;
  }
  else {
    switch((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6c97)))))) {
    case 1:
      uVar6 = boot_region_crc_pending();
      if (uVar6 != 0) {
        return;
      }
      uVar6 = boot_region_crc_result();
      if (uVar6 == 0) {
        if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6ceb))))) == '\0') {
          bVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6c96))))) | (byte)(1 << ((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6c98))))) & 0x1f));
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6c96))))) = bVar2;
          if ((bVar2 == 1) &&
             (uVar6 = boot_lookup_completion_marker
                                ((*((uint *)camry_host_ptr((uint32_t)(puVar3 + -0x6ca8)))),(*((uint *)camry_host_ptr((uint32_t)(puVar3 + -0x6ca4)))),&local_8),
             uVar6 == 0)) {
            boot_program_completion_marker_word_5286(local_8);
            uVar1 = 3;
          }
          else {
            uVar1 = 4;
          }
LAB_00005a62:
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6c97))))) = uVar1;
          return;
        }
        boot_authentication_crypto_initialize();
        uVar6 = boot_region_authentication_submit
                          ((*((uint *)camry_host_ptr((uint32_t)(puVar3 + -0x6ca8)))),(*((uint *)camry_host_ptr((uint32_t)(puVar3 + -0x6ca4)))));
        if (uVar6 == 0) {
          uVar1 = 2;
          goto LAB_00005a62;
        }
        boot_region_authentication_clear_contexts();
      }
      break;
    case 2:
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6c03))))) != '\0') {
        return;
      }
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6c04))))) == '\0') {
        bVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6c96))))) | (byte)(1 << ((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6c98))))) & 0x1f));
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6c96))))) = bVar2;
        if ((bVar2 == 1) &&
           (uVar6 = boot_lookup_completion_marker
                              ((*((uint *)camry_host_ptr((uint32_t)(puVar3 + -0x6ca8)))),(*((uint *)camry_host_ptr((uint32_t)(puVar3 + -0x6ca4)))),&local_8),
           uVar6 == 0)) {
          boot_program_completion_marker_word_5286(local_8);
          uVar1 = 3;
        }
        else {
          uVar1 = 4;
        }
      }
      else {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6c96))))) = 0;
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6ce9))))) = 0;
        boot_routine_control_negative_response_5630(0x72);
        uVar1 = 0;
      }
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6c97))))) = uVar1;
      boot_region_authentication_clear_contexts();
      return;
    case 3:
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-27999))))) != '\0') {
        return;
      }
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-28000))))) == '\0') {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6c96))))) = 0x81;
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6c97))))) = 4;
        return;
      }
      boot_request_flash_worker_cancel();
      break;
    case 4:
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6ce9))))) = 0;
      boot_routine_control_positive_response_5644();
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6c96))))) = 0;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6c97))))) = 0;
      return;
    default:
      goto switchD_00005a28_default;
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6c96))))) = 0;
    uVar4 = 0x72;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6ce9))))) = 0;
  }
  boot_routine_control_negative_response_5630(uVar4);
switchD_00005a28_default:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6c97))))) = 0;
  return;
}

void boot_advance_flash_worker_routine_5b70(void)

{
  uint32_t puVar1;
  undefined4 uVar2;
  int iVar3;
  
  puVar1 = (camry_gp + 0x0u);
  if ((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9317u)))) != '\x02') {
    return;
  }
  iVar3 = boot_get_combined_request_response_state_67f6();
  if (iVar3 == 6) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6cee))))) = 0;
    boot_request_flash_worker_cancel();
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6ce9))))) = 0;
    uVar2 = 0x10;
  }
  else {
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6c97))))) != '\x01') {
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6c97))))) == '\x04') {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6ce9))))) = 0;
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6cee))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6cee))))) | (byte)(1 << ((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6c98))))) & 0x1f));
        boot_routine_control_positive_response_5644();
      }
      goto LAB_00005bfe;
    }
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-27999))))) != '\0') {
      iVar3 = boot_get_combined_request_response_state_67f6();
      if (iVar3 != 5) {
        return;
      }
      boot_set_flash_worker_pause('\0');
      return;
    }
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-28000))))) == '\0') {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6c97))))) = 4;
      return;
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6cee))))) = 0;
    boot_request_flash_worker_cancel();
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6ce9))))) = 0;
    uVar2 = 0x72;
  }
  boot_routine_control_negative_response_5630(uVar2);
LAB_00005bfe:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6c97))))) = 0;
  return;
}

void boot_routine_timer_progress(void)

{
  uint32_t puVar1;
  
  if (((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9369u)))) != '\0') && ((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff93bcu)))) != '\x01')) {
    puVar1 = ((uint32_t)((*((volatile uint16_t *)camry_host_ptr((camry_gp + 0xffff9364u)))) - 0x10f0));
    if ((puVar1)<((uint32_t)((uint32_t)(0x2)))) {
      boot_advance_crc_authentication_routine_5936();
    }
    else if ((puVar1)==((uint32_t)((uint32_t)(0x2)))) {
      boot_advance_crc_authentication_marker_routine_5a04();
    }
    else if ((puVar1)==((uint32_t)(0xee10u))) {
      boot_advance_flash_worker_routine_5b70();
    }
    else {
      (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9369u)))) = '\0';
    }
  }
  return;
}

void clear_routine_state_and_completion_mask_5c4a(void)

{
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9369u)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff936au)))) = 0;
  return;
}

void boot_transfer_exit_negative_and_mark_download_failed_5c54(uchar param_1)

{
  uint32_t puVar1;
  puVar1 = (camry_gp + 0x0u);
  boot_negative_response('7',param_1);
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6ced))))) != '\0') {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6ced))))) = 0xf;
  }
  return;
}

void boot_transfer_exit_positive_response_5c76(void)

{
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff92d0u)))) = 0x77;
  boot_response_submit('\x01',((undefined *)camry_host_ptr((camry_gp + 0xffff92d0u))),1);
  return;
}

void boot_service_transfer_exit(ushort request_length)

{
  uint32_t puVar1;
  F33BootInterruptEntry *pFVar2;
  undefined4 uVar3;
  int iVar4;
  undefined1 uStack_9;
  
  puVar1 = (camry_gp + 0x0u);
  pFVar2 = ((volatile F33BootInterruptEntry *)camry_host_ptr((camry_tp + 0x0u)));
  boot_copy_request_bytes_and_clear_append_index_67b0(&uStack_9,1);
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6cf2))))) != (char)pFVar2[0x10c].eiic) {
    uVar3 = 0x7f;
    goto LAB_00005cb2;
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6ced))))) == '\x02') {
    iVar4 = get_transfer_remaining_u32_4f98();
    if (iVar4 == 0) {
LAB_00005cfc:
      if (request_length == 1) {
        if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6ceb))))) != '\0') {
          boot_transfer_crypto_clear();
        }
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6ce9))))) = 0;
        (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x6d00)))) = 0;
        (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x6cfc)))) = 0;
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6ced))))) = 0;
        boot_transfer_exit_positive_response_5c76();
        return;
      }
      uVar3 = 0x13;
      goto LAB_00005cb2;
    }
    if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6ce9))))) == '\x02') && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-27999))))) != '\0')) {
      boot_request_flash_worker_cancel();
    }
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6ceb))))) != '\0') {
      boot_transfer_crypto_clear();
    }
  }
  else if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6ced))))) == '\n') && (iVar4 = get_transfer_remaining_u32_4f98(), iVar4 == 0)) goto LAB_00005cfc;
  uVar3 = 0x24;
LAB_00005cb2:
  boot_transfer_exit_negative_and_mark_download_failed_5c54(uVar3);
  return;
}

void return_only_stub_5d2a(void)

{
  return;
}

void boot_request_download_negative_response_5d2c(uchar param_1)

{
  boot_negative_response('4',param_1);
  return;
}

void boot_download_positive_response(void)

{
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff92d0u)))) = 0x74;
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff92d2u)))) = 4;
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff92d1u)))) = 0x20;
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff92d3u)))) = 2;
  boot_response_submit('\x01',((undefined *)camry_host_ptr((camry_gp + 0xffff92d0u))),4);
  return;
}

void boot_service_request_download(ushort request_length)

{
  uint8_t stack_record_22[34];
  bool bVar1;
  int iVar2;
  int iVar3;
  undefined1 uVar4;
  uint32_t puVar5;
  F33BootInterruptEntry *pFVar6;
  undefined4 uVar7;
  uint start;
  uint length;
  uint uVar8;
  int iVar9;
  
  puVar5 = (camry_gp + 0x0u);
  pFVar6 = ((volatile F33BootInterruptEntry *)camry_host_ptr((camry_tp + 0x0u)));
  ((uint8_t *)(stack_record_22))[3] = '\0';
  ((uint8_t *)(stack_record_22))[2] = 0;
  ((uint8_t *)(stack_record_22))[1] = 0;
  iVar9 = 0;
  do {
    ((uint8_t *)(stack_record_22))[iVar9 + 4] = 0;
    iVar3 = iVar9 + 1;
    iVar2 = iVar9 + -5;
    iVar9 = iVar3;
  } while (((iVar2 < 0) || (iVar3 < 0)));
  iVar9 = 0;
  do {
    ((uint8_t *)((stack_record_22 + 10)))[iVar9] = 0;
    iVar3 = iVar9 + 1;
    iVar2 = iVar9 + -3;
    iVar9 = iVar3;
  } while (((iVar2 < 0) || (iVar3 < 0)));
  boot_copy_request_bytes_and_clear_append_index_67b0(((uint8_t *)(stack_record_22)) + 1,0xd);
  start = read_variable_width_big_endian_u32_52a6(((uint8_t *)(stack_record_22)) + 6,4);
  length = read_variable_width_big_endian_u32_52a6(((uint8_t *)((stack_record_22 + 10))),4);
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x6cf2))))) != (*((char *)((uint8_t *)&pFVar6[0x10b].handler + (2))))) {
    uVar7 = 0x7f;
    goto LAB_00005f34;
  }
  if (request_length < 5) {
LAB_00005ea8:
    uVar7 = 0x13;
    goto LAB_00005f34;
  }
  if (((uint8_t *)(stack_record_22))[2] >> 4 == 0) {
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x6ced))))) == '\0') {
      if (((((uint8_t *)(stack_record_22))[2] & 0xf) == (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x6ceb)))))) && (((uint8_t *)(stack_record_22))[3] == 'F')) {
        if (request_length != 0xd) goto LAB_00005ea8;
        if ((((((uint8_t *)(stack_record_22))[4] == '\0') || (((uint8_t *)(stack_record_22))[4] == '\x01')) && (((uint8_t *)(stack_record_22))[5] == '\0')) &&
           ((uVar8 = boot_classify_service_range(start,length,'\0',((uint8_t *)(stack_record_22))), uVar8 == 0 &&
            (((uint8_t *)(stack_record_22))[0] < 2)))) {
          bVar1 = false;
          if (((uint8_t *)(stack_record_22))[0] == 0) {
            if (((uint8_t *)(stack_record_22))[4] == '\0') {
              iVar9 = is_boot_flag_2b12_not_one_52be();
              if (((iVar9 == 0) && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x6cea))))) == '\x01')) &&
                 (uVar8 = boot_submit_erase_program_stream(start,length), uVar8 == 0)) {
                (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x6ce9))))) = 2;
                boot_set_flash_worker_pause('\x01');
              }
              else {
LAB_00005e82:
                bVar1 = true;
              }
LAB_00005e8a:
              uVar4 = 1;
              goto LAB_00005efc;
            }
          }
          else if (((uint8_t *)(stack_record_22))[4] == '\x01') {
            if ((((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x6cef)))))) == -0x7f) || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x6cea))))) != '\x01')) goto LAB_00005e82;
            (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x6ce9))))) = 1;
            goto LAB_00005e8a;
          }
        }
      }
    }
    else {
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x6ced))))) != '\b') {
LAB_00005f30:
        uVar7 = 0x22;
        goto LAB_00005f34;
      }
      if (((((uint8_t *)(stack_record_22))[2] & 0xf) == (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x6ceb)))))) && (((uint8_t *)(stack_record_22))[3] == 'F')) {
        if (request_length != 0xd) goto LAB_00005ea8;
        if ((((((uint8_t *)(stack_record_22))[4] == '\0') && (((uint8_t *)(stack_record_22))[5] == '\0')) &&
            (uVar8 = boot_classify_service_range(start,length,'\x05',((uint8_t *)(stack_record_22))), uVar8 == 0))
           && ((((uint8_t *)(stack_record_22))[0] == 0 && (((uint8_t *)(stack_record_22))[4] == '\0')))) {
          bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x6cea))))) != '\x01';
          if (!bVar1) {
            (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x6ce9))))) = 2;
          }
          uVar4 = 9;
LAB_00005efc:
          if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x6cf1))))) != '\x02') {
            uVar7 = 0x33;
            goto LAB_00005f34;
          }
          if (!bVar1) {
            (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x6ced))))) = uVar4;
            if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x6ceb))))) != '\0') {
              boot_transfer_crypto_initialize();
            }
            (*((uint *)camry_host_ptr((uint32_t)(puVar5 + -0x6d00)))) = start;
            (*((uint *)camry_host_ptr((uint32_t)(puVar5 + -0x6cfc)))) = length;
            fill_constant_block_4f9e();
            boot_download_positive_response();
            return;
          }
          goto LAB_00005f30;
        }
      }
    }
  }
  uVar7 = 0x31;
LAB_00005f34:
  boot_request_download_negative_response_5d2c(uVar7);
  return;
}

void return_only_stub_5f3c(void)

{
  return;
}

uint boot_read_did_fill_payload(uchar descriptor_index,ushort payload_offset)

{
  int iVar1;
  int iVar2;
  
  for (iVar2 = 0;
      iVar1 = iVar2 - (uint)(*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x8f14u + (uint32_t)((short)(ushort)descriptor_index) * (uint32_t)sizeof(F33BootDidEntry)) + (uint32_t)(0) * (uint32_t)sizeof(F33BootDidEntry) + (uint32_t)offsetof(F33BootDidEntry, payload_length))))), ((iVar1 < 0) || (iVar2 < 0));
      iVar2 = iVar2 + 1) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff936eu) + (uint32_t)(iVar2 + (uint)payload_offset) * 1u)))) = 0x21;
  }
  return 0;
}

void boot_read_data_negative_response_5f68(uchar param_1)

{
  boot_negative_response('\"',param_1);
  return;
}

void boot_read_data_positive_payload_response_5f7c(void)

{
  uint uVar1;
  
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff92d0u))))) = 0x62;
  for (uVar1 = 0; uVar1 < (*((volatile uint16_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff936cu))))); uVar1 = uVar1 + 1 & 0xffff) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff92d1u) + (uint32_t)(uVar1) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff936eu) + (uint32_t)(uVar1) * 1u))));
  }
  boot_response_submit('\x01',((undefined *)camry_host_ptr((camry_gp + 0xffff92d0u))),(*((volatile uint16_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff936cu))))) + 1);
  return;
}

void boot_service_read_did(ushort request_length)

{
  uint8_t stack_record_13[19];
  int iVar1;
  char cVar2;
  bool bVar3;
  bool bVar4;
  uint uVar5;
  uint32_t puVar6;
  F33BootInterruptEntry *pFVar7;
  int iVar8;
  undefined4 uVar9;
  ushort payload_offset;
  uint uVar10;
  int iVar11;
  
  puVar6 = (camry_gp + 0x0u);
  pFVar7 = ((volatile F33BootInterruptEntry *)camry_host_ptr((camry_tp + 0x0u)));
  boot_copy_request_bytes_and_clear_append_index_67b0(((uint8_t *)(stack_record_13)),3);
  uVar10 = read_variable_width_big_endian_u32_52a6(((uint8_t *)((stack_record_13 + 1))),2);
  bVar3 = false;
  uVar10 = uVar10 & 0xffff;
  iVar8 = 0;
  do {
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6cf2))))) == (*((char *)((uint8_t *)&pFVar7[0x10c].handler + (iVar8))))) {
      bVar3 = true;
      break;
    }
    iVar1 = iVar8 + 1;
    iVar11 = iVar8 + -2;
    iVar8 = iVar1;
  } while (((iVar11 < 0) || (iVar1 < 0)));
  bVar4 = true;
  uVar5 = 1;
  iVar8 = 0;
  while( true ) {
    iVar11 = (short)iVar8 * 0xc;
    if ((uVar10 == (*((ushort *)camry_host_ptr((uint32_t)((int)camry_host_addr(pFVar7) + iVar11 + 0x87e))))) &&
       (((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(pFVar7) + iVar11 + 0x880)))) & 1) != 0)) break;
    iVar1 = iVar8 + 1;
    iVar11 = iVar8 + -3;
    iVar8 = iVar1;
    if (iVar11 < 0 == (iVar1 < 0 && -1 < iVar11)) {
LAB_0000604e:
      if (bVar3) {
        if (request_length == 3) {
          if (bVar4) {
            uVar9 = 0x31;
          }
          else {
            if (uVar5 == 0) {
              boot_read_data_positive_payload_response_5f7c();
              return;
            }
            uVar9 = 0x72;
          }
        }
        else {
          uVar9 = 0x13;
        }
      }
      else {
        uVar9 = 0x7f;
      }
      boot_read_data_negative_response_5f68(uVar9);
      return;
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6c91))))) = (char)uVar10;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6c92))))) = (char)(uVar10 >> 8);
  iVar11 = (short)iVar8 * 0xc;
  cVar2 = (*((char *)camry_host_ptr((uint32_t)((int)camry_host_addr(pFVar7) + iVar11 + 0x882))));
  payload_offset = 2;
  bVar4 = false;
  if (((int8_t)cVar2) != -1) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6c90))))) = cVar2;
    payload_offset = 3;
  }
  (*((ushort *)camry_host_ptr((uint32_t)(puVar6 + -0x6c94)))) = (*((short *)camry_host_ptr((uint32_t)((int)camry_host_addr(pFVar7) + iVar11 + 0x87c)))) + payload_offset;
  uVar5 = boot_read_did_fill_payload((uchar)iVar8,payload_offset);
  goto LAB_0000604e;
}
