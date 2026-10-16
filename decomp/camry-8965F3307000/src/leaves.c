#include "camry.h"

/* Leaves checked against the original instruction bytes and retained oracles.
 * Loads and stores are the six-byte EP accessors at 0x78AD4..0x78AF6.
 * NvM table bases are tp 0x23DFC plus the decoded displacements:
 * descriptors at 0x27634 (6 bytes), logical descriptors at 0x26C0C (16 bytes).
 */

extern const unsigned char f33_nvm_descriptors[];
extern const unsigned char f33_nvm_logical_descriptors[];
extern const unsigned char f33_nvm_family0_request_cell_count;
extern const unsigned char f33_nvm_family1_request_cell_count;

uint32_t f33_load_u8(const void *source) {
    return *(const uint8_t *)source;
}

uint32_t f33_load_u16(const void *source) {
    return *(const uint16_t *)source;
}

void f33_store_u8(void *destination, uint32_t value) {
    *(uint8_t *)destination = (uint8_t)value;
}

void f33_store_u16(void *destination, uint32_t value) {
    *(uint16_t *)destination = (uint16_t)value;
}

void f33_store_u32(void *destination, uint32_t value) {
    *(uint32_t *)destination = value;
}

uint32_t f33_nvm_sum_bytes(uint32_t byte_count, const uint8_t *source) {
    uint32_t total = 0;
    uint32_t index = 0;
    byte_count &= 0xffffu;
    while (index < byte_count) {
        total += source[index];
        index = (index + 1u) & 0xffffu;
    }
    return total;
}

uint32_t f33_nvm_family0_chunk_cost(uint32_t payload_bytes) {
    uint32_t rounded = ((uint16_t)(payload_bytes + 20u) + 63u) >> 6;
    if (rounded < 2u)
        rounded = 2u;
    return rounded;
}

uint32_t f33_scale_u16_delta_s16_x4(uint32_t value, uint32_t origin, uint32_t gain) {
    uint32_t delta = (uint16_t)value - (uint16_t)origin;
    uint32_t product = (uint32_t)((int64_t)(int32_t)delta * (int64_t)(int16_t)gain);
    return product << 2;
}

static uint16_t read_u16(const unsigned char *address) {
    return (uint16_t)address[0] | ((uint16_t)address[1] << 8);
}

uint32_t f33_nvm_payload_length(uint32_t handle) {
    return read_u16(f33_nvm_descriptors + (handle & 0xffffu) * 6u + 2u);
}

uint32_t f33_nvm_base_offset(uint32_t handle) {
    return (uint32_t)read_u16(f33_nvm_descriptors + (handle & 0xffffu) * 6u) << 6;
}

static uint32_t descriptor_option(uint32_t handle) {
    return f33_nvm_descriptors[(handle & 0xffffu) * 6u + 4u];
}

static uint32_t allocation_pages(uint32_t handle) {
    uint32_t length = f33_nvm_payload_length(handle);
    uint32_t bytes = length;
    if (length > 32u)
        bytes += 4u;
    bytes += descriptor_option(handle) == 0u ? 4u : 12u;
    return (bytes + 64u) >> 6;
}

uint32_t f33_nvm_payload_page_count(uint32_t handle) {
    uint32_t length = f33_nvm_payload_length(handle);
    uint32_t narrowed = (length + (length & 3u)) & 0xffffu;
    return (narrowed + 0x3cu) >> 6;
}

uint32_t f33_nvm_trailer_offset(uint32_t handle) {
    return (allocation_pages(handle) << 6) - 4u;
}

uint32_t f33_nvm_storage_handle(uint32_t handle) {
    return read_u16(f33_nvm_logical_descriptors + (handle & 0xffffu) * 16u + 8u);
}

static uint32_t advance_request_index(uint32_t index, unsigned cell_count) {
    uint32_t current = index & 0xffu;
    int32_t limit = (int32_t)cell_count - 1;
    if ((int32_t)current < limit)
        return (current + 1u) & 0xffu;
    return 0;
}

uint32_t f33_nvm_advance_family0_request_index(uint32_t index) {
    return advance_request_index(index, f33_nvm_family0_request_cell_count);
}

uint32_t f33_nvm_advance_family1_request_index(uint32_t index) {
    return advance_request_index(index, f33_nvm_family1_request_cell_count);
}
