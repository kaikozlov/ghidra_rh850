#include "common.h"


undefined4 FUN_00008010(byte *param_1,uchar *param_2,char param_3,F33BootAes128Context *param_4)

{
  uint uVar1;
  byte local_1c;
  byte bStack_1b;
  byte bStack_1a;
  byte bStack_19;
  byte bStack_18;
  byte bStack_17;
  byte bStack_16;
  byte bStack_15;
  byte bStack_14;
  byte bStack_13;
  byte bStack_12;
  byte bStack_11;
  byte bStack_10;
  byte bStack_f;
  byte bStack_e;
  byte bStack_d;
  
  if ((param_3 == '\x10') && (param_4->valid == '\x01')) {
    local_1c = *param_1 ^ param_4[1].round_keys[0];
    bStack_1b = param_1[1] ^ param_4[1].round_keys[1];
    bStack_1a = param_1[2] ^ param_4[1].round_keys[2];
    bStack_19 = param_1[3] ^ param_4[1].round_keys[3];
    bStack_18 = param_1[4] ^ param_4[1].round_keys[4];
    bStack_17 = param_1[5] ^ param_4[1].round_keys[5];
    bStack_16 = param_1[6] ^ param_4[1].round_keys[6];
    bStack_15 = param_1[7] ^ param_4[1].round_keys[7];
    bStack_14 = param_1[8] ^ param_4[1].round_keys[8];
    bStack_13 = param_1[9] ^ param_4[1].round_keys[9];
    bStack_12 = param_1[10] ^ param_4[1].round_keys[10];
    bStack_11 = param_1[0xb] ^ param_4[1].round_keys[0xb];
    bStack_10 = param_1[0xc] ^ param_4[1].round_keys[0xc];
    bStack_f = param_1[0xd] ^ param_4[1].round_keys[0xd];
    bStack_e = param_1[0xe] ^ param_4[1].round_keys[0xe];
    bStack_d = param_1[0xf] ^ param_4[1].round_keys[0xf];
    uVar1 = f33_boot_aes128_encrypt_block(&local_1c,param_2,'\x10',param_4);
    if (uVar1 == 0) {
      *(undefined4 *)param_4[1].round_keys = *(undefined4 *)param_2;
      *(undefined4 *)(param_4[1].round_keys + 4) = *(undefined4 *)(param_2 + 4);
      *(undefined4 *)(param_4[1].round_keys + 8) = *(undefined4 *)(param_2 + 8);
      *(undefined4 *)(param_4[1].round_keys + 0xc) = *(undefined4 *)(param_2 + 0xc);
      return 0;
    }
  }
  return 0xff;
}



undefined4 FUN_0000811a(uchar *param_1,char param_2,F33BootAes128Context *param_3)

{
  uint uVar1;
  
  if (param_2 == '\x10') {
    param_3->valid = '\0';
    param_3[1].round_keys[0] = '\0';
    param_3[1].round_keys[1] = '\0';
    param_3[1].round_keys[2] = '\0';
    param_3[1].round_keys[3] = '\0';
    param_3[1].round_keys[4] = '\0';
    param_3[1].round_keys[5] = '\0';
    param_3[1].round_keys[6] = '\0';
    param_3[1].round_keys[7] = '\0';
    param_3[1].round_keys[8] = '\0';
    param_3[1].round_keys[9] = '\0';
    param_3[1].round_keys[10] = '\0';
    param_3[1].round_keys[0xb] = '\0';
    param_3[1].round_keys[0xc] = '\0';
    param_3[1].round_keys[0xd] = '\0';
    param_3[1].round_keys[0xe] = '\0';
    param_3[1].round_keys[0xf] = '\0';
    uVar1 = f33_boot_aes128_initialize_context(param_1,'\x10',param_3);
    if (uVar1 == 0) {
      param_3->valid = '\x01';
      return 0;
    }
  }
  return 0xff;
}



void FUN_0000814e(int param_1)

{
  (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 0xc0)))) = 0;
  FUN_000076b6(((undefined4 *)camry_host_ptr((uint32_t)(param_1))), 0xd4);
  return;
}



/* Require low8 key/IV lengths16; clear AES.valid, copyIV to+C4, initialize AES base under key,
   setvalid1 on success. Return0/FF. Fifth argument callerSP+0/calleeSP+8. Does not initialize
   unused final16 bytes of228-byte clear allocation. */

uint f33_boot_aes128_cbc_initialize
               (uchar *key,uchar key_length,uchar *iv,uchar iv_length,
               F33BootAes128CbcContext *context)

{
  uint uVar1;
  
  if ((key_length == '\x10') && (iv_length == '\x10')) {
    (context->aes).valid = '\0';
    context->previous_ciphertext[0] = *iv;
    context->previous_ciphertext[1] = iv[1];
    context->previous_ciphertext[2] = iv[2];
    context->previous_ciphertext[3] = iv[3];
    context->previous_ciphertext[4] = iv[4];
    context->previous_ciphertext[5] = iv[5];
    context->previous_ciphertext[6] = iv[6];
    context->previous_ciphertext[7] = iv[7];
    context->previous_ciphertext[8] = iv[8];
    context->previous_ciphertext[9] = iv[9];
    context->previous_ciphertext[10] = iv[10];
    context->previous_ciphertext[0xb] = iv[0xb];
    context->previous_ciphertext[0xc] = iv[0xc];
    context->previous_ciphertext[0xd] = iv[0xd];
    context->previous_ciphertext[0xe] = iv[0xe];
    context->previous_ciphertext[0xf] = iv[0xf];
    uVar1 = f33_boot_aes128_initialize_context(key,'\x10',&context->aes);
    if (uVar1 == 0) {
      (context->aes).valid = '\x01';
      return 0;
    }
  }
  return 0xff;
}



/* Clear AES.valid then entire228-byte CBC allocation through76B6. Does not clear configured IV/key
   material. */

void f33_boot_aes128_cbc_clear(F33BootAes128CbcContext *context)

{
  (context->aes).valid = '\0';
  FUN_000076b6(context,0xe4);
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


