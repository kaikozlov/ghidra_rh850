#include "common.h"


/* Call51C66(event,32 hex); diagnostic lifecycle rejection is separate from later control-action
   publication. Event selection 0xc7. */

void f33_record_asserted_state_sample_threshold_b_failure(void)

{
  f33_report_diagnostic_event_failure(199,0x32);
  return;
}



/* Return readiness latch in r10:5A means admitted, not a void side-effect-only helper. Retain
   completed latch until explicit stage initializer; pending sequencing and counts per
   configured-family readiness contract. No hardware success is inferred from this software latch.
    */

uint f33_admit_sample_difference_monitor_a(void)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  
  uVar2 = (uint)DAT_febe6800;
  iVar1 = (uint)DAT_febe66b8 - (uint)DAT_febe66ae;
  if (uVar2 != 0x5a) {
    if (DAT_febe65f0 == 'Z') {
      iVar3 = (int)DAT_0002b758;
      if ((iVar1 - iVar3 < 0 == (iVar1 < 0 != iVar3 < 0 && iVar3 < 0 == iVar1 - iVar3 < 0) &&
           iVar1 != iVar3) && (DAT_febe6802 <= DAT_0002b752)) {
        DAT_febe6802 = DAT_febe6802 + 1;
      }
      else {
        uVar2 = 0x5a;
      }
    }
    else {
      DAT_febe6802 = 0;
    }
  }
  DAT_febe6800 = (char)uVar2;
  return uVar2;
}



/* Return readiness latch in r10:5A means admitted, not a void side-effect-only helper. Retain
   completed latch until explicit stage initializer; pending sequencing and counts per
   configured-family readiness contract. No hardware success is inferred from this software latch.
    */

uint f33_admit_sample_difference_elapsed_a(void)

{
  uint uVar1;
  
  uVar1 = (uint)DAT_febe6801;
  if (uVar1 != 0x5a) {
    if (DAT_febe6804 < DAT_0002b754) {
      DAT_febe6804 = DAT_febe6804 + 1;
    }
    else {
      uVar1 = 0x5a;
    }
  }
  DAT_febe6801 = (char)uVar1;
  return uVar1;
}



/* No-argument configured classifier. Gate baseline_zero: same as baseline_one except6614.bit0==0.
   Closed gate returns44, otherwise22 iff (int32(uint16(66B8))-int32(uint16(66AE))>1180
   &&66B8<=4736) || (66AE<1055 &&66B8>4736), else11. Full threshold partitions preserved in ROM. No
   physical units/source identity asserted. */

uint f33_classify_sample_difference_window_a(void)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  
  uVar2 = (uint)DAT_febe66b8;
  iVar1 = uVar2 - DAT_febe66ae;
  if (((((DAT_febe64d8 != '\0') || (DAT_febe64d0 != '\0')) || ((DAT_febe6620 >> 2 & 1) == 0)) ||
      (((DAT_febe661c >> 2 & 1) == 0 || ((DAT_febe6628 >> 1 & 1) != 0)))) ||
     (((DAT_febe6614 & 1) != 0 || (DAT_febe65f0 != 'Z')))) {
    return 0x44;
  }
  iVar3 = (int)DAT_0002b758;
  if (((iVar1 - iVar3 < 0 != (iVar1 < 0 != iVar3 < 0 && iVar3 < 0 == iVar1 - iVar3 < 0) ||
        iVar1 == iVar3) || (DAT_0002b756 < uVar2)) &&
     (((uint)DAT_0002b75a <= (uint)DAT_febe66ae || (uVar2 <= DAT_0002b756)))) {
    return 0x11;
  }
  return 0x22;
}



/* Set healthy-observed6120 bit via51E2C; does not clear current/retained diagnostic failure. Event
   selection 0x79. */

void f33_record_sample_difference_window_a_healthy_observed(void)

{
  f33_report_diagnostic_healthy_observed(0x79);
  return;
}



/* Call51C66(event,32 hex); diagnostic lifecycle rejection is separate from later control-action
   publication. Event selection 0x79. */

void f33_record_sample_difference_window_a_failure(void)

{
  f33_report_diagnostic_event_failure(0x79,0x32);
  return;
}



/* Return readiness latch in r10:5A means admitted, not a void side-effect-only helper. Retain
   completed latch until explicit stage initializer; pending sequencing and counts per
   configured-family readiness contract. No hardware success is inferred from this software latch.
    */

uint f33_admit_sample_difference_monitor_b(void)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  
  uVar2 = (uint)DAT_febe6808;
  iVar1 = (uint)DAT_febe66b8 - (uint)DAT_febe66b0;
  if (uVar2 != 0x5a) {
    if (DAT_febe65f0 == 'Z') {
      iVar3 = (int)DAT_0002b764;
      if ((iVar1 - iVar3 < 0 == (iVar1 < 0 != iVar3 < 0 && iVar3 < 0 == iVar1 - iVar3 < 0) &&
           iVar1 != iVar3) && (DAT_febe680a <= DAT_0002b75e)) {
        DAT_febe680a = DAT_febe680a + 1;
      }
      else {
        uVar2 = 0x5a;
      }
    }
    else {
      DAT_febe680a = 0;
    }
  }
  DAT_febe6808 = (char)uVar2;
  return uVar2;
}



/* Return readiness latch in r10:5A means admitted, not a void side-effect-only helper. Retain
   completed latch until explicit stage initializer; pending sequencing and counts per
   configured-family readiness contract. No hardware success is inferred from this software latch.
    */

uint f33_admit_sample_difference_elapsed_b(void)

{
  uint uVar1;
  
  uVar1 = (uint)DAT_febe6809;
  if (uVar1 != 0x5a) {
    if (DAT_febe680c < DAT_0002b760) {
      DAT_febe680c = DAT_febe680c + 1;
    }
    else {
      uVar1 = 0x5a;
    }
  }
  DAT_febe6809 = (char)uVar1;
  return uVar1;
}



/* No-argument configured classifier. Gate baseline_zero: same as baseline_one except6614.bit0==0.
   Closed gate returns44, otherwise22 iff (int32(uint16(66B8))-int32(uint16(66B0))>1180
   &&66B8<=4736) || (66B0<1055 &&66B8>4736), else11. Full threshold partitions preserved in ROM. No
   physical units/source identity asserted. */

uint f33_classify_sample_difference_window_b(void)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  
  uVar3 = (uint)DAT_febe66b8;
  iVar1 = uVar3 - DAT_febe66b0;
  if (((((DAT_febe64d9 != '\0') || (DAT_febe64d1 != '\0')) || ((DAT_febe6620 >> 0x12 & 1) == 0)) ||
      (((DAT_febe661c >> 0x12 & 1) == 0 || ((DAT_febe6628 >> 0x11 & 1) != 0)))) ||
     (((DAT_febe6614 & 1) != 0 || (DAT_febe65f0 != 'Z')))) {
    return 0x44;
  }
  iVar2 = (int)DAT_0002b764;
  if (((iVar1 - iVar2 < 0 != (iVar1 < 0 != iVar2 < 0 && iVar2 < 0 == iVar1 - iVar2 < 0) ||
        iVar1 == iVar2) || (DAT_0002b762 < uVar3)) &&
     (((uint)DAT_0002b766 <= (uint)DAT_febe66b0 || (uVar3 <= DAT_0002b762)))) {
    return 0x11;
  }
  return 0x22;
}



/* Set healthy-observed6120 bit via51E2C; does not clear current/retained diagnostic failure. Event
   selection 0xb8. */

void f33_record_sample_difference_window_b_healthy_observed(void)

{
  f33_report_diagnostic_healthy_observed(0xb8);
  return;
}



/* Call51C66(event,32 hex); diagnostic lifecycle rejection is separate from later control-action
   publication. Event selection 0xb8. */

void f33_record_sample_difference_window_b_failure(void)

{
  f33_report_diagnostic_event_failure(0xb8,0x32);
  return;
}



undefined4 FUN_00040424(void)

{
  int iVar1;
  uint32_t puVar2;
  undefined4 uVar3;
  int iVar4;
  int iVar5;
  ushort uVar6;
  ushort uVar7;
  ushort uVar8;
  
  puVar2 = 0xfebeb800u;
  uVar3 = 0;
  iVar5 = 0;
  iVar4 = 0;
  if (DAT_febe6814 < DAT_0002b76c) {
    iVar1 = 0;
    uVar8 = DAT_febe6814 + 1;
  }
  else {
    iVar1 = 0x5a;
    uVar8 = DAT_febe6814;
  }
  if (DAT_febe6816 < DAT_0002b76e) {
    uVar7 = DAT_febe6816 + 1;
  }
  else {
    iVar5 = 0x5a;
    uVar7 = DAT_febe6816;
  }
  if (DAT_febe6818 < DAT_0002b770) {
    uVar6 = DAT_febe6818 + 1;
  }
  else {
    iVar4 = 0x5a;
    uVar6 = DAT_febe6818;
  }
  if (((iVar1 == 0x5a) && (iVar5 == 0x5a)) && (iVar4 == 0x5a)) {
    puVar2 = 0xfebeb800u;
    if ((DAT_febe6764 & 1) == 0) {
      puVar2 = 0xfebeb800u;
      FUN_00056c26(DAT_febe6764 & 1,4);
    }
    uVar3 = 1;
  }
  (*((ushort *)camry_host_ptr((uint32_t)((0xffffb014u + (uint32_t)((int)puVar2)))))) = uVar8;
  (*((ushort *)camry_host_ptr((uint32_t)((0xffffb016u + (uint32_t)((int)puVar2)))))) = uVar7;
  (*((ushort *)camry_host_ptr((uint32_t)((0xffffb018u + (uint32_t)((int)puVar2)))))) = uVar6;
  return uVar3;
}



undefined4 FUN_0004049e(void)

{
  undefined4 uVar1;
  
  uVar1 = 1;
  if (DAT_febe681a < DAT_0002b772) {
    DAT_febe681a = DAT_febe681a + 1;
  }
  else {
    uVar1 = 2;
  }
  return uVar1;
}



/* Return readiness latch in r10:5A means admitted, not a void side-effect-only helper. Retain
   completed latch until explicit stage initializer; pending sequencing and counts per
   configured-family readiness contract. No hardware success is inferred from this software latch.
    */

uint f33_admit_matched_state2_status_monitor_a(void)

{
  undefined *puVar1;
  uint uVar2;
  int iVar3;
  uint uVar4;
  ushort uVar5;
  
  puVar1 = ((undefined *)camry_host_ptr(0xfebeb800u));
  uVar4 = (uint)DAT_febe6811;
  uVar2 = (uint)DAT_febe6810;
  uVar5 = DAT_febe6812;
  if (uVar4 != 0x5a) {
    if (DAT_0002b76a < DAT_febe6812) {
      iVar3 = 0x5a;
    }
    else {
      uVar5 = DAT_febe6812 + 1;
      iVar3 = 0;
    }
    if ((2 < uVar2) || (puVar1 = ((undefined *)camry_host_ptr(0xfebeb800u)), uVar2 == 0)) {
      puVar1 = ((undefined *)camry_host_ptr(0xfebeb800u));
      uVar2 = FUN_00040424();
    }
    if (uVar2 == 1) {
      uVar2 = FUN_0004049e();
    }
    if ((iVar3 == 0x5a) && (uVar2 == 2)) {
      uVar4 = 0x5a;
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb010u + (uint32_t)((int)camry_host_addr(puVar1)) * 1u)))) = (char)uVar2;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb011u + (uint32_t)((int)camry_host_addr(puVar1)) * 1u)))) = (char)uVar4;
  *(ushort *)(((undefined *)camry_host_ptr(0xffffb012u)) + (int)camry_host_addr(puVar1)) = uVar5;
  return uVar4;
}



/* No-argument configured classifier. Gate off_both2: requested==2 &&observed==2
   &&(6620&(6<<b))==(4<<b) &&(661C&(6<<b))==(4<<b) &&bit(6628,b+1)==0 &&6614.bit0==0 &&
   own65F6/65F7==5A. Closed gate returns44, otherwise22 iff 8282==5A, else11. Full threshold
   partitions preserved in ROM. No physical units/source identity asserted. */

uint f33_classify_matched_state2_status_bit_a(void)

{
  if ((((((DAT_febe64d8 == '\x02') && (DAT_febe64d0 == '\x02')) && ((DAT_febe6620 >> 1 & 1) == 0))
       && (((DAT_febe6620 >> 2 & 1) != 0 && ((DAT_febe661c >> 1 & 1) == 0)))) &&
      (((DAT_febe661c >> 2 & 1) != 0 &&
       (((DAT_febe6628 >> 1 & 1) == 0 && ((DAT_febe6614 & 1) == 0)))))) && (DAT_febe65f6 == 'Z')) {
    if (DAT_febe8282 != 'Z') {
      return 0x11;
    }
    return 0x22;
  }
  return 0x44;
}



/* Set healthy-observed6120 bit via51E2C; does not clear current/retained diagnostic failure. Event
   selection 0x78. */

void f33_record_matched_state2_status_bit_a_healthy_observed(void)

{
  f33_report_diagnostic_healthy_observed(0x78);
  return;
}



/* Call51C66(event,32 hex); diagnostic lifecycle rejection is separate from later control-action
   publication. Event selection 0x78. */

void f33_record_matched_state2_status_bit_a_failure(void)

{
  f33_report_diagnostic_event_failure(0x78,0x32);
  return;
}



undefined4 FUN_00040660(void)

{
  int iVar1;
  uint32_t puVar2;
  undefined4 uVar3;
  int iVar4;
  int iVar5;
  ushort uVar6;
  ushort uVar7;
  ushort uVar8;
  
  puVar2 = 0xfebeb800u;
  uVar3 = 0;
  iVar5 = 0;
  iVar4 = 0;
  if (DAT_febe6820 < DAT_0002b778) {
    iVar1 = 0;
    uVar8 = DAT_febe6820 + 1;
  }
  else {
    iVar1 = 0x5a;
    uVar8 = DAT_febe6820;
  }
  if (DAT_febe6822 < DAT_0002b77a) {
    uVar7 = DAT_febe6822 + 1;
  }
  else {
    iVar5 = 0x5a;
    uVar7 = DAT_febe6822;
  }
  if (DAT_febe6824 < DAT_0002b77c) {
    uVar6 = DAT_febe6824 + 1;
  }
  else {
    iVar4 = 0x5a;
    uVar6 = DAT_febe6824;
  }
  if (((iVar1 == 0x5a) && (iVar5 == 0x5a)) && (iVar4 == 0x5a)) {
    puVar2 = 0xfebeb800u;
    if ((DAT_febe6764 >> 1 & 1) == 0) {
      puVar2 = 0xfebeb800u;
      FUN_00056c26(1,0x40000);
    }
    uVar3 = 1;
  }
  (*((ushort *)camry_host_ptr((uint32_t)((0xffffb020u + (uint32_t)((int)puVar2)))))) = uVar8;
  (*((ushort *)camry_host_ptr((uint32_t)((0xffffb022u + (uint32_t)((int)puVar2)))))) = uVar7;
  (*((ushort *)camry_host_ptr((uint32_t)((0xffffb024u + (uint32_t)((int)puVar2)))))) = uVar6;
  return uVar3;
}



undefined4 FUN_000406da(void)

{
  undefined4 uVar1;
  
  uVar1 = 1;
  if (DAT_febe6826 < DAT_0002b77e) {
    DAT_febe6826 = DAT_febe6826 + 1;
  }
  else {
    uVar1 = 2;
  }
  return uVar1;
}



/* Return readiness latch in r10:5A means admitted, not a void side-effect-only helper. Retain
   completed latch until explicit stage initializer; pending sequencing and counts per
   configured-family readiness contract. No hardware success is inferred from this software latch.
    */

uint f33_admit_matched_state2_status_monitor_b(void)

{
  undefined *puVar1;
  uint uVar2;
  int iVar3;
  uint uVar4;
  ushort uVar5;
  
  puVar1 = ((undefined *)camry_host_ptr(0xfebeb800u));
  uVar4 = (uint)DAT_febe681d;
  uVar2 = (uint)DAT_febe681c;
  uVar5 = DAT_febe681e;
  if (uVar4 != 0x5a) {
    if (DAT_0002b776 < DAT_febe681e) {
      iVar3 = 0x5a;
    }
    else {
      uVar5 = DAT_febe681e + 1;
      iVar3 = 0;
    }
    if ((2 < uVar2) || (puVar1 = ((undefined *)camry_host_ptr(0xfebeb800u)), uVar2 == 0)) {
      puVar1 = ((undefined *)camry_host_ptr(0xfebeb800u));
      uVar2 = FUN_00040660();
    }
    if (uVar2 == 1) {
      uVar2 = FUN_000406da();
    }
    if ((iVar3 == 0x5a) && (uVar2 == 2)) {
      uVar4 = 0x5a;
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb01cu + (uint32_t)((int)camry_host_addr(puVar1)) * 1u)))) = (char)uVar2;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb01du + (uint32_t)((int)camry_host_addr(puVar1)) * 1u)))) = (char)uVar4;
  *(ushort *)(((undefined *)camry_host_ptr(0xffffb01eu)) + (int)camry_host_addr(puVar1)) = uVar5;
  return uVar4;
}



/* No-argument configured classifier. Gate off_both2: requested==2 &&observed==2
   &&(6620&(6<<b))==(4<<b) &&(661C&(6<<b))==(4<<b) &&bit(6628,b+1)==0 &&6614.bit0==0 &&
   own65F6/65F7==5A. Closed gate returns44, otherwise22 iff 8281==5A, else11. Full threshold
   partitions preserved in ROM. No physical units/source identity asserted. */

uint f33_classify_matched_state2_status_bit_b(void)

{
  if ((((((DAT_febe64d9 == '\x02') && (DAT_febe64d1 == '\x02')) && ((DAT_febe6620 >> 0x11 & 1) == 0)
        ) && (((DAT_febe6620 >> 0x12 & 1) != 0 && ((DAT_febe661c >> 0x11 & 1) == 0)))) &&
      (((DAT_febe661c & 0x40000) != 0 &&
       (((DAT_febe6628 >> 0x11 & 1) == 0 && ((DAT_febe6614 & 1) == 0)))))) && (DAT_febe65f7 == 'Z'))
  {
    if (DAT_febe8281 != 'Z') {
      return 0x11;
    }
    return 0x22;
  }
  return 0x44;
}



/* Set healthy-observed6120 bit via51E2C; does not clear current/retained diagnostic failure. Event
   selection 0xc4. */

void f33_record_matched_state2_status_bit_b_healthy_observed(void)

{
  f33_report_diagnostic_healthy_observed(0xc4);
  return;
}



/* Call51C66(event,32 hex); diagnostic lifecycle rejection is separate from later control-action
   publication. Event selection 0xc4. */

void f33_record_matched_state2_status_bit_b_failure(void)

{
  f33_report_diagnostic_event_failure(0xc4,0x32);
  return;
}



/* Return readiness latch in r10:5A means admitted, not a void side-effect-only helper. Retain
   completed latch until explicit stage initializer; pending sequencing and counts per
   configured-family readiness contract. No hardware success is inferred from this software latch.
    */

uint f33_admit_baseline_sample_monitor_a(void)

{
  uint uVar1;
  
  uVar1 = (uint)DAT_febe6828;
  if (uVar1 != 0x5a) {
    if (DAT_febe682a < DAT_0002b788) {
      DAT_febe682a = DAT_febe682a + 1;
    }
    else {
      uVar1 = 0x5a;
    }
  }
  DAT_febe6828 = (char)uVar1;
  return uVar1;
}



/* No-argument configured classifier. Gate baseline_zero: same as baseline_one except6614.bit0==0.
   Closed gate returns44, otherwise22 iff 66B2>1247 (both3328 partitions), else11. Full threshold
   partitions preserved in ROM. No physical units/source identity asserted. */

uint f33_classify_baseline_sample_threshold_a(void)

{
  if (((((DAT_febe64d8 != '\0') || (DAT_febe64d0 != '\0')) || ((DAT_febe6620 >> 2 & 1) == 0)) ||
      (((DAT_febe661c >> 2 & 1) == 0 || ((DAT_febe6628 >> 1 & 1) != 0)))) ||
     (((DAT_febe6614 & 1) != 0 || (DAT_febe65f0 != 'Z')))) {
    return 0x44;
  }
  if (((DAT_febe66b2 <= DAT_0002b784) || (DAT_0002b782 < DAT_febe66b8)) &&
     ((DAT_febe66b2 <= DAT_0002b786 || (DAT_febe66b8 <= DAT_0002b782)))) {
    return 0x11;
  }
  return 0x22;
}



/* Set healthy-observed6120 bit via51E2C; does not clear current/retained diagnostic failure. Event
   selection 0x9c. */

void f33_record_baseline_sample_threshold_a_healthy_observed(void)

{
  f33_report_diagnostic_healthy_observed(0x9c);
  return;
}



/* Call51C66(event,32 hex); diagnostic lifecycle rejection is separate from later control-action
   publication. Event selection 0x9c. */

void f33_record_baseline_sample_threshold_a_failure(void)

{
  f33_report_diagnostic_event_failure(0x9c,0x32);
  return;
}



/* Return readiness latch in r10:5A means admitted, not a void side-effect-only helper. Retain
   completed latch until explicit stage initializer; pending sequencing and counts per
   configured-family readiness contract. No hardware success is inferred from this software latch.
    */

uint f33_admit_baseline_sample_monitor_b(void)

{
  uint uVar1;
  
  uVar1 = (uint)DAT_febe682c;
  if (uVar1 != 0x5a) {
    if (DAT_febe682e < DAT_0002b790) {
      DAT_febe682e = DAT_febe682e + 1;
    }
    else {
      uVar1 = 0x5a;
    }
  }
  DAT_febe682c = (char)uVar1;
  return uVar1;
}



/* No-argument configured classifier. Gate baseline_zero: same as baseline_one except6614.bit0==0.
   Closed gate returns44, otherwise22 iff 66B4>1247 (both3328 partitions), else11. Full threshold
   partitions preserved in ROM. No physical units/source identity asserted. */

uint f33_classify_baseline_sample_threshold_b(void)

{
  if (((((DAT_febe64d9 != '\0') || (DAT_febe64d1 != '\0')) || ((DAT_febe6620 >> 0x12 & 1) == 0)) ||
      (((DAT_febe661c >> 0x12 & 1) == 0 || ((DAT_febe6628 >> 0x11 & 1) != 0)))) ||
     (((DAT_febe6614 & 1) != 0 || (DAT_febe65f0 != 'Z')))) {
    return 0x44;
  }
  if (((DAT_febe66b4 <= DAT_0002b78c) || (DAT_0002b78a < DAT_febe66b8)) &&
     ((DAT_febe66b4 <= DAT_0002b78e || (DAT_febe66b8 <= DAT_0002b78a)))) {
    return 0x11;
  }
  return 0x22;
}



/* Set healthy-observed6120 bit via51E2C; does not clear current/retained diagnostic failure. Event
   selection 0xc6. */

void f33_record_baseline_sample_threshold_b_healthy_observed(void)

{
  f33_report_diagnostic_healthy_observed(0xc6);
  return;
}



/* Call51C66(event,32 hex); diagnostic lifecycle rejection is separate from later control-action
   publication. Event selection 0xc6. */

void f33_record_baseline_sample_threshold_b_failure(void)

{
  f33_report_diagnostic_event_failure(0xc6,0x32);
  return;
}



undefined4 FUN_00040b8e(void)

{
  uint32_t puVar1;
  undefined4 uVar2;
  ushort uVar3;
  
  uVar3 = DAT_febe6832;
  puVar1 = 0xfebeb800u;
  if (DAT_febe6832 < DAT_0002b792) {
    uVar2 = 0;
    uVar3 = DAT_febe6832 + 1;
  }
  else {
    puVar1 = 0xfebeb800u;
    if ((DAT_febe6764 & 1) == 0) {
      puVar1 = 0xfebeb800u;
      FUN_000569ac(DAT_febe6764 & 1,2);
    }
    uVar2 = 1;
  }
  (*((ushort *)camry_host_ptr((uint32_t)((0xffffb032u + (uint32_t)((int)puVar1)))))) = uVar3;
  return uVar2;
}



undefined4 FUN_00040bc4(void)

{
  uint32_t puVar1;
  undefined4 uVar2;
  ushort uVar3;
  
  uVar3 = DAT_febe6836;
  puVar1 = 0xfebeb800u;
  if (DAT_febe6836 < DAT_0002b796) {
    uVar2 = 1;
    uVar3 = DAT_febe6836 + 1;
  }
  else {
    puVar1 = 0xfebeb800u;
    if ((DAT_febe6764 & 1) == 0) {
      puVar1 = 0xfebeb800u;
      FUN_00056f14(DAT_febe6764 & 1,2);
    }
    uVar2 = 2;
  }
  (*((ushort *)camry_host_ptr((uint32_t)((0xffffb036u + (uint32_t)((int)puVar1)))))) = uVar3;
  return uVar2;
}



undefined4 FUN_00040bfa(void)

{
  undefined4 uVar1;
  
  uVar1 = 2;
  if (DAT_febe6834 < DAT_0002b794) {
    DAT_febe6834 = DAT_febe6834 + 1;
  }
  else {
    uVar1 = 3;
  }
  return uVar1;
}



undefined4 FUN_00040c18(void)

{
  undefined4 uVar1;
  
  if (DAT_0002b798 < DAT_febe6838) {
    uVar1 = 0x5a;
  }
  else {
    DAT_febe6838 = DAT_febe6838 + 1;
    uVar1 = 0;
  }
  return uVar1;
}



/* Return readiness latch in r10:5A means admitted, not a void side-effect-only helper. Retain
   completed latch until explicit stage initializer; pending sequencing and counts per
   configured-family readiness contract. No hardware success is inferred from this software latch.
    */

uint f33_admit_observed_state_sample_monitor_a(void)

{
  undefined *puVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  
  puVar1 = ((undefined *)camry_host_ptr(0xfebeb800u));
  uVar3 = (uint)DAT_febe6831;
  uVar4 = (uint)DAT_febe6830;
  if (uVar3 != 0x5a) {
    if ((3 < uVar4) || (puVar1 = ((undefined *)camry_host_ptr(0xfebeb800u)), uVar4 == 0)) {
      puVar1 = ((undefined *)camry_host_ptr(0xfebeb800u));
      uVar4 = FUN_00040b8e();
    }
    if (uVar4 == 1) {
      uVar4 = FUN_00040bc4();
    }
    if (uVar4 == 2) {
      uVar4 = FUN_00040bfa();
    }
    if (((uVar4 < 4) && (iVar2 = FUN_00040c18(), uVar4 == 3)) && (iVar2 == 0x5a)) {
      uVar3 = 0x5a;
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb031u + (uint32_t)((int)camry_host_addr(puVar1)) * 1u)))) = (char)uVar3;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb030u + (uint32_t)((int)camry_host_addr(puVar1)) * 1u)))) = (char)uVar4;
  return uVar3;
}



/* No-argument configured classifier. Gate observed2_zero: requested==0 &&observed==2
   &&bit(6620,b+2)==1 &&(661C&(6<<b))==(2<<b) &&bit(6628,b+1)==1 &&6614.bit0==0 &&65F0==5A. Closed
   gate returns44, otherwise22 iff 66B2<886 ||66B2>6020 (six-region predicate partitions66B8
   at2816/4736 with equal lower/upper thresholds), else11. Full threshold partitions preserved in
   ROM. No physical units/source identity asserted. */

uint f33_classify_observed_state_sample_regions_a(void)

{
  if (((((DAT_febe64d8 != '\0') || (DAT_febe64d0 != '\x02')) || ((DAT_febe6620 >> 2 & 1) == 0)) ||
      (((DAT_febe661c >> 1 & 1) == 0 || ((DAT_febe661c >> 2 & 1) != 0)))) ||
     (((DAT_febe6628 >> 1 & 1) == 0 || (((DAT_febe6614 & 1) != 0 || (DAT_febe65f0 != 'Z')))))) {
    return 0x44;
  }
  if (((DAT_0002b79e <= DAT_febe66b2) || (DAT_0002b79a < DAT_febe66b8)) &&
     ((((((DAT_0002b7a0 <= DAT_febe66b2 || (DAT_febe66b8 <= DAT_0002b79a)) ||
         (DAT_0002b79c < DAT_febe66b8)) &&
        (((DAT_0002b7a2 <= DAT_febe66b2 || (DAT_febe66b8 <= DAT_0002b79c)) &&
         ((DAT_febe66b2 <= DAT_0002b7a4 || (DAT_0002b79a < DAT_febe66b8)))))) &&
       (((DAT_febe66b2 <= DAT_0002b7a6 || (DAT_febe66b8 <= DAT_0002b79a)) ||
        (DAT_0002b79c < DAT_febe66b8)))) &&
      ((DAT_febe66b2 <= DAT_0002b7a8 || (DAT_febe66b8 <= DAT_0002b79c)))))) {
    return 0x11;
  }
  return 0x22;
}



/* Set healthy-observed6120 bit via51E2C; does not clear current/retained diagnostic failure. Event
   selection 0x7b. */

void f33_record_observed_state_sample_regions_a_healthy_observed(void)

{
  f33_report_diagnostic_healthy_observed(0x7b);
  return;
}



/* Call51C66(event,32 hex); diagnostic lifecycle rejection is separate from later control-action
   publication. Event selection 0x7b. */

void f33_record_observed_state_sample_regions_a_failure(void)

{
  f33_report_diagnostic_event_failure(0x7b,0x32);
  return;
}



undefined4 FUN_00040e28(void)

{
  uint32_t puVar1;
  undefined4 uVar2;
  ushort uVar3;
  
  uVar3 = DAT_febe683e;
  puVar1 = 0xfebeb800u;
  if (DAT_febe683e < DAT_0002b7aa) {
    uVar2 = 0;
    uVar3 = DAT_febe683e + 1;
  }
  else {
    puVar1 = 0xfebeb800u;
    if ((DAT_febe6764 >> 1 & 1) == 0) {
      puVar1 = 0xfebeb800u;
      FUN_000569ac(1,0x20000);
    }
    uVar2 = 1;
  }
  (*((ushort *)camry_host_ptr((uint32_t)((0xffffb03eu + (uint32_t)((int)puVar1)))))) = uVar3;
  return uVar2;
}



undefined4 FUN_00040e5e(void)

{
  uint32_t puVar1;
  undefined4 uVar2;
  ushort uVar3;
  
  uVar3 = DAT_febe6842;
  puVar1 = 0xfebeb800u;
  uVar2 = 1;
  if (DAT_febe6842 < DAT_0002b7ae) {
    uVar3 = DAT_febe6842 + 1;
  }
  else {
    puVar1 = 0xfebeb800u;
    if ((DAT_febe6764 >> 1 & 1) == 0) {
      puVar1 = 0xfebeb800u;
      FUN_00056f14(1,0x20000);
    }
    uVar2 = 2;
  }
  (*((ushort *)camry_host_ptr((uint32_t)((int)(0xffffb042u + (uint32_t)((int)puVar1)))))) = uVar3;
  return uVar2;
}



undefined4 FUN_00040e94(void)

{
  undefined4 uVar1;
  
  uVar1 = 2;
  if (DAT_febe6840 < DAT_0002b7ac) {
    DAT_febe6840 = DAT_febe6840 + 1;
  }
  else {
    uVar1 = 3;
  }
  return uVar1;
}



undefined4 FUN_00040eb2(void)

{
  undefined4 uVar1;
  
  if (DAT_0002b7b0 < DAT_febe6844) {
    uVar1 = 0x5a;
  }
  else {
    DAT_febe6844 = DAT_febe6844 + 1;
    uVar1 = 0;
  }
  return uVar1;
}



/* Return readiness latch in r10:5A means admitted, not a void side-effect-only helper. Retain
   completed latch until explicit stage initializer; pending sequencing and counts per
   configured-family readiness contract. No hardware success is inferred from this software latch.
    */

uint f33_admit_observed_state_sample_monitor_b(void)

{
  undefined *puVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  
  puVar1 = ((undefined *)camry_host_ptr(0xfebeb800u));
  uVar3 = (uint)DAT_febe683d;
  uVar4 = (uint)DAT_febe683c;
  if (uVar3 != 0x5a) {
    if ((3 < uVar4) || (puVar1 = ((undefined *)camry_host_ptr(0xfebeb800u)), uVar4 == 0)) {
      puVar1 = ((undefined *)camry_host_ptr(0xfebeb800u));
      uVar4 = FUN_00040e28();
    }
    if (uVar4 == 1) {
      uVar4 = FUN_00040e5e();
    }
    if (uVar4 == 2) {
      uVar4 = FUN_00040e94();
    }
    if (((uVar4 < 4) && (iVar2 = FUN_00040eb2(), uVar4 == 3)) && (iVar2 == 0x5a)) {
      uVar3 = 0x5a;
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb03du + (uint32_t)((int)camry_host_addr(puVar1)) * 1u)))) = (char)uVar3;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb03cu + (uint32_t)((int)camry_host_addr(puVar1)) * 1u)))) = (char)uVar4;
  return uVar3;
}



/* No-argument configured classifier. Gate observed2_zero: requested==0 &&observed==2
   &&bit(6620,b+2)==1 &&(661C&(6<<b))==(2<<b) &&bit(6628,b+1)==1 &&6614.bit0==0 &&65F0==5A. Closed
   gate returns44, otherwise22 iff 66B4<886 ||66B4>6020 (six-region predicate partitions66B8
   at2816/4736 with equal lower/upper thresholds), else11. Full threshold partitions preserved in
   ROM. No physical units/source identity asserted. */

uint f33_classify_observed_state_sample_regions_b(void)

{
  if (((((DAT_febe64d9 != '\0') || (DAT_febe64d1 != '\x02')) || ((DAT_febe6620 >> 0x12 & 1) == 0))
      || (((DAT_febe661c >> 0x11 & 1) == 0 || ((DAT_febe661c & 0x40000) != 0)))) ||
     (((DAT_febe6628 >> 0x11 & 1) == 0 || (((DAT_febe6614 & 1) != 0 || (DAT_febe65f0 != 'Z')))))) {
    return 0x44;
  }
  if (((DAT_0002b7b6 <= DAT_febe66b4) || (DAT_0002b7b2 < DAT_febe66b8)) &&
     ((((((DAT_0002b7b8 <= DAT_febe66b4 || (DAT_febe66b8 <= DAT_0002b7b2)) ||
         (DAT_0002b7b4 < DAT_febe66b8)) &&
        (((DAT_0002b7ba <= DAT_febe66b4 || (DAT_febe66b8 <= DAT_0002b7b4)) &&
         ((DAT_febe66b4 <= DAT_0002b7bc || (DAT_0002b7b2 < DAT_febe66b8)))))) &&
       (((DAT_febe66b4 <= DAT_0002b7be || (DAT_febe66b8 <= DAT_0002b7b2)) ||
        (DAT_0002b7b4 < DAT_febe66b8)))) &&
      ((DAT_febe66b4 <= DAT_0002b7c0 || (DAT_febe66b8 <= DAT_0002b7b4)))))) {
    return 0x11;
  }
  return 0x22;
}



/* Set healthy-observed6120 bit via51E2C; does not clear current/retained diagnostic failure. Event
   selection 0xba. */

void f33_record_observed_state_sample_regions_b_healthy_observed(void)

{
  f33_report_diagnostic_healthy_observed(0xba);
  return;
}



/* Call51C66(event,32 hex); diagnostic lifecycle rejection is separate from later control-action
   publication. Event selection 0xba. */

void f33_record_observed_state_sample_regions_b_failure(void)

{
  f33_report_diagnostic_event_failure(0xba,0x32);
  return;
}



void FUN_00041096(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe76ac = 0;
  DAT_febe76ae = 0;
  DAT_febe76b0 = 0;
  f33_reset_terminal_monitor(f33_sample_range_triplet_a_states);
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbe9cu + (uint32_t)((int)puVar1))))));
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbea4u + (uint32_t)((int)puVar1))))));
  return;
}



void FUN_000410c0(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe684a = 0;
  f33_reset_terminal_monitor(f33_sample_range_triplet_a_states);
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbe9cu + (uint32_t)((int)puVar1))))));
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbea4u + (uint32_t)((int)puVar1))))));
  return;
}



/* Return readiness latch in r10:5A means admitted, not a void side-effect-only helper. Retain
   completed latch until explicit stage initializer; pending sequencing and counts per
   configured-family readiness contract. No hardware success is inferred from this software latch.
    */

uint f33_admit_sample_range_triplet_a(void)

{
  uint uVar1;
  
  uVar1 = (uint)DAT_febe6848;
  if (uVar1 != 0x5a) {
    if (DAT_febe684c < DAT_0002b7c6) {
      DAT_febe684c = DAT_febe684c + 1;
    }
    else {
      uVar1 = 0x5a;
    }
  }
  DAT_febe6848 = (char)uVar1;
  return uVar1;
}



/* No-argument configured classifier. Gate range_both2: same as off_both2 but admission
   own65F2/65F3==5A. Closed gate returns44, otherwise22 iff scratch_u16>54526 selects first event;
   scratch_u16<10224 selects second event; inclusive10224..54526 healthy, else11. Full threshold
   partitions preserved in ROM. No physical units/source identity asserted. */

uint f33_classify_sample_range_triplet_a(void)

{
  undefined2 uVar1;
  
  if ((((((DAT_febe64d8 == '\x02') && (DAT_febe64d0 == '\x02')) && ((DAT_febe6620 >> 1 & 1) == 0))
       && (((DAT_febe6620 >> 2 & 1) != 0 && ((DAT_febe661c >> 1 & 1) == 0)))) &&
      (((DAT_febe661c >> 2 & 1) != 0 &&
       (((DAT_febe6628 >> 1 & 1) == 0 && ((DAT_febe6614 & 1) == 0)))))) && (DAT_febe65f2 == 'Z')) {
    uVar1 = DAT_febe76ac;
    if ((DAT_febe76b0 <= DAT_0002b7c2) && (uVar1 = DAT_febe76ae, DAT_0002b7c4 <= DAT_febe76b0)) {
      return 0x11;
    }
    DAT_febe684a = uVar1;
    return 0x22;
  }
  return 0x44;
}



/* Set healthy-observed6120 bit via51E2C; does not clear current/retained diagnostic failure. Event
   selection is mutable source scratch before each engine invocation. */

void f33_record_sample_range_triplet_a_healthy_observed(void)

{
  uint event;
  
  event = (uint)DAT_febe76ae;
  f33_report_diagnostic_healthy_observed((uint)DAT_febe76ac);
  f33_report_diagnostic_healthy_observed(event);
  return;
}



/* Call51C66(event,32 hex); diagnostic lifecycle rejection is separate from later control-action
   publication. Event selection uses persistent684A/6852 written only by actually executed range
   predicate. */

void f33_record_sample_range_triplet_a_failure(void)

{
  f33_report_diagnostic_event_failure((uint)DAT_febe684a,0x32);
  return;
}



void FUN_00041300(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe76cc = 0;
  DAT_febe76ce = 0;
  DAT_febe76d0 = 0;
  f33_reset_terminal_monitor(f33_sample_range_triplet_b_states);
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbebcu + (uint32_t)((int)puVar1))))));
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbec4u + (uint32_t)((int)puVar1))))));
  return;
}



void FUN_0004132a(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe6852 = 0;
  f33_reset_terminal_monitor(f33_sample_range_triplet_b_states);
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbebcu + (uint32_t)((int)puVar1))))));
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbec4u + (uint32_t)((int)puVar1))))));
  return;
}



/* Return readiness latch in r10:5A means admitted, not a void side-effect-only helper. Retain
   completed latch until explicit stage initializer; pending sequencing and counts per
   configured-family readiness contract. No hardware success is inferred from this software latch.
    */

uint f33_admit_sample_range_triplet_b(void)

{
  uint uVar1;
  
  uVar1 = (uint)DAT_febe6850;
  if (uVar1 != 0x5a) {
    if (DAT_febe6854 < DAT_0002b7ce) {
      DAT_febe6854 = DAT_febe6854 + 1;
    }
    else {
      uVar1 = 0x5a;
    }
  }
  DAT_febe6850 = (char)uVar1;
  return uVar1;
}



/* No-argument configured classifier. Gate range_both2: same as off_both2 but admission
   own65F2/65F3==5A. Closed gate returns44, otherwise22 iff same unsigned range10224..54526;
   first/second eventF5..F7/F8..FA, else11. Full threshold partitions preserved in ROM. No physical
   units/source identity asserted. */

uint f33_classify_sample_range_triplet_b(void)

{
  undefined2 uVar1;
  
  if ((((((DAT_febe64d9 == '\x02') && (DAT_febe64d1 == '\x02')) && ((DAT_febe6620 >> 0x11 & 1) == 0)
        ) && (((DAT_febe6620 >> 0x12 & 1) != 0 && ((DAT_febe661c >> 0x11 & 1) == 0)))) &&
      (((DAT_febe661c & 0x40000) != 0 &&
       (((DAT_febe6628 >> 0x11 & 1) == 0 && ((DAT_febe6614 & 1) == 0)))))) && (DAT_febe65f3 == 'Z'))
  {
    uVar1 = DAT_febe76cc;
    if ((DAT_febe76d0 <= DAT_0002b7ca) && (uVar1 = DAT_febe76ce, DAT_0002b7cc <= DAT_febe76d0)) {
      return 0x11;
    }
    DAT_febe6852 = uVar1;
    return 0x22;
  }
  return 0x44;
}



/* Set healthy-observed6120 bit via51E2C; does not clear current/retained diagnostic failure. Event
   selection is mutable source scratch before each engine invocation. */

void f33_record_sample_range_triplet_b_healthy_observed(void)

{
  uint event;
  
  event = (uint)DAT_febe76ce;
  f33_report_diagnostic_healthy_observed((uint)DAT_febe76cc);
  f33_report_diagnostic_healthy_observed(event);
  return;
}



/* Call51C66(event,32 hex); diagnostic lifecycle rejection is separate from later control-action
   publication. Event selection uses persistent684A/6852 written only by actually executed range
   predicate. */

void f33_record_sample_range_triplet_b_failure(void)

{
  f33_report_diagnostic_event_failure((uint)DAT_febe6852,0x32);
  return;
}



void FUN_0004156e(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe76ec = 0;
  DAT_febe76ee = 0;
  f33_reset_terminal_monitor(f33_startup_status_bit_triplet_a_states);
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbedcu + (uint32_t)((int)puVar1))))));
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbee4u + (uint32_t)((int)puVar1))))));
  return;
}



void FUN_00041596(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe6858 = 0;
  DAT_febe6859 = 0;
  DAT_febe685a = 0;
  f33_reset_terminal_monitor(f33_startup_status_bit_triplet_a_states);
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbedcu + (uint32_t)((int)puVar1))))));
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbee4u + (uint32_t)((int)puVar1))))));
  return;
}



/* No-argument configured classifier. Gate baseline_one: requested==0 && observed==0 &&
   bit(6620,b+2)==1 && bit(661C,b+2)==1 && bit(6628,b+1)==0 && bit(6614,0)==1 &&65F0==5A. Closed
   gate returns44, otherwise22 iff scratch_byte==5A, else11. Full threshold partitions preserved in
   ROM. No physical units/source identity asserted. */

uint f33_classify_startup_status_bit_triplet_a(void)

{
  if ((((DAT_febe64d8 == '\0') && (DAT_febe64d0 == '\0')) && ((DAT_febe6620 >> 2 & 1) != 0)) &&
     ((((DAT_febe661c >> 2 & 1) != 0 && ((DAT_febe6628 >> 1 & 1) == 0)) &&
      (((DAT_febe6614 & 1) != 0 && (DAT_febe65f0 == 'Z')))))) {
    if (DAT_febe76ec != 'Z') {
      return 0x11;
    }
    return 0x22;
  }
  return 0x44;
}



/* Set healthy-observed6120 bit via51E2C; does not clear current/retained diagnostic failure. Event
   selection is mutable source scratch before each engine invocation. */

void f33_record_startup_status_bit_triplet_a_healthy_observed(void)

{
  f33_report_diagnostic_healthy_observed((uint)DAT_febe76ee);
  return;
}



/* Call51C66(event,32 hex); diagnostic lifecycle rejection is separate from later control-action
   publication. Event selection is mutable source scratch before each engine invocation. */

void f33_record_startup_status_bit_triplet_a_failure(void)

{
  f33_report_diagnostic_event_failure((uint)DAT_febe76ee,0x32);
  return;
}



void FUN_000417a6(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe7708 = 0;
  DAT_febe770a = 0;
  f33_reset_terminal_monitor(f33_startup_status_bit_triplet_b_states);
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbef8u + (uint32_t)((int)puVar1))))));
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbf00u + (uint32_t)((int)puVar1))))));
  return;
}



void FUN_000417ce(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe685c = 0;
  DAT_febe685d = 0;
  DAT_febe685e = 0;
  f33_reset_terminal_monitor(f33_startup_status_bit_triplet_b_states);
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbef8u + (uint32_t)((int)puVar1))))));
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbf00u + (uint32_t)((int)puVar1))))));
  return;
}



/* No-argument configured classifier. Gate baseline_one: requested==0 && observed==0 &&
   bit(6620,b+2)==1 && bit(661C,b+2)==1 && bit(6628,b+1)==0 && bit(6614,0)==1 &&65F0==5A. Closed
   gate returns44, otherwise22 iff scratch_byte==5A, else11. Full threshold partitions preserved in
   ROM. No physical units/source identity asserted. */

uint f33_classify_startup_status_bit_triplet_b(void)

{
  if ((((DAT_febe64d9 == '\0') && (DAT_febe64d1 == '\0')) && ((DAT_febe6620 >> 0x12 & 1) != 0)) &&
     ((((DAT_febe661c >> 0x12 & 1) != 0 && ((DAT_febe6628 >> 0x11 & 1) == 0)) &&
      (((DAT_febe6614 & 1) != 0 && (DAT_febe65f0 == 'Z')))))) {
    if (DAT_febe7708 != 'Z') {
      return 0x11;
    }
    return 0x22;
  }
  return 0x44;
}



/* Set healthy-observed6120 bit via51E2C; does not clear current/retained diagnostic failure. Event
   selection is mutable source scratch before each engine invocation. */

void f33_record_startup_status_bit_triplet_b_healthy_observed(void)

{
  f33_report_diagnostic_healthy_observed((uint)DAT_febe770a);
  return;
}



/* Call51C66(event,32 hex); diagnostic lifecycle rejection is separate from later control-action
   publication. Event selection is mutable source scratch before each engine invocation. */

void f33_record_startup_status_bit_triplet_b_failure(void)

{
  f33_report_diagnostic_event_failure((uint)DAT_febe770a,0x32);
  return;
}



void FUN_000419de(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe7724 = 0;
  DAT_febe7726 = 0;
  f33_reset_terminal_monitor(f33_matched_state2_startup_triplet_a_states);
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbf14u + (uint32_t)((int)puVar1))))));
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbf1cu + (uint32_t)((int)puVar1))))));
  return;
}



void FUN_00041a06(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe6860 = 0;
  DAT_febe6861 = 0;
  f33_reset_terminal_monitor(f33_matched_state2_startup_triplet_a_states);
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbf14u + (uint32_t)((int)puVar1))))));
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbf1cu + (uint32_t)((int)puVar1))))));
  return;
}



/* No-argument configured classifier. Gate off_both2: requested==2 &&observed==2
   &&(6620&(6<<b))==(4<<b) &&(661C&(6<<b))==(4<<b) &&bit(6628,b+1)==0 &&6614.bit0==0 &&
   own65F6/65F7==5A. Closed gate returns44, otherwise22 iff scratch_byte==5A, else11. Full threshold
   partitions preserved in ROM. No physical units/source identity asserted. */

uint f33_classify_matched_state2_startup_triplet_a(void)

{
  if ((((((DAT_febe64d8 == '\x02') && (DAT_febe64d0 == '\x02')) && ((DAT_febe6620 >> 1 & 1) == 0))
       && (((DAT_febe6620 >> 2 & 1) != 0 && ((DAT_febe661c >> 1 & 1) == 0)))) &&
      (((DAT_febe661c >> 2 & 1) != 0 &&
       (((DAT_febe6628 >> 1 & 1) == 0 && ((DAT_febe6614 & 1) == 0)))))) && (DAT_febe65f6 == 'Z')) {
    if (DAT_febe7724 != 'Z') {
      return 0x11;
    }
    return 0x22;
  }
  return 0x44;
}



/* Set healthy-observed6120 bit via51E2C; does not clear current/retained diagnostic failure. Event
   selection is mutable source scratch before each engine invocation. */

void f33_record_matched_state2_startup_triplet_a_healthy_observed(void)

{
  f33_report_diagnostic_healthy_observed((uint)DAT_febe7726);
  return;
}



/* Call51C66(event,32 hex); diagnostic lifecycle rejection is separate from later control-action
   publication. Event selection is mutable source scratch before each engine invocation. */

void f33_record_matched_state2_startup_triplet_a_failure(void)

{
  f33_report_diagnostic_event_failure((uint)DAT_febe7726,0x32);
  return;
}



void FUN_00041c0e(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe7740 = 0;
  DAT_febe7742 = 0;
  f33_reset_terminal_monitor(f33_matched_state2_startup_triplet_b_states);
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbf30u + (uint32_t)((int)puVar1))))));
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbf38u + (uint32_t)((int)puVar1))))));
  return;
}



void FUN_00041c36(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe6864 = 0;
  DAT_febe6865 = 0;
  f33_reset_terminal_monitor(f33_matched_state2_startup_triplet_b_states);
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbf30u + (uint32_t)((int)puVar1))))));
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbf38u + (uint32_t)((int)puVar1))))));
  return;
}



/* No-argument configured classifier. Gate off_both2: requested==2 &&observed==2
   &&(6620&(6<<b))==(4<<b) &&(661C&(6<<b))==(4<<b) &&bit(6628,b+1)==0 &&6614.bit0==0 &&
   own65F6/65F7==5A. Closed gate returns44, otherwise22 iff scratch_byte==5A, else11. Full threshold
   partitions preserved in ROM. No physical units/source identity asserted. */

uint f33_classify_matched_state2_startup_triplet_b(void)

{
  if ((((((DAT_febe64d9 == '\x02') && (DAT_febe64d1 == '\x02')) && ((DAT_febe6620 >> 0x11 & 1) == 0)
        ) && (((DAT_febe6620 >> 0x12 & 1) != 0 && ((DAT_febe661c >> 0x11 & 1) == 0)))) &&
      (((DAT_febe661c & 0x40000) != 0 &&
       (((DAT_febe6628 >> 0x11 & 1) == 0 && ((DAT_febe6614 & 1) == 0)))))) && (DAT_febe65f7 == 'Z'))
  {
    if (DAT_febe7740 != 'Z') {
      return 0x11;
    }
    return 0x22;
  }
  return 0x44;
}



/* Set healthy-observed6120 bit via51E2C; does not clear current/retained diagnostic failure. Event
   selection is mutable source scratch before each engine invocation. */

void f33_record_matched_state2_startup_triplet_b_healthy_observed(void)

{
  f33_report_diagnostic_healthy_observed((uint)DAT_febe7742);
  return;
}



/* Call51C66(event,32 hex); diagnostic lifecycle rejection is separate from later control-action
   publication. Event selection is mutable source scratch before each engine invocation. */

void f33_record_matched_state2_startup_triplet_b_failure(void)

{
  f33_report_diagnostic_event_failure((uint)DAT_febe7742,0x32);
  return;
}



void FUN_00041e42(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe7744 = 0;
  DAT_febe7746 = 0;
  DAT_febe7748 = 0;
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe774cu)));
  f33_reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xffffbf58u + (uint32_t)((int)puVar1))))));
  f33_reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xffffbf64u + (uint32_t)((int)puVar1))))));
  return;
}



void FUN_00041e6c(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe7744 = 0;
  DAT_febe7746 = 0;
  DAT_febe7748 = 0;
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe774cu)));
  f33_reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xffffbf58u + (uint32_t)((int)puVar1))))));
  f33_reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xffffbf64u + (uint32_t)((int)puVar1))))));
  return;
}



void FUN_00041e96(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bbe4 == 'Z') {
    f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe774cu)));
    f33_reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xffffbf58u + (uint32_t)((int)puVar1))))));
    f33_reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xffffbf64u + (uint32_t)((int)puVar1))))));
  }
  else if ((DAT_febe71ec & 1) == 0) {
    DAT_febe7744 = 0x4a;
    DAT_febe7746 = f33_monitor_current_second_midpoint_plane[0];
    DAT_febe7748 = f33_monitor_current_first_midpoint_plane[0];
    f33_step_latched_monitor
              ((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe774cu)),(F33MonitorLimits *)&PTR_DAT_0002b7e4,
               (F33TwoSidedMonitorCallbacks *)&PTR_f33_classify_channel_negative_pair_a_00028508);
    (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffbf44u + (uint32_t)((int)puVar1)))))) = 0x4b;
    (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffbf46u + (uint32_t)((int)puVar1)))))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x397a))));
    (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffbf48u + (uint32_t)((int)puVar1)))))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x396e))));
    f33_step_latched_monitor
              (((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xffffbf58u + (uint32_t)((int)puVar1))))),
               (F33MonitorLimits *)&PTR_DAT_0002b7e4,
               (F33TwoSidedMonitorCallbacks *)&PTR_f33_classify_channel_negative_pair_a_00028508);
    (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffbf44u + (uint32_t)((int)puVar1)))))) = 0x4c;
    (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffbf46u + (uint32_t)((int)puVar1)))))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x3978))));
    (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffbf48u + (uint32_t)((int)puVar1)))))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x396c))));
    f33_step_latched_monitor
              (((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xffffbf64u + (uint32_t)((int)puVar1))))),
               (F33MonitorLimits *)&PTR_DAT_0002b7e4,
               (F33TwoSidedMonitorCallbacks *)&PTR_f33_classify_channel_negative_pair_a_00028508);
  }
  else {
    f33_retain_disabled_latched_monitor
              ((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe774cu)),(F33MonitorLimits *)&PTR_DAT_0002b7e4);
    f33_retain_disabled_latched_monitor
              (((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xffffbf58u + (uint32_t)((int)puVar1))))),
               (F33MonitorLimits *)&PTR_DAT_0002b7e4);
    f33_retain_disabled_latched_monitor
              (((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xffffbf64u + (uint32_t)((int)puVar1))))),
               (F33MonitorLimits *)&PTR_DAT_0002b7e4);
  }
  f33_set_channel_monitor_status_a(4,(uchar)(*((undefined4 *)camry_host_ptr((uint32_t)((0xffffbf4cu + (uint32_t)((int)puVar1)))))));
  f33_set_channel_monitor_status_a(5,(uchar)(*((undefined4 *)camry_host_ptr((uint32_t)((0xffffbf58u + (uint32_t)((int)puVar1)))))));
  f33_set_channel_monitor_status_a(6,(uchar)(*((undefined4 *)camry_host_ptr((uint32_t)((0xffffbf64u + (uint32_t)((int)puVar1)))))));
  return;
}



/* ROM28508 predicate: both signed comparison members<-19968 return22, otherwise11. Recovered
   ROM28508 callback returns22 only when both signed comparison members are strictly below-19968;
   otherwise11. */

uint f33_classify_channel_negative_pair_a(void)

{
  int iVar1;
  int iVar2;
  
  iVar2 = (int)DAT_0002b80e;
  iVar1 = DAT_febe7746 - iVar2;
  if ((iVar1 < 0 != (DAT_febe7746 < 0 != iVar2 < 0 && iVar2 < 0 == iVar1 < 0)) &&
     (iVar2 = (int)DAT_0002b810, iVar1 = DAT_febe7748 - iVar2,
     iVar1 < 0 != (DAT_febe7748 < 0 != iVar2 < 0 && iVar2 < 0 == iVar1 < 0))) {
    return 0x22;
  }
  return 0x11;
}



/* f33_report_diagnostic_healthy_observed((uint)DAT_febe7744); whole-body shape-verified. The
   literal is the encoded diagnostic event, not a recovered OEM name. */

void f33_report_diagnostic_healthy_observed_cell_41f9a(void)

{
  f33_report_diagnostic_healthy_observed((uint)DAT_febe7744);
  return;
}



/* f33_report_diagnostic_event_failure((uint)DAT_febe7744,10); whole-body shape-verified. The
   literal is the encoded diagnostic event, not a recovered OEM name. */

void f33_report_diagnostic_event_failure_10_41faa(void)

{
  f33_report_diagnostic_event_failure((uint)DAT_febe7744,10);
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_41fbc(void)

{
  return;
}



void FUN_00041fbe(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  if (DAT_febe62f8 + 0x7fff < 0 == (-1 < DAT_febe62f8 && DAT_febe62f8 + 0x7fff < 0) &&
      DAT_febe62f8 != -0x7fff) {
    iVar3 = DAT_febe62f8;
    if (DAT_febe62f8 + -0x7fff < 0 == (DAT_febe62f8 < 0 && -1 < DAT_febe62f8 + -0x7fff) &&
        DAT_febe62f8 != 0x7fff) {
      iVar3 = 0x7fff;
    }
  }
  else {
    iVar3 = -0x7fff;
  }
  if (DAT_febe62fc + 0x7fff < 0 == (-1 < DAT_febe62fc && DAT_febe62fc + 0x7fff < 0) &&
      DAT_febe62fc != -0x7fff) {
    iVar2 = DAT_febe62fc;
    if (DAT_febe62fc + -0x7fff < 0 == (DAT_febe62fc < 0 && -1 < DAT_febe62fc + -0x7fff) &&
        DAT_febe62fc != 0x7fff) {
      iVar2 = 0x7fff;
    }
  }
  else {
    iVar2 = -0x7fff;
  }
  if (DAT_febe6300 + 0x7fff < 0 == (-1 < DAT_febe6300 && DAT_febe6300 + 0x7fff < 0) &&
      DAT_febe6300 != -0x7fff) {
    iVar1 = DAT_febe6300;
    if (DAT_febe6300 + -0x7fff < 0 == (DAT_febe6300 < 0 && -1 < DAT_febe6300 + -0x7fff) &&
        DAT_febe6300 != 0x7fff) {
      iVar1 = 0x7fff;
    }
  }
  else {
    iVar1 = -0x7fff;
  }
  DAT_febe7770 = (short)iVar3;
  DAT_febe7772 = (short)iVar2;
  DAT_febe7774 = (short)iVar1;
  DAT_febe7778 = iVar3 << 0x10;
  DAT_febe777c = iVar2 << 0x10;
  DAT_febe7780 = iVar1 << 0x10;
  return;
}



/* WARNING: Removing unreachable block (ram,0x00042124) */
/* WARNING: Removing unreachable block (ram,0x000420f8) */
/* WARNING: Removing unreachable block (ram,0x000420d8) */

void FUN_00042030(void)

{
  uint uVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  
  if (DAT_febe62f8 + 0x7fff < 0 == (-1 < DAT_febe62f8 && DAT_febe62f8 + 0x7fff < 0) &&
      DAT_febe62f8 != -0x7fff) {
    iVar2 = (int)(short)DAT_febe62f8;
    if (DAT_febe62f8 + -0x7fff < 0 == (DAT_febe62f8 < 0 && -1 < DAT_febe62f8 + -0x7fff) &&
        DAT_febe62f8 != 0x7fff) {
      iVar2 = 0x7fff;
    }
  }
  else {
    iVar2 = -0x7fff;
  }
  if (DAT_febe62fc + 0x7fff < 0 == (-1 < DAT_febe62fc && DAT_febe62fc + 0x7fff < 0) &&
      DAT_febe62fc != -0x7fff) {
    iVar3 = (int)(short)DAT_febe62fc;
    if (DAT_febe62fc + -0x7fff < 0 == (DAT_febe62fc < 0 && -1 < DAT_febe62fc + -0x7fff) &&
        DAT_febe62fc != 0x7fff) {
      iVar3 = 0x7fff;
    }
  }
  else {
    iVar3 = -0x7fff;
  }
  if (DAT_febe6300 + 0x7fff < 0 == (-1 < DAT_febe6300 && DAT_febe6300 + 0x7fff < 0) &&
      DAT_febe6300 != -0x7fff) {
    iVar4 = (int)(short)DAT_febe6300;
    if (DAT_febe6300 + -0x7fff < 0 == (DAT_febe6300 < 0 && -1 < DAT_febe6300 + -0x7fff) &&
        DAT_febe6300 != 0x7fff) {
      iVar4 = 0x7fff;
    }
  }
  else {
    iVar4 = -0x7fff;
  }
  uVar1 = (uint)DAT_0002b812;
  if (uVar1 - 1 < 0xffff) {
    iVar5 = (int)DAT_febe7770 * uVar1;
    iVar2 = iVar2 * uVar1;
  }
  else {
    iVar5 = (int)DAT_febe7770 << 0x10;
    iVar2 = iVar2 << 0x10;
  }
  DAT_febe7778 = iVar2 + (DAT_febe7778 - iVar5);
  if (uVar1 - 1 < 0xffff) {
    iVar2 = (int)DAT_febe7772 * uVar1;
    iVar3 = iVar3 * uVar1;
  }
  else {
    iVar2 = (int)DAT_febe7772 << 0x10;
    iVar3 = iVar3 << 0x10;
  }
  DAT_febe777c = iVar3 + (DAT_febe777c - iVar2);
  if (uVar1 - 1 < 0xffff) {
    iVar2 = (int)DAT_febe7774 * uVar1;
    iVar4 = iVar4 * uVar1;
  }
  else {
    iVar2 = (int)DAT_febe7774 << 0x10;
    iVar4 = iVar4 << 0x10;
  }
  DAT_febe7770 = (short)(DAT_febe7778 / 0x10000);
  DAT_febe7780 = iVar4 + (DAT_febe7780 - iVar2);
  DAT_febe7772 = (short)(DAT_febe777c / 0x10000);
  DAT_febe7774 = (short)(DAT_febe7780 / 0x10000);
  return;
}



void FUN_00042132(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe77b4 = 0;
  DAT_febe77b6 = 0;
  DAT_febe77b8 = 0;
  DAT_febe77bc = 0;
  f33_reset_windowed_monitor((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe7784u)));
  f33_reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)((0xffffbf94u + (uint32_t)((int)puVar1))))));
  f33_reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)((0xffffbfa4u + (uint32_t)((int)puVar1))))));
  return;
}



void FUN_0004215e(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe77b4 = 0;
  DAT_febe77b6 = 0;
  DAT_febe77b8 = 0;
  DAT_febe77bc = 0;
  f33_reset_windowed_monitor((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe7784u)));
  f33_reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)((0xffffbf94u + (uint32_t)((int)puVar1))))));
  f33_reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)((0xffffbfa4u + (uint32_t)((int)puVar1))))));
  return;
}



void FUN_0004218a(void)

{
  uint32_t puVar1;
  byte bVar2;
  
  puVar1 = 0xfebeb800u;
  if (DAT_0002bbe8 == 'Z') {
    f33_reset_windowed_monitor((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe7784u)));
    f33_reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)((0xffffbf94u + (uint32_t)((int)puVar1))))));
    f33_reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)((0xffffbfa4u + (uint32_t)((int)puVar1))))));
  }
  else {
    bVar2 = DAT_febe74ad |
            DAT_febe74ac |
            DAT_febe74aa |
            DAT_febe7825 |
            DAT_febe781b |
            DAT_febe781e |
            DAT_febe781d | DAT_febe781c | DAT_febe7824 | DAT_febe781a | DAT_febe7819 | DAT_febe7818;
    if (((DAT_febe71ec & 1) == 0) && (DAT_febeeb85 == 'Z')) {
      DAT_febe77bc = (int)DAT_febe7770;
      DAT_febe77b8 = DAT_febe6390;
      DAT_febe77b6 = 0x43;
      DAT_febe77b4 = bVar2;
      f33_step_windowed_monitor
                ((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe7784u)),(F33WindowedMonitorLimits *)((undefined *)camry_host_ptr(0x2b7e8u)),
                 (F33TwoSidedMonitorCallbacks *)&PTR_f33_classify_channel_residual_a_0002853c);
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbfb4u + (uint32_t)((int)puVar1) * 1u)))) = bVar2;
      (*((int *)camry_host_ptr((uint32_t)((0xffffbfbcu + (uint32_t)((int)puVar1)))))) = (int)(*((short *)camry_host_ptr((uint32_t)((0xffffbf72u + (uint32_t)((int)puVar1))))));
      (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffbfb8u + (uint32_t)((int)puVar1)))))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x546e))));
      (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffbfb6u + (uint32_t)((int)puVar1)))))) = 0x44;
      f33_step_windowed_monitor
                (((F33WindowedMonitorState *)camry_host_ptr((uint32_t)((0xffffbf94u + (uint32_t)((int)puVar1))))),
                 (F33WindowedMonitorLimits *)((undefined *)camry_host_ptr(0x2b7e8u)),
                 (F33TwoSidedMonitorCallbacks *)&PTR_f33_classify_channel_residual_a_0002853c);
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbfb4u + (uint32_t)((int)puVar1) * 1u)))) = bVar2;
      (*((int *)camry_host_ptr((uint32_t)((0xffffbfbcu + (uint32_t)((int)puVar1)))))) = (int)(*((short *)camry_host_ptr((uint32_t)((0xffffbf74u + (uint32_t)((int)puVar1))))));
      (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffbfb8u + (uint32_t)((int)puVar1)))))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x546c))));
      (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffbfb6u + (uint32_t)((int)puVar1)))))) = 0x45;
      f33_step_windowed_monitor
                (((F33WindowedMonitorState *)camry_host_ptr((uint32_t)((0xffffbfa4u + (uint32_t)((int)puVar1))))),
                 (F33WindowedMonitorLimits *)((undefined *)camry_host_ptr(0x2b7e8u)),
                 (F33TwoSidedMonitorCallbacks *)&PTR_f33_classify_channel_residual_a_0002853c);
    }
    else {
      FUN_0006ae48(((undefined *)camry_host_ptr(0xfebe7784u)),((undefined *)camry_host_ptr(0x2b7e8u)));
      FUN_0006ae48(((undefined *)camry_host_ptr((uint32_t)((0xffffbf94u + (uint32_t)((int)puVar1))))), ((undefined *)camry_host_ptr(0x2b7e8u)));
      FUN_0006ae48(((undefined *)camry_host_ptr((uint32_t)((0xffffbfa4u + (uint32_t)((int)puVar1))))), ((undefined *)camry_host_ptr(0x2b7e8u)));
    }
  }
  f33_set_channel_monitor_status_a(7,(uchar)(*((undefined4 *)camry_host_ptr((uint32_t)((0xffffbf84u + (uint32_t)((int)puVar1)))))));
  f33_set_channel_monitor_status_a(8,(uchar)(*((undefined4 *)camry_host_ptr((uint32_t)((0xffffbf94u + (uint32_t)((int)puVar1)))))));
  f33_set_channel_monitor_status_a(9,(uchar)(*((undefined4 *)camry_host_ptr((uint32_t)((0xffffbfa4u + (uint32_t)((int)puVar1)))))));
  return;
}



/* f33_report_diagnostic_healthy_observed((uint)DAT_febe77b6); whole-body shape-verified. The
   literal is the encoded diagnostic event, not a recovered OEM name. */

void f33_report_diagnostic_healthy_observed_cell_4238e(void)

{
  f33_report_diagnostic_healthy_observed((uint)DAT_febe77b6);
  return;
}



/* f33_report_diagnostic_event_failure((uint)DAT_febe77b6,10); whole-body shape-verified. The
   literal is the encoded diagnostic event, not a recovered OEM name. */

void f33_report_diagnostic_event_failure_10_4239e(void)

{
  f33_report_diagnostic_event_failure((uint)DAT_febe77b6,10);
  return;
}



/* Single constant publisher: DAT_febe77c2 = 0; Shape-classified from the canonical corpus; the
   target cell is not yet named, so the written state's meaning is unknown. */

void FUN_000423b0(void)

{
  DAT_febe77c2 = 0;
  return;
}



/* Single constant publisher: DAT_febe77c2 = 0; Shape-classified from the canonical corpus; the
   target cell is not yet named, so the written state's meaning is unknown. */

void FUN_000423b6(void)

{
  DAT_febe77c2 = 0;
  return;
}



void FUN_000423bc(void)

{
  undefined *puVar1;
  char cVar3;
  uchar status;
  byte bVar4;
  uint32_t puVar2;
  cVar3 = DAT_febe77c1;
  bVar4 = DAT_febe77c0;
  puVar2 = 0xfebeb800u;
  puVar1 = ((undefined *)camry_host_ptr(0xfebeb800u));
  if (DAT_0002bbec != 'Z') {
    if ((DAT_febe71ec & 1) == 0) {
      if (DAT_febe6425 == 'Z') {
        status = '\"';
        f33_report_diagnostic_event_failure(0x36,10);
        puVar1 = ((undefined *)camry_host_ptr((uint32_t)(puVar2)));
      }
      else {
        if (DAT_febe6424 == '\0') {
          status = '\0';
          if (((DAT_0002b82c < DAT_febe7da6) || ((short)f33_output_request_status != 0)) ||
             (DAT_febeeb85 != 'Z')) {
            bVar4 = 0;
          }
          else if (DAT_febe77c0 < DAT_0002b82a) {
            bVar4 = DAT_febe77c0 + 1;
          }
          else if (DAT_febe77c1 != 'Z') {
            puVar1 = ((undefined *)camry_host_ptr(0xfebeb800u));
            f33_report_diagnostic_healthy_observed(0x36);
            cVar3 = 'Z';
          }
          goto LAB_00042456;
        }
        status = '\x11';
        puVar1 = ((undefined *)camry_host_ptr(0xfebeb800u));
      }
      bVar4 = 0;
      goto LAB_00042456;
    }
    status = DAT_febe77c2;
    if (DAT_febe77c2 != '\x11') goto LAB_00042456;
  }
  status = '\0';
LAB_00042456:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbfc0u + (uint32_t)((int)camry_host_addr(puVar1)) * 1u)))) = bVar4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbfc1u + (uint32_t)((int)camry_host_addr(puVar1)) * 1u)))) = cVar3;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbfc2u + (uint32_t)((int)camry_host_addr(puVar1)) * 1u)))) = status;
  f33_set_channel_monitor_status_a(0xc,status);
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4246c(void)

{
  return;
}



/* Constant-block fill: 7 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_4246e(void)

{
  DAT_febe77c4 = 0;
  DAT_febe77c5 = 0;
  DAT_febe77c6 = 0;
  DAT_febe77c7 = 0;
  DAT_febe77c8 = 0x8000;
  DAT_febe77ca = 0x8000;
  DAT_febe77cc = 0x8000;
  return;
}



/* Sum three unsigned sample differences from8238..823C versus822C..8230. Exact31E5E==5A selects
   retained members refreshed by EAC1 and individual validity. Sum three unsigned sample differences
   with exact-image retained-member selection and per-member validity refresh; no physical
   sample-age claim. */

int f33_sum_channel_snapshot_differences_a(void)

{
  ushort uVar1;
  char cVar4;
  char cVar5;
  ushort uVar2;
  ushort uVar3;
  
  uVar1 = DAT_febe8238;
  uVar2 = DAT_febe823c;
  uVar3 = DAT_febe823a;
  if (DAT_00031e5e != 'Z') goto LAB_000424f0;
  if (DAT_febeeac1 == 'Z') {
    cVar4 = DAT_febe7e21;
    cVar5 = DAT_febe7e22;
    if (DAT_febe7e20 == 'Z') goto LAB_000424b6;
  }
  else {
    cVar4 = 'Z';
    cVar5 = 'Z';
LAB_000424b6:
    DAT_febe77c8 = DAT_febe8238;
  }
  if (cVar4 == 'Z') {
    DAT_febe77ca = DAT_febe823a;
  }
  uVar1 = DAT_febe77c8;
  uVar2 = DAT_febe77cc;
  uVar3 = DAT_febe77ca;
  if (cVar5 == 'Z') {
    DAT_febe77cc = DAT_febe823c;
    uVar2 = DAT_febe823c;
  }
LAB_000424f0:
  return ((uint)uVar2 - (uint)DAT_febe8230) +
         ((uint)uVar3 - (uint)DAT_febe822e) + ((uint)uVar1 - (uint)DAT_febe822c);
}



/* Separate snapshot producer: abs(unsigned-sample difference sum)>21103 and gate<=4298 accumulate
   failure through15, then next invocation publishes5A. Healthy count reaches25 before next
   invocation clears failure/publishesA5; qualification freezes state. Separate residual-difference
   latch publishes failure only after count15 is already reached; healthy publication follows
   count25. Qualification freezes state and high-water history persists. */

void f33_step_channel_difference_latch_a(void)

{
  ushort uVar1;
  short sVar2;
  ushort uVar3;
  byte bVar4;
  int iVar5;
  uint32_t puVar6;
  int iVar7;
  int iVar8;
  byte bVar9;
  undefined1 uVar10;
  byte bVar11;
  byte bVar12;
  
  uVar10 = DAT_febe77c7;
  bVar4 = DAT_febe77c6;
  bVar11 = DAT_febe77c5;
  bVar12 = DAT_febe77c4;
  puVar6 = 0xfebeb800u;
  if (((byte)DAT_febe71ec & 1) == 0) {
    iVar7 = f33_sum_channel_snapshot_differences_a();
    uVar3 = DAT_00031e62;
    sVar2 = DAT_00031e60;
    if (iVar7 + 0x7fffffff < 0 == (-1 < iVar7 && iVar7 + 0x7fffffff < 0) && iVar7 != -0x7fffffff) {
      iVar5 = iVar7;
      if (iVar7 < 0) {
        iVar5 = -iVar7;
      }
    }
    else {
      iVar5 = 0x7fffffff;
    }
    iVar8 = (int)DAT_00031e60;
    uVar1 = (*((ushort *)camry_host_ptr((uint32_t)(puVar6 + -0x3a5a))));
    (*((int *)camry_host_ptr((uint32_t)((0xffffbfd0u + (uint32_t)((int)puVar6)))))) = iVar7;
    (*((short *)camry_host_ptr((uint32_t)((0xffffbfceu + (uint32_t)((int)puVar6)))))) = sVar2;
    bVar9 = bVar4;
    if ((iVar5 - iVar8 < 0 == (iVar5 < 0 != iVar8 < 0 && iVar8 < 0 == iVar5 - iVar8 < 0) &&
         iVar5 != iVar8) && (uVar1 <= uVar3)) {
      bVar11 = 0;
      if (bVar12 < DAT_00031e5c) {
        uVar10 = 0;
        bVar12 = bVar12 + 1;
        bVar9 = bVar12;
        if (bVar12 <= bVar4) {
          bVar9 = bVar4;
        }
      }
      else {
        uVar10 = 0x5a;
      }
    }
    else if (bVar11 < DAT_00031e5d) {
      bVar11 = bVar11 + 1;
    }
    else {
      bVar12 = 0;
      uVar10 = 0xa5;
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbfc4u + (uint32_t)((int)puVar6) * 1u)))) = bVar12;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbfc5u + (uint32_t)((int)puVar6) * 1u)))) = bVar11;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbfc6u + (uint32_t)((int)puVar6) * 1u)))) = bVar9;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbfc7u + (uint32_t)((int)puVar6) * 1u)))) = uVar10;
  }
  return;
}



void FUN_00042592(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe77d4 = 0;
  DAT_febe77d6 = 0;
  DAT_febe77d8 = 0;
  f33_reset_windowed_monitor((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe77dcu)));
  f33_reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)((0xffffbfecu + (uint32_t)((int)puVar1))))));
  f33_reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)((0xffffbffcu + (uint32_t)((int)puVar1))))));
  f33_reset_recoverable_monitor(((F33RecoverableMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3ff4))));
  return;
}



void FUN_000425c4(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe77d4 = 0;
  DAT_febe77d6 = 0;
  DAT_febe77d8 = 0;
  f33_reset_windowed_monitor((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe77dcu)));
  f33_reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)((0xffffbfecu + (uint32_t)((int)puVar1))))));
  f33_reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)((0xffffbffcu + (uint32_t)((int)puVar1))))));
  f33_reset_recoverable_monitor(((F33RecoverableMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3ff4))));
  return;
}



/* Three conditioned phase/comparison predicates run retained window qualification with strict
   count>25 confirmation; separately aggregate any phase failure count>=1 with zero confirmation
   limits. Event38/39/3A reporting does not gate action status. Compose three retained phase windows
   and separate failure-counter aggregate. Count25->26 confirms first phase; attempted event38 is
   inhibited without suppressing action status. */

void f33_step_channel_phase_monitors_a(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bbf0 == 'Z') {
    puVar1 = 0xfebeb800u;
    f33_reset_windowed_monitor((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe77dcu)));
    f33_reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)((0xffffbfecu + (uint32_t)((int)puVar1))))));
    f33_reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)((0xffffbffcu + (uint32_t)((int)puVar1))))));
  }
  else {
    if (((DAT_febe71ec & 1) == 0) && (DAT_febeeb85 == 'Z')) {
      DAT_febe77d4 = 0x38;
      DAT_febe77d6 = f33_monitor_current_dynamic_reference_plane[0];
      DAT_febe77d8 = f33_monitor_current_second_midpoint_plane[0];
      f33_step_windowed_monitor
                ((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe77dcu)),(F33WindowedMonitorLimits *)((undefined *)camry_host_ptr(0x2b7f0u)),
                 (F33TwoSidedMonitorCallbacks *)&PTR_f33_classify_channel_phase_sample_a_00028570);
      (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffbfd4u + (uint32_t)((int)puVar1)))))) = 0x39;
      (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffbfd6u + (uint32_t)((int)puVar1)))))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x3986))));
      (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffbfd8u + (uint32_t)((int)puVar1)))))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x397a))));
      f33_step_windowed_monitor
                (((F33WindowedMonitorState *)camry_host_ptr((uint32_t)((0xffffbfecu + (uint32_t)((int)puVar1))))),
                 (F33WindowedMonitorLimits *)((undefined *)camry_host_ptr(0x2b7f0u)),
                 (F33TwoSidedMonitorCallbacks *)&PTR_f33_classify_channel_phase_sample_a_00028570);
      (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffbfd4u + (uint32_t)((int)puVar1)))))) = 0x3a;
      (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffbfd6u + (uint32_t)((int)puVar1)))))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x3984))));
      (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffbfd8u + (uint32_t)((int)puVar1)))))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x3978))));
      f33_step_windowed_monitor
                (((F33WindowedMonitorState *)camry_host_ptr((uint32_t)((0xffffbffcu + (uint32_t)((int)puVar1))))),
                 (F33WindowedMonitorLimits *)((undefined *)camry_host_ptr(0x2b7f0u)),
                 (F33TwoSidedMonitorCallbacks *)&PTR_f33_classify_channel_phase_sample_a_00028570);
      f33_step_recoverable_monitor
                (((F33RecoverableMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3ff4))),
                 (F33RecoverableMonitorLimits *)((undefined *)camry_host_ptr(0x2b7f8u)),
                 (F33RecoverableMonitorCallbacks *)
                 &PTR_f33_classify_channel_phase_failure_count_a_000285a4);
      goto LAB_000426e2;
    }
    puVar1 = 0xfebeb800u;
    FUN_0006ae48(((undefined *)camry_host_ptr(0xfebe77dcu)),((undefined *)camry_host_ptr(0x2b7f0u)));
    FUN_0006ae48(((undefined *)camry_host_ptr((uint32_t)((0xffffbfecu + (uint32_t)((int)puVar1))))), ((undefined *)camry_host_ptr(0x2b7f0u)));
    FUN_0006ae48(((undefined *)camry_host_ptr((uint32_t)((0xffffbffcu + (uint32_t)((int)puVar1))))), ((undefined *)camry_host_ptr(0x2b7f0u)));
  }
  f33_reset_recoverable_monitor(((F33RecoverableMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3ff4))));
LAB_000426e2:
  f33_set_channel_monitor_status_a(0,(uchar)(*((undefined4 *)camry_host_ptr((uint32_t)((0xffffbfdcu + (uint32_t)((int)puVar1)))))));
  f33_set_channel_monitor_status_a(1,(uchar)(*((undefined4 *)camry_host_ptr((uint32_t)((0xffffbfecu + (uint32_t)((int)puVar1)))))));
  f33_set_channel_monitor_status_a(2,(uchar)(*((undefined4 *)camry_host_ptr((uint32_t)((0xffffbffcu + (uint32_t)((int)puVar1)))))));
  f33_set_channel_monitor_status_a(10,(uchar)(*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x3ff4)))));
  return;
}



/* Failure22: sat_abs16(sample)>19968 or source62E4==0/comparison<-19968, with unsigned7DA6<=4298
   and signed62DC>-32768. Neutral33 on unadmitted abnormality, otherwise11. Phase magnitude>19968 or
   qualified comparison<-19968 requires unsigned gate<=4298 and signed source>-32768 for failure22.
   Unadmitted abnormality33 and pass11 remain distinct. */

uint f33_classify_channel_phase_sample_a(void)

{
  ushort uVar1;
  ushort uVar2;
  char cVar3;
  ushort uVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  short sStack_22;
  
  uVar4 = DAT_febe7da6;
  cVar3 = DAT_febe62e4;
  uVar2 = DAT_0002b83a;
  uVar1 = DAT_0002b834;
  iVar8 = (int)DAT_febe77d8;
  iVar7 = (int)DAT_febe62dc;
  FUN_0006a522((int)DAT_febe77d6,&sStack_22);
  iVar5 = (int)sStack_22;
  iVar6 = (int)DAT_0002b830;
  if (cVar3 == '\0') {
    if ((((iVar5 - iVar6 < 0 == (iVar5 < 0 != iVar6 < 0 && iVar6 < 0 == iVar5 - iVar6 < 0) &&
           iVar5 != iVar6) ||
         (iVar6 = (int)DAT_0002b832,
         iVar8 - iVar6 < 0 != (iVar8 < 0 != iVar6 < 0 && iVar6 < 0 == iVar8 - iVar6 < 0))) &&
        (uVar4 <= uVar1)) &&
       (iVar6 = (int)DAT_0002b83c,
       iVar7 - iVar6 < 0 == (iVar7 < 0 != iVar6 < 0 && iVar6 < 0 == iVar7 - iVar6 < 0) &&
       iVar7 != iVar6)) {
      return 0x22;
    }
    iVar6 = (int)DAT_0002b836;
    if (iVar5 - iVar6 < 0 == (iVar5 < 0 != iVar6 < 0 && iVar6 < 0 == iVar5 - iVar6 < 0) &&
        iVar5 != iVar6) {
      return 0x33;
    }
    iVar5 = (int)DAT_0002b838;
    if (iVar8 - iVar5 < 0 != (iVar8 < 0 != iVar5 < 0 && iVar5 < 0 == iVar8 - iVar5 < 0)) {
      return 0x33;
    }
  }
  else {
    if (((iVar5 - iVar6 < 0 == (iVar5 < 0 != iVar6 < 0 && iVar6 < 0 == iVar5 - iVar6 < 0) &&
          iVar5 != iVar6) && (uVar4 <= uVar1)) &&
       (iVar6 = (int)DAT_0002b83c,
       iVar7 - iVar6 < 0 == (iVar7 < 0 != iVar6 < 0 && iVar6 < 0 == iVar7 - iVar6 < 0) &&
       iVar7 != iVar6)) {
      return 0x22;
    }
    iVar6 = (int)DAT_0002b836;
    if (iVar5 - iVar6 < 0 == (iVar5 < 0 != iVar6 < 0 && iVar6 < 0 == iVar5 - iVar6 < 0) &&
        iVar5 != iVar6) {
      return 0x33;
    }
  }
  if (uVar2 < uVar4) {
    return 0x33;
  }
  return 0x11;
}



/* f33_report_diagnostic_healthy_observed((uint)DAT_febe77d4); whole-body shape-verified. The
   literal is the encoded diagnostic event, not a recovered OEM name. */

void f33_report_diagnostic_healthy_observed_cell_427a0(void)

{
  f33_report_diagnostic_healthy_observed((uint)DAT_febe77d4);
  return;
}



/* f33_report_diagnostic_event_failure((uint)DAT_febe77d4,10); whole-body shape-verified. The
   literal is the encoded diagnostic event, not a recovered OEM name. */

void f33_report_diagnostic_event_failure_10_427b0(void)

{
  f33_report_diagnostic_event_failure((uint)DAT_febe77d4,10);
  return;
}



/* Any retained phase failure counter>=exact byte threshold1 returns22, otherwise11. ROM285A4 has no
   reporting callbacks; can confirm before an individual phase. Any phase failure counter>=byte
   threshold1 fails immediately through aggregate monitor with zero confirmation limits. Its ROM
   vector has no diagnostic callbacks. */

uint f33_classify_channel_phase_failure_count_a(void)

{
  ushort uVar1;
  
  uVar1 = (ushort)DAT_0002b82e;
  if (((DAT_febe77e4 < uVar1) && (DAT_febe77f4 < uVar1)) && (DAT_febe7804 < uVar1)) {
    return 0x11;
  }
  return 0x22;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_427ee(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_427f0(void)

{
  return;
}



/* Rebuild fault slot2 from14 statuses7818..7825: retain old five words, clear current, merge
   pending/confirmed templates, then select current. Qualification71EC.bit0 and diagnostic reporting
   admission are separate. Aggregate status10 has no diagnostic callbacks and is excluded from the
   third summary and both channel caches. First-channel fourteen-status reduction rebuilds fault
   slot2 despite diagnostic event inhibition. Native phase confirmation merges real templates and
   preserves old record/complements/caches. */

void f33_publish_channel_monitor_actions_a(void)

{
  byte bVar1;
  byte bVar2;
  ushort uVar3;
  uint32_t puVar4;
  uchar uVar5;
  undefined1 uVar6;
  
  uVar3 = DAT_febe71ec;
  puVar4 = 0xfebeb800u;
  f33_retain_and_clear_fault_record(2);
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fdb))))) |
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fdc))))) |
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe2))))) |
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe3))))) |
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe4))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe5))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe6))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe7))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe8)))))) &
      0x11) == 0x11) {
    f33_encode_fault_action_kind('\x02','\n');
  }
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fdc))))) |
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe6))))) |
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe7))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe8))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe2))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe3))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe4)))))) &
      0x22) == 0x22) {
    f33_encode_fault_action_kind('\x02','#');
  }
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fdb))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe5))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fdf))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe0))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe1)))))) &
      0x22) == 0x22) {
    f33_encode_fault_action_kind('\x02','\x1b');
  }
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fdd))))) & 0x22) == 0x22) {
    f33_encode_fault_action_kind('\x02','\x1d');
  }
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fde))))) & 0x22) == 0x22) {
    f33_encode_fault_action_kind('\x02','\'');
  }
  if (((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fdb))))) |
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fdc))))) |
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe2))))) |
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe3))))) |
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe4))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe5))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe6))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe7))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe8)))))) &
       0x22) == 0x22) && ((uVar3 & 1) == 0)) {
    f33_encode_fault_action_kind('\x02','\n');
  }
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fdc))))) |
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe2))))) |
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe3))))) |
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe4))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe5))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe6))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe7))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe8)))))) &
      0x22) == 0x22) {
    f33_encode_fault_action_kind('\x02','2');
  }
  f33_select_current_fault_record(2);
  bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe6))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe7))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe8)))));
  uVar6 = 0;
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe1))))) | bVar1 | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe0))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fdf)))))) & 0x11) == 0x11) {
    uVar6 = 0x5a;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fda))))) = uVar6;
  uVar6 = 0x11;
  if ((((((bVar1 == 0 && (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe5))))) == '\0') && (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe4))))) == '\0') &&
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe3))))) == '\0') && (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe2))))) == '\0') && (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fdc))))) == '\0') &&
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fdb))))) == '\0') {
    uVar6 = 0;
  }
  uVar5 = '\0';
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fd9))))) = uVar6;
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fdb))))) != '\0' ||
      ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fdd))))) != '\0' ||
      ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fdf))))) != 0 ||
      ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe0))))) != 0 ||
      ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe1))))) != 0 ||
      ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe5))))) != '\0' ||
      ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe6))))) != 0 ||
      ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe7))))) != 0 ||
      ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe8))))) != 0 ||
      ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe2))))) != '\0' ||
      ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe3))))) != '\0' || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe4))))) != '\0' || (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fdc))))) != '\0')))))))))))) {
    uVar5 = '\x11';
  }
  f33_set_diagnostic_cache_blocker('\x03',uVar5);
  bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe6))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe7))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe8)))));
  bVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fdb))))) |
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fdd))))) |
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fdf))))) |
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fdc))))) | bVar1 | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe4))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe3))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe2))))) |
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe5))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe1))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe0)))));
  if ((bVar2 == 0) || (bVar2 == 0x11)) {
    uVar6 = 0;
  }
  else {
    uVar6 = 0x5a;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fd8))))) = uVar6;
  uVar5 = '\0';
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fdd))))) |
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fdf))))) |
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe0))))) |
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe1))))) |
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fdb))))) |
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fdc))))) |
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe2))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe3))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe4))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe5))))) | bVar1) & 0x11) ==
      0x11) {
    uVar5 = 'Z';
  }
  f33_set_monitor_pending_projection('\x02',uVar5);
  return;
}



/* Bound unsigned index<14 before storing one status byte at7818+index. Bound unsigned index<14 then
   store one first-channel status byte. */

void f33_set_channel_monitor_status_a(uint index,uchar status)

{
  if ((index & 0xff) < 0xe) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7818u + (uint32_t)(index & 0xff) * 1u)))) = status;
  }
  return;
}



/* f33_reset_latched_monitor wrapper resetting exactly one monitor state ((F33LatchedMonitorState
   *)((undefined *)camry_host_ptr(0xfebe782cu))); whole-body shape-verified from the canonical corpus. Per-instance semantics
   derive from the referenced state cell; not individually executed. */

void f33_reset_latched_monitor_febe782c(void)

{
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe782cu)));
  return;
}



/* f33_reset_latched_monitor wrapper resetting exactly one monitor state ((F33LatchedMonitorState
   *)((undefined *)camry_host_ptr(0xfebe782cu))); whole-body shape-verified from the canonical corpus. Per-instance semantics
   derive from the referenced state cell; not individually executed. */

void f33_reset_latched_monitor_febe782c_42a5a(void)

{
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe782cu)));
  return;
}



void FUN_00042a6a(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bbf4 == 'Z') {
    f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe782cu)));
  }
  else if (((DAT_febe6764 & 1) == 0) && (DAT_febee820 == 'Z')) {
    f33_step_latched_monitor
              ((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe782cu)),(F33MonitorLimits *)((undefined *)camry_host_ptr(0x2b7feu)),
               (F33TwoSidedMonitorCallbacks *)&PTR_FUN_000285e0);
  }
  else {
    f33_retain_disabled_latched_monitor
              ((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe782cu)),(F33MonitorLimits *)((undefined *)camry_host_ptr(0x2b7feu)));
  }
  f33_set_channel_monitor_status_a(0xb,(uchar)(*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x3fd4)))));
  return;
}



undefined4 FUN_00042ac4(void)

{
  int iVar1;
  int iVar2;
  
  iVar1 = (uint)DAT_febe66b8 - (uint)DAT_febe66ae;
  if ((DAT_febe827c == 'Z') &&
     (((uint)DAT_0002b83e < (uint)DAT_febe66b8 ||
      (iVar2 = (int)DAT_0002b840,
      iVar1 - iVar2 < 0 != (iVar1 < 0 != iVar2 < 0 && iVar2 < 0 == iVar1 - iVar2 < 0) ||
      iVar1 == iVar2)))) {
    return 0x5a;
  }
  return 0;
}



undefined4 FUN_00042af4(void)

{
  char cVar1;
  uint uVar2;
  char cVar3;
  char cVar4;
  char cVar5;
  int iVar6;
  undefined4 uVar7;
  
  cVar5 = DAT_febe8280;
  cVar4 = DAT_febe827c;
  cVar3 = DAT_febe827b;
  uVar2 = DAT_febe6618;
  cVar1 = DAT_febe65f6;
  iVar6 = FUN_00042ac4();
  if ((cVar1 == 'Z') && ((uVar2 & 1) == 0)) {
    if ((cVar3 == 'Z') || ((iVar6 == 0x5a || (cVar5 == 'Z')))) {
      uVar7 = 0x22;
    }
    else if (((cVar3 == '\0') && (cVar4 == '\0')) && (cVar5 == '\0')) {
      uVar7 = 0x11;
    }
    else {
      uVar7 = 0x33;
    }
  }
  else {
    uVar7 = 0x44;
  }
  return uVar7;
}



/* f33_report_diagnostic_healthy_observed(0x86); whole-body shape-verified. The literal is the
   encoded diagnostic event, not a recovered OEM name. */

void f33_report_diagnostic_healthy_observed_86_42b50(void)

{
  f33_report_diagnostic_healthy_observed(0x86);
  return;
}



/* f33_report_diagnostic_event_failure(0x86,0x32); whole-body shape-verified. The literal is the
   encoded diagnostic event, not a recovered OEM name. */

void f33_report_diagnostic_event_failure_86_32_42b60(void)

{
  f33_report_diagnostic_event_failure(0x86,0x32);
  return;
}



/* f33_reset_latched_monitor wrapper resetting exactly one monitor state ((F33LatchedMonitorState
   *)((undefined *)camry_host_ptr(0xfebe7838u))); whole-body shape-verified from the canonical corpus. Per-instance semantics
   derive from the referenced state cell; not individually executed. */

void f33_reset_latched_monitor_febe7838(void)

{
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7838u)));
  return;
}



/* f33_reset_latched_monitor wrapper resetting exactly one monitor state ((F33LatchedMonitorState
   *)((undefined *)camry_host_ptr(0xfebe7838u))); whole-body shape-verified from the canonical corpus. Per-instance semantics
   derive from the referenced state cell; not individually executed. */

void f33_reset_latched_monitor_febe7838_42b84(void)

{
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7838u)));
  return;
}



void FUN_00042b94(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bbf8 == 'Z') {
    f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7838u)));
  }
  else if (((DAT_febe71ec & 1) == 0) && (DAT_febeeb85 == 'Z')) {
    f33_step_latched_monitor
              ((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7838u)),(F33MonitorLimits *)((undefined *)camry_host_ptr(0x2b802u)),
               (F33TwoSidedMonitorCallbacks *)&PTR_f33_classify_channel_raw_lower_bound_a_00028614);
  }
  else {
    f33_retain_disabled_latched_monitor
              ((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7838u)),(F33MonitorLimits *)((undefined *)camry_host_ptr(0x2b802u)));
  }
  f33_set_channel_monitor_status_a(0xd,(uchar)(*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x3fc8)))));
  return;
}



/* Low16 8B28 must clear. Any raw6238/3A/3C<10224 with its636C/D/E validity5A fails22; all>=10224
   and all valid pass11. Otherwise33; closed gate44. Low-half gate admission precedes raw
   lower-bound10224 and individual validity checks; any valid low sample fails and all high/valid
   samples pass. */

uint f33_classify_channel_raw_lower_bound_a(void)

{
  if ((short)f33_output_request_status != 0) {
    return 0x44;
  }
  if ((((DAT_0002b842 <= DAT_febe6238) || (DAT_febe636c != 'Z')) &&
      ((DAT_0002b842 <= DAT_febe623a || (DAT_febe636d != 'Z')))) &&
     ((DAT_0002b842 <= DAT_febe623c || (DAT_febe636e != 'Z')))) {
    if ((DAT_0002b844 <= DAT_febe6238) &&
       ((((DAT_febe636c == 'Z' && (DAT_0002b844 <= DAT_febe623a)) && (DAT_febe636d == 'Z')) &&
        ((DAT_0002b844 <= DAT_febe623c && (DAT_febe636e == 'Z')))))) {
      return 0x11;
    }
    return 0x33;
  }
  return 0x22;
}



/* f33_report_diagnostic_healthy_observed(0x136); whole-body shape-verified. The literal is the
   encoded diagnostic event, not a recovered OEM name. */

void f33_report_diagnostic_healthy_observed_136_42c68(void)

{
  f33_report_diagnostic_healthy_observed(0x136);
  return;
}



/* f33_report_diagnostic_event_failure(0x136,10); whole-body shape-verified. The literal is the
   encoded diagnostic event, not a recovered OEM name. */

void f33_report_diagnostic_event_failure_136_10_42c78(void)

{
  f33_report_diagnostic_event_failure(0x136,10);
  return;
}



/* f33_reset_windowed_monitor wrapper resetting exactly one monitor state ((F33WindowedMonitorState
   *)((undefined *)camry_host_ptr(0xfebe7844u))); whole-body shape-verified from the canonical corpus. Per-instance semantics
   derive from the referenced state cell; not individually executed. */

void f33_reset_windowed_monitor_febe7844(void)

{
  f33_reset_windowed_monitor((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe7844u)));
  return;
}



/* f33_reset_windowed_monitor wrapper resetting exactly one monitor state ((F33WindowedMonitorState
   *)((undefined *)camry_host_ptr(0xfebe7844u))); whole-body shape-verified from the canonical corpus. Per-instance semantics
   derive from the referenced state cell; not individually executed. */

void f33_reset_windowed_monitor_febe7844_42c9a(void)

{
  f33_reset_windowed_monitor((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe7844u)));
  return;
}



/* f33_report_diagnostic_healthy_observed(0x41); whole-body shape-verified. The literal is the
   encoded diagnostic event, not a recovered OEM name. */

void f33_report_diagnostic_healthy_observed_41_42dde(void)

{
  f33_report_diagnostic_healthy_observed(0x41);
  return;
}



/* f33_report_diagnostic_event_failure(0x41,10); whole-body shape-verified. The literal is the
   encoded diagnostic event, not a recovered OEM name. */

void f33_report_diagnostic_event_failure_41_10_42dee(void)

{
  f33_report_diagnostic_event_failure(0x41,10);
  return;
}



void FUN_00042e00(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe7854 = 0;
  DAT_febe7856 = 0;
  DAT_febe7858 = 0;
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe785cu)));
  f33_reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3f98))));
  f33_reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3f8c))));
  return;
}



void FUN_00042e2a(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe7854 = 0;
  DAT_febe7856 = 0;
  DAT_febe7858 = 0;
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe785cu)));
  f33_reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3f98))));
  f33_reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3f8c))));
  return;
}



void FUN_00042e54(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bc00 == 'Z') {
    f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe785cu)));
    f33_reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3f98))));
    f33_reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3f8c))));
  }
  else if ((DAT_febe71ec >> 1 & 1) == 0) {
    DAT_febe7854 = 0x2d;
    DAT_febe7856 = f33_monitor_current_second_midpoint_plane[3];
    DAT_febe7858 = f33_monitor_current_first_midpoint_plane[3];
    f33_step_latched_monitor
              ((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe785cu)),(F33MonitorLimits *)&PTR_DAT_0002b854,
               (F33TwoSidedMonitorCallbacks *)&PTR_f33_classify_channel_negative_pair_b_0002867c);
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x3fac)))) = 0x2e;
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x3faa)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x3974))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x3fa8)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x3968))));
    f33_step_latched_monitor
              (((F33LatchedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3f98))),(F33MonitorLimits *)&PTR_DAT_0002b854,
               (F33TwoSidedMonitorCallbacks *)&PTR_f33_classify_channel_negative_pair_b_0002867c);
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x3fac)))) = 0x2f;
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x3faa)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x3972))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x3fa8)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x3966))));
    f33_step_latched_monitor
              (((F33LatchedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3f8c))),(F33MonitorLimits *)&PTR_DAT_0002b854,
               (F33TwoSidedMonitorCallbacks *)&PTR_f33_classify_channel_negative_pair_b_0002867c);
  }
  else {
    f33_retain_disabled_latched_monitor
              ((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe785cu)),(F33MonitorLimits *)&PTR_DAT_0002b854);
    f33_retain_disabled_latched_monitor
              (((F33LatchedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3f98))),(F33MonitorLimits *)&PTR_DAT_0002b854);
    f33_retain_disabled_latched_monitor
              (((F33LatchedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3f8c))),(F33MonitorLimits *)&PTR_DAT_0002b854);
  }
  f33_set_channel_monitor_status_b(4,(uchar)(*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x3fa4)))));
  f33_set_channel_monitor_status_b(5,(uchar)(*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x3f98)))));
  f33_set_channel_monitor_status_b(6,(uchar)(*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x3f8c)))));
  return;
}



/* Parallel ROM2867C predicate; same strict signed bounds. Recovered parallel ROM2867C negative-pair
   classifier with matching signed strict thresholds. */

uint f33_classify_channel_negative_pair_b(void)

{
  int iVar1;
  int iVar2;
  
  iVar2 = (int)DAT_0002b87e;
  iVar1 = DAT_febe7856 - iVar2;
  if ((iVar1 < 0 != (DAT_febe7856 < 0 != iVar2 < 0 && iVar2 < 0 == iVar1 < 0)) &&
     (iVar2 = (int)DAT_0002b880, iVar1 = DAT_febe7858 - iVar2,
     iVar1 < 0 != (DAT_febe7858 < 0 != iVar2 < 0 && iVar2 < 0 == iVar1 < 0))) {
    return 0x22;
  }
  return 0x11;
}



/* f33_report_diagnostic_healthy_observed((uint)DAT_febe7854); whole-body shape-verified. The
   literal is the encoded diagnostic event, not a recovered OEM name. */

void f33_report_diagnostic_healthy_observed_cell_42f58(void)

{
  f33_report_diagnostic_healthy_observed((uint)DAT_febe7854);
  return;
}



/* f33_report_diagnostic_event_failure((uint)DAT_febe7854,10); whole-body shape-verified. The
   literal is the encoded diagnostic event, not a recovered OEM name. */

void f33_report_diagnostic_event_failure_10_42f68(void)

{
  f33_report_diagnostic_event_failure((uint)DAT_febe7854,10);
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_42f7a(void)

{
  return;
}



void FUN_00042f7c(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  if (DAT_febe6310 + 0x7fff < 0 == (-1 < DAT_febe6310 && DAT_febe6310 + 0x7fff < 0) &&
      DAT_febe6310 != -0x7fff) {
    iVar3 = DAT_febe6310;
    if (DAT_febe6310 + -0x7fff < 0 == (DAT_febe6310 < 0 && -1 < DAT_febe6310 + -0x7fff) &&
        DAT_febe6310 != 0x7fff) {
      iVar3 = 0x7fff;
    }
  }
  else {
    iVar3 = -0x7fff;
  }
  if (DAT_febe6314 + 0x7fff < 0 == (-1 < DAT_febe6314 && DAT_febe6314 + 0x7fff < 0) &&
      DAT_febe6314 != -0x7fff) {
    iVar2 = DAT_febe6314;
    if (DAT_febe6314 + -0x7fff < 0 == (DAT_febe6314 < 0 && -1 < DAT_febe6314 + -0x7fff) &&
        DAT_febe6314 != 0x7fff) {
      iVar2 = 0x7fff;
    }
  }
  else {
    iVar2 = -0x7fff;
  }
  if (DAT_febe6318 + 0x7fff < 0 == (-1 < DAT_febe6318 && DAT_febe6318 + 0x7fff < 0) &&
      DAT_febe6318 != -0x7fff) {
    iVar1 = DAT_febe6318;
    if (DAT_febe6318 + -0x7fff < 0 == (DAT_febe6318 < 0 && -1 < DAT_febe6318 + -0x7fff) &&
        DAT_febe6318 != 0x7fff) {
      iVar1 = 0x7fff;
    }
  }
  else {
    iVar1 = -0x7fff;
  }
  DAT_febe7880 = (short)iVar3;
  DAT_febe7882 = (short)iVar2;
  DAT_febe7884 = (short)iVar1;
  DAT_febe7888 = iVar3 << 0x10;
  DAT_febe788c = iVar2 << 0x10;
  DAT_febe7890 = iVar1 << 0x10;
  return;
}



/* WARNING: Removing unreachable block (ram,0x000430e2) */
/* WARNING: Removing unreachable block (ram,0x000430b6) */
/* WARNING: Removing unreachable block (ram,0x00043096) */

void FUN_00042fee(void)

{
  uint uVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  
  if (DAT_febe6310 + 0x7fff < 0 == (-1 < DAT_febe6310 && DAT_febe6310 + 0x7fff < 0) &&
      DAT_febe6310 != -0x7fff) {
    iVar2 = (int)(short)DAT_febe6310;
    if (DAT_febe6310 + -0x7fff < 0 == (DAT_febe6310 < 0 && -1 < DAT_febe6310 + -0x7fff) &&
        DAT_febe6310 != 0x7fff) {
      iVar2 = 0x7fff;
    }
  }
  else {
    iVar2 = -0x7fff;
  }
  if (DAT_febe6314 + 0x7fff < 0 == (-1 < DAT_febe6314 && DAT_febe6314 + 0x7fff < 0) &&
      DAT_febe6314 != -0x7fff) {
    iVar3 = (int)(short)DAT_febe6314;
    if (DAT_febe6314 + -0x7fff < 0 == (DAT_febe6314 < 0 && -1 < DAT_febe6314 + -0x7fff) &&
        DAT_febe6314 != 0x7fff) {
      iVar3 = 0x7fff;
    }
  }
  else {
    iVar3 = -0x7fff;
  }
  if (DAT_febe6318 + 0x7fff < 0 == (-1 < DAT_febe6318 && DAT_febe6318 + 0x7fff < 0) &&
      DAT_febe6318 != -0x7fff) {
    iVar4 = (int)(short)DAT_febe6318;
    if (DAT_febe6318 + -0x7fff < 0 == (DAT_febe6318 < 0 && -1 < DAT_febe6318 + -0x7fff) &&
        DAT_febe6318 != 0x7fff) {
      iVar4 = 0x7fff;
    }
  }
  else {
    iVar4 = -0x7fff;
  }
  uVar1 = (uint)DAT_0002b882;
  if (uVar1 - 1 < 0xffff) {
    iVar5 = (int)DAT_febe7880 * uVar1;
    iVar2 = iVar2 * uVar1;
  }
  else {
    iVar5 = (int)DAT_febe7880 << 0x10;
    iVar2 = iVar2 << 0x10;
  }
  DAT_febe7888 = iVar2 + (DAT_febe7888 - iVar5);
  if (uVar1 - 1 < 0xffff) {
    iVar2 = (int)DAT_febe7882 * uVar1;
    iVar3 = iVar3 * uVar1;
  }
  else {
    iVar2 = (int)DAT_febe7882 << 0x10;
    iVar3 = iVar3 << 0x10;
  }
  DAT_febe788c = iVar3 + (DAT_febe788c - iVar2);
  if (uVar1 - 1 < 0xffff) {
    iVar2 = (int)DAT_febe7884 * uVar1;
    iVar4 = iVar4 * uVar1;
  }
  else {
    iVar2 = (int)DAT_febe7884 << 0x10;
    iVar4 = iVar4 << 0x10;
  }
  DAT_febe7880 = (short)(DAT_febe7888 / 0x10000);
  DAT_febe7890 = iVar4 + (DAT_febe7890 - iVar2);
  DAT_febe7882 = (short)(DAT_febe788c / 0x10000);
  DAT_febe7884 = (short)(DAT_febe7890 / 0x10000);
  return;
}



void FUN_000430f0(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe78c4 = 0;
  DAT_febe78c6 = 0;
  DAT_febe78c8 = 0;
  DAT_febe78cc = 0;
  f33_reset_windowed_monitor((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe7894u)));
  f33_reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3f5c))));
  f33_reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3f4c))));
  return;
}



void FUN_0004311c(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe78c4 = 0;
  DAT_febe78c6 = 0;
  DAT_febe78c8 = 0;
  DAT_febe78cc = 0;
  f33_reset_windowed_monitor((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe7894u)));
  f33_reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3f5c))));
  f33_reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3f4c))));
  return;
}



void FUN_00043148(void)

{
  uint32_t puVar1;
  byte bVar2;
  
  puVar1 = 0xfebeb800u;
  if (DAT_0002bc04 == 'Z') {
    f33_reset_windowed_monitor((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe7894u)));
    f33_reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3f5c))));
    f33_reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3f4c))));
  }
  else {
    bVar2 = DAT_febe74ad |
            DAT_febe74ac |
            DAT_febe74ab |
            DAT_febe7935 |
            DAT_febe792b |
            DAT_febe792e |
            DAT_febe792d | DAT_febe792c | DAT_febe7934 | DAT_febe792a | DAT_febe7929 | DAT_febe7928;
    if (((DAT_febe71ec >> 1 & 1) == 0) && (DAT_febeeb85 == 'Z')) {
      DAT_febe78cc = (int)DAT_febe7880;
      DAT_febe78c8 = DAT_febe6396;
      DAT_febe78c6 = 0x26;
      DAT_febe78c4 = bVar2;
      f33_step_windowed_monitor
                ((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe7894u)),(F33WindowedMonitorLimits *)((undefined *)camry_host_ptr(0x2b858u)),
                 (F33TwoSidedMonitorCallbacks *)&PTR_f33_classify_channel_residual_b_000286b0);
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3f3c))))) = bVar2;
      (*((int *)camry_host_ptr((uint32_t)(puVar1 + -0x3f34)))) = (int)(*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x3f7e))));
      (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x3f38)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x5468))));
      (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x3f3a)))) = 0x27;
      f33_step_windowed_monitor
                (((F33WindowedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3f5c))),
                 (F33WindowedMonitorLimits *)((undefined *)camry_host_ptr(0x2b858u)),
                 (F33TwoSidedMonitorCallbacks *)&PTR_f33_classify_channel_residual_b_000286b0);
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3f3c))))) = bVar2;
      (*((int *)camry_host_ptr((uint32_t)(puVar1 + -0x3f34)))) = (int)(*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x3f7c))));
      (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x3f38)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x5466))));
      (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x3f3a)))) = 0x28;
      f33_step_windowed_monitor
                (((F33WindowedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3f4c))),
                 (F33WindowedMonitorLimits *)((undefined *)camry_host_ptr(0x2b858u)),
                 (F33TwoSidedMonitorCallbacks *)&PTR_f33_classify_channel_residual_b_000286b0);
    }
    else {
      FUN_0006ae48(((undefined *)camry_host_ptr(0xfebe7894u)),((undefined *)camry_host_ptr(0x2b858u)));
      FUN_0006ae48(((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x3f5c))), ((undefined *)camry_host_ptr(0x2b858u)));
      FUN_0006ae48(((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x3f4c))), ((undefined *)camry_host_ptr(0x2b858u)));
    }
  }
  f33_set_channel_monitor_status_b(7,(uchar)(*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x3f6c)))));
  f33_set_channel_monitor_status_b(8,(uchar)(*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x3f5c)))));
  f33_set_channel_monitor_status_b(9,(uchar)(*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x3f4c)))));
  return;
}



/* f33_report_diagnostic_healthy_observed((uint)DAT_febe78c6); whole-body shape-verified. The
   literal is the encoded diagnostic event, not a recovered OEM name. */

void f33_report_diagnostic_healthy_observed_cell_4334c(void)

{
  f33_report_diagnostic_healthy_observed((uint)DAT_febe78c6);
  return;
}



/* f33_report_diagnostic_event_failure((uint)DAT_febe78c6,10); whole-body shape-verified. The
   literal is the encoded diagnostic event, not a recovered OEM name. */

void f33_report_diagnostic_event_failure_10_4335c(void)

{
  f33_report_diagnostic_event_failure((uint)DAT_febe78c6,10);
  return;
}



/* Single constant publisher: DAT_febe78d2 = 0; Shape-classified from the canonical corpus; the
   target cell is not yet named, so the written state's meaning is unknown. */

void FUN_0004336e(void)

{
  DAT_febe78d2 = 0;
  return;
}



/* Single constant publisher: DAT_febe78d2 = 0; Shape-classified from the canonical corpus; the
   target cell is not yet named, so the written state's meaning is unknown. */

void FUN_00043374(void)

{
  DAT_febe78d2 = 0;
  return;
}



void FUN_0004337a(void)

{
  undefined *puVar1;
  char cVar3;
  uchar status;
  byte bVar4;
  uint32_t puVar2;
  cVar3 = DAT_febe78d1;
  bVar4 = DAT_febe78d0;
  puVar2 = 0xfebeb800u;
  puVar1 = ((undefined *)camry_host_ptr(0xfebeb800u));
  if (DAT_0002bc08 != 'Z') {
    if ((DAT_febe71ec >> 1 & 1) == 0) {
      if (DAT_febe6429 == 'Z') {
        status = '\"';
        f33_report_diagnostic_event_failure(0x19,10);
        puVar1 = ((undefined *)camry_host_ptr((uint32_t)(puVar2)));
      }
      else {
        if (DAT_febe6428 == '\0') {
          status = '\0';
          if (((DAT_0002b89c < DAT_febe7da8) || (f33_output_request_status >> 0x10 != 0)) ||
             (DAT_febeeb85 != 'Z')) {
            bVar4 = 0;
          }
          else if (DAT_febe78d0 < DAT_0002b89a) {
            bVar4 = DAT_febe78d0 + 1;
          }
          else if (DAT_febe78d1 != 'Z') {
            puVar1 = ((undefined *)camry_host_ptr(0xfebeb800u));
            f33_report_diagnostic_healthy_observed(0x19);
            cVar3 = 'Z';
          }
          goto LAB_00043418;
        }
        status = '\x11';
        puVar1 = ((undefined *)camry_host_ptr(0xfebeb800u));
      }
      bVar4 = 0;
      goto LAB_00043418;
    }
    status = DAT_febe78d2;
    if (DAT_febe78d2 != '\x11') goto LAB_00043418;
  }
  status = '\0';
LAB_00043418:
  puVar1[-0x3f30] = bVar4;
  puVar1[-0x3f2f] = cVar3;
  puVar1[-0x3f2e] = status;
  f33_set_channel_monitor_status_b(0xc,status);
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4342e(void)

{
  return;
}



/* Constant-block fill: 7 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_43430(void)

{
  DAT_febe78d4 = 0;
  DAT_febe78d5 = 0;
  DAT_febe78d6 = 0;
  DAT_febe78d7 = 0;
  DAT_febe78d8 = 0x8000;
  DAT_febe78da = 0x8000;
  DAT_febe78dc = 0x8000;
  return;
}



/* Parallel sum from823E..8242 versus8232..8236 with31E66==5A and independent validity. Independent
   second-channel sample-difference sum with matching retained-member selection. */

int f33_sum_channel_snapshot_differences_b(void)

{
  ushort uVar1;
  char cVar4;
  char cVar5;
  ushort uVar2;
  ushort uVar3;
  
  uVar1 = DAT_febe823e;
  uVar2 = DAT_febe8242;
  uVar3 = DAT_febe8240;
  if (DAT_00031e66 != 'Z') goto LAB_000434b2;
  if (DAT_febeeac1 == 'Z') {
    cVar4 = DAT_febe7e24;
    cVar5 = DAT_febe7e25;
    if (DAT_febe7e23 == 'Z') goto LAB_00043478;
  }
  else {
    cVar4 = 'Z';
    cVar5 = 'Z';
LAB_00043478:
    DAT_febe78d8 = DAT_febe823e;
  }
  if (cVar4 == 'Z') {
    DAT_febe78da = DAT_febe8240;
  }
  uVar1 = DAT_febe78d8;
  uVar2 = DAT_febe78dc;
  uVar3 = DAT_febe78da;
  if (cVar5 == 'Z') {
    DAT_febe78dc = DAT_febe8242;
    uVar2 = DAT_febe8242;
  }
LAB_000434b2:
  return ((uint)uVar2 - (uint)DAT_febe8236) +
         ((uint)uVar3 - (uint)DAT_febe8234) + ((uint)uVar1 - (uint)DAT_febe8232);
}



/* Parallel delayed snapshot latch; retain failure high-water count. Later5CA3A snapshot and4337A
   consumption are separate generations. Parallel delayed snapshot producer; later snapshot and
   status consumption are distinct generations. */

void f33_step_channel_difference_latch_b(void)

{
  short sVar1;
  ushort uVar2;
  byte bVar3;
  int iVar4;
  uint32_t puVar5;
  int iVar6;
  int iVar7;
  byte bVar8;
  undefined1 uVar9;
  byte bVar10;
  byte bVar11;
  
  uVar9 = DAT_febe78d7;
  bVar3 = DAT_febe78d6;
  bVar10 = DAT_febe78d5;
  bVar11 = DAT_febe78d4;
  puVar5 = 0xfebeb800u;
  if (((byte)DAT_febe71ec & 2) == 0) {
    iVar6 = f33_sum_channel_snapshot_differences_b();
    uVar2 = DAT_00031e6a;
    sVar1 = DAT_00031e68;
    if (iVar6 + 0x7fffffff < 0 == (-1 < iVar6 && iVar6 + 0x7fffffff < 0) && iVar6 != -0x7fffffff) {
      iVar4 = iVar6;
      if (iVar6 < 0) {
        iVar4 = -iVar6;
      }
    }
    else {
      iVar4 = 0x7fffffff;
    }
    iVar7 = (int)DAT_00031e68;
    (*((int *)camry_host_ptr((uint32_t)(puVar5 + -0x3f20)))) = iVar6;
    (*((short *)camry_host_ptr((uint32_t)(puVar5 + -0x3f22)))) = sVar1;
    bVar8 = bVar3;
    if ((iVar4 - iVar7 < 0 == (iVar4 < 0 != iVar7 < 0 && iVar7 < 0 == iVar4 - iVar7 < 0) &&
         iVar4 != iVar7) && ((*((ushort *)camry_host_ptr((uint32_t)(puVar5 + -0x3a58)))) <= uVar2)) {
      bVar10 = 0;
      if (bVar11 < DAT_00031e64) {
        uVar9 = 0;
        bVar11 = bVar11 + 1;
        bVar8 = bVar11;
        if (bVar11 <= bVar3) {
          bVar8 = bVar3;
        }
      }
      else {
        uVar9 = 0x5a;
      }
    }
    else if (bVar10 < DAT_00031e65) {
      bVar10 = bVar10 + 1;
    }
    else {
      bVar11 = 0;
      uVar9 = 0xa5;
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3f2c))))) = bVar11;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3f2b))))) = bVar10;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3f2a))))) = bVar8;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3f29))))) = uVar9;
  }
  return;
}



void FUN_00043554(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe78e4 = 0;
  DAT_febe78e6 = 0;
  DAT_febe78e8 = 0;
  f33_reset_windowed_monitor((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe78ecu)));
  f33_reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3f04))));
  f33_reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3ef4))));
  f33_reset_recoverable_monitor(((F33RecoverableMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3ee4))));
  return;
}



void FUN_00043586(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe78e4 = 0;
  DAT_febe78e6 = 0;
  DAT_febe78e8 = 0;
  f33_reset_windowed_monitor((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe78ecu)));
  f33_reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3f04))));
  f33_reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3ef4))));
  f33_reset_recoverable_monitor(((F33RecoverableMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3ee4))));
  return;
}



/* Parallel phase qualification and immediate aggregate counter monitor; diagnostic events1B/1C/1D
   are separate from slot3 action kinds. Exact count25 remains pending but nonzero phase count
   independently confirms aggregate status10. Distinct status lifetimes reach actual slot3 action
   composition. */

void f33_step_channel_phase_monitors_b(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bc0c == 'Z') {
    puVar1 = 0xfebeb800u;
    f33_reset_windowed_monitor((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe78ecu)));
    f33_reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3f04))));
    f33_reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3ef4))));
  }
  else {
    if (((DAT_febe71ec >> 1 & 1) == 0) && (DAT_febeeb85 == 'Z')) {
      DAT_febe78e4 = 0x1b;
      DAT_febe78e6 = f33_monitor_current_dynamic_reference_plane[3];
      DAT_febe78e8 = f33_monitor_current_second_midpoint_plane[3];
      f33_step_windowed_monitor
                ((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe78ecu)),(F33WindowedMonitorLimits *)((undefined *)camry_host_ptr(0x2b860u)),
                 (F33TwoSidedMonitorCallbacks *)&PTR_f33_classify_channel_phase_sample_b_000286e4);
      (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x3f1c)))) = 0x1c;
      (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x3f1a)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x3980))));
      (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x3f18)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x3974))));
      f33_step_windowed_monitor
                (((F33WindowedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3f04))),
                 (F33WindowedMonitorLimits *)((undefined *)camry_host_ptr(0x2b860u)),
                 (F33TwoSidedMonitorCallbacks *)&PTR_f33_classify_channel_phase_sample_b_000286e4);
      (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x3f1c)))) = 0x1d;
      (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x3f1a)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x397e))));
      (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x3f18)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x3972))));
      f33_step_windowed_monitor
                (((F33WindowedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3ef4))),
                 (F33WindowedMonitorLimits *)((undefined *)camry_host_ptr(0x2b860u)),
                 (F33TwoSidedMonitorCallbacks *)&PTR_f33_classify_channel_phase_sample_b_000286e4);
      f33_step_recoverable_monitor
                (((F33RecoverableMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3ee4))),
                 (F33RecoverableMonitorLimits *)((undefined *)camry_host_ptr(0x2b868u)),
                 (F33RecoverableMonitorCallbacks *)
                 &PTR_f33_classify_channel_phase_failure_count_b_00028718);
      goto LAB_000436a4;
    }
    puVar1 = 0xfebeb800u;
    FUN_0006ae48(((undefined *)camry_host_ptr(0xfebe78ecu)),((undefined *)camry_host_ptr(0x2b860u)));
    FUN_0006ae48(((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x3f04))), ((undefined *)camry_host_ptr(0x2b860u)));
    FUN_0006ae48(((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x3ef4))), ((undefined *)camry_host_ptr(0x2b860u)));
  }
  f33_reset_recoverable_monitor(((F33RecoverableMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3ee4))));
LAB_000436a4:
  f33_set_channel_monitor_status_b(0,(uchar)(*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x3f14)))));
  f33_set_channel_monitor_status_b(1,(uchar)(*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x3f04)))));
  f33_set_channel_monitor_status_b(2,(uchar)(*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x3ef4)))));
  f33_set_channel_monitor_status_b(10,(uchar)(*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x3ee4)))));
  return;
}



/* Matching sample/comparison classifier with source62E5 and unsigned7DA8 admission. Second-channel
   phase predicate uses matching exact bounds with independent sample/comparison/source and unsigned
   gate. */

uint f33_classify_channel_phase_sample_b(void)

{
  ushort uVar1;
  ushort uVar2;
  char cVar3;
  ushort uVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  short sStack_22;
  
  uVar4 = DAT_febe7da8;
  cVar3 = DAT_febe62e5;
  uVar2 = DAT_0002b8aa;
  uVar1 = DAT_0002b8a4;
  iVar8 = (int)DAT_febe78e8;
  iVar7 = (int)DAT_febe62dc;
  FUN_0006a522((int)DAT_febe78e6,&sStack_22);
  iVar5 = (int)sStack_22;
  iVar6 = (int)DAT_0002b8a0;
  if (cVar3 == '\0') {
    if ((((iVar5 - iVar6 < 0 == (iVar5 < 0 != iVar6 < 0 && iVar6 < 0 == iVar5 - iVar6 < 0) &&
           iVar5 != iVar6) ||
         (iVar6 = (int)DAT_0002b8a2,
         iVar8 - iVar6 < 0 != (iVar8 < 0 != iVar6 < 0 && iVar6 < 0 == iVar8 - iVar6 < 0))) &&
        (uVar4 <= uVar1)) &&
       (iVar6 = (int)DAT_0002b8ac,
       iVar7 - iVar6 < 0 == (iVar7 < 0 != iVar6 < 0 && iVar6 < 0 == iVar7 - iVar6 < 0) &&
       iVar7 != iVar6)) {
      return 0x22;
    }
    iVar6 = (int)DAT_0002b8a6;
    if (iVar5 - iVar6 < 0 == (iVar5 < 0 != iVar6 < 0 && iVar6 < 0 == iVar5 - iVar6 < 0) &&
        iVar5 != iVar6) {
      return 0x33;
    }
    iVar5 = (int)DAT_0002b8a8;
    if (iVar8 - iVar5 < 0 != (iVar8 < 0 != iVar5 < 0 && iVar5 < 0 == iVar8 - iVar5 < 0)) {
      return 0x33;
    }
  }
  else {
    if (((iVar5 - iVar6 < 0 == (iVar5 < 0 != iVar6 < 0 && iVar6 < 0 == iVar5 - iVar6 < 0) &&
          iVar5 != iVar6) && (uVar4 <= uVar1)) &&
       (iVar6 = (int)DAT_0002b8ac,
       iVar7 - iVar6 < 0 == (iVar7 < 0 != iVar6 < 0 && iVar6 < 0 == iVar7 - iVar6 < 0) &&
       iVar7 != iVar6)) {
      return 0x22;
    }
    iVar6 = (int)DAT_0002b8a6;
    if (iVar5 - iVar6 < 0 == (iVar5 < 0 != iVar6 < 0 && iVar6 < 0 == iVar5 - iVar6 < 0) &&
        iVar5 != iVar6) {
      return 0x33;
    }
  }
  if (uVar2 < uVar4) {
    return 0x33;
  }
  return 0x11;
}



/* f33_report_diagnostic_healthy_observed((uint)DAT_febe78e4); whole-body shape-verified. The
   literal is the encoded diagnostic event, not a recovered OEM name. */

void f33_report_diagnostic_healthy_observed_cell_43762(void)

{
  f33_report_diagnostic_healthy_observed((uint)DAT_febe78e4);
  return;
}



/* f33_report_diagnostic_event_failure((uint)DAT_febe78e4,10); whole-body shape-verified. The
   literal is the encoded diagnostic event, not a recovered OEM name. */

void f33_report_diagnostic_event_failure_10_43772(void)

{
  f33_report_diagnostic_event_failure((uint)DAT_febe78e4,10);
  return;
}



/* Parallel immediate aggregate predicate at ROM28718; not itself a diagnostic event. Parallel
   failure-counter aggregate can confirm before its phase and independently select ancillary action.
    */

uint f33_classify_channel_phase_failure_count_b(void)

{
  ushort uVar1;
  
  uVar1 = (ushort)DAT_0002b89e;
  if (((DAT_febe78f4 < uVar1) && (DAT_febe7904 < uVar1)) && (DAT_febe7914 < uVar1)) {
    return 0x11;
  }
  return 0x22;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_437b0(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_437b2(void)

{
  return;
}



/* Parallel slot3 reduction from7928..7935 with71EC.bit1 and distinct action kinds. Phase status11
   can coexist with aggregate status22, producing ancillary action without phase confirmation;
   aggregate10 is excluded from third summary and channel caches. Second-channel phase remains
   pending at25 while aggregate10 confirms and publishes ancillary action. Aggregate10 is excluded
   from third summary and channel caches; native summary remains zero for other-status OR11. */

void f33_publish_channel_monitor_actions_b(void)

{
  byte bVar1;
  byte bVar2;
  ushort uVar3;
  uint32_t puVar4;
  uchar uVar5;
  undefined1 uVar6;
  
  uVar3 = DAT_febe71ec;
  puVar4 = 0xfebeb800u;
  f33_retain_and_clear_fault_record(3);
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ecb))))) |
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ecc))))) |
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed2))))) |
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed3))))) |
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed4))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed5))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed6))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed7))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed8)))))) &
      0x11) == 0x11) {
    f33_encode_fault_action_kind('\x03','\n');
  }
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ecc))))) |
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed6))))) |
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed7))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed8))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed2))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed3))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed4)))))) &
      0x22) == 0x22) {
    f33_encode_fault_action_kind('\x03','$');
  }
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ecb))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed5))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ecf))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed0))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed1)))))) &
      0x22) == 0x22) {
    f33_encode_fault_action_kind('\x03','\x1c');
  }
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ecd))))) & 0x22) == 0x22) {
    f33_encode_fault_action_kind('\x03','\x1e');
  }
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ece))))) & 0x22) == 0x22) {
    f33_encode_fault_action_kind('\x03','(');
  }
  if (((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ecb))))) |
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ecc))))) |
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed2))))) |
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed3))))) |
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed4))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed5))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed6))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed7))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed8)))))) &
       0x22) == 0x22) && ((uVar3 >> 1 & 1) == 0)) {
    f33_encode_fault_action_kind('\x03','\n');
  }
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ecc))))) |
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed2))))) |
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed3))))) |
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed4))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed5))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed6))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed7))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed8)))))) &
      0x22) == 0x22) {
    f33_encode_fault_action_kind('\x03','2');
  }
  f33_select_current_fault_record(3);
  bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed6))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed7))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed8)))));
  uVar6 = 0;
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed1))))) | bVar1 | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed0))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ecf)))))) & 0x11) == 0x11) {
    uVar6 = 0x5a;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3eca))))) = uVar6;
  uVar6 = 0x11;
  if ((((((bVar1 == 0 && (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed5))))) == '\0') && (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed4))))) == '\0') &&
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed3))))) == '\0') && (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed2))))) == '\0') && (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ecc))))) == '\0') &&
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ecb))))) == '\0') {
    uVar6 = 0;
  }
  uVar5 = '\0';
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ec9))))) = uVar6;
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ecb))))) != '\0' ||
      ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ecd))))) != '\0' ||
      ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ecf))))) != 0 ||
      ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed0))))) != 0 ||
      ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed1))))) != 0 ||
      ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed5))))) != '\0' ||
      ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed6))))) != 0 ||
      ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed7))))) != 0 ||
      ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed8))))) != 0 ||
      ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed2))))) != '\0' ||
      ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed3))))) != '\0' || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed4))))) != '\0' || (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ecc))))) != '\0')))))))))))) {
    uVar5 = '\x11';
  }
  f33_set_diagnostic_cache_blocker('\x04',uVar5);
  bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed6))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed7))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed8)))));
  bVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ecb))))) |
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ecd))))) |
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ecf))))) |
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ecc))))) | bVar1 | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed4))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed3))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed2))))) |
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed5))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed1))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed0)))));
  if ((bVar2 == 0) || (bVar2 == 0x11)) {
    uVar6 = 0;
  }
  else {
    uVar6 = 0x5a;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ec8))))) = uVar6;
  uVar5 = '\0';
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ecd))))) |
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ecf))))) |
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed0))))) |
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed1))))) |
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ecb))))) |
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ecc))))) |
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed2))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed3))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed4))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed5))))) | bVar1) & 0x11) ==
      0x11) {
    uVar5 = 'Z';
  }
  f33_set_monitor_pending_projection('\x03',uVar5);
  return;
}



/* Bound unsigned index<14 before storing one status byte at7928+index. Matching bounded setter for
   second-channel status bank. */

void f33_set_channel_monitor_status_b(uint index,uchar status)

{
  if ((index & 0xff) < 0xe) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7928u + (uint32_t)(index & 0xff) * 1u)))) = status;
  }
  return;
}



/* f33_reset_latched_monitor wrapper resetting exactly one monitor state ((F33LatchedMonitorState
   *)((undefined *)camry_host_ptr(0xfebe793cu))); whole-body shape-verified from the canonical corpus. Per-instance semantics
   derive from the referenced state cell; not individually executed. */

void f33_reset_latched_monitor_febe793c(void)

{
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe793cu)));
  return;
}



/* f33_reset_latched_monitor wrapper resetting exactly one monitor state ((F33LatchedMonitorState
   *)((undefined *)camry_host_ptr(0xfebe793cu))); whole-body shape-verified from the canonical corpus. Per-instance semantics
   derive from the referenced state cell; not individually executed. */

void f33_reset_latched_monitor_febe793c_43a1c(void)

{
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe793cu)));
  return;
}



void FUN_00043a2c(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bc10 == 'Z') {
    f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe793cu)));
  }
  else if (((DAT_febe6764 >> 1 & 1) == 0) && (DAT_febee820 == 'Z')) {
    f33_step_latched_monitor
              ((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe793cu)),(F33MonitorLimits *)((undefined *)camry_host_ptr(0x2b86eu)),
               (F33TwoSidedMonitorCallbacks *)&PTR_FUN_00028754);
  }
  else {
    f33_retain_disabled_latched_monitor
              ((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe793cu)),(F33MonitorLimits *)((undefined *)camry_host_ptr(0x2b86eu)));
  }
  f33_set_channel_monitor_status_b(0xb,(uchar)(*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x3ec4)))));
  return;
}



undefined4 FUN_00043a86(void)

{
  int iVar1;
  int iVar2;
  
  iVar1 = (uint)DAT_febe66b8 - (uint)DAT_febe66b0;
  if ((DAT_febe827a == 'Z') &&
     (((uint)DAT_0002b8ae < (uint)DAT_febe66b8 ||
      (iVar2 = (int)DAT_0002b8b0,
      iVar1 - iVar2 < 0 != (iVar1 < 0 != iVar2 < 0 && iVar2 < 0 == iVar1 - iVar2 < 0) ||
      iVar1 == iVar2)))) {
    return 0x5a;
  }
  return 0;
}



undefined4 FUN_00043ab6(void)

{
  char cVar1;
  uint uVar2;
  char cVar3;
  char cVar4;
  char cVar5;
  int iVar6;
  undefined4 uVar7;
  
  cVar5 = DAT_febe827f;
  cVar4 = DAT_febe827a;
  cVar3 = DAT_febe8279;
  uVar2 = DAT_febe6618;
  cVar1 = DAT_febe65f7;
  iVar6 = FUN_00043a86();
  if ((cVar1 == 'Z') && ((uVar2 >> 1 & 1) == 0)) {
    if ((cVar3 == 'Z') || ((iVar6 == 0x5a || (cVar5 == 'Z')))) {
      uVar7 = 0x22;
    }
    else if (((cVar3 == '\0') && (cVar4 == '\0')) && (cVar5 == '\0')) {
      uVar7 = 0x11;
    }
    else {
      uVar7 = 0x33;
    }
  }
  else {
    uVar7 = 0x44;
  }
  return uVar7;
}



/* f33_report_diagnostic_healthy_observed(0x87); whole-body shape-verified. The literal is the
   encoded diagnostic event, not a recovered OEM name. */

void f33_report_diagnostic_healthy_observed_87_43b12(void)

{
  f33_report_diagnostic_healthy_observed(0x87);
  return;
}



/* f33_report_diagnostic_event_failure(0x87,0x32); whole-body shape-verified. The literal is the
   encoded diagnostic event, not a recovered OEM name. */

void f33_report_diagnostic_event_failure_87_32_43b22(void)

{
  f33_report_diagnostic_event_failure(0x87,0x32);
  return;
}



/* f33_reset_latched_monitor wrapper resetting exactly one monitor state ((F33LatchedMonitorState
   *)((undefined *)camry_host_ptr(0xfebe7948u))); whole-body shape-verified from the canonical corpus. Per-instance semantics
   derive from the referenced state cell; not individually executed. */

void f33_reset_latched_monitor_febe7948(void)

{
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7948u)));
  return;
}



/* f33_reset_latched_monitor wrapper resetting exactly one monitor state ((F33LatchedMonitorState
   *)((undefined *)camry_host_ptr(0xfebe7948u))); whole-body shape-verified from the canonical corpus. Per-instance semantics
   derive from the referenced state cell; not individually executed. */

void f33_reset_latched_monitor_febe7948_43b46(void)

{
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7948u)));
  return;
}



void FUN_00043b56(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bc14 == 'Z') {
    f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7948u)));
  }
  else if (((DAT_febe71ec >> 1 & 1) == 0) && (DAT_febeeb85 == 'Z')) {
    f33_step_latched_monitor
              ((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7948u)),(F33MonitorLimits *)((undefined *)camry_host_ptr(0x2b872u)),
               (F33TwoSidedMonitorCallbacks *)&PTR_f33_classify_channel_raw_lower_bound_b_00028788);
  }
  else {
    f33_retain_disabled_latched_monitor
              ((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7948u)),(F33MonitorLimits *)((undefined *)camry_host_ptr(0x2b872u)));
  }
  f33_set_channel_monitor_status_b(0xd,(uchar)(*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x3eb8)))));
  return;
}



/* Parallel623E/6240/6242 with636F/70/71 validity and high16 8B28 gate. Parallel raw predicate uses
   high-half gate and independent sample/validity triplet; neutral and failed admission remain
   distinct. */

uint f33_classify_channel_raw_lower_bound_b(void)

{
  if (f33_output_request_status >> 0x10 != 0) {
    return 0x44;
  }
  if ((((DAT_0002b8b2 <= DAT_febe623e) || (DAT_febe636f != 'Z')) &&
      ((DAT_0002b8b2 <= DAT_febe6240 || (DAT_febe6370 != 'Z')))) &&
     ((DAT_0002b8b2 <= DAT_febe6242 || (DAT_febe6371 != 'Z')))) {
    if ((DAT_0002b8b4 <= DAT_febe623e) &&
       ((((DAT_febe636f == 'Z' && (DAT_0002b8b4 <= DAT_febe6240)) && (DAT_febe6370 == 'Z')) &&
        ((DAT_0002b8b4 <= DAT_febe6242 && (DAT_febe6371 == 'Z')))))) {
      return 0x11;
    }
    return 0x33;
  }
  return 0x22;
}



/* f33_report_diagnostic_healthy_observed(0x139); whole-body shape-verified. The literal is the
   encoded diagnostic event, not a recovered OEM name. */

void f33_report_diagnostic_healthy_observed_139_43c2c(void)

{
  f33_report_diagnostic_healthy_observed(0x139);
  return;
}



/* f33_report_diagnostic_event_failure(0x139,10); whole-body shape-verified. The literal is the
   encoded diagnostic event, not a recovered OEM name. */

void f33_report_diagnostic_event_failure_139_10_43c3c(void)

{
  f33_report_diagnostic_event_failure(0x139,10);
  return;
}



/* f33_reset_windowed_monitor wrapper resetting exactly one monitor state ((F33WindowedMonitorState
   *)((undefined *)camry_host_ptr(0xfebe7954u))); whole-body shape-verified from the canonical corpus. Per-instance semantics
   derive from the referenced state cell; not individually executed. */

void f33_reset_windowed_monitor_febe7954(void)

{
  f33_reset_windowed_monitor((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe7954u)));
  return;
}



/* f33_reset_windowed_monitor wrapper resetting exactly one monitor state ((F33WindowedMonitorState
   *)((undefined *)camry_host_ptr(0xfebe7954u))); whole-body shape-verified from the canonical corpus. Per-instance semantics
   derive from the referenced state cell; not individually executed. */

void f33_reset_windowed_monitor_febe7954_43c5e(void)

{
  f33_reset_windowed_monitor((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe7954u)));
  return;
}



/* f33_report_diagnostic_healthy_observed(0x24); whole-body shape-verified. The literal is the
   encoded diagnostic event, not a recovered OEM name. */

void f33_report_diagnostic_healthy_observed_24_43da2(void)

{
  f33_report_diagnostic_healthy_observed(0x24);
  return;
}



/* f33_report_diagnostic_event_failure(0x24,10); whole-body shape-verified. The literal is the
   encoded diagnostic event, not a recovered OEM name. */

void f33_report_diagnostic_event_failure_24_10_43db2(void)

{
  f33_report_diagnostic_event_failure(0x24,10);
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_43dc4(void)

{
  return;
}



/* Constant-block fill: 6 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_43dc6(void)

{
  DAT_febe7964 = 0;
  DAT_febe7965 = 0;
  DAT_febe7966 = 0;
  DAT_febe7967 = 0;
  DAT_febe7968 = 0;
  DAT_febe796c = 0;
  return;
}



undefined1 FUN_00043dd8(ushort param_1,undefined1 param_2)

{
  if (((DAT_0002fbce < DAT_febe7db0) && (DAT_0002fbca < param_1)) && (DAT_febe7bb9 != 'Z')) {
    return 0x5a;
  }
  if ((DAT_febe7db0 <= (ushort)PTR_DAT_0002fbd0) && (param_1 <= DAT_0002fbcc)) {
    param_2 = 0;
  }
  return param_2;
}



void FUN_00043e14(char param_1)

{
  uint32_t puVar1;
  undefined4 uVar2;
  
  puVar1 = 0xfebeb800u;
  uVar2 = DAT_febe7968;
  if (DAT_0002bc30 == '\0') {
    if ((DAT_0002fbc9 == 'Z') && (param_1 == 'Z')) {
      uVar2 = 0xc;
    }
    else {
      uVar2 = 2;
    }
  }
  FUN_00056cda(4,uVar2);
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x3e98)))) = uVar2;
  return;
}



void FUN_00043e54(void)

{
  uint32_t puVar1;
  uint uVar2;
  
  puVar1 = 0xfebeb800u;
  uVar2 = (uint)DAT_febe7964;
  if (((byte)DAT_febe71ec & 1) == 0) {
    puVar1 = 0xfebeb800u;
    uVar2 = FUN_00043dd8(DAT_febe7da6,uVar2);
  }
  FUN_00043e14(uVar2);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3e9c))))) = (char)uVar2;
  return;
}



void FUN_00043e7c(char param_1)

{
  uint32_t puVar1;
  undefined4 uVar2;
  
  puVar1 = 0xfebeb800u;
  uVar2 = DAT_febe796c;
  if (DAT_0002bc34 == '\0') {
    if ((DAT_0002fbc9 == 'Z') && (param_1 == 'Z')) {
      uVar2 = 0xc0000;
    }
    else {
      uVar2 = 0x20000;
    }
  }
  FUN_00056cda(5,uVar2);
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x3e94)))) = uVar2;
  return;
}



void FUN_00043ec0(void)

{
  uint32_t puVar1;
  uint uVar2;
  
  puVar1 = 0xfebeb800u;
  uVar2 = (uint)DAT_febe7965;
  if (((byte)DAT_febe71ec & 2) == 0) {
    puVar1 = 0xfebeb800u;
    uVar2 = FUN_00043dd8(DAT_febe7da8,uVar2);
  }
  FUN_00043e7c(uVar2);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3e9b))))) = (char)uVar2;
  return;
}



void FUN_00043ee8(void)

{
  if (((DAT_0002fbc8 != 'Z') || (DAT_febe7967 = DAT_febe7964, DAT_febe7964 != 'Z')) &&
     (DAT_febe7967 = '\0', DAT_0002fbc8 != 'Z')) {
    DAT_febe7966 = 0;
    DAT_febe7967 = 0;
    return;
  }
  if (DAT_febe7965 != 'Z') {
    DAT_febe7966 = 0;
    return;
  }
  DAT_febe7966 = DAT_febe7965;
  return;
}



void FUN_00043f1a(void)

{
  if (DAT_febeeb85 == 'Z') {
    FUN_00043e54();
    FUN_00043ec0();
    FUN_00043ee8();
  }
  return;
}



/* f33_reset_latched_monitor wrapper resetting exactly one monitor state ((F33LatchedMonitorState
   *)((undefined *)camry_host_ptr(0xfebe7970u))); whole-body shape-verified from the canonical corpus. Per-instance semantics
   derive from the referenced state cell; not individually executed. */

void f33_reset_latched_monitor_febe7970(void)

{
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7970u)));
  return;
}



/* f33_reset_latched_monitor wrapper resetting exactly one monitor state ((F33LatchedMonitorState
   *)((undefined *)camry_host_ptr(0xfebe7970u))); whole-body shape-verified from the canonical corpus. Per-instance semantics
   derive from the referenced state cell; not individually executed. */

void f33_reset_latched_monitor_febe7970_43f48(void)

{
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7970u)));
  return;
}



void FUN_00043f58(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bc1c == 'Z') {
    f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7970u)));
  }
  else if (((DAT_febe71ec >> 1 & 1) == 0) || (DAT_febeeb85 != 'Z')) {
    f33_report_diagnostic_healthy_observed(0xe2);
  }
  else {
    f33_step_latched_monitor
              ((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7970u)),(F33MonitorLimits *)((undefined *)camry_host_ptr(0x2b8c4u)),
               (F33TwoSidedMonitorCallbacks *)&PTR_f33_classify_inverse_gate_a_000287f0);
  }
  f33_publish_shared_condition_monitor_status(7,(*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x3e90)))));
  return;
}



/* Exact slot0/1 callback predicate. Return11/22/33/44 protocol; software source, qualification and
   retained-snapshot conditions are not physical freshness guarantees. InverseA gate>6400 and
   shared<=4096 fails22, else11; wrapper uses pass0/fail50, not immediate failure. */

uint f33_classify_inverse_gate_a(void)

{
  if ((DAT_0002b8ea < DAT_febe7da6) && (DAT_febe7db0 <= DAT_0002b8e8)) {
    return 0x22;
  }
  return 0x11;
}



/* f33_report_diagnostic_event_failure(0xe2,10); whole-body shape-verified. The literal is the
   encoded diagnostic event, not a recovered OEM name. */

void f33_report_diagnostic_event_failure_e2_10_43fd8(void)

{
  f33_report_diagnostic_event_failure(0xe2,10);
  return;
}



/* f33_reset_latched_monitor wrapper resetting exactly one monitor state ((F33LatchedMonitorState
   *)((undefined *)camry_host_ptr(0xfebe797cu))); whole-body shape-verified from the canonical corpus. Per-instance semantics
   derive from the referenced state cell; not individually executed. */

void f33_reset_latched_monitor_febe797c(void)

{
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe797cu)));
  return;
}



/* f33_reset_latched_monitor wrapper resetting exactly one monitor state ((F33LatchedMonitorState
   *)((undefined *)camry_host_ptr(0xfebe797cu))); whole-body shape-verified from the canonical corpus. Per-instance semantics
   derive from the referenced state cell; not individually executed. */

void f33_reset_latched_monitor_febe797c_43ffa(void)

{
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe797cu)));
  return;
}


