#include "common.h"

uint32_t boot_security_encrypt_block(uchar *key,uchar *plaintext,uchar *ciphertext)

{
  uint32_t camry_r10_result;
  (camry_r10_result = boot_aes128_initialize_context(key, '\x10', ((F33BootAes128Context *)camry_host_ptr((uint32_t)(((camry_gp + 0xffff9548u)))))));
  (camry_r10_result = boot_aes128_encrypt_block(plaintext, ciphertext, '\x10', ((F33BootAes128Context *)camry_host_ptr((uint32_t)(((camry_gp + 0xffff9548u)))))));
  boot_aes128_clear_context(((F33BootAes128Context *)camry_host_ptr((uint32_t)(((camry_gp + 0xffff9548u))))));
  return camry_r10_result;
}

uint32_t boot_security_derive_expected_key
               (uchar *client_material,uchar *challenge,uchar *expected_key)

{
  uchar auStack_1c [16];
  
  boot_security_decrypt_client_material(client_material,auStack_1c);
  return boot_security_encrypt_block(auStack_1c,challenge,expected_key);
}

uint32_t boot_image_derive_key(void)

{
  uint32_t camry_r10_result;
  uint32_t puVar1;
  puVar1 = (camry_gp + 0x0u);
  (camry_r10_result = boot_aes128_initialize_context
            (boot_image_key_derivation_key, '\x10', ((F33BootAes128Context *)camry_host_ptr((uint32_t)(((camry_gp + 0xffff9548u)))))));
  (camry_r10_result = boot_aes128_encrypt_block
            (((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x6af8))),  ((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x6ae8))),  '\x10', ((F33BootAes128Context *)camry_host_ptr((uint32_t)(((camry_gp + 0xffff9548u)))))));
  boot_aes128_clear_context(((F33BootAes128Context *)camry_host_ptr((uint32_t)(((camry_gp + 0xffff9548u))))));
  return camry_r10_result;
}

uint boot_image_initialize_contexts(void)

{
  uint32_t puVar1;
  puVar1 = (camry_gp + 0x0u);
  boot_aes128_cbc_initialize
            (((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9518u))), '\x10', ((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff94f8u))), '\x10', ((F33BootAes128CbcContext *)camry_host_ptr((uint32_t)(((camry_gp + 0xffff96f0u))))));
  boot_aes128_cmac_initialize
            (((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9518u))),'\x10',((F33BootAes128CmacContext *)camry_host_ptr((uint32_t)(puVar1 + -0x6c00))));
  return boot_aes128_cmac_derive_subkeys(((F33BootAes128CmacContext *)camry_host_ptr((uint32_t)(puVar1 + -0x6c00))));
}

uint boot_image_crypto_initialize(void)

{
  boot_image_derive_key();
  return boot_image_initialize_contexts();
}

void boot_image_clear_contexts(void)

{
  uint32_t puVar1;
  puVar1 = (camry_gp + 0x0u);
  boot_aes128_cbc_clear(((F33BootAes128CbcContext *)camry_host_ptr((uint32_t)(((camry_gp + 0xffff96f0u))))));
  boot_aes128_cmac_clear(((F33BootAes128CmacContext *)camry_host_ptr((uint32_t)(puVar1 + -0x6c00))));
  return;
}

void boot_image_crypto_clear(void)

{
  boot_image_clear_contexts();
  return;
}

uint boot_image_decrypt_block(uchar *ciphertext,uchar *plaintext)

{
  uint uVar1;
  
  uVar1 = boot_aes128_cbc_decrypt_block(ciphertext, plaintext, '\x10', ((F33BootAes128CbcContext *)camry_host_ptr((uint32_t)(((camry_gp + 0xffff96f0u))))))
  ;
  return (uint)(uVar1 != 0);
}

uint boot_image_authentication_begin(uint start,uint length)

{
  uint32_t puVar1;
  uint uVar2;
  uint uVar3;
  uint uStack_14;
  
  puVar1 = (camry_gp + 0x0u);
  uVar3 = 1;
  uVar2 = boot_lookup_authentication_trailer(start,length,&uStack_14);
  if (uVar2 == 0) {
    (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x6754)))) = uStack_14;
    uVar2 = boot_aes128_cmac_update_block
                      (((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x6b08))), ((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x6ad8))), '\x10', 0, 
                       ((F33BootAes128CmacContext *)camry_host_ptr((uint32_t)(puVar1 + -0x6c00))));
    if (uVar2 == 0) {
      (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x6750)))) = start;
      (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x6758)))) = length + start + -0x10;
      uVar3 = 0;
    }
  }
  return uVar3;
}

uint boot_image_authentication_step(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint32_t puVar4;
  uint uVar5;
  uint32_t puVar6;
  uint uVar7;
  
  puVar4 = (camry_gp + 0x0u);
  uVar7 = 0;
  puVar6 = (*((volatile uint32_t *)camry_host_ptr((camry_gp + 0xffff98b0u)))) + 0x10;
  if (((*((volatile uint32_t *)camry_host_ptr((camry_gp + 0xffff98b0u)))) == (uint32_t)((*((volatile uint32_t *)camry_host_ptr((camry_gp + 0xffff98a8u)))))) ||
     ((puVar6 == (uint32_t)((*((volatile uint32_t *)camry_host_ptr((camry_gp + 0xffff98a8u)))) )&&
      (puVar6 == (*((volatile uint32_t *)camry_host_ptr((camry_gp + 0xffff98acu)))))))) {
    uVar7 = 1;
  }
  if ((*((volatile uint32_t *)camry_host_ptr((camry_gp + 0xffff98b0u)))) != (*((volatile uint32_t *)camry_host_ptr((camry_gp + 0xffff98acu))))) {
    puVar4 = (camry_gp + 0x0u);
    uVar5 = boot_aes128_cmac_update_block
                      (((uchar *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((camry_gp + 0xffff98b0u))))))), ((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9528u))), 
                       '\x10', uVar7, ((F33BootAes128CmacContext *)camry_host_ptr((uint32_t)(((camry_gp + 0xffff9400u))))));
    if (uVar5 != 0) {
LAB_000071e4:
      uVar7 = 1;
      goto LAB_000071e6;
    }
    if (uVar7 == 1) {
      iVar3 = 0;
      do {
        if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff9528u) + (uint32_t)(iVar3) * 1u)))) != (*((volatile uchar *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)((puVar4 + -0x6754))))))))))
        goto LAB_000071e4;
        iVar2 = iVar3 + 1;
        (*((volatile uint32_t *)camry_host_ptr((uint32_t)((puVar4 + -0x6754))))) = ((uint32_t)((uint32_t)((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)((puVar4 + -0x6754)))))) + (uint32_t)(1) * 1u)));
        iVar1 = iVar3 + -0xf;
        iVar3 = iVar2;
      } while (((iVar1 < 0) || (iVar2 < 0)));
      uVar7 = 0;
      goto LAB_000071e6;
    }
  }
  uVar7 = 2;
LAB_000071e6:
  (*((volatile uint32_t *)camry_host_ptr((uint32_t)((puVar4 + -0x6750))))) = puVar6;
  return uVar7;
}

void busy_wait_155_decrements_per_unit_7208(int param_1)

{
  bool bVar1;
  int iVar2;
  
  if (param_1 != 0) {
    do {
      iVar2 = 0x9b;
      do {
        bVar1 = iVar2 != 1;
        iVar2 = iVar2 + -1;
      } while (bVar1);
      bVar1 = param_1 != 1;
      param_1 = param_1 + -1;
    } while (bVar1);
  }
  return;
}

uint raise_pmr_and_return_previous_mask_721e(int param_1)

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

void restore_pmr_preserving_interrupt_disable_state_7244(undefined4 param_1)

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

char saturating_increment_u8_7262(char param_1)

{
  if (param_1 != -1) {
    return param_1 + '\x01';
  }
  return -1;
}

uint boot_security_generate_candidate_block
               (uchar *challenge_out,F33BootAes128CtrContext *context)

{
  undefined1 uVar1;
  uchar *puVar2;
  uint uVar3;
  uint uVar4;
  undefined1 *puVar5;
  uchar local_14 [16];
  
  puVar2 = local_14;
  puVar5 = ((undefined *)camry_host_ptr((camry_tp + 0x924u)));
  do {
    uVar1 = *puVar5;
    puVar5 = puVar5 + 1;
    *puVar2 = uVar1;
    puVar2 = puVar2 + 1;
  } while (camry_host_addr(puVar5)!=((uint32_t)(camry_tp + 0x934u)));
  uVar4 = boot_aes128_ctr_transform_block(local_14,challenge_out,'\x10',context);
  uVar3 = 0;
  if (uVar4 != 0) {
    uVar3 = 0xff;
  }
  return uVar3;
}

uint boot_security_initialize_candidate_context
               (uchar *timer_key,uchar key_length,F33BootAes128CtrContext *context)

{
  uchar uVar1;
  uchar *puVar2;
  uint uVar3;
  uchar *puVar4;
  uchar local_14 [16];
  
  puVar4 = "";
  puVar2 = local_14;
  do {
    uVar1 = *puVar4;
    puVar4 = puVar4 + 1;
    *puVar2 = uVar1;
    puVar2 = puVar2 + 1;
  } while (camry_host_addr(puVar4)!=((uint32_t)(camry_tp + 0x944u)));
  if ((key_length == '\x10') &&
     (uVar3 = boot_aes128_ctr_initialize(timer_key,'\x10',local_14,'\x10',context), uVar3 == 0))
  {
    return 0;
  }
  return 0xff;
}

undefined4 boot_reinitialize_valid_aes_ctr_with_existing_counter_7316(uchar *param_1,char param_2,F33BootAes128CtrContext *param_3)

{
  uint uVar1;
  
  if (((param_2 == '\x10') && ((param_3->aes).valid == '\x01')) &&
     (uVar1 = boot_aes128_ctr_initialize(param_1,'\x10',param_3->counter_be,'\x10',param_3),
     uVar1 == 0)) {
    return 0;
  }
  return 0xff;
}

void boot_security_clear_candidate_context(F33BootAes128CtrContext *context)

{
  boot_aes128_ctr_clear(context);
  return;
}

uint boot_aes128_encrypt_block
               (uchar *plaintext,uchar *ciphertext,uchar length,F33BootAes128Context *context)

{
  byte bVar1;
  uint uVar2;
  
  if ((length == '\x10') && (context->valid == '\x01')) {
    context->round = '\0';
    context->row_order_state[0] = *plaintext;
    context->row_order_state[4] = plaintext[1];
    context->row_order_state[8] = plaintext[2];
    context->row_order_state[0xc] = plaintext[3];
    context->row_order_state[1] = plaintext[4];
    context->row_order_state[5] = plaintext[5];
    context->row_order_state[9] = plaintext[6];
    context->row_order_state[0xd] = plaintext[7];
    context->row_order_state[2] = plaintext[8];
    context->row_order_state[6] = plaintext[9];
    context->row_order_state[10] = plaintext[10];
    context->row_order_state[0xe] = plaintext[0xb];
    context->row_order_state[3] = plaintext[0xc];
    context->row_order_state[7] = plaintext[0xd];
    context->row_order_state[0xb] = plaintext[0xe];
    context->row_order_state[0xf] = plaintext[0xf];
    while( true ) {
      aes_add_round_key_transposed_state_76da(camry_host_addr(context));
      bVar1 = context->round + 1;
      context->round = bVar1;
      aes_substitute_state_bytes_77a8(camry_host_addr(context));
      aes_shift_state_rows_786e(camry_host_addr(context));
      if (9 < bVar1) break;
      aes_mix_state_columns_7896(camry_host_addr(context));
    }
    aes_add_round_key_transposed_state_76da(camry_host_addr(context));
    uVar2 = 0;
    *ciphertext = context->row_order_state[0];
    ciphertext[1] = context->row_order_state[4];
    ciphertext[2] = context->row_order_state[8];
    ciphertext[3] = context->row_order_state[0xc];
    ciphertext[4] = context->row_order_state[1];
    ciphertext[5] = context->row_order_state[5];
    ciphertext[6] = context->row_order_state[9];
    ciphertext[7] = context->row_order_state[0xd];
    ciphertext[8] = context->row_order_state[2];
    ciphertext[9] = context->row_order_state[6];
    ciphertext[10] = context->row_order_state[10];
    ciphertext[0xb] = context->row_order_state[0xe];
    ciphertext[0xc] = context->row_order_state[3];
    ciphertext[0xd] = context->row_order_state[7];
    ciphertext[0xe] = context->row_order_state[0xb];
    ciphertext[0xf] = context->row_order_state[0xf];
  }
  else {
    uVar2 = 0xff;
  }
  return uVar2;
}

uint boot_aes128_decrypt_block
               (uchar *ciphertext,uchar *plaintext,uchar length,F33BootAes128Context *context)

{
  uchar uVar1;
  uint uVar2;
  
  if ((length == '\x10') && (context->valid == '\x01')) {
    context->round = '\n';
    context->row_order_state[0] = *ciphertext;
    context->row_order_state[4] = ciphertext[1];
    context->row_order_state[8] = ciphertext[2];
    context->row_order_state[0xc] = ciphertext[3];
    context->row_order_state[1] = ciphertext[4];
    context->row_order_state[5] = ciphertext[5];
    context->row_order_state[9] = ciphertext[6];
    context->row_order_state[0xd] = ciphertext[7];
    context->row_order_state[2] = ciphertext[8];
    context->row_order_state[6] = ciphertext[9];
    context->row_order_state[10] = ciphertext[10];
    context->row_order_state[0xe] = ciphertext[0xb];
    context->row_order_state[3] = ciphertext[0xc];
    context->row_order_state[7] = ciphertext[0xd];
    context->row_order_state[0xb] = ciphertext[0xe];
    context->row_order_state[0xf] = ciphertext[0xf];
    aes_add_round_key_transposed_state_76da(camry_host_addr(context));
    while( true ) {
      uVar1 = context->round + 0xff;
      context->round = uVar1;
      aes_inverse_shift_state_rows_79ee(camry_host_addr(context));
      aes_inverse_substitute_state_bytes_7928(camry_host_addr(context));
      aes_add_round_key_transposed_state_76da(camry_host_addr(context));
      if (uVar1 == '\0') break;
      aes_inverse_mix_state_columns_7a16(camry_host_addr(context));
    }
    *plaintext = context->row_order_state[0];
    plaintext[1] = context->row_order_state[4];
    plaintext[2] = context->row_order_state[8];
    plaintext[3] = context->row_order_state[0xc];
    plaintext[4] = context->row_order_state[1];
    plaintext[5] = context->row_order_state[5];
    plaintext[6] = context->row_order_state[9];
    plaintext[7] = context->row_order_state[0xd];
    plaintext[8] = context->row_order_state[2];
    plaintext[9] = context->row_order_state[6];
    plaintext[10] = context->row_order_state[10];
    plaintext[0xb] = context->row_order_state[0xe];
    plaintext[0xc] = context->row_order_state[3];
    plaintext[0xd] = context->row_order_state[7];
    plaintext[0xe] = context->row_order_state[0xb];
    plaintext[0xf] = context->row_order_state[0xf];
    uVar2 = 0;
  }
  else {
    uVar2 = 0xff;
  }
  return uVar2;
}

void boot_aes128_expand_round_keys(uchar *key,uchar *round_keys)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  
  uVar3 = 4;
  *round_keys = *key;
  round_keys[1] = key[1];
  round_keys[2] = key[2];
  round_keys[3] = key[3];
  round_keys[4] = key[4];
  round_keys[5] = key[5];
  round_keys[6] = key[6];
  round_keys[7] = key[7];
  round_keys[8] = key[8];
  round_keys[9] = key[9];
  round_keys[10] = key[10];
  round_keys[0xb] = key[0xb];
  round_keys[0xc] = key[0xc];
  round_keys[0xd] = key[0xd];
  round_keys[0xe] = key[0xe];
  round_keys[0xf] = key[0xf];
  do {
    iVar1 = uVar3 * 4;
    uVar2 = *(uint *)(round_keys + iVar1 + -4);
    if ((uVar3 & 3) == 0) {
      uVar2 = (uint)(*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x955u) + (uint32_t)(uVar2 & 0xff) * 1u)))) << 0x18 |
              (uint)(*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x955u) + (uint32_t)(uVar2 >> 0x18) * 1u)))) << 0x10 |
              (uint)(*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x955u) + (uint32_t)((uVar2 >> 8 & 0xffff) >> 8) * 1u)))) << 8 |
              (uint)((*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x944u) + (uint32_t)((int)uVar3 >> 2) * 1u)))) ^ (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x955u) + (uint32_t)(uVar2 >> 8 & 0xff) * 1u))))
                    );
    }
    uVar3 = uVar3 + 1 & 0xffff;
    *(uint *)(round_keys + iVar1) = (*((uint *)camry_host_ptr((uint32_t)((int)camry_host_addr((round_keys + iVar1)) + -0x10)))) ^ uVar2;
  } while (uVar3 < 0x2c);
  return;
}

uint boot_aes128_initialize_context(uchar *key,uchar key_length,F33BootAes128Context *context)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  
  if (key_length == '\x10') {
    context->valid = '\0';
    context->row_order_state[0] = '\0';
    context->row_order_state[1] = '\0';
    context->row_order_state[2] = '\0';
    context->row_order_state[3] = '\0';
    context->row_order_state[4] = '\0';
    context->row_order_state[5] = '\0';
    context->row_order_state[6] = '\0';
    context->row_order_state[7] = '\0';
    context->row_order_state[8] = '\0';
    context->row_order_state[9] = '\0';
    context->row_order_state[10] = '\0';
    context->row_order_state[0xb] = '\0';
    context->row_order_state[0xc] = '\0';
    context->row_order_state[0xd] = '\0';
    context->row_order_state[0xe] = '\0';
    context->row_order_state[0xf] = '\0';
    context->round = '\0';
    uVar2 = 4;
    context->round_keys[0] = *key;
    context->round_keys[1] = key[1];
    context->round_keys[2] = key[2];
    context->round_keys[3] = key[3];
    context->round_keys[4] = key[4];
    context->round_keys[5] = key[5];
    context->round_keys[6] = key[6];
    context->round_keys[7] = key[7];
    context->round_keys[8] = key[8];
    context->round_keys[9] = key[9];
    context->round_keys[10] = key[10];
    context->round_keys[0xb] = key[0xb];
    context->round_keys[0xc] = key[0xc];
    context->round_keys[0xd] = key[0xd];
    context->round_keys[0xe] = key[0xe];
    context->round_keys[0xf] = key[0xf];
    do {
      iVar1 = uVar2 * 4;
      uVar3 = *(uint *)(context->round_keys + iVar1 + -4);
      if ((uVar2 & 3) == 0) {
        uVar3 = (uint)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x8ff1u + (uint32_t)(uVar3 & 0xff) * 1u)))) << 0x18 |
                (uint)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x8ff1u + (uint32_t)(uVar3 >> 0x18) * 1u)))) << 0x10 |
                (uint)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x8ff1u + (uint32_t)((uVar3 >> 8 & 0xffff) >> 8) * 1u)))) << 8 |
                (uint)((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x8fe0u + (uint32_t)((int)uVar2 >> 2) * 1u)))) ^
                      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x8ff1u + (uint32_t)(uVar3 >> 8 & 0xff) * 1u)))));
      }
      uVar2 = uVar2 + 1 & 0xffff;
      *(uint *)(context->round_keys + iVar1) =
           *(uint *)(context->round_keys + iVar1 + -0x10) ^ uVar3;
    } while (uVar2 < 0x2c);
    context->valid = '\x01';
    uVar2 = 0;
  }
  else {
    uVar2 = 0xff;
  }
  return uVar2;
}

void zero_words_by_byte_count_76b6(undefined4 *param_1,int param_2)

{
  for (; param_2 != 0; param_2 = param_2 + -4) {
    *param_1 = 0;
    param_1 = param_1 + 1;
  }
  return;
}

void boot_aes128_clear_context(F33BootAes128Context *context)

{
  context->valid = '\0';
  zero_words_by_byte_count_76b6(context,0xc4);
  return;
}

void aes_add_round_key_transposed_state_76da(int param_1)

{
  byte *pbVar1;
  
  pbVar1 = ((byte *)camry_host_ptr((uint32_t)(param_1 + ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(param_1 + 0xc1)))) & 0xf) * 0x10)));
  (*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xb0)))) = (*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xb0)))) ^ *pbVar1;
  (*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xb4)))) = (*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xb4)))) ^ pbVar1[1];
  (*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xb8)))) = (*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xb8)))) ^ pbVar1[2];
  (*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xbc)))) = (*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xbc)))) ^ pbVar1[3];
  (*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xb1)))) = (*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xb1)))) ^ pbVar1[4];
  (*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xb5)))) = (*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xb5)))) ^ pbVar1[5];
  (*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xb9)))) = (*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xb9)))) ^ pbVar1[6];
  (*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xbd)))) = (*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xbd)))) ^ pbVar1[7];
  (*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xb2)))) = (*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xb2)))) ^ pbVar1[8];
  (*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xb6)))) = (*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xb6)))) ^ pbVar1[9];
  (*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xba)))) = (*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xba)))) ^ pbVar1[10];
  (*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xbe)))) = (*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xbe)))) ^ pbVar1[0xb];
  (*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xb3)))) = (*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xb3)))) ^ pbVar1[0xc];
  (*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xb7)))) = (*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xb7)))) ^ pbVar1[0xd];
  (*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xbb)))) = (*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xbb)))) ^ pbVar1[0xe];
  (*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xbf)))) = (*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xbf)))) ^ pbVar1[0xf];
  return;
}

void aes_substitute_state_bytes_77a8(int param_1)

{
  (*((uchar *)camry_host_ptr((uint32_t)(param_1 + 0xb0)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x955u) + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xb0))))) * 1u))));
  (*((uchar *)camry_host_ptr((uint32_t)(param_1 + 0xb1)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x955u) + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xb1))))) * 1u))));
  (*((uchar *)camry_host_ptr((uint32_t)(param_1 + 0xb2)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x955u) + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xb2))))) * 1u))));
  (*((uchar *)camry_host_ptr((uint32_t)(param_1 + 0xb3)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x955u) + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xb3))))) * 1u))));
  (*((uchar *)camry_host_ptr((uint32_t)(param_1 + 0xb4)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x955u) + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xb4))))) * 1u))));
  (*((uchar *)camry_host_ptr((uint32_t)(param_1 + 0xb5)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x955u) + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xb5))))) * 1u))));
  (*((uchar *)camry_host_ptr((uint32_t)(param_1 + 0xb6)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x955u) + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xb6))))) * 1u))));
  (*((uchar *)camry_host_ptr((uint32_t)(param_1 + 0xb7)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x955u) + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xb7))))) * 1u))));
  (*((uchar *)camry_host_ptr((uint32_t)(param_1 + 0xb8)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x955u) + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xb8))))) * 1u))));
  (*((uchar *)camry_host_ptr((uint32_t)(param_1 + 0xb9)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x955u) + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xb9))))) * 1u))));
  (*((uchar *)camry_host_ptr((uint32_t)(param_1 + 0xba)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x955u) + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xba))))) * 1u))));
  (*((uchar *)camry_host_ptr((uint32_t)(param_1 + 0xbb)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x955u) + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xbb))))) * 1u))));
  (*((uchar *)camry_host_ptr((uint32_t)(param_1 + 0xbc)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x955u) + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xbc))))) * 1u))));
  (*((uchar *)camry_host_ptr((uint32_t)(param_1 + 0xbd)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x955u) + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xbd))))) * 1u))));
  (*((uchar *)camry_host_ptr((uint32_t)(param_1 + 0xbe)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x955u) + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xbe))))) * 1u))));
  (*((uchar *)camry_host_ptr((uint32_t)(param_1 + 0xbf)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x955u) + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xbf))))) * 1u))));
  return;
}

void aes_shift_state_rows_786e(int param_1)

{
  (*((uint *)camry_host_ptr((uint32_t)(param_1 + 0xb4)))) = (*((uint *)camry_host_ptr((uint32_t)(param_1 + 0xb4)))) << 0x18 | (*((uint *)camry_host_ptr((uint32_t)(param_1 + 0xb4)))) >> 8;
  (*((uint *)camry_host_ptr((uint32_t)(param_1 + 0xb8)))) = (*((uint *)camry_host_ptr((uint32_t)(param_1 + 0xb8)))) << 0x10 | (*((uint *)camry_host_ptr((uint32_t)(param_1 + 0xb8)))) >> 0x10;
  (*((uint *)camry_host_ptr((uint32_t)(param_1 + 0xbc)))) = (*((uint *)camry_host_ptr((uint32_t)(param_1 + 0xbc)))) << 8 | (*((uint *)camry_host_ptr((uint32_t)(param_1 + 0xbc)))) >> 0x18;
  return;
}

void aes_mix_state_columns_7896(int param_1)

{
  byte *pbVar1;
  int iVar2;
  byte bVar3;
  byte bVar4;
  byte bVar5;
  byte bVar6;
  uint uVar7;
  
  param_1 = param_1 + 0xb0;
  uVar7 = 0;
  do {
    pbVar1 = ((byte *)camry_host_ptr((uint32_t)(uVar7 + param_1)));
    bVar3 = *pbVar1;
    bVar4 = pbVar1[4] ^ bVar3;
    bVar6 = bVar4 << 1;
    bVar5 = pbVar1[8] ^ bVar4 ^ pbVar1[0xc];
    if ((char)bVar4 < '\0') {
      bVar6 = bVar6 ^ 0x1b;
    }
    pbVar1 = ((byte *)camry_host_ptr((uint32_t)(uVar7 + param_1)));
    *pbVar1 = bVar5 ^ bVar6 ^ bVar3;
    bVar4 = pbVar1[8] ^ pbVar1[4];
    bVar6 = bVar4 << 1;
    if ((char)bVar4 < '\0') {
      bVar6 = bVar6 ^ 0x1b;
    }
    iVar2 = uVar7 + param_1;
    (*((byte *)camry_host_ptr((uint32_t)(iVar2 + 4)))) = bVar5 ^ bVar6 ^ pbVar1[4];
    bVar4 = (*((byte *)camry_host_ptr((uint32_t)(iVar2 + 0xc)))) ^ (*((byte *)camry_host_ptr((uint32_t)(iVar2 + 8))));
    bVar6 = bVar4 << 1;
    if ((char)bVar4 < '\0') {
      bVar6 = bVar6 ^ 0x1b;
    }
    (*((byte *)camry_host_ptr((uint32_t)(uVar7 + param_1 + 8)))) = bVar5 ^ bVar6 ^ (*((byte *)camry_host_ptr((uint32_t)(iVar2 + 8))));
    bVar4 = (*((byte *)camry_host_ptr((uint32_t)(uVar7 + param_1 + 0xc))));
    bVar3 = bVar3 ^ bVar4;
    bVar6 = bVar3 << 1;
    if ((char)bVar3 < '\0') {
      bVar6 = bVar6 ^ 0x1b;
    }
    (*((byte *)camry_host_ptr((uint32_t)(uVar7 + param_1 + 0xc)))) = bVar5 ^ bVar6 ^ bVar4;
    uVar7 = uVar7 + 1;
  } while (uVar7 < 4);
  return;
}

void aes_inverse_substitute_state_bytes_7928(int param_1)

{
  (*((uchar *)camry_host_ptr((uint32_t)(param_1 + 0xb0)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0xa55u) + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xb0))))) * 1u))));
  (*((uchar *)camry_host_ptr((uint32_t)(param_1 + 0xb1)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0xa55u) + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xb1))))) * 1u))));
  (*((uchar *)camry_host_ptr((uint32_t)(param_1 + 0xb2)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0xa55u) + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xb2))))) * 1u))));
  (*((uchar *)camry_host_ptr((uint32_t)(param_1 + 0xb3)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0xa55u) + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xb3))))) * 1u))));
  (*((uchar *)camry_host_ptr((uint32_t)(param_1 + 0xb4)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0xa55u) + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xb4))))) * 1u))));
  (*((uchar *)camry_host_ptr((uint32_t)(param_1 + 0xb5)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0xa55u) + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xb5))))) * 1u))));
  (*((uchar *)camry_host_ptr((uint32_t)(param_1 + 0xb6)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0xa55u) + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xb6))))) * 1u))));
  (*((uchar *)camry_host_ptr((uint32_t)(param_1 + 0xb7)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0xa55u) + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xb7))))) * 1u))));
  (*((uchar *)camry_host_ptr((uint32_t)(param_1 + 0xb8)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0xa55u) + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xb8))))) * 1u))));
  (*((uchar *)camry_host_ptr((uint32_t)(param_1 + 0xb9)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0xa55u) + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xb9))))) * 1u))));
  (*((uchar *)camry_host_ptr((uint32_t)(param_1 + 0xba)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0xa55u) + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xba))))) * 1u))));
  (*((uchar *)camry_host_ptr((uint32_t)(param_1 + 0xbb)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0xa55u) + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xbb))))) * 1u))));
  (*((uchar *)camry_host_ptr((uint32_t)(param_1 + 0xbc)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0xa55u) + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xbc))))) * 1u))));
  (*((uchar *)camry_host_ptr((uint32_t)(param_1 + 0xbd)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0xa55u) + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xbd))))) * 1u))));
  (*((uchar *)camry_host_ptr((uint32_t)(param_1 + 0xbe)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0xa55u) + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xbe))))) * 1u))));
  (*((uchar *)camry_host_ptr((uint32_t)(param_1 + 0xbf)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0xa55u) + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xbf))))) * 1u))));
  return;
}

void aes_inverse_shift_state_rows_79ee(int param_1)

{
  (*((uint *)camry_host_ptr((uint32_t)(param_1 + 0xb4)))) = (*((uint *)camry_host_ptr((uint32_t)(param_1 + 0xb4)))) >> 0x18 | (*((uint *)camry_host_ptr((uint32_t)(param_1 + 0xb4)))) << 8;
  (*((uint *)camry_host_ptr((uint32_t)(param_1 + 0xb8)))) = (*((uint *)camry_host_ptr((uint32_t)(param_1 + 0xb8)))) >> 0x10 | (*((uint *)camry_host_ptr((uint32_t)(param_1 + 0xb8)))) << 0x10;
  (*((uint *)camry_host_ptr((uint32_t)(param_1 + 0xbc)))) = (*((uint *)camry_host_ptr((uint32_t)(param_1 + 0xbc)))) >> 8 | (*((uint *)camry_host_ptr((uint32_t)(param_1 + 0xbc)))) << 0x18;
  return;
}

void aes_inverse_mix_state_columns_7a16(int param_1)

{
  byte *pbVar1;
  byte bVar2;
  byte bVar3;
  byte bVar4;
  byte bVar5;
  uint uVar6;
  uint uVar7;
  uint uVar8;
  uint uVar9;
  byte bVar10;
  byte bVar11;
  byte bVar12;
  uint uVar13;
  byte local_4 [4];
  
  param_1 = param_1 + 0xb0;
  uVar8 = 0;
  do {
    uVar9 = 0;
    do {
      bVar5 = (*((byte *)camry_host_ptr((uint32_t)(uVar8 + uVar9 * 4 + param_1))));
      uVar13 = (uint)bVar5;
      uVar6 = uVar13 << 1;
      if ((char)bVar5 < '\0') {
        uVar6 = uVar6 ^ 0x1b;
      }
      uVar7 = (uVar6 ^ uVar13) << 1;
      if (((uVar6 ^ uVar13) >> 7 & 1) != 0) {
        uVar7 = uVar7 ^ 0x1b;
      }
      bVar5 = (byte)((uVar7 ^ uVar13) << 1);
      if (((uVar7 ^ uVar13) >> 7 & 1) != 0) {
        bVar5 = bVar5 ^ 0x1b;
      }
      bVar2 = (*((byte *)camry_host_ptr((uint32_t)(uVar8 + (uVar9 + 1 & 3) * 4 + param_1))));
      uVar6 = (uint)bVar2 << 1;
      if ((char)bVar2 < '\0') {
        uVar6 = uVar6 ^ 0x1b;
      }
      uVar13 = uVar6 << 1;
      if ((uVar6 >> 7 & 1) != 0) {
        uVar13 = uVar13 ^ 0x1b;
      }
      uVar13 = uVar13 ^ bVar2;
      bVar12 = (byte)(uVar13 << 1);
      if ((uVar13 >> 7 & 1) != 0) {
        bVar12 = bVar12 ^ 0x1b;
      }
      bVar3 = (*((byte *)camry_host_ptr((uint32_t)(uVar8 + (uVar9 + 2 & 3) * 4 + param_1))));
      uVar6 = (uint)bVar3 << 1;
      if ((char)bVar3 < '\0') {
        uVar6 = uVar6 ^ 0x1b;
      }
      uVar6 = uVar6 ^ bVar3;
      uVar13 = uVar6 << 1;
      if ((uVar6 >> 7 & 1) != 0) {
        uVar13 = uVar13 ^ 0x1b;
      }
      bVar11 = (byte)(uVar13 << 1);
      if ((uVar13 >> 7 & 1) != 0) {
        bVar11 = bVar11 ^ 0x1b;
      }
      bVar4 = (*((byte *)camry_host_ptr((uint32_t)(uVar8 + (uVar9 - 1 & 3) * 4 + param_1))));
      uVar6 = (uint)bVar4 << 1;
      if ((char)bVar4 < '\0') {
        uVar6 = uVar6 ^ 0x1b;
      }
      uVar13 = uVar6 << 1;
      if ((uVar6 >> 7 & 1) != 0) {
        uVar13 = uVar13 ^ 0x1b;
      }
      bVar10 = (byte)(uVar13 << 1);
      if ((uVar13 >> 7 & 1) != 0) {
        bVar10 = bVar10 ^ 0x1b;
      }
      local_4[uVar9] = bVar10 ^ bVar4 ^ bVar11 ^ bVar3 ^ bVar12 ^ bVar2 ^ bVar5;
      uVar9 = uVar9 + 1;
    } while (uVar9 < 4);
    pbVar1 = ((byte *)camry_host_ptr((uint32_t)(uVar8 + param_1)));
    uVar8 = uVar8 + 1;
    *pbVar1 = local_4[0];
    pbVar1[4] = local_4[1];
    pbVar1[8] = local_4[2];
    pbVar1[0xc] = local_4[3];
  } while (uVar8 < 4);
  return;
}

uint boot_aes128_ctr_transform_block
               (uchar *input,uchar *output,uchar length,F33BootAes128CtrContext *context)

{
  uint8_t stack_record_20[32];
  uchar *puVar1;
  int iVar2;
  uchar uVar3;
  uint uVar4;
  int iVar5;
  uchar *plaintext;
  
  if ((((length == '\x10') && ((context->aes).valid == '\x01')) &&
      ((plaintext = context->counter_be, *(int *)context->counter_be != -1 ||
       (((*(int *)(context->counter_be + 4) != -1 || (*(int *)(context->counter_be + 8) != -1)) ||
        (*(int *)(context->counter_be + 0xc) != -1)))))) &&
     (uVar4 = boot_aes128_encrypt_block(plaintext,((uint8_t *)(stack_record_20)),'\x10',&context->aes), uVar4 == 0))
  {
    *output = *input ^ stack_record_20[0];
    output[1] = input[1] ^ stack_record_20[1];
    output[2] = input[2] ^ stack_record_20[2];
    output[3] = input[3] ^ stack_record_20[3];
    output[4] = input[4] ^ stack_record_20[4];
    output[5] = input[5] ^ stack_record_20[5];
    output[6] = input[6] ^ stack_record_20[6];
    output[7] = input[7] ^ stack_record_20[7];
    output[8] = input[8] ^ stack_record_20[8];
    output[9] = input[9] ^ stack_record_20[9];
    output[10] = input[10] ^ stack_record_20[10];
    output[0xb] = input[0xb] ^ stack_record_20[11];
    output[0xc] = input[0xc] ^ stack_record_20[12];
    output[0xd] = input[0xd] ^ stack_record_20[13];
    output[0xe] = input[0xe] ^ stack_record_20[14];
    output[0xf] = input[0xf] ^ stack_record_20[15];
    iVar5 = 3;
    do {
      iVar2 = iVar5 * 4;
      uVar3 = plaintext[iVar2 + 3];
      plaintext[iVar2 + 3] = uVar3 + '\x01';
      if (((uchar)(uVar3 + '\x01') == '\0') &&
         (uVar3 = plaintext[iVar2 + 2], plaintext[iVar2 + 2] = uVar3 + '\x01',
         (uchar)(uVar3 + '\x01') == '\0')) {
        puVar1 = plaintext + iVar2;
        uVar3 = puVar1[1];
        puVar1[1] = uVar3 + '\x01';
        if ((uchar)(uVar3 + '\x01') == '\0') {
          *puVar1 = *puVar1 + '\x01';
        }
      }
      uVar4 = 0;
    } while ((*(int *)(plaintext + iVar5 * 4) == 0) &&
            (iVar2 = iVar5 + -1, iVar5 = iVar5 + -1, -1 < iVar2));
  }
  else {
    uVar4 = 0xff;
  }
  return uVar4;
}

uint boot_aes128_ctr_initialize
               (uchar *key,uchar key_length,uchar *counter,uchar counter_length,
               F33BootAes128CtrContext *context)

{
  uint uVar1;
  
  if ((key_length == '\x10') && (counter_length == '\x10')) {
    context->cleared_extension[0] = '\0';
    context->cleared_extension[1] = '\0';
    context->cleared_extension[2] = '\0';
    context->cleared_extension[3] = '\0';
    context->cleared_extension[4] = '\0';
    context->cleared_extension[5] = '\0';
    context->cleared_extension[6] = '\0';
    context->cleared_extension[7] = '\0';
    context->cleared_extension[8] = '\0';
    context->cleared_extension[9] = '\0';
    context->cleared_extension[10] = '\0';
    context->cleared_extension[0xb] = '\0';
    context->cleared_extension[0xc] = '\0';
    context->cleared_extension[0xd] = '\0';
    context->cleared_extension[0xe] = '\0';
    context->cleared_extension[0xf] = '\0';
    (context->aes).valid = '\0';
    context->counter_be[0] = *counter;
    context->counter_be[1] = counter[1];
    context->counter_be[2] = counter[2];
    context->counter_be[3] = counter[3];
    context->counter_be[4] = counter[4];
    context->counter_be[5] = counter[5];
    context->counter_be[6] = counter[6];
    context->counter_be[7] = counter[7];
    context->counter_be[8] = counter[8];
    context->counter_be[9] = counter[9];
    context->counter_be[10] = counter[10];
    context->counter_be[0xb] = counter[0xb];
    context->counter_be[0xc] = counter[0xc];
    context->counter_be[0xd] = counter[0xd];
    context->counter_be[0xe] = counter[0xe];
    context->counter_be[0xf] = counter[0xf];
    uVar1 = boot_aes128_initialize_context(key,'\x10',&context->aes);
    if (uVar1 == 0) {
      (context->aes).valid = '\x01';
      return 0;
    }
  }
  return 0xff;
}

void boot_aes128_ctr_clear(F33BootAes128CtrContext *context)

{
  (context->aes).valid = '\0';
  zero_words_by_byte_count_76b6(context,0xe4);
  return;
}

uint boot_aes128_cmac_derive_subkeys(F33BootAes128CmacContext *context)

{
  uint8_t stack_record_28[40];
  int iVar1;
  uchar uVar2;
  uchar *puVar3;
  int iVar4;
  uint uVar5;
  bool bVar6;
  uchar *puVar7;
  
  puVar7 = "";
  puVar3 = ((uint8_t *)((stack_record_28 + 16)));
  do {
    uVar2 = *puVar7;
    puVar7 = puVar7 + 1;
    *puVar3 = uVar2;
    puVar3 = puVar3 + 1;
  } while (camry_host_addr(puVar7)!=((uint32_t)(camry_tp + 0xb65u)));
  if (((context->aes).valid == '\x01') &&
     (uVar5 = boot_aes128_encrypt_block(((uint8_t *)((stack_record_28 + 16))),((uint8_t *)(stack_record_28)),'\x10',&context->aes), uVar5 == 0)) {
    puVar7 = context->subkey1;
    bVar6 = false;
    iVar4 = 0xf;
    do {
      puVar7[iVar4] = bVar6 | ((uint8_t *)(stack_record_28))[iVar4] << 1;
      bVar6 = (((uint8_t *)(stack_record_28))[iVar4] & 0x80) != 0;
      iVar1 = iVar4 + -1;
      iVar4 = iVar4 + -1;
    } while (-1 < iVar1);
    if ((char)((uint8_t *)(stack_record_28))[0] < '\0') {
      context->subkey1[0xf] = context->subkey1[0xf] ^ 0x87;
    }
    bVar6 = false;
    iVar4 = 0xf;
    do {
      context->subkey2[iVar4] = bVar6 | puVar7[iVar4] << 1;
      bVar6 = (puVar7[iVar4] & 0x80) != 0;
      iVar1 = iVar4 + -1;
      iVar4 = iVar4 + -1;
    } while (-1 < iVar1);
    if ((*puVar7 & 0x80) != 0) {
      context->subkey2[0xf] = context->subkey2[0xf] ^ 0x87;
    }
    context->subkeys_ready = '\x01';
    uVar5 = 0;
  }
  else {
    uVar5 = 0xff;
  }
  return uVar5;
}

uint boot_aes128_cmac_update_block
               (uchar *input,uchar *output,uchar length,uint final_block,
               F33BootAes128CmacContext *context)

{
  uint8_t stack_record_1c[28];
  uchar *puVar1;
  byte *pbVar2;
  uint uVar3;
  uint uVar4;
  byte bVar5;
  byte *pbVar6;
  byte local_2c [16];
  
  uVar4 = (uint)length;
  if (final_block == 1) {
    if (0xf < uVar4 - 1) {
      return 0xff;
    }
  }
  else if (uVar4 != 0x10) {
    return 0xff;
  }
  if (((context->aes).valid == '\x01') && (context->subkeys_ready == '\x01')) {
    pbVar6 = input;
    if (final_block == 1) {
      uVar3 = 0;
      if (uVar4 == 0x10) {
        do {
          pbVar6 = input + uVar3;
          puVar1 = context->subkey1 + uVar3;
          pbVar2 = local_2c + uVar3;
          uVar3 = uVar3 + 1;
          *pbVar2 = *pbVar6 ^ *puVar1;
          pbVar6 = local_2c;
        } while (uVar3 < 0x10);
      }
      else {
        do {
          if (uVar3 < uVar4) {
            bVar5 = input[uVar3];
          }
          else {
            bVar5 = 0;
            if (uVar3 == uVar4) {
              bVar5 = 0x80;
            }
          }
          pbVar6 = local_2c + uVar3;
          *pbVar6 = bVar5;
          puVar1 = context->subkey2 + uVar3;
          uVar3 = uVar3 + 1;
          *pbVar6 = *puVar1 ^ bVar5;
          pbVar6 = local_2c;
        } while (uVar3 < 0x10);
      }
    }
    stack_record_1c[0] = *pbVar6 ^ context->chain[0];
    stack_record_1c[1] = pbVar6[1] ^ context->chain[1];
    stack_record_1c[2] = pbVar6[2] ^ context->chain[2];
    stack_record_1c[3] = pbVar6[3] ^ context->chain[3];
    stack_record_1c[4] = pbVar6[4] ^ context->chain[4];
    stack_record_1c[5] = pbVar6[5] ^ context->chain[5];
    stack_record_1c[6] = pbVar6[6] ^ context->chain[6];
    stack_record_1c[7] = pbVar6[7] ^ context->chain[7];
    stack_record_1c[8] = pbVar6[8] ^ context->chain[8];
    stack_record_1c[9] = pbVar6[9] ^ context->chain[9];
    stack_record_1c[10] = pbVar6[10] ^ context->chain[10];
    stack_record_1c[11] = pbVar6[0xb] ^ context->chain[0xb];
    stack_record_1c[12] = pbVar6[0xc] ^ context->chain[0xc];
    stack_record_1c[13] = pbVar6[0xd] ^ context->chain[0xd];
    stack_record_1c[14] = pbVar6[0xe] ^ context->chain[0xe];
    stack_record_1c[15] = pbVar6[0xf] ^ context->chain[0xf];
    uVar4 = boot_aes128_encrypt_block(stack_record_1c,output,'\x10',&context->aes);
    if (uVar4 == 0) {
      *(undefined4 *)context->chain = *(undefined4 *)output;
      *(undefined4 *)(context->chain + 4) = *(undefined4 *)(output + 4);
      *(undefined4 *)(context->chain + 8) = *(undefined4 *)(output + 8);
      *(undefined4 *)(context->chain + 0xc) = *(undefined4 *)(output + 0xc);
      return 0;
    }
  }
  return 0xff;
}

uint boot_aes128_cmac_initialize(uchar *key,uchar key_length,F33BootAes128CmacContext *context)

{
  uint uVar1;
  
  if (key_length == '\x10') {
    (context->aes).valid = '\0';
    context->chain[0] = '\0';
    context->chain[1] = '\0';
    context->chain[2] = '\0';
    context->chain[3] = '\0';
    context->chain[4] = '\0';
    context->chain[5] = '\0';
    context->chain[6] = '\0';
    context->chain[7] = '\0';
    context->chain[8] = '\0';
    context->chain[9] = '\0';
    context->chain[10] = '\0';
    context->chain[0xb] = '\0';
    context->chain[0xc] = '\0';
    context->chain[0xd] = '\0';
    context->chain[0xe] = '\0';
    context->chain[0xf] = '\0';
    context->subkey1[0] = '\0';
    context->subkey1[1] = '\0';
    context->subkey1[2] = '\0';
    context->subkey1[3] = '\0';
    context->subkey1[4] = '\0';
    context->subkey1[5] = '\0';
    context->subkey1[6] = '\0';
    context->subkey1[7] = '\0';
    context->subkey1[8] = '\0';
    context->subkey1[9] = '\0';
    context->subkey1[10] = '\0';
    context->subkey1[0xb] = '\0';
    context->subkey1[0xc] = '\0';
    context->subkey1[0xd] = '\0';
    context->subkey1[0xe] = '\0';
    context->subkey1[0xf] = '\0';
    context->subkey2[0] = '\0';
    context->subkey2[1] = '\0';
    context->subkey2[2] = '\0';
    context->subkey2[3] = '\0';
    context->subkey2[4] = '\0';
    context->subkey2[5] = '\0';
    context->subkey2[6] = '\0';
    context->subkey2[7] = '\0';
    context->subkey2[8] = '\0';
    context->subkey2[9] = '\0';
    context->subkey2[10] = '\0';
    context->subkey2[0xb] = '\0';
    context->subkey2[0xc] = '\0';
    context->subkey2[0xd] = '\0';
    context->subkey2[0xe] = '\0';
    context->subkey2[0xf] = '\0';
    context->subkeys_ready = '\0';
    uVar1 = boot_aes128_initialize_context(key,'\x10',&context->aes);
    if (uVar1 == 0) {
      (context->aes).valid = '\x01';
      return 0;
    }
  }
  return 0xff;
}

void boot_aes128_cmac_clear(F33BootAes128CmacContext *context)

{
  (context->aes).valid = '\0';
  zero_words_by_byte_count_76b6(context,0xf8);
  return;
}
