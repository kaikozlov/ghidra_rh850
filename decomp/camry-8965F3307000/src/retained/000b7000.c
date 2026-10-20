#include "common.h"

void run_init_chain_b7054(void)

{
  refresh_record_102_marker_without_diagnostics_b6dfa();
  advance_record_102_b318_write_b6e58();
  advance_record_102_zero_write_b6f24();
  advance_record_102_b31c_write_b6fc4();
  return;
}

void stage_record_102_marker_write_b706c(undefined4 param_1)

{
  DAT_febeb310 = 0x11;
  DAT_febeb318 = param_1;
  return;
}

void prepare_record_102_zero_write_b707a(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  finish_pending_b324_capture_b72a2();
  stop_event_100_monitor_b6c14();
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x4ef))))) = 0x11;
  return;
}

void report_event_ff_for_invalid_b314_b70b0(void)

{
  if (DAT_febeb314 == 0x33333333) {
    report_diagnostic_event_failure(0xff,100);
  }
  return;
}

void clear_b324_capture_status_b70d2(void)

{
  DAT_febeb324 = 0;
  return;
}

void snapshot_f055_into_b321_b70d8(void)

{
  DAT_febeb321 = DAT_febef055;
  return;
}

void publish_bede_admission_capture_gate_b70e2(void)

{
  if ((DAT_000aef5a < DAT_febebede) || (1 < published_internal_source_admission_state)) {
    DAT_febeb323 = 0;
  }
  else {
    DAT_febeb323 = 0x5a;
  }
  return;
}

void debounce_be88_marker_on_f055_changes_b7108(void)

{
  if ((DAT_febeb323 != 'Z') || (DAT_febebe89 != '\0')) {
    DAT_febeb320 = 0;
    DAT_febeb321 = DAT_febef055;
    DAT_febeb328 = 0;
    return;
  }
  if (DAT_febeb321 == DAT_febef055) {
    DAT_febeb321 = DAT_febef055;
    DAT_febeb328 = 0;
    return;
  }
  if (DAT_febeb320 == 0) {
    DAT_febeb320 = DAT_000aef58 != 0;
    DAT_febeb322 = DAT_febebe88;
  }
  else if (DAT_febeb322 == DAT_febebe88) {
    if (DAT_000aef58 <= DAT_febeb320) goto LAB_000b715a;
    DAT_febeb320 = DAT_febeb320 + 1;
  }
  else {
    DAT_febeb320 = 1;
    DAT_febeb322 = DAT_febebe88;
  }
  if (DAT_febeb320 < DAT_000aef58) {
    DAT_febeb321 = DAT_febef055;
    DAT_febeb328 = 0;
    return;
  }
LAB_000b715a:
  if (DAT_febebe88 == 'Z') {
    DAT_febeb328 = 0xaa5555aa;
  }
  else if (DAT_febebe88 == '\0') {
    DAT_febeb328 = 0x55aaaa55;
  }
  else {
    DAT_febeb328 = 0;
    DAT_febeb320 = 0;
  }
  DAT_febeb321 = DAT_febef055;
  return;
}

undefined2 stage_debounced_b328_marker_or_zero_b7186(undefined2 param_1)

{
  if (((DAT_000aef58 <= DAT_febeb320) || (DAT_febeb43c == 'Z')) || (DAT_febeb43b == 'Z')) {
    if ((DAT_febeb328 == -0x55aaaa56) || (DAT_febeb328 == 0x55aaaa55)) {
      stage_record_102_marker_write_b706c((*((volatile uint32_t *)camry_host_ptr(0xfebeb328u))));
      param_1 = 0x2211;
    }
    else {
      stage_record_102_marker_write_b706c(0);
      param_1 = 0x4411;
    }
  }
  return param_1;
}

undefined2 update_capture_gate_debounce_and_marker_stage_b71e2(undefined2 param_1)

{
  ((void)(param_1), publish_bede_admission_capture_gate_b70e2());
  debounce_be88_marker_on_f055_changes_b7108();
  return stage_debounced_b328_marker_or_zero_b7186((uint)(ushort)param_1);
}

undefined ** finalize_record_102_capture_write_status_b71f8(uint param_1)

{
  if (((DAT_febeb310 != '\0') && (DAT_febeb310 != '\x11')) && (DAT_febeb310 != '\"')) {
    if ((DAT_febeb310 == 'D') && ((int)(param_1 & 0xffff) >> 8 == 0x22)) {
      return &PTR_LAB_00008822;
    }
    return (undefined **)((undefined *)camry_host_ptr(0x8844u));
  }
  return ((undefined * *)camry_host_ptr((uint32_t)(param_1 & 0xffff)));
}

void advance_b324_record_102_capture_status_b722c(void)

{
  int iVar1;
  uint32_t puVar2;
  ushort uVar3;
  
  puVar2 = 0xfebeb800u;
  iVar1 = (int)(uint)DAT_febeb324 >> 8;
  uVar3 = DAT_febeb324;
  if (iVar1 != 0) {
    if (iVar1 == 0x11) {
      puVar2 = 0xfebeb800u;
      uVar3 = update_capture_gate_debounce_and_marker_stage_b71e2((*((volatile uint16_t *)camry_host_ptr(0xfebeb324u))));
    }
    else if ((iVar1 == 0x22) || (iVar1 == 0x44)) {
      puVar2 = 0xfebeb800u;
      uVar3 = camry_host_addr(finalize_record_102_capture_write_status_b71f8((*((volatile uint16_t *)camry_host_ptr(0xfebeb324u)))));
    }
    else if (iVar1 != 0x88) {
      uVar3 = 0x8844;
    }
  }
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x4dc)))) = uVar3;
  return;
}

void start_b324_record_102_capture_b726c(void)

{
  undefined1 uVar1;
  uint32_t puVar2;
  undefined1 uVar3;
  undefined1 uVar4;
  ushort uVar5;
  
  uVar1 = DAT_febef055;
  puVar2 = 0xfebeb800u;
  if (((int)(uint)DAT_febeb324 >> 8 == 0) ||
     (uVar4 = DAT_febeb320, uVar3 = DAT_febeb321, uVar5 = DAT_febeb324,
     (int)(uint)DAT_febeb324 >> 8 == 0x88)) {
    uVar4 = 0;
    uVar5 = 0x1111;
    puVar2 = 0xfebeb800u;
    stop_event_100_monitor_b6c14();
    uVar3 = uVar1;
  }
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x4dc)))) = uVar5;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x4e0))))) = uVar4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x4df))))) = uVar3;
  return;
}

void finish_pending_b324_capture_b72a2(void)

{
  if ((int)(uint)DAT_febeb324 >> 8 == 0x11) {
    DAT_febeb324 = 0x8822;
  }
  return;
}

void clear_b334_status_b72ba(void)

{
  DAT_febeb334 = 0;
  return;
}

void return_only_stub_b72c0(void)

{
  return;
}

void fill_constant_block_b72c2(void)

{
  DAT_febeb32f = 0x11;
  DAT_febeb333 = 2;
  DAT_febeb32c = 0;
  DAT_febeb335 = 0;
  DAT_febeb32d = 0;
  DAT_febeb332 = 0;
  DAT_febeb32e = 0;
  DAT_febeb330 = 0;
  return;
}

void reset_b333_b335_workflow_state_b72ec(void)

{
  DAT_febeb333 = 2;
  DAT_febeb32c = 0;
  DAT_febeb334 = 0x22;
  DAT_febeb335 = 0;
  return;
}

void return_only_stub_b733e(void)

{
  return;
}

void fill_constant_block_b7314(void)

{
  DAT_febeb344 = 0x55aaaa55;
  DAT_febeb33b = 0;
  DAT_febeb338 = 0;
  DAT_febeb33d = 0;
  DAT_febeb339 = 0;
  DAT_febeb33e = 0;
  DAT_febeb33a = 0;
  DAT_febeb33f = 0;
  DAT_febeb33c = 0;
  return;
}

void clear_b352_state_b734e(void)

{
  DAT_febeb352 = 0;
  return;
}

void return_only_stub_b7354(void)

{
  return;
}

void return_only_stub_b7356(void)

{
  return;
}

void fill_constant_block_b7358(void)

{
  DAT_febeb352 = 0x8822;
  DAT_febeb348 = 0;
  DAT_febeb34c = 0;
  DAT_febeb349 = 0;
  DAT_febeb34e = 0;
  return;
}

void clear_b354_state_b736c(void)

{
  DAT_febeb354 = 0;
  return;
}

void return_only_stub_b7372(void)

{
  return;
}

int publish_inverted_62e12_result_b7374(void)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  iVar2 = thunk_get_identity_word_febf0668_62e12();
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x4ac))))) = iVar2 == 0;
  return iVar2;
}

void return_only_stub_b738a(void)

{
  return;
}

void start_quad_sample_learning_window_b738c(void)

{
  DAT_febeb358 = 1;
  DAT_febeb359 = 2;
  DAT_febeb35a = 0x1e;
  return;
}

void update_u16_maximum_and_minimum_b73a0(ushort param_1,ushort *param_2,ushort *param_3)

{
  if (*param_2 < param_1) {
    *param_2 = param_1;
  }
  if (param_1 < *param_3) {
    *param_3 = param_1;
  }
  return;
}

void accumulate_validate_and_publish_quad_sample_window_b73cc(void)

{
  uint8_t stack_record_5e[94];
  ushort origin;
  char cVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  uint32_t puVar6;
  undefined4 uVar7;
  int extraout_r7;
  int extraout_r7_00;
  int extraout_r8;
  int extraout_r8_00;
  int iVar8;
  ushort value;
  int iVar9;
  uint uVar10;
  uint uVar11;
  uint uVar12;
  char cVar13;
  uint uVar14;
  uint uVar15;
  uint uVar16;
  char cVar17;
  uint uVar18;
  short sVar19;
  
  sVar19 = DAT_febeb35a;
  cVar17 = DAT_febeb359;
  cVar13 = DAT_febeb358;
  puVar6 = 0xfebeb800u;
  (*((int16_t *)(stack_record_5e + 0))) = DAT_febeb35c;
  (*((int16_t *)(stack_record_5e + 2))) = DAT_febeb35e;
  (*((int16_t *)(stack_record_5e + 4))) = DAT_febeb360;
  (*((int16_t *)(stack_record_5e + 6))) = DAT_febeb362;
  (*((int16_t *)(stack_record_5e + 8))) = DAT_febeb364;
  (*((int16_t *)(stack_record_5e + 10))) = DAT_febeb366;
  (*((int16_t *)(stack_record_5e + 12))) = DAT_febeb368;
  (*((int16_t *)(stack_record_5e + 14))) = DAT_febeb36a;
  uVar14 = DAT_febeb378;
  uVar15 = DAT_febeb374;
  uVar16 = DAT_febeb370;
  uVar18 = DAT_febeb36c;
  if ((DAT_febeb358 != '\x01') || (DAT_febeb37d != 'Z')) goto LAB_000b76ce;
  if (((DAT_febeb05e & 0xc) == 4) ||
     ((((DAT_febeb05e & 0xc) == 8 || ((DAT_febeb060 & 0xc) == 4)) || ((DAT_febeb060 & 0xc) == 8))))
  {
    cVar1 = '\x04';
    uVar7 = 0x31;
    puVar6 = 0xfebeb800u;
  }
  else {
    uVar12 = (uint)DAT_febeb058;
    uVar11 = (uint)DAT_febeb05a;
    uVar10 = (uint)DAT_febeb05c;
    if (DAT_febeb35a == 0x1e) {
      (*((int16_t *)(stack_record_5e + 14))) = 0xfff;
      (*((int16_t *)(stack_record_5e + 12))) = 0xfff;
      (*((int16_t *)(stack_record_5e + 10))) = 0xfff;
      (*((int16_t *)(stack_record_5e + 8))) = 0xfff;
      (*((int16_t *)(stack_record_5e + 6))) = 0;
      (*((int16_t *)(stack_record_5e + 4))) = 0;
      (*((int16_t *)(stack_record_5e + 2))) = 0;
      uVar18 = 0;
      (*((int16_t *)(stack_record_5e + 0))) = 0;
      uVar16 = 0;
      uVar15 = 0;
      uVar14 = 0;
    }
    uVar18 = uVar18 + DAT_febeb056;
    uVar16 = uVar16 + uVar12;
    uVar15 = uVar15 + uVar11;
    uVar14 = uVar14 + uVar10;
    puVar6 = 0xfebeb800u;
    update_u16_maximum_and_minimum_b73a0((uint)DAT_febeb056,((int16_t *)(stack_record_5e)),((int16_t *)((stack_record_5e + 8))));
    update_u16_maximum_and_minimum_b73a0(uVar12, ((ushort *)camry_host_ptr((uint32_t)(extraout_r7 + 2))), ((ushort *)camry_host_ptr((uint32_t)(extraout_r8 + 2))));
    update_u16_maximum_and_minimum_b73a0(uVar11,((int16_t *)((stack_record_5e + 4))),((int16_t *)((stack_record_5e + 12))));
    update_u16_maximum_and_minimum_b73a0(uVar10, ((ushort *)camry_host_ptr((uint32_t)(extraout_r7_00 + 2))), ((ushort *)camry_host_ptr((uint32_t)(extraout_r8_00 + 2))));
    origin = sVar19 - 1;
    sVar19 = sVar19 + -1;
    if (sVar19 != 0) goto LAB_000b76ce;
    (*((uint16_t *)(stack_record_5e + 16))) = (undefined2)( (int)(uVar14) / (int)0x1e);
    (*((uint16_t *)((uint8_t *)((uint32_t *)((stack_record_5e + 42))) + 0u))) = (*((int16_t *)(stack_record_5e + 0))) - (*((int16_t *)(stack_record_5e + 8)));
    (*((uint16_t *)((uint8_t *)((uint32_t *)((stack_record_5e + 42))) + 2u))) = (*((int16_t *)(stack_record_5e + 2))) - (*((int16_t *)(stack_record_5e + 10)));
    (*((uint16_t *)(stack_record_5e + 46))) = (*((int16_t *)(stack_record_5e + 4))) - (*((int16_t *)(stack_record_5e + 12)));
    (*((uint16_t *)(stack_record_5e + 48))) = (*((int16_t *)(stack_record_5e + 6))) - (*((int16_t *)(stack_record_5e + 14)));
    (*((int32_t *)(stack_record_5e + 18))) = scale_u16_delta_s16_x4((ushort)( (int)(uVar18) / (int)0x1e),0x800,-0x9cd);
    (*((int32_t *)(stack_record_5e + 22))) = scale_u16_delta_s16_x4((ushort)( (int)(uVar16) / (int)0x1e),0x800,-0x9cd);
    (*((int32_t *)(stack_record_5e + 26))) = scale_u16_delta_s16_x4((ushort)( (int)(uVar15) / (int)0x1e),0x800,-0x9cd);
    (*((int32_t *)(stack_record_5e + 30))) = scale_u16_delta_s16_x4(value,0x800,-0x9cd);
    (*((int32_t *)(stack_record_5e + 34))) = scale_u16_delta_s16_x4((ushort)(*((uint32_t *)(stack_record_5e + 42))),origin,-0x9cd);
    (*((int32_t *)(stack_record_5e + 38))) = scale_u16_delta_s16_x4((*((uint16_t *)((uint8_t *)((uint32_t *)((stack_record_5e + 42))) + 2u))),origin,-0x9cd);
    (*((uint32_t *)(stack_record_5e + 42))) = scale_u16_delta_s16_x4((*((uint16_t *)(stack_record_5e + 46))),origin,-0x9cd);
    iVar8 = scale_u16_delta_s16_x4((*((uint16_t *)(stack_record_5e + 48))),origin,-0x9cd);
    if ((*((int32_t *)(stack_record_5e + 34))) + 0x7fffffff < 0 == (-1 < (*((int32_t *)(stack_record_5e + 34))) && (*((int32_t *)(stack_record_5e + 34))) + 0x7fffffff < 0) &&
        (*((int32_t *)(stack_record_5e + 34))) != -0x7fffffff) {
      iVar2 = (*((int32_t *)(stack_record_5e + 34)));
      if ((*((int32_t *)(stack_record_5e + 34))) < 0) {
        iVar2 = -(*((int32_t *)(stack_record_5e + 34)));
      }
    }
    else {
      iVar2 = 0x7fffffff;
    }
    if ((*((int32_t *)(stack_record_5e + 38))) + 0x7fffffff < 0 == (-1 < (*((int32_t *)(stack_record_5e + 38))) && (*((int32_t *)(stack_record_5e + 38))) + 0x7fffffff < 0) &&
        (*((int32_t *)(stack_record_5e + 38))) != -0x7fffffff) {
      iVar3 = (*((int32_t *)(stack_record_5e + 38)));
      if ((*((int32_t *)(stack_record_5e + 38))) < 0) {
        iVar3 = -(*((int32_t *)(stack_record_5e + 38)));
      }
    }
    else {
      iVar3 = 0x7fffffff;
    }
    if ((*((uint32_t *)(stack_record_5e + 42))) + 0x7fffffff < 0 == (-1 < (*((uint32_t *)(stack_record_5e + 42))) && (*((uint32_t *)(stack_record_5e + 42))) + 0x7fffffff < 0) &&
        (*((uint32_t *)(stack_record_5e + 42))) != -0x7fffffff) {
      iVar4 = (*((uint32_t *)(stack_record_5e + 42)));
      if ((*((uint32_t *)(stack_record_5e + 42))) < 0) {
        iVar4 = -(*((uint32_t *)(stack_record_5e + 42)));
      }
    }
    else {
      iVar4 = 0x7fffffff;
    }
    if (iVar8 + 0x7fffffff < 0 == (-1 < iVar8 && iVar8 + 0x7fffffff < 0) && iVar8 != -0x7fffffff) {
      if (iVar8 < 0) {
        iVar8 = -iVar8;
      }
    }
    else {
      iVar8 = 0x7fffffff;
    }
    iVar9 = ((*((int32_t *)(stack_record_5e + 26))) - (*((int32_t *)(stack_record_5e + 30)))) / 2;
    iVar5 = ((*((int32_t *)(stack_record_5e + 18))) - (*((int32_t *)(stack_record_5e + 22)))) / 2;
    if (iVar5 + 0x7fffffff < 0 == (-1 < iVar5 && iVar5 + 0x7fffffff < 0) && iVar5 != -0x7fffffff) {
      if (iVar5 < 0) {
        iVar5 = -iVar5;
      }
    }
    else {
      iVar5 = 0x7fffffff;
    }
    if (iVar9 + 0x7fffffff < 0 == (-1 < iVar9 && iVar9 + 0x7fffffff < 0) && iVar9 != -0x7fffffff) {
      if (iVar9 < 0) {
        iVar9 = -iVar9;
      }
    }
    else {
      iVar9 = 0x7fffffff;
    }
    if ((((((*((int32_t *)(stack_record_5e + 18))) - learned_quad_rom_bounds.pair1_upper < 0 !=
            ((*((int32_t *)(stack_record_5e + 18))) < 0 != learned_quad_rom_bounds.pair1_upper < 0 &&
            learned_quad_rom_bounds.pair1_upper < 0 ==
            (*((int32_t *)(stack_record_5e + 18))) - learned_quad_rom_bounds.pair1_upper < 0) ||
            (*((int32_t *)(stack_record_5e + 18))) == learned_quad_rom_bounds.pair1_upper) &&
          ((*((int32_t *)(stack_record_5e + 18))) - learned_quad_rom_bounds.pair1_lower < 0 ==
           ((*((int32_t *)(stack_record_5e + 18))) < 0 != learned_quad_rom_bounds.pair1_lower < 0 &&
           learned_quad_rom_bounds.pair1_lower < 0 ==
           (*((int32_t *)(stack_record_5e + 18))) - learned_quad_rom_bounds.pair1_lower < 0))) &&
         (((*((int32_t *)(stack_record_5e + 22))) - learned_quad_rom_bounds.pair1_upper < 0 !=
           ((*((int32_t *)(stack_record_5e + 22))) < 0 != learned_quad_rom_bounds.pair1_upper < 0 &&
           learned_quad_rom_bounds.pair1_upper < 0 ==
           (*((int32_t *)(stack_record_5e + 22))) - learned_quad_rom_bounds.pair1_upper < 0) ||
           (*((int32_t *)(stack_record_5e + 22))) == learned_quad_rom_bounds.pair1_upper &&
          (((*((int32_t *)(stack_record_5e + 22))) - learned_quad_rom_bounds.pair1_lower < 0 ==
            ((*((int32_t *)(stack_record_5e + 22))) < 0 != learned_quad_rom_bounds.pair1_lower < 0 &&
            learned_quad_rom_bounds.pair1_lower < 0 ==
            (*((int32_t *)(stack_record_5e + 22))) - learned_quad_rom_bounds.pair1_lower < 0) &&
           ((*((int32_t *)(stack_record_5e + 26))) - learned_quad_rom_bounds.pair2_upper < 0 !=
            ((*((int32_t *)(stack_record_5e + 26))) < 0 != learned_quad_rom_bounds.pair2_upper < 0 &&
            learned_quad_rom_bounds.pair2_upper < 0 ==
            (*((int32_t *)(stack_record_5e + 26))) - learned_quad_rom_bounds.pair2_upper < 0) ||
            (*((int32_t *)(stack_record_5e + 26))) == learned_quad_rom_bounds.pair2_upper)))))) &&
        ((*((int32_t *)(stack_record_5e + 26))) - learned_quad_rom_bounds.pair2_lower < 0 ==
         ((*((int32_t *)(stack_record_5e + 26))) < 0 != learned_quad_rom_bounds.pair2_lower < 0 &&
         learned_quad_rom_bounds.pair2_lower < 0 ==
         (*((int32_t *)(stack_record_5e + 26))) - learned_quad_rom_bounds.pair2_lower < 0))) &&
       ((((((*((int32_t *)(stack_record_5e + 30))) - learned_quad_rom_bounds.pair2_upper < 0 !=
            ((*((int32_t *)(stack_record_5e + 30))) < 0 != learned_quad_rom_bounds.pair2_upper < 0 &&
            learned_quad_rom_bounds.pair2_upper < 0 ==
            (*((int32_t *)(stack_record_5e + 30))) - learned_quad_rom_bounds.pair2_upper < 0) ||
            (*((int32_t *)(stack_record_5e + 30))) == learned_quad_rom_bounds.pair2_upper &&
           ((*((int32_t *)(stack_record_5e + 30))) - learned_quad_rom_bounds.pair2_lower < 0 ==
            ((*((int32_t *)(stack_record_5e + 30))) < 0 != learned_quad_rom_bounds.pair2_lower < 0 &&
            learned_quad_rom_bounds.pair2_lower < 0 ==
            (*((int32_t *)(stack_record_5e + 30))) - learned_quad_rom_bounds.pair2_lower < 0))) &&
          (iVar2 - DAT_000aef6c < 0 !=
           (iVar2 < 0 != DAT_000aef6c < 0 && DAT_000aef6c < 0 == iVar2 - DAT_000aef6c < 0) ||
           iVar2 == DAT_000aef6c)) &&
         ((iVar3 - DAT_000aef6c < 0 !=
           (iVar3 < 0 != DAT_000aef6c < 0 && DAT_000aef6c < 0 == iVar3 - DAT_000aef6c < 0) ||
           iVar3 == DAT_000aef6c &&
          (iVar4 - DAT_000aef70 < 0 !=
           (iVar4 < 0 != DAT_000aef70 < 0 && DAT_000aef70 < 0 == iVar4 - DAT_000aef70 < 0) ||
           iVar4 == DAT_000aef70)))) &&
        ((iVar8 - DAT_000aef70 < 0 !=
          (iVar8 < 0 != DAT_000aef70 < 0 && DAT_000aef70 < 0 == iVar8 - DAT_000aef70 < 0) ||
          iVar8 == DAT_000aef70 &&
         ((iVar5 - DAT_000aef74 < 0 !=
           (iVar5 < 0 != DAT_000aef74 < 0 && DAT_000aef74 < 0 == iVar5 - DAT_000aef74 < 0) ||
           iVar5 == DAT_000aef74 &&
          (iVar9 - DAT_000aef78 < 0 !=
           (iVar9 < 0 != DAT_000aef78 < 0 && DAT_000aef78 < 0 == iVar9 - DAT_000aef78 < 0) ||
           iVar9 == DAT_000aef78)))))))) {
      thunk_set_four_learned_quad_halfwords_35772( (int)(uVar18) / (int)0x1e & 0xffff, (int)(uVar16) / (int)0x1e & 0xffff, (int)(uVar15) / (int)0x1e & 0xffff,
                         (*((uint16_t *)(stack_record_5e + 16))));
      cVar13 = '\x02';
      thunk_persist_learned_quad_record_100_35780();
      goto LAB_000b76ce;
    }
    cVar1 = '\x03';
    uVar7 = 0x30;
  }
  if (cVar17 != '\0') {
    cVar17 = cVar17 + -1;
    if (cVar17 == '\0') {
      thunk_route_event_failure_by_e85a_mode_51d38(uVar7,0xb,100);
      set_indexed_request_and_clear_complement_b15ac(0x2d);
      cVar13 = cVar1;
    }
    else {
      cVar13 = '\x01';
    }
  }
  sVar19 = 0x1e;
LAB_000b76ce:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x4a8))))) = cVar13;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x4a7))))) = cVar17;
  (*((short *)camry_host_ptr((uint32_t)(puVar6 + -0x4a6)))) = sVar19;
  (*((short *)camry_host_ptr((uint32_t)(puVar6 + -0x4a4)))) = (*((int16_t *)(stack_record_5e + 0)));
  (*((uint *)camry_host_ptr((uint32_t)(puVar6 + -0x494)))) = uVar18;
  (*((uint *)camry_host_ptr((uint32_t)(puVar6 + -0x490)))) = uVar16;
  (*((uint *)camry_host_ptr((uint32_t)(puVar6 + -0x48c)))) = uVar15;
  (*((short *)camry_host_ptr((uint32_t)(puVar6 + -0x4a2)))) = (*((int16_t *)(stack_record_5e + 2)));
  (*((uint *)camry_host_ptr((uint32_t)(puVar6 + -0x488)))) = uVar14;
  (*((short *)camry_host_ptr((uint32_t)(puVar6 + -0x4a0)))) = (*((int16_t *)(stack_record_5e + 4)));
  (*((short *)camry_host_ptr((uint32_t)(puVar6 + -0x49e)))) = (*((int16_t *)(stack_record_5e + 6)));
  (*((short *)camry_host_ptr((uint32_t)(puVar6 + -0x49c)))) = (*((int16_t *)(stack_record_5e + 8)));
  (*((short *)camry_host_ptr((uint32_t)(puVar6 + -0x49a)))) = (*((int16_t *)(stack_record_5e + 10)));
  (*((short *)camry_host_ptr((uint32_t)(puVar6 + -0x498)))) = (*((int16_t *)(stack_record_5e + 12)));
  (*((short *)camry_host_ptr((uint32_t)(puVar6 + -0x496)))) = (*((int16_t *)(stack_record_5e + 14)));
  return;
}

void return_only_stub_b7714(void)

{
  return;
}

void fill_constant_block_b7716(void)

{
  DAT_febeb37c = 0;
  DAT_febeb37d = 0;
  DAT_febeb380 = 0;
  DAT_febeb382 = 0;
  DAT_febeb384 = 0;
  DAT_febeb37e = 0;
  return;
}

void advance_quad_learning_readiness_delay_b7728(void)

{
  uint32_t puVar1;
  undefined1 uVar2;
  char cVar3;
  ushort uVar4;
  char cVar5;
  short sVar6;
  short sStack_1e;
  
  uVar4 = DAT_febeb382;
  sVar6 = DAT_febeb380;
  uVar2 = DAT_febeb37d;
  puVar1 = 0xfebeb800u;
  sStack_1e = ((int)(int16_t)DAT_febeb384);
  if (((int8_t)DAT_febeb37c) != -0x5b) {
    cVar5 = DAT_febeb37c;
    cVar3 = DAT_febeb37e;
    if (DAT_febeaf44 == '\x01') {
      cVar5 = 'Z';
      cVar3 = cVar5;
    }
    if (DAT_febeb37c == 'Z') {
      if ((((DAT_000aef7e < DAT_febebee4) && (DAT_febebef0 == '\x11')) || (DAT_febef093 != '\0')) ||
         (DAT_febef094 != '\0')) {
        cVar5 = -0x5b;
        puVar1 = 0xfebeb800u;
        thunk_route_event_failure_by_e85a_mode_51d38(0x32,0xb,0x32);
        set_indexed_request_and_clear_complement_b15ac(0x2d);
        cVar3 = -1;
      }
      else {
        puVar1 = 0xfebeb800u;
        lookup_unsigned16_step_table_to_output_d22c0(((undefined *)camry_host_ptr(0xaece4u)),DAT_febeb380,&sStack_1e);
        if (sVar6 != -1) {
          sVar6 = sVar6 + 1;
        }
        if (sStack_1e == 0) {
          if (uVar4 < DAT_000aef7c) {
            uVar4 = uVar4 + 1;
          }
          else {
            cVar5 = -0x5b;
            uVar2 = 0x5a;
            cVar3 = cVar5;
          }
        }
      }
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x484))))) = cVar5;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x483))))) = uVar2;
    (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x480)))) = sVar6;
    (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x47e)))) = uVar4;
    (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x47c)))) = sStack_1e;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x482))))) = cVar3;
  }
  return;
}

void latch_b1a7_and_clear_requests_zero_one_b77f4(void)

{
  set_b1a7_latch_b42f0();
  set_output_request_word('\0',0);
  set_output_request_word('\x01',0);
  return;
}

void publish_requests_zero_one_when_b1a4_clear_b7810(void)

{
  if (DAT_febeb1a4 == '\0') {
    set_output_request_word('\0',0x70017001);
    set_output_request_word('\x01',0x70017001);
    clear_b1a7_latch_b42fa();
  }
  return;
}

void load_halfword_b38c_from_af434_b783c(void)

{
  DAT_febeb38c = DAT_000af434;
  return;
}

void return_only_stub_b784a(void)

{
  return;
}

void update_scaled_afe8_ratio_and_reference_difference_b784c(void)

{
  uint uVar1;
  int iVar2;
  
  uVar1 = (uint)(DAT_febeb138 >> 3);
  if (uVar1 != 0) {
    iVar2 = DAT_febeafe8 * -0x80;
    if (uVar1 != 0) {
      if (iVar2 == -0x80000000 && uVar1 == 0xffffffff) {
        iVar2 = 0;
      }
      else {
        iVar2 = iVar2 / (int)uVar1;
      }
    }
    DAT_febeb394 = (((iVar2 * 0x168) / 0x10) * 100) / 0x1000;
  }
  DAT_febeb398 = 0;
  if (DAT_febeb388 != '\0') {
    DAT_febeb398 = DAT_febeb394 - DAT_febeb390;
  }
  return;
}

void publish_clamped_b398_tenths_or_19999_b7896(void)

{
  uint32_t puVar1;
  int local_8;
  
  puVar1 = 0xfebeb800u;
  if (DAT_febeb388 == '\x02') {
    local_8 = (int)(DAT_febeb398) / (int)10;
    puVar1 = 0xfebeb800u;
    store_signed32_clamped_between_upper_and_lower_d1cf6(local_8,0x7fff,(int)0xffff8001,&local_8);
  }
  else {
    (*((uint16_t *)((uint8_t *)&local_8 + 0u))) = 19999;
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x476)))) = (undefined2)local_8;
  return;
}

void tick_b38c_and_refresh_scaled_difference_b78d0(void)

{
  uint32_t puVar1;
  short sVar2;
  
  puVar1 = 0xfebeb800u;
  sVar2 = DAT_febeb38c;
  if (DAT_febeb38c != 0) {
    sVar2 = DAT_febeb38c + -1;
  }
  update_scaled_afe8_ratio_and_reference_difference_b784c();
  publish_clamped_b398_tenths_or_19999_b7896();
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x474)))) = sVar2;
  return;
}

void clear_ratio_reference_and_mode_b78ee(void)

{
  DAT_febeb390 = 0;
  DAT_febeb388 = 0;
  return;
}

undefined4 initialize_scaled_mean_reference_from_pair_b78f8(int param_1,int param_2)

{
  uint uVar1;
  int iVar2;
  undefined4 uVar3;
  
  uVar1 = (uint)(DAT_febeb138 >> 3);
  if (uVar1 == 0) {
    DAT_febeb388 = 0;
    uVar3 = 0x5a;
    DAT_febeb390 = 0;
  }
  else {
    uVar3 = 0;
    DAT_febeb388 = 1;
    iVar2 = (param_2 + param_1) / 2 << 7;
    if (uVar1 != 0) {
      if (iVar2 == -0x80000000 && uVar1 == 0xffffffff) {
        iVar2 = 0;
      }
      else {
        iVar2 = iVar2 / (int)uVar1;
      }
    }
    DAT_febeb390 = (((iVar2 * 0x168) / 0x10) * 100) / 0x1000;
  }
  update_scaled_afe8_ratio_and_reference_difference_b784c();
  publish_clamped_b398_tenths_or_19999_b7896();
  return uVar3;
}

void invalidate_nonzero_ratio_mode_output_b794e(void)

{
  if (DAT_febeb388 != '\0') {
    DAT_febeb38a = 19999;
    DAT_febeb388 = '\x01';
  }
  return;
}

void enable_ratio_mode_two_and_refresh_output_b7966(void)

{
  DAT_febeb388 = 2;
  update_scaled_afe8_ratio_and_reference_difference_b784c();
  publish_clamped_b398_tenths_or_19999_b7896();
  return;
}

void return_only_stub_b797c(void)

{
  return;
}

void return_only_stub_b797e(void)

{
  return;
}

void latch_b3f8_threshold_result_and_invalidate_ratio_b7980(void)

{
  int iVar1;
  ushort uVar2;
  uint32_t puVar3;
  char cVar4;
  
  puVar3 = 0xfebeb800u;
  cVar4 = DAT_febeb39c;
  if (DAT_febeb39c == '\0') {
    uVar2 = (ushort)DAT_0001be20;
    if (DAT_febeaffc == '\x01') {
      uVar2 = DAT_00013e20;
    }
    if ((((uVar2 != 0) && (DAT_febeb3f4 != '\x02')) && (DAT_febeb3f4 != '\0')) &&
       (((DAT_febeb3f4 != '\x03' && (((int)(int32_t)DAT_febeb3f8) != 0)) && ((DAT_febeb082 & 0x81ff) == 0)))) {
      iVar1 = (uint)uVar2 - DAT_000af478;
      if (iVar1 - ((int)(int32_t)DAT_febeb3f8) < 0 ==
          (iVar1 < 0 != ((int)(int32_t)DAT_febeb3f8) < 0 && ((int)(int32_t)DAT_febeb3f8) < 0 == iVar1 - ((int)(int32_t)DAT_febeb3f8) < 0) &&
          iVar1 != ((int)(int32_t)DAT_febeb3f8)) {
        puVar3 = 0xfebeb800u;
        thunk_gate_indexed_event_payload_during_diagnostic_clears_51cf6(0x24,0x32);
        invalidate_nonzero_ratio_mode_output_b794e();
        cVar4 = '\x02';
      }
      else {
        cVar4 = '\x01';
      }
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x464))))) = cVar4;
  return;
}

void clear_byte_febeb39c_b79fa(void)

{
  DAT_febeb39c = 0;
  return;
}

void return_only_stub_b7a00(void)

{
  return;
}

void fill_constant_block_b7a02(void)

{
  DAT_febeb3a1 = 0;
  DAT_febeb3a2 = 0;
  DAT_febeb3a4 = 0;
  DAT_febeb3a6 = 0;
  DAT_febeb3a0 = 0;
  return;
}

void add_clamped_ac70_correction_to_b3c4_b7a12(void)

{
  uint8_t stack_record_14[20];
  bool bVar1;
  int iVar2;
  undefined1 uVar3;
  int iVar4;
  uint32_t puVar5;
  short sVar6;
  int iVar7;
  
  iVar2 = DAT_febeb3c4;
  puVar5 = 0xfebeb800u;
  (*((int32_t *)(stack_record_14 + 0))) = (((int)(int16_t)DAT_febeac70) * 10) / 8;
  store_signed32_clamped_between_upper_and_lower_d1cf6((*((int32_t *)(stack_record_14 + 0))),(int)DAT_000af480,-(int)DAT_000af480,((int32_t *)(stack_record_14)));
  iVar4 = (int)DAT_000af47c;
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + -0x45e)))) = (short)(*((int32_t *)(stack_record_14 + 0)));
  (*((int32_t *)(stack_record_14 + 4))) = -((*((int32_t *)(stack_record_14 + 0))) * iVar4) / 0x40;
  store_signed32_clamped_between_upper_and_lower_d1cf6((*((int32_t *)(stack_record_14 + 4))),0x7fff,(int)0xffff8001,((int32_t *)((stack_record_14 + 4))));
  sVar6 = DAT_000af47e;
  iVar4 = (int)DAT_000af47e;
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + -0x45c)))) = (short)(*((int32_t *)(stack_record_14 + 4)));
  iVar2 = iVar2 + (*((int32_t *)(stack_record_14 + 4)));
  if (iVar2 - iVar4 < 0 == (iVar2 < 0 != iVar4 < 0 && iVar4 < 0 == iVar2 - iVar4 < 0) &&
      iVar2 != iVar4) {
    uVar3 = 2;
  }
  else {
    iVar7 = -iVar4;
    iVar4 = iVar2 + iVar4;
    bVar1 = iVar2 < 0 != iVar7 < 0 && iVar7 < 0 == iVar4 < 0;
    if (iVar4 < 0 == bVar1) {
      iVar7 = iVar2;
    }
    sVar6 = (short)iVar7;
    uVar3 = iVar4 < 0 != bVar1;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x460))))) = uVar3;
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + -0x45a)))) = sVar6;
  return;
}

void refresh_b3c4_correction_when_b3a1_and_ed00_ready_b7a9e(void)

{
  if ((DAT_febeb3a1 == 'Z') && (DAT_febeed00 == 'Z')) {
    add_clamped_ac70_correction_to_b3c4_b7a12();
  }
  return;
}

void fill_constant_block_b7abe(void)

{
  DAT_febeb3a2 = 0;
  DAT_febeb3a4 = 0;
  DAT_febeb3a6 = 0;
  DAT_febeb3a0 = 0;
  DAT_febeb3a1 = 0x5a;
  return;
}

void fill_constant_block_b7ad2(void)

{
  DAT_febeb3a1 = 0;
  DAT_febeb3a2 = 0;
  DAT_febeb3a4 = 0;
  DAT_febeb3a6 = 0;
  DAT_febeb3a0 = 0;
  return;
}

void return_only_stub_b7ae2(void)

{
  return;
}

void fill_constant_block_b7ae4(void)

{
  DAT_febeb3a8 = 0;
  DAT_febeb3aa = 0;
  DAT_febeb3b8 = 0;
  DAT_febeb3ac = 0;
  DAT_febeb3bc = 0;
  DAT_febeb3b4 = 0;
  DAT_febeb3ae = 0;
  DAT_febeb3c0 = 0;
  DAT_febeb3b0 = 0;
  DAT_febeb3b2 = 0;
  DAT_febeb3c4 = 0;
  return;
}

void update_b398_filtered_proportional_integral_sum_b7b00(void)

{
  uint8_t stack_record_2c[44];
  short sVar1;
  char cVar2;
  int iVar3;
  int iVar4;
  uint32_t puVar5;
  int iVar6;
  
  puVar5 = 0xfebeb800u;
  (*((int32_t *)(stack_record_2c + 4))) = -((int)DAT_febeb398 / 10);
  store_signed32_clamped_between_upper_and_lower_d1cf6((*((int32_t *)(stack_record_2c + 4))),(int)DAT_000af484,-(int)DAT_000af484,((int32_t *)((stack_record_2c + 4))));
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + -0x456)))) = (short)(*((int32_t *)(stack_record_2c + 4)));
  sVar1 = (*((short *)camry_host_ptr((uint32_t)(puVar5 + -0x454))));
  iVar4 = ((*((int32_t *)(stack_record_2c + 4))) - (*((int *)camry_host_ptr((uint32_t)(puVar5 + -0x444))))) + (*((int *)camry_host_ptr((uint32_t)(puVar5 + -0x448))));
  iVar3 = (int)DAT_000af486;
  iVar6 = iVar4;
  if (iVar3 != 0) {
    if (iVar4 == -0x80000000 && iVar3 == -1) {
      iVar6 = -0x80000000;
    }
    else {
      iVar6 = (int)iVar4 / (int)iVar3;
    }
  }
  store_signed32_clamped_between_upper_and_lower_d1cf6(iVar6,0x7fff,(int)0xffff8001,((int32_t *)(stack_record_2c)));
  (*((int32_t *)(stack_record_2c + 12))) = (*((int *)camry_host_ptr((uint32_t)(puVar5 + -0x440))));
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + -0x44c)))) = sVar1;
  (*((int *)camry_host_ptr((uint32_t)(puVar5 + -0x448)))) = iVar4;
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + -0x454)))) = (short)(*((int32_t *)(stack_record_2c + 0)));
  iVar4 = (int)DAT_000af488;
  (*((int *)camry_host_ptr((uint32_t)(puVar5 + -0x444)))) = iVar6;
  cVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x800)))));
  (*((int32_t *)(stack_record_2c + 8))) = ((sVar1 + (*((int32_t *)(stack_record_2c + 0)))) * iVar4) / 0x80;
  store_signed32_clamped_between_upper_and_lower_d1cf6((*((int32_t *)(stack_record_2c + 8))),0x7fff,(int)0xffff8001,((int32_t *)((stack_record_2c + 8))));
  if (((cVar2 != '\x02') || ((*((int32_t *)(stack_record_2c + 8))) < 0)) && ((cVar2 != '\x01' || (-1 < (*((int32_t *)(stack_record_2c + 8))))))) {
    (*((int32_t *)(stack_record_2c + 12))) = (*((int32_t *)(stack_record_2c + 12))) + (*((int32_t *)(stack_record_2c + 8)));
  }
  store_signed32_clamped_between_upper_and_lower_d1cf6((*((int32_t *)(stack_record_2c + 12))),PTR_LAB_000af490,-(int)PTR_LAB_000af490,((int32_t *)((stack_record_2c + 12))));
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + -0x452)))) = (short)(*((int32_t *)(stack_record_2c + 8)));
  (*((int *)camry_host_ptr((uint32_t)(puVar5 + -0x440)))) = (*((int32_t *)(stack_record_2c + 12)));
  (*((int32_t *)(stack_record_2c + 16))) = (*((int32_t *)(stack_record_2c + 0))) * DAT_000af48a;
  store_signed32_clamped_between_upper_and_lower_d1cf6((*((int32_t *)(stack_record_2c + 16))),0x7fff,(int)0xffff8001,((int32_t *)((stack_record_2c + 16))));
  (*((int32_t *)(stack_record_2c + 20))) = 0;
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + -0x450)))) = (short)(*((int32_t *)(stack_record_2c + 16)));
  store_signed32_clamped_between_upper_and_lower_d1cf6(0,0x7fff,(int)0xffff8001,((int32_t *)((stack_record_2c + 20))));
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + -0x44e)))) = (short)(*((int32_t *)(stack_record_2c + 20)));
  (*((int *)camry_host_ptr((uint32_t)(puVar5 + -0x43c)))) = (*((int32_t *)(stack_record_2c + 12))) + (*((int32_t *)(stack_record_2c + 16))) + (*((int32_t *)(stack_record_2c + 20)));
  return;
}

void update_b398_filter_when_b3a8_ready_b7c2c(void)

{
  if (DAT_febeb3a8 == 'Z') {
    update_b398_filtered_proportional_integral_sum_b7b00();
  }
  return;
}

void fill_constant_block_b7c42(void)

{
  DAT_febeb3aa = 0;
  DAT_febeb3b8 = 0;
  DAT_febeb3ac = 0;
  DAT_febeb3bc = 0;
  DAT_febeb3b4 = 0;
  DAT_febeb3ae = 0;
  DAT_febeb3c0 = 0;
  DAT_febeb3b0 = 0;
  DAT_febeb3b2 = 0;
  DAT_febeb3c4 = 0;
  DAT_febeb3a8 = 0x5a;
  return;
}

void fill_constant_block_b7c62(void)

{
  DAT_febeb3a8 = 0;
  DAT_febeb3aa = 0;
  DAT_febeb3b8 = 0;
  DAT_febeb3ac = 0;
  DAT_febeb3bc = 0;
  DAT_febeb3b4 = 0;
  DAT_febeb3ae = 0;
  DAT_febeb3c0 = 0;
  DAT_febeb3b0 = 0;
  DAT_febeb3b2 = 0;
  DAT_febeb3c4 = 0;
  return;
}

void return_only_stub_b7c7e(void)

{
  return;
}

void return_only_stub_b7c80(void)

{
  return;
}

void latch_timed_b3cf_ratio_invalidation_b7c82(void)

{
  undefined1 uVar1;
  uint32_t puVar2;
  ushort uVar3;
  
  uVar3 = DAT_febeb3e0;
  puVar2 = 0xfebeb800u;
  if (DAT_febeb3cf == 'Z') {
    return;
  }
  if (DAT_febeb3e0 < DAT_000af498) {
    uVar3 = DAT_febeb3e0 + 1;
  }
  else if ((DAT_febeb3d1 == 'Z') && ((DAT_febeb3ca == '\0' || (DAT_febeb3db == '\0')))) {
    puVar2 = 0xfebeb800u;
    invalidate_nonzero_ratio_mode_output_b794e();
    uVar1 = 0x5a;
    goto LAB_000b7cc4;
  }
  uVar1 = 0;
LAB_000b7cc4:
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x420)))) = uVar3;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x431))))) = uVar1;
  return;
}

void latch_b054_magnitude_ratio_invalidation_b7cd0(void)

{
  char cVar1;
  char cVar2;
  char cVar3;
  char cVar4;
  int iVar5;
  uint32_t puVar6;
  int iVar7;
  undefined1 uVar8;
  short sStack_16;
  
  cVar4 = DAT_febeb3db;
  cVar3 = DAT_febeb3d2;
  cVar2 = DAT_febeb3d1;
  cVar1 = DAT_febeb3ca;
  puVar6 = 0xfebeb800u;
  if (DAT_febeb3d0 == 'Z') {
    return;
  }
  store_saturated_signed16_absolute_d1178((int)((int)(int16_t)DAT_febeb054),&sStack_16);
  if (cVar3 == '\0') {
    iVar5 = (int)DAT_000af4ac;
    iVar7 = (int)sStack_16;
    if (iVar7 - iVar5 < 0 != (iVar7 < 0 != iVar5 < 0 && iVar5 < 0 == iVar7 - iVar5 < 0) ||
        iVar7 == iVar5) goto LAB_000b7d0a;
LAB_000b7d1a:
    if ((cVar2 == 'Z') && ((cVar1 == '\0' || (cVar4 == '\0')))) {
      invalidate_nonzero_ratio_mode_output_b794e();
      uVar8 = 0x5a;
      goto LAB_000b7d30;
    }
  }
  else {
LAB_000b7d0a:
    if (cVar3 == 'Z') {
      iVar5 = (int)DAT_000af4ae;
      iVar7 = (int)sStack_16;
      if (iVar7 - iVar5 < 0 == (iVar7 < 0 != iVar5 < 0 && iVar5 < 0 == iVar7 - iVar5 < 0) &&
          iVar7 != iVar5) goto LAB_000b7d1a;
    }
  }
  uVar8 = 0;
LAB_000b7d30:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x430))))) = uVar8;
  return;
}

uchar qualify_service_progress(uchar done,uchar cancel)

{
  uchar uVar1;
  
  if (cancel == 'Z') {
    DAT_febeb3cb = 0;
    uVar1 = 'Z';
  }
  else if (done == 'Z') {
    DAT_febeb3cb = 2;
    uVar1 = 'Z';
  }
  else if (((((DAT_febeb079 == '\0') && (DAT_febeb11a < 0x600)) && ((DAT_febeb082 & 0x81ff) == 0))
           && ((DAT_febeb3cf != 'Z' && (DAT_febeb3d0 != 'Z')))) &&
          ((DAT_febeb39c != '\x02' && ((DAT_febebef0 == '\x11' && (DAT_febebede <= DAT_000af49c)))))
          ) {
    DAT_febeb3cb = 1;
    uVar1 = '\0';
  }
  else {
    uVar1 = 'Z';
    DAT_febeb3cb = 3;
  }
  return uVar1;
}

uchar advance_to_phase_two_after_b3d4_latch_b7dba(uchar phase)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_febeb3d4 == 'Z') {
    puVar1 = 0xfebeb800u;
    fill_constant_block_b8a10();
    fill_constant_block_b8b10();
    phase = '\x02';
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x42c))))) = 0x5a;
  return phase;
}

undefined4 debounce_small_afdc_and_afe8_delta_b7de2(void)

{
  uint8_t stack_record_16[22];
  int iVar1;
  byte bVar2;
  int iVar3;
  uint32_t puVar4;
  undefined4 uVar5;
  char cVar6;
  
  iVar3 = DAT_febeb3ec;
  bVar2 = DAT_febeb3cd;
  iVar1 = DAT_febeafe8;
  puVar4 = 0xfebeb800u;
  store_saturated_signed16_absolute_d1178((int)((int)(int16_t)DAT_febeafdc),((int16_t *)(stack_record_16)));
  store_saturated_signed32_absolute_d1194(iVar1 - iVar3,((int32_t *)((stack_record_16 + 2))));
  if ((int)(*((int16_t *)(stack_record_16 + 0))) >= (int)(short)DAT_000af4a0 || (*((int32_t *)(stack_record_16 + 2))) >= (int)DAT_000af4b0) {
    cVar6 = '\0';
    uVar5 = 0;
  }
  else if (bVar2 < DAT_000af495) {
    uVar5 = 0;
    cVar6 = bVar2 + 1;
  }
  else {
    cVar6 = '\0';
    uVar5 = 0x5a;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x433))))) = cVar6;
  return uVar5;
}

uchar advance_to_phase_three_after_stable_delta_b7e44(uchar phase)

{
  int iVar1;
  
  iVar1 = debounce_small_afdc_and_afe8_delta_b7de2();
  if (iVar1 == 0x5a) {
    fill_constant_block_b8b24();
    fill_constant_block_b8a30();
    phase = '\x03';
  }
  return phase;
}

undefined4 increment_b3ce_until_byte_limit_then_signal_b7e66(byte param_1)

{
  undefined4 uVar1;
  
  if (DAT_febeb3ce < param_1) {
    uVar1 = 0;
    DAT_febeb3ce = DAT_febeb3ce + 1;
  }
  else {
    DAT_febeb3ce = '\0';
    uVar1 = 0x5a;
  }
  return uVar1;
}

uchar update_service_minimum_excursion(uchar qualification)

{
  uint32_t puVar1;
  uchar uVar2;
  int iVar3;
  int iVar4;
  
  puVar1 = 0xfebeb800u;
  iVar3 = -DAT_febeafe8;
  iVar4 = ((int)(int32_t)DAT_febeb3e4);
  uVar2 = DAT_febeb3c8;
  if (DAT_febeb3c8 != 'Z') {
    if (iVar3 - ((int)(int32_t)DAT_febeb3e4) < 0 ==
        (iVar3 < 0 != ((int)(int32_t)DAT_febeb3e4) < 0 && ((int)(int32_t)DAT_febeb3e4) < 0 == iVar3 - ((int)(int32_t)DAT_febeb3e4) < 0)) {
      iVar3 = ((int)(int32_t)DAT_febeb3e4);
    }
    puVar1 = 0xfebeb800u;
    uVar2 = increment_b3ce_until_byte_limit_then_signal_b7e66(qualification);
    iVar4 = iVar3;
  }
  (*((int *)camry_host_ptr((uint32_t)(puVar1 + -0x41c)))) = iVar4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x438))))) = uVar2;
  return uVar2;
}

uchar advance_to_phase_four_after_minimum_excursion_b7eb2(uchar phase)

{
  uchar uVar1;
  
  uVar1 = update_service_minimum_excursion(DAT_000af494);
  if (uVar1 == 'Z') {
    fill_constant_block_b8a10();
    fill_constant_block_b8b10();
    phase = '\x04';
  }
  return phase;
}

uchar advance_to_phase_five_after_stable_delta_b7edc(uchar phase)

{
  int iVar1;
  
  iVar1 = debounce_small_afdc_and_afe8_delta_b7de2();
  if (iVar1 == 0x5a) {
    fill_constant_block_b8b24();
    fill_constant_block_b8a30();
    phase = '\x05';
  }
  return phase;
}

uchar update_service_maximum_excursion(uchar qualification)

{
  uint32_t puVar1;
  uchar uVar2;
  int iVar3;
  int iVar4;
  
  puVar1 = 0xfebeb800u;
  iVar3 = -DAT_febeafe8;
  iVar4 = ((int)(int32_t)DAT_febeb3e8);
  uVar2 = DAT_febeb3c9;
  if (DAT_febeb3c9 != 'Z') {
    if (iVar3 - ((int)(int32_t)DAT_febeb3e8) < 0 !=
        (iVar3 < 0 != ((int)(int32_t)DAT_febeb3e8) < 0 && ((int)(int32_t)DAT_febeb3e8) < 0 == iVar3 - ((int)(int32_t)DAT_febeb3e8) < 0) ||
        iVar3 == ((int)(int32_t)DAT_febeb3e8)) {
      iVar3 = ((int)(int32_t)DAT_febeb3e8);
    }
    puVar1 = 0xfebeb800u;
    uVar2 = increment_b3ce_until_byte_limit_then_signal_b7e66(qualification);
    iVar4 = iVar3;
  }
  (*((int *)camry_host_ptr((uint32_t)(puVar1 + -0x418)))) = iVar4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x437))))) = uVar2;
  return uVar2;
}

uint queue_service_center_and_check_geometry(void)

{
  uint8_t stack_record_18[24];
  undefined4 uVar1;
  undefined4 uVar2;
  uint32_t puVar3;
  uint uVar4;
  
  uVar2 = DAT_febeb3e8;
  uVar1 = DAT_febeb3e4;
  puVar3 = 0xfebeb800u;
  store_saturated_signed32_absolute_d1194(DAT_febeb3e4,stack_record_18);
  store_saturated_signed32_absolute_d1194(uVar2,(stack_record_18 + 4));
  write_nvm_106_word_with_zero_tail_b865e(((((*((int32_t *)(stack_record_18 + 4))) + (*((int32_t *)(stack_record_18 + 0)))) / 0x80) * DAT_000af4b8 * 10) / 0x20000);
  uVar4 = initialize_scaled_mean_reference_from_pair_b78f8(uVar1,uVar2);
  (*((int *)camry_host_ptr((uint32_t)(puVar3 + -0x410)))) = (*((int32_t *)(stack_record_18 + 4))) + (*((int32_t *)(stack_record_18 + 0)));
  return uVar4;
}

uchar select_phase_six_or_nine_after_maximum_excursion_b7f8a(uchar phase)

{
  uchar uVar1;
  uint uVar2;
  
  uVar1 = update_service_maximum_excursion(DAT_000af494);
  if (uVar1 == 'Z') {
    uVar2 = queue_service_center_and_check_geometry();
    if (uVar2 == 0x5a) {
      phase = '\t';
    }
    else {
      phase = '\x06';
    }
  }
  return phase;
}

undefined4 debounce_b398_magnitude_with_halfword_counter_b7fb8(int param_1,ushort param_2)

{
  ushort uVar1;
  uint32_t puVar2;
  undefined4 uVar3;
  short sVar4;
  int local_14;
  
  uVar1 = DAT_febeb3de;
  puVar2 = 0xfebeb800u;
  store_saturated_signed32_absolute_d1194(DAT_febeb398,&local_14);
  uVar3 = 0;
  if (local_14 - param_1 < 0 ==
      (local_14 < 0 != param_1 < 0 && param_1 < 0 == local_14 - param_1 < 0) && local_14 != param_1)
  {
    sVar4 = 0;
  }
  else if (uVar1 < param_2) {
    sVar4 = uVar1 + 1;
  }
  else {
    sVar4 = 0;
    uVar3 = 0x5a;
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + -0x422)))) = sVar4;
  return uVar3;
}

uchar complete_phase_seven_or_start_phase_eight_ramp_b7ff4(uchar phase)

{
  char cVar1;
  uint32_t puVar2;
  int iVar3;
  undefined1 uVar4;
  
  puVar2 = 0xfebeb800u;
  iVar3 = debounce_b398_magnitude_with_halfword_counter_b7fb8(DAT_000af4b4,DAT_000af4a2);
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x42d)))));
  uVar4 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x436)))));
  if (iVar3 == 0x5a) {
    fill_constant_block_b7ad2();
    fill_constant_block_b7c62();
    if (cVar1 == 'Z') {
      phase = '\t';
      enable_ratio_mode_two_and_refresh_output_b7966();
      uVar4 = 0x5a;
    }
    else {
      fill_constant_block_b8872();
      phase = '\b';
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x436))))) = uVar4;
  return phase;
}
