#include "common.h"


/* WARNING: This is an inlined function */
/* Length0returns1 unchanged. Otherwise alignaddressdown512, add low9bits tolength modulo32,
   fillthat manyFF prefixbytes in1800 ring; publishproducer=prefix,consumer0 andreturn0. Realleaf
   preservesR6/R7/R9 for411A subsequent40E0; inlineactualp-code. Lateradmission failure doesnotundo
   ringmutation. Native combined admission verifies retained original range, aligned prefix and
   pending state; no flash completion. */

uint f33_boot_prepare_aligned_input_ring
               (uint address,uint length,uint *aligned_address,uint *padded_length)

{
  int iVar1;
  uint uVar2;
  
  if (length != 0) {
    uVar2 = address & 0x1ff;
    *aligned_address = address & 0xfffffe00;
    *padded_length = uVar2 + length;
    for (iVar1 = 0; (int)(iVar1 - uVar2) < 0 != (iVar1 < 0 && -1 < (int)(iVar1 - uVar2));
        iVar1 = iVar1 + 1) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebf1800u + (uint32_t)(iVar1) * 1u)))) = 0xff;
    }
    DAT_febf2998 = (short)uVar2;
    DAT_febf299a = 0;
    return 0;
  }
  return 1;
}



/* Rejectlength0 orfailedfirst3474 lookup. Lookup modulo32lastaddress, ignoresecondlookupreturn,
   andreturn(last_block<first_block). An out-of-range lastaddress can use3474 fallbackF8000; this is
   not complete region validation. */

uint f33_boot_select_operation_blocks(uint address,uint length,uint *first_block,uint *last_block)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = 1;
  if (length != 0) {
    uVar1 = f33_boot_find_flash_block_start(address,first_block);
    if (uVar1 == 0) {
      f33_boot_find_flash_block_start((length + address) - 1,last_block);
      uVar2 = (uint)(*last_block < *first_block);
    }
  }
  return uVar2;
}



/* WARNING: Inlined function: f33_boot_prepare_aligned_input_ring */
/* Rejectbusy2AA1.40A2prepares512-aligned ringbefore40E0rangeadmission. Onaccept
   setmode0,currentblock/nextboundary,writecursor,paddedremaining,result1,busy1;
   clearfinal/cancel/pause. Retain prior2994counter-block selection.0accepted/1rejected;
   notflashcompletion. Native combined admission verifies retained original range, aligned prefix
   and pending state; no flash completion. */

uint f33_boot_submit_erase_program_stream(uint address,uint length)

{
  bool bVar1;
  int iVar2;
  uint32_t puVar3;
  uint uVar4;
  uint uVar5;
  uint local_24;
  uint uStack_20;
  uint uStack_1c;
  uint uStack_18;
  int iStack_14;
  
  puVar3 = 0xfebf9800u;
  uVar5 = 1;
  if (DAT_febf2aa1 == '\0') {
    if (length == 0) {
      bVar1 = true;
    }
    else {
      uStack_18 = address & 0xfffffe00;
      uVar4 = address & 0x1ff;
      iStack_14 = uVar4 + length;
      for (iVar2 = 0; (int)(iVar2 - uVar4) < 0 != (iVar2 < 0 && -1 < (int)(iVar2 - uVar4));
          iVar2 = iVar2 + 1) {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebf1800u + (uint32_t)(iVar2) * 1u)))) = 0xff;
      }
      DAT_febf2998 = (undefined2)uVar4;
      bVar1 = false;
      DAT_febf299a = 0;
    }
    if ((!bVar1) &&
       (uVar4 = f33_boot_select_operation_blocks(address,length,&local_24,&uStack_20), uVar4 == 0))
    {
      (*((uint *)camry_host_ptr((uint32_t)(puVar3 + -0x6e74)))) = uStack_18;
      (*((uint *)camry_host_ptr((uint32_t)(puVar3 + -0x6e80)))) = local_24;
      (*((int *)camry_host_ptr((uint32_t)(puVar3 + -0x6e70)))) = iStack_14;
      f33_boot_find_flash_block_end(local_24,&uStack_1c);
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-28000))))) = 1;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-27999))))) = 1;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6e64))))) = 0;
      uVar5 = 0;
      (*((uint *)camry_host_ptr((uint32_t)(puVar3 + -0x6e78)))) = uStack_1c;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6e63))))) = 0;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6e62))))) = 0;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6e61))))) = 0;
    }
  }
  return uVar5;
}



/* WARNING: Inlined function: f33_boot_prepare_aligned_input_ring */
/* Rejectbusy;40A2seedsalignmentprefixbefore3562 ECC-backedroundedblankcheck. Onaccept
   setmode1,writecursor,paddedremaining,result1,busy1;clearfinal/cancel/pause.0accepted/1rejected.
   Hardwareblankcheck andfailed-admission ringeffects are separate. */

uint f33_boot_submit_program_stream(uint address,uint length)

{
  bool bVar1;
  int iVar2;
  uint32_t puVar3;
  uint uVar4;
  uint uVar5;
  uint local_10;
  uint uStack_c;
  
  puVar3 = 0xfebf9800u;
  uVar5 = 1;
  if (DAT_febf2aa1 == '\0') {
    if (length == 0) {
      bVar1 = true;
    }
    else {
      local_10 = address & 0xfffffe00;
      uVar4 = address & 0x1ff;
      uStack_c = uVar4 + length;
      for (iVar2 = 0; (int)(iVar2 - uVar4) < 0 != (iVar2 < 0 && -1 < (int)(iVar2 - uVar4));
          iVar2 = iVar2 + 1) {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebf1800u + (uint32_t)(iVar2) * 1u)))) = 0xff;
      }
      DAT_febf2998 = (undefined2)uVar4;
      bVar1 = false;
      DAT_febf299a = 0;
    }
    if ((!bVar1) &&
       (uVar4 = f33_boot_check_rounded_program_span_blank(local_10,uStack_c), uVar4 == 0)) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6e64))))) = 1;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-28000))))) = 1;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-27999))))) = 1;
      (*((uint *)camry_host_ptr((uint32_t)(puVar3 + -0x6e74)))) = local_10;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6e63))))) = 0;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6e62))))) = 0;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6e61))))) = 0;
      (*((uint *)camry_host_ptr((uint32_t)(puVar3 + -0x6e70)))) = uStack_c;
      uVar5 = 0;
    }
  }
  return uVar5;
}



/* Rejectbusy;40E0selectsfirst/lastblocks;3402selectscounterblock. Clearcoveredskipflags3506;
   setmode2,first/last/nextblock,counteraddress,result1,busy1;clearfinal/cancel/pause.0accepted/1rejected;
   no deviceoperation until4428. */

uint f33_boot_submit_block_erase(uint address,uint length)

{
  uint32_t puVar1;
  uint uVar2;
  uint uVar3;
  uint local_20;
  uint uStack_1c;
  uint uStack_18;
  uint uStack_14;
  
  puVar1 = 0xfebf9800u;
  uVar3 = 1;
  if (((DAT_febf2aa1 == '\0') &&
      (uVar2 = f33_boot_select_operation_blocks(address,length,&local_20,&uStack_1c), uVar2 == 0))
     && (uVar2 = f33_boot_select_counter_block_for_range(address,length,&uStack_14), uVar2 == 0)) {
    f33_boot_clear_flash_block_skip_flags(local_20,uStack_1c);
    (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x6e80)))) = local_20;
    (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x6e7c)))) = uStack_1c;
    f33_boot_find_flash_block_end(local_20,&uStack_18);
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-28000))))) = 1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-27999))))) = 1;
    (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x6e78)))) = uStack_18;
    uVar3 = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6e64))))) = 2;
    (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x6e6c)))) = uStack_14;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6e63))))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6e62))))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6e61))))) = 0;
  }
  return uVar3;
}



/* Storelow8 into299F. Any nonzero pauses4428 work, but finalcancel processing remains active. */

void f33_boot_set_flash_worker_pause(uchar paused)

{
  DAT_febf299f = paused;
  return;
}



/* Set299E=1; doesnot immediatelyclearbusy orchange result.4428 later consumes it evenwhenpaused. */

void f33_boot_request_flash_worker_cancel(void)

{
  DAT_febf299e = 1;
  return;
}



/* Append low16length bytes fromsource to1800 ring; wrapproducer at1100 andpublish2998 afterward. No
   owncapacitycheck orPMR. Caller42D8 admission protectsreservedslot. */

void f33_boot_append_program_input(uchar *source,ushort length)

{
  uchar uVar1;
  uint uVar2;
  uint uVar3;
  
  uVar3 = (uint)DAT_febf2998;
  for (; length != 0; length = length - 1) {
    uVar1 = *source;
    uVar2 = uVar3 + 1 & 0xffff;
    source = source + 1;
    if (0x10ff < uVar2) {
      uVar2 = 0;
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebf1800u + (uint32_t)(uVar3) * 1u)))) = uVar1;
    uVar3 = uVar2;
  }
  DAT_febf2998 = (short)uVar3;
  return;
}



/* Return signed(1100-occupancy < low16(requested_length)+1). Reserveoneslot; validcapacity4351. No
   enqueue orstatechange. */

uint f33_boot_program_input_has_insufficient_space(ushort requested_length)

{
  int iVar1;
  uint uVar2;
  
  uVar2 = f33_boot_program_input_occupancy();
  iVar1 = (0x1100 - uVar2) - (requested_length + 1);
  return (uint)(iVar1 < 0 != ((int)(0x1100 - uVar2) < 0 && -1 < iVar1));
}



/* Copylow16length bytes from1800 ring,wrapconsumerat1100,publish299Aaftercopy.
   Caller43BEchecksavailability; no localcapacitycheck. Native wrapped16-byte input is consumed in
   order and paddedFF; exact counter-block exclusion avoids driver dispatch. Other programming paths
   remain static. */

void f33_boot_consume_program_input(uchar *destination,ushort length)

{
  uchar *puVar1;
  uint uVar2;
  
  uVar2 = (uint)DAT_febf299a;
  for (; length != 0; length = length - 1) {
    puVar1 = ((undefined *)camry_host_ptr(0xfebf1800u)) + uVar2;
    uVar2 = uVar2 + 1 & 0xffff;
    *destination = *puVar1;
    destination = destination + 1;
    if (0x10ff < uVar2) {
      uVar2 = 0;
    }
  }
  DAT_febf299a = (short)uVar2;
  return;
}



/* Clearbusy,pause,cancel,finalmarker,ringproducer/consumer;setresult1.
   Doesnotclearcursor,remaining,counterblock orstaging; no lowerdevicecancel. */

void f33_boot_reset_flash_operation_queue(void)

{
  DAT_febf2aa1 = 0;
  DAT_febf299f = 0;
  DAT_febf299e = 0;
  DAT_febf299d = 0;
  DAT_febf2aa0 = 1;
  DAT_febf2998 = 0;
  DAT_febf299a = 0;
  return;
}



void FUN_00004744(undefined2 param_1,undefined4 param_2,undefined1 param_3)

{
  FUN_000046ee(0,param_1,param_2,param_3);
  return;
}



void FUN_0000475c(undefined2 param_1,undefined4 param_2,undefined1 param_3)

{
  FUN_000046ee(2,param_1,param_2,param_3);
  return;
}



bool FUN_00004776(void)

{
  bool bVar1;
  
  bVar1 = DAT_febf2aa3 != '\0';
  if (!bVar1) {
    DAT_febf2aa3 = '\x01';
    DAT_febf2aa2 = 2;
  }
  return bVar1;
}



undefined1 FUN_0000478e(void)

{
  return DAT_febf2aa2;
}



undefined1 FUN_00004794(void)

{
  return DAT_febf2aa3;
}



void FUN_0000479a(void)

{
  if (DAT_febf2aa3 != '\0') {
    DAT_febf2aa2 = 0;
    DAT_febf2aa3 = '\0';
  }
  return;
}



/* Paired constant publisher: DAT_febf2aa2 = 2; and DAT_febf2aa3 = 0;; shape-classified from the
   canonical corpus. Target cells not yet named. */

void FUN_000047ac(void)

{
  DAT_febf2aa2 = 2;
  DAT_febf2aa3 = 0;
  return;
}



/* If2AADnonzeroreturn1unchanged; otherwisequeueaddress/length/tag,setresult2,pending1,return0. No
   rangevalidationhere;4874 validatesselectedregion later. Noterase. */

uint f33_boot_submit_region_crc_verification(uint address,uint length,uchar opaque_tag)

{
  bool bVar1;
  
  bVar1 = DAT_febf2aad != '\0';
  if (!bVar1) {
    DAT_febf2aad = '\x01';
    DAT_febf2aac = 2;
    DAT_febf2aa4 = address;
    DAT_febf2aa8 = length;
    DAT_febf2aae = opaque_tag;
  }
  return (uint)bVar1;
}



/* Returnzero-extended2AAC result: initializer/admission2, worker0success/1failure. */

uint f33_boot_region_crc_result(void)

{
  return (uint)DAT_febf2aac;
}



/* Returnzero-extended2AAD pendingbyte; notCRCresult. */

uint f33_boot_region_crc_pending(void)

{
  return (uint)DAT_febf2aad;
}



uint FUN_000047ea(int param_1,uint param_2,uint param_3)

{
  int iVar1;
  uint uVar2;
  
  DCRA1CTL = '\0';
  uVar2 = 0;
  DCRA1COUT = param_3;
  while (uVar2 < param_2 >> 2) {
    iVar1 = uVar2 * 4;
    uVar2 = uVar2 + 1;
    DCRA1CIN = (*((uint *)camry_host_ptr((uint32_t)(iVar1 + param_1))));
  }
  uVar2 = DCRA1COUT;
  return ~uVar2;
}



/* SetCRCresult2 andpending0; retainaddress,length,opaque tag. Separatefrom47AC transition-job
   reset. */

void f33_boot_reset_region_crc_verification(void)

{
  DAT_febf2aac = 2;
  DAT_febf2aad = 0;
  return;
}



void FUN_000048d2(undefined1 *param_1,uint param_2)

{
  undefined2 uVar1;
  uint uVar2;
  
  for (uVar2 = (param_2 & 0xff) >> 1; uVar2 != 0; uVar2 = uVar2 - 1) {
    uVar1 = FUN_00001d24();
    *param_1 = (char)((ushort)uVar1 >> 8);
    param_1[1] = (char)uVar1;
    param_1 = param_1 + 2;
  }
  return;
}



void FUN_00004900(uchar param_1)

{
  f33_boot_negative_response('.',param_1);
  return;
}



/* Paired constant publisher: DAT_febf2ab2 = 0; and DAT_febf2ab1 = 0;; shape-classified from the
   canonical corpus. Target cells not yet named. */

void FUN_00004a90(void)

{
  DAT_febf2ab2 = 0;
  DAT_febf2ab1 = 0;
  return;
}



/* Waits2BFBjobcompletion;responds6Eor72afterrequestpendinglockclears. */

void f33_boot_write_did_progress(void)

{
  uint32_t puVar1;
  undefined4 uVar2;
  int iVar3;
  
  puVar1 = 0xfebf9800u;
  if (DAT_febf2ab1 != '\x01') {
    return;
  }
  if (f33_boot_response_pending_in_flight == '\x01') {
    return;
  }
  iVar3 = FUN_000067f6();
  if (iVar3 == 6) {
    uVar2 = 0x10;
  }
  else {
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6c05))))) != '\0') {
      return;
    }
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6c06))))) == '\0') {
      FUN_00004914();
      goto LAB_00004ada;
    }
    uVar2 = 0x72;
  }
  FUN_00004900(uVar2);
LAB_00004ada:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6d4f))))) = 0;
  return;
}



undefined4 FUN_00004ae2(void)

{
  uint32_t puVar1;
  undefined1 uVar2;
  undefined4 uVar3;
  
  puVar1 = 0xfebf9800u;
  if ((*((char *)camry_host_ptr((uint32_t)(DAT_febf2ab4 + 1)))) == (char)(DAT_febf2ac8 + '\x01')) {
    DAT_febf2ac7 = 0;
    uVar3 = 0;
  }
  else if ((DAT_febf2ac9 == '\x01') && ((*((char *)camry_host_ptr((uint32_t)(DAT_febf2ab4 + 1)))) == DAT_febf2ac8)) {
    puVar1 = 0xfebf9800u;
    uVar2 = FUN_00007262(DAT_febf2ac7);
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6d39))))) = uVar2;
    uVar3 = 1;
  }
  else {
    DAT_febf2ac7 = 0;
    uVar3 = 2;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6d37))))) = 1;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6d38))))) = (*((undefined1 *)camry_host_ptr((uint32_t)(*(int *)(puVar1 + -0x6d4c) + 1))));
  return uVar3;
}



void FUN_00004b38(uchar param_1)

{
  uint32_t puVar1;
  puVar1 = 0xfebf9800u;
  f33_boot_negative_response('6',param_1);
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6ced))))) != '\0') {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6ced))))) = 0xf;
  }
  return;
}



void FUN_00004b5a(void)

{
  DAT_febf2ad0 = 0x76;
  DAT_febf2ad1 = DAT_febf2ac8;
  f33_boot_response_submit('\x01',((undefined *)camry_host_ptr(0xfebf2ad0u)),2);
  return;
}



/* Use request length even in unsupported download state: wrong session gives7F; otherwise length<3
   gives13, else24. Reply through4B38; no input consumption. Static exact-image instruction/dataflow
   contract; no complete transfer execution claim. */

void f33_boot_reject_transfer_state(ushort request_length)

{
  undefined4 uVar1;
  
  if (f33_boot_diagnostic_session == f33_boot_service_session_constants[7]) {
    uVar1 = 0x24;
    if (request_length < 3) {
      uVar1 = 0x13;
    }
  }
  else {
    uVar1 = 0x7f;
  }
  FUN_00004b38(uVar1);
  return;
}



/* Resident SID36: preserve request length inr6; advance download1 to2 or9 to10, then call4B7C
   program/copy or4CA2 comparison. Payload is at most1024 bytes and full1024 except final; sequence
   mismatches73, duplicate sequence repeats76 without requeue. Actual ready data consumption occurs
   later in foreground4F50; timer4DF2/4E92 owns completion and positive76/sequence. */

void f33_boot_service_transfer_data(ushort request_length)

{
  uchar uVar1;
  
  uVar1 = '\x02';
  if ((f33_boot_download_state == '\x01') || (uVar1 = '\n', f33_boot_download_state == '\t')) {
    f33_boot_download_state = uVar1;
  }
  if (f33_boot_download_state == '\x02') {
    f33_boot_admit_program_transfer_chunk(request_length);
  }
  else if (f33_boot_download_state == '\n') {
    f33_boot_admit_compare_transfer_chunk(request_length);
  }
  else {
    f33_boot_reject_transfer_state(request_length);
  }
  return;
}



void FUN_00004df2(void)

{
  byte bVar1;
  undefined1 uVar2;
  uint32_t puVar3;
  undefined4 uVar4;
  int iVar5;
  uint uVar6;
  
  puVar3 = 0xfebf9800u;
  if (f33_boot_operation_region_class != '\x01' && f33_boot_operation_region_class != '\x02') {
    return;
  }
  iVar5 = FUN_000067f6();
  if (iVar5 == 6) {
    f33_boot_request_flash_worker_cancel();
    uVar4 = 0x10;
LAB_00004e84:
    FUN_00004b38(uVar4);
  }
  else {
    bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6d3a)))));
    if (bVar1 != 0) {
      if (bVar1 == 1) {
        if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6c22))))) != '\0') {
          return;
        }
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6d35))))) = 1;
        uVar2 = 2;
        goto LAB_00004e8a;
      }
      if (bVar1 < 3) {
        if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6d35))))) != '\0') {
          return;
        }
        if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6d36))))) == '\x02') {
          if ((*((int *)camry_host_ptr((uint32_t)(puVar3 + -0x6d44)))) == 0) {
            if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-27999))))) != '\0') {
              return;
            }
            if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-28000))))) != '\0') {
LAB_00004e5c:
              uVar4 = 0x72;
              goto LAB_00004e84;
            }
          }
          else {
            if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-27999))))) == '\0') goto LAB_00004e5c;
            uVar6 = f33_boot_program_input_has_insufficient_space(0x400);
            if (uVar6 != 0) {
              return;
            }
            f33_boot_set_flash_worker_pause('\x01');
          }
        }
        uVar2 = 3;
        goto LAB_00004e8a;
      }
      if (bVar1 == 3) {
        FUN_00004b5a();
      }
    }
  }
  uVar2 = 0;
LAB_00004e8a:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6d3a))))) = uVar2;
  return;
}



void FUN_00004e92(void)

{
  byte bVar1;
  undefined1 uVar2;
  uint32_t puVar3;
  undefined4 uVar4;
  int iVar5;
  uint uVar6;
  
  puVar3 = 0xfebf9800u;
  if (f33_boot_operation_region_class != '\x01' && f33_boot_operation_region_class != '\x02') {
    return;
  }
  iVar5 = FUN_000067f6();
  if (iVar5 == 6) {
LAB_00004f0a:
    uVar4 = 0x10;
LAB_00004f0e:
    FUN_00004b38(uVar4);
  }
  else {
    bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6d3a)))));
    if (bVar1 != 0) {
      if (bVar1 == 1) {
        if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6c22))))) != '\0') {
          return;
        }
        uVar6 = f33_boot_compare_submit
                          (*(uchar **)(puVar3 + -0x6d40),*(uchar **)(puVar3 + -0x6d48),
                           (uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x6d3c)))));
        if (uVar6 == 0) {
          uVar2 = 2;
          goto LAB_00004f14;
        }
        uVar4 = 0x72;
        goto LAB_00004f0e;
      }
      if (bVar1 < 3) {
        if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6c13))))) != '\0') {
          return;
        }
        (*((uint *)camry_host_ptr((uint32_t)(puVar3 + -0x6d44)))) =
             (*((int *)camry_host_ptr((uint32_t)(puVar3 + -0x6d44)))) - (uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x6d3c))));
        (*((uint *)camry_host_ptr((uint32_t)(puVar3 + -0x6d48)))) =
             (*((int *)camry_host_ptr((uint32_t)(puVar3 + -0x6d48)))) + (uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x6d3c))));
        if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6c14))))) == '\0') {
          uVar2 = 3;
          goto LAB_00004f14;
        }
        goto LAB_00004f0a;
      }
      if (bVar1 == 3) {
        FUN_00004b5a();
      }
    }
  }
  uVar2 = 0;
LAB_00004f14:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6d3a))))) = uVar2;
  return;
}



/* Downloadstate2\u21924DF2program/copy;10\u21924E92compare,otherwiseclearsactive.
   Downloadstate2→4DF2program/copy;10→4E92compare,otherwiseclearsactive. */

void f33_boot_transfer_timer_progress(void)

{
  if ((DAT_febf2ac6 != '\0') && (f33_boot_response_pending_in_flight != '\x01')) {
    if (f33_boot_download_state == '\x02') {
      FUN_00004df2();
    }
    else if (f33_boot_download_state == '\n') {
      FUN_00004e92();
    }
    else {
      DAT_febf2ac6 = '\0';
    }
  }
  return;
}



/* Readyqueuebridgeonlywhenoperationclass1/2;u16lenfrom2AC4,ringsource2AC0orRAMcopyto2AB8,clear2ACBandadvanceaddress.
    */

void f33_boot_transfer_foreground_consume(void)

{
  uint32_t puVar1;
  uint uVar2;
  
  puVar1 = 0xfebf9800u;
  if ((f33_boot_operation_region_class == '\x01' || f33_boot_operation_region_class == '\x02') &&
     (DAT_febf2acb == '\x01')) {
    uVar2 = (uint)DAT_febf2ac4;
    if (DAT_febf2aca == '\x02') {
      f33_boot_append_program_input(((uchar *)camry_host_ptr((uint32_t)(DAT_febf2ac0))), DAT_febf2ac4);
    }
    else {
      FUN_0000153a(((undefined1 *)camry_host_ptr((uint32_t)(DAT_febf2ac0))), ((undefined1 *)camry_host_ptr((uint32_t)(DAT_febf2ab8))), uVar2);
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6d35))))) = 0;
    (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x6d48)))) = (*((int *)camry_host_ptr((uint32_t)(puVar1 + -0x6d48)))) + uVar2;
  }
  return;
}



undefined4 FUN_00004f98(void)

{
  return DAT_febf2abc;
}



/* Constant-block fill: 7 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_4f9e(void)

{
  DAT_febf2ac6 = 0;
  DAT_febf2ac7 = 0;
  DAT_febf2ac8 = 0;
  DAT_febf2ab8 = DAT_febf2b00;
  DAT_febf2ac9 = 0;
  DAT_febf2acb = 0;
  DAT_febf2abc = DAT_febf2b04;
  return;
}



void FUN_00004fba(uchar param_1)

{
  f33_boot_negative_response('>',param_1);
  return;
}



void FUN_00004fce(void)

{
  DAT_febf2ad0 = 0x7e;
  DAT_febf2ad1 = DAT_febf2acc & 0x7f;
  f33_boot_response_submit(DAT_febf2acc >> 7 ^ 1,((undefined *)camry_host_ptr(0xfebf2ad0u)),2);
  return;
}



undefined1 FUN_00005060(char *param_1,char param_2,char param_3)

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



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_5084(void)

{
  return;
}



void FUN_00005086(void)

{
  f33_boot_diagnostic_session = '\x01';
  f33_boot_security_state = '\x01';
  f33_boot_download_state = '\0';
  DAT_febf2b10 = 0;
  DAT_febf2b11 = 0;
  DAT_febf2b12 = 0;
  DAT_febf2b14 = 2;
  DAT_febf2b15 = 0;
  DAT_febf2b16 = 0;
  f33_boot_operation_region_class = '\0';
  FUN_00006300();
  f33_return_only_stub_6134();
  f33_boot_security_initialize_handshake();
  f33_return_only_stub_68fa();
  f33_return_only_stub_699a();
  f33_return_only_stub_5084();
  f33_return_only_stub_6082();
  FUN_00004a90();
  FUN_00005c4a();
  f33_return_only_stub_5f3c();
  f33_fill_constant_block_4f9e();
  f33_return_only_stub_5d2a();
  return;
}



void FUN_000050ea(void)

{
  f33_boot_diagnostic_session = '\x02';
  f33_boot_download_state = '\0';
  DAT_febf2b10 = 0;
  DAT_febf2b11 = 0;
  DAT_febf2b12 = 0;
  DAT_febf2b14 = 2;
  DAT_febf2b15 = 0;
  DAT_febf2b16 = 0;
  f33_boot_operation_region_class = '\0';
  FUN_00006300();
  f33_return_only_stub_6134();
  f33_boot_security_initialize_handshake();
  f33_return_only_stub_68fa();
  f33_return_only_stub_699a();
  f33_return_only_stub_5084();
  f33_return_only_stub_6082();
  FUN_00004a90();
  FUN_00005c4a();
  f33_return_only_stub_5f3c();
  f33_fill_constant_block_4f9e();
  f33_return_only_stub_5d2a();
  return;
}



void FUN_00005148(void)

{
  FUN_0000630c();
  f33_boot_security_cancel_delay();
  return;
}



/* Single constant publisher: DAT_febf2b10 = 1; Shape-classified from the canonical corpus; the
   target cell is not yet named, so the written state's meaning is unknown. */

void FUN_00005158(void)

{
  DAT_febf2b10 = 1;
  return;
}



void FUN_0000519c(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebf9800u;
  FUN_00005160();
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6cef))))) = 0;
  return;
}



/* 6244session,5584securitydelay,4A9ADID,5C06routine,4F1Ctransferorderedtimerwork. */

void f33_boot_diagnostic_timer_progress(void)

{
  f33_boot_session_progress();
  f33_boot_security_delay_progress();
  f33_boot_write_did_progress();
  f33_boot_routine_timer_progress();
  f33_boot_transfer_timer_progress();
  return;
}



void FUN_000051c8(void)

{
  f33_boot_session_foreground_join();
  f33_boot_transfer_foreground_consume();
  return;
}



/* Forms7F,SID,NRC;mode0functionalelse2physical;submitslength3. Native functional routine rejection
   constructs7F3111 and passes suppression mode0; stops at674A before response processing. */

void f33_boot_negative_response(uchar sid,uchar nrc)

{
  uchar mode;
  
  DAT_febf2ad0 = 0x7f;
  if (f33_boot_address_mode == '\0') {
    mode = '\0';
  }
  else {
    mode = '\x02';
  }
  DAT_febf2ad1 = sid;
  DAT_febf2ad2 = nrc;
  f33_boot_response_submit(mode,((undefined *)camry_host_ptr(0xfebf2ad0u)),3);
  return;
}



bool FUN_0000526a(undefined4 param_1,undefined1 param_2,undefined1 param_3)

{
  int iVar1;
  
  iVar1 = FUN_00005060(((char *)camry_host_ptr((uint32_t)(param_1))), param_2, param_3);
  return iVar1 == 0;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_5280(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_5282(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_5284(void)

{
  return;
}



void FUN_00005286(uint param_1)

{
  uchar local_8 [4];
  
  local_8[0] = 'Z';
  local_8[1] = 0xa5;
  local_8[2] = 0xa5;
  local_8[3] = 'Z';
  f33_boot_submit_program_stream(param_1,4);
  f33_boot_append_program_input(local_8,4);
  return;
}



int FUN_000052a6(byte *param_1,uint param_2)

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



bool FUN_000052be(void)

{
  return DAT_febf2b12 != '\x01';
}



void FUN_000052ca(uchar param_1)

{
  f33_boot_negative_response('\'',param_1);
  return;
}



void FUN_000052de(void)

{
  int iVar1;
  int iVar2;
  uchar uVar3;
  int iVar4;
  ushort length;
  
  uVar3 = f33_boot_security_request_subfunction;
  DAT_febf2ad0 = 0x67;
  DAT_febf2ad1 = f33_boot_security_request_subfunction;
  if ((f33_boot_security_request_subfunction & 1) == 0) {
    length = 2;
  }
  else {
    length = 0x12;
    iVar4 = 0;
    do {
      iVar2 = iVar4 + 1;
      iVar1 = iVar4 + -0xf;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebf2ad2u + (uint32_t)(iVar4) * 1u)))) = f33_boot_security_response_challenge[iVar4];
      iVar4 = iVar2;
    } while (((iVar1 < 0) || (iVar2 < 0)));
  }
  f33_boot_response_submit(uVar3 >> 7 ^ 1,((undefined *)camry_host_ptr(0xfebf2ad0u)),length);
  return;
}



/* Only handshake2 checks exact18-byte request and derives expected16 bytes at currentSP
   using704C(client2B34,challenge2B24,SP). Compare is early-exit bytewise, not constant-time. Valid
   key 
   storessecurity2,clearsfailurecountandchallenge,forms6702,pendinghandshake3inr29;2B55=3onlyafter52DE/674Areturns.
   First mismatch increments shared failed count and35,pendingstate1; second mismatch or second
   malformed-length attempt captures raw counter
   andstarts200000000delay,clearscount/challenge,gives36,pendingstate1. First malformed length13
   also counts. States1/3reject24;state0/>3silentlynormalizes1.No explicit delay gate in key path.
   Native AES known-answer and protocol-state cases use explicit RAM. Service paths stop at674A
   before response/timer completion; direct session invalidation cases return. No complete unlock or
   entropy claim. */

void f33_boot_security_key_request(ushort request_length)

{
  int iVar1;
  int iVar2;
  int iVar3;
  undefined *puVar4;
  undefined *puVar5;
  undefined4 uVar6;
  int iVar7;
  uchar uVar8;
  uchar local_18 [16];
  
  puVar5 = ((undefined *)camry_host_ptr(0xfebf9800u));
  puVar4 = ((undefined *)camry_host_ptr(0xfebf9800u));
  if (f33_boot_security_handshake_state == '\0') {
LAB_0000550c:
    uVar8 = '\x01';
  }
  else {
    if (f33_boot_security_handshake_state == '\x01') {
LAB_00005506:
      uVar6 = 0x24;
      uVar8 = f33_boot_security_handshake_state;
      puVar4 = ((undefined *)camry_host_ptr(0xfebf9800u));
    }
    else {
      if (3 < f33_boot_security_handshake_state) goto LAB_0000550c;
      if (2 < f33_boot_security_handshake_state) goto LAB_00005506;
      if (request_length == 0x12) {
        puVar4 = ((undefined *)camry_host_ptr(0xfebf9800u));
        f33_boot_security_derive_expected_key
                  (f33_boot_security_client_material,f33_boot_security_challenge,local_18);
        iVar3 = 0;
LAB_0000546e:
        iVar7 = *(int *)(puVar4 + -0x6ce8);
        if (local_18[iVar3] == (*((uchar *)camry_host_ptr((uint32_t)(iVar3 + iVar7 + 2))))) goto code_r0x00005484;
        if (-1 < (int)((byte)puVar4[-0x6ca9] - 1)) {
          puVar5 = puVar4;
          uVar6 = FUN_00001d24();
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
      if ((int)(f33_boot_security_failed_attempts - 1) < 0) {
        uVar6 = 0x13;
        uVar8 = '\x01';
        puVar4 = ((undefined *)camry_host_ptr(0xfebf9800u));
        f33_boot_security_failed_attempts = f33_boot_security_failed_attempts + '\x01';
      }
      else {
        uVar6 = FUN_00001d24();
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
    FUN_000052ca(uVar6);
  }
LAB_0000550e:
  puVar4[-0x6cab] = uVar8;
  return;
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
  FUN_000052de();
  goto LAB_0000550e;
}



/* Onlydelayflag1:unsigned32elapsed=(timer-start),cleardelayonlyelapsed>duration(strict);doesnotresetfailures,handshake,security,buffers.Timer51ACownsperiodiccall;noexplicitseconds.
    */

void f33_boot_security_delay_progress(void)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebf9800u;
  if ((f33_boot_security_delay_active == '\x01') &&
     (iVar2 = FUN_00001d24(),
     (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x6ce4)))) < (uint)(iVar2 - (*((int *)camry_host_ptr((uint32_t)(puVar1 + -0x6ce0))))))) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6caa))))) = 0;
  }
  return;
}



/* Calledbyprioritymasked51D8sessionpublication.Ifhandshake1:securityunchanged;handshake2:clear16challengebyteswithoutwritingsecurity;otherstates(includingaccepted3):security1.Thenhandshake1.Retainsclient,responsecache,failcount,delay/history.
   Native AES known-answer and protocol-state cases use explicit RAM. Service paths stop at674A
   before response/timer completion; direct session invalidation cases return. No complete unlock or
   entropy claim. */

void f33_boot_security_invalidate_handshake(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  if (f33_boot_security_handshake_state != '\x01') {
    if (f33_boot_security_handshake_state == '\x02') {
      iVar3 = 0;
      do {
        f33_boot_security_challenge[iVar3] = '\0';
        iVar2 = iVar3 + 1;
        iVar1 = iVar3 + -0xf;
        iVar3 = iVar2;
      } while (((iVar1 < 0) || (iVar2 < 0)));
    }
    else {
      f33_boot_security_state = '\x01';
    }
  }
  f33_boot_security_handshake_state = '\x01';
  return;
}



/* Onlyclearactive-delayflag.5148callsonapplicationhandoffreplaypath6504;doesnotresetfailurecountorhandshakeorclient/challenge.
    */

void f33_boot_security_cancel_delay(void)

{
  f33_boot_security_delay_active = '\0';
  return;
}



void FUN_00005630(uchar param_1)

{
  f33_boot_negative_response('1',param_1);
  return;
}



void FUN_00005644(void)

{
  DAT_febf2ad0 = 0x71;
  DAT_febf2ad1 = DAT_febf2b66 & 0x7f;
  DAT_febf2ad2 = (undefined1)((ushort)DAT_febf2b64 >> 8);
  DAT_febf2ad3 = (undefined1)DAT_febf2b64;
  f33_boot_response_submit(DAT_febf2b66 >> 7 ^ 1,((undefined *)camry_host_ptr(0xfebf2ad0u)),DAT_febf2b67 + 4);
  return;
}



void FUN_00005936(void)

{
  char cVar1;
  undefined1 uVar2;
  uint32_t puVar3;
  undefined4 uVar4;
  int iVar5;
  uint uVar6;
  
  puVar3 = 0xfebf9800u;
  iVar5 = FUN_000067f6();
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
          return;
        }
        if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6c04))))) == '\0') {
          uVar2 = 4;
        }
        else {
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6ce9))))) = 0;
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6cef))))) = 0;
          FUN_00005630(0x72);
          uVar2 = 0;
        }
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6c97))))) = uVar2;
        f33_boot_region_authentication_clear_contexts();
        return;
      }
      if (cVar1 == '\x04') {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6ce9))))) = 0;
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6cef))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6cef))))) | (byte)(1 << ((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6c98))))) & 0x1f));
        FUN_00005644();
      }
      goto LAB_000059fc;
    }
    uVar6 = f33_boot_region_crc_pending();
    if (uVar6 != 0) {
      return;
    }
    uVar6 = f33_boot_region_crc_result();
    if (uVar6 == 0) {
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6ceb))))) == '\0') {
        uVar2 = 4;
LAB_00005986:
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6c97))))) = uVar2;
        return;
      }
      f33_boot_authentication_crypto_initialize();
      uVar6 = f33_boot_region_authentication_submit
                        ((*((uint *)camry_host_ptr((uint32_t)(puVar3 + -0x6ca8)))),(*((uint *)camry_host_ptr((uint32_t)(puVar3 + -0x6ca4)))));
      if (uVar6 == 0) {
        uVar2 = 2;
        goto LAB_00005986;
      }
      f33_boot_region_authentication_clear_contexts();
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6ce9))))) = 0;
    uVar4 = 0x72;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6cef))))) = 0;
  }
  FUN_00005630(uVar4);
LAB_000059fc:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6c97))))) = 0;
  return;
}



void FUN_00005a04(void)

{
  undefined1 uVar1;
  byte bVar2;
  uint32_t puVar3;
  undefined4 uVar4;
  int iVar5;
  uint uVar6;
  uint local_8;
  
  puVar3 = 0xfebf9800u;
  if (f33_boot_operation_region_class != '\x02') {
    return;
  }
  iVar5 = FUN_000067f6();
  if (iVar5 == 6) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6c96))))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6ce9))))) = 0;
    f33_boot_request_flash_worker_cancel();
    uVar4 = 0x10;
  }
  else {
    switch((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6c97)))))) {
    case 1:
      uVar6 = f33_boot_region_crc_pending();
      if (uVar6 != 0) {
        return;
      }
      uVar6 = f33_boot_region_crc_result();
      if (uVar6 == 0) {
        if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6ceb))))) == '\0') {
          bVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6c96))))) | (byte)(1 << ((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6c98))))) & 0x1f));
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6c96))))) = bVar2;
          if ((bVar2 == 1) &&
             (uVar6 = f33_boot_lookup_completion_marker
                                ((*((uint *)camry_host_ptr((uint32_t)(puVar3 + -0x6ca8)))),(*((uint *)camry_host_ptr((uint32_t)(puVar3 + -0x6ca4)))),&local_8),
             uVar6 == 0)) {
            FUN_00005286(local_8);
            uVar1 = 3;
          }
          else {
            uVar1 = 4;
          }
LAB_00005a62:
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6c97))))) = uVar1;
          return;
        }
        f33_boot_authentication_crypto_initialize();
        uVar6 = f33_boot_region_authentication_submit
                          ((*((uint *)camry_host_ptr((uint32_t)(puVar3 + -0x6ca8)))),(*((uint *)camry_host_ptr((uint32_t)(puVar3 + -0x6ca4)))));
        if (uVar6 == 0) {
          uVar1 = 2;
          goto LAB_00005a62;
        }
        f33_boot_region_authentication_clear_contexts();
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
           (uVar6 = f33_boot_lookup_completion_marker
                              ((*((uint *)camry_host_ptr((uint32_t)(puVar3 + -0x6ca8)))),(*((uint *)camry_host_ptr((uint32_t)(puVar3 + -0x6ca4)))),&local_8),
           uVar6 == 0)) {
          FUN_00005286(local_8);
          uVar1 = 3;
        }
        else {
          uVar1 = 4;
        }
      }
      else {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6c96))))) = 0;
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6ce9))))) = 0;
        FUN_00005630(0x72);
        uVar1 = 0;
      }
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6c97))))) = uVar1;
      f33_boot_region_authentication_clear_contexts();
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
      f33_boot_request_flash_worker_cancel();
      break;
    case 4:
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6ce9))))) = 0;
      FUN_00005644();
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
  FUN_00005630(uVar4);
switchD_00005a28_default:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6c97))))) = 0;
  return;
}



void FUN_00005b70(void)

{
  uint32_t puVar1;
  undefined4 uVar2;
  int iVar3;
  
  puVar1 = 0xfebf9800u;
  if (f33_boot_operation_region_class != '\x02') {
    return;
  }
  iVar3 = FUN_000067f6();
  if (iVar3 == 6) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6cee))))) = 0;
    f33_boot_request_flash_worker_cancel();
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6ce9))))) = 0;
    uVar2 = 0x10;
  }
  else {
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6c97))))) != '\x01') {
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6c97))))) == '\x04') {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6ce9))))) = 0;
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6cee))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6cee))))) | (byte)(1 << ((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6c98))))) & 0x1f));
        FUN_00005644();
      }
      goto LAB_00005bfe;
    }
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-27999))))) != '\0') {
      iVar3 = FUN_000067f6();
      if (iVar3 != 5) {
        return;
      }
      f33_boot_set_flash_worker_pause('\0');
      return;
    }
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-28000))))) == '\0') {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6c97))))) = 4;
      return;
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6cee))))) = 0;
    f33_boot_request_flash_worker_cancel();
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6ce9))))) = 0;
    uVar2 = 0x72;
  }
  FUN_00005630(uVar2);
LAB_00005bfe:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6c97))))) = 0;
  return;
}



/* ExplicitRIDdispatch10F0/10F1\u21925936,10F2\u21925A04,FF00\u21925B70;noROMcallbackcallthroughFFFFFFFF.
   ExplicitRIDdispatch10F0/10F1→5936,10F2→5A04,FF00→5B70;noROMcallbackcallthroughFFFFFFFF. */

void f33_boot_routine_timer_progress(void)

{
  undefined *puVar1;
  
  if ((DAT_febf2b69 != '\0') && (f33_boot_response_pending_in_flight != '\x01')) {
    puVar1 = ((undefined *)camry_host_ptr((uint32_t)(DAT_febf2b64 - 0x10f0)));
    if (puVar1 < ((undefined *)camry_host_ptr((uint32_t)(0x2)))) {
      FUN_00005936();
    }
    else if (puVar1 == ((undefined *)camry_host_ptr((uint32_t)(0x2)))) {
      FUN_00005a04();
    }
    else if (puVar1 == ((undefined *)camry_host_ptr(0xee10u))) {
      FUN_00005b70();
    }
    else {
      DAT_febf2b69 = '\0';
    }
  }
  return;
}



/* Paired constant publisher: DAT_febf2b69 = 0; and DAT_febf2b6a = 0;; shape-classified from the
   canonical corpus. Target cells not yet named. */

void FUN_00005c4a(void)

{
  DAT_febf2b69 = 0;
  DAT_febf2b6a = 0;
  return;
}



void FUN_00005c54(uchar param_1)

{
  uint32_t puVar1;
  puVar1 = 0xfebf9800u;
  f33_boot_negative_response('7',param_1);
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6ced))))) != '\0') {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6ced))))) = 0xf;
  }
  return;
}



void FUN_00005c76(void)

{
  DAT_febf2ad0 = 0x77;
  f33_boot_response_submit('\x01',((undefined *)camry_host_ptr(0xfebf2ad0u)),1);
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_5d2a(void)

{
  return;
}



void FUN_00005d2c(uchar param_1)

{
  f33_boot_negative_response('4',param_1);
  return;
}



/* Forms74 20 04 02andpasseslength4inr8to674A;repairmisrenderedmissinglength. */

void f33_boot_download_positive_response(void)

{
  DAT_febf2ad0 = 0x74;
  DAT_febf2ad2 = 4;
  DAT_febf2ad1 = 0x20;
  DAT_febf2ad3 = 2;
  f33_boot_response_submit('\x01',((undefined *)camry_host_ptr(0xfebf2ad0u)),4);
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_5f3c(void)

{
  return;
}



void FUN_00005f68(uchar param_1)

{
  f33_boot_negative_response('\"',param_1);
  return;
}



void FUN_00005f7c(void)

{
  uint uVar1;
  
  DAT_febf2ad0 = 0x62;
  for (uVar1 = 0; uVar1 < DAT_febf2b6c; uVar1 = uVar1 + 1 & 0xffff) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebf2ad1u + (uint32_t)(uVar1) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebf2b6eu + (uint32_t)(uVar1) * 1u))));
  }
  f33_boot_response_submit('\x01',((undefined *)camry_host_ptr(0xfebf2ad0u)),DAT_febf2b6c + 1);
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_6082(void)

{
  return;
}



void FUN_00006084(uchar param_1)

{
  f33_boot_negative_response('\x11',param_1);
  return;
}



void FUN_00006098(void)

{
  DAT_febf2ad0 = 0x51;
  DAT_febf2ad1 = DAT_febf2b9e & 0x7f;
  f33_boot_response_submit(DAT_febf2b9e >> 7 ^ 1,((undefined *)camry_host_ptr(0xfebf2ad0u)),2);
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_6134(void)

{
  return;
}



void FUN_00006136(uchar param_1)

{
  f33_boot_negative_response('\x10',param_1);
  return;
}



/* Resident SID10: require length2 and masked subfunction1/2/3; reject target2 from session1 or
   target3 from session2 with7E. Stage requested session in2B9F/2BA0 and deferred state2BA3;
   programming entry queues4776 or foreground flag2BA2.6244 publishes the session only after the
   foreground join, then responds50/subfunction/00 32 01 F4. Native session3 request10 02 queues
   deferred transition; session/security publication remains unchanged. */

void f33_boot_service_session_control(ushort request_length)

{
  uint32_t puVar1;
  undefined4 uVar2;
  int iVar3;
  byte bVar4;
  bool bVar5;
  undefined1 uStack_e;
  byte bStack_d;
  
  puVar1 = 0xfebf9800u;
  uStack_e = 0;
  bStack_d = 0;
  FUN_000067b0(&uStack_e,2);
  bVar4 = bStack_d & 0x7f;
  if (1 < request_length) {
    if (((bVar4 != 1) && (bVar4 != 2)) && (bVar4 != 3)) {
      uVar2 = 0x12;
      goto LAB_0000617e;
    }
    if (bVar4 == 2) {
      bVar5 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6cf2))))) == '\x01';
LAB_0000619c:
      if (bVar5) {
        uVar2 = 0x7e;
        goto LAB_0000617e;
      }
    }
    else if (bVar4 == 3) {
      bVar5 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6cf2))))) == '\x02';
      goto LAB_0000619c;
    }
    if (request_length == 2) {
      if ((bStack_d & 0x7f) == 0) {
        return;
      }
      if (bVar4 != 1) {
        if (3 < bVar4) {
          return;
        }
        if (bVar4 < 3) {
          if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6c5f))))) == '\0') {
            iVar3 = FUN_00004776();
            if (iVar3 != 0) {
              FUN_00006136(0x22);
              (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6c5d))))) = 0;
              return;
            }
            (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6c60))))) = bVar4;
            (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6c61))))) = bStack_d;
            (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6c5d))))) = 1;
            return;
          }
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6c5f))))) = 0;
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6c5e))))) = 1;
        }
      }
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6c60))))) = bVar4;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6c61))))) = bStack_d;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6c5d))))) = 2;
      return;
    }
  }
  uVar2 = 0x13;
LAB_0000617e:
  FUN_00006136(uVar2);
  return;
}



void FUN_00006204(void)

{
  DAT_febf2ad0 = 0x50;
  DAT_febf2ad1 = (undefined1)(DAT_febf2b9f & 0x7f);
  if ((DAT_febf2b9f & 0x7f) - 1 < 3) {
    DAT_febf2ad2 = 0;
    DAT_febf2ad3 = 0x32;
    DAT_febf2ad4 = 1;
    DAT_febf2ad5 = 0xf4;
  }
  f33_boot_response_submit(DAT_febf2b9f >> 7 ^ 1,((undefined *)camry_host_ptr(0xfebf2ad0u)),6);
  return;
}



/* Timer-contextdeferredsessiontransition;waits4794/478Ethenforeground62DCflagbeforepublication/positive50.
    */

void f33_boot_session_progress(void)

{
  byte bVar1;
  undefined1 uVar2;
  uint32_t puVar3;
  uchar session;
  undefined4 uVar4;
  int iVar5;
  
  puVar3 = 0xfebf9800u;
  if (DAT_febf2ba3 == '\0') {
    return;
  }
  if (f33_boot_response_pending_in_flight == '\x01') {
    return;
  }
  iVar5 = FUN_000067f6();
  if (iVar5 == 6) {
    uVar4 = 0x10;
LAB_000062ce:
    FUN_00006136(uVar4);
  }
  else {
    bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6c60)))));
    if (bVar1 != 0) {
      if (bVar1 == 1) {
        if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6c5d))))) == '\x02') {
          session = '\x01';
LAB_000062c0:
          f33_boot_session_publish(session);
          FUN_00006204();
        }
      }
      else if (bVar1 < 3) {
        if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6c5d))))) == '\x01') {
          iVar5 = FUN_00004794();
          if (iVar5 != 0) {
            return;
          }
          iVar5 = FUN_0000478e();
          if (iVar5 == 0) {
            (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6c5e))))) = 1;
            uVar2 = 2;
            goto LAB_000062d4;
          }
          uVar4 = 0x22;
          goto LAB_000062ce;
        }
        if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6c5d))))) == '\x02') {
          if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6c5e))))) != '\0') {
            return;
          }
          session = '\x02';
          goto LAB_000062c0;
        }
      }
      else if ((bVar1 == 3) && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6c5d))))) == '\x02')) {
        session = '\x03';
        goto LAB_000062c0;
      }
    }
  }
  uVar2 = 0;
LAB_000062d4:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6c5d))))) = uVar2;
  return;
}



/* Consumes2BA2flag;preparesdriveronlyif2BD1!=1,thenalwaysclearsflag. */

void f33_boot_session_foreground_join(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebf9800u;
  if (DAT_febf2ba2 == '\x01') {
    if (DAT_febf2bd1 == '\0') {
      puVar1 = 0xfebf9800u;
      f33_boot_programming_prepare();
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6c5e))))) = 0;
  }
  return;
}



void FUN_00006300(void)

{
  DAT_febf2ba1 = 0;
  DAT_febf2ba2 = 0;
  DAT_febf2ba3 = 0;
  return;
}



void FUN_0000630c(void)

{
  DAT_febf2ba1 = 1;
  f33_boot_session_publish('\x03');
  return;
}



void FUN_00006320(void)

{
  uint32_t puVar1;
  undefined4 uVar2;
  
  puVar1 = 0xfebf9800u;
  f33_boot_request_append_index = 0;
  f33_boot_request_length = 0;
  f33_boot_response_remaining = 0;
  f33_boot_request_state = '\0';
  f33_boot_response_state = '\0';
  f33_boot_response_pending_in_flight = '\0';
  uVar2 = FUN_00001d24();
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x6c4c)))) = uVar2;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6c43))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6c41))))) = 0;
  return;
}



void FUN_0000636e(void)

{
  f33_boot_request_append_index = 0;
  return;
}



void FUN_00006588(void)

{
  DAT_febf2bbe = 0;
  f33_boot_request_append_index = f33_boot_request_length;
  f33_boot_request_state = '\x01';
  f33_boot_request_receive_complete(0,'\0');
  return;
}



/* Executingrequests\u219265AA;idlesession2/3rawelapsedtimeoutpublishesdefault1.
   Executingrequests→65AA;idlesession2/3rawelapsedtimeoutpublishesdefault1. */

void f33_boot_diagnostic_timeout_progress(void)

{
  uint32_t puVar1;
  int iVar2;
  undefined4 uVar3;
  uint uVar4;
  
  puVar1 = 0xfebf9800u;
  if (f33_boot_request_state == '\x02') {
    f33_boot_response_timer_progress();
  }
  else if ((f33_boot_request_state == '\0') && (DAT_febf2bbf != '\x01')) {
    iVar2 = FUN_00001d24();
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6cf2))))) == '\x02' || (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6cf2))))) == '\x03') {
      uVar4 = 100000000;
    }
    else {
      uVar4 = 0xffffffff;
    }
    if (uVar4 < (uint)(iVar2 - (*((int *)camry_host_ptr((uint32_t)(puVar1 + -0x6c4c)))))) {
      f33_boot_session_publish('\x01');
      uVar3 = FUN_00001d24();
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x6c4c)))) = uVar3;
    }
  }
  return;
}



undefined1 * FUN_000067d0(void)

{
  f33_boot_request_append_index = 0;
  return ((undefined *)camry_host_ptr(0xfebf30c0u));
}



void FUN_000067da(void)

{
  if (f33_boot_request_state == '\0') {
    FUN_0000159e();
  }
  else {
    f33_boot_terminal_after_response = '\x01';
  }
  return;
}



void FUN_0000684c(uchar param_1)

{
  f33_boot_negative_response('(',param_1);
  return;
}



void FUN_00006860(void)

{
  DAT_febf2ad0 = 0x68;
  DAT_febf2ad1 = DAT_febf2bc3 & 0x7f;
  f33_boot_response_submit(DAT_febf2bc3 >> 7 ^ 1,((undefined *)camry_host_ptr(0xfebf2ad0u)),2);
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_68fa(void)

{
  return;
}



void FUN_000068fc(uchar param_1)

{
  f33_boot_negative_response(0x85,param_1);
  return;
}



void FUN_00006910(void)

{
  DAT_febf2ad0 = 0xc5;
  DAT_febf2ad1 = DAT_febf2bc4 & 0x7f;
  f33_boot_response_submit(DAT_febf2bc4 >> 7 ^ 1,((undefined *)camry_host_ptr(0xfebf2ad0u)),2);
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_699a(void)

{
  return;
}



void FUN_0000699c(uchar param_1)

{
  f33_boot_negative_response(DAT_febf2bc5,param_1);
  return;
}



/* Sharedconfiguredcallbackfor23/2C/14/19/2F/AB/BA/BB;readsSIDfromrequestbyte0andreturnsNRC7F.Doesnotimplementthoseservices.
    */

void f33_boot_service_reject_configured(ushort request_length)

{
  uint32_t puVar1;
  undefined1 uStack_5;
  
  puVar1 = 0xfebf9800u;
  FUN_000067b0(&uStack_5,1);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6c3b))))) = uStack_5;
  FUN_0000699c(0x7f);
  return;
}



/* Enabledtimer666Cthen51AC;doesnotcallhardwareforeground4428. */

void f33_boot_diagnostic_timer_services(void)

{
  if (DAT_febf2bd0 != '\0') {
    f33_boot_diagnostic_timeout_progress();
    f33_boot_diagnostic_timer_progress();
  }
  return;
}



/* Clears2BD2,152Adriverprepare/519Cformatinitialize,thenpublishes2BD1=1. */

void f33_boot_programming_prepare(void)

{
  DAT_febf2bd2 = 0;
  FUN_0000152a();
  FUN_0000519c();
  DAT_febf2bd1 = 1;
  return;
}



/* Far-call trampoline: prepare {lp},0 / jarl 0x5158 / dispose 0,{lp},lp; byte-verified against the
   exact image. Forwards with registers and stack unchanged; marked as a thunk. Forwarding shape
   machine-verified; target semantics not recovered. */

void thunk_FUN_00005158(void)

{
  FUN_00005158();
  return;
}



/* Enabledgateveneerpreservesr9fourthargumentto6374;returns1whendisabled. */

uint f33_boot_transport_request_admit
               (ushort channel,F33BootPduInfo *first_chunk,ushort total_length,
               ushort *remaining_capacity)

{
  uint uVar1;
  
  if (DAT_febf2bd0 == '\0') {
    uVar1 = 1;
  }
  else {
    uVar1 = f33_boot_request_admit(channel,first_chunk,total_length,remaining_capacity);
  }
  return uVar1;
}



/* Registerpreserving6464veneer;notvoidone-argumentCfunction. */

uint f33_boot_transport_request_append
               (ushort channel,F33BootPduInfo *chunk,ushort *remaining_capacity)

{
  uint uVar1;
  
  uVar1 = f33_boot_request_append(channel,chunk,remaining_capacity);
  return uVar1;
}



/* Correcttypedveneerfor64B8completion. */

void f33_boot_transport_receive_complete(ushort channel,uchar status)

{
  f33_boot_request_receive_complete(channel,status);
  return;
}



/* Realresponsechunkcallbackveneerforwardingr7/r8/r9;notvoidone-argument. */

uint f33_boot_transport_response_copy
               (ushort channel,F33BootPduInfo *chunk,uint unused,ushort *remaining)

{
  uint uVar1;
  
  uVar1 = f33_boot_response_copy_chunk(channel,chunk,unused,remaining);
  return uVar1;
}



/* Responsecompletionveneerfor66BE;notreceivecompletion64B8. */

void f33_boot_transport_response_complete(ushort channel,uchar status)

{
  f33_boot_response_complete(channel,status);
  return;
}



/* SID34 optional-transform setup forwards70D4; derives image key and resets BOTH CBC/CMAC contexts.
    */

void f33_boot_transfer_crypto_initialize(void)

{
  f33_boot_image_crypto_initialize();
  return;
}



/* TransferExit optional-transform cleanup forwards70FC; wipes BOTH CBC and CMAC, not worker
   activity/pointers or configured materials. */

void f33_boot_transfer_crypto_clear(void)

{
  f33_boot_image_crypto_clear();
  return;
}



/* Refine existing owner: CBC decrypt at most one full16-byte block via7108 into stack-local then
   copy back; preserve originalciphertext chain for in-place job. Ignore crypto failure and copy
   local regardless. Tail1..15 deducted without decrypt/copy or pointer advancement; active clears
   atremaining0. */

void f33_boot_transfer_block_transform_progress(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  undefined *puVar4;
  undefined8 uVar5;
  int iVar6;
  uint uVar7;
  uchar local_1c [16];
  
  uVar5 = 0xfebf9800;
  puVar4 = ((undefined *)camry_host_ptr(0xfebf9800u));
  if (DAT_febf2bde != '\0') {
    uVar7 = (uint)DAT_febf2bdc;
    if (0xf < uVar7) {
      uVar7 = 0x10;
    }
    for (iVar6 = (int)uVar7 >> 4; iVar6 != 0; iVar6 = iVar6 + -1) {
      f33_boot_image_decrypt_block(*(uchar **)((int)uVar5 + -0x6c2c),local_1c);
      puVar4 = ((undefined *)camry_host_ptr((uint32_t)(uVar5)));
      *(int *)(puVar4 + -0x6c2c) = *(int *)(puVar4 + -0x6c2c) + 0x10;
      iVar3 = 0;
      do {
        iVar2 = iVar3 + 1;
        **(uchar **)(puVar4 + -0x6c28) = local_1c[iVar3];
        iVar1 = iVar3 + -0xf;
        *(int *)(puVar4 + -0x6c28) = *(int *)(puVar4 + -0x6c28) + 1;
        iVar3 = iVar2;
      } while (((iVar1 < 0) || (iVar2 < 0)));
    }
    uVar7 = *(ushort *)(puVar4 + -0x6c24) - uVar7;
    *(ushort *)(puVar4 + -0x6c24) = (ushort)uVar7;
    if ((uVar7 & 0xffff) == 0) {
      puVar4[-0x6c22] = 0;
    }
  }
  return;
}



/* Clear2BDE active only; retain transform remaining/source/destination and all crypto contexts.
   Resident initialization6A22 uses this, not a secure erase. */

void f33_boot_block_transform_clear_activity(void)

{
  DAT_febf2bde = 0;
  return;
}



bool FUN_00006c5a(int *param_1)

{
  return *param_1 != 0x5aa5a55a;
}



/* Paired constant publisher: DAT_febf2bec = 1; and DAT_febf2bed = 0;; shape-classified from the
   canonical corpus. Target cells not yet named. */

void FUN_00006d02(void)

{
  DAT_febf2bec = 1;
  DAT_febf2bed = 0;
  return;
}



uint FUN_00006d10(uint *param_1,uchar *param_2)

{
  uint uVar1;
  
  uVar1 = f33_boot_submit_program_stream(*param_1,(uint)(ushort)param_1[1]);
  if (uVar1 == 0) {
    f33_boot_append_program_input(param_2,(ushort)param_1[1]);
  }
  return uVar1;
}



undefined4 FUN_00006d3a(int *param_1,int param_2)

{
  int iVar1;
  int iVar2;
  
  iVar2 = *param_1;
  for (iVar1 = 0;
      (int)(iVar1 - (uint)*(ushort *)(param_1 + 1)) < 0 !=
      (iVar1 < 0 && -1 < (int)(iVar1 - (uint)*(ushort *)(param_1 + 1))); iVar1 = iVar1 + 1) {
    (*((undefined1 *)camry_host_ptr((uint32_t)(iVar1 + iVar2)))) = (*((undefined1 *)camry_host_ptr((uint32_t)(iVar1 + param_2))));
  }
  return 0;
}



undefined4 FUN_00006dc0(int *param_1,int param_2)

{
  int iVar1;
  int iVar2;
  
  iVar2 = *param_1;
  for (iVar1 = 0;
      (int)(iVar1 - (uint)*(ushort *)(param_1 + 1)) < 0 !=
      (iVar1 < 0 && -1 < (int)(iVar1 - (uint)*(ushort *)(param_1 + 1))); iVar1 = iVar1 + 1) {
    (*((undefined1 *)camry_host_ptr((uint32_t)(iVar1 + param_2)))) = (*((undefined1 *)camry_host_ptr((uint32_t)(iVar1 + iVar2))));
  }
  return 0;
}



undefined4 FUN_00006de4(int *param_1,int param_2)

{
  int iVar1;
  int iVar2;
  
  iVar2 = *param_1;
  for (iVar1 = 0;
      (int)(iVar1 - (uint)*(ushort *)(param_1 + 1)) < 0 !=
      (iVar1 < 0 && -1 < (int)(iVar1 - (uint)*(ushort *)(param_1 + 1))); iVar1 = iVar1 + 1) {
    (*((undefined1 *)camry_host_ptr((uint32_t)(iVar1 + param_2)))) = (*((undefined1 *)camry_host_ptr((uint32_t)(iVar1 + iVar2))));
  }
  return 0;
}



/* Paired constant publisher: DAT_febf2bfa = 0; and DAT_febf2bfb = 0;; shape-classified from the
   canonical corpus. Target cells not yet named. */

void FUN_00006e4a(void)

{
  DAT_febf2bfa = 0;
  DAT_febf2bfb = 0;
  return;
}



/* Paired constant publisher: DAT_febf2bfa = 1; and DAT_febf2bfb = 0;; shape-classified from the
   canonical corpus. Target cells not yet named. */

void FUN_00006e54(void)

{
  DAT_febf2bfa = 1;
  DAT_febf2bfb = 0;
  return;
}



/* Paired constant publisher: DAT_febf2bfa = 0; and DAT_febf2bfb = 0;; shape-classified from the
   canonical corpus. Target cells not yet named. */

void FUN_00006ea2(void)

{
  DAT_febf2bfa = 0;
  DAT_febf2bfb = 0;
  return;
}



/* Routine CRC-success path initializes image key/BOTH CBC-CMAC contexts via70D4 before
   authentication submission. */

void f33_boot_authentication_crypto_initialize(void)

{
  f33_boot_image_crypto_initialize();
  return;
}



/* Real r6/r7 start,length passed unchanged to7122; reject ifactive2BFD!=0, else seed
   CMAC-prefix/cursors and publishresult1/active1 on success. Return0accepted/1rejected. Does not
   initialize contexts by itself. */

uint f33_boot_region_authentication_submit(uint start,uint length)

{
  uint32_t puVar1;
  uint uVar2;
  uint uVar3;
  
  puVar1 = 0xfebf9800u;
  uVar3 = 1;
  if ((DAT_febf2bfd == '\0') &&
     (uVar2 = f33_boot_image_authentication_begin(start,length), uVar2 == 0)) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6c04))))) = 1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6c03))))) = 1;
    uVar3 = 0;
  }
  return uVar3;
}



/* Retain established name. Process
   onlyactive,7170return2busy;0clearsresult;terminal0/1clearsactive. Does not wipe
   contexts/configured key/output/cursors; timer routine5936/5A04 separately clearscontexts on
   normal terminal consumption. */

void f33_boot_region_authentication_progress(void)

{
  uint32_t puVar1;
  uint uVar2;
  
  puVar1 = 0xfebf9800u;
  if ((DAT_febf2bfd != '\0') && (uVar2 = f33_boot_image_authentication_step(), uVar2 != 2)) {
    if (uVar2 == 0) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6c04))))) = 0;
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6c03))))) = 0;
  }
  return;
}



/* Routine wait-auth terminal cleanup forwards70FC; wipes both CBC and CMAC, retaining
   result/activity/cursors/configured materials/output. */

void f33_boot_region_authentication_clear_contexts(void)

{
  f33_boot_image_crypto_clear();
  return;
}



/* Setresult2BFC=1,clearactive2BFD=0 only; no context/material/cursor wipe. Resident6A22
   initialization caller. */

void f33_boot_region_authentication_clear_activity(void)

{
  DAT_febf2bfc = 1;
  DAT_febf2bfd = 0;
  return;
}



/* AES-128 single-block DECRYPT client_material under exactROMBFE8 key into intermediate_key;not
   encryption andnotCMAC. Shared AES contextFEBF2D48
   init7680,length16,decrypt7470,length16,clear76C6. Native AES known-answer and protocol-state
   cases use explicit RAM. Service paths stop at674A before response/timer completion; direct
   session invalidation cases return. No complete unlock or entropy claim. */

void f33_boot_security_decrypt_client_material(uchar *client_material,uchar *intermediate_key)

{
  f33_boot_aes128_initialize_context
            (f33_boot_security_client_decryption_key, '\x10', ((F33BootAes128Context *)camry_host_ptr((uint32_t)((0xfebf2d48u)))));
  f33_boot_aes128_decrypt_block
            (client_material, intermediate_key, '\x10', ((F33BootAes128Context *)camry_host_ptr((uint32_t)((0xfebf2d48u)))));
  f33_boot_aes128_clear_context(((F33BootAes128Context *)camry_host_ptr((uint32_t)((0xfebf2d48u)))));
  return;
}



/* AES-128 single-block encryption with16-byte key/input/output,using shared
   contextFEBF2D48;clearsentire196-bytecontextafteroperation. r6key,r7plaintext,r8output;
   noapplicationGP/SecOCsemantics. Native AES known-answer and protocol-state cases use explicit
   RAM. Service paths stop at674A before response/timer completion; direct session invalidation
   cases return. No complete unlock or entropy claim. */

void f33_boot_security_encrypt_block(uchar *key,uchar *plaintext,uchar *ciphertext)

{
  f33_boot_aes128_initialize_context(key, '\x10', ((F33BootAes128Context *)camry_host_ptr((uint32_t)((0xfebf2d48u)))));
  f33_boot_aes128_encrypt_block(plaintext, ciphertext, '\x10', ((F33BootAes128Context *)camry_host_ptr((uint32_t)((0xfebf2d48u)))));
  f33_boot_aes128_clear_context(((F33BootAes128Context *)camry_host_ptr((uint32_t)((0xfebf2d48u)))));
  return;
}



/* Expected key = AES128_ENCRYPT(AES128_DECRYPT(ROM[BFE8..BFF7], client_material), challenge).
   The16-byte intermediate is stack-local, not CMAC, hash or a seed-only mapping. Both operations
   clear the shared196-byte context; intermediate and expected-key stack buffers are not explicitly
   cleared. Independent known-answer native composition verifies this transform, not complete
   transport/unlock. Native AES known-answer and protocol-state cases use explicit RAM. Service
   paths stop at674A before response/timer completion; direct session invalidation cases return. No
   complete unlock or entropy claim. */

void f33_boot_security_derive_expected_key
               (uchar *client_material,uchar *challenge,uchar *expected_key)

{
  uchar auStack_1c [16];
  
  f33_boot_security_decrypt_client_material(client_material,auStack_1c);
  f33_boot_security_encrypt_block(auStack_1c,challenge,expected_key);
  return;
}



/* Derive retained2D18=AES128_ENCRYPT(ROMBFD8,configured2D08),one16-byte block. Shared AES2D48
   cleared196bytes afterward; configured/derived buffers retained. Distinct from SID27 BFE8 decrypt
   derivation. */

void f33_boot_image_derive_key(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebf9800u;
  f33_boot_aes128_initialize_context
            (f33_boot_image_key_derivation_key, '\x10', ((F33BootAes128Context *)camry_host_ptr((uint32_t)((0xfebf2d48u)))));
  f33_boot_aes128_encrypt_block
            (((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x6af8))),  ((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x6ae8))),  '\x10', ((F33BootAes128Context *)camry_host_ptr((uint32_t)((0xfebf2d48u)))));
  f33_boot_aes128_clear_context(((F33BootAes128Context *)camry_host_ptr((uint32_t)((0xfebf2d48u)))));
  return;
}



/* Initialize CBC2EF0 with derived key2D18/IV2CF8; initialize CMAC2C00 same key with zero chain then
   derive CMAC subkeys. Wrapper ignores all statuses. Does not consume authentication prefix yet. */

void f33_boot_image_initialize_contexts(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebf9800u;
  f33_boot_aes128_cbc_initialize
            (f33_boot_image_derived_key, '\x10', f33_boot_image_iv_and_authentication_prefix, '\x10', ((F33BootAes128CbcContext *)camry_host_ptr((uint32_t)((0xfebf2ef0u)))));
  f33_boot_aes128_cmac_initialize
            (f33_boot_image_derived_key,'\x10',((F33BootAes128CmacContext *)camry_host_ptr((uint32_t)(puVar1 + -0x6c00))));
  f33_boot_aes128_cmac_derive_subkeys(((F33BootAes128CmacContext *)camry_host_ptr((uint32_t)(puVar1 + -0x6c00))));
  return;
}



/* Derive image key7068 then initialize both CBC/CMAC709A. Reinitializes shared image contexts, not
   a per-transfer-chunk action. */

void f33_boot_image_crypto_initialize(void)

{
  f33_boot_image_derive_key();
  f33_boot_image_initialize_contexts();
  return;
}



/* Clear CBC2EF0 all228 bytes then CMAC2C00 all248 bytes. Retain IV/material/derived key/output and
   authentication cursors; does not reset activity flags. */

void f33_boot_image_clear_contexts(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebf9800u;
  f33_boot_aes128_cbc_clear(((F33BootAes128CbcContext *)camry_host_ptr((uint32_t)((0xfebf2ef0u)))));
  f33_boot_aes128_cmac_clear(((F33BootAes128CmacContext *)camry_host_ptr((uint32_t)(puVar1 + -0x6c00))));
  return;
}



/* Forward to70E4, wiping CBC and CMAC contexts only. TransferExit6BD2 and routine completion6F04
   share this owner. */

void f33_boot_image_crypto_clear(void)

{
  f33_boot_image_clear_contexts();
  return;
}



/* AES128-CBC decrypt one16-byte block with persistent2EF0 context through8162. Return0 success or1
   failure; foreground6BDE ignores this return. */

uint f33_boot_image_decrypt_block(uchar *ciphertext,uchar *plaintext)

{
  uint uVar1;
  
  uVar1 = f33_boot_aes128_cbc_decrypt_block(ciphertext, plaintext, '\x10', ((F33BootAes128CbcContext *)camry_host_ptr((uint32_t)((0xfebf2ef0u)))))
  ;
  return (uint)(uVar1 != 0);
}



/* Select fixed descriptor trailer; feed configured IV2CF8 as NONFINAL16-byte CMAC prefix into2D28;
   on success seed cursor=start and last_block=start+length-16. Return0/1. No
   length-multiple/minimum/alignment validation; context must already be initialized. Trailer is
   stored even if prefix update fails. */

uint f33_boot_image_authentication_begin(uint start,uint length)

{
  uint32_t puVar1;
  uint uVar2;
  uint uVar3;
  uint uStack_14;
  
  puVar1 = 0xfebf9800u;
  uVar3 = 1;
  uVar2 = f33_boot_lookup_authentication_trailer(start,length,&uStack_14);
  if (uVar2 == 0) {
    (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x6754)))) = uStack_14;
    uVar2 = f33_boot_aes128_cmac_update_block
                      (((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x6b08))), ((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x6ad8))), '\x10', 0, 
                       ((F33BootAes128CmacContext *)camry_host_ptr((uint32_t)(puVar1 + -0x6c00))));
    if (uVar2 == 0) {
      (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x6750)))) = start;
      (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x6758)))) = length + start + -0x10;
      uVar3 = 0;
    }
  }
  return uVar3;
}



void FUN_00007208(int param_1)

{
  bool bVar1;
  int iVar2;
  
  if (param_1 != 0) {
    do {
      iVar2 = 0x9b;
      do {
        bVar1 = iVar2 != 1;
        iVar2 = iVar2 + -1;
      } while (bVar1);
      bVar1 = param_1 != 1;
      param_1 = param_1 + -1;
    } while (bVar1);
  }
  return;
}



char FUN_00007262(char param_1)

{
  if (param_1 != -1) {
    return param_1 + '\x01';
  }
  return -1;
}



/* CopyzeroROM8FC0blocktostack;7B42AESCTRtransformintooutputusingr9context.Return0/FF. */

uint f33_boot_security_generate_candidate_block
               (uchar *challenge_out,F33BootAes128CtrContext *context)

{
  undefined1 uVar1;
  uchar *puVar2;
  uint uVar3;
  uint uVar4;
  undefined1 *puVar5;
  uchar local_14 [16];
  
  puVar2 = local_14;
  puVar5 = ((undefined *)camry_host_ptr(0x8fc0u));
  do {
    uVar1 = *puVar5;
    puVar5 = puVar5 + 1;
    *puVar2 = uVar1;
    puVar2 = puVar2 + 1;
  } while (puVar5 != ((undefined *)camry_host_ptr(0x8fd0u)));
  uVar4 = f33_boot_aes128_ctr_transform_block(local_14,challenge_out,'\x10',context);
  uVar3 = 0;
  if (uVar4 != 0) {
    uVar3 = 0xff;
  }
  return uVar3;
}



/* CopyROM8FD0zero16-bytecounter;onlylength16;call7C9A(key,16,counter,16,context)withfifthargstack+0atcallerSP.Return0/FF.
    */

uint f33_boot_security_initialize_candidate_context
               (uchar *timer_key,uchar key_length,F33BootAes128CtrContext *context)

{
  uchar uVar1;
  uchar *puVar2;
  uint uVar3;
  uchar *puVar4;
  uchar local_14 [16];
  
  puVar4 = "";
  puVar2 = local_14;
  do {
    uVar1 = *puVar4;
    puVar4 = puVar4 + 1;
    *puVar2 = uVar1;
    puVar2 = puVar2 + 1;
  } while (puVar4 != ((undefined *)camry_host_ptr(0x8fe0u)));
  if ((key_length == '\x10') &&
     (uVar3 = f33_boot_aes128_ctr_initialize(timer_key,'\x10',local_14,'\x10',context), uVar3 == 0))
  {
    return 0;
  }
  return 0xff;
}



/* Forwardr6to7D3C,wipeentire228-byteAESCTRcontext;notzeroargumentdespitemissingpseudoparameter. */

void f33_boot_security_clear_candidate_context(F33BootAes128CtrContext *context)

{
  f33_boot_aes128_ctr_clear(context);
  return;
}



/* WARNING: This is an inlined function */
/* Expand16 key bytes into176 bytes (44 words), using the standard forward S-box and ten round
   constants. Exact leaf preserves incoming R8 context, subsequently used at76AC; inline real p-code
   instead of inventing another return value. Native AES known-answer and protocol-state cases use
   explicit RAM. Service paths stop at674A before response/timer completion; direct session
   invalidation cases return. No complete unlock or entropy claim. */

void f33_boot_aes128_expand_round_keys(uchar *key,uchar *round_keys)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  
  uVar3 = 4;
  *round_keys = *key;
  round_keys[1] = key[1];
  round_keys[2] = key[2];
  round_keys[3] = key[3];
  round_keys[4] = key[4];
  round_keys[5] = key[5];
  round_keys[6] = key[6];
  round_keys[7] = key[7];
  round_keys[8] = key[8];
  round_keys[9] = key[9];
  round_keys[10] = key[10];
  round_keys[0xb] = key[0xb];
  round_keys[0xc] = key[0xc];
  round_keys[0xd] = key[0xd];
  round_keys[0xe] = key[0xe];
  round_keys[0xf] = key[0xf];
  do {
    iVar1 = uVar3 * 4;
    uVar2 = *(uint *)(round_keys + iVar1 + -4);
    if ((uVar3 & 3) == 0) {
      uVar2 = (uint)CRYPT_AES_Encryption_SBox[uVar2 & 0xff] << 0x18 |
              (uint)CRYPT_AES_Encryption_SBox[uVar2 >> 0x18] << 0x10 |
              (uint)CRYPT_AES_Encryption_SBox[(uVar2 >> 8 & 0xffff) >> 8] << 8 |
              (uint)((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x8fe0u + (uint32_t)((int)uVar3 >> 2) * 1u)))) ^ CRYPT_AES_Encryption_SBox[uVar2 >> 8 & 0xff]
                    );
    }
    uVar3 = uVar3 + 1 & 0xffff;
    *(uint *)(round_keys + iVar1) = (*((uint *)camry_host_ptr((uint32_t)((int)camry_host_addr((round_keys + iVar1)) + -0x10)))) ^ uVar2;
  } while (uVar3 < 0x2c);
  return;
}



void FUN_000076b6(undefined4 *param_1,int param_2)

{
  for (; param_2 != 0; param_2 = param_2 + -4) {
    *param_1 = 0;
    param_1 = param_1 + 1;
  }
  return;
}



void FUN_000076da(int param_1)

{
  byte *pbVar1;
  
  pbVar1 = ((byte *)camry_host_ptr((uint32_t)(param_1 + (*(byte *)(param_1 + 0xc1) & 0xf) * 0x10)));
  (*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xb0)))) = (*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xb0)))) ^ *pbVar1;
  (*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xb4)))) = (*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xb4)))) ^ pbVar1[1];
  (*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xb8)))) = (*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xb8)))) ^ pbVar1[2];
  (*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xbc)))) = (*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xbc)))) ^ pbVar1[3];
  (*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xb1)))) = (*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xb1)))) ^ pbVar1[4];
  (*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xb5)))) = (*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xb5)))) ^ pbVar1[5];
  (*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xb9)))) = (*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xb9)))) ^ pbVar1[6];
  (*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xbd)))) = (*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xbd)))) ^ pbVar1[7];
  (*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xb2)))) = (*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xb2)))) ^ pbVar1[8];
  (*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xb6)))) = (*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xb6)))) ^ pbVar1[9];
  (*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xba)))) = (*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xba)))) ^ pbVar1[10];
  (*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xbe)))) = (*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xbe)))) ^ pbVar1[0xb];
  (*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xb3)))) = (*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xb3)))) ^ pbVar1[0xc];
  (*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xb7)))) = (*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xb7)))) ^ pbVar1[0xd];
  (*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xbb)))) = (*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xbb)))) ^ pbVar1[0xe];
  (*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xbf)))) = (*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xbf)))) ^ pbVar1[0xf];
  return;
}



void FUN_000077a8(int param_1)

{
  (*((uchar *)camry_host_ptr((uint32_t)(param_1 + 0xb0)))) = CRYPT_AES_Encryption_SBox[(*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xb0))))];
  (*((uchar *)camry_host_ptr((uint32_t)(param_1 + 0xb1)))) = CRYPT_AES_Encryption_SBox[(*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xb1))))];
  (*((uchar *)camry_host_ptr((uint32_t)(param_1 + 0xb2)))) = CRYPT_AES_Encryption_SBox[(*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xb2))))];
  (*((uchar *)camry_host_ptr((uint32_t)(param_1 + 0xb3)))) = CRYPT_AES_Encryption_SBox[(*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xb3))))];
  (*((uchar *)camry_host_ptr((uint32_t)(param_1 + 0xb4)))) = CRYPT_AES_Encryption_SBox[(*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xb4))))];
  (*((uchar *)camry_host_ptr((uint32_t)(param_1 + 0xb5)))) = CRYPT_AES_Encryption_SBox[(*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xb5))))];
  (*((uchar *)camry_host_ptr((uint32_t)(param_1 + 0xb6)))) = CRYPT_AES_Encryption_SBox[(*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xb6))))];
  (*((uchar *)camry_host_ptr((uint32_t)(param_1 + 0xb7)))) = CRYPT_AES_Encryption_SBox[(*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xb7))))];
  (*((uchar *)camry_host_ptr((uint32_t)(param_1 + 0xb8)))) = CRYPT_AES_Encryption_SBox[(*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xb8))))];
  (*((uchar *)camry_host_ptr((uint32_t)(param_1 + 0xb9)))) = CRYPT_AES_Encryption_SBox[(*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xb9))))];
  (*((uchar *)camry_host_ptr((uint32_t)(param_1 + 0xba)))) = CRYPT_AES_Encryption_SBox[(*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xba))))];
  (*((uchar *)camry_host_ptr((uint32_t)(param_1 + 0xbb)))) = CRYPT_AES_Encryption_SBox[(*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xbb))))];
  (*((uchar *)camry_host_ptr((uint32_t)(param_1 + 0xbc)))) = CRYPT_AES_Encryption_SBox[(*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xbc))))];
  (*((uchar *)camry_host_ptr((uint32_t)(param_1 + 0xbd)))) = CRYPT_AES_Encryption_SBox[(*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xbd))))];
  (*((uchar *)camry_host_ptr((uint32_t)(param_1 + 0xbe)))) = CRYPT_AES_Encryption_SBox[(*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xbe))))];
  (*((uchar *)camry_host_ptr((uint32_t)(param_1 + 0xbf)))) = CRYPT_AES_Encryption_SBox[(*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xbf))))];
  return;
}



void FUN_0000786e(int param_1)

{
  (*((uint *)camry_host_ptr((uint32_t)(param_1 + 0xb4)))) = (*((uint *)camry_host_ptr((uint32_t)(param_1 + 0xb4)))) << 0x18 | (*((uint *)camry_host_ptr((uint32_t)(param_1 + 0xb4)))) >> 8;
  (*((uint *)camry_host_ptr((uint32_t)(param_1 + 0xb8)))) = (*((uint *)camry_host_ptr((uint32_t)(param_1 + 0xb8)))) << 0x10 | (*((uint *)camry_host_ptr((uint32_t)(param_1 + 0xb8)))) >> 0x10;
  (*((uint *)camry_host_ptr((uint32_t)(param_1 + 0xbc)))) = (*((uint *)camry_host_ptr((uint32_t)(param_1 + 0xbc)))) << 8 | (*((uint *)camry_host_ptr((uint32_t)(param_1 + 0xbc)))) >> 0x18;
  return;
}



void FUN_00007896(int param_1)

{
  byte *pbVar1;
  int iVar2;
  byte bVar3;
  byte bVar4;
  byte bVar5;
  byte bVar6;
  uint uVar7;
  
  param_1 = param_1 + 0xb0;
  uVar7 = 0;
  do {
    pbVar1 = ((byte *)camry_host_ptr((uint32_t)(uVar7 + param_1)));
    bVar3 = *pbVar1;
    bVar4 = pbVar1[4] ^ bVar3;
    bVar6 = bVar4 << 1;
    bVar5 = pbVar1[8] ^ bVar4 ^ pbVar1[0xc];
    if ((char)bVar4 < '\0') {
      bVar6 = bVar6 ^ 0x1b;
    }
    pbVar1 = ((byte *)camry_host_ptr((uint32_t)(uVar7 + param_1)));
    *pbVar1 = bVar5 ^ bVar6 ^ bVar3;
    bVar4 = pbVar1[8] ^ pbVar1[4];
    bVar6 = bVar4 << 1;
    if ((char)bVar4 < '\0') {
      bVar6 = bVar6 ^ 0x1b;
    }
    iVar2 = uVar7 + param_1;
    (*((byte *)camry_host_ptr((uint32_t)(iVar2 + 4)))) = bVar5 ^ bVar6 ^ pbVar1[4];
    bVar4 = (*((byte *)camry_host_ptr((uint32_t)(iVar2 + 0xc)))) ^ (*((byte *)camry_host_ptr((uint32_t)(iVar2 + 8))));
    bVar6 = bVar4 << 1;
    if ((char)bVar4 < '\0') {
      bVar6 = bVar6 ^ 0x1b;
    }
    (*((byte *)camry_host_ptr((uint32_t)(uVar7 + param_1 + 8)))) = bVar5 ^ bVar6 ^ (*((byte *)camry_host_ptr((uint32_t)(iVar2 + 8))));
    bVar4 = (*((byte *)camry_host_ptr((uint32_t)(uVar7 + param_1 + 0xc))));
    bVar3 = bVar3 ^ bVar4;
    bVar6 = bVar3 << 1;
    if ((char)bVar3 < '\0') {
      bVar6 = bVar6 ^ 0x1b;
    }
    (*((byte *)camry_host_ptr((uint32_t)(uVar7 + param_1 + 0xc)))) = bVar5 ^ bVar6 ^ bVar4;
    uVar7 = uVar7 + 1;
  } while (uVar7 < 4);
  return;
}



void FUN_00007928(int param_1)

{
  (*((uchar *)camry_host_ptr((uint32_t)(param_1 + 0xb0)))) = CRYPT_AES_Decryption_SBox_Inverse[(*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xb0))))];
  (*((uchar *)camry_host_ptr((uint32_t)(param_1 + 0xb1)))) = CRYPT_AES_Decryption_SBox_Inverse[(*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xb1))))];
  (*((uchar *)camry_host_ptr((uint32_t)(param_1 + 0xb2)))) = CRYPT_AES_Decryption_SBox_Inverse[(*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xb2))))];
  (*((uchar *)camry_host_ptr((uint32_t)(param_1 + 0xb3)))) = CRYPT_AES_Decryption_SBox_Inverse[(*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xb3))))];
  (*((uchar *)camry_host_ptr((uint32_t)(param_1 + 0xb4)))) = CRYPT_AES_Decryption_SBox_Inverse[(*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xb4))))];
  (*((uchar *)camry_host_ptr((uint32_t)(param_1 + 0xb5)))) = CRYPT_AES_Decryption_SBox_Inverse[(*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xb5))))];
  (*((uchar *)camry_host_ptr((uint32_t)(param_1 + 0xb6)))) = CRYPT_AES_Decryption_SBox_Inverse[(*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xb6))))];
  (*((uchar *)camry_host_ptr((uint32_t)(param_1 + 0xb7)))) = CRYPT_AES_Decryption_SBox_Inverse[(*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xb7))))];
  (*((uchar *)camry_host_ptr((uint32_t)(param_1 + 0xb8)))) = CRYPT_AES_Decryption_SBox_Inverse[(*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xb8))))];
  (*((uchar *)camry_host_ptr((uint32_t)(param_1 + 0xb9)))) = CRYPT_AES_Decryption_SBox_Inverse[(*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xb9))))];
  (*((uchar *)camry_host_ptr((uint32_t)(param_1 + 0xba)))) = CRYPT_AES_Decryption_SBox_Inverse[(*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xba))))];
  (*((uchar *)camry_host_ptr((uint32_t)(param_1 + 0xbb)))) = CRYPT_AES_Decryption_SBox_Inverse[(*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xbb))))];
  (*((uchar *)camry_host_ptr((uint32_t)(param_1 + 0xbc)))) = CRYPT_AES_Decryption_SBox_Inverse[(*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xbc))))];
  (*((uchar *)camry_host_ptr((uint32_t)(param_1 + 0xbd)))) = CRYPT_AES_Decryption_SBox_Inverse[(*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xbd))))];
  (*((uchar *)camry_host_ptr((uint32_t)(param_1 + 0xbe)))) = CRYPT_AES_Decryption_SBox_Inverse[(*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xbe))))];
  (*((uchar *)camry_host_ptr((uint32_t)(param_1 + 0xbf)))) = CRYPT_AES_Decryption_SBox_Inverse[(*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xbf))))];
  return;
}



void FUN_000079ee(int param_1)

{
  (*((uint *)camry_host_ptr((uint32_t)(param_1 + 0xb4)))) = (*((uint *)camry_host_ptr((uint32_t)(param_1 + 0xb4)))) >> 0x18 | (*((uint *)camry_host_ptr((uint32_t)(param_1 + 0xb4)))) << 8;
  (*((uint *)camry_host_ptr((uint32_t)(param_1 + 0xb8)))) = (*((uint *)camry_host_ptr((uint32_t)(param_1 + 0xb8)))) >> 0x10 | (*((uint *)camry_host_ptr((uint32_t)(param_1 + 0xb8)))) << 0x10;
  (*((uint *)camry_host_ptr((uint32_t)(param_1 + 0xbc)))) = (*((uint *)camry_host_ptr((uint32_t)(param_1 + 0xbc)))) >> 8 | (*((uint *)camry_host_ptr((uint32_t)(param_1 + 0xbc)))) << 0x18;
  return;
}



void FUN_00007a16(int param_1)

{
  byte *pbVar1;
  byte bVar2;
  byte bVar3;
  byte bVar4;
  byte bVar5;
  uint uVar6;
  uint uVar7;
  uint uVar8;
  uint uVar9;
  byte bVar10;
  byte bVar11;
  byte bVar12;
  uint uVar13;
  byte local_4 [4];
  
  param_1 = param_1 + 0xb0;
  uVar8 = 0;
  do {
    uVar9 = 0;
    do {
      bVar5 = (*((byte *)camry_host_ptr((uint32_t)(uVar8 + uVar9 * 4 + param_1))));
      uVar13 = (uint)bVar5;
      uVar6 = uVar13 << 1;
      if ((char)bVar5 < '\0') {
        uVar6 = uVar6 ^ 0x1b;
      }
      uVar7 = (uVar6 ^ uVar13) << 1;
      if (((uVar6 ^ uVar13) >> 7 & 1) != 0) {
        uVar7 = uVar7 ^ 0x1b;
      }
      bVar5 = (byte)((uVar7 ^ uVar13) << 1);
      if (((uVar7 ^ uVar13) >> 7 & 1) != 0) {
        bVar5 = bVar5 ^ 0x1b;
      }
      bVar2 = (*((byte *)camry_host_ptr((uint32_t)(uVar8 + (uVar9 + 1 & 3) * 4 + param_1))));
      uVar6 = (uint)bVar2 << 1;
      if ((char)bVar2 < '\0') {
        uVar6 = uVar6 ^ 0x1b;
      }
      uVar13 = uVar6 << 1;
      if ((uVar6 >> 7 & 1) != 0) {
        uVar13 = uVar13 ^ 0x1b;
      }
      uVar13 = uVar13 ^ bVar2;
      bVar12 = (byte)(uVar13 << 1);
      if ((uVar13 >> 7 & 1) != 0) {
        bVar12 = bVar12 ^ 0x1b;
      }
      bVar3 = (*((byte *)camry_host_ptr((uint32_t)(uVar8 + (uVar9 + 2 & 3) * 4 + param_1))));
      uVar6 = (uint)bVar3 << 1;
      if ((char)bVar3 < '\0') {
        uVar6 = uVar6 ^ 0x1b;
      }
      uVar6 = uVar6 ^ bVar3;
      uVar13 = uVar6 << 1;
      if ((uVar6 >> 7 & 1) != 0) {
        uVar13 = uVar13 ^ 0x1b;
      }
      bVar11 = (byte)(uVar13 << 1);
      if ((uVar13 >> 7 & 1) != 0) {
        bVar11 = bVar11 ^ 0x1b;
      }
      bVar4 = (*((byte *)camry_host_ptr((uint32_t)(uVar8 + (uVar9 - 1 & 3) * 4 + param_1))));
      uVar6 = (uint)bVar4 << 1;
      if ((char)bVar4 < '\0') {
        uVar6 = uVar6 ^ 0x1b;
      }
      uVar13 = uVar6 << 1;
      if ((uVar6 >> 7 & 1) != 0) {
        uVar13 = uVar13 ^ 0x1b;
      }
      bVar10 = (byte)(uVar13 << 1);
      if ((uVar13 >> 7 & 1) != 0) {
        bVar10 = bVar10 ^ 0x1b;
      }
      local_4[uVar9] = bVar10 ^ bVar4 ^ bVar11 ^ bVar3 ^ bVar12 ^ bVar2 ^ bVar5;
      uVar9 = uVar9 + 1;
    } while (uVar9 < 4);
    pbVar1 = ((byte *)camry_host_ptr((uint32_t)(uVar8 + param_1)));
    uVar8 = uVar8 + 1;
    *pbVar1 = local_4[0];
    pbVar1[4] = local_4[1];
    pbVar1[8] = local_4[2];
    pbVar1[0xc] = local_4[3];
  } while (uVar8 < 4);
  return;
}


