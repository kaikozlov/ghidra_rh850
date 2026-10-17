#include "common.h"


/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_5802a(void)

{
  return;
}



/* Constant-block fill: 12 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

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



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_58070(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_58802(void)

{
  return;
}



/* Run cold software initialization58828, then request redundant8C08=A55A. This runs inside666BC
   before timers; it is not physical reset or an aggregate hardware-success gate. */

void f33_initialize_application_and_request_first_generation(void)

{
  f33_initialize_cold_application_state();
  FUN_0005889a();
  return;
}



/* Ordered common initializer:59448 ECU work state, FDC14\u2192BF97A control work state, then5C6D8
   copies control publications into ECU views. Both cold58828 and warm5886C call this; it does not
   invoke the low-level666BC hardware/NvM startup sequence. Ordered common initializer:59448 ECU
   work state, FDC14→BF97A control work state, then5C6D8 copies control publications into ECU
   views. */

void f33_initialize_generated_application_components(void)

{
  f33_initialize_ecu_application_work_state();
  FUN_000fdc14();
  f33_snapshot_initialized_control_publications();
  return;
}



/* Clear restart token, redundant restart classification8C1A/B/C, counters8C16/17 and cadence8C19.
   Initialize cold ECU acquisition58C9A and cold control-retained cellsBF91E viaFDC00, then
   common58814. This path differs from warm5886C. */

void f33_initialize_cold_application_state(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  f33_publish_redundant_u16(0,((undefined *)camry_host_ptr(0xfebe8c08u)),(ushort *)((undefined *)camry_host_ptr(0xfebe8c0au)),(ushort *)((undefined *)camry_host_ptr(0xfebe8c14u)));
  f33_publish_redundant_u8('\0', ((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x2be6))), ((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x2be5))), ((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x2be4))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x2bea))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x2be9))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x2be7))))) = 0;
  f33_initialize_cold_ecu_input_state();
  FUN_000fdc00();
  f33_initialize_generated_application_components();
  return;
}



/* Clear four task last-mode words8C00/02/04/06 and set inverses8C0C/0E/10/12=FFFF, then
   common58814. Do not rerun58C9A/BF91E or reset task cadence/restart token. BF97A resets both live
   mode and publishedE8CC to0; acquired inputs and cold-owned health generation history survive.
   Composed warm restart resets control/mode/monitor state and published mode, preserves acquired
   samples, cadence, cold-owned health history and lower NvM busy state. */

void f33_reinitialize_application_for_foreground_restart(void)

{
  DAT_febe8c00 = 0;
  DAT_febe8c02 = 0;
  DAT_febe8c04 = 0;
  DAT_febe8c06 = 0;
  DAT_febe8c0c = 0xffff;
  DAT_febe8c0e = 0xffff;
  DAT_febe8c10 = 0xffff;
  DAT_febe8c12 = 0xffff;
  f33_initialize_generated_application_components();
  return;
}



void FUN_0005889a(void)

{
  f33_publish_redundant_u16(0xa55a,((undefined *)camry_host_ptr(0xfebe8c08u)),(ushort *)((undefined *)camry_host_ptr(0xfebe8c0au)),(ushort *)((undefined *)camry_host_ptr(0xfebe8c14u)));
  return;
}



undefined4 FUN_000588b6(void)

{
  int iVar1;
  undefined4 uVar2;
  uchar uStack_5;
  
  iVar1 = f33_vote_redundant_u8(((undefined *)camry_host_ptr(0xfebe8c1au)),((undefined *)camry_host_ptr(0xfebe8c1bu)),((undefined *)camry_host_ptr(0xfebe8c1cu)),&uStack_5);
  if ((uStack_5 == 0xa5) || (iVar1 == -0xd)) {
    uVar2 = 0x5a;
  }
  else {
    uVar2 = 0;
  }
  return uVar2;
}



/* Save PMR; setFFC0; copy ECU inputs through5C7B6 and control inputs throughFDC28; restore
   entryPMR. The caller subsequently runs CH1 transition/steady workers. */

void f33_snapshot_ch1_inputs(void)

{
  undefined4 uVar1;
  
  uVar1 = FUN_000701a0();
  FUN_000701a6(0xffc0);
  FUN_0005c7b6();
  f33_copy_cell_block_c1b24();
  FUN_000701a6(uVar1);
  return;
}



/* Save PMR; FFC0 protects5CA3A/FDC3C acquisition snapshot; FF80 protects5CF1C/FDC50 control
   snapshot; restore entryPMR. These are ordered windows, not an all-task atomic generation. */

void f33_snapshot_ch2_inputs(void)

{
  undefined4 uVar1;
  
  uVar1 = FUN_000701a0();
  FUN_000701a6(0xffc0);
  f33_snapshot_ecu_ch2_acquisition();
  FUN_000fdc3c();
  FUN_000701a6(0xff80);
  f33_copy_cell_block_5cf1c();
  FUN_000fdc50();
  FUN_000701a6(uVar1);
  return;
}



void FUN_00058ad8(void)

{
  int iVar1;
  uchar uStack_11;
  
  iVar1 = f33_vote_redundant_u8(((undefined *)camry_host_ptr(0xfebe8c1au)),((undefined *)camry_host_ptr(0xfebe8c1bu)),((undefined *)camry_host_ptr(0xfebe8c1cu)),&uStack_11);
  if (iVar1 != 0) {
    if (iVar1 != -0xc && iVar1 != -0xb) {
      uStack_11 = 0xa5;
    }
    f33_publish_redundant_u8(uStack_11,((undefined *)camry_host_ptr(0xfebe8c1au)),((undefined *)camry_host_ptr(0xfebe8c1bu)),((undefined *)camry_host_ptr(0xfebe8c1cu)));
  }
  return;
}



/* Save PMR; FFC0\u21925D12C/FDC64 acquisition views, FF80\u21925D5E0/FDC78 control views,
   FF00\u21925D6DC/FDC8C monitor/health/service views; restore entryPMR. Not one interrupt-free
   snapshot and not physical input freshness. FFC0→5D12C/FDC64 acquisition views,
   FF80→5D5E0/FDC78 control views, FF00→5D6DC/FDC8C monitor/health/service views; */

void f33_snapshot_foreground_inputs(void)

{
  undefined4 uVar1;
  
  uVar1 = FUN_000701a0();
  FUN_000701a6(0xffc0);
  f33_snapshot_ecu_foreground_acquisition();
  FUN_000fdc64();
  FUN_000701a6(0xff80);
  f33_copy_cell_block_5d5e0();
  FUN_000fdc78();
  FUN_000701a6(0xff00);
  f33_snapshot_monitor_inputs();
  FUN_000fdc8c();
  FUN_000701a6(uVar1);
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



/* Cold-only ECU input/status initialization before generated components. Both six-halfword
   acquisition banks822C/8238 start8000; many status/validity cells have explicit nonzero defaults.
   Not a blanket zeroing operation and not called by warm5886C. */

void f33_initialize_cold_ecu_input_state(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = 0;
  do {
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe822cu + (uint32_t)(iVar3) * 2u)))) = 0x8000;
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -5;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe8238u + (uint32_t)(iVar3) * 2u)))) = 0x8000;
    iVar1 = iVar3 + -5;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  DAT_febe81f4 = 0;
  DAT_febe81f6 = 0;
  DAT_febe81f8 = 0;
  DAT_febe81fa = 0;
  DAT_febe81fc = 0;
  DAT_febe81fe = 0;
  DAT_febe8200 = 0;
  DAT_febe8202 = 0;
  DAT_febe8204 = 0;
  DAT_febe8206 = 0;
  DAT_febe8208 = 0;
  DAT_febe820a = 0;
  DAT_febe8b04 = 0;
  DAT_febe820c = 0;
  DAT_febe820e = 0;
  DAT_febe8210 = 0;
  DAT_febe8212 = 0;
  DAT_febe8214 = 0;
  DAT_febe8216 = 0;
  DAT_febe8218 = 0;
  DAT_febe821a = 0;
  DAT_febe821c = 0;
  DAT_febe821e = 0;
  DAT_febe8220 = 0;
  DAT_febe8222 = 0;
  DAT_febe8224 = 0;
  DAT_febe8226 = 0;
  DAT_febe8228 = 0;
  DAT_febe82aa = 3;
  DAT_febe82a0 = 1;
  DAT_febe82ae = 4;
  DAT_febe82a1 = 0x5a;
  DAT_febe82a2 = 0x5a;
  DAT_febe82ab = 0;
  DAT_febe82ac = 0;
  DAT_febe82ad = 0;
  DAT_febe82b6 = 0;
  DAT_febe82b8 = 0;
  DAT_febe81cc = 0x5a;
  DAT_febe7f4c = 0x5a;
  DAT_febe7f60 = 0;
  DAT_febe7f4d = 0;
  DAT_febe7f4e = 0;
  DAT_febe7f62 = 0;
  DAT_febe7f4f = 0;
  DAT_febe7f64 = 0;
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7f50u + (uint32_t)(iVar3) * 1u)))) = 0x5a;
    iVar1 = iVar3 + -2;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  DAT_febe7f5d = 0xff;
  DAT_febe7f5e = 0xff;
  DAT_febe7f5f = 0xff;
  DAT_febe7f53 = 0;
  DAT_febe7f54 = 0;
  DAT_febe7f55 = 0;
  DAT_febe7f56 = 0;
  DAT_febe7f57 = 0;
  DAT_febe7f58 = 0;
  DAT_febe7f59 = 0;
  DAT_febe7f5a = 0;
  DAT_febe7f5b = 0;
  DAT_febe7f5c = 0;
  iVar3 = 0;
  do {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7f2cu + (uint32_t)(iVar3) * 1u)))) = 0;
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -1;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  iVar3 = 0;
  do {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7f2eu + (uint32_t)(iVar3) * 1u)))) = 0;
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -1;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  DAT_febe7f3a = 0;
  DAT_febe7f3c = 0;
  DAT_febe7f3e = 0;
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe7f40u)) + iVar3 * 2) = 0;
    iVar1 = iVar3 + -1;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  iVar3 = 0;
  do {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7f32u + (uint32_t)(iVar3) * 1u)))) = 0;
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -1;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe7f44u)) + iVar3 * 2) = 0;
    iVar1 = iVar3 + -1;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  DAT_febe7f48 = 0;
  DAT_febe7f4a = 0;
  DAT_febe7f34 = 0;
  iVar3 = 0;
  do {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7f35u + (uint32_t)(iVar3) * 1u)))) = 0;
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -1;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  DAT_febe801b = 0;
  DAT_febe801a = 0;
  DAT_febe8019 = 0;
  DAT_febe7ff1 = 0;
  DAT_febe7ff0 = 0;
  DAT_febe8045 = 0;
  DAT_febe8013 = 0;
  DAT_febe8012 = 0;
  DAT_febe800e = 0;
  DAT_febe8011 = 0;
  DAT_febe800d = 0;
  DAT_febe800c = 0;
  DAT_febe800b = 0;
  DAT_febe80d7 = 0;
  DAT_febe80d6 = 0;
  DAT_febe80d4 = 0;
  DAT_febe80d2 = 0;
  DAT_febe80cf = 0;
  DAT_febe80cc = 0;
  DAT_febe80cb = 0;
  DAT_febe80ca = 0;
  DAT_febe80c8 = 0;
  DAT_febe80c7 = 0;
  DAT_febe80c6 = 0;
  DAT_febe80c5 = 0;
  DAT_febe80c4 = 0;
  DAT_febe80c3 = 0;
  DAT_febe80c2 = 0;
  DAT_febe80c1 = 0;
  DAT_febe80c0 = 0;
  DAT_febe80bf = 0;
  DAT_febe80be = 0;
  DAT_febe80ba = 0;
  DAT_febe80b8 = 0;
  DAT_febe80bd = 0;
  DAT_febe80bc = 0;
  DAT_febe80b5 = 0;
  DAT_febe80b4 = 0;
  DAT_febe80ac = 0;
  DAT_febe80ab = 0;
  DAT_febe80aa = 0;
  DAT_febe80a9 = 0;
  DAT_febe80a8 = 0;
  DAT_febe80a6 = 0;
  DAT_febe80a4 = 0;
  DAT_febe80a3 = 0;
  DAT_febe809e = 0;
  DAT_febe809c = 0;
  DAT_febe809a = 0;
  DAT_febe8097 = 0;
  DAT_febe8096 = 0;
  DAT_febe808e = 0;
  DAT_febe808c = 0;
  DAT_febe808a = 0;
  DAT_febe8088 = 0;
  DAT_febe8095 = 0;
  DAT_febe8092 = 0;
  DAT_febe8090 = 0;
  DAT_febe8082 = 0;
  DAT_febe8080 = 0;
  DAT_febe807f = 0;
  DAT_febe807e = 0;
  DAT_febe807d = 0;
  DAT_febe807c = 0;
  DAT_febe807b = 0;
  DAT_febe807a = 0;
  DAT_febe8079 = 0;
  DAT_febe8077 = 0;
  DAT_febe8076 = 0;
  DAT_febe8074 = 0;
  DAT_febe8072 = 0;
  DAT_febe806a = 0;
  DAT_febe806e = 0;
  DAT_febe806d = 0;
  DAT_febe806c = 0;
  DAT_febe8068 = 0;
  DAT_febe8067 = 0;
  DAT_febe8066 = 0;
  DAT_febe8065 = 0;
  DAT_febe8064 = 0;
  DAT_febe8062 = 0;
  DAT_febe8060 = 0;
  DAT_febe805e = 0;
  DAT_febe805c = 0;
  DAT_febe8051 = 0;
  DAT_febe804a = 0;
  DAT_febe804f = 0;
  DAT_febe8048 = 0;
  DAT_febe804e = 0;
  DAT_febe804d = 0;
  DAT_febe804c = 0;
  DAT_febe803d = 0;
  DAT_febe803c = 0;
  DAT_febe803b = 0;
  DAT_febe8039 = 0;
  DAT_febe8038 = 0;
  DAT_febe8033 = 0;
  DAT_febe8032 = 0;
  DAT_febe8031 = 0;
  DAT_febe8030 = 0;
  f33_route30_consumed_generation = '\0';
  DAT_febe802c = 0;
  DAT_febe8026 = 0;
  DAT_febe8020 = 0;
  DAT_febe801e = 0;
  DAT_febe8017 = 0;
  DAT_febe8016 = 0;
  DAT_febe8014 = 0;
  DAT_febe8008 = 0;
  DAT_febe8007 = 0;
  DAT_febe8006 = 0;
  DAT_febe8004 = 0;
  DAT_febe8000 = 0;
  DAT_febe7ffa = 0;
  DAT_febe7f37 = 0;
  DAT_febe687d = 0;
  DAT_febe687c = 0;
  DAT_febe8044 = 0xff;
  DAT_febe8043 = 0xff;
  DAT_febe8042 = 0xff;
  DAT_febe8041 = 0xff;
  DAT_febe8040 = 0xff;
  DAT_febe803f = 0xff;
  DAT_febe80d1 = 0xff;
  DAT_febe80ce = 0xff;
  DAT_febe8c50 = 0;
  DAT_febe8c4f = 0;
  DAT_febe8c4e = 0;
  DAT_febe8c4d = 0;
  DAT_febe8c4c = 0;
  DAT_febe8c4b = 0;
  DAT_febe8c4a = 0;
  DAT_febe8c49 = 0;
  DAT_febe8c48 = 0;
  DAT_febe8c2e = 0;
  DAT_febe8c2c = 0;
  DAT_febe8c47 = 0;
  DAT_febe8c46 = 0;
  DAT_febe8c45 = 0;
  DAT_febe8c44 = 0;
  DAT_febe8c43 = 0;
  DAT_febe8c42 = 0;
  DAT_febe8c41 = 0;
  DAT_febe8c40 = 0;
  DAT_febe8c3f = 0;
  DAT_febe8c2a = 0;
  DAT_febe8c3e = 0;
  DAT_febe8c3d = 0;
  DAT_febe8c3b = 0;
  DAT_febe8c3a = 0;
  DAT_febe8c20 = 0;
  DAT_febe8c39 = 0;
  DAT_febe8c28 = 0;
  DAT_febe8c38 = 0;
  DAT_febe8c36 = 0;
  DAT_febe8c35 = 0;
  DAT_febe8c26 = 0;
  DAT_febe8c34 = 0;
  DAT_febe8c24 = 0;
  DAT_febe8c33 = 0;
  DAT_febe8c32 = 0;
  DAT_febe7ffc = 0xff;
  DAT_febe8002 = 0xff;
  DAT_febe8005 = 0xff;
  f33_route31_numeric_scalar = 0xffffffff;
  DAT_febe80cd = 0xff;
  DAT_febe7f94 = 0;
  DAT_febe7f98 = 0;
  DAT_febe7f96 = 0;
  DAT_febe7f97 = 0;
  DAT_febe7ff8 = 0xffff;
  DAT_febe7ffd = 0xf;
  DAT_febe7ffe = 0xf;
  DAT_febe7fff = 0xf;
  DAT_febe8022 = 0xf;
  DAT_febe8023 = 0xf;
  DAT_febe8024 = 0xf;
  DAT_febe8027 = 0xf;
  DAT_febe8028 = 0xf;
  DAT_febe802a = 0xf;
  DAT_febe802b = 0xf;
  DAT_febe8029 = 3;
  DAT_febe8054 = 0x1a6f;
  DAT_febe8056 = 0x1a6f;
  DAT_febe8058 = 0x1a6f;
  DAT_febe805a = 0x1a6f;
  DAT_febe7ff4 = 0xffffff;
  DAT_febe8084 = 0x200;
  DAT_febe8086 = 0x200;
  DAT_febe8c3c = 1;
  DAT_febe8c37 = 1;
  DAT_febe7ffb = 1;
  DAT_febe8001 = 1;
  DAT_febe8003 = 1;
  DAT_febe8009 = 1;
  DAT_febe8018 = 1;
  DAT_febe8021 = 1;
  DAT_febe8025 = 1;
  DAT_febe802d = 1;
  f33_route30_receive_status = '\x01';
  DAT_febe803a = 1;
  DAT_febe803e = 1;
  DAT_febe8050 = 1;
  DAT_febe8052 = 1;
  DAT_febe8069 = 1;
  DAT_febe806f = 1;
  DAT_febe8070 = 1;
  DAT_febe8078 = 1;
  DAT_febe8081 = 1;
  DAT_febe8091 = 1;
  DAT_febe8093 = 1;
  DAT_febe8094 = 1;
  DAT_febe8098 = 1;
  DAT_febe80a0 = 1;
  DAT_febe80a1 = 1;
  DAT_febe80a2 = 1;
  DAT_febe80a5 = 1;
  DAT_febe80a7 = 1;
  DAT_febe80b6 = 1;
  DAT_febe80c9 = 1;
  DAT_febe80d0 = 1;
  DAT_febe80d5 = 1;
  DAT_febe80d8 = 1;
  DAT_febe800a = 1;
  DAT_febe8010 = 1;
  DAT_febe8046 = 1;
  DAT_febe7ff2 = 1;
  DAT_febe801c = 1;
  DAT_febe7f95 = 1;
  DAT_febe80b0 = 0xfffe0000;
  DAT_febe816e = 0;
  DAT_febe8151 = 0;
  DAT_febe8150 = 0;
  DAT_febe814f = 0;
  DAT_febe814e = 0;
  DAT_febe814d = 0;
  DAT_febe814c = 0;
  DAT_febe814b = 0;
  DAT_febe814a = 0;
  DAT_febe8149 = 0;
  DAT_febe8148 = 0;
  DAT_febe8147 = 0;
  DAT_febe8146 = 0;
  DAT_febe8178 = 0;
  DAT_febe8145 = 0;
  DAT_febe8144 = 0;
  DAT_febe816c = 0;
  DAT_febe8142 = 0;
  DAT_febe8141 = 0;
  DAT_febe8140 = 0;
  DAT_febe816a = 0;
  DAT_febe813f = 0;
  DAT_febe813e = 1;
  DAT_febe813d = 0;
  DAT_febe813c = 0;
  DAT_febe8174 = 0;
  DAT_febe813b = 0;
  DAT_febe8168 = 0;
  DAT_febe813a = 0;
  DAT_febe8139 = 0;
  DAT_febe8166 = 0;
  DAT_febe8138 = 0;
  DAT_febe8164 = 0;
  DAT_febe8137 = 0;
  DAT_febe8136 = 0;
  DAT_febe8135 = 0;
  DAT_febe8134 = 0;
  DAT_febe8133 = 0;
  DAT_febe8132 = 0;
  DAT_febe8131 = 0;
  DAT_febe8130 = 0;
  DAT_febe812f = 1;
  DAT_febe8162 = 0;
  DAT_febe812e = 1;
  DAT_febe812d = 0;
  DAT_febe8160 = 0;
  DAT_febe8129 = 0;
  DAT_febe8128 = 0;
  DAT_febe8127 = 0;
  DAT_febe8126 = 0;
  DAT_febe8125 = 0;
  DAT_febe8124 = 0;
  DAT_febe8123 = 0;
  DAT_febe8122 = 0;
  DAT_febe8121 = 0;
  DAT_febe8120 = 0;
  DAT_febe811f = 0;
  DAT_febe811e = 0;
  DAT_febe811d = 0;
  DAT_febe815e = 0;
  DAT_febe811c = 0;
  DAT_febe811b = 0;
  DAT_febe811a = 0;
  DAT_febe8119 = 0;
  DAT_febe8118 = 0;
  DAT_febe815c = 0;
  DAT_febe8170 = 0;
  DAT_febe815a = 0;
  DAT_febe8117 = 0;
  DAT_febe8116 = 0;
  DAT_febe8115 = 0;
  DAT_febe8114 = 0;
  DAT_febe8113 = 0;
  DAT_febe8112 = 0;
  DAT_febe8111 = 0;
  DAT_febe8110 = 0;
  DAT_febe810f = 0;
  DAT_febe810e = 0;
  DAT_febe810d = 0;
  DAT_febe810c = 0;
  DAT_febe810b = 0;
  DAT_febe810a = 0;
  DAT_febe8109 = 0;
  DAT_febe8108 = 0;
  DAT_febe80dc = 0;
  DAT_febe80dd = 0;
  DAT_febe80de = 0;
  DAT_febe80df = 1;
  DAT_febe80e0 = 1;
  DAT_febe80e1 = 1;
  DAT_febe80e2 = 1;
  DAT_febe80e3 = 0;
  DAT_febe8152 = 0;
  DAT_febe8154 = 0;
  DAT_febe8156 = 0;
  DAT_febe8158 = 0;
  DAT_febe80e4 = 0;
  DAT_febe80e5 = 0;
  DAT_febe80e6 = 0;
  DAT_febe80e7 = 0;
  DAT_febe80e8 = 0;
  DAT_febe80e9 = 0;
  DAT_febe80ea = 0;
  DAT_febe80eb = 0;
  DAT_febe80ec = 0;
  DAT_febe80ed = 0;
  DAT_febe80ee = 0;
  DAT_febe80ef = 0;
  DAT_febe80f0 = 0;
  DAT_febe80f1 = 0;
  DAT_febe80f2 = 0;
  DAT_febe80f3 = 0;
  DAT_febe80f4 = 0;
  DAT_febe80f5 = 0;
  DAT_febe80f6 = 0;
  DAT_febe80f7 = 0;
  DAT_febe80f8 = 0;
  DAT_febe80f9 = 0;
  DAT_febe80fa = 0xff;
  DAT_febe80fb = 0xff;
  DAT_febe80fc = 0;
  DAT_febe80fd = 0;
  DAT_febe80fe = 0;
  DAT_febe80ff = 0;
  DAT_febe8100 = 0;
  DAT_febe8101 = 0;
  DAT_febe8102 = 0;
  DAT_febe8103 = 0;
  DAT_febe8104 = 0;
  DAT_febe8105 = 0;
  DAT_febe8106 = 0;
  DAT_febe8107 = 0;
  DAT_febe8c5d = 9;
  DAT_febe818e = 0;
  DAT_febe818d = 0;
  DAT_febe818b = 0;
  DAT_febe817c = 0;
  DAT_febe80d3 = 4;
  DAT_febe81ab = 0;
  DAT_febe81b0 = 0;
  DAT_febe8c51 = 0;
  DAT_febe8c52 = 0;
  DAT_febe8c53 = 0;
  DAT_febe8c54 = 0;
  DAT_febe8c55 = 0;
  DAT_febe8c56 = 0;
  DAT_febe8c57 = 0;
  DAT_febe8c58 = 0;
  DAT_febe8c59 = 0;
  DAT_febe8c5a = 0;
  DAT_febe8c5b = 0;
  DAT_febe8c5c = 0;
  DAT_febe8c5e = 0;
  DAT_febe8c30 = 0;
  DAT_febe7d40 = 0;
  DAT_febe7da6 = 0;
  DAT_febe7da8 = 0;
  DAT_febe7db8 = 0;
  DAT_febe7dbc = 0;
  DAT_febe7daa = 0;
  DAT_febe7dac = 0;
  DAT_febe7dc0 = 0;
  DAT_febe7dc4 = 0;
  DAT_febe7dae = 0;
  DAT_febe7db0 = 0;
  DAT_febe7dc8 = 0;
  DAT_febe7db2 = 0;
  DAT_febe7da4 = 0;
  DAT_febe7db4 = 0;
  DAT_febe7db6 = 0;
  DAT_febe7058 = 0;
  iVar3 = 0;
  do {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7059u + (uint32_t)(iVar3) * 1u)))) = 0;
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -7;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  iVar3 = 0;
  do {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7061u + (uint32_t)(iVar3) * 1u)))) = 0;
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -7;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  iVar3 = 0;
  do {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7069u + (uint32_t)(iVar3) * 1u)))) = 0;
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -7;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  iVar3 = 0;
  do {
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7074u + (uint32_t)(iVar3) * 2u)))) = 0x3980;
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -2;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  DAT_febe7088 = 0;
  DAT_febe708c = 0;
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    *(undefined4 *)(((undefined *)camry_host_ptr(0xfebe7090u)) + iVar3 * 4) = 0;
    iVar1 = iVar3 + -7;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  DAT_febe70b0 = 0;
  DAT_febe70b4 = 0;
  DAT_febe70b8 = 0;
  DAT_febe70bc = 0;
  DAT_febe70c0 = 0;
  DAT_febe707a = 0;
  DAT_febe707c = 0;
  DAT_febe7071 = 0;
  DAT_febe7072 = 0;
  DAT_febe707e = 0;
  DAT_febe7080 = 0;
  DAT_febe7084 = 0;
  DAT_febe70c4 = 0;
  DAT_febe6f36 = 0x3480;
  DAT_febe6f34 = 0;
  DAT_febe6f40 = 0x3480;
  DAT_febe6f4c = 0;
  DAT_febe6f50 = 0;
  DAT_febe6f42 = 0;
  DAT_febe6f44 = 0;
  DAT_febe6f46 = 1;
  DAT_febe6f48 = 1;
  DAT_febe6f4a = 0;
  DAT_febe6f54 = 0x3480;
  DAT_febe6f60 = 0;
  DAT_febe6f64 = 0;
  DAT_febe6f56 = 0;
  DAT_febe6f58 = 0;
  DAT_febe6f5a = 1;
  DAT_febe6f5c = 1;
  DAT_febe6f5e = 0;
  DAT_febe6f12 = 0x3480;
  DAT_febe6f14 = 0;
  DAT_febe6f20 = 0;
  DAT_febe6f24 = 0;
  DAT_febe6f16 = 0;
  DAT_febe6f18 = 0;
  DAT_febe6f1a = 1;
  DAT_febe6f1c = 1;
  DAT_febe6f10 = 0;
  DAT_febe6eae = 0x3480;
  DAT_febe6ec0 = 0;
  DAT_febe6ec4 = 0;
  DAT_febe6ec8 = 0;
  DAT_febe6ecc = 0;
  DAT_febe6ed0 = 0;
  DAT_febe6ed4 = 0;
  DAT_febe6eb0 = 0;
  DAT_febe6eb2 = 0;
  DAT_febe6eb4 = 0;
  DAT_febe6eb6 = 0;
  DAT_febe6eb8 = 0;
  DAT_febe6eba = 0;
  DAT_febe6ebc = 0;
  DAT_febe6eac = 0;
  DAT_febe6fe2 = 0x3480;
  DAT_febe6fe0 = 0;
  DAT_febe6fec = 0x3480;
  DAT_febe6fee = 0;
  DAT_febe6ff0 = 0;
  DAT_febe6ff2 = 0;
  DAT_febe6ff4 = 0;
  DAT_febe6ff8 = 0;
  DAT_febe6ffc = 0x3480;
  DAT_febe6ffe = 0;
  DAT_febe7000 = 0;
  DAT_febe7002 = 0;
  DAT_febe7004 = 0;
  DAT_febe7008 = 0;
  DAT_febe6f82 = 0x3480;
  DAT_febe6f80 = 0;
  DAT_febe6f8c = 0x3480;
  DAT_febe6f8e = 0;
  DAT_febe6f90 = 0;
  DAT_febe6f94 = 0;
  DAT_febe6f98 = 0;
  DAT_febe6f92 = 0;
  DAT_febe6f9c = 0x3480;
  DAT_febe6f9e = 0;
  DAT_febe6fa0 = 0;
  DAT_febe6fa4 = 0;
  DAT_febe6fa8 = 0;
  DAT_febe6fa2 = 0;
  return;
}


