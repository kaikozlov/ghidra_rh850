#include "common.h"

void f33_reset_latched_monitor(F33LatchedMonitorState *state)

{
  state->packed_status = 0;
  state->passing_count = 0;
  state->failing_count = 0;
  state->failing_high_water = 0;
  return;
}

void f33_reset_windowed_monitor(F33WindowedMonitorState *state)

{
  state->packed_status = 0;
  state->passing_count = 0;
  state->passing_window = 0;
  state->failing_count = 0;
  state->failing_window = 0;
  state->failing_high_water = 0;
  return;
}

void FUN_0006a574(undefined4 param_1,undefined1 *param_2)

{
  *param_2 = (char)((uint)param_1 >> 8);
  param_2[1] = (char)param_1;
  return;
}

undefined4 FUN_00095418(ushort param_1,undefined2 *param_2)

{
  uint uVar1;
  undefined4 uVar2;
  uint uVar3;
  uint uVar4;
  
  uVar2 = 1;
  if (DAT_00026014 != 0) {
    uVar4 = 0;
    if (param_1 < DAT_00026028) {
      return uVar2;
    }
    if (DAT_00026028 != param_1) {
      uVar3 = (uint)(ushort)(DAT_00026014 - 1);
      if (DAT_00026028 < param_1) {
        return uVar2;
      }
      do {
        if (uVar3 <= uVar4) {
          return uVar2;
        }
        uVar1 = (int)(uVar4 + uVar3) >> 1;
        if (DAT_00026028 < param_1) {
          uVar4 = uVar1 + 1 & 0xffff;
          uVar1 = uVar3;
        }
        uVar3 = uVar1;
      } while (DAT_00026028 != param_1);
    }
    *param_2 = (short)uVar4;
    uVar2 = 0;
  }
  return uVar2;
}

void FUN_0007025c(short *param_1,short param_2,short *param_3)

{
  short *psVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  short sVar5;
  
  iVar4 = (int)param_2;
  iVar2 = (int)*param_1;
  if ((iVar2 == 0x7fff) ||
     (iVar2 - iVar4 < 0 == (iVar2 < 0 != iVar4 < 0 && iVar4 < 0 == iVar2 - iVar4 < 0))) {
    sVar5 = param_1[1];
  }
  else {
    iVar2 = 0;
    while( true ) {
      psVar1 = param_1 + iVar2 * 2;
      iVar3 = (int)*psVar1;
      if (iVar3 == 0x7fff) break;
      if (iVar3 - iVar4 < 0 == (iVar3 < 0 != iVar4 < 0 && iVar4 < 0 == iVar3 - iVar4 < 0) &&
          iVar3 != iVar4) {
        iVar3 = iVar3 - psVar1[-2];
        iVar2 = (iVar4 - psVar1[-2]) * ((uint)(ushort)psVar1[1] - (uint)(ushort)psVar1[-1]);
        if (iVar3 != 0) {
          if (iVar2 == -0x80000000 && iVar3 == -1) {
            iVar2 = 0;
          }
          else {
            iVar2 = iVar2 / iVar3;
          }
        }
        sVar5 = psVar1[-1] + (short)iVar2;
        goto LAB_000702aa;
      }
      iVar2 = iVar2 + 1;
    }
    sVar5 = psVar1[-1];
  }
LAB_000702aa:
  *param_3 = sVar5;
  return;
}

void FUN_0006b98a(undefined4 *param_1)

{
  *param_1 = 0;
  *(undefined2 *)(param_1 + 1) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 6)))) = 0;
  *(undefined2 *)(param_1 + 2) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 10)))) = 0;
  *(undefined2 *)(param_1 + 3) = 0;
  return;
}

void f33_reset_recoverable_monitor(F33RecoverableMonitorState *state)

{
  state->packed_status = 0;
  state->passing_count = 0;
  state->failing_count = 0;
  state->failing_high_water = 0;
  state->recovery_count = 0;
  return;
}

void FUN_00044ece(uint param_1,ushort *param_2)

{
  *param_2 = *param_2 | (ushort)(1 << ((int)(param_1 & 0xffff) >> 0xc));
  return;
}

void f33_set_channel_owner_request(uchar owner,uint request_mask)

{
  if (owner < 5) {
    f33_channel_request_state.owner_requests[owner] = request_mask;
  }
  return;
}

void FUN_0006a522(short param_1,short *param_2)

{
  int iVar1;
  
  iVar1 = (int)param_1;
  if (iVar1 + 0x7fff < 0 == (-1 < iVar1 && iVar1 + 0x7fff < 0) && iVar1 != -0x7fff) {
    if (iVar1 < 0) {
      param_1 = -param_1;
    }
  }
  else {
    param_1 = 0x7fff;
  }
  *param_2 = param_1;
  return;
}

void f33_reset_terminal_monitor(F33TerminalMonitorState *state)

{
  state->status = 0xff;
  state->passing_count = 0;
  state->failing_count = 0;
  state->failing_high_water = 0;
  return;
}

void FUN_00054aac(int param_1,int param_2)

{
  int iVar1;
  uint uVar2;
  
  uVar2 = 0;
  do {
    iVar1 = uVar2 * 4;
    uVar2 = uVar2 + 1;
    (*((undefined4 *)camry_host_ptr((uint32_t)(iVar1 + param_1)))) = (*((undefined4 *)camry_host_ptr((uint32_t)(iVar1 + param_2))));
  } while (uVar2 < 8);
  return;
}

void FUN_000d1222(short param_1,int *param_2)

{
  int iVar1;
  
  iVar1 = (int)param_1;
  if (iVar1 < 1) {
    iVar1 = 0;
  }
  *param_2 = iVar1;
  return;
}

void FUN_0004d144(int param_1,undefined1 *param_2)

{
  undefined1 uVar1;
  
  if ((param_1 == -3) || (param_1 == -5)) {
    uVar1 = 0x12;
  }
  else if (param_1 == -6) {
    uVar1 = 0x22;
  }
  else if (param_1 == -0xd) {
    uVar1 = 0x11;
  }
  else if (param_1 == -0xe) {
    uVar1 = 0x33;
  }
  else {
    uVar1 = 0x10;
  }
  *param_2 = uVar1;
  return;
}

void f33_step_retained_unsigned_gain(F33GainSlewState *state)

{
  int iVar1;
  ushort uVar2;
  ushort uVar3;
  ushort uVar4;
  uint uVar5;
  
  uVar2 = state->current;
  uVar5 = (uint)uVar2;
  uVar4 = state->down_target;
  if ((uVar5 < uVar4) || (state->direction != '\x02')) {
    uVar4 = state->up_target;
    uVar3 = state->up_step;
    uVar5 = uVar4 - uVar5;
    iVar1 = uVar5 - uVar3;
    if (iVar1 < 0 == ((int)uVar5 < 0 && -1 < iVar1) && uVar5 != uVar3) {
      uVar4 = uVar2 + uVar3;
    }
  }
  else {
    uVar3 = state->down_step;
    uVar5 = uVar5 - uVar4;
    iVar1 = uVar5 - uVar3;
    if (iVar1 < 0 == ((int)uVar5 < 0 && -1 < iVar1) && uVar5 != uVar3) {
      uVar4 = uVar2 - uVar3;
    }
  }
  state->current = uVar4;
  return;
}

void FUN_000b6160(void)

{
  undefined1 uStack_13;
  undefined1 uStack_12;
  undefined1 uStack_11;
  
  uStack_13 = 1;
  uStack_12 = 0;
  uStack_11 = 0xff;
  FUN_000b6142(0, camry_host_addr(&uStack_13));
  uStack_13 = 1;
  uStack_12 = 0;
  uStack_11 = 0xff;
  FUN_000b6142(1, camry_host_addr(&uStack_13));
  uStack_13 = 1;
  uStack_12 = 0;
  uStack_11 = 0xff;
  FUN_000b6142(2, camry_host_addr(&uStack_13));
  uStack_13 = 1;
  uStack_12 = 0;
  uStack_11 = 0xff;
  FUN_000b6142(3, camry_host_addr(&uStack_13));
  uStack_13 = 1;
  uStack_12 = 0;
  uStack_11 = 0xff;
  FUN_000b6142(4, camry_host_addr(&uStack_13));
  uStack_13 = 1;
  uStack_12 = 0;
  uStack_11 = 0xff;
  FUN_000b6142(5, camry_host_addr(&uStack_13));
  uStack_13 = 1;
  uStack_12 = 0;
  uStack_11 = 0xff;
  FUN_000b6142(6, camry_host_addr(&uStack_13));
  uStack_13 = 1;
  uStack_12 = 0;
  uStack_11 = 0xff;
  FUN_000b6142(7, camry_host_addr(&uStack_13));
  return;
}

void 
f33_copy_diagnostic_capture(F33DiagnosticCapture *destination,F33DiagnosticCapture *source)

{
  int iVar1;
  uint uVar2;
  
  uVar2 = 0;
  do {
    iVar1 = uVar2 * 4;
    uVar2 = uVar2 + 1;
    *(undefined4 *)(destination->profile_prefix + iVar1) =
         *(undefined4 *)(source->profile_prefix + iVar1);
  } while (uVar2 < 0x3c);
  return;
}

void FUN_0006a5cc(short param_1,undefined1 *param_2)

{
  undefined1 uVar1;
  int iVar2;
  
  iVar2 = (int)param_1;
  if (iVar2 + 0x7f < 0 == (-1 < iVar2 && iVar2 + 0x7f < 0)) {
    if (iVar2 + -0x7f < 0 == (iVar2 < 0 && -1 < iVar2 + -0x7f) && iVar2 != 0x7f) {
      uVar1 = 0x7f;
    }
    else {
      if (iVar2 + 0x80 < 0 != (-1 < iVar2 && iVar2 + 0x80 < 0) || iVar2 == -0x80) {
        iVar2 = -0x80;
      }
      uVar1 = (undefined1)iVar2;
    }
  }
  else {
    uVar1 = 0x81;
  }
  *param_2 = uVar1;
  return;
}

void FUN_00070110(short param_1,short param_2,short param_3,short *param_4)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar1 = (int)param_1;
  iVar2 = (int)param_2;
  iVar3 = (int)param_3;
  if (iVar2 - iVar1 < 0 != (iVar2 < 0 != iVar1 < 0 && iVar1 < 0 == iVar2 - iVar1 < 0)) {
    iVar1 = iVar2;
  }
  if (iVar3 - iVar1 < 0 != (iVar3 < 0 != iVar1 < 0 && iVar1 < 0 == iVar3 - iVar1 < 0) ||
      iVar3 == iVar1) {
    param_3 = (short)iVar1;
  }
  *param_4 = param_3;
  return;
}

void FUN_00070208(short *param_1,short param_2,short *param_3)

{
  short *psVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  short sVar5;
  
  iVar4 = (int)param_2;
  iVar2 = (int)*param_1;
  if ((iVar2 == 0x7fff) ||
     (iVar2 - iVar4 < 0 == (iVar2 < 0 != iVar4 < 0 && iVar4 < 0 == iVar2 - iVar4 < 0))) {
    sVar5 = param_1[1];
  }
  else {
    iVar2 = 0;
    while( true ) {
      psVar1 = param_1 + iVar2 * 2;
      iVar3 = (int)*psVar1;
      if (iVar3 == 0x7fff) break;
      if (iVar3 - iVar4 < 0 == (iVar3 < 0 != iVar4 < 0 && iVar4 < 0 == iVar3 - iVar4 < 0) &&
          iVar3 != iVar4) {
        iVar3 = iVar3 - psVar1[-2];
        iVar2 = (iVar4 - psVar1[-2]) * ((int)psVar1[1] - (int)psVar1[-1]);
        if (iVar3 != 0) {
          if (iVar2 == -0x80000000 && iVar3 == -1) {
            iVar2 = 0;
          }
          else {
            iVar2 = iVar2 / iVar3;
          }
        }
        sVar5 = psVar1[-1] + (short)iVar2;
        goto LAB_00070256;
      }
      iVar2 = iVar2 + 1;
    }
    sVar5 = psVar1[-1];
  }
LAB_00070256:
  *param_3 = sVar5;
  return;
}

undefined4 FUN_00095500(void)

{
  uint uVar1;
  
  for (uVar1 = (uint)DAT_00026018; uVar1 != 0; uVar1 = uVar1 - 1) {
    DAT_febe5d23 = 0;
  }
  return 0;
}

void FUN_00083c9c(uint param_1)

{
  char cVar1;
  uint uVar2;
  uint uVar3;
  
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5019u + (uint32_t)(param_1 & 0xff) * 1u))));
  if ((cVar1 == 'Z') || (((int8_t)cVar1) == -0x6a)) {
    uVar3 = (uint)DAT_00022ea4;
    for (uVar2 = 0; uVar2 < uVar3; uVar2 = uVar2 + 1 & 0xff) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5019u + (uint32_t)(uVar2) * 1u)))) = 0x69;
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5019u + (uint32_t)(param_1 & 0xff) * 1u)))) = 'Z';
  }
  return;
}

undefined4 FUN_00094d9c(ushort param_1,undefined2 *param_2)

{
  uint uVar1;
  undefined4 uVar2;
  uint uVar3;
  uint uVar4;
  
  uVar2 = 1;
  if (DAT_00026018 != '\0') {
    uVar4 = 0;
    if (param_1 < DAT_00025fec) {
      return uVar2;
    }
    if (DAT_00025fec != param_1) {
      uVar3 = (uint)(byte)(DAT_00026018 - 1);
      if (DAT_00025fec < param_1) {
        return uVar2;
      }
      do {
        if (uVar3 <= uVar4) {
          return uVar2;
        }
        uVar1 = (int)(uVar4 + uVar3) >> 1;
        if (DAT_00025fec < param_1) {
          uVar4 = uVar1 + 1 & 0xff;
          uVar1 = uVar3;
        }
        uVar3 = uVar1;
      } while (DAT_00025fec != param_1);
    }
    *param_2 = (short)uVar4;
    uVar2 = 0;
  }
  return uVar2;
}

void FUN_00074872(int param_1,undefined1 param_2,uint param_3)

{
  uint uVar1;
  
  for (uVar1 = 0; uVar1 < param_3; uVar1 = uVar1 + 1) {
    (*((undefined1 *)camry_host_ptr((uint32_t)(uVar1 + param_1)))) = param_2;
  }
  return;
}

void FUN_0007211a(uint param_1)

{
  f33_nvm_accumulate_diagnostic_mask((uint)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x273dcu + (uint32_t)(param_1 & 0xff) * 4u)))));
  return;
}

int f33_interpolate_signed_sentinel_curve(short *points,short input)

{
  short *psVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  iVar4 = (int)input;
  iVar2 = (int)*points;
  if ((iVar2 != 0x7fff) &&
     (iVar2 - iVar4 < 0 != (iVar2 < 0 != iVar4 < 0 && iVar4 < 0 == iVar2 - iVar4 < 0))) {
    iVar2 = 0;
    while( true ) {
      psVar1 = points + iVar2 * 2;
      iVar3 = (int)*psVar1;
      if (iVar3 == 0x7fff) {
        return (int)psVar1[-1];
      }
      if (iVar3 - iVar4 < 0 == (iVar3 < 0 != iVar4 < 0 && iVar4 < 0 == iVar3 - iVar4 < 0)) break;
      iVar2 = iVar2 + 1;
    }
    iVar3 = iVar3 - psVar1[-2];
    iVar2 = (iVar4 - psVar1[-2]) * ((int)psVar1[1] - (int)psVar1[-1]);
    if (iVar3 != 0) {
      if (iVar2 == -0x80000000 && iVar3 == -1) {
        iVar2 = 0;
      }
      else {
        iVar2 = iVar2 / iVar3;
      }
    }
    return (int)(short)(psVar1[-1] + (short)iVar2);
  }
  return (int)points[1];
}

void f33_set_direct_output_codes_bank0(ushort *codes)

{
  f33_direct_output_codes_bank0[0] = *codes;
  f33_direct_output_codes_bank0[1] = codes[1];
  f33_direct_output_codes_bank0[2] = codes[2];
  return;
}

void f33_reset_application_latched_monitor(F33LatchedMonitorState *state)

{
  state->packed_status = 0;
  state->passing_count = 0;
  state->failing_count = 0;
  state->failing_high_water = 0;
  return;
}

void FUN_000706ae(int param_1,int param_2,uint *param_3)

{
  int iVar1;
  uint uVar2;
  
  if ((param_1 == 0) || (param_2 == 0)) {
    uVar2 = 0;
    goto LAB_00070700;
  }
  if (param_1 < 0) {
    if (-1 < param_2) goto LAB_000706e4;
  }
  else if (param_2 < 0) {
LAB_000706e4:
    iVar1 = (int)((ulonglong)((longlong)param_2 * (longlong)param_1) >> 0x20) + 1;
    if ((iVar1 < 0 != (-1 < (longlong)param_2 * (longlong)param_1 && iVar1 < 0)) ||
       (uVar2 = param_1 * param_2, uVar2 < 0x80000001)) {
      uVar2 = 0x80000001;
    }
    goto LAB_00070700;
  }
  if ((-1 < (longlong)param_2 * (longlong)param_1 &&
       (int)((ulonglong)((longlong)param_2 * (longlong)param_1) >> 0x20) != 0) ||
     (uVar2 = param_1 * param_2, 0x7fffffff < (uint)(param_1 * param_2))) {
    uVar2 = 0x7fffffff;
  }
LAB_00070700:
  *param_3 = uVar2;
  return;
}

undefined4 FUN_00089d08(undefined2 *param_1)

{
  if ((uintptr_t)(param_1)!=(uintptr_t)((undefined2 *)0x0)) {
    *param_1 = 0;
    return 0;
  }
  return 1;
}

undefined1 FUN_00005060(char *param_1,char param_2,char param_3)

{
  undefined1 uVar1;
  
  uVar1 = 1;
  if (((param_3 == '\0') && (param_2 == '\x02')) && (*param_1 == '>')) {
    if (((int8_t)param_1[1]) == -0x80) {
      uVar1 = 0;
    }
    else {
      uVar1 = 1;
    }
  }
  return uVar1;
}

void f33_fill_constant_block_8de1a(void)

{
  DAT_febf45d6 = 0x300;
  DAT_febf45d4 = 0;
  DAT_febf45dd = 1;
  DAT_febf45d2 = 0;
  DAT_febf45d0 = 0;
  DAT_febf45dc = 0;
  DAT_febf45e3 = 1;
  DAT_febf45e2 = 0xff;
  DAT_febf45e1 = 0;
  DAT_febf45e0 = 0;
  DAT_febf45d8 = 0;
  DAT_febf45df = 1;
  DAT_febf45de = 0;
  return;
}

void FUN_0007012a(int param_1,int param_2,int param_3,int *param_4)

{
  if (param_2 - param_1 < 0 != (param_2 < 0 != param_1 < 0 && param_1 < 0 == param_2 - param_1 < 0))
  {
    param_1 = param_2;
  }
  if (param_3 - param_1 < 0 == (param_3 < 0 != param_1 < 0 && param_1 < 0 == param_3 - param_1 < 0)
      && param_3 != param_1) {
    param_1 = param_3;
  }
  *param_4 = param_1;
  return;
}

void thunk_FUN_000772f8(void)

{
  FUN_000772f8();
  return;
}

void FUN_000772f8(void)

{
  f33_nvm_checksum_accumulator = 0;
  DAT_febf6c24 = 0xffffffff;
  DAT_febf6c44 = 0xffff;
  return;
}

void f33_return_only_stub_7be4c(void)

{
  return;
}

void FUN_000d1178(short param_1,short *param_2)

{
  int iVar1;
  
  iVar1 = (int)param_1;
  if (iVar1 + 0x7fff < 0 == (-1 < iVar1 && iVar1 + 0x7fff < 0) && iVar1 != -0x7fff) {
    if (iVar1 < 0) {
      param_1 = -param_1;
    }
  }
  else {
    param_1 = 0x7fff;
  }
  *param_2 = param_1;
  return;
}

uint FUN_000d07f2(short *param_1,short param_2)

{
  short *psVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  iVar4 = (int)param_2;
  iVar2 = (int)*param_1;
  if ((iVar2 != 0x7fff) &&
     (iVar2 - iVar4 < 0 != (iVar2 < 0 != iVar4 < 0 && iVar4 < 0 == iVar2 - iVar4 < 0))) {
    iVar2 = 0;
    while( true ) {
      psVar1 = param_1 + iVar2 * 2;
      iVar3 = (int)*psVar1;
      if (iVar3 == 0x7fff) {
        return (uint)(ushort)psVar1[-1];
      }
      if (iVar3 - iVar4 < 0 == (iVar3 < 0 != iVar4 < 0 && iVar4 < 0 == iVar3 - iVar4 < 0)) break;
      iVar2 = iVar2 + 1;
    }
    iVar3 = iVar3 - psVar1[-2];
    iVar2 = (iVar4 - psVar1[-2]) * ((uint)(ushort)psVar1[1] - (uint)(ushort)psVar1[-1]);
    if (iVar3 != 0) {
      if (iVar2 == -0x80000000 && iVar3 == -1) {
        iVar2 = 0;
      }
      else {
        iVar2 = iVar2 / iVar3;
      }
    }
    return (uint)(ushort)psVar1[-1] + iVar2 & 0xffff;
  }
  return (uint)(ushort)param_1[1];
}

void FUN_000d22c0(ushort *param_1,ushort param_2,ushort *param_3)

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

void f33_reset_bank1_current_reference_feedback(void)

{
  f33_current_reference_feedback[1].request = 0;
  f33_current_reference_feedback[1].error = 0;
  f33_current_reference_feedback[1].previous_error = 0;
  f33_current_reference_feedback[1].opaque_14 = 0;
  f33_current_reference_feedback[1].request_before_global_clamp = 0;
  f33_current_reference_feedback[1].current_gain = 0;
  f33_current_reference_feedback[1].previous_gain = 0;
  f33_current_reference_feedback[1].retained_transient_delta = 0;
  f33_current_reference_feedback[1].saturated_base_plus_delta = 0;
  return;
}

void f33_reset_task_rate_window(F33TaskRateWindow *state)

{
  state->phase = '\0';
  state->count = '\0';
  state->maximum = '\0';
  state->minimum = 0xff;
  return;
}

uint FUN_00082e54(char param_1)

{
  uint uVar1;
  
  for (uVar1 = 0; (uVar1 < DAT_00022abc && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22a8eu + (uint32_t)(uVar1) * 1u)))) != param_1));
      uVar1 = uVar1 + 1 & 0xff) {
  }
  return uVar1;
}

void f33_return_only_stub_79d36(void)

{
  return;
}

void FUN_00070160(int param_1,int param_2,int *param_3)

{
  if (param_2 - param_1 < 0 != (param_2 < 0 != param_1 < 0 && param_1 < 0 == param_2 - param_1 < 0))
  {
    param_1 = param_2;
  }
  *param_3 = param_1;
  return;
}

void f33_follow_s16_fractional
               (F33FractionalFollowing16 *state,uint coefficient,short *output,int *new_accumulator)

{
  int iVar1;
  
  if (0xfffe < coefficient - 1) {
    coefficient = 0x10000;
  }
  iVar1 = (int)state->target * coefficient +
          (state->accumulator - (int)state->previous * coefficient);
  *new_accumulator = iVar1;
  *output = (short)(iVar1 / 0x10000);
  return;
}

F33MonitorCurrentRecord * FUN_000567be(void)

{
  return ((undefined *)camry_host_ptr(0xa000u));
}

void f33_return_only_stub_7be4a(void)

{
  return;
}

void f33_return_only_stub_796bc(void)

{
  return;
}

F33CanTpConfiguration * FUN_0007a32e(void)

{
  return ((undefined *)camry_host_ptr(0x22c70u));
}

void FUN_000d1e8c(ushort *param_1,uint param_2,ushort *param_3)

{
  ushort *puVar1;
  ushort uVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  
  param_2 = param_2 & 0xffff;
  if ((*param_1 == 0xffff) || (param_2 <= *param_1)) {
    uVar2 = param_1[1];
  }
  else {
    iVar3 = 0;
    while( true ) {
      puVar1 = param_1 + iVar3 * 2;
      uVar5 = (uint)*puVar1;
      if (uVar5 == 0xffff) break;
      if (param_2 < uVar5) {
        iVar3 = uVar5 - puVar1[-2];
        iVar4 = (param_2 - puVar1[-2]) * ((int)(short)puVar1[1] - (int)(short)puVar1[-1]);
        if (iVar3 != 0) {
          if (iVar4 == -0x80000000 && iVar3 == -1) {
            iVar4 = 0;
          }
          else {
            iVar4 = iVar4 / iVar3;
          }
        }
        uVar2 = puVar1[-1] + (short)iVar4;
        goto LAB_000d1eda;
      }
      iVar3 = iVar3 + 1;
    }
    uVar2 = puVar1[-1];
  }
LAB_000d1eda:
  *param_3 = uVar2;
  return;
}

void f33_return_only_stub_35c36(void)

{
  return;
}

bool FUN_00095514(short param_1,undefined1 *param_2)

{
  if (param_1 == 0) {
    *param_2 = DAT_febe5d23;
  }
  return param_1 != 0;
}

void FUN_00073424(undefined4 *param_1,undefined4 *param_2)

{
  *param_1 = *param_2;
  *(undefined2 *)(param_1 + 1) = *(undefined2 *)(param_2 + 3);
  param_1[2] = param_2[1];
  param_1[3] = param_2[2];
  return;
}

void f33_return_only_stub_b1d9e(void)

{
  return;
}

void FUN_00093154(undefined1 *param_1,undefined1 param_2,undefined1 param_3)

{
  param_1[1] = param_2;
  *param_1 = 0x7f;
  param_1[2] = param_3;
  return;
}

uint f33_nvm_queue_key(ushort logical_handle)

{
  return (uint)f33_nvm_logical_descriptors[logical_handle].queue_key;
}

undefined4 FUN_00073978(uint *param_1)

{
  if (f33_nvm_zero_handle_operation.operation != 0x9da70ae7) {
    *param_1 = f33_nvm_zero_handle_operation.operation;
    *(ushort *)(param_1 + 1) = f33_nvm_zero_handle_operation.logical_handle;
    param_1[2] = (uint)f33_nvm_zero_handle_operation.buffer_08;
    param_1[3] = (uint)f33_nvm_zero_handle_operation.buffer_0c;
    return 0;
  }
  return 1;
}

F33DidPublicationMetadata * f33_get_did_publication_metadata(ushort *count)

{
  *count = 0xf2;
  return f33_did_publication_metadata;
}

void FUN_00073e54(void)

{
  uint uVar1;
  undefined1 local_c;
  undefined1 uStack_b;
  undefined2 uStack_a;
  
  uStack_a = 0xffff;
  local_c = 0xff;
  uStack_b = 0xff;
  uVar1 = FUN_000769a6(&uStack_a,&local_c,&uStack_b);
  if ((uVar1 & 1) != 0) {
    FUN_00072108(4);
  }
  if ((uVar1 >> 2 & 1) != 0) {
    FUN_00072108(5);
  }
  return;
}

uchar FUN_000769a6(undefined2 *param_1,undefined1 *param_2,undefined1 *param_3)

{
  *param_1 = DAT_febf6b70;
  *param_2 = DAT_febf6b74;
  *param_3 = DAT_febf6b75;
  return f33_nvm_physical_attempt_flags;
}

ushort f33_dcm_count_receiving_slots(void)

{
  uint uVar1;
  ushort uVar2;
  
  uVar2 = 0;
  uVar1 = 0;
  do {
    if (f33_dcm_receive_buffer_state[uVar1].receiving == '\x01') {
      uVar2 = uVar2 + 1;
    }
    uVar1 = uVar1 + 1;
  } while (uVar1 < 3);
  return uVar2;
}

void f33_clear_diagnostic_supplement(uchar *destination)

{
  uchar *puVar1;
  uint uVar2;
  
  uVar2 = 0;
  do {
    puVar1 = destination + uVar2 * 4;
    uVar2 = uVar2 + 1;
    puVar1[0] = '\0';
    puVar1[1] = '\0';
    puVar1[2] = '\0';
    puVar1[3] = '\0';
  } while (uVar2 < 0x12);
  return;
}

void f33_return_only_stub_796ba(void)

{
  return;
}

void FUN_000d1194(int param_1,int *param_2)

{
  if (param_1 + 0x7fffffff < 0 == (-1 < param_1 && param_1 + 0x7fffffff < 0) &&
      param_1 != -0x7fffffff) {
    if (param_1 < 0) {
      param_1 = -param_1;
    }
  }
  else {
    param_1 = 0x7fffffff;
  }
  *param_2 = param_1;
  return;
}

undefined4 FUN_00055836(short param_1,int param_2,short *param_3)

{
  undefined4 uVar1;
  
  uVar1 = 0;
  if ((param_2 != 0) && (param_1 == *param_3)) {
    FUN_0006a574(param_3[0x23], ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
    uVar1 = 2;
  }
  return uVar1;
}

void FUN_0007e3bc(void)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = (uint)DAT_00021c6e;
  for (uVar1 = 0; uVar1 < uVar2; uVar1 = uVar1 + 1 & 0xff) {
    f33_com_tx_pending_and_group_state[uVar1 + 5] = '\x02';
    f33_com_tx_pending_and_group_state[uVar1 + 4] = '\x02';
    f33_com_tx_pending_and_group_state[uVar1 + 3] = '\0';
  }
  return;
}

void FUN_0006b7d2(undefined1 *param_1)

{
  *param_1 = 0;
  *(undefined2 *)(param_1 + 2) = 0;
  *(undefined2 *)(param_1 + 4) = 0;
  *(undefined2 *)(param_1 + 6) = 0;
  return;
}

undefined1 FUN_000813e4(uint param_1)

{
  undefined *puVar1;
  uint uVar2;
  undefined1 uVar3;
  int iVar4;
  
  puVar1 = ((undefined *)camry_host_ptr((uint32_t)(param_1 & 0xf800)));
  param_1 = param_1 & 0x7ff;
  uVar3 = 0xff;
  iVar4 = 0;
  if ((((((uintptr_t)(puVar1)==(uintptr_t)((undefined *)0x0)) || (iVar4 = 1,(uintptr_t)(puVar1)==(uintptr_t)(((undefined *)camry_host_ptr((uint32_t)(0x6000)))))) ||
       (iVar4 = 2,(uintptr_t)(puVar1)==(uintptr_t)(((undefined *)camry_host_ptr((uint32_t)(0x800)))))) ||
      ((iVar4 = 3,(uintptr_t)(puVar1)==(uintptr_t)(((undefined *)camry_host_ptr(0xb800u)))|| (iVar4 = 4,(uintptr_t)(puVar1)==(uintptr_t)(((undefined *)camry_host_ptr((uint32_t)(0xc000)))))))) ||
     (iVar4 = 5,(uintptr_t)(puVar1)==(uintptr_t)(((undefined *)camry_host_ptr((uint32_t)(0xf800)))))) {
    uVar2 = (uint)(ushort)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x21a48u + (uint32_t)(iVar4) * 2u))));
    if ((uVar2 <= param_1) &&
       ((int)(param_1 - ((*((ushort *)camry_host_ptr((uint32_t)((int)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21a0cu + (uint32_t)(iVar4) * 4u)))) + 0x10)))) + uVar2)) < 0)) {
      uVar3 = (*((undefined1 *)camry_host_ptr((uint32_t)((param_1 - uVar2 & 0xffff) * 8 + *(int *)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21a0cu + (uint32_t)(iVar4) * 4u)))) + 5))));
    }
  }
  return uVar3;
}

void FUN_000d1cf6(int param_1,int param_2,int param_3,int *param_4)

{
  if (param_2 - param_1 < 0 != (param_2 < 0 != param_1 < 0 && param_1 < 0 == param_2 - param_1 < 0))
  {
    param_1 = param_2;
  }
  if (param_3 - param_1 < 0 == (param_3 < 0 != param_1 < 0 && param_1 < 0 == param_3 - param_1 < 0)
      && param_3 != param_1) {
    param_1 = param_3;
  }
  *param_4 = param_1;
  return;
}

void FUN_000cfea4(char param_1,short *param_2)

{
  undefined *puVar1;
  
  if (param_1 != DAT_febecbed) {
    *param_2 = 0;
    if (param_1 == '\0') {
      DAT_febecbf6 = 0;
      DAT_febecbfa = 0;
      DAT_febecbfc = 0;
      return;
    }
    puVar1 = ((void *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb148cu + (uint32_t)(DAT_febeac3c & 1) * 4u)))))));
    if (param_1 == '\x01') {
      DAT_febecbf6 = *(undefined2 *)(puVar1 + 0x36);
    }
    else if (param_1 == '\x02') {
      DAT_febecbf6 = *(undefined2 *)(puVar1 + 0x38);
    }
    else {
      DAT_febecbf6 = *(undefined2 *)(puVar1 + 0x3a);
    }
    DAT_febecbfa = DAT_febecbf6;
    DAT_febecbfc = DAT_febecbf6;
    *param_2 = *param_2 + 1;
  }
  return;
}

undefined1 FUN_000b6a28(void)

{
  return DAT_000aec5d;
}

void f33_set_direct_output_codes_bank1(ushort *codes)

{
  f33_direct_output_codes_bank1[0] = *codes;
  f33_direct_output_codes_bank1[1] = codes[1];
  f33_direct_output_codes_bank1[2] = codes[2];
  return;
}

void f33_request_direct_output_bank1(void)

{
  f33_direct_output_request_enables[1] = 'Z';
  return;
}

int f33_interpolate_unsigned_axis_sentinel_curve(ushort *points,ushort input)

{
  ushort *puVar1;
  int iVar2;
  uint uVar3;
  int iVar4;
  uint uVar5;
  
  uVar3 = (uint)input;
  if ((*points != 0xffff) && (*points < uVar3)) {
    iVar2 = 0;
    while( true ) {
      puVar1 = points + iVar2 * 2;
      uVar5 = (uint)*puVar1;
      if (uVar5 == 0xffff) {
        return (int)(short)puVar1[-1];
      }
      if (uVar3 <= uVar5) break;
      iVar2 = iVar2 + 1;
    }
    iVar2 = uVar5 - puVar1[-2];
    iVar4 = (uVar3 - puVar1[-2]) * ((int)(short)puVar1[1] - (int)(short)puVar1[-1]);
    if (iVar2 != 0) {
      if (iVar4 == -0x80000000 && iVar2 == -1) {
        iVar4 = 0;
      }
      else {
        iVar4 = iVar4 / iVar2;
      }
    }
    return (int)(short)(puVar1[-1] + (short)iVar4);
  }
  return (int)(short)points[1];
}

void thunk_FUN_0008b134(void)

{
  FUN_0008b134();
  return;
}

void FUN_0008b134(void)

{
  f33_app_programming_local_word = 0;
  DAT_febf3b1c = 1;
  DAT_febf3b1b = 1;
  DAT_febf3b1a = 0;
  f33_app_programming_pending_latch = '\0';
  f33_app_programming_admission_latched = '\0';
  DAT_febf3b1d = 0xff;
  return;
}

void FUN_000cf56a(void)

{
  undefined1 uVar1;
  undefined1 uVar2;
  undefined1 uVar3;
  undefined1 uVar4;
  undefined1 uVar5;
  undefined1 uVar6;
  
  uVar6 = DAT_febecb58;
  uVar5 = DAT_febecb57;
  uVar4 = DAT_febecb3a;
  uVar3 = DAT_febecafd;
  uVar2 = DAT_febec862;
  uVar1 = DAT_febec834;
  FUN_000cf4da(0,DAT_febecb57);
  FUN_000cf4f8(0,uVar5,uVar3);
  FUN_000cf51c(0,uVar5,uVar4);
  FUN_000cf4da(1,uVar6);
  FUN_000cf4f8(1,uVar6,uVar3);
  FUN_000cf51c(1,uVar6,uVar4);
  FUN_000cf4da(2,uVar2);
  FUN_000cf4f8(2,1,uVar1);
  FUN_000cf51c(2,uVar2,uVar4);
  return;
}

void FUN_000cf51c(uint param_1,char param_2,char param_3)

{
  ushort uVar1;
  char cVar2;
  
  param_1 = param_1 & 0xff;
  if (((param_2 == '\x01') && (param_3 == '\x01')) && (param_1 < 3)) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebecb4eu + (uint32_t)(param_1 * 2) * 1u)))) = 0xa5;
    cVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebecb54u + (uint32_t)(param_1) * 1u))));
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebecb4fu + (uint32_t)(param_1 * 2) * 1u)))) = 0;
    if (cVar2 == '\0') {
      uVar1 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebecb3cu + (uint32_t)(param_1) * 2u))));
      if (uVar1 < 0xff) {
        (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebecb3cu + (uint32_t)(param_1) * 2u)))) = uVar1 + 1;
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebecb54u + (uint32_t)(param_1) * 1u)))) = 0x5a;
      }
    }
  }
  return;
}

void FUN_000cf4da(uint param_1,char param_2)

{
  int iVar1;
  
  if ((param_2 == '\x01') && ((param_1 & 0xff) < 3)) {
    iVar1 = (param_1 & 0xff) * 2;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebecb42u + (uint32_t)(iVar1) * 1u)))) = 0xa5;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebecb43u + (uint32_t)(iVar1) * 1u)))) = 0;
  }
  return;
}

void FUN_000cf4f8(uint param_1,char param_2,char param_3)

{
  int iVar1;
  
  if (((param_2 == '\x01') && (param_3 == '\x01')) && ((param_1 & 0xff) < 3)) {
    iVar1 = (param_1 & 0xff) * 2;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebecb48u + (uint32_t)(iVar1) * 1u)))) = 0xa5;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebecb49u + (uint32_t)(iVar1) * 1u)))) = 0;
  }
  return;
}

void FUN_00070152(int param_1,int param_2,int *param_3)

{
  if (param_2 - param_1 < 0 == (param_2 < 0 != param_1 < 0 && param_1 < 0 == param_2 - param_1 < 0)
      && param_2 != param_1) {
    param_1 = param_2;
  }
  *param_3 = param_1;
  return;
}

void FUN_00070674(int param_1,int param_2,int *param_3)

{
  int iVar1;
  
  if (param_1 < 1) {
    if ((param_2 < 1) &&
       (iVar1 = -0x7fffffff - param_1,
       iVar1 - param_2 < 0 == (iVar1 < 0 != param_2 < 0 && param_2 < 0 == iVar1 - param_2 < 0) &&
       iVar1 != param_2)) {
      param_2 = -0x7fffffff;
      goto LAB_000706a8;
    }
  }
  else if ((0 < param_2) &&
          (iVar1 = (0x7fffffff - param_1) - param_2,
          iVar1 < 0 != (0x7fffffff - param_1 < 0 != param_2 < 0 && param_2 < 0 == iVar1 < 0))) {
    param_2 = 0x7fffffff;
    goto LAB_000706a8;
  }
  param_2 = param_2 + param_1;
LAB_000706a8:
  *param_3 = param_2;
  return;
}

uint f33_nvm_snapshot_scheduler_operation(F33NvmOperation *output)

{
  ushort uVar1;
  uint uVar2;
  
  uVar1 = f33_nvm_scheduler_operation.logical_handle;
  uVar2 = (uint)(f33_nvm_scheduler_operation.operation != 0x9da70ae7);
  if (f33_nvm_scheduler_operation.operation != 0x9da70ae7) {
    if (((f33_nvm_scheduler_phase == '\b') || (f33_nvm_scheduler_phase == '\x10')) ||
       (f33_nvm_scheduler_phase == ' ')) {
      uVar2 = 2;
    }
    output->operation = f33_nvm_scheduler_operation.operation;
    output->logical_handle = uVar1;
    output->buffer_08 = f33_nvm_scheduler_operation.buffer_08;
    output->buffer_0c = f33_nvm_scheduler_operation.buffer_0c;
  }
  return uVar2;
}

bool FUN_0000526a(undefined4 param_1,undefined1 param_2,undefined1 param_3)

{
  int iVar1;
  
  iVar1 = FUN_00005060(((char *)camry_host_ptr((uint32_t)(param_1))), param_2, param_3);
  return iVar1 == 0;
}

char FUN_00007262(char param_1)

{
  if (param_1 != -1) {
    return param_1 + '\x01';
  }
  return -1;
}

void f33_initialize_thermal_shutdown_counter(void)

{
  uint32_t puVar1;
  undefined2 uStack_6;
  
  puVar1 = 0xfebeb800u;
  FUN_0007025c(((undefined *)camry_host_ptr(0x30e78u)),0,&uStack_6);
  (*((undefined2 *)camry_host_ptr((uint32_t)((int)(0xffffb08cu + (uint32_t)((int)puVar1)))))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)((int)(0xffffb08eu + (uint32_t)((int)puVar1)))))) = uStack_6;
  return;
}

void FUN_000320c2(void)

{
  uint uVar1;
  uint uVar2;
  
  if ((DAT_febe6890 == '\0') && (DAT_febe68b4 != -1)) {
    uVar2 = 0;
    do {
      uVar1 = uVar2 + 1;
      (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe689au + (uint32_t)(uVar2) * 2u)))) = *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe68aau)) + uVar2 * 2);
      (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe68a0u + (uint32_t)(uVar2) * 2u)))) = *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe68b0u)) + uVar2 * 2);
      uVar2 = uVar1;
    } while (uVar1 < 2);
    DAT_febe6890 = 'Z';
  }
  return;
}

void FUN_000320fe(uint param_1,undefined2 param_2)

{
  (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe689au + (uint32_t)(param_1 & 0xff) * 2u)))) = param_2;
  return;
}

void FUN_00032146(uint param_1,undefined2 param_2)

{
  (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe68a0u + (uint32_t)(param_1 & 0xff) * 2u)))) = param_2;
  return;
}

void FUN_00032c86(void)

{
  DAT_febe6958 = 0;
  DAT_febe6959 = 0;
  DAT_febe695c = 0;
  DAT_febe695a = 0;
  return;
}

void thunk_FUN_00032c86(void)

{
  FUN_00032c86();
  return;
}

void f33_begin_six_channel_fit(void)

{
  f33_six_channel_fit_work.state = '\0';
  f33_six_channel_fit_work.active = 'Z';
  return;
}

void f33_reset_published_fit_coefficients(void)

{
  f33_published_fit_coefficients.first_center[0] = 0x8000;
  f33_published_fit_coefficients.first_center[1] = 0x8000;
  f33_published_fit_coefficients.first_center[2] = 0x8000;
  f33_published_fit_coefficients.first_center[3] = 0x8000;
  f33_published_fit_coefficients.first_center[4] = 0x8000;
  f33_published_fit_coefficients.first_center[5] = 0x8000;
  f33_published_fit_coefficients.first_gain[0] = 0x8000;
  f33_published_fit_coefficients.first_gain[1] = 0x8000;
  f33_published_fit_coefficients.first_gain[2] = 0x8000;
  f33_published_fit_coefficients.first_gain[3] = 0x8000;
  f33_published_fit_coefficients.first_gain[4] = 0x8000;
  f33_published_fit_coefficients.first_gain[5] = 0x8000;
  f33_published_fit_coefficients.second_gain[0] = 0x8000;
  f33_published_fit_coefficients.second_gain[1] = 0x8000;
  f33_published_fit_coefficients.second_gain[2] = 0x8000;
  f33_published_fit_coefficients.second_gain[3] = 0x8000;
  f33_published_fit_coefficients.second_gain[4] = 0x8000;
  f33_published_fit_coefficients.second_gain[5] = 0x8000;
  f33_published_fit_coefficients.second_center[0] = 0;
  f33_published_fit_coefficients.second_center[1] = 0;
  f33_published_fit_coefficients.second_center[2] = 0;
  f33_published_fit_coefficients.second_center[3] = 0;
  f33_published_fit_coefficients.second_center[4] = 0;
  f33_published_fit_coefficients.second_center[5] = 0;
  f33_published_fit_coefficients.component_angle[0] = 0x2000;
  f33_published_fit_coefficients.component_angle[1] = 0x2000;
  f33_published_fit_coefficients.component_angle[2] = 0x2000;
  return;
}

void FUN_00033d32(void)

{
  DAT_febe6a5c = 0;
  DAT_febe6a5d = 0;
  return;
}

uint f33_request_six_channel_fit(void)

{
  DAT_febe6a5c = 0x5a;
  return 0;
}

void f33_initialize_mode600_stimulus_fit(void)

{
  f33_mode600_stimulus_fit_work.state = '\x10';
  f33_mode600_stimulus_fit_work.stimulus_valid = '\0';
  f33_mode600_stimulus_fit_work.positive_mean = 0;
  f33_mode600_stimulus_fit_work.negative_mean = 0;
  f33_mode600_stimulus_fit_work.stimulus = 0;
  f33_mode600_stimulus_fit_work.hold_count = 0;
  f33_mode600_stimulus_fit_work.sample_count = 0;
  f33_mode600_stimulus_fit_work.folded_angle_sum = 0;
  f33_mode600_stimulus_fit_work.signed_component_sum = 0;
  return;
}

void f33_cancel_mode600_stimulus_fit(void)

{
  f33_mode600_stimulus_fit_work.active = '\0';
  f33_mode600_stimulus_fit_work.stimulus_valid = '\0';
  f33_mode600_stimulus_fit_work.state = '\x10';
  return;
}

uint f33_begin_mode600_stimulus_fit(void)

{
  f33_mode600_stimulus_fit_work.active = 'Z';
  f33_initialize_mode600_stimulus_fit();
  return 0;
}

void FUN_00034c48(void)

{
  DAT_febe6acc = 0;
  DAT_febe6ac8 = 0;
  DAT_febe6ac9 = 0;
  DAT_febe6aca = 0;
  return;
}

undefined4 FUN_00035532(void)

{
  if ((((DAT_febe6ad2 == f33_learned_quad[0]) && (DAT_febe6ad4 == f33_learned_quad[1])) &&
      (DAT_febe6ad6 == f33_learned_quad[2])) && (DAT_febe6ad8 == f33_learned_quad[3])) {
    return 0;
  }
  return 0x5a;
}

void FUN_00035568(void)

{
  DAT_febe6ad2 = f33_learned_quad[0];
  DAT_febe6ad4 = f33_learned_quad[1];
  DAT_febe6ad6 = f33_learned_quad[2];
  DAT_febe6ad8 = f33_learned_quad[3];
  return;
}

void FUN_00035586(void)

{
  DAT_febe6ad2 = 0x800;
  DAT_febe6ad4 = 0x800;
  DAT_febe6ad6 = 0x800;
  DAT_febe6ad8 = 0x800;
  return;
}

void FUN_00035772(ushort param_1,ushort param_2,ushort param_3,ushort param_4)

{
  f33_learned_quad[0] = param_1;
  f33_learned_quad[1] = param_2;
  f33_learned_quad[2] = param_3;
  f33_learned_quad[3] = param_4;
  return;
}

bool FUN_00035a06(void)

{
  int iVar1;
  ushort uVar2;
  ushort uVar3;
  char cVar4;
  char cVar5;
  char cVar6;
  ushort uVar7;
  bool bVar8;
  short sStack_1e;
  
  uVar7 = DAT_febee892;
  cVar6 = DAT_febee81a;
  cVar5 = DAT_febe80a5;
  cVar4 = DAT_febe80a0;
  uVar3 = DAT_febe66b8;
  uVar2 = DAT_febe6764 & 0x81ff;
  FUN_0006a522((int)DAT_febe66a8,&sStack_1e);
  if ((((cVar6 == '\x01') && (DAT_00030e32 <= uVar3)) && (uVar7 <= DAT_00030e34)) &&
     (((cVar5 == '\0' && (cVar4 == '\0')) &&
      (iVar1 = sStack_1e + -0x200, ((iVar1 < 0) || (sStack_1e < 0)))))) {
    bVar8 = uVar2 == 0;
  }
  else {
    bVar8 = false;
  }
  return bVar8;
}

undefined4 FUN_00035a96(void)

{
  DAT_febe6ae2 = 0x11;
  return 2;
}

void FUN_00035aa2(void)

{
  if ((((DAT_febe6af0 != -1) && (DAT_febe6af0 != -0x5aa5a55b)) && (((int8_t)DAT_febe6add) != -0x78)) &&
     ((DAT_febe6add != '\x11' && (DAT_febe6ae2 != '\x11')))) {
    DAT_febe6ae2 = '\"';
  }
  return;
}

void FUN_00035ad6(void)

{
  if (((int8_t)DAT_febe6add) == -0x78) {
    DAT_febe6add = '\0';
  }
  return;
}

void f33_fill_constant_block_35aea(void)

{
  DAT_febe5f58 = 0;
  DAT_febe5f59 = 0;
  DAT_febe5f5a = 0;
  DAT_febe5f5e = DAT_0002bd02;
  DAT_febe5f60 = DAT_0002bd02;
  DAT_febe5f5b = 0;
  DAT_febe5f5c = 0;
  DAT_febe5f5d = 0;
  DAT_febe5f62 = DAT_0002bd06;
  DAT_febe5f64 = DAT_0002bd06;
  return;
}

undefined4 FUN_00035b12(undefined4 param_1,undefined4 param_2,uint param_3)

{
  undefined2 uVar1;
  byte bVar2;
  undefined4 uVar3;
  
  uVar1 = DAT_0002bd02;
  bVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5f58u + (uint32_t)(param_3 & 0xff) * 1u))));
  uVar3 = 0;
  if (DAT_0002bd00 <= bVar2) {
    uVar3 = 0x5a;
    bVar2 = 0;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5f58u + (uint32_t)(param_3 & 0xff) * 1u)))) = bVar2;
  (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe5f5eu + (uint32_t)(param_3 & 0xff) * 2u)))) = uVar1;
  return uVar3;
}

undefined4 FUN_00035b44(undefined4 param_1,undefined4 param_2,uint param_3)

{
  undefined2 uVar1;
  byte bVar2;
  undefined4 uVar3;
  
  uVar1 = DAT_0002bd06;
  param_3 = param_3 & 0xff;
  bVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5f5au + (uint32_t)(param_3) * 1u))));
  uVar3 = 0;
  if (DAT_0002bd01 <= bVar2) {
    uVar3 = 0x5a;
    bVar2 = 0;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5f5au + (uint32_t)(param_3) * 1u)))) = bVar2;
  (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe5f62u + (uint32_t)(param_3) * 2u)))) = uVar1;
  return uVar3;
}

void FUN_00035c02(void)

{
  DAT_febe5f6c = 0;
  DAT_febe5f68 = 0;
  DAT_febe5f6a = 0;
  DAT_febe5f69 = 0;
  return;
}

void FUN_00035c10(void)

{
  if ((DAT_0002bd08 <= DAT_febe5f6a) ||
     (DAT_febe5f6a = DAT_febe5f6a + 1, DAT_0002bd08 <= DAT_febe5f6a)) {
    DAT_febe5f69 = 0;
  }
  DAT_febe5f68 = 0;
  return;
}

void FUN_00035c38(void)

{
  FUN_00035c10();
  f33_return_only_stub_35c36();
  return;
}

void f33_update_limit_budget_branch0(void)

{
  int iVar1;
  int iVar2;
  
  if ((DAT_febe71ec & 1) != 0) {
    DAT_febe6afc = 0;
    DAT_febe6b00 = 0;
    DAT_febe6b04 = 0;
    return;
  }
  iVar1 = DAT_00031938;
  if ((DAT_febe71ec >> 1 & 1) != 0) {
    iVar1 = DAT_0003193c;
  }
  iVar2 = (int)DAT_febe62d6;
  DAT_febe6b04 = iVar1 - (int)DAT_febe62bc * (int)DAT_febe62d4;
  if (iVar2 < 0) {
    iVar2 = -iVar2;
  }
  else {
    iVar1 = DAT_0003191c;
    if (iVar2 == 0) goto LAB_00035d38;
  }
  iVar1 = DAT_febe6b04;
  if (iVar2 != 0) {
    if (DAT_febe6b04 == -0x80000000 && iVar2 == -1) {
      iVar1 = -0x80000000;
    }
    else {
      iVar1 = DAT_febe6b04 / iVar2;
    }
  }
LAB_00035d38:
  iVar2 = DAT_0003191c;
  if (iVar1 - DAT_0003191c < 0 !=
      (iVar1 < 0 != DAT_0003191c < 0 && DAT_0003191c < 0 == iVar1 - DAT_0003191c < 0)) {
    iVar2 = iVar1;
  }
  DAT_febe6afc = -DAT_0003191c;
  if (iVar2 + DAT_0003191c < 0 ==
      (iVar2 < 0 != DAT_febe6afc < 0 && DAT_febe6afc < 0 == iVar2 + DAT_0003191c < 0)) {
    DAT_febe6afc = iVar2;
  }
  DAT_febe6b00 = (int)DAT_febe62bc * (int)DAT_febe62d4;
  return;
}

void f33_reset_owner9_budget_limit_state(void)

{
  DAT_febe6b14 = 0;
  DAT_febe6b15 = 0;
  DAT_febe6b1e = 0;
  DAT_febe6b18 = DAT_0003192a;
  DAT_febe6b24 = (uint)DAT_0003192a << 0x10;
  DAT_febe6b1a = DAT_0003192a;
  DAT_febe6b16 = DAT_0003192a;
  DAT_febe6b28 = (uint)DAT_0003192a << 0x10;
  DAT_febe6b1c = 0;
  return;
}

void f33_initialize_terminal_output_ramp(void)

{
  DAT_febe6b2c = 0;
  DAT_febe6b2d = 0;
  DAT_febe6b2e = 0;
  DAT_febe6b30 = 0;
  return;
}

undefined1 FUN_00036066(byte param_1,short param_2)

{
  int iVar1;
  undefined1 uVar2;
  int iVar3;
  
  if ((param_1 & 3) == 0) {
    uVar2 = 1;
  }
  else {
    iVar1 = (int)param_2;
    if (DAT_febe6b2e == 0) {
      if (iVar1 + 0x7fff < 0 == (-1 < iVar1 && iVar1 + 0x7fff < 0) && iVar1 != -0x7fff) {
        if (iVar1 < 0) {
          iVar1 = (int)-param_2;
        }
      }
      else {
        iVar1 = 0x7fff;
      }
      iVar3 = (int)DAT_00030e58;
      uVar2 = iVar1 - iVar3 < 0 == (iVar1 < 0 != iVar3 < 0 && iVar3 < 0 == iVar1 - iVar3 < 0) &&
              iVar1 != iVar3;
    }
    else {
      uVar2 = 2;
    }
    DAT_febe6b2e = DAT_febe6b2e | param_1;
  }
  return uVar2;
}

void f33_request_terminal_output_ramp(void)

{
  DAT_febe6b2c = 0x5a;
  return;
}

void f33_cancel_terminal_output_ramp(void)

{
  DAT_febe6b2c = 0;
  return;
}

void FUN_000360ce(void)

{
  DAT_febe6798 = 0;
  DAT_febe6799 = DAT_00030e70;
  return;
}

void FUN_000360e0(void)

{
  int iVar1;
  bool bVar2;
  char cVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  
  iVar5 = -(int)DAT_febe64e2;
  cVar3 = DAT_00030e70;
  if ((DAT_febe64cc & 0x40004) == 0) {
    DAT_febe6798 = 0;
  }
  else {
    iVar6 = (int)DAT_febe6770;
    iVar7 = (int)DAT_00030e72;
    if (((iVar6 - iVar7 < 0 == (iVar6 < 0 != iVar7 < 0 && iVar7 < 0 == iVar6 - iVar7 < 0) &&
          iVar6 != iVar7) &&
        (iVar4 = (int)DAT_00030e74, iVar1 = iVar5 + -iVar4,
        iVar1 < 0 == (iVar5 < 0 != iVar4 < 0 && iVar4 < 0 == iVar1 < 0) &&
        -iVar4 != (int)DAT_febe64e2)) ||
       ((iVar6 + iVar7 < 0 != (iVar6 < 0 != -iVar7 < 0 && -iVar7 < 0 == iVar6 + iVar7 < 0) &&
        (iVar6 = iVar5 + DAT_00030e74, bVar2 = -(int)DAT_00030e74 < 0,
        iVar6 < 0 != (iVar5 < 0 != bVar2 && bVar2 == iVar6 < 0))))) {
      if (DAT_febe6799 == '\0') {
        DAT_febe6798 = 1;
        cVar3 = '\0';
      }
      else {
        cVar3 = DAT_febe6799 + -1;
      }
    }
  }
  DAT_febe6799 = cVar3;
  return;
}

void f33_reset_bank0_current_reference_feedback(void)

{
  f33_current_reference_feedback[0].request = 0;
  f33_current_reference_feedback[0].error = 0;
  f33_current_reference_feedback[0].previous_error = 0;
  f33_current_reference_feedback[0].opaque_14 = 0;
  f33_current_reference_feedback[0].request_before_global_clamp = 0;
  f33_current_reference_feedback[0].current_gain = 0;
  f33_current_reference_feedback[0].previous_gain = 0;
  f33_current_reference_feedback[0].retained_transient_delta = 0;
  f33_current_reference_feedback[0].saturated_base_plus_delta = 0;
  return;
}

void f33_initialize_bank0_current_reference_feedback(void)

{
  f33_reset_bank0_current_reference_feedback();
  return;
}

void f33_initialize_bank1_current_reference_feedback(void)

{
  f33_reset_bank1_current_reference_feedback();
  return;
}

void FUN_000368aa(void)

{
  DAT_febe6be4 = 0;
  return;
}

void f33_map_phase_compensation_gain(void)

{
  uint uVar1;
  uint uVar2;
  
  uVar1 = (uint)DAT_febe6e0a;
  if ((int)(uVar1 + 0x7fff) < 0 == (-1 < (int)uVar1 && (int)(uVar1 + 0x7fff) < 0) &&
      uVar1 != 0xffff8001) {
    if ((int)uVar1 < 0) {
      uVar1 = -uVar1;
    }
  }
  else {
    uVar1 = 0x7fff;
  }
  uVar2 = (uVar1 & 0xffff) >> 4;
  if (uVar2 < 0x7f) {
    DAT_febe6be4 = f33_phase_compensation_gain_curve[uVar2].y +
                   (short)((int)((uVar1 & 0xf) *
                                ((uint)f33_phase_compensation_gain_curve[uVar2 + 1].y -
                                (uint)f33_phase_compensation_gain_curve[uVar2].y)) / 0x10);
  }
  else {
    DAT_febe6be4 = 0x400;
  }
  return;
}

void FUN_00036910(void)

{
  f33_regulator_output_envelopes[0].second_saturation = '\0';
  f33_regulator_output_envelopes[0].first_saturation = '\0';
  f33_regulator_output_envelopes[0].first = 0;
  f33_regulator_output_envelopes[0].second = 0;
  f33_regulator_output_envelopes[0].first_unclipped = 0;
  f33_regulator_output_envelopes[0].second_unclipped = 0;
  f33_regulator_output_envelopes[0].raw_cubic = f33_regulator_output_envelope_calibrations[0].base;
  f33_regulator_output_envelopes[0].selected_second_limit =
       (short)(f33_regulator_output_envelope_calibrations[0].base / 0x800);
  f33_regulator_output_envelopes[0].second_upper =
       f33_regulator_output_envelopes[0].selected_second_limit;
  f33_regulator_output_envelopes[0].combined_second = 0;
  f33_regulator_output_envelopes[0].reset_cleared_status = '\0';
  f33_regulator_output_envelopes[0].lower_before_clamp =
       f33_regulator_output_envelope_calibrations[0].base -
       f33_regulator_output_envelope_calibrations[0].band_width;
  f33_regulator_output_envelopes[0].retained_24 = 0x400;
  f33_regulator_output_envelopes[0].retained_28 = 0x400;
  f33_regulator_output_envelopes[0].second_lower =
       (short)((f33_regulator_output_envelope_calibrations[0].base -
               f33_regulator_output_envelope_calibrations[0].band_width) / 0x800);
  return;
}

void f33_fill_constant_block_370d6(void)

{
  DAT_febe6c70 = 0;
  DAT_febe6c72 = 0;
  DAT_febe6c74 = 0;
  DAT_febe6c76 = 0;
  DAT_febe6c78 = 0;
  return;
}

void f33_fill_constant_block_37218(void)

{
  DAT_febe6c7c = 0;
  DAT_febe6c7e = 0;
  DAT_febe6c80 = 0;
  DAT_febe6c82 = 0;
  DAT_febe6c8c = 0;
  return;
}

void f33_fill_constant_block_373be(void)

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

int FUN_000373e6(void)

{
  int iVar1;
  int iVar2;
  
  iVar1 = (int)DAT_febe6d7e - (int)DAT_febe6d76;
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

uint FUN_00037418(short param_1)

{
  uint uVar1;
  
  if ((((f33_regulator_output_envelopes[0].second < 0) ||
       (f33_regulator_output_envelopes[0].second_saturation != '\x01')) &&
      ((-1 < f33_regulator_output_envelopes[1].second ||
       (f33_regulator_output_envelopes[1].second_saturation != '\x02')))) || (param_1 < 0)) {
    if (((f33_regulator_output_envelopes[0].second < 0) &&
        (f33_regulator_output_envelopes[0].second_saturation == '\x02')) ||
       ((-1 < f33_regulator_output_envelopes[1].second &&
        (f33_regulator_output_envelopes[1].second_saturation == '\x01')))) {
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

void f33_fill_constant_block_3759c(void)

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

int FUN_000375c2(void)

{
  int iVar1;
  
  iVar1 = DAT_febe6d7c - DAT_febe6d78;
  if (iVar1 + -0x7fff < 0 == (iVar1 < 0 && -1 < iVar1 + -0x7fff)) {
    iVar1 = 0x7fff;
  }
  if (iVar1 + 0x7fff < 0 != (-1 < iVar1 && iVar1 + 0x7fff < 0)) {
    iVar1 = -0x7fff;
  }
  return (int)(short)iVar1;
}

uint FUN_000375e6(short param_1)

{
  uint uVar1;
  
  if ((((f33_regulator_output_envelopes[0].second < 0) ||
       (f33_regulator_output_envelopes[0].second_saturation != '\x01')) &&
      ((f33_regulator_output_envelopes[1].second < 0 ||
       (f33_regulator_output_envelopes[1].second_saturation != '\x01')))) || (param_1 < 0)) {
    if (((f33_regulator_output_envelopes[0].second < 0) &&
        (f33_regulator_output_envelopes[0].second_saturation == '\x02')) ||
       ((f33_regulator_output_envelopes[1].second < 0 &&
        (f33_regulator_output_envelopes[1].second_saturation == '\x02')))) {
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

void f33_initialize_shared_second_axis_envelope(void)

{
  f33_shared_second_axis_envelope = DAT_000317ac;
  return;
}

void f33_map_additional_second_axis_envelope(short magnitude)

{
  uint32_t puVar1;
  undefined2 uStack_6;
  
  puVar1 = 0xfebeb800u;
  if ((DAT_febee741 == '\x11') || (DAT_febee741 == '\"')) {
    puVar1 = 0xfebeb800u;
    FUN_00070208(((short *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x31eacu + (uint32_t)(DAT_febee5c3 & 1) * 4u))))))), (int)magnitude, &uStack_6);
  }
  else {
    uStack_6 = (*((undefined2 *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x31ea4u + (uint32_t)(DAT_febee5c3 & 1) * 4u)))) + 2))));
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb4e2u + (uint32_t)((int)puVar1)))))) = uStack_6;
  return;
}

void FUN_00037920(void)

{
  DAT_febe6cf0 = 0x400;
  return;
}

void FUN_0003792a(void)

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

void FUN_00037956(void)

{
  DAT_febe6cf4 = 0x400;
  return;
}

void FUN_00037960(void)

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

void FUN_0003798c(void)

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

undefined4 FUN_000379fc(void)

{
  if (((uint)((int)DAT_febe6e12 * (int)DAT_febe6e12 + (int)DAT_febe6e14 * (int)DAT_febe6e14) <
       DAT_00031ae0) &&
     ((uint)((int)DAT_febe6e16 * (int)DAT_febe6e16 + (int)DAT_febe6e18 * (int)DAT_febe6e18) <
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

undefined4 FUN_00037a62(void)

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

void f33_initialize_phase_offset_selector(void)

{
  DAT_febe6d6d = 0;
  f33_phase_offset_selector_counter = 0;
  f33_phase_offset_selector = 'Z';
  return;
}

void f33_advance_phase_offset_selector(void)

{
  uchar uVar1;
  
  if ((f33_phase_offset_selector_period <= f33_phase_offset_selector_counter) ||
     (f33_phase_offset_selector_counter = f33_phase_offset_selector_counter + 1,
     uVar1 = f33_phase_offset_selector,
     f33_phase_offset_selector_period <= f33_phase_offset_selector_counter)) {
    f33_phase_offset_selector_counter = 0;
    uVar1 = 'Z';
    if (f33_phase_offset_selector == 'Z') {
      uVar1 = 0xa5;
    }
  }
  if (f33_phase_offset_selector_override == '3') {
    uVar1 = 'Z';
  }
  else if (f33_phase_offset_selector_override == '\"') {
    uVar1 = 0xa5;
  }
  f33_phase_offset_selector = uVar1;
  return;
}

uint f33_current_reference_curve_feedback_magnitude(void)

{
  int iVar1;
  uint uVar2;
  
  iVar1 = (int)DAT_febe6d72;
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
  if ((int)(uVar2 + 0x7fff) < 0 == (-1 < (int)uVar2 && (int)(uVar2 + 0x7fff) < 0) &&
      uVar2 != 0xffff8001) {
    if ((int)uVar2 < 0) {
      return (int)(short)-(short)iVar1;
    }
    return uVar2;
  }
  return 0x7fff;
}

short f33_scale_additional_first_current_request(short request)

{
  f33_additional_first_current_reference.previous_output =
       f33_additional_first_current_reference.output;
  f33_additional_first_current_reference.scaled_request =
       (short)(((int)f33_additional_first_current_reference.gain_q7 * (int)request) / 0x80);
  f33_additional_first_current_reference.delta =
       f33_additional_first_current_reference.scaled_request -
       f33_additional_first_current_reference.output;
  f33_additional_first_current_reference.delta_passthrough =
       f33_additional_first_current_reference.delta;
  f33_additional_first_current_reference.candidate =
       f33_additional_first_current_reference.delta + f33_additional_first_current_reference.output;
  return f33_additional_first_current_reference.delta +
         f33_additional_first_current_reference.output;
}

void FUN_000387ba(void)

{
  DAT_febe6e04 = 0;
  DAT_febe6e05 = 0;
  DAT_febe6e0a = DAT_febe6af4;
  return;
}

void f33_latch_current_feedback_and_reference_inputs(void)

{
  DAT_febe6e12 = DAT_febe6b34;
  DAT_febe6e14 = DAT_febe6b36;
  DAT_febe6e16 = DAT_febe6b38;
  DAT_febe6e18 = DAT_febe6b3a;
  DAT_febe6e28 = DAT_febe6b3c;
  DAT_febe6e2c = DAT_febe6b40;
  DAT_febe6e30 = DAT_febe6b44;
  DAT_febe6e1e = 0;
  DAT_febe6e20 = 0;
  DAT_febe6e34 = DAT_febe6b48;
  DAT_febe6e1a = f33_current_reference_feedback[0].request;
  DAT_febe6e1c = f33_current_reference_feedback[1].request;
  DAT_febe6e22 = DAT_febe6af6;
  DAT_febe6e24 = DAT_febe6af6;
  DAT_febe6e0c = f33_regulator_output_envelopes[0].first_saturation;
  DAT_febe6e0e = f33_regulator_output_envelopes[1].first_saturation;
  DAT_febe6e0d = f33_regulator_output_envelopes[0].second_saturation;
  DAT_febe6e0f = f33_regulator_output_envelopes[1].second_saturation;
  return;
}

void FUN_00038838(void)

{
  DAT_febe6e40 = 0;
  DAT_febe6e44 = 0;
  return;
}

void FUN_00038942(void)

{
  DAT_febe6e50 = 0;
  DAT_febe6e54 = 0;
  return;
}

void FUN_00038a4c(void)

{
  DAT_febe6e58 = 0;
  DAT_febe6e5a = 0;
  DAT_febe6e5c = 0;
  return;
}

void FUN_00038b5e(void)

{
  DAT_febe6e60 = 0;
  DAT_febe6e62 = 0;
  DAT_febe6e64 = 0;
  return;
}

void FUN_00038c70(void)

{
  DAT_febe6e68 = 0;
  DAT_febe6e6a = 0;
  DAT_febe6e6c = 0;
  return;
}

void FUN_00038d60(void)

{
  DAT_febe6e70 = 0;
  DAT_febe6e72 = 0;
  DAT_febe6e74 = 0;
  return;
}

uint f33_qualify_additional_current_reference_envelope(int signed_product)

{
  uint uVar1;
  
  if (((((DAT_febee741 == '\x11') || (DAT_febee741 == '\"')) && (0 < signed_product)) ||
      (DAT_febee741 == '\0')) &&
     (((DAT_febeeac0 != '\x11' || (DAT_febeeac6 < (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x31ec4u + (uint32_t)(DAT_febee5c3 & 1) * 4u)))))))))
      && ((DAT_febee740 == '\0' && (DAT_febee742 == '\0')))))) {
    uVar1 = 0x5a;
  }
  else {
    uVar1 = 0;
  }
  if (DAT_000317b0 == 'Z') {
    uVar1 = 0;
  }
  if (DAT_febeeac2 == 'Z') {
    uVar1 = 0;
  }
  return uVar1;
}

undefined4 FUN_000390d4(short param_1,short param_2)

{
  int iVar1;
  int iVar2;
  undefined4 local_8;
  
  iVar2 = (int)param_2;
  if (iVar2 == 0) {
    local_8 = 0;
  }
  else {
    iVar1 = (int)param_1 << 0xc;
    if (iVar2 != 0) {
      if (iVar1 == -0x80000000 && iVar2 == -1) {
        iVar1 = -0x80000000;
      }
      else {
        iVar1 = iVar1 / iVar2;
      }
    }
    FUN_000706ae(iVar1,0x80,&local_8);
  }
  return local_8;
}

void f33_fill_constant_block_39372(void)

{
  DAT_febe6eb2 = 0;
  DAT_febe6eb4 = 0;
  DAT_febe6eb6 = 0;
  DAT_febe6eb8 = 0;
  DAT_febe6eba = 0;
  DAT_febe6ebc = 0;
  DAT_febe6ec0 = 0;
  DAT_febe6ec4 = 0;
  DAT_febe6ec8 = 0;
  DAT_febe6ecc = 0;
  DAT_febe6ed0 = 0;
  DAT_febe6ed4 = 0;
  return;
}

void FUN_00039392(void)

{
  DAT_febe6ee0 = 0x569a;
  DAT_febe6ee2 = 0x2b4d;
  return;
}

void f33_publish_ecu_source5_thermal_limit_maps(void)

{
  uint32_t puVar1;
  int iVar2;
  undefined2 local_c;
  undefined2 uStack_a;
  
  puVar1 = 0xfebeb800u;
  iVar2 = (int)DAT_febe6eae;
  FUN_0007025c(f33_ecu_source5_current_curve_bank0,iVar2,&local_c);
  FUN_0007025c(f33_ecu_source5_current_curve_bank1,iVar2,&uStack_a);
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb6e0u + (uint32_t)((int)puVar1)))))) = local_c;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb6e2u + (uint32_t)((int)puVar1)))))) = uStack_a;
  return;
}

void FUN_000393de(void)

{
  DAT_febe6ee6 = DAT_febe6f06;
  DAT_febe6ee8 = DAT_febe6f08;
  return;
}

uint f33_scale_thermal_divisor(uint base,uint scale)

{
  uint uVar1;
  uint uVar2;
  
  uVar1 = (base & 0xffff) * (scale & 0xffff) >> 10;
  uVar2 = uVar1 & 0xffff;
  if (0xffff < uVar1) {
    uVar2 = 0xffff;
  }
  return uVar2;
}

int f33_update_nonnegative_thermal_pole(int previous,int drive,uint divisor)

{
  int iVar1;
  uint uVar2;
  int local_c;
  int iStack_8;
  
  uVar2 = divisor & 0xffff;
  if (drive < 0) {
    if ((-1 < previous) &&
       (iVar1 = (drive + 0x7fffffff) - previous,
       iVar1 < 0 != (drive + 0x7fffffff < 0 != previous < 0 && previous < 0 == iVar1 < 0))) {
      local_c = -0x7fffffff;
      goto LAB_00039472;
    }
  }
  else if ((previous < 0) &&
          (iVar1 = -(0x7fffffff - drive),
          iVar1 - previous < 0 ==
          (iVar1 < 0 != previous < 0 && previous < 0 == iVar1 - previous < 0) && iVar1 != previous))
  {
    local_c = 0x7fffffff;
    goto LAB_00039472;
  }
  local_c = drive - previous;
LAB_00039472:
  if ((uVar2 != 0) && (uVar2 != 0)) {
    if (local_c == -0x80000000 && uVar2 == 0xffffffff) {
      local_c = -0x80000000;
    }
    else {
      local_c = local_c / (int)uVar2;
    }
  }
  FUN_00070674(previous,local_c,&local_c);
  FUN_00070152(local_c,0,&iStack_8);
  return iStack_8;
}

int f33_scale_thermal_contribution(int state,short gain,short upper,short lower)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  uint uVar6;
  
  iVar3 = (int)gain;
  iVar4 = (int)upper;
  iVar5 = (int)lower;
  iVar2 = state / 0x80;
  if ((iVar2 == 0) || (iVar3 == 0)) {
    uVar6 = 0;
    goto LAB_000394fa;
  }
  if (iVar2 < 0) {
    if (-1 < iVar3) goto LAB_000394dc;
  }
  else if (iVar3 < 0) {
LAB_000394dc:
    iVar1 = (int)((ulonglong)((longlong)iVar3 * (longlong)iVar2) >> 0x20) + 1;
    if ((iVar1 < 0 != (-1 < (longlong)iVar3 * (longlong)iVar2 && iVar1 < 0)) ||
       (uVar6 = iVar2 * iVar3, uVar6 < 0x80000001)) {
      uVar6 = 0x80000001;
    }
    goto LAB_000394fa;
  }
  if ((-1 < (longlong)iVar3 * (longlong)iVar2 &&
       (int)((ulonglong)((longlong)iVar3 * (longlong)iVar2) >> 0x20) != 0) ||
     (uVar6 = iVar2 * iVar3, 0x7fffffff < (uint)(iVar2 * iVar3))) {
    uVar6 = 0x7fffffff;
  }
LAB_000394fa:
  iVar2 = (int)uVar6 / 0x1000;
  if (iVar2 - iVar4 < 0 != (iVar2 < 0 != iVar4 < 0 && iVar4 < 0 == iVar2 - iVar4 < 0) ||
      iVar2 == iVar4) {
    iVar4 = iVar2;
  }
  if (iVar4 - iVar5 < 0 == (iVar4 < 0 != iVar5 < 0 && iVar5 < 0 == iVar4 - iVar5 < 0)) {
    lower = (short)iVar4;
  }
  return (int)lower;
}

int FUN_0003975a(short param_1,short param_2)

{
  return ((int)param_2 * (int)param_1) / 0x3000;
}

int FUN_00039768(void)

{
  uint32_t puVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  int local_28;
  int iStack_24;
  
  puVar1 = 0xfebeb800u;
  iVar8 = (int)DAT_febe65b2;
  iVar7 = (int)DAT_febe65b4;
  iVar6 = (int)DAT_febe65b6;
  iVar5 = (int)DAT_febe66e8;
  iVar4 = (int)DAT_febe66ea;
  iVar3 = (int)DAT_febe66ec;
  iVar2 = FUN_0003975a((int)DAT_febe65b0,(int)DAT_febe66e6);
  iVar5 = FUN_0003975a(iVar8,iVar5);
  FUN_0007012a(iVar5 + iVar2,0x4000,(int)0xffffc000,&local_28);
  iVar2 = FUN_0003975a(iVar7,iVar4);
  iVar5 = FUN_0003975a(iVar6,iVar3);
  FUN_0007012a(iVar5 + iVar2,0x4000,(int)0xffffc000,&iStack_24);
  (*((short *)camry_host_ptr((uint32_t)((0xffffb6eeu + (uint32_t)((int)puVar1)))))) = (short)iStack_24;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb6ecu + (uint32_t)((int)puVar1)))))) = (short)local_28;
  (*((int *)camry_host_ptr((uint32_t)((0xffffb6fcu + (uint32_t)((int)puVar1)))))) = iStack_24 + local_28;
  return iVar2;
}

void f33_stage_ecu_thermal_squared_inputs(void)

{
  uint32_t puVar1;
  int iVar2;
  int iVar3;
  undefined4 local_1c;
  undefined4 uStack_18;
  undefined4 uStack_14;
  
  puVar1 = 0xfebeb800u;
  iVar2 = (int)DAT_febe6eee;
  iVar3 = (int)DAT_febe6eec;
  FUN_0007012a(DAT_febe6efc * DAT_febe6efc,DAT_0002b2f0,DAT_0002b2f4,&local_1c);
  FUN_0007012a(iVar3 * iVar3,DAT_0002b2f8,DAT_0002b2fc,&uStack_18);
  FUN_0007012a(iVar2 * iVar2,DAT_0002b300,DAT_0002b304,&uStack_14);
  (*((undefined4 *)camry_host_ptr((uint32_t)((0xffffb6f0u + (uint32_t)((int)puVar1)))))) = local_1c;
  (*((undefined4 *)camry_host_ptr((uint32_t)((0xffffb6f4u + (uint32_t)((int)puVar1)))))) = uStack_18;
  (*((undefined4 *)camry_host_ptr((uint32_t)((0xffffb6f8u + (uint32_t)((int)puVar1)))))) = uStack_14;
  return;
}

void f33_fill_constant_block_398fa(void)

{
  DAT_febe6f06 = 0;
  DAT_febe6f08 = 0;
  DAT_febe6f0c = 0;
  DAT_febe6f00 = 0;
  DAT_febe6f02 = 0;
  DAT_febe6f04 = 0;
  return;
}

void FUN_0003990c(void)

{
  DAT_febe6f06 = 0;
  DAT_febe6f08 = 0;
  DAT_febe6f00 = 0;
  DAT_febe6f02 = 0;
  return;
}

int FUN_00039996(short param_1,short param_2)

{
  int iVar1;
  int iVar2;
  
  iVar2 = (int)param_2;
  if (iVar2 == 0) {
    return 0;
  }
  iVar1 = (int)param_1 << 0xc;
  if (iVar2 != 0) {
    if (iVar1 == -0x80000000 && iVar2 == -1) {
      iVar1 = -0x80000000;
    }
    else {
      iVar1 = iVar1 / iVar2;
    }
  }
  if (iVar1 < 0) {
    iVar2 = (int)((ulonglong)((longlong)iVar1 * 0x80) >> 0x20) + 1;
    if ((iVar2 < 0 != (-1 < (longlong)iVar1 * 0x80 && iVar2 < 0)) ||
       ((uint)(iVar1 * 0x80) < 0x80000001)) {
      return -0x7fffffff;
    }
  }
  else {
    if (iVar1 == 0) {
      return 0;
    }
    if ((-1 < (longlong)iVar1 * 0x80 && (int)((ulonglong)((longlong)iVar1 * 0x80) >> 0x20) != 0) ||
       (0x7fffffff < (uint)(iVar1 * 0x80))) {
      return 0x7fffffff;
    }
  }
  return iVar1 * 0x80;
}

void FUN_00039ba2(void)

{
  DAT_febe6f16 = 0;
  DAT_febe6f18 = 0;
  DAT_febe6f20 = 0;
  DAT_febe6f24 = 0;
  return;
}

void FUN_00039bb2(void)

{
  DAT_febe6f30 = 0x569a;
  DAT_febe6f32 = 0x2b4d;
  return;
}

void f33_publish_ecu_source4_thermal_limit_maps(void)

{
  uint32_t puVar1;
  int iVar2;
  undefined2 local_c;
  undefined2 uStack_a;
  
  puVar1 = 0xfebeb800u;
  iVar2 = (int)DAT_febe6f12;
  FUN_0007025c(f33_ecu_source4_current_curve_bank0,iVar2,&local_c);
  FUN_0007025c(f33_ecu_source4_current_curve_bank1,iVar2,&uStack_a);
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb730u + (uint32_t)((int)puVar1)))))) = local_c;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb732u + (uint32_t)((int)puVar1)))))) = uStack_a;
  return;
}

int FUN_00039eae(short param_1,short param_2)

{
  int iVar1;
  int iVar2;
  
  iVar2 = (int)param_2;
  if (iVar2 == 0) {
    return 0;
  }
  iVar1 = (int)param_1 << 0xc;
  if (iVar2 != 0) {
    if (iVar1 == -0x80000000 && iVar2 == -1) {
      iVar1 = -0x80000000;
    }
    else {
      iVar1 = iVar1 / iVar2;
    }
  }
  if (iVar1 < 0) {
    iVar2 = (int)((ulonglong)((longlong)iVar1 * 0x80) >> 0x20) + 1;
    if ((iVar2 < 0 != (-1 < (longlong)iVar1 * 0x80 && iVar2 < 0)) ||
       ((uint)(iVar1 * 0x80) < 0x80000001)) {
      return -0x7fffffff;
    }
  }
  else {
    if (iVar1 == 0) {
      return 0;
    }
    if ((-1 < (longlong)iVar1 * 0x80 && (int)((ulonglong)((longlong)iVar1 * 0x80) >> 0x20) != 0) ||
       (0x7fffffff < (uint)(iVar1 * 0x80))) {
      return 0x7fffffff;
    }
  }
  return iVar1 * 0x80;
}

void FUN_00039ffa(void)

{
  DAT_febe6f42 = 0;
  DAT_febe6f44 = 0;
  DAT_febe6f4c = 0;
  DAT_febe6f50 = 0;
  return;
}

int FUN_0003a110(short param_1,short param_2)

{
  int iVar1;
  int iVar2;
  
  iVar2 = (int)param_2;
  if (iVar2 == 0) {
    return 0;
  }
  iVar1 = (int)param_1 << 0xc;
  if (iVar2 != 0) {
    if (iVar1 == -0x80000000 && iVar2 == -1) {
      iVar1 = -0x80000000;
    }
    else {
      iVar1 = iVar1 / iVar2;
    }
  }
  if (iVar1 < 0) {
    iVar2 = (int)((ulonglong)((longlong)iVar1 * 0x80) >> 0x20) + 1;
    if ((iVar2 < 0 != (-1 < (longlong)iVar1 * 0x80 && iVar2 < 0)) ||
       ((uint)(iVar1 * 0x80) < 0x80000001)) {
      return -0x7fffffff;
    }
  }
  else {
    if (iVar1 == 0) {
      return 0;
    }
    if ((-1 < (longlong)iVar1 * 0x80 && (int)((ulonglong)((longlong)iVar1 * 0x80) >> 0x20) != 0) ||
       (0x7fffffff < (uint)(iVar1 * 0x80))) {
      return 0x7fffffff;
    }
  }
  return iVar1 * 0x80;
}

void FUN_0003a25c(void)

{
  DAT_febe6f56 = 0;
  DAT_febe6f58 = 0;
  DAT_febe6f60 = 0;
  DAT_febe6f64 = 0;
  return;
}

void FUN_0003a26c(void)

{
  DAT_febe6f68 = 0x569a;
  DAT_febe6f6a = 0x2b4d;
  return;
}

void f33_publish_ecu_source2_thermal_limit_maps(void)

{
  uint32_t puVar1;
  int iVar2;
  undefined2 local_c;
  undefined2 uStack_a;
  
  puVar1 = 0xfebeb800u;
  iVar2 = (int)DAT_febe6f36;
  FUN_0007025c(f33_ecu_source2_current_curve_bank0,iVar2,&local_c);
  FUN_0007025c(f33_ecu_source2_current_curve_bank1,iVar2,&uStack_a);
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb768u + (uint32_t)((int)puVar1)))))) = local_c;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb76au + (uint32_t)((int)puVar1)))))) = uStack_a;
  return;
}

void f33_fill_constant_block_3a2b8(void)

{
  DAT_febe6f6e = 0x569a;
  DAT_febe6f70 = 0x569a;
  DAT_febe6f72 = 0x2b4d;
  DAT_febe6f74 = 0x569a;
  DAT_febe6f76 = 0x569a;
  DAT_febe6f78 = 0x2b4d;
  return;
}

int f33_select_smaller_magnitude_s16(short first,short second)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  iVar2 = (int)first;
  iVar3 = (int)second;
  if (iVar2 + 0x7fff < 0 == (-1 < iVar2 && iVar2 + 0x7fff < 0) && iVar2 != -0x7fff) {
    iVar1 = iVar2;
    if (iVar2 < 0) {
      iVar1 = (int)-first;
    }
  }
  else {
    iVar1 = 0x7fff;
  }
  if (iVar3 + 0x7fff < 0 == (-1 < iVar3 && iVar3 + 0x7fff < 0) && iVar3 != -0x7fff) {
    iVar4 = iVar3;
    if (iVar3 < 0) {
      iVar4 = (int)-second;
    }
  }
  else {
    iVar4 = 0x7fff;
  }
  if (iVar1 - iVar4 < 0 != (iVar1 < 0 != iVar4 < 0 && iVar4 < 0 == iVar1 - iVar4 < 0) ||
      iVar1 == iVar4) {
    iVar3 = iVar2;
  }
  return iVar3;
}

int FUN_0003a6c6(short param_1,short param_2)

{
  int iVar1;
  int iVar2;
  
  iVar2 = (int)param_2;
  if (iVar2 == 0) {
    return 0;
  }
  iVar1 = (int)param_1 << 0xc;
  if (iVar2 != 0) {
    if (iVar1 == -0x80000000 && iVar2 == -1) {
      iVar1 = -0x80000000;
    }
    else {
      iVar1 = iVar1 / iVar2;
    }
  }
  if (iVar1 < 0) {
    iVar2 = (int)((ulonglong)((longlong)iVar1 * 0x80) >> 0x20) + 1;
    if ((iVar2 < 0 != (-1 < (longlong)iVar1 * 0x80 && iVar2 < 0)) ||
       ((uint)(iVar1 * 0x80) < 0x80000001)) {
      return -0x7fffffff;
    }
  }
  else {
    if (iVar1 == 0) {
      return 0;
    }
    if ((-1 < (longlong)iVar1 * 0x80 && (int)((ulonglong)((longlong)iVar1 * 0x80) >> 0x20) != 0) ||
       (0x7fffffff < (uint)(iVar1 * 0x80))) {
      return 0x7fffffff;
    }
  }
  return iVar1 * 0x80;
}

undefined4 FUN_0003a808(short param_1)

{
  uint32_t puVar1;
  undefined4 uVar2;
  
  puVar1 = 0xfebeb800u;
  uVar2 = FUN_0003a6c6((int)param_1,(int)DAT_0002b4bc);
  (*((undefined4 *)camry_host_ptr((uint32_t)((0xffffb794u + (uint32_t)((int)puVar1)))))) = uVar2;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb78cu + (uint32_t)((int)puVar1)))))) = 0x3480;
  return uVar2;
}

void FUN_0003a844(void)

{
  DAT_febe6f8e = 0;
  DAT_febe6f94 = 0;
  return;
}

void FUN_0003a84e(void)

{
  DAT_febe6f90 = 0;
  DAT_febe6f98 = 0;
  return;
}

undefined4 FUN_0003a94a(short param_1)

{
  uint32_t puVar1;
  undefined4 uVar2;
  
  puVar1 = 0xfebeb800u;
  uVar2 = FUN_0003a6c6((int)param_1,(int)DAT_0002b4d0);
  (*((undefined4 *)camry_host_ptr((uint32_t)((0xffffb7a4u + (uint32_t)((int)puVar1)))))) = uVar2;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb79cu + (uint32_t)((int)puVar1)))))) = 0x3480;
  return uVar2;
}

void FUN_0003a986(void)

{
  DAT_febe6f9e = 0;
  DAT_febe6fa4 = 0;
  return;
}

void FUN_0003a990(void)

{
  DAT_febe6fa0 = 0;
  DAT_febe6fa8 = 0;
  return;
}

void FUN_0003a99c(void)

{
  DAT_febe6fac = 0x569a;
  DAT_febe6fae = 0x2b4d;
  return;
}

void f33_publish_motor_thermal_limit_maps(void)

{
  uint32_t puVar1;
  int iVar2;
  undefined2 local_c;
  undefined2 uStack_a;
  
  puVar1 = 0xfebeb800u;
  iVar2 = (int)DAT_febe6f82;
  FUN_0007025c(((undefined *)camry_host_ptr(0x2b4e4u)),iVar2,&local_c);
  FUN_0007025c(((undefined *)camry_host_ptr(0x2b500u)),iVar2,&uStack_a);
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb7acu + (uint32_t)((int)puVar1)))))) = local_c;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb7aeu + (uint32_t)((int)puVar1)))))) = uStack_a;
  return;
}

int FUN_0003ae66(short param_1,short param_2)

{
  int iVar1;
  int iVar2;
  
  iVar2 = (int)param_2;
  if (iVar2 == 0) {
    return 0;
  }
  iVar1 = (int)param_1 << 0xc;
  if (iVar2 != 0) {
    if (iVar1 == -0x80000000 && iVar2 == -1) {
      iVar1 = -0x80000000;
    }
    else {
      iVar1 = iVar1 / iVar2;
    }
  }
  if (iVar1 < 0) {
    iVar2 = (int)((ulonglong)((longlong)iVar1 * 0x80) >> 0x20) + 1;
    if ((iVar2 < 0 != (-1 < (longlong)iVar1 * 0x80 && iVar2 < 0)) ||
       ((uint)(iVar1 * 0x80) < 0x80000001)) {
      return -0x7fffffff;
    }
  }
  else {
    if (iVar1 == 0) {
      return 0;
    }
    if ((-1 < (longlong)iVar1 * 0x80 && (int)((ulonglong)((longlong)iVar1 * 0x80) >> 0x20) != 0) ||
       (0x7fffffff < (uint)(iVar1 * 0x80))) {
      return 0x7fffffff;
    }
  }
  return iVar1 * 0x80;
}

void FUN_0003afc0(void)

{
  DAT_febe6ff0 = 0;
  DAT_febe6ff2 = 0;
  DAT_febe6ff4 = 0;
  DAT_febe6ff8 = 0;
  return;
}

void FUN_0003b0d8(void)

{
  DAT_febe7000 = 0;
  DAT_febe7002 = 0;
  DAT_febe7004 = 0;
  DAT_febe7008 = 0;
  return;
}

void FUN_0003b0e8(void)

{
  DAT_febe700c = 0x569a;
  DAT_febe700e = 0x2b4d;
  return;
}

void f33_publish_ecu_source3_thermal_limit_maps(void)

{
  uint32_t puVar1;
  int iVar2;
  undefined2 local_c;
  undefined2 uStack_a;
  
  puVar1 = 0xfebeb800u;
  iVar2 = (int)DAT_febe6fe2;
  FUN_0007025c(((undefined *)camry_host_ptr(0x2b554u)),iVar2,&local_c);
  FUN_0007025c(((undefined *)camry_host_ptr(0x2b570u)),iVar2,&uStack_a);
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb80cu + (uint32_t)((int)puVar1)))))) = local_c;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb80eu + (uint32_t)((int)puVar1)))))) = uStack_a;
  return;
}

void FUN_0003b134(void)

{
  uint uVar1;
  uint uVar2;
  
  DAT_febe7010 = 0x5a;
  uVar2 = 0;
  do {
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe701eu + (uint32_t)(uVar2) * 2u)))) = 0x3480;
    uVar2 = uVar2 + 1;
  } while (uVar2 < 6);
  uVar2 = 0;
  do {
    uVar1 = uVar2 + 1;
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe702au + (uint32_t)(uVar2) * 2u)))) = 0x3480;
    uVar2 = uVar1;
  } while (uVar1 < 6);
  DAT_febe7038 = 0;
  DAT_febe703c = 0;
  return;
}

void FUN_0003b288(void)

{
  int iVar1;
  int iVar2;
  
  iVar2 = (int)DAT_febe701e;
  iVar1 = (int)DAT_febe702a;
  DAT_febe7036 = DAT_febe701e;
  if (iVar1 - iVar2 < 0 == (iVar1 < 0 != iVar2 < 0 && iVar2 < 0 == iVar1 - iVar2 < 0) &&
      iVar1 != iVar2) {
    DAT_febe7036 = DAT_febe702a;
  }
  if ((((DAT_febe7bf8 & 0x22) == 0) && ((DAT_febe7bf8 & 0x2200) != 0)) || (DAT_febe6764 == 2)) {
    DAT_febe7012 = '\x11';
    DAT_febe7014 = DAT_febe701e;
  }
  else if ((((DAT_febe7bf8 & 0x22) == 0) || ((DAT_febe7bf8 & 0x2200) != 0)) && (DAT_febe6764 != 1))
  {
    DAT_febe7014 = DAT_febe7036;
    if (((DAT_febe7bf8 & 0x22) == 0) || ((DAT_febe7bf8 & 0x2200) == 0)) {
      DAT_febe7012 = '\0';
    }
    else {
      if (DAT_febe7012 == '\x11') {
        DAT_febe7014 = DAT_febe701e;
        return;
      }
      if (DAT_febe7012 == '\"') {
        DAT_febe7014 = DAT_febe702a;
        return;
      }
    }
  }
  else {
    DAT_febe7012 = '\"';
    DAT_febe7014 = DAT_febe702a;
  }
  return;
}

void f33_reset_latched_monitor_febe7040(void)

{
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7040u)));
  return;
}

void f33_reset_latched_monitor_febe7040_3b3c0(void)

{
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7040u)));
  return;
}

undefined4 FUN_0003b400(void)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  uint uVar4;
  short sStack_a;
  
  uVar4 = (uint)DAT_febe6f6e;
  FUN_0006a522((int)DAT_febe6772,&sStack_a);
  iVar3 = (int)DAT_0002b5d8;
  iVar1 = ((int)sStack_a - uVar4) - iVar3;
  if (iVar1 < 0 == ((int)((int)sStack_a - uVar4) < 0 != iVar3 < 0 && iVar3 < 0 == iVar1 < 0)) {
    uVar2 = 0x22;
  }
  else {
    uVar2 = 0x11;
  }
  return uVar2;
}

void f33_reset_latched_monitor_febe704c(void)

{
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe704cu)));
  return;
}

void f33_reset_latched_monitor_febe704c_3b468(void)

{
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe704cu)));
  return;
}

undefined4 FUN_0003b4a8(void)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  uint uVar4;
  short sStack_a;
  
  uVar4 = (uint)DAT_febe6f74;
  FUN_0006a522((int)DAT_febe6772,&sStack_a);
  iVar3 = (int)DAT_0002b5dc;
  iVar1 = ((int)sStack_a - uVar4) - iVar3;
  if (iVar1 < 0 == ((int)((int)sStack_a - uVar4) < 0 != iVar3 < 0 && iVar3 < 0 == iVar1 < 0)) {
    uVar2 = 0x22;
  }
  else {
    uVar2 = 0x11;
  }
  return uVar2;
}

uint f33_should_zero_restored_thermal_offset(short record_marker)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  int iVar4;
  
  iVar4 = (int)DAT_febe7dce;
  iVar3 = (int)DAT_febe7dd6;
  if ((DAT_febe7bf8 & 0xff) == 0) {
    iVar1 = iVar4;
    if ((DAT_febe7bf8 & 0xff00) != 0) goto LAB_0003b586;
  }
  else {
    iVar1 = iVar3;
    if ((DAT_febe7bf8 & 0xff00) == 0) goto LAB_0003b586;
  }
  iVar1 = iVar4;
  if (iVar3 - iVar4 < 0 == (iVar3 < 0 != iVar4 < 0 && iVar4 < 0 == iVar3 - iVar4 < 0) &&
      iVar3 != iVar4) {
    iVar1 = iVar3;
  }
LAB_0003b586:
  iVar3 = (int)DAT_0002b59e;
  if ((iVar1 - iVar3 < 0 == (iVar1 < 0 != iVar3 < 0 && iVar3 < 0 == iVar1 - iVar3 < 0)) ||
     (record_marker != 0)) {
    uVar2 = 0;
  }
  else {
    uVar2 = 0x5a;
  }
  DAT_febe707e = DAT_febe7dce;
  DAT_febe7080 = DAT_febe7dd6;
  return uVar2;
}

int f33_seed_thermal_offset_pole(short contribution,short gain)

{
  int iVar1;
  int iVar2;
  int local_8;
  
  iVar2 = (int)gain;
  if (iVar2 == 0) {
    local_8 = 0;
  }
  else {
    iVar1 = (int)contribution << 0xc;
    if (iVar2 != 0) {
      if (iVar1 == -0x80000000 && iVar2 == -1) {
        iVar1 = -0x80000000;
      }
      else {
        iVar1 = iVar1 / iVar2;
      }
    }
    FUN_000706ae(iVar1,0x80,&local_8);
  }
  return local_8;
}

void FUN_0003b810(void)

{
  int iVar1;
  ushort uVar2;
  int iVar3;
  
  uVar2 = DAT_febe7bf8;
  iVar3 = 7;
  do {
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7061u + (uint32_t)(iVar3) * 1u)))) == '\0') goto LAB_0003b83a;
    iVar1 = iVar3 + -1;
    iVar3 = iVar3 + -1;
  } while (-1 < iVar1);
  DAT_febe7058 = '\x02';
  iVar3 = 7;
  do {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7061u + (uint32_t)(iVar3) * 1u)))) = 0;
    iVar1 = iVar3 + -1;
    iVar3 = iVar3 + -1;
  } while (-1 < iVar1);
LAB_0003b83a:
  iVar3 = 7;
  do {
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7069u + (uint32_t)(iVar3) * 1u)))) == '\0') goto LAB_0003b85a;
    iVar1 = iVar3 + -1;
    iVar3 = iVar3 + -1;
  } while (-1 < iVar1);
  DAT_febe7058 = '\0';
  iVar3 = 7;
  do {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7069u + (uint32_t)(iVar3) * 1u)))) = 0;
    iVar1 = iVar3 + -1;
    iVar3 = iVar3 + -1;
  } while (-1 < iVar1);
LAB_0003b85a:
  if ((((DAT_febe7058 == '\0') || (DAT_febe7058 == '\x03')) && ((uVar2 & 0x22) != 0)) &&
     ((uVar2 & 0x2200) != 0)) {
    DAT_febe7058 = '\x01';
  }
  else if (DAT_febe7058 != '\x01' && DAT_febe7058 != '\x02') {
    return;
  }
  if (((uVar2 & 0x22) == 0) || ((uVar2 & 0x2200) == 0)) {
    DAT_febe7058 = '\x03';
  }
  return;
}

int f33_follow_thermal_offset_target(uint selector,short target,short previous,short bias)

{
  int iVar1;
  int iVar2;
  short sStack_22;
  int iStack_20;
  int iStack_1c;
  F33FractionalFollowing16 FStack_18;
  
  iVar1 = (selector & 0xff) * 4;
  FStack_18.accumulator = *(int *)(((undefined *)camry_host_ptr(0xfebe7090u)) + iVar1);
  if ((int)(short)(FStack_18.accumulator / 0x10000) != (int)previous) {
    FStack_18.accumulator = (int)previous << 0x10;
  }
  FStack_18.previous = previous;
  FStack_18.target = target;
  f33_follow_s16_fractional(&FStack_18,(uint)DAT_0002b594 * 800,&sStack_22,&iStack_1c);
  iVar2 = (int)DAT_0002b596;
  *(int *)(((undefined *)camry_host_ptr(0xfebe7090u)) + iVar1) = bias * 0x10000 + iStack_1c;
  iStack_20 = (int)sStack_22 + (int)bias;
  FUN_00070160(iStack_20,iVar2,&iStack_20);
  return (int)(short)iStack_20;
}

void FUN_0003ba78(void)

{
  DAT_febe70b4 = 0;
  DAT_febe70b8 = 0;
  DAT_febe70b0 = 0;
  return;
}

void FUN_0003ba84(void)

{
  DAT_febe707a = 0;
  DAT_febe707c = 0;
  DAT_febe70bc = 0;
  DAT_febe70c0 = 0;
  return;
}

void f33_reset_scalar_monitor_3bab2(void)

{
  f33_reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)((0xfebe70c8u)))));
  return;
}

void f33_reset_scalar_monitor_3bab2_3baa2(void)

{
  f33_reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)((0xfebe70c8u)))));
  return;
}

uint f33_classify_acquisition_status_a(void)

{
  if (DAT_febe81d0 == 'Z') {
    return 0x22;
  }
  return 0x11;
}

void f33_reset_scalar_monitor_3bb44(void)

{
  f33_reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)((0xfebe70d8u)))));
  return;
}

void f33_reset_scalar_monitor_3bb44_3bb34(void)

{
  f33_reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)((0xfebe70d8u)))));
  return;
}

uint f33_classify_acquisition_status_b(void)

{
  if (DAT_febe81d1 == 'Z') {
    return 0x22;
  }
  return 0x11;
}

void f33_publish_acquisition_monitor_status(uchar index,uint packed_status)

{
  if (index < 4) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe70e8u + (uint32_t)(index) * 1u)))) = (char)packed_status;
  }
  return;
}

void f33_reset_scalar_monitor_3bc4c(void)

{
  f33_reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebe70ecu)))));
  return;
}

void f33_reset_scalar_monitor_3bc4c_3bc3c(void)

{
  f33_reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebe70ecu)))));
  return;
}

uint f33_classify_acquisition_range_a(void)

{
  if (DAT_febe81d4 != 'Z') {
    return 0x44;
  }
  if ((DAT_0002b5f8 <= DAT_febe81d6) && (DAT_febe81d8 <= DAT_0002b5fa)) {
    return 0x11;
  }
  return 0x22;
}

void f33_reset_scalar_monitor_3bcfc(void)

{
  f33_reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebe70f8u)))));
  return;
}

void f33_reset_scalar_monitor_3bcfc_3bcec(void)

{
  f33_reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebe70f8u)))));
  return;
}

uint f33_classify_acquisition_range_b(void)

{
  if (DAT_febe81d5 != 'Z') {
    return 0x44;
  }
  if ((DAT_0002b5fc <= DAT_febe81da) && (DAT_febe81dc <= DAT_0002b5fe)) {
    return 0x11;
  }
  return 0x22;
}

void f33_classify_fault_qualification(uint classes)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  
  DAT_febe71ee = 0;
  if ((classes & 0xffff) != 0) {
    uVar3 = 0;
    uVar4 = 0;
    do {
      uVar5 = uVar4;
      if ((((classes & 0xffff) >> (uVar3 & 0x1f) & 1) != 0) && (uVar5 = 0x8000, uVar4 == 0)) {
        uVar5 = 1 << (uVar3 & 0x1f) & 0xffff;
      }
      DAT_febe71ee = (undefined2)uVar5;
      uVar2 = uVar3 + 1;
      iVar1 = uVar3 - 0xf;
      uVar3 = uVar2;
      uVar4 = uVar5;
    } while (iVar1 < 0 != ((int)uVar2 < 0 && -1 < iVar1));
  }
  return;
}

void f33_select_retained_fault_record(uint slot)

{
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe71ccu + (uint32_t)(slot & 0xff) * 1u)))) = 0xa5;
  return;
}

void f33_retain_and_clear_fault_record(uint slot)

{
  int iVar1;
  int iVar2;
  uint slot_00;
  
  slot_00 = slot & 0xff;
  if (slot_00 < 0x18) {
    iVar1 = (int)(short)slot_00;
    iVar2 = slot_00 * 2;
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7320u + (uint32_t)(iVar1 * 6) * 2u)))) = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7200u + (uint32_t)(iVar1 * 6) * 2u))));
    *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe710cu)) + iVar2) = *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe713cu)) + iVar2);
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7322u + (uint32_t)(iVar1 * 6) * 2u)))) = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7202u + (uint32_t)(iVar1 * 6) * 2u))));
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7324u + (uint32_t)(iVar1 * 6) * 2u)))) = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7204u + (uint32_t)(iVar1 * 6) * 2u))));
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7326u + (uint32_t)(iVar1 * 6) * 2u)))) = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7206u + (uint32_t)(iVar1 * 6) * 2u))));
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7328u + (uint32_t)(iVar1 * 6) * 2u)))) = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7208u + (uint32_t)(iVar1 * 6) * 2u))));
    *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe716cu)) + iVar2) = *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe719cu)) + iVar2);
    f33_select_retained_fault_record(slot_00);
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7200u + (uint32_t)(iVar1 * 6) * 2u)))) = 0;
    *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe713cu)) + iVar2) = 0xffff;
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7202u + (uint32_t)(iVar1 * 6) * 2u)))) = 0;
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7204u + (uint32_t)(iVar1 * 6) * 2u)))) = 0;
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7206u + (uint32_t)(iVar1 * 6) * 2u)))) = 0;
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7208u + (uint32_t)(iVar1 * 6) * 2u)))) = 0;
    *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe719cu)) + iVar2) = 0xffff;
  }
  return;
}

void f33_select_current_fault_record(uint slot)

{
  if ((slot & 0xff) < 0x18) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe71ccu + (uint32_t)(slot & 0xff) * 1u)))) = 0x5a;
  }
  return;
}

void FUN_0003c310(void)

{
  uchar uVar1;
  uchar uVar2;
  uint uVar3;
  uint32_t puVar4;
  byte bVar5;
  byte bVar6;
  
  uVar3 = f33_output_request_status;
  uVar2 = f33_channel_request_state.channel1_state;
  uVar1 = f33_channel_request_state.channel0_state;
  bVar5 = DAT_febe71e8;
  bVar6 = DAT_febe71e5;
  puVar4 = 0xfebeb800u;
  f33_set_channel_owner_request('\x02',0x20002);
  if ((uVar1 == '\0') && (uVar2 == '\0')) {
    if (bVar6 < DAT_000317d5) {
      bVar6 = bVar6 + 1;
    }
    else {
      f33_cancel_terminal_output_ramp();
      f33_set_output_request_word('\x02',0x70017001);
      if ((uVar3 & 0x70017001) == 0x70017001) {
        if (bVar5 < DAT_000317d6) {
          bVar5 = bVar5 + 1;
        }
        else {
          FUN_00056e66(2, camry_host_addr(((undefined *)camry_host_ptr(0x20002u))));
        }
      }
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb9e5u + (uint32_t)((int)puVar4) * 1u)))) = bVar6;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb9e8u + (uint32_t)((int)puVar4) * 1u)))) = bVar5;
  return;
}

void FUN_0003c386(void)

{
  DAT_febe71e5 = 0;
  DAT_febe71e8 = 0;
  f33_set_output_request_word('\x02',0);
  f33_cancel_terminal_output_ramp();
  f33_set_channel_owner_request('\x02',0);
  FUN_00056e66(2,0);
  return;
}

void FUN_0003c3b2(void)

{
  uchar uVar1;
  uint32_t puVar2;
  byte bVar3;
  
  uVar1 = f33_channel_request_state.channel0_state;
  bVar3 = DAT_febe71e6;
  puVar2 = 0xfebeb800u;
  f33_set_channel_owner_request('\x03',2);
  if (uVar1 == '\0') {
    if (bVar3 < DAT_000317d5) {
      bVar3 = bVar3 + 1;
    }
    else {
      f33_set_output_request_word('\x05',0x7001);
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb9e6u + (uint32_t)((int)puVar2) * 1u)))) = bVar3;
  return;
}

void FUN_0003c3ec(void)

{
  DAT_febe71e6 = 0;
  f33_set_output_request_word('\x05',0);
  f33_set_channel_owner_request('\x03',0);
  FUN_00056e66(3,0);
  return;
}

void FUN_0003c410(void)

{
  uchar uVar1;
  uint32_t puVar2;
  byte bVar3;
  
  uVar1 = f33_channel_request_state.channel1_state;
  bVar3 = DAT_febe71e7;
  puVar2 = 0xfebeb800u;
  f33_set_channel_owner_request('\x04',0x20000);
  if (uVar1 == '\0') {
    if (bVar3 < DAT_000317d5) {
      bVar3 = bVar3 + 1;
    }
    else {
      f33_set_output_request_word('\x06',0x70010000);
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb9e7u + (uint32_t)((int)puVar2) * 1u)))) = bVar3;
  return;
}

void FUN_0003c44c(void)

{
  DAT_febe71e7 = 0;
  f33_set_output_request_word('\x06',0);
  f33_set_channel_owner_request('\x04',0);
  FUN_00056e66(4,0);
  return;
}

void FUN_0003cb32(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = 0;
  do {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe744cu + (uint32_t)(iVar3) * 1u)))) = 0;
    iVar2 = iVar3 + 1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7452u + (uint32_t)(iVar3) * 1u)))) = 0;
    iVar1 = iVar3 + -5;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  return;
}

void FUN_0003cb48(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  DAT_febe7458 = 0;
  iVar3 = 0;
  do {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7459u + (uint32_t)(iVar3) * 1u)))) = 0;
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -1;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  iVar3 = 0;
  do {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe745du + (uint32_t)(iVar3) * 1u)))) = 0;
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -1;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  iVar3 = 0;
  do {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe744cu + (uint32_t)(iVar3) * 1u)))) = 0;
    iVar2 = iVar3 + 1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7452u + (uint32_t)(iVar3) * 1u)))) = 0;
    iVar1 = iVar3 + -5;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  DAT_febe745b = 0;
  DAT_febe745c = 0;
  return;
}

void f33_set_communication_monitor_status(uint index,uchar status)

{
  if ((index & 0xff) < 0x19) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7476u + (uint32_t)(index & 0xff) * 1u)))) = status;
  }
  return;
}

void FUN_0003d330(void)

{
  DAT_febe7474 = 0;
  return;
}

void FUN_0003d336(void)

{
  DAT_febe7475 = DAT_febe7486 == '\"';
  return;
}

void f33_reset_latched_monitor_febe7490(void)

{
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7490u)));
  return;
}

void f33_reset_latched_monitor_febe7490_3d426(void)

{
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7490u)));
  return;
}

uint f33_classify_received_content_a(void)

{
  if ((f33_internal_source_admission_state == '\0') && (DAT_febe8052 == '\0')) {
    if (DAT_febe804d == '\x01') {
      return 0x22;
    }
    return 0x11;
  }
  return 0x44;
}

void f33_reset_latched_monitor_febe749c(void)

{
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe749cu)));
  return;
}

void f33_reset_latched_monitor_febe749c_3d4c0(void)

{
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe749cu)));
  return;
}

uint f33_classify_received_content_b(void)

{
  if ((f33_internal_source_admission_state == '\0') && (DAT_febe8052 == '\0')) {
    if (DAT_febe804e == '\x01') {
      return 0x22;
    }
    return 0x11;
  }
  return 0x44;
}

void f33_set_local_status_monitor_status(uint index,uchar status)

{
  if ((index & 0xff) < 6) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe74a8u + (uint32_t)(index & 0xff) * 1u)))) = status;
  }
  return;
}

void f33_reset_latched_monitor_febe74b0(void)

{
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe74b0u)));
  return;
}

void f33_reset_latched_monitor_febe74b0_3d746(void)

{
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe74b0u)));
  return;
}

uint f33_classify_qualified_local_status(void)

{
  char cVar1;
  uint uVar2;
  
  cVar1 = DAT_febe65f1;
  if ((DAT_febe64d0 == '\x02') || (DAT_febe64d1 == '\x02')) {
    if (DAT_febe67a0 < DAT_0002b61e) {
      DAT_febe67a0 = DAT_febe67a0 + 1;
    }
    else {
      cVar1 = DAT_febe65f7;
      if (DAT_febe65f6 == 'Z') goto LAB_0003d7de;
    }
  }
  else {
    DAT_febe67a0 = 0;
  }
  if (cVar1 != 'Z') {
    return 0x44;
  }
LAB_0003d7de:
  uVar2 = 0x11;
  if (DAT_febe8278 == 'Z') {
    uVar2 = 0x22;
  }
  return uVar2;
}

void f33_reset_recoverable_monitor_febe74bc(void)

{
  f33_reset_recoverable_monitor((F33RecoverableMonitorState *)((undefined *)camry_host_ptr(0xfebe74bcu)));
  return;
}

void FUN_0003d826(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  f33_reset_recoverable_monitor((F33RecoverableMonitorState *)((undefined *)camry_host_ptr(0xfebe74bcu)));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbcc8u + (uint32_t)((int)puVar1) * 1u)))) = 0;
  return;
}

uint f33_classify_paired_local_status(void)

{
  if ((DAT_febe827e == 'Z') && (DAT_febe827d == 'Z')) {
    return 0x22;
  }
  return 0x11;
}

uint f33_classify_paired_local_status_recovery(void)

{
  if ((DAT_febe827e == 'Z') && (DAT_febe827d == 'Z')) {
    return 0x22;
  }
  return 0x11;
}

void f33_reset_recoverable_monitor_febe74cc(void)

{
  f33_reset_recoverable_monitor((F33RecoverableMonitorState *)((undefined *)camry_host_ptr(0xfebe74ccu)));
  return;
}

void f33_reset_recoverable_monitor_febe74cc_3d906(void)

{
  f33_reset_recoverable_monitor((F33RecoverableMonitorState *)((undefined *)camry_host_ptr(0xfebe74ccu)));
  return;
}

uint f33_classify_individual_local_status_a(void)

{
  if (DAT_febe74c8 == 'Z') {
    return 0x44;
  }
  if (DAT_febe827e == 'Z') {
    return 0x22;
  }
  return 0x11;
}

void f33_reset_recoverable_monitor_febe74d8(void)

{
  f33_reset_recoverable_monitor((F33RecoverableMonitorState *)((undefined *)camry_host_ptr(0xfebe74d8u)));
  return;
}

void f33_reset_recoverable_monitor_febe74d8_3d9b8(void)

{
  f33_reset_recoverable_monitor((F33RecoverableMonitorState *)((undefined *)camry_host_ptr(0xfebe74d8u)));
  return;
}

uint f33_classify_individual_local_status_b(void)

{
  if (DAT_febe74c8 == 'Z') {
    return 0x44;
  }
  if (DAT_febe827d == 'Z') {
    return 0x22;
  }
  return 0x11;
}

void FUN_0003da5a(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  f33_reset_windowed_monitor((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe74e4u)));
  f33_reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)((0xffffbcf4u + (uint32_t)((int)puVar1))))));
  return;
}

void FUN_0003da72(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  f33_reset_windowed_monitor((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe74e4u)));
  f33_reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)((0xffffbcf4u + (uint32_t)((int)puVar1))))));
  return;
}

uint f33_classify_paired_source_delayed_difference_aa(void)

{
  if (((DAT_febe7bc2 != 'Z') && (DAT_febe7bc3 != 'Z')) ||
     (f33_paired_source_monitor_status[0] != '\0')) {
    return 0x44;
  }
  if ((DAT_febe7554 & 1) != 0) {
    return 0x22;
  }
  if (((DAT_febe7554 == 0) && (((int16_t)DAT_febe7b44) == -1)) && ((DAT_febe71ec >> 7 & 1) == 0)) {
    return 0x11;
  }
  return 0x33;
}

uint f33_classify_paired_source_delayed_difference_ab(void)

{
  if (((DAT_febe7bc2 != 'Z') && (DAT_febe7bc3 != 'Z')) ||
     (f33_paired_source_monitor_status[0] != '\0')) {
    return 0x44;
  }
  if ((DAT_febe7554 >> 1 & 1) != 0) {
    return 0x22;
  }
  if (((DAT_febe7554 == 0) && (((int16_t)DAT_febe7b44) == -1)) && ((DAT_febe71ec >> 7 & 1) == 0)) {
    return 0x11;
  }
  return 0x33;
}

void FUN_0003dbe6(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  f33_reset_windowed_monitor((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe7504u)));
  f33_reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)((0xffffbd14u + (uint32_t)((int)puVar1))))));
  return;
}

void FUN_0003dbfe(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  f33_reset_windowed_monitor((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe7504u)));
  f33_reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)((0xffffbd14u + (uint32_t)((int)puVar1))))));
  return;
}

uint f33_classify_paired_source_delayed_difference_ba(void)

{
  if (((DAT_febe7bc2 != 'Z') && (DAT_febe7bc3 != 'Z')) ||
     (f33_paired_source_monitor_status[1] != '\0')) {
    return 0x44;
  }
  if ((DAT_febe7554 >> 4 & 1) != 0) {
    return 0x22;
  }
  if (((DAT_febe7554 == 0) && (((int16_t)DAT_febe7b46) == -1)) && ((DAT_febe71ec >> 8 & 1) == 0)) {
    return 0x11;
  }
  return 0x33;
}

uint f33_classify_paired_source_delayed_difference_bb(void)

{
  if (((DAT_febe7bc2 != 'Z') && (DAT_febe7bc3 != 'Z')) ||
     (f33_paired_source_monitor_status[1] != '\0')) {
    return 0x44;
  }
  if ((DAT_febe7554 >> 5 & 1) != 0) {
    return 0x22;
  }
  if (((DAT_febe7554 == 0) && (((int16_t)DAT_febe7b46) == -1)) && ((DAT_febe71ec >> 8 & 1) == 0)) {
    return 0x11;
  }
  return 0x33;
}

void f33_reset_latched_monitor_febe7524(void)

{
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7524u)));
  return;
}

void FUN_0003dd82(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7524u)));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbd34u + (uint32_t)((int)puVar1) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x54b4)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbd35u + (uint32_t)((int)puVar1) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x54b2)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbd36u + (uint32_t)((int)puVar1) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x54b0)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbd37u + (uint32_t)((int)puVar1) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x54ae)))));
  return;
}

void f33_reset_latched_monitor_febe7538(void)

{
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7538u)));
  return;
}

void FUN_0003df22(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7538u)));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbd48u + (uint32_t)((int)puVar1) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x54b3)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbd49u + (uint32_t)((int)puVar1) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x54b1)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbd4au + (uint32_t)((int)puVar1) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x54af)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbd4bu + (uint32_t)((int)puVar1) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x54ad)))));
  return;
}

void FUN_0003e0b4(void)

{
  DAT_febe754f = 0;
  DAT_febe7550 = 0;
  DAT_febe7551 = 0;
  DAT_febe7552 = 0;
  return;
}

uint f33_classify_paired_source_sample_differences(void)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  
  iVar1 = (int)DAT_0002b65a;
  iVar3 = (int)(short)(DAT_febe8250 - DAT_febe8252);
  iVar4 = (int)(short)(DAT_febe824c - DAT_febe824e);
  uVar2 = 0;
  iVar5 = (int)(short)(DAT_febe824c - DAT_febe8250);
  if ((iVar4 - iVar1 < 0 == (iVar4 < 0 != iVar1 < 0 && iVar1 < 0 == iVar4 - iVar1 < 0) &&
       iVar4 != iVar1) ||
     (iVar4 + iVar1 < 0 != (iVar4 < 0 != -iVar1 < 0 && -iVar1 < 0 == iVar4 + iVar1 < 0))) {
    uVar2 = 1;
  }
  iVar1 = (int)DAT_0002b65c;
  if ((iVar3 - iVar1 < 0 == (iVar3 < 0 != iVar1 < 0 && iVar1 < 0 == iVar3 - iVar1 < 0) &&
       iVar3 != iVar1) ||
     (iVar3 + iVar1 < 0 != (iVar3 < 0 != -iVar1 < 0 && -iVar1 < 0 == iVar3 + iVar1 < 0))) {
    uVar2 = uVar2 | 4;
  }
  iVar1 = (int)DAT_0002b65e;
  if ((iVar5 - iVar1 < 0 == (iVar5 < 0 != iVar1 < 0 && iVar1 < 0 == iVar5 - iVar1 < 0) &&
       iVar5 != iVar1) ||
     (iVar5 + iVar1 < 0 != (iVar5 < 0 != -iVar1 < 0 && -iVar1 < 0 == iVar5 + iVar1 < 0))) {
    uVar2 = uVar2 | 2;
  }
  return uVar2;
}

void f33_fill_constant_block_3e1da(void)

{
  DAT_febe7554 = 0;
  DAT_febe7555 = 0;
  DAT_febe7556 = 0;
  DAT_febe7557 = 0;
  DAT_febe7558 = 0;
  return;
}

void f33_publish_paired_source_difference_changes(void)

{
  DAT_febe7554 = DAT_febe642c != DAT_febe7555;
  if (DAT_febe642d != DAT_febe7556) {
    DAT_febe7554 = DAT_febe7554 | 2;
  }
  if (DAT_febe642e != DAT_febe7557) {
    DAT_febe7554 = DAT_febe7554 | 0x10;
  }
  if (DAT_febe642f != DAT_febe7558) {
    DAT_febe7554 = DAT_febe7554 | 0x20;
  }
  DAT_febe7555 = DAT_febe642c;
  DAT_febe7556 = DAT_febe642d;
  DAT_febe7557 = DAT_febe642e;
  DAT_febe7558 = DAT_febe642f;
  return;
}

void f33_publish_paired_source_monitor_status(uint index,uint packed)

{
  uint uVar1;
  
  uVar1 = index & 0xff;
  if (uVar1 < 10) {
    f33_paired_source_monitor_status[uVar1] = (uchar)packed;
    f33_paired_source_monitor_transition[uVar1] = (uchar)(packed >> 0x10);
  }
  return;
}

void f33_reset_windowed_monitor_febe757c(void)

{
  f33_reset_windowed_monitor((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe757cu)));
  return;
}

void f33_reset_windowed_monitor_febe757c_3e3ea(void)

{
  f33_reset_windowed_monitor((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe757cu)));
  return;
}

uint f33_classify_paired_source_status_masks_a(void)

{
  if (((DAT_febe7bc2 == 'Z') || (DAT_febe7bc3 == 'Z')) &&
     (f33_paired_source_monitor_status[0] == '\0')) {
    if (((DAT_0002b662 & DAT_febe6360) == 0) && ((DAT_0002b664 & DAT_febe6362) == 0)) {
      return 0x11;
    }
    return 0x22;
  }
  return 0x44;
}

void f33_reset_windowed_monitor_febe758c(void)

{
  f33_reset_windowed_monitor((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe758cu)));
  return;
}

void f33_reset_windowed_monitor_febe758c_3e4bc(void)

{
  f33_reset_windowed_monitor((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe758cu)));
  return;
}

uint f33_classify_paired_source_status_masks_b(void)

{
  if (((DAT_febe7bc2 == 'Z') || (DAT_febe7bc3 == 'Z')) &&
     (f33_paired_source_monitor_status[1] == '\0')) {
    if (((DAT_0002b666 & DAT_febe6364) == 0) && ((DAT_0002b668 & DAT_febe6366) == 0)) {
      return 0x11;
    }
    return 0x22;
  }
  return 0x44;
}

void FUN_0003e57e(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe75b4 = 0;
  DAT_febe75b6 = 0;
  f33_reset_terminal_monitor(f33_delayed_status_bit_triplet_a_states);
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbda4u + (uint32_t)((int)puVar1))))));
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbdacu + (uint32_t)((int)puVar1))))));
  return;
}

void FUN_0003e5a6(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe67a5 = 0;
  DAT_febe67a4 = 0;
  DAT_febe67a6 = 0;
  DAT_febe67a8 = 0;
  f33_reset_terminal_monitor(f33_delayed_status_bit_triplet_a_states);
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbda4u + (uint32_t)((int)puVar1))))));
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbdacu + (uint32_t)((int)puVar1))))));
  return;
}

uint f33_admit_delayed_status_bit_triplet_a(void)

{
  uint32_t puVar1;
  uint uVar2;
  ushort uVar3;
  
  uVar3 = DAT_febe67a8;
  puVar1 = 0xfebeb800u;
  uVar2 = (uint)DAT_febe67a4;
  if (uVar2 != 0x5a) {
    if (DAT_febe67a8 < DAT_0002b6d8) {
      uVar3 = DAT_febe67a8 + 1;
    }
    else {
      puVar1 = 0xfebeb800u;
      if ((DAT_febe6764 & 1) == 0) {
        puVar1 = 0xfebeb800u;
        f33_set_output_request_word((uchar)(DAT_febe6764 & 1),DAT_febe6764 & 1);
        f33_set_direct_output_codes_bank0((ushort *)((undefined *)camry_host_ptr(0x2b6dau)));
        f33_request_direct_output_bank0();
      }
      uVar2 = 0x5a;
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x505c))))) = (char)uVar2;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x5058)))) = uVar3;
  return uVar2;
}

uint f33_classify_delayed_status_bit_triplet_a(void)

{
  if ((((DAT_febe64d8 == '\0') && (DAT_febe64d0 == '\0')) && ((DAT_febe6620 >> 2 & 1) != 0)) &&
     ((((DAT_febe661c >> 2 & 1) != 0 && ((DAT_febe6628 >> 1 & 1) == 0)) &&
      (((DAT_febe6614 & 1) != 0 && (DAT_febe65f0 == 'Z')))))) {
    if (DAT_febe75b4 != 'Z') {
      return 0x11;
    }
    return 0x22;
  }
  return 0x44;
}

void FUN_0003e816(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe75d0 = 0;
  DAT_febe75d2 = 0;
  f33_reset_terminal_monitor(f33_delayed_status_bit_triplet_b_states);
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbdc0u + (uint32_t)((int)puVar1))))));
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbdc8u + (uint32_t)((int)puVar1))))));
  return;
}

void FUN_0003e83e(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe67ad = 0;
  DAT_febe67ac = 0;
  DAT_febe67ae = 0;
  DAT_febe67b0 = 0;
  f33_reset_terminal_monitor(f33_delayed_status_bit_triplet_b_states);
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbdc0u + (uint32_t)((int)puVar1))))));
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbdc8u + (uint32_t)((int)puVar1))))));
  return;
}

uint f33_admit_delayed_status_bit_triplet_b(void)

{
  uint32_t puVar1;
  uint uVar2;
  ushort uVar3;
  
  uVar3 = DAT_febe67b0;
  puVar1 = 0xfebeb800u;
  uVar2 = (uint)DAT_febe67ac;
  if (uVar2 != 0x5a) {
    if (DAT_febe67b0 < DAT_0002b6e4) {
      uVar3 = DAT_febe67b0 + 1;
    }
    else {
      puVar1 = 0xfebeb800u;
      if ((DAT_febe6764 & 2) == 0) {
        puVar1 = 0xfebeb800u;
        f33_set_output_request_word('\x01',DAT_febe6764 & 2);
        f33_set_direct_output_codes_bank1((ushort *)((undefined *)camry_host_ptr(0x2b6e6u)));
        f33_request_direct_output_bank1();
      }
      uVar2 = 0x5a;
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5054))))) = (char)uVar2;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x5050)))) = uVar3;
  return uVar2;
}

uint f33_classify_delayed_status_bit_triplet_b(void)

{
  if ((((DAT_febe64d9 == '\0') && (DAT_febe64d1 == '\0')) && ((DAT_febe6620 >> 0x12 & 1) != 0)) &&
     ((((DAT_febe661c >> 0x12 & 1) != 0 && ((DAT_febe6628 >> 0x11 & 1) == 0)) &&
      (((DAT_febe6614 & 1) != 0 && (DAT_febe65f0 == 'Z')))))) {
    if (DAT_febe75d0 != 'Z') {
      return 0x11;
    }
    return 0x22;
  }
  return 0x44;
}

void FUN_0003eab4(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe75ec = 0;
  DAT_febe75ee = 0;
  f33_reset_terminal_monitor(f33_matched_state2_status_bit_triplet_a_states);
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbddcu + (uint32_t)((int)puVar1))))));
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbde4u + (uint32_t)((int)puVar1))))));
  return;
}

void FUN_0003eadc(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe67b4 = 0;
  DAT_febe67b5 = 0;
  f33_reset_terminal_monitor(f33_matched_state2_status_bit_triplet_a_states);
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbddcu + (uint32_t)((int)puVar1))))));
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbde4u + (uint32_t)((int)puVar1))))));
  return;
}

uint f33_classify_matched_state2_status_bit_triplet_a(void)

{
  if ((((((DAT_febe64d8 == '\x02') && (DAT_febe64d0 == '\x02')) && ((DAT_febe6620 >> 1 & 1) == 0))
       && (((DAT_febe6620 >> 2 & 1) != 0 && ((DAT_febe661c >> 1 & 1) == 0)))) &&
      (((DAT_febe661c >> 2 & 1) != 0 &&
       (((DAT_febe6628 >> 1 & 1) == 0 && ((DAT_febe6614 & 1) == 0)))))) && (DAT_febe65f6 == 'Z')) {
    if (DAT_febe75ec != 'Z') {
      return 0x11;
    }
    return 0x22;
  }
  return 0x44;
}

void FUN_0003ece4(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe7608 = 0;
  DAT_febe760a = 0;
  f33_reset_terminal_monitor(f33_matched_state2_status_bit_triplet_b_states);
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbdf8u + (uint32_t)((int)puVar1))))));
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbe00u + (uint32_t)((int)puVar1))))));
  return;
}

void FUN_0003ed0c(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe67b8 = 0;
  DAT_febe67b9 = 0;
  f33_reset_terminal_monitor(f33_matched_state2_status_bit_triplet_b_states);
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbdf8u + (uint32_t)((int)puVar1))))));
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbe00u + (uint32_t)((int)puVar1))))));
  return;
}

uint f33_classify_matched_state2_status_bit_triplet_b(void)

{
  if ((((((DAT_febe64d9 == '\x02') && (DAT_febe64d1 == '\x02')) && ((DAT_febe6620 >> 0x11 & 1) == 0)
        ) && (((DAT_febe6620 >> 0x12 & 1) != 0 && ((DAT_febe661c >> 0x11 & 1) == 0)))) &&
      (((DAT_febe661c & 0x40000) != 0 &&
       (((DAT_febe6628 >> 0x11 & 1) == 0 && ((DAT_febe6614 & 1) == 0)))))) && (DAT_febe65f7 == 'Z'))
  {
    if (DAT_febe7608 != 'Z') {
      return 0x11;
    }
    return 0x22;
  }
  return 0x44;
}

void f33_reset_coupled_sample_threshold_both(void)

{
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xfebe760cu)))));
  return;
}

void FUN_0003eff0(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xfebe760cu)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5044))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5043))))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x5042)))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x5040)))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x503e)))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x503c)))) = 0;
  return;
}

undefined4 FUN_0003f010(void)

{
  ushort uVar1;
  uint32_t puVar2;
  undefined4 uVar3;
  ushort uVar4;
  
  uVar4 = DAT_febe67c0;
  uVar1 = DAT_febe6764;
  puVar2 = 0xfebeb800u;
  if (DAT_febe67c0 < DAT_0002b6fa) {
    uVar3 = 0;
    uVar4 = DAT_febe67c0 + 1;
  }
  else {
    puVar2 = 0xfebeb800u;
    if ((DAT_febe6764 & 1) == 0) {
      puVar2 = 0xfebeb800u;
      FUN_00056e66(DAT_febe6764 & 1,2);
      FUN_00056f14(0,4);
    }
    if ((uVar1 >> 1 & 1) == 0) {
      FUN_00056e66(1,0x20000);
      FUN_00056f14(1,0x40000);
    }
    uVar3 = 1;
  }
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x5040)))) = uVar4;
  return uVar3;
}

undefined4 FUN_0003f066(void)

{
  ushort uVar1;
  uint32_t puVar2;
  undefined4 uVar3;
  ushort uVar4;
  
  uVar4 = DAT_febe67c2;
  uVar1 = DAT_febe6764;
  puVar2 = 0xfebeb800u;
  if (DAT_febe67c2 < DAT_0002b6fc) {
    uVar3 = 1;
    uVar4 = DAT_febe67c2 + 1;
  }
  else {
    puVar2 = 0xfebeb800u;
    if ((DAT_febe6764 & 1) == 0) {
      puVar2 = 0xfebeb800u;
      FUN_00056c26(DAT_febe6764 & 1,2);
    }
    if ((uVar1 >> 1 & 1) == 0) {
      FUN_00056c26(1,0x20000);
    }
    uVar3 = 2;
  }
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x503e)))) = uVar4;
  return uVar3;
}

undefined4 FUN_0003f0aa(void)

{
  undefined4 uVar1;
  
  uVar1 = 2;
  if (DAT_febe67c4 < DAT_0002b6fe) {
    DAT_febe67c4 = DAT_febe67c4 + 1;
  }
  else {
    uVar1 = 3;
  }
  return uVar1;
}

void f33_reset_command_status_bit_clear_a(void)

{
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xfebe7614u)))));
  return;
}

void FUN_0003f2d6(void)

{
  DAT_febe67c8 = 0;
  DAT_febe67c9 = 0;
  DAT_febe67ca = 0;
  DAT_febe67cc = 0;
  DAT_febe67ce = 0;
  DAT_febe67d0 = 0;
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xfebe7614u)))));
  return;
}

undefined4 FUN_0003f2f6(void)

{
  ushort uVar1;
  uint32_t puVar2;
  undefined4 uVar3;
  ushort uVar4;
  
  uVar4 = DAT_febe67ca;
  uVar1 = DAT_febe6764;
  puVar2 = 0xfebeb800u;
  if (DAT_febe67ca < DAT_0002b70a) {
    uVar3 = 0;
    uVar4 = DAT_febe67ca + 1;
  }
  else {
    puVar2 = 0xfebeb800u;
    FUN_00050c82(0,0);
    if ((uVar1 & 1) == 0) {
      FUN_00056cda(uVar1 & 1,2);
    }
    uVar3 = 1;
  }
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x5036)))) = uVar4;
  return uVar3;
}

undefined4 FUN_0003f334(void)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  iVar3 = 0;
  uVar1 = 1;
  iVar2 = 0;
  if (DAT_febe67cc < DAT_0002b70c) {
    iVar4 = 0;
    DAT_febe67cc = DAT_febe67cc + 1;
  }
  else {
    iVar4 = 0x5a;
  }
  if (DAT_febe67ce < DAT_0002b70e) {
    DAT_febe67ce = DAT_febe67ce + 1;
  }
  else {
    iVar3 = 0x5a;
  }
  if (DAT_febe67d0 < DAT_0002b710) {
    DAT_febe67d0 = DAT_febe67d0 + 1;
  }
  else {
    iVar2 = 0x5a;
  }
  if ((iVar4 == 0x5a) && (iVar3 == 0x5a)) {
    if (iVar2 == 0x5a) {
      uVar1 = 2;
    }
    else {
      uVar1 = 1;
    }
  }
  return uVar1;
}

uint f33_classify_command_status_bit_clear_a(void)

{
  if ((((DAT_febe64d8 == '\0') && (DAT_febe64d0 == '\0')) && ((DAT_febe6620 >> 2 & 1) != 0)) &&
     ((((DAT_febe661c >> 2 & 1) != 0 && ((DAT_febe6628 >> 1 & 1) == 0)) &&
      (((DAT_febe6614 & 1) == 0 && (DAT_febe65f0 == 'Z')))))) {
    if (DAT_febe8291 != '\0') {
      return 0x11;
    }
    return 0x22;
  }
  return 0x44;
}

void f33_reset_command_status_bit_clear_b(void)

{
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xfebe761cu)))));
  return;
}

void FUN_0003f4ec(void)

{
  DAT_febe67d4 = 0;
  DAT_febe67d5 = 0;
  DAT_febe67d6 = 0;
  DAT_febe67d8 = 0;
  DAT_febe67da = 0;
  DAT_febe67dc = 0;
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xfebe761cu)))));
  return;
}

undefined4 FUN_0003f50c(void)

{
  ushort uVar1;
  uint32_t puVar2;
  undefined4 uVar3;
  ushort uVar4;
  
  uVar4 = DAT_febe67d6;
  uVar1 = DAT_febe6764;
  puVar2 = 0xfebeb800u;
  if (DAT_febe67d6 < DAT_0002b712) {
    uVar3 = 0;
    uVar4 = DAT_febe67d6 + 1;
  }
  else {
    puVar2 = 0xfebeb800u;
    FUN_00050c82(1,0);
    if ((uVar1 >> 1 & 1) == 0) {
      FUN_00056cda(1,0x20000);
    }
    uVar3 = 1;
  }
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x502a)))) = uVar4;
  return uVar3;
}

undefined4 FUN_0003f54a(void)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  iVar3 = 0;
  uVar1 = 1;
  iVar2 = 0;
  if (DAT_febe67d8 < DAT_0002b714) {
    iVar4 = 0;
    DAT_febe67d8 = DAT_febe67d8 + 1;
  }
  else {
    iVar4 = 0x5a;
  }
  if (DAT_febe67da < DAT_0002b716) {
    DAT_febe67da = DAT_febe67da + 1;
  }
  else {
    iVar3 = 0x5a;
  }
  if (DAT_febe67dc < DAT_0002b718) {
    DAT_febe67dc = DAT_febe67dc + 1;
  }
  else {
    iVar2 = 0x5a;
  }
  if ((iVar4 == 0x5a) && (iVar3 == 0x5a)) {
    if (iVar2 == 0x5a) {
      uVar1 = 2;
    }
    else {
      uVar1 = 1;
    }
  }
  return uVar1;
}

uint f33_classify_command_status_bit_clear_b(void)

{
  if ((((DAT_febe64d9 == '\0') && (DAT_febe64d1 == '\0')) && ((DAT_febe6620 >> 0x12 & 1) != 0)) &&
     ((((DAT_febe661c >> 0x12 & 1) != 0 && ((DAT_febe6628 >> 0x11 & 1) == 0)) &&
      (((DAT_febe6614 & 1) == 0 && (DAT_febe65f0 == 'Z')))))) {
    if (DAT_febe8292 != '\0') {
      return 0x11;
    }
    return 0x22;
  }
  return 0x44;
}

void f33_reset_bounded_sample_or_status_a(void)

{
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xfebe7624u)))));
  return;
}

void FUN_0003f702(void)

{
  DAT_febe67e0 = 0;
  DAT_febe67e4 = 0;
  DAT_febe67e2 = 0;
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xfebe7624u)))));
  return;
}

uint f33_admit_bounded_sample_monitor_a(void)

{
  uint uVar1;
  
  uVar1 = (uint)DAT_febe67e0;
  if (uVar1 != 0x5a) {
    if (DAT_febe67e2 < DAT_0002b71c) {
      DAT_febe67e2 = DAT_febe67e2 + 1;
    }
    else {
      uVar1 = 0x5a;
    }
  }
  DAT_febe67e0 = (char)uVar1;
  return uVar1;
}

uint f33_classify_bounded_sample_or_status_a(void)

{
  uint uVar1;
  
  if (((((DAT_febe64d8 == '\0') && (DAT_febe64d0 == '\0')) && ((DAT_febe6620 >> 2 & 1) != 0)) &&
      (((DAT_febe661c >> 2 & 1) != 0 && ((DAT_febe6628 >> 1 & 1) == 0)))) &&
     (((DAT_febe6614 & 1) == 0 && (DAT_febe65f0 == 'Z')))) {
    if ((DAT_febe66bc < DAT_0002b71a) || (DAT_febe8284 == 'Z')) {
      uVar1 = 0x22;
    }
    else {
      uVar1 = 0x11;
    }
  }
  else {
    DAT_febe67e4 = DAT_febe67e4 + 1;
    uVar1 = 0x44;
  }
  return uVar1;
}

void f33_reset_bounded_sample_or_status_b(void)

{
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xfebe762cu)))));
  return;
}

void FUN_0003f88e(void)

{
  DAT_febe67e8 = 0;
  DAT_febe67ec = 0;
  DAT_febe67ea = 0;
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xfebe762cu)))));
  return;
}

uint f33_admit_bounded_sample_monitor_b(void)

{
  uint uVar1;
  
  uVar1 = (uint)DAT_febe67e8;
  if (uVar1 != 0x5a) {
    if (DAT_febe67ea < DAT_0002b724) {
      DAT_febe67ea = DAT_febe67ea + 1;
    }
    else {
      uVar1 = 0x5a;
    }
  }
  DAT_febe67e8 = (char)uVar1;
  return uVar1;
}

uint f33_classify_bounded_sample_or_status_b(void)

{
  uint uVar1;
  
  if (((((DAT_febe64d9 == '\0') && (DAT_febe64d1 == '\0')) && ((DAT_febe6620 >> 0x12 & 1) != 0)) &&
      (((DAT_febe661c >> 0x12 & 1) != 0 && ((DAT_febe6628 >> 0x11 & 1) == 0)))) &&
     (((DAT_febe6614 & 1) == 0 && (DAT_febe65f0 == 'Z')))) {
    if ((DAT_febe66be < DAT_0002b722) || (DAT_febe8283 == 'Z')) {
      uVar1 = 0x22;
    }
    else {
      uVar1 = 0x11;
    }
  }
  else {
    DAT_febe67ec = DAT_febe67ec + 1;
    uVar1 = 0x44;
  }
  return uVar1;
}

void f33_reset_requested_state_sample_threshold_a(void)

{
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xfebe7634u)))));
  return;
}

void FUN_0003fa1a(void)

{
  DAT_febe763c = 0;
  DAT_febe763d = 0;
  DAT_febe763e = 0;
  DAT_febe7640 = 0;
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xfebe7634u)))));
  return;
}

bool FUN_0003fa36(void)

{
  bool bVar1;
  uint32_t puVar2;
  ushort uVar3;
  
  uVar3 = DAT_febe763e;
  puVar2 = 0xfebeb800u;
  bVar1 = DAT_febe763e < DAT_0002b72a;
  if (bVar1) {
    uVar3 = DAT_febe763e + 1;
  }
  else {
    puVar2 = 0xfebeb800u;
    f33_set_channel_owner_request('\0',0);
  }
  (*((ushort *)camry_host_ptr((uint32_t)((0xffffbe3eu + (uint32_t)((int)puVar2)))))) = uVar3;
  return !bVar1;
}

undefined4 FUN_0003fa62(void)

{
  undefined4 uVar1;
  
  uVar1 = 1;
  if (DAT_febe7640 < DAT_0002b72c) {
    DAT_febe7640 = DAT_febe7640 + 1;
  }
  else {
    uVar1 = 2;
  }
  return uVar1;
}

uint f33_classify_requested_state_sample_threshold_a(void)

{
  if (((((DAT_febe64d8 != '\x02') || (DAT_febe64d0 != '\0')) || ((DAT_febe6620 >> 2 & 1) == 0)) ||
      (((DAT_febe661c >> 2 & 1) == 0 || ((DAT_febe6628 >> 1 & 1) != 0)))) ||
     (((DAT_febe6614 & 1) == 0 || (DAT_febe65f0 != 'Z')))) {
    return 0x44;
  }
  if (((DAT_febe66b2 <= DAT_0002b730) || (DAT_0002b72e < DAT_febe66b8)) &&
     ((DAT_febe66b2 <= DAT_0002b732 || (DAT_febe66b8 <= DAT_0002b72e)))) {
    return 0x11;
  }
  return 0x22;
}

void f33_reset_requested_state_sample_threshold_b(void)

{
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xfebe7644u)))));
  return;
}

void FUN_0003fbf4(void)

{
  DAT_febe764c = 0;
  DAT_febe764d = 0;
  DAT_febe764e = 0;
  DAT_febe7650 = 0;
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xfebe7644u)))));
  return;
}

bool FUN_0003fc10(void)

{
  bool bVar1;
  uint32_t puVar2;
  ushort uVar3;
  
  uVar3 = DAT_febe764e;
  puVar2 = 0xfebeb800u;
  bVar1 = DAT_febe764e < DAT_0002b736;
  if (bVar1) {
    uVar3 = DAT_febe764e + 1;
  }
  else {
    puVar2 = 0xfebeb800u;
    f33_set_channel_owner_request('\x01',0);
  }
  (*((ushort *)camry_host_ptr((uint32_t)((0xffffbe4eu + (uint32_t)((int)puVar2)))))) = uVar3;
  return !bVar1;
}

undefined4 FUN_0003fc3c(void)

{
  undefined4 uVar1;
  
  uVar1 = 1;
  if (DAT_febe7650 < DAT_0002b738) {
    DAT_febe7650 = DAT_febe7650 + 1;
  }
  else {
    uVar1 = 2;
  }
  return uVar1;
}

uint f33_classify_requested_state_sample_threshold_b(void)

{
  if (((((DAT_febe64d9 != '\x02') || (DAT_febe64d1 != '\0')) || ((DAT_febe6620 >> 0x12 & 1) == 0))
      || (((DAT_febe661c >> 0x12 & 1) == 0 || ((DAT_febe6628 >> 0x11 & 1) != 0)))) ||
     (((DAT_febe6614 & 1) == 0 || (DAT_febe65f0 != 'Z')))) {
    return 0x44;
  }
  if (((DAT_febe66b4 <= DAT_0002b73c) || (DAT_0002b73a < DAT_febe66b8)) &&
     ((DAT_febe66b4 <= DAT_0002b73e || (DAT_febe66b8 <= DAT_0002b73a)))) {
    return 0x11;
  }
  return 0x22;
}

void f33_reset_asserted_state_sample_threshold_a(void)

{
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xfebe67f0u)))));
  return;
}

void f33_reset_asserted_state_sample_threshold_a_3fdce(void)

{
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xfebe67f0u)))));
  return;
}

uint f33_classify_asserted_state_sample_threshold_a(void)

{
  if (((((DAT_febe64d8 != '\x02') || (DAT_febe64d0 != '\0')) || ((DAT_febe6620 >> 1 & 1) == 0)) ||
      (((DAT_febe6620 >> 2 & 1) != 0 || ((DAT_febe661c >> 2 & 1) == 0)))) ||
     (((DAT_febe6628 >> 1 & 1) == 0 || (((DAT_febe6614 & 1) != 0 || (DAT_febe65f0 != 'Z')))))) {
    return 0x44;
  }
  if (((DAT_0002b744 <= DAT_febe66b2) || (DAT_0002b742 < DAT_febe66b8)) &&
     ((DAT_0002b746 <= DAT_febe66b2 || (DAT_febe66b8 <= DAT_0002b742)))) {
    return 0x11;
  }
  return 0x22;
}

void f33_reset_asserted_state_sample_threshold_b(void)

{
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xfebe67f8u)))));
  return;
}

void f33_reset_asserted_state_sample_threshold_b_3ff08(void)

{
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xfebe67f8u)))));
  return;
}

uint f33_classify_asserted_state_sample_threshold_b(void)

{
  if (((((DAT_febe64d9 != '\x02') || (DAT_febe64d1 != '\0')) || ((DAT_febe6620 >> 0x11 & 1) == 0))
      || (((DAT_febe6620 >> 0x12 & 1) != 0 || ((DAT_febe661c >> 0x12 & 1) == 0)))) ||
     (((DAT_febe6628 >> 0x11 & 1) == 0 || (((DAT_febe6614 & 1) != 0 || (DAT_febe65f0 != 'Z')))))) {
    return 0x44;
  }
  if (((DAT_0002b74c <= DAT_febe66b4) || (DAT_0002b74a < DAT_febe66b8)) &&
     ((DAT_0002b74e <= DAT_febe66b4 || (DAT_febe66b8 <= DAT_0002b74a)))) {
    return 0x11;
  }
  return 0x22;
}

void f33_reset_sample_difference_window_a(void)

{
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xfebe7654u)))));
  return;
}

void FUN_00040042(void)

{
  DAT_febe6800 = 0;
  DAT_febe6801 = 0;
  DAT_febe6802 = 0;
  DAT_febe6804 = 0;
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xfebe7654u)))));
  return;
}

uint f33_admit_sample_difference_monitor_a(void)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  
  uVar2 = (uint)DAT_febe6800;
  iVar1 = (uint)DAT_febe66b8 - (uint)DAT_febe66ae;
  if (uVar2 != 0x5a) {
    if (DAT_febe65f0 == 'Z') {
      iVar3 = (int)DAT_0002b758;
      if ((iVar1 - iVar3 < 0 == (iVar1 < 0 != iVar3 < 0 && iVar3 < 0 == iVar1 - iVar3 < 0) &&
           iVar1 != iVar3) && (DAT_febe6802 <= DAT_0002b752)) {
        DAT_febe6802 = DAT_febe6802 + 1;
      }
      else {
        uVar2 = 0x5a;
      }
    }
    else {
      DAT_febe6802 = 0;
    }
  }
  DAT_febe6800 = (char)uVar2;
  return uVar2;
}

uint f33_admit_sample_difference_elapsed_a(void)

{
  uint uVar1;
  
  uVar1 = (uint)DAT_febe6801;
  if (uVar1 != 0x5a) {
    if (DAT_febe6804 < DAT_0002b754) {
      DAT_febe6804 = DAT_febe6804 + 1;
    }
    else {
      uVar1 = 0x5a;
    }
  }
  DAT_febe6801 = (char)uVar1;
  return uVar1;
}

uint f33_classify_sample_difference_window_a(void)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  
  uVar2 = (uint)DAT_febe66b8;
  iVar1 = uVar2 - DAT_febe66ae;
  if (((((DAT_febe64d8 != '\0') || (DAT_febe64d0 != '\0')) || ((DAT_febe6620 >> 2 & 1) == 0)) ||
      (((DAT_febe661c >> 2 & 1) == 0 || ((DAT_febe6628 >> 1 & 1) != 0)))) ||
     (((DAT_febe6614 & 1) != 0 || (DAT_febe65f0 != 'Z')))) {
    return 0x44;
  }
  iVar3 = (int)DAT_0002b758;
  if (((iVar1 - iVar3 < 0 != (iVar1 < 0 != iVar3 < 0 && iVar3 < 0 == iVar1 - iVar3 < 0) ||
        iVar1 == iVar3) || (DAT_0002b756 < uVar2)) &&
     (((uint)DAT_0002b75a <= (uint)DAT_febe66ae || (uVar2 <= DAT_0002b756)))) {
    return 0x11;
  }
  return 0x22;
}

void f33_reset_sample_difference_window_b(void)

{
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xfebe765cu)))));
  return;
}

void FUN_00040222(void)

{
  DAT_febe6808 = 0;
  DAT_febe6809 = 0;
  DAT_febe680a = 0;
  DAT_febe680c = 0;
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xfebe765cu)))));
  return;
}

uint f33_admit_sample_difference_monitor_b(void)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  
  uVar2 = (uint)DAT_febe6808;
  iVar1 = (uint)DAT_febe66b8 - (uint)DAT_febe66b0;
  if (uVar2 != 0x5a) {
    if (DAT_febe65f0 == 'Z') {
      iVar3 = (int)DAT_0002b764;
      if ((iVar1 - iVar3 < 0 == (iVar1 < 0 != iVar3 < 0 && iVar3 < 0 == iVar1 - iVar3 < 0) &&
           iVar1 != iVar3) && (DAT_febe680a <= DAT_0002b75e)) {
        DAT_febe680a = DAT_febe680a + 1;
      }
      else {
        uVar2 = 0x5a;
      }
    }
    else {
      DAT_febe680a = 0;
    }
  }
  DAT_febe6808 = (char)uVar2;
  return uVar2;
}

uint f33_admit_sample_difference_elapsed_b(void)

{
  uint uVar1;
  
  uVar1 = (uint)DAT_febe6809;
  if (uVar1 != 0x5a) {
    if (DAT_febe680c < DAT_0002b760) {
      DAT_febe680c = DAT_febe680c + 1;
    }
    else {
      uVar1 = 0x5a;
    }
  }
  DAT_febe6809 = (char)uVar1;
  return uVar1;
}

uint f33_classify_sample_difference_window_b(void)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  
  uVar3 = (uint)DAT_febe66b8;
  iVar1 = uVar3 - DAT_febe66b0;
  if (((((DAT_febe64d9 != '\0') || (DAT_febe64d1 != '\0')) || ((DAT_febe6620 >> 0x12 & 1) == 0)) ||
      (((DAT_febe661c >> 0x12 & 1) == 0 || ((DAT_febe6628 >> 0x11 & 1) != 0)))) ||
     (((DAT_febe6614 & 1) != 0 || (DAT_febe65f0 != 'Z')))) {
    return 0x44;
  }
  iVar2 = (int)DAT_0002b764;
  if (((iVar1 - iVar2 < 0 != (iVar1 < 0 != iVar2 < 0 && iVar2 < 0 == iVar1 - iVar2 < 0) ||
        iVar1 == iVar2) || (DAT_0002b762 < uVar3)) &&
     (((uint)DAT_0002b766 <= (uint)DAT_febe66b0 || (uVar3 <= DAT_0002b762)))) {
    return 0x11;
  }
  return 0x22;
}

void f33_reset_matched_state2_status_bit_a(void)

{
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xfebe7664u)))));
  return;
}

void FUN_00040402(void)

{
  DAT_febe6811 = 0;
  DAT_febe6810 = 0;
  DAT_febe6812 = 0;
  DAT_febe6814 = 0;
  DAT_febe6816 = 0;
  DAT_febe6818 = 0;
  DAT_febe681a = 0;
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xfebe7664u)))));
  return;
}

undefined4 FUN_00040424(void)

{
  int iVar1;
  uint32_t puVar2;
  undefined4 uVar3;
  int iVar4;
  int iVar5;
  ushort uVar6;
  ushort uVar7;
  ushort uVar8;
  
  puVar2 = 0xfebeb800u;
  uVar3 = 0;
  iVar5 = 0;
  iVar4 = 0;
  if (DAT_febe6814 < DAT_0002b76c) {
    iVar1 = 0;
    uVar8 = DAT_febe6814 + 1;
  }
  else {
    iVar1 = 0x5a;
    uVar8 = DAT_febe6814;
  }
  if (DAT_febe6816 < DAT_0002b76e) {
    uVar7 = DAT_febe6816 + 1;
  }
  else {
    iVar5 = 0x5a;
    uVar7 = DAT_febe6816;
  }
  if (DAT_febe6818 < DAT_0002b770) {
    uVar6 = DAT_febe6818 + 1;
  }
  else {
    iVar4 = 0x5a;
    uVar6 = DAT_febe6818;
  }
  if (((iVar1 == 0x5a) && (iVar5 == 0x5a)) && (iVar4 == 0x5a)) {
    puVar2 = 0xfebeb800u;
    if ((DAT_febe6764 & 1) == 0) {
      puVar2 = 0xfebeb800u;
      FUN_00056c26(DAT_febe6764 & 1,4);
    }
    uVar3 = 1;
  }
  (*((ushort *)camry_host_ptr((uint32_t)((0xffffb014u + (uint32_t)((int)puVar2)))))) = uVar8;
  (*((ushort *)camry_host_ptr((uint32_t)((0xffffb016u + (uint32_t)((int)puVar2)))))) = uVar7;
  (*((ushort *)camry_host_ptr((uint32_t)((0xffffb018u + (uint32_t)((int)puVar2)))))) = uVar6;
  return uVar3;
}

undefined4 FUN_0004049e(void)

{
  undefined4 uVar1;
  
  uVar1 = 1;
  if (DAT_febe681a < DAT_0002b772) {
    DAT_febe681a = DAT_febe681a + 1;
  }
  else {
    uVar1 = 2;
  }
  return uVar1;
}

uint f33_classify_matched_state2_status_bit_a(void)

{
  if ((((((DAT_febe64d8 == '\x02') && (DAT_febe64d0 == '\x02')) && ((DAT_febe6620 >> 1 & 1) == 0))
       && (((DAT_febe6620 >> 2 & 1) != 0 && ((DAT_febe661c >> 1 & 1) == 0)))) &&
      (((DAT_febe661c >> 2 & 1) != 0 &&
       (((DAT_febe6628 >> 1 & 1) == 0 && ((DAT_febe6614 & 1) == 0)))))) && (DAT_febe65f6 == 'Z')) {
    if (DAT_febe8282 != 'Z') {
      return 0x11;
    }
    return 0x22;
  }
  return 0x44;
}

void f33_reset_matched_state2_status_bit_b(void)

{
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xfebe766cu)))));
  return;
}

void FUN_0004063e(void)

{
  DAT_febe681d = 0;
  DAT_febe681c = 0;
  DAT_febe681e = 0;
  DAT_febe6820 = 0;
  DAT_febe6822 = 0;
  DAT_febe6824 = 0;
  DAT_febe6826 = 0;
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xfebe766cu)))));
  return;
}

undefined4 FUN_00040660(void)

{
  int iVar1;
  uint32_t puVar2;
  undefined4 uVar3;
  int iVar4;
  int iVar5;
  ushort uVar6;
  ushort uVar7;
  ushort uVar8;
  
  puVar2 = 0xfebeb800u;
  uVar3 = 0;
  iVar5 = 0;
  iVar4 = 0;
  if (DAT_febe6820 < DAT_0002b778) {
    iVar1 = 0;
    uVar8 = DAT_febe6820 + 1;
  }
  else {
    iVar1 = 0x5a;
    uVar8 = DAT_febe6820;
  }
  if (DAT_febe6822 < DAT_0002b77a) {
    uVar7 = DAT_febe6822 + 1;
  }
  else {
    iVar5 = 0x5a;
    uVar7 = DAT_febe6822;
  }
  if (DAT_febe6824 < DAT_0002b77c) {
    uVar6 = DAT_febe6824 + 1;
  }
  else {
    iVar4 = 0x5a;
    uVar6 = DAT_febe6824;
  }
  if (((iVar1 == 0x5a) && (iVar5 == 0x5a)) && (iVar4 == 0x5a)) {
    puVar2 = 0xfebeb800u;
    if ((DAT_febe6764 >> 1 & 1) == 0) {
      puVar2 = 0xfebeb800u;
      FUN_00056c26(1,0x40000);
    }
    uVar3 = 1;
  }
  (*((ushort *)camry_host_ptr((uint32_t)((0xffffb020u + (uint32_t)((int)puVar2)))))) = uVar8;
  (*((ushort *)camry_host_ptr((uint32_t)((0xffffb022u + (uint32_t)((int)puVar2)))))) = uVar7;
  (*((ushort *)camry_host_ptr((uint32_t)((0xffffb024u + (uint32_t)((int)puVar2)))))) = uVar6;
  return uVar3;
}

undefined4 FUN_000406da(void)

{
  undefined4 uVar1;
  
  uVar1 = 1;
  if (DAT_febe6826 < DAT_0002b77e) {
    DAT_febe6826 = DAT_febe6826 + 1;
  }
  else {
    uVar1 = 2;
  }
  return uVar1;
}

uint f33_classify_matched_state2_status_bit_b(void)

{
  if ((((((DAT_febe64d9 == '\x02') && (DAT_febe64d1 == '\x02')) && ((DAT_febe6620 >> 0x11 & 1) == 0)
        ) && (((DAT_febe6620 >> 0x12 & 1) != 0 && ((DAT_febe661c >> 0x11 & 1) == 0)))) &&
      (((DAT_febe661c & 0x40000) != 0 &&
       (((DAT_febe6628 >> 0x11 & 1) == 0 && ((DAT_febe6614 & 1) == 0)))))) && (DAT_febe65f7 == 'Z'))
  {
    if (DAT_febe8281 != 'Z') {
      return 0x11;
    }
    return 0x22;
  }
  return 0x44;
}

void f33_reset_baseline_sample_threshold_a(void)

{
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xfebe7674u)))));
  return;
}

void FUN_0004087e(void)

{
  DAT_febe6828 = 0;
  DAT_febe682a = 0;
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xfebe7674u)))));
  return;
}

uint f33_admit_baseline_sample_monitor_a(void)

{
  uint uVar1;
  
  uVar1 = (uint)DAT_febe6828;
  if (uVar1 != 0x5a) {
    if (DAT_febe682a < DAT_0002b788) {
      DAT_febe682a = DAT_febe682a + 1;
    }
    else {
      uVar1 = 0x5a;
    }
  }
  DAT_febe6828 = (char)uVar1;
  return uVar1;
}

uint f33_classify_baseline_sample_threshold_a(void)

{
  if (((((DAT_febe64d8 != '\0') || (DAT_febe64d0 != '\0')) || ((DAT_febe6620 >> 2 & 1) == 0)) ||
      (((DAT_febe661c >> 2 & 1) == 0 || ((DAT_febe6628 >> 1 & 1) != 0)))) ||
     (((DAT_febe6614 & 1) != 0 || (DAT_febe65f0 != 'Z')))) {
    return 0x44;
  }
  if (((DAT_febe66b2 <= DAT_0002b784) || (DAT_0002b782 < DAT_febe66b8)) &&
     ((DAT_febe66b2 <= DAT_0002b786 || (DAT_febe66b8 <= DAT_0002b782)))) {
    return 0x11;
  }
  return 0x22;
}

void f33_reset_baseline_sample_threshold_b(void)

{
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xfebe767cu)))));
  return;
}

void FUN_000409f6(void)

{
  DAT_febe682c = 0;
  DAT_febe682e = 0;
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xfebe767cu)))));
  return;
}

uint f33_admit_baseline_sample_monitor_b(void)

{
  uint uVar1;
  
  uVar1 = (uint)DAT_febe682c;
  if (uVar1 != 0x5a) {
    if (DAT_febe682e < DAT_0002b790) {
      DAT_febe682e = DAT_febe682e + 1;
    }
    else {
      uVar1 = 0x5a;
    }
  }
  DAT_febe682c = (char)uVar1;
  return uVar1;
}

uint f33_classify_baseline_sample_threshold_b(void)

{
  if (((((DAT_febe64d9 != '\0') || (DAT_febe64d1 != '\0')) || ((DAT_febe6620 >> 0x12 & 1) == 0)) ||
      (((DAT_febe661c >> 0x12 & 1) == 0 || ((DAT_febe6628 >> 0x11 & 1) != 0)))) ||
     (((DAT_febe6614 & 1) != 0 || (DAT_febe65f0 != 'Z')))) {
    return 0x44;
  }
  if (((DAT_febe66b4 <= DAT_0002b78c) || (DAT_0002b78a < DAT_febe66b8)) &&
     ((DAT_febe66b4 <= DAT_0002b78e || (DAT_febe66b8 <= DAT_0002b78a)))) {
    return 0x11;
  }
  return 0x22;
}

void f33_reset_observed_state_sample_regions_a(void)

{
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xfebe7684u)))));
  return;
}

void FUN_00040b6e(void)

{
  DAT_febe6830 = 0;
  DAT_febe6831 = 0;
  DAT_febe6832 = 0;
  DAT_febe6836 = 0;
  DAT_febe6834 = 0;
  DAT_febe6838 = 0;
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xfebe7684u)))));
  return;
}

undefined4 FUN_00040b8e(void)

{
  uint32_t puVar1;
  undefined4 uVar2;
  ushort uVar3;
  
  uVar3 = DAT_febe6832;
  puVar1 = 0xfebeb800u;
  if (DAT_febe6832 < DAT_0002b792) {
    uVar2 = 0;
    uVar3 = DAT_febe6832 + 1;
  }
  else {
    puVar1 = 0xfebeb800u;
    if ((DAT_febe6764 & 1) == 0) {
      puVar1 = 0xfebeb800u;
      FUN_000569ac(DAT_febe6764 & 1,2);
    }
    uVar2 = 1;
  }
  (*((ushort *)camry_host_ptr((uint32_t)((0xffffb032u + (uint32_t)((int)puVar1)))))) = uVar3;
  return uVar2;
}

undefined4 FUN_00040bc4(void)

{
  uint32_t puVar1;
  undefined4 uVar2;
  ushort uVar3;
  
  uVar3 = DAT_febe6836;
  puVar1 = 0xfebeb800u;
  if (DAT_febe6836 < DAT_0002b796) {
    uVar2 = 1;
    uVar3 = DAT_febe6836 + 1;
  }
  else {
    puVar1 = 0xfebeb800u;
    if ((DAT_febe6764 & 1) == 0) {
      puVar1 = 0xfebeb800u;
      FUN_00056f14(DAT_febe6764 & 1,2);
    }
    uVar2 = 2;
  }
  (*((ushort *)camry_host_ptr((uint32_t)((0xffffb036u + (uint32_t)((int)puVar1)))))) = uVar3;
  return uVar2;
}

undefined4 FUN_00040bfa(void)

{
  undefined4 uVar1;
  
  uVar1 = 2;
  if (DAT_febe6834 < DAT_0002b794) {
    DAT_febe6834 = DAT_febe6834 + 1;
  }
  else {
    uVar1 = 3;
  }
  return uVar1;
}

undefined4 FUN_00040c18(void)

{
  undefined4 uVar1;
  
  if (DAT_0002b798 < DAT_febe6838) {
    uVar1 = 0x5a;
  }
  else {
    DAT_febe6838 = DAT_febe6838 + 1;
    uVar1 = 0;
  }
  return uVar1;
}

void f33_reset_observed_state_sample_regions_b(void)

{
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xfebe768cu)))));
  return;
}

void FUN_00040e08(void)

{
  DAT_febe683c = 0;
  DAT_febe683d = 0;
  DAT_febe683e = 0;
  DAT_febe6842 = 0;
  DAT_febe6840 = 0;
  DAT_febe6844 = 0;
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xfebe768cu)))));
  return;
}

undefined4 FUN_00040e28(void)

{
  uint32_t puVar1;
  undefined4 uVar2;
  ushort uVar3;
  
  uVar3 = DAT_febe683e;
  puVar1 = 0xfebeb800u;
  if (DAT_febe683e < DAT_0002b7aa) {
    uVar2 = 0;
    uVar3 = DAT_febe683e + 1;
  }
  else {
    puVar1 = 0xfebeb800u;
    if ((DAT_febe6764 >> 1 & 1) == 0) {
      puVar1 = 0xfebeb800u;
      FUN_000569ac(1,0x20000);
    }
    uVar2 = 1;
  }
  (*((ushort *)camry_host_ptr((uint32_t)((0xffffb03eu + (uint32_t)((int)puVar1)))))) = uVar3;
  return uVar2;
}

undefined4 FUN_00040e5e(void)

{
  uint32_t puVar1;
  undefined4 uVar2;
  ushort uVar3;
  
  uVar3 = DAT_febe6842;
  puVar1 = 0xfebeb800u;
  uVar2 = 1;
  if (DAT_febe6842 < DAT_0002b7ae) {
    uVar3 = DAT_febe6842 + 1;
  }
  else {
    puVar1 = 0xfebeb800u;
    if ((DAT_febe6764 >> 1 & 1) == 0) {
      puVar1 = 0xfebeb800u;
      FUN_00056f14(1,0x20000);
    }
    uVar2 = 2;
  }
  (*((ushort *)camry_host_ptr((uint32_t)((int)(0xffffb042u + (uint32_t)((int)puVar1)))))) = uVar3;
  return uVar2;
}

undefined4 FUN_00040e94(void)

{
  undefined4 uVar1;
  
  uVar1 = 2;
  if (DAT_febe6840 < DAT_0002b7ac) {
    DAT_febe6840 = DAT_febe6840 + 1;
  }
  else {
    uVar1 = 3;
  }
  return uVar1;
}

undefined4 FUN_00040eb2(void)

{
  undefined4 uVar1;
  
  if (DAT_0002b7b0 < DAT_febe6844) {
    uVar1 = 0x5a;
  }
  else {
    DAT_febe6844 = DAT_febe6844 + 1;
    uVar1 = 0;
  }
  return uVar1;
}

void FUN_00041096(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe76ac = 0;
  DAT_febe76ae = 0;
  DAT_febe76b0 = 0;
  f33_reset_terminal_monitor(f33_sample_range_triplet_a_states);
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbe9cu + (uint32_t)((int)puVar1))))));
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbea4u + (uint32_t)((int)puVar1))))));
  return;
}

void FUN_000410c0(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe684a = 0;
  f33_reset_terminal_monitor(f33_sample_range_triplet_a_states);
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbe9cu + (uint32_t)((int)puVar1))))));
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbea4u + (uint32_t)((int)puVar1))))));
  return;
}

uint f33_admit_sample_range_triplet_a(void)

{
  uint uVar1;
  
  uVar1 = (uint)DAT_febe6848;
  if (uVar1 != 0x5a) {
    if (DAT_febe684c < DAT_0002b7c6) {
      DAT_febe684c = DAT_febe684c + 1;
    }
    else {
      uVar1 = 0x5a;
    }
  }
  DAT_febe6848 = (char)uVar1;
  return uVar1;
}

uint f33_classify_sample_range_triplet_a(void)

{
  undefined2 uVar1;
  
  if ((((((DAT_febe64d8 == '\x02') && (DAT_febe64d0 == '\x02')) && ((DAT_febe6620 >> 1 & 1) == 0))
       && (((DAT_febe6620 >> 2 & 1) != 0 && ((DAT_febe661c >> 1 & 1) == 0)))) &&
      (((DAT_febe661c >> 2 & 1) != 0 &&
       (((DAT_febe6628 >> 1 & 1) == 0 && ((DAT_febe6614 & 1) == 0)))))) && (DAT_febe65f2 == 'Z')) {
    uVar1 = DAT_febe76ac;
    if ((DAT_febe76b0 <= DAT_0002b7c2) && (uVar1 = DAT_febe76ae, DAT_0002b7c4 <= DAT_febe76b0)) {
      return 0x11;
    }
    DAT_febe684a = uVar1;
    return 0x22;
  }
  return 0x44;
}

void FUN_00041300(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe76cc = 0;
  DAT_febe76ce = 0;
  DAT_febe76d0 = 0;
  f33_reset_terminal_monitor(f33_sample_range_triplet_b_states);
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbebcu + (uint32_t)((int)puVar1))))));
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbec4u + (uint32_t)((int)puVar1))))));
  return;
}

void FUN_0004132a(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe6852 = 0;
  f33_reset_terminal_monitor(f33_sample_range_triplet_b_states);
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbebcu + (uint32_t)((int)puVar1))))));
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbec4u + (uint32_t)((int)puVar1))))));
  return;
}

uint f33_admit_sample_range_triplet_b(void)

{
  uint uVar1;
  
  uVar1 = (uint)DAT_febe6850;
  if (uVar1 != 0x5a) {
    if (DAT_febe6854 < DAT_0002b7ce) {
      DAT_febe6854 = DAT_febe6854 + 1;
    }
    else {
      uVar1 = 0x5a;
    }
  }
  DAT_febe6850 = (char)uVar1;
  return uVar1;
}

void FUN_0004156e(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe76ec = 0;
  DAT_febe76ee = 0;
  f33_reset_terminal_monitor(f33_startup_status_bit_triplet_a_states);
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbedcu + (uint32_t)((int)puVar1))))));
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbee4u + (uint32_t)((int)puVar1))))));
  return;
}

void FUN_00041596(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe6858 = 0;
  DAT_febe6859 = 0;
  DAT_febe685a = 0;
  f33_reset_terminal_monitor(f33_startup_status_bit_triplet_a_states);
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbedcu + (uint32_t)((int)puVar1))))));
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbee4u + (uint32_t)((int)puVar1))))));
  return;
}

uint f33_classify_startup_status_bit_triplet_a(void)

{
  if ((((DAT_febe64d8 == '\0') && (DAT_febe64d0 == '\0')) && ((DAT_febe6620 >> 2 & 1) != 0)) &&
     ((((DAT_febe661c >> 2 & 1) != 0 && ((DAT_febe6628 >> 1 & 1) == 0)) &&
      (((DAT_febe6614 & 1) != 0 && (DAT_febe65f0 == 'Z')))))) {
    if (DAT_febe76ec != 'Z') {
      return 0x11;
    }
    return 0x22;
  }
  return 0x44;
}

void FUN_000417a6(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe7708 = 0;
  DAT_febe770a = 0;
  f33_reset_terminal_monitor(f33_startup_status_bit_triplet_b_states);
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbef8u + (uint32_t)((int)puVar1))))));
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbf00u + (uint32_t)((int)puVar1))))));
  return;
}

void FUN_000417ce(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe685c = 0;
  DAT_febe685d = 0;
  DAT_febe685e = 0;
  f33_reset_terminal_monitor(f33_startup_status_bit_triplet_b_states);
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbef8u + (uint32_t)((int)puVar1))))));
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbf00u + (uint32_t)((int)puVar1))))));
  return;
}

uint f33_classify_startup_status_bit_triplet_b(void)

{
  if ((((DAT_febe64d9 == '\0') && (DAT_febe64d1 == '\0')) && ((DAT_febe6620 >> 0x12 & 1) != 0)) &&
     ((((DAT_febe661c >> 0x12 & 1) != 0 && ((DAT_febe6628 >> 0x11 & 1) == 0)) &&
      (((DAT_febe6614 & 1) != 0 && (DAT_febe65f0 == 'Z')))))) {
    if (DAT_febe7708 != 'Z') {
      return 0x11;
    }
    return 0x22;
  }
  return 0x44;
}

void FUN_000419de(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe7724 = 0;
  DAT_febe7726 = 0;
  f33_reset_terminal_monitor(f33_matched_state2_startup_triplet_a_states);
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbf14u + (uint32_t)((int)puVar1))))));
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbf1cu + (uint32_t)((int)puVar1))))));
  return;
}

void FUN_00041a06(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe6860 = 0;
  DAT_febe6861 = 0;
  f33_reset_terminal_monitor(f33_matched_state2_startup_triplet_a_states);
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbf14u + (uint32_t)((int)puVar1))))));
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbf1cu + (uint32_t)((int)puVar1))))));
  return;
}

uint f33_classify_matched_state2_startup_triplet_a(void)

{
  if ((((((DAT_febe64d8 == '\x02') && (DAT_febe64d0 == '\x02')) && ((DAT_febe6620 >> 1 & 1) == 0))
       && (((DAT_febe6620 >> 2 & 1) != 0 && ((DAT_febe661c >> 1 & 1) == 0)))) &&
      (((DAT_febe661c >> 2 & 1) != 0 &&
       (((DAT_febe6628 >> 1 & 1) == 0 && ((DAT_febe6614 & 1) == 0)))))) && (DAT_febe65f6 == 'Z')) {
    if (DAT_febe7724 != 'Z') {
      return 0x11;
    }
    return 0x22;
  }
  return 0x44;
}

void FUN_00041c0e(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe7740 = 0;
  DAT_febe7742 = 0;
  f33_reset_terminal_monitor(f33_matched_state2_startup_triplet_b_states);
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbf30u + (uint32_t)((int)puVar1))))));
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbf38u + (uint32_t)((int)puVar1))))));
  return;
}

void FUN_00041c36(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe6864 = 0;
  DAT_febe6865 = 0;
  f33_reset_terminal_monitor(f33_matched_state2_startup_triplet_b_states);
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbf30u + (uint32_t)((int)puVar1))))));
  f33_reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbf38u + (uint32_t)((int)puVar1))))));
  return;
}

uint f33_classify_matched_state2_startup_triplet_b(void)

{
  if ((((((DAT_febe64d9 == '\x02') && (DAT_febe64d1 == '\x02')) && ((DAT_febe6620 >> 0x11 & 1) == 0)
        ) && (((DAT_febe6620 >> 0x12 & 1) != 0 && ((DAT_febe661c >> 0x11 & 1) == 0)))) &&
      (((DAT_febe661c & 0x40000) != 0 &&
       (((DAT_febe6628 >> 0x11 & 1) == 0 && ((DAT_febe6614 & 1) == 0)))))) && (DAT_febe65f7 == 'Z'))
  {
    if (DAT_febe7740 != 'Z') {
      return 0x11;
    }
    return 0x22;
  }
  return 0x44;
}

void FUN_00041e42(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe7744 = 0;
  DAT_febe7746 = 0;
  DAT_febe7748 = 0;
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe774cu)));
  f33_reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xffffbf58u + (uint32_t)((int)puVar1))))));
  f33_reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xffffbf64u + (uint32_t)((int)puVar1))))));
  return;
}

void FUN_00041e6c(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe7744 = 0;
  DAT_febe7746 = 0;
  DAT_febe7748 = 0;
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe774cu)));
  f33_reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xffffbf58u + (uint32_t)((int)puVar1))))));
  f33_reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xffffbf64u + (uint32_t)((int)puVar1))))));
  return;
}

void FUN_00042132(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe77b4 = 0;
  DAT_febe77b6 = 0;
  DAT_febe77b8 = 0;
  DAT_febe77bc = 0;
  f33_reset_windowed_monitor((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe7784u)));
  f33_reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)((0xffffbf94u + (uint32_t)((int)puVar1))))));
  f33_reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)((0xffffbfa4u + (uint32_t)((int)puVar1))))));
  return;
}

void FUN_0004215e(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe77b4 = 0;
  DAT_febe77b6 = 0;
  DAT_febe77b8 = 0;
  DAT_febe77bc = 0;
  f33_reset_windowed_monitor((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe7784u)));
  f33_reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)((0xffffbf94u + (uint32_t)((int)puVar1))))));
  f33_reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)((0xffffbfa4u + (uint32_t)((int)puVar1))))));
  return;
}

void FUN_000423b0(void)

{
  DAT_febe77c2 = 0;
  return;
}

void FUN_000423b6(void)

{
  DAT_febe77c2 = 0;
  return;
}

void f33_fill_constant_block_4246e(void)

{
  DAT_febe77c4 = 0;
  DAT_febe77c5 = 0;
  DAT_febe77c6 = 0;
  DAT_febe77c7 = 0;
  DAT_febe77c8 = 0x8000;
  DAT_febe77ca = 0x8000;
  DAT_febe77cc = 0x8000;
  return;
}

int f33_sum_channel_snapshot_differences_a(void)

{
  ushort uVar1;
  char cVar4;
  char cVar5;
  ushort uVar2;
  ushort uVar3;
  
  uVar1 = DAT_febe8238;
  uVar2 = DAT_febe823c;
  uVar3 = DAT_febe823a;
  if (DAT_00031e5e != 'Z') goto LAB_000424f0;
  if (DAT_febeeac1 == 'Z') {
    cVar4 = DAT_febe7e21;
    cVar5 = DAT_febe7e22;
    if (DAT_febe7e20 == 'Z') goto LAB_000424b6;
  }
  else {
    cVar4 = 'Z';
    cVar5 = 'Z';
LAB_000424b6:
    DAT_febe77c8 = DAT_febe8238;
  }
  if (cVar4 == 'Z') {
    DAT_febe77ca = DAT_febe823a;
  }
  uVar1 = DAT_febe77c8;
  uVar2 = DAT_febe77cc;
  uVar3 = DAT_febe77ca;
  if (cVar5 == 'Z') {
    DAT_febe77cc = DAT_febe823c;
    uVar2 = DAT_febe823c;
  }
LAB_000424f0:
  return ((uint)uVar2 - (uint)DAT_febe8230) +
         ((uint)uVar3 - (uint)DAT_febe822e) + ((uint)uVar1 - (uint)DAT_febe822c);
}

void FUN_00042592(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe77d4 = 0;
  DAT_febe77d6 = 0;
  DAT_febe77d8 = 0;
  f33_reset_windowed_monitor((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe77dcu)));
  f33_reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)((0xffffbfecu + (uint32_t)((int)puVar1))))));
  f33_reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)((0xffffbffcu + (uint32_t)((int)puVar1))))));
  f33_reset_recoverable_monitor(((F33RecoverableMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3ff4))));
  return;
}

void FUN_000425c4(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe77d4 = 0;
  DAT_febe77d6 = 0;
  DAT_febe77d8 = 0;
  f33_reset_windowed_monitor((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe77dcu)));
  f33_reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)((0xffffbfecu + (uint32_t)((int)puVar1))))));
  f33_reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)((0xffffbffcu + (uint32_t)((int)puVar1))))));
  f33_reset_recoverable_monitor(((F33RecoverableMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3ff4))));
  return;
}

uint f33_classify_channel_phase_failure_count_a(void)

{
  ushort uVar1;
  
  uVar1 = (ushort)DAT_0002b82e;
  if (((DAT_febe77e4 < uVar1) && (DAT_febe77f4 < uVar1)) && (DAT_febe7804 < uVar1)) {
    return 0x11;
  }
  return 0x22;
}

void f33_set_channel_monitor_status_a(uint index,uchar status)

{
  if ((index & 0xff) < 0xe) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7818u + (uint32_t)(index & 0xff) * 1u)))) = status;
  }
  return;
}

void f33_reset_latched_monitor_febe782c(void)

{
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe782cu)));
  return;
}

void f33_reset_latched_monitor_febe782c_42a5a(void)

{
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe782cu)));
  return;
}

undefined4 FUN_00042ac4(void)

{
  int iVar1;
  int iVar2;
  
  iVar1 = (uint)DAT_febe66b8 - (uint)DAT_febe66ae;
  if ((DAT_febe827c == 'Z') &&
     (((uint)DAT_0002b83e < (uint)DAT_febe66b8 ||
      (iVar2 = (int)DAT_0002b840,
      iVar1 - iVar2 < 0 != (iVar1 < 0 != iVar2 < 0 && iVar2 < 0 == iVar1 - iVar2 < 0) ||
      iVar1 == iVar2)))) {
    return 0x5a;
  }
  return 0;
}

undefined4 FUN_00042af4(void)

{
  char cVar1;
  uint uVar2;
  char cVar3;
  char cVar4;
  char cVar5;
  int iVar6;
  undefined4 uVar7;
  
  cVar5 = DAT_febe8280;
  cVar4 = DAT_febe827c;
  cVar3 = DAT_febe827b;
  uVar2 = DAT_febe6618;
  cVar1 = DAT_febe65f6;
  iVar6 = FUN_00042ac4();
  if ((cVar1 == 'Z') && ((uVar2 & 1) == 0)) {
    if ((cVar3 == 'Z') || ((iVar6 == 0x5a || (cVar5 == 'Z')))) {
      uVar7 = 0x22;
    }
    else if (((cVar3 == '\0') && (cVar4 == '\0')) && (cVar5 == '\0')) {
      uVar7 = 0x11;
    }
    else {
      uVar7 = 0x33;
    }
  }
  else {
    uVar7 = 0x44;
  }
  return uVar7;
}

void f33_reset_latched_monitor_febe7838(void)

{
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7838u)));
  return;
}

void f33_reset_latched_monitor_febe7838_42b84(void)

{
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7838u)));
  return;
}

uint f33_classify_channel_raw_lower_bound_a(void)

{
  if ((short)f33_output_request_status != 0) {
    return 0x44;
  }
  if ((((DAT_0002b842 <= DAT_febe6238) || (DAT_febe636c != 'Z')) &&
      ((DAT_0002b842 <= DAT_febe623a || (DAT_febe636d != 'Z')))) &&
     ((DAT_0002b842 <= DAT_febe623c || (DAT_febe636e != 'Z')))) {
    if ((DAT_0002b844 <= DAT_febe6238) &&
       ((((DAT_febe636c == 'Z' && (DAT_0002b844 <= DAT_febe623a)) && (DAT_febe636d == 'Z')) &&
        ((DAT_0002b844 <= DAT_febe623c && (DAT_febe636e == 'Z')))))) {
      return 0x11;
    }
    return 0x33;
  }
  return 0x22;
}

void f33_reset_windowed_monitor_febe7844(void)

{
  f33_reset_windowed_monitor((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe7844u)));
  return;
}

void f33_reset_windowed_monitor_febe7844_42c9a(void)

{
  f33_reset_windowed_monitor((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe7844u)));
  return;
}

void FUN_00042e00(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe7854 = 0;
  DAT_febe7856 = 0;
  DAT_febe7858 = 0;
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe785cu)));
  f33_reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3f98))));
  f33_reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3f8c))));
  return;
}

void FUN_00042e2a(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe7854 = 0;
  DAT_febe7856 = 0;
  DAT_febe7858 = 0;
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe785cu)));
  f33_reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3f98))));
  f33_reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3f8c))));
  return;
}

void FUN_000430f0(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe78c4 = 0;
  DAT_febe78c6 = 0;
  DAT_febe78c8 = 0;
  DAT_febe78cc = 0;
  f33_reset_windowed_monitor((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe7894u)));
  f33_reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3f5c))));
  f33_reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3f4c))));
  return;
}

void FUN_0004311c(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe78c4 = 0;
  DAT_febe78c6 = 0;
  DAT_febe78c8 = 0;
  DAT_febe78cc = 0;
  f33_reset_windowed_monitor((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe7894u)));
  f33_reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3f5c))));
  f33_reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3f4c))));
  return;
}

void FUN_0004336e(void)

{
  DAT_febe78d2 = 0;
  return;
}

void FUN_00043374(void)

{
  DAT_febe78d2 = 0;
  return;
}

void f33_fill_constant_block_43430(void)

{
  DAT_febe78d4 = 0;
  DAT_febe78d5 = 0;
  DAT_febe78d6 = 0;
  DAT_febe78d7 = 0;
  DAT_febe78d8 = 0x8000;
  DAT_febe78da = 0x8000;
  DAT_febe78dc = 0x8000;
  return;
}

int f33_sum_channel_snapshot_differences_b(void)

{
  ushort uVar1;
  char cVar4;
  char cVar5;
  ushort uVar2;
  ushort uVar3;
  
  uVar1 = DAT_febe823e;
  uVar2 = DAT_febe8242;
  uVar3 = DAT_febe8240;
  if (DAT_00031e66 != 'Z') goto LAB_000434b2;
  if (DAT_febeeac1 == 'Z') {
    cVar4 = DAT_febe7e24;
    cVar5 = DAT_febe7e25;
    if (DAT_febe7e23 == 'Z') goto LAB_00043478;
  }
  else {
    cVar4 = 'Z';
    cVar5 = 'Z';
LAB_00043478:
    DAT_febe78d8 = DAT_febe823e;
  }
  if (cVar4 == 'Z') {
    DAT_febe78da = DAT_febe8240;
  }
  uVar1 = DAT_febe78d8;
  uVar2 = DAT_febe78dc;
  uVar3 = DAT_febe78da;
  if (cVar5 == 'Z') {
    DAT_febe78dc = DAT_febe8242;
    uVar2 = DAT_febe8242;
  }
LAB_000434b2:
  return ((uint)uVar2 - (uint)DAT_febe8236) +
         ((uint)uVar3 - (uint)DAT_febe8234) + ((uint)uVar1 - (uint)DAT_febe8232);
}

void FUN_00043554(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe78e4 = 0;
  DAT_febe78e6 = 0;
  DAT_febe78e8 = 0;
  f33_reset_windowed_monitor((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe78ecu)));
  f33_reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3f04))));
  f33_reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3ef4))));
  f33_reset_recoverable_monitor(((F33RecoverableMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3ee4))));
  return;
}

void FUN_00043586(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe78e4 = 0;
  DAT_febe78e6 = 0;
  DAT_febe78e8 = 0;
  f33_reset_windowed_monitor((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe78ecu)));
  f33_reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3f04))));
  f33_reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3ef4))));
  f33_reset_recoverable_monitor(((F33RecoverableMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3ee4))));
  return;
}

uint f33_classify_channel_phase_failure_count_b(void)

{
  ushort uVar1;
  
  uVar1 = (ushort)DAT_0002b89e;
  if (((DAT_febe78f4 < uVar1) && (DAT_febe7904 < uVar1)) && (DAT_febe7914 < uVar1)) {
    return 0x11;
  }
  return 0x22;
}

void f33_set_channel_monitor_status_b(uint index,uchar status)

{
  if ((index & 0xff) < 0xe) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7928u + (uint32_t)(index & 0xff) * 1u)))) = status;
  }
  return;
}

void f33_reset_latched_monitor_febe793c(void)

{
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe793cu)));
  return;
}

void f33_reset_latched_monitor_febe793c_43a1c(void)

{
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe793cu)));
  return;
}

undefined4 FUN_00043a86(void)

{
  int iVar1;
  int iVar2;
  
  iVar1 = (uint)DAT_febe66b8 - (uint)DAT_febe66b0;
  if ((DAT_febe827a == 'Z') &&
     (((uint)DAT_0002b8ae < (uint)DAT_febe66b8 ||
      (iVar2 = (int)DAT_0002b8b0,
      iVar1 - iVar2 < 0 != (iVar1 < 0 != iVar2 < 0 && iVar2 < 0 == iVar1 - iVar2 < 0) ||
      iVar1 == iVar2)))) {
    return 0x5a;
  }
  return 0;
}

undefined4 FUN_00043ab6(void)

{
  char cVar1;
  uint uVar2;
  char cVar3;
  char cVar4;
  char cVar5;
  int iVar6;
  undefined4 uVar7;
  
  cVar5 = DAT_febe827f;
  cVar4 = DAT_febe827a;
  cVar3 = DAT_febe8279;
  uVar2 = DAT_febe6618;
  cVar1 = DAT_febe65f7;
  iVar6 = FUN_00043a86();
  if ((cVar1 == 'Z') && ((uVar2 >> 1 & 1) == 0)) {
    if ((cVar3 == 'Z') || ((iVar6 == 0x5a || (cVar5 == 'Z')))) {
      uVar7 = 0x22;
    }
    else if (((cVar3 == '\0') && (cVar4 == '\0')) && (cVar5 == '\0')) {
      uVar7 = 0x11;
    }
    else {
      uVar7 = 0x33;
    }
  }
  else {
    uVar7 = 0x44;
  }
  return uVar7;
}

void f33_reset_latched_monitor_febe7948(void)

{
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7948u)));
  return;
}

void f33_reset_latched_monitor_febe7948_43b46(void)

{
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7948u)));
  return;
}

uint f33_classify_channel_raw_lower_bound_b(void)

{
  if (f33_output_request_status >> 0x10 != 0) {
    return 0x44;
  }
  if ((((DAT_0002b8b2 <= DAT_febe623e) || (DAT_febe636f != 'Z')) &&
      ((DAT_0002b8b2 <= DAT_febe6240 || (DAT_febe6370 != 'Z')))) &&
     ((DAT_0002b8b2 <= DAT_febe6242 || (DAT_febe6371 != 'Z')))) {
    if ((DAT_0002b8b4 <= DAT_febe623e) &&
       ((((DAT_febe636f == 'Z' && (DAT_0002b8b4 <= DAT_febe6240)) && (DAT_febe6370 == 'Z')) &&
        ((DAT_0002b8b4 <= DAT_febe6242 && (DAT_febe6371 == 'Z')))))) {
      return 0x11;
    }
    return 0x33;
  }
  return 0x22;
}

void f33_reset_windowed_monitor_febe7954(void)

{
  f33_reset_windowed_monitor((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe7954u)));
  return;
}

void f33_reset_windowed_monitor_febe7954_43c5e(void)

{
  f33_reset_windowed_monitor((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe7954u)));
  return;
}

void f33_fill_constant_block_43dc6(void)

{
  DAT_febe7964 = 0;
  DAT_febe7965 = 0;
  DAT_febe7966 = 0;
  DAT_febe7967 = 0;
  DAT_febe7968 = 0;
  DAT_febe796c = 0;
  return;
}

undefined1 FUN_00043dd8(ushort param_1,undefined1 param_2)

{
  if (((DAT_0002fbce < DAT_febe7db0) && (DAT_0002fbca < param_1)) && (DAT_febe7bb9 != 'Z')) {
    return 0x5a;
  }
  if ((DAT_febe7db0 <= (ushort)PTR_DAT_0002fbd0) && (param_1 <= DAT_0002fbcc)) {
    param_2 = 0;
  }
  return param_2;
}

void FUN_00043e14(char param_1)

{
  uint32_t puVar1;
  undefined4 uVar2;
  
  puVar1 = 0xfebeb800u;
  uVar2 = DAT_febe7968;
  if (DAT_0002bc30 == '\0') {
    if ((DAT_0002fbc9 == 'Z') && (param_1 == 'Z')) {
      uVar2 = 0xc;
    }
    else {
      uVar2 = 2;
    }
  }
  FUN_00056cda(4,uVar2);
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x3e98)))) = uVar2;
  return;
}

void FUN_00043e7c(char param_1)

{
  uint32_t puVar1;
  undefined4 uVar2;
  
  puVar1 = 0xfebeb800u;
  uVar2 = DAT_febe796c;
  if (DAT_0002bc34 == '\0') {
    if ((DAT_0002fbc9 == 'Z') && (param_1 == 'Z')) {
      uVar2 = 0xc0000;
    }
    else {
      uVar2 = 0x20000;
    }
  }
  FUN_00056cda(5,uVar2);
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x3e94)))) = uVar2;
  return;
}

void FUN_00043ee8(void)

{
  if (((DAT_0002fbc8 != 'Z') || (DAT_febe7967 = DAT_febe7964, DAT_febe7964 != 'Z')) &&
     (DAT_febe7967 = '\0', DAT_0002fbc8 != 'Z')) {
    DAT_febe7966 = 0;
    DAT_febe7967 = 0;
    return;
  }
  if (DAT_febe7965 != 'Z') {
    DAT_febe7966 = 0;
    return;
  }
  DAT_febe7966 = DAT_febe7965;
  return;
}

void f33_reset_latched_monitor_febe7970(void)

{
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7970u)));
  return;
}

void f33_reset_latched_monitor_febe7970_43f48(void)

{
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7970u)));
  return;
}

uint f33_classify_inverse_gate_a(void)

{
  if ((DAT_0002b8ea < DAT_febe7da6) && (DAT_febe7db0 <= DAT_0002b8e8)) {
    return 0x22;
  }
  return 0x11;
}

void f33_reset_latched_monitor_febe797c(void)

{
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe797cu)));
  return;
}

void f33_reset_latched_monitor_febe797c_43ffa(void)

{
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe797cu)));
  return;
}

uint f33_classify_inverse_gate_b(void)

{
  if ((DAT_0002b8ee < DAT_febe7da8) && (DAT_febe7db0 <= DAT_0002b8ec)) {
    return 0x22;
  }
  return 0x11;
}

void f33_reset_latched_monitor_febe7988(void)

{
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7988u)));
  return;
}

void f33_reset_latched_monitor_febe7988_440ac(void)

{
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7988u)));
  return;
}

undefined4 FUN_00044116(void)

{
  if (((((DAT_febe7bba != '\0') || (DAT_febeeb86 != '\0')) || (DAT_febeeb80 != 'Z')) ||
      ((((DAT_febeeb88 != '\0' || (DAT_0002b8f0 <= DAT_febe7da6)) || (DAT_febe7db0 < DAT_0002b8f2))
       && (((DAT_febeeb88 != 'Z' || (DAT_0002b8f4 <= DAT_febe7da6)) || (DAT_febe7db0 < DAT_0002b8f2)
           ))))) &&
     ((DAT_0002b8f6 <= DAT_febe7da6 ||
      (((DAT_febe7bba != 'Z' && (DAT_febeeb86 != 'Z')) && (((int8_t)DAT_febeeb80) != -0x5b)))))) {
    return 0;
  }
  return 0x5a;
}

void f33_reset_latched_monitor_febe7994(void)

{
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7994u)));
  return;
}

void f33_reset_latched_monitor_febe7994_4425c(void)

{
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7994u)));
  return;
}

undefined4 FUN_000442c6(void)

{
  if (((((DAT_febe7bba != '\0') || (DAT_febeeb86 != '\0')) || (DAT_febeeb80 != 'Z')) ||
      ((((DAT_febeeb88 != '\0' || (DAT_0002b8fc <= DAT_febe7da8)) || (DAT_febe7db0 < DAT_0002b8fe))
       && (((DAT_febeeb88 != 'Z' || (DAT_0002b900 <= DAT_febe7da8)) || (DAT_febe7db0 < DAT_0002b8fe)
           ))))) &&
     ((DAT_0002b902 <= DAT_febe7da8 ||
      (((DAT_febe7bba != 'Z' && (DAT_febeeb86 != 'Z')) && (((int8_t)DAT_febeeb80) != -0x5b)))))) {
    return 0;
  }
  return 0x5a;
}

void f33_reset_latched_monitor_febe79a0(void)

{
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe79a0u)));
  return;
}

void f33_reset_latched_monitor_febe79a0_4440c(void)

{
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe79a0u)));
  return;
}

void f33_reset_latched_monitor_febe79ac(void)

{
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe79acu)));
  return;
}

void f33_reset_latched_monitor_febe79ac_445fc(void)

{
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe79acu)));
  return;
}

uint f33_classify_direct_source_a(void)

{
  if (f33_shared_condition_status[0] != '\0') {
    return 0x44;
  }
  if (DAT_febe8291 == 'Z') {
    return 0x22;
  }
  return 0x11;
}

void f33_reset_latched_monitor_febe79b8(void)

{
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe79b8u)));
  return;
}

void f33_reset_latched_monitor_febe79b8_446aa(void)

{
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe79b8u)));
  return;
}

uint f33_classify_direct_source_b(void)

{
  if (f33_shared_condition_status[0] != '\0') {
    return 0x44;
  }
  if (DAT_febe8292 == 'Z') {
    return 0x22;
  }
  return 0x11;
}

void f33_reset_latched_monitor_febe79c4(void)

{
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe79c4u)));
  return;
}

void f33_reset_latched_monitor_febe79c4_44758(void)

{
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe79c4u)));
  return;
}

uint f33_classify_paired_shared_gate_a(void)

{
  if ((DAT_0002b916 < DAT_febe7da6) &&
     ((DAT_febe7db0 <= DAT_0002b914 || ((DAT_febe7da8 <= DAT_0002b918 && (DAT_febe7966 != 'Z'))))))
  {
    return 0x22;
  }
  if ((DAT_febe7da6 <= DAT_0002b91c) &&
     ((DAT_febe7db0 <= DAT_0002b91a && (DAT_febe7da8 <= DAT_0002b91e)))) {
    return 0x11;
  }
  return 0x33;
}

void f33_reset_latched_monitor_febe79d0(void)

{
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe79d0u)));
  return;
}

void f33_reset_latched_monitor_febe79d0_44846(void)

{
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe79d0u)));
  return;
}

uint f33_classify_paired_shared_gate_b(void)

{
  if ((DAT_0002b922 < DAT_febe7da8) &&
     ((DAT_febe7db0 <= DAT_0002b920 || ((DAT_febe7da6 <= DAT_0002b924 && (DAT_febe7967 != 'Z'))))))
  {
    return 0x22;
  }
  if ((DAT_febe7da8 <= DAT_0002b928) &&
     ((DAT_febe7db0 <= DAT_0002b926 && (DAT_febe7da6 <= DAT_0002b92a)))) {
    return 0x11;
  }
  return 0x33;
}

void f33_publish_shared_condition_monitor_status(uint index,uint packed)

{
  if ((index & 0xff) < 9) {
    f33_shared_condition_status[index & 0xff] = (uchar)packed;
  }
  return;
}

void FUN_00044b20(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  f33_reset_windowed_monitor((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe7a00u)));
  f33_reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3df0))));
  f33_reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3de0))));
  f33_reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3dd0))));
  f33_reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3dc0))));
  f33_reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3db0))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x3da0)))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x3d9e)))) = 0;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x3d9c)))) = 0;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x3d98)))) = 0;
  return;
}

void FUN_00044c22(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  f33_reset_windowed_monitor((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe7a74u)));
  f33_reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3d7c))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x3d94)))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x3d92)))) = 0;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x3d90)))) = 0;
  return;
}

void FUN_00044cd0(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  f33_reset_windowed_monitor((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe7a9cu)));
  f33_reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3d54))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x3d6c)))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x3d6a)))) = 0;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x3d68)))) = 0;
  return;
}

void FUN_00044d7e(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  f33_reset_windowed_monitor((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe7ac4u)));
  f33_reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3d2c))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x3d44)))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x3d42)))) = 0;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x3d40)))) = 0;
  return;
}

void FUN_00044e2c(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe7ae4 = 0;
  DAT_febe7ae6 = 0;
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7ae8u)));
  f33_reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3d0c))));
  f33_reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3d00))));
  f33_reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3cf4))));
  f33_reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3ce8))));
  f33_reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3cdc))));
  return;
}

void FUN_00045086(void)

{
  int iVar1;
  uint32_t puVar2;
  int iVar3;
  int iVar4;
  undefined2 uStack_6;
  
  puVar2 = 0xfebeb800u;
  iVar3 = (int)DAT_febe63e8;
  uStack_6 = DAT_febe7b34;
  iVar1 = (int)DAT_febe629e;
  if (iVar1 + 0x7fff < 0 == (-1 < iVar1 && iVar1 + 0x7fff < 0) && iVar1 != -0x7fff) {
    if (iVar1 < 0) {
      iVar1 = (int)-DAT_febe629e;
    }
  }
  else {
    iVar1 = 0x7fff;
  }
  if (iVar3 + 0x7fff < 0 == (-1 < iVar3 && iVar3 + 0x7fff < 0) && iVar3 != -0x7fff) {
    if (iVar3 < 0) {
      iVar3 = (int)-DAT_febe63e8;
    }
  }
  else {
    iVar3 = 0x7fff;
  }
  iVar4 = (int)DAT_0002b99c;
  if ((iVar3 - iVar4 < 0 == (iVar3 < 0 != iVar4 < 0 && iVar4 < 0 == iVar3 - iVar4 < 0) &&
       iVar3 != iVar4) &&
     (iVar3 = (int)DAT_0002b99e,
     iVar1 - iVar3 < 0 != (iVar1 < 0 != iVar3 < 0 && iVar3 < 0 == iVar1 - iVar3 < 0) ||
     iVar1 == iVar3)) {
    puVar2 = 0xfebeb800u;
    FUN_00044ece(DAT_febe63b8,&uStack_6);
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x3ccc)))) = uStack_6;
  return;
}

void FUN_000450f0(void)

{
  int iVar1;
  uint32_t puVar2;
  int iVar3;
  int iVar4;
  undefined2 uStack_6;
  
  puVar2 = 0xfebeb800u;
  iVar3 = (int)DAT_febe63ec;
  uStack_6 = DAT_febe7b36;
  iVar1 = (int)DAT_febe629e;
  if (iVar1 + 0x7fff < 0 == (-1 < iVar1 && iVar1 + 0x7fff < 0) && iVar1 != -0x7fff) {
    if (iVar1 < 0) {
      iVar1 = (int)-DAT_febe629e;
    }
  }
  else {
    iVar1 = 0x7fff;
  }
  if (iVar3 + 0x7fff < 0 == (-1 < iVar3 && iVar3 + 0x7fff < 0) && iVar3 != -0x7fff) {
    if (iVar3 < 0) {
      iVar3 = (int)-DAT_febe63ec;
    }
  }
  else {
    iVar3 = 0x7fff;
  }
  iVar4 = (int)DAT_0002b99c;
  if ((iVar3 - iVar4 < 0 == (iVar3 < 0 != iVar4 < 0 && iVar4 < 0 == iVar3 - iVar4 < 0) &&
       iVar3 != iVar4) &&
     (iVar3 = (int)DAT_0002b99e,
     iVar1 - iVar3 < 0 != (iVar1 < 0 != iVar3 < 0 && iVar3 < 0 == iVar1 - iVar3 < 0) ||
     iVar1 == iVar3)) {
    puVar2 = 0xfebeb800u;
    FUN_00044ece(DAT_febe63b8,&uStack_6);
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x3cca)))) = uStack_6;
  return;
}

void FUN_0004515a(void)

{
  short sVar1;
  
  sVar1 = DAT_febe7b36;
  if (((int16_t)DAT_febe7b34) != -1) {
    FUN_00045086();
  }
  if (sVar1 != -1) {
    FUN_000450f0();
  }
  return;
}

void FUN_0004517e(void)

{
  int iVar1;
  uint32_t puVar2;
  int iVar3;
  short sStack_6;
  
  puVar2 = 0xfebeb800u;
  sStack_6 = DAT_febe7b44;
  if (((int16_t)DAT_febe7b44) != -1) {
    iVar1 = (int)DAT_0002b9a2;
    iVar3 = (int)(short)(DAT_febe6354 - DAT_febe6356);
    if ((iVar3 - iVar1 < 0 != (iVar3 < 0 != iVar1 < 0 && iVar1 < 0 == iVar3 - iVar1 < 0) ||
         iVar3 == iVar1) &&
       (iVar3 + iVar1 < 0 == (iVar3 < 0 != -iVar1 < 0 && -iVar1 < 0 == iVar3 + iVar1 < 0))) {
      iVar3 = (int)DAT_febe629e;
      iVar1 = (int)DAT_0002b9a4;
      if ((iVar3 - iVar1 < 0 != (iVar3 < 0 != iVar1 < 0 && iVar1 < 0 == iVar3 - iVar1 < 0) ||
           iVar3 == iVar1) &&
         (iVar3 + iVar1 < 0 == (iVar3 < 0 != -iVar1 < 0 && -iVar1 < 0 == iVar3 + iVar1 < 0))) {
        puVar2 = 0xfebeb800u;
        FUN_00044ece(DAT_febe6284,&sStack_6);
      }
    }
    (*((short *)camry_host_ptr((uint32_t)(puVar2 + -0x3cbc)))) = sStack_6;
  }
  return;
}

void FUN_000451d6(void)

{
  int iVar1;
  uint32_t puVar2;
  int iVar3;
  short sStack_6;
  
  puVar2 = 0xfebeb800u;
  sStack_6 = DAT_febe7b46;
  if (((int16_t)DAT_febe7b46) != -1) {
    iVar1 = (int)DAT_0002b9a2;
    iVar3 = (int)(short)(DAT_febe6358 - DAT_febe635a);
    if ((iVar3 - iVar1 < 0 != (iVar3 < 0 != iVar1 < 0 && iVar1 < 0 == iVar3 - iVar1 < 0) ||
         iVar3 == iVar1) &&
       (iVar3 + iVar1 < 0 == (iVar3 < 0 != -iVar1 < 0 && -iVar1 < 0 == iVar3 + iVar1 < 0))) {
      iVar3 = (int)DAT_febe629e;
      iVar1 = (int)DAT_0002b9a4;
      if ((iVar3 - iVar1 < 0 != (iVar3 < 0 != iVar1 < 0 && iVar1 < 0 == iVar3 - iVar1 < 0) ||
           iVar3 == iVar1) &&
         (iVar3 + iVar1 < 0 == (iVar3 < 0 != -iVar1 < 0 && -iVar1 < 0 == iVar3 + iVar1 < 0))) {
        puVar2 = 0xfebeb800u;
        FUN_00044ece(DAT_febe6284,&sStack_6);
      }
    }
    (*((short *)camry_host_ptr((uint32_t)(puVar2 + -0x3cba)))) = sStack_6;
  }
  return;
}

void FUN_0004522e(void)

{
  FUN_0004517e();
  FUN_000451d6();
  return;
}

void f33_publish_local_channel_a_monitor_status(uchar index,uint packed_status)

{
  if (index < 2) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7b4cu + (uint32_t)(index) * 1u)))) = (char)packed_status;
  }
  return;
}

void f33_reset_scalar_monitor_45356(void)

{
  f33_reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebe7b50u)))));
  return;
}

void f33_reset_scalar_monitor_45356_45346(void)

{
  f33_reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebe7b50u)))));
  return;
}

uint f33_classify_local_output_status_a(void)

{
  if (((DAT_febe6624 & 1) != 0) && (DAT_febe65f6 == 'Z')) {
    if (DAT_febe8284 == 'Z') {
      return 0x22;
    }
    return 0x11;
  }
  return 0x44;
}

void f33_reset_scalar_monitor_45410(void)

{
  f33_reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebe7b5cu)))));
  return;
}

void f33_reset_scalar_monitor_45410_45400(void)

{
  f33_reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebe7b5cu)))));
  return;
}

uint f33_classify_local_channel_mismatch_a(void)

{
  if (((((byte)DAT_febe64dc & 2) == 0) && (((byte)DAT_febe64d4 & 2) == 0)) && (DAT_febe65f6 == 'Z'))
  {
    if (DAT_febe8282 == 'Z') {
      return 0x22;
    }
    return 0x11;
  }
  return 0x44;
}

void f33_publish_local_channel_b_monitor_status(uchar index,uint packed_status)

{
  if (index < 2) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7b68u + (uint32_t)(index) * 1u)))) = (char)packed_status;
  }
  return;
}

void f33_reset_scalar_monitor_45572(void)

{
  f33_reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebe7b6cu)))));
  return;
}

void f33_reset_scalar_monitor_45572_45562(void)

{
  f33_reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebe7b6cu)))));
  return;
}

uint f33_classify_local_output_status_b(void)

{
  if ((((byte)DAT_febe6624 & 2) != 0) && (DAT_febe65f7 == 'Z')) {
    if (DAT_febe8283 == 'Z') {
      return 0x22;
    }
    return 0x11;
  }
  return 0x44;
}

void f33_reset_scalar_monitor_4562a(void)

{
  f33_reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebe7b78u)))));
  return;
}

void f33_reset_scalar_monitor_4562a_4561a(void)

{
  f33_reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebe7b78u)))));
  return;
}

uint f33_classify_local_channel_mismatch_b(void)

{
  if (((((*((volatile uint8_t *)camry_host_ptr(0xfebe64deu))) & 2) == 0) && (((*((volatile uint8_t *)camry_host_ptr(0xfebe64d6u))) & 2) == 0)) && (DAT_febe65f7 == 'Z'))
  {
    if (DAT_febe8281 == 'Z') {
      return 0x22;
    }
    return 0x11;
  }
  return 0x44;
}

void f33_reset_scalar_monitor_456fa(void)

{
  f33_reset_recoverable_monitor(((F33RecoverableMonitorState *)camry_host_ptr((uint32_t)((0xfebe7b84u)))));
  return;
}

void f33_reset_scalar_monitor_456fa_456ea(void)

{
  f33_reset_recoverable_monitor(((F33RecoverableMonitorState *)camry_host_ptr((uint32_t)((0xfebe7b84u)))));
  return;
}

uint f33_classify_admitted_scalar_receive_condition(void)

{
  if ((DAT_febee822 == 'Z') && (DAT_febee823 == '\0')) {
    if (DAT_0002b9d8 <= DAT_febe6868) {
      if ((DAT_febe803c == '\x01') && (DAT_febe803e == '\0')) {
        return 0x22;
      }
      if ((DAT_febe66b8 < DAT_0002b9de) && (DAT_0002b9e0 < DAT_febe66b8)) {
        return 0x11;
      }
      return 0x33;
    }
    DAT_febe6868 = DAT_febe6868 + 1;
  }
  else {
    DAT_febe6868 = 0;
  }
  if ((DAT_febe66b8 < DAT_0002b9de) && (DAT_0002b9e0 < DAT_febe66b8)) {
    return 0x11;
  }
  return 0x44;
}

uint f33_classify_scalar_receive_recovery(void)

{
  if ((DAT_febe66b8 < DAT_0002b9da) && (DAT_0002b9dc < DAT_febe66b8)) {
    return 0x11;
  }
  return 0x22;
}

void f33_reset_scalar_monitor_45838(void)

{
  f33_reset_recoverable_monitor(((F33RecoverableMonitorState *)camry_host_ptr((uint32_t)((0xfebe7b90u)))));
  return;
}

void f33_reset_scalar_monitor_45838_45828(void)

{
  f33_reset_recoverable_monitor(((F33RecoverableMonitorState *)camry_host_ptr((uint32_t)((0xfebe7b90u)))));
  return;
}

uint f33_classify_paired_scalar_relation(void)

{
  if (DAT_febe6752 != '\0' ||
      (DAT_febe6751 != '\0' ||
      (DAT_febe65c4 != '\0' ||
      (DAT_febe65c3 != '\0' || (DAT_febe65c2 != '\0' || DAT_febe65c5 != '\0'))))) {
    return 0x44;
  }
  if ((DAT_0002b9e4 < DAT_febe66b8) &&
     ((DAT_febe66ae <= DAT_0002b9e8 || (DAT_febe66b0 <= DAT_0002b9ea)))) {
    return 0x22;
  }
  if ((DAT_febe66b8 <= DAT_0002b9ee) &&
     ((DAT_febe66ae <= DAT_0002b9f0 || (DAT_febe66b0 <= DAT_0002b9f2)))) {
    return 0x11;
  }
  return 0x33;
}

uint f33_classify_paired_scalar_recovery(void)

{
  if (DAT_febe6752 != '\0' ||
      (DAT_febe6751 != '\0' ||
      (DAT_febe65c4 != '\0' ||
      (DAT_febe65c3 != '\0' || (DAT_febe65c2 != '\0' || DAT_febe65c5 != '\0'))))) {
    return 0x44;
  }
  if ((DAT_febe66b8 <= DAT_0002b9e6) && (DAT_0002b9ec <= DAT_febe66b8)) {
    return 0x11;
  }
  return 0x22;
}

void f33_reset_scalar_monitor_4599c(void)

{
  f33_reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebe7b9cu)))));
  return;
}

void f33_reset_scalar_monitor_4599c_4598c(void)

{
  f33_reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebe7b9cu)))));
  return;
}

uint f33_classify_qualified_scalar_relation_a(void)

{
  if (DAT_febe6751 != '\0' ||
      (DAT_febe65c4 != '\0' || (DAT_febe65c2 != '\0' || DAT_febe65c5 != '\0'))) {
    return 0x44;
  }
  if ((DAT_0002b9f4 < DAT_febe66b8) && (DAT_febe66ae <= DAT_0002b9f6)) {
    return 0x22;
  }
  return 0x11;
}

void f33_reset_scalar_monitor_45a6c(void)

{
  f33_reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebe7ba8u)))));
  return;
}

void f33_reset_scalar_monitor_45a6c_45a5c(void)

{
  f33_reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebe7ba8u)))));
  return;
}

uint f33_classify_qualified_scalar_relation_b(void)

{
  if (DAT_febe6752 != '\0' ||
      (DAT_febe65c4 != '\0' || (DAT_febe65c3 != '\0' || DAT_febe65c5 != '\0'))) {
    return 0x44;
  }
  if ((DAT_0002b9f8 < DAT_febe66b8) && (DAT_febe66b0 <= DAT_0002b9fa)) {
    return 0x22;
  }
  return 0x11;
}

void f33_publish_scalar_relation_monitor_status(uchar index,uint packed_status)

{
  if (index < 4) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7bb4u + (uint32_t)(index) * 1u)))) = (char)packed_status;
  }
  return;
}

void f33_fill_constant_block_45bb2(void)

{
  DAT_febe7bbc = 0;
  DAT_febe7bbd = 0;
  DAT_febe7bbe = 0;
  DAT_febe7bbf = 0;
  DAT_febe7bc0 = 0;
  DAT_febe7bc1 = 0;
  DAT_febe7bc2 = 0;
  DAT_febe7bc3 = 0;
  return;
}

void f33_publish_primary_scalar_availability(void)

{
  if (DAT_febe7db0 < DAT_0002b9fe) {
    DAT_febe7bbd = 0;
    DAT_febe7bbc = 0;
  }
  else {
    DAT_febe7bbd = 0x5a;
    DAT_febe7bbc = 0x5a;
    if (DAT_0002b9fc < DAT_febe7db0) {
      DAT_febe7bbd = 0;
    }
  }
  return;
}

void f33_publish_channel_scalar_availability_a(void)

{
  if (DAT_febe7da6 < DAT_0002ba08) {
    DAT_febe7bbe = 0;
    DAT_febe7bc0 = 0;
  }
  else {
    DAT_febe7bbe = 0x5a;
    DAT_febe7bc0 = 0x5a;
    if (DAT_febe7da6 < DAT_0002ba04) {
      DAT_febe7bbe = 0;
    }
  }
  return;
}

void f33_publish_channel_scalar_availability_b(void)

{
  if (DAT_febe7da8 < DAT_0002ba08) {
    DAT_febe7bbf = 0;
    DAT_febe7bc1 = 0;
  }
  else {
    DAT_febe7bbf = 0x5a;
    DAT_febe7bc1 = 0x5a;
    if (DAT_febe7da8 < DAT_0002ba04) {
      DAT_febe7bbf = 0;
    }
  }
  return;
}

void f33_publish_paired_scalar_availability(void)

{
  ushort uVar1;
  ushort uVar2;
  
  uVar1 = DAT_0002ba04;
  uVar2 = DAT_0002b9fe;
  if (DAT_febeeb85 == 'Z') {
    uVar1 = DAT_0002ba06;
    uVar2 = DAT_0002ba00;
  }
  if (((DAT_febe7db0 < uVar2) || (DAT_0002b9fc < DAT_febe7db0)) &&
     ((DAT_febe7da6 < uVar1 || (DAT_0002ba02 < DAT_febe7da6)))) {
    DAT_febe7bc2 = 0;
  }
  else {
    DAT_febe7bc2 = 0x5a;
  }
  if (((DAT_febe7db0 < uVar2) || (DAT_0002b9fc < DAT_febe7db0)) &&
     ((DAT_febe7da8 < uVar1 || (DAT_0002ba02 < DAT_febe7da8)))) {
    DAT_febe7bc3 = 0;
  }
  else {
    DAT_febe7bc3 = 0x5a;
  }
  return;
}

void f33_update_scalar_availability(void)

{
  f33_publish_primary_scalar_availability();
  f33_publish_channel_scalar_availability_a();
  f33_publish_channel_scalar_availability_b();
  f33_publish_paired_scalar_availability();
  return;
}

void f33_clear_reserved_monitor_action_slot(void)

{
  f33_retain_and_clear_fault_record(0x15);
  f33_select_current_fault_record(0x15);
  f33_set_diagnostic_cache_blocker('\n','\0');
  return;
}

void f33_reset_scalar_monitor_45e74(void)

{
  f33_reset_recoverable_monitor(((F33RecoverableMonitorState *)camry_host_ptr((uint32_t)((0xfebe7bdcu)))));
  return;
}

void f33_reset_scalar_monitor_45e74_45e64(void)

{
  f33_reset_recoverable_monitor(((F33RecoverableMonitorState *)camry_host_ptr((uint32_t)((0xfebe7bdcu)))));
  return;
}

uint f33_classify_raw_thermistor_range_a(void)

{
  if ((DAT_0002ba1a <= DAT_febe6492) && (DAT_febe6492 <= DAT_0002ba18)) {
    return 0x11;
  }
  return 0x22;
}

void f33_reset_scalar_monitor_45f32(void)

{
  f33_reset_recoverable_monitor(((F33RecoverableMonitorState *)camry_host_ptr((uint32_t)((0xfebe7be8u)))));
  return;
}

void f33_reset_scalar_monitor_45f32_45f22(void)

{
  f33_reset_recoverable_monitor(((F33RecoverableMonitorState *)camry_host_ptr((uint32_t)((0xfebe7be8u)))));
  return;
}

uint f33_classify_raw_thermistor_range_b(void)

{
  if ((DAT_0002ba1e <= DAT_febe6498) && (DAT_febe6498 <= DAT_0002ba1c)) {
    return 0x11;
  }
  return 0x22;
}

void f33_publish_thermistor_range_monitor_status(uchar index,uint packed_status)

{
  if (index < 2) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7bf4u + (uint32_t)(index) * 1u)))) = (char)packed_status;
  }
  return;
}

void FUN_00046070(void)

{
  FUN_0006b98a(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe7c00u)))));
  return;
}

void FUN_00046080(void)

{
  FUN_0006b98a(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe7c00u)))));
  return;
}

void f33_request_shared_monitor_escalation_status_a(void)

{
  byte bVar1;
  
  bVar1 = f33_shared_snapshot_status[3] | f33_shared_snapshot_status[1] |
          f33_shared_snapshot_status[9];
  if ((((bVar1 & 0x22) == 0x22) || ((bVar1 & 0x44) == 0x44)) || (DAT_febe71ec != 0)) {
    DAT_febe7c10 = 0x5a;
  }
  return;
}

void FUN_00046346(void)

{
  FUN_0006b98a(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe7c1cu)))));
  return;
}

void FUN_00046356(void)

{
  FUN_0006b98a(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe7c1cu)))));
  return;
}

void f33_request_shared_monitor_escalation_status_b(void)

{
  byte bVar1;
  
  bVar1 = f33_shared_snapshot_status[2] | f33_shared_snapshot_status[0] |
          f33_shared_snapshot_status[8];
  if ((((bVar1 & 0x22) == 0x22) || ((bVar1 & 0x44) == 0x44)) || (DAT_febe71ec != 0)) {
    DAT_febe7c2c = 0x5a;
  }
  return;
}

void FUN_0004661e(void)

{
  DAT_febe7c4e = (byte)DAT_febe81ee & 3;
  if (DAT_febe8a1c == 'Z') {
    DAT_febe7c4e = DAT_febe7c4e - 1 & 3;
  }
  return;
}

void FUN_000467d0(void)

{
  DAT_febe7c66 = (byte)DAT_febe81f0 & 3;
  if (DAT_febe8a1c == 'Z') {
    DAT_febe7c66 = DAT_febe7c66 - 1 & 3;
  }
  return;
}

void FUN_00046982(void)

{
  DAT_febe686c = 0;
  DAT_febe6870 = 0;
  DAT_febe6874 = 0;
  DAT_febe6872 = 0;
  return;
}

void FUN_00046a2c(undefined1 param_1)

{
  DAT_febe686d = param_1;
  return;
}

void f33_reset_recoverable_monitor_febe7c68(void)

{
  f33_reset_recoverable_monitor((F33RecoverableMonitorState *)((undefined *)camry_host_ptr(0xfebe7c68u)));
  return;
}

void f33_reset_recoverable_monitor_febe7c68_46a42(void)

{
  f33_reset_recoverable_monitor((F33RecoverableMonitorState *)((undefined *)camry_host_ptr(0xfebe7c68u)));
  return;
}

uint f33_classify_selected_source_hold(void)

{
  if ((DAT_febe686c == 'Z') && (DAT_febe7cb8 == 'Z')) {
    return 0x22;
  }
  return 0x11;
}

uint f33_classify_selected_source_hold_recovery(void)

{
  if (DAT_febe686c == 'Z') {
    return 0x22;
  }
  return 0x11;
}

void FUN_00046afe(void)

{
  FUN_0006b98a(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe7c74u)))));
  return;
}

void FUN_00046b0e(void)

{
  FUN_0006b98a(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe7c74u)))));
  return;
}

void f33_request_shared_monitor_escalation_sample_bounds_a(void)

{
  byte bVar1;
  
  bVar1 = f33_shared_snapshot_status[3] | f33_shared_snapshot_status[1] |
          f33_shared_snapshot_status[9];
  if ((((bVar1 & 0x22) == 0x22) || ((bVar1 & 0x44) == 0x44)) || (DAT_febe71ec != 0)) {
    DAT_febe7c84 = 0x5a;
  }
  return;
}

void FUN_00046e08(void)

{
  FUN_0006b98a(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe7c90u)))));
  return;
}

void FUN_00046e18(void)

{
  FUN_0006b98a(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe7c90u)))));
  return;
}

void f33_request_shared_monitor_escalation_sample_bounds_b(void)

{
  byte bVar1;
  
  bVar1 = f33_shared_snapshot_status[2] | f33_shared_snapshot_status[0] |
          f33_shared_snapshot_status[8];
  if ((((bVar1 & 0x22) == 0x22) || ((bVar1 & 0x44) == 0x44)) || (DAT_febe71ec != 0)) {
    DAT_febe7ca0 = 0x5a;
  }
  return;
}

void f33_publish_shared_snapshot_monitor_status(uint index,uint packed)

{
  uint uVar1;
  
  uVar1 = index & 0xff;
  if (uVar1 < 0xb) {
    f33_shared_snapshot_status[uVar1] = (uchar)packed;
    f33_shared_snapshot_transition[uVar1] = (uchar)(packed >> 0x10);
  }
  return;
}

void FUN_000473ec(void)

{
  FUN_0006b98a(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe7cc8u)))));
  return;
}

void FUN_000473fc(void)

{
  FUN_0006b98a(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe7cc8u)))));
  return;
}

uint f33_classify_snapshot_bit3_a(void)

{
  uint uVar1;
  
  if ((DAT_febe6321 == DAT_febe7cd8) || (DAT_febe7db2 < DAT_0002bade)) {
    uVar1 = 0x11;
  }
  else {
    uVar1 = 0x22;
  }
  DAT_febe7cd8 = DAT_febe6321;
  return uVar1;
}

uint f33_classify_snapshot_bit3_recovery_a(void)

{
  return 0x44;
}

void FUN_000474b4(void)

{
  FUN_0006b98a(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe7cdcu)))));
  return;
}

void FUN_000474c4(void)

{
  FUN_0006b98a(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe7cdcu)))));
  return;
}

uint f33_classify_snapshot_bit3_b(void)

{
  uint uVar1;
  
  if ((DAT_febe6339 == DAT_febe7cec) || (DAT_febe7db2 < DAT_0002bae2)) {
    uVar1 = 0x11;
  }
  else {
    uVar1 = 0x22;
  }
  DAT_febe7cec = DAT_febe6339;
  return uVar1;
}

uint f33_classify_snapshot_bit3_recovery_b(void)

{
  return 0x44;
}

void FUN_0004757c(void)

{
  FUN_0006b98a(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe7cf0u)))));
  return;
}

void FUN_0004758c(void)

{
  FUN_0006b98a(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe7cf0u)))));
  return;
}

uint f33_classify_snapshot_low_gate_a(void)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  
  iVar1 = 0;
  iVar5 = 0;
  iVar4 = 0;
  iVar3 = 0;
  if (DAT_febe631c != DAT_febe7d00) {
    iVar1 = 0x5a;
  }
  if (DAT_febe631d != DAT_febe7d01) {
    iVar5 = 0x5a;
  }
  if (DAT_febe631e != DAT_febe7d02) {
    iVar4 = 0x5a;
  }
  if (DAT_febe631f != DAT_febe7d03) {
    iVar3 = 0x5a;
  }
  if (((((iVar1 == 0x5a) || (iVar5 == 0x5a)) || (iVar4 == 0x5a)) || (iVar3 == 0x5a)) &&
     (DAT_febe7db2 < DAT_0002bae6)) {
    uVar2 = 0x22;
  }
  else {
    uVar2 = 0x11;
  }
  DAT_febe7d00 = DAT_febe631c;
  DAT_febe7d01 = DAT_febe631d;
  DAT_febe7d02 = DAT_febe631e;
  DAT_febe7d03 = DAT_febe631f;
  return uVar2;
}

void FUN_00047682(void)

{
  FUN_0006b98a(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe7d04u)))));
  return;
}

void FUN_00047692(void)

{
  FUN_0006b98a(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe7d04u)))));
  return;
}

uint f33_classify_snapshot_low_gate_b(void)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  
  iVar1 = 0;
  iVar5 = 0;
  iVar4 = 0;
  iVar3 = 0;
  if (DAT_febe6334 != DAT_febe7d14) {
    iVar1 = 0x5a;
  }
  if (DAT_febe6335 != DAT_febe7d15) {
    iVar5 = 0x5a;
  }
  if (DAT_febe6336 != DAT_febe7d16) {
    iVar4 = 0x5a;
  }
  if (DAT_febe6337 != DAT_febe7d17) {
    iVar3 = 0x5a;
  }
  if (((((iVar1 == 0x5a) || (iVar5 == 0x5a)) || (iVar4 == 0x5a)) || (iVar3 == 0x5a)) &&
     (DAT_febe7db2 < DAT_0002baea)) {
    uVar2 = 0x22;
  }
  else {
    uVar2 = 0x11;
  }
  DAT_febe7d14 = DAT_febe6334;
  DAT_febe7d15 = DAT_febe6335;
  DAT_febe7d16 = DAT_febe6336;
  DAT_febe7d17 = DAT_febe6337;
  return uVar2;
}

void FUN_00047788(void)

{
  FUN_0006b98a(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe7d18u)))));
  return;
}

void FUN_00047798(void)

{
  FUN_0006b98a(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe7d18u)))));
  return;
}

uint f33_classify_snapshot_bit2_a(void)

{
  uint uVar1;
  
  if (DAT_febe6320 == DAT_febe7d29) {
    if ((DAT_febe7b48 == 'Z') && (DAT_febe7b49 == 'Z')) {
      uVar1 = 0x11;
    }
    else {
      uVar1 = 0x33;
    }
  }
  else {
    uVar1 = 0x22;
  }
  DAT_febe7d29 = DAT_febe6320;
  return uVar1;
}

uint f33_classify_snapshot_bit2_recovery_a(void)

{
  uint uVar1;
  
  uVar1 = 0x11;
  if (DAT_febe6320 != DAT_febe7d29) {
    uVar1 = 0x22;
  }
  DAT_febe7d29 = DAT_febe6320;
  return uVar1;
}

void f33_request_shared_monitor_escalation_bit2_a(void)

{
  byte bVar1;
  
  bVar1 = f33_shared_snapshot_status[3] | f33_shared_snapshot_status[1] |
          f33_shared_snapshot_status[9];
  if ((((bVar1 & 0x22) == 0x22) || ((bVar1 & 0x44) == 0x44)) || (DAT_febe71ec != 0)) {
    DAT_febe7d28 = 0x5a;
  }
  return;
}

void FUN_00047924(void)

{
  FUN_0006b98a(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe7d2cu)))));
  return;
}

void FUN_00047934(void)

{
  FUN_0006b98a(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe7d2cu)))));
  return;
}

uint f33_classify_snapshot_bit2_b(void)

{
  uint uVar1;
  
  if (DAT_febe6338 == DAT_febe7d3d) {
    if ((DAT_febe7b48 == 'Z') && (DAT_febe7b49 == 'Z')) {
      uVar1 = 0x11;
    }
    else {
      uVar1 = 0x33;
    }
  }
  else {
    uVar1 = 0x22;
  }
  DAT_febe7d3d = DAT_febe6338;
  return uVar1;
}

uint f33_classify_snapshot_bit2_recovery_b(void)

{
  uint uVar1;
  
  uVar1 = 0x11;
  if (DAT_febe6338 != DAT_febe7d3d) {
    uVar1 = 0x22;
  }
  DAT_febe7d3d = DAT_febe6338;
  return uVar1;
}

void f33_request_shared_monitor_escalation_bit2_b(void)

{
  byte bVar1;
  
  bVar1 = f33_shared_snapshot_status[2] | f33_shared_snapshot_status[0] |
          f33_shared_snapshot_status[8];
  if ((((bVar1 & 0x22) == 0x22) || ((bVar1 & 0x44) == 0x44)) || (DAT_febe71ec != 0)) {
    DAT_febe7d3c = 0x5a;
  }
  return;
}

void FUN_00047ac4(void)

{
  DAT_febe7d40 = 0;
  if (DAT_febe8026 < 0x10) {
    DAT_febe7d40 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x212b8u + (uint32_t)(DAT_febe8026) * 1u))));
  }
  return;
}

void f33_fill_constant_block_47b3c(void)

{
  DAT_febe7d48 = 0;
  DAT_febe7d49 = 0;
  DAT_febe7d4a = 0;
  DAT_febe7d4c = 0;
  DAT_febe7d4e = 0;
  DAT_febe7d50 = 0;
  DAT_febe7d52 = 0;
  DAT_febe7d54 = 0;
  DAT_febe7d56 = 0;
  DAT_febe7d58 = 0;
  DAT_febe7d5a = 0;
  DAT_febe7d5c = 0;
  DAT_febe7d5e = 0;
  DAT_febe7d60 = 0;
  DAT_febe7d62 = 0;
  DAT_febe7d64 = 0;
  DAT_febe7d66 = 0;
  DAT_febe7d68 = 0;
  DAT_febe7d6c = 0;
  DAT_febe7d70 = 0;
  return;
}

void FUN_00047d34(void)

{
  DAT_febe7d74 = 0;
  return;
}

ushort f33_select_electrical_angle_sample(uchar channel)

{
  DAT_febe7d90 = DAT_febe824c;
  if (channel == '\x01') {
    DAT_febe7d90 = DAT_febe8250;
  }
  return DAT_febe7d90;
}

short f33_correct_electrical_angle_sample(uchar enabled,uchar bank,short phase)

{
  char cVar1;
  short sVar2;
  int iVar3;
  
  if (enabled == 'Z') {
    iVar3 = camry_host_addr(FUN_000567be());
    iVar3 = (uint)bank * 0x100 + iVar3 + 0xc0;
    cVar1 = (*((char *)camry_host_ptr((uint32_t)((uint)((ushort)phase >> 8) + iVar3))));
    sVar2 = (short)((int)(((int)(*((char *)camry_host_ptr((uint32_t)((((ushort)phase >> 8) + 1 & 0xff) + iVar3)))) - (int)cVar1) *
                         ((int)phase & 0xffU)) / 0x100) + (short)cVar1;
  }
  else {
    sVar2 = 0;
  }
  return phase - sVar2;
}

int f33_accumulate_electrical_angle(int previous,short phase)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar2 = (int)phase - (int)(short)previous;
  if (iVar2 + -0x8000 < 0 == (iVar2 < 0 && -1 < iVar2 + -0x8000)) {
    iVar2 = iVar2 + -0x10000;
  }
  else if (iVar2 + 0x8000 < 0 != (-1 < iVar2 && iVar2 + 0x8000 < 0)) {
    iVar2 = iVar2 + 0x10000;
  }
  iVar1 = 0x3330000 - iVar2;
  iVar3 = previous + -0x6660000;
  if ((iVar1 - previous < 0 == (iVar1 < 0 != previous < 0 && previous < 0 == iVar1 - previous < 0)
       && iVar1 != previous) &&
     (iVar1 = -0x3330000 - iVar2, iVar3 = previous,
     iVar1 - previous < 0 == (iVar1 < 0 != previous < 0 && previous < 0 == iVar1 - previous < 0) &&
     iVar1 != previous)) {
    iVar3 = previous + 0x6660000;
  }
  return (uint)(ushort)phase | iVar2 + iVar3 & 0xffff0000U;
}

void f33_fill_constant_block_47ea4(void)

{
  DAT_febe5f34 = 0;
  DAT_febe5f36 = 0;
  DAT_febe5f40 = 0;
  DAT_febe5f38 = DAT_febe7d74;
  DAT_febe5f3c = 0;
  return;
}

void FUN_0004819a(void)

{
  DAT_febe7db4 = (short)((uint)DAT_febe8226 * (uint)DAT_0002fbea >> 0x10);
  DAT_febe7db6 = (short)((uint)DAT_febe8228 * (uint)DAT_0002fbea >> 0x10);
  return;
}

void FUN_000481c0(void)

{
  if ((DAT_febe71ec & 1) == 0) {
    if ((DAT_febe71ec & 2) != 0) {
      DAT_febe7dae = DAT_febe7da6;
      return;
    }
  }
  else if ((DAT_febe71ec & 2) == 0) {
    DAT_febe7dae = DAT_febe7da8;
    return;
  }
  if (DAT_febe7da8 < DAT_febe7da6) {
    if (DAT_febe7da6 <= DAT_0002fbde) {
      DAT_febe7dae = DAT_febe7da6;
      return;
    }
  }
  else if (DAT_0002fbde < DAT_febe7da8) {
    DAT_febe7dae = DAT_febe7da6;
    return;
  }
  DAT_febe7dae = DAT_febe7da8;
  return;
}

void FUN_00048200(void)

{
  if (DAT_febe7dae < DAT_febe7db0) {
    if (DAT_febe7db0 <= DAT_0002fbe0) {
      DAT_febe7da4 = 0x5a;
      DAT_febe7db2 = DAT_febe7db0;
      return;
    }
  }
  else if (DAT_0002fbde < DAT_febe7dae) {
    DAT_febe7da4 = 0x5a;
    DAT_febe7db2 = DAT_febe7db0;
    return;
  }
  DAT_febe7db2 = DAT_febe7dae;
  DAT_febe7da4 = 0x5a;
  return;
}

void FUN_000483b6(void)

{
  DAT_febe7de4 = 0;
  return;
}

void f33_fill_constant_block_4843c(void)

{
  DAT_febe7dea = 0;
  DAT_febe7dfc = 0;
  DAT_febe7e00 = 0;
  DAT_febe7e04 = 0;
  DAT_febe7e08 = 0;
  DAT_febe7dec = 0;
  DAT_febe7dee = 0;
  DAT_febe7df0 = 0;
  DAT_febe7df2 = 0;
  DAT_febe7df4 = 0;
  DAT_febe7df6 = 0;
  DAT_febe7df8 = 0;
  DAT_febe7dfa = 0;
  DAT_febe7de8 = 0;
  return;
}

short f33_select_torque_pair_differences(short first_pair,short second_pair)

{
  short sVar1;
  
  DAT_febe7de8 = DAT_febe7cb7;
  if ((DAT_febe71ec & 0x60) != 0) {
    if ((DAT_febe71ec >> 5 & 1) == 0) {
      DAT_febe7de8 = 2;
    }
    else {
      DAT_febe7de8 = 1;
    }
  }
  if (1 < DAT_febe7de8) {
    return first_pair;
  }
  if (DAT_febe7de8 == 0) {
    sVar1 = (short)(((int)first_pair - (int)second_pair) / 2);
  }
  else {
    sVar1 = -second_pair;
  }
  return sVar1;
}

void FUN_0004867e(void)

{
  DAT_febe7e0c = 0;
  return;
}

void f33_fill_constant_block_486aa(void)

{
  DAT_febe7e2e = 0x8000;
  DAT_febe7e30 = 0x8000;
  DAT_febe7e32 = 0x8000;
  DAT_febe7e34 = 0x8000;
  DAT_febe7e36 = 0x8000;
  DAT_febe7e38 = 0x8000;
  DAT_febe7e10 = 0x8000;
  DAT_febe7e12 = 0x8000;
  DAT_febe7e14 = 0x8000;
  DAT_febe7e16 = 0x8000;
  DAT_febe7e18 = 0x8000;
  DAT_febe7e1a = 0x8000;
  return;
}

void FUN_00048d32(void)

{
  f33_monitor_current_retained_reference[0] = 0x8000;
  f33_monitor_current_retained_reference[1] = 0x8000;
  f33_monitor_current_retained_reference[2] = 0x8000;
  f33_monitor_current_retained_reference[3] = 0x8000;
  f33_monitor_current_retained_reference[4] = 0x8000;
  f33_monitor_current_retained_reference[5] = 0x8000;
  return;
}

void f33_fill_constant_block_495a4(void)

{
  DAT_febe7e9c = 0;
  DAT_febe7e9e = 0;
  DAT_febe7ea0 = 0;
  DAT_febe7ea2 = 0;
  DAT_febe7ea4 = 0;
  DAT_febe7ea6 = 0;
  return;
}

void FUN_0004963e(void)

{
  DAT_febe7ea8 = 0;
  DAT_febe7eaa = 0;
  DAT_febe7eac = 0;
  DAT_febe7eb0 = 0;
  return;
}

void FUN_000496d4(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = 0;
  do {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7ef0u + (uint32_t)(iVar3) * 1u)))) = 0;
    iVar2 = iVar3 + 1;
    *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe7eb4u)) + iVar3 * 2) = 0;
    iVar1 = iVar3 + -0x1d;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    f33_application_receive_status[iVar3] = '\x01';
    iVar1 = iVar3 + -0x1d;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  return;
}

uchar f33_get_application_receive_status(uint selector)

{
  if ((selector & 0xff) < 0x1e) {
    return f33_application_receive_status[selector & 0xff];
  }
  return '\x01';
}

void FUN_00049918(void)

{
  if (((DAT_febee826 == '\"') && (DAT_febe7f37 == '\x11')) ||
     ((DAT_febee826 == '\0' && (DAT_febe7f37 == '3')))) {
    DAT_febe7f48 = 0;
    DAT_febe7f4a = 0;
    if (DAT_febee88e <= DAT_000317b4) {
      DAT_febe7f4a = DAT_000317b4 - DAT_febee88e;
    }
  }
  if (DAT_febe7f48 < DAT_febe7f4a) {
    DAT_febe7f34 = 0;
    DAT_febe7f48 = DAT_febe7f48 + 1;
  }
  else {
    DAT_febe7f34 = 0x5a;
  }
  DAT_febe7f37 = DAT_febee826;
  return;
}

void f33_fill_constant_block_49b3c(void)

{
  DAT_febe7f54 = 0;
  DAT_febe7f55 = 0;
  DAT_febe7f56 = 0;
  DAT_febe7f57 = 0;
  DAT_febe7f58 = 0;
  DAT_febe7f59 = 0;
  DAT_febe7f5a = 0;
  DAT_febe7f5b = 0;
  DAT_febe7f5c = 0;
  DAT_febe7f5d = 0xff;
  DAT_febe7f5e = 0xff;
  DAT_febe7f5f = 0xff;
  return;
}

char FUN_00049b5c(char param_1)

{
  uint32_t puVar1;
  char extraout_r6;
  char cVar2;
  ushort uVar3;
  
  puVar1 = 0xfebeb800u;
  if (((param_1 == DAT_febe7f53) || (param_1 == '3')) || (DAT_febe7f53 == '\"')) {
    cVar2 = DAT_febe7f4c;
    uVar3 = DAT_febe7f60;
    if (((param_1 != '\x11') && (DAT_febe7f4c == 'Z')) &&
       ((DAT_0002fbf0 < DAT_febe7f60 || (uVar3 = DAT_febe7f60 + 1, DAT_0002fbf0 < uVar3)))) {
      cVar2 = '\0';
    }
  }
  else {
    puVar1 = 0xfebeb800u;
    f33_fill_constant_block_49b3c();
    cVar2 = 'Z';
    uVar3 = 0;
    param_1 = extraout_r6;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x38b4))))) = cVar2;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x38a0)))) = uVar3;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x38ad))))) = param_1;
  return cVar2;
}

void FUN_00049c64(void)

{
  if (((DAT_febe7f56 == 'Z') || (1 < f33_internal_source_admission_state)) || (DAT_febe803e != '\0')
     ) {
    DAT_febe7f55 = 0;
  }
  else if ((DAT_febe7f54 != DAT_febe803d) &&
          ((DAT_0002fbec <= DAT_febe7f55 ||
           (DAT_febe7f55 = DAT_febe7f55 + 1, DAT_0002fbec <= DAT_febe7f55)))) {
    DAT_febe7f56 = 'Z';
  }
  DAT_febe7f54 = DAT_febe803d;
  return;
}

void FUN_00049cb0(void)

{
  if (((DAT_febe7f59 == 'Z') || (1 < f33_internal_source_admission_state)) || (DAT_febe8018 != '\0')
     ) {
    DAT_febe7f58 = 0;
  }
  else if ((DAT_febe7f57 != DAT_febe8017) &&
          ((DAT_0002fbed <= DAT_febe7f58 ||
           (DAT_febe7f58 = DAT_febe7f58 + 1, DAT_0002fbed <= DAT_febe7f58)))) {
    DAT_febe7f59 = 'Z';
  }
  DAT_febe7f57 = DAT_febe8017;
  return;
}

void FUN_00049cfc(void)

{
  if (((DAT_febe7f5c == 'Z') || (1 < f33_internal_source_admission_state)) || (DAT_febe800a != '\0')
     ) {
    DAT_febe7f5b = 0;
  }
  else if ((DAT_febe7f5a != DAT_febe800b) &&
          ((DAT_0002fbee <= DAT_febe7f5b ||
           (DAT_febe7f5b = DAT_febe7f5b + 1, DAT_0002fbee <= DAT_febe7f5b)))) {
    DAT_febe7f5c = 'Z';
  }
  DAT_febe7f5a = DAT_febe800b;
  return;
}

void FUN_00049d4a(void)

{
  FUN_00049c64();
  FUN_00049cb0();
  FUN_00049cfc();
  return;
}

void FUN_00049de4(void)

{
  undefined1 uVar1;
  undefined1 uVar2;
  undefined1 uVar3;
  undefined1 uVar4;
  uint uVar5;
  
  uVar3 = DAT_febe7f52;
  uVar2 = DAT_febe7f51;
  uVar1 = DAT_febe7f50;
  uVar5 = 0;
  do {
    uVar4 = uVar2;
    if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x290dau + (uint32_t)(uVar5 * 8) * 1u)))) != '\x01') &&
       (uVar4 = uVar1, (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x290dau + (uint32_t)(uVar5 * 8) * 1u)))) == '\x02')) {
      uVar4 = uVar3;
    }
    FUN_0008e7d0((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x290d4u + (uint32_t)(uVar5 * 8) * 1u)))),uVar4);
    uVar5 = uVar5 + 1;
  } while (uVar5 < 0x1e);
  return;
}

void FUN_00049efe(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  f33_fill_constant_block_49ec6();
  f33_fill_constant_block_49eda();
  f33_fill_constant_block_49eec();
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3898))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3897))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3896))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3895))))) = 0;
  return;
}

void FUN_0004a44a(void)

{
  DAT_febe7f94 = 0;
  DAT_febe7f95 = 1;
  return;
}

void f33_update_application_communication_inhibits(void)

{
  if ((DAT_febee86d == 'Z') &&
     (((DAT_febe7f95 == '\0' || (DAT_febee860 != '\0')) && (DAT_febe7f94 == '\x01')))) {
    DAT_febe7f98 = 0;
    DAT_febe7f97 = 0x5a;
    DAT_febe7f96 = 0x5a;
  }
  else {
    DAT_febe7f97 = 0;
    if (DAT_febe7f98 < DAT_000317b8) {
      DAT_febe7f98 = DAT_febe7f98 + 1;
    }
    else {
      DAT_febe7f96 = 0;
    }
  }
  return;
}

void FUN_0004a49e(void)

{
  FUN_0004a44a();
  f33_update_application_communication_inhibits();
  return;
}

bool FUN_0004a4b2(void)

{
  if ((DAT_febee81f != '\0') && (DAT_febee828 != 'Z')) {
    return DAT_febee825 != 'Z';
  }
  return false;
}

void FUN_0004a4d4(void)

{
  DAT_febe7fa8 = 0;
  DAT_febe7fac = 0;
  if (DAT_febe7f9f == '\x11') {
    DAT_febe7f9f = '\0';
  }
  if (DAT_febe7fa1 == '\x11') {
    DAT_febe7fa1 = '\0';
  }
  return;
}

void FUN_0004a4f6(void)

{
  if (f33_route30_receive_status == '\0') {
    DAT_febe7fa4 = 0;
    DAT_febe7fa1 = 0;
    DAT_febe7faa = 0;
    DAT_febe7fa0 = 0;
  }
  else if (((DAT_febe7fa0 == '\0') || (DAT_febe7fa0 == '\x11')) && (DAT_febe7faa < DAT_0002baf0)) {
    DAT_febe7faa = DAT_febe7faa + 1;
    DAT_febe7fa0 = 0x11;
  }
  else {
    DAT_febe7fa0 = 0x22;
    DAT_febe7fa4 = 0x5a;
  }
  DAT_febe7f9e = 0;
  DAT_febe7f9f = 0;
  DAT_febe7fa2 = 0;
  DAT_febe7fa3 = 0;
  DAT_febe7fa6 = 0;
  DAT_febe7fa8 = 0;
  return;
}

void FUN_0004a54a(void)

{
  if (f33_route30_receive_status == '\0') {
    DAT_febe7fa2 = 0;
    DAT_febe7f9f = 0;
    DAT_febe7fa6 = 0;
    DAT_febe7f9e = 0;
  }
  else if (((DAT_febe7f9e == '\0') || (DAT_febe7f9e == '\x11')) && (DAT_febe7fa6 < DAT_0002baee)) {
    DAT_febe7fa6 = DAT_febe7fa6 + 1;
    DAT_febe7f9e = 0x11;
  }
  else {
    DAT_febe7f9e = 0x22;
    DAT_febe7fa2 = 0x5a;
  }
  DAT_febe7fa0 = 0;
  DAT_febe7fa1 = 0;
  DAT_febe7fa4 = 0;
  DAT_febe7fa5 = 0;
  DAT_febe7faa = 0;
  DAT_febe7fac = 0;
  return;
}

void f33_fill_constant_block_4a59e(void)

{
  DAT_febe7f9e = 0;
  DAT_febe7f9f = 0;
  DAT_febe7fa2 = 0;
  DAT_febe7fa3 = 0;
  DAT_febe7fa6 = 0;
  DAT_febe7fa8 = 0;
  DAT_febe7fa0 = 0;
  DAT_febe7fa1 = 0;
  DAT_febe7fa4 = 0;
  DAT_febe7fa5 = 0;
  DAT_febe7faa = 0;
  DAT_febe7fac = 0;
  return;
}

void FUN_0004a5bc(void)

{
  DAT_febe7fa6 = 0;
  DAT_febe7faa = 0;
  if (DAT_febe7f9e == '\x11') {
    DAT_febe7f9e = '\0';
  }
  if (DAT_febe7fa0 == '\x11') {
    DAT_febe7fa0 = '\0';
  }
  return;
}

void FUN_0004a5de(void)

{
  if (f33_route30_receive_status == '\0') {
    DAT_febe7fa5 = 0;
    DAT_febe7fa0 = 0;
    DAT_febe7fac = 0;
    DAT_febe7fa4 = 0;
    DAT_febe7fa1 = '\0';
  }
  else if ((DAT_febee812 == '\x11') && (DAT_0002bb24 <= DAT_febee892)) {
    if (((DAT_febe7fa1 == '\0') || (DAT_febe7fa1 == '\x11')) && (DAT_febe7fac < DAT_0002baf2)) {
      DAT_febe7fac = DAT_febe7fac + 1;
      DAT_febe7fa1 = '\x11';
    }
    else {
      DAT_febe7fa1 = '\"';
      DAT_febe7fa5 = 0x5a;
    }
  }
  DAT_febe7f9e = 0;
  DAT_febe7f9f = 0;
  DAT_febe7fa2 = 0;
  DAT_febe7fa3 = 0;
  DAT_febe7fa6 = 0;
  DAT_febe7fa8 = 0;
  return;
}

void FUN_0004a64e(void)

{
  if (f33_route30_receive_status == '\0') {
    DAT_febe7fa3 = 0;
    DAT_febe7f9e = 0;
    DAT_febe7fa8 = 0;
    DAT_febe7fa2 = 0;
    DAT_febe7f9f = '\0';
  }
  else if ((DAT_febee812 == '\x11') && (DAT_0002bb24 <= DAT_febee892)) {
    if (((DAT_febe7f9f == '\0') || (DAT_febe7f9f == '\x11')) && (DAT_febe7fa8 < DAT_0002baf2)) {
      DAT_febe7fa8 = DAT_febe7fa8 + 1;
      DAT_febe7f9f = '\x11';
    }
    else {
      DAT_febe7f9f = '\"';
      DAT_febe7fa3 = 0x5a;
    }
  }
  DAT_febe7fa0 = 0;
  DAT_febe7fa1 = 0;
  DAT_febe7fa4 = 0;
  DAT_febe7fa5 = 0;
  DAT_febe7faa = 0;
  DAT_febe7fac = 0;
  return;
}

void FUN_0004a6be(void)

{
  if ((((DAT_febe7f9e == '\"') || (DAT_febe7fa0 == '\"')) || (DAT_febe7f9f == '\"')) ||
     (DAT_febe7fa1 == '\"')) {
    DAT_febe7f9c = 0x22;
  }
  else if (((DAT_febe7f9e != '\0') || (DAT_febe7fa0 != '\0')) ||
          ((DAT_febe7f9f != '\0' || (DAT_febe7f9c = 0, DAT_febe7fa1 != '\0')))) {
    DAT_febe7f9c = 0x11;
  }
  return;
}

undefined4 FUN_0004a7ac(void)

{
  if (((DAT_febee81f != '\0') && (DAT_febee828 != 'Z')) && (DAT_febee825 != 'Z')) {
    return 0x5a;
  }
  return 0;
}

void FUN_0004aa1c(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = 0;
  do {
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7fb8u + (uint32_t)(iVar3) * 1u)))) == '\x11') {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7fb8u + (uint32_t)(iVar3) * 1u)))) = 0;
    }
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -7;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  DAT_febe7fc2 = 0;
  DAT_febe7fc4 = 0;
  return;
}

void FUN_0004aa40(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = 0;
  do {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7fb8u + (uint32_t)(iVar3) * 1u)))) = 0;
    iVar2 = iVar3 + 1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7fb0u + (uint32_t)(iVar3) * 1u)))) = 0;
    iVar1 = iVar3 + -7;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  DAT_febe7fc2 = 0;
  DAT_febe7fc4 = 0;
  return;
}

void FUN_0004aac0(void)

{
  DAT_febe687d = 0;
  FUN_0006b7d2(((undefined *)camry_host_ptr(0xfebe7fc8u)));
  return;
}

void FUN_0004aad4(void)

{
  DAT_febe687d = 0;
  FUN_0006b7d2(((undefined *)camry_host_ptr(0xfebe7fc8u)));
  return;
}

void FUN_0004abbe(void)

{
  int iVar1;
  
  if ((DAT_febe80b0 & 0x3ffff) == 0x20000) {
    DAT_febe7fd0 = 0;
  }
  else {
    iVar1 = (int)(DAT_febe80b0 * 0x271d) / 0x100000;
    if (iVar1 + -0x7fff < 0 == (iVar1 < 0 && -1 < iVar1 + -0x7fff)) {
      iVar1 = 0x7fff;
    }
    if (iVar1 + 0x7fff < 0 != (-1 < iVar1 && iVar1 + 0x7fff < 0)) {
      iVar1 = -0x7fff;
    }
    DAT_febe7fd0 = (undefined2)iVar1;
  }
  return;
}

void FUN_0004ac00(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7fd4u)));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3820))))) = 0;
  return;
}

void FUN_0004ac14(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7fd4u)));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3820))))) = 0;
  return;
}

void f33_fill_constant_block_4ad1a(void)

{
  DAT_febe7fe4 = 0;
  DAT_febe7fe5 = 0;
  DAT_febe7fe6 = 0;
  DAT_febe7fe8 = 0;
  DAT_febe7fe7 = 0;
  DAT_febe7fe9 = 0;
  DAT_febe7fea = 0;
  return;
}

void FUN_0004ad2e(void)

{
  if ((f33_internal_source_admission_state < 2) && (DAT_febe8021 == '\0')) {
    if ((DAT_00030e3d <= DAT_febe7fe7) ||
       (DAT_febe7fe7 = DAT_febe7fe7 + 1, DAT_00030e3d <= DAT_febe7fe7)) {
      DAT_febe7fea = 0;
    }
  }
  else {
    DAT_febe7fe7 = 0;
  }
  DAT_febe7fe8 = 0;
  return;
}

void FUN_0004ad68(void)

{
  if ((f33_internal_source_admission_state < 2) && (DAT_febe806f == '\0')) {
    if ((DAT_00030e3d <= DAT_febe7fe6) ||
       (DAT_febe7fe6 = DAT_febe7fe6 + 1, DAT_00030e3d <= DAT_febe7fe6)) {
      DAT_febe7fe9 = 0;
    }
  }
  else {
    DAT_febe7fe6 = 0;
  }
  DAT_febe7fe5 = 0;
  return;
}

void FUN_0004ada2(void)

{
  uint32_t puVar1;
  byte bVar2;
  
  bVar2 = DAT_febe7fe4;
  puVar1 = 0xfebeb800u;
  if (DAT_febe7fe4 < DAT_00030e3c) {
    bVar2 = DAT_febe7fe4 + 1;
  }
  else {
    puVar1 = 0xfebeb800u;
    FUN_0004ad2e();
    FUN_0004ad68();
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x381c))))) = bVar2;
  return;
}

void FUN_0004adce(void)

{
  DAT_febe7fec = (DAT_febe800c == '\x01') * '\b' +
                 (DAT_febe8016 == '\x01') * '\x04' +
                 (DAT_febe803b == '\x01') * '\x02' + (DAT_febe803c == '\x01');
  return;
}

void FUN_0004bffa(void)

{
  DAT_febe8143 = 0;
  return;
}

void FUN_0004c0e8(void)

{
  undefined *puVar1;
  
  if (((DAT_febee8cc & 0xff00) == 0x400) &&
     (DAT_febe812e = (undefined1)DAT_febe6764, (DAT_febe6764 & 0x1ff) == 0)) {
    puVar1 = ((void *)camry_host_ptr((uint32_t)(DAT_febe64ec)));
    if ((int)(DAT_febe64ec + -0x8a99) < 0 ==
        ((int)DAT_febe64ec < 0 && -1 < (int)(DAT_febe64ec + -0x8a99))) {
      puVar1 = ((undefined *)camry_host_ptr(0x8a99u));
    }
    if ((int)camry_host_addr((((undefined *)camry_host_ptr(0x8abcu)) + (int)puVar1)) < 0 !=
        (-1 < (int)camry_host_addr(puVar1) && (int)camry_host_addr((((undefined *)camry_host_ptr(0x8abcu)) + (int)puVar1)) < 0)) {
      puVar1 = ((undefined *)camry_host_ptr((uint32_t)(0xffff7544)));
    }
    DAT_febe8162 = (undefined2)(((int)camry_host_addr(puVar1) * 0x7627) / 0x100000);
  }
  else {
    DAT_febe812e = 1;
    DAT_febe8162 = 0;
  }
  DAT_febe80f5 = 0;
  DAT_febe80fd = 0;
  DAT_febe80fe = 0;
  DAT_febe80ff = 0;
  return;
}

void FUN_0004c142(void)

{
  DAT_febe8103 = 0;
  DAT_febe8104 = 0;
  DAT_febe8108 = 0;
  return;
}

void FUN_0004c14e(void)

{
  uint32_t puVar1;
  undefined1 uStack_7;
  undefined1 auStack_6 [2];
  
  puVar1 = 0xfebeb800u;
  DAT_febe810d = (undefined1)DAT_febe8048;
  DAT_febe810b = DAT_febe80de | 0x20;
  DAT_febe810c = (byte)((ushort)DAT_febe8048 >> 8) & 0xf;
  FUN_00070110((int)DAT_febe7d46,0x7ff,(int)0xfffff800,auStack_6);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x36f1))))) = auStack_6[0];
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x36f2))))) = auStack_6[1] & 0xf;
  FUN_0006a5cc((int)((*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x36ae)))) / 10),&uStack_7);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x36f0))))) = uStack_7;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x36ef))))) = (char)((ushort)(*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x36a8)))) >> 8);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x36ee))))) = (char)(*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x36a8))));
  return;
}

char FUN_0004c1c0(void)

{
  char cVar1;
  
  if ((DAT_febe8100 == '\x01') && (DAT_febee82b == '\0')) {
    DAT_febe812c = 'Z';
    DAT_febe812b = 0;
    cVar1 = DAT_febee82b;
  }
  else {
    cVar1 = DAT_febe8100;
    if (DAT_febe812c != 'Z') {
      DAT_febe812a = DAT_febe5339;
      return DAT_febee82b;
    }
  }
  if ((DAT_febe812b < DAT_0002fbf8) && (DAT_febe812a == DAT_febe5339)) {
    DAT_febe812b = DAT_febe812b + 1;
  }
  else {
    DAT_febe812b = '\0';
    DAT_febe812c = '\0';
    cVar1 = DAT_febee82b;
  }
  DAT_febe812a = DAT_febe5339;
  return cVar1;
}

void FUN_0004c216(undefined1 param_1)

{
  if (((DAT_febe6764 & 3) == 0) || (DAT_febe8143 == '\0')) {
    DAT_febe8101 = 0;
  }
  else {
    param_1 = 7;
    DAT_febe8101 = 1;
  }
  DAT_febe8100 = param_1;
  return;
}

void FUN_0004c24a(void)

{
  uint uVar1;
  
  uVar1 = DAT_febe82a0 - 1;
  if (3 < uVar1) {
    if (uVar1 == 4) {
      DAT_febe8102 = DAT_febe82ae;
      DAT_febe8105 = DAT_febe82ad;
      DAT_febe8106 = DAT_febe82aa;
      DAT_febe8107 = DAT_febe82ab;
      DAT_febe8109 = DAT_febe82ac;
      DAT_febe810a = 1;
      return;
    }
    if (0xd < uVar1) {
      if (uVar1 == 0xe) {
        DAT_febe8102 = DAT_febe82ae;
        DAT_febe8105 = DAT_febe82ad;
        DAT_febe8106 = DAT_febe82aa;
        DAT_febe8107 = DAT_febe82ab;
        DAT_febe8109 = DAT_febe82ac;
        DAT_febe810a = 2;
        return;
      }
      if (uVar1 != 0xf) {
        DAT_febe8102 = DAT_febe82ae;
        DAT_febe8105 = DAT_febe82ad;
        DAT_febe8106 = DAT_febe82aa;
        DAT_febe8107 = DAT_febe82ab;
        DAT_febe8109 = DAT_febe82ac;
        DAT_febe810a = 0;
        return;
      }
    }
  }
  DAT_febe810a = 3;
  DAT_febe8102 = DAT_febe82ae;
  DAT_febe8105 = DAT_febe82ad;
  DAT_febe8106 = DAT_febe82aa;
  DAT_febe8107 = DAT_febe82ab;
  DAT_febe8109 = DAT_febe82ac;
  return;
}

void FUN_0004c294(void)

{
  DAT_febe80e3 = DAT_febee848;
  return;
}

void f33_fill_constant_block_4c29e(void)

{
  DAT_febe80e4 = 0;
  DAT_febe80e5 = 0;
  DAT_febe80fc = 0;
  DAT_febe80e6 = 0;
  DAT_febe80e7 = 0;
  DAT_febe80e8 = 0;
  DAT_febe80e9 = 0;
  DAT_febe80ea = 0;
  return;
}

void FUN_0004c2b4(void)

{
  DAT_febe80fa = 0xff;
  DAT_febe80fb = 0xff;
  return;
}

void f33_fill_constant_block_4c2c0(void)

{
  DAT_febe80f3 = 0;
  DAT_febe80eb = 0;
  DAT_febe80ed = 0;
  DAT_febe80ef = 0;
  DAT_febe80f1 = 0;
  return;
}

void FUN_0004c2d0(void)

{
  DAT_febe8154 = 0;
  DAT_febe80df = 1;
  return;
}

void f33_fill_constant_block_4c2dc(void)

{
  DAT_febe80ee = 0;
  DAT_febe80f0 = 0;
  DAT_febe80f2 = 0;
  DAT_febe80ec = DAT_febee834;
  DAT_febe80f4 = 0;
  DAT_febe80f6 = DAT_febee82f;
  DAT_febe80f7 = DAT_febee83d;
  DAT_febe80f8 = DAT_febee83b;
  DAT_febe80f9 = DAT_febee83c;
  DAT_febe80e0 = DAT_febee83a;
  DAT_febe8156 = DAT_febee8bc;
  return;
}

void FUN_0004c314(void)

{
  DAT_febe80dc = DAT_febee830;
  return;
}

void f33_fill_constant_block_4c31e(void)

{
  DAT_febe8113 = 0;
  DAT_febe8114 = 0;
  DAT_febe8115 = 0;
  DAT_febe8116 = 0;
  DAT_febe8117 = 0;
  return;
}

void FUN_0004c32e(void)

{
  DAT_febe8170 = 0;
  DAT_febe815c = 0;
  DAT_febe8118 = 0;
  DAT_febe8119 = 0;
  return;
}

void FUN_0004c33c(void)

{
  DAT_febe815a = 0;
  DAT_febe811a = 0;
  DAT_febe811b = 0;
  DAT_febe812d = 0;
  return;
}

void f33_fill_constant_block_4c34a(void)

{
  DAT_febe811d = 0;
  DAT_febe811e = 0;
  DAT_febe811f = 0;
  DAT_febe8121 = 0;
  DAT_febe8123 = 0;
  DAT_febe8120 = 0;
  DAT_febe8122 = 0;
  DAT_febe8124 = 0;
  DAT_febe8126 = 0;
  DAT_febe8135 = 0;
  DAT_febe8131 = 0;
  DAT_febe815e = 0;
  DAT_febe8125 = 0;
  DAT_febe8132 = 0;
  DAT_febe8133 = 0;
  DAT_febe811c = 0;
  return;
}

void f33_fill_constant_block_4c370(void)

{
  DAT_febe8160 = 0;
  DAT_febe8127 = 0;
  DAT_febe8128 = 0;
  DAT_febe8129 = 0;
  DAT_febe8134 = 0;
  return;
}

void FUN_0004c5e8(undefined1 param_1)

{
  DAT_febe8143 = param_1;
  return;
}

void FUN_0004c5f0(void)

{
  DAT_febe8190 = DAT_0002fbfc;
  return;
}

void FUN_0004c5fe(void)

{
  if (DAT_febee82a == '\0') {
    if (DAT_febe8190 <= DAT_0002fbfc) {
      DAT_febe8190 = DAT_febe8190 + 1;
    }
  }
  else {
    DAT_febe8190 = 0;
  }
  if ((DAT_febee82a == 'Z') || (DAT_febe8190 <= DAT_0002fbfc)) {
    DAT_febe818c = 0x5a;
  }
  else {
    DAT_febe818c = 0;
  }
  return;
}

uint FUN_0004c63c(void)

{
  DAT_febe8187 = 0;
  if (DAT_febee836 == '\x01') {
    DAT_febe8187 = 0x5a;
  }
  return DAT_febe8187;
}

uint FUN_0004c6e6(void)

{
  DAT_febe8189 = DAT_febe80c9 & 2;
  if ((((((DAT_febe80c9 & 2) != 0) || ((DAT_febe6764 & 0x1ff) != 0)) || (DAT_febe82ba != 0)) ||
      ((DAT_febe82c2 != 0 || (DAT_febe82c4 != 0)))) ||
     ((DAT_febee857 == '\"' || ((DAT_febee858 == '\"' || (DAT_febee859 == '\"')))))) {
    DAT_febe8189 = 0x5a;
  }
  return DAT_febe8189;
}

void FUN_0004c772(void)

{
  DAT_febe818d = DAT_febee88c;
  DAT_febe818e = DAT_febee88d;
  return;
}

void f33_set_monitor_pending_projection(uchar index,uchar status)

{
  if (index < 10) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe817du + (uint32_t)(index) * 1u)))) = status;
  }
  return;
}

void thunk_FUN_0004d4bc(void)

{
  FUN_0004d4bc();
  return;
}

undefined4 f33_return_const_5a_4cf66(void)

{
  return 0x5a;
}

void FUN_0004cf6c(void)

{
  uint uVar1;
  
  uVar1 = 0;
  DAT_febe81b2 = 0;
  DAT_febe8194 = 0;
  DAT_febe8195 = 0;
  DAT_febe81c0 = 0;
  f33_diagnostic_normal_tx_policy_request = '\0';
  f33_dtc_setting_inhibit_request = '\0';
  f33_dtc_requested_status_mask = '\0';
  f33_dtc_iteration_result_count = 0;
  f33_dtc_iteration_catalogue_cursor = 0;
  f33_snapshot_identifier_cached_dtc = 0;
  DAT_febe8199 = 0;
  DAT_febe819a = 0;
  DAT_febe81b8 = 0;
  DAT_febe81ad = 0;
  DAT_febe81ba = 0;
  DAT_febe81bc = 0;
  f33_app_programming_mode_request_latched = '\0';
  DAT_febe81af = 0;
  do {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe819bu + (uint32_t)(uVar1) * 1u)))) = 0;
    uVar1 = uVar1 + 1;
  } while (uVar1 < 0x10);
  return;
}

uint f33_diag_translate_application_request_status(int application_status)

{
  if (application_status == 0) {
    return 0;
  }
  if (application_status == -0xc) {
    return 4;
  }
  if (application_status == -7) {
    return 8;
  }
  if (application_status != -6) {
    if (application_status != -1) {
      return 9;
    }
    return 2;
  }
  return 5;
}

uint f33_check_diagnostic_application_admission(uchar addressing_kind)

{
  uint uVar1;
  
  if ((DAT_febe81cc == 'Z') && (DAT_febe81ac == 'Z')) {
    uVar1 = (uint)(DAT_febe7f97 == 'Z');
  }
  else {
    uVar1 = 1;
  }
  DAT_febe819a = addressing_kind;
  return uVar1;
}

uint f33_did_available_4d3be(void)

{
  if (DAT_febee91c == -0x55aaaa56) {
    return 0x5a;
  }
  return 0;
}

uint f33_did_available_4d3d6(void)

{
  uint uVar1;
  
  if (DAT_febee802 == 'Z') {
    uVar1 = 0x5a;
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}

uint f33_did_available_4d3e4(void)

{
  uint uVar1;
  
  if (DAT_febee804 == 'Z') {
    uVar1 = 0x5a;
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}

uint f33_did_available_4d3f2(void)

{
  uint uVar1;
  
  if (DAT_febee803 == 'Z') {
    uVar1 = 0x5a;
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}

uint f33_did_available_4d400(void)

{
  uint uVar1;
  
  uVar1 = 0x5a;
  if (DAT_febee870 == 'Z') {
    uVar1 = 0;
  }
  return uVar1;
}

uint f33_did_available_4d412(void)

{
  uint uVar1;
  
  if (DAT_febee870 == 'Z') {
    uVar1 = 0x5a;
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}

uint f33_did_available_4d420(void)

{
  uint uVar1;
  
  if (DAT_febee805 == 'Z') {
    uVar1 = 0x5a;
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}

uint f33_did_available_4d42e(void)

{
  uint uVar1;
  
  if (DAT_febee806 == 'Z') {
    uVar1 = 0x5a;
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}

uint f33_did_metadata_always_available(void)

{
  return 0x5a;
}

uint f33_did_always_available(void)

{
  return 0x5a;
}

void FUN_0004d4bc(void)

{
  DAT_febe81c8 = 0;
  return;
}

void FUN_0004d4c4(void)

{
  DAT_febe8195 = 0;
  return;
}

undefined1 FUN_0004d4f2(int param_1)

{
  undefined1 uStack_5;
  
  uStack_5 = 0;
  if (param_1 == 0) {
    uStack_5 = 0;
  }
  else if (param_1 == -1) {
    uStack_5 = 2;
  }
  else {
    FUN_0004d144(param_1,&uStack_5);
  }
  return uStack_5;
}

uint f33_app_session_transition_precondition(uchar current_session_ignored,uchar target)

{
  if ((target == '\x02') && (f33_communication_control_admission_limit < DAT_febee892)) {
    return 0xb;
  }
  return 0;
}

undefined1 FUN_0004d5d8(void)

{
  undefined1 uVar1;
  
  if (((DAT_febee81f == '\x11') || (DAT_febe66ba < DAT_000318b2)) ||
     (uVar1 = 0, DAT_febe819a != '\0')) {
    uVar1 = 1;
  }
  return uVar1;
}

void FUN_0004d5fe(void)

{
  f33_app_programming_mode_request_latched = '\0';
  return;
}

uint f33_validate_clear_all_diagnostic_group(uint group)

{
  return (uint)(group != 0xffffff);
}

uint f33_begin_filtered_dtc_iteration(uchar mask)

{
  f33_dtc_requested_status_mask = mask & 0xb9;
  f33_dtc_iteration_result_count = 0;
  f33_dtc_iteration_catalogue_cursor = 0;
  return 0;
}

uchar f33_get_did_metadata_route_kind(ushort did)

{
  uint uVar1;
  F33DidPublicationMetadata *pFVar2;
  uchar uVar3;
  ushort uStack_e;
  
  uVar3 = 0xff;
  pFVar2 = f33_get_did_publication_metadata(&uStack_e);
  for (uVar1 = 0; (int)(uVar1 - uStack_e) < 0 != ((int)uVar1 < 0 && -1 < (int)(uVar1 - uStack_e));
      uVar1 = uVar1 + 1) {
    if (pFVar2[uVar1].did == did) {
      uVar3 = pFVar2[uVar1 & 0xffff].route_kind;
    }
  }
  return uVar3;
}

undefined4 f33_rdbi_0111_callback(void)

{
  return 0;
}

undefined4 f33_rdbi_1066_callback(void)

{
  return 0;
}

undefined4 f33_rdbi_106a_callback(void)

{
  return 0;
}

undefined4 f33_rdbi_10c7_callback(void)

{
  return 0;
}

undefined4 f33_rdbi_10c8_callback(void)

{
  return 0;
}

undefined4 f33_rdbi_10c9_callback(void)

{
  return 0;
}

undefined4 f33_rdbi_10f7_callback(void)

{
  return 0;
}

undefined4 f33_rdbi_10f8_callback(void)

{
  return 0;
}

undefined4 f33_rdbi_10f9_callback(void)

{
  return 0;
}

undefined4 f33_rdbi_1124_callback(void)

{
  return 0;
}

undefined4 f33_rdbi_1125_callback(void)

{
  return 0;
}

undefined4 f33_rdbi_1126_callback(void)

{
  return 0;
}

undefined4 f33_rdbi_1127_callback(void)

{
  return 0;
}

undefined4 f33_rdbi_1128_callback(void)

{
  return 0;
}

undefined4 f33_rdbi_1129_callback(void)

{
  return 0;
}

undefined4 f33_rdbi_112f_callback(void)

{
  return 0;
}

undefined4 f33_rdbi_1130_callback(void)

{
  return 0;
}

undefined4 f33_rdbi_1131_callback(void)

{
  return 0;
}

undefined4 f33_rdbi_11bc_callback(void)

{
  return 0;
}

undefined4 f33_rdbi_1c99_callback(void)

{
  return 0;
}

undefined4 f33_rdbi_1c9a_callback(void)

{
  return 0;
}

undefined4 f33_rdbi_1c9b_callback(void)

{
  return 0;
}

undefined4 f33_rdbi_1c9c_callback(void)

{
  return 0;
}

undefined4 f33_rdbi_1c9d_callback(void)

{
  return 0;
}

undefined4 f33_rdbi_1c9e_callback(void)

{
  return 0;
}

undefined4 f33_rdbi_1c9f_callback(void)

{
  return 0;
}

undefined4 f33_rdbi_1ca0_callback(void)

{
  return 0;
}

undefined4 f33_rdbi_1f03_callback(void)

{
  return 0;
}

undefined4 f33_rdbi_1f04_callback(void)

{
  return 0;
}

uint f33_communication_request_sample_above_limit(void)

{
  return (uint)(f33_communication_control_admission_limit < DAT_febee892);
}

void f33_publish_diagnostic_normal_tx_policy_request(uchar network_selector,uchar disable_tx)

{
  uchar uVar1;
  
  uVar1 = '\0';
  if ((disable_tx == '\0') || (uVar1 = '\x11', disable_tx == '\x01')) {
    f33_diagnostic_normal_tx_policy_request = uVar1;
  }
  return;
}

uint f33_write_0204_precondition(void)

{
  uint uVar1;
  
  if (DAT_000318ae < DAT_febee892) {
    uVar1 = 5;
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}

uint f33_write_2001_precondition(void)

{
  uint uVar1;
  
  if (DAT_000318ae < DAT_febee892) {
    uVar1 = 5;
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}

uint f33_write_2002_precondition(void)

{
  uint uVar1;
  
  if (DAT_000318ae < DAT_febee892) {
    uVar1 = 5;
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}

uint f33_write_2005_precondition(void)

{
  uint uVar1;
  
  if (DAT_000318ae < DAT_febee892) {
    uVar1 = 5;
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}

uint f33_write_2006_precondition(void)

{
  uint uVar1;
  
  if (DAT_000318ae < DAT_febee892) {
    uVar1 = 5;
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}

uint f33_write_2007_precondition(void)

{
  uint uVar1;
  
  if (DAT_000318ae < DAT_febee892) {
    uVar1 = 5;
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}

uint f33_write_2008_precondition(void)

{
  uint uVar1;
  
  if (DAT_000318ae < DAT_febee892) {
    uVar1 = 5;
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}

uint f33_write_2009_precondition(void)

{
  uint uVar1;
  
  if (DAT_000318ae < DAT_febee892) {
    uVar1 = 5;
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}

uint f33_write_200d_precondition(void)

{
  uint uVar1;
  
  if (DAT_000318ae < DAT_febee892) {
    uVar1 = 5;
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}

uint f33_write_2010_precondition(void)

{
  uint uVar1;
  
  if (DAT_000318ae < DAT_febee892) {
    uVar1 = 5;
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}

uint f33_write_2012_precondition(void)

{
  return 0;
}

uint f33_write_2014_precondition(void)

{
  if (((DAT_febe80a5 == '\0') && (DAT_febe80a0 == '\0')) && (DAT_febee892 <= DAT_000318ae)) {
    return 0;
  }
  return 5;
}

void FUN_00050094(undefined1 param_1)

{
  FUN_0008b79a(param_1);
  return;
}

uint f33_diag_routine_1001_admit(void)

{
  uint uVar1;
  
  if (DAT_febe819a == '\x01') {
    uVar1 = 5;
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}

uint f33_diag_routine_1000_admit(void)

{
  uint uVar1;
  
  if (DAT_febe819a == '\x01') {
    uVar1 = 5;
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}

uint f33_diag_routine_1002_admit(uchar control_type)

{
  if (DAT_febe819a == '\x01') {
    return 5;
  }
  if (control_type == '\x01') {
    if (DAT_000318ae < DAT_febee892) {
      return 5;
    }
    if (DAT_febe819d == '\x01') {
      return 8;
    }
  }
  else if (control_type != '\x03') {
    return 7;
  }
  return 0;
}

uint f33_diag_routine_1009_admit(uchar control_type)

{
  if (DAT_febe819a == '\x01') {
    return 5;
  }
  if (control_type == '\x01') {
    if (DAT_febe81a1 == '\x01') {
      return 8;
    }
  }
  else if (control_type != '\x03') {
    return 7;
  }
  return 0;
}

uint f33_diag_routine_1100_admit(void)

{
  uint uVar1;
  
  if (DAT_febe819a == '\x01') {
    uVar1 = 5;
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}

uint f33_diag_routine_1106_admit(uchar control_type)

{
  if (DAT_febe819a == '\x01') {
    return 5;
  }
  if (control_type == '\x01') {
    if (DAT_000318ae < DAT_febee892) {
      return 5;
    }
    if (DAT_febe81a4 == '\x01') {
      return 8;
    }
  }
  else if (control_type != '\x03') {
    return 7;
  }
  return 0;
}

uint f33_diag_routine_1108_admit(uchar control_type)

{
  if (DAT_febe819a == '\x01') {
    return 5;
  }
  if (control_type == '\x01') {
    if (DAT_febe81a5 == '\x01') {
      return 8;
    }
  }
  else if (control_type != '\x03') {
    return 7;
  }
  return 0;
}

uint f33_diag_routine_1109_admit(uchar control_type)

{
  if (DAT_febe819a == '\x01') {
    return 5;
  }
  if (control_type == '\x01') {
    if (DAT_000318ae < DAT_febee892) {
      return 5;
    }
    if (DAT_febe81a3 == '\x01') {
      return 5;
    }
    if (DAT_febe80a0 != '\0') {
      return 5;
    }
    if (DAT_febe80a5 != '\0') {
      return 5;
    }
    if (DAT_febee81f != '\0') {
      return 5;
    }
    if (DAT_febee884 == 'Z') {
      return 5;
    }
    if (DAT_febee88a == 'Z') {
      return 5;
    }
    if (DAT_febe81a6 == '\x01') {
      return 8;
    }
  }
  else if (control_type != '\x03') {
    return 7;
  }
  return 0;
}

uint f33_diag_routine_110b_admit_noop(void)

{
  return 0;
}

uint f33_diag_routine_110b_action_noop(void)

{
  return 0;
}

void f33_diag_routine_clear_nonrunning_results(uchar preserve_selector2)

{
  uint uVar1;
  
  uVar1 = 0;
  if (preserve_selector2 == 'Z') {
    do {
      if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe819bu + (uint32_t)(uVar1) * 1u)))) != '\x01') && (uVar1 != 2)) {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe819bu + (uint32_t)(uVar1) * 1u)))) = 0;
      }
      uVar1 = uVar1 + 1;
    } while (uVar1 < 0x10);
    return;
  }
  do {
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe819bu + (uint32_t)(uVar1) * 1u)))) != '\x01') {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe819bu + (uint32_t)(uVar1) * 1u)))) = 0;
    }
    uVar1 = uVar1 + 1;
  } while (uVar1 < 0x10);
  return;
}

undefined4 f33_return_const_0_50900(void)

{
  return 0;
}

void f33_publish_dtc_setting_request(uchar selection)

{
  f33_dtc_setting_inhibit_request = '\0';
  if (selection == '\x02') {
    f33_dtc_setting_inhibit_request = 'Z';
  }
  return;
}

void FUN_00050916(undefined1 param_1,undefined2 param_2,undefined2 param_3)

{
  DAT_febe81ad = param_1;
  DAT_febe81ba = param_2;
  DAT_febe81bc = param_3;
  return;
}

void f33_snapshot_acquisition_status_flags(void)

{
  DAT_febe81d0 = DAT_febe5f26;
  DAT_febe81d1 = DAT_febe5f27;
  return;
}

void f33_snapshot_acquisition_range_fields(void)

{
  DAT_febe81d6 = DAT_febe5eea;
  DAT_febe81d8 = DAT_febe5eec;
  DAT_febe81d4 = DAT_febe5f26 ^ 0x5a;
  DAT_febe81da = DAT_febe5eee;
  DAT_febe81dc = DAT_febe5ef0;
  DAT_febe81d5 = DAT_febe5f27 ^ 0x5a;
  return;
}

void FUN_00050a52(void)

{
  DAT_febe81e0 = 0;
  if ((DAT_febe5f08 & 0x84) != 0) {
    DAT_febe81e0 = 0x5a;
  }
  DAT_febe81e1 = 0;
  if ((DAT_febe5f08 & 0x78) != 0) {
    DAT_febe81e1 = 0x5a;
  }
  DAT_febe81e2 = 0;
  if ((DAT_febe5f08 >> 1 & 1) != 0) {
    DAT_febe81e2 = 0x5a;
  }
  DAT_febe81e6 = DAT_febe5f02;
  DAT_febe81e8 = DAT_febe5f04;
  DAT_febe81ee = DAT_febe5f06;
  return;
}

void FUN_00050a9a(void)

{
  DAT_febe81e3 = 0;
  if ((DAT_febe5f10 & 0x84) != 0) {
    DAT_febe81e3 = 0x5a;
  }
  DAT_febe81e4 = 0;
  if ((DAT_febe5f10 & 0x78) != 0) {
    DAT_febe81e4 = 0x5a;
  }
  DAT_febe81e5 = 0;
  if ((DAT_febe5f10 >> 1 & 1) != 0) {
    DAT_febe81e5 = 0x5a;
  }
  DAT_febe81ea = DAT_febe5f0a;
  DAT_febe81ec = DAT_febe5f0c;
  DAT_febe81f0 = DAT_febe5f0e;
  return;
}

void f33_fill_constant_block_50b00(void)

{
  DAT_febe81f8 = 0x8000;
  DAT_febe81fa = 0x8000;
  DAT_febe81fc = 0x8000;
  DAT_febe81fe = 0x8000;
  DAT_febe81f4 = 0x8000;
  DAT_febe8200 = 0x8000;
  DAT_febe8202 = 0x8000;
  DAT_febe8204 = 0x8000;
  DAT_febe8206 = 0x8000;
  DAT_febe81f6 = 0x8000;
  DAT_febe8208 = 0x8000;
  DAT_febe820a = 0x8000;
  return;
}

void f33_copy_cell_block_50b26(void)

{
  DAT_febe821e = DAT_febe5efe;
  DAT_febe8220 = DAT_febe5ee6;
  DAT_febe8226 = DAT_febe5ee6;
  DAT_febe8212 = DAT_febe5ee6;
  DAT_febe8224 = DAT_febe5f00;
  DAT_febe8214 = DAT_febe5ee6;
  DAT_febe8216 = DAT_febe5ee6;
  DAT_febe8210 = DAT_febe5ee0;
  DAT_febe820c = DAT_febe5ee2;
  DAT_febe820e = DAT_febe5ee4;
  DAT_febe8222 = DAT_febe5ee8;
  DAT_febe8228 = DAT_febe5ee8;
  DAT_febe8218 = DAT_febe5ee8;
  DAT_febe821a = DAT_febe5ee8;
  DAT_febe821c = DAT_febe5ee8;
  return;
}

void f33_copy_acquisition_banks_to_application(void)

{
  DAT_febe8238 = f33_acquisition_application_sample_banks[0];
  DAT_febe823a = f33_acquisition_application_sample_banks[1];
  DAT_febe823c = f33_acquisition_application_sample_banks[2];
  DAT_febe822c = f33_acquisition_application_sample_banks[6];
  DAT_febe822e = f33_acquisition_application_sample_banks[7];
  DAT_febe8230 = f33_acquisition_application_sample_banks[8];
  DAT_febe823e = f33_acquisition_application_sample_banks[3];
  DAT_febe8240 = f33_acquisition_application_sample_banks[4];
  DAT_febe8242 = f33_acquisition_application_sample_banks[5];
  DAT_febe8232 = f33_acquisition_application_sample_banks[9];
  DAT_febe8234 = f33_acquisition_application_sample_banks[10];
  DAT_febe8236 = f33_acquisition_application_sample_banks[0xb];
  return;
}

void f33_copy_serial_acquisition_to_application(void)

{
  DAT_febe824c = DAT_febe5f12 << 2;
  DAT_febe824e = DAT_febe5f14 << 2;
  DAT_febe8254 = DAT_febe5f16;
  DAT_febe8244 = f33_serial_acquisition_failure_counter_snapshot[0];
  DAT_febe8246 = f33_serial_acquisition_failure_counter_snapshot[1];
  DAT_febe8248 = f33_serial_acquisition_failure_counter_snapshot[2];
  DAT_febe824a = f33_serial_acquisition_failure_counter_snapshot[3];
  DAT_febe8258 = DAT_febe5f18;
  DAT_febe825a = DAT_febe5f1a;
  DAT_febe8250 = DAT_febe5f1c << 2;
  DAT_febe8252 = DAT_febe5f1e << 2;
  DAT_febe8256 = DAT_febe5f20;
  DAT_febe8245 = f33_serial_acquisition_failure_counter_snapshot[4];
  DAT_febe8247 = f33_serial_acquisition_failure_counter_snapshot[5];
  DAT_febe8249 = f33_serial_acquisition_failure_counter_snapshot[6];
  DAT_febe824b = f33_serial_acquisition_failure_counter_snapshot[7];
  DAT_febe825c = DAT_febe5f22;
  DAT_febe825e = DAT_febe5f24;
  return;
}

void FUN_00050c38(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    *(undefined4 *)(((undefined *)camry_host_ptr(0xfebe8260u)) + iVar3 * 4) = 0;
    iVar1 = iVar3 + -4;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  return;
}

void FUN_00050c4e(byte param_1)

{
  DAT_febe3889 = param_1 & 1;
  return;
}

void FUN_00050c58(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint32_t puVar4;
  uint uVar5;
  
  puVar4 = 0xfebeb800u;
  uVar5 = 0;
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    uVar5 = uVar5 | *(uint *)(((undefined *)camry_host_ptr(0xfebe8260u)) + iVar3 * 4);
    iVar1 = iVar3 + -4;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  FUN_00050c4e(uVar5);
  (*((uint *)camry_host_ptr((uint32_t)(puVar4 + -0x358c)))) = uVar5;
  return;
}

void FUN_00050c82(uint param_1,undefined4 param_2)

{
  if ((param_1 & 0xff) < 5) {
    *(undefined4 *)(((undefined *)camry_host_ptr(0xfebe8260u)) + (param_1 & 0xff) * 4) = param_2;
  }
  return;
}

void FUN_00050fae(void)

{
  DAT_febe82ca = f33_classifier_primary_age_threshold;
  DAT_febe82cc = f33_classifier_secondary_age_threshold;
  DAT_febe82ce = f33_classifier_retained_age_threshold;
  return;
}

void f33_reset_classifier_counts_and_flags(void)

{
  DAT_febe82ba = 0;
  DAT_febe82bc = 0;
  DAT_febe82c0 = 0;
  DAT_febe82be = 0;
  DAT_febe82c2 = 0;
  DAT_febe82c4 = 0;
  DAT_febe82d0 = 0;
  DAT_febe82c6 = 0;
  DAT_febe82c8 = 0;
  DAT_febe82ca = f33_classifier_primary_age_threshold;
  DAT_febe82cc = f33_classifier_secondary_age_threshold;
  DAT_febe82a3 = 0;
  DAT_febe82a4 = 0;
  DAT_febe82ce = f33_classifier_retained_age_threshold;
  DAT_febe82a5 = 0;
  return;
}

void FUN_000515ca(void)

{
  DAT_febe82a9 = 0x5a;
  return;
}

void FUN_000515d4(void)

{
  DAT_febe82a2 = 0x5a;
  DAT_febe82a1 = 0x5a;
  DAT_febe82b8 = 0;
  DAT_febe82b6 = 0;
  return;
}

void FUN_00051612(void)

{
  uint uVar1;
  
  uVar1 = 0;
  DAT_febe82d5 = 0;
  DAT_febe82d4 = 0;
  do {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe82d8u + (uint32_t)(uVar1) * 1u)))) = 0;
    uVar1 = uVar1 + 1;
  } while (uVar1 < 4);
  DAT_febe82d6 = 0;
  DAT_febe82d7 = 0;
  return;
}

void f33_repair_diagnostic_queue_consumer(void)

{
  uint uVar1;
  int iVar2;
  byte bVar3;
  
  if (3 < DAT_febe82d7) {
    uVar1 = (uint)DAT_febe82d6;
    iVar2 = 0;
    bVar3 = 0;
    do {
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe82d8u + (uint32_t)(uVar1) * 1u)))) == '\0') {
        uVar1 = uVar1 + 1 & 0xff;
        if (3 < uVar1) {
          uVar1 = 0;
        }
      }
      else {
        iVar2 = 0x5a;
      }
      bVar3 = bVar3 + 1;
    } while ((bVar3 < 4) && (iVar2 != 0x5a));
    DAT_febe82d7 = (byte)uVar1;
  }
  return;
}

void f33_rebuild_event_descriptor_bitmap(void)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  
  uVar3 = 0;
  do {
    if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2fc52u + (uint32_t)(uVar3 * 8) * 1u)))) == '\0') || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2fc55u + (uint32_t)(uVar3 * 8) * 1u)))) == '\0')) {
      *(uint *)(((undefined *)camry_host_ptr(0xfebe6120u)) + (uVar3 >> 5) * 4) =
           *(uint *)(((undefined *)camry_host_ptr(0xfebe6120u)) + (uVar3 >> 5) * 4) | 1 << (uVar3 & 0x1f);
    }
    uVar2 = uVar3 + 1;
    iVar1 = uVar3 - 0x17f;
    uVar3 = uVar2;
  } while (iVar1 < 0 != ((int)uVar2 < 0 && -1 < iVar1));
  return;
}

void f33_clear_current_and_first_event_history(void)

{
  int iVar1;
  uint uVar2;
  uint32_t puVar3;
  puVar3 = 0xfebeb800u;
  DAT_febe5f85 = 0xaa;
  uVar2 = 0;
  do {
    iVar1 = uVar2 * 4;
    uVar2 = uVar2 + 1;
    *(undefined4 *)(((undefined *)camry_host_ptr(0xfebe6090u)) + iVar1) = 0;
    *(undefined4 *)(((undefined *)camry_host_ptr(0xfebe60c0u)) + iVar1) = 0;
    *(undefined4 *)(((undefined *)camry_host_ptr(0xfebe6120u)) + iVar1) = 0;
  } while (uVar2 < 0xc);
  f33_rebuild_event_descriptor_bitmap();
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x587f))))) = 0x5a;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x587e))))) = 0x5a;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x587c))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x587c))))) | 8;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x587b))))) = 0xa5;
  return;
}

void f33_clear_second_event_history(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  
  uVar4 = 0;
  do {
    iVar3 = uVar4 * 4;
    uVar4 = uVar4 + 1;
    *(undefined4 *)(((undefined *)camry_host_ptr(0xfebe60f0u)) + iVar3) = 0;
  } while (uVar4 < 0xc);
  iVar3 = 0;
  do {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5f71u + (uint32_t)(iVar3) * 1u)))) = 0;
    iVar2 = iVar3 + 1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5f79u + (uint32_t)(iVar3) * 1u)))) = 0;
    iVar1 = iVar3 + -7;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  DAT_febe602a = 0;
  DAT_febe6028 = 0;
  DAT_febe5f84 = DAT_febe5f84 | 0x10;
  DAT_febe5f85 = 0xa5;
  return;
}

void FUN_000525e0(uint param_1)

{
  int iVar1;
  uint uVar2;
  
  uVar2 = param_1 & 0xffff;
  if ((uVar2 != 0) && (uVar2 < 0x180)) {
    iVar1 = (uVar2 >> 5) * 4;
    uVar2 = 1 << (param_1 & 0x1f);
    *(uint *)(((undefined *)camry_host_ptr(0xfebe6090u)) + iVar1) = *(uint *)(((undefined *)camry_host_ptr(0xfebe6090u)) + iVar1) | uVar2;
    *(uint *)(((undefined *)camry_host_ptr(0xfebe60f0u)) + iVar1) = *(uint *)(((undefined *)camry_host_ptr(0xfebe60f0u)) + iVar1) | uVar2;
    *(uint *)(((undefined *)camry_host_ptr(0xfebe60c0u)) + iVar1) = *(uint *)(((undefined *)camry_host_ptr(0xfebe60c0u)) + iVar1) | uVar2;
  }
  return;
}

uint f33_get_diagnostic_event_state(uint event)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  
  uVar3 = 0;
  uVar2 = event & 0xffff;
  if ((uVar2 != 0) && (uVar2 < 0x180)) {
    iVar1 = (uVar2 >> 5) * 4;
    uVar2 = event & 0x1f;
    uVar3 = (uint)((*(uint *)(((undefined *)camry_host_ptr(0xfebe6090u)) + iVar1) >> uVar2 & 1) != 0);
    if ((*(uint *)(((undefined *)camry_host_ptr(0xfebe60c0u)) + iVar1) >> uVar2 & 1) != 0) {
      uVar3 = uVar3 | 2;
    }
    if ((*(uint *)(((undefined *)camry_host_ptr(0xfebe60f0u)) + iVar1) >> uVar2 & 1) != 0) {
      uVar3 = uVar3 | 4;
    }
  }
  return uVar3;
}

void FUN_00052aa6(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  f33_clear_diagnostic_supplement((uchar *)((undefined *)camry_host_ptr(0xfebe85acu)));
  f33_copy_diagnostic_capture
            (((F33DiagnosticCapture *)camry_host_ptr((uint32_t)(puVar1 + -0x3524))),(F33DiagnosticCapture *)((undefined *)camry_host_ptr(0x2a1f4u)));
  f33_copy_diagnostic_capture
            (((F33DiagnosticCapture *)camry_host_ptr((uint32_t)(puVar1 + -0x3434))),(F33DiagnosticCapture *)((undefined *)camry_host_ptr(0x2a1f4u)));
  f33_copy_diagnostic_capture
            (((F33DiagnosticCapture *)camry_host_ptr((uint32_t)(puVar1 + -0x3344))),(F33DiagnosticCapture *)((undefined *)camry_host_ptr(0x2a1f4u)));
  return;
}

void FUN_00053092(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe6150 = 0xaa;
  DAT_febe615a = 0x5a;
  DAT_febe6166 = 0;
  DAT_febe6151 = 0;
  f33_copy_diagnostic_capture(f33_diagnostic_capture_slots,(F33DiagnosticCapture *)((undefined *)camry_host_ptr(0x2a1f4u)));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x56ac))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x56ac))))) | 4;
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x337d))))) == '\"') {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x56ae))))) = 0;
    f33_copy_diagnostic_capture
              (((F33DiagnosticCapture *)camry_host_ptr((uint32_t)(puVar1 + -0x3434))),(F33DiagnosticCapture *)((undefined *)camry_host_ptr(0x2a1f4u)));
  }
  else {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x337d))))) = 0x44;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x56ab))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x56ab))))) | 4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x56ad))))) = 0;
  f33_copy_diagnostic_capture
            (((F33DiagnosticCapture *)camry_host_ptr((uint32_t)(puVar1 + -0x3344))),(F33DiagnosticCapture *)((undefined *)camry_host_ptr(0x2a1f4u)));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x56aa))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x56aa))))) | 4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x56b0))))) = 0xa5;
  return;
}

void f33_set_diagnostic_cache_blocker(uchar index,uchar status)

{
  if (index < 0xb) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe615bu + (uint32_t)(index) * 1u)))) = status;
  }
  return;
}

int FUN_00053532(short param_1)

{
  int iVar1;
  
  iVar1 = (int)(short)((param_1 * 10) / 0x80);
  if (iVar1 + -2000 < 0 == (iVar1 < 0 && -1 < iVar1 + -2000)) {
    iVar1 = 2000;
  }
  if (iVar1 + 500 < 0 != (-1 < iVar1 && iVar1 + 500 < 0)) {
    iVar1 = -500;
  }
  return iVar1;
}

int FUN_00053608(short param_1)

{
  int iVar1;
  
  iVar1 = (param_1 * 1000) / 0x100;
  if (iVar1 + -25000 < 0 == (iVar1 < 0 && -1 < iVar1 + -25000)) {
    iVar1 = 25000;
  }
  if (iVar1 + 25000 < 0 != (-1 < iVar1 && iVar1 + 25000 < 0)) {
    iVar1 = -25000;
  }
  return (int)(short)iVar1;
}

int FUN_00053686(short param_1)

{
  int iVar1;
  
  iVar1 = (int)(short)((param_1 * 100) / 0x80);
  if (iVar1 + -0x7fff < 0 == (iVar1 < 0 && -1 < iVar1 + -0x7fff)) {
    iVar1 = 0x7fff;
  }
  if (iVar1 + 0x7fff < 0 != (-1 < iVar1 && iVar1 + 0x7fff < 0)) {
    iVar1 = -0x7fff;
  }
  return iVar1;
}

uint FUN_00053706(uint param_1)

{
  uint uVar1;
  
  uVar1 = (param_1 & 0xffff) * 0x271 >> 0xb;
  if (9999 < uVar1) {
    uVar1 = 10000;
  }
  return uVar1;
}

uint FUN_0005377c(uint param_1)

{
  uint uVar1;
  
  uVar1 = (param_1 & 0xffff) * 100 >> 8;
  if (9999 < uVar1) {
    uVar1 = 10000;
  }
  return uVar1;
}

uint FUN_00053a2c(short param_1)

{
  uint uVar1;
  
  uVar1 = (uint)(param_1 / 100);
  if ((int)(uVar1 - 0xff) < 0 == ((int)uVar1 < 0 && -1 < (int)(uVar1 - 0xff))) {
    uVar1 = 0xff;
  }
  if ((int)uVar1 < 0) {
    uVar1 = 0;
  }
  return uVar1 & 0xff;
}

int FUN_00053b1c(short param_1)

{
  int iVar1;
  
  iVar1 = (int)(short)((param_1 * 100) / 0x80);
  if (iVar1 + -0x7fff < 0 == (iVar1 < 0 && -1 < iVar1 + -0x7fff)) {
    iVar1 = 0x7fff;
  }
  if (iVar1 + 0x7fff < 0 != (-1 < iVar1 && iVar1 + 0x7fff < 0)) {
    iVar1 = -0x7fff;
  }
  return iVar1;
}

undefined2 FUN_000546f2(uint param_1)

{
  if ((param_1 & 0xff) < 0x12) {
    return *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe860au)) + (param_1 & 0xff) * 2);
  }
  return 0;
}

undefined2 FUN_0005470c(uint param_1)

{
  if ((param_1 & 0xff) < 10) {
    return *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe862eu)) + (param_1 & 0xff) * 2);
  }
  return 0;
}

undefined4 FUN_00054bec(char param_1)

{
  undefined4 uVar1;
  
  uVar1 = 0x20;
  if (param_1 == '\0') {
    uVar1 = 0x14;
  }
  if (param_1 == '\x03') {
    uVar1 = 0x15;
  }
  if (param_1 == '\x02') {
    uVar1 = 0x17;
  }
  return uVar1;
}

int FUN_00054fa4(char param_1)

{
  uint uVar1;
  uint32_t puVar2;
  uint uVar3;
  int iVar4;
  uint uVar5;
  
  uVar1 = DAT_febe89e4;
  puVar2 = 0xfebeb800u;
  uVar3 = 0;
  uVar5 = 0;
  if (param_1 == '\0') {
    puVar2 = 0xfebeb800u;
    uVar3 = FUN_0006a130();
    uVar5 = uVar1;
  }
  if (param_1 == '\x02') {
    uVar3 = (*((uint *)camry_host_ptr((uint32_t)(puVar2 + -0x2d04))));
    uVar5 = DAT_febe89ec;
  }
  if (~uVar5 < uVar3) {
    iVar4 = -1;
  }
  else {
    iVar4 = uVar3 + uVar5;
  }
  return iVar4;
}

void FUN_000555da(uint param_1)

{
  int iVar1;
  undefined8 uVar2;
  int iVar3;
  uint uVar4;
  
  uVar2 = 0xfebeb800;
  param_1 = param_1 & 0xff;
  iVar3 = 0x5a;
  if (param_1 < 4) {
    uVar4 = 0;
    do {
      iVar1 = ((short)param_1 * 5 + uVar4) * 0x20 + (int)uVar2;
      if ((*((short *)camry_host_ptr((uint32_t)(iVar1 + -0x30b8)))) == 0x2222) {
        FUN_00054aac(iVar1 + -0x30bc, camry_host_addr(((undefined *)camry_host_ptr(0x2a2e4u))));
        (*((undefined2 *)camry_host_ptr((uint32_t)(iVar1 + -0x30b8)))) = 0x1111;
        (*((undefined2 *)camry_host_ptr((uint32_t)(iVar1 + -0x30ba)))) = 0;
      }
      else if ((*((short *)camry_host_ptr((uint32_t)(iVar1 + -0x30b8)))) != 0x1111) {
        iVar3 = 0;
        (*((undefined2 *)camry_host_ptr((uint32_t)(iVar1 + -0x30b8)))) = 0x4444;
      }
      uVar4 = uVar4 + 1;
    } while (uVar4 < 5);
    if (iVar3 == 0x5a) {
      *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe89dau)) + param_1 * 2) = 0x100;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe89c6u + (uint32_t)(param_1) * 1u)))) = 0;
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe89d2u + (uint32_t)(param_1) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe89d2u + (uint32_t)(param_1) * 1u)))) | 4;
  }
  return;
}

undefined4 FUN_0005578c(uint param_1)

{
  undefined4 uVar1;
  
  uVar1 = 0;
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2aacdu + (uint32_t)((param_1 & 0xff) * 4) * 1u)))) == 'Z') ||
     (((uint)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebe8a0cu + (uint32_t)((param_1 & 0xff) >> 5) * 4u)))) >> (param_1 & 0x1f) & 1) == 0)) {
    uVar1 = 0x5a;
  }
  return uVar1;
}

uint FUN_00055858(undefined2 param_1,int param_2,uint param_3)

{
  uint32_t puVar1;
  int iVar2;
  uint uVar3;
  
  puVar1 = 0xfebeb800u;
  uVar3 = 0;
  if ((DAT_febe86e6 != 0x1111) && (DAT_febe86e6 != 0x2222)) {
    puVar1 = 0xfebeb800u;
    uVar3 = FUN_00055836(param_1,param_2,((undefined *)camry_host_ptr(0xfebe86e4u)));
  }
  if (((*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x317a)))) != 0x1111) && ((*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x317a)))) != 0x2222)) {
    iVar2 = FUN_00055836(param_1, uVar3 + param_2, ((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x317c))));
    uVar3 = uVar3 + iVar2;
  }
  iVar2 = uVar3 - (param_3 & 0xffff);
  if (iVar2 < 0 == ((int)uVar3 < 0 && -1 < iVar2) && uVar3 != (param_3 & 0xffff)) {
    uVar3 = 0xffffffff;
  }
  return uVar3;
}

uint FUN_000558ae(short param_1,int param_2,uint param_3,ushort param_4)

{
  short *psVar1;
  undefined8 uVar2;
  int iVar3;
  uint uVar4;
  uint uVar5;
  
  uVar2 = 0xfebeb800;
  uVar5 = 0;
  iVar3 = 0;
  if ((param_4 & 0xff) < 4) {
    uVar4 = 0;
    do {
      psVar1 = ((short *)camry_host_ptr((uint32_t)(((short)(param_4 & 0xff) * 5 + uVar4) * 0x20 + (int)uVar2 + -0x30bc)));
      if (((psVar1[2] != 0x1111) && (psVar1[2] != 0x2222)) && (*psVar1 == param_1)) {
        if ((param_3 & 0xffff) < (uVar5 + 2 & 0xffff)) {
          iVar3 = 0x5a;
        }
        else {
          FUN_0006a574(((ushort)psVar1[1] + 4) % 5 + 1, ((undefined1 *)camry_host_ptr((uint32_t)(uVar5 + param_2))));
          uVar5 = uVar5 + 2 & 0xffff;
        }
      }
      uVar4 = uVar4 + 1;
    } while (uVar4 < 5);
    if (iVar3 != 0) {
      uVar5 = 0xffffffff;
    }
  }
  return uVar5;
}

undefined4 FUN_0005592c(short param_1,undefined4 param_2,undefined2 param_3)

{
  char cVar1;
  undefined4 uVar2;
  uint uVar3;
  
  uVar3 = 0;
  cVar1 = '\0';
  do {
    if (param_1 == *(short *)(((undefined *)camry_host_ptr(0x2ab70u)) + uVar3 * 8)) {
      cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2ab74u + (uint32_t)(uVar3 * 8) * 1u))));
      break;
    }
    uVar3 = uVar3 + 1 & 0xff;
  } while (uVar3 < 0x40);
  if (cVar1 == '\x11') {
    uVar2 = FUN_00055858((uint)(ushort)param_1, param_2, (uint)(ushort)param_3);
  }
  else {
    if (cVar1 == '\"') {
      uVar2 = 0;
    }
    else if (cVar1 == 'D') {
      uVar2 = 3;
    }
    else {
      if (cVar1 != 'U') {
        return 0xfffffffc;
      }
      uVar2 = 2;
    }
    uVar2 = FUN_000558ae(param_1,param_2,param_3,uVar2);
  }
  return uVar2;
}

void FUN_00056684(void)

{
  DAT_febe8a14 = 0;
  return;
}

void FUN_000566a2(void)

{
  DAT_febe8a18 = 0;
  DAT_febe8a19 = 0;
  return;
}

char FUN_000566ac(void)

{
  undefined1 uVar1;
  uint32_t puVar2;
  char cVar3;
  
  puVar2 = 0xfebeb800u;
  cVar3 = FUN_00058c90();
  if ((byte)(cVar3 - (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x2de7)))))) < 5) {
    uVar1 = 0;
  }
  else {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x2de7))))) = cVar3;
    uVar1 = 0x5a;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x2de8))))) = uVar1;
  return cVar3;
}

void FUN_000566d6(void)

{
  DAT_febe8a1c = 0;
  return;
}

void FUN_000566dc(void)

{
  DAT_febe8a1c = 0;
  if ((DAT_febe5f28 & 1) == 0) {
    DAT_febe8a1c = 0x5a;
  }
  return;
}

void FUN_000566f0(void)

{
  DAT_febe8a20 = 0;
  DAT_febe8a21 = 0;
  return;
}

char FUN_000566fa(void)

{
  bool bVar1;
  uint32_t puVar2;
  char cVar3;
  
  puVar2 = 0xfebeb800u;
  cVar3 = FUN_00058c8a();
  bVar1 = 3 < (byte)(cVar3 - (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x2ddf))))));
  if (bVar1) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x2ddf))))) = cVar3;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x2de0))))) = bVar1;
  return cVar3;
}

void FUN_00056722(void)

{
  DAT_febe8a24 = 0;
  DAT_febe8a25 = 0;
  return;
}

char FUN_0005672c(void)

{
  undefined1 uVar1;
  uint32_t puVar2;
  char cVar3;
  
  puVar2 = 0xfebeb800u;
  cVar3 = FUN_00058c90();
  if ((byte)(cVar3 - (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x2ddb)))))) < 5) {
    uVar1 = 0;
  }
  else {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x2ddb))))) = cVar3;
    uVar1 = 0x5a;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x2ddc))))) = uVar1;
  return cVar3;
}

void FUN_000567fe(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    *(undefined4 *)(((undefined *)camry_host_ptr(0xfebe8a2cu)) + iVar3 * 4) = 0;
    iVar1 = iVar3 + -4;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  return;
}

void FUN_00056814(uint param_1)

{
  undefined4 uVar1;
  
  if ((param_1 >> 2 & 1) == 0) {
    if ((param_1 >> 3 & 1) == 0) {
      if ((param_1 & 0x10) == 0) {
        DAT_febe3866 = 0;
        DAT_febe3873 = 0;
        if ((param_1 >> 5 & 1) == 0) {
          DAT_febe3872 = 0xff;
        }
        else {
          DAT_febe3872 = 0;
        }
        uVar1 = 0;
        goto LAB_00056854;
      }
      DAT_febe3873 = 0xff;
      goto LAB_0005683e;
    }
    DAT_febe3873 = 0xff;
    DAT_febe3872 = 0;
  }
  else {
    DAT_febe3873 = 0;
LAB_0005683e:
    DAT_febe3872 = 0xff;
  }
  DAT_febe3866 = 0xff;
  uVar1 = 2;
LAB_00056854:
  FUN_00056b78(0,uVar1);
  return;
}

void FUN_0005685e(uint param_1)

{
  undefined4 uVar1;
  
  if ((param_1 >> 0x12 & 1) == 0) {
    if ((param_1 >> 0x13 & 1) == 0) {
      if ((param_1 & 0x100000) == 0) {
        DAT_febe3865 = 0;
        DAT_febe3871 = 0;
        if ((param_1 >> 0x15 & 1) == 0) {
          DAT_febe3870 = 0xff;
        }
        else {
          DAT_febe3870 = 0;
        }
        uVar1 = 0;
        goto LAB_000568a2;
      }
      DAT_febe3871 = 0xff;
      goto LAB_0005688a;
    }
    DAT_febe3871 = 0xff;
    DAT_febe3870 = 0;
  }
  else {
    DAT_febe3871 = 0;
LAB_0005688a:
    DAT_febe3870 = 0xff;
  }
  DAT_febe3865 = 0xff;
  uVar1 = 0x20000;
LAB_000568a2:
  FUN_00056b78(1,uVar1);
  return;
}

void FUN_000568ac(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint32_t puVar4;
  uint uVar5;
  
  puVar4 = 0xfebeb800u;
  uVar5 = 0;
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    uVar5 = uVar5 | *(uint *)(((undefined *)camry_host_ptr(0xfebe8a2cu)) + iVar3 * 4);
    iVar1 = iVar3 + -4;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  FUN_00056814(uVar5);
  FUN_0005685e(uVar5);
  (*((uint *)camry_host_ptr((uint32_t)(puVar4 + -0x2dc0)))) = uVar5;
  return;
}

void FUN_000568dc(uint param_1,undefined4 param_2)

{
  if ((param_1 & 0xff) < 5) {
    *(undefined4 *)(((undefined *)camry_host_ptr(0xfebe8a2cu)) + (param_1 & 0xff) * 4) = param_2;
  }
  return;
}

void FUN_000568f2(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    *(undefined4 *)(((undefined *)camry_host_ptr(0xfebe8a48u)) + iVar3 * 4) = 0;
    iVar1 = iVar3 + -1;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  return;
}

void FUN_00056908(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  DAT_febe8a44 = 0;
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    DAT_febe8a44 = DAT_febe8a44 | *(uint *)(((undefined *)camry_host_ptr(0xfebe8a48u)) + iVar3 * 4);
    iVar1 = iVar3 + -1;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  if ((DAT_febe8a44 & 1) == 0) {
    DAT_febe3877 = 0;
  }
  else {
    DAT_febe3877 = 0xff;
  }
  if ((DAT_febe8a44 >> 1 & 1) == 0) {
    DAT_febe3876 = 0;
  }
  else {
    DAT_febe3876 = 0xff;
  }
  return;
}

void FUN_0005693e(uint param_1,undefined4 param_2)

{
  if ((param_1 & 0xff) < 2) {
    *(undefined4 *)(((undefined *)camry_host_ptr(0xfebe8a48u)) + (param_1 & 0xff) * 4) = param_2;
  }
  return;
}

void FUN_00056954(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    *(undefined4 *)(((undefined *)camry_host_ptr(0xfebe8a50u)) + iVar3 * 4) = 0;
    iVar1 = iVar3 + -4;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  return;
}

void FUN_0005696a(uint param_1)

{
  if ((param_1 >> 1 & 1) == 0) {
    DAT_febe386f = 0;
  }
  else {
    DAT_febe386f = 0xff;
  }
  if ((param_1 >> 0x11 & 1) == 0) {
    DAT_febe386e = 0;
  }
  else {
    DAT_febe386e = 0xff;
  }
  return;
}

void FUN_00056982(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint32_t puVar4;
  uint uVar5;
  
  puVar4 = 0xfebeb800u;
  uVar5 = 0;
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    uVar5 = uVar5 | *(uint *)(((undefined *)camry_host_ptr(0xfebe8a50u)) + iVar3 * 4);
    iVar1 = iVar3 + -4;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  FUN_0005696a(uVar5);
  (*((uint *)camry_host_ptr((uint32_t)(puVar4 + -0x2d9c)))) = uVar5;
  return;
}

void FUN_000569ac(uint param_1,undefined4 param_2)

{
  if ((param_1 & 0xff) < 5) {
    *(undefined4 *)(((undefined *)camry_host_ptr(0xfebe8a50u)) + (param_1 & 0xff) * 4) = param_2;
  }
  return;
}

void FUN_00056a48(void)

{
  if ((f33_channel_request_state.observed_mismatch & 2) == 0) {
    f33_channel_request_state.channel0_mismatch_calls = '\0';
    if (f33_channel_request_state.channel0_match_calls < DAT_000318f8) {
      f33_channel_request_state.channel0_match_calls =
           f33_channel_request_state.channel0_match_calls + '\x01';
      f33_channel_request_state.channel0_state = '\x03';
    }
    else {
      f33_channel_request_state.channel0_state = '\x02';
    }
  }
  else {
    f33_channel_request_state.channel0_match_calls = '\0';
    if (f33_channel_request_state.channel0_mismatch_calls < DAT_000318f9) {
      f33_channel_request_state.channel0_mismatch_calls =
           f33_channel_request_state.channel0_mismatch_calls + '\x01';
      f33_channel_request_state.channel0_state = '\x01';
    }
    else {
      f33_channel_request_state.channel0_state = '\0';
    }
  }
  return;
}

void FUN_00056b1c(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    *(undefined4 *)(((undefined *)camry_host_ptr(0xfebe8a88u)) + iVar3 * 4) = 0;
    iVar1 = iVar3 + -3;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  return;
}

void FUN_00056b32(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  DAT_febe8a98 = 0;
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    DAT_febe8a98 = DAT_febe8a98 | *(uint *)(((undefined *)camry_host_ptr(0xfebe8a88u)) + iVar3 * 4);
    iVar1 = iVar3 + -3;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  if (((DAT_febe8a98 >> 1 & 1) != 0) ||
     (DAT_febe3864 = (byte)DAT_febe71ec & 1, (DAT_febe71ec & 1) != 0)) {
    DAT_febe3864 = 0xff;
  }
  if (((DAT_febe8a98 >> 0x11 & 1) != 0) ||
     (DAT_febe3863 = (byte)DAT_febe71ec & 2, (DAT_febe71ec & 2) != 0)) {
    DAT_febe3863 = 0xff;
  }
  return;
}

void FUN_00056b78(uint param_1,undefined4 param_2)

{
  if ((param_1 & 0xff) < 4) {
    *(undefined4 *)(((undefined *)camry_host_ptr(0xfebe8a88u)) + (param_1 & 0xff) * 4) = param_2;
  }
  return;
}

void FUN_00056b8e(void)

{
  DAT_febe8a9c = 4;
  DAT_febe8aa0 = 0x40000;
  return;
}

void FUN_00056b9e(uint param_1)

{
  if ((param_1 >> 2 & 1) == 0) {
    if ((param_1 >> 1 & 1) == 0) {
      DAT_febe3882 = 0xff;
    }
    else {
      DAT_febe3882 = 0;
    }
    DAT_febe3883 = 0xff;
  }
  else {
    DAT_febe3882 = 0xff;
    DAT_febe3883 = 0;
  }
  return;
}

void FUN_00056bc0(uint param_1)

{
  if ((param_1 >> 0x12 & 1) == 0) {
    if ((param_1 >> 0x11 & 1) == 0) {
      DAT_febe3880 = 0xff;
    }
    else {
      DAT_febe3880 = 0;
    }
    DAT_febe3881 = 0xff;
  }
  else {
    DAT_febe3880 = 0xff;
    DAT_febe3881 = 0;
  }
  return;
}

void FUN_00056be2(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint32_t puVar4;
  uint uVar5;
  
  puVar4 = 0xfebeb800u;
  if ((f33_channel_request_state.observed_mismatch >> 1 & 1) == 0) {
    uVar5 = 0;
  }
  else {
    uVar5 = 4;
  }
  if ((f33_channel_request_state.observed_mismatch >> 0x11 & 1) != 0) {
    uVar5 = uVar5 | 0x40000;
  }
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    uVar5 = uVar5 | (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebe8a9cu + (uint32_t)(iVar3) * 4u))));
    iVar1 = iVar3 + -1;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  FUN_00056b9e(uVar5);
  FUN_00056bc0(uVar5);
  (*((uint *)camry_host_ptr((uint32_t)(puVar4 + -0x2d5c)))) = uVar5;
  return;
}

void FUN_00056c26(uint param_1,undefined4 param_2)

{
  if ((param_1 & 0xff) < 2) {
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebe8a9cu + (uint32_t)(param_1 & 0xff) * 4u)))) = param_2;
  }
  return;
}

void f33_fill_constant_block_56c3c(void)

{
  DAT_febe8aa8 = 0xc;
  DAT_febe8ab0 = 0;
  DAT_febe8aac = 0xc0000;
  DAT_febe8ab4 = 0;
  DAT_febe8ab8 = 0;
  DAT_febe8abc = 0;
  return;
}

void FUN_00056c54(uint param_1)

{
  if (DAT_000318fc != 'Z') {
    if (((param_1 >> 2 & 1) == 0) && ((param_1 & 2) != 0)) {
      DAT_febe3875 = 0xff;
    }
    else {
      DAT_febe3875 = 0;
    }
    if (((param_1 >> 0x12 & 1) == 0) && ((param_1 & 0x20000) != 0)) {
      DAT_febe3874 = 0xff;
    }
    else {
      DAT_febe3874 = 0;
    }
    if ((param_1 >> 3 & 1) == 0) {
      DAT_febe386d = 0;
    }
    else {
      DAT_febe386d = 0xff;
    }
    if ((param_1 >> 0x13 & 1) == 0) {
      DAT_febe386c = 0;
    }
    else {
      DAT_febe386c = 0xff;
    }
    return;
  }
  DAT_febe3875 = 0;
  DAT_febe3874 = 0;
  return;
}

void FUN_00056cb0(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint32_t puVar4;
  uint uVar5;
  
  puVar4 = 0xfebeb800u;
  uVar5 = 0;
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    uVar5 = uVar5 | (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebe8aa8u + (uint32_t)(iVar3) * 4u))));
    iVar1 = iVar3 + -5;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  FUN_00056c54(uVar5);
  (*((uint *)camry_host_ptr((uint32_t)(puVar4 + -0x2d40)))) = uVar5;
  return;
}

void FUN_00056cda(uint param_1,undefined4 param_2)

{
  if ((param_1 & 0xff) < 6) {
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebe8aa8u + (uint32_t)(param_1 & 0xff) * 4u)))) = param_2;
  }
  return;
}

void FUN_00056cf0(void)

{
  DAT_febe8ac4 = 0;
  return;
}

void FUN_00056d7a(void)

{
  DAT_febe8ad0 = 2;
  DAT_febe8ad4 = 0x20000;
  DAT_febe8ad8 = camry_host_addr(((undefined *)camry_host_ptr(0x20002u)));
  DAT_febe8adc = camry_host_addr(((undefined *)camry_host_ptr(0x20002u)));
  DAT_febe8ae0 = camry_host_addr(((undefined *)camry_host_ptr(0x20002u)));
  return;
}

void FUN_00056d92(uint param_1)

{
  if ((param_1 >> 1 & 1) == 0) {
    DAT_febe3885 = 0xff;
  }
  else {
    DAT_febe3885 = 0;
  }
  if ((param_1 >> 0x11 & 1) == 0) {
    DAT_febe3884 = 0xff;
  }
  else {
    DAT_febe3884 = 0;
  }
  return;
}

void FUN_00056daa(void)

{
  if ((DAT_febe8ae4 & 2) == 0) {
    DAT_febe8aca = 0;
    if (DAT_febe8ac9 < DAT_00031900) {
      DAT_febe8ac9 = DAT_febe8ac9 + 1;
      DAT_febe8ac8 = 3;
    }
    else {
      DAT_febe8ac8 = 2;
    }
  }
  else {
    DAT_febe8ac9 = 0;
    if (DAT_febe8aca < DAT_00031901) {
      DAT_febe8aca = DAT_febe8aca + 1;
      DAT_febe8ac8 = 1;
    }
    else {
      DAT_febe8ac8 = 0;
    }
  }
  return;
}

void FUN_00056dee(void)

{
  if ((DAT_febe8ae4 & 0x20000) == 0) {
    DAT_febe8acd = 0;
    if (DAT_febe8acc < DAT_00031900) {
      DAT_febe8acc = DAT_febe8acc + 1;
      DAT_febe8acb = 3;
    }
    else {
      DAT_febe8acb = 2;
    }
  }
  else {
    DAT_febe8acc = 0;
    if (DAT_febe8acd < DAT_00031901) {
      DAT_febe8acd = DAT_febe8acd + 1;
      DAT_febe8acb = 1;
    }
    else {
      DAT_febe8acb = 0;
    }
  }
  return;
}

void FUN_00056e34(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint32_t puVar4;
  uint uVar5;
  
  puVar4 = 0xfebeb800u;
  uVar5 = 0;
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    uVar5 = uVar5 | (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebe8ad0u + (uint32_t)(iVar3) * 4u))));
    iVar1 = iVar3 + -4;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  FUN_00056d92(uVar5);
  (*((uint *)camry_host_ptr((uint32_t)(puVar4 + -0x2d1c)))) = uVar5;
  FUN_00056daa();
  FUN_00056dee();
  return;
}

void FUN_00056e66(uint param_1,undefined4 param_2)

{
  if ((param_1 & 0xff) < 5) {
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebe8ad0u + (uint32_t)(param_1 & 0xff) * 4u)))) = param_2;
  }
  return;
}

void FUN_00056e7c(void)

{
  DAT_febe8ae8 = 4;
  DAT_febe8aec = 0x40000;
  return;
}

void FUN_00056e8c(uint param_1)

{
  if ((param_1 >> 2 & 1) == 0) {
    if ((param_1 >> 1 & 1) == 0) {
      DAT_febe387e = 0xff;
    }
    else {
      DAT_febe387e = 0;
    }
    DAT_febe387f = 0xff;
  }
  else {
    DAT_febe387e = 0xff;
    DAT_febe387f = 0;
  }
  return;
}

void FUN_00056eae(uint param_1)

{
  if ((param_1 >> 0x12 & 1) == 0) {
    if ((param_1 >> 0x11 & 1) == 0) {
      DAT_febe387c = 0xff;
    }
    else {
      DAT_febe387c = 0;
    }
    DAT_febe387d = 0xff;
  }
  else {
    DAT_febe387c = 0xff;
    DAT_febe387d = 0;
  }
  return;
}

void FUN_00056ed0(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint32_t puVar4;
  uint uVar5;
  
  puVar4 = 0xfebeb800u;
  if ((DAT_febe8ae4 >> 1 & 1) == 0) {
    uVar5 = 0;
  }
  else {
    uVar5 = 4;
  }
  if ((DAT_febe8ae4 >> 0x11 & 1) != 0) {
    uVar5 = uVar5 | 0x40000;
  }
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    uVar5 = uVar5 | (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebe8ae8u + (uint32_t)(iVar3) * 4u))));
    iVar1 = iVar3 + -1;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  FUN_00056e8c(uVar5);
  FUN_00056eae(uVar5);
  (*((uint *)camry_host_ptr((uint32_t)(puVar4 + -0x2d10)))) = uVar5;
  return;
}

void FUN_00056f14(uint param_1,undefined4 param_2)

{
  if ((param_1 & 0xff) < 2) {
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebe8ae8u + (uint32_t)(param_1 & 0xff) * 4u)))) = param_2;
  }
  return;
}

void FUN_00056fbc(void)

{
  DAT_febe8afc = 0;
  return;
}

void FUN_00056fc2(void)

{
  DAT_febe8b00 = 0;
  return;
}

void FUN_00056fc8(void)

{
  DAT_febe8b00 = 0;
  return;
}

void FUN_0005704e(void)

{
  DAT_febe8b04 = 0;
  return;
}

void FUN_000570aa(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  DAT_febe8b17 = 0x5a;
  iVar3 = 0;
  DAT_febe8b10 = DAT_febe8b17;
  do {
    iVar2 = iVar3 + 1;
    DAT_febe8b10 = DAT_febe8b10 & (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe8b11u + (uint32_t)(iVar3) * 1u))));
    iVar1 = iVar3 + -2;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    DAT_febe8b17 = DAT_febe8b17 & (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe8b14u + (uint32_t)(iVar3) * 1u))));
    iVar1 = iVar3 + -2;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  if (DAT_febe8b10 == 0x5a) {
    DAT_febe3887 = 0xff;
  }
  else {
    DAT_febe3887 = 0;
  }
  if (DAT_febe8b17 == 0x5a) {
    DAT_febe3886 = 0xff;
  }
  else {
    DAT_febe3886 = 0;
  }
  return;
}

void FUN_000570f4(uint param_1,undefined1 param_2)

{
  if ((param_1 & 0xff) < 3) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe8b11u + (uint32_t)(param_1 & 0xff) * 1u)))) = param_2;
  }
  return;
}

void FUN_00057106(uint param_1,undefined1 param_2)

{
  if ((param_1 & 0xff) < 3) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe8b14u + (uint32_t)(param_1 & 0xff) * 1u)))) = param_2;
  }
  return;
}

void FUN_0005711a(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    *(undefined4 *)(((undefined *)camry_host_ptr(0xfebe8b1cu)) + iVar3 * 4) = 0;
    iVar1 = iVar3 + -1;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  return;
}

void FUN_00057130(void)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  int iVar4;
  
  uVar3 = 0;
  iVar4 = 0;
  do {
    iVar2 = iVar4 + 1;
    uVar3 = uVar3 | *(uint *)(((undefined *)camry_host_ptr(0xfebe8b1cu)) + iVar4 * 4);
    iVar1 = iVar4 + -1;
    iVar4 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  if (((uVar3 >> 0x10 & 1) == 0) &&
     ((((uVar3 & 1) == 0 || ((f33_channel_request_state.observed_mismatch & 2) == 0)) ||
      ((DAT_febe8ae4 & 2) == 0)))) {
    DAT_febe8b18 = 0;
    DAT_febe387b = 0;
  }
  else {
    DAT_febe8b18 = 1;
    DAT_febe387b = 0xff;
  }
  if (((uVar3 & 0x20000) == 0) &&
     ((((uVar3 >> 1 & 1) == 0 || ((f33_channel_request_state.observed_mismatch >> 0x11 & 1) == 0))
      || ((DAT_febe8ae4 >> 0x11 & 1) == 0)))) {
    DAT_febe387a = 0;
  }
  else {
    DAT_febe8b18 = DAT_febe8b18 | 2;
    DAT_febe387a = 0xff;
  }
  return;
}

void FUN_0005719c(uint param_1,undefined4 param_2)

{
  if ((param_1 & 0xff) < 2) {
    *(undefined4 *)(((undefined *)camry_host_ptr(0xfebe8b1cu)) + (param_1 & 0xff) * 4) = param_2;
  }
  return;
}

void f33_set_output_request_word(uchar owner,uint request)

{
  if (owner < 8) {
    f33_output_request_words[owner] = request;
  }
  return;
}

void f33_initialize_direct_output_requests(void)

{
  f33_direct_output_request_enables[1] = '\0';
  f33_direct_output_request_enables[0] = '\0';
  f33_direct_output_codes_bank1[2] = 0x4000;
  f33_direct_output_codes_bank1[1] = 0x4000;
  f33_direct_output_codes_bank1[0] = 0x4000;
  f33_direct_output_codes_bank0[2] = 0x4000;
  f33_direct_output_codes_bank0[1] = 0x4000;
  f33_direct_output_codes_bank0[0] = 0x4000;
  return;
}

void f33_clear_direct_output_enables(void)

{
  f33_direct_output_request_enables[0] = '\0';
  f33_direct_output_request_enables[1] = '\0';
  return;
}

void f33_clear_direct_output_bank0(void)

{
  f33_direct_output_request_enables[0] = '\0';
  return;
}

void f33_request_direct_output_bank0(void)

{
  f33_direct_output_request_enables[0] = 'Z';
  return;
}

void f33_fill_constant_block_5745a(void)

{
  DAT_febe8b5c = 0;
  DAT_febe8b5d = 0;
  DAT_febe8b5e = 0;
  DAT_febe8b5f = 0;
  DAT_febe8b6c = 0x4000;
  DAT_febe8b6e = 0x4000;
  DAT_febe8b70 = 0x4000;
  DAT_febe8b72 = 0x4000;
  DAT_febe8b74 = 0x4000;
  DAT_febe8b76 = 0x4000;
  DAT_febe8b78 = 0x4000;
  DAT_febe8b7a = 0x4000;
  DAT_febe8b7c = 0x4000;
  DAT_febe8b7e = 0x4000;
  DAT_febe8b80 = 0x4000;
  DAT_febe8b82 = 0x4000;
  return;
}

void FUN_000575ac(void)

{
  DAT_febe8b84 = 0x7fff;
  DAT_febe8b86 = 0x7fff;
  return;
}

void f33_initialize_output_code_limit_requests(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = 0;
  do {
    *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe8b8au)) + iVar3 * 2) = 0x8000;
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -2;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe8b94u)) + iVar3 * 2) = 0x8000;
    iVar1 = iVar3 + -2;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  DAT_febe8b90 = 0x8000;
  DAT_febe8b9a = 0x8000;
  DAT_febe8b84 = 0x7fff;
  DAT_febe8b86 = 0x7fff;
  return;
}

void f33_set_output_code_limit_bank0(uchar owner,ushort limit)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  int iVar4;
  
  if (owner < 3) {
    iVar4 = (uint)owner * 2;
    if (*(ushort *)(((undefined *)camry_host_ptr(0xfebe8b8au)) + iVar4) == limit) {
      if (DAT_febe8b90 <= limit) {
        return;
      }
      uVar3 = 0x8000;
      iVar4 = 0;
      do {
        if ((int)(*(ushort *)(((undefined *)camry_host_ptr(0xfebe8b8au)) + iVar4 * 2) - uVar3) < 0) {
          uVar3 = (uint)*(ushort *)(((undefined *)camry_host_ptr(0xfebe8b8au)) + iVar4 * 2);
        }
        iVar2 = iVar4 + 1;
        iVar1 = iVar4 + -2;
        iVar4 = iVar2;
      } while (((iVar1 < 0) || (iVar2 < 0)));
      DAT_febe8b90 = (ushort)uVar3;
    }
    else {
      *(ushort *)(((undefined *)camry_host_ptr(0xfebe8b8au)) + iVar4) = limit;
      uVar3 = 0x8000;
      iVar4 = 0;
      do {
        if ((int)(*(ushort *)(((undefined *)camry_host_ptr(0xfebe8b8au)) + iVar4 * 2) - uVar3) < 0) {
          uVar3 = (uint)*(ushort *)(((undefined *)camry_host_ptr(0xfebe8b8au)) + iVar4 * 2);
        }
        iVar2 = iVar4 + 1;
        iVar1 = iVar4 + -2;
        iVar4 = iVar2;
      } while (((iVar1 < 0) || (iVar2 < 0)));
      DAT_febe8b90 = (ushort)uVar3;
    }
    DAT_febe8b84 = ~(ushort)uVar3;
  }
  return;
}

void f33_set_output_code_limit_bank1(uchar owner,ushort limit)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  int iVar4;
  
  if (owner < 3) {
    iVar4 = (uint)owner * 2;
    if (*(ushort *)(((undefined *)camry_host_ptr(0xfebe8b94u)) + iVar4) == limit) {
      if (DAT_febe8b9a <= limit) {
        return;
      }
      uVar3 = 0x8000;
      iVar4 = 0;
      do {
        if ((int)(*(ushort *)(((undefined *)camry_host_ptr(0xfebe8b94u)) + iVar4 * 2) - uVar3) < 0) {
          uVar3 = (uint)*(ushort *)(((undefined *)camry_host_ptr(0xfebe8b94u)) + iVar4 * 2);
        }
        iVar2 = iVar4 + 1;
        iVar1 = iVar4 + -2;
        iVar4 = iVar2;
      } while (((iVar1 < 0) || (iVar2 < 0)));
      DAT_febe8b9a = (ushort)uVar3;
    }
    else {
      *(ushort *)(((undefined *)camry_host_ptr(0xfebe8b94u)) + iVar4) = limit;
      uVar3 = 0x8000;
      iVar4 = 0;
      do {
        if ((int)(*(ushort *)(((undefined *)camry_host_ptr(0xfebe8b94u)) + iVar4 * 2) - uVar3) < 0) {
          uVar3 = (uint)*(ushort *)(((undefined *)camry_host_ptr(0xfebe8b94u)) + iVar4 * 2);
        }
        iVar2 = iVar4 + 1;
        iVar1 = iVar4 + -2;
        iVar4 = iVar2;
      } while (((iVar1 < 0) || (iVar2 < 0)));
      DAT_febe8b9a = (ushort)uVar3;
    }
    DAT_febe8b86 = ~(ushort)uVar3;
  }
  return;
}

void f33_release_output_code_limit_bank0(uchar owner)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  
  if (owner < 3) {
    iVar3 = (uint)owner * 2;
    uVar4 = 0x8000;
    if (*(short *)(((undefined *)camry_host_ptr(0xfebe8b8au)) + iVar3) == -0x8000) {
      if (DAT_febe8b90 < 0x8001) {
        return;
      }
      iVar3 = 0;
      do {
        if ((int)(*(ushort *)(((undefined *)camry_host_ptr(0xfebe8b8au)) + iVar3 * 2) - uVar4) < 0) {
          uVar4 = (uint)*(ushort *)(((undefined *)camry_host_ptr(0xfebe8b8au)) + iVar3 * 2);
        }
        iVar2 = iVar3 + 1;
        iVar1 = iVar3 + -2;
        iVar3 = iVar2;
      } while (((iVar1 < 0) || (iVar2 < 0)));
      DAT_febe8b90 = (ushort)uVar4;
    }
    else {
      *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe8b8au)) + iVar3) = 0x8000;
      uVar4 = 0x8000;
      iVar3 = 0;
      do {
        if ((int)(*(ushort *)(((undefined *)camry_host_ptr(0xfebe8b8au)) + iVar3 * 2) - uVar4) < 0) {
          uVar4 = (uint)*(ushort *)(((undefined *)camry_host_ptr(0xfebe8b8au)) + iVar3 * 2);
        }
        iVar2 = iVar3 + 1;
        iVar1 = iVar3 + -2;
        iVar3 = iVar2;
      } while (((iVar1 < 0) || (iVar2 < 0)));
      DAT_febe8b90 = (ushort)uVar4;
    }
    DAT_febe8b84 = ~(ushort)uVar4;
  }
  return;
}

void f33_release_output_code_limit_bank1(uchar owner)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  
  if (owner < 3) {
    iVar3 = (uint)owner * 2;
    uVar4 = 0x8000;
    if (*(short *)(((undefined *)camry_host_ptr(0xfebe8b94u)) + iVar3) == -0x8000) {
      if (DAT_febe8b9a < 0x8001) {
        return;
      }
      iVar3 = 0;
      do {
        if ((int)(*(ushort *)(((undefined *)camry_host_ptr(0xfebe8b94u)) + iVar3 * 2) - uVar4) < 0) {
          uVar4 = (uint)*(ushort *)(((undefined *)camry_host_ptr(0xfebe8b94u)) + iVar3 * 2);
        }
        iVar2 = iVar3 + 1;
        iVar1 = iVar3 + -2;
        iVar3 = iVar2;
      } while (((iVar1 < 0) || (iVar2 < 0)));
      DAT_febe8b9a = (ushort)uVar4;
    }
    else {
      *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe8b94u)) + iVar3) = 0x8000;
      uVar4 = 0x8000;
      iVar3 = 0;
      do {
        if ((int)(*(ushort *)(((undefined *)camry_host_ptr(0xfebe8b94u)) + iVar3 * 2) - uVar4) < 0) {
          uVar4 = (uint)*(ushort *)(((undefined *)camry_host_ptr(0xfebe8b94u)) + iVar3 * 2);
        }
        iVar2 = iVar3 + 1;
        iVar1 = iVar3 + -2;
        iVar3 = iVar2;
      } while (((iVar1 < 0) || (iVar2 < 0)));
      DAT_febe8b9a = (ushort)uVar4;
    }
    DAT_febe8b86 = ~(ushort)uVar4;
  }
  return;
}

void FUN_000579e8(void)

{
  DAT_febe8ba0 = 0xff;
  DAT_febe8ba1 = 0xff;
  return;
}

void f33_initialize_phase_output_slots(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  DAT_febe8ba7 = 0;
  iVar3 = 0;
  do {
    f33_output_slot_enables_bank0[iVar3] = '\0';
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -4;
    f33_output_slot_codes_bank0[iVar3 * 3] = 0x4000;
    f33_output_slot_codes_bank0[iVar3 * 3 + 1] = 0x4000;
    f33_output_slot_codes_bank0[iVar3 * 3 + 2] = 0x4000;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  DAT_febe8bad = 0;
  iVar3 = 0;
  do {
    f33_output_slot_enables_bank1[iVar3] = '\0';
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -4;
    f33_output_slot_codes_bank1[iVar3 * 3] = 0x4000;
    f33_output_slot_codes_bank1[iVar3 * 3 + 1] = 0x4000;
    f33_output_slot_codes_bank1[iVar3 * 3 + 2] = 0x4000;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  DAT_febe8baf = 0;
  DAT_febe8bae = 0;
  DAT_febe8ba1 = 0xff;
  f33_output_slot_enables_bank1[0] = 'Z';
  DAT_febe8ba0 = 0xff;
  f33_output_slot_enables_bank0[0] = 'Z';
  return;
}

void f33_activate_phase_output_slot_pair(uchar slot)

{
  uint uVar1;
  uchar uVar2;
  
  uVar1 = (uint)slot;
  if (uVar1 < 5) {
    uVar2 = f33_output_slot_enables_bank0[uVar1];
    if (uVar2 != 'Z') {
      uVar2 = 'Z';
      f33_output_slot_enables_bank0[uVar1] = 'Z';
      DAT_febe8ba7 = 0x5a;
    }
    if (f33_output_slot_enables_bank1[uVar1] != 'Z') {
      f33_output_slot_enables_bank1[uVar1] = uVar2;
      DAT_febe8bad = uVar2;
    }
  }
  return;
}

void f33_release_phase_output_slot_pair(uchar slot)

{
  uint uVar1;
  
  uVar1 = (uint)slot;
  if (uVar1 < 5) {
    if (f33_output_slot_enables_bank0[uVar1] != '\0') {
      f33_output_slot_enables_bank0[uVar1] = '\0';
      DAT_febe8ba7 = 0x5a;
    }
    if (f33_output_slot_enables_bank1[uVar1] != '\0') {
      f33_output_slot_enables_bank1[uVar1] = '\0';
      DAT_febe8bad = 0x5a;
    }
  }
  return;
}

void f33_activate_phase_output_slot_bank0(uchar slot)

{
  if ((slot < 5) && (f33_output_slot_enables_bank0[slot] != 'Z')) {
    f33_output_slot_enables_bank0[slot] = 'Z';
    DAT_febe8ba7 = 0x5a;
  }
  return;
}

void f33_release_phase_output_slot_bank0(uchar slot)

{
  if ((slot < 5) && (f33_output_slot_enables_bank0[slot] != '\0')) {
    f33_output_slot_enables_bank0[slot] = '\0';
    DAT_febe8ba7 = 0x5a;
  }
  return;
}

void f33_activate_phase_output_slot_bank1(uchar slot)

{
  uint uVar1;
  
  uVar1 = (uint)slot;
  if ((uVar1 < 5) && (f33_output_slot_enables_bank1[uVar1] != 'Z')) {
    f33_output_slot_enables_bank1[uVar1] = 'Z';
    DAT_febe8bad = 0x5a;
  }
  return;
}

void f33_release_phase_output_slot_bank1(uchar slot)

{
  uint uVar1;
  
  uVar1 = (uint)slot;
  if ((uVar1 < 5) && (f33_output_slot_enables_bank1[uVar1] != '\0')) {
    f33_output_slot_enables_bank1[uVar1] = '\0';
    DAT_febe8bad = 0x5a;
  }
  return;
}

void FUN_00057e16(void)

{
  DAT_febe8bfa = 1;
  DAT_febe8bfb = 2;
  DAT_febe8bfc = 0;
  return;
}

void FUN_00057eb4(void)

{
  DAT_febe5f48 = 1;
  return;
}

void FUN_00057ebc(void)

{
  if (((DAT_00030d74 < DAT_febe7da6) || (DAT_febe7da6 < DAT_00030d76)) &&
     ((DAT_00030d74 < DAT_febe7da8 || (DAT_febe7da8 < DAT_00030d76)))) {
    DAT_febe5f48 = true;
    if (DAT_febe7db0 <= DAT_00030d70) {
      DAT_febe5f48 = DAT_febe7db0 < DAT_00030d72;
    }
  }
  else {
    DAT_febe5f48 = false;
  }
  return;
}

void f33_fill_constant_block_5802e(void)

{
  DAT_febeed01 = 0;
  DAT_febeed02 = 0;
  DAT_febeed03 = 0;
  DAT_febeed04 = DAT_febe7e0c;
  DAT_febeed06 = DAT_febe81e6;
  DAT_febeed08 = DAT_febe81e8;
  DAT_febeed0a = DAT_febe81ea;
  DAT_febeed0c = DAT_febe81ec;
  DAT_febeed0e = DAT_febe81ee;
  DAT_febeed10 = DAT_febe81f0;
  DAT_febeed00 = DAT_febe8a1c;
  DAT_febeed12 = DAT_febe7df8;
  return;
}

undefined1 FUN_00058c84(void)

{
  return DAT_febe8c19;
}

undefined1 FUN_00058c8a(void)

{
  return DAT_febe8c16;
}

undefined1 FUN_00058c90(void)

{
  return DAT_febe8c18;
}

void FUN_0005fa3a(void)

{
  int iVar1;
  uint uVar2;
  
  uVar2 = 0;
  DAT_feef90e0 = 0;
  do {
    iVar1 = uVar2 * 4;
    uVar2 = uVar2 + 1;
    *(undefined4 *)(((undefined *)camry_host_ptr(0xfeef80a0u)) + iVar1) = 0;
  } while (uVar2 < 0x50);
  uVar2 = 0;
  DAT_feef90e4 = 0;
  do {
    iVar1 = uVar2 * 4;
    uVar2 = uVar2 + 1;
    (*((undefined4 *)camry_host_ptr((uint32_t)((0xfeef81e0u) + iVar1)))) = 0;
  } while (uVar2 < 0x1b0);
  DAT_feef90e8 = 0;
  return;
}

void FUN_0005fa84(void)

{
  int iVar1;
  uint uVar2;
  
  uVar2 = 0;
  DAT_feef90ec = 0;
  do {
    iVar1 = uVar2 * 4;
    uVar2 = uVar2 + 1;
    *(undefined4 *)(((undefined *)camry_host_ptr(0xfeef88a0u)) + iVar1) = 0;
  } while (uVar2 < 0x60);
  uVar2 = 0;
  DAT_feef90f0 = 0;
  do {
    iVar1 = uVar2 * 4;
    uVar2 = uVar2 + 1;
    (*((undefined4 *)camry_host_ptr((uint32_t)((0xfeef8a20u) + iVar1)))) = 0;
  } while (uVar2 < 0x1b0);
  DAT_feef90f4 = 0;
  return;
}

void FUN_0005face(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  FUN_0005fa3a();
  FUN_0005fa84();
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x7ff6))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x7ff5))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x7ffa))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x7ff9))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x7ff8))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x7ff7))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x7ffc))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x7ffb))))) = 0;
  return;
}

int FUN_00060630(uint param_1)

{
  uint uVar1;
  
  if (0x4f < (param_1 & 0xffff)) {
    return 0;
  }
  uVar1 = *(uint *)(((undefined *)camry_host_ptr(0xfeef80a0u)) + (param_1 & 0xffff) * 4);
  *(uint *)(((undefined *)camry_host_ptr(0xfeef80a0u)) + (param_1 & 0xffff) * 4) = uVar1 & 0xffff0000;
  return (uVar1 & 0x7ff8) << 1;
}

uint f33_consume_acquisition_group0_entry(ushort index)

{
  uint uVar1;
  
  if (0x1af < index) {
    return 0;
  }
  uVar1 = (*((uint *)camry_host_ptr((uint32_t)((0xfeef81e0u) + (uint)index * 4))));
  (*((uint *)camry_host_ptr((uint32_t)((0xfeef81e0u) + (uint)index * 4)))) = uVar1 & 0xffff0000;
  return (uVar1 & 0x7ff8) << 1;
}

int FUN_000606da(uint param_1)

{
  uint uVar1;
  
  if (0x5f < (param_1 & 0xffff)) {
    return 0;
  }
  uVar1 = *(uint *)(((undefined *)camry_host_ptr(0xfeef88a0u)) + (param_1 & 0xffff) * 4);
  *(uint *)(((undefined *)camry_host_ptr(0xfeef88a0u)) + (param_1 & 0xffff) * 4) = uVar1 & 0xffff0000;
  return (uVar1 & 0x7ff8) << 1;
}

uint f33_consume_acquisition_group8_entry(ushort index)

{
  uint uVar1;
  
  if (0x1af < index) {
    return 0;
  }
  uVar1 = (*((uint *)camry_host_ptr((uint32_t)((0xfeef8a20u) + (uint)index * 4))));
  (*((uint *)camry_host_ptr((uint32_t)((0xfeef8a20u) + (uint)index * 4)))) = uVar1 & 0xffff0000;
  return (uVar1 & 0x7ff8) << 1;
}

void FUN_00060aa8(void)

{
  uint uVar1;
  uint uVar2;
  int iVar3;
  
  uVar2 = 0;
  do {
    uVar1 = 0;
    do {
      iVar3 = (short)((short)uVar1 + (short)(uVar2 << 1)) * 0x18;
      uVar1 = uVar1 + 1;
      *(undefined4 *)(((undefined *)camry_host_ptr(0xfeef90f8u)) + iVar3) = 0;
      *(undefined4 *)(((undefined *)camry_host_ptr(0xfeef90fcu)) + iVar3) = 0;
      *(undefined4 *)(((undefined *)camry_host_ptr(0xfeef9100u)) + iVar3) = 0;
      *(undefined4 *)(((undefined *)camry_host_ptr(0xfeef9104u)) + iVar3) = 0;
      *(undefined4 *)(((undefined *)camry_host_ptr(0xfeef9108u)) + iVar3) = 0;
      *(undefined4 *)(((undefined *)camry_host_ptr(0xfeef910cu)) + iVar3) = 0x800800;
    } while (uVar1 < 2);
    uVar2 = uVar2 + 1;
  } while (uVar2 < 2);
  return;
}

void FUN_00060d52(uint param_1)

{
  uint uVar1;
  
  param_1 = param_1 & 0xff;
  if (param_1 < 2) {
    for (uVar1 = 0; uVar1 < (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x31411u + (uint32_t)((short)param_1 * 0x50) * 1u)))); uVar1 = uVar1 + 1 & 0xff)
    {
      (*((undefined2 *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x313fcu + (uint32_t)(param_1) * 4u)))) + uVar1 * 2)))) = 0;
    }
  }
  return;
}

byte FUN_000614b0(void)

{
  return (DAT_febe383e >> 0xd & 1) != 0 | ((DAT_febe383e >> 0xe & 1) != 0) << 1 |
         ((short)DAT_febe383e < 0) << 2;
}

void FUN_0006165a(void)

{
  DAT_febe3847 = 0;
  DAT_febe3848 = 0;
  return;
}

void f33_stage_configured_phase_mask(uint bank,uint mask)

{
  ushort uVar1;
  int iVar2;
  
  iVar2 = (short)bank * 0x1c;
  uVar1 = 0;
  if ((mask & 1) == 0) {
    uVar1 = *(ushort *)(((undefined *)camry_host_ptr(0x315dcu)) + iVar2);
  }
  if ((mask >> 3 & 1) == 0) {
    uVar1 = uVar1 | *(ushort *)(((undefined *)camry_host_ptr(0x315deu)) + iVar2);
  }
  if ((mask >> 1 & 1) == 0) {
    uVar1 = uVar1 | *(ushort *)(((undefined *)camry_host_ptr(0x315e0u)) + iVar2);
  }
  if ((mask >> 4 & 1) == 0) {
    uVar1 = uVar1 | *(ushort *)(((undefined *)camry_host_ptr(0x315e2u)) + iVar2);
  }
  if ((mask >> 2 & 1) == 0) {
    uVar1 = uVar1 | *(ushort *)(((undefined *)camry_host_ptr(0x315e4u)) + iVar2);
  }
  if ((mask >> 5 & 1) == 0) {
    uVar1 = uVar1 | *(ushort *)(((undefined *)camry_host_ptr(0x315e6u)) + iVar2);
  }
  f33_pwm_halfword_stages[bank].port_mask = uVar1;
  return;
}

ushort f33_select_acquisition_six_entry_base(ushort count,ushort capacity)

{
  ushort uVar1;
  
  if ((count & 1) == 0) {
    if (count < 6) {
      uVar1 = (capacity + count) - 6;
    }
    else {
      uVar1 = count - 6;
    }
  }
  else {
    uVar1 = count - 3;
  }
  return uVar1;
}

void f33_accumulate_serial_acquisition_masks(uchar channel,ushort first_mask,ushort second_mask)

{
  int iVar1;
  
  if (channel < 2) {
    iVar1 = ((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe392eu + (uint32_t)((short)(ushort)channel * 0x5a) * 1u)))) & 3) * 2 +
            (short)(ushort)channel * 0x5a;
    *(ushort *)(((undefined *)camry_host_ptr(0xfebe3900u)) + iVar1 + 0x30) =
         *(ushort *)(((undefined *)camry_host_ptr(0xfebe3900u)) + iVar1 + 0x30) | first_mask;
    *(ushort *)(((undefined *)camry_host_ptr(0xfebe3900u)) + iVar1 + 0x38) =
         *(ushort *)(((undefined *)camry_host_ptr(0xfebe3900u)) + iVar1 + 0x38) | second_mask;
  }
  return;
}

void FUN_000626d6(ushort param_1,char param_2)

{
  bool bVar1;
  undefined2 *puVar2;
  int iVar3;
  
  if ((param_1 & 0xff) < 2) {
    iVar3 = (short)(param_1 & 0xff) * 0x5a;
    puVar2 = (undefined2 *)(((undefined *)camry_host_ptr(0xfebe3900u)) + iVar3);
    bVar1 = param_2 != '\0';
    puVar2[(short)(ushort)bVar1 * 5 + 0x23] = *puVar2;
    puVar2[(short)(ushort)bVar1 * 5 + 0x24] = *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe3902u)) + iVar3);
    puVar2[(short)(ushort)bVar1 * 5 + 0x25] = *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe3904u)) + iVar3);
    puVar2[(short)(ushort)bVar1 * 5 + 0x26] = *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe3906u)) + iVar3);
    puVar2[(short)(ushort)bVar1 * 5 + 0x27] = *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe3908u)) + iVar3);
  }
  return;
}

undefined1 FUN_00062e18(void)

{
  return DAT_febf066c;
}

void f33_initialize_task_progress_supervision(void)

{
  undefined1 *puVar1;
  int iVar2;
  uint uVar3;
  uint32_t puVar4;
  puVar4 = 0xfebeb800u;
  f33_reset_task_rate_window(f33_task_rate_windows);
  f33_reset_task_rate_window(((F33TaskRateWindow *)camry_host_ptr((uint32_t)(puVar4 + -0x2a4c))));
  f33_reset_task_rate_window(((F33TaskRateWindow *)camry_host_ptr((uint32_t)(puVar4 + -0x2a48))));
  f33_reset_task_rate_window(((F33TaskRateWindow *)camry_host_ptr((uint32_t)(puVar4 + -0x2a44))));
  uVar3 = 0;
  do {
    iVar2 = uVar3 * 8;
    uVar3 = uVar3 + 1;
    puVar1 = ((undefined *)camry_host_ptr((uint32_t)(puVar4 + iVar2 + -0x2a40)));
    *puVar1 = 0;
    *(undefined2 *)(puVar1 + 2) = 0;
    *(undefined2 *)(puVar1 + 4) = 0;
    *(undefined2 *)(puVar1 + 6) = 0xffff;
  } while (uVar3 < 4);
  return;
}

void FUN_0006681e(void)

{
  DAT_febe5f28 = 0;
  return;
}

void f33_stage_output_bank0_phase_mask(uchar mask)

{
  f33_stage_configured_phase_mask(0,(uint)mask);
  return;
}

void f33_stage_output_bank1_phase_mask(uchar mask)

{
  f33_stage_configured_phase_mask(1,(uint)mask);
  return;
}

void FUN_00066ef4(void)

{
  f33_nvm_acquisition_phase = '3';
  FUN_00067346();
  FUN_00067a52();
  f33_nvm_arm_initial_read_acquisition();
  return;
}

undefined1 FUN_00066f10(void)

{
  undefined1 uVar1;
  
  uVar1 = 0;
  if (f33_nvm_acquisition_phase != '\0') {
    uVar1 = 0x5a;
  }
  return uVar1;
}

uint f33_platform_restart_selector_constant_zero(void)

{
  return 0;
}

void FUN_00067346(void)

{
  f33_nvm_family0_scan_cursor = 0;
  f33_nvm_family0_probe_offset = 0;
  return;
}

byte FUN_00067874(void)

{
  byte bVar1;
  
  bVar1 = DAT_febf067c == 'Z';
  if (f33_nvm_family0_classification_latch == 'Z') {
    bVar1 = bVar1 | 2;
  }
  DAT_febf067c = 0;
  f33_nvm_family0_classification_latch = '\0';
  return bVar1;
}

undefined4 FUN_00067984(void)

{
  uint uVar1;
  
  uVar1 = 0;
  while( true ) {
    if (f33_nvm_family0_object_count <= uVar1) {
      return 1;
    }
    if ((f33_nvm_family0_status[uVar1] & 0xf0) == 0x20) break;
    uVar1 = uVar1 + 1 & 0xffff;
  }
  return 0;
}

uint f33_nvm_get_family0_phase(void)

{
  return (uint)f33_nvm_family0_phase;
}

void FUN_00067a52(void)

{
  f33_nvm_family1_scan_cursor = 0;
  return;
}

uint f33_nvm_get_family1_phase(void)

{
  return (uint)f33_nvm_family1_phase;
}

void f33_nvm_arm_initial_read_acquisition(void)

{
  f33_nvm_initial_read_token = 'Z';
  return;
}

uchar FUN_00068924(void)

{
  return f33_nvm_family0_busy;
}

uint f33_nvm_get_family0_completion(ushort object)

{
  if ((uint)object < (uint)f33_nvm_family0_object_count) {
    return (uint)f33_nvm_family0_completion[object];
  }
  return 0xa5;
}

uchar FUN_00068a4a(void)

{
  return f33_nvm_family1_busy;
}

uint f33_nvm_handle_family0_write_result(uchar result,ushort logical_handle)

{
  byte bVar1;
  uint uVar2;
  uchar uVar3;
  
  bVar1 = f33_nvm_logical_application_routes[logical_handle].object;
  uVar2 = (uint)f33_nvm_family0_selected_logical_handles[bVar1];
  if ((uVar2 == 0xffff) ||
     (uVar2 = uVar2 + 1 & 0xffff,
     (((uint)f33_nvm_family0_ram_descriptors[bVar1].logical_count +
      (uint)f33_nvm_family0_ram_descriptors[bVar1].first_logical_handle) - 1 & 0xffff) < uVar2)) {
    uVar2 = (uint)f33_nvm_family0_ram_descriptors[bVar1].first_logical_handle;
  }
  if ((result == '\0') && (uVar2 == logical_handle)) {
    f33_nvm_family0_selected_logical_handles[bVar1] = (ushort)uVar2;
    uVar3 = 'Z';
  }
  else {
    uVar3 = 0xa5;
  }
  f33_nvm_family0_completion[bVar1] = uVar3;
  return 0x5a;
}

uchar FUN_00068f64(void)

{
  return f33_nvm_direct_operation_request;
}

undefined4 f33_return_const_0_68f6a(void)

{
  return 0;
}

undefined4 f33_return_const_0_68f6e(void)

{
  return 0;
}

void f33_crypto_bank_clear_fragment_history(void)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  
  uVar2 = 0;
  do {
    uVar3 = 0;
    do {
      iVar1 = uVar3 + uVar2 * 8;
      uVar3 = uVar3 + 1;
      f33_crypto_key_fragment_previous[iVar1] = '\0';
      f33_crypto_key_fragment_qualified[iVar1] = '\0';
    } while (uVar3 < 8);
    f33_crypto_key_fragment_repeat_count[uVar2] = '\0';
    uVar3 = uVar2 + 1;
    f33_crypto_key_fragment_previous_generation[uVar2] = '\0';
    f33_crypto_key_fragment_seen[uVar2] = '\0';
    uVar2 = uVar3;
  } while (uVar3 < 8);
  f33_crypto_key_fragment_qualified_mask = '\0';
  return;
}

void f33_crypto_bank_clear_key_material(uchar slot)

{
  uint uVar1;
  uint uVar2;
  
  if (slot < 2) {
    uVar2 = 0;
    do {
      uVar1 = uVar2 + 1;
      f33_crypto_key_request[slot][uVar2] = '\0';
      uVar2 = uVar1;
    } while (uVar1 < 0x40);
    uVar2 = 0;
    do {
      uVar1 = uVar2 + 1;
      f33_crypto_key_result[(short)(ushort)slot][uVar2] = '\0';
      uVar2 = uVar1;
    } while (uVar1 < 0x30);
  }
  return;
}

void f33_crypto_bank_initialize_mode(void)

{
  f33_crypto_mode = 'Z';
  f33_crypto_previous_mode = 'Z';
  return;
}

void f33_crypto_bank_retire_direct_update(void)

{
  if (f33_crypto_direct_phase == 'U') {
    f33_crypto_direct_activation = '\x02';
  }
  if (((f33_crypto_direct_phase == 'f') &&
      (f33_crypto_direct_activation = 0xff, f33_crypto_direct_failure_count != 0xff)) &&
     (f33_crypto_direct_failure_count = f33_crypto_direct_failure_count + 1,
     f33_crypto_config_direct_failure_limit <= f33_crypto_direct_failure_count)) {
    f33_crypto_direct_inhibited = 'Z';
  }
  return;
}

void f33_crypto_bank_retire_collected_update(void)

{
  uint uVar1;
  uchar uVar2;
  uint uVar3;
  uint32_t puVar4;
  uchar uVar5;
  
  uVar2 = f33_crypto_collected_phase;
  puVar4 = 0xfebeb800u;
  uVar5 = f33_crypto_collected_activation;
  if (f33_crypto_collected_phase == 'U') {
    uVar5 = '\x02';
    puVar4 = 0xfebeb800u;
    f33_crypto_bank_clear_fragment_history();
    uVar3 = 0;
    do {
      uVar1 = uVar3 + 1;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(uVar3 - 0x65fa))))) = 0;
      uVar3 = uVar1;
    } while (uVar1 < 0x40);
    uVar3 = 0;
    do {
      uVar1 = uVar3 + 1;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(uVar3 - 0x658a))))) = 0;
      uVar3 = uVar1;
    } while (uVar1 < 0x30);
  }
  if (uVar2 == 'f') {
    uVar5 = 0xff;
    f33_crypto_bank_clear_fragment_history();
                    /* WARNING: Could not inline here */
    f33_crypto_bank_clear_key_material('\x01');
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x676a))))) = uVar5;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6769))))) = uVar2;
  return;
}

void f33_crypto_bank_retire_test_operation(void)

{
  if (f33_crypto_test_phase == '3') {
    f33_crypto_test_failed = '\0';
    f33_crypto_test_activation = '\x02';
  }
  if (f33_crypto_test_phase == 'D') {
    f33_crypto_test_activation = 0xff;
    f33_crypto_test_failed = 'Z';
  }
  return;
}

void f33_crypto_bank_snapshot_test_generations(void)

{
  f33_crypto_test_previous_generation[0] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5338u + (uint32_t)(DAT_000257d0) * 1u))));
  f33_crypto_test_previous_generation[1] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5338u + (uint32_t)(DAT_000257d2) * 1u))));
  f33_crypto_test_previous_generation[2] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5338u + (uint32_t)(DAT_000257d4) * 1u))));
  f33_crypto_test_previous_generation[3] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5338u + (uint32_t)(DAT_000257d6) * 1u))));
  f33_crypto_test_previous_generation[4] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5338u + (uint32_t)(DAT_000257d8) * 1u))));
  return;
}

uint f33_crypto_bank_compare_aes_result(void)

{
  uint uVar1;
  
  uVar1 = 0;
  do {
    if (f33_crypto_test_expected[uVar1] != f33_crypto_aes_result[uVar1]) {
      return 0x44;
    }
    uVar1 = uVar1 + 1;
  } while (uVar1 < 0x10);
  return 0x33;
}

uint f33_crypto_bank_compare_mac_result(void)

{
  uint uVar1;
  
  uVar1 = 0;
  do {
    if (f33_crypto_test_expected[uVar1] != f33_crypto_mac_result[uVar1]) {
      return 0x44;
    }
    uVar1 = uVar1 + 1;
  } while (uVar1 < 0x10);
  return 0x33;
}

undefined1 FUN_0006a12a(void)

{
  return DAT_febe508f;
}

undefined4 FUN_0006a130(void)

{
  return DAT_febe505c;
}

undefined2 FUN_0006a136(uint param_1)

{
  return *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe50b6u)) + (param_1 & 7) * 2);
}

undefined1 FUN_0006a144(void)

{
  return DAT_febe508b;
}

undefined1 FUN_0006a14a(void)

{
  return DAT_febe508c;
}

uchar FUN_0006a150(void)

{
  return f33_crypto_test_failed;
}

void FUN_0006a174(uchar param_1)

{
  f33_crypto_mode = param_1;
  return;
}

void FUN_0006a17a(void)

{
  DAT_febe505c = 0;
  return;
}

uchar FUN_0006a180(uint param_1)

{
  if ((param_1 & 0xff) < 2) {
    return f33_crypto_profile_failed[param_1 & 0xff];
  }
  return '\0';
}

undefined4 FUN_0006a192(void)

{
  if ((f33_crypto_direct_activation != '\x01') && (f33_crypto_collected_activation != '\x01')) {
    return 0;
  }
  return 0x5a;
}

void FUN_0006a1ac(undefined2 param_1)

{
  DAT_febe5070 = param_1;
  return;
}

void FUN_0006a280(undefined2 param_1)

{
  uint uVar1;
  
  if (DAT_febe5090 == '\0') {
    uVar1 = (uint)DAT_febe508a;
    DAT_febe508a = DAT_febe508a + 1;
    *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe50b6u)) + (uVar1 & 7) * 2) = param_1;
  }
  return;
}

uint f33_crypto_bank_key_update_completed(uchar result)

{
  uchar uVar1;
  
  uVar1 = 'f';
  if (result == '\0') {
    uVar1 = 'D';
  }
  if (f33_crypto_direct_activation == '\x01') {
    f33_crypto_direct_phase = uVar1;
    uVar1 = f33_crypto_collected_phase;
  }
  f33_crypto_collected_phase = uVar1;
  return 0;
}

uint f33_crypto_bank_aes_completed(uchar result)

{
  uint32_t puVar1;
  undefined1 uVar2;
  uint uVar3;
  
  puVar1 = 0xfebeb800u;
  uVar2 = 0x44;
  if (result == '\0') {
    puVar1 = 0xfebeb800u;
    uVar3 = f33_crypto_bank_compare_aes_result();
    uVar2 = (undefined1)uVar3;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6764))))) = uVar2;
  return 0;
}

uint f33_crypto_bank_verification_completed(uchar result)

{
  uchar *puVar1;
  
  if (result != '\0') {
    f33_crypto_verification_result = '\x01';
  }
  puVar1 = ((void *)camry_host_ptr((uint32_t)((0xfebe5097u))));
  if (f33_crypto_direct_activation == '\x01') {
    puVar1 = ((void *)camry_host_ptr((uint32_t)((0xfebe5092u))));
  }
  *puVar1 = 'F';
  return 0;
}

uint f33_crypto_bank_mac_completed(uchar result)

{
  uint32_t puVar1;
  undefined1 uVar2;
  uint uVar3;
  
  puVar1 = 0xfebeb800u;
  uVar2 = 0x44;
  if (result == '\0') {
    puVar1 = 0xfebeb800u;
    uVar3 = f33_crypto_bank_compare_mac_result();
    uVar2 = (undefined1)uVar3;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6764))))) = uVar2;
  return 0;
}

undefined4 FUN_0006a31a(undefined2 param_1)

{
  DAT_febe5088 = param_1;
  return 0;
}

undefined4 f33_return_const_0_6a328(void)

{
  return 0;
}

undefined4 f33_return_const_0_6a3f0(void)

{
  return 0;
}

undefined4 FUN_0006a3f4(undefined2 param_1)

{
  undefined4 uVar1;
  
  if (DAT_00028fd6 == 'Z') {
    uVar1 = 0;
  }
  else {
    uVar1 = ((void)(param_1), f33_return_const_0_6a3f0());
  }
  return uVar1;
}

void FUN_0006a440(void)

{
  uint uVar1;
  
  DAT_febe39dc = 0;
  uVar1 = 0;
  do {
    *(undefined4 *)(((undefined *)camry_host_ptr(0xfebe39e0u)) + uVar1 * 4) = 0xffff;
    uVar1 = uVar1 + 1;
  } while (uVar1 < 0x100);
  return;
}

void f33_nvm_initialize_logical_cells(void)

{
  uint uVar1;
  uint uVar2;
  uchar uVar3;
  
  uVar2 = 0;
  do {
    if ((((ushort)f33_nvm_logical_descriptors[uVar2].opaque_0a >> 0xb & 1) == 0) &&
       ((f33_nvm_logical_descriptors[uVar2].opaque_0a & 0x10) != 0)) {
      uVar3 = '\x01';
    }
    else {
      uVar3 = '\x02';
    }
    uVar1 = uVar2 + 1;
    f33_nvm_logical_results[uVar2].write_inhibit = uVar3;
    f33_nvm_logical_results[uVar2].result = '\0';
    uVar2 = uVar1;
  } while (uVar1 < 0x7c);
  DAT_febf60f8 = 0;
  return;
}

undefined4 f33_return_const_1_71cf4(void)

{
  return 1;
}

void FUN_00071d3e(void)

{
  uint uVar1;
  int iVar2;
  uint uVar3;
  
  uVar3 = (uint)DAT_febf60f8;
  iVar2 = 5;
  do {
    if (0x7b < uVar3) {
      uVar3 = 0;
    }
    if (f33_nvm_logical_results[uVar3].result == '\x02') {
      FUN_00072130();
    }
    uVar1 = uVar3 + 1;
    uVar3 = uVar1 & 0xffff;
    iVar2 = iVar2 + -1;
  } while (iVar2 != 0);
  DAT_febf60f8 = (short)uVar1;
  return;
}

void FUN_00071d7c(void)

{
  DAT_febf6102 = 0xf0;
  return;
}

undefined4 f33_return_const_0_71d88(void)

{
  return 0;
}

void FUN_000720bc(void)

{
  DAT_febf6100 = 1;
  return;
}

void FUN_000720d6(void)

{
  DAT_febf60fd = 1;
  return;
}

void FUN_00072108(uint param_1)

{
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebf60fau + (uint32_t)(param_1 & 0xff) * 1u)))) = 2;
  return;
}

void FUN_00072130(void)

{
  FUN_000796be(2);
  DAT_febf6102 = 0xf;
  return;
}

uint f33_nvm_service_uninitialized(void)

{
  return (uint)(((int8_t)DAT_febf6102) != -0x10);
}

void FUN_0007217e(void)

{
  f33_nvm_scheduler_phase = '\x01';
  DAT_febf6114 = 0x9da70ae7;
  f33_nvm_scheduler_operation.operation = 0x9da70ae7;
  f33_nvm_scheduler_operation.logical_handle = 0xffff;
  f33_nvm_scheduler_operation.buffer_08 = 0;
  f33_nvm_scheduler_operation.buffer_0c = 0;
  DAT_febf6120 = 0;
  DAT_febf6122 = 0xffff;
  DAT_febf6125 = 0;
  return;
}

void thunk_FUN_0007217e(void)

{
  FUN_0007217e();
  return;
}

bool FUN_00072418(void)

{
  int iVar1;
  
  iVar1 = FUN_00079420();
  if (iVar1 != 0) {
    FUN_0007305e(0);
  }
  else {
    FUN_0007305e(1);
  }
  return iVar1 != 0;
}

undefined4 FUN_0007285c(undefined2 param_1)

{
  int iVar1;
  undefined4 uVar2;
  char cStack_9;
  
  uVar2 = 0;
  iVar1 = ((void)(param_1), (void)(&cStack_9), f33_return_const_1_71cf4());
  if ((iVar1 == 0) && (cStack_9 == 'w')) {
    FUN_0007211a(5);
    uVar2 = 1;
  }
  return uVar2;
}

void FUN_00072888(char param_1)

{
  if ((param_1 != '\0') && (param_1 != '\x04')) {
    DAT_febf6120 = 1;
  }
  return;
}

bool FUN_00072f1e(ushort param_1)

{
  uint uVar1;
  F33NvmOperation FStack_1c;
  
  uVar1 = f33_nvm_snapshot_scheduler_operation(&FStack_1c);
  return (uVar1 == 1 || uVar1 == 2) && FStack_1c.logical_handle == param_1;
}

char FUN_00072fc8(char param_1)

{
  if (param_1 != '&') {
    if (param_1 == '6') {
      param_1 = '\x06';
    }
    return param_1;
  }
  return '\x01';
}

void FUN_0007305e(char param_1)

{
  undefined *puVar1;
  
  puVar1 = ((undefined *)camry_host_ptr((uint32_t)(0x5)));
  if (param_1 == '\x01') {
    puVar1 = ((undefined *)camry_host_ptr(0xfde8u));
  }
  FUN_000747c8(0, camry_host_addr(puVar1));
  return;
}

void f33_nvm_clear_queue_headers(void)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = 0;
  do {
    uVar1 = uVar2 + 1;
    f33_nvm_queue_headers[uVar2].head = 0xffff;
    f33_nvm_queue_headers[uVar2].tail = 0xffff;
    uVar2 = uVar1;
  } while (uVar1 < 0x7f);
  return;
}

uint f33_nvm_queue_index(uint base,uint offset)

{
  return offset + base & 0xffff;
}

void f33_nvm_reset_slot_range(ushort queue,ushort first,ushort last)

{
  uint uVar1;
  
  f33_nvm_queue_headers[queue].head = first;
  f33_nvm_queue_headers[queue].tail = last;
  for (uVar1 = (uint)first; uVar1 <= last; uVar1 = uVar1 + 1 & 0xffff) {
    f33_nvm_queue_slots[uVar1].operation = 0x9da70ae7;
    f33_nvm_queue_slots[uVar1].read_buffer = 0;
    f33_nvm_queue_slots[uVar1].write_buffer = 0;
    f33_nvm_queue_slots[uVar1].logical_handle = 0xffff;
    f33_nvm_queue_slots[uVar1].next = (short)uVar1 + 1;
  }
  f33_nvm_queue_slots[last].next = 0xffff;
  return;
}

bool FUN_00073274(void)

{
  bool bVar1;
  
  bVar1 = false;
  if (((ushort)(f33_nvm_reserved_free_count + f33_nvm_reserved_used_count) == 1) &&
     ((ushort)(f33_nvm_normal_free_count + f33_nvm_normal_used_count) == 0x7a)) {
    bVar1 = (ushort)(f33_nvm_normal_used_count + f33_nvm_reserved_used_count) != 0;
  }
  else {
    FUN_00072130();
  }
  return bVar1;
}

uint f33_nvm_check_slot_partition(ushort index,ushort queue)

{
  ushort uVar1;
  uint uVar2;
  ushort uVar3;
  
  uVar2 = 0;
  if ((queue == 0) || (queue == 2)) {
    uVar1 = 0x7a;
    uVar3 = uVar1;
  }
  else {
    uVar1 = 0;
    uVar3 = 0x79;
  }
  if ((uVar3 < index) || (index < uVar1)) {
    FUN_00072130();
    uVar2 = 1;
  }
  return uVar2;
}

bool FUN_00073334(uint param_1,short param_2)

{
  ushort logical_handle;
  uint uVar1;
  uint uVar2;
  bool bVar3;
  
  logical_handle = f33_nvm_queue_slots[param_1 & 0xffff].logical_handle;
  bVar3 = true;
  if ((logical_handle <= (ushort)(f33_nvm_logical_descriptor_count - 1)) && (1 < logical_handle)) {
    uVar2 = f33_nvm_queue_key(logical_handle);
    uVar1 = 0;
    if (param_2 != 2) {
      uVar1 = (uint)(ushort)(param_2 - 3);
    }
    bVar3 = uVar2 != uVar1;
    if (uVar2 == uVar1) {
      return false;
    }
  }
  FUN_00072130();
  return bVar3;
}

uint f33_nvm_append_queue_slot(ushort queue,ushort index)

{
  ushort index_00;
  uint uVar1;
  
  index_00 = f33_nvm_queue_headers[queue].tail;
  if (index_00 == 0xffff) {
    f33_nvm_queue_headers[queue].head = index;
  }
  else {
    uVar1 = f33_nvm_check_slot_partition(index_00,queue);
    if (uVar1 != 0) {
      return 1;
    }
    f33_nvm_queue_slots[index_00].next = index;
  }
  f33_nvm_queue_headers[queue].tail = index;
  f33_nvm_queue_slots[index].next = 0xffff;
  return 0;
}

uint FUN_00073748(ushort param_1,ushort param_2,undefined4 param_3)

{
  undefined4 *extraout_r7;
  uint uVar1;
  
  uVar1 = f33_nvm_append_queue_slot(param_1,param_2);
  if (uVar1 == 0) {
    FUN_00073424(((undefined4 *)camry_host_ptr((uint32_t)(param_3))), f33_nvm_queue_slots + param_2);
    *extraout_r7 = 0x9da70ae7;
    extraout_r7[1] = 0;
    extraout_r7[2] = 0;
    *(undefined2 *)(extraout_r7 + 3) = 0xffff;
  }
  return uVar1;
}

void FUN_000739e8(void)

{
  f33_nvm_zero_handle_operation.operation = 0x9da70ae7;
  f33_nvm_zero_handle_operation.logical_handle = 0xffff;
  f33_nvm_zero_handle_operation.buffer_08 = 0;
  f33_nvm_zero_handle_operation.buffer_0c = 0;
  return;
}

uchar thunk_FUN_000766c6(void)

{
  return FUN_000766c6();
}

uchar FUN_00073c6c(void)

{
  return f33_nvm_operation_state;
}

undefined1 FUN_00073c76(void)

{
  undefined1 uVar1;
  
  if (f33_nvm_operation_state == '\x02') {
    uVar1 = 2;
  }
  else {
    uVar1 = 1;
  }
  return uVar1;
}

ushort FUN_00073e8a(void)

{
  ushort uVar1;
  ushort uVar2;
  uchar uVar3;
  int iVar4;
  
  uVar1 = f33_nvm_pending_operation.logical_handle;
  ((void)(f33_nvm_pending_operation.logical_handle), FUN_00073e54());
  uVar2 = f33_nvm_operation_phase;
  iVar4 = ((void)(uVar1), thunk_FUN_000766c6());
  uVar3 = '\0';
  if (iVar4 != 0) {
    if (iVar4 != 1) {
      return uVar2;
    }
    FUN_00072108(0);
    FUN_00072108(4);
    uVar3 = '\x01';
  }
  f33_nvm_operation_state = uVar3;
  f33_nvm_operation_step = 0xffff;
  return 1;
}

undefined4 FUN_000741a0(void)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  undefined4 uVar4;
  undefined1 auStack_1c [16];
  
  iVar3 = 0;
  iVar1 = FUN_00073274();
  if (iVar1 == 0) {
    iVar3 = FUN_00073978(auStack_1c);
  }
  uVar2 = f33_nvm_service_uninitialized();
  if (uVar2 == 0) {
    if (iVar3 == 0) {
      uVar4 = 2;
    }
    else {
      uVar4 = 1;
    }
  }
  else {
    uVar4 = 4;
  }
  return uVar4;
}

uint f33_nvm_check_logical_handle(ushort logical_handle,uchar api,uchar allow_zero)

{
  uint uVar1;
  
  uVar1 = 1;
  if (((logical_handle < 2) || ((ushort)(f33_nvm_logical_descriptor_count - 1) < logical_handle)) &&
     ((allow_zero != '\x01' || (logical_handle != 0)))) {
    ((void)(0x14), (void)(0), (void)(api), (void)(10), f33_return_const_0_71d88());
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}

bool FUN_00074228(char param_1)

{
  if (param_1 != '\x01') {
    return param_1 != '\0';
  }
  return false;
}

bool FUN_00074274(uint param_1,undefined1 param_2)

{
  bool bVar1;
  
  bVar1 = ((ushort)f33_nvm_logical_descriptors[param_1 & 0xffff].opaque_0a >> 0xb & 1) != 0;
  if (bVar1) {
    ((void)(0x14), (void)(0), (void)(param_2), (void)(0x18), f33_return_const_0_71d88());
  }
  return bVar1;
}

bool FUN_000742ea(int param_1,undefined1 param_2)

{
  if (param_1 == 0) {
    ((void)(0x14), (void)(0), (void)(param_2), (void)(0xe), f33_return_const_0_71d88());
  }
  return param_1 == 0;
}

undefined4 FUN_0007430c(ushort param_1,undefined4 param_2)

{
  uint uVar1;
  int iVar2;
  undefined4 uVar3;
  
  uVar3 = 1;
  uVar1 = f33_nvm_check_logical_handle(param_1,'\x04','\x01');
  iVar2 = FUN_000742ea(param_2,4);
  if (uVar1 == 0) {
    if (iVar2 == 0) {
      uVar3 = 0;
    }
    else {
      uVar3 = 1;
    }
  }
  return uVar3;
}

bool FUN_00074338(int param_1,undefined1 param_2)

{
  if (param_1 == 0) {
    ((void)(0x14), (void)(0), (void)(param_2), (void)(0xf), f33_return_const_0_71d88());
  }
  return param_1 == 0;
}

bool FUN_0007435a(undefined4 param_1)

{
  int iVar1;
  
  iVar1 = FUN_00074338(param_1,0xf);
  return iVar1 != 0;
}

bool FUN_0007436e(ushort param_1)

{
  uint uVar1;
  
  uVar1 = f33_nvm_check_logical_handle(param_1,'\x10','\0');
  return uVar1 != 0;
}

bool FUN_00074468(undefined2 param_1,undefined1 param_2)

{
  int iVar1;
  
  iVar1 = ((void)(param_1), f33_return_const_0_745c4());
  if (iVar1 == 0) {
    ((void)(0x14), (void)(0), (void)(param_2), (void)(0x18), f33_return_const_0_71d88());
  }
  return iVar1 == 0;
}

undefined4 f33_return_const_0_745b8(void)

{
  return 0;
}

undefined4 f33_return_const_1_745c0(void)

{
  return 1;
}

undefined4 f33_return_const_0_745c4(void)

{
  return 0;
}

void FUN_000745c8(void)

{
  f33_nvm_read_buffer_override = 0;
  f33_nvm_write_buffer_override = 0;
  return;
}

void f33_nvm_reset_buffer_retry(void)

{
  f33_nvm_buffer_retry = '\0';
  return;
}

undefined4 FUN_0007463e(void)

{
  if (f33_nvm_buffer_retry < DAT_00026bf4) {
    f33_nvm_buffer_retry = f33_nvm_buffer_retry + '\x01';
    return 2;
  }
  return 1;
}

void FUN_0007477a(void)

{
  uint uVar1;
  
  for (uVar1 = (uint)DAT_00027624; uVar1 != 0; uVar1 = uVar1 - 1) {
    DAT_febf6b18 = 0;
  }
  return;
}

void FUN_000747c8(undefined4 param_1,undefined4 param_2)

{
  DAT_febf6b18 = param_2;
  return;
}

void FUN_000747d2(void)

{
  DAT_febf6b18 = 0;
  return;
}

void FUN_000749ae(void)

{
  DAT_febf6b20 = 0xff;
  DAT_febf6b21 = 0xff;
  return;
}

void FUN_000749bc(undefined1 param_1)

{
  DAT_febf6b20 = param_1;
  return;
}

void FUN_000749c6(undefined1 param_1)

{
  DAT_febf6b21 = param_1;
  return;
}

void FUN_000749d0(void)

{
  f33_nvm_driver_phase = '\0';
  DAT_febf6b24 = 0;
  DAT_febf6b1c = 0;
  DAT_febf6b68 = 0xffffffff;
  DAT_febf6b6c = 0;
  return;
}

void FUN_000749e4(void)

{
  DAT_febf6c34 = 0;
  FUN_000749ae();
  FUN_000749d0();
  return;
}

void FUN_000749fc(void)

{
  DAT_febf6c5a = 0xff;
  DAT_febf6c59 = 0;
  DAT_febf6c30 = 0xffffffff;
  DAT_febf6c48 = 0;
  FUN_00074872(camry_host_addr(((undefined *)camry_host_ptr(0xfebf6bd0u))), 0, 0x40);
  return;
}

uint f33_nvm_sync_access_blocked(void)

{
  int iVar1;
  uint uVar2;
  
  uVar2 = 1;
  if (f33_nvm_driver_block_latch == '\0') {
    iVar1 = FUN_00078896();
    uVar2 = (uint)(iVar1 == 0x80);
  }
  return uVar2;
}

void FUN_00074a82(undefined4 param_1)

{
  DAT_febf6c34 = param_1;
  return;
}

int FUN_00074bb4(uint param_1)

{
  return (int)(param_1 & 0xffff) >> 2;
}

undefined4 FUN_00074bf2(void)

{
  if (DAT_febf6b24 < DAT_0002792d) {
    DAT_febf6b24 = DAT_febf6b24 + 1;
    DAT_febf6b1c = DAT_0002791c;
    f33_nvm_driver_phase = 0xaa;
    return 2;
  }
  return 0xffff;
}

undefined4 FUN_00074cd2(char param_1)

{
  undefined4 uVar1;
  
  if (param_1 != '\t') {
    uVar1 = 0xff;
    if (param_1 == '\v') {
      uVar1 = 2;
    }
    return uVar1;
  }
  return 1;
}

void FUN_00074ce8(char param_1)

{
  undefined4 uVar1;
  
  if (param_1 == '\x01') {
    uVar1 = 0;
    f33_nvm_driver_block_latch = '\x01';
  }
  else {
    if (param_1 != '\x02') {
      return;
    }
    uVar1 = 1;
  }
  FUN_00076a8c(uVar1);
  return;
}

undefined4 FUN_00074e6e(void)

{
  uint uVar1;
  int iVar2;
  
  uVar1 = f33_nvm_sync_access_blocked();
  if (uVar1 != 1) {
    iVar2 = FUN_0007888c();
    if (iVar2 == 1) {
      return 0;
    }
    if (iVar2 == 2) {
      return 1;
    }
  }
  return 2;
}

void FUN_00074ec2(void)

{
  FUN_000749bc(1);
  return;
}

void FUN_00074ed0(void)

{
  FUN_000749bc(2);
  return;
}

undefined4 FUN_00074ede(char param_1)

{
  undefined4 uVar1;
  
  if ((param_1 != '\x05') && (-0x7f < param_1)) {
    uVar1 = 0xff;
    if (param_1 == -0x7e) {
      uVar1 = 2;
    }
    return uVar1;
  }
  return 1;
}

undefined4 FUN_00074efe(short param_1,undefined4 param_2,undefined4 param_3,undefined1 param_4)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = FUN_000781da();
  if ((iVar1 != 1) && (param_1 == 0x5c)) {
    FUN_000749c6(param_4);
    uVar2 = FUN_00074ede((uint)(byte)param_4);
    FUN_00074ce8(uVar2);
  }
  return 0;
}

uchar FUN_00074f2e(uint param_1)

{
  uchar uVar1;
  
  if ((param_1 & 0xffff) < (uint)f33_nvm_descriptor_count) {
    uVar1 = f33_nvm_descriptors[param_1 & 0xffff].option;
  }
  else {
    uVar1 = 0xff;
  }
  return uVar1;
}

int FUN_00074f4a(void)

{
  undefined4 uVar1;
  int iVar2;
  
  uVar1 = FUN_00077c9e();
  iVar2 = FUN_00074f2e(uVar1);
  if (iVar2 == 0) {
    uVar1 = 1;
  }
  else {
    uVar1 = 0xff;
    if (iVar2 == 1) {
      uVar1 = 0;
    }
  }
  FUN_000783b6(uVar1);
  return iVar2;
}

void FUN_00074f72(void)

{
  DAT_febf6c51 = 1;
  return;
}

void FUN_00074f7e(void)

{
  DAT_febf6c51 = 0;
  return;
}

undefined4 FUN_00074f88(char param_1)

{
  undefined4 uVar1;
  
  uVar1 = 0;
  if ((param_1 == '\0') && (DAT_febf6c51 == '\x01')) {
    DAT_febf6c51 = '\x02';
    uVar1 = 1;
  }
  return uVar1;
}

void f33_fill_constant_block_74fa2(void)

{
  DAT_febf6c55 = 0;
  DAT_febf6c54 = 0;
  DAT_febf6c53 = 0;
  DAT_febf6c52 = 0;
  DAT_febf6c51 = 0;
  DAT_febf6c50 = 0;
  DAT_febf6c3e = 0xffff;
  DAT_febf6c40 = 0xffff;
  return;
}

undefined4 FUN_00074fe6(void)

{
  f33_fill_constant_block_74fa2();
  thunk_FUN_000772f8();
  thunk_FUN_00077df2();
  return 1;
}

void FUN_00075008(undefined4 param_1)

{
  FUN_000783ca(param_1);
  FUN_000783c0(1);
  return;
}

void FUN_0007501a(undefined4 param_1)

{
  FUN_000783ca(param_1);
  FUN_000783c0(2);
  return;
}

void FUN_0007502c(undefined4 param_1)

{
  FUN_000783ca(param_1);
  DAT_febf6c55 = 1;
  return;
}

undefined4 FUN_0007505e(char param_1)

{
  undefined4 uVar1;
  
  if (param_1 == '\x01') {
    uVar1 = 10;
    DAT_febf6c52 = 0;
    FUN_00077d1e((uint)(byte)param_1);
  }
  else {
    uVar1 = 6;
  }
  return uVar1;
}

uint FUN_0007543c(uint param_1)

{
  return 1 << (param_1 & 0x1f) & 3;
}

uint FUN_00075678(uint param_1)

{
  return 1 << (1 << (param_1 & 0x1f) & 3U) & 3;
}

undefined4 FUN_00075760(void)

{
  int iVar1;
  undefined4 uVar2;
  
  if (DAT_febf6c55 == '\x01') {
    iVar1 = FUN_000783d4();
    if (iVar1 == 1) {
      DAT_febf6c54 = 1;
      uVar2 = 0xf;
      DAT_febf6c40 = DAT_febf6c3e;
    }
    else {
      uVar2 = 0xc;
      f33_nvm_mark_physical_attempt_error();
    }
  }
  else {
    uVar2 = 0xb;
  }
  return uVar2;
}

void FUN_000761e6(void)

{
  DAT_febf6c56 = 0;
  DAT_febf6c57 = 0;
  DAT_febf6c58 = 0;
  thunk_FUN_000772f8();
  return;
}

undefined4 FUN_0007620a(void)

{
  FUN_000761e6();
  return 1;
}

void FUN_00076224(undefined4 param_1)

{
  FUN_000783ca(param_1);
  FUN_000783c0(1);
  return;
}

void FUN_00076236(undefined4 param_1)

{
  FUN_000783ca(param_1);
  FUN_000783c0(2);
  return;
}

void FUN_00076248(undefined4 param_1)

{
  FUN_000783ca(param_1);
  DAT_febf6c58 = 1;
  return;
}

undefined4 FUN_000762ca(void)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = FUN_00077c64();
  if (iVar1 == 1) {
    DAT_febf6c57 = 0;
    uVar2 = 1;
  }
  else if (iVar1 == 2) {
    uVar2 = 4;
  }
  else {
    uVar2 = 0xff;
  }
  return uVar2;
}

void FUN_0007637e(void)

{
  DAT_febf6c56 = 1;
  return;
}

undefined4 FUN_0007638a(char param_1)

{
  undefined4 uVar1;
  
  uVar1 = 0;
  if ((param_1 == '\0') && (DAT_febf6c56 == '\x01')) {
    DAT_febf6c56 = '\x02';
    uVar1 = 1;
  }
  return uVar1;
}

void FUN_0007640c(void)

{
  DAT_febf6c56 = 0;
  return;
}

void FUN_000764c2(void)

{
  DAT_febf6b77 = 1;
  return;
}

void FUN_000764ce(void)

{
  f33_nvm_physical_result_state = '\0';
  FUN_000764c2();
  return;
}

undefined2 FUN_0007650c(undefined2 param_1)

{
  return param_1;
}

undefined4 FUN_00076512(undefined2 param_1,undefined4 param_2)

{
  uint32_t puVar1;
  int iVar2;
  undefined4 uVar3;
  
  puVar1 = 0x23dfcu;
  uVar3 = 1;
  iVar2 = FUN_00077c64();
  if (iVar2 == 0) {
    iVar2 = camry_host_addr(FUN_00077c82(param_1));
    if ((iVar2 == 1) && (iVar2 = camry_host_addr(FUN_00077cc8(param_2)), iVar2 == 1)) {
      FUN_00077c5a(2);
      FUN_000783de((*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x3b1c)))));
      uVar3 = 0;
    }
    else {
      uVar3 = 2;
    }
  }
  return uVar3;
}

undefined4 FUN_000765ba(undefined2 param_1,undefined4 param_2)

{
  uint32_t puVar1;
  int iVar2;
  undefined4 uVar3;
  
  puVar1 = 0x23dfcu;
  uVar3 = 1;
  iVar2 = FUN_00077c64();
  if (iVar2 == 0) {
    iVar2 = camry_host_addr(FUN_00077c82(param_1));
    if ((iVar2 == 1) && (iVar2 = camry_host_addr(FUN_00077ca8(param_2)), iVar2 == 1)) {
      FUN_00077c5a(1);
      FUN_000783de((*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x3b1c)))));
      uVar3 = 0;
    }
    else {
      uVar3 = 2;
    }
  }
  return uVar3;
}

void FUN_00076644(void)

{
  DAT_febf6b77 = 0;
  return;
}

undefined4 FUN_00076688(void)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = FUN_00077c64();
  if (iVar1 == 1 || iVar1 == 2) {
    uVar2 = 2;
  }
  else if ((DAT_febf6b77 == '\0') || (iVar1 = FUN_00074e6e(), iVar1 != 1 && iVar1 != 2)) {
    uVar2 = 1;
  }
  else {
    uVar2 = 3;
  }
  return uVar2;
}

undefined4 thunk_FUN_00076688(void)

{
  return FUN_00076688();
}

uchar FUN_000766c6(void)

{
  return f33_nvm_physical_result_state;
}

void thunk_FUN_000764c2(void)

{
  FUN_000764c2();
  return;
}

bool FUN_00076762(void)

{
  return DAT_febf6b77 != '\0';
}

void FUN_00076782(void)

{
  f33_nvm_secondary_result_state = '\0';
  f33_nvm_physical_attempt_flags = '\0';
  return;
}

void FUN_00076794(void)

{
  f33_nvm_physical_attempt_flags = '\0';
  return;
}

void FUN_00076988(void)

{
  f33_nvm_physical_attempt_flags = f33_nvm_physical_attempt_flags | 2;
  return;
}

void FUN_00076992(void)

{
  f33_nvm_physical_attempt_flags = f33_nvm_physical_attempt_flags | 4;
  return;
}

void FUN_0007699c(void)

{
  f33_nvm_physical_attempt_flags = f33_nvm_physical_attempt_flags | 8;
  return;
}

bool thunk_FUN_00079432(void)

{
  return FUN_00079432();
}

undefined4 thunk_FUN_00079444(void)

{
  return FUN_00079444();
}

void FUN_00076a8c(char param_1)

{
  if ((param_1 == '\0') || (param_1 == '\x01')) {
    FUN_000796be((uint)(byte)param_1);
  }
  return;
}

void FUN_00076aa2(char param_1)

{
  if (param_1 == '\0') {
    FUN_000796f4((uint)(byte)param_1);
  }
  return;
}

void thunk_FUN_00076782(void)

{
  FUN_00076782();
  return;
}

undefined4 thunk_FUN_0007490e(undefined4 param_1)

{
  return FUN_0007490e(param_1);
}

undefined4 FUN_000772ea(int param_1)

{
  return FUN_0007490e(param_1 + 0xc);
}

undefined4 FUN_000778d8(int param_1)

{
  return FUN_0007490e(param_1 + 4);
}

void FUN_00077bd8(void)

{
  DAT_febf6c4a = 0;
  DAT_febf6c38 = 0xffff;
  return;
}

void FUN_00077c42(void)

{
  if (2 < DAT_febf6c4a) {
    FUN_00077bd8();
  }
  return;
}

void FUN_00077c5a(undefined1 param_1)

{
  DAT_febf6c4a = param_1;
  return;
}

undefined1 FUN_00077c64(void)

{
  return DAT_febf6c4a;
}

void FUN_00077c6e(undefined2 param_1)

{
  DAT_febf6c3a = param_1;
  return;
}

undefined2 FUN_00077c78(void)

{
  return DAT_febf6c3a;
}

undefined * FUN_00077c82(ushort param_1)

{
  if (param_1 < f33_nvm_descriptor_count) {
    DAT_febf6c38 = param_1;
    return ((undefined *)camry_host_ptr((uint32_t)(0x1)));
  }
  return ((undefined *)camry_host_ptr(0xfffbu));
}

undefined2 FUN_00077c9e(void)

{
  return DAT_febf6c38;
}

undefined * FUN_00077ca8(int param_1)

{
  if (param_1 != 0) {
    DAT_febf6c14 = param_1;
    return ((undefined *)camry_host_ptr((uint32_t)(0x1)));
  }
  return ((undefined *)camry_host_ptr(0xfffbu));
}

undefined4 FUN_00077cbe(void)

{
  return DAT_febf6c14;
}

undefined * FUN_00077cc8(int param_1)

{
  if (param_1 != 0) {
    DAT_febf6c18 = param_1;
    return ((undefined *)camry_host_ptr((uint32_t)(0x1)));
  }
  return ((undefined *)camry_host_ptr(0xfffbu));
}

undefined4 FUN_00077cde(void)

{
  return DAT_febf6c18;
}

void FUN_00077ce8(void)

{
  f33_nvm_completion_mode = DAT_febf6c4a;
  f33_nvm_completion_storage_handle = DAT_febf6c38;
  FUN_00077bd8();
  return;
}

void FUN_00077d14(uint param_1)

{
  f33_nvm_completion_raw_result = param_1;
  return;
}

void FUN_00077d1e(uchar param_1)

{
  if (param_1 != '\0') {
    f33_nvm_completion_side_status = param_1;
  }
  return;
}

void FUN_00077df2(void)

{
  DAT_febf6c2c = 0xffffffff;
  return;
}

void thunk_FUN_00077df2(void)

{
  FUN_00077df2();
  return;
}

void FUN_000781a0(void)

{
  DAT_febf6c5c = 0;
  return;
}

void FUN_000781aa(undefined1 param_1)

{
  DAT_febf6c5b = param_1;
  return;
}

undefined1 FUN_000781b4(void)

{
  return DAT_febf6c5b;
}

undefined1 FUN_000781da(void)

{
  return DAT_febf6c5c;
}

void f33_fill_constant_block_781e4(void)

{
  DAT_febf6c20 = 0;
  DAT_febf6c4f = 0xff;
  DAT_febf6c4e = 0;
  DAT_febf6c4d = 0xff;
  DAT_febf6c1c = 1;
  return;
}

undefined1 FUN_000782b2(void)

{
  return DAT_febf6c4d;
}

void FUN_000783b6(undefined1 param_1)

{
  DAT_febf6c4d = param_1;
  return;
}

void FUN_000783c0(undefined1 param_1)

{
  DAT_febf6c4f = param_1;
  return;
}

void FUN_000783ca(undefined4 param_1)

{
  DAT_febf6c1c = param_1;
  return;
}

undefined4 FUN_000783d4(void)

{
  return DAT_febf6c1c;
}

undefined1 FUN_0007888c(void)

{
  return DAT_febf6cb0;
}

undefined1 FUN_00078896(void)

{
  return DAT_febf6cb1;
}

undefined1 FUN_00078aca(void)

{
  return DAT_febf6cb2;
}

void FUN_00078af8(void)

{
  int iVar1;
  uint uVar2;
  
  DAT_febf6c64 = 0;
  uVar2 = 0;
  DAT_febf6c60 = 0;
  DAT_febf6c68 = 0;
  DAT_febf6cac = 0;
  do {
    iVar1 = uVar2 * 4;
    uVar2 = uVar2 + 1;
    *(undefined4 *)(((undefined *)camry_host_ptr(0xfebf6c6cu)) + iVar1) = 0;
  } while (uVar2 < 0x10);
  return;
}

void FUN_00078b1c(void)

{
  FUN_00078af8();
  DAT_febf6cb1 = 1;
  DAT_febf6cb3 = 0;
  DAT_febf6cb2 = 0xe;
  DAT_febf6cb0 = 1;
  return;
}

bool FUN_00078d80(int param_1)

{
  return param_1 == 0;
}

undefined4 FUN_00078d88(uint param_1,int param_2)

{
  if ((param_1 < 0x8000) && ((param_2 - 1U & param_1) == 0)) {
    return 0;
  }
  return 1;
}

bool FUN_00078d9e(uint param_1,uint param_2,int param_3)

{
  if ((((param_2 != 0) && (param_2 < 0x41)) && ((param_3 - 1U & param_1) == 0)) &&
     ((param_3 - 1U & param_2) == 0)) {
    return 0x7fff < (param_2 + param_1) - 1;
  }
  return true;
}

bool FUN_00078dca(int param_1,int param_2)

{
  if (param_2 != 0) {
    return 0x7fff < (param_2 + param_1) - 1U;
  }
  return true;
}

undefined4 FUN_0007939c(undefined2 param_1,undefined1 param_2,undefined1 param_3,undefined1 param_4)

{
  return FUN_00074efe(param_1,param_2,param_3,param_4);
}

bool FUN_00079420(void)

{
  int iVar1;
  
  iVar1 = FUN_00079d12();
  return iVar1 != 0;
}

bool FUN_00079432(void)

{
  int iVar1;
  
  iVar1 = f33_return_const_0_79d24();
  return iVar1 != 0;
}

undefined4 FUN_00079444(void)

{
  int iVar1;
  undefined4 uVar2;
  
  uVar2 = 1;
  iVar1 = FUN_00079b5c();
  if (iVar1 != 0xc) {
    iVar1 = f33_return_const_0_79d28();
    if (iVar1 == 0) {
      uVar2 = 0;
    }
    else {
      uVar2 = 1;
    }
  }
  return uVar2;
}

uint f33_nvm_driver_gate_rejected(ushort ignored_service)

{
  uint uVar1;
  
  uVar1 = f33_nvm_driver_gate_hook();
  return (uint)(uVar1 != 0);
}

void FUN_00079638(void)

{
  f33_nvm_service_diagnostic_mask = 0;
  DAT_febf6cbc = 0xffff;
  f33_nvm_service_cd_diagnostic_mask = 0;
  DAT_febf6cc4 = 0xffff;
  DAT_febf6cb4 = 0;
  DAT_febf6cb8 = 0;
  f33_nvm_diagnostic_service = 0xff;
  return;
}

void FUN_0007969a(uchar param_1)

{
  f33_nvm_service_cd_diagnostic_mask = 0;
  DAT_febf6cc4 = 0;
  if (param_1 != '\f' && param_1 != '\r') {
    param_1 = 0xff;
  }
  f33_nvm_diagnostic_service = param_1;
  return;
}

void FUN_000796be(uint param_1)

{
  uint uVar1;
  
  uVar1 = DAT_febf6cb4;
  if ((param_1 & 0xff) < 3) {
    DAT_febf6cb4 = *(uint *)(((undefined *)camry_host_ptr(0x27cccu)) + (param_1 & 0xff) * 8) | DAT_febf6cb4;
    FUN_000797f6();
    if (uVar1 != DAT_febf6cb4) {
      ((void)(((undefined *)camry_host_ptr(0xfebf6cb4u))), f33_return_only_stub_79d36());
    }
  }
  return;
}

void FUN_000796f4(uint param_1)

{
  if ((param_1 & 0xff) < 3) {
    DAT_febf6cb4 = DAT_febf6cb4 & ~*(uint *)(((undefined *)camry_host_ptr(0x27cccu)) + (param_1 & 0xff) * 8);
    FUN_000797f6();
  }
  return;
}

void FUN_000797f6(void)

{
  uint uVar1;
  uint uVar2;
  
  DAT_febf6cb8 = 0;
  uVar1 = 0;
  uVar2 = 0;
  do {
    if ((*(uint *)(((undefined *)camry_host_ptr(0x27cccu)) + uVar2 * 8) & DAT_febf6cb4) != 0) {
      uVar1 = uVar1 | *(uint *)(((undefined *)camry_host_ptr(0x27cd0u)) + uVar2 * 8);
      DAT_febf6cb8 = uVar1;
    }
    uVar2 = uVar2 + 1;
  } while (uVar2 < 3);
  return;
}

bool FUN_00079848(uchar param_1,int param_2)

{
  if (param_2 != 0) {
    return param_1 != f33_nvm_diagnostic_service;
  }
  return true;
}

void FUN_00079862(void)

{
  DAT_febf6cd2 = 0;
  DAT_febf6cd4 = 0xff;
  DAT_febf6cd3 = 0xff;
  return;
}

void FUN_0007987e(undefined1 param_1)

{
  DAT_febf6cd0 = param_1;
  DAT_febf6cd1 = param_1;
  return;
}

void FUN_00079a0e(void)

{
  DAT_febf6cd4 = 0xff;
  DAT_febf6cd3 = 0xff;
  DAT_febf6cd2 = 1;
  f33_nvm_service_guards.deferred = 0xff;
  f33_nvm_service_guards.paired_call = '\x01';
  f33_nvm_service_guards.service = '\x01';
  FUN_0007987e(0);
  return;
}

undefined1 FUN_00079ad4(void)

{
  if (DAT_febf6cd0 != DAT_febf6cd1) {
    return 1;
  }
  return 0;
}

undefined1 FUN_00079af0(void)

{
  int iVar1;
  
  iVar1 = FUN_00079ad4();
  if (iVar1 != 0) {
    FUN_0007987e(0);
  }
  return DAT_febf6cd0;
}

bool FUN_00079b0e(void)

{
  return DAT_febf6cd0 != '\0';
}

void FUN_00079b1e(void)

{
  DAT_febf6cdb = 0;
  f33_nvm_service_mode_nonzero = '\0';
  DAT_febf6cd9 = 0;
  DAT_febf6cd6 = 0xffff;
  DAT_febf6cd8 = 0xff;
  FUN_00079c6c();
  FUN_00079638();
  FUN_00079a0e();
  return;
}

undefined1 FUN_00079b5c(void)

{
  return DAT_febf6cd8;
}

undefined2 FUN_00079b66(void)

{
  return DAT_febf6cd6;
}

undefined4 FUN_00079b70(void)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = FUN_000741a0();
  if (iVar1 == 2) {
    uVar2 = 0x1e;
  }
  else if ((iVar1 == 4) ||
          ((iVar1 = FUN_00079c94(), iVar1 == 0 && (iVar1 = thunk_FUN_00076688(), iVar1 != 1)))) {
    uVar2 = 0xf0;
  }
  else {
    uVar2 = 0xf;
  }
  return uVar2;
}

void FUN_00079be8(undefined1 param_1)

{
  DAT_febf6cd8 = param_1;
  FUN_0007969a((uint)(byte)param_1);
  return;
}

void FUN_00079bfe(undefined4 param_1,char param_2)

{
  if ((param_2 != '\f') && (param_2 != '\r')) {
    DAT_febf6cd8 = 0xff;
  }
  DAT_febf6cd6 = 0xffff;
  ((void)(param_2), f33_return_only_stub_796ba());
  return;
}

void FUN_00079c2a(undefined1 param_1)

{
  DAT_febf6cd8 = 0xff;
  ((void)(param_1), f33_return_only_stub_796bc());
  return;
}

void FUN_00079c42(undefined1 param_1)

{
  DAT_febf6cd9 = param_1;
  return;
}

void f33_nvm_store_service_mode_nonzero(uchar value)

{
  f33_nvm_service_mode_nonzero = value;
  return;
}

void FUN_00079c56(undefined1 param_1)

{
  DAT_febf6cdb = param_1;
  return;
}

void FUN_00079c6c(void)

{
  f33_nvm_direct_operation_mode = '\0';
  return;
}

uchar FUN_00079c76(void)

{
  uchar uVar1;
  int iVar2;
  
  iVar2 = FUN_00079af0();
  uVar1 = 'U';
  if (iVar2 == 0) {
    uVar1 = f33_nvm_direct_operation_mode;
  }
  return uVar1;
}

uchar FUN_00079c94(void)

{
  return f33_nvm_direct_operation_mode;
}

bool FUN_00079d12(void)

{
  int iVar1;
  
  iVar1 = FUN_0006a192();
  return iVar1 != 0;
}

undefined4 f33_return_const_0_79d24(void)

{
  return 0;
}

undefined4 f33_return_const_0_79d28(void)

{
  return 0;
}

uint f33_nvm_driver_gate_hook(void)

{
  return 0;
}

bool FUN_00079d46(void)

{
  int iVar1;
  
  iVar1 = FUN_00068f64();
  return iVar1 == 0x5a;
}

void FUN_00079f42(void)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = (uint)DAT_00021865;
  for (uVar1 = 0; uVar1 < uVar2; uVar1 = uVar1 + 1 & 0xff) {
    f33_upper_network_software_indication[uVar1] = '\0';
  }
  return;
}

void FUN_00079f9a(uint param_1)

{
  if ((param_1 & 0xff) < (uint)DAT_00021865) {
    f33_upper_network_software_indication[param_1 & 0xff] = '\x01';
    f33_return_only_stub_7be4c();
  }
  return;
}

void FUN_00079fba(uint param_1)

{
  if ((param_1 & 0xff) < (uint)DAT_00021865) {
    f33_upper_network_software_indication[param_1 & 0xff] = '\x03';
    f33_return_only_stub_7be4a();
  }
  return;
}

void FUN_0007a0dc(void)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = (uint)DAT_00021864;
  for (uVar1 = 0; uVar1 < uVar2; uVar1 = uVar1 + 1 & 0xff) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe3deau + (uint32_t)(uVar1) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe3decu + (uint32_t)(uVar1) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe3deeu + (uint32_t)(uVar1) * 1u)))) = 0;
  }
  return;
}

uint f33_cantp_multiply_receive_block_capacity(uchar cf_payload_capacity,uchar block_size)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = 0;
  uVar1 = 0;
  do {
    if ((1 << (uVar1 & 0x1f) & 0xffU & (uint)block_size) != 0) {
      uVar2 = uVar2 + ((uint)cf_payload_capacity << (uVar1 & 0x1f)) & 0xffff;
    }
    uVar1 = uVar1 + 1;
  } while (uVar1 < 8);
  return uVar2;
}

uint f33_cantp_select_receive_flow_status
               (uint remaining,uint available,uchar cf_payload_capacity,uchar block_size)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = 0xe1;
  uVar1 = remaining;
  if ((block_size != '\0') &&
     (uVar1 = f33_cantp_multiply_receive_block_capacity(cf_payload_capacity,block_size),
     remaining <= uVar1)) {
    uVar1 = remaining;
  }
  if (uVar1 <= available) {
    uVar2 = 0xf0;
  }
  return uVar2;
}

void f33_cantp_tick_channel_timeouts(void)

{
  byte bVar1;
  ushort uVar2;
  ushort uVar3;
  uint32_t puVar4;
  uint32_t puVar5;
  int iVar6;
  uint uVar7;
  ushort uVar8;
  
  puVar4 = 0xfebeb800u;
  puVar5 = 0x23dfcu;
  if (((int8_t)DAT_febe4f3d) == -0x56) {
    iVar6 = camry_host_addr(FUN_0007a32e());
    if (iVar6 != 0) {
      bVar1 = (*((byte *)camry_host_ptr((uint32_t)(iVar6 + 0xc))));
      uVar2 = (*((ushort *)camry_host_ptr((uint32_t)(puVar5 + -0x11b8))));
      for (uVar7 = 0; uVar7 < bVar1; uVar7 = uVar7 + 1 & 0xff) {
        iVar6 = uVar7 * 0x20;
        uVar3 = (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + iVar6 + -0x68aa))));
        uVar8 = (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + iVar6 + -0x68ba))));
        if (uVar2 < uVar3) {
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x68c4))))) = 0xf;
          uVar3 = 0;
        }
        else if (uVar3 != 0) {
          uVar3 = uVar3 - 1;
        }
        if (uVar2 < uVar8) {
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x68c4))))) = 0xf;
          uVar8 = 0;
        }
        else if (uVar8 != 0) {
          uVar8 = uVar8 - 1;
        }
        (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + iVar6 + -0x68aa)))) = uVar3;
        (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + iVar6 + -0x68ba)))) = uVar8;
      }
    }
  }
  else if (DAT_febe4f3d != 'U') {
    DAT_febe4f3c = 0xf;
  }
  return;
}

byte FUN_0007bb9c(void)

{
  uint32_t puVar1;
  byte bVar2;
  
  puVar1 = 0xfebeb800u;
  bVar2 = FUN_0007be2e(DAT_00021866);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6853))))) = 0xff;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6854))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6852))))) = bVar2;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6851))))) = bVar2 ^ 0xff;
  return bVar2;
}

byte FUN_0007bc42(void)

{
  byte bVar1;
  
  bVar1 = DAT_febe4fac;
  if ((DAT_febe4fad ^ DAT_febe4fac) != 0xff) {
    bVar1 = 0;
  }
  return bVar1;
}

void FUN_0007bcf4(byte param_1)

{
  if (param_1 < DAT_00021865) {
    FUN_0007e4ea((uint)(byte)param_1);
  }
  return;
}

byte FUN_0007bd3a(uint param_1)

{
  byte bVar1;
  byte bVar2;
  
  bVar2 = 0;
  if (((param_1 & 0xff) < (uint)DAT_00021865) &&
     ((bVar1 = f33_upper_network_software_indication[param_1 & 0xff], bVar1 < 2 || (bVar1 == 3)))) {
    bVar2 = bVar1;
  }
  return bVar2;
}

undefined1 FUN_0007be2e(undefined1 param_1)

{
  return param_1;
}

undefined4 f33_return_const_0_7be42(void)

{
  return 0;
}

void FUN_0007c0e8(void)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = (uint)DAT_0002183c;
  for (uVar1 = 0; uVar1 < uVar2; uVar1 = uVar1 + 1 & 0xff) {
    ((volatile F33RequestedNormalNetworkPolicy *)camry_host_ptr(0xfebe3de0u))[uVar1].remaining_delay = 0;
    ((volatile F33RequestedNormalNetworkPolicy *)camry_host_ptr(0xfebe3de0u))[uVar1].requested_policy = '\x1e';
    ((volatile F33RequestedNormalNetworkPolicy *)camry_host_ptr(0xfebe3de0u))[uVar1].reconciled_software_policy = '\x0f';
  }
  return;
}

uint f33_request_normal_network_policy_disable(uchar network)

{
  bool bVar1;
  uchar uVar2;
  uint uVar3;
  
  uVar3 = 0x12;
  uVar2 = ((volatile F33RequestedNormalNetworkPolicy *)camry_host_ptr(0xfebe3de0u))[(uint)network - (uint)DAT_0002183d & 0xff].
          requested_policy;
  bVar1 = uVar2 == '\x1e';
  if (bVar1) {
    uVar2 = '\x0f';
  }
  ((volatile F33RequestedNormalNetworkPolicy *)camry_host_ptr(0xfebe3de0u))[(uint)network - (uint)DAT_0002183d & 0xff].requested_policy
       = uVar2;
  if (bVar1) {
    uVar3 = 0;
  }
  return uVar3;
}

void FUN_0007c2d6(uint param_1)

{
  ushort uVar1;
  
  uVar1 = ((volatile F33RequestedNormalNetworkPolicy *)camry_host_ptr(0xfebe3de0u))[param_1 & 0xff].remaining_delay;
  if (uVar1 != 0) {
    uVar1 = uVar1 - 1;
  }
  ((volatile F33RequestedNormalNetworkPolicy *)camry_host_ptr(0xfebe3de0u))[param_1 & 0xff].remaining_delay = uVar1;
  return;
}

undefined1 FUN_0007c604(undefined4 param_1,undefined1 param_2)

{
  return param_2;
}

uint FUN_0007c60e(uint param_1)

{
  uint uVar1;
  
  uVar1 = (uint)((param_1 & 1) != 0);
  if ((param_1 >> 1 & 1) != 0) {
    uVar1 = uVar1 | 2;
  }
  if ((param_1 >> 2 & 1) != 0) {
    uVar1 = uVar1 | 4;
  }
  if ((param_1 >> 5 & 1) != 0) {
    uVar1 = uVar1 | 0x20;
  }
  if ((param_1 >> 7 & 1) != 0) {
    uVar1 = uVar1 | 0x80;
  }
  if ((param_1 >> 8 & 1) != 0) {
    uVar1 = uVar1 | 0x100;
  }
  if ((param_1 >> 9 & 1) != 0) {
    uVar1 = uVar1 | 0x200;
  }
  return uVar1;
}

uint FUN_0007c6e8(undefined2 param_1)

{
  uint32_t puVar1;
  uint uVar2;
  
  puVar1 = 0x23dfcu;
  uVar2 = FUN_000813e4(param_1);
  if (uVar2 < (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x25c0)))))) {
    uVar2 = (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x25bf))))) + uVar2 & 0xff;
  }
  else {
    uVar2 = 0xff;
  }
  return uVar2;
}

void FUN_0007cd12(void)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = (uint)DAT_00021ba8;
  for (uVar1 = 0; uVar1 < uVar2; uVar1 = uVar1 + 1 & 0xff) {
    ((volatile F33SelectedNetworkRecoveryState *)camry_host_ptr(0xfebe491cu))[uVar1].remaining_hold = 0;
    ((volatile F33SelectedNetworkRecoveryState *)camry_host_ptr(0xfebe491cu))[uVar1].recovery_state = 0xff;
    ((volatile F33SelectedNetworkRecoveryState *)camry_host_ptr(0xfebe491cu))[uVar1].aggregated_cause = 0;
    ((volatile F33SelectedNetworkRecoveryState *)camry_host_ptr(0xfebe491cu))[uVar1].reported_fault_class = '\x03';
    ((volatile F33SelectedNetworkRecoveryState *)camry_host_ptr(0xfebe491cu))[uVar1].uninterpreted = '\0';
  }
  return;
}

undefined4 FUN_0007cda0(char param_1)

{
  undefined4 uVar1;
  int iVar2;
  
  iVar2 = ((void)(DAT_00021ba9 + param_1), f33_return_const_0_7cf74());
  uVar1 = 0;
  if (iVar2 != 0) {
    uVar1 = 0x80;
  }
  return uVar1;
}

undefined4 f33_return_const_0_7cf74(void)

{
  return 0;
}

int FUN_0007cf78(undefined4 param_1,short param_2)

{
  return (int)param_2;
}

undefined4 f33_return_const_0_7cf7e(void)

{
  return 0;
}

uint FUN_0007cf86(uint param_1)

{
  uint uVar1;
  
  uVar1 = (uint)((param_1 & 1) != 0);
  if ((param_1 >> 1 & 1) != 0) {
    uVar1 = uVar1 | 2;
  }
  if ((param_1 >> 2 & 1) != 0) {
    uVar1 = uVar1 | 4;
  }
  if ((param_1 >> 5 & 1) != 0) {
    uVar1 = uVar1 | 0x20;
  }
  if ((param_1 >> 7 & 1) != 0) {
    uVar1 = uVar1 | 0x80;
  }
  if ((param_1 & 0x300) != 0) {
    uVar1 = uVar1 | 0x200;
  }
  if ((param_1 >> 3 & 1) == 0) {
    if ((param_1 >> 4 & 1) == 0) {
      if ((param_1 >> 6 & 1) != 0) {
        uVar1 = uVar1 | 0x40;
      }
      return uVar1;
    }
    return uVar1 | 0x10;
  }
  return uVar1 | 8;
}

byte FUN_0007d0ea(uint param_1)

{
  uchar *puVar1;
  byte bVar2;
  
  param_1 = param_1 & 0xffff;
  bVar2 = f33_com_tx_pdu_flags[param_1] & 0x33;
  if (param_1 < DAT_00021c56) {
    puVar1 = f33_com_tx_pending_and_group_state + 3;
  }
  else {
    puVar1 = ((undefined *)camry_host_ptr(0xfebe4a42u));
  }
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22148u + (uint32_t)(param_1) * 1u)))) & puVar1[(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x226c2u + (uint32_t)(param_1 * 8) * 1u))))]) != 0) {
    bVar2 = bVar2 | 0x80;
  }
  return bVar2;
}

void FUN_0007d646(int param_1)

{
  undefined1 uVar1;
  uint uVar2;
  uint uVar3;
  
  uVar3 = (uint)DAT_00021c6e;
  for (uVar2 = 0; uVar2 < uVar3; uVar2 = uVar2 + 1 & 0xff) {
    uVar1 = (*((undefined1 *)camry_host_ptr((uint32_t)(uVar2 + uVar3 + param_1))));
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a43u + (uint32_t)(uVar2) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a44u + (uint32_t)(uVar2) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a41u + (uint32_t)(uVar2) * 1u)))) = uVar1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a42u + (uint32_t)(uVar2) * 1u)))) = uVar1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a45u + (uint32_t)(uVar2) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a46u + (uint32_t)(uVar2) * 1u)))) = 0;
  }
  return;
}

void FUN_0007d67c(void)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = (uint)DAT_00021c6e;
  for (uVar1 = 0; uVar1 < uVar2; uVar1 = uVar1 + 1 & 0xff) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a42u + (uint32_t)(uVar1) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a44u + (uint32_t)(uVar1) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a46u + (uint32_t)(uVar1) * 1u)))) = 0;
  }
  return;
}

void FUN_0007d69e(int param_1)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = (uint)DAT_00021c6e;
  for (uVar1 = 0; uVar1 < uVar2; uVar1 = uVar1 + 1 & 0xff) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a43u + (uint32_t)(uVar1) * 1u)))) = (*((undefined1 *)camry_host_ptr((uint32_t)(uVar2 + uVar1 + param_1))));
  }
  return;
}

void FUN_0007d6c2(int param_1)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = (uint)DAT_00021c6e;
  for (uVar1 = 0; uVar1 < uVar2; uVar1 = uVar1 + 1 & 0xff) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a45u + (uint32_t)(uVar1) * 1u)))) = (*((undefined1 *)camry_host_ptr((uint32_t)(uVar2 + uVar1 + param_1))));
  }
  return;
}

undefined4 f33_return_const_1_7d800(void)

{
  return 1;
}

void FUN_0007d88e(void)

{
  FUN_0007e3bc();
  FUN_0007d67c();
  return;
}

undefined4 FUN_0007dab6(uint param_1,char param_2)

{
  uchar *puVar1;
  
  if (param_2 == '\0') {
    puVar1 = f33_com_tx_pending_and_group_state + 1;
  }
  else {
    puVar1 = f33_com_tx_pending_and_group_state;
  }
  puVar1[param_1 >> 3 & 0xff] = puVar1[param_1 >> 3 & 0xff] | (byte)(1 << (param_1 & 7));
  return 0;
}

uint FUN_0007dae0(uint param_1,uint param_2,uint param_3)

{
  param_3 = param_3 & 0xffff;
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x226c6u + (uint32_t)((param_2 & 0xffff) * 8) * 1u)))) & 4) != 0) &&
     (f33_com_tx_pending_and_group_state[(param_1 & 0xff) + 5] == '\x01')) {
    param_3 = FUN_0007e4e0((uint)(byte)param_1, (uint)(ushort)param_2, (uint)(ushort)param_3);
  }
  return param_3;
}

void FUN_0007dee6(uint param_1)

{
  byte bVar1;
  uint uVar2;
  
  uVar2 = param_1 >> 3 & 0xff;
  bVar1 = (byte)(1 << (param_1 & 7)) ^ 0xff;
  f33_com_tx_pending_and_group_state[uVar2] = f33_com_tx_pending_and_group_state[uVar2] & bVar1;
  f33_com_tx_pending_and_group_state[uVar2 + 1] =
       f33_com_tx_pending_and_group_state[uVar2 + 1] & bVar1;
  return;
}

void FUN_0007e2ea(uint param_1)

{
  uint uVar1;
  int iVar2;
  uint uVar3;
  
  iVar2 = (param_1 & 0xff) * 4;
  uVar3 = (uint)*(ushort *)(((undefined *)camry_host_ptr(0x22140u)) + iVar2);
  uVar1 = *(ushort *)(((undefined *)camry_host_ptr(0x22142u)) + iVar2) + uVar3;
  for (; uVar3 < (uVar1 & 0xffff); uVar3 = uVar3 + 1 & 0xffff) {
    f33_com_tx_periodic_countdowns[uVar3] = 0;
  }
  return;
}

void FUN_0007e312(void)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = (uint)DAT_00021c70;
  for (uVar1 = 0; uVar1 < uVar2; uVar1 = uVar1 + 1 & 0xff) {
    f33_com_tx_inhibit_pair[uVar1 + 1] = 0xff;
    f33_com_tx_inhibit_pair[uVar1] = '\0';
    f33_com_tx_pending_and_group_state[uVar1 + 1] = '\0';
    f33_com_tx_pending_and_group_state[uVar1] = '\0';
  }
  DAT_febe4fb1 = 0;
  return;
}

void FUN_0007e33e(void)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = 1;
  if (DAT_00021c6f == '\0') {
    uVar2 = (uint)DAT_00021c6e;
  }
  for (uVar1 = 0; uVar1 < uVar2; uVar1 = uVar1 + 1 & 0xff) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a37u + (uint32_t)(uVar1) * 1u)))) = 2;
  }
  return;
}

void FUN_0007e364(void)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = (uint)DAT_00021c56;
  for (uVar1 = 0; uVar1 < uVar2; uVar1 = uVar1 + 1 & 0xffff) {
    f33_com_tx_minimum_delay_countdowns[uVar1] = 0;
  }
  return;
}

void FUN_0007e380(int param_1)

{
  uchar uVar1;
  uint uVar2;
  uint uVar3;
  
  uVar3 = (uint)DAT_00021c6e;
  for (uVar2 = 0; uVar2 < uVar3; uVar2 = uVar2 + 1 & 0xff) {
    uVar1 = (*((uchar *)camry_host_ptr((uint32_t)(uVar2 + param_1))));
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a3fu + (uint32_t)(uVar2) * 1u)))) = 0;
    f33_com_tx_pending_and_group_state[uVar2 + 2] = uVar1;
    f33_com_tx_pending_and_group_state[uVar2 + 3] = uVar1;
    f33_com_tx_pending_and_group_state[uVar2 + 4] = '\x02';
    f33_com_tx_pending_and_group_state[uVar2 + 5] = '\x02';
    *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe4986u)) + uVar2 * 2) = 0;
  }
  return;
}

undefined4 f33_return_const_1_7e4dc(void)

{
  return 1;
}

undefined2 FUN_0007e4e0(undefined4 param_1,undefined4 param_2,undefined2 param_3)

{
  return param_3;
}

void FUN_0007e4ea(uint param_1)

{
  if ((param_1 & 0xff) < (uint)DAT_00021c6e) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a37u + (uint32_t)(param_1 & 0xff) * 1u)))) = 1;
  }
  return;
}

undefined4 f33_return_const_fffffff3_7e590(void)

{
  return 0xfffffff3;
}

undefined4 f33_return_const_0_7e722(void)

{
  return 0;
}

undefined4 f33_return_const_0_7e726(void)

{
  return 0;
}

undefined4 f33_return_const_1_7e77e(void)

{
  return 1;
}

void FUN_0007e7da(void)

{
  DAT_febe4938 = 0xff;
  return;
}

bool FUN_0007e7e4(uint param_1)

{
  if ((param_1 & 0xff) < (uint)DAT_00021be1) {
    return ((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x21be2u + (uint32_t)(param_1 & 0xff) * 1u)))) & DAT_febe493a) != 0;
  }
  return false;
}

void FUN_0007ead0(uint param_1,char param_2)

{
  undefined2 uVar1;
  
  if ((param_1 & 0xff) < (uint)DAT_00021be1) {
    uVar1 = 0x1fe;
    if (param_2 == '\0') {
      uVar1 = 0xff;
    }
    *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe492cu)) + (param_1 & 0xff) * 0x10) = uVar1;
  }
  return;
}

bool FUN_0007eb7c(uint param_1)

{
  uint32_t puVar1;
  int iVar2;
  bool bVar3;
  
  puVar1 = 0xfebeb800u;
  param_1 = param_1 & 0xff;
  bVar3 = false;
  if ((param_1 < DAT_00021be1) && (iVar2 = FUN_0007e7e4(param_1), iVar2 == 1)) {
    bVar3 = (*((short *)camry_host_ptr((uint32_t)(puVar1 + param_1 * 0x10 + -0x6ed4)))) == 0x1fe;
  }
  return bVar3;
}

void FUN_0007ed16(uint param_1)

{
  if ((param_1 & 0xff) < (uint)DAT_00021be1) {
    *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe492eu)) + (param_1 & 0xff) * 0x10) = 0x1fe;
  }
  return;
}

void FUN_0007ed2e(uint param_1)

{
  if ((param_1 & 0xff) < (uint)DAT_00021be1) {
    *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe492eu)) + (param_1 & 0xff) * 0x10) = 0xff;
  }
  return;
}

void FUN_0007ed4e(uint param_1)

{
  if ((param_1 & 0xff) < (uint)DAT_00021be1) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4937u + (uint32_t)((param_1 & 0xff) * 0x10) * 1u)))) = 0xe1;
  }
  return;
}

undefined4 f33_return_const_0_7ed68(void)

{
  return 0;
}

undefined4 f33_return_const_0_7ed6c(void)

{
  return 0;
}

undefined4 f33_return_const_0_7ed70(void)

{
  return 0;
}

undefined4 f33_return_const_1_7ed7c(void)

{
  return 1;
}

void FUN_0007ed80(void)

{
  short sVar1;
  short sVar2;
  uint uVar3;
  uint uVar4;
  
  uVar3 = (uint)DAT_00021be1;
  for (uVar4 = 0; uVar4 < uVar3; uVar4 = uVar4 + 1 & 0xff) {
    sVar1 = *(short *)(((undefined *)camry_host_ptr(0xfebe4928u)) + uVar4 * 0x10);
    if (sVar1 != 0) {
      sVar2 = sVar1 + -1;
      if (*(ushort *)(((undefined *)camry_host_ptr(0x21bdeu)) + uVar4 * 2) < (ushort)(sVar1 - 1U)) {
        sVar2 = 0;
      }
      *(short *)(((undefined *)camry_host_ptr(0xfebe4928u)) + uVar4 * 0x10) = sVar2;
    }
  }
  return;
}

void FUN_0007ef1a(byte param_1)

{
  if (param_1 < DAT_00021c7c) {
    FUN_0008344e((uint)(byte)param_1);
  }
  return;
}

void FUN_0007f098(uint param_1)

{
  int iVar1;
  int iVar2;
  ushort uVar3;
  
  iVar1 = (param_1 & 0xff) * 8;
  uVar3 = *(ushort *)(((undefined *)camry_host_ptr(0xfebe4916u)) + iVar1);
  if (uVar3 != 0) {
    iVar2 = (param_1 & 0xff) * 2;
    uVar3 = uVar3 - 1;
    if (*(ushort *)(((undefined *)camry_host_ptr(0x21b8cu)) + iVar2) < uVar3) {
      uVar3 = *(ushort *)(((undefined *)camry_host_ptr(0x21b8cu)) + iVar2);
    }
  }
  *(ushort *)(((undefined *)camry_host_ptr(0xfebe4916u)) + iVar1) = uVar3;
  return;
}

undefined4 FUN_0007f56a(uint param_1)

{
  uint32_t puVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  
  puVar1 = 0x23dfcu;
  if ((f33_logical_controller_request_cache[param_1 & 0xff] == 0x57a8) ||
     (f33_logical_controller_request_cache[param_1 & 0xff] == 0x6b94)) {
    uVar3 = (uint)DAT_00021971;
    for (uVar4 = 0; uVar4 < uVar3; uVar4 = uVar4 + 1 & 0xff) {
      if (((param_1 & 0xff) == (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(uVar4 - 0x2484)))))) &&
         (iVar2 = FUN_000841fc(uVar4), iVar2 != 0)) {
        return 1;
      }
    }
  }
  return 0;
}

undefined4 FUN_0007f6a4(char param_1)

{
  undefined8 uVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  
  uVar1 = 0x23dfc00000000;
  uVar3 = (uint)DAT_00021971;
  uVar4 = 0;
  while( true ) {
    if (uVar3 <= uVar4) {
      return 0;
    }
    if ((param_1 == (*((char *)camry_host_ptr((uint32_t)(uVar4 + (int)((ulonglong)uVar1 >> 0x20) + -0x2484))))) &&
       (iVar2 = ((void)(uVar4), f33_return_const_1_83598()), iVar2 == 0)) break;
    uVar4 = uVar4 + 1 & 0xff;
  }
  return 1;
}

undefined4 FUN_0007fbb0(uint param_1)

{
  ushort uVar1;
  
  uVar1 = f33_logical_controller_request_cache[param_1 & 0xff];
  if (uVar1 == 0x57a8) {
    return 3;
  }
  if (uVar1 != 0x6b94) {
    if (uVar1 != 0x6d92) {
      return 0;
    }
    return 1;
  }
  return 2;
}

bool FUN_0008037a(uint param_1,byte param_2)

{
  bool bVar1;
  
  param_1 = param_1 & 0xff;
  bVar1 = true;
  if (param_1 < DAT_00021970) {
    if ((param_2 < (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x21972u + (uint32_t)(param_1) * 1u))))) &&
       (f33_logical_controller_request_cache[param_1] == 0x57a8)) {
      bVar1 = *(short *)(((undefined *)camry_host_ptr(0xfebe48feu)) + param_1 * 2) != 0x5555;
    }
  }
  return bVar1;
}

void FUN_00080bc2(void)

{
  int iVar1;
  uint uVar2;
  undefined *puVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  
  uVar4 = (uint)DAT_00021970;
  for (uVar2 = 0; uVar2 < uVar4; uVar2 = uVar2 + 1 & 0xff) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe490fu + (uint32_t)(uVar2) * 1u)))) = 0;
    iVar1 = (int)(short)uVar2;
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe48f8u + (uint32_t)(iVar1 * 3) * 2u)))) = 0;
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe48fau + (uint32_t)(iVar1 * 3) * 2u)))) = 0;
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe48fcu + (uint32_t)(iVar1 * 3) * 2u)))) = 0;
    uVar6 = 0;
    uVar5 = (uint)*(ushort *)(((undefined *)camry_host_ptr(0x21966u)) + uVar2 * 2);
    if (uVar5 == 0) {
      uVar5 = 1;
    }
    puVar3 = ((void *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21904u + (uint32_t)(uVar2) * 4u)))))));
    for (; uVar6 < uVar5; uVar6 = uVar6 + 1 & 0xffff) {
      *(undefined4 *)(puVar3 + uVar6 * 4) = 0;
    }
  }
  DAT_febe4ff4 = 0xffffffff;
  return;
}

uint FUN_00080d76(uint param_1)

{
  uint uVar1;
  
  uVar1 = (uint)((param_1 & 0xc0) != 0x40);
  if ((param_1 & 0x30) != 0x10) {
    uVar1 = uVar1 | 0x80;
  }
  if ((param_1 & 0xc) != 4) {
    uVar1 = uVar1 | 2;
  }
  if ((param_1 & 3) != 1) {
    uVar1 = uVar1 | 0x20;
  }
  if ((param_1 & 0x300) != 0x100) {
    uVar1 = uVar1 | 0x100;
  }
  if (uVar1 == 0) {
    uVar1 = 0x20;
  }
  return uVar1;
}

void FUN_00080f5a(uint param_1,undefined1 param_2)

{
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4912u + (uint32_t)(param_1 & 0xff) * 1u)))) = param_2;
  return;
}

undefined4 FUN_00080f6c(uint param_1,byte param_2)

{
  undefined1 uVar1;
  undefined4 uVar2;
  
  uVar2 = 1;
  if (((param_1 & 0xff) < (uint)DAT_00021970) &&
     ((uVar1 = 0x5a, param_2 == 3 || (uVar1 = 0x69, param_2 < 2)))) {
    uVar2 = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4903u + (uint32_t)(param_1 & 0xff) * 1u)))) = uVar1;
  }
  return uVar2;
}

undefined4 f33_return_const_0_814ae(void)

{
  return 0;
}

void FUN_0008156c(uint param_1)

{
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4911u + (uint32_t)(param_1 & 0xff) * 1u)))) = 0x55;
  return;
}

undefined4 f33_return_const_1_8158a(void)

{
  return 1;
}

undefined4 f33_return_const_1_816b0(void)

{
  return 1;
}

undefined4 f33_return_const_1_816b4(void)

{
  return 1;
}

undefined4 f33_return_const_1_816b8(void)

{
  return 1;
}

undefined4 f33_return_const_0_81f62(void)

{
  return 0;
}

undefined4 f33_return_const_0_81ffa(void)

{
  return 0;
}

void FUN_000821a6(undefined1 param_1)

{
  DAT_febe5004 = param_1;
  DAT_febe5005 = 1;
  return;
}

undefined1 FUN_000821ca(void)

{
  return DAT_febe5005;
}

undefined1 FUN_000821d0(void)

{
  return DAT_febe5004;
}

void FUN_00082288(undefined4 param_1)

{
  DAT_febe5000 = param_1;
  return;
}

undefined4 FUN_0008228e(void)

{
  return DAT_febe5000;
}

undefined4 FUN_00082494(void)

{
  uint uVar1;
  
  uVar1 = 0;
  while( true ) {
    if (DAT_00022ae7 <= uVar1) {
      return 0;
    }
    if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4ce1u + (uint32_t)(uVar1 * 8) * 1u)))) & 1) != 0) break;
    uVar1 = uVar1 + 1 & 0xff;
  }
  return 1;
}

undefined4 FUN_0008277a(void)

{
  int iVar1;
  uint uVar2;
  undefined4 uVar3;
  
  uVar3 = 0;
  uVar2 = 0;
  while( true ) {
    if (DAT_00022ae7 <= uVar2) {
      return uVar3;
    }
    iVar1 = uVar2 * 8;
    if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4ce1u + (uint32_t)(iVar1) * 1u)))) & 4) != 0) &&
       ((uVar3 = 1, *(short *)(((undefined *)camry_host_ptr(0xfebe4cdcu)) + iVar1) == 0 ||
        (DAT_00022ae8 <= (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4ce2u + (uint32_t)(iVar1) * 1u)))))))) break;
    uVar2 = uVar2 + 1 & 0xff;
  }
  return 0;
}

uint FUN_00082a3c(uint param_1)

{
  param_1 = param_1 & 0xff;
  if (0x33 < param_1) {
    return (int)(param_1 + 1) >> 1 | 0x700;
  }
  return (short)param_1 * 5 | 0x600;
}

uint FUN_00082f18(undefined1 param_1,char param_2)

{
  undefined1 uVar1;
  uint32_t puVar2;
  uint32_t puVar3;
  uint uVar4;
  
  puVar2 = 0xfebeb800u;
  puVar3 = 0x23dfcu;
  uVar4 = FUN_00082e54(param_1);
  if (uVar4 < (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x1340)))))) {
    uVar1 = 0x69;
    if (param_2 == '\x01') {
      uVar1 = 0x5a;
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(uVar4 - 0x691a))))) = uVar1;
  }
  return uVar4;
}

void FUN_00082f44(undefined1 param_1,int param_2,undefined2 param_3)

{
  undefined4 *puVar1;
  int iVar2;
  uint uVar3;
  ushort uVar4;
  uint uVar5;
  uint uVar6;
  uint uVar7;
  uint uVar8;
  
  uVar6 = (uint)DAT_00022abe;
  uVar3 = (uint)DAT_febe500c;
  uVar8 = (uint)DAT_febe500d;
  if ((uVar3 < uVar6) && (uVar8 < uVar6)) {
    uVar5 = (uint)DAT_00022abf;
    uVar4 = (ushort)DAT_00022abf;
    for (uVar7 = 0; uVar7 < uVar5; uVar7 = uVar7 + 1 & 0xff) {
      puVar1 = ((undefined4 *)camry_host_ptr((uint32_t)(uVar7 * 8 + param_2)));
      iVar2 = (uVar7 + (int)(short)uVar4 * (int)(short)(ushort)DAT_febe500c) * 8;
      *(undefined4 *)(((undefined *)camry_host_ptr(0xfebe4c3cu)) + iVar2) = *puVar1;
      *(undefined4 *)(((undefined *)camry_host_ptr(0xfebe4c40u)) + iVar2) = puVar1[1];
    }
    *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe4ec0u)) + uVar3 * 2) = param_3;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4ee7u + (uint32_t)(uVar3) * 1u)))) = param_1;
    uVar3 = uVar3 + 1 & 0xff;
    if (uVar6 <= uVar3) {
      uVar3 = 0;
    }
    if ((uVar3 == uVar8) && (DAT_febe500d = (byte)(uVar8 + 1), uVar6 <= (uVar8 + 1 & 0xff))) {
      DAT_febe500d = 0;
    }
    DAT_febe500c = (byte)uVar3;
  }
  return;
}

bool FUN_00083072(undefined1 param_1)

{
  return FUN_00083570(param_1);
}

void thunk_FUN_00082288(undefined4 param_1)

{
  FUN_00082288(param_1);
  return;
}

undefined4 thunk_FUN_0008228e(void)

{
  return FUN_0008228e();
}

bool FUN_00083172(void)

{
  return DAT_febe3df4 == '\x0f';
}

void FUN_000831be(uint param_1,undefined1 param_2,undefined1 param_3)

{
  uint uVar1;
  
  param_1 = param_1 & 0xff;
  uVar1 = (uint)DAT_00021865;
  if (param_1 < uVar1) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe3deau + (uint32_t)(param_1) * 1u)))) = param_2;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe3deau + (uint32_t)(param_1 + uVar1) * 1u)))) = param_3;
  }
  return;
}

void FUN_000831dc(uint param_1,undefined1 param_2)

{
  if ((param_1 & 0xff) < (uint)DAT_00021865) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe3decu + (uint32_t)((param_1 & 0xff) + (uint)DAT_00021865) * 1u)))) = param_2;
  }
  return;
}

void FUN_000831f0(uint param_1,undefined1 param_2)

{
  if ((param_1 & 0xff) < (uint)DAT_00021865) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe3deeu + (uint32_t)((param_1 & 0xff) + (uint)DAT_00021865) * 1u)))) = param_2;
  }
  return;
}

void FUN_00083282(char param_1)

{
  FUN_00079f9a(DAT_0002183d + param_1);
  return;
}

void FUN_00083298(char param_1)

{
  FUN_00079fba(DAT_0002183d + param_1);
  return;
}

void FUN_000833cc(void)

{
  DAT_febe4a47 = 0xa5;
  return;
}

void FUN_000833d6(void)

{
  DAT_febe4a47 = 0x5a;
  return;
}

undefined4 f33_return_const_1_833e0(void)

{
  return 1;
}

void FUN_0008344e(uint param_1)

{
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4935u + (uint32_t)((param_1 & 0xff) * 0x10) * 1u)))) = 0xe1;
  return;
}

bool FUN_00083570(char param_1)

{
  if (DAT_febe5005 == '\x01') {
    return DAT_febe5004 != param_1;
  }
  return true;
}

undefined4 f33_return_const_1_83598(void)

{
  return 1;
}

void FUN_0008359c(void)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = (uint)DAT_00022e41;
  for (uVar1 = 0; uVar1 < uVar2; uVar1 = uVar1 + 1 & 0xff) {
    f33_driver_bus_off_observation_latch[uVar1] = '<';
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5013u + (uint32_t)(uVar1) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5016u + (uint32_t)(uVar1) * 1u)))) = 0x5a;
  }
  return;
}

void FUN_000835c6(uint param_1)

{
  f33_driver_bus_off_observation_latch[param_1 & 0xff] = '<';
  return;
}

void FUN_0008366e(uint param_1)

{
  f33_driver_bus_off_observation_latch[param_1 & 0xff] = 'Z';
  return;
}

bool FUN_00083710(uint param_1)

{
  return (param_1 & 0xff) + ((int)(param_1 & 0xffff) >> 8) != 0xff;
}

void FUN_000837ac(uint param_1)

{
  if (((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5016u + (uint32_t)(param_1 & 0xff) * 1u))))) != -0x6a) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5016u + (uint32_t)(param_1 & 0xff) * 1u)))) = 'Z';
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5013u + (uint32_t)(param_1 & 0xff) * 1u)))) = 0;
  }
  FUN_00083c9c((uint)(byte)param_1);
  return;
}

void FUN_00083c72(void)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = (uint)DAT_00022ea4;
  for (uVar1 = 0; uVar1 < uVar2; uVar1 = uVar1 + 1 & 0xff) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5019u + (uint32_t)(uVar1) * 1u)))) = 0x5a;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe501cu + (uint32_t)(uVar1) * 1u)))) = 0xa5;
  }
  return;
}

undefined4 f33_return_const_1_83c98(void)

{
  return 1;
}

void FUN_00083cd6(uint param_1)

{
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe501cu + (uint32_t)(param_1 & 0xff) * 1u)))) = 0x5a;
  return;
}

bool FUN_000841fc(uint param_1)

{
  if (f33_driver_channel_software_states[param_1 & 0xff] != initialized) {
    return f33_driver_channel_software_states[param_1 & 0xff] != stopped_software_state;
  }
  return false;
}

void FUN_000842dc(void)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = (uint)DAT_00022ea4;
  for (uVar1 = 0; uVar1 < uVar2; uVar1 = uVar1 + 1 & 0xff) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5026u + (uint32_t)(uVar1) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22eabu + (uint32_t)(uVar1) * 1u))));
  }
  return;
}

void FUN_000850c2(void)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = (uint)DAT_00022e3e;
  for (uVar1 = 0; uVar1 < uVar2; uVar1 = uVar1 + 1 & 0xffff) {
    *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe502au)) + uVar1 * 2) = 0xffff;
  }
  return;
}

void FUN_000850e0(uint param_1)

{
  uint uVar1;
  int iVar2;
  uint uVar3;
  
  iVar2 = (param_1 & 0xff) * 8;
  uVar3 = (uint)*(ushort *)(((undefined *)camry_host_ptr(0x22e44u)) + iVar2) - (uint)DAT_00022e3c & 0xffff;
  uVar1 = (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22e48u + (uint32_t)(iVar2) * 1u)))) + uVar3;
  for (; uVar3 < (uVar1 & 0xffff); uVar3 = uVar3 + 1 & 0xffff) {
    *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe502au)) + uVar3 * 2) = 0xffff;
  }
  return;
}

undefined4 FUN_0008834a(void)

{
  undefined4 uVar1;
  
  if (((int8_t)DAT_febf10f0) != -0x1f) {
    if (((int8_t)DAT_febf10f0) == -0x2e) {
      uVar1 = 0;
    }
    else {
      uVar1 = 2;
    }
    return uVar1;
  }
  return 0;
}

undefined4 FUN_00088b3a(void)

{
  undefined4 uVar1;
  
  if (((int8_t)DAT_febf11ac) != -0x1f) {
    if (((int8_t)DAT_febf11ac) == -0x2e) {
      uVar1 = 0;
    }
    else {
      uVar1 = 2;
    }
    return uVar1;
  }
  return 0;
}

undefined4 FUN_00088f7a(void)

{
  undefined4 uVar1;
  
  if (((int8_t)DAT_febf1204) != -0x1f) {
    if (((int8_t)DAT_febf1204) == -0x2e) {
      uVar1 = 0;
    }
    else {
      uVar1 = 2;
    }
    return uVar1;
  }
  return 0;
}

undefined4 FUN_00089386(void)

{
  undefined4 uVar1;
  
  if (((int8_t)DAT_febf1294) != -0x1f) {
    if (((int8_t)DAT_febf1294) == -0x2e) {
      uVar1 = 0;
    }
    else {
      uVar1 = 2;
    }
    return uVar1;
  }
  return 0;
}

void FUN_00089414(void)

{
  DAT_febf1370 = 0;
  DAT_febf1378 = 0xe1;
  DAT_febf1374 = 0xffffffff;
  return;
}

void FUN_0008961a(void)

{
  DAT_febf137c = 0;
  DAT_febf1384 = 0xe1;
  DAT_febf1380 = 0xffffffff;
  return;
}

void FUN_0008980c(void)

{
  DAT_febf1388 = 0;
  DAT_febf1390 = 0xe1;
  DAT_febf138c = 0xffffffff;
  return;
}

void FUN_000899fa(void)

{
  DAT_febf1394 = 0;
  DAT_febf139c = 0xe1;
  DAT_febf1398 = 0xffffffff;
  return;
}

undefined4 FUN_00089bb6(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  DAT_febf13a4 = param_2;
  DAT_febf13a8 = param_3;
  return 0;
}

undefined4 FUN_00089c8c(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  DAT_febf13b4 = param_2;
  DAT_febf13b8 = param_3;
  return 0;
}

void f33_fill_constant_block_8a450(void)

{
  DAT_febf131c = 0;
  DAT_febf1320 = 0;
  DAT_febf1324 = 0;
  DAT_febf1328 = 0;
  DAT_febf132c = 0;
  DAT_febf1330 = 0;
  DAT_febf1334 = 0;
  DAT_febf1338 = 0;
  DAT_febf133c = 0;
  DAT_febf1340 = 0;
  DAT_febf1344 = 0;
  DAT_febf1348 = 0;
  DAT_febf134c = 0;
  DAT_febf136d = 0;
  DAT_febf1360 = 0xffffffff;
  DAT_febf1364 = 0xffffffff;
  DAT_febf1368 = 0xffffffff;
  DAT_febf1350 = 0xffffffff;
  DAT_febf1354 = 0xffffffff;
  DAT_febf1358 = 0xffffffff;
  DAT_febf135c = 0xffffffff;
  return;
}

undefined4 FUN_0008b026(void)

{
  if (((((int8_t)DAT_febf136c) == -0x1f) || (((int8_t)DAT_febf136c) == -0x2e)) || (((int8_t)DAT_febf136c) == -0x3d)) {
    if (DAT_febf136d == '\0') {
      return 1;
    }
  }
  else if (DAT_febf136c == '\0') {
    return 0x1000;
  }
  return 0x2000;
}

void FUN_0008b070(void)

{
  uint uVar1;
  
  DAT_febf380a = 0;
  DAT_febf3810 = 0;
  DAT_febf380f = 0;
  DAT_febf380e = 0;
  DAT_febf3806 = 0;
  DAT_febf3804 = 0;
  DAT_febf380d = 0;
  DAT_febf380c = 0;
  DAT_febf3800 = 0;
  DAT_febf3808 = 0;
  DAT_febf3811 = 0;
  uVar1 = 0;
  do {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebf3812u + (uint32_t)(uVar1) * 1u)))) = 0;
    uVar1 = uVar1 + 1;
  } while (uVar1 < 0x300);
  return;
}

uint f33_check_diagnostic_addressing_admission(uchar addressing_flags)

{
  uint uVar1;
  
  uVar1 = f33_check_diagnostic_application_admission(addressing_flags & 1);
  return uVar1;
}

undefined4 f33_return_const_0_8b10c(void)

{
  return 0;
}

undefined4 f33_return_const_0_8b110(void)

{
  return 0;
}

int FUN_0008b17e(void)

{
  int iVar1;
  
  if (f33_app_programming_admission_latched == '\0') {
    iVar1 = FUN_0004d5d8();
    if (iVar1 == 0) {
      ((void)(0), FUN_0004d5fe());
      f33_app_programming_admission_latched = 'Z';
    }
  }
  else {
    iVar1 = 0;
  }
  return iVar1;
}

void f33_reset_write_did_transaction(void)

{
  DAT_febf3b25 = 0;
  DAT_febf3b20 = 0;
  DAT_febf3b1e = 0;
  DAT_febf3b23 = 1;
  DAT_febf3b22 = 1;
  DAT_febf3b21 = 0;
  DAT_febf3b24 = 0xff;
  return;
}

void FUN_0008b3d4(void)

{
  DAT_febf3b27 = 1;
  DAT_febf3b28 = 1;
  DAT_febf3b26 = 0;
  DAT_febf3b29 = 0xff;
  return;
}

void FUN_0008b3e8(void)

{
  f33_reset_write_did_transaction();
  return;
}

void thunk_FUN_0008b3d4(void)

{
  FUN_0008b3d4();
  return;
}

void FUN_0008b79a(undefined1 param_1)

{
  DAT_febf3b20 = param_1;
  return;
}

undefined1 FUN_0008b7a4(void)

{
  return DAT_febf3b25;
}

void FUN_0008b7ae(undefined1 param_1)

{
  DAT_febf3b25 = param_1;
  return;
}

undefined4 f33_return_const_0_8b854(void)

{
  return 0;
}

uint f33_diag_routine_crypto_admit(void)

{
  uint uVar1;
  
  uVar1 = f33_return_const_0_8b854();
  return uVar1;
}

undefined4 f33_return_const_2_8bd72(void)

{
  return 2;
}

undefined1 FUN_0008bd76(undefined1 param_1)

{
  return param_1;
}

void f33_fill_constant_block_8bfea(void)

{
  DAT_febf3bd2 = 1;
  DAT_febf3bd1 = 1;
  DAT_febf3bd0 = 0;
  DAT_febf3bcc = 0;
  DAT_febf3bd3 = 0xff;
  return;
}

void FUN_0008c318(void)

{
  uint uVar1;
  
  DAT_febf3bf8 = 0xff;
  DAT_febf3bf7 = 0;
  DAT_febf3bf2 = 0;
  DAT_febf3bf6 = 0;
  DAT_febf3bf5 = 0;
  DAT_febf3bf4 = 0;
  uVar1 = 0;
  do {
    f33_dtc_count_local_tuple_scratch[uVar1] = '\0';
    uVar1 = uVar1 + 1;
  } while (uVar1 < 0x300);
  DAT_febf3bf9 = 0;
  return;
}

uint f33_begin_dtc_count_iteration(uchar mask)

{
  uint uVar1;
  
  uVar1 = f33_begin_filtered_dtc_iteration(mask);
  DAT_febf3bf5 = mask;
  return uVar1;
}

void f33_fill_constant_block_8cb8c(void)

{
  DAT_febf4247 = 0xff;
  DAT_febf4246 = 0;
  DAT_febf4242 = 0;
  DAT_febf4240 = 0;
  DAT_febf4245 = 0;
  DAT_febf4244 = 0;
  return;
}

undefined4 f33_return_const_0_8cbc0(void)

{
  return 0;
}

void FUN_0008d4ae(void)

{
  DAT_febf459a = 0;
  DAT_febf4599 = 1;
  DAT_febf4598 = 1;
  DAT_febf459b = 0xff;
  return;
}

void thunk_FUN_0008d4ae(void)

{
  FUN_0008d4ae();
  return;
}

undefined4 FUN_0008d4e0(char param_1)

{
  if ((param_1 != '\x01') && (param_1 != '\x03' && param_1 != '\x04')) {
    return 0;
  }
  return 0x31;
}

void f33_app_security_reset_challenge_material(void)

{
  uint uVar1;
  
  uVar1 = 0;
  do {
    f33_app_security_challenge[uVar1] = '\0';
    f33_app_security_challenge_duplicate[uVar1] = '\0';
    f33_app_security_client_material[uVar1] = '\0';
    uVar1 = uVar1 + 1;
  } while (uVar1 < 0x10);
  f33_app_security_challenge_active = '\0';
  f33_app_security_comparison_result = '\0';
  return;
}

void FUN_0008d6a4(void)

{
  f33_app_security_reset_challenge_material();
  return;
}

uchar FUN_0008d9a2(void)

{
  return f33_app_security_comparison_result;
}

void FUN_0008d9ac(void)

{
  f33_app_security_comparison_result = '\0';
  return;
}

void FUN_0008d9ca(void)

{
  f33_dcm_communication_local_state.last_tx_disable_bit = '\0';
  f33_dcm_communication_local_state.last_mapped_mode = '\0';
  f33_dcm_communication_local_state.retained_subnet = '\0';
  f33_dcm_communication_local_state.action_state = '\0';
  f33_dcm_communication_local_state.lower_status = '\0';
  f33_dcm_communication_local_state.application_status = '\0';
  f33_dcm_communication_local_state.admission_result = '\x01';
  f33_dcm_communication_local_state.side_status = 0xff;
  return;
}

void f33_fill_constant_block_8db22(void)

{
  DAT_febf45ae = 1;
  DAT_febf45ad = 1;
  DAT_febf45ac = 0;
  DAT_febf45ab = 0;
  DAT_febf45aa = 0;
  DAT_febf45a8 = 0;
  DAT_febf45a9 = 0xff;
  DAT_febf45b0 = 1;
  DAT_febf45af = 1;
  return;
}

undefined4 FUN_0008dc60(void)

{
  uchar selection;
  
  if (DAT_febf45a8 == '\x01') {
    selection = '\x01';
  }
  else {
    selection = '\x02';
  }
  f33_publish_dtc_setting_request(selection);
  return 0;
}

uint f33_begin_proprietary_event_selection
               (uchar operation,uchar selector,ushort event_id,ushort subselector)

{
  DAT_febf45d0 = event_id;
  DAT_febf45d2 = subselector;
  DAT_febf45dc = selector;
  FUN_00050916((uint)(byte)selector, (uint)(ushort)event_id, (uint)(ushort)subselector);
  return 0;
}

undefined4 FUN_0008debe(char param_1)

{
  if (param_1 == '\x04') {
    return 0x31;
  }
  if (param_1 != '\x06') {
    if (param_1 != '\n') {
      return 0;
    }
    return 0x10;
  }
  return 0x14;
}

void FUN_0008e1e0(void)

{
  f33_dcm_proprietary_continuation.selected_index = '\0';
  f33_dcm_proprietary_continuation.side_result = '\x01';
  f33_dcm_proprietary_continuation.application_result = '\x01';
  f33_dcm_proprietary_continuation.phase = '\0';
  f33_dcm_proprietary_continuation.side_status = 0xff;
  return;
}

uint f33_merge_two_diagnostic_statuses
               (uchar application_status,uchar lower_status,uchar success_status,
               uchar pending_status)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  
  uVar1 = (uint)application_status;
  uVar2 = (uint)lower_status;
  uVar3 = (uint)pending_status;
  if ((((uVar2 != uVar3) && (uVar1 != uVar3)) && (uVar3 = uVar1, uVar1 == success_status)) &&
     (uVar2 != success_status)) {
    uVar3 = uVar2;
  }
  return uVar3;
}

uint f33_diag_routine_local_dispatch_enabled(void)

{
  return 0x5a;
}

void FUN_0008e74e(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = 0;
  do {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5338u + (uint32_t)(iVar3) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5398u + (uint32_t)(iVar3) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe52d8u + (uint32_t)(iVar3) * 1u)))) = 0x5a;
    iVar2 = iVar3 + 1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe53f8u + (uint32_t)(iVar3) * 1u)))) = 0x5a;
    iVar1 = iVar3 + -0x5f;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  return;
}

void FUN_0008e772(uint param_1)

{
  param_1 = param_1 & 0xffff;
  if (param_1 < 0x60) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe52d8u + (uint32_t)(param_1) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5338u + (uint32_t)(param_1) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5338u + (uint32_t)(param_1) * 1u)))) + '\x01';
  }
  return;
}

void FUN_0008e790(uint param_1)

{
  if ((param_1 & 0xffff) < 0x60) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe52d8u + (uint32_t)(param_1 & 0xffff) * 1u)))) = 0x5a;
  }
  return;
}

void FUN_0008e7a4(uint param_1)

{
  if ((param_1 & 0xffff) < 0x60) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5338u + (uint32_t)(param_1 & 0xffff) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5338u + (uint32_t)(param_1 & 0xffff) * 1u)))) + '\x01';
  }
  return;
}

void FUN_0008e7ba(uint param_1)

{
  if ((param_1 & 0xffff) < 0x60) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5398u + (uint32_t)(param_1 & 0xffff) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5398u + (uint32_t)(param_1 & 0xffff) * 1u)))) + '\x01';
  }
  return;
}

void FUN_0008e7d0(uint param_1,undefined1 param_2)

{
  if ((param_1 & 0xffff) < 0x60) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe53f8u + (uint32_t)(param_1 & 0xffff) * 1u)))) = param_2;
  }
  return;
}

bool FUN_0008e9a0(ushort param_1,ushort param_2)

{
  if (param_1 == 0) {
    f33_secoc_tx_queue_head_pair[1] = ~param_2;
    f33_secoc_tx_queue_head_pair[0] = param_2;
  }
  if (param_1 == 1) {
    DAT_febe5466 = ~param_2;
    DAT_febe5464 = param_2;
  }
  return 1 < param_1;
}

short FUN_0008eee8(void)

{
  short sStack_6;
  
  sStack_6 = 0;
  FUN_00089d08(&sStack_6);
  if ((sStack_6 != 0) && (sStack_6 != 1)) {
    sStack_6 = 2;
  }
  return sStack_6;
}

undefined4 FUN_0008ef0c(void)

{
  undefined4 uVar1;
  
  if (((int16_t)DAT_febe54f4) == -0x1ff) {
    uVar1 = 0;
    if (((int16_t)DAT_febe54f6) != -0x1ff) {
      if (((int16_t)DAT_febe54f6) == -0x2fe) {
        uVar1 = 0;
      }
      else {
        uVar1 = 2;
      }
    }
    return uVar1;
  }
  if (DAT_febe54f4 == 0) {
    uVar1 = 1;
  }
  else {
    uVar1 = 2;
  }
  return uVar1;
}

undefined4 thunk_FUN_0008fa86(void)

{
  return FUN_0008fa86();
}

int thunk_FUN_0008f2fc(void)

{
  return FUN_0008f2fc();
}

undefined4 FUN_0008f0d4(short param_1)

{
  undefined4 uVar1;
  
  uVar1 = 1;
  if ((((int16_t)DAT_febe54f4) == -0x1ff) && (param_1 == DAT_0002583c)) {
    ((void)(0), FUN_0008f3ec());
    uVar1 = 0;
  }
  return uVar1;
}

undefined4 f33_return_const_1_8f10e(void)

{
  return 1;
}

undefined4 f33_return_const_1_8f112(void)

{
  return 1;
}

undefined4 f33_return_const_1_8f116(void)

{
  return 1;
}

uint f33_secoc_crypto_qualification_reported(void)

{
  return (uint)(f33_secoc_crypto_qualification == 0xd2);
}

int FUN_0008f2fc(void)

{
  char cVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  
  iVar3 = 0;
  iVar2 = 1;
  uVar4 = 0;
  do {
    cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5524u + (uint32_t)(uVar4) * 1u))));
    if (((int8_t)cVar1) != -0x1f) {
      if ((((((int8_t)cVar1) == -0x6a) || (((int8_t)cVar1) == -0x5b)) || (((int8_t)cVar1) == -0x4c)) ||
         ((((int8_t)cVar1) == -0x3d || (((int8_t)cVar1) == -0x2e)))) {
        iVar2 = 2;
      }
      else {
        iVar3 = 0xff;
      }
    }
    uVar4 = uVar4 + 1;
  } while (uVar4 < 3);
  if ((iVar3 == 0xff) && (iVar2 == 1)) {
    iVar2 = 3;
  }
  return iVar2;
}

void FUN_0008f3ec(void)

{
  DAT_febe551c = 0;
  return;
}

undefined4 FUN_0008f9c6(void)

{
  char cVar1;
  undefined4 uVar2;
  uint uVar3;
  
  uVar3 = (uint)DAT_febe5520;
  uVar2 = 2;
  if (2 < uVar3) {
    uVar3 = 0;
  }
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5524u + (uint32_t)(uVar3) * 1u))));
  if ((((((int8_t)cVar1) == -0x6a) || (((int8_t)cVar1) == -0x5b)) || (((int8_t)cVar1) == -0x4c)) ||
     (((((int8_t)cVar1) == -0x3d || (((int8_t)cVar1) == -0x2e)) || (((int8_t)cVar1) == -0x1f)))) {
    uVar2 = 0;
  }
  else {
    DAT_febe5522 = 3;
  }
  if (DAT_febe5522 != 0) {
    DAT_febe5522 = DAT_febe5522 + -1;
    uVar2 = 2;
  }
  DAT_febe5520 = (short)uVar3 + 1;
  return uVar2;
}

undefined4 FUN_0008fa86(void)

{
  if (((int8_t)DAT_febe5568) == -0x1f) {
    return 1;
  }
  if ((((((int8_t)DAT_febe5568) != -0x6a) && (((int8_t)DAT_febe5568) != -0x5b)) && (((int8_t)DAT_febe5568) != -0x4c)) &&
     ((((int8_t)DAT_febe5568) != -0x3d && (((int8_t)DAT_febe5568) != -0x2e)))) {
    return 3;
  }
  return 2;
}

ushort FUN_0008fc58(void)

{
  ushort uVar1;
  
  uVar1 = DAT_00025826;
  if (DAT_febe556a < DAT_00025826) {
    uVar1 = DAT_febe556a;
  }
  return uVar1;
}

void FUN_000912b2(void)

{
  f33_dcm_final_nrc = '\0';
  return;
}

void FUN_000912b8(void)

{
  f33_dcm_final_nrc = '\0';
  return;
}

void f33_dcm_reset_message_context(void)

{
  f33_dcm_message_context.request = 0;
  f33_dcm_message_context.request_length = 0;
  f33_dcm_message_context.response = 0;
  f33_dcm_message_context.response_length = 0;
  f33_dcm_message_context.addressing_kind = '\0';
  f33_dcm_message_context.suppress_positive = '\0';
  f33_dcm_message_context.response_capacity = 0;
  f33_dcm_message_context.service_id = '\0';
  f33_dcm_message_context.service_list_selector = 0;
  return;
}

void FUN_000913ea(undefined1 param_1)

{
  DAT_febe562c = param_1;
  return;
}

undefined1 FUN_0009168e(void)

{
  return DAT_febe562c;
}

bool FUN_0009169a(void)

{
  return f33_dcm_active_service_callback != 0x0u;
}

undefined1 FUN_000916a6(void)

{
  return DAT_febe562d;
}

bool FUN_0009177c(void)

{
  return f33_dcm_active_service_callback == 0x0u;
}

void FUN_000917b2(void)

{
  int iVar1;
  uint uVar2;
  
  uVar2 = 0;
  do {
    iVar1 = uVar2 * 2;
    uVar2 = uVar2 + 1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe564cu + (uint32_t)(iVar1) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe564du + (uint32_t)(iVar1) * 1u)))) = 0;
  } while (uVar2 < 2);
  DAT_febe5650 = 1;
  return;
}

void FUN_00091ab8(void)

{
  return;
}

void FUN_00091ac2(undefined1 param_1)

{
  FUN_0007ed16(param_1);
  return;
}

void FUN_00091ad0(undefined1 param_1)

{
  FUN_0007ed2e(param_1);
  return;
}

ushort thunk_FUN_00093c60(void)

{
  return FUN_00093c60();
}

void FUN_00091cd2(undefined1 param_1,undefined1 param_2)

{
  FUN_00093162(param_1,param_2);
  return;
}

undefined4 FUN_00091f9c(undefined1 param_1)

{
  return FUN_000925a0(param_1);
}

undefined4 f33_return_const_0_9203c(void)

{
  return 0;
}

undefined4 f33_return_const_0_92040(void)

{
  return 0;
}

undefined4 FUN_00092054(undefined1 param_1,undefined1 param_2)

{
  return ((void)(param_1), (void)(param_2), f33_return_const_0_9203c());
}

void FUN_000924e8(void)

{
  f33_app_dcm_session_snapshot.current = '\x01';
  f33_app_dcm_session_snapshot.previous = '\x01';
  f33_app_dcm_session_snapshot.target = '\x01';
  f33_app_dcm_session_snapshot.pending_publication = '\0';
  return;
}

undefined4 FUN_000925a0(undefined1 param_1)

{
  return ((void)(param_1), f33_return_const_0_9260c());
}

void FUN_00092602(void)

{
  return;
}

undefined4 f33_return_const_0_9260c(void)

{
  return 0;
}

void FUN_00092610(uchar param_1)

{
  f33_dcm_request_phase = param_1;
  return;
}

void FUN_00092616(void)

{
  FUN_00092610(0);
  return;
}

uchar FUN_00092624(void)

{
  return f33_dcm_request_phase;
}

uint f33_dcm_map_response_delivery_result(uchar disposition,uchar transport_result)

{
  if (disposition == '\0') {
    return (uint)(transport_result != '\0');
  }
  if (disposition == '\x01') {
    if (transport_result != '\0') {
      return 3;
    }
  }
  else if (disposition == '\x02') {
    return 0;
  }
  return 2;
}

undefined4 FUN_00092c46(uint param_1)

{
  uint uVar1;
  undefined4 uVar2;
  
  uVar1 = (param_1 & 0xff) - 0x30;
  uVar2 = 0;
  if ((uVar1 < 3) || (uVar1 == 0x10)) {
    uVar2 = 1;
  }
  return uVar2;
}

uchar FUN_00092f6a(void)

{
  return f33_dcm_explicit_pending_notification;
}

void FUN_00092f70(uchar param_1)

{
  f33_dcm_explicit_pending_notification = param_1;
  return;
}

void FUN_00093162(undefined1 param_1,undefined1 param_2)

{
  FUN_00093154(f33_dcm_final_negative_response,param_1,param_2);
  return;
}

undefined4 f33_return_const_febe5978_93690(void)

{
  return 0xfebe5978;
}

undefined4 FUN_00093a8c(void)

{
  ushort uVar1;
  int iVar2;
  
  iVar2 = FUN_00092624();
  uVar1 = f33_dcm_count_receiving_slots();
  if (iVar2 == 2) {
    if (uVar1 < 2) {
      return 0;
    }
  }
  else if (uVar1 == 0) {
    return 0;
  }
  return 1;
}

void FUN_00093ab2(void)

{
  DAT_febe59d4 = 0xff;
  return;
}

void FUN_00093aba(void)

{
  uint uVar1;
  uint uVar2;
  uchar *puVar3;
  uint uVar4;
  
  f33_dcm_pending_transport_accepted = '\0';
  f33_dcm_shared_response_buffer[0] = '\0';
  f33_dcm_pending_dispatch_receive_slot = 0;
  f33_dcm_current_dispatch_receive_slot = 0;
  f33_dcm_retained_p2_star_raw = 0;
  f33_dcm_pending_spacing_raw = 0;
  DAT_febe59e4 = 0;
  DAT_febe59e6 = 0;
  f33_dcm_displaced_transmit_id = 0;
  f33_dcm_zero_p2_deadline = '\0';
  f33_dcm_zero_overall_timeout = '\0';
  uVar4 = 0;
  do {
    f33_dcm_receive_buffer_state[uVar4].receiving = '\0';
    puVar3 = ((void *)camry_host_ptr((uint32_t)(f33_dcm_receive_buffer_configuration[uVar4].base)));
    uVar1 = uVar4 + 1;
    f33_dcm_receive_buffer_state[uVar4].write_cursor = camry_host_addr(puVar3);
    *puVar3 = '\0';
    uVar2 = f33_dcm_receive_buffer_configuration[uVar4].capacity;
    f33_dcm_receive_buffer_state[uVar4].received_length = 0;
    f33_dcm_receive_buffer_state[uVar4].abort_pending = '\0';
    f33_dcm_receive_buffer_state[uVar4].inactivity_participant = '\0';
    f33_dcm_receive_buffer_state[uVar4].remaining_capacity = (ushort)uVar2;
    uVar4 = uVar1;
  } while (uVar1 < 3);
  return;
}

ushort FUN_00093c5a(void)

{
  return f33_dcm_pending_spacing_raw;
}

ushort FUN_00093c60(void)

{
  return f33_dcm_current_dispatch_receive_slot;
}

void FUN_00093c66(ushort param_1)

{
  f33_dcm_current_dispatch_receive_slot = param_1;
  return;
}

uchar FUN_00093c8e(void)

{
  return f33_dcm_pending_transport_accepted;
}

void FUN_00093c94(uchar param_1)

{
  f33_dcm_pending_transport_accepted = param_1;
  return;
}

void FUN_00093c9a(uint param_1,char param_2)

{
  uchar *puVar1;
  uint uVar2;
  
  param_1 = param_1 & 0xffff;
  if (param_2 == '\0') {
    f33_dcm_shared_response_buffer[0] = '\0';
    f33_dcm_pending_transport_accepted = '\0';
  }
  puVar1 = ((void *)camry_host_ptr((uint32_t)(f33_dcm_receive_buffer_configuration[param_1].base)));
  f33_dcm_receive_buffer_state[param_1].receiving = '\0';
  f33_dcm_receive_buffer_state[param_1].write_cursor = camry_host_addr(puVar1);
  *puVar1 = '\0';
  uVar2 = f33_dcm_receive_buffer_configuration[param_1].capacity;
  f33_dcm_receive_buffer_state[param_1].received_length = 0;
  f33_dcm_receive_buffer_state[param_1].inactivity_participant = '\0';
  f33_dcm_receive_buffer_state[param_1].remaining_capacity = (ushort)uVar2;
  return;
}

void FUN_00094008(ushort param_1)

{
  f33_dcm_pending_dispatch_receive_slot = param_1;
  return;
}

ushort FUN_0009400e(void)

{
  return f33_dcm_pending_dispatch_receive_slot;
}

void FUN_0009405c(undefined2 param_1)

{
  uint uVar1;
  
  uVar1 = DAT_febe59e6 + 1;
  *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe59dcu)) + (uint)DAT_febe59e6 * 2) = param_1;
  DAT_febe59e6 = (ushort)uVar1;
  if (1 < (uVar1 & 0xffff)) {
    DAT_febe59e6 = 0;
  }
  return;
}

undefined2 FUN_0009407c(void)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  
  uVar2 = (uint)DAT_febe59e4;
  uVar1 = uVar2 + 1;
  uVar3 = uVar1 & 0xffff;
  DAT_febe59e4 = (ushort)uVar1;
  if (1 < uVar3) {
    DAT_febe59e4 = 0;
    uVar3 = 0;
  }
  if (uVar3 == DAT_febe59e6) {
    DAT_febe59e4 = 0;
    DAT_febe59e6 = 0;
  }
  return *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe59dcu)) + uVar2 * 2);
}

ushort FUN_000940ca(void)

{
  return f33_dcm_displaced_transmit_id;
}

void FUN_000940d0(uchar param_1,char param_2)

{
  if (param_2 == '\0') {
    f33_dcm_zero_p2_deadline = param_1;
    return;
  }
  if (param_2 == '\x01') {
    f33_dcm_zero_overall_timeout = param_1;
  }
  return;
}

uchar FUN_000940e6(char param_1)

{
  uchar uVar1;
  
  if (param_1 == '\0') {
    return f33_dcm_zero_p2_deadline;
  }
  uVar1 = '\0';
  if (param_1 == '\x01') {
    uVar1 = f33_dcm_zero_overall_timeout;
  }
  return uVar1;
}

undefined4 FUN_00094df6(short param_1,int param_2,int param_3)

{
  uint32_t puVar1;
  int extraout_r7;
  int iVar2;
  uint uVar3;
  byte bVar4;
  byte bStack_1b;
  undefined2 uStack_1a;
  undefined1 auStack_18 [3];
  byte bStack_15;
  
  puVar1 = 0x23dfcu;
  uVar3 = 0;
  if ((((param_1 == 0) && (iVar2 = FUN_00094d9c(DAT_00026028,&uStack_1a), iVar2 == 0)) &&
      (iVar2 = FUN_00095514(uStack_1a, ((undefined1 *)camry_host_ptr((uint32_t)(extraout_r7 + -1)))), iVar2 == 0)) &&
     ((uint)bStack_1b + param_2 <= (uint)(*((byte *)camry_host_ptr((uint32_t)(*(int *)(puVar1 + 0x2220) + 0xc)))))) {
    for (bVar4 = 0; bVar4 < bStack_1b; bVar4 = bVar4 + 1) {
      iVar2 = ((void)(auStack_18), FUN_0009552a(uStack_1a, bVar4));
      if (iVar2 != 0) {
        return 1;
      }
      uVar3 = uVar3 + bStack_15 & 0xffff;
    }
    if (uVar3 + param_3 == 0) {
      return 0;
    }
  }
  return 1;
}

undefined4 FUN_00094e6a(undefined2 param_1,int param_2,uint param_3)

{
  int iVar1;
  undefined4 uVar2;
  uint uVar3;
  byte bStack_19;
  undefined2 uStack_18;
  undefined1 uStack_16;
  undefined1 uStack_15;
  
  iVar1 = FUN_00095514(param_1,&bStack_19);
  uVar3 = 0;
  if (iVar1 == 0) {
    for (; uVar3 < (param_3 & 0xff); uVar3 = uVar3 + 1 & 0xff) {
      iVar1 = uVar3 * 4;
      uStack_18 = CONCAT11((*((undefined1 *)camry_host_ptr((uint32_t)(iVar1 + 2 + param_2)))),(*((undefined1 *)camry_host_ptr((uint32_t)(iVar1 + 3 + param_2))))
                          );
      uStack_16 = (*((undefined1 *)camry_host_ptr((uint32_t)(iVar1 + param_2 + 4))));
      uStack_15 = (*((undefined1 *)camry_host_ptr((uint32_t)(iVar1 + param_2 + 5))));
      iVar1 = ((void)(&uStack_18), FUN_00095474(param_1, bStack_19 + uVar3 & 0xff));
      if (iVar1 != 0) goto LAB_00094e86;
    }
    uVar2 = FUN_000954dc(param_1,(param_3 & 0xff) + (uint)bStack_19 & 0xff);
  }
  else {
LAB_00094e86:
    uVar2 = 1;
  }
  return uVar2;
}

undefined4 FUN_00094f3a(undefined2 param_1)

{
  int iVar1;
  undefined4 uVar2;
  undefined2 uStack_a;
  
  uVar2 = 1;
  iVar1 = FUN_00094d9c(param_1,&uStack_a);
  if (iVar1 == 0) {
    uVar2 = FUN_000954ee(uStack_a);
  }
  return uVar2;
}

undefined4 thunk_FUN_00095500(void)

{
  return FUN_00095500();
}

undefined4 FUN_0009512c(void)

{
  DAT_febe5d20 = 0;
  DAT_febe5d21 = 0;
  return FUN_00095500();
}

undefined4 FUN_00095474(short param_1,uint param_2)

{
  uint32_t puVar1;
  undefined2 *extraout_r8;
  int iVar2;
  undefined4 uVar3;
  short asStack_12 [3];
  
  puVar1 = 0x23dfcu;
  uVar3 = 1;
  if ((((param_1 == 0) && (DAT_00025fe8 != 0)) &&
      (iVar2 = FUN_00095418(DAT_00025fec,asStack_12), iVar2 == 0)) &&
     ((asStack_12[0] == 0 && ((param_2 & 0xff) < (uint)(*((byte *)camry_host_ptr((uint32_t)(*(int *)(puVar1 + 0x2220) + 0xc)))))))
     ) {
    iVar2 = (param_2 & 0xff) * 4;
    (*((undefined2 *)camry_host_ptr((uint32_t)(*(int *)(puVar1 + 0x21ec) + iVar2)))) = *extraout_r8;
    (*((undefined1 *)camry_host_ptr((uint32_t)(*(int *)(puVar1 + 0x21ec) + iVar2 + 2)))) = *(undefined1 *)(extraout_r8 + 1);
    (*((undefined1 *)camry_host_ptr((uint32_t)(iVar2 + *(int *)(puVar1 + 0x21ec) + 3)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(extraout_r8) + 3))));
    uVar3 = 0;
  }
  return uVar3;
}

bool FUN_000954dc(short param_1,undefined1 param_2)

{
  if (param_1 == 0) {
    DAT_febe5d23 = param_2;
  }
  return param_1 != 0;
}

bool FUN_000954ee(short param_1)

{
  if (param_1 == 0) {
    DAT_febe5d23 = 0;
  }
  return param_1 != 0;
}

undefined4 FUN_0009552a(short param_1,uint param_2)

{
  uint32_t puVar1;
  undefined2 *extraout_r8;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  short asStack_12 [3];
  
  puVar1 = 0x23dfcu;
  uVar3 = 1;
  if ((((param_1 == 0) && (DAT_00025fe8 != 0)) &&
      (iVar2 = FUN_00095418(DAT_00025fec,asStack_12), iVar2 == 0)) &&
     ((asStack_12[0] == 0 && ((param_2 & 0xff) < (uint)(*((byte *)camry_host_ptr((uint32_t)(*(int *)(puVar1 + 0x2220) + 0xc)))))))
     ) {
    iVar2 = (param_2 & 0xff) * 4;
    iVar4 = (*((int *)camry_host_ptr((uint32_t)(puVar1 + 0x21ec))));
    *extraout_r8 = (*((undefined2 *)camry_host_ptr((uint32_t)(*(int *)(puVar1 + 0x21ec) + iVar2))));
    *(undefined1 *)(extraout_r8 + 1) = (*((undefined1 *)camry_host_ptr((uint32_t)(iVar4 + iVar2 + 2))));
    (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(extraout_r8) + 3)))) = (*((undefined1 *)camry_host_ptr((uint32_t)(iVar2 + *(int *)(puVar1 + 0x21ec) + 3))));
    uVar3 = 0;
  }
  return uVar3;
}

void FUN_000955b6(uchar param_1)

{
  f33_app_dcm_callback_pending = param_1;
  return;
}

uchar FUN_000955bc(void)

{
  return f33_app_dcm_callback_pending;
}

void FUN_0009560e(char param_1)

{
  if (param_1 == '\x01') {
    DAT_febe5d24 = 0;
  }
  else {
    DAT_febe5d24 = 0xa5a5a5a5;
  }
  return;
}

undefined4 f33_return_const_1_95622(void)

{
  return 1;
}

void FUN_00095a06(void)

{
  FUN_0009560e(1);
  return;
}

undefined4 FUN_00095d4e(char param_1)

{
  if (param_1 == '\0') {
    thunk_FUN_0008b134();
  }
  return 0;
}

void FUN_00096622(uint param_1,char param_2)

{
  uint uVar1;
  
  if ((param_1 & 0xff) < 2) {
    uVar1 = 1 << (param_1 & 0x1f);
    if (param_2 == '\x01') {
      f33_app_security_delay_bits = f33_app_security_delay_bits | uVar1;
    }
    else {
      f33_app_security_delay_bits = f33_app_security_delay_bits & ~uVar1;
    }
  }
  return;
}

void FUN_000968c6(void)

{
  f33_app_security_issued_level = '\0';
  return;
}

undefined4 f33_return_const_1_968de(void)

{
  return 1;
}

undefined4 f33_return_const_1_96b24(void)

{
  return 1;
}

undefined4 f33_return_const_1_96b38(void)

{
  return 1;
}

undefined4 f33_return_const_0_9713a(void)

{
  return 0;
}

undefined4 f33_return_const_b_9713e(void)

{
  return 0xb;
}

uint FUN_00098850(uchar param_1,uchar param_2,ushort param_3,ushort param_4)

{
  uint uVar1;
  
  if (param_1 == '\x02') {
    f33_fill_constant_block_8de1a();
    uVar1 = 0;
  }
  else {
    uVar1 = f33_begin_proprietary_event_selection(param_1,param_2,param_3,param_4);
  }
  return uVar1;
}

undefined4 f33_return_const_1_988e4(void)

{
  return 1;
}

undefined4 FUN_000988e8(int param_1)

{
  undefined4 uVar1;
  
  if (param_1 == 0) {
    uVar1 = 1;
  }
  else {
    uVar1 = f33_return_const_1_988e4();
  }
  return uVar1;
}

undefined4 f33_return_const_0_98936(void)

{
  return 0;
}

void f33_dcm_reset_event_ring(void)

{
  f33_dcm_event_ring.producer = '\0';
  f33_dcm_event_ring.consumer = '\0';
  f33_dcm_event_ring.occupied_slots = '\0';
  return;
}

uint f33_dcm_validate_event_id(uchar event_id)

{
  uint uVar1;
  uint uVar2;
  
  uVar1 = (uint)event_id;
  uVar2 = 1;
  if ((uVar1 < 0x2c) ||
     ((0xea < uVar1 && ((int)(uVar1 - (f33_dcm_extended_event_count + 0xeb)) < 0)))) {
    uVar2 = 0;
  }
  return uVar2;
}

void f33_dcm_reset_timer_slots(void)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = 0;
  do {
    uVar1 = uVar2 + 1;
    f33_dcm_software_timers[uVar2].remaining = 0;
    f33_dcm_software_timers[uVar2].active = '\0';
    uVar2 = uVar1;
  } while (uVar1 < 9);
  return;
}

void FUN_00098f4c(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = 0;
  do {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5ebcu + (uint32_t)(iVar3) * 1u)))) = 0;
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -7;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  DAT_febe5ec4 = 1;
  DAT_febe5ec5 = 0;
  DAT_febe5ec6 = 0;
  return;
}

void FUN_00098f6e(int param_1,char param_2,undefined1 param_3)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  if (param_2 == 'Z') {
    DAT_febe5ebc = 0xff;
    iVar3 = 1;
    do {
      iVar2 = iVar3 + 1;
      iVar1 = iVar3 + -7;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5ebcu + (uint32_t)(iVar3) * 1u)))) = (*((undefined1 *)camry_host_ptr((uint32_t)(iVar3 + param_1))));
      iVar3 = iVar2;
    } while (((iVar1 < 0) || (iVar2 < 0)));
    return;
  }
  DAT_febe5ebc = 0xfe;
  iVar3 = 2;
  DAT_febe5ebd = param_3;
  do {
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -7;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5ebcu + (uint32_t)(iVar3) * 1u)))) = (*((undefined1 *)camry_host_ptr((uint32_t)(iVar3 + param_1))));
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  return;
}

void FUN_000b149c(void)

{
  uint uVar1;
  
  uVar1 = 0;
  do {
    *(undefined4 *)(((undefined *)camry_host_ptr(0xfebeb090u)) + uVar1 * 4) = 0xffffffff;
    uVar1 = uVar1 + 1;
  } while (uVar1 < 2);
  return;
}

void FUN_000b14b2(void)

{
  int iVar1;
  uint uVar2;
  
  uVar2 = 0;
  do {
    iVar1 = uVar2 * 4;
    *(undefined4 *)(((undefined *)camry_host_ptr(0xfebeb098u)) + iVar1) = 0;
    uVar2 = uVar2 + 1;
    *(undefined4 *)(((undefined *)camry_host_ptr(0xfebeb090u)) + iVar1) = 0xffffffff;
  } while (uVar2 < 2);
  return;
}

void f33_reset_mode_readiness_counter(void)

{
  DAT_febeb114 = 0;
  f33_return_only_stub_b1d9e();
  return;
}

uint f33_probe_pending_mode_request(uchar request_id)

{
  uint uVar1;
  
  if (*(short *)(((undefined *)camry_host_ptr(0xfebeb0a8u)) + (uint)request_id * 2) == -0x5aa6) {
    uVar1 = 1;
    if (request_id < 0x10) {
      DAT_febeb0a6 = ~request_id;
      DAT_febeb10c = request_id;
      DAT_febeb11c = DAT_febeb11a;
      DAT_febeb0a2 = ~DAT_febeb11a;
      return uVar1;
    }
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}

uint f33_materialize_mode_request(uint request_id)

{
  undefined *puVar1;
  
  puVar1 = ((undefined *)camry_host_ptr((uint32_t)((uint)*(ushort *)(((undefined *)camry_host_ptr(0xfebeb0a8u)) + (request_id & 0xff) * 2))));
  if ((uintptr_t)(puVar1)!=(uintptr_t)(((undefined *)camry_host_ptr((uint32_t)(0x5aa5))))) {
    puVar1 = ((undefined *)camry_host_ptr(0xa55au));
    *(ushort *)(((undefined *)camry_host_ptr(0xfebeb0a8u)) + (request_id & 0xff) * 2) = 0xa55a;
  }
  return (uint)camry_host_addr(puVar1);
}

undefined2 FUN_000b1c34(uint param_1)

{
  return *(undefined2 *)(((undefined *)camry_host_ptr(0xfebeb0a8u)) + (param_1 & 0xff) * 2);
}

bool FUN_000b1c40(void)

{
  return DAT_febeb0a6 == (byte)~DAT_febeb10c;
}

uint f33_get_mode700_progress_marker(void)

{
  if ((DAT_febeb11a != 0x702) && (DAT_febeb11a == 0x701)) {
    return 0;
  }
  return 0x5a;
}

uint f33_select_service_join_after_mode200(void)

{
  uint uVar1;
  
  if (DAT_febef208 == 0) {
    uVar1 = 2;
  }
  else {
    uVar1 = 1;
  }
  DAT_febeb10f = (char)uVar1;
  return uVar1;
}

void f33_enter_mode600(void)

{
  DAT_febeb110 = 0;
  return;
}

int f33_latch_internal_ba_selector(uint selector)

{
  if (selector == 5) {
    DAT_febeb113 = 0x22;
  }
  else if (selector == 6) {
    DAT_febeb113 = 0x44;
  }
  else {
    DAT_febeb113 = 0x88;
    if (selector != 7) {
      DAT_febeb113 = 0x11;
    }
  }
  DAT_febeb112 = 0x5a;
  return 0;
}

int f33_latch_ba_unsigned_override(uchar value)

{
  DAT_febeb116 = 0x5a;
  DAT_febeb117 = value;
  return 0;
}

int f33_latch_ba_owner5_fast_release(void)

{
  DAT_febeb118 = 0x5a;
  return 0;
}

void FUN_000b3866(void)

{
  uint uVar1;
  
  DAT_febeb13a = 0;
  uVar1 = (uint)DAT_000aef4c;
  if (uVar1 != 0) {
    DAT_febeb13a = (undefined2)(0x10000000 / uVar1);
  }
  DAT_febeb138 = DAT_000aef4c;
  DAT_febeb13c = 0x564e;
  if (uVar1 != 0) {
    DAT_febeb13c = (undefined2)(0x2774564e / uVar1);
  }
  DAT_febeb140 = DAT_febeb13c;
  DAT_febeb13e = (undefined2)((uVar1 << 0xe) / 0x9dd1);
  DAT_febeb142 = DAT_febeb13e;
  return;
}

void FUN_000b389c(void)

{
  uint uVar1;
  
  DAT_febeb13a = 0;
  uVar1 = (uint)DAT_000aef4c;
  if (uVar1 != 0) {
    DAT_febeb13a = (undefined2)(0x10000000 / uVar1);
  }
  DAT_febeb138 = DAT_000aef4c;
  DAT_febeb13c = 0x564e;
  if (uVar1 != 0) {
    DAT_febeb13c = (undefined2)(0x2774564e / uVar1);
  }
  DAT_febeb140 = DAT_febeb13c;
  DAT_febeb13e = (undefined2)((uVar1 << 0xe) / 0x9dd1);
  DAT_febeb142 = DAT_febeb13e;
  return;
}

void FUN_000b3ac4(void)

{
  DAT_febeb168 = 0;
  if (DAT_febeb078 == '\0') {
    DAT_febeb168 = 0x5a;
  }
  return;
}

void FUN_000b3ad8(void)

{
  if ((((DAT_febef06b == '\0') && (DAT_febef069 == '\0')) && (DAT_febef154 == '\x02')) &&
     (f33_published_internal_source_admission_state < 2)) {
    DAT_febeb169 = 0x5a;
  }
  else {
    DAT_febeb169 = 0;
  }
  return;
}

void FUN_000b3b06(void)

{
  if ((DAT_febef069 == '\0') && (f33_published_internal_source_admission_state < 2)) {
    DAT_febeb16c = DAT_febef1a0 * 0xf + (short)DAT_febef06f;
  }
  return;
}

void FUN_000b3baa(void)

{
  if ((DAT_febeb168 == 'Z') && (DAT_febeb16a == 'Z')) {
    DAT_febeb178 = -DAT_febeb174 - DAT_febeafe8;
  }
  return;
}

uint f33_qualify_secondary_received_status_delay(void)

{
  uint uVar1;
  
  uVar1 = 0;
  if (((DAT_febebedd == 'Z') && (DAT_000aefae <= DAT_febebede)) && (DAT_000aefa8 <= DAT_febeb084)) {
    if ((DAT_000aefb0 < DAT_febeb19c) ||
       (DAT_febeb19c = DAT_febeb19c + 1, DAT_000aefb0 < DAT_febeb19c)) {
      uVar1 = 1;
    }
  }
  else {
    DAT_febeb19c = 0;
  }
  return uVar1;
}

uint f33_is_health_or_command_completion_observed(void)

{
  uint uVar1;
  
  uVar1 = 0;
  if ((DAT_febeb20e == '\x11') || (DAT_febeb190 == 'Z')) {
    uVar1 = 1;
  }
  return uVar1;
}

void f33_close_health_receive_generation_qualification(void)

{
  f33_health_receive_generation_armed = '\0';
  return;
}

void f33_reset_secondary_channel_qualification_history(void)

{
  DAT_febeb1a0 = 0;
  DAT_febeb19e = 0;
  DAT_febeb193 = 0;
  DAT_febeb194 = DAT_febeb194 & 0xfe;
  return;
}

void f33_latch_health_command_completion(void)

{
  DAT_febeb190 = 0x5a;
  return;
}

void f33_latch_availability_override(void)

{
  DAT_febeb18f = 0x5a;
  return;
}

void f33_publish_health_lifecycle_mode_indicator(void)

{
  if (((DAT_febeb11a & 0xff00) < 0x301) ||
     (((DAT_febeb11a & 0xff00) == 0x400 && (DAT_febeb1bd == 'Z')))) {
    DAT_febeb1a6 = 0;
  }
  else {
    DAT_febeb1a6 = 0x5a;
  }
  return;
}

void FUN_000b42f0(void)

{
  DAT_febeb1a7 = 0x5a;
  return;
}

void FUN_000b42fa(void)

{
  DAT_febeb1a7 = 0;
  return;
}

void f33_fill_constant_block_b4302(void)

{
  DAT_febeb1ac = 0;
  DAT_febeb1ad = 0;
  DAT_febeb1b6 = 0;
  DAT_febeb1b8 = 0;
  DAT_febeb1ba = DAT_000aefba;
  return;
}

void FUN_000b431a(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febeb1aa = 0;
  DAT_febeb1ab = 0;
  DAT_febeb1ae = 0;
  DAT_febeb1b0 = 0;
  DAT_febeb1b4 = 0;
  DAT_febeb1b2 = DAT_000aefba;
  f33_fill_constant_block_b4302();
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x658))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x657))))) = 0;
  return;
}

void FUN_000b4538(void)

{
  DAT_febeb1bc = 0;
  DAT_febeb1bd = 0;
  DAT_febeb1c0 = 0;
  DAT_febeb1c2 = 0;
  return;
}

void FUN_000b47d6(void)

{
  DAT_febeb1c4 = 2;
  return;
}

void FUN_000b47de(void)

{
  if (((DAT_febeb1ce == 'Z') || (DAT_febeb1d1 == 'Z')) || (DAT_febeb1bd == 'Z')) {
    DAT_febeb1c4 = 2;
  }
  else {
    DAT_febeb1c4 = 1;
  }
  return;
}

undefined2 FUN_000b480c(void)

{
  if ((((f33_published_internal_source_admission_state != '\x03') && ((DAT_febef093 >> 1 & 1) == 0))
      && (DAT_febef013 != '\x02')) && ((DAT_febef013 != '\x03' && ((DAT_febef16a & 0x1010) == 0))))
  {
    return DAT_febebede;
  }
  return DAT_febebee2;
}

void FUN_000b48dc(void)

{
  if (((DAT_febeb1ca == 'Z') && (DAT_febef0b3 != 'Z')) && (DAT_febeb1c9 == '\0')) {
    if ((DAT_febef0fe == '\0') && (DAT_febef0fd != '\0')) {
      DAT_febeb1e8 = 0;
    }
    else if (DAT_febeb1e8 < DAT_000aefd8) {
      DAT_febeb1e8 = DAT_febeb1e8 + 1;
    }
    else {
      DAT_febeb1e8 = 0;
      DAT_febeb1ca = '\0';
    }
    if (DAT_febeb1ea < DAT_000aefdc) {
      DAT_febeb1ea = DAT_febeb1ea + 1;
    }
    else {
      DAT_febeb1ea = 0;
      DAT_febeb1ca = '\0';
    }
  }
  else {
    DAT_febeb1e8 = 0;
    DAT_febeb1ea = 0;
  }
  return;
}

void FUN_000b4b04(void)

{
  if ((DAT_febeb1d0 == 'Z') && (DAT_febeb1ce == 'Z')) {
    if ((DAT_febeb1f4 < DAT_febeb1ec) && (DAT_febeb200 < DAT_000aeff2)) {
      if ((DAT_febebedd == 'Z') && (DAT_febebede <= DAT_000aeff0)) {
        DAT_febeb200 = DAT_febeb200 + 1;
      }
      else {
        DAT_febeb200 = 0;
      }
      DAT_febeb1f4 = DAT_febeb1f4 + 1;
    }
    else {
      DAT_febeb1f4 = 0;
      DAT_febeb1d0 = '\0';
      DAT_febeb200 = 0;
    }
  }
  else {
    DAT_febeb1f4 = 0;
    DAT_febeb200 = 0;
  }
  return;
}

void f33_latch_qualified_health_completion_conditions(void)

{
  if (DAT_febeb1cd == 'Z') {
    if ((DAT_000aeff8 < DAT_febeb080) && (DAT_febeb080 < DAT_000aeffa)) {
      if (DAT_febeb1fe < DAT_000aeff6) {
        DAT_febeb1fe = DAT_febeb1fe + 1;
      }
      else {
        DAT_febeb1c8 = DAT_febeb1c8 | 1;
      }
    }
    else {
      DAT_febeb1fe = 0;
      if (DAT_febeb080 <= DAT_000aeff8) {
        DAT_febeb1fe = 0;
        return;
      }
    }
    if ((DAT_febeb080 < DAT_000aeffa) && ((DAT_febeb11a & 0xff00) == 0x800)) {
      DAT_febeb1c8 = DAT_febeb1c8 | 2;
    }
  }
  return;
}

void FUN_000b4eb6(void)

{
  undefined2 uVar1;
  undefined1 uVar2;
  
  if (DAT_febeb1d4 == 'Z') {
    uVar1 = DAT_febeb202;
    uVar2 = DAT_febeb1d2;
    if (DAT_febeb1a7 == 'Z') {
      DAT_febeb1d3 = DAT_febeb1a7;
      return;
    }
  }
  else {
    uVar1 = DAT_febebede;
    uVar2 = DAT_febebef0;
    if (DAT_febeb1f0 != 1) {
      uVar1 = DAT_febeb202;
      uVar2 = DAT_febeb1d2;
    }
  }
  DAT_febeb1d2 = uVar2;
  DAT_febeb202 = uVar1;
  DAT_febeb1d3 = 0;
  return;
}

void FUN_000b50ac(void)

{
  if (((((DAT_febef204 != -0x5aa5a55b) || (DAT_febef210 != -0x5aa5a55b)) ||
       (DAT_febef214 != -0x5aa5a55b)) ||
      ((DAT_febef20c != -0x5aa5a55b || (DAT_febef21c != -0x5aa5a55b)))) ||
     (DAT_febeb218 = DAT_febef208, DAT_febef208 != -0x5aa5a55b)) {
    if (((DAT_febef204 == 0x5aa5a55a) || (DAT_febef210 == 0x5aa5a55a)) ||
       ((DAT_febef214 == 0x5aa5a55a ||
        (((DAT_febef20c == 0x5aa5a55a || (DAT_febef21c == 0x5aa5a55a)) ||
         (DAT_febef208 == 0x5aa5a55a)))))) {
      DAT_febeb218 = 0x5aa5a55a;
    }
    else if (((DAT_febef204 == 0) || (DAT_febef210 == 0)) ||
            ((DAT_febef214 == 0 ||
             (((DAT_febef20c == 0 || (DAT_febef21c == 0)) || (DAT_febef208 == 0)))))) {
      DAT_febeb218 = 0;
    }
    else {
      DAT_febeb218 = -1;
    }
  }
  return;
}

void FUN_000b51a8(void)

{
  DAT_febeb215 = 0;
  if (DAT_febeb2d0 == '\"') {
    DAT_febeb215 = 0x5a;
  }
  return;
}

void FUN_000b524a(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  FUN_000b5ec6();
  FUN_000b707a();
  FUN_000b8fa8();
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5ec))))) = 0x11;
  return;
}

void f33_fill_constant_block_b5266(void)

{
  DAT_febeb24c = 0;
  DAT_febeb24f = 0;
  DAT_febeb251 = 0;
  DAT_febeb24d = DAT_000aeba8;
  DAT_febeb252 = 0;
  DAT_febeb25a = 0;
  DAT_febeb26c = 0;
  DAT_febeb25c = 0;
  DAT_febeb24e = DAT_000aebb8;
  DAT_febeb250 = 0x5a;
  return;
}

void FUN_000b5868(uint param_1,int param_2)

{
  int iVar1;
  undefined1 uVar2;
  
  iVar1 = (param_1 & 0xff) * 4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb230u + (uint32_t)(iVar1) * 1u)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb231u + (uint32_t)(iVar1) * 1u)))) = (*((undefined1 *)camry_host_ptr((uint32_t)(param_2 + 1))));
  uVar2 = (*((undefined1 *)camry_host_ptr((uint32_t)(param_2 + 2))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb233u + (uint32_t)(iVar1) * 1u)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb232u + (uint32_t)(iVar1) * 1u)))) = uVar2;
  return;
}

void FUN_000b59d8(void)

{
  if ((DAT_febeb24f != 'Z') &&
     (DAT_febeb24f = '\0',
     (byte)(DAT_febeb248 & 0x40 |
            DAT_febeb244 & 0x20 |
            DAT_febeb240 & 0x10 |
            DAT_febeb23c & 8 | DAT_febeb238 & 4 | DAT_febeb234 & 2 | DAT_febeb230 & 1 | 0x80) ==
     0xff)) {
    DAT_febeb24f = 'Z';
  }
  return;
}

undefined4 FUN_000b5a36(void)

{
  char cVar1;
  char cVar2;
  char cVar3;
  uint32_t puVar4;
  int iVar5;
  undefined4 uVar6;
  
  cVar3 = DAT_febeb43c;
  cVar2 = DAT_febeb43b;
  cVar1 = DAT_febeb24f;
  puVar4 = 0xfebeb800u;
  iVar5 = FUN_000b6a28();
  if (((iVar5 == 0) || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x533))))) != '\0')) &&
     ((cVar1 == 'Z' || ((cVar3 == 'Z' || (cVar2 == 'Z')))))) {
    uVar6 = 0x5a;
  }
  else {
    uVar6 = 0;
  }
  return uVar6;
}

void FUN_000b5b8c(char param_1)

{
  if (param_1 == '\x01') {
    DAT_febeb224 = DAT_febeb24c;
    DAT_febeb220 = 0xa55a5aa5;
    DAT_febeb228 = DAT_febeb232;
    DAT_febeb229 = DAT_febeb236;
    DAT_febeb22a = DAT_febeb23a;
    DAT_febeb22b = DAT_febeb23e;
    DAT_febeb22c = DAT_febeb242;
    DAT_febeb22d = DAT_febeb246;
    DAT_febeb22e = DAT_febeb24a;
  }
  else {
    DAT_febeb224 = 0;
    DAT_febeb22e = 0;
    DAT_febeb220 = 0;
    DAT_febeb228 = 0;
    DAT_febeb229 = 0;
    DAT_febeb22a = 0;
    DAT_febeb22b = 0;
    DAT_febeb22c = 0;
    DAT_febeb22d = 0;
  }
  DAT_febeb226 = 0;
  DAT_febeb225 = 0;
  DAT_febeb22f = 0;
  DAT_febeb254 = 0x11;
  return;
}

undefined4 FUN_000b5c6a(void)

{
  char cVar1;
  
  cVar1 = DAT_febeb24f;
  if ((((DAT_febeb25c != '\x11') || (cVar1 = DAT_febeb43d, DAT_febeb2ce == '\x11')) ||
      (DAT_febeb24f != 'Z')) && (cVar1 != 'Z')) {
    return 0;
  }
  return 0x5a;
}

void FUN_000b5eb0(void)

{
  DAT_febeb250 = 0x5a;
  return;
}

uint f33_request_record101_reset_write(void)

{
  DAT_febeb255 = 0x11;
  return 1;
}

void FUN_000b5ec6(void)

{
  DAT_febeb256 = 0x44;
  return;
}

undefined4 f33_return_const_1_b5ed0(void)

{
  return 1;
}

undefined4 f33_return_const_ff_b5ed4(void)

{
  return 0xff;
}

void FUN_000b5eda(void)

{
  DAT_febeb26c = 0x8822;
  DAT_febeb25d = 0;
  return;
}

void FUN_000b5f00(void)

{
  DAT_febeb25c = 0x22;
  DAT_febeb25b = 0;
  DAT_febeb250 = 0x5a;
  return;
}

void FUN_000b5f28(void)

{
  DAT_febeb2d4 = 0;
  DAT_febeb2ce = 0;
  return;
}

void FUN_000b6142(uint param_1,int param_2)

{
  int iVar1;
  undefined1 uVar2;
  
  iVar1 = (param_1 & 0xff) * 4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb290u + (uint32_t)(iVar1) * 1u)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb291u + (uint32_t)(iVar1) * 1u)))) = (*((undefined1 *)camry_host_ptr((uint32_t)(param_2 + 1))));
  uVar2 = (*((undefined1 *)camry_host_ptr((uint32_t)(param_2 + 2))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb293u + (uint32_t)(iVar1) * 1u)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb292u + (uint32_t)(iVar1) * 1u)))) = uVar2;
  return;
}

void FUN_000b63ac(char param_1)

{
  if (param_1 == '\x01') {
    DAT_febeb2b0 = 0xa55a5aa5;
    DAT_febeb2b8 = DAT_febeb292;
    DAT_febeb2b9 = DAT_febeb296;
    DAT_febeb2ba = DAT_febeb29a;
    DAT_febeb2bb = DAT_febeb29e;
    DAT_febeb2bc = DAT_febeb2a2;
    DAT_febeb2bd = DAT_febeb2a6;
    DAT_febeb2be = DAT_febeb2aa;
    DAT_febeb2bf = DAT_febeb2ae;
  }
  else {
    DAT_febeb2bf = 0xff;
    DAT_febeb2b8 = 0xff;
    DAT_febeb2b0 = 0;
    DAT_febeb2b9 = 0xff;
    DAT_febeb2ba = 0xff;
    DAT_febeb2bb = 0xff;
    DAT_febeb2bc = 0xff;
    DAT_febeb2bd = 0xff;
    DAT_febeb2be = 0xff;
  }
  DAT_febeb2b4 = 0;
  DAT_febeb2c8 = 0x11;
  return;
}

void FUN_000b6624(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  DAT_febeb2c0 = 0xff;
  DAT_febeb2c1 = 0xff;
  DAT_febeb2c2 = 0xff;
  DAT_febeb2c3 = 0xff;
  DAT_febeb2c4 = 0xff;
  DAT_febeb2c5 = 0xff;
  DAT_febeb2c6 = 0xff;
  DAT_febeb2c7 = 0xff;
  DAT_febeb2cd = 0x33;
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    *(undefined4 *)(((undefined *)camry_host_ptr(0xfebeb2d8u)) + iVar3 * 4) = 0;
    iVar1 = iVar3 + -7;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  DAT_febeb2f8 = 0;
  return;
}

void FUN_000b692a(void)

{
  bool bVar1;
  
  bVar1 = DAT_febeb2ce == '\x11';
  if (bVar1) {
    DAT_febeb2ce = '\0';
  }
  if (bVar1) {
    DAT_febeb2cf = 0xff;
  }
  return;
}

void FUN_000b6944(void)

{
  bool bVar1;
  char cVar2;
  uint32_t puVar3;
  undefined1 uVar4;
  undefined1 uVar5;
  ushort uVar6;
  
  puVar3 = 0xfebeb800u;
  uVar4 = DAT_febeb2d2;
  uVar5 = DAT_febeb2cd;
  if (DAT_000aec5d == '\0') {
    uVar6 = 0x8822;
  }
  else if (((int)(uint)DAT_febeb2d4 >> 8 == 0) ||
          (uVar6 = DAT_febeb2d4, (int)(uint)DAT_febeb2d4 >> 8 == 0x88)) {
    uVar6 = 0x1111;
    puVar3 = 0xfebeb800u;
    FUN_000b6160();
    cVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x532)))));
    uVar4 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x531)))));
    bVar1 = cVar2 == '\x11';
    if (bVar1) {
      cVar2 = '\0';
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x532))))) = cVar2;
    if (bVar1) {
      uVar4 = 0xff;
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x531))))) = uVar4;
    uVar4 = 0;
    uVar5 = 0;
  }
  (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x52c)))) = uVar6;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x52e))))) = uVar4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x533))))) = uVar5;
  return;
}

void FUN_000b6990(void)

{
  if ((int)(uint)DAT_febeb2d4 >> 8 == 0x11) {
    DAT_febeb2d4 = 0x8822;
  }
  return;
}

void f33_stage_record103_byte_write(uchar selector,uchar value)

{
  bool bVar1;
  
  if ((int)(uint)DAT_febeb2d4 >> 8 == 0x11) {
    DAT_febeb2d4 = 0x8822;
  }
  bVar1 = DAT_febeb2ce == '\x11';
  if (bVar1) {
    DAT_febeb2ce = '\0';
  }
  if (bVar1) {
    DAT_febeb2cf = 0xff;
  }
  DAT_febeb2ca = 0x11;
  DAT_febeb2cc = selector;
  DAT_febeb2cb = value;
  return;
}

void FUN_000b69c6(void)

{
  bool bVar1;
  
  if ((int)(uint)DAT_febeb2d4 >> 8 == 0x11) {
    DAT_febeb2d4 = 0x8822;
  }
  bVar1 = DAT_febeb2ce == '\x11';
  if (bVar1) {
    DAT_febeb2ce = '\0';
  }
  if (bVar1) {
    DAT_febeb2cf = 0xff;
  }
  DAT_febeb2c9 = 0x11;
  return;
}

void FUN_000b69de(void)

{
  char cVar1;
  uint32_t puVar2;
  undefined1 uVar3;
  
  puVar2 = 0xfebeb800u;
  uVar3 = DAT_febeb2cf;
  if (DAT_000aec5d == '\0') {
    cVar1 = '\"';
  }
  else {
    cVar1 = DAT_febeb2ce;
    if (DAT_febeb2ce != '\x11') {
      if ((char)DAT_febeb2d4 == '\x11') {
        cVar1 = 'D';
      }
      else {
        puVar2 = 0xfebeb800u;
        FUN_000b6160();
        cVar1 = '\x11';
        uVar3 = 0;
      }
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x532))))) = cVar1;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x531))))) = uVar3;
  return;
}

void FUN_000b6a32(void)

{
  DAT_febeb302 = 0;
  return;
}

void FUN_000b6a38(void)

{
  DAT_febeb2fe = DAT_febef055;
  return;
}

void FUN_000b6a42(void)

{
  if (((DAT_febeb314 == 0) || (DAT_febeb314 == 0x33333333)) || (DAT_febeb314 == -1)) {
    DAT_febeb301 = 0;
    if (DAT_febeb2fc == 1) {
      DAT_febeb2fc = 2;
      DAT_febeb302 = 0x44;
    }
  }
  else if ((DAT_febeb2fc < 2) && (f33_published_internal_source_admission_state < 2)) {
    DAT_febeb301 = 0x5a;
  }
  else {
    DAT_febeb301 = 0;
  }
  return;
}

void FUN_000b6a8a(void)

{
  if ((DAT_febeb301 == 'Z') && (DAT_febebe89 == '\0')) {
    if (DAT_febeb2fe != DAT_febef055) {
      if (DAT_febeb2fd == 0) {
        DAT_febeb2fd = DAT_000aef50 != 0;
        DAT_febeb2ff = DAT_febebe88;
      }
      else if (DAT_febeb2ff == DAT_febebe88) {
        if (DAT_febeb2fd < DAT_000aef50) {
          DAT_febeb2fd = DAT_febeb2fd + 1;
        }
      }
      else {
        DAT_febeb2fd = 1;
        DAT_febeb2ff = DAT_febebe88;
      }
    }
  }
  else {
    DAT_febeb2fd = 0;
  }
  DAT_febeb2fe = DAT_febef055;
  return;
}

void FUN_000b6be6(void)

{
  if ((DAT_febeb302 != '\x11') && (DAT_febeb302 = 'D', (char)DAT_febeb324 != '\x11')) {
    DAT_febeb302 = '\x11';
    DAT_febeb2fc = 1;
    DAT_febeb2fd = 0;
  }
  return;
}

void FUN_000b6c14(void)

{
  if (DAT_febeb2fc == '\x01') {
    DAT_febeb302 = 0;
  }
  DAT_febeb2fc = 2;
  return;
}

void FUN_000b6c2a(void)

{
  DAT_febeb305 = DAT_febef055;
  return;
}

void FUN_000b6c34(void)

{
  if (DAT_febeb30a < DAT_000aef56) {
    DAT_febeb30a = DAT_febeb30a + 1;
  }
  else {
    DAT_febeb309 = 0x5a;
  }
  return;
}

void FUN_000b6c56(char param_1)

{
  if ((((DAT_febeb314 == 0) || (DAT_febeb314 == 0x33333333)) || (DAT_febeb314 == -1)) ||
     (1 < f33_published_internal_source_admission_state)) {
    DAT_febeb308 = 0;
  }
  else {
    DAT_febeb308 = 0x5a;
    if (DAT_febebe89 == '\0') {
      if (DAT_febeb305 == param_1) {
        DAT_febeb308 = 0x5a;
        return;
      }
      if (DAT_febeb304 == 0) {
        DAT_febeb304 = DAT_000aef54 != 0;
        DAT_febeb306 = DAT_febebe88;
        DAT_febeb308 = 0x5a;
        return;
      }
      if (DAT_febeb306 != DAT_febebe88) {
        DAT_febeb304 = 1;
        DAT_febeb306 = DAT_febebe88;
        DAT_febeb308 = 0x5a;
        return;
      }
      if (DAT_000aef54 <= DAT_febeb304) {
        DAT_febeb308 = 0x5a;
        return;
      }
      DAT_febeb304 = DAT_febeb304 + 1;
      DAT_febeb308 = 0x5a;
      return;
    }
  }
  DAT_febeb304 = 0;
  return;
}

void FUN_000b6cc8(void)

{
  if (DAT_febeb304 < DAT_000aef54) {
    if (DAT_febeb309 != 'Z') {
      return;
    }
  }
  else {
    if ((DAT_febeb314 == -0x55aaaa56) && (DAT_febeb306 == 'Z')) {
      DAT_febeb307 = 0;
      DAT_febeb30c = 0xaa5555aa;
      return;
    }
    if ((DAT_febeb314 == 0x55aaaa55) && (DAT_febeb306 == '\0')) {
      DAT_febeb307 = 0;
      DAT_febeb30c = 0x55aaaa55;
      return;
    }
  }
  DAT_febeb307 = 0x5a;
  return;
}

void FUN_000b6d20(void)

{
  undefined1 uVar1;
  uint32_t puVar2;
  uVar1 = DAT_febef055;
  puVar2 = 0xfebeb800u;
  if ((DAT_febeb30c == -0x55aaaa56) || (DAT_febeb30c == 0x55aaaa55)) {
    DAT_febeb309 = 0;
    DAT_febeb30a = 0;
  }
  else {
    puVar2 = 0xfebeb800u;
    FUN_000b6c34();
    FUN_000b6c56(uVar1);
    FUN_000b6cc8();
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x4fb))))) = uVar1;
  return;
}

void f33_fill_constant_block_b6d60(void)

{
  DAT_febeb309 = 0;
  DAT_febeb30a = 0;
  DAT_febeb304 = 0;
  DAT_febeb307 = 0;
  DAT_febeb30c = 0;
  return;
}

void FUN_000b706c(undefined4 param_1)

{
  DAT_febeb310 = 0x11;
  DAT_febeb318 = param_1;
  return;
}

void FUN_000b707a(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  FUN_000b72a2();
  FUN_000b6c14();
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x4ef))))) = 0x11;
  return;
}

void f33_stage_record102_mode_write(uint encoded_mode)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  FUN_000b72a2();
  FUN_000b6c14();
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x4ee))))) = 0x11;
  (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x4e4)))) = encoded_mode;
  return;
}

void FUN_000b70d2(void)

{
  DAT_febeb324 = 0;
  return;
}

void FUN_000b70d8(void)

{
  DAT_febeb321 = DAT_febef055;
  return;
}

void FUN_000b70e2(void)

{
  if ((DAT_000aef5a < DAT_febebede) || (1 < f33_published_internal_source_admission_state)) {
    DAT_febeb323 = 0;
  }
  else {
    DAT_febeb323 = 0x5a;
  }
  return;
}

void FUN_000b7108(void)

{
  if ((DAT_febeb323 != 'Z') || (DAT_febebe89 != '\0')) {
    DAT_febeb320 = 0;
    DAT_febeb321 = DAT_febef055;
    DAT_febeb328 = 0;
    return;
  }
  if (DAT_febeb321 == DAT_febef055) {
    DAT_febeb321 = DAT_febef055;
    DAT_febeb328 = 0;
    return;
  }
  if (DAT_febeb320 == 0) {
    DAT_febeb320 = DAT_000aef58 != 0;
    DAT_febeb322 = DAT_febebe88;
  }
  else if (DAT_febeb322 == DAT_febebe88) {
    if (DAT_000aef58 <= DAT_febeb320) goto LAB_000b715a;
    DAT_febeb320 = DAT_febeb320 + 1;
  }
  else {
    DAT_febeb320 = 1;
    DAT_febeb322 = DAT_febebe88;
  }
  if (DAT_febeb320 < DAT_000aef58) {
    DAT_febeb321 = DAT_febef055;
    DAT_febeb328 = 0;
    return;
  }
LAB_000b715a:
  if (DAT_febebe88 == 'Z') {
    DAT_febeb328 = 0xaa5555aa;
  }
  else if (DAT_febebe88 == '\0') {
    DAT_febeb328 = 0x55aaaa55;
  }
  else {
    DAT_febeb328 = 0;
    DAT_febeb320 = 0;
  }
  DAT_febeb321 = DAT_febef055;
  return;
}

undefined2 FUN_000b7186(undefined2 param_1)

{
  if (((DAT_000aef58 <= DAT_febeb320) || (DAT_febeb43c == 'Z')) || (DAT_febeb43b == 'Z')) {
    if ((DAT_febeb328 == -0x55aaaa56) || (DAT_febeb328 == 0x55aaaa55)) {
      FUN_000b706c((*((volatile uint32_t *)camry_host_ptr(0xfebeb328u))));
      param_1 = 0x2211;
    }
    else {
      FUN_000b706c(0);
      param_1 = 0x4411;
    }
  }
  return param_1;
}

undefined ** FUN_000b71f8(uint param_1)

{
  if (((DAT_febeb310 != '\0') && (DAT_febeb310 != '\x11')) && (DAT_febeb310 != '\"')) {
    if ((DAT_febeb310 == 'D') && ((int)(param_1 & 0xffff) >> 8 == 0x22)) {
      return &PTR_LAB_00008822;
    }
    return (undefined **)((undefined *)camry_host_ptr(0x8844u));
  }
  return (undefined **)(param_1 & 0xffff);
}

void FUN_000b726c(void)

{
  undefined1 uVar1;
  uint32_t puVar2;
  undefined1 uVar3;
  undefined1 uVar4;
  ushort uVar5;
  
  uVar1 = DAT_febef055;
  puVar2 = 0xfebeb800u;
  if (((int)(uint)DAT_febeb324 >> 8 == 0) ||
     (uVar4 = DAT_febeb320, uVar3 = DAT_febeb321, uVar5 = DAT_febeb324,
     (int)(uint)DAT_febeb324 >> 8 == 0x88)) {
    uVar4 = 0;
    uVar5 = 0x1111;
    puVar2 = 0xfebeb800u;
    FUN_000b6c14();
    uVar3 = uVar1;
  }
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x4dc)))) = uVar5;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x4e0))))) = uVar4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x4df))))) = uVar3;
  return;
}

void FUN_000b72a2(void)

{
  if ((int)(uint)DAT_febeb324 >> 8 == 0x11) {
    DAT_febeb324 = 0x8822;
  }
  return;
}

void FUN_000b72ba(void)

{
  DAT_febeb334 = 0;
  return;
}

void FUN_000b72ec(void)

{
  DAT_febeb333 = 2;
  DAT_febeb32c = 0;
  DAT_febeb334 = 0x22;
  DAT_febeb335 = 0;
  return;
}

void FUN_000b734e(void)

{
  DAT_febeb352 = 0;
  return;
}

void f33_fill_constant_block_b7358(void)

{
  DAT_febeb352 = 0x8822;
  DAT_febeb348 = 0;
  DAT_febeb34c = 0;
  DAT_febeb349 = 0;
  DAT_febeb34e = 0;
  return;
}

void FUN_000b736c(void)

{
  DAT_febeb354 = 0;
  return;
}

int FUN_000b7374(void)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  iVar2 = thunk_FUN_00062e12();
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x4ac))))) = iVar2 == 0;
  return iVar2;
}

void FUN_000b738c(void)

{
  DAT_febeb358 = 1;
  DAT_febeb359 = 2;
  DAT_febeb35a = 0x1e;
  return;
}

void f33_fill_constant_block_b7716(void)

{
  DAT_febeb37c = 0;
  DAT_febeb37d = 0;
  DAT_febeb380 = 0;
  DAT_febeb382 = 0;
  DAT_febeb384 = 0;
  DAT_febeb37e = 0;
  return;
}

void FUN_000b783c(void)

{
  DAT_febeb38c = DAT_000af434;
  return;
}

void FUN_000b784c(void)

{
  uint uVar1;
  int iVar2;
  
  uVar1 = (uint)(DAT_febeb138 >> 3);
  if (uVar1 != 0) {
    iVar2 = DAT_febeafe8 * -0x80;
    if (uVar1 != 0) {
      if (iVar2 == -0x80000000 && uVar1 == 0xffffffff) {
        iVar2 = 0;
      }
      else {
        iVar2 = iVar2 / (int)uVar1;
      }
    }
    DAT_febeb394 = (((iVar2 * 0x168) / 0x10) * 100) / 0x1000;
  }
  DAT_febeb398 = 0;
  if (DAT_febeb388 != '\0') {
    DAT_febeb398 = DAT_febeb394 - DAT_febeb390;
  }
  return;
}

void FUN_000b7896(void)

{
  uint32_t puVar1;
  int local_8;
  
  puVar1 = 0xfebeb800u;
  if (DAT_febeb388 == '\x02') {
    local_8 = DAT_febeb398 / 10;
    puVar1 = 0xfebeb800u;
    FUN_000d1cf6(local_8,0x7fff,(int)0xffff8001,&local_8);
  }
  else {
    (*((uint16_t *)((uint8_t *)&local_8 + 0u))) = 19999;
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x476)))) = (undefined2)local_8;
  return;
}

void FUN_000b78d0(void)

{
  uint32_t puVar1;
  short sVar2;
  
  puVar1 = 0xfebeb800u;
  sVar2 = DAT_febeb38c;
  if (DAT_febeb38c != 0) {
    sVar2 = DAT_febeb38c + -1;
  }
  FUN_000b784c();
  FUN_000b7896();
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x474)))) = sVar2;
  return;
}

void FUN_000b78ee(void)

{
  DAT_febeb390 = 0;
  DAT_febeb388 = 0;
  return;
}

undefined4 FUN_000b78f8(int param_1,int param_2)

{
  uint uVar1;
  int iVar2;
  undefined4 uVar3;
  
  uVar1 = (uint)(DAT_febeb138 >> 3);
  if (uVar1 == 0) {
    DAT_febeb388 = 0;
    uVar3 = 0x5a;
    DAT_febeb390 = 0;
  }
  else {
    uVar3 = 0;
    DAT_febeb388 = 1;
    iVar2 = (param_2 + param_1) / 2 << 7;
    if (uVar1 != 0) {
      if (iVar2 == -0x80000000 && uVar1 == 0xffffffff) {
        iVar2 = 0;
      }
      else {
        iVar2 = iVar2 / (int)uVar1;
      }
    }
    DAT_febeb390 = (((iVar2 * 0x168) / 0x10) * 100) / 0x1000;
  }
  FUN_000b784c();
  FUN_000b7896();
  return uVar3;
}

void FUN_000b794e(void)

{
  if (DAT_febeb388 != '\0') {
    DAT_febeb38a = 19999;
    DAT_febeb388 = '\x01';
  }
  return;
}

void FUN_000b7966(void)

{
  DAT_febeb388 = 2;
  FUN_000b784c();
  FUN_000b7896();
  return;
}

void FUN_000b79fa(void)

{
  DAT_febeb39c = 0;
  return;
}

void f33_fill_constant_block_b7a02(void)

{
  DAT_febeb3a1 = 0;
  DAT_febeb3a2 = 0;
  DAT_febeb3a4 = 0;
  DAT_febeb3a6 = 0;
  DAT_febeb3a0 = 0;
  return;
}

void f33_fill_constant_block_b7abe(void)

{
  DAT_febeb3a2 = 0;
  DAT_febeb3a4 = 0;
  DAT_febeb3a6 = 0;
  DAT_febeb3a0 = 0;
  DAT_febeb3a1 = 0x5a;
  return;
}

void f33_fill_constant_block_b7ad2(void)

{
  DAT_febeb3a1 = 0;
  DAT_febeb3a2 = 0;
  DAT_febeb3a4 = 0;
  DAT_febeb3a6 = 0;
  DAT_febeb3a0 = 0;
  return;
}

void f33_fill_constant_block_b7ae4(void)

{
  DAT_febeb3a8 = 0;
  DAT_febeb3aa = 0;
  DAT_febeb3b8 = 0;
  DAT_febeb3ac = 0;
  DAT_febeb3bc = 0;
  DAT_febeb3b4 = 0;
  DAT_febeb3ae = 0;
  DAT_febeb3c0 = 0;
  DAT_febeb3b0 = 0;
  DAT_febeb3b2 = 0;
  DAT_febeb3c4 = 0;
  return;
}

void f33_fill_constant_block_b7c42(void)

{
  DAT_febeb3aa = 0;
  DAT_febeb3b8 = 0;
  DAT_febeb3ac = 0;
  DAT_febeb3bc = 0;
  DAT_febeb3b4 = 0;
  DAT_febeb3ae = 0;
  DAT_febeb3c0 = 0;
  DAT_febeb3b0 = 0;
  DAT_febeb3b2 = 0;
  DAT_febeb3c4 = 0;
  DAT_febeb3a8 = 0x5a;
  return;
}

void f33_fill_constant_block_b7c62(void)

{
  DAT_febeb3a8 = 0;
  DAT_febeb3aa = 0;
  DAT_febeb3b8 = 0;
  DAT_febeb3ac = 0;
  DAT_febeb3bc = 0;
  DAT_febeb3b4 = 0;
  DAT_febeb3ae = 0;
  DAT_febeb3c0 = 0;
  DAT_febeb3b0 = 0;
  DAT_febeb3b2 = 0;
  DAT_febeb3c4 = 0;
  return;
}

void FUN_000b7c82(void)

{
  undefined1 uVar1;
  uint32_t puVar2;
  ushort uVar3;
  
  uVar3 = DAT_febeb3e0;
  puVar2 = 0xfebeb800u;
  if (DAT_febeb3cf == 'Z') {
    return;
  }
  if (DAT_febeb3e0 < DAT_000af498) {
    uVar3 = DAT_febeb3e0 + 1;
  }
  else if ((DAT_febeb3d1 == 'Z') && ((DAT_febeb3ca == '\0' || (DAT_febeb3db == '\0')))) {
    puVar2 = 0xfebeb800u;
    FUN_000b794e();
    uVar1 = 0x5a;
    goto LAB_000b7cc4;
  }
  uVar1 = 0;
LAB_000b7cc4:
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x420)))) = uVar3;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x431))))) = uVar1;
  return;
}

void FUN_000b7cd0(void)

{
  char cVar1;
  char cVar2;
  char cVar3;
  char cVar4;
  int iVar5;
  uint32_t puVar6;
  int iVar7;
  undefined1 uVar8;
  short sStack_16;
  
  cVar4 = DAT_febeb3db;
  cVar3 = DAT_febeb3d2;
  cVar2 = DAT_febeb3d1;
  cVar1 = DAT_febeb3ca;
  puVar6 = 0xfebeb800u;
  if (DAT_febeb3d0 == 'Z') {
    return;
  }
  FUN_000d1178((int)DAT_febeb054,&sStack_16);
  if (cVar3 == '\0') {
    iVar5 = (int)DAT_000af4ac;
    iVar7 = (int)sStack_16;
    if (iVar7 - iVar5 < 0 != (iVar7 < 0 != iVar5 < 0 && iVar5 < 0 == iVar7 - iVar5 < 0) ||
        iVar7 == iVar5) goto LAB_000b7d0a;
LAB_000b7d1a:
    if ((cVar2 == 'Z') && ((cVar1 == '\0' || (cVar4 == '\0')))) {
      FUN_000b794e();
      uVar8 = 0x5a;
      goto LAB_000b7d30;
    }
  }
  else {
LAB_000b7d0a:
    if (cVar3 == 'Z') {
      iVar5 = (int)DAT_000af4ae;
      iVar7 = (int)sStack_16;
      if (iVar7 - iVar5 < 0 == (iVar7 < 0 != iVar5 < 0 && iVar5 < 0 == iVar7 - iVar5 < 0) &&
          iVar7 != iVar5) goto LAB_000b7d1a;
    }
  }
  uVar8 = 0;
LAB_000b7d30:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x430))))) = uVar8;
  return;
}

uchar FUN_000b7dba(uchar phase)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_febeb3d4 == 'Z') {
    puVar1 = 0xfebeb800u;
    f33_fill_constant_block_b8a10();
    f33_fill_constant_block_b8b10();
    phase = '\x02';
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x42c))))) = 0x5a;
  return phase;
}

undefined4 FUN_000b7e66(byte param_1)

{
  undefined4 uVar1;
  
  if (DAT_febeb3ce < param_1) {
    uVar1 = 0;
    DAT_febeb3ce = DAT_febeb3ce + 1;
  }
  else {
    DAT_febeb3ce = '\0';
    uVar1 = 0x5a;
  }
  return uVar1;
}

uchar f33_update_service_minimum_excursion(uchar qualification)

{
  uint32_t puVar1;
  uchar uVar2;
  int iVar3;
  int iVar4;
  
  puVar1 = 0xfebeb800u;
  iVar3 = -DAT_febeafe8;
  iVar4 = DAT_febeb3e4;
  uVar2 = DAT_febeb3c8;
  if (DAT_febeb3c8 != 'Z') {
    if (iVar3 - DAT_febeb3e4 < 0 ==
        (iVar3 < 0 != DAT_febeb3e4 < 0 && DAT_febeb3e4 < 0 == iVar3 - DAT_febeb3e4 < 0)) {
      iVar3 = DAT_febeb3e4;
    }
    puVar1 = 0xfebeb800u;
    uVar2 = FUN_000b7e66(qualification);
    iVar4 = iVar3;
  }
  (*((int *)camry_host_ptr((uint32_t)(puVar1 + -0x41c)))) = iVar4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x438))))) = uVar2;
  return uVar2;
}

uchar FUN_000b7eb2(uchar phase)

{
  uchar uVar1;
  
  uVar1 = f33_update_service_minimum_excursion(DAT_000af494);
  if (uVar1 == 'Z') {
    f33_fill_constant_block_b8a10();
    f33_fill_constant_block_b8b10();
    phase = '\x04';
  }
  return phase;
}

uchar f33_update_service_maximum_excursion(uchar qualification)

{
  uint32_t puVar1;
  uchar uVar2;
  int iVar3;
  int iVar4;
  
  puVar1 = 0xfebeb800u;
  iVar3 = -DAT_febeafe8;
  iVar4 = DAT_febeb3e8;
  uVar2 = DAT_febeb3c9;
  if (DAT_febeb3c9 != 'Z') {
    if (iVar3 - DAT_febeb3e8 < 0 !=
        (iVar3 < 0 != DAT_febeb3e8 < 0 && DAT_febeb3e8 < 0 == iVar3 - DAT_febeb3e8 < 0) ||
        iVar3 == DAT_febeb3e8) {
      iVar3 = DAT_febeb3e8;
    }
    puVar1 = 0xfebeb800u;
    uVar2 = FUN_000b7e66(qualification);
    iVar4 = iVar3;
  }
  (*((int *)camry_host_ptr((uint32_t)(puVar1 + -0x418)))) = iVar4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x437))))) = uVar2;
  return uVar2;
}

undefined4 FUN_000b7fb8(int param_1,ushort param_2)

{
  ushort uVar1;
  uint32_t puVar2;
  undefined4 uVar3;
  short sVar4;
  int local_14;
  
  uVar1 = DAT_febeb3de;
  puVar2 = 0xfebeb800u;
  FUN_000d1194(DAT_febeb398,&local_14);
  uVar3 = 0;
  if (local_14 - param_1 < 0 ==
      (local_14 < 0 != param_1 < 0 && param_1 < 0 == local_14 - param_1 < 0) && local_14 != param_1)
  {
    sVar4 = 0;
  }
  else if (uVar1 < param_2) {
    sVar4 = uVar1 + 1;
  }
  else {
    sVar4 = 0;
    uVar3 = 0x5a;
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + -0x422)))) = sVar4;
  return uVar3;
}

uchar FUN_000b7ff4(uchar phase)

{
  char cVar1;
  uint32_t puVar2;
  int iVar3;
  undefined1 uVar4;
  
  puVar2 = 0xfebeb800u;
  iVar3 = FUN_000b7fb8(DAT_000af4b4,DAT_000af4a2);
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x42d)))));
  uVar4 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x436)))));
  if (iVar3 == 0x5a) {
    f33_fill_constant_block_b7ad2();
    f33_fill_constant_block_b7c62();
    if (cVar1 == 'Z') {
      phase = '\t';
      FUN_000b7966();
      uVar4 = 0x5a;
    }
    else {
      f33_fill_constant_block_b8872();
      phase = '\b';
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x436))))) = uVar4;
  return phase;
}

uchar FUN_000b8040(uchar phase)

{
  undefined1 uVar1;
  uint32_t puVar2;
  puVar2 = 0xfebeb800u;
  uVar1 = DAT_febeb3d3;
  if (DAT_febeb405 == 'Z') {
    puVar2 = 0xfebeb800u;
    FUN_000b8886();
    f33_fill_constant_block_b7c42();
    f33_fill_constant_block_b7abe();
    uVar1 = 0x5a;
    phase = '\a';
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x42d))))) = uVar1;
  return phase;
}

uchar FUN_000b8070(uchar phase)

{
  if (5 < phase) {
    if (phase == '\x06') {
      f33_fill_constant_block_b7c42();
      f33_fill_constant_block_b7abe();
      phase = '\a';
    }
    else if (phase < 8) {
      phase = FUN_000b7ff4(phase);
    }
    else if (phase == '\b') {
      phase = FUN_000b8040('\b');
    }
  }
  return phase;
}

undefined1 FUN_000b8116(undefined1 param_1)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_febeb3d4 == 'Z') {
    puVar1 = 0xfebeb800u;
    f33_fill_constant_block_b7c42();
    f33_fill_constant_block_b7abe();
    param_1 = 10;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x42c))))) = 0x5a;
  return param_1;
}

undefined1 FUN_000b813e(undefined1 param_1)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  iVar2 = FUN_000b7fb8(DAT_000af4b4,DAT_000af4a2);
  if (iVar2 == 0x5a) {
    f33_fill_constant_block_b7ad2();
    f33_fill_constant_block_b7c62();
    FUN_000b7966();
    param_1 = 0xb;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x425))))) = 0x5a;
  }
  return param_1;
}

uint FUN_000b8176(uint param_1)

{
  param_1 = param_1 & 0xff;
  if (param_1 == 1) {
    param_1 = FUN_000b8116((uint)(byte)param_1);
  }
  else if (param_1 == 10) {
    param_1 = FUN_000b813e((uint)(byte)param_1);
  }
  return param_1;
}

undefined1 FUN_000b82a8(undefined1 param_1)

{
  uint32_t puVar1;
  uchar uVar2;
  
  puVar1 = 0xfebeb800u;
  uVar2 = f33_update_service_minimum_excursion(DAT_000af496);
  if (uVar2 == 'Z') {
    param_1 = 0xc;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x428))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x428))))) | 1;
  }
  return param_1;
}

undefined1 FUN_000b82d6(undefined1 param_1)

{
  uint32_t puVar1;
  uchar uVar2;
  
  puVar1 = 0xfebeb800u;
  uVar2 = f33_update_service_maximum_excursion(DAT_000af496);
  if (uVar2 == 'Z') {
    param_1 = 0xc;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x428))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x428))))) | 2;
  }
  return param_1;
}

undefined1 FUN_000b8304(undefined1 param_1)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  iVar2 = FUN_000b7fb8(DAT_000af4bc,DAT_000af4aa);
  if (iVar2 == 0x5a) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x42a))))) = 0x5a;
    param_1 = 0x10;
  }
  return param_1;
}

void FUN_000b83f2(undefined1 param_1)

{
  DAT_febeb3d1 = param_1;
  return;
}

undefined4 FUN_000b8474(void)

{
  char cVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  short sStack_a;
  
  cVar1 = DAT_febeb3d2;
  FUN_000d1178((int)DAT_febeb054,&sStack_a);
  if (cVar1 == '\0') {
    iVar2 = (int)DAT_000af4ac;
    iVar4 = (int)sStack_a;
    if (iVar4 - iVar2 < 0 == (iVar4 < 0 != iVar2 < 0 && iVar2 < 0 == iVar4 - iVar2 < 0) &&
        iVar4 != iVar2) goto LAB_000b849c;
LAB_000b84ac:
    uVar3 = 0x5a;
  }
  else {
LAB_000b849c:
    if (cVar1 == 'Z') {
      iVar2 = (int)DAT_000af4ae;
      iVar4 = (int)sStack_a;
      if (iVar4 - iVar2 < 0 != (iVar4 < 0 != iVar2 < 0 && iVar2 < 0 == iVar4 - iVar2 < 0) ||
          iVar4 == iVar2) goto LAB_000b84ac;
    }
    uVar3 = 0;
  }
  return uVar3;
}

void f33_set_service_qualification_mode(uchar mode)

{
  DAT_febeb3d2 = mode;
  return;
}

void FUN_000b85a8(undefined1 param_1)

{
  DAT_febeb3d7 = param_1;
  return;
}

void FUN_000b85ae(void)

{
  DAT_febeb3dc = 0x5a;
  DAT_febeb3cb = 0;
  return;
}

void FUN_000b85bc(void)

{
  DAT_febeb3dd = 0x5a;
  DAT_febeb3cb = 0;
  return;
}

void FUN_000b85ca(void)

{
  DAT_febeb3dc = 0;
  return;
}

void FUN_000b85d0(void)

{
  DAT_febeb3dd = 0;
  return;
}

void FUN_000b8682(void)

{
  DAT_febeb3fc = 0;
  DAT_febeb3fe = 0;
  DAT_febeb400 = 0;
  DAT_febeb3fd = 0;
  return;
}

uint FUN_000b8742(char param_1)

{
  uint uVar1;
  uint uVar2;
  
  if (param_1 != 'Z') {
    return 0;
  }
  uVar2 = 0x569a;
  uVar1 = 0;
  do {
    if ((int)((ushort)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebebd34u + (uint32_t)(uVar1) * 2u)))) - uVar2) < 0) {
      uVar2 = (uint)(ushort)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebebd34u + (uint32_t)(uVar1) * 2u))));
    }
    do {
      uVar1 = uVar1 + 1 & 0xff;
      if (9 < uVar1) {
        return uVar2;
      }
    } while (uVar1 == 5);
  } while( true );
}

undefined2 f33_publish_service_engine_substitution(void)

{
  uint32_t puVar1;
  undefined2 uVar2;
  undefined1 uVar3;
  char cVar4;
  undefined2 local_e;
  
  puVar1 = 0xfebeb800u;
  if (DAT_febeb3d5 == 0) {
LAB_000b8792:
    local_e = 0;
    cVar4 = '\0';
  }
  else {
    local_e = DAT_febeb3a6;
    if (DAT_febeb3d5 == 1) {
      switch(DAT_febeb3cc) {
      case '\x02':
      case '\x04':
        cVar4 = 'Z';
        local_e = DAT_febeb436;
        break;
      case '\x03':
        cVar4 = 'Z';
        local_e = DAT_000af4c0;
        break;
      case '\x05':
        cVar4 = 'Z';
        local_e = DAT_000af4c2;
        break;
      default:
        cVar4 = '\0';
        local_e = 0;
        break;
      case '\a':
        cVar4 = 'Z';
        break;
      case '\b':
        cVar4 = 'Z';
        local_e = DAT_febeb406;
      }
    }
    else {
      if (2 < DAT_febeb3d5) {
        if (DAT_febeb3d5 == 3) {
          switch(DAT_febeb3cc) {
          case '\f':
          case '\x0f':
            cVar4 = 'Z';
            local_e = DAT_febeac56;
            break;
          case '\r':
            cVar4 = 'Z';
            local_e = DAT_000af4c4;
            break;
          case '\x0e':
            cVar4 = 'Z';
            local_e = DAT_000af4c6;
            break;
          default:
            cVar4 = '\0';
            local_e = 0;
          }
          if (cVar4 == 'Z') {
            uVar3 = 0x5a;
          }
          else {
            uVar3 = 0;
          }
          goto LAB_000b87b8;
        }
        goto LAB_000b8792;
      }
      if (DAT_febeb3cc == '\n') {
        cVar4 = 'Z';
      }
      else {
        cVar4 = '\0';
        local_e = 0;
      }
    }
  }
  uVar3 = 0;
LAB_000b87b8:
  uVar2 = FUN_000b8742(cVar4);
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x400)))) = uVar2;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x404))))) = cVar4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x403))))) = uVar3;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x402)))) = local_e;
  return uVar2;
}

void FUN_000b87d2(void)

{
  DAT_febeb3fc = 0;
  DAT_febeb3fe = 0;
  DAT_febeb400 = 0;
  DAT_febeb3fd = 0;
  return;
}

void f33_fill_constant_block_b87e2(void)

{
  DAT_febeb406 = 0;
  DAT_febeb408 = 0;
  DAT_febeb40a = 0;
  DAT_febeb404 = 0;
  DAT_febeb405 = 0;
  return;
}

void FUN_000b87f2(void)

{
  int iVar1;
  uint32_t puVar2;
  char cVar3;
  ushort uVar4;
  short sVar5;
  short sStack_12;
  
  uVar4 = DAT_febeb40a;
  sVar5 = DAT_febeb408;
  cVar3 = DAT_febeb405;
  puVar2 = 0xfebeb800u;
  if (DAT_febeb405 == '\0') {
    puVar2 = 0xfebeb800u;
    FUN_000d22c0(((undefined *)camry_host_ptr(0xaf4ccu)),DAT_febeb408,&sStack_12);
    iVar1 = (int)((uint)DAT_000af4ca * (int)sStack_12) / 0x4000;
    if (sVar5 != -1) {
      sVar5 = sVar5 + 1;
    }
    if (iVar1 == 0) {
      if (uVar4 < DAT_000af4c8) {
        uVar4 = uVar4 + 1;
      }
      else {
        cVar3 = 'Z';
      }
    }
  }
  else {
    iVar1 = 0;
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + -0x3fa)))) = (short)iVar1;
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + -0x3f8)))) = sVar5;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x3f6)))) = uVar4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x3fb))))) = cVar3;
  return;
}

void f33_fill_constant_block_b8872(void)

{
  DAT_febeb406 = 0;
  DAT_febeb408 = 0;
  DAT_febeb40a = 0;
  DAT_febeb405 = 0;
  DAT_febeb404 = 0x5a;
  return;
}

void FUN_000b8886(void)

{
  DAT_febeb404 = 0;
  DAT_febeb406 = 0;
  DAT_febeb408 = 0;
  DAT_febeb40a = 0;
  return;
}

void f33_fill_constant_block_b8896(void)

{
  DAT_febeb40c = 0;
  DAT_febeb41c = 0;
  DAT_febeb420 = 0;
  DAT_febeb40e = 0;
  DAT_febeb424 = 0;
  DAT_febeb416 = 0;
  DAT_febeb410 = 0;
  DAT_febeb428 = 0;
  DAT_febeb412 = 0;
  DAT_febeb414 = 0;
  DAT_febeb42c = 0;
  return;
}

void f33_fill_constant_block_b8a10(void)

{
  DAT_febeb41c = 0;
  DAT_febeb420 = 0;
  DAT_febeb40e = 0;
  DAT_febeb424 = 0;
  DAT_febeb416 = 0;
  DAT_febeb410 = 0;
  DAT_febeb428 = 0;
  DAT_febeb412 = 0;
  DAT_febeb414 = 0;
  DAT_febeb42c = 0;
  DAT_febeb40c = 0x5a;
  return;
}

void f33_fill_constant_block_b8a30(void)

{
  DAT_febeb40c = 0;
  DAT_febeb41c = 0;
  DAT_febeb420 = 0;
  DAT_febeb40e = 0;
  DAT_febeb424 = 0;
  DAT_febeb416 = 0;
  DAT_febeb410 = 0;
  DAT_febeb428 = 0;
  DAT_febeb412 = 0;
  DAT_febeb414 = 0;
  DAT_febeb42c = 0;
  return;
}

void f33_set_service_numeric_target(ushort target)

{
  DAT_febeb418 = target;
  return;
}

void f33_fill_constant_block_b8a54(void)

{
  DAT_febeb431 = 0;
  DAT_febeb432 = 0;
  DAT_febeb434 = 0;
  DAT_febeb436 = 0;
  DAT_febeb430 = 0;
  return;
}

void f33_fill_constant_block_b8b10(void)

{
  DAT_febeb432 = 0;
  DAT_febeb434 = 0;
  DAT_febeb436 = 0;
  DAT_febeb430 = 0;
  DAT_febeb431 = 0x5a;
  return;
}

void f33_fill_constant_block_b8b24(void)

{
  DAT_febeb431 = 0;
  DAT_febeb432 = 0;
  DAT_febeb434 = 0;
  DAT_febeb436 = 0;
  DAT_febeb430 = 0;
  return;
}

undefined4 FUN_000b8d9c(char param_1)

{
  char cVar1;
  char cVar2;
  
  cVar1 = DAT_febeb43a;
  cVar2 = DAT_febeb439;
  if ((((param_1 == '\0') || (cVar2 = DAT_febeb438, param_1 == '\x01')) ||
      (cVar1 = DAT_febeb439, param_1 == '\x02')) && ((cVar2 != '\x11' && (cVar1 != '\x11')))) {
    return 0x5a;
  }
  return 0;
}

void FUN_000b8e52(void)

{
  undefined2 uVar1;
  uint32_t puVar2;
  puVar2 = 0xfebeb800u;
  uVar1 = DAT_febeb442;
  if (DAT_febeb43a != '\x11') {
    puVar2 = 0xfebeb800u;
    FUN_000b69de();
    FUN_000b5f00();
    FUN_000b6be6();
    FUN_000b8ef0();
    FUN_000b72ec();
    uVar1 = 0;
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x3be)))) = uVar1;
  DAT_febeb43a = 0x11;
  return;
}

void FUN_000b8e8e(void)

{
  DAT_febeb446 = 1;
  DAT_febeb44c = 1;
  return;
}

void FUN_000b8e9a(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  FUN_000b8e8e();
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3bc))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x387b)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3b6))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x382f)))));
  return;
}

void thunk_FUN_000b8e8e(void)

{
  FUN_000b8e8e();
  return;
}

void FUN_000b8ec2(void)

{
  DAT_febeb462 = 0;
  return;
}

void FUN_000b8ef0(void)

{
  DAT_febeb461 = 2;
  DAT_febeb45c = 0;
  DAT_febeb462 = 0x22;
  return;
}

void FUN_000b8fa8(void)

{
  DAT_febeb471 = 0x44;
  return;
}

uint f33_stage_encoded_mode_pair(uint first,uint second)

{
  DAT_febeb472 = 0x44;
  DAT_febeb480 = first;
  DAT_febeb484 = second;
  return 0;
}

void FUN_000b8fc6(void)

{
  DAT_febeb490 = 0;
  return;
}

void FUN_000b8fd0(void)

{
  DAT_febeb490 = 0x8822;
  DAT_febeb48c = 0;
  DAT_febeb48d = 0;
  return;
}

void FUN_000b8fe2(void)

{
  DAT_febeb494 = 0;
  DAT_febeb495 = 0;
  DAT_febeb496 = 0;
  return;
}

void FUN_000b9320(undefined1 param_1)

{
  DAT_febeaf47 = param_1;
  return;
}

void FUN_000b932a(void)

{
  DAT_febeb49c = 0;
  if (DAT_febeb078 != '\0') {
    DAT_febeb49c = 0x5a;
  }
  return;
}

void f33_accumulate_profile_counter_first_a(uchar slot)

{
  int iVar1;
  int iVar2;
  int iVar3;
  short sVar4;
  int iVar5;
  int iVar6;
  uint uVar7;
  
  uVar7 = (uint)slot;
  iVar2 = uVar7 * 2;
  iVar3 = uVar7 * 4;
  sVar4 = *(short *)(((undefined *)camry_host_ptr(0xfebeb4b2u)) + iVar2);
  iVar5 = *(int *)(((undefined *)camry_host_ptr(0xfebeb554u)) + iVar3);
  if (f33_profile_qualification[uVar7] == 'Z') {
    iVar1 = (uint)DAT_febef15b - (int)sVar4;
    iVar6 = iVar1 + iVar5;
    if ((short)iVar1 < 0) {
      iVar6 = iVar6 + 0x100;
    }
  }
  else {
    iVar5 = 0;
    iVar6 = 0;
  }
  *(ushort *)(((undefined *)camry_host_ptr(0xfebeb4b2u)) + iVar2) = (ushort)DAT_febef15b;
  if (iVar6 + -0x7fff < 0 == (iVar6 < 0 && -1 < iVar6 + -0x7fff)) {
    iVar6 = 0x7fff;
  }
  if (iVar6 + 0x8000 < 0 != (-1 < iVar6 && iVar6 + 0x8000 < 0)) {
    iVar6 = -0x8000;
  }
  *(short *)(((undefined *)camry_host_ptr(0xfebeb518u)) + iVar2) = sVar4;
  *(int *)(((undefined *)camry_host_ptr(0xfebeb554u)) + iVar3) = iVar6;
  *(int *)(((undefined *)camry_host_ptr(0xfebeb540u)) + iVar3) = iVar5;
  return;
}

void f33_accumulate_profile_counter_first_b(uchar slot)

{
  int iVar1;
  int iVar2;
  int iVar3;
  short sVar4;
  int iVar5;
  int iVar6;
  uint uVar7;
  
  uVar7 = (uint)slot;
  iVar2 = uVar7 * 2;
  iVar3 = uVar7 * 4;
  sVar4 = *(short *)(((undefined *)camry_host_ptr(0xfebeb4c6u)) + iVar2);
  iVar5 = *(int *)(((undefined *)camry_host_ptr(0xfebeb57cu)) + iVar3);
  if (f33_profile_qualification[uVar7] == 'Z') {
    iVar1 = (uint)DAT_febef15c - (int)sVar4;
    iVar6 = iVar1 + iVar5;
    if ((short)iVar1 < 0) {
      iVar6 = iVar6 + 0x100;
    }
  }
  else {
    iVar5 = 0;
    iVar6 = 0;
  }
  *(ushort *)(((undefined *)camry_host_ptr(0xfebeb4c6u)) + iVar2) = (ushort)DAT_febef15c;
  if (iVar6 + -0x7fff < 0 == (iVar6 < 0 && -1 < iVar6 + -0x7fff)) {
    iVar6 = 0x7fff;
  }
  if (iVar6 + 0x8000 < 0 != (-1 < iVar6 && iVar6 + 0x8000 < 0)) {
    iVar6 = -0x8000;
  }
  *(short *)(((undefined *)camry_host_ptr(0xfebeb52cu)) + iVar2) = sVar4;
  *(int *)(((undefined *)camry_host_ptr(0xfebeb57cu)) + iVar3) = iVar6;
  *(int *)(((undefined *)camry_host_ptr(0xfebeb568u)) + iVar3) = iVar5;
  return;
}

void f33_accumulate_profile_counter_second_a(uchar slot)

{
  int iVar1;
  int iVar2;
  int iVar3;
  short sVar4;
  int iVar5;
  int iVar6;
  uint uVar7;
  
  uVar7 = (uint)slot;
  iVar2 = uVar7 * 2;
  iVar3 = uVar7 * 4;
  sVar4 = *(short *)(((undefined *)camry_host_ptr(0xfebeb4bcu)) + iVar2);
  iVar5 = *(int *)(((undefined *)camry_host_ptr(0xfebeb5a4u)) + iVar3);
  if (f33_profile_qualification[uVar7] == 'Z') {
    iVar1 = (uint)DAT_febef15d - (int)sVar4;
    iVar6 = iVar1 + iVar5;
    if ((short)iVar1 < 0) {
      iVar6 = iVar6 + 0x100;
    }
  }
  else {
    iVar5 = 0;
    iVar6 = 0;
  }
  *(ushort *)(((undefined *)camry_host_ptr(0xfebeb4bcu)) + iVar2) = (ushort)DAT_febef15d;
  if (iVar6 + -0x7fff < 0 == (iVar6 < 0 && -1 < iVar6 + -0x7fff)) {
    iVar6 = 0x7fff;
  }
  if (iVar6 + 0x8000 < 0 != (-1 < iVar6 && iVar6 + 0x8000 < 0)) {
    iVar6 = -0x8000;
  }
  *(short *)(((undefined *)camry_host_ptr(0xfebeb522u)) + iVar2) = sVar4;
  *(int *)(((undefined *)camry_host_ptr(0xfebeb5a4u)) + iVar3) = iVar6;
  *(int *)(((undefined *)camry_host_ptr(0xfebeb590u)) + iVar3) = iVar5;
  return;
}

void f33_accumulate_profile_counter_second_b(uchar slot)

{
  int iVar1;
  int iVar2;
  int iVar3;
  short sVar4;
  int iVar5;
  int iVar6;
  uint uVar7;
  
  uVar7 = (uint)slot;
  iVar2 = uVar7 * 2;
  iVar3 = uVar7 * 4;
  sVar4 = *(short *)(((undefined *)camry_host_ptr(0xfebeb4d0u)) + iVar2);
  iVar5 = *(int *)(((undefined *)camry_host_ptr(0xfebeb5ccu)) + iVar3);
  if (f33_profile_qualification[uVar7] == 'Z') {
    iVar1 = (uint)DAT_febef15e - (int)sVar4;
    iVar6 = iVar1 + iVar5;
    if ((short)iVar1 < 0) {
      iVar6 = iVar6 + 0x100;
    }
  }
  else {
    iVar5 = 0;
    iVar6 = 0;
  }
  *(ushort *)(((undefined *)camry_host_ptr(0xfebeb4d0u)) + iVar2) = (ushort)DAT_febef15e;
  if (iVar6 + -0x7fff < 0 == (iVar6 < 0 && -1 < iVar6 + -0x7fff)) {
    iVar6 = 0x7fff;
  }
  if (iVar6 + 0x8000 < 0 != (-1 < iVar6 && iVar6 + 0x8000 < 0)) {
    iVar6 = -0x8000;
  }
  *(int *)(((undefined *)camry_host_ptr(0xfebeb5ccu)) + iVar3) = iVar6;
  *(short *)(((undefined *)camry_host_ptr(0xfebeb536u)) + iVar2) = sVar4;
  *(int *)(((undefined *)camry_host_ptr(0xfebeb5b8u)) + iVar3) = iVar5;
  return;
}

void f33_run_init_chain_b975a(uchar param_1)

{
  f33_accumulate_profile_counter_first_a(param_1);
  f33_accumulate_profile_counter_first_b(param_1);
  f33_accumulate_profile_counter_second_a(param_1);
  f33_accumulate_profile_counter_second_b(param_1);
  return;
}

void f33_publish_control_profile_threshold_result(uchar slot)

{
  int iVar1;
  uchar uVar2;
  int iVar3;
  uint uVar4;
  
  uVar4 = (uint)slot;
  iVar3 = *(int *)(((undefined *)camry_host_ptr(0xfebeb644u)) + uVar4 * 4);
  uVar2 = f33_profile_threshold_result[uVar4];
  if (f33_profile_counter_pair_qualification[uVar4] == 'Z') {
    iVar1 = *(int *)(((undefined *)camry_host_ptr(0xfebeb61cu)) + uVar4 * 4) - iVar3;
    if (iVar1 < 0 ==
        (*(int *)(((undefined *)camry_host_ptr(0xfebeb61cu)) + uVar4 * 4) < 0 != iVar3 < 0 && iVar3 < 0 == iVar1 < 0)) {
      uVar2 = 'Z';
    }
    else {
      uVar2 = '\0';
    }
  }
  f33_profile_threshold_result[uVar4] = uVar2;
  return;
}

void f33_reset_control_profile_interval(uchar slot)

{
  int iVar1;
  undefined2 uVar2;
  
  uVar2 = DAT_febeb4e4;
  iVar1 = (uint)slot * 2;
  *(undefined2 *)(((undefined *)camry_host_ptr(0xfebeb4e6u)) + iVar1) = DAT_febeb4e4;
  *(undefined2 *)(((undefined *)camry_host_ptr(0xfebeb4f0u)) + iVar1) = uVar2;
  iVar1 = (uint)slot * 4;
  *(undefined4 *)(((undefined *)camry_host_ptr(0xfebeb554u)) + iVar1) = 0;
  *(undefined4 *)(((undefined *)camry_host_ptr(0xfebeb57cu)) + iVar1) = 0;
  *(undefined4 *)(((undefined *)camry_host_ptr(0xfebeb5a4u)) + iVar1) = 0;
  *(undefined4 *)(((undefined *)camry_host_ptr(0xfebeb5ccu)) + iVar1) = 0;
  *(undefined4 *)(((undefined *)camry_host_ptr(0xfebeb540u)) + iVar1) = 0;
  *(undefined4 *)(((undefined *)camry_host_ptr(0xfebeb568u)) + iVar1) = 0;
  *(undefined4 *)(((undefined *)camry_host_ptr(0xfebeb590u)) + iVar1) = 0;
  *(undefined4 *)(((undefined *)camry_host_ptr(0xfebeb5b8u)) + iVar1) = 0;
  return;
}

void f33_publish_control_profile_interval(uchar slot)

{
  int iVar1;
  int iVar2;
  uchar uVar3;
  short sVar4;
  uint uVar5;
  
  uVar5 = (uint)slot;
  iVar1 = uVar5 * 2;
  if (f33_profile_threshold_result[uVar5] == 'Z') {
    sVar4 = *(short *)(((undefined *)camry_host_ptr(0xfebeb4fau)) + iVar1);
    iVar2 = uVar5 * 4;
    *(short *)(((undefined *)camry_host_ptr(0xfebeb50eu)) + iVar1) = sVar4;
    f33_profile_qualification[uVar5] = '\0';
    *(undefined2 *)(((undefined *)camry_host_ptr(0xfebeb4fau)) + iVar1) = 0;
    *(undefined4 *)(((undefined *)camry_host_ptr(0xfebeb694u)) + iVar2) = 0;
    *(undefined4 *)(((undefined *)camry_host_ptr(0xfebeb680u)) + iVar2) = 0;
    *(undefined4 *)(((undefined *)camry_host_ptr(0xfebeb66cu)) + iVar2) = 0;
    *(undefined4 *)(((undefined *)camry_host_ptr(0xfebeb658u)) + iVar2) = 0;
    f33_reset_control_profile_interval(slot);
    uVar3 = 'Z';
  }
  else {
    sVar4 = *(short *)(((undefined *)camry_host_ptr(0xfebeb50eu)) + iVar1);
    uVar3 = '\0';
  }
  f33_profile_published_observation[uVar5] = sVar4;
  f33_profile_observation_published[uVar5] = uVar3;
  return;
}

void f33_refresh_profile_scaled_word(void)

{
  if ((DAT_febef0c0 == '\0') && (f33_published_internal_source_admission_state < 2)) {
    DAT_febebbd8 = (DAT_febef228 * 0x24ab) / 0x10000;
  }
  return;
}

void f33_refresh_profile_received_composite(void)

{
  if ((((DAT_febef069 == '\0') && (f33_published_internal_source_admission_state < 2)) &&
      (DAT_febef154 == '\x02')) && (DAT_febef06b == '\0')) {
    DAT_febeb852 = (short)DAT_febef06f + DAT_febef1a0 * 0xf;
  }
  return;
}

void f33_select_profile_source_extrema(uchar slot)

{
  undefined2 uVar1;
  uint uVar2;
  undefined2 uVar3;
  
  uVar2 = (uint)slot;
  if (f33_profile_counter_pair_qualification[uVar2] == 'Z') {
    uVar1 = *(undefined2 *)(((undefined *)camry_host_ptr(0xfebeb4e6u)) + uVar2 * 2);
    uVar3 = *(undefined2 *)(((undefined *)camry_host_ptr(0xfebeb4f0u)) + uVar2 * 2);
  }
  else {
    uVar1 = DAT_febeb4e4;
    uVar3 = DAT_febeb4e4;
    if (f33_profile_first_validity[uVar2] != 'Z') {
      uVar1 = 0;
      uVar3 = 0;
    }
  }
  *(undefined2 *)(((undefined *)camry_host_ptr(0xfebeb83eu)) + uVar2 * 2) = uVar1;
  *(undefined2 *)(((undefined *)camry_host_ptr(0xfebeb848u)) + uVar2 * 2) = uVar3;
  return;
}

void f33_integrate_control_profile_unsigned_source(uchar slot)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  undefined2 uVar4;
  undefined2 uVar5;
  
  iVar1 = (uint)slot * 2;
  iVar2 = (uint)slot * 4;
  uVar5 = *(undefined2 *)(((undefined *)camry_host_ptr(0xfebeb868u)) + iVar1);
  uVar4 = *(undefined2 *)(((undefined *)camry_host_ptr(0xfebeb872u)) + iVar1);
  uVar3 = *(uint *)(((undefined *)camry_host_ptr(0xfebebbdcu)) + iVar2);
  if ((((DAT_febef093 == '\0') && (f33_published_internal_source_admission_state < 2)) &&
      (DAT_febef094 == '\0')) && (400 < DAT_febef1b6)) {
    uVar3 = uVar3 + DAT_febef1b6;
    if (899999999 < uVar3) {
      uVar3 = 900000000;
    }
    uVar4 = (undefined2)(uVar3 / 36000);
    uVar5 = uVar4;
  }
  *(undefined2 *)(((undefined *)camry_host_ptr(0xfebeb872u)) + iVar1) = uVar4;
  *(undefined2 *)(((undefined *)camry_host_ptr(0xfebeb868u)) + iVar1) = uVar5;
  *(uint *)(((undefined *)camry_host_ptr(0xfebebbdcu)) + iVar2) = uVar3;
  return;
}

void f33_refresh_control_profile_scalar_metadata(uchar slot)

{
  undefined1 uVar1;
  uint uVar2;
  uint uVar3;
  
  uVar3 = (uint)slot;
  uVar2 = *(uint *)(((undefined *)camry_host_ptr(0xfebebbf0u)) + uVar3 * 4);
  uVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb6d0u + (uint32_t)(uVar3) * 1u))));
  if ((DAT_febef065 == '\0') && (f33_published_internal_source_admission_state < 2)) {
    uVar2 = f33_published_route31_numeric_scalar;
    uVar1 = DAT_febef067;
  }
  *(uint *)(((undefined *)camry_host_ptr(0xfebebbf0u)) + uVar3 * 4) = uVar2;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb6d0u + (uint32_t)(uVar3) * 1u)))) = uVar1;
  return;
}

void f33_reset_owner5_release_state(void)

{
  DAT_febebca8 = 0;
  DAT_febebcac = 0;
  DAT_febebcb8 = 0;
  DAT_febebca9 = 0;
  DAT_febebcae = 0;
  DAT_febebcb0 = 0;
  DAT_febebcb4 = 0;
  DAT_febebcaa = 0;
  DAT_febebcab = 0x5a;
  return;
}

void f33_reset_owner4_release_state(void)

{
  DAT_febebcc0 = 0x569a;
  DAT_febebcc2 = 0x569a;
  DAT_febebcbc = 0;
  DAT_febebcbd = 0;
  DAT_febebcbe = 0;
  DAT_febebcc4 = 0x569a0000;
  return;
}

uint f33_force_owner4_nominal_request(void)

{
  DAT_febebcbc = 0;
  DAT_febebcc4 = 0;
  return 0x569a;
}

uint f33_force_owner4_zero_request(void)

{
  DAT_febebcbc = 0;
  DAT_febebcc4 = 0;
  return 0;
}

void f33_set_owner4_limit_mode(uint mode)

{
  DAT_febebcbd = (char)mode;
  return;
}

void f33_reset_owner8_release_state(void)

{
  DAT_febebcd4 = 0x569a;
  DAT_febebcd6 = 0x569a;
  DAT_febebcd0 = 0;
  DAT_febebcd2 = 0;
  DAT_febebcdc = 0x569a0000;
  return;
}

void f33_reset_owner1_qualification_state(void)

{
  DAT_febebce2 = 0x5a;
  DAT_febebce0 = 0;
  DAT_febebce4 = 0;
  DAT_febebce5 = 0;
  DAT_febebce1 = 0;
  DAT_febebce3 = 0;
  DAT_febebce8 = 0x569a;
  DAT_febebce6 = 0;
  DAT_febebcec = 0;
  return;
}

void f33_initialize_owner1_persisted_admission(void)

{
  int iVar1;
  int iVar2;
  
  if (DAT_febef027 == 'Z') {
    if ((DAT_febef1e0 == 0) &&
       (iVar2 = (int)DAT_000af060, iVar1 = DAT_febef182 - iVar2,
       iVar1 < 0 != (DAT_febef182 < 0 != iVar2 < 0 && iVar2 < 0 == iVar1 < 0))) {
      DAT_febebce2 = 0x5a;
    }
    else {
      DAT_febebce2 = 0;
    }
    DAT_febebce3 = 0x5a;
  }
  return;
}

void f33_reset_owner1_limit_request(void)

{
  DAT_febebcf0 = 0x569a;
  return;
}

void f33_initialize_lifecycle_difference_monitor(void)

{
  f33_reset_application_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebebcf4u)))));
  return;
}

void f33_reset_lifecycle_difference_monitor_entry(void)

{
  f33_reset_application_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebebcf4u)))));
  return;
}

void f33_reset_owner6_calibration_envelope(void)

{
  DAT_febebd18 = 0x569a0000;
  DAT_febebd00 = 0;
  DAT_febebd01 = 0;
  DAT_febebd10 = DAT_febeafdc;
  DAT_febebd02 = 0;
  DAT_febebd2c = (int)DAT_febeafdc << 0x10;
  DAT_febebd06 = 0x569a;
  DAT_febebd08 = DAT_febeb084;
  DAT_febebd1c = (uint)DAT_febeb084 << 0x10;
  DAT_febebd20 = 0;
  DAT_febebd03 = 0;
  DAT_febebd0a = 0;
  DAT_febebd0e = DAT_febeb084;
  DAT_febebd24 = (uint)DAT_febeb084 << 0x10;
  DAT_febebd04 = 0;
  DAT_febebd0c = 0x569a;
  DAT_febebd28 = 0;
  DAT_febebd12 = 0x569a;
  DAT_febebd14 = 0x569a;
  DAT_febebd30 = 0x569a;
  DAT_febebd16 = 0x569a;
  return;
}

void f33_select_owner6_calibration_family(void)

{
  DAT_febebd20 = DAT_febeb30c;
  if ((DAT_febeb30c != 0x55aaaa55) && (DAT_febeb30c != -0x55aaaa56)) {
    DAT_febebd20 = DAT_000af1b8;
  }
  return;
}

void f33_set_current_limit_request(uint owner,ushort limit)

{
  if ((owner & 0xff) < 10) {
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebebd34u + (uint32_t)(owner & 0xff) * 2u)))) = limit;
  }
  return;
}

uint f33_reduce_thermal_current_requests(void)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  
  uVar4 = 0x569a;
  uVar3 = 0;
  do {
    if ((((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xaf0ccu + (uint32_t)(uVar3 >> 5) * 4u)))) >> (uVar3 & 0x1f) & 1) != 0) &&
       ((int)((ushort)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebebd34u + (uint32_t)(uVar3) * 2u)))) - uVar4) < 0)) {
      uVar4 = (uint)(ushort)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebebd34u + (uint32_t)(uVar3) * 2u))));
    }
    uVar2 = uVar3 + 1;
    iVar1 = uVar3 - 9;
    uVar3 = uVar2;
  } while (iVar1 < 0 != ((int)uVar2 < 0 && -1 < iVar1));
  return uVar4;
}

uint f33_reduce_other_current_requests(void)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  
  uVar4 = 0x569a;
  uVar3 = 0;
  do {
    if ((((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xaf0ccu + (uint32_t)(uVar3 >> 5) * 4u)))) >> (uVar3 & 0x1f) & 1) == 0) &&
       ((int)((ushort)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebebd34u + (uint32_t)(uVar3) * 2u)))) - uVar4) < 0)) {
      uVar4 = (uint)(ushort)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebebd34u + (uint32_t)(uVar3) * 2u))));
    }
    uVar2 = uVar3 + 1;
    iVar1 = uVar3 - 9;
    uVar3 = uVar2;
  } while (iVar1 < 0 != ((int)uVar2 < 0 && -1 < iVar1));
  return uVar4;
}

uint f33_reduce_service_current_requests(void)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  
  uVar4 = 0x569a;
  uVar3 = 0;
  do {
    if (((f33_service_current_owner_exclusions >> (uVar3 & 0x1f) & 1) == 0) &&
       ((int)((ushort)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebebd34u + (uint32_t)(uVar3) * 2u)))) - uVar4) < 0)) {
      uVar4 = (uint)(ushort)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebebd34u + (uint32_t)(uVar3) * 2u))));
    }
    uVar2 = uVar3 + 1;
    iVar1 = uVar3 - 9;
    uVar3 = uVar2;
  } while (iVar1 < 0 != ((int)uVar2 < 0 && -1 < iVar1));
  return uVar4;
}

void FUN_000bb87a(void)

{
  DAT_febebd48 = 0;
  DAT_febebd4a = 0;
  DAT_febebd4c = 0x569a;
  DAT_febebd4e = 0x569a;
  return;
}

void FUN_000bbb3c(void)

{
  byte bVar1;
  uint32_t puVar2;
  short sVar3;
  short sStack_a;
  
  puVar2 = 0xfebeb800u;
  if (DAT_febebd84 < 0x927c) {
    sVar3 = DAT_febebd84 + 1;
  }
  else {
    sVar3 = -0x6d84;
  }
  FUN_000d1e8c(((undefined *)camry_host_ptr(0xaee60u)),sVar3,&sStack_a);
  bVar1 = DAT_000aee34;
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0x584)))) = sVar3;
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0x560)))) = sStack_a;
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0x562)))) = (short)(((int)(short)(ushort)bVar1 * (int)sStack_a) / 0x80);
  return;
}

void FUN_000bbe26(void)

{
  if ((DAT_febeb1a7 == DAT_febebd50) || (DAT_febeb1a7 != 'Z')) {
    DAT_febebd52 = '\0';
  }
  else {
    DAT_febebd52 = 'Z';
  }
  if (((DAT_febebcb0 == 0) && (DAT_febeb1bc == 'Z')) && (DAT_febebd53 == '\0')) {
    DAT_febebd53 = 'Z';
  }
  if (DAT_febebd52 != 'Z') {
    if ((DAT_febebcb0 == 0) || (DAT_febebd53 != 'Z')) {
      DAT_febebd52 = '\0';
    }
    else {
      DAT_febebd53 = '\0';
      DAT_febebd52 = 'Z';
    }
  }
  DAT_febebd50 = DAT_febeb1a7;
  return;
}

void f33_reset_owner3_shutdown_request(void)

{
  DAT_febebd9e = 0x569a;
  DAT_febebd9c = 0;
  DAT_febebd9d = 0;
  DAT_febebda0 = 0;
  DAT_febebda4 = 0x569a0000;
  return;
}

void f33_reset_owner3_signal_qualification(void)

{
  DAT_febebda8 = 0;
  DAT_febebda9 = 0;
  DAT_febebdac = DAT_000af110;
  DAT_febebdae = DAT_000af112;
  return;
}

void f33_set_owner3_entry_inhibit(uint inhibit)

{
  DAT_febebdaa = (char)inhibit;
  return;
}

void f33_reset_owner2_deficit_request(void)

{
  DAT_febebdb0 = 0;
  DAT_febebdb1 = 0;
  DAT_febebdb4 = 0x569a;
  DAT_febebdb6 = 0;
  DAT_febebdb8 = 0;
  DAT_febebdba = 0;
  DAT_febebdbc = 0x569a;
  DAT_febebdbe = DAT_000af144;
  DAT_febebdc0 = DAT_000af13e;
  DAT_febebdc2 = DAT_000af140;
  DAT_febebdc8 = 0x569a;
  DAT_febebdd0 = 0;
  DAT_febebdc4 = DAT_000af142;
  DAT_febebdcc = 0x569a0000;
  DAT_febebdd4 = 0;
  DAT_febebdd8 = 0;
  return;
}

void f33_set_owner2_entry_inhibit(uint inhibit)

{
  DAT_febebdb2 = (char)inhibit;
  return;
}

void f33_fill_constant_block_bc648(void)

{
  DAT_febebde0 = 0;
  DAT_febebde1 = 0;
  DAT_febebde2 = 0;
  DAT_febebde3 = 0;
  DAT_febebde4 = 0;
  DAT_febebde6 = 0;
  DAT_febebde8 = 0;
  DAT_febebdea = 0;
  return;
}

void f33_fill_constant_block_bc7be(void)

{
  DAT_febebdec = 0;
  DAT_febebded = 0;
  DAT_febebdf0 = 0;
  DAT_febebdf2 = 0;
  DAT_febebdf4 = 0;
  return;
}

void FUN_000bc93a(undefined1 param_1)

{
  DAT_febebdee = param_1;
  return;
}

void FUN_000bc958(void)

{
  DAT_febeac01 = 0;
  if (DAT_febeee14 != '\0') {
    DAT_febeac01 = 0x5a;
  }
  return;
}

void FUN_000bd86e(undefined1 param_1)

{
  DAT_febeacec = param_1;
  FUN_000d1160();
  return;
}

void FUN_000bdb8e(void)

{
  DAT_febebe1c = 0;
  return;
}

void FUN_000bdb98(void)

{
  DAT_febebe20 = 0;
  DAT_febebe21 = 0;
  DAT_febebe22 = 0;
  DAT_febebe23 = 0;
  return;
}

void f33_fill_constant_block_bdba8(void)

{
  DAT_febebe28 = 0;
  DAT_febebe2a = 0;
  DAT_febebe2c = 0;
  DAT_febebe2e = 0;
  DAT_febebe30 = 0;
  DAT_febebe24 = 0;
  DAT_febebe25 = 0;
  DAT_febebe26 = 0;
  return;
}

void f33_scale_staged_byte_pair_to_control_raw(void)

{
  f33_scaled_staged_byte_a = (ushort)((uint)((short)(ushort)DAT_febef03d * 0x147b) >> 0xc);
  f33_scaled_staged_byte_b = (ushort)((uint)((short)(ushort)DAT_febef03e * 0x147b) >> 0xc);
  return;
}

void f33_seed_health_received_source_filter(void)

{
  undefined1 uVar1;
  uint uVar2;
  uint32_t puVar3;
  int local_c;
  
  uVar1 = DAT_febef052;
  puVar3 = 0xfebeb800u;
  FUN_000d1222((int)DAT_febef194,&local_c);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x678))))) = uVar1;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x67b))))) = 0;
  uVar2 = (uint)(local_c * 800) >> 10;
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0x682)))) = (short)uVar2;
  (*((uint *)camry_host_ptr((uint32_t)(puVar3 + 0x684)))) = uVar2 << 0x10;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x67a))))) = 0x5a;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x679))))) = 0x5a;
  return;
}

void f33_refresh_second_health_source_cache(void)

{
  if (DAT_febef052 == '\x01') {
    DAT_febebe7a = 0xa5;
    DAT_febebe7b = true;
  }
  else {
    DAT_febebe7a = 0xff;
    if (DAT_febef052 == '\0') {
      DAT_febebe7a = 0x5a;
    }
    DAT_febebe7b = DAT_febeb18f == 'Z';
  }
  DAT_febebe78 = DAT_febef052;
  return;
}

void f33_refresh_health_channel_classifications(void)

{
  if ((DAT_febef00b == '\0') && (DAT_febef00c == '\0')) {
    DAT_febebe7c = DAT_febef057 & 1;
    if ((DAT_febef057 & 1) == 0) goto LAB_000be74a;
  }
  else if ((DAT_febef00b == '\"') || (DAT_febef00c == '\"')) {
    DAT_febebe7c = 0x22;
    goto LAB_000be74a;
  }
  DAT_febebe7c = 0x11;
LAB_000be74a:
  if ((DAT_febef00d == '\0') && (DAT_febef00e == '\0')) {
    if ((DAT_febef051 & 1) == 0) {
      DAT_febebe7d = DAT_febef051 & 1;
      return;
    }
  }
  else if ((DAT_febef00d == '\"') || (DAT_febef00e == '\"')) {
    DAT_febebe7d = 0x22;
    return;
  }
  DAT_febebe7d = 0x11;
  return;
}

void FUN_000be798(void)

{
  DAT_febebe88 = 0;
  if (DAT_febef056 == '\x01') {
    DAT_febebe88 = 0x5a;
  }
  return;
}

void FUN_000be7ac(void)

{
  if ((((DAT_febef003 == '\0') && (DAT_febef005 == '\0')) && (DAT_febef004 == '\0')) &&
     (DAT_febef006 == '\0')) {
    if ((DAT_febef054 & 1) == 0) {
      DAT_febebe89 = DAT_febef054 & 1;
      return;
    }
  }
  else if (((DAT_febef003 == '\"') || (DAT_febef005 == '\"')) ||
          ((DAT_febef004 == '\"' || (DAT_febef006 == '\"')))) {
    DAT_febebe89 = 0x22;
    return;
  }
  DAT_febebe89 = 0x11;
  return;
}

void FUN_000be7fa(void)

{
  FUN_000be798();
  FUN_000be7ac();
  return;
}

void f33_publish_first_fixed_received_marker(void)

{
  DAT_febebed4 = 0x55aaaa55;
  DAT_febebe9d = 0;
  DAT_febebeb3 = 0;
  DAT_febebea7 = 0x5a;
  return;
}

void f33_publish_second_fixed_received_marker(void)

{
  DAT_febebed8 = 0x55aaaa55;
  DAT_febebe9e = 0;
  DAT_febebeb4 = 0;
  DAT_febebea8 = 0x5a;
  return;
}

void f33_initialize_fixed_received_markers(void)

{
  f33_publish_first_fixed_received_marker();
  f33_publish_second_fixed_received_marker();
  return;
}

void f33_qualify_received_scalar_startup(void)

{
  if (DAT_febebea2 == '\0') {
    DAT_febebeac = 0;
    if (f33_published_internal_source_admission_state < 2) {
      if (DAT_febebec4 < DAT_000af406) {
        DAT_febebec4 = DAT_febebec4 + 1;
      }
      else {
        DAT_febebea2 = 'Z';
        DAT_febebe98 = 0;
      }
    }
    else {
      DAT_febebec4 = 0;
    }
  }
  DAT_febebead = 0;
  DAT_febebeae = DAT_febebe98;
  return;
}

void f33_qualify_received_channel_b_startup(void)

{
  if (DAT_febebea3 == '\0') {
    if (((f33_published_internal_source_admission_state < 2) && (DAT_febef028 == '\0')) &&
       (DAT_febef02b == '\x01')) {
      if (DAT_febebebc < DAT_000af3fe) {
        DAT_febebebc = DAT_febebebc + 1;
      }
      else {
        DAT_febebea3 = 'Z';
        DAT_febebe99 = DAT_febebea3;
      }
    }
    else {
      DAT_febebebc = 0;
    }
  }
  DAT_febebeaf = 0;
  return;
}

void f33_qualify_received_channel_c_startup(void)

{
  if (DAT_febebea4 == '\0') {
    if ((f33_published_internal_source_admission_state < 2) && (DAT_febef060 == '\0')) {
      if (DAT_febebebe < DAT_000af400) {
        DAT_febebebe = DAT_febebebe + 1;
      }
      else {
        DAT_febebea4 = 'Z';
        DAT_febebe9a = DAT_febebea4;
      }
    }
    else {
      DAT_febebebe = 0;
    }
  }
  DAT_febebeb0 = 0;
  return;
}

void f33_qualify_received_channel_d_startup(void)

{
  if (DAT_febebea5 == '\0') {
    if ((f33_published_internal_source_admission_state < 2) && (DAT_febef069 == '\0')) {
      if (DAT_febebec0 < DAT_000af402) {
        DAT_febebec0 = DAT_febebec0 + 1;
      }
      else {
        DAT_febebea5 = 'Z';
        DAT_febebe9b = DAT_febebea5;
      }
    }
    else {
      DAT_febebec0 = 0;
    }
  }
  DAT_febebeb2 = DAT_febebe9b;
  return;
}

void f33_qualify_received_channel_e_startup(void)

{
  if (DAT_febebea6 == '\0') {
    if ((f33_published_internal_source_admission_state < 2) && (DAT_febef04c == '\0')) {
      if (DAT_febebec2 < DAT_000af404) {
        DAT_febebec2 = DAT_febebec2 + 1;
      }
      else {
        DAT_febebea6 = 'Z';
        DAT_febebe9c = DAT_febebea6;
      }
    }
    else {
      DAT_febebec2 = 0;
    }
  }
  DAT_febebeb1 = DAT_febebe9c;
  return;
}

void f33_publish_received_channel_f_defaults(void)

{
  DAT_febebe9f = 0x5a;
  DAT_febebeb6 = 0x5a;
  return;
}

void f33_publish_received_channel_g_default(void)

{
  DAT_febebea0 = 0x5a;
  return;
}

void f33_publish_received_channel_h_default(void)

{
  DAT_febebea1 = 0x5a;
  return;
}

void f33_publish_fixed_received_channel_defaults(void)

{
  f33_publish_received_channel_f_defaults();
  f33_publish_received_channel_g_default();
  f33_publish_received_channel_h_default();
  return;
}

void f33_clear_fixed_received_metadata(void)

{
  DAT_febebeb8 = 0;
  DAT_febebeb5 = 0;
  return;
}

void f33_qualify_received_paired_channel_startup(void)

{
  if (DAT_febebebb == '\0') {
    if ((f33_published_internal_source_admission_state < 2) &&
       ((DAT_febef148 == '\0' || (DAT_febef149 == '\0')))) {
      if (DAT_febebed0 < DAT_000af40e) {
        DAT_febebed0 = DAT_febebed0 + 1;
      }
      else {
        DAT_febebebb = 'Z';
        DAT_febebeba = DAT_febebebb;
      }
    }
    else {
      DAT_febebed0 = 0;
    }
  }
  DAT_febebeb7 = DAT_febebeba;
  return;
}

void f33_publish_received_startup_delay_default(void)

{
  DAT_febebead = 0;
  return;
}

void FUN_000becd0(void)

{
  DAT_febebedd = 0;
  if (((f33_published_internal_source_admission_state < 2) && (DAT_febef093 == '\0')) &&
     (DAT_febef013 == '\0')) {
    DAT_febebedd = 0x5a;
  }
  return;
}

void FUN_000beda2(void)

{
  DAT_febebee4 = 0;
  DAT_febebee0 = 0;
  DAT_febebeec = 0;
  DAT_febebee2 = 0;
  DAT_febebee8 = 0;
  if (DAT_febebef0 == '\x11') {
    DAT_febebee0 = 0x5a;
  }
  DAT_febebee1 = 0;
  return;
}

void FUN_000bef22(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  DAT_febebef0 = 0x11;
  iVar3 = 0;
  do {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebebef1u + (uint32_t)(iVar3) * 1u)))) = 0;
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -1;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  return;
}

void FUN_000bef3e(void)

{
  int iVar1;
  int iVar2;
  char cVar3;
  int iVar4;
  
  cVar3 = DAT_febebedc;
  if (((DAT_febebedc != '\x11') && (DAT_febebedc != 'D')) &&
     (cVar3 = DAT_febebef0, DAT_febebef0 != 'D')) {
    cVar3 = '\"';
  }
  iVar4 = 0;
  do {
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebebef1u + (uint32_t)(iVar4) * 1u)))) != '\0') {
      cVar3 = 'D';
    }
    iVar2 = iVar4 + 1;
    iVar1 = iVar4 + -1;
    iVar4 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  DAT_febebef0 = cVar3;
  return;
}

void FUN_000bef80(uint param_1)

{
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebebef1u + (uint32_t)(param_1 & 0xff) * 1u)))) = 0x5a;
  return;
}

void FUN_000bef8e(uint param_1)

{
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebebef1u + (uint32_t)(param_1 & 0xff) * 1u)))) = 0;
  return;
}

void f33_update_acquired_scalar_hysteresis(void)

{
  char cVar1;
  int iVar2;
  uint32_t puVar3;
  int iVar4;
  undefined1 uVar5;
  short sStack_12;
  
  uVar5 = DAT_febebf11;
  cVar1 = DAT_000aef88;
  puVar3 = 0xfebeb800u;
  FUN_000d1178((int)DAT_febeafe0,&sStack_12);
  iVar2 = (int)sStack_12;
  iVar4 = (int)DAT_000aef8a;
  if ((iVar2 - iVar4 < 0 == (iVar2 < 0 != iVar4 < 0 && iVar4 < 0 == iVar2 - iVar4 < 0)) &&
     (cVar1 == 'Z')) {
    uVar5 = 0x5a;
  }
  else {
    iVar4 = (int)DAT_000aef8c;
    if ((iVar2 - iVar4 < 0 != (iVar2 < 0 != iVar4 < 0 && iVar4 < 0 == iVar2 - iVar4 < 0) ||
         iVar2 == iVar4) || (cVar1 != 'Z')) {
      uVar5 = 0;
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x711))))) = uVar5;
  return;
}

void f33_debounce_acquired_scalar_hysteresis(void)

{
  if (DAT_febebf11 == 'Z') {
    if (DAT_febebf12 <= DAT_000aef8e) {
      DAT_febebf14 = 0;
      DAT_febebf12 = DAT_febebf12 + 1;
    }
  }
  else if (DAT_febebf14 <= DAT_000aef8e) {
    DAT_febebf12 = 0;
    DAT_febebf14 = DAT_febebf14 + 1;
  }
  if (DAT_febebf10 == '\0') {
    DAT_febebf10 = DAT_000aef8e < DAT_febebf12;
  }
  else if (DAT_000aef8e < DAT_febebf14) {
    DAT_febebf10 = '\0';
  }
  return;
}

void f33_refresh_acquired_scalar_status_publication(void)

{
  f33_update_acquired_scalar_hysteresis();
  f33_debounce_acquired_scalar_hysteresis();
  return;
}

void f33_fill_constant_block_bf33e(void)

{
  DAT_febee408 = DAT_febeac58;
  DAT_febee40a = DAT_febeac56;
  DAT_febee40c = DAT_febeac54;
  DAT_febee40e = DAT_febeac70;
  DAT_febee400 = DAT_febeac2d;
  DAT_febee410 = DAT_febeac76;
  DAT_febee401 = 0;
  DAT_febee402 = 0;
  DAT_febee412 = DAT_febeac7a;
  DAT_febee404 = 0;
  DAT_febee403 = DAT_febeac39;
  DAT_febee414 = DAT_febeac7e;
  DAT_febee405 = DAT_febeac3e;
  DAT_febee416 = DAT_febeb3fe;
  DAT_febee406 = DAT_febeb3fc;
  DAT_febee418 = DAT_febeb400;
  DAT_febee407 = DAT_febeb354;
  return;
}

void f33_initialize_cold_control_retained_state(void)

{
  f33_health_cached_route30_generation = '\0';
  DAT_febebead = 0;
  DAT_febebe6c = 0;
  DAT_febebe63 = 0;
  DAT_febebe61 = 0;
  DAT_febebf10 = 0;
  f33_health_receive_generation_armed = '\0';
  f33_previous_health_receive_generation = '\0';
  DAT_febebef4 = 1;
  DAT_febebd56 = 0;
  DAT_febebd55 = 0;
  DAT_febebd54 = 0;
  DAT_febebd84 = 0;
  DAT_febebd7e = 0;
  DAT_febebd6c = 0;
  DAT_febebd6a = 0;
  DAT_febebd90 = 0;
  DAT_febebd68 = 0;
  DAT_febebd66 = 0;
  DAT_febebd64 = 0;
  DAT_febebd8c = 0;
  DAT_febebd62 = 0;
  DAT_febebd60 = 0;
  DAT_febebd5e = 0;
  DAT_febebd88 = 0;
  DAT_febebd5c = 0;
  DAT_febebd5a = 0;
  DAT_febebd58 = 0;
  DAT_febebe8c = 1;
  DAT_febebca4 = 1;
  DAT_febebca6 = 0;
  return;
}

void f33_snapshot_control_ch2_acquisition(void)

{
  DAT_febeaf78 = DAT_febeec04;
  DAT_febeaf7a = DAT_febeec06;
  DAT_febeaf7c = DAT_febeec08;
  DAT_febeaf7e = DAT_febeec0a;
  DAT_febeaf80 = DAT_febeec0c;
  DAT_febeaf88 = DAT_febeec14;
  DAT_febeaf8c = DAT_febeec18;
  DAT_febeaf90 = DAT_febeec1c;
  DAT_febeaf94 = DAT_febeec20;
  DAT_febeaf82 = DAT_febeec0e;
  DAT_febeaf98 = DAT_febeec24;
  DAT_febeaf74 = DAT_febeec00;
  DAT_febeaf75 = DAT_febeec01;
  DAT_febeaf76 = DAT_febeec02;
  DAT_febeaf84 = DAT_febeec10;
  return;
}

void f33_snapshot_control_foreground_acquisition(void)

{
  DAT_febeafd8 = DAT_febeec04;
  DAT_febeafda = DAT_febeec06;
  DAT_febeafdc = DAT_febeec08;
  DAT_febeafde = DAT_febeec0a;
  DAT_febeafe0 = DAT_febeec0c;
  DAT_febeafe8 = DAT_febeec14;
  DAT_febeafec = DAT_febeec18;
  DAT_febeaff0 = DAT_febeec1c;
  DAT_febeaff4 = DAT_febeec20;
  DAT_febeafe2 = DAT_febeec0e;
  DAT_febeaff8 = DAT_febeec24;
  DAT_febeafd4 = DAT_febeec00;
  DAT_febeafd5 = DAT_febeec01;
  DAT_febeafd6 = DAT_febeec02;
  DAT_febeafe4 = DAT_febeec10;
  return;
}

void FUN_000c28ae(void)

{
  DAT_febebf3c = 0;
  DAT_febebf40 = 0;
  DAT_febebf18 = 0;
  DAT_febebf1c = 0;
  DAT_febebf34 = 0;
  DAT_febebf36 = 0;
  DAT_febebf20 = 0;
  DAT_febebf24 = 0;
  DAT_febebf28 = 0;
  DAT_febebf2c = f33_calibration_bank_bases[DAT_febeac3c & 1];
  DAT_febebf38 = 0;
  DAT_febebf3a = 0;
  DAT_febebf30 = f33_calibration_bank_bases[DAT_febeac3c & 1] + 0x44;
  return;
}

void f33_fill_constant_block_c2c78(void)

{
  DAT_febebf44 = 1;
  DAT_febebf45 = 1;
  DAT_febebf46 = 1;
  DAT_febebf47 = 1;
  DAT_febebf48 = 0;
  DAT_febebf49 = 0;
  DAT_febebf4a = 0;
  DAT_febebf4b = 1;
  DAT_febebf4c = 0;
  return;
}

undefined4 FUN_000c2ca0(uint param_1,uint param_2)

{
  if (((param_1 & 0xff) == 0) && ((param_2 & 0xff) == 0)) {
    return 0;
  }
  if ((((param_1 & 0xff) >> 1 & 1) == 0) && (((param_2 & 0xff) >> 1 & 1) == 0)) {
    return 1;
  }
  return 2;
}

undefined1 FUN_000c2cc0(void)

{
  byte bVar1;
  undefined1 uVar2;
  uint32_t puVar3;
  undefined1 uVar4;
  
  uVar2 = DAT_febeacc1;
  puVar3 = 0xfebeb800u;
  uVar4 = FUN_000c2ca0(DAT_febeacc1,0);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x744))))) = uVar4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x745))))) = uVar2;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x746))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xa91)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x747))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xa90)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x748))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xb29))))) & 1;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x749))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xb30))))) & 1;
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xb2d))))) & 1) != 0) || (bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xb2e))))) & 1, ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xb2e))))) & 1) != 0)) {
    bVar1 = 1;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x74a))))) = bVar1;
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xa8f))))) != '\0') || (uVar2 = 0, (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xa8e))))) != '\0')) {
    uVar2 = 1;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x74b))))) = uVar2;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x74c))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xa24))))) != '\x02';
  return uVar4;
}

void f33_clear_observer_source_term(void)

{
  DAT_febeaba4 = 0;
  DAT_febebfc4 = 0;
  DAT_febebf6d = 0;
  DAT_febebf6e = 0;
  DAT_febebfc5 = 0;
  return;
}

void FUN_000c2ed0(void)

{
  if ((((((DAT_febeacda == '\0') && (DAT_febeacd9 == '\0')) && (DAT_febeace9 == '\0')) &&
       ((DAT_febeacea == '\0' && (DAT_febeacc0 == '\x01')))) &&
      ((DAT_febeacdc == '\0' && ((DAT_febeacdd == '\0' && (DAT_febeacde == '\0')))))) &&
     ((DAT_febeace3 == '\0' && (DAT_febeace4 == '\0')))) {
    DAT_febebfb0 = 0x5a;
  }
  else {
    DAT_febebfb0 = 0;
  }
  return;
}

void FUN_000c2f26(void)

{
  if ((((((DAT_febeacdb == '\0') && (DAT_febeacd9 == '\0')) && (DAT_febeace7 == '\0')) &&
       ((DAT_febeace8 == '\0' && (DAT_febeacc0 == '\x01')))) &&
      ((DAT_febeacdf == '\0' && ((DAT_febeace1 == '\0' && (DAT_febeace0 == '\0')))))) &&
     (DAT_febebf4b == '\0')) {
    DAT_febebfb1 = 0x5a;
  }
  else {
    DAT_febebfb1 = 0;
  }
  return;
}

void FUN_000c2f78(void)

{
  if ((((DAT_febebf44 == '\0') && (DAT_febeacbd < 2)) && (DAT_febeacc4 == '\0')) &&
     ((DAT_febeacc2 == '\0' && (DAT_febebf4c == '\0')))) {
    DAT_febebfae = 0x5a;
  }
  else {
    DAT_febebfae = 0;
  }
  return;
}

void FUN_000c2fac(void)

{
  if ((((DAT_febebf45 == '\0') && (DAT_febeacbd < 2)) && (DAT_febeacc4 == '\0')) &&
     (DAT_febeacc2 == '\0')) {
    DAT_febebfaf = 0x5a;
  }
  else {
    DAT_febebfaf = 0;
  }
  return;
}

void FUN_000c2fd8(void)

{
  if ((((DAT_febeacc7 == '\0') && (DAT_febeacc8 == '\0')) && (DAT_febeacc9 == '\0')) &&
     ((DAT_febeacca == '\0' && (DAT_febeaccb == '\0')))) {
    DAT_febebfb2 = 0x5a;
  }
  else {
    DAT_febebfb2 = 0;
  }
  return;
}

void FUN_000c3008(void)

{
  if ((DAT_febebf47 != '\0') || (DAT_febebfb3 = 0, DAT_febeacd6 != '\0')) {
    DAT_febebfb3 = 0x5a;
  }
  return;
}

void FUN_000c3022(void)

{
  if ((DAT_febeaccf == '\0') && (DAT_febebf49 == '\0')) {
    if ((DAT_febeacd1 != '\0') || (DAT_febebf4a == '\0')) {
      DAT_febebfb4 = 0;
      return;
    }
  }
  else if ((DAT_febeacd1 == '\0') && ((DAT_febebf4a == '\0' && (DAT_febeaccf != '\0')))) {
    DAT_febebfb4 = 0;
    return;
  }
  DAT_febebfb4 = 0x5a;
  return;
}

void FUN_000c305c(void)

{
  if ((DAT_febebf47 != '\0') || (DAT_febebfb5 = 0, DAT_febebf48 != '\0')) {
    DAT_febebfb5 = 0x5a;
  }
  return;
}

void FUN_000c3076(void)

{
  FUN_000c3008();
  FUN_000c3022();
  FUN_000c305c();
  return;
}

void FUN_000c308a(void)

{
  byte bVar1;
  
  if ((DAT_febead3c == '\0') || (DAT_febead3c == '\x03')) {
LAB_000c30ca:
    DAT_febebf6c = '\"';
LAB_000c30ce:
    if ((1 < DAT_febeacbd) || (DAT_febebf6c != '\x11')) {
      DAT_febebfb6 = 0;
      return;
    }
  }
  else {
    if (DAT_febead3c == '\x02') {
      if ((DAT_febebf44 == 0) && (DAT_febead25 == 0)) {
LAB_000c30ba:
        DAT_febebf6c = '\x11';
        goto LAB_000c30ce;
      }
      bVar1 = DAT_febead25;
      if ((DAT_febebf44 >> 1 & 1) == 0) goto LAB_000c30c2;
    }
    else {
      bVar1 = DAT_febebf44;
      if (DAT_febebf44 == 0) goto LAB_000c30ba;
LAB_000c30c2:
      if ((bVar1 >> 1 & 1) == 0) goto LAB_000c30ca;
    }
    DAT_febebf6c = 'D';
  }
  DAT_febebfb6 = 0x5a;
  return;
}

void f33_run_init_chain_c30ea(void)

{
  FUN_000c2ed0();
  FUN_000c2f26();
  FUN_000c2f78();
  FUN_000c2fac();
  FUN_000c2fd8();
  FUN_000c3076();
  FUN_000c308a();
  return;
}

void FUN_000c3228(void)

{
  if ((DAT_febead3c == '\0') || (DAT_febead3c == '\x03')) {
    DAT_febebfb7 = 0;
    DAT_febebfb8 = 0;
    DAT_febebf84 = 0;
  }
  else if (DAT_febead3c == '\x02') {
    if (DAT_febead3e == '\x02') {
      DAT_febebf84 = (int)(((DAT_febebf9e * 0xeaaf) / 0x10000) * (uint)DAT_febeae38) / 0x400;
      DAT_febebfb7 = 0x5a;
    }
    else {
      DAT_febebfb7 = 0;
    }
    DAT_febebfb8 = 1;
  }
  else {
    DAT_febebf84 = 0;
    DAT_febebfb7 = 0x5a;
    DAT_febebfb8 = 0;
  }
  return;
}

void f33_refresh_observer_source_term(void)

{
  DAT_febeaba4 = -DAT_febeac18;
  DAT_febebfc4 = DAT_febeac02;
  return;
}

void FUN_000c32be(void)

{
  if (DAT_febeac01 == '\0') {
    if ((DAT_febebf6e < 10) && (DAT_febebf6e = DAT_febebf6e + 1, 9 < DAT_febebf6e)) {
      DAT_febebfc5 = 0;
    }
    DAT_febebf6d = 0;
  }
  else {
    if ((DAT_febebf6d < DAT_000af56c) &&
       (DAT_febebf6d = DAT_febebf6d + 1, DAT_000af56c <= DAT_febebf6d)) {
      DAT_febebfc5 = 0x5a;
    }
    DAT_febebf6e = 0;
  }
  return;
}

void FUN_000c330c(void)

{
  f33_refresh_observer_source_term();
  FUN_000c32be();
  return;
}

int f33_estimator_reference_correction(void)

{
  int value;
  uint32_t puVar1;
  ushort input;
  uint uVar2;
  int iVar3;
  uint uVar4;
  
  puVar1 = 0xfebeb800u;
  uVar4 = (uint)DAT_febeae38;
  value = DAT_febebf7c - DAT_febebf70;
  DAT_febebfc8 = value;
  iVar3 = f33_abs_s32_wrapping(value);
  if (uVar4 == 0) {
    uVar2 = 0;
  }
  else {
    uVar2 = iVar3 << 10;
    if (uVar4 != 0) {
      uVar2 = uVar2 / uVar4;
    }
    if (0xffff < uVar2) {
      input = 0xffff;
      goto LAB_000c34d0;
    }
  }
  input = (ushort)uVar2;
LAB_000c34d0:
  iVar3 = f33_interpolate_unsigned_axis_sentinel_curve((ushort *)((undefined *)camry_host_ptr(0xaf5ceu)),input);
  iVar3 = (int)(iVar3 * uVar4) / 0x400;
  (*((int *)camry_host_ptr((uint32_t)(puVar1 + 0x7cc)))) = iVar3;
  if (-1 < value) {
    iVar3 = -iVar3;
  }
  (*((int *)camry_host_ptr((uint32_t)(puVar1 + 2000)))) = iVar3;
  return iVar3;
}

void f33_snapshot_retained_estimator_projection(void)

{
  DAT_febebff4 = DAT_febeaf04;
  DAT_febebff8 = DAT_febeae0e;
  DAT_febebffa = DAT_febeacec;
  return;
}

void f33_update_estimator_source_mode_gate(void)

{
  undefined1 uVar1;
  undefined *puVar2;
  int iVar3;
  
  puVar2 = ((undefined *)camry_host_ptr(0xfebeb800u));
  if ((DAT_febead3f == '\x02') &&
     ((DAT_febead5c != '\x02' ||
      (puVar2 = ((undefined *)camry_host_ptr(0xfebeb800u)), iVar3 = f33_abs_s32_wrapping((int)DAT_febeae40),
      (int)(iVar3 - (uint)*(ushort *)(puVar2 + 0x828)) < 0 ==
      (iVar3 < 0 && -1 < (int)(iVar3 - (uint)*(ushort *)(puVar2 + 0x828))))))) {
    uVar1 = 0;
  }
  else {
    uVar1 = 0x5a;
  }
  puVar2[0x82e] = uVar1;
  return;
}

uint f33_estimator_base_source_constraint(void)

{
  char cVar1;
  char cVar2;
  char cVar3;
  short sVar4;
  short sVar5;
  uint uVar8;
  int iVar9;
  int iVar10;
  int iVar6;
  int iVar7;
  
  cVar3 = DAT_febebfb4;
  cVar2 = DAT_febebfb3;
  cVar1 = DAT_febebf46;
  sVar5 = DAT_febeae04;
  iVar10 = (int)f33_estimator_source_amplitude_limits[0];
  iVar9 = (int)f33_estimator_source_amplitude_limits[1];
  sVar4 = f33_abs_s16_wrapping(DAT_febeae06);
  iVar6 = (int)sVar4;
  sVar5 = f33_abs_s16_wrapping(sVar5);
  iVar7 = (int)sVar5;
  if ((((cVar2 == '\0') && (cVar3 == '\0')) &&
      (iVar6 - iVar10 < 0 != (iVar6 < 0 != iVar10 < 0 && iVar10 < 0 == iVar6 - iVar10 < 0) ||
       iVar6 == iVar10)) &&
     ((iVar7 - iVar9 < 0 != (iVar7 < 0 != iVar9 < 0 && iVar9 < 0 == iVar7 - iVar9 < 0) ||
       iVar7 == iVar9 && (cVar1 == '\0')))) {
    uVar8 = 0x5a;
  }
  else {
    uVar8 = 0;
  }
  return uVar8;
}

uint f33_estimator_mode2_constraint_a(void)

{
  char cVar1;
  char cVar2;
  char cVar3;
  short sVar4;
  short sVar5;
  uint uVar8;
  int iVar9;
  int iVar10;
  int iVar6;
  int iVar7;
  
  sVar5 = DAT_febeae50;
  cVar3 = DAT_febead3c;
  cVar2 = DAT_febead35;
  cVar1 = DAT_febead34;
  iVar10 = (int)f33_estimator_source_amplitude_limits[2];
  iVar9 = (int)f33_estimator_source_amplitude_limits[3];
  sVar4 = f33_abs_s16_wrapping(DAT_febeae4c);
  iVar6 = (int)sVar4;
  sVar5 = f33_abs_s16_wrapping(sVar5);
  iVar7 = (int)sVar5;
  if ((cVar3 == '\x02') &&
     ((((iVar6 - iVar10 < 0 == (iVar6 < 0 != iVar10 < 0 && iVar10 < 0 == iVar6 - iVar10 < 0) &&
         iVar6 != iVar10 ||
        (iVar7 - iVar9 < 0 == (iVar7 < 0 != iVar9 < 0 && iVar9 < 0 == iVar7 - iVar9 < 0) &&
         iVar7 != iVar9)) || (cVar1 != '\0')) || (cVar2 != '\0')))) {
    uVar8 = 0;
  }
  else {
    uVar8 = 0x5a;
  }
  return uVar8;
}

uint f33_estimator_mode2_constraint_b(void)

{
  char cVar1;
  char cVar2;
  char cVar3;
  short sVar4;
  short sVar5;
  uint uVar8;
  int iVar9;
  int iVar10;
  int iVar6;
  int iVar7;
  
  sVar5 = DAT_febeae52;
  cVar3 = DAT_febead3f;
  cVar2 = DAT_febead35;
  cVar1 = DAT_febead34;
  iVar10 = (int)f33_estimator_source_amplitude_limits[4];
  iVar9 = (int)f33_estimator_source_amplitude_limits[5];
  sVar4 = f33_abs_s16_wrapping(DAT_febeae4e);
  iVar6 = (int)sVar4;
  sVar5 = f33_abs_s16_wrapping(sVar5);
  iVar7 = (int)sVar5;
  if ((cVar3 == '\x02') &&
     ((((iVar6 - iVar10 < 0 == (iVar6 < 0 != iVar10 < 0 && iVar10 < 0 == iVar6 - iVar10 < 0) &&
         iVar6 != iVar10 ||
        (iVar7 - iVar9 < 0 == (iVar7 < 0 != iVar9 < 0 && iVar9 < 0 == iVar7 - iVar9 < 0) &&
         iVar7 != iVar9)) || (cVar1 != '\0')) || (cVar2 != '\0')))) {
    uVar8 = 0;
  }
  else {
    uVar8 = 0x5a;
  }
  return uVar8;
}

void f33_reset_rate_observer(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  f33_clear_observer_source_term();
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x884)))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + 0x86c)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x88e))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x88f))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x890))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x891))))) = 0;
  return;
}

void f33_apply_estimator_center_reseed(void)

{
  if (DAT_febec091 == 'Z') {
    DAT_febec080 = DAT_febec0b0;
    DAT_febec078 = DAT_febec0b0 << 0xb;
    DAT_febec08d = 0x5a;
  }
  else {
    DAT_febec08d = 0;
  }
  return;
}

void f33_classify_estimator_source_band(void)

{
  DAT_febec08a = DAT_febec08e;
  if ((DAT_febead3c != '\0') && (DAT_febead3c != '\x03')) {
    DAT_febec088 = f33_estimator_lower_band_default;
    DAT_febec06a = f33_estimator_upper_band_default;
    if (DAT_febead3c == '\x02') {
      DAT_febec088 = f33_estimator_lower_band_mode2;
      DAT_febec06a = f33_estimator_upper_band_mode2;
    }
    if (DAT_febec088 <= DAT_febebfec) {
      if (DAT_febebfec < DAT_febec06a) {
        DAT_febec06e = 0x11;
        return;
      }
      DAT_febec06e = 0x22;
      return;
    }
  }
  DAT_febec06e = 0;
  return;
}

void f33_initialize_retained_estimator_qualification(void)

{
  DAT_febec094 = 0;
  DAT_febec098 = 0;
  DAT_febec09c = 0;
  DAT_febec0a0 = 0;
  DAT_febec0ac = 0;
  DAT_febec0ad = 0;
  DAT_febec0a4 = 0;
  DAT_febec0a6 = 0;
  DAT_febec0a8 = 0;
  DAT_febec0aa = 0;
  DAT_febec0b0 = 0;
  DAT_febeaba8 = 0;
  DAT_febec0ae = 0;
  DAT_febec0b6 = 0;
  DAT_febec0b7 = 0;
  DAT_febec0b4 = 0;
  return;
}

void f33_clear_retained_estimator_and_request_reset(void)

{
  DAT_febec0b4 = 0;
  DAT_febec0b7 = 0;
  DAT_febec08e = 0;
  DAT_febec08f = 0;
  DAT_febec0b6 = 0;
  DAT_febeaba8 = 0;
  DAT_febec0b0 = 0;
  DAT_febec0ac = 0;
  DAT_febec0ad = 0;
  DAT_febebfb9 = 0;
  DAT_febebfbb = 0;
  DAT_febebfbd = 0;
  DAT_febebfbe = 0;
  DAT_febebfaa = 0;
  DAT_febebfac = 0;
  DAT_febec090 = 0x5a;
  return;
}

void f33_count_retained_estimator_failure(void)

{
  ushort uVar1;
  uint32_t puVar2;
  ushort uVar3;
  
  uVar1 = DAT_000af7ec;
  puVar2 = 0xfebeb800u;
  DAT_febec0a4 = 0;
  DAT_febec0a6 = 0;
  DAT_febec0aa = 0;
  uVar3 = DAT_febec0a8 + 1U;
  if (DAT_000af7ec <= (ushort)(DAT_febec0a8 + 1U)) {
    puVar2 = 0xfebeb800u;
    f33_clear_retained_estimator_and_request_reset();
    uVar3 = uVar1;
  }
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0x8a8)))) = uVar3;
  return;
}

void f33_fill_constant_block_c4a06(void)

{
  DAT_febec0cc = 0;
  DAT_febec0d0 = 0;
  DAT_febec0b8 = 0;
  DAT_febec0c0 = DAT_000af7f8;
  DAT_febec0bc = 0;
  DAT_febec0c8 = 0;
  DAT_febec0ca = 0;
  DAT_febec0c4 = DAT_000af7f8;
  return;
}

void FUN_000c4a32(void)

{
  undefined4 *puVar1;
  
  if (DAT_febec08e == '\"') {
    puVar1 = ((undefined *)camry_host_ptr(0xaf7f0u));
  }
  else {
    if (DAT_febec08e != '\x11') {
      puVar1 = ((undefined *)camry_host_ptr(0xaf7f8u));
      goto LAB_000c4a5e;
    }
    puVar1 = ((undefined *)camry_host_ptr(0xaf7f4u));
  }
  DAT_febec0ca = 1;
LAB_000c4a5e:
  DAT_febec0c0 = *puVar1;
  DAT_febec0c4 = *puVar1;
  return;
}

void FUN_000c4a70(void)

{
  DAT_febec0bc = DAT_000af7f0;
  if ((DAT_febec08e != '\"') && (DAT_febec0bc = DAT_000af7f8, DAT_febec08e == '\x11')) {
    DAT_febec0bc = DAT_000af7f4;
  }
  return;
}

void FUN_000c4b4e(void)

{
  if (DAT_febec0b8 < 0) {
    if (DAT_febec084 + DAT_febec0c4 < 0 !=
        (DAT_febec084 < 0 != -DAT_febec0c4 < 0 &&
        -DAT_febec0c4 < 0 == DAT_febec084 + DAT_febec0c4 < 0)) {
      DAT_febec0b8 = DAT_febec084;
      return;
    }
    if (DAT_febec084 + DAT_febec0bc < 0 !=
        (DAT_febec084 < 0 != -DAT_febec0bc < 0 &&
        -DAT_febec0bc < 0 == DAT_febec084 + DAT_febec0bc < 0)) {
      DAT_febec0b8 = DAT_febec084;
      return;
    }
  }
  else if (DAT_febec0b8 != 0) {
    if (DAT_febec084 - DAT_febec0c4 < 0 ==
        (DAT_febec084 < 0 != DAT_febec0c4 < 0 && DAT_febec0c4 < 0 == DAT_febec084 - DAT_febec0c4 < 0
        ) && DAT_febec084 != DAT_febec0c4) {
      DAT_febec0b8 = DAT_febec084;
      return;
    }
    if (DAT_febec084 - DAT_febec0bc < 0 ==
        (DAT_febec084 < 0 != DAT_febec0bc < 0 && DAT_febec0bc < 0 == DAT_febec084 - DAT_febec0bc < 0
        ) && DAT_febec084 != DAT_febec0bc) {
      DAT_febec0b8 = DAT_febec084;
      return;
    }
  }
  DAT_febec0c4 = DAT_febec0c0;
  DAT_febec0b8 = DAT_febec084;
  return;
}

void f33_initialize_secondary_estimator_stability(void)

{
  DAT_febec0de = 0;
  DAT_febec0dd = 0;
  DAT_febec0d4 = 0;
  DAT_febec0dc = DAT_febead5b;
  DAT_febec0d8 = 0;
  return;
}

void f33_initialize_assist_torque_conditioner(void)

{
  DAT_febec114 = 0;
  DAT_febec0f0 = 0;
  DAT_febec110 = 0;
  DAT_febec0fc = DAT_000afb34;
  DAT_febec124 = 0;
  DAT_febec0f8 = 0;
  DAT_febec0f4 = 0;
  DAT_febec112 = 0;
  DAT_febec0e4 = DAT_000af80c;
  DAT_febec128 = 0;
  DAT_febec116 = 0;
  DAT_febec118 = 0;
  DAT_febec11a = 0;
  DAT_febec108 = 0;
  DAT_febec11c = 0;
  DAT_febec100 = 0;
  DAT_febec104 = 0;
  DAT_febec10c = 0;
  DAT_febec0e0 = 0;
  DAT_febec0e8 = 0;
  DAT_febec10e = 0;
  DAT_febec0ec = DAT_000afb34;
  DAT_febec12a = 0;
  DAT_febec11e = 0;
  DAT_febec120 = 0;
  return;
}

void f33_initialize_torque_memory_gain(void)

{
  DAT_febec136 = 0;
  DAT_febec12c = 0x400;
  DAT_febec12e = 0x400;
  DAT_febec130 = 0x400;
  DAT_febec132 = 0x400;
  DAT_febec134 = 0x400;
  return;
}

void f33_update_torque_memory_gain(void)

{
  int iVar1;
  uint32_t puVar2;
  uint uVar3;
  F33GainSlewState local_10;
  
  puVar2 = 0xfebeb800u;
  uVar3 = 7;
  if (DAT_febecab7 == '\x01') {
    uVar3 = (uint)DAT_febecb00;
  }
  local_10.current = DAT_febec134;
  if (uVar3 < 7) {
    local_10.direction = '\x02';
    iVar1 = (short)(DAT_febeac3c & 1) * 7 + uVar3;
    local_10.up_target = f33_torque_memory_gain_calibrations[iVar1].up_target;
    local_10.down_step = *((uint16_t *)camry_host_ptr((uint32_t)(f33_torque_memory_gain_calibrations[iVar1].down_step)));
    local_10.up_step = *((uint16_t *)camry_host_ptr((uint32_t)(f33_torque_memory_gain_calibrations[iVar1].up_step)));
    local_10.down_target = *((uint16_t *)camry_host_ptr((uint32_t)(f33_torque_memory_gain_calibrations[iVar1].down_target)));
  }
  else {
    local_10.direction = '\x01';
    local_10.up_target = DAT_febec12c;
    local_10.down_step = DAT_febec130;
    local_10.up_step = DAT_febec132;
    local_10.down_target = DAT_febec12e;
  }
  f33_step_retained_unsigned_gain(&local_10);
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0x930)))) = local_10.down_step;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0x932)))) = local_10.up_step;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0x92e)))) = local_10.down_target;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0x92c)))) = local_10.up_target;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0x934)))) = local_10.current;
  return;
}

short f33_scale_torque_memory_correction(short value)

{
  DAT_febec136 = (short)((int)((uint)DAT_febec134 * (int)value) / 0x400);
  return DAT_febec136;
}

void f33_initialize_torque_memory_correction(void)

{
  DAT_febec14e = 0;
  DAT_febec138 = 0;
  DAT_febec13c = 0;
  DAT_febec140 = 0;
  DAT_febec144 = 0;
  DAT_febec146 = 0;
  DAT_febec150 = 0;
  DAT_febec148 = 0;
  DAT_febec14a = 0;
  DAT_febec14c = 0;
  return;
}

void f33_publish_bounded_assist_torque_input(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = (int)DAT_000af818;
  DAT_febec14c = DAT_febeac44 + DAT_febec146;
  iVar2 = (int)DAT_febec14c;
  DAT_febec150 = DAT_000af818;
  if ((iVar2 - iVar3 < 0 != (iVar2 < 0 != iVar3 < 0 && iVar3 < 0 == iVar2 - iVar3 < 0) ||
       iVar2 == iVar3) &&
     (iVar1 = -iVar3, DAT_febec150 = DAT_febec14c,
     iVar2 + iVar3 < 0 != (iVar2 < 0 != iVar1 < 0 && iVar1 < 0 == iVar2 + iVar3 < 0) ||
     iVar2 == iVar1)) {
    DAT_febec150 = (short)iVar1;
  }
  return;
}

void f33_initialize_assist_surface_selection(void)

{
  DAT_febec154 = 0;
  DAT_febec152 = 0;
  DAT_febec158 = 0;
  DAT_febec156 = 0;
  return;
}

void f33_publish_assist_surface_selector(void)

{
  undefined2 uVar1;
  
  DAT_febec156 = 0;
  uVar1 = 1;
  if (((DAT_febec158 == 'w') || (uVar1 = 2, DAT_febec158 == 'D')) ||
     (uVar1 = 3, ((int8_t)DAT_febec158) == -0x78)) {
    DAT_febec156 = uVar1;
  }
  return;
}

void FUN_000c557a(void)

{
  DAT_febec168 = 0;
  DAT_febec16a = 0;
  DAT_febec16c = 0;
  DAT_febec15c = 0;
  DAT_febec160 = 0;
  DAT_febec164 = 0;
  DAT_febec172 = 0;
  DAT_febec170 = 0;
  DAT_febec16e = (short)((uint)DAT_febeae3a * 0xdbba + 0x8000 >> 0x10);
  return;
}

void FUN_000c55b4(void)

{
  int iVar1;
  
  if (DAT_febec170 == '\0') {
    DAT_febec170 = '\x01';
    iVar1 = 0;
  }
  else {
    iVar1 = DAT_febeac88 - DAT_febec164;
    if (iVar1 + -0x7fff < 0 == (iVar1 < 0 && -1 < iVar1 + -0x7fff) && iVar1 != 0x7fff) {
      iVar1 = 0x7fff;
    }
    else if (iVar1 + 0x7fff < 0 != (-1 < iVar1 && iVar1 + 0x7fff < 0)) {
      iVar1 = -0x7fff;
    }
  }
  DAT_febec168 = (short)iVar1;
  DAT_febec164 = DAT_febeac88;
  return;
}

void FUN_000c566c(void)

{
  DAT_febec16e = (short)((uint)DAT_febeae3a * 0xdbba + 0x8000 >> 0x10);
  return;
}

void FUN_000c5686(void)

{
  DAT_febec180 = 0;
  DAT_febec182 = 0;
  DAT_febec184 = 0;
  DAT_febec174 = 0;
  DAT_febec178 = 0;
  DAT_febec17c = 0;
  DAT_febec18a = 0;
  DAT_febec186 = (ushort)((uint)DAT_febeae3a * 90000 + 0x20000 >> 0x12);
  DAT_febec188 = 0;
  return;
}

void FUN_000c56c0(void)

{
  int iVar1;
  
  if (DAT_febec188 == '\0') {
    DAT_febec188 = '\x01';
    iVar1 = 0;
  }
  else {
    iVar1 = DAT_febeac14 - DAT_febec17c;
    if (iVar1 + -0x7fff < 0 == (iVar1 < 0 && -1 < iVar1 + -0x7fff) && iVar1 != 0x7fff) {
      iVar1 = 0x7fff;
    }
    else if (iVar1 + 0x7fff < 0 != (-1 < iVar1 && iVar1 + 0x7fff < 0)) {
      iVar1 = -0x7fff;
    }
  }
  DAT_febec180 = (short)iVar1;
  DAT_febec17c = DAT_febeac14;
  return;
}

void FUN_000c5778(void)

{
  DAT_febec186 = (ushort)((uint)DAT_febeae3a * 90000 + 0x20000 >> 0x12);
  return;
}

void FUN_000c5792(void)

{
  DAT_febec198 = 0;
  DAT_febec19a = 0;
  DAT_febec19c = 0;
  DAT_febec18c = 0;
  DAT_febec190 = 0;
  DAT_febec194 = 0;
  DAT_febec1a2 = 0;
  DAT_febec19e = (ushort)((uint)DAT_febeae3a * 90000 + 0x20000 >> 0x12);
  DAT_febec1a0 = 0;
  return;
}

void FUN_000c57cc(void)

{
  int iVar1;
  
  if (DAT_febec1a0 == '\0') {
    DAT_febec1a0 = '\x01';
    iVar1 = 0;
  }
  else {
    iVar1 = DAT_febeac14 - DAT_febec194;
    if (iVar1 + -0x7fff < 0 == (iVar1 < 0 && -1 < iVar1 + -0x7fff) && iVar1 != 0x7fff) {
      iVar1 = 0x7fff;
    }
    else if (iVar1 + 0x7fff < 0 != (-1 < iVar1 && iVar1 + 0x7fff < 0)) {
      iVar1 = -0x7fff;
    }
  }
  DAT_febec198 = (short)iVar1;
  DAT_febec194 = DAT_febeac14;
  return;
}

void FUN_000c5884(void)

{
  DAT_febec19e = (ushort)((uint)DAT_febeae3a * 90000 + 0x20000 >> 0x12);
  return;
}

void f33_fill_constant_block_c589e(void)

{
  DAT_febec1a4 = 0;
  DAT_febec1a6 = 0;
  DAT_febec1a8 = 0;
  DAT_febec1aa = 0;
  DAT_febec1ac = 0;
  DAT_febec1ae = 0;
  return;
}

void f33_fill_constant_block_c6138(void)

{
  DAT_febec24c = 0;
  DAT_febec24e = 0;
  DAT_febec240 = 0;
  DAT_febec254 = 0;
  DAT_febec266 = 0;
  DAT_febec258 = 0;
  DAT_febec244 = 0;
  DAT_febec248 = 0;
  DAT_febec256 = 0;
  DAT_febec25a = 0;
  DAT_febec264 = 0;
  DAT_febec250 = 0;
  DAT_febec252 = 0;
  DAT_febec25c = 0;
  DAT_febec25e = 0;
  DAT_febec265 = 0;
  DAT_febec260 = 0;
  DAT_febec262 = 0;
  return;
}

void f33_fill_constant_block_c635a(void)

{
  DAT_febec280 = 0;
  DAT_febec268 = 0;
  DAT_febec282 = 0;
  DAT_febec26c = 0;
  DAT_febec284 = 0;
  DAT_febec270 = 0;
  DAT_febec286 = 0;
  DAT_febec288 = 0;
  DAT_febec28a = 0;
  DAT_febec274 = 0;
  DAT_febec28c = 0;
  DAT_febec278 = 0;
  DAT_febec28e = 0;
  DAT_febec27c = 0;
  DAT_febec290 = 0;
  DAT_febec292 = 0;
  DAT_febec294 = 0;
  DAT_febec296 = 0;
  DAT_febec298 = 0;
  DAT_febec29a = 0;
  return;
}

void f33_fill_constant_block_c65f0(void)

{
  DAT_febec2a6 = 0;
  DAT_febec29c = 0x400;
  DAT_febec29e = 0x400;
  DAT_febec2a0 = 0x400;
  DAT_febec2a2 = 0x400;
  DAT_febec2a4 = 0x400;
  return;
}

void FUN_000c666c(void)

{
  int iVar1;
  uint32_t puVar2;
  uint uVar3;
  F33GainSlewState local_10;
  
  puVar2 = 0xfebeb800u;
  uVar3 = 7;
  if (DAT_febecab7 == '\x01') {
    uVar3 = (uint)DAT_febecb00;
  }
  local_10.current = DAT_febec2a4;
  if (uVar3 < 7) {
    local_10.direction = '\x02';
    iVar1 = (short)(DAT_febeac3c & 1) * 7 + uVar3;
    local_10.up_target = *(ushort *)(((undefined *)camry_host_ptr(0xd3130u)) + iVar1 * 0x10);
    local_10.down_step = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd312cu + (uint32_t)(iVar1 * 4) * 4u)))))));
    local_10.up_step = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3134u + (uint32_t)(iVar1 * 4) * 4u)))))));
    local_10.down_target = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3128u + (uint32_t)(iVar1 * 4) * 4u)))))));
  }
  else {
    local_10.direction = '\x01';
    local_10.up_target = DAT_febec29c;
    local_10.down_step = DAT_febec2a0;
    local_10.up_step = DAT_febec2a2;
    local_10.down_target = DAT_febec29e;
  }
  f33_step_retained_unsigned_gain(&local_10);
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xaa0)))) = local_10.down_step;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xaa2)))) = local_10.up_step;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xa9e)))) = local_10.down_target;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xa9c)))) = local_10.up_target;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xaa4)))) = local_10.current;
  return;
}

uint FUN_000c66b4(short param_1)

{
  DAT_febec2a6 = (short)((int)((uint)DAT_febec2a4 * (int)param_1) / 0x400);
  return DAT_febec2a6;
}

void FUN_000c6be0(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  DAT_febec2e4 = 0;
  DAT_febec2ee = 0x400;
  DAT_febec2ec = 0x400;
  DAT_febec2f0 = 0x400;
  DAT_febec2f2 = 0x400;
  DAT_febec2f4 = 0x400;
  iVar3 = 0;
  do {
    *(undefined2 *)(((undefined *)camry_host_ptr(0xfebec300u)) + iVar3 * 2) = 0x400;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebec2f8u + (uint32_t)(iVar3) * 1u)))) = 0;
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -6;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  DAT_febec2f6 = 0x400;
  DAT_febec2e8 = 0;
  return;
}

void FUN_000c6c82(void)

{
  int iVar1;
  uint32_t puVar2;
  uint uVar3;
  F33GainSlewState local_10;
  
  puVar2 = 0xfebeb800u;
  uVar3 = 7;
  if (DAT_febecab7 == '\x01') {
    uVar3 = (uint)DAT_febecb00;
  }
  local_10.current = DAT_febec2f4;
  if (uVar3 < 7) {
    local_10.direction = '\x02';
    iVar1 = (short)(DAT_febeac3c & 1) * 7 + uVar3;
    local_10.up_target = *(ushort *)(((undefined *)camry_host_ptr(0xd3210u)) + iVar1 * 0x10);
    local_10.down_step = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd320cu + (uint32_t)(iVar1 * 4) * 4u)))))));
    local_10.up_step = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3214u + (uint32_t)(iVar1 * 4) * 4u)))))));
    local_10.down_target = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3208u + (uint32_t)(iVar1 * 4) * 4u)))))));
  }
  else {
    local_10.direction = '\x01';
    local_10.up_target = DAT_febec2ec;
    local_10.down_step = DAT_febec2f0;
    local_10.up_step = DAT_febec2f2;
    local_10.down_target = DAT_febec2ee;
  }
  f33_step_retained_unsigned_gain(&local_10);
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xaf0)))) = local_10.down_step;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xaf2)))) = local_10.up_step;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xaee)))) = local_10.down_target;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xaec)))) = local_10.up_target;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xaf4)))) = local_10.current;
  return;
}

int f33_apply_internal_assist_attenuation(int value)

{
  DAT_febec2e4 = (int)((uint)DAT_febec2f4 * value) / 0x400;
  DAT_febec2e8 = (int)((uint)DAT_febec2f6 * DAT_febec2e4) / 0x400;
  return DAT_febec2e8;
}

void FUN_000c709e(void)

{
  if (DAT_febec399 == '\0') {
    DAT_febec399 = '\x01';
    DAT_febec314 = 0;
  }
  else {
    DAT_febec314 = (int)DAT_febeac0e - (int)DAT_febec36e;
  }
  DAT_febec36e = DAT_febeac0e;
  DAT_febec318 = (DAT_febec314 * 500) / 0x10;
  return;
}

void f33_fill_constant_block_c73c4(void)

{
  DAT_febec3ba = 0;
  DAT_febec3b0 = 0;
  DAT_febec3a4 = 0;
  DAT_febec3b2 = 0;
  DAT_febec3b4 = 0;
  DAT_febec3b6 = 0;
  DAT_febeabb0 = 0;
  DAT_febec3a8 = 0;
  DAT_febec3ac = 0;
  DAT_febec3b8 = 0;
  return;
}

int f33_map_first_model_derivative_compensation(void)

{
  short input;
  short sVar1;
  uint32_t puVar2;
  short sVar3;
  int iVar4;
  
  sVar1 = DAT_febec23c;
  puVar2 = 0xfebeb800u;
  sVar3 = f33_abs_s16_wrapping(DAT_febec23c);
  input = (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0x740))));
  iVar4 = f33_interpolate_signed_sentinel_curve((short *)((undefined *)camry_host_ptr(0xb11d2u)),sVar3);
  sVar3 = (short)iVar4;
  if (sVar1 < 0) {
    sVar3 = -sVar3;
  }
  iVar4 = f33_interpolate_signed_sentinel_curve
                    (((short *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb1454u + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0xbc4))))) & 1) * 4u)))) + 0xc))),input);
  (*((int *)camry_host_ptr((uint32_t)(puVar2 + 0xba4)))) =
       ((((int)(short)iVar4 * (int)sVar3) / 0x400) * (int)(*((short *)camry_host_ptr((uint32_t)(puVar2 + 0xbb0))))) / 0x400;
  return iVar4;
}

int f33_map_second_model_derivative_compensation(void)

{
  short input;
  short sVar1;
  uint32_t puVar2;
  short sVar3;
  int iVar4;
  
  sVar1 = DAT_febec23e;
  puVar2 = 0xfebeb800u;
  sVar3 = f33_abs_s16_wrapping(DAT_febec23e);
  input = (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0x740))));
  iVar4 = f33_interpolate_signed_sentinel_curve((short *)((undefined *)camry_host_ptr(0xb11e6u)),sVar3);
  sVar3 = (short)iVar4;
  if (sVar1 < 0) {
    sVar3 = -sVar3;
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0xbb4)))) = sVar3;
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + 3000)))) = sVar1;
  iVar4 = f33_interpolate_signed_sentinel_curve((short *)((undefined *)camry_host_ptr(0xb11aeu)),input);
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0xbb6)))) = (short)iVar4;
  (*((int *)camry_host_ptr((uint32_t)(puVar2 + -0xc50)))) =
       ((int)(short)iVar4 * (int)(short)(((int)sVar3 * (int)(*((short *)camry_host_ptr((uint32_t)(puVar2 + 0xbb2))))) / 0x400)) /
       0x400;
  return iVar4;
}

void FUN_000c7540(void)

{
  DAT_febec3e2 = 0;
  DAT_febec3e8 = 0;
  DAT_febec3e7 = 0;
  DAT_febec3de = 0;
  DAT_febec3e6 = 0;
  DAT_febec3e4 = 0;
  DAT_febec3c4 = 0;
  DAT_febec3c0 = 0;
  DAT_febec3dc = 0;
  DAT_febec3e0 = 0;
  DAT_febec3bc = 0;
  DAT_febec3cc = 0;
  DAT_febec3da = 0;
  DAT_febec3d8 = 0;
  DAT_febec3d6 = 0;
  DAT_febec3d4 = 0;
  DAT_febec3d2 = 0;
  DAT_febec3d0 = 0;
  DAT_febeabb4 = 0;
  DAT_febec3ce = 0;
  DAT_febec3ea = 0;
  DAT_febec3e9 = 0x5a;
  DAT_febec3e5 = 0x5a;
  DAT_febec3c8 = PTR_DAT_000b0140;
  return;
}

void FUN_000c75ae(void)

{
  if ((DAT_febeacd4 == '\0') && (DAT_febeacbd == '\0')) {
    if (DAT_febeacd8 == '\x01') {
      DAT_febec3de = 0;
      DAT_febec3e6 = DAT_febeacd8;
      DAT_febec3e7 = 0;
      DAT_febec3e8 = 1;
      return;
    }
    if ((DAT_febec3e6 != '\x01') && (DAT_febec3e7 != '\x01')) {
      DAT_febec3e6 = DAT_febeacd8;
      return;
    }
    if (DAT_febec3de < DAT_000b014c) {
      DAT_febec3de = DAT_febec3de + 1;
      DAT_febec3e6 = DAT_febeacd8;
      DAT_febec3e7 = 1;
      return;
    }
  }
  DAT_febec3e8 = 0;
  DAT_febec3e7 = 0;
  DAT_febec3de = 0;
  DAT_febec3e6 = DAT_febeacd8;
  return;
}

void FUN_000c772a(void)

{
  if ((DAT_febead18 == '\x11') && (DAT_febeadf6 <= DAT_000b0156)) {
    if (DAT_000b0158 <= DAT_febec3e2) {
      DAT_febec3e9 = 0x5a;
      return;
    }
    DAT_febec3e2 = DAT_febec3e2 + 1;
    return;
  }
  DAT_febec3e2 = 0;
  DAT_febec3e9 = 0;
  return;
}

void FUN_000c786c(char param_1)

{
  int iVar1;
  
  iVar1 = ((int)DAT_febec3dc * (int)DAT_febec3e0) / 0x100;
  if (iVar1 + -0x7fff < 0 == (iVar1 < 0 && -1 < iVar1 + -0x7fff) && iVar1 != 0x7fff) {
    iVar1 = 0x7fff;
  }
  else if (iVar1 + 0x7fff < 0 != (-1 < iVar1 && iVar1 + 0x7fff < 0)) {
    iVar1 = -0x7fff;
  }
  DAT_febeabb4 = (undefined2)iVar1;
  if (param_1 == '\0') {
    DAT_febec3e5 = 'Z';
  }
  else {
    if (DAT_febec3e4 == '\0') {
      DAT_febec3ce = DAT_febeabb4;
      DAT_febec3e5 = 0;
      return;
    }
    if (DAT_febec3e5 != 'Z') {
      DAT_febec3ce = DAT_febeabb4;
      return;
    }
  }
  DAT_febec3ce = DAT_febeabb4;
  DAT_febeabb4 = 0;
  return;
}

void f33_fill_constant_block_c79a0(void)

{
  DAT_febec3ec = 0x400;
  DAT_febec3ee = 0x400;
  DAT_febec3f0 = 0x400;
  DAT_febec3f2 = 0x400;
  DAT_febec3f4 = 0x400;
  return;
}

void FUN_000c7a18(void)

{
  int iVar1;
  uint32_t puVar2;
  uint uVar3;
  F33GainSlewState local_10;
  
  puVar2 = 0xfebeb800u;
  uVar3 = 7;
  if (DAT_febecab7 == '\x01') {
    uVar3 = (uint)DAT_febecb00;
  }
  local_10.current = DAT_febec3f4;
  if (uVar3 < 7) {
    local_10.direction = '\x02';
    iVar1 = (short)(DAT_febeac3c & 1) * 7 + uVar3;
    local_10.up_target = *(ushort *)(((undefined *)camry_host_ptr(0xd3398u)) + iVar1 * 0x10);
    local_10.down_step = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3394u + (uint32_t)(iVar1 * 4) * 4u)))))));
    local_10.up_step = **(ushort **)(((undefined *)camry_host_ptr(0xd339cu)) + iVar1 * 0x10);
    local_10.down_target = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3390u + (uint32_t)(iVar1 * 4) * 4u)))))));
  }
  else {
    local_10.direction = '\x01';
    local_10.up_target = DAT_febec3ec;
    local_10.down_step = DAT_febec3f0;
    local_10.up_step = DAT_febec3f2;
    local_10.down_target = DAT_febec3ee;
  }
  f33_step_retained_unsigned_gain(&local_10);
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xbf0)))) = local_10.down_step;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xbf2)))) = local_10.up_step;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xbee)))) = local_10.down_target;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xbec)))) = local_10.up_target;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xbf4)))) = local_10.current;
  return;
}

int FUN_000c7a60(short param_1)

{
  return (int)(short)((int)((uint)DAT_febec3f4 * (int)param_1) / 0x400);
}

void f33_fill_constant_block_c7a76(void)

{
  DAT_febec41c = 0;
  DAT_febec410 = 0;
  DAT_febec412 = 0;
  DAT_febec414 = 0;
  DAT_febec416 = 0;
  DAT_febec3f8 = 0;
  DAT_febec3fc = 0;
  DAT_febec400 = 0;
  DAT_febec404 = 0;
  DAT_febec408 = 0;
  DAT_febec418 = 0;
  DAT_febec41a = 0;
  DAT_febec40c = 0;
  DAT_febec41e = 0;
  return;
}

void f33_initialize_three_term_compensation(void)

{
  DAT_febec420 = 0;
  DAT_febec43c = 0;
  DAT_febec424 = 0x400;
  DAT_febec426 = 0x400;
  DAT_febec428 = 0x400;
  DAT_febec42a = 0x400;
  DAT_febec42c = 0x400;
  DAT_febec42e = 0;
  DAT_febec430 = 0x400;
  DAT_febec432 = 0x400;
  DAT_febec434 = 0x400;
  DAT_febec436 = 0x400;
  DAT_febec438 = 0x400;
  DAT_febec43a = 0;
  return;
}

void FUN_000c7d14(void)

{
  int iVar1;
  uint32_t puVar2;
  uint uVar3;
  F33GainSlewState local_10;
  
  puVar2 = 0xfebeb800u;
  uVar3 = 7;
  if (DAT_febecab7 == '\x01') {
    uVar3 = (uint)DAT_febecb00;
  }
  local_10.current = DAT_febec42c;
  if (uVar3 < 7) {
    local_10.direction = '\x02';
    iVar1 = (short)(DAT_febeac3c & 1) * 7 + uVar3;
    local_10.up_target = *(ushort *)(((undefined *)camry_host_ptr(0xd3478u)) + iVar1 * 0x10);
    local_10.down_step = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3474u + (uint32_t)(iVar1 * 4) * 4u)))))));
    local_10.up_step = **(ushort **)(((undefined *)camry_host_ptr(0xd347cu)) + iVar1 * 0x10);
    local_10.down_target = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3470u + (uint32_t)(iVar1 * 4) * 4u)))))));
  }
  else {
    local_10.direction = '\x01';
    local_10.up_target = DAT_febec424;
    local_10.down_step = DAT_febec428;
    local_10.up_step = DAT_febec42a;
    local_10.down_target = DAT_febec426;
  }
  f33_step_retained_unsigned_gain(&local_10);
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xc28)))) = local_10.down_step;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xc2a)))) = local_10.up_step;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xc26)))) = local_10.down_target;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xc24)))) = local_10.up_target;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xc2c)))) = local_10.current;
  return;
}

short f33_scale_rate_assist_term(short value)

{
  DAT_febec42e = (short)((int)((uint)DAT_febec42c * (int)value) / 0x400);
  return DAT_febec42e;
}

void FUN_000c7dd4(void)

{
  int iVar1;
  uint32_t puVar2;
  uint uVar3;
  F33GainSlewState local_10;
  
  puVar2 = 0xfebeb800u;
  uVar3 = 7;
  if (DAT_febecab7 == '\x01') {
    uVar3 = (uint)DAT_febecb00;
  }
  local_10.current = DAT_febec438;
  if (uVar3 < 7) {
    local_10.direction = '\x02';
    iVar1 = (short)(DAT_febeac3c & 1) * 7 + uVar3;
    local_10.up_target = *(ushort *)(((undefined *)camry_host_ptr(0xd3558u)) + iVar1 * 0x10);
    local_10.down_step = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3554u + (uint32_t)(iVar1 * 4) * 4u)))))));
    local_10.up_step = **(ushort **)(((undefined *)camry_host_ptr(0xd355cu)) + iVar1 * 0x10);
    local_10.down_target = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3550u + (uint32_t)(iVar1 * 4) * 4u)))))));
  }
  else {
    local_10.direction = '\x01';
    local_10.up_target = DAT_febec430;
    local_10.down_step = DAT_febec434;
    local_10.up_step = DAT_febec436;
    local_10.down_target = DAT_febec432;
  }
  f33_step_retained_unsigned_gain(&local_10);
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xc34)))) = local_10.down_step;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xc36)))) = local_10.up_step;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xc32)))) = local_10.down_target;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xc30)))) = local_10.up_target;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xc38)))) = local_10.current;
  return;
}

uint FUN_000c7e1c(short param_1)

{
  DAT_febec43a = (short)((int)((uint)DAT_febec438 * (int)param_1) / 0x400);
  return DAT_febec43a;
}

void f33_initialize_nonlinear_torque_compensation(void)

{
  DAT_febec43e = 0;
  DAT_febec440 = 0;
  DAT_febec442 = 0;
  DAT_febec444 = 0;
  DAT_febec446 = 0;
  DAT_febec44c = 0;
  DAT_febec448 = 0;
  DAT_febec44a = 0;
  DAT_febec44e = 0;
  return;
}

ushort f33_update_nonlinear_torque_slope(void)

{
  char cVar1;
  short sVar2;
  short sVar3;
  short sVar4;
  undefined2 uVar5;
  uint32_t puVar6;
  ushort uVar7;
  
  sVar3 = DAT_febec43e;
  sVar2 = DAT_febeac6e;
  cVar1 = DAT_febeac2b;
  puVar6 = 0xfebeb800u;
  uVar7 = f33_abs_s16_wrapping(DAT_febec128);
  sVar4 = 0xa99;
  if (uVar7 >> 5 < 0x7f) {
    sVar4 = *(short *)(((undefined *)camry_host_ptr(0xafda8u)) + (uint)(uVar7 >> 5) * 4);
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar6 + 0xc48)))) = sVar4;
  sVar4 = (short)(((int)sVar3 * (int)sVar4) / 0x400);
  (*((short *)camry_host_ptr((uint32_t)(puVar6 + 0xc4a)))) = sVar4;
  if (cVar1 == 'Z') {
    uVar5 = 0;
  }
  else {
    uVar5 = (undefined2)(((int)sVar2 * (int)sVar4) / 0x400);
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar6 + 0xc4e)))) = uVar5;
  return uVar7;
}

void f33_initialize_angle_rate_compensation(void)

{
  DAT_febec450 = 0;
  DAT_febec452 = 0;
  DAT_febec454 = 0;
  DAT_febec456 = 0;
  DAT_febec458 = 0;
  DAT_febec45a = 0;
  return;
}

void f33_initialize_directional_rate_compensation(void)

{
  DAT_febec460 = 0;
  DAT_febec462 = 0;
  DAT_febec470 = 0;
  DAT_febec464 = 0;
  DAT_febec466 = 0;
  DAT_febec468 = 0;
  DAT_febec46a = 0;
  DAT_febec46c = 0;
  DAT_febec46e = 0;
  DAT_febec472 = 0;
  DAT_febec45c = 0;
  return;
}

void FUN_000c81ee(void)

{
  DAT_febec474 = 0;
  DAT_febec476 = 0;
  return;
}

void FUN_000c8642(void)

{
  DAT_febec4ac = camry_host_addr(((undefined *)camry_host_ptr(0xb1248u)));
  DAT_febec4b4 = 0;
  DAT_febec4b6 = 0;
  DAT_febec4c0 = 0;
  DAT_febec4a4 = 0;
  DAT_febec4a8 = 0;
  DAT_febec4b8 = 0;
  DAT_febec4ba = 0;
  DAT_febec4bc = 0;
  DAT_febec4b0 = camry_host_addr(((undefined *)camry_host_ptr(0xb121cu)));
  return;
}

void FUN_000c873e(void)

{
  DAT_febec4e0 = 0;
  DAT_febec4c8 = 0;
  DAT_febec4ce = DAT_000b12ba;
  DAT_febec4ca = 0x400;
  DAT_febec4cc = 0x400;
  DAT_febec4d0 = DAT_000b12ba;
  DAT_febec4c4 = (uint)DAT_000b12ba;
  DAT_febec4d2 = 0;
  DAT_febec4d4 = 0x400;
  DAT_febec4d6 = 0x400;
  DAT_febec4d8 = 0x400;
  DAT_febec4da = 0x400;
  DAT_febec4dc = 0x400;
  DAT_febec4de = 0;
  return;
}

uint FUN_000c8894(short param_1)

{
  DAT_febec4d2 = (short)((int)((int)param_1 * (uint)DAT_febec4ca) / 0x400);
  return DAT_febec4d2;
}

void FUN_000c890e(void)

{
  int iVar1;
  uint32_t puVar2;
  uint uVar3;
  F33GainSlewState local_10;
  
  puVar2 = 0xfebeb800u;
  uVar3 = 7;
  if (DAT_febecab7 == '\x01') {
    uVar3 = (uint)DAT_febecb00;
  }
  local_10.current = DAT_febec4dc;
  if (uVar3 < 7) {
    local_10.direction = '\x02';
    iVar1 = (short)(DAT_febeac3c & 1) * 7 + uVar3;
    local_10.up_target = *(ushort *)(((undefined *)camry_host_ptr(0xd36f8u)) + iVar1 * 0x10);
    local_10.down_step = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd36f4u + (uint32_t)(iVar1 * 4) * 4u)))))));
    local_10.up_step = **(ushort **)(((undefined *)camry_host_ptr(0xd36fcu)) + iVar1 * 0x10);
    local_10.down_target = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd36f0u + (uint32_t)(iVar1 * 4) * 4u)))))));
  }
  else {
    local_10.direction = '\x01';
    local_10.up_target = DAT_febec4d4;
    local_10.down_step = DAT_febec4d8;
    local_10.up_step = DAT_febec4da;
    local_10.down_target = DAT_febec4d6;
  }
  f33_step_retained_unsigned_gain(&local_10);
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xcd8)))) = local_10.down_step;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xcda)))) = local_10.up_step;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xcd6)))) = local_10.down_target;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xcd4)))) = local_10.up_target;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xcdc)))) = local_10.current;
  return;
}

uint FUN_000c8956(short param_1)

{
  DAT_febec4de = (short)((int)((uint)DAT_febec4dc * (int)param_1) / 0x400);
  return DAT_febec4de;
}

void f33_fill_constant_block_c8970(void)

{
  DAT_febec4e4 = 0;
  DAT_febec520 = 0;
  DAT_febec508 = 0;
  DAT_febeabce = 0;
  DAT_febec50a = 0;
  DAT_febec50c = 0;
  DAT_febec4e8 = 0;
  DAT_febec4ec = 0;
  DAT_febec50e = 0;
  DAT_febec510 = 0;
  DAT_febec512 = 0;
  DAT_febec514 = 0;
  DAT_febec524 = 0;
  DAT_febec4f0 = 0;
  DAT_febeabc8 = 0;
  DAT_febec4f4 = 0;
  DAT_febec4f8 = 0;
  DAT_febec521 = 0;
  DAT_febec522 = 0x5a;
  DAT_febec516 = 0;
  DAT_febec4fc = 0;
  DAT_febec518 = 0;
  DAT_febec500 = 0;
  DAT_febec51a = 0;
  DAT_febec51c = 0;
  DAT_febec51e = 0;
  DAT_febeabcc = 0;
  DAT_febec504 = 0;
  return;
}

void f33_fill_constant_block_c8df6(void)

{
  DAT_febec536 = 0;
  DAT_febec537 = 0;
  DAT_febec538 = 0;
  DAT_febec528 = 0;
  DAT_febec530 = 0;
  DAT_febec532 = 0;
  DAT_febec53a = 0;
  DAT_febec534 = 0;
  DAT_febec52c = 0;
  return;
}

void FUN_000c8f90(void)

{
  bool bVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = (int)DAT_febec534;
  iVar2 = (int)DAT_000b1274;
  DAT_febec53a = DAT_000b1274;
  if ((iVar3 - iVar2 < 0 != (iVar3 < 0 != iVar2 < 0 && iVar2 < 0 == iVar3 - iVar2 < 0) ||
       iVar3 == iVar2) &&
     (iVar2 = iVar3 + DAT_000b1274, bVar1 = -(int)DAT_000b1274 < 0, DAT_febec53a = DAT_febec534,
     iVar2 < 0 != (iVar3 < 0 != bVar1 && bVar1 == iVar2 < 0))) {
    DAT_febec53a = -DAT_000b1274;
  }
  return;
}

void FUN_000c8fb6(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  DAT_febec546 = 0;
  DAT_febec53c = 0x400;
  DAT_febec53e = 0x400;
  DAT_febec540 = 0x400;
  DAT_febec542 = 0x400;
  DAT_febec544 = 0x400;
  iVar3 = 0;
  do {
    *(undefined2 *)(((undefined *)camry_host_ptr(0xfebec554u)) + iVar3 * 2) = 0x400;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebec54cu + (uint32_t)(iVar3) * 1u)))) = 0;
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -6;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  DAT_febec548 = 0x400;
  DAT_febec54a = 0;
  return;
}

void FUN_000c9058(void)

{
  int iVar1;
  uint32_t puVar2;
  uint uVar3;
  F33GainSlewState local_10;
  
  puVar2 = 0xfebeb800u;
  uVar3 = 7;
  if (DAT_febecab7 == '\x01') {
    uVar3 = (uint)DAT_febecb00;
  }
  local_10.current = DAT_febec544;
  if (uVar3 < 7) {
    local_10.direction = '\x02';
    iVar1 = (short)(DAT_febeac3c & 1) * 7 + uVar3;
    local_10.up_target = *(ushort *)(((undefined *)camry_host_ptr(0xd3858u)) + iVar1 * 0x10);
    local_10.down_step = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3854u + (uint32_t)(iVar1 * 4) * 4u)))))));
    local_10.up_step = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd385cu + (uint32_t)(iVar1 * 4) * 4u)))))));
    local_10.down_target = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3850u + (uint32_t)(iVar1 * 4) * 4u)))))));
  }
  else {
    local_10.direction = '\x01';
    local_10.up_target = DAT_febec53c;
    local_10.down_step = DAT_febec540;
    local_10.up_step = DAT_febec542;
    local_10.down_target = DAT_febec53e;
  }
  f33_step_retained_unsigned_gain(&local_10);
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xd40)))) = local_10.down_step;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xd42)))) = local_10.up_step;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xd3e)))) = local_10.down_target;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xd3c)))) = local_10.up_target;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xd44)))) = local_10.current;
  return;
}

void FUN_000c945e(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar2 = (int)DAT_000b12ea;
  iVar1 = ((int)DAT_febeabe4 * (int)DAT_febeabde) / 0x800;
  iVar3 = iVar2;
  if ((iVar1 - iVar2 < 0 != (iVar1 < 0 != iVar2 < 0 && iVar2 < 0 == iVar1 - iVar2 < 0) ||
       iVar1 == iVar2) &&
     (iVar3 = -iVar2,
     iVar1 + iVar2 < 0 == (iVar1 < 0 != iVar3 < 0 && iVar3 < 0 == iVar1 + iVar2 < 0) &&
     iVar1 != iVar3)) {
    iVar3 = iVar1;
  }
  DAT_febec59e = (short)iVar3;
  iVar3 = (int)DAT_000b12ec;
  iVar1 = ((int)DAT_febeabe6 * (int)DAT_febec594) / 0x100;
  DAT_febec5a0 = DAT_000b12ec;
  if (iVar1 - iVar3 < 0 != (iVar1 < 0 != iVar3 < 0 && iVar3 < 0 == iVar1 - iVar3 < 0) ||
      iVar1 == iVar3) {
    iVar2 = -iVar3;
    if (iVar1 + iVar3 < 0 == (iVar1 < 0 != iVar2 < 0 && iVar2 < 0 == iVar1 + iVar3 < 0) &&
        iVar1 != iVar2) {
      DAT_febec5a0 = (short)iVar1;
    }
    else {
      DAT_febec5a0 = (short)iVar2;
    }
  }
  return;
}

void FUN_000c9562(void)

{
  DAT_febec5ac = 1;
  return;
}

void FUN_000c956a(void)

{
  if ((DAT_febeaccc != 0) || (DAT_febec5ac = 0, DAT_febead6f != 0)) {
    if (((DAT_febeaccc >> 1 & 1) == 0) && ((DAT_febead6f & 2) == 0)) {
      DAT_febec5ac = 1;
    }
    else {
      DAT_febec5ac = 2;
    }
  }
  return;
}

void f33_fill_constant_block_c962e(void)

{
  DAT_febec5f0 = 0;
  DAT_febec5d4 = 0;
  DAT_febec5ea = 0;
  DAT_febec5de = 0;
  DAT_febec5da = 0;
  DAT_febec5dc = 0;
  DAT_febec5e0 = 0;
  DAT_febec5e2 = 0;
  return;
}

void f33_fill_constant_block_c9c7c(void)

{
  DAT_febec5fc = 0;
  DAT_febec600 = 0;
  DAT_febec5f6 = 0;
  DAT_febec5f7 = 0;
  DAT_febec601 = 0;
  DAT_febec602 = 0;
  DAT_febec5fe = 0;
  DAT_febec603 = 0;
  DAT_febec5fa = 0;
  DAT_febec5f8 = 0;
  DAT_febec5f9 = 0;
  return;
}

void f33_fill_constant_block_c9df2(void)

{
  DAT_febec608 = 1;
  DAT_febec609 = 1;
  DAT_febec60a = 1;
  DAT_febec604 = 0;
  DAT_febec606 = 0;
  return;
}

void FUN_000c9e0a(void)

{
  DAT_febec60c = 0;
  DAT_febec60e = 0;
  DAT_febec60f = 0;
  return;
}

void FUN_000c9e18(void)

{
  DAT_febec60e = DAT_febeacf0;
  DAT_febec60f = DAT_febeacef;
  DAT_febec60c = DAT_febeae10;
  if ((((int8_t)DAT_febeacf0) == -0x5b) && (((int8_t)DAT_febeacef) != -1)) {
    DAT_febec60f = DAT_febeacef + '\x01';
  }
  return;
}

void FUN_000c9f1e(void)

{
  DAT_febeae10 = DAT_febec60c;
  DAT_febeacf0 = DAT_febec60e;
  DAT_febeacef = DAT_febec60f;
  return;
}

void FUN_000c9f38(void)

{
  int iVar1;
  undefined4 uVar2;
  uint uVar3;
  
  uVar2 = DAT_febeaee8;
  DAT_febec61c = 0;
  DAT_febec618 = 0;
  DAT_febec614 = 0;
  DAT_febec610 = 0;
  DAT_febec686 = 0;
  DAT_febec685 = 0;
  DAT_febec628 = 0;
  DAT_febec684 = 0;
  DAT_febec626 = 0;
  DAT_febec683 = 0;
  DAT_febec624 = 0;
  DAT_febec682 = 0;
  DAT_febec622 = 0;
  DAT_febec681 = 0;
  DAT_febec680 = 0;
  DAT_febec620 = 0;
  uVar3 = 0;
  do {
    iVar1 = uVar3 * 4;
    uVar3 = uVar3 + 1;
    *(undefined4 *)(((undefined *)camry_host_ptr(0xfebec630u)) + iVar1) = uVar2;
  } while (uVar3 < 0x14);
  DAT_febec62a = 0;
  DAT_febec62b = 0;
  DAT_febec62c = 0;
  DAT_febec62d = 0;
  return;
}

void FUN_000ca550(void)

{
  DAT_febec6ae = 1;
  return;
}

void FUN_000cb1e8(void)

{
  int iVar1;
  undefined4 uVar2;
  uint uVar3;
  
  uVar2 = DAT_febeaee8;
  DAT_febec79b = 0;
  DAT_febec79a = 0;
  DAT_febec734 = 0;
  DAT_febec730 = 0;
  DAT_febec72c = 0;
  DAT_febec728 = 0;
  DAT_febec799 = 0;
  DAT_febec740 = 0;
  DAT_febec798 = 0;
  DAT_febec73e = 0;
  DAT_febec797 = 0;
  DAT_febec73c = 0;
  DAT_febec796 = 0;
  DAT_febec73a = 0;
  DAT_febec795 = 0;
  DAT_febec794 = 0;
  DAT_febec738 = 0;
  uVar3 = 0;
  do {
    iVar1 = uVar3 * 4;
    uVar3 = uVar3 + 1;
    *(undefined4 *)(((undefined *)camry_host_ptr(0xfebec744u)) + iVar1) = uVar2;
  } while (uVar3 < 0x14);
  return;
}

void FUN_000cb246(void)

{
  ushort uVar1;
  ushort uVar2;
  
  if (DAT_febec794 == '\0') {
    if ((DAT_febec7bf != '\x01') || ((DAT_febec81c != '\x01' && (DAT_febec81d != '\x01')))) {
      DAT_febec738 = 0;
      return;
    }
    if ((DAT_febec738 < DAT_000b04b0) &&
       (uVar1 = DAT_febec738 + 1, uVar2 = DAT_febec738 + 1, DAT_febec738 = uVar1,
       DAT_000b04b0 <= uVar2)) {
      DAT_febec794 = DAT_febec7bf;
      return;
    }
  }
  else if (DAT_febec7bf == '\0') {
    DAT_febec738 = 0;
    DAT_febec794 = '\0';
  }
  return;
}

short FUN_000cb396(void)

{
  int iVar1;
  ushort uVar2;
  ushort uVar3;
  short sVar4;
  uint32_t puVar5;
  short sVar6;
  uint uVar7;
  
  sVar4 = DAT_000b04d4;
  puVar5 = 0xfebeb800u;
  sVar6 = f33_abs_s16_wrapping(DAT_febecc6c);
  uVar3 = DAT_000b04b6;
  uVar7 = (uint)sVar6;
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(0xfbf))))) == '\x01') || ((*((short *)camry_host_ptr((uint32_t)(puVar5 + 0xfbc)))) != sVar4)) ||
     (iVar1 = uVar7 - DAT_000b04b4,
     iVar1 < 0 != ((int)uVar7 < 0 && -1 < iVar1) || uVar7 == DAT_000b04b4)) {
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar5 + 0xf3c)))) = 0;
  }
  else {
    uVar2 = (*((ushort *)camry_host_ptr((uint32_t)(puVar5 + 0xf3c))));
    if ((uVar2 <= DAT_000b04b6) &&
       ((*((ushort *)camry_host_ptr((uint32_t)(puVar5 + 0xf3c)))) = uVar2 + 1, uVar3 < (ushort)(uVar2 + 1))) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(0xf97))))) = 1;
    }
  }
  return sVar6;
}

uint FUN_000cb3f4(void)

{
  ushort uVar1;
  ushort uVar2;
  uint32_t puVar3;
  uint uVar4;
  
  puVar3 = 0xfebeb800u;
  uVar4 = f33_abs_s32_wrapping((int)DAT_febec80a - (int)DAT_febec80c);
  uVar2 = DAT_000b04ba;
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0xf98))))) == '\0') {
    if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0xfbf))))) == '\x01') && (DAT_000b04b8 < uVar4)) {
      uVar1 = (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + 0xf3e))));
      if ((uVar1 < DAT_000b04ba) &&
         ((*((ushort *)camry_host_ptr((uint32_t)(puVar3 + 0xf3e)))) = uVar1 + 1, uVar2 <= (ushort)(uVar1 + 1))) {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0xf98))))) = 1;
      }
    }
    else {
      (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + 0xf3e)))) = 0;
    }
  }
  else if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0xfbf))))) == '\0') {
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + 0xf3e)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0xf98))))) = 0;
  }
  return uVar4;
}

uint FUN_000cb9ae(void)

{
  uint uVar1;
  
  uVar1 = (uint)DAT_febec7bc;
  if (DAT_febec7ac + uVar1 != 0xffff) {
    uVar1 = (uint)DAT_000b04d4;
  }
  return uVar1;
}

uint FUN_000cb9c8(void)

{
  uint uVar1;
  
  uVar1 = (uint)DAT_febec7a0;
  if (DAT_febec7aa + uVar1 != 0xffff) {
    uVar1 = (uint)DAT_000b04c4;
  }
  return uVar1;
}

void FUN_000cbc80(void)

{
  int iVar1;
  int iVar2;
  
  iVar2 = DAT_febec7c8;
  if ((DAT_febec7bf == '\x01') && (iVar2 = DAT_febeac88, DAT_febec7c0 != '\0')) {
    iVar2 = DAT_febec7c8;
  }
  iVar1 = DAT_febeac88 - iVar2;
  DAT_febec7c4 = 0x7d000000;
  if ((iVar1 + -0x7d000000 < 0 != (iVar1 < 0 && -1 < iVar1 + -0x7d000000) || iVar1 == 0x7d000000) &&
     (DAT_febec7c4 = iVar1,
     iVar1 + 0x7d000000 < 0 != (-1 < iVar1 && iVar1 + 0x7d000000 < 0) || iVar1 == -0x7d000000)) {
    DAT_febec7c4 = -0x7d000000;
  }
  DAT_febec7c8 = iVar2;
  return;
}

void f33_fill_constant_block_cc038(void)

{
  DAT_febec81e = 0;
  DAT_febec820 = 0;
  DAT_febec822 = 0;
  DAT_febec824 = 0;
  DAT_febec82e = 0;
  DAT_febec834 = 0;
  DAT_febec826 = 0;
  DAT_febec835 = 0;
  DAT_febec82f = 0;
  DAT_febec828 = 0;
  DAT_febec82a = 0;
  DAT_febec82c = 0;
  DAT_febec830 = 0;
  DAT_febec831 = 0;
  DAT_febec832 = 0;
  DAT_febec833 = 0;
  return;
}

int FUN_000cc114(void)

{
  uint32_t puVar1;
  short sVar2;
  
  puVar1 = 0xfebeb800u;
  sVar2 = f33_abs_s16_wrapping(DAT_febeae24);
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + 0x1026)))) = 0;
  return (int)sVar2;
}

void FUN_000cc130(void)

{
  DAT_febec835 = DAT_febec82e == '\x01' || DAT_febec834 == '\x01';
  return;
}

void f33_fill_constant_block_cc148(void)

{
  DAT_febec860 = 0;
  DAT_febec846 = 0x100;
  DAT_febec848 = 0x100;
  DAT_febec861 = 0;
  DAT_febec858 = 0;
  DAT_febec862 = 0;
  DAT_febec859 = 0;
  DAT_febec863 = 0;
  DAT_febec844 = 0;
  DAT_febec85a = 0;
  DAT_febec85b = 0;
  DAT_febec84a = 0;
  DAT_febec838 = 0;
  DAT_febec84c = 0;
  DAT_febec85e = 0;
  DAT_febec864 = 0;
  DAT_febec84e = 0;
  DAT_febec850 = 0;
  DAT_febec852 = 0x400;
  DAT_febec854 = 0;
  DAT_febec83c = 0;
  DAT_febec856 = 0;
  DAT_febec85c = 0;
  DAT_febec865 = 0;
  DAT_febec840 = 0;
  return;
}

void FUN_000cc514(void)

{
  DAT_febec865 = DAT_febeacbe == '\x01' && (DAT_febeadfc & 0x1ff) == 0;
  return;
}

void f33_fill_constant_block_cc596(void)

{
  DAT_febec884 = 0;
  DAT_febec888 = 0;
  DAT_febec870 = 0;
  DAT_febec88a = 0;
  DAT_febec894 = 0;
  return;
}

void FUN_000ccd50(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  
  iVar3 = (int)DAT_000b05b2;
  iVar4 = (int)DAT_000b05b0;
  iVar2 = (int)DAT_febec9ec;
  iVar5 = iVar4;
  if (DAT_febecab7 == '\x01') {
    iVar5 = iVar3;
  }
  if (((DAT_febecab5 == '\x11') || (DAT_febecab5 == '\"')) || (DAT_febecab5 == 'D')) {
    DAT_febec898 = (DAT_febec898 + iVar5) - (int)DAT_febec9e8;
    iVar1 = DAT_febec898;
    if (iVar2 != 0) {
      if (DAT_febec898 == -0x80000000 && iVar2 == -1) {
        iVar1 = -0x80000000;
      }
      else {
        iVar1 = DAT_febec898 / iVar2;
      }
    }
    if (((iVar5 != iVar3) ||
        (iVar2 = iVar3 - DAT_febec9f4,
        iVar1 - iVar2 < 0 != (iVar1 < 0 != iVar2 < 0 && iVar2 < 0 == iVar1 - iVar2 < 0))) &&
       ((iVar3 = iVar1, iVar5 == iVar4 &&
        (iVar2 = DAT_febec9f4 + iVar4, iVar3 = iVar4,
        iVar1 - iVar2 < 0 == (iVar1 < 0 != iVar2 < 0 && iVar2 < 0 == iVar1 - iVar2 < 0) &&
        iVar1 != iVar2)))) {
      iVar3 = iVar1;
    }
    DAT_febec9e8 = (short)iVar3;
  }
  DAT_febec9ea = (short)iVar5;
  return;
}

void FUN_000ccdc4(void)

{
  int iVar1;
  
  iVar1 = (int)(short)((DAT_febecb00 & 7) + (DAT_febeac3c & 1) * 8);
  DAT_febec9f6 = (*((undefined2 *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3cbcu + (uint32_t)(iVar1 * 0x57) * 4u)))))));
  DAT_febec9f8 = (*((undefined2 *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3cc0u + (uint32_t)(iVar1 * 0x57) * 4u)))))));
  return;
}

void FUN_000ccecc(void)

{
  int iVar1;
  
  if ((DAT_febecb00 & 7) == 7) {
    DAT_febec9fe = 0x7ffe;
    DAT_febeca00 = 0x7ffe;
  }
  else {
    iVar1 = (int)(short)((DAT_febecb00 & 7) + (DAT_febeac3c & 1) * 8);
    DAT_febec9fe = (*((undefined2 *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3cc4u + (uint32_t)(iVar1 * 0x57) * 4u)))))));
    DAT_febeca00 = (*((undefined2 *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3cc8u + (uint32_t)(iVar1 * 0x57) * 4u)))))));
  }
  return;
}

void f33_bound_selected_angle_target(void)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  
  uVar5 = (uint)DAT_febec9fe;
  uVar4 = (uint)DAT_febeca00;
  if (((DAT_febec8b4 == DAT_febec99c) || (DAT_febec8b4 == DAT_febec9c8)) ||
     (DAT_febec8b0 = DAT_febec99c, DAT_febec99c != DAT_febec9c8)) {
    DAT_febec8b0 = DAT_febec8b4;
  }
  if (((DAT_febec8b8 == DAT_febec9a0) || (DAT_febec8b8 == DAT_febec9cc)) ||
     (DAT_febec9a0 != DAT_febec9cc)) {
    DAT_febec9a0 = DAT_febec8b8;
  }
  if ((DAT_febecb00 & 7) != 7) {
    uVar2 = DAT_febec8b0 - DAT_febec9a0;
    if (((int)(uVar2 - uVar4) < 0 != ((int)uVar2 < 0 && -1 < (int)(uVar2 - uVar4)) || uVar2 == uVar4
        ) && (uVar3 = -uVar4, iVar1 = uVar2 + uVar4, uVar4 = uVar3,
             iVar1 < 0 == ((int)uVar2 < 0 != (int)uVar3 < 0 && (int)uVar3 < 0 == iVar1 < 0) &&
             uVar2 != uVar3)) {
      uVar4 = uVar2;
    }
    DAT_febec8b0 = uVar4 + DAT_febec9a0;
  }
  DAT_febec8b8 = uVar5;
  if (((int)(DAT_febec8b0 - uVar5) < 0 !=
       ((int)DAT_febec8b0 < 0 && -1 < (int)(DAT_febec8b0 - uVar5)) || DAT_febec8b0 == uVar5) &&
     (DAT_febec8b8 = -uVar5,
     (int)(DAT_febec8b0 + uVar5) < 0 ==
     ((int)DAT_febec8b0 < 0 != (int)DAT_febec8b8 < 0 &&
     (int)DAT_febec8b8 < 0 == (int)(DAT_febec8b0 + uVar5) < 0) && DAT_febec8b0 != DAT_febec8b8)) {
    DAT_febec8b8 = DAT_febec8b0;
  }
  DAT_febec9a0 = DAT_febec8b8;
  DAT_febec9cc = DAT_febec8b8;
  return;
}

undefined2 FUN_000cd5ea(void)

{
  int iVar1;
  undefined2 uVar2;
  undefined2 uVar3;
  uint32_t puVar4;
  short sVar5;
  undefined2 uVar6;
  undefined2 uVar7;
  uint uVar8;
  
  puVar4 = 0xfebeb800u;
  iVar1 = (int)(short)((DAT_febecb00 & 7) + (DAT_febeac3c & 1) * 8);
  uVar8 = f33_abs_s32_wrapping((int)DAT_febeca32);
  if ((int)(uVar8 - 0xffff) < 0 == ((int)uVar8 < 0 && -1 < (int)(uVar8 - 0xffff))) {
    uVar8 = 0xffff;
  }
  sVar5 = f33_abs_s16_wrapping((*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x740)))));
  uVar6 = FUN_000d0896(((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3d3cu + (uint32_t)(iVar1 * 0x57) * 4u))))))), uVar8 & 0xffff);
  uVar7 = FUN_000d07f2(((short *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3d40u + (uint32_t)(iVar1 * 0x57) * 4u))))))), (int)sVar5);
  uVar2 = (*((undefined2 *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3cd0u + (uint32_t)(iVar1 * 0x57) * 4u)))))));
  uVar3 = (*((undefined2 *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3cd4u + (uint32_t)(iVar1 * 0x57) * 4u)))))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar4 + 0x1204)))) = uVar6;
  (*((undefined2 *)camry_host_ptr((uint32_t)(0x1206u + (int)puVar4)))) = uVar7;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar4 + 0x1218)))) = uVar2;
  (*((undefined2 *)camry_host_ptr((uint32_t)(0x121au + (int)puVar4)))) = uVar3;
  return uVar7;
}

void FUN_000cd84e(void)

{
  DAT_febec980 = (uint)(*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3d00u + (uint32_t)((short)((DAT_febecb00 & 7) + (DAT_febeac3c & 1) * 8) * 0x57) * 4u)))))));
  return;
}

uint FUN_000ce454(undefined2 param_1)

{
  return FUN_000d0896(((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3dc8u + (uint32_t)((short)((DAT_febecb00 & 7) + (DAT_febeac3c & 1) * 8) * 0x57) * 4u))))))), 
               param_1);
}

uint FUN_000ce486(undefined2 param_1)

{
  return FUN_000d0896(((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3dccu + (uint32_t)((short)((DAT_febeca9f & 7) + (DAT_febeac3c & 1) * 8) * 0x57) * 4u))))))), 
               param_1);
}

int f33_shape_angle_controller_target(void)

{
  short value;
  uint32_t puVar1;
  short *points;
  short input;
  int iVar2;
  undefined2 uVar3;
  
  puVar1 = 0xfebeb800u;
  if (((DAT_febeca46 == DAT_febeca7c) || (DAT_febeca46 == DAT_febeca8a)) ||
     (value = DAT_febeca7c, DAT_febeca7c != DAT_febeca8a)) {
    value = DAT_febeca46;
  }
  input = f33_abs_s16_wrapping(value);
  if (value < 0) {
    points = (short *)((undefined *)camry_host_ptr(0xb05e8u));
  }
  else {
    points = (short *)((undefined *)camry_host_ptr(0xb05c4u));
  }
  iVar2 = f33_interpolate_signed_sentinel_curve(points,input);
  (*((short *)camry_host_ptr((uint32_t)(0x1228u + (int)(puVar1 + 4))))) = (short)iVar2;
  uVar3 = (undefined2)(((int)(short)iVar2 * (int)value) / 0x400);
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + 0x122e)))) = uVar3;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + 0x1280)))) = uVar3;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + 0x128e)))) = uVar3;
  return iVar2;
}

void f33_fill_constant_block_ce750(void)

{
  DAT_febecaae = 0;
  DAT_febecab2 = 0;
  DAT_febecab3 = 0;
  DAT_febecab4 = 0;
  DAT_febecab0 = 0;
  DAT_febecab5 = 0;
  DAT_febecab6 = 0;
  DAT_febecab7 = 0;
  return;
}

char FUN_000ce772(char param_1)

{
  if ((((param_1 == '\0') && (DAT_febeaccc == '\0')) && (DAT_febeaccd == '\0')) &&
     (((DAT_febeadbf < 2 && (DAT_febecafc == '\0')) && (DAT_febecad9 == '\0')))) {
    param_1 = '\x01';
  }
  return param_1;
}

char FUN_000ce7a6(char param_1)

{
  if ((param_1 == '\x01') && (DAT_febeaccd != '\0')) {
    DAT_febecaae = DAT_febecaae + 1;
  }
  else {
    DAT_febecaae = 0;
    if (param_1 != '\x01') {
      DAT_febecaae = 0;
      return param_1;
    }
  }
  if ((((DAT_febeaccc != '\0') || (DAT_000b060e < DAT_febecaae)) ||
      (DAT_febeadbf == '\x02' || DAT_febeadbf == '\x03')) ||
     ((DAT_febecafc == '\x01' || (DAT_febecad9 == '\x01')))) {
    param_1 = '\0';
    DAT_febecaae = 0;
  }
  return param_1;
}

void f33_fill_constant_block_ce964(void)

{
  DAT_febecabc = 0;
  DAT_febecac0 = 0;
  DAT_febecac4 = 0;
  DAT_febecab8 = 0;
  DAT_febecaca = 0;
  DAT_febecacc = 0;
  DAT_febecacb = 0;
  DAT_febecace = 0;
  DAT_febecad0 = 0;
  DAT_febecad8 = 0;
  DAT_febecacd = 0;
  DAT_febecacf = 0;
  DAT_febecad2 = 0;
  DAT_febecad4 = 0;
  DAT_febecad6 = 0;
  DAT_febecac8 = 0;
  DAT_febecad9 = 1;
  return;
}

void FUN_000ce9ac(void)

{
  if ((DAT_febeacc4 == '\0') && (DAT_febecafe == '\x01')) {
    DAT_febecaca = DAT_febeacbd == '\0';
  }
  else {
    DAT_febecaca = false;
  }
  return;
}

void FUN_000ce9d0(void)

{
  DAT_febecacc = DAT_febecaff == '\x01' && DAT_febeacbd == '\0';
  return;
}

void FUN_000ceb92(void)

{
  int iVar1;
  bool bVar2;
  int iVar3;
  uint32_t puVar4;
  int iVar5;
  undefined1 uVar6;
  ushort uVar7;
  
  uVar6 = DAT_febecad9;
  uVar7 = DAT_febecac8;
  iVar1 = DAT_000b0614;
  puVar4 = 0xfebeb800u;
  iVar5 = (int)DAT_febecad2;
  iVar3 = (int)DAT_febecad4;
  if (((iVar5 == iVar3) || (iVar5 == DAT_febecad6)) || (iVar3 != DAT_febecad6)) {
    iVar3 = iVar5;
  }
  iVar5 = DAT_000b0614 * 2;
  if ((DAT_febead4c == '\0') && (DAT_febecaca == '\x01')) {
    puVar4 = 0xfebeb800u;
    iVar3 = f33_abs_s32_wrapping(iVar3 - DAT_febecab8);
    iVar1 = iVar3 + iVar1 * -2;
    bVar2 = iVar5 < 0;
    if (iVar1 < 0 == (iVar3 < 0 != bVar2 && bVar2 == iVar1 < 0)) {
      if (uVar7 < DAT_000b0618) {
        uVar7 = uVar7 + 1;
      }
      else {
        uVar6 = 1;
      }
    }
    else {
      uVar6 = 0;
      uVar7 = 0;
    }
  }
  else {
    uVar6 = 1;
    uVar7 = 0;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x12d9))))) = uVar6;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + 0x12c8)))) = uVar7;
  return;
}

void f33_fill_constant_block_cec0c(void)

{
  DAT_febecafc = 0;
  DAT_febecada = 0;
  DAT_febecadc = 0;
  DAT_febecade = 0;
  DAT_febecaf4 = 0;
  DAT_febecae0 = 0;
  DAT_febecae2 = 0;
  DAT_febecae4 = 0;
  DAT_febecaf5 = 0;
  DAT_febecaf6 = 0;
  DAT_febecaf7 = 0;
  DAT_febecaf8 = 0;
  DAT_febecaf9 = 0;
  DAT_febecae6 = 0;
  DAT_febecae8 = 0;
  DAT_febecafa = 0;
  DAT_febecafb = 0;
  DAT_febecaea = 0;
  DAT_febecaec = 0;
  DAT_febecaee = 0;
  DAT_febecaf0 = 0;
  DAT_febecaf2 = 0;
  DAT_febecafd = 0;
  DAT_febecafe = 0;
  DAT_febecaff = 0;
  return;
}

void FUN_000cec72(void)

{
  DAT_febecafc = DAT_febecafb == '\x01' || DAT_febecafd == '\x01';
  return;
}

void FUN_000cec8a(void)

{
  int iVar1;
  int iVar2;
  
  iVar1 = (int)(short)DAT_febecada;
  if ((int)((uint)DAT_febeadbc - iVar1) < 0 ==
      (iVar1 < 0 && iVar1 < 0 == (int)((uint)DAT_febeadbc - iVar1) < 0)) {
    DAT_febecadc = DAT_febeadbc - DAT_febecada;
  }
  else {
    DAT_febecadc = DAT_000b0620 + (DAT_febeadbc - DAT_febecada) + 1;
  }
  DAT_febecada = (ushort)DAT_febeadbc;
  iVar1 = (int)DAT_febecadc;
  if (iVar1 + -1 < 0 == (iVar1 < 0 && -1 < iVar1 + -1) && iVar1 != 1) {
    iVar2 = (int)DAT_000b0622;
    DAT_febecade = DAT_febecadc;
    if (iVar1 - iVar2 < 0 == (iVar1 < 0 != iVar2 < 0 && iVar2 < 0 == iVar1 - iVar2 < 0)) {
      DAT_febecade = DAT_000b0622;
    }
  }
  else {
    DAT_febecade = 1;
  }
  return;
}

void FUN_000cecd6(void)

{
  if (((DAT_febecb00 & 7) == 7) || (DAT_febeacd6 != '\x01')) {
    DAT_febecaf4 = 0;
    DAT_febecaf5 = false;
    DAT_febecae0 = 0;
  }
  else {
    if (DAT_febecae0 < (*((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb146cu + (uint32_t)(DAT_febeac3c & 1) * 4u)))) + 2))))) {
      DAT_febecae0 = DAT_febecae0 + 1;
    }
    DAT_febecaf5 = (*((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb146cu + (uint32_t)(DAT_febeac3c & 1) * 4u)))) + 2)))) <= DAT_febecae0;
    DAT_febecaf4 = 1;
  }
  return;
}

short FUN_000ced28(void)

{
  undefined1 uVar1;
  ushort uVar2;
  uint32_t puVar3;
  short sVar4;
  int iVar6;
  bool bVar7;
  ushort uVar8;
  int iVar5;
  
  uVar8 = DAT_febecae2;
  puVar3 = 0xfebeb800u;
  uVar2 = (ushort)DAT_febecb00;
  sVar4 = f33_abs_s16_wrapping(DAT_febeae22);
  iVar5 = (int)sVar4;
  iVar6 = (int)(*((short *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3dd8u + (uint32_t)((short)((uVar2 & 7) + (short)(((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xbc4))))) & 1) << 3)) * 0x57) * 4u)))))));
  if (((uVar2 & 7) == 7) ||
     (iVar5 - iVar6 < 0 != (iVar5 < 0 != iVar6 < 0 && iVar6 < 0 == iVar5 - iVar6 < 0) ||
      iVar5 == iVar6)) {
    uVar1 = 0;
    bVar7 = false;
    uVar8 = 0;
  }
  else {
    uVar1 = 1;
    if (uVar8 < (*((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb146cu + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xbc4))))) & 1) * 4u)))) + 8))))) {
      uVar8 = uVar8 + 1;
    }
    bVar7 = (*((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb146cu + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xbc4))))) & 1) * 4u)))) + 8)))) <= uVar8;
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0x12e4)))) =
       (*((short *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3dd8u + (uint32_t)((short)((uVar2 & 7) + (short)(((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xbc4))))) & 1) << 3)) * 0x57) * 4u)))))));
  (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + 0x12e2)))) = uVar8;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x12f6))))) = uVar1;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x12f7))))) = bVar7;
  return sVar4;
}

short FUN_000ceda4(void)

{
  int iVar1;
  short sVar2;
  undefined1 uVar3;
  ushort uVar4;
  uint32_t puVar5;
  short sVar6;
  int iVar7;
  bool bVar8;
  ushort uVar9;
  
  uVar9 = DAT_febecae6;
  puVar5 = 0xfebeb800u;
  uVar4 = (ushort)DAT_febecb00;
  sVar6 = f33_abs_s16_wrapping(DAT_febeae24);
  sVar2 = (*((short *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3ddcu + (uint32_t)((short)((uVar4 & 7) + (short)(((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0xbc4))))) & 1) << 3)) * 0x57) * 4u)))))));
  iVar7 = (int)sVar2;
  if (((uVar4 & 7) == 7) ||
     (iVar1 = sVar6 - iVar7, iVar1 < 0 == (sVar6 < 0 != iVar7 < 0 && iVar7 < 0 == iVar1 < 0))) {
    uVar3 = 0;
    bVar8 = false;
    uVar9 = 0;
  }
  else {
    uVar3 = 1;
    if (uVar9 < (*((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb146cu + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0xbc4))))) & 1) * 4u)))) + 0xe))))) {
      uVar9 = uVar9 + 1;
    }
    bVar8 = (*((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb146cu + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0xbc4))))) & 1) * 4u)))) + 0xe)))) <= uVar9;
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + 0x12e8)))) = sVar2;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar5 + 0x12e6)))) = uVar9;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(0x12f8))))) = uVar3;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(0x12f9))))) = bVar8;
  return sVar6;
}

void FUN_000cee46(void)

{
  int iVar1;
  
  iVar1 = (int)(short)((DAT_febecb00 & 7) + (DAT_febeac3c & 1) * 8);
  DAT_febecaea = (*((undefined2 *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3de0u + (uint32_t)(iVar1 * 0x57) * 4u)))))));
  DAT_febecaec = (*((undefined2 *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3de4u + (uint32_t)(iVar1 * 0x57) * 4u)))))));
  return;
}

void FUN_000ceff4(void)

{
  DAT_febecb00 = 7;
  return;
}

void f33_select_angle_controller_mode(void)

{
  DAT_febecb00 = 7;
  if ((DAT_febeacbd == '\0') && (DAT_febecaff == '\x01')) {
    if (DAT_febeadb0 == '\x01') {
      DAT_febecb00 = 0;
    }
    else if (DAT_febeadb0 == '\x04') {
      DAT_febecb00 = 1;
    }
    else if (DAT_febeadb0 == '\n') {
      DAT_febecb00 = 3;
    }
    else if (DAT_febeadb0 == '\v') {
      DAT_febecb00 = 2;
    }
    else if (DAT_febeadb0 == '\x12') {
      DAT_febecb00 = 5;
    }
    else if (DAT_febeadb0 == '\x13') {
      DAT_febecb00 = 4;
    }
  }
  return;
}

void FUN_000cf04a(void)

{
  f33_select_angle_controller_mode();
  return;
}

void FUN_000cf056(void)

{
  f33_angle_controller_envelope_parameters[1] = 1;
  f33_angle_controller_envelope_parameters[2] = 1;
  f33_angle_controller_envelope_parameters[3] = 1;
  f33_angle_controller_envelope_parameters[5] = 1;
  f33_angle_controller_envelope_parameters[0] = 0;
  f33_angle_controller_envelope_parameters[4] = 0;
  f33_angle_controller_envelope_accumulator = 0;
  DAT_febecb08 = 0;
  DAT_febecb0c = 0;
  DAT_febecb10 = 0;
  f33_angle_controller_envelope_parameters[6] = 0;
  f33_angle_controller_envelope_parameters[7] = 0;
  DAT_febecb14 = 0;
  DAT_febecb18 = 0;
  DAT_febecb1c = 0;
  DAT_febecb38 = 0;
  DAT_febecb30 = 0;
  DAT_febecb32 = 0;
  DAT_febecb34 = 0x22;
  DAT_febecb35 = 0x22;
  DAT_febecb36 = 0;
  DAT_febecb3a = 0;
  return;
}

void FUN_000cf0b6(void)

{
  DAT_febecb35 = DAT_febecb34;
  if ((DAT_febecab5 == '\x11') || (DAT_febec862 == '\x01')) {
    DAT_febecb34 = 0x11;
  }
  else {
    DAT_febecb34 = 0x22;
    if (DAT_febecab5 == 'D') {
      DAT_febecb34 = 0x33;
    }
  }
  return;
}

void FUN_000cf0ea(void)

{
  int iVar1;
  
  iVar1 = (int)(short)((DAT_febecb00 & 7) + (DAT_febeac3c & 1) * 8);
  if ((DAT_febecb00 & 7) != 7) {
    f33_angle_controller_envelope_parameters[1] = *(ushort *)(((undefined *)camry_host_ptr(0xd3df4u)) + iVar1 * 0x15c);
    f33_angle_controller_envelope_parameters[2] = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3df8u + (uint32_t)(iVar1 * 0x57) * 4u)))))));
    f33_angle_controller_envelope_parameters[3] = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3dfcu + (uint32_t)(iVar1 * 0x57) * 4u)))))));
    f33_angle_controller_envelope_parameters[4] = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3df0u + (uint32_t)(iVar1 * 0x57) * 4u)))))));
  }
  return;
}

void f33_vote_angle_target_and_update_fade_latch(void)

{
  int iVar1;
  
  iVar1 = (int)f33_angle_controller_target_triplicate[0];
  DAT_febecb08 = (int)f33_angle_controller_target_triplicate[1];
  if (((iVar1 == DAT_febecb08) || (iVar1 == f33_angle_controller_target_triplicate[2])) ||
     (DAT_febecb08 != f33_angle_controller_target_triplicate[2])) {
    DAT_febecb08 = iVar1;
  }
  if ((DAT_febecb00 & 7) == 7) {
    if (DAT_febecb36 == '\0') {
      DAT_febecb08 = 0;
    }
    else if (f33_angle_controller_envelope_parameters[0] == 0) {
      DAT_febecb36 = '\0';
    }
  }
  else {
    DAT_febecb36 = '\x02';
  }
  return;
}

void f33_fill_constant_block_cf35c(void)

{
  DAT_febecb57 = 0;
  DAT_febecb58 = 0;
  DAT_febecb54 = 0;
  DAT_febecb55 = 0;
  DAT_febecb56 = 0;
  return;
}

void FUN_000cf370(void)

{
  uint uVar1;
  int iVar2;
  uint uVar3;
  
  uVar3 = 0;
  do {
    iVar2 = uVar3 * 2;
    uVar1 = uVar3 + 1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebecb42u + (uint32_t)(iVar2) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebecb43u + (uint32_t)(iVar2) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebecb48u + (uint32_t)(iVar2) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebecb49u + (uint32_t)(iVar2) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebecb4eu + (uint32_t)(iVar2) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebecb4fu + (uint32_t)(iVar2) * 1u)))) = 0;
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebecb3cu + (uint32_t)(uVar3) * 2u)))) = 0;
    uVar3 = uVar1;
  } while (uVar1 < 3);
  return;
}

void FUN_000cf4a8(void)

{
  if ((DAT_febecab7 == '\x01') && ((DAT_febecb00 & 7) == 2)) {
    DAT_febecb57 = 1;
  }
  else {
    DAT_febecb57 = 0;
    if (DAT_febecab7 == '\x01') {
      DAT_febecb57 = 0;
      DAT_febecb58 = (DAT_febecb00 & 7) == 0;
      return;
    }
  }
  DAT_febecb58 = 0;
  return;
}

void FUN_000cf5de(void)

{
  FUN_000cf4a8();
  FUN_000cf56a();
  return;
}

void FUN_000cfa84(void)

{
  uint uVar1;
  
  if (((DAT_febecb70 == DAT_febecb90) || (DAT_febecb70 == DAT_febecba4)) ||
     (uVar1 = DAT_febecb90, DAT_febecb90 != DAT_febecba4)) {
    uVar1 = DAT_febecb70;
  }
  if (DAT_febecbfe != DAT_febecbed) {
    DAT_febecb6c = 0;
  }
  if (DAT_febecb6c < uVar1) {
    DAT_febecb6c = DAT_febecb6c + 1;
  }
  else {
    DAT_febecb6c = 0;
  }
  return;
}

void FUN_000cfcd4(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar1 = DAT_febecc22 + DAT_febecb64;
  iVar3 = (int)(*((short *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb148cu + (uint32_t)(DAT_febeac3c & 1) * 4u)))) + 10))));
  DAT_febecbe8 = (*((short *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb148cu + (uint32_t)(DAT_febeac3c & 1) * 4u)))) + 10))));
  if ((iVar1 - iVar3 < 0 != (iVar1 < 0 != iVar3 < 0 && iVar3 < 0 == iVar1 - iVar3 < 0) ||
       iVar1 == iVar3) &&
     (iVar2 = -iVar3, DAT_febecbe8 = (short)iVar1,
     iVar1 + iVar3 < 0 != (iVar1 < 0 != iVar2 < 0 && iVar2 < 0 == iVar1 + iVar3 < 0) ||
     iVar1 == iVar2)) {
    DAT_febecbe8 = (short)iVar2;
  }
  DAT_febecbc4 = (short)iVar1;
  return;
}

void FUN_000cfd0a(void)

{
  DAT_febecbed = 0;
  DAT_febecbee = 0;
  return;
}

void f33_fill_constant_block_cfd88(void)

{
  DAT_febecbf3 = 0;
  DAT_febecbf4 = 1;
  DAT_febecbf5 = 0;
  DAT_febecbf0 = 0;
  DAT_febecbf2 = 0;
  return;
}

char FUN_000cfdd4(void)

{
  char cVar1;
  
  if (((DAT_febeadbf == '\x02' || DAT_febeadbf == '\x03') || (DAT_febeacbd != '\0')) ||
     (DAT_febecbf3 == '\0')) {
    DAT_febecbf4 = 1;
    cVar1 = DAT_febecbea;
  }
  else {
    DAT_febecbf4 = 0;
    cVar1 = DAT_febecbf2;
    if (((DAT_febecbf2 != '\x01') && (DAT_febecbf2 != '\x02')) && (DAT_febecbf2 != '\x03')) {
      cVar1 = '\0';
    }
  }
  return cVar1;
}

char FUN_000cfe14(void)

{
  char cVar1;
  
  cVar1 = DAT_febecbeb;
  if (((((DAT_febecbeb == '\0') && (DAT_febecbf4 == '\0')) &&
       (cVar1 = DAT_febecbf5 == '\0', (bool)cVar1)) || (cVar1 == '\x01')) &&
     (DAT_febecbf4 == '\x01')) {
    cVar1 = '\0';
  }
  else if (DAT_febecbf5 != '\x01') {
    return cVar1;
  }
  DAT_febecbf5 = DAT_febecbf0 < DAT_000b115c;
  if ((bool)DAT_febecbf5) {
    DAT_febecbf0 = DAT_febecbf0 + 1;
  }
  else {
    DAT_febecbf0 = 0;
  }
  return cVar1;
}

void f33_fill_constant_block_cfe8e(void)

{
  DAT_febecbfe = 0;
  DAT_febecbf6 = 0;
  DAT_febecbfa = 0;
  DAT_febecbfc = 0;
  DAT_febecbf8 = 0;
  return;
}

void FUN_000cff04(void)

{
  undefined1 uVar1;
  ushort uVar2;
  uint32_t puVar3;
  undefined1 uVar4;
  ushort uStack_a;
  
  uVar1 = DAT_febecbea;
  puVar3 = 0xfebeb800u;
  uStack_a = DAT_febecbf8;
  if (((DAT_febecbf6 == DAT_febecbfa) || (DAT_febecbf6 == DAT_febecbfc)) ||
     (uVar2 = DAT_febecbfa, DAT_febecbfa != DAT_febecbfc)) {
    uVar2 = DAT_febecbf6;
  }
  if (DAT_febecbeb == '\x01') {
    uVar4 = DAT_febecbfe;
    if (DAT_febecbf8 < uVar2) {
      uStack_a = DAT_febecbf8 + 1;
    }
    else if (DAT_febecbec == '\0') {
      puVar3 = 0xfebeb800u;
      FUN_000cfea4(DAT_febecbea,&uStack_a);
      uVar4 = uVar1;
    }
  }
  else {
    uVar4 = 0;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x13fe))))) = uVar4;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + 0x13f8)))) = uStack_a;
  return;
}

void FUN_000cff6e(void)

{
  DAT_febecc1a = 0;
  DAT_febecc1c = 0;
  return;
}

void f33_fill_constant_block_cff78(void)

{
  DAT_febecc20 = 0;
  DAT_febecc18 = 0;
  DAT_febecc00 = 0;
  DAT_febecc04 = 0;
  DAT_febecc08 = 0;
  DAT_febecc0c = 0;
  DAT_febecc10 = 0;
  DAT_febecc1e = 0;
  DAT_febecc14 = 0;
  DAT_febecc22 = 0;
  return;
}

void FUN_000d0130(void)

{
  DAT_febecc2c = 0;
  DAT_febecc24 = 0;
  DAT_febecc28 = 0;
  return;
}

void f33_fill_constant_block_d01b4(void)

{
  DAT_febecc4c = 0;
  DAT_febecc30 = 0;
  DAT_febecc34 = 0;
  DAT_febecc38 = 0;
  DAT_febecc3c = 0;
  DAT_febecc4e = 0;
  DAT_febecc60 = 0;
  DAT_febecc50 = 0;
  DAT_febecc62 = 0;
  DAT_febecc52 = 0;
  DAT_febecc54 = 0;
  DAT_febecc66 = 0;
  DAT_febecc64 = 0;
  DAT_febecc68 = 0;
  DAT_febecc6a = 0;
  DAT_febecc5c = 0;
  DAT_febecc56 = 0;
  DAT_febecc58 = 0;
  DAT_febecc5a = 0;
  DAT_febecc5e = 0;
  DAT_febecc5f = 0;
  DAT_febecc40 = 0;
  DAT_febecc44 = 0;
  DAT_febecc48 = 0;
  DAT_febecc6c = 0;
  return;
}

void f33_fill_constant_block_d04f0(void)

{
  DAT_febecc70 = 0;
  DAT_febecc74 = 0;
  DAT_febecc88 = 0;
  DAT_febecc78 = 0;
  DAT_febecc8a = 0;
  DAT_febecc7c = 0;
  DAT_febecc98 = 0;
  DAT_febecc90 = 1;
  DAT_febecc80 = 0;
  DAT_febecc8c = 0;
  DAT_febecc84 = 0;
  DAT_febecc8e = 0;
  DAT_febecc91 = 0;
  return;
}

void FUN_000d06ea(void)

{
  DAT_febecc9a = 0;
  DAT_febecc9c = 0;
  DAT_febecc9e = 1;
  return;
}

void FUN_000d06fa(void)

{
  DAT_febecc9a = 0;
  if (DAT_febeadf6 < DAT_000b1352) {
    DAT_febecc9a = 0x4000;
  }
  return;
}

short f33_abs_s16_wrapping(short value)

{
  if (0 < value) {
    return value;
  }
  return -value;
}

void f33_publish_command_snapshot(void)

{
  DAT_febeac39 = 0;
  DAT_febeac54 = DAT_febecc64;
  DAT_febeac76 = DAT_febecc66;
  DAT_febeac56 = DAT_febecc62;
  DAT_febeac58 = DAT_febec128;
  DAT_febeac68 = DAT_febecc60;
  DAT_febeac7e = DAT_febecc68;
  DAT_febeac2d = 0;
  if (DAT_febecc98 != '\0') {
    DAT_febeac2d = 0x5a;
  }
  DAT_febeac3e = 0;
  DAT_febeac70 = DAT_febec172;
  DAT_febeac3f = 0x5a;
  return;
}

void FUN_000d10e4(void)

{
  FUN_000c9e0a();
  FUN_000cf370();
  return;
}

void thunk_FUN_000d10e4(void)

{
  FUN_000d10e4();
  return;
}

void FUN_000d1160(void)

{
  f33_snapshot_retained_estimator_projection();
  return;
}

undefined8 FUN_000d2da0(uint param_1,uint param_2,uint param_3)

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

void thunk_FUN_000fcc9c(void)

{
  FUN_000fcc9c();
  return;
}

void FUN_000fc87c(void)

{
  FUN_000fd426();
  FUN_000fd444();
  return;
}

void FUN_000fcc9c(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  DAT_febef380 = f33_internal_source_admission_state;
  DAT_febef394 = DAT_febe6af0;
  DAT_febef381 = DAT_febe6878;
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -0x11;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebef382u + (uint32_t)(iVar3) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe85f4u + (uint32_t)(iVar3) * 1u))));
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  return;
}

void FUN_000fd426(void)

{
  DAT_febee744 = DAT_febeac1c;
  DAT_febee740 = DAT_febeac08;
  DAT_febee741 = DAT_febeac09;
  DAT_febee742 = DAT_febeac02;
  return;
}

void FUN_000fd444(void)

{
  DAT_febee782 = DAT_febeaf40;
  DAT_febee780 = DAT_febeaf3d;
  return;
}

void FUN_000fdc00(void)

{
  f33_initialize_cold_control_retained_state();
  return;
}

void FUN_000fdc3c(void)

{
  f33_snapshot_control_ch2_acquisition();
  return;
}

void FUN_000fdc64(void)

{
  f33_snapshot_control_foreground_acquisition();
  return;
}

undefined1 thunk_FUN_00058c84(void)

{
  return FUN_00058c84();
}

uint f33_get_mode_restart_hardware_selector(void)

{
  uint uVar1;
  
  uVar1 = f33_platform_restart_selector_constant_zero();
  return uVar1;
}

void thunk_FUN_00066ef4(void)

{
  FUN_00066ef4();
  return;
}

undefined4 thunk_FUN_00062e12(void)

{
  return FUN_00062e12();
}

undefined4 FUN_000b5a74(uint param_1)

{
  undefined4 uVar1;
  
  param_1 = param_1 & 0xff;
  uVar1 = 0;
  if ((param_1 < 0x10) && ((param_1 == 1 || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xaeba8u + (uint32_t)(param_1) * 1u)))) != DAT_000aeba8)))) {
    uVar1 = 1;
  }
  return uVar1;
}

void FUN_000076b6(undefined4 *param_1,int param_2)

{
  for (; param_2 != 0; param_2 = param_2 + -4) {
    *param_1 = 0;
    param_1 = param_1 + 1;
  }
  return;
}

void f33_dcm_selected_did_payload_length(ushort *length)

{
  f33_get_selected_did_payload_length(length);
  return;
}

void f33_get_selected_did_payload_length(ushort *length)

{
  ushort uVar1;
  uint32_t puVar2;
  F33DidPublicationMetadata *pFVar3;
  ushort uStack_a;
  
  puVar2 = 0xfebeb800u;
  pFVar3 = f33_get_did_publication_metadata(&uStack_a);
  uVar1 = 0;
  if ((uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x3648)))) < (uint)uStack_a) {
    uVar1 = pFVar3[(*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x3648))))].payload_length;
  }
  *length = uVar1;
  return;
}

void f33_return_only_stub_4d4c2(void)

{
  return;
}

void FUN_00001478(undefined4 *param_1,undefined4 *param_2,int param_3)

{
  undefined4 uVar1;
  
  if (0 < param_3) {
    do {
      uVar1 = *param_1;
      param_1 = param_1 + 1;
      *param_2 = uVar1;
      param_2 = param_2 + 1;
      param_3 = param_3 + -1;
    } while (param_3 != 0);
  }
  return;
}

void FUN_0000153a(undefined1 *param_1,undefined1 *param_2,int param_3)

{
  undefined1 uVar1;
  
  if (0 < param_3) {
    do {
      uVar1 = *param_1;
      param_1 = param_1 + 1;
      *param_2 = uVar1;
      param_2 = param_2 + 1;
      param_3 = param_3 + -1;
    } while (param_3 != 0);
  }
  return;
}

void FUN_00001d0e(byte *param_1,uint param_2)

{
  *param_1 = *param_1 | '\x01' << (param_2 & 7);
  return;
}

uint f33_boot_select_region_for_range(uint address,uint length,uint *region)

{
  uint uVar1;
  
  if (length != 0) {
    uVar1 = 0;
    do {
      if ((f33_boot_regions[(short)uVar1].lower <= address) &&
         ((length + address) - 1 <= f33_boot_regions[(short)uVar1].upper)) {
        *region = uVar1;
        return 0;
      }
      uVar1 = uVar1 + 1;
    } while (uVar1 < 3);
  }
  return 1;
}

uint f33_boot_lookup_authentication_trailer(uint start,uint length,uint *trailer_address)

{
  short sVar1;
  uint uVar2;
  
  if (length != 0) {
    uVar2 = 0;
    do {
      sVar1 = (short)uVar2;
      if (((f33_boot_regions[sVar1].lower <= start) &&
          ((length + start) - 1 <= f33_boot_regions[sVar1].upper)) &&
         (f33_boot_regions[sVar1].authentication_trailer != 0)) {
        *trailer_address = f33_boot_regions[sVar1].authentication_trailer;
        return 0;
      }
      uVar2 = uVar2 + 1;
    } while (uVar2 < 3);
  }
  return 1;
}

uint f33_boot_lookup_completion_marker(uint start,uint length,uint *marker_address)

{
  short sVar1;
  uint uVar2;
  
  if (length != 0) {
    uVar2 = 0;
    do {
      sVar1 = (short)uVar2;
      if ((f33_boot_regions[sVar1].lower <= start) &&
         ((length + start) - 1 <= f33_boot_regions[sVar1].upper)) {
        *marker_address = f33_boot_regions[sVar1].marker_block;
        return 0;
      }
      uVar2 = uVar2 + 1;
    } while (uVar2 < 3);
  }
  return 1;
}

uint f33_boot_select_counter_block_for_range(uint address,uint length,uint *counter_block)

{
  short sVar1;
  uint uVar2;
  
  if (length != 0) {
    uVar2 = 0;
    do {
      sVar1 = (short)uVar2;
      if ((f33_boot_regions[sVar1].lower <= address) &&
         ((length + address) - 1 <= f33_boot_regions[sVar1].upper)) {
        *counter_block = f33_boot_regions[sVar1].counter_block;
        return 0;
      }
      uVar2 = uVar2 + 1;
    } while (uVar2 < 3);
  }
  return 1;
}

int FUN_000052a6(byte *param_1,uint param_2)

{
  byte bVar1;
  int iVar2;
  
  iVar2 = 0;
  for (param_2 = param_2 & 0xff; param_2 != 0; param_2 = param_2 - 1) {
    bVar1 = *param_1;
    param_1 = param_1 + 1;
    iVar2 = iVar2 * 0x100 + (uint)bVar1;
  }
  return iVar2;
}

bool FUN_00006c5a(int *param_1)

{
  return *param_1 != 0x5aa5a55a;
}

void f33_boot_security_clear_candidate_context(F33BootAes128CtrContext *context)

{
  f33_boot_aes128_ctr_clear(context);
  return;
}

uint f33_boot_aes128_initialize_context(uchar *key,uchar key_length,F33BootAes128Context *context)

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
        uVar3 = (uint)CRYPT_AES_Encryption_SBox[uVar3 & 0xff] << 0x18 |
                (uint)CRYPT_AES_Encryption_SBox[uVar3 >> 0x18] << 0x10 |
                (uint)CRYPT_AES_Encryption_SBox[(uVar3 >> 8 & 0xffff) >> 8] << 8 |
                (uint)((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x8fe0u + (uint32_t)((int)uVar2 >> 2) * 1u)))) ^
                      CRYPT_AES_Encryption_SBox[uVar3 >> 8 & 0xff]);
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

void f33_boot_aes128_clear_context(F33BootAes128Context *context)

{
  context->valid = '\0';
  FUN_000076b6(context,0xc4);
  return;
}

void f33_boot_aes128_ctr_clear(F33BootAes128CtrContext *context)

{
  (context->aes).valid = '\0';
  FUN_000076b6(context,0xe4);
  return;
}

uint f33_boot_aes128_cmac_initialize(uchar *key,uchar key_length,F33BootAes128CmacContext *context)

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
    uVar1 = f33_boot_aes128_initialize_context(key,'\x10',&context->aes);
    if (uVar1 == 0) {
      (context->aes).valid = '\x01';
      return 0;
    }
  }
  return 0xff;
}

void f33_boot_aes128_cmac_clear(F33BootAes128CmacContext *context)

{
  (context->aes).valid = '\0';
  FUN_000076b6(context,0xf8);
  return;
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

void f33_boot_aes128_cbc_clear(F33BootAes128CbcContext *context)

{
  (context->aes).valid = '\0';
  FUN_000076b6(context,0xe4);
  return;
}

int f33_stage_pair_correction(uchar selector,short *values)

{
  short *psVar1;
  int iVar2;
  uint uVar3;
  
  uVar3 = 0;
  if (selector == '\0') {
    do {
      iVar2 = uVar3 * 2;
      psVar1 = values + uVar3;
      uVar3 = uVar3 + 1 & 0xff;
      *(short *)(((undefined *)camry_host_ptr(0xfebe68aau)) + iVar2) = *psVar1;
    } while (uVar3 < 2);
    DAT_febe68b4 = 0xa55a5aa5;
    return 0;
  }
  return -6;
}

uint f33_compare_ba_token_bytes(uchar *left,uchar *right,uchar length)

{
  uint uVar1;
  
  uVar1 = 0;
  while( true ) {
    if (length <= uVar1) {
      return 1;
    }
    if ((uintptr_t)(left[uVar1])!=(uintptr_t)(right[uVar1])) break;
    uVar1 = uVar1 + 1 & 0xff;
  }
  return 0;
}

uint f33_ba_enable_closed_gate_exception(uchar operation,uchar request_length,uchar *payload)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = 0;
  uVar1 = f33_compare_ba_token_bytes
                    (payload,(uchar *)"BAENAJTEKMTMPCLJTRM1JTRM2BADISBAENATZCLRJTRM3VSPDASINC",
                     '\x05');
  if (((operation == 0xf7) && (request_length == '\x06')) && (uVar1 == 1)) {
    uVar2 = 0x5a;
  }
  return uVar2;
}

int FUN_00035004(byte *param_1)

{
  return (uint)param_1[1] + (uint)*param_1 * 0x100;
}

int FUN_00035010(byte *param_1)

{
  return (uint)param_1[3] +
         (uint)param_1[2] * 0x100 + (uint)param_1[1] * 0x10000 + (uint)*param_1 * 0x1000000;
}

int f33_ba_f3_validate_tmpcl(uchar configured_index,uchar *payload,uchar *response)

{
  uint uVar1;
  
  if (f33_ba_application_work.retained_start_phase == '\0') {
    uVar1 = f33_compare_ba_token_bytes
                      (payload,"TMPCLJTRM1JTRM2BADISBAENATZCLRJTRM3VSPDASINC",'\x05');
    if (uVar1 == 1) {
      return 0;
    }
  }
  else if (f33_ba_application_work.retained_start_phase == 'Z') {
    if ((DAT_febe6ee4 == '\x01') || (DAT_febe7de4 == '\x01')) {
      return -1;
    }
    if ((((int8_t)DAT_febe6ee4) == -1) && (((int8_t)DAT_febe7de4) == -1)) {
      return 0;
    }
  }
  return -6;
}

int f33_ba_f8_validate_tzclr(uchar configured_index,uchar *payload,uchar *response)

{
  char cVar1;
  char cVar2;
  char cVar3;
  ushort uVar4;
  uint uVar5;
  
  uVar4 = DAT_febee892;
  cVar3 = DAT_febee88a;
  cVar2 = DAT_febee884;
  cVar1 = DAT_febee81f;
  uVar5 = f33_compare_ba_token_bytes(payload,"TZCLRJTRM3VSPDASINC",'\x05');
  if ((((uVar5 != 1) || (cVar1 != '\0')) || (f33_ba_tzclr_raw_input_limit < uVar4)) ||
     ((cVar2 == 'Z' || (uVar5 = (uint)(cVar3 == 'Z'), cVar3 == 'Z')))) {
    uVar5 = 0xfffffffa;
  }
  return uVar5;
}

int f33_ba_fa_stage_unsigned_override(uchar configured_index,uchar *payload,uchar *response)

{
  char cVar1;
  uint32_t puVar2;
  uint uVar3;
  int iVar4;
  
  cVar1 = DAT_febe80a5;
  puVar2 = 0xfebeb800u;
  uVar3 = f33_compare_ba_token_bytes(payload + 1,"VSPDASINC",'\x04');
  if ((uVar3 == 1) && (cVar1 != '\0')) {
    iVar4 = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x58ae))))) = *payload;
  }
  else {
    iVar4 = -6;
  }
  return iVar4;
}

int f33_ba_fb_validate_asinc(uchar configured_index,uchar *payload,uchar *response)

{
  uint uVar1;
  int iVar2;
  
  uVar1 = f33_compare_ba_token_bytes(payload,"ASINC",'\x05');
  if (uVar1 == 1) {
    iVar2 = 0;
  }
  else {
    iVar2 = -6;
  }
  return iVar2;
}

uint f33_choose_thermal_limit_source
               (ushort current,ushort candidate,uchar *source,uchar candidate_source)

{
  uint uVar1;
  
  uVar1 = (uint)current;
  if (((uintptr_t)(source)!=(uintptr_t)((uchar *)0x0)) && (candidate <= uVar1)) {
    *source = candidate_source;
    uVar1 = (uint)candidate;
  }
  return uVar1;
}

void f33_select_motor_thermal_diagnostic
               (ushort limit,ushort nominal,uchar *active,short *temperature)

{
  short sVar1;
  
  if (limit < nominal) {
    *active = '\x01';
    sVar1 = DAT_febe6f82;
  }
  else {
    *active = '\0';
    sVar1 = 0;
  }
  *temperature = sVar1;
  return;
}

void FUN_0004afcc(char param_1,short param_2,uint param_3,undefined2 *param_4)

{
  int iVar1;
  
  if (param_1 == '\0') {
    iVar1 = (param_3 & 0xffff) - (int)param_2;
    if (iVar1 + -0x7fff < 0 == (iVar1 < 0 && -1 < iVar1 + -0x7fff) && iVar1 != 0x7fff) {
      iVar1 = 0x7fff;
    }
    *param_4 = (short)iVar1;
  }
  return;
}

uint f33_get_dtc_status_availability_mask(uchar *mask)

{
  *mask = 0xb9;
  return 0;
}

uint f33_next_snapshot_identifier_tuple(uint *dtc,uchar *record_number)

{
  uint32_t puVar1;
  byte bVar2;
  uint uVar3;
  uchar uVar4;
  uint local_10;
  
  puVar1 = 0xfebeb800u;
  uVar3 = (uint)DAT_febe8199;
  local_10 = f33_snapshot_identifier_cached_dtc;
  if (((uintptr_t)(dtc)==(uintptr_t)((uint *)0x0)) || ((uintptr_t)(record_number)==(uintptr_t)((uchar *)0x0))) {
LAB_0004d786:
    local_10 = 0;
    bVar2 = 0;
    uVar3 = 1;
  }
  else {
    puVar1 = 0xfebeb800u;
    if (f33_snapshot_identifier_cached_dtc == 0) {
      puVar1 = 0xfebeb800u;
      uVar3 = f33_get_secondary_capture_record_mask(&local_10);
    }
    if ((uVar3 & 1) == 0) {
      if ((uVar3 >> 1 & 1) == 0) goto LAB_0004d786;
      bVar2 = (byte)uVar3 & 0xfd;
      uVar4 = '\x10';
      *dtc = local_10;
    }
    else {
      bVar2 = (byte)uVar3 & 0xfe;
      uVar4 = '\x01';
      *dtc = local_10;
    }
    *record_number = uVar4;
    uVar3 = 0;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3667))))) = bVar2;
  (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x363c)))) = local_10;
  return uVar3;
}

undefined4 f33_rdbi_0204_callback(undefined1 *param_1)

{
  char cVar1;
  undefined1 uVar2;
  
  cVar1 = DAT_febee856;
  *param_1 = 0x80;
  uVar2 = 0;
  if (cVar1 == '\x11') {
    uVar2 = 0x80;
  }
  param_1[1] = uVar2;
  return 0;
}

undefined4 f33_rdbi_1033_callback(undefined1 *param_1)

{
  undefined1 uStack_9;
  
  uStack_9 = DAT_febee811;
  FUN_0007016e(DAT_febee811,1,&uStack_9);
  *param_1 = uStack_9;
  return 0;
}

uint f33_rdbi_1034_callback(uchar *output)

{
  undefined2 uStack_a;
  
  uStack_a = (undefined2)((uint)DAT_febe66ba * 100 >> 8);
  FUN_00070180((uint)DAT_febe66ba * 100 >> 8,0x9c4,&uStack_a);
  FUN_0006a574(uStack_a,output);
  return 0;
}

undefined4 f33_rdbi_1038_callback(byte *param_1)

{
  *param_1 = DAT_febe7fec & 0xf;
  return 0;
}

undefined4 f33_rdbi_1064_callback(undefined1 *param_1)

{
  undefined1 uStack_9;
  
  uStack_9 = DAT_febee829;
  FUN_0007016e(DAT_febee829,2,&uStack_9);
  *param_1 = uStack_9;
  return 0;
}

undefined4 f33_rdbi_1133_callback(undefined1 *param_1)

{
  undefined1 uStack_9;
  
  uStack_9 = DAT_febee88b;
  FUN_0007016e(DAT_febee88b,3,&uStack_9);
  *param_1 = uStack_9;
  return 0;
}

undefined4 f33_rdbi_1181_callback(undefined1 *param_1)

{
  undefined1 uStack_9;
  
  uStack_9 = DAT_febe7d44;
  FUN_0007016e(DAT_febe7d44,3,&uStack_9);
  *param_1 = uStack_9;
  return 0;
}

undefined4 f33_rdbi_1182_callback(byte *param_1)

{
  byte bVar1;
  
  bVar1 = DAT_febe8006;
  if (4 < DAT_febe8006) {
    bVar1 = 1;
  }
  *param_1 = bVar1;
  return 0;
}

undefined4 f33_rdbi_11b1_callback(undefined1 *param_1)

{
  undefined4 uVar1;
  undefined2 uStack_a;
  
  uVar1 = FUN_000546f2(0);
  uStack_a = (undefined2)uVar1;
  FUN_00070180(uVar1,0xff,&uStack_a);
  *param_1 = (char)uStack_a;
  return 0;
}

undefined4 f33_rdbi_11b3_callback(undefined1 *param_1)

{
  undefined4 uVar1;
  undefined2 uStack_a;
  
  uVar1 = FUN_000546f2(5);
  uStack_a = (undefined2)uVar1;
  FUN_00070180(uVar1,0xff,&uStack_a);
  *param_1 = (char)uStack_a;
  return 0;
}

undefined4 f33_rdbi_11b4_callback(undefined1 *param_1)

{
  undefined4 uVar1;
  undefined2 uStack_a;
  
  uVar1 = FUN_000546f2(6);
  uStack_a = (undefined2)uVar1;
  FUN_00070180(uVar1,0xff,&uStack_a);
  *param_1 = (char)uStack_a;
  return 0;
}

undefined4 f33_rdbi_11b5_callback(undefined1 *param_1)

{
  undefined4 uVar1;
  undefined2 uStack_a;
  
  uVar1 = FUN_000546f2(7);
  uStack_a = (undefined2)uVar1;
  FUN_00070180(uVar1,0xff,&uStack_a);
  *param_1 = (char)uStack_a;
  return 0;
}

undefined4 f33_rdbi_11b6_callback(undefined1 *param_1)

{
  short sStack_a;
  
  sStack_a = (ushort)DAT_febe8645 + (ushort)DAT_febe8644;
  FUN_00070180(sStack_a,0xff,&sStack_a);
  *param_1 = (char)sStack_a;
  return 0;
}

undefined4 f33_rdbi_11b7_callback(undefined1 *param_1)

{
  undefined1 uStack_9;
  
  uStack_9 = DAT_febe8646;
  FUN_0007016e(DAT_febe8646,0xff,&uStack_9);
  *param_1 = uStack_9;
  return 0;
}

undefined4 f33_rdbi_11b8_callback(undefined1 *param_1)

{
  undefined1 uStack_9;
  
  uStack_9 = DAT_febe8647;
  FUN_0007016e(DAT_febe8647,0xff,&uStack_9);
  *param_1 = uStack_9;
  return 0;
}

undefined4 f33_rdbi_11b9_callback(undefined1 *param_1)

{
  undefined1 uStack_9;
  
  uStack_9 = DAT_febe8648;
  FUN_0007016e(DAT_febe8648,0xff,&uStack_9);
  *param_1 = uStack_9;
  return 0;
}

undefined4 f33_rdbi_11ba_callback(undefined1 *param_1)

{
  undefined1 uStack_9;
  
  uStack_9 = DAT_febe8649;
  FUN_0007016e(DAT_febe8649,0xff,&uStack_9);
  *param_1 = uStack_9;
  return 0;
}

undefined4 f33_rdbi_11bb_callback(undefined1 *param_1)

{
  undefined1 uStack_9;
  
  uStack_9 = DAT_febe864b;
  FUN_0007016e(DAT_febe864b,0xff,&uStack_9);
  *param_1 = uStack_9;
  return 0;
}

undefined4 f33_rdbi_11bd_callback(undefined1 *param_1)

{
  undefined4 uVar1;
  undefined2 uStack_a;
  
  uVar1 = FUN_000546f2(0xe);
  uStack_a = (undefined2)uVar1;
  FUN_00070180(uVar1,0xff,&uStack_a);
  *param_1 = (char)uStack_a;
  return 0;
}

undefined4 f33_rdbi_1c08_callback(undefined1 *param_1)

{
  undefined1 uStack_9;
  
  uStack_9 = DAT_febe6f6c;
  FUN_0007016e(DAT_febe6f6c,0xff,&uStack_9);
  *param_1 = uStack_9;
  return 0;
}

undefined4 f33_rdbi_1c09_callback(undefined1 *param_1)

{
  undefined1 uStack_9;
  
  uStack_9 = DAT_febe6f6d;
  FUN_0007016e(DAT_febe6f6d,0xff,&uStack_9);
  *param_1 = uStack_9;
  return 0;
}

undefined4 f33_rdbi_1c31_callback(undefined1 *param_1)

{
  undefined1 uStack_9;
  
  uStack_9 = DAT_febee840;
  FUN_0007016e(DAT_febee840,1,&uStack_9);
  *param_1 = uStack_9;
  return 0;
}

undefined4 f33_rdbi_1c33_callback(undefined1 *param_1)

{
  undefined2 uStack_a;
  
  uStack_a = DAT_febee8c4;
  FUN_00070180(DAT_febee8c4,0xff,&uStack_a);
  *param_1 = (char)uStack_a;
  return 0;
}

undefined4 f33_rdbi_1c37_callback(undefined1 *param_1)

{
  undefined1 uStack_9;
  
  uStack_9 = DAT_febee842;
  FUN_0007016e(DAT_febee842,1,&uStack_9);
  *param_1 = uStack_9;
  return 0;
}

undefined4 f33_rdbi_1c39_callback(undefined1 *param_1)

{
  undefined2 uStack_a;
  
  uStack_a = DAT_febee8c8;
  FUN_00070180(DAT_febee8c8,0xff,&uStack_a);
  *param_1 = (char)uStack_a;
  return 0;
}

undefined4 f33_rdbi_1c3d_callback(undefined1 *param_1)

{
  undefined1 uStack_9;
  
  uStack_9 = DAT_febee82d;
  FUN_0007016e(DAT_febee82d,1,&uStack_9);
  *param_1 = uStack_9;
  return 0;
}

undefined4 f33_rdbi_1c3f_callback(undefined1 *param_1)

{
  undefined2 uStack_a;
  
  uStack_a = DAT_febee8b8;
  FUN_00070180(DAT_febee8b8,0xff,&uStack_a);
  *param_1 = (char)uStack_a;
  return 0;
}

undefined4 f33_rdbi_1c43_callback(undefined1 *param_1)

{
  undefined1 uStack_9;
  
  uStack_9 = DAT_febee831;
  FUN_0007016e(DAT_febee831,1,&uStack_9);
  *param_1 = uStack_9;
  return 0;
}

undefined4 f33_rdbi_1c49_callback(undefined1 *param_1)

{
  undefined1 uStack_9;
  
  uStack_9 = DAT_febee83e;
  FUN_0007016e(DAT_febee83e,1,&uStack_9);
  *param_1 = uStack_9;
  return 0;
}

undefined4 f33_rdbi_1c4b_callback(undefined1 *param_1)

{
  undefined2 uStack_a;
  
  uStack_a = DAT_febee8be;
  FUN_00070180(DAT_febee8be,0xff,&uStack_a);
  *param_1 = (char)uStack_a;
  return 0;
}

undefined4 f33_rdbi_1c4f_callback(undefined1 *param_1)

{
  undefined1 uStack_9;
  
  uStack_9 = DAT_febee83f;
  FUN_0007016e(DAT_febee83f,1,&uStack_9);
  *param_1 = uStack_9;
  return 0;
}

undefined4 f33_rdbi_1c51_callback(undefined1 *param_1)

{
  undefined2 uStack_a;
  
  uStack_a = DAT_febee8c0;
  FUN_00070180(DAT_febee8c0,0xff,&uStack_a);
  *param_1 = (char)uStack_a;
  return 0;
}

undefined4 f33_rdbi_1c52_callback(undefined1 *param_1)

{
  undefined1 uStack_9;
  
  uStack_9 = DAT_febee860;
  FUN_0007016e(DAT_febee860,0xf,&uStack_9);
  *param_1 = uStack_9;
  return 0;
}

undefined4 f33_rdbi_1c81_callback(undefined1 *param_1)

{
  undefined4 uVar1;
  undefined2 uStack_a;
  
  uVar1 = FUN_000546f2(8);
  uStack_a = (undefined2)uVar1;
  FUN_00070180(uVar1,0xff,&uStack_a);
  *param_1 = (char)uStack_a;
  return 0;
}

undefined4 f33_rdbi_1c82_callback(undefined1 *param_1)

{
  undefined4 uVar1;
  undefined2 uStack_a;
  
  uVar1 = FUN_000546f2(2);
  uStack_a = (undefined2)uVar1;
  FUN_00070180(uVar1,0xff,&uStack_a);
  *param_1 = (char)uStack_a;
  return 0;
}

undefined4 f33_rdbi_1c83_callback(undefined1 *param_1)

{
  undefined4 uVar1;
  undefined2 uStack_a;
  
  uVar1 = FUN_000546f2(3);
  uStack_a = (undefined2)uVar1;
  FUN_00070180(uVar1,0xff,&uStack_a);
  *param_1 = (char)uStack_a;
  return 0;
}

undefined4 f33_rdbi_1c84_callback(undefined1 *param_1)

{
  undefined4 uVar1;
  undefined2 uStack_a;
  
  uVar1 = FUN_000546f2(0xd);
  uStack_a = (undefined2)uVar1;
  FUN_00070180(uVar1,0xff,&uStack_a);
  *param_1 = (char)uStack_a;
  return 0;
}

undefined4 f33_rdbi_1c86_callback(undefined1 *param_1)

{
  undefined2 uStack_a;
  
  uStack_a = DAT_febe7bcc;
  FUN_00070180(DAT_febe7bcc,0xff,&uStack_a);
  *param_1 = (char)uStack_a;
  return 0;
}

undefined4 f33_rdbi_1ca1_callback(undefined1 *param_1)

{
  undefined1 uStack_9;
  
  uStack_9 = DAT_febee816;
  FUN_0007016e(DAT_febee816,0xff,&uStack_9);
  *param_1 = uStack_9;
  return 0;
}

undefined4 f33_rdbi_1ca5_callback(undefined1 *param_1)

{
  undefined1 uStack_9;
  
  uStack_9 = DAT_febee817;
  FUN_0007016e(DAT_febee817,0xff,&uStack_9);
  *param_1 = uStack_9;
  return 0;
}

undefined4 f33_rdbi_2002_callback(undefined1 *param_1)

{
  undefined1 uVar1;
  
  if (DAT_febee91c == 0x55aaaa55) {
    uVar1 = 0;
  }
  else if (DAT_febee91c == -0x55aaaa56) {
    uVar1 = 1;
  }
  else {
    uVar1 = 0xff;
  }
  *param_1 = uVar1;
  return 0;
}

undefined4 f33_rdbi_2005_callback(undefined1 *param_1)

{
  undefined1 uStack_9;
  
  uStack_9 = DAT_febee84d;
  if (DAT_febee84a == 'Z') {
    FUN_0007016e(DAT_febee84d,0xff,&uStack_9);
  }
  else {
    uStack_9 = 0xff;
  }
  *param_1 = uStack_9;
  return 0;
}

undefined4 f33_rdbi_2006_callback(undefined1 *param_1)

{
  undefined1 uStack_9;
  
  uStack_9 = DAT_febee84e;
  if (DAT_febee84a == 'Z') {
    FUN_0007016e(DAT_febee84e,0xff,&uStack_9);
  }
  else {
    uStack_9 = 0xff;
  }
  *param_1 = uStack_9;
  return 0;
}

undefined4 f33_rdbi_2007_callback(undefined1 *param_1)

{
  undefined1 uStack_9;
  
  uStack_9 = DAT_febee84f;
  if (DAT_febee84a == 'Z') {
    FUN_0007016e(DAT_febee84f,0xff,&uStack_9);
  }
  else {
    uStack_9 = 0xff;
  }
  *param_1 = uStack_9;
  return 0;
}

undefined4 f33_rdbi_2008_callback(undefined1 *param_1)

{
  undefined1 uStack_9;
  
  uStack_9 = DAT_febee850;
  if (DAT_febee84a == 'Z') {
    FUN_0007016e(DAT_febee850,0xff,&uStack_9);
  }
  else {
    uStack_9 = 0xff;
  }
  *param_1 = uStack_9;
  return 0;
}

undefined4 f33_rdbi_2009_callback(undefined1 *param_1)

{
  undefined1 uStack_9;
  
  uStack_9 = DAT_febee851;
  if (DAT_febee84a == 'Z') {
    FUN_0007016e(DAT_febee851,0xff,&uStack_9);
  }
  else {
    uStack_9 = 0xff;
  }
  *param_1 = uStack_9;
  return 0;
}

undefined4 f33_rdbi_200d_callback(undefined1 *param_1)

{
  undefined1 uStack_9;
  
  uStack_9 = DAT_febee852;
  if (DAT_febee84a == 'Z') {
    FUN_0007016e(DAT_febee852,0xff,&uStack_9);
  }
  else {
    uStack_9 = 0xff;
  }
  *param_1 = uStack_9;
  return 0;
}

undefined4 f33_rdbi_2010_callback(undefined1 *param_1)

{
  undefined1 uVar1;
  
  if ((DAT_febee924 == 0x55aaaa55) && (DAT_febee92c == 0x55aaaa55)) {
    uVar1 = 0;
    goto LAB_0004f976;
  }
  if (DAT_febee924 == -0x55aaaa56) {
    if (DAT_febee92c == 0x55aaaa55) {
      uVar1 = 1;
      goto LAB_0004f976;
    }
    if (DAT_febee92c == -0x55aaaa56) {
      uVar1 = 2;
      goto LAB_0004f976;
    }
  }
  if ((DAT_febee924 == 0x55aaaa55) && (DAT_febee92c == -0x55aaaa56)) {
    uVar1 = 3;
  }
  else {
    uVar1 = 0xff;
  }
LAB_0004f976:
  *param_1 = uVar1;
  return 0;
}

undefined4 f33_rdbi_2032_callback(undefined1 *param_1)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  *param_1 = 1;
  iVar3 = FUN_00062e18();
  iVar2 = 0;
  if (iVar3 == 0) {
    do {
      iVar1 = iVar2 + 1;
      iVar3 = iVar2 + -0xf;
      param_1[iVar2 + 1] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x17d80u + (uint32_t)(iVar2) * 1u))));
      iVar2 = iVar1;
    } while (((iVar3 < 0) || (iVar1 < 0)));
  }
  else {
    do {
      iVar1 = iVar2 + 1;
      param_1[iVar2 + 1] = 0x21;
      iVar3 = iVar2 + -0xf;
      iVar2 = iVar1;
    } while (((iVar3 < 0) || (iVar1 < 0)));
  }
  return 0;
}

undefined4 f33_rdbi_f181_callback(undefined1 *param_1)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  *param_1 = 2;
  iVar3 = FUN_00062e18();
  iVar2 = 0;
  if (iVar3 == 0) {
    do {
      param_1[iVar2 + 1] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x20860u + (uint32_t)(iVar2) * 1u))));
      iVar1 = iVar2 + 1;
      iVar3 = iVar2 + -0xf;
      param_1[iVar2 + 0x11] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x17dc0u + (uint32_t)(iVar2) * 1u))));
      iVar2 = iVar1;
    } while (((iVar3 < 0) || (iVar1 < 0)));
  }
  else {
    do {
      iVar1 = iVar2 + 1;
      param_1[iVar2 + 1] = 0x21;
      iVar3 = iVar2 + -0xf;
      param_1[iVar2 + 0x11] = 0x21;
      iVar2 = iVar1;
    } while (((iVar3 < 0) || (iVar1 < 0)));
  }
  return 0;
}

uint f33_write_0204_stage_mode_persistence(uchar *payload,ushort unused_length)

{
  DAT_febe81af = 0x21;
  if ((payload[1] & 0x80) != 0) {
    DAT_febe81af = 0x11;
  }
  DAT_febe81b2 = 0x2e10;
  return 2;
}

uint f33_diag_routine_1004_admit(uchar control_type,uchar *input)

{
  if (DAT_febe819a == '\x01') {
    return 5;
  }
  if (control_type == '\x01') {
    if ((*input != 0xff) || (input[1] != 0xff)) {
      return 4;
    }
    if (DAT_febe819e == '\x01') {
      return 8;
    }
  }
  else if (control_type != '\x03') {
    return 7;
  }
  return 0;
}

void f33_copy_diagnostic_supplement(uchar *destination,uchar *source)

{
  int iVar1;
  uint uVar2;
  
  uVar2 = 0;
  do {
    iVar1 = uVar2 * 4;
    uVar2 = uVar2 + 1;
    *(undefined4 *)(destination + iVar1) = *(undefined4 *)(source + iVar1);
  } while (uVar2 < 0x12);
  return;
}

uint f33_get_secondary_capture_record_mask(uint *dtc)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  
  uVar2 = 0;
  if (((uintptr_t)(dtc)!=(uintptr_t)((uint *)0x0)) && (DAT_febe6152 == '\x01')) {
    uVar1 = 0;
    if (f33_diagnostic_capture_slots[1].event < 0x180) {
      uVar1 = *(uint *)(((undefined *)camry_host_ptr(0x30850u)) +
                       (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2fc52u + (uint32_t)((uint)f33_diagnostic_capture_slots[1].event * 8) * 1u))))
                       * 8);
    }
    uVar3 = 0;
    if (f33_diagnostic_capture_slots[1].event_copy < 0x180) {
      uVar3 = *(uint *)(((undefined *)camry_host_ptr(0x30850u)) +
                       (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2fc52u + (uint32_t)((uint)f33_diagnostic_capture_slots[1].event_copy * 8) * 1u)))) * 8);
    }
    if ((uVar1 == uVar3) && (uVar1 != 0)) {
      *dtc = uVar1;
      uVar2 = 3;
    }
  }
  return uVar2;
}

undefined4 FUN_00053168(int param_1,int param_2,ushort param_3,undefined1 *param_4)

{
  undefined1 uVar1;
  undefined4 uVar2;
  
  uVar2 = 0;
  if (((param_2 == 0) || (DAT_febe6152 != '\x01')) || (param_1 == 0)) {
    uVar1 = 1;
  }
  else if (param_3 < 2) {
    uVar1 = 2;
    uVar2 = 0xffffffff;
  }
  else {
    uVar1 = 0;
    uVar2 = 0;
  }
  *param_4 = uVar1;
  return uVar2;
}

void f33_capture_slot_dispatch_53354(undefined4 param_1,uchar *param_2)

{
  undefined4 uVar1;
  uchar uVar2;
  
  uVar1 = (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * 240u + 200u))));
  if (0xf423fu < (uint)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * 240u + 200u))))) {
    (*((uint8_t *)((uint8_t *)&uVar1 + 0u))) = '\0';
    (*((uint8_t *)((uint8_t *)&uVar1 + 1u))) = '\0';
    (*((uint8_t *)((uint8_t *)&uVar1 + 2u))) = '\0';
    (*((uint8_t *)((uint8_t *)&uVar1 + 3u))) = '\0';
  }
  uVar2 = f33_diagnostic_capture_slots[1].extended_middle[7];
  if (1 < f33_diagnostic_capture_slots[1].extended_middle[7]) {
    uVar2 = '\x02';
  }
  FUN_0006a55c(uVar1, param_2);
  *param_2 = uVar2;
  return;
}

undefined4 FUN_00054f6e(char param_1,undefined2 *param_2,undefined2 *param_3)

{
  undefined2 uVar1;
  undefined4 uVar2;
  undefined2 uVar3;
  
  if (DAT_febe89d8 == DAT_febe86ca) {
    if (param_1 == '\x02') {
LAB_00054f92:
      uVar1 = 0x12;
      uVar3 = 0x13;
      uVar2 = 1;
      goto LAB_00054f9c;
    }
  }
  else if (param_1 != '\x02') goto LAB_00054f92;
  uVar1 = 0x13;
  uVar3 = 0x12;
  uVar2 = 2;
LAB_00054f9c:
  *param_2 = uVar1;
  *param_3 = uVar3;
  return uVar2;
}

F33CaptureFieldDescriptor * FUN_00056664(undefined2 *param_1)

{
  *param_1 = 0x4b;
  return f33_capture_field_descriptor;
}

undefined * FUN_00056674(undefined2 *param_1)

{
  *param_1 = 6;
  return ((undefined *)camry_host_ptr(0x2aa6cu));
}

undefined4 FUN_000623ee(byte *param_1)

{
  undefined4 uVar1;
  
  uVar1 = 0x5a;
  if (param_1[8] ==
      ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2b118u + (uint32_t)(param_1[9] ^
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2b118u + (uint32_t)(param_1[6] ^
         (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2b118u + (uint32_t)(param_1[7] ^
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2b118u + (uint32_t)(param_1[4] ^
           (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2b118u + (uint32_t)(param_1[5] ^
            (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2b118u + (uint32_t)(param_1[2] ^ (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2b118u + (uint32_t)(param_1[3] ^ (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2b118u + (uint32_t)(*param_1 ^ 0xff) * 1u))))) * 1u))))) * 1u))))) * 1u))))) * 1u))))) * 1u))))) * 1u))))) * 1u)))) ^
      0xff)) {
    uVar1 = 0;
  }
  return uVar1;
}

byte FUN_000625f6(byte *param_1)

{
  return (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2b118u + (uint32_t)(param_1[5] ^
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2b118u + (uint32_t)(param_1[2] ^
           (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2b118u + (uint32_t)(param_1[3] ^ (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2b118u + (uint32_t)(*param_1 ^ (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2b118u + (uint32_t)(param_1[1] ^ 0xff) * 1u))))) * 1u))))) * 1u))))) * 1u))))) * 1u)))) ^ 0xff;
}

void f33_rotate_and_copy_serial_acquisition_masks(F33SerialAcquisitionMasks *output)

{
  F33SerialAcquisitionMasks *pFVar1;
  ushort uVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  uint uVar6;
  
  uVar5 = 0;
  do {
    iVar4 = (short)uVar5 * 0x5a;
    uVar6 = (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe392eu + (uint32_t)(iVar4) * 1u)))) & 3;
    iVar3 = (uVar6 - 1 & 3) * 2 + iVar4;
    *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe3900u)) + iVar3 + 0x30) = 0;
    *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe3900u)) + iVar3 + 0x38) = 0;
    uVar2 = *(ushort *)(((undefined *)camry_host_ptr(0xfebe3930u)) + uVar6 * 2 + iVar4);
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe392eu + (uint32_t)(iVar4) * 1u)))) = (char)uVar6 + 1U & 3;
    pFVar1 = output + uVar5;
    uVar5 = uVar5 + 1;
    pFVar1->first = uVar2;
    pFVar1->second = *(ushort *)(((undefined *)camry_host_ptr(0xfebe3900u)) + uVar6 * 2 + iVar4 + 0x38);
  } while (uVar5 < 2);
  return;
}

undefined4 FUN_00062d56(undefined2 *param_1)

{
  *param_1 = 0;
  return 0;
}

uint f33_crypto_bank_read_direct_result(uchar *output,ushort length)

{
  uchar uVar1;
  uint uVar2;
  uint uVar3;
  
  uVar1 = f33_crypto_direct_activation;
  uVar3 = (uint)length;
  if (uVar3 < 0x32) {
    if (uVar3 == 0) goto LAB_00069f8c;
  }
  else {
    uVar3 = 0x31;
  }
  *output = f33_crypto_direct_activation;
  uVar2 = 1;
  if (uVar1 == '\x02') {
    for (; uVar2 < uVar3; uVar2 = uVar2 + 1 & 0xffff) {
      output[uVar2] = f33_crypto_key_request[1][uVar2 + 0x3f];
    }
  }
  else {
    for (; uVar2 < uVar3; uVar2 = uVar2 + 1 & 0xffff) {
      output[uVar2] = '\0';
    }
  }
LAB_00069f8c:
  if ((uVar1 == '\x02') || (uVar1 == 0xff)) {
    uVar3 = 0;
    do {
      uVar2 = uVar3 + 1;
      f33_crypto_key_request[0][uVar3] = '\0';
      uVar3 = uVar2;
    } while (uVar2 < 0x40);
    uVar3 = 0;
    do {
      uVar2 = uVar3 + 1;
      f33_crypto_key_result[0][uVar3] = '\0';
      uVar3 = uVar2;
    } while (uVar2 < 0x30);
  }
  return 0;
}

void FUN_0006a53e(int param_1,int *param_2)

{
  if (param_1 + 0x7fffffff < 0 == (-1 < param_1 && param_1 + 0x7fffffff < 0) &&
      param_1 != -0x7fffffff) {
    if (param_1 < 0) {
      param_1 = -param_1;
    }
  }
  else {
    param_1 = 0x7fffffff;
  }
  *param_2 = param_1;
  return;
}

void FUN_0006a55c(undefined4 param_1,undefined1 *param_2)

{
  *param_2 = (char)((uint)param_1 >> 0x18);
  param_2[1] = (char)((uint)param_1 >> 0x10);
  param_2[2] = (char)((uint)param_1 >> 8);
  param_2[3] = (char)param_1;
  return;
}

void FUN_0006a594(undefined4 param_1,undefined1 *param_2)

{
  *param_2 = (char)((uint)param_1 >> 0x18);
  param_2[1] = (char)((uint)param_1 >> 0x10);
  param_2[2] = (char)((uint)param_1 >> 8);
  param_2[3] = (char)param_1;
  return;
}

void FUN_0006a5ac(undefined4 param_1,undefined1 *param_2)

{
  *param_2 = (char)((uint)param_1 >> 8);
  param_2[1] = (char)param_1;
  return;
}

void FUN_0006a5fa(int param_1,undefined2 *param_2)

{
  undefined2 uVar1;
  
  if (param_1 + 0x7fff < 0 == (-1 < param_1 && param_1 + 0x7fff < 0)) {
    if (param_1 + -0x7fff < 0 == (param_1 < 0 && -1 < param_1 + -0x7fff) && param_1 != 0x7fff) {
      uVar1 = 0x7fff;
    }
    else {
      if (param_1 + 0x8000 < 0 != (-1 < param_1 && param_1 + 0x8000 < 0) || param_1 == -0x8000) {
        param_1 = -0x8000;
      }
      uVar1 = (undefined2)param_1;
    }
  }
  else {
    uVar1 = 0x8001;
  }
  *param_2 = uVar1;
  return;
}

void FUN_0006a624(uint param_1,undefined1 *param_2)

{
  undefined1 uVar1;
  
  uVar1 = 0;
  if (-1 < (int)param_1) {
    if (param_1 < 0xff) {
      uVar1 = (undefined1)param_1;
    }
    else {
      uVar1 = 0xff;
    }
  }
  *param_2 = uVar1;
  return;
}

void FUN_0006a678(ushort *param_1,int param_2,undefined2 *param_3,int *param_4)

{
  int iVar1;
  
  if (0xfffe < param_2 - 1U) {
    param_2 = 0x10000;
  }
  iVar1 = (uint)param_1[1] * param_2 + (*(int *)(param_1 + 2) - (uint)*param_1 * param_2);
  *param_3 = (short)((uint)iVar1 >> 0x10);
  *param_4 = iVar1;
  return;
}

void f33_retain_disabled_recoverable_monitor
               (F33RecoverableMonitorState *state,F33RecoverableMonitorLimits *limits)

{
  uint uVar1;
  
  if ((uintptr_t)(limits->failing_limit)<(uintptr_t)(state->failing_count)) {
    uVar1 = 0x22;
  }
  else {
    if ((state->failing_count == 0) && ((uintptr_t)(limits->passing_limit)<(uintptr_t)(state->passing_count))) {
      uVar1 = 0x2200;
    }
    else {
      state->passing_count = 0;
      uVar1 = 0;
    }
    state->failing_count = 0;
    state->recovery_count = 0;
  }
  state->packed_status = uVar1;
  return;
}

void f33_retain_disabled_latched_monitor(F33LatchedMonitorState *state,F33MonitorLimits *limits)

{
  uint uVar1;
  
  if ((uintptr_t)(limits->failing_limit)<(uintptr_t)(state->failing_count)) {
    uVar1 = 0x22;
  }
  else {
    if ((state->failing_count == 0) && ((uintptr_t)(limits->passing_limit)<(uintptr_t)(state->passing_count))) {
      uVar1 = 0x2200;
    }
    else {
      state->passing_count = 0;
      uVar1 = 0;
    }
    state->failing_count = 0;
  }
  state->packed_status = uVar1;
  return;
}

void FUN_0006ae48(undefined4 *param_1,ushort *param_2)

{
  undefined4 uVar1;
  
  if (param_2[2] < *(ushort *)(param_1 + 2)) {
    uVar1 = 0x22;
  }
  else {
    if ((*(ushort *)(param_1 + 2) == 0) && (*param_2 < *(ushort *)(param_1 + 1))) {
      uVar1 = 0x2200;
    }
    else {
      *(undefined2 *)(param_1 + 1) = 0;
      uVar1 = 0;
      (*((undefined2 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 6)))) = 0;
    }
    *(undefined2 *)(param_1 + 2) = 0;
    (*((undefined2 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 10)))) = 0;
  }
  *param_1 = uVar1;
  return;
}

void f33_retain_disabled_escalating_monitor(F33EscalatingMonitorState *state,ushort *calibration)

{
  uint uVar1;
  
  if ((uintptr_t)(calibration[7])<(uintptr_t)(state->elapsed_count)) {
    uVar1 = 0x44;
  }
  else if ((state->elapsed_count == 0) && ((uintptr_t)(state->failing_count)<=(uintptr_t)(calibration[5]))) {
    if ((state->failing_count == 0) && ((uintptr_t)(calibration[2])<(uintptr_t)(state->passing_count))) {
      uVar1 = 0x2200;
    }
    else {
      state->passing_count = 0;
      uVar1 = 0;
    }
    state->failing_count = 0;
    state->recovery_count = 0;
    state->elapsed_count = 0;
  }
  else {
    uVar1 = 0x22;
  }
  state->packed_status = uVar1;
  return;
}

void FUN_0007013e(uint param_1,uint param_2,uint param_3,uint *param_4)

{
  if (param_2 < param_1) {
    param_1 = param_2;
  }
  if (param_1 < param_3) {
    param_1 = param_3;
  }
  *param_4 = param_1;
  return;
}

void FUN_0007016e(byte param_1,byte param_2,byte *param_3)

{
  if (param_2 < param_1) {
    param_1 = param_2;
  }
  *param_3 = param_1;
  return;
}

void FUN_00070180(ushort param_1,ushort param_2,ushort *param_3)

{
  if (param_2 < param_1) {
    param_1 = param_2;
  }
  *param_3 = param_1;
  return;
}

void FUN_00070192(uint param_1,uint param_2,uint *param_3)

{
  if (param_2 < param_1) {
    param_1 = param_2;
  }
  *param_3 = param_1;
  return;
}

void FUN_000702b0(ushort *param_1,uint param_2,ushort *param_3)

{
  ushort *puVar1;
  ushort uVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  
  param_2 = param_2 & 0xffff;
  if ((*param_1 == 0xffff) || (param_2 <= *param_1)) {
    uVar2 = param_1[1];
  }
  else {
    iVar3 = 0;
    while( true ) {
      puVar1 = param_1 + iVar3 * 2;
      uVar5 = (uint)*puVar1;
      if (uVar5 == 0xffff) break;
      if (param_2 < uVar5) {
        iVar3 = uVar5 - puVar1[-2];
        iVar4 = (param_2 - puVar1[-2]) * ((int)(short)puVar1[1] - (int)(short)puVar1[-1]);
        if (iVar3 != 0) {
          if (iVar4 == -0x80000000 && iVar3 == -1) {
            iVar4 = 0;
          }
          else {
            iVar4 = iVar4 / iVar3;
          }
        }
        uVar2 = puVar1[-1] + (short)iVar4;
        goto LAB_000702fe;
      }
      iVar3 = iVar3 + 1;
    }
    uVar2 = puVar1[-1];
  }
LAB_000702fe:
  *param_3 = uVar2;
  return;
}

void FUN_00070304(ushort *param_1,uint param_2,ushort *param_3)

{
  ushort *puVar1;
  ushort uVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  
  param_2 = param_2 & 0xffff;
  if ((*param_1 == 0xffff) || (param_2 <= *param_1)) {
    uVar2 = param_1[1];
  }
  else {
    iVar3 = 0;
    while( true ) {
      puVar1 = param_1 + iVar3 * 2;
      uVar5 = (uint)*puVar1;
      if (uVar5 == 0xffff) break;
      if (param_2 < uVar5) {
        iVar3 = uVar5 - puVar1[-2];
        iVar4 = (param_2 - puVar1[-2]) * ((uint)puVar1[1] - (uint)puVar1[-1]);
        if (iVar3 != 0) {
          if (iVar4 == -0x80000000 && iVar3 == -1) {
            iVar4 = 0;
          }
          else {
            iVar4 = iVar4 / iVar3;
          }
        }
        uVar2 = puVar1[-1] + (short)iVar4;
        goto LAB_00070352;
      }
      iVar3 = iVar3 + 1;
    }
    uVar2 = puVar1[-1];
  }
LAB_00070352:
  *param_3 = uVar2;
  return;
}

void FUN_00070706(short param_1,short param_2,undefined2 *param_3)

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

uint f33_step_monitor_recovery_scratch
               (uchar classification,F33MonitorRecoveryScratch *scratch,ushort *limit)

{
  ushort uVar1;
  ushort uVar2;
  
  if (classification != '\x11') {
    if ((classification == '\"') || (classification == 'D')) {
      scratch->recovery_count = 0;
    }
    return 0x22;
  }
  uVar1 = scratch->recovery_count;
  uVar2 = *limit;
  if ((uVar1 <= uVar2) && (scratch->recovery_count = uVar1 + 1, (ushort)(uVar1 + 1) <= uVar2)) {
    return 0x44000022;
  }
  scratch->passing_count = 0;
  scratch->opaque_02 = 0;
  scratch->failing_count = 0;
  scratch->opaque_08 = 0;
  scratch->recovery_count = 0;
  scratch->opaque_0c = 0;
  scratch->opaque_10 = 0;
  return 0;
}

undefined4 FUN_00070fa4(char param_1,undefined2 *param_2,ushort *param_3)

{
  ushort uVar1;
  ushort uVar2;
  
  if (param_1 == 'D') {
    param_2[5] = 0;
    param_2[8] = 0;
    return 0x22;
  }
  uVar1 = param_2[8];
  uVar2 = param_3[1];
  if ((uVar2 < uVar1) || (param_2[8] = uVar1 + 1, uVar2 < (ushort)(uVar1 + 1))) {
    return 0x44;
  }
  if (param_1 != '\x11') {
    if (param_1 == '\"') {
      param_2[5] = 0;
    }
    return 0x22;
  }
  uVar1 = param_2[5];
  uVar2 = *param_3;
  if ((uVar1 <= uVar2) && (param_2[5] = uVar1 + 1, (ushort)(uVar1 + 1) <= uVar2)) {
    return 0x44000022;
  }
  *param_2 = 0;
  param_2[1] = 0;
  param_2[2] = 0;
  param_2[4] = 0;
  param_2[5] = 0;
  param_2[6] = 0;
  param_2[8] = 0;
  return 0;
}

undefined4 FUN_00071014(char param_1,undefined2 *param_2,ushort *param_3)

{
  ushort uVar1;
  ushort uVar2;
  
  if (((uintptr_t)(param_2)==(uintptr_t)((undefined2 *)0x0)) || ((uintptr_t)(param_3)==(uintptr_t)((ushort *)0x0))) {
    return 0xffff;
  }
  if (param_1 == 'D') {
    param_2[5] = 0;
    param_2[8] = 0;
  }
  else {
    uVar1 = param_2[8];
    uVar2 = param_3[1];
    if ((uVar2 < uVar1) || (param_2[8] = uVar1 + 1, uVar2 < (ushort)(uVar1 + 1))) {
      return 0x44;
    }
    if (param_1 == '\x11') {
      uVar1 = param_2[5];
      uVar2 = *param_3;
      if ((uVar1 <= uVar2) && (param_2[5] = uVar1 + 1, (ushort)(uVar1 + 1) <= uVar2)) {
        return 0x44000022;
      }
      *param_2 = 0;
      param_2[1] = 0;
      param_2[2] = 0;
      param_2[4] = 0;
      param_2[5] = 0;
      param_2[6] = 0;
      param_2[8] = 0;
      return 0;
    }
  }
  return 0x22;
}

uint f33_nvm_read_logical_result(ushort logical_handle,uchar *output)

{
  *output = f33_nvm_logical_results[logical_handle].result;
  return 0;
}

bool FUN_0007220e(uint *param_1)

{
  bool bVar1;
  
  bVar1 = f33_nvm_scheduler_operation.operation != 0x9da70ae7;
  if (!bVar1) {
    f33_nvm_scheduler_operation.operation = *param_1;
    f33_nvm_scheduler_phase = '\x01';
    f33_nvm_scheduler_operation.logical_handle = (ushort)param_1[1];
    f33_nvm_scheduler_operation.buffer_08 = camry_host_addr((void *)param_1[2]);
    f33_nvm_scheduler_operation.buffer_0c = camry_host_addr((void *)param_1[3]);
  }
  return bVar1;
}

undefined4 FUN_0007282c(uint param_1,ushort param_2,undefined2 *param_3)

{
  uint uVar1;
  
  while( true ) {
    uVar1 = param_1 & 0xffff;
    if ((ushort)(f33_nvm_logical_descriptor_count - 1) < uVar1) {
      return 1;
    }
    if (param_2 == (f33_nvm_logical_descriptors[uVar1].opaque_0a & param_2)) break;
    param_1 = uVar1 + 1;
  }
  *param_3 = (short)param_1;
  return 0;
}

uint f33_nvm_check_queue_empty(F33NvmQueueHeader *header,uchar *empty)

{
  if (header->head == 0xffff) {
    if (header->tail == 0xffff) {
      *empty = '\x01';
      return 0;
    }
  }
  else if (header->tail != 0xffff) {
    *empty = '\0';
    return 0;
  }
  FUN_00072130();
  return 1;
}

void f33_nvm_copy_operation_to_slot(F33NvmQueueSlot *slot,F33NvmOperation *operation)

{
  slot->operation = operation->operation;
  slot->logical_handle = operation->logical_handle;
  slot->read_buffer = operation->buffer_08;
  slot->write_buffer = operation->buffer_0c;
  return;
}

uint f33_nvm_append_operation(ushort queue,ushort index,F33NvmOperation *operation)

{
  uint uVar1;
  
  uVar1 = f33_nvm_append_queue_slot(queue,index);
  if (uVar1 == 0) {
    f33_nvm_queue_slots[index].operation = operation->operation;
    f33_nvm_queue_slots[index].logical_handle = operation->logical_handle;
    f33_nvm_queue_slots[index].read_buffer = operation->buffer_08;
    f33_nvm_queue_slots[index].write_buffer = operation->buffer_0c;
  }
  return uVar1;
}

undefined4 FUN_00073828(ushort *param_1,ushort param_2,ushort *param_3,undefined2 *param_4)

{
  ushort uVar1;
  uint uVar2;
  uint uVar3;
  int iVar4;
  
  uVar1 = *param_1;
  iVar4 = 0x7b;
  uVar3 = 0xffffffff;
  do {
    uVar2 = (uint)uVar1;
    if (uVar2 == 0xffff) {
      return 1;
    }
    if (0x7a < uVar2) {
      FUN_00072130();
      return 1;
    }
    if (param_2 == f33_nvm_queue_slots[uVar2].logical_handle) {
      *param_3 = uVar1;
      *param_4 = (short)uVar3;
      return 0;
    }
    uVar1 = f33_nvm_queue_slots[uVar2].next;
    iVar4 = iVar4 + -1;
    uVar3 = uVar2;
  } while (iVar4 != 0);
  return 1;
}

bool FUN_000739a8(uint *param_1)

{
  bool bVar1;
  
  bVar1 = f33_nvm_zero_handle_operation.operation != 0x9da70ae7;
  if (bVar1) {
    FUN_00072108(3);
  }
  else {
    f33_nvm_zero_handle_operation.operation = *param_1;
    f33_nvm_zero_handle_operation.logical_handle = (ushort)param_1[1];
    f33_nvm_zero_handle_operation.buffer_08 = camry_host_addr((void *)param_1[2]);
    f33_nvm_zero_handle_operation.buffer_0c = camry_host_addr((void *)param_1[3]);
  }
  return bVar1;
}

void f33_nvm_copy_operation(F33NvmOperation *request)

{
  f33_nvm_pending_operation.operation = request->operation;
  f33_nvm_pending_operation.logical_handle = request->logical_handle;
  f33_nvm_pending_operation.buffer_08 = request->buffer_08;
  f33_nvm_pending_operation.buffer_0c = request->buffer_0c;
  return;
}

uint FUN_00073f78(ushort param_1,uchar *param_2)

{
  int iVar1;
  uint uVar2;
  
  uVar2 = 1;
  iVar1 = FUN_0007430c((uint)(ushort)param_1, camry_host_addr(param_2));
  if (iVar1 == 0) {
    uVar2 = f33_nvm_read_logical_result(param_1,param_2);
  }
  return uVar2;
}

uint f33_nvm_check_not_pending(ushort logical_handle,uchar api)

{
  bool bVar1;
  uchar uStack_d;
  
  uStack_d = '\x02';
  f33_nvm_read_logical_result(logical_handle,&uStack_d);
  bVar1 = uStack_d == '\x02';
  if (bVar1) {
    ((void)(0x14), (void)(0), (void)(api), (void)(0x15), f33_return_const_0_71d88());
  }
  return (uint)bVar1;
}

uint f33_nvm_check_buffer_argument(ushort logical_handle,void *buffer,uchar api)

{
  uint uVar1;
  
  uVar1 = 0;
  if ((((uintptr_t)(buffer)==(uintptr_t)((void *)0x0)) &&
      (f33_nvm_logical_descriptors[logical_handle].buffer_mode != '\x04')) &&
     (f33_nvm_logical_descriptors[logical_handle].buffer_mode != '\x02')) {
    ((void)(0x14), (void)(0), (void)(api), (void)(0xd), f33_return_const_0_71d88());
    uVar1 = 1;
  }
  return uVar1;
}

uint f33_nvm_check_read_request(ushort logical_handle,void *buffer)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  
  uVar3 = 1;
  uVar1 = f33_nvm_check_logical_handle(logical_handle,'\x06','\0');
  if (uVar1 == 0) {
    uVar1 = f33_nvm_check_not_pending(logical_handle,'\x06');
    uVar2 = f33_nvm_check_buffer_argument(logical_handle,buffer,'\x06');
    if (uVar1 == 0) {
      if (uVar2 == 0) {
        uVar3 = 0;
      }
      else {
        uVar3 = 1;
      }
    }
  }
  return uVar3;
}

undefined4 FUN_000744de(ushort param_1)

{
  uint uVar1;
  uint uVar2;
  undefined4 uVar3;
  
  uVar3 = 1;
  uVar1 = f33_nvm_check_logical_handle(param_1,'\x16','\0');
  if (uVar1 == 0) {
    uVar1 = f33_nvm_check_not_pending(param_1,'\x16');
    uVar2 = f33_nvm_check_buffer_argument(param_1,(void *)0x0,'\x16');
    if (uVar1 == 0) {
      if (uVar2 == 0) {
        uVar3 = 0;
      }
      else {
        uVar3 = 1;
      }
    }
  }
  return uVar3;
}

void f33_copy_bytes_forward(uchar *destination,uchar *source,uint byte_count)

{
  uint uVar1;
  
  for (uVar1 = 0; uVar1 < byte_count; uVar1 = uVar1 + 1) {
    destination[uVar1] = source[uVar1];
  }
  return;
}

undefined1 FUN_00075b4e(undefined4 *param_1)

{
  char cVar1;
  undefined1 uVar2;
  int iVar3;
  
  cVar1 = DAT_febf6c54 + -1;
  DAT_febf6c54 = cVar1;
  DAT_febf6c3e = FUN_0007543c(DAT_febf6c3e);
  if (cVar1 == '\0') {
    DAT_febf6c53 = 2;
    iVar3 = FUN_00077c64();
    if (iVar3 == 1) {
      uVar2 = 2;
      DAT_febf6c52 = 0;
    }
    else if (iVar3 == 2) {
      uVar2 = 6;
    }
    else {
      *param_1 = camry_host_addr(((undefined *)camry_host_ptr(0xfffbu)));
      uVar2 = 0;
    }
  }
  else {
    uVar2 = 0xe;
    DAT_febf6c40 = DAT_febf6c3e;
  }
  return uVar2;
}

undefined4 FUN_00075d0c(undefined4 param_1,int *param_2)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = FUN_000783d4();
  if (iVar1 == 1) {
    uVar2 = 0x15;
  }
  else {
    *param_2 = iVar1;
    uVar2 = 0;
  }
  return uVar2;
}

undefined4 FUN_00075d4a(undefined4 param_1,int *param_2)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = FUN_000783d4();
  if (iVar1 == 1) {
    uVar2 = 0x16;
  }
  else {
    *param_2 = iVar1;
    uVar2 = 0;
  }
  return uVar2;
}

undefined4 FUN_00075d88(undefined4 param_1,int *param_2)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = FUN_000783d4();
  if (iVar1 == 1) {
    uVar2 = 0x17;
  }
  else {
    *param_2 = iVar1;
    uVar2 = 0;
  }
  return uVar2;
}

undefined4 FUN_00076138(undefined4 *param_1)

{
  uint32_t puVar1;
  uint uVar2;
  int iVar3;
  
  puVar1 = 0x23dfcu;
  DAT_febf6c3e = FUN_0007543c(DAT_febf6c3e);
  uVar2 = FUN_00077c9e();
  if (uVar2 < (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + 0x3b2c))))) {
    DAT_febf6c53 = 2;
    iVar3 = FUN_00077c64();
    if (iVar3 == 1) {
      DAT_febf6c52 = 0;
      return 2;
    }
    if (iVar3 == 2) {
      return 6;
    }
  }
  *param_1 = camry_host_addr(((undefined *)camry_host_ptr(0xfffbu)));
  return 0;
}

undefined2 FUN_0007729c(undefined2 *param_1)

{
  return *param_1;
}

void FUN_000772a2(undefined2 *param_1,undefined2 param_2)

{
  *param_1 = param_2;
  return;
}

uint f33_nvm_header_checksum(F33NvmRecordContext *context)

{
  return (uint)context->checksum16;
}

void f33_nvm_set_read_destination(F33NvmRecordContext *context,uchar *destination)

{
  context->destination_buffer = camry_host_addr(destination);
  return;
}

uint f33_nvm_tail_checksum(F33NvmRecordContext *context)

{
  return context->checksum32;
}

void f33_nvm_bind_record_context(F33NvmCommitContext *context,F33NvmRecordContext *record)

{
  context->record = camry_host_addr(record);
  return;
}

void FUN_00077e22(char *param_1,undefined1 *param_2,undefined1 *param_3)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  *param_2 = 0xd;
  *param_3 = 0xff;
  iVar2 = 0;
  while (((iVar3 = (short)iVar2 * 5, (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x27c84u + (uint32_t)(iVar3) * 1u)))) != *param_1 ||
          ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x27c85u + (uint32_t)(iVar3) * 1u)))) != param_1[1])) || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x27c86u + (uint32_t)(iVar3) * 1u)))) != param_1[2]))) {
    iVar1 = iVar2 + 1;
    iVar3 = iVar2 + -0xb;
    iVar2 = iVar1;
    if (iVar3 < 0 == (iVar1 < 0 && -1 < iVar3)) {
      return;
    }
  }
  *param_2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x27c87u + (uint32_t)(iVar3) * 1u))));
  *param_3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x27c88u + (uint32_t)(iVar3) * 1u))));
  return;
}

uint f33_load_u32(uint *source)

{
  return *source;
}

undefined4 FUN_000793c8(undefined1 *param_1)

{
  undefined1 uVar1;
  
  uVar1 = FUN_000781b4();
  *param_1 = uVar1;
  return 0;
}

undefined4 FUN_00079780(uint param_1,undefined2 *param_2)

{
  int iVar1;
  undefined4 uVar2;
  
  param_1 = param_1 & 0xff;
  uVar2 = 1;
  iVar1 = FUN_00079848((uint)(byte)param_1, camry_host_addr(param_2));
  if ((iVar1 == 0) &&
     (((param_1 - 6 < 3 || (param_1 == 0xc || param_1 == 0xd)) || (param_1 - 0x16 < 3)))) {
    *param_2 = DAT_febf6cbc;
    *(uint *)(param_2 + 2) = f33_nvm_service_diagnostic_mask;
    uVar2 = 0;
  }
  return uVar2;
}

undefined4 FUN_000797c2(char param_1,undefined2 *param_2)

{
  int iVar1;
  undefined4 uVar2;
  
  uVar2 = 1;
  iVar1 = FUN_00079848((uint)(byte)param_1, camry_host_addr(param_2));
  if ((iVar1 == 0) && (param_1 == '\f' || param_1 == '\r')) {
    *param_2 = DAT_febf6cc4;
    *(uint *)(param_2 + 2) = f33_nvm_service_cd_diagnostic_mask;
    uVar2 = 0;
  }
  return uVar2;
}

void f33_cantp_reset_receive_owner(F33CanTpRxState *state)

{
  state->receive_id = 0xffff;
  state->remaining_length = 0;
  state->state = 0xe1;
  state->expected_sequence_number = 0xff;
  state->timeout_ticks = 0;
  state->wait_frame_count = 0;
  state->first_frame_dlc = '\0';
  state->block_remaining = '\0';
  state->flow_status_marker = 0xf0;
  return;
}

void FUN_0007a84c(byte *param_1,ushort param_2)

{
  f33_cantp_rx_flow_parameters_with_complements[*param_1][0] = param_2 | (param_2 ^ 0xff) << 8;
  return;
}

uint FUN_0007a862(byte *param_1)

{
  uint uVar1;
  
  uVar1 = (uint)f33_cantp_rx_flow_parameters_with_complements[*param_1][0];
  if ((uVar1 & 0xff ^ (int)uVar1 >> 8) != 0xff) {
    uVar1 = (uint)param_1[0x16];
    DAT_febe4f3c = 0xf;
    FUN_0007a84c(param_1,uVar1);
  }
  return uVar1 & 0xff;
}

void FUN_0007a89a(byte *param_1,ushort param_2)

{
  f33_cantp_rx_flow_parameters_with_complements[*param_1][1] = param_2 | (param_2 ^ 0xff) << 8;
  return;
}

uint FUN_0007a8b0(byte *param_1)

{
  uint uVar1;
  
  uVar1 = (uint)f33_cantp_rx_flow_parameters_with_complements[*param_1][1];
  if ((uVar1 & 0xff ^ (int)uVar1 >> 8) != 0xff) {
    uVar1 = (uint)param_1[0x17];
    DAT_febe4f3c = 0xf;
    FUN_0007a89a(param_1,uVar1);
  }
  return uVar1 & 0xff;
}

uint f33_cantp_reject_single_frame_extent(F33CanTpRxConnection *connection,F33CanTpFrameInfo *frame)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  
  uVar3 = 1;
  uVar5 = frame->length;
  uVar4 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22b98u + (uint32_t)(connection->addressing_format) * 1u))));
  if (((uVar5 < 9) && (uVar2 = ((uint8_t *)camry_host_ptr((uint32_t)(frame->data)))[uVar4] & 0xf, (((uint8_t *)camry_host_ptr((uint32_t)(frame->data)))[uVar4] & 0xf) != 0)) &&
     (uVar1 = 7 - uVar4,
     (int)(uVar2 - uVar1) < 0 != ((int)uVar1 < 0 && (int)uVar1 < 0 == (int)(uVar2 - uVar1) < 0) ||
     uVar2 == uVar1)) {
    if (connection->require_padded_receive == '\x01') {
      if (uVar5 != 8) {
        return uVar3;
      }
    }
    else if (uVar5 < (uVar2 + uVar4 + 1 & 0xff)) {
      return uVar3;
    }
    uVar3 = 0;
  }
  return uVar3;
}

void f33_cantp_reset_transmit_owner(F33CanTpTxStatePrefix *state)

{
  state->transmit_id = 0xffff;
  state->remaining_or_accepted_length = 0;
  state->state = 0xe1;
  state->timeout_ticks = 0;
  state->sequence_number = 0xff;
  state->block_remaining = '\0';
  state->block_size = '\0';
  state->spacing_ticks = '\0';
  return;
}

uint f33_get_selected_network_software_mode(uchar network,uchar *mode)

{
  ushort uVar1;
  uchar uVar2;
  uint uVar3;
  
  uVar3 = (uint)network - (uint)DAT_00021ba9 & 0xff;
  if (DAT_00021ba8 <= uVar3) {
    return 1;
  }
  uVar1 = ((volatile F33SelectedNetworkModeState *)camry_host_ptr(0xfebe4924u))[uVar3].mode_state;
  if (uVar1 == 0xff) {
    uVar2 = '\0';
  }
  else {
    if (uVar1 != 0x1fe) {
      if (uVar1 == 0x2fd) {
        *mode = '\x02';
        if (((volatile F33SelectedNetworkRecoveryState *)camry_host_ptr(0xfebe491cu))[uVar3].recovery_state != 0x1fe) {
          return 0;
        }
      }
      else if ((((uVar1 != 0x3fc) && (uVar1 != 0x4fb)) && (uVar1 != 0x5fa)) && (uVar1 != 0x8f7)) {
        return 1;
      }
    }
    uVar2 = '\x01';
  }
  *mode = uVar2;
  return 0;
}

void FUN_00089e2c(char param_1,int *param_2)

{
  if (param_1 == '\0') {
    *param_2 = *param_2 + 1;
    return;
  }
  if (param_1 == -0x1f) {
    param_2[1] = param_2[1] + 1;
    return;
  }
  if ((((param_1 != -0x5b) && (param_1 != -0x4c)) && (param_1 != -0x3d)) && (param_1 != -0x2e)) {
    param_2[3] = param_2[3] + 1;
    return;
  }
  param_2[2] = param_2[2] + 1;
  return;
}

undefined1 FUN_0008cfe8(char param_1,undefined1 *param_2,undefined1 *param_3,byte *param_4)

{
  byte bVar1;
  undefined1 uVar2;
  undefined1 uVar3;
  undefined1 uVar4;
  
  bVar1 = *param_4;
  uVar4 = *param_2;
  if (bVar1 < 0xfe) {
    bVar1 = bVar1 + 1;
    uVar2 = *param_3;
    uVar3 = 0;
    if (param_1 == -1) {
      uVar4 = 0x5a;
      uVar3 = uVar4;
    }
  }
  else {
    uVar2 = 0x5a;
    uVar3 = uVar2;
  }
  *param_4 = bVar1;
  *param_2 = uVar4;
  *param_3 = uVar2;
  return uVar3;
}

uint f33_admit_application_communication_request
               (uchar subfunction,uchar communication_type,ushort node,uchar *nrc)

{
  uint uVar1;
  byte bVar2;
  
  bVar2 = f33_dcm_communication_local_state.retained_subnet;
  if (f33_dcm_communication_local_state.action_state == '\0') {
    bVar2 = communication_type >> 4;
    uVar1 = f33_communication_request_sample_above_limit();
    f33_dcm_communication_local_state.action_state = uVar1 != 1;
    if ((bool)f33_dcm_communication_local_state.action_state) {
      uVar1 = 0;
      goto LAB_0008da52;
    }
  }
  uVar1 = 1;
  *nrc = '\"';
LAB_0008da52:
  f33_dcm_communication_local_state.admission_result = (uchar)uVar1;
  f33_dcm_communication_local_state.retained_subnet = bVar2;
  return uVar1;
}

undefined4 FUN_0008e672(undefined1 param_1,undefined4 *param_2)

{
  undefined4 *puVar1;
  undefined4 uVar2;
  undefined4 *puVar3;
  
  puVar3 = ((undefined *)camry_host_ptr(0xfebe52bcu));
  puVar1 = param_2;
  do {
    uVar2 = *puVar1;
    puVar1 = puVar1 + 1;
    *puVar3 = uVar2;
    puVar3 = puVar3 + 1;
  } while ((uintptr_t)(param_2 + 7)!=(uintptr_t)(puVar1));
  DAT_febe52ac = *param_2;
  DAT_febe52b0 = param_2[1];
  DAT_febe52b4 = param_2[2];
  DAT_febe52b8 = param_2[3];
  ((void)(param_1), (void)(((undefined *)camry_host_ptr(0xfebe52acu))), f33_return_only_stub_4d4c2());
  return 0;
}

undefined2 FUN_0008e912(short param_1,ushort param_2,undefined4 *param_3,undefined4 *param_4)

{
  undefined2 uVar1;
  
  uVar1 = 1;
  if ((param_1 == 0) && (param_2 == 0)) {
    *param_3 = DAT_00025954;
    *param_4 = DAT_00025958;
    uVar1 = 0;
  }
  if ((param_1 == 1) && (param_2 < 3)) {
    uVar1 = 0;
    *param_3 = *(undefined4 *)(((undefined *)camry_host_ptr(0x2586cu)) + (short)param_2 * 0x50);
    *param_4 = *(undefined4 *)(((undefined *)camry_host_ptr(0x25870u)) + (short)param_2 * 0x50);
  }
  return uVar1;
}

undefined2 FUN_0008e954(short param_1,ushort *param_2)

{
  undefined2 uVar1;
  
  uVar1 = 1;
  if (param_1 == 0) {
    if (f33_secoc_tx_queue_head_pair[0] == (ushort)~f33_secoc_tx_queue_head_pair[1]) {
      *param_2 = f33_secoc_tx_queue_head_pair[0];
      uVar1 = 0;
    }
    else {
      DAT_febe5468 = 0xa5;
    }
  }
  if (param_1 == 1) {
    if (DAT_febe5464 == (ushort)~DAT_febe5466) {
      *param_2 = DAT_febe5464;
      return 0;
    }
    DAT_febe5468 = 0xa5;
  }
  return uVar1;
}

undefined4 FUN_0008f2b0(short param_1,char param_2,ushort *param_3)

{
  ushort uVar1;
  
  if ((uintptr_t)(param_3)!=(uintptr_t)((ushort *)0x0)) {
    uVar1 = 0;
    if (param_2 == '\0') {
      while (param_1 != (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x2587cu + (uint32_t)((short)uVar1 * 0x28) * 2u))))) {
        uVar1 = uVar1 + 1;
        if (2 < uVar1) {
          return 1;
        }
      }
LAB_0008f2ec:
      *param_3 = uVar1;
      return 0;
    }
    if (param_2 == '\x01') {
      uVar1 = 0;
      do {
        if (param_1 == (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x2587eu + (uint32_t)((short)uVar1 * 0x28) * 2u))))) goto LAB_0008f2ec;
        uVar1 = uVar1 + 1;
      } while (uVar1 < 3);
    }
  }
  return 1;
}

undefined4 FUN_0008fa5a(short param_1,char param_2,undefined2 *param_3)

{
  short sVar1;
  undefined4 uVar2;
  
  uVar2 = 1;
  if ((uintptr_t)(param_3)!=(uintptr_t)((undefined2 *)0x0)) {
    sVar1 = DAT_00025964;
    if (((param_2 != '\0') && (sVar1 = DAT_00025966, param_2 != '\x01')) || (param_1 != sVar1)) {
      return uVar2;
    }
    *param_3 = 0;
    uVar2 = 0;
  }
  return uVar2;
}

undefined4 FUN_0009022a(short param_1,undefined2 *param_2)

{
  undefined4 uVar1;
  
  uVar1 = 0;
  if ((DAT_0002583e == 0) && (param_1 == DAT_0002583c)) {
    *param_2 = 0;
    uVar1 = 1;
    param_2[1] = 0;
  }
  return uVar1;
}

undefined4 FUN_000902b0(short param_1,undefined2 *param_2)

{
  undefined4 uVar1;
  undefined1 auStack_c [2];
  undefined2 uStack_a;
  
  uVar1 = 0;
  if ((DAT_0002583e == 0) && (param_1 == DAT_00025946)) {
    FUN_0009022a(DAT_0002583c,auStack_c);
    param_2[1] = 0;
    uVar1 = 1;
    *param_2 = uStack_a;
  }
  return uVar1;
}

void FUN_000906a4(undefined4 *param_1,undefined1 *param_2,uint *param_3)

{
  uint uVar1;
  
  if ((byte)*param_3 < (*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb))))) {
    uVar1 = 0;
  }
  else {
    *param_2 = (char)((uint)*param_1 >> 8);
    param_2[1] = (char)*param_1;
    param_2[2] = (char)((uint)param_1[1] >> 0xc);
    param_2[3] = (char)((uint)param_1[1] >> 4);
    param_2[4] = (char)(param_1[1] << 4);
    uVar1 = (uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb))));
  }
  *param_3 = uVar1;
  return;
}

void FUN_00090836(undefined1 *param_1,int param_2,uint *param_3)

{
  undefined1 uVar1;
  uint uVar2;
  
  if (param_2 == 0x24) {
    *param_3 = (uint)CONCAT11(*param_1,param_1[1]);
    uVar2 = (uint)((byte)param_1[4] >> 4) |
            (uint)(byte)param_1[3] << 4 | (uint)(byte)param_1[2] << 0xc;
    uVar1 = 0x24;
  }
  else {
    *param_3 = 0;
    uVar2 = 0;
    uVar1 = 0;
  }
  param_3[1] = uVar2;
  *(undefined2 *)(param_3 + 2) = 0;
  (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 10)))) = 0;
  (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0xb)))) = uVar1;
  return;
}

undefined1 FUN_00091694(undefined1 *param_1)

{
  return *param_1;
}

bool FUN_000916c6(char param_1,undefined4 *param_2)

{
  bool bVar1;
  
  bVar1 = false;
  if (((param_1 == '\x01') && (*(short *)(param_2 + 1) == 2)) && (*(char *)*param_2 == '>')) {
    bVar1 = ((char *)*param_2)[1] == -0x80;
  }
  return bVar1;
}

void FUN_00092064(uchar param_1,ushort *param_2,ushort *param_3,ushort *param_4)

{
  int iVar1;
  int iVar2;
  short sVar3;
  int iVar4;
  
  iVar4 = 0;
  do {
    sVar3 = (short)iVar4;
    if (f33_app_session_timing_rows[sVar3].session == param_1) {
      *param_2 = f33_app_session_timing_rows[sVar3].response_timing_a_raw;
      *param_3 = f33_app_session_timing_rows[sVar3].transport_timing_b_raw;
      *param_4 = f33_app_session_timing_rows[sVar3].transport_timing_c_raw;
      return;
    }
    iVar2 = iVar4 + 1;
    iVar1 = iVar4 + -3;
    iVar4 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  return;
}

void FUN_00093b32(short param_1,ushort *param_2,ushort *param_3,ushort *param_4)

{
  *param_2 = f33_dcm_receive_route[param_1].protocol_index;
  *param_3 = f33_dcm_receive_route[param_1].connection_index;
  *param_4 = f33_dcm_receive_route[param_1].receive_descriptor_index;
  return;
}

void FUN_00093c6c(uint param_1,undefined4 *param_2)

{
  uchar *puVar1;
  
  param_1 = param_1 & 0xffff;
  puVar1 = ((void *)camry_host_ptr((uint32_t)(f33_dcm_receive_buffer_configuration[param_1].base)));
  f33_dcm_receive_buffer_state[param_1].write_cursor = camry_host_addr(puVar1);
  *param_2 = camry_host_addr(puVar1);
  *(ushort *)(param_2 + 1) = f33_dcm_receive_buffer_state[param_1].received_length;
  return;
}

void FUN_00093cce(short param_1,ushort *param_2,ushort *param_3)

{
  *param_2 = f33_dcm_receive_route[param_1].protocol_index;
  *param_3 = f33_dcm_receive_route[param_1].connection_index;
  return;
}

undefined4 FUN_0009456e(byte param_1,uint param_2,short param_3,undefined1 *param_4)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = (param_2 & 0xff) - 1;
  uVar2 = 0;
  if (((int)((uint)param_1 - iVar1) < 0 !=
       (iVar1 < 0 && iVar1 < 0 == (int)((uint)param_1 - iVar1) < 0)) && (param_3 == 0)) {
    DAT_febe5d20 = param_1 + 1;
    uVar2 = 10;
    *param_4 = 1;
  }
  return uVar2;
}

undefined4 FUN_00094f6a(undefined2 param_1,undefined1 *param_2,undefined4 param_3)

{
  undefined2 *extraout_r8;
  int iVar1;
  undefined4 uVar2;
  
  *param_2 = 0;
  uVar2 = 1;
  iVar1 = FUN_00094d9c(param_1, ((undefined2 *)camry_host_ptr((uint32_t)(param_3))));
  if (iVar1 == 0) {
    uVar2 = FUN_00095514(*extraout_r8,param_2);
  }
  return uVar2;
}

undefined4 FUN_00095262(undefined4 param_1,byte param_2,ushort *param_3)

{
  if (param_2 < 2) {
    f33_dcm_selected_did_payload_length(param_3);
  }
  return 0;
}

undefined4 FUN_00095278(undefined4 param_1,byte param_2,ushort *param_3)

{
  if (param_2 < 2) {
    f33_dcm_selected_did_payload_length(param_3);
  }
  return 0;
}

undefined4 FUN_0009528e(undefined4 param_1,byte param_2,ushort *param_3)

{
  if (param_2 < 2) {
    f33_dcm_selected_did_payload_length(param_3);
  }
  return 0;
}

undefined4 FUN_000952a4(undefined4 param_1,byte param_2,ushort *param_3)

{
  if (param_2 < 2) {
    f33_dcm_selected_did_payload_length(param_3);
  }
  return 0;
}

undefined4 FUN_000952ba(undefined4 param_1,byte param_2,ushort *param_3)

{
  if (param_2 < 2) {
    f33_dcm_selected_did_payload_length(param_3);
  }
  return 0;
}

uint f33_dcm_check_communication_application_admission
               (uchar subfunction,uchar communication_type,ushort node,uchar *nrc)

{
  uint uVar1;
  
  uVar1 = f33_admit_application_communication_request(subfunction,communication_type,node,nrc);
  return uVar1;
}

bool FUN_00097172(ushort param_1,undefined2 *param_2)

{
  ushort uVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  
  if (DAT_00026492 != 0) {
    uVar4 = 0;
    uVar3 = (uint)(ushort)(DAT_00026492 - 1);
    if ((DAT_00026918 <= param_1) && (uVar1 = DAT_00026918, param_1 <= (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x26918u + (uint32_t)(uVar3 * 4) * 2u))))))
    {
      while( true ) {
        if (uVar1 == param_1) {
          *param_2 = (short)uVar4;
          return (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2691bu + (uint32_t)(uVar4 * 8) * 1u)))) != '\x01';
        }
        if (uVar3 <= uVar4) break;
        uVar2 = uVar3 + uVar4 >> 1;
        if ((*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x26918u + (uint32_t)(uVar2 * 4) * 2u)))) < param_1) {
          uVar4 = uVar2 + 1 & 0xffff;
          uVar2 = uVar3;
        }
        uVar3 = uVar2;
        uVar1 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x26918u + (uint32_t)(uVar4 * 4) * 2u))));
      }
    }
  }
  return true;
}

void FUN_00099004(undefined4 param_1,undefined1 *param_2)

{
  param_2[1] = (char)((uint)param_1 >> 8);
  *param_2 = (char)param_1;
  param_2[2] = (char)((uint)param_1 >> 0x10);
  param_2[3] = (char)((uint)param_1 >> 0x18);
  return;
}

void FUN_000991b6(undefined4 *param_1,undefined4 *param_2)

{
  *param_2 = *param_1;
  return;
}

undefined4 FUN_000b5a98(uint param_1,undefined1 *param_2)

{
  uint uVar1;
  uint32_t puVar2;
  undefined1 *extraout_r7;
  int iVar3;
  undefined4 uVar4;
  undefined1 uVar5;
  uint uVar6;
  
  puVar2 = 0xfebeb800u;
  uVar6 = DAT_febeb288 &
          DAT_febeb284 & DAT_febeb280 & DAT_febeb27c & DAT_febeb278 & DAT_febeb274 & DAT_febeb270;
  param_1 = param_1 & uVar6;
  if (param_1 != 0) {
    uVar5 = 0;
    uVar1 = 0;
    do {
      if ((param_1 >> (uVar1 & 0x1f) & 1) != 0) {
        DAT_febeb258 = (undefined1)uVar1;
        uVar5 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xaeb98u + (uint32_t)(uVar1) * 1u))));
      }
      uVar1 = uVar1 + 1;
    } while (uVar1 < 0xd);
    puVar2 = 0xfebeb800u;
    iVar3 = FUN_000b5a74(uVar5);
    param_2 = extraout_r7;
    if (iVar3 == 1) {
      uVar4 = 0;
      goto LAB_000b5af2;
    }
  }
  uVar5 = 0;
  uVar4 = 0x5a;
LAB_000b5af2:
  *param_2 = uVar5;
  (*((uint *)camry_host_ptr((uint32_t)(puVar2 + -0x574)))) = uVar6;
  return uVar4;
}

void FUN_000b73a0(ushort param_1,ushort *param_2,ushort *param_3)

{
  if (*param_2 < param_1) {
    *param_2 = param_1;
  }
  if (param_1 < *param_3) {
    *param_3 = param_1;
  }
  return;
}

uint f33_select_service_kind2_sample(short *sample)

{
  short sVar1;
  uint uVar2;
  
  if (DAT_febeb3cc == '\n') {
    uVar2 = 0x5a;
    sVar1 = DAT_febeb3a6;
  }
  else {
    uVar2 = 0;
    sVar1 = 0;
  }
  *sample = sVar1;
  return uVar2;
}

void FUN_000bbaa4(char *param_1,int *param_2,short *param_3)

{
  short sVar1;
  int iVar3;
  char cVar4;
  int iVar5;
  int iVar2;
  
  cVar4 = *param_1;
  if (cVar4 == '\x11') {
    iVar5 = *param_2 - (int)*param_3;
    iVar2 = iVar5;
    if (DAT_000aee50 != 0) {
      if (iVar5 == -0x80000000 && DAT_000aee50 == -1) {
        iVar2 = 0;
      }
      else {
        iVar2 = iVar5 / DAT_000aee50;
      }
    }
    iVar3 = (int)DAT_000aee40;
    sVar1 = (short)iVar2;
    iVar2 = (int)sVar1;
    if (iVar2 - iVar3 < 0 != (iVar2 < 0 != iVar3 < 0 && iVar3 < 0 == iVar2 - iVar3 < 0) ||
        iVar2 == iVar3) {
      iVar5 = 0;
      sVar1 = 0;
      cVar4 = '\"';
    }
  }
  else {
    iVar5 = 0;
    sVar1 = 0;
  }
  *param_1 = cVar4;
  *param_2 = iVar5;
  *param_3 = sVar1;
  return;
}

void FUN_000be216(undefined1 *param_1)

{
  short sVar1;
  undefined1 uVar2;
  undefined2 uVar3;
  
  sVar1 = DAT_febeaf40;
  param_1[3] = DAT_febebe60;
  param_1[4] = DAT_febebe62;
  *(ushort *)(param_1 + 8) = f33_received_retained_word;
  *(uint *)(param_1 + 0x10) = f33_received_word_unchanged_age;
  *(uint *)(param_1 + 0x14) = f33_received_typed_scalar;
  param_1[0x18] = f33_received_packed_decimal_fields[0];
  param_1[0x19] = f33_received_packed_decimal_fields[1];
  param_1[0x1a] = f33_received_packed_decimal_fields[2];
  param_1[0x1b] = f33_received_packed_decimal_fields[3];
  param_1[0x1c] = f33_received_packed_decimal_fields[4];
  param_1[0x1d] = f33_received_packed_decimal_fields[5];
  *(undefined2 *)(param_1 + 10) = DAT_febebee2;
  uVar3 = DAT_febebe82;
  *(short *)(param_1 + 0xe) = sVar1;
  *(undefined2 *)(param_1 + 6) = 0;
  *(undefined2 *)(param_1 + 0x1e) = 0;
  *(undefined2 *)(param_1 + 0xc) = uVar3;
  *param_1 = DAT_febebe78;
  uVar2 = DAT_febeb1c4;
  param_1[2] = 0 < sVar1;
  param_1[5] = 0;
  param_1[1] = uVar2;
  return;
}

void FUN_000be28e(undefined1 *param_1)

{
  short sVar1;
  undefined1 uVar2;
  undefined2 uVar3;
  
  sVar1 = DAT_febeafd0;
  param_1[3] = DAT_febebe60;
  param_1[4] = DAT_febebe62;
  *(ushort *)(param_1 + 8) = f33_received_retained_word;
  *(uint *)(param_1 + 0x10) = f33_received_word_unchanged_age;
  *(uint *)(param_1 + 0x14) = f33_received_typed_scalar;
  param_1[0x18] = f33_received_packed_decimal_fields[0];
  param_1[0x19] = f33_received_packed_decimal_fields[1];
  param_1[0x1a] = f33_received_packed_decimal_fields[2];
  param_1[0x1b] = f33_received_packed_decimal_fields[3];
  param_1[0x1c] = f33_received_packed_decimal_fields[4];
  param_1[0x1d] = f33_received_packed_decimal_fields[5];
  *(undefined2 *)(param_1 + 10) = DAT_febebee2;
  uVar3 = DAT_febebe82;
  *(short *)(param_1 + 0xe) = sVar1;
  *(undefined2 *)(param_1 + 6) = 0;
  *(undefined2 *)(param_1 + 0x1e) = 0;
  *(undefined2 *)(param_1 + 0xc) = uVar3;
  *param_1 = DAT_febebe78;
  uVar2 = DAT_febeb1c4;
  param_1[2] = 0 < sVar1;
  param_1[5] = 0;
  param_1[1] = uVar2;
  return;
}

void f33_qualify_record8_admitted_observations
               (uchar *result,uchar *completed,ushort *zero_count,ushort *nonzero_count)

{
  ushort uVar1;
  ushort uVar2;
  
  uVar2 = DAT_000af430;
  uVar1 = DAT_000af42e;
  if (DAT_000af42e <= *zero_count) {
    *completed = 'Z';
    *result = DAT_febeaced;
    *zero_count = uVar1;
    return;
  }
  if (DAT_000af430 <= *nonzero_count) {
    *completed = 'Z';
    *result = '\0';
    *nonzero_count = uVar2;
  }
  return;
}

void f33_accept_consistent_estimator_center(uchar *snapshot)

{
  ushort uVar1;
  
  DAT_febec0a6 = 0;
  DAT_febec0a8 = 0;
  DAT_febec0aa = 0;
  uVar1 = DAT_febec0a4 + 1;
  if (DAT_000af7e8 <= (ushort)(DAT_febec0a4 + 1)) {
    DAT_febec0b6 = 0x5a;
    DAT_febec0b7 = snapshot[8];
    DAT_febec0b4 = *(undefined2 *)(snapshot + 0x10);
    DAT_febeaba8 = *(undefined4 *)(snapshot + 0x2c);
    uVar1 = DAT_000af7e8;
    DAT_febec0b0 = DAT_febeaba8;
  }
  DAT_febec0a4 = uVar1;
  return;
}

void f33_request_secondary_estimator_reseed(uchar *snapshot)

{
  ushort uVar1;
  
  DAT_febec0a4 = 0;
  DAT_febec0a8 = 0;
  DAT_febec0aa = 0;
  uVar1 = DAT_febec0a6 + 1;
  if (DAT_000af7ea <= (ushort)(DAT_febec0a6 + 1)) {
    DAT_febec0b7 = snapshot[9];
    DAT_febec0b4 = *(undefined2 *)(snapshot + 0x12);
    DAT_febec091 = 0x5a;
    uVar1 = DAT_000af7ea;
  }
  DAT_febec0a6 = uVar1;
  return;
}

void f33_accept_unqualified_estimator_center(uchar *snapshot)

{
  ushort uVar1;
  
  DAT_febec0a4 = 0;
  DAT_febec0a6 = 0;
  DAT_febec0a8 = 0;
  uVar1 = DAT_febec0aa + 1;
  if (DAT_000af7ee <= (ushort)(DAT_febec0aa + 1)) {
    DAT_febec0b7 = snapshot[8];
    DAT_febec0b6 = 0;
    DAT_febeaba8 = *(undefined4 *)(snapshot + 0x2c);
    DAT_febec0b4 = *(undefined2 *)(snapshot + 0x10);
    uVar1 = DAT_000af7ee;
  }
  DAT_febec0aa = uVar1;
  return;
}

void f33_qualify_secondary_estimator_change(int change,uchar *count,uchar *qualified)

{
  int iVar1;
  byte bVar2;
  uchar uVar3;
  
  iVar1 = (int)(DAT_000af804 * (uint)DAT_febeae38) / 0x400;
  if (change - iVar1 < 0 == (change < 0 != iVar1 < 0 && iVar1 < 0 == change - iVar1 < 0)) {
    uVar3 = '\0';
    bVar2 = 0;
  }
  else {
    bVar2 = *count;
    uVar3 = *qualified;
    if ((DAT_000af808 <= bVar2) || (bVar2 = bVar2 + 1, DAT_000af808 <= bVar2)) {
      uVar3 = 'Z';
    }
  }
  *qualified = uVar3;
  *count = bVar2;
  return;
}

void f33_prepare_torque_memory_gain_parameters(F33GainSlewState *state,uint mode)

{
  int iVar1;
  ushort uVar2;
  uchar uVar3;
  ushort uVar4;
  ushort uVar5;
  ushort uVar6;
  
  if ((mode & 0xff) < 7) {
    uVar3 = '\x02';
    iVar1 = (short)(DAT_febeac3c & 1) * 7 + (mode & 0xff);
    uVar2 = f33_torque_memory_gain_calibrations[iVar1].up_target;
    uVar6 = *((uint16_t *)camry_host_ptr((uint32_t)(f33_torque_memory_gain_calibrations[iVar1].down_step)));
    uVar5 = *((uint16_t *)camry_host_ptr((uint32_t)(f33_torque_memory_gain_calibrations[iVar1].up_step)));
    uVar4 = *((uint16_t *)camry_host_ptr((uint32_t)(f33_torque_memory_gain_calibrations[iVar1].down_target)));
  }
  else {
    uVar3 = '\x01';
    uVar2 = DAT_febec12c;
    uVar6 = DAT_febec130;
    uVar5 = DAT_febec132;
    uVar4 = DAT_febec12e;
  }
  state->down_step = uVar6;
  state->up_step = uVar5;
  state->down_target = uVar4;
  state->up_target = uVar2;
  state->direction = uVar3;
  return;
}

void f33_prepare_gain_parameters_c2a4(F33GainSlewState *state,uint mode)

{
  int iVar1;
  ushort uVar2;
  uchar uVar3;
  ushort uVar4;
  ushort uVar5;
  ushort uVar6;
  
  if ((mode & 0xff) < 7) {
    uVar3 = '\x02';
    iVar1 = (short)(DAT_febeac3c & 1) * 7 + (mode & 0xff);
    uVar2 = *(ushort *)(((undefined *)camry_host_ptr(0xd3130u)) + iVar1 * 0x10);
    uVar6 = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd312cu + (uint32_t)(iVar1 * 4) * 4u)))))));
    uVar5 = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3134u + (uint32_t)(iVar1 * 4) * 4u)))))));
    uVar4 = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3128u + (uint32_t)(iVar1 * 4) * 4u)))))));
  }
  else {
    uVar3 = '\x01';
    uVar2 = DAT_febec29c;
    uVar6 = DAT_febec2a0;
    uVar5 = DAT_febec2a2;
    uVar4 = DAT_febec29e;
  }
  state->down_step = uVar6;
  state->up_step = uVar5;
  state->down_target = uVar4;
  state->up_target = uVar2;
  state->direction = uVar3;
  return;
}

void f33_prepare_gain_parameters_c2f4(F33GainSlewState *state,uint mode)

{
  int iVar1;
  ushort uVar2;
  uchar uVar3;
  ushort uVar4;
  ushort uVar5;
  ushort uVar6;
  
  if ((mode & 0xff) < 7) {
    uVar3 = '\x02';
    iVar1 = (short)(DAT_febeac3c & 1) * 7 + (mode & 0xff);
    uVar2 = *(ushort *)(((undefined *)camry_host_ptr(0xd3210u)) + iVar1 * 0x10);
    uVar6 = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd320cu + (uint32_t)(iVar1 * 4) * 4u)))))));
    uVar5 = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3214u + (uint32_t)(iVar1 * 4) * 4u)))))));
    uVar4 = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3208u + (uint32_t)(iVar1 * 4) * 4u)))))));
  }
  else {
    uVar3 = '\x01';
    uVar2 = DAT_febec2ec;
    uVar6 = DAT_febec2f0;
    uVar5 = DAT_febec2f2;
    uVar4 = DAT_febec2ee;
  }
  state->down_step = uVar6;
  state->up_step = uVar5;
  state->down_target = uVar4;
  state->up_target = uVar2;
  state->direction = uVar3;
  return;
}

void f33_prepare_gain_parameters_c544(F33GainSlewState *state,uint mode)

{
  int iVar1;
  ushort uVar2;
  uchar uVar3;
  ushort uVar4;
  ushort uVar5;
  ushort uVar6;
  
  if ((mode & 0xff) < 7) {
    uVar3 = '\x02';
    iVar1 = (short)(DAT_febeac3c & 1) * 7 + (mode & 0xff);
    uVar2 = *(ushort *)(((undefined *)camry_host_ptr(0xd3858u)) + iVar1 * 0x10);
    uVar6 = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3854u + (uint32_t)(iVar1 * 4) * 4u)))))));
    uVar5 = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd385cu + (uint32_t)(iVar1 * 4) * 4u)))))));
    uVar4 = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3850u + (uint32_t)(iVar1 * 4) * 4u)))))));
  }
  else {
    uVar3 = '\x01';
    uVar2 = DAT_febec53c;
    uVar6 = DAT_febec540;
    uVar5 = DAT_febec542;
    uVar4 = DAT_febec53e;
  }
  state->down_step = uVar6;
  state->up_step = uVar5;
  state->down_target = uVar4;
  state->up_target = uVar2;
  state->direction = uVar3;
  return;
}

void FUN_000d097a(ushort *param_1,uint param_2,undefined2 *param_3,undefined2 *param_4)

{
  int iVar1;
  ushort *puVar2;
  int iVar3;
  int iVar4;
  
  param_2 = param_2 & 0xffff;
  iVar3 = 0;
  if (*param_1 < param_2) {
    for (; (puVar2 = param_1 + iVar3, puVar2[1] < param_2 && (puVar2[1] != 0xffff));
        iVar3 = (int)(short)((short)iVar3 + 1)) {
    }
    iVar4 = 0x400;
    if (puVar2[1] == 0xffff) {
      iVar3 = iVar3 + -1;
    }
    else if (puVar2[1] != *puVar2) {
      iVar4 = (param_2 - *puVar2) * 0x400;
      iVar1 = (uint)puVar2[1] - (uint)*puVar2;
      if (iVar1 != 0) {
        if (iVar4 == -0x80000000 && iVar1 == -1) {
          iVar4 = 0;
        }
        else {
          iVar4 = iVar4 / iVar1;
        }
      }
    }
  }
  else {
    iVar4 = 0;
  }
  *param_3 = (short)iVar3;
  *param_4 = (short)iVar4;
  return;
}

void FUN_000d0a06(int param_1,int param_2,int *param_3)

{
  int iVar1;
  
  if (param_1 < 1) {
    if ((param_2 < 1) &&
       (iVar1 = -0x7fffffff - param_1,
       iVar1 - param_2 < 0 == (iVar1 < 0 != param_2 < 0 && param_2 < 0 == iVar1 - param_2 < 0) &&
       iVar1 != param_2)) {
      param_2 = -0x7fffffff;
      goto LAB_000d0a3a;
    }
  }
  else if ((0 < param_2) &&
          (iVar1 = (0x7fffffff - param_1) - param_2,
          iVar1 < 0 != (0x7fffffff - param_1 < 0 != param_2 < 0 && param_2 < 0 == iVar1 < 0))) {
    param_2 = 0x7fffffff;
    goto LAB_000d0a3a;
  }
  param_2 = param_2 + param_1;
LAB_000d0a3a:
  *param_3 = param_2;
  return;
}

void FUN_000d11d6(undefined4 param_1,undefined4 param_2,undefined1 *param_3)

{
  *param_3 = (char)((uint)param_1 >> 8);
  param_3[1] = (char)param_1;
  param_3[2] = (char)((uint)param_2 >> 8);
  param_3[3] = (char)param_2;
  return;
}

void FUN_000d1232(short param_1,uint param_2,uint param_3,short *param_4)

{
  int iVar1;
  int iVar2;
  
  param_3 = param_3 & 0xffff;
  if (((param_2 & 0xffff) != 0) && (param_3 != 0)) {
    iVar2 = (int)param_1 * (param_2 & 0xffff);
    if (param_3 != 0) {
      if (iVar2 == -0x80000000 && param_3 == 0xffffffff) {
        iVar2 = -0x80000000;
      }
      else {
        iVar2 = iVar2 / (int)param_3;
      }
    }
    if (iVar2 + 0x7fff < 0 == (-1 < iVar2 && iVar2 + 0x7fff < 0) && iVar2 != -0x7fff) {
      iVar1 = 0x7fff;
      if ((iVar2 + -0x7fff < 0 != (iVar2 < 0 && -1 < iVar2 + -0x7fff) || iVar2 == 0x7fff) &&
         (iVar1 = iVar2,
         iVar2 + 0x8000 < 0 != (-1 < iVar2 && iVar2 + 0x8000 < 0) || iVar2 == -0x8000)) {
        iVar1 = -0x8000;
      }
      param_1 = (short)iVar1;
    }
    else {
      param_1 = -0x7fff;
    }
  }
  *param_4 = param_1;
  return;
}

void f33_filter_unsigned_sample_accumulator
               (ushort *sample,uint coefficient,ushort *output,uint *accumulator)

{
  uint uVar1;
  
  if (0xfffe < coefficient - 1) {
    coefficient = 0x10000;
  }
  uVar1 = sample[1] * coefficient + (*(int *)(sample + 2) - *sample * coefficient);
  *output = (ushort)(uVar1 >> 0x10);
  *accumulator = uVar1;
  return;
}

void FUN_000d1cdc(short param_1,short param_2,short param_3,short *param_4)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar1 = (int)param_1;
  iVar2 = (int)param_2;
  iVar3 = (int)param_3;
  if (iVar2 - iVar1 < 0 != (iVar2 < 0 != iVar1 < 0 && iVar1 < 0 == iVar2 - iVar1 < 0)) {
    iVar1 = iVar2;
  }
  if (iVar3 - iVar1 < 0 != (iVar3 < 0 != iVar1 < 0 && iVar1 < 0 == iVar3 - iVar1 < 0) ||
      iVar3 == iVar1) {
    param_3 = (short)iVar1;
  }
  *param_4 = param_3;
  return;
}

void f33_store_signed_halfword_max(short value,short bound,short *output)

{
  int iVar1;
  int iVar2;
  
  iVar1 = (int)value;
  iVar2 = (int)bound;
  if (iVar2 - iVar1 < 0 == (iVar2 < 0 != iVar1 < 0 && iVar1 < 0 == iVar2 - iVar1 < 0) &&
      iVar2 != iVar1) {
    value = bound;
  }
  *output = value;
  return;
}

void FUN_000d1d1c(ushort *param_1,undefined2 *param_2)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  
  uVar3 = (uint)*param_1;
  uVar1 = (uint)param_1[1] - (uint)param_1[3];
  uVar2 = (uint)param_1[2] + (uint)param_1[1];
  if (((int)(uVar3 - uVar2) < 0 || uVar3 == uVar2) &&
     (uVar2 = uVar3,
     (int)(uVar1 - uVar3) < 0 == ((int)uVar1 < 0 && -1 < (int)(uVar1 - uVar3)) && uVar1 != uVar3)) {
    uVar2 = uVar1;
  }
  *param_2 = (short)uVar2;
  return;
}

void f33_store_signed_halfword_min(short value,short bound,short *output)

{
  int iVar1;
  int iVar2;
  
  iVar2 = (int)value;
  iVar1 = bound - iVar2;
  if (iVar1 < 0 != (bound < 0 != iVar2 < 0 && iVar2 < 0 == iVar1 < 0)) {
    value = bound;
  }
  *output = value;
  return;
}

void FUN_000d1d4e(int param_1,int param_2,int *param_3)

{
  if (param_2 - param_1 < 0 != (param_2 < 0 != param_1 < 0 && param_1 < 0 == param_2 - param_1 < 0))
  {
    param_1 = param_2;
  }
  *param_3 = param_1;
  return;
}

void FUN_000d1d5c(ushort param_1,ushort param_2,ushort *param_3)

{
  if (param_2 < param_1) {
    param_1 = param_2;
  }
  *param_3 = param_1;
  return;
}

void FUN_000d1d6e(uint param_1,uint param_2,uint *param_3)

{
  if (param_2 < param_1) {
    param_1 = param_2;
  }
  *param_3 = param_1;
  return;
}

void FUN_000d1ee0(ushort *param_1,uint param_2,ushort *param_3)

{
  ushort *puVar1;
  ushort uVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  
  param_2 = param_2 & 0xffff;
  if ((*param_1 == 0xffff) || (param_2 <= *param_1)) {
    uVar2 = param_1[1];
  }
  else {
    iVar3 = 0;
    while( true ) {
      puVar1 = param_1 + iVar3 * 2;
      uVar5 = (uint)*puVar1;
      if (uVar5 == 0xffff) break;
      if (param_2 < uVar5) {
        iVar3 = uVar5 - puVar1[-2];
        iVar4 = (param_2 - puVar1[-2]) * ((uint)puVar1[1] - (uint)puVar1[-1]);
        if (iVar3 != 0) {
          if (iVar4 == -0x80000000 && iVar3 == -1) {
            iVar4 = 0;
          }
          else {
            iVar4 = iVar4 / iVar3;
          }
        }
        uVar2 = puVar1[-1] + (short)iVar4;
        goto LAB_000d1f2e;
      }
      iVar3 = iVar3 + 1;
    }
    uVar2 = puVar1[-1];
  }
LAB_000d1f2e:
  *param_3 = uVar2;
  return;
}

void FUN_000d2388(short param_1,short param_2,undefined2 *param_3)

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
