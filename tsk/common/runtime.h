#ifndef SECOC_EXPLOIT_RUNTIME_H
#define SECOC_EXPLOIT_RUNTIME_H

#include "patch_config.h"

void runtime_init(void);
void telemetry_stage(unsigned int stage);
void telemetry_value(unsigned int tag, unsigned int field, unsigned int value);
void telemetry_error(unsigned int code, unsigned int detail);
void runtime_halt(void) __attribute__((noreturn));
void feed_watchdog(void);
unsigned int crc32_flash_range(unsigned int start, unsigned int end);
unsigned int crc32_bytes(const volatile unsigned char *data, unsigned int length);
unsigned int validate_patch_config_runtime(const struct patch_config_v1 *cfg);
unsigned int read_le_word(unsigned int address);
int verify_patch_preimage(const struct patch_config_v1 *cfg, unsigned int *observed_word);

#endif
