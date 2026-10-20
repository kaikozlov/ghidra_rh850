#include "common.h"

uint write_2013_service_numeric_target(uchar *payload,ushort unused_length)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  set_service_numeric_target_thunk(CONCAT11(*payload,payload[1]));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x364e)))) = 0;
  return 0;
}

uint write_2014_precondition(void)

{
  if (((DAT_febe80a5 == '\0') && (DAT_febe80a0 == '\0')) && (DAT_febee892 <= DAT_000318ae)) {
    return 0;
  }
  return 5;
}

uint write_2014_service_qualification_mode(uchar *payload,ushort unused_length)

{
  uint32_t puVar1;
  uchar mode;
  uint uVar2;
  
  puVar1 = 0xfebeb800u;
  if (*payload == '\0') {
    mode = '\0';
  }
  else {
    if (*payload != '\x01') {
      uVar2 = 4;
      goto LAB_0005008c;
    }
    mode = 'Z';
  }
  puVar1 = 0xfebeb800u;
  set_service_qualification_mode_thunk(mode);
  uVar2 = 0;
LAB_0005008c:
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x364e)))) = 0;
  return uVar2;
}

void forward_byte_store_to_febf3b20_50094(undefined1 param_1)

{
  set_status_byte3b20_8b79a(param_1);
  return;
}

uint diag_routine_1001_admit(void)

{
  uint uVar1;
  
  if (DAT_febe819a == '\x01') {
    uVar1 = 5;
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}

uint diag_routine_1001_family_capabilities
               (uchar control_type,uchar *unused_input,ushort unused_input_length,uchar *output,
               ushort *output_length)

{
  uint32_t puVar1;
  uint uVar2;
  
  puVar1 = 0xfebeb800u;
  uVar2 = 0;
  if (control_type == '\x01') {
    ((void)(unused_input_length), build_table_identifier_group_bitmap_4d222(camry_host_addr(output), 0x20));
    *output_length = 0x20;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3664))))) = 2;
  }
  else if (control_type == '\x03') {
    *output = DAT_febe819c;
    *output_length = 1;
  }
  else {
    uVar2 = 7;
  }
  return uVar2;
}

uint diag_routine_1000_admit(void)

{
  uint uVar1;
  
  if (DAT_febe819a == '\x01') {
    uVar1 = 5;
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}

uint diag_routine_1000_capabilities
               (uchar control_type,uchar *unused_input,ushort unused_input_length,uchar *output,
               ushort *output_length)

{
  uint32_t puVar1;
  uint uVar2;
  
  puVar1 = 0xfebeb800u;
  uVar2 = 0;
  if (control_type == '\x01') {
    build_identifier_page_member_bitmap_4d308(0x1000, camry_host_addr(output), 0x20);
    *output_length = 0x20;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3665))))) = 2;
  }
  else if (control_type == '\x03') {
    *output = DAT_febe819b;
    *output_length = 1;
  }
  else {
    uVar2 = 7;
  }
  return uVar2;
}

uint diag_routine_1002_admit(uchar control_type)

{
  if (DAT_febe819a == '\x01') {
    return 5;
  }
  if (control_type == '\x01') {
    if (DAT_000318ae < DAT_febee892) {
      return 5;
    }
    if (DAT_febe819d == '\x01') {
      return 8;
    }
  }
  else if (control_type != '\x03') {
    return 7;
  }
  return 0;
}

uint diag_routine_1002_normalize_lifecycle
               (uchar control_type,uchar *unused_input,ushort unused_input_length,uchar *output,
               ushort *output_length)

{
  ushort uVar1;
  uint32_t puVar2;
  puVar2 = 0xfebeb800u;
  if (control_type == '\x01') {
    ((void)(1), (void)(unused_input), (void)(unused_input_length), request_default_quad_when_marker_and_status_allow_35aa2());
    thunk_set_byte_febeaf47_b9320(0x44);
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x3663))))) = 1;
    uVar1 = 0;
  }
  else {
    if (control_type != '\x03') {
      return 7;
    }
    *output = DAT_febe819d;
    uVar1 = 1;
  }
  *output_length = uVar1;
  return 0;
}

uint diag_routine_1004_admit(uchar control_type,uchar *input)

{
  if (DAT_febe819a == '\x01') {
    return 5;
  }
  if (control_type == '\x01') {
    if ((*input != 0xff) || (input[1] != 0xff)) {
      return 4;
    }
    if (DAT_febe819e == '\x01') {
      return 8;
    }
  }
  else if (control_type != '\x03') {
    return 7;
  }
  return 0;
}

uint diag_routine_1004_request_history_rewrite
               (uchar control_type,uchar *unused_input,ushort unused_input_length,uchar *output,
               ushort *output_length)

{
  ushort uVar1;
  int application_status;
  uint uVar2;
  
  if (control_type == '\x01') {
    application_status = ((void)(1), (void)(unused_input), (void)(unused_input_length), start_or_enqueue_diagnostic_operation5_518e0());
    uVar2 = diag_translate_application_request_status(application_status);
    if (uVar2 == 0) {
      DAT_febe819e = '\x01';
    }
    uVar1 = 0;
  }
  else {
    if (control_type != '\x03') {
      return 7;
    }
    uVar2 = 0;
    *output = DAT_febe819e;
    uVar1 = 1;
  }
  *output_length = uVar1;
  return uVar2;
}

uint diag_routine_1007_admit(uchar control_type)

{
  char cVar1;
  int iVar2;
  
  cVar1 = DAT_febe819f;
  if (control_type == '\x01') {
    iVar2 = thunk_check_selected_pair_of_lifecycle_states_idle_b8d9c(0);
    if (iVar2 != 0x5a) {
      return 5;
    }
    if (cVar1 == '\x01') {
      return 8;
    }
  }
  else if (control_type != '\x03') {
    return 7;
  }
  return 0;
}

uint diag_routine_1007_restart_lifecycle_group0
               (uchar control_type,uchar *unused_input,ushort unused_input_length,uchar *output,
               ushort *output_length)

{
  ushort uVar1;
  uint32_t puVar2;
  puVar2 = 0xfebeb800u;
  if (control_type == '\x01') {
    ((void)(unused_input), (void)(unused_input_length), thunk_start_selected_b438_or_b439_lifecycle_group_b8dda(0));
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x3661))))) = 1;
    uVar1 = 0;
  }
  else {
    if (control_type != '\x03') {
      return 7;
    }
    *output = DAT_febe819f;
    uVar1 = 1;
  }
  *output_length = uVar1;
  return 0;
}

uint diag_routine_1008_admit(uchar control_type)

{
  char cVar1;
  int iVar2;
  
  cVar1 = DAT_febe81a0;
  if (control_type == '\x01') {
    iVar2 = thunk_check_selected_pair_of_lifecycle_states_idle_b8d9c(2);
    if (iVar2 != 0x5a) {
      return 5;
    }
    if (cVar1 == '\x01') {
      return 8;
    }
  }
  else if (control_type != '\x03') {
    return 7;
  }
  return 0;
}

uint diag_routine_1008_restart_lifecycle_group2
               (uchar control_type,uchar *unused_input,ushort unused_input_length,uchar *output,
               ushort *output_length)

{
  ushort uVar1;
  uint32_t puVar2;
  puVar2 = 0xfebeb800u;
  if (control_type == '\x01') {
    ((void)(1), (void)(unused_input), (void)(unused_input_length), thunk_start_b43a_lifecycle_group_and_clear_counter_b8e52());
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x3660))))) = 1;
    uVar1 = 0;
  }
  else {
    if (control_type != '\x03') {
      return 7;
    }
    *output = DAT_febe81a0;
    uVar1 = 1;
  }
  *output_length = uVar1;
  return 0;
}

uint diag_routine_1009_admit(uchar control_type)

{
  if (DAT_febe819a == '\x01') {
    return 5;
  }
  if (control_type == '\x01') {
    if (DAT_febe81a1 == '\x01') {
      return 8;
    }
  }
  else if (control_type != '\x03') {
    return 7;
  }
  return 0;
}

uint diag_routine_1009_reset_record103
               (uchar control_type,uchar *unused_input,ushort unused_input_length,uchar *output,
               ushort *output_length)

{
  ushort uVar1;
  uint32_t puVar2;
  puVar2 = 0xfebeb800u;
  if (control_type == '\x01') {
    ((void)(1), (void)(unused_input), (void)(unused_input_length), thunk_prepare_record_103_invalid_write_b69c6());
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x365f))))) = 1;
    uVar1 = 0;
  }
  else {
    if (control_type != '\x03') {
      return 7;
    }
    *output = DAT_febe81a1;
    uVar1 = 1;
  }
  *output_length = uVar1;
  return 0;
}

uint diag_routine_1100_admit(void)

{
  uint uVar1;
  
  if (DAT_febe819a == '\x01') {
    uVar1 = 5;
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}

uint diag_routine_1100_capabilities
               (uchar control_type,uchar *unused_input,ushort unused_input_length,uchar *output,
               ushort *output_length)

{
  uint32_t puVar1;
  uint uVar2;
  
  puVar1 = 0xfebeb800u;
  uVar2 = 0;
  if (control_type == '\x01') {
    build_identifier_page_member_bitmap_4d308(0x1100, camry_host_addr(output), 0x20);
    *output_length = 0x20;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x365e))))) = 2;
  }
  else if (control_type == '\x03') {
    *output = DAT_febe81a2;
    *output_length = 1;
  }
  else {
    uVar2 = 7;
  }
  return uVar2;
}

uint diag_routine_1103_admit(uchar control_type)

{
  int iVar1;
  uint uVar2;
  
  if (DAT_febe819a == '\x01') {
LAB_0005042c:
    uVar2 = 5;
  }
  else {
    if (control_type == '\x01') {
      iVar1 = check_learned_quad_action_state_thresholds_35a06();
      if ((iVar1 != 1) || (DAT_febe81a6 == '\x01')) goto LAB_0005042c;
      if (DAT_febe81a3 == '\x01') {
        return 8;
      }
    }
    else if (control_type != '\x03') {
      return 7;
    }
    uVar2 = 0;
  }
  return uVar2;
}

uint diag_routine_1103_request_service1
               (uchar control_type,uchar *unused_input,ushort unused_input_length,uchar *output,
               ushort *output_length)

{
  ushort uVar1;
  uint uVar2;
  
  if (control_type == '\x01') {
    uVar2 = ((void)(1), (void)(unused_input), (void)(unused_input_length), request_learned_quad_service_and_return_two_35a96());
    if (uVar2 == 2) {
      uVar2 = 0;
      DAT_febe81a3 = '\x01';
    }
    uVar1 = 0;
  }
  else {
    if (control_type != '\x03') {
      return 7;
    }
    uVar2 = 0;
    *output = DAT_febe81a3;
    uVar1 = 1;
  }
  *output_length = uVar1;
  return uVar2;
}

uint diag_routine_1106_admit(uchar control_type)

{
  if (DAT_febe819a == '\x01') {
    return 5;
  }
  if (control_type == '\x01') {
    if (DAT_000318ae < DAT_febee892) {
      return 5;
    }
    if (DAT_febe81a4 == '\x01') {
      return 8;
    }
  }
  else if (control_type != '\x03') {
    return 7;
  }
  return 0;
}

uint diag_routine_1106_restart_lifecycle_groups
               (uchar control_type,uchar *unused_input,ushort unused_input_length,uchar *output,
               ushort *output_length)

{
  ushort uVar1;
  uint32_t puVar2;
  puVar2 = 0xfebeb800u;
  if (control_type == '\x01') {
    ((void)(1), (void)(unused_input), (void)(unused_input_length), thunk_initialize_three_state_groups_and_b214_b524a());
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x365c))))) = 1;
    uVar1 = 0;
  }
  else {
    if (control_type != '\x03') {
      return 7;
    }
    *output = DAT_febe81a4;
    uVar1 = 1;
  }
  *output_length = uVar1;
  return 0;
}

uint diag_routine_1108_admit(uchar control_type)

{
  if (DAT_febe819a == '\x01') {
    return 5;
  }
  if (control_type == '\x01') {
    if (DAT_febe81a5 == '\x01') {
      return 8;
    }
  }
  else if (control_type != '\x03') {
    return 7;
  }
  return 0;
}

uint diag_routine_1108_request_checkpoint_reset
               (uchar control_type,uchar *unused_input,ushort unused_input_length,uchar *output,
               ushort *output_length)

{
  ushort uVar1;
  int application_status;
  uint uVar2;
  
  if (control_type == '\x01') {
    application_status = ((void)(1), (void)(unused_input), (void)(unused_input_length), start_or_enqueue_diagnostic_clear_operation2_517dc());
    uVar2 = diag_translate_application_request_status(application_status);
    if (uVar2 == 0) {
      DAT_febe81a5 = '\x01';
    }
    uVar1 = 0;
  }
  else {
    if (control_type != '\x03') {
      return 7;
    }
    uVar2 = 0;
    *output = DAT_febe81a5;
    uVar1 = 1;
  }
  *output_length = uVar1;
  return uVar2;
}

uint diag_routine_1109_admit(uchar control_type)

{
  if (DAT_febe819a == '\x01') {
    return 5;
  }
  if (control_type == '\x01') {
    if (DAT_000318ae < DAT_febee892) {
      return 5;
    }
    if (DAT_febe81a3 == '\x01') {
      return 5;
    }
    if (DAT_febe80a0 != '\0') {
      return 5;
    }
    if (DAT_febe80a5 != '\0') {
      return 5;
    }
    if (DAT_febee81f != '\0') {
      return 5;
    }
    if (DAT_febee884 == 'Z') {
      return 5;
    }
    if (DAT_febee88a == 'Z') {
      return 5;
    }
    if (DAT_febe81a6 == '\x01') {
      return 8;
    }
  }
  else if (control_type != '\x03') {
    return 7;
  }
  return 0;
}

uint diag_routine_1109_request_record100_reset
               (uchar control_type,uchar *unused_input,ushort unused_input_length,uchar *output,
               ushort *output_length)

{
  ushort uVar1;
  int application_status;
  uint uVar2;
  
  if (control_type == '\x01') {
    application_status = ((void)(unused_input_length), thunk_coordinate_two_masked_requests_and_return_status_b90ca(0x22, 1));
    uVar2 = diag_translate_application_request_status(application_status);
    if (uVar2 == 2) {
      uVar2 = 0;
      DAT_febe81a6 = '\x01';
    }
    else if (uVar2 == 0) {
      DAT_febe81a6 = '\x02';
    }
    uVar1 = 0;
  }
  else {
    if (control_type != '\x03') {
      return 7;
    }
    uVar2 = 0;
    *output = DAT_febe81a6;
    uVar1 = 1;
  }
  *output_length = uVar1;
  return uVar2;
}

uint diag_routine_110a_admit(uchar control_type)

{
  uint32_t puVar1;
  uint uVar2;
  
  puVar1 = 0xfebeb800u;
  if (DAT_febe819a == '\x01') {
    return 5;
  }
  if (control_type == '\x01') {
    uVar2 = qualify_service_admission('\x01');
    if ((((uVar2 == 0) || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x365a))))) == '\x01')) || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x3084))))) == 'Z')) ||
       ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x308a))))) == 'Z')) {
      return 5;
    }
    if (DAT_febe81a7 == '\x01') {
      return 8;
    }
  }
  else if (control_type == '\x02') {
    if (DAT_febe81a7 == '\0') {
      return 8;
    }
  }
  else if (control_type != '\x03') {
    return 7;
  }
  return 0;
}

uint diag_routine_110a_control_service2
               (uchar control_type,uchar *unused_input,ushort unused_input_length,uchar *output,
               ushort *output_length)

{
  ushort uVar1;
  int application_status;
  uint uVar2;
  
  if (control_type == '\x01') {
    application_status = queue_application_service('\x02');
    uVar2 = diag_translate_application_request_status(application_status);
    if (uVar2 == 2) {
      uVar2 = 0;
      thunk_clear_byte_febeb3dd_b85d0();
      DAT_febe81a7 = '\x01';
    }
    uVar1 = 0;
  }
  else if (control_type == '\x02') {
    if (DAT_febe81a7 == '\x01') {
      ((void)(2), (void)(unused_input), (void)(unused_input_length), thunk_set_b3dd_ready_and_clear_b3cb_b85bc());
    }
    else {
      DAT_febe81a7 = '\0';
    }
    uVar2 = 0;
    uVar1 = 0;
  }
  else {
    if (control_type != '\x03') {
      return 7;
    }
    uVar2 = 0;
    *output = DAT_febe81a7;
    uVar1 = 1;
  }
  *output_length = uVar1;
  return uVar2;
}

uint diag_routine_110b_admit_noop(void)

{
  return 0;
}

uint diag_routine_110b_action_noop(void)

{
  return 0;
}

uint diag_routine_110c_admit(uchar control_type)

{
  uint32_t puVar1;
  uint uVar2;
  
  puVar1 = 0xfebeb800u;
  if (DAT_febe819a == '\x01') {
LAB_00050758:
    uVar2 = 5;
  }
  else {
    if (control_type == '\x01') {
      uVar2 = qualify_service_admission('\x02');
      if ((((uVar2 == 0) || (DAT_febe81a6 == '\x01')) || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x308a))))) == 'Z')) ||
         (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x3084))))) == 'Z' || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x3089))))) == '\0')))) goto LAB_00050758;
      if (DAT_febe81a9 == '\x01') {
        return 8;
      }
    }
    else if (control_type != '\x03') {
      return 7;
    }
    uVar2 = 0;
  }
  return uVar2;
}

uint diag_routine_110c_request_service3
               (uchar control_type,uchar *unused_input,ushort unused_input_length,uchar *output,
               ushort *output_length)

{
  ushort uVar1;
  int application_status;
  uint uVar2;
  
  if (control_type == '\x01') {
    application_status = queue_application_service('\x03');
    uVar2 = diag_translate_application_request_status(application_status);
    if (uVar2 == 2) {
      uVar2 = 0;
      DAT_febe81a9 = '\x01';
    }
    uVar1 = 0;
  }
  else {
    if (control_type != '\x03') {
      return 7;
    }
    uVar2 = 0;
    *output = DAT_febe81a9;
    uVar1 = 1;
  }
  *output_length = uVar1;
  return uVar2;
}

uint diag_routine_110d_admit(uchar control_type)

{
  uint32_t puVar1;
  uint uVar2;
  
  puVar1 = 0xfebeb800u;
  if (DAT_febe819a == '\x01') {
    return 5;
  }
  if (control_type == '\x01') {
    uVar2 = qualify_service_admission('\x03');
    if ((((uVar2 == 0) || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x365a))))) == '\x01')) || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x308a))))) == 'Z')) ||
       ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x3084))))) == 'Z')) {
      return 5;
    }
    if (DAT_febe81aa == '\x01') {
      return 8;
    }
  }
  else if (control_type == '\x02') {
    if (DAT_febe81aa == '\0') {
      return 8;
    }
  }
  else if (control_type != '\x03') {
    return 7;
  }
  return 0;
}

uint diag_routine_110d_control_service4
               (uchar control_type,uchar *unused_input,ushort unused_input_length,uchar *output,
               ushort *output_length)

{
  ushort uVar1;
  int application_status;
  uint uVar2;
  
  if (control_type == '\x01') {
    application_status = queue_application_service('\x04');
    uVar2 = diag_translate_application_request_status(application_status);
    if (uVar2 == 2) {
      uVar2 = 0;
      thunk_clear_byte_febeb3dc_b85ca();
      DAT_febe81aa = '\x01';
    }
    uVar1 = 0;
  }
  else if (control_type == '\x02') {
    if (DAT_febe81aa == '\x01') {
      ((void)(2), (void)(unused_input), (void)(unused_input_length), thunk_set_b3dc_ready_and_clear_b3cb_b85ae());
    }
    else {
      DAT_febe81aa = '\0';
    }
    uVar2 = 0;
    uVar1 = 0;
  }
  else {
    if (control_type != '\x03') {
      return 7;
    }
    uVar2 = 0;
    *output = DAT_febe81aa;
    uVar1 = 1;
  }
  *output_length = uVar1;
  return uVar2;
}

void diag_routine_clear_nonrunning_results(uchar preserve_selector2)

{
  uint uVar1;
  
  uVar1 = 0;
  if (preserve_selector2 == 'Z') {
    do {
      if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe819bu + (uint32_t)(uVar1) * 1u)))) != '\x01') && (uVar1 != 2)) {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe819bu + (uint32_t)(uVar1) * 1u)))) = 0;
      }
      uVar1 = uVar1 + 1;
    } while (uVar1 < 0x10);
    return;
  }
  do {
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe819bu + (uint32_t)(uVar1) * 1u)))) != '\x01') {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe819bu + (uint32_t)(uVar1) * 1u)))) = 0;
    }
    uVar1 = uVar1 + 1;
  } while (uVar1 < 0x10);
  return;
}

void diag_routine_publish_terminal_result(uchar result_selector,uchar completion_status)

{
  undefined1 uVar1;
  uint uVar2;
  
  uVar2 = (uint)result_selector;
  if (uVar2 < 0x10) {
    if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe819bu + (uint32_t)(uVar2) * 1u)))) == '\x01') && (completion_status != '\x10')) {
      if (completion_status == '\0') {
        uVar1 = 2;
      }
      else if (completion_status == '0') {
        uVar1 = 0;
      }
      else {
        uVar1 = 3;
      }
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe819bu + (uint32_t)(uVar2) * 1u)))) = uVar1;
    }
  }
  return;
}

undefined4 return_const_0_50900(void)

{
  return 0;
}

void publish_dtc_setting_request(uchar selection)

{
  dtc_setting_inhibit_request = '\0';
  if (selection == '\x02') {
    dtc_setting_inhibit_request = 'Z';
  }
  return;
}

void set_pending_kind_and_two_halfword_arguments_50916(undefined1 param_1,undefined2 param_2,undefined2 param_3)

{
  DAT_febe81ad = param_1;
  DAT_febe81ba = param_2;
  DAT_febe81bc = param_3;
  return;
}

uint serialize_selected_proprietary_event(uchar *output,ushort *length)

{
  uint uVar1;
  uint uVar2;
  
  if ((camry_host_addr((output))!= 0) && (camry_host_addr((length))!= 0)) {
    uVar2 = (uint)*length;
    if (DAT_febe81ad != 0) {
      if (DAT_febe81ad == 1) {
        uVar1 = serialize_latched_event_identifiers_be16_557c4(camry_host_addr(output), uVar2);
      }
      else if (DAT_febe81ad < 3) {
        uVar1 = dispatch_capture_record_number_serialization_5592c(DAT_febe81ba, camry_host_addr(output), uVar2);
      }
      else {
        if (DAT_febe81ad != 3) {
          return 10;
        }
        uVar1 = dispatch_capture_field_serialization_55c6e(DAT_febe81ba, DAT_febe81bc, camry_host_addr(output), uVar2);
      }
      if ((-1 < (int)uVar1) &&
         ((int)(uVar1 - uVar2) < 0 != ((int)uVar1 < 0 && -1 < (int)(uVar1 - uVar2)) ||
          uVar1 == uVar2)) {
        *length = (ushort)uVar1;
        return 0;
      }
      if (uVar1 == 0xfffffffc) {
        return 4;
      }
      if (uVar1 == 0xffffffff) {
        return 6;
      }
    }
  }
  return 10;
}

F33DidPublicationMetadata * get_did_publication_metadata(ushort *count)

{
  *count = 0xf2;
  return did_publication_metadata;
}

void return_only_stub_509a0(void)

{
  return;
}

void return_only_stub_509a2(void)

{
  return;
}

void refresh_diagnostic_application_availability(void)

{
  char cVar1;
  uint32_t puVar2;
  undefined1 uVar3;
  undefined1 uVar4;
  
  cVar1 = DAT_febe81cd;
  puVar2 = 0xfebeb800u;
  if (((DAT_febee826 == '3') || (DAT_febee826 == '\x11')) || (DAT_febe7bba == 'Z')) {
    uVar3 = 0;
  }
  else {
    uVar3 = 0x5a;
    uVar4 = 0x5a;
    if (DAT_febe7f97 != 'Z') {
      puVar2 = 0xfebeb800u;
      set_crypto_mode_byte_6a174(0x5a);
      uVar3 = uVar4;
      if (((int8_t)cVar1) == -0x5b) {
        reset_event28_profile_report_latch_5704e();
      }
      goto LAB_000509f6;
    }
  }
  set_crypto_mode_byte_6a174(0xa5);
  uVar4 = 0xa5;
LAB_000509f6:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x3633))))) = uVar4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x3634))))) = uVar3;
  return;
}

void return_only_stub_50a02(void)

{
  return;
}

void return_only_stub_50a04(void)

{
  return;
}

void snapshot_acquisition_status_flags(void)

{
  DAT_febe81d0 = DAT_febe5f26;
  DAT_febe81d1 = DAT_febe5f27;
  return;
}

void return_only_stub_50a18(void)

{
  return;
}

void return_only_stub_50a1a(void)

{
  return;
}

void snapshot_acquisition_range_fields(void)

{
  DAT_febe81d6 = DAT_febe5eea;
  DAT_febe81d8 = DAT_febe5eec;
  DAT_febe81d4 = DAT_febe5f26 ^ 0x5a;
  DAT_febe81da = DAT_febe5eee;
  DAT_febe81dc = DAT_febe5ef0;
  DAT_febe81d5 = DAT_febe5f27 ^ 0x5a;
  return;
}

void return_only_stub_50a4e(void)

{
  return;
}

void return_only_stub_50a50(void)

{
  return;
}

void decode_febe5f08_masks_and_copy_three_words_50a52(void)

{
  DAT_febe81e0 = 0;
  if ((DAT_febe5f08 & 0x84) != 0) {
    DAT_febe81e0 = 0x5a;
  }
  DAT_febe81e1 = 0;
  if ((DAT_febe5f08 & 0x78) != 0) {
    DAT_febe81e1 = 0x5a;
  }
  DAT_febe81e2 = 0;
  if ((DAT_febe5f08 >> 1 & 1) != 0) {
    DAT_febe81e2 = 0x5a;
  }
  DAT_febe81e6 = DAT_febe5f02;
  DAT_febe81e8 = DAT_febe5f04;
  DAT_febe81ee = DAT_febe5f06;
  return;
}

void decode_febe5f10_masks_and_copy_three_words_50a9a(void)

{
  DAT_febe81e3 = 0;
  if ((DAT_febe5f10 & 0x84) != 0) {
    DAT_febe81e3 = 0x5a;
  }
  DAT_febe81e4 = 0;
  if ((DAT_febe5f10 & 0x78) != 0) {
    DAT_febe81e4 = 0x5a;
  }
  DAT_febe81e5 = 0;
  if ((DAT_febe5f10 >> 1 & 1) != 0) {
    DAT_febe81e5 = 0x5a;
  }
  DAT_febe81ea = DAT_febe5f0a;
  DAT_febe81ec = DAT_febe5f0c;
  DAT_febe81f0 = DAT_febe5f0e;
  return;
}

void refresh_two_three_word_snapshots_when_8a1c_z_50ae2(void)

{
  if (DAT_febe8a1c == 'Z') {
    decode_febe5f08_masks_and_copy_three_words_50a52();
    decode_febe5f10_masks_and_copy_three_words_50a9a();
  }
  return;
}

void return_only_stub_50afc(void)

{
  return;
}

void return_only_stub_50afe(void)

{
  return;
}

void fill_constant_block_50b00(void)

{
  DAT_febe81f8 = 0x8000;
  DAT_febe81fa = 0x8000;
  DAT_febe81fc = 0x8000;
  DAT_febe81fe = 0x8000;
  DAT_febe81f4 = 0x8000;
  DAT_febe8200 = 0x8000;
  DAT_febe8202 = 0x8000;
  DAT_febe8204 = 0x8000;
  DAT_febe8206 = 0x8000;
  DAT_febe81f6 = 0x8000;
  DAT_febe8208 = 0x8000;
  DAT_febe820a = 0x8000;
  return;
}

void return_only_stub_50b22(void)

{
  return;
}

void return_only_stub_50b24(void)

{
  return;
}

void copy_cell_block_50b26(void)

{
  DAT_febe821e = DAT_febe5efe;
  DAT_febe8220 = DAT_febe5ee6;
  DAT_febe8226 = DAT_febe5ee6;
  DAT_febe8212 = DAT_febe5ee6;
  DAT_febe8224 = DAT_febe5f00;
  DAT_febe8214 = DAT_febe5ee6;
  DAT_febe8216 = DAT_febe5ee6;
  DAT_febe8210 = DAT_febe5ee0;
  DAT_febe820c = DAT_febe5ee2;
  DAT_febe820e = DAT_febe5ee4;
  DAT_febe8222 = DAT_febe5ee8;
  DAT_febe8228 = DAT_febe5ee8;
  DAT_febe8218 = DAT_febe5ee8;
  DAT_febe821a = DAT_febe5ee8;
  DAT_febe821c = DAT_febe5ee8;
  return;
}

void return_only_stub_50b66(void)

{
  return;
}

void return_only_stub_50b68(void)

{
  return;
}

void copy_acquisition_banks_to_application(void)

{
  DAT_febe8238 = ((volatile uint16_t *)camry_host_ptr(0xfebe5ec8u))[0];
  DAT_febe823a = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe5ec8u + (uint32_t)(1) * 2u))));
  DAT_febe823c = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe5ec8u + (uint32_t)(2) * 2u))));
  DAT_febe822c = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe5ec8u + (uint32_t)(6) * 2u))));
  DAT_febe822e = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe5ec8u + (uint32_t)(7) * 2u))));
  DAT_febe8230 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe5ec8u + (uint32_t)(8) * 2u))));
  DAT_febe823e = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe5ec8u + (uint32_t)(3) * 2u))));
  DAT_febe8240 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe5ec8u + (uint32_t)(4) * 2u))));
  DAT_febe8242 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe5ec8u + (uint32_t)(5) * 2u))));
  DAT_febe8232 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe5ec8u + (uint32_t)(9) * 2u))));
  DAT_febe8234 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe5ec8u + (uint32_t)(10) * 2u))));
  DAT_febe8236 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe5ec8u + (uint32_t)(0xb) * 2u))));
  return;
}

void return_only_stub_50bb8(void)

{
  return;
}

void return_only_stub_50bba(void)

{
  return;
}

void copy_serial_acquisition_to_application(void)

{
  DAT_febe824c = DAT_febe5f12 << 2;
  DAT_febe824e = DAT_febe5f14 << 2;
  DAT_febe8254 = DAT_febe5f16;
  DAT_febe8244 = ((volatile uint8_t *)camry_host_ptr(0xfebe5f29u))[0];
  DAT_febe8246 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5f29u + (uint32_t)(1) * 1u))));
  DAT_febe8248 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5f29u + (uint32_t)(2) * 1u))));
  DAT_febe824a = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5f29u + (uint32_t)(3) * 1u))));
  DAT_febe8258 = DAT_febe5f18;
  DAT_febe825a = DAT_febe5f1a;
  DAT_febe8250 = DAT_febe5f1c << 2;
  DAT_febe8252 = DAT_febe5f1e << 2;
  DAT_febe8256 = DAT_febe5f20;
  DAT_febe8245 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5f29u + (uint32_t)(4) * 1u))));
  DAT_febe8247 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5f29u + (uint32_t)(5) * 1u))));
  DAT_febe8249 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5f29u + (uint32_t)(6) * 1u))));
  DAT_febe824b = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5f29u + (uint32_t)(7) * 1u))));
  DAT_febe825c = DAT_febe5f22;
  DAT_febe825e = DAT_febe5f24;
  return;
}

void return_only_stub_50c36(void)

{
  return;
}

void clear_five_status_mask_words_50c38(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe8260u + (uint32_t)(iVar3 * 4) * 1u)))) = 0;
    iVar1 = iVar3 + -4;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  return;
}

void store_low_bit_to_febe3889_50c4e(byte param_1)

{
  DAT_febe3889 = param_1 & 1;
  return;
}

void merge_five_status_masks_and_publish_low_bit_50c58(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint32_t puVar4;
  uint uVar5;
  
  puVar4 = 0xfebeb800u;
  uVar5 = 0;
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    uVar5 = uVar5 | *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe8260u + (uint32_t)(iVar3 * 4) * 1u))));
    iVar1 = iVar3 + -4;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  store_low_bit_to_febe3889_50c4e(uVar5);
  (*((uint *)camry_host_ptr((uint32_t)(puVar4 + -0x358c)))) = uVar5;
  return;
}

void set_indexed_status_mask_word_if_below_five_50c82(uint param_1,undefined4 param_2)

{
  if ((param_1 & 0xff) < 5) {
    *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe8260u + (uint32_t)((param_1 & 0xff) * 4) * 1u)))) = param_2;
  }
  return;
}

void return_only_stub_50c96(void)

{
  return;
}

void return_only_stub_50c98(void)

{
  return;
}

undefined4 snapshot_local_status_link_flags(void)

{
  ushort uVar1;
  ushort uVar2;
  char cVar3;
  uint32_t puVar4;
  undefined4 uVar5;
  uint uVar6;
  uint uVar7;
  uint uVar8;
  uint uVar9;
  uint uVar10;
  uint uVar11;
  uint uVar12;
  uint uVar13;
  uint uVar14;
  uint uVar15;
  uint uVar16;
  uint uVar17;
  uint uVar18;
  uint uVar19;
  uint uVar20;
  uint uVar21;
  uint uVar22;
  uint uVar23;
  uint uVar24;
  uint uVar25;
  uint uVar26;
  uint uVar27;
  uint uVar28;
  uint uVar29;
  uint uVar30;
  uint uVar31;
  uint uVar32;
  
  puVar4 = 0xfebeb800u;
  uVar5 = compose_serial_and_monitor_failure_bitmap_62cd4();
  uVar1 = (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + -0x7fc8))));
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar4 + -0x356c)))) = uVar5;
  cVar3 = '\0';
  if ((uVar1 >> 6 & 1) != 0) {
    cVar3 = 'Z';
  }
  uVar32 = 0;
  if (cVar3 != '\0') {
    uVar32 = 0x20;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3588))))) = cVar3;
  cVar3 = '\0';
  if ((uVar1 >> 4 & 1) != 0) {
    cVar3 = 'Z';
  }
  uVar20 = 0;
  if (cVar3 != '\0') {
    uVar20 = 0x40000000;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3587))))) = cVar3;
  cVar3 = '\0';
  if ((uVar1 >> 2 & 1) != 0) {
    cVar3 = 'Z';
  }
  uVar21 = 0;
  if (cVar3 != '\0') {
    uVar21 = 0x10000000;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3586))))) = cVar3;
  cVar3 = '\0';
  if ((uVar1 >> 5 & 1) != 0) {
    cVar3 = 'Z';
  }
  uVar22 = 0;
  if (cVar3 != '\0') {
    uVar22 = 0x80000000;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3585))))) = cVar3;
  cVar3 = '\0';
  if ((uVar1 >> 3 & 1) != 0) {
    cVar3 = 'Z';
  }
  uVar23 = 0;
  if (cVar3 != '\0') {
    uVar23 = 0x20000000;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3584))))) = cVar3;
  uVar2 = (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + -0x7fc6))));
  cVar3 = '\0';
  if ((uVar2 >> 0xc & 1) != 0) {
    cVar3 = 'Z';
  }
  uVar6 = 0;
  if (cVar3 != '\0') {
    uVar6 = 0x4000000;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3583))))) = cVar3;
  cVar3 = '\0';
  if ((uVar2 >> 0xd & 1) != 0) {
    cVar3 = 'Z';
  }
  uVar7 = 0;
  if (cVar3 != '\0') {
    uVar7 = 0x8000000;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3582))))) = cVar3;
  cVar3 = '\0';
  if ((uVar1 & 1) != 0) {
    cVar3 = 'Z';
  }
  uVar8 = 0;
  if (cVar3 != '\0') {
    uVar8 = 0x1000000;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3581))))) = cVar3;
  cVar3 = '\0';
  if ((uVar1 >> 1 & 1) != 0) {
    cVar3 = 'Z';
  }
  uVar24 = 0;
  if (cVar3 != '\0') {
    uVar24 = 0x2000000;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3580))))) = cVar3;
  cVar3 = '\0';
  if ((uVar2 >> 8 & 1) != 0) {
    cVar3 = 'Z';
  }
  uVar25 = 0;
  if (cVar3 != '\0') {
    uVar25 = 0x400000;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x357f))))) = cVar3;
  cVar3 = '\0';
  if ((uVar2 >> 9 & 1) != 0) {
    cVar3 = 'Z';
  }
  uVar26 = 0;
  if (cVar3 != '\0') {
    uVar26 = 0x800000;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x357e))))) = cVar3;
  cVar3 = '\0';
  if ((uVar2 >> 2 & 1) != 0) {
    cVar3 = 'Z';
  }
  uVar27 = 0;
  if (cVar3 != '\0') {
    uVar27 = 0x100000;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x357d))))) = cVar3;
  cVar3 = '\0';
  if ((uVar2 >> 3 & 1) != 0) {
    cVar3 = 'Z';
  }
  uVar28 = 0;
  if (cVar3 != '\0') {
    uVar28 = 0x200000;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x357c))))) = cVar3;
  uVar1 = (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + -0x7fc4))));
  cVar3 = '\0';
  if ((uVar1 >> 0xb & 1) != 0) {
    cVar3 = 'Z';
  }
  uVar9 = 0;
  if (cVar3 != '\0') {
    uVar9 = 0x80000;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x357b))))) = cVar3;
  cVar3 = '\0';
  if ((uVar1 >> 10 & 1) != 0) {
    cVar3 = 'Z';
  }
  uVar10 = 0;
  if (cVar3 != '\0') {
    uVar10 = 0x40000;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x357a))))) = cVar3;
  cVar3 = '\0';
  if ((uVar1 >> 9 & 1) != 0) {
    cVar3 = 'Z';
  }
  uVar11 = 0;
  if (cVar3 != '\0') {
    uVar11 = 0x20000;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3579))))) = cVar3;
  cVar3 = '\0';
  if ((uVar1 >> 8 & 1) != 0) {
    cVar3 = 'Z';
  }
  uVar12 = 0;
  if (cVar3 != '\0') {
    uVar12 = 0x10000;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3578))))) = cVar3;
  cVar3 = '\0';
  if ((uVar1 >> 7 & 1) != 0) {
    cVar3 = 'Z';
  }
  uVar13 = 0;
  if (cVar3 != '\0') {
    uVar13 = 0x8000;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3577))))) = cVar3;
  cVar3 = '\0';
  if ((uVar1 >> 6 & 1) != 0) {
    cVar3 = 'Z';
  }
  uVar14 = 0;
  if (cVar3 != '\0') {
    uVar14 = 0x4000;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3576))))) = cVar3;
  cVar3 = '\0';
  if ((uVar1 >> 5 & 1) != 0) {
    cVar3 = 'Z';
  }
  uVar15 = 0;
  if (cVar3 != '\0') {
    uVar15 = 0x2000;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3575))))) = cVar3;
  cVar3 = '\0';
  if ((uVar1 >> 4 & 1) != 0) {
    cVar3 = 'Z';
  }
  uVar16 = 0;
  if (cVar3 != '\0') {
    uVar16 = 0x1000;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3574))))) = cVar3;
  cVar3 = '\0';
  if ((uVar1 >> 3 & 1) != 0) {
    cVar3 = 'Z';
  }
  uVar17 = 0;
  if (cVar3 != '\0') {
    uVar17 = 0x800;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3573))))) = cVar3;
  cVar3 = '\0';
  if ((uVar1 >> 2 & 1) != 0) {
    cVar3 = 'Z';
  }
  uVar18 = 0;
  if (cVar3 != '\0') {
    uVar18 = 0x400;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3572))))) = cVar3;
  cVar3 = '\0';
  if ((uVar1 >> 1 & 1) != 0) {
    cVar3 = 'Z';
  }
  uVar19 = 0;
  if (cVar3 != '\0') {
    uVar19 = 0x200;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3571))))) = cVar3;
  cVar3 = '\0';
  if ((uVar1 & 1) != 0) {
    cVar3 = 'Z';
  }
  uVar29 = 0;
  if (cVar3 != '\0') {
    uVar29 = 0x100;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3570))))) = cVar3;
  cVar3 = '\0';
  if ((uVar2 >> 5 & 1) != 0) {
    cVar3 = 'Z';
  }
  uVar30 = 0;
  if (cVar3 != '\0') {
    uVar30 = 0x80;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x356f))))) = cVar3;
  cVar3 = '\0';
  if ((uVar2 >> 4 & 1) != 0) {
    cVar3 = 'Z';
  }
  uVar31 = 0;
  if (cVar3 != '\0') {
    uVar31 = 0x40;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x356e))))) = cVar3;
  DAT_febe829c = 0;
  DAT_febe8298 = uVar32 | uVar20 | uVar21 | uVar22 | uVar23 | uVar6 | uVar7 | uVar8 | uVar24 |
                 uVar25 | uVar26 | uVar27 | uVar28 | uVar9 | uVar10 | uVar11 | uVar12 | uVar13 |
                 uVar14 | uVar15 | uVar16 | uVar17 | uVar18 | uVar19 | uVar29 | uVar30 | uVar31;
  return uVar5;
}

void return_only_stub_50fac(void)

{
  return;
}

void copy_three_classifier_age_thresholds_50fae(void)

{
  DAT_febe82ca = classifier_primary_age_threshold;
  DAT_febe82cc = classifier_secondary_age_threshold;
  DAT_febe82ce = classifier_retained_age_threshold;
  return;
}
