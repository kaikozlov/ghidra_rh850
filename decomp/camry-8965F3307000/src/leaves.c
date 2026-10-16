#include "camry.h"

/* Leaves checked against the original instruction bytes and retained oracles.
 * Loads and stores are the six-byte EP accessors at 0x78AD4..0x78AF6.
 * NvM table bases are tp plus the decoded displacements: descriptors at
 * tp+0x3838 (6 bytes), logical descriptors at tp+0x2810 (16 bytes).
 * With tp 0x23DFC those are 0x27634 and 0x26C0C.
 */

uint32_t camry_gp;
uint32_t camry_tp;

void f33_pwm_initialize_compare_stages(uint32_t compare) {
    uint32_t value = compare & 0xffffu;
    uint32_t index = 0;
    while (index < 2u) {
        uint32_t halves = camry_gp - 32608u + (index << 3);
        uint32_t loaded = camry_read16((3u << 16) + (index << 3) + 5650u);
        camry_write16(halves + 2u, value);
        camry_write16(halves + 4u, value);
        camry_write16(halves + 6u, value);
        camry_write16(halves, loaded);
        uint32_t words = camry_gp - 32592u + index * 12u;
        camry_write32(words, value);
        camry_write32(words + 4u, value);
        camry_write32(words + 8u, value);
        index += 1u;
    }
}

uint32_t f33_force_unconfirmed_terminal_monitor_healthy(
    uint32_t state, uint32_t thresholds, uint32_t callbacks) {
    uint32_t limit_high = camry_read16(thresholds + 2u);
    uint32_t value_high = camry_read16(state + 4u);
    uint32_t value_low = camry_read16(state + 2u);
    uint32_t limit_low = camry_read16(thresholds);
    uint32_t callback;
    if (value_high > limit_high || value_low > limit_low)
        return 17u;
    callback = camry_read32(callbacks + 4u);
    camry_write8(state, 0);
    if (callback != 0u)
        ((void (*)(void))(uintptr_t)callback)();
    camry_write16(state + 4u, 0);
    camry_write16(state + 2u, limit_low + 1u);
    return 17u;
}

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

static uint32_t read_u32(const unsigned char *address) {
    return (uint32_t)address[0]
        | ((uint32_t)address[1] << 8)
        | ((uint32_t)address[2] << 16)
        | ((uint32_t)address[3] << 24);
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

uint32_t f33_nvm_allocation_pages(uint32_t handle) {
    uint32_t length = f33_nvm_payload_length(handle);
    uint32_t bytes = length;
    if (length >= 33u)
        bytes += 4u;
    bytes += descriptor_option(handle) == 0u ? 4u : 12u;
    return (bytes + 64u) >> 6;
}

uint32_t f33_nvm_record_offset(uint32_t handle, uint32_t allocation_index, uint32_t byte_offset) {
    uint32_t narrowed = handle & 0xffffu;
    uint32_t base = f33_nvm_base_offset(narrowed);
    uint32_t pages = f33_nvm_allocation_pages(narrowed);
    uint32_t span = (allocation_index & 0xffffu) * pages;
    return byte_offset + (span << 6) + base;
}

uint32_t f33_nvm_payload_page_count(uint32_t handle) {
    uint32_t length = f33_nvm_payload_length(handle);
    uint32_t narrowed = (length + (length & 3u)) & 0xffffu;
    return (narrowed + 0x3cu) >> 6;
}

uint32_t f33_nvm_payload_chunk_length(uint32_t handle, uint32_t payload_offset) {
    uint32_t remaining = (f33_nvm_payload_length(handle & 0xffffu) - payload_offset) & 0xffffu;
    if (remaining >= 65u)
        remaining = 64u;
    return (remaining + (remaining & 3u)) & 0xffffu;
}

uint32_t f33_nvm_trailer_offset(uint32_t handle) {
    return (f33_nvm_allocation_pages(handle) << 6) - 4u;
}

uint32_t f33_nvm_storage_handle(uint32_t handle) {
    return read_u16(f33_nvm_logical_descriptors + (handle & 0xffffu) * 16u + 8u);
}

static const unsigned char *logical_descriptor(uint32_t handle) {
    return f33_nvm_logical_descriptors + (handle & 0xffffu) * 16u;
}

static uint32_t logical_buffer(uint32_t logical_handle, uint32_t override_address) {
    uint32_t override = camry_read32(override_address);
    const unsigned char *row = logical_descriptor(logical_handle);
    if (override != 0u)
        return override;
    if (row[4] == 4u)
        return 0xfebf6b10u;
    return read_u32(row + 12);
}

uint32_t f33_nvm_read_buffer(uint32_t logical_handle) {
    return logical_buffer(logical_handle, 0xfebf6b08u);
}

uint32_t f33_nvm_write_buffer(uint32_t logical_handle) {
    return logical_buffer(logical_handle, 0xfebf6b0cu);
}

uint32_t f33_nvm_get_storage_page(uint32_t storage_handle, uint16_t *page_out) {
    *page_out = read_u16(f33_nvm_descriptors + (storage_handle & 0xffffu) * 6u);
    return 0;
}

uint32_t f33_nvm_get_logical_storage_page(uint32_t logical_handle, uint16_t *page_out) {
    uint32_t handle = logical_handle & 0xffffu;
    if ((handle - 2u) >= 122u)
        return 1;
    return f33_nvm_get_storage_page(f33_nvm_storage_handle(handle), page_out);
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

uint32_t f33_nvm_get_family0_status(uint32_t object) {
    uint32_t index = object & 0xffffu;
    uint32_t count = camry_read16((3u << 16) - 21136u);
    if (index >= count)
        return 0xffu;
    return camry_read8(camry_gp + index + 19208u);
}

uint32_t f33_nvm_get_family1_completion(uint32_t object) {
    uint32_t index = object & 0xffffu;
    uint32_t count = camry_read16((3u << 16) - 21134u);
    if (index >= count)
        return 0xa5u;
    return camry_read8(camry_gp + index + 19288u);
}

static uint32_t family1_word_fold(uint32_t object) {
    uint32_t descriptor = 0x2af0cu + (object << 3);
    uint32_t words = camry_read16(descriptor) >> 2;
    uint32_t buffer = camry_read32(descriptor + 4u);
    uint32_t total = 0;
    uint32_t cursor = 0;
    while (cursor < words) {
        uint32_t word = camry_read32(buffer + (cursor << 2));
        cursor += 1u;
        total += word;
        total += word >> 16;
    }
    return total;
}

uint32_t f33_nvm_check_family1_checksum(uint32_t object) {
    uint32_t index = object & 0xffffu;
    uint32_t total = family1_word_fold(index);
    uint32_t seed = camry_read16(camry_gp + (index << 1) + 19496u);
    if (((total + seed) & 0xffffu) == 0xa55au)
        return 1u;
    return 0xffffffffu;
}

void f33_nvm_publish_family1_checksum(uint32_t object) {
    uint32_t index = object & 0xffffu;
    uint32_t total = family1_word_fold(index);
    camry_write16(camry_gp + (index << 1) + 19496u, 0xa55au - total);
}

uint32_t f33_nvm_probe_range_rejected(uint32_t byte_offset, uint32_t byte_count) {
    uint32_t first_page = camry_read16(camry_tp + 16076u);
    uint32_t page_count;
    uint32_t start;
    uint32_t end;
    uint32_t remaining;
    if (first_page == 0xffffu)
        return 1u;
    page_count = camry_read16(camry_tp + 16078u);
    start = first_page << 6;
    end = ((first_page + page_count) << 6) - 1u;
    if (byte_offset < start || byte_offset > end)
        return 1u;
    remaining = (end - byte_offset) + 1u;
    return byte_count > remaining ? 1u : 0u;
}

uint32_t f33_nvm_translate_diagnostic_mask(uint32_t source_mask) {
    uint32_t result = 0;
    uint32_t index = 0;
    uint32_t base = camry_tp + 16104u;
    while (index < 17u) {
        uint32_t record = base + (index << 3);
        if (camry_read32(record) & source_mask)
            result |= camry_read32(record + 4u);
        index += 1u;
    }
    return result;
}

void f33_nvm_accumulate_diagnostic_mask(uint32_t source_mask) {
    uint32_t translated = f33_nvm_translate_diagnostic_mask(source_mask);
    uint32_t service = camry_read8(0xfebf6cccu);
    uint32_t adjusted = service - 6u;
    uint32_t base = 0xfebf6cc0u;
    if (adjusted <= 2u) {
        camry_write32(base, camry_read32(base) | translated);
        return;
    }
    adjusted -= 6u;
    if (adjusted <= 1u) {
        camry_write32(base, camry_read32(base) | translated);
        camry_write32(base + 8u, camry_read32(base + 8u) | translated);
        return;
    }
    adjusted -= 10u;
    if (adjusted > 2u)
        return;
    camry_write32(base, camry_read32(base) | translated);
}

void f33_nvm_accumulate_side_status(uint32_t value) {
    uint32_t mask = value > 1u ? 0x8000u : (value == 1u ? 2u : 1u);
    f33_nvm_accumulate_diagnostic_mask(mask);
}

void f33_nvm_accumulate_result_class(uint32_t result_class) {
    uint32_t code = (result_class & 0xffu) - 33u;
    uint32_t mask;
    if (code <= 1u)
        mask = 8u;
    else if (code == 94u)
        mask = 4u;
    else if (code == 96u)
        mask = 32u;
    else if (code == 98u)
        mask = 64u;
    else if (code == 220u)
        mask = 8u;
    else if (code == 222u)
        mask = 16u;
    else
        mask = 0x8000u;
    f33_nvm_accumulate_diagnostic_mask(mask);
}

void f33_nvm_unlink_queue_slot(uint32_t header, uint32_t index, uint32_t previous) {
    uint32_t slot = 0xfebf6128u + (index & 0xffffu) * 16u;
    uint32_t next = camry_read16(slot + 14u);
    uint32_t prev = previous & 0xffffu;
    if (prev == 0xffffu) {
        camry_write16(header, next);
        prev = next;
    } else {
        camry_write16(0xfebf6128u + prev * 16u + 14u, next);
    }
    if (next == 0xffffu)
        camry_write16(header + 2u, prev);
}

void f33_nvm_initialize_operation(void) {
    camry_write32(0xfebf6aecu + 12u, 0);
    camry_write32(0xfebf6aecu + 8u, 0);
    camry_write8(0xfebf6b00u, 0);
    camry_write16(0xfebf6afcu, 1u);
    camry_write16(0xfebf6aecu + 4u, 0xffffu);
    camry_write32(0xfebf6aecu, 0xffffffffu);
    camry_write16(0xfebf6afeu, 0xffffu);
}

uint32_t f33_lookup_u32_value_by_key(uint32_t key, uint32_t fallback, uint32_t table) {
    uint32_t count = camry_read32(table);
    uint32_t index = 0;
    while (index < count) {
        uint32_t slot = camry_read32(table + 4u) + (index << 3);
        if (camry_read32(slot + 4u) == key)
            return camry_read32(slot);
        index += 1u;
    }
    return fallback;
}

uint32_t f33_poll_word_masks(uint32_t word, uint32_t first_mask, uint32_t second_mask, uint32_t attempts) {
    for (;;) {
        uint32_t value = camry_read32(word);
        if (value & first_mask)
            return 0;
        if (value & second_mask)
            return 1;
        attempts -= 1u;
        if (attempts == 0u)
            return 2;
    }
}

void f33_nvm_set_physical_result_state(uint32_t state) {
    uint32_t narrowed = state & 0xffu;
    uint32_t current;
    int store;
    if (narrowed == 3u) {
        current = camry_read8(0xfebf6b76u);
        store = current == 2u;
    } else if (narrowed <= 2u || narrowed == 4u) {
        store = 1;
    } else {
        store = 0;
    }
    if (store)
        camry_write8(0xfebf6b76u, narrowed);
}

void f33_nvm_set_secondary_result_state(uint32_t state) {
    uint32_t narrowed = state & 0xffu;
    uint32_t current;
    int store;
    if (narrowed == 5u) {
        current = camry_read8(0xfebf6b72u);
        store = current == 1u;
    } else if (narrowed <= 1u || narrowed == 4u || narrowed == 6u) {
        store = 1;
    } else {
        store = 0;
    }
    if (store)
        camry_write8(0xfebf6b72u, narrowed);
}

uint32_t f33_nvm_get_secondary_result(void) {
    return camry_read8(0xfebf6b72u);
}

uint32_t f33_nvm_get_direct_operation_result(void) {
    uint32_t value = f33_nvm_get_secondary_result();
    if (value == 0u)
        return 0;
    if (value == 1u)
        return 1;
    if (value == 5u || value == 6u)
        return value;
    return 4;
}

uint32_t f33_icus20_read_bit0(void) {
    uint32_t value = camry_read32(0xffc5d020u) << 31;
    return value != 0u ? 1u : 0u;
}

uint32_t f33_nvm_lookup_byte_result(uint32_t key, uint32_t rows, uint32_t row_count) {
    uint32_t narrowed = key & 0xffu;
    uint32_t index = 0;
    while (index < row_count) {
        uint32_t row = rows + (index << 3);
        if (camry_read8(row) == narrowed)
            return camry_read32(row + 4u);
        index += 1u;
    }
    return 0xffffffffu;
}

uint32_t f33_nvm_translate_read_driver_result(uint32_t driver_result) {
    return f33_nvm_lookup_byte_result(driver_result, camry_tp + 15248u, 11u);
}

uint32_t f33_nvm_translate_saved_driver_result(void) {
    uint32_t key = camry_read8(0xfebf0000u + 27425u);
    return f33_nvm_lookup_byte_result(key, camry_tp + 15160u, 11u);
}
