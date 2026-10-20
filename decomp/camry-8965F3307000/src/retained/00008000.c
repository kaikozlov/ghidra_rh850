#include "common.h"

undefined4 boot_aes_cbc_encrypt_block_and_update_chain_8010(byte *param_1,uchar *param_2,char param_3,F33BootAes128Context *param_4)

{
  uint8_t stack_record_1c[28];
  uint uVar1;
  
  if ((param_3 == '\x10') && (param_4->valid == '\x01')) {
    stack_record_1c[0] = *param_1 ^ param_4[1].round_keys[0];
    stack_record_1c[1] = param_1[1] ^ param_4[1].round_keys[1];
    stack_record_1c[2] = param_1[2] ^ param_4[1].round_keys[2];
    stack_record_1c[3] = param_1[3] ^ param_4[1].round_keys[3];
    stack_record_1c[4] = param_1[4] ^ param_4[1].round_keys[4];
    stack_record_1c[5] = param_1[5] ^ param_4[1].round_keys[5];
    stack_record_1c[6] = param_1[6] ^ param_4[1].round_keys[6];
    stack_record_1c[7] = param_1[7] ^ param_4[1].round_keys[7];
    stack_record_1c[8] = param_1[8] ^ param_4[1].round_keys[8];
    stack_record_1c[9] = param_1[9] ^ param_4[1].round_keys[9];
    stack_record_1c[10] = param_1[10] ^ param_4[1].round_keys[10];
    stack_record_1c[11] = param_1[0xb] ^ param_4[1].round_keys[0xb];
    stack_record_1c[12] = param_1[0xc] ^ param_4[1].round_keys[0xc];
    stack_record_1c[13] = param_1[0xd] ^ param_4[1].round_keys[0xd];
    stack_record_1c[14] = param_1[0xe] ^ param_4[1].round_keys[0xe];
    stack_record_1c[15] = param_1[0xf] ^ param_4[1].round_keys[0xf];
    uVar1 = boot_aes128_encrypt_block(((uint8_t *)(stack_record_1c)),param_2,'\x10',param_4);
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

undefined4 boot_initialize_aes_cbc_with_zero_chain_811a(uchar *param_1,char param_2,F33BootAes128Context *param_3)

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
    uVar1 = boot_aes128_initialize_context(param_1,'\x10',param_3);
    if (uVar1 == 0) {
      param_3->valid = '\x01';
      return 0;
    }
  }
  return 0xff;
}

void boot_clear_aes_context_212_bytes_814e(int param_1)

{
  (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 0xc0)))) = 0;
  zero_words_by_byte_count_76b6(((undefined4 *)camry_host_ptr((uint32_t)(param_1))), 0xd4);
  return;
}

uint boot_aes128_cbc_decrypt_block
               (uchar *ciphertext,uchar *plaintext,uchar length,F33BootAes128CbcContext *context)

{
  uint8_t stack_record_20[32];
  uint uVar1;
  
  if (((length == '\x10') && ((context->aes).valid == '\x01')) &&
     (uVar1 = boot_aes128_decrypt_block(ciphertext,((uint8_t *)(stack_record_20)),'\x10',&context->aes), uVar1 == 0))
  {
    *plaintext = context->previous_ciphertext[0] ^ stack_record_20[0];
    plaintext[1] = context->previous_ciphertext[1] ^ stack_record_20[1];
    plaintext[2] = context->previous_ciphertext[2] ^ stack_record_20[2];
    plaintext[3] = context->previous_ciphertext[3] ^ stack_record_20[3];
    plaintext[4] = context->previous_ciphertext[4] ^ stack_record_20[4];
    plaintext[5] = context->previous_ciphertext[5] ^ stack_record_20[5];
    plaintext[6] = context->previous_ciphertext[6] ^ stack_record_20[6];
    plaintext[7] = context->previous_ciphertext[7] ^ stack_record_20[7];
    plaintext[8] = context->previous_ciphertext[8] ^ stack_record_20[8];
    plaintext[9] = context->previous_ciphertext[9] ^ stack_record_20[9];
    plaintext[10] = context->previous_ciphertext[10] ^ stack_record_20[10];
    plaintext[0xb] = context->previous_ciphertext[0xb] ^ stack_record_20[11];
    plaintext[0xc] = context->previous_ciphertext[0xc] ^ stack_record_20[12];
    plaintext[0xd] = context->previous_ciphertext[0xd] ^ stack_record_20[13];
    plaintext[0xe] = context->previous_ciphertext[0xe] ^ stack_record_20[14];
    plaintext[0xf] = context->previous_ciphertext[0xf] ^ stack_record_20[15];
    context->previous_ciphertext[0] = *ciphertext;
    context->previous_ciphertext[1] = ciphertext[1];
    context->previous_ciphertext[2] = ciphertext[2];
    context->previous_ciphertext[3] = ciphertext[3];
    context->previous_ciphertext[4] = ciphertext[4];
    context->previous_ciphertext[5] = ciphertext[5];
    context->previous_ciphertext[6] = ciphertext[6];
    context->previous_ciphertext[7] = ciphertext[7];
    context->previous_ciphertext[8] = ciphertext[8];
    context->previous_ciphertext[9] = ciphertext[9];
    context->previous_ciphertext[10] = ciphertext[10];
    context->previous_ciphertext[0xb] = ciphertext[0xb];
    context->previous_ciphertext[0xc] = ciphertext[0xc];
    context->previous_ciphertext[0xd] = ciphertext[0xd];
    context->previous_ciphertext[0xe] = ciphertext[0xe];
    context->previous_ciphertext[0xf] = ciphertext[0xf];
    uVar1 = 0;
  }
  else {
    uVar1 = 0xff;
  }
  return uVar1;
}

uint boot_aes128_cbc_initialize
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
    uVar1 = boot_aes128_initialize_context(key,'\x10',&context->aes);
    if (uVar1 == 0) {
      (context->aes).valid = '\x01';
      return 0;
    }
  }
  return 0xff;
}

void boot_aes128_cbc_clear(F33BootAes128CbcContext *context)

{
  (context->aes).valid = '\0';
  zero_words_by_byte_count_76b6(context,0xe4);
  return;
}

void boot_ram_dispatch(int param_1)
{
  uint32_t slot = 0xfebf0f00u;
  uint32_t key;
  camry_write32((camry_sp - 4u) & ~3u, camry_gpr[29]);
  camry_write32((camry_sp - 8u) & ~3u, camry_gpr[31]);
  camry_sp -= 8u;
  camry_gpr[3] = camry_sp;
  camry_gpr[1] = 0;
  for (;;) {
    key = camry_read32(slot);
    if (key == 0xffffffffu || key == (uint32_t)param_1) break;
    slot += 8u;
    camry_gpr[1] += 1u;
  }
  camry_gpr[19] = key;
  camry_gpr[30] = slot;
  camry_gpr[29] = camry_read32(slot + 4u);
  camry_gpr[6] = (uint32_t)param_1;
  camry_gpr[31] = 0x8396u;
  camry_gpr[10] = ((uint32_t (*)(uint32_t, uint32_t, uint32_t, uint32_t))
      camry_indirect(camry_gpr[29]))
      (camry_gpr[6], camry_gpr[7], camry_gpr[8], camry_gpr[9]);
  if (camry_halted) return;
  camry_gpr[31] = camry_read32(camry_sp & ~3u);
  camry_gpr[29] = camry_read32((camry_sp + 4u) & ~3u);
  camry_sp += 8u;
  camry_gpr[3] = camry_sp;
  return;
}

void set_ebase_with_low_bit_one_preserving_irq_state_84f8(uint param_1)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  uint in_FPEC = camry_SR[0][11];
  uint in_RBASE = camry_SR[1][2];
  uint in_FPIPR = camry_SR[1][7];
  uint in_ISPR = camry_SR[2][10];
  
  if ((camry_psw & 0x20) == 0) {
    __disable_irq();
    camry_SR[1][3] = param_1 | 1u;
    __synchronize();
    if ((in_FPEC & 1) != 0) {
      uVar1 = in_FPIPR & 0x1f;
      if (0xf < uVar1) {
        uVar1 = 0x10;
      }
      uVar2 = uVar1;
      if (0xf < uVar1) {
        uVar2 = 0xf;
      }
      uVar3 = PMR;
      if ((((uVar3 & 1 << uVar2) == 0) && ((in_ISPR & (1 << uVar1 + 1) - 1U & 0xffff) == 0)) &&
         ((camry_psw & 0x80) == 0)) {
        if (((camry_psw & 0xbfffffd0) >> 0xf & 1) == 0) {
          param_1 = in_RBASE;
        }
        (*(int (*)())camry_indirect((uint32_t)((param_1 & 0xfffffe00) + 0x70)))();
      }
    }
    __enable_irq();
  }
  else {
    camry_SR[1][3] = param_1 | 1u;
    __synchronize();
  }
  return;
}

uint raise_flash_pmr_and_return_previous_mask_851c(int param_1)

{
  uint uVar1;
  uint uVar2;
  int iVar3;
  undefined4 uVar4;
  uint uVar5;
  uint in_FPEC = 0;
  uint in_RBASE = 0;
  uint in_EBASE = 0;
  uint in_FPIPR = 0;
  uint in_ISPR = 0;
  
  iVar3 = PMR;
  if (iVar3 - param_1 < 0 != (iVar3 < 0 != param_1 < 0 && param_1 < 0 == iVar3 - param_1 < 0)) {
    if ((camry_psw & 0x20) == 0) {
      __disable_irq();
      PMR = param_1;
      if ((in_FPEC & 1) != 0) {
        uVar4 = PMR;
      }
      if ((in_FPEC & 1) != 0) {
        uVar1 = in_FPIPR & 0x1f;
        if (0xf < uVar1) {
          uVar1 = 0x10;
        }
        uVar2 = uVar1;
        if (0xf < uVar1) {
          uVar2 = 0xf;
        }
        uVar5 = PMR;
        if ((((uVar5 & 1 << uVar2) == 0) && ((in_ISPR & (1 << uVar1 + 1) - 1U & 0xffff) == 0)) &&
           ((camry_psw & 0x80) == 0)) {
          if (((camry_psw & 0xbfffffd0) >> 0xf & 1) == 0) {
            in_EBASE = in_RBASE;
          }
          (*(int (*)())camry_indirect((uint32_t)((in_EBASE & 0xfffffe00) + 0x70)))();
        }
      }
      __enable_irq();
    }
    else {
      PMR = param_1;
      if ((in_FPEC & 1) != 0) {
        uVar1 = in_FPIPR & 0x1f;
        if (0xf < uVar1) {
          uVar1 = 0x10;
        }
        uVar2 = uVar1;
        if (0xf < uVar1) {
          uVar2 = 0xf;
        }
        uVar5 = PMR;
        if ((((uVar5 & 1 << uVar2) == 0) && ((in_ISPR & (1 << uVar1 + 1) - 1U & 0xffff) == 0)) &&
           ((camry_psw & 0xa0) == 0)) {
          if (((camry_psw & 0xbfffffb0) >> 0xf & 1) == 0) {
            in_EBASE = in_RBASE;
          }
          (*(int (*)())camry_indirect((uint32_t)((in_EBASE & 0xfffffe00) + 0x70)))();
        }
      }
    }
    __synchronize();
  }
  return iVar3;
}

void restore_flash_pmr_preserving_irq_state_8542(undefined4 param_1)

{
  uint uVar1;
  uint uVar2;
  undefined4 uVar3;
  uint uVar4;
  uint in_FPEC = 0;
  uint in_RBASE = 0;
  uint in_EBASE = 0;
  uint in_FPIPR = 0;
  uint in_ISPR = 0;
  
  if ((camry_psw >> 5 & 1) == 0) {
    __disable_irq();
    PMR = param_1;
    if ((in_FPEC & 1) != 0) {
      uVar3 = PMR;
    }
    if ((in_FPEC & 1) != 0) {
      uVar1 = in_FPIPR & 0x1f;
      if (0xf < uVar1) {
        uVar1 = 0x10;
      }
      uVar2 = uVar1;
      if (0xf < uVar1) {
        uVar2 = 0xf;
      }
      uVar4 = PMR;
      if ((((uVar4 & 1 << uVar2) == 0) && ((in_ISPR & (1 << uVar1 + 1) - 1U & 0xffff) == 0)) &&
         ((camry_psw & 0x80) == 0)) {
        if (((camry_psw & 0xbfffffd0) >> 0xf & 1) == 0) {
          in_EBASE = in_RBASE;
        }
        (*(int (*)())camry_indirect((uint32_t)((in_EBASE & 0xfffffe00) + 0x70)))();
      }
    }
    __enable_irq();
  }
  else {
    PMR = param_1;
    if ((in_FPEC & 1) != 0) {
      uVar1 = in_FPIPR & 0x1f;
      if (0xf < uVar1) {
        uVar1 = 0x10;
      }
      uVar2 = uVar1;
      if (0xf < uVar1) {
        uVar2 = 0xf;
      }
      uVar4 = PMR;
      if ((((uVar4 & 1 << uVar2) == 0) && ((in_ISPR & (1 << uVar1 + 1) - 1U & 0xffff) == 0)) &&
         ((camry_psw & 0xa0) == 0)) {
        if (((camry_psw & 0xbfffffb0) >> 0xf & 1) == 0) {
          in_EBASE = in_RBASE;
        }
        (*(int (*)())camry_indirect((uint32_t)((in_EBASE & 0xfffffe00) + 0x70)))();
      }
    }
  }
  __synchronize();
  return;
}

undefined4 check_flash_words_and_ecc_test_pattern_8560(int *param_1,uint param_2)

{
  uint uVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  int *piVar5;
  
  uVar3 = raise_flash_pmr_and_return_previous_mask_851c(0xffff);
  set_ebase_with_low_bit_one_preserving_irq_state_84f8(camry_host_addr(((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebf0c88u + (uint32_t)(0x3a4) * 1u)))));
  camry_write32(0xffc62400u, 0x4001);
  camry_write32(0xffc62200u, 0x4001);
  uVar4 = 0;
  uVar1 = camry_read32(0xffc62200u);
  __synchronize();
  __synchronize();
  piVar5 = param_1;
  for (iVar2 = 0;
      (int)(iVar2 - param_2) < 0 !=
      (iVar2 < 0 != (int)param_2 < 0 && (int)param_2 < 0 == (int)(iVar2 - param_2) < 0);
      iVar2 = iVar2 + 1) {
    if (*piVar5 != -1) {
      uVar4 = 1;
      goto LAB_000085fa;
    }
    piVar5 = piVar5 + 1;
  }
  camry_write32(0xffc624f0u, 0x4001);
  camry_write32(0xffc622f0u, 0x4001);
  uVar1 = camry_read32(0xffc622f0u);
  __synchronize();
  __synchronize();
  param_2 = param_2 >> 2;
  do {
    if (param_2 == 0) {
LAB_000085e2:
      camry_write32(0xffc624f0u, 0x4000);
      camry_write32(0xffc622f0u, 0x4000);
      uVar1 = camry_read32(0xffc622f0u);
      __synchronize();
      __synchronize();
LAB_000085fa:
      camry_write32(0xffc62400u, 0x4000);
      camry_write32(0xffc62200u, 0x4000);
      uVar1 = camry_read32(0xffc62200u);
      __synchronize();
      __synchronize();
      set_ebase_with_low_bit_one_preserving_irq_state_84f8(0);
      restore_flash_pmr_preserving_irq_state_8542(uVar3);
      return uVar4;
    }
    if (*param_1 != 0x3ff) {
      uVar4 = 1;
      goto LAB_000085e2;
    }
    param_1 = param_1 + 4;
    param_2 = param_2 - 1;
  } while( true );
}

void load_self_id_words_from_selected_flash_area_8628(void)

{
  uint uVar1;
  undefined1 uVar2;
  undefined4 uVar3;
  
  uVar3 = raise_flash_pmr_and_return_previous_mask_851c(0xffff);
  set_ebase_with_low_bit_one_preserving_irq_state_84f8(camry_host_addr(((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebf0c88u + (uint32_t)(0x3a4) * 1u)))));
  (*((volatile uint8_t *)camry_host_ptr(0xffc59008u))) = 1;
  uVar2 = (*((volatile uint8_t *)camry_host_ptr(0xffc59008u)));
  __synchronize();
  __synchronize();
  SELFID0 = (*((volatile int32_t *)camry_host_ptr(0xff300050u)));
  SELFID1 = (*((volatile int32_t *)camry_host_ptr(0xff300054u)));
  SELFID2 = (*((volatile int32_t *)camry_host_ptr(0xff300058u)));
  SELFID3 = (*((volatile int32_t *)camry_host_ptr(0xff30005cu)));
  uVar1 = SELFID3;
  __synchronize();
  (*((volatile uint8_t *)camry_host_ptr(0xffc59008u))) = 0;
  uVar2 = (*((volatile uint8_t *)camry_host_ptr(0xffc59008u)));
  __synchronize();
  __synchronize();
  set_ebase_with_low_bit_one_preserving_irq_state_84f8(0);
  restore_flash_pmr_preserving_irq_state_8542(uVar3);
  return;
}
