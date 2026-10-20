#include "common.h"

void nvm_begin_record_slot_checksum_scan_7708c(ushort param_1,ushort param_2,uchar param_3)

{
  uint32_t puVar1;
  uint uVar2;
  uint uVar3;
  
  puVar1 = 0x23dfcu;
  uVar3 = (uint)param_1;
  if (uVar3 < nvm_descriptor_count) {
    DAT_febf6c44 = param_1;
    uVar2 = nvm_payload_page_count(param_1);
    nvm_payload_chunks_remaining = (ushort)uVar2;
    DAT_febf6c24 = nvm_record_offset(param_1,param_2,0);
    uVar2 = nvm_read_header_validate_handle_and_accumulate_7786a(uVar3,DAT_febf6c24,param_3);
    if ((uVar2 == 1) && (uVar2 = nvm_read_chunk_accumulate_and_check_inline_checksum_76ff0(uVar3,DAT_febf6c24,param_3), uVar2 == 1)) {
      if (nvm_payload_chunks_remaining != 0) {
        return;
      }
      if (0x20 < (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + uVar3 * 6 + 0x383a))))) {
        uVar2 = nvm_read_payload_checksum(param_1,DAT_febf6c24,param_3);
      }
    }
    nvm_dispatch_read_completion_and_reset_record_77640(uVar2);
  }
  return;
}

uint nvm_continue_record_checksum_scan_7712a(void)

{
  uint uVar1;
  
  uVar1 = nvm_read_chunk_accumulate_and_check_inline_checksum_76ff0(DAT_febf6c44,DAT_febf6c24,0);
  if (uVar1 == 1) {
    if (nvm_payload_chunks_remaining != 0) {
      return uVar1;
    }
    uVar1 = nvm_read_payload_checksum(DAT_febf6c44,DAT_febf6c24,'\0');
  }
  nvm_dispatch_read_completion_and_reset_record_77640(uVar1);
  return uVar1;
}

uint nvm_write_copy_header_from_source_slot_77170(ushort param_1)

{
  ushort uVar1;
  uint uVar2;
  undefined4 uVar3;
  int iVar4;
  uchar *puVar5;
  uint uVar6;
  
  uVar1 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x27634u + (uint32_t)(param_1) * (uint32_t)sizeof(F33NvmDescriptor)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmDescriptor) + (uint32_t)offsetof(F33NvmDescriptor, payload_bytes)))));
  uVar2 = nvm_record_offset(param_1,DAT_febf6c42,0);
  uVar3 = thunk_return_argument_word_7490e((0xfebf6b80u));
  nvm_record_context_set_handle_772a2(((undefined2 *)camry_host_ptr((uint32_t)((0xfebf6b80u)))), (uint)param_1);
  if (uVar1 < 0x21) {
    uVar1 = uVar1 + (uVar1 & 3);
    iVar4 = nvm_read_map_blank_and_failure_status_776fa(uVar2 + 4,uVar1,((undefined *)camry_host_ptr(0xfebf6b90u)),0);
    if (iVar4 != 1) {
      return (uint)iVar4;
    }
    puVar5 = ((uchar *)camry_host_ptr((uint32_t)(thunk_return_argument_word_7490e((0xfebf6b80u)))));
    uVar2 = nvm_sum_bytes(2,puVar5);
    uVar6 = nvm_sum_bytes(uVar1,((undefined *)camry_host_ptr(0xfebf6b90u)));
    nvm_checksum_accumulator = nvm_checksum_accumulator + uVar6 + uVar2 + 0xc000;
    nvm_record_context_set_header_checksum_772ae((0xfebf6b80u),nvm_checksum_accumulator & 0xffff);
  }
  else {
    nvm_record_context_set_header_checksum_772ae((0xfebf6b80u),0);
    puVar5 = ((uchar *)camry_host_ptr((uint32_t)(thunk_return_argument_word_7490e((0xfebf6b80u)))));
    uVar2 = nvm_sum_bytes(2,puVar5);
    nvm_checksum_accumulator = nvm_checksum_accumulator + uVar2;
  }
  return nvm_stage_and_submit_program_with_optional_deferral_74c54(DAT_febf6c24, 4, ((uchar *)camry_host_ptr((uint32_t)(uVar3))), 9, 0);
}

undefined * nvm_begin_record_slot_copy_7723c(ushort param_1,ushort param_2,undefined2 param_3)

{
  uint uVar1;
  undefined *puVar2;
  
  if (param_1 < nvm_descriptor_count) {
    DAT_febf6c42 = param_3;
    DAT_febf6c44 = param_1;
    uVar1 = nvm_payload_page_count(param_1);
    nvm_payload_chunks_remaining = (ushort)uVar1;
    DAT_febf6c24 = nvm_record_offset(param_1,param_2,0);
    puVar2 = ((undefined *)camry_host_ptr((uint32_t)(nvm_write_copy_header_from_source_slot_77170(param_1))));
  }
  else {
    puVar2 = ((undefined *)camry_host_ptr(0xfffbu));
  }
  return puVar2;
}

undefined4 thunk_return_argument_word_7490e(undefined4 param_1)

{
  return return_argument_word_7490e(param_1);
}

undefined2 nvm_record_context_get_handle_7729c(undefined2 *param_1)

{
  return *param_1;
}

void nvm_record_context_set_handle_772a2(undefined2 *param_1,undefined2 param_2)

{
  *param_1 = param_2;
  return;
}

uint nvm_header_checksum(F33NvmRecordContext *context)

{
  return (uint)context->checksum16;
}

void nvm_record_context_set_header_checksum_772ae(int param_1,undefined2 param_2)

{
  (*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 2)))) = param_2;
  return;
}

undefined4 nvm_record_context_get_payload_source_772b4(int param_1)

{
  return (*((undefined4 *)camry_host_ptr((uint32_t)(param_1 + 4))));
}

void nvm_record_context_set_payload_source_772ba(int param_1,undefined4 param_2)

{
  (*((undefined4 *)camry_host_ptr((uint32_t)(param_1 + 4)))) = param_2;
  return;
}

void nvm_copy_payload_chunk
               (F33NvmRecordContext *context,ushort payload_offset,ushort byte_count,uchar *source)

{
  copy_bytes_forward(((uchar *)camry_host_ptr((uint32_t)(context->destination_buffer + payload_offset))), source, (uint)byte_count);
  return;
}

void nvm_set_read_destination(F33NvmRecordContext *context,uchar *destination)

{
  context->destination_buffer = camry_host_addr(destination);
  return;
}

uint nvm_tail_checksum(F33NvmRecordContext *context)

{
  return context->checksum32;
}

void nvm_record_context_set_checksum_trailer_772e4(int param_1,undefined4 param_2)

{
  (*((undefined4 *)camry_host_ptr((uint32_t)(param_1 + 0xc)))) = param_2;
  return;
}

undefined4 nvm_record_context_checksum_trailer_address_772ea(int param_1)

{
  return return_argument_word_7490e(param_1 + 0xc);
}

void nvm_reset_active_record_and_checksum_772f8(void)

{
  nvm_checksum_accumulator = 0;
  DAT_febf6c24 = 0xffffffff;
  DAT_febf6c44 = 0xffff;
  return;
}

void nvm_dispatch_erase_completion_and_reset_record_77370(uint param_1)

{
  nvm_dispatch_selected_descriptor_callback_slot_six_7847c(param_1);
  nvm_reset_active_record_and_checksum_772f8();
  return;
}

undefined * nvm_compare_written_payload_source_chunk_77380(void)

{
  ushort handle;
  uint32_t puVar1;
  int iVar2;
  uint uVar3;
  int iVar4;
  undefined *puVar5;
  uint uVar6;
  uchar auStack_58 [64];
  
  handle = DAT_febf6c44;
  iVar4 = DAT_febf6c24;
  puVar1 = 0x23dfcu;
  puVar5 = ((undefined *)camry_host_ptr(0xfffbu));
  iVar2 = nvm_record_context_get_payload_source_772b4((0xfebf6b80u));
  if (handle < (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + 0x3b2c))))) {
    uVar3 = nvm_payload_page_count(handle);
    uVar3 = (uVar3 - nvm_payload_chunks_remaining) * 0x40;
    uVar6 = uVar3 & 0xffff;
    uVar3 = nvm_payload_chunk_length(handle,(ushort)uVar3);
    puVar5 = ((undefined *)camry_host_ptr((uint32_t)(nvm_read_with_optional_blank_check(iVar4 + uVar6 + 4,(ushort)uVar3,auStack_58,'\0')
    )));
    if ((camry_host_addr(puVar5)==((uint32_t)((uint32_t)(0x1)))) &&
       (iVar4 = compare_unsigned_byte_ranges_7484a(uVar6 + iVar2, camry_host_addr(auStack_58), uVar3), iVar4 != 0)) {
      puVar5 = ((undefined *)camry_host_ptr(0xfffdu));
    }
  }
  return puVar5;
}

uint nvm_write_payload_chunk_with_zero_padding_773fe(ushort param_1)

{
  ushort uVar1;
  int iVar2;
  uint uVar3;
  uchar *puVar4;
  int iVar5;
  uint uVar6;
  uint uVar7;
  
  iVar2 = DAT_febf6c24;
  uVar1 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x27634u + (uint32_t)(param_1) * (uint32_t)sizeof(F33NvmDescriptor)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmDescriptor) + (uint32_t)offsetof(F33NvmDescriptor, payload_bytes)))));
  uVar3 = nvm_payload_page_count(param_1);
  uVar3 = (uVar3 - nvm_payload_chunks_remaining) * 0x40;
  uVar7 = uVar3 & 0xffff;
  uVar3 = nvm_payload_chunk_length(param_1,(ushort)uVar3);
  if ((uVar1 & 3) != 0) {
    fill_byte_range_74872((int)((uint32_t)(0xfebf6b90u)), 0, uVar3);
    puVar4 = ((uchar *)camry_host_ptr((uint32_t)(nvm_record_context_get_payload_source_772b4((0xfebf6b80u)))));
    copy_bytes_forward(((undefined *)camry_host_ptr(0xfebf6b90u)),puVar4,(uint)uVar1);
    nvm_record_context_set_payload_source_772ba((0xfebf6b80u), (int)((uint32_t)(0xfebf6b90u)));
  }
  iVar5 = nvm_record_context_get_payload_source_772b4((0xfebf6b80u));
  puVar4 = ((uchar *)camry_host_ptr((uint32_t)(uVar7 + iVar5)));
  uVar6 = nvm_sum_bytes((ushort)uVar3,puVar4);
  nvm_checksum_accumulator = nvm_checksum_accumulator + uVar6;
  return nvm_stage_and_submit_program_with_optional_deferral_74c54(iVar2 + uVar7 + 4,uVar3,puVar4,2,0);
}

uint nvm_write_accumulated_checksum_trailer_7749e(ushort param_1)

{
  ushort uVar1;
  int iVar2;
  uint32_t puVar3;
  undefined4 uVar4;
  
  iVar2 = DAT_febf6c24;
  puVar3 = 0x23dfcu;
  uVar4 = nvm_record_context_checksum_trailer_address_772ea((0xfebf6b80u));
  uVar1 = (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + (uint)param_1 * 6 + 0x383a))));
  nvm_checksum_accumulator = nvm_checksum_accumulator + 0xc0000000;
  nvm_record_context_set_checksum_trailer_772e4(0xfebf6b80u, nvm_checksum_accumulator);
  return nvm_stage_and_submit_program_with_optional_deferral_74c54(iVar2 + uVar1 + 4, 4, ((uchar *)camry_host_ptr((uint32_t)(uVar4))), 4, 0);
}

void nvm_verify_written_chunk_and_continue_774ee(int param_1)

{
  uint32_t puVar1;
  puVar1 = 0x23dfcu;
  if ((param_1 == 1) && (param_1 = camry_host_addr(nvm_compare_written_payload_source_chunk_77380()), param_1 == 1)) {
    nvm_payload_chunks_remaining = nvm_payload_chunks_remaining - 1;
    if (nvm_payload_chunks_remaining == 0) {
      if (0x20 < (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + (uint)DAT_febf6c44 * 6 + 0x383a))))) {
        param_1 = nvm_write_accumulated_checksum_trailer_7749e(DAT_febf6c44);
      }
    }
    else {
      param_1 = nvm_write_payload_chunk_with_zero_padding_773fe((*((volatile uint16_t *)camry_host_ptr(0xfebf6c44u))));
    }
  }
  if (param_1 != 2) {
    nvm_dispatch_selected_descriptor_callback_slot_seven_7849e(param_1);
    nvm_reset_active_record_and_checksum_772f8();
  }
  return;
}

undefined * nvm_compare_full_record_header_77548(void)

{
  undefined4 uVar1;
  int iVar2;
  undefined *puVar3;
  uchar auStack_c [4];
  
  puVar3 = ((undefined *)camry_host_ptr(0xfffbu));
  if ((DAT_febf6c44 < nvm_descriptor_count) &&
     (puVar3 = ((undefined *)camry_host_ptr((uint32_t)(nvm_read_with_optional_blank_check(DAT_febf6c24,4,auStack_c,'\0')))),camry_host_addr(puVar3)==((uint32_t)((uint32_t)(0x1))))) {
    uVar1 = thunk_return_argument_word_7490e((0xfebf6b80u));
    iVar2 = compare_unsigned_byte_ranges_7484a(uVar1, camry_host_addr(auStack_c), 4);
    if (iVar2 != 0) {
      puVar3 = ((undefined *)camry_host_ptr(0xfffdu));
    }
  }
  return puVar3;
}

void nvm_verify_header_then_write_payload_7759a(int param_1)

{
  if ((param_1 == 1) && (param_1 = camry_host_addr(nvm_compare_full_record_header_77548()), param_1 == 1)) {
    param_1 = nvm_write_payload_chunk_with_zero_padding_773fe(DAT_febf6c44);
  }
  if (param_1 != 2) {
    nvm_dispatch_selected_descriptor_callback_slot_seven_7849e(param_1);
    nvm_reset_active_record_and_checksum_772f8();
  }
  return;
}

undefined * nvm_compare_checksum_trailer_775ca(void)

{
  undefined4 uVar1;
  int iVar2;
  undefined *puVar3;
  uchar auStack_10 [4];
  
  puVar3 = ((undefined *)camry_host_ptr(0xfffbu));
  if (((uint)DAT_febf6c44 < (uint)nvm_descriptor_count) &&
     (puVar3 = ((undefined *)camry_host_ptr((uint32_t)(nvm_read_with_optional_blank_check
                         (DAT_febf6c24 + (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x27634u + (uint32_t)(DAT_febf6c44) * (uint32_t)sizeof(F33NvmDescriptor)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmDescriptor) + (uint32_t)offsetof(F33NvmDescriptor, payload_bytes))))) + 4,4,
                          auStack_10,'\0')))),camry_host_addr(puVar3)==((uint32_t)((uint32_t)(0x1))))) {
    uVar1 = nvm_record_context_checksum_trailer_address_772ea((0xfebf6b80u));
    iVar2 = compare_unsigned_byte_ranges_7484a(uVar1, camry_host_addr(auStack_10), 4);
    if (iVar2 != 0) {
      puVar3 = ((undefined *)camry_host_ptr(0xfffdu));
    }
  }
  return puVar3;
}

void nvm_verify_trailer_then_complete_write_77626(int param_1)

{
  if (param_1 == 1) {
    param_1 = camry_host_addr(nvm_compare_checksum_trailer_775ca());
  }
  nvm_dispatch_selected_descriptor_callback_slot_seven_7849e(param_1);
  nvm_reset_active_record_and_checksum_772f8();
  return;
}

void nvm_dispatch_read_completion_and_reset_record_77640(uint param_1)

{
  nvm_dispatch_selected_descriptor_callback_slot_eight_784c0(param_1);
  nvm_reset_active_record_and_checksum_772f8();
  return;
}

uint nvm_start_reverse_erase_with_flag1_77650(uint param_1,uint param_2)

{
  return nvm_start_reverse_erase(param_1,param_2 & 0xffff,1);
}

uint nvm_write_record_header_from_payload_source_77660(uint param_1)

{
  ushort byte_count;
  undefined4 uVar1;
  uchar *puVar2;
  uint uVar3;
  uint uVar4;
  
  byte_count = (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x27634u + (uint32_t)(param_1 & 0xffff) * (uint32_t)sizeof(F33NvmDescriptor)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmDescriptor) + (uint32_t)offsetof(F33NvmDescriptor, payload_bytes)))));
  uVar1 = thunk_return_argument_word_7490e((0xfebf6b80u));
  nvm_record_context_set_handle_772a2(((undefined2 *)camry_host_ptr((uint32_t)((0xfebf6b80u)))), param_1 & 0xffff);
  if (byte_count < 0x21) {
    puVar2 = ((uchar *)camry_host_ptr((uint32_t)(thunk_return_argument_word_7490e((int)0xfebf6b80))));
    uVar3 = nvm_sum_bytes(2,puVar2);
    puVar2 = ((uchar *)camry_host_ptr((uint32_t)(nvm_record_context_get_payload_source_772b4((0xfebf6b80u)))));
    uVar4 = nvm_sum_bytes(byte_count,puVar2);
    nvm_checksum_accumulator = nvm_checksum_accumulator + uVar4 + uVar3 + 0xc000;
    nvm_record_context_set_header_checksum_772ae((0xfebf6b80u),nvm_checksum_accumulator & 0xffff);
  }
  else {
    nvm_record_context_set_header_checksum_772ae((int)0xfebf6b80, 0x0);
    puVar2 = ((uchar *)camry_host_ptr((uint32_t)(thunk_return_argument_word_7490e((int)0xfebf6b80))));
    uVar3 = nvm_sum_bytes(2,puVar2);
    nvm_checksum_accumulator = nvm_checksum_accumulator + uVar3;
  }
  return nvm_stage_and_submit_program_with_optional_deferral_74c54(DAT_febf6c24, 4, ((uchar *)camry_host_ptr((uint32_t)(uVar1))), 3, 0);
}

uint nvm_read_map_blank_and_failure_status_776fa(uint param_1,ushort param_2,uchar *param_3,uchar param_4)

{
  uint result;
  uint uVar2;
  
  uVar2 = nvm_read_with_optional_blank_check(param_1,param_2,param_3,param_4);
  result = 1;
  if ((uVar2 != 1) && (result = 0xfffb, uVar2 == 3)) {
    result = 0xfffc;
  }
  return result;
}

uint nvm_read_payload_chunk(ushort handle,uint record_offset,uchar read_option)

{
  ushort uVar1;
  ushort payload_offset;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  uchar auStack_64 [64];
  
  uVar1 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x27634u + (uint32_t)(handle) * (uint32_t)sizeof(F33NvmDescriptor)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmDescriptor) + (uint32_t)offsetof(F33NvmDescriptor, payload_bytes)))));
  uVar2 = (uint)uVar1;
  uVar3 = nvm_payload_page_count(handle);
  uVar3 = (uVar3 - nvm_payload_chunks_remaining) * 0x40;
  payload_offset = (ushort)uVar3;
  uVar4 = nvm_payload_chunk_length(handle,payload_offset);
  uVar3 = nvm_read_map_blank_and_failure_status_776fa(record_offset + (uVar3 & 0xffff) + 4,uVar4,auStack_64,read_option);
  if (uVar3 == 1) {
    if (uVar2 < 0x21) {
      uVar5 = nvm_sum_bytes((ushort)uVar4,auStack_64);
      uVar5 = nvm_checksum_accumulator + uVar5 + 0xc000;
      nvm_checksum_accumulator = uVar5;
      uVar6 = nvm_header_checksum(((F33NvmRecordContext *)camry_host_ptr((uint32_t)((0xfebf6b80u)))));
      if (uVar6 != (uVar5 & 0xffff)) {
        return 0xfffc;
      }
    }
    else {
      uVar5 = nvm_sum_bytes((ushort)uVar4,auStack_64);
      nvm_checksum_accumulator = nvm_checksum_accumulator + uVar5;
    }
    if ((uVar1 & 3) == 0) {
      uVar2 = uVar4;
    }
    nvm_copy_payload_chunk(((F33NvmRecordContext *)camry_host_ptr((uint32_t)((0xfebf6b80u)))), payload_offset, (ushort)uVar2, auStack_64);
    nvm_payload_chunks_remaining = nvm_payload_chunks_remaining - 1;
  }
  return uVar3;
}

uint nvm_read_payload_checksum(ushort handle,uint record_offset,uchar read_option)

{
  uint32_t puVar1;
  undefined4 uVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  
  puVar1 = 0x23dfcu;
  uVar2 = nvm_record_context_checksum_trailer_address_772ea((0xfebf6b80u));
  uVar3 = nvm_read_map_blank_and_failure_status_776fa(((uint32_t)((uint32_t)((*((ushort *)camry_host_ptr((uint32_t)(puVar1 + (uint)handle * 6 + 0x383a)))) + record_offset + 4))),  4, ((uchar *)camry_host_ptr((uint32_t)(uVar2))),  
                       read_option);
  if (uVar3 == 1) {
    uVar5 = nvm_checksum_accumulator + 0xc0000000;
    nvm_checksum_accumulator = uVar5;
    uVar4 = nvm_tail_checksum(((F33NvmRecordContext *)camry_host_ptr((uint32_t)((0xfebf6b80u)))));
    if (uVar4 != uVar5) {
      uVar3 = 0xfffc;
    }
  }
  return uVar3;
}

uint nvm_continue_record_payload_read_77824(void)

{
  uint uVar1;
  
  uVar1 = nvm_read_payload_chunk(DAT_febf6c44,DAT_febf6c24,'\0');
  if (uVar1 == 1) {
    if (nvm_payload_chunks_remaining != 0) {
      return uVar1;
    }
    uVar1 = nvm_read_payload_checksum(DAT_febf6c44,DAT_febf6c24,'\0');
  }
  nvm_dispatch_read_completion_and_reset_record_77640(uVar1);
  return uVar1;
}

int nvm_read_header_validate_handle_and_accumulate_7786a(uint param_1,undefined4 param_2,undefined1 param_3)

{
  uchar *source;
  int iVar1;
  uint uVar2;
  uint uVar3;
  
  source = ((uchar *)camry_host_ptr((uint32_t)(thunk_return_argument_word_7490e((0xfebf6b80u)))));
  iVar1 = nvm_read_map_blank_and_failure_status_776fa(param_2,4,source,param_3);
  if (iVar1 == 1) {
    uVar2 = nvm_record_context_get_handle_7729c(((undefined2 *)camry_host_ptr((uint32_t)((0xfebf6b80u)))));
    uVar3 = nvm_sum_bytes(2,source);
    nvm_checksum_accumulator = nvm_checksum_accumulator + uVar3;
    if (uVar2 != (param_1 & 0xffff)) {
      iVar1 = 0xfffc;
      nvm_mark_attempt_header_mismatch_76988();
    }
  }
  return iVar1;
}

void nvm_bind_record_context(F33NvmCommitContext *context,F33NvmRecordContext *record)

{
  context->record = camry_host_addr(record);
  return;
}

undefined4 nvm_commit_context_get_marker_778cc(int param_1)

{
  return (*((undefined4 *)camry_host_ptr((uint32_t)(param_1 + 4))));
}

void nvm_commit_context_set_marker_778d2(int param_1,undefined4 param_2)

{
  (*((undefined4 *)camry_host_ptr((uint32_t)(param_1 + 4)))) = param_2;
  return;
}

undefined4 nvm_commit_context_marker_address_778d8(int param_1)

{
  return return_argument_word_7490e(param_1 + 4);
}

void thunk_nvm_reset_active_record_and_checksum_772f8(void)

{
  nvm_reset_active_record_and_checksum_772f8();
  return;
}

undefined * nvm_verify_commit_trailer_marker_77910(void)

{
  int iVar1;
  undefined *puVar2;
  uint uVar3;
  uchar *destination;
  int local_c;
  
  iVar1 = DAT_febf6c24;
  puVar2 = ((undefined *)camry_host_ptr(0xfffbu));
  if (DAT_febf6c44 < nvm_descriptor_count) {
    uVar3 = nvm_trailer_offset(DAT_febf6c44);
    destination = ((uchar *)camry_host_ptr((uint32_t)(return_argument_word_7490e(camry_host_addr(&local_c)))));
    puVar2 = ((undefined *)camry_host_ptr((uint32_t)(nvm_read_with_optional_blank_check(iVar1 + uVar3,4,destination,'\x01')
    )));
    if (camry_host_addr(puVar2)==((uint32_t)((uint32_t)(0x1)))) {
      if (local_c == -0x55555556) {
        return ((undefined *)camry_host_ptr((uint32_t)(0x1)));
      }
    }
    else if (camry_host_addr(puVar2)!=((uint32_t)((uint32_t)(0x3)))) {
      return puVar2;
    }
    puVar2 = ((undefined *)camry_host_ptr(0xfffdu));
  }
  return puVar2;
}

void nvm_verify_commit_marker_then_complete_write_77968(int param_1)

{
  if (param_1 == 1) {
    param_1 = camry_host_addr(nvm_verify_commit_trailer_marker_77910());
  }
  nvm_dispatch_selected_descriptor_callback_slot_seven_7849e(param_1);
  thunk_nvm_reset_active_record_and_checksum_772f8();
  return;
}

uint nvm_begin_base_record_write_with_commit_checksum_779b2(ushort param_1,int param_2)

{
  uint32_t puVar1;
  uint uVar2;
  uchar *source;
  uint uVar3;
  undefined4 local_14 [2];
  
  puVar1 = 0x23dfcu;
  uVar3 = (uint)param_1;
  local_14[0] = 0xaaaaaaaa;
  if ((uVar3 < nvm_descriptor_count) && (param_2 != 0)) {
    nvm_commit_context.record = (0xfebf6b80u);
    DAT_febf6c44 = param_1;
    nvm_record_context_set_payload_source_772ba((0xfebf6b80u),param_2);
    uVar2 = nvm_payload_page_count(param_1);
    nvm_payload_chunks_remaining = (ushort)uVar2;
    DAT_febf6c24 = (uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar1 + uVar3 * 6 + 0x3838)))) << 6;
    source = ((uchar *)camry_host_ptr((uint32_t)(return_argument_word_7490a(camry_host_addr(local_14)))));
    uVar2 = nvm_sum_bytes(4,source);
    nvm_checksum_accumulator = nvm_checksum_accumulator + uVar2;
    return nvm_write_record_header_from_payload_source_77660(uVar3);
  }
  return 0xfffb;
}

undefined * nvm_write_commit_trailer_marker_77a36(ushort param_1)

{
  ushort uVar1;
  uint32_t puVar2;
  undefined4 uVar3;
  uint uVar4;
  undefined *puVar5;
  
  puVar2 = 0x23dfcu;
  puVar5 = ((undefined *)camry_host_ptr(0xfffbu));
  uVar3 = nvm_commit_context_marker_address_778d8((0xfebf6b78u));
  if ((uint)param_1 < (uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0x3b2c))))) {
    nvm_commit_context.record = (0xfebf6b80u);
    DAT_febf6c44 = param_1;
    nvm_commit_context_set_marker_778d2((0xfebf6b78u),(int)0xaaaaaaaa);
    uVar1 = (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + (uint)param_1 * 6 + 0x3838))));
    DAT_febf6c24 = (uint)uVar1 * 0x40;
    uVar4 = nvm_trailer_offset(param_1);
    puVar5 = ((undefined *)camry_host_ptr((uint32_t)(nvm_stage_and_submit_program_with_optional_deferral_74c54(uVar4 + (uint)uVar1 * 0x40, 4, ((uchar *)camry_host_ptr((uint32_t)(uVar3))), 10, 1))));
  }
  return puVar5;
}

uint nvm_read_commit_marker_and_accumulate_77aa8(ushort param_1,int param_2,uchar param_3)

{
  uchar *destination;
  uint uVar1;
  int iVar2;
  
  destination = ((uchar *)camry_host_ptr((uint32_t)(nvm_commit_context_marker_address_778d8((0xfebf6b78u)))));
  uVar1 = nvm_trailer_offset(param_1);
  uVar1 = nvm_read_with_optional_blank_check(uVar1 + param_2,4,destination,param_3);
  if (uVar1 == 1) {
    iVar2 = nvm_commit_context_get_marker_778cc((0xfebf6b78u));
    if (iVar2 == -0x55555556) {
      uVar1 = nvm_sum_bytes(4,destination);
      nvm_checksum_accumulator = nvm_checksum_accumulator + uVar1;
      return 1;
    }
  }
  else if (uVar1 != 3) {
    return uVar1;
  }
  return 0xfffc;
}

void nvm_begin_record_read(ushort handle,uchar *destination,uchar read_option)

{
  F33NvmRecordContext *context;
  uint uVar1;
  uint uVar2;
  
  if ((handle < nvm_descriptor_count) && (camry_host_addr(destination)!=camry_host_addr((uchar *)0x0))) {
    DAT_febf6c44 = handle;
    nvm_bind_record_context(((F33NvmCommitContext *)camry_host_ptr((uint32_t)((0xfebf6b78u)))), ((F33NvmRecordContext *)camry_host_ptr((uint32_t)((0xfebf6b80u)))));
    nvm_set_read_destination(((F33NvmRecordContext *)camry_host_ptr((uint32_t)((int)0xfebf6b80))), destination);
    uVar1 = nvm_payload_page_count(handle);
    nvm_payload_chunks_remaining = (uint16_t)uVar1;
    DAT_febf6c24 = nvm_base_offset(handle);
    uVar1 = nvm_read_commit_marker_and_accumulate_77aa8(handle,DAT_febf6c24,1);
    if ((uVar1 == 1) &&
       ((uVar1 = nvm_read_header_validate_handle_and_accumulate_7786a(handle,DAT_febf6c24,read_option), uVar1 == 1 &&
        (uVar1 = nvm_read_payload_chunk(handle,DAT_febf6c24,read_option), uVar1 == 1)))) {
      if (nvm_payload_chunks_remaining != 0) {
        return;
      }
      uVar2 = nvm_payload_length(handle);
      if (0x20 < uVar2) {
        uVar1 = nvm_read_payload_checksum(handle,DAT_febf6c24,read_option);
      }
    }
    nvm_dispatch_read_completion_and_reset_record_77640(uVar1);
  }
  return;
}

void thunk_nvm_continue_record_payload_read_77824(void)

{
  nvm_continue_record_payload_read_77824();
  return;
}

void nvm_reset_request_mode_and_storage_handle_77bd8(void)

{
  DAT_febf6c4a = 0;
  DAT_febf6c38 = 0xffff;
  return;
}

void nvm_reset_request_and_completion_contexts_77c32(void)

{
  nvm_reset_request_mode_and_storage_handle_77bd8();
  nvm_reset_completion_context();
  return;
}

void nvm_clear_completed_request_mode_77c42(void)

{
  if (2 < DAT_febf6c4a) {
    nvm_reset_request_mode_and_storage_handle_77bd8();
  }
  return;
}

void nvm_set_request_mode_77c5a(undefined1 param_1)

{
  DAT_febf6c4a = param_1;
  return;
}

undefined1 nvm_get_request_mode_77c64(void)

{
  return DAT_febf6c4a;
}

void nvm_set_request_handle_snapshot_77c6e(undefined2 param_1)

{
  DAT_febf6c3a = param_1;
  return;
}

undefined2 nvm_get_request_handle_snapshot_77c78(void)

{
  return DAT_febf6c3a;
}

undefined * nvm_validate_and_set_storage_handle_77c82(ushort param_1)

{
  if (param_1 < nvm_descriptor_count) {
    DAT_febf6c38 = param_1;
    return ((undefined *)camry_host_ptr((uint32_t)(0x1)));
  }
  return ((undefined *)camry_host_ptr(0xfffbu));
}

undefined2 nvm_get_storage_handle_77c9e(void)

{
  return DAT_febf6c38;
}

undefined * nvm_validate_and_set_write_source_77ca8(int param_1)

{
  if (param_1 != 0) {
    DAT_febf6c14 = param_1;
    return ((undefined *)camry_host_ptr((uint32_t)(0x1)));
  }
  return ((undefined *)camry_host_ptr(0xfffbu));
}

undefined4 nvm_get_write_source_77cbe(void)

{
  return DAT_febf6c14;
}

undefined * nvm_validate_and_set_read_destination_77cc8(int param_1)

{
  if (param_1 != 0) {
    DAT_febf6c18 = param_1;
    return ((undefined *)camry_host_ptr((uint32_t)(0x1)));
  }
  return ((undefined *)camry_host_ptr(0xfffbu));
}

undefined4 nvm_get_read_destination_77cde(void)

{
  return DAT_febf6c18;
}

void nvm_snapshot_completion_mode_handle_and_reset_request_77ce8(void)

{
  nvm_completion_mode = DAT_febf6c4a;
  nvm_completion_storage_handle = DAT_febf6c38;
  nvm_reset_request_mode_and_storage_handle_77bd8();
  return;
}

void nvm_set_completion_raw_result_77d14(uint param_1)

{
  nvm_completion_raw_result = param_1;
  return;
}

void nvm_set_nonzero_completion_side_status_77d1e(uchar param_1)

{
  if (param_1 != '\0') {
    nvm_completion_side_status = param_1;
  }
  return;
}

void nvm_invalidate_marker_write_address_77df2(void)

{
  DAT_febf6c2c = 0xffffffff;
  return;
}

void thunk_nvm_invalidate_marker_write_address_77df2(void)

{
  nvm_invalidate_marker_write_address_77df2();
  return;
}

int nvm_allocation_end_minus_trailer_words_77e0a(uint param_1,uint param_2)

{
  uint uVar1;
  int iVar2;
  
  uVar1 = (uint)(*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x27634u + (uint32_t)(param_1 & 0xffff) * (uint32_t)sizeof(F33NvmDescriptor)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmDescriptor) + (uint32_t)offsetof(F33NvmDescriptor, payload_bytes)))));
  if (0x20 < uVar1) {
    uVar1 = uVar1 + 4;
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0x27634u + (uint32_t)(param_1 & 0xffff) * (uint32_t)sizeof(F33NvmDescriptor)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmDescriptor) + (uint32_t)offsetof(F33NvmDescriptor, option))))) == '\0') {
    iVar2 = uVar1 + 4;
  }
  else {
    iVar2 = uVar1 + 0xc;
  }
  return (iVar2 + 0x40U & 0xffffffc0) + (param_2 & 0xff) * -4;
}

void nvm_lookup_three_byte_status_pair_77e22(char *param_1,undefined1 *param_2,undefined1 *param_3)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  *param_2 = 0xd;
  *param_3 = 0xff;
  iVar2 = 0;
  while (((iVar3 = (short)iVar2 * 5, (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x27c84u + (uint32_t)(iVar3) * 1u)))) != *param_1 ||
          ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x27c85u + (uint32_t)(iVar3) * 1u)))) != param_1[1])) || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x27c86u + (uint32_t)(iVar3) * 1u)))) != param_1[2]))) {
    iVar1 = iVar2 + 1;
    iVar3 = iVar2 + -0xb;
    iVar2 = iVar1;
    if (iVar3 < 0 == (iVar1 < 0 && -1 < iVar3)) {
      return;
    }
  }
  *param_2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x27c87u + (uint32_t)(iVar3) * 1u))));
  *param_3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x27c88u + (uint32_t)(iVar3) * 1u))));
  return;
}

uint nvm_classify_two_word_blank_pattern_77e6e(uint param_1,undefined1 *param_2)

{
  undefined1 uVar1;
  uint uVar2;
  uchar auStack_10 [4];
  
  *param_2 = 0;
  uVar2 = nvm_read_with_optional_blank_check(param_1 + 4,4,auStack_10,'\x01');
  if (uVar2 == 1) {
    uVar1 = 0xff;
  }
  else {
    if (uVar2 != 3) {
      return uVar2;
    }
    uVar2 = nvm_read_with_optional_blank_check(param_1,4,auStack_10,'\x01');
    if (uVar2 != 1) {
      *param_2 = 0;
      if (uVar2 != 3) {
        return uVar2;
      }
      return 1;
    }
    uVar1 = 0xaa;
  }
  *param_2 = uVar1;
  return 1;
}

code * nvm_read_three_record_markers_and_decode_77eba(ushort param_1,undefined1 *param_2,undefined1 *param_3)

{
  uint uVar1;
  code *pcVar2;
  uint uVar3;
  undefined1 auStack_1b [3];
  
  pcVar2 = (code *)((undefined *)camry_host_ptr(0xfffbu));
  if (((param_1 < nvm_descriptor_count) && (camry_host_addr((param_2))!= 0)) &&
     (camry_host_addr((param_3))!= 0)) {
    *param_2 = 0xd;
    *param_3 = 0xff;
    uVar3 = 0;
    do {
      uVar1 = nvm_allocation_end_minus_trailer_words_77e0a(param_1,2);
      uVar1 = nvm_record_offset(param_1,(ushort)uVar3,uVar1);
      pcVar2 = ((code *)camry_host_ptr((uint32_t)(nvm_classify_two_word_blank_pattern_77e6e(uVar1,auStack_1b + uVar3))));
      if (camry_host_addr(pcVar2)!=((uint32_t)((uint32_t)(0x1)))) {
        return pcVar2;
      }
      uVar3 = uVar3 + 1 & 0xffff;
    } while (uVar3 < 3);
    nvm_lookup_three_byte_status_pair_77e22(auStack_1b,param_2,param_3);
    pcVar2 = ((code *)camry_host_ptr((uint32_t)(0x1)));
  }
  return pcVar2;
}

undefined * nvm_read_record_presence_marker_77f26(ushort param_1,ushort param_2,undefined1 *param_3)

{
  uint status;
  uint uVar2;
  uchar auStack_14 [4];
  
  status = 0xfffb;
  if (param_1 < nvm_descriptor_count) {
    *param_3 = 0;
    uVar2 = nvm_allocation_end_minus_trailer_words_77e0a(param_1,3);
    uVar2 = nvm_record_offset(param_1,param_2,uVar2);
    status = nvm_read_with_optional_blank_check(uVar2,4,auStack_14,'\x01');
    if (status == 1) {
      *param_3 = 0x55;
    }
    else if (status == 3) {
      *param_3 = 0;
      status = 1;
    }
  }
  return (undefined *)camry_host_ptr(status);
}

int nvm_match_three_markers_to_final_table_entries_77f7e(ushort param_1,undefined1 *param_2,char *param_3)

{
  char *pcVar1;
  undefined8 uVar2;
  uint uVar3;
  int iVar4;
  uint uVar5;
  char acStack_17 [3];
  
  uVar2 = 0x23dfc00000000;
  if (param_1 < nvm_descriptor_count) {
    *param_2 = 0xe;
    *param_3 = -1;
    uVar5 = 0;
    do {
      uVar3 = nvm_allocation_end_minus_trailer_words_77e0a(param_1,2);
      uVar3 = nvm_record_offset(param_1,(ushort)uVar5,uVar3);
      iVar4 = nvm_classify_two_word_blank_pattern_77e6e(uVar3,acStack_17 + uVar5);
      if (iVar4 != 1) {
        return iVar4;
      }
      uVar5 = uVar5 + 1 & 0xffff;
    } while (uVar5 < 3);
    uVar5 = 9;
    do {
      pcVar1 = ((char *)camry_host_ptr((uint32_t)((short)uVar5 * 5 + (int)((ulonglong)uVar2 >> 0x20) + 0x3e88)));
      if (((*pcVar1 == acStack_17[0]) && ((uintptr_t)(((pcVar1[1])))==(uintptr_t)(((acStack_17[1]))))) &&
         ((uintptr_t)(((pcVar1[2])))==(uintptr_t)(((acStack_17[2]))))) {
        *param_2 = 0xc;
        *param_3 = pcVar1[4];
        return 1;
      }
      uVar5 = uVar5 + 1;
    } while (uVar5 < 0xc);
    return 1;
  }
  return 0xfffb;
}
