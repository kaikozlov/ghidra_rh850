/* Exercise resolver parsing and candidate state with synthetic inputs. */
#include <assert.h>
#include <stdlib.h>
#include "../../../tsk/ram_runtime/request_signer/tss3_request_signer_resolver.c"

static void check_candidates(void)
{
    const uint32_t values[] = {0u, 2u, CODEFLASH_SIZE - 2u};
    unsigned index;
    for (index = 0; index < ARRAY_SIZE(values); ++index) {
        uint32_t candidate = UINT32_MAX;
        assert(candidate >= CODEFLASH_SIZE);
        record_hit(&candidate, values[index]);
        assert(candidate == values[index]);
        record_hit(&candidate, values[index]);
        assert(candidate == CODEFLASH_SIZE);
        record_hit(&candidate, values[(index + 1u) % ARRAY_SIZE(values)]);
        assert(candidate == CODEFLASH_SIZE);
    }
}

static void check_pattern(
    const uint8_t *pattern, unsigned length, const uint8_t *variable)
{
    uint8_t candidate[FOREGROUND_SIZE] = {0};
    uint8_t covered[FOREGROUND_SIZE] = {0};
    const uint8_t *run = pattern;
    unsigned size;
    unsigned index;
    assert(length <= sizeof(candidate));
    while ((size = *run++) != 0u) {
        unsigned offset = *run++;
        assert(offset + size <= length);
        while (size-- != 0u) {
            assert(!covered[offset] && !variable[offset]);
            covered[offset] = 1;
            candidate[offset++] = *run++;
        }
    }
    assert(pattern_matches(candidate, pattern));
    for (index = 0; index < length; ++index) {
        unsigned value;
        uint8_t original = candidate[index];
        assert(covered[index] == !variable[index]);
        for (value = 0; value <= UINT8_MAX; ++value) {
            candidate[index] = (uint8_t)value;
            assert(pattern_matches(candidate, pattern) ==
                   (variable[index] || value == original));
        }
        candidate[index] = original;
    }
}

static void check_patterns(void)
{
    const uint8_t rx_variable[44] = {
        [7] = 1, [13] = 1, [31] = 1, [33] = 1, [43] = 1,
    };
    uint8_t foreground_variable[FOREGROUND_SIZE] = {
        [6] = 1, [7] = 1, [12] = 1, [13] = 1,
        [16] = 1, [17] = 1, [20] = 1, [21] = 1, [82] = 1, [83] = 1,
    };
    unsigned index;
    for (index = 0; index < ARRAY_SIZE(foreground_call_offsets); ++index) {
        unsigned byte;
        for (byte = 0; byte < 4u; ++byte) {
            foreground_variable[foreground_call_offsets[index] + byte] = 1;
        }
    }
    check_pattern(rx_producer_pattern, sizeof(rx_variable), rx_variable);
    check_pattern(foreground_pattern, sizeof(foreground_variable), foreground_variable);
}

int main(void)
{
    uint8_t *image = calloc(CODEFLASH_SIZE, 1);
    uint32_t first;
    uint32_t second;
    uint32_t address;
    assert(image != NULL);
    check_candidates();
    check_patterns();

    for (first = 0; first <= UINT16_MAX; ++first) {
        image[0] = (uint8_t)first;
        image[1] = (uint8_t)(first >> 8);
        image[2] = 0x20;
        image[3] = 0;
        assert(read16(image) == first);
        assert(read32(image) == (first | 0x00200000u));
        assert(is_jarl22(image, 0) == (first >= 0xff80u && first < 0xffc0u));
        image[2] |= 1u;
        assert(!is_jarl22(image, 0));
    }

    /* Every valid displacement, including both signs and all high bits. */
    for (first = 0; first < 64u; ++first) {
        image[0] = (uint8_t)(0x80u | first);
        image[1] = 0xff;
        for (second = 0; second <= UINT16_MAX; second += 2u) {
            int32_t displacement = (int32_t)((first << 16) | second);
            if (first >= 32u) {
                displacement -= 0x400000;
            }
            image[2] = (uint8_t)second;
            image[3] = (uint8_t)(second >> 8);
            assert(is_jarl22(image, 0));
            assert(jarl22_target(image, 0) == (uint32_t)displacement);
            image[2] |= 1u;
            assert(!is_jarl22(image, 0));
        }
    }

    /* Byte readers also accept an unaligned buffer. */
    image[1] = 0xfe;
    image[2] = 0xff;
    image[3] = 0x34;
    image[4] = 0x12;
    assert(read16(image + 1) == 0xfffeu);
    assert((int16_t)read16(image + 1) == -2);
    assert(read32(image + 1) == 0x1234fffeu);

    address = CODEFLASH_SIZE - 4u;
    image[address] = 0xbf;
    image[address + 1u] = 0xff;
    image[address + 2u] = 0xfe;
    image[address + 3u] = 0xff;
    assert(is_jarl22(image, address));
    assert(jarl22_target(image, address) == address - 2u);
    for (address = CODEFLASH_SIZE - 3u; address <= CODEFLASH_SIZE; ++address) {
        assert(!is_jarl22(image, address));
    }
    assert(!is_jarl22(image, UINT32_MAX));
    assert(!is_jarl22(image, UINT32_MAX - 3u));

    free(image);
    return 0;
}
