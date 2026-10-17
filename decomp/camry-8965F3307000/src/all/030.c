#include "common.h"


/* Cell-block copy: 15 whole-cell assignments with a fixed source-to-destination mapping;
   shape-verified. The mapping is per-cell; cell meanings are not recovered. */

void f33_copy_cell_block_c1b24(void)

{
  DAT_febeaf50 = DAT_febeec04;
  DAT_febeaf52 = DAT_febeec06;
  DAT_febeaf54 = DAT_febeec08;
  DAT_febeaf56 = DAT_febeec0a;
  DAT_febeaf58 = DAT_febeec0c;
  DAT_febeaf60 = DAT_febeec14;
  DAT_febeaf64 = DAT_febeec18;
  DAT_febeaf68 = DAT_febeec1c;
  DAT_febeaf6c = DAT_febeec20;
  DAT_febeaf5a = DAT_febeec0e;
  DAT_febeaf70 = DAT_febeec24;
  DAT_febeaf4c = DAT_febeec00;
  DAT_febeaf4d = DAT_febeec01;
  DAT_febeaf4e = DAT_febeec02;
  DAT_febeaf5c = DAT_febeec10;
  return;
}



/* CopyEC00..EC24 publication into AF74..AF98 CH2 input view, preserving byte/halfword/word widths.
   FDC3C is called within58A1C FFC0 window. ForegroundAFD4..AFF8 is separately sampled. */

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



/* CopyACxx controller fields andED00..ED12 outputs into AF9C..AFCA CH2 view under the58A1C FF80
   window, after the separately masked acquisition copy. */

void f33_snapshot_control_ch2_feedback(void)

{
  DAT_febeafa2 = DAT_febeac54;
  DAT_febeafa4 = DAT_febeac56;
  DAT_febeaf9c = DAT_febeac2d;
  DAT_febeafa6 = DAT_febeac58;
  DAT_febeafb4 = DAT_febeac94;
  DAT_febeafa8 = DAT_febeac68;
  DAT_febeafaa = DAT_febeac70;
  DAT_febeafac = DAT_febeac76;
  DAT_febeafae = DAT_febeac7a;
  DAT_febeaf9d = DAT_febeac39;
  DAT_febeafb0 = DAT_febeac7e;
  DAT_febeaf9e = DAT_febeac3b;
  DAT_febeaf9f = DAT_febeac3e;
  DAT_febeafb2 = DAT_febeac82;
  DAT_febeafa0 = DAT_febeac3f;
  DAT_febeafa1 = DAT_febeac40;
  DAT_febeafbc = DAT_febeed04;
  DAT_febeafbe = DAT_febeed06;
  DAT_febeafc0 = DAT_febeed08;
  DAT_febeafc2 = DAT_febeed0a;
  DAT_febeafc4 = DAT_febeed0c;
  DAT_febeafc6 = DAT_febeed0e;
  DAT_febeafc8 = DAT_febeed10;
  DAT_febeafb8 = DAT_febeed00;
  DAT_febeafb9 = DAT_febeed01;
  DAT_febeafba = DAT_febeed02;
  DAT_febeafbb = DAT_febeed03;
  DAT_febeafca = DAT_febeed12;
  return;
}



/* CopyEC00..EC24 publication into AFD4..AFF8 foreground view, preserving widths. FDC64 is called
   within58B1A FFC0 window; no synchronization with a previously sampled CH2 bank is implied. */

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



/* CopyB354/B3A0/B3A6/B430/B436, ACxx controller fields andED00..ED12 outputs into AFFC..B062
   foreground view under58B1A FF80, before monitor/health/service snapshot window. */

void f33_snapshot_control_foreground_feedback(void)

{
  DAT_febeaffc = DAT_febeb354;
  DAT_febeb002 = DAT_febeb3a6;
  DAT_febeb000 = DAT_febeb3a0;
  DAT_febeb006 = DAT_febeb436;
  DAT_febeb004 = DAT_febeb430;
  DAT_febeb02a = DAT_febeac54;
  DAT_febeb02c = DAT_febeac56;
  DAT_febeb024 = DAT_febeac2d;
  DAT_febeb02e = DAT_febeac58;
  DAT_febeb03c = DAT_febeac94;
  DAT_febeb030 = DAT_febeac68;
  DAT_febeb032 = DAT_febeac70;
  DAT_febeb034 = DAT_febeac76;
  DAT_febeb036 = DAT_febeac7a;
  DAT_febeb025 = DAT_febeac39;
  DAT_febeb038 = DAT_febeac7e;
  DAT_febeb026 = DAT_febeac3b;
  DAT_febeb027 = DAT_febeac3e;
  DAT_febeb03a = DAT_febeac82;
  DAT_febeb028 = DAT_febeac3f;
  DAT_febeb029 = DAT_febeac40;
  DAT_febeb054 = DAT_febeed04;
  DAT_febeb056 = DAT_febeed06;
  DAT_febeb058 = DAT_febeed08;
  DAT_febeb05a = DAT_febeed0a;
  DAT_febeb05c = DAT_febeed0c;
  DAT_febeb05e = DAT_febeed0e;
  DAT_febeb060 = DAT_febeed10;
  DAT_febeb050 = DAT_febeed00;
  DAT_febeb051 = DAT_febeed01;
  DAT_febeb052 = DAT_febeed02;
  DAT_febeb053 = DAT_febeed03;
  DAT_febeb062 = DAT_febeed12;
  return;
}



/* Copy status, observer, analog and all ten BD34 current-limit owner cells into the health/service
   snapshot, including B010[0..9]. B84B8 checks every owner except5 against22170. This sequential
   snapshot is not an atomic hardware sample or instantaneous owner publication. Sequential
   health/service snapshot includes all ten current-limit owner cells BD34..BD46 into B010..B022,
   plus status, observer and analog fields. B84B8 admits only when all owners except5 are at
   least22170; snapshot timing remains separate. */

void f33_snapshot_health_and_service_inputs(void)

{
  DAT_febeb04c = DAT_febebe20;
  DAT_febeb04d = DAT_febebe21;
  DAT_febeb04e = DAT_febebe22;
  DAT_febeb04f = DAT_febebe23;
  DAT_febeb008 = DAT_febebdb2;
  DAT_febeb00a = DAT_febebdb4;
  DAT_febeb00c = DAT_febebcf0;
  DAT_febeafcc = DAT_febeaf3c;
  DAT_febeafd0 = DAT_febeaf40;
  DAT_febeafcd = DAT_febeaf3d;
  DAT_febeafce = DAT_febeaf3e;
  DAT_febeafd2 = DAT_febeaf42;
  DAT_febeb010 = DAT_febebd34;
  DAT_febeb012 = DAT_febebd36;
  DAT_febeb014 = DAT_febebd38;
  DAT_febeb016 = DAT_febebd3a;
  DAT_febeb018 = DAT_febebd3c;
  DAT_febeb01a = DAT_febebd3e;
  DAT_febeb01c = DAT_febebd40;
  DAT_febeb01e = DAT_febebd42;
  DAT_febeb020 = DAT_febebd44;
  DAT_febeb022 = DAT_febebd46;
  DAT_febeb040 = DAT_febeac01;
  DAT_febeb041 = DAT_febeac02;
  DAT_febeb042 = DAT_febeac05;
  DAT_febeb043 = DAT_febeac08;
  DAT_febeb048 = DAT_febeac1c;
  DAT_febeb044 = DAT_febeac09;
  DAT_febeb080 = DAT_febeee1c;
  DAT_febeb064 = DAT_febeee00;
  DAT_febeb065 = DAT_febeee01;
  DAT_febeb066 = DAT_febeee02;
  DAT_febeb082 = DAT_febeee1e;
  DAT_febeb084 = DAT_febeee20;
  DAT_febeb067 = DAT_febeee03;
  DAT_febeb068 = DAT_febeee04;
  DAT_febeb069 = DAT_febeee05;
  DAT_febeb06a = DAT_febeee06;
  DAT_febeb06b = DAT_febeee07;
  DAT_febeb06c = DAT_febeee08;
  DAT_febeb06d = DAT_febeee09;
  DAT_febeb06e = DAT_febeee0a;
  DAT_febeb06f = DAT_febeee0b;
  DAT_febeb070 = DAT_febeee0c;
  DAT_febeb071 = DAT_febeee0d;
  DAT_febeb072 = DAT_febeee0e;
  DAT_febeb073 = DAT_febeee0f;
  DAT_febeb086 = DAT_febeee22;
  DAT_febeb074 = DAT_febeee10;
  DAT_febeb075 = DAT_febeee11;
  DAT_febeb088 = DAT_febeee24;
  DAT_febeb08c = DAT_febeee28;
  DAT_febeb076 = DAT_febeee12;
  DAT_febeb08a = DAT_febeee26;
  DAT_febeb077 = DAT_febeee13;
  DAT_febeb078 = DAT_febeee14;
  DAT_febeb079 = DAT_febeee15;
  DAT_febeb07a = DAT_febeee16;
  DAT_febeb07b = DAT_febeee17;
  DAT_febeb07c = DAT_febeee18;
  DAT_febeb07d = DAT_febeee19;
  DAT_febeb07e = DAT_febeee1a;
  return;
}



void FUN_000c1f7a(undefined4 param_1,uint param_2,uint param_3)

{
  param_3 = param_3 & 0xffff;
  param_2 = param_2 & 0xffff;
  if (0x102 < param_2) {
    if (param_3 < 0x103) {
      f33_return_only_stub_b7372();
    }
    FUN_000b7374();
  }
  if (param_2 - 0x300 < 0x223) {
    if (0x222 < param_3 - 0x300) {
      f33_run_init_chain_d0a3e();
    }
    FUN_000bcd02();
  }
  if (param_2 == 0x520) {
    if (param_3 == 0x520) {
      FUN_000b8af0();
      FUN_000b7a9e();
    }
    else {
      f33_fill_constant_block_b8a54();
      FUN_000b8af0();
      f33_fill_constant_block_b7a02();
      FUN_000b7a9e();
      FUN_000b8682();
    }
    f33_publish_service_engine_substitution();
  }
  if (0x101 < param_2) {
    if (param_3 < 0x102) {
      f33_return_only_stub_be06c();
    }
    f33_return_only_stub_be06e();
  }
  f33_fill_constant_block_bf33e();
  return;
}



void FUN_000c2000(undefined4 param_1,uint param_2)

{
  param_2 = param_2 & 0xffff;
  if (0x102 < param_2) {
    FUN_000b7374();
  }
  if (param_2 - 0x300 < 0x223) {
    FUN_000bcd02();
  }
  if (param_2 == 0x520) {
    FUN_000b8af0();
    FUN_000b7a9e();
    f33_publish_service_engine_substitution();
  }
  if (0x101 < param_2) {
    f33_return_only_stub_be06e();
  }
  f33_fill_constant_block_bf33e();
  return;
}



void FUN_000c2044(undefined4 param_1,uint param_2,uint param_3)

{
  param_3 = param_3 & 0xffff;
  param_2 = param_2 & 0xffff;
  if (0x102 < param_2) {
    if (param_3 < 0x103) {
      f33_return_only_stub_bdb96();
    }
    FUN_000bdb98();
  }
  if (param_2 - 0x200 < 0x323) {
    if (param_3 - 0x200 < 0x323) {
      f33_publish_owner2_deficit_limit_request();
    }
    else {
      f33_reset_owner2_deficit_request();
      f33_publish_owner2_deficit_limit_request();
      f33_return_only_stub_bc5fc();
    }
    FUN_000bc5fe();
  }
  if (0x1ff < param_2) {
    if (param_3 < 0x200) {
      f33_reset_owner1_limit_request();
      f33_publish_owner1_limit_request();
      f33_return_only_stub_bb7f8();
    }
    else {
      f33_publish_owner1_limit_request();
    }
    f33_publish_other_current_limit();
  }
  if (param_2 - 0x300 < 0x223) {
    if (0x222 < param_3 - 0x300) {
      thunk_FUN_000d0bda();
    }
    f33_run_init_chain_bca62();
  }
  if (0x101 < param_2) {
    if (param_3 < 0x102) {
      f33_return_only_stub_bdfa8();
      f33_return_only_stub_bdfaa();
      f33_return_only_stub_be212();
    }
    else {
      f33_return_only_stub_bdfaa();
    }
    f33_return_only_stub_be214();
  }
  f33_fill_constant_block_bf2f8();
  return;
}



void FUN_000c20f6(undefined4 param_1,uint param_2)

{
  param_2 = param_2 & 0xffff;
  if (0x102 < param_2) {
    FUN_000bdb98();
  }
  if (param_2 - 0x200 < 0x323) {
    f33_publish_owner2_deficit_limit_request();
    FUN_000bc5fe();
  }
  if (0x1ff < param_2) {
    f33_publish_owner1_limit_request();
    f33_publish_other_current_limit();
  }
  if (param_2 - 0x300 < 0x223) {
    f33_run_init_chain_bca62();
  }
  if (0x101 < param_2) {
    f33_return_only_stub_bdfaa();
    f33_return_only_stub_be214();
  }
  f33_fill_constant_block_bf2f8();
  return;
}



/* Use low16 new/old captured mode to run crossing-only initializers plus admitted steady
   components, with cadence bits1/4 controlling slower work. Health is active above0100; current
   limit producers above01FF; projectionBCD62 only0300..0522. Reconcile/advance live mode after
   producers, then publishBF3AA; later workers still use captured arguments. */

void f33_dispatch_control_foreground_transition
               (uint cadence_mask,uint captured_mode,uint previous_mode)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  
  uVar2 = captured_mode & 0xffff;
  uVar3 = previous_mode & 0xffff;
  if (0xff < uVar2) {
    if (uVar3 < 0x100) {
      f33_return_only_stub_be324();
      f33_condition_staged_offset_scalar();
      f33_return_only_stub_be302();
    }
    else {
      f33_condition_staged_offset_scalar();
    }
    f33_scale_staged_byte_pair_to_control_raw();
  }
  if (0x100 < uVar2) {
    if (uVar3 < 0x101) {
      f33_return_only_stub_bea54();
      f33_update_delayed_received_startup_qualification();
      f33_return_only_stub_bf0a8();
    }
    else {
      f33_update_delayed_received_startup_qualification();
    }
    f33_update_initialized_record8_confirmation();
    uVar1 = cadence_mask & 2;
    if (uVar3 < 0x101) {
      f33_seed_health_received_source_filter();
      if (uVar1 != 0) {
        f33_refresh_health_received_source_generation();
      }
      f33_return_only_stub_becce();
      if (uVar1 != 0) {
        FUN_000bed90();
      }
      FUN_000bef22();
      if (uVar1 != 0) {
        FUN_000bef3e();
      }
      FUN_000beda2();
      if (uVar1 != 0) {
        FUN_000bef10();
      }
      f33_return_only_stub_be80c();
      if (uVar1 != 0) {
        FUN_000be80e();
      }
      f33_return_only_stub_be844();
      if (uVar1 != 0) {
        FUN_000be846();
      }
      f33_return_only_stub_bef9a();
      if (uVar1 != 0) {
        FUN_000bef9c();
      }
      f33_return_only_stub_befd4();
      if (uVar1 != 0) {
        FUN_000befd6();
      }
      f33_return_only_stub_be796();
    }
    else if (uVar1 != 0) {
      f33_refresh_health_received_source_generation();
      FUN_000bed90();
      FUN_000bef3e();
      FUN_000bef10();
      FUN_000be80e();
      FUN_000be846();
      FUN_000bef9c();
      FUN_000befd6();
    }
    FUN_000be7fa();
  }
  if (0x101 < uVar2) {
    if (uVar3 < 0x102) {
      f33_initialize_received_word_age_from_record13();
    }
    f33_refresh_received_control_metadata();
  }
  if (0xff < uVar2) {
    if (uVar3 < 0x100) {
      f33_fill_constant_block_bdba8();
    }
    FUN_000bdbe0();
  }
  if (0x102 < uVar2) {
    if (uVar3 < 0x103) {
      FUN_000bdd22();
      FUN_000bde16();
      f33_return_only_stub_bdb86();
      f33_return_only_stub_bdb88();
      f33_return_only_stub_bdb8c();
    }
    else {
      FUN_000bde16();
      f33_return_only_stub_bdb88();
    }
    FUN_000bdb8e();
  }
  if (0x101 < uVar2) {
    if (uVar3 < 0x102) {
      FUN_000b918e();
      FUN_000b92f0();
      FUN_000b8fe2();
    }
    else {
      FUN_000b92f0();
    }
    f33_monitor_pending_learned_record_updates();
  }
  if (0x102 < uVar2) {
    uVar1 = cadence_mask & 2;
    if (uVar3 < 0x103) {
      f33_return_only_stub_b8b36();
      FUN_000b8d8c();
      thunk_FUN_000b6d72();
      if (uVar1 != 0) {
        f33_run_init_chain_b7054();
      }
      FUN_000b70d8();
      if (uVar1 != 0) {
        FUN_000b722c();
      }
      FUN_000b6c2a();
      if (uVar1 != 0) {
        FUN_000b6d20();
      }
      FUN_000b6a38();
      if (uVar1 != 0) {
        FUN_000b6b9a();
      }
      FUN_000b8f74();
      if (uVar1 != 0) {
        thunk_FUN_000b8f4a();
      }
      f33_return_only_stub_b8fcc();
      if (uVar1 != 0) {
        f33_return_only_stub_b8fce();
      }
      f33_return_only_stub_b8f3a();
      if (uVar1 != 0) {
        f33_fill_constant_block_b8f16();
      }
      f33_return_only_stub_b8ec8();
      if (uVar1 != 0) {
        f33_fill_constant_block_b8eca();
      }
      f33_return_only_stub_b7354();
      if (uVar1 != 0) {
        f33_return_only_stub_b7356();
      }
      f33_return_only_stub_b733e();
      if (uVar1 != 0) {
        f33_fill_constant_block_b7314();
      }
      f33_return_only_stub_b72c0();
      if (uVar1 != 0) {
        f33_fill_constant_block_b72c2();
      }
      FUN_000b8e9a();
      if (uVar1 != 0) {
        thunk_FUN_000b8e8e();
      }
      FUN_000b61e0();
      f33_run_init_chain_b690a();
      FUN_000b532a();
      FUN_000b53c2();
      f33_return_only_stub_b50aa();
    }
    else {
      FUN_000b8d8c();
      if (uVar1 != 0) {
        f33_run_init_chain_b7054();
        FUN_000b722c();
        FUN_000b6d20();
        FUN_000b6b9a();
        thunk_FUN_000b8f4a();
        f33_return_only_stub_b8fce();
        f33_fill_constant_block_b8f16();
        f33_fill_constant_block_b8eca();
        if (uVar1 != 0) {
          f33_return_only_stub_b7356();
          f33_fill_constant_block_b7314();
          f33_fill_constant_block_b72c2();
          thunk_FUN_000b8e8e();
        }
      }
      f33_run_init_chain_b690a();
      FUN_000b53c2();
    }
    f33_run_init_chain_b5232();
  }
  if (uVar2 == 0x522) {
    if (uVar3 == 0x522) {
      FUN_000b7728();
    }
    else {
      f33_fill_constant_block_b7716();
      FUN_000b7728();
      FUN_000b738c();
    }
    if ((cadence_mask >> 1 & 1) != 0) {
      FUN_000b73cc();
    }
  }
  if (0x102 < uVar2) {
    if (uVar3 < 0x103) {
      f33_return_only_stub_b3a54();
      f33_run_init_chain_b3bd2();
      FUN_000b389c();
      FUN_000b38d2();
      f33_return_only_stub_b391e();
      FUN_000b3a42();
      f33_return_only_stub_b342e();
    }
    else {
      f33_run_init_chain_b3bd2();
      FUN_000b38d2();
      FUN_000b3a42();
    }
    FUN_000b37da();
  }
  if (0x100 < uVar2) {
    if (uVar3 < 0x101) {
      f33_reset_current_source_coherence_observations();
      f33_update_source_coherence_history();
      f33_reset_health_record_lifecycle_entry();
      f33_advance_health_record_lifecycle();
      f33_return_only_stub_b480a();
      f33_update_qualified_health_source_policy();
      f33_reset_qualified_health_state_entry();
      f33_advance_qualified_health_state();
      FUN_000b4538();
      FUN_000b47c0();
      FUN_000b47d6();
      FUN_000b47de();
      f33_return_only_stub_b3c6a();
    }
    else {
      f33_update_source_coherence_history();
      f33_advance_health_record_lifecycle();
      f33_update_qualified_health_source_policy();
      f33_advance_qualified_health_state();
      FUN_000b47c0();
      FUN_000b47de();
    }
    f33_publish_health_coherence_fault_actions();
    if (uVar3 < 0x101) {
      FUN_000b431a();
    }
    f33_update_health_status_delay_summaries();
  }
  if (uVar2 - 0x200 < 0x323) {
    if (uVar3 - 0x200 < 0x323) {
      f33_qualify_owner3_shutdown_signal();
      f33_publish_owner3_shutdown_request();
      if ((cadence_mask & 2) != 0) {
        FUN_000bc7ce();
      }
    }
    else {
      f33_reset_owner3_signal_qualification();
      f33_qualify_owner3_shutdown_signal();
      f33_reset_owner3_shutdown_request();
      f33_publish_owner3_shutdown_request();
      f33_fill_constant_block_bc7be();
      if ((cadence_mask & 2) != 0) {
        FUN_000bc7ce();
      }
      f33_fill_constant_block_bc648();
    }
    FUN_000bc65e();
  }
  if (0x1ff < uVar2) {
    uVar1 = cadence_mask & 0x10;
    if (uVar3 < 0x200) {
      FUN_000bb95e();
      if (uVar1 != 0) {
        FUN_000bbf8a();
      }
      f33_return_only_stub_bad00();
      f33_stage_absolute_limit_seeds();
      f33_reset_owner5_release_state();
      f33_publish_owner5_limit_request();
      f33_reset_owner4_release_state();
      f33_publish_owner4_limit_request();
      f33_reset_owner8_release_state();
      f33_publish_owner8_limit_request();
      f33_reset_owner6_calibration_envelope();
      f33_update_owner6_calibration_envelope();
      f33_reset_owner1_qualification_state();
      f33_qualify_owner1_limit_state();
      f33_reset_lifecycle_difference_monitor_entry();
      if (uVar1 != 0) {
        f33_step_lifecycle_difference_monitor();
      }
      FUN_000bb87a();
      f33_update_thermal_release_envelope();
      f33_return_only_stub_ba8ae();
    }
    else {
      if (uVar1 != 0) {
        FUN_000bbf8a();
      }
      f33_stage_absolute_limit_seeds();
      f33_publish_owner5_limit_request();
      f33_publish_owner4_limit_request();
      f33_publish_owner8_limit_request();
      f33_update_owner6_calibration_envelope();
      f33_qualify_owner1_limit_state();
      if (uVar1 != 0) {
        f33_step_lifecycle_difference_monitor();
      }
      f33_update_thermal_release_envelope();
    }
    FUN_000ba8b0();
  }
  if (uVar2 - 0x300 < 0x223) {
    if (uVar3 - 0x300 < 0x223) {
      f33_refresh_foreground_control_projection();
    }
    else {
      FUN_000bcd22();
      f33_refresh_foreground_control_projection();
      f33_return_only_stub_b9328();
    }
    if ((cadence_mask >> 1 & 1) != 0) {
      f33_run_control_profile_qualification();
    }
  }
  if (0xff < uVar2) {
    if (uVar3 < 0x100) {
      f33_return_only_stub_b9bc0();
    }
    if ((cadence_mask >> 1 & 1) != 0) {
      f33_run_control_profile_retention();
    }
    if (uVar3 < 0x100) {
      FUN_000b14b2();
      f33_reconcile_mode_requests();
      f33_reset_mode_readiness_counter();
    }
    else {
      f33_reconcile_mode_requests();
    }
    f33_advance_application_mode();
  }
  if (0x102 < uVar2) {
    if (uVar3 < 0x103) {
      f33_return_only_stub_b784a();
    }
    FUN_000b78d0();
  }
  if (uVar2 == 0x520) {
    if (uVar3 == 0x520) {
      FUN_000b83ba();
    }
    else {
      f33_return_only_stub_b7c80();
      FUN_000b83ba();
      f33_fill_constant_block_b87e2();
    }
    FUN_000b885c();
  }
  if (0x102 < uVar2) {
    if (uVar3 < 0x103) {
      FUN_000b85d8();
    }
    FUN_000b8622();
  }
  if (uVar2 - 0x200 < 0x323) {
    if (0x322 < uVar3 - 0x200) {
      f33_return_only_stub_b797e();
    }
    FUN_000b7980();
  }
  if (uVar2 == 0x520) {
    if (uVar3 == 0x520) {
      FUN_000b89e0();
    }
    else {
      f33_fill_constant_block_b8896();
      FUN_000b89e0();
      f33_fill_constant_block_b7ae4();
    }
    FUN_000b7c2c();
  }
  if (0x101 < uVar2) {
    if (uVar3 < 0x102) {
      f33_return_only_stub_bdf80();
      f33_return_only_stub_bdf82();
      f33_return_only_stub_be130();
      f33_return_only_stub_be132();
      f33_return_only_stub_be1f4();
      f33_return_only_stub_be1f6();
      f33_return_only_stub_be28a();
    }
    else {
      f33_return_only_stub_bdf82();
      f33_return_only_stub_be132();
      f33_return_only_stub_be1f6();
    }
    f33_return_only_stub_be28c();
  }
  if (0xff < uVar2) {
    if (uVar3 < 0x100) {
      f33_return_only_stub_bf24a();
    }
    f33_refresh_acquired_scalar_status_publication();
  }
  f33_publish_foreground_control_outputs();
  return;
}



/* Run components admitted by low16 captured mode and cadence bits, without crossing initializers.
   Health above0100 precedes nonthermal/thermal limit producers above01FF; projection
   only0300..0522. Reconcile/advance live mode, then publishBF3AA even when capturedmode0. No atomic
   change of other task generations. */

void f33_dispatch_control_foreground_steady(uint cadence_mask,uint captured_mode)

{
  uint uVar1;
  
  uVar1 = captured_mode & 0xffff;
  if (0xff < uVar1) {
    f33_condition_staged_offset_scalar();
    f33_scale_staged_byte_pair_to_control_raw();
  }
  if (0x100 < uVar1) {
    f33_update_delayed_received_startup_qualification();
    f33_update_initialized_record8_confirmation();
    if ((cadence_mask >> 1 & 1) != 0) {
      f33_refresh_health_received_source_generation();
      FUN_000bed90();
      FUN_000bef3e();
      FUN_000bef10();
      FUN_000be80e();
      FUN_000be846();
      FUN_000bef9c();
      FUN_000befd6();
    }
    FUN_000be7fa();
  }
  if (0x101 < uVar1) {
    f33_refresh_received_control_metadata();
  }
  if (0xff < uVar1) {
    FUN_000bdbe0();
  }
  if (0x102 < uVar1) {
    FUN_000bde16();
    f33_return_only_stub_bdb88();
    FUN_000bdb8e();
  }
  if (0x101 < uVar1) {
    FUN_000b92f0();
    f33_monitor_pending_learned_record_updates();
  }
  if (0x102 < uVar1) {
    FUN_000b8d8c();
    if ((cadence_mask & 2) != 0) {
      f33_run_init_chain_b7054();
      FUN_000b722c();
      FUN_000b6d20();
      FUN_000b6b9a();
      thunk_FUN_000b8f4a();
      f33_return_only_stub_b8fce();
      f33_fill_constant_block_b8f16();
      f33_fill_constant_block_b8eca();
      if ((cadence_mask & 2) != 0) {
        f33_return_only_stub_b7356();
        f33_fill_constant_block_b7314();
        f33_fill_constant_block_b72c2();
        thunk_FUN_000b8e8e();
      }
    }
    f33_run_init_chain_b690a();
    FUN_000b53c2();
    f33_run_init_chain_b5232();
  }
  if ((uVar1 == 0x522) && (FUN_000b7728(), (cadence_mask >> 1 & 1) != 0)) {
    FUN_000b73cc();
  }
  if (0x102 < uVar1) {
    f33_run_init_chain_b3bd2();
    FUN_000b38d2();
    FUN_000b3a42();
    FUN_000b37da();
  }
  if (0x100 < uVar1) {
    f33_update_source_coherence_history();
    f33_advance_health_record_lifecycle();
    f33_update_qualified_health_source_policy();
    f33_advance_qualified_health_state();
    FUN_000b47c0();
    FUN_000b47de();
    f33_publish_health_coherence_fault_actions();
    f33_update_health_status_delay_summaries();
  }
  if (uVar1 - 0x200 < 0x323) {
    f33_qualify_owner3_shutdown_signal();
    f33_publish_owner3_shutdown_request();
    if ((cadence_mask >> 1 & 1) != 0) {
      FUN_000bc7ce();
    }
    FUN_000bc65e();
  }
  if (0x1ff < uVar1) {
    if ((cadence_mask & 0x10) != 0) {
      FUN_000bbf8a();
    }
    f33_stage_absolute_limit_seeds();
    f33_publish_owner5_limit_request();
    f33_publish_owner4_limit_request();
    f33_publish_owner8_limit_request();
    f33_update_owner6_calibration_envelope();
    f33_qualify_owner1_limit_state();
    if ((cadence_mask & 0x10) != 0) {
      f33_step_lifecycle_difference_monitor();
    }
    f33_update_thermal_release_envelope();
    FUN_000ba8b0();
  }
  if ((uVar1 - 0x300 < 0x223) &&
     (f33_refresh_foreground_control_projection(), (cadence_mask >> 1 & 1) != 0)) {
    f33_run_control_profile_qualification();
  }
  if (0xff < uVar1) {
    if ((cadence_mask >> 1 & 1) != 0) {
      f33_run_control_profile_retention();
    }
    f33_reconcile_mode_requests();
    f33_advance_application_mode();
  }
  if (0x102 < uVar1) {
    FUN_000b78d0();
  }
  if (uVar1 == 0x520) {
    FUN_000b83ba();
    FUN_000b885c();
  }
  if (0x102 < uVar1) {
    FUN_000b8622();
  }
  if (uVar1 - 0x200 < 0x323) {
    FUN_000b7980();
  }
  if (uVar1 == 0x520) {
    FUN_000b89e0();
    FUN_000b7c2c();
  }
  if (0x101 < uVar1) {
    f33_return_only_stub_bdf82();
    f33_return_only_stub_be132();
    f33_return_only_stub_be1f6();
    f33_return_only_stub_be28c();
  }
  if (0xff < uVar1) {
    f33_refresh_acquired_scalar_status_publication();
  }
  f33_publish_foreground_control_outputs();
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



/* WARNING: Removing unreachable block (ram,0x000c2c48) */
/* Interpolate prior base-curve slopes BF34/BF36 with C1A6, add nonlinear slopeC44E, then clamp by
   AF88C into signed16 BF40. */

void f33_publish_combined_assist_slope(void)

{
  int iVar1;
  int iVar2;
  
  iVar2 = (int)DAT_000af88c;
  DAT_febebf18 = (((int)DAT_febebf36 - (int)DAT_febebf34) * (int)DAT_febec1a6) / 0x400 +
                 (int)DAT_febebf34;
  DAT_febebf1c = DAT_febec44e + DAT_febebf18;
  DAT_febebf40 = DAT_000af88c;
  if (DAT_febebf1c - iVar2 < 0 !=
      (DAT_febebf1c < 0 != iVar2 < 0 && iVar2 < 0 == DAT_febebf1c - iVar2 < 0) ||
      DAT_febebf1c == iVar2) {
    iVar1 = -iVar2;
    if (DAT_febebf1c + iVar2 < 0 ==
        (DAT_febebf1c < 0 != iVar1 < 0 && iVar1 < 0 == DAT_febebf1c + iVar2 < 0) &&
        DAT_febebf1c != iVar1) {
      DAT_febebf40 = (short)DAT_febebf1c;
    }
    else {
      DAT_febebf40 = (short)iVar1;
    }
  }
  return;
}



/* Constant-block fill: 9 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

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



void FUN_000c2cc0(void)

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
  return;
}



/* Constant-block fill: 52 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_c2d3e(void)

{
  DAT_febebf98 = 0;
  DAT_febebf70 = 0;
  DAT_febebf74 = 0;
  DAT_febebf78 = 0;
  DAT_febebf7c = 0;
  DAT_febebf9a = 0;
  DAT_febebf9c = 0;
  DAT_febebf9e = 0;
  DAT_febebf50 = 0;
  DAT_febebfae = 0;
  DAT_febebfaf = 0;
  DAT_febebfb0 = 0;
  DAT_febebfb1 = 0;
  DAT_febebfb2 = 0;
  DAT_febebfb3 = 0;
  DAT_febebfb4 = 0;
  DAT_febebfb5 = 0;
  DAT_febebf6c = 0x22;
  DAT_febebfb6 = 0;
  DAT_febebf84 = 0;
  DAT_febebfb7 = 0;
  DAT_febebfb8 = 0;
  DAT_febebf54 = 0;
  DAT_febebf80 = 0;
  DAT_febebf58 = 0;
  DAT_febebfa0 = 0;
  DAT_febebf5c = 0;
  DAT_febebfa2 = 0;
  DAT_febebf60 = 0;
  DAT_febebfa4 = 0;
  DAT_febebf64 = 0;
  DAT_febebfa6 = 0;
  DAT_febebf68 = 0;
  DAT_febebfa8 = 0;
  DAT_febebfb9 = 0;
  DAT_febeaba0 = 0;
  DAT_febebfba = 0;
  DAT_febebfbb = 0;
  DAT_febebfbc = 0;
  DAT_febebfbd = 0;
  DAT_febebfbe = 0;
  DAT_febebfbf = 0;
  DAT_febebfc0 = 0;
  DAT_febebfaa = 0;
  DAT_febebfac = 0;
  DAT_febebf88 = 0;
  DAT_febebf8c = 0;
  DAT_febebf90 = 0;
  DAT_febebf94 = 0;
  DAT_febebfc1 = 0;
  DAT_febebfc2 = 0;
  DAT_febebfc3 = 0;
  return;
}



/* Clear ABA4,BFC4,BF6D,BF6E,BFC5; not a whole raw-estimator reset. Clear external observer term and
   qualifiers only; */

void f33_clear_observer_source_term(void)

{
  DAT_febeaba4 = 0;
  DAT_febebfc4 = 0;
  DAT_febebf6d = 0;
  DAT_febebf6e = 0;
  DAT_febebfc5 = 0;
  return;
}



/* WARNING: Removing unreachable block (ram,0x000c2eae) */
/* WARNING: Removing unreachable block (ram,0x000c2e9a) */
/* WARNING: Removing unreachable block (ram,0x000c2e78) */
/* WARNING: Removing unreachable block (ram,0x000c2e4c) */

void FUN_000c2e2a(void)

{
  uint uVar1;
  short sVar2;
  
  DAT_febebf78 = -DAT_febeaeec;
  DAT_febebf98 = DAT_febeadf2;
  uVar1 = ((uint)DAT_febeae3a * 0x1e4) / 0x40000;
  if ((uVar1 != 0) && (DAT_febebf70 = (int)DAT_febeadf2 << 4, uVar1 != 0)) {
    if (DAT_febebf70 == -0x80000000 && uVar1 == 0xffffffff) {
      DAT_febebf70 = -0x80000000;
    }
    else {
      DAT_febebf70 = DAT_febebf70 / (int)uVar1;
    }
  }
  DAT_febebf74 = (int)((int)DAT_febecc64 * (uint)DAT_febeae5a) / 0x2000;
  DAT_febebf9a = DAT_febec172;
  DAT_febebf9c = DAT_febec1a2;
  sVar2 = (short)(((uint)DAT_febeae38 * 0x18) / 0x400);
  DAT_febebf7c = (int)(short)(((uint)DAT_febeae38 * 0x666) / 0x100000) * (int)(short)DAT_febeacc5 +
                 (int)sVar2 * (int)DAT_febeadfe;
  DAT_febebf50 = (int)sVar2 * (int)DAT_febeaed0;
  DAT_febebf9e = DAT_febeae44;
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



/* Sequential initializer chain: 7 unconditional calls and no other statements; shape-verified. The
   called sequence is the function's entire behavior; chain family members differ in callee sets. */

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



void FUN_000c310e(void)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  
  if (DAT_febebfb0 == 'Z') {
    DAT_febebf54 = (DAT_febeaf00 + DAT_febebf54) - DAT_febebf80;
    DAT_febebf80 = DAT_febebf54 * 0x400;
    if (DAT_000af560 != 0) {
      if (DAT_febebf80 == -0x80000000 && DAT_000af560 == -1) {
        DAT_febebf80 = -0x80000000;
      }
      else {
        DAT_febebf80 = DAT_febebf80 / DAT_000af560;
      }
    }
  }
  if (DAT_febebfb1 == 'Z') {
    DAT_febebf58 = (DAT_febebf58 + DAT_febeae0c) - (int)DAT_febebfa0;
    iVar1 = DAT_febebf58 * 0x400;
    if (DAT_000af564 != 0) {
      if (iVar1 == -0x80000000 && DAT_000af564 == -1) {
        iVar1 = 0;
      }
      else {
        iVar1 = iVar1 / DAT_000af564;
      }
    }
    DAT_febebfa0 = (short)iVar1;
  }
  if (DAT_febebfb2 == 'Z') {
    uVar5 = 0;
    if (-1 < (int)DAT_febeaef0) {
      uVar5 = DAT_febeaef0 & 0xffff;
    }
    uVar4 = 0;
    if (-1 < (int)DAT_febeaef4) {
      uVar4 = DAT_febeaef4 & 0xffff;
    }
    uVar3 = 0;
    if (-1 < (int)DAT_febeaef8) {
      uVar3 = DAT_febeaef8 & 0xffff;
    }
    uVar2 = 0;
    if (-1 < (int)DAT_febeaefc) {
      uVar2 = DAT_febeaefc & 0xffff;
    }
    DAT_febebf5c = (DAT_febebf5c + uVar5) - (uint)DAT_febebfa2;
    uVar5 = DAT_febebf5c * 0x400;
    if (DAT_000af568 != 0) {
      uVar5 = uVar5 / DAT_000af568;
    }
    DAT_febebfa2 = (ushort)uVar5;
    DAT_febebf60 = (DAT_febebf60 + uVar4) - (uint)DAT_febebfa4;
    uVar5 = DAT_febebf60 * 0x400;
    if (DAT_000af568 != 0) {
      uVar5 = uVar5 / DAT_000af568;
    }
    DAT_febebfa4 = (ushort)uVar5;
    DAT_febebf64 = (DAT_febebf64 + uVar3) - (uint)DAT_febebfa6;
    uVar5 = DAT_febebf64 * 0x400;
    if (DAT_000af568 != 0) {
      uVar5 = uVar5 / DAT_000af568;
    }
    DAT_febebfa6 = (ushort)uVar5;
    DAT_febebf68 = (DAT_febebf68 + uVar2) - (uint)DAT_febebfa8;
    uVar5 = DAT_febebf68 * 0x400;
    if (DAT_000af568 != 0) {
      uVar5 = uVar5 / DAT_000af568;
    }
    DAT_febebfa8 = (ushort)uVar5;
  }
  return;
}



/* WARNING: Removing unreachable block (ram,0x000c326c) */
/* WARNING: Removing unreachable block (ram,0x000c325c) */

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



/* Sequential initializer chain: 4 unconditional calls and no other statements; shape-verified. The
   called sequence is the function's entire behavior; chain family members differ in callee sets. */

void f33_run_init_chain_c3292(void)

{
  FUN_000c2e2a();
  f33_run_init_chain_c30ea();
  FUN_000c310e();
  FUN_000c3228();
  return;
}



/* Publish ABA4=low32(-AC18) and BFC4=AC02 before observer sampling. Refresh ABA4 with low32
   negation ofAC18 and BFC4 fromAC02 before sampling. */

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



/* Snapshot inputs before PMRFFC0, then publish BFD4->ABA0, BFD8->BF88, C074->BF8C, C080->BF90,
   BF50->BF94 plus acquisition/mode/status bytes and BFEC/BFEE limits. ABA0 is the acquired
   reference, not accepted sampleBFD8; publication is not hardware freshness. Snapshot before PMR
   then publish referenceBFD4->ABA0 separately from sampleBFD8->BF88, differenceC074->BF8C and
   centerC080->BF90, with source/status/limit copies. */

void f33_publish_raw_estimator_state(void)

{
  undefined1 uVar1;
  undefined1 uVar2;
  undefined1 uVar3;
  undefined1 uVar4;
  undefined1 uVar5;
  undefined4 uVar6;
  undefined1 uVar7;
  undefined1 uVar8;
  undefined4 uVar9;
  undefined4 uVar10;
  undefined2 uVar11;
  undefined2 uVar12;
  undefined1 uVar13;
  undefined1 uVar14;
  undefined4 uVar15;
  undefined4 uVar16;
  undefined1 uVar17;
  undefined1 uVar18;
  uint32_t puVar19;
  undefined4 uVar20;
  
  uVar18 = DAT_febec08b;
  uVar17 = DAT_febec08a;
  uVar16 = DAT_febec080;
  uVar15 = DAT_febec074;
  uVar14 = DAT_febebff1;
  uVar13 = DAT_febebff0;
  uVar12 = DAT_febebfee;
  uVar11 = DAT_febebfec;
  uVar10 = DAT_febebfd8;
  uVar9 = DAT_febebfd4;
  uVar8 = DAT_febebfb6;
  uVar7 = DAT_febebfae;
  uVar6 = DAT_febebf50;
  uVar5 = DAT_febead5c;
  uVar4 = DAT_febead3f;
  uVar3 = DAT_febead3c;
  uVar2 = DAT_febead1a;
  uVar1 = DAT_febeacbd;
  puVar19 = 0xfebeb800u;
  uVar20 = FUN_000d1da0(0xffc0);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar19 + (uint32_t)(0x7bf))))) = uVar4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar19 + (uint32_t)(0x7c0))))) = uVar5;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar19 + 0x7aa)))) = uVar11;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar19 + (uint32_t)(0x7c1))))) = uVar8;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar19 + 0x7ac)))) = uVar12;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar19 + (uint32_t)(0x7c2))))) = uVar1;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar19 + (uint32_t)(0x7b9))))) = uVar13;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar19 + -0xc60)))) = uVar9;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar19 + (uint32_t)(0x7ba))))) = uVar7;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar19 + (uint32_t)(0x7bb))))) = uVar14;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar19 + (uint32_t)(0x7bc))))) = uVar3;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar19 + (uint32_t)(0x7bd))))) = uVar18;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar19 + (uint32_t)(0x7be))))) = uVar17;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar19 + 0x788)))) = uVar10;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar19 + 0x78c)))) = uVar15;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar19 + 0x790)))) = uVar16;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar19 + 0x794)))) = uVar6;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar19 + (uint32_t)(0x7c3))))) = uVar2;
  FUN_000d1dc6(uVar20);
  return;
}



/* Under PMRFFC0 clear ABA0, published BF88..BF94, BF B9..C3 status bytes and BFAA/BFAC limits. Does
   not itself clear the underlying BFD4 acquisition reference. Protected clear of published
   reference/source/status/limit copies does not itself reset underlying acquisition referenceBFD4.
    */

void f33_clear_published_estimator_state(void)

{
  uint32_t puVar1;
  undefined4 uVar2;
  
  puVar1 = 0xfebeb800u;
  uVar2 = FUN_000d1da0(0xffc0);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x7b9))))) = 0;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0xc60)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x7ba))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x7bb))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x7bc))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x7bd))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x7be))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x7bf))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x7c0))))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + 0x7aa)))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + 0x7ac)))) = 0;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x788)))) = 0;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x78c)))) = 0;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x790)))) = 0;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x794)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x7c1))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x7c2))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x7c3))))) = 0;
  FUN_000d1dc6(uVar2);
  return;
}



void FUN_000c3444(void)

{
  uint32_t puVar1;
  undefined4 uVar2;
  
  puVar1 = 0xfebeb800u;
  DAT_febebfd8 = 0;
  DAT_febebff1 = 0;
  DAT_febebfe8 = 0;
  DAT_febebfc8 = 0;
  DAT_febebfcc = 0;
  DAT_febebfd0 = 0;
  uVar2 = FUN_000d1da0(0xffc0);
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x7d4)))) = 0;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x7e4)))) = 0xffffffff;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x7f0))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x7f2))))) = 0xff;
  FUN_000d1dc6(uVar2);
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + 0x7ea)))) = 0;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x7dc)))) = 0;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x7e0)))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + 0x7ec)))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + 0x7ee)))) = 0;
  return;
}



/* WARNING: Removing unreachable block (ram,0x000c34e2) */
/* Return signed correction in R10, also storeBFD0; former void inference lost it.
   BFC8=low32(BF7C-BF70); normalize its abs32 with low32 left shift10, unsigned division byAE38 and
   capFFFF (zero coefficient gives input0). MapAF5CE; low32 multiply byAE38, signed divide1024
   intoBFCC, then negate when BFC8>=0. Preserve wrap and division order. Signed correction return
   inR10 is consumed by reference acquisition. Preserve low32 shift/product, unsigned coefficient
   normalization, signed divide1024 and sign reversal from BF7C-BF70. Previous void prototype lost
   dataflow. */

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



/* Require BFF1/BFB7==5A, BFC5/BFC4==0, wrapped abs16(BF9C)<160 and abs16(BF98)<512. D095E returns
   -32768 for INT16_MIN, so that raw value passes both signed comparisons. Increment u16BFE8; only
   count>10 withC0DE==5A publishes. Elapsed count pins10 even if C0DE rejects; failed outer gate
   resets0. BFD4=correction+BF78-BF84-BF7C+BFD8+BF70 with low32 arithmetic; under PMRFFC0 publish
   inverseBFE4,validBFF0=5A,markerBFF2=A5. Signed amplitude gates use wrapping D095E: INT16_MIN
   returns-32768 and passes both comparisons, confirmed natively. Commit otherwise requires
   incremented warmup>10 andC0DE5A; publish algebraic reference and inverse/markers under PMRFFC0.
   Physical producer domain is not established. */

void f33_acquire_external_estimator_reference(void)

{
  int iVar1;
  uint uVar2;
  ushort uVar3;
  char cVar4;
  char cVar5;
  char cVar6;
  char cVar7;
  uint32_t puVar8;
  short sVar9;
  short sVar10;
  undefined4 uVar11;
  int iVar12;
  int iVar13;
  ushort uVar14;
  
  cVar7 = DAT_febebff1;
  cVar6 = DAT_febebfc5;
  cVar5 = DAT_febebfc4;
  cVar4 = DAT_febebfb7;
  sVar10 = DAT_febebf98;
  puVar8 = 0xfebeb800u;
  iVar13 = (int)DAT_000af578;
  iVar12 = (int)DAT_000af57a;
  sVar9 = f33_abs_s16_wrapping(DAT_febebf9c);
  sVar10 = f33_abs_s16_wrapping(sVar10);
  uVar3 = DAT_000af57c;
  if (((((cVar7 == 'Z') && (cVar6 == '\0')) && (cVar5 == '\0')) &&
      ((iVar1 = sVar9 - iVar13, iVar1 < 0 != (sVar9 < 0 != iVar13 < 0 && iVar13 < 0 == iVar1 < 0) &&
       (iVar13 = sVar10 - iVar12,
       iVar13 < 0 != (sVar10 < 0 != iVar12 < 0 && iVar12 < 0 == iVar13 < 0))))) && (cVar4 == 'Z')) {
    uVar14 = (*((short *)camry_host_ptr((uint32_t)(puVar8 + 0x7e8)))) + 1U;
    if ((DAT_000af57c < (ushort)((*((short *)camry_host_ptr((uint32_t)(puVar8 + 0x7e8)))) + 1U)) &&
       (uVar14 = uVar3, (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar8 + (uint32_t)(0x8de))))) == 'Z')) {
      iVar12 = f33_estimator_reference_correction();
      uVar2 = iVar12 + ((*((int *)camry_host_ptr((uint32_t)(puVar8 + 0x778)))) -
                       ((((*((int *)camry_host_ptr((uint32_t)(puVar8 + 0x784)))) + (*((int *)camry_host_ptr((uint32_t)(puVar8 + 0x77c))))) -
                        (*((int *)camry_host_ptr((uint32_t)(puVar8 + 0x7d8))))) - (*((int *)camry_host_ptr((uint32_t)(puVar8 + 0x770))))));
      uVar11 = FUN_000d1da0(0xffc0);
      (*((uint *)camry_host_ptr((uint32_t)(puVar8 + 0x7d4)))) = uVar2;
      (*((uint *)camry_host_ptr((uint32_t)(puVar8 + 0x7e4)))) = ~uVar2;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar8 + (uint32_t)(0x7f0))))) = 0x5a;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar8 + (uint32_t)(0x7f2))))) = 0xa5;
      FUN_000d1dc6(uVar11);
    }
  }
  else {
    uVar14 = 0;
  }
  (*((ushort *)camry_host_ptr((uint32_t)(puVar8 + 0x7e8)))) = uVar14;
  return;
}



/* Clear model windowBFEA and accumulatorsBFDC/BFE0 before the external-reference warmup/commit.
   Accepted sample and committed estimator reference are distinct states. External acquisition
   selection clears the model window/count before invoking its independent warmup/commit path. */

void f33_select_external_reference_acquisition(void)

{
  DAT_febebfea = 0;
  DAT_febebfdc = 0;
  DAT_febebfe0 = 0;
  f33_acquire_external_estimator_reference();
  return;
}



/* BFC5!=0 clears model accumulators/count. Otherwise failed C045/C044/C042==5A, AD18==11
   orADF4>=3840 gate HOLDS them. Qualified passes accumulate signed BF78/2000 and BF78%2000. At
   incremented u16count>=2000 publish quotient-sum+remainder-sum/2000 and inverse/markers under
   PMRFFC0, then CLEAR accumulators/count. Counts are invocations. Model quotient/remainder
   window2000 preserves accumulators on interrupted qualification, clears on BFC5!=0, and clears
   after protected reference publication. Successful publication does not retain the window. */

void f33_accumulate_model_estimator_reference(void)

{
  undefined *puVar1;
  ushort uVar2;
  undefined *puVar3;
  uint32_t puVar4;
  undefined4 uVar5;
  int iVar6;
  uint uVar7;
  int iVar8;
  
  puVar4 = 0xfebeb800u;
  puVar3 = ((undefined *)camry_host_ptr(0xfebeb800u));
  puVar1 = ((undefined *)camry_host_ptr(0xfebeb800u));
  if (DAT_febebfc5 == '\0') {
    iVar8 = DAT_febebfdc;
    iVar6 = DAT_febebfe0;
    uVar2 = DAT_febebfea;
    if ((((DAT_febec045 != 'Z') || (DAT_febec044 != 'Z')) || (DAT_febec042 != 'Z')) ||
       ((DAT_febead18 != '\x11' || (DAT_febeadf4 < DAT_000af57e)))) goto LAB_000c367c;
    uVar7 = (uint)f33_estimator_reference_window;
    uVar2 = (ushort)(DAT_febebfea + 1);
    if (uVar7 == 0) {
      iVar6 = 0x11;
      iVar8 = DAT_febebf78;
    }
    else if (DAT_febebf78 == -0x80000000 && uVar7 == 0xffffffff) {
      iVar6 = 0;
      iVar8 = -0x80000000;
    }
    else {
      iVar6 = DAT_febebf78 % (int)uVar7;
      iVar8 = DAT_febebf78 / (int)uVar7;
    }
    iVar8 = DAT_febebfdc + iVar8;
    iVar6 = DAT_febebfe0 + iVar6;
    if ((DAT_febebfea + 1 & 0xffff) < uVar7) goto LAB_000c367c;
    if (uVar7 != 0) {
      if (iVar6 == -0x80000000 && uVar7 == 0xffffffff) {
        iVar6 = -0x80000000;
      }
      else {
        iVar6 = iVar6 / (int)uVar7;
      }
    }
    uVar5 = FUN_000d1da0(0xffc0);
    (*((int *)camry_host_ptr((uint32_t)(puVar4 + 0x7d4)))) = iVar6 + iVar8;
    (*((int *)camry_host_ptr((uint32_t)(puVar4 + 0x7e4)))) = ~(iVar6 + iVar8);
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x7f0))))) = 0x5a;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x7f2))))) = 0xa5;
    FUN_000d1dc6(uVar5);
    puVar1 = ((undefined *)camry_host_ptr((uint32_t)(puVar4)));
  }
  puVar3 = puVar1;
  iVar8 = 0;
  iVar6 = 0;
  uVar2 = 0;
LAB_000c367c:
  *(int *)(puVar3 + 0x7dc) = iVar8;
  *(int *)(puVar3 + 0x7e0) = iVar6;
  *(ushort *)(puVar3 + 0x7ea) = uVar2;
  return;
}



/* Invalidate accepted-external markerBFF1, warmupBFE8, source markerBFFA and countBFF8 before model
   accumulation. A failed model qualifier can still retain its prior window. Model fallback clears
   external acceptance/warmup and source count/marker before model accumulation; model qualification
   failure can retain its independent window. */

void f33_select_model_reference_acquisition(void)

{
  DAT_febebff1 = 0;
  DAT_febebfe8 = 0;
  DAT_febebffa = 0;
  DAT_febebff8 = 0;
  f33_accumulate_model_estimator_reference();
  return;
}



/* CopyBFF4->BFD8 and setBFF1=5A. AD3C==1 orAD3E==2 selects external acquisition; otherwise AD3E==1
   selects model acquisition, which clears the accepted marker again. Other combinations retain the
   sample without invoking either acquisition channel. Latch BFF4 intoBFD8 and accepted marker.
   AD3C1 orAD3E2 selects external acquisition; remainingAD3E1 selects model; other combinations
   invoke neither. Acceptance is not reference commitment. */

void f33_latch_estimator_external_sample(void)

{
  DAT_febebfd8 = DAT_febebff4;
  DAT_febebff1 = 0x5a;
  if ((DAT_febead3c == '\x01') || (DAT_febead3e == '\x02')) {
    f33_select_external_reference_acquisition();
  }
  else if (DAT_febead3e == '\x01') {
    f33_select_model_reference_acquisition();
  }
  return;
}



/* Without BFF0==5A retain BFEC/BFEE. With valid reference and BFFA==5A map BFF8 through AF570[BFB8]
   into both. Otherwise selectAF582 or mode2AF584; BOTH exact defaults are8000 (little-endian401F),
   not320/500. No local BFB8 bounds check. Until reference valid retain limits; then external marker
   selects curve byBFB8/BFF8 or defaults. Exact AF582/AF584 are both8000, not320/500. No local
   curve-index bound. */

void f33_update_estimator_source_limits(void)

{
  uint32_t puVar1;
  undefined *puVar2;
  ushort uVar3;
  ushort uVar4;
  
  puVar1 = 0xfebeb800u;
  puVar2 = ((undefined *)camry_host_ptr(0xfebeb800u));
  uVar3 = DAT_febebfec;
  uVar4 = DAT_febebfee;
  if (DAT_febebff0 == 'Z') {
    if (DAT_febebffa == 'Z') {
      uVar3 = FUN_000d0896(((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xaf570u + (uint32_t)(DAT_febebfb8) * 4u))))))), DAT_febebff8);
      puVar2 = ((undefined *)camry_host_ptr((uint32_t)(puVar1)));
      uVar4 = uVar3;
    }
    else {
      puVar2 = ((undefined *)camry_host_ptr(0xfebeb800u));
      uVar3 = f33_estimator_source_limit_default;
      uVar4 = f33_estimator_source_limit_default;
      if (DAT_febead3c == '\x02') {
        uVar3 = f33_estimator_source_limit_mode2;
        uVar4 = f33_estimator_source_limit_mode2;
      }
    }
  }
  *(ushort *)(puVar2 + 0x7ec) = uVar3;
  *(ushort *)(puVar2 + 0x7ee) = uVar4;
  return;
}



/* BFB6!=5A clears accepted marker, both acquisition counters and model accumulators. Otherwise
   AD3C==0/3 holds state; every other byte admits selection. Mode2 choosesAF7D0, othersAF7CE
   (both1). BFFA/BFAF==5A and BFF8>=threshold accept the external sample; otherwise select model
   accumulation. Finally update source limits. Native selection distinguishes accepted sample from
   reference commit at warmup boundary; model publication clears its window while qualifier
   interruption preserves it. Exact mode predicate admits every byte except0/3; physical identities
   and elapsed time remain bounded. */

void f33_select_estimator_acquisition_source(void)

{
  if (DAT_febebfb6 == 'Z') {
    if ((DAT_febead3c != '\0') && (DAT_febead3c != '\x03')) {
      DAT_febec088 = f33_estimator_lower_band_default;
      if (DAT_febead3c == '\x02') {
        DAT_febec088 = f33_estimator_lower_band_mode2;
      }
      if (((DAT_febebffa == 'Z') && (DAT_febebfaf == 'Z')) && (DAT_febec088 <= DAT_febebff8)) {
        f33_latch_estimator_external_sample();
      }
      else {
        f33_select_model_reference_acquisition();
      }
      f33_update_estimator_source_limits();
    }
  }
  else {
    DAT_febebff1 = 0;
    DAT_febebfe8 = 0;
    DAT_febebfea = 0;
    DAT_febebfdc = 0;
    DAT_febebfe0 = 0;
  }
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_c37b8(void)

{
  return;
}



/* Snapshot AF04/AE0E/ACEC intoBFF4/BFF8/BFFA for separate publication retention gates. Snapshot
   published projection/count/qualification into separate retained interface consumed by publication
   retention gates. */

void f33_snapshot_retained_estimator_projection(void)

{
  DAT_febebff4 = DAT_febeaf04;
  DAT_febebff8 = DAT_febeae0e;
  DAT_febebffa = DAT_febeacec;
  return;
}



/* Conditionally copyC07C/countC0B4 toAF04/AE0E using observer state, acceptance and prior
   snapshotBFFA/BFF8. Some BFFA5A branches hold values while publishingACEC5A; qualification is not
   freshness. Observed reset first clearsC07C/BFFA. Conditional projection/count publication depends
   on prior marker/count and observer state. Some retained-marker paths hold values while asserting
   qualification; qualification is not a fresh-copy witness. */

void f33_publish_retained_estimator_projection(void)

{
  char cVar1;
  ushort uVar2;
  undefined1 uVar3;
  uint32_t puVar4;
  undefined4 uVar5;
  
  puVar4 = 0xfebeb800u;
  uVar5 = FUN_000d1da0(0xffc0);
  uVar2 = (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + 0x8b4))));
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x890)))));
  FUN_000d1dc6(uVar5);
  if (cVar1 == 'Z') {
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar4 + 0x87c)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x7fa))))) = 0;
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x7fa))))) == 'Z') {
    cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x88e)))));
    if ((((cVar1 == '\x11') || (cVar1 == '\"')) && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x7f1))))) == 'Z')) &&
       ((*((ushort *)camry_host_ptr((uint32_t)(puVar4 + 0x7f8)))) <= uVar2)) goto LAB_000c385e;
    if (((cVar1 == '\0') && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x7f1))))) == 'Z')) && ((*((ushort *)camry_host_ptr((uint32_t)(puVar4 + 0x7f8)))) <= uVar2))
    goto LAB_000c3870;
  }
  else {
    if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x7fa))))) != '\0') ||
       ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x88e))))) != '\x11' && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x88e))))) != '\"')) || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x7f1))))) != 'Z')))) {
LAB_000c3870:
      uVar3 = 0;
      goto LAB_000c3872;
    }
LAB_000c385e:
    (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + -0x9f2)))) = uVar2;
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar4 + -0x8fc)))) = (*((undefined4 *)camry_host_ptr((uint32_t)(puVar4 + 0x87c))));
  }
  uVar3 = 0x5a;
LAB_000c3872:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0xb14))))) = uVar3;
  return;
}



/* Constant-block fill: 35 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_c387a(void)

{
  DAT_febec00c = 0;
  DAT_febec00e = 0;
  DAT_febec010 = 0;
  DAT_febec012 = 0;
  DAT_febec014 = 0;
  DAT_febec016 = 0;
  DAT_febec018 = 0;
  DAT_febec01a = 0;
  DAT_febec01c = 0;
  DAT_febec01e = 0;
  DAT_febec020 = 0;
  DAT_febec022 = 0;
  DAT_febec024 = 0;
  DAT_febec026 = 0;
  DAT_febec028 = 0;
  DAT_febec02e = 0;
  DAT_febebffc = 0;
  DAT_febec034 = 0;
  DAT_febec038 = 0;
  DAT_febec03c = 0;
  DAT_febec000 = 0;
  DAT_febec004 = 0;
  DAT_febec008 = 0;
  DAT_febec03e = 0;
  DAT_febec042 = 0;
  DAT_febec02f = 0;
  DAT_febec02a = 0;
  DAT_febec02c = 0;
  DAT_febec043 = 0;
  DAT_febec040 = 0;
  DAT_febec044 = 0;
  DAT_febec045 = 0;
  DAT_febec030 = 0;
  DAT_febec031 = 0;
  DAT_febec032 = 0;
  return;
}



/* WARNING: Removing unreachable block (ram,0x000c39b6) */
/* WARNING: Removing unreachable block (ram,0x000c39f0) */
/* Always refresh five C0B4-indexed scalesC00C..14; exact maps are flat1024. Only AD18==11 refreshes
   axisADF6 maps and composite thresholdsC016..28. AD3F==2 selects separate but numerically
   identical curves:584,218,102,384,40. Other AD18 holds those thresholds. Source-count scales
   always refresh and are flat1024; axis/composite thresholds update only forAD1811, otherwise hold.
   Mode-selected curves are separate but numerically identical. */

void f33_refresh_estimator_qualifier_thresholds(void)

{
  bool bVar1;
  char cVar2;
  char cVar3;
  ushort input;
  undefined2 uVar4;
  uint32_t puVar5;
  ushort uVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  int iVar10;
  int iVar11;
  int iVar12;
  int iVar13;
  int iVar14;
  int iVar15;
  
  uVar4 = DAT_febec0b4;
  input = DAT_febeadf6;
  cVar3 = DAT_febead3f;
  cVar2 = DAT_febead18;
  puVar5 = 0xfebeb800u;
  iVar7 = FUN_000d0896(((undefined *)camry_host_ptr(0xaf634u)),DAT_febec0b4);
  iVar8 = FUN_000d0896(((undefined *)camry_host_ptr(0xaf648u)),uVar4);
  iVar9 = FUN_000d0896(((undefined *)camry_host_ptr(0xaf65cu)),uVar4);
  iVar10 = FUN_000d0896(((undefined *)camry_host_ptr(0xaf670u)),uVar4);
  uVar6 = FUN_000d0896(((undefined *)camry_host_ptr(0xaf684u)),uVar4);
  if (cVar2 == '\x11') {
    bVar1 = cVar3 == '\x02';
    iVar11 = FUN_000d0896(((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd2f10u + (uint32_t)(bVar1) * 4u))))))), input);
    iVar12 = f33_interpolate_unsigned_axis_sentinel_curve
                       (((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd2f18u + (uint32_t)(bVar1) * 4u)))))),input);
    iVar13 = FUN_000d0896(((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd2f20u + (uint32_t)(bVar1) * 4u))))))), input);
    iVar14 = f33_interpolate_unsigned_axis_sentinel_curve
                       (((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd2f28u + (uint32_t)(bVar1) * 4u)))))),input);
    iVar15 = FUN_000d0896(((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd2f30u + (uint32_t)(bVar1) * 4u))))))), input);
    (*((short *)camry_host_ptr((uint32_t)(puVar5 + 0x81e)))) = (short)iVar15;
    (*((short *)camry_host_ptr((uint32_t)(puVar5 + 0x820)))) = (short)((uint)(iVar11 * iVar7) >> 10);
    (*((short *)camry_host_ptr((uint32_t)(puVar5 + 0x816)))) = (short)iVar11;
    (*((short *)camry_host_ptr((uint32_t)(puVar5 + 0x822)))) = (short)((iVar12 * iVar8) / 0x400);
    (*((short *)camry_host_ptr((uint32_t)(puVar5 + 0x824)))) = (short)((uint)(iVar13 * iVar9) >> 10);
    (*((short *)camry_host_ptr((uint32_t)(puVar5 + 0x818)))) = (short)iVar12;
    (*((short *)camry_host_ptr((uint32_t)(puVar5 + 0x826)))) = (short)((iVar14 * iVar10) / 0x400);
    (*((short *)camry_host_ptr((uint32_t)(puVar5 + 0x828)))) = (short)(iVar15 * (uint)uVar6 >> 10);
    (*((short *)camry_host_ptr((uint32_t)(puVar5 + 0x81a)))) = (short)iVar13;
    (*((short *)camry_host_ptr((uint32_t)(puVar5 + 0x81c)))) = (short)iVar14;
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + 0x80c)))) = (short)iVar7;
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + 0x80e)))) = (short)iVar8;
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + 0x810)))) = (short)iVar9;
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + 0x812)))) = (short)iVar10;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar5 + 0x814)))) = uVar6;
  return;
}



/* C02E is5A except when AD3F==2 and eitherAD5C!=2 or abs32(s16AE40)>=unsignedC028. The signed16
   input is widened before abs32, not passed through wrapping abs16. Mode2 requiresAD5C2 and widened
   signed16 AE40 absolute value below unsignedC028. Other modes publishC02E5A; distinct from
   wrapping abs16. */

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



/* WARNING: Removing unreachable block (ram,0x000c3ad0) */
/* Count0 reseeds max/minC000/C004 toBF78; otherwise extend extrema. Wrapped spread must be strictly
   below80*AE38/1024. Incremented u16 count>10 pins10 and publishes5A; earlier admitted counts
   retain oldC042. Failed spread clears count/status. Count0 reseeds source extrema; subsequent
   calls extend them. Strict spread gate then strict count>10 maturity; earlier admission
   retainsC042, rejection clears count/status. */

void f33_advance_estimator_stability_window(ushort *count,uchar *qualified)

{
  int iVar1;
  ushort uVar2;
  int iVar3;
  int iVar4;
  uchar uVar5;
  
  iVar3 = DAT_febebf78;
  iVar4 = DAT_febebf78;
  if (((*count != 0) &&
      (iVar3 = DAT_febec004,
      DAT_febebf78 - DAT_febec000 < 0 !=
      (DAT_febebf78 < 0 != DAT_febec000 < 0 && DAT_febec000 < 0 == DAT_febebf78 - DAT_febec000 < 0)
      || DAT_febebf78 == DAT_febec000)) &&
     (iVar3 = DAT_febebf78, iVar4 = DAT_febec000,
     DAT_febebf78 - DAT_febec004 < 0 ==
     (DAT_febebf78 < 0 != DAT_febec004 < 0 && DAT_febec004 < 0 == DAT_febebf78 - DAT_febec004 < 0)))
  {
    iVar3 = DAT_febec004;
  }
  DAT_febec008 = iVar4 - iVar3;
  iVar1 = (int)(f33_estimator_stability_spread_scale * (uint)DAT_febeae38) / 0x400;
  if (DAT_febec008 - iVar1 < 0 ==
      (DAT_febec008 < 0 != iVar1 < 0 && iVar1 < 0 == DAT_febec008 - iVar1 < 0)) {
    uVar2 = 0;
    uVar5 = '\0';
  }
  else {
    uVar2 = *count + 1;
    uVar5 = DAT_febec042;
    if (f33_estimator_stability_window < uVar2) {
      uVar5 = 'Z';
      uVar2 = f33_estimator_stability_window;
    }
  }
  DAT_febec000 = iVar4;
  DAT_febec004 = iVar3;
  *count = uVar2;
  *qualified = uVar5;
  return;
}



/* Refresh source-mode gate even if outer AD3F0/3, BFC5!=0 orAC02!=0 rejects. Admitted path clamps
   low32(BF74+s16BF98) symmetrically16, updatesC034 by input-oldC03C, then low32 shift10 /8672 and
   narrowing toC03C. Wrapped abs16(output)<signedC026, abs16(BF9C)<160 andC02E5A admit the extrema
   window; rejection clearsC03E/C042. Source mode and qualifiers gate retained low32 filter; narrow
   before wrapped abs16 comparisons. Successful amplitude checks admit extrema window; rejection
   clearsC03E/C042 but is not a reset of every internal cell. */

void f33_qualify_estimator_source_stability(void)

{
  char cVar1;
  char cVar2;
  char cVar3;
  uint32_t puVar4;
  short sVar5;
  short sVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  uchar uStack_17;
  ushort uStack_16;
  
  cVar3 = DAT_febebfc5;
  cVar2 = DAT_febead3f;
  cVar1 = DAT_febeac02;
  puVar4 = 0xfebeb800u;
  f33_update_estimator_source_mode_gate();
  if ((((cVar2 != '\0') && (cVar2 != '\x03')) && (cVar3 == '\0')) && (cVar1 == '\0')) {
    iVar8 = (*((int *)camry_host_ptr((uint32_t)(puVar4 + 0x774)))) + (int)(*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x798))));
    if (iVar8 + -0x7fff < 0 == (iVar8 < 0 && -1 < iVar8 + -0x7fff) && iVar8 != 0x7fff) {
      iVar7 = 0x7fff;
    }
    else {
      iVar7 = (int)(short)iVar8;
      if (iVar8 + 0x7fff < 0 != (-1 < iVar8 && iVar8 + 0x7fff < 0)) {
        iVar7 = -0x7fff;
      }
    }
    (*((int *)camry_host_ptr((uint32_t)(puVar4 + 0x7fc)))) = iVar8;
    iVar9 = f33_estimator_stability_filter_divisor;
    cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x82e)))));
    iVar8 = ((*((int *)camry_host_ptr((uint32_t)(puVar4 + 0x834)))) + iVar7) - (int)(*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x83c))));
    (*((int *)camry_host_ptr((uint32_t)(puVar4 + 0x834)))) = iVar8;
    uStack_16 = (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + 0x83e))));
    iVar8 = iVar8 * 0x400;
    if (iVar9 != 0) {
      if (iVar8 == -0x80000000 && iVar9 == -1) {
        iVar8 = -0x80000000;
      }
      else {
        iVar8 = iVar8 / iVar9;
      }
    }
    sVar6 = (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x79c))));
    iVar9 = (int)f33_estimator_stability_amplitude_limit;
    (*((int *)camry_host_ptr((uint32_t)(puVar4 + 0x838)))) = iVar8;
    (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x83c)))) = (short)iVar8;
    sVar5 = f33_abs_s16_wrapping((short)iVar8);
    sVar6 = f33_abs_s16_wrapping(sVar6);
    iVar7 = (int)(*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x826))));
    iVar8 = sVar5 - iVar7;
    if (((iVar8 < 0 != (sVar5 < 0 != iVar7 < 0 && iVar7 < 0 == iVar8 < 0)) &&
        (iVar8 = sVar6 - iVar9, iVar8 < 0 != (sVar6 < 0 != iVar9 < 0 && iVar9 < 0 == iVar8 < 0))) &&
       (cVar1 == 'Z')) {
      f33_advance_estimator_stability_window(&uStack_16,&uStack_17);
      goto LAB_000c3bc2;
    }
  }
  uStack_16 = 0;
  uStack_17 = '\0';
LAB_000c3bc2:
  (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + 0x83e)))) = uStack_16;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x842))))) = uStack_17;
  return;
}



/* Real grouped status selector12hex nonzero resetsC02A and inhibitsC02F5A. Zero increments u16
   count; reaching inclusive40 pins40 and clears inhibition in that invocation. Nonzero grouped
   status12hex resets count and inhibits. Zero status reaches inclusive40 to clear inhibition in the
   same invocation, unlike strict stability-window maturity. */

void f33_update_estimator_group_release(void)

{
  ushort uVar1;
  uint32_t puVar2;
  uchar uVar3;
  undefined1 uVar4;
  
  puVar2 = 0xfebeb800u;
  uVar3 = f33_get_application_grouped_status(0x12);
  uVar4 = 0x5a;
  if (uVar3 == '\0') {
    uVar1 = (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0x82a)))) + 1;
    if (f33_estimator_group_release_window <= uVar1) {
      uVar4 = 0;
      uVar1 = f33_estimator_group_release_window;
    }
  }
  else {
    uVar1 = 0;
    uVar4 = 0x5a;
  }
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0x82a)))) = uVar1;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x82f))))) = uVar4;
  return;
}



/* Mean of four unsignedBFA2/4/6/8 samples must be nonzero. Either normalized cross-pair difference
   >=7 percent rejects and setsC0435A. Require pair difference<C024, abs32(BF80)<C020,
   abs32(s16BFA0)<signedC022 andBFB0/BFB15A. Incremented count>10 pins10/publishes5A; earlier
   admission retainsC044. Rejection clears count/status. Nonzero four-sample mean and normalized
   cross-pair mismatch<7 percent precede strict amplitude/pair bounds and producer validity.
   Count>10 matures; zero mean or rejection clears count/status. */

void f33_advance_estimator_pair_window(ushort *count,uchar *qualified)

{
  short sVar1;
  char cVar2;
  char cVar3;
  uchar uVar4;
  uint32_t puVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  uint uVar9;
  uint uVar10;
  uint uVar11;
  char cVar12;
  uint uVar13;
  uint uVar14;
  ushort uVar15;
  
  puVar5 = 0xfebeb800u;
  uVar10 = (uint)DAT_febebfa4;
  uVar11 = (uint)DAT_febebfa2;
  uVar9 = (uint)DAT_febebfa8;
  uVar15 = *count;
  uVar13 = uVar9 + (uint)DAT_febebfa6 + uVar10 + uVar11 >> 2;
  uVar14 = uVar13 & 0xffff;
  DAT_febec02c = (ushort)uVar13;
  if (uVar14 == 0) {
    uVar4 = '\0';
    cVar12 = '\0';
    uVar15 = DAT_febec02c;
  }
  else {
    puVar5 = 0xfebeb800u;
    iVar6 = f33_abs_s32_wrapping(uVar11 - DAT_febebfa6);
    iVar7 = f33_abs_s32_wrapping(uVar10 - uVar9);
    iVar6 = iVar6 * 100;
    iVar7 = iVar7 * 100;
    if (uVar14 != 0) {
      if (iVar6 == -0x80000000 && uVar14 == 0xffffffff) {
        iVar6 = -0x80000000;
      }
      else {
        iVar6 = iVar6 / (int)uVar14;
      }
    }
    if (uVar14 != 0) {
      if (iVar7 == -0x80000000 && uVar14 == 0xffffffff) {
        iVar7 = -0x80000000;
      }
      else {
        iVar7 = iVar7 / (int)uVar14;
      }
    }
    iVar8 = iVar6 - (uint)f33_estimator_pair_percent_limit;
    if ((iVar8 < 0 == (iVar6 < 0 && -1 < iVar8)) ||
       (iVar6 = iVar7 - (uint)f33_estimator_pair_percent_limit,
       iVar6 < 0 == (iVar7 < 0 && -1 < iVar6))) {
      cVar12 = 'Z';
    }
    else {
      cVar12 = '\0';
    }
    cVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(0x7b0)))));
    cVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(0x7b1)))));
    sVar1 = (*((short *)camry_host_ptr((uint32_t)(puVar5 + 0x7a0))));
    iVar6 = f33_abs_s32_wrapping((*((int *)camry_host_ptr((uint32_t)(puVar5 + 0x780)))));
    iVar7 = f33_abs_s32_wrapping((int)sVar1);
    iVar8 = f33_abs_s32_wrapping(uVar11 - uVar10);
    if (((((int)(iVar8 - (uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar5 + 0x824))))) < 0 ==
           (iVar8 < 0 && -1 < (int)(iVar8 - (uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar5 + 0x824))))))) || (cVar12 != '\0')
         ) || (cVar2 != 'Z')) ||
       ((((int)(iVar6 - (uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar5 + 0x820))))) < 0 ==
          (iVar6 < 0 && -1 < (int)(iVar6 - (uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar5 + 0x820)))))) || (cVar3 != 'Z')) ||
        (iVar6 = (int)(*((short *)camry_host_ptr((uint32_t)(puVar5 + 0x822)))),
        iVar7 - iVar6 < 0 == (iVar7 < 0 != iVar6 < 0 && iVar6 < 0 == iVar7 - iVar6 < 0))))) {
      uVar4 = '\0';
      uVar15 = 0;
    }
    else {
      uVar4 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(0x844)))));
      uVar15 = uVar15 + 1;
      if (f33_estimator_pair_window < uVar15) {
        uVar4 = 'Z';
        uVar15 = f33_estimator_pair_window;
      }
    }
  }
  *count = uVar15;
  *qualified = uVar4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(0x843))))) = cVar12;
  return;
}



/* Always update grouped release. BFB25A andC02F0 admit paired window; otherwise clearC040/C044 but
   leave pair-mismatchC043 unchanged because the window did not run. Always update grouped
   release;BFB25A/C02F0 admit paired window. Otherwise clearC040/C044 while retaining mismatchC043
   because its producer did not run. */

void f33_qualify_estimator_paired_sources(void)

{
  uint32_t puVar1;
  uchar uStack_7;
  ushort uStack_6;
  
  puVar1 = 0xfebeb800u;
  f33_update_estimator_group_release();
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x7b2))))) == 'Z') && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x82f))))) == '\0')) {
    uStack_6 = (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + 0x840))));
    f33_advance_estimator_pair_window(&uStack_6,&uStack_7);
  }
  else {
    uStack_6 = 0;
    uStack_7 = '\0';
  }
  (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + 0x840)))) = uStack_6;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x844))))) = uStack_7;
  return;
}



/* Return5A only for BFB3/BFB4/BF46 zero and wrapped abs16(AE06/AE04)<=1; otherwise0. Return5A only
   forBFB3/BFB4/BF46 zero and wrapped abs16 AE06/AE04 within inclusive signed1 limits. */

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



/* AD3C other than2 returns5A. Mode2 requires wrapped abs16(AE4C/AE50)<=1 andAD34/AD35 zero. AD3C2
   alone adds wrapped abs16 AE4C/AE50<=1 and zeroAD34/AD35 requirements; other modes return5A. */

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



/* AD3F other than2 returns5A. Mode2 requires wrapped abs16(AE4E/AE52)<=1 andAD34/AD35 zero. AD3F2
   adds independent AE4E/AE52 amplitude constraints and zeroAD34/AD35; other modes return5A. */

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



/* Always compute/store three source constraintsC030..32. C0455A additionally requires both
   AD3C/AD3F outside0/3, AD1811, BFB25A, BFB50 and absolute paired mean minusADF6 strictly
   below1280. This is not the same gate as either consecutive window. Always publish three
   constraint results; compositeC045 additionally requires admitted modes/source markers and
   paired-mean axis difference strictly below1280. No consecutive-window counter. */

void f33_qualify_estimator_source_constraints(void)

{
  char cVar1;
  char cVar2;
  char cVar3;
  undefined1 uVar4;
  uint32_t puVar5;
  uint uVar6;
  uint uVar7;
  uint uVar8;
  int iVar9;
  uint uVar10;
  
  puVar5 = 0xfebeb800u;
  uVar6 = f33_estimator_base_source_constraint();
  uVar7 = f33_estimator_mode2_constraint_a();
  uVar8 = f33_estimator_mode2_constraint_b();
  if (((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0xac4))))) != '\0') && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0xac4))))) != '\x03')) && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0xac1))))) != '\0')) &&
     ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0xac1))))) != '\x03')) {
    cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0xae8)))));
    cVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(0x7b2)))));
    cVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(0x7b5)))));
    uVar10 = (uint)f33_estimator_pair_axis_margin;
    iVar9 = f33_abs_s32_wrapping
                      (camry_host_addr(((undefined *)camry_host_ptr((uint32_t)(((uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar5 + 0x7a2)))) + (uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar5 + 0x7a4)))) >> 1)
                       - (uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar5 + -0xa0a)))))))));
    if (((((cVar2 == 'Z') && (cVar1 == '\x11')) &&
         (((int)(iVar9 - uVar10) < 0 != (iVar9 < 0 && -1 < (int)(iVar9 - uVar10)) &&
          ((cVar3 == '\0' && (uVar6 == 0x5a)))))) && (uVar7 == 0x5a)) && (uVar8 == 0x5a)) {
      uVar4 = 0x5a;
      goto LAB_000c3ec8;
    }
  }
  uVar4 = 0;
LAB_000c3ec8:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(0x845))))) = uVar4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(0x830))))) = (char)uVar6;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(0x831))))) = (char)uVar7;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(0x832))))) = (char)uVar8;
  return;
}



void FUN_000c3edc(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  f33_fill_constant_block_c2d3e();
  f33_initialize_secondary_estimator_stability();
  f33_fill_constant_block_c387a();
  FUN_000c3444();
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x874)))) = 0;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x848)))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + 0x860)))) = 1;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + 0x862)))) = 1;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x84c)))) = 0;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x878)))) = 0;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x850)))) = 0;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x854)))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + 0x864)))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + 0x866)))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + 0x868)))) = 0;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x87c)))) = 0;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x858)))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + 0x888)))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + 0x86a)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x86e))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x88a))))) = 0;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x85c)))) = 0;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x880)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x88b))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x86f))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x88c))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x88d))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x870))))) = 0;
  return;
}



/* Reset external-source acquisition throughC2E14, then C084,C06C,C08E/F and C090/91. Sibling
   estimator, acquisition verdicts and cross-rate interface have separate reset owners. Reset
   external estimator state then clear observer rate, threshold, state/qualification and associated
   flags. Other qualifier/deadband reset owners remain separate. */

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



/* When C091==5A setC080=C0B0,C078=low32(C0B0<<11),C08D=5A; otherwise clearC08D. The requestC091
   remains set until its separate consumer acknowledges it. RequestC0915A reseeds centerC080 and
   shifted accumulatorC078, setsackC08D but does not consume request. Subsequent acquisition reset
   can overwrite the seeded center. */

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



/* C090==5A clears reference/inverse validity, acquisition windows, model qualifiers, limits,
   difference tracker and center; setsC08C=5A. Does not clear requestC090 or accepted sampleBFD8.
   Without request only clear acknowledgementC08C. RequestC0905A clears reference validity,
   acquisition/tracking windows and center; acknowledgesC08C but retains request and accepted
   sampleBFD8. No request clears acknowledgement only. */

void f33_apply_estimator_acquisition_reset(void)

{
  undefined1 uVar1;
  uint32_t puVar2;
  undefined4 uVar3;
  
  puVar2 = 0xfebeb800u;
  if (DAT_febec090 == 'Z') {
    puVar2 = 0xfebeb800u;
    uVar3 = FUN_000d1da0(0xffc0);
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0x7d4)))) = 0;
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0x7e4)))) = 0xffffffff;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x7f0))))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x7f2))))) = 0xff;
    FUN_000d1dc6(uVar3);
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x7f1))))) = 0;
    uVar1 = 0x5a;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x7fa))))) = 0;
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0x784)))) = 0;
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + 0x7e8)))) = 0;
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + 0x7ea)))) = 0;
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0x7dc)))) = 0;
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0x7e0)))) = 0;
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + 0x83e)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x842))))) = 0;
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + 0x840)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x844))))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x843))))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x845))))) = 0;
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + 0x864)))) = 0;
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0x84c)))) = 0;
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + 0x7ec)))) = 0;
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + 0x7ee)))) = 0;
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + 0x868)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x86e))))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x88b))))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x88a))))) = 0;
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0x880)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x86f))))) = 0;
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0x834)))) = 0;
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0x838)))) = 0;
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0x878)))) = 0;
  }
  else {
    uVar1 = 0;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x88c))))) = uVar1;
  return;
}


