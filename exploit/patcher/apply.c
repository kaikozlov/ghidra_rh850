#include "../common/runtime.h"
#include "../common/telemetry.h"
#include "flash_backend.h"

#define FIELD_TARGET_BLOCK      0x0200u
#define FIELD_TARGET_OFFSET     0x0201u
#define FIELD_TARGET_BEFORE     0x0202u
#define FIELD_TARGET_AFTER      0x0203u
#define FIELD_TARGET_FLASH_ERR  0x0204u
#define FIELD_PREFIX_CRC        0x0300u
#define FIELD_FIXUP_OLD         0x0301u
#define FIELD_FIXUP_NEW         0x0302u
#define FIELD_FIXUP_FLASH_ERR   0x0303u
#define FIELD_FIXUP_READBACK    0x0304u
#define FIELD_FINAL_RESIDUE     0x0305u

static void copy_flash_block(unsigned int block_base, volatile unsigned char *dst) {
    unsigned int i;
    volatile unsigned char *src = (volatile unsigned char *)block_base;
    for (i = 0u; i < PATCH_BACKEND_BLOCK_SIZE; i++) {
        dst[i] = src[i];
        if ((i & 0x3FFFu) == 0u)
            feed_watchdog();
    }
}

static unsigned int bytes_to_word(const unsigned char *bytes, unsigned int length) {
    unsigned int value = 0u;
    unsigned int i;
    for (i = 0u; i < length; i++)
        value |= ((unsigned int)bytes[i]) << (8u * i);
    return value;
}

static unsigned int live_bytes_to_word(unsigned int address, unsigned int length) {
    volatile unsigned char *p = (volatile unsigned char *)address;
    unsigned int value = 0u;
    unsigned int i;
    for (i = 0u; i < length; i++)
        value |= ((unsigned int)p[i]) << (8u * i);
    return value;
}

static int live_bytes_equal(unsigned int address, const unsigned char *expected, unsigned int length) {
    volatile unsigned char *p = (volatile unsigned char *)address;
    unsigned int i;
    for (i = 0u; i < length; i++) {
        if (p[i] != expected[i])
            return 0;
    }
    return 1;
}

static void store_le_word(volatile unsigned char *dst, unsigned int value) {
    dst[0] = (unsigned char)(value >> 0);
    dst[1] = (unsigned char)(value >> 8);
    dst[2] = (unsigned char)(value >> 16);
    dst[3] = (unsigned char)(value >> 24);
}

unsigned int run_apply(const struct patch_config_v1 *cfg) {
    volatile unsigned char *buffer = flash_work_buffer();
    unsigned int observed;
    unsigned int patch_offset;
    unsigned int crc_prefix;
    unsigned int old_fixup;
    unsigned int new_fixup;
    unsigned int fixup_offset;
    unsigned int readback;
    unsigned int final_residue;
    unsigned int i;
    int flash_err;

    /* Re-check immediately before the first persistent write. */
    if (!verify_patch_preimage(cfg, &observed)) {
        telemetry_error(ERR_PATCH_PREIMAGE, observed);
        return ERR_PATCH_PREIMAGE;
    }

    telemetry_stage(STAGE_APPLY_TARGET);
    patch_offset = cfg->patch_va - cfg->patch_block_base;
    telemetry_value(TAG_APPLY, FIELD_TARGET_BLOCK, cfg->patch_block_base);
    telemetry_value(TAG_APPLY, FIELD_TARGET_OFFSET, patch_offset);
    telemetry_value(TAG_APPLY, FIELD_TARGET_BEFORE, observed);

    copy_flash_block(cfg->patch_block_base, buffer);
    for (i = 0u; i < cfg->patch_len; i++)
        buffer[patch_offset + i] = cfg->replacement[i];
    telemetry_value(TAG_APPLY, FIELD_TARGET_AFTER, bytes_to_word(cfg->replacement, cfg->patch_len));

    flash_err = flash_block_rmw(cfg->patch_block_base);
    telemetry_value(TAG_APPLY, FIELD_TARGET_FLASH_ERR, (unsigned int)flash_err);
    if (flash_err != 0) {
        telemetry_error(ERR_TARGET_RMW, (unsigned int)flash_err);
        return ERR_TARGET_RMW;
    }

    readback = live_bytes_to_word(cfg->patch_va, cfg->patch_len);
    if (!live_bytes_equal(cfg->patch_va, cfg->replacement, cfg->patch_len)) {
        telemetry_value(TAG_APPLY, FIELD_TARGET_AFTER, readback);
        telemetry_error(ERR_TARGET_READBACK, readback);
        return ERR_TARGET_READBACK;
    }
    telemetry_value(TAG_APPLY, FIELD_TARGET_AFTER, readback);

    /* CRC is intentionally computed from LIVE CodeFlash only after target RMW. */
    telemetry_stage(STAGE_APPLY_CRC);
    feed_watchdog();
    crc_prefix = crc32_flash_range(cfg->crc_start, cfg->crc_fixup_va);
    new_fixup = crc_prefix ^ 0xFFFFFFFFu;
    old_fixup = read_le_word(cfg->crc_fixup_va);
    telemetry_value(TAG_CRC, FIELD_PREFIX_CRC, crc_prefix);
    telemetry_value(TAG_CRC, FIELD_FIXUP_OLD, old_fixup);
    telemetry_value(TAG_CRC, FIELD_FIXUP_NEW, new_fixup);

    copy_flash_block(cfg->crc_fixup_block_base, buffer);
    fixup_offset = cfg->crc_fixup_va - cfg->crc_fixup_block_base;
    store_le_word(buffer + fixup_offset, new_fixup);

    flash_err = flash_block_rmw(cfg->crc_fixup_block_base);
    telemetry_value(TAG_CRC, FIELD_FIXUP_FLASH_ERR, (unsigned int)flash_err);
    if (flash_err != 0) {
        telemetry_error(ERR_FIXUP_RMW, (unsigned int)flash_err);
        return ERR_FIXUP_RMW;
    }

    readback = read_le_word(cfg->crc_fixup_va);
    telemetry_value(TAG_CRC, FIELD_FIXUP_READBACK, readback);
    if (readback != new_fixup) {
        telemetry_error(ERR_FIXUP_READBACK, readback);
        return ERR_FIXUP_READBACK;
    }

    telemetry_stage(STAGE_VERIFY_FINAL);
    feed_watchdog();
    final_residue = crc32_flash_range(cfg->crc_start, cfg->crc_end);
    telemetry_value(TAG_CRC, FIELD_FINAL_RESIDUE, final_residue);
    if (final_residue != cfg->expected_residue) {
        telemetry_error(ERR_FINAL_RESIDUE, final_residue);
        return ERR_FINAL_RESIDUE;
    }

    return 0u;
}
