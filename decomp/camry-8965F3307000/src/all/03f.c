#include "common.h"


void FUN_000fc2a0(void)

{
  FUN_000fcc00();
  FUN_000fcc4e();
  return;
}



/* Far-call trampoline: prepare {lp},0 / jarl 0xFCC9C / dispose 0,{lp},lp; byte-verified against the
   exact image. Forwards with registers and stack unchanged; marked as a thunk. Forwarding shape
   machine-verified; target semantics not recovered. */

void thunk_FUN_000fcc9c(void)

{
  FUN_000fcc9c();
  return;
}



void FUN_000fc3cc(void)

{
  f33_copy_cell_block_fd400();
  FUN_000fd426();
  f33_copy_cell_block_fd456();
  return;
}



void FUN_000fc462(void)

{
  FUN_000fd444();
  FUN_000fd49e();
  return;
}



/* Far-call trampoline: prepare {lp},0 / jarl 0xFD562 / dispose 0,{lp},lp; byte-verified against the
   exact image. Forwards with registers and stack unchanged; marked as a thunk. Forwarding shape
   machine-verified; target semantics not recovered. */

void thunk_FUN_000fd562(void)

{
  FUN_000fd562();
  return;
}



void FUN_000fc4f8(void)

{
  FUN_000fcc4e();
  FUN_000fcc9c();
  return;
}



/* Far-call trampoline: prepare {lp},0 / jarl 0xFCC00 / dispose 0,{lp},lp; byte-verified against the
   exact image. Forwards with registers and stack unchanged; marked as a thunk. Forwarding shape
   machine-verified; target semantics not recovered. */

void thunk_FUN_000fcc00(void)

{
  FUN_000fcc00();
  return;
}



void FUN_000fc87c(void)

{
  FUN_000fd426();
  FUN_000fd444();
  return;
}



void FUN_000fc9a8(void)

{
  f33_copy_cell_block_fd456();
  FUN_000fd49e();
  FUN_000fd562();
  return;
}



void FUN_000fcc00(void)

{
  DAT_febeef86 = DAT_febe7db0;
  DAT_febeef80 = DAT_febe7bbc;
  DAT_febeef81 = DAT_febe686c;
  DAT_febeef88 = DAT_febe71ec;
  DAT_febeef8a = DAT_febe7da6;
  DAT_febeef84 = 0;
  DAT_febeef85 = 0;
  DAT_febeef8c = DAT_febe7da8;
  DAT_febeef90 = f33_output_request_status;
  DAT_febeef8e = DAT_febe71f2;
  DAT_febeef82 = DAT_febe7567;
  DAT_febeef83 = DAT_febe7568;
  return;
}



void FUN_000fcc4e(void)

{
  DAT_febef308 = f33_monitor_current_staged_calibration.marker;
  DAT_febef300 = f33_internal_source_admission_state;
  DAT_febef304 = DAT_febe7f3a;
  DAT_febef30c = DAT_febe6af0;
  DAT_febef310 = DAT_febe6ac4;
  DAT_febef314 = DAT_febe6abc;
  DAT_febef318 = DAT_febe6ac0;
  DAT_febef301 = DAT_febe6878;
  DAT_febef306 = DAT_febe8152;
  DAT_febef302 = DAT_febe80a5;
  DAT_febef303 = DAT_febe80a0;
  DAT_febef31c = DAT_febe68b4;
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



/* Cell-block copy: 5 whole-cell assignments with a fixed source-to-destination mapping;
   shape-verified. The mapping is per-cell; cell meanings are not recovered. */

void f33_copy_cell_block_fd400(void)

{
  DAT_febee5c4 = DAT_febeac70;
  DAT_febee5c0 = DAT_febeac2d;
  DAT_febee5c1 = DAT_febeac39;
  DAT_febee5c2 = DAT_febeac3e;
  DAT_febee5c3 = DAT_febeb354;
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



/* Cell-block copy: 11 whole-cell assignments with a fixed source-to-destination mapping;
   shape-verified. The mapping is per-cell; cell meanings are not recovered. */

void f33_copy_cell_block_fd456(void)

{
  DAT_febeeac4 = DAT_febebede;
  DAT_febeeac0 = DAT_febebef0;
  DAT_febeeac6 = DAT_febebee2;
  DAT_febeead0 = DAT_febeb218;
  DAT_febeeac8 = DAT_febeb138;
  DAT_febeeaca = DAT_febeb13c;
  DAT_febeeac1 = DAT_febeb1a7;
  DAT_febeeacc = DAT_febeb11a;
  DAT_febeeac2 = DAT_febeb112;
  DAT_febeeace = DAT_febeae86;
  DAT_febeeac3 = DAT_febead9e;
  return;
}



void FUN_000fd49e(void)

{
  DAT_febeeb24 = f33_learned_quad_rom_bounds.pair1_upper;
  DAT_febeeb28 = f33_learned_quad_rom_bounds.pair1_lower;
  DAT_febeeb2c = f33_learned_quad_rom_bounds.pair2_upper;
  DAT_febeeb30 = f33_learned_quad_rom_bounds.pair2_lower;
  DAT_febeeb34 = DAT_000aef6c;
  DAT_febeeb38 = DAT_000aef70;
  DAT_febeeb3c = DAT_000aef74;
  DAT_febeeb40 = DAT_000aef78;
  DAT_febeeb00 = DAT_febebe9b;
  DAT_febeeb0a = DAT_febebe82;
  DAT_febeeb01 = DAT_febebe78;
  DAT_febeeb0c = DAT_febebee2;
  DAT_febeeb44 = f33_received_word_unchanged_age;
  DAT_febeeb0e = f33_received_retained_word;
  DAT_febeeb02 = DAT_febebe60;
  DAT_febeeb10 = DAT_febeb384;
  DAT_febeeb12 = DAT_febeb142;
  DAT_febeeb14 = DAT_febeb13c;
  DAT_febeeb16 = DAT_febeae12;
  DAT_febeeb03 = DAT_febeacf1;
  DAT_febeeb18 = DAT_febeae58;
  DAT_febeeb04 = DAT_febead39;
  DAT_febeeb1a = DAT_febeae36;
  DAT_febeeb05 = DAT_febead0a;
  DAT_febeeb06 = DAT_febeacf5;
  DAT_febeeb1c = DAT_febeae16;
  DAT_febeeb1e = DAT_febeb11a;
  DAT_febeeb07 = DAT_febead93;
  DAT_febeeb08 = DAT_febebeb8;
  DAT_febeeb20 = DAT_febeaecc;
  DAT_febeeb22 = DAT_febeb38a;
  return;
}



void FUN_000fd562(void)

{
  DAT_febeeb80 = DAT_febeb1d5;
  DAT_febeeb81 = DAT_febebe9b;
  DAT_febeeb92 = DAT_febebe82;
  DAT_febeeb82 = DAT_febebe78;
  DAT_febeeb83 = DAT_febebef0;
  DAT_febeeb94 = DAT_febebee2;
  DAT_febeebac = f33_received_word_unchanged_age;
  DAT_febeeb96 = f33_received_retained_word;
  DAT_febeeb84 = DAT_febebe60;
  DAT_febeeb98 = DAT_febeb142;
  DAT_febeeb85 = DAT_febeb1a7;
  DAT_febeeb86 = DAT_febeb1ce;
  DAT_febeeb87 = DAT_febeb20e;
  DAT_febeeb88 = DAT_febeb1a8;
  DAT_febeeb9a = DAT_febebcc2;
  DAT_febeeb9c = DAT_febebcd6;
  DAT_febeeb9e = DAT_febeae12;
  DAT_febeeb89 = DAT_febeacf1;
  DAT_febeeba0 = DAT_febeae58;
  DAT_febeeb8a = DAT_febead39;
  DAT_febeeba2 = DAT_febeae36;
  DAT_febeeb8b = DAT_febead0a;
  DAT_febeeb8c = DAT_febeacf5;
  DAT_febeeba4 = DAT_febeae16;
  DAT_febeeba6 = DAT_febeb11a;
  DAT_febeeb8d = DAT_febead93;
  DAT_febeeb8e = DAT_febebeb8;
  DAT_febeeb8f = f33_source_coherence_history;
  DAT_febeeb90 = DAT_febeb1cd;
  DAT_febeeba8 = DAT_febeaecc;
  DAT_febeebaa = DAT_febeb38a;
  return;
}



void FUN_000fdc00(void)

{
  f33_initialize_cold_control_retained_state();
  return;
}



void FUN_000fdc14(void)

{
  f33_initialize_control_application_work_state();
  return;
}



void FUN_000fdc3c(void)

{
  f33_snapshot_control_ch2_acquisition();
  return;
}



void FUN_000fdc50(void)

{
  f33_snapshot_control_ch2_feedback();
  return;
}



void FUN_000fdc64(void)

{
  f33_snapshot_control_foreground_acquisition();
  return;
}



void FUN_000fdc78(void)

{
  f33_snapshot_control_foreground_feedback();
  return;
}



void FUN_000fdc8c(void)

{
  f33_snapshot_health_and_service_inputs();
  return;
}



void FUN_000fdcf0(undefined1 param_1,undefined2 param_2,undefined2 param_3)

{
  FUN_000c1f7a(param_1,param_2,param_3);
  return;
}



void FUN_000fdd04(undefined1 param_1,undefined2 param_2)

{
  FUN_000c2000(param_1,param_2);
  return;
}



void FUN_000fdd18(undefined1 param_1,undefined2 param_2,undefined2 param_3)

{
  FUN_000c2044(param_1,param_2,param_3);
  return;
}



void FUN_000fdd2c(undefined1 param_1,undefined2 param_2)

{
  FUN_000c20f6(param_1,param_2);
  return;
}



void FUN_000fdd40(uint param_1,uint param_2,uint param_3)

{
  f33_dispatch_control_foreground_transition(param_1 & 0xff,param_2 & 0xffff,param_3 & 0xffff);
  return;
}



void FUN_000fdd54(uint param_1,uint param_2)

{
  f33_dispatch_control_foreground_steady(param_1 & 0xff,param_2 & 0xffff);
  return;
}



void FUN_000fdd68(void)

{
  f33_start_mode100_after_foreground_restart();
  return;
}



void thunk_FUN_000b1c64(void)

{
  FUN_000b1c64();
  return;
}



void thunk_FUN_000bdcfe(void)

{
  FUN_000bdcfe();
  return;
}



void thunk_FUN_000bdf24(void)

{
  FUN_000bdf24();
  return;
}



void thunk_FUN_000b524a(void)

{
  FUN_000b524a();
  return;
}



void thunk_FUN_000b8e52(void)

{
  FUN_000b8e52();
  return;
}



void thunk_FUN_000bdb48(void)

{
  FUN_000bdb48();
  return;
}



/* TransparentthunktoB8FB2;return0used4FF9A. */

uint f33_stage_encoded_mode_pair_thunk(uint first,uint second)

{
  uint uVar1;
  
  uVar1 = f33_stage_encoded_mode_pair(first,second);
  return uVar1;
}



void thunk_FUN_000b69c6(void)

{
  FUN_000b69c6();
  return;
}



/* Transparent CodeFlashthunk->B69A8, actualselectors3..8 fromconfiguredwritecallbacks. */

void f33_record103_byte_write_thunk(uchar selector,uchar value)

{
  f33_stage_record103_byte_write(selector,value);
  return;
}



/* Far-call trampoline: prepare {lp},0 / jarl 0xFC3CC / dispose 0,{lp},lp; byte-verified against the
   exact image. Forwards with registers and stack unchanged; marked as a thunk. Forwarding shape
   machine-verified; target semantics not recovered. */

void thunk_FUN_000fc3cc(void)

{
  FUN_000fc3cc();
  return;
}



/* Far-call trampoline: prepare {lp},0 / jarl 0xFC462 / dispose 0,{lp},lp; byte-verified against the
   exact image. Forwards with registers and stack unchanged; marked as a thunk. Forwarding shape
   machine-verified; target semantics not recovered. */

void thunk_FUN_000fc462(void)

{
  FUN_000fc462();
  return;
}



/* TransparentthunkB85A2 from5006A. */

void f33_set_service_qualification_mode_thunk(uchar mode)

{
  f33_set_service_qualification_mode(mode);
  return;
}



/* TransparentthunkB8A4C from50026. */

void f33_set_service_numeric_target_thunk(ushort target)

{
  f33_set_service_numeric_target(target);
  return;
}



void thunk_FUN_000b85ae(void)

{
  FUN_000b85ae();
  return;
}



void thunk_FUN_000b85bc(void)

{
  FUN_000b85bc();
  return;
}



void thunk_FUN_000b85ca(void)

{
  FUN_000b85ca();
  return;
}



void thunk_FUN_000b85d0(void)

{
  FUN_000b85d0();
  return;
}



void thunk_FUN_000515ca(void)

{
  FUN_000515ca();
  return;
}



void thunk_FUN_000515d4(void)

{
  FUN_000515d4();
  return;
}



void thunk_FUN_000515e6(void)

{
  FUN_000515e6();
  return;
}



void thunk_FUN_0003599e(void)

{
  FUN_0003599e();
  return;
}



void thunk_FUN_00035780(void)

{
  FUN_00035780();
  return;
}



void thunk_FUN_00045cfc(void)

{
  FUN_00045cfc();
  return;
}



void thunk_FUN_00045d98(void)

{
  FUN_00045d98();
  return;
}



void thunk_FUN_00034bce(void)

{
  FUN_00034bce();
  return;
}



void thunk_FUN_0004841e(void)

{
  FUN_0004841e();
  return;
}



/* Far-call trampoline: prepare {lp},0 / jarl 0x5889A / dispose 0,{lp},lp; byte-verified against the
   exact image. Forwards with registers and stack unchanged; marked as a thunk. Forwarding shape
   machine-verified; target semantics not recovered. */

void thunk_FUN_0005889a(void)

{
  FUN_0005889a();
  return;
}



/* Far-call trampoline: prepare {lp},0 / jarl 0x588B6 / dispose 0,{lp},lp; byte-verified against the
   exact image. Forwards with registers and stack unchanged; marked as a thunk. Forwarding shape
   machine-verified; target semantics not recovered. */

void thunk_FUN_000588b6(void)

{
  FUN_000588b6();
  return;
}



/* Far-call trampoline: prepare {lp},0 / jarl 0x58C84 / dispose 0,{lp},lp; byte-verified against the
   exact image. Forwards with registers and stack unchanged; marked as a thunk. Forwarding shape
   machine-verified; target semantics not recovered. */

void thunk_FUN_00058c84(void)

{
  FUN_00058c84();
  return;
}



/* Tail-call66F1E and preserve its full R10 readiness result. No independent hardware power or
   persistence assertion. */

uint f33_query_application_nvm_readiness(void)

{
  uint uVar1;
  
  uVar1 = f33_application_nvm_is_ready();
  return uVar1;
}



/* Far-call trampoline: prepare {lp},0 / jarl 0x66F84 / dispose 0,{lp},lp; byte-verified against the
   exact image. Forwards with registers and stack unchanged; marked as a thunk. Forwarding shape
   machine-verified; target semantics not recovered. */

void thunk_FUN_00066f84(void)

{
  FUN_00066f84();
  return;
}



/* Far-call trampoline: prepare {lp},0 / jarl 0x66FBA / dispose 0,{lp},lp; byte-verified against the
   exact image. Forwards with registers and stack unchanged; marked as a thunk. Forwarding shape
   machine-verified; target semantics not recovered. */

void thunk_FUN_00066fba(void)

{
  FUN_00066fba();
  return;
}



/* Tail-wrapper66FEE returns0 inexactimage.0701event2-ready therefore takesB17EE
   softwareforegroundrestart; return5A alternative0800edgeisnotreachablethroughthistarget. */

uint f33_get_mode_restart_hardware_selector(void)

{
  uint uVar1;
  
  uVar1 = f33_platform_restart_selector_constant_zero();
  return uVar1;
}



/* Far-call trampoline: prepare {lp},0 / jarl 0x66FD4 / dispose 0,{lp},lp; byte-verified against the
   exact image. Forwards with registers and stack unchanged; marked as a thunk. Forwarding shape
   machine-verified; target semantics not recovered. */

void thunk_FUN_00066fd4(void)

{
  FUN_00066fd4();
  return;
}



/* Far-call trampoline: prepare {lp},0 / jarl 0x66EF4 / dispose 0,{lp},lp; byte-verified against the
   exact image. Forwards with registers and stack unchanged; marked as a thunk. Forwarding shape
   machine-verified; target semantics not recovered. */

void thunk_FUN_00066ef4(void)

{
  FUN_00066ef4();
  return;
}



void FUN_000ff09c(uint param_1,uint *param_2)

{
  f33_nvm_set_record(param_1 & 0xffff,param_2);
  return;
}



void FUN_000ff0b0(uint param_1,uint *param_2)

{
  f33_nvm_get_record(param_1 & 0xffff, camry_host_addr(param_2));
  return;
}



void FUN_000ff0c4(uint param_1)

{
  f33_nvm_get_record_status(param_1 & 0xffff);
  return;
}



void FUN_000ff0d8(void)

{
                    /* WARNING: Subroutine does not return */
  f33_enter_terminal_hardware_sequence();
}



/* Far-call trampoline: prepare {lp},0 / jarl 0x6163E / dispose 0,{lp},lp; byte-verified against the
   exact image. Forwards with registers and stack unchanged; marked as a thunk. Forwarding shape
   machine-verified; target semantics not recovered. */

void thunk_FUN_0006163e(void)

{
  FUN_0006163e();
  return;
}



void thunk_FUN_00052a10(void)

{
  FUN_00052a10();
  return;
}



void thunk_FUN_000562fa(void)

{
  FUN_000562fa();
  return;
}



void thunk_FUN_00035ad6(void)

{
  FUN_00035ad6();
  return;
}



/* Far-call trampoline: prepare {lp},0 / jarl 0x62E12 / dispose 0,{lp},lp; byte-verified against the
   exact image. Forwards with registers and stack unchanged; marked as a thunk. Forwarding shape
   machine-verified; target semantics not recovered. */

void thunk_FUN_00062e12(void)

{
  FUN_00062e12();
  return;
}


