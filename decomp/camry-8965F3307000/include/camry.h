#pragma once

#include <stdint.h>

/* Camry 8965F3307000 application prototypes. A function lives here once its
 * C is checked against the original bytes. Names are the symbol-map names.
 */

void *f33_memcpy_forward(void *destination, void *source, uint32_t byte_count);
void f33_memzero(void *destination, uint32_t byte_count);
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
uint32_t f33_nvm_payload_page_count(uint32_t handle);
uint32_t f33_nvm_trailer_offset(uint32_t handle);
uint32_t f33_nvm_storage_handle(uint32_t handle);
uint32_t f33_nvm_advance_family0_request_index(uint32_t index);
uint32_t f33_nvm_advance_family1_request_index(uint32_t index);
