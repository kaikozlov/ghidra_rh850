#include "common.h"


void FUN_0000400a(uint param_1)

{
  undefined1 uStack_1a;
  undefined1 uStack_19;
  undefined4 uStack_18;
  undefined1 auStack_14 [8];
  
  FUN_00003f96((param_1 & 0x7f) >> 4, param_1 & 0xf, camry_host_addr(&uStack_18), camry_host_addr(&uStack_1a), &uStack_19, auStack_14);
  FUN_00004678(param_1 & 0xffff,uStack_18,uStack_1a,uStack_19,auStack_14);
  return;
}



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
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe3800u + (uint32_t)(iVar1) * 1u)))) = 0xff;
    }
    (*((volatile uint16_t *)camry_host_ptr(0xfebe4998u))) = (short)uVar2;
    (*((volatile uint16_t *)camry_host_ptr(0xfebe499au))) = 0;
    return 0;
  }
  return 1;
}



/* Rejectlength0 orfailedfirst3474 lookup. Lookup modulo32lastaddress, ignoresecondlookupreturn,
   andreturn((uintptr_t)(last_block)<(uintptr_t)(first_block)). An out-of-range lastaddress can use3474 fallbackF8000; this is
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
  
  puVar3 = 0xfebeb800u;
  uVar5 = 1;
  if ((*((volatile uint8_t *)camry_host_ptr(0xfebe4aa1u))) == '\0') {
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
  
  puVar1 = 0xfebeb800u;
  uVar3 = 1;
  if ((((*((volatile uint8_t *)camry_host_ptr(0xfebe4aa1u))) == '\0') &&
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
  (*((volatile uint8_t *)camry_host_ptr(0xfebe499fu))) = paused;
  return;
}



/* Set299E=1; doesnot immediatelyclearbusy orchange result.4428 later consumes it evenwhenpaused. */

void f33_boot_request_flash_worker_cancel(void)

{
  (*((volatile uint8_t *)camry_host_ptr(0xfebe499eu))) = 1;
  return;
}



/* Append low16length bytes fromsource to1800 ring; wrapproducer at1100 andpublish2998 afterward. No
   owncapacitycheck orPMR. Caller42D8 admission protectsreservedslot. */

void f33_boot_append_program_input(uchar *source,ushort length)

{
  uchar uVar1;
  uint uVar2;
  uint uVar3;
  
  uVar3 = (uint)(*((volatile uint16_t *)camry_host_ptr(0xfebe4998u)));
  for (; length != 0; length = length - 1) {
    uVar1 = *source;
    uVar2 = uVar3 + 1 & 0xffff;
    source = source + 1;
    if (0x10ff < uVar2) {
      uVar2 = 0;
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe3800u + (uint32_t)(uVar3) * 1u)))) = uVar1;
    uVar3 = uVar2;
  }
  (*((volatile uint16_t *)camry_host_ptr(0xfebe4998u))) = (short)uVar3;
  return;
}



/* Snapshotu16producer2998 andconsumer299A underFFFF PMR; compute modulo1100 occupancy, zxh
   tofullR10, restorePMR. Equalindicesmeanempty. Native wrapped16-byte input is consumed in order
   and paddedFF; exact counter-block exclusion avoids driver dispatch. Other programming paths
   remain static. */

uint f33_boot_program_input_occupancy(void)

{
  ushort uVar1;
  uint32_t puVar2;
  undefined4 uVar3;
  ushort uVar4;
  
  puVar2 = 0xfebeb800u;
  uVar3 = FUN_0000721e(0xffff);
  uVar4 = (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x6e68))));
  uVar1 = (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x6e66))));
  if (uVar4 < uVar1) {
    uVar4 = 0x1100 - (uVar1 - uVar4);
  }
  else {
    uVar4 = uVar4 - uVar1;
  }
  FUN_00007244(uVar3);
  return (uint)uVar4;
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



/* Skipcallbackonlyif34DA(currentblock)==1. Otherwise42F6 optionallystagescounter;
   call[FEBF0FD0](block,0,1,&status), thenonstatus0 andstagedcounter call(pointer,29A0,0,&status).
   Any nonzero statusreturns1, else0. Boot-phase dynamicdriverboundary; overlapping
   applicationNvMglobalisnotcallee. */

uint f33_boot_erase_current_block_preserving_counter(void)

{
  undefined4 uVar1;
  uint32_t puVar2;
  uint uVar3;
  uint uVar4;
  char cStack_11;
  
  puVar2 = 0xfebeb800u;
  uVar4 = 0;
  uVar3 = f33_boot_get_flash_block_skip_flag((*((volatile uint32_t *)camry_host_ptr(0xfebe4980u))));
  if (uVar3 != 1) {
    uVar3 = f33_boot_stage_preserved_program_counter();
    uVar1 = (*((volatile uint32_t *)camry_host_ptr(0xfebf0fd0u)));
    (*(int (*)())camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr(0xfebf0fd0u)))))((*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + -0x6e80)))),0,1,&cStack_11)
    ;
    if ((cStack_11 != '\0') ||
       ((uVar3 == 0 &&
        ((*(int (*)())camry_host_ptr((uint32_t)(uVar1)))((*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + -0x6e6c)))),puVar2 + -0x6e60,0,&cStack_11),
        cStack_11 != '\0')))) {
      uVar4 = 1;
    }
  }
  return uVar4;
}



/* Copylow16length bytes from1800 ring,wrapconsumerat1100,publish299Aaftercopy.
   Caller43BEchecksavailability; no localcapacitycheck. Native wrapped16-byte input is consumed in
   order and paddedFF; exact counter-block exclusion avoids driver dispatch. Other programming paths
   remain static. */

void f33_boot_consume_program_input(uchar *destination,ushort length)

{
  uchar *puVar1;
  uint uVar2;
  
  uVar2 = (uint)(*((volatile uint16_t *)camry_host_ptr(0xfebe499au)));
  for (; length != 0; length = length - 1) {
    puVar1 = ((undefined *)camry_host_ptr(0xfebe3800u)) + uVar2;
    uVar2 = uVar2 + 1 & 0xffff;
    *destination = *puVar1;
    destination = destination + 1;
    if (0x10ff < uVar2) {
      uVar2 = 0;
    }
  }
  (*((volatile uint16_t *)camry_host_ptr(0xfebe499au))) = (short)uVar2;
  return;
}



/* Return2withoutmutation iflow16length>ringoccupancy. Otherwiseconsumeinto29A0,padFF to256
   usingfullsignedlength comparison, theninvoke[FEBF0FD0](cursor,buffer,0,&status)
   unlesscursor==2994counterblock. Returnbool(status!=0); skippedcounterblockreturns0.
   Consumptionprecedesdevicefailure;4428supplieslength<=256. Native wrapped16-byte input is consumed
   in order and paddedFF; exact counter-block exclusion avoids driver dispatch. Other programming
   paths remain static. */

uint f33_boot_stage_and_program_input_chunk(uint length)

{
  uint32_t puVar1;
  uint uVar2;
  uint uVar3;
  uchar *destination;
  char cStack_11;
  
  puVar1 = 0xfebeb800u;
  uVar3 = 2;
  uVar2 = f33_boot_program_input_occupancy();
  if ((length & 0xffff) <= uVar2) {
    destination = ((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x6e60)));
    f33_boot_consume_program_input(destination,(ushort)length);
    for (; (int)(length - 0x100) < 0 != ((int)length < 0 && -1 < (int)(length - 0x100));
        length = length + 1) {
      destination[length] = 0xff;
    }
    if ((*((int *)camry_host_ptr((uint32_t)(puVar1 + -0x6e74)))) == (*((int *)camry_host_ptr((uint32_t)(puVar1 + -0x6e6c))))) {
      cStack_11 = '\0';
    }
    else {
      (*(int (*)())camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr(0xfebf0fd0u)))))((*((int *)camry_host_ptr((uint32_t)(puVar1 + -0x6e74)))),destination,0,&cStack_11);
    }
    uVar3 = (uint)(cStack_11 != '\0');
  }
  return uVar3;
}



/* UnderFFFF PMR, busy0returns; nonzeropause skipswork.
   Mode0erasesanddrains<=256chunks,mode1drains,mode2erasescoveredblocks.
   rc2waitsforinput;rc1clearsbusy retainingresult; successfulcompletionsetsresult0/busy0.
   Finalcancel==1alwaysclearcancel/busy/pausewithoutpromotingsuccess.
   Devicecallbackandphysicalcompletionremainexplicitboundary. Native resident foreground verifies
   protected-counter-block consumption, wrapped ring/padding and pause-versus-cancel precedence.
   Dynamic driver success is not exercised. */

void f33_boot_advance_flash_operation(void)

{
  char cVar1;
  bool bVar2;
  uint32_t puVar3;
  undefined4 uVar4;
  uint uVar5;
  uint uVar6;
  undefined1 uVar7;
  char cVar8;
  uint local_18;
  
  puVar3 = 0xfebeb800u;
  uVar4 = FUN_0000721e(0xffff);
  cVar8 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-27999)))));
  if (cVar8 == '\0') goto LAB_00004586;
  uVar7 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-28000)))));
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6e61))))) != '\0') goto LAB_0000456c;
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6e64)))));
  if (cVar1 == '\0') {
    bVar2 = false;
    if ((*((uint *)camry_host_ptr((uint32_t)(puVar3 + -0x6e78)))) <= (*((uint *)camry_host_ptr((uint32_t)(puVar3 + -0x6e74))))) {
      uVar6 = f33_boot_program_input_occupancy();
      if (uVar6 == 0) {
        bVar2 = true;
      }
      else {
        (*((uint *)camry_host_ptr((uint32_t)(puVar3 + -0x6e80)))) = (*((uint *)camry_host_ptr((uint32_t)(puVar3 + -0x6e78))));
        f33_boot_find_flash_block_end((*((uint *)camry_host_ptr((uint32_t)(puVar3 + -0x6e78)))),&local_18);
        (*((uint *)camry_host_ptr((uint32_t)(puVar3 + -0x6e78)))) = local_18;
      }
    }
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6e63))))) == '\x01') {
      uVar6 = f33_boot_program_input_occupancy();
      (*((uint *)camry_host_ptr((uint32_t)(puVar3 + -0x6e70)))) = uVar6;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6e63))))) = 0;
    }
    if (!bVar2) {
      uVar6 = f33_boot_erase_current_block_preserving_counter();
      if (uVar6 == 1) {
LAB_000044ce:
        cVar8 = '\0';
      }
      else {
        uVar6 = (*((uint *)camry_host_ptr((uint32_t)(puVar3 + -0x6e70))));
        if (uVar6 != 0) {
          if (0xff < uVar6) {
            uVar6 = 0x100;
          }
          uVar5 = f33_boot_stage_and_program_input_chunk(uVar6);
          if (uVar5 == 1) goto LAB_000044ce;
          if (uVar5 == 0) {
            (*((uint *)camry_host_ptr((uint32_t)(puVar3 + -0x6e74)))) = (*((int *)camry_host_ptr((uint32_t)(puVar3 + -0x6e74)))) + uVar6;
            (*((uint *)camry_host_ptr((uint32_t)(puVar3 + -0x6e70)))) = (*((int *)camry_host_ptr((uint32_t)(puVar3 + -0x6e70)))) - uVar6;
          }
        }
      }
    }
    uVar6 = (*((uint *)camry_host_ptr((uint32_t)(puVar3 + -0x6e70))));
LAB_00004534:
    if (uVar6 == 0) {
LAB_00004550:
      uVar7 = 0;
      cVar8 = '\0';
    }
  }
  else if (cVar1 == '\x01') {
    uVar6 = (*((uint *)camry_host_ptr((uint32_t)(puVar3 + -0x6e70))));
    if (0xff < uVar6) {
      uVar6 = 0x100;
    }
    uVar5 = f33_boot_stage_and_program_input_chunk(uVar6);
    if (uVar5 == 1) {
LAB_00004540:
      cVar8 = '\0';
    }
    else if (uVar5 == 0) {
      (*((uint *)camry_host_ptr((uint32_t)(puVar3 + -0x6e74)))) = (*((int *)camry_host_ptr((uint32_t)(puVar3 + -0x6e74)))) + uVar6;
      uVar5 = (*((uint *)camry_host_ptr((uint32_t)(puVar3 + -0x6e70))));
      (*((uint *)camry_host_ptr((uint32_t)(puVar3 + -0x6e70)))) = uVar5 - uVar6;
      if (uVar5 == uVar6) goto LAB_00004550;
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6e63))))) != '\x01') goto LAB_0000456c;
      uVar6 = f33_boot_program_input_occupancy();
      goto LAB_00004534;
    }
  }
  else if (cVar1 == '\x02') {
    uVar6 = f33_boot_erase_current_block_preserving_counter();
    if (uVar6 == 1) goto LAB_00004540;
    if ((*((int *)camry_host_ptr((uint32_t)(puVar3 + -0x6e80)))) == (*((int *)camry_host_ptr((uint32_t)(puVar3 + -0x6e7c))))) goto LAB_00004550;
    (*((uint *)camry_host_ptr((uint32_t)(puVar3 + -0x6e80)))) = (*((uint *)camry_host_ptr((uint32_t)(puVar3 + -0x6e78))));
    f33_boot_find_flash_block_end((*((uint *)camry_host_ptr((uint32_t)(puVar3 + -0x6e78)))),&local_18);
    (*((uint *)camry_host_ptr((uint32_t)(puVar3 + -0x6e78)))) = local_18;
  }
LAB_0000456c:
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6e62))))) == '\x01') {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6e62))))) = 0;
    cVar8 = '\0';
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6e61))))) = 0;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-28000))))) = uVar7;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-27999))))) = cVar8;
LAB_00004586:
  FUN_00007244(uVar4);
  return;
}



/* Clearbusy,pause,cancel,finalmarker,ringproducer/consumer;setresult1.
   Doesnotclearcursor,remaining,counterblock orstaging; no lowerdevicecancel. */

void f33_boot_reset_flash_operation_queue(void)

{
  (*((volatile uint8_t *)camry_host_ptr(0xfebe4aa1u))) = 0;
  (*((volatile uint8_t *)camry_host_ptr(0xfebe499fu))) = 0;
  (*((volatile uint8_t *)camry_host_ptr(0xfebe499eu))) = 0;
  (*((volatile uint8_t *)camry_host_ptr(0xfebe499du))) = 0;
  (*((volatile uint8_t *)camry_host_ptr(0xfebe4aa0u))) = 1;
  (*((volatile uint16_t *)camry_host_ptr(0xfebe4998u))) = 0;
  (*((volatile uint16_t *)camry_host_ptr(0xfebe499au))) = 0;
  return;
}



void FUN_00004678(uint param_1,int param_2,char param_3,uint param_4,undefined4 *param_5)

{
  undefined4 *puVar1;
  undefined4 *puVar2;
  bool bVar3;
  bool bVar4;
  undefined8 uVar5;
  uint uVar6;
  ushort uVar7;
  undefined4 local_34;
  undefined4 uStack_30;
  uint uStack_2c;
  undefined4 uStack_28;
  undefined4 uStack_24;
  
  uVar5 = 0x869c00000000;
  puVar1 = ((undefined4 *)camry_host_ptr((uint32_t)(PTR_PTR_00008940 + (param_1 & 0xffff) * 8)));
  uVar6 = (uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(puVar1) + 6))));
  uVar7 = *(ushort *)(puVar1 + 1);
  bVar4 = false;
  do {
    if (uVar6 == 0) {
      return;
    }
    puVar2 = ((undefined4 *)camry_host_ptr((uint32_t)((uint)uVar7 * 0xc + *(int *)((int)((ulonglong)uVar5 >> 0x20) + 0x29c))));
    if ((param_2 == puVar2[1]) && (param_3 == *(char *)(puVar2 + 2))) {
      bVar3 = true;
      local_34 = 1;
      uStack_30 = *puVar2;
      uStack_28 = *param_5;
      uStack_24 = param_5[1];
      uStack_2c = param_4 & 0xff;
      FUN_00003460(*puVar1, camry_host_addr(&local_34));
    }
    else {
      bVar3 = false;
      if (bVar4) {
        return;
      }
    }
    uVar7 = uVar7 + 1;
    uVar6 = uVar6 - 1;
    bVar4 = bVar3;
  } while( true );
}



void FUN_000046ee(uint param_1,uint param_2,int param_3,char param_4)

{
  undefined4 *puVar1;
  undefined4 *puVar2;
  ushort uVar3;
  uint uVar4;
  uint local_c;
  undefined4 uStack_8;
  
  local_c = param_1 & 0xff;
  puVar1 = ((undefined4 *)camry_host_ptr((uint32_t)(PTR_PTR_00008940 + (param_2 & 0xffff) * 8)));
  uVar4 = (uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(puVar1) + 6))));
  uVar3 = *(ushort *)(puVar1 + 1);
  while( true ) {
    if (uVar4 == 0) {
      return;
    }
    puVar2 = ((undefined4 *)camry_host_ptr((uint32_t)(PTR_DAT_0000893c + (uint)uVar3 * 0xc)));
    if ((param_3 == puVar2[1]) && (param_4 == *(char *)(puVar2 + 2))) break;
    uVar3 = uVar3 + 1;
    uVar4 = uVar4 - 1;
  }
  uStack_8 = *puVar2;
  FUN_00003460(*puVar1, camry_host_addr(&local_c));
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
  
  bVar1 = (*((volatile uint8_t *)camry_host_ptr(0xfebe4aa3u))) != '\0';
  if (!bVar1) {
    (*((volatile uint8_t *)camry_host_ptr(0xfebe4aa3u))) = '\x01';
    (*((volatile uint8_t *)camry_host_ptr(0xfebe4aa2u))) = 2;
  }
  return bVar1;
}



undefined1 FUN_0000478e(void)

{
  return (*((volatile uint8_t *)camry_host_ptr(0xfebe4aa2u)));
}



undefined1 FUN_00004794(void)

{
  return (*((volatile uint8_t *)camry_host_ptr(0xfebe4aa3u)));
}



void FUN_0000479a(void)

{
  if ((*((volatile uint8_t *)camry_host_ptr(0xfebe4aa3u))) != '\0') {
    (*((volatile uint8_t *)camry_host_ptr(0xfebe4aa2u))) = 0;
    (*((volatile uint8_t *)camry_host_ptr(0xfebe4aa3u))) = '\0';
  }
  return;
}



/* Paired constant publisher: DAT_febf2aa2 = 2; and DAT_febf2aa3 = 0;; shape-classified from the
   canonical corpus. Target cells not yet named. */

void FUN_000047ac(void)

{
  (*((volatile uint8_t *)camry_host_ptr(0xfebe4aa2u))) = 2;
  (*((volatile uint8_t *)camry_host_ptr(0xfebe4aa3u))) = 0;
  return;
}



/* If2AADnonzeroreturn1unchanged; otherwisequeueaddress/length/tag,setresult2,pending1,return0. No
   rangevalidationhere;4874 validatesselectedregion later. Noterase. */

uint f33_boot_submit_region_crc_verification(uint address,uint length,uchar opaque_tag)

{
  bool bVar1;
  
  bVar1 = (*((volatile uint8_t *)camry_host_ptr(0xfebe4aadu))) != '\0';
  if (!bVar1) {
    (*((volatile uint8_t *)camry_host_ptr(0xfebe4aadu))) = '\x01';
    (*((volatile uint8_t *)camry_host_ptr(0xfebe4aacu))) = 2;
    (*((volatile uint32_t *)camry_host_ptr(0xfebe4aa4u))) = address;
    (*((volatile uint32_t *)camry_host_ptr(0xfebe4aa8u))) = length;
    (*((volatile uint8_t *)camry_host_ptr(0xfebe4aaeu))) = opaque_tag;
  }
  return (uint)bVar1;
}



/* Returnzero-extended2AAC result: initializer/admission2, worker0success/1failure. */

uint f33_boot_region_crc_result(void)

{
  return (uint)(*((volatile uint8_t *)camry_host_ptr(0xfebe4aacu)));
}



/* Returnzero-extended2AAD pendingbyte; notCRCresult. */

uint f33_boot_region_crc_pending(void)

{
  return (uint)(*((volatile uint8_t *)camry_host_ptr(0xfebe4aadu)));
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



/* WARNING: Inlined function: f33_boot_crc_descriptors */
/* Validate region selector through344C/3438;reject missingdescriptor/count. For each16-byte
   descriptor,require base andlength equal metadata-indirected words,then47EA streams words from
   thatbase withCRC seedFFFFFFFF andmust return0. Return0 on allpassing;FFFFFFFF on failure.
   Selectors0/1 cover CodeFlash and selector2 covers FEBF0000+FF0 with metadata atFEBF0FE0/4; each
   has one descriptor. This is not generic pointer or image validity outside those descriptors.
   Selectors0/1 cover CodeFlash; selector2 covers FEBF0000+FF0 with metadataFEBF0FE0/4. All three
   hold one record each;not generic pointer or image validity outside those descriptors. */

uint f33_boot_validate_crc_region(uint region)

{
  F33BootCrcDescriptor *pFVar1;
  F33BootCrcDescriptor *pFVar2;
  uint uVar3;
  int iVar4;
  uint uVar5;
  uint uVar6;
  
  if (region < 3) {
    pFVar2 = ((void *)camry_host_ptr((uint32_t)(f33_boot_regions[(short)region].crc_descriptors)));
  }
  else {
    pFVar2 = (F33BootCrcDescriptor *)0x0;
  }
  uVar3 = f33_boot_crc_descriptor_count(region);
  if ((uVar3 == 0) || ((uintptr_t)(pFVar2)==(uintptr_t)((F33BootCrcDescriptor *)0x0))) {
LAB_0000486c:
    uVar5 = 0xffffffff;
  }
  else {
    for (uVar6 = 0; uVar5 = 0, uVar6 < uVar3; uVar6 = uVar6 + 1) {
      pFVar1 = pFVar2 + uVar6;
      if (((pFVar1->base != *((uint32_t *)camry_host_ptr((uint32_t)(pFVar1->base_metadata)))) || (pFVar1->length != *((uint32_t *)camry_host_ptr((uint32_t)(pFVar1->length_metadata)))))
         || (iVar4 = FUN_000047ea(pFVar1->base,pFVar1->length,(int)0xffffffff), iVar4 != 0))
      goto LAB_0000486c;
    }
  }
  return uVar5;
}



/* Onlypending==1 and335Evalidrange call481A onselectedwholeregion, notrequestedsubrange.
   ThenunderFFFF PMRclear pending/start/length andsetresultbool(CRC!=0);opaque tagretained.
   Invalidorzerolength remains pending unchanged. Native zero-length CRC request stays pending
   unchanged while a separate stream completes; no hardware CRC acceptance claim. */

void f33_boot_advance_region_crc_verification(void)

{
  uint32_t puVar1;
  uint uVar2;
  undefined4 uVar3;
  uint local_c;
  
  puVar1 = 0xfebeb800u;
  if (((*((volatile uint8_t *)camry_host_ptr(0xfebe4aadu))) == '\x01') &&
     (uVar2 = f33_boot_select_region_for_range((*((volatile uint32_t *)camry_host_ptr(0xfebe4aa4u))),(*((volatile uint32_t *)camry_host_ptr(0xfebe4aa8u))),&local_c), uVar2 == 0)) {
    uVar2 = f33_boot_validate_crc_region(local_c);
    uVar3 = FUN_0000721e(0xffff);
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6d53))))) = 0;
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x6d58)))) = 0;
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x6d5c)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6d54))))) = uVar2 != 0;
    FUN_00007244(uVar3);
  }
  return;
}



/* SetCRCresult2 andpending0; retainaddress,length,opaque tag. Separatefrom47AC transition-job
   reset. */

void f33_boot_reset_region_crc_verification(void)

{
  (*((volatile uint8_t *)camry_host_ptr(0xfebe4aacu))) = 2;
  (*((volatile uint8_t *)camry_host_ptr(0xfebe4aadu))) = 0;
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



void FUN_00004914(void)

{
  (*((volatile uint8_t *)camry_host_ptr(0xfebe4ad0u))) = 0x6e;
  DAT_febf2ad2 = (undefined1)f33_boot_diagnostic_identifiers[(short)(ushort)(*((volatile uint8_t *)camry_host_ptr(0xfebe4ab0u)))].identifier
  ;
  DAT_febf2ad1 = (undefined1)
                 (f33_boot_diagnostic_identifiers[(short)(ushort)(*((volatile uint8_t *)camry_host_ptr(0xfebe4ab0u)))].identifier >> 8);
  f33_boot_response_submit('\x01',((undefined *)camry_host_ptr(0xfebe4ad0u)),3);
  return;
}



/* Resident SID2E: session2, security2, exact length3+8F14 descriptor payload and write flag2.0201
   requires2AB2=1 and schedules16-byte job then state2;0202 requires state2, schedules16-byte job,
   sets2B16=1/state0;0203 requires state0 and returns immediate6E/state1.4A9A waits asynchronous job
   completion and emits6E or72. */

void f33_boot_service_write_did(ushort request_length)

{
  int iVar1;
  char cVar2;
  uint32_t puVar3;
  F33BootInterruptEntry *pFVar4;
  undefined4 uVar5;
  ushort uVar6;
  int iVar7;
  short sVar8;
  int iVar9;
  bool bVar10;
  undefined1 uStack_1b;
  undefined1 auStack_1a [2];
  undefined1 auStack_18 [16];
  
  puVar3 = 0xfebeb800u;
  pFVar4 = f33_boot_interrupt_dispatch;
  FUN_000067b0(&uStack_1b,0x13);
  uVar6 = FUN_000052a6(auStack_1a,2);
  cVar2 = *(char *)&pFVar4[0x10b].handler;
  bVar10 = true;
  sVar8 = 0;
  iVar7 = 0;
  do {
    iVar9 = (short)iVar7 * 0xc;
    if ((uVar6 == (*((ushort *)camry_host_ptr((uint32_t)((int)camry_host_addr(pFVar4) + iVar9 + 0x87e))))) &&
       (((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(pFVar4) + iVar9 + 0x880)))) & 2) != 0)) {
      sVar8 = (*((short *)camry_host_ptr((uint32_t)((int)camry_host_addr(pFVar4) + iVar9 + 0x87c))));
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6d50))))) = (char)iVar7;
      bVar10 = false;
      break;
    }
    iVar1 = iVar7 + 1;
    iVar9 = iVar7 + -3;
    iVar7 = iVar1;
  } while (((iVar9 < 0) || (iVar1 < 0)));
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6cf2))))) != cVar2) {
    uVar5 = 0x7f;
    goto LAB_000049aa;
  }
  if (request_length < 4) {
LAB_000049c0:
    uVar5 = 0x13;
    goto LAB_000049aa;
  }
  if (bVar10) {
LAB_00004a0c:
    uVar5 = 0x31;
    goto LAB_000049aa;
  }
  if (request_length != (ushort)(sVar8 + 3U)) goto LAB_000049c0;
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6cf1))))) != '\x02') {
    uVar5 = 0x33;
    goto LAB_000049aa;
  }
  if (uVar6 < 0x201) goto LAB_00004a0c;
  if (uVar6 == 0x201) {
    bVar10 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6d4e))))) == '\x01';
LAB_00004a04:
    if (!bVar10) {
LAB_00004a06:
      uVar5 = 0x22;
LAB_000049aa:
      FUN_00004900(uVar5);
      return;
    }
  }
  else {
    if (uVar6 < 0x203) {
      bVar10 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6d4e))))) == '\x02';
      goto LAB_00004a04;
    }
    if (uVar6 != 0x203) goto LAB_00004a0c;
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6d4e))))) != '\0') goto LAB_00004a06;
  }
  if (uVar6 < 0x201) {
LAB_00004a80:
    uVar5 = 0x31;
  }
  else {
    if (uVar6 == 0x201) {
      iVar7 = FUN_00006d5e(((undefined4 *)camry_host_ptr((uint32_t)((int)camry_host_addr(pFVar4) + (short)(ushort)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6d50))))) * 0xc + 0x878))), camry_host_addr(auStack_18));
      if (iVar7 == 0) {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6d4e))))) = 2;
LAB_00004a7c:
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6d4f))))) = 1;
        return;
      }
    }
    else {
      if (0x202 < uVar6) {
        if (uVar6 == 0x203) {
          FUN_00004914();
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6d4e))))) = 1;
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6d4f))))) = 0;
          return;
        }
        goto LAB_00004a80;
      }
      iVar7 = FUN_00006d5e(((undefined4 *)camry_host_ptr((uint32_t)((int)camry_host_addr(pFVar4) + (short)(ushort)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6d50))))) * 0xc + 0x878))), camry_host_addr(auStack_18));
      if (iVar7 == 0) {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6cea))))) = 1;
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6d4e))))) = 0;
        goto LAB_00004a7c;
      }
    }
    uVar5 = 0x72;
  }
  FUN_00004900(uVar5);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6d4f))))) = 0;
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
  
  puVar1 = 0xfebeb800u;
  if ((*((volatile uint8_t *)camry_host_ptr(0xfebe4ab1u))) != '\x01') {
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
  
  puVar1 = 0xfebeb800u;
  if ((*((char *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr(0xfebe4ab4u))) + 1)))) == (char)((*((volatile uint8_t *)camry_host_ptr(0xfebe4ac8u))) + '\x01')) {
    (*((volatile uint8_t *)camry_host_ptr(0xfebe4ac7u))) = 0;
    uVar3 = 0;
  }
  else if (((*((volatile uint8_t *)camry_host_ptr(0xfebe4ac9u))) == '\x01') && ((*((char *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr(0xfebe4ab4u))) + 1)))) == (*((volatile uint8_t *)camry_host_ptr(0xfebe4ac8u))))) {
    puVar1 = 0xfebeb800u;
    uVar2 = FUN_00007262((*((volatile uint8_t *)camry_host_ptr(0xfebe4ac7u))));
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6d39))))) = uVar2;
    uVar3 = 1;
  }
  else {
    (*((volatile uint8_t *)camry_host_ptr(0xfebe4ac7u))) = 0;
    uVar3 = 2;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6d37))))) = 1;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6d38))))) = (*((undefined1 *)camry_host_ptr((uint32_t)(*(int *)(puVar1 + -0x6d4c) + 1))));
  return uVar3;
}



void FUN_00004b38(uchar param_1)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  f33_boot_negative_response('6',param_1);
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6ced))))) != '\0') {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6ced))))) = 0xf;
  }
  return;
}



void FUN_00004b5a(void)

{
  (*((volatile uint8_t *)camry_host_ptr(0xfebe4ad0u))) = 0x76;
  DAT_febf2ad1 = (*((volatile uint8_t *)camry_host_ptr(0xfebe4ac8u)));
  f33_boot_response_submit('\x01',((undefined *)camry_host_ptr(0xfebe4ad0u)),2);
  return;
}



/* Consume the full low16 request length forwarded from4DBA. Require session2, nonzero remaining,
   sequence admission and payload1..1024, full1024 unless final. Decrement remaining at admission;
   classify RAM versus CodeFlash, stage source/length and transform-or-ready state. Foreground4F50
   consumes later; failures request queue cancellation. Static exact-image instruction/dataflow
   contract; no complete transfer execution claim. */

void f33_boot_admit_program_transfer_chunk(ushort request_length)

{
  uchar *source;
  uint32_t puVar1;
  F33BootInterruptEntry *pFVar2;
  uint length;
  undefined4 uVar3;
  int iVar4;
  ushort length_00;
  uint uVar5;
  uchar uStack_d;
  
  puVar1 = 0xfebeb800u;
  pFVar2 = f33_boot_interrupt_dispatch;
  uVar3 = camry_host_addr(FUN_000067d0());
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x6d4c)))) = uVar3;
  iVar4 = FUN_00004ae2();
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6cf2))))) != (*((char *)camry_host_ptr((uint32_t)((int)&pFVar2[0x10b].handler + 3))))) {
    f33_boot_request_flash_worker_cancel();
    uVar3 = 0x7f;
    goto LAB_00004ba8;
  }
  length_00 = request_length - 2;
  uVar5 = (uint)length_00;
  if (request_length < 3) goto LAB_00004c1a;
  length = (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x6d44))));
  if (length == 0) {
    f33_boot_request_flash_worker_cancel();
    uVar3 = 0x24;
    goto LAB_00004ba8;
  }
  if (length < uVar5) {
    f33_boot_request_flash_worker_cancel();
    uVar3 = 0x71;
    goto LAB_00004ba8;
  }
  if ((iVar4 == 2) || (iVar4 == 3)) {
    f33_boot_request_flash_worker_cancel();
    uVar3 = 0x73;
    goto LAB_00004ba8;
  }
  if (iVar4 != 0) {
    FUN_00004b5a();
    return;
  }
  if (length == uVar5) {
    if (0x400 < uVar5) goto LAB_00004c0a;
    if (request_length < 0x403) goto LAB_00004c24;
  }
  else {
    if (uVar5 != 0x400) {
LAB_00004c0a:
      f33_boot_request_flash_worker_cancel();
      uVar3 = 0x31;
      goto LAB_00004ba8;
    }
    if (request_length == 0x402) {
LAB_00004c24:
      f33_boot_classify_service_range((*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x6d48)))),length,'\0',&uStack_d);
      (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x6d44)))) = (*((int *)camry_host_ptr((uint32_t)(puVar1 + -0x6d44)))) - uVar5;
      if (uStack_d == '\0') {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6d36))))) = 2;
        f33_boot_set_flash_worker_pause('\0');
      }
      else {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6d36))))) = 1;
      }
      (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x6d3c)))) = length_00;
      source = ((uchar *)camry_host_ptr((uint32_t)(*(int *)(puVar1 + -0x6d4c) + 2)));
      *(uchar **)(puVar1 + -0x6d40) = source;
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6ceb))))) != '\0') {
        uVar5 = f33_boot_block_transform_submit(length_00,source,source);
        if (uVar5 != 0) {
          FUN_00004b38(0x72);
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6d3a))))) = 0;
          return;
        }
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6d3a))))) = 1;
        return;
      }
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6d35))))) = 1;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6d3a))))) = 2;
      return;
    }
  }
LAB_00004c1a:
  f33_boot_request_flash_worker_cancel();
  uVar3 = 0x13;
LAB_00004ba8:
  FUN_00004b38(uVar3);
  return;
}



/* Consume low16 request length from4DBA with the same payload/sequence shape, but stage comparison
   rather than direct transfer. Preserve payload length in R8 for6C6C; optional block transform
   precedes comparison. Foreground comparison and timer response are separate completion owners.
   Static exact-image instruction/dataflow contract; no complete transfer execution claim. */

void f33_boot_admit_compare_transfer_chunk(ushort request_length)

{
  uchar *left;
  undefined1 uVar1;
  uint uVar2;
  uint32_t puVar3;
  F33BootInterruptEntry *pFVar4;
  ushort length;
  uint uVar5;
  undefined4 uVar6;
  int iVar7;
  
  puVar3 = 0xfebeb800u;
  pFVar4 = f33_boot_interrupt_dispatch;
  uVar6 = camry_host_addr(FUN_000067d0());
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar3 + -0x6d4c)))) = uVar6;
  iVar7 = FUN_00004ae2();
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6cf2))))) != (*((char *)camry_host_ptr((uint32_t)((int)&pFVar4[0x10b].handler + 3))))) {
    uVar6 = 0x7f;
    goto LAB_00004cca;
  }
  length = request_length - 2;
  uVar5 = (uint)length;
  if (request_length < 3) goto LAB_00004d2a;
  uVar2 = (*((uint *)camry_host_ptr((uint32_t)(puVar3 + -0x6d44))));
  if (uVar2 == 0) {
    uVar6 = 0x24;
    goto LAB_00004cca;
  }
  if (uVar2 < uVar5) {
    uVar6 = 0x71;
    goto LAB_00004cca;
  }
  if ((iVar7 == 2) || (iVar7 == 3)) {
    uVar6 = 0x73;
    goto LAB_00004cca;
  }
  if (iVar7 != 0) {
    FUN_00004b5a();
    return;
  }
  if (uVar2 == uVar5) {
    if (0x400 < uVar5) goto LAB_00004d1e;
    if (request_length < 0x403) goto LAB_00004d30;
  }
  else {
    if (uVar5 != 0x400) {
LAB_00004d1e:
      uVar6 = 0x31;
      goto LAB_00004cca;
    }
    if (request_length == 0x402) {
LAB_00004d30:
      (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x6d3c)))) = length;
      left = ((uchar *)camry_host_ptr((uint32_t)(*(int *)(puVar3 + -0x6d4c) + 2)));
      *(uchar **)(puVar3 + -0x6d40) = left;
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6ceb))))) == '\0') {
        if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6ce9))))) != '\x01' && (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6ce9))))) != '\x02') {
          return;
        }
        uVar5 = f33_boot_compare_submit(left,*(uchar **)(puVar3 + -0x6d48),uVar5);
        if (uVar5 != 0) goto LAB_00004d6e;
        uVar1 = 2;
      }
      else {
        uVar5 = f33_boot_block_transform_submit(length,left,left);
        if (uVar5 != 0) {
LAB_00004d6e:
          FUN_00004b38(0x72);
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6d3a))))) = 0;
          return;
        }
        uVar1 = 1;
      }
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6d3a))))) = uVar1;
      return;
    }
  }
LAB_00004d2a:
  uVar6 = 0x13;
LAB_00004cca:
  FUN_00004b38(uVar6);
  return;
}



/* Use request length even in unsupported download state: wrong session gives7F; otherwise length<3
   gives13, else24. Reply through4B38; no input consumption. Static exact-image instruction/dataflow
   contract; no complete transfer execution claim. */

void f33_boot_reject_transfer_state(ushort request_length)

{
  undefined4 uVar1;
  
  if ((*((volatile uint8_t *)camry_host_ptr(0xfebe4b0eu))) == f33_boot_service_session_constants[7]) {
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
  if (((*((volatile uint8_t *)camry_host_ptr(0xfebe4b13u))) == '\x01') || (uVar1 = '\n', (*((volatile uint8_t *)camry_host_ptr(0xfebe4b13u))) == '\t')) {
    (*((volatile uint8_t *)camry_host_ptr(0xfebe4b13u))) = uVar1;
  }
  if ((*((volatile uint8_t *)camry_host_ptr(0xfebe4b13u))) == '\x02') {
    f33_boot_admit_program_transfer_chunk(request_length);
  }
  else if ((*((volatile uint8_t *)camry_host_ptr(0xfebe4b13u))) == '\n') {
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
  
  puVar3 = 0xfebeb800u;
  if ((*((volatile uint8_t *)camry_host_ptr(0xfebe4b17u))) != '\x01' && (*((volatile uint8_t *)camry_host_ptr(0xfebe4b17u))) != '\x02') {
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
  
  puVar3 = 0xfebeb800u;
  if ((*((volatile uint8_t *)camry_host_ptr(0xfebe4b17u))) != '\x01' && (*((volatile uint8_t *)camry_host_ptr(0xfebe4b17u))) != '\x02') {
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
  if (((*((volatile uint8_t *)camry_host_ptr(0xfebe4ac6u))) != '\0') && ((*((volatile uint8_t *)camry_host_ptr(0xfebe4bbcu))) != '\x01')) {
    if ((*((volatile uint8_t *)camry_host_ptr(0xfebe4b13u))) == '\x02') {
      FUN_00004df2();
    }
    else if ((*((volatile uint8_t *)camry_host_ptr(0xfebe4b13u))) == '\n') {
      FUN_00004e92();
    }
    else {
      (*((volatile uint8_t *)camry_host_ptr(0xfebe4ac6u))) = '\0';
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
  
  puVar1 = 0xfebeb800u;
  if (((*((volatile uint8_t *)camry_host_ptr(0xfebe4b17u))) == '\x01' || (*((volatile uint8_t *)camry_host_ptr(0xfebe4b17u))) == '\x02') &&
     ((*((volatile uint8_t *)camry_host_ptr(0xfebe4acbu))) == '\x01')) {
    uVar2 = (uint)DAT_febf2ac4;
    if ((*((volatile uint8_t *)camry_host_ptr(0xfebe4acau))) == '\x02') {
      f33_boot_append_program_input(((uchar *)camry_host_ptr((uint32_t)(DAT_febf2ac0))), DAT_febf2ac4);
    }
    else {
      FUN_0000153a(((undefined1 *)camry_host_ptr((uint32_t)(DAT_febf2ac0))), ((undefined1 *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr(0xfebe4ab8u)))))), uVar2);
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6d35))))) = 0;
    (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x6d48)))) = (*((int *)camry_host_ptr((uint32_t)(puVar1 + -0x6d48)))) + uVar2;
  }
  return;
}



undefined4 FUN_00004f98(void)

{
  return (*((volatile uint32_t *)camry_host_ptr(0xfebe4abcu)));
}



/* Constant-block fill: 7 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_4f9e(void)

{
  DAT_febf2ac6 = 0;
  DAT_febf2ac7 = 0;
  DAT_febf2ac8 = 0;
  (*((volatile uint32_t *)camry_host_ptr(0xfebe4ab8u))) = (*((volatile uint32_t *)camry_host_ptr(0xfebe4b00u)));
  DAT_febf2ac9 = 0;
  DAT_febf2acb = 0;
  DAT_febf2abc = (*((volatile uint32_t *)camry_host_ptr(0xfebe4b04u)));
  return;
}



void FUN_00004fba(uchar param_1)

{
  f33_boot_negative_response('>',param_1);
  return;
}



void FUN_00004fce(void)

{
  (*((volatile uint8_t *)camry_host_ptr(0xfebe4ad0u))) = 0x7e;
  DAT_febf2ad1 = (*((volatile uint8_t *)camry_host_ptr(0xfebe4accu))) & 0x7f;
  f33_boot_response_submit((*((volatile uint8_t *)camry_host_ptr(0xfebe4accu))) >> 7 ^ 1,((undefined *)camry_host_ptr(0xfebe4ad0u)),2);
  return;
}



/* Resident SID3E: sessions1/2/3, length2, subfunction00 or80 only. Form7E/00 through4FCE; original
   bit7 controls positive-response suppression. Functional3E80 has a separate request-admission
   special case while another request is receiving. */

void f33_boot_service_tester_present(ushort request_length)

{
  int iVar1;
  int iVar2;
  uint32_t puVar3;
  F33BootInterruptEntry *pFVar4;
  undefined4 uVar5;
  int iVar6;
  undefined1 uStack_e;
  char cStack_d;
  
  puVar3 = 0xfebeb800u;
  pFVar4 = f33_boot_interrupt_dispatch;
  uStack_e = 0;
  cStack_d = '\0';
  FUN_000067b0(&uStack_e,2);
  iVar6 = 0;
  do {
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6cf2))))) == (*((char *)camry_host_ptr((uint32_t)((int)&pFVar4[0x10c].eiic + iVar6 + 1))))) {
      if (1 < request_length) {
        if ((cStack_d != '\0') && (((int8_t)cStack_d) != -0x80)) {
          uVar5 = 0x12;
          goto LAB_0000502c;
        }
        if (request_length == 2) {
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6d34))))) = cStack_d;
          FUN_00004fce();
          return;
        }
      }
      uVar5 = 0x13;
      goto LAB_0000502c;
    }
    iVar2 = iVar6 + 1;
    iVar1 = iVar6 + -2;
    iVar6 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  uVar5 = 0x7f;
LAB_0000502c:
  FUN_00004fba(uVar5);
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
  (*((volatile uint8_t *)camry_host_ptr(0xfebe4b0eu))) = '\x01';
  (*((volatile uint8_t *)camry_host_ptr(0xfebe4b0fu))) = '\x01';
  (*((volatile uint8_t *)camry_host_ptr(0xfebe4b13u))) = '\0';
  (*((volatile uint8_t *)camry_host_ptr(0xfebe4b10u))) = 0;
  (*((volatile uint8_t *)camry_host_ptr(0xfebe4b11u))) = 0;
  (*((volatile uint8_t *)camry_host_ptr(0xfebe4b12u))) = 0;
  (*((volatile uint8_t *)camry_host_ptr(0xfebe4b14u))) = 2;
  (*((volatile uint8_t *)camry_host_ptr(0xfebe4b15u))) = 0;
  (*((volatile uint8_t *)camry_host_ptr(0xfebe4b16u))) = 0;
  (*((volatile uint8_t *)camry_host_ptr(0xfebe4b17u))) = '\0';
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
  (*((volatile uint8_t *)camry_host_ptr(0xfebe4b0eu))) = '\x02';
  (*((volatile uint8_t *)camry_host_ptr(0xfebe4b13u))) = '\0';
  (*((volatile uint8_t *)camry_host_ptr(0xfebe4b10u))) = 0;
  (*((volatile uint8_t *)camry_host_ptr(0xfebe4b11u))) = 0;
  (*((volatile uint8_t *)camry_host_ptr(0xfebe4b12u))) = 0;
  (*((volatile uint8_t *)camry_host_ptr(0xfebe4b14u))) = 2;
  (*((volatile uint8_t *)camry_host_ptr(0xfebe4b15u))) = 0;
  (*((volatile uint8_t *)camry_host_ptr(0xfebe4b16u))) = 0;
  (*((volatile uint8_t *)camry_host_ptr(0xfebe4b17u))) = '\0';
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
  (*((volatile uint8_t *)camry_host_ptr(0xfebe4b10u))) = 1;
  return;
}



void FUN_00005160(void)

{
  char cVar1;
  bool bVar2;
  uint32_t puVar3;
  int local_c;
  
  cVar1 = DAT_0000bff8;
  puVar3 = 0xfebeb800u;
  FUN_00001514(camry_host_addr(&local_c), 1);
  if ((local_c == 0xff) || (((int8_t)DAT_000ffdb0) == -1)) {
    bVar2 = cVar1 != -1;
  }
  else {
    bVar2 = true;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6ceb))))) = bVar2;
  return;
}



void FUN_0000519c(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
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



/* Prioritymaskedpublicationof2B0Efollowed55FCsecurityhandshakereset. */

undefined4 f33_boot_session_publish(uchar session)

{
  uint32_t puVar1;
  undefined4 uVar2;
  
  puVar1 = 0xfebeb800u;
  uVar2 = FUN_0000721e(0xffff);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6cf2))))) = session;
  f33_boot_security_invalidate_handshake();
  FUN_00007244(uVar2);
  return uVar2;
}



/* Forms7F,SID,NRC;mode0functionalelse2physical;submitslength3. Native functional routine rejection
   constructs7F3111 and passes suppression mode0; stops at674A before response processing. */

void f33_boot_negative_response(uchar sid,uchar nrc)

{
  uchar mode;
  
  (*((volatile uint8_t *)camry_host_ptr(0xfebe4ad0u))) = 0x7f;
  if ((*((volatile uint8_t *)camry_host_ptr(0xfebe50bfu))) == '\0') {
    mode = '\0';
  }
  else {
    mode = '\x02';
  }
  DAT_febf2ad1 = sid;
  DAT_febf2ad2 = nrc;
  f33_boot_response_submit(mode,((undefined *)camry_host_ptr(0xfebe4ad0u)),3);
  return;
}



/* ROM8E54twentyentryresident-onlyservice/address-modedispatch;unmatchedormaskdenied\u219251FA(SID,11).NoapplicationDCMtable.
   ROM8E54twentyentryresident-onlyservice/address-modedispatch;unmatchedormaskdenied→51FA(SID,11).NoapplicationDCMtable.
   Native ROM dispatch queues programming-session transition and separately rejects functional
   routine access before handler execution. No completed session/hardware transport claim. */

void f33_boot_dispatch_diagnostic_service(uchar sid,ushort request_length)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = 0;
  do {
    if (sid == f33_boot_diagnostic_services[iVar3].sid) {
      if (((uint)f33_boot_diagnostic_services[iVar3].address_mode_mask &
          1 << ((*((volatile uint8_t *)camry_host_ptr(0xfebe50bfu))) & 0x1f)) != 0) {
        (*(int (*)())f33_boot_diagnostic_services[iVar3].handler)(request_length);
        return;
      }
      break;
    }
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -0x13;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  f33_boot_negative_response(sid,'\x11');
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
  return (*((volatile uint8_t *)camry_host_ptr(0xfebe4b12u))) != '\x01';
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
  
  uVar3 = (*((volatile uint8_t *)camry_host_ptr(0xfebe4b54u)));
  (*((volatile uint8_t *)camry_host_ptr(0xfebe4ad0u))) = 0x67;
  DAT_febf2ad1 = (*((volatile uint8_t *)camry_host_ptr(0xfebe4b54u)));
  if (((*((volatile uint8_t *)camry_host_ptr(0xfebe4b54u))) & 1) == 0) {
    length = 2;
  }
  else {
    length = 0x12;
    iVar4 = 0;
    do {
      iVar2 = iVar4 + 1;
      iVar1 = iVar4 + -0xf;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4ad2u + (uint32_t)(iVar4) * 1u)))) = ((volatile uint8_t *)camry_host_ptr(0xfebe4b44u))[iVar4];
      iVar4 = iVar2;
    } while (((iVar1 < 0) || (iVar2 < 0)));
  }
  f33_boot_response_submit(uVar3 >> 7 ^ 1,((undefined *)camry_host_ptr(0xfebe4ad0u)),length);
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
  
  puVar5 = ((undefined *)camry_host_ptr(0xfebeb800u));
  puVar4 = ((undefined *)camry_host_ptr(0xfebeb800u));
  if ((*((volatile uint8_t *)camry_host_ptr(0xfebe4b55u))) == '\0') {
LAB_0000550c:
    uVar8 = '\x01';
  }
  else {
    if ((*((volatile uint8_t *)camry_host_ptr(0xfebe4b55u))) == '\x01') {
LAB_00005506:
      uVar6 = 0x24;
      uVar8 = (*((volatile uint8_t *)camry_host_ptr(0xfebe4b55u)));
      puVar4 = ((undefined *)camry_host_ptr(0xfebeb800u));
    }
    else {
      if (3 < (*((volatile uint8_t *)camry_host_ptr(0xfebe4b55u)))) goto LAB_0000550c;
      if (2 < (*((volatile uint8_t *)camry_host_ptr(0xfebe4b55u)))) goto LAB_00005506;
      if (request_length == 0x12) {
        puVar4 = ((undefined *)camry_host_ptr(0xfebeb800u));
        f33_boot_security_derive_expected_key
                  (f33_boot_security_client_material,((volatile uint8_t *)camry_host_ptr(0xfebe4b24u)),local_18);
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
      if ((int)((*((volatile uint8_t *)camry_host_ptr(0xfebe4b57u))) - 1) < 0) {
        uVar6 = 0x13;
        uVar8 = '\x01';
        puVar4 = ((undefined *)camry_host_ptr(0xfebeb800u));
        (*((volatile uint8_t *)camry_host_ptr(0xfebe4b57u))) = (*((volatile uint8_t *)camry_host_ptr(0xfebe4b57u))) + '\x01';
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



/* Resident SID27: session2; masked subfunctions1 and2 only. Both seed and key requests require18
   bytes.5328 stages16 client bytes and returns a16-byte challenge;53F2 derives and compares16
   expected key bytes. Success stores security2B0F=2 before response submission; handshake2B55=3
   follows its return. Bad key35; a second counted failure gives36 and raw-counter delay. Active
   delay rejects seed with37 before length validation; reseed and replay behavior are owned
   by5328/53F2. Success sets security2B0F=2/handshake2B55=3; bad key35, repeated failures36 plus
   raw-counter delay; active delay rejects seed with37. */

void f33_boot_service_security_access(ushort request_length)

{
  char cVar1;
  byte bVar2;
  uint32_t puVar3;
  F33BootInterruptEntry *pFVar4;
  undefined4 uVar5;
  int iVar6;
  byte bVar7;
  
  puVar3 = 0xfebeb800u;
  pFVar4 = f33_boot_interrupt_dispatch;
  iVar6 = camry_host_addr(FUN_000067d0());
  cVar1 = (*((char *)camry_host_ptr((uint32_t)((int)&pFVar4[0x10b].eiic + 1))));
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
          f33_boot_security_seed_request(request_length);
          return;
        }
        if (bVar7 == 2) {
          f33_boot_security_key_request(request_length);
          return;
        }
      }
      uVar5 = 0x12;
    }
  }
  else {
    uVar5 = 0x7f;
  }
  FUN_000052ca(uVar5);
  return;
}



/* Onlydelayflag1:unsigned32elapsed=(timer-start),cleardelayonlyelapsed>duration(strict);doesnotresetfailures,handshake,security,buffers.Timer51ACownsperiodiccall;noexplicitseconds.
    */

void f33_boot_security_delay_progress(void)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  if (((*((volatile uint8_t *)camry_host_ptr(0xfebe4b56u))) == '\x01') &&
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
  (*((volatile uint8_t *)camry_host_ptr(0xfebe4b56u))) = '\0';
  return;
}



void FUN_00005630(uchar param_1)

{
  f33_boot_negative_response('1',param_1);
  return;
}



void FUN_00005644(void)

{
  (*((volatile uint8_t *)camry_host_ptr(0xfebe4ad0u))) = 0x71;
  DAT_febf2ad1 = (*((volatile uint8_t *)camry_host_ptr(0xfebe4b66u))) & 0x7f;
  DAT_febf2ad2 = (undefined1)((ushort)(*((volatile uint16_t *)camry_host_ptr(0xfebe4b64u))) >> 8);
  DAT_febf2ad3 = (undefined1)(*((volatile uint16_t *)camry_host_ptr(0xfebe4b64u)));
  f33_boot_response_submit((*((volatile uint8_t *)camry_host_ptr(0xfebe4b66u))) >> 7 ^ 1,((undefined *)camry_host_ptr(0xfebe4ad0u)),(*((volatile uint8_t *)camry_host_ptr(0xfebe4b67u))) + 4);
  return;
}



/* Resident SID31: session2, security2, masked start subfunction1, exact length4+configured
   options.8F44 configures10F0/10F1/10F2/10F3/FF00; all except10F3 require45 00 plus BE32
   address/length. Range-kind gates32D2/3318 precede CRC-verification47BA or queued operation41E0.
   Timer5C06 owns deferred completion;10F3 immediately sets alternate download state8 and
   responds71. */

void f33_boot_service_routine_control(ushort request_length)

{
  int iVar1;
  undefined4 *puVar2;
  int iVar3;
  bool bVar4;
  int iVar5;
  undefined *puVar6;
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
  uchar local_2c;
  uchar auStack_2b [2];
  byte bStack_29;
  char local_28 [8];
  undefined1 auStack_20 [8];
  
  puVar7 = 0xfebeb800u;
  pFVar8 = f33_boot_interrupt_dispatch;
  bStack_29 = 0;
  auStack_2b[1] = 0;
  iVar5 = 0;
  do {
    local_28[iVar5] = '\0';
    iVar3 = iVar5 + 1;
    iVar1 = iVar5 + -1;
    iVar5 = iVar3;
  } while (((iVar1 < 0) || (iVar3 < 0)));
  iVar5 = 0;
  do {
    local_28[iVar5 + 2] = '\0';
    iVar3 = iVar5 + 1;
    iVar1 = iVar5 + -9;
    iVar5 = iVar3;
  } while (((iVar1 < 0) || (iVar3 < 0)));
  FUN_000067b0(auStack_2b + 1,0xe);
  uVar10 = FUN_000052a6(local_28,2);
  bVar4 = true;
  uVar12 = 0;
  uVar14 = (uint)uVar10;
  auStack_2b[0] = '\x01';
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
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(-0x6cf2))))) != (*((char *)camry_host_ptr((uint32_t)((int)&pFVar8[0x10b].handler + 1))))) {
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
      if ((bStack_29 & 0x7f) != 1) {
        uVar9 = 0x12;
        goto LAB_00005706;
      }
      if (request_length != (ushort)(uVar12 + 4)) goto LAB_0000573c;
      start = 0;
      puVar6 = ((undefined *)camry_host_ptr((uint32_t)(uVar14 - 0x10f0)));
      length = 0;
      if ((uintptr_t)(puVar6)<(uintptr_t)(((undefined *)camry_host_ptr((uint32_t)(0x2))))) {
        if ((local_28[2] == 'E') && (local_28[3] == '\0')) {
          start = FUN_000052a6(local_28 + 4,4);
          length = FUN_000052a6(auStack_20,4);
          uVar11 = f33_boot_classify_service_range(start,length,'\x04',&local_2c);
          if ((uVar11 == 0) &&
             (((local_2c != '\0' && (local_2c == '\x01')) &&
              (uVar11 = f33_boot_service_range_completion_selector(start,length,'\x04',auStack_2b),
              uVar11 == 0)))) {
            uVar11 = f33_boot_submit_region_crc_verification(start,length,local_2c);
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
      else if ((uintptr_t)(puVar6)==(uintptr_t)(((undefined *)camry_host_ptr((uint32_t)(0x2))))) {
        if ((local_28[2] == 'E') && (local_28[3] == '\0')) {
          start = FUN_000052a6(local_28 + 4,4);
          length = FUN_000052a6(auStack_20,4);
          uVar11 = f33_boot_classify_service_range(start,length,'\x04',&local_2c);
          if ((uVar11 == 0) &&
             ((local_2c == '\0' &&
              (uVar11 = f33_boot_service_range_completion_selector(start,length,'\x04',auStack_2b),
              uVar11 == 0)))) {
            uVar11 = f33_boot_submit_region_crc_verification(start,length,local_2c);
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
        if ((uintptr_t)(puVar6)==(uintptr_t)(((undefined *)camry_host_ptr((uint32_t)(0x3))))) {
LAB_000058da:
          (*((ushort *)camry_host_ptr((uint32_t)(puVar7 + -0x6c9c)))) = uVar10;
          (*((uint *)camry_host_ptr((uint32_t)(puVar7 + -0x6ca8)))) = start;
          puVar6 = ((undefined *)camry_host_ptr((uint32_t)(uVar14 - 0x10f0)));
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(-0x6c9a))))) = bStack_29;
          (*((uint *)camry_host_ptr((uint32_t)(puVar7 + -0x6ca4)))) = length;
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(-0x6c99))))) = uVar13;
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(-0x6c98))))) = auStack_2b[0];
          if ((uintptr_t)(puVar6)<(uintptr_t)(((undefined *)camry_host_ptr((uint32_t)(0x3))))) {
            (*((undefined4 *)camry_host_ptr((uint32_t)(puVar7 + -0x6ca0)))) = unaff_r25;
            (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(-0x6c97))))) = 1;
            return;
          }
          if ((uintptr_t)(puVar6)==(uintptr_t)(((undefined *)camry_host_ptr((uint32_t)(0x3))))) {
            (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(-0x6ced))))) = 8;
            FUN_00005644();
          }
          else {
            if ((uintptr_t)(puVar6)==(uintptr_t)(((undefined *)camry_host_ptr(0xee10u)))) {
              (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(-0x6c97))))) = 1;
              return;
            }
            FUN_00005630(0x31);
          }
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(-0x6c97))))) = 0;
          return;
        }
        if ((((uintptr_t)(puVar6)==(uintptr_t)(((undefined *)camry_host_ptr(0xee10u)))) && (local_28[2] == 'E')) && (local_28[3] == '\0')) {
          start = FUN_000052a6(local_28 + 4,4);
          length = FUN_000052a6(auStack_20,4);
          uVar11 = f33_boot_classify_service_range(start,length,'\x01',&local_2c);
          if (((uVar11 == 0) && (local_2c == '\0')) &&
             (uVar11 = f33_boot_service_range_completion_selector(start,length,'\x01',auStack_2b),
             uVar11 == 0)) {
            if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(-0x6cef))))) == '\x01') || (((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(-0x6cef)))))) == -0x7f)) &&
               (uVar11 = f33_boot_submit_block_erase(start,length), uVar11 == 0)) {
              (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(-0x6cef))))) = 0x81;
              (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(-0x6ce9))))) = 2;
              f33_boot_set_flash_worker_pause('\x01');
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
  FUN_00005630(uVar9);
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
  
  puVar3 = 0xfebeb800u;
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
  
  puVar3 = 0xfebeb800u;
  if ((*((volatile uint8_t *)camry_host_ptr(0xfebe4b17u))) != '\x02') {
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
  
  puVar1 = 0xfebeb800u;
  if ((*((volatile uint8_t *)camry_host_ptr(0xfebe4b17u))) != '\x02') {
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
  
  if (((*((volatile uint8_t *)camry_host_ptr(0xfebe4b69u))) != '\0') && ((*((volatile uint8_t *)camry_host_ptr(0xfebe4bbcu))) != '\x01')) {
    puVar1 = ((undefined *)camry_host_ptr((uint32_t)((*((volatile uint16_t *)camry_host_ptr(0xfebe4b64u))) - 0x10f0)));
    if ((uintptr_t)(puVar1)<(uintptr_t)(((undefined *)camry_host_ptr((uint32_t)(0x2))))) {
      FUN_00005936();
    }
    else if ((uintptr_t)(puVar1)==(uintptr_t)(((undefined *)camry_host_ptr((uint32_t)(0x2))))) {
      FUN_00005a04();
    }
    else if ((uintptr_t)(puVar1)==(uintptr_t)(((undefined *)camry_host_ptr(0xee10u)))) {
      FUN_00005b70();
    }
    else {
      (*((volatile uint8_t *)camry_host_ptr(0xfebe4b69u))) = '\0';
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
  puVar1 = 0xfebeb800u;
  f33_boot_negative_response('7',param_1);
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6ced))))) != '\0') {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6ced))))) = 0xf;
  }
  return;
}



void FUN_00005c76(void)

{
  (*((volatile uint8_t *)camry_host_ptr(0xfebe4ad0u))) = 0x77;
  f33_boot_response_submit('\x01',((undefined *)camry_host_ptr(0xfebe4ad0u)),1);
  return;
}



/* Resident SID37: session2, download state2 or10, remaining transfer bytes0 and exact length1.
   Optionally end block crypto; clear operation class2B17, address2B00, length2B04 and download
   state2B13; respond77. Incomplete transfer rejects24 and may request4266 cancellation. No call
   to426E final-input setter is present. */

void f33_boot_service_transfer_exit(ushort request_length)

{
  uint32_t puVar1;
  F33BootInterruptEntry *pFVar2;
  undefined4 uVar3;
  int iVar4;
  undefined1 uStack_9;
  
  puVar1 = 0xfebeb800u;
  pFVar2 = f33_boot_interrupt_dispatch;
  FUN_000067b0(&uStack_9,1);
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6cf2))))) != (char)pFVar2[0x10c].eiic) {
    uVar3 = 0x7f;
    goto LAB_00005cb2;
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6ced))))) == '\x02') {
    iVar4 = FUN_00004f98();
    if (iVar4 == 0) {
LAB_00005cfc:
      if (request_length == 1) {
        if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6ceb))))) != '\0') {
          f33_boot_transfer_crypto_clear();
        }
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6ce9))))) = 0;
        (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x6d00)))) = 0;
        (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x6cfc)))) = 0;
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6ced))))) = 0;
        FUN_00005c76();
        return;
      }
      uVar3 = 0x13;
      goto LAB_00005cb2;
    }
    if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6ce9))))) == '\x02') && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-27999))))) != '\0')) {
      f33_boot_request_flash_worker_cancel();
    }
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6ceb))))) != '\0') {
      f33_boot_transfer_crypto_clear();
    }
  }
  else if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6ced))))) == '\n') && (iVar4 = FUN_00004f98(), iVar4 == 0)) goto LAB_00005cfc;
  uVar3 = 0x24;
LAB_00005cb2:
  FUN_00005c54(uVar3);
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
  (*((volatile uint8_t *)camry_host_ptr(0xfebe4ad0u))) = 0x74;
  DAT_febf2ad2 = 4;
  DAT_febf2ad1 = 0x20;
  DAT_febf2ad3 = 2;
  f33_boot_response_submit('\x01',((undefined *)camry_host_ptr(0xfebe4ad0u)),4);
  return;
}



/* Resident SID34: session2/security2, exact13-byte custom request; DFI high nibble0, low
   nibble2B15, following format46, selector00/01 then00, BE32 address and size.32D2 classifies the
   range; normal state0 stages download1, alternate state8 stages9. Store2B00/2B04 and reset
   transfer counters; optional block crypto starts6BA8. Positive response is four bytes74 20 04 02.
    */

void f33_boot_service_request_download(ushort request_length)

{
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
  byte abStack_22 [10];
  undefined1 local_18 [4];
  
  puVar5 = 0xfebeb800u;
  pFVar6 = f33_boot_interrupt_dispatch;
  abStack_22[3] = '\0';
  abStack_22[2] = 0;
  abStack_22[1] = 0;
  iVar9 = 0;
  do {
    abStack_22[iVar9 + 4] = 0;
    iVar3 = iVar9 + 1;
    iVar2 = iVar9 + -5;
    iVar9 = iVar3;
  } while (((iVar2 < 0) || (iVar3 < 0)));
  iVar9 = 0;
  do {
    local_18[iVar9] = 0;
    iVar3 = iVar9 + 1;
    iVar2 = iVar9 + -3;
    iVar9 = iVar3;
  } while (((iVar2 < 0) || (iVar3 < 0)));
  FUN_000067b0(abStack_22 + 1,0xd);
  start = FUN_000052a6(abStack_22 + 6,4);
  length = FUN_000052a6(local_18,4);
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x6cf2))))) != (*((char *)camry_host_ptr((uint32_t)((int)&pFVar6[0x10b].handler + 2))))) {
    uVar7 = 0x7f;
    goto LAB_00005f34;
  }
  if (request_length < 5) {
LAB_00005ea8:
    uVar7 = 0x13;
    goto LAB_00005f34;
  }
  if (abStack_22[2] >> 4 == 0) {
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x6ced))))) == '\0') {
      if (((abStack_22[2] & 0xf) == (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x6ceb)))))) && (abStack_22[3] == 'F')) {
        if (request_length != 0xd) goto LAB_00005ea8;
        if ((((abStack_22[4] == '\0') || (abStack_22[4] == '\x01')) && (abStack_22[5] == '\0')) &&
           ((uVar8 = f33_boot_classify_service_range(start,length,'\0',abStack_22), uVar8 == 0 &&
            (abStack_22[0] < 2)))) {
          bVar1 = false;
          if (abStack_22[0] == 0) {
            if (abStack_22[4] == '\0') {
              iVar9 = FUN_000052be();
              if (((iVar9 == 0) && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x6cea))))) == '\x01')) &&
                 (uVar8 = f33_boot_submit_erase_program_stream(start,length), uVar8 == 0)) {
                (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x6ce9))))) = 2;
                f33_boot_set_flash_worker_pause('\x01');
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
          else if (abStack_22[4] == '\x01') {
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
      if (((abStack_22[2] & 0xf) == (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x6ceb)))))) && (abStack_22[3] == 'F')) {
        if (request_length != 0xd) goto LAB_00005ea8;
        if ((((abStack_22[4] == '\0') && (abStack_22[5] == '\0')) &&
            (uVar8 = f33_boot_classify_service_range(start,length,'\x05',abStack_22), uVar8 == 0))
           && ((abStack_22[0] == 0 && (abStack_22[4] == '\0')))) {
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
              f33_boot_transfer_crypto_initialize();
            }
            (*((uint *)camry_host_ptr((uint32_t)(puVar5 + -0x6d00)))) = start;
            (*((uint *)camry_host_ptr((uint32_t)(puVar5 + -0x6cfc)))) = length;
            f33_fill_constant_block_4f9e();
            f33_boot_download_positive_response();
            return;
          }
          goto LAB_00005f30;
        }
      }
    }
  }
  uVar7 = 0x31;
LAB_00005f34:
  FUN_00005d2c(uVar7);
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_5f3c(void)

{
  return;
}



/* FirmwarefillsconfiguredDIDpayloadbyteswithliteral0x21;keepscallerregisterABI(notanOEManumberread).
    */

uint f33_boot_read_did_fill_payload(uchar descriptor_index,ushort payload_offset)

{
  int iVar1;
  int iVar2;
  
  for (iVar2 = 0;
      iVar1 = iVar2 - (uint)f33_boot_diagnostic_identifiers[(short)(ushort)descriptor_index].
                            payload_length, ((iVar1 < 0) || (iVar2 < 0));
      iVar2 = iVar2 + 1) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4b6eu + (uint32_t)(iVar2 + (uint)payload_offset) * 1u)))) = 0x21;
  }
  return 0;
}



void FUN_00005f68(uchar param_1)

{
  f33_boot_negative_response('\"',param_1);
  return;
}



void FUN_00005f7c(void)

{
  uint uVar1;
  
  (*((volatile uint8_t *)camry_host_ptr(0xfebe4ad0u))) = 0x62;
  for (uVar1 = 0; uVar1 < (*((volatile uint16_t *)camry_host_ptr(0xfebe4b6cu))); uVar1 = uVar1 + 1 & 0xffff) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4ad1u + (uint32_t)(uVar1) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4b6eu + (uint32_t)(uVar1) * 1u))));
  }
  f33_boot_response_submit('\x01',((undefined *)camry_host_ptr(0xfebe4ad0u)),(*((volatile uint16_t *)camry_host_ptr(0xfebe4b6cu))) + 1);
  return;
}



/* Resident SID22: sessions1/2/3, length3 and a read-enabled match among four8F14 descriptors. Only
   configured F181 is readable: reply62/F181/02 followed by32 literal21 bytes generated by5F3E.
   Unknown or unreadable DID31; bad length13.5F3E receives descriptor index inr6 and payload offset
   inr7. */

void f33_boot_service_read_did(ushort request_length)

{
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
  undefined1 uStack_13;
  undefined1 auStack_12 [2];
  
  puVar6 = 0xfebeb800u;
  pFVar7 = f33_boot_interrupt_dispatch;
  FUN_000067b0(&uStack_13,3);
  uVar10 = FUN_000052a6(auStack_12,2);
  bVar3 = false;
  uVar10 = uVar10 & 0xffff;
  iVar8 = 0;
  do {
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6cf2))))) == (*((char *)camry_host_ptr((uint32_t)((int)&pFVar7[0x10c].handler + iVar8))))) {
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
              FUN_00005f7c();
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
      FUN_00005f68(uVar9);
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
  uVar5 = f33_boot_read_did_fill_payload((uchar)iVar8,payload_offset);
  goto LAB_0000604e;
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
  (*((volatile uint8_t *)camry_host_ptr(0xfebe4ad0u))) = 0x51;
  DAT_febf2ad1 = (*((volatile uint8_t *)camry_host_ptr(0xfebe4b9eu))) & 0x7f;
  f33_boot_response_submit((*((volatile uint8_t *)camry_host_ptr(0xfebe4b9eu))) >> 7 ^ 1,((undefined *)camry_host_ptr(0xfebe4ad0u)),2);
  return;
}



/* Resident SID11: session2, security2, length2, masked subfunction1 only. Stage51/subfunction
   positive response and request terminal action through67DA; successful response completion
   joins159E resident-state3/interrupt-disable halt path, not a proven physical ECU reset. */

void f33_boot_service_reset_request(ushort request_length)

{
  uint32_t puVar1;
  F33BootInterruptEntry *pFVar2;
  undefined4 uVar3;
  undefined1 uStack_a;
  byte bStack_9;
  
  puVar1 = 0xfebeb800u;
  pFVar2 = f33_boot_interrupt_dispatch;
  uStack_a = 0;
  bStack_9 = 0;
  FUN_000067b0(&uStack_a,2);
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6cf2))))) != (char)pFVar2[0x10b].eiic) {
    uVar3 = 0x7f;
    goto LAB_000060ee;
  }
  if (1 < request_length) {
    if ((bStack_9 & 0x7f) != 1) {
      uVar3 = 0x12;
      goto LAB_000060ee;
    }
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6cf1))))) != '\x02') {
      uVar3 = 0x33;
      goto LAB_000060ee;
    }
    if (request_length == 2) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6c62))))) = bStack_9;
      FUN_000067da();
      FUN_00006098();
      return;
    }
  }
  uVar3 = 0x13;
LAB_000060ee:
  FUN_00006084(uVar3);
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
  
  puVar1 = 0xfebeb800u;
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
  (*((volatile uint8_t *)camry_host_ptr(0xfebe4ad0u))) = 0x50;
  DAT_febf2ad1 = (undefined1)((*((volatile uint8_t *)camry_host_ptr(0xfebe4b9fu))) & 0x7f);
  if (((*((volatile uint8_t *)camry_host_ptr(0xfebe4b9fu))) & 0x7f) - 1 < 3) {
    DAT_febf2ad2 = 0;
    DAT_febf2ad3 = 0x32;
    DAT_febf2ad4 = 1;
    DAT_febf2ad5 = 0xf4;
  }
  f33_boot_response_submit((*((volatile uint8_t *)camry_host_ptr(0xfebe4b9fu))) >> 7 ^ 1,((undefined *)camry_host_ptr(0xfebe4ad0u)),6);
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
  
  puVar3 = 0xfebeb800u;
  if ((*((volatile uint8_t *)camry_host_ptr(0xfebe4ba3u))) == '\0') {
    return;
  }
  if ((*((volatile uint8_t *)camry_host_ptr(0xfebe4bbcu))) == '\x01') {
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
  puVar1 = 0xfebeb800u;
  if ((*((volatile uint8_t *)camry_host_ptr(0xfebe4ba2u))) == '\x01') {
    if (DAT_febf2bd1 == '\0') {
      puVar1 = 0xfebeb800u;
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
  (*((volatile uint8_t *)camry_host_ptr(0xfebe4ba1u))) = 1;
  f33_boot_session_publish('\x03');
  return;
}



undefined4 FUN_00006320(void)

{
  uint32_t puVar1;
  undefined4 uVar2;
  
  puVar1 = 0xfebeb800u;
  (*((volatile uint16_t *)camry_host_ptr(0xfebe4bb8u))) = 0;
  (*((volatile uint16_t *)camry_host_ptr(0xfebe50b8u))) = 0;
  (*((volatile uint16_t *)camry_host_ptr(0xfebe50bau))) = 0;
  (*((volatile uint8_t *)camry_host_ptr(0xfebe4bbau))) = '\0';
  (*((volatile uint8_t *)camry_host_ptr(0xfebe4bbbu))) = '\0';
  (*((volatile uint8_t *)camry_host_ptr(0xfebe4bbcu))) = '\0';
  uVar2 = FUN_00001d24();
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x6c4c)))) = uVar2;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6c43))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6c41))))) = 0;
  return uVar2;
}



void FUN_0000636e(void)

{
  (*((volatile uint16_t *)camry_host_ptr(0xfebe4bb8u))) = 0;
  return;
}



/* Admissionreturns0accepted/1busy/3tooLong.Maximum4096;writesr9capacity;storesSID/address-mode/channelandresetsappendindex.Seeexceptionalreceivingreplacementbehavior.
   Native real SF admission copies10 02 without padding, preserving the live capacity pointer; stops
   before timer capture/service dispatch. */

uint f33_boot_request_admit
               (ushort channel,F33BootPduInfo *first_chunk,ushort total_length,
               ushort *remaining_capacity)

{
  undefined1 uVar1;
  uchar uVar2;
  uint32_t puVar3;
  int iVar4;
  uchar *puVar5;
  uint uVar6;
  
  puVar3 = 0xfebeb800u;
  puVar5 = ((void *)camry_host_ptr((uint32_t)(first_chunk->data)));
  uVar2 = f33_boot_diagnostic_channels[channel].address_mode;
  uVar1 = (undefined1)first_chunk->length;
  if (total_length < 0x1001) {
    uVar6 = 0;
    *remaining_capacity = 0x1000;
  }
  else {
    uVar6 = 3;
  }
  if ((*((volatile uint8_t *)camry_host_ptr(0xfebe4bbau))) == '\x02') {
LAB_000063dc:
    uVar6 = 1;
  }
  else {
    iVar4 = FUN_0000526a(camry_host_addr(puVar5), uVar1, uVar2);
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6c46))))) == '\x01') {
      if (iVar4 == 1) goto LAB_000063dc;
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6c42))))) == '\x01') {
        ((void)((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6742)))))), f33_return_only_stub_5284());
      }
    }
    else if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6c41))))) == '\x01') goto LAB_000063dc;
    if (uVar6 == 0) {
      (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x6744)))) = channel;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6741))))) = uVar2;
      uVar2 = *puVar5;
      (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x6748)))) = 0;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6742))))) = uVar2;
      FUN_0000636e();
      if (iVar4 == 2) {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6c42))))) = 1;
        ((void)((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6742)))))), (void)(uVar1), f33_return_only_stub_5280());
      }
      else {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6c42))))) = 0;
      }
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6c46))))) = 1;
    }
  }
  return uVar6;
}



/* WARNING: This is an inlined function */
/* Appendinto4096-byteFEBF30C0using2BB8index.Preservesr8;inlineexactleafinGhidraso6464doesnotinventextraout_r8.
   Native real SF admission copies10 02 without padding, preserving the live capacity pointer; stops
   before timer capture/service dispatch. */

void f33_boot_request_append_bytes(uchar *source,uchar length)

{
  uchar uVar1;
  uint uVar2;
  uint uVar3;
  
  uVar3 = (uint)length;
  uVar2 = (uint)(*((volatile uint16_t *)camry_host_ptr(0xfebe4bb8u)));
  if ((-1 < (int)(uVar3 + uVar2 + -0x1000)) && (uVar3 = 0, uVar2 < 0x1000)) {
    uVar3 = 0x1000 - uVar2 & 0xffff;
  }
  for (; uVar3 != 0; uVar3 = uVar3 - 1) {
    uVar1 = *source;
    source = source + 1;
    (*((volatile uint16_t *)camry_host_ptr(0xfebe4bb8u))) = (ushort)(uVar2 + 1);
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe50c0u + (uint32_t)(uVar2) * 1u)))) = uVar1;
    uVar2 = uVar2 + 1 & 0xffff;
  }
  return;
}



/* WARNING: Inlined function: f33_boot_request_append_bytes */
/* Returns0success/1capacityerror;readsONLYlowbyteofdescriptorlength,updatesu16total30B8,andcalls6422.6422mustpreserver8capacityoutputliveacrosscall.
   Native real SF admission copies10 02 without padding, preserving the live capacity pointer; stops
   before timer capture/service dispatch. */

uint f33_boot_request_append(ushort channel,F33BootPduInfo *chunk,ushort *remaining_capacity)

{
  uchar uVar1;
  byte bVar2;
  uchar *puVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  
  bVar2 = (byte)chunk->length;
  uVar6 = (uint)bVar2;
  puVar3 = ((void *)camry_host_ptr((uint32_t)(chunk->data)));
  uVar5 = 1;
  if (uVar6 != 0) {
    uVar4 = 0x1000 - (*((volatile uint16_t *)camry_host_ptr(0xfebe50b8u)));
    if ((int)(uVar6 - uVar4) < 0 == ((int)uVar4 < 0 && (int)uVar4 < 0 == (int)(uVar6 - uVar4) < 0)
        && uVar6 != uVar4) goto LAB_000064a0;
    (*((volatile uint16_t *)camry_host_ptr(0xfebe50b8u))) = bVar2 + (*((volatile uint16_t *)camry_host_ptr(0xfebe50b8u)));
    uVar5 = (uint)f33_boot_request_append_index;
    uVar4 = uVar6;
    if ((-1 < (int)(uVar6 + uVar5 + -0x1000)) && (uVar4 = 0, uVar5 < 0x1000)) {
      uVar4 = 0x1000 - uVar5 & 0xffff;
    }
    for (; uVar4 != 0; uVar4 = uVar4 - 1) {
      uVar1 = *puVar3;
      puVar3 = puVar3 + 1;
      f33_boot_request_append_index = (ushort)(uVar5 + 1);
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebf30c0u + (uint32_t)(uVar5) * 1u)))) = uVar1;
      uVar5 = uVar5 + 1 & 0xffff;
    }
  }
  uVar5 = 0;
  *remaining_capacity = 0x1000 - (*((volatile uint16_t *)camry_host_ptr(0xfebe50b8u)));
LAB_000064a0:
  if ((*((volatile uint8_t *)camry_host_ptr(0xfebe4bbeu))) == '\x01') {
    ((void)((*((volatile uint8_t *)camry_host_ptr(0xfebe50beu)))), (void)(uVar6), f33_return_only_stub_5282());
  }
  return uVar5;
}



/* Status0capturesrawcountertimestamps,publishesexecuting2/substate0anddispatchesSID+length.Nonzerostatusabortsthereceive.
    */

void f33_boot_request_receive_complete(ushort channel,uchar status)

{
  uint32_t puVar1;
  uint32_t puVar2;
  undefined4 uVar3;
  
  puVar2 = 0xfebeb800u;
  puVar1 = 0xfebeb800u;
  if (status == '\0') {
    uVar3 = ((void)(channel), FUN_00001d24());
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x6c54)))) = uVar3;
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x6c50)))) = uVar3;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6c46))))) = 2;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6c45))))) = 0;
    f33_boot_dispatch_diagnostic_service((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6742))))),(*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x6748)))));
  }
  else {
    if ((*((volatile uint8_t *)camry_host_ptr(0xfebe4bbeu))) == '\x01') {
      puVar2 = 0xfebeb800u;
      ((void)((*((volatile uint8_t *)camry_host_ptr(0xfebe50beu)))), f33_return_only_stub_5284());
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6c46))))) = 0;
    uVar3 = FUN_00001d24();
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + -0x6c4c)))) = uVar3;
  }
  return;
}



/* Matchchannelrecord8F04/8F0C,forceextendedsession3andreadsubfunction/suppressionfromhandoffword4/5,thenadmit/append/complete10request.
    */

void f33_boot_diagnostic_replay_handoff_session(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  ushort channel;
  int in_r6;
  uint uVar4;
  ushort local_14;
  uchar uStack_12;
  byte bStack_11;
  F33BootPduInfo FStack_10;
  
  iVar3 = 0;
  do {
    if ((*((uint *)camry_host_ptr((uint32_t)(in_r6 + 4)))) == f33_boot_diagnostic_channels[iVar3].handoff_selector) {
      uStack_12 = '\x10';
      bStack_11 = (*((byte *)camry_host_ptr((uint32_t)(in_r6 + 0x10))));
      if ((*((char *)camry_host_ptr((uint32_t)(in_r6 + 0x14)))) != '\0') {
        bStack_11 = bStack_11 | 0x80;
      }
      FUN_00005148();
      FStack_10.data = camry_host_addr(&uStack_12);
      FStack_10.length = 2;
      channel = (ushort)iVar3;
      uVar4 = f33_boot_request_admit(channel,&FStack_10,2,&local_14);
      if (((uVar4 == 0) && (1 < local_14)) &&
         (uVar4 = f33_boot_request_append(channel,&FStack_10,&local_14), uVar4 == 0)) {
        f33_boot_request_receive_complete(channel,'\0');
      }
      return;
    }
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -1;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}



void FUN_00006588(void)

{
  (*((volatile uint8_t *)camry_host_ptr(0xfebe4bbeu))) = 0;
  (*((volatile uint16_t *)camry_host_ptr(0xfebe4bb8u))) = (*((volatile uint16_t *)camry_host_ptr(0xfebe50b8u)));
  (*((volatile uint8_t *)camry_host_ptr(0xfebe4bbau))) = '\x01';
  f33_boot_request_receive_complete(0,'\0');
  return;
}



/* Ownstimestamp-gatedsend,78pending,inflightlockandoverallterminalstate;doesnotownFACIoperation. */

void f33_boot_response_timer_progress(void)

{
  undefined1 uVar1;
  uint32_t puVar2;
  F33BootInterruptEntry *pFVar3;
  int iVar4;
  undefined4 uVar5;
  undefined *puVar6;
  
  puVar2 = 0xfebeb800u;
  pFVar3 = f33_boot_interrupt_dispatch;
  if ((*((volatile uint8_t *)camry_host_ptr(0xfebe4bbbu))) == '\x01') {
    iVar4 = FUN_00001d24();
    if (iVar4 == (*((int *)camry_host_ptr((uint32_t)(puVar2 + -0x6c54))))) {
      return;
    }
    FUN_00002d88((*((undefined1 *)camry_host_ptr((uint32_t)((int)&pFVar3[*(ushort *)(puVar2 + -0x6744) + 0x10d].handler + 2)))), camry_host_addr(((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x6c5c)))));
    uVar1 = 2;
  }
  else {
    if ((*((volatile uint8_t *)camry_host_ptr(0xfebe4bbbu))) == '\x02') {
      return;
    }
    if ((*((volatile uint8_t *)camry_host_ptr(0xfebe4bbbu))) == '\x04') {
      return;
    }
    puVar6 = ((undefined *)camry_host_ptr(0x9c40u));
    if ((*((volatile uint8_t *)camry_host_ptr(0xfebe4bbbu))) == '\x03') {
      puVar6 = ((undefined *)camry_host_ptr((uint32_t)(0x2349340)));
    }
    puVar2 = 0xfebeb800u;
    iVar4 = FUN_00001d24();
    if ((uint)(iVar4 - (*((int *)camry_host_ptr((uint32_t)(puVar2 + -0x6c50))))) < 3600000000) {
      if ((uintptr_t)(((undefined *)camry_host_ptr((uint32_t)(iVar4 - *(int *)(puVar2 + -0x6c54)))))<=(uintptr_t)(puVar6)) {
        return;
      }
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6c44))))) == '\x01') {
        return;
      }
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6c40))))) = 0x7f;
      *(undefined **)(puVar2 + -0x6c5c) = ((void *)camry_host_ptr((uint32_t)(puVar2 + -0x6c40)));
      (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x6c58)))) = 3;
      (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x6746)))) = 3;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6c3f))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6742)))));
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6c3e))))) = 0x78;
      FUN_00002d88((*((undefined1 *)camry_host_ptr((uint32_t)((int)&pFVar3[*(ushort *)(puVar2 + -0x6744) + 0x10d].handler + 2)))), camry_host_addr(((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x6c5c)))));
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6c44))))) = 1;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6c45))))) = 3;
      uVar5 = FUN_00001d24();
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + -0x6c54)))) = uVar5;
      return;
    }
    uVar1 = 4;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6c45))))) = uVar1;
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
  
  puVar1 = 0xfebeb800u;
  if ((*((volatile uint8_t *)camry_host_ptr(0xfebe4bbau))) == '\x02') {
    f33_boot_response_timer_progress();
  }
  else if (((*((volatile uint8_t *)camry_host_ptr(0xfebe4bbau))) == '\0') && ((*((volatile uint8_t *)camry_host_ptr(0xfebe4bbfu))) != '\x01')) {
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



/* Duringresponse-pendingstate3onlyclearsinflightlock2BBC;othercompletionreleasesrequestownerandmayjointheterminalpath159E.
    */

void f33_boot_response_complete(ushort channel,uchar status)

{
  uint32_t puVar1;
  undefined4 uVar2;
  
  puVar1 = 0xfebeb800u;
  if ((*((volatile uint8_t *)camry_host_ptr(0xfebe4bbbu))) == '\x03') {
    (*((volatile uint8_t *)camry_host_ptr(0xfebe4bbcu))) = '\0';
  }
  else {
    (*((volatile uint8_t *)camry_host_ptr(0xfebe4bbau))) = '\0';
    uVar2 = ((void)(channel), FUN_00001d24());
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x6c4c)))) = uVar2;
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6c43))))) == '\x01') {
      if (status == '\0') {
        FUN_0000159e();
      }
      else {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6c43))))) = 0;
      }
    }
  }
  return;
}



/* Outgoingrequestdescriptorlengthlowbytecontrolsactualcopy;consumes30BAremaining,writesr9remaining;caller6B8Aforwardsliveregisters.
    */

uint f33_boot_response_copy_chunk
               (ushort channel,F33BootPduInfo *chunk,uint unused,ushort *remaining)

{
  byte bVar1;
  uint uVar2;
  uchar *puVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  
  bVar1 = (byte)chunk->length;
  uVar4 = (uint)bVar1;
  puVar3 = ((void *)camry_host_ptr((uint32_t)(chunk->data)));
  if (uVar4 != 0) {
    if ((*((volatile uint16_t *)camry_host_ptr(0xfebe50bau))) < uVar4) {
      return 1;
    }
    uVar6 = (uint)(*((volatile uint16_t *)camry_host_ptr(0xfebe4ba8u))) - (uint)(*((volatile uint16_t *)camry_host_ptr(0xfebe50bau)));
    for (uVar2 = 0; uVar2 < uVar4; uVar2 = uVar2 + 1 & 0xff) {
      uVar5 = uVar6 & 0xffff;
      uVar6 = uVar5 + 1;
      puVar3[uVar2] = (*((uchar *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr(0xfebe4ba4u))) + uVar5))));
    }
    (*((volatile uint16_t *)camry_host_ptr(0xfebe50bau))) = (*((volatile uint16_t *)camry_host_ptr(0xfebe50bau))) - bVar1;
  }
  *remaining = (*((volatile uint16_t *)camry_host_ptr(0xfebe50bau)));
  return 0;
}



/* Stagesresponseorcompletesasuppressedrequest;forcestransmissionafterprevious78pending.Same-countertickdeferralavoidsimmediatesend,then65AAownsprogress.
    */

void f33_boot_response_submit(uchar mode,uchar *data,ushort length)

{
  undefined1 uVar1;
  uint32_t puVar2;
  uint32_t puVar3;
  F33BootInterruptEntry *pFVar4;
  int iVar5;
  undefined4 uVar6;
  
  puVar2 = 0xfebeb800u;
  puVar3 = 0xfebeb800u;
  pFVar4 = f33_boot_interrupt_dispatch;
  if (((*((volatile uint8_t *)camry_host_ptr(0xfebe4bbbu))) == '\x03') || (mode != '\0')) {
    (*((volatile uint32_t *)camry_host_ptr(0xfebe4ba4u))) = camry_host_addr(data);
    DAT_febf2ba8 = length;
    (*((volatile uint16_t *)camry_host_ptr(0xfebe50bau))) = length;
    iVar5 = FUN_00001d24();
    if (iVar5 == (*((int *)camry_host_ptr((uint32_t)(puVar3 + -0x6c54))))) {
      uVar1 = 1;
    }
    else {
      FUN_00002d88((*((undefined1 *)camry_host_ptr((uint32_t)((int)&pFVar4[*(ushort *)(puVar3 + -0x6744) + 0x10d].handler + 2)))), camry_host_addr(((undefined *)camry_host_ptr((uint32_t)(puVar3 + -0x6c5c)))));
      uVar1 = 2;
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6c45))))) = uVar1;
  }
  else {
    (*((volatile uint8_t *)camry_host_ptr(0xfebe4bbau))) = '\0';
    uVar6 = FUN_00001d24();
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + -0x6c4c)))) = uVar6;
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6c43))))) == '\x01') {
      FUN_0000159e();
    }
  }
  return;
}



void FUN_000067b0(undefined1 *param_1,uint param_2)

{
  uint uVar1;
  
  for (uVar1 = 0; uVar1 < (param_2 & 0xffff); uVar1 = uVar1 + 1) {
    *param_1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe50c0u + (uint32_t)(uVar1) * 1u))));
    param_1 = param_1 + 1;
  }
  (*((volatile uint16_t *)camry_host_ptr(0xfebe4bb8u))) = 0;
  return;
}



undefined1 * FUN_000067d0(void)

{
  (*((volatile uint16_t *)camry_host_ptr(0xfebe4bb8u))) = 0;
  return ((undefined *)camry_host_ptr(0xfebe50c0u));
}



void FUN_000067da(void)

{
  if ((*((volatile uint8_t *)camry_host_ptr(0xfebe4bbau))) == '\0') {
    FUN_0000159e();
  }
  else {
    (*((volatile uint8_t *)camry_host_ptr(0xfebe4bbdu))) = '\x01';
  }
  return;
}



char FUN_000067f6(void)

{
  uint32_t puVar1;
  undefined4 uVar2;
  char cVar3;
  
  puVar1 = 0xfebeb800u;
  uVar2 = FUN_0000721e(0xffff);
  cVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6c46)))));
  if (cVar3 == '\x02') {
    cVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6c45))))) + '\x02';
  }
  FUN_00007244(uVar2);
  return cVar3;
}



void FUN_0000681e(undefined1 param_1)

{
  uint32_t puVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  
  puVar1 = 0xfebeb800u;
  uVar2 = FUN_0000721e(0xffff);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6c41))))) = param_1;
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6c46))))) == '\0') {
    uVar3 = FUN_00001d24();
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x6c4c)))) = uVar3;
  }
  FUN_00007244(uVar2);
  return;
}



void FUN_0000684c(uchar param_1)

{
  f33_boot_negative_response('(',param_1);
  return;
}



void FUN_00006860(void)

{
  (*((volatile uint8_t *)camry_host_ptr(0xfebe4ad0u))) = 0x68;
  DAT_febf2ad1 = (*((volatile uint8_t *)camry_host_ptr(0xfebe4bc3u))) & 0x7f;
  f33_boot_response_submit((*((volatile uint8_t *)camry_host_ptr(0xfebe4bc3u))) >> 7 ^ 1,((undefined *)camry_host_ptr(0xfebe4ad0u)),2);
  return;
}



/* Resident SID28: session3, length3, masked subfunction1 and communication byte1 only; invalid
   subfunction12, invalid communication byte31, bad length13. Store original subfunction and
   form68/masked-subfunction with bit7 positive-response suppression. No physical
   communication-disable side effect is established by this handler. */

void f33_boot_service_communication_control(ushort request_length)

{
  uint32_t puVar1;
  F33BootInterruptEntry *pFVar2;
  undefined4 uVar3;
  undefined1 uStack_b;
  byte bStack_a;
  char cStack_9;
  
  puVar1 = 0xfebeb800u;
  pFVar2 = f33_boot_interrupt_dispatch;
  uStack_b = 0;
  bStack_a = 0;
  cStack_9 = '\0';
  FUN_000067b0(&uStack_b,3);
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6cf2))))) != (*((char *)camry_host_ptr((uint32_t)((int)&pFVar2[0x10b].eiic + 2))))) {
    uVar3 = 0x7f;
    goto LAB_000068b8;
  }
  if (2 < request_length) {
    if ((bStack_a & 0x7f) != 1) {
      uVar3 = 0x12;
      goto LAB_000068b8;
    }
    if (request_length == 3) {
      if (cStack_9 == '\x01') {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6c3d))))) = bStack_a;
        FUN_00006860();
        return;
      }
      uVar3 = 0x31;
      goto LAB_000068b8;
    }
  }
  uVar3 = 0x13;
LAB_000068b8:
  FUN_0000684c(uVar3);
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
  (*((volatile uint8_t *)camry_host_ptr(0xfebe4ad0u))) = 0xc5;
  DAT_febf2ad1 = (*((volatile uint8_t *)camry_host_ptr(0xfebe4bc4u))) & 0x7f;
  f33_boot_response_submit((*((volatile uint8_t *)camry_host_ptr(0xfebe4bc4u))) >> 7 ^ 1,((undefined *)camry_host_ptr(0xfebe4ad0u)),2);
  return;
}



/* Resident SID85: session3, length2 and masked subfunction2 only. Store original subfunction and
   formC5/02 through6910 with bit7 positive-response suppression. No application DTC-state mutation
   is established here. */

void f33_boot_service_dtc_setting(ushort request_length)

{
  uint32_t puVar1;
  F33BootInterruptEntry *pFVar2;
  undefined4 uVar3;
  undefined1 uStack_a;
  byte bStack_9;
  
  puVar1 = 0xfebeb800u;
  pFVar2 = f33_boot_interrupt_dispatch;
  uStack_a = 0;
  bStack_9 = 0;
  FUN_000067b0(&uStack_a,2);
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6cf2))))) == (*((char *)camry_host_ptr((uint32_t)((int)&pFVar2[0x10b].eiic + 3))))) {
    if (1 < request_length) {
      if ((bStack_9 & 0x7f) != 2) {
        uVar3 = 0x12;
        goto LAB_00006966;
      }
      if (request_length == 2) {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6c3c))))) = bStack_9;
        FUN_00006910();
        return;
      }
    }
    uVar3 = 0x13;
  }
  else {
    uVar3 = 0x7f;
  }
LAB_00006966:
  FUN_000068fc(uVar3);
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
  f33_boot_negative_response((*((volatile uint8_t *)camry_host_ptr(0xfebe4bc5u))),param_1);
  return;
}



/* Sharedconfiguredcallbackfor23/2C/14/19/2F/AB/BA/BB;readsSIDfromrequestbyte0andreturnsNRC7F.Doesnotimplementthoseservices.
    */

void f33_boot_service_reject_configured(ushort request_length)

{
  uint32_t puVar1;
  undefined1 uStack_5;
  
  puVar1 = 0xfebeb800u;
  FUN_000067b0(&uStack_5,1);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6c3b))))) = uStack_5;
  FUN_0000699c(0x7f);
  return;
}



/* Enablesonlyhandofftag0orFF;noapplicationDCMinitialization. */

void f33_boot_diagnostic_enable_from_handoff(void)

{
  int local_c;
  
  DAT_febf2bd0 = 0;
  FUN_00001514(camry_host_addr(&local_c), 1);
  if ((local_c == 0) || (local_c == 0xff)) {
    DAT_febf2bd0 = 1;
    FUN_000014be(0);
  }
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



/* Resetsresidentserviceworkers;tag0preparesdriverandreplaysrecordsessionthrough6504;tagFFwaitswithtimestamp.
    */

void f33_boot_diagnostic_initialize_from_handoff(void)

{
  int local_2c [8];
  
  if (DAT_febf2bd0 != '\0') {
    DAT_febf2bd1 = 0;
    DAT_febf2bd2 = 0;
    FUN_00006320();
    FUN_00005086();
    f33_boot_region_authentication_clear_activity();
    FUN_00006ea2();
    f33_boot_block_transform_clear_activity();
    FUN_00006d02();
    FUN_00001514(camry_host_addr(local_2c), 8);
    if (local_2c[0] == 0) {
      DAT_febf2bcc = 0xffffffff;
      DAT_febf2bd1 = 1;
      DAT_febf2bd2 = 0;
      FUN_0000152a();
      FUN_0000519c();
      f33_boot_diagnostic_replay_handoff_session();
    }
    else if (local_2c[0] == 0xff) {
      DAT_febf2bcc = 0xffffffff;
      DAT_febf2bc8 = FUN_00001d24();
    }
  }
  return;
}



/* Enabledforegroundruns51C8/6E60/6EE0/6BDE/6C8Einthatorder;separatefromtimer51AC. */

void f33_boot_diagnostic_foreground(void)

{
  undefined4 uVar1;
  int iVar2;
  
  if (DAT_febf2bd0 != '\0') {
    FUN_000051c8();
    FUN_00006e60();
    f33_boot_region_authentication_progress();
    f33_boot_transfer_block_transform_progress();
    f33_boot_transfer_compare_progress();
    uVar1 = FUN_0000721e(0xffff);
    if (DAT_febf2bd1 != '\x01') {
      iVar2 = FUN_00001d24();
      if ((((uint)(iVar2 - DAT_febf2bc8) <= DAT_febf2bcc) && (DAT_febf2bd2 == '\x01')) &&
         (iVar2 != DAT_febf2bc8)) {
        DAT_febf2bd2 = '\0';
      }
    }
    FUN_00007244(uVar1);
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

uint f33_boot_transfer_crypto_initialize(void)

{
  return f33_boot_image_crypto_initialize();
}



/* Returns1busy/0accepted;storeslengthu16,pointers,sets2BDEactive;worker6BDEtransformsfull16-byteblocks.
    */

uint f33_boot_block_transform_submit(ushort length,uchar *source,uchar *destination)

{
  bool bVar1;
  
  bVar1 = (*((volatile uint8_t *)camry_host_ptr(0xfebe4bdeu))) == '\0';
  if (bVar1) {
    (*((volatile uint8_t *)camry_host_ptr(0xfebe4bdeu))) = '\x01';
    (*((volatile uint32_t *)camry_host_ptr(0xfebe4bd4u))) = camry_host_addr(source);
    (*((volatile uint32_t *)camry_host_ptr(0xfebe4bd8u))) = camry_host_addr(destination);
    (*((volatile uint16_t *)camry_host_ptr(0xfebe4bdcu))) = length;
  }
  return (uint)!bVar1;
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
  
  uVar5 = 0xfebeb800;
  puVar4 = ((undefined *)camry_host_ptr(0xfebeb800u));
  if ((*((volatile uint8_t *)camry_host_ptr(0xfebe4bdeu))) != '\0') {
    uVar7 = (uint)(*((volatile uint16_t *)camry_host_ptr(0xfebe4bdcu)));
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
  (*((volatile uint8_t *)camry_host_ptr(0xfebe4bdeu))) = 0;
  return;
}



bool FUN_00006c5a(int *param_1)

{
  return *param_1 != 0x5aa5a55a;
}



/* Returns1ifalreadybusyelse0,setsfailure1/active1andfull32-bitremaining/pointers;4CA2preserveslivelengthr8acrosssetup.
    */

uint f33_boot_compare_submit(uchar *left,uchar *right,uint length)

{
  bool bVar1;
  
  bVar1 = (*((volatile uint8_t *)camry_host_ptr(0xfebe4bedu))) == '\0';
  if (bVar1) {
    (*((volatile uint8_t *)camry_host_ptr(0xfebe4becu))) = 1;
    (*((volatile uint8_t *)camry_host_ptr(0xfebe4bedu))) = '\x01';
    (*((volatile uint32_t *)camry_host_ptr(0xfebe4be0u))) = length;
    (*((volatile uint32_t *)camry_host_ptr(0xfebe4be4u))) = camry_host_addr(left);
    (*((volatile uint32_t *)camry_host_ptr(0xfebe4be8u))) = camry_host_addr(right);
  }
  return (uint)!bVar1;
}



/* Atmost16bytespercall;firstmismatchclearsbusybutkeepsfailure1;onlycompleteall-matchclearsfailure0.
    */

void f33_boot_transfer_compare_progress(void)

{
  bool bVar1;
  uint32_t puVar2;
  undefined4 uVar3;
  uint uVar4;
  uint uVar5;
  
  puVar2 = 0xfebeb800u;
  if ((*((volatile uint8_t *)camry_host_ptr(0xfebe4bedu))) != '\0') {
    uVar5 = 0;
    uVar4 = (*((volatile uint32_t *)camry_host_ptr(0xfebe4be0u)));
    if (0xf < (*((volatile uint32_t *)camry_host_ptr(0xfebe4be0u)))) {
      uVar4 = 0x10;
    }
    for (; uVar5 < uVar4; uVar5 = uVar5 + 1) {
      if ((*((char *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr(0xfebe4be4u))) + uVar5)))) != (*((char *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr(0xfebe4be8u))) + uVar5))))) {
        (*((volatile uint8_t *)camry_host_ptr(0xfebe4bedu))) = 0;
        return;
      }
    }
    (*((volatile uint32_t *)camry_host_ptr(0xfebe4be4u))) = (*((volatile uint32_t *)camry_host_ptr(0xfebe4be4u))) + uVar4;
    (*((volatile uint32_t *)camry_host_ptr(0xfebe4be8u))) = (*((volatile uint32_t *)camry_host_ptr(0xfebe4be8u))) + uVar4;
    uVar5 = (*((volatile uint32_t *)camry_host_ptr(0xfebe4be0u))) - uVar4;
    bVar1 = (*((volatile uint32_t *)camry_host_ptr(0xfebe4be0u))) == uVar4;
    (*((volatile uint32_t *)camry_host_ptr(0xfebe4be0u))) = uVar5;
    if (bVar1) {
      uVar3 = FUN_0000721e(0xffff);
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6c14))))) = 0;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6c13))))) = 0;
      FUN_00007244(uVar3);
    }
  }
  return;
}



/* Paired constant publisher: DAT_febf2bec = 1; and DAT_febf2bed = 0;; shape-classified from the
   canonical corpus. Target cells not yet named. */

void FUN_00006d02(void)

{
  (*((volatile uint8_t *)camry_host_ptr(0xfebe4becu))) = 1;
  (*((volatile uint8_t *)camry_host_ptr(0xfebe4bedu))) = 0;
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



int FUN_00006d5e(undefined4 *param_1,undefined4 param_2)

{
  undefined1 uVar1;
  undefined4 uVar2;
  uint32_t puVar3;
  undefined4 uVar4;
  int iVar5;
  
  puVar3 = 0xfebeb800u;
  iVar5 = 1;
  uVar4 = FUN_0000721e(0xffff);
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6c05))))) != '\x01') {
    if ((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 9)))) < 2) {
      if ((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 9)))) == 0) {
        iVar5 = FUN_00006d10(param_1, ((uchar *)camry_host_ptr((uint32_t)(param_2))));
      }
      else {
        iVar5 = FUN_00006d3a(param_1,param_2);
      }
    }
    if (iVar5 == 0) {
      uVar2 = *param_1;
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar3 + -0x6c0c)))) = 0;
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar3 + -0x6c10)))) = uVar2;
      uVar1 = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 9))));
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6c07))))) = 0;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6c08))))) = uVar1;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6c06))))) = 1;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6c05))))) = 1;
    }
  }
  FUN_00007244(uVar4);
  return iVar5;
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



undefined4 FUN_00006e08(int param_1,undefined4 param_2)

{
  uint32_t puVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  
  puVar1 = 0xfebeb800u;
  uVar3 = 1;
  uVar2 = FUN_0000721e(0xffff);
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6c05))))) != '\x01') && ((*((byte *)camry_host_ptr((uint32_t)(param_1 + 9)))) < 2)) {
    if ((*((byte *)camry_host_ptr((uint32_t)(param_1 + 9)))) == 0) {
      uVar3 = FUN_00006dc0(((int *)camry_host_ptr((uint32_t)(param_1))),  param_2);
    }
    else {
      uVar3 = FUN_00006de4(((int *)camry_host_ptr((uint32_t)(param_1))), param_2);
    }
  }
  FUN_00007244(uVar2);
  return uVar3;
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



undefined4 FUN_00006e60(void)

{
  uint32_t puVar1;
  undefined4 uVar2;
  
  puVar1 = 0xfebeb800u;
  uVar2 = FUN_0000721e(0xffff);
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6c05))))) != '\x01') || (1 < (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6c08))))))) goto LAB_00006e98;
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6c08))))) == 0) {
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-27999))))) == '\x01') goto LAB_00006e98;
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-28000))))) != '\0') {
      FUN_00006e54();
      goto LAB_00006e98;
    }
  }
  FUN_00006e4a();
LAB_00006e98:
  FUN_00007244(uVar2);
  return uVar2;
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

uint f33_boot_authentication_crypto_initialize(void)

{
  return f33_boot_image_crypto_initialize();
}



/* Real r6/r7 start,length passed unchanged to7122; reject ifactive2BFD!=0, else seed
   CMAC-prefix/cursors and publishresult1/active1 on success. Return0accepted/1rejected. Does not
   initialize contexts by itself. */

uint f33_boot_region_authentication_submit(uint start,uint length)

{
  uint32_t puVar1;
  uint uVar2;
  uint uVar3;
  
  puVar1 = 0xfebeb800u;
  uVar3 = 1;
  if (((*((volatile uint8_t *)camry_host_ptr(0xfebe4bfdu))) == '\0') &&
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
  
  puVar1 = 0xfebeb800u;
  if (((*((volatile uint8_t *)camry_host_ptr(0xfebe4bfdu))) != '\0') && (uVar2 = f33_boot_image_authentication_step(), uVar2 != 2)) {
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
  (*((volatile uint8_t *)camry_host_ptr(0xfebe4bfcu))) = 1;
  (*((volatile uint8_t *)camry_host_ptr(0xfebe4bfdu))) = 0;
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
            (f33_boot_security_client_decryption_key, '\x10', ((F33BootAes128Context *)camry_host_ptr((uint32_t)((0xfebe4d48u)))));
  f33_boot_aes128_decrypt_block
            (client_material, intermediate_key, '\x10', ((F33BootAes128Context *)camry_host_ptr((uint32_t)((0xfebe4d48u)))));
  f33_boot_aes128_clear_context(((F33BootAes128Context *)camry_host_ptr((uint32_t)((0xfebe4d48u)))));
  return;
}



/* AES-128 single-block encryption with16-byte key/input/output,using shared
   contextFEBF2D48;clearsentire196-bytecontextafteroperation. r6key,r7plaintext,r8output;
   noapplicationGP/SecOCsemantics. Native AES known-answer and protocol-state cases use explicit
   RAM. Service paths stop at674A before response/timer completion; direct session invalidation
   cases return. No complete unlock or entropy claim. */

void f33_boot_security_encrypt_block(uchar *key,uchar *plaintext,uchar *ciphertext)

{
  f33_boot_aes128_initialize_context(key, '\x10', ((F33BootAes128Context *)camry_host_ptr((uint32_t)((0xfebe4d48u)))));
  f33_boot_aes128_encrypt_block(plaintext, ciphertext, '\x10', ((F33BootAes128Context *)camry_host_ptr((uint32_t)((0xfebe4d48u)))));
  f33_boot_aes128_clear_context(((F33BootAes128Context *)camry_host_ptr((uint32_t)((0xfebe4d48u)))));
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
  puVar1 = 0xfebeb800u;
  f33_boot_aes128_initialize_context
            (f33_boot_image_key_derivation_key, '\x10', ((F33BootAes128Context *)camry_host_ptr((uint32_t)((0xfebe4d48u)))));
  f33_boot_aes128_encrypt_block
            (((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x6af8))),  ((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x6ae8))),  '\x10', ((F33BootAes128Context *)camry_host_ptr((uint32_t)((0xfebe4d48u)))));
  f33_boot_aes128_clear_context(((F33BootAes128Context *)camry_host_ptr((uint32_t)((0xfebe4d48u)))));
  return;
}



/* Initialize CBC2EF0 with derived key2D18/IV2CF8; initialize CMAC2C00 same key with zero chain then
   derive CMAC subkeys. Wrapper ignores all statuses. Does not consume authentication prefix yet. */

uint f33_boot_image_initialize_contexts(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  f33_boot_aes128_cbc_initialize
            (((volatile uint8_t *)camry_host_ptr(0xfebe4d18u)), '\x10', ((volatile uint8_t *)camry_host_ptr(0xfebe4cf8u)), '\x10', ((F33BootAes128CbcContext *)camry_host_ptr((uint32_t)((0xfebe4ef0u)))));
  f33_boot_aes128_cmac_initialize
            (((volatile uint8_t *)camry_host_ptr(0xfebe4d18u)),'\x10',((F33BootAes128CmacContext *)camry_host_ptr((uint32_t)(puVar1 + -0x6c00))));
  return f33_boot_aes128_cmac_derive_subkeys(((F33BootAes128CmacContext *)camry_host_ptr((uint32_t)(puVar1 + -0x6c00))));
}



/* Derive image key7068 then initialize both CBC/CMAC709A. Reinitializes shared image contexts, not
   a per-transfer-chunk action. */

uint f33_boot_image_crypto_initialize(void)

{
  f33_boot_image_derive_key();
  return f33_boot_image_initialize_contexts();
}



/* Clear CBC2EF0 all228 bytes then CMAC2C00 all248 bytes. Retain IV/material/derived key/output and
   authentication cursors; does not reset activity flags. */

void f33_boot_image_clear_contexts(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  f33_boot_aes128_cbc_clear(((F33BootAes128CbcContext *)camry_host_ptr((uint32_t)((0xfebe4ef0u)))));
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
  
  uVar1 = f33_boot_aes128_cbc_decrypt_block(ciphertext, plaintext, '\x10', ((F33BootAes128CbcContext *)camry_host_ptr((uint32_t)((0xfebe4ef0u)))))
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



/* WARNING: Removing unreachable block (ram,0x00007232) */

uint FUN_0000721e(int param_1)

{
  uint uVar1;
  uint uVar2;
  int iVar3;
  undefined4 uVar4;
  uint uVar5;
  uint in_PSW;
  uint in_FPEC;
  uint in_RBASE;
  uint in_EBASE;
  uint in_FPIPR;
  uint in_ISPR;
  
  iVar3 = PMR;
  if (iVar3 - param_1 < 0 != (iVar3 < 0 != param_1 < 0 && param_1 < 0 == iVar3 - param_1 < 0)) {
    if ((in_PSW & 0x20) == 0) {
      __disable_irq();
      PMR = param_1;
      if ((in_FPEC & 1) != 0) {
        uVar4 = PMR;
      }
      if ((in_FPEC & 1) != 0) {
        uVar1 = in_FPIPR & 0x1f;
        if (0xf < uVar1) {
          uVar1 = 0x10;
        }
        uVar2 = uVar1;
        if (0xf < uVar1) {
          uVar2 = 0xf;
        }
        uVar5 = PMR;
        if ((((uVar5 & 1 << uVar2) == 0) && ((in_ISPR & (1 << uVar1 + 1) - 1U & 0xffff) == 0)) &&
           ((in_PSW & 0x80) == 0)) {
          if (((in_PSW & 0xbfffffd0) >> 0xf & 1) == 0) {
            in_EBASE = in_RBASE;
          }
          (*(int (*)())camry_host_ptr((uint32_t)((in_EBASE & 0xfffffe00) + 0x70)))();
        }
      }
      __enable_irq();
    }
    else {
      PMR = param_1;
      if ((in_FPEC & 1) != 0) {
        uVar1 = in_FPIPR & 0x1f;
        if (0xf < uVar1) {
          uVar1 = 0x10;
        }
        uVar2 = uVar1;
        if (0xf < uVar1) {
          uVar2 = 0xf;
        }
        uVar5 = PMR;
        if ((((uVar5 & 1 << uVar2) == 0) && ((in_ISPR & (1 << uVar1 + 1) - 1U & 0xffff) == 0)) &&
           ((in_PSW & 0xa0) == 0)) {
          if (((in_PSW & 0xbfffffb0) >> 0xf & 1) == 0) {
            in_EBASE = in_RBASE;
          }
          (*(int (*)())camry_host_ptr((uint32_t)((in_EBASE & 0xfffffe00) + 0x70)))();
        }
      }
    }
    __synchronize();
  }
  return iVar3;
}



/* WARNING: Removing unreachable block (ram,0x00007250) */

void FUN_00007244(undefined4 param_1)

{
  uint uVar1;
  uint uVar2;
  undefined4 uVar3;
  uint uVar4;
  uint in_PSW;
  uint in_FPEC;
  uint in_RBASE;
  uint in_EBASE;
  uint in_FPIPR;
  uint in_ISPR;
  
  if ((in_PSW >> 5 & 1) == 0) {
    __disable_irq();
    PMR = param_1;
    if ((in_FPEC & 1) != 0) {
      uVar3 = PMR;
    }
    if ((in_FPEC & 1) != 0) {
      uVar1 = in_FPIPR & 0x1f;
      if (0xf < uVar1) {
        uVar1 = 0x10;
      }
      uVar2 = uVar1;
      if (0xf < uVar1) {
        uVar2 = 0xf;
      }
      uVar4 = PMR;
      if ((((uVar4 & 1 << uVar2) == 0) && ((in_ISPR & (1 << uVar1 + 1) - 1U & 0xffff) == 0)) &&
         ((in_PSW & 0x80) == 0)) {
        if (((in_PSW & 0xbfffffd0) >> 0xf & 1) == 0) {
          in_EBASE = in_RBASE;
        }
        (*(int (*)())camry_host_ptr((uint32_t)((in_EBASE & 0xfffffe00) + 0x70)))();
      }
    }
    __enable_irq();
  }
  else {
    PMR = param_1;
    if ((in_FPEC & 1) != 0) {
      uVar1 = in_FPIPR & 0x1f;
      if (0xf < uVar1) {
        uVar1 = 0x10;
      }
      uVar2 = uVar1;
      if (0xf < uVar1) {
        uVar2 = 0xf;
      }
      uVar4 = PMR;
      if ((((uVar4 & 1 << uVar2) == 0) && ((in_ISPR & (1 << uVar1 + 1) - 1U & 0xffff) == 0)) &&
         ((in_PSW & 0xa0) == 0)) {
        if (((in_PSW & 0xbfffffb0) >> 0xf & 1) == 0) {
          in_EBASE = in_RBASE;
        }
        (*(int (*)())camry_host_ptr((uint32_t)((in_EBASE & 0xfffffe00) + 0x70)))();
      }
    }
  }
  __synchronize();
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
  } while ((uintptr_t)(puVar5)!=(uintptr_t)(((undefined *)camry_host_ptr(0x8fd0u))));
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
  } while ((uintptr_t)(puVar4)!=(uintptr_t)(((undefined *)camry_host_ptr(0x8fe0u))));
  if ((key_length == '\x10') &&
     (uVar3 = f33_boot_aes128_ctr_initialize(timer_key,'\x10',local_14,'\x10',context), uVar3 == 0))
  {
    return 0;
  }
  return 0xff;
}



undefined4 FUN_00007316(uchar *param_1,char param_2,F33BootAes128CtrContext *param_3)

{
  uint uVar1;
  
  if (((param_2 == '\x10') && ((param_3->aes).valid == '\x01')) &&
     (uVar1 = f33_boot_aes128_ctr_initialize(param_1,'\x10',param_3->counter_be,'\x10',param_3),
     uVar1 == 0)) {
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



/* SoftwareAES128singleblock:requirelength16andcontext.valid1;row-orientedstateat+B0,10rounds,noMixColumnsinlastround,outputstandardcolumnorder.Return0success,FFinvalid.Exact-leaflive-registerpreservation
   matters:7B42callswithr8=16/r9contextalreadylive. Native AES known-answer and protocol-state cases
   use explicit RAM. Service paths stop at674A before response/timer completion; direct session
   invalidation cases return. No complete unlock or entropy claim. */

uint f33_boot_aes128_encrypt_block
               (uchar *plaintext,uchar *ciphertext,uchar length,F33BootAes128Context *context)

{
  byte bVar1;
  uint uVar2;
  
  if ((length == '\x10') && (context->valid == '\x01')) {
    context->round = '\0';
    context->row_order_state[0] = *plaintext;
    context->row_order_state[4] = plaintext[1];
    context->row_order_state[8] = plaintext[2];
    context->row_order_state[0xc] = plaintext[3];
    context->row_order_state[1] = plaintext[4];
    context->row_order_state[5] = plaintext[5];
    context->row_order_state[9] = plaintext[6];
    context->row_order_state[0xd] = plaintext[7];
    context->row_order_state[2] = plaintext[8];
    context->row_order_state[6] = plaintext[9];
    context->row_order_state[10] = plaintext[10];
    context->row_order_state[0xe] = plaintext[0xb];
    context->row_order_state[3] = plaintext[0xc];
    context->row_order_state[7] = plaintext[0xd];
    context->row_order_state[0xb] = plaintext[0xe];
    context->row_order_state[0xf] = plaintext[0xf];
    while( true ) {
      FUN_000076da(camry_host_addr(context));
      bVar1 = context->round + 1;
      context->round = bVar1;
      FUN_000077a8(camry_host_addr(context));
      FUN_0000786e(camry_host_addr(context));
      if (9 < bVar1) break;
      FUN_00007896(camry_host_addr(context));
    }
    FUN_000076da(camry_host_addr(context));
    uVar2 = 0;
    *ciphertext = context->row_order_state[0];
    ciphertext[1] = context->row_order_state[4];
    ciphertext[2] = context->row_order_state[8];
    ciphertext[3] = context->row_order_state[0xc];
    ciphertext[4] = context->row_order_state[1];
    ciphertext[5] = context->row_order_state[5];
    ciphertext[6] = context->row_order_state[9];
    ciphertext[7] = context->row_order_state[0xd];
    ciphertext[8] = context->row_order_state[2];
    ciphertext[9] = context->row_order_state[6];
    ciphertext[10] = context->row_order_state[10];
    ciphertext[0xb] = context->row_order_state[0xe];
    ciphertext[0xc] = context->row_order_state[3];
    ciphertext[0xd] = context->row_order_state[7];
    ciphertext[0xe] = context->row_order_state[0xb];
    ciphertext[0xf] = context->row_order_state[0xf];
  }
  else {
    uVar2 = 0xff;
  }
  return uVar2;
}



/* SoftwareinverseAES128singleblock;length16andvalid1;round10AddRoundKeythen10inverseShiftRows/inverseSubBytes/AddRoundKeyroundswithinverseMixColumnsonlynonfinalrounds;return0/FF.
   Native AES known-answer and protocol-state cases use explicit RAM. Service paths stop at674A
   before response/timer completion; direct session invalidation cases return. No complete unlock or
   entropy claim. */

uint f33_boot_aes128_decrypt_block
               (uchar *ciphertext,uchar *plaintext,uchar length,F33BootAes128Context *context)

{
  uchar uVar1;
  uint uVar2;
  
  if ((length == '\x10') && (context->valid == '\x01')) {
    context->round = '\n';
    context->row_order_state[0] = *ciphertext;
    context->row_order_state[4] = ciphertext[1];
    context->row_order_state[8] = ciphertext[2];
    context->row_order_state[0xc] = ciphertext[3];
    context->row_order_state[1] = ciphertext[4];
    context->row_order_state[5] = ciphertext[5];
    context->row_order_state[9] = ciphertext[6];
    context->row_order_state[0xd] = ciphertext[7];
    context->row_order_state[2] = ciphertext[8];
    context->row_order_state[6] = ciphertext[9];
    context->row_order_state[10] = ciphertext[10];
    context->row_order_state[0xe] = ciphertext[0xb];
    context->row_order_state[3] = ciphertext[0xc];
    context->row_order_state[7] = ciphertext[0xd];
    context->row_order_state[0xb] = ciphertext[0xe];
    context->row_order_state[0xf] = ciphertext[0xf];
    FUN_000076da(camry_host_addr(context));
    while( true ) {
      uVar1 = context->round + 0xff;
      context->round = uVar1;
      FUN_000079ee(camry_host_addr(context));
      FUN_00007928(camry_host_addr(context));
      FUN_000076da(camry_host_addr(context));
      if (uVar1 == '\0') break;
      FUN_00007a16(camry_host_addr(context));
    }
    *plaintext = context->row_order_state[0];
    plaintext[1] = context->row_order_state[4];
    plaintext[2] = context->row_order_state[8];
    plaintext[3] = context->row_order_state[0xc];
    plaintext[4] = context->row_order_state[1];
    plaintext[5] = context->row_order_state[5];
    plaintext[6] = context->row_order_state[9];
    plaintext[7] = context->row_order_state[0xd];
    plaintext[8] = context->row_order_state[2];
    plaintext[9] = context->row_order_state[6];
    plaintext[10] = context->row_order_state[10];
    plaintext[0xb] = context->row_order_state[0xe];
    plaintext[0xc] = context->row_order_state[3];
    plaintext[0xd] = context->row_order_state[7];
    plaintext[0xe] = context->row_order_state[0xb];
    plaintext[0xf] = context->row_order_state[0xf];
    uVar2 = 0;
  }
  else {
    uVar2 = 0xff;
  }
  return uVar2;
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



/* WARNING: Inlined function: f33_boot_aes128_expand_round_keys */
/* Only16-bytekeyaccepted;clearstate/valid/round,expand44words=176byteswith7594,setvalid1.Return0orFF.7594preserveslivecontextpointerr8at76ACdespiteordinarydecompilerextraout_r8;useexistingexact-leafinliningconventionratherthaninventingextraABIresult.
   Native AES known-answer and protocol-state cases use explicit RAM. Service paths stop at674A
   before response/timer completion; direct session invalidation cases return. No complete unlock or
   entropy claim. */

uint f33_boot_aes128_initialize_context(uchar *key,uchar key_length,F33BootAes128Context *context)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  
  if (key_length == '\x10') {
    context->valid = '\0';
    context->row_order_state[0] = '\0';
    context->row_order_state[1] = '\0';
    context->row_order_state[2] = '\0';
    context->row_order_state[3] = '\0';
    context->row_order_state[4] = '\0';
    context->row_order_state[5] = '\0';
    context->row_order_state[6] = '\0';
    context->row_order_state[7] = '\0';
    context->row_order_state[8] = '\0';
    context->row_order_state[9] = '\0';
    context->row_order_state[10] = '\0';
    context->row_order_state[0xb] = '\0';
    context->row_order_state[0xc] = '\0';
    context->row_order_state[0xd] = '\0';
    context->row_order_state[0xe] = '\0';
    context->row_order_state[0xf] = '\0';
    context->round = '\0';
    uVar2 = 4;
    context->round_keys[0] = *key;
    context->round_keys[1] = key[1];
    context->round_keys[2] = key[2];
    context->round_keys[3] = key[3];
    context->round_keys[4] = key[4];
    context->round_keys[5] = key[5];
    context->round_keys[6] = key[6];
    context->round_keys[7] = key[7];
    context->round_keys[8] = key[8];
    context->round_keys[9] = key[9];
    context->round_keys[10] = key[10];
    context->round_keys[0xb] = key[0xb];
    context->round_keys[0xc] = key[0xc];
    context->round_keys[0xd] = key[0xd];
    context->round_keys[0xe] = key[0xe];
    context->round_keys[0xf] = key[0xf];
    do {
      iVar1 = uVar2 * 4;
      uVar3 = *(uint *)(context->round_keys + iVar1 + -4);
      if ((uVar2 & 3) == 0) {
        uVar3 = (uint)CRYPT_AES_Encryption_SBox[uVar3 & 0xff] << 0x18 |
                (uint)CRYPT_AES_Encryption_SBox[uVar3 >> 0x18] << 0x10 |
                (uint)CRYPT_AES_Encryption_SBox[(uVar3 >> 8 & 0xffff) >> 8] << 8 |
                (uint)((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x8fe0u + (uint32_t)((int)uVar2 >> 2) * 1u)))) ^
                      CRYPT_AES_Encryption_SBox[uVar3 >> 8 & 0xff]);
      }
      uVar2 = uVar2 + 1 & 0xffff;
      *(uint *)(context->round_keys + iVar1) =
           *(uint *)(context->round_keys + iVar1 + -0x10) ^ uVar3;
    } while (uVar2 < 0x2c);
    context->valid = '\x01';
    uVar2 = 0;
  }
  else {
    uVar2 = 0xff;
  }
  return uVar2;
}



void FUN_000076b6(undefined4 *param_1,int param_2)

{
  for (; param_2 != 0; param_2 = param_2 + -4) {
    *param_1 = 0;
    param_1 = param_1 + 1;
  }
  return;
}



/* Clearvalidthenall196bytesvia76B6wordzero loop. Native AES known-answer and protocol-state cases
   use explicit RAM. Service paths stop at674A before response/timer completion; direct session
   invalidation cases return. No complete unlock or entropy claim. */

void f33_boot_aes128_clear_context(F33BootAes128Context *context)

{
  context->valid = '\0';
  FUN_000076b6(context,0xc4);
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



/* Require length16, valid context and counter not allFF. Encrypt counter, XOR16 input bytes into
   output, increment counter as128-bit big-endian. Return0 orFF. R8 length andR9 context remain live
   for7352; not an arbitrary-length streaming API. */

uint f33_boot_aes128_ctr_transform_block
               (uchar *input,uchar *output,uchar length,F33BootAes128CtrContext *context)

{
  uchar *puVar1;
  int iVar2;
  uchar uVar3;
  uint uVar4;
  int iVar5;
  uchar *plaintext;
  byte local_20;
  byte bStack_1f;
  byte bStack_1e;
  byte bStack_1d;
  byte bStack_1c;
  byte bStack_1b;
  byte bStack_1a;
  byte bStack_19;
  byte bStack_18;
  byte bStack_17;
  byte bStack_16;
  byte bStack_15;
  byte bStack_14;
  byte bStack_13;
  byte bStack_12;
  byte bStack_11;
  
  if ((((length == '\x10') && ((context->aes).valid == '\x01')) &&
      ((plaintext = context->counter_be, *(int *)context->counter_be != -1 ||
       (((*(int *)(context->counter_be + 4) != -1 || (*(int *)(context->counter_be + 8) != -1)) ||
        (*(int *)(context->counter_be + 0xc) != -1)))))) &&
     (uVar4 = f33_boot_aes128_encrypt_block(plaintext,&local_20,'\x10',&context->aes), uVar4 == 0))
  {
    *output = *input ^ local_20;
    output[1] = input[1] ^ bStack_1f;
    output[2] = input[2] ^ bStack_1e;
    output[3] = input[3] ^ bStack_1d;
    output[4] = input[4] ^ bStack_1c;
    output[5] = input[5] ^ bStack_1b;
    output[6] = input[6] ^ bStack_1a;
    output[7] = input[7] ^ bStack_19;
    output[8] = input[8] ^ bStack_18;
    output[9] = input[9] ^ bStack_17;
    output[10] = input[10] ^ bStack_16;
    output[0xb] = input[0xb] ^ bStack_15;
    output[0xc] = input[0xc] ^ bStack_14;
    output[0xd] = input[0xd] ^ bStack_13;
    output[0xe] = input[0xe] ^ bStack_12;
    output[0xf] = input[0xf] ^ bStack_11;
    iVar5 = 3;
    do {
      iVar2 = iVar5 * 4;
      uVar3 = plaintext[iVar2 + 3];
      plaintext[iVar2 + 3] = uVar3 + '\x01';
      if (((uchar)(uVar3 + '\x01') == '\0') &&
         (uVar3 = plaintext[iVar2 + 2], plaintext[iVar2 + 2] = uVar3 + '\x01',
         (uchar)(uVar3 + '\x01') == '\0')) {
        puVar1 = plaintext + iVar2;
        uVar3 = puVar1[1];
        puVar1[1] = uVar3 + '\x01';
        if ((uchar)(uVar3 + '\x01') == '\0') {
          *puVar1 = *puVar1 + '\x01';
        }
      }
      uVar4 = 0;
    } while ((*(int *)(plaintext + iVar5 * 4) == 0) &&
            (iVar2 = iVar5 + -1, iVar5 = iVar5 + -1, -1 < iVar2));
  }
  else {
    uVar4 = 0xff;
  }
  return uVar4;
}



/* Require low8 key/counter lengths16. Fifth argument is context at callerSP+0, calleeSP+8 after
   saves. Clear extension, copy16-byte big-endian counter to+D4 and initialize AES context. Return0
   success orFF invalid. */

uint f33_boot_aes128_ctr_initialize
               (uchar *key,uchar key_length,uchar *counter,uchar counter_length,
               F33BootAes128CtrContext *context)

{
  uint uVar1;
  
  if ((key_length == '\x10') && (counter_length == '\x10')) {
    context->cleared_extension[0] = '\0';
    context->cleared_extension[1] = '\0';
    context->cleared_extension[2] = '\0';
    context->cleared_extension[3] = '\0';
    context->cleared_extension[4] = '\0';
    context->cleared_extension[5] = '\0';
    context->cleared_extension[6] = '\0';
    context->cleared_extension[7] = '\0';
    context->cleared_extension[8] = '\0';
    context->cleared_extension[9] = '\0';
    context->cleared_extension[10] = '\0';
    context->cleared_extension[0xb] = '\0';
    context->cleared_extension[0xc] = '\0';
    context->cleared_extension[0xd] = '\0';
    context->cleared_extension[0xe] = '\0';
    context->cleared_extension[0xf] = '\0';
    (context->aes).valid = '\0';
    context->counter_be[0] = *counter;
    context->counter_be[1] = counter[1];
    context->counter_be[2] = counter[2];
    context->counter_be[3] = counter[3];
    context->counter_be[4] = counter[4];
    context->counter_be[5] = counter[5];
    context->counter_be[6] = counter[6];
    context->counter_be[7] = counter[7];
    context->counter_be[8] = counter[8];
    context->counter_be[9] = counter[9];
    context->counter_be[10] = counter[10];
    context->counter_be[0xb] = counter[0xb];
    context->counter_be[0xc] = counter[0xc];
    context->counter_be[0xd] = counter[0xd];
    context->counter_be[0xe] = counter[0xe];
    context->counter_be[0xf] = counter[0xf];
    uVar1 = f33_boot_aes128_initialize_context(key,'\x10',&context->aes);
    if (uVar1 == 0) {
      (context->aes).valid = '\x01';
      return 0;
    }
  }
  return 0xff;
}



/* Clear valid then all228 context bytes through76B6. Does not clear caller stack buffers or
   retained challenge history. */

void f33_boot_aes128_ctr_clear(F33BootAes128CtrContext *context)

{
  (context->aes).valid = '\0';
  FUN_000076b6(context,0xe4);
  return;
}



/* AES_K(16 zero ROM91F1 bytes), then big-endian128-bit doubling twice; XOR87 into low byte for each
   high-bit carry. Store K1 at+D4,K2 at+E4,ready1 at+F4. Return0/FF. */

uint f33_boot_aes128_cmac_derive_subkeys(F33BootAes128CmacContext *context)

{
  int iVar1;
  uchar uVar2;
  uchar *puVar3;
  int iVar4;
  uint uVar5;
  bool bVar6;
  uchar *puVar7;
  byte local_28 [16];
  uchar local_18 [16];
  
  puVar7 = "";
  puVar3 = local_18;
  do {
    uVar2 = *puVar7;
    puVar7 = puVar7 + 1;
    *puVar3 = uVar2;
    puVar3 = puVar3 + 1;
  } while ((uintptr_t)(puVar7)!=(uintptr_t)(((undefined *)camry_host_ptr(0x9201u))));
  if (((context->aes).valid == '\x01') &&
     (uVar5 = f33_boot_aes128_encrypt_block(local_18,local_28,'\x10',&context->aes), uVar5 == 0)) {
    puVar7 = context->subkey1;
    bVar6 = false;
    iVar4 = 0xf;
    do {
      puVar7[iVar4] = bVar6 | local_28[iVar4] << 1;
      bVar6 = (local_28[iVar4] & 0x80) != 0;
      iVar1 = iVar4 + -1;
      iVar4 = iVar4 + -1;
    } while (-1 < iVar1);
    if ((char)local_28[0] < '\0') {
      context->subkey1[0xf] = context->subkey1[0xf] ^ 0x87;
    }
    bVar6 = false;
    iVar4 = 0xf;
    do {
      context->subkey2[iVar4] = bVar6 | puVar7[iVar4] << 1;
      bVar6 = (puVar7[iVar4] & 0x80) != 0;
      iVar1 = iVar4 + -1;
      iVar4 = iVar4 + -1;
    } while (-1 < iVar1);
    if ((*puVar7 & 0x80) != 0) {
      context->subkey2[0xf] = context->subkey2[0xf] ^ 0x87;
    }
    context->subkeys_ready = '\x01';
    uVar5 = 0;
  }
  else {
    uVar5 = 0xff;
  }
  return uVar5;
}



/* AES128-CMAC update. Nonfinal length16; final==1 allows1..16 (zero rejected). Full final XOR K1;
   partial final80/zero pad XOR K2. XOR retained chain, encrypt, copy output to chain. Require
   AES.valid1/subkeys_ready1. Return0/FF; does NOT invalidate/finalize-latch or wipe. Fifth arg
   callerSP+0. */

uint f33_boot_aes128_cmac_update_block
               (uchar *input,uchar *output,uchar length,uint final_block,
               F33BootAes128CmacContext *context)

{
  uchar *puVar1;
  byte *pbVar2;
  uint uVar3;
  uint uVar4;
  byte bVar5;
  byte *pbVar6;
  byte local_2c [16];
  byte bStack_1c;
  byte bStack_1b;
  byte bStack_1a;
  byte bStack_19;
  byte bStack_18;
  byte bStack_17;
  byte bStack_16;
  byte bStack_15;
  byte bStack_14;
  byte bStack_13;
  byte bStack_12;
  byte bStack_11;
  byte bStack_10;
  byte bStack_f;
  byte bStack_e;
  byte bStack_d;
  
  uVar4 = (uint)length;
  if (final_block == 1) {
    if (0xf < uVar4 - 1) {
      return 0xff;
    }
  }
  else if (uVar4 != 0x10) {
    return 0xff;
  }
  if (((context->aes).valid == '\x01') && (context->subkeys_ready == '\x01')) {
    pbVar6 = input;
    if (final_block == 1) {
      uVar3 = 0;
      if (uVar4 == 0x10) {
        do {
          pbVar6 = input + uVar3;
          puVar1 = context->subkey1 + uVar3;
          pbVar2 = local_2c + uVar3;
          uVar3 = uVar3 + 1;
          *pbVar2 = *pbVar6 ^ *puVar1;
          pbVar6 = local_2c;
        } while (uVar3 < 0x10);
      }
      else {
        do {
          if (uVar3 < uVar4) {
            bVar5 = input[uVar3];
          }
          else {
            bVar5 = 0;
            if (uVar3 == uVar4) {
              bVar5 = 0x80;
            }
          }
          pbVar6 = local_2c + uVar3;
          *pbVar6 = bVar5;
          puVar1 = context->subkey2 + uVar3;
          uVar3 = uVar3 + 1;
          *pbVar6 = *puVar1 ^ bVar5;
          pbVar6 = local_2c;
        } while (uVar3 < 0x10);
      }
    }
    bStack_1c = *pbVar6 ^ context->chain[0];
    bStack_1b = pbVar6[1] ^ context->chain[1];
    bStack_1a = pbVar6[2] ^ context->chain[2];
    bStack_19 = pbVar6[3] ^ context->chain[3];
    bStack_18 = pbVar6[4] ^ context->chain[4];
    bStack_17 = pbVar6[5] ^ context->chain[5];
    bStack_16 = pbVar6[6] ^ context->chain[6];
    bStack_15 = pbVar6[7] ^ context->chain[7];
    bStack_14 = pbVar6[8] ^ context->chain[8];
    bStack_13 = pbVar6[9] ^ context->chain[9];
    bStack_12 = pbVar6[10] ^ context->chain[10];
    bStack_11 = pbVar6[0xb] ^ context->chain[0xb];
    bStack_10 = pbVar6[0xc] ^ context->chain[0xc];
    bStack_f = pbVar6[0xd] ^ context->chain[0xd];
    bStack_e = pbVar6[0xe] ^ context->chain[0xe];
    bStack_d = pbVar6[0xf] ^ context->chain[0xf];
    uVar4 = f33_boot_aes128_encrypt_block(&bStack_1c,output,'\x10',&context->aes);
    if (uVar4 == 0) {
      *(undefined4 *)context->chain = *(undefined4 *)output;
      *(undefined4 *)(context->chain + 4) = *(undefined4 *)(output + 4);
      *(undefined4 *)(context->chain + 8) = *(undefined4 *)(output + 8);
      *(undefined4 *)(context->chain + 0xc) = *(undefined4 *)(output + 0xc);
      return 0;
    }
  }
  return 0xff;
}



/* Require key length16, clear AES.valid and49-byte chain/K1/K2/ready extension, initialize shared
   AES base. Does not derive subkeys;7D50 required separately. Return0/FF. */

uint f33_boot_aes128_cmac_initialize(uchar *key,uchar key_length,F33BootAes128CmacContext *context)

{
  uint uVar1;
  
  if (key_length == '\x10') {
    (context->aes).valid = '\0';
    context->chain[0] = '\0';
    context->chain[1] = '\0';
    context->chain[2] = '\0';
    context->chain[3] = '\0';
    context->chain[4] = '\0';
    context->chain[5] = '\0';
    context->chain[6] = '\0';
    context->chain[7] = '\0';
    context->chain[8] = '\0';
    context->chain[9] = '\0';
    context->chain[10] = '\0';
    context->chain[0xb] = '\0';
    context->chain[0xc] = '\0';
    context->chain[0xd] = '\0';
    context->chain[0xe] = '\0';
    context->chain[0xf] = '\0';
    context->subkey1[0] = '\0';
    context->subkey1[1] = '\0';
    context->subkey1[2] = '\0';
    context->subkey1[3] = '\0';
    context->subkey1[4] = '\0';
    context->subkey1[5] = '\0';
    context->subkey1[6] = '\0';
    context->subkey1[7] = '\0';
    context->subkey1[8] = '\0';
    context->subkey1[9] = '\0';
    context->subkey1[10] = '\0';
    context->subkey1[0xb] = '\0';
    context->subkey1[0xc] = '\0';
    context->subkey1[0xd] = '\0';
    context->subkey1[0xe] = '\0';
    context->subkey1[0xf] = '\0';
    context->subkey2[0] = '\0';
    context->subkey2[1] = '\0';
    context->subkey2[2] = '\0';
    context->subkey2[3] = '\0';
    context->subkey2[4] = '\0';
    context->subkey2[5] = '\0';
    context->subkey2[6] = '\0';
    context->subkey2[7] = '\0';
    context->subkey2[8] = '\0';
    context->subkey2[9] = '\0';
    context->subkey2[10] = '\0';
    context->subkey2[0xb] = '\0';
    context->subkey2[0xc] = '\0';
    context->subkey2[0xd] = '\0';
    context->subkey2[0xe] = '\0';
    context->subkey2[0xf] = '\0';
    context->subkeys_ready = '\0';
    uVar1 = f33_boot_aes128_initialize_context(key,'\x10',&context->aes);
    if (uVar1 == 0) {
      (context->aes).valid = '\x01';
      return 0;
    }
  }
  return 0xff;
}



/* Clear valid then all248 CMAC context bytes through76B6; not caller configured key/material or
   output. */

void f33_boot_aes128_cmac_clear(F33BootAes128CmacContext *context)

{
  (context->aes).valid = '\0';
  FUN_000076b6(context,0xf8);
  return;
}


