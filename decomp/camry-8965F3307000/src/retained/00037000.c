#include "common.h"

void return_only_stub_370d4(void)

{
  return;
}

void fill_constant_block_370d6(void)

{
  DAT_febe6c70 = 0;
  DAT_febe6c72 = 0;
  DAT_febe6c74 = 0;
  DAT_febe6c76 = 0;
  DAT_febe6c78 = 0;
  return;
}

void update_clamped_differential_error_accumulator_370e6(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  uint uVar5;
  int iVar6;
  uint uVar7;
  
  if (((DAT_febe8bae != '\0') && (DAT_febe8baf != '\0')) ||
     ((output_request_status & 0x40004) != 0)) {
    DAT_febe6c70 = 0;
    DAT_febe6c72 = 0;
    DAT_febe6c74 = 0;
    DAT_febe6c76 = 0;
    DAT_febe6c78 = 0;
    return;
  }
  iVar3 = (int)((int)(int16_t)DAT_febe6d82) - (int)((int)(int16_t)DAT_febe6d74);
  if (iVar3 + 0x7fff < 0 == (-1 < iVar3 && iVar3 + 0x7fff < 0) && iVar3 != -0x7fff) {
    if (iVar3 + -0x7fff < 0 == (iVar3 < 0 && -1 < iVar3 + -0x7fff) && iVar3 != 0x7fff) {
      iVar6 = 0x7fff;
    }
    else {
      iVar6 = -0x8000;
      if (iVar3 + 0x8000 < 0 == (-1 < iVar3 && iVar3 + 0x8000 < 0)) {
        iVar6 = (int)(short)iVar3;
      }
    }
  }
  else {
    iVar6 = -0x7fff;
  }
  if (((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe6be8u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, first_saturation))))) == '\x01') ||
       ((*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6be8u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, first_saturation))))) == '\x02')) && (-1 < iVar6)) ||
     ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe6be8u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, first_saturation))))) == '\x02' ||
       ((*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6be8u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, first_saturation))))) == '\x01')) && (iVar6 < 0)))) {
    DAT_febe6c70 = 1;
    iVar3 = 0;
  }
  else {
    DAT_febe6c70 = 0;
    iVar3 = iVar6;
  }
  uVar4 = (uint)DAT_00031a30;
  if (DAT_febe6d16 <= uVar4) {
    uVar4 = (uint)DAT_febe6d16;
  }
  uVar5 = (uint)DAT_00031a32;
  if (uVar5 <= uVar4) {
    uVar5 = uVar4;
  }
  uVar4 = DAT_00031a34;
  if (DAT_febe6d58 <= DAT_00031a34) {
    uVar4 = DAT_febe6d58;
  }
  uVar7 = DAT_00031a38;
  if (DAT_00031a38 <= uVar4) {
    uVar7 = uVar4;
  }
  iVar1 = uVar5 * (iVar6 - ((int)(int16_t)DAT_febe6c72)) + (int)((uVar7 >> 9) * (((int)(int16_t)DAT_febe6c74) + iVar3)) / 0x40;
  if (iVar1 < 1) {
    if ((((int)(int32_t)DAT_febe6c78) < 1) &&
       (iVar2 = -0x7fffffff - iVar1,
       iVar2 - ((int)(int32_t)DAT_febe6c78) < 0 ==
       (iVar2 < 0 != ((int)(int32_t)DAT_febe6c78) < 0 && ((int)(int32_t)DAT_febe6c78) < 0 == iVar2 - ((int)(int32_t)DAT_febe6c78) < 0) &&
       iVar2 != ((int)(int32_t)DAT_febe6c78))) {
      iVar1 = -0x7fffffff;
      goto LAB_000371f4;
    }
  }
  else if ((0 < ((int)(int32_t)DAT_febe6c78)) &&
          (iVar2 = (0x7fffffff - iVar1) - ((int)(int32_t)DAT_febe6c78),
          iVar2 < 0 != (0x7fffffff - iVar1 < 0 != (int)DAT_febe6c78 < 0 && (int)DAT_febe6c78 < 0 == iVar2 < 0)
          )) {
    iVar1 = 0x7fffffff;
    goto LAB_000371f4;
  }
  iVar1 = iVar1 + ((int)(int32_t)DAT_febe6c78);
LAB_000371f4:
  iVar2 = DAT_00031a3c;
  if (iVar1 - DAT_00031a3c < 0 !=
      (iVar1 < 0 != DAT_00031a3c < 0 && DAT_00031a3c < 0 == iVar1 - DAT_00031a3c < 0) ||
      iVar1 == DAT_00031a3c) {
    iVar2 = iVar1;
  }
  DAT_febe6c78 = -DAT_00031a3c;
  if (iVar2 + DAT_00031a3c < 0 ==
      (iVar2 < 0 != ((int)(int32_t)DAT_febe6c78) < 0 && ((int)(int32_t)DAT_febe6c78) < 0 == iVar2 + DAT_00031a3c < 0)) {
    DAT_febe6c78 = iVar2;
  }
  DAT_febe6c72 = (short)iVar6;
  DAT_febe6c74 = (short)iVar3;
  DAT_febe6c76 = (short)iVar6;
  return;
}

void return_only_stub_37216(void)

{
  return;
}

void fill_constant_block_37218(void)

{
  DAT_febe6c7c = 0;
  DAT_febe6c7e = 0;
  DAT_febe6c80 = 0;
  DAT_febe6c82 = 0;
  DAT_febe6c8c = 0;
  return;
}

void update_coupled_common_error_accumulator_37228(void)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  uint uVar9;
  
  if (((DAT_febe8bae != '\0') && (DAT_febe8baf != '\0')) ||
     ((output_request_status & 0x40004) != 0)) {
    DAT_febe6c7c = 0;
    DAT_febe6c7e = 0;
    DAT_febe6c80 = 0;
    DAT_febe6c82 = 0;
    DAT_febe6c8c = 0;
    return;
  }
  iVar7 = (int)((int)(int16_t)DAT_febe6d80) - (int)((int)(int16_t)DAT_febe6d70);
  if (iVar7 + 0x7fff < 0 == (-1 < iVar7 && iVar7 + 0x7fff < 0) && iVar7 != -0x7fff) {
    if (iVar7 + -0x7fff < 0 == (iVar7 < 0 && -1 < iVar7 + -0x7fff) && iVar7 != 0x7fff) {
      iVar8 = 0x7fff;
    }
    else {
      iVar8 = -0x8000;
      if (iVar7 + 0x8000 < 0 == (-1 < iVar7 && iVar7 + 0x8000 < 0)) {
        iVar8 = (int)(short)iVar7;
      }
    }
  }
  else {
    iVar8 = -0x7fff;
  }
  if (((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe6be8u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, first_saturation))))) == '\x01') ||
       ((*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6be8u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, first_saturation))))) == '\x01')) && (-1 < iVar8)) ||
     ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe6be8u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, first_saturation))))) == '\x02' ||
       ((*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6be8u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, first_saturation))))) == '\x02')) && (iVar8 < 0)))) {
    DAT_febe6c7c = 1;
    iVar7 = 0;
  }
  else {
    DAT_febe6c7c = 0;
    iVar7 = iVar8;
  }
  uVar2 = (uint)DAT_00031a40;
  if (DAT_febe6d06 <= uVar2) {
    uVar2 = (uint)DAT_febe6d06;
  }
  uVar3 = (uint)DAT_00031a42;
  if (uVar3 <= uVar2) {
    uVar3 = uVar2;
  }
  uVar2 = DAT_00031a44;
  if (DAT_febe6d40 <= DAT_00031a44) {
    uVar2 = DAT_febe6d40;
  }
  uVar9 = DAT_00031a48;
  if (DAT_00031a48 <= uVar2) {
    uVar9 = uVar2;
  }
  iVar6 = 0x7fffffff;
  iVar5 = -0x7fffffff;
  iVar4 = iVar6;
  if (((DAT_febe71ec & 1) == 0) || (DAT_febe6c84 != 0)) {
    if (((DAT_febe71ec >> 1 & 1) != 0) && (DAT_febe6c84 == 0)) {
      if (((int)(int32_t)DAT_febe6c8c) < 1) {
        if ((0 < ((int)(int32_t)DAT_febe6c78)) ||
           (iVar1 = -0x7fffffff - ((int)(int32_t)DAT_febe6c8c), iVar4 = iVar5,
           iVar1 - ((int)(int32_t)DAT_febe6c78) < 0 !=
           (iVar1 < 0 != ((int)(int32_t)DAT_febe6c78) < 0 && ((int)(int32_t)DAT_febe6c78) < 0 == iVar1 - ((int)(int32_t)DAT_febe6c78) < 0) ||
           iVar1 == ((int)(int32_t)DAT_febe6c78))) goto LAB_00037360;
      }
      else if ((((int)(int32_t)DAT_febe6c78) < 1) ||
              (iVar1 = (0x7fffffff - ((int)(int32_t)DAT_febe6c8c)) - ((int)(int32_t)DAT_febe6c78),
              iVar1 < 0 ==
              (0x7fffffff - (int)DAT_febe6c8c < 0 != (int)DAT_febe6c78 < 0 && (int)DAT_febe6c78 < 0 == iVar1 < 0)))
      {
LAB_00037360:
        iVar4 = ((int)(int32_t)DAT_febe6c78) + ((int)(int32_t)DAT_febe6c8c);
      }
      goto LAB_00037364;
    }
  }
  else {
    if (((int)(int32_t)DAT_febe6c8c) < 0) {
      if ((((int)(int32_t)DAT_febe6c78) < 0) ||
         (iVar1 = (((int)(int32_t)DAT_febe6c8c) + 0x7fffffff) - ((int)(int32_t)DAT_febe6c78), iVar4 = iVar5,
         iVar1 < 0 ==
         ((int)DAT_febe6c8c + 0x7fffffff < 0 != (int)DAT_febe6c78 < 0 && (int)DAT_febe6c78 < 0 == iVar1 < 0)))
      goto LAB_0003732e;
    }
    else if ((-1 < ((int)(int32_t)DAT_febe6c78)) ||
            (iVar1 = -(0x7fffffff - ((int)(int32_t)DAT_febe6c8c)),
            iVar1 - ((int)(int32_t)DAT_febe6c78) < 0 !=
            (iVar1 < 0 != ((int)(int32_t)DAT_febe6c78) < 0 && ((int)(int32_t)DAT_febe6c78) < 0 == iVar1 - ((int)(int32_t)DAT_febe6c78) < 0) ||
            iVar1 == ((int)(int32_t)DAT_febe6c78))) {
LAB_0003732e:
      iVar4 = ((int)(int32_t)DAT_febe6c8c) - ((int)(int32_t)DAT_febe6c78);
    }
LAB_00037364:
    DAT_febe6c8c = iVar4 / 2;
  }
  iVar4 = uVar3 * (iVar8 - ((int)(int16_t)DAT_febe6c7e)) + (int)((uVar9 >> 9) * (((int)(int16_t)DAT_febe6c80) + iVar7)) / 0x40;
  if (iVar4 < 1) {
    if ((((int)(int32_t)DAT_febe6c8c) < 1) &&
       (iVar1 = -0x7fffffff - iVar4, iVar6 = iVar5,
       iVar1 - ((int)(int32_t)DAT_febe6c8c) < 0 ==
       (iVar1 < 0 != ((int)(int32_t)DAT_febe6c8c) < 0 && ((int)(int32_t)DAT_febe6c8c) < 0 == iVar1 - ((int)(int32_t)DAT_febe6c8c) < 0) &&
       iVar1 != ((int)(int32_t)DAT_febe6c8c))) goto LAB_000373b0;
  }
  else if ((0 < ((int)(int32_t)DAT_febe6c8c)) &&
          (iVar5 = (0x7fffffff - iVar4) - ((int)(int32_t)DAT_febe6c8c),
          iVar5 < 0 != (0x7fffffff - iVar4 < 0 != (int)DAT_febe6c8c < 0 && (int)DAT_febe6c8c < 0 == iVar5 < 0)
          )) goto LAB_000373b0;
  iVar6 = iVar4 + ((int)(int32_t)DAT_febe6c8c);
LAB_000373b0:
  DAT_febe6c88 = ((int)(int32_t)DAT_febe6c8c);
  DAT_febe6c84 = DAT_febe71ec;
  DAT_febe6c82 = (short)iVar8;
  DAT_febe6c80 = (short)iVar7;
  DAT_febe6c8c = iVar6;
  DAT_febe6c7e = DAT_febe6c82;
  return;
}

void return_only_stub_373bc(void)

{
  return;
}

void fill_constant_block_373be(void)

{
  DAT_febe6c90 = 0;
  DAT_febe6c92 = 0;
  DAT_febe6c94 = 0;
  DAT_febe6c9c = DAT_febe6d14;
  DAT_febe6c96 = 0;
  DAT_febe6ca0 = 0;
  DAT_febe6cb4 = 0;
  DAT_febe6c98 = 0;
  DAT_febe6c9a = 0;
  DAT_febe6ca8 = 0;
  DAT_febe6cb0 = 0;
  DAT_febe6cac = 0;
  DAT_febe6ca4 = DAT_febe6d54;
  return;
}

int subtract_6d76_from_6d7e_saturating_s16_373e6(void)

{
  int iVar1;
  int iVar2;
  
  iVar1 = (int)((int)(int16_t)DAT_febe6d7e) - (int)((int)(int16_t)DAT_febe6d76);
  if (iVar1 + 0x7fff < 0 == (-1 < iVar1 && iVar1 + 0x7fff < 0) && iVar1 != -0x7fff) {
    if (iVar1 + -0x7fff < 0 == (iVar1 < 0 && -1 < iVar1 + -0x7fff) && iVar1 != 0x7fff) {
      iVar2 = 0x7fff;
    }
    else {
      iVar2 = -0x8000;
      if (iVar1 + 0x8000 < 0 == (-1 < iVar1 && iVar1 + 0x8000 < 0)) {
        iVar2 = (int)(short)iVar1;
      }
    }
    return iVar2;
  }
  return -0x7fff;
}

uint detect_opposed_second_envelope_saturation_37418(short param_1)

{
  uint uVar1;
  
  if (((((*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebe6be8u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, second))))) < 0) ||
       ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe6be8u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, second_saturation))))) != '\x01')) &&
      ((-1 < (*((volatile int16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6be8u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, second))))) ||
       ((*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6be8u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, second_saturation))))) != '\x02')))) || (param_1 < 0)) {
    if ((((*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebe6be8u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, second))))) < 0) &&
        ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe6be8u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, second_saturation))))) == '\x02')) ||
       ((-1 < (*((volatile int16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6be8u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, second))))) &&
        ((*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6be8u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, second_saturation))))) == '\x01')))) {
      uVar1 = (uint)(int)param_1 >> 0x1f;
    }
    else {
      uVar1 = 0;
    }
  }
  else {
    uVar1 = 1;
  }
  DAT_febe6c90 = (char)uVar1;
  return uVar1;
}

void update_6ca0_clamped_error_accumulator_37460(short param_1,char param_2)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  int iVar4;
  int iVar5;
  int limit;
  uint uVar6;
  
  DAT_febe6ca4 = DAT_febe6d54;
  DAT_febe6c9c = DAT_febe6d14;
  uVar2 = (uint)DAT_00031a4c;
  iVar5 = (int)param_1;
  if (param_2 == '\x01') {
    iVar5 = 0;
  }
  if (DAT_febe6d14 < uVar2) {
    uVar2 = (uint)DAT_febe6d14;
  }
  uVar3 = (uint)DAT_00031a4e;
  if (uVar3 <= uVar2) {
    uVar3 = uVar2;
  }
  uVar2 = DAT_00031a50;
  if (DAT_febe6d54 < DAT_00031a50) {
    uVar2 = DAT_febe6d54;
  }
  uVar6 = DAT_00031a54;
  if (DAT_00031a54 <= uVar2) {
    uVar6 = uVar2;
  }
  limit = (int)DAT_00031a58;
  iVar4 = limit;
  if ((int)DAT_febe6ca0 - limit < 0 !=
      ((int)DAT_febe6ca0 < 0 != limit < 0 && limit < 0 == (int)DAT_febe6ca0 - limit < 0))
  {
    iVar4 = (int)DAT_febe6ca0;
  }
  DAT_febe6ca0 = -limit;
  DAT_febe6ca8 = ((int)(int32_t)DAT_febe6ca0);
  if (iVar4 + limit < 0 ==
      (iVar4 < 0 != (int)DAT_febe6ca0 < 0 && (int)DAT_febe6ca0 < 0 == iVar4 + limit < 0)) {
    DAT_febe6ca8 = iVar4;
  }
  DAT_febe6cac = (uVar6 >> 9) * (((int)(int16_t)DAT_febe6c94) + iVar5);
  DAT_febe6cb0 = uVar3 * ((int)param_1 - (int)((int)(int16_t)DAT_febe6c92));
  iVar4 = (int)DAT_febe6cac / 0x40 + (int)DAT_febe6cb0;
  if (iVar4 < 1) {
    if ((((int)(int32_t)DAT_febe6ca8) < 1) &&
       (iVar1 = -0x7fffffff - iVar4,
       iVar1 - ((int)(int32_t)DAT_febe6ca8) < 0 ==
       (iVar1 < 0 != ((int)(int32_t)DAT_febe6ca8) < 0 && ((int)(int32_t)DAT_febe6ca8) < 0 == iVar1 - ((int)(int32_t)DAT_febe6ca8) < 0) &&
       iVar1 != ((int)(int32_t)DAT_febe6ca8))) {
      DAT_febe6cb4 = -0x7fffffff;
      goto LAB_00037512;
    }
  }
  else if ((0 < ((int)(int32_t)DAT_febe6ca8)) &&
          (iVar1 = (0x7fffffff - iVar4) - ((int)(int32_t)DAT_febe6ca8),
          iVar1 < 0 != (0x7fffffff - iVar4 < 0 != (int)DAT_febe6ca8 < 0 && (int)DAT_febe6ca8 < 0 == iVar1 < 0)
          )) {
    DAT_febe6cb4 = 0x7fffffff;
    goto LAB_00037512;
  }
  DAT_febe6cb4 = ((int)(int32_t)DAT_febe6ca8) + iVar4;
LAB_00037512:
  DAT_febe6c98 = ((int)(int16_t)DAT_febe6c92);
  limit = (int)DAT_00031a58;
  iVar4 = limit;
  if ((int)DAT_febe6cb4 - limit < 0 !=
      ((int)DAT_febe6cb4 < 0 != limit < 0 && limit < 0 == (int)DAT_febe6cb4 - limit < 0))
  {
    iVar4 = (int)DAT_febe6cb4;
  }
  DAT_febe6c9a = ((int)(int16_t)DAT_febe6c94);
  DAT_febe6c92 = param_1;
  if (iVar4 + limit < 0 ==
      (iVar4 < 0 != (int)DAT_febe6ca0 < 0 && (int)DAT_febe6ca0 < 0 == iVar4 + limit < 0)) {
    DAT_febe6ca0 = iVar4;
  }
  DAT_febe6c94 = (short)iVar5;
  DAT_febe6c96 = param_1;
  return;
}

void run_or_reset_6ca0_error_accumulator_37538(void)

{
  undefined4 uVar1;
  undefined4 uVar2;
  
  if (((DAT_febe8bae == '\0') || (DAT_febe8baf == '\0')) &&
     ((output_request_status & 0x40004) == 0)) {
    uVar1 = subtract_6d76_from_6d7e_saturating_s16_373e6();
    uVar2 = detect_opposed_second_envelope_saturation_37418(uVar1);
    update_6ca0_clamped_error_accumulator_37460(uVar1,uVar2);
  }
  else {
    DAT_febe6c90 = 0;
    DAT_febe6c92 = 0;
    DAT_febe6c94 = 0;
    DAT_febe6c9c = DAT_febe6d14;
    DAT_febe6c96 = 0;
    DAT_febe6ca0 = 0;
    DAT_febe6cb4 = 0;
    DAT_febe6c98 = 0;
    DAT_febe6c9a = 0;
    DAT_febe6ca8 = 0;
    DAT_febe6cb0 = 0;
    DAT_febe6cac = 0;
    DAT_febe6ca4 = DAT_febe6d54;
  }
  return;
}

void return_only_stub_3759a(void)

{
  return;
}

void fill_constant_block_3759c(void)

{
  DAT_febe6cb8 = 0;
  DAT_febe6cba = 0;
  DAT_febe6cbc = 0;
  DAT_febe6cc4 = DAT_febe6d04;
  DAT_febe6cbe = 0;
  DAT_febe6ccc = 0;
  DAT_febe6cc0 = 0;
  DAT_febe6cc2 = 0;
  DAT_febe6cd4 = 0;
  DAT_febe6cdc = 0;
  DAT_febe6cd8 = 0;
  DAT_febe6cd0 = DAT_febe6d3c;
  return;
}

int subtract_6d78_from_6d7c_saturating_s16_375c2(void)

{
  int iVar1;
  
  iVar1 = ((int)(int16_t)DAT_febe6d7c) - DAT_febe6d78;
  if (iVar1 + -0x7fff < 0 == (iVar1 < 0 && -1 < iVar1 + -0x7fff)) {
    iVar1 = 0x7fff;
  }
  if (iVar1 + 0x7fff < 0 != (-1 < iVar1 && iVar1 + 0x7fff < 0)) {
    iVar1 = -0x7fff;
  }
  return (int)(short)iVar1;
}

uint detect_same_direction_second_envelope_saturation_375e6(short param_1)

{
  uint uVar1;
  
  if (((((*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebe6be8u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, second))))) < 0) ||
       ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe6be8u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, second_saturation))))) != '\x01')) &&
      (((*((volatile int16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6be8u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, second))))) < 0 ||
       ((*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6be8u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, second_saturation))))) != '\x01')))) || (param_1 < 0)) {
    if ((((*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebe6be8u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, second))))) < 0) &&
        ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe6be8u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, second_saturation))))) == '\x02')) ||
       (((*((volatile int16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6be8u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, second))))) < 0 &&
        ((*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6be8u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, second_saturation))))) == '\x02')))) {
      uVar1 = (uint)(int)param_1 >> 0x1f;
    }
    else {
      uVar1 = 0;
    }
  }
  else {
    uVar1 = 1;
  }
  DAT_febe6cb8 = (char)uVar1;
  return uVar1;
}

void update_6ccc_coupled_clamped_error_accumulator_3762e(short param_1,char param_2)

{
  uint uVar1;
  uint uVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int limit;
  uint uVar6;
  
  iVar5 = (int)param_1;
  if (param_2 == '\x01') {
    iVar5 = 0;
  }
  DAT_febe6cc4 = DAT_febe6d04;
  DAT_febe6cd0 = DAT_febe6d3c;
  uVar1 = (uint)DAT_00031a5c;
  if (DAT_febe6d04 < uVar1) {
    uVar1 = (uint)DAT_febe6d04;
  }
  uVar2 = (uint)DAT_00031a5e;
  if (uVar2 <= uVar1) {
    uVar2 = uVar1;
  }
  uVar1 = DAT_00031a60;
  if (DAT_febe6d3c < DAT_00031a60) {
    uVar1 = DAT_febe6d3c;
  }
  uVar6 = DAT_00031a64;
  if (DAT_00031a64 <= uVar1) {
    uVar6 = uVar1;
  }
  limit = (int)DAT_00031a68;
  iVar4 = limit;
  if ((int)DAT_febe6ccc - limit < 0 !=
      ((int)DAT_febe6ccc < 0 != limit < 0 && limit < 0 == (int)DAT_febe6ccc - limit < 0))
  {
    iVar4 = (int)DAT_febe6ccc;
  }
  DAT_febe6ccc = -limit;
  DAT_febe6cc8 = ((int)(int32_t)DAT_febe6ccc);
  if (iVar4 + limit < 0 ==
      (iVar4 < 0 != (int)DAT_febe6ccc < 0 && (int)DAT_febe6ccc < 0 == iVar4 + limit < 0)) {
    DAT_febe6cc8 = iVar4;
  }
  iVar4 = 0x7fffffff;
  if (((DAT_febe71ec & 1) == 0) || (DAT_febe6cc6 != 0)) {
    if (((DAT_febe71ec >> 1 & 1) != 0) && (DAT_febe6cc6 == 0)) {
      if (((int)(int32_t)DAT_febe6cc8) < 1) {
        if ((0 < ((int)(int32_t)DAT_febe6ca0)) ||
           (iVar4 = -0x7fffffff - ((int)(int32_t)DAT_febe6cc8),
           iVar4 - ((int)(int32_t)DAT_febe6ca0) < 0 !=
           (iVar4 < 0 != ((int)(int32_t)DAT_febe6ca0) < 0 && ((int)(int32_t)DAT_febe6ca0) < 0 == iVar4 - ((int)(int32_t)DAT_febe6ca0) < 0) ||
           iVar4 == ((int)(int32_t)DAT_febe6ca0))) goto LAB_00037704;
        iVar4 = -0x7fffffff;
      }
      else if ((((int)(int32_t)DAT_febe6ca0) < 1) ||
              (iVar3 = (0x7fffffff - ((int)(int32_t)DAT_febe6cc8)) - ((int)(int32_t)DAT_febe6ca0),
              iVar3 < 0 ==
              (0x7fffffff - (int)DAT_febe6cc8 < 0 != (int)DAT_febe6ca0 < 0 && (int)DAT_febe6ca0 < 0 == iVar3 < 0)))
      {
LAB_00037704:
        iVar4 = ((int)(int32_t)DAT_febe6ca0) + ((int)(int32_t)DAT_febe6cc8);
      }
      goto LAB_00037708;
    }
  }
  else {
    if (((int)(int32_t)DAT_febe6cc8) < 0) {
      if ((((int)(int32_t)DAT_febe6ca0) < 0) ||
         (iVar4 = (((int)(int32_t)DAT_febe6cc8) + 0x7fffffff) - ((int)(int32_t)DAT_febe6ca0),
         iVar4 < 0 ==
         ((int)DAT_febe6cc8 + 0x7fffffff < 0 != (int)DAT_febe6ca0 < 0 && (int)DAT_febe6ca0 < 0 == iVar4 < 0)))
      goto LAB_000376d2;
      iVar4 = -0x7fffffff;
    }
    else if ((-1 < ((int)(int32_t)DAT_febe6ca0)) ||
            (iVar3 = -(0x7fffffff - ((int)(int32_t)DAT_febe6cc8)),
            iVar3 - ((int)(int32_t)DAT_febe6ca0) < 0 !=
            (iVar3 < 0 != ((int)(int32_t)DAT_febe6ca0) < 0 && ((int)(int32_t)DAT_febe6ca0) < 0 == iVar3 - ((int)(int32_t)DAT_febe6ca0) < 0) ||
            iVar3 == ((int)(int32_t)DAT_febe6ca0))) {
LAB_000376d2:
      iVar4 = ((int)(int32_t)DAT_febe6cc8) - ((int)(int32_t)DAT_febe6ca0);
    }
LAB_00037708:
    DAT_febe6cc8 = iVar4 / 2;
  }
  DAT_febe6cd8 = (uVar6 >> 9) * (((int)(int16_t)DAT_febe6cbc) + iVar5);
  DAT_febe6cc6 = DAT_febe71ec;
  DAT_febe6cdc = uVar2 * ((int)param_1 - (int)((int)(int16_t)DAT_febe6cba));
  iVar4 = (int)DAT_febe6cd8 / 0x40 + (int)DAT_febe6cdc;
  if (iVar4 < 1) {
    if ((((int)(int32_t)DAT_febe6cc8) < 1) &&
       (iVar3 = -0x7fffffff - iVar4,
       iVar3 - ((int)(int32_t)DAT_febe6cc8) < 0 ==
       (iVar3 < 0 != ((int)(int32_t)DAT_febe6cc8) < 0 && ((int)(int32_t)DAT_febe6cc8) < 0 == iVar3 - ((int)(int32_t)DAT_febe6cc8) < 0) &&
       iVar3 != ((int)(int32_t)DAT_febe6cc8))) {
      iVar4 = -0x7fffffff;
      goto LAB_0003775e;
    }
  }
  else if ((0 < ((int)(int32_t)DAT_febe6cc8)) &&
          (iVar3 = (0x7fffffff - iVar4) - ((int)(int32_t)DAT_febe6cc8),
          iVar3 < 0 != (0x7fffffff - iVar4 < 0 != (int)DAT_febe6cc8 < 0 && (int)DAT_febe6cc8 < 0 == iVar3 < 0)
          )) {
    iVar4 = 0x7fffffff;
    goto LAB_0003775e;
  }
  iVar4 = ((int)(int32_t)DAT_febe6cc8) + iVar4;
LAB_0003775e:
  DAT_febe6cd4 = ((int)(int32_t)DAT_febe6cc8);
  DAT_febe6cc0 = ((int)(int16_t)DAT_febe6cba);
  limit = (int)DAT_00031a68;
  iVar3 = limit;
  if (iVar4 - limit < 0 !=
      (iVar4 < 0 != limit < 0 && limit < 0 == iVar4 - limit < 0)) {
    iVar3 = iVar4;
  }
  DAT_febe6cc2 = ((int)(int16_t)DAT_febe6cbc);
  DAT_febe6cba = param_1;
  if (iVar3 + limit < 0 ==
      (iVar3 < 0 != (int)DAT_febe6ccc < 0 && (int)DAT_febe6ccc < 0 == iVar3 + limit < 0)) {
    DAT_febe6ccc = iVar3;
  }
  DAT_febe6cbc = (short)iVar5;
  DAT_febe6cbe = param_1;
  return;
}

void run_or_reset_6ccc_error_accumulator_3777e(void)

{
  undefined4 uVar1;
  undefined4 uVar2;
  
  if (((DAT_febe8bae == '\0') || (DAT_febe8baf == '\0')) &&
     ((output_request_status & 0x40004) == 0)) {
    uVar1 = subtract_6d78_from_6d7c_saturating_s16_375c2();
    uVar2 = detect_same_direction_second_envelope_saturation_375e6(uVar1);
    update_6ccc_coupled_clamped_error_accumulator_3762e(uVar1,uVar2);
  }
  else {
    DAT_febe6cb8 = 0;
    DAT_febe6cba = 0;
    DAT_febe6cbc = 0;
    DAT_febe6cc4 = DAT_febe6d04;
    DAT_febe6cbe = 0;
    DAT_febe6ccc = 0;
    DAT_febe6cc0 = 0;
    DAT_febe6cc2 = 0;
    DAT_febe6cd4 = 0;
    DAT_febe6cdc = 0;
    DAT_febe6cd8 = 0;
    DAT_febe6cd0 = DAT_febe6d3c;
  }
  return;
}

void initialize_shared_second_axis_envelope(void)

{
  shared_second_axis_envelope = DAT_000317ac;
  return;
}

void return_only_stub_377ec(void)

{
  return;
}

void map_additional_second_axis_envelope(short magnitude)

{
  uint32_t puVar1;
  undefined2 uStack_6;
  
  puVar1 = 0xfebeb800u;
  if ((DAT_febee741 == '\x11') || (DAT_febee741 == '\"')) {
    puVar1 = 0xfebeb800u;
    interpolate_s16_axis_s16_values_70208(((short *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x31eacu + (uint32_t)(DAT_febee5c3 & 1) * 4u))))))), (int)magnitude, &uStack_6);
  }
  else {
    uStack_6 = (*((undefined2 *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x31ea4u + (uint32_t)(DAT_febee5c3 & 1) * 4u)))) + 2))));
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb4e2u + (uint32_t)((int)puVar1)))))) = uStack_6;
  return;
}

void refresh_shared_second_axis_envelope(void)

{
  short sVar1;
  byte bVar2;
  short sVar3;
  int iVar4;
  uint32_t puVar5;
  int iVar6;
  
  puVar5 = 0xfebeb800u;
  if (DAT_febe8a20 == '\x01') {
    if (((int)(int32_t)(int)DAT_febee744) + -0x7fff < 0 == (((int)(int32_t)(int)DAT_febee744) < 0 && -1 < ((int)(int32_t)(int)DAT_febee744) + -0x7fff) &&
        ((int)(int32_t)DAT_febee744) != 0x7fff) {
      DAT_febe6ce0 = 0x7fff;
    }
    else {
      iVar4 = ((int)(int32_t)DAT_febee744);
      if (((int)(int32_t)(int)DAT_febee744) + 0x7fff < 0 != (-1 < ((int)(int32_t)(int)DAT_febee744) && ((int)(int32_t)(int)DAT_febee744) + 0x7fff < 0)) {
        iVar4 = -0x7fff;
      }
      DAT_febe6ce0 = (short)iVar4;
      iVar4 = (int)DAT_febe6ce0;
      if (iVar4 + 0x7fff < 0 == (-1 < iVar4 && iVar4 + 0x7fff < 0) && iVar4 != -0x7fff) {
        if (DAT_febe6ce0 < 0) {
          DAT_febe6ce0 = -DAT_febe6ce0;
        }
      }
      else {
        DAT_febe6ce0 = 0x7fff;
      }
    }
    map_additional_second_axis_envelope(DAT_febe6ce0);
    sVar1 = DAT_000317ac;
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb6a8u + (uint32_t)((int)puVar5) * 1u)))) == 'Z') {
      sVar1 = (*((short *)camry_host_ptr((uint32_t)((0xffffb4e2u + (uint32_t)((int)puVar5))))));
    }
    iVar4 = (int)sVar1;
    bVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(0x2dc3)))));
    (*((int *)camry_host_ptr((uint32_t)((0xffffb4e8u + (uint32_t)((int)puVar5)))))) = iVar4;
    sVar3 = (*((short *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x31ea4u + (uint32_t)(bVar2 & 1) * 4u)))))));
    iVar6 = (int)sVar3;
    if (iVar4 - iVar6 < 0 == (iVar4 < 0 != iVar6 < 0 && iVar6 < 0 == iVar4 - iVar6 < 0) &&
        iVar4 != iVar6) {
      sVar3 = sVar1;
    }
    (*((short *)camry_host_ptr((uint32_t)((0xffffb4e4u + (uint32_t)((int)puVar5)))))) = sVar3;
  }
  return;
}

void return_only_stub_378d0(void)

{
  return;
}

void return_only_stub_378d2(void)

{
  return;
}

void apply_shared_second_axis_envelope(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = (int)shared_second_axis_envelope;
  iVar2 = (int)(*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebe6be8u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, second)))));
  DAT_febe6cec = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebe6be8u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, second)))));
  if (((additional_current_envelope_qualified == 'Z') &&
      (DAT_febe6cec = shared_second_axis_envelope,
      iVar2 - iVar3 < 0 != (iVar2 < 0 != iVar3 < 0 && iVar3 < 0 == iVar2 - iVar3 < 0))) &&
     (iVar1 = -iVar3, DAT_febe6cec = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebe6be8u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, second))))),
     iVar2 + iVar3 < 0 != (iVar2 < 0 != iVar1 < 0 && iVar1 < 0 == iVar2 + iVar3 < 0) ||
     iVar2 == iVar1)) {
    DAT_febe6cec = (short)iVar1;
  }
  iVar2 = (int)(*((volatile int16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6be8u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, second)))));
  DAT_febe6cee = (*((volatile int16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6be8u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, second)))));
  if (((additional_current_envelope_qualified == 'Z') &&
      (DAT_febe6cee = shared_second_axis_envelope,
      iVar2 - iVar3 < 0 != (iVar2 < 0 != iVar3 < 0 && iVar3 < 0 == iVar2 - iVar3 < 0))) &&
     (iVar1 = -iVar3, DAT_febe6cee = (*((volatile int16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6be8u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, second))))),
     iVar2 + iVar3 < 0 != (iVar2 < 0 != iVar1 < 0 && iVar1 < 0 == iVar2 + iVar3 < 0) ||
     iVar2 == iVar1)) {
    DAT_febe6cee = (short)iVar1;
  }
  return;
}

void return_only_stub_3791e(void)

{
  return;
}

void initialize_6cf0_scale_to_1024_37920(void)

{
  DAT_febe6cf0 = 0x400;
  return;
}

void compute_7da6_reciprocal_adjusted_scale_3792a(void)

{
  int iVar1;
  uint uVar2;
  
  uVar2 = (uint)DAT_febe7da6;
  DAT_febe6cf0 = 0x400;
  if (uVar2 != 0) {
    iVar1 = (DAT_00031a6e - uVar2) * (uint)DAT_00031a6c;
    if (uVar2 != 0) {
      if (iVar1 == -0x80000000 && uVar2 == 0xffffffff) {
        iVar1 = -0x80000000;
      }
      else {
        iVar1 = iVar1 / (int)uVar2;
      }
    }
    DAT_febe6cf0 = iVar1 + 0x400;
  }
  return;
}

void return_only_stub_37954(void)

{
  return;
}

void initialize_6cf4_scale_to_1024_37956(void)

{
  DAT_febe6cf4 = 0x400;
  return;
}

void compute_7da8_reciprocal_adjusted_scale_37960(void)

{
  int iVar1;
  uint uVar2;
  
  uVar2 = (uint)DAT_febe7da8;
  DAT_febe6cf4 = 0x400;
  if (uVar2 != 0) {
    iVar1 = (DAT_00031a72 - uVar2) * (uint)DAT_00031a70;
    if (uVar2 != 0) {
      if (iVar1 == -0x80000000 && uVar2 == 0xffffffff) {
        iVar1 = -0x80000000;
      }
      else {
        iVar1 = iVar1 / (int)uVar2;
      }
    }
    DAT_febe6cf4 = iVar1 + 0x400;
  }
  return;
}

void return_only_stub_3798a(void)

{
  return;
}

void initialize_eight_gain_filters_and_counters_3798c(void)

{
  DAT_febe6cfa = 0;
  DAT_febe6cf8 = 0;
  DAT_febe6d08 = DAT_00031a78;
  DAT_febe6d34 = (uint)DAT_00031a78 << 0x10;
  DAT_febe6d00 = DAT_00031a7a;
  DAT_febe6d2c = (uint)DAT_00031a7a << 0x10;
  DAT_febe6d0a = DAT_00031a80;
  DAT_febe6d38 = (uint)DAT_00031a80 << 0x10;
  DAT_febe6d02 = DAT_00031a82;
  DAT_febe6d30 = (uint)DAT_00031a82 << 0x10;
  DAT_febe6d18 = DAT_00031a7c;
  DAT_febe6d4c = (uint)DAT_00031a7c << 0x10;
  DAT_febe6d10 = DAT_00031a7e;
  DAT_febe6d44 = (uint)DAT_00031a7e << 0x10;
  DAT_febe6d1a = DAT_00031a84;
  DAT_febe6d50 = (uint)DAT_00031a84 << 0x10;
  DAT_febe6d12 = DAT_00031a86;
  DAT_febe6d48 = (uint)DAT_00031a86 << 0x10;
  return;
}

undefined4 update_pair_norm_or_flag_hold_counter_379fc(void)

{
  if (((uint)((int)((int)(int16_t)DAT_febe6e12) * (int)((int)(int16_t)DAT_febe6e12) + (int)((int)(int16_t)DAT_febe6e14) * (int)((int)(int16_t)DAT_febe6e14)) <
       DAT_00031ae0) &&
     ((uint)((int)((int)(int16_t)DAT_febe6e16) * (int)((int)(int16_t)DAT_febe6e16) + (int)((int)(int16_t)DAT_febe6e18) * (int)((int)(int16_t)DAT_febe6e18)) <
      DAT_00031ae0)) {
    if ((DAT_febe6cf8 != 0) && (DAT_febe6cf8 < DAT_00031a9a)) goto LAB_00037a50;
    if ((DAT_febe7826 != 'Z') && (DAT_febe7936 != 'Z')) {
      DAT_febe6cf8 = 0;
      return 0;
    }
  }
  if (DAT_00031a9a <= DAT_febe6cf8) {
    return 0x5a;
  }
LAB_00037a50:
  DAT_febe6cf8 = DAT_febe6cf8 + 2;
  return 0x5a;
}

undefined4 advance_e5c0_limited_window_counter_37a62(void)

{
  if (DAT_febee5c0 == '\0') {
    DAT_febe6cfa = 0;
    return 0;
  }
  if (DAT_febe6cfa < DAT_00031a98) {
    DAT_febe6cfa = DAT_febe6cfa + 2;
    return 0x5a;
  }
  return 0;
}

void select_and_filter_eight_control_gains_37a92(void)

{
  ushort uVar1;
  ushort uVar5;
  int iVar6;
  int iVar7;
  uint uVar8;
  uint32_t puVar9;
  int iVar10;
  undefined2 uVar11;
  undefined2 uVar12;
  undefined2 uVar13;
  undefined2 uVar14;
  int iVar15;
  uint uVar16;
  uint uVar17;
  uint uVar18;
  undefined2 *puVar19;
  ushort uVar2;
  ushort uVar3;
  ushort uVar4;
  
  uVar5 = DAT_febe71ec;
  puVar9 = 0xfebeb800u;
  if (DAT_febe8a14 != '\x01') {
    return;
  }
  DAT_febe6d20 = DAT_00031a78;
  DAT_febe6d1c = DAT_00031a7a;
  DAT_febe6d22 = DAT_00031a80;
  DAT_febe6d1e = DAT_00031a82;
  iVar6 = (int)((int)(int16_t)DAT_febe5f36);
  if (iVar6 + 0x7fff < 0 == (-1 < iVar6 && iVar6 + 0x7fff < 0) && iVar6 != -0x7fff) {
    if (iVar6 < 0) {
      iVar6 = (int)-((int)(int16_t)DAT_febe5f36);
    }
  }
  else {
    iVar6 = 0x7fff;
  }
  iVar10 = DAT_00031a76 - iVar6;
  uVar1 = DAT_00031a8c;
  uVar2 = DAT_00031a96;
  uVar3 = DAT_00031a94;
  uVar4 = DAT_00031a8e;
  if (iVar10 < 0 == (DAT_00031a76 < 0 != iVar6 < 0 && iVar6 < 0 == iVar10 < 0)) {
    uVar1 = DAT_00031a7c;
    uVar2 = DAT_00031a86;
    uVar3 = DAT_00031a84;
    uVar4 = DAT_00031a7e;
  }
  iVar6 = (uint)DAT_00031abc * 4;
  iVar10 = (uint)DAT_00031abe * 4;
  if (iVar6 - 1U < 0xffff) {
    iVar15 = (uint)DAT_febe6d18 * iVar6;
    iVar7 = (uint)uVar1 * iVar6;
  }
  else {
    iVar15 = (uint)DAT_febe6d18 << 0x10;
    iVar7 = (uint)uVar1 << 0x10;
  }
  DAT_febe6d4c = iVar7 + (DAT_febe6d4c - iVar15);
  DAT_febe6d18 = (ushort)((uint)DAT_febe6d4c >> 0x10);
  if (iVar10 - 1U < 0xffff) {
    iVar15 = (uint)DAT_febe6d10 * iVar10;
    iVar7 = (uint)uVar4 * iVar10;
  }
  else {
    iVar15 = (uint)DAT_febe6d10 << 0x10;
    iVar7 = (uint)uVar4 << 0x10;
  }
  DAT_febe6d44 = iVar7 + (DAT_febe6d44 - iVar15);
  DAT_febe6d10 = (ushort)((uint)DAT_febe6d44 >> 0x10);
  if (iVar6 - 1U < 0xffff) {
    iVar15 = (uint)DAT_febe6d1a * iVar6;
    iVar6 = (uint)uVar3 * iVar6;
  }
  else {
    iVar15 = (uint)DAT_febe6d1a << 0x10;
    iVar6 = (uint)uVar3 << 0x10;
  }
  DAT_febe6d50 = iVar6 + (DAT_febe6d50 - iVar15);
  DAT_febe6d1a = (ushort)((uint)DAT_febe6d50 >> 0x10);
  if (iVar10 - 1U < 0xffff) {
    iVar6 = (uint)DAT_febe6d12 * iVar10;
    iVar10 = (uint)uVar2 * iVar10;
  }
  else {
    iVar6 = (uint)DAT_febe6d12 << 0x10;
    iVar10 = (uint)uVar2 << 0x10;
  }
  DAT_febe6d48 = iVar10 + (DAT_febe6d48 - iVar6);
  DAT_febe6d12 = (ushort)((uint)DAT_febe6d48 >> 0x10);
  DAT_febe6d24 = DAT_febe6d10;
  DAT_febe6d26 = DAT_febe6d12;
  DAT_febe6d28 = DAT_febe6d18;
  DAT_febe6d2a = DAT_febe6d1a;
  iVar6 = update_pair_norm_or_flag_hold_counter_379fc();
  iVar10 = advance_e5c0_limited_window_counter_37a62();
  if ((uVar5 & 3) == 0) {
    if (iVar6 == 0x5a) {
      puVar19 = ((undefined *)camry_host_ptr(0x31aacu));
    }
    else {
      if (iVar10 != 0x5a) {
        uVar14 = (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb520u + (uint32_t)((int)puVar9))))));
        uVar8 = (uint)(*((ushort *)camry_host_ptr((uint32_t)((0xffffb51cu + (uint32_t)((int)puVar9))))));
        uVar13 = (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb522u + (uint32_t)((int)puVar9))))));
        uVar18 = (uint)(*((ushort *)camry_host_ptr((uint32_t)((0xffffb51eu + (uint32_t)((int)puVar9))))));
        uVar12 = (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb528u + (uint32_t)((int)puVar9))))));
        uVar17 = (uint)(*((ushort *)camry_host_ptr((uint32_t)((0xffffb524u + (uint32_t)((int)puVar9))))));
        uVar11 = (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb52au + (uint32_t)((int)puVar9))))));
        uVar16 = (uint)(*((ushort *)camry_host_ptr((uint32_t)((0xffffb526u + (uint32_t)((int)puVar9))))));
        goto LAB_00037c18;
      }
      puVar19 = ((undefined *)camry_host_ptr(0x31a9cu));
    }
    uVar14 = *puVar19;
    uVar8 = (uint)(ushort)puVar19[1];
    uVar13 = puVar19[4];
    uVar18 = (uint)(ushort)puVar19[5];
    uVar12 = puVar19[2];
    uVar17 = (uint)(ushort)puVar19[3];
    uVar11 = puVar19[6];
    uVar16 = (uint)(ushort)puVar19[7];
  }
  else {
    uVar12 = 0;
    uVar11 = 0;
    uVar8 = (uint)DAT_00031ac2;
    uVar17 = 0;
    uVar16 = 0;
    uVar18 = (uint)DAT_00031ac6;
    uVar14 = DAT_00031ac0;
    uVar13 = DAT_00031ac4;
  }
LAB_00037c18:
  (*((short *)camry_host_ptr((uint32_t)((0xffffb4fcu + (uint32_t)((int)puVar9)))))) = (short)uVar8;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb4feu + (uint32_t)((int)puVar9)))))) = (short)uVar18;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb50cu + (uint32_t)((int)puVar9)))))) = (short)uVar17;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb50eu + (uint32_t)((int)puVar9)))))) = (short)uVar16;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb504u + (uint32_t)((int)puVar9)))))) = uVar14;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb506u + (uint32_t)((int)puVar9)))))) = uVar13;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb514u + (uint32_t)((int)puVar9)))))) = uVar12;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb516u + (uint32_t)((int)puVar9)))))) = uVar11;
  (*((uint *)camry_host_ptr((uint32_t)((0xffffb53cu + (uint32_t)((int)puVar9)))))) = uVar8 * 0x69;
  (*((uint *)camry_host_ptr((uint32_t)((0xffffb540u + (uint32_t)((int)puVar9)))))) = uVar18 * 0x69;
  (*((uint *)camry_host_ptr((uint32_t)((0xffffb554u + (uint32_t)((int)puVar9)))))) = uVar17 * 0x69;
  (*((uint *)camry_host_ptr((uint32_t)((0xffffb558u + (uint32_t)((int)puVar9)))))) = uVar16 * 0x69;
  return;
}

void return_only_stub_37c48(void)

{
  return;
}

void return_only_stub_37c4a(void)

{
  return;
}

void select_phase_modulation_modes(void)

{
  uint uVar1;
  uint uVar2;
  
  DAT_febe6d64 = (int)((int)(int16_t)DAT_febe6c40) * (int)((int)(int16_t)DAT_febe6c40) + (int)((int)(int16_t)DAT_febe6c42) * (int)((int)(int16_t)DAT_febe6c42);
  uVar1 = DAT_febe6d64 >> 0xc;
  uVar2 = (uVar1 & 0xffff) >> 5;
  if (phase_offset_selector == 'Z') {
    if (uVar2 < 0x7f) {
      DAT_febe6d5e = (short)((int)((uVar1 & 0x1f) *
                                  ((uint)(*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x2bf14u + (uint32_t)(uVar2 + 1) * (uint32_t)sizeof(F33CurvePointS16U16)) + (uint32_t)(0) * (uint32_t)sizeof(F33CurvePointS16U16) + (uint32_t)offsetof(F33CurvePointS16U16, y))))) -
                                  (uint)(*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x2bf14u + (uint32_t)(uVar2) * (uint32_t)sizeof(F33CurvePointS16U16)) + (uint32_t)(0) * (uint32_t)sizeof(F33CurvePointS16U16) + (uint32_t)offsetof(F33CurvePointS16U16, y))))))) / 0x20) +
                     (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x2bf14u + (uint32_t)(uVar2) * (uint32_t)sizeof(F33CurvePointS16U16)) + (uint32_t)(0) * (uint32_t)sizeof(F33CurvePointS16U16) + (uint32_t)offsetof(F33CurvePointS16U16, y)))));
    }
    else {
      DAT_febe6d5e = 0x2366;
    }
  }
  else if (uVar2 < 0x7f) {
    DAT_febe6d5e = (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x2c118u + (uint32_t)(uVar2) * (uint32_t)sizeof(F33CurvePointS16U16)) + (uint32_t)(0) * (uint32_t)sizeof(F33CurvePointS16U16) + (uint32_t)offsetof(F33CurvePointS16U16, y))))) +
                   (short)((int)((uVar1 & 0x1f) *
                                ((uint)(*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x2c118u + (uint32_t)(uVar2 + 1) * (uint32_t)sizeof(F33CurvePointS16U16)) + (uint32_t)(0) * (uint32_t)sizeof(F33CurvePointS16U16) + (uint32_t)offsetof(F33CurvePointS16U16, y))))) -
                                (uint)(*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x2c118u + (uint32_t)(uVar2) * (uint32_t)sizeof(F33CurvePointS16U16)) + (uint32_t)(0) * (uint32_t)sizeof(F33CurvePointS16U16) + (uint32_t)offsetof(F33CurvePointS16U16, y))))))) / 0x20);
  }
  else {
    DAT_febe6d5e = 0xc9a;
  }
  if (DAT_febe8b88 == 'Z') {
    DAT_febe6d5c = 0;
    DAT_febe6d5e = phase_forced_offset;
  }
  else if (DAT_febe6d64 < phase_modulation_first_energy_threshold) {
    DAT_febe6d5c = 0;
  }
  else {
    DAT_febe6d5c = 0x5a;
    if (phase_modulation_second_energy_threshold <= DAT_febe6d64) {
      DAT_febe6d5c = 0xa5;
    }
  }
  DAT_febe6d68 = (int)((int)(int16_t)DAT_febe6c44) * (int)((int)(int16_t)DAT_febe6c44) + (int)((int)(int16_t)DAT_febe6c46) * (int)((int)(int16_t)DAT_febe6c46);
  uVar1 = DAT_febe6d68 >> 0xc;
  uVar2 = (uVar1 & 0xffff) >> 5;
  if (phase_offset_selector == 'Z') {
    if (uVar2 < 0x7f) {
      DAT_febe6d60 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x2c118u + (uint32_t)(uVar2) * (uint32_t)sizeof(F33CurvePointS16U16)) + (uint32_t)(0) * (uint32_t)sizeof(F33CurvePointS16U16) + (uint32_t)offsetof(F33CurvePointS16U16, y))))) +
                     (short)((int)((uVar1 & 0x1f) *
                                  ((uint)(*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x2c118u + (uint32_t)(uVar2 + 1) * (uint32_t)sizeof(F33CurvePointS16U16)) + (uint32_t)(0) * (uint32_t)sizeof(F33CurvePointS16U16) + (uint32_t)offsetof(F33CurvePointS16U16, y))))) -
                                  (uint)(*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x2c118u + (uint32_t)(uVar2) * (uint32_t)sizeof(F33CurvePointS16U16)) + (uint32_t)(0) * (uint32_t)sizeof(F33CurvePointS16U16) + (uint32_t)offsetof(F33CurvePointS16U16, y))))))) / 0x20);
    }
    else {
      DAT_febe6d60 = 0xc9a;
    }
  }
  else if (uVar2 < 0x7f) {
    DAT_febe6d60 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x2bf14u + (uint32_t)(uVar2) * (uint32_t)sizeof(F33CurvePointS16U16)) + (uint32_t)(0) * (uint32_t)sizeof(F33CurvePointS16U16) + (uint32_t)offsetof(F33CurvePointS16U16, y))))) +
                   (short)((int)((uVar1 & 0x1f) *
                                ((uint)(*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x2bf14u + (uint32_t)(uVar2 + 1) * (uint32_t)sizeof(F33CurvePointS16U16)) + (uint32_t)(0) * (uint32_t)sizeof(F33CurvePointS16U16) + (uint32_t)offsetof(F33CurvePointS16U16, y))))) -
                                (uint)(*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x2bf14u + (uint32_t)(uVar2) * (uint32_t)sizeof(F33CurvePointS16U16)) + (uint32_t)(0) * (uint32_t)sizeof(F33CurvePointS16U16) + (uint32_t)offsetof(F33CurvePointS16U16, y))))))) / 0x20);
  }
  else {
    DAT_febe6d60 = 0x2366;
  }
  if (DAT_febe8b89 == 'Z') {
    DAT_febe6d5d = 0;
    DAT_febe6d60 = phase_forced_offset;
  }
  else if (DAT_febe6d68 < phase_modulation_first_energy_threshold) {
    DAT_febe6d5d = 0;
  }
  else {
    DAT_febe6d5d = 0x5a;
    if (phase_modulation_second_energy_threshold <= DAT_febe6d68) {
      DAT_febe6d5d = 0xa5;
    }
  }
  return;
}

void return_only_stub_37de2(void)

{
  return;
}

void initialize_phase_offset_selector(void)

{
  DAT_febe6d6d = 0;
  phase_offset_selector_counter = 0;
  phase_offset_selector = 'Z';
  return;
}

void advance_phase_offset_selector(void)

{
  uchar uVar1;
  
  if ((phase_offset_selector_period <= phase_offset_selector_counter) ||
     (phase_offset_selector_counter = phase_offset_selector_counter + 1,
     uVar1 = phase_offset_selector,
     phase_offset_selector_period <= phase_offset_selector_counter)) {
    phase_offset_selector_counter = 0;
    uVar1 = 'Z';
    if (phase_offset_selector == 'Z') {
      uVar1 = 0xa5;
    }
  }
  if (phase_offset_selector_override == '3') {
    uVar1 = 'Z';
  }
  else if (phase_offset_selector_override == '\"') {
    uVar1 = 0xa5;
  }
  phase_offset_selector = uVar1;
  return;
}

void return_only_stub_37e44(void)

{
  return;
}

void return_only_stub_37e46(void)

{
  return;
}

void compose_current_feedback(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  
  if ((output_request_status & 0x40004) != 0) {
    DAT_febe6d70 = 0;
    DAT_febe6d72 = 0;
    DAT_febe6d78 = 0;
    return;
  }
  iVar4 = DAT_febe6e2c;
  iVar1 = DAT_febe6e28;
  if ((DAT_febe71ec & 1) != 0) {
    iVar4 = 0;
    iVar1 = 0;
  }
  iVar2 = DAT_febe6e34;
  iVar5 = DAT_febe6e30;
  if ((DAT_febe71ec >> 1 & 1) != 0) {
    iVar2 = 0;
    iVar5 = 0;
  }
  iVar3 = iVar5 + iVar1;
  DAT_febe6d78 = iVar2 + iVar4;
  iVar1 = iVar1 - iVar5;
  iVar4 = iVar4 - iVar2;
  if (iVar3 + 0x7fff < 0 == (-1 < iVar3 && iVar3 + 0x7fff < 0) && iVar3 != -0x7fff) {
    if (iVar3 + -0x7fff < 0 == (iVar3 < 0 && -1 < iVar3 + -0x7fff) && iVar3 != 0x7fff) {
      iVar3 = 0x7fff;
    }
    DAT_febe6d70 = (undefined2)iVar3;
  }
  else {
    DAT_febe6d70 = 0x8001;
  }
  if ((int)DAT_febe6d78 + 0x7fff < 0 == (-1 < (int)DAT_febe6d78 && (int)DAT_febe6d78 + 0x7fff < 0) &&
      ((int)(int32_t)DAT_febe6d78) != -0x7fff) {
    iVar5 = ((int)(int32_t)DAT_febe6d78);
    if ((int)DAT_febe6d78 + -0x7fff < 0 == ((int)DAT_febe6d78 < 0 && -1 < (int)DAT_febe6d78 + -0x7fff) &&
        ((int)(int32_t)DAT_febe6d78) != 0x7fff) {
      iVar5 = 0x7fff;
    }
  }
  else {
    iVar5 = -0x7fff;
  }
  DAT_febe6d72 = (short)iVar5;
  if (iVar1 + 0x7fff < 0 == (-1 < iVar1 && iVar1 + 0x7fff < 0) && iVar1 != -0x7fff) {
    if (iVar1 + -0x7fff < 0 == (iVar1 < 0 && -1 < iVar1 + -0x7fff) && iVar1 != 0x7fff) {
      DAT_febe6d74 = 0x7fff;
    }
    else {
      DAT_febe6d74 = (undefined2)iVar1;
    }
  }
  else {
    DAT_febe6d74 = 0x8001;
  }
  if (iVar4 + 0x7fff < 0 == (-1 < iVar4 && iVar4 + 0x7fff < 0) && iVar4 != -0x7fff) {
    if (iVar4 + -0x7fff < 0 == (iVar4 < 0 && -1 < iVar4 + -0x7fff) && iVar4 != 0x7fff) {
      DAT_febe6d76 = 0x7fff;
    }
    else {
      DAT_febe6d76 = (undefined2)iVar4;
    }
  }
  else {
    DAT_febe6d76 = 0x8001;
  }
  return;
}

void return_only_stub_37f12(void)

{
  return;
}

void return_only_stub_37f14(void)

{
  return;
}

void publish_corrected_current_reference_pairs(void)

{
  int iVar1;
  int iVar2;
  
  DAT_febe6d84 = ((int)(int16_t)DAT_febe6dd6);
  DAT_febe6d86 = actual_first_current_command;
  iVar2 = (int)((int)(int16_t)DAT_febe6da6) + (int)actual_first_current_command;
  iVar1 = (int)((int)(int16_t)DAT_febe6da8) + (int)((int)(int16_t)DAT_febe6dd6);
  if (iVar2 + 0x7fff < 0 == (-1 < iVar2 && iVar2 + 0x7fff < 0) && iVar2 != -0x7fff) {
    if (iVar2 + -0x7fff < 0 == (iVar2 < 0 && -1 < iVar2 + -0x7fff) && iVar2 != 0x7fff) {
      iVar2 = 0x7fff;
    }
    DAT_febe6d80 = (undefined2)iVar2;
  }
  else {
    DAT_febe6d80 = 0x8001;
  }
  if (iVar1 + 0x7fff < 0 == (-1 < iVar1 && iVar1 + 0x7fff < 0) && iVar1 != -0x7fff) {
    if (iVar1 + -0x7fff < 0 == (iVar1 < 0 && -1 < iVar1 + -0x7fff) && iVar1 != 0x7fff) {
      DAT_febe6d7c = 0x7fff;
    }
    else {
      DAT_febe6d7c = (undefined2)iVar1;
    }
  }
  else {
    DAT_febe6d7c = 0x8001;
  }
  DAT_febe6d82 = DAT_00031b2a + ((int)(int16_t)DAT_febe6daa);
  DAT_febe6d7e = DAT_00031b28 + ((int)(int16_t)DAT_febe6dac);
  return;
}

void return_only_stub_37f8e(void)

{
  return;
}

void return_only_stub_37f90(void)

{
  return;
}

uint current_reference_curve_feedback_magnitude(void)

{
  int iVar1;
  uint uVar2;
  
  iVar1 = (int)((int)(int16_t)DAT_febe6d72);
  if ((DAT_febe71ec & 3) != 0) {
    iVar1 = iVar1 << 1;
  }
  if (iVar1 + -0x7fff < 0 == (iVar1 < 0 && -1 < iVar1 + -0x7fff)) {
    iVar1 = 0x7fff;
  }
  if (iVar1 + 0x7fff < 0 != (-1 < iVar1 && iVar1 + 0x7fff < 0)) {
    iVar1 = -0x7fff;
  }
  uVar2 = (uint)(short)iVar1;
  if ((int)((int)uVar2 + 0x7fff) < 0 == (-1 < (int)uVar2 && (int)((int)uVar2 + 0x7fff) < 0) &&
      uVar2 != 0xffff8001) {
    if ((int)uVar2 < 0) {
      return (int)(short)-(short)iVar1;
    }
    return uVar2;
  }
  return 0x7fff;
}

void update_current_reference_curve_floor(ushort feedback_magnitude)

{
  uchar uVar1;
  short sVar2;
  ushort uVar3;
  int iVar4;
  uint32_t puVar5;
  uint uVar6;
  int iVar7;
  short sVar8;
  int iVar9;
  int iVar10;
  uchar uVar11;
  short sStack_1a;
  
  uVar3 = DAT_febe71ec;
  iVar7 = current_reference_floor.accumulator_q16;
  sVar2 = current_reference_floor.curve_floor;
  uVar11 = current_reference_floor.filter_active;
  uVar1 = current_reference_transient.active;
  puVar5 = 0xfebeb800u;
  iVar10 = (int)current_reference_floor.curve_floor;
  if (current_reference_transient.active == 'Z') {
    puVar5 = 0xfebeb800u;
    interpolate_u16_axis_s16_values_702b0(switched_signed_request_curve,(uint)feedback_magnitude,&sStack_1a);
  }
  else {
    uVar6 = (uint)(feedback_magnitude >> 7);
    if (uVar6 < 0xff) {
      iVar9 = (int)(short)(*(short *)(((undefined *)camry_host_ptr((uint32_t)(0x2c31eu + (uint32_t)(uVar6 * 4) * 1u)))) +
                          (short)((int)((feedback_magnitude & 0x7f) *
                                       ((int)*(short *)(((undefined *)camry_host_ptr((uint32_t)(0x2c31eu + (uint32_t)((uVar6 + 1) * 4) * 1u)))) -
                                       (int)*(short *)(((undefined *)camry_host_ptr((uint32_t)(0x2c31eu + (uint32_t)(uVar6 * 4) * 1u)))))) / 0x80));
    }
    else {
      iVar9 = 0;
    }
    sStack_1a = (short)iVar9;
    if (current_reference_floor.previous_transient == 'Z') {
      iVar7 = iVar10 << 0x10;
      uVar11 = 'Z';
    }
    iVar4 = (int)((int)(int16_t)DAT_febe6f7e);
    if (iVar4 - iVar9 < 0 == (iVar4 < 0 != iVar9 < 0 && iVar9 < 0 == iVar4 - iVar9 < 0) &&
        iVar4 != iVar9) {
      sStack_1a = ((int)(int16_t)DAT_febe6f7e);
    }
  }
  if ((uVar3 & 3) != 0) {
    sStack_1a = sStack_1a / 2;
  }
  (*((short *)camry_host_ptr((uint32_t)((0xffffb58eu + (uint32_t)((int)puVar5)))))) = sStack_1a;
  sVar8 = sStack_1a;
  if (uVar11 == 'Z') {
    uVar6 = (uint)current_reference_floor_calibration.filter_coefficient;
    if (uVar6 - 1 < 0xffff) {
      iVar10 = iVar10 * uVar6;
      iVar9 = (int)sStack_1a * uVar6;
    }
    else {
      iVar10 = iVar10 << 0x10;
      iVar9 = (int)sStack_1a << 0x10;
    }
    iVar9 = iVar9 + (iVar7 - iVar10);
    (*((int *)camry_host_ptr((uint32_t)((0xffffb598u + (uint32_t)((int)puVar5)))))) = iVar9;
    iVar7 = (int)current_reference_floor_calibration.release_delta_threshold;
    iVar10 = (int)(short)(sStack_1a - sVar2);
    sVar8 = (short)(iVar9 / 0x10000);
    (*((short *)camry_host_ptr((uint32_t)((0xffffb592u + (uint32_t)((int)puVar5)))))) = sVar8;
    (*((short *)camry_host_ptr((uint32_t)((0xffffb590u + (uint32_t)((int)puVar5)))))) = sStack_1a - sVar2;
    if (iVar10 - iVar7 < 0 != (iVar10 < 0 != iVar7 < 0 && iVar7 < 0 == iVar10 - iVar7 < 0) ||
        iVar10 == iVar7) {
      uVar11 = '\0';
      sVar8 = sStack_1a;
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb588u + (uint32_t)((int)puVar5) * 1u)))) = uVar1;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb589u + (uint32_t)((int)puVar5) * 1u)))) = uVar11;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb58cu + (uint32_t)((int)puVar5)))))) = sVar8;
  return;
}
