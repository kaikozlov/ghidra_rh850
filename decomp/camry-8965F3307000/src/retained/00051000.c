#include "common.h"

uint release_diagnostic_classifier(uchar classification)

{
  uint32_t puVar1;
  uint saved_mask;
  
  puVar1 = 0xfebeb800u;
  saved_mask = priority_mask_enter(0xff00);
  if (classification == '\x02') {
    if ((*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x3546)))) != 0) {
      (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x3546)))) = (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x3546)))) + -1;
    }
  }
  else if (classification == '\x04') {
    if ((*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x3544)))) != 0) {
      (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x3544)))) = (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x3544)))) + -1;
    }
  }
  else if (classification == '\b') {
    if ((*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x3542)))) != 0) {
      (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x3542)))) = (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x3542)))) + -1;
    }
  }
  else if (classification == '\x0f') {
    if ((*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x3540)))) != 0) {
      (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x3540)))) = (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x3540)))) + -1;
    }
  }
  else if (classification == '\x10') {
    if ((*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x353e)))) != 0) {
      (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x353e)))) = (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x353e)))) + -1;
    }
  }
  else if (classification == ' ') {
    if ((*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x353c)))) != 0) {
      (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x353c)))) = (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x353c)))) + -1;
    }
  }
  else if (classification == '@') {
    if ((*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x353a)))) != 0) {
      (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x353a)))) = (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x353a)))) + -1;
    }
  }
  else if (classification == 0x80) {
    if ((*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x3538)))) != 0) {
      (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x3538)))) = (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x3538)))) + -1;
    }
  }
  else if ((classification == 0xf0) && ((*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x3530)))) != 0)) {
    (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x3530)))) = (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x3530)))) + -1;
  }
  priority_mask_restore(saved_mask);
  return saved_mask;
}

void reset_classifier_counts_and_flags(void)

{
  DAT_febe82ba = 0;
  DAT_febe82bc = 0;
  DAT_febe82c0 = 0;
  DAT_febe82be = 0;
  DAT_febe82c2 = 0;
  DAT_febe82c4 = 0;
  DAT_febe82d0 = 0;
  DAT_febe82c6 = 0;
  DAT_febe82c8 = 0;
  DAT_febe82ca = classifier_primary_age_threshold;
  DAT_febe82cc = classifier_secondary_age_threshold;
  DAT_febe82a3 = 0;
  DAT_febe82a4 = 0;
  DAT_febe82ce = classifier_retained_age_threshold;
  DAT_febe82a5 = 0;
  return;
}

void set_byte_febe82a9_to_z_515ca(void)

{
  DAT_febe82a9 = 0x5a;
  return;
}

void set_two_classifier_flags_and_clear_two_counts_515d4(void)

{
  DAT_febe82a2 = 0x5a;
  DAT_febe82a1 = 0x5a;
  DAT_febe82b8 = 0;
  DAT_febe82b6 = 0;
  return;
}

uint reset_classifier_counts_and_rearm_status_flags_515e6(void)

{
  uint32_t puVar1;
  uint saved_mask;
  
  puVar1 = 0xfebeb800u;
  saved_mask = priority_mask_enter(0xff00);
  reset_classifier_counts_and_flags();
  set_two_classifier_flags_and_clear_two_counts_515d4();
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3557))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3550))))) = 0x5a;
  priority_mask_restore(saved_mask);
  return saved_mask;
}

void return_only_stub_51610(void)

{
  return;
}

void reset_four_slot_diagnostic_operation_queue_51612(void)

{
  uint uVar1;
  
  uVar1 = 0;
  DAT_febe82d5 = 0;
  DAT_febe82d4 = 0;
  do {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe82d8u + (uint32_t)(uVar1) * 1u)))) = 0;
    uVar1 = uVar1 + 1;
  } while (uVar1 < 4);
  DAT_febe82d6 = 0;
  DAT_febe82d7 = 0;
  return;
}

void repair_diagnostic_queue_consumer(void)

{
  uint uVar1;
  int iVar2;
  byte bVar3;
  
  if (3 < DAT_febe82d7) {
    uVar1 = (uint)DAT_febe82d6;
    iVar2 = 0;
    bVar3 = 0;
    do {
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe82d8u + (uint32_t)(uVar1) * 1u)))) == '\0') {
        uVar1 = uVar1 + 1 & 0xff;
        if (3 < uVar1) {
          uVar1 = 0;
        }
      }
      else {
        iVar2 = 0x5a;
      }
      bVar3 = bVar3 + 1;
    } while ((bVar3 < 4) && (iVar2 != 0x5a));
    DAT_febe82d7 = (byte)uVar1;
  }
  return;
}

void snapshot_preserved_current_events(ushort *events)

{
  int iVar1;
  int iVar2;
  ushort uVar3;
  uint uVar4;
  int iVar5;
  
  iVar5 = 0;
  do {
    uVar3 = *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x2fc44u + (uint32_t)(iVar5 * 2) * 1u))));
    uVar4 = get_diagnostic_event_state((uint)uVar3);
    if ((uVar4 & 1) == 0) {
      uVar3 = 0;
    }
    events[iVar5] = uVar3;
    iVar2 = iVar5 + 1;
    iVar1 = iVar5 + -5;
    iVar5 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  return;
}

void restore_preserved_current_events(ushort *events)

{
  int iVar1;
  int iVar2;
  ushort uVar3;
  int iVar4;
  
  iVar4 = 0;
  do {
    uVar3 = events[iVar4];
    set_event_bit_in_three_bitmaps_525e0((uint)uVar3);
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2fc51u + (uint32_t)((uint)uVar3 * 8) * 1u)))) != '\0') {
      assert_diagnostic_classifier((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2fc51u + (uint32_t)((uint)uVar3 * 8) * 1u)))));
    }
    iVar2 = iVar4 + 1;
    iVar1 = iVar4 + -5;
    iVar4 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  return;
}

void clear_diagnostic_ram_generation(void)

{
  ushort auStack_10 [6];
  
  if (DAT_febee856 == '\x11') {
    snapshot_preserved_current_events(auStack_10);
    clear_current_and_first_event_history();
    mark_capture_slots_for_clear();
    reset_classifier_counts_and_flags();
    restore_preserved_current_events(auStack_10);
  }
  else {
    clear_current_and_first_event_history();
    mark_capture_slots_for_clear();
    reset_classifier_counts_and_flags();
  }
  return;
}

uint request_diagnostic_clear(void)

{
  uint uVar1;
  uint32_t puVar2;
  int iVar3;
  
  puVar2 = 0xfebeb800u;
  if (DAT_febe82d4 == '\0') {
    DAT_febe82d4 = '\x01';
    clear_diagnostic_ram_generation();
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x352c))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x352c))))) | 0x80;
  }
  else if (((int8_t)DAT_febe82d4) != -0x7f) {
    iVar3 = 0;
    uVar1 = 0;
    do {
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe82d8u + (uint32_t)(uVar1) * 1u)))) == '\x01') {
        iVar3 = 0x5a;
      }
      uVar1 = uVar1 + 1 & 0xff;
    } while ((uVar1 < 4) && (iVar3 != 0x5a));
    if (iVar3 == 0) {
      uVar1 = (uint)DAT_febe82d6;
      if (3 < uVar1) {
        uVar1 = 0;
      }
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe82d8u + (uint32_t)(uVar1) * 1u)))) = 1;
      if (uVar1 < 3) {
        DAT_febe82d6 = (char)uVar1 + 1;
      }
      else {
        DAT_febe82d6 = 0;
      }
    }
  }
  return 0;
}

void clear_diagnostic_histories_with_mode_conditional_event_preservation_51788(void)

{
  char cVar1;
  ushort auStack_14 [6];
  
  cVar1 = DAT_febee856;
  thunk_prepare_d113c_and_write_record9_configuration_bdb48();
  clear_twelve_counters_three_records_and_nvm14_54a24();
  clear_6f00_6f02_6f06_6f08_halfwords_3990c();
  clear_and_persist_record_twelve_samples_45e12();
  thunk_clear_paired_snapshot_fields_and_write_zero_record15_bdf24();
  thunk_clear_be28_be2a_and_write_zero_record11_bdcfe();
  initialize_capture_storage_from_2222_markers_55658();
  if (cVar1 == '\x11') {
    snapshot_preserved_current_events(auStack_14);
    clear_second_event_history();
    selectively_reset_marked_capture_slots_and_mark_dirty_52f32();
    clear_counter_and_value_arrays_and_mark_forced_write_546a2();
    restore_preserved_current_events(auStack_14);
  }
  else {
    clear_second_event_history();
    selectively_reset_marked_capture_slots_and_mark_dirty_52f32();
    clear_counter_and_value_arrays_and_mark_forced_write_546a2();
  }
  return;
}

undefined4 start_or_enqueue_diagnostic_clear_operation2_517dc(void)

{
  uint uVar1;
  uint32_t puVar2;
  int iVar3;
  
  puVar2 = 0xfebeb800u;
  if (DAT_febe82d4 == '\0') {
    DAT_febe82d4 = '\x02';
    clear_diagnostic_histories_with_mode_conditional_event_preservation_51788();
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x352c))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x352c))))) | 0x80;
  }
  else if ((((int8_t)DAT_febe82d4) != -0x7e) && (((int8_t)DAT_febe82d4) != -0x7a)) {
    iVar3 = 0;
    uVar1 = 0;
    do {
      if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe82d8u + (uint32_t)(uVar1) * 1u)))) == '\x02') || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe82d8u + (uint32_t)(uVar1) * 1u)))) == '\x06')) {
        iVar3 = 0x5a;
      }
      uVar1 = uVar1 + 1 & 0xff;
    } while ((uVar1 < 4) && (iVar3 != 0x5a));
    if (iVar3 == 0) {
      if (3 < DAT_febe82d6) {
        DAT_febe82d6 = 0;
      }
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe82d8u + (uint32_t)(DAT_febe82d6) * 1u)))) = 2;
      if (DAT_febe82d6 < 3) {
        DAT_febe82d6 = DAT_febe82d6 + 1;
      }
      else {
        DAT_febe82d6 = 0;
      }
    }
  }
  return 0;
}

undefined4 start_or_enqueue_diagnostic_ram_clear_operation4_51866(void)

{
  uint uVar1;
  uint32_t puVar2;
  puVar2 = 0xfebeb800u;
  if (DAT_febe82d4 == '\0') {
    DAT_febe82d4 = '\x04';
    clear_diagnostic_ram_generation();
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x352c))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x352c))))) | 0x80;
  }
  else if (((int8_t)DAT_febe82d4) != -0x7c) {
    uVar1 = 0;
    do {
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe82d8u + (uint32_t)(uVar1) * 1u)))) == '\x04') break;
      uVar1 = uVar1 + 1;
    } while (uVar1 < 4);
    if (uVar1 == 4) {
      if (3 < DAT_febe82d6) {
        DAT_febe82d6 = 0;
      }
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe82d8u + (uint32_t)(DAT_febe82d6) * 1u)))) = 4;
      if (DAT_febe82d6 < 3) {
        DAT_febe82d6 = DAT_febe82d6 + 1;
      }
      else {
        DAT_febe82d6 = 0;
      }
    }
  }
  return 0;
}

void thunk_initialize_capture_storage_from_4444_markers_5551a(void)

{
  initialize_capture_storage_from_4444_markers_5551a();
  return;
}

undefined4 start_or_enqueue_diagnostic_operation5_518e0(void)

{
  uint uVar1;
  uint32_t puVar2;
  int iVar3;
  
  puVar2 = 0xfebeb800u;
  if (DAT_febe82d4 == '\0') {
    DAT_febe82d4 = '\x05';
    thunk_initialize_capture_storage_from_4444_markers_5551a();
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x352c))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x352c))))) | 0x80;
  }
  else if ((((int8_t)DAT_febe82d4) != -0x7b) && (((int8_t)DAT_febe82d4) != -0x7a)) {
    iVar3 = 0;
    uVar1 = 0;
    do {
      if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe82d8u + (uint32_t)(uVar1) * 1u)))) == '\x05') || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe82d8u + (uint32_t)(uVar1) * 1u)))) == '\x06')) {
        iVar3 = 0x5a;
      }
      uVar1 = uVar1 + 1 & 0xff;
    } while ((uVar1 < 4) && (iVar3 != 0x5a));
    if (iVar3 == 0) {
      uVar1 = (uint)DAT_febe82d6;
      if (3 < uVar1) {
        uVar1 = 0;
      }
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe82d8u + (uint32_t)(uVar1) * 1u)))) = 5;
      if (uVar1 < 3) {
        DAT_febe82d6 = (char)uVar1 + 1;
      }
      else {
        DAT_febe82d6 = 0;
      }
    }
  }
  return 0;
}

void clear_diagnostic_histories_preserving_current_events_51962(void)

{
  ushort auStack_10 [6];
  
  thunk_prepare_d113c_and_write_record9_configuration_bdb48();
  clear_twelve_counters_three_records_and_nvm14_54a24();
  clear_6f00_6f02_6f06_6f08_halfwords_3990c();
  clear_and_persist_record_twelve_samples_45e12();
  thunk_clear_paired_snapshot_fields_and_write_zero_record15_bdf24();
  thunk_clear_be28_be2a_and_write_zero_record11_bdcfe();
  reset_all_enabled_capture_storage_5575e();
  snapshot_preserved_current_events(auStack_10);
  clear_second_event_history();
  reset_first_third_captures_and_selectively_reset_second_53092();
  clear_counter_and_value_arrays_and_mark_forced_write_546a2();
  restore_preserved_current_events(auStack_10);
  return;
}

undefined4 start_or_enqueue_diagnostic_clear_operation6_5199e(void)

{
  uint uVar1;
  uint32_t puVar2;
  int iVar3;
  
  puVar2 = 0xfebeb800u;
  if (DAT_febe82d4 == '\0') {
    DAT_febe82d4 = '\x06';
    clear_diagnostic_histories_preserving_current_events_51962();
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x352c))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x352c))))) | 0x80;
  }
  else if (((int8_t)DAT_febe82d4) != -0x7a) {
    iVar3 = 0;
    uVar1 = 0;
    do {
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe82d8u + (uint32_t)(uVar1) * 1u)))) == '\x06') {
        iVar3 = 0x5a;
      }
      uVar1 = uVar1 + 1 & 0xff;
    } while ((uVar1 < 4) && (iVar3 != 0x5a));
    if (iVar3 == 0) {
      uVar1 = (uint)DAT_febe82d6;
      if (3 < uVar1) {
        uVar1 = 0;
      }
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe82d8u + (uint32_t)(uVar1) * 1u)))) = 6;
      if (uVar1 < 3) {
        DAT_febe82d6 = (char)uVar1 + 1;
      }
      else {
        DAT_febe82d6 = 0;
      }
    }
  }
  return 0;
}

void dispatch_next_diagnostic_request(void)

{
  char cVar1;
  int iVar2;
  undefined8 uVar3;
  int iVar4;
  byte bVar5;
  uint uVar6;
  
  uVar3 = 0xfebeb800;
  repair_diagnostic_queue_consumer();
  uVar6 = (uint)DAT_febe82d7;
  DAT_febe82d4 = 0;
  bVar5 = 0;
  while( true ) {
    iVar2 = (int)uVar3;
    cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe82d8u + (uint32_t)(uVar6) * 1u))));
    if (cVar1 == '\0') break;
    bVar5 = bVar5 + 1;
    iVar4 = 0x5a;
    if (cVar1 == '\x01') {
      request_diagnostic_clear();
    }
    else if (cVar1 == '\x02') {
      start_or_enqueue_diagnostic_clear_operation2_517dc();
    }
    else if (cVar1 == '\x04') {
      start_or_enqueue_diagnostic_ram_clear_operation4_51866();
    }
    else if (cVar1 == '\x05') {
      start_or_enqueue_diagnostic_operation5_518e0();
    }
    else if (cVar1 == '\x06') {
      start_or_enqueue_diagnostic_clear_operation6_5199e();
    }
    else {
      iVar4 = 0;
    }
    iVar2 = (int)uVar3;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe82d8u + (uint32_t)(uVar6) * 1u)))) = 0;
    if (uVar6 < 3) {
      uVar6 = uVar6 + 1 & 0xff;
    }
    else {
      uVar6 = 0;
    }
    if ((iVar4 != 0) || (3 < bVar5)) goto LAB_00051a90;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe82d8u + (uint32_t)(uVar6) * 1u)))) = 0;
LAB_00051a90:
  (*((char *)camry_host_ptr((uint32_t)(iVar2 + -0x3529)))) = (char)uVar6;
  return;
}

void complete_diagnostic_request_and_dispatch(void)

{
  undefined4 uVar1;
  undefined1 uVar2;
  
  if (DAT_febe82d4 == '\0') {
    return;
  }
  if (((int8_t)DAT_febe5f85) == -0x56) {
    return;
  }
  if (((int8_t)DAT_febe5f85) == -0x5b) {
    return;
  }
  if (((int8_t)DAT_febe6150) == -0x56) {
    return;
  }
  if (((int8_t)DAT_febe6150) == -0x5b) {
    return;
  }
  if (((int8_t)DAT_febe8608) == -0x56) {
    return;
  }
  if (((int8_t)DAT_febe8608) == -0x5b) {
    return;
  }
  if (((int8_t)DAT_febe89c4) == -0x56) {
    return;
  }
  if (((int8_t)DAT_febe89c4) == -0x5b) {
    return;
  }
  if (((int8_t)DAT_febe82d4) == -0x7f) {
    if ((DAT_febe5f85 != '\0') || (DAT_febe6150 != '\0')) {
      uVar1 = 0x11;
      goto LAB_00051b54;
    }
    uVar1 = 0x11;
    uVar2 = 0;
  }
  else {
    if (((int8_t)DAT_febe82d4) == -0x7a) {
      if (((DAT_febe5f85 == '\0') && (DAT_febe6150 == '\0')) &&
         ((DAT_febe8608 == '\0' && (DAT_febe89c4 == '\0')))) {
        uVar2 = 0;
      }
      else {
        uVar2 = 0x20;
      }
      publish_result_to_active_routines3_and10_4d0e8(uVar2);
      goto LAB_00051b5c;
    }
    if (((int8_t)DAT_febe82d4) == -0x7e) {
      if ((((DAT_febe5f85 == '\0') && (DAT_febe6150 == '\0')) && (DAT_febe8608 == '\0')) &&
         (DAT_febe89c4 == '\0')) {
        uVar1 = 10;
        uVar2 = 0;
      }
      else {
        uVar1 = 10;
LAB_00051b54:
        uVar2 = 0x20;
      }
    }
    else {
      if (((int8_t)DAT_febe82d4) != -0x7b) goto LAB_00051b5c;
      uVar1 = 3;
      if (DAT_febe89c4 != '\0') goto LAB_00051b54;
      uVar2 = 0;
    }
  }
  publish_routine_or_pending_write_terminal_result_4d0a4(uVar1,uVar2);
LAB_00051b5c:
  dispatch_next_diagnostic_request();
  return;
}

void dispatch_four_callbacks_for_e856_and_e85b_modes_51b64(void)

{
  uint32_t puVar1;
  uint uVar2;
  
  puVar1 = 0x23dfcu;
  if ((DAT_febee856 == '\x11') && ((DAT_febee85b == '\0' || (DAT_febee85b == '\"')))) {
    uVar2 = 0;
    do {
      if ((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar1 + uVar2 * 4 + -0x2ab0))))) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar1 + uVar2 * 4 + -0x2ab0))))))))))))();
      }
      uVar2 = uVar2 + 1;
    } while (uVar2 < 4);
  }
  return;
}

void service_diagnostic_request_lifecycle(void)

{
  if (DAT_febe82d4 != '\0') {
    complete_diagnostic_request_and_dispatch();
  }
  dispatch_four_callbacks_for_e856_and_e85b_modes_51b64();
  return;
}

void gate_diagnostic_event_capture(uint event,ushort capture_kind,uchar prior_qualification)

{
  byte bVar1;
  
  if (prior_qualification == 'Z') {
    bVar1 = 6;
  }
  else {
    bVar1 = 2;
  }
  if ((bVar1 & (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2fc50u + (uint32_t)((event & 0xffff) * 8) * 1u))))) != 0) {
    capture_diagnostic_event((ushort)event,capture_kind,prior_qualification == 'Z');
  }
  return;
}

void update_diagnostic_event_statistics(uint event,uchar prior_qualification)

{
  uint uVar1;
  undefined1 uVar2;
  
  if (prior_qualification == '\0') {
    switch((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2fc54u + (uint32_t)((event & 0xffff) * 8) * 1u))))) {
    case 0x81:
      uVar2 = 5;
      break;
    case 0x82:
      uVar2 = 6;
      break;
    default:
      goto switchD_00051c0a_caseD_83;
    case 0x86:
      uVar2 = 2;
      break;
    case 0x87:
      uVar2 = 3;
      break;
    case 0x88:
      uVar2 = 7;
      break;
    case 0x89:
      uVar2 = 8;
      break;
    case 0x8a:
      uVar2 = 9;
      break;
    case 0x8b:
      uVar2 = 0;
      break;
    case 0x8c:
      uVar2 = 1;
    }
    uVar1 = get_indexed_u16_value_or_zero_5470c(uVar2);
    if (uVar1 < 0xffff) {
      uVar1 = uVar1 + 1 & 0xffff;
    }
    set_indexed_u16_value_and_mark_record4_dirty_54632(uVar2,uVar1);
  }
switchD_00051c0a_caseD_83:
  return;
}

void gate_indexed_event_payload_during_diagnostic_clears_51cf6(byte param_1,undefined2 param_2)

{
  int iVar1;
  
  if ((((param_1 < 0x29) && (DAT_febe82d4 != '\x05')) && (DAT_febe82d4 != '\x02')) &&
     (((DAT_febe82d4 != '\x06' && (DAT_febee85a != '\0')) &&
      (iVar1 = test_event_capture_exempt_or_not_latched_5578c(param_1), iVar1 == 0x5a)))) {
    dispatch_event_capture_by_descriptor_class_55398(param_1,param_2);
  }
  return;
}

void route_event_failure_by_e85a_mode_51d38(uint param_1,undefined1 param_2,ushort param_3)

{
  if (DAT_febee85a == '\0') {
    report_diagnostic_event_failure(param_1 & 0xffff,param_3);
  }
  else {
    gate_indexed_event_payload_during_diagnostic_clears_51cf6(param_2, (uint)(ushort)param_3);
  }
  return;
}

void thunk_clear_eighteen_counters_and_mark_forced_record4_write_54662(void)

{
  clear_eighteen_counters_and_mark_forced_record4_write_54662();
  return;
}

undefined4 start_or_enqueue_counter_clear_operation3_51dbe(void)

{
  uint uVar1;
  uint32_t puVar2;
  puVar2 = 0xfebeb800u;
  if (DAT_febe82d4 == '\0') {
    DAT_febe82d4 = '\x03';
    thunk_clear_eighteen_counters_and_mark_forced_record4_write_54662();
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x352c))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x352c))))) | 0x80;
  }
  else if (((int8_t)DAT_febe82d4) != -0x7d) {
    uVar1 = 0;
    do {
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe82d8u + (uint32_t)(uVar1) * 1u)))) == '\x03') break;
      uVar1 = uVar1 + 1;
    } while (uVar1 < 4);
    if (uVar1 == 4) {
      if (3 < DAT_febe82d6) {
        DAT_febe82d6 = 0;
      }
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe82d8u + (uint32_t)(DAT_febe82d6) * 1u)))) = 3;
      if (DAT_febe82d6 < 3) {
        DAT_febe82d6 = DAT_febe82d6 + 1;
      }
      else {
        DAT_febe82d6 = 0;
      }
    }
  }
  return 0;
}

void return_only_stub_51e44(void)

{
  return;
}

void rebuild_event_descriptor_bitmap(void)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  
  uVar3 = 0;
  do {
    if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2fc52u + (uint32_t)(uVar3 * 8) * 1u)))) == '\0') || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2fc55u + (uint32_t)(uVar3 * 8) * 1u)))) == '\0')) {
      *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe6120u + (uint32_t)((uVar3 >> 5) * 4) * 1u)))) =
           *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe6120u + (uint32_t)((uVar3 >> 5) * 4) * 1u)))) | 1 << (uVar3 & 0x1f);
    }
    uVar2 = uVar3 + 1;
    iVar1 = uVar3 - 0x17f;
    uVar3 = uVar2;
  } while (iVar1 < 0 != ((int)uVar2 < 0 && -1 < iVar1));
  return;
}

uint32_t restore_event_bitmaps_history_and_generation_from_nvm_51e8a(void)

{
  uint32_t camry_r10_result;
  uint8_t stack_record_b0[176];
  int iVar1;
  int iVar2;
  int iVar3;
  uint *puVar4;
  int iVar5;
  uint32_t puVar6;
  uint uVar7;
  uint *puVar8;
  
  puVar6 = 0xfebeb800u;
  puVar8 = ((undefined *)camry_host_ptr(0x21364u));
  puVar4 = ((uint32_t *)((stack_record_b0 + 8)));
  do {
    uVar7 = *puVar8;
    puVar8 = puVar8 + 1;
    *puVar4 = uVar7;
    puVar4 = puVar4 + 1;
  } while (camry_host_addr(puVar8)!=((uint32_t)(0x21404u)));
  (*((uint32_t *)(stack_record_b0 + 0))) = DAT_0002135c;
  (*((uint32_t *)(stack_record_b0 + 4))) = DAT_00021360;
  uVar7 = (camry_r10_result = nvm_get_record(0, camry_host_addr(((uint32_t *)((stack_record_b0 + 8))))));
  iVar5 = 0;
  if (uVar7 == 0x10) {
    do {
      iVar3 = iVar5 * 4;
      iVar2 = iVar5 + 1;
      iVar1 = iVar5 + -0xb;
      *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe60c0u + (uint32_t)(iVar3) * 1u)))) = ((uint32_t *)((stack_record_b0 + 24)))[iVar5];
      *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe60f0u + (uint32_t)(iVar3) * 1u)))) = ((uint32_t *)((stack_record_b0 + 72)))[iVar5];
      *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe6120u + (uint32_t)(iVar3) * 1u)))) = ((uint32_t *)((stack_record_b0 + 120)))[iVar5];
      iVar5 = iVar2;
    } while (((iVar1 < 0) || (iVar2 < 0)));
    iVar5 = 0;
    do {
      iVar2 = iVar5 + 1;
      iVar1 = iVar5 + -7;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5f71u + (uint32_t)(iVar5) * 1u)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(((uint32_t *)((stack_record_b0 + 8)))) + iVar5))));
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5f79u + (uint32_t)(iVar5) * 1u)))) = ((uint8_t *)((stack_record_b0 + 16)))[iVar5];
      iVar5 = iVar2;
    } while (((iVar1 < 0) || (iVar2 < 0)));
  }
  else if (uVar7 == 0x11) {
    do {
      iVar3 = iVar5 * 4;
      iVar2 = iVar5 + 1;
      iVar1 = iVar5 + -0xb;
      *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe60c0u + (uint32_t)(iVar3) * 1u)))) = 0;
      *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe60f0u + (uint32_t)(iVar3) * 1u)))) = 0;
      *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe6120u + (uint32_t)(iVar3) * 1u)))) = 0;
      iVar5 = iVar2;
    } while (((iVar1 < 0) || (iVar2 < 0)));
    iVar5 = 0;
    do {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5f71u + (uint32_t)(iVar5) * 1u)))) = 0;
      iVar2 = iVar5 + 1;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5f79u + (uint32_t)(iVar5) * 1u)))) = 0;
      iVar1 = iVar5 + -7;
      iVar5 = iVar2;
    } while (((iVar1 < 0) || (iVar2 < 0)));
  }
  else {
    do {
      iVar1 = iVar5 * 4;
      iVar2 = iVar5 + 1;
      *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe60c0u + (uint32_t)(iVar1) * 1u)))) = *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe6090u + (uint32_t)(iVar1) * 1u))));
      uVar7 = ((uint32_t *)((stack_record_b0 + 72)))[iVar5];
      *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe6120u + (uint32_t)(iVar1) * 1u)))) = 0;
      *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe60f0u + (uint32_t)(iVar1) * 1u)))) = *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe60f0u + (uint32_t)(iVar1) * 1u)))) | uVar7;
      iVar1 = iVar5 + -0xb;
      iVar5 = iVar2;
    } while (((iVar1 < 0) || (iVar2 < 0)));
    iVar5 = 0;
    do {
      iVar2 = iVar5 + 1;
      iVar1 = iVar5 + -7;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5f71u + (uint32_t)(iVar5) * 1u)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(((uint32_t *)((stack_record_b0 + 8)))) + iVar5))));
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5f79u + (uint32_t)(iVar5) * 1u)))) = ((uint8_t *)((stack_record_b0 + 16)))[iVar5];
      iVar5 = iVar2;
    } while (((iVar1 < 0) || (iVar2 < 0)));
  }
  rebuild_event_descriptor_bitmap();
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x587e))))) = 0x5a;
  uVar7 = (camry_r10_result = nvm_get_record(10, camry_host_addr(stack_record_b0)));
  if (uVar7 == 0x11) {
    (*((uint16_t *)((uint8_t *)stack_record_b0 + 0u))) = 0;
    (*((uint16_t *)((uint8_t *)stack_record_b0 + 2u))) = 0;
  }
  else if ((((int16_t)(*((uint16_t *)((uint8_t *)stack_record_b0 + 2u)))) == -0x5aa6) && ((short)(*((uint32_t *)(stack_record_b0 + 0))) != -1)) {
    (*((uint16_t *)((uint8_t *)stack_record_b0 + 0u))) = (short)(*((uint32_t *)(stack_record_b0 + 0))) + 1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x587c))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x587c))))) | 0x40;
  }
  DAT_febe6028 = (short)(*((uint32_t *)(stack_record_b0 + 0)));
  DAT_febe602a = (*((uint16_t *)((uint8_t *)stack_record_b0 + 2u)));
  return camry_r10_result;
}

void rebuild_derived_diagnostic_banks(uchar generation_selector)

{
  uint8_t stack_record_3c[60];
  int iVar1;
  int iVar2;
  byte bVar3;
  uint uVar4;
  uint32_t puVar5;
  uint *puVar6;
  uint32_t puVar7;
  uint uVar8;
  uint uVar9;
  int iVar10;
  undefined1 *puVar11;
  
  iVar10 = 0;
  do {
    iVar2 = iVar10 + 1;
    ((uint32_t *)((stack_record_3c + 40)))[iVar10] = 0;
    ((uint32_t *)(stack_record_3c))[iVar10 + 5] = 0;
    ((uint32_t *)(stack_record_3c))[iVar10] = 0;
    iVar1 = iVar10 + -4;
    iVar10 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  if (generation_selector == 0xa5) {
    puVar7 = (0xfebe6090u);
    puVar6 = derived_current_dtc_bitmap;
    puVar5 = (0xfebe6068u);
    puVar11 = ((undefined *)camry_host_ptr(0xfebe5f81u));
  }
  else {
    puVar7 = (0xfebe60c0u);
    puVar6 = derived_retained_dtc_bitmap;
    puVar5 = (0xfebe607cu);
    puVar11 = ((undefined *)camry_host_ptr(0xfebe5f82u));
  }
  *puVar11 = 0;
  uVar9 = 1;
  do {
    if (((*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar7 + (uVar9 >> 5) * 4)))) >> (uVar9 & 0x1f) & 1) != 0) {
      iVar10 = uVar9 * 8;
      uVar8 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2fc52u + (uint32_t)(iVar10) * 1u))));
      if (((uVar8 != 0) && (uVar8 < 0xa0)) && (((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2fc50u + (uint32_t)(iVar10) * 1u)))) >> 6 & 1) != 0)) {
        bVar3 = (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2fc52u + (uint32_t)(iVar10) * 1u)))) >> 5;
        uVar8 = 1 << (uVar8 & 0x1f);
        ((uint32_t *)((stack_record_3c + 40)))[bVar3] = ((uint32_t *)((stack_record_3c + 40)))[bVar3] | uVar8;
        if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2fc51u + (uint32_t)(iVar10) * 1u)))) != '\0') && (generation_selector == 0xa5)) {
          ((uint32_t *)(stack_record_3c))[bVar3] = ((uint32_t *)(stack_record_3c))[bVar3] | uVar8;
        }
      }
      uVar8 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2fc53u + (uint32_t)(iVar10) * 1u))));
      if ((uVar8 != 0) && (uVar8 < 0x40)) {
        uVar4 = (uint)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2fc53u + (uint32_t)(iVar10) * 1u)))) >> 5);
        ((uint32_t *)(stack_record_3c))[uVar4 + 5] = ((uint32_t *)(stack_record_3c))[uVar4 + 5] | 1 << (uVar8 & 0x1f);
      }
    }
    uVar9 = uVar9 + 1;
  } while (uVar9 < 0x180);
  iVar10 = 0;
  do {
    puVar6[iVar10] = ((uint32_t *)((stack_record_3c + 40)))[iVar10];
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar5 + iVar10 * 4)))) = ((uint32_t *)(stack_record_3c))[iVar10 + 5];
    if (generation_selector == 0xa5) {
      (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebe6054u + (uint32_t)(iVar10) * 4u)))) = ((uint32_t *)(stack_record_3c))[iVar10];
    }
    iVar2 = iVar10 + 1;
    iVar1 = iVar10 + -4;
    iVar10 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  return;
}
