/*
 * Single translation unit for the generic RH850 patch shellcode.
 *
 * The pinned community build extracts only this object's .text section. Keeping
 * exploit() first plus -fno-toplevel-reorder preserves the bootloader entry at
 * shellcode offset zero without introducing a new linker/runtime model.
 */
#include "main.c"
#include "../common/runtime.c"
#include "preflight.c"
#include "flash_backend.c"
#include "apply.c"
