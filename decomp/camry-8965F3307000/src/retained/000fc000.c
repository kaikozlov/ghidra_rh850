#include "common.h"

void snapshot_request_and_calibration_status_blocks_fc2a0(void)

{
  snapshot_request_status_to_ef80_block_fcc00();
  snapshot_calibration_and_admission_to_f300_block_fcc4e();
  return;
}

void thunk_snapshot_admission_metadata_and_eighteen_source_bytes_fcc9c(void)

{
  snapshot_admission_metadata_and_eighteen_source_bytes_fcc9c();
  return;
}

void snapshot_three_control_input_blocks_fc3cc(void)

{
  copy_cell_block_fd400();
  snapshot_acquisition_status_to_e740_block_fd426();
  copy_cell_block_fd456();
  return;
}

void snapshot_service_pair_and_control_summary_fc462(void)

{
  snapshot_service_byte_and_signed_word_pair_fd444();
  snapshot_rom_bounds_and_retained_control_to_eb00_block_fd49e();
  return;
}

void snapshot_calibration_status_and_source_byte_block_fc4f8(void)

{
  snapshot_calibration_and_admission_to_f300_block_fcc4e();
  snapshot_admission_metadata_and_eighteen_source_bytes_fcc9c();
  return;
}

void thunk_snapshot_request_status_to_ef80_block_fcc00(void)

{
  snapshot_request_status_to_ef80_block_fcc00();
  return;
}

void snapshot_control_status_and_service_pair_fc87c(void)

{
  snapshot_acquisition_status_to_e740_block_fd426();
  snapshot_service_byte_and_signed_word_pair_fd444();
  return;
}

void snapshot_three_retained_control_summary_blocks_fc9a8(void)

{
  copy_cell_block_fd456();
  snapshot_rom_bounds_and_retained_control_to_eb00_block_fd49e();
  snapshot_retained_and_coherence_state_to_eb80_block_fd562();
  return;
}

void snapshot_request_status_to_ef80_block_fcc00(void)

{
  DAT_febeef86 = DAT_febe7db0;
  DAT_febeef80 = DAT_febe7bbc;
  DAT_febeef81 = DAT_febe686c;
  DAT_febeef88 = DAT_febe71ec;
  DAT_febeef8a = DAT_febe7da6;
  DAT_febeef84 = 0;
  DAT_febeef85 = 0;
  DAT_febeef8c = DAT_febe7da8;
  DAT_febeef90 = output_request_status;
  DAT_febeef8e = DAT_febe71f2;
  DAT_febeef82 = DAT_febe7567;
  DAT_febeef83 = DAT_febe7568;
  return;
}

void snapshot_calibration_and_admission_to_f300_block_fcc4e(void)

{
  DAT_febef308 = monitor_current_staged_calibration.marker;
  DAT_febef300 = internal_source_admission_state;
  DAT_febef304 = DAT_febe7f3a;
  DAT_febef30c = DAT_febe6af0;
  DAT_febef310 = DAT_febe6ac4;
  DAT_febef314 = DAT_febe6abc;
  DAT_febef318 = DAT_febe6ac0;
  DAT_febef301 = DAT_febe6878;
  DAT_febef306 = ((int)(int16_t)DAT_febe8152);
  DAT_febef302 = DAT_febe80a5;
  DAT_febef303 = DAT_febe80a0;
  DAT_febef31c = DAT_febe68b4;
  return;
}

void snapshot_admission_metadata_and_eighteen_source_bytes_fcc9c(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  DAT_febef380 = internal_source_admission_state;
  DAT_febef394 = DAT_febe6af0;
  DAT_febef381 = DAT_febe6878;
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -0x11;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebef382u + (uint32_t)(iVar3) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe85f4u + (uint32_t)(iVar3) * 1u))));
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  return;
}
