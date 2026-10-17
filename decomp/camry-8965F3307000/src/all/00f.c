#include "common.h"


/* Select 24 current7200 or retained7320 records by71CC markers5A/A5, stride12. Only words0/4
   require their separate complements; words1/2/3 are ORed independently. Qualify aggregate word4,
   optionally OR7440..7446 when71EC.bit15, dispatch four action words, then mirror all five
   at71F4..71FC. Source stripping affects later aggregation. Native current/retained aggregation
   rejects invalid protected words0/4 while unprotected status/ancillary actions survive.
   Qualification strips current records only; dispatch preserves distinct
   status0351/mode/current-limit namespaces and PMR. */

void f33_aggregate_fault_actions(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint32_t puVar4;
  ushort uVar5;
  uint actions;
  uint actions_00;
  uint actions_01;
  uint actions_02;
  undefined2 *puVar6;
  ushort local_28;
  undefined2 uStack_26;
  undefined2 uStack_24;
  undefined2 uStack_22;
  ushort uStack_20;
  
  puVar4 = 0xfebeb800u;
  actions_02 = 0;
  actions_01 = 0;
  actions_00 = 0;
  actions = 0;
  uVar5 = 0;
  iVar3 = 0;
  do {
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe71ccu + (uint32_t)(iVar3) * 1u)))) == 'Z') {
      puVar6 = ((undefined *)camry_host_ptr(0xfebe7200u)) + iVar3 * 6;
      if ((~(uint)(ushort)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7200u + (uint32_t)(iVar3 * 6) * 2u)))) & 0xffff) ==
          (uint)*(ushort *)(((undefined *)camry_host_ptr(0xfebe713cu)) + iVar3 * 2)) {
        actions_02 = actions_02 | (ushort)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7200u + (uint32_t)(iVar3 * 6) * 2u))));
      }
      if ((ushort)~(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7208u + (uint32_t)(iVar3 * 6) * 2u)))) == *(ushort *)(((undefined *)camry_host_ptr(0xfebe719cu)) + iVar3 * 2)) {
        uVar5 = uVar5 | (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7208u + (uint32_t)(iVar3 * 6) * 2u))));
      }
LAB_0003c0a0:
      actions_01 = actions_01 | (ushort)puVar6[1];
      actions_00 = actions_00 | (ushort)puVar6[2];
      actions = actions | (ushort)puVar6[3];
    }
    else if (((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe71ccu + (uint32_t)(iVar3) * 1u))))) == -0x5b) {
      puVar6 = ((undefined *)camry_host_ptr(0xfebe7320u)) + iVar3 * 6;
      if ((~(uint)(ushort)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7320u + (uint32_t)(iVar3 * 6) * 2u)))) & 0xffff) ==
          (uint)*(ushort *)(((undefined *)camry_host_ptr(0xfebe710cu)) + iVar3 * 2)) {
        actions_02 = actions_02 | (ushort)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7320u + (uint32_t)(iVar3 * 6) * 2u))));
      }
      if ((ushort)~(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7328u + (uint32_t)(iVar3 * 6) * 2u)))) == *(ushort *)(((undefined *)camry_host_ptr(0xfebe716cu)) + iVar3 * 2)) {
        uVar5 = uVar5 | (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7328u + (uint32_t)(iVar3 * 6) * 2u))));
      }
      goto LAB_0003c0a0;
    }
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -0x17;
    iVar3 = iVar2;
    if (iVar1 < 0 == (iVar2 < 0 && -1 < iVar1)) {
      local_28 = (ushort)actions_02;
      uStack_26 = (undefined2)actions_01;
      uStack_24 = (undefined2)actions_00;
      uStack_22 = (undefined2)actions;
      uStack_20 = uVar5;
      f33_qualify_fault_action_aggregate(&local_28);
      if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb9edu + (uint32_t)((int)puVar4) * 1u)))) & 0x80) != 0) {
        actions_02 = actions_02 | DAT_febe7440;
        actions_01 = actions_01 | DAT_febe7442;
        actions_00 = actions_00 | DAT_febe7444;
        actions = actions | DAT_febe7446;
      }
      f33_route_fault_action_mode_request(actions_02);
      f33_route_fault_status_actions(actions_01);
      f33_route_fault_output_actions(actions_00);
      f33_route_fault_ancillary_actions(actions);
      DAT_febe71f4 = (short)actions_02;
      DAT_febe71f6 = (short)actions_01;
      DAT_febe71f8 = (short)actions_00;
      DAT_febe71fa = (short)actions;
      DAT_febe71fc = uVar5;
      return;
    }
  } while( true );
}



/* StoreA5 to71CC[low8(slot)]; no local bounds check. WriteA5 to71CC[low8slot] without a local
   bounds check; retain actual R6 slot from caller. */

void f33_select_retained_fault_record(uint slot)

{
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe71ccu + (uint32_t)(slot & 0xff) * 1u)))) = 0xa5;
  return;
}



/* Low8 slot<24: copy five current halfwords and two complements to retained storage, markA5, clear
   five current words and set complementsFFFF. Stride-tail halfwords untouched. Low8 slot<24 copies
   five words and two complements to retained storage, selectsA5, clears current words and sets
   complementsFFFF. Sixth halfwords remain untouched. */

void f33_retain_and_clear_fault_record(uint slot)

{
  int iVar1;
  int iVar2;
  uint slot_00;
  
  slot_00 = slot & 0xff;
  if (slot_00 < 0x18) {
    iVar1 = (int)(short)slot_00;
    iVar2 = slot_00 * 2;
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7320u + (uint32_t)(iVar1 * 6) * 2u)))) = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7200u + (uint32_t)(iVar1 * 6) * 2u))));
    *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe710cu)) + iVar2) = *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe713cu)) + iVar2);
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7322u + (uint32_t)(iVar1 * 6) * 2u)))) = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7202u + (uint32_t)(iVar1 * 6) * 2u))));
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7324u + (uint32_t)(iVar1 * 6) * 2u)))) = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7204u + (uint32_t)(iVar1 * 6) * 2u))));
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7326u + (uint32_t)(iVar1 * 6) * 2u)))) = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7206u + (uint32_t)(iVar1 * 6) * 2u))));
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7328u + (uint32_t)(iVar1 * 6) * 2u)))) = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7208u + (uint32_t)(iVar1 * 6) * 2u))));
    *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe716cu)) + iVar2) = *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe719cu)) + iVar2);
    f33_select_retained_fault_record(slot_00);
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7200u + (uint32_t)(iVar1 * 6) * 2u)))) = 0;
    *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe713cu)) + iVar2) = 0xffff;
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7202u + (uint32_t)(iVar1 * 6) * 2u)))) = 0;
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7204u + (uint32_t)(iVar1 * 6) * 2u)))) = 0;
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7206u + (uint32_t)(iVar1 * 6) * 2u)))) = 0;
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7208u + (uint32_t)(iVar1 * 6) * 2u)))) = 0;
    *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe719cu)) + iVar2) = 0xffff;
  }
  return;
}



/* Store5A to71CC[low8(slot)] only for slot<24. Select current fault record with marker5A only for
   low8slot<24. */

void f33_select_current_fault_record(uint slot)

{
  if ((slot & 0xff) < 0x18) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe71ccu + (uint32_t)(slot & 0xff) * 1u)))) = 0x5a;
  }
  return;
}



/* For low8(slot)<24, mutate the five-word input when its word4 overlaps71EC: clear word0 bits12,
   word1 bits70 and word2 bitsC00 (hex masks). OR into current record at7200+12*slot; AND
   corresponding word0/4 complements with inverse input. Does not mark the record current. The sixth
   halfword in the stride is not part of this contract. Mutable five-word template is stripped by
   overlapping qualification then OR-merged into a current slot with word0/4 complement updates.
   Low8 slot<24; no current-marker publication. Stride12 does not mean six action words. */

void f33_merge_fault_action_record(ushort *actions,uint slot)

{
  int iVar1;
  ushort uVar2;
  uint uVar3;
  
  uVar3 = slot & 0xff;
  if (uVar3 < 0x18) {
    iVar1 = (int)(short)uVar3;
    uVar2 = actions[4];
    if ((DAT_febe71ec & uVar2) != 0) {
      *actions = *actions & 0xffed;
      actions[1] = actions[1] & 0xff8f;
      (*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(actions) + 5)))) = (*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(actions) + 5)))) & 0xf7;
      (*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(actions) + 5)))) = (*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(actions) + 5)))) & 0xfb;
    }
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7200u + (uint32_t)(iVar1 * 6) * 2u)))) = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7200u + (uint32_t)(iVar1 * 6) * 2u)))) | *actions;
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7202u + (uint32_t)(iVar1 * 6) * 2u)))) = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7202u + (uint32_t)(iVar1 * 6) * 2u)))) | actions[1];
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7204u + (uint32_t)(iVar1 * 6) * 2u)))) = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7204u + (uint32_t)(iVar1 * 6) * 2u)))) | actions[2];
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7206u + (uint32_t)(iVar1 * 6) * 2u)))) = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7206u + (uint32_t)(iVar1 * 6) * 2u)))) | actions[3];
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7208u + (uint32_t)(iVar1 * 6) * 2u)))) = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7208u + (uint32_t)(iVar1 * 6) * 2u)))) | uVar2;
    *(ushort *)(((undefined *)camry_host_ptr(0xfebe713cu)) + uVar3 * 2) = *(ushort *)(((undefined *)camry_host_ptr(0xfebe713cu)) + uVar3 * 2) & ~*actions;
    *(ushort *)(((undefined *)camry_host_ptr(0xfebe719cu)) + uVar3 * 2) = *(ushort *)(((undefined *)camry_host_ptr(0xfebe719cu)) + uVar3 * 2) & ~actions[4];
  }
  return;
}



/* Bits2/1/0 or bit15-qualified6/5/4 select status4/3/2 viaBACF8. Active status increments71F0 while
   <=317DE=50, so the retained ceiling is51. No action publishes (counter<=50), then resets the
   counter only if unsignedEB9A>22169. Prioritized action bits publish internal status4/3/2
   throughBACF8 toBCBD. Active counter increments while<=50 to51; absent action reports counter<=50
   then resets only at unsignedEB9A>=22170. */

void f33_route_fault_status_actions(uint actions)

{
  ushort uVar1;
  uint32_t puVar2;
  uint mode;
  ushort uVar3;
  
  uVar1 = DAT_febeeb9a;
  uVar3 = DAT_febe71f0;
  puVar2 = 0xfebeb800u;
  if (((actions >> 2 & 1) == 0) && (((DAT_febe71ec & 0x8000) == 0 || ((actions >> 6 & 1) == 0)))) {
    if (((actions >> 1 & 1) == 0) && (((DAT_febe71ec & 0x8000) == 0 || ((actions >> 5 & 1) == 0))))
    {
      if (((actions & 1) == 0) && (((DAT_febe71ec & 0x8000) == 0 || ((actions >> 4 & 1) == 0)))) {
        f33_set_owner4_limit_mode((uint)(DAT_febe71f0 <= DAT_000317de));
        if (0x5699 < uVar1) {
          uVar3 = 0;
        }
        goto LAB_0003c308;
      }
      mode = 2;
    }
    else {
      mode = 3;
    }
  }
  else {
    mode = 4;
  }
  f33_set_owner4_limit_mode(mode);
  if (uVar3 <= DAT_000317de) {
    uVar3 = uVar3 + 1;
  }
LAB_0003c308:
  (*((ushort *)camry_host_ptr((uint32_t)((0xffffb9f0u + (uint32_t)((int)puVar2)))))) = uVar3;
  return;
}



void FUN_0003c386(void)

{
  DAT_febe71e5 = 0;
  DAT_febe71e8 = 0;
  f33_set_output_request_word('\x02',0);
  f33_cancel_terminal_output_ramp();
  f33_set_channel_owner_request('\x02',0);
  FUN_00056e66(2,0);
  return;
}



void FUN_0003c3ec(void)

{
  DAT_febe71e6 = 0;
  f33_set_output_request_word('\x05',0);
  f33_set_channel_owner_request('\x03',0);
  FUN_00056e66(3,0);
  return;
}



void FUN_0003c44c(void)

{
  DAT_febe71e7 = 0;
  f33_set_output_request_word('\x06',0);
  f33_set_channel_owner_request('\x04',0);
  FUN_00056e66(4,0);
  return;
}



/* Build five action words, suppress the entire template if word4 intersects ROM317DC, then merge
   into the slot. Word3 is ancillary action flags; word4 is qualification class. Kind32(hex) sets
   word3.bit15, not the qualifier bit15. Kinds are not DTC identities. Encode action kind into five
   words; ROM317DC suppresses by word4 before merge. Word3 ancillary flags and word4 qualification
   classes are distinct; kind32 sets ancillary bit15, not the qualifier. */

void f33_encode_fault_action_kind(uchar slot,uchar kind)

{
  ushort local_10;
  ushort uStack_e;
  undefined2 uStack_c;
  undefined2 uStack_a;
  ushort uStack_8;
  
  uStack_a = 0;
  uStack_8 = 0;
  uStack_c = 0;
  uStack_e = 0;
  local_10 = 0;
  switch(kind) {
  case '\x01':
    uStack_e = 4;
    goto LAB_0003c892;
  case '\x02':
    uStack_e = 2;
    goto LAB_0003c892;
  case '\x03':
    uStack_e = 1;
LAB_0003c892:
    local_10 = 1;
    uStack_c = 0xc;
    break;
  case '\x04':
    uStack_e = 4;
    local_10 = 0;
    uStack_c = 0x4000;
    break;
  case '\x05':
    uStack_e = 2;
    goto LAB_0003c8c0;
  case '\x06':
    uStack_e = 1;
LAB_0003c8c0:
    local_10 = 0;
    uStack_c = 0x8080;
    break;
  case '\a':
    uStack_e = 4;
    goto LAB_0003c8cc;
  case '\b':
    uStack_e = 2;
    goto LAB_0003c8cc;
  case '\t':
    uStack_e = 1;
LAB_0003c8cc:
    local_10 = 0;
    uStack_c = 0;
    break;
  case '\n':
    uStack_a = 2;
    break;
  case '\v':
    uStack_c = 0x10;
    uStack_e = 4;
    uStack_a = 0x6000;
    break;
  case '\r':
    uStack_e = 0x40;
    uStack_8 = 4;
    goto LAB_0003ca30;
  case '\x0e':
    uStack_e = 0x40;
    uStack_8 = 8;
    goto LAB_0003ca30;
  case '\x0f':
    uStack_e = 0x40;
    uStack_8 = 0x10;
    goto LAB_0003ca30;
  case '\x10':
    uStack_e = 0x20;
    uStack_8 = uStack_e;
    goto LAB_0003ca30;
  case '\x11':
    uStack_e = 0x20;
    uStack_8 = 0x40;
    goto LAB_0003ca30;
  case '\x12':
    uStack_e = 0x40;
    uStack_8 = 0x20;
    goto LAB_0003ca30;
  case '\x13':
    uStack_e = 0x40;
    uStack_8 = uStack_e;
    goto LAB_0003ca30;
  case '\x14':
    uStack_e = 0x40;
    goto LAB_0003ca10;
  case '\x15':
    uStack_e = 0x20;
LAB_0003ca10:
    uStack_8 = 0x4000;
    goto LAB_0003ca30;
  case '\x16':
    uStack_e = 0x10;
    uStack_8 = 0x4000;
    goto LAB_0003ca30;
  case '\x17':
    local_10 = 8;
    uStack_c = 0x120;
    goto LAB_0003c8f8;
  case '\x18':
    uStack_a = 0x14;
    break;
  case '\x19':
    uStack_a = 0x28;
    break;
  case '\x1a':
    local_10 = 1;
    uStack_c = 0xc;
LAB_0003c8f8:
    uStack_e = 4;
    uStack_a = 0x3c0;
    break;
  case '\x1b':
    local_10 = 2;
    uStack_e = 0x40;
    uStack_c = 0x405;
    goto LAB_0003ca42;
  case '\x1c':
    uStack_e = 0x40;
    uStack_c = 0x40a;
    goto LAB_0003ca5e;
  case '\x1d':
    local_10 = 2;
    uStack_e = 0x40;
    uStack_c = 0x444;
    goto LAB_0003ca42;
  case '\x1e':
    uStack_e = 0x40;
    uStack_c = 0x608;
    goto LAB_0003ca5e;
  case '\x1f':
    local_10 = 2;
    uStack_e = 0x20;
    uStack_c = 0x1401;
    goto LAB_0003ca42;
  case ' ':
    uStack_e = 0x20;
    uStack_c = 0x2402;
LAB_0003ca5e:
    local_10 = 2;
LAB_0003caf2:
    uStack_8 = 2;
    uStack_a = 0x4280;
    break;
  case '!':
    local_10 = 2;
    uStack_e = 0x40;
    uStack_c = 0x404;
    break;
  case '\"':
    local_10 = 2;
    uStack_e = 0x40;
    uStack_c = 0x408;
    break;
  case '#':
    local_10 = 0x10;
    uStack_e = 0x40;
    uStack_c = 0x825;
LAB_0003ca42:
    uStack_a = 0x2140;
    uStack_8 = 1;
    break;
  case '$':
    local_10 = 0x10;
    uStack_e = 0x40;
    uStack_c = 0x90a;
    goto LAB_0003caf2;
  case '%':
    uStack_a = 4;
    break;
  case '&':
    uStack_a = 0x10;
    break;
  case '\'':
    uStack_a = 8;
    break;
  case '(':
    uStack_a = 0x20;
    break;
  case '/':
    uStack_a = 0x400;
    break;
  case '0':
    uStack_a = 0x800;
    break;
  case '1':
    local_10 = 1;
    uStack_e = 4;
    uStack_c = 0x4000;
    uStack_a = 0x1000;
    break;
  case '2':
    uStack_a = 0x8000;
    break;
  case '5':
    uStack_e = 0x40;
    uStack_8 = 0x80;
    goto LAB_0003ca30;
  case '6':
    uStack_e = 0x40;
    uStack_8 = 0x100;
LAB_0003ca30:
    uStack_c = 0x400;
    local_10 = 2;
  }
  if ((DAT_000317dc & uStack_8) != 0) {
    local_10 = 0;
    uStack_e = 0;
    uStack_c = 0;
    uStack_8 = 0;
    uStack_a = 0;
  }
  f33_merge_fault_action_record(&local_10,(uint)slot);
  return;
}



void FUN_0003cb32(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = 0;
  do {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe744cu + (uint32_t)(iVar3) * 1u)))) = 0;
    iVar2 = iVar3 + 1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7452u + (uint32_t)(iVar3) * 1u)))) = 0;
    iVar1 = iVar3 + -5;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  return;
}



void FUN_0003cb48(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  DAT_febe7458 = 0;
  iVar3 = 0;
  do {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7459u + (uint32_t)(iVar3) * 1u)))) = 0;
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -1;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  iVar3 = 0;
  do {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe745du + (uint32_t)(iVar3) * 1u)))) = 0;
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -1;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  iVar3 = 0;
  do {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe744cu + (uint32_t)(iVar3) * 1u)))) = 0;
    iVar2 = iVar3 + 1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7452u + (uint32_t)(iVar3) * 1u)))) = 0;
    iVar1 = iVar3 + -5;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  DAT_febe745b = 0;
  DAT_febe745c = 0;
  return;
}



void FUN_0003cb88(uint param_1)

{
  char cVar1;
  uint event;
  
  param_1 = param_1 & 0xff;
  if (param_1 < 6) {
    cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7452u + (uint32_t)(param_1) * 1u))));
    event = (uint)*(ushort *)(((undefined *)camry_host_ptr(0x280a6u)) + param_1 * 8);
    if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe744cu + (uint32_t)(param_1) * 1u)))) != 'Z') && (event != 0)) {
      f33_report_diagnostic_healthy_observed(event);
    }
    if (cVar1 == 'Z') {
      if (event != 0) {
        f33_report_diagnostic_event_pass(event);
      }
      cVar1 = '\0';
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7452u + (uint32_t)(param_1) * 1u)))) = cVar1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe744cu + (uint32_t)(param_1) * 1u)))) = 0x5a;
  }
  return;
}



void FUN_0003cbe8(uint param_1)

{
  char cVar1;
  
  param_1 = param_1 & 0xff;
  if (param_1 < 6) {
    cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x280a4u + (uint32_t)(param_1 * 8) * 1u))));
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7452u + (uint32_t)(param_1) * 1u)))) != 'Z') {
      if (*(ushort *)(((undefined *)camry_host_ptr(0x280a6u)) + param_1 * 8) != 0) {
        f33_report_diagnostic_event_failure((uint)*(ushort *)(((undefined *)camry_host_ptr(0x280a6u)) + param_1 * 8),0x32);
      }
      if (cVar1 != '\0') {
        FUN_000545de(cVar1);
      }
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7452u + (uint32_t)(param_1) * 1u)))) = 0x5a;
  }
  return;
}



/* R6 bank/R7 status: zero publishes0 and healthy edge; invalid-only publishes22; original bit1 set
   publishes44 and first-failure edge. Local latch updates despite Dem inhibition. Low8 status0
   clears bank via healthy edge, invalid-only publishes22, original bit1 publishes44 and
   first-failure edge. Local latches can update while Dem reporter is inhibited. */

void f33_publish_receive_fault_bank(uchar bank,uchar status)

{
  uchar status_00;
  
  if (status == '\0') {
    FUN_0003cb88(bank);
    status_00 = '\0';
  }
  else if ((status >> 1 & 1) == 0) {
    status_00 = '\"';
  }
  else {
    FUN_0003cbe8(bank);
    status_00 = 'D';
  }
  if (bank < 6) {
    f33_set_communication_monitor_status((uint)(byte)(bank + 0x12),status_00);
  }
  return;
}



void FUN_0003cc74(byte param_1,uchar param_2)

{
  uint32_t puVar1;
  uint uVar2;
  
  puVar1 = 0xfebeb800u;
  if (param_1 < 6) {
    f33_publish_receive_fault_bank(param_1,param_2);
    uVar2 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x280abu + (uint32_t)((uint)param_1 * 8) * 1u))));
    if ((uVar2 < 6) && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbc52u + (uint32_t)((int)(puVar1 + uVar2)) * 1u)))) == 'Z')) {
      f33_report_diagnostic_event_pass((uint)*(ushort *)(((undefined *)camry_host_ptr(0x280a6u)) + uVar2 * 8));
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbc52u + (uint32_t)((int)(puVar1 + uVar2)) * 1u)))) = 0;
    }
  }
  return;
}



void FUN_0003cd16(void)

{
  byte bVar1;
  uint32_t puVar2;
  int iVar3;
  
  puVar2 = 0xfebeb800u;
  bVar1 = (byte)DAT_febe7f3a & 0x10;
  if (((byte)DAT_febe7f3a & 0x10) == 0) {
    iVar3 = 0x5a;
  }
  else {
    puVar2 = 0xfebeb800u;
    if (DAT_febe7459 == '\0') {
      puVar2 = 0xfebeb800u;
      f33_report_diagnostic_event_failure(0x76,0x32);
    }
    bVar1 = 0x5a;
    iVar3 = 0;
  }
  DAT_febe7459 = bVar1;
  if (iVar3 == 0x5a) {
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbc58u + (uint32_t)((int)puVar2) * 1u)))) != 'Z') {
      f33_report_diagnostic_healthy_observed(0x76);
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbc58u + (uint32_t)((int)puVar2) * 1u)))) = 0x5a;
  }
  return;
}



void FUN_0003cd72(void)

{
  byte bVar1;
  
  bVar1 = (byte)DAT_febe7f3a & 0x20;
  if (((byte)DAT_febe7f3a & 0x20) != 0) {
    if (DAT_febe745d == '\0') {
      f33_report_diagnostic_event_failure(0xa8,0x32);
    }
    bVar1 = 0x5a;
  }
  DAT_febe745d = bVar1;
  return;
}



/* Compose six receive rows, bus-status adapters and internal7F68 summary. 7F68 modes1/2 retain the
   previous summary; mode3 publishes44. Compose receive rows, controller status adapters and
   internal7F68 summary; intermediate modes1/2 retain previous terminal summary. */

void f33_update_communication_qualification_monitors(void)

{
  uchar status;
  
  f33_update_configured_receive_fault_banks();
  FUN_0003cd16();
  FUN_0003cd72();
  status = FUN_0003cda8();
  f33_set_communication_monitor_status(0,status);
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_3ce60(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_3ce62(void)

{
  return;
}



void FUN_0003ce64(void)

{
  uchar uVar1;
  uint32_t puVar2;
  char cVar3;
  char cVar4;
  
  uVar1 = f33_route30_receive_status;
  cVar3 = DAT_febe7465;
  cVar4 = DAT_febe7464;
  puVar2 = 0xfebeb800u;
  if (DAT_febee91c == 0x55aaaa55) {
    puVar2 = 0xfebeb800u;
    f33_report_diagnostic_healthy_observed(0x103);
    cVar3 = 'Z';
    if ((uVar1 == '\0') && (cVar4 != 'Z')) {
      f33_report_diagnostic_healthy_observed(0xaf);
      cVar4 = cVar3;
    }
  }
  else if (DAT_febee91c == -0x55aaaa56) {
    puVar2 = 0xfebeb800u;
    f33_report_diagnostic_healthy_observed(0xaf);
    cVar4 = 'Z';
    if ((uVar1 == '\0') && (cVar3 != 'Z')) {
      f33_report_diagnostic_healthy_observed(0x103);
      cVar3 = cVar4;
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbc64u + (uint32_t)((int)puVar2) * 1u)))) = cVar4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbc65u + (uint32_t)((int)puVar2) * 1u)))) = cVar3;
  return;
}



/* Application selected-source diagnostic adapters; not a CAN frame decoder. Selected-source
   flags7FA2/4/3/5 publish indices2/4/3/5 with diagnostic edge eventsAB/102/AF/103; source
   production is independent of frame-ID identity. */

void f33_publish_selected_source_fault_edges(void)

{
  char cVar1;
  char cVar2;
  char cVar3;
  char cVar4;
  uint32_t puVar5;
  uchar status;
  uchar status_00;
  uchar status_01;
  uchar status_02;
  int iVar6;
  char cVar7;
  char cVar8;
  char cVar9;
  char cVar10;
  char cVar11;
  
  cVar4 = DAT_febe7fa5;
  cVar3 = DAT_febe7fa4;
  cVar2 = DAT_febe7fa3;
  cVar1 = DAT_febe7fa2;
  cVar8 = DAT_febe7463;
  cVar10 = DAT_febe7462;
  cVar9 = DAT_febe7461;
  cVar11 = DAT_febe7460;
  puVar5 = 0xfebeb800u;
  cVar7 = '\0';
  iVar6 = 0;
  FUN_0003ce64();
  if (cVar1 == 'Z') {
    if (cVar11 != 'Z') {
      f33_report_diagnostic_event_failure(0xab,0x32);
      cVar11 = 'Z';
      cVar7 = 'Z';
    }
    status_02 = '\"';
  }
  else {
    if (cVar11 == 'Z') {
      f33_report_diagnostic_event_pass(0xab);
      cVar11 = '\0';
      iVar6 = 0x5a;
    }
    status_02 = '\0';
  }
  if (cVar3 == 'Z') {
    if (cVar10 != 'Z') {
      f33_report_diagnostic_event_failure(0x102,0x32);
      cVar10 = 'Z';
      cVar7 = 'Z';
    }
    status_01 = '\"';
  }
  else {
    if (cVar10 == 'Z') {
      f33_report_diagnostic_event_pass(0x102);
      cVar10 = '\0';
      iVar6 = 0x5a;
    }
    status_01 = '\0';
  }
  if (cVar2 == 'Z') {
    if (cVar9 != 'Z') {
      f33_report_diagnostic_event_failure(0xaf,0x32);
      cVar9 = 'Z';
      cVar7 = 'Z';
    }
    status_00 = '\"';
  }
  else {
    if (cVar9 == 'Z') {
      f33_report_diagnostic_event_pass(0xaf);
      cVar9 = '\0';
      iVar6 = 0x5a;
    }
    status_00 = '\0';
  }
  if (cVar4 == 'Z') {
    if (cVar8 != 'Z') {
      f33_report_diagnostic_event_failure(0x103,0x32);
      cVar8 = 'Z';
      cVar7 = 'Z';
    }
    status = '\"';
  }
  else {
    if (cVar8 == 'Z') {
      f33_report_diagnostic_event_pass(0x103);
      cVar8 = '\0';
      iVar6 = 0x5a;
    }
    status = '\0';
  }
  if (iVar6 == 0x5a) {
    FUN_00054724(5);
  }
  if (cVar7 == 'Z') {
    FUN_000545de(5);
  }
  f33_set_communication_monitor_status(2,status_02);
  f33_set_communication_monitor_status(4,status_01);
  f33_set_communication_monitor_status(3,status_00);
  f33_set_communication_monitor_status(5,status);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbc60u + (uint32_t)((int)puVar5) * 1u)))) = cVar11;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbc62u + (uint32_t)((int)puVar5) * 1u)))) = cVar10;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbc61u + (uint32_t)((int)puVar5) * 1u)))) = cVar9;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbc63u + (uint32_t)((int)puVar5) * 1u)))) = cVar8;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_3d026(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_3d028(void)

{
  return;
}



void FUN_0003d02a(void)

{
  char cVar1;
  uint32_t puVar2;
  char cVar3;
  char cVar4;
  
  cVar1 = DAT_febe802d;
  cVar3 = DAT_febe7471;
  cVar4 = DAT_febe7470;
  puVar2 = 0xfebeb800u;
  if (DAT_febee91c == 0x55aaaa55) {
    puVar2 = 0xfebeb800u;
    f33_report_diagnostic_healthy_observed(0x107);
    cVar3 = 'Z';
    if ((cVar1 == '\0') && (cVar4 != 'Z')) {
      f33_report_diagnostic_healthy_observed(0x105);
      cVar4 = cVar3;
    }
  }
  else if (DAT_febee91c == -0x55aaaa56) {
    puVar2 = 0xfebeb800u;
    f33_report_diagnostic_healthy_observed(0x105);
    cVar4 = 'Z';
    if ((cVar1 == '\0') && (cVar3 != 'Z')) {
      f33_report_diagnostic_healthy_observed(0x107);
      cVar3 = cVar4;
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbc70u + (uint32_t)((int)puVar2) * 1u)))) = cVar4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbc71u + (uint32_t)((int)puVar2) * 1u)))) = cVar3;
  return;
}



/* Application source-family diagnostic edges remain distinct from action selection. Source-family
   flags7FB0..7FB7 publish indices7..14 and event104..10B edges; only selected members enter slot16
   primary action mask. */

void f33_publish_source_family_fault_edges(void)

{
  char cVar1;
  char cVar2;
  char cVar3;
  char cVar4;
  char cVar5;
  char cVar6;
  char cVar7;
  char cVar8;
  uint32_t puVar9;
  uchar status;
  uchar status_00;
  uchar status_01;
  uchar status_02;
  uchar status_03;
  uchar status_04;
  uchar status_05;
  uchar status_06;
  char cVar10;
  char cVar11;
  char cVar12;
  char cVar13;
  char cVar14;
  char cVar15;
  char cVar16;
  char cVar17;
  
  cVar8 = DAT_febe7fb7;
  cVar7 = DAT_febe7fb6;
  cVar6 = DAT_febe7fb5;
  cVar5 = DAT_febe7fb4;
  cVar4 = DAT_febe7fb3;
  cVar3 = DAT_febe7fb2;
  cVar2 = DAT_febe7fb1;
  cVar1 = DAT_febe7fb0;
  cVar10 = DAT_febe746f;
  cVar14 = DAT_febe746e;
  cVar11 = DAT_febe746d;
  cVar15 = DAT_febe746c;
  cVar12 = DAT_febe746b;
  cVar16 = DAT_febe746a;
  cVar13 = DAT_febe7469;
  cVar17 = DAT_febe7468;
  puVar9 = 0xfebeb800u;
  FUN_0003d02a();
  if (cVar1 == 'Z') {
    if (cVar17 != 'Z') {
      f33_report_diagnostic_event_failure(0x104,0x32);
      cVar17 = 'Z';
    }
    status_06 = '\"';
  }
  else {
    if (cVar17 == 'Z') {
      f33_report_diagnostic_event_pass(0x104);
      cVar17 = '\0';
    }
    status_06 = '\0';
  }
  if (cVar3 == 'Z') {
    if (cVar16 != 'Z') {
      f33_report_diagnostic_event_failure(0x106,0x32);
      cVar16 = 'Z';
    }
    status_05 = '\"';
  }
  else {
    if (cVar16 == 'Z') {
      f33_report_diagnostic_event_pass(0x106);
      cVar16 = '\0';
    }
    status_05 = '\0';
  }
  if (cVar5 == 'Z') {
    if (cVar15 != 'Z') {
      f33_report_diagnostic_event_failure(0x108,0x32);
      cVar15 = 'Z';
    }
    status = '\"';
  }
  else {
    if (cVar15 == 'Z') {
      f33_report_diagnostic_event_pass(0x108);
      cVar15 = '\0';
    }
    status = '\0';
  }
  if (cVar7 == 'Z') {
    if (cVar14 != 'Z') {
      f33_report_diagnostic_event_failure(0x10a,0x32);
      cVar14 = 'Z';
    }
    status_00 = '\"';
  }
  else {
    if (cVar14 == 'Z') {
      f33_report_diagnostic_event_pass(0x10a);
      cVar14 = '\0';
    }
    status_00 = '\0';
  }
  if (cVar2 == 'Z') {
    if (cVar13 != 'Z') {
      f33_report_diagnostic_event_failure(0x105,0x32);
      cVar13 = 'Z';
    }
    status_01 = '\"';
  }
  else {
    if (cVar13 == 'Z') {
      f33_report_diagnostic_event_pass(0x105);
      cVar13 = '\0';
    }
    status_01 = '\0';
  }
  if (cVar4 == 'Z') {
    if (cVar12 != 'Z') {
      f33_report_diagnostic_event_failure(0x107,0x32);
      cVar12 = 'Z';
    }
    status_02 = '\"';
  }
  else {
    if (cVar12 == 'Z') {
      f33_report_diagnostic_event_pass(0x107);
      cVar12 = '\0';
    }
    status_02 = '\0';
  }
  if (cVar6 == 'Z') {
    if (cVar11 != 'Z') {
      f33_report_diagnostic_event_failure(0x109,0x32);
      cVar11 = 'Z';
    }
    status_03 = '\"';
  }
  else {
    if (cVar11 == 'Z') {
      f33_report_diagnostic_event_pass(0x109);
      cVar11 = '\0';
    }
    status_03 = '\0';
  }
  if (cVar8 == 'Z') {
    if (cVar10 != 'Z') {
      f33_report_diagnostic_event_failure(0x10b,0x32);
      cVar10 = 'Z';
    }
    status_04 = '\"';
  }
  else {
    if (cVar10 == 'Z') {
      f33_report_diagnostic_event_pass(0x10b);
      cVar10 = '\0';
    }
    status_04 = '\0';
  }
  f33_set_communication_monitor_status(7,status_06);
  f33_set_communication_monitor_status(9,status_05);
  f33_set_communication_monitor_status(0xb,status);
  f33_set_communication_monitor_status(0xd,status_00);
  f33_set_communication_monitor_status(8,status_01);
  f33_set_communication_monitor_status(10,status_02);
  f33_set_communication_monitor_status(0xc,status_03);
  f33_set_communication_monitor_status(0xe,status_04);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbc68u + (uint32_t)((int)puVar9) * 1u)))) = cVar17;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbc6au + (uint32_t)((int)puVar9) * 1u)))) = cVar16;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbc6cu + (uint32_t)((int)puVar9) * 1u)))) = cVar15;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbc6eu + (uint32_t)((int)puVar9) * 1u)))) = cVar14;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbc69u + (uint32_t)((int)puVar9) * 1u)))) = cVar13;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbc6bu + (uint32_t)((int)puVar9) * 1u)))) = cVar12;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbc6du + (uint32_t)((int)puVar9) * 1u)))) = cVar11;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbc6fu + (uint32_t)((int)puVar9) * 1u)))) = cVar10;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_3d318(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_3d31a(void)

{
  return;
}



/* Bounded indexed publication into communication monitor status array; action-root membership is
   narrower than all published banks. */

void f33_set_communication_monitor_status(uint index,uchar status)

{
  if ((index & 0xff) < 0x19) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7476u + (uint32_t)(index & 0xff) * 1u)))) = status;
  }
  return;
}



/* Single constant publisher: DAT_febe7474 = 0; Shape-classified from the canonical corpus; the
   target cell is not yet named, so the written state's meaning is unknown. */

void FUN_0003d330(void)

{
  DAT_febe7474 = 0;
  return;
}



void FUN_0003d336(void)

{
  DAT_febe7475 = DAT_febe7486 == '\"';
  return;
}



/* f33_reset_latched_monitor wrapper resetting exactly one monitor state ((F33LatchedMonitorState
   *)((undefined *)camry_host_ptr(0xfebe7490u))); whole-body shape-verified from the canonical corpus. Per-instance semantics
   derive from the referenced state cell; not individually executed. */

void f33_reset_latched_monitor_febe7490(void)

{
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7490u)));
  return;
}



/* f33_reset_latched_monitor wrapper resetting exactly one monitor state ((F33LatchedMonitorState
   *)((undefined *)camry_host_ptr(0xfebe7490u))); whole-body shape-verified from the canonical corpus. Per-instance semantics
   derive from the referenced state cell; not individually executed. */

void f33_reset_latched_monitor_febe7490_3d426(void)

{
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7490u)));
  return;
}



/* Thresholds pass0/fail20, eventDE confirmed failure; callback vector has no ordinary pass
   reporter. Content monitorA uses pass0/fail20 with DE failure callback and no ordinary pass
   callback; reset/re-entry clears ten-byte state. */

void f33_update_received_content_monitor_a(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bb48 == 'Z') {
    f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7490u)));
  }
  else {
    f33_step_latched_monitor
              ((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7490u)),(F33MonitorLimits *)((undefined *)camry_host_ptr(0x2b600u)),
               (F33TwoSidedMonitorCallbacks *)&PTR_f33_classify_received_content_a_000280d4);
  }
  f33_set_communication_monitor_status(0x10,(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbc90u + (uint32_t)((int)puVar1) * 1u)))));
  return;
}



/* Return44 unless7F68==0 and8052==0, then22 iff804D==1, otherwise11. ContentA returns44 unless7F68
   and8052 arezero; then804D==1 yields22, otherwise11. */

uint f33_classify_received_content_a(void)

{
  if ((f33_internal_source_admission_state == '\0') && (DAT_febe8052 == '\0')) {
    if (DAT_febe804d == '\x01') {
      return 0x22;
    }
    return 0x11;
  }
  return 0x44;
}



/* f33_report_diagnostic_event_failure(0xde,0x32); whole-body shape-verified. The literal is the
   encoded diagnostic event, not a recovered OEM name. */

void f33_report_diagnostic_event_failure_de_32_3d49c(void)

{
  f33_report_diagnostic_event_failure(0xde,0x32);
  return;
}



/* f33_reset_latched_monitor wrapper resetting exactly one monitor state ((F33LatchedMonitorState
   *)((undefined *)camry_host_ptr(0xfebe749cu))); whole-body shape-verified from the canonical corpus. Per-instance semantics
   derive from the referenced state cell; not individually executed. */

void f33_reset_latched_monitor_febe749c(void)

{
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe749cu)));
  return;
}



/* f33_reset_latched_monitor wrapper resetting exactly one monitor state ((F33LatchedMonitorState
   *)((undefined *)camry_host_ptr(0xfebe749cu))); whole-body shape-verified from the canonical corpus. Per-instance semantics
   derive from the referenced state cell; not individually executed. */

void f33_reset_latched_monitor_febe749c_3d4c0(void)

{
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe749cu)));
  return;
}



/* Parallel content monitor with eventDF; not a raw timeout predicate. Content monitorB uses
   pass0/fail20 with DF failure callback and no ordinary pass callback; not raw timeout detection.
    */

void f33_update_received_content_monitor_b(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bb4c == 'Z') {
    f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe749cu)));
  }
  else {
    f33_step_latched_monitor
              ((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe749cu)),(F33MonitorLimits *)((undefined *)camry_host_ptr(0x2b604u)),
               (F33TwoSidedMonitorCallbacks *)&PTR_f33_classify_received_content_b_00028108);
  }
  f33_set_communication_monitor_status(0x11,(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbc9cu + (uint32_t)((int)puVar1) * 1u)))));
  return;
}



/* Return44 unless7F68==0 and8052==0, then22 iff804E==1, otherwise11. ContentB returns44 unless7F68
   and8052 arezero; then804E==1 yields22, otherwise11. */

uint f33_classify_received_content_b(void)

{
  if ((f33_internal_source_admission_state == '\0') && (DAT_febe8052 == '\0')) {
    if (DAT_febe804e == '\x01') {
      return 0x22;
    }
    return 0x11;
  }
  return 0x44;
}



/* f33_report_diagnostic_event_failure(0xdf,0x32); whole-body shape-verified. The literal is the
   encoded diagnostic event, not a recovered OEM name. */

void f33_report_diagnostic_event_failure_df_32_3d536(void)

{
  f33_report_diagnostic_event_failure(0xdf,0x32);
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_3d54a(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_3d54c(void)

{
  return;
}



void FUN_0003d54e(void)

{
  char cVar1;
  uchar status;
  uint32_t puVar2;
  char cVar3;
  char cVar4;
  
  status = DAT_febe687b;
  cVar1 = DAT_febe687a;
  cVar3 = DAT_febe679d;
  puVar2 = 0xfebeb800u;
  cVar4 = DAT_febe679c;
  if (DAT_febe6879 == 'Z') {
    if (DAT_febe679c != 'Z') {
      puVar2 = 0xfebeb800u;
      f33_report_diagnostic_event_failure(0x97,0x32);
      FUN_000545de(0xb);
      FUN_00051cf6(9,0x32);
      cVar4 = 'Z';
    }
  }
  else if (DAT_febe679c == 'Z') {
    puVar2 = 0xfebeb800u;
    f33_report_diagnostic_event_pass(0x97);
    cVar4 = '\0';
  }
  if (cVar1 == 'Z') {
    if (cVar3 != 'Z') {
      f33_report_diagnostic_event_failure(0x98,0x32);
      cVar3 = 'Z';
    }
  }
  else if (cVar3 == 'Z') {
    f33_report_diagnostic_event_pass(0x98);
    cVar3 = '\0';
  }
  f33_set_communication_monitor_status(6,status);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x5064))))) = cVar4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x5063))))) = cVar3;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_3d5e2(void)

{
  return;
}



/* 8294.bit0 publishes local index0=22 and reportsEC; healthy publishes0 without ordinary pass.
   Local-link aggregate8294.bit0 publishes74A8=22 and reportsEC; healthy path publisheszero without
   ordinary pass reporter. */

void f33_publish_local_status_link_fault(void)

{
  uchar status;
  
  status = (uchar)(DAT_febe8294 & 1);
  if ((DAT_febe8294 & 1) != 0) {
    f33_report_diagnostic_event_failure(0xec,0x32);
    status = '\"';
  }
  f33_set_local_status_monitor_status(0,status);
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_3d6ce(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_3d6d0(void)

{
  return;
}



/* Slot12 ORs only74A8/74A9/74AD. Complete22 selects kind17; ANY nonzero publishes615B11 and
   prevents healthy diagnostic-cache refresh, even preconfirmation11. any nonzero, including11,
   blocks healthy diagnostic-cache refresh through615B. */

void f33_compose_local_status_fault_actions(void)

{
  uint32_t puVar1;
  uchar status;
  
  puVar1 = 0xfebeb800u;
  f33_retain_and_clear_fault_record(0xc);
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbcadu + (uint32_t)((int)puVar1) * 1u)))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbca9u + (uint32_t)((int)puVar1) * 1u)))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbca8u + (uint32_t)((int)puVar1) * 1u)))))
      & 0x22) == 0x22) {
    f33_encode_fault_action_kind('\f','\x17');
  }
  f33_select_current_fault_record(0xc);
  status = '\0';
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbcadu + (uint32_t)((int)puVar1) * 1u)))) != '\0' ||
      ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbca9u + (uint32_t)((int)puVar1) * 1u)))) != '\0' || (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbca8u + (uint32_t)((int)puVar1) * 1u)))) != '\0')) {
    status = '\x11';
  }
  f33_set_diagnostic_cache_blocker('\0',status);
  return;
}



/* Indexed local-status publisher; index1 is initialized/consumed but no active normal publisher is
   asserted. */

void f33_set_local_status_monitor_status(uint index,uchar status)

{
  if ((index & 0xff) < 6) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe74a8u + (uint32_t)(index & 0xff) * 1u)))) = status;
  }
  return;
}



/* f33_reset_latched_monitor wrapper resetting exactly one monitor state ((F33LatchedMonitorState
   *)((undefined *)camry_host_ptr(0xfebe74b0u))); whole-body shape-verified from the canonical corpus. Per-instance semantics
   derive from the referenced state cell; not individually executed. */

void f33_reset_latched_monitor_febe74b0(void)

{
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe74b0u)));
  return;
}



/* f33_reset_latched_monitor wrapper resetting exactly one monitor state ((F33LatchedMonitorState
   *)((undefined *)camry_host_ptr(0xfebe74b0u))); whole-body shape-verified from the canonical corpus. Per-instance semantics
   derive from the referenced state cell; not individually executed. */

void f33_reset_latched_monitor_febe74b0_3d746(void)

{
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe74b0u)));
  return;
}



/* Index5, thresholds40/40; F3 failure callback, healthy-observed51E2C on pass confirmation.
   Qualified local packet-flag monitor publishes index5 with40/40 thresholds; F3 pass confirmation
   uses healthy-observed API, not ordinary pass. */

void f33_update_qualified_local_status_monitor(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bb50 == 'Z') {
    f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe74b0u)));
  }
  else {
    f33_step_latched_monitor
              ((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe74b0u)),(F33MonitorLimits *)((undefined *)camry_host_ptr(0x2b608u)),
               (F33TwoSidedMonitorCallbacks *)&PTR_f33_classify_qualified_local_status_0002813c);
  }
  f33_set_local_status_monitor_status(5,(uchar)(*((undefined4 *)camry_host_ptr((uint32_t)((0xffffbcb0u + (uint32_t)((int)puVar1)))))));
  return;
}



/* 8278 fails22/passes11 only with qualification. Channel state2 counts67A0 to5 before switching65F1
   admission to65F6/7; closed gate44. Channel state2 counts67A0 to5 before switching65F1 admission
   to65F6/7. Gate failure44 differs from packet-flag failure22. */

uint f33_classify_qualified_local_status(void)

{
  char cVar1;
  uint uVar2;
  
  cVar1 = DAT_febe65f1;
  if ((DAT_febe64d0 == '\x02') || (DAT_febe64d1 == '\x02')) {
    if (DAT_febe67a0 < DAT_0002b61e) {
      DAT_febe67a0 = DAT_febe67a0 + 1;
    }
    else {
      cVar1 = DAT_febe65f7;
      if (DAT_febe65f6 == 'Z') goto LAB_0003d7de;
    }
  }
  else {
    DAT_febe67a0 = 0;
  }
  if (cVar1 != 'Z') {
    return 0x44;
  }
LAB_0003d7de:
  uVar2 = 0x11;
  if (DAT_febe8278 == 'Z') {
    uVar2 = 0x22;
  }
  return uVar2;
}



/* f33_report_diagnostic_healthy_observed(0xf3); whole-body shape-verified. The literal is the
   encoded diagnostic event, not a recovered OEM name. */

void f33_report_diagnostic_healthy_observed_f3_3d7f2(void)

{
  f33_report_diagnostic_healthy_observed(0xf3);
  return;
}



/* f33_report_diagnostic_event_failure(0xf3,0x32); whole-body shape-verified. The literal is the
   encoded diagnostic event, not a recovered OEM name. */

void f33_report_diagnostic_event_failure_f3_32_3d802(void)

{
  f33_report_diagnostic_event_failure(0xf3,0x32);
  return;
}



/* f33_reset_recoverable_monitor wrapper resetting exactly one monitor state
   ((F33RecoverableMonitorState *)((undefined *)camry_host_ptr(0xfebe74bcu))); whole-body shape-verified from the canonical
   corpus. Per-instance semantics derive from the referenced state cell; not individually executed.
    */

void f33_reset_recoverable_monitor_febe74bc(void)

{
  f33_reset_recoverable_monitor((F33RecoverableMonitorState *)((undefined *)camry_host_ptr(0xfebe74bcu)));
  return;
}



void FUN_0003d826(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  f33_reset_recoverable_monitor((F33RecoverableMonitorState *)((undefined *)camry_host_ptr(0xfebe74bcu)));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbcc8u + (uint32_t)((int)puVar1) * 1u)))) = 0;
  return;
}



/* Paired827D/827E monitor index4; any low status produces74C8 inhibition of individual predicates.
   Paired827D/827E monitor produces index4 and74C8 inhibition of individual predicates; excluded
   from slot12 action OR. */

void f33_update_paired_local_status_monitor(void)

{
  uchar status;
  uchar uVar1;
  uint32_t puVar2;
  puVar2 = 0xfebeb800u;
  if (DAT_0002bb54 == 'Z') {
    f33_reset_recoverable_monitor((F33RecoverableMonitorState *)((undefined *)camry_host_ptr(0xfebe74bcu)));
  }
  else if ((DAT_febe6764 & 3) == 0) {
    f33_step_recoverable_monitor
              ((F33RecoverableMonitorState *)((undefined *)camry_host_ptr(0xfebe74bcu)),
               (F33RecoverableMonitorLimits *)((undefined *)camry_host_ptr(0x2b60cu)),
               (F33RecoverableMonitorCallbacks *)&PTR_f33_classify_paired_local_status_00028170);
  }
  else {
    f33_retain_disabled_recoverable_monitor
              ((F33RecoverableMonitorState *)((undefined *)camry_host_ptr(0xfebe74bcu)),
               (F33RecoverableMonitorLimits *)((undefined *)camry_host_ptr(0x2b60cu)));
  }
  status = (uchar)(*((uint *)camry_host_ptr((uint32_t)((0xffffbcbcu + (uint32_t)((int)puVar2))))));
  uVar1 = status;
  if (((*((uint *)camry_host_ptr((uint32_t)((0xffffbcbcu + (uint32_t)((int)puVar2)))))) & 0xff) != 0) {
    uVar1 = 'Z';
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbcc8u + (uint32_t)((int)puVar2) * 1u)))) = uVar1;
  f33_set_local_status_monitor_status(4,status);
  return;
}



/* Failure only when both827D and827E equal5A. Paired local predicate fails only when both827D
   and827E equal5A. */

uint f33_classify_paired_local_status(void)

{
  if ((DAT_febe827e == 'Z') && (DAT_febe827d == 'Z')) {
    return 0x22;
  }
  return 0x11;
}



/* Confirmed-state paired predicate; both827D/827E5A is failure. Paired local confirmed-state
   predicate classifies the same both5A condition for recovery. */

uint f33_classify_paired_local_status_recovery(void)

{
  if ((DAT_febe827e == 'Z') && (DAT_febe827d == 'Z')) {
    return 0x22;
  }
  return 0x11;
}



/* f33_report_diagnostic_event_failure(0xf4,0x32); whole-body shape-verified. The literal is the
   encoded diagnostic event, not a recovered OEM name. */

void f33_report_diagnostic_event_failure_f4_32_3d8d2(void)

{
  f33_report_diagnostic_event_failure(0xf4,0x32);
  return;
}



/* f33_report_diagnostic_event_pass(0xf4); whole-body shape-verified. The literal is the encoded
   diagnostic event, not a recovered OEM name. */

void f33_report_diagnostic_event_pass_f4_3d8e6(void)

{
  f33_report_diagnostic_event_pass(0xf4);
  return;
}



/* f33_reset_recoverable_monitor wrapper resetting exactly one monitor state
   ((F33RecoverableMonitorState *)((undefined *)camry_host_ptr(0xfebe74ccu))); whole-body shape-verified from the canonical
   corpus. Per-instance semantics derive from the referenced state cell; not individually executed.
    */

void f33_reset_recoverable_monitor_febe74cc(void)

{
  f33_reset_recoverable_monitor((F33RecoverableMonitorState *)((undefined *)camry_host_ptr(0xfebe74ccu)));
  return;
}



/* f33_reset_recoverable_monitor wrapper resetting exactly one monitor state
   ((F33RecoverableMonitorState *)((undefined *)camry_host_ptr(0xfebe74ccu))); whole-body shape-verified from the canonical
   corpus. Per-instance semantics derive from the referenced state cell; not individually executed.
    */

void f33_reset_recoverable_monitor_febe74cc_3d906(void)

{
  f33_reset_recoverable_monitor((F33RecoverableMonitorState *)((undefined *)camry_host_ptr(0xfebe74ccu)));
  return;
}



/* Individual827E monitor publishes index2, inhibited by paired74C8; diagnostic eventF1 remains
   separate from action membership. */

void f33_update_individual_local_status_a(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bb58 == 'Z') {
    f33_reset_recoverable_monitor((F33RecoverableMonitorState *)((undefined *)camry_host_ptr(0xfebe74ccu)));
  }
  else if ((DAT_febe6764 & 1) == 0) {
    f33_step_recoverable_monitor
              ((F33RecoverableMonitorState *)((undefined *)camry_host_ptr(0xfebe74ccu)),
               (F33RecoverableMonitorLimits *)((undefined *)camry_host_ptr(0x2b612u)),
               (F33RecoverableMonitorCallbacks *)
               &PTR_f33_classify_individual_local_status_a_000281ac);
  }
  else {
    f33_retain_disabled_recoverable_monitor
              ((F33RecoverableMonitorState *)((undefined *)camry_host_ptr(0xfebe74ccu)),
               (F33RecoverableMonitorLimits *)((undefined *)camry_host_ptr(0x2b612u)));
  }
  f33_set_local_status_monitor_status(2,(uchar)(*((undefined4 *)camry_host_ptr((uint32_t)((0xffffbcccu + (uint32_t)((int)puVar1)))))));
  return;
}



/* Return44 while74C8==5A; otherwise classify827E as22/11. Individual827E predicate returns44
   under74C8=5A, otherwise22/11 from staged flag. */

uint f33_classify_individual_local_status_a(void)

{
  if (DAT_febe74c8 == 'Z') {
    return 0x44;
  }
  if (DAT_febe827e == 'Z') {
    return 0x22;
  }
  return 0x11;
}



/* f33_report_diagnostic_event_failure(0xf1,0x32); whole-body shape-verified. The literal is the
   encoded diagnostic event, not a recovered OEM name. */

void f33_report_diagnostic_event_failure_f1_32_3d984(void)

{
  f33_report_diagnostic_event_failure(0xf1,0x32);
  return;
}



/* f33_report_diagnostic_event_pass(0xf1); whole-body shape-verified. The literal is the encoded
   diagnostic event, not a recovered OEM name. */

void f33_report_diagnostic_event_pass_f1_3d998(void)

{
  f33_report_diagnostic_event_pass(0xf1);
  return;
}



/* f33_reset_recoverable_monitor wrapper resetting exactly one monitor state
   ((F33RecoverableMonitorState *)((undefined *)camry_host_ptr(0xfebe74d8u))); whole-body shape-verified from the canonical
   corpus. Per-instance semantics derive from the referenced state cell; not individually executed.
    */

void f33_reset_recoverable_monitor_febe74d8(void)

{
  f33_reset_recoverable_monitor((F33RecoverableMonitorState *)((undefined *)camry_host_ptr(0xfebe74d8u)));
  return;
}



/* f33_reset_recoverable_monitor wrapper resetting exactly one monitor state
   ((F33RecoverableMonitorState *)((undefined *)camry_host_ptr(0xfebe74d8u))); whole-body shape-verified from the canonical
   corpus. Per-instance semantics derive from the referenced state cell; not individually executed.
    */

void f33_reset_recoverable_monitor_febe74d8_3d9b8(void)

{
  f33_reset_recoverable_monitor((F33RecoverableMonitorState *)((undefined *)camry_host_ptr(0xfebe74d8u)));
  return;
}



/* Individual827D monitor publishes index3, inhibited by paired74C8; diagnostic eventF2 remains
   separate from action membership. */

void f33_update_individual_local_status_b(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bb5c == 'Z') {
    f33_reset_recoverable_monitor((F33RecoverableMonitorState *)((undefined *)camry_host_ptr(0xfebe74d8u)));
  }
  else if ((DAT_febe6764 >> 1 & 1) == 0) {
    f33_step_recoverable_monitor
              ((F33RecoverableMonitorState *)((undefined *)camry_host_ptr(0xfebe74d8u)),
               (F33RecoverableMonitorLimits *)((undefined *)camry_host_ptr(0x2b618u)),
               (F33RecoverableMonitorCallbacks *)
               &PTR_f33_classify_individual_local_status_b_000281e8);
  }
  else {
    f33_retain_disabled_recoverable_monitor
              ((F33RecoverableMonitorState *)((undefined *)camry_host_ptr(0xfebe74d8u)),
               (F33RecoverableMonitorLimits *)((undefined *)camry_host_ptr(0x2b618u)));
  }
  f33_set_local_status_monitor_status(3,(uchar)(*((undefined4 *)camry_host_ptr((uint32_t)((0xffffbcd8u + (uint32_t)((int)puVar1)))))));
  return;
}



/* Return44 while74C8==5A; otherwise classify827D as22/11. Individual827D predicate returns44
   under74C8=5A, otherwise22/11 from staged flag. */

uint f33_classify_individual_local_status_b(void)

{
  if (DAT_febe74c8 == 'Z') {
    return 0x44;
  }
  if (DAT_febe827d == 'Z') {
    return 0x22;
  }
  return 0x11;
}



/* f33_report_diagnostic_event_failure(0xf2,0x32); whole-body shape-verified. The literal is the
   encoded diagnostic event, not a recovered OEM name. */

void f33_report_diagnostic_event_failure_f2_32_3da36(void)

{
  f33_report_diagnostic_event_failure(0xf2,0x32);
  return;
}



/* f33_report_diagnostic_event_pass(0xf2); whole-body shape-verified. The literal is the encoded
   diagnostic event, not a recovered OEM name. */

void f33_report_diagnostic_event_pass_f2_3da4a(void)

{
  f33_report_diagnostic_event_pass(0xf2);
  return;
}



void FUN_0003da5a(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  f33_reset_windowed_monitor((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe74e4u)));
  f33_reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)((0xffffbcf4u + (uint32_t)((int)puVar1))))));
  return;
}



void FUN_0003da72(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  f33_reset_windowed_monitor((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe74e4u)));
  f33_reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)((0xffffbcf4u + (uint32_t)((int)puVar1))))));
  return;
}



/* Step delayed-difference indices6/7 without wrapper qualification disable. Qualification can
   permit failure while preventing pass. */

void f33_step_paired_source_difference_monitors_a(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bb60 == 'Z') {
    f33_reset_windowed_monitor((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe74e4u)));
    f33_reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)((0xffffbcf4u + (uint32_t)((int)puVar1))))));
  }
  else {
    f33_step_windowed_monitor
              ((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe74e4u)),(F33WindowedMonitorLimits *)((undefined *)camry_host_ptr(0x2b622u)),
               (F33TwoSidedMonitorCallbacks *)
               &PTR_f33_classify_paired_source_delayed_difference_aa_00028224);
    f33_step_windowed_monitor
              (((F33WindowedMonitorState *)camry_host_ptr((uint32_t)((0xffffbcf4u + (uint32_t)((int)puVar1))))),
               (F33WindowedMonitorLimits *)((undefined *)camry_host_ptr(0x2b62au)),
               (F33TwoSidedMonitorCallbacks *)
               &PTR_f33_classify_paired_source_delayed_difference_ab_00028258);
  }
  f33_publish_paired_source_monitor_status(6,(*((uint *)camry_host_ptr((uint32_t)((0xffffbce4u + (uint32_t)((int)puVar1)))))));
  f33_publish_paired_source_monitor_status(7,(*((uint *)camry_host_ptr((uint32_t)((0xffffbcf4u + (uint32_t)((int)puVar1)))))));
  return;
}



/* f33_report_diagnostic_healthy_observed(0x29); whole-body shape-verified. The literal is the
   encoded diagnostic event, not a recovered OEM name. */

void f33_report_diagnostic_healthy_observed_29_3db3e(void)

{
  f33_report_diagnostic_healthy_observed(0x29);
  return;
}



void FUN_0003db4e(void)

{
  uint event;
  
  event = 0x29;
  if (((byte)DAT_febe71ec & 0x80) != 0) {
    event = 0x22;
  }
  f33_report_diagnostic_event_failure(event,10);
  return;
}



/* f33_report_diagnostic_healthy_observed(0x2a); whole-body shape-verified. The literal is the
   encoded diagnostic event, not a recovered OEM name. */

void f33_report_diagnostic_healthy_observed_2a_3dbbc(void)

{
  f33_report_diagnostic_healthy_observed(0x2a);
  return;
}



void FUN_0003dbcc(void)

{
  uint event;
  
  event = 0x2a;
  if (((byte)DAT_febe71ec & 0x80) != 0) {
    event = 0x23;
  }
  f33_report_diagnostic_event_failure(event,10);
  return;
}



void FUN_0003dbe6(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  f33_reset_windowed_monitor((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe7504u)));
  f33_reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)((0xffffbd14u + (uint32_t)((int)puVar1))))));
  return;
}



void FUN_0003dbfe(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  f33_reset_windowed_monitor((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe7504u)));
  f33_reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)((0xffffbd14u + (uint32_t)((int)puVar1))))));
  return;
}



/* Parallel delayed-difference indices8/9, with independent retained windows and diagnostic
   reporting admission. */

void f33_step_paired_source_difference_monitors_b(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bb64 == 'Z') {
    f33_reset_windowed_monitor((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe7504u)));
    f33_reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)((0xffffbd14u + (uint32_t)((int)puVar1))))));
  }
  else {
    f33_step_windowed_monitor
              ((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe7504u)),(F33WindowedMonitorLimits *)((undefined *)camry_host_ptr(0x2b632u)),
               (F33TwoSidedMonitorCallbacks *)
               &PTR_f33_classify_paired_source_delayed_difference_ba_0002828c);
    f33_step_windowed_monitor
              (((F33WindowedMonitorState *)camry_host_ptr((uint32_t)((0xffffbd14u + (uint32_t)((int)puVar1))))),
               (F33WindowedMonitorLimits *)((undefined *)camry_host_ptr(0x2b63au)),
               (F33TwoSidedMonitorCallbacks *)
               &PTR_f33_classify_paired_source_delayed_difference_bb_000282c0);
  }
  f33_publish_paired_source_monitor_status(8,(*((uint *)camry_host_ptr((uint32_t)((0xffffbd04u + (uint32_t)((int)puVar1)))))));
  f33_publish_paired_source_monitor_status(9,(*((uint *)camry_host_ptr((uint32_t)((0xffffbd14u + (uint32_t)((int)puVar1)))))));
  return;
}



/* f33_report_diagnostic_healthy_observed(0x2b); whole-body shape-verified. The literal is the
   encoded diagnostic event, not a recovered OEM name. */

void f33_report_diagnostic_healthy_observed_2b_3dcca(void)

{
  f33_report_diagnostic_healthy_observed(0x2b);
  return;
}



/* f33_report_diagnostic_healthy_observed(0x2c); whole-body shape-verified. The literal is the
   encoded diagnostic event, not a recovered OEM name. */

void f33_report_diagnostic_healthy_observed_2c_3dd48(void)

{
  f33_report_diagnostic_healthy_observed(0x2c);
  return;
}



/* f33_reset_latched_monitor wrapper resetting exactly one monitor state ((F33LatchedMonitorState
   *)((undefined *)camry_host_ptr(0xfebe7524u))); whole-body shape-verified from the canonical corpus. Per-instance semantics
   derive from the referenced state cell; not individually executed. */

void f33_reset_latched_monitor_febe7524(void)

{
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7524u)));
  return;
}



void FUN_0003dd82(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7524u)));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbd34u + (uint32_t)((int)puVar1) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x54b4)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbd35u + (uint32_t)((int)puVar1) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x54b2)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbd36u + (uint32_t)((int)puVar1) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x54b0)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbd37u + (uint32_t)((int)puVar1) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x54ae)))));
  return;
}



/* Own qualification bit7 clear admits primary A; exact pass/fail25, strict26 confirmation. Disable
   clears cause bytes but retains confirmed state. */

void f33_step_paired_source_counter_monitor_a(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bb68 == 'Z') {
    puVar1 = 0xfebeb800u;
    f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7524u)));
  }
  else {
    if (((byte)DAT_febe71ec & 0x80) == 0) {
      f33_step_latched_monitor
                ((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7524u)),(F33MonitorLimits *)((undefined *)camry_host_ptr(0x2b642u)),
                 (F33TwoSidedMonitorCallbacks *)
                 &PTR_f33_classify_paired_source_counter_changes_a_000282f4);
      goto LAB_0003ddf2;
    }
    puVar1 = 0xfebeb800u;
    f33_retain_disabled_latched_monitor
              ((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7524u)),(F33MonitorLimits *)((undefined *)camry_host_ptr(0x2b642u)));
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbd30u + (uint32_t)((int)puVar1) * 1u)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbd31u + (uint32_t)((int)puVar1) * 1u)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbd32u + (uint32_t)((int)puVar1) * 1u)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbd33u + (uint32_t)((int)puVar1) * 1u)))) = 0;
LAB_0003ddf2:
  f33_publish_paired_source_monitor_status(0,(*((uint *)camry_host_ptr((uint32_t)((0xffffbd24u + (uint32_t)((int)puVar1)))))));
  return;
}



/* Compare four wrapping counter snapshots; actual invocation refreshes them even on44, but
   confirmed retained failure bypasses predicate. */

uint f33_classify_paired_source_counter_changes_a(void)

{
  uint uVar1;
  
  DAT_febe7530 = '\0';
  DAT_febe7531 = '\0';
  DAT_febe7532 = '\0';
  DAT_febe7533 = '\0';
  if ((DAT_febe7bc2 == 'Z') || (DAT_febe7bc3 == 'Z')) {
    DAT_febe7530 = '\0';
    if (DAT_febe634c != DAT_febe7534) {
      DAT_febe7530 = 'Z';
    }
    DAT_febe7531 = '\0';
    if (DAT_febe634e != DAT_febe7535) {
      DAT_febe7531 = 'Z';
    }
    DAT_febe7532 = '\0';
    if (DAT_febe6350 != DAT_febe7536) {
      DAT_febe7532 = 'Z';
    }
    DAT_febe7533 = '\0';
    if (DAT_febe6352 != DAT_febe7537) {
      DAT_febe7533 = 'Z';
    }
    if ((((DAT_febe7530 == 'Z') || (DAT_febe7531 == 'Z')) || (DAT_febe7532 == 'Z')) ||
       (DAT_febe7533 == 'Z')) {
      uVar1 = 0x22;
    }
    else {
      uVar1 = 0x11;
    }
  }
  else {
    uVar1 = 0x44;
  }
  DAT_febe7534 = DAT_febe634c;
  DAT_febe7535 = DAT_febe634e;
  DAT_febe7536 = DAT_febe6350;
  DAT_febe7537 = DAT_febe6352;
  return uVar1;
}



/* Sequential initializer chain: 4 unconditional calls and no other statements; shape-verified. The
   called sequence is the function's entire behavior; chain family members differ in callee sets. */

void f33_run_init_chain_3de92(void)

{
  f33_report_diagnostic_healthy_observed(0x46);
  f33_report_diagnostic_healthy_observed(0x47);
  f33_report_diagnostic_healthy_observed(0x48);
  f33_report_diagnostic_healthy_observed(0x49);
  return;
}



void FUN_0003deba(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_febe7530 == 'Z') {
    puVar1 = 0xfebeb800u;
    f33_report_diagnostic_event_failure(0x46,10);
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbd31u + (uint32_t)((int)puVar1) * 1u)))) == 'Z') {
    f33_report_diagnostic_event_failure(0x47,10);
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbd32u + (uint32_t)((int)puVar1) * 1u)))) == 'Z') {
    f33_report_diagnostic_event_failure(0x48,10);
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbd33u + (uint32_t)((int)puVar1) * 1u)))) == 'Z') {
    f33_report_diagnostic_event_failure(0x49,10);
  }
  return;
}



/* f33_reset_latched_monitor wrapper resetting exactly one monitor state ((F33LatchedMonitorState
   *)((undefined *)camry_host_ptr(0xfebe7538u))); whole-body shape-verified from the canonical corpus. Per-instance semantics
   derive from the referenced state cell; not individually executed. */

void f33_reset_latched_monitor_febe7538(void)

{
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7538u)));
  return;
}



void FUN_0003df22(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7538u)));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbd48u + (uint32_t)((int)puVar1) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x54b3)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbd49u + (uint32_t)((int)puVar1) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x54b1)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbd4au + (uint32_t)((int)puVar1) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x54af)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbd4bu + (uint32_t)((int)puVar1) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x54ad)))));
  return;
}



/* Compare four wrapping counter snapshots; actual invocation refreshes them even on44, but
   confirmed retained failure bypasses predicate. */

uint f33_classify_paired_source_counter_changes_b(void)

{
  uint uVar1;
  
  DAT_febe7544 = '\0';
  DAT_febe7545 = '\0';
  DAT_febe7546 = '\0';
  DAT_febe7547 = '\0';
  if ((DAT_febe7bc2 == 'Z') || (DAT_febe7bc3 == 'Z')) {
    DAT_febe7544 = '\0';
    if (DAT_febe634d != DAT_febe7548) {
      DAT_febe7544 = 'Z';
    }
    DAT_febe7545 = '\0';
    if (DAT_febe634f != DAT_febe7549) {
      DAT_febe7545 = 'Z';
    }
    DAT_febe7546 = '\0';
    if (DAT_febe6351 != DAT_febe754a) {
      DAT_febe7546 = 'Z';
    }
    DAT_febe7547 = '\0';
    if (DAT_febe6353 != DAT_febe754b) {
      DAT_febe7547 = 'Z';
    }
    if ((((DAT_febe7544 == 'Z') || (DAT_febe7545 == 'Z')) || (DAT_febe7546 == 'Z')) ||
       (DAT_febe7547 == 'Z')) {
      uVar1 = 0x22;
    }
    else {
      uVar1 = 0x11;
    }
  }
  else {
    uVar1 = 0x44;
  }
  DAT_febe7548 = DAT_febe634d;
  DAT_febe7549 = DAT_febe634f;
  DAT_febe754a = DAT_febe6351;
  DAT_febe754b = DAT_febe6353;
  return uVar1;
}



/* Sequential initializer chain: 4 unconditional calls and no other statements; shape-verified. The
   called sequence is the function's entire behavior; chain family members differ in callee sets. */

void f33_run_init_chain_3e032(void)

{
  f33_report_diagnostic_healthy_observed(0xfb);
  f33_report_diagnostic_healthy_observed(0xfc);
  f33_report_diagnostic_healthy_observed(0xfd);
  f33_report_diagnostic_healthy_observed(0xfe);
  return;
}



void FUN_0003e05a(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_febe7544 == 'Z') {
    puVar1 = 0xfebeb800u;
    f33_report_diagnostic_event_failure(0xfb,10);
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbd45u + (uint32_t)((int)puVar1) * 1u)))) == 'Z') {
    f33_report_diagnostic_event_failure(0xfc,10);
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbd46u + (uint32_t)((int)puVar1) * 1u)))) == 'Z') {
    f33_report_diagnostic_event_failure(0xfd,10);
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbd47u + (uint32_t)((int)puVar1) * 1u)))) == 'Z') {
    f33_report_diagnostic_event_failure(0xfe,10);
  }
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_3e0b2(void)

{
  return;
}



void FUN_0003e0b4(void)

{
  DAT_febe754f = 0;
  DAT_febe7550 = 0;
  DAT_febe7551 = 0;
  DAT_febe7552 = 0;
  return;
}



/* Signed16-wrapped824C-824E,824C-8250,8250-8252 outside inclusive[-1274,1274] set bits0/1/2;
   equality does not fail. */

uint f33_classify_paired_source_sample_differences(void)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  
  iVar1 = (int)DAT_0002b65a;
  iVar3 = (int)(short)(DAT_febe8250 - DAT_febe8252);
  iVar4 = (int)(short)(DAT_febe824c - DAT_febe824e);
  uVar2 = 0;
  iVar5 = (int)(short)(DAT_febe824c - DAT_febe8250);
  if ((iVar4 - iVar1 < 0 == (iVar4 < 0 != iVar1 < 0 && iVar1 < 0 == iVar4 - iVar1 < 0) &&
       iVar4 != iVar1) ||
     (iVar4 + iVar1 < 0 != (iVar4 < 0 != -iVar1 < 0 && -iVar1 < 0 == iVar4 + iVar1 < 0))) {
    uVar2 = 1;
  }
  iVar1 = (int)DAT_0002b65c;
  if ((iVar3 - iVar1 < 0 == (iVar3 < 0 != iVar1 < 0 && iVar1 < 0 == iVar3 - iVar1 < 0) &&
       iVar3 != iVar1) ||
     (iVar3 + iVar1 < 0 != (iVar3 < 0 != -iVar1 < 0 && -iVar1 < 0 == iVar3 + iVar1 < 0))) {
    uVar2 = uVar2 | 4;
  }
  iVar1 = (int)DAT_0002b65e;
  if ((iVar5 - iVar1 < 0 == (iVar5 < 0 != iVar1 < 0 && iVar1 < 0 == iVar5 - iVar1 < 0) &&
       iVar5 != iVar1) ||
     (iVar5 + iVar1 < 0 != (iVar5 < 0 != -iVar1 < 0 && -iVar1 < 0 == iVar5 + iVar1 < 0))) {
    uVar2 = uVar2 | 2;
  }
  return uVar2;
}



/* Combine raw difference mask with confirmed first-group statuses. */

uint f33_classify_paired_source_difference_first(uint mask)

{
  uint uVar1;
  
  uVar1 = 0;
  if ((((mask & 1) != 0) || (f33_paired_source_monitor_status[6] == '\"')) ||
     (f33_paired_source_monitor_status[7] == '\"')) {
    uVar1 = 0x5a;
  }
  return uVar1;
}



/* Combine middle raw difference and retained paired monitor confirmations. */

uint f33_classify_paired_source_difference_middle(uint mask)

{
  uint uVar1;
  
  uVar1 = 0;
  if ((((mask >> 1 & 1) != 0) || (f33_paired_source_monitor_status[6] == '\"')) ||
     (f33_paired_source_monitor_status[8] == '\"')) {
    uVar1 = 0x5a;
  }
  return uVar1;
}



/* Combine last raw difference and retained paired monitor confirmations. */

uint f33_classify_paired_source_difference_last(uint mask)

{
  uint uVar1;
  
  uVar1 = 0;
  if ((((mask >> 2 & 1) != 0) || (f33_paired_source_monitor_status[8] == '\"')) ||
     (f33_paired_source_monitor_status[9] == '\"')) {
    uVar1 = 0x5a;
  }
  return uVar1;
}



/* Classify signed wrapped differences and retained failures; increment wrapping counters754F..7552.
   Later snapshot/recomparison, not direct per-cycle fail status. */

void f33_accumulate_paired_source_difference_counts(void)

{
  uint32_t puVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  char cVar5;
  char cVar6;
  char cVar7;
  char cVar8;
  
  cVar5 = DAT_febe7552;
  cVar6 = DAT_febe7551;
  cVar7 = DAT_febe7550;
  cVar8 = DAT_febe754f;
  puVar1 = 0xfebeb800u;
  uVar2 = f33_classify_paired_source_sample_differences();
  uVar3 = f33_classify_paired_source_difference_first(uVar2);
  uVar4 = f33_classify_paired_source_difference_middle(uVar2);
  uVar2 = f33_classify_paired_source_difference_last(uVar2);
  if (uVar3 == 0) {
    if (uVar2 == 0) goto LAB_0003e1c2;
    if (uVar4 == 0) goto LAB_0003e1b4;
  }
  else {
    if (uVar4 == 0) {
      cVar7 = cVar7 + '\x01';
      if (uVar2 == 0) goto LAB_0003e1c2;
LAB_0003e1b4:
      cVar5 = cVar5 + '\x01';
      goto LAB_0003e1c2;
    }
    cVar8 = cVar8 + '\x01';
    if (uVar2 == 0) goto LAB_0003e1c2;
  }
  cVar6 = cVar6 + '\x01';
LAB_0003e1c2:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbd4cu + (uint32_t)((int)puVar1) * 1u)))) = (char)uVar3;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbd4du + (uint32_t)((int)puVar1) * 1u)))) = (char)uVar4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbd4eu + (uint32_t)((int)puVar1) * 1u)))) = (char)uVar2;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbd4fu + (uint32_t)((int)puVar1) * 1u)))) = cVar8;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbd50u + (uint32_t)((int)puVar1) * 1u)))) = cVar7;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbd51u + (uint32_t)((int)puVar1) * 1u)))) = cVar6;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbd52u + (uint32_t)((int)puVar1) * 1u)))) = cVar5;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_3e1d8(void)

{
  return;
}



/* Constant-block fill: 5 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_3e1da(void)

{
  DAT_febe7554 = 0;
  DAT_febe7555 = 0;
  DAT_febe7556 = 0;
  DAT_febe7557 = 0;
  DAT_febe7558 = 0;
  return;
}



/* Compare642C..642F against7555..7558, publish changed bits1/2/10/20 at7554 and refresh comparison
   snapshots. */

void f33_publish_paired_source_difference_changes(void)

{
  DAT_febe7554 = DAT_febe642c != DAT_febe7555;
  if (DAT_febe642d != DAT_febe7556) {
    DAT_febe7554 = DAT_febe7554 | 2;
  }
  if (DAT_febe642e != DAT_febe7557) {
    DAT_febe7554 = DAT_febe7554 | 0x10;
  }
  if (DAT_febe642f != DAT_febe7558) {
    DAT_febe7554 = DAT_febe7554 | 0x20;
  }
  DAT_febe7555 = DAT_febe642c;
  DAT_febe7556 = DAT_febe642d;
  DAT_febe7557 = DAT_febe642e;
  DAT_febe7558 = DAT_febe642f;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_3e22c(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_3e22e(void)

{
  return;
}



/* Rebuild slot4 from groups0/2/6/7 and1/3/8/9; confirmed22 selects kinds35/36. Transition11 plus
   exact lower OR11 holds7576/7578; otherwise refresh6292/6298. Diagnostic admission does not gate
   action/caches. Native eight-call monitor interval covers pending25/confirmed26, qualification
   filtering, window500/501, retained opposite failure, action records and held/refreshed7576/7578
   cache. Downstream47E4C publication and physical freshness remain static/unproved respectively. */

void f33_publish_paired_source_monitor_actions(void)

{
  char cVar1;
  char cVar2;
  char cVar3;
  uint32_t puVar4;
  uchar uVar5;
  
  cVar2 = DAT_febe7bc3;
  cVar1 = DAT_febe7bc2;
  puVar4 = 0xfebeb800u;
  f33_retain_and_clear_fault_record(4);
  if ((((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbd71u + (uint32_t)((int)puVar4) * 1u)))) |
         (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbd70u + (uint32_t)((int)puVar4) * 1u)))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbd6cu + (uint32_t)((int)puVar4) * 1u)))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbd6au + (uint32_t)((int)puVar4) * 1u)))))
        & 0x11) == 0x11) &&
      ((byte)(f33_paired_source_monitor_status[7] |
             f33_paired_source_monitor_status[6] |
             f33_paired_source_monitor_status[2] | f33_paired_source_monitor_status[0]) == 0x11)) ||
     (((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbd73u + (uint32_t)((int)puVar4) * 1u)))) |
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbd72u + (uint32_t)((int)puVar4) * 1u)))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbd6du + (uint32_t)((int)puVar4) * 1u)))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbd6bu + (uint32_t)((int)puVar4) * 1u)))))
       & 0x11) == 0x11 &&
      ((byte)(f33_paired_source_monitor_status[9] |
             f33_paired_source_monitor_status[8] |
             f33_paired_source_monitor_status[3] | f33_paired_source_monitor_status[1]) == 0x11))))
  {
    cVar3 = 'Z';
  }
  else {
    cVar3 = '\0';
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbd66u + (uint32_t)((int)puVar4) * 1u)))) = cVar3;
  if (cVar3 != 'Z') {
    (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffbd76u + (uint32_t)((int)puVar4)))))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar4 + -0x556e))));
    (*((undefined4 *)camry_host_ptr((uint32_t)((0xffffbd78u + (uint32_t)((int)puVar4)))))) = (*((undefined4 *)camry_host_ptr((uint32_t)(puVar4 + -0x5568))));
  }
  if (((f33_paired_source_monitor_status[7] |
       f33_paired_source_monitor_status[6] |
       f33_paired_source_monitor_status[2] | f33_paired_source_monitor_status[0]) & 0x22) == 0x22) {
    f33_encode_fault_action_kind('\x04','5');
  }
  if (((f33_paired_source_monitor_status[9] |
       f33_paired_source_monitor_status[8] |
       f33_paired_source_monitor_status[3] | f33_paired_source_monitor_status[1]) & 0x22) == 0x22) {
    f33_encode_fault_action_kind('\x04','6');
  }
  f33_select_current_fault_record(4);
  if ((cVar1 == 'Z') || (cVar2 == 'Z')) {
    DAT_febe7569 = 0x5a;
  }
  else {
    DAT_febe7569 = 0;
  }
  uVar5 = '\0';
  DAT_febe7574 = f33_paired_source_monitor_status[7] |
                 f33_paired_source_monitor_status[6] |
                 f33_paired_source_monitor_status[2] | f33_paired_source_monitor_status[0];
  DAT_febe7567 = f33_paired_source_monitor_status[9] |
                 f33_paired_source_monitor_status[8] |
                 f33_paired_source_monitor_status[3] |
                 f33_paired_source_monitor_status[1] | DAT_febe7574;
  DAT_febe7575 = f33_paired_source_monitor_status[9] |
                 f33_paired_source_monitor_status[8] |
                 f33_paired_source_monitor_status[3] | f33_paired_source_monitor_status[1];
  DAT_febe7568 = 0x11;
  if (DAT_febe7567 == 0) {
    DAT_febe7568 = 0;
  }
  else {
    uVar5 = '\x11';
  }
  f33_set_diagnostic_cache_blocker('\x02',uVar5);
  uVar5 = '\0';
  if (((f33_paired_source_monitor_status[9] |
       f33_paired_source_monitor_status[8] |
       f33_paired_source_monitor_status[3] |
       f33_paired_source_monitor_status[1] |
       f33_paired_source_monitor_status[7] |
       f33_paired_source_monitor_status[6] |
       f33_paired_source_monitor_status[2] | f33_paired_source_monitor_status[0]) & 0x11) == 0x11) {
    uVar5 = 'Z';
  }
  f33_set_monitor_pending_projection('\0',uVar5);
  return;
}



/* Unsigned low8 index<10: low status byte to755C[index], bits16..23 to756A[index]. Normal producer
   census covers0/1/2/3/6/7/8/9. */

void f33_publish_paired_source_monitor_status(uint index,uint packed)

{
  uint uVar1;
  
  uVar1 = index & 0xff;
  if (uVar1 < 10) {
    f33_paired_source_monitor_status[uVar1] = (uchar)packed;
    f33_paired_source_monitor_transition[uVar1] = (uchar)(packed >> 0x10);
  }
  return;
}



/* f33_reset_windowed_monitor wrapper resetting exactly one monitor state ((F33WindowedMonitorState
   *)((undefined *)camry_host_ptr(0xfebe757cu))); whole-body shape-verified from the canonical corpus. Per-instance semantics
   derive from the referenced state cell; not individually executed. */

void f33_reset_windowed_monitor_febe757c(void)

{
  f33_reset_windowed_monitor((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe757cu)));
  return;
}



/* f33_reset_windowed_monitor wrapper resetting exactly one monitor state ((F33WindowedMonitorState
   *)((undefined *)camry_host_ptr(0xfebe757cu))); whole-body shape-verified from the canonical corpus. Per-instance semantics
   derive from the referenced state cell; not individually executed. */

void f33_reset_windowed_monitor_febe757c_3e3ea(void)

{
  f33_reset_windowed_monitor((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe757cu)));
  return;
}



/* Admission and own primary status exactlyzero required; either staged mask intersecting05A0 fails.
    */

uint f33_classify_paired_source_status_masks_a(void)

{
  if (((DAT_febe7bc2 == 'Z') || (DAT_febe7bc3 == 'Z')) &&
     (f33_paired_source_monitor_status[0] == '\0')) {
    if (((DAT_0002b662 & DAT_febe6360) == 0) && ((DAT_0002b664 & DAT_febe6362) == 0)) {
      return 0x11;
    }
    return 0x22;
  }
  return 0x44;
}



/* f33_report_diagnostic_healthy_observed(0x4d); whole-body shape-verified. The literal is the
   encoded diagnostic event, not a recovered OEM name. */

void f33_report_diagnostic_healthy_observed_4d_3e48a(void)

{
  f33_report_diagnostic_healthy_observed(0x4d);
  return;
}



/* f33_report_diagnostic_event_failure(0x4d,10); whole-body shape-verified. The literal is the
   encoded diagnostic event, not a recovered OEM name. */

void f33_report_diagnostic_event_failure_4d_10_3e49a(void)

{
  f33_report_diagnostic_event_failure(0x4d,10);
  return;
}



/* f33_reset_windowed_monitor wrapper resetting exactly one monitor state ((F33WindowedMonitorState
   *)((undefined *)camry_host_ptr(0xfebe758cu))); whole-body shape-verified from the canonical corpus. Per-instance semantics
   derive from the referenced state cell; not individually executed. */

void f33_reset_windowed_monitor_febe758c(void)

{
  f33_reset_windowed_monitor((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe758cu)));
  return;
}



/* f33_reset_windowed_monitor wrapper resetting exactly one monitor state ((F33WindowedMonitorState
   *)((undefined *)camry_host_ptr(0xfebe758cu))); whole-body shape-verified from the canonical corpus. Per-instance semantics
   derive from the referenced state cell; not individually executed. */

void f33_reset_windowed_monitor_febe758c_3e4bc(void)

{
  f33_reset_windowed_monitor((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe758cu)));
  return;
}



/* Admission and own primary status exactlyzero required; either staged mask intersecting05A0 fails.
    */

uint f33_classify_paired_source_status_masks_b(void)

{
  if (((DAT_febe7bc2 == 'Z') || (DAT_febe7bc3 == 'Z')) &&
     (f33_paired_source_monitor_status[1] == '\0')) {
    if (((DAT_0002b666 & DAT_febe6364) == 0) && ((DAT_0002b668 & DAT_febe6366) == 0)) {
      return 0x11;
    }
    return 0x22;
  }
  return 0x44;
}



/* f33_report_diagnostic_healthy_observed(0x112); whole-body shape-verified. The literal is the
   encoded diagnostic event, not a recovered OEM name. */

void f33_report_diagnostic_healthy_observed_112_3e55c(void)

{
  f33_report_diagnostic_healthy_observed(0x112);
  return;
}



/* f33_report_diagnostic_event_failure(0x112,10); whole-body shape-verified. The literal is the
   encoded diagnostic event, not a recovered OEM name. */

void f33_report_diagnostic_event_failure_112_10_3e56c(void)

{
  f33_report_diagnostic_event_failure(0x112,10);
  return;
}



/* Return readiness latch in r10:5A means admitted, not a void side-effect-only helper. Retain
   completed latch until explicit stage initializer; pending sequencing and counts per
   configured-family readiness contract. No hardware success is inferred from this software latch.
    */

uint f33_admit_delayed_status_bit_triplet_a(void)

{
  uint32_t puVar1;
  uint uVar2;
  ushort uVar3;
  
  uVar3 = DAT_febe67a8;
  puVar1 = 0xfebeb800u;
  uVar2 = (uint)DAT_febe67a4;
  if (uVar2 != 0x5a) {
    if (DAT_febe67a8 < DAT_0002b6d8) {
      uVar3 = DAT_febe67a8 + 1;
    }
    else {
      puVar1 = 0xfebeb800u;
      if ((DAT_febe6764 & 1) == 0) {
        puVar1 = 0xfebeb800u;
        f33_set_output_request_word((uchar)(DAT_febe6764 & 1),DAT_febe6764 & 1);
        f33_set_direct_output_codes_bank0((ushort *)((undefined *)camry_host_ptr(0x2b6dau)));
        f33_request_direct_output_bank0();
      }
      uVar2 = 0x5a;
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x505c))))) = (char)uVar2;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x5058)))) = uVar3;
  return uVar2;
}



/* No-argument configured classifier. Gate baseline_one: requested==0 && observed==0 &&
   bit(6620,b+2)==1 && bit(661C,b+2)==1 && bit(6628,b+1)==0 && bit(6614,0)==1 &&65F0==5A. Closed
   gate returns44, otherwise22 iff scratch_byte==5A, else11. Full threshold partitions preserved in
   ROM. No physical units/source identity asserted. */

uint f33_classify_delayed_status_bit_triplet_a(void)

{
  if ((((DAT_febe64d8 == '\0') && (DAT_febe64d0 == '\0')) && ((DAT_febe6620 >> 2 & 1) != 0)) &&
     ((((DAT_febe661c >> 2 & 1) != 0 && ((DAT_febe6628 >> 1 & 1) == 0)) &&
      (((DAT_febe6614 & 1) != 0 && (DAT_febe65f0 == 'Z')))))) {
    if (DAT_febe75b4 != 'Z') {
      return 0x11;
    }
    return 0x22;
  }
  return 0x44;
}



/* Set healthy-observed6120 bit via51E2C; does not clear current/retained diagnostic failure. Event
   selection is mutable source scratch before each engine invocation. */

void f33_record_delayed_status_bit_triplet_a_healthy_observed(void)

{
  f33_report_diagnostic_healthy_observed((uint)DAT_febe75b6);
  return;
}



/* Call51C66(event,32 hex); diagnostic lifecycle rejection is separate from later control-action
   publication. Event selection is mutable source scratch before each engine invocation. */

void f33_record_delayed_status_bit_triplet_a_failure(void)

{
  f33_report_diagnostic_event_failure((uint)DAT_febe75b6,0x32);
  return;
}



/* Return readiness latch in r10:5A means admitted, not a void side-effect-only helper. Retain
   completed latch until explicit stage initializer; pending sequencing and counts per
   configured-family readiness contract. No hardware success is inferred from this software latch.
    */

uint f33_admit_delayed_status_bit_triplet_b(void)

{
  uint32_t puVar1;
  uint uVar2;
  ushort uVar3;
  
  uVar3 = DAT_febe67b0;
  puVar1 = 0xfebeb800u;
  uVar2 = (uint)DAT_febe67ac;
  if (uVar2 != 0x5a) {
    if (DAT_febe67b0 < DAT_0002b6e4) {
      uVar3 = DAT_febe67b0 + 1;
    }
    else {
      puVar1 = 0xfebeb800u;
      if ((DAT_febe6764 & 2) == 0) {
        puVar1 = 0xfebeb800u;
        f33_set_output_request_word('\x01',DAT_febe6764 & 2);
        f33_set_direct_output_codes_bank1((ushort *)((undefined *)camry_host_ptr(0x2b6e6u)));
        f33_request_direct_output_bank1();
      }
      uVar2 = 0x5a;
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5054))))) = (char)uVar2;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x5050)))) = uVar3;
  return uVar2;
}



/* No-argument configured classifier. Gate baseline_one: requested==0 && observed==0 &&
   bit(6620,b+2)==1 && bit(661C,b+2)==1 && bit(6628,b+1)==0 && bit(6614,0)==1 &&65F0==5A. Closed
   gate returns44, otherwise22 iff scratch_byte==5A, else11. Full threshold partitions preserved in
   ROM. No physical units/source identity asserted. */

uint f33_classify_delayed_status_bit_triplet_b(void)

{
  if ((((DAT_febe64d9 == '\0') && (DAT_febe64d1 == '\0')) && ((DAT_febe6620 >> 0x12 & 1) != 0)) &&
     ((((DAT_febe661c >> 0x12 & 1) != 0 && ((DAT_febe6628 >> 0x11 & 1) == 0)) &&
      (((DAT_febe6614 & 1) != 0 && (DAT_febe65f0 == 'Z')))))) {
    if (DAT_febe75d0 != 'Z') {
      return 0x11;
    }
    return 0x22;
  }
  return 0x44;
}



/* Set healthy-observed6120 bit via51E2C; does not clear current/retained diagnostic failure. Event
   selection is mutable source scratch before each engine invocation. */

void f33_record_delayed_status_bit_triplet_b_healthy_observed(void)

{
  f33_report_diagnostic_healthy_observed((uint)DAT_febe75d2);
  return;
}



/* Call51C66(event,32 hex); diagnostic lifecycle rejection is separate from later control-action
   publication. Event selection is mutable source scratch before each engine invocation. */

void f33_record_delayed_status_bit_triplet_b_failure(void)

{
  f33_report_diagnostic_event_failure((uint)DAT_febe75d2,0x32);
  return;
}



/* No-argument configured classifier. Gate off_both2: requested==2 &&observed==2
   &&(6620&(6<<b))==(4<<b) &&(661C&(6<<b))==(4<<b) &&bit(6628,b+1)==0 &&6614.bit0==0 &&
   own65F6/65F7==5A. Closed gate returns44, otherwise22 iff scratch_byte==5A, else11. Full threshold
   partitions preserved in ROM. No physical units/source identity asserted. */

uint f33_classify_matched_state2_status_bit_triplet_a(void)

{
  if ((((((DAT_febe64d8 == '\x02') && (DAT_febe64d0 == '\x02')) && ((DAT_febe6620 >> 1 & 1) == 0))
       && (((DAT_febe6620 >> 2 & 1) != 0 && ((DAT_febe661c >> 1 & 1) == 0)))) &&
      (((DAT_febe661c >> 2 & 1) != 0 &&
       (((DAT_febe6628 >> 1 & 1) == 0 && ((DAT_febe6614 & 1) == 0)))))) && (DAT_febe65f6 == 'Z')) {
    if (DAT_febe75ec != 'Z') {
      return 0x11;
    }
    return 0x22;
  }
  return 0x44;
}



/* Set healthy-observed6120 bit via51E2C; does not clear current/retained diagnostic failure. Event
   selection is mutable source scratch before each engine invocation. */

void f33_record_matched_state2_status_bit_triplet_a_healthy_observed(void)

{
  f33_report_diagnostic_healthy_observed((uint)DAT_febe75ee);
  return;
}



/* Call51C66(event,32 hex); diagnostic lifecycle rejection is separate from later control-action
   publication. Event selection is mutable source scratch before each engine invocation. */

void f33_record_matched_state2_status_bit_triplet_a_failure(void)

{
  f33_report_diagnostic_event_failure((uint)DAT_febe75ee,0x32);
  return;
}



/* No-argument configured classifier. Gate off_both2: requested==2 &&observed==2
   &&(6620&(6<<b))==(4<<b) &&(661C&(6<<b))==(4<<b) &&bit(6628,b+1)==0 &&6614.bit0==0 &&
   own65F6/65F7==5A. Closed gate returns44, otherwise22 iff scratch_byte==5A, else11. Full threshold
   partitions preserved in ROM. No physical units/source identity asserted. */

uint f33_classify_matched_state2_status_bit_triplet_b(void)

{
  if ((((((DAT_febe64d9 == '\x02') && (DAT_febe64d1 == '\x02')) && ((DAT_febe6620 >> 0x11 & 1) == 0)
        ) && (((DAT_febe6620 >> 0x12 & 1) != 0 && ((DAT_febe661c >> 0x11 & 1) == 0)))) &&
      (((DAT_febe661c & 0x40000) != 0 &&
       (((DAT_febe6628 >> 0x11 & 1) == 0 && ((DAT_febe6614 & 1) == 0)))))) && (DAT_febe65f7 == 'Z'))
  {
    if (DAT_febe7608 != 'Z') {
      return 0x11;
    }
    return 0x22;
  }
  return 0x44;
}



/* Set healthy-observed6120 bit via51E2C; does not clear current/retained diagnostic failure. Event
   selection is mutable source scratch before each engine invocation. */

void f33_record_matched_state2_status_bit_triplet_b_healthy_observed(void)

{
  f33_report_diagnostic_healthy_observed((uint)DAT_febe760a);
  return;
}



/* Call51C66(event,32 hex); diagnostic lifecycle rejection is separate from later control-action
   publication. Event selection is mutable source scratch before each engine invocation. */

void f33_record_matched_state2_status_bit_triplet_b_failure(void)

{
  f33_report_diagnostic_event_failure((uint)DAT_febe760a,0x32);
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_3ef18(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_3ef1a(void)

{
  return;
}



/* 3EFD4\u21923EF1C evaluates27 per-root getters of FAIL COUNTS at state+4 (not status),
   then530FC(9,11) if any fail count nonzero. A first failing observation makes this summary11
   before status22 confirmation. UnknownFF with zero failure count does not. Inadmissible44
   preserves nonzero fail counts and therefore summary; explicit reset clears them. 3EFD4→3EF1C
   evaluates27 per-root getters of FAIL COUNTS at state+4 (not status), then530FC(9,11) if any fail
   count nonzero. */

void f33_publish_configured_monitor_failure_count_summary(void)

{
  uchar status;
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  int iVar10;
  int iVar11;
  int iVar12;
  int iVar13;
  int iVar14;
  int iVar15;
  int iVar16;
  int iVar17;
  int iVar18;
  int iVar19;
  int iVar20;
  int iVar21;
  int iVar22;
  int iVar23;
  int iVar24;
  int iVar25;
  int iVar26;
  int iVar27;
  
  iVar1 = f33_status_failing_sample_difference_window_a_states();
  iVar2 = f33_status_failing_sample_difference_window_b_states();
  iVar3 = f33_status_failing_baseline_sample_threshold_a_states();
  iVar4 = f33_status_failing_baseline_sample_threshold_b_states();
  iVar5 = f33_status_failing_requested_state_sample_threshold_a_states();
  iVar6 = f33_status_failing_requested_state_sample_threshold_b_states();
  iVar7 = FUN_00041788();
  iVar8 = FUN_000419c0();
  iVar9 = FUN_0003e7f8();
  iVar10 = FUN_0003ea96();
  iVar11 = f33_status_failing_observed_state_sample_regions_a_states();
  iVar12 = f33_status_failing_observed_state_sample_regions_b_states();
  iVar13 = f33_status_failing_coupled_sample_threshold_both_states();
  iVar14 = f33_status_failing_asserted_state_sample_threshold_a_states();
  iVar15 = f33_status_failing_asserted_state_sample_threshold_b_states();
  iVar16 = f33_status_failing_matched_state2_status_bit_a_states();
  iVar17 = f33_status_failing_matched_state2_status_bit_b_states();
  iVar18 = FUN_000412e2();
  iVar19 = FUN_00041550();
  iVar20 = FUN_00041bf0();
  iVar21 = FUN_00041e24();
  iVar22 = FUN_0003ecc6();
  iVar23 = FUN_0003eefa();
  iVar24 = f33_status_failing_bounded_sample_or_status_a_states();
  iVar25 = f33_status_failing_bounded_sample_or_status_b_states();
  iVar26 = f33_status_failing_command_status_bit_clear_a_states();
  iVar27 = f33_status_failing_command_status_bit_clear_b_states();
  status = '\0';
  if ((((((((((((((((((((((((((iVar1 != 0 || iVar2 != 0) || iVar3 != 0) || iVar4 != 0) || iVar5 != 0
                           ) || iVar6 != 0) || iVar7 != 0) || iVar8 != 0) || iVar9 != 0) ||
                      iVar10 != 0) || iVar11 != 0) || iVar12 != 0) || iVar13 != 0) || iVar14 != 0)
                 || iVar15 != 0) || iVar16 != 0) || iVar17 != 0) || iVar18 != 0) || iVar19 != 0) ||
            iVar20 != 0) || iVar21 != 0) || iVar22 != 0) || iVar23 != 0) || iVar24 != 0) ||
       iVar25 != 0) || iVar26 != 0) || iVar27 != 0) {
    status = '\x11';
  }
  f33_set_diagnostic_cache_blocker('\t',status);
  return;
}



void FUN_0003efd4(void)

{
  f33_publish_configured_monitor_failure_count_summary();
  return;
}



undefined4 FUN_0003f010(void)

{
  ushort uVar1;
  uint32_t puVar2;
  undefined4 uVar3;
  ushort uVar4;
  
  uVar4 = DAT_febe67c0;
  uVar1 = DAT_febe6764;
  puVar2 = 0xfebeb800u;
  if (DAT_febe67c0 < DAT_0002b6fa) {
    uVar3 = 0;
    uVar4 = DAT_febe67c0 + 1;
  }
  else {
    puVar2 = 0xfebeb800u;
    if ((DAT_febe6764 & 1) == 0) {
      puVar2 = 0xfebeb800u;
      FUN_00056e66(DAT_febe6764 & 1,2);
      FUN_00056f14(0,4);
    }
    if ((uVar1 >> 1 & 1) == 0) {
      FUN_00056e66(1,0x20000);
      FUN_00056f14(1,0x40000);
    }
    uVar3 = 1;
  }
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x5040)))) = uVar4;
  return uVar3;
}



undefined4 FUN_0003f066(void)

{
  ushort uVar1;
  uint32_t puVar2;
  undefined4 uVar3;
  ushort uVar4;
  
  uVar4 = DAT_febe67c2;
  uVar1 = DAT_febe6764;
  puVar2 = 0xfebeb800u;
  if (DAT_febe67c2 < DAT_0002b6fc) {
    uVar3 = 1;
    uVar4 = DAT_febe67c2 + 1;
  }
  else {
    puVar2 = 0xfebeb800u;
    if ((DAT_febe6764 & 1) == 0) {
      puVar2 = 0xfebeb800u;
      FUN_00056c26(DAT_febe6764 & 1,2);
    }
    if ((uVar1 >> 1 & 1) == 0) {
      FUN_00056c26(1,0x20000);
    }
    uVar3 = 2;
  }
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x503e)))) = uVar4;
  return uVar3;
}



undefined4 FUN_0003f0aa(void)

{
  undefined4 uVar1;
  
  uVar1 = 2;
  if (DAT_febe67c4 < DAT_0002b6fe) {
    DAT_febe67c4 = DAT_febe67c4 + 1;
  }
  else {
    uVar1 = 3;
  }
  return uVar1;
}



/* Return readiness latch in r10:5A means admitted, not a void side-effect-only helper. Retain
   completed latch until explicit stage initializer; pending sequencing and counts per
   configured-family readiness contract. No hardware success is inferred from this software latch.
    */

uint f33_admit_coupled_sample_monitor(void)

{
  ushort uVar1;
  undefined *puVar2;
  uint uVar3;
  int iVar4;
  uint uVar5;
  ushort uVar6;
  
  puVar2 = ((undefined *)camry_host_ptr(0xfebeb800u));
  uVar5 = (uint)DAT_febe67bd;
  uVar3 = (uint)DAT_febe67bc;
  uVar6 = DAT_febe67be;
  if (uVar5 != 0x5a) {
    uVar1 = DAT_0002b6f8;
    if ((DAT_febe6764 & 3) == 0) {
      uVar1 = DAT_0002b6f6;
    }
    if (uVar1 < DAT_febe67be) {
      iVar4 = 0x5a;
    }
    else {
      iVar4 = 0;
      uVar6 = DAT_febe67be + 1;
    }
    if ((3 < uVar3) || (puVar2 = ((undefined *)camry_host_ptr(0xfebeb800u)), uVar3 == 0)) {
      puVar2 = ((undefined *)camry_host_ptr(0xfebeb800u));
      uVar3 = FUN_0003f010();
    }
    if (uVar3 == 1) {
      uVar3 = FUN_0003f066();
    }
    if (uVar3 == 2) {
      uVar3 = FUN_0003f0aa();
    }
    if ((iVar4 == 0x5a) && (uVar3 == 3)) {
      uVar5 = 0x5a;
    }
  }
  puVar2[-0x5044] = (char)uVar3;
  puVar2[-0x5043] = (char)uVar5;
  *(ushort *)(puVar2 + -0x5042) = uVar6;
  return uVar5;
}



/* No-argument configured classifier. Gate coupled: 64D8==2 &&64D9==2 &&64D0==0 &&64D1==0
   &&(6620&60006)==20002 &&(661C&40004)==40004 &&(6628&20002)==20002 &&6614.bit0==0 &&65F0==5A; hex
   masks. Closed gate returns44, otherwise22 iff 66B2<1326 &&66B4<1326 (configured equal threshold
   pairs;66B8 partition3328 covers all values), else11. Full threshold partitions preserved in ROM.
   No physical units/source identity asserted. */

uint f33_classify_coupled_sample_threshold_both(void)

{
  if ((((((DAT_febe64d8 != '\x02') || (DAT_febe64d9 != '\x02')) || (DAT_febe64d0 != '\0')) ||
       ((DAT_febe64d1 != '\0' || ((DAT_febe6620 >> 1 & 1) == 0)))) ||
      (((DAT_febe6620 >> 2 & 1) != 0 ||
       (((DAT_febe6620 >> 0x11 & 1) == 0 || ((DAT_febe6620 >> 0x12 & 1) != 0)))))) ||
     (((DAT_febe661c >> 2 & 1) == 0 ||
      (((((DAT_febe661c & 0x40000) == 0 || ((DAT_febe6628 >> 1 & 1) == 0)) ||
        ((DAT_febe6628 >> 0x11 & 1) == 0)) || (((DAT_febe6614 & 1) != 0 || (DAT_febe65f0 != 'Z')))))
      ))) {
    return 0x44;
  }
  if (((DAT_0002b702 <= DAT_febe66b2) ||
      ((DAT_0002b704 <= DAT_febe66b4 || (DAT_0002b700 < DAT_febe66b8)))) &&
     ((DAT_0002b708 <= DAT_febe66b2 ||
      ((DAT_0002b706 <= DAT_febe66b4 || (DAT_febe66b8 <= DAT_0002b700)))))) {
    return 0x11;
  }
  return 0x22;
}



/* Set healthy-observed6120 bit via51E2C; does not clear current/retained diagnostic failure. Event
   selection 0x60,0x61. */

void f33_record_coupled_sample_threshold_both_healthy_observed(void)

{
  f33_report_diagnostic_healthy_observed(0x60);
  f33_report_diagnostic_healthy_observed(0x61);
  return;
}



/* Call51C66(event,32 hex); diagnostic lifecycle rejection is separate from later control-action
   publication. Event selection 0x60,0x61. */

void f33_record_coupled_sample_threshold_both_failure(void)

{
  f33_report_diagnostic_event_failure(0x60,0x32);
  f33_report_diagnostic_event_failure(0x61,0x32);
  return;
}



undefined4 FUN_0003f2f6(void)

{
  ushort uVar1;
  uint32_t puVar2;
  undefined4 uVar3;
  ushort uVar4;
  
  uVar4 = DAT_febe67ca;
  uVar1 = DAT_febe6764;
  puVar2 = 0xfebeb800u;
  if (DAT_febe67ca < DAT_0002b70a) {
    uVar3 = 0;
    uVar4 = DAT_febe67ca + 1;
  }
  else {
    puVar2 = 0xfebeb800u;
    FUN_00050c82(0,0);
    if ((uVar1 & 1) == 0) {
      FUN_00056cda(uVar1 & 1,2);
    }
    uVar3 = 1;
  }
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x5036)))) = uVar4;
  return uVar3;
}



undefined4 FUN_0003f334(void)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  iVar3 = 0;
  uVar1 = 1;
  iVar2 = 0;
  if (DAT_febe67cc < DAT_0002b70c) {
    iVar4 = 0;
    DAT_febe67cc = DAT_febe67cc + 1;
  }
  else {
    iVar4 = 0x5a;
  }
  if (DAT_febe67ce < DAT_0002b70e) {
    DAT_febe67ce = DAT_febe67ce + 1;
  }
  else {
    iVar3 = 0x5a;
  }
  if (DAT_febe67d0 < DAT_0002b710) {
    DAT_febe67d0 = DAT_febe67d0 + 1;
  }
  else {
    iVar2 = 0x5a;
  }
  if ((iVar4 == 0x5a) && (iVar3 == 0x5a)) {
    if (iVar2 == 0x5a) {
      uVar1 = 2;
    }
    else {
      uVar1 = 1;
    }
  }
  return uVar1;
}



/* Return readiness latch in r10:5A means admitted, not a void side-effect-only helper. Retain
   completed latch until explicit stage initializer; pending sequencing and counts per
   configured-family readiness contract. No hardware success is inferred from this software latch.
    */

uint f33_admit_command_status_monitor_a(void)

{
  undefined *puVar1;
  uint uVar2;
  uint uVar3;
  
  puVar1 = ((undefined *)camry_host_ptr(0xfebeb800u));
  uVar3 = (uint)DAT_febe67c9;
  uVar2 = (uint)DAT_febe67c8;
  if (uVar3 != 0x5a) {
    if ((2 < uVar2) || (puVar1 = ((undefined *)camry_host_ptr(0xfebeb800u)), uVar2 == 0)) {
      puVar1 = ((undefined *)camry_host_ptr(0xfebeb800u));
      uVar2 = FUN_0003f2f6();
    }
    if (uVar2 == 1) {
      uVar2 = FUN_0003f334();
    }
    if (uVar2 == 2) {
      uVar3 = 0x5a;
    }
  }
  puVar1[-0x5038] = (char)uVar2;
  puVar1[-0x5037] = (char)uVar3;
  return uVar3;
}



/* No-argument configured classifier. Gate baseline_zero: same as baseline_one except6614.bit0==0.
   Closed gate returns44, otherwise22 iff 8291==0, else11. Full threshold partitions preserved in
   ROM. No physical units/source identity asserted. */

uint f33_classify_command_status_bit_clear_a(void)

{
  if ((((DAT_febe64d8 == '\0') && (DAT_febe64d0 == '\0')) && ((DAT_febe6620 >> 2 & 1) != 0)) &&
     ((((DAT_febe661c >> 2 & 1) != 0 && ((DAT_febe6628 >> 1 & 1) == 0)) &&
      (((DAT_febe6614 & 1) == 0 && (DAT_febe65f0 == 'Z')))))) {
    if (DAT_febe8291 != '\0') {
      return 0x11;
    }
    return 0x22;
  }
  return 0x44;
}



/* Set healthy-observed6120 bit via51E2C; does not clear current/retained diagnostic failure. Event
   selection 0x74. */

void f33_record_command_status_bit_clear_a_healthy_observed(void)

{
  f33_report_diagnostic_healthy_observed(0x74);
  return;
}



/* Call51C66(event,32 hex); diagnostic lifecycle rejection is separate from later control-action
   publication. Event selection 0x74. */

void f33_record_command_status_bit_clear_a_failure(void)

{
  f33_report_diagnostic_event_failure(0x74,0x32);
  return;
}



undefined4 FUN_0003f50c(void)

{
  ushort uVar1;
  uint32_t puVar2;
  undefined4 uVar3;
  ushort uVar4;
  
  uVar4 = DAT_febe67d6;
  uVar1 = DAT_febe6764;
  puVar2 = 0xfebeb800u;
  if (DAT_febe67d6 < DAT_0002b712) {
    uVar3 = 0;
    uVar4 = DAT_febe67d6 + 1;
  }
  else {
    puVar2 = 0xfebeb800u;
    FUN_00050c82(1,0);
    if ((uVar1 >> 1 & 1) == 0) {
      FUN_00056cda(1,0x20000);
    }
    uVar3 = 1;
  }
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x502a)))) = uVar4;
  return uVar3;
}



undefined4 FUN_0003f54a(void)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  iVar3 = 0;
  uVar1 = 1;
  iVar2 = 0;
  if (DAT_febe67d8 < DAT_0002b714) {
    iVar4 = 0;
    DAT_febe67d8 = DAT_febe67d8 + 1;
  }
  else {
    iVar4 = 0x5a;
  }
  if (DAT_febe67da < DAT_0002b716) {
    DAT_febe67da = DAT_febe67da + 1;
  }
  else {
    iVar3 = 0x5a;
  }
  if (DAT_febe67dc < DAT_0002b718) {
    DAT_febe67dc = DAT_febe67dc + 1;
  }
  else {
    iVar2 = 0x5a;
  }
  if ((iVar4 == 0x5a) && (iVar3 == 0x5a)) {
    if (iVar2 == 0x5a) {
      uVar1 = 2;
    }
    else {
      uVar1 = 1;
    }
  }
  return uVar1;
}



/* Return readiness latch in r10:5A means admitted, not a void side-effect-only helper. Retain
   completed latch until explicit stage initializer; pending sequencing and counts per
   configured-family readiness contract. No hardware success is inferred from this software latch.
    */

uint f33_admit_command_status_monitor_b(void)

{
  undefined *puVar1;
  uint uVar2;
  uint uVar3;
  
  puVar1 = ((undefined *)camry_host_ptr(0xfebeb800u));
  uVar3 = (uint)DAT_febe67d5;
  uVar2 = (uint)DAT_febe67d4;
  if (uVar3 != 0x5a) {
    if ((2 < uVar2) || (puVar1 = ((undefined *)camry_host_ptr(0xfebeb800u)), uVar2 == 0)) {
      puVar1 = ((undefined *)camry_host_ptr(0xfebeb800u));
      uVar2 = FUN_0003f50c();
    }
    if (uVar2 == 1) {
      uVar2 = FUN_0003f54a();
    }
    if (uVar2 == 2) {
      uVar3 = 0x5a;
    }
  }
  puVar1[-0x502c] = (char)uVar2;
  puVar1[-0x502b] = (char)uVar3;
  return uVar3;
}



/* No-argument configured classifier. Gate baseline_zero: same as baseline_one except6614.bit0==0.
   Closed gate returns44, otherwise22 iff 8292==0, else11. Full threshold partitions preserved in
   ROM. No physical units/source identity asserted. */

uint f33_classify_command_status_bit_clear_b(void)

{
  if ((((DAT_febe64d9 == '\0') && (DAT_febe64d1 == '\0')) && ((DAT_febe6620 >> 0x12 & 1) != 0)) &&
     ((((DAT_febe661c >> 0x12 & 1) != 0 && ((DAT_febe6628 >> 0x11 & 1) == 0)) &&
      (((DAT_febe6614 & 1) == 0 && (DAT_febe65f0 == 'Z')))))) {
    if (DAT_febe8292 != '\0') {
      return 0x11;
    }
    return 0x22;
  }
  return 0x44;
}



/* Set healthy-observed6120 bit via51E2C; does not clear current/retained diagnostic failure. Event
   selection 0x75. */

void f33_record_command_status_bit_clear_b_healthy_observed(void)

{
  f33_report_diagnostic_healthy_observed(0x75);
  return;
}



/* Call51C66(event,32 hex); diagnostic lifecycle rejection is separate from later control-action
   publication. Event selection 0x75. */

void f33_record_command_status_bit_clear_b_failure(void)

{
  f33_report_diagnostic_event_failure(0x75,0x32);
  return;
}



/* Return readiness latch in r10:5A means admitted, not a void side-effect-only helper. Retain
   completed latch until explicit stage initializer; pending sequencing and counts per
   configured-family readiness contract. No hardware success is inferred from this software latch.
    */

uint f33_admit_bounded_sample_monitor_a(void)

{
  uint uVar1;
  
  uVar1 = (uint)DAT_febe67e0;
  if (uVar1 != 0x5a) {
    if (DAT_febe67e2 < DAT_0002b71c) {
      DAT_febe67e2 = DAT_febe67e2 + 1;
    }
    else {
      uVar1 = 0x5a;
    }
  }
  DAT_febe67e0 = (char)uVar1;
  return uVar1;
}



/* No-argument configured classifier. Gate baseline_zero: same as baseline_one except6614.bit0==0.
   Closed gate returns44, otherwise22 iff 66BC<351 || 8284==5A, else11. Full threshold partitions
   preserved in ROM. No physical units/source identity asserted. */

uint f33_classify_bounded_sample_or_status_a(void)

{
  uint uVar1;
  
  if (((((DAT_febe64d8 == '\0') && (DAT_febe64d0 == '\0')) && ((DAT_febe6620 >> 2 & 1) != 0)) &&
      (((DAT_febe661c >> 2 & 1) != 0 && ((DAT_febe6628 >> 1 & 1) == 0)))) &&
     (((DAT_febe6614 & 1) == 0 && (DAT_febe65f0 == 'Z')))) {
    if ((DAT_febe66bc < DAT_0002b71a) || (DAT_febe8284 == 'Z')) {
      uVar1 = 0x22;
    }
    else {
      uVar1 = 0x11;
    }
  }
  else {
    DAT_febe67e4 = DAT_febe67e4 + 1;
    uVar1 = 0x44;
  }
  return uVar1;
}



/* Set healthy-observed6120 bit via51E2C; does not clear current/retained diagnostic failure. Event
   selection 0x89. */

void f33_record_bounded_sample_or_status_a_healthy_observed(void)

{
  f33_report_diagnostic_healthy_observed(0x89);
  return;
}



/* Call51C66(event,32 hex); diagnostic lifecycle rejection is separate from later control-action
   publication. Event selection 0x89. */

void f33_record_bounded_sample_or_status_a_failure(void)

{
  f33_report_diagnostic_event_failure(0x89,0x32);
  return;
}



/* Return readiness latch in r10:5A means admitted, not a void side-effect-only helper. Retain
   completed latch until explicit stage initializer; pending sequencing and counts per
   configured-family readiness contract. No hardware success is inferred from this software latch.
    */

uint f33_admit_bounded_sample_monitor_b(void)

{
  uint uVar1;
  
  uVar1 = (uint)DAT_febe67e8;
  if (uVar1 != 0x5a) {
    if (DAT_febe67ea < DAT_0002b724) {
      DAT_febe67ea = DAT_febe67ea + 1;
    }
    else {
      uVar1 = 0x5a;
    }
  }
  DAT_febe67e8 = (char)uVar1;
  return uVar1;
}



/* No-argument configured classifier. Gate baseline_zero: same as baseline_one except6614.bit0==0.
   Closed gate returns44, otherwise22 iff 66BE<351 || 8283==5A, else11. Full threshold partitions
   preserved in ROM. No physical units/source identity asserted. */

uint f33_classify_bounded_sample_or_status_b(void)

{
  uint uVar1;
  
  if (((((DAT_febe64d9 == '\0') && (DAT_febe64d1 == '\0')) && ((DAT_febe6620 >> 0x12 & 1) != 0)) &&
      (((DAT_febe661c >> 0x12 & 1) != 0 && ((DAT_febe6628 >> 0x11 & 1) == 0)))) &&
     (((DAT_febe6614 & 1) == 0 && (DAT_febe65f0 == 'Z')))) {
    if ((DAT_febe66be < DAT_0002b722) || (DAT_febe8283 == 'Z')) {
      uVar1 = 0x22;
    }
    else {
      uVar1 = 0x11;
    }
  }
  else {
    DAT_febe67ec = DAT_febe67ec + 1;
    uVar1 = 0x44;
  }
  return uVar1;
}



/* Set healthy-observed6120 bit via51E2C; does not clear current/retained diagnostic failure. Event
   selection 0x8a. */

void f33_record_bounded_sample_or_status_b_healthy_observed(void)

{
  f33_report_diagnostic_healthy_observed(0x8a);
  return;
}



/* Call51C66(event,32 hex); diagnostic lifecycle rejection is separate from later control-action
   publication. Event selection 0x8a. */

void f33_record_bounded_sample_or_status_b_failure(void)

{
  f33_report_diagnostic_event_failure(0x8a,0x32);
  return;
}



bool FUN_0003fa36(void)

{
  bool bVar1;
  uint32_t puVar2;
  ushort uVar3;
  
  uVar3 = DAT_febe763e;
  puVar2 = 0xfebeb800u;
  bVar1 = DAT_febe763e < DAT_0002b72a;
  if (bVar1) {
    uVar3 = DAT_febe763e + 1;
  }
  else {
    puVar2 = 0xfebeb800u;
    f33_set_channel_owner_request('\0',0);
  }
  (*((ushort *)camry_host_ptr((uint32_t)((0xffffbe3eu + (uint32_t)((int)puVar2)))))) = uVar3;
  return !bVar1;
}



undefined4 FUN_0003fa62(void)

{
  undefined4 uVar1;
  
  uVar1 = 1;
  if (DAT_febe7640 < DAT_0002b72c) {
    DAT_febe7640 = DAT_febe7640 + 1;
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

uint f33_admit_requested_state_sample_monitor_a(void)

{
  undefined *puVar1;
  uint uVar2;
  uint uVar3;
  
  puVar1 = ((undefined *)camry_host_ptr(0xfebeb800u));
  uVar3 = (uint)DAT_febe763d;
  uVar2 = (uint)DAT_febe763c;
  if (uVar3 != 0x5a) {
    if ((2 < uVar2) || (puVar1 = ((undefined *)camry_host_ptr(0xfebeb800u)), uVar2 == 0)) {
      puVar1 = ((undefined *)camry_host_ptr(0xfebeb800u));
      uVar2 = FUN_0003fa36();
    }
    if (uVar2 == 1) {
      uVar2 = FUN_0003fa62();
    }
    if (uVar2 == 2) {
      uVar3 = 0x5a;
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbe3cu + (uint32_t)((int)camry_host_addr(puVar1)) * 1u)))) = (char)uVar2;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbe3du + (uint32_t)((int)camry_host_addr(puVar1)) * 1u)))) = (char)uVar3;
  return uVar3;
}



/* No-argument configured classifier. Gate requested2_one: requested==2 &&observed==0
   &&bit(6620,b+2)==1 &&bit(661C,b+2)==1 &&bit(6628,b+1)==0 &&6614.bit0==1 &&65F0==5A. Closed gate
   returns44, otherwise22 iff 66B2>1247 (both3328 partitions), else11. Full threshold partitions
   preserved in ROM. No physical units/source identity asserted. */

uint f33_classify_requested_state_sample_threshold_a(void)

{
  if (((((DAT_febe64d8 != '\x02') || (DAT_febe64d0 != '\0')) || ((DAT_febe6620 >> 2 & 1) == 0)) ||
      (((DAT_febe661c >> 2 & 1) == 0 || ((DAT_febe6628 >> 1 & 1) != 0)))) ||
     (((DAT_febe6614 & 1) == 0 || (DAT_febe65f0 != 'Z')))) {
    return 0x44;
  }
  if (((DAT_febe66b2 <= DAT_0002b730) || (DAT_0002b72e < DAT_febe66b8)) &&
     ((DAT_febe66b2 <= DAT_0002b732 || (DAT_febe66b8 <= DAT_0002b72e)))) {
    return 0x11;
  }
  return 0x22;
}



/* Set healthy-observed6120 bit via51E2C; does not clear current/retained diagnostic failure. Event
   selection 0xef. */

void f33_record_requested_state_sample_threshold_a_healthy_observed(void)

{
  f33_report_diagnostic_healthy_observed(0xef);
  return;
}



/* Call51C66(event,32 hex); diagnostic lifecycle rejection is separate from later control-action
   publication. Event selection 0xef. */

void f33_record_requested_state_sample_threshold_a_failure(void)

{
  f33_report_diagnostic_event_failure(0xef,0x32);
  return;
}



bool FUN_0003fc10(void)

{
  bool bVar1;
  uint32_t puVar2;
  ushort uVar3;
  
  uVar3 = DAT_febe764e;
  puVar2 = 0xfebeb800u;
  bVar1 = DAT_febe764e < DAT_0002b736;
  if (bVar1) {
    uVar3 = DAT_febe764e + 1;
  }
  else {
    puVar2 = 0xfebeb800u;
    f33_set_channel_owner_request('\x01',0);
  }
  (*((ushort *)camry_host_ptr((uint32_t)((0xffffbe4eu + (uint32_t)((int)puVar2)))))) = uVar3;
  return !bVar1;
}



undefined4 FUN_0003fc3c(void)

{
  undefined4 uVar1;
  
  uVar1 = 1;
  if (DAT_febe7650 < DAT_0002b738) {
    DAT_febe7650 = DAT_febe7650 + 1;
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

uint f33_admit_requested_state_sample_monitor_b(void)

{
  undefined *puVar1;
  uint uVar2;
  uint uVar3;
  
  puVar1 = ((undefined *)camry_host_ptr(0xfebeb800u));
  uVar3 = (uint)DAT_febe764d;
  uVar2 = (uint)DAT_febe764c;
  if (uVar3 != 0x5a) {
    if ((2 < uVar2) || (puVar1 = ((undefined *)camry_host_ptr(0xfebeb800u)), uVar2 == 0)) {
      puVar1 = ((undefined *)camry_host_ptr(0xfebeb800u));
      uVar2 = FUN_0003fc10();
    }
    if (uVar2 == 1) {
      uVar2 = FUN_0003fc3c();
    }
    if (uVar2 == 2) {
      uVar3 = 0x5a;
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbe4cu + (uint32_t)((int)camry_host_addr(puVar1)) * 1u)))) = (char)uVar2;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbe4du + (uint32_t)((int)camry_host_addr(puVar1)) * 1u)))) = (char)uVar3;
  return uVar3;
}



/* No-argument configured classifier. Gate requested2_one: requested==2 &&observed==0
   &&bit(6620,b+2)==1 &&bit(661C,b+2)==1 &&bit(6628,b+1)==0 &&6614.bit0==1 &&65F0==5A. Closed gate
   returns44, otherwise22 iff 66B4>1247 (both3328 partitions), else11. Full threshold partitions
   preserved in ROM. No physical units/source identity asserted. */

uint f33_classify_requested_state_sample_threshold_b(void)

{
  if (((((DAT_febe64d9 != '\x02') || (DAT_febe64d1 != '\0')) || ((DAT_febe6620 >> 0x12 & 1) == 0))
      || (((DAT_febe661c >> 0x12 & 1) == 0 || ((DAT_febe6628 >> 0x11 & 1) != 0)))) ||
     (((DAT_febe6614 & 1) == 0 || (DAT_febe65f0 != 'Z')))) {
    return 0x44;
  }
  if (((DAT_febe66b4 <= DAT_0002b73c) || (DAT_0002b73a < DAT_febe66b8)) &&
     ((DAT_febe66b4 <= DAT_0002b73e || (DAT_febe66b8 <= DAT_0002b73a)))) {
    return 0x11;
  }
  return 0x22;
}



/* Set healthy-observed6120 bit via51E2C; does not clear current/retained diagnostic failure. Event
   selection 0xf0. */

void f33_record_requested_state_sample_threshold_b_healthy_observed(void)

{
  f33_report_diagnostic_healthy_observed(0xf0);
  return;
}



/* Call51C66(event,32 hex); diagnostic lifecycle rejection is separate from later control-action
   publication. Event selection 0xf0. */

void f33_record_requested_state_sample_threshold_b_failure(void)

{
  f33_report_diagnostic_event_failure(0xf0,0x32);
  return;
}



/* No-argument configured classifier. Gate asserted_zero: requested==2 &&observed==0
   &&(6620&(6<<b))==(2<<b) &&bit(661C,b+2)==1 &&bit(6628,b+1)==1 &&6614.bit0==0 &&65F0==5A. Closed
   gate returns44, otherwise22 iff 66B2<965 (configured equal thresholds in both3328 partitions),
   else11. Full threshold partitions preserved in ROM. No physical units/source identity asserted.
    */

uint f33_classify_asserted_state_sample_threshold_a(void)

{
  if (((((DAT_febe64d8 != '\x02') || (DAT_febe64d0 != '\0')) || ((DAT_febe6620 >> 1 & 1) == 0)) ||
      (((DAT_febe6620 >> 2 & 1) != 0 || ((DAT_febe661c >> 2 & 1) == 0)))) ||
     (((DAT_febe6628 >> 1 & 1) == 0 || (((DAT_febe6614 & 1) != 0 || (DAT_febe65f0 != 'Z')))))) {
    return 0x44;
  }
  if (((DAT_0002b744 <= DAT_febe66b2) || (DAT_0002b742 < DAT_febe66b8)) &&
     ((DAT_0002b746 <= DAT_febe66b2 || (DAT_febe66b8 <= DAT_0002b742)))) {
    return 0x11;
  }
  return 0x22;
}



/* Set healthy-observed6120 bit via51E2C; does not clear current/retained diagnostic failure. Event
   selection 0x9d. */

void f33_record_asserted_state_sample_threshold_a_healthy_observed(void)

{
  f33_report_diagnostic_healthy_observed(0x9d);
  return;
}



/* Call51C66(event,32 hex); diagnostic lifecycle rejection is separate from later control-action
   publication. Event selection 0x9d. */

void f33_record_asserted_state_sample_threshold_a_failure(void)

{
  f33_report_diagnostic_event_failure(0x9d,0x32);
  return;
}



/* No-argument configured classifier. Gate asserted_zero: requested==2 &&observed==0
   &&(6620&(6<<b))==(2<<b) &&bit(661C,b+2)==1 &&bit(6628,b+1)==1 &&6614.bit0==0 &&65F0==5A. Closed
   gate returns44, otherwise22 iff 66B4<965 (configured equal thresholds in both3328 partitions),
   else11. Full threshold partitions preserved in ROM. No physical units/source identity asserted.
    */

uint f33_classify_asserted_state_sample_threshold_b(void)

{
  if (((((DAT_febe64d9 != '\x02') || (DAT_febe64d1 != '\0')) || ((DAT_febe6620 >> 0x11 & 1) == 0))
      || (((DAT_febe6620 >> 0x12 & 1) != 0 || ((DAT_febe661c >> 0x12 & 1) == 0)))) ||
     (((DAT_febe6628 >> 0x11 & 1) == 0 || (((DAT_febe6614 & 1) != 0 || (DAT_febe65f0 != 'Z')))))) {
    return 0x44;
  }
  if (((DAT_0002b74c <= DAT_febe66b4) || (DAT_0002b74a < DAT_febe66b8)) &&
     ((DAT_0002b74e <= DAT_febe66b4 || (DAT_febe66b8 <= DAT_0002b74a)))) {
    return 0x11;
  }
  return 0x22;
}



/* Set healthy-observed6120 bit via51E2C; does not clear current/retained diagnostic failure. Event
   selection 0xc7. */

void f33_record_asserted_state_sample_threshold_b_healthy_observed(void)

{
  f33_report_diagnostic_healthy_observed(199);
  return;
}


