#include "common.h"


/* ClearB198/B19A/B19C andB192; publishB18E&F4 clearingbits0/1/3 only. PreserveB191,B195/B196 and
   separate sticky pair. */

undefined4 f33_clear_source_coherence_reentry_history(void)

{
  DAT_febeb198 = 0;
  DAT_febeb19a = 0;
  DAT_febeb19c = 0;
  DAT_febeb192 = 0;
  return FUN_000d268c(f33_source_coherence_history & 0xf4, ((byte *)camry_host_ptr((uint32_t)((0xfebeb18eu)))), ((byte *)camry_host_ptr((uint32_t)((0xfebeb18cu)))), ((undefined *)camry_host_ptr(0xfebeb18du)));
}



/* Clear onlyB196. Invoked by qualifiedB20E11->22; does not rewriteB195. */

void f33_close_health_receive_generation_qualification(void)

{
  f33_health_receive_generation_armed = '\0';
  return;
}



/* ClearB19E/B1A0,B193 andonlybit0ofB194. */

void f33_reset_secondary_channel_qualification_history(void)

{
  DAT_febeb1a0 = 0;
  DAT_febeb19e = 0;
  DAT_febeb193 = 0;
  DAT_febeb194 = DAT_febeb194 & 0xfe;
  return;
}



/* SetB190=5A; laterB3F2A OR-latches sourcehistorybit4; no mode request here. */

void f33_latch_health_command_completion(void)

{
  DAT_febeb190 = 0x5a;
  return;
}



/* DirectB18F5A;noNvMrequest. */

void f33_latch_availability_override(void)

{
  DAT_febeb18f = 0x5a;
  return;
}



/* Only redundantB1A4=0; preserve neighboring one-shot and stage-entry history. */

undefined4 f33_initialize_health_record_lifecycle(void)

{
  return FUN_000d268c(0,((undefined *)camry_host_ptr(0xfebeb1a4u)),((undefined *)camry_host_ptr(0xfebeb1a2u)),((undefined *)camry_host_ptr(0xfebeb1a3u)));
}



/* ClearB1A5/B1A7 and redundantB1A4; distinct fromB41AE initializer. */

undefined4 f33_reset_health_record_lifecycle_entry(void)

{
  DAT_febeb1a5 = 0;
  DAT_febeb1a7 = 0;
  return FUN_000d268c(0,((undefined *)camry_host_ptr(0xfebeb1a4u)),((undefined *)camry_host_ptr(0xfebeb1a2u)),((undefined *)camry_host_ptr(0xfebeb1a3u)));
}



/* B1A6 zero for family<=0300 or0400withB1BD5A, otherwise5A. */

void f33_publish_health_lifecycle_mode_indicator(void)

{
  if (((DAT_febeb11a & 0xff00) < 0x301) ||
     (((DAT_febeb11a & 0xff00) == 0x400 && (DAT_febeb1bd == 'Z')))) {
    DAT_febeb1a6 = 0;
  }
  else {
    DAT_febeb1a6 = 0x5a;
  }
  return;
}



/* VoteB1A4 fallback11. Sticky sourcehistorybit3 enters family-specific record
   invalidation/request23/lifecycle11; old11+completionbit4 enters22. State0->11 cannot also
   complete same call. Republish lifecycle triplet. Native family0300 request23 with retained
   one-shot, and old-state precedence preventing same-call lifecycle0→11→22. */

void f33_advance_health_record_lifecycle(void)

{
  byte bVar1;
  uint32_t puVar2;
  int iVar3;
  uint uVar4;
  undefined1 uVar5;
  char cVar6;
  char cStack_1d;
  
  puVar2 = 0xfebeb800u;
  iVar3 = FUN_000d23b8(((undefined *)camry_host_ptr(0xfebeb1a4u)),((undefined *)camry_host_ptr(0xfebeb1a2u)),((undefined *)camry_host_ptr(0xfebeb1a3u)),&cStack_1d);
  uVar5 = DAT_febeb1a7;
  cVar6 = DAT_febeb1a5;
  if (iVar3 == -0xd) {
    cStack_1d = '\x11';
  }
  bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x672)))));
  uVar4 = FUN_000b1c64();
  if (cStack_1d == '\0') {
    uVar4 = uVar4 & 0xff00;
    if ((bVar1 >> 3 & 1) != 0) {
      if (uVar4 == 0x500) {
        f33_set_output_request_word('\0',0);
        f33_set_output_request_word('\x01',0);
        thunk_FUN_0004841e();
        f33_invalidate_thermal_history_record();
        FUN_000bd8ea();
        FUN_000bd8ba();
        cStack_1d = '\x11';
      }
      else {
        if (uVar4 != 0x300) {
          if (uVar4 == 0x400) {
            cStack_1d = '\x11';
          }
          goto LAB_000b42d4;
        }
        if (cVar6 == '\0') {
          thunk_FUN_0004841e();
          f33_invalidate_thermal_history_record();
          FUN_000bd8ba();
          cVar6 = 'Z';
        }
        FUN_000b15ac(0x23);
      }
      uVar5 = 0x5a;
    }
  }
  else if ((cStack_1d == '\x11') && ((bVar1 >> 4 & 1) != 0)) {
    cStack_1d = '\"';
  }
LAB_000b42d4:
  f33_publish_health_lifecycle_mode_indicator();
  FUN_000d268c(cStack_1d,((undefined *)camry_host_ptr(0xfebeb1a4u)),((undefined *)camry_host_ptr(0xfebeb1a2u)),((undefined *)camry_host_ptr(0xfebeb1a3u)));
  DAT_febeb1a5 = cVar6;
  DAT_febeb1a7 = uVar5;
  return;
}



/* Single constant publisher: DAT_febeb1a7 = 0x5a; Shape-classified from the canonical corpus; the
   target cell is not yet named, so the written state's meaning is unknown. */

void FUN_000b42f0(void)

{
  DAT_febeb1a7 = 0x5a;
  return;
}



/* Single constant publisher: DAT_febeb1a7 = 0; Shape-classified from the canonical corpus; the
   target cell is not yet named, so the written state's meaning is unknown. */

void FUN_000b42fa(void)

{
  DAT_febeb1a7 = 0;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_b4300(void)

{
  return;
}



/* Constant-block fill: 5 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_b4302(void)

{
  DAT_febeb1ac = 0;
  DAT_febeb1ad = 0;
  DAT_febeb1b6 = 0;
  DAT_febeb1b8 = 0;
  DAT_febeb1ba = DAT_000aefba;
  return;
}



void FUN_000b431a(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febeb1aa = 0;
  DAT_febeb1ab = 0;
  DAT_febeb1ae = 0;
  DAT_febeb1b0 = 0;
  DAT_febeb1b4 = 0;
  DAT_febeb1b2 = DAT_000aefba;
  f33_fill_constant_block_b4302();
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x658))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x657))))) = 0;
  return;
}



/* F058 bit0 clear resetsB1B4 and returns0; otherwise return1 until strict count>268, then3.
   Confirmed count holds. R10 is reused across the following first-window helper. otherwise1 until
   strict count>268 then3. Confirmed count holds; native composed case forwards classifier3 through
   both windows. Verified only for the composed current/held inhibition case; other branches remain
   static reconstruction. */

uint f33_classify_received_status_delay(void)

{
  uint uVar1;
  
  if ((DAT_febef058 & 1) == 0) {
    uVar1 = 0;
    DAT_febeb1b4 = 0;
  }
  else {
    uVar1 = 1;
    if ((0x10c < DAT_febeb1b4) || (DAT_febeb1b4 = DAT_febeb1b4 + 1, 0x10c < DAT_febeb1b4)) {
      uVar1 = 3;
    }
  }
  return uVar1;
}



/* WARNING: This is an inlined function */
/* UnderBE9C5A, received-status windows use1200/2000 counters and current B191/classification
   inhibition. Inactive hold release uses200; publishB1AA/B1AB. Exact192-byte leaf preservesR10
   while shiftingR6. Inline real p-code so B451A forwards its original classifier to the second
   window. First received-status1200/2000 window and200-observation hold; B191/classifier
   inhibition. Exact leaf preservesR10 but shiftsR6; inline actual p-code to preserve original
   classifier in B451A. Verified only for the composed current/held inhibition case; other branches
   remain static reconstruction. */

void f33_update_first_health_status_window(uint classification)

{
  if (DAT_febebe9c == 'Z') {
    if (DAT_febef04d == '\x04') {
      if ((DAT_febeb1ae < DAT_000aefb4) &&
         ((DAT_febeb084 < DAT_000aefb6 ||
          (((f33_current_source_coherence_observations & 1) == 0 &&
           (((f33_current_source_coherence_observations >> 1 & 1) == 0 ||
            ((classification >> 1 & 1) == 0)))))))) {
        if (DAT_febeb1ae == 0) {
          DAT_febeb1ab = 0x5a;
          DAT_febeb1aa = 0x5a;
          DAT_febeb1b2 = 0;
        }
        DAT_febeb1ae = DAT_febeb1ae + 1;
        return;
      }
    }
    else {
      if ((DAT_febef04d != '\x02' && DAT_febef04d != '\x03') || (DAT_febef04c == '\0')) {
        if (DAT_febeb1b2 < DAT_000aefba) {
          DAT_febeb1b2 = DAT_febeb1b2 + 1;
        }
        else {
          DAT_febeb1ab = 0;
        }
        goto LAB_000b441e;
      }
      if ((DAT_febeb1b0 < DAT_000aefb8) &&
         ((DAT_febeb084 < DAT_000aefb6 ||
          (((f33_current_source_coherence_observations & 1) == 0 &&
           (((f33_current_source_coherence_observations >> 1 & 1) == 0 ||
            ((classification >> 1 & 1) == 0)))))))) {
        if (DAT_febeb1b0 == 0) {
          DAT_febeb1ab = 0x5a;
          DAT_febeb1aa = 0x5a;
        }
        DAT_febeb1b0 = DAT_febeb1b0 + 1;
        return;
      }
    }
    DAT_febeb1ab = 0;
  }
  else {
    DAT_febeb1ab = 0;
LAB_000b441e:
    DAT_febeb1ae = 0;
    DAT_febeb1b0 = 0;
  }
  DAT_febeb1aa = 0;
  return;
}



/* CompanionB1AC/B1AD window. Initial F04E1 branch uses B191/classification inhibition; alternate
   F04C!=0/B1BD5A branch does not. Distinct1200/2000 active counters and200-observation held
   release. Second current/held window: initial branch uses B191/classifier inhibition, alternate
   branch does not. Native case verifies original classifier3 inhibits second window after
   destructive first-helper R6 use. Verified only for the composed current/held inhibition case;
   other branches remain static reconstruction. */

void f33_update_second_health_status_window(uint classification)

{
  if (DAT_febebe9c == 'Z') {
    if (DAT_febef04e == '\x01') {
      if ((DAT_febeb1b6 < DAT_000aefbc) &&
         ((DAT_febeb084 < DAT_000aefb6 ||
          (((f33_current_source_coherence_observations & 1) == 0 &&
           (((f33_current_source_coherence_observations >> 1 & 1) == 0 ||
            ((classification >> 1 & 1) == 0)))))))) {
        if (DAT_febeb1b6 == 0) {
          DAT_febeb1ad = 0x5a;
          DAT_febeb1ac = 0x5a;
          DAT_febeb1ba = 0;
        }
        DAT_febeb1b6 = DAT_febeb1b6 + 1;
        return;
      }
    }
    else {
      if ((DAT_febef04c == '\0') || (DAT_febeb1bd != 'Z')) {
        if (DAT_febeb1ba < DAT_000aefba) {
          DAT_febeb1ba = DAT_febeb1ba + 1;
        }
        else {
          DAT_febeb1ad = 0;
        }
        goto LAB_000b44ce;
      }
      if (DAT_febeb1b8 < DAT_000aefbe) {
        if (DAT_febeb1b8 == 0) {
          DAT_febeb1ad = 0x5a;
          DAT_febeb1ac = 0x5a;
        }
        DAT_febeb1b8 = DAT_febeb1b8 + 1;
        return;
      }
    }
    DAT_febeb1ad = 0;
  }
  else {
    DAT_febeb1ad = 0;
LAB_000b44ce:
    DAT_febeb1b6 = 0;
    DAT_febeb1b8 = 0;
  }
  DAT_febeb1ac = 0;
  return;
}



/* Rebuild B1A8 from currentB1AA/B1AC, B1A9 from heldB1AB/B1AD. Current inhibits owner1
   qualification; held selects owner6 source override. No meaningful scalar return contract. Publish
   B1A8 from current andB1A9 from held source windows. Native composition clears both after
   classified inhibition; outer scalar return is not part of contract. Verified only for the
   composed current/held inhibition case; other branches remain static reconstruction. */

void f33_publish_current_and_held_health_windows(void)

{
  if ((DAT_febeb1aa == 'Z') || (DAT_febeb1ac == 'Z')) {
    DAT_febeb1a8 = 0x5a;
  }
  else {
    DAT_febeb1a8 = 0;
  }
  if ((DAT_febeb1ab == 'Z') || (DAT_febeb1ad == 'Z')) {
    DAT_febeb1a9 = 0x5a;
  }
  else {
    DAT_febeb1a9 = 0;
  }
  return;
}



/* WARNING: Inlined function: f33_update_first_health_status_window */
/* B4346 classification0/1/3 is retainedinR10 acrossB4370(noR10write), thenpassedtoB4430;
   B4370maydestructivelyshiftR6. BothfeedB44E0current/heldsummaries. Do
   notinventsecondpermissionreturn. Composed real classifier3 survives first window inR10 despite
   destructiveR6 bit tests, inhibits second window, and publishes cleared current/held summaries.
   Inline actual B4370 p-code; do not invent a fresh return or use post-callR6. Other window
   branches remain static reconstruction. */

void f33_update_health_status_delay_summaries(void)

{
  char cVar1;
  byte bVar2;
  ushort uVar3;
  uint32_t puVar4;
  uint classification;
  undefined1 uVar5;
  ushort uVar6;
  undefined1 uVar7;
  ushort uVar8;
  
  puVar4 = 0xfebeb800u;
  classification = f33_classify_received_status_delay();
  uVar6 = (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + -0x64e))));
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x69c))))) == 'Z') {
    cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x384d)))));
    uVar7 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x656)))));
    uVar5 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x655)))));
    uVar3 = (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + -0x652))));
    uVar8 = (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + -0x650))));
    bVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x66f)))));
    if (cVar1 == '\x04') {
      if ((uVar3 < DAT_000aefb4) &&
         (((*((ushort *)camry_host_ptr((uint32_t)(puVar4 + -0x77c)))) < DAT_000aefb6 ||
          (((bVar2 & 1) == 0 && (((bVar2 >> 1 & 1) == 0 || ((classification >> 1 & 1) == 0)))))))) {
        if (uVar3 == 0) {
          uVar5 = 0x5a;
          uVar7 = 0x5a;
          uVar6 = 0;
        }
        uVar3 = uVar3 + 1;
        goto LAB_000b4420;
      }
    }
    else {
      if ((cVar1 != '\x02' && cVar1 != '\x03') || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x384c))))) == '\0')) {
        if (uVar6 < DAT_000aefba) {
          uVar6 = uVar6 + 1;
        }
        else {
          uVar5 = 0;
        }
        goto LAB_000b441e;
      }
      if ((uVar8 < DAT_000aefb8) &&
         (((*((ushort *)camry_host_ptr((uint32_t)(puVar4 + -0x77c)))) < DAT_000aefb6 ||
          (((bVar2 & 1) == 0 && (((bVar2 >> 1 & 1) == 0 || ((classification >> 1 & 1) == 0)))))))) {
        if (uVar8 == 0) {
          uVar5 = 0x5a;
          uVar7 = 0x5a;
        }
        uVar8 = uVar8 + 1;
        goto LAB_000b4420;
      }
    }
    uVar7 = 0;
    uVar5 = 0;
  }
  else {
    uVar5 = 0;
LAB_000b441e:
    uVar7 = 0;
    uVar3 = 0;
    uVar8 = 0;
  }
LAB_000b4420:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x656))))) = uVar7;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x655))))) = uVar5;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + -0x652)))) = uVar3;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + -0x650)))) = uVar8;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + -0x64e)))) = uVar6;
  f33_update_second_health_status_window(classification);
  f33_publish_current_and_held_health_windows();
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_b4536(void)

{
  return;
}



void FUN_000b4538(void)

{
  DAT_febeb1bc = 0;
  DAT_febeb1bd = 0;
  DAT_febeb1c0 = 0;
  DAT_febeb1c2 = 0;
  return;
}



void FUN_000b4546(void)

{
  char cVar1;
  int iVar2;
  char cVar3;
  char cVar4;
  uint32_t puVar5;
  uint event;
  char cVar6;
  char cVar7;
  ushort uVar8;
  char cVar9;
  ushort uVar10;
  char cVar11;
  
  cVar4 = DAT_febef0fe;
  cVar3 = DAT_febef0fd;
  iVar2 = DAT_febeb30c;
  cVar1 = DAT_febeb1d1;
  cVar11 = DAT_febeb1be;
  puVar5 = 0xfebeb800u;
  if (DAT_febeb30c == 0x55aaaa55) {
    cVar9 = DAT_febebe79;
    uVar8 = DAT_000aefc0;
    cVar7 = DAT_febebe7c;
    cVar6 = '\0';
  }
  else {
    cVar9 = DAT_febebe7a;
    uVar8 = DAT_000aefc6;
    cVar7 = DAT_febebe7d;
    cVar6 = DAT_febef10d;
    if (DAT_febeb30c != -0x55aaaa56) {
      cVar9 = -1;
      cVar7 = '\"';
      uVar8 = 0xffff;
      cVar6 = '\0';
    }
  }
  uVar10 = DAT_febeb1c0;
  if (DAT_febeb1bc == 'Z') {
    cVar9 = 'Z';
    goto LAB_000b46d2;
  }
  if (((((DAT_febeb1a4 == '\x11') &&
        ((((DAT_febeb20e == '\0' || (DAT_febeb20e == '3')) &&
          (f33_published_internal_source_admission_state < 2)) &&
         ((cVar7 == '\0' && (DAT_febeb18f == '\0')))))) &&
       ((DAT_febef04c != '\0' ||
        (((DAT_febef04d != '\x02' && (DAT_febef04d != '\x03')) && (DAT_febef04d != '\x04')))))) &&
      ((((DAT_febeb11a & 0xff00) != 0x500 && (cVar9 == 'Z')) &&
       ((DAT_febef10e != '\0' || (cVar6 == '\0')))))) &&
     ((DAT_febebeb8 == '\0' || ((DAT_febebeb8 == 'Z' && (DAT_febead93 == '\0')))))) {
    cVar9 = DAT_febeb1bd;
    if (uVar8 < DAT_febeb1c0) goto LAB_000b46d2;
    uVar10 = DAT_febeb1c0 + 1;
    puVar5 = 0xfebeb800u;
    if (uVar8 < uVar10) {
      puVar5 = 0xfebeb800u;
      f33_publish_thermal_reference_record();
      f33_publish_thermal_history_record();
      f33_stage_received_word_age_record13();
      cVar9 = 'Z';
      if (cVar1 == '\0') {
        if ((cVar3 == '\0') && (cVar4 == '\0')) {
          cVar11 = 'D';
        }
        else {
          if (iVar2 == -0x55aaaa56) {
            f33_report_diagnostic_event_failure(0x101,0x32);
            cVar11 = '\x11';
          }
          else {
            f33_report_diagnostic_event_failure(0x99,0x32);
            cVar11 = '\0';
          }
          thunk_FUN_000545de(0xf);
          thunk_FUN_00051cf6(7,0x32);
        }
      }
      else {
        f33_report_diagnostic_event_failure(0x90,0x32);
        cVar11 = '\"';
      }
      goto LAB_000b46d2;
    }
  }
  else {
    uVar10 = 0;
    puVar5 = 0xfebeb800u;
    if (DAT_febeb1bd == 'Z') {
      puVar5 = 0xfebeb800u;
      thunk_FUN_0004841e();
      f33_invalidate_thermal_history_record();
      if (cVar11 == '\x11') {
        event = 0x101;
      }
      else {
        event = 0x90;
        if (cVar11 == '\0') {
          event = 0x99;
        }
      }
      f33_report_diagnostic_event_pass(event);
    }
  }
  cVar9 = '\0';
LAB_000b46d2:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x643))))) = cVar9;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar5 + -0x640)))) = uVar10;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x642))))) = cVar11;
  return;
}



void FUN_000b46e0(void)

{
  undefined1 uVar1;
  uint32_t puVar2;
  ushort uVar3;
  
  puVar2 = 0xfebeb800u;
  uVar1 = DAT_febeb1bc;
  if (((DAT_febeb1bd == 'Z') && (DAT_febebedd == 'Z')) && (DAT_febebede <= DAT_000aefc4)) {
    uVar3 = DAT_febeb1c2;
    if ((DAT_febeb1c2 <= DAT_000aefc2) && (uVar3 = DAT_febeb1c2 + 1, DAT_000aefc2 < uVar3)) {
      puVar2 = 0xfebeb800u;
      f33_clear_source_coherence_reentry_history();
      uVar1 = 0x5a;
    }
  }
  else {
    uVar3 = 0;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x644))))) = uVar1;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x63e)))) = uVar3;
  return;
}



void FUN_000b4736(void)

{
  uchar uVar1;
  char cVar2;
  int iVar3;
  uint32_t puVar4;
  uint uVar5;
  undefined2 uVar6;
  undefined2 uVar7;
  undefined1 uVar8;
  char cVar9;
  
  iVar3 = DAT_febeb30c;
  uVar6 = DAT_febeb1c2;
  uVar7 = DAT_febeb1c0;
  cVar2 = DAT_febeb1be;
  uVar8 = DAT_febeb1bd;
  cVar9 = DAT_febeb1bc;
  uVar1 = f33_source_coherence_history;
  puVar4 = 0xfebeb800u;
  uVar5 = 0;
  if (DAT_febeb1bc == 'Z') {
    if (DAT_febebcb0 == 0) {
      uVar5 = 0x70017001;
    }
    puVar4 = 0xfebeb800u;
    f33_set_output_request_word('\x04',uVar5);
    if (((uVar1 >> 3 & 1) != 0) || (iVar3 == 0)) {
      f33_set_output_request_word('\x04',0);
      if (cVar2 == '\x11') {
        uVar5 = 0x101;
      }
      else {
        uVar5 = 0x90;
        if (cVar2 == '\0') {
          uVar5 = 0x99;
        }
      }
      f33_report_diagnostic_event_pass(uVar5);
      thunk_FUN_0004841e();
      f33_invalidate_thermal_history_record();
      uVar7 = 0;
      uVar6 = 0;
      uVar8 = 0;
      cVar9 = '\0';
    }
  }
  else {
    f33_set_output_request_word('\x04',0);
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar4 + -0x640)))) = uVar7;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x643))))) = uVar8;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar4 + -0x63e)))) = uVar6;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x644))))) = cVar9;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x642))))) = cVar2;
  return;
}



void FUN_000b47c0(void)

{
  FUN_000b4546();
  FUN_000b46e0();
  FUN_000b4736();
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_b47d4(void)

{
  return;
}



/* Single constant publisher: DAT_febeb1c4 = 2; Shape-classified from the canonical corpus; the
   target cell is not yet named, so the written state's meaning is unknown. */

void FUN_000b47d6(void)

{
  DAT_febeb1c4 = 2;
  return;
}



void FUN_000b47de(void)

{
  if (((DAT_febeb1ce == 'Z') || (DAT_febeb1d1 == 'Z')) || (DAT_febeb1bd == 'Z')) {
    DAT_febeb1c4 = 2;
  }
  else {
    DAT_febeb1c4 = 1;
  }
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_b4808(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_b480a(void)

{
  return;
}



undefined2 FUN_000b480c(void)

{
  if ((((f33_published_internal_source_admission_state != '\x03') && ((DAT_febef093 >> 1 & 1) == 0))
      && (DAT_febef013 != '\x02')) && ((DAT_febef013 != '\x03' && ((DAT_febef16a & 0x1010) == 0))))
  {
    return DAT_febebede;
  }
  return DAT_febebee2;
}



void FUN_000b483e(void)

{
  char cVar1;
  uint32_t puVar2;
  uint uVar3;
  uint uVar4;
  undefined1 uVar5;
  short sVar6;
  undefined2 uStack_12;
  
  puVar2 = 0xfebeb800u;
  uStack_12 = DAT_febeb1ec;
  uVar4 = (uint)DAT_000af028;
  uVar5 = DAT_febeb1cb;
  cVar1 = DAT_febeb1c9;
  if ((((DAT_febeb1c9 == 'Z') && (DAT_febeb1ca == 'Z')) && (DAT_febeb080 < DAT_000aefca)) &&
     ((DAT_febebeb8 == '\0' || ((DAT_febebeb8 == 'Z' && (DAT_febead93 == '\0')))))) {
    if (DAT_febeb1e4 < DAT_000aefd4) {
      sVar6 = DAT_febeb1e4 + 1;
    }
    else {
      sVar6 = 0;
      if (DAT_febeb1ce != 'Z') {
        puVar2 = 0xfebeb800u;
        uVar3 = FUN_000b480c();
        uVar5 = 0;
        if (uVar4 <= uVar3) {
          uVar5 = 0x5a;
          FUN_000d1ee0(((undefined *)camry_host_ptr(0xaf000u)),uVar3,&uStack_12);
        }
        cVar1 = '\0';
      }
    }
  }
  else {
    sVar6 = 0;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x635))))) = uVar5;
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + -0x61c)))) = sVar6;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x637))))) = cVar1;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x614)))) = uStack_12;
  return;
}



void FUN_000b48dc(void)

{
  if (((DAT_febeb1ca == 'Z') && (DAT_febef0b3 != 'Z')) && (DAT_febeb1c9 == '\0')) {
    if ((DAT_febef0fe == '\0') && (DAT_febef0fd != '\0')) {
      DAT_febeb1e8 = 0;
    }
    else if (DAT_febeb1e8 < DAT_000aefd8) {
      DAT_febeb1e8 = DAT_febeb1e8 + 1;
    }
    else {
      DAT_febeb1e8 = 0;
      DAT_febeb1ca = '\0';
    }
    if (DAT_febeb1ea < DAT_000aefdc) {
      DAT_febeb1ea = DAT_febeb1ea + 1;
    }
    else {
      DAT_febeb1ea = 0;
      DAT_febeb1ca = '\0';
    }
  }
  else {
    DAT_febeb1e8 = 0;
    DAT_febeb1ea = 0;
  }
  return;
}



void FUN_000b4948(void)

{
  char cVar1;
  uint32_t puVar2;
  uint uVar3;
  uint uVar4;
  undefined1 uVar5;
  short sVar6;
  undefined2 uStack_12;
  
  puVar2 = 0xfebeb800u;
  uStack_12 = DAT_febeb1ec;
  uVar4 = (uint)DAT_000af028;
  uVar5 = DAT_febeb1cb;
  cVar1 = DAT_febeb1cc;
  if (((DAT_febeb1cc == 'Z') && ((DAT_febef0b3 == 'Z' || (DAT_febef0b1 == 'Z')))) &&
     ((DAT_febef0fe != '\0' || (DAT_febef0fd == '\0')))) {
    if (DAT_febeb1ee < DAT_000aefda) {
      sVar6 = DAT_febeb1ee + 1;
    }
    else {
      sVar6 = 0;
      if (DAT_febeb1ce != 'Z') {
        puVar2 = 0xfebeb800u;
        uVar3 = FUN_000b480c();
        uVar5 = 0;
        if (uVar4 <= uVar3) {
          uVar5 = 0x5a;
          FUN_000d1ee0(((undefined *)camry_host_ptr(0xaf000u)),uVar3,&uStack_12);
        }
        cVar1 = '\0';
      }
    }
  }
  else {
    sVar6 = 0;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x635))))) = uVar5;
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + -0x612)))) = sVar6;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x634))))) = cVar1;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x614)))) = uStack_12;
  return;
}



/* Qualify strictB0802125..4096 orF0FD1/F0FE0; on recovery event8Dpass/cache flags/sourcehistory
   reentry-clear; B1C8bit4->bit2. ConditionalB192 feedback clearsB1D1. */

void f33_qualify_health_source_recovery(void)

{
  char cVar1;
  uint32_t puVar2;
  undefined1 uVar3;
  undefined1 uVar4;
  undefined1 uVar5;
  char cVar6;
  char cVar7;
  char cVar8;
  byte bVar9;
  ushort uVar10;
  ushort uVar11;
  
  bVar9 = DAT_febeb1c8;
  puVar2 = 0xfebeb800u;
  cVar1 = '\0';
  uVar5 = DAT_febeb1ce;
  uVar4 = DAT_febeb1d0;
  uVar3 = DAT_febeb1d1;
  cVar8 = DAT_febeb1c9;
  cVar6 = DAT_febeb1ca;
  cVar7 = DAT_febeb1cc;
  uVar11 = DAT_febeb1fa;
  uVar10 = DAT_febeb1fc;
  if (DAT_febeb1cd != '\0') goto LAB_000b4a90;
  if (((DAT_febeb1c9 == '\0') && (DAT_000aefd0 < DAT_febeb080)) && (DAT_febeb080 < DAT_000aefd2)) {
    if (DAT_febeb1fa < DAT_000aefea) {
      uVar11 = DAT_febeb1fa + 1;
    }
    else {
      cVar1 = 'Z';
      uVar11 = 0;
      cVar8 = cVar1;
      cVar6 = cVar1;
    }
  }
  else {
    uVar11 = 0;
  }
  if (((DAT_febeb1cc == '\0') && (DAT_febef0fd == '\x01')) && (DAT_febef0fe == '\0')) {
    if (DAT_febeb1fc < DAT_000aefec) {
      uVar10 = DAT_febeb1fc + 1;
      goto LAB_000b4a68;
    }
    uVar10 = 0;
    cVar7 = 'Z';
  }
  else {
    uVar10 = 0;
LAB_000b4a68:
    if (cVar1 != 'Z') goto LAB_000b4a90;
  }
  puVar2 = 0xfebeb800u;
  f33_report_diagnostic_event_pass(0x8d);
  thunk_FUN_000515d4();
  f33_clear_source_coherence_reentry_history();
  uVar5 = 0;
  uVar4 = 0x5a;
  uVar3 = 0x5a;
  bVar9 = bVar9 & 0xef | 4;
LAB_000b4a90:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x637))))) = cVar8;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x636))))) = cVar6;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x634))))) = cVar7;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x632))))) = uVar5;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x630))))) = uVar4;
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x66e))))) == 'Z') {
    uVar3 = 0;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x638))))) = bVar9;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x606)))) = uVar11;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x604)))) = uVar10;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x62f))))) = uVar3;
  return;
}



/* Gated call fromB4EF4: latchB1CE andB1C8bit4 while clearingbit2; reportevent8D failure
   independently of health publication. */

void f33_latch_health_source_unavailability(void)

{
  char cVar1;
  uint32_t puVar2;
  byte bVar3;
  
  bVar3 = DAT_febeb1c8;
  puVar2 = 0xfebeb800u;
  cVar1 = DAT_febeb1ce;
  if ((((DAT_febeb1cd == '\0') && (DAT_febeb1ce == '\0')) &&
      ((DAT_febeb1ca == '\0' || (DAT_febeb1cc == '\0')))) && (DAT_febeb1cb == 'Z')) {
    puVar2 = 0xfebeb800u;
    f33_report_diagnostic_event_failure(0x8d,0x32);
    cVar1 = 'Z';
    bVar3 = bVar3 & 0xfb | 0x10;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x632))))) = cVar1;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x638))))) = bVar3;
  return;
}



void FUN_000b4b04(void)

{
  if ((DAT_febeb1d0 == 'Z') && (DAT_febeb1ce == 'Z')) {
    if ((DAT_febeb1f4 < DAT_febeb1ec) && (DAT_febeb200 < DAT_000aeff2)) {
      if ((DAT_febebedd == 'Z') && (DAT_febebede <= DAT_000aeff0)) {
        DAT_febeb200 = DAT_febeb200 + 1;
      }
      else {
        DAT_febeb200 = 0;
      }
      DAT_febeb1f4 = DAT_febeb1f4 + 1;
    }
    else {
      DAT_febeb1f4 = 0;
      DAT_febeb1d0 = '\0';
      DAT_febeb200 = 0;
    }
  }
  else {
    DAT_febeb1f4 = 0;
    DAT_febeb200 = 0;
  }
  return;
}



void FUN_000b4b6c(void)

{
  ushort uVar1;
  ushort uVar2;
  int iVar3;
  uint32_t puVar4;
  uint uVar5;
  int iVar6;
  char cVar7;
  ushort uVar8;
  ushort uStack_1e;
  uint uStack_1c;
  ushort auStack_18 [2];
  uint uStack_14;
  
  cVar7 = DAT_febeb1cf;
  puVar4 = 0xfebeb800u;
  iVar6 = (int)DAT_febeb054;
  uStack_1e = DAT_febeb1f8;
  uStack_1c = DAT_febeb208;
  if (iVar6 + 0x7fff < 0 == (-1 < iVar6 && iVar6 + 0x7fff < 0) && iVar6 != -0x7fff) {
    if (iVar6 < 0) {
      iVar6 = (int)-DAT_febeb054;
    }
  }
  else {
    iVar6 = 0x7fff;
  }
  auStack_18[0] = DAT_febeb1f8;
  uStack_14 = DAT_febeb208;
  if ((DAT_febeb1cf == '\0') && (DAT_febeb1d0 == '\0')) {
    if (DAT_000aeff4 < DAT_febeb1f8) {
      uVar1 = DAT_000aefe6;
      uVar8 = DAT_febeb1f6;
      if (DAT_febeb1f6 < DAT_000aefe2) {
        iVar3 = (int)DAT_000aefe4;
        uVar8 = DAT_febeb1f6 + 1;
        uVar1 = DAT_000aefe8;
        if (iVar6 - iVar3 < 0 != (iVar6 < 0 != iVar3 < 0 && iVar3 < 0 == iVar6 - iVar3 < 0) ||
            iVar6 == iVar3) goto LAB_000b4bf4;
      }
      auStack_18[1] = 0;
      puVar4 = 0xfebeb800u;
      f33_filter_unsigned_sample_accumulator(auStack_18,(uint)uVar1,&uStack_1e,&uStack_1c);
    }
    else {
      cVar7 = 'Z';
      uVar8 = 0;
    }
LAB_000b4bf4:
    uVar5 = 0;
    uVar1 = uVar8;
    uVar2 = 0;
    if (0x14 < uStack_1e) goto LAB_000b4c38;
  }
  else {
    auStack_18[1] = 0x400;
    uVar8 = 0;
    f33_filter_unsigned_sample_accumulator(auStack_18,(uint)DAT_000aefee,&uStack_1e,&uStack_1c);
    uVar5 = 0x4000000;
    uVar1 = 0;
    uVar2 = 0x400;
    if (uStack_1e < 0x3ec) goto LAB_000b4c38;
  }
  uStack_1e = uVar2;
  uVar8 = uVar1;
  uStack_1c = uVar5;
LAB_000b4c38:
  (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + -0x608)))) = uStack_1e;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x631))))) = cVar7;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + -0x60a)))) = uVar8;
  (*((uint *)camry_host_ptr((uint32_t)(puVar4 + -0x5f8)))) = uStack_1c;
  return;
}



/* StageB1D5/B1D6 from paired receivedstatuses andB193. Later exact0/0 reset branch wins, callsB4186
   and returnsstageA5; no invented permission. */

void f33_update_health_secondary_qualification_handshake(void)

{
  char cVar1;
  int iVar2;
  uint32_t puVar3;
  int iVar4;
  undefined1 uVar5;
  int iVar6;
  char cVar7;
  ushort uVar8;
  bool bVar9;
  
  puVar3 = 0xfebeb800u;
  if (DAT_000aefca < DAT_febeb080) {
    if (DAT_febeb204 < DAT_000aefd4) {
      uVar8 = DAT_febeb204 + 1;
      iVar2 = 0;
    }
    else {
      iVar2 = 0x5a;
      uVar8 = DAT_febeb204;
    }
  }
  else {
    uVar8 = 0;
    iVar2 = 0;
  }
  uVar5 = DAT_febeb1d6;
  cVar7 = DAT_febeb1d5;
  if (((int8_t)DAT_febeb1d5) == -0x5b) {
    if (DAT_febef0fe == '\0') {
      bVar9 = DAT_febef0fd == '\x01';
    }
    else {
      bVar9 = iVar2 == 0x5a;
    }
    if (!bVar9) goto LAB_000b4d18;
    if ((DAT_febef100 == '\0') && (DAT_febef0ff == '\x01')) {
      iVar4 = 0x5a;
    }
    else {
      iVar4 = 0;
    }
    if ((DAT_febef102 == '\0') && (DAT_febef101 == '\x01')) {
      iVar6 = 0x5a;
    }
    else {
      iVar6 = 0;
    }
    if (iVar4 == 0x5a) {
      cVar1 = DAT_febef102;
      if (iVar6 != 0x5a) goto LAB_000b4ce2;
    }
    else {
      cVar1 = DAT_febef100;
      if (iVar6 != 0x5a) goto LAB_000b4cf0;
LAB_000b4ce2:
      if (cVar1 == '\0') goto LAB_000b4cf0;
    }
    uVar5 = 0x5a;
    if (DAT_febeb193 == 'Z') {
      cVar7 = 'Z';
    }
  }
LAB_000b4cf0:
  if (DAT_febef0fe == '\0') {
    bVar9 = DAT_febef0fd == '\x01';
  }
  else {
    bVar9 = iVar2 == 0x5a;
  }
  if ((bVar9) &&
     (((DAT_febef100 == '\0' && (DAT_febef0ff == '\0')) ||
      ((DAT_febef102 == '\0' && (DAT_febef101 == '\0')))))) {
    puVar3 = 0xfebeb800u;
    f33_reset_secondary_channel_qualification_history();
    uVar5 = 0;
    cVar7 = -0x5b;
  }
LAB_000b4d18:
  (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x5fc)))) = uVar8;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x62a))))) = uVar5;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x62b))))) = cVar7;
  return;
}



/* Existing staged-source eligibility plus conditionedmulti-input/count paths OR-latchB1C8bit3/B1CD.
   Preserve numeric software policy; physical meanings unknown. */

void f33_latch_qualified_health_entry_conditions(void)

{
  ushort uVar1;
  ushort uVar2;
  int iVar3;
  int iVar4;
  
  iVar4 = (int)DAT_febeafdc;
  if (iVar4 + 0x7fff < 0 == (-1 < iVar4 && iVar4 + 0x7fff < 0) && iVar4 != -0x7fff) {
    if (iVar4 < 0) {
      iVar4 = (int)-DAT_febeafdc;
    }
  }
  else {
    iVar4 = 0x7fff;
  }
  uVar2 = DAT_febeb086;
  uVar1 = DAT_febeb088;
  if ((DAT_febeb082 & 1) == 0) {
    uVar1 = DAT_febeb086;
    if ((DAT_febeb082 & 2) == 0) {
      uVar1 = DAT_febeb088;
    }
  }
  else {
    uVar2 = DAT_febeb088;
    if ((DAT_febeb082 & 2) != 0) {
      uVar2 = DAT_febeb086;
    }
  }
  if (DAT_febeb1cd == '\0') {
    if (((((DAT_febeb11a & 0xff00) < 0x700) && (DAT_febeb1a7 != '\0')) || (DAT_febeb1c9 != '\0')) &&
       ((((DAT_febeb1ce != '\0' || ((DAT_febeb1ca != '\0' && (DAT_febeb1cc != '\0')))) ||
         (DAT_febeb1cb != '\0')) && (DAT_febeb1cf != 'Z')))) {
      DAT_febeb1cd = '\0';
      if (((DAT_000aefcc < DAT_febeb080) && (DAT_000aefce < uVar2)) &&
         ((DAT_000aefce < uVar1 &&
          (iVar3 = (int)DAT_000aeffc,
          iVar4 - iVar3 < 0 != (iVar4 < 0 != iVar3 < 0 && iVar3 < 0 == iVar4 - iVar3 < 0))))) {
        if (DAT_000aefe0 <= DAT_febeb1f0) {
          DAT_febeb1c8 = DAT_febeb1c8 | 8;
          DAT_febeb1cd = 0x5a;
          DAT_febeb1d4 = 0x5a;
          DAT_febeb1f0 = 0;
          DAT_febeb1f2 = 0;
          return;
        }
        DAT_febeb1f0 = DAT_febeb1f0 + 1;
        goto LAB_000b4e0c;
      }
    }
    else {
      DAT_febeb1cd = 'Z';
      DAT_febeb1c8 = DAT_febeb1c8 | 8;
    }
  }
  DAT_febeb1f0 = 0;
LAB_000b4e0c:
  if (((((DAT_febeb1cd == '\0') && ((DAT_febeb11a & 0xff00) < 0x501)) && (DAT_febeb1a7 == '\0')) &&
      (DAT_000aefcc < DAT_febeb080)) && ((DAT_febef0fe != '\0' || (DAT_febef0fd == '\0')))) {
    if (DAT_febeb1f2 < DAT_000aefde) {
      DAT_febeb1f2 = DAT_febeb1f2 + 1;
      return;
    }
    DAT_febeb1c8 = DAT_febeb1c8 | 8;
    DAT_febeb1cd = 0x5a;
    DAT_febeb1f2 = 0;
    return;
  }
  DAT_febeb1f2 = 0;
  return;
}



/* UnderB1CD5A, strict2125<B080<4096: after40 counts ORbit0; family0800 ORbit1 immediately. Outside
   resets counter not latchedbits. */

void f33_latch_qualified_health_completion_conditions(void)

{
  if (DAT_febeb1cd == 'Z') {
    if ((DAT_000aeff8 < DAT_febeb080) && (DAT_febeb080 < DAT_000aeffa)) {
      if (DAT_febeb1fe < DAT_000aeff6) {
        DAT_febeb1fe = DAT_febeb1fe + 1;
      }
      else {
        DAT_febeb1c8 = DAT_febeb1c8 | 1;
      }
    }
    else {
      DAT_febeb1fe = 0;
      if (DAT_febeb080 <= DAT_000aeff8) {
        DAT_febeb1fe = 0;
        return;
      }
    }
    if ((DAT_febeb080 < DAT_000aeffa) && ((DAT_febeb11a & 0xff00) == 0x800)) {
      DAT_febeb1c8 = DAT_febeb1c8 | 2;
    }
  }
  return;
}



void FUN_000b4eb6(void)

{
  undefined2 uVar1;
  undefined1 uVar2;
  
  if (DAT_febeb1d4 == 'Z') {
    uVar1 = DAT_febeb202;
    uVar2 = DAT_febeb1d2;
    if (DAT_febeb1a7 == 'Z') {
      DAT_febeb1d3 = DAT_febeb1a7;
      return;
    }
  }
  else {
    uVar1 = DAT_febebede;
    uVar2 = DAT_febebef0;
    if (DAT_febeb1f0 != 1) {
      uVar1 = DAT_febeb202;
      uVar2 = DAT_febeb1d2;
    }
  }
  DAT_febeb1d2 = uVar2;
  DAT_febeb202 = uVar1;
  DAT_febeb1d3 = 0;
  return;
}



/* Advance received/conditioned recovery policy, gated unavailability/fade, secondary handshake,
   entry/completion latches; called afterB3F44/B4214 beforeB4FFC. */

void f33_update_qualified_health_source_policy(void)

{
  char cVar1;
  uint32_t puVar2;
  ushort uVar3;
  
  cVar1 = DAT_febeb1a7;
  puVar2 = 0xfebeb800u;
  uVar3 = DAT_febeb11a & 0xff00;
  FUN_000b483e();
  FUN_000b48dc();
  FUN_000b4948();
  f33_qualify_health_source_recovery();
  if ((cVar1 == 'Z') && (uVar3 < 0x501)) {
    f33_latch_health_source_unavailability();
    FUN_000b4b04();
    FUN_000b4b6c();
  }
  else {
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x608)))) = 0x400;
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + -0x5f8)))) = 0x4000000;
  }
  f33_update_health_secondary_qualification_handshake();
  f33_latch_qualified_health_entry_conditions();
  f33_latch_qualified_health_completion_conditions();
  FUN_000b4eb6();
  return;
}



/* Initialize redundantB20E0 only; not stickyB20F or source-generation reset. */

undefined4 f33_initialize_qualified_health_state(void)

{
  return FUN_000d268c(0,((undefined *)camry_host_ptr(0xfebeb20eu)),((undefined *)camry_host_ptr(0xfebeb20cu)),((undefined *)camry_host_ptr(0xfebeb20du)));
}



/* Initialize redundantB20E0 andclearB20F; doesnotclearB195/B196. */

void f33_reset_qualified_health_state_entry(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  FUN_000d268c(0,((undefined *)camry_host_ptr(0xfebeb20eu)),((undefined *)camry_host_ptr(0xfebeb20cu)),((undefined *)camry_host_ptr(0xfebeb20du)));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5f1))))) = 0;
  return;
}



/* State11 requests1, with BCB0==0 in0400/0500;22 requests1 only in0400/0500 and2 in0700/0800.
   Exact0522 also requiresAFCE!=11 andBCB0==0. Never cancels request1. Routing consumes the new
   qualified state before redundant publication. Native qualified22 in family0800 queues request2
   despite nonzero owner5 request; other routing branches remain static reconstruction. */

void f33_route_qualified_health_mode_requests(uchar qualified_state)

{
  ushort uVar1;
  undefined4 uVar2;
  
  uVar1 = DAT_febeb11a & 0xff00;
  if (qualified_state == '\x11') {
    if (DAT_febeb11a == 0x522) {
LAB_000b4fc2:
      if (DAT_febebcb0 != 0) {
        return;
      }
      if (DAT_febeafce == '\x11') {
        return;
      }
    }
    else if ((uVar1 == 0x400) || (uVar1 == 0x500)) goto LAB_000b4fde;
  }
  else {
    if (qualified_state != '\"') {
      return;
    }
    if (DAT_febeb11a == 0x522) goto LAB_000b4fc2;
    if ((uVar1 != 0x400) && (uVar1 != 0x500)) {
      if ((uVar1 != 0x700) && (uVar1 != 0x800)) {
        return;
      }
      uVar2 = 2;
      goto LAB_000b4ff4;
    }
LAB_000b4fde:
    if (DAT_febebcb0 != 0) {
      return;
    }
  }
  uVar2 = 1;
LAB_000b4ff4:
  FUN_000b15ac(uVar2);
  return;
}



/* VoteB20E/B20C/B20D with fallback0 only on uncorrectable disagreement. States0/33 take11 first
   onB1C8 bit3/5; otherwise0\u219233 onbit4 and33\u21920 onbit2.11\u219222 onbit0/1 latchesB20F and
   clearsB196. Route new state before publishing;22 does not self-clear. Numeric software phases,
   not OEM failure labels. otherwise0→33 onbit4 and33→0 onbit2.11→22 onbit0/1 latchesB20F and
   clearsB196. Native majority-repaired11→22 closes receive qualification, latches completion and
   invokes request2 route before publication. */

undefined4 f33_advance_qualified_health_state(void)

{
  byte bVar1;
  uint32_t puVar2;
  int iVar3;
  uchar uStack_11;
  
  puVar2 = 0xfebeb800u;
  iVar3 = FUN_000d23b8(((undefined *)camry_host_ptr(0xfebeb20eu)),((undefined *)camry_host_ptr(0xfebeb20cu)),((undefined *)camry_host_ptr(0xfebeb20du)),&uStack_11);
  if (iVar3 == -0xd) {
    uStack_11 = '\0';
  }
  bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x638)))));
  if (uStack_11 == '\0') {
    if (((bVar1 >> 3 & 1) == 0) && ((bVar1 >> 5 & 1) == 0)) {
      if ((bVar1 >> 4 & 1) != 0) {
        uStack_11 = '3';
      }
      goto LAB_000b508e;
    }
  }
  else {
    if (uStack_11 != '3') {
      if ((uStack_11 == '\x11') && (((bVar1 & 1) != 0 || ((bVar1 >> 1 & 1) != 0)))) {
        uStack_11 = '\"';
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x5f1))))) = 0x5a;
        f33_close_health_receive_generation_qualification();
      }
      goto LAB_000b508e;
    }
    if (((bVar1 >> 3 & 1) == 0) && ((bVar1 >> 5 & 1) == 0)) {
      if ((bVar1 >> 2 & 1) != 0) {
        uStack_11 = '\0';
      }
      goto LAB_000b508e;
    }
  }
  uStack_11 = '\x11';
LAB_000b508e:
  f33_route_qualified_health_mode_requests(uStack_11);
  return FUN_000d268c(uStack_11,((undefined *)camry_host_ptr(0xfebeb20eu)),((undefined *)camry_host_ptr(0xfebeb20cu)),((undefined *)camry_host_ptr(0xfebeb20du)));
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_b50a8(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_b50aa(void)

{
  return;
}



void FUN_000b50ac(void)

{
  if (((((DAT_febef204 != -0x5aa5a55b) || (DAT_febef210 != -0x5aa5a55b)) ||
       (DAT_febef214 != -0x5aa5a55b)) ||
      ((DAT_febef20c != -0x5aa5a55b || (DAT_febef21c != -0x5aa5a55b)))) ||
     (DAT_febeb218 = DAT_febef208, DAT_febef208 != -0x5aa5a55b)) {
    if (((DAT_febef204 == 0x5aa5a55a) || (DAT_febef210 == 0x5aa5a55a)) ||
       ((DAT_febef214 == 0x5aa5a55a ||
        (((DAT_febef20c == 0x5aa5a55a || (DAT_febef21c == 0x5aa5a55a)) ||
         (DAT_febef208 == 0x5aa5a55a)))))) {
      DAT_febeb218 = 0x5aa5a55a;
    }
    else if (((DAT_febef204 == 0) || (DAT_febef210 == 0)) ||
            ((DAT_febef214 == 0 ||
             (((DAT_febef20c == 0 || (DAT_febef21c == 0)) || (DAT_febef208 == 0)))))) {
      DAT_febeb218 = 0;
    }
    else {
      DAT_febeb218 = -1;
    }
  }
  return;
}



void FUN_000b5120(void)

{
  if (((((DAT_febeb314 == -1) || (DAT_febeb300 == '\"')) || (DAT_febeb474 == -1)) ||
      ((DAT_febeb45f == '\"' || (DAT_febeb478 == -1)))) || (DAT_febeb32f == '\"')) {
    DAT_febeb21c = 0x5aa5a55a;
  }
  else if ((((DAT_febeb314 == 0x55aaaa55) || (DAT_febeb314 == -0x55aaaa56)) &&
           ((DAT_febeb474 == 0x55aaaa55 || (DAT_febeb474 == -0x55aaaa56)))) &&
          ((DAT_febeb478 == 0x55aaaa55 || (DAT_febeb478 == -0x55aaaa56)))) {
    DAT_febeb21c = 0xa55a5aa5;
  }
  else if ((DAT_febeb314 == 0x33333333) ||
          ((DAT_febeb474 == 0x33333333 || (DAT_febeb478 == 0x33333333)))) {
    DAT_febeb21c = 0;
  }
  else {
    DAT_febeb21c = 0xffffffff;
  }
  return;
}



void FUN_000b51a8(void)

{
  DAT_febeb215 = 0;
  if (DAT_febeb2d0 == '\"') {
    DAT_febeb215 = 0x5a;
  }
  return;
}



/* B214=11waitsB311/B471/B256;all44success,otherterminalfail;selector9. */

void f33_monitor_routine_1106_lifecycle_groups(void)

{
  uint32_t puVar1;
  char cVar2;
  
  puVar1 = 0xfebeb800u;
  cVar2 = DAT_febeb214;
  if (DAT_febeb214 == '\x11') {
    if (((DAT_febeb311 == 'D') && (DAT_febeb471 == 'D')) && (DAT_febeb256 == 'D')) {
      puVar1 = 0xfebeb800u;
      thunk_FUN_0004d0a4(9,0);
      cVar2 = '\"';
    }
    else if ((((DAT_febeb311 != '\x11') && (DAT_febeb311 != '\"')) &&
             ((DAT_febeb471 != '\x11' && ((DAT_febeb471 != '\"' && (DAT_febeb256 != '\x11')))))) &&
            (DAT_febeb256 != '\"')) {
      puVar1 = 0xfebeb800u;
      thunk_FUN_0004d0a4(9,0x20);
      cVar2 = 'D';
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5ec))))) = cVar2;
  return;
}



/* Sequential initializer chain: 4 unconditional calls and no other statements; shape-verified. The
   called sequence is the function's entire behavior; chain family members differ in callee sets. */

void f33_run_init_chain_b5232(void)

{
  FUN_000b50ac();
  FUN_000b5120();
  FUN_000b51a8();
  f33_monitor_routine_1106_lifecycle_groups();
  return;
}



void FUN_000b524a(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  FUN_000b5ec6();
  FUN_000b707a();
  FUN_000b8fa8();
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5ec))))) = 0x11;
  return;
}



/* Constant-block fill: 10 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_b5266(void)

{
  DAT_febeb24c = 0;
  DAT_febeb24f = 0;
  DAT_febeb251 = 0;
  DAT_febeb24d = DAT_000aeba8;
  DAT_febeb252 = 0;
  DAT_febeb25a = 0;
  DAT_febeb26c = 0;
  DAT_febeb25c = 0;
  DAT_febeb24e = DAT_000aebb8;
  DAT_febeb250 = 0x5a;
  return;
}



void FUN_000b5294(void)

{
  int iVar1;
  int iVar2;
  undefined4 *puVar3;
  int iVar4;
  undefined4 uVar5;
  undefined1 uVar6;
  undefined4 *puVar7;
  undefined4 local_18 [2];
  undefined1 uStack_10;
  undefined1 uStack_f;
  undefined1 uStack_e;
  undefined1 uStack_d;
  undefined1 uStack_c;
  undefined1 uStack_a;
  
  puVar3 = local_18;
  puVar7 = ((undefined *)camry_host_ptr(0x1bdfcu));
  do {
    uVar5 = *puVar7;
    puVar7 = puVar7 + 1;
    *puVar3 = uVar5;
    puVar3 = puVar3 + 1;
  } while ((uintptr_t)(puVar7)!=(uintptr_t)(((undefined *)camry_host_ptr(0x1be0cu))));
  if (DAT_febeb252 == 'D') {
    iVar4 = FUN_000ff0b0(0x101,local_18);
    if (iVar4 == 0x10) {
      iVar4 = 0;
      do {
        switch(iVar4) {
        case 0:
          uVar6 = uStack_10;
          break;
        case 1:
          uVar6 = uStack_f;
          break;
        case 2:
          uVar6 = uStack_e;
          break;
        case 3:
          uVar6 = uStack_d;
          break;
        case 4:
          uVar6 = uStack_c;
          break;
        case 5:
          uVar6 = uStack_a;
          break;
        default:
          uVar6 = 0xff;
        }
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb25fu + (uint32_t)(iVar4) * 1u)))) = uVar6;
        iVar2 = iVar4 + 1;
        iVar1 = iVar4 + -0xc;
        iVar4 = iVar2;
      } while (((iVar1 < 0) || (iVar2 < 0)));
    }
  }
  else {
    iVar4 = 0;
    do {
      iVar2 = iVar4 + 1;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb25fu + (uint32_t)(iVar4) * 1u)))) = 0xff;
      iVar1 = iVar4 + -0xc;
      iVar4 = iVar2;
    } while (((iVar1 < 0) || (iVar2 < 0)));
  }
  return;
}



void FUN_000b532a(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febeb252 = 0x44;
  DAT_febeb24c = 0;
  DAT_febeb25a = 0x44;
  DAT_febeb24d = DAT_000aeba8;
  DAT_febeb24e = DAT_000aebb8;
  f33_report_diagnostic_healthy_observed(0x129);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5b0))))) = 0x5a;
  FUN_000b5294();
  return;
}



void FUN_000b5368(void)

{
  undefined1 uVar1;
  uint32_t puVar2;
  char cVar3;
  
  puVar2 = 0xfebeb800u;
  cVar3 = DAT_febeb255;
  if (DAT_febeb255 == '\x11') {
    puVar2 = 0xfebeb800u;
    thunk_FUN_0004d0a4(0x13,0);
    cVar3 = 'D';
  }
  f33_report_diagnostic_healthy_observed(0x129);
  thunk_FUN_000524be(0xbe);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x5ae))))) = 0x44;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x5a6))))) = 0x44;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x5b4))))) = 0;
  uVar1 = DAT_000aeba8;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x5ab))))) = cVar3;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x5b3))))) = uVar1;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x5b2))))) = DAT_000aebb8;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x5b0))))) = 0x5a;
  return;
}



void FUN_000b53c2(void)

{
  FUN_000b5368();
  FUN_000b5294();
  return;
}



void FUN_000b53d2(void)

{
  undefined1 uVar1;
  undefined1 uVar2;
  undefined4 *puVar3;
  undefined *puVar4;
  int iVar5;
  undefined4 uVar6;
  undefined1 uVar7;
  undefined1 uVar8;
  undefined4 *puVar9;
  undefined4 local_24;
  byte bStack_20;
  
  uVar2 = DAT_febeb24e;
  uVar1 = DAT_febeb24d;
  puVar4 = ((undefined *)camry_host_ptr(0xfebeb800u));
  puVar3 = &local_24;
  puVar9 = ((undefined *)camry_host_ptr(0x1be0cu));
  do {
    uVar6 = *puVar9;
    puVar9 = puVar9 + 1;
    *puVar3 = uVar6;
    puVar3 = puVar3 + 1;
  } while ((uintptr_t)(puVar9)!=(uintptr_t)(((undefined *)camry_host_ptr(0x1be1cu))));
  uVar8 = DAT_000aeba8;
  uVar7 = DAT_000aebb8;
  if ((DAT_febeb252 == 'D') &&
     (puVar4 = ((undefined *)camry_host_ptr(0xfebeb800u)), iVar5 = FUN_000ff0b0(0x101,&local_24), uVar8 = uVar1, uVar7 = uVar2,
     iVar5 == 0x10)) {
    uVar8 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xaeba8u + (uint32_t)(bStack_20) * 1u))));
    uVar7 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xaebb8u + (uint32_t)(bStack_20) * 1u))));
  }
  puVar4[-0x5b3] = uVar8;
  puVar4[-0x5b2] = uVar7;
  return;
}



void FUN_000b5440(uint param_1,uint param_2)

{
  int iVar1;
  byte bVar2;
  uint uVar3;
  
  bVar2 = DAT_000aeb88;
  if ((param_1 & 0xff) < 2) {
    uVar3 = 0;
    do {
      if ((bVar2 >> (uVar3 & 0x1f) & 1) != 0) {
        iVar1 = (uVar3 + (param_1 & 0xff) * 4) * 4;
        if (((param_2 & 0xff) >> (uVar3 & 0x1f) & 1) == 0) {
          thunk_FUN_000524be(*(undefined2 *)(((undefined *)camry_host_ptr(0xaebc8u)) + iVar1));
        }
        else {
          thunk_FUN_00051d38(*(undefined2 *)(((undefined *)camry_host_ptr(0xaebc8u)) + iVar1),(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xaebcau + (uint32_t)(iVar1) * 1u)))),0x32);
        }
      }
      uVar3 = uVar3 + 1;
    } while (uVar3 < 4);
  }
  return;
}



void FUN_000b5498(void)

{
  char cVar1;
  undefined1 uVar2;
  uint32_t puVar3;
  undefined4 uVar4;
  uint uVar5;
  undefined1 uVar6;
  undefined1 uVar7;
  undefined1 uVar8;
  ushort uVar9;
  uint uVar10;
  undefined1 uVar11;
  char cVar12;
  
  uVar9 = DAT_febeb26c;
  uVar2 = DAT_febeb25d;
  uVar6 = DAT_febeb25a;
  cVar1 = DAT_febeb259;
  uVar7 = DAT_febeb257;
  cVar12 = DAT_febeb254;
  uVar8 = DAT_febeb253;
  uVar11 = DAT_febeb252;
  puVar3 = 0xfebeb800u;
  uVar10 = (uint)DAT_febeb26c;
  if (DAT_febeb254 == '\x11') {
    if ((DAT_febeb255 != '\"') && (DAT_febeb256 != '\"')) {
      puVar3 = 0xfebeb800u;
      FUN_000ff09c(0x101,((undefined *)camry_host_ptr(0xfebeb220u)));
      cVar12 = '\"';
    }
  }
  else if (DAT_febeb254 == '\"') {
    puVar3 = 0xfebeb800u;
    uVar5 = FUN_000ff0c4(0x101);
    if (uVar5 == 0x10) {
      if ((int)uVar10 >> 8 == 0x22) {
        uVar11 = 0x44;
        f33_report_diagnostic_event_pass(0xbe);
        uVar9 = 0x8822;
      }
      else {
        uVar11 = 0x11;
        thunk_FUN_00051d38(0xbe,0xc,0x32);
        uVar9 = 0x8844;
      }
      FUN_000b5440(0,uVar2);
      FUN_000b5440(1,0);
      uVar4 = 0;
      if (cVar1 == 'Z') {
        uVar4 = 0xff;
      }
      FUN_000b60d0(1,uVar4);
      FUN_000b60d0(3,0);
      uVar8 = 0;
      uVar7 = 0;
      cVar12 = 'D';
      uVar6 = uVar11;
    }
    else if ((uVar5 & 0xf0) != 0x20) {
      f33_report_diagnostic_event_failure(0x131,0x32);
      uVar9 = 0x8844;
      cVar12 = -0x78;
      uVar11 = 0x22;
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x5ac))))) = cVar12;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x5ae))))) = uVar11;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x5ad))))) = uVar8;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x5a9))))) = uVar7;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x5a6))))) = uVar6;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x594)))) = uVar9;
  return;
}



uint FUN_000b5586(void)

{
  undefined4 local_14;
  undefined1 uStack_10;
  undefined1 uStack_f;
  undefined2 uStack_e;
  undefined1 uStack_c;
  undefined1 uStack_b;
  undefined1 uStack_a;
  undefined1 uStack_9;
  undefined1 uStack_8;
  undefined1 uStack_7;
  undefined1 uStack_6;
  undefined1 uStack_5;
  
  uStack_f = 0;
  uStack_e = 0xa55a;
  uStack_10 = DAT_febeb25e;
  local_14 = 0xa55a5aa5;
  uStack_c = 0;
  uStack_b = 0;
  uStack_a = 0;
  uStack_9 = 0;
  uStack_8 = 0;
  uStack_7 = 0;
  uStack_6 = 0;
  uStack_5 = 0;
  return FUN_000ff09c(0x101,&local_14);
}



void FUN_000b55c0(void)

{
  uint32_t puVar1;
  uint uVar2;
  char cVar3;
  undefined1 uVar4;
  undefined1 uVar5;
  char cVar6;
  char cVar7;
  
  cVar3 = DAT_febeb25a;
  uVar4 = DAT_febeb257;
  cVar7 = DAT_febeb255;
  uVar5 = DAT_febeb253;
  cVar6 = DAT_febeb252;
  puVar1 = 0xfebeb800u;
  if (DAT_febeb255 == '\x11') {
    if ((DAT_febeb254 != '\"') && (DAT_febeb256 != '\"')) {
      puVar1 = 0xfebeb800u;
      FUN_000b5586();
      cVar7 = '\"';
    }
  }
  else if (DAT_febeb255 == '\"') {
    puVar1 = 0xfebeb800u;
    uVar2 = FUN_000ff0c4(0x101);
    if (uVar2 == 0x10) {
      cVar6 = 'D';
      f33_report_diagnostic_event_pass(0xbe);
      FUN_000b5440(0,0);
      FUN_000b5440(1,0);
      FUN_000b60d0(1,0);
      FUN_000b60d0(3,0);
      uVar5 = 0;
      thunk_FUN_0004d0a4(0x13,0);
      uVar4 = 0x5a;
      cVar7 = cVar6;
      cVar3 = cVar6;
    }
    else if ((uVar2 & 0xf0) != 0x20) {
      f33_report_diagnostic_event_failure(0x131,0x32);
      thunk_FUN_0004d0a4(0x13,0x20);
      cVar7 = -0x78;
      cVar6 = '\"';
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5ae))))) = cVar6;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5ad))))) = uVar5;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5ab))))) = cVar7;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5a9))))) = uVar4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5a6))))) = cVar3;
  return;
}



uint FUN_000b5682(void)

{
  undefined4 local_14;
  undefined1 uStack_10;
  undefined1 uStack_f;
  undefined2 uStack_e;
  undefined1 uStack_c;
  undefined1 uStack_b;
  undefined1 uStack_a;
  undefined1 uStack_9;
  undefined1 uStack_8;
  undefined1 uStack_7;
  undefined1 uStack_6;
  undefined1 uStack_5;
  
  uStack_10 = 0;
  uStack_f = 0;
  uStack_e = 0;
  local_14 = 0;
  uStack_c = 0;
  uStack_b = 0;
  uStack_a = 0;
  uStack_9 = 0;
  uStack_8 = 0;
  uStack_7 = 0;
  uStack_6 = 0;
  uStack_5 = 0;
  return FUN_000ff09c(0x101,&local_14);
}



void FUN_000b56ae(void)

{
  uint32_t puVar1;
  uint uVar2;
  undefined1 uVar3;
  undefined1 uVar4;
  undefined1 uVar5;
  undefined1 uVar6;
  char cVar7;
  
  uVar3 = DAT_febeb25a;
  uVar4 = DAT_febeb257;
  cVar7 = DAT_febeb256;
  uVar5 = DAT_febeb253;
  uVar6 = DAT_febeb252;
  puVar1 = 0xfebeb800u;
  if (DAT_febeb256 == '\x11') {
    if ((DAT_febeb254 != '\"') && (DAT_febeb255 != '\"')) {
      puVar1 = 0xfebeb800u;
      FUN_000b5682();
      cVar7 = '\"';
    }
  }
  else if (DAT_febeb256 == '\"') {
    puVar1 = 0xfebeb800u;
    uVar2 = FUN_000ff0c4(0x101);
    if (uVar2 == 0x10) {
      uVar6 = 0x11;
      uVar4 = 0;
      thunk_FUN_00051d38(0xbe,0xc,0x32);
      FUN_000b5440(0,0);
      FUN_000b5440(1,0);
      FUN_000b60d0(1,0);
      FUN_000b60d0(3,0);
      uVar5 = 0;
      cVar7 = 'D';
      uVar3 = uVar6;
    }
    else if ((uVar2 & 0xf0) != 0x20) {
      f33_report_diagnostic_event_failure(0x131,0x32);
      cVar7 = -0x78;
      uVar6 = 0x22;
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5aa))))) = cVar7;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5ae))))) = uVar6;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5ad))))) = uVar5;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5a9))))) = uVar4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5a6))))) = uVar3;
  return;
}



undefined4 FUN_000b5760(uint param_1,char param_2)

{
  char *pcVar1;
  uint uVar2;
  
  uVar2 = 0;
  while( true ) {
    if ((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xaeb8au + (uint32_t)(param_1 & 0xff) * 1u)))) <= uVar2) {
      return 0;
    }
    pcVar1 = ((void *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xaebe8u + (uint32_t)(param_1 & 0xff) * 4u)))) + uVar2 * 8)));
    if ((*pcVar1 == 'Z') || (param_2 == pcVar1[1])) break;
    uVar2 = uVar2 + 1 & 0xff;
  }
  return *(undefined4 *)(pcVar1 + 4);
}



void FUN_000b57a4(uint param_1,byte *param_2,byte param_3,char param_4)

{
  int iVar1;
  byte bVar2;
  byte bVar3;
  byte bVar4;
  byte bVar5;
  undefined1 extraout_r9;
  int iVar6;
  undefined1 uVar7;
  byte bVar8;
  byte bVar9;
  char cVar10;
  
  param_1 = param_1 & 0xff;
  iVar1 = param_1 * 4;
  uVar7 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb233u + (uint32_t)(iVar1) * 1u))));
  cVar10 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb230u + (uint32_t)(iVar1) * 1u))));
  bVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb232u + (uint32_t)(iVar1) * 1u))));
  bVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb231u + (uint32_t)(iVar1) * 1u))));
  iVar6 = (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebeb270u + (uint32_t)(param_1) * 4u))));
  bVar8 = bVar3;
  bVar9 = bVar2;
  if (((int8_t)cVar10) != -1) {
    if ((param_3 & DAT_000aeb89) == 0) {
      cVar10 = -1;
      iVar6 = FUN_000b5760(param_1,0xff);
      uVar7 = 0;
      bVar9 = 0xff;
    }
    else {
      bVar4 = param_2[1];
      bVar5 = param_2[2];
      bVar8 = bVar4;
      if ((*param_2 & 1) == 0) {
        bVar8 = bVar3;
      }
      if ((bVar4 != bVar8) && (bVar9 = bVar5, (byte)(bVar4 - bVar8) != 1)) {
        if (bVar2 == bVar5) {
          bVar9 = bVar2;
          if (DAT_000aecd8 <= (byte)(bVar4 - bVar8)) {
            if (param_4 == 'Z') {
              cVar10 = -1;
              iVar6 = FUN_000b5760(param_1,bVar2);
              uVar7 = extraout_r9;
              if (iVar6 != 0) {
                uVar7 = 0;
              }
            }
            else {
              iVar6 = FUN_000b5760(param_1,bVar2);
              if (iVar6 == 0) {
                cVar10 = '\0';
                bVar8 = bVar4;
                bVar9 = bVar5;
              }
              else {
                uVar7 = 0;
                cVar10 = -1;
              }
            }
          }
        }
        else {
          cVar10 = '\0';
          bVar8 = bVar4 - 1;
        }
      }
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb231u + (uint32_t)(iVar1) * 1u)))) = bVar8;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb232u + (uint32_t)(iVar1) * 1u)))) = bVar9;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb230u + (uint32_t)(iVar1) * 1u)))) = cVar10;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb233u + (uint32_t)(iVar1) * 1u)))) = uVar7;
  (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebeb270u + (uint32_t)(param_1) * 4u)))) = iVar6;
  return;
}



void FUN_000b5868(uint param_1,int param_2)

{
  int iVar1;
  undefined1 uVar2;
  
  iVar1 = (param_1 & 0xff) * 4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb230u + (uint32_t)(iVar1) * 1u)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb231u + (uint32_t)(iVar1) * 1u)))) = (*((undefined1 *)camry_host_ptr((uint32_t)(param_2 + 1))));
  uVar2 = (*((undefined1 *)camry_host_ptr((uint32_t)(param_2 + 2))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb233u + (uint32_t)(iVar1) * 1u)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb232u + (uint32_t)(iVar1) * 1u)))) = uVar2;
  return;
}



void FUN_000b5910(undefined1 param_1)

{
  undefined1 uStack_b;
  undefined1 uStack_a;
  undefined1 uStack_9;
  
  uStack_b = 1;
  uStack_a = 0;
  uStack_9 = 0xff;
  FUN_000b57a4(0,&uStack_b,1,param_1);
  uStack_b = 1;
  uStack_a = 0;
  uStack_9 = 0xff;
  FUN_000b57a4(1,&uStack_b,2,param_1);
  uStack_b = 1;
  uStack_a = 0;
  uStack_9 = 0xff;
  FUN_000b57a4(2,&uStack_b,4,param_1);
  uStack_b = 1;
  uStack_a = 0;
  uStack_9 = 0xff;
  FUN_000b57a4(3,&uStack_b,8,param_1);
  uStack_b = 1;
  uStack_a = 0;
  uStack_9 = 0xff;
  FUN_000b57a4(4,&uStack_b,0x10,param_1);
  uStack_b = 1;
  uStack_a = 0;
  uStack_9 = 0xff;
  FUN_000b57a4(5,&uStack_b,0x20,param_1);
  uStack_b = 1;
  uStack_a = 0;
  uStack_9 = 0xff;
  FUN_000b57a4(6,&uStack_b,0x40,param_1);
  return;
}



void FUN_000b59d8(void)

{
  if ((DAT_febeb24f != 'Z') &&
     (DAT_febeb24f = '\0',
     (byte)(DAT_febeb248 & 0x40 |
            DAT_febeb244 & 0x20 |
            DAT_febeb240 & 0x10 |
            DAT_febeb23c & 8 | DAT_febeb238 & 4 | DAT_febeb234 & 2 | DAT_febeb230 & 1 | 0x80) ==
     0xff)) {
    DAT_febeb24f = 'Z';
  }
  return;
}



undefined4 FUN_000b5a36(void)

{
  char cVar1;
  char cVar2;
  char cVar3;
  uint32_t puVar4;
  int iVar5;
  undefined4 uVar6;
  
  cVar3 = DAT_febeb43c;
  cVar2 = DAT_febeb43b;
  cVar1 = DAT_febeb24f;
  puVar4 = 0xfebeb800u;
  iVar5 = FUN_000b6a28();
  if (((iVar5 == 0) || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x533))))) != '\0')) &&
     ((cVar1 == 'Z' || ((cVar3 == 'Z' || (cVar2 == 'Z')))))) {
    uVar6 = 0x5a;
  }
  else {
    uVar6 = 0;
  }
  return uVar6;
}



undefined4 FUN_000b5a74(uint param_1)

{
  undefined4 uVar1;
  
  param_1 = param_1 & 0xff;
  uVar1 = 0;
  if ((param_1 < 0x10) && ((param_1 == 1 || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xaeba8u + (uint32_t)(param_1) * 1u)))) != DAT_000aeba8)))) {
    uVar1 = 1;
  }
  return uVar1;
}



undefined4 FUN_000b5a98(uint param_1,undefined1 *param_2)

{
  uint uVar1;
  uint32_t puVar2;
  undefined1 *extraout_r7;
  int iVar3;
  undefined4 uVar4;
  undefined1 uVar5;
  uint uVar6;
  
  puVar2 = 0xfebeb800u;
  uVar6 = DAT_febeb288 &
          DAT_febeb284 & DAT_febeb280 & DAT_febeb27c & DAT_febeb278 & DAT_febeb274 & DAT_febeb270;
  param_1 = param_1 & uVar6;
  if (param_1 != 0) {
    uVar5 = 0;
    uVar1 = 0;
    do {
      if ((param_1 >> (uVar1 & 0x1f) & 1) != 0) {
        DAT_febeb258 = (undefined1)uVar1;
        uVar5 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xaeb98u + (uint32_t)(uVar1) * 1u))));
      }
      uVar1 = uVar1 + 1;
    } while (uVar1 < 0xd);
    puVar2 = 0xfebeb800u;
    iVar3 = FUN_000b5a74(uVar5);
    param_2 = extraout_r7;
    if (iVar3 == 1) {
      uVar4 = 0;
      goto LAB_000b5af2;
    }
  }
  uVar5 = 0;
  uVar4 = 0x5a;
LAB_000b5af2:
  *param_2 = uVar5;
  (*((uint *)camry_host_ptr((uint32_t)(puVar2 + -0x574)))) = uVar6;
  return uVar4;
}



int FUN_000b5afe(void)

{
  char cVar1;
  undefined1 uVar2;
  uint uVar3;
  uint32_t puVar4;
  undefined4 uVar5;
  int iVar6;
  byte bVar7;
  undefined1 uStack_9;
  
  puVar4 = 0xfebeb800u;
  bVar7 = 0;
  uVar3 = 0;
  do {
    if ((((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb230u + (uint32_t)(uVar3 * 4) * 1u))))) != -1) || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb233u + (uint32_t)(uVar3 * 4) * 1u)))) != '\0')) {
      bVar7 = bVar7 | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xaeb91u + (uint32_t)(uVar3) * 1u))));
    }
    uVar3 = uVar3 + 1;
  } while (uVar3 < 7);
  iVar6 = FUN_000b6a28();
  if (iVar6 == 0) {
    cVar1 = 'Z';
    uVar5 = 0xffffffff;
  }
  else {
    cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x533)))));
    uVar5 = (*((undefined4 *)camry_host_ptr((uint32_t)(puVar4 + -0x508))));
  }
  if ((bVar7 == 0) && (cVar1 == 'Z')) {
    iVar6 = FUN_000b5a98(uVar5,&uStack_9);
    if (iVar6 == 0x5a) {
      uVar2 = 0x5a;
      bVar7 = DAT_000aeb88;
    }
    else {
      uVar2 = 0;
    }
  }
  else {
    uStack_9 = 0;
    uVar2 = 0;
    iVar6 = 0x5a;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x5a3))))) = bVar7;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x5a7))))) = uVar2;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x5b4))))) = uStack_9;
  return iVar6;
}



void FUN_000b5b8c(char param_1)

{
  if (param_1 == '\x01') {
    DAT_febeb224 = DAT_febeb24c;
    DAT_febeb220 = 0xa55a5aa5;
    DAT_febeb228 = DAT_febeb232;
    DAT_febeb229 = DAT_febeb236;
    DAT_febeb22a = DAT_febeb23a;
    DAT_febeb22b = DAT_febeb23e;
    DAT_febeb22c = DAT_febeb242;
    DAT_febeb22d = DAT_febeb246;
    DAT_febeb22e = DAT_febeb24a;
  }
  else {
    DAT_febeb224 = 0;
    DAT_febeb22e = 0;
    DAT_febeb220 = 0;
    DAT_febeb228 = 0;
    DAT_febeb229 = 0;
    DAT_febeb22a = 0;
    DAT_febeb22b = 0;
    DAT_febeb22c = 0;
    DAT_febeb22d = 0;
  }
  DAT_febeb226 = 0;
  DAT_febeb225 = 0;
  DAT_febeb22f = 0;
  DAT_febeb254 = 0x11;
  return;
}



void FUN_000b5bf6(void)

{
  uint32_t puVar1;
  int iVar2;
  undefined2 uVar3;
  
  uVar3 = DAT_febeb26c;
  puVar1 = 0xfebeb800u;
  if (DAT_febeb257 == 'Z') {
    uVar3 = 0x8822;
  }
  else {
    if ((DAT_000aecda < DAT_febebede) || (f33_published_internal_source_admission_state != '\0')) {
      puVar1 = 0xfebeb800u;
      FUN_000b5886();
    }
    else {
      puVar1 = 0xfebeb800u;
      FUN_000b5910(0x5a);
      FUN_000b59d8();
    }
    iVar2 = FUN_000b5a36();
    if (iVar2 == 0x5a) {
      iVar2 = FUN_000b5afe();
      if (iVar2 == 0x5a) {
        FUN_000b5b8c(2);
        uVar3 = 0x4411;
      }
      else {
        FUN_000b5b8c(1);
        uVar3 = 0x2211;
      }
    }
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x594)))) = uVar3;
  return;
}



undefined4 FUN_000b5c6a(void)

{
  char cVar1;
  
  cVar1 = DAT_febeb24f;
  if ((((DAT_febeb25c != '\x11') || (cVar1 = DAT_febeb43d, DAT_febeb2ce == '\x11')) ||
      (DAT_febeb24f != 'Z')) && (cVar1 != 'Z')) {
    return 0;
  }
  return 0x5a;
}



void FUN_000b5ca2(void)

{
  char *pcVar1;
  char cVar2;
  undefined4 *puVar3;
  uint uVar4;
  uint32_t puVar5;
  char cVar6;
  int iVar7;
  int iVar8;
  undefined4 uVar9;
  byte bVar10;
  undefined4 *puVar11;
  char local_28;
  char acStack_27 [7];
  undefined4 local_20;
  char cStack_1c;
  char cStack_18;
  undefined1 uStack_17;
  undefined1 uStack_16;
  undefined1 uStack_15;
  undefined1 uStack_14;
  undefined1 uStack_13;
  undefined1 uStack_12;
  
  puVar5 = 0xfebeb800u;
  puVar11 = ((undefined *)camry_host_ptr(0x1be1cu));
  puVar3 = &local_20;
  do {
    uVar9 = *puVar11;
    puVar11 = puVar11 + 1;
    *puVar3 = uVar9;
    puVar3 = puVar3 + 1;
  } while ((uintptr_t)(puVar11)!=(uintptr_t)(((undefined *)camry_host_ptr(0x1be2cu))));
  FUN_000ff0b0(0x101,&local_20);
  bVar10 = 0;
  acStack_27[0] = cStack_18;
  acStack_27[1] = uStack_17;
  acStack_27[2] = uStack_16;
  acStack_27[3] = uStack_15;
  acStack_27[4] = uStack_14;
  acStack_27[5] = uStack_13;
  acStack_27[6] = uStack_12;
  uVar4 = 0;
  do {
    pcVar1 = ((undefined *)camry_host_ptr((uint32_t)(puVar5 + uVar4 * 4 + -0x5d0)));
    if (((*pcVar1 != -1) || (pcVar1[3] != '\0')) || (pcVar1[2] != acStack_27[uVar4])) {
      bVar10 = bVar10 | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xaeb91u + (uint32_t)(uVar4) * 1u))));
    }
    uVar4 = uVar4 + 1;
  } while (uVar4 < 7);
  iVar7 = FUN_000b6a28();
  if (iVar7 == 0) {
    cVar2 = 'Z';
    uVar9 = 0xffffffff;
    cVar6 = '\0';
  }
  else {
    cVar6 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x531)))));
    cVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x533)))));
    uVar9 = (*((undefined4 *)camry_host_ptr((uint32_t)(puVar5 + -0x508))));
  }
  if (bVar10 == 0) {
    iVar7 = 0;
    iVar8 = iVar7;
    if (((cVar6 == '\0') && (cVar2 == 'Z')) &&
       ((iVar8 = FUN_000b5a98(uVar9,&local_28), cStack_1c != local_28 || (iVar8 == 0x5a)))) {
      iVar7 = 0x5a;
      iVar8 = iVar7;
      bVar10 = DAT_000aeb88;
    }
  }
  else {
    iVar7 = 0;
    iVar8 = 0x5a;
  }
  FUN_000b5440(1,bVar10);
  uVar9 = 0;
  if (iVar7 == 0x5a) {
    uVar9 = 0xff;
  }
  FUN_000b60d0(3,uVar9);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x5a5))))) = bVar10;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x5a7))))) = (char)iVar7;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x5ad))))) = (char)iVar8;
  return;
}



void FUN_000b5dba(void)

{
  char cVar1;
  char cVar2;
  char cVar3;
  undefined1 uVar4;
  uint32_t puVar5;
  int iVar6;
  undefined1 uVar7;
  
  cVar3 = DAT_febeb25c;
  cVar2 = DAT_febeb257;
  cVar1 = DAT_febeb252;
  uVar7 = DAT_febeb250;
  puVar5 = 0xfebeb800u;
  if ((DAT_febeb252 == 'D') && (DAT_febeb257 != 'Z')) {
    if (f33_published_internal_source_admission_state == '\0') {
      uVar4 = 0;
      if (DAT_febeb25c == '\x11') {
        uVar4 = 0x5a;
      }
      puVar5 = 0xfebeb800u;
      FUN_000b5910(uVar4);
      FUN_000b59d8();
    }
    else {
      puVar5 = 0xfebeb800u;
      FUN_000b5886();
    }
    iVar6 = FUN_000b5c6a();
    if (iVar6 != 0x5a) {
LAB_000b5e34:
      uVar4 = 0x11;
      goto LAB_000b5e38;
    }
    FUN_000b5ca2();
    uVar7 = 0x5a;
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x5b1))))) == 'Z') {
LAB_000b5e2e:
      uVar7 = 0x5a;
      uVar4 = 0x22;
      goto LAB_000b5e38;
    }
  }
  else {
    FUN_000b5886();
    if (cVar1 == 'D') {
      if (cVar2 == 'Z') goto LAB_000b5e2e;
      goto LAB_000b5e34;
    }
  }
  uVar4 = 0x44;
LAB_000b5e38:
  if (cVar3 == '\x11') {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x5a4))))) = uVar4;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x5b0))))) = uVar7;
  return;
}



void FUN_000b5e4a(void)

{
  uint32_t puVar1;
  undefined1 uVar2;
  
  puVar1 = 0xfebeb800u;
  if (DAT_febeb26e < DAT_000aecdc) {
    DAT_febeb26e = DAT_febeb26e + 1;
  }
  else {
    DAT_febeb250 = 'Z';
  }
  if ((DAT_febeb26c & 0xff) == 0x11) {
    uVar2 = 1;
    if ((int)(uint)DAT_febeb26c >> 8 == 0x11) {
      puVar1 = 0xfebeb800u;
      FUN_000b5bf6();
    }
  }
  else if ((DAT_febeb250 == '\0') || (DAT_febeb25c == '\x11')) {
    uVar2 = 2;
    puVar1 = 0xfebeb800u;
    FUN_000b5dba();
  }
  else {
    uVar2 = 3;
    puVar1 = 0xfebeb800u;
    FUN_000b5886();
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5af))))) = uVar2;
  return;
}



/* Single constant publisher: DAT_febeb250 = 0x5a; Shape-classified from the canonical corpus; the
   target cell is not yet named, so the written state's meaning is unknown. */

void FUN_000b5eb0(void)

{
  DAT_febeb250 = 0x5a;
  return;
}



/* B5EBA..C4 onlystoresB255=11 andreturns1;incomingr6payloadunused. */

uint f33_request_record101_reset_write(void)

{
  DAT_febeb255 = 0x11;
  return 1;
}



/* Single constant publisher: DAT_febeb256 = 0x44; Shape-classified from the canonical corpus; the
   target cell is not yet named, so the written state's meaning is unknown. */

void FUN_000b5ec6(void)

{
  DAT_febeb256 = 0x44;
  return;
}



/* Constant source: return 1; shape-classified from the canonical corpus. Callers receive this
   literal directly; its meaning is not recovered. */

undefined4 f33_return_const_1_b5ed0(void)

{
  return 1;
}



/* Constant source: return 0xff; shape-classified from the canonical corpus. Callers receive this
   literal directly; its meaning is not recovered. */

undefined4 f33_return_const_ff_b5ed4(void)

{
  return 0xff;
}



/* Paired constant publisher: DAT_febeb26c = 0x8822; and DAT_febeb25d = 0;; shape-classified from
   the canonical corpus. Target cells not yet named. */

void FUN_000b5eda(void)

{
  DAT_febeb26c = 0x8822;
  DAT_febeb25d = 0;
  return;
}



void FUN_000b5f00(void)

{
  DAT_febeb25c = 0x22;
  DAT_febeb25b = 0;
  DAT_febeb250 = 0x5a;
  return;
}



/* Paired constant publisher: DAT_febeb2d4 = 0; and DAT_febeb2ce = 0;; shape-classified from the
   canonical corpus. Target cells not yet named. */

void FUN_000b5f28(void)

{
  DAT_febeb2d4 = 0;
  DAT_febeb2ce = 0;
  return;
}



undefined4 FUN_000b5f32(uint param_1,char param_2)

{
  char *pcVar1;
  uint uVar2;
  
  uVar2 = 0;
  while( true ) {
    if ((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xaec44u + (uint32_t)(param_1 & 0xff) * 1u)))) <= uVar2) {
      return 0;
    }
    pcVar1 = ((void *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xaec60u + (uint32_t)(param_1 & 0xff) * 4u)))) + uVar2 * 8)));
    if ((*pcVar1 == 'Z') || (param_2 == pcVar1[1])) break;
    uVar2 = uVar2 + 1 & 0xff;
  }
  return *(undefined4 *)(pcVar1 + 4);
}



void FUN_000b5f76(void)

{
  int iVar1;
  int iVar2;
  int *piVar3;
  uint32_t puVar4;
  uint uVar5;
  uint uVar6;
  uint uVar7;
  uint uVar8;
  uint uVar9;
  uint uVar10;
  uint uVar11;
  int iVar12;
  undefined1 uVar13;
  undefined1 uVar14;
  undefined1 uVar15;
  undefined1 uVar16;
  undefined1 uVar17;
  undefined1 uVar18;
  undefined1 uVar19;
  undefined1 uVar20;
  undefined1 uVar21;
  int *piVar22;
  uint auStack_5c [4];
  uint uStack_4c;
  uint uStack_48;
  uint uStack_44;
  uint uStack_40;
  int local_3c [2];
  undefined1 local_34;
  undefined1 uStack_33;
  undefined1 uStack_32;
  undefined1 uStack_31;
  undefined1 uStack_30;
  undefined1 uStack_2f;
  undefined1 uStack_2e;
  undefined1 uStack_2d;
  
  uVar14 = DAT_febeb2c7;
  uVar15 = DAT_febeb2c6;
  uVar16 = DAT_febeb2c5;
  uVar17 = DAT_febeb2c4;
  uVar18 = DAT_febeb2c3;
  uVar19 = DAT_febeb2c2;
  uVar20 = DAT_febeb2c1;
  uVar21 = DAT_febeb2c0;
  puVar4 = 0xfebeb800u;
  piVar22 = ((undefined *)camry_host_ptr(0x1be2cu));
  piVar3 = local_3c;
  do {
    iVar12 = *piVar22;
    piVar22 = piVar22 + 1;
    *piVar3 = iVar12;
    piVar3 = piVar3 + 1;
  } while ((uintptr_t)(piVar22)!=(uintptr_t)(((undefined *)camry_host_ptr(0x1be3cu))));
  iVar12 = FUN_000ff0b0(0x103,local_3c);
  if (iVar12 == 0x10) {
    if ((local_3c[0] == 0) || (local_3c[0] != -0x5aa5a55b)) {
      uVar21 = 0xff;
      uVar13 = 0x33;
      uVar14 = uVar21;
      uVar15 = uVar21;
      uVar16 = uVar21;
      uVar17 = uVar21;
      uVar18 = uVar21;
      uVar19 = uVar21;
      uVar20 = uVar21;
    }
    else {
      uVar13 = 0x5a;
      uVar21 = local_34;
      uVar14 = uStack_2d;
      uVar15 = uStack_2e;
      uVar16 = uStack_2f;
      uVar17 = uStack_30;
      uVar18 = uStack_31;
      uVar19 = uStack_32;
      uVar20 = uStack_33;
    }
  }
  else {
    uVar13 = 0xff;
    if (iVar12 == 0x11) {
      uVar13 = 0x33;
    }
  }
  uVar5 = FUN_000b5f32(0,uVar21);
  auStack_5c[0] = uVar5;
  uVar6 = FUN_000b5f32(1,uVar20);
  auStack_5c[1] = uVar6;
  uVar7 = FUN_000b5f32(2,uVar19);
  auStack_5c[2] = uVar7;
  uVar8 = FUN_000b5f32(3,uVar18);
  auStack_5c[3] = uVar8;
  uVar9 = FUN_000b5f32(4,uVar17);
  uStack_4c = uVar9;
  uVar10 = FUN_000b5f32(5,uVar16);
  uStack_48 = uVar10;
  uVar11 = FUN_000b5f32(6,uVar15);
  uStack_44 = uVar11;
  uStack_40 = FUN_000b5f32(7,uVar14);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x540))))) = uVar21;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x53f))))) = uVar20;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x53e))))) = uVar19;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x53d))))) = uVar18;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x53c))))) = uVar17;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x53b))))) = uVar16;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x53a))))) = uVar15;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x539))))) = uVar14;
  iVar12 = 0;
  do {
    iVar2 = iVar12 + 1;
    iVar1 = iVar12 + -7;
    *(uint *)(((undefined *)camry_host_ptr(0xfebeb2d8u)) + iVar12 * 4) = auStack_5c[iVar12];
    iVar12 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  (*((uint *)camry_host_ptr((uint32_t)(puVar4 + -0x508)))) = uStack_40 & uVar11 & uVar10 & uVar9 & uVar8 & uVar7 & uVar6 & uVar5;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x533))))) = uVar13;
  return;
}



void FUN_000b60d0(uint param_1,uint param_2)

{
  int iVar1;
  byte bVar2;
  uint uVar3;
  
  bVar2 = DAT_000aec5c;
  if ((param_1 & 0xff) < 4) {
    uVar3 = 0;
    do {
      if ((bVar2 >> (uVar3 & 0x1f) & 1) != 0) {
        iVar1 = (uVar3 + (param_1 & 0xff) * 2) * 4;
        if (((param_2 & 0xff) >> (uVar3 & 0x1f) & 1) == 0) {
          thunk_FUN_000524be(*(undefined2 *)(((undefined *)camry_host_ptr(0xaec80u)) + iVar1));
        }
        else {
          thunk_FUN_00051d38(*(undefined2 *)(((undefined *)camry_host_ptr(0xaec80u)) + iVar1),(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xaec82u + (uint32_t)(iVar1) * 1u)))),0x32);
        }
      }
      uVar3 = uVar3 + 1;
    } while (uVar3 < 2);
  }
  return;
}



void FUN_000b6128(void)

{
  if (DAT_febeb2cd == 'Z') {
    FUN_000b60d0(0,0);
  }
  return;
}



void FUN_000b6142(uint param_1,int param_2)

{
  int iVar1;
  undefined1 uVar2;
  
  iVar1 = (param_1 & 0xff) * 4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb290u + (uint32_t)(iVar1) * 1u)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb291u + (uint32_t)(iVar1) * 1u)))) = (*((undefined1 *)camry_host_ptr((uint32_t)(param_2 + 1))));
  uVar2 = (*((undefined1 *)camry_host_ptr((uint32_t)(param_2 + 2))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb293u + (uint32_t)(iVar1) * 1u)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb292u + (uint32_t)(iVar1) * 1u)))) = uVar2;
  return;
}



void FUN_000b61e0(void)

{
  FUN_000b5f76();
  FUN_000b6128();
  FUN_000b6160();
  return;
}



void FUN_000b61f4(uint param_1,byte *param_2,byte param_3)

{
  int iVar1;
  byte bVar2;
  byte bVar3;
  byte bVar4;
  int iVar5;
  undefined1 uVar6;
  byte bVar7;
  char cVar8;
  byte bVar9;
  
  param_1 = param_1 & 0xff;
  iVar1 = param_1 * 4;
  cVar8 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb290u + (uint32_t)(iVar1) * 1u))));
  bVar7 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb291u + (uint32_t)(iVar1) * 1u))));
  bVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb292u + (uint32_t)(iVar1) * 1u))));
  uVar6 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb293u + (uint32_t)(iVar1) * 1u))));
  bVar9 = bVar2;
  if (((int8_t)cVar8) != -1) {
    if ((param_3 & DAT_000aec5d) == 0) {
      cVar8 = -1;
      uVar6 = 0;
      bVar9 = 0xff;
    }
    else {
      bVar3 = param_2[1];
      bVar4 = param_2[2];
      if (((*param_2 & 1) != 0) || (bVar4 == (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xaec4cu + (uint32_t)(param_1) * 1u)))))) {
        bVar7 = bVar3;
      }
      if ((bVar3 != bVar7) && (bVar9 = bVar4, (byte)(bVar3 - bVar7) != 1)) {
        if (bVar2 == bVar4) {
          bVar9 = bVar2;
          if (DAT_000aece0 <= (byte)(bVar3 - bVar7)) {
            cVar8 = -1;
            iVar5 = FUN_000b5f32(param_1,bVar2);
            uVar6 = 0x5a;
            if (iVar5 != 0) {
              uVar6 = 0;
            }
          }
        }
        else {
          bVar7 = bVar3 - 1;
        }
      }
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb291u + (uint32_t)(iVar1) * 1u)))) = bVar7;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb292u + (uint32_t)(iVar1) * 1u)))) = bVar9;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb290u + (uint32_t)(iVar1) * 1u)))) = cVar8;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb293u + (uint32_t)(iVar1) * 1u)))) = uVar6;
  return;
}



void FUN_000b628e(void)

{
  undefined1 uStack_13;
  undefined1 uStack_12;
  undefined1 uStack_11;
  
  uStack_13 = 1;
  uStack_12 = 0;
  uStack_11 = 0xff;
  FUN_000b61f4(0,&uStack_13, 0x1);
  uStack_13 = 1;
  uStack_12 = 0;
  uStack_11 = 0xff;
  FUN_000b61f4(1,&uStack_13,2);
  uStack_13 = 1;
  uStack_12 = 0;
  uStack_11 = 0xff;
  FUN_000b61f4(2,&uStack_13,4);
  uStack_13 = 1;
  uStack_12 = 0;
  uStack_11 = 0xff;
  FUN_000b61f4(3,&uStack_13,8);
  uStack_13 = 1;
  uStack_12 = 0;
  uStack_11 = 0xff;
  FUN_000b61f4(4,&uStack_13,0x10);
  uStack_13 = 1;
  uStack_12 = 0;
  uStack_11 = 0xff;
  FUN_000b61f4(5,&uStack_13,0x20);
  uStack_13 = 1;
  uStack_12 = 0;
  uStack_11 = 0xff;
  FUN_000b61f4(6,&uStack_13,0x40);
  uStack_13 = 1;
  uStack_12 = 0;
  uStack_11 = 0xff;
  FUN_000b61f4(7,&uStack_13,0x80);
  return;
}



void FUN_000b6342(void)

{
  undefined1 uVar1;
  uint32_t puVar2;
  undefined1 uVar3;
  
  puVar2 = 0xfebeb800u;
  if (DAT_000aec5d == '\0') {
LAB_000b639c:
    uVar3 = 0x33;
    puVar2 = 0xfebeb800u;
    FUN_000b6160();
  }
  else {
    if (((char)DAT_febeb2d4 == '\x11') && (f33_published_internal_source_admission_state == '\0')) {
      uVar1 = 0x11;
    }
    else {
      if ((DAT_febeb2ce != '\x11') ||
         (((DAT_febeb257 != '\0' || (DAT_febeb1c9 != 'Z')) ||
          (f33_published_internal_source_admission_state != '\0')))) goto LAB_000b639c;
      uVar3 = 0x22;
      uVar1 = 0x22;
      if (DAT_febeb2cd != 'Z') goto LAB_000b63a4;
    }
    uVar3 = uVar1;
    puVar2 = 0xfebeb800u;
    FUN_000b628e();
  }
LAB_000b63a4:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x52f))))) = uVar3;
  return;
}



void FUN_000b63ac(char param_1)

{
  if (param_1 == '\x01') {
    DAT_febeb2b0 = 0xa55a5aa5;
    DAT_febeb2b8 = DAT_febeb292;
    DAT_febeb2b9 = DAT_febeb296;
    DAT_febeb2ba = DAT_febeb29a;
    DAT_febeb2bb = DAT_febeb29e;
    DAT_febeb2bc = DAT_febeb2a2;
    DAT_febeb2bd = DAT_febeb2a6;
    DAT_febeb2be = DAT_febeb2aa;
    DAT_febeb2bf = DAT_febeb2ae;
  }
  else {
    DAT_febeb2bf = 0xff;
    DAT_febeb2b8 = 0xff;
    DAT_febeb2b0 = 0;
    DAT_febeb2b9 = 0xff;
    DAT_febeb2ba = 0xff;
    DAT_febeb2bb = 0xff;
    DAT_febeb2bc = 0xff;
    DAT_febeb2bd = 0xff;
    DAT_febeb2be = 0xff;
  }
  DAT_febeb2b4 = 0;
  DAT_febeb2c8 = 0x11;
  return;
}



undefined2 FUN_000b6414(undefined2 param_1)

{
  uint uVar1;
  uint32_t puVar2;
  byte bVar3;
  
  puVar2 = 0xfebeb800u;
  if (((byte)(DAT_febeb2ac & 0x80 |
             DAT_febeb2a8 & 0x40 |
             DAT_febeb2a4 & 0x20 |
             DAT_febeb2a0 & 0x10 |
             DAT_febeb29c & 8 | DAT_febeb298 & 4 | DAT_febeb294 & 2 | DAT_febeb290 & 1) == 0xff) ||
     (bVar3 = DAT_febeb2d2, DAT_febeb43c == 'Z')) {
    bVar3 = 0;
    uVar1 = 0;
    do {
      if ((((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb290u + (uint32_t)(uVar1 * 4) * 1u))))) != -1) || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb293u + (uint32_t)(uVar1 * 4) * 1u)))) != '\0')) {
        bVar3 = bVar3 | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xaec54u + (uint32_t)(uVar1) * 1u))));
      }
      uVar1 = uVar1 + 1;
    } while (uVar1 < 8);
    puVar2 = 0xfebeb800u;
    if (bVar3 == 0) {
      FUN_000b63ac(1);
      param_1 = 0x2211;
    }
    else {
      FUN_000b63ac(2);
      param_1 = 0x4411;
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x52e))))) = bVar3;
  return param_1;
}



undefined ** FUN_000b64c8(uint param_1)

{
  uint32_t puVar1;
  undefined1 uVar2;
  undefined **ppuVar3;
  
  puVar1 = 0xfebeb800u;
  ppuVar3 = ((void *)camry_host_ptr((uint32_t)((undefined **)(param_1 & 0xffff))));
  uVar2 = DAT_febeb2d0;
  if (((DAT_febeb2c8 != '\0') && (DAT_febeb2c8 != '\x11')) && (DAT_febeb2c8 != '\"')) {
    puVar1 = 0xfebeb800u;
    if (DAT_febeb2c8 == 'D') {
      puVar1 = 0xfebeb800u;
      FUN_000b60d0(0,DAT_febeb2d2);
      FUN_000b60d0(2,0);
      uVar2 = 0;
      if ((int)camry_host_addr(ppuVar3) >> 8 == 0x22) {
        ppuVar3 = &PTR_LAB_00008822;
        goto LAB_000b6516;
      }
    }
    ppuVar3 = ((void *)camry_host_ptr((uint32_t)((undefined **)((undefined *)camry_host_ptr(0x8844u)))));
  }
LAB_000b6516:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x530))))) = uVar2;
  return ppuVar3;
}



void FUN_000b655e(void)

{
  uint32_t puVar1;
  uint uVar2;
  char cVar3;
  
  cVar3 = DAT_febeb2c8;
  puVar1 = 0xfebeb800u;
  if (DAT_febeb2c8 == '\x11') {
    if ((DAT_febeb2c9 != '\"') && (DAT_febeb2ca != '\"')) {
      puVar1 = 0xfebeb800u;
      FUN_000ff09c(0x103,((undefined *)camry_host_ptr(0xfebeb2b0u)));
      cVar3 = '\"';
    }
  }
  else if (DAT_febeb2c8 == '\"') {
    puVar1 = 0xfebeb800u;
    uVar2 = FUN_000ff0c4(0x103);
    if (uVar2 == 0x10) {
      cVar3 = 'D';
      FUN_000b5f76();
    }
    else if ((uVar2 & 0xf0) != 0x20) {
      cVar3 = -0x78;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x533))))) = 0xff;
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x538))))) = cVar3;
  return;
}



uint FUN_000b65ca(void)

{
  undefined4 local_14;
  undefined4 uStack_10;
  undefined1 uStack_c;
  undefined1 uStack_b;
  undefined1 uStack_a;
  undefined1 uStack_9;
  undefined1 uStack_8;
  undefined1 uStack_7;
  undefined1 uStack_6;
  undefined1 uStack_5;
  
  uStack_10 = 0;
  local_14 = 0;
  uStack_5 = 0xff;
  uStack_6 = 0xff;
  uStack_7 = 0xff;
  uStack_8 = 0xff;
  uStack_9 = 0xff;
  uStack_a = 0xff;
  uStack_b = 0xff;
  uStack_c = 0xff;
  return FUN_000ff09c(0x103,&local_14);
}



void FUN_000b65f4(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  FUN_000b60d0(0,0);
  FUN_000b60d0(1,0);
  FUN_000b60d0(2,0);
  FUN_000b60d0(3,0);
  FUN_000b6160();
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x530))))) = 0;
  return;
}



void FUN_000b6624(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  DAT_febeb2c0 = 0xff;
  DAT_febeb2c1 = 0xff;
  DAT_febeb2c2 = 0xff;
  DAT_febeb2c3 = 0xff;
  DAT_febeb2c4 = 0xff;
  DAT_febeb2c5 = 0xff;
  DAT_febeb2c6 = 0xff;
  DAT_febeb2c7 = 0xff;
  DAT_febeb2cd = 0x33;
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    *(undefined4 *)(((undefined *)camry_host_ptr(0xfebeb2d8u)) + iVar3 * 4) = 0;
    iVar1 = iVar3 + -7;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  DAT_febeb2f8 = 0;
  return;
}



/* B2C9states11\u219222\u219244/88;B65CAqueues103;FF0C4status10success/high20pending;selector6.
   B2C9states11→22→44/88;B65CAqueues103;FF0C4status10success/high20pending;selector6. */

void f33_monitor_routine_1009_record103_reset(void)

{
  uint32_t puVar1;
  uint uVar2;
  char cVar3;
  
  cVar3 = DAT_febeb2c9;
  puVar1 = 0xfebeb800u;
  if (DAT_febeb2c9 == '\x11') {
    if ((DAT_febeb2c8 != '\"') && (DAT_febeb2ca != '\"')) {
      puVar1 = 0xfebeb800u;
      FUN_000b65ca();
      cVar3 = '\"';
    }
  }
  else if (DAT_febeb2c9 == '\"') {
    puVar1 = 0xfebeb800u;
    uVar2 = FUN_000ff0c4(0x103);
    if (uVar2 == 0x10) {
      cVar3 = 'D';
      FUN_000b65f4();
      thunk_FUN_0004d0a4(6,0);
      FUN_000b6624();
    }
    else if ((uVar2 & 0xf0) != 0x20) {
      cVar3 = -0x78;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x533))))) = 0xff;
      thunk_FUN_0004d0a4(6,0x20);
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x537))))) = cVar3;
  return;
}



/* Copieslive8bytes,selector1..8 replacesone,magicA55A5AA5,FF09C103;sharedstagingnotqueue. */

void f33_submit_staged_record103_byte_write(void)

{
  undefined4 local_14;
  undefined4 uStack_10;
  undefined1 uStack_c;
  undefined1 uStack_b;
  undefined1 uStack_a;
  undefined1 uStack_9;
  undefined1 uStack_8;
  undefined1 uStack_7;
  undefined1 uStack_6;
  undefined1 uStack_5;
  
  uStack_c = DAT_febeb2c0;
  uStack_b = DAT_febeb2c1;
  uStack_a = DAT_febeb2c2;
  uStack_9 = DAT_febeb2c3;
  uStack_8 = DAT_febeb2c4;
  uStack_7 = DAT_febeb2c5;
  uStack_6 = DAT_febeb2c6;
  uStack_5 = DAT_febeb2c7;
  switch(DAT_febeb2cc) {
  case 1:
    uStack_c = DAT_febeb2cb;
    break;
  case 2:
    uStack_b = DAT_febeb2cb;
    break;
  case 3:
    uStack_a = DAT_febeb2cb;
    break;
  case 4:
    uStack_9 = DAT_febeb2cb;
    break;
  case 5:
    uStack_8 = DAT_febeb2cb;
    break;
  case 6:
    uStack_7 = DAT_febeb2cb;
    break;
  case 7:
    uStack_6 = DAT_febeb2cb;
    break;
  case 8:
    uStack_5 = DAT_febeb2cb;
  }
  local_14 = 0xa55a5aa5;
  uStack_10 = 0;
  FUN_000ff09c(0x103,&local_14);
  return;
}



/* 11->22 request whenpeerstatesnot22;pollrecord103;10->44reload/ack,20xwait,other88ackfailure. */

void f33_service_record103_byte_write(void)

{
  uint32_t puVar1;
  uint uVar2;
  char cVar3;
  
  cVar3 = DAT_febeb2ca;
  puVar1 = 0xfebeb800u;
  if (DAT_febeb2ca == '\x11') {
    if ((DAT_febeb2c8 != '\"') && (DAT_febeb2c9 != '\"')) {
      puVar1 = 0xfebeb800u;
      f33_submit_staged_record103_byte_write();
      cVar3 = '\"';
    }
  }
  else if (DAT_febeb2ca == '\"') {
    puVar1 = 0xfebeb800u;
    uVar2 = FUN_000ff0c4(0x103);
    if (uVar2 == 0x10) {
      cVar3 = 'D';
      FUN_000b65f4();
      thunk_FUN_0004d0a4(0x15,0);
      FUN_000b5f76();
    }
    else if ((uVar2 & 0xf0) != 0x20) {
      cVar3 = -0x78;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x533))))) = 0xff;
      thunk_FUN_0004d0a4(0x15,0x20);
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x536))))) = cVar3;
  return;
}



void FUN_000b67cc(void)

{
  int iVar1;
  byte bVar2;
  char cVar3;
  uint uVar4;
  uint32_t puVar5;
  undefined1 uVar6;
  byte bVar7;
  byte bVar8;
  char local_18 [8];
  
  bVar2 = DAT_000aec5c;
  puVar5 = 0xfebeb800u;
  uVar6 = DAT_febeb2d0;
  cVar3 = DAT_febeb2ce;
  bVar8 = DAT_febeb2cf;
  if (DAT_febeb2ce != '\x11') goto LAB_000b68fc;
  if (DAT_febeb257 == 'Z') {
    bVar8 = 0;
    puVar5 = 0xfebeb800u;
  }
  else {
    bVar7 = DAT_febeb2ac & 0x80 |
            DAT_febeb2a8 & 0x40 |
            DAT_febeb2a4 & 0x20 |
            DAT_febeb2a0 & 0x10 |
            DAT_febeb29c & 8 | DAT_febeb298 & 4 | DAT_febeb294 & 2 | DAT_febeb290 & 1;
    if (DAT_febeb2cd != 'Z') {
      puVar5 = 0xfebeb800u;
      FUN_000b60d0(2,DAT_000aec5c);
      uVar6 = 0x22;
      cVar3 = 'D';
      bVar8 = bVar2;
      goto LAB_000b68fc;
    }
    if ((bVar7 != 0xff) && (DAT_febeb43d != 'Z')) goto LAB_000b68fc;
    bVar8 = 0;
    local_18[0] = DAT_febeb2c0;
    local_18[1] = DAT_febeb2c1;
    local_18[2] = DAT_febeb2c2;
    local_18[3] = DAT_febeb2c3;
    local_18[4] = DAT_febeb2c4;
    local_18[5] = DAT_febeb2c5;
    local_18[6] = DAT_febeb2c6;
    local_18[7] = DAT_febeb2c7;
    uVar4 = 0;
    do {
      iVar1 = uVar4 * 4;
      if (((((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb290u + (uint32_t)(iVar1) * 1u))))) != -1) || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb293u + (uint32_t)(iVar1) * 1u)))) != '\0')) ||
         ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb292u + (uint32_t)(iVar1) * 1u)))) != local_18[uVar4])) {
        bVar8 = bVar8 | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xaec54u + (uint32_t)(uVar4) * 1u))));
      }
      uVar4 = uVar4 + 1;
    } while (uVar4 < 8);
    puVar5 = 0xfebeb800u;
    FUN_000b60d0(2,bVar8);
    uVar6 = 0x22;
    if (bVar8 == 0) {
      uVar6 = 0x11;
    }
    cVar3 = 'D';
    if (bVar7 != 0xff) goto LAB_000b68fc;
  }
  cVar3 = '\"';
LAB_000b68fc:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x532))))) = cVar3;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x531))))) = bVar8;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x530))))) = uVar6;
  return;
}



/* Sequential initializer chain: 6 unconditional calls and no other statements; shape-verified. The
   called sequence is the function's entire behavior; chain family members differ in callee sets. */

void f33_run_init_chain_b690a(void)

{
  FUN_000b6342();
  FUN_000b651e();
  FUN_000b655e();
  f33_monitor_routine_1009_record103_reset();
  f33_service_record103_byte_write();
  FUN_000b67cc();
  return;
}



/* WARNING: This is an inlined function */

void FUN_000b692a(void)

{
  bool bVar1;
  
  bVar1 = DAT_febeb2ce == '\x11';
  if (bVar1) {
    DAT_febeb2ce = '\0';
  }
  if (bVar1) {
    DAT_febeb2cf = 0xff;
  }
  return;
}



/* WARNING: Inlined function: FUN_000b692a */

void FUN_000b6944(void)

{
  bool bVar1;
  char cVar2;
  uint32_t puVar3;
  undefined1 uVar4;
  undefined1 uVar5;
  ushort uVar6;
  
  puVar3 = 0xfebeb800u;
  uVar4 = DAT_febeb2d2;
  uVar5 = DAT_febeb2cd;
  if (DAT_000aec5d == '\0') {
    uVar6 = 0x8822;
  }
  else if (((int)(uint)DAT_febeb2d4 >> 8 == 0) ||
          (uVar6 = DAT_febeb2d4, (int)(uint)DAT_febeb2d4 >> 8 == 0x88)) {
    uVar6 = 0x1111;
    puVar3 = 0xfebeb800u;
    FUN_000b6160();
    cVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x532)))));
    uVar4 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x531)))));
    bVar1 = cVar2 == '\x11';
    if (bVar1) {
      cVar2 = '\0';
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x532))))) = cVar2;
    if (bVar1) {
      uVar4 = 0xff;
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x531))))) = uVar4;
    uVar4 = 0;
    uVar5 = 0;
  }
  (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x52c)))) = uVar6;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x52e))))) = uVar4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x533))))) = uVar5;
  return;
}



/* WARNING: This is an inlined function */

void FUN_000b6990(void)

{
  if ((int)(uint)DAT_febeb2d4 >> 8 == 0x11) {
    DAT_febeb2d4 = 0x8822;
  }
  return;
}



/* WARNING: Inlined function: FUN_000b6990 */
/* WARNING: Inlined function: FUN_000b692a */
/* B69BEB69C0 stores incomingr6 selectoratB2CC,r7 valueB2CB. B6990/B692A preserveboth registers.
   Corpus void(void) losesABI. */

void f33_stage_record103_byte_write(uchar selector,uchar value)

{
  bool bVar1;
  
  if ((int)(uint)DAT_febeb2d4 >> 8 == 0x11) {
    DAT_febeb2d4 = 0x8822;
  }
  bVar1 = DAT_febeb2ce == '\x11';
  if (bVar1) {
    DAT_febeb2ce = '\0';
  }
  if (bVar1) {
    DAT_febeb2cf = 0xff;
  }
  DAT_febeb2ca = 0x11;
  DAT_febeb2cc = selector;
  DAT_febeb2cb = value;
  return;
}



/* WARNING: Inlined function: FUN_000b6990 */
/* WARNING: Inlined function: FUN_000b692a */

void FUN_000b69c6(void)

{
  bool bVar1;
  
  if ((int)(uint)DAT_febeb2d4 >> 8 == 0x11) {
    DAT_febeb2d4 = 0x8822;
  }
  bVar1 = DAT_febeb2ce == '\x11';
  if (bVar1) {
    DAT_febeb2ce = '\0';
  }
  if (bVar1) {
    DAT_febeb2cf = 0xff;
  }
  DAT_febeb2c9 = 0x11;
  return;
}



void FUN_000b69de(void)

{
  char cVar1;
  uint32_t puVar2;
  undefined1 uVar3;
  
  puVar2 = 0xfebeb800u;
  uVar3 = DAT_febeb2cf;
  if (DAT_000aec5d == '\0') {
    cVar1 = '\"';
  }
  else {
    cVar1 = DAT_febeb2ce;
    if (DAT_febeb2ce != '\x11') {
      if ((char)DAT_febeb2d4 == '\x11') {
        cVar1 = 'D';
      }
      else {
        puVar2 = 0xfebeb800u;
        FUN_000b6160();
        cVar1 = '\x11';
        uVar3 = 0;
      }
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x532))))) = cVar1;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x531))))) = uVar3;
  return;
}



undefined1 FUN_000b6a28(void)

{
  return DAT_000aec5d;
}



/* Single constant publisher: DAT_febeb302 = 0; Shape-classified from the canonical corpus; the
   target cell is not yet named, so the written state's meaning is unknown. */

void FUN_000b6a32(void)

{
  DAT_febeb302 = 0;
  return;
}



void FUN_000b6a38(void)

{
  DAT_febeb2fe = DAT_febef055;
  return;
}



void FUN_000b6a42(void)

{
  if (((DAT_febeb314 == 0) || (DAT_febeb314 == 0x33333333)) || (DAT_febeb314 == -1)) {
    DAT_febeb301 = 0;
    if (DAT_febeb2fc == 1) {
      DAT_febeb2fc = 2;
      DAT_febeb302 = 0x44;
    }
  }
  else if ((DAT_febeb2fc < 2) && (f33_published_internal_source_admission_state < 2)) {
    DAT_febeb301 = 0x5a;
  }
  else {
    DAT_febeb301 = 0;
  }
  return;
}



void FUN_000b6a8a(void)

{
  if ((DAT_febeb301 == 'Z') && (DAT_febebe89 == '\0')) {
    if (DAT_febeb2fe != DAT_febef055) {
      if (DAT_febeb2fd == 0) {
        DAT_febeb2fd = DAT_000aef50 != 0;
        DAT_febeb2ff = DAT_febebe88;
      }
      else if (DAT_febeb2ff == DAT_febebe88) {
        if (DAT_febeb2fd < DAT_000aef50) {
          DAT_febeb2fd = DAT_febeb2fd + 1;
        }
      }
      else {
        DAT_febeb2fd = 1;
        DAT_febeb2ff = DAT_febebe88;
      }
    }
  }
  else {
    DAT_febeb2fd = 0;
  }
  DAT_febeb2fe = DAT_febef055;
  return;
}



void FUN_000b6ae0(void)

{
  uint32_t puVar1;
  uint uVar2;
  undefined1 uVar3;
  undefined1 uVar4;
  char cVar5;
  
  uVar3 = DAT_febeb302;
  cVar5 = DAT_febeb2fc;
  puVar1 = 0xfebeb800u;
  if (DAT_febeb2fd < DAT_000aef50) {
    uVar4 = DAT_febeb300;
    if ((DAT_febeb2fc != '\x01') || (DAT_febeb43d != 'Z')) goto LAB_000b6b8c;
    uVar4 = 0x22;
    puVar1 = 0xfebeb800u;
    thunk_FUN_00051d38(0x100,0x14,100);
    uVar3 = 0x44;
  }
  else {
    puVar1 = 0xfebeb800u;
    if (((DAT_febeb314 == -0x55aaaa56) && (DAT_febeb2ff != 'Z')) ||
       ((DAT_febeb314 == 0x55aaaa55 && (DAT_febeb2ff != '\0')))) {
      uVar4 = 0x22;
      thunk_FUN_00051d38(0x100,0x14,100);
    }
    else {
      if (DAT_febeb2fc == '\x01') {
        puVar1 = 0xfebeb800u;
        uVar2 = f33_get_diagnostic_event_state(0x100);
        if ((uVar2 & 1) != 0) {
          f33_report_diagnostic_event_pass(0x100);
        }
        thunk_FUN_000524be(0x100);
      }
      uVar4 = 0x11;
    }
    if (cVar5 == '\x01') {
      uVar3 = 0x22;
    }
  }
  cVar5 = '\x02';
LAB_000b6b8c:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x4fe))))) = uVar3;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x500))))) = uVar4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x504))))) = cVar5;
  return;
}



void FUN_000b6b9a(void)

{
  FUN_000b6a42();
  FUN_000b6a8a();
  FUN_000b6ae0();
  return;
}



void FUN_000b6bae(void)

{
  char cVar1;
  uint32_t puVar2;
  uint uVar3;
  
  cVar1 = DAT_febeb2fc;
  puVar2 = 0xfebeb800u;
  uVar3 = f33_get_diagnostic_event_state(0x100);
  if ((uVar3 & 1) != 0) {
    f33_report_diagnostic_event_pass(0x100);
  }
  thunk_FUN_000524be(0x100);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x503))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x500))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x504))))) = cVar1 == '\x01';
  return;
}



void FUN_000b6be6(void)

{
  if ((DAT_febeb302 != '\x11') && (DAT_febeb302 = 'D', (char)DAT_febeb324 != '\x11')) {
    DAT_febeb302 = '\x11';
    DAT_febeb2fc = 1;
    DAT_febeb2fd = 0;
  }
  return;
}



void FUN_000b6c14(void)

{
  if (DAT_febeb2fc == '\x01') {
    DAT_febeb302 = 0;
  }
  DAT_febeb2fc = 2;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_b6c28(void)

{
  return;
}



void FUN_000b6c2a(void)

{
  DAT_febeb305 = DAT_febef055;
  return;
}



void FUN_000b6c34(void)

{
  if (DAT_febeb30a < DAT_000aef56) {
    DAT_febeb30a = DAT_febeb30a + 1;
  }
  else {
    DAT_febeb309 = 0x5a;
  }
  return;
}



void FUN_000b6c56(char param_1)

{
  if ((((DAT_febeb314 == 0) || (DAT_febeb314 == 0x33333333)) || (DAT_febeb314 == -1)) ||
     (1 < f33_published_internal_source_admission_state)) {
    DAT_febeb308 = 0;
  }
  else {
    DAT_febeb308 = 0x5a;
    if (DAT_febebe89 == '\0') {
      if (DAT_febeb305 == param_1) {
        DAT_febeb308 = 0x5a;
        return;
      }
      if (DAT_febeb304 == 0) {
        DAT_febeb304 = DAT_000aef54 != 0;
        DAT_febeb306 = DAT_febebe88;
        DAT_febeb308 = 0x5a;
        return;
      }
      if (DAT_febeb306 != DAT_febebe88) {
        DAT_febeb304 = 1;
        DAT_febeb306 = DAT_febebe88;
        DAT_febeb308 = 0x5a;
        return;
      }
      if (DAT_000aef54 <= DAT_febeb304) {
        DAT_febeb308 = 0x5a;
        return;
      }
      DAT_febeb304 = DAT_febeb304 + 1;
      DAT_febeb308 = 0x5a;
      return;
    }
  }
  DAT_febeb304 = 0;
  return;
}



void FUN_000b6cc8(void)

{
  if (DAT_febeb304 < DAT_000aef54) {
    if (DAT_febeb309 != 'Z') {
      return;
    }
  }
  else {
    if ((DAT_febeb314 == -0x55aaaa56) && (DAT_febeb306 == 'Z')) {
      DAT_febeb307 = 0;
      DAT_febeb30c = 0xaa5555aa;
      return;
    }
    if ((DAT_febeb314 == 0x55aaaa55) && (DAT_febeb306 == '\0')) {
      DAT_febeb307 = 0;
      DAT_febeb30c = 0x55aaaa55;
      return;
    }
  }
  DAT_febeb307 = 0x5a;
  return;
}



void FUN_000b6d20(void)

{
  undefined1 uVar1;
  uint32_t puVar2;
  uVar1 = DAT_febef055;
  puVar2 = 0xfebeb800u;
  if ((DAT_febeb30c == -0x55aaaa56) || (DAT_febeb30c == 0x55aaaa55)) {
    DAT_febeb309 = 0;
    DAT_febeb30a = 0;
  }
  else {
    puVar2 = 0xfebeb800u;
    FUN_000b6c34();
    FUN_000b6c56(uVar1);
    FUN_000b6cc8();
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x4fb))))) = uVar1;
  return;
}



/* Constant-block fill: 5 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_b6d60(void)

{
  DAT_febeb309 = 0;
  DAT_febeb30a = 0;
  DAT_febeb304 = 0;
  DAT_febeb307 = 0;
  DAT_febeb30c = 0;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_b6d70(void)

{
  return;
}



void FUN_000b6d72(void)

{
  uint32_t puVar1;
  int iVar2;
  int local_10 [2];
  
  puVar1 = 0xfebeb800u;
  iVar2 = FUN_000ff0b0(0x102,local_10);
  if (iVar2 == 0x10) {
    f33_report_diagnostic_healthy_observed(0x12a);
    if ((local_10[0] != 0) && ((local_10[0] == 0x55aaaa55 || (local_10[0] == -0x55aaaa56)))) {
      f33_report_diagnostic_event_pass(0xff);
      thunk_FUN_000524be(0x14d);
      iVar2 = local_10[0];
      goto LAB_000b6de6;
    }
  }
  else if (iVar2 != 0x11) {
    iVar2 = -1;
    f33_report_diagnostic_event_failure(0x12a,100);
    goto LAB_000b6de6;
  }
  iVar2 = 0x33333333;
  thunk_FUN_00051d38(0xff,0xd,100);
LAB_000b6de6:
  (*((int *)camry_host_ptr((uint32_t)(puVar1 + -0x4ec)))) = iVar2;
  return;
}



/* Far-call trampoline: prepare {lp},0 / jarl 0xB6D72 / dispose 0,{lp},lp; byte-verified against the
   exact image. Forwards with registers and stack unchanged; marked as a thunk. Forwarding shape
   machine-verified; target semantics not recovered. */

void thunk_FUN_000b6d72(void)

{
  FUN_000b6d72();
  return;
}



void FUN_000b6dfa(void)

{
  uint32_t puVar1;
  int iVar2;
  int iVar3;
  int local_10 [2];
  
  iVar3 = DAT_febeb314;
  puVar1 = 0xfebeb800u;
  iVar2 = FUN_000ff0b0(0x102,local_10);
  if ((iVar2 == 0x10) &&
     ((local_10[0] == 0 ||
      ((iVar3 = local_10[0], local_10[0] != 0x55aaaa55 && (local_10[0] != -0x55aaaa56)))))) {
    iVar3 = 0x33333333;
  }
  (*((int *)camry_host_ptr((uint32_t)(puVar1 + -0x4ec)))) = iVar3;
  return;
}



uint FUN_000b6e3c(void)

{
  undefined4 local_c;
  undefined4 uStack_8;
  
  uStack_8 = 0;
  local_c = DAT_febeb318;
  return FUN_000ff09c(0x102,&local_c);
}



void FUN_000b6e58(void)

{
  int iVar1;
  uint32_t puVar2;
  uint uVar3;
  char cVar4;
  
  iVar1 = DAT_febeb318;
  cVar4 = DAT_febeb310;
  puVar2 = 0xfebeb800u;
  if (DAT_febeb310 == '\x11') {
    if ((DAT_febeb311 != '\"') && (DAT_febeb312 != '\"')) {
      puVar2 = 0xfebeb800u;
      FUN_000b6e3c();
      cVar4 = '\"';
    }
  }
  else if (DAT_febeb310 == '\"') {
    puVar2 = 0xfebeb800u;
    uVar3 = FUN_000ff0c4(0x102);
    if (uVar3 == 0x10) {
      cVar4 = 'D';
      if ((iVar1 == 0x55aaaa55) || (iVar1 == -0x55aaaa56)) {
        f33_report_diagnostic_event_pass(0xff);
        thunk_FUN_000524be(0x14d);
      }
      else {
        thunk_FUN_00051d38(0xff,0xd,100);
        thunk_FUN_00051d38(0x14d,0x14,100);
      }
      f33_fill_constant_block_b6d60();
      FUN_000b6bae();
    }
    else if ((uVar3 & 0xf0) != 0x20) {
      cVar4 = -0x78;
      f33_report_diagnostic_event_failure(0x132,100);
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x4f0))))) = cVar4;
  return;
}



uint FUN_000b6f0c(void)

{
  undefined4 local_c;
  undefined4 uStack_8;
  
  local_c = 0;
  uStack_8 = 0;
  return FUN_000ff09c(0x102,&local_c);
}



void FUN_000b6f24(void)

{
  uint32_t puVar1;
  uint uVar2;
  char cVar3;
  
  cVar3 = DAT_febeb311;
  puVar1 = 0xfebeb800u;
  if (DAT_febeb311 == '\x11') {
    if ((DAT_febeb310 != '\"') && (DAT_febeb312 != '\"')) {
      puVar1 = 0xfebeb800u;
      FUN_000b6f0c();
      cVar3 = '\"';
    }
  }
  else if (DAT_febeb311 == '\"') {
    puVar1 = 0xfebeb800u;
    uVar2 = FUN_000ff0c4(0x102);
    if (uVar2 == 0x10) {
      cVar3 = 'D';
      thunk_FUN_00051d38(0xff,0xd,100);
      thunk_FUN_000524be(0x14d);
      f33_fill_constant_block_b6d60();
      FUN_000b6bae();
    }
    else if ((uVar2 & 0xf0) != 0x20) {
      cVar3 = -0x78;
      f33_report_diagnostic_event_failure(0x132,100);
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x4ef))))) = cVar3;
  return;
}



uint FUN_000b6fa8(void)

{
  undefined4 local_c;
  undefined4 uStack_8;
  
  uStack_8 = 0;
  local_c = DAT_febeb31c;
  return FUN_000ff09c(0x102,&local_c);
}



void FUN_000b6fc4(void)

{
  uint32_t puVar1;
  undefined4 uVar2;
  uint uVar3;
  char cVar4;
  
  cVar4 = DAT_febeb312;
  puVar1 = 0xfebeb800u;
  if (DAT_febeb312 == '\x11') {
    if ((DAT_febeb310 != '\"') && (DAT_febeb311 != '\"')) {
      puVar1 = 0xfebeb800u;
      FUN_000b6fa8();
      cVar4 = '\"';
    }
  }
  else if (DAT_febeb312 == '\"') {
    puVar1 = 0xfebeb800u;
    uVar3 = FUN_000ff0c4(0x102);
    if (uVar3 == 0x10) {
      cVar4 = 'D';
      f33_report_diagnostic_event_pass(0xff);
      thunk_FUN_000524be(0x14d);
      f33_fill_constant_block_b6d60();
      FUN_000b6bae();
      uVar2 = 0;
    }
    else {
      if ((uVar3 & 0xf0) == 0x20) goto LAB_000b704c;
      cVar4 = -0x78;
      f33_report_diagnostic_event_failure(0x132,100);
      uVar2 = 0x20;
    }
    thunk_FUN_0004d0a4(0x14,uVar2);
  }
LAB_000b704c:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x4ee))))) = cVar4;
  return;
}



/* Sequential initializer chain: 4 unconditional calls and no other statements; shape-verified. The
   called sequence is the function's entire behavior; chain family members differ in callee sets. */

void f33_run_init_chain_b7054(void)

{
  FUN_000b6dfa();
  FUN_000b6e58();
  FUN_000b6f24();
  FUN_000b6fc4();
  return;
}



void FUN_000b706c(undefined4 param_1)

{
  DAT_febeb310 = 0x11;
  DAT_febeb318 = param_1;
  return;
}



void FUN_000b707a(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  FUN_000b72a2();
  FUN_000b6c14();
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x4ef))))) = 0x11;
  return;
}



/* Resetsqualification,B31211,B31Cencodedmode,doesnotwriteliveB314. */

void f33_stage_record102_mode_write(uint encoded_mode)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  FUN_000b72a2();
  FUN_000b6c14();
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x4ee))))) = 0x11;
  (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x4e4)))) = encoded_mode;
  return;
}



void FUN_000b70b0(void)

{
  if (DAT_febeb314 == 0x33333333) {
    f33_report_diagnostic_event_failure(0xff,100);
  }
  return;
}



/* Single constant publisher: DAT_febeb324 = 0; Shape-classified from the canonical corpus; the
   target cell is not yet named, so the written state's meaning is unknown. */

void FUN_000b70d2(void)

{
  DAT_febeb324 = 0;
  return;
}



void FUN_000b70d8(void)

{
  DAT_febeb321 = DAT_febef055;
  return;
}



void FUN_000b70e2(void)

{
  if ((DAT_000aef5a < DAT_febebede) || (1 < f33_published_internal_source_admission_state)) {
    DAT_febeb323 = 0;
  }
  else {
    DAT_febeb323 = 0x5a;
  }
  return;
}



void FUN_000b7108(void)

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



undefined2 FUN_000b71e2(undefined2 param_1)

{
  ((void)(param_1), FUN_000b70e2());
  FUN_000b7108();
  return FUN_000b7186((uint)(ushort)param_1);
}



undefined ** FUN_000b71f8(uint param_1)

{
  if (((DAT_febeb310 != '\0') && (DAT_febeb310 != '\x11')) && (DAT_febeb310 != '\"')) {
    if ((DAT_febeb310 == 'D') && ((int)(param_1 & 0xffff) >> 8 == 0x22)) {
      return &PTR_LAB_00008822;
    }
    return (undefined **)((undefined *)camry_host_ptr(0x8844u));
  }
  return (undefined **)(param_1 & 0xffff);
}



void FUN_000b726c(void)

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
    FUN_000b6c14();
    uVar3 = uVar1;
  }
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x4dc)))) = uVar5;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x4e0))))) = uVar4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x4df))))) = uVar3;
  return;
}



void FUN_000b72a2(void)

{
  if ((int)(uint)DAT_febeb324 >> 8 == 0x11) {
    DAT_febeb324 = 0x8822;
  }
  return;
}



/* Single constant publisher: DAT_febeb334 = 0; Shape-classified from the canonical corpus; the
   target cell is not yet named, so the written state's meaning is unknown. */

void FUN_000b72ba(void)

{
  DAT_febeb334 = 0;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_b72c0(void)

{
  return;
}



/* Constant-block fill: 8 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_b72c2(void)

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



void FUN_000b72ec(void)

{
  DAT_febeb333 = 2;
  DAT_febeb32c = 0;
  DAT_febeb334 = 0x22;
  DAT_febeb335 = 0;
  return;
}



/* Constant-block fill: 9 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_b7314(void)

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



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_b733e(void)

{
  return;
}



/* Single constant publisher: DAT_febeb352 = 0; Shape-classified from the canonical corpus; the
   target cell is not yet named, so the written state's meaning is unknown. */

void FUN_000b734e(void)

{
  DAT_febeb352 = 0;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_b7354(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_b7356(void)

{
  return;
}



/* Constant-block fill: 5 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_b7358(void)

{
  DAT_febeb352 = 0x8822;
  DAT_febeb348 = 0;
  DAT_febeb34c = 0;
  DAT_febeb349 = 0;
  DAT_febeb34e = 0;
  return;
}



/* Single constant publisher: DAT_febeb354 = 0; Shape-classified from the canonical corpus; the
   target cell is not yet named, so the written state's meaning is unknown. */

void FUN_000b736c(void)

{
  DAT_febeb354 = 0;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_b7372(void)

{
  return;
}



void FUN_000b7374(void)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  iVar2 = thunk_FUN_00062e12();
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x4ac))))) = iVar2 == 0;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_b738a(void)

{
  return;
}



void FUN_000b738c(void)

{
  DAT_febeb358 = 1;
  DAT_febeb359 = 2;
  DAT_febeb35a = 0x1e;
  return;
}



void FUN_000b73a0(ushort param_1,ushort *param_2,ushort *param_3)

{
  if (*param_2 < param_1) {
    *param_2 = param_1;
  }
  if (param_1 < *param_3) {
    *param_3 = param_1;
  }
  return;
}



/* WARNING: Removing unreachable block (ram,0x000b75fe) */
/* WARNING: Removing unreachable block (ram,0x000b75fa) */
/* WARNING: Removing unreachable block (ram,0x000b74ce) */
/* WARNING: Removing unreachable block (ram,0x000b74c6) */
/* WARNING: Removing unreachable block (ram,0x000b74ca) */
/* WARNING: Removing unreachable block (ram,0x000b74d2) */

void FUN_000b73cc(void)

{
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
  short sStack_5e;
  short sStack_5c;
  short sStack_5a;
  short sStack_58;
  short sStack_56;
  short sStack_54;
  short sStack_52;
  short sStack_50;
  undefined2 uStack_4e;
  int iStack_4c;
  int iStack_48;
  int iStack_44;
  int local_40;
  int local_3c;
  int local_38;
  undefined4 local_34;
  ushort uStack_30;
  ushort uStack_2e;
  
  sVar19 = DAT_febeb35a;
  cVar17 = DAT_febeb359;
  cVar13 = DAT_febeb358;
  puVar6 = 0xfebeb800u;
  sStack_5e = DAT_febeb35c;
  sStack_5c = DAT_febeb35e;
  sStack_5a = DAT_febeb360;
  sStack_58 = DAT_febeb362;
  sStack_56 = DAT_febeb364;
  sStack_54 = DAT_febeb366;
  sStack_52 = DAT_febeb368;
  sStack_50 = DAT_febeb36a;
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
      sStack_50 = 0xfff;
      sStack_52 = 0xfff;
      sStack_54 = 0xfff;
      sStack_56 = 0xfff;
      sStack_58 = 0;
      sStack_5a = 0;
      sStack_5c = 0;
      uVar18 = 0;
      sStack_5e = 0;
      uVar16 = 0;
      uVar15 = 0;
      uVar14 = 0;
    }
    uVar18 = uVar18 + DAT_febeb056;
    uVar16 = uVar16 + uVar12;
    uVar15 = uVar15 + uVar11;
    uVar14 = uVar14 + uVar10;
    puVar6 = 0xfebeb800u;
    FUN_000b73a0((uint)DAT_febeb056,&sStack_5e,&sStack_56);
    FUN_000b73a0(uVar12, ((ushort *)camry_host_ptr((uint32_t)(extraout_r7 + 2))), ((ushort *)camry_host_ptr((uint32_t)(extraout_r8 + 2))));
    FUN_000b73a0(uVar11,&sStack_5a,&sStack_52);
    FUN_000b73a0(uVar10, ((ushort *)camry_host_ptr((uint32_t)(extraout_r7_00 + 2))), ((ushort *)camry_host_ptr((uint32_t)(extraout_r8_00 + 2))));
    origin = sVar19 - 1;
    sVar19 = sVar19 + -1;
    if (sVar19 != 0) goto LAB_000b76ce;
    uStack_4e = (undefined2)(uVar14 / 0x1e);
    (*((uint16_t *)((uint8_t *)&local_34 + 0u))) = sStack_5e - sStack_56;
    (*((uint16_t *)((uint8_t *)&local_34 + 2u))) = sStack_5c - sStack_54;
    uStack_30 = sStack_5a - sStack_52;
    uStack_2e = sStack_58 - sStack_50;
    iStack_4c = f33_scale_u16_delta_s16_x4((ushort)(uVar18 / 0x1e),0x800,-0x9cd);
    iStack_48 = f33_scale_u16_delta_s16_x4((ushort)(uVar16 / 0x1e),0x800,-0x9cd);
    iStack_44 = f33_scale_u16_delta_s16_x4((ushort)(uVar15 / 0x1e),0x800,-0x9cd);
    local_40 = f33_scale_u16_delta_s16_x4(value,0x800,-0x9cd);
    local_3c = f33_scale_u16_delta_s16_x4((ushort)local_34,origin,-0x9cd);
    local_38 = f33_scale_u16_delta_s16_x4((*((uint16_t *)((uint8_t *)&local_34 + 2u))),origin,-0x9cd);
    local_34 = f33_scale_u16_delta_s16_x4(uStack_30,origin,-0x9cd);
    iVar8 = f33_scale_u16_delta_s16_x4(uStack_2e,origin,-0x9cd);
    if (local_3c + 0x7fffffff < 0 == (-1 < local_3c && local_3c + 0x7fffffff < 0) &&
        local_3c != -0x7fffffff) {
      iVar2 = local_3c;
      if (local_3c < 0) {
        iVar2 = -local_3c;
      }
    }
    else {
      iVar2 = 0x7fffffff;
    }
    if (local_38 + 0x7fffffff < 0 == (-1 < local_38 && local_38 + 0x7fffffff < 0) &&
        local_38 != -0x7fffffff) {
      iVar3 = local_38;
      if (local_38 < 0) {
        iVar3 = -local_38;
      }
    }
    else {
      iVar3 = 0x7fffffff;
    }
    if (local_34 + 0x7fffffff < 0 == (-1 < local_34 && local_34 + 0x7fffffff < 0) &&
        local_34 != -0x7fffffff) {
      iVar4 = local_34;
      if (local_34 < 0) {
        iVar4 = -local_34;
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
    iVar9 = (iStack_44 - local_40) / 2;
    iVar5 = (iStack_4c - iStack_48) / 2;
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
    if (((((iStack_4c - f33_learned_quad_rom_bounds.pair1_upper < 0 !=
            (iStack_4c < 0 != f33_learned_quad_rom_bounds.pair1_upper < 0 &&
            f33_learned_quad_rom_bounds.pair1_upper < 0 ==
            iStack_4c - f33_learned_quad_rom_bounds.pair1_upper < 0) ||
            iStack_4c == f33_learned_quad_rom_bounds.pair1_upper) &&
          (iStack_4c - f33_learned_quad_rom_bounds.pair1_lower < 0 ==
           (iStack_4c < 0 != f33_learned_quad_rom_bounds.pair1_lower < 0 &&
           f33_learned_quad_rom_bounds.pair1_lower < 0 ==
           iStack_4c - f33_learned_quad_rom_bounds.pair1_lower < 0))) &&
         ((iStack_48 - f33_learned_quad_rom_bounds.pair1_upper < 0 !=
           (iStack_48 < 0 != f33_learned_quad_rom_bounds.pair1_upper < 0 &&
           f33_learned_quad_rom_bounds.pair1_upper < 0 ==
           iStack_48 - f33_learned_quad_rom_bounds.pair1_upper < 0) ||
           iStack_48 == f33_learned_quad_rom_bounds.pair1_upper &&
          ((iStack_48 - f33_learned_quad_rom_bounds.pair1_lower < 0 ==
            (iStack_48 < 0 != f33_learned_quad_rom_bounds.pair1_lower < 0 &&
            f33_learned_quad_rom_bounds.pair1_lower < 0 ==
            iStack_48 - f33_learned_quad_rom_bounds.pair1_lower < 0) &&
           (iStack_44 - f33_learned_quad_rom_bounds.pair2_upper < 0 !=
            (iStack_44 < 0 != f33_learned_quad_rom_bounds.pair2_upper < 0 &&
            f33_learned_quad_rom_bounds.pair2_upper < 0 ==
            iStack_44 - f33_learned_quad_rom_bounds.pair2_upper < 0) ||
            iStack_44 == f33_learned_quad_rom_bounds.pair2_upper)))))) &&
        (iStack_44 - f33_learned_quad_rom_bounds.pair2_lower < 0 ==
         (iStack_44 < 0 != f33_learned_quad_rom_bounds.pair2_lower < 0 &&
         f33_learned_quad_rom_bounds.pair2_lower < 0 ==
         iStack_44 - f33_learned_quad_rom_bounds.pair2_lower < 0))) &&
       (((((local_40 - f33_learned_quad_rom_bounds.pair2_upper < 0 !=
            (local_40 < 0 != f33_learned_quad_rom_bounds.pair2_upper < 0 &&
            f33_learned_quad_rom_bounds.pair2_upper < 0 ==
            local_40 - f33_learned_quad_rom_bounds.pair2_upper < 0) ||
            local_40 == f33_learned_quad_rom_bounds.pair2_upper &&
           (local_40 - f33_learned_quad_rom_bounds.pair2_lower < 0 ==
            (local_40 < 0 != f33_learned_quad_rom_bounds.pair2_lower < 0 &&
            f33_learned_quad_rom_bounds.pair2_lower < 0 ==
            local_40 - f33_learned_quad_rom_bounds.pair2_lower < 0))) &&
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
      thunk_FUN_00035772(uVar18 / 0x1e & 0xffff,uVar16 / 0x1e & 0xffff,uVar15 / 0x1e & 0xffff,
                         uStack_4e);
      cVar13 = '\x02';
      thunk_FUN_00035780();
      goto LAB_000b76ce;
    }
    cVar1 = '\x03';
    uVar7 = 0x30;
  }
  if (cVar17 != '\0') {
    cVar17 = cVar17 + -1;
    if (cVar17 == '\0') {
      thunk_FUN_00051d38(uVar7,0xb,100);
      FUN_000b15ac(0x2d);
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
  (*((short *)camry_host_ptr((uint32_t)(puVar6 + -0x4a4)))) = sStack_5e;
  (*((uint *)camry_host_ptr((uint32_t)(puVar6 + -0x494)))) = uVar18;
  (*((uint *)camry_host_ptr((uint32_t)(puVar6 + -0x490)))) = uVar16;
  (*((uint *)camry_host_ptr((uint32_t)(puVar6 + -0x48c)))) = uVar15;
  (*((short *)camry_host_ptr((uint32_t)(puVar6 + -0x4a2)))) = sStack_5c;
  (*((uint *)camry_host_ptr((uint32_t)(puVar6 + -0x488)))) = uVar14;
  (*((short *)camry_host_ptr((uint32_t)(puVar6 + -0x4a0)))) = sStack_5a;
  (*((short *)camry_host_ptr((uint32_t)(puVar6 + -0x49e)))) = sStack_58;
  (*((short *)camry_host_ptr((uint32_t)(puVar6 + -0x49c)))) = sStack_56;
  (*((short *)camry_host_ptr((uint32_t)(puVar6 + -0x49a)))) = sStack_54;
  (*((short *)camry_host_ptr((uint32_t)(puVar6 + -0x498)))) = sStack_52;
  (*((short *)camry_host_ptr((uint32_t)(puVar6 + -0x496)))) = sStack_50;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_b7714(void)

{
  return;
}



/* Constant-block fill: 6 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_b7716(void)

{
  DAT_febeb37c = 0;
  DAT_febeb37d = 0;
  DAT_febeb380 = 0;
  DAT_febeb382 = 0;
  DAT_febeb384 = 0;
  DAT_febeb37e = 0;
  return;
}



void FUN_000b7728(void)

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
  sStack_1e = DAT_febeb384;
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
        thunk_FUN_00051d38(0x32,0xb,0x32);
        FUN_000b15ac(0x2d);
        cVar3 = -1;
      }
      else {
        puVar1 = 0xfebeb800u;
        FUN_000d22c0(((undefined *)camry_host_ptr(0xaece4u)),DAT_febeb380,&sStack_1e);
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



void FUN_000b77f4(void)

{
  FUN_000b42f0();
  f33_set_output_request_word('\0',0);
  f33_set_output_request_word('\x01',0);
  return;
}



void FUN_000b7810(void)

{
  if (DAT_febeb1a4 == '\0') {
    f33_set_output_request_word('\0',0x70017001);
    f33_set_output_request_word('\x01',0x70017001);
    FUN_000b42fa();
  }
  return;
}



void FUN_000b783c(void)

{
  DAT_febeb38c = DAT_000af434;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_b784a(void)

{
  return;
}



/* WARNING: Removing unreachable block (ram,0x000b7882) */
/* WARNING: Removing unreachable block (ram,0x000b7876) */

void FUN_000b784c(void)

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



/* WARNING: Removing unreachable block (ram,0x000b78b2) */

void FUN_000b7896(void)

{
  uint32_t puVar1;
  int local_8;
  
  puVar1 = 0xfebeb800u;
  if (DAT_febeb388 == '\x02') {
    local_8 = DAT_febeb398 / 10;
    puVar1 = 0xfebeb800u;
    FUN_000d1cf6(local_8,0x7fff,(int)0xffff8001,&local_8);
  }
  else {
    (*((uint16_t *)((uint8_t *)&local_8 + 0u))) = 19999;
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x476)))) = (undefined2)local_8;
  return;
}



void FUN_000b78d0(void)

{
  uint32_t puVar1;
  short sVar2;
  
  puVar1 = 0xfebeb800u;
  sVar2 = DAT_febeb38c;
  if (DAT_febeb38c != 0) {
    sVar2 = DAT_febeb38c + -1;
  }
  FUN_000b784c();
  FUN_000b7896();
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x474)))) = sVar2;
  return;
}



/* Paired constant publisher: DAT_febeb390 = 0; and DAT_febeb388 = 0;; shape-classified from the
   canonical corpus. Target cells not yet named. */

void FUN_000b78ee(void)

{
  DAT_febeb390 = 0;
  DAT_febeb388 = 0;
  return;
}



/* WARNING: Removing unreachable block (ram,0x000b792c) */
/* WARNING: Removing unreachable block (ram,0x000b7920) */
/* WARNING: Removing unreachable block (ram,0x000b7908) */

undefined4 FUN_000b78f8(int param_1,int param_2)

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
  FUN_000b784c();
  FUN_000b7896();
  return uVar3;
}



void FUN_000b794e(void)

{
  if (DAT_febeb388 != '\0') {
    DAT_febeb38a = 19999;
    DAT_febeb388 = '\x01';
  }
  return;
}



void FUN_000b7966(void)

{
  DAT_febeb388 = 2;
  FUN_000b784c();
  FUN_000b7896();
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_b797c(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_b797e(void)

{
  return;
}



void FUN_000b7980(void)

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
       (((DAT_febeb3f4 != '\x03' && (DAT_febeb3f8 != 0)) && ((DAT_febeb082 & 0x81ff) == 0)))) {
      iVar1 = (uint)uVar2 - DAT_000af478;
      if (iVar1 - DAT_febeb3f8 < 0 ==
          (iVar1 < 0 != DAT_febeb3f8 < 0 && DAT_febeb3f8 < 0 == iVar1 - DAT_febeb3f8 < 0) &&
          iVar1 != DAT_febeb3f8) {
        puVar3 = 0xfebeb800u;
        thunk_FUN_00051cf6(0x24,0x32);
        FUN_000b794e();
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



/* Single constant publisher: DAT_febeb39c = 0; Shape-classified from the canonical corpus; the
   target cell is not yet named, so the written state's meaning is unknown. */

void FUN_000b79fa(void)

{
  DAT_febeb39c = 0;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_b7a00(void)

{
  return;
}



/* Constant-block fill: 5 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_b7a02(void)

{
  DAT_febeb3a1 = 0;
  DAT_febeb3a2 = 0;
  DAT_febeb3a4 = 0;
  DAT_febeb3a6 = 0;
  DAT_febeb3a0 = 0;
  return;
}



/* WARNING: Removing unreachable block (ram,0x000b7a62) */
/* WARNING: Removing unreachable block (ram,0x000b7a34) */

void FUN_000b7a12(void)

{
  bool bVar1;
  int iVar2;
  undefined1 uVar3;
  int iVar4;
  uint32_t puVar5;
  short sVar6;
  int local_14;
  int iStack_10;
  int iVar7;
  
  iVar2 = DAT_febeb3c4;
  puVar5 = 0xfebeb800u;
  local_14 = (DAT_febeac70 * 10) / 8;
  FUN_000d1cf6(local_14,(int)DAT_000af480,-(int)DAT_000af480,&local_14);
  iVar4 = (int)DAT_000af47c;
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + -0x45e)))) = (short)local_14;
  iStack_10 = -(local_14 * iVar4) / 0x40;
  FUN_000d1cf6(iStack_10,0x7fff,(int)0xffff8001,&iStack_10);
  sVar6 = DAT_000af47e;
  iVar4 = (int)DAT_000af47e;
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + -0x45c)))) = (short)iStack_10;
  iVar2 = iVar2 + iStack_10;
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



void FUN_000b7a9e(void)

{
  if ((DAT_febeb3a1 == 'Z') && (DAT_febeed00 == 'Z')) {
    FUN_000b7a12();
  }
  return;
}



/* Constant-block fill: 5 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_b7abe(void)

{
  DAT_febeb3a2 = 0;
  DAT_febeb3a4 = 0;
  DAT_febeb3a6 = 0;
  DAT_febeb3a0 = 0;
  DAT_febeb3a1 = 0x5a;
  return;
}



/* Constant-block fill: 5 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_b7ad2(void)

{
  DAT_febeb3a1 = 0;
  DAT_febeb3a2 = 0;
  DAT_febeb3a4 = 0;
  DAT_febeb3a6 = 0;
  DAT_febeb3a0 = 0;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_b7ae2(void)

{
  return;
}



/* Constant-block fill: 11 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_b7ae4(void)

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



/* WARNING: Removing unreachable block (ram,0x000b7b8e) */
/* WARNING: Removing unreachable block (ram,0x000b7b18) */

void FUN_000b7b00(void)

{
  short sVar1;
  char cVar2;
  int iVar3;
  int iVar4;
  uint32_t puVar5;
  int iVar6;
  int local_2c;
  int iStack_28;
  int iStack_24;
  int iStack_20;
  int iStack_1c;
  int iStack_18;
  
  puVar5 = 0xfebeb800u;
  iStack_28 = -(DAT_febeb398 / 10);
  FUN_000d1cf6(iStack_28,(int)DAT_000af484,-(int)DAT_000af484,&iStack_28);
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + -0x456)))) = (short)iStack_28;
  sVar1 = (*((short *)camry_host_ptr((uint32_t)(puVar5 + -0x454))));
  iVar4 = (iStack_28 - (*((int *)camry_host_ptr((uint32_t)(puVar5 + -0x444))))) + (*((int *)camry_host_ptr((uint32_t)(puVar5 + -0x448))));
  iVar3 = (int)DAT_000af486;
  iVar6 = iVar4;
  if (iVar3 != 0) {
    if (iVar4 == -0x80000000 && iVar3 == -1) {
      iVar6 = -0x80000000;
    }
    else {
      iVar6 = iVar4 / iVar3;
    }
  }
  FUN_000d1cf6(iVar6,0x7fff,(int)0xffff8001,&local_2c);
  iStack_20 = (*((int *)camry_host_ptr((uint32_t)(puVar5 + -0x440))));
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + -0x44c)))) = sVar1;
  (*((int *)camry_host_ptr((uint32_t)(puVar5 + -0x448)))) = iVar4;
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + -0x454)))) = (short)local_2c;
  iVar4 = (int)DAT_000af488;
  (*((int *)camry_host_ptr((uint32_t)(puVar5 + -0x444)))) = iVar6;
  cVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x800)))));
  iStack_24 = ((sVar1 + local_2c) * iVar4) / 0x80;
  FUN_000d1cf6(iStack_24,0x7fff,(int)0xffff8001,&iStack_24);
  if (((cVar2 != '\x02') || (iStack_24 < 0)) && ((cVar2 != '\x01' || (-1 < iStack_24)))) {
    iStack_20 = iStack_20 + iStack_24;
  }
  FUN_000d1cf6(iStack_20,PTR_LAB_000af490,-(int)PTR_LAB_000af490,&iStack_20);
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + -0x452)))) = (short)iStack_24;
  (*((int *)camry_host_ptr((uint32_t)(puVar5 + -0x440)))) = iStack_20;
  iStack_1c = local_2c * DAT_000af48a;
  FUN_000d1cf6(iStack_1c,0x7fff,(int)0xffff8001,&iStack_1c);
  iStack_18 = 0;
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + -0x450)))) = (short)iStack_1c;
  FUN_000d1cf6(0,0x7fff,(int)0xffff8001,&iStack_18);
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + -0x44e)))) = (short)iStack_18;
  (*((int *)camry_host_ptr((uint32_t)(puVar5 + -0x43c)))) = iStack_20 + iStack_1c + iStack_18;
  return;
}



void FUN_000b7c2c(void)

{
  if (DAT_febeb3a8 == 'Z') {
    FUN_000b7b00();
  }
  return;
}



/* Constant-block fill: 11 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_b7c42(void)

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



/* Constant-block fill: 11 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_b7c62(void)

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



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_b7c7e(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_b7c80(void)

{
  return;
}



void FUN_000b7c82(void)

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
    FUN_000b794e();
    uVar1 = 0x5a;
    goto LAB_000b7cc4;
  }
  uVar1 = 0;
LAB_000b7cc4:
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x420)))) = uVar3;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x431))))) = uVar1;
  return;
}



void FUN_000b7cd0(void)

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
  FUN_000d1178((int)DAT_febeb054,&sStack_16);
  if (cVar3 == '\0') {
    iVar5 = (int)DAT_000af4ac;
    iVar7 = (int)sStack_16;
    if (iVar7 - iVar5 < 0 != (iVar7 < 0 != iVar5 < 0 && iVar5 < 0 == iVar7 - iVar5 < 0) ||
        iVar7 == iVar5) goto LAB_000b7d0a;
LAB_000b7d1a:
    if ((cVar2 == 'Z') && ((cVar1 == '\0' || (cVar4 == '\0')))) {
      FUN_000b794e();
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



/* Cancellation precedes done; publish B3CB=0/2. Otherwise runtime predicates select continuing1 or
   failed3. Return5A for terminal,0 for continuing. Counts are not milliseconds. Cancellation
   precedes completion; otherwise runtime predicates choose continuing or failure. Publish
   B3CB0/2/1/3 and return terminal5A versus continuing0. Invocation counts are not elapsed-time
   measurements. */

uchar f33_qualify_service_progress(uchar done,uchar cancel)

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



uchar FUN_000b7dba(uchar phase)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_febeb3d4 == 'Z') {
    puVar1 = 0xfebeb800u;
    f33_fill_constant_block_b8a10();
    f33_fill_constant_block_b8b10();
    phase = '\x02';
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x42c))))) = 0x5a;
  return phase;
}



undefined4 FUN_000b7de2(void)

{
  int iVar1;
  byte bVar2;
  int iVar3;
  uint32_t puVar4;
  undefined4 uVar5;
  char cVar6;
  short sStack_16;
  int iStack_14;
  
  iVar3 = DAT_febeb3ec;
  bVar2 = DAT_febeb3cd;
  iVar1 = DAT_febeafe8;
  puVar4 = 0xfebeb800u;
  FUN_000d1178((int)DAT_febeafdc,&sStack_16);
  FUN_000d1194(iVar1 - iVar3,&iStack_14);
  iVar3 = (int)DAT_000af4a0;
  iVar1 = sStack_16 - iVar3;
  if ((iVar1 < 0 == (sStack_16 < 0 != iVar3 < 0 && iVar3 < 0 == iVar1 < 0)) ||
     (iStack_14 - DAT_000af4b0 < 0 ==
      (iStack_14 < 0 != DAT_000af4b0 < 0 && DAT_000af4b0 < 0 == iStack_14 - DAT_000af4b0 < 0))) {
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



uchar FUN_000b7e44(uchar phase)

{
  int iVar1;
  
  iVar1 = FUN_000b7de2();
  if (iVar1 == 0x5a) {
    f33_fill_constant_block_b8b24();
    f33_fill_constant_block_b8a30();
    phase = '\x03';
  }
  return phase;
}



undefined4 FUN_000b7e66(byte param_1)

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



/* Update minimum of -AFE8 while not qualified, call B7E66, retain and return B3C8 status. Retain
   minimum -AFE8 while B3C8 is not5A; advance shared qualification counter and store/return its
   status. Low-byte parameter is the qualification threshold. */

uchar f33_update_service_minimum_excursion(uchar qualification)

{
  uint32_t puVar1;
  uchar uVar2;
  int iVar3;
  int iVar4;
  
  puVar1 = 0xfebeb800u;
  iVar3 = -DAT_febeafe8;
  iVar4 = DAT_febeb3e4;
  uVar2 = DAT_febeb3c8;
  if (DAT_febeb3c8 != 'Z') {
    if (iVar3 - DAT_febeb3e4 < 0 ==
        (iVar3 < 0 != DAT_febeb3e4 < 0 && DAT_febeb3e4 < 0 == iVar3 - DAT_febeb3e4 < 0)) {
      iVar3 = DAT_febeb3e4;
    }
    puVar1 = 0xfebeb800u;
    uVar2 = FUN_000b7e66(qualification);
    iVar4 = iVar3;
  }
  (*((int *)camry_host_ptr((uint32_t)(puVar1 + -0x41c)))) = iVar4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x438))))) = uVar2;
  return uVar2;
}



uchar FUN_000b7eb2(uchar phase)

{
  uchar uVar1;
  
  uVar1 = f33_update_service_minimum_excursion(DAT_000af494);
  if (uVar1 == 'Z') {
    f33_fill_constant_block_b8a10();
    f33_fill_constant_block_b8b10();
    phase = '\x04';
  }
  return phase;
}



uchar FUN_000b7edc(uchar phase)

{
  int iVar1;
  
  iVar1 = FUN_000b7de2();
  if (iVar1 == 0x5a) {
    f33_fill_constant_block_b8b24();
    f33_fill_constant_block_b8a30();
    phase = '\x05';
  }
  return phase;
}



/* Update maximum of -AFE8 while not qualified, call B7E66, retain and return B3C9 status. Retain
   maximum -AFE8 while B3C9 is not5A; advance qualification and store/return its status. Full scalar
   result is consumed by the subsequent phase logic. */

uchar f33_update_service_maximum_excursion(uchar qualification)

{
  uint32_t puVar1;
  uchar uVar2;
  int iVar3;
  int iVar4;
  
  puVar1 = 0xfebeb800u;
  iVar3 = -DAT_febeafe8;
  iVar4 = DAT_febeb3e8;
  uVar2 = DAT_febeb3c9;
  if (DAT_febeb3c9 != 'Z') {
    if (iVar3 - DAT_febeb3e8 < 0 !=
        (iVar3 < 0 != DAT_febeb3e8 < 0 && DAT_febeb3e8 < 0 == iVar3 - DAT_febeb3e8 < 0) ||
        iVar3 == DAT_febeb3e8) {
      iVar3 = DAT_febeb3e8;
    }
    puVar1 = 0xfebeb800u;
    uVar2 = FUN_000b7e66(qualification);
    iVar4 = iVar3;
  }
  (*((int *)camry_host_ptr((uint32_t)(puVar1 + -0x418)))) = iVar4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x437))))) = uVar2;
  return uVar2;
}



/* WARNING: Removing unreachable block (ram,0x000b7f72) */
/* WARNING: Removing unreachable block (ram,0x000b7f5a) */
/* Queue learned selector106 scalar BEFORE B78F8 geometry establishment. Preserve its R10 status
   across the B3F0 store and return it;5A signals invalid B138>>3 geometry. Diagnostic completion
   does not await the separate selector106 persistence poll. Queue learned scalar106 before geometry
   establishment; preserve B78F8 status in full R10 across B3F0 store and return. Invalid geometry
   can follow a queued persistence change; phase advancement alone is not success. */

uint f33_queue_service_center_and_check_geometry(void)

{
  undefined4 uVar1;
  undefined4 uVar2;
  uint32_t puVar3;
  uint uVar4;
  int local_18;
  int iStack_14;
  
  uVar2 = DAT_febeb3e8;
  uVar1 = DAT_febeb3e4;
  puVar3 = 0xfebeb800u;
  FUN_000d1194(DAT_febeb3e4,&local_18);
  FUN_000d1194(uVar2,&iStack_14);
  FUN_000b865e((((iStack_14 + local_18) / 0x80) * DAT_000af4b8 * 10) / 0x20000);
  uVar4 = FUN_000b78f8(uVar1,uVar2);
  (*((int *)camry_host_ptr((uint32_t)(puVar3 + -0x410)))) = iStack_14 + local_18;
  return uVar4;
}



uchar FUN_000b7f8a(uchar phase)

{
  uchar uVar1;
  uint uVar2;
  
  uVar1 = f33_update_service_maximum_excursion(DAT_000af494);
  if (uVar1 == 'Z') {
    uVar2 = f33_queue_service_center_and_check_geometry();
    if (uVar2 == 0x5a) {
      phase = '\t';
    }
    else {
      phase = '\x06';
    }
  }
  return phase;
}



undefined4 FUN_000b7fb8(int param_1,ushort param_2)

{
  ushort uVar1;
  uint32_t puVar2;
  undefined4 uVar3;
  short sVar4;
  int local_14;
  
  uVar1 = DAT_febeb3de;
  puVar2 = 0xfebeb800u;
  FUN_000d1194(DAT_febeb398,&local_14);
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



uchar FUN_000b7ff4(uchar phase)

{
  char cVar1;
  uint32_t puVar2;
  int iVar3;
  undefined1 uVar4;
  
  puVar2 = 0xfebeb800u;
  iVar3 = FUN_000b7fb8(DAT_000af4b4,DAT_000af4a2);
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x42d)))));
  uVar4 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x436)))));
  if (iVar3 == 0x5a) {
    f33_fill_constant_block_b7ad2();
    f33_fill_constant_block_b7c62();
    if (cVar1 == 'Z') {
      phase = '\t';
      FUN_000b7966();
      uVar4 = 0x5a;
    }
    else {
      f33_fill_constant_block_b8872();
      phase = '\b';
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x436))))) = uVar4;
  return phase;
}


