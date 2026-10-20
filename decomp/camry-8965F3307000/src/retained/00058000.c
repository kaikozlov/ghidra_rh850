#include "common.h"

void return_only_stub_5802a(void)

{
  return;
}

void fill_constant_block_5802e(void)

{
  DAT_febeed01 = 0;
  DAT_febeed02 = 0;
  DAT_febeed03 = 0;
  DAT_febeed04 = ((int)(int16_t)DAT_febe7e0c);
  DAT_febeed06 = DAT_febe81e6;
  DAT_febeed08 = DAT_febe81e8;
  DAT_febeed0a = DAT_febe81ea;
  DAT_febeed0c = DAT_febe81ec;
  DAT_febeed0e = DAT_febe81ee;
  DAT_febeed10 = DAT_febe81f0;
  DAT_febeed00 = DAT_febe8a1c;
  DAT_febeed12 = ((int)(int16_t)DAT_febe7df8);
  return;
}

void return_only_stub_58070(void)

{
  return;
}

void publish_foreground_ecu_outputs(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  DAT_febef204 = monitor_current_staged_calibration.marker;
  published_internal_source_admission_state = internal_source_admission_state;
  DAT_febef001 = DAT_febe7f70;
  DAT_febef16a = DAT_febe7f3a;
  DAT_febef002 = dtc_setting_inhibit_request;
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -7;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebef003u + (uint32_t)(iVar3) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7fb8u + (uint32_t)(iVar3) * 1u))));
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  DAT_febef16c = ((int)(int16_t)DAT_febe6f36);
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -3;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebef00bu + (uint32_t)(iVar3) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7f9eu + (uint32_t)(iVar3) * 1u))));
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  DAT_febef16e = ((int)(int16_t)DAT_febe6f12);
  DAT_febef170 = ((int)(int16_t)DAT_febe6eae);
  DAT_febef208 = DAT_febe6af0;
  DAT_febef172 = DAT_febe6ae4;
  DAT_febef00f = DAT_febe6adc;
  DAT_febef010 = DAT_febe6add;
  DAT_febef174 = ((int)(int16_t)DAT_febe6f82);
  DAT_febef20c = DAT_febe6ac4;
  DAT_febef210 = DAT_febe6abc;
  DAT_febef214 = DAT_febe6ac0;
  DAT_febef176 = DAT_febe6a82;
  DAT_febef011 = DAT_febe6a78;
  DAT_febef012 = DAT_febe6a7a;
  DAT_febef178 = ((int)(int16_t)DAT_febe707a);
  DAT_febef17a = ((int)(int16_t)DAT_febe707c);
  DAT_febef013 = DAT_febe6878;
  DAT_febef014 = DAT_febe687b;
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -2;
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebef17cu + (uint32_t)(iVar3) * 2u)))) = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7014u + (uint32_t)(iVar3) * 2u))));
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -0x11;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebef015u + (uint32_t)(iVar3) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe85f4u + (uint32_t)(iVar3) * 1u))));
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  DAT_febef027 = DAT_febe7dcc;
  DAT_febef02c = DAT_febe7ff2;
  DAT_febef182 = ((int)(int16_t)DAT_febe7dda);
  DAT_febef028 = 1;
  DAT_febef02d = DAT_febe7ff0;
  DAT_febef050 = DAT_febe8030;
  DAT_febef188 = 0xe000;
  DAT_febef029 = 0;
  DAT_febef02a = 0;
  DAT_febef038 = DAT_febe7ffb;
  DAT_febef192 = ((int)(int16_t)DAT_febe800e);
  DAT_febef02b = 0;
  DAT_febef039 = DAT_febe7ffa;
  DAT_febef053 = DAT_febe8029;
  DAT_febef02e = 1;
  DAT_febef18a = DAT_febe7ff8;
  DAT_febef042 = 3;
  DAT_febef054 = DAT_febe802d;
  DAT_febef02f = 0;
  DAT_febef04c = DAT_febe8009;
  DAT_febef055 = DAT_febe802c;
  DAT_febef030 = 1;
  DAT_febef04d = DAT_febe8006;
  DAT_febef031 = 0;
  DAT_febef032 = 0;
  DAT_febef033 = 1;
  DAT_febef04e = DAT_febe8007;
  DAT_febef034 = 0;
  DAT_febef035 = 0;
  DAT_febef036 = 0;
  DAT_febef04f = route30_receive_status;
  DAT_febef051 = route30_receive_status;
  DAT_febef057 = route30_receive_status;
  DAT_febef058 = route30_receive_status;
  DAT_febef037 = 1;
  DAT_febef03a = 1;
  DAT_febef03b = 0;
  DAT_febef194 = ((int)(int16_t)DAT_febe8014);
  DAT_febef03c = 0;
  DAT_febef03d = 0;
  DAT_febef03e = 0;
  DAT_febef059 = DAT_febe8021;
  DAT_febef03f = 0;
  DAT_febef040 = 0;
  DAT_febef041 = 0;
  DAT_febef196 = ((int)(int16_t)DAT_febe801e);
  DAT_febef043 = 0;
  DAT_febef044 = 0;
  DAT_febef045 = 0;
  DAT_febef198 = ((int)(int16_t)DAT_febe8152);
  DAT_febef046 = 1;
  DAT_febef047 = 0;
  DAT_febef048 = 0;
  DAT_febef05c = DAT_febe80de;
  DAT_febef049 = DAT_febe8081;
  DAT_febef04a = DAT_febe807c;
  DAT_febef04b = DAT_febe807c;
  DAT_febef05d = DAT_febe80e4;
  DAT_febef052 = DAT_febe8031;
  DAT_febef056 = DAT_febe7d40;
  DAT_febef05a = 1;
  DAT_febef065 = DAT_febe803a;
  DAT_febef05b = 0;
  DAT_febef05e = 1;
  DAT_febef05f = 0;
  DAT_febef066 = DAT_febe8039;
  DAT_febef060 = 1;
  DAT_febef061 = 0;
  DAT_febef062 = 0;
  published_route31_numeric_scalar = route31_numeric_scalar;
  DAT_febef063 = 0;
  DAT_febef064 = 0;
  DAT_febef070 = 1;
  DAT_febef067 = DAT_febe8038;
  DAT_febef071 = 0;
  DAT_febef072 = 0;
  DAT_febef073 = 0;
  DAT_febef068 = DAT_febe804d;
  DAT_febef074 = 0;
  DAT_febef075 = 0;
  DAT_febef076 = 0;
  DAT_febef069 = DAT_febe8052;
  DAT_febef077 = 0;
  DAT_febef078 = 0;
  DAT_febef079 = 0;
  DAT_febef06a = DAT_febe8051;
  DAT_febef07a = 1;
  DAT_febef06b = DAT_febe804e;
  DAT_febef06c = 2;
  DAT_febef07b = 0;
  DAT_febef07c = 0;
  DAT_febef07d = 0;
  DAT_febef06d = DAT_febe804c;
  DAT_febef07e = 0;
  DAT_febef07f = 0;
  DAT_febef06e = DAT_febe8050;
  DAT_febef19e = ((int)(int16_t)DAT_febe804a);
  DAT_febef184 = 0;
  DAT_febef186 = 0;
  DAT_febef18c = 0;
  DAT_febef1a0 = ((int)(int16_t)DAT_febe8048);
  DAT_febef18e = 0;
  DAT_febef190 = 0;
  DAT_febef19a = 0;
  DAT_febef06f = ((int)(int8_t)DAT_febe804f);
  DAT_febef080 = 0;
  DAT_febef081 = 0;
  DAT_febef082 = 1;
  DAT_febef1aa = ((int)(int16_t)DAT_febe805e);
  DAT_febef088 = 0;
  DAT_febef089 = 0;
  DAT_febef08a = 1;
  DAT_febef083 = DAT_febe8065;
  DAT_febef08b = 1;
  DAT_febef08c = 0;
  DAT_febef08d = 0;
  DAT_febef1ac = ((int)(int16_t)DAT_febe805c);
  DAT_febef090 = DAT_febe806f;
  DAT_febef19c = 0;
  DAT_febef1a2 = 0;
  DAT_febef084 = DAT_febe8064;
  DAT_febef1a4 = 0;
  DAT_febef1a6 = 0;
  DAT_febef1a8 = 0;
  DAT_febef1ae = ((int)(int16_t)DAT_febe8062);
  DAT_febef1b2 = 0;
  DAT_febef1b4 = 0;
  DAT_febef1c0 = 0;
  DAT_febef085 = DAT_febe8067;
  DAT_febef1c2 = 0;
  DAT_febef1c4 = 0;
  DAT_febef1d2 = 0;
  DAT_febef1b0 = ((int)(int16_t)DAT_febe8060);
  DAT_febef1d4 = 0;
  DAT_febef1d6 = 0;
  DAT_febef1d8 = 0;
  DAT_febef086 = DAT_febe8066;
  DAT_febef1da = 0;
  DAT_febef1dc = 0;
  DAT_febef1de = 0;
  DAT_febef087 = DAT_febe8069;
  DAT_febef08e = DAT_febe8079;
  DAT_febef08f = DAT_febe806c;
  DAT_febef091 = DAT_febe807f;
  DAT_febef092 = DAT_febe806d;
  DAT_febef093 = DAT_febe80a5;
  DAT_febef1b6 = DAT_febe809a;
  DAT_febef1b8 = DAT_febe809c;
  DAT_febef1ba = DAT_febe809e;
  DAT_febef094 = DAT_febe80a0;
  DAT_febef095 = DAT_febe80a1;
  DAT_febef096 = DAT_febe80a2;
  DAT_febef0a2 = DAT_febe807c;
  DAT_febef0a0 = DAT_febe80d5;
  DAT_febef1bc = ((int)(int16_t)DAT_febe8072);
  DAT_febef1c6 = ((int)(int16_t)DAT_febe808a);
  DAT_febef097 = DAT_febe8076;
  DAT_febef1c8 = ((int)(int16_t)DAT_febe808c);
  DAT_febef098 = 0;
  DAT_febef1be = ((int)(int16_t)DAT_febe8074);
  DAT_febef0a4 = DAT_febe8090;
  DAT_febef099 = 0;
  DAT_febef09a = 1;
  DAT_febef09b = DAT_febe8098;
  DAT_febef0a5 = DAT_febe8092;
  DAT_febef09c = 1;
  DAT_febef09d = DAT_febe8095;
  DAT_febef09e = DAT_febe8094;
  DAT_febef0a6 = DAT_febe8091;
  DAT_febef09f = 1;
  DAT_febef0a1 = DAT_febe80d3;
  DAT_febef0a3 = DAT_febe8081;
  DAT_febef0a7 = DAT_febe8093;
  DAT_febef0a8 = DAT_febe8098;
  DAT_febef0a9 = DAT_febe8098;
  DAT_febef0aa = 0;
  DAT_febef0ab = 0;
  DAT_febef0ac = 1;
  DAT_febef0ad = DAT_febe8095;
  DAT_febef0ae = DAT_febe8094;
  DAT_febef0af = DAT_febe8095;
  DAT_febef0b0 = DAT_febe8094;
  DAT_febef0c2 = DAT_febe8081;
  DAT_febef0c3 = 0;
  DAT_febef0c4 = 0;
  DAT_febef1ca = ((int)(int16_t)DAT_febe808e);
  DAT_febef0c5 = 0;
  DAT_febef0c6 = 0;
  DAT_febef0c7 = 0;
  DAT_febef21c = DAT_febe68b4;
  DAT_febef0c8 = 0;
  DAT_febef0c9 = 0;
  DAT_febef1e0 = DAT_febe7bf8;
  DAT_febef0b1 = DAT_febe7bb9;
  DAT_febef1e2 = 0;
  DAT_febef1e4 = 0;
  DAT_febef0b2 = DAT_febe7bb8;
  DAT_febef1e6 = 0;
  DAT_febef1e8 = 0;
  DAT_febef1ea = 0;
  DAT_febef0b3 = DAT_febe7bba;
  DAT_febef1ec = 0;
  DAT_febef1ee = 0;
  DAT_febef1f0 = 0;
  DAT_febef220 = DAT_febe6efc;
  DAT_febef1f2 = 0;
  DAT_febef1f4 = 0;
  DAT_febef1f6 = 0;
  DAT_febef0b4 = DAT_febe8022;
  DAT_febef1f8 = 0;
  DAT_febef0b5 = DAT_febe8023;
  DAT_febef0b6 = DAT_febe8024;
  DAT_febef0b7 = DAT_febe8025;
  DAT_febef0b8 = DAT_febe8004;
  DAT_febef0b9 = DAT_febe8003;
  DAT_febef0ba = DAT_febe8002;
  DAT_febef0bb = DAT_febe80cf;
  DAT_febef0bc = DAT_febe80d0;
  DAT_febef0bd = DAT_febe80ce;
  DAT_febef0be = DAT_febe80d1;
  DAT_febef0bf = DAT_febe80cd;
  DAT_febef0c0 = DAT_febe80b6;
  DAT_febef0c1 = DAT_febe8078;
  DAT_febef1cc = 0;
  DAT_febef1ce = 0;
  DAT_febef1d0 = 0;
  DAT_febef0ca = 0;
  DAT_febef0cb = 0;
  DAT_febef0cc = 0;
  DAT_febef0cd = 0;
  DAT_febef0ce = 0;
  DAT_febef0cf = 0;
  DAT_febef0d0 = 0;
  DAT_febef0d1 = 0;
  DAT_febef0d2 = 0;
  DAT_febef0d3 = 0;
  DAT_febef0d4 = 0;
  DAT_febef0d5 = 1;
  DAT_febef0d6 = 0;
  DAT_febef0d7 = 0;
  DAT_febef0d8 = 0;
  DAT_febef0d9 = 0;
  DAT_febef0da = 0;
  DAT_febef0db = 1;
  DAT_febef0dc = 0;
  DAT_febef0dd = 0;
  DAT_febef0de = 0;
  DAT_febef0df = 0;
  DAT_febef0e0 = 0;
  DAT_febef0e1 = 0;
  DAT_febef0e2 = 0;
  DAT_febef0f1 = DAT_febe803f;
  DAT_febef0e3 = 0;
  DAT_febef0e4 = 0;
  DAT_febef0e5 = 0;
  DAT_febef0f2 = DAT_febe8040;
  DAT_febef0e6 = 0;
  DAT_febef0e7 = 1;
  DAT_febef0e8 = 0;
  DAT_febef0f3 = DAT_febe8041;
  DAT_febef0e9 = 0;
  DAT_febef0ea = 0;
  DAT_febef0eb = 1;
  DAT_febef0f4 = DAT_febe8042;
  DAT_febef0ec = 0;
  DAT_febef0ed = 0;
  DAT_febef0ee = 0;
  DAT_febef0f5 = DAT_febe8043;
  DAT_febef0ef = 1;
  DAT_febef0f0 = DAT_febe8010;
  DAT_febef0f9 = 0;
  DAT_febef0f6 = DAT_febe8044;
  DAT_febef0fa = 1;
  DAT_febef0fb = DAT_febe8031;
  DAT_febef0f7 = DAT_febe8045;
  DAT_febef0f8 = DAT_febe8046;
  DAT_febef0fc = DAT_febe803b;
  DAT_febef0fd = DAT_febe803c;
  DAT_febef0fe = DAT_febe803e;
  DAT_febef10e = DAT_febe8010;
  DAT_febef103 = 0;
  DAT_febef0ff = DAT_febe8016;
  DAT_febef10f = DAT_febe7ffc;
  DAT_febef104 = 0;
  DAT_febef100 = DAT_febe8018;
  DAT_febef110 = DAT_febe8000;
  DAT_febef105 = 0;
  DAT_febef101 = DAT_febe800c;
  DAT_febef111 = DAT_febe8001;
  DAT_febef106 = 0;
  DAT_febef102 = DAT_febe800a;
  DAT_febef112 = DAT_febe7ffd;
  DAT_febef107 = 0;
  DAT_febef10c = DAT_febe7474;
  DAT_febef113 = DAT_febe7ffe;
  DAT_febef108 = 0;
  DAT_febef10d = DAT_febe8013;
  DAT_febef114 = DAT_febe7fff;
  DAT_febef109 = 0;
  DAT_febef10a = 0;
  DAT_febef10b = 0;
  DAT_febef115 = DAT_febe8027;
  DAT_febef119 = 0;
  DAT_febef11a = 0;
  DAT_febef11b = 1;
  DAT_febef116 = DAT_febe802a;
  DAT_febef11c = 0;
  DAT_febef117 = DAT_febe8026;
  DAT_febef118 = DAT_febe806e;
  DAT_febef130 = DAT_febe80bc;
  DAT_febef11d = 0;
  DAT_febef11e = 0;
  DAT_febef11f = 0;
  DAT_febef131 = DAT_febe80bd;
  DAT_febef120 = 0;
  DAT_febef121 = 0;
  DAT_febef122 = 0;
  DAT_febef123 = 1;
  DAT_febef124 = 0;
  DAT_febef125 = 0;
  DAT_febef126 = 0;
  DAT_febef127 = 0;
  DAT_febef128 = 0;
  DAT_febef129 = 1;
  DAT_febef12a = 0;
  DAT_febef12b = 0;
  DAT_febef12c = 0;
  DAT_febef12d = 0;
  DAT_febef12e = 0;
  DAT_febef12f = 1;
  DAT_febef1fa = ((int)(int16_t)DAT_febe80b8);
  DAT_febef13b = 0;
  DAT_febef142 = 0;
  DAT_febef143 = 0;
  DAT_febef1fc = ((int)(int16_t)DAT_febe80ba);
  DAT_febef144 = 0;
  DAT_febef132 = DAT_febe80be;
  DAT_febef133 = DAT_febe80bf;
  DAT_febef134 = DAT_febe80c0;
  DAT_febef135 = DAT_febe80c1;
  DAT_febef136 = DAT_febe80c2;
  DAT_febef137 = DAT_febe80c3;
  DAT_febef138 = DAT_febe80c4;
  DAT_febef139 = DAT_febe80c5;
  DAT_febef13a = DAT_febe80c6;
  DAT_febef13c = DAT_febe80c7;
  DAT_febef13d = DAT_febe80c8;
  DAT_febef13e = DAT_febe80c9;
  published_route30_consumed_generation = route30_consumed_generation;
  DAT_febef224 = DAT_febe80ac;
  DAT_febef140 = DAT_febe80b4;
  DAT_febef228 = DAT_febe80b0;
  DAT_febef141 = DAT_febe8032;
  DAT_febef145 = DAT_febe817c;
  DAT_febef1fe = ((int)(int16_t)DAT_febe8168);
  DAT_febef146 = DAT_febe813b;
  DAT_febef22c = DAT_febe8178;
  DAT_febef148 = 1;
  DAT_febef149 = 1;
  DAT_febef153 = 1;
  DAT_febef147 = DAT_febe7dcd;
  DAT_febef14c = 0;
  DAT_febef200 = ((int)(int16_t)DAT_febe7fd0);
  DAT_febef14a = DAT_febe8033;
  DAT_febef14e = 0;
  DAT_febef154 = DAT_febe7fe0;
  DAT_febef14b = DAT_febe8082;
  DAT_febef14f = 0;
  DAT_febef155 = DAT_febe80cb;
  DAT_febef14d = DAT_febe80ca;
  DAT_febef150 = 0;
  DAT_febef151 = 0;
  DAT_febef156 = DAT_febe80d6;
  DAT_febef152 = 0;
  DAT_febef162 = DAT_febe806e;
  DAT_febef163 = DAT_febe806f;
  DAT_febef157 = DAT_febe80d8;
  DAT_febef158 = DAT_febe80cc;
  DAT_febef159 = DAT_febe8019;
  DAT_febef15a = DAT_febe801a;
  DAT_febef15b = DAT_febe80a8;
  DAT_febef15c = DAT_febe80a9;
  DAT_febef15d = DAT_febe80aa;
  DAT_febef15e = DAT_febe80ab;
  DAT_febef15f = DAT_febe8070;
  DAT_febef202 = DAT_febe806a;
  DAT_febef160 = DAT_febe801b;
  DAT_febef161 = DAT_febe801c;
  DAT_febef164 = DAT_febe80a6;
  DAT_febef165 = DAT_febe80a7;
  DAT_febef166 = DAT_febe8005;
  DAT_febef167 = DAT_febe800d;
  DAT_febef168 = DAT_febe80d2;
  return;
}

void return_only_stub_58802(void)

{
  return;
}

int initialize_application_and_request_first_generation(void)

{
  initialize_cold_application_state();
  return publish_redundant_mode_marker_a55a_5889a();
}

void initialize_generated_application_components(void)

{
  initialize_ecu_application_work_state();
  call_initialize_control_application_work_state_fdc14();
  snapshot_initialized_control_publications();
  return;
}

void initialize_cold_application_state(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  publish_redundant_u16(0,((undefined *)camry_host_ptr(0xfebe8c08u)),(ushort *)((undefined *)camry_host_ptr(0xfebe8c0au)),(ushort *)((undefined *)camry_host_ptr(0xfebe8c14u)));
  publish_redundant_u8('\0', ((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x2be6))), ((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x2be5))), ((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x2be4))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x2bea))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x2be9))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x2be7))))) = 0;
  initialize_cold_ecu_input_state();
  call_initialize_cold_control_retained_state_fdc00();
  initialize_generated_application_components();
  return;
}

void reinitialize_application_for_foreground_restart(void)

{
  DAT_febe8c00 = 0;
  DAT_febe8c02 = 0;
  DAT_febe8c04 = 0;
  DAT_febe8c06 = 0;
  DAT_febe8c0c = 0xffff;
  DAT_febe8c0e = 0xffff;
  DAT_febe8c10 = 0xffff;
  DAT_febe8c12 = 0xffff;
  initialize_generated_application_components();
  return;
}

int publish_redundant_mode_marker_a55a_5889a(void)

{
  return publish_redundant_u16(0xa55a,((undefined *)camry_host_ptr(0xfebe8c08u)),(ushort *)((undefined *)camry_host_ptr(0xfebe8c0au)),(ushort *)((undefined *)camry_host_ptr(0xfebe8c14u)));
}

undefined4 test_redundant_status_a5_or_vote_error13_588b6(void)

{
  int iVar1;
  undefined4 uVar2;
  uchar uStack_5;
  
  iVar1 = vote_redundant_u8(((undefined *)camry_host_ptr(0xfebe8c1au)),((undefined *)camry_host_ptr(0xfebe8c1bu)),((undefined *)camry_host_ptr(0xfebe8c1cu)),&uStack_5);
  if ((uStack_5 == 0xa5) || (iVar1 == -0xd)) {
    uVar2 = 0x5a;
  }
  else {
    uVar2 = 0;
  }
  return uVar2;
}

void dispatch_current_control_slice_by_redundant_mode_588e8(void)

{
  ushort previous_mode;
  ushort uVar1;
  uint32_t puVar2;
  undefined4 uVar3;
  
  puVar2 = 0xfebeb800u;
  thunk_snapshot_three_control_input_blocks_fc3cc();
  previous_mode = (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x2c00))));
  uVar1 = (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0x30cc))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x2bea))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x2bea))))) + '\x01';
  if (previous_mode == (ushort)~(*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x2bf4))))) {
    if (uVar1 != previous_mode) {
      uVar3 = thunk_vote_redundant_application_mode_u16_b1c64();
      uVar1 = (ushort)uVar3;
      (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x2c00)))) = uVar1;
      (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x2bf4)))) = ~uVar1;
      dispatch_acquisition_and_fit_mode_entry_bit0_5dc7e(1,uVar3,previous_mode);
      update_mode_owned_current_feedback(1,uVar1,previous_mode);
      ((void)(2), (void)(uVar3), (void)(previous_mode), return_only_stub_5df5a());
      dispatch_current_control_mode_entry_bit1_5df5c(2,uVar3,previous_mode);
      return;
    }
  }
  else {
    (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x2c00)))) = uVar1;
    (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x2bf4)))) = ~uVar1;
  }
  dispatch_acquisition_and_fit_mode_step_bit0_5de82(1,uVar1);
  update_steady_current_feedback(1,uVar1);
  ((void)(2), (void)(uVar1), return_only_stub_5e200());
  run_current_control_and_stage_output(2,uVar1);
  return;
}

undefined4 snapshot_ch1_inputs(void)

{
  undefined4 uVar1;
  
  uVar1 = read_priority_mask_701a0();
  write_priority_mask_preserving_irq_disable_701a6(0xffc0);
  snapshot_application_banks_to_febe6168_5c7b6();
  copy_cell_block_c1b24();
  write_priority_mask_preserving_irq_disable_701a6(uVar1);
  return uVar1;
}

void dispatch_ch1_processing_slice_by_redundant_mode_5899e(void)

{
  ushort uVar1;
  ushort uVar2;
  uint32_t puVar3;
  undefined4 uVar4;
  
  puVar3 = 0xfebeb800u;
  snapshot_ch1_inputs();
  snapshot_request_and_calibration_status_blocks_fc2a0();
  thunk_snapshot_service_pair_and_control_summary_fc462();
  uVar1 = (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x2bfe))));
  uVar2 = (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + 0x30cc))));
  if (uVar1 == (ushort)~(*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x2bf2))))) {
    if (uVar2 != uVar1) {
      uVar4 = thunk_vote_redundant_application_mode_u16_b1c64();
      (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x2bfe)))) = (ushort)uVar4;
      (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x2bf2)))) = ~(ushort)uVar4;
      dispatch_torque_feedback_mode_entry_5e2da(1,uVar4,uVar1);
      call_mode_transition_dispatch_with_service_substitution_fdcf0(1,uVar4,uVar1);
      dispatch_motor_command_mode_entry_5e38e(1,uVar4,uVar1);
      return;
    }
  }
  else {
    (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x2bfe)))) = uVar2;
    (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x2bf2)))) = ~uVar2;
  }
  dispatch_torque_feedback_mode_step_5e3ca(1,uVar2);
  call_mode_steady_dispatch_with_service_substitution_fdd04(1,uVar2);
  dispatch_motor_command_mode_step_5e420(1,uVar2);
  return;
}

undefined4 snapshot_ch2_inputs(void)

{
  undefined4 uVar1;
  
  uVar1 = read_priority_mask_701a0();
  write_priority_mask_preserving_irq_disable_701a6(0xffc0);
  snapshot_ecu_ch2_acquisition();
  call_snapshot_control_ch2_acquisition_fdc3c();
  write_priority_mask_preserving_irq_disable_701a6(0xff80);
  copy_cell_block_5cf1c();
  call_snapshot_control_ch2_feedback_fdc50();
  write_priority_mask_preserving_irq_disable_701a6(uVar1);
  return uVar1;
}

void dispatch_ch2_monitor_slice_by_redundant_mode_58a50(void)

{
  ushort previous_mode;
  ushort uVar1;
  uint32_t puVar2;
  undefined4 uVar3;
  
  puVar2 = 0xfebeb800u;
  snapshot_ch2_inputs();
  thunk_snapshot_admission_metadata_and_eighteen_source_bytes_fcc9c();
  thunk_snapshot_retained_and_coherence_state_to_eb80_block_fd562();
  previous_mode = (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x2bfc))));
  uVar1 = (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0x30cc))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x2be8))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x2be8))))) + '\x01';
  if (previous_mode == (ushort)~(*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x2bf0))))) {
    if (uVar1 != previous_mode) {
      uVar3 = thunk_vote_redundant_application_mode_u16_b1c64();
      uVar1 = (ushort)uVar3;
      (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x2bfc)))) = uVar1;
      (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x2bf0)))) = ~uVar1;
      step_transitioned_channel_monitor_slice(1,uVar1,previous_mode);
      call_mode_transition_dispatch_for_limit_and_assist_groups_fdd18(1,uVar3,previous_mode);
      update_mode_owned_application_requests(1,uVar1,previous_mode);
      return;
    }
  }
  else {
    (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x2bfc)))) = uVar1;
    (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x2bf0)))) = ~uVar1;
  }
  step_steady_channel_monitor_slice(1,uVar1);
  call_mode_steady_dispatch_for_limit_and_assist_groups_fdd2c(1,uVar1);
  update_steady_application_requests(1,uVar1);
  return;
}

void repair_redundant_status_bytes_or_publish_a5_58ad8(void)

{
  int iVar1;
  uchar uStack_11;
  
  iVar1 = vote_redundant_u8(((undefined *)camry_host_ptr(0xfebe8c1au)),((undefined *)camry_host_ptr(0xfebe8c1bu)),((undefined *)camry_host_ptr(0xfebe8c1cu)),&uStack_11);
  if (iVar1 != 0) {
    if (iVar1 != -0xc && iVar1 != -0xb) {
      uStack_11 = 0xa5;
    }
    publish_redundant_u8(uStack_11,((undefined *)camry_host_ptr(0xfebe8c1au)),((undefined *)camry_host_ptr(0xfebe8c1bu)),((undefined *)camry_host_ptr(0xfebe8c1cu)));
  }
  return;
}

undefined4 snapshot_foreground_inputs(void)

{
  undefined4 uVar1;
  
  uVar1 = read_priority_mask_701a0();
  write_priority_mask_preserving_irq_disable_701a6(0xffc0);
  snapshot_ecu_foreground_acquisition();
  call_snapshot_control_foreground_acquisition_fdc64();
  write_priority_mask_preserving_irq_disable_701a6(0xff80);
  copy_cell_block_5d5e0();
  call_snapshot_control_foreground_feedback_fdc78();
  write_priority_mask_preserving_irq_disable_701a6(0xff00);
  snapshot_monitor_inputs();
  call_snapshot_health_and_service_inputs_fdc8c();
  write_priority_mask_preserving_irq_disable_701a6(uVar1);
  return uVar1;
}

void dispatch_foreground_mode_generation(void)

{
  uint8_t stack_record_1f[32];
  camry_fill_bytes(stack_record_1f, sizeof stack_record_1f);
  ushort uVar1;
  ushort uVar2;
  uint32_t puVar3;
  int iVar4;
  undefined4 uVar5;
  ushort *raw;
  ushort *xor5555;
  byte bVar6;
  ushort *xorAAAA;
  uchar *raw_00;
  byte bVar7;
  uchar *xor55;
  uchar *xorAA;
  
  puVar3 = 0xfebeb800u;
  repair_redundant_status_bytes_or_publish_a5_58ad8();
  if ((*((short *)camry_host_ptr((uint32_t)(puVar3 + -0x2bf8)))) == -0x5aa6) {
    raw = ((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x2bf8)));
    xor5555 = ((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x2bf6)));
    xorAAAA = ((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x2bec)));
    iVar4 = read_xor_redundant_u16_with_vote_status_707ac(raw,xor5555,xorAAAA,((int16_t *)((stack_record_1f + 1))));
    if ((iVar4 == 0) && ((*((int16_t *)(stack_record_1f + 1))) == -0x5aa6)) {
      raw_00 = ((undefined *)camry_host_ptr((uint32_t)(puVar3 + -0x2be6)));
      xor55 = ((undefined *)camry_host_ptr((uint32_t)(puVar3 + -0x2be5)));
      xorAA = ((undefined *)camry_host_ptr((uint32_t)(puVar3 + -0x2be4)));
      iVar4 = vote_redundant_u8(raw_00,xor55,xorAA,((uint8_t *)(stack_record_1f)));
      if ((iVar4 == -0xd) || (stack_record_1f[0] != '\0')) {
        stack_record_1f[0] = 0xa5;
      }
      else {
        stack_record_1f[0] = 'Z';
      }
      publish_redundant_u8(stack_record_1f[0],raw_00,xor55,xorAA);
      reinitialize_application_for_foreground_restart();
      snapshot_ch1_inputs();
      snapshot_ch2_inputs();
      snapshot_foreground_inputs();
      call_restart_application_at_mode100_fdd68();
    }
    publish_redundant_u16(0,raw,xor5555,xorAAAA);
  }
  snapshot_foreground_inputs();
  uVar1 = (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x2bfa))));
  uVar2 = (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + 0x30cc))));
  bVar6 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x2be9))))) + 2;
  bVar7 = ~(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x2be9))))) & bVar6 & 0x3e | 1;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x2be7))))) = bVar7;
  if (uVar1 == (ushort)~(*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x2bee))))) {
    if (uVar2 != uVar1) {
      uVar5 = thunk_vote_redundant_application_mode_u16_b1c64();
      (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x2bfa)))) = (ushort)uVar5;
      (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x2bee)))) = ~(ushort)uVar5;
      dispatch_monitor_learning_thermal_mode_entry_5ec24(bVar7,uVar5,uVar1);
      call_control_foreground_transition_dispatch_fdd40(bVar7,uVar5,uVar1);
      dispatch_diagnostic_services_mode_entry_5f464(bVar7,uVar5,uVar1);
      goto LAB_00058c7c;
    }
  }
  else {
    (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x2bfa)))) = uVar2;
    (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x2bee)))) = ~uVar2;
  }
  dispatch_monitor_learning_thermal_mode_step_5f610(bVar7,uVar2);
  call_control_foreground_steady_dispatch_fdd54(bVar7,uVar2);
  dispatch_diagnostic_services_mode_step_5f91c(bVar7,uVar2);
LAB_00058c7c:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x2be9))))) = bVar6;
  return;
}

undefined1 get_state_byte_8c19_58c84(void)

{
  return DAT_febe8c19;
}

undefined1 get_current_control_slice_call_count_58c8a(void)

{
  return DAT_febe8c16;
}

undefined1 get_ch2_monitor_slice_call_count_58c90(void)

{
  return DAT_febe8c18;
}

void initialize_cold_ecu_input_state(void)

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
    *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe7f40u + (uint32_t)(iVar3 * 2) * 1u)))) = 0;
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
    *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe7f44u + (uint32_t)(iVar3 * 2) * 1u)))) = 0;
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
  (*((volatile uint8_t *)camry_host_ptr(0xfebe8012u))) = 0;
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
  (*((volatile uint8_t *)camry_host_ptr(0xfebe80a3u))) = 0;
  DAT_febe809e = 0;
  DAT_febe809c = 0;
  DAT_febe809a = 0;
  DAT_febe8097 = 0;
  (*((volatile uint8_t *)camry_host_ptr(0xfebe8096u))) = 0;
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
  (*((volatile uint8_t *)camry_host_ptr(0xfebe807eu))) = 0;
  (*((volatile uint8_t *)camry_host_ptr(0xfebe807du))) = 0;
  DAT_febe807c = 0;
  (*((volatile uint8_t *)camry_host_ptr(0xfebe807bu))) = 0;
  (*((volatile uint8_t *)camry_host_ptr(0xfebe807au))) = 0;
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
  route30_consumed_generation = '\0';
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
  route31_numeric_scalar = 0xffffffff;
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
  (*((volatile uint8_t *)camry_host_ptr(0xfebe8028u))) = 0xf;
  DAT_febe802a = 0xf;
  (*((volatile uint8_t *)camry_host_ptr(0xfebe802bu))) = 0xf;
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
  route30_receive_status = '\x01';
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
    *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe7090u + (uint32_t)(iVar3 * 4) * 1u)))) = 0;
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
