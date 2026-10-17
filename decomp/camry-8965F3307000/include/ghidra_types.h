#pragma once

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/* Ghidra decompiler types for corpus C. Absolute addresses go through the
 * host map under CAMRY_HOST and through integer casts on the target.
 */

typedef uint8_t byte;
typedef uint8_t uchar;
typedef uint8_t code;
typedef uint8_t undefined;
typedef uint8_t undefined1;
typedef uint16_t undefined2;
typedef uint32_t undefined4;
typedef uint64_t undefined8;
typedef uint64_t uint5;
typedef uint16_t ushort;
typedef uint32_t uint;
typedef uint32_t ulong;
typedef uint64_t ulonglong;
typedef int64_t longlong;

#ifdef CAMRY_HOST
uint8_t *camry_host_ptr(uint32_t address);
uint32_t camry_host_addr(const void *pointer);
#else
static inline uint8_t *camry_host_ptr(uint32_t address) {
    return (uint8_t *)(uintptr_t)address;
}
static inline uint32_t camry_host_addr(const void *pointer) {
    return (uint32_t)(uintptr_t)pointer;
}
#endif

#define __synchronize() ((void)0)
