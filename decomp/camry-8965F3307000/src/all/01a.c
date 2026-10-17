#include "common.h"


bool FUN_0006805e(void)

{
  undefined1 uVar1;
  uint32_t puVar2;
  uchar uStack_6;
  uchar uStack_5;
  
  puVar2 = 0xfebeb800u;
  f33_nvm_recover_family1_request_indices(&uStack_6,&uStack_5);
  if (uStack_6 == uStack_5) {
    uVar1 = 0x5a;
  }
  else {
    uVar1 = 0xff;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x4e88))))) = uVar1;
  return uStack_6 == uStack_5;
}



undefined4 FUN_0006808e(void)

{
  int iVar1;
  undefined8 uVar2;
  undefined4 uVar3;
  int iVar4;
  
  uVar2 = 0xfebeb800;
  uVar3 = 0;
  if (f33_nvm_family1_span_request == 0xa5) {
    for (iVar4 = 0; iVar1 = (int)uVar2,
        (int)(iVar4 - (uint)f33_nvm_family1_object_count) < 0 !=
        (iVar4 < 0 && -1 < (int)(iVar4 - (uint)f33_nvm_family1_object_count)); iVar4 = iVar4 + 1) {
      f33_publish_redundant_u8
                ('\x11',((uchar *)camry_host_ptr((uint32_t)(iVar1 + 0x4b28 + iVar4))),((uchar *)camry_host_ptr((uint32_t)(iVar1 + 0x5888 + iVar4))),
                 ((uchar *)camry_host_ptr((uint32_t)(iVar1 + 0x58ac + iVar4))));
    }
    (*((undefined1 *)camry_host_ptr((uint32_t)(iVar1 + 0x4e88)))) = 0;
    uVar3 = 1;
  }
  else if (f33_nvm_family1_span_request == 0xff) {
    for (iVar4 = 0; iVar1 = (int)uVar2,
        (int)(iVar4 - (uint)f33_nvm_family1_object_count) < 0 !=
        (iVar4 < 0 && -1 < (int)(iVar4 - (uint)f33_nvm_family1_object_count)); iVar4 = iVar4 + 1) {
      f33_publish_redundant_u8
                ('1',((uchar *)camry_host_ptr((uint32_t)(iVar1 + 0x4b28 + iVar4))),((uchar *)camry_host_ptr((uint32_t)(iVar1 + 0x5888 + iVar4))),
                 ((uchar *)camry_host_ptr((uint32_t)(iVar1 + 0x58ac + iVar4))));
    }
    (*((undefined1 *)camry_host_ptr((uint32_t)(iVar1 + 0x4e88)))) = 0;
    uVar3 = 0xffffffff;
  }
  return uVar3;
}



undefined4 FUN_000681aa(void)

{
  int iVar1;
  undefined8 uVar2;
  uint uVar3;
  uint uVar4;
  
  uVar2 = 0xfebeb800;
  uVar4 = 0;
  while( true ) {
    if (f33_nvm_family1_object_count <= uVar4) {
      return 1;
    }
    iVar1 = (int)uVar2;
    uVar3 = f33_read_repair_redundant_u8
                      (camry_host_addr(((uchar *)camry_host_ptr((uint32_t)(iVar1 + 0x4b28 + uVar4)))), camry_host_addr(((uchar *)camry_host_ptr((uint32_t)(iVar1 + 0x5888 + uVar4)))), camry_host_addr(((uchar *)camry_host_ptr((uint32_t)(iVar1 + 0x58ac + uVar4)))), '\x12');
    if ((uVar3 & 0xf0) == 0x20) break;
    uVar4 = uVar4 + 1 & 0xffff;
  }
  return 0;
}



/* Return zero-extended byte0689; snapshot precedes hold decoding. Exact LDBU0689 into full32r10
   thenJMPLP. Native work-selection calls snapshot this family1 phase before hold repair and prefer
   it when both phases are active. */

uint f33_nvm_get_family1_phase(void)

{
  return (uint)f33_nvm_family1_phase;
}



/* Clear family0/1 completion; set family0 objectsFFFF/counters0; clear 0690..0694, four failure
   masks, write staging, four read stages and both1024-byte buffers0708/0C88. Then
   call79B1E,73F0A,764E2; no lower initialization result is propagated. Native19535 instructions
   with explicit ICU-S zero and externally completed FACI forced stop. ICU-S bit0 rejection still
   returns after RAM initialization, preserving prior6CB0/6CB2/6CB3 and setting6CB1=1. Not acquired
   application data. Initialize completion/bookkeeping and both1024-byte buffers then
   actual79B1E/73F0A/764E2. Full19535-instruction normal call uses explicit ICU-S input and external
   forced-stop completion. Lower ICUS rejection still finishes RAM initialization and preserves
   prior admission bytes while setting6CB1=1; no propagated success status or acquired-data claim.
    */

void f33_nvm_initialize_acquisition(void)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  short sVar4;
  
  f33_nvm_family0_busy = '\0';
  f33_nvm_family1_busy = '\0';
  uVar2 = 0;
  do {
    uVar3 = uVar2 + 1;
    f33_nvm_family1_copy_failure_masks[uVar2] = 0;
    uVar2 = uVar3;
  } while (uVar3 < 4);
  for (uVar2 = 0; uVar2 < f33_nvm_family0_object_count; uVar2 = uVar2 + 1 & 0xffff) {
    f33_nvm_family0_completion[uVar2] = '\0';
    f33_nvm_family0_selected_logical_handles[uVar2] = 0xffff;
    f33_nvm_family0_sequences[uVar2] = 0;
  }
  for (uVar2 = 0; uVar2 < f33_nvm_family1_object_count; uVar2 = uVar2 + 1 & 0xffff) {
    f33_nvm_family1_completion[uVar2] = '\0';
  }
  uVar2 = 0;
  do {
    f33_nvm_family0_write_record[uVar2] = '\0';
    f33_nvm_family0_read_record[uVar2] = '\0';
    uVar2 = uVar2 + 1;
  } while (uVar2 < 0x400);
  uVar2 = 0;
  do {
    uVar3 = 0;
    do {
      sVar4 = (short)uVar2;
      uVar1 = uVar3 + 1;
      f33_nvm_family1_read_stages[sVar4].raw[uVar3] = '\0';
      f33_nvm_family1_read_stages[sVar4].xor55[uVar3] = '\0';
      f33_nvm_family1_read_stages[sVar4].xorAA[uVar3] = '\0';
      uVar3 = uVar1;
    } while (uVar1 < 0x20);
    uVar2 = uVar2 + 1;
  } while (uVar2 < 4);
  uVar2 = 0;
  do {
    f33_nvm_family1_write_stage.raw[uVar2] = '\0';
    uVar3 = uVar2 + 1;
    f33_nvm_family1_write_stage.xor55[uVar2] = '\0';
    f33_nvm_family1_write_stage.xorAA[uVar2] = '\0';
    uVar2 = uVar3;
  } while (uVar3 < 0x20);
  f33_nvm_initial_read_token = '\0';
  f33_nvm_direct_operation_request = '\0';
  f33_nvm_copy_read_retry = '\0';
  FUN_00079b1e();
  f33_nvm_initialize_logical_module();
  f33_run_init_chain_764e2();
  return;
}



/* Always call74114 first. If either family busy byte equalsA5, poll and normalize result. Retain
   both flags and direct-operation request only for result1; any other result clears both busy bytes
   and request, then performs real mode-exit cancellation/reconciliation. */

void f33_nvm_service_and_release_erase_span(void)

{
  uint32_t puVar1;
  uint uVar2;
  
  puVar1 = 0xfebeb800u;
  f33_nvm_service_application_cycle();
  if ((((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x4e90)))))) == -0x5b) || (((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x4e91)))))) == -0x5b)) {
    f33_nvm_poll_direct_operation();
    uVar2 = f33_nvm_get_direct_operation_result();
    if (uVar2 != 1) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x4e90))))) = 0;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x4e91))))) = 0;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x4e92u + (uint32_t)((int)(puVar1 + 1)))))) = (code)0x0;
      f33_nvm_poll_probe_mode();
    }
  }
  return;
}



void FUN_00068318(void)

{
  f33_nvm_service_acquisition_driver();
  return;
}



/* Store only5A to0692; does not submit or complete any request. Exact three instructions store5A
   only to0692. Real bounded bootstrap then consumes that arm token; the store itself does not
   submit or complete requests. */

void f33_nvm_arm_initial_read_acquisition(void)

{
  f33_nvm_initial_read_token = 'Z';
  return;
}



/* Truncate page/count independently to16 bits and shift by6. Set direct-operation request5A and
   reconcile. Call794DA; return0 and retain mode only for result7. Otherwise clear request, perform
   real cancellation/reconciliation and returnFF. Native admitted path is bounded before opcode20,
   not erased data. */

uint f33_nvm_begin_page_erase_span(uint first_page,uint page_count)

{
  uint32_t puVar1;
  uint uVar2;
  
  puVar1 = 0xfebeb800u;
  f33_nvm_direct_operation_request = 'Z';
  f33_nvm_poll_probe_mode();
  uVar2 = f33_nvm_request_erase_span(0,(first_page & 0xffff) << 6,(page_count & 0xffff) << 6);
  if (uVar2 == 7) {
    uVar2 = 0;
  }
  else {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x4e92u + (uint32_t)((int)(puVar1 + 1)))))) = (code)0x0;
    f33_nvm_poll_probe_mode();
    uVar2 = 0xff;
  }
  return uVar2;
}



/* Busy nonzero returnsFF. Otherwise map every enabled object's logical members; retain
   minimum/maximum pages and logical owner of the first strictly greatest page. Add that owner's
   chunk cost to the maximum; call6879C(min,low16(max+cost-min)). Return its result; zero sets
   busyA5. Exact table computes page10C/count164. Native admitted proof stops BEFORE6879C; no
   completed range operation. Map every enabled logical member; retain min/max pages and owner of
   first strict maximum. Extent uses highest owner chunk cost; exact input produces min10C and164
   pages. Native real mapping loops stop before6879C. Source return0 sets family busyA5. This proves
   selected span, not accepted or completed physical operation. */

uint f33_nvm_dispatch_family0_page_span(void)

{
  uint uVar1;
  uint uVar2;
  int iVar3;
  undefined8 uVar4;
  uint uVar5;
  uint uVar6;
  uint unaff_r24;
  uint uVar7;
  uint first_page;
  uint uVar8;
  uint uVar9;
  ushort uStack_1e;
  
  uVar4 = 0xfebeb800;
  if (f33_nvm_family0_busy == '\0') {
    first_page = 0xffff;
    uVar6 = 0;
    for (uVar2 = 0; iVar3 = (int)uVar4, uVar2 < f33_nvm_family0_object_count;
        uVar2 = uVar2 + 1 & 0xffff) {
      uVar9 = (uint)f33_nvm_family0_ram_descriptors[uVar2].first_logical_handle;
      if (uVar9 != 0xffff) {
        iVar3 = f33_nvm_family0_ram_descriptors[uVar2].logical_count + uVar9;
        for (; uVar9 <= (iVar3 - 1U & 0xffff); uVar9 = uVar9 + 1 & 0xffff) {
          uVar5 = f33_nvm_get_logical_storage_page((ushort)uVar9,&uStack_1e);
          uVar7 = unaff_r24;
          uVar1 = uVar6;
          uVar8 = first_page;
          if (uVar5 == 0) {
            uVar1 = (uint)uStack_1e;
            uVar8 = uVar1;
            if (first_page <= uVar1) {
              uVar8 = first_page;
            }
            uVar7 = uVar9;
            if (uVar1 <= uVar6) {
              uVar7 = unaff_r24;
              uVar1 = uVar6;
            }
          }
          unaff_r24 = uVar7;
          uVar6 = uVar1;
          first_page = uVar8;
        }
      }
    }
    uVar2 = (ushort)(f33_nvm_family0_ram_descriptors
                     [f33_nvm_logical_application_routes[unaff_r24].object].payload_bytes + 0x14) +
            0x3f >> 6;
    if (uVar2 < 2) {
      uVar2 = 2;
    }
    uVar6 = f33_nvm_begin_page_erase_span(first_page,(uVar2 + uVar6) - first_page & 0xffff);
    if (uVar6 == 0) {
      (*((undefined1 *)camry_host_ptr((uint32_t)(iVar3 + 0x4e90)))) = 0xa5;
    }
  }
  else {
    uVar6 = 0xff;
  }
  return uVar6;
}



/* Busy nonzero returnsFF. Map enabled base/+4/+8 handles, accumulating min/max successful pages.
   Call6879C(min,max+1-min); zero result sets busyA5. Exact table computes page1B0/count48. Native
   admitted proof stops BEFORE6879C; no physical operation claim. Map each enabled base/+4/+8;
   extent=max+1-min. Exact input produces min1B0 and48 pages. Native real mapping loops stop
   before6879C. Source return0 sets family busyA5. This proves selected span, not accepted or
   completed physical operation. */

uint f33_nvm_dispatch_family1_page_span(void)

{
  ushort uVar1;
  int iVar2;
  undefined8 uVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  uint first_page;
  uint uVar7;
  uint uVar8;
  uint uVar9;
  ushort uStack_1a;
  
  uVar3 = 0xfebeb800;
  if (f33_nvm_family1_busy == '\0') {
    first_page = 0xffff;
    uVar5 = 0;
    for (uVar9 = 0; iVar2 = (int)uVar3, uVar9 < f33_nvm_family1_object_count;
        uVar9 = uVar9 + 1 & 0xffff) {
      uVar1 = f33_nvm_family1_ram_descriptors[uVar9].first_logical_handle;
      if (uVar1 != 0xffff) {
        uVar8 = 0;
        uVar6 = uVar5;
        uVar7 = first_page;
        do {
          uVar4 = f33_nvm_get_logical_storage_page((short)uVar8 * 4 + uVar1,&uStack_1a);
          uVar5 = uVar6;
          first_page = uVar7;
          if (uVar4 == 0) {
            uVar5 = (uint)uStack_1a;
            first_page = uVar5;
            if (uVar7 <= uVar5) {
              first_page = uVar7;
            }
            if (uVar5 <= uVar6) {
              uVar5 = uVar6;
            }
          }
          uVar8 = uVar8 + 1;
          uVar6 = uVar5;
          uVar7 = first_page;
        } while (uVar8 < 3);
      }
    }
    uVar5 = f33_nvm_begin_page_erase_span(first_page,(uVar5 + 1) - first_page & 0xffff);
    if (uVar5 == 0) {
      (*((undefined1 *)camry_host_ptr((uint32_t)(iVar2 + 0x4e91)))) = 0xa5;
    }
  }
  else {
    uVar5 = 0xff;
  }
  return uVar5;
}



uchar FUN_00068924(void)

{
  return f33_nvm_family0_busy;
}



/* Bound low16 object by registered32; return zero-extended0338 byte, orA5 without reading
   completion RAM when out of range. Low16 object<registered32 returns zero-extended0338 byte;
   otherwiseA5 before array access. Exact ten-instruction gate plus native full32-object acquisition
   passes; malformed-index path is byte/disassembly evidence, not a separate native execution. */

uint f33_nvm_get_family0_completion(ushort object)

{
  if ((uint)object < (uint)f33_nvm_family0_object_count) {
    return (uint)f33_nvm_family0_completion[object];
  }
  return 0xa5;
}



/* Reject invalid/disabled object or last-member page-map error withFF before mode changes.
   Otherwise base=(low16(mapped_last_page+offset)<<6); set0693=5A/reconcile once, probe count64-byte
   chunks in ascending order. Continue only on class2; every other class yields0, including driver
   errors, unlike68A6C. All2 or count0 yields5A. Clear/reconcile once, including real cancellation.
   Native blank/nonblank, blocked, zero-count and invalid-object paths; explicit FACI inputs do not
   prove blankness. Invalid/disabled object or last-member map error returnsFF before mode changes.
   Start=(low16(mapped_last_page+offset)<<6), enter0693=5A/reconcile, probe ascending64-byte chunks,
   then clear/reconcile with actual cancellation. any other class returns0 including lower driver
   rejection. All2 or zero count returns5A. Native explicit blank/nonblank events, blocked probe,
   zero count, invalid object and disabled caller. No payload publication or physical blankness
   claim. */

uint f33_nvm_classify_family0_chunks(ushort object,ushort chunk_offset,ushort chunk_count)

{
  undefined8 uVar1;
  uint uVar2;
  uint uVar3;
  ushort uVar4;
  uint uVar5;
  ushort uStack_16;
  
  uVar1 = 0xfebeb800;
  uVar2 = (uint)object;
  uVar5 = 0xff;
  if (uVar2 < f33_nvm_family0_object_count) {
    if ((f33_nvm_family0_ram_descriptors[uVar2].first_logical_handle != 0xffff) &&
       (uVar2 = f33_nvm_get_logical_storage_page
                          ((f33_nvm_family0_ram_descriptors[uVar2].logical_count +
                           f33_nvm_family0_ram_descriptors[uVar2].first_logical_handle) - 1,
                           &uStack_16), uVar2 == 0)) {
      uVar5 = 0x5a;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x4e92u + (uint32_t)((int)uVar1 + 1))))) = (code)0x5a;
      uVar2 = (uint)(ushort)(chunk_offset + uStack_16) << 6;
      f33_nvm_poll_probe_mode();
      uVar4 = 0;
      while ((uVar4 < chunk_count && (uVar5 == 0x5a))) {
        uVar3 = f33_nvm_classify_storage_range(0,uVar2,0x40);
        if (uVar3 != 2) {
          uVar5 = 0;
        }
        uVar4 = uVar4 + 1;
        uVar2 = uVar2 + 0x40;
      }
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x4e92u + (uint32_t)((int)uVar1 + 1))))) = (code)0x0;
      f33_nvm_poll_probe_mode();
    }
  }
  return uVar5;
}



undefined4 FUN_000689f2(uint param_1,undefined4 param_2,uint param_3)

{
  uint32_t puVar1;
  uint uVar2;
  int iVar3;
  undefined4 uVar4;
  
  puVar1 = 0xfebeb800u;
  f33_nvm_direct_operation_request = 'Z';
  f33_nvm_poll_probe_mode();
  uVar2 = f33_nvm_classify_storage_range(0,param_1 & 0xffff,param_3);
  if (uVar2 == 3) {
    iVar3 = FUN_00079554(0,param_1 & 0xffff,param_2,param_3);
    uVar4 = 0;
    if (iVar3 == 0) goto LAB_00068a3a;
  }
  else if (uVar2 == 2) {
    uVar4 = 0x5a;
    goto LAB_00068a3a;
  }
  uVar4 = 0xff;
LAB_00068a3a:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x4e92u + (uint32_t)((int)(puVar1 + 1)))))) = (code)0x0;
  f33_nvm_poll_probe_mode();
  return uVar4;
}



uchar FUN_00068a4a(void)

{
  return f33_nvm_family1_busy;
}



/* Reject object>=16 or descriptor first_handleFFFF withFF before changing probe mode. Set0693=5A
   and reconcile; translate logical base/+4/+8 through747E0 and classify64 bytes at page<<6.
   Continue only on class2; all three2->5A, first3->0, mapping failure/other classes->FF. Clear0693
   and reconcile on every admitted exit. That exit invokes real physical cancellation, can issue B3,
   and sets logical phase8 if operation state2. No application payload publication; 0 is not
   checksum/ECC integrity proof. Native first/last nonblank and all-blank cases use explicit FACI
   completion and a separate cancellation completion. Low16 object<16 and enabled first handle;
   probe64-byte pages for logical base/+4/+8. Continue on class2; three2->5A; first3->0; mapping
   error or other class->FF. Admitted entry sets0693=5A/reconciles; exit clears/reconciles and
   really cancels physical operation. Native4429 all-blank and2931/4933 first/last nonblank include
   explicit separate B3 completion; active logical phase changes to8. No application payload
   publication or checksum-validity claim. */

uint f33_nvm_classify_family1_pages(ushort object)

{
  ushort logical_handle;
  uint32_t puVar1;
  uint uVar2;
  uint uVar3;
  ushort uStack_e;
  
  puVar1 = 0xfebeb800u;
  uVar3 = 0xff;
  if ((uint)f33_nvm_family1_object_count <= (uint)object) {
    return 0xff;
  }
  logical_handle = f33_nvm_family1_ram_descriptors[object].first_logical_handle;
  if (logical_handle == 0xffff) {
    return 0xff;
  }
  f33_nvm_direct_operation_request = 'Z';
  f33_nvm_poll_probe_mode();
  uVar2 = f33_nvm_get_logical_storage_page(logical_handle,&uStack_e);
  if (uVar2 != 0) goto LAB_00068b1e;
  uVar2 = f33_nvm_classify_storage_range(0,(uint)uStack_e << 6,0x40);
  if (uVar2 == 2) {
    uVar2 = f33_nvm_get_logical_storage_page(logical_handle + 4,&uStack_e);
    if (uVar2 != 0) goto LAB_00068b1e;
    uVar2 = f33_nvm_classify_storage_range(0,(uint)uStack_e << 6,0x40);
    if (uVar2 == 2) {
      uVar2 = f33_nvm_get_logical_storage_page(logical_handle + 8,&uStack_e);
      if (uVar2 != 0) goto LAB_00068b1e;
      uVar2 = f33_nvm_classify_storage_range(0,(uint)uStack_e << 6,0x40);
      if (uVar2 == 2) {
        uVar3 = 0x5a;
        goto LAB_00068b1e;
      }
    }
  }
  if (uVar2 == 3) {
    uVar3 = 0;
  }
LAB_00068b1e:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x4e92u + (uint32_t)((int)(puVar1 + 1)))))) = (code)0x0;
  f33_nvm_poll_probe_mode();
  return uVar3;
}



/* Resolve unchecked route object/descriptor. Nonzero result retries below2 via real73FE8,
   increments shared0694 regardless enqueue result, returns0 before finalization; exhaustion clears
   retry and skips copy. Success clears retry, reads sequence at fixed0C88, inverse trailer at
   record+3C for payload<=56, else record+low16(payload+4); accept inverse match and no selection or
   unsigned sequence delta<=C0000000. Copy exactly payload bytes from record+4 immediately, then
   update sequence/selection. At handle>=low16(first+count-1), completion is5A iff any selection
   exists elseA5, and return5A for either outcome; otherwise0. Native early/long publication, bad
   inverse, delta boundary and retry rejection/exhaustion through68E9E. Shared0694 retry below2
   increments despite real enqueue rejection and returns before finalization; success/exhaustion
   clears retry. Fixed0C88 sequence header; payload/trailer use r8, trailer offset3C for length<=56
   else low16(length+4). Inverse match plus no selection or unsigned delta<=C0000000 admits
   immediate byte-exact copy and selection update. Final member publishes completion5A iff any
   selection exists elseA5; both return5A and release busy through router. Native short/long, bad
   inverse, delta boundary and retries; no physical flash restoration claim. */

uint f33_nvm_handle_family0_read_result(uchar result,ushort logical_handle,uchar *record)

{
  ushort uVar1;
  ushort uVar2;
  uint uVar3;
  uchar uVar4;
  int iVar5;
  uint32_t puVar6;
  uchar *puVar7;
  int iVar8;
  uint uVar9;
  uint uVar10;
  code cVar11;
  uint uVar12;
  
  uVar4 = f33_nvm_copy_read_retry;
  puVar6 = 0xfebeb800u;
  iVar8 = 0x5a;
  uVar10 = (uint)f33_nvm_logical_application_routes[logical_handle].object;
  uVar1 = f33_nvm_family0_ram_descriptors[uVar10].logical_count;
  uVar2 = f33_nvm_family0_ram_descriptors[uVar10].first_logical_handle;
  uVar9 = (uint)f33_nvm_family0_ram_descriptors[uVar10].payload_bytes;
  iVar5 = 0;
  if (result == '\0') {
    cVar11 = (code)0x0;
    iVar8 = 0;
  }
  else if (f33_nvm_copy_read_retry < 2) {
    puVar6 = 0xfebeb800u;
    f33_nvm_enqueue_read(logical_handle, camry_host_addr(record));
    cVar11 = (code)(uVar4 + '\x01');
    iVar5 = iVar8;
  }
  else {
    cVar11 = (code)0x0;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x4e92u + (uint32_t)((int)(puVar6 + 2)))))) = cVar11;
  if (iVar5 != 0x5a) {
    if (iVar8 != 0x5a) {
      uVar3 = (*((uint *)camry_host_ptr((uint32_t)(puVar6 + 0x5488))));
      uVar12 = 0x3c;
      if (0x38 < uVar9) {
        uVar12 = uVar9 + 4 & 0xffff;
      }
      if ((*(uint *)(record + uVar12) ^ uVar3) == 0xffffffff) {
        if (((*((short *)camry_host_ptr((uint32_t)(puVar6 + uVar10 * 2 + 0x4b68)))) == -1) ||
           (uVar3 - (*((int *)camry_host_ptr((uint32_t)(puVar6 + uVar10 * 4 + 0x4ba8)))) < 0xc0000001)) {
          puVar7 = ((void *)camry_host_ptr((uint32_t)(f33_nvm_family0_ram_descriptors[uVar10].buffer)));
          for (iVar5 = 0; (int)(iVar5 - uVar9) < 0 != (iVar5 < 0 && -1 < (int)(iVar5 - uVar9));
              iVar5 = iVar5 + 1) {
            puVar7[iVar5] = record[iVar5 + 4];
          }
          (*((uint *)camry_host_ptr((uint32_t)(puVar6 + uVar10 * 4 + 0x4ba8)))) = uVar3;
          (*((ushort *)camry_host_ptr((uint32_t)(puVar6 + uVar10 * 2 + 0x4b68)))) = logical_handle;
        }
      }
    }
    if ((uint)(ushort)((uVar1 + uVar2) - 1) <= (uint)logical_handle) {
      cVar11 = (code)0xa5;
      if ((*((short *)camry_host_ptr((uint32_t)(puVar6 + uVar10 * 2 + 0x4b68)))) != -1) {
        cVar11 = (code)0x5a;
      }
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x4b38u + (uint32_t)((int)(puVar6 + uVar10)))))) = cVar11;
      return 0x5a;
    }
  }
  return 0;
}



/* Unchecked route object/descriptor. Expected member is low16(selection+1), wrapping to first on
   oldFFFF or past descriptor end. Only result0 and exact expected handle update selection and
   completion5A; otherwise completionA5. Always return5A, causing router busy release even on
   failure. No third argument, sequence/payload update or local retry. Expected member is
   low16(selection+1), or first on oldFFFF/past-end. Only result0 and exact expected member update
   selection and completion5A; other cases publishA5. Always return5A, so real68E9E clears busy even
   on failure. No third argument or sequence/payload/retry update. */

uint f33_nvm_handle_family0_write_result(uchar result,ushort logical_handle)

{
  byte bVar1;
  uint uVar2;
  uchar uVar3;
  
  bVar1 = f33_nvm_logical_application_routes[logical_handle].object;
  uVar2 = (uint)f33_nvm_family0_selected_logical_handles[bVar1];
  if ((uVar2 == 0xffff) ||
     (uVar2 = uVar2 + 1 & 0xffff,
     (((uint)f33_nvm_family0_ram_descriptors[bVar1].logical_count +
      (uint)f33_nvm_family0_ram_descriptors[bVar1].first_logical_handle) - 1 & 0xffff) < uVar2)) {
    uVar2 = (uint)f33_nvm_family0_ram_descriptors[bVar1].first_logical_handle;
  }
  if ((result == '\0') && (uVar2 == logical_handle)) {
    f33_nvm_family0_selected_logical_handles[bVar1] = (ushort)uVar2;
    uVar3 = 'Z';
  }
  else {
    uVar3 = 0xa5;
  }
  f33_nvm_family0_completion[bVar1] = uVar3;
  return 0x5a;
}



/* Unchecked route object and family1 descriptor; slot=object&3. Copy0 resets the entire mask
   without reading it. Nonzero result ORs5A into that copy byte; success does not clear prior
   failures. Copy2 publishes5A iff the FULL32 mask is zero, otherwiseA5, and returns5A in both
   cases. Earlier copies return0. Unmatched handle sets005A5A5A and returns0. No read retry, data
   copy or physical-programming proof. Copy0 resets entire slot mask without a prior read; nonzero
   result ORs5A into its byte, success preserves prior failures. Copy2 requires full32 mask==0 for
   completion5A elseA5, returns5A either way so real router releases busy. No read retry or payload
   read/write. Native first/middle/final, non-5A error bit, slot3 and high-argument-bit cases. No
   physical-programming claim. */

uint f33_nvm_handle_family1_write_result(uchar result,ushort logical_handle)

{
  uint uVar1;
  uint uVar2;
  uchar uVar3;
  uint uVar4;
  int iVar5;
  uint uVar6;
  
  uVar2 = (uint)logical_handle;
  uVar6 = (uint)f33_nvm_logical_application_routes[uVar2].object;
  uVar4 = (uint)f33_nvm_family1_ram_descriptors[uVar6].first_logical_handle;
  if (uVar2 == uVar4) {
    iVar5 = 0;
    uVar1 = 0;
LAB_00068e6e:
    if (result != '\0') {
      uVar1 = uVar1 | 0x5a << (iVar5 << 3);
    }
    if (iVar5 == 2) {
      uVar3 = 0xa5;
      if (uVar1 == 0) {
        uVar3 = 'Z';
      }
      uVar2 = 0x5a;
      f33_nvm_family1_completion[uVar6] = uVar3;
      goto LAB_00068e9a;
    }
  }
  else {
    uVar1 = f33_nvm_family1_copy_failure_masks[uVar6 & 3];
    if (uVar2 == uVar4 + 4) {
      iVar5 = 1;
      goto LAB_00068e6e;
    }
    if (uVar2 == uVar4 + 8) {
      iVar5 = 2;
      goto LAB_00068e6e;
    }
    uVar1 = 0x5a5a5a;
  }
  uVar2 = 0;
LAB_00068e9a:
  f33_nvm_family1_copy_failure_masks[uVar6 & 3] = uVar1;
  return uVar2;
}



uchar FUN_00068f64(void)

{
  return f33_nvm_direct_operation_request;
}



/* Constant source: return 0; shape-classified from the canonical corpus. Callers receive this
   literal directly; its meaning is not recovered. */

undefined4 f33_return_const_0_68f6a(void)

{
  return 0;
}



/* Constant source: return 0; shape-classified from the canonical corpus. Callers receive this
   literal directly; its meaning is not recovered. */

undefined4 f33_return_const_0_68f6e(void)

{
  return 0;
}



/* Clear eight repeat/generation/seen bytes, previous/qualified64-byte banks and qualified mask.
   Does not by itself release an application operation. */

void f33_crypto_bank_clear_fragment_history(void)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  
  uVar2 = 0;
  do {
    uVar3 = 0;
    do {
      iVar1 = uVar3 + uVar2 * 8;
      uVar3 = uVar3 + 1;
      f33_crypto_key_fragment_previous[iVar1] = '\0';
      f33_crypto_key_fragment_qualified[iVar1] = '\0';
    } while (uVar3 < 8);
    f33_crypto_key_fragment_repeat_count[uVar2] = '\0';
    uVar3 = uVar2 + 1;
    f33_crypto_key_fragment_previous_generation[uVar2] = '\0';
    f33_crypto_key_fragment_seen[uVar2] = '\0';
    uVar2 = uVar3;
  } while (uVar3 < 8);
  f33_crypto_key_fragment_qualified_mask = '\0';
  return;
}



/* WARNING: This is an inlined function */
/* For low8 slot<2 clear exactly64 request and48 result bytes. Leaf preserves incomingR7/R8/R9;
   inline real p-code so direct request output pointer survives. No key erasure in hardware is
   implied. */

void f33_crypto_bank_clear_key_material(uchar slot)

{
  uint uVar1;
  uint uVar2;
  
  if (slot < 2) {
    uVar2 = 0;
    do {
      uVar1 = uVar2 + 1;
      f33_crypto_key_request[slot][uVar2] = '\0';
      uVar2 = uVar1;
    } while (uVar1 < 0x40);
    uVar2 = 0;
    do {
      uVar1 = uVar2 + 1;
      f33_crypto_key_result[(short)(ushort)slot][uVar2] = '\0';
      uVar2 = uVar1;
    } while (uVar1 < 0x30);
  }
  return;
}



/* Clear five qualification histories, scalar pair, four8-byte previous/qualified groups and
   fixed16-byte input/expected/AES/MAC buffers. No hardware cancellation. */

void f33_crypto_bank_clear_test_material(void)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  
  uVar2 = 0;
  do {
    uVar3 = 0;
    do {
      iVar1 = uVar3 + uVar2 * 8;
      uVar3 = uVar3 + 1;
      f33_crypto_test_fragment_previous[iVar1] = '\0';
      f33_crypto_test_fragment_qualified[iVar1] = '\0';
    } while (uVar3 < 8);
    uVar2 = uVar2 + 1;
  } while (uVar2 < 4);
  uVar2 = 0;
  do {
    f33_crypto_test_repeat_count[uVar2] = '\0';
    uVar3 = uVar2 + 1;
    f33_crypto_test_previous_generation[uVar2] = '\0';
    f33_crypto_test_seen[uVar2] = '\0';
    uVar2 = uVar3;
  } while (uVar3 < 5);
  uVar2 = 0;
  do {
    f33_crypto_test_input[uVar2] = '\0';
    uVar2 = uVar2 + 1;
  } while (uVar2 < 0x10);
  uVar2 = 0;
  do {
    f33_crypto_test_expected[uVar2] = '\0';
    uVar3 = uVar2 + 1;
    f33_crypto_aes_result[uVar2] = '\0';
    f33_crypto_mac_result[uVar2] = '\0';
    uVar2 = uVar3;
  } while (uVar3 < 0x10);
  f33_crypto_test_selector = '\0';
  DAT_febe509f = 0;
  f33_crypto_test_mode = '\0';
  DAT_febe50a0 = 0;
  DAT_febe509e = 0;
  DAT_febe50a1 = 0;
  f33_crypto_test_qualified_mask = '\0';
  return;
}



/* WARNING: Inlined function: f33_crypto_bank_clear_key_material */
/* Clear direct/collected/test activation, timers, qualification histories and outputs. Initialize
   result lengths48/16/16, verification result1, two profile states11 and observation counters. Mode
   bytes5099/509A are separately owned. */

void f33_crypto_bank_initialize_work(void)

{
  uint uVar1;
  int iVar2;
  uint uVar3;
  uint32_t puVar4;
  puVar4 = 0xfebeb800u;
  f33_crypto_direct_activation = '\0';
  f33_crypto_direct_phase = '\0';
  f33_crypto_direct_elapsed_calls = 0;
  f33_crypto_direct_failure_count = '\0';
  f33_crypto_direct_inhibited = '\0';
  f33_crypto_direct_abort_request = '\0';
  f33_crypto_collected_activation = '\0';
  f33_crypto_collected_phase = '\0';
  f33_crypto_collected_elapsed_calls = 0;
  f33_crypto_bank_clear_fragment_history();
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
  f33_crypto_bank_clear_key_material('\x01');
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6765))))) = 0;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar4 + -0x679c)))) = 0x30;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6763))))) = 1;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6764))))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar4 + -0x677a)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x675d))))) = 0;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar4 + -0x6798)))) = 0x10;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar4 + -0x6794)))) = 0x10;
  f33_crypto_bank_clear_test_material();
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



/* Initialize current and previous mode bytes5099/509A to5A; startup also invokes69064. */

void f33_crypto_bank_initialize_mode(void)

{
  f33_crypto_mode = 'Z';
  f33_crypto_previous_mode = 'Z';
  return;
}



/* WARNING: This is an inlined function */
/* Return min(unsigned ROM2597C,2); exact value1. Five-instruction leaf preservesR6, including
   packed callback high16 consumed by6A1B2. Inline real p-code. */

uint f33_crypto_bank_profile_count(void)

{
  uint uVar1;
  
  uVar1 = (uint)f33_crypto_config_profile_count;
  if (2 < uVar1) {
    uVar1 = 2;
  }
  return uVar1;
}



/* WARNING: Inlined function: f33_crypto_bank_profile_count */
/* For bounded configured profile count invoke8F0A8 then8F0D4, discarding statuses. Root invokes
   this on the first non-A5 cycle after modeA5; lower freshness/profile reset semantics remain
   separate. */

void f33_crypto_bank_reset_configured_profiles(void)

{
  uint uVar1;
  uint uVar2;
  
  uVar1 = (uint)f33_crypto_config_profile_count;
  if (2 < uVar1) {
    uVar1 = 2;
  }
  for (uVar2 = 0; uVar2 < uVar1; uVar2 = uVar2 + 1) {
    FUN_0008f0a8(uVar2);
    FUN_0008f0d4(uVar2);
  }
  return;
}



/* Initialize verification result1. Only ROM30D67==5A enters fixed-vector command7 sequence, with
   explicit interrupt/priority handling. Exact gate0 skips hardware work and reports result==0
   through8EE16(FF). Not an established key-validity proof. */

uint f33_crypto_bank_run_startup_verification(void)

{
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
  char cStack_21;
  undefined4 uStack_20;
  undefined1 uStack_1c;
  
  puVar3 = 0x23dfcu;
  cStack_21 = '\x01';
  uVar6 = camry_psw & 0xfffffff0 | (uint)(f33_crypto_config_fixed_verification_enable == 'Z');
  if ((bool)((byte)uVar6 & 1)) {
    iVar4 = FUN_00089c5a(0, camry_host_addr(((undefined *)camry_host_ptr(0x21604u))));
    uVar6 = uVar6 & 0xfffffff0 | (uint)(iVar4 == 0);
    if ((bool)((byte)uVar6 & 1)) {
      iVar4 = FUN_00089c8c(iVar4, camry_host_addr(((undefined *)camry_host_ptr((uint32_t)(puVar3 + -0x2818)))),  0x10);
      uVar6 = uVar6 & 0xfffffff0 | (uint)(iVar4 == 0);
      if ((bool)((byte)uVar6 & 1)) {
        uVar5 = FUN_000701a0();
        f33_priority_mask_restore(0);
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
            (*(int (*)())camry_host_ptr((uint32_t)((in_EBASE & 0xfffffe00) + 0x70)))();
          }
        }
        __enable_irq();
        iVar4 = FUN_00089c98(0, camry_host_addr(((undefined *)camry_host_ptr((uint32_t)(puVar3 + -0x2808)))),  0x10, camry_host_addr(&cStack_21));
        __disable_irq();
        FUN_000701a6(uVar5);
        if (iVar4 == 0) goto LAB_000691fe;
      }
    }
    cStack_21 = '\x01';
  }
LAB_000691fe:
  uStack_20 = 1;
  uStack_1c = cStack_21 == '\0';
  return FUN_0008ee16(0xff, camry_host_addr(&uStack_20));
}



/* Run startup verification publication then clear accumulated observation count505C. Exact gate0
   does not issue a crypto command. */

void f33_crypto_bank_initialize_verification_report(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  f33_crypto_bank_run_startup_verification();
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x67a4)))) = 0;
  return;
}



/* WARNING: Inlined function: f33_crypto_bank_profile_count */
/* For state11: three zero-status observations select44 immediately. Otherwise increment16-bit count
   while below620; a later call at620 selects88/status5A only for zero good and nonzero bad, else22.
   No physical-time conversion. */

void f33_crypto_bank_advance_profile_qualification(void)

{
  ushort uVar1;
  uint uVar2;
  uint uVar3;
  uchar uVar4;
  
  uVar3 = (uint)f33_crypto_config_profile_count;
  if (2 < uVar3) {
    uVar3 = 2;
  }
  for (uVar2 = 0; uVar2 < uVar3; uVar2 = uVar2 + 1 & 0xff) {
    uVar4 = f33_crypto_profile_phase[uVar2];
    if (uVar4 == '\x11') {
      if (f33_crypto_profile_zero_status_count[uVar2] < 3) {
        uVar1 = f33_crypto_profile_elapsed_calls[uVar2];
        if (uVar1 < f33_crypto_config_profile_wait_calls) {
          f33_crypto_profile_elapsed_calls[uVar2] = uVar1 + 1;
        }
        else if ((f33_crypto_profile_zero_status_count[uVar2] == 0) &&
                (f33_crypto_profile_nonzero_status_count[uVar2] != '\0')) {
          uVar4 = 0x88;
          f33_crypto_profile_failed[uVar2] = 'Z';
        }
        else {
          uVar4 = '\"';
        }
      }
      else {
        uVar4 = 'D';
      }
    }
    f33_crypto_profile_phase[uVar2] = uVar4;
  }
  return;
}



/* Pass record{word1,byte(result509D==0)} to initialized SecOC API8EE16 with IDFF. Boolean
   publication is separate from ICU-S command completion. */

uint f33_crypto_bank_publish_verification_result(void)

{
  undefined4 local_18;
  undefined1 uStack_14;
  
  local_18 = 1;
  uStack_14 = f33_crypto_verification_result == '\0';
  return FUN_0008ee16(0xff, camry_host_addr(&local_18));
}



/* For slot<2 wait in22 unless79B70 returns0F and direct NvM result is not1. Reset output
   capacity48; submit configured command8 job0 with64 input bytes. Accepted0 yields33, other
   results66. Physical readiness/crypto completion remain dependencies. */

uint f33_crypto_bank_submit_key_material(uchar slot)

{
  uint32_t puVar1;
  int iVar2;
  uint uVar3;
  
  puVar1 = 0xfebeb800u;
  if (slot < 2) {
    iVar2 = FUN_00079b70();
    uVar3 = f33_nvm_get_direct_operation_result();
    if ((iVar2 != 0xf) || (uVar3 == 1)) {
      return 0x22;
    }
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x679c)))) = 0x30;
    iVar2 = FUN_00089a26(0, camry_host_addr(((undefined *)camry_host_ptr((uint32_t)(puVar1 + (uint)slot * 0x40 + -0x663a)))),  0x40,  0, camry_host_addr(((undefined *)camry_host_ptr((uint32_t)(puVar1 + (short)(ushort)slot * 0x30 + -0x65ba)))), camry_host_addr(((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x679c)))));
    if (iVar2 == 0) {
      return 0x33;
    }
  }
  return 0x66;
}



/* Reset result509D to1. Exact ROM30D67=0 returns46 without issuing fixed-vector command7.
   Configured5A branch returns45 on accepted job1, else46 with result1. */

uint f33_crypto_bank_begin_post_update_verification(void)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  f33_crypto_verification_result = '\x01';
  if (f33_crypto_config_fixed_verification_enable == 'Z') {
    iVar2 = FUN_00089646(1, camry_host_addr(((undefined *)camry_host_ptr(0x21604u))), camry_host_addr(((undefined *)camry_host_ptr(0x215e4u))), 0x10, camry_host_addr(((undefined *)camry_host_ptr(0x215f4u))), 0x10, 
                         (0xfebe509du));
    if (iVar2 == 0) {
      return 0x45;
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6763))))) = 1;
  }
  return 0x46;
}



/* Increment saturating16-bit timer. Above120 choose66; timeout while45 also publishes result1.
   States11/22 submit;44 starts optional verification;46 publishes result and becomes55. Store phase
   and timer after sequential transitions. */

void f33_crypto_bank_advance_direct_update(void)

{
  undefined *puVar1;
  uint uVar2;
  ushort uVar3;
  
  puVar1 = ((undefined *)camry_host_ptr(0xfebeb800u));
  uVar2 = (uint)f33_crypto_direct_phase;
  uVar3 = f33_crypto_direct_elapsed_calls;
  if (f33_crypto_direct_elapsed_calls != 0xffff) {
    uVar3 = f33_crypto_direct_elapsed_calls + 1;
  }
  if (f33_crypto_config_direct_timeout_calls < uVar3) {
    if (uVar2 == 0x45) {
      f33_crypto_verification_result = '\x01';
      puVar1 = ((undefined *)camry_host_ptr(0xfebeb800u));
      f33_crypto_bank_publish_verification_result();
    }
    uVar2 = 0x66;
  }
  else {
    if ((uVar2 == 0x11) || (puVar1 = ((undefined *)camry_host_ptr(0xfebeb800u)), uVar2 == 0x22)) {
      puVar1 = ((undefined *)camry_host_ptr(0xfebeb800u));
      uVar2 = f33_crypto_bank_submit_key_material('\0');
    }
    if (uVar2 == 0x44) {
      uVar2 = f33_crypto_bank_begin_post_update_verification();
    }
    if (uVar2 == 0x46) {
      f33_crypto_bank_publish_verification_result();
      uVar2 = 0x55;
    }
  }
  puVar1[-0x676e] = (char)uVar2;
  *(ushort *)(puVar1 + -0x677e) = uVar3;
  return;
}



/* Observe eight configured generation bytes and copy8 bytes per changed group. First/matching
   sample increments wrapping repeat count; mismatch restarts at1. Count>=3 sets sticky qualified
   bit and copies group. Later mismatch does not clear that bit. MaskFF copies64 qualified bytes to
   slot1 and returns22; otherwise11. Group getter status is ignored. */

uint f33_crypto_bank_collect_key_fragments(void)

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
  uVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5338u + (uint32_t)(f33_crypto_key_fragment_generation_indices[0]) * 1u))));
  if (uVar2 != f33_crypto_key_fragment_previous_generation[0]) {
    puVar4 = 0xfebeb800u;
    FUN_0007e72a(f33_crypto_key_fragment_signal_indices[0], f33_crypto_key_fragment_byte_offsets[0], 8
                 , camry_host_addr(acStack_54));
    acStack_54[0x40] = 0x5a;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x67bc))))) = uVar2;
  cVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(f33_crypto_key_fragment_generation_indices[1] - 0x64c8)))));
  if (cVar3 != (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x67bb)))))) {
    FUN_0007e72a(f33_crypto_key_fragment_signal_indices[1], f33_crypto_key_fragment_byte_offsets[1], 8
                 , camry_host_addr(acStack_54 + 8));
    acStack_54[0x41] = 0x5a;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x67bb))))) = cVar3;
  cVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(f33_crypto_key_fragment_generation_indices[2] - 0x64c8)))));
  if (cVar3 != (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x67ba)))))) {
    FUN_0007e72a(f33_crypto_key_fragment_signal_indices[2], f33_crypto_key_fragment_byte_offsets[2], 8
                 , camry_host_addr(acStack_54 + 0x10));
    acStack_54[0x42] = 0x5a;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x67ba))))) = cVar3;
  cVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(f33_crypto_key_fragment_generation_indices[3] - 0x64c8)))));
  if (cVar3 != (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x67b9)))))) {
    FUN_0007e72a(f33_crypto_key_fragment_signal_indices[3], f33_crypto_key_fragment_byte_offsets[3], 8
                 , camry_host_addr(acStack_54 + 0x18));
    acStack_54[0x43] = 0x5a;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x67b9))))) = cVar3;
  cVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(f33_crypto_key_fragment_generation_indices[4] - 0x64c8)))));
  if (cVar3 != (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x67b8)))))) {
    FUN_0007e72a(f33_crypto_key_fragment_signal_indices[4], f33_crypto_key_fragment_byte_offsets[4], 8
                 , camry_host_addr(acStack_54 + 0x20));
    acStack_54[0x44] = 0x5a;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x67b8))))) = cVar3;
  cVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(f33_crypto_key_fragment_generation_indices[5] - 0x64c8)))));
  if (cVar3 != (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x67b7)))))) {
    FUN_0007e72a(f33_crypto_key_fragment_signal_indices[5], f33_crypto_key_fragment_byte_offsets[5], 8
                 , camry_host_addr(acStack_54 + 0x28));
    acStack_54[0x45] = 0x5a;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x67b7))))) = cVar3;
  cVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(f33_crypto_key_fragment_generation_indices[6] - 0x64c8)))));
  if (cVar3 != (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x67b6)))))) {
    FUN_0007e72a(f33_crypto_key_fragment_signal_indices[6], f33_crypto_key_fragment_byte_offsets[6], 8
                 , camry_host_addr(acStack_54 + 0x30));
    acStack_54[0x46] = 0x5a;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x67b6))))) = cVar3;
  cVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(f33_crypto_key_fragment_generation_indices[7] - 0x64c8)))));
  if (cVar3 != (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x67b5)))))) {
    FUN_0007e72a(f33_crypto_key_fragment_signal_indices[7], f33_crypto_key_fragment_byte_offsets[7], 8
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
        if (f33_crypto_config_fragment_repeat_threshold <= bVar5) {
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



/* Increment saturating timer; strict >1200 gives66. State11 collects;22 submits;44 starts optional
   verification;46 publishes then55, with sequential transitions possible in one invocation.
   Physical submission readiness remains distinct. */

void f33_crypto_bank_advance_collected_update(void)

{
  uint32_t puVar1;
  uint uVar2;
  ushort uVar3;
  
  puVar1 = 0xfebeb800u;
  uVar2 = (uint)f33_crypto_collected_phase;
  uVar3 = f33_crypto_collected_elapsed_calls;
  if (f33_crypto_collected_elapsed_calls != 0xffff) {
    uVar3 = f33_crypto_collected_elapsed_calls + 1;
  }
  if (f33_crypto_config_collected_timeout_calls < uVar3) {
    if (uVar2 == 0x45) {
      f33_crypto_verification_result = '\x01';
      puVar1 = 0xfebeb800u;
      f33_crypto_bank_publish_verification_result();
    }
    uVar2 = 0x66;
  }
  else {
    puVar1 = 0xfebeb800u;
    if (uVar2 == 0x11) {
      puVar1 = 0xfebeb800u;
      uVar2 = f33_crypto_bank_collect_key_fragments();
    }
    if (uVar2 == 0x22) {
      uVar2 = f33_crypto_bank_submit_key_material('\x01');
    }
    if (uVar2 == 0x44) {
      uVar2 = f33_crypto_bank_begin_post_update_verification();
    }
    if (uVar2 == 0x46) {
      f33_crypto_bank_publish_verification_result();
      uVar2 = 0x55;
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6769))))) = (char)uVar2;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x677c)))) = uVar3;
  return;
}



/* Mode0 submits configured AES job0 with selector50A4 and16-byte input/output; mode1 submits MAC
   job1 with the same fixed input extent. Reset capacity16. Accepted0 gives23, invalid
   mode/refusal44. No algorithm outcome is fabricated. */

uint f33_crypto_bank_submit_test_vector(void)

{
  int iVar1;
  uint uStack_18;
  uchar uStack_14;
  
  uStack_18 = (uint)f33_crypto_test_mode;
  if (uStack_18 == 0) {
    uStack_18 = 1;
    f33_crypto_aes_result_capacity = 0x10;
    uStack_14 = f33_crypto_test_selector;
    iVar1 = FUN_00089838(0, camry_host_addr(&uStack_18), camry_host_addr(f33_crypto_test_input), 0x10, camry_host_addr(f33_crypto_aes_result), 
                         (0xfebe5068u));
  }
  else {
    if (uStack_18 != 1) {
      return 0x44;
    }
    f33_crypto_mac_result_capacity = 0x10;
    uStack_14 = f33_crypto_test_selector;
    iVar1 = FUN_00089440(1, camry_host_addr(&uStack_18), camry_host_addr(f33_crypto_test_input), 0x10, camry_host_addr(f33_crypto_mac_result), 
                         (0xfebe506cu), 1);
  }
  if (iVar1 != 0) {
    return 0x44;
  }
  return 0x23;
}



/* Increment saturating timer; strict >1160 selects44. State11 collects then may submit22 in the
   same call; accepted job waits in23. Completion callback separately compares output and
   publishes33 or44. */

void f33_crypto_bank_advance_test_operation(void)

{
  uint32_t puVar1;
  uint uVar2;
  ushort uVar3;
  
  puVar1 = 0xfebeb800u;
  uVar2 = (uint)f33_crypto_test_phase;
  uVar3 = f33_crypto_test_elapsed_calls;
  if (f33_crypto_test_elapsed_calls != 0xffff) {
    uVar3 = f33_crypto_test_elapsed_calls + 1;
  }
  if (f33_crypto_config_test_timeout_calls < uVar3) {
    uVar2 = 0x44;
  }
  else {
    puVar1 = 0xfebeb800u;
    if (uVar2 == 0x11) {
      puVar1 = 0xfebeb800u;
      uVar2 = f33_crypto_bank_collect_test_vector();
    }
    if (uVar2 == 0x22) {
      uVar2 = f33_crypto_bank_submit_test_vector();
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6764))))) = (char)uVar2;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x677a)))) = uVar3;
  return;
}



/* WARNING: Inlined function: f33_crypto_bank_clear_key_material */
/* Before normal receive/DCM: modeA5 reinitializes work each cycle; priorA5 on departure resets
   configured profiles. Advance profile qualification, consume direct abort5A, then active
   direct/collected/test workers in order. Save old current mode as previous. Hardware completion is
   not performed by this aggregate. */

void f33_crypto_bank_foreground_cycle(void)

{
  uint uVar1;
  uchar uVar2;
  uint uVar3;
  uint32_t puVar4;
  uVar2 = f33_crypto_mode;
  puVar4 = 0xfebeb800u;
  if (f33_crypto_mode == 0xa5) {
    puVar4 = 0xfebeb800u;
    f33_crypto_bank_initialize_work();
  }
  else if (f33_crypto_previous_mode == 0xa5) {
    puVar4 = 0xfebeb800u;
    f33_crypto_bank_reset_configured_profiles();
  }
  f33_crypto_bank_advance_profile_qualification();
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
    f33_crypto_bank_advance_direct_update();
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x676a))))) == '\x01') {
    f33_crypto_bank_advance_collected_update();
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6765))))) == '\x01') {
    f33_crypto_bank_advance_test_operation();
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6766))))) = uVar2;
  return;
}



/* Phase55 sets activation2;66 setsFF and saturating failure count, latching inhibition5A at
   configured5 failures. Preserve material until result read or later reset. */

void f33_crypto_bank_retire_direct_update(void)

{
  if (f33_crypto_direct_phase == 'U') {
    f33_crypto_direct_activation = '\x02';
  }
  if (((f33_crypto_direct_phase == 'f') &&
      (f33_crypto_direct_activation = 0xff, f33_crypto_direct_failure_count != 0xff)) &&
     (f33_crypto_direct_failure_count = f33_crypto_direct_failure_count + 1,
     f33_crypto_config_direct_failure_limit <= f33_crypto_direct_failure_count)) {
    f33_crypto_direct_inhibited = 'Z';
  }
  return;
}



/* WARNING: Inlined function: f33_crypto_bank_clear_key_material */
/* Phase55/66 sets activation2/FF and clears fragment history plus slot1 request/result material.
   Restore terminal phase after clearing; completion does not retain slot1 response bytes. */

void f33_crypto_bank_retire_collected_update(void)

{
  uint uVar1;
  uchar uVar2;
  uint uVar3;
  uint32_t puVar4;
  uchar uVar5;
  
  uVar2 = f33_crypto_collected_phase;
  puVar4 = 0xfebeb800u;
  uVar5 = f33_crypto_collected_activation;
  if (f33_crypto_collected_phase == 'U') {
    uVar5 = '\x02';
    puVar4 = 0xfebeb800u;
    f33_crypto_bank_clear_fragment_history();
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
    f33_crypto_bank_clear_fragment_history();
                    /* WARNING: Could not inline here */
    f33_crypto_bank_clear_key_material('\x01');
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x676a))))) = uVar5;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6769))))) = uVar2;
  return;
}



/* Phase33 sets activation2 and failure flag0;44 sets activationFF and failure flag5A. Other phases
   remain active. */

void f33_crypto_bank_retire_test_operation(void)

{
  if (f33_crypto_test_phase == '3') {
    f33_crypto_test_failed = '\0';
    f33_crypto_test_activation = '\x02';
  }
  if (f33_crypto_test_phase == 'D') {
    f33_crypto_test_activation = 0xff;
    f33_crypto_test_failed = 'Z';
  }
  return;
}



/* Reduce callback observation counts using exact30D62/30D64 thresholds, saturating total505C,
   wrapping byte interval/index and sixteen-bit counters. Preserve raw count semantics; no inferred
   milliseconds or steering authority. */

void f33_crypto_bank_publish_observation_window(void)

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



/* After DCM in667E6: retire each active application bank then publish observation window. Separate
   from69CA2 advance before receive; neither is a CAN-controller lifecycle manager. */

void f33_crypto_bank_maintain_terminal_states(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (f33_crypto_direct_activation == '\x01') {
    puVar1 = 0xfebeb800u;
    f33_crypto_bank_retire_direct_update();
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x676a))))) == '\x01') {
    f33_crypto_bank_retire_collected_update();
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6765))))) == '\x01') {
    f33_crypto_bank_retire_test_operation();
  }
  f33_crypto_bank_publish_observation_window();
  return;
}



/* WARNING: Inlined function: f33_crypto_bank_clear_key_material */
/* Clamp request64/output49. Return5 when inhibited,8 when already active, otherwise initialize
   active direct update22 and clear material. Input copy still occurs on refusal/busy; output status
   plus zeros is written when length nonzero. ActualR8 survives68FAA; no NULL checks. */

uint f33_crypto_bank_stage_direct_request
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
  if (f33_crypto_direct_inhibited == '\0') {
    if (f33_crypto_direct_activation == '\x01') {
      uVar2 = 8;
    }
    else {
      f33_crypto_direct_activation = '\x01';
      f33_crypto_direct_elapsed_calls = 0;
      f33_crypto_direct_phase = '\"';
      uVar2 = 0;
      do {
        uVar1 = uVar2 + 1;
        f33_crypto_key_request[0][uVar2] = '\0';
        uVar2 = uVar1;
      } while (uVar1 < 0x40);
      uVar2 = 0;
      do {
        uVar1 = uVar2 + 1;
        f33_crypto_key_result[0][uVar2] = '\0';
        uVar2 = uVar1;
      } while (uVar1 < 0x30);
      uVar2 = 0;
    }
  }
  else {
    uVar2 = 5;
  }
  for (uVar1 = 0; uVar1 < uVar3; uVar1 = uVar1 + 1 & 0xffff) {
    f33_crypto_key_request[0][uVar1] = input[uVar1];
  }
  if (uVar4 != 0) {
    *output = f33_crypto_direct_activation;
    for (uVar3 = 1; uVar3 < uVar4; uVar3 = uVar3 + 1 & 0xffff) {
      output[uVar3] = '\0';
    }
  }
  return uVar2;
}



/* WARNING: Inlined function: f33_crypto_bank_clear_key_material */
/* Clamp output49; emit activation then48 result bytes only for activation2, otherwise zeros. If
   activation2 orFF clear direct request/result even for length0; retain activation. Repeated
   completed reads therefore return status2 with consumed zero material. Return0. */

uint f33_crypto_bank_read_direct_result(uchar *output,ushort length)

{
  uchar uVar1;
  uint uVar2;
  uint uVar3;
  
  uVar1 = f33_crypto_direct_activation;
  uVar3 = (uint)length;
  if (uVar3 < 0x32) {
    if (uVar3 == 0) goto LAB_00069f8c;
  }
  else {
    uVar3 = 0x31;
  }
  *output = f33_crypto_direct_activation;
  uVar2 = 1;
  if (uVar1 == '\x02') {
    for (; uVar2 < uVar3; uVar2 = uVar2 + 1 & 0xffff) {
      output[uVar2] = f33_crypto_key_request[1][uVar2 + 0x3f];
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
      f33_crypto_key_request[0][uVar3] = '\0';
      uVar3 = uVar2;
    } while (uVar2 < 0x40);
    uVar3 = 0;
    do {
      uVar2 = uVar3 + 1;
      f33_crypto_key_result[0][uVar3] = '\0';
      uVar3 = uVar2;
    } while (uVar2 < 0x30);
  }
  return 0;
}



/* Snapshot configured generation indices10..17 into prior-generation bytes. Activation does not
   treat already-present material as a new generation. */

void f33_crypto_bank_snapshot_key_generations(void)

{
  f33_crypto_key_fragment_previous_generation[0] =
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5338u + (uint32_t)(f33_crypto_key_fragment_generation_indices[0]) * 1u))));
  f33_crypto_key_fragment_previous_generation[1] =
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5338u + (uint32_t)(f33_crypto_key_fragment_generation_indices[1]) * 1u))));
  f33_crypto_key_fragment_previous_generation[2] =
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5338u + (uint32_t)(f33_crypto_key_fragment_generation_indices[2]) * 1u))));
  f33_crypto_key_fragment_previous_generation[3] =
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5338u + (uint32_t)(f33_crypto_key_fragment_generation_indices[3]) * 1u))));
  f33_crypto_key_fragment_previous_generation[4] =
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5338u + (uint32_t)(f33_crypto_key_fragment_generation_indices[4]) * 1u))));
  f33_crypto_key_fragment_previous_generation[5] =
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5338u + (uint32_t)(f33_crypto_key_fragment_generation_indices[5]) * 1u))));
  f33_crypto_key_fragment_previous_generation[6] =
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5338u + (uint32_t)(f33_crypto_key_fragment_generation_indices[6]) * 1u))));
  f33_crypto_key_fragment_previous_generation[7] =
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5338u + (uint32_t)(f33_crypto_key_fragment_generation_indices[7]) * 1u))));
  return;
}



/* WARNING: Inlined function: f33_crypto_bank_clear_key_material */
/* Only activation0 becomes1/state11/timer0; clear fragment/material state and snapshot current
   eight generations. Existing nonzero activation is not restarted. */

void f33_crypto_bank_activate_collected_update(void)

{
  uint uVar1;
  uint uVar2;
  uint32_t puVar3;
  puVar3 = 0xfebeb800u;
  if (f33_crypto_collected_activation == '\0') {
    f33_crypto_collected_activation = '\x01';
    f33_crypto_collected_elapsed_calls = 0;
    f33_crypto_collected_phase = '\x11';
    f33_crypto_bank_clear_fragment_history();
    uVar2 = 0;
    do {
      uVar1 = uVar2 + 1;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(uVar2 - 0x65fa))))) = 0;
      uVar2 = uVar1;
    } while (uVar1 < 0x40);
    uVar2 = 0;
    do {
      uVar1 = uVar2 + 1;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(uVar2 - 0x658a))))) = 0;
      uVar2 = uVar1;
    } while (uVar1 < 0x30);
    f33_crypto_bank_snapshot_key_generations();
  }
  return;
}



/* Snapshot five configured source generations before collection; scalar pair and four byte groups
   have independent histories. */

void f33_crypto_bank_snapshot_test_generations(void)

{
  f33_crypto_test_previous_generation[0] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5338u + (uint32_t)(DAT_000257d0) * 1u))));
  f33_crypto_test_previous_generation[1] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5338u + (uint32_t)(DAT_000257d2) * 1u))));
  f33_crypto_test_previous_generation[2] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5338u + (uint32_t)(DAT_000257d4) * 1u))));
  f33_crypto_test_previous_generation[3] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5338u + (uint32_t)(DAT_000257d6) * 1u))));
  f33_crypto_test_previous_generation[4] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5338u + (uint32_t)(DAT_000257d8) * 1u))));
  return;
}



/* RID100F action reaches this gate. Only activation0 becomes1/state11/timer0; clear test
   material/history and snapshot generations. CAN bytes alone do not arm it. */

void f33_crypto_bank_activate_test_operation(void)

{
  if (f33_crypto_test_activation == '\0') {
    f33_crypto_test_activation = '\x01';
    f33_crypto_test_elapsed_calls = 0;
    f33_crypto_test_phase = '\x11';
    f33_crypto_bank_clear_test_material();
    f33_crypto_bank_snapshot_test_generations();
  }
  return;
}



/* Compare16 fixed expected bytes5196 with AES result51A6; mismatch44, complete equality33. Not a
   hardware implementation of AES. */

uint f33_crypto_bank_compare_aes_result(void)

{
  uint uVar1;
  
  uVar1 = 0;
  do {
    if (f33_crypto_test_expected[uVar1] != f33_crypto_aes_result[uVar1]) {
      return 0x44;
    }
    uVar1 = uVar1 + 1;
  } while (uVar1 < 0x10);
  return 0x33;
}



/* Compare16 fixed expected bytes5196 with MAC result51B6; mismatch44, complete equality33. No
   arbitrary message or output length. */

uint f33_crypto_bank_compare_mac_result(void)

{
  uint uVar1;
  
  uVar1 = 0;
  do {
    if (f33_crypto_test_expected[uVar1] != f33_crypto_mac_result[uVar1]) {
      return 0x44;
    }
    uVar1 = uVar1 + 1;
  } while (uVar1 < 0x10);
  return 0x33;
}



undefined1 FUN_0006a12a(void)

{
  return DAT_febe508f;
}



undefined4 FUN_0006a130(void)

{
  return DAT_febe505c;
}



undefined2 FUN_0006a136(uint param_1)

{
  return *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe50b6u)) + (param_1 & 7) * 2);
}



undefined1 FUN_0006a144(void)

{
  return DAT_febe508b;
}



undefined1 FUN_0006a14a(void)

{
  return DAT_febe508c;
}



uchar FUN_0006a150(void)

{
  return f33_crypto_test_failed;
}



void FUN_0006a156(undefined4 param_1,char param_2)

{
  if (((param_2 == '\x01') || (param_2 == '@')) && (f33_crypto_direct_activation != '\0')) {
    f33_crypto_direct_abort_request = 'Z';
  }
  return;
}



void FUN_0006a174(uchar param_1)

{
  f33_crypto_mode = param_1;
  return;
}



/* Single constant publisher: DAT_febe505c = 0; Shape-classified from the canonical corpus; the
   target cell is not yet named, so the written state's meaning is unknown. */

void FUN_0006a17a(void)

{
  DAT_febe505c = 0;
  return;
}



uchar FUN_0006a180(uint param_1)

{
  if ((param_1 & 0xff) < 2) {
    return f33_crypto_profile_failed[param_1 & 0xff];
  }
  return '\0';
}



undefined4 FUN_0006a192(void)

{
  if ((f33_crypto_direct_activation != '\x01') && (f33_crypto_collected_activation != '\x01')) {
    return 0;
  }
  return 0x5a;
}



void FUN_0006a1ac(undefined2 param_1)

{
  DAT_febe5070 = param_1;
  return;
}



/* WARNING: Inlined function: f33_crypto_bank_profile_count */
/* Store low/high16 at5054/5056. For state11 and configured low ID0, saturating-increment
   zero-status507E or nonzero-status5080. High16 remains inR6 across exact6915A leaf; no extra
   callback argument. */

void f33_crypto_bank_record_profile_status(uint packed_status)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  uchar uVar4;
  uint uVar5;
  uchar *puVar6;
  
  uVar5 = packed_status & 0xffff;
  uVar2 = packed_status >> 0x10;
  uVar3 = (uint)f33_crypto_config_profile_count;
  if (2 < uVar3) {
    uVar3 = 2;
  }
  uVar1 = 0;
  while( true ) {
    DAT_febe5056 = (undefined2)(packed_status >> 0x10);
    DAT_febe5054 = (undefined2)packed_status;
    if (uVar3 <= uVar1) break;
    if ((f33_crypto_profile_phase[uVar1] == '\x11') && (uVar5 == DAT_00025840)) {
      if (uVar2 == 0) {
        puVar6 = f33_crypto_profile_zero_status_count + uVar1;
        uVar4 = *puVar6;
        if (uVar4 != 0xff) {
          uVar4 = uVar4 + '\x01';
        }
      }
      else {
        puVar6 = f33_crypto_profile_nonzero_status_count + uVar1;
        uVar4 = *puVar6;
        if (uVar4 != 0xff) {
          uVar4 = uVar4 + '\x01';
        }
      }
      *puVar6 = uVar4;
      packed_status = CONCAT22(DAT_febe5056,DAT_febe5054);
    }
    uVar1 = uVar1 + 1 & 0xff;
  }
  return;
}



void FUN_0006a280(undefined2 param_1)

{
  uint uVar1;
  
  if (DAT_febe5090 == '\0') {
    uVar1 = (uint)DAT_febe508a;
    DAT_febe508a = DAT_febe508a + 1;
    *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe50b6u)) + (uVar1 & 7) * 2) = param_1;
  }
  return;
}



/* Configured command8 callback27E54: low8 result0 selects44 else66. Route to direct phase5092 only
   if direct activation5091==1; otherwise write collected phase5097 without its activation check.
   Routing uses current activation, not a retained submission-bank token. Return0. */

uint f33_crypto_bank_key_update_completed(uchar result)

{
  uchar uVar1;
  
  uVar1 = 'f';
  if (result == '\0') {
    uVar1 = 'D';
  }
  if (f33_crypto_direct_activation == '\x01') {
    f33_crypto_direct_phase = uVar1;
    uVar1 = f33_crypto_collected_phase;
  }
  f33_crypto_collected_phase = uVar1;
  return 0;
}



/* Configured AES callback: nonzero result sets test phase44; zero compares fixed16-byte output and
   sets33/44. No active-generation check here; return0. */

uint f33_crypto_bank_aes_completed(uchar result)

{
  uint32_t puVar1;
  undefined1 uVar2;
  uint uVar3;
  
  puVar1 = 0xfebeb800u;
  uVar2 = 0x44;
  if (result == '\0') {
    puVar1 = 0xfebeb800u;
    uVar3 = f33_crypto_bank_compare_aes_result();
    uVar2 = (undefined1)uVar3;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6764))))) = uVar2;
  return 0;
}



/* Configured command7 job1 callback27E0C: nonzero result forces509D=1. Select direct phase if
   activation1, otherwise collected phase; set46. Return0; no submission-generation token. */

uint f33_crypto_bank_verification_completed(uchar result)

{
  uchar *puVar1;
  
  if (result != '\0') {
    f33_crypto_verification_result = '\x01';
  }
  puVar1 = ((void *)camry_host_ptr((uint32_t)((0xfebe5097u))));
  if (f33_crypto_direct_activation == '\x01') {
    puVar1 = ((void *)camry_host_ptr((uint32_t)((0xfebe5092u))));
  }
  *puVar1 = 'F';
  return 0;
}



/* Configured MAC job1 callback: nonzero result sets44; zero compares fixed16-byte output and
   sets33/44. Return0, no local active-generation check. */

uint f33_crypto_bank_mac_completed(uchar result)

{
  uint32_t puVar1;
  undefined1 uVar2;
  uint uVar3;
  
  puVar1 = 0xfebeb800u;
  uVar2 = 0x44;
  if (result == '\0') {
    puVar1 = 0xfebeb800u;
    uVar3 = f33_crypto_bank_compare_mac_result();
    uVar2 = (undefined1)uVar3;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6764))))) = uVar2;
  return 0;
}



undefined4 FUN_0006a31a(undefined2 param_1)

{
  DAT_febe5088 = param_1;
  return 0;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_6a322(void)

{
  return;
}



/* Constant source: return 0; shape-classified from the canonical corpus. Callers receive this
   literal directly; its meaning is not recovered. */

undefined4 f33_return_const_0_6a328(void)

{
  return 0;
}



undefined4 FUN_0006a32c(ushort param_1,uint *param_2)

{
  byte *pbVar1;
  int iVar2;
  undefined8 uVar3;
  undefined4 uVar4;
  uint uVar5;
  uint uVar6;
  uint uVar7;
  uint uVar8;
  
  uVar3 = 0x23dfc00000000;
  uVar6 = (uint)DAT_00028fd4;
  uVar4 = 0;
  iVar2 = 0;
  uVar7 = 0;
  while ((uVar7 < uVar6 && (iVar2 == 0))) {
    pbVar1 = ((byte *)camry_host_ptr((uint32_t)(uVar7 * 8 + (int)((ulonglong)uVar3 >> 0x20) + 0x51e8)));
    if ((ushort)*pbVar1 == (param_1 & 0xff)) {
      if ((((pbVar1[7] == 0x5a) && ((uintptr_t)(param_2)!=(uintptr_t)((uint *)0x0))) && (uVar8 = param_2[2], uVar8 != 0)) &&
         (7 < (*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 7)))))) {
        iVar2 = 0;
        uVar5 = 0;
        do {
          pbVar1 = ((byte *)camry_host_ptr((uint32_t)(uVar5 + uVar8)));
          uVar5 = uVar5 + 1;
          iVar2 = iVar2 + (uint)*pbVar1;
        } while (uVar5 < 7);
        if ((iVar2 + *param_2 + ((*param_2 & 0x700) >> 8) + 8 & 0xff) == (uint)(*((byte *)camry_host_ptr((uint32_t)(uVar8 + 7)))))
        {
          uVar4 = 0;
        }
        else {
          FUN_0008e7ba(param_1);
          uVar4 = 1;
        }
      }
      iVar2 = 0x5a;
    }
    uVar7 = uVar7 + 1 & 0xff;
  }
  return uVar4;
}



void FUN_0006a3be(undefined2 param_1, undefined4 param_2)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0x23dfcu;
  iVar2 = 0;
  if (DAT_00028fd6 != 'Z') {
    iVar2 = ((void)(param_1), f33_return_const_0_6a328());
  }
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x51d8u + (uint32_t)((int)(puVar1 + 3)))))) == (code)0x5a) && (iVar2 == 0)) {
    FUN_0006a32c(param_1, ((uint *)camry_host_ptr((uint32_t)(param_2))));
  }
  return;
}



/* Constant source: return 0; shape-classified from the canonical corpus. Callers receive this
   literal directly; its meaning is not recovered. */

undefined4 f33_return_const_0_6a3f0(void)

{
  return 0;
}



undefined4 FUN_0006a3f4(undefined2 param_1)

{
  undefined4 uVar1;
  
  if (DAT_00028fd6 == 'Z') {
    uVar1 = 0;
  }
  else {
    uVar1 = ((void)(param_1), f33_return_const_0_6a3f0());
  }
  return uVar1;
}



void FUN_0006a410(void)

{
  FUN_0008eff8();
  FUN_00089dec();
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_6a420(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_6a434(void)

{
  return;
}



void FUN_0006a440(void)

{
  uint uVar1;
  
  DAT_febe39dc = 0;
  uVar1 = 0;
  do {
    *(undefined4 *)(((undefined *)camry_host_ptr(0xfebe39e0u)) + uVar1 * 4) = 0xffff;
    uVar1 = uVar1 + 1;
  } while (uVar1 < 0x100);
  return;
}



void FUN_0006a522(short param_1,short *param_2)

{
  int iVar1;
  
  iVar1 = (int)param_1;
  if (iVar1 + 0x7fff < 0 == (-1 < iVar1 && iVar1 + 0x7fff < 0) && iVar1 != -0x7fff) {
    if (iVar1 < 0) {
      param_1 = -param_1;
    }
  }
  else {
    param_1 = 0x7fff;
  }
  *param_2 = param_1;
  return;
}



void FUN_0006a53e(int param_1,int *param_2)

{
  if (param_1 + 0x7fffffff < 0 == (-1 < param_1 && param_1 + 0x7fffffff < 0) &&
      param_1 != -0x7fffffff) {
    if (param_1 < 0) {
      param_1 = -param_1;
    }
  }
  else {
    param_1 = 0x7fffffff;
  }
  *param_2 = param_1;
  return;
}



void FUN_0006a55c(undefined4 param_1,undefined1 *param_2)

{
  *param_2 = (char)((uint)param_1 >> 0x18);
  param_2[1] = (char)((uint)param_1 >> 0x10);
  param_2[2] = (char)((uint)param_1 >> 8);
  param_2[3] = (char)param_1;
  return;
}



void FUN_0006a574(undefined4 param_1,undefined1 *param_2)

{
  *param_2 = (char)((uint)param_1 >> 8);
  param_2[1] = (char)param_1;
  return;
}



void FUN_0006a594(undefined4 param_1,undefined1 *param_2)

{
  *param_2 = (char)((uint)param_1 >> 0x18);
  param_2[1] = (char)((uint)param_1 >> 0x10);
  param_2[2] = (char)((uint)param_1 >> 8);
  param_2[3] = (char)param_1;
  return;
}



void FUN_0006a5ac(undefined4 param_1,undefined1 *param_2)

{
  *param_2 = (char)((uint)param_1 >> 8);
  param_2[1] = (char)param_1;
  return;
}



void FUN_0006a5cc(short param_1,undefined1 *param_2)

{
  undefined1 uVar1;
  int iVar2;
  
  iVar2 = (int)param_1;
  if (iVar2 + 0x7f < 0 == (-1 < iVar2 && iVar2 + 0x7f < 0)) {
    if (iVar2 + -0x7f < 0 == (iVar2 < 0 && -1 < iVar2 + -0x7f) && iVar2 != 0x7f) {
      uVar1 = 0x7f;
    }
    else {
      if (iVar2 + 0x80 < 0 != (-1 < iVar2 && iVar2 + 0x80 < 0) || iVar2 == -0x80) {
        iVar2 = -0x80;
      }
      uVar1 = (undefined1)iVar2;
    }
  }
  else {
    uVar1 = 0x81;
  }
  *param_2 = uVar1;
  return;
}



void FUN_0006a5fa(int param_1,undefined2 *param_2)

{
  undefined2 uVar1;
  
  if (param_1 + 0x7fff < 0 == (-1 < param_1 && param_1 + 0x7fff < 0)) {
    if (param_1 + -0x7fff < 0 == (param_1 < 0 && -1 < param_1 + -0x7fff) && param_1 != 0x7fff) {
      uVar1 = 0x7fff;
    }
    else {
      if (param_1 + 0x8000 < 0 != (-1 < param_1 && param_1 + 0x8000 < 0) || param_1 == -0x8000) {
        param_1 = -0x8000;
      }
      uVar1 = (undefined2)param_1;
    }
  }
  else {
    uVar1 = 0x8001;
  }
  *param_2 = uVar1;
  return;
}



void FUN_0006a624(uint param_1,undefined1 *param_2)

{
  undefined1 uVar1;
  
  uVar1 = 0;
  if (-1 < (int)param_1) {
    if (param_1 < 0xff) {
      uVar1 = (undefined1)param_1;
    }
    else {
      uVar1 = 0xff;
    }
  }
  *param_2 = uVar1;
  return;
}



/* WARNING: Removing unreachable block (ram,0x0006a668) */
/* Use coefficient1..65535, otherwise65536. Compute low32 accumulator +
   coefficient*(target-previous); publish signed division by65536 narrowed16, not SAR rounding.
   Eight-byte previous/target/accumulator record. Coefficient outside1..65535 becomes65536; low32
   fractional recurrence publishes signed truncation by65536 narrowed16. */

void f33_follow_s16_fractional
               (F33FractionalFollowing16 *state,uint coefficient,short *output,int *new_accumulator)

{
  int iVar1;
  
  if (0xfffe < coefficient - 1) {
    coefficient = 0x10000;
  }
  iVar1 = (int)state->target * coefficient +
          (state->accumulator - (int)state->previous * coefficient);
  *new_accumulator = iVar1;
  *output = (short)(iVar1 / 0x10000);
  return;
}



void FUN_0006a678(ushort *param_1,int param_2,undefined2 *param_3,int *param_4)

{
  int iVar1;
  
  if (0xfffe < param_2 - 1U) {
    param_2 = 0x10000;
  }
  iVar1 = (uint)param_1[1] * param_2 + (*(int *)(param_1 + 2) - (uint)*param_1 * param_2);
  *param_3 = (short)((uint)iVar1 >> 0x10);
  *param_4 = iVar1;
  return;
}



/* statusFF; pass/fail/highwater0; padding byte1 untouched. Eight-byte
   layout:status0,padding1,pass2,fail4,highwater6. */

void f33_reset_terminal_monitor(F33TerminalMonitorState *state)

{
  state->status = 0xff;
  state->passing_count = 0;
  state->failing_count = 0;
  state->failing_high_water = 0;
  return;
}



/* Inputs r6 state*,r7 two uint16 thresholds*,r8 three-pointer callback table*. Test fail>threshold
   first => status22 with no predicate or callback. Else pass>threshold => status0 with no predicate
   or callback. Else call table[0].11 clears fail and increments pass; crossing strict
   pass>threshold sets0 and calls table[1] once.22 clears pass and increments fail, updates
   highwater max; crossing fail>threshold sets22 and calls table[2] once.44 or any other
   classification storesFF and preserves all counters/highwater. Result r10 always11, not stored
   status. No automatic recovery from either terminal state before explicit reset. Native exact-mode
   range compositions distinguish count==200 from strict failure crossing and preserve the previous
   action until confirmation. Other configured predicates remain statically reconstructed. */

uint f33_step_terminal_monitor
               (F33TerminalMonitorState *state,F33MonitorLimits *thresholds,
               F33TerminalMonitorCallbacks *callbacks)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  F33MonitorAction *pFVar4;
  ushort uVar5;
  uchar uVar6;
  uchar uVar7;
  uint uVar8;
  uint uVar9;
  
  uVar9 = (uint)state->failing_count;
  uVar2 = (uint)thresholds->failing_limit;
  uVar8 = (uint)state->passing_count;
  uVar5 = state->failing_high_water;
  if ((int)(uVar9 - uVar2) < 0 || uVar9 == uVar2) {
    uVar3 = (uint)thresholds->passing_limit;
    if ((int)(uVar8 - uVar3) < 0 || uVar8 == uVar3) {
      uVar6 = 0xff;
      uVar1 = (*(int (*)())callbacks->classify)();
      if (uVar1 == 0x11) {
        uVar9 = 0;
        if (((int)(uVar8 - uVar3) < 0 || uVar8 == uVar3) &&
           (uVar8 = uVar8 + 1, (int)(uVar8 - uVar3) < 0 || uVar8 == uVar3)) goto LAB_0006a732;
        pFVar4 = ((void *)camry_host_ptr((uint32_t)(callbacks->healthy_observed)));
        uVar7 = '\0';
        uVar6 = '\0';
      }
      else {
        if (uVar1 != 0x22) goto LAB_0006a732;
        uVar8 = 0;
        if ((int)(uVar9 - uVar2) < 0 || uVar9 == uVar2) {
          uVar9 = uVar9 + 1;
        }
        uVar3 = uVar9;
        if (-1 < (int)(uVar5 - uVar9)) {
          uVar3 = (uint)uVar5;
        }
        uVar5 = (ushort)uVar3;
        if ((int)(uVar9 - uVar2) < 0 || uVar9 == uVar2) goto LAB_0006a732;
        pFVar4 = ((void *)camry_host_ptr((uint32_t)(callbacks->failed)));
        uVar7 = '\"';
        uVar6 = '\"';
      }
      if ((uintptr_t)(pFVar4)!=(uintptr_t)(f33_reset_vector)) {
        (*(int (*)())pFVar4)();
        uVar6 = uVar7;
      }
    }
    else {
      uVar6 = '\0';
    }
  }
  else {
    uVar6 = '\"';
  }
LAB_0006a732:
  state->status = uVar6;
  state->passing_count = (ushort)uVar8;
  state->failing_count = (ushort)uVar9;
  state->failing_high_water = uVar5;
  return 0x11;
}



undefined4 FUN_0006a780(undefined1 *param_1,ushort *param_2,int param_3)

{
  ushort uVar1;
  undefined4 uVar2;
  code *pcVar3;
  
  uVar2 = 0x11;
  if ((((uintptr_t)(param_1)==(uintptr_t)((undefined1 *)0x0)) || ((uintptr_t)(param_2)==(uintptr_t)((ushort *)0x0))) || (param_3 == 0)) {
    uVar2 = 0x22;
  }
  else {
    uVar1 = param_2[1];
    if (((int)((uint)*(ushort *)(param_1 + 4) - (uint)uVar1) < 0 ||
         (uint)*(ushort *)(param_1 + 4) == (uint)uVar1) &&
       ((int)((uint)*(ushort *)(param_1 + 2) - (uint)*param_2) < 0 ||
        (uint)*(ushort *)(param_1 + 2) == (uint)*param_2)) {
      pcVar3 = *(code **)(param_3 + 8);
      *param_1 = 0x22;
      if ((uintptr_t)(pcVar3)!=(uintptr_t)(f33_reset_vector)) {
        (*(int (*)())pcVar3)();
      }
      *(undefined2 *)(param_1 + 2) = 0;
      *(ushort *)(param_1 + 4) = uVar1 + 1;
      *(ushort *)(param_1 + 6) = uVar1 + 1;
    }
  }
  return uVar2;
}



undefined4 FUN_0006a7d8(undefined1 *param_1,ushort *param_2,undefined4 *param_3)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  ushort uVar4;
  code *pcVar5;
  undefined1 uVar6;
  undefined1 uVar7;
  uint uVar8;
  uint uVar9;
  
  if (((((uintptr_t)(param_1)==(uintptr_t)((undefined1 *)0x0)) || ((uintptr_t)(param_2)==(uintptr_t)((ushort *)0x0))) ||
      ((uintptr_t)(param_3)==(uintptr_t)((undefined4 *)0x0))) || ((uintptr_t)((code *)*param_3)==(uintptr_t)(f33_reset_vector))) {
    return 0x22;
  }
  uVar9 = (uint)*(ushort *)(param_1 + 4);
  uVar3 = (uint)param_2[1];
  uVar8 = (uint)*(ushort *)(param_1 + 2);
  uVar4 = *(ushort *)(param_1 + 6);
  if ((int)(uVar9 - uVar3) < 0 || uVar9 == uVar3) {
    uVar2 = (uint)*param_2;
    if ((int)(uVar8 - uVar2) < 0 || uVar8 == uVar2) {
      uVar6 = 0xff;
      iVar1 = (*(int (*)())*param_3)();
      if (iVar1 == 0x11) {
        uVar8 = uVar8 + 1;
        if ((int)(uVar8 - uVar2) < 0 || uVar8 == uVar2) goto LAB_0006a864;
        pcVar5 = (code *)param_3[1];
        uVar7 = 0;
        uVar6 = 0;
      }
      else {
        if (iVar1 != 0x22) goto LAB_0006a864;
        uVar8 = 0;
        if ((int)(uVar9 - uVar3) < 0 || uVar9 == uVar3) {
          uVar9 = uVar9 + 1;
        }
        uVar2 = uVar9;
        if (-1 < (int)(uVar4 - uVar9)) {
          uVar2 = (uint)uVar4;
        }
        uVar4 = (ushort)uVar2;
        if ((int)(uVar9 - uVar3) < 0 || uVar9 == uVar3) goto LAB_0006a864;
        pcVar5 = (code *)param_3[2];
        uVar7 = 0x22;
        uVar6 = 0x22;
      }
      if ((uintptr_t)(pcVar5)!=(uintptr_t)(f33_reset_vector)) {
        (*(int (*)())pcVar5)();
        uVar6 = uVar7;
      }
    }
    else {
      uVar6 = 0;
    }
  }
  else {
    uVar6 = 0x22;
  }
LAB_0006a864:
  *param_1 = uVar6;
  *(short *)(param_1 + 2) = (short)uVar8;
  *(short *)(param_1 + 4) = (short)uVar9;
  *(ushort *)(param_1 + 6) = uVar4;
  return 0x11;
}



/* Clear all12 bytes: packed status,passing/failing counts,failure high-water and recovery count. */

void f33_reset_recoverable_monitor(F33RecoverableMonitorState *state)

{
  state->packed_status = 0;
  state->passing_count = 0;
  state->failing_count = 0;
  state->failing_high_water = 0;
  state->recovery_count = 0;
  return;
}



/* Retain confirmed failure22 including its recovery count; preserve confirmed pass2200,otherwise
   discard pending counts. Clear recovery only outside confirmed failure; high-water survives. No
   predicate or reporting callback. */

void f33_retain_disabled_recoverable_monitor
               (F33RecoverableMonitorState *state,F33RecoverableMonitorLimits *limits)

{
  uint uVar1;
  
  if ((uintptr_t)(limits->failing_limit)<(uintptr_t)(state->failing_count)) {
    uVar1 = 0x22;
  }
  else {
    if ((state->failing_count == 0) && ((uintptr_t)(limits->passing_limit)<(uintptr_t)(state->passing_count))) {
      uVar1 = 0x2200;
    }
    else {
      state->passing_count = 0;
      uVar1 = 0;
    }
    state->failing_count = 0;
    state->recovery_count = 0;
  }
  state->packed_status = uVar1;
  return;
}



/* Twelve-byte state and15-pointer callbacks. Pending confirmation follows strict passing/failing
   thresholds. Confirmed failure calls third predicate and70F56 recovery scratch: strict
   recovery_count>limit clears current counts/status and invokes recovery callback. Preserve failure
   high-water. Stores packed status; returns full R10=11. The local recovery scratch is not the same
   layout as persistent state. Native paired raw-thermistor recovery accepts both inclusive
   endpoints and clears current status after recovery26>25, preserving failure high-water. */

uint f33_step_recoverable_monitor
               (F33RecoverableMonitorState *state,F33RecoverableMonitorLimits *limits,
               F33RecoverableMonitorCallbacks *callbacks)

{
  ushort uVar1;
  ushort uVar2;
  uint uVar3;
  uint uVar4;
  short sVar5;
  ushort uVar6;
  F33MonitorAction *pFVar7;
  ushort local_2c;
  F33MonitorRecoveryScratch FStack_2a;
  
  FStack_2a.failing_high_water = state->failing_high_water;
  FStack_2a.passing_count = state->passing_count;
  FStack_2a.failing_count = state->failing_count;
  FStack_2a.recovery_count = state->recovery_count;
  uVar1 = limits->passing_limit;
  local_2c = limits->recovery_limit;
  uVar2 = limits->failing_limit;
  if (FStack_2a.failing_count == 0) {
    if (uVar1 < FStack_2a.passing_count) {
      sVar5 = 0x2200;
    }
    else {
      sVar5 = 0;
      if (FStack_2a.passing_count != 0) {
        sVar5 = 0x1100;
      }
    }
  }
  else {
    sVar5 = 0x22;
    if (FStack_2a.failing_count <= uVar2) {
      sVar5 = 0x11;
    }
  }
  if (sVar5 == 0) {
    uVar4 = (*(int (*)())callbacks->classify_normal)();
    if (uVar4 == 0x11) {
      if ((uVar1 < FStack_2a.passing_count) ||
         (uVar2 = FStack_2a.passing_count + 1, uVar6 = FStack_2a.passing_count + 1,
         FStack_2a.passing_count = uVar2, uVar1 < uVar6)) {
        uVar4 = 0x2200;
      }
      else {
        uVar4 = 0x11001100;
      }
      FStack_2a.failing_count = 0;
    }
    else if (uVar4 == 0x22) {
      FStack_2a.passing_count = 0;
      if (FStack_2a.failing_count <= uVar2) {
        FStack_2a.failing_count = FStack_2a.failing_count + 1;
      }
      if (FStack_2a.failing_high_water < FStack_2a.failing_count) {
        FStack_2a.failing_high_water = FStack_2a.failing_count;
      }
      uVar4 = 0x22;
      if (FStack_2a.failing_count <= uVar2) {
        uVar4 = 0x110011;
      }
    }
    else if ((uVar4 == 0x33) || (uVar4 == 0x44)) {
      FStack_2a.failing_count = 0;
      FStack_2a.passing_count = 0;
      uVar4 = 0;
    }
    else {
      uVar4 = 0xffff;
    }
    uVar3 = uVar4 & 0xffff;
    if (uVar3 == 0) goto LAB_0006add8;
    if (uVar3 == 0x11) {
      if ((uintptr_t)(callbacks->enter_failing)!=(uintptr_t)(f33_reset_vector)) {
        (*(int (*)())callbacks->enter_failing)();
      }
      pFVar7 = ((void *)camry_host_ptr((uint32_t)(callbacks->repeat_pending_failing)));
    }
    else if (uVar3 == 0x22) {
      if ((uintptr_t)(callbacks->enter_failing)!=(uintptr_t)(f33_reset_vector)) {
        (*(int (*)())callbacks->enter_failing)();
      }
      if ((uintptr_t)(callbacks->confirm_failing)!=(uintptr_t)(f33_reset_vector)) {
        (*(int (*)())callbacks->confirm_failing)();
      }
      pFVar7 = ((void *)camry_host_ptr((uint32_t)(callbacks->repeat_confirmed_failing)));
    }
    else if (uVar3 == 0x1100) {
      if ((uintptr_t)(callbacks->enter_passing)!=(uintptr_t)(f33_reset_vector)) {
        (*(int (*)())callbacks->enter_passing)();
      }
      pFVar7 = ((void *)camry_host_ptr((uint32_t)(callbacks->repeat_pending_passing)));
    }
    else {
      if (uVar3 != 0x2200) {
        uVar4 = 0;
        goto LAB_0006add8;
      }
      if ((uintptr_t)(callbacks->enter_passing)!=(uintptr_t)(f33_reset_vector)) {
        (*(int (*)())callbacks->enter_passing)();
      }
      if ((uintptr_t)(callbacks->confirm_passing)!=(uintptr_t)(f33_reset_vector)) {
        (*(int (*)())callbacks->confirm_passing)();
      }
      pFVar7 = ((void *)camry_host_ptr((uint32_t)(callbacks->repeat_confirmed_passing)));
    }
    goto joined_r0x0006abfe;
  }
  if (sVar5 == 0x11) {
    uVar4 = (*(int (*)())callbacks->classify_failing)();
    if (uVar4 == 0x11) {
      if ((uVar1 < FStack_2a.passing_count) ||
         (uVar2 = FStack_2a.passing_count + 1, uVar6 = FStack_2a.passing_count + 1,
         FStack_2a.passing_count = uVar2, uVar1 < uVar6)) {
        uVar4 = 0x2200;
      }
      else {
        uVar4 = 0x11001100;
      }
      FStack_2a.failing_count = 0;
    }
    else if (uVar4 == 0x22) {
      FStack_2a.passing_count = 0;
      if (FStack_2a.failing_count <= uVar2) {
        FStack_2a.failing_count = FStack_2a.failing_count + 1;
      }
      if (FStack_2a.failing_high_water < FStack_2a.failing_count) {
        FStack_2a.failing_high_water = FStack_2a.failing_count;
      }
      uVar4 = 0x22;
      if (FStack_2a.failing_count <= uVar2) {
        uVar4 = 0x110011;
      }
    }
    else if ((uVar4 == 0x33) || (uVar4 == 0x44)) {
      FStack_2a.failing_count = 0;
      FStack_2a.passing_count = 0;
      uVar4 = 0;
    }
    else {
      uVar4 = 0xffff;
    }
    uVar3 = uVar4 & 0xffff;
    if (uVar3 != 0) {
      if (uVar3 == 0x11) {
        pFVar7 = ((void *)camry_host_ptr((uint32_t)(callbacks->repeat_pending_failing)));
      }
      else if (uVar3 == 0x22) {
        if ((uintptr_t)(callbacks->confirm_failing)!=(uintptr_t)(f33_reset_vector)) {
          (*(int (*)())callbacks->confirm_failing)();
        }
        pFVar7 = ((void *)camry_host_ptr((uint32_t)(callbacks->repeat_confirmed_failing)));
      }
      else if (uVar3 == 0x1100) {
        if ((uintptr_t)(callbacks->leave_pending_failing)!=(uintptr_t)(f33_reset_vector)) {
          (*(int (*)())callbacks->leave_pending_failing)();
        }
        if ((uintptr_t)(callbacks->enter_passing)!=(uintptr_t)(f33_reset_vector)) {
          (*(int (*)())callbacks->enter_passing)();
        }
        pFVar7 = ((void *)camry_host_ptr((uint32_t)(callbacks->repeat_pending_passing)));
      }
      else {
        if (uVar3 != 0x2200) {
          if ((uintptr_t)(callbacks->repeat_pending_failing)!=(uintptr_t)(f33_reset_vector)) {
            (*(int (*)())callbacks->repeat_pending_failing)();
          }
          uVar4 = 0x11;
          goto LAB_0006add8;
        }
        if ((uintptr_t)(callbacks->leave_pending_failing)!=(uintptr_t)(f33_reset_vector)) {
          (*(int (*)())callbacks->leave_pending_failing)();
        }
        if ((uintptr_t)(callbacks->enter_passing)!=(uintptr_t)(f33_reset_vector)) {
          (*(int (*)())callbacks->enter_passing)();
        }
        if ((uintptr_t)(callbacks->confirm_passing)!=(uintptr_t)(f33_reset_vector)) {
          (*(int (*)())callbacks->confirm_passing)();
        }
        pFVar7 = ((void *)camry_host_ptr((uint32_t)(callbacks->repeat_confirmed_passing)));
      }
      goto joined_r0x0006abfe;
    }
    pFVar7 = ((void *)camry_host_ptr((uint32_t)(callbacks->leave_pending_failing)));
joined_r0x0006ad1a:
    if ((uintptr_t)(pFVar7)!=(uintptr_t)(f33_reset_vector)) {
      (*(int (*)())pFVar7)();
    }
  }
  else {
    if (sVar5 == 0x1100) {
      uVar4 = (*(int (*)())callbacks->classify_normal)();
      if (uVar4 == 0x11) {
        if ((uVar1 < FStack_2a.passing_count) ||
           (uVar2 = FStack_2a.passing_count + 1, uVar6 = FStack_2a.passing_count + 1,
           FStack_2a.passing_count = uVar2, uVar1 < uVar6)) {
          uVar4 = 0x2200;
        }
        else {
          uVar4 = 0x11001100;
        }
        FStack_2a.failing_count = 0;
      }
      else if (uVar4 == 0x22) {
        FStack_2a.passing_count = 0;
        if (FStack_2a.failing_count <= uVar2) {
          FStack_2a.failing_count = FStack_2a.failing_count + 1;
        }
        if (FStack_2a.failing_high_water < FStack_2a.failing_count) {
          FStack_2a.failing_high_water = FStack_2a.failing_count;
        }
        uVar4 = 0x22;
        if (FStack_2a.failing_count <= uVar2) {
          uVar4 = 0x110011;
        }
      }
      else if ((uVar4 == 0x33) || (uVar4 == 0x44)) {
        FStack_2a.failing_count = 0;
        FStack_2a.passing_count = 0;
        uVar4 = 0;
      }
      else {
        uVar4 = 0xffff;
      }
      uVar3 = uVar4 & 0xffff;
      if (uVar3 == 0) {
        pFVar7 = ((void *)camry_host_ptr((uint32_t)(callbacks->leave_pending_passing)));
        goto joined_r0x0006ad1a;
      }
      if (uVar3 == 0x11) {
        if ((uintptr_t)(callbacks->leave_pending_passing)!=(uintptr_t)(f33_reset_vector)) {
          (*(int (*)())callbacks->leave_pending_passing)();
        }
        if ((uintptr_t)(callbacks->enter_failing)!=(uintptr_t)(f33_reset_vector)) {
          (*(int (*)())callbacks->enter_failing)();
        }
        pFVar7 = ((void *)camry_host_ptr((uint32_t)(callbacks->repeat_pending_failing)));
      }
      else if (uVar3 == 0x22) {
        if ((uintptr_t)(callbacks->leave_pending_passing)!=(uintptr_t)(f33_reset_vector)) {
          (*(int (*)())callbacks->leave_pending_passing)();
        }
        if ((uintptr_t)(callbacks->enter_failing)!=(uintptr_t)(f33_reset_vector)) {
          (*(int (*)())callbacks->enter_failing)();
        }
        if ((uintptr_t)(callbacks->confirm_failing)!=(uintptr_t)(f33_reset_vector)) {
          (*(int (*)())callbacks->confirm_failing)();
        }
        pFVar7 = ((void *)camry_host_ptr((uint32_t)(callbacks->repeat_confirmed_failing)));
      }
      else if (uVar3 == 0x1100) {
        pFVar7 = ((void *)camry_host_ptr((uint32_t)(callbacks->repeat_pending_passing)));
      }
      else {
        if (uVar3 != 0x2200) {
          if ((uintptr_t)(callbacks->repeat_pending_passing)!=(uintptr_t)(f33_reset_vector)) {
            (*(int (*)())callbacks->repeat_pending_passing)();
          }
          uVar4 = 0x1100;
          goto LAB_0006add8;
        }
        if ((uintptr_t)(callbacks->confirm_passing)!=(uintptr_t)(f33_reset_vector)) {
          (*(int (*)())callbacks->confirm_passing)();
        }
        pFVar7 = ((void *)camry_host_ptr((uint32_t)(callbacks->repeat_confirmed_passing)));
      }
    }
    else if (sVar5 == 0x2200) {
      uVar4 = (*(int (*)())callbacks->classify_normal)();
      if (uVar4 == 0x11) {
LAB_0006a970:
        FStack_2a.failing_count = 0;
LAB_0006a974:
        uVar4 = 0x2200;
      }
      else {
        if (uVar4 != 0x22) {
          if ((uVar4 == 0x33) || (uVar4 == 0x44)) goto LAB_0006a970;
          goto LAB_0006a974;
        }
        FStack_2a.passing_count = 0;
        if (FStack_2a.failing_count <= uVar2) {
          FStack_2a.failing_count = FStack_2a.failing_count + 1;
        }
        if (FStack_2a.failing_high_water < FStack_2a.failing_count) {
          FStack_2a.failing_high_water = FStack_2a.failing_count;
        }
        uVar4 = 0x22;
        if (FStack_2a.failing_count <= uVar2) {
          uVar4 = 0x110011;
        }
      }
      uVar3 = uVar4 & 0xffff;
      if (uVar3 == 0) {
        pFVar7 = ((void *)camry_host_ptr((uint32_t)(callbacks->leave_confirmed_passing)));
        goto joined_r0x0006ad1a;
      }
      if (uVar3 == 0x11) {
        if ((uintptr_t)(callbacks->leave_confirmed_passing)!=(uintptr_t)(f33_reset_vector)) {
          (*(int (*)())callbacks->leave_confirmed_passing)();
        }
        if ((uintptr_t)(callbacks->enter_failing)!=(uintptr_t)(f33_reset_vector)) {
          (*(int (*)())callbacks->enter_failing)();
        }
        pFVar7 = ((void *)camry_host_ptr((uint32_t)(callbacks->repeat_pending_failing)));
      }
      else if (uVar3 == 0x22) {
        if ((uintptr_t)(callbacks->leave_confirmed_passing)!=(uintptr_t)(f33_reset_vector)) {
          (*(int (*)())callbacks->leave_confirmed_passing)();
        }
        if ((uintptr_t)(callbacks->enter_failing)!=(uintptr_t)(f33_reset_vector)) {
          (*(int (*)())callbacks->enter_failing)();
        }
        if ((uintptr_t)(callbacks->confirm_failing)!=(uintptr_t)(f33_reset_vector)) {
          (*(int (*)())callbacks->confirm_failing)();
        }
        pFVar7 = ((void *)camry_host_ptr((uint32_t)(callbacks->repeat_confirmed_failing)));
      }
      else {
        pFVar7 = ((void *)camry_host_ptr((uint32_t)(callbacks->repeat_confirmed_passing)));
        if (uVar3 != 0x2200) {
          if ((uintptr_t)(pFVar7)!=(uintptr_t)(f33_reset_vector)) {
            (*(int (*)())pFVar7)();
          }
          uVar4 = 0x2200;
          goto LAB_0006add8;
        }
      }
    }
    else {
      uVar4 = (*(int (*)())callbacks->classify_recovery)();
      uVar4 = f33_step_monitor_recovery_scratch((uchar)uVar4,&FStack_2a,&local_2c);
      if ((uVar4 & 0xffff) == 0) {
        pFVar7 = ((void *)camry_host_ptr((uint32_t)(callbacks->recover_confirmed_failing)));
      }
      else {
        pFVar7 = ((void *)camry_host_ptr((uint32_t)(callbacks->repeat_confirmed_failing)));
        if ((uVar4 & 0xffff) != 0x22) {
          if ((uintptr_t)(pFVar7)!=(uintptr_t)(f33_reset_vector)) {
            (*(int (*)())pFVar7)();
          }
          uVar4 = 0x22;
          goto LAB_0006add8;
        }
      }
    }
joined_r0x0006abfe:
    if ((uintptr_t)(pFVar7)!=(uintptr_t)(f33_reset_vector)) {
      (*(int (*)())pFVar7)();
    }
  }
LAB_0006add8:
  state->packed_status = uVar4;
  state->passing_count = FStack_2a.passing_count;
  state->failing_count = FStack_2a.failing_count;
  state->failing_high_water = FStack_2a.failing_high_water;
  state->recovery_count = FStack_2a.recovery_count;
  return 0x11;
}



/* Clear packed status, passing/failing counts and failure high-water at offsets0/4/6/8. Exactly10
   bytes of the usual12-byte allocation; adjacent halfword untouched. */

void f33_reset_latched_monitor(F33LatchedMonitorState *state)

{
  state->packed_status = 0;
  state->passing_count = 0;
  state->failing_count = 0;
  state->failing_high_water = 0;
  return;
}



/* Clear14 used bytes of16-byte state allocation: result,pass count/window,fail count/window,fail
   high-water. Adjacent trailing halfword untouched. */

void f33_reset_windowed_monitor(F33WindowedMonitorState *state)

{
  state->packed_status = 0;
  state->passing_count = 0;
  state->passing_window = 0;
  state->failing_count = 0;
  state->failing_window = 0;
  state->failing_high_water = 0;
  return;
}



/* Recompute state from counters without callbacks: retain failure22 when fail_count>fail_limit;
   otherwise retain pass2200 only when fail_count=0 and pass_count>pass_limit. Clear pending paths;
   preserve failure high-water. Gate closure is not a reset of a confirmed failure. */

void f33_retain_disabled_latched_monitor(F33LatchedMonitorState *state,F33MonitorLimits *limits)

{
  uint uVar1;
  
  if ((uintptr_t)(limits->failing_limit)<(uintptr_t)(state->failing_count)) {
    uVar1 = 0x22;
  }
  else {
    if ((state->failing_count == 0) && ((uintptr_t)(limits->passing_limit)<(uintptr_t)(state->passing_count))) {
      uVar1 = 0x2200;
    }
    else {
      state->passing_count = 0;
      uVar1 = 0;
    }
    state->failing_count = 0;
  }
  state->packed_status = uVar1;
  return;
}



void FUN_0006ae48(undefined4 *param_1,ushort *param_2)

{
  undefined4 uVar1;
  
  if (param_2[2] < *(ushort *)(param_1 + 2)) {
    uVar1 = 0x22;
  }
  else {
    if ((*(ushort *)(param_1 + 2) == 0) && (*param_2 < *(ushort *)(param_1 + 1))) {
      uVar1 = 0x2200;
    }
    else {
      *(undefined2 *)(param_1 + 1) = 0;
      uVar1 = 0;
      (*((undefined2 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 6)))) = 0;
    }
    *(undefined2 *)(param_1 + 2) = 0;
    (*((undefined2 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 10)))) = 0;
  }
  *param_1 = uVar1;
  return;
}



/* Ten-byte state and13-pointer callbacks. Derive phase from counters, not old packed status.11/22
   classify healthy/failure; strict counter>limit confirms. Failed22 is terminal and bypasses
   predicates; confirmed healthy still evaluates entry predicate for failure. Pending33/44 resets
   both current counts. Transition hooks differ from repeated-state hooks. Write packed
   status0/11001100/2200/00110011/22; return full R10=11,not status. */

uint f33_step_latched_monitor
               (F33LatchedMonitorState *state,F33MonitorLimits *limits,
               F33TwoSidedMonitorCallbacks *callbacks)

{
  ushort uVar1;
  ushort uVar2;
  short sVar3;
  uint uVar4;
  uint uVar5;
  ushort uVar6;
  ushort uVar7;
  ushort uVar8;
  F33MonitorAction *pFVar9;
  
  uVar8 = state->failing_count;
  uVar7 = state->passing_count;
  uVar6 = state->failing_high_water;
  uVar1 = limits->passing_limit;
  uVar2 = limits->failing_limit;
  if (uVar8 == 0) {
    if (uVar1 < uVar7) {
      sVar3 = 0x2200;
    }
    else {
      sVar3 = 0;
      if (uVar7 != 0) {
        sVar3 = 0x1100;
      }
    }
  }
  else {
    sVar3 = 0x22;
    if (uVar8 <= uVar2) {
      sVar3 = 0x11;
    }
  }
  if (sVar3 == 0) {
    uVar5 = (*(int (*)())callbacks->classify_normal)();
    if (uVar5 == 0x11) {
      if ((uVar1 < uVar7) || (uVar7 = uVar7 + 1, uVar1 < uVar7)) {
        uVar5 = 0x2200;
      }
      else {
        uVar5 = 0x11001100;
      }
      uVar8 = 0;
    }
    else if (uVar5 == 0x22) {
      uVar7 = 0;
      if (uVar8 <= uVar2) {
        uVar8 = uVar8 + 1;
      }
      uVar1 = uVar8;
      if (uVar8 <= uVar6) {
        uVar1 = uVar6;
      }
      uVar6 = uVar1;
      uVar5 = 0x22;
      if (uVar8 <= uVar2) {
        uVar5 = 0x110011;
      }
    }
    else if ((uVar5 == 0x33) || (uVar5 == 0x44)) {
      uVar7 = 0;
      uVar8 = 0;
      uVar5 = 0;
    }
    else {
      uVar5 = 0xffff;
    }
    uVar4 = uVar5 & 0xffff;
    if (uVar4 != 0) {
      if (uVar4 == 0x11) {
        if ((uintptr_t)(callbacks->enter_failing)!=(uintptr_t)(f33_reset_vector)) {
          (*(int (*)())callbacks->enter_failing)();
        }
        pFVar9 = ((void *)camry_host_ptr((uint32_t)(callbacks->repeat_pending_failing)));
      }
      else if (uVar4 == 0x22) {
        if ((uintptr_t)(callbacks->enter_failing)!=(uintptr_t)(f33_reset_vector)) {
          (*(int (*)())callbacks->enter_failing)();
        }
        if ((uintptr_t)(callbacks->confirm_failing)!=(uintptr_t)(f33_reset_vector)) {
          (*(int (*)())callbacks->confirm_failing)();
        }
        pFVar9 = ((void *)camry_host_ptr((uint32_t)(callbacks->repeat_confirmed_failing)));
      }
      else if (uVar4 == 0x1100) {
        if ((uintptr_t)(callbacks->enter_passing)!=(uintptr_t)(f33_reset_vector)) {
          (*(int (*)())callbacks->enter_passing)();
        }
        pFVar9 = ((void *)camry_host_ptr((uint32_t)(callbacks->repeat_pending_passing)));
      }
      else {
        if (uVar4 != 0x2200) {
          uVar5 = 0;
          goto LAB_0006b308;
        }
        if ((uintptr_t)(callbacks->enter_passing)!=(uintptr_t)(f33_reset_vector)) {
          (*(int (*)())callbacks->enter_passing)();
        }
        if ((uintptr_t)(callbacks->confirm_passing)!=(uintptr_t)(f33_reset_vector)) {
          (*(int (*)())callbacks->confirm_passing)();
        }
        pFVar9 = ((void *)camry_host_ptr((uint32_t)(callbacks->repeat_confirmed_passing)));
      }
      if ((uintptr_t)(pFVar9)!=(uintptr_t)(f33_reset_vector)) {
        (*(int (*)())pFVar9)();
      }
    }
    goto LAB_0006b308;
  }
  if (sVar3 == 0x11) {
    uVar5 = (*(int (*)())callbacks->classify_failing)();
    if (uVar5 == 0x11) {
      if ((uVar1 < uVar7) || (uVar7 = uVar7 + 1, uVar1 < uVar7)) {
        uVar5 = 0x2200;
      }
      else {
        uVar5 = 0x11001100;
      }
      uVar8 = 0;
    }
    else if (uVar5 == 0x22) {
      uVar7 = 0;
      if (uVar8 <= uVar2) {
        uVar8 = uVar8 + 1;
      }
      uVar1 = uVar8;
      if (uVar8 <= uVar6) {
        uVar1 = uVar6;
      }
      uVar6 = uVar1;
      uVar5 = 0x22;
      if (uVar8 <= uVar2) {
        uVar5 = 0x110011;
      }
    }
    else if ((uVar5 == 0x33) || (uVar5 == 0x44)) {
      uVar7 = 0;
      uVar8 = 0;
      uVar5 = 0;
    }
    else {
      uVar5 = 0xffff;
    }
    uVar4 = uVar5 & 0xffff;
    if (uVar4 == 0) {
      if ((uintptr_t)(callbacks->leave_pending_failing)!=(uintptr_t)(f33_reset_vector)) {
        (*(int (*)())callbacks->leave_pending_failing)();
      }
    }
    else {
      if (uVar4 == 0x11) {
        pFVar9 = ((void *)camry_host_ptr((uint32_t)(callbacks->repeat_pending_failing)));
      }
      else if (uVar4 == 0x22) {
        if ((uintptr_t)(callbacks->confirm_failing)!=(uintptr_t)(f33_reset_vector)) {
          (*(int (*)())callbacks->confirm_failing)();
        }
        pFVar9 = ((void *)camry_host_ptr((uint32_t)(callbacks->repeat_confirmed_failing)));
      }
      else if (uVar4 == 0x1100) {
        if ((uintptr_t)(callbacks->leave_pending_failing)!=(uintptr_t)(f33_reset_vector)) {
          (*(int (*)())callbacks->leave_pending_failing)();
        }
        if ((uintptr_t)(callbacks->enter_passing)!=(uintptr_t)(f33_reset_vector)) {
          (*(int (*)())callbacks->enter_passing)();
        }
        pFVar9 = ((void *)camry_host_ptr((uint32_t)(callbacks->repeat_pending_passing)));
      }
      else {
        if (uVar4 != 0x2200) {
          if ((uintptr_t)(callbacks->repeat_pending_failing)!=(uintptr_t)(f33_reset_vector)) {
            (*(int (*)())callbacks->repeat_pending_failing)();
          }
          uVar5 = 0x11;
          goto LAB_0006b308;
        }
        if ((uintptr_t)(callbacks->leave_pending_failing)!=(uintptr_t)(f33_reset_vector)) {
          (*(int (*)())callbacks->leave_pending_failing)();
        }
        if ((uintptr_t)(callbacks->enter_passing)!=(uintptr_t)(f33_reset_vector)) {
          (*(int (*)())callbacks->enter_passing)();
        }
        if ((uintptr_t)(callbacks->confirm_passing)!=(uintptr_t)(f33_reset_vector)) {
          (*(int (*)())callbacks->confirm_passing)();
        }
        pFVar9 = ((void *)camry_host_ptr((uint32_t)(callbacks->repeat_confirmed_passing)));
      }
      if ((uintptr_t)(pFVar9)!=(uintptr_t)(f33_reset_vector)) {
        (*(int (*)())pFVar9)();
      }
    }
    goto LAB_0006b308;
  }
  if (sVar3 == 0x1100) {
    uVar5 = (*(int (*)())callbacks->classify_normal)();
    if (uVar5 == 0x11) {
      if ((uVar1 < uVar7) || (uVar7 = uVar7 + 1, uVar1 < uVar7)) {
        uVar5 = 0x2200;
      }
      else {
        uVar5 = 0x11001100;
      }
      uVar8 = 0;
    }
    else if (uVar5 == 0x22) {
      uVar7 = 0;
      if (uVar8 <= uVar2) {
        uVar8 = uVar8 + 1;
      }
      uVar1 = uVar8;
      if (uVar8 <= uVar6) {
        uVar1 = uVar6;
      }
      uVar6 = uVar1;
      uVar5 = 0x22;
      if (uVar8 <= uVar2) {
        uVar5 = 0x110011;
      }
    }
    else if ((uVar5 == 0x33) || (uVar5 == 0x44)) {
      uVar7 = 0;
      uVar8 = 0;
      uVar5 = 0;
    }
    else {
      uVar5 = 0xffff;
    }
    uVar4 = uVar5 & 0xffff;
    if (uVar4 == 0) {
      if ((uintptr_t)(callbacks->leave_pending_passing)!=(uintptr_t)(f33_reset_vector)) {
        (*(int (*)())callbacks->leave_pending_passing)();
      }
    }
    else {
      if (uVar4 == 0x11) {
        if ((uintptr_t)(callbacks->leave_pending_passing)!=(uintptr_t)(f33_reset_vector)) {
          (*(int (*)())callbacks->leave_pending_passing)();
        }
        if ((uintptr_t)(callbacks->enter_failing)!=(uintptr_t)(f33_reset_vector)) {
          (*(int (*)())callbacks->enter_failing)();
        }
        pFVar9 = ((void *)camry_host_ptr((uint32_t)(callbacks->repeat_pending_failing)));
      }
      else if (uVar4 == 0x22) {
        if ((uintptr_t)(callbacks->leave_pending_passing)!=(uintptr_t)(f33_reset_vector)) {
          (*(int (*)())callbacks->leave_pending_passing)();
        }
        if ((uintptr_t)(callbacks->enter_failing)!=(uintptr_t)(f33_reset_vector)) {
          (*(int (*)())callbacks->enter_failing)();
        }
        if ((uintptr_t)(callbacks->confirm_failing)!=(uintptr_t)(f33_reset_vector)) {
          (*(int (*)())callbacks->confirm_failing)();
        }
        pFVar9 = ((void *)camry_host_ptr((uint32_t)(callbacks->repeat_confirmed_failing)));
      }
      else if (uVar4 == 0x1100) {
        pFVar9 = ((void *)camry_host_ptr((uint32_t)(callbacks->repeat_pending_passing)));
      }
      else {
        if (uVar4 != 0x2200) {
          if ((uintptr_t)(callbacks->repeat_pending_passing)!=(uintptr_t)(f33_reset_vector)) {
            (*(int (*)())callbacks->repeat_pending_passing)();
          }
          uVar5 = 0x1100;
          goto LAB_0006b308;
        }
        if ((uintptr_t)(callbacks->confirm_passing)!=(uintptr_t)(f33_reset_vector)) {
          (*(int (*)())callbacks->confirm_passing)();
        }
        pFVar9 = ((void *)camry_host_ptr((uint32_t)(callbacks->repeat_confirmed_passing)));
      }
      if ((uintptr_t)(pFVar9)!=(uintptr_t)(f33_reset_vector)) {
        (*(int (*)())pFVar9)();
      }
    }
    goto LAB_0006b308;
  }
  if (sVar3 != 0x2200) {
    if ((uintptr_t)(callbacks->repeat_confirmed_failing)!=(uintptr_t)(f33_reset_vector)) {
      (*(int (*)())callbacks->repeat_confirmed_failing)();
    }
    uVar5 = 0x22;
    goto LAB_0006b308;
  }
  uVar5 = (*(int (*)())callbacks->classify_normal)();
  if (uVar5 == 0x11) {
LAB_0006af18:
    uVar8 = 0;
LAB_0006af1a:
    uVar5 = 0x2200;
  }
  else {
    if (uVar5 != 0x22) {
      if ((uVar5 == 0x33) || (uVar5 == 0x44)) goto LAB_0006af18;
      goto LAB_0006af1a;
    }
    uVar7 = 0;
    if (uVar8 <= uVar2) {
      uVar8 = uVar8 + 1;
    }
    uVar1 = uVar8;
    if (uVar8 <= uVar6) {
      uVar1 = uVar6;
    }
    uVar6 = uVar1;
    uVar5 = 0x22;
    if (uVar8 <= uVar2) {
      uVar5 = 0x110011;
    }
  }
  uVar4 = uVar5 & 0xffff;
  if (uVar4 == 0) {
    if ((uintptr_t)(callbacks->leave_confirmed_passing)!=(uintptr_t)(f33_reset_vector)) {
      (*(int (*)())callbacks->leave_confirmed_passing)();
    }
  }
  else {
    if (uVar4 == 0x11) {
      if ((uintptr_t)(callbacks->leave_confirmed_passing)!=(uintptr_t)(f33_reset_vector)) {
        (*(int (*)())callbacks->leave_confirmed_passing)();
      }
      if ((uintptr_t)(callbacks->enter_failing)!=(uintptr_t)(f33_reset_vector)) {
        (*(int (*)())callbacks->enter_failing)();
      }
      pFVar9 = ((void *)camry_host_ptr((uint32_t)(callbacks->repeat_pending_failing)));
    }
    else if (uVar4 == 0x22) {
      if ((uintptr_t)(callbacks->leave_confirmed_passing)!=(uintptr_t)(f33_reset_vector)) {
        (*(int (*)())callbacks->leave_confirmed_passing)();
      }
      if ((uintptr_t)(callbacks->enter_failing)!=(uintptr_t)(f33_reset_vector)) {
        (*(int (*)())callbacks->enter_failing)();
      }
      if ((uintptr_t)(callbacks->confirm_failing)!=(uintptr_t)(f33_reset_vector)) {
        (*(int (*)())callbacks->confirm_failing)();
      }
      pFVar9 = ((void *)camry_host_ptr((uint32_t)(callbacks->repeat_confirmed_failing)));
    }
    else {
      pFVar9 = ((void *)camry_host_ptr((uint32_t)(callbacks->repeat_confirmed_passing)));
      if (uVar4 != 0x2200) {
        if ((uintptr_t)(pFVar9)!=(uintptr_t)(f33_reset_vector)) {
          (*(int (*)())pFVar9)();
        }
        uVar5 = 0x2200;
        goto LAB_0006b308;
      }
    }
    if ((uintptr_t)(pFVar9)!=(uintptr_t)(f33_reset_vector)) {
      (*(int (*)())pFVar9)();
    }
  }
LAB_0006b308:
  state->packed_status = uVar5;
  state->passing_count = uVar7;
  state->failing_count = uVar8;
  state->failing_high_water = uVar6;
  return 0x11;
}



/* Fourteen-byte state and13-pointer callbacks. Pending failure counts failing classifications
   within a separately advancing window: healthy11 or ambiguous33 preserves accumulated failure
   count; invalid44 resets it. Window expiry wins before another failure can confirm. Both
   confirmation and expiry use strict > comparisons with16-bit increments. Exact acquisition config
   pass2/windowFFFF,fail3/window6. Confirmed failure latches; packed status stored and full R10=11
   returned. Native acquisition scheduler compositions confirm at failure-window6 but expire at7
   before another failing classification can confirm. Failure high-water and record padding survive.
    */

uint f33_step_windowed_monitor
               (F33WindowedMonitorState *state,F33WindowedMonitorLimits *limits,
               F33TwoSidedMonitorCallbacks *callbacks)

{
  ushort uVar1;
  ushort uVar2;
  ushort uVar3;
  ushort uVar4;
  short sVar5;
  uint uVar6;
  uint uVar7;
  ushort uVar8;
  ushort uVar9;
  ushort uVar10;
  ushort uVar11;
  ushort uVar12;
  F33MonitorAction *pFVar13;
  
  uVar10 = state->passing_count;
  uVar9 = state->passing_window;
  uVar12 = state->failing_count;
  uVar11 = state->failing_window;
  uVar8 = state->failing_high_water;
  uVar1 = limits->passing_window_limit;
  uVar2 = limits->passing_limit;
  uVar3 = limits->failing_limit;
  uVar4 = limits->failing_window_limit;
  if (uVar12 == 0) {
    if (uVar2 < uVar10) {
      sVar5 = 0x2200;
    }
    else {
      sVar5 = 0;
      if (uVar10 != 0) {
        sVar5 = 0x1100;
      }
    }
  }
  else {
    sVar5 = 0x22;
    if (uVar12 <= uVar3) {
      sVar5 = 0x11;
    }
  }
  if (sVar5 == 0) {
    uVar7 = (*(int (*)())callbacks->classify_normal)();
    if (uVar7 == 0x11) {
      if ((uVar1 < uVar9) || (uVar9 = uVar9 + 1, uVar1 < uVar9)) {
        uVar10 = 0;
        uVar9 = 0;
        uVar7 = 0;
      }
      else if ((uVar2 < uVar10) || (uVar10 = uVar10 + 1, uVar2 < uVar10)) {
        uVar7 = 0x2200;
      }
      else {
        uVar7 = 0x11001100;
      }
      uVar12 = 0;
      uVar11 = 0;
    }
    else if (uVar7 == 0x22) {
      uVar10 = 0;
      uVar9 = 0;
      if ((uVar4 < uVar11) || (uVar11 = uVar11 + 1, uVar4 < uVar11)) goto LAB_0006b648;
      if (uVar12 <= uVar3) {
        uVar12 = uVar12 + 1;
      }
      uVar1 = uVar12;
      if (uVar12 <= uVar8) {
        uVar1 = uVar8;
      }
      uVar8 = uVar1;
      uVar7 = 0x22;
      if (uVar12 <= uVar3) {
        uVar7 = 0x110011;
      }
    }
    else if ((uVar7 == 0x33) || (uVar7 == 0x44)) {
LAB_0006b648:
      uVar10 = 0;
      uVar9 = 0;
      uVar11 = 0;
      uVar7 = 0;
      uVar12 = uVar9;
    }
    else {
      uVar7 = 0;
    }
    uVar6 = uVar7 & 0xffff;
    if (uVar6 != 0) {
      if (uVar6 == 0x11) {
        if ((uintptr_t)(callbacks->enter_failing)!=(uintptr_t)(f33_reset_vector)) {
          (*(int (*)())callbacks->enter_failing)();
        }
        pFVar13 = ((void *)camry_host_ptr((uint32_t)(callbacks->repeat_pending_failing)));
      }
      else if (uVar6 == 0x22) {
        if ((uintptr_t)(callbacks->enter_failing)!=(uintptr_t)(f33_reset_vector)) {
          (*(int (*)())callbacks->enter_failing)();
        }
        if ((uintptr_t)(callbacks->confirm_failing)!=(uintptr_t)(f33_reset_vector)) {
          (*(int (*)())callbacks->confirm_failing)();
        }
        pFVar13 = ((void *)camry_host_ptr((uint32_t)(callbacks->repeat_confirmed_failing)));
      }
      else if (uVar6 == 0x1100) {
        if ((uintptr_t)(callbacks->enter_passing)!=(uintptr_t)(f33_reset_vector)) {
          (*(int (*)())callbacks->enter_passing)();
        }
        pFVar13 = ((void *)camry_host_ptr((uint32_t)(callbacks->repeat_pending_passing)));
      }
      else {
        if (uVar6 != 0x2200) {
          uVar7 = 0;
          goto LAB_0006b7bc;
        }
        if ((uintptr_t)(callbacks->enter_passing)!=(uintptr_t)(f33_reset_vector)) {
          (*(int (*)())callbacks->enter_passing)();
        }
        if ((uintptr_t)(callbacks->confirm_passing)!=(uintptr_t)(f33_reset_vector)) {
          (*(int (*)())callbacks->confirm_passing)();
        }
        pFVar13 = ((void *)camry_host_ptr((uint32_t)(callbacks->repeat_confirmed_passing)));
      }
      if ((uintptr_t)(pFVar13)!=(uintptr_t)(f33_reset_vector)) {
        (*(int (*)())pFVar13)();
      }
    }
    goto LAB_0006b7bc;
  }
  if (sVar5 == 0x11) {
    uVar7 = (*(int (*)())callbacks->classify_failing)();
    if ((uVar4 < uVar11) || (uVar11 = uVar11 + 1, uVar4 < uVar11)) {
LAB_0006b744:
      uVar10 = 0;
      uVar9 = 0;
      uVar12 = 0;
      uVar11 = 0;
      uVar7 = 0;
    }
    else {
      if (uVar7 == 0x11) {
LAB_0006b73e:
        uVar10 = 0;
        uVar9 = uVar10;
      }
      else {
        if (uVar7 == 0x22) {
          uVar10 = 0;
          uVar9 = 0;
          if (uVar12 <= uVar3) {
            uVar12 = uVar12 + 1;
          }
          uVar1 = uVar12;
          if (uVar12 <= uVar8) {
            uVar1 = uVar8;
          }
          uVar8 = uVar1;
          uVar7 = 0x22;
          if (uVar12 <= uVar3) {
            uVar7 = 0x110011;
          }
          goto LAB_0006b74e;
        }
        if (uVar7 == 0x33) goto LAB_0006b73e;
        if (uVar7 == 0x44) goto LAB_0006b744;
      }
      uVar7 = 0x11;
    }
LAB_0006b74e:
    uVar6 = uVar7 & 0xffff;
    if (uVar6 == 0) {
      if ((uintptr_t)(callbacks->leave_pending_failing)!=(uintptr_t)(f33_reset_vector)) {
        (*(int (*)())callbacks->leave_pending_failing)();
      }
    }
    else {
      if (uVar6 == 0x11) {
        pFVar13 = ((void *)camry_host_ptr((uint32_t)(callbacks->repeat_pending_failing)));
      }
      else {
        if (uVar6 != 0x22) {
          if ((uintptr_t)(callbacks->repeat_pending_failing)!=(uintptr_t)(f33_reset_vector)) {
            (*(int (*)())callbacks->repeat_pending_failing)();
          }
          uVar7 = 0x11;
          goto LAB_0006b7bc;
        }
        if ((uintptr_t)(callbacks->confirm_failing)!=(uintptr_t)(f33_reset_vector)) {
          (*(int (*)())callbacks->confirm_failing)();
        }
        pFVar13 = ((void *)camry_host_ptr((uint32_t)(callbacks->repeat_confirmed_failing)));
      }
      if ((uintptr_t)(pFVar13)!=(uintptr_t)(f33_reset_vector)) {
        (*(int (*)())pFVar13)();
      }
    }
    goto LAB_0006b7bc;
  }
  if (sVar5 == 0x1100) {
    uVar7 = (*(int (*)())callbacks->classify_normal)();
    if ((uVar1 < uVar9) || (uVar9 = uVar9 + 1, uVar1 < uVar9)) {
LAB_0006b502:
      uVar10 = 0;
      uVar9 = 0;
      uVar11 = 0;
      uVar7 = 0;
      uVar12 = uVar9;
    }
    else if (uVar7 == 0x11) {
      if ((uVar2 < uVar10) || (uVar10 = uVar10 + 1, uVar2 < uVar10)) {
        uVar7 = 0x2200;
      }
      else {
        uVar7 = 0x11001100;
      }
      uVar12 = 0;
      uVar11 = 0;
    }
    else if (uVar7 == 0x22) {
      uVar10 = 0;
      uVar9 = 0;
      if ((uVar4 < uVar11) || (uVar11 = uVar11 + 1, uVar4 < uVar11)) goto LAB_0006b502;
      if (uVar12 <= uVar3) {
        uVar12 = uVar12 + 1;
      }
      uVar1 = uVar12;
      if (uVar12 <= uVar8) {
        uVar1 = uVar8;
      }
      uVar8 = uVar1;
      uVar7 = 0x22;
      if (uVar12 <= uVar3) {
        uVar7 = 0x110011;
      }
    }
    else {
      if (uVar7 == 0x33) {
        uVar12 = 0;
        uVar11 = uVar12;
      }
      else if (uVar7 == 0x44) goto LAB_0006b502;
      uVar7 = 0x1100;
    }
    uVar6 = uVar7 & 0xffff;
    if (uVar6 == 0) {
      if ((uintptr_t)(callbacks->leave_pending_passing)!=(uintptr_t)(f33_reset_vector)) {
        (*(int (*)())callbacks->leave_pending_passing)();
      }
    }
    else {
      if (uVar6 == 0x11) {
        if ((uintptr_t)(callbacks->leave_pending_passing)!=(uintptr_t)(f33_reset_vector)) {
          (*(int (*)())callbacks->leave_pending_passing)();
        }
        if ((uintptr_t)(callbacks->enter_failing)!=(uintptr_t)(f33_reset_vector)) {
          (*(int (*)())callbacks->enter_failing)();
        }
        pFVar13 = ((void *)camry_host_ptr((uint32_t)(callbacks->repeat_pending_failing)));
      }
      else if (uVar6 == 0x22) {
        if ((uintptr_t)(callbacks->leave_pending_passing)!=(uintptr_t)(f33_reset_vector)) {
          (*(int (*)())callbacks->leave_pending_passing)();
        }
        if ((uintptr_t)(callbacks->enter_failing)!=(uintptr_t)(f33_reset_vector)) {
          (*(int (*)())callbacks->enter_failing)();
        }
        if ((uintptr_t)(callbacks->confirm_failing)!=(uintptr_t)(f33_reset_vector)) {
          (*(int (*)())callbacks->confirm_failing)();
        }
        pFVar13 = ((void *)camry_host_ptr((uint32_t)(callbacks->repeat_confirmed_failing)));
      }
      else if (uVar6 == 0x1100) {
        pFVar13 = ((void *)camry_host_ptr((uint32_t)(callbacks->repeat_pending_passing)));
      }
      else {
        if (uVar6 != 0x2200) {
          if ((uintptr_t)(callbacks->repeat_pending_passing)!=(uintptr_t)(f33_reset_vector)) {
            (*(int (*)())callbacks->repeat_pending_passing)();
          }
          uVar7 = 0x1100;
          goto LAB_0006b7bc;
        }
        if ((uintptr_t)(callbacks->confirm_passing)!=(uintptr_t)(f33_reset_vector)) {
          (*(int (*)())callbacks->confirm_passing)();
        }
        pFVar13 = ((void *)camry_host_ptr((uint32_t)(callbacks->repeat_confirmed_passing)));
      }
      if ((uintptr_t)(pFVar13)!=(uintptr_t)(f33_reset_vector)) {
        (*(int (*)())pFVar13)();
      }
    }
    goto LAB_0006b7bc;
  }
  if (sVar5 != 0x2200) {
    if ((uintptr_t)(callbacks->repeat_confirmed_failing)!=(uintptr_t)(f33_reset_vector)) {
      (*(int (*)())callbacks->repeat_confirmed_failing)();
    }
    uVar7 = 0x22;
    goto LAB_0006b7bc;
  }
  uVar7 = (*(int (*)())callbacks->classify_normal)();
  if (uVar7 == 0x11) {
LAB_0006b3d6:
    uVar12 = 0;
    uVar11 = 0;
LAB_0006b3da:
    uVar7 = 0x2200;
  }
  else {
    if (uVar7 != 0x22) {
      if ((uVar7 == 0x33) || (uVar7 == 0x44)) goto LAB_0006b3d6;
      goto LAB_0006b3da;
    }
    uVar10 = 0;
    uVar9 = 0;
    if ((uVar4 < uVar11) || (uVar11 = uVar11 + 1, uVar4 < uVar11)) {
      uVar12 = 0;
      uVar11 = 0;
      uVar7 = 0;
    }
    else {
      if (uVar12 <= uVar3) {
        uVar12 = uVar12 + 1;
      }
      uVar1 = uVar12;
      if (uVar12 <= uVar8) {
        uVar1 = uVar8;
      }
      uVar8 = uVar1;
      uVar7 = 0x22;
      if (uVar12 <= uVar3) {
        uVar7 = 0x110011;
      }
    }
  }
  uVar6 = uVar7 & 0xffff;
  if (uVar6 == 0) {
    if ((uintptr_t)(callbacks->leave_confirmed_passing)!=(uintptr_t)(f33_reset_vector)) {
      (*(int (*)())callbacks->leave_confirmed_passing)();
    }
  }
  else {
    if (uVar6 == 0x11) {
      if ((uintptr_t)(callbacks->leave_confirmed_passing)!=(uintptr_t)(f33_reset_vector)) {
        (*(int (*)())callbacks->leave_confirmed_passing)();
      }
      if ((uintptr_t)(callbacks->enter_failing)!=(uintptr_t)(f33_reset_vector)) {
        (*(int (*)())callbacks->enter_failing)();
      }
      pFVar13 = ((void *)camry_host_ptr((uint32_t)(callbacks->repeat_pending_failing)));
    }
    else if (uVar6 == 0x22) {
      if ((uintptr_t)(callbacks->leave_confirmed_passing)!=(uintptr_t)(f33_reset_vector)) {
        (*(int (*)())callbacks->leave_confirmed_passing)();
      }
      if ((uintptr_t)(callbacks->enter_failing)!=(uintptr_t)(f33_reset_vector)) {
        (*(int (*)())callbacks->enter_failing)();
      }
      if ((uintptr_t)(callbacks->confirm_failing)!=(uintptr_t)(f33_reset_vector)) {
        (*(int (*)())callbacks->confirm_failing)();
      }
      pFVar13 = ((void *)camry_host_ptr((uint32_t)(callbacks->repeat_confirmed_failing)));
    }
    else {
      pFVar13 = ((void *)camry_host_ptr((uint32_t)(callbacks->repeat_confirmed_passing)));
      if (uVar6 != 0x2200) {
        if ((uintptr_t)(pFVar13)!=(uintptr_t)(f33_reset_vector)) {
          (*(int (*)())pFVar13)();
        }
        uVar7 = 0x2200;
        goto LAB_0006b7bc;
      }
    }
    if ((uintptr_t)(pFVar13)!=(uintptr_t)(f33_reset_vector)) {
      (*(int (*)())pFVar13)();
    }
  }
LAB_0006b7bc:
  state->packed_status = uVar7;
  state->passing_count = uVar10;
  state->passing_window = uVar9;
  state->failing_count = uVar12;
  state->failing_window = uVar11;
  state->failing_high_water = uVar8;
  return 0x11;
}



void FUN_0006b7d2(undefined1 *param_1)

{
  *param_1 = 0;
  *(undefined2 *)(param_1 + 2) = 0;
  *(undefined2 *)(param_1 + 4) = 0;
  *(undefined2 *)(param_1 + 6) = 0;
  return;
}



undefined1 FUN_0006b7f0(char *param_1,ushort *param_2,undefined4 *param_3)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  ushort uVar6;
  uint uVar7;
  char cVar8;
  code *pcVar9;
  ushort uVar10;
  uint uVar11;
  ushort uVar12;
  uint uVar13;
  undefined1 uStack_31;
  
  cVar8 = *param_1;
  uVar10 = *(ushort *)(param_1 + 6);
  uVar11 = (uint)uVar10;
  uVar12 = *(ushort *)(param_1 + 2);
  uVar13 = (uint)uVar12;
  uVar6 = *(ushort *)(param_1 + 4);
  uVar7 = (uint)uVar6;
  uStack_31 = 0x11;
  uVar5 = (uint)param_2[2];
  uVar3 = (uint)param_2[3];
  uVar4 = (uint)*param_2;
  uVar2 = (uint)param_2[1];
  iVar1 = (*(int (*)())*param_3)();
  if (cVar8 == '\0') {
    if (iVar1 != 0x22) {
      if ((iVar1 == 0x11) || (iVar1 == 0x44)) {
        uVar12 = 0;
      }
      goto LAB_0006b978;
    }
    if ((int)(uVar13 - uVar4) < 0 || uVar13 == uVar4) {
      uVar13 = uVar13 + 1;
    }
    uVar2 = uVar13;
    if (-1 < (int)(uVar7 - uVar13)) {
      uVar2 = uVar7;
    }
    uVar6 = (ushort)uVar2;
    cVar8 = '\x11';
    if ((uintptr_t)((code *)param_3[1])!=(uintptr_t)(f33_reset_vector)) {
      (*(int (*)())param_3[1])();
    }
LAB_0006b8cc:
    uVar12 = (ushort)uVar13;
    uVar10 = (ushort)uVar11;
    pcVar9 = (code *)param_3[7];
  }
  else {
    if (cVar8 == '\x11') {
      if (iVar1 == 0x11) {
        if ((-1 < (int)(uVar11 - uVar5) && uVar11 != uVar5) ||
           (uVar11 = uVar11 + 1, -1 < (int)(uVar11 - uVar5) && uVar11 != uVar5)) {
          pcVar9 = (code *)param_3[2];
          uVar10 = 0;
          uVar12 = 0;
          cVar8 = '\0';
          goto joined_r0x0006b8d2;
        }
      }
      else if (iVar1 == 0x22) {
        uVar11 = 0;
        if ((int)(uVar13 - uVar4) < 0 || uVar13 == uVar4) {
          uVar13 = uVar13 + 1;
        }
        uVar2 = uVar13;
        if (-1 < (int)(uVar7 - uVar13)) {
          uVar2 = uVar7;
        }
        uVar6 = (ushort)uVar2;
        if (-1 < (int)(uVar13 - uVar4) && uVar13 != uVar4) {
          if ((uintptr_t)((code *)param_3[3])!=(uintptr_t)(f33_reset_vector)) {
            (*(int (*)())param_3[3])();
          }
          goto LAB_0006b92c;
        }
      }
      else if (iVar1 == 0x44) {
        uVar11 = 0;
        uVar13 = 0;
      }
      goto LAB_0006b8cc;
    }
    if (cVar8 == '\"') {
      if (iVar1 == 0x11) {
        if ((-1 < (int)(uVar11 - uVar5) && uVar11 != uVar5) ||
           (uVar11 = uVar11 + 1, -1 < (int)(uVar11 - uVar5) && uVar11 != uVar5)) {
          pcVar9 = (code *)param_3[4];
          uVar10 = 0;
          uVar12 = 0;
          cVar8 = '\0';
          goto joined_r0x0006b8d2;
        }
      }
      else if (iVar1 == 0x22) {
        uVar11 = 0;
        if ((int)(uVar13 - uVar2) < 0 || uVar13 == uVar2) {
          uVar13 = uVar13 + 1;
        }
        uVar3 = uVar13;
        if (-1 < (int)(uVar7 - uVar13)) {
          uVar3 = uVar7;
        }
        uVar6 = (ushort)uVar3;
        if (-1 < (int)(uVar13 - uVar2) && uVar13 != uVar2) {
          cVar8 = 'D';
          if ((uintptr_t)((code *)param_3[5])!=(uintptr_t)(f33_reset_vector)) {
            (*(int (*)())param_3[5])();
          }
          goto LAB_0006b96c;
        }
      }
      else if (iVar1 == 0x44) {
        uVar11 = 0;
        uVar13 = 0;
      }
LAB_0006b92c:
      uVar12 = (ushort)uVar13;
      cVar8 = '\"';
      uVar10 = (ushort)uVar11;
      pcVar9 = (code *)param_3[8];
    }
    else {
      if (cVar8 != 'D') {
        uStack_31 = 0x33;
        goto LAB_0006b978;
      }
      if (iVar1 == 0x11) {
        if ((-1 < (int)(uVar11 - uVar3) && uVar11 != uVar3) ||
           (uVar11 = uVar11 + 1, -1 < (int)(uVar11 - uVar3) && uVar11 != uVar3)) {
          pcVar9 = (code *)param_3[6];
          uVar10 = 0;
          uVar12 = 0;
          cVar8 = '\0';
          goto joined_r0x0006b8d2;
        }
      }
      else if (iVar1 == 0x22) {
        uVar11 = 0;
      }
      else if (iVar1 == 0x44) {
        uVar11 = 0;
        uVar13 = 0;
      }
LAB_0006b96c:
      uVar12 = (ushort)uVar13;
      uVar10 = (ushort)uVar11;
      pcVar9 = (code *)param_3[9];
    }
  }
joined_r0x0006b8d2:
  if ((uintptr_t)(pcVar9)!=(uintptr_t)(f33_reset_vector)) {
    (*(int (*)())pcVar9)();
  }
LAB_0006b978:
  *(ushort *)(param_1 + 4) = uVar6;
  *(ushort *)(param_1 + 2) = uVar12;
  *(ushort *)(param_1 + 6) = uVar10;
  *param_1 = cVar8;
  return uStack_31;
}



void FUN_0006b98a(undefined4 *param_1)

{
  *param_1 = 0;
  *(undefined2 *)(param_1 + 1) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 6)))) = 0;
  *(undefined2 *)(param_1 + 2) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 10)))) = 0;
  *(undefined2 *)(param_1 + 3) = 0;
  return;
}



/* Reclassify from counters; retain confirmed22/escalated44 and confirmed pass2200, discard pending
   paths. Failure high-water survives. Disabled escalating monitor reclassifies from counters,
   retaining confirmed22/escalated44/confirmed-pass2200 while clearing pending state; high-water
   survives. */

void f33_retain_disabled_escalating_monitor(F33EscalatingMonitorState *state,ushort *calibration)

{
  uint uVar1;
  
  if ((uintptr_t)(calibration[7])<(uintptr_t)(state->elapsed_count)) {
    uVar1 = 0x44;
  }
  else if ((state->elapsed_count == 0) && ((uintptr_t)(state->failing_count)<=(uintptr_t)(calibration[5]))) {
    if ((state->failing_count == 0) && ((uintptr_t)(calibration[2])<(uintptr_t)(state->passing_count))) {
      uVar1 = 0x2200;
    }
    else {
      state->passing_count = 0;
      uVar1 = 0;
    }
    state->failing_count = 0;
    state->recovery_count = 0;
    state->elapsed_count = 0;
  }
  else {
    uVar1 = 0x22;
  }
  state->packed_status = uVar1;
  return;
}



/* Fourteen-byte retained state, eight-u16 calibration and17-slot callback vector. Saturating
   counters, strict confirmation thresholds, recovery/elapsed escalation. Packed result is written
   to state, NOT returned: normal API return is11. Fourteen-byte escalating monitor state,
   eight-halfword calibration,17 callbacks; strict thresholds, saturated counts and retained
   recovery/escalation. Packed result is stored; API returns11. */

uint f33_step_escalating_monitor
               (F33EscalatingMonitorState *state,ushort *calibration,uint *callbacks)

{
  int iVar1;
  ushort uVar2;
  ushort uVar3;
  int iVar4;
  undefined4 uVar5;
  uint uVar6;
  uint uVar7;
  uint uVar8;
  uint uVar9;
  code *pcVar10;
  ushort local_3c;
  ushort uStack_3a;
  ushort auStack_36 [2];
  ushort uStack_32;
  ushort uStack_30;
  ushort uStack_2c;
  ushort uStack_26;
  
  uStack_30 = state->failing_high_water;
  auStack_36[0] = state->passing_count;
  uStack_32 = state->failing_count;
  uStack_26 = state->elapsed_count;
  uStack_2c = state->recovery_count;
  local_3c = calibration[6];
  uVar7 = (uint)*calibration;
  uVar2 = calibration[1];
  uVar6 = (uint)calibration[2];
  uStack_3a = calibration[7];
  uVar9 = (uint)calibration[3];
  uVar3 = calibration[4];
  uVar8 = (uint)calibration[5];
  if (uStack_32 == 0) {
    if (uVar6 < auStack_36[0]) {
      iVar4 = 0x2200;
    }
    else {
      iVar4 = 0;
      if (auStack_36[0] != 0) {
        iVar4 = 0x1100;
      }
    }
  }
  else if (uVar8 < uStack_32) {
    iVar4 = 0x44;
    if (uStack_26 <= uStack_3a) {
      iVar4 = 0x22;
    }
  }
  else {
    iVar4 = 0x11;
  }
  if (iVar4 == 0) {
    iVar4 = (*(int (*)())*callbacks)();
    if (iVar4 == 0x11) {
      iVar1 = 0xffff - uVar7;
      iVar4 = (uint)auStack_36[0] - iVar1;
      if (iVar4 < 0 == (iVar1 < 0 && iVar1 < 0 == iVar4 < 0)) {
        uVar8 = 0xffff;
      }
      else {
        uVar8 = auStack_36[0] + uVar7 & 0xffff;
      }
      auStack_36[0] = (ushort)uVar8;
      uVar7 = 0x2200;
      if (uVar8 <= uVar6) {
        uVar7 = 0x11001100;
      }
      uStack_32 = 0;
    }
    else if (iVar4 == 0x22) {
      auStack_36[0] = 0;
      iVar1 = 0xffff - uVar9;
      iVar4 = (uint)uStack_32 - iVar1;
      if (iVar4 < 0 == (iVar1 < 0 && iVar1 < 0 == iVar4 < 0)) {
        uVar6 = 0xffff;
      }
      else {
        uVar6 = uStack_32 + uVar9 & 0xffff;
      }
      uStack_32 = (ushort)uVar6;
      if (uStack_30 < uVar6) {
        uStack_30 = uStack_32;
      }
      uVar7 = 0x22;
      if (uVar6 <= uVar8) {
        uVar7 = 0x110011;
      }
    }
    else if ((iVar4 == 0x33) || (iVar4 == 0x44)) {
      uStack_32 = 0;
      auStack_36[0] = 0;
      uVar7 = 0;
    }
    else {
      uVar7 = 0;
    }
    uVar6 = uVar7 & 0xffff;
    if (uVar6 != 0) {
      if (uVar6 == 0x11) {
        if ((uintptr_t)((code *)callbacks[7])!=(uintptr_t)(f33_reset_vector)) {
          (*(int (*)())callbacks[7])();
        }
        pcVar10 = (code *)callbacks[0xe];
      }
      else if (uVar6 == 0x22) {
        if ((uintptr_t)((code *)callbacks[7])!=(uintptr_t)(f33_reset_vector)) {
          (*(int (*)())callbacks[7])();
        }
        if ((uintptr_t)((code *)callbacks[9])!=(uintptr_t)(f33_reset_vector)) {
          (*(int (*)())callbacks[9])();
        }
        pcVar10 = (code *)callbacks[0xf];
      }
      else if (uVar6 == 0x1100) {
        if ((uintptr_t)((code *)callbacks[3])!=(uintptr_t)(f33_reset_vector)) {
          (*(int (*)())callbacks[3])();
        }
        pcVar10 = (code *)callbacks[0xc];
      }
      else {
        if (uVar6 != 0x2200) {
          uVar7 = 0;
          goto LAB_0006c32e;
        }
        if ((uintptr_t)((code *)callbacks[3])!=(uintptr_t)(f33_reset_vector)) {
          (*(int (*)())callbacks[3])();
        }
        if ((uintptr_t)((code *)callbacks[5])!=(uintptr_t)(f33_reset_vector)) {
          (*(int (*)())callbacks[5])();
        }
        pcVar10 = (code *)callbacks[0xd];
      }
      if ((uintptr_t)(pcVar10)!=(uintptr_t)(f33_reset_vector)) {
        (*(int (*)())pcVar10)();
      }
    }
    goto LAB_0006c32e;
  }
  if (iVar4 == 0x11) {
    iVar4 = (*(int (*)())callbacks[1])();
    if (iVar4 == 0x11) {
LAB_0006c238:
      auStack_36[0] = 0;
      if (uVar3 < uStack_32) {
        uStack_32 = uStack_32 - uVar3;
LAB_0006c1fc:
        uVar7 = 0x11;
      }
      else {
LAB_0006c252:
        auStack_36[0] = 0;
        uVar7 = 0;
        uStack_32 = 0;
      }
    }
    else {
      if (iVar4 != 0x22) {
        if (iVar4 == 0x33) goto LAB_0006c238;
        if (iVar4 == 0x44) goto LAB_0006c252;
        goto LAB_0006c1fc;
      }
      auStack_36[0] = 0;
      iVar1 = 0xffff - uVar9;
      iVar4 = (uint)uStack_32 - iVar1;
      if (iVar4 < 0 == (iVar1 < 0 && iVar1 < 0 == iVar4 < 0)) {
        uVar6 = 0xffff;
      }
      else {
        uVar6 = uStack_32 + uVar9 & 0xffff;
      }
      uStack_32 = (ushort)uVar6;
      if (uStack_30 < uVar6) {
        uStack_30 = uStack_32;
      }
      uVar7 = 0x22;
      if (uVar6 <= uVar8) {
        uVar7 = 0x110011;
      }
    }
    uVar6 = uVar7 & 0xffff;
    if (uVar6 == 0) {
      if ((uintptr_t)((code *)callbacks[8])!=(uintptr_t)(f33_reset_vector)) {
        (*(int (*)())callbacks[8])();
      }
    }
    else {
      if (uVar6 == 0x11) {
        pcVar10 = (code *)callbacks[0xe];
      }
      else {
        if (uVar6 != 0x22) {
          if ((uintptr_t)((code *)callbacks[0xe])!=(uintptr_t)(f33_reset_vector)) {
            (*(int (*)())callbacks[0xe])();
          }
          uVar7 = 0x11;
          goto LAB_0006c32e;
        }
        if ((uintptr_t)((code *)callbacks[9])!=(uintptr_t)(f33_reset_vector)) {
          (*(int (*)())callbacks[9])();
        }
        pcVar10 = (code *)callbacks[0xf];
      }
      if ((uintptr_t)(pcVar10)!=(uintptr_t)(f33_reset_vector)) {
        (*(int (*)())pcVar10)();
      }
    }
    goto LAB_0006c32e;
  }
  if (iVar4 == 0x22) {
    uVar5 = (*(int (*)())callbacks[2])();
    uVar7 = FUN_00070fa4(uVar5,auStack_36,&local_3c);
    uVar6 = uVar7 & 0xffff;
    if (uVar6 == 0) {
      pcVar10 = (code *)callbacks[10];
    }
    else if (uVar6 == 0x22) {
      pcVar10 = (code *)callbacks[0xf];
    }
    else {
      if (uVar6 != 0x44) {
        if ((uintptr_t)((code *)callbacks[0xf])!=(uintptr_t)(f33_reset_vector)) {
          (*(int (*)())callbacks[0xf])();
        }
        uVar7 = 0x22;
        goto LAB_0006c32e;
      }
      if ((uintptr_t)((code *)callbacks[0xb])!=(uintptr_t)(f33_reset_vector)) {
        (*(int (*)())callbacks[0xb])();
      }
      pcVar10 = (code *)callbacks[0x10];
    }
    if ((uintptr_t)(pcVar10)!=(uintptr_t)(f33_reset_vector)) {
      (*(int (*)())pcVar10)();
    }
    goto LAB_0006c32e;
  }
  if (iVar4 == 0x1100) {
    iVar4 = (*(int (*)())*callbacks)();
    if (iVar4 == 0x11) {
      iVar1 = 0xffff - uVar7;
      iVar4 = (uint)auStack_36[0] - iVar1;
      if (iVar4 < 0 == (iVar1 < 0 && iVar1 < 0 == iVar4 < 0)) {
        uVar8 = 0xffff;
      }
      else {
        uVar8 = auStack_36[0] + uVar7 & 0xffff;
      }
      auStack_36[0] = (ushort)uVar8;
      uVar7 = 0x2200;
      if (uVar8 <= uVar6) {
        uVar7 = 0x11001100;
      }
LAB_0006bfe6:
      uStack_32 = 0;
    }
    else if (iVar4 == 0x22) {
      auStack_36[0] = 0;
      iVar1 = 0xffff - uVar9;
      iVar4 = (uint)uStack_32 - iVar1;
      if (iVar4 < 0 == (iVar1 < 0 && iVar1 < 0 == iVar4 < 0)) {
        uVar6 = 0xffff;
      }
      else {
        uVar6 = uStack_32 + uVar9 & 0xffff;
      }
      uStack_32 = (ushort)uVar6;
      if (uStack_30 < uVar6) {
        uStack_30 = uStack_32;
      }
      uVar7 = 0x22;
      if (uVar6 <= uVar8) {
        uVar7 = 0x110011;
      }
    }
    else {
      if (iVar4 == 0x33) {
        if (uVar2 < auStack_36[0]) {
          auStack_36[0] = auStack_36[0] - uVar2;
          uVar7 = 0x1100;
        }
        else {
          auStack_36[0] = 0;
          uVar7 = 0;
        }
        goto LAB_0006bfe6;
      }
      if (iVar4 == 0x44) {
        uStack_32 = 0;
        auStack_36[0] = 0;
        uVar7 = 0;
      }
      else {
        uVar7 = 0x1100;
      }
    }
    uVar6 = uVar7 & 0xffff;
    if (uVar6 == 0) {
      if ((uintptr_t)((code *)callbacks[4])!=(uintptr_t)(f33_reset_vector)) {
        (*(int (*)())callbacks[4])();
      }
    }
    else {
      if (uVar6 == 0x11) {
        if ((uintptr_t)((code *)callbacks[4])!=(uintptr_t)(f33_reset_vector)) {
          (*(int (*)())callbacks[4])();
        }
        if ((uintptr_t)((code *)callbacks[7])!=(uintptr_t)(f33_reset_vector)) {
          (*(int (*)())callbacks[7])();
        }
        pcVar10 = (code *)callbacks[0xe];
      }
      else if (uVar6 == 0x22) {
        if ((uintptr_t)((code *)callbacks[4])!=(uintptr_t)(f33_reset_vector)) {
          (*(int (*)())callbacks[4])();
        }
        if ((uintptr_t)((code *)callbacks[7])!=(uintptr_t)(f33_reset_vector)) {
          (*(int (*)())callbacks[7])();
        }
        if ((uintptr_t)((code *)callbacks[9])!=(uintptr_t)(f33_reset_vector)) {
          (*(int (*)())callbacks[9])();
        }
        pcVar10 = (code *)callbacks[0xf];
      }
      else if (uVar6 == 0x1100) {
        pcVar10 = (code *)callbacks[0xc];
      }
      else {
        if (uVar6 != 0x2200) {
          if ((uintptr_t)((code *)callbacks[0xc])!=(uintptr_t)(f33_reset_vector)) {
            (*(int (*)())callbacks[0xc])();
          }
          uVar7 = 0x1100;
          goto LAB_0006c32e;
        }
        if ((uintptr_t)((code *)callbacks[5])!=(uintptr_t)(f33_reset_vector)) {
          (*(int (*)())callbacks[5])();
        }
        pcVar10 = (code *)callbacks[0xd];
      }
      if ((uintptr_t)(pcVar10)!=(uintptr_t)(f33_reset_vector)) {
        (*(int (*)())pcVar10)();
      }
    }
    goto LAB_0006c32e;
  }
  if (iVar4 != 0x2200) {
    if ((uintptr_t)((code *)callbacks[0x10])!=(uintptr_t)(f33_reset_vector)) {
      (*(int (*)())callbacks[0x10])();
    }
    uVar7 = 0x44;
    goto LAB_0006c32e;
  }
  iVar4 = (*(int (*)())*callbacks)();
  if (iVar4 == 0x11) {
LAB_0006bea2:
    uStack_32 = 0;
LAB_0006bea6:
    uVar7 = 0x2200;
  }
  else {
    if (iVar4 != 0x22) {
      if ((iVar4 == 0x33) || (iVar4 == 0x44)) goto LAB_0006bea2;
      goto LAB_0006bea6;
    }
    auStack_36[0] = 0;
    iVar1 = 0xffff - uVar9;
    iVar4 = (uint)uStack_32 - iVar1;
    if (iVar4 < 0 == (iVar1 < 0 && iVar1 < 0 == iVar4 < 0)) {
      uVar6 = 0xffff;
    }
    else {
      uVar6 = uStack_32 + uVar9 & 0xffff;
    }
    uStack_32 = (ushort)uVar6;
    if (uStack_30 < uVar6) {
      uStack_30 = uStack_32;
    }
    uVar7 = 0x22;
    if (uVar6 <= uVar8) {
      uVar7 = 0x110011;
    }
  }
  uVar6 = uVar7 & 0xffff;
  if (uVar6 == 0) {
    if ((uintptr_t)((code *)callbacks[6])!=(uintptr_t)(f33_reset_vector)) {
      (*(int (*)())callbacks[6])();
    }
  }
  else {
    if (uVar6 == 0x11) {
      if ((uintptr_t)((code *)callbacks[6])!=(uintptr_t)(f33_reset_vector)) {
        (*(int (*)())callbacks[6])();
      }
      if ((uintptr_t)((code *)callbacks[7])!=(uintptr_t)(f33_reset_vector)) {
        (*(int (*)())callbacks[7])();
      }
      pcVar10 = (code *)callbacks[0xe];
    }
    else if (uVar6 == 0x22) {
      if ((uintptr_t)((code *)callbacks[6])!=(uintptr_t)(f33_reset_vector)) {
        (*(int (*)())callbacks[6])();
      }
      if ((uintptr_t)((code *)callbacks[7])!=(uintptr_t)(f33_reset_vector)) {
        (*(int (*)())callbacks[7])();
      }
      if ((uintptr_t)((code *)callbacks[9])!=(uintptr_t)(f33_reset_vector)) {
        (*(int (*)())callbacks[9])();
      }
      pcVar10 = (code *)callbacks[0xf];
    }
    else {
      pcVar10 = (code *)callbacks[0xd];
      if (uVar6 != 0x2200) {
        if ((uintptr_t)(pcVar10)!=(uintptr_t)(f33_reset_vector)) {
          (*(int (*)())pcVar10)();
        }
        uVar7 = 0x2200;
        goto LAB_0006c32e;
      }
    }
    if ((uintptr_t)(pcVar10)!=(uintptr_t)(f33_reset_vector)) {
      (*(int (*)())pcVar10)();
    }
  }
LAB_0006c32e:
  state->packed_status = uVar7;
  state->passing_count = auStack_36[0];
  state->failing_count = uStack_32;
  state->failing_high_water = uStack_30;
  state->recovery_count = uStack_2c;
  state->elapsed_count = uStack_26;
  return 0x11;
}


