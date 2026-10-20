#include "common.h"

int publish_redundant_byte_6884_31ed0(uchar param_1)

{
  return publish_redundant_u8(param_1,((undefined *)camry_host_ptr(0xfebe6884u)),((undefined *)camry_host_ptr(0xfebe6880u)),((undefined *)camry_host_ptr(0xfebe6882u)));
}

int publish_redundant_byte_6885_31eea(uchar param_1)

{
  return publish_redundant_u8(param_1,((undefined *)camry_host_ptr(0xfebe6885u)),((undefined *)camry_host_ptr(0xfebe6881u)),((undefined *)camry_host_ptr(0xfebe6883u)));
}

int clear_both_redundant_bytes_6884_6885_31f04(void)

{
  publish_redundant_byte_6884_31ed0(0);
  return publish_redundant_byte_6885_31eea(0);
}

int initialize_redundant_bytes_and_vote_error_counters_31f18(void)

{
  DAT_febe6886 = 0;
  DAT_febe6888 = 0;
  publish_redundant_byte_6884_31ed0(0);
  return publish_redundant_byte_6885_31eea(0);
}

void vote_repair_byte_6884_and_count_failures_31f36(void)

{
  ushort uVar1;
  uint32_t puVar2;
  int iVar3;
  uchar uStack_5;
  
  puVar2 = 0xfebeb800u;
  iVar3 = vote_redundant_u8(((undefined *)camry_host_ptr(0xfebe6884u)),((undefined *)camry_host_ptr(0xfebe6880u)),((undefined *)camry_host_ptr(0xfebe6882u)),&uStack_5);
  uVar1 = (*((ushort *)camry_host_ptr((uint32_t)((int)(0xffffb086u + (uint32_t)((int)puVar2))))));
  if (iVar3 != 0) {
    if ((iVar3 != -0xb) && (iVar3 != -0xc)) {
      if (uVar1 <= DAT_0002bcfc) {
        uVar1 = uVar1 + 1;
      }
      goto LAB_00031f78;
    }
    publish_redundant_byte_6884_31ed0(uStack_5);
  }
  uVar1 = 0;
LAB_00031f78:
  (*((ushort *)camry_host_ptr((uint32_t)((int)(0xffffb086u + (uint32_t)((int)puVar2)))))) = uVar1;
  return;
}

void vote_repair_byte_6885_and_count_failures_31f80(void)

{
  ushort uVar1;
  uint32_t puVar2;
  int iVar3;
  uchar uStack_5;
  
  puVar2 = 0xfebeb800u;
  iVar3 = vote_redundant_u8(((undefined *)camry_host_ptr(0xfebe6885u)),((undefined *)camry_host_ptr(0xfebe6881u)),((undefined *)camry_host_ptr(0xfebe6883u)),&uStack_5);
  uVar1 = (*((ushort *)camry_host_ptr((uint32_t)((int)(0xffffb088u + (uint32_t)((int)puVar2))))));
  if (iVar3 != 0) {
    if ((iVar3 != -0xb) && (iVar3 != -0xc)) {
      if (uVar1 <= DAT_0002bcfc) {
        uVar1 = uVar1 + 1;
      }
      goto LAB_00031fc2;
    }
    publish_redundant_byte_6885_31eea(uStack_5);
  }
  uVar1 = 0;
LAB_00031fc2:
  (*((ushort *)camry_host_ptr((uint32_t)((int)(0xffffb088u + (uint32_t)((int)puVar2)))))) = uVar1;
  return;
}

void request_published_mode200_phase(void)

{
  ushort uVar1;
  ushort uVar2;
  uint32_t puVar3;
  uVar2 = DAT_febee8cc;
  uVar1 = DAT_febe6764;
  puVar3 = 0xfebeb800u;
  if ((DAT_febee8cc & 0xff00) == 0x200) {
    vote_repair_byte_6884_and_count_failures_31f36();
    vote_repair_byte_6885_and_count_failures_31f80();
    if ((((((*((char *)camry_host_ptr((uint32_t)((int)(0xffffb084u + (uint32_t)((int)puVar3)))))) == 'Z') &&
          ((*((char *)camry_host_ptr((uint32_t)((int)0xffffb084u + (int)(puVar3 + 1))))) == 'Z')) ||
         (((uVar1 & 1) != 0 && ((*((char *)camry_host_ptr((uint32_t)((int)0xffffb084u + (int)(puVar3 + 1))))) == 'Z')))) ||
        (((uVar1 >> 1 & 1) != 0 && ((*((char *)camry_host_ptr((uint32_t)((int)(0xffffb084u + (uint32_t)((int)puVar3)))))) == 'Z')))) &&
       ((uVar2 + 0x15 & 0xff) < 0x23)) {
      thunk_set_indexed_request_and_clear_complement_b15ac((uVar2 + 0x15) & 0xff);
      publish_redundant_byte_6884_31ed0(0);
      publish_redundant_byte_6885_31eea(0);
    }
  }
  return;
}
