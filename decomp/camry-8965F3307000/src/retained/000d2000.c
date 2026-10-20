#include "common.h"

void lookup_unsigned16_step_table_to_output_d22c0(ushort *param_1,ushort param_2,ushort *param_3)

{
  ushort uVar1;
  int iVar2;
  
  if ((*param_1 == 0xffff) || (param_2 <= *param_1)) {
    uVar1 = param_1[1];
  }
  else {
    iVar2 = 1;
    while( true ) {
      uVar1 = param_1[iVar2 * 2];
      if ((param_2 < uVar1) || (uVar1 == 0xffff)) break;
      iVar2 = iVar2 + 1;
    }
    uVar1 = (param_1 + iVar2 * 2)[-1];
  }
  *param_3 = uVar1;
  return;
}

void store_symmetric_saturated_signed32_product_d2330(int param_1,int param_2,uint *param_3)

{
  int iVar1;
  uint uVar2;
  
  if ((param_1 == 0) || (param_2 == 0)) {
    uVar2 = 0;
    goto LAB_000d2382;
  }
  if (param_1 < 0) {
    if (-1 < param_2) goto LAB_000d2366;
  }
  else if (param_2 < 0) {
LAB_000d2366:
    iVar1 = (int)((ulonglong)((longlong)param_2 * (longlong)param_1) >> 0x20) + 1;
    if ((iVar1 < 0 != (-1 < (longlong)param_2 * (longlong)param_1 && iVar1 < 0)) ||
       (uVar2 = param_1 * param_2, uVar2 < 0x80000001)) {
      uVar2 = 0x80000001;
    }
    goto LAB_000d2382;
  }
  if ((-1 < (longlong)param_2 * (longlong)param_1 &&
       (int)((ulonglong)((longlong)param_2 * (longlong)param_1) >> 0x20) != 0) ||
     (uVar2 = param_1 * param_2, 0x7fffffff < (uint)(param_1 * param_2))) {
    uVar2 = 0x7fffffff;
  }
LAB_000d2382:
  *param_3 = uVar2;
  return;
}

void store_symmetric_saturated_signed16_difference_d2388(short param_1,short param_2,undefined2 *param_3)

{
  undefined2 uVar1;
  int iVar2;
  
  iVar2 = (int)param_1 - (int)param_2;
  if (iVar2 + 0x7fff < 0 == (-1 < iVar2 && iVar2 + 0x7fff < 0) && iVar2 != -0x7fff) {
    if (iVar2 + -0x7fff < 0 == (iVar2 < 0 && -1 < iVar2 + -0x7fff) && iVar2 != 0x7fff) {
      uVar1 = 0x7fff;
    }
    else {
      if (iVar2 + 0x8000 < 0 != (-1 < iVar2 && iVar2 + 0x8000 < 0) || iVar2 == -0x8000) {
        iVar2 = -0x8000;
      }
      uVar1 = (undefined2)iVar2;
    }
  }
  else {
    uVar1 = 0x8001;
  }
  *param_3 = uVar1;
  return;
}

undefined4 read_vote_xor_encoded_u8_triplicate_d23b8(byte *param_1,byte *param_2,byte *param_3,byte *param_4)

{
  byte bVar1;
  undefined4 uVar2;
  byte bVar3;
  byte bVar4;
  
  if ((((camry_host_addr((param_1))== 0) || (camry_host_addr((param_2))== 0)) || (camry_host_addr((param_3))== 0)) ||
     ((camry_host_addr((param_4))== 0|| (camry_host_addr(param_1)==camry_host_addr(param_4))))) {
    uVar2 = 0xffffffff;
  }
  else {
    uVar2 = raise_priority_mask_and_return_previous_d1da0(0xffc0);
    bVar1 = *param_1;
    bVar4 = *param_2;
    bVar3 = *param_3;
    restore_priority_mask_preserving_interrupt_enable_d1dc6(uVar2);
    bVar4 = bVar4 ^ 0x55;
    bVar3 = bVar3 ^ 0xaa;
    if (bVar1 == bVar4) {
      if (bVar1 == bVar3) {
        *param_4 = bVar1;
        return 0;
      }
    }
    else if (bVar1 != bVar3) {
      if (bVar4 == bVar3) {
        uVar2 = 0xfffffff4;
        bVar1 = bVar4;
      }
      else {
        uVar2 = 0xfffffff3;
      }
      *param_4 = bVar1;
      return uVar2;
    }
    *param_4 = bVar1;
    uVar2 = 0xfffffff5;
  }
  return uVar2;
}

undefined4 read_vote_xor_encoded_u16_triplicate_d242e(ushort *param_1,ushort *param_2,ushort *param_3,ushort *param_4)

{
  ushort uVar1;
  undefined4 uVar2;
  ushort uVar3;
  ushort uVar4;
  
  if ((((camry_host_addr((param_1))== 0) || (camry_host_addr((param_2))== 0)) || (camry_host_addr((param_3))== 0)) ||
     ((camry_host_addr((param_4))== 0|| (camry_host_addr(param_1)==camry_host_addr(param_4))))) {
    uVar2 = 0xffffffff;
  }
  else {
    uVar2 = raise_priority_mask_and_return_previous_d1da0(0xffc0);
    uVar1 = *param_1;
    uVar4 = *param_2;
    uVar3 = *param_3;
    restore_priority_mask_preserving_interrupt_enable_d1dc6(uVar2);
    uVar4 = uVar4 ^ 0x5555;
    uVar3 = uVar3 ^ 0xaaaa;
    if (uVar1 == uVar4) {
      if (uVar1 == uVar3) {
        *param_4 = uVar1;
        return 0;
      }
    }
    else if (uVar1 != uVar3) {
      if (uVar4 == uVar3) {
        uVar2 = 0xfffffff4;
        uVar1 = uVar4;
      }
      else {
        uVar2 = 0xfffffff3;
      }
      *param_4 = uVar1;
      return uVar2;
    }
    *param_4 = uVar1;
    uVar2 = 0xfffffff5;
  }
  return uVar2;
}

undefined4 read_vote_xor_encoded_u32_triplicate_d24a4(uint *param_1,uint *param_2,uint *param_3,uint *param_4)

{
  undefined4 uVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  
  if ((((camry_host_addr((param_1))== 0) || (camry_host_addr((param_2))== 0)) || (camry_host_addr((param_3))== 0)) ||
     ((camry_host_addr((param_4))== 0|| (camry_host_addr(param_1)==camry_host_addr(param_4))))) {
    uVar1 = 0xffffffff;
  }
  else {
    uVar1 = raise_priority_mask_and_return_previous_d1da0(0xffc0);
    uVar4 = *param_1;
    uVar3 = *param_2;
    uVar2 = *param_3;
    restore_priority_mask_preserving_interrupt_enable_d1dc6(uVar1);
    uVar3 = uVar3 ^ 0x55555555;
    uVar2 = uVar2 ^ 0xaaaaaaaa;
    if (uVar4 == uVar3) {
      if (uVar4 == uVar2) {
        *param_4 = uVar4;
        return 0;
      }
    }
    else if (uVar4 != uVar2) {
      if (uVar3 == uVar2) {
        uVar1 = 0xfffffff4;
        uVar4 = uVar3;
      }
      else {
        uVar1 = 0xfffffff3;
      }
      *param_4 = uVar4;
      return uVar1;
    }
    *param_4 = uVar4;
    uVar1 = 0xfffffff5;
  }
  return uVar1;
}

undefined4 read_vote_xor_encoded_u8_triplicate_d2522(byte *param_1,byte *param_2,byte *param_3,byte *param_4)

{
  byte bVar1;
  undefined4 uVar2;
  byte bVar3;
  byte bVar4;
  
  if ((((camry_host_addr((param_1))== 0) || (camry_host_addr((param_2))== 0)) || (camry_host_addr((param_3))== 0)) ||
     ((camry_host_addr((param_4))== 0|| (camry_host_addr(param_1)==camry_host_addr(param_4))))) {
    uVar2 = 0xffffffff;
  }
  else {
    uVar2 = raise_priority_mask_and_return_previous_d1da0(0xffc0);
    bVar1 = *param_1;
    bVar4 = *param_2;
    bVar3 = *param_3;
    restore_priority_mask_preserving_interrupt_enable_d1dc6(uVar2);
    bVar4 = bVar4 ^ 0x55;
    bVar3 = bVar3 ^ 0xaa;
    if (bVar1 == bVar4) {
      if (bVar1 == bVar3) {
        *param_4 = bVar1;
        return 0;
      }
    }
    else if (bVar1 != bVar3) {
      if (bVar4 == bVar3) {
        uVar2 = 0xfffffff4;
        bVar1 = bVar4;
      }
      else {
        uVar2 = 0xfffffff3;
      }
      *param_4 = bVar1;
      return uVar2;
    }
    *param_4 = bVar1;
    uVar2 = 0xfffffff5;
  }
  return uVar2;
}

undefined4 read_vote_xor_encoded_u16_triplicate_d2598(ushort *param_1,ushort *param_2,ushort *param_3,ushort *param_4)

{
  ushort uVar1;
  undefined4 uVar2;
  ushort uVar3;
  ushort uVar4;
  
  if ((((camry_host_addr((param_1))== 0) || (camry_host_addr((param_2))== 0)) || (camry_host_addr((param_3))== 0)) ||
     ((camry_host_addr((param_4))== 0|| (camry_host_addr(param_1)==camry_host_addr(param_4))))) {
    uVar2 = 0xffffffff;
  }
  else {
    uVar2 = raise_priority_mask_and_return_previous_d1da0(0xffc0);
    uVar1 = *param_1;
    uVar4 = *param_2;
    uVar3 = *param_3;
    restore_priority_mask_preserving_interrupt_enable_d1dc6(uVar2);
    uVar4 = uVar4 ^ 0x5555;
    uVar3 = uVar3 ^ 0xaaaa;
    if (uVar1 == uVar4) {
      if (uVar1 == uVar3) {
        *param_4 = uVar1;
        return 0;
      }
    }
    else if (uVar1 != uVar3) {
      if (uVar4 == uVar3) {
        uVar2 = 0xfffffff4;
        uVar1 = uVar4;
      }
      else {
        uVar2 = 0xfffffff3;
      }
      *param_4 = uVar1;
      return uVar2;
    }
    *param_4 = uVar1;
    uVar2 = 0xfffffff5;
  }
  return uVar2;
}

undefined4 read_vote_xor_encoded_u32_triplicate_d260e(uint *param_1,uint *param_2,uint *param_3,uint *param_4)

{
  undefined4 uVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  
  if ((((camry_host_addr((param_1))== 0) || (camry_host_addr((param_2))== 0)) || (camry_host_addr((param_3))== 0)) ||
     ((camry_host_addr((param_4))== 0|| (camry_host_addr(param_1)==camry_host_addr(param_4))))) {
    uVar1 = 0xffffffff;
  }
  else {
    uVar1 = raise_priority_mask_and_return_previous_d1da0(0xffc0);
    uVar4 = *param_1;
    uVar3 = *param_2;
    uVar2 = *param_3;
    restore_priority_mask_preserving_interrupt_enable_d1dc6(uVar1);
    uVar3 = uVar3 ^ 0x55555555;
    uVar2 = uVar2 ^ 0xaaaaaaaa;
    if (uVar4 == uVar3) {
      if (uVar4 == uVar2) {
        *param_4 = uVar4;
        return 0;
      }
    }
    else if (uVar4 != uVar2) {
      if (uVar3 == uVar2) {
        uVar1 = 0xfffffff4;
        uVar4 = uVar3;
      }
      else {
        uVar1 = 0xfffffff3;
      }
      *param_4 = uVar4;
      return uVar1;
    }
    *param_4 = uVar4;
    uVar1 = 0xfffffff5;
  }
  return uVar1;
}

undefined4 write_xor_encoded_u8_triplicate_d268c(byte param_1,byte *param_2,byte *param_3,byte *param_4)

{
  undefined4 uVar1;
  
  if (((camry_host_addr((param_2))== 0) || (camry_host_addr((param_3))== 0)) || (camry_host_addr((param_4))== 0)) {
    uVar1 = 0xffffffff;
  }
  else {
    uVar1 = raise_priority_mask_and_return_previous_d1da0(0xffc0);
    *param_2 = param_1;
    *param_3 = param_1 ^ 0x55;
    *param_4 = param_1 ^ 0xaa;
    restore_priority_mask_preserving_interrupt_enable_d1dc6(uVar1);
    uVar1 = 0;
  }
  return uVar1;
}

undefined4 write_xor_encoded_u16_triplicate_d26d0(ushort param_1,ushort *param_2,ushort *param_3,ushort *param_4)

{
  undefined4 uVar1;
  
  if (((camry_host_addr((param_2))== 0) || (camry_host_addr((param_3))== 0)) || (camry_host_addr((param_4))== 0)) {
    uVar1 = 0xffffffff;
  }
  else {
    uVar1 = raise_priority_mask_and_return_previous_d1da0(0xffc0);
    *param_2 = param_1;
    *param_3 = param_1 ^ 0x5555;
    *param_4 = param_1 ^ 0xaaaa;
    restore_priority_mask_preserving_interrupt_enable_d1dc6(uVar1);
    uVar1 = 0;
  }
  return uVar1;
}

undefined4 write_xor_encoded_u32_triplicate_d2714(uint param_1,uint *param_2,uint *param_3,uint *param_4)

{
  undefined4 uVar1;
  
  if (((camry_host_addr((param_2))== 0) || (camry_host_addr((param_3))== 0)) || (camry_host_addr((param_4))== 0)) {
    uVar1 = 0xffffffff;
  }
  else {
    uVar1 = raise_priority_mask_and_return_previous_d1da0(0xffc0);
    *param_2 = param_1;
    *param_3 = param_1 ^ 0x55555555;
    *param_4 = param_1 ^ 0xaaaaaaaa;
    restore_priority_mask_preserving_interrupt_enable_d1dc6(uVar1);
    uVar1 = 0;
  }
  return uVar1;
}

undefined4 write_xor_encoded_u8_triplicate_d2760(byte param_1,byte *param_2,byte *param_3,byte *param_4)

{
  undefined4 uVar1;
  
  if (((camry_host_addr((param_2))== 0) || (camry_host_addr((param_3))== 0)) || (camry_host_addr((param_4))== 0)) {
    uVar1 = 0xffffffff;
  }
  else {
    uVar1 = raise_priority_mask_and_return_previous_d1da0(0xffc0);
    *param_2 = param_1;
    *param_3 = param_1 ^ 0x55;
    *param_4 = param_1 ^ 0xaa;
    restore_priority_mask_preserving_interrupt_enable_d1dc6(uVar1);
    uVar1 = 0;
  }
  return uVar1;
}

undefined4 write_xor_encoded_u16_triplicate_d27a4(ushort param_1,ushort *param_2,ushort *param_3,ushort *param_4)

{
  undefined4 uVar1;
  
  if (((camry_host_addr((param_2))== 0) || (camry_host_addr((param_3))== 0)) || (camry_host_addr((param_4))== 0)) {
    uVar1 = 0xffffffff;
  }
  else {
    uVar1 = raise_priority_mask_and_return_previous_d1da0(0xffc0);
    *param_2 = param_1;
    *param_3 = param_1 ^ 0x5555;
    *param_4 = param_1 ^ 0xaaaa;
    restore_priority_mask_preserving_interrupt_enable_d1dc6(uVar1);
    uVar1 = 0;
  }
  return uVar1;
}

undefined4 write_xor_encoded_u32_triplicate_d27e8(uint param_1,uint *param_2,uint *param_3,uint *param_4)

{
  undefined4 uVar1;
  
  if (((camry_host_addr((param_2))== 0) || (camry_host_addr((param_3))== 0)) || (camry_host_addr((param_4))== 0)) {
    uVar1 = 0xffffffff;
  }
  else {
    uVar1 = raise_priority_mask_and_return_previous_d1da0(0xffc0);
    *param_2 = param_1;
    *param_3 = param_1 ^ 0x55555555;
    *param_4 = param_1 ^ 0xaaaaaaaa;
    restore_priority_mask_preserving_interrupt_enable_d1dc6(uVar1);
    uVar1 = 0;
  }
  return uVar1;
}

undefined8 multiply_two_word_integers_modulo_64_bits_d2834(uint param_1,uint param_2,uint param_3,uint param_4)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  
  uVar6 = param_1 & 0xffff;
  uVar5 = param_3 & 0xffff;
  param_3 = param_3 >> 0x10;
  param_1 = param_1 >> 0x10;
  uVar3 = uVar6 * (param_4 & 0xffff);
  uVar1 = (uVar6 * uVar5 >> 0x10) + (uVar6 * param_3 & 0xffff) + (param_1 * uVar5 & 0xffff);
  uVar4 = (param_2 & 0xffff) * uVar5;
  uVar2 = (uVar6 * param_3 >> 0x10) + (uVar3 & 0xffff) + (param_1 * uVar5 >> 0x10) +
          (param_1 * param_3 & 0xffff) + (uVar4 & 0xffff) + (uVar1 >> 0x10);
  return CONCAT44(((uVar3 >> 0x10) + uVar6 * (param_4 >> 0x10) + (param_1 * param_3 >> 0x10) +
                   param_1 * (param_4 & 0xffff) + (uVar4 >> 0x10) + (param_2 & 0xffff) * param_3 +
                   (param_2 >> 0x10) * uVar5 + (uVar2 >> 0x10)) * 0x10000 | uVar2 & 0xffff,
                  uVar1 * 0x10000 | uVar6 * uVar5 & 0xffff);
}

ulonglong divide_signed_two_word_integers_d28ea(uint param_1,int param_2,uint param_3,int param_4)

{
  bool bVar1;
  uint uVar2;
  uint uVar3;
  ulonglong uVar4;
  
  if (param_2 != 0 || param_4 != 0) {
    bVar1 = param_2 < 0;
    uVar2 = param_1;
    if (bVar1) {
      uVar2 = -param_1;
      param_2 = -(uint)(param_1 != 0) - param_2;
    }
    uVar3 = param_3;
    if (param_4 < 0) {
      uVar3 = -param_3;
      param_4 = -(uint)(param_3 != 0) - param_4;
      bVar1 = !bVar1;
    }
    uVar4 = divide_unsigned_two_word_integers_with_word_fast_path_d2d86(uVar2,param_2,uVar3,param_4);
    if (bVar1) {
      uVar4 = CONCAT44(-(uint)((int)uVar4 != 0) - (int)(uVar4 >> 0x20),-(int)uVar4);
    }
    return uVar4;
  }
  if (param_3 != 0) {
    param_1 = param_1 / param_3;
  }
  return (ulonglong)param_1;
}

uint divide_unsigned_two_word_integers_by_normalized_limbs_d2942(uint param_1,uint param_2,uint param_3,uint param_4)

{
  bool bVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  int iVar6;
  uint uVar7;
  uint uVar8;
  uint uVar9;
  uint uVar10;
  uint uVar11;
  uint uVar12;
  uint uVar13;
  uint uVar14;
  uint uVar15;
  uint uVar16;
  int iVar17;
  
  if (param_3 != 0 || param_4 != 0) {
    uVar8 = 0;
    uVar13 = param_4;
    do {
      if ((int)uVar13 < 0) {
        iVar6 = uVar8 + 1;
        goto code_r0x000d2952;
      }
      uVar13 = uVar13 << 1;
      uVar8 = uVar8 + 1;
    } while (uVar8 < 0x20);
    iVar6 = 0;
code_r0x000d2952:
    if (iVar6 == 0) {
      uVar8 = 0;
      uVar13 = param_3;
      do {
        if ((int)uVar13 < 0) {
          iVar6 = uVar8 + 1;
          goto code_r0x000d2958;
        }
        uVar13 = uVar13 << 1;
        uVar8 = uVar8 + 1;
      } while (uVar8 < 0x20);
      iVar6 = 0;
code_r0x000d2958:
      iVar6 = iVar6 + 0x20;
    }
    uVar13 = iVar6 - 1;
    if ((param_3 - 1 & param_3) == 0 && (param_4 - (param_3 == 0) & param_4) == 0) {
      uVar13 = logical_right_shift_two_word_integer_d2da0(param_1,param_2,0x3f - uVar13);
      return uVar13;
    }
    if (param_2 < param_4 + (param_1 < param_3)) {
      param_1 = 0;
    }
    else if (uVar13 == 0) {
      param_1 = 1;
    }
    else {
      if (iVar6 + -0x21 < 0 == ((int)uVar13 < 0 && -1 < iVar6 + -0x21)) {
        if (param_2 == 0) {
          if (param_3 != 0) {
            param_1 = param_1 / param_3;
          }
          return param_1;
        }
        if (iVar6 + -0x31 < 0 == ((int)uVar13 < 0 && -1 < iVar6 + -0x31)) {
          param_3 = param_3 & 0xffff;
          uVar10 = param_2 >> 0x10;
          uVar8 = param_3 << (0x20 - (-uVar13 + 0x40) & 0x1f);
          if (uVar8 == 0) {
            uVar2 = 1;
          }
          else {
            uVar2 = (int)((ulonglong)
                          (uint)-(int)((ulonglong)(int)uVar8 * (ulonglong)(0x7fffffff - (int)uVar8) >> 0x20) *
                          (ulonglong)(0x7fffffff - (int)uVar8) >> 0x20) << 1;
            uVar2 = (int)((ulonglong)(uint)-(int)((ulonglong)uVar8 * (ulonglong)uVar2 >> 0x20) *
                          (ulonglong)uVar2 >> 0x20) << 1;
            uVar2 = (int)((ulonglong)(uint)-(int)((ulonglong)uVar8 * (ulonglong)uVar2 >> 0x20) *
                          (ulonglong)uVar2 >> 0x20) << 1;
            uVar2 = (int)((ulonglong)(uint)-(int)((ulonglong)uVar8 * (ulonglong)uVar2 >> 0x20) *
                          (ulonglong)uVar2 >> 0x20) * 4 - 3;
            uVar2 = uVar2 - (uVar8 + (int)((ulonglong)uVar8 * (ulonglong)uVar2 >> 0x20));
            uVar2 = uVar2 - (uVar8 + (int)((ulonglong)uVar8 * (ulonglong)uVar2 >> 0x20));
            uVar2 = uVar2 - (uVar8 + (int)((ulonglong)uVar8 * (ulonglong)uVar2 >> 0x20));
          }
          iVar6 = (int)((ulonglong)uVar10 * (ulonglong)uVar2 >> 0x20);
          uVar13 = -uVar13 + 0x3f;
          uVar8 = param_2 & 0xffff |
                  (uVar10 - ((uVar10 - iVar6 >> 1) + iVar6 >> (uVar13 & 0x1f) & 0xffff) * param_3) *
                  0x10000;
          iVar6 = (int)((ulonglong)uVar8 * (ulonglong)uVar2 >> 0x20);
          uVar10 = param_1 >> 0x10 |
                   (uVar8 - ((uVar8 - iVar6 >> 1) + iVar6 >> (uVar13 & 0x1f) & 0xffff) * param_3) *
                   0x10000;
          iVar6 = (int)((ulonglong)uVar10 * (ulonglong)uVar2 >> 0x20);
          uVar8 = (uVar10 - iVar6 >> 1) + iVar6 >> (uVar13 & 0x1f);
          uVar10 = param_1 & 0xffff | (uVar10 - (uVar8 & 0xffff) * param_3) * 0x10000;
          iVar6 = (int)((ulonglong)uVar10 * (ulonglong)uVar2 >> 0x20);
          return (uVar10 - iVar6 >> 1) + iVar6 >> (uVar13 & 0x1f) & 0xffff | uVar8 << 0x10;
        }
      }
      iVar17 = (int)uVar13 >> 4;
      uVar8 = 4 - iVar17;
      if ((uVar13 != 0) && (uVar13 != 0)) {
        if (uVar13 < 0x20) {
          param_4 = param_3 >> (0x20 - uVar13 & 0x1f) | param_4 << (uVar13 & 0x1f);
          param_3 = param_3 << (uVar13 & 0x1f);
        }
        else {
          param_4 = param_3 << (iVar6 - 0x21U & 0x1f);
          param_3 = 0;
        }
      }
      uVar13 = uVar13 & 0xf;
      uVar2 = param_2 >> 0x10;
      uVar10 = (uint)(uVar2 == 0);
      if (uVar2 == 0) {
        if (uVar13 != 0) {
          if (uVar13 < 0x20) {
            param_2 = param_1 >> (0x20 - uVar13 & 0x1f) | param_2 << uVar13;
            param_1 = param_1 << uVar13;
          }
          else {
            param_2 = param_1 << (uVar13 - 0x20 & 0x1f);
            param_1 = 0;
          }
        }
        iVar17 = iVar17 + -1;
        uVar10 = param_2 >> 0x10;
        uVar2 = param_2 & 0xffff;
        uVar7 = 0;
        param_2 = param_1 >> 0x10;
        uVar13 = param_1;
      }
      else {
        if (uVar13 != 0) {
          uVar10 = uVar2 >> (0x10 - uVar13 & 0x1f) & 0xffff;
          if (uVar13 != 0) {
            if (uVar13 < 0x20) {
              param_2 = param_1 >> (0x20 - uVar13 & 0x1f) | param_2 << uVar13;
              param_1 = param_1 << uVar13;
            }
            else {
              param_2 = param_1 << (uVar13 - 0x20 & 0x1f);
              param_1 = 0;
            }
          }
          uVar2 = param_2 >> 0x10;
        }
        uVar13 = param_1 >> 0x10;
        uVar7 = param_1 & 0xffff;
      }
      uVar13 = uVar13 & 0xffff;
      uVar3 = param_4 >> 0x10;
      uVar4 = (uint)((uVar3 - 1 & uVar3) != 0);
      param_4 = param_4 & 0xffff;
      param_1 = 0;
      uVar11 = uVar3 << (0x20 - (uVar4 + 0xf) & 0x1f);
      if (uVar11 == 0) {
        uVar16 = 1;
      }
      else {
        uVar16 = (int)((ulonglong)
                       (uint)-(int)((ulonglong)(int)uVar11 * (ulonglong)(0x7fffffff - (int)uVar11) >> 0x20) *
                       (ulonglong)(0x7fffffff - (int)uVar11) >> 0x20) << 1;
        uVar16 = (int)((ulonglong)(uint)-(int)((ulonglong)uVar11 * (ulonglong)uVar16 >> 0x20) *
                       (ulonglong)uVar16 >> 0x20) << 1;
        uVar16 = (int)((ulonglong)(uint)-(int)((ulonglong)uVar11 * (ulonglong)uVar16 >> 0x20) *
                       (ulonglong)uVar16 >> 0x20) << 1;
        uVar16 = (int)((ulonglong)(uint)-(int)((ulonglong)uVar11 * (ulonglong)uVar16 >> 0x20) *
                       (ulonglong)uVar16 >> 0x20) * 4 - 3;
        uVar16 = uVar16 - (uVar11 + (int)((ulonglong)uVar11 * (ulonglong)uVar16 >> 0x20));
        uVar16 = uVar16 - (uVar11 + (int)((ulonglong)uVar11 * (ulonglong)uVar16 >> 0x20));
        uVar16 = uVar16 - (uVar11 + (int)((ulonglong)uVar11 * (ulonglong)uVar16 >> 0x20));
      }
      uVar15 = uVar8 & 5;
      uVar8 = uVar8 & 4;
      uVar11 = param_2 & 0xffff;
      do {
        if (uVar10 != uVar3) {
          uVar14 = uVar2 | uVar10 << 0x10;
          iVar6 = (int)((ulonglong)uVar14 * (ulonglong)uVar16 >> 0x20);
          uVar12 = (uVar14 - iVar6 >> 1) + iVar6 >> uVar4 + 0xe;
          uVar14 = uVar14 - uVar12 * uVar3;
          goto LAB_000d2c7a;
        }
        uVar12 = 0x10000;
        uVar14 = uVar2;
        do {
          uVar12 = uVar12 - 1;
          uVar14 = uVar14 + uVar3;
          if (0xffff < uVar14) {
            uVar9 = param_4 * uVar12;
            break;
          }
LAB_000d2c7a:
          uVar9 = param_4 * uVar12;
          uVar5 = uVar11 | uVar14 << 0x10;
        } while (uVar5 <= uVar9 && uVar9 - uVar5 != 0);
        uVar14 = 0;
        if (uVar8 != 0) {
          uVar14 = uVar7 - (param_3 & 0xffff) * uVar12;
          uVar7 = uVar14 & 0xffff;
          uVar14 = -(uVar14 >> 0x10) & 0xffff;
        }
        uVar5 = uVar13;
        if (uVar15 != 0) {
          uVar14 = (uVar13 - (param_3 >> 0x10) * uVar12) - uVar14;
          uVar5 = uVar14 & 0xffff;
          uVar14 = -(uVar14 >> 0x10) & 0xffff;
        }
        uVar14 = (uVar11 - uVar9) - uVar14;
        uVar9 = uVar14 & 0xffff;
        uVar13 = (uVar2 - uVar3 * uVar12) - (-(uVar14 >> 0x10) & 0xffff);
        uVar11 = uVar13 & 0xffff;
        uVar2 = uVar10 - (-(uVar13 >> 0x10) & 0xffff);
        uVar13 = uVar7;
        uVar10 = uVar11;
        if ((uVar2 >> 0x10 != 0) && (uVar12 = uVar12 - 1, iVar17 != 0)) {
          if (uVar8 != 0) {
            uVar2 = uVar2 + (param_3 & 0xffff) + uVar7;
            uVar7 = uVar2 & 0xffff;
            uVar2 = uVar2 >> 0x10;
          }
          if (uVar15 != 0) {
            uVar2 = uVar2 + (param_3 >> 0x10) + uVar5;
            uVar5 = uVar2 & 0xffff;
            uVar2 = uVar2 >> 0x10;
          }
          uVar2 = uVar2 + param_4 + uVar9;
          uVar9 = uVar2 & 0xffff;
          uVar10 = (uVar2 >> 0x10) + uVar3 + uVar11 & 0xffff;
          uVar13 = uVar7;
        }
        uVar7 = 0;
        uVar2 = iVar17 * 0x10;
        if (uVar2 != 0) {
          if (uVar2 < 0x20) {
            uVar12 = uVar12 << (uVar2 & 0x1f);
          }
          else {
            uVar12 = 0;
          }
        }
        param_1 = param_1 | uVar12;
        bVar1 = iVar17 != 0;
        uVar11 = uVar5;
        uVar2 = uVar9;
        iVar17 = iVar17 + -1;
      } while (bVar1);
    }
  }
  return param_1;
}

uint divide_unsigned_two_word_integers_with_word_fast_path_d2d86(uint param_1,int param_2,uint param_3,int param_4)

{
  uint uVar1;
  
  if (param_2 == 0) {
    uVar1 = 0;
    if ((param_4 == 0) && (uVar1 = param_1, param_3 != 0)) {
      uVar1 = param_1 / param_3;
    }
    return uVar1;
  }
  uVar1 = divide_unsigned_two_word_integers_by_normalized_limbs_d2942(param_1, param_2, param_3, param_4);
  return uVar1;
}

undefined8 logical_right_shift_two_word_integer_d2da0(uint param_1,uint param_2,uint param_3)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  
  uVar3 = 0;
  uVar2 = 0;
  if (param_3 < 0x40) {
    uVar1 = param_3 - 0x20;
    uVar3 = param_2 >> (uVar1 & 0x1f);
    if ((int)uVar1 < 0) {
      uVar2 = param_2 >> (param_3 & 0x1f);
      uVar3 = (param_2 << (~uVar1 & 0x1f)) << 1 | param_1 >> (param_3 & 0x1f);
    }
  }
  return CONCAT44(uVar2,uVar3);
}
