#ifndef SECOC_PATCH_FLASH_BACKEND_H
#define SECOC_PATCH_FLASH_BACKEND_H

#include "../common/patch_config.h"

int flash_block_rmw(unsigned int block_base);
volatile unsigned char *flash_work_buffer(void);

#endif
