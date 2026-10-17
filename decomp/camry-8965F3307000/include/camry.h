#pragma once

#include <stdint.h>

/* Camry 8965F3307000 application prototypes. A function lives here once its
 * C is checked against the original bytes. Names are the symbol-map names.
 *
 * camry_read/camry_write are the absolute 32-bit address space. camry_gp,
 * camry_tp, and camry_sp are the ABI gp, tp, and entry sp registers.
 */

#ifdef CAMRY_HOST
uint32_t camry_read8(uint32_t address);
uint32_t camry_read16(uint32_t address);
uint32_t camry_read32(uint32_t address);
void camry_write8(uint32_t address, uint32_t value);
void camry_write16(uint32_t address, uint32_t value);
void camry_write32(uint32_t address, uint32_t value);
uint8_t *camry_host_ptr(uint32_t address);
#else
static inline uint32_t camry_read8(uint32_t address) {
    return *(volatile uint8_t *)(uintptr_t)address;
}
static inline uint32_t camry_read16(uint32_t address) {
    return *(volatile uint16_t *)(uintptr_t)address;
}
static inline uint32_t camry_read32(uint32_t address) {
    return *(volatile uint32_t *)(uintptr_t)address;
}
static inline void camry_write8(uint32_t address, uint32_t value) {
    *(volatile uint8_t *)(uintptr_t)address = (uint8_t)value;
}
static inline void camry_write16(uint32_t address, uint32_t value) {
    *(volatile uint16_t *)(uintptr_t)address = (uint16_t)value;
}
static inline void camry_write32(uint32_t address, uint32_t value) {
    *(volatile uint32_t *)(uintptr_t)address = value;
}
static inline uint8_t *camry_host_ptr(uint32_t address) {
    return (uint8_t *)(uintptr_t)address;
}
#endif

extern uint32_t camry_gp;
extern uint32_t camry_tp;
extern uint32_t camry_pmr;

void *f33_memcpy_forward(void *destination, void *source, uint32_t byte_count);
void f33_memzero(void *destination, uint32_t byte_count);
void f33_pwm_initialize_compare_stages(uint32_t compare);
void f33_pwm_stage_halfword_compares(uint32_t slot, uint32_t u_code, uint32_t v_code, uint32_t w_code);
void f33_pwm_stage_word_compares(uint32_t slot, uint32_t w_code, uint32_t v_code, uint32_t u_code);
uint32_t f33_force_unconfirmed_terminal_monitor_healthy(uint32_t state, uint32_t thresholds, uint32_t callbacks);
void f33_copy_whole_words(uint32_t *destination, uint32_t *source, uint16_t byte_count);
uint32_t f33_update_whole_words(uint32_t *destination, uint32_t *source, uint16_t byte_count);

uint32_t f33_load_u8(const void *source);
uint32_t f33_load_u16(const void *source);
void f33_store_u8(void *destination, uint32_t value);
void f33_store_u16(void *destination, uint32_t value);
void f33_store_u32(void *destination, uint32_t value);

uint32_t f33_nvm_sum_bytes(uint32_t byte_count, const uint8_t *source);
uint32_t f33_nvm_family0_chunk_cost(uint32_t payload_bytes);
uint32_t f33_scale_u16_delta_s16_x4(uint32_t value, uint32_t origin, uint32_t gain);

uint32_t f33_nvm_payload_length(uint32_t handle);
uint32_t f33_nvm_base_offset(uint32_t handle);
uint32_t f33_nvm_allocation_pages(uint32_t handle);
uint32_t FUN_00077982(uint32_t handle);
uint32_t f33_nvm_record_offset(uint32_t handle, uint32_t allocation_index, uint32_t byte_offset);
uint32_t f33_nvm_payload_page_count(uint32_t handle);
uint32_t f33_nvm_payload_chunk_length(uint32_t handle, uint32_t payload_offset);
uint32_t f33_nvm_trailer_offset(uint32_t handle);
uint32_t f33_nvm_storage_handle(uint32_t handle);
uint32_t f33_nvm_read_buffer(uint32_t logical_handle);
uint32_t f33_nvm_write_buffer(uint32_t logical_handle);
void f33_nvm_set_read_buffer(uint32_t logical_handle, uint32_t buffer);
void f33_nvm_set_write_buffer(uint32_t logical_handle, uint32_t buffer);
uint32_t f33_nvm_get_storage_page(uint32_t storage_handle, uint16_t *page_out);
uint32_t f33_nvm_get_logical_storage_page(uint32_t logical_handle, uint16_t *page_out);
uint32_t f33_nvm_advance_family0_request_index(uint32_t index);
uint32_t f33_nvm_advance_family1_request_index(uint32_t index);
uint32_t f33_nvm_get_family0_status(uint32_t object);
uint32_t f33_nvm_get_family1_completion(uint32_t object);
uint32_t f33_nvm_get_family1_record(uint32_t object, uint32_t destination);
uint32_t f33_nvm_get_family1_status(uint32_t object);
uint32_t f33_nvm_get_family2_status(uint32_t object);
uint32_t f33_dcra1_crc_raw_words(uint32_t source, uint32_t byte_count, uint32_t raw_seed);
uint32_t f33_nvm_check_family2_rom_crc(uint32_t group);
uint32_t f33_nvm_get_family2_rom_record(uint32_t object, uint32_t destination);
uint32_t f33_nvm_get_record(uint32_t selector, uint32_t destination);
uint32_t f33_nvm_refresh_family2_record_status(uint32_t object);
void f33_publish_learned_quad(void);
uint32_t f33_restore_learned_quad(void);
void f33_nvm_initialize_family1_application(void);
void f33_nvm_publish_logical_result(uint32_t logical_handle, uint32_t operation, uint32_t result);
uint32_t f33_read_repair_redundant_u8(
    uint32_t raw, uint32_t encoded55, uint32_t encoded_aa, uint32_t fallback);
uint32_t f33_nvm_check_family1_checksum(uint32_t object);
void f33_nvm_publish_family1_checksum(uint32_t object);
uint32_t f33_nvm_retain_token_while_reads_pending(uint32_t token);
uint32_t f33_nvm_probe_range_rejected(uint32_t byte_offset, uint32_t byte_count);
uint32_t f33_nvm_translate_diagnostic_mask(uint32_t source_mask);
void f33_nvm_accumulate_diagnostic_mask(uint32_t source_mask);
void f33_nvm_accumulate_side_status(uint32_t value);
void f33_nvm_accumulate_result_class(uint32_t result_class);

uint32_t f33_lookup_u32_value_by_key(uint32_t key, uint32_t fallback, uint32_t table);
void f33_nvm_initialize_operation(void);
uint32_t f33_nvm_submit_operation(uint32_t operation);
void f33_nvm_unlink_queue_slot(uint32_t header, uint32_t index, uint32_t previous);
uint32_t f33_poll_word_masks(uint32_t word, uint32_t first_mask, uint32_t second_mask, uint32_t attempts);

void f33_nvm_set_physical_result_state(uint32_t state);
void f33_nvm_set_secondary_result_state(uint32_t state);
uint32_t f33_nvm_get_secondary_result(void);
uint32_t f33_nvm_get_direct_operation_result(void);
uint32_t f33_icus20_read_bit0(void);
uint32_t f33_faci_decode_completion_status(void);
uint32_t f33_nvm_lookup_byte_result(uint32_t key, uint32_t rows, uint32_t row_count);
uint32_t f33_nvm_translate_read_driver_result(uint32_t driver_result);
uint32_t f33_nvm_translate_saved_driver_result(void);
void f33_nvm_recover_family0_request_indices(uint8_t *producer_out, uint8_t *consumer_out);
void f33_nvm_recover_family1_request_indices(uint8_t *producer_out, uint8_t *consumer_out);
void f33_freshness_encode_wire(uint32_t freshness, uint32_t wire, uint32_t bit_capacity);
void f33_freshness_decode_wire(uint32_t wire, uint32_t bit_length, uint32_t freshness);
uint32_t f33_freshness_select_reset_candidate(uint32_t received, uint32_t search);
void f33_freshness_commit_pending(uint32_t slot, uint32_t verification_result);
uint32_t f33_freshness_reconstruct_ordinary(
    uint32_t slot, uint32_t received, uint32_t search, uint32_t reconstructed);
uint32_t f33_freshness_reconstruct_candidate(
    uint32_t slot, uint32_t received, uint32_t skip_matches, uint32_t reconstructed);
uint32_t f33_classify_channel_residual_a(void);
uint32_t f33_curve16_interpolate_with_slope(uint32_t curve, uint32_t x, uint32_t slope);
uint32_t f33_check_learned_quad_bounds(void);
uint32_t f33_nvm_enqueue_family0_read(uint32_t object);
uint32_t f33_nvm_set_family0_record(uint32_t object, uint32_t source);
void f33_update_thermal_release_envelope(void);
void f33_update_thermal_history_qualification(void);
void f33_nvm_initialize_queues(void);
void f33_nvm_reset_queues_notifying(void);
uint32_t f33_nvm_pop_queue_head(uint32_t queue, uint32_t index);
uint32_t f33_nvm_enqueue_read(uint32_t logical, uint32_t destination);
uint32_t f33_nvm_enqueue_write(uint32_t logical, uint32_t source);
uint32_t f33_nvm_arm_family0_read(uint32_t object);
uint32_t f33_nvm_arm_family0_write(uint32_t object);
uint32_t f33_nvm_submit_family1_read_copies(uint32_t object);
uint32_t f33_nvm_submit_family1_write_copies(uint32_t object);
uint32_t f33_nvm_submit_bulk_reads(void);
uint32_t f33_nvm_step_initial_read_acquisition(void);
uint32_t f33_nvm_step_acquisition_pass(void);
void f33_nvm_run_bounded_initial_acquisition(void);
uint32_t f33_priority_mask_enter(uint32_t requested_mask);
void f33_priority_mask_restore(uint32_t saved_mask);
uint32_t FUN_000d1da0(uint32_t requested_mask);
void FUN_000d1dc6(uint32_t saved_mask);
void FUN_0006a45e(void);
void FUN_0006a4c4(void);
uint32_t f33_dataflash_copy_words_ecc(
    uint32_t dataflash_offset, uint32_t destination, uint32_t byte_count);
