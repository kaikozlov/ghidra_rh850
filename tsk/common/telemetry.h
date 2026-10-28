#ifndef SECOC_EXPLOIT_TELEMETRY_H
#define SECOC_EXPLOIT_TELEMETRY_H

/* Stage markers are sent as (0xDEAD0000 | stage, 0xCAFEBABE). */
#define STAGE_BOOT             0x10u
#define STAGE_CONFIG           0x11u
#define STAGE_PREFLIGHT        0x12u
#define STAGE_APPLY_TARGET     0x20u
#define STAGE_APPLY_CRC        0x21u
#define STAGE_VERIFY_FINAL     0x22u
#define STAGE_SUCCESS          0x7Fu
#define STAGE_DONE             0xFFu

/* Fail-closed error namespace. */
#define ERR_CONFIG_MAGIC             0x1001u
#define ERR_CONFIG_VERSION           0x1002u
#define ERR_CONFIG_FLAGS             0x1003u
#define ERR_CONFIG_CRC               0x1004u
#define ERR_CONFIG_IMAGE_RANGE       0x1005u
#define ERR_CONFIG_PATCH_RANGE       0x1006u
#define ERR_CONFIG_BLOCK_GEOMETRY    0x1007u
#define ERR_CONFIG_CRC_GEOMETRY      0x1008u
#define ERR_CONFIG_RESIDUE           0x1009u
#define ERR_PATCH_PREIMAGE           0x2001u
#define ERR_APPLY_UNAVAILABLE        0x2002u
#define ERR_TARGET_RMW               0x3001u
#define ERR_TARGET_READBACK          0x3002u
#define ERR_FIXUP_RMW                0x3003u
#define ERR_FIXUP_READBACK           0x3004u
#define ERR_FINAL_RESIDUE            0x3005u

/* Telemetry tags. Low byte is tag; upper 24 bits are a tag-local field ID. */
#define TAG_RUNTIME            0xB0u
#define TAG_CONFIG             0xB1u
#define TAG_PREFLIGHT          0xB2u
#define TAG_APPLY              0xC0u
#define TAG_CRC                0xC1u
#define TAG_ERROR              0xEEu

#endif
