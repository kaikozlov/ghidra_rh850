#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

/* Host stand-in for the 32-bit address space. Later regions overlay earlier
 * ones, so an oracle image can cover RAM while CodeFlash stays at VA 0.
 */

#define CAMRY_HOST_REGIONS 8

typedef struct {
    uint32_t base;
    uint32_t size;
    uint8_t *data;
} CamryHostRegion;

static CamryHostRegion camry_host_regions[CAMRY_HOST_REGIONS];
static int camry_host_region_count;

void camry_host_reset(void) {
    camry_host_region_count = 0;
}

void camry_host_add(uint32_t base, uint8_t *data, uint32_t size) {
    if (camry_host_region_count >= CAMRY_HOST_REGIONS)
        abort();
    camry_host_regions[camry_host_region_count].base = base;
    camry_host_regions[camry_host_region_count].size = size;
    camry_host_regions[camry_host_region_count].data = data;
    camry_host_region_count += 1;
}

static uint8_t *camry_host_locate(uint32_t address, uint32_t width) {
    int index;
    for (index = camry_host_region_count - 1; index >= 0; index -= 1) {
        CamryHostRegion *region = &camry_host_regions[index];
        uint32_t offset;
        if (address < region->base)
            continue;
        offset = address - region->base;
        if (offset < region->size && width <= region->size - offset)
            return region->data + offset;
    }
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

uint32_t camry_host_addr(const void *pointer) {
    const uint8_t *bytes = pointer;
    int index;
    for (index = camry_host_region_count - 1; index >= 0; index -= 1) {
        CamryHostRegion *region = &camry_host_regions[index];
        const uint8_t *end = region->data + region->size;
        if (bytes >= region->data && bytes < end)
            return region->base + (uint32_t)(bytes - region->data);
    }
    fprintf(stderr, "unmapped camry host pointer\n");
    abort();
}

void camry_write32(uint32_t address, uint32_t value) {
    uint8_t *bytes = camry_host_locate(address, 4);
    bytes[0] = (uint8_t)value;
    bytes[1] = (uint8_t)(value >> 8);
    bytes[2] = (uint8_t)(value >> 16);
    bytes[3] = (uint8_t)(value >> 24);
}
