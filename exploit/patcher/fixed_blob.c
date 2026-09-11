/* Exact-image two-segment CodeFlash installer/remover.
 *
 * Both target spans must live in the same 32 KiB block and outside the
 * application's protected CRC interval. The builder embeds exact expected
 * and replacement bytes; this is deliberately not an arbitrary-write API.
 */
#include "../common/patch_config.h"
#include "../common/runtime.h"
#include "../common/telemetry.h"
#include "flash_backend.h"

#ifndef FIXED_BLOB_TARGET0
#error FIXED_BLOB_TARGET0 is required
#endif
#ifndef FIXED_BLOB_SIZE0
#error FIXED_BLOB_SIZE0 is required
#endif
#ifndef FIXED_BLOB_TARGET1
#error FIXED_BLOB_TARGET1 is required
#endif
#ifndef FIXED_BLOB_SIZE1
#error FIXED_BLOB_SIZE1 is required
#endif
#ifndef FIXED_BLOB_SOURCE_FIXUP
#error FIXED_BLOB_SOURCE_FIXUP is required
#endif

#define FIXED_BLOB_BLOCK       (FIXED_BLOB_TARGET0 & ~(PATCH_BACKEND_BLOCK_SIZE - 1u))
#define FIXED_BLOB_OFFSET0     (FIXED_BLOB_TARGET0 - FIXED_BLOB_BLOCK)
#define FIXED_BLOB_OFFSET1     (FIXED_BLOB_TARGET1 - FIXED_BLOB_BLOCK)
#define CRC_START              0x00018000u
#define CRC_END                0x000FFDF0u
#define CRC_FIXUP_VA           0x000FFDECu
#define REQUIRED_STAGE5_VA     0x0008F890u
#define REQUIRED_STAGE5_VALUE  0x01E0u
#define REQUIRED_HOOK_VA       0x0007A272u
#define REQUIRED_HOOK_VALUE    0x1CEEFF80u

#if (FIXED_BLOB_TARGET1 & ~(PATCH_BACKEND_BLOCK_SIZE - 1u)) != FIXED_BLOB_BLOCK
#error fixed blob segments must share one flash block
#endif
#if FIXED_BLOB_TARGET0 + FIXED_BLOB_SIZE0 > FIXED_BLOB_TARGET1
#error fixed blob segments overlap or are not ordered
#endif
#if !((FIXED_BLOB_TARGET0 + FIXED_BLOB_SIZE0 <= CRC_START) || (FIXED_BLOB_TARGET0 >= CRC_END))
#error fixed blob segment 0 overlaps application CRC interval
#endif
#if !((FIXED_BLOB_TARGET1 + FIXED_BLOB_SIZE1 <= CRC_START) || (FIXED_BLOB_TARGET1 >= CRC_END))
#error fixed blob segment 1 overlaps application CRC interval
#endif

#define ERR_FIXED_STAGE5       0x4101u
#define ERR_FIXED_HOOK         0x4102u
#define ERR_FIXED_FIXUP        0x4103u
#define ERR_FIXED_CRC          0x4104u
#define ERR_FIXED_PREIMAGE0    0x4105u
#define ERR_FIXED_PREIMAGE1    0x4106u
#define ERR_FIXED_TARGET_RMW   0x4107u
#define ERR_FIXED_READBACK0    0x4108u
#define ERR_FIXED_READBACK1    0x4109u
#define ERR_FIXED_FINAL_CRC    0x410Au

extern const unsigned char fixed_blob_expected0[];
extern const unsigned char fixed_blob_replacement0[];
extern const unsigned char fixed_blob_expected1[];
extern const unsigned char fixed_blob_replacement1[];

static void require_bytes(volatile unsigned char *live,
                          const unsigned char *expected,
                          unsigned int size, unsigned int error);

/* Keep exploit first: the bootloader enters shellcode offset zero. */
void exploit(void) {
    volatile unsigned char *buffer;
    volatile unsigned char *live0 = (volatile unsigned char *)FIXED_BLOB_TARGET0;
    volatile unsigned char *live1 = (volatile unsigned char *)FIXED_BLOB_TARGET1;
    unsigned int i;
    unsigned int crc;
    int err;

    asm("di");
    runtime_init();
    telemetry_stage(STAGE_BOOT);
    if (*(volatile unsigned short *)REQUIRED_STAGE5_VA != REQUIRED_STAGE5_VALUE) {
        telemetry_error(ERR_FIXED_STAGE5, *(volatile unsigned short *)REQUIRED_STAGE5_VA);
        runtime_halt();
    }
    if (*(volatile unsigned int *)REQUIRED_HOOK_VA != REQUIRED_HOOK_VALUE) {
        telemetry_error(ERR_FIXED_HOOK, *(volatile unsigned int *)REQUIRED_HOOK_VA);
        runtime_halt();
    }
    if (read_le_word(CRC_FIXUP_VA) != FIXED_BLOB_SOURCE_FIXUP) {
        telemetry_error(ERR_FIXED_FIXUP, read_le_word(CRC_FIXUP_VA));
        runtime_halt();
    }
    crc = crc32_flash_range(CRC_START, CRC_END);
    telemetry_value(TAG_PREFLIGHT, 0x0103u, crc);
    if (crc != 0xFFFFFFFFu) {
        telemetry_error(ERR_FIXED_CRC, crc);
        runtime_halt();
    }
    require_bytes(live0, fixed_blob_expected0, FIXED_BLOB_SIZE0, ERR_FIXED_PREIMAGE0);
    require_bytes(live1, fixed_blob_expected1, FIXED_BLOB_SIZE1, ERR_FIXED_PREIMAGE1);
    telemetry_value(TAG_PREFLIGHT, 0x0100u, FIXED_BLOB_SIZE0 + FIXED_BLOB_SIZE1);

#ifndef FIXED_BLOB_WRITE
    telemetry_stage(STAGE_SUCCESS);
    runtime_halt();
#else
    telemetry_stage(STAGE_APPLY_TARGET);
    buffer = flash_work_buffer();
    for (i = 0u; i < PATCH_BACKEND_BLOCK_SIZE; i++)
        buffer[i] = ((volatile unsigned char *)FIXED_BLOB_BLOCK)[i];
    for (i = 0u; i < FIXED_BLOB_SIZE0; i++)
        buffer[FIXED_BLOB_OFFSET0 + i] = fixed_blob_replacement0[i];
    for (i = 0u; i < FIXED_BLOB_SIZE1; i++)
        buffer[FIXED_BLOB_OFFSET1 + i] = fixed_blob_replacement1[i];
    err = flash_block_rmw(FIXED_BLOB_BLOCK);
    if (err != 0) {
        telemetry_error(ERR_FIXED_TARGET_RMW, (unsigned int)err);
        runtime_halt();
    }
    require_bytes(live0, fixed_blob_replacement0, FIXED_BLOB_SIZE0, ERR_FIXED_READBACK0);
    require_bytes(live1, fixed_blob_replacement1, FIXED_BLOB_SIZE1, ERR_FIXED_READBACK1);

    telemetry_stage(STAGE_VERIFY_FINAL);
    crc = crc32_flash_range(CRC_START, CRC_END);
    telemetry_value(TAG_CRC, 0x0305u, crc);
    if (crc != 0xFFFFFFFFu) {
        telemetry_error(ERR_FIXED_FINAL_CRC, crc);
        runtime_halt();
    }
    telemetry_stage(STAGE_SUCCESS);
    runtime_halt();
#endif
}

static void require_bytes(volatile unsigned char *live,
                          const unsigned char *expected,
                          unsigned int size, unsigned int error) {
    unsigned int i;
    for (i = 0u; i < size; i++) {
        if (live[i] != expected[i]) {
            telemetry_error(error, i);
            runtime_halt();
        }
    }
}

#include "../common/runtime.c"
#include "flash_backend.c"
