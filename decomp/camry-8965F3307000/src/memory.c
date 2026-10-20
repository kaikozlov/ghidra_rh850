#include "camry.h"

#include <stdint.h>

/* Leaf memory routines from CodeFlash. Block structure follows the original
 * control flow. These are equivalent C: GCC does not byte-match this image.
 */

#ifdef CAMRY_HOST
static void *camry_bytes(void *pointer) {
    return camry_host_resolve(pointer);
}
#else
static void *camry_bytes(void *pointer) {
    return pointer;
}
#endif

void *memcpy_forward(void *destination, void *source, uint32_t byte_count) {
    uint8_t *dest = camry_bytes(destination);
    const uint8_t *src = camry_bytes(source);
    if ((((uintptr_t)dest | (uintptr_t)src) & 3u) == 0u) {
        while (byte_count > 31u) {
            uint32_t *out = (uint32_t *)dest;
            const uint32_t *in = (const uint32_t *)src;
            out[0] = in[0];
            out[1] = in[1];
            out[2] = in[2];
            out[3] = in[3];
            out[4] = in[4];
            out[5] = in[5];
            out[6] = in[6];
            out[7] = in[7];
            dest += 32;
            src += 32;
            byte_count -= 32u;
        }
        if (byte_count > 15u) {
            uint32_t *out = (uint32_t *)dest;
            const uint32_t *in = (const uint32_t *)src;
            out[0] = in[0];
            out[1] = in[1];
            out[2] = in[2];
            out[3] = in[3];
            dest += 16;
            src += 16;
            byte_count -= 16u;
        }
        while (byte_count > 3u) {
            *(uint32_t *)dest = *(const uint32_t *)src;
            dest += 4;
            src += 4;
            byte_count -= 4u;
        }
    }
    while (byte_count != 0u) {
        *dest++ = *src++;
        byte_count -= 1u;
    }
    return destination;
}

static void zero_words(uint8_t *dest, uint32_t size) {
    uint32_t offset = 0;
    while (offset < size) {
        *(uint32_t *)(dest + offset) = 0;
        offset += 4u;
    }
}

void memzero(void *destination, uint32_t byte_count) {
    uint8_t *dest = camry_bytes(destination);
    if (((uintptr_t)dest & 3u) != 0u && byte_count > 3u) {
        uint32_t head = 4u - ((uintptr_t)dest & 3u);
        byte_count -= head;
        while (head != 0u) {
            *dest++ = 0;
            head -= 1u;
        }
    }
    while (byte_count > 0x7fu) {
        zero_words(dest, 0x80u);
        dest += 0x80;
        byte_count -= 0x80u;
    }
    if (byte_count > 0x3fu) {
        zero_words(dest, 0x40u);
        dest += 0x40;
        byte_count -= 0x40u;
    }
    if (byte_count > 0x1fu) {
        zero_words(dest, 0x20u);
        dest += 0x20;
        byte_count -= 0x20u;
    }
    if (byte_count > 0xfu) {
        zero_words(dest, 0x10u);
        dest += 0x10;
        byte_count -= 0x10u;
    }
    while (byte_count > 3u) {
        *(uint32_t *)dest = 0;
        dest += 4;
        byte_count -= 4u;
    }
    while (byte_count != 0u) {
        *dest++ = 0;
        byte_count -= 1u;
    }
}

void copy_whole_words(uint32_t *destination, uint32_t *source, uint16_t byte_count) {
    uint32_t index;
    destination = camry_bytes(destination);
    source = camry_bytes(source);
    for (index = 0; index < (uint32_t)(byte_count >> 2); index = (index + 1u) & 0xffffu)
        destination[index] = source[index];
}

uint32_t update_whole_words(uint32_t *destination, uint32_t *source, uint16_t byte_count) {
    uint32_t index;
    uint32_t differed = 0;
    destination = camry_bytes(destination);
    source = camry_bytes(source);
    for (index = 0; index < (uint32_t)(byte_count >> 2); index = (index + 1u) & 0xffffu) {
        if (destination[index] != source[index]) {
            destination[index] = source[index];
            differed = 1;
        }
    }
    return differed;
}

void clear_application_ram_4k(void) {
    uint32_t address = 0xfebe7000u;
    while (address < 0xfebe8000u) {
        camry_write32(address, 0);
        address += 4u;
    }
}
