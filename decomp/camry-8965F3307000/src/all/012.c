#include "common.h"


void FUN_00048026(void)

{
  uint uVar1;
  uint32_t puVar2;
  uint uVar3;
  undefined2 local_20;
  undefined2 uStack_1e;
  undefined4 uStack_1c;
  undefined4 uStack_18;
  undefined2 uStack_14;
  undefined2 uStack_12;
  undefined4 uStack_10;
  
  puVar2 = 0xfebeb800u;
  uVar3 = (uint)DAT_0002fbe2;
  uStack_14 = DAT_febe7da6;
  uStack_10 = DAT_febe7db8;
  local_20 = (undefined2)(DAT_febe820c * uVar3 >> 0x10);
  uVar1 = (uint)DAT_0002fbd8;
  uStack_12 = local_20;
  FUN_0006a678(&uStack_14,uVar1 * 10,&local_20,&uStack_1c);
  uStack_14 = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x3a58))));
  uStack_10 = (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + -0x3a44))));
  uStack_1e = (undefined2)((*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x35f2)))) * uVar3 >> 0x10);
  uStack_12 = uStack_1e;
  FUN_0006a678(&uStack_14,uVar1 * 10,&uStack_1e,&uStack_18);
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + -0x3a48)))) = uStack_1c;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + -0x3a44)))) = uStack_18;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x3a5a)))) = local_20;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x3a58)))) = uStack_1e;
  return;
}



void FUN_000480b4(void)

{
  uint uVar1;
  uint32_t puVar2;
  undefined2 local_20;
  undefined2 uStack_1e;
  undefined4 uStack_1c;
  undefined4 uStack_18;
  undefined2 uStack_14;
  undefined2 uStack_12;
  undefined4 uStack_10;
  
  puVar2 = 0xfebeb800u;
  uStack_14 = DAT_febe7daa;
  uStack_10 = DAT_febe7dc0;
  local_20 = (undefined2)((uint)DAT_febe8220 * (uint)DAT_0002fbe4 >> 0x10);
  uVar1 = (uint)DAT_0002fbda;
  uStack_12 = local_20;
  FUN_0006a678(&uStack_14,uVar1 * 10,&local_20,&uStack_1c);
  uStack_14 = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x3a54))));
  uStack_10 = (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + -0x3a3c))));
  uStack_1e = (undefined2)((uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x35de)))) * (uint)DAT_0002fbe6 >> 0x10);
  uStack_12 = uStack_1e;
  FUN_0006a678(&uStack_14,uVar1 * 10,&uStack_1e,&uStack_18);
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x3a56)))) = local_20;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x3a54)))) = uStack_1e;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + -0x3a40)))) = uStack_1c;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + -0x3a3c)))) = uStack_18;
  return;
}



void FUN_00048146(void)

{
  uint32_t puVar1;
  undefined2 uStack_12;
  undefined4 uStack_10;
  undefined2 uStack_c;
  undefined2 uStack_a;
  undefined4 uStack_8;
  
  puVar1 = 0xfebeb800u;
  uStack_12 = (undefined2)((uint)DAT_febe8210 * (uint)DAT_0002fbe8 >> 0x10);
  uStack_c = DAT_febe7db0;
  uStack_8 = DAT_febe7dc8;
  uStack_a = uStack_12;
  FUN_0006a678(&uStack_c,(uint)DAT_0002fbdc * 10,&uStack_12,&uStack_10);
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x3a38)))) = uStack_10;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x3a50)))) = uStack_12;
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



void FUN_00048230(void)

{
  ushort uVar1;
  
  uVar1 = DAT_febeeba6;
  FUN_00048026();
  FUN_000480b4();
  FUN_00048146();
  if (uVar1 < 0x300) {
    FUN_0004819a();
  }
  FUN_000481c0();
  FUN_00048200();
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4825a(void)

{
  return;
}



/* Filter unsigned6492 into7DD2/7DDC; mismatch of accumulator high16 and previous output reseeds
   from the input before6A678. Map via31808 into signed7DCE. Condition staged6492 through
   retained7DD2/7DDC; repair inconsistent accumulator high16 by reseeding input, then filter and
   map31808 into signed7DCE. No hardware-freshness inference. */

void f33_filter_thermistor_channel0(void)

{
  uint32_t puVar1;
  ushort uStack_16;
  uint uStack_14;
  ushort uStack_10;
  ushort uStack_e;
  uint uStack_c;
  
  puVar1 = 0xfebeb800u;
  uStack_e = DAT_febe6492;
  uStack_14 = DAT_febe7ddc;
  uStack_c = DAT_febe7ddc;
  uStack_16 = DAT_febe7dd2;
  uStack_10 = DAT_febe7dd2;
  if (DAT_febe7ddc >> 0x10 != (uint)DAT_febe7dd2) {
    uStack_10 = DAT_febe6492;
    uStack_c = (uint)DAT_febe6492 << 0x10;
  }
  FUN_0006a678(&uStack_10,DAT_00031804,&uStack_16,&uStack_14);
  FUN_000702b0(((undefined *)camry_host_ptr(0x31808u)),uStack_16,((undefined *)camry_host_ptr(0xfebe7dceu)));
  (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x3a2e)))) = uStack_16;
  (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x3a24)))) = uStack_14;
  return;
}



/* Companion6498 ->7DD4/7DE0 -> signed7DD6, with the same coherence repair and ROM map. This is
   software conditioning of staged inputs, not hardware sample-freshness proof. Companion6498 filter
   into7DD4/7DE0 and signed7DD6 uses the same coherence repair and ROM map as channel0. */

void f33_filter_thermistor_channel1(void)

{
  uint32_t puVar1;
  ushort uStack_16;
  uint uStack_14;
  ushort uStack_10;
  ushort uStack_e;
  uint uStack_c;
  
  puVar1 = 0xfebeb800u;
  uStack_e = DAT_febe6498;
  uStack_14 = DAT_febe7de0;
  uStack_c = DAT_febe7de0;
  uStack_16 = DAT_febe7dd4;
  uStack_10 = DAT_febe7dd4;
  if (DAT_febe7de0 >> 0x10 != (uint)DAT_febe7dd4) {
    uStack_10 = DAT_febe6498;
    uStack_c = (uint)DAT_febe6498 << 0x10;
  }
  FUN_0006a678(&uStack_10,DAT_00031804,&uStack_16,&uStack_14);
  FUN_000702b0(((undefined *)camry_host_ptr(0x31808u)),uStack_16,((undefined *)camry_host_ptr(0xfebe7dd6u)));
  (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x3a2c)))) = uStack_16;
  (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x3a20)))) = uStack_14;
  return;
}



/* Run both channel filters; publish signed max(7DCE,7DD6) at7DDA and mark7DCC=5A. Exact
   RDBI1063/1069 aliases expose this same publication, not two independent values. Run both
   thermistor filters and publish signed maximum at7DDA with software marker7DCC=5A. System2
   diagnostic label does not create a second independent published value. */

void f33_update_thermistor_channels(void)

{
  short sVar1;
  int iVar2;
  uint32_t puVar3;
  int iVar4;
  
  puVar3 = 0xfebeb800u;
  f33_filter_thermistor_channel0();
  f33_filter_thermistor_channel1();
  iVar2 = (int)(*((short *)camry_host_ptr((uint32_t)(puVar3 + -0x3a2a))));
  sVar1 = (*((short *)camry_host_ptr((uint32_t)(puVar3 + -0x3a32))));
  iVar4 = (int)sVar1;
  if (iVar2 - iVar4 < 0 == (iVar2 < 0 != iVar4 < 0 && iVar4 < 0 == iVar2 - iVar4 < 0) &&
      iVar2 != iVar4) {
    sVar1 = (*((short *)camry_host_ptr((uint32_t)(puVar3 + -0x3a2a))));
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + -0x3a26)))) = sVar1;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3a34))))) = 0x5a;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_483b4(void)

{
  return;
}



/* Single constant publisher: DAT_febe7de4 = 0; Shape-classified from the canonical corpus; the
   target cell is not yet named, so the written state's meaning is unknown. */

void FUN_000483b6(void)

{
  DAT_febe7de4 = 0;
  return;
}



void FUN_000483bc(void)

{
  uint32_t puVar1;
  uint uVar2;
  char cVar3;
  
  cVar3 = DAT_febe7de4;
  puVar1 = 0xfebeb800u;
  if (DAT_febe7de4 == '\x01') {
    puVar1 = 0xfebeb800u;
    uVar2 = f33_nvm_get_record_status(5);
    if (uVar2 == 0x10) {
      cVar3 = -1;
    }
    else if ((uVar2 & 0xf0) == 0x30) {
      cVar3 = -2;
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3a1c))))) = cVar3;
  return;
}



/* Require7DCC5A; publish signed7DCE/7DD6 plus zero word to family0 record5. Set7DE4=1 before
   setter; acceptance ignored. Independent from record6's7071 gate. 7DCC5A independently admits
   record5 with staged7DCE/7DD6 and zero word; arm7DE4 before calling setter, regardless of
   acceptance. */

void f33_publish_thermal_reference_record(void)

{
  undefined2 local_c;
  undefined2 uStack_a;
  undefined4 uStack_8;
  
  if (DAT_febe7dcc == 'Z') {
    local_c = DAT_febe7dce;
    uStack_8 = 0;
    uStack_a = DAT_febe7dd6;
    DAT_febe7de4 = 1;
    f33_nvm_set_record(5,(uint *)&local_c);
  }
  return;
}



void FUN_0004841e(void)

{
  undefined2 local_c;
  undefined2 uStack_a;
  undefined4 uStack_8;
  
  local_c = 32000;
  uStack_a = 32000;
  uStack_8 = 0;
  f33_nvm_set_record(5,(uint *)&local_c);
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4843a(void)

{
  return;
}



/* Constant-block fill: 14 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

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



/* WARNING: Removing unreachable block (ram,0x00048486) */
/* R6/R7 are the saturated A-B and C-D differences, BEFORE their /2 diagnostic mirrors. 7CB7 selects
   (first-second)/2, negated second, or first. Nonzero71EC bits5/6 override: bit5 selects negated
   second, otherwise first. Publish the effective selector at7DE8. Select full saturated pair
   differences P/Q passed in R6/R7: mode0=(P-Q)/2; mode1=-Q; other modes=P. Override71EC bits5/6
   precedes7CB7; arguments are not original sensor channels or half-scaled mirrors. */

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



/* FIRST clamp previous to+/-5120, then bound value within that center+/-u16[30E50]. Exact window
   is5120. This is not an unbounded previous-value-centered slew limiter. Clamp previous center
   to+-5120 before bounding the new selected difference within center+-5120. The prior center is not
   trusted to be already bounded. */

short f33_bound_torque_tracking_step(short value,short previous)

{
  int iVar1;
  int iVar2;
  int iVar3;
  short sVar4;
  
  iVar2 = (int)value;
  iVar3 = (int)previous;
  if (iVar3 + -0x1400 < 0 == (iVar3 < 0 && -1 < iVar3 + -0x1400)) {
    iVar3 = 0x1400;
  }
  if (iVar3 + 0x1400 < 0 != (-1 < iVar3 && iVar3 + 0x1400 < 0)) {
    iVar3 = -0x1400;
  }
  iVar1 = iVar3 - (uint)DAT_00030e50;
  iVar3 = (uint)DAT_00030e50 + iVar3;
  if (iVar2 - iVar3 < 0 != (iVar2 < 0 != iVar3 < 0 && iVar3 < 0 == iVar2 - iVar3 < 0)) {
    iVar3 = iVar2;
  }
  if (iVar3 - iVar1 < 0 == (iVar3 < 0 != iVar1 < 0 && iVar1 < 0 == iVar3 - iVar1 < 0)) {
    sVar4 = (short)iVar3;
  }
  else {
    sVar4 = (short)iVar1;
  }
  return sVar4;
}



/* Clamp signed16 input to+/-s16[30E52], exact2109 raw counts, and return in R10. Apply exact ROM
   final symmetric torque limit2109 after the retained-center window. Signed-halfword input and
   return. */

short f33_clamp_decoded_torque(short value)

{
  int iVar1;
  int iVar2;
  short sVar3;
  int iVar4;
  
  iVar2 = (int)value;
  iVar1 = (int)DAT_00030e52;
  sVar3 = -DAT_00030e52;
  iVar4 = (int)sVar3;
  if (iVar2 - iVar1 < 0 != (iVar2 < 0 != iVar1 < 0 && iVar1 < 0 == iVar2 - iVar1 < 0)) {
    iVar1 = iVar2;
  }
  if (iVar1 - iVar4 < 0 == (iVar1 < 0 != iVar4 < 0 && iVar4 < 0 == iVar1 - iVar4 < 0)) {
    sVar3 = (short)iVar1;
  }
  return sVar3;
}



/* WARNING: Removing unreachable block (ram,0x00048654) */
/* WARNING: Removing unreachable block (ram,0x0004864c) */
/* WARNING: Removing unreachable block (ram,0x000485f0) */
/* WARNING: Removing unreachable block (ram,0x000485e8) */
/* WARNING: Removing unreachable block (ram,0x000485e0) */
/* WARNING: Removing unreachable block (ram,0x000485d8) */
/* WARNING: Removing unreachable block (ram,0x00048560) */
/* WARNING: Removing unreachable block (ram,0x0004855c) */
/* WARNING: Removing unreachable block (ram,0x00048558) */
/* WARNING: Removing unreachable block (ram,0x00048554) */
/* Only on8A1C==5A: subtract four zero points from unsigned raw channels, apply signed ROM
   gains/div2048, publish channel/pair mirrors, select from the full pair differences, bound the
   tracking center/step and independently amplitude-clamp into7DEA. Alternate software cadence
   retains state. Native four-channel composition uses signed gain-2509; full pair differences feed
   mode override; out-of-range prior center16000 is bounded before tracking5016 and final clamp2109.
   Physical torque units and frame freshness remain separate. */

void f33_decode_torque_sensor_channels(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint32_t puVar4;
  short value;
  short sVar5;
  int iVar6;
  int iVar7;
  
  sVar5 = DAT_febe7dfa;
  puVar4 = 0xfebeb800u;
  if (DAT_febe8a1c == 'Z') {
    DAT_febe7dfc = (uint)DAT_febe81e6 - (uint)DAT_febe6ad2;
    DAT_febe7e00 = (uint)DAT_febe81e8 - (uint)DAT_febe6ad4;
    DAT_febe7e04 = (uint)DAT_febe81ea - (uint)DAT_febe6ad6;
    DAT_febe7e08 = (uint)DAT_febe81ec - (uint)DAT_febe6ad8;
    iVar7 = (DAT_febe7dfc * DAT_00030e54) / 0x800;
    iVar6 = (DAT_febe7e00 * DAT_00030e54) / 0x800;
    iVar3 = (DAT_febe7e04 * DAT_00030e56) / 0x800;
    iVar1 = (DAT_febe7e08 * DAT_00030e56) / 0x800;
    if (iVar7 + 0x7fff < 0 == (-1 < iVar7 && iVar7 + 0x7fff < 0) && iVar7 != -0x7fff) {
      if (iVar7 + -0x7fff < 0 == (iVar7 < 0 && -1 < iVar7 + -0x7fff) && iVar7 != 0x7fff) {
        iVar7 = 0x7fff;
      }
      else {
        iVar7 = (int)(short)iVar7;
      }
    }
    else {
      iVar7 = -0x7fff;
    }
    if (iVar6 + 0x7fff < 0 == (-1 < iVar6 && iVar6 + 0x7fff < 0) && iVar6 != -0x7fff) {
      if (iVar6 + -0x7fff < 0 == (iVar6 < 0 && -1 < iVar6 + -0x7fff) && iVar6 != 0x7fff) {
        iVar6 = 0x7fff;
      }
      else {
        iVar6 = (int)(short)iVar6;
      }
    }
    else {
      iVar6 = -0x7fff;
    }
    if (iVar3 + 0x7fff < 0 == (-1 < iVar3 && iVar3 + 0x7fff < 0) && iVar3 != -0x7fff) {
      iVar2 = (int)(short)iVar3;
      if (iVar3 + -0x7fff < 0 == (iVar3 < 0 && -1 < iVar3 + -0x7fff) && iVar3 != 0x7fff) {
        iVar2 = 0x7fff;
      }
    }
    else {
      iVar2 = -0x7fff;
    }
    if (iVar1 + 0x7fff < 0 == (-1 < iVar1 && iVar1 + 0x7fff < 0) && iVar1 != -0x7fff) {
      iVar3 = (int)(short)iVar1;
      if (iVar1 + -0x7fff < 0 == (iVar1 < 0 && -1 < iVar1 + -0x7fff) && iVar1 != 0x7fff) {
        iVar3 = 0x7fff;
      }
    }
    else {
      iVar3 = -0x7fff;
    }
    DAT_febe7dec = (undefined2)(iVar7 / 2);
    DAT_febe7dee = (undefined2)(iVar6 / 2);
    DAT_febe7df0 = (undefined2)(iVar2 / 2);
    iVar7 = iVar7 - iVar6;
    DAT_febe7df2 = (undefined2)(iVar3 / 2);
    if (iVar7 + 0x7fff < 0 == (-1 < iVar7 && iVar7 + 0x7fff < 0) && iVar7 != -0x7fff) {
      if (iVar7 + -0x7fff < 0 == (iVar7 < 0 && -1 < iVar7 + -0x7fff) && iVar7 != 0x7fff) {
        iVar6 = 0x7fff;
      }
      else {
        iVar6 = -0x8000;
        if (iVar7 + 0x8000 < 0 == (-1 < iVar7 && iVar7 + 0x8000 < 0)) {
          iVar6 = (int)(short)iVar7;
        }
      }
    }
    else {
      iVar6 = -0x7fff;
    }
    iVar2 = iVar2 - iVar3;
    if (iVar2 + 0x7fff < 0 == (-1 < iVar2 && iVar2 + 0x7fff < 0) && iVar2 != -0x7fff) {
      if (iVar2 + -0x7fff < 0 == (iVar2 < 0 && -1 < iVar2 + -0x7fff) && iVar2 != 0x7fff) {
        iVar7 = 0x7fff;
      }
      else {
        iVar7 = -0x8000;
        if (iVar2 + 0x8000 < 0 == (-1 < iVar2 && iVar2 + 0x8000 < 0)) {
          iVar7 = (int)(short)iVar2;
        }
      }
    }
    else {
      iVar7 = -0x7fff;
    }
    DAT_febe7df4 = (undefined2)(iVar6 / 2);
    DAT_febe7df6 = (undefined2)(iVar7 / 2);
    value = f33_select_torque_pair_differences((short)iVar6,(short)iVar7);
    (*((short *)camry_host_ptr((uint32_t)(puVar4 + -0x3a08)))) = value;
    sVar5 = f33_bound_torque_tracking_step(value,sVar5);
    (*((short *)camry_host_ptr((uint32_t)(puVar4 + -0x3a06)))) = sVar5;
    sVar5 = f33_clamp_decoded_torque(sVar5);
    (*((short *)camry_host_ptr((uint32_t)(puVar4 + -0x3a16)))) = sVar5;
  }
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4867c(void)

{
  return;
}



/* Single constant publisher: DAT_febe7e0c = 0; Shape-classified from the canonical corpus; the
   target cell is not yet named, so the written state's meaning is unknown. */

void FUN_0004867e(void)

{
  DAT_febe7e0c = 0;
  return;
}



/* On8A1C==5A publish7E0C from6870 if686C==5A, otherwise7DEA; else hold. The selection byte alone is
   not a physical sensor-health classification. Only8A1C==5A publishes7E0C. Gate686C==5A
   selects6870; otherwise7DEA. Source selection alone does not establish physical health or
   permission. */

void f33_publish_selected_torque_feedback(void)

{
  if ((DAT_febe8a1c == 'Z') && (DAT_febe7e0c = DAT_febe6870, DAT_febe686c != 'Z')) {
    DAT_febe7e0c = DAT_febe7dea;
  }
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_486a8(void)

{
  return;
}



/* Constant-block fill: 12 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

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



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_48d30(void)

{
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



/* Exact31E58=1: refresh each retained three-channel reference bank7E6C/7E72 only when corresponding
   snapshot636A/636B equals5A; otherwise hold the older reference generation. */

void f33_refresh_monitor_current_reference_banks(void)

{
  if (DAT_00031e58 == '\x01') {
    if (DAT_febe636a == 'Z') {
      f33_monitor_current_retained_reference[0] = DAT_febe6238;
      f33_monitor_current_retained_reference[1] = DAT_febe623a;
      f33_monitor_current_retained_reference[2] = DAT_febe623c;
    }
    if (DAT_febe636b != 'Z') {
      return;
    }
  }
  else {
    f33_monitor_current_retained_reference[0] = DAT_febe6238;
    f33_monitor_current_retained_reference[1] = DAT_febe623a;
    f33_monitor_current_retained_reference[2] = DAT_febe623c;
  }
  f33_monitor_current_retained_reference[5] = DAT_febe6242;
  f33_monitor_current_retained_reference[4] = DAT_febe6240;
  f33_monitor_current_retained_reference[3] = DAT_febe623e;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_495a2(void)

{
  return;
}



/* Constant-block fill: 6 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

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



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4963c(void)

{
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



/* WARNING: Removing unreachable block (ram,0x000496cc) */

void FUN_0004964c(void)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  int iVar4;
  
  if ((DAT_febe8a14 == '\x01') && (uVar3 = (uint)DAT_febeeac8, uVar3 != 0)) {
    iVar1 = (int)DAT_febe5f36 << 0xe;
    if (uVar3 != 0) {
      if (iVar1 == -0x80000000 && uVar3 == 0xffffffff) {
        iVar1 = -0x80000000;
      }
      else {
        iVar1 = iVar1 / (int)uVar3;
      }
    }
    iVar4 = -iVar1;
    if (iVar4 + 0x7fff < 0 == (-1 < iVar4 && iVar4 + 0x7fff < 0) && iVar1 != 0x7fff) {
      if (iVar4 + -0x7fff < 0 == (iVar4 < 0 && -1 < iVar4 + -0x7fff) && iVar1 != -0x7fff) {
        iVar1 = 0x7fff;
      }
      else {
        iVar1 = (int)(short)iVar4;
      }
    }
    else {
      iVar1 = -0x7fff;
    }
    uVar3 = (uint)DAT_000318a8;
    if ((uVar3 == 0) || (0xffff < uVar3 * 4)) {
      iVar4 = (int)DAT_febe7eaa << 0x10;
      iVar2 = iVar1 << 0x10;
    }
    else {
      iVar4 = (int)DAT_febe7eaa * uVar3 * 4;
      iVar2 = iVar1 * uVar3 * 4;
    }
    DAT_febe7ea8 = (undefined2)iVar1;
    DAT_febe7eac = DAT_febe7eaa;
    DAT_febe7eb0 = iVar2 + (DAT_febe7eb0 - iVar4);
    DAT_febe7eaa = (short)(DAT_febe7eb0 / 0x10000);
  }
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



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_49706(void)

{
  return;
}



/* Channel1/2, grouped status, group enable/bypass11 and E82A gates. Separate return2 retains prior
   monitor state instead of declaring healthy. Channel/group/status/E82A admission has separate
   retain result2; disabled monitoring is not uniformly a healthy observation. */

uchar f33_classify_receive_monitor_admission(uint channel,uint group,uint selector)

{
  char cVar1;
  char cVar2;
  code cVar3;
  uint32_t puVar4;
  uchar uVar5;
  
  puVar4 = 0xfebeb800u;
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7f2eu + (uint32_t)(channel & 0xff) * 1u))));
  cVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7f2cu + (uint32_t)(channel & 0xff) * 1u))));
  uVar5 = f33_get_grouped_status_byte(selector & 0xff);
  cVar3 = (code)0x5a;
  if ((group & 0xff) != 0xb) {
    cVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x3000u + (uint32_t)((int)(puVar4 + (group & 0xff) + 7))))));
  }
  if ((((cVar2 != '\x01' && cVar2 != '\x02') || (uVar5 != '\0')) || (cVar3 != (code)0x5a)) ||
     (uVar5 = '\0', (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x302a))))) != '\0')) {
    if (cVar1 == 'Z') {
      uVar5 = '\x02';
    }
    else {
      uVar5 = '\x01';
    }
  }
  return uVar5;
}



/* Raw marker5A drives strict counter>threshold timeout; other marker clears. Confirmed timeout
   retention is distinct from raw invalidity. Raw marker5A advances timeout counter and confirms
   only strictly above descriptor threshold; non5A clears counter. */

uint f33_advance_receive_timeout(uint selector)

{
  int iVar1;
  int iVar2;
  ushort uVar3;
  uint uVar4;
  
  iVar1 = (selector & 0xff) * 8;
  iVar2 = (selector & 0xff) * 2;
  uVar3 = *(ushort *)(((undefined *)camry_host_ptr(0xfebe7eb4u)) + iVar2);
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe52d8u + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x28fe4u + (uint32_t)(iVar1) * 1u))))) * 1u)))) == 'Z') {
    if ((*(ushort *)(((undefined *)camry_host_ptr(0x28fe8u)) + iVar1) < uVar3) ||
       (uVar3 = uVar3 + 1, *(ushort *)(((undefined *)camry_host_ptr(0x28fe8u)) + iVar1) < uVar3)) {
      uVar4 = 0x22;
    }
    else {
      uVar4 = 0x11;
    }
  }
  else {
    uVar4 = 0;
    uVar3 = 0;
  }
  *(ushort *)(((undefined *)camry_host_ptr(0xfebe7eb4u)) + iVar2) = uVar3;
  return uVar4;
}



/* Raw marker5A drives strict counter>threshold timeout; other marker clears. Confirmed timeout
   retention is distinct from raw invalidity. Confirmed receive timeout remains while marker5A;
   other marker clears it independently of raw nonzero invalidity. */

uint f33_retain_receive_timeout(uint selector)

{
  char cVar1;
  uint uVar2;
  undefined2 uVar3;
  
  uVar2 = 0x22;
  uVar3 = *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe7eb4u)) + (selector & 0xff) * 2);
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe52d8u + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x28fe4u + (uint32_t)((selector & 0xff) * 8) * 1u))))) * 1u))));
  if (cVar1 != 'Z') {
    uVar3 = 0;
  }
  *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe7eb4u)) + (selector & 0xff) * 2) = uVar3;
  if (cVar1 != 'Z') {
    uVar2 = 0;
  }
  return uVar2;
}



undefined4 FUN_000497dc(uint param_1)

{
  f33_application_receive_status[param_1 & 0xff] = '\x01';
  *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe7eb4u)) + (param_1 & 0xff) * 2) = 0;
  return 0;
}



undefined4 FUN_000497f4(uint param_1)

{
  int iVar1;
  uint32_t puVar2;
  uchar uVar3;
  undefined4 uVar4;
  undefined1 uVar5;
  uint uVar6;
  
  puVar2 = 0xfebeb800u;
  param_1 = param_1 & 0xff;
  iVar1 = param_1 * 8;
  uVar6 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7ef0u + (uint32_t)(param_1) * 1u))));
  uVar3 = f33_classify_receive_monitor_admission
                    ((uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x28fe5u + (uint32_t)(iVar1) * 1u)))),(uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x28fe7u + (uint32_t)(iVar1) * 1u)))),param_1);
  if (uVar3 == '\0') {
    if ((uVar6 == 0) || (uVar6 == 0x11)) {
      uVar6 = f33_advance_receive_timeout(param_1);
    }
    else if (uVar6 == 0x22) {
LAB_00049868:
      uVar6 = f33_retain_receive_timeout(param_1);
    }
    else {
      uVar6 = FUN_000497dc(param_1);
    }
LAB_00049872:
    if (uVar6 == 0x22) {
      uVar4 = 2;
      uVar5 = 0x22;
      goto LAB_00049880;
    }
  }
  else {
    if (uVar3 == '\x02') goto LAB_00049872;
    if ((uVar6 != 0) && (uVar6 != 0x11)) {
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x28fe6u + (uint32_t)(iVar1) * 1u)))) == 'Z') goto LAB_00049868;
      goto LAB_00049872;
    }
    uVar6 = 0;
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + param_1 * 2 + -0x394c)))) = 0;
  }
  uVar5 = (undefined1)uVar6;
  uVar4 = 0;
LAB_00049880:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7ef0u + (uint32_t)(param_1) * 1u)))) = uVar5;
  return uVar4;
}



/* Rebuild30 status bytes: raw-marker-nonzero bit0 plus confirmed-timeout bit1. Admission can
   preserve old state; status generation is not a timestamp. All30 receive-status rows join raw
   marker nonzero with separately confirmed timeout. Exact threshold equality remains invalid-only;
   next count confirms stale status. */

void f33_update_application_receive_statuses(void)

{
  int iVar1;
  int iVar2;
  char cVar3;
  undefined8 uVar4;
  byte bVar5;
  int iVar6;
  
  uVar4 = 0xfebeb800;
  iVar6 = 0;
  do {
    cVar3 = (*((char *)camry_host_ptr((uint32_t)((uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x28fe4u + (uint32_t)(iVar6 * 8) * 1u)))) + (int)uVar4 + -0x6528))));
    if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2bca8u + (uint32_t)(iVar6) * 1u)))) == 'Z') || (*(short *)(((undefined *)camry_host_ptr(0x28fe8u)) + iVar6 * 8) == -1)) {
      bVar5 = 0;
    }
    else {
      bVar5 = FUN_000497f4(iVar6);
    }
    iVar2 = iVar6 + 1;
    (*((byte *)camry_host_ptr((uint32_t)((int)uVar4 + iVar6 + -0x38f2)))) = bVar5 | cVar3 != '\0';
    iVar1 = iVar6 + -0x1d;
    iVar6 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  return;
}



/* Read7F0E[selector] for selector<30, otherwise return1. Read selected application receive-status
   byte for selector<30; otherwise return1. Selectors are not numeric CAN IDs. */

uchar f33_get_application_receive_status(uint selector)

{
  if ((selector & 0xff) < 0x1e) {
    return f33_application_receive_status[selector & 0xff];
  }
  return '\x01';
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_498f4(void)

{
  return;
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



void FUN_0004996e(uint param_1)

{
  char cVar1;
  uint uVar2;
  char cVar3;
  undefined1 uVar4;
  undefined1 uVar5;
  uint uVar6;
  char cVar7;
  uint uVar8;
  char cStack_2f;
  ushort uStack_2e;
  
  cVar1 = DAT_febe7f34;
  uVar2 = param_1 & 0xff;
  cVar7 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7f2eu + (uint32_t)(uVar2) * 1u))));
  FUN_0007c652(uVar2,&uStack_2e);
  if ((uStack_2e & 0x48) != 0) {
    cVar7 = 'Z';
  }
  uVar5 = 0;
  if ((uStack_2e & 1) != 0) {
    uVar5 = 0x5a;
  }
  FUN_0007e88c(uVar2,&cStack_2f);
  if (((cStack_2f == '\x02') || (cStack_2f == '\x03')) || (cStack_2f == '\x04')) {
    uVar6 = 1 << (param_1 & 0x1f) | 0x100;
  }
  else {
    uVar6 = 0;
  }
  if (uVar2 != 0) {
    uVar8 = uVar6 & 2;
  }
  else {
    uVar8 = uVar6 & 1;
  }
  cVar3 = FUN_0007bd3a(uVar2 != 0);
  if ((((uVar6 & 0xff00) == 0x100) && (uVar8 == 1 || uVar8 == 2)) && (cVar7 != 'Z')) {
    if (cVar3 == '\x03') {
      if (cVar1 == 'Z') {
        uVar4 = 2;
        goto LAB_00049a1c;
      }
    }
    else if (cVar3 != '\x01') goto LAB_00049a1a;
    uVar4 = 1;
  }
  else {
LAB_00049a1a:
    uVar4 = 3;
  }
LAB_00049a1c:
  DAT_febe7f3c = (undefined2)uVar6;
  DAT_febe7f3e = (undefined2)(uVar6 & 0xff00);
  *(short *)(((undefined *)camry_host_ptr(0xfebe7f40u)) + uVar2 * 2) = (short)uVar8;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7f32u + (uint32_t)(uVar2) * 1u)))) = cVar3;
  *(ushort *)(((undefined *)camry_host_ptr(0xfebe7f44u)) + uVar2 * 2) = uStack_2e;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7f2eu + (uint32_t)(uVar2) * 1u)))) = cVar7;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7f30u + (uint32_t)(uVar2) * 1u)))) = uVar5;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7f2cu + (uint32_t)(uVar2) * 1u)))) = uVar4;
  return;
}



uint FUN_00049a98(undefined1 param_1,char param_2,char param_3)

{
  uint uVar1;
  
  uVar1 = 0;
  switch(param_1) {
  case 0:
    uVar1 = 1;
    break;
  case 1:
    uVar1 = 2;
    break;
  case 2:
    uVar1 = 4;
    break;
  case 3:
    uVar1 = 8;
  }
  if (param_2 == 'Z') {
    uVar1 = uVar1 | 0x10;
  }
  if (param_3 == 'Z') {
    uVar1 = uVar1 | 0x20;
  }
  return uVar1;
}



/* Snapshot8196/81CC;composechannelmonitor;enableonlystate2&&8196!=11&&81CC==5A,otherwiseissuedisableedge.
   Publish7F3Asoftwarestatus. */

void f33_reconcile_application_normal_network_policy(void)

{
  undefined1 uVar1;
  undefined1 uVar2;
  undefined1 uVar3;
  uchar uVar4;
  char cVar5;
  uint32_t puVar6;
  undefined *puVar7;
  ushort uVar8;
  short sVar9;
  
  cVar5 = DAT_febe81cc;
  uVar4 = f33_diagnostic_normal_tx_policy_request;
  puVar6 = 0xfebeb800u;
  FUN_00049918();
  FUN_0004996e(0);
  puVar7 = ((undefined *)camry_host_ptr((uint32_t)(puVar6)));
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x38d4))))) == '\x02') && (uVar4 != '\x11')) && (cVar5 == 'Z')) {
    FUN_00049a70(0);
  }
  else {
    FUN_00049a48(0);
  }
  uVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x38d1)))));
  uVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x38cf)))));
  uVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x38d3)))));
  uVar8 = FUN_00049a98((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x38d4))))),(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x38d2))))),(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x38d0))))));
  sVar9 = FUN_00049a98(uVar3,uVar1,uVar2);
  *(ushort *)(puVar7 + -0x38c6) = uVar8 | sVar9 << 8;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_49b38(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_49b3a(void)

{
  return;
}



/* Constant-block fill: 12 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

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



void FUN_00049bba(char param_1)

{
  char cVar1;
  
  if ((param_1 == '3') || (DAT_febe66b8 < DAT_00030e38)) {
    cVar1 = 'Z';
  }
  else {
    cVar1 = '\0';
  }
  if (DAT_febe66ac != '\0') {
    if (cVar1 == 'Z') {
      DAT_febe7f62 = 0;
      DAT_febe7f4e = 'Z';
      DAT_febe7f4d = 'Z';
    }
    else if (DAT_febe7f4d == 'Z') {
      DAT_febe7f4d = '\0';
    }
    else if ((DAT_febe7f4e == 'Z') &&
            ((DAT_0002fbf2 < DAT_febe7f62 ||
             (DAT_febe7f62 = DAT_febe7f62 + 1, DAT_0002fbf2 < DAT_febe7f62)))) {
      DAT_febe7f4e = '\0';
    }
  }
  return;
}



void FUN_00049c2c(char param_1)

{
  if (param_1 == 'Z') {
    DAT_febe7f64 = 0;
    DAT_febe7f4f = 'Z';
  }
  else if ((DAT_febe7f4f == 'Z') &&
          ((DAT_0002fbf4 < DAT_febe7f64 ||
           (DAT_febe7f64 = DAT_febe7f64 + 1, DAT_0002fbf4 < DAT_febe7f64)))) {
    DAT_febe7f4f = '\0';
  }
  return;
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



undefined4 FUN_00049d5e(char param_1)

{
  DAT_febe7f5f = -1;
  DAT_febe7f5d = DAT_febe7f5f;
  DAT_febe7f5e = DAT_febe7f5f;
  if (param_1 == '\x01' || param_1 == '\x02') {
    if ((DAT_febe7f56 == 'Z') && (DAT_febe7f5d = DAT_febe803c, param_1 == '\x01')) {
      DAT_febe7f5d = DAT_febe803b;
    }
    if (DAT_febe7f59 == 'Z') {
      DAT_febe7f5e = DAT_febe8016;
    }
    if (DAT_febe7f5c == 'Z') {
      DAT_febe7f5f = DAT_febe800c;
    }
    if (((((((int8_t)DAT_febe7f5d) != -1) || (((int8_t)DAT_febe7f5e) != -1)) || (((int8_t)DAT_febe7f5f) != -1)) &&
        ((DAT_febe7f5d == '\0' || (((int8_t)DAT_febe7f5d) == -1)))) &&
       (((DAT_febe7f5e == '\0' || (DAT_febe7f5f == '\0')) ||
        ((((int8_t)DAT_febe7f5e) == -1 && (((int8_t)DAT_febe7f5f) == -1)))))) {
      return 0x5a;
    }
  }
  return 0;
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



/* Low8 selector<30 reads290DA+8*selector: values1/2 select7F51/7F52; other rows or out-of-range
   selectors return7F50. These are staged status bytes, not event IDs. Low8 selector<30
   reads290DA+8*selector:1/2 route to7F51/52, otherwise7F50. Return is a staged status byte, not
   event identity or physical freshness. */

uchar f33_get_grouped_status_byte(uint selector)

{
  if ((selector & 0xff) < 0x1e) {
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x290dau + (uint32_t)((selector & 0xff) * 8) * 1u)))) == '\x01') {
      return DAT_febe7f51;
    }
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x290dau + (uint32_t)((selector & 0xff) * 8) * 1u)))) == '\x02') {
      return DAT_febe7f52;
    }
  }
  return DAT_febe7f50;
}



/* Constant-block fill: 7 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_49ec6(void)

{
  DAT_febe7f6c = 0;
  DAT_febe7f72 = 0;
  DAT_febe7f74 = 0;
  DAT_febe7f76 = 0;
  DAT_febe7f78 = 0;
  DAT_febe7f7a = 0;
  DAT_febe7f7c = 0;
  return;
}



/* Constant-block fill: 6 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_49eda(void)

{
  DAT_febe7f6d = 0;
  DAT_febe7f7e = 0;
  DAT_febe7f80 = 0;
  DAT_febe7f82 = 0;
  DAT_febe7f84 = 0;
  DAT_febe7f86 = 0;
  return;
}



/* Constant-block fill: 6 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_49eec(void)

{
  DAT_febe7f6e = 0;
  DAT_febe7f88 = 0;
  DAT_febe7f8a = 0;
  DAT_febe7f8c = 0;
  DAT_febe7f8e = 0;
  DAT_febe7f90 = 0;
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



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_49f1e(void)

{
  return;
}



/* Configured source qualifier: local0 + predicate22 starts11 and shared mode1. Persistent22 with
   entry count>=5 selects local22/shared2; entry persistence>=200 selects local44/shared3. Local11
   resets on any predicate other than22, including inapplicable44. Local22 recovers on11 immediately
   with configured recovery limit0; predicate44 resets counters only. Local44 recovers only after
   entry healthy-count>=200; other predicates reset that recovery count. Direct shared7F68 writes
   are ordered, not a max/OR reduction. */

void f33_advance_dual_source_admission_qualification(void)

{
  ushort uVar1;
  ushort uVar2;
  uint32_t puVar3;
  uint uVar4;
  undefined *puVar5;
  
  puVar3 = 0xfebeb800u;
  puVar5 = ((undefined *)camry_host_ptr(0xfebeb800u));
  if (DAT_febe7f6c == '\0') {
    uVar4 = f33_classify_dual_internal_source_observations();
    if (uVar4 != 0x22) {
      return;
    }
    uVar2 = *(short *)(puVar5 + -0x388e) + 1;
    *(ushort *)(puVar5 + -0x388e) = uVar2;
    if (*(ushort *)(puVar5 + -0x388c) < uVar2) {
      *(ushort *)(puVar5 + -0x388c) = uVar2;
    }
    puVar5[-0x3894] = 0x11;
    FUN_0004a3fc();
    return;
  }
  if (DAT_febe7f6c == '\x11') {
    uVar4 = f33_classify_dual_internal_source_observations();
    if (uVar4 == 0x22) {
      uVar2 = (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x388e))));
      if (DAT_0002bb0c <= uVar2) {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3894))))) = 0x22;
        FUN_0004a40e();
        return;
      }
      (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x388e)))) = uVar2 + 1;
      if ((ushort)(uVar2 + 1) <= (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x388c))))) {
        return;
      }
      (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x388c)))) = uVar2 + 1;
      return;
    }
    puVar5 = ((undefined *)camry_host_ptr((uint32_t)(puVar3 + -0x3898)));
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x388e)))) = 0;
  }
  else if (DAT_febe7f6c == '\"') {
    uVar4 = f33_classify_dual_internal_source_observations();
    uVar1 = DAT_0002bb10;
    uVar2 = DAT_0002bb0e;
    if (uVar4 == 0x22) {
      uVar1 = (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x3888))));
      (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x388a)))) = 0;
      if (uVar2 <= uVar1) {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3894))))) = 0x44;
        FUN_0004a416();
        return;
      }
      (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x3888)))) = uVar1 + 1;
      if ((ushort)(uVar1 + 1) <= (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x3886))))) {
        return;
      }
      (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x3886)))) = uVar1 + 1;
      return;
    }
    if (uVar4 != 0x11) {
      if (uVar4 != 0x44) {
        return;
      }
      (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3888)))) = 0;
      (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x388a)))) = 0;
      return;
    }
    puVar5 = ((undefined *)camry_host_ptr((uint32_t)(puVar3 + -0x3898)));
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3888)))) = 0;
    if ((*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x388a)))) < uVar1) {
      (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x388a)))) = (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x388a)))) + 1;
      return;
    }
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x388e)))) = 0;
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x388a)))) = 0;
  }
  else {
    if (DAT_febe7f6c != 'D') {
      return;
    }
    uVar4 = f33_classify_dual_internal_source_observations();
    if (uVar4 != 0x11) {
      (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3884)))) = 0;
      return;
    }
    if ((*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x3884)))) < DAT_0002bb12) {
      (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x3884)))) = (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x3884)))) + 1;
      return;
    }
    puVar5 = ((undefined *)camry_host_ptr((uint32_t)(puVar3 + -0x3898)));
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x388e)))) = 0;
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x388a)))) = 0;
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3888)))) = 0;
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3884)))) = 0;
  }
  puVar5[4] = 0;
  FUN_0004a404();
  return;
}



/* Configured source qualifier: local0 + predicate22 starts11 and shared mode1. Persistent22 with
   entry count>=5 selects local22/shared2; entry persistence>=200 selects local44/shared3. Local11
   resets on any predicate other than22, including inapplicable44. Local22 recovers on11 immediately
   with configured recovery limit0; predicate44 resets counters only. Local44 has no ordinary
   recovery branch; cause latch7F6A is set on entry. Direct shared7F68 writes are ordered, not a
   max/OR reduction. */

void f33_advance_first_source_admission_qualification(void)

{
  ushort uVar1;
  ushort uVar2;
  uint32_t puVar3;
  uint32_t puVar4;
  uint uVar5;
  
  puVar4 = 0xfebeb800u;
  puVar3 = 0xfebeb800u;
  if (DAT_febe7f6d == '\0') {
    uVar5 = f33_classify_first_internal_source_observation();
    if (uVar5 != 0x22) {
      return;
    }
    uVar2 = (*((short *)camry_host_ptr((uint32_t)(puVar3 + -0x3882)))) + 1;
    (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x3882)))) = uVar2;
    if ((*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x3880)))) < uVar2) {
      (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x3880)))) = uVar2;
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3893))))) = 0x11;
    FUN_0004a3fc();
    return;
  }
  if (DAT_febe7f6d == '\x11') {
    uVar5 = f33_classify_first_internal_source_observation();
    if (uVar5 == 0x22) {
      uVar2 = (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + -0x3882))));
      if (DAT_0002bb14 <= uVar2) {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3893))))) = 0x22;
        FUN_0004a40e();
        return;
      }
      (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + -0x3882)))) = uVar2 + 1;
      if ((ushort)(uVar2 + 1) <= (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + -0x3880))))) {
        return;
      }
      (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + -0x3880)))) = uVar2 + 1;
      return;
    }
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar4 + -0x3882)))) = 0;
  }
  else {
    if (DAT_febe7f6d != '\"') {
      return;
    }
    uVar5 = f33_classify_first_internal_source_observation();
    uVar1 = DAT_0002bb18;
    uVar2 = DAT_0002bb16;
    if (uVar5 == 0x22) {
      uVar1 = (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + -0x387c))));
      (*((undefined2 *)camry_host_ptr((uint32_t)(puVar4 + -0x387e)))) = 0;
      if (uVar2 <= uVar1) {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3893))))) = 0x44;
        FUN_0004a426();
        return;
      }
      (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + -0x387c)))) = uVar1 + 1;
      if ((ushort)(uVar1 + 1) <= (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + -0x387a))))) {
        return;
      }
      (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + -0x387a)))) = uVar1 + 1;
      return;
    }
    if (uVar5 != 0x11) {
      if (uVar5 != 0x44) {
        return;
      }
      (*((undefined2 *)camry_host_ptr((uint32_t)(puVar4 + -0x387c)))) = 0;
      (*((undefined2 *)camry_host_ptr((uint32_t)(puVar4 + -0x387e)))) = 0;
      return;
    }
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar4 + -0x387c)))) = 0;
    if ((*((ushort *)camry_host_ptr((uint32_t)(puVar4 + -0x387e)))) < uVar1) {
      (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + -0x387e)))) = (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + -0x387e)))) + 1;
      return;
    }
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar4 + -0x3882)))) = 0;
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar4 + -0x387e)))) = 0;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3893))))) = 0;
  FUN_0004a404();
  return;
}



/* Configured source qualifier: local0 + predicate22 starts11 and shared mode1. Persistent22 with
   entry count>=5 selects local22/shared2; entry persistence>=200 selects local44/shared3. Local11
   resets on any predicate other than22, including inapplicable44. Local22 recovers on11 immediately
   with configured recovery limit0; predicate44 resets counters only. Local44 has no ordinary
   recovery branch; cause latch7F6B is set on entry. Direct shared7F68 writes are ordered, not a
   max/OR reduction. */

void f33_advance_second_source_admission_qualification(void)

{
  ushort uVar1;
  ushort uVar2;
  uint32_t puVar3;
  uint uVar4;
  
  puVar3 = 0xfebeb800u;
  if (DAT_febe7f6e == '\0') {
    uVar4 = f33_classify_second_internal_source_observation();
    if (uVar4 != 0x22) {
      return;
    }
    uVar2 = (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x3878)))) + 1;
    (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x3878)))) = uVar2;
    if ((*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x3876)))) < uVar2) {
      (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x3876)))) = uVar2;
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3892))))) = 0x11;
    FUN_0004a3fc();
    return;
  }
  if (DAT_febe7f6e == '\x11') {
    puVar3 = 0xfebeb800u;
    uVar4 = f33_classify_second_internal_source_observation();
    if (uVar4 == 0x22) {
      uVar2 = (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x3878))));
      if (DAT_0002bb1a <= uVar2) {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3892))))) = 0x22;
        FUN_0004a40e();
        return;
      }
      (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x3878)))) = uVar2 + 1;
      if ((ushort)(uVar2 + 1) <= (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x3876))))) {
        return;
      }
      (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x3876)))) = uVar2 + 1;
      return;
    }
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3878)))) = 0;
  }
  else {
    if (DAT_febe7f6e != '\"') {
      return;
    }
    uVar4 = f33_classify_second_internal_source_observation();
    uVar1 = DAT_0002bb1e;
    uVar2 = DAT_0002bb1c;
    if (uVar4 == 0x22) {
      uVar1 = (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x3872))));
      (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3874)))) = 0;
      if (uVar2 <= uVar1) {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3892))))) = 0x44;
        FUN_0004a436();
        return;
      }
      (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x3872)))) = uVar1 + 1;
      if ((ushort)(uVar1 + 1) <= (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x3870))))) {
        return;
      }
      (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x3870)))) = uVar1 + 1;
      return;
    }
    if (uVar4 != 0x11) {
      if (uVar4 != 0x44) {
        return;
      }
      (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3872)))) = 0;
      (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3874)))) = 0;
      return;
    }
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3872)))) = 0;
    if ((*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x3874)))) < uVar1) {
      (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x3874)))) = (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x3874)))) + 1;
      return;
    }
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3878)))) = 0;
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3874)))) = 0;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3892))))) = 0;
  FUN_0004a404();
  return;
}



/* 7F70=5Aonlyunsigned66B8in2304..4096and7F68not2/3;otherwise0. IndependentlypublishedF001. */

void f33_publish_internal_source_observation_admission(void)

{
  if (((DAT_febe66b8 < DAT_0002bb22) || (DAT_0002bb20 < DAT_febe66b8)) ||
     (f33_internal_source_admission_state == '\x02' || f33_internal_source_admission_state == '\x03'
     )) {
    DAT_febe7f70 = 0;
  }
  else {
    DAT_febe7f70 = 0x5a;
  }
  return;
}



/* Set7F6Ffrom7F2C1/2,runthreeconfiguredobservationfamiliesinorder,then7F70admission.
   Shared7F68isorderedlastwriter,notwirepayloadoraggregateOR. Native ordered qualifiers leave first
   local44 intact while later healthy local11 resets shared7F68; not a max/OR reduction or physical
   source claim. */

void f33_update_internal_source_admission_lifecycle(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe7f6f = 0;
  if (DAT_febe7f2c == '\x01' || DAT_febe7f2c == '\x02') {
    DAT_febe7f6f = 0x5a;
  }
  if (DAT_0002bce8 == 'Z') {
    f33_fill_constant_block_49ec6();
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3898))))) = 0;
  }
  else {
    f33_advance_dual_source_admission_qualification();
  }
  if (DAT_0002bce9 == 'Z') {
    f33_fill_constant_block_49eda();
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3898))))) = 0;
  }
  else {
    f33_advance_first_source_admission_qualification();
  }
  if (DAT_0002bcea == 'Z') {
    f33_fill_constant_block_49eec();
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3898))))) = 0;
  }
  else {
    f33_advance_second_source_admission_qualification();
  }
  f33_publish_internal_source_observation_admission();
  return;
}



/* Return44for6764lowqualificationbitsorclosed7F6F;22foravailable66B8outside2304..4096andboth66AE/66B0below2304orbothabove4096;else11.
    */

uint f33_classify_dual_internal_source_observations(void)

{
  if (((DAT_febe6764 & 3) != 0) || (DAT_febe7f6f != 'Z')) {
    return 0x44;
  }
  if (((DAT_febe66ac != '\0') && ((DAT_febe66b8 < DAT_0002bb06 || (DAT_0002bb04 < DAT_febe66b8))))
     && (((DAT_febe66ae < DAT_0002bb0a && (DAT_febe66b0 < DAT_0002bb0a)) ||
         ((DAT_0002bb08 < DAT_febe66ae && (DAT_0002bb08 < DAT_febe66b0)))))) {
    return 0x22;
  }
  return 0x11;
}



/* Requires6764.bit1and7F6F5A,else44;available66B8outside2304..4096plus66AEoutsidefails22;else11. */

uint f33_classify_first_internal_source_observation(void)

{
  if ((((byte)DAT_febe6764 & 2) == 0) || (DAT_febe7f6f != 'Z')) {
    return 0x44;
  }
  if (((DAT_febe66ac != '\0') && ((DAT_febe66b8 < DAT_0002bb06 || (DAT_0002bb04 < DAT_febe66b8))))
     && ((DAT_febe66ae < DAT_0002bb0a || (DAT_0002bb08 < DAT_febe66ae)))) {
    return 0x22;
  }
  return 0x11;
}



/* Requires6764.bit0and7F6F5A,else44;available66B8outside2304..4096plus66B0outsidefails22;else11. */

uint f33_classify_second_internal_source_observation(void)

{
  if ((((byte)DAT_febe6764 & 1) == 0) || (DAT_febe7f6f != 'Z')) {
    return 0x44;
  }
  if (((DAT_febe66ac != '\0') && ((DAT_febe66b8 < DAT_0002bb06 || (DAT_0002bb04 < DAT_febe66b8))))
     && ((DAT_febe66b0 < DAT_0002bb0a || (DAT_0002bb08 < DAT_febe66b0)))) {
    return 0x22;
  }
  return 0x11;
}



void FUN_0004a3fc(void)

{
  f33_internal_source_admission_state = '\x01';
  return;
}



void FUN_0004a404(void)

{
  f33_internal_source_admission_state = '\0';
  DAT_febe7f69 = 0;
  return;
}



void FUN_0004a40e(void)

{
  f33_internal_source_admission_state = '\x02';
  return;
}



void FUN_0004a416(void)

{
  f33_internal_source_admission_state = '\x03';
  DAT_febe7f69 = 0x5a;
  return;
}



void FUN_0004a426(void)

{
  f33_internal_source_admission_state = '\x03';
  DAT_febe7f6a = 0x5a;
  return;
}



void FUN_0004a436(void)

{
  f33_internal_source_admission_state = '\x03';
  DAT_febe7f6b = 0x5a;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4a446(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4a448(void)

{
  return;
}



/* Paired constant publisher: DAT_febe7f94 = 0; and DAT_febe7f95 = 1;; shape-classified from the
   canonical corpus. Target cells not yet named. */

void FUN_0004a44a(void)

{
  DAT_febe7f94 = 0;
  DAT_febe7f95 = 1;
  return;
}



/* Condition E86D=5A and(7F95=0 or E860!=0) and7F94=1 immediately sets7F96/97=5A and clears7F98. On
   release clear7F97 immediately; only clear7F96 once invocation counter reaches ROM317B8. */

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



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4a4ae(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4a4b0(void)

{
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



/* Constant-block fill: 12 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

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



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4a7a8(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4a7aa(void)

{
  return;
}



undefined4 FUN_0004a7ac(void)

{
  if (((DAT_febee81f != '\0') && (DAT_febee828 != 'Z')) && (DAT_febee825 != 'Z')) {
    return 0x5a;
  }
  return 0;
}



void FUN_0004a7d0(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  undefined1 local_10 [8];
  char local_8 [8];
  
  iVar3 = 0;
  do {
    local_8[iVar3] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7fb8u + (uint32_t)(iVar3) * 1u))));
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -7;
    local_10[iVar3] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7fb0u + (uint32_t)(iVar3) * 1u))));
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  iVar3 = 0;
  if (DAT_febe802d == '\0') {
    do {
      local_8[iVar3] = '\0';
      iVar2 = iVar3 + 1;
      iVar1 = iVar3 + -7;
      iVar3 = iVar2;
    } while (((iVar1 < 0) || (iVar2 < 0)));
    local_10[0] = 0;
    local_10[2] = 0;
    DAT_febe7fc2 = 0;
    local_10[4] = 0;
    local_10[6] = 0;
  }
  else {
    do {
      if (local_8[iVar3] == '\x11') {
        local_8[iVar3] = '\0';
      }
      iVar2 = iVar3 + 1;
      iVar1 = iVar3 + -7;
      iVar3 = iVar2;
    } while (((iVar1 < 0) || (iVar2 < 0)));
    if (DAT_febee91c == 0x55aaaa55) {
      iVar3 = 0;
    }
    else if (DAT_febee91c == -0x55aaaa56) {
      iVar3 = 2;
    }
    else if (DAT_febee91c == 0x33333333) {
      iVar3 = 4;
    }
    else {
      iVar3 = 6;
    }
    if ((((local_8[0] == '\"') || (local_8[2] == '\"')) || (local_8[4] == '\"')) ||
       ((local_8[6] == '\"' || (DAT_0002baf4 <= DAT_febe7fc2)))) {
      local_8[iVar3] = '\"';
      local_10[iVar3] = 0x5a;
    }
    else {
      DAT_febe7fc2 = DAT_febe7fc2 + 1;
      local_8[iVar3] = '\x11';
    }
  }
  iVar3 = 0;
  do {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7fb8u + (uint32_t)(iVar3) * 1u)))) = local_8[iVar3];
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -7;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7fb0u + (uint32_t)(iVar3) * 1u)))) = local_10[iVar3];
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  DAT_febe7fc4 = 0;
  return;
}



void FUN_0004a8e6(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  char local_10 [16];
  
  iVar3 = 0;
  do {
    local_10[iVar3 + 8] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7fb8u + (uint32_t)(iVar3) * 1u))));
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -7;
    local_10[iVar3] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7fb0u + (uint32_t)(iVar3) * 1u))));
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  if (DAT_febe802d == '\0') {
    DAT_febe7fc4 = 0;
    iVar3 = 0;
    do {
      local_10[iVar3 + 8] = '\0';
      iVar2 = iVar3 + 1;
      iVar1 = iVar3 + -7;
      iVar3 = iVar2;
    } while (((iVar1 < 0) || (iVar2 < 0)));
    local_10[1] = 0;
    local_10[3] = 0;
    local_10[5] = 0;
    local_10[7] = 0;
    local_10[0] = '\0';
    local_10[2] = 0;
    local_10[4] = 0;
    local_10[6] = 0;
  }
  else if ((DAT_febee812 == '\x11') && (DAT_0002bb28 <= DAT_febee892)) {
    iVar3 = 0;
    do {
      if (local_10[iVar3 + 8] == '\x11') {
        local_10[iVar3 + 8] = '\0';
      }
      iVar2 = iVar3 + 1;
      iVar1 = iVar3 + -7;
      iVar3 = iVar2;
    } while (((iVar1 < 0) || (iVar2 < 0)));
    if (DAT_febee91c == 0x55aaaa55) {
      iVar3 = 1;
    }
    else if (DAT_febee91c == -0x55aaaa56) {
      iVar3 = 3;
    }
    else if (DAT_febee91c == 0x33333333) {
      iVar3 = 5;
    }
    else {
      iVar3 = 7;
    }
    if ((((local_10[9] == '\"') || (local_10[0xb] == '\"')) || (local_10[0xd] == '\"')) ||
       ((local_10[0xf] == '\"' || (DAT_0002baf6 <= DAT_febe7fc4)))) {
      local_10[iVar3 + 8] = '\"';
      local_10[iVar3] = 'Z';
    }
    else {
      DAT_febe7fc4 = DAT_febe7fc4 + 1;
      local_10[iVar3 + 8] = '\x11';
    }
  }
  iVar3 = 0;
  do {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7fb8u + (uint32_t)(iVar3) * 1u)))) = local_10[iVar3 + 8];
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -7;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7fb0u + (uint32_t)(iVar3) * 1u)))) = local_10[iVar3];
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  DAT_febe7fc2 = 0;
  return;
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



void FUN_0004aa5c(void)

{
  char cVar1;
  uint32_t puVar2;
  uchar uVar3;
  int iVar4;
  undefined1 uVar5;
  
  cVar1 = DAT_febe7f2c;
  puVar2 = 0xfebeb800u;
  uVar3 = f33_get_grouped_status_byte(0xb);
  uVar5 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x3840)))));
  if (DAT_0002bcf0 == 'Z') {
    FUN_0004aa40();
  }
  else if (((cVar1 == '\x01' || cVar1 == '\x02') && (uVar3 == '\0')) && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x302a))))) == '\0')) {
    iVar4 = FUN_0004a7ac();
    uVar5 = (undefined1)iVar4;
    if (iVar4 == 0) {
      FUN_0004a7d0();
    }
    else {
      FUN_0004a8e6();
    }
  }
  else if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x38d2))))) != 'Z') {
    FUN_0004aa1c();
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x3840))))) = uVar5;
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



void FUN_0004aae8(void)

{
  char cVar1;
  char cVar2;
  undefined1 uVar3;
  undefined *puVar4;
  int iVar5;
  char cVar6;
  
  cVar2 = DAT_febe80a4;
  puVar4 = ((undefined *)camry_host_ptr(0xfebeb800u));
  cVar6 = DAT_febe687d;
  if (DAT_febe687c != DAT_febe80a4) {
    cVar6 = 'Z';
  }
  if (DAT_0002bcf4 == 'Z') {
    puVar4 = ((undefined *)camry_host_ptr(0xfebeb800u));
    FUN_0006b7d2(((undefined *)camry_host_ptr(0xfebe7fc8u)));
  }
  else if ((cVar6 != '\0') &&
          (puVar4 = ((undefined *)camry_host_ptr(0xfebeb800u)),
          iVar5 = FUN_0006b7f0(((undefined *)camry_host_ptr(0xfebe7fc8u)),((undefined *)camry_host_ptr(0x2baf8u)),&PTR_LAB_000212d0), iVar5 == 0x33)) {
    puVar4[-0x3838] = 0xff;
  }
  cVar1 = puVar4[-0x3838];
  if (cVar1 == '\0') {
    uVar3 = 0;
  }
  else if (cVar1 == '\x11') {
    uVar3 = 1;
  }
  else if (cVar1 == '\"') {
    uVar3 = 2;
  }
  else {
    uVar3 = 3;
  }
  (*((undefined1 *)camry_host_ptr((uint32_t)((int)0xffffb078u + (int)camry_host_addr(puVar4))))) = uVar3;
  (*((char *)camry_host_ptr((uint32_t)((int)0xffffb07cu + (int)camry_host_addr(puVar4))))) = cVar2;
  (*((char *)camry_host_ptr((uint32_t)((int)0xffffb07cu + (int)camry_host_addr((puVar4 + 1)))))) = cVar6;
  (*((char *)camry_host_ptr((uint32_t)((int)0xffffb07au + (int)camry_host_addr((puVar4 + 1)))))) = cVar1;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4abba(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4abbc(void)

{
  return;
}



/* WARNING: Removing unreachable block (ram,0x0004abdc) */

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



void FUN_0004ac28(void)

{
  uint32_t puVar1;
  undefined1 uVar2;
  
  puVar1 = 0xfebeb800u;
  if (DAT_0002bcf8 == 'Z') {
    f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7fd4u)));
  }
  else {
    f33_step_latched_monitor
              ((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7fd4u)),(F33MonitorLimits *)((undefined *)camry_host_ptr(0x2bb00u)),
               (F33TwoSidedMonitorCallbacks *)&PTR_FUN_00029210);
  }
  uVar2 = 1;
  if ((((*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x382c)))) & 0xff) == 0x22) ||
     (uVar2 = 2, ((*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x382c)))) & 0xff00) == 0x2200)) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3820))))) = uVar2;
  }
  return;
}



undefined4 FUN_0004ac7a(void)

{
  int iVar1;
  short sVar2;
  char cVar3;
  char cVar4;
  char cVar5;
  char cVar6;
  int iVar7;
  uint32_t puVar8;
  uchar uVar9;
  undefined4 uVar10;
  uint uVar11;
  short local_24;
  short sStack_22;
  
  puVar8 = 0xfebeb800u;
  uVar9 = f33_get_grouped_status_byte(0x19);
  cVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar8 + (uint32_t)(0x302a)))));
  cVar4 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar8 + (uint32_t)(-0x3898)))));
  cVar5 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar8 + (uint32_t)(-0x374a)))));
  cVar6 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar8 + (uint32_t)(-0x37ae)))));
  uVar11 = (*((uint *)camry_host_ptr((uint32_t)(puVar8 + -0x3750))));
  sVar2 = (*((short *)camry_host_ptr((uint32_t)(puVar8 + -0x37b8))));
  FUN_0006a522((int)(*((short *)camry_host_ptr((uint32_t)(puVar8 + -0x3830)))),&local_24);
  FUN_0006a522((int)sVar2,&sStack_22);
  if ((((uVar9 == '\0') && (cVar3 == '\0')) && (cVar4 == '\0')) &&
     ((cVar5 == '\0' && (cVar6 == '\0')))) {
    iVar7 = (int)DAT_0002bb2c;
    iVar1 = local_24 - iVar7;
    if (((iVar1 < 0 == (local_24 < 0 != iVar7 < 0 && iVar7 < 0 == iVar1 < 0)) &&
        ((uVar11 & 0x3ffff) != 0x20000)) ||
       (iVar7 = (int)DAT_0002bb2e, iVar1 = sStack_22 - iVar7,
       iVar1 < 0 == (sStack_22 < 0 != iVar7 < 0 && iVar7 < 0 == iVar1 < 0))) {
      uVar10 = 0x22;
    }
    else {
      uVar10 = 0x11;
    }
  }
  else {
    uVar10 = 0x44;
  }
  return uVar10;
}



void FUN_0004ad04(void)

{
  FUN_00051cf6(0x23,0x32);
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4ad18(void)

{
  return;
}



/* Constant-block fill: 7 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

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



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4adca(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4adcc(void)

{
  return;
}



void FUN_0004adce(void)

{
  DAT_febe7fec = (DAT_febe800c == '\x01') * '\b' +
                 (DAT_febe8016 == '\x01') * '\x04' +
                 (DAT_febe803b == '\x01') * '\x02' + (DAT_febe803c == '\x01');
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4ae08(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4ae26(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4ae28(void)

{
  return;
}



void FUN_0004ae2a(void)

{
  char cVar1;
  uint32_t puVar2;
  uchar uVar3;
  
  cVar1 = DAT_febe533d;
  puVar2 = 0xfebeb800u;
  if ((f33_internal_source_admission_state < 2) && (DAT_febe7ff1 != DAT_febe533d)) {
    puVar2 = 0xfebeb800u;
    FUN_0007d12a(0x3c,0x3a,8,0,0,((undefined *)camry_host_ptr(0xfebe7ff0u)));
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x380f))))) = cVar1;
  uVar3 = f33_get_application_receive_status(0);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x380e))))) = uVar3;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4ae6e(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4ae70(void)

{
  return;
}



void FUN_0004ae72(void)

{
  char cVar1;
  uint32_t puVar2;
  uchar uVar3;
  
  cVar1 = DAT_febe533e;
  puVar2 = 0xfebeb800u;
  if ((f33_internal_source_admission_state < 2) && (DAT_febe7ffa != DAT_febe533e)) {
    puVar2 = 0xfebeb800u;
    FUN_0007d12a(0x42,0x41,0x10,0,0,((undefined *)camry_host_ptr(0xfebe7ff8u)));
    FUN_0007d12a(0x43, 0x43, 0x20, 0, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x380c))));
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x3806))))) = cVar1;
  uVar3 = f33_get_application_receive_status(1);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x3805))))) = uVar3;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4aed2(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4aed4(void)

{
  return;
}



void FUN_0004aed6(void)

{
  char cVar1;
  uint32_t puVar2;
  uchar uVar3;
  
  cVar1 = DAT_febe533f;
  puVar2 = 0xfebeb800u;
  if ((f33_internal_source_admission_state < 2) && (DAT_febe8000 != DAT_febe533f)) {
    puVar2 = 0xfebeb800u;
    FUN_0007d12a(0x46,0x49,8,0,0,((undefined *)camry_host_ptr(0xfebe7ffcu)));
    FUN_0007d12a(0x47, 0x4a, 4, 4, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x3803))));
    FUN_0007d12a(0x48, 0x4a, 4, 0, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x3802))));
    FUN_0007d12a(0x49, 0x4b, 4, 4, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x3801))));
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x3800))))) = cVar1;
  uVar3 = f33_get_application_receive_status(2);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x37ff))))) = uVar3;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4af68(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4af6a(void)

{
  return;
}



void FUN_0004af6c(void)

{
  char cVar1;
  uint32_t puVar2;
  uchar uVar3;
  
  cVar1 = DAT_febe5340;
  puVar2 = 0xfebeb800u;
  if ((f33_internal_source_admission_state < 2) && (DAT_febe8004 != DAT_febe5340)) {
    puVar2 = 0xfebeb800u;
    FUN_0007d12a(0x53,0x52,8,0,0,((undefined *)camry_host_ptr(0xfebe8002u)));
    FUN_0007d12a(0x55, 0x54, 8, 0, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x37fb))));
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x37fc))))) = cVar1;
  uVar3 = f33_get_application_receive_status(3);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x37fd))))) = uVar3;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4afca(void)

{
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



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4afe8(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4afea(void)

{
  return;
}



void FUN_0004afec(void)

{
  char cVar1;
  uint32_t puVar2;
  uchar uVar3;
  
  cVar1 = DAT_febe534f;
  puVar2 = 0xfebeb800u;
  if ((f33_internal_source_admission_state < 2) && (DAT_febe8008 != DAT_febe534f)) {
    puVar2 = 0xfebeb800u;
    FUN_0007d12a(0x6e,0xc9,3,0,0,((undefined *)camry_host_ptr(0xfebe8006u)));
    FUN_0007d12a(0x6a, 0xc9, 1, 6, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x37f9))));
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x37f8))))) = cVar1;
  uVar3 = f33_get_application_receive_status(5);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x37f7))))) = uVar3;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4b04a(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4b04c(void)

{
  return;
}



void FUN_0004b04e(void)

{
  char cVar1;
  uint32_t puVar2;
  uchar uVar3;
  
  cVar1 = DAT_febe5350;
  puVar2 = 0xfebeb800u;
  if ((f33_internal_source_admission_state < 2) && (DAT_febe800b != DAT_febe5350)) {
    puVar2 = 0xfebeb800u;
    FUN_0007d12a(0x79,0xd1,1,0,0,((undefined *)camry_host_ptr(0xfebe800cu)));
    FUN_0007d12a(0x76, 0xcf, 1, 4, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x37f3))));
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x37f5))))) = cVar1;
  uVar3 = f33_get_application_receive_status(6);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x37f6))))) = uVar3;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4b0ac(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4b0ae(void)

{
  return;
}



void FUN_0004b0b0(void)

{
  char cVar1;
  uint32_t puVar2;
  uchar uVar3;
  
  cVar1 = DAT_febe5351;
  puVar2 = 0xfebeb800u;
  if ((f33_internal_source_admission_state < 2) && (DAT_febe8011 != DAT_febe5351)) {
    puVar2 = 0xfebeb800u;
    FUN_0007d12a(0x82,0xda,0xb,0,1,((undefined *)camry_host_ptr(0xfebe800eu)));
    FUN_0007d12a(0x7c, 0xd7, 6, 2, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x37ee))));
    FUN_0007d12a(0x7e, 0xd8, 1, 3, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x37ed))));
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x37ef))))) = cVar1;
  uVar3 = f33_get_application_receive_status(7);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x37f0))))) = uVar3;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4b12a(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4b12c(void)

{
  return;
}



void FUN_0004b12e(void)

{
  char cVar1;
  uint32_t puVar2;
  uchar uVar3;
  
  cVar1 = DAT_febe5352;
  puVar2 = 0xfebeb800u;
  if ((f33_internal_source_admission_state < 2) && (DAT_febe8017 != DAT_febe5352)) {
    puVar2 = 0xfebeb800u;
    FUN_0007d12a(0x86,0xdf,0x10,0,1,((undefined *)camry_host_ptr(0xfebe8014u)));
    FUN_0007d12a(0x87, 0xe2, 1, 1, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x37ea))));
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x37e9))))) = cVar1;
  uVar3 = f33_get_application_receive_status(8);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x37e8))))) = uVar3;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4b190(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4b192(void)

{
  return;
}



void FUN_0004b194(void)

{
  char cVar1;
  uint32_t puVar2;
  uchar uVar3;
  
  cVar1 = DAT_febe5353;
  puVar2 = 0xfebeb800u;
  if ((f33_internal_source_admission_state < 2) && (DAT_febe801b != DAT_febe5353)) {
    puVar2 = 0xfebeb800u;
    FUN_0007d12a(0x8a,0xe7,8,0,0,((undefined *)camry_host_ptr(0xfebe8019u)));
    FUN_0007d12a(0x8b, 0xe9, 1, 7, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x37e6))));
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x37e5))))) = cVar1;
  uVar3 = f33_get_application_receive_status(9);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x37e4))))) = uVar3;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4b1f2(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4b1f4(void)

{
  return;
}



void FUN_0004b1f6(void)

{
  char cVar1;
  uint32_t puVar2;
  uchar uVar3;
  
  cVar1 = DAT_febe5354;
  puVar2 = 0xfebeb800u;
  if ((f33_internal_source_admission_state < 2) && (DAT_febe8020 != DAT_febe5354)) {
    puVar2 = 0xfebeb800u;
    FUN_0007d12a(0x8d,0xf1,0x10,0,1,((undefined *)camry_host_ptr(0xfebe801eu)));
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x37e0))))) = cVar1;
  uVar3 = f33_get_application_receive_status(10);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x37df))))) = uVar3;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4b23e(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4b240(void)

{
  return;
}



void FUN_0004b242(void)

{
  char cVar1;
  uint32_t puVar2;
  uchar uVar3;
  
  cVar1 = DAT_febe5355;
  puVar2 = 0xfebeb800u;
  if ((f33_internal_source_admission_state < 2) && (DAT_febe802c != DAT_febe5355)) {
    puVar2 = 0xfebeb800u;
    FUN_0007d12a(0x90,0xf7,4,4,0,((undefined *)camry_host_ptr(0xfebe8022u)));
    FUN_0007d12a(0x91, 0xf7, 4, 0, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x37dd))));
    FUN_0007d12a(0x92, 0xf8, 4, 4, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x37dc))));
    FUN_0007d12a(0x93, 0xf8, 1, 3, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x37db))));
    FUN_0007d12a(0x99, 0xfb, 4, 4, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x37da))));
    FUN_0007d12a(0x96, 0xf9, 4, 4, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x37d9))));
    FUN_0007d12a(0x97, 0xf9, 4, 0, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x37d8))));
    FUN_0007d12a(0x94, 0xf8, 2, 1, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x37d7))));
    FUN_0007d12a(0x98, 0xfa, 4, 0, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x37d6))));
    FUN_0007d12a(0x9a, 0xfb, 4, 0, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x37d5))));
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x37d4))))) = cVar1;
  uVar3 = f33_get_application_receive_status(0xb);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x37d3))))) = uVar3;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4b374(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4b376(void)

{
  return;
}



/* Route30classical51E/8;only7F68<2andchanged5356decodefourfields.
   Alwaysconsume5356->802Eandrefreshstatusselector12->802F,evenwithfrozendecode.802EfeedsF13F/BE7E.
   Native ECU steady interval consumes route30 generation2 under gate3 without payload decoding,
   then real58074 publishes generation and duplicated health inputs. */

void f33_refresh_route30_health_inputs(void)

{
  uint32_t puVar1;
  uchar uVar2;
  
  uVar2 = f33_route30_copy_generation;
  puVar1 = 0xfebeb800u;
  if ((f33_internal_source_admission_state < 2) &&
     (f33_route30_consumed_generation != f33_route30_copy_generation)) {
    puVar1 = 0xfebeb800u;
    FUN_0007d12a(0x9d,0xff,1,7,0,((undefined *)camry_host_ptr(0xfebe8031u)));
    FUN_0007d12a(0xa0, 0xff, 4, 0, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x37d0))));
    FUN_0007d12a(0xa6, 0x104, 2, 6, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x37ce))));
    FUN_0007d12a(0xa3, 0x100, 4, 0, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x37cd))));
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x37d2))))) = uVar2;
  uVar2 = f33_get_application_receive_status(0xc);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x37d1))))) = uVar2;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4b40a(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4b40c(void)

{
  return;
}



void FUN_0004b40e(void)

{
  char cVar1;
  uint32_t puVar2;
  uchar uVar3;
  
  cVar1 = DAT_febe5357;
  puVar2 = 0xfebeb800u;
  if ((f33_internal_source_admission_state < 2) && (DAT_febe8039 != DAT_febe5357)) {
    puVar2 = 0xfebeb800u;
    FUN_0007d12a(0xa9,0x10a,2,4,0,((undefined *)camry_host_ptr(0xfebe8038u)));
    FUN_0007d12a(0xab, 0x10b, 0x20, 0, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x37cc))));
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x37c7))))) = cVar1;
  uVar3 = f33_get_application_receive_status(0xd);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x37c6))))) = uVar3;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4b46e(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4b470(void)

{
  return;
}



void FUN_0004b472(void)

{
  char cVar1;
  uint32_t puVar2;
  uchar uVar3;
  
  cVar1 = DAT_febe5358;
  puVar2 = 0xfebeb800u;
  if ((f33_internal_source_admission_state < 2) && (DAT_febe803d != DAT_febe5358)) {
    puVar2 = 0xfebeb800u;
    FUN_0007d12a(0xac,0x10f,1,0,0,((undefined *)camry_host_ptr(0xfebe803bu)));
    FUN_0007d12a(0xad, 0x110, 1, 0, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x37c4))));
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x37c3))))) = cVar1;
  uVar3 = f33_get_application_receive_status(0xe);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x37c2))))) = uVar3;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4b4d0(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4b4d2(void)

{
  return;
}



void FUN_0004b4d4(void)

{
  char cVar1;
  uint32_t puVar2;
  uchar uVar3;
  
  cVar1 = DAT_febe5359;
  puVar2 = 0xfebeb800u;
  if ((f33_internal_source_admission_state < 2) && (DAT_febe8045 != DAT_febe5359)) {
    puVar2 = 0xfebeb800u;
    FUN_0007d12a(0xb1,0x119,8,0,0,((undefined *)camry_host_ptr(0xfebe803fu)));
    FUN_0007d12a(0xb2, 0x11a, 8, 0, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x37c0))));
    FUN_0007d12a(0xb3, 0x11b, 8, 0, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x37bf))));
    FUN_0007d12a(0xb4, 0x11c, 8, 0, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x37be))));
    FUN_0007d12a(0xb5, 0x11d, 8, 0, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x37bd))));
    FUN_0007d12a(0xb6, 0x11e, 8, 0, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x37bc))));
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x37bb))))) = cVar1;
  uVar3 = f33_get_application_receive_status(0xf);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x37ba))))) = uVar3;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4b59a(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4b59c(void)

{
  return;
}



void FUN_0004b59e(void)

{
  char cVar1;
  uint32_t puVar2;
  uchar uVar3;
  
  cVar1 = DAT_febe535b;
  puVar2 = 0xfebeb800u;
  if ((f33_internal_source_admission_state < 2) && (DAT_febe8051 != DAT_febe535b)) {
    puVar2 = 0xfebeb800u;
    FUN_0007d12a(0xbb,0x127,0xc,0,1,((undefined *)camry_host_ptr(0xfebe8048u)));
    FUN_0007d12a(0xbc, 299, 4, 4, 1, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x37b1))));
    FUN_0007d12a(0xbd, 299, 0xc, 0, 1, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x37b6))));
    FUN_0007d12a(0xb8, 0x127, 1, 7, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x37b4))));
    FUN_0007d12a(0xb9, 0x127, 1, 6, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x37b3))));
    FUN_0007d12a(0xba, 0x127, 1, 5, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x37b2))));
    FUN_0007d12a(0xbe, 0x12d, 1, 3, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x37b0))));
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x37af))))) = cVar1;
  uVar3 = f33_get_application_receive_status(0x11);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x37ae))))) = uVar3;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4b686(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4b688(void)

{
  return;
}



void FUN_0004b68a(void)

{
  char cVar1;
  uint32_t puVar2;
  uchar uVar3;
  
  cVar1 = DAT_febe535c;
  puVar2 = 0xfebeb800u;
  if ((f33_internal_source_admission_state < 2) && (DAT_febe8068 != DAT_febe535c)) {
    puVar2 = 0xfebeb800u;
    FUN_0007d12a(0xc3,0x147,0xf,0,0,((undefined *)camry_host_ptr(0xfebe8054u)));
    FUN_0004afcc(0, 0x1a6f, (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x37ac)))), ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x37a4))));
    FUN_0007d12a(0xc5, 0x149, 0xf, 0, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x37aa))));
    FUN_0004afcc(0, 0x1a6f, (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x37aa)))), ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x37a2))));
    FUN_0007d12a(199, 0x14b, 0xf, 0, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x37a8))));
    FUN_0004afcc(0, 0x1a6f, (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x37a8)))), ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x37a0))));
    FUN_0007d12a(0xc9, 0x14d, 0xf, 0, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x37a6))));
    FUN_0004afcc(0, 0x1a6f, (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x37a6)))), ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x379e))));
    FUN_0007d12a(0xc2, 0x147, 1, 7, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x379c))));
    FUN_0007d12a(0xc4, 0x149, 1, 7, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x379b))));
    FUN_0007d12a(0xc6, 0x14b, 1, 7, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x379a))));
    FUN_0007d12a(200, 0x14d, 1, 7, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x3799))));
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x3798))))) = cVar1;
  uVar3 = f33_get_application_receive_status(0x12);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x3797))))) = uVar3;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4b7d2(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4b7d4(void)

{
  return;
}



void FUN_0004b7d6(void)

{
  char cVar1;
  uint32_t puVar2;
  uchar uVar3;
  
  cVar1 = DAT_febe535d;
  puVar2 = 0xfebeb800u;
  if ((f33_internal_source_admission_state < 2) && (DAT_febe806e != DAT_febe535d)) {
    puVar2 = 0xfebeb800u;
    FUN_0007d12a(0xce,0x14f,1,3,0,((undefined *)camry_host_ptr(0xfebe806cu)));
    FUN_0007d12a(0xca, 0x14f, 1, 7, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x3793))));
    FUN_0007d12a(0xd0, 0x151, 1, 3, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x3790))));
    FUN_0007d12a(0xd1, 0x151, 10, 0, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x3796))));
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x3792))))) = cVar1;
  uVar3 = f33_get_application_receive_status(0x13);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x3791))))) = uVar3;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4b86a(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4b86c(void)

{
  return;
}



void FUN_0004b86e(void)

{
  char cVar1;
  uint32_t puVar2;
  uchar uVar3;
  
  cVar1 = DAT_febe535e;
  puVar2 = 0xfebeb800u;
  if ((f33_internal_source_admission_state < 2) && (DAT_febe8077 != DAT_febe535e)) {
    puVar2 = 0xfebeb800u;
    FUN_0007d12a(0xd4,0x158,0x10,0,1,((undefined *)camry_host_ptr(0xfebe8072u)));
    FUN_0007d12a(0xd5, 0x15a, 0x10, 0, 1, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x378c))));
    FUN_0007d12a(0xd3, 0x157, 1, 3, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x378a))));
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x3789))))) = cVar1;
  uVar3 = f33_get_application_receive_status(0x14);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x3788))))) = uVar3;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4b8f0(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4b8f2(void)

{
  return;
}



void FUN_0004b8f4(void)

{
  char cVar1;
  uint32_t puVar2;
  uchar uVar3;
  
  cVar1 = DAT_febe535f;
  puVar2 = 0xfebeb800u;
  if ((f33_internal_source_admission_state < 2) && (DAT_febe8080 != DAT_febe535f)) {
    puVar2 = 0xfebeb800u;
    FUN_0007d12a(0xd7,0x15f,5,3,0,((undefined *)camry_host_ptr(0xfebe8079u)));
    FUN_0007d12a(0xd8, 0x15f, 1, 2, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x3786))));
    FUN_0007d12a(0xd9, 0x15f, 1, 1, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x3785))));
    FUN_0007d12a(0xdb, 0x160, 6, 2, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x3784))));
    FUN_0007d12a(0xdd, 0x160, 1, 0, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x3783))));
    FUN_0007d12a(0xde, 0x161, 1, 6, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x3782))));
    FUN_0007d12a(0xdf, 0x161, 1, 5, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x3781))));
    FUN_0007d12a(0xe0, 0x161, 4, 0, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x377e))));
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x3780))))) = cVar1;
  uVar3 = f33_get_application_receive_status(0x15);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x377f))))) = uVar3;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4b9f0(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4b9f2(void)

{
  return;
}



void FUN_0004b9f4(void)

{
  char cVar1;
  uint32_t puVar2;
  uchar uVar3;
  
  cVar1 = DAT_febe5360;
  puVar2 = 0xfebeb800u;
  if ((f33_internal_source_admission_state < 2) && (DAT_febe8097 != DAT_febe5360)) {
    puVar2 = 0xfebeb800u;
    FUN_0007d12a(0xe3,0x167,1,7,0,((undefined *)camry_host_ptr(0xfebe8090u)));
    FUN_0007d12a(0xe4, 0x167, 1, 6, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x376f))));
    FUN_0007d12a(0xe5, 0x167, 10, 0, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x377c))));
    FUN_0004afcc(0, 0x200, (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x377c)))), ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x3776))));
    FUN_0007d12a(0xe6, 0x169, 1, 7, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x376e))));
    FUN_0007d12a(0xe7, 0x169, 1, 6, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x376d))));
    FUN_0007d12a(0xe8, 0x169, 10, 0, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x377a))));
    FUN_0004afcc(0, 0x200, (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x377a)))), ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x3774))));
    FUN_0007d12a(0xe9, 0x16b, 1, 7, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x376c))));
    FUN_0007d12a(0xea, 0x16b, 1, 6, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x376b))));
    FUN_0007d12a(0xeb, 0x16b, 10, 0, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x3778))));
    FUN_0004afcc(0, 0x200, (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x3778)))), ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x3772))));
    FUN_0007d12a(0xf1, 0x183, 4, 4, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x376a))));
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x3769))))) = cVar1;
  uVar3 = f33_get_application_receive_status(0x16);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x3768))))) = uVar3;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4bb5e(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4bb60(void)

{
  return;
}



void FUN_0004bb62(void)

{
  char cVar1;
  uint32_t puVar2;
  uchar uVar3;
  undefined1 uStack_9;
  
  cVar1 = DAT_febe5361;
  puVar2 = 0xfebeb800u;
  uStack_9 = DAT_febe80a0;
  if ((f33_internal_source_admission_state < 2) && (DAT_febe80a4 != DAT_febe5361)) {
    puVar2 = 0xfebeb800u;
    FUN_0007d12a(0xf6,0x188,0x10,0,0,((undefined *)camry_host_ptr(0xfebe809au)));
    FUN_0007d12a(0xf7, 0x18a, 0x10, 0, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x3764))));
    FUN_0007d12a(0xf3,0x187,1,7,0,&uStack_9);
    FUN_0007d12a(0xf4, 0x187, 1, 6, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x375f))));
    FUN_0007d12a(0xf9, 0x1a3, 4, 4, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x375d))));
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x375c))))) = cVar1;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x3760))))) = uStack_9;
  uVar3 = f33_get_application_receive_status(0x17);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x375b))))) = uVar3;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4bc24(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4bc26(void)

{
  return;
}



void FUN_0004bc28(void)

{
  char cVar1;
  uint32_t puVar2;
  uchar uVar3;
  
  cVar1 = DAT_febe5362;
  puVar2 = 0xfebeb800u;
  if ((f33_internal_source_admission_state < 2) && (DAT_febe80a6 != DAT_febe5362)) {
    puVar2 = 0xfebeb800u;
    FUN_0007d12a(0xfb,0x1a9,8,0,0,((undefined *)camry_host_ptr(0xfebe80a8u)));
    FUN_0007d12a(0xfc, 0x1aa, 8, 0, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x3757))));
    FUN_0007d12a(0xfd, 0x1ac, 8, 0, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x3756))));
    FUN_0007d12a(0xfe, 0x1ad, 8, 0, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x3755))));
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x375a))))) = cVar1;
  uVar3 = f33_get_application_receive_status(0x18);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x3759))))) = uVar3;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4bcbc(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4bcbe(void)

{
  return;
}



void FUN_0004bcc0(void)

{
  char cVar1;
  uint32_t puVar2;
  uchar uVar3;
  
  cVar1 = DAT_febe5363;
  puVar2 = 0xfebeb800u;
  if ((f33_internal_source_admission_state < 2) && (DAT_febe80b5 != DAT_febe5363)) {
    puVar2 = 0xfebeb800u;
    FUN_0007d12a(0xff,0x1b1,0x12,6,1,((undefined *)camry_host_ptr(0xfebe80acu)));
    FUN_0007d12a(0x100, 0x1b3, 1, 5, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x374c))));
    FUN_0007d12a(0x101, 0x1b3, 0x12, 0, 1, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x3750))));
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x374b))))) = cVar1;
  uVar3 = f33_get_application_receive_status(0x19);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x374a))))) = uVar3;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4bd42(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4bd44(void)

{
  return;
}



void FUN_0004bd46(void)

{
  char cVar1;
  uint32_t puVar2;
  uchar uVar3;
  
  cVar1 = DAT_febe5364;
  puVar2 = 0xfebeb800u;
  if ((f33_internal_source_admission_state < 2) && (DAT_febe80c8 != DAT_febe5364)) {
    puVar2 = 0xfebeb800u;
    FUN_0007d12a(0x105,0x1ba,6,0,0,((undefined *)camry_host_ptr(0xfebe80bcu)));
    FUN_0007d12a(0x106, 0x1bb, 0x10, 0, 1, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x3748))));
    FUN_0007d12a(0x107, 0x1bd, 1, 7, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x3735))));
    FUN_0007d12a(0x108, 0x1bd, 3, 4, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x3742))));
    FUN_0007d12a(0x109, 0x1bd, 1, 2, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x3740))));
    FUN_0007d12a(0x10a, 0x1bd, 2, 0, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x373f))));
    FUN_0007d12a(0x10b, 0x1be, 2, 6, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x373e))));
    FUN_0007d12a(0x10c, 0x1be, 6, 0, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x373d))));
    FUN_0007d12a(0x10d, 0x1bf, 8, 0, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x373c))));
    FUN_0007d12a(0x10e, 0x1c0, 8, 0, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x373b))));
    FUN_0007d12a(0x10f, 0x1c1, 1, 7, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x373a))));
    FUN_0007d12a(0x110, 0x1c1, 1, 5, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x3734))));
    FUN_0007d12a(0x111, 0x1c1, 3, 0, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x3736))));
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x3738))))) = cVar1;
  uVar3 = f33_get_application_receive_status(0x1a);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x3737))))) = uVar3;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4becc(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4bece(void)

{
  return;
}



void FUN_0004bed0(void)

{
  char cVar1;
  uint32_t puVar2;
  uchar uVar3;
  
  cVar1 = DAT_febe5365;
  puVar2 = 0xfebeb800u;
  if ((f33_internal_source_admission_state < 2) && (DAT_febe80cf != DAT_febe5365)) {
    puVar2 = 0xfebeb800u;
    FUN_0007d12a(0x114,0x1d7,8,0,0,((undefined *)camry_host_ptr(0xfebe80cdu)));
    FUN_0007d12a(0x115, 0x1d8, 8, 0, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x3732))));
    FUN_0007d12a(0x116, 0x1d9, 8, 0, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x372f))));
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x3731))))) = cVar1;
  uVar3 = f33_get_application_receive_status(0x1b);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x3730))))) = uVar3;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4bf4a(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4bf4c(void)

{
  return;
}



void FUN_0004bf4e(void)

{
  char cVar1;
  uint32_t puVar2;
  uchar uVar3;
  
  cVar1 = DAT_febe5366;
  puVar2 = 0xfebeb800u;
  if ((f33_internal_source_admission_state < 2) && (DAT_febe80d4 != DAT_febe5366)) {
    puVar2 = 0xfebeb800u;
    FUN_0007d12a(0x118,0x1df,3,4,0,((undefined *)camry_host_ptr(0xfebe80d2u)));
    FUN_0007d12a(0x119, 0x1df, 4, 0, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x372d))));
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x372c))))) = cVar1;
  uVar3 = f33_get_application_receive_status(0x1c);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x372b))))) = uVar3;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4bfae(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4bfb0(void)

{
  return;
}



void FUN_0004bfb2(void)

{
  char cVar1;
  uint32_t puVar2;
  uchar uVar3;
  
  cVar1 = DAT_febe5367;
  puVar2 = 0xfebeb800u;
  if ((f33_internal_source_admission_state < 2) && (DAT_febe80d7 != DAT_febe5367)) {
    puVar2 = 0xfebeb800u;
    FUN_0007d12a(0x11a,0x1e0,4,0,0,((undefined *)camry_host_ptr(0xfebe80d6u)));
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x3729))))) = cVar1;
  uVar3 = f33_get_application_receive_status(0x1d);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x3728))))) = uVar3;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4bff8(void)

{
  return;
}



/* Single constant publisher: DAT_febe8143 = 0; Shape-classified from the canonical corpus; the
   target cell is not yet named, so the written state's meaning is unknown. */

void FUN_0004bffa(void)

{
  DAT_febe8143 = 0;
  return;
}


