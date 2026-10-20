#include "common.h"

void apply_mode0204_entry_requests(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if ((DAT_febeb082 & 1) == 0) {
    puVar1 = 0xfebeb800u;
    set_output_request_word((uchar)(DAT_febeb082 & 1),DAT_febeb082 & 1);
    set_direct_output_codes_bank0((ushort *)((undefined *)camry_host_ptr(0xaf3deu)));
    request_direct_output_bank0();
    set_channel_owner_request('\0',2);
    thunk_set_priority_mask_8a9c_bounded2_56c26(0,4);
    thunk_set_secondary_channel_request_bounded5_56e66(0,2);
    thunk_set_secondary_priority_mask_bounded2_56f14(0,4);
    thunk_set_request_word_8a50_bounded5_569ac(0,0);
    thunk_set_request_word_8a2c_bounded5_568dc(0,2);
    thunk_set_indexed_status_mask_word_if_below_five_50c82(0,1);
    thunk_set_request_word_8aa8_bounded6_56cda(0,0xc);
  }
  if (((*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x77e)))) & 2) == 0) {
    set_output_request_word('\x01',(*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x77e)))) & 2);
    set_direct_output_codes_bank1((ushort *)((undefined *)camry_host_ptr(0xaf3deu)));
    request_direct_output_bank1();
    set_channel_owner_request('\x01',0x20000);
    thunk_set_priority_mask_8a9c_bounded2_56c26(1,0x40000);
    thunk_set_secondary_channel_request_bounded5_56e66(1,0x20000);
    thunk_set_secondary_priority_mask_bounded2_56f14(1,0x40000);
    thunk_set_request_word_8a50_bounded5_569ac(1,0);
    thunk_set_request_word_8a2c_bounded5_568dc(1,0x20000);
    thunk_set_indexed_status_mask_word_if_below_five_50c82(1,1);
    thunk_set_request_word_8aa8_bounded6_56cda(1,0xc0000);
  }
  thunk_set_request_word_8a48_bounded2_5693e(0,0);
  return;
}

void apply_mode0205_entry_requests(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if ((DAT_febeb082 & 1) == 0) {
    puVar1 = 0xfebeb800u;
    set_output_request_word((byte)DAT_febeb082 & 1,0x7001);
    clear_direct_output_bank0();
    set_channel_owner_request('\0',2);
    thunk_set_priority_mask_8a9c_bounded2_56c26(0,4);
    thunk_set_secondary_channel_request_bounded5_56e66(0,2);
    thunk_set_secondary_priority_mask_bounded2_56f14(0,4);
    thunk_set_request_word_8a50_bounded5_569ac(0,0);
    thunk_set_request_word_8a2c_bounded5_568dc(0,2);
    thunk_set_indexed_status_mask_word_if_below_five_50c82(0,1);
    thunk_set_request_word_8aa8_bounded6_56cda(0,0xc);
  }
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x77e))))) & 2) == 0) {
    set_output_request_word('\x01',0x70010000);
    clear_direct_output_bank1();
    set_channel_owner_request('\x01',0x20000);
    thunk_set_priority_mask_8a9c_bounded2_56c26(1,0x40000);
    thunk_set_secondary_channel_request_bounded5_56e66(1,0x20000);
    thunk_set_secondary_priority_mask_bounded2_56f14(1,0x40000);
    thunk_set_request_word_8a50_bounded5_569ac(1,0);
    thunk_set_request_word_8a2c_bounded5_568dc(1,0x20000);
    thunk_set_indexed_status_mask_word_if_below_five_50c82(1,1);
    thunk_set_request_word_8aa8_bounded6_56cda(1,0xc0000);
  }
  thunk_set_request_word_8a48_bounded2_5693e(0,0);
  return;
}

void apply_mode0206_entry_requests(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if ((DAT_febeb082 & 1) == 0) {
    puVar1 = 0xfebeb800u;
    set_output_request_word((byte)DAT_febeb082 & 1,0x7001);
    clear_direct_output_bank0();
    set_channel_owner_request('\0',2);
    thunk_set_priority_mask_8a9c_bounded2_56c26(0,4);
    thunk_set_secondary_channel_request_bounded5_56e66(0,2);
    thunk_set_secondary_priority_mask_bounded2_56f14(0,4);
    thunk_set_request_word_8a50_bounded5_569ac(0,0);
    thunk_set_request_word_8a2c_bounded5_568dc(0,2);
    thunk_set_indexed_status_mask_word_if_below_five_50c82(0,1);
    thunk_set_request_word_8aa8_bounded6_56cda(0,0xc);
  }
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x77e))))) & 2) == 0) {
    set_output_request_word('\x01',0x70010000);
    clear_direct_output_bank1();
    set_channel_owner_request('\x01',0x20000);
    thunk_set_priority_mask_8a9c_bounded2_56c26(1,0x40000);
    thunk_set_secondary_channel_request_bounded5_56e66(1,0x20000);
    thunk_set_secondary_priority_mask_bounded2_56f14(1,0x40000);
    thunk_set_request_word_8a50_bounded5_569ac(1,0);
    thunk_set_request_word_8a2c_bounded5_568dc(1,0x20000);
    thunk_set_indexed_status_mask_word_if_below_five_50c82(1,1);
    thunk_set_request_word_8aa8_bounded6_56cda(1,0xc0000);
  }
  thunk_set_request_word_8a48_bounded2_5693e(0,0);
  return;
}

void apply_mode0207_entry_requests(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if ((DAT_febeb082 & 1) == 0) {
    puVar1 = 0xfebeb800u;
    set_output_request_word((byte)DAT_febeb082 & 1,0x7001);
    clear_direct_output_bank0();
    set_channel_owner_request('\0',2);
    thunk_set_priority_mask_8a9c_bounded2_56c26(0,4);
    thunk_set_secondary_channel_request_bounded5_56e66(0,0);
    thunk_set_secondary_priority_mask_bounded2_56f14(0,0);
    thunk_set_request_word_8a50_bounded5_569ac(0,0);
    thunk_set_request_word_8a2c_bounded5_568dc(0,2);
    thunk_set_indexed_status_mask_word_if_below_five_50c82(0,0);
    thunk_set_request_word_8aa8_bounded6_56cda(0,0xc);
  }
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x77e))))) & 2) == 0) {
    set_output_request_word('\x01',0x70010000);
    clear_direct_output_bank1();
    set_channel_owner_request('\x01',0x20000);
    thunk_set_priority_mask_8a9c_bounded2_56c26(1,0x40000);
    thunk_set_secondary_channel_request_bounded5_56e66(1,0);
    thunk_set_secondary_priority_mask_bounded2_56f14(1,0);
    thunk_set_request_word_8a50_bounded5_569ac(1,0);
    thunk_set_request_word_8a2c_bounded5_568dc(1,0x20000);
    thunk_set_indexed_status_mask_word_if_below_five_50c82(1,0);
    thunk_set_request_word_8aa8_bounded6_56cda(1,0xc0000);
  }
  thunk_set_request_word_8a48_bounded2_5693e(0,0);
  return;
}

void apply_mode0208_entry_requests(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if ((DAT_febeb082 & 1) == 0) {
    puVar1 = 0xfebeb800u;
    set_output_request_word((byte)DAT_febeb082 & 1,0x7001);
    clear_direct_output_bank0();
    set_channel_owner_request('\0',0);
    thunk_set_priority_mask_8a9c_bounded2_56c26(0,0);
    thunk_set_secondary_channel_request_bounded5_56e66(0,0);
    thunk_set_secondary_priority_mask_bounded2_56f14(0,2);
    thunk_set_request_word_8a50_bounded5_569ac(0,2);
    thunk_set_request_word_8a2c_bounded5_568dc(0,2);
    thunk_set_indexed_status_mask_word_if_below_five_50c82(0,0);
    thunk_set_request_word_8aa8_bounded6_56cda(0,0xc);
  }
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x77e))))) & 2) == 0) {
    set_output_request_word('\x01',0x70010000);
    clear_direct_output_bank1();
    set_channel_owner_request('\x01',0);
    thunk_set_priority_mask_8a9c_bounded2_56c26(1,0);
    thunk_set_secondary_channel_request_bounded5_56e66(1,0);
    thunk_set_secondary_priority_mask_bounded2_56f14(1,0x20000);
    thunk_set_request_word_8a50_bounded5_569ac(1,0x20000);
    thunk_set_request_word_8a2c_bounded5_568dc(1,0x20000);
    thunk_set_indexed_status_mask_word_if_below_five_50c82(1,0);
    thunk_set_request_word_8aa8_bounded6_56cda(1,0xc0000);
  }
  thunk_set_request_word_8a48_bounded2_5693e(0,0);
  return;
}

void apply_mode0209_entry_requests(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if ((DAT_febeb082 & 1) == 0) {
    puVar1 = 0xfebeb800u;
    set_output_request_word((byte)DAT_febeb082 & 1,0x7001);
    clear_direct_output_bank0();
    set_channel_owner_request('\0',0);
    thunk_set_priority_mask_8a9c_bounded2_56c26(0,2);
    thunk_set_secondary_channel_request_bounded5_56e66(0,2);
    thunk_set_secondary_priority_mask_bounded2_56f14(0,4);
    thunk_set_request_word_8a50_bounded5_569ac(0,2);
    thunk_set_request_word_8a2c_bounded5_568dc(0,2);
    thunk_set_indexed_status_mask_word_if_below_five_50c82(0,0);
    thunk_set_request_word_8aa8_bounded6_56cda(0,0xc);
  }
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x77e))))) & 2) == 0) {
    set_output_request_word('\x01',0x70010000);
    clear_direct_output_bank1();
    set_channel_owner_request('\x01',0);
    thunk_set_priority_mask_8a9c_bounded2_56c26(1,0x20000);
    thunk_set_secondary_channel_request_bounded5_56e66(1,0x20000);
    thunk_set_secondary_priority_mask_bounded2_56f14(1,0x40000);
    thunk_set_request_word_8a50_bounded5_569ac(1,0x20000);
    thunk_set_request_word_8a2c_bounded5_568dc(1,0x20000);
    thunk_set_indexed_status_mask_word_if_below_five_50c82(1,0);
    thunk_set_request_word_8aa8_bounded6_56cda(1,0xc0000);
  }
  thunk_set_request_word_8a48_bounded2_5693e(0,0);
  return;
}

void apply_mode020a_entry_requests(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if ((DAT_febeb082 & 1) == 0) {
    puVar1 = 0xfebeb800u;
    set_output_request_word((byte)DAT_febeb082 & 1,0x7001);
    clear_direct_output_bank0();
    set_channel_owner_request('\0',0);
    thunk_set_priority_mask_8a9c_bounded2_56c26(0,0);
    thunk_set_secondary_channel_request_bounded5_56e66(0,0);
    thunk_set_secondary_priority_mask_bounded2_56f14(0,4);
    thunk_set_request_word_8a50_bounded5_569ac(0,0);
    thunk_set_request_word_8a2c_bounded5_568dc(0,2);
    thunk_set_indexed_status_mask_word_if_below_five_50c82(0,0);
    thunk_set_request_word_8aa8_bounded6_56cda(0,0xc);
  }
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x77e))))) & 2) == 0) {
    set_output_request_word('\x01',0x70010000);
    clear_direct_output_bank1();
    set_channel_owner_request('\x01',0);
    thunk_set_priority_mask_8a9c_bounded2_56c26(1,0);
    thunk_set_secondary_channel_request_bounded5_56e66(1,0);
    thunk_set_secondary_priority_mask_bounded2_56f14(1,0x40000);
    thunk_set_request_word_8a50_bounded5_569ac(1,0);
    thunk_set_request_word_8a2c_bounded5_568dc(1,0x20000);
    thunk_set_indexed_status_mask_word_if_below_five_50c82(1,0);
    thunk_set_request_word_8aa8_bounded6_56cda(1,0xc0000);
  }
  thunk_set_request_word_8a48_bounded2_5693e(0,3);
  return;
}

void apply_mode020b_entry_requests(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if ((DAT_febeb082 & 1) == 0) {
    puVar1 = 0xfebeb800u;
    set_output_request_word((byte)DAT_febeb082 & 1,0x7001);
    clear_direct_output_bank0();
    set_channel_owner_request('\0',0);
    thunk_set_priority_mask_8a9c_bounded2_56c26(0,4);
    thunk_set_secondary_channel_request_bounded5_56e66(0,0);
    thunk_set_secondary_priority_mask_bounded2_56f14(0,4);
    thunk_set_request_word_8a50_bounded5_569ac(0,0);
    thunk_set_request_word_8a2c_bounded5_568dc(0,2);
    thunk_set_indexed_status_mask_word_if_below_five_50c82(0,0);
    thunk_set_request_word_8aa8_bounded6_56cda(0,2);
  }
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x77e))))) & 2) == 0) {
    set_output_request_word('\x01',0x70010000);
    clear_direct_output_bank1();
    set_channel_owner_request('\x01',0);
    thunk_set_priority_mask_8a9c_bounded2_56c26(1,0x40000);
    thunk_set_secondary_channel_request_bounded5_56e66(1,0);
    thunk_set_secondary_priority_mask_bounded2_56f14(1,0x40000);
    thunk_set_request_word_8a50_bounded5_569ac(1,0);
    thunk_set_request_word_8a2c_bounded5_568dc(1,0x20000);
    thunk_set_indexed_status_mask_word_if_below_five_50c82(1,0);
    thunk_set_request_word_8aa8_bounded6_56cda(1,0x20000);
  }
  thunk_set_request_word_8a48_bounded2_5693e(0,3);
  return;
}

void apply_mode020c_entry_requests(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if ((DAT_febeb082 & 1) == 0) {
    puVar1 = 0xfebeb800u;
    set_output_request_word((byte)DAT_febeb082 & 1,1);
    set_direct_output_codes_bank0((ushort *)((undefined *)camry_host_ptr(0xaf3deu)));
    request_direct_output_bank0();
    set_channel_owner_request('\0',0);
    thunk_set_priority_mask_8a9c_bounded2_56c26(0,4);
    thunk_set_secondary_channel_request_bounded5_56e66(0,0);
    thunk_set_secondary_priority_mask_bounded2_56f14(0,4);
    thunk_set_request_word_8a50_bounded5_569ac(0,0);
    thunk_set_request_word_8a2c_bounded5_568dc(0,2);
    thunk_set_indexed_status_mask_word_if_below_five_50c82(0,0);
    thunk_set_request_word_8aa8_bounded6_56cda(0,2);
  }
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x77e))))) & 2) == 0) {
    set_output_request_word('\x01',0x10000);
    set_direct_output_codes_bank1((ushort *)((undefined *)camry_host_ptr(0xaf3deu)));
    request_direct_output_bank1();
    set_channel_owner_request('\x01',0);
    thunk_set_priority_mask_8a9c_bounded2_56c26(1,0x40000);
    thunk_set_secondary_channel_request_bounded5_56e66(1,0);
    thunk_set_secondary_priority_mask_bounded2_56f14(1,0x40000);
    thunk_set_request_word_8a50_bounded5_569ac(1,0);
    thunk_set_request_word_8a2c_bounded5_568dc(1,0x20000);
    thunk_set_indexed_status_mask_word_if_below_five_50c82(1,0);
    thunk_set_request_word_8aa8_bounded6_56cda(1,0x20000);
  }
  thunk_set_request_word_8a48_bounded2_5693e(0,3);
  return;
}

void apply_mode020d_entry_requests(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if ((DAT_febeb082 & 1) == 0) {
    puVar1 = 0xfebeb800u;
    set_output_request_word((byte)DAT_febeb082 & 1,1);
    set_direct_output_codes_bank0((ushort *)((undefined *)camry_host_ptr(0xaf3e4u)));
    request_direct_output_bank0();
    set_channel_owner_request('\0',0);
    thunk_set_priority_mask_8a9c_bounded2_56c26(0,4);
    thunk_set_secondary_channel_request_bounded5_56e66(0,0);
    thunk_set_secondary_priority_mask_bounded2_56f14(0,4);
    thunk_set_request_word_8a50_bounded5_569ac(0,0);
    thunk_set_request_word_8a2c_bounded5_568dc(0,2);
    thunk_set_indexed_status_mask_word_if_below_five_50c82(0,0);
    thunk_set_request_word_8aa8_bounded6_56cda(0,2);
  }
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x77e))))) & 2) == 0) {
    set_output_request_word('\x01',0x10000);
    set_direct_output_codes_bank1((ushort *)((undefined *)camry_host_ptr(0xaf3e4u)));
    request_direct_output_bank1();
    set_channel_owner_request('\x01',0);
    thunk_set_priority_mask_8a9c_bounded2_56c26(1,0x40000);
    thunk_set_secondary_channel_request_bounded5_56e66(1,0);
    thunk_set_secondary_priority_mask_bounded2_56f14(1,0x40000);
    thunk_set_request_word_8a50_bounded5_569ac(1,0);
    thunk_set_request_word_8a2c_bounded5_568dc(1,0x20000);
    thunk_set_indexed_status_mask_word_if_below_five_50c82(1,0);
    thunk_set_request_word_8aa8_bounded6_56cda(1,0x20000);
  }
  thunk_set_request_word_8a48_bounded2_5693e(0,3);
  return;
}

undefined4 complete_mode200_output_sequence(void)

{
  uint uVar1;
  
  clear_direct_output_enables();
  uVar1 = select_service_join_after_mode200();
  if (uVar1 != 1) {
    set_indexed_request_and_clear_complement_b15ac(6);
  }
  return set_indexed_request_and_clear_complement_b15ac(3);
}

void advance_mode200_output_sequence(void)

{
  uchar request_id;
  uint uVar1;
  
  switch(DAT_febeb11a) {
  case 0x200:
    uVar1 = probe_pending_mode_request('\x15');
    if (uVar1 == 1) {
      apply_mode0201_entry_requests();
      publish_live_application_mode(0x201);
    }
    request_id = '\x15';
    break;
  case 0x201:
    uVar1 = probe_pending_mode_request('\x16');
    if (uVar1 == 1) {
      apply_mode0202_entry_requests();
      publish_live_application_mode(0x202);
    }
    request_id = '\x16';
    break;
  case 0x202:
    uVar1 = probe_pending_mode_request('\x17');
    if (uVar1 == 1) {
      apply_mode0203_entry_requests();
      publish_live_application_mode(0x203);
    }
    request_id = '\x17';
    break;
  case 0x203:
    uVar1 = probe_pending_mode_request('\x18');
    if (uVar1 == 1) {
      apply_mode0204_entry_requests();
      publish_live_application_mode(0x204);
    }
    request_id = '\x18';
    break;
  case 0x204:
    uVar1 = probe_pending_mode_request('\x19');
    if (uVar1 == 1) {
      apply_mode0205_entry_requests();
      publish_live_application_mode(0x205);
    }
    request_id = '\x19';
    break;
  case 0x205:
    uVar1 = probe_pending_mode_request('\x1a');
    if (uVar1 == 1) {
      apply_mode0206_entry_requests();
      publish_live_application_mode(0x206);
    }
    request_id = '\x1a';
    break;
  case 0x206:
    uVar1 = probe_pending_mode_request('\x1b');
    if (uVar1 == 1) {
      apply_mode0207_entry_requests();
      publish_live_application_mode(0x207);
    }
    request_id = '\x1b';
    break;
  case 0x207:
    uVar1 = probe_pending_mode_request('\x1c');
    if (uVar1 == 1) {
      apply_mode0208_entry_requests();
      publish_live_application_mode(0x208);
    }
    request_id = '\x1c';
    break;
  case 0x208:
    uVar1 = probe_pending_mode_request('\x1d');
    if (uVar1 == 1) {
      apply_mode0209_entry_requests();
      publish_live_application_mode(0x209);
    }
    request_id = '\x1d';
    break;
  case 0x209:
    uVar1 = probe_pending_mode_request('\x1e');
    if (uVar1 == 1) {
      apply_mode020a_entry_requests();
      publish_live_application_mode(0x20a);
    }
    request_id = '\x1e';
    break;
  case 0x20a:
    uVar1 = probe_pending_mode_request('\x1f');
    if (uVar1 == 1) {
      apply_mode020b_entry_requests();
      publish_live_application_mode(0x20b);
    }
    request_id = '\x1f';
    break;
  case 0x20b:
    uVar1 = probe_pending_mode_request(' ');
    if (uVar1 == 1) {
      apply_mode020c_entry_requests();
      publish_live_application_mode(0x20c);
    }
    request_id = ' ';
    break;
  case 0x20c:
    uVar1 = probe_pending_mode_request('!');
    if (uVar1 == 1) {
      apply_mode020d_entry_requests();
      publish_live_application_mode(0x20d);
    }
    request_id = '!';
    break;
  case 0x20d:
    uVar1 = probe_pending_mode_request('\"');
    if (uVar1 == 1) {
      complete_mode200_output_sequence();
    }
    request_id = '\"';
    break;
  default:
    goto switchD_000b2830_default;
  }
  acknowledge_selected_mode_request(request_id);
switchD_000b2830_default:
  return;
}

void reset_unmasked_output_bank_requests_b29fa(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if ((DAT_febeb082 & 1) == 0) {
    puVar1 = 0xfebeb800u;
    set_output_request_word((byte)DAT_febeb082 & 1,0x7001);
    clear_direct_output_bank0();
    set_channel_owner_request('\0',2);
    thunk_set_priority_mask_8a9c_bounded2_56c26(0,4);
    thunk_set_secondary_channel_request_bounded5_56e66(0,2);
    thunk_set_secondary_priority_mask_bounded2_56f14(0,4);
    thunk_set_request_word_8a50_bounded5_569ac(0,0);
    thunk_set_request_word_8a2c_bounded5_568dc(0,2);
    thunk_set_indexed_status_mask_word_if_below_five_50c82(0,0);
    thunk_set_request_word_8aa8_bounded6_56cda(0,0xc);
  }
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x77e))))) & 2) == 0) {
    set_output_request_word('\x01',0x70010000);
    clear_direct_output_bank1();
    set_channel_owner_request('\x01',0x20000);
    thunk_set_priority_mask_8a9c_bounded2_56c26(1,0x40000);
    thunk_set_secondary_channel_request_bounded5_56e66(1,0x20000);
    thunk_set_secondary_priority_mask_bounded2_56f14(1,0x40000);
    thunk_set_request_word_8a50_bounded5_569ac(1,0);
    thunk_set_request_word_8a2c_bounded5_568dc(1,0x20000);
    thunk_set_indexed_status_mask_word_if_below_five_50c82(1,0);
    thunk_set_request_word_8aa8_bounded6_56cda(1,0xc0000);
  }
  thunk_set_request_word_8a48_bounded2_5693e(0,0);
  return;
}

void thunk_reset_unmasked_output_bank_requests_b29fa(void)

{
  reset_unmasked_output_bank_requests_b29fa();
  return;
}

void run_init_chain_b2ace(void)

{
  set_output_request_word('\0',0x7001);
  set_output_request_word('\x01',0x70010000);
  clear_direct_output_enables();
  thunk_set_request_word_8a48_bounded2_5693e(0,3);
  thunk_set_request_word_8a2c_bounded5_568dc(0,2);
  thunk_set_request_word_8a2c_bounded5_568dc(1,0x20000);
  return;
}

undefined4 clear_output_bank_owners_and_set_default_requests_b2b0a(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  set_output_request_word('\0',0x70017001);
  set_output_request_word('\x01',0x70017001);
  set_channel_owner_request('\0',0);
  set_channel_owner_request('\x01',0);
  thunk_set_secondary_channel_request_bounded5_56e66(0,0);
  thunk_set_secondary_channel_request_bounded5_56e66(1,0);
  if (((*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x77e)))) & 1) == 0) {
    thunk_set_request_word_8aa8_bounded6_56cda((*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x77e)))) & 1,2);
  }
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x77e))))) & 2) == 0) {
    thunk_set_request_word_8aa8_bounded6_56cda(1,0x20000);
  }
  return pack_and_write_record9_configuration_fields_bd8ea();
}

void step_mode301_invocation_counter(void)

{
  uint32_t puVar1;
  byte bVar2;
  
  bVar2 = DAT_febeb10d;
  puVar1 = 0xfebeb800u;
  if (DAT_febeb10d < 5) {
    bVar2 = DAT_febeb10d + 1;
  }
  else {
    puVar1 = 0xfebeb800u;
    set_indexed_request_and_clear_complement_b15ac(0x24);
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6f3))))) = bVar2;
  return;
}

undefined4 set_request_index_12_b2b90(void)

{
  return set_indexed_request_and_clear_complement_b15ac(0xc);
}

void advance_mode300_substate(void)

{
  uchar request_id;
  uint uVar1;
  
  if (DAT_febeb11a == 0x300) {
    uVar1 = probe_pending_mode_request('#');
    if (uVar1 == 1) {
      clear_output_bank_owners_and_set_default_requests_b2b0a();
      publish_live_application_mode(0x301);
    }
    request_id = '#';
  }
  else {
    if (DAT_febeb11a != 0x301) {
      return;
    }
    step_mode301_invocation_counter();
    uVar1 = probe_pending_mode_request('$');
    if (uVar1 == 1) {
      set_request_index_12_b2b90();
    }
    request_id = '$';
  }
  acknowledge_selected_mode_request(request_id);
  return;
}

void mode_hook_b2bf4(void)

{
  return;
}

void mode_hook_b2bf6(void)

{
  return;
}

void apply_mode400_output_requests(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  set_output_request_word('\0',0);
  set_output_request_word('\x01',0);
  thunk_set_priority_mask_8a9c_bounded2_56c26(0,0);
  thunk_set_priority_mask_8a9c_bounded2_56c26(1,0);
  thunk_set_secondary_priority_mask_bounded2_56f14(0,0);
  thunk_set_secondary_priority_mask_bounded2_56f14(1,0);
  thunk_set_request_word_8a50_bounded5_569ac(0,0);
  thunk_set_request_word_8a50_bounded5_569ac(1,0);
  thunk_set_request_word_8a2c_bounded5_568dc(0,0);
  thunk_set_request_word_8a2c_bounded5_568dc(1,0);
  thunk_set_indexed_status_mask_word_if_below_five_50c82(0,0);
  thunk_set_indexed_status_mask_word_if_below_five_50c82(1,0);
  if (((*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x77e)))) & 1) == 0) {
    thunk_set_request_word_8aa8_bounded6_56cda((*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x77e)))) & 1,2);
  }
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x77e))))) & 2) == 0) {
    thunk_set_request_word_8aa8_bounded6_56cda(1,0x20000);
  }
  return;
}

void enter_mode400(void)

{
  thunk_capture_and_persist_record_twelve_samples_45cfc();
  set_output_request_word('\0',0);
  set_output_request_word('\x01',0);
  thunk_set_byte_febe82a9_to_z_515ca();
  return;
}

void mode_hook_b2ca2(void)

{
  return;
}

void set_request_words_two_and_three_b2ca6(void)

{
  thunk_set_request_word_8a88_bounded4_56b78(2,2);
  thunk_set_request_word_8a88_bounded4_56b78(3,0x20000);
  return;
}

undefined4 snapshot_retained_control_records(void)

{
  publish_thermal_reference_record();
  publish_thermal_history_record();
  return write_record8_current_fields_when_initialized_bd87e();
}

undefined4 set_request_index_10_b2cd6(void)

{
  return set_indexed_request_and_clear_complement_b15ac(10);
}

uint get_mode700_progress_marker(void)

{
  if ((DAT_febeb11a != 0x702) && (DAT_febeb11a == 0x701)) {
    return 0;
  }
  return 0x5a;
}

uint advance_mode700_substate(void)

{
  uchar request_id;
  uint uVar1;
  
  if (0x6ff < DAT_febeb11a) {
    if (DAT_febeb11a == 0x700) {
      uVar1 = probe_pending_mode_request('&');
      if (uVar1 == 1) {
        set_request_words_two_and_three_b2ca6();
        publish_live_application_mode(0x701);
      }
      request_id = '&';
    }
    else if (DAT_febeb11a < 0x702) {
      uVar1 = probe_pending_mode_request('\'');
      if (uVar1 == 1) {
        snapshot_retained_control_records();
        publish_live_application_mode(0x702);
      }
      request_id = '\'';
    }
    else {
      if (DAT_febeb11a != 0x702) goto LAB_000b2d6c;
      uVar1 = probe_pending_mode_request('(');
      if (uVar1 == 1) {
        set_request_index_10_b2cd6();
      }
      request_id = '(';
    }
    acknowledge_selected_mode_request(request_id);
  }
LAB_000b2d6c:
  uVar1 = get_mode700_progress_marker();
  return uVar1;
}

void request_mode701_snapshot_unless_health_selected(void)

{
  char cVar1;
  int iVar2;
  
  cVar1 = DAT_febeb10c;
  iVar2 = check_status_byte_complement_pair_b1c40();
  if ((iVar2 != 1) || (cVar1 != '\x01')) {
    set_indexed_request_and_clear_complement_b15ac(0x27);
  }
  return;
}

void request_mode700_initial_step(void)

{
  set_indexed_request_and_clear_complement_b15ac(0x26);
  thunk_capture_and_persist_record_twelve_samples_45cfc();
  return;
}

void enter_mode700(void)

{
  report_pending_service_aborts();
  publish_thermal_reference_record();
  publish_thermal_history_record();
  write_record8_current_fields_when_initialized_bd87e();
  pack_and_write_record9_configuration_fields_bd8ea();
  stage_received_word_age_record13();
  thunk_set_event_state_dirty_bit1_under_priority_mask_52a10();
  thunk_promote_capture_bank_dirty_bit3_to_bit1_562fa();
  consume_ba_retained_admission_count();
  set_b250_completion_latch_b5eb0();
  request_mode701_snapshot_unless_health_selected();
  request_mode700_initial_step();
  thunk_set_request_word_8a48_bounded2_5693e(0,3);
  set_output_request_word('\0',0x70017001);
  set_output_request_word('\x01',0x70017001);
  thunk_set_secondary_channel_request_bounded5_56e66(0,0);
  thunk_set_secondary_channel_request_bounded5_56e66(1,0);
  thunk_set_secondary_priority_mask_bounded2_56f14(0,0);
  thunk_set_secondary_priority_mask_bounded2_56f14(1,0);
  thunk_set_request_word_8a50_bounded5_569ac(0,0);
  thunk_set_request_word_8a50_bounded5_569ac(1,0);
  thunk_set_request_word_8a2c_bounded5_568dc(0,0);
  thunk_set_request_word_8a2c_bounded5_568dc(1,0);
  thunk_set_indexed_status_mask_word_if_below_five_50c82(0,0);
  thunk_set_indexed_status_mask_word_if_below_five_50c82(1,0);
  thunk_set_request_word_8aa8_bounded6_56cda(0,4);
  thunk_set_request_word_8aa8_bounded6_56cda(1,0x40000);
  return;
}

void mode_hook_b2e62(void)

{
  return;
}

uint apply_mode800_ready_output_requests(void)

{
  uint uVar1;
  
  uVar1 = query_application_nvm_readiness();
  if (uVar1 == 1) {
    set_channel_owner_request('\0',0x20002);
    set_channel_owner_request('\x01',0x20002);
    thunk_set_priority_mask_8a9c_bounded2_56c26(0,4);
    thunk_set_priority_mask_8a9c_bounded2_56c26(1,0x40000);
    thunk_set_secondary_channel_request_bounded5_56e66(0,0);
    thunk_set_secondary_channel_request_bounded5_56e66(1,0);
    thunk_set_secondary_priority_mask_bounded2_56f14(0,0);
    thunk_set_secondary_priority_mask_bounded2_56f14(1,0);
    thunk_set_request_word_8aa8_bounded6_56cda(0,4);
    thunk_set_request_word_8aa8_bounded6_56cda(1,0x40000);
    thunk_set_request_word_8a88_bounded4_56b78(2,2);
    thunk_set_request_word_8a88_bounded4_56b78(3,0x20000);
  }
  return uVar1;
}

void mode_hook_b2ee2(void)

{
  return;
}

void mode_hook_b2ee4(void)

{
  return;
}

void select_request_from_mode_bits_and_completion_markers_b2ee6(void)

{
  undefined4 uVar1;
  
  if (((DAT_febeb10e & 1) == 0) || (DAT_febef176 != 0)) {
    if (((DAT_febeb10e >> 1 & 1) == 0) || ((DAT_febef172 != 0 || (DAT_febef208 != 0)))) {
      if (((DAT_febeb10e >> 2 & 1) == 0) &&
         (((DAT_febeb10e >> 3 & 1) == 0 && ((DAT_febeb10e >> 4 & 1) == 0)))) {
        if (DAT_febef208 != -0x5aa5a55b) {
          return;
        }
        if ((DAT_febeb10e >> 1 & 1) != 0) {
          return;
        }
        uVar1 = 4;
      }
      else {
        uVar1 = 0x2e;
      }
    }
    else {
      uVar1 = 0x2c;
    }
  }
  else {
    uVar1 = 0x2a;
  }
  set_indexed_request_and_clear_complement_b15ac(uVar1);
  return;
}

void thunk_latch_b1a7_and_clear_requests_zero_one_b77f4(void)

{
  latch_b1a7_and_clear_requests_zero_one_b77f4();
  return;
}

void initialize_service_engine_kind_from_mode_bits_b2f5e(void)

{
  uchar kind;
  
  if ((DAT_febeb10e >> 2 & 1) == 0) {
    if ((DAT_febeb10e >> 3 & 1) != 0) {
      kind = '\x02';
      invalidate_nonzero_ratio_mode_output_b794e();
      goto LAB_000b2f82;
    }
    kind = '\x03';
  }
  else {
    kind = '\x01';
  }
  clear_ratio_reference_and_mode_b78ee();
LAB_000b2f82:
  initialize_service_engine(kind);
  return;
}

void set_request_43_on_status44_and_completion_marker_b2f8c(void)

{
  if ((DAT_febef012 == 'D') && (DAT_febef210 == -0x5aa5a55b)) {
    set_indexed_request_and_clear_complement_b15ac(0x2b);
  }
  return;
}

void clear_mode_bit0_and_reset_6958_state_b2fb4(void)

{
  DAT_febeb10e = DAT_febeb10e & 0xfe;
  thunk_clear_state_bytes_6958_and_counter_695c_32c86();
  return;
}

void set_request_45_on_status44_and_completion_marker_b2fc6(void)

{
  if ((DAT_febef010 == 'D') && (DAT_febef208 == -0x5aa5a55b)) {
    set_indexed_request_and_clear_complement_b15ac(0x2d);
  }
  return;
}

void publish_routine8_completion_and_clear_mode_bit1_b2fee(void)

{
  uint32_t puVar1;
  undefined4 uVar2;
  
  puVar1 = 0xfebeb800u;
  if (DAT_febef208 == -0x5aa5a55b) {
    uVar2 = 0;
  }
  else {
    puVar1 = 0xfebeb800u;
    thunk_clear_quad_status_if_88_35ad6();
    uVar2 = 0x20;
  }
  thunk_publish_routine_or_pending_write_terminal_result_4d0a4(8,uVar2);
  publish_requests_zero_one_when_b1a4_clear_b7810();
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6f2))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6f2))))) & 0xfd;
  return;
}
