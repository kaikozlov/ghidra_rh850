/* Resolve the request-signer ABI from the running ECU's 1 MiB CodeFlash.
 *
 * The host-side tss3_request_signer_contract.py remains the descriptive
 * checker. This freestanding resolver carries only the machine invariants
 * needed to materialize the 33-word boot/config handoff in retained RAM. Every
 * candidate must be unique; an unknown or ambiguous image fails before the
 * resident or helper is installed.
 */
#include <stdint.h>

#define CODEFLASH_SIZE 0x100000u
#define RESIDENT_BASE 0xFEBFF9F0u
#define HELPER_BASE 0xFEF07C00u
#define HELPER_END 0xFEF08000u
#define HELPER_CODE_LIMIT 0x398u

#define ARRAY_SIZE(values) (sizeof(values) / sizeof((values)[0]))
#define BOOT_CALL_COUNT 5u

enum config_word {
    CONFIG_WORD_APP_CONTEXT,
    CONFIG_WORD_STARTUP_FIRST,
    CONFIG_WORD_STARTUP_AFTER,
    CONFIG_WORD_STARTUP_FINAL,
    CONFIG_WORD_TIMING_FLAG,
    CONFIG_WORD_TICK_COUNTER,
    CONFIG_WORD_FG_TIMING_BEGIN,
    CONFIG_WORD_FG_PRE_0,
    CONFIG_WORD_FG_PRE_1,
    CONFIG_WORD_FG_PRE_2,
    CONFIG_WORD_FG_PRE_3,
    CONFIG_WORD_FG_AGGREGATE,
    CONFIG_WORD_FG_POST_0,
    CONFIG_WORD_FG_POST_1,
    CONFIG_WORD_FG_POST_2,
    CONFIG_WORD_FG_TIMING_END,
    CONFIG_WORD_STATE_BASE,
    CONFIG_WORD_SCRATCH_BASE,
    CONFIG_WORD_RING_BASE,
    CONFIG_WORD_RING_PRODUCER,
    CONFIG_WORD_AUTH_RESET,
    CONFIG_WORD_AUTH_TRIP,
    CONFIG_WORD_FRESHNESS_ENCODE,
    CONFIG_WORD_COMMAND5_SYNC,
    CONFIG_WORD_LOWER_CAN_WRITE,
    CONFIG_WORD_COMMAND5_GLOBALS,
    CONFIG_WORD_RESPONSE_HANDLE,
    CONFIG_WORD_RUNTIME_GEOMETRY,
    CONFIG_WORD_COUNT,
};
_Static_assert(CONFIG_WORD_COUNT == 28, "signer config word count");

#define FOREGROUND_SIZE 92u

/* Each run is {size, offset, fixed bytes...}; size zero ends the pattern. */
static const uint8_t foreground_pattern[] = {
    6, 0x00, 0x80, 0x07, 0x61, 0x00, 0xc0, 0xe7,
    4, 0x08, 0xe2, 0xfd, 0xc0, 0xa7,
    2, 0x0e, 0x40, 0x0e,
    2, 0x12, 0x81, 0x0f,
    8, 0x16, 0x00, 0xea, 0x01, 0x06, 0xa6, 0xff, 0xda, 0x05,
    4, 0x22, 0x20, 0xee, 0x5a, 0x00,
    6, 0x46, 0x1d, 0x06, 0xa6, 0xff, 0xba, 0x05,
    2, 0x50, 0x24, 0xf6,
    8, 0x54, 0x60, 0x08, 0x41, 0x0a, 0x80, 0x0b, 0xd5, 0xd5,
    0,
};
static const uint8_t foreground_call_offsets[10] = {
    0x1e, 0x26, 0x2a, 0x2e, 0x32, 0x36, 0x3a, 0x3e, 0x42, 0x4c,
};
static const uint8_t rx_producer_pattern[] = {
    7, 0, 0x80, 0x07, 0xe1, 0xf1, 0x86, 0x00, 0x07,
    5, 8, 0x07, 0xf0, 0x00, 0xc5, 0x67,
    17, 14, 0x08, 0x0a, 0x18, 0x98, 0x9f, 0x9a, 0xb9, 0x05, 0x20,
    0x0e, 0x40, 0x00, 0xe6, 0xee, 0x06, 0x00, 0xe1,
    1, 32, 0xe1,
    9, 34, 0x36, 0xbb, 0x06, 0xc8, 0xc1, 0x32, 0xc5, 0x31, 0xe6,
    0,
};
static const uint8_t freshness_signature[12] = {
    0x06, 0xf0, 0x6b, 0x08, 0x88, 0x9f, 0x01, 0x00, 0xf3, 0x09, 0xeb, 0x35,
};
static const uint8_t command5_signature[16] = {
    0x86, 0x07, 0x61, 0x00, 0x09, 0x90, 0xc6, 0x00,
    0x07, 0x08, 0x08, 0xe8, 0x92, 0x00, 0x44, 0x07,
};
static const uint8_t lower_can_signature[12] = {
    0x86, 0x07, 0xe1, 0xf0, 0x06, 0xc8, 0xd9, 0x00, 0x07, 0xe0, 0x25, 0x0f,
};
static const uint8_t shadow_copy_signature[36] = {
    0x3e, 0x06, 0x00, 0x7c, 0xbf, 0xfe, 0x21, 0x06,
    0x00, 0x00, 0x01, 0x00, 0xe5, 0x05, 0x21, 0x9f,
    0x01, 0x00, 0x44, 0x0a, 0x01, 0x9d, 0x44, 0xf2,
    0x33, 0x06, 0xf0, 0x7d, 0x01, 0x00, 0xf3, 0x09,
    0xf1, 0xf5, 0x7f, 0x00,
};

static uint16_t read16(const uint8_t *p)
{
    return (uint16_t)p[0] | (uint16_t)((uint16_t)p[1] << 8);
}

static uint32_t read32(const uint8_t *p)
{
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8) |
           ((uint32_t)p[2] << 16) | ((uint32_t)p[3] << 24);
}

static int bytes_equal(const uint8_t *left, const uint8_t *right, unsigned size)
{
    while (size-- != 0u) {
        if (*left++ != *right++) {
            return 0;
        }
    }
    return 1;
}

static int is_jarl22(const uint8_t *image, uint32_t address)
{
    uint16_t first;
    if (address > CODEFLASH_SIZE - 4u) {
        return 0;
    }
    first = read16(image + address);
    return (first & 0xffc0u) == 0xff80u && (image[address + 2u] & 1u) == 0u;
}

static uint32_t jarl22_target(const uint8_t *image, uint32_t address)
{
    uint32_t instruction = read32(image + address);
    int32_t high = (int32_t)(instruction & 0x3fu);
    if ((high & 0x20) != 0) {
        high -= 0x40;
    }
    return address + (uint32_t)(high * 0x10000) + (instruction >> 16);
}

/* UINT32_MAX is unseen; CODEFLASH_SIZE is ambiguous and stays ambiguous.
 * Only a unique hit leaves an address inside CodeFlash. */
static void record_hit(uint32_t *address, uint32_t value)
{
    *address = *address == UINT32_MAX ? value : CODEFLASH_SIZE;
}

static int pattern_matches(const uint8_t *candidate, const uint8_t *pattern)
{
    unsigned size;
    while ((size = *pattern++) != 0u) {
        const uint8_t *actual = candidate + *pattern++;
        do {
            if (*actual++ != *pattern++) {
                return 0;
            }
        } while (--size != 0u);
    }
    return 1;
}

static int32_t resolve_foreground(
    const uint8_t *image, uint32_t address)
{
    int16_t foreground_flag_displacement;
    unsigned index;
    if (!pattern_matches(image + address, foreground_pattern)) {
        return 0;
    }
    foreground_flag_displacement =
        *(const int16_t *)(const void *)(image + address + 6u);
    if (foreground_flag_displacement !=
        *(const int16_t *)(const void *)(image + address + 12u)) {
        return 0;
    }
    for (index = 0; index < ARRAY_SIZE(foreground_call_offsets); ++index) {
        if (!is_jarl22(image, address + foreground_call_offsets[index])) {
            return 0;
        }
    }
    return foreground_flag_displacement;
}

static int recover_auth_trip(
    const uint8_t *image, uint32_t freshness, uint32_t gp, uint32_t *auth_trip)
{
    uint32_t offset;
    uint32_t start = freshness > 0x80u ? freshness - 0x80u : 0u;
    uint32_t candidate = 0;
    unsigned count = 0;

    for (offset = start; offset + 8u <= freshness; offset += 2u) {
        if (read32(image + offset) == 0x00210780u &&
            read16(image + offset + 4u) == 0x3624u) {
            candidate = gp + (uint32_t)(int16_t)read16(image + offset + 6u);
            ++count;
        }
    }
    if (count != 1u || candidate < 0xfebe0000u ||
        candidate + 4u >= 0xfec00000u) {
        return 0;
    }
    *auth_trip = candidate;
    return 1;
}

static int recover_context(
    const uint8_t *image, uint32_t context, uint32_t *gp, uint32_t *tp)
{
    uint32_t offset;
    uint32_t end;
    uint8_t found = 0;
    if (context >= CODEFLASH_SIZE) {
        return 0;
    }
    end = context + 0x80u;
    if (end > CODEFLASH_SIZE - 6u) {
        end = CODEFLASH_SIZE - 6u;
    }
    for (offset = context; offset < end; offset += 2u) {
        uint16_t opcode = read16(image + offset);
        if (opcode == 0x007fu) {
            break;
        }
        if (opcode == 0x0624u) {
            if ((found & 1u) != 0u) {
                return 0;
            }
            *gp = read32(image + offset + 2u);
            found |= 1u;
        } else if (opcode == 0x0625u) {
            if ((found & 2u) != 0u) {
                return 0;
            }
            *tp = read32(image + offset + 2u);
            found |= 2u;
        }
    }
    return found == 3u;
}

int resolve_request_signer_image(const uint8_t *image, uint32_t *output)
{
    uint32_t boot = UINT32_MAX, coordinator = UINT32_MAX, producer = UINT32_MAX;
    uint32_t freshness = UINT32_MAX, command5 = UINT32_MAX, lower_can = UINT32_MAX;
    uint32_t diagnostic_tx = UINT32_MAX, class_route = UINT32_MAX;
    uint32_t coordinator_after = 0;
    unsigned mpu_count = 0;
    unsigned transit_pointer_count = 0;
    uint32_t offset;
    uint32_t q;
    unsigned index;

    for (offset = 0; offset + 256u < CODEFLASH_SIZE; offset += 2u) {
        const uint8_t *p = image + offset;
        uint32_t word = read32(p);
        uint16_t first = (uint16_t)word;

        if (word == 0x00610782u) {
            unsigned calls = 0;
            q = offset + 4u;
            while (calls < BOOT_CALL_COUNT && is_jarl22(image, q)) {
                ++calls;
                q += 4u;
            }
            if (calls == BOOT_CALL_COUNT && read16(image + q) == 0x51e0u) {
                record_hit(&boot, offset);
            }
        }
        if (first == 0x0780u) {
            if (word == 0x00210780u) {
                unsigned calls = 0;
                q = offset + 4u;
                while (calls < 66u && is_jarl22(image, q)) {
                    ++calls;
                    q += 4u;
                }
                if (calls >= 9u && calls <= 65u && read16(image + q) == 0x3200u &&
                    is_jarl22(image, q + 2u) &&
                    read32(image + q + 6u) == 0x016087e0u &&
                    is_jarl22(image, q + 10u) &&
                    read32(image + q + 14u) == 0x003f0640u) {
                    record_hit(&coordinator, offset);
                    coordinator_after = q;
                }
            }
            if (word == 0xf1e10780u && pattern_matches(p, rx_producer_pattern)) {
                record_hit(&producer, offset);
            }
        }
        if (first == 0xf006u &&
            bytes_equal(p, freshness_signature, sizeof(freshness_signature))) {
            record_hit(&freshness, offset);
        }
        if (first == 0x0786u) {
            if (bytes_equal(p, command5_signature, sizeof(command5_signature))) {
                record_hit(&command5, offset);
            }
            if (bytes_equal(p, lower_can_signature, sizeof(lower_can_signature))) {
                record_hit(&lower_can, offset);
            }
        }
        if ((word & 0xff00ffffu) == 0xff00ff00u &&
            p[2] != 0xffu && p[4] == 0xffu) {
            record_hit(&class_route, offset);
        }
        if ((offset & 3u) == 0u) {
            if (word == 0x7a9u && read32(p + 8u) == word) {
                record_hit(&diagnostic_tx, offset);
            }
            if (word == 0u && read32(p + 4) == 0xfebdfffcu &&
                read32(p + 8) == 0xfebf7c00u && read32(p + 12) == 0xfebffbfcu &&
                read32(p + 96) == 0xfec00000u &&
                read32(p + 100) == 0xfffffffcu &&
                read32(p + 176) == 0xb8u && read32(p + 240) == 0xb8u) {
                ++mpu_count;
            }
            if (word >= HELPER_BASE && word < HELPER_END) {
                ++transit_pointer_count;
            }
        }
    }

    if (boot >= CODEFLASH_SIZE || coordinator >= CODEFLASH_SIZE || producer >= CODEFLASH_SIZE) {
        return -1;
    }
    if (freshness >= CODEFLASH_SIZE || command5 >= CODEFLASH_SIZE || lower_can >= CODEFLASH_SIZE) {
        return -2;
    }
    if (mpu_count != 1u || transit_pointer_count != 0u) {
        return -3;
    }
    if (diagnostic_tx >= CODEFLASH_SIZE || class_route >= CODEFLASH_SIZE) {
        return -11;
    }

    for (index = 0; index < BOOT_CALL_COUNT; ++index) {
        uint32_t target = jarl22_target(image, boot + 4u + index * 4u);
        if (target >= CODEFLASH_SIZE) {
            return -5;
        }
        output[index] = target;
    }

    {
        uint32_t app_context = 0;
        uint32_t startup_final;
        uint32_t foreground;
        int32_t foreground_flag_displacement;
        uint32_t gp;
        uint32_t tp;
        uint32_t capacity_table;
        uint32_t ring_words;
        uint32_t ring_bytes;
        uint32_t ring_producer;
        uint32_t ring_base = 0;
        uint32_t ring_hits = 0;
        uint32_t auth_trip;
        uint32_t command5_globals;
        uint32_t *config = output + BOOT_CALL_COUNT;
        unsigned shadow_calls = 0;

        /* Candidate discovery already validated this complete call span. */
        for (q = coordinator + 4u; q < coordinator_after; q += 4u) {
            uint32_t target = jarl22_target(image, q);
            if (target >= CODEFLASH_SIZE) {
                return -6;
            }
            if (q == coordinator + 4u) {
                app_context = target;
            } else if (target <= CODEFLASH_SIZE - sizeof(shadow_copy_signature) &&
                       bytes_equal(image + target, shadow_copy_signature,
                                   sizeof(shadow_copy_signature))) {
                ++shadow_calls;
            }
        }
        config[CONFIG_WORD_STARTUP_AFTER] = q;
        startup_final = jarl22_target(image, q + 2u);
        foreground = jarl22_target(image, q + 10u);
        if (shadow_calls != 1u ||
            startup_final >= CODEFLASH_SIZE ||
            foreground > CODEFLASH_SIZE - FOREGROUND_SIZE ||
            (foreground_flag_displacement =
                 resolve_foreground(image, foreground)) == 0) {
            return -6;
        }
        if (!recover_context(image, app_context, &gp, &tp)) {
            return -7;
        }

        config[CONFIG_WORD_APP_CONTEXT] = app_context;
        config[CONFIG_WORD_STARTUP_FIRST] = coordinator + 8u;
        config[CONFIG_WORD_STARTUP_FINAL] = startup_final;
        config[CONFIG_WORD_TIMING_FLAG] =
            ((uint32_t)read16(image + foreground + 0x10u) << 16) +
            (uint32_t)((int16_t)read16(image + foreground + 0x14u) & -2);
        config[CONFIG_WORD_TICK_COUNTER] =
            gp + (uint32_t)(int16_t)read16(image + foreground + 0x52u);
        capacity_table = tp + (uint32_t)((int16_t)read16(image + producer + 44u) & -2);
        ring_producer = gp + (uint32_t)((int16_t)read16(image + producer + 54u) & -2);
        if (capacity_table < 0x100u || capacity_table + 2u > CODEFLASH_SIZE ||
            ring_producer < 0xfebe0000u || ring_producer >= 0xfec00000u) {
            return -8;
        }
        ring_words = read16(image + capacity_table);
        ring_bytes = ring_words * 4u;
        for (offset = capacity_table - 0x100u; offset < capacity_table; offset += 2u) {
            uint32_t value = read32(image + offset);
            uint32_t gap = ring_producer - value;
            if (value >= 0xfebe0000u && value < 0xfec00000u &&
                gap - ring_bytes <= 0x40u) {
                ring_base = value;
                ++ring_hits;
            }
        }
        if (ring_hits != 1u) {
            return -8;
        }
        config[CONFIG_WORD_RING_BASE] = ring_base;
        config[CONFIG_WORD_RING_PRODUCER] = ring_producer;
        config[CONFIG_WORD_RUNTIME_GEOMETRY] =
            ring_words | ((uint32_t)(uint16_t)foreground_flag_displacement << 16);

        if (!recover_auth_trip(image, freshness, gp, &auth_trip)) {
            return -9;
        }
        command5_globals = gp + (uint32_t)(int16_t)read16(image + command5 + 16u) - 0x1cu;
        if (command5_globals < 0xfebe0000u || command5_globals >= 0xfec00000u) {
            return -9;
        }
        config[CONFIG_WORD_AUTH_RESET] = auth_trip + 4u;
        config[CONFIG_WORD_AUTH_TRIP] = auth_trip;
        config[CONFIG_WORD_FRESHNESS_ENCODE] = freshness;
        config[CONFIG_WORD_COMMAND5_SYNC] = command5;
        config[CONFIG_WORD_LOWER_CAN_WRITE] = lower_can;
        config[CONFIG_WORD_COMMAND5_GLOBALS] = command5_globals;

        config[CONFIG_WORD_STATE_BASE] = RESIDENT_BASE;
        config[CONFIG_WORD_SCRATCH_BASE] = HELPER_BASE + HELPER_CODE_LIMIT;

        q = (uint32_t)image[class_route + 2u] + image[diagnostic_tx + 6u];

        ring_hits = 0;
        for (offset = class_route; offset + 10u < diagnostic_tx; offset += 2u) {
            const uint8_t *row = image + offset;
            uint32_t mapping = read32(row + 4u);
            if (read32(row) == 0x00020007u && read16(row + 8u) == q) {
                config[CONFIG_WORD_RESPONSE_HANDLE] = mapping >> 16;
                ++ring_hits;
            }
        }
        if (ring_hits != 1u) {
            return -11;
        }
        for (index = 0; index < ARRAY_SIZE(foreground_call_offsets); ++index) {
            uint32_t target = jarl22_target(image, foreground + foreground_call_offsets[index]);
            if (target >= CODEFLASH_SIZE) {
                return -12;
            }
            config[CONFIG_WORD_FG_TIMING_BEGIN + index] = target;
        }
    }
    return 0;
}
