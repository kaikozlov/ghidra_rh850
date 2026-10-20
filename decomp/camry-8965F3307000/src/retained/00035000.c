#include "common.h"

int read_u16_big_endian_35004(byte *param_1)

{
  return (uint)param_1[1] + (uint)*param_1 * 0x100;
}

int read_u32_big_endian_35010(byte *param_1)

{
  return (uint)param_1[3] +
         (uint)param_1[2] * 0x100 + (uint)param_1[1] * 0x10000 + (uint)*param_1 * 0x1000000;
}

undefined4 decode_ba_numeric_field_to_native_width_35028(uint param_1,undefined1 *param_2,undefined1 *param_3)

{
  uchar uVar1;
  undefined2 uVar2;
  undefined4 uVar3;
  
  uVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0x27ec4u + (uint32_t)(param_1 & 0xff) * (uint32_t)sizeof(F33BaConfiguredOperation)) + (uint32_t)(0) * (uint32_t)sizeof(F33BaConfiguredOperation) + (uint32_t)offsetof(F33BaConfiguredOperation, numeric_format)))));
  if (uVar1 == '\x01') {
    *param_3 = *param_2;
  }
  else if (uVar1 == '\x02') {
    uVar2 = read_u16_big_endian_35004(param_2);
    *(undefined2 *)param_3 = uVar2;
  }
  else {
    if (uVar1 != '\x04') {
      if (uVar1 == '\t') {
        *param_3 = *param_2;
        return 0;
      }
      if (uVar1 == '\n') {
        uVar2 = read_u16_big_endian_35004(param_2);
        *(undefined2 *)param_3 = uVar2;
        return 0;
      }
      if (uVar1 != '\f') {
        return 0xfffffffa;
      }
    }
    uVar3 = read_u32_big_endian_35010(param_2);
    *(undefined4 *)param_3 = uVar3;
  }
  return 0;
}

int ba_f1_validate_jtekm(uchar configured_index,uchar *payload,uchar *response)

{
  int iVar1;
  uint uVar2;
  
  uVar2 = compare_ba_token_bytes
                    (payload,"JTEKMTMPCLJTRM1JTRM2BADISBAENATZCLRJTRM3VSPDASINC",'\x05');
  iVar1 = -6;
  if (uVar2 == 1) {
    iVar1 = admit_internal_ba_selector(3,0);
  }
  return iVar1;
}

int ba_f1_latch_selector3(void)

{
  int iVar1;
  
  iVar1 = latch_internal_ba_selector(3);
  return iVar1;
}

int ba_f3_validate_tmpcl(uchar configured_index,uchar *payload,uchar *response)

{
  uint uVar1;
  
  if (ba_application_work.retained_start_phase == '\0') {
    uVar1 = compare_ba_token_bytes
                      (payload,"TMPCLJTRM1JTRM2BADISBAENATZCLRJTRM3VSPDASINC",'\x05');
    if (uVar1 == 1) {
      return 0;
    }
  }
  else if (ba_application_work.retained_start_phase == 'Z') {
    if ((DAT_febe6ee4 == '\x01') || (DAT_febe7de4 == '\x01')) {
      return -1;
    }
    if ((((int8_t)DAT_febe6ee4) == -1) && (((int8_t)DAT_febe7de4) == -1)) {
      return 0;
    }
  }
  return -6;
}

int service_clear_thermal_history(void)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  if (ba_application_work.thermal_clear_phase == '\0') {
    clear_70b0_70b4_70b8_states_3ba78();
    reset_thermal_models_and_history_record();
    publish_thermal_reference_record();
    iVar2 = -1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x58af))))) = 0x5a;
  }
  else if (ba_application_work.thermal_clear_phase == 'Z') {
    if ((DAT_febe6ee4 == '\x01') || (DAT_febe7de4 == '\x01')) {
      iVar2 = -1;
    }
    else {
      if ((((int8_t)DAT_febe6ee4) == -1) && (((int8_t)DAT_febe7de4) == -1)) {
        iVar2 = 0;
      }
      else {
        iVar2 = -6;
      }
      ba_application_work.thermal_clear_phase = '\0';
    }
  }
  else {
    iVar2 = -6;
  }
  return iVar2;
}

int ba_f4_validate_jtrm1(uchar configured_index,uchar *payload,uchar *response)

{
  int iVar1;
  uint uVar2;
  
  uVar2 = compare_ba_token_bytes(payload,"JTRM1JTRM2BADISBAENATZCLRJTRM3VSPDASINC",'\x05');
  iVar1 = -6;
  if (uVar2 == 1) {
    iVar1 = admit_internal_ba_selector(5,0);
  }
  return iVar1;
}

int ba_f4_latch_selector5(void)

{
  int iVar1;
  
  iVar1 = latch_internal_ba_selector(5);
  return iVar1;
}

int ba_f5_validate_jtrm2(uchar configured_index,uchar *payload,uchar *response)

{
  int iVar1;
  uint uVar2;
  
  uVar2 = compare_ba_token_bytes(payload,"JTRM2BADISBAENATZCLRJTRM3VSPDASINC",'\x05');
  iVar1 = -6;
  if (uVar2 == 1) {
    iVar1 = admit_internal_ba_selector(6,0);
  }
  return iVar1;
}

int ba_f5_latch_selector6(void)

{
  int iVar1;
  
  iVar1 = latch_internal_ba_selector(6);
  return iVar1;
}

int ba_f6_request_disable(uchar configured_index,uchar *payload,uchar *response)

{
  uint8_t stack_record_18[24];
  uint32_t puVar1;
  uint uVar2;
  uint uVar3;
  
  puVar1 = 0xfebeb800u;
  if (ba_application_work.retained_start_phase == '\0') {
    uVar2 = compare_ba_token_bytes(payload,"BADISBAENATZCLRJTRM3VSPDASINC",'\x05');
    if (uVar2 == 1) {
      (*((uint32_t *)(stack_record_18 + 4))) = 0;
      (*((uint16_t *)(stack_record_18 + 2))) = 0;
      stack_record_18[1] = 0;
      stack_record_18[0] = 0;
      nvm_set_record(0x18,(uint *)((uint8_t *)(stack_record_18)));
      ((uint32_t *)((stack_record_18 + 8)))[1] = 0;
      ((uint32_t *)((stack_record_18 + 8)))[0] = 0;
      nvm_set_record(0x105,((uint32_t *)((stack_record_18 + 8))));
      return 0;
    }
    return -6;
  }
  if (ba_application_work.retained_start_phase == 'Z') {
    uVar2 = nvm_get_record_status(0x105);
    uVar3 = nvm_get_record_status(0x18);
    if ((uVar2 == 0x10) && (uVar3 == 0x10)) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x58b0))))) = 0;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x58b1))))) = 0;
      return 0;
    }
    if ((uVar2 == 0x20 || uVar2 == 0x21) || (uVar3 == 0x20 || uVar3 == 0x21)) {
      return -1;
    }
  }
  return -9;
}

int ba_f6_finish_disable(void)

{
  uint32_t puVar1;
  uint uVar2;
  uint uVar3;
  int iVar4;
  
  puVar1 = 0xfebeb800u;
  uVar2 = nvm_get_record_status(0x105);
  uVar3 = nvm_get_record_status(0x18);
  if ((uVar2 == 0x10) && (uVar3 == 0x10)) {
    iVar4 = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x58b0))))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x58b1))))) = 0;
  }
  else if ((uVar2 == 0x20 || uVar2 == 0x21) || (uVar3 == 0x20 || uVar3 == 0x21)) {
    iVar4 = -1;
  }
  else {
    iVar4 = -9;
  }
  return iVar4;
}

uint ba_security_level_bit1_enabled(void)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = get_current_security_level_byte_8d9b6();
  uVar1 = 0x5a;
  if ((uVar2 & 2) == 0) {
    uVar1 = 0;
  }
  return uVar1;
}

int ba_f7_request_enable(uchar configured_index,uchar *payload,uchar *response)

{
  uint8_t stack_record_1c[28];
  uint32_t puVar1;
  uint32_t puVar2;
  uint uVar3;
  uint uVar4;
  int iVar5;
  
  puVar1 = 0xfebeb800u;
  puVar2 = 0x23dfcu;
  uVar3 = ba_security_level_bit1_enabled();
  if (uVar3 == 0x5a) {
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x58b4))))) == '\0') {
      uVar3 = compare_ba_token_bytes(payload, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x2d46))), '\x05');
      if (uVar3 == 1) {
        iVar5 = 0;
        ((uint8_t *)(stack_record_1c))[1] = 0;
        ((uint8_t *)(stack_record_1c))[2] = '\0';
        ((uint8_t *)(stack_record_1c))[3] = '\0';
        ((uint8_t *)(stack_record_1c))[4] = '\0';
        ((uint8_t *)(stack_record_1c))[5] = '\0';
        ((uint8_t *)(stack_record_1c))[6] = '\0';
        ((uint8_t *)(stack_record_1c))[7] = '\0';
        ((uint8_t *)(stack_record_1c))[0] = ba_retained_admission_count_limit;
        nvm_set_record(0x18,((uint *)camry_host_ptr((uint32_t)(((uint8_t *)(stack_record_1c))))));
        ((uint32_t *)((stack_record_1c + 8)))[0] = 0xa55a5aa5;
        ((uint32_t *)((stack_record_1c + 8)))[1] = 0;
        nvm_set_record(0x105,((uint32_t *)((stack_record_1c + 8))));
      }
      else {
        iVar5 = -6;
      }
    }
    else {
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x58b4))))) == 'Z') {
        uVar3 = nvm_get_record_status(0x105);
        uVar4 = nvm_get_record_status(0x18);
        if ((uVar3 == 0x10) && (uVar4 == 0x10)) {
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x58b0))))) = ba_retained_admission_count_limit;
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x58b1))))) = 0x5a;
          return 0;
        }
        if ((uVar3 == 0x20 || uVar3 == 0x21) || (uVar4 == 0x20 || uVar4 == 0x21)) {
          return -1;
        }
      }
      iVar5 = -9;
    }
  }
  else {
    iVar5 = -0xe;
  }
  return iVar5;
}

int ba_f7_finish_enable(void)

{
  uint32_t puVar1;
  uint uVar2;
  uint uVar3;
  int iVar4;
  
  puVar1 = 0xfebeb800u;
  uVar2 = nvm_get_record_status(0x105);
  uVar3 = nvm_get_record_status(0x18);
  if ((uVar2 == 0x10) && (uVar3 == 0x10)) {
    iVar4 = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x58b0))))) = ba_retained_admission_count_limit;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x58b1))))) = 0x5a;
  }
  else if ((uVar2 == 0x20 || uVar2 == 0x21) || (uVar3 == 0x20 || uVar3 == 0x21)) {
    iVar4 = -1;
  }
  else {
    iVar4 = -9;
  }
  return iVar4;
}

int ba_f8_validate_tzclr(uchar configured_index,uchar *payload,uchar *response)

{
  char cVar1;
  char cVar2;
  char cVar3;
  ushort uVar4;
  uint uVar5;
  
  uVar4 = DAT_febee892;
  cVar3 = DAT_febee88a;
  cVar2 = DAT_febee884;
  cVar1 = DAT_febee81f;
  uVar5 = compare_ba_token_bytes(payload,"TZCLRJTRM3VSPDASINC",'\x05');
  if ((((uVar5 != 1) || (cVar1 != '\0')) || (ba_tzclr_raw_input_limit < uVar4)) ||
     ((cVar2 == 'Z' || (uVar5 = (uint)(cVar3 == 'Z'), cVar3 == 'Z')))) {
    uVar5 = 0xfffffffa;
  }
  return uVar5;
}

int ba_f8_request_learned_reset(void)

{
  int iVar1;
  
  iVar1 = thunk_coordinate_two_masked_requests_and_return_status_b90ca(0x22,2);
  return iVar1;
}

int ba_f9_validate_jtrm3(uchar configured_index,uchar *payload,uchar *response)

{
  int iVar1;
  uint uVar2;
  
  uVar2 = compare_ba_token_bytes(payload,"JTRM3VSPDASINC",'\x05');
  iVar1 = -6;
  if (uVar2 == 1) {
    iVar1 = admit_internal_ba_selector(7,0);
  }
  return iVar1;
}

int ba_f9_latch_selector7(void)

{
  int iVar1;
  
  iVar1 = latch_internal_ba_selector(7);
  return iVar1;
}

int ba_fa_stage_unsigned_override(uchar configured_index,uchar *payload,uchar *response)

{
  char cVar1;
  uint32_t puVar2;
  uint uVar3;
  int iVar4;
  
  cVar1 = DAT_febe80a5;
  puVar2 = 0xfebeb800u;
  uVar3 = compare_ba_token_bytes(payload + 1,"VSPDASINC",'\x04');
  if ((uVar3 == 1) && (cVar1 != '\0')) {
    iVar4 = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x58ae))))) = *payload;
  }
  else {
    iVar4 = -6;
  }
  return iVar4;
}

int ba_fa_latch_unsigned_override(void)

{
  int iVar1;
  
  iVar1 = latch_ba_unsigned_override(ba_application_work.staged_unsigned_override);
  return iVar1;
}

int ba_fb_validate_asinc(uchar configured_index,uchar *payload,uchar *response)

{
  uint uVar1;
  int iVar2;
  
  uVar1 = compare_ba_token_bytes(payload,"ASINC",'\x05');
  if (uVar1 == 1) {
    iVar2 = 0;
  }
  else {
    iVar2 = -6;
  }
  return iVar2;
}

int ba_fb_latch_owner5_fast_release(void)

{
  int iVar1;
  
  iVar1 = latch_ba_owner5_fast_release();
  return iVar1;
}

void return_only_stub_3552e(void)

{
  return;
}

void return_only_stub_35530(void)

{
  return;
}

undefined4 compare_learned_quad_with_cached_halfwords_35532(void)

{
  if ((((DAT_febe6ad2 == ((volatile uint16_t *)camry_host_ptr(0xfebe6ae6u))[0]) && (DAT_febe6ad4 == (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe6ae6u + (uint32_t)(1) * 2u)))))) &&
      (DAT_febe6ad6 == (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe6ae6u + (uint32_t)(2) * 2u)))))) && (DAT_febe6ad8 == (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe6ae6u + (uint32_t)(3) * 2u)))))) {
    return 0;
  }
  return 0x5a;
}

void cache_current_learned_quad_halfwords_35568(void)

{
  DAT_febe6ad2 = ((volatile uint16_t *)camry_host_ptr(0xfebe6ae6u))[0];
  DAT_febe6ad4 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe6ae6u + (uint32_t)(1) * 2u))));
  DAT_febe6ad6 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe6ae6u + (uint32_t)(2) * 2u))));
  DAT_febe6ad8 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe6ae6u + (uint32_t)(3) * 2u))));
  return;
}

void reset_cached_quad_halfwords_to_2048_35586(void)

{
  DAT_febe6ad2 = 0x800;
  DAT_febe6ad4 = 0x800;
  DAT_febe6ad6 = 0x800;
  DAT_febe6ad8 = 0x800;
  return;
}

void refresh_or_default_cached_learned_quad_35598(void)

{
  uint32_t puVar1;
  uint uVar2;
  uint uVar3;
  
  puVar1 = 0xfebeb800u;
  if (DAT_febe8a18 != 'Z') {
    return;
  }
  uVar3 = (uint)DAT_febe6ad0;
  uVar2 = (uint)DAT_febe6ad1;
  if ((DAT_febe6af0 == -0x5aa5a55b) && (DAT_febe6ae1 == '\0')) {
    puVar1 = 0xfebeb800u;
    uVar3 = compare_learned_quad_with_cached_halfwords_35532();
    if (uVar3 != 0x5a) {
      uVar2 = 0;
      goto LAB_000355e8;
    }
    uVar2 = check_learned_quad_bounds();
    if (uVar2 == 0) {
      cache_current_learned_quad_halfwords_35568();
      goto LAB_000355e8;
    }
  }
  reset_cached_quad_halfwords_to_2048_35586();
LAB_000355e8:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb2d0u + (uint32_t)((int)puVar1) * 1u)))) = (char)uVar3;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb2d1u + (uint32_t)((int)puVar1) * 1u)))) = (char)uVar2;
  return;
}

void return_only_stub_355f4(void)

{
  return;
}

void initialize_learned_quad_record_100_status_356c8(void)

{
  undefined2 uVar1;
  uint32_t puVar2;
  uint uVar3;
  uint uVar4;
  undefined1 uVar5;
  uint local_1c [4];
  
  puVar2 = 0xfebeb800u;
  uVar3 = nvm_get_record(0x100, camry_host_addr(local_1c));
  if (uVar3 == 0x10) {
    if (local_1c[0] != 0) {
      if (local_1c[0] == 0xa55a5aa5) {
        publish_learned_quad();
        uVar3 = check_learned_quad_bounds();
        if (uVar3 == 0) {
          uVar5 = 0x44;
          report_diagnostic_healthy_observed(0x128);
          uVar4 = get_diagnostic_event_state(0xe);
          uVar3 = local_1c[0];
          if ((uVar4 & 1) == 0) {
            clear_event_bit_from_three_bitmaps_and_mark_dirty_524be(0xe);
          }
          else {
            report_diagnostic_event_pass(0xe);
          }
          goto LAB_0003575c;
        }
      }
LAB_00035746:
      uVar3 = 0x5aa5a55a;
      uVar5 = 0x22;
      report_diagnostic_event_failure(0x128,0x32);
      goto LAB_0003575c;
    }
    report_diagnostic_healthy_observed(0x128);
  }
  else {
    if (uVar3 != 0x11) goto LAB_00035746;
    local_1c[0] = 0;
  }
  uVar5 = 0x44;
  route_event_failure_by_e85a_mode_51d38(0xe,10,0x32);
  uVar3 = local_1c[0];
LAB_0003575c:
  uVar1 = DAT_00030e30;
  (*((uint *)camry_host_ptr((uint32_t)((0xffffb2f0u + (uint32_t)((int)puVar2)))))) = uVar3;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb2e0u + (uint32_t)((int)puVar2) * 1u)))) = uVar5;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb2e4u + (uint32_t)((int)puVar2)))))) = uVar1;
  return;
}

void set_four_learned_quad_halfwords_35772(ushort param_1,ushort param_2,ushort param_3,ushort param_4)

{
  ((volatile uint16_t *)camry_host_ptr(0xfebe6ae6u))[0] = param_1;
  (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe6ae6u + (uint32_t)(1) * 2u)))) = param_2;
  (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe6ae6u + (uint32_t)(2) * 2u)))) = param_3;
  (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe6ae6u + (uint32_t)(3) * 2u)))) = param_4;
  return;
}

void persist_learned_quad_record_100_35780(void)

{
  uint8_t stack_record_14[20];
  uint32_t puVar1;
  
  puVar1 = 0xfebeb800u;
  (*((uint16_t *)(stack_record_14 + 4))) = ((volatile uint16_t *)camry_host_ptr(0xfebe6ae6u))[0];
  (*((uint16_t *)(stack_record_14 + 6))) = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe6ae6u + (uint32_t)(1) * 2u))));
  (*((uint16_t *)(stack_record_14 + 8))) = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe6ae6u + (uint32_t)(2) * 2u))));
  (*((uint32_t *)(stack_record_14 + 12))) = 0;
  (*((uint16_t *)(stack_record_14 + 10))) = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe6ae6u + (uint32_t)(3) * 2u))));
  (*((uint32_t *)(stack_record_14 + 0))) = 0xa55a5aa5;
  nvm_set_record(0x100,stack_record_14);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb2ddu + (uint32_t)((int)puVar1) * 1u)))) = 0x11;
  return;
}

void service_learned_quad_request_or_default_persist_357c0(void)

{
  char cVar1;
  undefined *puVar2;
  int iVar3;
  
  puVar2 = ((undefined *)camry_host_ptr(0xfebeb800u));
  if ((((DAT_febe6ae2 == '\x11') && (((int8_t)DAT_febe6add) != -0x78)) && (DAT_febe6add != '\x11')) &&
     (((DAT_febee8cc & 0xff00) != 0x500 || (DAT_febe6af0 != -0x5aa5a55b)))) {
    puVar2 = ((undefined *)camry_host_ptr(0xfebeb800u));
    if ((DAT_febe6add == '\"') ||
       (puVar2 = ((undefined *)camry_host_ptr(0xfebeb800u)), iVar3 = queue_application_service('\x01'), iVar3 != -1)) {
      publish_routine_or_pending_write_terminal_result_4d0a4(8,0x20);
    }
    else {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb2ddu + (uint32_t)((int)camry_host_addr(puVar2)) * 1u)))) = 0x88;
    }
  }
  else {
    cVar1 = DAT_febe6ae2;
    if ((DAT_febe6ae2 != '\"') || (0x3fe < (DAT_febee8cc & 0xff00) - 0x201)) goto LAB_00035842;
    puVar2 = ((undefined *)camry_host_ptr(0xfebeb800u));
    set_four_learned_quad_halfwords_35772(0x800,0x800,0x800,0x800);
    persist_learned_quad_record_100_35780();
  }
  cVar1 = '\0';
LAB_00035842:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb2e2u + (uint32_t)((int)camry_host_addr(puVar2)) * 1u)))) = cVar1;
  return;
}

void step_learned_quad_record_completion(void)

{
  uint32_t puVar1;
  uint uVar2;
  undefined1 uVar3;
  char cVar4;
  char cVar5;
  uint uVar6;
  short sVar7;
  
  puVar1 = 0xfebeb800u;
  service_learned_quad_request_or_default_persist_357c0();
  sVar7 = (*((short *)camry_host_ptr((uint32_t)((0xffffb2e4u + (uint32_t)((int)puVar1))))));
  uVar6 = (*((uint *)camry_host_ptr((uint32_t)((0xffffb2f0u + (uint32_t)((int)puVar1))))));
  cVar5 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb2ddu + (uint32_t)((int)puVar1) * 1u))));
  cVar4 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb2dcu + (uint32_t)((int)puVar1) * 1u))));
  if (sVar7 != 0) {
    sVar7 = sVar7 + -1;
  }
  uVar3 = 0;
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x512b))))) == 'Z') && (uVar6 == 0xa55a5aa5)) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb2e1u + (uint32_t)((int)puVar1) * 1u)))) = 0x5a;
    uVar6 = restore_learned_quad();
    if (uVar6 == 0xa55a5aa5) {
      uVar3 = 0;
    }
    else {
      report_diagnostic_event_failure(0x128,0x32);
      uVar3 = 0x5a;
    }
  }
  if (cVar5 == '\x11') {
    uVar2 = nvm_get_record_status(0x100);
    if (uVar2 == 0x10) {
      uVar6 = 0xa55a5aa5;
      cVar5 = 'D';
      report_diagnostic_event_pass(0xe);
    }
    else if ((uVar2 & 0xf0) != 0x20) {
      cVar5 = '\"';
      report_diagnostic_event_failure(0x130,0x32);
      retain_and_clear_fault_record(0x11);
      encode_fault_action_kind('\x11','\x01');
      select_current_fault_record(0x11);
    }
  }
  if (cVar4 == '\x11') {
    uVar2 = nvm_get_record_status(0x100);
    if (uVar2 == 0x10) {
      uVar6 = 0;
      cVar4 = 'D';
      route_event_failure_by_e85a_mode_51d38(0xe,10,0x32);
    }
    else if ((uVar2 & 0xf0) != 0x20) {
      cVar4 = '\"';
      report_diagnostic_event_failure(0x130,0x32);
      retain_and_clear_fault_record(0x11);
      encode_fault_action_kind('\x11','\x01');
      select_current_fault_record(0x11);
    }
  }
  (*((uint *)camry_host_ptr((uint32_t)((0xffffb2f0u + (uint32_t)((int)puVar1)))))) = uVar6;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb2e4u + (uint32_t)((int)puVar1)))))) = sVar7;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb2ddu + (uint32_t)((int)puVar1) * 1u)))) = cVar5;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb2dcu + (uint32_t)((int)puVar1) * 1u)))) = cVar4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb2e1u + (uint32_t)((int)puVar1) * 1u)))) = uVar3;
  return;
}

void invalidate_learned_quad_record_with_default_payload_3599e(void)

{
  uint8_t stack_record_18[24];
  uint32_t puVar1;
  undefined1 uVar2;
  
  puVar1 = 0xfebeb800u;
  uVar2 = 0x44;
  if (DAT_febe6af0 != 0) {
    (*((uint32_t *)(stack_record_18 + 0))) = 0;
    (*((uint32_t *)(stack_record_18 + 12))) = 0;
    (*((uint16_t *)(stack_record_18 + 10))) = 0x800;
    (*((uint16_t *)(stack_record_18 + 8))) = 0x800;
    (*((uint16_t *)(stack_record_18 + 6))) = 0x800;
    (*((uint16_t *)(stack_record_18 + 4))) = 0x800;
    uVar2 = 0x11;
    puVar1 = 0xfebeb800u;
    nvm_set_record(0x100,stack_record_18);
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb2dcu + (uint32_t)((int)puVar1) * 1u)))) = uVar2;
  return;
}

bool check_learned_quad_action_state_thresholds_35a06(void)

{
  int iVar1;
  ushort uVar2;
  ushort uVar3;
  char cVar4;
  char cVar5;
  char cVar6;
  ushort uVar7;
  bool bVar8;
  short sStack_1e;
  
  uVar7 = DAT_febee892;
  cVar6 = DAT_febee81a;
  cVar5 = DAT_febe80a5;
  cVar4 = DAT_febe80a0;
  uVar3 = DAT_febe66b8;
  uVar2 = DAT_febe6764 & 0x81ff;
  store_saturating_absolute_s16_6a522((int)((int)(int16_t)DAT_febe66a8),&sStack_1e);
  if ((((cVar6 == '\x01') && (DAT_00030e32 <= uVar3)) && (uVar7 <= DAT_00030e34)) &&
     (((cVar5 == '\0' && (cVar4 == '\0')) &&
      (iVar1 = sStack_1e + -0x200, ((iVar1 < 0) || (sStack_1e < 0)))))) {
    bVar8 = uVar2 == 0;
  }
  else {
    bVar8 = false;
  }
  return bVar8;
}

void evaluate_quad_action_gate_and_clear_two_flags_35a68(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  check_learned_quad_action_state_thresholds_35a06();
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb2dfu + (uint32_t)((int)puVar1) * 1u)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb2deu + (uint32_t)((int)puVar1) * 1u)))) = 0;
  return;
}

void report_event_0e_failure_when_quad_marker_zero_35a7c(void)

{
  if (DAT_febe6af0 == 0) {
    report_diagnostic_event_failure(0xe,0x32);
  }
  return;
}

undefined4 request_learned_quad_service_and_return_two_35a96(void)

{
  DAT_febe6ae2 = 0x11;
  return 2;
}

void request_default_quad_when_marker_and_status_allow_35aa2(void)

{
  if ((((DAT_febe6af0 != -1) && (DAT_febe6af0 != -0x5aa5a55b)) && (((int8_t)DAT_febe6add) != -0x78)) &&
     ((DAT_febe6add != '\x11' && (DAT_febe6ae2 != '\x11')))) {
    DAT_febe6ae2 = '\"';
  }
  return;
}

void clear_quad_status_if_88_35ad6(void)

{
  if (((int8_t)DAT_febe6add) == -0x78) {
    DAT_febe6add = '\0';
  }
  return;
}

void return_only_stub_35ae8(void)

{
  return;
}

void fill_constant_block_35aea(void)

{
  DAT_febe5f58 = 0;
  DAT_febe5f59 = 0;
  DAT_febe5f5a = 0;
  DAT_febe5f5e = DAT_0002bd02;
  DAT_febe5f60 = DAT_0002bd02;
  DAT_febe5f5b = 0;
  DAT_febe5f5c = 0;
  DAT_febe5f5d = 0;
  DAT_febe5f62 = DAT_0002bd06;
  DAT_febe5f64 = DAT_0002bd06;
  return;
}

undefined4 reset_indexed_counter_at_limit_and_reload_halfword_35b12(undefined4 param_1,undefined4 param_2,uint param_3)

{
  undefined2 uVar1;
  byte bVar2;
  undefined4 uVar3;
  
  uVar1 = DAT_0002bd02;
  bVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5f58u + (uint32_t)(param_3 & 0xff) * 1u))));
  uVar3 = 0;
  if (DAT_0002bd00 <= bVar2) {
    uVar3 = 0x5a;
    bVar2 = 0;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5f58u + (uint32_t)(param_3 & 0xff) * 1u)))) = bVar2;
  (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe5f5eu + (uint32_t)(param_3 & 0xff) * 2u)))) = uVar1;
  return uVar3;
}

undefined4 reset_exceeded_indexed_count_and_reload_timer_35b44(undefined4 param_1,undefined4 param_2,uint param_3)

{
  undefined2 uVar1;
  byte bVar2;
  undefined4 uVar3;
  
  uVar1 = DAT_0002bd06;
  param_3 = param_3 & 0xff;
  bVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5f5au + (uint32_t)(param_3) * 1u))));
  uVar3 = 0;
  if (DAT_0002bd01 <= bVar2) {
    uVar3 = 0x5a;
    bVar2 = 0;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5f5au + (uint32_t)(param_3) * 1u)))) = bVar2;
  (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe5f62u + (uint32_t)(param_3) * 2u)))) = uVar1;
  return uVar3;
}

void check_paired_counters_and_clear_pending_flags_35b78(void)

{
  undefined1 uVar1;
  int iVar2;
  int iVar3;
  
  uVar1 = DAT_febe5f5c;
  iVar2 = reset_indexed_counter_at_limit_and_reload_halfword_35b12(0,DAT_febe5f5c,0);
  iVar3 = reset_indexed_counter_at_limit_and_reload_halfword_35b12(0x0, (*((volatile uint8_t *)camry_host_ptr(0xfebe5f5du))), 0x1);
  if ((iVar2 == 0x5a) || (iVar3 == 0x5a)) {
    start_or_enqueue_diagnostic_ram_clear_operation4_51866();
    DAT_febe5f58 = 0;
    DAT_febe5f59 = 0;
    DAT_febe5f5e = DAT_0002bd02;
    DAT_febe5f60 = DAT_0002bd02;
  }
  iVar2 = reset_exceeded_indexed_count_and_reload_timer_35b44(0,uVar1,0);
  iVar3 = reset_exceeded_indexed_count_and_reload_timer_35b44(0x0, (*((volatile uint8_t *)camry_host_ptr(0xfebe5f5du))), 0x1);
  if ((iVar2 == 0x5a) || (iVar3 == 0x5a)) {
    thunk_coordinate_two_masked_requests_and_return_status_b90ca(0x22,0);
    DAT_febe5f5a = 0;
    DAT_febe5f5b = 0;
    DAT_febe5f62 = DAT_0002bd06;
    DAT_febe5f64 = DAT_0002bd06;
  }
  DAT_febe5f5c = 0;
  DAT_febe5f5d = 0;
  return;
}

void return_only_stub_35c00(void)

{
  return;
}

void clear_5f68_counter_and_status_state_35c02(void)

{
  DAT_febe5f6c = 0;
  DAT_febe5f68 = 0;
  DAT_febe5f6a = 0;
  DAT_febe5f69 = 0;
  return;
}

void advance_5f6a_counter_and_clear_expired_status_35c10(void)

{
  if ((DAT_0002bd08 <= DAT_febe5f6a) ||
     (DAT_febe5f6a = DAT_febe5f6a + 1, DAT_0002bd08 <= DAT_febe5f6a)) {
    DAT_febe5f69 = 0;
  }
  DAT_febe5f68 = 0;
  return;
}

void return_only_stub_35c36(void)

{
  return;
}

void run_5f6a_counter_update_35c38(void)

{
  advance_5f6a_counter_and_clear_expired_status_35c10();
  return_only_stub_35c36();
  return;
}

void return_only_stub_35c48(void)

{
  return;
}

void return_only_stub_35c4a(void)

{
  return;
}

void sample_motor_command(void)

{
  short sVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  
  iVar5 = (int)((int)(int16_t)DAT_febee782);
  iVar4 = (int)((int)(int16_t)DAT_febeeb10);
  iVar2 = (int)((int)(int16_t)DAT_febee416);
  iVar3 = (int)((int)(int16_t)DAT_febee418);
  if ((DAT_00030f1c == 'Z') && (DAT_00031914 == 'Z')) {
    DAT_febe6af4 = DAT_00031916;
    DAT_febe6af6 = DAT_00031916;
    DAT_febe6af8 = DAT_00031916;
    DAT_febe6afa = ((int)(int16_t)DAT_febee782);
    return;
  }
  DAT_febe6af6 = ((int)(int16_t)DAT_febee40a);
  DAT_febe6af8 = ((int)(int16_t)DAT_febee410);
  sVar1 = ((int)(int16_t)DAT_febee40c);
  if ((DAT_febeeb1e & 0xff00) == 0x500) {
    if (DAT_febee780 == 'Z') {
      if (iVar5 - iVar4 < 0 != (iVar5 < 0 != iVar4 < 0 && iVar4 < 0 == iVar5 - iVar4 < 0)) {
        iVar4 = iVar5;
      }
      iVar3 = -iVar5;
      if (iVar4 + iVar5 < 0 == (iVar4 < 0 != iVar3 < 0 && iVar3 < 0 == iVar4 + iVar5 < 0)) {
        iVar3 = iVar4;
      }
      DAT_febe6af8 = (short)iVar3;
      DAT_febe6af6 = ((int)(int16_t)DAT_febeeb10);
      sVar1 = DAT_febe6af8;
    }
    else if (DAT_febee406 == 'Z') {
      iVar4 = (int)-((int)(int16_t)DAT_febee418);
      if (iVar2 - iVar3 < 0 != (iVar2 < 0 != iVar3 < 0 && iVar3 < 0 == iVar2 - iVar3 < 0)) {
        iVar3 = iVar2;
      }
      if (iVar3 - iVar4 < 0 == (iVar3 < 0 != iVar4 < 0 && iVar4 < 0 == iVar3 - iVar4 < 0)) {
        iVar4 = iVar3;
      }
      DAT_febe6af8 = (short)iVar4;
      DAT_febe6af6 = ((int)(int16_t)DAT_febee416);
      sVar1 = DAT_febe6af8;
    }
  }
  DAT_febe6af4 = -sVar1;
  DAT_febe6afa = ((int)(int16_t)DAT_febee782);
  return;
}

void return_only_stub_35ce8(void)

{
  return;
}

void return_only_stub_35cea(void)

{
  return;
}

void update_limit_budget_branch0(void)

{
  int iVar1;
  int iVar2;
  
  if ((DAT_febe71ec & 1) != 0) {
    DAT_febe6afc = 0;
    DAT_febe6b00 = 0;
    DAT_febe6b04 = 0;
    return;
  }
  iVar1 = DAT_00031938;
  if ((DAT_febe71ec >> 1 & 1) != 0) {
    iVar1 = DAT_0003193c;
  }
  iVar2 = (int)((int)(int16_t)DAT_febe62d6);
  DAT_febe6b04 = iVar1 - (int)((int)(int16_t)DAT_febe62bc) * (int)((int)(int16_t)DAT_febe62d4);
  if (iVar2 < 0) {
    iVar2 = -iVar2;
  }
  else {
    iVar1 = DAT_0003191c;
    if (iVar2 == 0) goto LAB_00035d38;
  }
  iVar1 = DAT_febe6b04;
  if (iVar2 != 0) {
    if (DAT_febe6b04 == -0x80000000 && iVar2 == -1) {
      iVar1 = -0x80000000;
    }
    else {
      iVar1 = (int)DAT_febe6b04 / (int)iVar2;
    }
  }
LAB_00035d38:
  iVar2 = DAT_0003191c;
  if (iVar1 - DAT_0003191c < 0 !=
      (iVar1 < 0 != DAT_0003191c < 0 && DAT_0003191c < 0 == iVar1 - DAT_0003191c < 0)) {
    iVar2 = iVar1;
  }
  DAT_febe6afc = -DAT_0003191c;
  if (iVar2 + DAT_0003191c < 0 ==
      (iVar2 < 0 != ((int)(int32_t)DAT_febe6afc) < 0 && ((int)(int32_t)DAT_febe6afc) < 0 == iVar2 + DAT_0003191c < 0)) {
    DAT_febe6afc = iVar2;
  }
  DAT_febe6b00 = (int)((int)(int16_t)DAT_febe62bc) * (int)((int)(int16_t)DAT_febe62d4);
  return;
}

void return_only_stub_35d54(void)

{
  return;
}

void return_only_stub_35d56(void)

{
  return;
}

void update_limit_budget_branch1(void)

{
  int iVar1;
  int iVar2;
  
  if ((DAT_febe71ec & 2) != 0) {
    DAT_febe6b08 = 0;
    DAT_febe6b0c = 0;
    DAT_febe6b10 = 0;
    return;
  }
  iVar1 = DAT_00031938;
  if ((DAT_febe71ec & 1) != 0) {
    iVar1 = DAT_0003193c;
  }
  iVar2 = (int)((int)(int16_t)DAT_febe62da);
  DAT_febe6b10 = iVar1 - (int)((int)(int16_t)DAT_febe62c0) * (int)((int)(int16_t)DAT_febe62d8);
  if (iVar2 < 0) {
    iVar2 = -iVar2;
  }
  else {
    iVar1 = DAT_00031920;
    if (iVar2 == 0) goto LAB_00035da4;
  }
  iVar1 = DAT_febe6b10;
  if (iVar2 != 0) {
    if (DAT_febe6b10 == -0x80000000 && iVar2 == -1) {
      iVar1 = -0x80000000;
    }
    else {
      iVar1 = (int)DAT_febe6b10 / iVar2;
    }
  }
LAB_00035da4:
  iVar2 = (int)DAT_00031920;
  if (iVar2 < iVar1) {
    iVar1 = iVar2;
  }
  if (iVar1 < -iVar2) {
    iVar1 = -iVar2;
  }
  DAT_febe6b08 = iVar1;
  DAT_febe6b0c = (int)((int)(int16_t)DAT_febe62c0) * (int)((int)(int16_t)DAT_febe62d8);
  return;
}

void return_only_stub_35dc0(void)

{
  return;
}

void reset_owner9_budget_limit_state(void)

{
  DAT_febe6b14 = 0;
  DAT_febe6b15 = 0;
  DAT_febe6b1e = 0;
  DAT_febe6b18 = DAT_0003192a;
  DAT_febe6b24 = (uint)DAT_0003192a << 0x10;
  DAT_febe6b1a = DAT_0003192a;
  DAT_febe6b16 = DAT_0003192a;
  DAT_febe6b28 = (uint)DAT_0003192a << 0x10;
  DAT_febe6b1c = 0;
  return;
}

uint map_owner9_budget_limit(uint budget)

{
  uint uVar1;
  
  uVar1 = lookup_signed_five_map_signal(budget & 0xffff,((int)(int16_t)DAT_febe6422));
  if ((int)(uVar1 - 0x569a) < 0 == ((int)uVar1 < 0 && -1 < (int)(uVar1 - 0x569a))) {
    uVar1 = 0x569a;
  }
  return uVar1 & 0xffff;
}

uint follow_owner9_limit_request(uint target)

{
  short sVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  int iVar5;
  uint uVar6;
  int iVar7;
  uint32_t puVar8;
  uint32_t puVar9;
  
  uVar4 = target & 0xffff;
  uVar6 = 0;
  DAT_febe6b1e = 0;
  uVar2 = (uint)DAT_febe6b16;
  puVar9 = ((uint32_t)((uint)DAT_febe6b1c));
  uVar3 = uVar4;
  if (DAT_00031925 == 'Z') {
    sVar1 = (short)target;
    if (DAT_00031926 == '\x11') {
      if (uVar2 <= uVar4) {
        uVar3 = (uint)DAT_0003192c;
        if (uVar3 - 1 < 0xffff) {
          iVar5 = uVar2 * uVar3;
          iVar7 = uVar4 * uVar3;
        }
        else {
          iVar5 = uVar2 << 0x10;
          iVar7 = target << 0x10;
        }
        DAT_febe6b28 = iVar7 + (DAT_febe6b28 - iVar5);
        iVar5 = (int)DAT_00031930;
        iVar7 = (int)(short)(sVar1 - (short)(DAT_febe6b28 >> 0x10));
        uVar3 = DAT_febe6b28 >> 0x10;
        if (iVar7 - iVar5 < 0 == (iVar7 < 0 != iVar5 < 0 && iVar5 < 0 == iVar7 - iVar5 < 0) &&
            iVar7 != iVar5) goto LAB_00035ec0;
      }
      DAT_febe6b28 = target << 0x10;
      uVar3 = uVar4;
    }
    else {
      if (DAT_00031926 == '\"') {
        uVar3 = (uint)(short)(sVar1 - DAT_febe6b16);
        iVar5 = DAT_0003192e - uVar3;
        puVar8 = puVar9;
        if (iVar5 < 0 != ((int)uVar3 < 0 && (int)uVar3 < 0 == iVar5 < 0)) {
          uVar3 = (uint)DAT_0003192e;
        }
      }
      else {
        if (DAT_00031926 != '3') goto LAB_00035ec0;
        puVar8 = (0x0);
        if (uVar2 < uVar4) {
          uVar6 = ((uint)DAT_febe6b1c + 1) & 0xffff;
          if (0xfffe < uVar6) {
            uVar6 = 0xfffe;
          }
          puVar8 = ((uintptr_t)uVar6);
        }
        uVar6 = ((uint)(uintptr_t)puVar8 * (uint)DAT_00031940) >> 3;
        if (0x5699 < uVar6) {
          uVar6 = 0x569a;
        }
        uVar3 = (uint)(short)(sVar1 - DAT_febe6b16);
        if ((int)(uVar6 - uVar3) < 0 !=
            ((int)uVar3 < 0 && (int)uVar3 < 0 == (int)(uVar6 - uVar3) < 0)) {
          uVar3 = uVar6;
        }
      }
      DAT_febe6b1e = (undefined2)uVar6;
      DAT_febe6b1c = (ushort)puVar8;
      uVar3 = uVar2 + uVar3 & 0xffff;
    }
  }
LAB_00035ec0:
  uVar2 = (uint)DAT_00031932;
  DAT_febe6b20 = (short)uVar3;
  if (uVar3 < uVar2) {
    uVar2 = uVar3;
  }
  uVar3 = (uint)DAT_00031934;
  if (uVar3 <= uVar2) {
    uVar3 = uVar2;
  }
  return uVar3;
}

void publish_owner9_budget_limit(void)

{
  uint uVar1;
  uint32_t puVar2;
  uint uVar3;
  uint uVar4;
  ushort limit;
  int iVar5;
  int iVar6;
  
  puVar2 = 0xfebeb800u;
  if (((int)(int16_t)DAT_febe62dc) < 0) {
    if (DAT_febe6b15 < DAT_00031924) {
      DAT_febe6b15 = DAT_febe6b15 + 1;
      DAT_febe6b14 = 'Z';
    }
    else {
      DAT_febe6b14 = -0x5b;
    }
  }
  else {
    DAT_febe6b15 = 0;
    DAT_febe6b14 = '\0';
  }
  uVar1 = DAT_febe6b08 + DAT_febe6afc;
  uVar4 = (uint)DAT_0003192a;
  if ((int)(uVar1 - uVar4) < 0 != ((int)uVar1 < 0 && -1 < (int)(uVar1 - uVar4))) {
    uVar4 = uVar1;
  }
  if ((int)uVar4 < 0) {
    uVar4 = 0;
  }
  uVar1 = (uint)DAT_00031928;
  if (uVar1 - 1 < 0xffff) {
    iVar5 = DAT_febe6b18 * uVar1;
    iVar6 = (uVar4 & 0xffff) * uVar1;
  }
  else {
    iVar5 = (uint)DAT_febe6b18 << 0x10;
    iVar6 = uVar4 << 0x10;
  }
  uVar1 = iVar6 + (DAT_febe6b24 - iVar5);
  if (((((int8_t)DAT_febe6b14) == -0x5b) || (DAT_febe7827 != '\0')) || (DAT_febe7937 != '\0')) {
    uVar4 = 0x569a;
    limit = 0x569a;
    DAT_febe6b28 = 0x569a0000;
  }
  else {
    puVar2 = 0xfebeb800u;
    uVar4 = map_owner9_budget_limit(uVar1 >> 0x10);
    uVar3 = follow_owner9_limit_request(uVar4);
    limit = (ushort)uVar3;
  }
  set_current_limit_request(9,limit);
  (*((short *)camry_host_ptr((uint32_t)((0xffffb318u + (uint32_t)((int)puVar2)))))) = (short)(uVar1 >> 0x10);
  (*((uint *)camry_host_ptr((uint32_t)((0xffffb324u + (uint32_t)((int)puVar2)))))) = uVar1;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb31au + (uint32_t)((int)puVar2)))))) = (short)uVar4;
  (*((ushort *)camry_host_ptr((uint32_t)((0xffffb316u + (uint32_t)((int)puVar2)))))) = limit;
  return;
}

void return_only_stub_35fac(void)

{
  return;
}

void initialize_terminal_output_ramp(void)

{
  DAT_febe6b2c = 0;
  DAT_febe6b2d = 0;
  DAT_febe6b2e = 0;
  DAT_febe6b30 = 0;
  return;
}

void step_terminal_output_ramp(void)

{
  uint8_t stack_record_1a[26];
  short sVar1;
  uint32_t puVar2;
  undefined1 uVar3;
  ushort uVar4;
  
  uVar4 = DAT_febe6b30;
  puVar2 = 0xfebeb800u;
  if (DAT_febe6b2c == 'Z') {
    if (DAT_febe6b30 < DAT_00030e5a) {
      puVar2 = 0xfebeb800u;
      set_output_request_word('\a',0x40004);
      sVar1 = DAT_00030e5c;
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x5068))))) != '\x01') {
        sVar1 = 1;
      }
      uVar4 = uVar4 + sVar1;
      interpolate_u16_axis_u16_values_70304(((undefined *)camry_host_ptr(0x30e60u)),uVar4,((uint16_t *)(stack_record_1a)));
      uVar3 = 1;
    }
    else {
      puVar2 = 0xfebeb800u;
      set_output_request_word('\a',0x70017001);
      (*((uint16_t *)(stack_record_1a + 0))) = 0x8000;
      uVar3 = 2;
    }
    (*((uint16_t *)(stack_record_1a + 2))) = (*((uint16_t *)(stack_record_1a + 0)));
    (*((uint16_t *)(stack_record_1a + 4))) = (*((uint16_t *)(stack_record_1a + 0)));
    (*((uint16_t *)(stack_record_1a + 6))) = (*((uint16_t *)(stack_record_1a + 0)));
    (*((uint16_t *)(stack_record_1a + 8))) = (*((uint16_t *)(stack_record_1a + 0)));
    (*((uint16_t *)(stack_record_1a + 10))) = (*((uint16_t *)(stack_record_1a + 0)));
    (*((uint16_t *)(stack_record_1a + 12))) = (*((uint16_t *)(stack_record_1a + 0)));
    write_phase_output_slot_pair(2,'\x01',((uint16_t *)((stack_record_1a + 8))),((uint16_t *)((stack_record_1a + 2))));
    activate_phase_output_slot_pair('\x01');
  }
  else {
    set_output_request_word('\a',0);
    uVar4 = 0;
    uVar3 = 0;
    release_phase_output_slot_pair('\x01');
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb32du + (uint32_t)((int)puVar2) * 1u)))) = uVar3;
  (*((ushort *)camry_host_ptr((uint32_t)((0xffffb330u + (uint32_t)((int)puVar2)))))) = uVar4;
  return;
}
