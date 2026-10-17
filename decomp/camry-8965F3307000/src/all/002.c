#include "common.h"


void FUN_0000814e(int param_1)

{
  (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 0xc0)))) = 0;
  FUN_000076b6(((undefined4 *)camry_host_ptr((uint32_t)(param_1))), 0xd4);
  return;
}



/* Boot-phase source of the dispatcher copied by35E4 to FEBF1000. Scan eight-byte {u32 key,u32
   handler} records atFEBF0F00 until key equals full32-bit r6 orFFFFFFFF; call the selected handler.
   No local table bound. r6-r9 are unchanged before the call; DISPOSE does not change callback
   result registers. No complete callback ABI is imposed. Native execution covers matching/fallback
   selection and real35E4 relocation followed by RAM instruction execution, stopping before the
   callback. Synthetic input table; no flash operation. Scan eight-byte key/handler records
   atFEBF0F00 until full32-bit r6 matches or keyFFFFFFFF; no local bound. Forward r6-r9 unchanged to
   selected handler. Five native cases include actual35E4 copy then RAM execution atFEBF1000, with
   relocated return link. Stop before callback; table is synthetic and callback ABI/OEM entries
   remain unclosed. Correct42-byte body replaces a four-byte PREPARE-only body blocked by false data
   at8374. */

void f33_boot_ram_dispatch(int param_1)

{
  int iVar1;
  
  iVar1 = 0;
  while( true ) {
    if (((*((int *)camry_host_ptr((uint32_t)(f33_nvm_family0_read_record + iVar1 * 8 + 0x278)))) == -1) ||
       ((*((int *)camry_host_ptr((uint32_t)(f33_nvm_family0_read_record + iVar1 * 8 + 0x278)))) == param_1)) break;
    iVar1 = iVar1 + 1;
  }
  (*(int (*)())*(code **)(f33_nvm_family0_read_record + iVar1 * 8 + 0x27c))();
  return;
}


