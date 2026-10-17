#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

/* Host stand-in for the 32-bit address space. Later regions overlay earlier
 * ones, so an oracle image can cover RAM while CodeFlash stays at VA 0.
 */

#define CAMRY_HOST_REGIONS 8

/* A C local is not in a firmware region. camry_host_addr assigns it a
 * firmware address, and camry_host_ptr of that address returns the local.
 */
#define CAMRY_ALIAS_SLOTS 64
#define CAMRY_ALIAS_STRIDE 0x200u
#define CAMRY_ALIAS_BASE 0xFEBD0000u

typedef struct {
    uint32_t base;
    uint32_t size;
    uint8_t *data;
} CamryHostRegion;

typedef struct {
    uintptr_t host;
    uint32_t firmware;
} CamryAlias;

static CamryHostRegion camry_host_regions[CAMRY_HOST_REGIONS];
static int camry_host_region_count;
static CamryAlias camry_aliases[CAMRY_ALIAS_SLOTS];
static int camry_alias_count;

void camry_host_reset(void) {
    camry_host_region_count = 0;
    camry_alias_count = 0;
}

void camry_host_add(uint32_t base, uint8_t *data, uint32_t size) {
    if (camry_host_region_count >= CAMRY_HOST_REGIONS)
        abort();
    camry_host_regions[camry_host_region_count].base = base;
    camry_host_regions[camry_host_region_count].size = size;
    camry_host_regions[camry_host_region_count].data = data;
    camry_host_region_count += 1;
}

static uint8_t *camry_alias_locate(uint32_t address, uint32_t width) {
    int index;
    for (index = camry_alias_count - 1; index >= 0; index -= 1) {
        CamryAlias *alias = &camry_aliases[index];
        uint32_t offset;
        if (address < alias->firmware)
            continue;
        offset = address - alias->firmware;
        if (offset < CAMRY_ALIAS_STRIDE && width <= CAMRY_ALIAS_STRIDE - offset)
            return (uint8_t *)alias->host + offset;
    }
    return NULL;
}

static uint8_t *camry_host_locate(uint32_t address, uint32_t width) {
    int index;
    uint8_t *aliased;
    for (index = camry_host_region_count - 1; index >= 0; index -= 1) {
        CamryHostRegion *region = &camry_host_regions[index];
        uint32_t offset;
        if (address < region->base)
            continue;
        offset = address - region->base;
        if (offset < region->size && width <= region->size - offset)
            return region->data + offset;
    }
    aliased = camry_alias_locate(address, width);
    if (aliased != NULL)
        return aliased;
    fprintf(stderr, "unmapped camry access at %#x\n", address);
    abort();
}

uint32_t camry_read8(uint32_t address) {
    return *camry_host_locate(address, 1);
}

uint32_t camry_read16(uint32_t address) {
    const uint8_t *bytes = camry_host_locate(address, 2);
    return (uint32_t)bytes[0] | ((uint32_t)bytes[1] << 8);
}

uint32_t camry_read32(uint32_t address) {
    const uint8_t *bytes = camry_host_locate(address, 4);
    return (uint32_t)bytes[0]
        | ((uint32_t)bytes[1] << 8)
        | ((uint32_t)bytes[2] << 16)
        | ((uint32_t)bytes[3] << 24);
}

void camry_write8(uint32_t address, uint32_t value) {
    *camry_host_locate(address, 1) = (uint8_t)value;
}

void camry_write16(uint32_t address, uint32_t value) {
    uint8_t *bytes = camry_host_locate(address, 2);
    bytes[0] = (uint8_t)value;
    bytes[1] = (uint8_t)(value >> 8);
}

uint8_t *camry_host_ptr(uint32_t address) {
    return camry_host_locate(address, 1);
}

int camry_host_firmware(const void *pointer, uint32_t *out) {
    const uint8_t *bytes = pointer;
    uintptr_t raw = (uintptr_t)pointer;
    int index;
    for (index = camry_host_region_count - 1; index >= 0; index -= 1) {
        CamryHostRegion *region = &camry_host_regions[index];
        const uint8_t *end = region->data + region->size;
        if (bytes >= region->data && bytes < end) {
            *out = region->base + (uint32_t)(bytes - region->data);
            return 1;
        }
    }
    for (index = camry_alias_count - 1; index >= 0; index -= 1) {
        CamryAlias *alias = &camry_aliases[index];
        if (raw >= alias->host && raw < alias->host + CAMRY_ALIAS_STRIDE) {
            *out = alias->firmware + (uint32_t)(raw - alias->host);
            return 1;
        }
    }
    return 0;
}

uint32_t camry_host_addr(const void *pointer) {
    const uint8_t *bytes = pointer;
    uintptr_t raw = (uintptr_t)pointer;
    int index;
    for (index = camry_host_region_count - 1; index >= 0; index -= 1) {
        CamryHostRegion *region = &camry_host_regions[index];
        const uint8_t *end = region->data + region->size;
        if (bytes >= region->data && bytes < end)
            return region->base + (uint32_t)(bytes - region->data);
    }
    for (index = camry_alias_count - 1; index >= 0; index -= 1) {
        CamryAlias *alias = &camry_aliases[index];
        if (raw >= alias->host && raw < alias->host + CAMRY_ALIAS_STRIDE)
            return alias->firmware + (uint32_t)(raw - alias->host);
    }
    if (camry_alias_count >= CAMRY_ALIAS_SLOTS) {
        fprintf(stderr, "unmapped camry host pointer\n");
        abort();
    }
    camry_aliases[camry_alias_count].host = raw;
    camry_aliases[camry_alias_count].firmware =
        CAMRY_ALIAS_BASE + (uint32_t)camry_alias_count * CAMRY_ALIAS_STRIDE;
    camry_alias_count += 1;
    return camry_aliases[camry_alias_count - 1].firmware;
}

void camry_write32(uint32_t address, uint32_t value) {
    uint8_t *bytes = camry_host_locate(address, 4);
    bytes[0] = (uint8_t)value;
    bytes[1] = (uint8_t)(value >> 8);
    bytes[2] = (uint8_t)(value >> 16);
    bytes[3] = (uint8_t)(value >> 24);
}
