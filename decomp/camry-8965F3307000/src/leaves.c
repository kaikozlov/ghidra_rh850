#include "camry.h"

/* Leaves checked against the original instruction bytes and retained oracles.
 * Loads and stores are the six-byte EP accessors at 0x78AD4..0x78AF6.
 * NvM table bases are tp plus the decoded displacements: descriptors at
 * tp+0x3838 (6 bytes), logical descriptors at tp+0x2810 (16 bytes).
 * With tp 0x23DFC those are 0x27634 and 0x26C0C.
 */

uint32_t camry_gp;
uint32_t camry_tp;
uint32_t camry_sp;

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

static void f33_nvm_reset_buffer_retry(void) {
    camry_write8(0xfebf6b14u, 0);
}

static void f33_return_only_stub_71ce0(void) {
}

static void publish_buffer_override(uint32_t logical_handle, uint32_t buffer, uint32_t override) {
    uint32_t handle = logical_handle & 0xffffu;
    f33_nvm_reset_buffer_retry();
    camry_write32(override, buffer);
    if (buffer == 0u && camry_read8(camry_tp + (handle << 4) + 11796u) == 2u)
        f33_return_only_stub_71ce0();
}

void f33_nvm_set_read_buffer(uint32_t logical_handle, uint32_t buffer) {
    publish_buffer_override(logical_handle, buffer, 0xfebf6b08u);
}

void f33_nvm_set_write_buffer(uint32_t logical_handle, uint32_t buffer) {
    publish_buffer_override(logical_handle, buffer, 0xfebf6b0cu);
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

static int32_t f33_vote_redundant_u8(
    uint32_t raw, uint32_t encoded55, uint32_t encoded_aa, uint32_t *voted) {
    uint32_t plain;
    uint32_t copy55;
    uint32_t copy_aa;
    int32_t status;
    if (raw == 0u || encoded55 == 0u || encoded_aa == 0u)
        return -1;
    plain = camry_read8(raw);
    copy55 = camry_read8(encoded55) ^ 0x55u;
    copy_aa = camry_read8(encoded_aa) ^ 0xaau;
    if (plain == copy55) {
        *voted = plain;
        if (plain == copy_aa)
            return 0;
        return -11;
    }
    if (plain != copy_aa) {
        if (copy55 == copy_aa) {
            status = -12;
            plain = copy55;
        } else {
            status = -13;
        }
        *voted = plain;
        return status;
    }
    *voted = plain;
    return -11;
}

static int32_t f33_publish_redundant_u8(
    uint32_t value, uint32_t raw, uint32_t encoded55, uint32_t encoded_aa) {
    if (raw == 0u || encoded55 == 0u || encoded_aa == 0u)
        return -1;
    value &= 0xffu;
    camry_write8(raw, value);
    camry_write8(encoded55, value ^ 0x55u);
    camry_write8(encoded_aa, value ^ 0xaau);
    return 0;
}

uint32_t f33_read_repair_redundant_u8(
    uint32_t raw, uint32_t encoded55, uint32_t encoded_aa, uint32_t fallback) {
    uint32_t voted = 0u;
    int32_t status = f33_vote_redundant_u8(raw, encoded55, encoded_aa, &voted);
    if (status != 0) {
        if (status != -12 && status != -11)
            voted = fallback & 0xffu;
        f33_publish_redundant_u8(voted, raw, encoded55, encoded_aa);
    }
    return voted & 0xffu;
}

uint32_t f33_nvm_get_family1_record(uint32_t object, uint32_t destination) {
    uint32_t index = object & 0xffffu;
    uint32_t descriptor;
    uint32_t source;
    uint32_t words;
    uint32_t offset;
    uint32_t status;
    if (index >= camry_read16((3u << 16) - 21134u))
        return 0xffu;
    descriptor = 0x2af0cu + (index << 3);
    source = camry_read32(descriptor + 4u);
    words = camry_read16(descriptor) >> 2;
    for (offset = 0u; offset < words; offset = (offset + 1u) & 0xffffu)
        camry_write32(destination + (offset << 2), camry_read32(source + (offset << 2)));
    status = f33_read_repair_redundant_u8(
        camry_gp + index + 19240u,
        camry_gp + index + 22664u,
        camry_gp + index + 22700u,
        0x12u);
    if (status == 0x10u && f33_nvm_check_family1_checksum(index) != 1u)
        status = 0x12u;
    return status;
}

uint32_t f33_nvm_get_family1_status(uint32_t object) {
    uint32_t index = object & 0xffffu;
    if (index >= camry_read16((3u << 16) - 21134u))
        return 0xffu;
    return f33_read_repair_redundant_u8(
        camry_gp + index + 19240u,
        camry_gp + index + 22664u,
        camry_gp + index + 22700u,
        0x12u);
}

uint32_t f33_nvm_get_family2_status(uint32_t object) {
    uint32_t index = object & 0xffffu;
    if (index >= camry_read16((3u << 16) - 21132u))
        return 0xffu;
    return f33_read_repair_redundant_u8(
        camry_gp + index + 20048u,
        camry_gp + index + 22680u,
        camry_gp + index + 22716u,
        0x10u);
}

static uint32_t crc32_word(uint32_t state, uint32_t word) {
    uint32_t byte_index;
    for (byte_index = 0u; byte_index < 4u; byte_index++) {
        uint32_t bit;
        state ^= (word >> (byte_index * 8u)) & 0xffu;
        for (bit = 0u; bit < 8u; bit++) {
            uint32_t mask = -(state & 1u);
            state = (state >> 1) ^ (0xedb88320u & mask);
        }
    }
    return state;
}

uint32_t f33_dcra1_crc_raw_words(uint32_t source, uint32_t byte_count, uint32_t raw_seed) {
    uint32_t words = byte_count >> 2;
    uint32_t index;
    uint32_t state = raw_seed;
    camry_write8(0xffd51020u, 0);
    for (index = 0u; index < words; index++) {
        uint32_t word = camry_read32(source + (index << 2));
        camry_write32(0xffd51000u, word);
        state = crc32_word(state, word);
    }
    camry_write32(0xffd51004u, state ^ 0xffffffffu);
    return state;
}

uint32_t f33_nvm_check_family2_rom_crc(uint32_t group) {
    uint32_t index = group & 0xffffu;
    uint32_t descriptor = 0x2af8cu + index * 12u;
    uint32_t bytes = (camry_read16(descriptor) + 4u) & 0xffffu;
    uint32_t residue = f33_dcra1_crc_raw_words(
        camry_read32(descriptor + 8u), bytes, 0xffffffffu);
    return residue == 0u ? 0x10u : 0x30u;
}

static void copy_record_words(uint32_t destination, uint32_t source, uint32_t byte_count) {
    uint32_t offset;
    for (offset = 0u; offset < (byte_count >> 2); offset = (offset + 1u) & 0xffffu)
        camry_write32(destination + (offset << 2), camry_read32(source + (offset << 2)));
}

static uint32_t f33_nvm_get_family0_record(uint32_t object, uint32_t destination) {
    uint32_t index = object & 0xffffu;
    uint32_t descriptor;
    if (index >= camry_read16(0x2ad70u))
        return 0xffu;
    descriptor = 0x2ad8cu + index * 12u;
    copy_record_words(destination, camry_read32(descriptor + 8u), camry_read16(descriptor));
    return camry_read8(camry_gp + index + 19208u);
}

uint32_t f33_nvm_get_family2_rom_record(uint32_t object, uint32_t destination) {
    uint32_t index = object & 0xffffu;
    uint32_t descriptor;
    uint32_t residue;
    if (index >= camry_read16((3u << 16) - 21132u))
        return 0xffu;
    residue = f33_nvm_check_family2_rom_crc(index);
    if (residue != 0x10u)
        residue = f33_nvm_check_family2_rom_crc(index);
    f33_publish_redundant_u8(
        residue,
        camry_gp + index + 20048u,
        camry_gp + index + 22680u,
        camry_gp + index + 22716u);
    if (residue == 0x10u) {
        descriptor = 0x2af8cu + index * 12u;
        copy_record_words(destination, camry_read32(descriptor + 8u), camry_read16(descriptor));
    }
    return residue;
}

uint32_t f33_nvm_get_record(uint32_t selector, uint32_t destination) {
    uint32_t family = selector & 0xff00u;
    uint32_t object = selector & 0xffu;
    if (family == 0u)
        return f33_nvm_get_family0_record(object, destination);
    if (family == 0x100u)
        return f33_nvm_get_family1_record(object, destination);
    if (family == 0x200u)
        return f33_nvm_get_family2_rom_record(object, destination);
    return 0xffu;
}

uint32_t f33_nvm_refresh_family2_record_status(uint32_t object) {
    uint32_t index = object & 0xffffu;
    uint32_t residue;
    if (index >= camry_read16((3u << 16) - 21132u))
        return 0u;
    residue = f33_nvm_check_family2_rom_crc(index);
    if (residue != 0x10u)
        residue = f33_nvm_check_family2_rom_crc(index);
    f33_publish_redundant_u8(
        residue,
        camry_gp + index + 20048u,
        camry_gp + index + 22680u,
        camry_gp + index + 22716u);
    return 1u;
}

void f33_nvm_initialize_family1_application(void) {
    uint32_t requests = camry_read8((3u << 16) - 21109u);
    uint32_t objects = camry_read16((3u << 16) - 21134u);
    uint32_t index;
    uint32_t cell;
    uint32_t descriptor;
    uint32_t words;
    uint32_t buffer;
    uint32_t offset;
    uint32_t base;
    for (index = 0u; index < requests; index++) {
        cell = camry_gp + 19852u + (index << 2);
        camry_write8(cell, 0xffu);
        camry_write16(cell + 2u, 0xffffu);
    }
    for (index = 0u; index < objects; index++) {
        camry_write16(camry_gp + (index << 1) + 19496u, 0);
        f33_publish_redundant_u8(
            0u,
            camry_gp + index + 19240u,
            camry_gp + index + 22664u,
            camry_gp + index + 22700u);
        descriptor = 0x2af0cu + (index << 3);
        words = camry_read16(descriptor) >> 2;
        buffer = camry_read32(descriptor + 4u);
        for (offset = 0u; offset < words; offset++)
            camry_write32(buffer + (offset << 2), 0);
    }
    camry_write16(camry_gp + 20110u, 0);
    base = camry_gp + 20102u;
    camry_write16(base + 6u, 0xffffu);
    for (offset = 0u; offset < 5u; offset++)
        camry_write8(base + offset, 0);
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

uint32_t f33_nvm_retain_token_while_reads_pending(uint32_t token) {
    uint32_t value = token & 0xffu;
    uint32_t marker = 90u;
    uint32_t index = 0;
    uint32_t count = camry_read16((3u << 16) - 21134u);
    while (index < count && marker != 0u) {
        if (camry_read8(camry_gp + index + 19288u) == 255u)
            marker = 0u;
        index = (index + 1u) & 0xffffu;
    }
    if (marker != 0u) {
        index = 0;
        count = camry_read16((3u << 16) - 21136u);
        while (index < count) {
            if (camry_read8(camry_gp + index + 19256u) == 255u)
                marker = 0u;
            index = (index + 1u) & 0xffffu;
            if (marker == 0u)
                break;
        }
        if (marker != 0u)
            value = 0u;
    }
    return value;
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

static void recover_request_indices(
    uint32_t producer_out,
    uint32_t consumer_out,
    uint32_t indices,
    uint32_t count_address,
    uint32_t cell0) {
    uint32_t producer = camry_read8(indices);
    uint32_t consumer = camry_read8(indices + 1u);
    uint32_t count = camry_read8(count_address);
    uint32_t index;
    if (producer < count && consumer < count) {
        camry_write8(producer_out, producer);
        camry_write8(consumer_out, consumer);
        return;
    }
    producer = 0;
    consumer = 0;
    index = 1u;
    while (index < count) {
        uint32_t previous = camry_read16(cell0 + ((index - 1u) << 2));
        uint32_t current = camry_read16(cell0 + (index << 2));
        if (previous == 0xffffu) {
            if (current != 0xffffu)
                consumer = index;
        } else if (current == 0xffffu) {
            producer = index;
        }
        index = (index + 1u) & 0xffu;
    }
    camry_write8(producer_out, producer);
    camry_write8(consumer_out, consumer);
    camry_write8(indices, producer);
    camry_write8(indices + 1u, consumer);
}

void f33_nvm_recover_family0_request_indices(uint32_t producer_out, uint32_t consumer_out) {
    recover_request_indices(
        producer_out,
        consumer_out,
        camry_gp + 20090u,
        (3u << 16) - 21110u,
        camry_gp + 19594u);
}

void f33_nvm_recover_family1_request_indices(uint32_t producer_out, uint32_t consumer_out) {
    recover_request_indices(
        producer_out,
        consumer_out,
        camry_gp + 20102u,
        (3u << 16) - 21109u,
        camry_gp + 19854u);
}

static int32_t sign_half(uint32_t bits);

void f33_freshness_encode_wire(uint32_t freshness, uint32_t wire, uint32_t bit_capacity) {
    uint32_t length = camry_read8(freshness + 11u);
    if (length > camry_read8(bit_capacity))
        return;
    if (length == 46u) {
        uint32_t trip = camry_read32(freshness);
        uint32_t reset = camry_read32(freshness + 4u);
        uint32_t message = camry_read16(freshness + 8u);
        uint32_t low = camry_read8(freshness + 10u);
        camry_write8(wire, trip >> 8);
        camry_write8(wire + 1u, trip);
        camry_write8(wire + 2u, reset >> 12);
        camry_write8(wire + 3u, reset >> 4);
        camry_write8(wire + 4u, (reset << 4) | (message >> 4));
        camry_write8(wire + 5u, (message << 4) | (low << 2));
    } else if (length == 4u) {
        uint32_t message = camry_read16(freshness + 8u);
        uint32_t low = camry_read8(freshness + 10u);
        camry_write8(wire, (message << 6) | (low << 4));
    } else {
        length = 0;
    }
    camry_write32(bit_capacity, length);
}

static uint32_t stage_halfword_compare(uint32_t code) {
    uint32_t span = camry_read16(0x3166cu);
    uint32_t offset = camry_read16(0x3166eu);
    if (code == 0u)
        return span + (offset << 1);
    if (code >= 0x8000u)
        return 0;
    return offset + ((((0x8000u - code) * span) >> 15));
}

void f33_pwm_stage_halfword_compares(
    uint32_t slot, uint32_t u_code, uint32_t v_code, uint32_t w_code) {
    uint32_t record = camry_gp - 32608u + (slot << 3);
    camry_write16(record + 2u, stage_halfword_compare(u_code & 0xffffu));
    camry_write16(record + 4u, stage_halfword_compare(v_code & 0xffffu));
    camry_write16(record + 6u, stage_halfword_compare(w_code & 0xffffu));
}

void f33_pwm_stage_word_compares(
    uint32_t slot, uint32_t w_code, uint32_t v_code, uint32_t u_code) {
    uint32_t base = camry_gp - 32592u + (uint32_t)((int32_t)(int16_t)slot * 12);
    camry_write32(base, stage_halfword_compare(u_code & 0xffffu) & 0xffffu);
    camry_write32(base + 4u, stage_halfword_compare(v_code & 0xffffu) & 0xffffu);
    camry_write32(base + 8u, stage_halfword_compare(w_code & 0xffffu) & 0xffffu);
}

static void f33_nvm_copy_operation(uint32_t operation) {
    camry_write32(0xfebf6aecu, camry_read32(operation));
    camry_write16(0xfebf6af0u, camry_read16(operation + 4u));
    camry_write32(0xfebf6af4u, camry_read32(operation + 8u));
    camry_write32(0xfebf6af8u, camry_read32(operation + 12u));
}

uint32_t f33_nvm_submit_operation(uint32_t operation) {
    if (camry_read8(0xfebf6b00u) == 2u)
        return 1u;
    f33_nvm_copy_operation(operation);
    camry_write8(0xfebf6b00u, 2u);
    camry_write16(0xfebf6afcu, 1u);
    return 0u;
}

uint32_t f33_freshness_select_reset_candidate(uint32_t received, uint32_t search) {
    uint32_t skip = camry_read16(search + 12u);
    uint32_t index = 0;
    camry_write16(search + 14u, 0);
    while (index < 5u) {
        uint32_t reset = camry_read32(camry_gp - 25148u);
        uint32_t candidate = reset;
        int usable = 1;
        camry_write32(search + 8u, reset);
        if (index == 1u) {
            usable = reset != 0u;
            candidate = reset - 1u;
        } else if (index == 2u) {
            usable = reset <= 0xffffeu;
            candidate = reset + 1u;
        } else if (index == 3u) {
            usable = reset >= 2u;
            candidate = reset - 2u;
        } else if (index == 4u) {
            usable = reset <= 0xffffdu;
            candidate = reset + 2u;
        }
        if (usable) {
            uint32_t width = camry_read32(search + 4u) & 0x1fu;
            uint32_t masked = candidate & ((1u << width) - 1u);
            if (index != 0u)
                camry_write32(search + 8u, candidate);
            if ((masked & 0xffu) == camry_read8(received + 10u)) {
                if (skip == 0u)
                    return 1u;
                skip = (skip - 1u) & 0xffffu;
            }
        }
        index = (index + 1u) & 0xffffu;
        camry_write16(search + 14u, index);
    }
    return 0;
}

void f33_freshness_commit_pending(uint32_t slot, uint32_t verification_result) {
    uint32_t index = slot & 0xffffu;
    uint32_t offset;
    uint32_t displacement;
    uint32_t destination;
    uint32_t source;
    if (index >= 2u || (verification_result & 0xffu) != 1u)
        return;
    displacement = index * 12u;
    destination = camry_gp - 25124u + displacement;
    source = camry_gp - 25100u + displacement;
    for (offset = 0u; offset < 12u; offset++)
        camry_write8(destination + offset, camry_read8(source + offset));
}

uint32_t f33_freshness_reconstruct_ordinary(
    uint32_t slot, uint32_t received, uint32_t search, uint32_t reconstructed) {
    uint32_t trip = camry_read32(camry_gp - 25152u);
    int32_t slot_index = sign_half(camry_read16(slot + 2u));
    uint32_t record = camry_gp - 25124u + (uint32_t)(slot_index * 12);
    uint32_t committed_trip = camry_read32(record);
    uint32_t committed_reset = camry_read32(record + 4u);
    uint32_t committed_message = camry_read16(record + 8u);
    uint32_t ceiling = 0xffffffffu >> 12;
    uint32_t result = 0x22u;

    if (committed_trip == trip && committed_reset == camry_read32(search + 8u)) {
        uint32_t width;
        uint32_t span;
        uint32_t combined;
        uint32_t interval;
        uint32_t sum;
        camry_write32(reconstructed, committed_trip);
        camry_write32(reconstructed + 4u, committed_reset);
        result = 0u;
        if (committed_reset >= ceiling)
            goto saturate;
        width = camry_read32(search);
        span = 1u << (width & 31u);
        combined = camry_read16(received + 8u) | (committed_message & ~(span - 1u));
        camry_write16(reconstructed + 8u, combined);
        if (camry_read8(search + 16u) != 1u)
            return 0u;
        interval = 0u;
        if (width < 8u)
            interval = span & 0xffffu;
        sum = interval + committed_message;
        if ((sum & 0xffffu) <= committed_message || (int32_t)(sum - 255u) > 0)
            goto saturate;
        camry_write16(reconstructed + 8u, combined + interval);
        return 0u;
    }
    if (trip > committed_trip
        || (trip == committed_trip && camry_read32(search + 8u) > committed_reset)) {
        uint32_t reset = camry_read32(search + 8u);
        camry_write32(reconstructed, trip);
        camry_write16(reconstructed + 8u, camry_read16(received + 8u));
        camry_write32(reconstructed + 4u, reset);
        if (reset < ceiling)
            return 0u;
    } else {
        if (camry_read16(search + 14u) < 4u)
            return 0x23u;
        return result;
    }
saturate:
    camry_write16(reconstructed + 8u, 0xffu);
    return 0u;
}

uint32_t f33_freshness_reconstruct_candidate(
    uint32_t slot, uint32_t received, uint32_t skip_matches, uint32_t reconstructed) {
    uint32_t search = 0xfebe1fd8u;
    uint32_t bit_length = camry_read8(received + 11u);
    uint32_t message_width;
    uint32_t reset_width;
    uint32_t span;
    uint32_t committed_message;
    uint32_t received_message;
    int32_t slot_index;

    camry_write8(search + 16u, 0);
    camry_write16(search + 12u, skip_matches);
    if (bit_length > 10u) {
        message_width = 8u;
        reset_width = 2u;
    } else if (bit_length < 2u) {
        message_width = 0u;
        reset_width = bit_length;
    } else {
        message_width = (bit_length - 2u) & 0xffffu;
        reset_width = 2u;
    }
    camry_write32(search + 4u, reset_width);
    slot_index = sign_half(camry_read16(slot + 2u));
    camry_write32(search, message_width);
    span = 1u << (message_width & 31u);
    committed_message = camry_read16(camry_gp - 25116u + (uint32_t)(slot_index * 12));
    received_message = camry_read16(received + 8u);
    if (received_message <= (committed_message & (span - 1u)))
        camry_write8(search + 16u, 1u);
    if (f33_freshness_select_reset_candidate(received, search) != 1u)
        return 0x22u;
    return f33_freshness_reconstruct_ordinary(slot, received, search, reconstructed);
}

void f33_freshness_decode_wire(uint32_t wire, uint32_t bit_length, uint32_t freshness) {
    uint32_t low;
    if (bit_length == 4u) {
        uint32_t byte = camry_read8(wire);
        camry_write32(freshness, 0);
        camry_write32(freshness + 4u, 0);
        camry_write16(freshness + 8u, byte >> 6);
        low = byte >> 4;
    } else if (bit_length == 46u) {
        uint32_t first = camry_read8(wire);
        uint32_t second = camry_read8(wire + 1u);
        uint32_t third = camry_read8(wire + 2u);
        uint32_t fourth = camry_read8(wire + 3u);
        uint32_t fifth = camry_read8(wire + 4u);
        uint32_t sixth = camry_read8(wire + 5u);
        camry_write32(freshness, (first << 8) | second);
        camry_write32(freshness + 4u, (third << 12) | (fourth << 4) | (fifth >> 4));
        camry_write16(freshness + 8u, ((fifth << 4) | (sixth >> 4)) & 0xffu);
        low = sixth >> 2;
    } else {
        camry_write32(freshness, 0);
        camry_write32(freshness + 4u, 0);
        camry_write16(freshness + 8u, 0);
        camry_write8(freshness + 10u, 0);
        camry_write8(freshness + 11u, 0);
        return;
    }
    camry_write8(freshness + 10u, low & 3u);
    camry_write8(freshness + 11u, bit_length);
}

static int32_t sign_half(uint32_t bits) {
    return (int32_t)(int16_t)(bits & 0xffffu);
}

static uint32_t sat_abs_half(uint32_t bits) {
    int32_t value = sign_half(bits);
    if (value <= -32767)
        return 32767u;
    if (value < 0)
        value = -value;
    return (uint32_t)value;
}

static uint32_t sat_abs_word(uint32_t bits) {
    int32_t value = (int32_t)bits;
    if (value <= (int32_t)0x80000001u)
        return 0x7fffffffu;
    if (value < 0)
        return (uint32_t)(-value);
    return bits;
}

uint32_t f33_classify_channel_residual_a(void) {
    uint32_t status = camry_read32(0xfebe8b28u);
    int32_t reference = (int32_t)sat_abs_half(camry_read16(0xfebe77b8u));
    int32_t channel = (int32_t)sat_abs_half(camry_read16(0xfebe629eu));
    uint32_t minimum = camry_read16(0xfebe7da6u);
    uint32_t gate = camry_read16(0xfebe7b34u);
    uint32_t companion = camry_read8(0xfebe77b4u);
    uint32_t source = sat_abs_word(camry_read32(0xfebe77bcu));
    uint32_t selector;
    int32_t channel_limit;
    uint32_t minimum_limit;
    const uint32_t rom = 0x2b816u;

    if (companion != 0u || (status & 0x40004u) != 0u)
        return 0x44u;
    selector = camry_read8(0xfebeeb88u);
    if (selector == 0x5au) {
        channel_limit = sign_half(camry_read16(rom + 8u));
        minimum_limit = camry_read16(rom + 10u);
    } else {
        channel_limit = sign_half(camry_read16(rom + 4u));
        minimum_limit = camry_read16(rom + 6u);
    }
    if (reference < sign_half(camry_read16(rom))
        && source > camry_read16(rom + 2u)
        && channel <= channel_limit
        && minimum >= minimum_limit)
        return 0x22u;
    if (reference < sign_half(camry_read16(rom + 12u))
        && source <= camry_read16(rom + 14u)
        && selector == 0u
        && channel <= sign_half(camry_read16(rom + 16u))
        && minimum >= camry_read16(rom + 18u)
        && gate == 0xffffu)
        return 0x11u;
    return 0x33u;
}

static int32_t divq_s(int32_t dividend, int32_t divisor) {
    if (divisor == 0)
        return dividend;
    if (dividend == (int32_t)0x80000000u && divisor == -1)
        return dividend;
    return dividend / divisor;
}

static int32_t mul_low_s(int32_t left, int32_t right) {
    return (int32_t)((int64_t)left * (int64_t)right);
}

static int32_t curve_x(uint32_t curve, uint32_t index) {
    return sign_half(camry_read16(curve + (index << 2)));
}

static uint32_t curve_y(uint32_t curve, uint32_t index) {
    return camry_read16(curve + (index << 2) + 2u);
}

static uint32_t curve_segment(uint32_t curve, int32_t x) {
    if (x >= curve_x(curve, 8u)) {
        if (x >= curve_x(curve, 12u)) {
            if (x >= curve_x(curve, 14u))
                return x < curve_x(curve, 15u) ? 14u : 15u;
            return x < curve_x(curve, 13u) ? 12u : 13u;
        }
        if (x >= curve_x(curve, 10u))
            return x < curve_x(curve, 11u) ? 10u : 11u;
        return x < curve_x(curve, 9u) ? 8u : 9u;
    }
    if (x >= curve_x(curve, 4u)) {
        if (x >= curve_x(curve, 6u))
            return x < curve_x(curve, 7u) ? 6u : 7u;
        return x < curve_x(curve, 5u) ? 4u : 5u;
    }
    if (x >= curve_x(curve, 2u))
        return x < curve_x(curve, 3u) ? 2u : 3u;
    return x < curve_x(curve, 1u) ? 0u : 1u;
}

static int32_t slope_term(int32_t dx, int32_t dy) {
    int32_t scaled = (int32_t)((uint32_t)dy << 8);
    if (dx == 0) {
        int32_t fallback = sign_half(camry_read16(0xaf88cu));
        return divq_s((int32_t)((uint32_t)fallback << 8), 512);
    }
    return divq_s(scaled, dx);
}

static uint32_t curve_value(uint32_t curve, int32_t x, uint32_t index) {
    int32_t x0;
    int32_t x1;
    uint32_t y0;
    uint32_t y1;
    int32_t dx;
    int32_t quot;

    if (index == 15u)
        return curve_y(curve, 15u);
    x0 = curve_x(curve, index);
    x1 = curve_x(curve, index + 1u);
    y0 = curve_y(curve, index);
    y1 = curve_y(curve, index + 1u);
    dx = sign_half((uint32_t)(x1 - x0));
    quot = divq_s(mul_low_s((int32_t)(y1 - y0), x - x0), dx);
    return ((uint32_t)quot + y0) & 0xffffu;
}

static int32_t curve_slope(uint32_t curve, int32_t x, uint32_t index) {
    int32_t x0;
    int32_t x1;
    uint32_t y0;
    uint32_t y1;
    int32_t dx;
    int32_t current;
    int32_t next;
    int32_t previous;
    int32_t high;
    int32_t low;
    int32_t mixed;

    if (index == 15u) {
        int32_t span = curve_x(curve, 15u) - curve_x(curve, 14u);
        if (span == 0)
            return sign_half(camry_read16(0xaf88cu));
        current = divq_s(
            (int32_t)((uint32_t)(int32_t)(curve_y(curve, 15u) - curve_y(curve, 14u)) << 8),
            span);
        return divq_s((int32_t)((uint32_t)current << 9), 256);
    }
    x0 = curve_x(curve, index);
    x1 = curve_x(curve, index + 1u);
    y0 = curve_y(curve, index);
    y1 = curve_y(curve, index + 1u);
    dx = x1 - x0;
    current = slope_term(dx, (int32_t)(y1 - y0));
    if (index == 14u) {
        next = current;
    } else {
        next = slope_term(
            curve_x(curve, index + 2u) - x1,
            (int32_t)(curve_y(curve, index + 2u) - y1));
    }
    if (index == 0u) {
        previous = current;
    } else {
        previous = slope_term(
            x0 - curve_x(curve, index - 1u),
            (int32_t)(y0 - curve_y(curve, index - 1u)));
    }
    if (dx == 0)
        return sign_half(camry_read16(0xaf88cu));
    high = current > next ? current : next;
    low = previous > current ? previous : current;
    mixed = (int32_t)((uint32_t)low + (uint32_t)divq_s(
        mul_low_s((int32_t)((uint32_t)high - (uint32_t)low), x - x0), dx));
    return divq_s((int32_t)((uint32_t)mixed << 9), 256);
}

uint32_t f33_check_learned_quad_bounds(void) {
    int32_t upper_a = (int32_t)camry_read32(0xfebee8e8u);
    int32_t lower_a = (int32_t)camry_read32(0xfebee8ecu);
    int32_t upper_b = (int32_t)camry_read32(0xfebee8f0u);
    int32_t lower_b = (int32_t)camry_read32(0xfebee8f4u);
    int32_t first = (int32_t)f33_scale_u16_delta_s16_x4(camry_read16(0xfebe6ae6u), 0x800u, 0xf633u);
    int32_t second = (int32_t)f33_scale_u16_delta_s16_x4(camry_read16(0xfebe6ae8u), 0x800u, 0xf633u);
    int32_t third = (int32_t)f33_scale_u16_delta_s16_x4(camry_read16(0xfebe6aeau), 0x800u, 0xf633u);
    int32_t fourth = (int32_t)f33_scale_u16_delta_s16_x4(camry_read16(0xfebe6aecu), 0x800u, 0xf633u);
    if (first > upper_a || first < lower_a || second > upper_a || second < lower_a
        || third > upper_b || third < lower_b || fourth > upper_b || fourth < lower_b)
        return 0x5au;
    return 0;
}

void f33_publish_learned_quad(void) {
    uint32_t buffer = camry_sp - 16u;
    uint32_t source = camry_tp - 11564u;
    uint32_t offset;
    uint32_t status;
    for (offset = 0u; offset < 16u; offset += 4u)
        camry_write32(buffer + offset, camry_read32(source + offset));
    status = f33_nvm_get_record(0x100u, buffer);
    if (status != 0x10u)
        return;
    camry_write16(camry_gp - 19738u, camry_read16(buffer + 4u));
    camry_write16(camry_gp - 19736u, camry_read16(buffer + 6u));
    camry_write16(camry_gp - 19734u, camry_read16(buffer + 8u));
    camry_write16(camry_gp - 19732u, camry_read16(buffer + 10u));
}

uint32_t f33_restore_learned_quad(void) {
    uint32_t buffer = camry_sp - 16u;
    uint32_t status = f33_nvm_get_record(0x100u, buffer);
    if (status == 0x10u && camry_read32(buffer) == 0xa55a5aa5u) {
        f33_publish_learned_quad();
        if (f33_check_learned_quad_bounds() == 0u)
            return 0xa55a5aa5u;
    }
    return 0x5aa5a55au;
}

static uint32_t f33_nvm_family0_request_full(uint32_t producer, uint32_t consumer) {
    uint32_t limit = consumer & 0xffu;
    if (limit == 0u)
        limit = camry_read8(0x2ad8au);
    return ((producer & 0xffu) + 1u == limit) ? 1u : 0u;
}

static uint32_t f33_nvm_previous_family0_request(uint32_t index) {
    uint32_t value = index & 0xffu;
    if (value == 0u)
        value = camry_read8(0x2ad8au);
    return (value - 1u) & 0xffu;
}

uint32_t f33_nvm_enqueue_family0_read(uint32_t object) {
    uint32_t handle = object & 0xffffu;
    uint32_t indices = camry_gp + 20090u;
    uint32_t producer;
    uint32_t result;
    uint32_t previous;
    uint32_t cell;

    f33_nvm_recover_family0_request_indices(indices, indices + 1u);
    producer = camry_read8(indices);
    if (f33_nvm_family0_request_full(producer, camry_read8(indices + 1u)) == 1u
        || handle >= camry_read16(0x2ad70u)) {
        result = 0u;
    } else {
        previous = f33_nvm_previous_family0_request(producer);
        cell = camry_gp + 19592u + (previous << 2);
        if (camry_read16(cell + 2u) != handle || camry_read8(cell) != 0x11u) {
            camry_write8(camry_gp + handle + 19208u, 0x20u);
            cell = camry_gp + 19592u + (producer << 2);
            camry_write8(cell, 0x11u);
            camry_write16(cell + 2u, handle);
            producer = f33_nvm_advance_family0_request_index(producer);
        }
        result = 1u;
    }
    camry_write8(indices, producer);
    return result;
}

static uint32_t f33_words_differ_and_copy(uint32_t destination, uint32_t source, uint32_t byte_count) {
    uint32_t index;
    uint32_t differed = 0u;
    for (index = 0u; index < (byte_count >> 2); index = (index + 1u) & 0xffffu) {
        uint32_t value = camry_read32(source + (index << 2));
        uint32_t address = destination + (index << 2);
        if (camry_read32(address) != value) {
            camry_write32(address, value);
            differed = 1u;
        }
    }
    return differed;
}

static void f33_copy_family0_request_cell(uint32_t from_index, uint32_t to_index) {
    uint32_t from = camry_gp + 19592u + (from_index << 2);
    uint32_t to = camry_gp + 19592u + (to_index << 2);
    camry_write8(to, camry_read8(from));
    camry_write16(to + 2u, camry_read16(from + 2u));
}

uint32_t f33_nvm_set_family0_record(uint32_t object, uint32_t source) {
    uint32_t handle = object & 0xffffu;
    uint32_t indices = camry_gp + 20090u;
    uint32_t producer;
    uint32_t consumer;
    uint32_t count;
    uint32_t found;
    uint32_t remaining;
    uint32_t kind;
    uint32_t previous;
    uint32_t descriptor;
    uint32_t slot;

    f33_nvm_recover_family0_request_indices(indices, indices + 1u);
    producer = camry_read8(indices);
    consumer = camry_read8(indices + 1u);
    if (f33_nvm_family0_request_full(producer, consumer) == 1u
        || handle >= camry_read16(0x2ad70u))
        return 0u;
    previous = f33_nvm_previous_family0_request(producer);
    count = camry_read8(0x2ad8au);
    found = 0xffu;
    remaining = count;
    while (remaining != 0u) {
        uint32_t cell = camry_gp + 19592u + (consumer << 2);
        uint32_t cell_kind = camry_read8(cell);
        remaining -= 1u;
        if (camry_read16(cell + 2u) == handle && (cell_kind == 0x22u || cell_kind == 0x33u))
            found = cell_kind;
        if (consumer == producer || found != 0xffu)
            break;
        consumer = f33_nvm_advance_family0_request_index(consumer);
    }
    descriptor = 0x2ad8cu + handle * 12u;
    kind = 0x33u;
    if (f33_words_differ_and_copy(camry_read32(descriptor + 8u), source, camry_read16(descriptor)) == 1u
        || found == 0x22u)
        kind = 0x22u;
    if (consumer == previous) {
        camry_write8(camry_gp + 19592u + (consumer << 2), kind);
    } else {
        slot = producer;
        if (consumer != producer && count != 0u) {
            remaining = count;
            while (remaining != 0u) {
                uint32_t next = f33_nvm_advance_family0_request_index(consumer);
                remaining -= 1u;
                if (consumer == previous) {
                    slot = consumer;
                    break;
                }
                f33_copy_family0_request_cell(next, consumer);
                consumer = next;
            }
        }
        camry_write8(camry_gp + handle + 19208u, 0x20u);
        camry_write8(camry_gp + 19592u + (slot << 2), kind);
        camry_write16(camry_gp + 19594u + (slot << 2), handle);
        producer = f33_nvm_advance_family0_request_index(slot);
    }
    camry_write8(indices, producer);
    return 1u;
}

uint32_t f33_curve16_interpolate_with_slope(uint32_t curve, uint32_t x_bits, uint32_t slope_out) {
    int32_t x = sign_half(x_bits);
    uint32_t index = curve_segment(curve, x);
    uint32_t value = curve_value(curve, x, index);
    camry_write16(slope_out, (uint32_t)curve_slope(curve, x, index));
    return value;
}

static void f33_set_current_limit_request(uint32_t owner, uint32_t limit) {
    owner &= 0xffu;
    if (owner < 10u)
        camry_write16(camry_gp + 1332u + (owner << 1), limit);
}

static uint32_t f33_reduce_thermal_current_requests(void) {
    uint32_t minimum = 22170u;
    uint32_t index;
    for (index = 0u; index < 10u; index++) {
        uint32_t mask = camry_read32(0xaf0ccu + ((index >> 5) << 2));
        if (((mask >> (index & 31u)) & 1u) == 0u)
            continue;
        {
            uint32_t request = camry_read16(camry_gp + 1332u + (index << 1));
            if ((int32_t)request < (int32_t)minimum)
                minimum = request;
        }
    }
    return minimum;
}

void f33_update_thermal_release_envelope(void) {
    uint32_t state = camry_gp + 1352u;
    uint32_t amplitude = sat_abs_half(camry_read16(camry_gp - 1964u));
    uint32_t speed = camry_read16(camry_gp + 1762u);
    uint32_t gate = camry_read8(camry_gp + 1776u);
    uint32_t previous = camry_read16(state + 6u);
    uint32_t base = camry_read16(state + 4u);
    uint32_t counter = camry_read16(state + 2u);
    uint32_t table = 0xaf0d0u;
    int32_t hold_amplitude = sign_half(camry_read16(table + 2u));
    uint32_t published = f33_reduce_thermal_current_requests();
    uint32_t mode = 0u;

    if (previous < published) {
        uint32_t saved = camry_read8(state);
        if ((int32_t)amplitude <= hold_amplitude && previous <= camry_read16(table)) {
            published = previous;
        } else {
            uint32_t coefficient;
            uint32_t square;
            uint64_t wide;
            if (speed < camry_read16(table + 4u) && gate == 17u) {
                coefficient = camry_read32(table + 8u);
                mode = 2u;
            } else {
                coefficient = camry_read32(table + 12u);
                mode = 1u;
            }
            if (saved != mode) {
                counter = 0u;
                base = previous;
            }
            if (counter != 0xffffu)
                counter = (counter + 1u) & 0xffffu;
            square = counter * counter;
            wide = (uint64_t)square * (uint64_t)coefficient;
            if ((wide >> 32) == 0u) {
                uint32_t sum = base + (uint32_t)(wide >> 16);
                if ((int32_t)sum <= (int32_t)published)
                    published = sum & 0xffffu;
            }
        }
    }
    f33_set_current_limit_request(7u, published);
    camry_write8(state, mode);
    camry_write16(state + 2u, counter);
    camry_write16(state + 4u, base);
    camry_write16(state + 6u, published);
}

static uint32_t f33_nvm_read_logical_result(uint32_t logical, uint32_t output) {
    uint32_t handle = logical & 0xffffu;
    camry_write8(output, camry_read8(0xfebf6000u + (handle << 1)));
    return 0u;
}

static uint32_t f33_nvm_check_logical_handle(
    uint32_t logical, uint32_t api, uint32_t allow_zero) {
    uint32_t handle = logical & 0xffffu;
    uint32_t limit = (camry_read16(camry_tp + 11788u) - 1u) & 0xffffu;
    (void)api;
    if (handle >= 2u) {
        if (handle <= limit)
            return 0u;
    } else if ((allow_zero & 0xffu) == 1u && handle == 0u) {
        return 0u;
    }
    return 1u;
}

static uint32_t f33_nvm_check_not_pending(uint32_t logical, uint32_t api) {
    uint32_t handle = logical & 0xffffu;
    uint32_t output = 0xfebe1fffu;
    (void)api;
    f33_nvm_read_logical_result(handle, output);
    if (camry_read8(output) != 2u)
        return 0u;
    return 1u;
}

static uint32_t f33_nvm_check_buffer_argument(
    uint32_t logical, uint32_t buffer, uint32_t api) {
    uint32_t handle = logical & 0xffffu;
    uint32_t kind;
    (void)api;
    if (buffer != 0u)
        return 0u;
    kind = camry_read8(camry_tp + 11792u + (handle << 4) + 4u);
    if (kind == 4u || kind == 2u)
        return 0u;
    return 1u;
}

static uint32_t f33_nvm_check_read_request(uint32_t logical, uint32_t buffer) {
    uint32_t pending;
    uint32_t argument;
    if (f33_nvm_check_logical_handle(logical, 6u, 0u) != 0u)
        return 1u;
    pending = f33_nvm_check_not_pending(logical, 6u);
    argument = f33_nvm_check_buffer_argument(logical, buffer, 6u);
    if (pending == 0u && argument == 0u)
        return 0u;
    return 1u;
}

typedef struct {
    uint32_t operation;
    uint16_t handle;
    uint16_t unused;
    uint32_t first_buffer;
    uint32_t second_buffer;
} F33QueueRequest;

static void f33_nvm_record_invalid_reset(void);
static uint32_t f33_nvm_check_slot_partition(uint32_t index, uint32_t queue);
static uint32_t f33_nvm_pop_queue_head_to(uint32_t queue, uint16_t *index);

static uint32_t f33_nvm_route_byte(uint32_t handle) {
    return camry_read8(camry_tp + ((handle & 0xffffu) << 4) + 0x2e11u);
}

static uint32_t f33_nvm_uses_reserved_queue(uint32_t handle, uint32_t operation) {
    if (f33_nvm_route_byte(handle) != 0u)
        return 0u;
    if (operation == 0x22aa8a36u || operation == 0x1c646989u)
        return 1u;
    return 0u;
}

static void f33_nvm_mark_queue_service(uint32_t code) {
    camry_write8(0xfebf60fau + (code & 0xffu), 2u);
}

static uint32_t f33_nvm_append_queue_slot(uint32_t queue, uint32_t index) {
    uint32_t id = queue & 0xffffu;
    uint32_t slot = index & 0xffffu;
    uint32_t header = 0xfebf68e8u + (id << 2);
    uint32_t tail = camry_read16(header + 2u);
    if (tail == 0xffffu) {
        camry_write16(header, slot);
    } else if (f33_nvm_check_slot_partition(tail, id) != 0u) {
        return 1u;
    } else {
        camry_write16(0xfebf6128u + (tail << 4) + 14u, slot);
    }
    camry_write16(header + 2u, slot);
    camry_write16(0xfebf6128u + (slot << 4) + 14u, 0xffffu);
    return 0u;
}

static void f33_nvm_copy_operation_to_slot(uint32_t slot, const F33QueueRequest *request) {
    camry_write32(slot, request->operation);
    camry_write16(slot + 12u, request->handle);
    camry_write32(slot + 4u, request->first_buffer);
    camry_write32(slot + 8u, request->second_buffer);
}

static uint32_t f33_nvm_append_operation(
    uint32_t queue, uint32_t index, const F33QueueRequest *request) {
    uint32_t status = f33_nvm_append_queue_slot(queue, index);
    if (status != 0u)
        return status;
    f33_nvm_copy_operation_to_slot(0xfebf6128u + ((index & 0xffffu) << 4), request);
    return 0u;
}

static uint32_t f33_nvm_enqueue_pooled_operation(const F33QueueRequest *request) {
    uint32_t handle = request->handle;
    uint16_t slot = 0xffffu;
    uint32_t selector;
    uint32_t base;
    uint32_t offset;
    uint32_t free_count;
    uint32_t used_count;
    uint32_t status;
    if (f33_nvm_uses_reserved_queue(handle, request->operation) == 1u) {
        selector = 0u;
        base = 2u;
        offset = 0u;
        free_count = 0xfebf6ae4u;
        used_count = 0xfebf6ae8u;
    } else {
        selector = 1u;
        base = 3u;
        offset = f33_nvm_route_byte(handle);
        free_count = 0xfebf6ae6u;
        used_count = 0xfebf6aeau;
    }
    status = f33_nvm_pop_queue_head_to(selector, &slot);
    if (status == 0u) {
        uint32_t address = 0xfebf6128u + ((uint32_t)slot << 4);
        if (camry_read32(address) != 0x9da70ae7u) {
            f33_nvm_record_invalid_reset();
            return 1u;
        }
        status = f33_nvm_append_operation((base + offset) & 0xffffu, slot, request);
        if (status != 0u)
            return status;
        camry_write16(free_count, (camry_read16(free_count) - 1u) & 0xffffu);
        camry_write16(used_count, (camry_read16(used_count) + 1u) & 0xffffu);
        return 0u;
    }
    if (camry_read16(free_count) == 0u) {
        f33_nvm_mark_queue_service(3u);
        return 1u;
    }
    f33_nvm_record_invalid_reset();
    return 1u;
}

static uint32_t f33_nvm_enqueue_zero_handle_operation(const F33QueueRequest *request) {
    if (camry_read32(0xfebf68d8u) != 0x9da70ae7u) {
        f33_nvm_mark_queue_service(3u);
        return 1u;
    }
    camry_write32(0xfebf68d8u, request->operation);
    camry_write16(0xfebf68dcu, request->handle);
    camry_write32(0xfebf68e0u, request->first_buffer);
    camry_write32(0xfebf68e4u, request->second_buffer);
    return 0u;
}

static void f33_nvm_finish_queued_operation(uint32_t selector) {
    (void)selector;
}

void f33_nvm_publish_logical_result(uint32_t logical_handle, uint32_t operation, uint32_t result);

static uint32_t f33_nvm_queue_operation(
    uint32_t operation, uint32_t logical, uint32_t buffer, uint32_t other) {
    uint32_t handle = logical & 0xffffu;
    F33QueueRequest request;
    uint32_t status;
    request.operation = operation;
    request.handle = (uint16_t)handle;
    request.unused = 0u;
    request.first_buffer = buffer;
    request.second_buffer = other;
    camry_write8(0xfebf60fdu, 1u);
    if (handle == 0u)
        status = f33_nvm_enqueue_zero_handle_operation(&request);
    else
        status = f33_nvm_enqueue_pooled_operation(&request);
    f33_nvm_finish_queued_operation(3u);
    if (status == 0u)
        f33_nvm_publish_logical_result(handle, operation, 2u);
    return status;
}

uint32_t f33_nvm_enqueue_read(uint32_t logical, uint32_t destination) {
    uint32_t handle = logical & 0xffffu;
    uint32_t status = 1u;
    if (f33_nvm_check_read_request(handle, destination) == 0u)
        status = f33_nvm_queue_operation(0xa1a62093u, handle, destination, 0u);
    return status;
}

static uint32_t f33_nvm_check_write_inhibit(uint32_t logical) {
    uint32_t handle = logical & 0xffffu;
    camry_write8(0xfebf6100u, 1u);
    if (camry_read8(0xfebf6000u + (handle << 1) + 1u) != 1u)
        return 0u;
    f33_nvm_mark_queue_service(6u);
    return 1u;
}

static uint32_t f33_nvm_check_write_request(uint32_t logical, uint32_t source) {
    if (f33_nvm_check_logical_handle(logical, 7u, 0u) != 0u)
        return 1u;
    if (f33_nvm_check_not_pending(logical, 7u) != 0u)
        return 1u;
    if (f33_nvm_check_buffer_argument(logical, source, 7u) != 0u)
        return 1u;
    return f33_nvm_check_write_inhibit(logical);
}

uint32_t f33_nvm_enqueue_write(uint32_t logical, uint32_t source) {
    uint32_t handle = logical & 0xffffu;
    if (f33_nvm_check_write_request(handle, source) != 0u)
        return 1u;
    return f33_nvm_queue_operation(0x22aa8a36u, handle, 0u, source);
}

static uint32_t f33_nvm_get_family0_completion(uint32_t object) {
    uint32_t index = object & 0xffffu;
    uint32_t count = camry_read16((3u << 16) - 21136u);
    if (index >= count)
        return 0xa5u;
    return camry_read8(camry_gp + index + 19256u);
}

static uint32_t f33_nvm_handle_family1_read_result(uint32_t result, uint32_t logical) {
    uint32_t handle = logical & 0xffffu;
    uint32_t object = camry_read8(0x2b010u + (handle << 1));
    uint32_t slot = object & 3u;
    uint32_t descriptor = 0x2af0cu + (object << 3);
    uint32_t first = camry_read16(descriptor + 2u);
    uint32_t payload = camry_read16(descriptor);
    uint32_t mask_address = camry_gp + 20120u + (slot << 2);
    uint32_t mask = camry_read32(mask_address);
    uint32_t copy;
    uint32_t completed = 0u;
    uint32_t retry_out;
    uint32_t index;
    uint32_t failed;
    uint32_t base;
    uint32_t destination;
    result &= 0xffu;
    if (handle == first) {
        copy = 0u;
        mask = 0u;
    } else if (handle == ((first + 4u) & 0xffffffffu)) {
        copy = 1u;
    } else if (handle == ((first + 8u) & 0xffffffffu)) {
        copy = 2u;
    } else {
        camry_write32(mask_address, 0x5a005au + 23040u);
        return 0u;
    }
    if (result == 0u) {
        retry_out = 0u;
    } else {
        uint32_t retry = camry_read8(camry_gp + 20116u);
        if (retry < 2u) {
            uint32_t stage = camry_gp + 21256u + (((slot * 3u) + copy) << 5);
            f33_nvm_enqueue_read(handle, stage);
            retry_out = (retry + 1u) & 0xffu;
            completed = 0x5au;
        } else {
            retry_out = 0u;
            mask |= 0x5au << ((copy << 3) & 31u);
        }
    }
    camry_write8(camry_gp + 20116u, retry_out);
    if (completed == 0x5au || copy != 2u) {
        camry_write32(mask_address, mask);
        return 0u;
    }
    failed = 0u;
    for (index = 0u; index < payload; index = (index + 1u) & 0xffffu) {
        uint32_t address = camry_gp + 21256u + (slot * 96u) + index;
        uint32_t raw = camry_read8(address);
        uint32_t copy55 = camry_read8(address + 32u) ^ 0x55u;
        uint32_t copy_aa = camry_read8(address + 64u) ^ 0xaau;
        if (raw == copy_aa && (mask & 0x5a005au) == 0u)
            continue;
        if (raw == copy55 && (mask & 0x5a5au) == 0u)
            continue;
        if (copy55 == copy_aa && (mask & (0x5a005au + 22950u)) == 0u)
            camry_write8(address, copy55);
        else
            failed = 0x5au;
    }
    if (failed == 0u) {
        destination = camry_read32(descriptor + 4u);
        base = camry_gp + 21256u + (slot * 96u);
        for (index = 0u; (int32_t)index < (int32_t)payload; index++)
            camry_write8(destination + index, camry_read8(base + index));
        camry_write8(camry_gp + object + 19288u, 0x5au);
    } else {
        camry_write8(camry_gp + object + 19288u, 0xa5u);
    }
    camry_write32(mask_address, mask);
    return 0x5au;
}

static uint32_t f33_nvm_handle_family1_write_result(uint32_t result, uint32_t logical) {
    uint32_t handle = logical & 0xffffu;
    uint32_t object = camry_read8(0x2b010u + (handle << 1));
    uint32_t descriptor = 0x2af0cu + (object << 3);
    uint32_t first = camry_read16(descriptor + 2u);
    uint32_t slot = object & 3u;
    uint32_t mask_address = camry_gp + 20120u + (slot << 2);
    uint32_t mask = camry_read32(mask_address);
    uint32_t copy;
    uint32_t completion;
    result &= 0xffu;
    if (handle == first) {
        copy = 0u;
        mask = 0u;
    } else if (handle == ((first + 4u) & 0xffffffffu)) {
        copy = 1u;
    } else if (handle == ((first + 8u) & 0xffffffffu)) {
        copy = 2u;
    } else {
        camry_write32(mask_address, 0x5a5a5au);
        return 0u;
    }
    if (result != 0u)
        mask |= 0x5au << ((copy << 3) & 31u);
    if (copy != 2u) {
        camry_write32(mask_address, mask);
        return 0u;
    }
    completion = mask == 0u ? 0x5au : 0xa5u;
    camry_write8(camry_gp + object + 19288u, completion);
    camry_write32(mask_address, mask);
    return 0x5au;
}

static uint32_t f33_nvm_handle_family0_write_result(uint32_t result, uint32_t logical) {
    uint32_t handle = logical & 0xffffu;
    uint32_t object = camry_read8(0x2b010u + (handle << 1));
    uint32_t descriptor = 0x2ad8cu + (object * 12u);
    uint32_t origin = camry_read16(descriptor + 4u);
    uint32_t last = (origin + camry_read16(descriptor + 2u) - 1u) & 0xffffu;
    uint32_t cursor_address = camry_gp + 19304u + (object << 1);
    uint32_t cursor = camry_read16(cursor_address);
    uint32_t completion;
    result &= 0xffu;
    if (cursor != 0xffffu) {
        uint32_t next = (cursor + 1u) & 0xffffu;
        if (next > last)
            cursor = origin;
        else
            cursor = next;
    } else {
        cursor = origin;
    }
    if (result == 0u && handle == cursor) {
        camry_write16(cursor_address, cursor);
        completion = 0x5au;
    } else {
        completion = 0xa5u;
    }
    camry_write8(camry_gp + object + 19256u, completion);
    return 0x5au;
}

static uint32_t f33_nvm_handle_family0_read_result(
    uint32_t result, uint32_t logical, uint32_t record) {
    (void)result;
    (void)logical;
    (void)record;
    return 0u;
}

static uint32_t f33_nvm_route_application_result(
    uint32_t event, uint32_t logical, uint32_t result) {
    uint32_t handle = logical & 0xffffu;
    uint32_t route = camry_read16(0x2b010u + (handle << 1));
    uint32_t object = route & 0xffu;
    uint32_t family = route & 0xff00u;
    uint32_t status;
    uint32_t descriptor;
    event &= 0xffu;
    result &= 0xffu;
    if (family == 0u) {
        if (f33_nvm_get_family0_completion(object) != 0xffu)
            return 0u;
        descriptor = 0x2ad8cu + (object * 12u);
        if (camry_read16(descriptor + 4u) == 0xffffu)
            return 0u;
        if (event == 6u)
            status = f33_nvm_handle_family0_read_result(result, handle, camry_gp + 21640u);
        else if (event == 7u)
            status = f33_nvm_handle_family0_write_result(result, handle);
        else
            return 0u;
        if (status == 0x5au)
            camry_write8(camry_gp + 20112u, 0u);
        return 0u;
    }
    if (family != 0x100u)
        return 0u;
    if (f33_nvm_get_family1_completion(object) != 0xffu)
        return 0u;
    descriptor = 0x2af0cu + (object << 3);
    if (camry_read16(descriptor + 2u) == 0xffffu)
        return 0u;
    if (event == 6u)
        status = f33_nvm_handle_family1_read_result(result, handle);
    else if (event == 7u)
        status = f33_nvm_handle_family1_write_result(result, handle);
    else
        return 0u;
    if (status == 0x5au)
        camry_write8(camry_gp + 20113u, 0u);
    return 0u;
}

static void f33_nvm_notify_zero_handle_result(uint32_t operation, uint32_t result) {
    uint32_t narrowed = result & 0xffu;
    uint32_t event = f33_lookup_u32_value_by_key(operation, 0xffu, camry_tp + 14288u);
    uint32_t callback = camry_read32(camry_tp + 11772u);
    (void)event;
    if (narrowed == 2u || callback == 0u)
        return;
}

static void f33_nvm_notify_logical_result(
    uint32_t logical, uint32_t operation, uint32_t result) {
    uint32_t handle = logical & 0xffffu;
    uint32_t narrowed = result & 0xffu;
    uint32_t callback = camry_read32(camry_tp + 11776u);
    uint32_t field = camry_read16(camry_tp + (handle << 4) + 0x2e1au);
    if (((field >> 5) & 1u) != 0u)
        (void)handle;
    if (narrowed == 2u || callback == 0u)
        return;
    f33_nvm_route_application_result(
        f33_lookup_u32_value_by_key(operation, 0xffu, camry_tp + 14288u),
        handle,
        narrowed);
}

static void f33_nvm_route_logical_result(
    uint32_t logical, uint32_t operation, uint32_t result) {
    if ((logical & 0xffffu) == 0u)
        f33_nvm_notify_zero_handle_result(operation, result);
    else
        f33_nvm_notify_logical_result(logical, operation, result);
}

void f33_nvm_publish_logical_result(
    uint32_t logical_handle, uint32_t operation, uint32_t result) {
    uint32_t handle = logical_handle & 0xffffu;
    camry_write8(0xfebf6000u + (handle << 1), result);
    f33_nvm_route_logical_result(handle, operation, result);
}

static int32_t gp_s16(int32_t displacement) {
    return sign_half(camry_read16(camry_gp + (uint32_t)displacement));
}

static int32_t larger_s32(int32_t left, int32_t right) {
    return left >= right ? left : right;
}

static int32_t saturate_symmetric_s16(int32_t value) {
    if (value <= -32767)
        return -32767;
    if (value > 32767)
        return 32767;
    return sign_half((uint32_t)value);
}

/* 0x7025c. Points are int16 x, uint16 y, four bytes apart, ended by x == 32767.
 * x is the low half of the argument. A point at or left of x returns its y.
 * A later point above x interpolates from the previous point with signed
 * DIVQ of the low 32 bits of the product. */
static uint32_t map_s16_u16_points(uint32_t table, int32_t raw_x) {
    int32_t x = sign_half((uint32_t)raw_x);
    int32_t first_x = sign_half(camry_read16(table));
    uint32_t index = 0u;
    if (first_x == 32767 || first_x >= x)
        return camry_read16(table + 2u);
    for (;;) {
        uint32_t point = table + (index << 2);
        int32_t point_x = sign_half(camry_read16(point));
        int32_t previous_x;
        int32_t slope;
        int32_t quotient;
        uint32_t previous_y;
        uint32_t point_y;
        if (point_x == 32767)
            return camry_read16(point - 2u);
        if (point_x <= x) {
            index += 1u;
            continue;
        }
        previous_x = sign_half(camry_read16(point - 4u));
        previous_y = camry_read16(point - 2u);
        point_y = camry_read16(point + 2u);
        slope = point_x - previous_x;
        quotient = (int32_t)((int64_t)(x - previous_x) *
                             (int64_t)((int32_t)point_y - (int32_t)previous_y));
        if (slope != 0) {
            if (quotient == (int32_t)0x80000000 && slope == -1)
                quotient = (int32_t)0x80000000;
            else
                quotient = quotient / slope;
        }
        return (previous_y + (uint32_t)quotient) & 0xffffu;
    }
}

static uint32_t f33_check_thermal_raw_estimate_margin(void) {
    int32_t common = sign_half(camry_read16(0x2fb54u));
    int32_t adjusted[5];
    uint32_t mapped[5];
    uint32_t tables[5] = {0x2b4e4u, 0x2b3c4u, 0x2b554u, 0x2b32cu, 0x2b2b8u};
    uint32_t minimum;
    uint32_t status = 0x5au;
    uint32_t index;
    uint32_t base = camry_gp - 18512u;
    adjusted[0] = saturate_symmetric_s16(
        larger_s32(gp_s16(-18526), gp_s16(-18542)) + common + sign_half(camry_read16(0x2fb56u)));
    adjusted[1] = saturate_symmetric_s16(
        larger_s32(gp_s16(-18594), gp_s16(-18614)) + common + sign_half(camry_read16(0x2fb58u)));
    adjusted[2] = saturate_symmetric_s16(
        larger_s32(gp_s16(-18434), gp_s16(-18450)) + common + sign_half(camry_read16(0x2fb5au)));
    adjusted[3] = saturate_symmetric_s16(gp_s16(-18668) + common + sign_half(camry_read16(0x2fb5cu)));
    adjusted[4] = saturate_symmetric_s16(gp_s16(-18768) + common + sign_half(camry_read16(0x2fb5eu)));
    for (index = 0u; index < 5u; index += 1u)
        mapped[index] = map_s16_u16_points(tables[index], adjusted[index]);
    minimum = mapped[0];
    for (index = 1u; index < 5u; index += 1u) {
        if (mapped[index] < minimum)
            minimum = mapped[index];
    }
    if (minimum >= camry_read16(0x2fb60u))
        status = 0xa5u;
    for (index = 0u; index < 5u; index += 1u)
        camry_write16(base + 4u + (index << 1), (uint32_t)adjusted[index]);
    for (index = 0u; index < 5u; index += 1u)
        camry_write16(base + 14u + (index << 1), mapped[index]);
    camry_write16(base + 24u, minimum);
    camry_write8(base + 1u, status);
    return status;
}

static uint32_t f33_check_thermal_contribution_count(void) {
    int32_t groups[5];
    uint32_t mapped[5];
    uint32_t tables[5] = {0x2fb64u, 0x2fb78u, 0x2fb8cu, 0x2fba0u, 0x2fbb4u};
    uint32_t maximum;
    uint32_t status = 0x5au;
    uint32_t index;
    uint32_t base = camry_gp - 18512u;
    uint32_t half = camry_read16(camry_gp - 20340u) >> 1;
    groups[0] = larger_s32(
        larger_s32(gp_s16(-18544), gp_s16(-18532 + 4)),
        larger_s32(gp_s16(-18546), gp_s16(-18532 + 2)));
    groups[1] = larger_s32(
        larger_s32(gp_s16(-18622), gp_s16(-18604 + 2)),
        larger_s32(gp_s16(-18620), gp_s16(-18604 + 4)));
    groups[2] = larger_s32(
        larger_s32(gp_s16(-18448), gp_s16(-18436 + 4)),
        larger_s32(gp_s16(-18446), gp_s16(-18436 + 6)));
    groups[3] = larger_s32(gp_s16(-18672 + 6), gp_s16(-18672 + 8));
    groups[4] = gp_s16(-18772 + 6);
    groups[4] = larger_s32(groups[4], gp_s16(-18772 + 8));
    groups[4] = larger_s32(groups[4], gp_s16(-18772 + 10));
    groups[4] = larger_s32(groups[4], gp_s16(-18772 + 12));
    groups[4] = larger_s32(groups[4], gp_s16(-18772 + 14));
    groups[4] = larger_s32(groups[4], gp_s16(-18772 + 16));
    for (index = 0u; index < 5u; index += 1u)
        mapped[index] = map_s16_u16_points(tables[index], groups[index]);
    maximum = mapped[0];
    for (index = 1u; index < 5u; index += 1u) {
        if (mapped[index] > maximum)
            maximum = mapped[index];
    }
    if (maximum < half)
        status = 0xa5u;
    for (index = 0u; index < 5u; index += 1u)
        camry_write16(base + 26u + (index << 1), (uint32_t)groups[index]);
    for (index = 0u; index < 5u; index += 1u)
        camry_write16(base + 36u + (index << 1), mapped[index]);
    camry_write16(base + 46u, maximum);
    camry_write8(base + 2u, status);
    return status;
}

void f33_update_thermal_history_qualification(void) {
    uint32_t saved = camry_read16(camry_gp - 20636u);
    uint32_t margin = f33_check_thermal_raw_estimate_margin();
    uint32_t count = f33_check_thermal_contribution_count();
    uint32_t status = 0x5au;
    if (margin == 0xa5u && count == 0xa5u && saved == 0u)
        status = 0xa5u;
    camry_write8(camry_gp - 18512u, status);
}

static void f33_nvm_clear_queue_headers(void) {
    uint32_t index = 0u;
    while (index < 127u) {
        uint32_t header = 0xfebf68e8u + (index << 2);
        camry_write16(header, 0xffffu);
        camry_write16(header + 2u, 0xffffu);
        index += 1u;
    }
}

static void f33_nvm_notify_reset_result(uint32_t logical, uint32_t operation) {
    uint32_t handle = logical & 0xffffu;
    if (handle != camry_read16(0xfebf6126u))
        f33_nvm_publish_logical_result(handle, operation, 6u);
}

/* 0x796be then 0x797f6. Code 0..2 merges one ROM mask word into FEBF6CB4
 * and accumulates the paired value for every hit among the three rows. */
static void f33_nvm_merge_reset_status(uint32_t code) {
    uint32_t narrowed = code & 0xffu;
    uint32_t base = 0xfebf6cb4u;
    uint32_t saved;
    uint32_t state;
    uint32_t accumulated = 0u;
    uint32_t index;
    if (narrowed >= 3u)
        return;
    saved = camry_read32(base);
    camry_write32(base, saved | camry_read32(camry_tp + (narrowed << 3) + 16080u));
    camry_write32(base + 4u, 0u);
    state = camry_read32(base);
    for (index = 0u; index < 3u; index += 1u) {
        uint32_t row = camry_tp + (index << 3) + 16080u;
        if ((state & camry_read32(row)) != 0u)
            accumulated |= camry_read32(row + 4u);
        camry_write32(base + 4u, accumulated);
    }
}

static void f33_nvm_record_invalid_reset(void) {
    f33_nvm_merge_reset_status(2u);
    camry_write8(0xfebf6102u, 15u);
}

static void f33_nvm_reset_slot_range(uint32_t queue, uint32_t first, uint32_t last, uint32_t notify) {
    uint32_t index = first & 0xffffu;
    uint32_t end = last & 0xffffu;
    uint32_t limit = (camry_read16(camry_tp + 11788u) - 1u) & 0xffffu;
    uint32_t header = 0xfebf68e8u + ((queue & 0xffffu) << 2);
    camry_write16(header, index);
    camry_write16(header + 2u, end);
    while (index <= end) {
        uint32_t slot = 0xfebf6128u + (index << 4);
        uint32_t next = (index + 1u) & 0xffffu;
        if (notify != 0u) {
            uint32_t operation = camry_read32(slot);
            if (operation != 0x9da70ae7u) {
                uint32_t logical = camry_read16(slot + 12u);
                if (logical > limit || logical < 2u)
                    f33_nvm_record_invalid_reset();
                else
                    f33_nvm_notify_reset_result(logical, operation);
            }
        }
        camry_write32(slot, 0x9da70ae7u);
        camry_write32(slot + 4u, 0u);
        camry_write32(slot + 8u, 0u);
        camry_write16(slot + 12u, 0xffffu);
        camry_write16(slot + 14u, next);
        if (index == end)
            break;
        index = next;
    }
    camry_write16(0xfebf6128u + (end << 4) + 14u, 0xffffu);
}

static void f33_nvm_reset_pooled_queues(uint32_t notify) {
    uint32_t mode = notify & 0xffu;
    f33_nvm_clear_queue_headers();
    if (mode == 1u) {
        f33_nvm_reset_slot_range(0u, 0x7au, 0x7au, 1u);
        f33_nvm_reset_slot_range(1u, 0u, 0x79u, 1u);
    } else {
        f33_nvm_reset_slot_range(0u, 0x7au, 0x7au, 0u);
        f33_nvm_reset_slot_range(1u, 0u, 0x79u, 0u);
    }
    camry_write16(0xfebf6ae4u, 1u);
    camry_write16(0xfebf6ae6u, 0x7au);
    camry_write16(0xfebf6ae8u, 0u);
    camry_write16(0xfebf6aeau, 0u);
}

static void f33_nvm_reset_zero_handle_operation(uint32_t notify) {
    uint32_t operation = camry_read32(0xfebf68d8u);
    if ((notify & 0xffu) == 1u && operation != 0x9da70ae7u)
        f33_nvm_notify_reset_result(0u, operation);
    camry_write32(0xfebf68d8u, 0x9da70ae7u);
    camry_write16(0xfebf68dcu, 0xffffu);
    camry_write32(0xfebf68e0u, 0u);
    camry_write32(0xfebf68e4u, 0u);
}

void f33_nvm_initialize_queues(void) {
    f33_nvm_reset_pooled_queues(0u);
    f33_nvm_reset_zero_handle_operation(0u);
}

void f33_nvm_reset_queues_notifying(void) {
    f33_nvm_reset_pooled_queues(1u);
    f33_nvm_reset_zero_handle_operation(1u);
}

static uint32_t f33_nvm_check_queue_empty(uint32_t header, uint8_t *empty) {
    uint32_t head = camry_read16(header);
    uint32_t tail = camry_read16(header + 2u);
    if (head == 0xffffu) {
        if (tail == 0xffffu) {
            *empty = 1u;
            return 0u;
        }
    } else if (tail != 0xffffu) {
        *empty = 0u;
        return 0u;
    }
    f33_nvm_record_invalid_reset();
    return 1u;
}

static uint32_t f33_nvm_check_slot_partition(uint32_t index, uint32_t queue) {
    uint32_t slot = index & 0xffffu;
    uint32_t id = queue & 0xffffu;
    uint32_t lower = (id == 0u || id == 2u) ? 0x7au : 0u;
    uint32_t upper = (id == 0u || id == 2u) ? 0x7au : 0x79u;
    if (slot > upper || slot < lower) {
        f33_nvm_record_invalid_reset();
        return 1u;
    }
    return 0u;
}

static uint32_t f33_nvm_pop_queue_head_to(uint32_t queue, uint16_t *index) {
    uint32_t id = queue & 0xffffu;
    uint32_t header = 0xfebf68e8u + (id << 2);
    uint8_t empty = 0u;
    uint32_t head;
    if (f33_nvm_check_queue_empty(header, &empty) != 0u || empty != 0u)
        return 1u;
    head = camry_read16(header);
    if (f33_nvm_check_slot_partition(head, id) != 0u)
        return 1u;
    f33_nvm_unlink_queue_slot(header, head, 0xffffu);
    *index = (uint16_t)head;
    return 0u;
}

uint32_t f33_nvm_pop_queue_head(uint32_t queue, uint32_t index) {
    uint16_t slot = 0u;
    uint32_t status = f33_nvm_pop_queue_head_to(queue, &slot);
    if (status == 0u)
        camry_write16(index, slot);
    return status;
}
