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
uint32_t camry_sample_icctrl(void);
void camry_write8(uint32_t address, uint32_t value);
void camry_write16(uint32_t address, uint32_t value);
void camry_write32(uint32_t address, uint32_t value);
uint8_t *camry_host_ptr(uint32_t address);
uint32_t camry_host_addr(const void *pointer);
/* A pointer whose bits are a firmware address is the host window of that
 * address. A real host pointer is returned unchanged. */
void *camry_host_resolve(const void *pointer);
/* A self-branch halt returns. Callers stop only when propagation is on. */
extern int camry_halt_propagate;
extern int camry_halted;
extern uint32_t camry_stop_arm;
extern uint32_t camry_stop_pc;
extern uint32_t camry_note_root;
int camry_note_call(uint32_t caller, uint32_t address);
#define camry_host_halt() do { camry_halted = 1; return; } while (0)
extern uint8_t camry_fill;
extern uint32_t camry_peripheral_file;
void camry_fill_bytes(void *bytes, unsigned long size);
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
extern uint32_t camry_sp;
extern uint32_t camry_pmr;
extern uint32_t camry_psw;
extern uint32_t camry_SR[14][32];
extern uint32_t camry_gpr[32];
extern uint32_t camry_r7;
void camry_gpr_import_aliases(void);
void camry_gpr_export_aliases(void);

typedef struct {
    uint32_t address;
    void *function;
} camry_indirect_slot;
extern const camry_indirect_slot camry_indirect_slots[];
extern const uint32_t camry_indirect_count;
void *camry_indirect(uint32_t address);
int camry_code_address(const void *pointer, uint32_t *address);

void *memcpy_forward(void *destination, void *source, uint32_t byte_count);
void memzero(void *destination, uint32_t byte_count);
void pwm_initialize_compare_stages(uint32_t compare);
void pwm_stage_halfword_compares(uint32_t slot, uint32_t u_code, uint32_t v_code, uint32_t w_code);
void pwm_stage_word_compares(uint32_t slot, uint32_t w_code, uint32_t v_code, uint32_t u_code);
uint32_t force_unconfirmed_terminal_monitor_healthy(uint32_t state, uint32_t thresholds, uint32_t callbacks);
void copy_whole_words(uint32_t *destination, uint32_t *source, uint16_t byte_count);
uint32_t update_whole_words(uint32_t *destination, uint32_t *source, uint16_t byte_count);

uint32_t load_u8(const void *source);
uint32_t load_u16(const void *source);
void store_u8(void *destination, uint32_t value);
void store_u16(void *destination, uint32_t value);
void store_u32(void *destination, uint32_t value);

uint32_t nvm_sum_bytes(uint32_t byte_count, const uint8_t *source);
uint32_t nvm_family0_chunk_cost(uint32_t payload_bytes);
uint32_t scale_u16_delta_s16_x4(uint32_t value, uint32_t origin, uint32_t gain);

uint32_t nvm_payload_length(uint32_t handle);
uint32_t nvm_base_offset(uint32_t handle);
uint32_t nvm_allocation_pages(uint32_t handle);
uint32_t nvm_erase_base_record_allocation_77982(uint32_t handle);
int dataflash_start_sixty_four_byte_block_erase_7867a(uint32_t byte_offset, uint32_t byte_count);
uint32_t nvm_record_offset(uint32_t handle, uint32_t allocation_index, uint32_t byte_offset);
uint32_t nvm_payload_page_count(uint32_t handle);
uint32_t nvm_payload_chunk_length(uint32_t handle, uint32_t payload_offset);
uint32_t nvm_trailer_offset(uint32_t handle);
uint32_t nvm_storage_handle(uint32_t handle);
uint32_t nvm_read_buffer(uint32_t logical_handle);
uint32_t nvm_write_buffer(uint32_t logical_handle);
void nvm_set_read_buffer(uint32_t logical_handle, uint32_t buffer);
void nvm_set_write_buffer(uint32_t logical_handle, uint32_t buffer);
uint32_t nvm_get_storage_page(uint32_t storage_handle, uint16_t *page_out);
uint32_t nvm_get_logical_storage_page(uint32_t logical_handle, uint16_t *page_out);
uint32_t nvm_advance_family0_request_index(uint32_t index);
uint32_t nvm_advance_family1_request_index(uint32_t index);
uint32_t nvm_get_family0_status(uint32_t object);
uint32_t nvm_get_family1_completion(uint32_t object);
uint32_t nvm_get_family1_record(uint32_t object, uint32_t destination);
uint32_t nvm_get_family1_status(uint32_t object);
uint32_t nvm_get_family2_status(uint32_t object);
uint32_t dcra1_crc_raw_words(uint32_t source, uint32_t byte_count, uint32_t raw_seed);
uint32_t nvm_check_family2_rom_crc(uint32_t group);
uint32_t nvm_get_family2_rom_record(uint32_t object, uint32_t destination);
uint32_t nvm_get_record(uint32_t selector, uint32_t destination);
uint32_t nvm_refresh_family2_record_status(uint32_t object);
void publish_learned_quad(void);
uint32_t restore_learned_quad(void);
void nvm_initialize_family1_application(void);
void nvm_publish_logical_result(uint32_t logical_handle, uint32_t operation, uint32_t result);
uint32_t read_repair_redundant_u8(
    uint32_t raw, uint32_t encoded55, uint32_t encoded_aa, uint32_t fallback);
uint32_t nvm_check_family1_checksum(uint32_t object);
void nvm_publish_family1_checksum(uint32_t object);
uint32_t nvm_retain_token_while_reads_pending(uint32_t token);
uint32_t nvm_probe_range_rejected(uint32_t byte_offset, uint32_t byte_count);
uint32_t nvm_poll_probe_mode(void);
uint32_t nvm_classify_storage_range(
    uint32_t ignored_selector, uint32_t byte_offset, uint32_t byte_count);
uint32_t nvm_translate_diagnostic_mask(uint32_t source_mask);
void nvm_accumulate_diagnostic_mask(uint32_t source_mask);
void nvm_accumulate_side_status(uint32_t value);
void nvm_accumulate_result_class(uint32_t result_class);

uint32_t lookup_u32_value_by_key(uint32_t key, uint32_t fallback, uint32_t table);
void nvm_initialize_operation(void);
uint32_t nvm_submit_operation(uint32_t operation);
void nvm_unlink_queue_slot(uint32_t header, uint32_t index, uint32_t previous);
uint32_t poll_word_masks(uint32_t word, uint32_t first_mask, uint32_t second_mask, uint32_t attempts);

void nvm_set_physical_result_state(uint32_t state);
void nvm_set_secondary_result_state(uint32_t state);
uint32_t nvm_get_secondary_result(void);
uint32_t nvm_get_direct_operation_result(void);
uint32_t icus20_read_bit0(void);
uint32_t faci_decode_completion_status(void);
uint32_t nvm_lookup_byte_result(uint32_t key, uint32_t rows, uint32_t row_count);
uint32_t nvm_translate_read_driver_result(uint32_t driver_result);
uint32_t nvm_translate_saved_driver_result(void);
void nvm_recover_family0_request_indices(uint8_t *producer_out, uint8_t *consumer_out);
void nvm_recover_family1_request_indices(uint8_t *producer_out, uint8_t *consumer_out);
void freshness_encode_wire(uint32_t freshness, uint32_t wire, uint32_t bit_capacity);
void freshness_decode_wire(uint32_t wire, uint32_t bit_length, uint32_t freshness);
uint32_t freshness_select_reset_candidate(uint32_t received, uint32_t search);
void freshness_commit_pending(uint32_t slot, uint32_t verification_result);
uint32_t freshness_reconstruct_ordinary(
    uint32_t slot, uint32_t received, uint32_t search, uint32_t reconstructed);
uint32_t freshness_reconstruct_candidate(
    uint32_t slot, uint32_t received, uint32_t skip_matches, uint32_t reconstructed);
uint32_t classify_channel_residual_a(void);
uint32_t curve16_interpolate_with_slope(uint32_t curve, uint32_t x, uint32_t slope);
uint32_t check_learned_quad_bounds(void);
uint32_t nvm_enqueue_family0_read(uint32_t object);
uint32_t nvm_set_family0_record(uint32_t object, uint32_t source);
void update_thermal_release_envelope(void);
void update_thermal_history_qualification(void);
void nvm_initialize_queues(void);
void nvm_reset_queues_notifying(void);
uint32_t nvm_pop_queue_head(uint32_t queue, uint32_t index);
uint32_t nvm_enqueue_read(uint32_t logical, uint32_t destination);
uint32_t nvm_enqueue_write(uint32_t logical, uint32_t source);
uint32_t nvm_arm_family0_read(uint32_t object);
uint32_t nvm_arm_family0_write(uint32_t object);
uint32_t nvm_submit_family1_read_copies(uint32_t object);
uint32_t nvm_submit_family1_write_copies(uint32_t object);
uint32_t nvm_submit_bulk_reads(void);
uint32_t nvm_step_initial_read_acquisition(void);
uint32_t nvm_step_acquisition_pass(void);
void nvm_run_bounded_initial_acquisition(void);
uint32_t priority_mask_enter(uint32_t requested_mask);
void priority_mask_restore(uint32_t saved_mask);
uint32_t raise_priority_mask_and_return_previous_d1da0(uint32_t requested_mask);
void restore_priority_mask_preserving_interrupt_enable_d1dc6(uint32_t saved_mask);
void push_priority_mask_and_raise_to_ff00_6a45e(void);
void pop_and_restore_priority_mask_stack_6a4c4(void);
uint32_t dataflash_copy_words_ecc(
    uint32_t dataflash_offset, uint32_t destination, uint32_t byte_count);
