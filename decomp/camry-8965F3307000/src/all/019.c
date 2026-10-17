#include "common.h"


void FUN_0006405e(void)

{
  int iVar1;
  byte bVar2;
  
  bVar2 = 0;
  Ramffc4ca00 = 0x80000000;
  FUN_00063f24();
  do {
    iVar1 = FUN_00063f94();
    if ((iVar1 != 0) && (1 < bVar2)) {
      FUN_00063ea4(0x11);
    }
    bVar2 = bVar2 + 1;
  } while (iVar1 != 0);
  f33_spin_wait(DAT_00030d9c);
  return;
}



int FUN_000640a0(void)

{
  ushort uVar1;
  uint outer_iterations;
  int iVar2;
  int iVar3;
  undefined8 uVar4;
  int iVar5;
  int iVar6;
  byte bVar7;
  undefined2 local_30;
  undefined2 uStack_2e;
  undefined2 uStack_2c;
  undefined2 uStack_2a;
  undefined2 uStack_28;
  undefined2 uStack_26;
  undefined2 uStack_24;
  undefined2 uStack_22;
  
  uVar4 = 0xfebeb800;
  bVar7 = 0;
  iVar6 = 0xff;
  do {
    uStack_22 = 0x1f00;
    uStack_24 = 0x5018;
    uStack_26 = 0;
    uStack_28 = 0x8250;
    FUN_00061836(&uStack_28);
    outer_iterations = DAT_00030d98;
    f33_spin_wait(DAT_00030d98);
    uStack_2a = 0x1f00;
    uStack_2c = 0x5018;
    uStack_2e = 0;
    local_30 = 0x8250;
    FUN_00061836(&local_30);
    f33_spin_wait(outer_iterations);
    FUN_000614d4();
    uVar1 = (*((ushort *)camry_host_ptr((uint32_t)((int)uVar4 + -0x7fc8))));
    iVar2 = 0;
    if ((uVar1 >> 7 & 1) != 0) {
      iVar2 = 0x5a;
    }
    iVar3 = 0;
    if ((uVar1 >> 8 & 1) != 0) {
      iVar3 = 0x5a;
    }
    iVar5 = FUN_000614b0();
    if (((iVar2 == 0) && (iVar3 == 0)) && (iVar5 == 0)) {
      iVar6 = 0;
    }
    else if (1 < bVar7) {
      iVar6 = 0x11;
    }
    bVar7 = bVar7 + 1;
  } while (iVar6 == 0xff);
  return iVar6;
}



void FUN_0006420e(void)

{
  uchar uVar1;
  byte bVar2;
  
  bVar2 = 0;
  do {
    bVar2 = bVar2 + 1;
    if (3 < bVar2) {
      FUN_00063ea4(0x11);
    }
    ECMMPCMD0 = 0xa5;
    ECMMESET = '\x01';
    ECMMESET = 0xfe;
    ECMMESET = '\x01';
    uVar1 = ECMPS;
  } while (uVar1 != '\0');
  bVar2 = 0;
  do {
    bVar2 = bVar2 + 1;
    if (3 < bVar2) {
      FUN_00063ea4(0x11);
    }
    ECMPCMD1 = 0xa5;
    ECMESSTC2 = 0x10000000;
    ECMESSTC2 = 0xefffffff;
    ECMESSTC2 = 0x10000000;
    uVar1 = ECMPS;
  } while (uVar1 != '\0');
  return;
}



int FUN_0006427a(byte param_1)

{
  uint outer_iterations;
  int iVar1;
  undefined8 uVar2;
  int iVar3;
  byte bVar4;
  bool bVar5;
  undefined2 local_24;
  undefined2 uStack_22;
  undefined2 uStack_20;
  undefined2 uStack_1e;
  undefined2 uStack_1c;
  undefined2 uStack_1a;
  undefined2 uStack_18;
  undefined2 uStack_16;
  
  uVar2 = 0xfebeb800;
  uStack_1c = 0x8200;
  bVar4 = 0;
  iVar3 = 0xff;
  uStack_18 = 0x5018;
  uStack_1a = 0;
  uStack_16 = 0x1f00;
  FUN_00061836(&uStack_1c);
  outer_iterations = DAT_00030d98;
  f33_spin_wait(DAT_00030d98);
  do {
    local_24 = 0x8200;
    uStack_22 = 0;
    uStack_20 = 0x5018;
    uStack_1e = 0x1f00;
    FUN_00061836(&local_24);
    f33_spin_wait(outer_iterations);
    FUN_000614d4();
    iVar1 = 0;
    if (((*((byte *)camry_host_ptr((uint32_t)((int)uVar2 + -0x7fc8)))) & 0x80) != 0) {
      iVar1 = 0x5a;
    }
    if (param_1 < 4) {
      bVar5 = iVar1 == 0;
    }
    else {
      bVar5 = iVar1 == 0x5a;
    }
    if (bVar5) {
      iVar3 = 0;
    }
    else if (1 < bVar4) {
      iVar3 = 0x11;
    }
    bVar4 = bVar4 + 1;
  } while (iVar3 == 0xff);
  return iVar3;
}



void FUN_00064310(void)

{
  uchar uVar1;
  uint uVar2;
  int iVar3;
  byte bVar4;
  byte bVar5;
  
  bVar4 = 0;
  iVar3 = 0xff;
  do {
    bVar5 = 0;
    if (iVar3 == 0) {
      do {
        bVar5 = bVar5 + 1;
        if (3 < bVar5) {
          FUN_00063ea4(0x11);
        }
        ECMPCMD1 = 0xa5;
        ECMESSTC2 = 0x10000000;
        ECMESSTC2 = 0xefffffff;
        ECMESSTC2 = 0x10000000;
        uVar1 = ECMPS;
      } while (uVar1 != '\0');
      f33_spin_wait(DAT_00030d9c);
      return;
    }
    do {
      bVar5 = bVar5 + 1;
      if (3 < bVar5) {
        FUN_00063ea4(0x11);
      }
      ECMPCMD1 = 0xa5;
      ECMESSTC2 = 0x40000000;
      ECMESSTC2 = 0xbfffffff;
      ECMESSTC2 = 0x40000000;
      uVar1 = ECMPS;
    } while (uVar1 != '\0');
    bVar5 = 0;
    do {
      bVar5 = bVar5 + 1;
      if (3 < bVar5) {
        FUN_00063ea4(0x11);
      }
      ECMMPCMD0 = 0xa5;
      ECMMECLR = '\x01';
      ECMMECLR = 0xfe;
      ECMMECLR = '\x01';
      uVar1 = ECMPS;
    } while (uVar1 != '\0');
    bVar5 = 0;
    uVar2 = 0;
    do {
      if (SUB51(((uint5)uVar2 << 1) >> 0x20,0)) {
        iVar3 = 0;
        goto LAB_000643aa;
      }
      uVar2 = ECMMESSTR2;
      bVar5 = bVar5 + 1;
    } while (bVar5 < 0x1f);
    iVar3 = 0x11;
    if (1 < bVar4) {
      FUN_00063ea4(0x11);
    }
LAB_000643aa:
    bVar4 = bVar4 + 1;
  } while( true );
}



void FUN_000643f6(void)

{
  uchar uVar1;
  byte bVar2;
  
  bVar2 = 0;
  do {
    bVar2 = bVar2 + 1;
    if (3 < bVar2) {
      FUN_00063ea4(0x11);
    }
    ECMCPCMD0 = 0xa5;
    ECMCESET = '\x01';
    ECMCESET = 0xfe;
    ECMCESET = '\x01';
    uVar1 = ECMPS;
  } while (uVar1 != '\0');
  bVar2 = 0;
  do {
    bVar2 = bVar2 + 1;
    if (3 < bVar2) {
      FUN_00063ea4(0x11);
    }
    ECMPCMD1 = 0xa5;
    ECMESSTC2 = 0x10000000;
    ECMESSTC2 = 0xefffffff;
    ECMESSTC2 = 0x10000000;
    uVar1 = ECMPS;
  } while (uVar1 != '\0');
  return;
}



void FUN_00064464(void)

{
  uchar uVar1;
  uint uVar2;
  int iVar3;
  byte bVar4;
  byte bVar5;
  
  bVar4 = 0;
  iVar3 = 0xff;
  do {
    bVar5 = 0;
    if (iVar3 == 0) {
      do {
        bVar5 = bVar5 + 1;
        if (3 < bVar5) {
          FUN_00063ea4(0x11);
        }
        ECMPCMD1 = 0xa5;
        ECMESSTC2 = 0x10000000;
        ECMESSTC2 = 0xefffffff;
        ECMESSTC2 = 0x10000000;
        uVar1 = ECMPS;
      } while (uVar1 != '\0');
      f33_spin_wait(DAT_00030d9c);
      return;
    }
    do {
      bVar5 = bVar5 + 1;
      if (3 < bVar5) {
        FUN_00063ea4(0x11);
      }
      ECMPCMD1 = 0xa5;
      ECMESSTC2 = 0x40000000;
      ECMESSTC2 = 0xbfffffff;
      ECMESSTC2 = 0x40000000;
      uVar1 = ECMPS;
    } while (uVar1 != '\0');
    bVar5 = 0;
    do {
      bVar5 = bVar5 + 1;
      if (3 < bVar5) {
        FUN_00063ea4(0x11);
      }
      ECMCPCMD0 = 0xa5;
      ECMCECLR = '\x01';
      ECMCECLR = 0xfe;
      ECMCECLR = '\x01';
      uVar1 = ECMPS;
    } while (uVar1 != '\0');
    uVar2 = 0x80000000;
    bVar5 = 0;
    do {
      if ((uVar2 & 0x80000000) == 0) {
        iVar3 = 0;
        goto LAB_00064502;
      }
      uVar2 = ECMCESSTR2;
      bVar5 = bVar5 + 1;
    } while (bVar5 < 0x1f);
    iVar3 = 0x11;
    if (1 < bVar4) {
      FUN_00063ea4(0x11);
    }
LAB_00064502:
    bVar4 = bVar4 + 1;
  } while( true );
}



int FUN_0006454e(char param_1)

{
  uint outer_iterations;
  int iVar1;
  int iVar2;
  byte bVar3;
  byte bVar4;
  undefined2 local_24;
  undefined2 uStack_22;
  undefined2 uStack_20;
  undefined2 uStack_1e;
  undefined2 uStack_1c;
  undefined2 uStack_1a;
  undefined2 uStack_18;
  undefined2 uStack_16;
  
  bVar3 = 0;
  bVar4 = 0;
  while( true ) {
    bVar4 = bVar4 + 1;
    if (param_1 == '\x11') {
      FUN_0006420e();
      f33_spin_wait(DAT_00030da0);
      iVar1 = FUN_0006427a(bVar4);
      FUN_00064310();
    }
    else {
      FUN_000643f6();
      f33_spin_wait(DAT_00030da0);
      iVar1 = FUN_0006427a(bVar4);
      FUN_00064464();
    }
    if (iVar1 == 0x11) break;
    if (3 < bVar4) {
      uStack_1c = 0x8200;
      iVar1 = 0xff;
      uStack_1a = 0;
      uStack_18 = 0x5018;
      uStack_16 = 0x1f00;
      FUN_00061836(&uStack_1c);
      outer_iterations = DAT_00030d98;
      f33_spin_wait(DAT_00030d98);
      do {
        local_24 = 0x8200;
        uStack_22 = 0;
        uStack_20 = 0x5018;
        uStack_1e = 0x1f00;
        FUN_00061836(&local_24);
        f33_spin_wait(outer_iterations);
        FUN_000614d4();
        iVar2 = FUN_000614b0();
        if (iVar2 == 4) {
          iVar1 = 0;
        }
        else if (1 < bVar3) {
          iVar1 = 0x11;
        }
        bVar3 = bVar3 + 1;
      } while (iVar1 == 0xff);
      return iVar1;
    }
  }
  return 0x11;
}



int FUN_00064620(void)

{
  int iVar1;
  undefined8 uVar2;
  int iVar3;
  byte bVar4;
  undefined2 local_14;
  undefined2 uStack_12;
  undefined2 uStack_10;
  undefined2 uStack_e;
  
  uVar2 = 0xfebeb800;
  bVar4 = 0;
  iVar3 = 0xff;
  do {
    local_14 = 0x8200;
    uStack_12 = 0;
    uStack_10 = 0x5018;
    uStack_e = 0x1f00;
    FUN_00061836(&local_14);
    f33_spin_wait(DAT_00030d98);
    FUN_000614d4();
    iVar1 = 0;
    if (((*((byte *)camry_host_ptr((uint32_t)((int)uVar2 + -0x7fc7)))) & 1) != 0) {
      iVar1 = 0x5a;
    }
    if (iVar1 == 0x5a) {
      iVar3 = 0;
    }
    else if (1 < bVar4) {
      iVar3 = 0x11;
    }
    bVar4 = bVar4 + 1;
  } while (iVar3 == 0xff);
  return iVar3;
}



void FUN_00064684(undefined1 param_1)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  iVar2 = FUN_0006454e(param_1);
  if (iVar2 == 0x11) {
    FUN_00063ea4(0x22);
  }
  iVar2 = 0;
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x7fc7))))) & 1) != 0) {
    iVar2 = 0x5a;
  }
  if ((iVar2 != 0x5a) && (iVar2 = FUN_00064620(), iVar2 == 0x11)) {
    FUN_00063ea4(0x33);
  }
  iVar2 = FUN_000640a0();
  if (iVar2 == 0x11) {
    FUN_00063ea4(0x44);
  }
  return;
}



int FUN_000646d6(char param_1)

{
  uint outer_iterations;
  undefined8 uVar1;
  int iVar2;
  byte bVar3;
  int iVar4;
  undefined2 local_2c;
  undefined2 uStack_2a;
  undefined2 uStack_28;
  undefined2 uStack_26;
  undefined2 uStack_24;
  undefined2 uStack_22;
  undefined2 uStack_20;
  undefined2 uStack_1e;
  undefined2 uStack_1c;
  undefined2 uStack_1a;
  undefined2 uStack_18;
  undefined2 uStack_16;
  
  uVar1 = 0xfebeb800;
  bVar3 = 0;
  iVar4 = 0xff;
  if (param_1 == '\x11') {
    FUN_0006420e();
  }
  else {
    FUN_000643f6();
  }
  f33_spin_wait(DAT_00030da4);
  uStack_1c = 0x8200;
  uStack_1a = 0;
  uStack_18 = 0x5018;
  uStack_16 = 0x1f00;
  FUN_00061836(&uStack_1c);
  outer_iterations = DAT_00030d98;
  f33_spin_wait(DAT_00030d98);
  do {
    uStack_24 = 0x8200;
    uStack_22 = 0;
    uStack_20 = 0x5018;
    uStack_1e = 0x1f00;
    FUN_00061836(&uStack_24);
    f33_spin_wait(outer_iterations);
    FUN_000614d4();
    iVar2 = 0;
    if (((*((byte *)camry_host_ptr((uint32_t)((int)uVar1 + -0x7fc8)))) & 0x80) != 0) {
      iVar2 = 0x5a;
    }
    if (iVar2 == 0) {
      iVar4 = 0;
    }
    else if (1 < bVar3) {
      iVar4 = 0x11;
    }
    bVar3 = bVar3 + 1;
  } while (iVar4 == 0xff);
  if (iVar4 != 0x11) {
    f33_spin_wait(DAT_00030da8);
    for (bVar3 = 0; bVar3 <= DAT_00030db0; bVar3 = bVar3 + 1) {
      if (iVar2 == 0x5a) {
        return 0;
      }
      local_2c = 0x8200;
      uStack_2a = 0;
      uStack_28 = 0x5018;
      uStack_26 = 0x1f00;
      FUN_00061836(&local_2c);
      f33_spin_wait(DAT_00030dac);
      FUN_000614d4();
      iVar2 = 0;
      if (((*((byte *)camry_host_ptr((uint32_t)((int)uVar1 + -0x7fc8)))) & 0x80) != 0) {
        iVar2 = 0x5a;
      }
    }
    iVar4 = 0x11;
  }
  return iVar4;
}



void FUN_000647ea(char param_1)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  iVar2 = FUN_000646d6((uint)(byte)param_1);
  if (iVar2 == 0x11) {
    FUN_00063ea4(0x22);
  }
  iVar2 = 0;
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x7fc7))))) & 1) != 0) {
    iVar2 = 0x5a;
  }
  if ((iVar2 != 0x5a) && (iVar2 = FUN_00064620(), iVar2 == 0x11)) {
    FUN_00063ea4(0x33);
  }
  if (param_1 == '\x11') {
    FUN_00064310();
  }
  else {
    FUN_00064464();
  }
  iVar2 = FUN_000640a0();
  if (iVar2 == 0x11) {
    FUN_00063ea4(0x44);
  }
  return;
}



/* Sequential initializer chain: 7 unconditional calls and no other statements; shape-verified. The
   called sequence is the function's entire behavior; chain family members differ in callee sets. */

void f33_run_init_chain_6484e(void)

{
  FUN_00063dba();
  FUN_00063dea();
  FUN_0006413c();
  FUN_00064684(0x11);
  FUN_00064684(0x22);
  FUN_000647ea(0x11);
  FUN_000647ea(0x22);
  return;
}



short FUN_00064882(void)

{
  int iVar1;
  short sStack_6;
  
  iVar1 = FUN_000707ac(((undefined *)camry_host_ptr(0xfebe39ccu)),((undefined *)camry_host_ptr(0xfebe8deeu)),((undefined *)camry_host_ptr(0xfebe8e02u)),&sStack_6);
  if ((iVar1 != 0) || (sStack_6 != -0x5aa6)) {
    sStack_6 = 0;
  }
  return sStack_6;
}



int FUN_000648ae(void)

{
  uint outer_iterations;
  int iVar1;
  undefined8 uVar2;
  byte bVar3;
  int iVar4;
  undefined2 local_20;
  undefined2 uStack_1e;
  undefined2 uStack_1c;
  undefined2 uStack_1a;
  undefined2 uStack_18;
  undefined2 uStack_16;
  undefined2 uStack_14;
  undefined2 uStack_12;
  
  uVar2 = 0xfebeb800;
  bVar3 = 0;
  iVar4 = 0xff;
  f33_spin_wait(DAT_00030db8);
  do {
    uStack_18 = 0x8200;
    uStack_16 = 0;
    uStack_14 = 0x5098;
    uStack_12 = 0x1f00;
    FUN_00061836(&uStack_18);
    outer_iterations = DAT_00030db4;
    f33_spin_wait(DAT_00030db4);
    FUN_000614d4();
    iVar1 = 0;
    if (((*((byte *)camry_host_ptr((uint32_t)((int)uVar2 + -0x7fc8)))) & 0x80) != 0) {
      iVar1 = 0x5a;
    }
    if (iVar1 == 0) {
      iVar4 = 0;
    }
    else if (1 < bVar3) {
      iVar4 = 0x11;
    }
    bVar3 = bVar3 + 1;
  } while (iVar4 == 0xff);
  if (iVar4 != 0x11) {
    bVar3 = 0;
    iVar4 = 0xff;
    f33_spin_wait(DAT_00030dbc);
    do {
      local_20 = 0x8200;
      uStack_1e = 0;
      uStack_1c = 0x5098;
      uStack_1a = 0x1f00;
      FUN_00061836(&local_20);
      f33_spin_wait(outer_iterations);
      FUN_000614d4();
      iVar1 = 0;
      if (((*((byte *)camry_host_ptr((uint32_t)((int)uVar2 + -0x7fc8)))) & 0x80) != 0) {
        iVar1 = 0x5a;
      }
      if (iVar1 == 0x5a) {
        iVar4 = 0;
      }
      else if (1 < bVar3) {
        iVar4 = 0x11;
      }
      bVar3 = bVar3 + 1;
    } while (iVar4 == 0xff);
  }
  return iVar4;
}



int FUN_00064986(void)

{
  uint outer_iterations;
  int iVar1;
  undefined8 uVar2;
  byte bVar3;
  undefined2 local_2c;
  undefined2 uStack_2a;
  undefined2 uStack_28;
  undefined2 uStack_26;
  undefined2 uStack_24;
  undefined2 uStack_22;
  undefined2 uStack_20;
  undefined2 uStack_1e;
  
  uVar2 = 0xfebeb800;
  bVar3 = 0;
  do {
    uStack_1e = 0x1f00;
    uStack_20 = 0x5098;
    uStack_22 = 0;
    uStack_24 = 0x8200;
    FUN_00061836(&uStack_24);
    outer_iterations = DAT_00030db4;
    f33_spin_wait(DAT_00030db4);
    uStack_26 = 0x1f00;
    uStack_28 = 0x5098;
    uStack_2a = 0;
    local_2c = 0x8200;
    FUN_00061836(&local_2c);
    f33_spin_wait(outer_iterations);
    FUN_000614d4();
    iVar1 = 0;
    if (((*((byte *)camry_host_ptr((uint32_t)((int)uVar2 + -0x7fc7)))) & 4) != 0) {
      iVar1 = 0x5a;
    }
    bVar3 = bVar3 + 1;
  } while ((iVar1 == 0x5a) && (bVar3 < 0x19));
  return FUN_000648ae();
}



void FUN_000649f6(char param_1)

{
  uint outer_iterations;
  uint32_t puVar1;
  undefined2 *puVar2;
  undefined2 local_20;
  undefined2 uStack_1e;
  undefined2 uStack_1c;
  undefined2 uStack_1a;
  undefined2 uStack_18;
  undefined2 uStack_16;
  undefined2 uStack_14;
  undefined2 uStack_12;
  
  puVar1 = 0xfebeb800u;
  if (param_1 == '\"') {
    f33_publish_redundant_u16
              (0xa55a,(ushort *)((undefined *)camry_host_ptr(0xfebe39d4u)),(ushort *)((undefined *)camry_host_ptr(0xfebe8df0u)),(ushort *)((undefined *)camry_host_ptr(0xfebe8e04u)));
    return;
  }
  if (param_1 == '\x11') {
    FUN_00062b90(0x6d6d6d6d);
    puVar2 = ((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x7e30)));
  }
  else {
    if (param_1 != '3') goto LAB_00064a3e;
    puVar2 = ((undefined *)camry_host_ptr(0xfebe39d2u));
  }
  *puVar2 = 0xa55a;
LAB_00064a3e:
  uStack_18 = 0x8200;
  uStack_16 = 0;
  uStack_14 = 0x5058;
  uStack_12 = 0x1f00;
  FUN_00061836(&uStack_18);
  outer_iterations = DAT_00030db4;
  f33_spin_wait(DAT_00030db4);
  local_20 = 0x8000;
  uStack_1e = 0;
  uStack_1c = 0x5018;
  uStack_1a = 0x1f00;
  FUN_00061836(&local_20);
  f33_spin_wait(outer_iterations);
                    /* WARNING: Subroutine does not return */
  f33_enter_terminal_hardware_sequence();
}



int FUN_00064a90(void)

{
  int iVar1;
  undefined8 uVar2;
  int iVar3;
  byte bVar4;
  undefined2 local_14;
  undefined2 uStack_12;
  undefined2 uStack_10;
  undefined2 uStack_e;
  
  uVar2 = 0xfebeb800;
  bVar4 = 0;
  iVar3 = 0xff;
  do {
    local_14 = 0x8200;
    uStack_12 = 0;
    uStack_10 = 0x5018;
    uStack_e = 0x1f00;
    FUN_00061836(&local_14);
    f33_spin_wait(DAT_00030db4);
    FUN_000614d4();
    iVar1 = 0;
    if (((*((byte *)camry_host_ptr((uint32_t)((int)uVar2 + -0x7fc7)))) & 2) != 0) {
      iVar1 = 0x5a;
    }
    if (iVar1 == 0x5a) {
      iVar3 = 0;
    }
    else if (1 < bVar4) {
      iVar3 = 0x11;
    }
    bVar4 = bVar4 + 1;
  } while (iVar3 == 0xff);
  return iVar3;
}



int FUN_00064af4(void)

{
  ushort uVar1;
  uint outer_iterations;
  int iVar2;
  int iVar3;
  undefined8 uVar4;
  int iVar5;
  byte bVar6;
  undefined2 local_30;
  undefined2 uStack_2e;
  undefined2 uStack_2c;
  undefined2 uStack_2a;
  undefined2 uStack_28;
  undefined2 uStack_26;
  undefined2 uStack_24;
  undefined2 uStack_22;
  
  uVar4 = 0xfebeb800;
  bVar6 = 0;
  iVar5 = 0xff;
  do {
    uStack_22 = 0x1f00;
    uStack_24 = 0x5058;
    uStack_26 = 0;
    uStack_28 = 0x8200;
    FUN_00061836(&uStack_28);
    outer_iterations = DAT_00030db4;
    f33_spin_wait(DAT_00030db4);
    uStack_2a = 0x1f00;
    uStack_2c = 0x5058;
    uStack_2e = 0;
    local_30 = 0x8200;
    FUN_00061836(&local_30);
    f33_spin_wait(outer_iterations);
    FUN_000614d4();
    uVar1 = (*((ushort *)camry_host_ptr((uint32_t)((int)uVar4 + -0x7fc8))));
    iVar2 = 0;
    if ((uVar1 >> 7 & 1) != 0) {
      iVar2 = 0x5a;
    }
    iVar3 = 0;
    if ((uVar1 >> 9 & 1) != 0) {
      iVar3 = 0x5a;
    }
    if ((iVar2 == 0) && (iVar3 == 0)) {
      iVar5 = 0;
    }
    else if (1 < bVar6) {
      iVar5 = 0x11;
    }
    bVar6 = bVar6 + 1;
  } while (iVar5 == 0xff);
  return iVar5;
}



void FUN_00064b86(void)

{
  uint outer_iterations;
  int iVar1;
  undefined8 uVar2;
  int iVar3;
  byte bVar4;
  undefined2 local_30;
  undefined2 uStack_2e;
  undefined2 uStack_2c;
  undefined2 uStack_2a;
  undefined2 uStack_28;
  undefined2 uStack_26;
  undefined2 uStack_24;
  undefined2 uStack_22;
  
  uVar2 = 0xfebeb800;
  bVar4 = 0;
  iVar3 = 0xff;
  do {
    uStack_22 = 0x1f00;
    uStack_24 = 0x5018;
    uStack_26 = 0;
    uStack_28 = 0x8000;
    FUN_00061836(&uStack_28);
    outer_iterations = DAT_00030db4;
    f33_spin_wait(DAT_00030db4);
    uStack_2a = 0x1f00;
    uStack_2c = 0x5018;
    uStack_2e = 0;
    local_30 = 0x8000;
    FUN_00061836(&local_30);
    f33_spin_wait(outer_iterations);
    FUN_000614d4();
    iVar1 = 0;
    if (((*((byte *)camry_host_ptr((uint32_t)((int)uVar2 + -0x7fc6)))) & 1) != 0) {
      iVar1 = 0x5a;
    }
    if (iVar1 == 0) {
      iVar3 = 0;
    }
    else if (1 < bVar4) {
                    /* WARNING: Subroutine does not return */
      f33_enter_terminal_hardware_sequence();
    }
    bVar4 = bVar4 + 1;
  } while (iVar3 == 0xff);
  return;
}



void FUN_00064c00(void)

{
  uint uVar1;
  int iVar2;
  uint32_t puVar3;
  ushort *raw;
  ushort *xor5555;
  ushort *xorAAAA;
  undefined2 local_18;
  undefined2 uStack_16;
  undefined2 uStack_14;
  undefined2 uStack_12;
  
  puVar3 = 0xfebeb800u;
  f33_publish_redundant_u16
            (0,(ushort *)((undefined *)camry_host_ptr(0xfebe39d4u)),(ushort *)((undefined *)camry_host_ptr(0xfebe8df0u)),(ushort *)((undefined *)camry_host_ptr(0xfebe8e04u)));
  raw = ((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x7e2a)));
  xor5555 = ((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x2a0e)));
  xorAAAA = ((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x29fa)));
  f33_publish_redundant_u16(0,raw,xor5555,xorAAAA);
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x7e30)))) = 0;
  iVar2 = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x7e2e)))) = 0;
  uVar1 = DAT_fff81000;
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x7fc7))))) & 2) != 0) {
    iVar2 = 0x5a;
  }
  if (iVar2 == 0x5a) {
    if (((((*((int *)camry_host_ptr((uint32_t)(puVar3 + -0x7e4c)))) == 0x7c7c7c7c) && ((*((int *)camry_host_ptr((uint32_t)(puVar3 + -0x2a1c)))) == 0x29292929))
        && ((*((int *)camry_host_ptr((uint32_t)(puVar3 + -0x2a08)))) == -0x2929292a)) && ((uVar1 & 1) == 0)) {
      f33_publish_redundant_u16(0xa55a,raw,xor5555,xorAAAA);
    }
    local_18 = 0x8200;
    uStack_16 = 0;
    uStack_14 = 0x5058;
    uStack_12 = 0x1f00;
    FUN_00061836(&local_18);
    f33_spin_wait(DAT_00030db4);
  }
  iVar2 = FUN_00064986();
  if (iVar2 == 0x11) {
    FUN_000649f6(0x11);
  }
  iVar2 = 0;
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x7fc7))))) & 2) != 0) {
    iVar2 = 0x5a;
  }
  if ((iVar2 != 0x5a) && (iVar2 = FUN_00064a90(), iVar2 == 0x11)) {
    FUN_000649f6(0x22);
  }
  iVar2 = FUN_00064af4();
  if (iVar2 == 0x11) {
    FUN_000649f6(0x33);
  }
  FUN_00064b86();
  return;
}



short FUN_00064d00(void)

{
  int iVar1;
  short sStack_6;
  
  iVar1 = FUN_000707ac(((undefined *)camry_host_ptr(0xfebe39d4u)),((undefined *)camry_host_ptr(0xfebe8df0u)),((undefined *)camry_host_ptr(0xfebe8e04u)),&sStack_6);
  if ((iVar1 != 0) || (sStack_6 != -0x5aa6)) {
    sStack_6 = 0;
  }
  return sStack_6;
}



short FUN_00064d2c(void)

{
  int iVar1;
  short sStack_6;
  
  iVar1 = FUN_000707ac(((undefined *)camry_host_ptr(0xfebe39d6u)),((undefined *)camry_host_ptr(0xfebe8df2u)),((undefined *)camry_host_ptr(0xfebe8e06u)),&sStack_6);
  if ((iVar1 != 0) || (sStack_6 != -0x5aa6)) {
    sStack_6 = 0;
  }
  return sStack_6;
}



/* Clear sample rings, start ticks, child accumulators and idle state. Active context and seven
   parent bytes become6 (idle); separate slot4 scalar samples are cleared too. Profiling data is not
   the independently active task-rate supervisor. */

void f33_initialize_execution_profiles(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    f33_execution_profiles.ch2_exclusive[iVar3] = 0;
    iVar1 = iVar3 + -9;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  f33_execution_profiles.slot4_exclusive = 0;
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    f33_execution_profiles.foreground_exclusive[iVar3] = 0;
    iVar1 = iVar3 + -0xf;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    f33_execution_profiles.ch2_inclusive[iVar3] = 0;
    iVar1 = iVar3 + -9;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  f33_execution_profiles.slot4_inclusive = 0;
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    f33_execution_profiles.foreground_inclusive[iVar3] = 0;
    iVar1 = iVar3 + -0xf;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  f33_execution_profiles.idle_previous = 0;
  f33_execution_profiles.idle_accumulated = 0;
  f33_execution_profiles.idle_last = 0;
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    f33_execution_profiles.start[iVar3] = 0;
    iVar1 = iVar3 + -5;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    f33_execution_profiles.child_ticks[iVar3] = 0;
    iVar1 = iVar3 + -5;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    f33_execution_profiles.ch0_inclusive[iVar3] = 0;
    iVar1 = iVar3 + -7;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    f33_execution_profiles.ch1_exclusive[iVar3] = 0;
    iVar1 = iVar3 + -7;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    f33_execution_profiles.ch1_inclusive[iVar3] = 0;
    iVar1 = iVar3 + -7;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  f33_execution_profiles.active = '\x06';
  f33_execution_profiles.ring_heads[0] = '\0';
  f33_execution_profiles.ring_heads[1] = '\0';
  f33_execution_profiles.ring_heads[2] = '\0';
  f33_execution_profiles.ring_heads[3] = '\0';
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    f33_execution_profiles.parent[iVar3] = '\x06';
    iVar1 = iVar3 + -6;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  return;
}



/* WARNING: This is an inlined function */
/* Return bitwise complement of u32[FFE51010]. Exact LD.W/NOT/JMP only alter R1/R10 and arithmetic
   flags; preserve incoming R6/R7/R8 for profile adapters. Inline this real leaf to repair
   decompiler live-argument loss. Hardware counter values, rate and entropy are not established. */

uint f33_read_inverted_profile_counter(void)

{
  uint uVar1;
  
  uVar1 = DAT_ffe51010;
  return ~uVar1;
}



/* WARNING: Inlined function: f33_read_inverted_profile_counter */
/* Read inverted counter, save prior active context in parent[slot], select slot and record adjusted
   start. If prior context6, add7 and accumulate idle delta; slot5 publishes/reset idle
   accumulation, choosing MIN with prior sample when31911==5A. Clear child ticks. Arithmetic
   wraps32; no local slot bound. */

void f33_begin_execution_profile(uchar slot,int entry_adjust)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  
  uVar3 = (uint)slot;
  uVar1 = DAT_ffe51010;
  uVar1 = ~uVar1 - entry_adjust;
  f33_execution_profiles.parent[uVar3] = f33_execution_profiles.active;
  if (f33_execution_profiles.active == '\x06') {
    uVar1 = uVar1 + 7;
    uVar2 = f33_execution_profiles.idle_accumulated + (uVar1 - f33_execution_profiles.idle_previous)
    ;
    f33_execution_profiles.idle_accumulated = uVar2;
    if (uVar3 == 5) {
      if ((f33_execution_profile_peak_hold == 'Z') && (f33_execution_profiles.idle_last < uVar2)) {
        uVar2 = f33_execution_profiles.idle_last;
      }
      f33_execution_profiles.idle_accumulated = 0;
      f33_execution_profiles.idle_last = uVar2;
    }
  }
  f33_execution_profiles.active = slot;
  f33_execution_profiles.start[uVar3] = uVar1;
  f33_execution_profiles.child_ticks[uVar3] = 0;
  return;
}



/* Begin slot0 with raw entry adjustment105. No local PMR wrapper. */

void f33_begin_execution_profile_slot0(void)

{
  f33_begin_execution_profile('\0',0x69);
  return;
}



/* Begin slot2 with raw entry adjustment118. Preserve PMR around FFC0 critical window. */

void f33_begin_execution_profile_slot2(void)

{
  uint saved_mask;
  
  saved_mask = f33_priority_mask_enter(0xffc0);
  f33_begin_execution_profile('\x02',0x76);
  f33_priority_mask_restore(saved_mask);
  return;
}



/* Begin slot3 with raw entry adjustment120. Preserve PMR around FFC0 critical window. */

void f33_begin_execution_profile_slot3(void)

{
  uint saved_mask;
  
  saved_mask = f33_priority_mask_enter(0xffc0);
  f33_begin_execution_profile('\x03',0x78);
  f33_priority_mask_restore(saved_mask);
  return;
}



/* Begin slot4 with raw entry adjustment59. Preserve PMR around FFC0 critical window. */

void f33_begin_execution_profile_slot4(void)

{
  uint saved_mask;
  
  saved_mask = f33_priority_mask_enter(0xffc0);
  f33_begin_execution_profile('\x04',0x3b);
  f33_priority_mask_restore(saved_mask);
  return;
}



/* Begin slot5 with raw entry adjustment31. Preserve PMR around FFC0 critical window. */

void f33_begin_execution_profile_slot5(void)

{
  uint saved_mask;
  
  saved_mask = f33_priority_mask_enter(0xffc0);
  f33_begin_execution_profile('\x05',0x1f);
  f33_priority_mask_restore(saved_mask);
  return;
}



/* WARNING: Inlined function: f33_read_inverted_profile_counter */
/* Restore active context from parent[slot]. Return (counter-exit_adjust)-start[slot] modulo32.
   Parent6 updates idle previous tick; other parents accumulate elapsed+parent_adjust in child
   ticks. Real R7/R8 inputs survive the counter leaf; no fake extra return registers. */

uint f33_end_execution_profile(uchar slot,int exit_adjust,uint parent_adjust)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  
  f33_execution_profiles.active = f33_execution_profiles.parent[slot];
  uVar3 = (uint)f33_execution_profiles.active;
  uVar2 = DAT_ffe51010;
  uVar1 = (~uVar2 - exit_adjust) - f33_execution_profiles.start[slot];
  uVar2 = ~uVar2 - exit_adjust;
  if (uVar3 != 6) {
    f33_execution_profiles.child_ticks[uVar3] =
         f33_execution_profiles.child_ticks[uVar3] + parent_adjust + uVar1;
    uVar2 = f33_execution_profiles.idle_previous;
  }
  f33_execution_profiles.idle_previous = uVar2;
  return uVar1;
}



/* End slot0, exit adjustment-19, parent adjustment81. Eight-entry u16 inclusive ring8D74. Exclusive
   subtracts accumulated child ticks modulo32; narrow u16 where specified.31911==5A retains maximum
   independently per output; otherwise overwrite. No timing-budget enforcement. */

void f33_end_execution_profile_slot0(void)

{
  uchar uVar1;
  uint uVar2;
  uint32_t puVar3;
  uint uVar4;
  uint uVar5;
  
  puVar3 = 0xfebeb800u;
  uVar4 = f33_end_execution_profile('\0',-0x13,0x51);
  uVar1 = f33_execution_profile_peak_hold;
  uVar4 = uVar4 & 0xffff;
  uVar2 = (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x2a5c))))) + 1 & 7;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x2a5c))))) = (byte)uVar2;
  if ((uVar1 == 'Z') &&
     (uVar5 = (uint)f33_execution_profiles.ch0_inclusive[uVar2],
     -1 < (int)(uVar5 - uVar4) && uVar5 != uVar4)) {
    uVar4 = uVar5;
  }
  f33_execution_profiles.ch0_inclusive[uVar2] = (ushort)uVar4;
  return;
}



/* End slot2, exit adjustment4, parent adjustment117. Eight-entry u16 exclusive/inclusive
   rings8D84/8D94. Exclusive subtracts accumulated child ticks modulo32; narrow u16 where
   specified.31911==5A retains maximum independently per output; otherwise overwrite. No
   timing-budget enforcement. */

void f33_end_execution_profile_slot2(void)

{
  int iVar1;
  ushort uVar2;
  uchar uVar3;
  uint32_t puVar4;
  undefined *puVar5;
  uint uVar6;
  uint uVar7;
  ushort uVar8;
  int iVar9;
  
  puVar4 = 0xfebeb800u;
  uVar6 = f33_priority_mask_enter(0xffc0);
  uVar7 = f33_end_execution_profile('\x02',4,0x75);
  iVar9 = (*((int *)camry_host_ptr((uint32_t)(puVar4 + -0x2a9c))));
  puVar5 = ((undefined *)camry_host_ptr((uint32_t)(puVar4)));
  f33_priority_mask_restore(uVar6);
  uVar3 = f33_execution_profile_peak_hold;
  uVar6 = (byte)puVar5[-0x2a5b] + 1 & 7;
  puVar5[-0x2a5b] = (byte)uVar6;
  iVar1 = uVar6 * 2;
  uVar6 = uVar7 & 0xffff;
  uVar8 = (ushort)(uVar7 - iVar9);
  if (uVar3 == 'Z') {
    uVar7 = uVar7 - iVar9 & 0xffff;
    uVar2 = (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + iVar1 + -0x2a7c))));
    if (-1 < (int)(uVar2 - uVar7) && uVar2 != uVar7) {
      uVar8 = uVar2;
    }
    (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + iVar1 + -0x2a7c)))) = uVar8;
    uVar7 = (uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar4 + iVar1 + -0x2a6c))));
    if (-1 < (int)(uVar7 - uVar6) && uVar7 != uVar6) {
      uVar6 = uVar7;
    }
  }
  else {
    (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + iVar1 + -0x2a7c)))) = uVar8;
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + iVar1 + -0x2a6c)))) = (short)uVar6;
  return;
}



/* End slot3, exit adjustment2, parent adjustment117. Ten-entry u32 exclusive/inclusive
   rings8C60/8CCC. Exclusive subtracts accumulated child ticks modulo32; narrow u16 where
   specified.31911==5A retains maximum independently per output; otherwise overwrite. No
   timing-budget enforcement. */

void f33_end_execution_profile_slot3(void)

{
  uint *puVar1;
  uint uVar2;
  uint32_t puVar3;
  undefined *puVar4;
  uint saved_mask;
  uint uVar5;
  int iVar6;
  
  puVar3 = 0xfebeb800u;
  saved_mask = f33_priority_mask_enter(0xffc0);
  uVar5 = f33_end_execution_profile('\x03',2,0x75);
  uVar2 = uVar5 - (*((int *)camry_host_ptr((uint32_t)(puVar3 + -0x2a98))));
  puVar4 = ((undefined *)camry_host_ptr((uint32_t)(puVar3)));
  f33_priority_mask_restore(saved_mask);
  if ((byte)puVar4[-0x2a5a] < 9) {
    iVar6 = (byte)puVar4[-0x2a5a] + 1;
  }
  else {
    iVar6 = 0;
  }
  puVar4[-0x2a5a] = (char)iVar6;
  puVar1 = ((uint *)camry_host_ptr((uint32_t)(puVar3 + iVar6 * 4 + -0x2ba0)));
  if (f33_execution_profile_peak_hold == 'Z') {
    if (uVar2 < *puVar1) {
      uVar2 = *puVar1;
    }
    *puVar1 = uVar2;
    if (uVar5 < puVar1[0x1b]) {
      uVar5 = puVar1[0x1b];
    }
  }
  else {
    *puVar1 = uVar2;
  }
  (*((uint *)camry_host_ptr((uint32_t)(puVar3 + iVar6 * 4 + -0x2b34)))) = uVar5;
  return;
}



/* End slot4, exit adjustment64, parent adjustment154. Single u32 exclusive/inclusive
   samples8C88/8CF4. Exclusive subtracts accumulated child ticks modulo32; narrow u16 where
   specified.31911==5A retains maximum independently per output; otherwise overwrite. No
   timing-budget enforcement. */

void f33_end_execution_profile_slot4(void)

{
  uint uVar1;
  uint32_t puVar2;
  uint saved_mask;
  uint uVar3;
  
  puVar2 = 0xfebeb800u;
  saved_mask = f33_priority_mask_enter(0xffc0);
  uVar3 = f33_end_execution_profile('\x04',0x40,0x9a);
  uVar1 = uVar3 - (*((int *)camry_host_ptr((uint32_t)(puVar2 + -0x2a94))));
  f33_priority_mask_restore(saved_mask);
  if (f33_execution_profile_peak_hold == 'Z') {
    if (uVar1 < (*((uint *)camry_host_ptr((uint32_t)(puVar2 + -0x2b78))))) {
      uVar1 = (*((uint *)camry_host_ptr((uint32_t)(puVar2 + -0x2b78))));
    }
    (*((uint *)camry_host_ptr((uint32_t)(puVar2 + -0x2b78)))) = uVar1;
    if (uVar3 < (*((uint *)camry_host_ptr((uint32_t)(puVar2 + -0x2b0c))))) {
      uVar3 = (*((uint *)camry_host_ptr((uint32_t)(puVar2 + -0x2b0c))));
    }
  }
  else {
    (*((uint *)camry_host_ptr((uint32_t)(puVar2 + -0x2b78)))) = uVar1;
  }
  (*((uint *)camry_host_ptr((uint32_t)(puVar2 + -0x2b0c)))) = uVar3;
  return;
}



/* End slot5, exit adjustment68, parent adjustment118. Sixteen-entry u32 exclusive/inclusive
   rings8C8C/8CF8. Exclusive subtracts accumulated child ticks modulo32; narrow u16 where
   specified.31911==5A retains maximum independently per output; otherwise overwrite. No
   timing-budget enforcement. */

void f33_end_execution_profile_slot5(void)

{
  int iVar1;
  uint uVar2;
  uint32_t puVar3;
  undefined *puVar4;
  uint uVar5;
  uint uVar6;
  
  puVar3 = 0xfebeb800u;
  uVar5 = f33_priority_mask_enter(0xffc0);
  uVar6 = f33_end_execution_profile('\x05',0x44,0x76);
  uVar2 = uVar6 - (*((int *)camry_host_ptr((uint32_t)(puVar3 + -0x2a90))));
  puVar4 = ((undefined *)camry_host_ptr((uint32_t)(puVar3)));
  f33_priority_mask_restore(uVar5);
  uVar5 = (byte)puVar4[-0x2a59] + 1 & 0xf;
  puVar4[-0x2a59] = (byte)uVar5;
  iVar1 = uVar5 * 4;
  if (f33_execution_profile_peak_hold == 'Z') {
    if (uVar2 < (*((uint *)camry_host_ptr((uint32_t)(puVar3 + iVar1 + -0x2b74))))) {
      uVar2 = (*((uint *)camry_host_ptr((uint32_t)(puVar3 + iVar1 + -0x2b74))));
    }
    (*((uint *)camry_host_ptr((uint32_t)(puVar3 + iVar1 + -0x2b74)))) = uVar2;
    if (uVar6 < (*((uint *)camry_host_ptr((uint32_t)(puVar3 + iVar1 + -0x2b08))))) {
      uVar6 = (*((uint *)camry_host_ptr((uint32_t)(puVar3 + iVar1 + -0x2b08))));
    }
  }
  else {
    (*((uint *)camry_host_ptr((uint32_t)(puVar3 + iVar1 + -0x2b74)))) = uVar2;
  }
  (*((uint *)camry_host_ptr((uint32_t)(puVar3 + iVar1 + -0x2b08)))) = uVar6;
  return;
}



/* WARNING: Inlined function: f33_read_inverted_profile_counter */
/* Return (inverted counter-exit_adjust)-start[low8(slot)] modulo32. ZXB before leaf call, then
   preserved R6/R7 determine index/adjustment. No slot validation or physical time conversion. */

uint f33_read_adjusted_profile_elapsed(uchar slot,int exit_adjust)

{
  uint uVar1;
  
  uVar1 = DAT_ffe51010;
  return (~uVar1 - exit_adjust) - f33_execution_profiles.start[slot];
}



/* Return adjusted live elapsed for slot0, adjustment-19. Keep actual R10 result; not void. */

uint f33_read_execution_profile_slot0(void)

{
  uint uVar1;
  
  uVar1 = f33_read_adjusted_profile_elapsed('\0',-0x13);
  return uVar1;
}



/* Return adjusted live elapsed for slot2, adjustment4. Subtract accumulated child ticks modulo32
   inside preserved FFC0 priority window. */

uint f33_read_execution_profile_slot2(void)

{
  uint32_t puVar1;
  uint saved_mask;
  uint uVar2;
  int iVar3;
  
  puVar1 = 0xfebeb800u;
  saved_mask = f33_priority_mask_enter(0xffc0);
  uVar2 = f33_read_adjusted_profile_elapsed('\x02',4);
  iVar3 = (*((int *)camry_host_ptr((uint32_t)(puVar1 + -0x2a9c))));
  f33_priority_mask_restore(saved_mask);
  return uVar2 - iVar3;
}



/* Return adjusted live elapsed for slot3, adjustment2. Subtract accumulated child ticks modulo32
   inside preserved FFC0 priority window. */

uint f33_read_execution_profile_slot3(void)

{
  uint32_t puVar1;
  uint saved_mask;
  uint uVar2;
  int iVar3;
  
  puVar1 = 0xfebeb800u;
  saved_mask = f33_priority_mask_enter(0xffc0);
  uVar2 = f33_read_adjusted_profile_elapsed('\x03',2);
  iVar3 = (*((int *)camry_host_ptr((uint32_t)(puVar1 + -0x2a98))));
  f33_priority_mask_restore(saved_mask);
  return uVar2 - iVar3;
}



/* Return adjusted live elapsed for slot4, adjustment64. Subtract accumulated child ticks modulo32
   inside preserved FFC0 priority window. */

uint f33_read_execution_profile_slot4(void)

{
  uint32_t puVar1;
  uint saved_mask;
  uint uVar2;
  int iVar3;
  
  puVar1 = 0xfebeb800u;
  saved_mask = f33_priority_mask_enter(0xffc0);
  uVar2 = f33_read_adjusted_profile_elapsed('\x04',0x40);
  iVar3 = (*((int *)camry_host_ptr((uint32_t)(puVar1 + -0x2a94))));
  f33_priority_mask_restore(saved_mask);
  return uVar2 - iVar3;
}



/* Return adjusted live elapsed for slot5, adjustment68. Subtract accumulated child ticks modulo32
   inside preserved FFC0 priority window. */

uint f33_read_execution_profile_slot5(void)

{
  uint32_t puVar1;
  uint saved_mask;
  uint uVar2;
  int iVar3;
  
  puVar1 = 0xfebeb800u;
  saved_mask = f33_priority_mask_enter(0xffc0);
  uVar2 = f33_read_adjusted_profile_elapsed('\x05',0x44);
  iVar3 = (*((int *)camry_host_ptr((uint32_t)(puVar1 + -0x2a90))));
  f33_priority_mask_restore(saved_mask);
  return uVar2 - iVar3;
}



/* Set phase/count/max to0 and min toFF; four-byte state, no timing or dispatch. */

void f33_reset_task_rate_window(F33TaskRateWindow *state)

{
  state->phase = '\0';
  state->count = '\0';
  state->maximum = '\0';
  state->minimum = 0xff;
  return;
}



/* Reset four task-rate records at8DB0 and four DMA records at8DC0. DMA phase/sum/max become0 and
   minFFFF; byte1 is untouched. */

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



/* Saturating u8 count increment under FFC0 priority mask; restore incoming PMR before comparing
   inclusive upper bound. Exceeding policy.max enters terminal61940 before task body. No local mode,
   DTC or engagement gate. */

void f33_record_supervised_task_dispatch(F33TaskRateWindow *state,F33TaskRatePolicy *policy)

{
  uint saved_mask;
  byte bVar1;
  
  saved_mask = f33_priority_mask_enter(0xffc0);
  bVar1 = state->count;
  if (bVar1 != 0xff) {
    bVar1 = bVar1 + 1;
  }
  state->count = bVar1;
  f33_priority_mask_restore(saved_mask);
  if (policy->maximum < bVar1) {
                    /* WARNING: Subroutine does not return */
    f33_enter_terminal_hardware_sequence();
  }
  return;
}



/* Apply real task-rate increment/upper-bound guard to state8DB0 using ROM30DC0. Runs before the
   corresponding task body. */

void f33_record_ch0_dispatch(void)

{
  f33_record_supervised_task_dispatch(f33_task_rate_windows,f33_task_rate_policies);
  return;
}



/* Apply real task-rate increment/upper-bound guard to state8DB4 using ROM30DC0. No direct caller
   recovered in the canonical graph; do not invent a scheduled task. */

void f33_record_auxiliary_dispatch(void)

{
  f33_record_supervised_task_dispatch(f33_task_rate_windows + 1,f33_task_rate_policies);
  return;
}



/* Apply real task-rate increment/upper-bound guard to state8DB8 using ROM30DC4. Runs before the
   corresponding task body. */

void f33_record_ch1_dispatch(void)

{
  f33_record_supervised_task_dispatch(f33_task_rate_windows + 2,f33_task_rate_policies + 1);
  return;
}



/* Four configured channels0/8/6/14 accumulate609B0 deltas with u32 addition then u16 saturation;
   wrapping u8 phase completes each six calls. Inclusive configured
   ranges138..258,138..258,15..60,18..72. Failure enters61940; success updates extrema and clears
   sum/phase. Hardware progress and physical timing remain unexecuted. */

void f33_check_dma_progress_windows(void)

{
  int iVar1;
  byte bVar2;
  undefined8 uVar3;
  uint uVar4;
  uint uVar5;
  undefined2 uVar6;
  uint uVar7;
  
  uVar3 = 0xfebeb800;
  uVar5 = 0;
  do {
    uVar4 = f33_read_dma_progress_delta(f33_dma_progress_policies[uVar5].channel);
    iVar1 = uVar5 * 8 + (int)uVar3;
    uVar4 = uVar4 + (*((ushort *)camry_host_ptr((uint32_t)(iVar1 + -0x2a3e))));
    uVar7 = uVar4 & 0xffff;
    if (0xfffe < uVar4) {
      uVar7 = 0xffff;
    }
    uVar6 = (undefined2)uVar7;
    bVar2 = (*((byte *)camry_host_ptr((uint32_t)(iVar1 + -0x2a40)))) + 1;
    if (f33_dma_progress_policies[uVar5].window <= bVar2) {
      if ((uVar7 < f33_dma_progress_policies[uVar5].minimum) ||
         (f33_dma_progress_policies[uVar5].maximum < uVar7)) {
                    /* WARNING: Subroutine does not return */
        f33_enter_terminal_hardware_sequence();
      }
      if ((*((ushort *)camry_host_ptr((uint32_t)(iVar1 + -0x2a3c)))) < uVar7) {
        (*((undefined2 *)camry_host_ptr((uint32_t)(iVar1 + -0x2a3c)))) = uVar6;
      }
      if (uVar7 < (*((ushort *)camry_host_ptr((uint32_t)(iVar1 + -0x2a3a))))) {
        (*((undefined2 *)camry_host_ptr((uint32_t)(iVar1 + -0x2a3a)))) = uVar6;
      }
      bVar2 = 0;
      uVar6 = 0;
    }
    (*((undefined2 *)camry_host_ptr((uint32_t)(iVar1 + -0x2a3e)))) = uVar6;
    (*((byte *)camry_host_ptr((uint32_t)(iVar1 + -0x2a40)))) = bVar2;
    uVar5 = uVar5 + 1;
    if (3 < uVar5) {
      return;
    }
  } while( true );
}



/* Saturating u8 phase increment. At configured window snapshot and clear count under FFC0, restore
   PMR, then enforce inclusive min/max. Failure enters61940 before extrema/phase publication.
   Success updates extrema and resets phase; incomplete windows retain count/extrema. */

void f33_check_task_rate_window(F33TaskRateWindow *state,F33TaskRatePolicy *policy)

{
  byte bVar1;
  byte bVar2;
  byte bVar3;
  uint saved_mask;
  uint uVar4;
  
  bVar3 = state->phase;
  if (bVar3 != 0xff) {
    bVar3 = bVar3 + 1;
  }
  if (policy->window <= bVar3) {
    saved_mask = f33_priority_mask_enter(0xffc0);
    bVar3 = state->count;
    uVar4 = (uint)bVar3;
    state->count = '\0';
    f33_priority_mask_restore(saved_mask);
    if ((uVar4 < policy->minimum) || (policy->maximum < uVar4)) {
                    /* WARNING: Subroutine does not return */
      f33_enter_terminal_hardware_sequence();
    }
    bVar1 = state->maximum;
    bVar2 = bVar3;
    if (-1 < (int)(bVar1 - uVar4) && bVar1 != uVar4) {
      bVar2 = bVar1;
    }
    state->maximum = bVar2;
    if ((int)(state->minimum - uVar4) < 0) {
      bVar3 = state->minimum;
    }
    state->minimum = bVar3;
    bVar3 = 0;
  }
  state->phase = bVar3;
  return;
}



/* CH2 calls DMA progress checks first, then CH0/CH1/foreground rate windows. ROM windows2/4/20
   accept5..20/5..20/1..8 dispatches. Native composition covers actual65414..6543E software interval
   after the DMA call, not DMA execution or elapsed-time guarantees. */

void f33_supervise_scheduled_progress(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  f33_check_dma_progress_windows();
  f33_check_task_rate_window(((F33TaskRateWindow *)camry_host_ptr((uint32_t)(puVar1 + -0x2a50))),f33_task_rate_policies);
  f33_check_task_rate_window(((F33TaskRateWindow *)camry_host_ptr((uint32_t)(puVar1 + -0x2a48))),f33_task_rate_policies + 1);
  f33_check_task_rate_window(((F33TaskRateWindow *)camry_host_ptr((uint32_t)(puVar1 + -0x2a44))),f33_task_rate_policies + 2);
  return;
}



/* Apply real task-rate increment/upper-bound guard to state8DBC using ROM30DC8. Runs before the
   corresponding task body. */

void f33_record_foreground_dispatch(void)

{
  f33_record_supervised_task_dispatch(f33_task_rate_windows + 3,f33_task_rate_policies + 2);
  return;
}



void FUN_00065458(void)

{
  Ramfffee680 = 0xfff000;
  Ramfffee688 = 4;
  Ramfffee684 = 0xfe000017;
  Ramfffee690 = 0xfff000;
  Ramfffee698 = 0x38;
  Ramfffee694 = 0xfe000013;
  Ramfffee6a0 = 0;
  Ramfffee6a8 = 0;
  Ramfffee6a4 = 0x16;
  Ramfffee6b0 = 0;
  Ramfffee6b8 = 0;
  Ramfffee6b4 = 0x16;
  Ramfffee6c0 = 0;
  Ramfffee6c8 = 0;
  Ramfffee6c4 = 0x16;
  Ramfffee6d0 = 0;
  Ramfffee6d8 = 0;
  Ramfffee6d4 = 0x16;
  Ramfffee6e0 = 0;
  Ramfffee6e8 = 0;
  Ramfffee6e4 = 0x16;
  Ramfffee6f0 = 0;
  Ramfffee6f8 = 0;
  Ramfffee6f4 = 0x16;
  return;
}



void FUN_000654aa(void)

{
  Ramffddd114 = 0xffffffff;
  Ramffddd110 = 0x8625fe1b;
  Ramffddd11c = 0x24;
  Ramffddd118 = 0x8625fe17;
  Ramffddd124 = 0xffffffff;
  Ramffddd120 = 0x8625fe1b;
  Ramffddd12c = 0x24;
  Ramffddd128 = 0x8625fe17;
  Ramffddd204 = 0xffffffff;
  Ramffddd200 = 0x8625fe1b;
  Ramffddd20c = 0x14;
  Ramffddd208 = 0x8625fe17;
  Ramffddd214 = 0xffffffff;
  Ramffddd210 = 0x8625fe1b;
  Ramffddd21c = 0x14;
  Ramffddd218 = 0x8625fe17;
  Ramffddd224 = 0xffffffff;
  Ramffddd220 = 0x8625fe1b;
  Ramffddd22c = 0x14;
  Ramffddd228 = 0x8625fe17;
  Ramffddd234 = 0xffffffff;
  Ramffddd230 = 0x8625fe1b;
  Ramffddd23c = 0x14;
  Ramffddd238 = 0x8625fe17;
  Ramffddd244 = 0xffffffff;
  Ramffddd240 = 0x8625fe1b;
  Ramffddd24c = 0x14;
  Ramffddd248 = 0x8625fe17;
  Ramffddd254 = 0xffffffff;
  Ramffddd250 = 0x8625fe1b;
  Ramffddd25c = 0x14;
  Ramffddd258 = 0x8625fe17;
  Ramffc4c004 = 0xffffffff;
  Ramffc4c000 = 0x862dfe1b;
  Ramffc4c00c = 4;
  Ramffc4c008 = 0x860dfe17;
  Ramffc4c014 = 0xffffffff;
  Ramffc4c010 = 0x862dfe1b;
  Ramffc4c01c = 4;
  Ramffc4c018 = 0x860dfe17;
  Ramffc4c024 = 0xffffffff;
  Ramffc4c020 = 0x862dfe1b;
  Ramffc4c02c = 4;
  Ramffc4c028 = 0x860dfe17;
  Ramffc4c044 = 0xffffffff;
  Ramffc4c040 = 0x866dfe1b;
  Ramffc4c04c = 4;
  Ramffc4c048 = 0x864dfe17;
  Ramffc4c054 = 0xffffffff;
  Ramffc4c050 = 0x862dfe1b;
  Ramffc4c05c = 4;
  Ramffc4c058 = 0x860dfe17;
  Ramffc4c074 = 0xffffffff;
  Ramffc4c070 = 0x862dfe1b;
  Ramffc4c07c = 4;
  Ramffc4c078 = 0x860dfe17;
  Ramffc5a004 = 0xffffffff;
  Ramffc5a000 = 0x8625fe1b;
  Ramffc5a00c = 4;
  Ramffc5a008 = 0x8605fe17;
  Ramffc5a024 = 0xffffffff;
  Ramffc5a020 = 0x8625fe1b;
  Ramffc5a02c = 4;
  Ramffc5a028 = 0x8605fe17;
  Ramffc5a034 = 0xffffffff;
  Ramffc5a030 = 0x8625fe1b;
  Ramffc5a03c = 4;
  Ramffc5a038 = 0x8605fe17;
  Ramffc5a044 = 4;
  Ramffc5a040 = 0x8605fe1b;
  Ramffc5a04c = 4;
  Ramffc5a048 = 0x8605fe17;
  Ramffc5a054 = 0xffffffff;
  Ramffc5a050 = 0x8625fe1b;
  Ramffc5a05c = 4;
  Ramffc5a058 = 0x8605fe17;
  Ramffddd004 = 0xffffffff;
  Ramffddd000 = 0x8625fe1b;
  Ramffddd00c = 4;
  Ramffddd008 = 0x8605fe17;
  Ramffddd014 = 0xffffffff;
  Ramffddd010 = 0x8625fe1b;
  Ramffddd01c = 4;
  Ramffddd018 = 0x8605fe17;
  Ramffddd024 = 0xffffffff;
  Ramffddd020 = 0x8625fe1b;
  Ramffddd02c = 4;
  Ramffddd028 = 0x8605fe17;
  Ramffddd034 = 0xffffffff;
  Ramffddd030 = 0x8625fe1b;
  Ramffddd03c = 4;
  Ramffddd038 = 0x8605fe17;
  Ramffddd044 = 0xffffffff;
  Ramffddd040 = 0x8625fe1b;
  Ramffddd04c = 4;
  Ramffddd048 = 0x8605fe17;
  Ramffddd054 = 0xffffffff;
  Ramffddd050 = 0x8625fe1b;
  Ramffddd05c = 4;
  Ramffddd058 = 0x8605fe17;
  Ramffddd064 = 0xffffffff;
  Ramffddd060 = 0x8625fe1b;
  Ramffddd06c = 4;
  Ramffddd068 = 0x8605fe17;
  Ramffddd074 = 0xffffffff;
  Ramffddd070 = 0x8625fe1b;
  Ramffddd07c = 4;
  Ramffddd078 = 0x8605fe17;
  Ramffddd084 = 0xffffffff;
  Ramffddd080 = 0x8625fe1b;
  Ramffddd08c = 4;
  Ramffddd088 = 0x8605fe17;
  Ramffddd094 = 0xffffffff;
  Ramffddd090 = 0x8625fe1b;
  Ramffddd09c = 4;
  Ramffddd098 = 0x8605fe17;
  Ramffddd0a4 = 0xffffffff;
  Ramffddd0a0 = 0x8625fe1b;
  Ramffddd0ac = 4;
  Ramffddd0a8 = 0x8605fe17;
  Ramffddd0b4 = 0xffffffff;
  Ramffddd0b0 = 0x8625fe1b;
  Ramffddd0bc = 4;
  Ramffddd0b8 = 0x8605fe17;
  Ramffddd0c4 = 0xffffffff;
  Ramffddd0c0 = 0x8625fe1b;
  Ramffddd0cc = 4;
  Ramffddd0c8 = 0x8605fe17;
  Ramffddd0d4 = 0xffffffff;
  Ramffddd0d0 = 0x8625fe1b;
  Ramffddd0dc = 4;
  Ramffddd0d8 = 0x8605fe17;
  Ramffddd0e4 = 0xffffffff;
  Ramffddd0e0 = 0x8625fe1b;
  Ramffddd0ec = 4;
  Ramffddd0e8 = 0x8605fe17;
  Ramffddd0f4 = 0xffffffff;
  Ramffddd0f0 = 0x8625fe1b;
  Ramffddd0fc = 4;
  Ramffddd0f8 = 0x8605fe17;
  Ramffddd104 = 0xffffffff;
  Ramffddd100 = 0x8625fe1b;
  Ramffddd10c = 4;
  Ramffddd108 = 0x8605fe17;
  Ramffddd134 = 0xffffffff;
  Ramffddd130 = 0x8625fe1b;
  Ramffddd13c = 4;
  Ramffddd138 = 0x8605fe17;
  Ramffddd144 = 0xffffffff;
  Ramffddd140 = 0x8625fe1b;
  Ramffddd14c = 4;
  Ramffddd148 = 0x8605fe17;
  Ramffddd154 = 0xffffffff;
  Ramffddd150 = 0x8625fe1b;
  Ramffddd15c = 4;
  Ramffddd158 = 0x8605fe17;
  Ramffddd164 = 0xffffffff;
  Ramffddd160 = 0x8625fe1b;
  Ramffddd16c = 4;
  Ramffddd168 = 0x8605fe17;
  Ramffddd174 = 0xffffffff;
  Ramffddd170 = 0x8625fe1b;
  Ramffddd17c = 4;
  Ramffddd178 = 0x8605fe17;
  Ramffddd184 = 0xffffffff;
  Ramffddd180 = 0x8625fe1b;
  Ramffddd18c = 4;
  Ramffddd188 = 0x8605fe17;
  Ramffddd194 = 0xffffffff;
  Ramffddd190 = 0x8625fe1b;
  Ramffddd19c = 4;
  Ramffddd198 = 0x8605fe17;
  Ramffddd1a4 = 0xffffffff;
  Ramffddd1a0 = 0x8625fe1b;
  Ramffddd1ac = 4;
  Ramffddd1a8 = 0x8605fe17;
  Ramffddd1b4 = 0xffffffff;
  Ramffddd1b0 = 0x8625fe1b;
  Ramffddd1bc = 4;
  Ramffddd1b8 = 0x8605fe17;
  Ramffddd1c4 = 0xffffffff;
  Ramffddd1c0 = 0x8625fe1b;
  Ramffddd1cc = 4;
  Ramffddd1c8 = 0x8605fe17;
  Ramffddd1d4 = 0xffffffff;
  Ramffddd1d0 = 0x8625fe1b;
  Ramffddd1dc = 4;
  Ramffddd1d8 = 0x8605fe17;
  Ramffddd1e4 = 0xffffffff;
  Ramffddd1e0 = 0x8625fe1b;
  Ramffddd1ec = 4;
  Ramffddd1e8 = 0x8605fe17;
  Ramffddd1f4 = 0xffffffff;
  Ramffddd1f0 = 0x8625fe1b;
  Ramffddd1fc = 4;
  Ramffddd1f8 = 0x8605fe17;
  Ramffddd264 = 0xffffffff;
  Ramffddd260 = 0x8625fe1b;
  Ramffddd26c = 4;
  Ramffddd268 = 0x8605fe17;
  Ramffddd274 = 0xffffffff;
  Ramffddd270 = 0x8625fe1b;
  Ramffddd27c = 4;
  Ramffddd278 = 0x8605fe17;
  Ramfff94004 = 0xffffffff;
  Ramfff94000 = 0x8625fe1b;
  Ramfff9400c = 4;
  Ramfff94008 = 0x8605fe17;
  Ramfff94014 = 0xffffffff;
  Ramfff94010 = 0x8625fe1b;
  Ramfff9401c = 4;
  Ramfff94018 = 0x8605fe17;
  Ramfff94024 = 0xffffffff;
  Ramfff94020 = 0x8625fe1b;
  Ramfff9402c = 4;
  Ramfff94028 = 0x8605fe17;
  Ramfff94034 = 0xffffffff;
  Ramfff94030 = 0x8625fe1b;
  Ramfff9403c = 4;
  Ramfff94038 = 0x8605fe17;
  Ramfff94044 = 0xffffffff;
  Ramfff94040 = 0x8625fe1b;
  Ramfff9404c = 4;
  Ramfff94048 = 0x8605fe17;
  Ramfff94054 = 0xffffffff;
  Ramfff94050 = 0x8625fe1b;
  Ramfff9405c = 4;
  Ramfff94058 = 0x8605fe17;
  Ramfff94064 = 0xffffffff;
  Ramfff94060 = 0x8625fe1b;
  Ramfff9406c = 4;
  Ramfff94068 = 0x8605fe17;
  Ramfff94074 = 0xffffffff;
  Ramfff94070 = 0x8625fe1b;
  Ramfff9407c = 4;
  Ramfff94078 = 0x8605fe17;
  Ramfff94084 = 0xffffffff;
  Ramfff94080 = 0x8625fe1b;
  Ramfff9408c = 4;
  Ramfff94088 = 0x8605fe17;
  Ramfff94094 = 0xffffffff;
  Ramfff94090 = 0x8625fe1b;
  Ramfff9409c = 4;
  Ramfff94098 = 0x8605fe17;
  Ramfff940a4 = 0xffffffff;
  Ramfff940a0 = 0x8625fe1b;
  Ramfff940ac = 4;
  Ramfff940a8 = 0x8605fe17;
  Ramfff940b4 = 0xffffffff;
  Ramfff940b0 = 0x8625fe1b;
  Ramfff940bc = 0x44;
  Ramfff940b8 = 0x8625fe17;
  Ramfff940c4 = 0xffffffff;
  Ramfff940c0 = 0x8625fe1b;
  Ramfff940cc = 0x44;
  Ramfff940c8 = 0x8625fe17;
  Ramfff940d4 = 0xffffffff;
  Ramfff940d0 = 0x8625fe1b;
  Ramfff940dc = 4;
  Ramfff940d8 = 0x8605fe17;
  Ramfff940e4 = 0xffffffff;
  Ramfff940e0 = 0x8625fe1b;
  Ramfff940ec = 4;
  Ramfff940e8 = 0x8605fe17;
  Ramfff94104 = 0xffffffff;
  Ramfff94100 = 0x8625fe1b;
  Ramfff9410c = 4;
  Ramfff94108 = 0x8605fe17;
  Ramfff94114 = 0xffffffff;
  Ramfff94110 = 0x8625fe1b;
  Ramfff9411c = 4;
  Ramfff94118 = 0x8605fe17;
  Ramfff94124 = 0xffffffff;
  Ramfff94120 = 0x8625fe1b;
  Ramfff9412c = 4;
  Ramfff94128 = 0x8605fe17;
  Ramfff94134 = 0xffffffff;
  Ramfff94130 = 0x8625fe1b;
  Ramfff9413c = 4;
  Ramfff94138 = 0x8605fe17;
  Ramfff94144 = 0xffffffff;
  Ramfff94140 = 0x8625fe1b;
  Ramfff9414c = 4;
  Ramfff94148 = 0x8605fe17;
  Ramfff94154 = 0xffffffff;
  Ramfff94150 = 0x8625fe1b;
  Ramfff9415c = 4;
  Ramfff94158 = 0x8605fe17;
  Ramffc40004 = 0xffffffff;
  Ramffc40000 = 0x8625fe1b;
  Ramffc4000c = 4;
  Ramffc40008 = 0x8605fe17;
  Ramffc40014 = 0xffffffff;
  Ramffc40010 = 0x8625fe1b;
  Ramffc4001c = 4;
  Ramffc40018 = 0x8605fe17;
  Ramffc40024 = 0xffffffff;
  Ramffc40020 = 0x8625fe1b;
  Ramffc4002c = 4;
  Ramffc40028 = 0x8605fe17;
  Ramffc40034 = 0xffffffff;
  Ramffc40030 = 0x8625fe1b;
  Ramffc4003c = 4;
  Ramffc40038 = 0x8605fe17;
  Ramffc40044 = 0xffffffff;
  Ramffc40040 = 0x8625fe1b;
  Ramffc4004c = 4;
  Ramffc40048 = 0x8605fe17;
  Ramffc40054 = 0xffffffff;
  Ramffc40050 = 0x8625fe1b;
  Ramffc4005c = 4;
  Ramffc40058 = 0x8605fe17;
  Ramffc40064 = 0xffffffff;
  Ramffc40060 = 0x8625fe1b;
  Ramffc4006c = 4;
  Ramffc40068 = 0x8605fe17;
  Ramffc40074 = 0xffffffff;
  Ramffc40070 = 0x8625fe1b;
  Ramffc4007c = 4;
  Ramffc40078 = 0x8605fe17;
  Ramffc40084 = 0xffffffff;
  Ramffc40080 = 0x8625fe1b;
  Ramffc4008c = 4;
  Ramffc40088 = 0x8605fe17;
  Ramffc40094 = 0xffffffff;
  Ramffc40090 = 0x8625fe1b;
  Ramffc4009c = 4;
  Ramffc40098 = 0x8605fe17;
  Ramffc400b4 = 0xffffffff;
  Ramffc400b0 = 0x8625fe1b;
  Ramffc400bc = 4;
  Ramffc400b8 = 0x8605fe17;
  Ramffc400c4 = 0xffffffff;
  Ramffc400c0 = 0x8625fe1b;
  Ramffc400cc = 4;
  Ramffc400c8 = 0x8605fe17;
  Ramffc400d4 = 0xffffffff;
  Ramffc400d0 = 0x8625fe1b;
  Ramffc400dc = 4;
  Ramffc400d8 = 0x8605fe17;
  Ramffc400e4 = 0xffffffff;
  Ramffc400e0 = 0x8625fe1b;
  Ramffc400ec = 4;
  Ramffc400e8 = 0x8605fe17;
  Ramffc400f4 = 0xffffffff;
  Ramffc400f0 = 0x8625fe1b;
  Ramffc400fc = 4;
  Ramffc400f8 = 0x8605fe17;
  Ramffc40104 = 0xffffffff;
  Ramffc40100 = 0x8625fe1b;
  Ramffc4010c = 4;
  Ramffc40108 = 0x8605fe17;
  Ramffc40114 = 0xffffffff;
  Ramffc40110 = 0x8625fe1b;
  Ramffc4011c = 4;
  Ramffc40118 = 0x8605fe17;
  Ramffc40124 = 0xffffffff;
  Ramffc40120 = 0x8625fe1b;
  Ramffc4012c = 4;
  Ramffc40128 = 0x8605fe17;
  return;
}



void FUN_000657fa(void)

{
  Ramffc49004 = 0xc;
  Ramffc49008 = 0;
  Ramffc4900c = 0x100000;
  Ramffc49000 = 0xc7fffe10;
  Ramffc49014 = 0;
  Ramffc49018 = 0;
  Ramffc4901c = 0;
  Ramffc49010 = 0x87fffe10;
  Ramffc49024 = 0;
  Ramffc49028 = 0;
  Ramffc4902c = 0;
  Ramffc49020 = 0x87fffe10;
  Ramffc49034 = 0;
  Ramffc49038 = 0;
  Ramffc4903c = 0;
  Ramffc49030 = 0x87fffe10;
  Ramffc49044 = 0;
  Ramffc49048 = 0;
  Ramffc4904c = 0;
  Ramffc49040 = 0x87fffe10;
  Ramffc49054 = 0;
  Ramffc49058 = 0;
  Ramffc4905c = 0;
  Ramffc49050 = 0x87fffe10;
  Ramffc49064 = 0;
  Ramffc49068 = 0;
  Ramffc4906c = 0;
  Ramffc49060 = 0x87fffe10;
  Ramffc49074 = 0;
  Ramffc49078 = 0;
  Ramffc4907c = 0;
  Ramffc49070 = 0x87fffe10;
  return;
}



void FUN_00065852(void)

{
  Ramfffa0004 = 0;
  Ramfffa0000 = 0x8601fe1b;
  Ramfffa000c = 0;
  Ramfffa0008 = 0x8601fe17;
  return;
}



undefined4 FUN_0006586a(void)

{
  __synchronize();
  __synchronize();
  f33_apply_mpu_attribute_profile(DAT_00031683);
  __synchronize();
  __synchronize();
  return 3;
}



undefined8 FUN_0006595e(void)

{
  uint32_t puVar1;
  undefined4 in_r10;
  undefined4 in_r11;
  
  puVar1 = 0xfebeb800u;
  ((void)(0x40), (void)(0xb8), FUN_000659f8());
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x7c00))))) = 0;
  ((void)(0x40), (void)(0xa8), FUN_000659f8());
  return CONCAT44(in_r11,in_r10);
}



/* Load MPAT0..15 from31708+64*low8(selector), then SYNCI/SYNCP. No index validation and no
   region-bound writes. Assembly system-register effects are authoritative; decompiler formerly
   exposed only the incidental last load in R10 as a false getter result. Apply MPAT0..15 attributes
   from31708+64*low8 selector, then synchronize. Not a scalar getter and not a region-bound update;
   no independent selector range check. */

void f33_apply_mpu_attribute_profile(uchar selector)

{
  __synchronize();
  __synchronize();
  return;
}



void FUN_000659f8(void)

{
  __synchronize();
  __synchronize();
  return;
}



/* Assembly MPAT0..15 save with persistent SP delta-64. Used in timer interrupt frames; not a normal
   stack-neutral leaf. */

void FUN_00065ac0(void)

{
  __synchronize();
  __synchronize();
  return;
}



/* Assembly MPAT0..15 restore with persistent SP delta+64, paired with65AC0. Restores the
   interrupted MPU profile, including foreground profile1. */

undefined4 FUN_00065b4a(void)

{
  undefined4 in_stack_00000000;
  
  __synchronize();
  __synchronize();
  return in_stack_00000000;
}



undefined4 FUN_00065bd4(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  uint uVar1;
  uint32_t puVar2;
  undefined4 in_r10;
  uint in_FEPSW;
  uint in_PSW;
  uint uVar3;
  uint in_FPEC;
  uint in_RBASE;
  uint in_EBASE;
  uint in_FPIPR;
  uint in_ISPR;
  uint in_INTCFG;
  
  uVar3 = in_PSW & 0xfffffff0;
  puVar2 = 0xfebeb800u;
  FUN_00065ac0();
  ((void)(0x40), (void)(0xb8), FUN_000659f8());
  if (((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x7c00)))))) != -1) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x7c00))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x7c00))))) + '\x01';
  }
  uVar3 = uVar3 & 0xfffffff0;
  FUN_00065b4a();
  if (((uVar3 >> 6 & 1) == 0) && ((in_INTCFG & 1) == 0)) {
    in_ISPR = in_ISPR & in_ISPR - 1;
  }
  if ((in_FPEC & 1) != 0) {
    in_FPIPR = in_FPIPR & 0x1f;
    if (0xf < in_FPIPR) {
      in_FPIPR = 0x10;
    }
    uVar3 = in_FPIPR;
    if (0xf < in_FPIPR) {
      uVar3 = 0xf;
    }
    uVar1 = PMR;
    if ((((uVar1 & 1 << uVar3) == 0) && ((in_ISPR & (1 << in_FPIPR + 1) - 1U & 0xffff) == 0)) &&
       ((in_FEPSW & 0xa0) == 0)) {
      if (((in_FEPSW & 0xbfffffbf) >> 0xf & 1) == 0) {
        in_EBASE = in_RBASE;
      }
      in_r10 = (*(int (*)())camry_host_ptr((uint32_t)((in_EBASE & 0xfffffe00) + 0x70)))(param_1,param_2,param_3,param_4);
    }
  }
  return in_r10;
}



void FUN_00065c64(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  ((void)(0x40), (void)(0xb8), FUN_000659f8());
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x7c02))))) = 0;
  ((void)(0x40), (void)(0xa8), FUN_000659f8());
  return;
}



void FUN_00065c88(void)

{
  undefined4 uVar1;
  uchar uVar2;
  byte bVar3;
  
  Ramffc65408 = 0xffffffff;
  Ramffc6540c = 0xf;
  uVar1 = Ramffc6540c;
  bVar3 = 0;
  __synchronize();
  do {
    ECMPCMD1 = 0xa5;
    ECMESSTC0 = 0x10000;
    ECMESSTC0 = 0xfffeffff;
    ECMESSTC0 = 0x10000;
    uVar2 = ECMPS;
    __synchronize();
    if (uVar2 == '\0') {
      return;
    }
    bVar3 = bVar3 + 1;
  } while (bVar3 < 3);
                    /* WARNING: Subroutine does not return */
  f33_enter_terminal_hardware_sequence();
}



void FUN_00065cda(void)

{
  uint32_t puVar1;
  byte bVar2;
  
  puVar1 = 0xfebeb800u;
  bVar2 = DAT_febf3402;
  if (DAT_febf3402 != 0xff) {
    bVar2 = DAT_febf3402 + 1;
  }
  if (DAT_00030dec <= bVar2) {
    FUN_00062b90((int)0xd6d6d6d6);
                    /* WARNING: Subroutine does not return */
    f33_enter_terminal_hardware_sequence();
  }
  FUN_00065c88();
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x7c02))))) = bVar2;
  return;
}



void FUN_00065d14(void)

{
  uint uVar1;
  
  for (uVar1 = 0; uVar1 < 0x20; uVar1 = uVar1 + 1) {
  }
  return;
}



void FUN_00065d38(void)

{
  if ((DAT_febe39d9 & 1) != 0) {
    FUN_00065d14();
  }
  return;
}



void FUN_00065d4a(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  ((void)(0x40), (void)(0xb8), FUN_000659f8());
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x7c03))))) = 0;
  ((void)(0x40), (void)(0xa8), FUN_000659f8());
  return;
}



void FUN_00065d6e(void)

{
  uint uVar1;
  uint uVar2;
  uchar uVar3;
  byte bVar4;
  
  bVar4 = 0;
  do {
    ECMPCMD1 = 0xa5;
    ECMESSTC0 = 0x80000;
    ECMESSTC0 = 0xfff7ffff;
    ECMESSTC0 = 0x80000;
    uVar3 = ECMPS;
    __synchronize();
    if (uVar3 == '\0') {
      uVar1 = UCFDERSTR;
      uVar2 = UCFDEDADR;
      if (((uVar1 & 1) != 0) || ((uVar1 >> 2 & 1) != 0)) {
        UCFDERSTCLR = 1;
        uVar1 = UCFDERSTCLR;
        __synchronize();
        FUN_00071c48();
      }
      return;
    }
    bVar4 = bVar4 + 1;
  } while (bVar4 < 3);
                    /* WARNING: Subroutine does not return */
  f33_enter_terminal_hardware_sequence();
}



void FUN_00065dd6(void)

{
  uint uVar1;
  uchar uVar2;
  
  uVar1 = UCFDEDADR;
  if (uVar1 + 0xfeff6000 < 0x2000) {
    ECMPCMD1 = 0xa5;
    ECMESSTC0 = 0x80000;
    ECMESSTC0 = 0xfff7ffff;
    ECMESSTC0 = 0x80000;
    uVar2 = ECMPS;
    __synchronize();
    UCFDERSTCLR = 1;
    uVar1 = UCFDERSTCLR;
    __synchronize();
  }
  else {
    if (DAT_febf3403 != 0xff) {
      DAT_febf3403 = DAT_febf3403 + 1;
    }
    if (DAT_00030ded <= DAT_febf3403) {
      FUN_00062b90((int)0xc7c7c7c7);
                    /* WARNING: Subroutine does not return */
      f33_enter_terminal_hardware_sequence();
    }
    FUN_00065d6e();
  }
  return;
}



void FUN_00065e58(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  ((void)(0x40), (void)(0xb8), FUN_000659f8());
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x7c04))))) = 0;
  ((void)(0x40), (void)(0xa8), FUN_000659f8());
  return;
}



void FUN_00065e7c(void)

{
  undefined4 uVar1;
  uchar uVar2;
  byte bVar3;
  
  bVar3 = 0;
  Ramffc62c08 = 1;
  Ramffc63408 = 1;
  Ramffc66008 = 1;
  Ramffc66408 = 1;
  Ramffc67008 = 1;
  Ramffc67408 = 1;
  Ramffc67808 = 1;
  Ramffc68408 = 1;
  Ramffc6a008 = 1;
  Ramffc6c008 = 1;
  uVar1 = Ramffc6c008;
  __synchronize();
  Ramffddd808 = 1;
  uVar1 = Ramffddd808;
  __synchronize();
  Ramfff94808 = 1;
  uVar1 = Ramfff94808;
  __synchronize();
  Ramffc40808 = 1;
  uVar1 = Ramffc40808;
  __synchronize();
  do {
    ECMPCMD1 = 0xa5;
    ECMESSTC0 = 0x10000000;
    ECMESSTC0 = 0xefffffff;
    ECMESSTC0 = 0x10000000;
    uVar2 = ECMPS;
    __synchronize();
    if (uVar2 == '\0') {
      return;
    }
    bVar3 = bVar3 + 1;
  } while (bVar3 < 3);
                    /* WARNING: Subroutine does not return */
  f33_enter_terminal_hardware_sequence();
}



void FUN_00065f24(void)

{
  uint32_t puVar1;
  byte bVar2;
  
  puVar1 = 0xfebeb800u;
  bVar2 = DAT_febf3404;
  if (DAT_febf3404 != 0xff) {
    bVar2 = DAT_febf3404 + 1;
  }
  if (DAT_00030dee <= bVar2) {
    FUN_00062b90((int)0xe3e3e3e3);
                    /* WARNING: Subroutine does not return */
    f33_enter_terminal_hardware_sequence();
  }
  FUN_00065e7c();
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x7c04))))) = bVar2;
  return;
}



void FUN_00065f8e(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  f33_initialize_task_progress_supervision();
  f33_initialize_execution_profiles();
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x7e28))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x7e27))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x7e26))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x7e25))))) = 0;
  return;
}



/* If ROM31910==5A bracket dispatch with slot0 profiling. Unconditionally run supervisor652E2 before
   body66786, then increment wrapping completion counter39D8. Exact31910=0 disables only profiling,
   not supervision. Native guard evidence stops before the task body. */

void f33_run_ch0_application_task(void)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  iVar2 = 0;
  if (f33_execution_profiling_enabled == 'Z') {
    puVar1 = 0xfebeb800u;
    f33_begin_execution_profile_slot0();
    iVar2 = 0x5a;
  }
  f33_record_ch0_dispatch();
  f33_fast_control_cycle();
  if (iVar2 == 0x5a) {
    f33_end_execution_profile_slot0();
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x7e28))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x7e28))))) + '\x01';
  return;
}



/* If ROM31910==5A bracket dispatch with slot2 profiling. Unconditionally run supervisor6530E before
   body6679E, then increment wrapping completion counter39D9. Exact31910=0 disables only profiling,
   not supervision. Native guard evidence stops before the task body. */

void f33_run_ch1_application_task(void)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  iVar2 = 0;
  if (f33_execution_profiling_enabled == 'Z') {
    puVar1 = 0xfebeb800u;
    f33_begin_execution_profile_slot2();
    iVar2 = 0x5a;
  }
  f33_record_ch1_dispatch();
  f33_run_init_chain_6679e();
  if (iVar2 == 0x5a) {
    f33_end_execution_profile_slot2();
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x7e27))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x7e27))))) + '\x01';
  return;
}



/* If ROM31910==5A bracket dispatch with slot3 profiling. Unconditionally run supervisor6540C before
   body667B6, then increment wrapping completion counter39DA. Exact31910=0 disables only profiling,
   not supervision. Native guard evidence stops before the task body. */

void f33_run_ch2_application_task(void)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  iVar2 = 0;
  if (f33_execution_profiling_enabled == 'Z') {
    puVar1 = 0xfebeb800u;
    f33_begin_execution_profile_slot3();
    iVar2 = 0x5a;
  }
  f33_supervise_scheduled_progress();
  f33_run_init_chain_667b6();
  if (iVar2 == 0x5a) {
    f33_end_execution_profile_slot3();
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x7e26))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x7e26))))) + '\x01';
  return;
}



/* Foreground polls and clears EIC136.bit12; a flag is not a counted backlog. Optional31910==5A
   hooks bracket bookkeeping, alternate-context physical NvM pump,667E6 subsystem cycle and
   alternate-context66CF6 application NvM cycle. Increment39DB after completion. Relative order is
   exact; execution time and missed-tick behavior are not a periodic-job guarantee. */

void FUN_00066062(void)

{
  byte bVar1;
  undefined8 uVar2;
  int iVar3;
  char *pcVar4;
  
  uVar2 = 0xfebeb800;
  do {
    do {
      bVar1 = (*((volatile uint8_t *)camry_host_ptr(0xffffb111u)));
    } while ((bVar1 & 0x10) == 0);
    bVar1 = (*((volatile uint8_t *)camry_host_ptr(0xffffb111u)));
    (*((volatile uint8_t *)camry_host_ptr(0xffffb111u))) = bVar1 & 0xef;
    iVar3 = 0;
    if (f33_execution_profiling_enabled == 'Z') {
      f33_begin_execution_profile_slot5();
      iVar3 = 0x5a;
    }
    f33_record_foreground_dispatch();
    FUN_00071378();
    thunk_FUN_00068318();
    FUN_00071398();
    f33_foreground_subsystem_cycle();
    FUN_00071378();
    f33_nvm_application_cycle();
    FUN_00071398();
    if (iVar3 == 0x5a) {
      f33_end_execution_profile_slot5();
    }
    pcVar4 = ((char *)camry_host_ptr((uint32_t)((int)uVar2 + -0x7e25)));
    *pcVar4 = *pcVar4 + '\x01';
  } while( true );
}



void FUN_000661fc(void)

{
  short sVar1;
  ushort uVar2;
  
  Ramffe20240 = 0x40;
  DAT_ffe20244 = 0;
  Ramffe20200 = 0;
  Ramffe20204 = 0x4000;
  Ramffe2020c = 0;
  Ramffe20214 = 0;
  Ramffe20220 = 0x4000;
  Ramffe20238 = 0x4000;
  DAT_ffe200c0 = 0;
  DAT_ffe200c4 = 0;
  DAT_ffe200cc = 0;
  DAT_ffe200d4 = 0;
  DAT_ffe200e0 = 0;
  DAT_ffe200f8 = 0;
  Ramffe20000 = DAT_00030e16 + DAT_00030e14 + -1;
  Ramffe20004 = DAT_00030e1a + DAT_00030e18 + -1;
  Ramffe2000c = DAT_00030e1e + DAT_00030e1c + -1;
  Ramffe20014 = (short)PTR_LAB_00030e22 + DAT_00030e20 + -1;
  sVar1 = DAT_00030e12 + DAT_00030e10 + -1;
  Ramffe20020 = sVar1;
  Ramffe20038 = sVar1;
  uVar2 = Ramffe2005c;
  Ramffe2005c = uVar2 & 0xbed4;
  uVar2 = Ramffe20058;
  Ramffe20058 = uVar2 & 0xbed4;
  uVar2 = Ramffe20260;
  Ramffe20260 = uVar2 & 0xbed4;
  uVar2 = Ramffe20268;
  Ramffe20268 = uVar2 & 0xbed4;
  uVar2 = Ramffe20264;
  Ramffe20264 = uVar2 & 0xbed4;
  uVar2 = Ramffe2026c;
  Ramffe2026c = uVar2 & 0xbed4;
  return;
}



void FUN_000662dc(void)

{
  ushort uVar1;
  
  Ramffe21240 = 0x40;
  DAT_ffe21244 = 0;
  Ramffe21200 = 0;
  Ramffe21204 = 0x4000;
  Ramffe2120c = 0;
  Ramffe21214 = 0;
  DAT_ffe210c0 = 0;
  DAT_ffe210c4 = 0;
  DAT_ffe210cc = 0;
  DAT_ffe210d4 = 0;
  Ramffe21000 = DAT_00030e16 + DAT_00030e14 + -1;
  Ramffe21004 = DAT_00030e1a + DAT_00030e18 + -1;
  Ramffe2100c = DAT_00030e1e + DAT_00030e1c + -1;
  Ramffe21014 = (short)PTR_LAB_00030e22 + DAT_00030e20 + -1;
  uVar1 = Ramffe2105c;
  Ramffe2105c = uVar1 & 0xffd4;
  uVar1 = Ramffe21058;
  Ramffe21058 = uVar1 & 0xffd4;
  uVar1 = Ramffe21260;
  Ramffe21260 = uVar1 & 0xffd4;
  uVar1 = Ramffe21268;
  Ramffe21268 = uVar1 & 0xffd4;
  uVar1 = Ramffe21264;
  Ramffe21264 = uVar1 & 0xffd4;
  uVar1 = Ramffe2126c;
  Ramffe2126c = uVar1 & 0xffd4;
  return;
}



void FUN_0006639c(void)

{
  byte bVar1;
  
  TAUJ0TPS = 0;
  (*((volatile uint8_t *)camry_host_ptr(0xffe50094u))) = 0;
  TAUJ0CMOR0 = 0;
  TAUJ0CMOR1 = 0;
  TAUJ0CMOR2 = 0;
  TAUJ0CMOR3 = 0;
  TAUJ0CMUR0 = '\0';
  TAUJ0CMUR1 = '\0';
  TAUJ0CMUR2 = '\0';
  TAUJ0CMUR3 = '\0';
  TAUJ0CDR0 = (uint)(PTR_FUN_00030df0 + DAT_00030df4 + -1);
  TAUJ0CDR1 = (DAT_00030dfc + DAT_00030df8) - 1;
  TAUJ0CDR2 = (DAT_00030e04 + DAT_00030e00) - 1;
  TAUJ0CDR3 = (DAT_00030e0c + DAT_00030e08) - 1;
  bVar1 = TAUJ0TOE;
  TAUJ0TOE = bVar1 & 0xf0;
  bVar1 = TAUJ0TO;
  TAUJ0TO = bVar1 & 0xf0;
  bVar1 = TAUJ0RDE;
  TAUJ0RDE = bVar1 & 0xf0;
  bVar1 = TAUJ0RDM;
  TAUJ0RDM = bVar1 & 0xf0;
  return;
}



void FUN_00066440(void)

{
  byte bVar1;
  
  DAT_ffe51090 = 0;
  DAT_ffe51094 = 0;
  DAT_ffe51080 = 0;
  DAT_ffe51020 = 0;
  DAT_ffe51000 = 0xffffffff;
  bVar1 = DAT_ffe51060;
  DAT_ffe51060 = bVar1 & 0xfe;
  bVar1 = DAT_ffe5105c;
  DAT_ffe5105c = bVar1 & 0xfe;
  bVar1 = DAT_ffe510a0;
  DAT_ffe510a0 = bVar1 & 0xfe;
  bVar1 = DAT_ffe510a4;
  DAT_ffe510a4 = bVar1 & 0xfe;
  return;
}



void FUN_00066474(void)

{
  ushort uVar1;
  uint uVar2;
  
  uVar1 = Ramffdd0010;
  Ramffdd0010 = uVar1 | 0x412b;
  uVar1 = Ramffdd0014;
  Ramffdd0014 = uVar1 | 0x2b;
  uVar1 = Ramffdd0018;
  Ramffdd0018 = uVar1 | 799;
  uVar1 = Ramffdd1040;
  Ramffdd1040 = uVar1 | 0x20;
  uVar1 = Ramffdd1044;
  Ramffdd1044 = uVar1 | 2;
  uVar1 = Ramffdd1060;
  Ramffdd1060 = uVar1 | 0x20;
  uVar1 = Ramffdd1064;
  Ramffdd1064 = uVar1 | 2;
  uVar2 = Ramffdd1000;
  Ramffdd1000 = uVar2 | 1;
  uVar2 = Ramffdd1004;
  Ramffdd1004 = uVar2 | 1;
  uVar2 = Ramffdd100c;
  Ramffdd100c = uVar2 | 0x30;
  uVar2 = Ramffdd1020;
  Ramffdd1020 = uVar2 | 2;
  uVar2 = Ramffdd1024;
  Ramffdd1024 = uVar2 | 2;
  uVar2 = Ramffdd102c;
  Ramffdd102c = uVar2 | 0xc0;
  return;
}



/* Sequential initializer chain: 5 unconditional calls and no other statements; shape-verified. The
   called sequence is the function's entire behavior; chain family members differ in callee sets. */

void f33_run_init_chain_664f6(void)

{
  FUN_000661fc();
  FUN_000662dc();
  FUN_0006639c();
  FUN_00066440();
  FUN_00066474();
  return;
}



void FUN_00066512(void)

{
  ushort uVar1;
  byte bVar2;
  uint saved_mask;
  
  saved_mask = f33_priority_mask_enter(0xffc0);
  Ramffe20000 = DAT_00030e14 + -1;
  Ramffe20004 = DAT_00030e18 + -1;
  Ramffe2000c = DAT_00030e1c + -1;
  Ramffe20014 = DAT_00030e20 + -1;
  Ramffe20020 = DAT_00030e10 + -1;
  Ramffe20038 = DAT_00030e10 + -1;
  uVar1 = Ramffe2005c;
  Ramffe2005c = uVar1 & 0xbed4;
  uVar1 = Ramffe20058;
  Ramffe20058 = uVar1 & 0xbed4;
  Ramffe21000 = DAT_00030e14 + -1;
  Ramffe21004 = DAT_00030e18 + -1;
  Ramffe2100c = DAT_00030e1c + -1;
  Ramffe21014 = DAT_00030e20 + -1;
  uVar1 = Ramffe2105c;
  Ramffe2105c = uVar1 & 0xffd0;
  uVar1 = Ramffe21058;
  Ramffe21058 = uVar1 & 0xffd0;
  TAUJ0CDR0 = (uint)(PTR_FUN_00030df0 + -1);
  TAUJ0CDR1 = DAT_00030df8 - 1;
  TAUJ0CDR2 = DAT_00030e00 - 1;
  TAUJ0CDR3 = DAT_00030e08 - 1;
  bVar2 = TAUJ0TOE;
  TAUJ0TOE = bVar2 & 0xf0;
  bVar2 = TAUJ0TO;
  TAUJ0TO = bVar2 & 0xf0;
  f33_priority_mask_restore(saved_mask);
  return;
}



/* PulsePIC1ASST=1 tostart previouslyselected timers withtheir
   configuredfirst-intervalCDRs;callrealspin_wait(1),writePWMcompares,thenreplacetimerreloadswithsteadyperiod-1.
   Calledonlyafter666BC initializationand6378C bootCRCgate,andbefore701EA(0),EI,66062.
   Triggercompletion/physicaltimingarenotmodeledhere. */

void f33_startup_start_timers_and_load_steady_periods(void)

{
  uint uVar1;
  
  DAT_ffdd0004 = 1;
  uVar1 = (uint)DAT_00031672 * 2 + (uint)f33_pwm_compare_offset * 2 & 0xffff;
  f33_spin_wait(1);
  DAT_ffe70144 = uVar1;
  DAT_ffe71144 = uVar1;
  uVar1 = TSG30CMPUE;
  TSG30CMPUE = uVar1;
  uVar1 = TSG31CMPUE;
  TSG31CMPUE = uVar1;
  Ramffe20000 = DAT_00030e14 + -1;
  Ramffe20004 = DAT_00030e18 + -1;
  Ramffe2000c = DAT_00030e1c + -1;
  Ramffe20014 = DAT_00030e20 + -1;
  Ramffe20020 = DAT_00030e10 + -1;
  Ramffe20038 = DAT_00030e10 + -1;
  Ramffe21000 = DAT_00030e14 + -1;
  Ramffe21004 = DAT_00030e18 + -1;
  Ramffe2100c = DAT_00030e1c + -1;
  Ramffe21014 = DAT_00030e20 + -1;
  TAUJ0CDR0 = (uint)(PTR_FUN_00030df0 + -1);
  TAUJ0CDR1 = DAT_00030df8 - 1;
  TAUJ0CDR2 = DAT_00030e00 - 1;
  TAUJ0CDR3 = DAT_00030e08 - 1;
  return;
}



/* Orderedapplicationinitializationdispatcher,calledby637EE
   withinterruptsdisabledbeforebootCRCgateandtimerstart. Lowlevelandsoftwareinitializersinclude66BC8
   NvMacquisitioninitialization/boundedbootstrap,diagnostics/communications,664F6timerconfiguration,65F8Ebookkeeping,62BF6retainedclassification,6681Eclear5F28,and58804appstateinitialization/publication.
   Noaggregatehardware-successreturnorrollbackexists;donotconflateinitializedstatewithacquireddataorphysicalreadiness.
    */

int f33_application_initialize_before_timer_start(void)

{
  FUN_000607d0();
  FUN_00060766();
  FUN_00060e5a();
  f33_run_init_chain_60178();
  FUN_00060c06();
  FUN_00061ee8();
  FUN_00061b56();
  FUN_000623c0();
  FUN_00061fce();
  FUN_000611ee();
  FUN_000613c8();
  FUN_00061526();
  FUN_0006165a();
  FUN_000616fc();
  FUN_000607f8();
  FUN_00066bc8();
  FUN_00089d3c();
  ((void)(0), FUN_0008ed14());
  f33_crypto_bank_initialize_mode();
  f33_crypto_bank_initialize_work();
  FUN_0006a440();
  FUN_0007a132();
  FUN_0008e74e();
  f33_return_only_stub_6a322();
  FUN_0008b120();
  FUN_0008b070();
  FUN_0008b134();
  f33_fill_constant_block_8bfea();
  FUN_0008c318();
  FUN_0008c70c();
  f33_fill_constant_block_8cb8c();
  f33_fill_constant_block_8cef0();
  FUN_0008b3d4();
  FUN_0008d4ae();
  f33_app_security_reset_challenge_material();
  FUN_0008d9ca();
  f33_reset_write_did_transaction();
  f33_diag_reset_routine_class_state();
  f33_fill_constant_block_8db22();
  f33_fill_constant_block_8de1a();
  FUN_0008e1e0();
  FUN_00098f4c();
  f33_crypto_bank_initialize_verification_report();
  f33_run_init_chain_664f6();
  FUN_00065f8e();
  f33_startup_classify_retained_token();
  FUN_0006681e();
  return f33_initialize_application_and_request_first_generation();
}



/* Commit PREVIOUS compare stage through61E72, then6289C, acquire/publish snapshots66824, and
   dispatch next application work588E8. New controller output is staged for a later cycle. No ADC
   freshness, timer-latch, electrical or mechanical proof. Fast cycle commits PREVIOUS compares
   before sample acquisition and dispatch of NEXT control/staging work. Exact software order;
   hardware latch timing, sample age and actuator response remain open. */

void f33_fast_control_cycle(void)

{
  FUN_00061e72();
  f33_service_serial_acquisition_pair();
  f33_publish_fast_acquisition_inputs();
  FUN_000588e8();
  return;
}



/* Sequential initializer chain: 4 unconditional calls and no other statements; shape-verified. The
   called sequence is the function's entire behavior; chain family members differ in callee sets. */

void f33_run_init_chain_6679e(void)

{
  FUN_00062df0();
  f33_consume_rsent_sensor_slots();
  FUN_0005899e();
  FUN_00065d38();
  return;
}



/* Sequential initializer chain: 10 unconditional calls and no other statements; shape-verified. The
   called sequence is the function's entire behavior; chain family members differ in callee sets. */

void f33_run_init_chain_667b6(void)

{
  FUN_000603c8();
  FUN_0005f9ce();
  FUN_000619c0();
  f33_publish_acquisition_diagnostic_snapshot();
  FUN_00058a50();
  FUN_0007a232();
  f33_update_local_status_packet();
  f33_update_local_status_bit_latch();
  FUN_00061664();
  FUN_0006174a();
  return;
}



/* Exact order69CA2,7A254,988C2,69E7C,58B5E,66512.7A254 contains RX drain then SecOC6A410;988C2 is
   DCM, not SecOC. Application work follows DCM and precedes the enclosing foreground NvM66CF6
   service. Foreground order is maintenance, communications/RX/SecOC, DCM, maintenance, application
   mode dispatch, timer reload. Enclosing application NvM service follows this aggregate. No
   scheduling jitter or guaranteed completion claim. */

void f33_foreground_subsystem_cycle(void)

{
  f33_crypto_bank_foreground_cycle();
  FUN_0007a254();
  f33_dcm_foreground_cycle();
  f33_crypto_bank_maintain_terminal_states();
  f33_dispatch_foreground_mode_generation();
  FUN_00066512();
  return;
}



/* Far-call trampoline: prepare {lp},0 / jarl 0x8583E / dispose 0,{lp},lp; byte-verified against the
   exact image. Forwards with registers and stack unchanged; marked as a thunk. Forwarding shape
   machine-verified; target semantics not recovered. */

void thunk_FUN_0008583e(void)

{
  FUN_0008583e();
  return;
}



/* Far-call trampoline: prepare {lp},0 / jarl 0x83F30 / dispose 0,{lp},lp; byte-verified against the
   exact image. Forwards with registers and stack unchanged; marked as a thunk. Forwarding shape
   machine-verified; target semantics not recovered. */

void thunk_FUN_00083f30(void)

{
  FUN_00083f30();
  return;
}



/* Single constant publisher: DAT_febe5f28 = 0; Shape-classified from the canonical corpus; the
   target cell is not yet named, so the written state's meaning is unknown. */

void FUN_0006681e(void)

{
  DAT_febe5f28 = 0;
  return;
}



/* Buffer twelve halfwords through6217E, then permute
   group0[0:3],group8[0:3],group0[3:6],group8[3:6] to5EC8..5EDE. Then629A2 copies cached serial
   triplets/counters and publish5F12/14/16,5F1C/1E/20,5F29..30. Does NOT write5F18/1A/22/24
   ancillary masks. Sequential stores, no validity gate or atomic cross-source generation. Native
   evidence covers explicit software continuations and a synthetic post-getter publication join, not
   descriptor acquisition or the intact fast task. */

void f33_publish_fast_acquisition_inputs(void)

{
  uint32_t puVar1;
  F33SerialAcquisitionRecord local_34;
  undefined2 uStack_28;
  undefined2 uStack_26;
  undefined2 uStack_24;
  undefined1 local_22;
  undefined1 uStack_21;
  undefined1 uStack_20;
  undefined1 uStack_1f;
  F33AcquisitionGroupPair FStack_1c;
  
  puVar1 = 0xfebeb800u;
  f33_copy_acquisition_group_pair(&FStack_1c);
  (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x5938)))) = FStack_1c.group0[0];
  (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x5936)))) = FStack_1c.group0[1];
  (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x5934)))) = FStack_1c.group0[2];
  (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x592c)))) = FStack_1c.group0[3];
  (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x592a)))) = FStack_1c.group0[4];
  (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x5928)))) = FStack_1c.group0[5];
  (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x5932)))) = FStack_1c.group8[0];
  (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x5930)))) = FStack_1c.group8[1];
  (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x592e)))) = FStack_1c.group8[2];
  (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x5926)))) = FStack_1c.group8[3];
  (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x5924)))) = FStack_1c.group8[4];
  (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x5922)))) = FStack_1c.group8[5];
  f33_copy_cached_serial_acquisition_records(&local_34);
  (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x58ee)))) = local_34.field14_0;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x58ec)))) = local_34.field14_1;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x58ea)))) = local_34.field12;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x58d7))))) = local_34.rx_count_failures;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x58d6))))) = local_34.rx_or_tx_failures;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x58d5))))) = local_34.crc_failures;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x58d4))))) = local_34.sequence_failures;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x58e4)))) = uStack_28;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x58e2)))) = uStack_26;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x58e0)))) = uStack_24;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x58d3))))) = local_22;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x58d2))))) = uStack_21;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x58d1))))) = uStack_20;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x58d0))))) = uStack_1f;
  return;
}



/* On odd5F28 consume two slot records through62B32 and publish5F02..5F10; increment5F28 on every
   call. Software one-of-two cadence, not proof that hardware supplied a new frame. Odd5F28 runs
   acquisition aggregation and publishes5F02..5F10; every call increments5F28. Later
   parity-derived8A1C is software cadence rather than fresh-frame evidence. */

void f33_consume_rsent_sensor_slots(void)

{
  uint32_t puVar1;
  undefined2 local_14;
  undefined2 uStack_12;
  undefined2 uStack_10;
  undefined2 uStack_e;
  undefined2 uStack_c;
  undefined2 uStack_a;
  undefined2 uStack_8;
  undefined2 uStack_6;
  
  puVar1 = 0xfebeb800u;
  if ((DAT_febe5f28 & 1) != 0) {
    puVar1 = 0xfebeb800u;
    FUN_00062b32(camry_host_addr(&local_14));
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x58fe)))) = local_14;
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x58fc)))) = uStack_12;
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x58fa)))) = uStack_10;
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x58f8)))) = uStack_e;
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x58f6)))) = uStack_c;
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x58f4)))) = uStack_a;
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x58f2)))) = uStack_8;
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x58f0)))) = uStack_6;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x58d8))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x58d8))))) + '\x01';
  return;
}



/* Compose62ABC,62B18,6294E into5EE0..5F24 and cached380A/B into5F26/27. 6294E rotates serial mask
   windows and publishes5F18/1A/22/24;66824 does not write these masks. The range and mask fields
   are staged generations, not an atomic physical measurement. Compose transfer-group
   copies62ABC,62B18,6294E into5EE0..5F24, and copy cached380A/B to5F26/27. The range
   fields5EEA/C/E/5EF0 and later81D6/8/A/C are staged generations, not an atomic physical
   measurement. 6294E separately rotates four-slot masks and publishes5F18/1A/22/24; numeric/counter
   producer66824 does not own those fields. */

void f33_publish_acquisition_diagnostic_snapshot(void)

{
  uint32_t puVar1;
  F33SerialAcquisitionMasks local_2c;
  undefined2 uStack_28;
  undefined2 uStack_26;
  undefined2 uStack_24;
  undefined2 uStack_22;
  ushort uStack_16;
  undefined2 uStack_14;
  undefined2 uStack_12;
  undefined2 uStack_10;
  undefined2 uStack_e;
  undefined2 uStack_c;
  undefined2 uStack_a;
  undefined2 local_8;
  undefined2 uStack_6;
  
  puVar1 = 0xfebeb800u;
  f33_copy_acquisition_diagnostic_samples(&uStack_16);
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x5920)))) = uStack_e;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x591e)))) = uStack_14;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x591c)))) = uStack_a;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x591a)))) = uStack_16;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x5918)))) = uStack_c;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x5916)))) = uStack_12;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x5914)))) = uStack_10;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x5912)))) = local_8;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x5910)))) = uStack_6;
  FUN_00062b18(camry_host_addr(&uStack_24));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x5902)))) = uStack_24;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x5900)))) = uStack_22;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x58da))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x7ff6)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x58d9))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x7ff5)))));
  f33_rotate_and_copy_serial_acquisition_masks(&local_2c);
  (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x58e8)))) = local_2c.first;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x58e6)))) = local_2c.second;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x58de)))) = uStack_28;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x58dc)))) = uStack_26;
  return;
}



/* Forward mask to61C40 with fixed bank0; software port-mask staging, not immediate hardware commit.
    */

void f33_stage_output_bank0_phase_mask(uchar mask)

{
  f33_stage_configured_phase_mask(0,(uint)mask);
  return;
}



void FUN_000669da(ushort param_1,ushort param_2,ushort param_3)

{
  f33_pwm_stage_halfword_compares(0,param_1,param_2,param_3);
  return;
}



void FUN_000669f6(ushort param_1,ushort param_2,ushort param_3)

{
  f33_pwm_stage_word_compares(0,param_1,param_2,param_3);
  return;
}



/* Fixed bank0 veneer for configured port level-a. Physical output response is outside the recovered
   software contract. */

void f33_write_output_bank0_port_level_a(void)

{
  f33_write_configured_output_port_level_a(0);
  return;
}



/* Fixed bank0 veneer for configured port level-b. Physical output response is outside the recovered
   software contract. */

void f33_write_output_bank0_port_level_b(void)

{
  f33_write_configured_output_port_level_b(0);
  return;
}



/* Forward mask to61C40 with fixed bank1; software port-mask staging, not immediate hardware commit.
    */

void f33_stage_output_bank1_phase_mask(uchar mask)

{
  f33_stage_configured_phase_mask(1,(uint)mask);
  return;
}



void FUN_00066a40(ushort param_1,ushort param_2,ushort param_3)

{
  f33_pwm_stage_halfword_compares(1,param_1,param_2,param_3);
  return;
}



void FUN_00066a5c(ushort param_1,ushort param_2,ushort param_3)

{
  f33_pwm_stage_word_compares(1,param_1,param_2,param_3);
  return;
}



/* Fixed bank1 veneer for configured port level-a. Physical output response is outside the recovered
   software contract. */

void f33_write_output_bank1_port_level_a(void)

{
  f33_write_configured_output_port_level_a(1);
  return;
}



/* Fixed bank1 veneer for configured port level-b. Physical output response is outside the recovered
   software contract. */

void f33_write_output_bank1_port_level_b(void)

{
  f33_write_configured_output_port_level_b(1);
  return;
}



void FUN_00066a94(void)

{
  f33_write_channel_reference_level(0);
  return;
}



void FUN_00066aa2(void)

{
  f33_write_channel_requested_level(0);
  return;
}



/* Return full-width0/1 for input channel0 equal to ROM31302 reference level1. Return full0/1 for
   channel0 input equal to exact reference level1. GPIO observation only. */

uint f33_channel0_matches_reference(void)

{
  uint uVar1;
  
  uVar1 = f33_read_channel_input_level(0);
  return (uint)(uVar1 == f33_channel_ports[0].reference_level);
}



void FUN_00066acc(void)

{
  f33_write_channel_reference_level(1);
  return;
}



void FUN_00066ada(void)

{
  f33_write_channel_requested_level(1);
  return;
}



/* Return full-width0/1 for input channel1 equal to ROM3130A reference level1. Return full0/1 for
   channel1 input equal to exact reference level1. No inference of physical permission or actuator
   response. */

uint f33_channel1_matches_reference(void)

{
  uint uVar1;
  
  uVar1 = f33_read_channel_input_level(1);
  return (uint)(uVar1 == f33_channel_ports[1].reference_level);
}



void FUN_00066b04(undefined1 param_1,undefined1 param_2,undefined2 param_3)

{
  FUN_00062a16(param_1,param_2,param_3);
  return;
}



void FUN_00066bc8(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  f33_publish_redundant_u8('Z', ((uchar *)camry_host_ptr((uint32_t)((0xfebf0670u)))), ((uchar *)camry_host_ptr((uint32_t)((0xfebf10a8u)))), ((uchar *)camry_host_ptr((uint32_t)((0xfebf10ccu)))))
  ;
  f33_publish_redundant_u8('\0', ((undefined *)camry_host_ptr((uint32_t)(puVar1 + 0x4e71))), ((undefined *)camry_host_ptr((uint32_t)(puVar1 + 0x58a9))), ((undefined *)camry_host_ptr((uint32_t)(puVar1 + 0x58cd))));
  f33_publish_redundant_u8('\0', ((undefined *)camry_host_ptr((uint32_t)(puVar1 + 0x4e72))), ((undefined *)camry_host_ptr((uint32_t)(puVar1 + 0x58aa))), ((undefined *)camry_host_ptr((uint32_t)(puVar1 + 0x58ce))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x4e73))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x4e74))))) = 0;
  FUN_000672c0();
  f33_nvm_initialize_family1_application();
  f33_nvm_initialize_family2_ram();
  f33_nvm_initialize_acquisition();
  f33_nvm_run_bounded_initial_acquisition();
  return;
}



/* Snapshot family phases before repairing0670/10A8/10CC with fallback0. Decoded5A returns0. Idle
   acquisition with an active phase selects2 for family1 before1 for family0. Otherwise step66B16;
   busy preserves current work. On idle completion,67B58==1 selects2, else 6740A==1 selects1, else
   preserve work. Native hold repair/fallback and phase priority; request selectors have separate
   native edge proofs. Decoded5A suppresses selection/progression. Idle acquisition with active
   phase chooses family1 work2 ahead of family0 work1. Otherwise step acquisition; busy preserves
   low8 current work, idle tries67B58 then6740A. Native repair/fallback and phase-priority branches;
   request selectors have separate native edge proofs; complete initialized physical acquisition
   remains separate. */

uint f33_nvm_select_acquisition_work(uchar current_work)

{
  uint32_t puVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  
  puVar1 = 0xfebeb800u;
  uVar2 = f33_nvm_get_family0_phase();
  uVar3 = f33_nvm_get_family1_phase();
  uVar4 = f33_read_repair_redundant_u8(camry_host_addr(((undefined *)camry_host_ptr((uint32_t)(puVar1 + 0x4e70)))), camry_host_addr(((undefined *)camry_host_ptr((uint32_t)(puVar1 + 0x58a8)))), camry_host_addr(((undefined *)camry_host_ptr((uint32_t)(puVar1 + 0x58cc)))),  '\0');
  if (uVar4 == 0x5a) {
    return 0;
  }
  if (((uVar2 == 0) && (uVar3 == 0)) || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x4e73))))) != '\0')) {
    uVar2 = f33_nvm_step_acquisition_pass();
    if (uVar2 != 0) {
      return (uint)current_work;
    }
    uVar2 = f33_nvm_select_family1_request();
    if (uVar2 == 1) {
      return 2;
    }
    uVar2 = f33_nvm_select_family0_request();
    if (uVar2 != 1) {
      return (uint)current_work;
    }
  }
  else if (uVar3 != 0) {
    return 2;
  }
  return 1;
}



char FUN_00066cc4(char param_1)

{
  int iVar1;
  
  if (param_1 == '\x01') {
    iVar1 = FUN_00068924();
    if (iVar1 != 0) {
      return '\x01';
    }
    FUN_000674dc();
  }
  else {
    if (param_1 != '\x02') {
      return param_1;
    }
    iVar1 = FUN_00068a4a();
    if (iVar1 != 0) {
      return '\x02';
    }
    f33_nvm_handle_family1_completion();
  }
  return '\0';
}



/* Select work from current0674 through66C5C; service logical/range work via682D6; finish the
   selected application phase through66CC4 and publish its low8 result to0674; then maintain the
   FLMD0 internal pull-down. Composed initialized-idle execution advances the logical scan, selects
   callback766F4 and leaves application ownership idle. Active flash sequencing remains a separate
   dependency. Application NvM cycle orders work selection, logical/range servicing, phase
   completion, work-byte publication and FLMD maintenance. Composed initialized-idle execution
   advances the logical scan, selects callback766F4 and leaves application ownership idle without
   peripheral commands. Active flash sequencing remains an explicit dependency. */

void f33_nvm_application_cycle(void)

{
  uint32_t puVar1;
  undefined1 uVar2;
  uint uVar3;
  
  puVar1 = 0xfebeb800u;
  uVar3 = f33_nvm_select_acquisition_work(DAT_febf0674);
  f33_nvm_service_and_release_erase_span();
  uVar2 = FUN_00066cc4(uVar3);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x4e74))))) = uVar2;
  f33_select_flmd0_internal_pulldown();
  return;
}



/* Repair gate0671/10A9/10CD with fallback0; exact5A rejects. Decode family bits8..15 and low8
   object, ignoring high16. Families0/1 enqueue read-kind11; family2 synchronously refreshes ROM
   status. Return acceptance, not persistence or CRC success. Static exact-instruction/dataflow
   review; */

uint f33_nvm_request_record_refresh(uint selector)

{
  uint uVar1;
  uint uVar2;
  uint object;
  uint uVar3;
  
  uVar2 = 0;
  uVar3 = selector & 0xff00;
  object = selector & 0xff;
  uVar1 = f33_read_repair_redundant_u8(camry_host_addr(((undefined *)camry_host_ptr(0xfebf0671u))), camry_host_addr(((undefined *)camry_host_ptr(0xfebf10a9u))), camry_host_addr(((undefined *)camry_host_ptr(0xfebf10cdu))), '\0');
  if (uVar1 != 0x5a) {
    if (uVar3 == 0) {
      uVar2 = f33_nvm_enqueue_family0_read(object);
    }
    else if (uVar3 == 0x100) {
      uVar2 = f33_nvm_enqueue_family1_read(object);
    }
    else if (uVar3 == 0x200) {
      uVar2 = f33_nvm_refresh_family2_record_status(object);
    }
  }
  return uVar2;
}



/* Repair gate0672/10AA/10CE with fallback0; exact5A rejects before source access. Dispatch
   family0/1 RAM update and request admission, or family2 RAM-only update. Unsupported families
   return0; high16 selector bits ignored. */

uint f33_nvm_set_record(uint selector,uint *source)

{
  uint uVar1;
  uint uVar2;
  uint object;
  uint uVar3;
  
  uVar2 = 0;
  uVar3 = selector & 0xff00;
  object = selector & 0xff;
  uVar1 = f33_read_repair_redundant_u8(camry_host_addr(((undefined *)camry_host_ptr(0xfebf0672u))), camry_host_addr(((undefined *)camry_host_ptr(0xfebf10aau))), camry_host_addr(((undefined *)camry_host_ptr(0xfebf10ceu))), '\0');
  if (uVar1 != 0x5a) {
    if (uVar3 == 0) {
      uVar2 = f33_nvm_set_family0_record(object, camry_host_addr(source));
    }
    else if (uVar3 == 0x100) {
      uVar2 = f33_nvm_set_family1_record(object,source);
    }
    else if (uVar3 == 0x200) {
      uVar2 = f33_nvm_set_family2_record(object,source);
    }
  }
  return uVar2;
}



/* Dispatch low8 object by selector bits8..15. Family0 reads raw status; family1 votes with
   fallback12; family2 votes with fallback10. Unknown families returnFF; no physical flash read.
   Static exact-instruction/dataflow review; */

uint f33_nvm_get_record_status(uint selector)

{
  uint uVar1;
  uint object;
  
  uVar1 = selector & 0xff00;
  object = selector & 0xff;
  if (uVar1 == 0) {
    uVar1 = f33_nvm_get_family0_status(object);
  }
  else if (uVar1 == 0x100) {
    uVar1 = f33_nvm_get_family1_status(object);
  }
  else if (uVar1 == 0x200) {
    uVar1 = f33_nvm_get_family2_status(object);
  }
  else {
    uVar1 = 0xff;
  }
  return uVar1;
}



int FUN_00066e7c(uint param_1,int param_2,uint param_3)

{
  undefined1 *puVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  uint uVar7;
  undefined1 auStack_20 [4];
  
  iVar4 = 0;
  uVar7 = param_1 & 0xfffc;
  iVar6 = (param_1 & 0xffff) - uVar7;
  iVar5 = 0;
  while( true ) {
    iVar2 = iVar5 - (param_3 & 0xffff);
    if (iVar2 < 0 == (iVar5 < 0 && -1 < iVar2)) {
      return iVar4;
    }
    if (iVar4 != 0) break;
    iVar2 = FUN_000689f2(uVar7, camry_host_addr(auStack_20), 4);
    if (iVar2 == 0) {
      iVar2 = (param_3 & 0xffff) - iVar5;
      iVar3 = 4 - iVar6;
      if (iVar3 - iVar2 < 0 != (iVar3 < 0 != iVar2 < 0 && iVar2 < 0 == iVar3 - iVar2 < 0)) {
        iVar2 = iVar3;
      }
      for (iVar3 = 0;
          iVar3 - iVar2 < 0 != (iVar3 < 0 != iVar2 < 0 && iVar2 < 0 == iVar3 - iVar2 < 0);
          iVar3 = iVar3 + 1) {
        puVar1 = ((undefined1 *)camry_host_ptr((uint32_t)(iVar5 + param_2)));
        iVar5 = iVar5 + 1;
        *puVar1 = auStack_20[iVar6 + iVar3];
      }
      uVar7 = uVar7 + 4 & 0xffff;
      iVar6 = 0;
    }
    else {
      if (iVar2 == 0x5a) {
        return 0x55555555;
      }
      iVar4 = -1;
    }
  }
  return iVar4;
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



/* Return1 onlywhen all32family0/all16repairedfamily1 statuses avoidpending
   highnibble20,busy0690/0691 neitherFFnorA5,and0673zero. Usedby0701/0800mode-readiness
   andexistingforegroundhandoff. No hardwarepowerpredicate. */

uint f33_application_nvm_is_ready(void)

{
  uint32_t puVar1;
  uint uVar2;
  int iVar3;
  int iVar4;
  
  puVar1 = 0xfebeb800u;
  uVar2 = FUN_00067984();
  if ((uVar2 == 1) && (uVar2 = FUN_000681aa(), uVar2 == 1)) {
    iVar3 = FUN_00068924();
    iVar4 = FUN_00068a4a();
    if (((iVar3 == 0xff) || (((iVar3 == 0xa5 || (iVar4 == 0xff)) || (iVar4 == 0xa5)))) ||
       ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x4e73))))) != '\0')) {
      uVar2 = 0;
    }
  }
  return uVar2;
}



int FUN_00066f68(void)

{
  return f33_publish_redundant_u8('Z',((undefined *)camry_host_ptr(0xfebf0671u)),((undefined *)camry_host_ptr(0xfebf10a9u)),((undefined *)camry_host_ptr(0xfebf10cdu)));
}



int FUN_00066f84(void)

{
  return f33_publish_redundant_u8('\0',((undefined *)camry_host_ptr(0xfebf0671u)),((undefined *)camry_host_ptr(0xfebf10a9u)),((undefined *)camry_host_ptr(0xfebf10cdu)));
}



int FUN_00066f9e(void)

{
  return f33_publish_redundant_u8('Z',((undefined *)camry_host_ptr(0xfebf0672u)),((undefined *)camry_host_ptr(0xfebf10aau)),((undefined *)camry_host_ptr(0xfebf10ceu)));
}



int FUN_00066fba(void)

{
  return f33_publish_redundant_u8('\0',((undefined *)camry_host_ptr(0xfebf0672u)),((undefined *)camry_host_ptr(0xfebf10aau)),((undefined *)camry_host_ptr(0xfebf10ceu)));
}



int FUN_00066fd4(void)

{
  return f33_publish_redundant_u8
            ('\0', ((uchar *)camry_host_ptr((uint32_t)((0xfebf0670u)))), ((uchar *)camry_host_ptr((uint32_t)((0xfebf10a8u)))), ((uchar *)camry_host_ptr((uint32_t)((0xfebf10ccu)))));
}



/* Return full R10=0. Exact-image selector used through FF038: ready0701 request2 takes software
   foreground restart, not0800. */

uint f33_platform_restart_selector_constant_zero(void)

{
  return 0;
}



/* Far-call trampoline: prepare {lp},0 / jarl 0x68318 / dispose 0,{lp},lp; byte-verified against the
   exact image. Forwards with registers and stack unchanged; marked as a thunk. Forwarding shape
   machine-verified; target semantics not recovered. */

void thunk_FUN_00068318(void)

{
  FUN_00068318();
  return;
}



/* For each registered family2 descriptor, clear setter flag, publish00/55/AA status and zero
   payload whole words in RAM. Preserve gaps and trailing bytes. No ROM-default copy or CRC
   computation. */

void f33_nvm_initialize_family2_ram(void)

{
  ushort uVar1;
  uint uVar2;
  int iVar3;
  undefined8 uVar4;
  uint *puVar5;
  int iVar6;
  
  uVar4 = 0xfebeb800;
  for (iVar6 = 0;
      (int)(iVar6 - (uint)f33_nvm_family2_object_count) < 0 !=
      (iVar6 < 0 && -1 < (int)(iVar6 - (uint)f33_nvm_family2_object_count)); iVar6 = iVar6 + 1) {
    iVar3 = (int)uVar4;
    (*((undefined1 *)camry_host_ptr((uint32_t)(iVar6 + iVar3 + 0x4e5b)))) = 0;
    f33_publish_redundant_u8
              ('\0',((uchar *)camry_host_ptr((uint32_t)(iVar3 + 0x4e50 + iVar6))),((uchar *)camry_host_ptr((uint32_t)(iVar3 + 0x5898 + iVar6))),
               ((uchar *)camry_host_ptr((uint32_t)(iVar3 + 0x58bc + iVar6))));
    uVar1 = f33_nvm_family2_descriptors[iVar6].payload_bytes;
    puVar5 = ((void *)camry_host_ptr((uint32_t)(f33_nvm_family2_descriptors[iVar6].ram_buffer)));
    for (uVar2 = 0; uVar2 < uVar1 >> 2; uVar2 = uVar2 + 1 & 0xffff) {
      puVar5[uVar2] = 0;
    }
  }
  return;
}



/* For11 groups, repair status triplet with fallback30. Exact10 bypasses CRC; other values
   call67090, retry exactly once only on non10, then publish last status across all planes. Real
   all-recompute sweep publishes10,30,10,30,10,10,10,10,10,10,10 with399 CIN writes. Status10 bypass
   can preserve prior10 even for the zero-filled groups. For registered11 groups
   repair0650/1098/10BC with fallback30. otherwise call67090 and retry once only on non10; publish
   last result. All-recompute records10,30,10,30,10,10,10,10,10,10,10 with399 input writes/425 MMIO
   writes. Cached10 can bypass even zero-filled ROM groups; shared status also has RAM-update
   writers. */

void f33_nvm_refresh_family2_status(void)

{
  int iVar1;
  undefined8 uVar2;
  uint uVar3;
  uint uVar4;
  
  uVar2 = 0xfebeb800;
  for (uVar4 = 0; uVar4 < f33_nvm_family2_object_count; uVar4 = uVar4 + 1 & 0xffff) {
    iVar1 = (int)uVar2;
    uVar3 = f33_read_repair_redundant_u8
                      (camry_host_addr(((uchar *)camry_host_ptr((uint32_t)(uVar4 + iVar1 + 0x4e50)))), camry_host_addr(((uchar *)camry_host_ptr((uint32_t)(uVar4 + iVar1 + 0x5898)))), camry_host_addr(((uchar *)camry_host_ptr((uint32_t)(uVar4 + iVar1 + 0x58bc)))), '0');
    if (uVar3 != 0x10) {
      uVar3 = f33_nvm_check_family2_rom_crc((ushort)uVar4);
      if (uVar3 != 0x10) {
        uVar3 = f33_nvm_check_family2_rom_crc((ushort)uVar4);
      }
      f33_publish_redundant_u8
                ((uchar)uVar3,((uchar *)camry_host_ptr((uint32_t)(uVar4 + iVar1 + 0x4e50))),((uchar *)camry_host_ptr((uint32_t)(uVar4 + iVar1 + 0x5898))),
                 ((uchar *)camry_host_ptr((uint32_t)(uVar4 + iVar1 + 0x58bc))));
    }
  }
  return;
}



/* Low16 object bound before source. Copy payload whole words into descriptor RAM, set flag5A and
   publish10/45/BA. Return1, invalid0. No ROM CRC or flash programming; no flag reader recovered. */

uint f33_nvm_set_family2_record(uint object,uint *source)

{
  uint uVar1;
  uint32_t puVar2;
  uint uVar3;
  
  puVar2 = 0xfebeb800u;
  uVar3 = object & 0xffff;
  uVar1 = (uint)f33_nvm_family2_object_count;
  if (uVar3 < uVar1) {
    f33_copy_whole_words
              (((uint32_t *)camry_host_ptr((uint32_t)(f33_nvm_family2_descriptors[uVar3].ram_buffer))), source, 
               f33_nvm_family2_descriptors[uVar3].payload_bytes);
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(uVar3 + 0x4e5b))))) = 0x5a;
    f33_publish_redundant_u8
              ('\x10', ((undefined *)camry_host_ptr((uint32_t)(puVar2 + uVar3 + 0x4e50))), ((undefined *)camry_host_ptr((uint32_t)(puVar2 + uVar3 + 0x5898))), ((undefined *)camry_host_ptr((uint32_t)(puVar2 + uVar3 + 0x58bc))));
  }
  return (uint)(uVar3 < uVar1);
}



/* If FLMDCNT.bit0 is clear, return. Otherwise enter PMRFFFF, attempt at most three A5/0/FFFFFFFF/0
   protected sequences, read back control, SYNCP and inspect FLMDPS.bit0; restore prior PMR. No
   final success result. Manual pp2869-2874 identifies internal pull control, not actual pin level
   or persistence. */

void f33_select_flmd0_internal_pulldown(void)

{
  uint saved_mask;
  uint uVar1;
  byte bVar2;
  
  uVar1 = FLMDCNT;
  if ((uVar1 & 1) != 0) {
    uVar1 = 1;
    saved_mask = f33_priority_mask_enter(0xffff);
    for (bVar2 = 0; ((uVar1 & 1) != 0 && (bVar2 < 3)); bVar2 = bVar2 + 1) {
      FLMDPCMD = 0xa5;
      FLMDCNT = 0;
      FLMDCNT = 0xffffffff;
      FLMDCNT = 0;
      uVar1 = FLMDCNT;
      __synchronize();
      uVar1 = FLMDPS;
    }
    f33_priority_mask_restore(saved_mask);
  }
  return;
}



void FUN_000672c0(void)

{
  uchar *puVar1;
  ushort uVar2;
  int iVar3;
  uchar *puVar4;
  uint uVar5;
  
  for (iVar3 = 0;
      (int)(iVar3 - (uint)f33_nvm_family0_request_cell_count) < 0 !=
      (iVar3 < 0 && -1 < (int)(iVar3 - (uint)f33_nvm_family0_request_cell_count)); iVar3 = iVar3 + 1
      ) {
    f33_nvm_family0_request_cells[iVar3].object = 0xffff;
    f33_nvm_family0_request_cells[iVar3].state = 0xff;
  }
  for (iVar3 = 0;
      (int)(iVar3 - (uint)f33_nvm_family0_object_count) < 0 !=
      (iVar3 < 0 && -1 < (int)(iVar3 - (uint)f33_nvm_family0_object_count)); iVar3 = iVar3 + 1) {
    f33_nvm_family0_status[iVar3] = '\0';
    uVar2 = f33_nvm_family0_ram_descriptors[iVar3].payload_bytes;
    puVar4 = ((void *)camry_host_ptr((uint32_t)(f33_nvm_family0_ram_descriptors[iVar3].buffer)));
    for (uVar5 = 0; uVar5 < uVar2 >> 2; uVar5 = uVar5 + 1 & 0xffff) {
      puVar1 = puVar4 + uVar5 * 4;
      puVar1[0] = '\0';
      puVar1[1] = '\0';
      puVar1[2] = '\0';
      puVar1[3] = '\0';
    }
  }
  f33_nvm_family0_probe_offset = 0;
  f33_nvm_family0_scan_cursor = 0;
  DAT_febf0684 = 0;
  f33_nvm_family0_active_object = 0xffff;
  f33_nvm_family0_phase = '\0';
  DAT_febf067f = 0;
  f33_nvm_family0_span_request = '\0';
  f33_nvm_family0_classification_latch = '\0';
  DAT_febf067c = 0;
  f33_nvm_family0_request_consumer = '\0';
  f33_nvm_family0_request_producer = '\0';
  return;
}



void FUN_00067346(void)

{
  f33_nvm_family0_scan_cursor = 0;
  f33_nvm_family0_probe_offset = 0;
  return;
}



/* Scan all65 object halfwords at048A+4*i for low16 object; return1 on first match else0. Ignore
   state, queue indices and empty sentinel meaning. Native duplicate outside the active interval
   overrides the selector's status even when that cell's state isFF. Scan all65 object halfwords
   at048A+4*i for low16 requested object; return1 first match else0. Ignore state and
   producer/consumer indices. Real selector sees a stateFF duplicate outside the active interval and
   overrides status32 to20. No local object bound or special FFFF interpretation. */

uint f33_nvm_family0_has_request_cell(ushort object)

{
  uint uVar1;
  
  uVar1 = 0;
  while( true ) {
    if (f33_nvm_family0_request_cell_count <= uVar1) {
      return 0;
    }
    if (f33_nvm_family0_request_cells[uVar1].object == object) break;
    uVar1 = uVar1 + 1 & 0xff;
  }
  return 1;
}



/* Recover indices first. Span flag5A calls687DE, ignores return and selects phase11/return1 without
   dequeue. Empty ring returns0. Otherwise clear state/object but preserve+1, then advance consumer
   BEFORE object/kind validation. Kind11 calls684D0, selects phase22; 22 always calls6853E,33 only
   when completion!=5A; both select phase33. Ignore arm return; set active object/status21 and
   return1. Unknown kind publishes32/returns0 without changing phase/active. Any matching remaining
   cell overrides status20. Invalid object only consumes cell. Bulk dispatch beyond the
   computed-span boundary is not proved. Recover indices. Span flag5A selects phase11/return1
   despite real busy rejection. Ordinary dequeue clears state/object and advances consumer before
   validation, preserving+1.11 selects read phase22;22 always attempts write,33 only if
   completion!=5A, both phase33. status21/active/return1. Unknown kind status32/return0 preserves
   phase/active; invalid object only consumes. Any remaining matching cell overrides20. Family0
   empty ring does no checksum scan. Bulk operation after6879C remains bounded. */

uint f33_nvm_select_family0_request(void)

{
  char *pcVar1;
  char cVar2;
  ushort object;
  uint32_t puVar3;
  uint uVar4;
  uint uVar5;
  undefined1 uVar6;
  undefined1 uVar7;
  byte bStack_16;
  byte bStack_15;
  
  puVar3 = 0xfebeb800u;
  f33_nvm_recover_family0_request_indices(&bStack_16,&bStack_15);
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x4e7e))))) == 'Z') {
    f33_nvm_dispatch_family0_page_span();
    uVar6 = 0x11;
    uVar5 = 1;
    goto LAB_000674ca;
  }
  uVar6 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x4e80)))));
  uVar5 = 0;
  if ((uint)bStack_16 == (uint)bStack_15) goto LAB_000674ca;
  pcVar1 = ((undefined *)camry_host_ptr((uint32_t)(puVar3 + (uint)bStack_15 * 4 + 0x4c88)));
  object = *(ushort *)(pcVar1 + 2);
  cVar2 = *pcVar1;
  pcVar1[2] = -1;
  pcVar1[3] = -1;
  *pcVar1 = -1;
  uVar4 = f33_nvm_advance_family0_request_index(bStack_15);
  bStack_15 = (byte)uVar4;
  if ((uint)f33_nvm_family0_object_count <= (uint)object) goto LAB_000674ca;
  if (cVar2 == '\x11') {
    f33_nvm_arm_family0_read(object);
    uVar6 = 0x22;
LAB_000674aa:
    uVar7 = 0x21;
    (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + 0x4e82)))) = object;
    uVar5 = 1;
  }
  else {
    if ((cVar2 == '\"') || (cVar2 == '3')) {
      uVar5 = f33_nvm_get_family0_completion(object);
      if ((cVar2 == '\"') || (uVar5 != 0x5a)) {
        f33_nvm_arm_family0_write(object);
      }
      uVar6 = 0x33;
      goto LAB_000674aa;
    }
    uVar7 = 0x32;
  }
  uVar4 = f33_nvm_family0_has_request_cell(object);
  if (uVar4 == 1) {
    uVar7 = 0x20;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(object + 0x4b08))))) = uVar7;
LAB_000674ca:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x4e80))))) = uVar6;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x4e7b))))) = bStack_15;
  return uVar5;
}



void FUN_000674dc(void)

{
  uchar uVar1;
  ushort object;
  uint32_t puVar2;
  uint uVar3;
  undefined1 uVar4;
  uint uVar5;
  
  object = f33_nvm_family0_active_object;
  uVar1 = f33_nvm_family0_phase;
  puVar2 = 0xfebeb800u;
  uVar5 = (uint)f33_nvm_family0_active_object;
  uVar3 = f33_nvm_get_family0_completion(f33_nvm_family0_active_object);
  if (uVar1 == '\x11') {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x4e7e))))) = 0xa5;
  }
  else {
    if (uVar1 == '\"') {
      if (f33_nvm_family0_object_count <= uVar5) goto LAB_00067596;
      if (uVar3 == 0x5a) {
        uVar4 = 0x10;
      }
      else {
        uVar3 = f33_nvm_family0_chunk_cost(f33_nvm_family0_ram_descriptors[uVar5].payload_bytes);
        uVar3 = f33_nvm_classify_family0_chunks
                          (object,0,(short)uVar3 *
                                    f33_nvm_family0_ram_descriptors[uVar5].logical_count);
        uVar4 = 0x11;
        if (uVar3 == 0) {
          uVar4 = 0x30;
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x4e7d))))) = 0x5a;
        }
      }
    }
    else {
      if ((uVar1 != '3') || (f33_nvm_family0_object_count <= uVar5)) goto LAB_00067596;
      uVar4 = 0x10;
      if (uVar3 != 0x5a) {
        uVar4 = 0x31;
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x4e7c))))) = 0x5a;
      }
    }
    uVar3 = f33_nvm_family0_has_request_cell(object);
    if (uVar3 == 1) {
      uVar4 = 0x20;
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(uVar5 + 0x4b08))))) = uVar4;
  }
LAB_00067596:
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + 0x4e82)))) = 0xffff;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x4e80))))) = 0;
  return;
}



/* Resume0676 with fresh charge0. Completion5A publishes status10 without charge or payload access.
   Otherwise cost=low16(count*689DE(payload)); admit full object while cost+charge<=ROM18, charge
   before 68946. Result0 publishes30 and latches067D=5A, including blocked reads; other full-object
   results publish11. Stop before exceeding budget. Generic split branch requires fresh charge0 and
   object cost>18; all32 registered costs<=12 make it unreachable here. Store cursor/offset and
   halfword charge; return5A iff cursor>=32. Native disabled charge4, blocked valid-object charge6
   and free completed-object publication. Completed5A objects publish10 for free without reading
   payload. Other full objects charge low16(count*chunk_cost) before probing while cumulative
   charge<=18. Probe0 publishes30 and latches067D5A even for blocked reads; other full results
   publish11. Store cursor/offset and u16 charge; Generic split path requires fresh object cost>18;
   all registered costs<=12 prove it unreachable for this image. Native disabled cost4 and blocked
   valid cost6. */

uint f33_nvm_classify_family0_pass(ushort *charged_out)

{
  undefined1 uVar1;
  int iVar2;
  uint uVar3;
  undefined8 uVar4;
  ushort chunk_offset;
  uint uVar5;
  uint uVar6;
  uint uVar7;
  uint uVar8;
  ushort object;
  uint uVar9;
  
  uVar4 = 0xfebeb800;
  uVar9 = (uint)f33_nvm_family0_scan_cursor;
  uVar6 = 0;
  iVar2 = 0x5a;
  uVar7 = 0;
  uVar8 = 0;
  do {
    while( true ) {
      uVar5 = (uint)f33_nvm_family0_object_count;
      object = (ushort)uVar9;
      if ((uVar5 <= uVar9) || (iVar2 == 0)) {
        (*((ushort *)camry_host_ptr((uint32_t)((int)uVar4 + 0x4e76)))) = object;
        (*((short *)camry_host_ptr((uint32_t)((int)uVar4 + 0x4e78)))) = (short)uVar8;
        *charged_out = (ushort)uVar7;
        if (uVar5 <= uVar9) {
          uVar6 = 0x5a;
        }
        return uVar6;
      }
      uVar5 = f33_nvm_get_family0_completion(object);
      if (uVar5 != 0x5a) break;
      uVar1 = 0x10;
LAB_0006764c:
      (*((undefined1 *)camry_host_ptr((uint32_t)(uVar9 + (int)uVar4 + 0x4b08)))) = uVar1;
      iVar2 = 0x5a;
      uVar9 = uVar9 + 1 & 0xffff;
    }
    uVar8 = f33_nvm_family0_chunk_cost(f33_nvm_family0_ram_descriptors[uVar9].payload_bytes);
    uVar3 = (uint)f33_nvm_classification_budget;
    uVar5 = (int)(short)f33_nvm_family0_ram_descriptors[uVar9].logical_count * (int)(short)uVar8 &
            0xffff;
    if ((int)((uVar5 + uVar7) - uVar3) < 0 || uVar5 + uVar7 == uVar3) {
      uVar8 = 0;
      chunk_offset = 0;
      uVar3 = uVar5;
LAB_00067628:
      uVar7 = uVar7 + uVar3 & 0xffff;
      uVar5 = f33_nvm_classify_family0_chunks(object,chunk_offset,(ushort)uVar3);
      if (uVar5 == 0) {
        uVar1 = 0x30;
        (*((undefined1 *)camry_host_ptr((uint32_t)((int)uVar4 + 0x4e7d)))) = 0x5a;
      }
      else {
        if (uVar8 != 0) goto LAB_0006765e;
        uVar1 = 0x11;
      }
      goto LAB_0006764c;
    }
    if (uVar7 == 0) {
      chunk_offset = (*((ushort *)camry_host_ptr((uint32_t)((int)uVar4 + 0x4e78))));
      uVar5 = uVar5 - chunk_offset;
      if ((int)(uVar5 - uVar3) < 0 == ((int)uVar5 < 0 && -1 < (int)(uVar5 - uVar3)) &&
          uVar5 != uVar3) {
        uVar8 = uVar3 + chunk_offset & 0xffff;
      }
      else {
        uVar3 = uVar5 & 0xffff;
        uVar8 = 0;
      }
      goto LAB_00067628;
    }
    uVar8 = 0;
LAB_0006765e:
    iVar2 = 0;
  } while( true );
}



/* Truncate both indices to low8. Return producer+1==(consumer==0?ROM cell_count65:consumer). No
   cell inspection; reserves one cell. */

uint f33_nvm_family0_request_full(uint producer,uint consumer)

{
  uint uVar1;
  
  uVar1 = consumer & 0xff;
  if (uVar1 == 0) {
    uVar1 = (uint)f33_nvm_family0_request_cell_count;
  }
  return (uint)((producer & 0xff) + 1 == uVar1);
}



/* Return zero-extended low8 predecessor, with zero wrapping to ROM cell_count65 minus1. No general
   index validation. */

uint f33_nvm_previous_family0_request(uint index)

{
  uint uVar1;
  
  uVar1 = index & 0xff;
  if (uVar1 == 0) {
    uVar1 = (uint)f33_nvm_family0_request_cell_count;
  }
  return uVar1 - 1 & 0xff;
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



bool FUN_00067894(void)

{
  undefined1 uVar1;
  uint32_t puVar2;
  uchar uStack_6;
  uchar uStack_5;
  
  puVar2 = 0xfebeb800u;
  f33_nvm_recover_family0_request_indices(&uStack_6,&uStack_5);
  if (uStack_6 == uStack_5) {
    uVar1 = 0x5a;
  }
  else {
    uVar1 = 0xff;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x4e7e))))) = uVar1;
  return uStack_6 == uStack_5;
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



/* Return zero-extended byte0680; snapshot precedes hold decoding. Exact LDBU0680 into full32r10
   thenJMPLP. Native work-selection calls snapshot this family0 phase before hold repair. */

uint f33_nvm_get_family0_phase(void)

{
  return (uint)f33_nvm_family0_phase;
}



void FUN_00067a52(void)

{
  f33_nvm_family1_scan_cursor = 0;
  return;
}



/* Same consume-before-validation and11/22/33 selection contract as family0, using68626/6869E and
   redundant status publication; write selection additionally clears068A. Span flag5A selects
   phase11 regardless6889A result. Empty ring scans repaired status triplets with fallback12; first
   status10 with failing live checksum calls68626 then stops, but still returns0 and preserves
   phase/active/completion. Native empty-ring failure queues three actual reads while leaving prior
   completion5A; caller reachability/restoration is not inferred. Recover indices. Span flag5A
   selects phase11/return1 despite real busy rejection. Ordinary dequeue clears state/object and
   advances consumer before validation, preserving+1.11 selects read phase22;22 always attempts
   write,33 only if completion!=5A, both phase33. Ignore arm return; status21/active/return1.
   Unknown kind status32/return0 preserves phase/active; invalid object only consumes. Any remaining
   matching cell overrides20. Family1 clears whole-write retry for22/33; empty ring repairs triplets
   then first status10/checksum failure submits reads yet returns0, preserving
   phase/active/completion. Native real three-read enqueue with old completion5A is a direct
   helper-state proof, not restoration. Bulk operation after6879C remains bounded. */

uint f33_nvm_select_family1_request(void)

{
  code *pcVar1;
  code cVar2;
  ushort object;
  int iVar3;
  undefined8 uVar4;
  uint uVar5;
  int iVar6;
  uint uVar7;
  undefined1 uVar8;
  uchar value;
  uint uVar9;
  int iVar10;
  byte bStack_1a;
  byte bStack_19;
  
  uVar4 = 0xfebeb800;
  f33_nvm_recover_family1_request_indices(&bStack_1a,&bStack_19);
  iVar3 = (int)uVar4;
  if ((*((char *)camry_host_ptr((uint32_t)(iVar3 + 0x4e88)))) == 'Z') {
    f33_nvm_dispatch_family1_page_span();
    uVar8 = 0x11;
    uVar7 = 1;
    goto LAB_00067c7a;
  }
  uVar8 = (*((undefined1 *)camry_host_ptr((uint32_t)(iVar3 + 0x4e89))));
  uVar7 = 0;
  if ((uint)bStack_1a == (uint)bStack_19) {
    for (iVar10 = 0; iVar3 = (int)uVar4,
        (int)(iVar10 - (uint)f33_nvm_family1_object_count) < 0 !=
        (iVar10 < 0 && -1 < (int)(iVar10 - (uint)f33_nvm_family1_object_count)); iVar10 = iVar10 + 1
        ) {
      uVar5 = f33_read_repair_redundant_u8
                        (camry_host_addr(((uchar *)camry_host_ptr((uint32_t)(iVar3 + 0x4b28 + iVar10)))), camry_host_addr(((uchar *)camry_host_ptr((uint32_t)(iVar3 + 0x5888 + iVar10)))), camry_host_addr(((uchar *)camry_host_ptr((uint32_t)(iVar3 + 0x58ac + iVar10)))), '\x12');
      if (uVar5 == 0x10) {
        iVar6 = f33_nvm_check_family1_checksum((ushort)iVar10);
        iVar3 = (int)uVar4;
        if (iVar6 != 1) {
          f33_nvm_submit_family1_read_copies((ushort)iVar10);
          break;
        }
      }
    }
    goto LAB_00067c7a;
  }
  pcVar1 = ((void *)camry_host_ptr((uint32_t)(0x4d8cu + (uint)bStack_19 * 4 + iVar3)));
  object = *(ushort *)(pcVar1 + 2);
  uVar9 = (uint)object;
  cVar2 = *pcVar1;
  *(undefined2 *)(pcVar1 + 2) = 0xffff;
  *pcVar1 = (code)0xff;
  uVar5 = f33_nvm_advance_family1_request_index(bStack_19);
  bStack_19 = (byte)uVar5;
  if (f33_nvm_family1_object_count <= uVar9) goto LAB_00067c7a;
  if (cVar2 == (code)0x11) {
    f33_nvm_submit_family1_read_copies(object);
    uVar8 = 0x22;
    (*((ushort *)camry_host_ptr((uint32_t)(iVar3 + 0x4e8c)))) = object;
LAB_00067c06:
    value = '!';
    uVar7 = 1;
  }
  else {
    if ((cVar2 == (code)0x22) || (cVar2 == (code)0x33)) {
      uVar7 = f33_nvm_get_family1_completion(object);
      if ((cVar2 == (code)0x22) || (uVar7 != 0x5a)) {
        f33_nvm_submit_family1_write_copies(object);
      }
      (*((ushort *)camry_host_ptr((uint32_t)(iVar3 + 0x4e8c)))) = object;
      uVar8 = 0x33;
      (*((undefined1 *)camry_host_ptr((uint32_t)(iVar3 + 0x4e8a)))) = 0;
      goto LAB_00067c06;
    }
    value = '2';
  }
  uVar5 = f33_nvm_family1_has_request_cell(object);
  if (uVar5 == 1) {
    value = ' ';
  }
  f33_publish_redundant_u8
            (value,((uchar *)camry_host_ptr((uint32_t)(iVar3 + 0x4b28 + uVar9))),((uchar *)camry_host_ptr((uint32_t)(iVar3 + 0x5888 + uVar9))),
             ((uchar *)camry_host_ptr((uint32_t)(iVar3 + 0x58ac + uVar9))));
LAB_00067c7a:
  (*((undefined1 *)camry_host_ptr((uint32_t)(iVar3 + 0x4e89)))) = uVar8;
  (*((byte *)camry_host_ptr((uint32_t)(iVar3 + 0x4e87)))) = bStack_19;
  return uVar7;
}



/* Snapshot phase/object and queue indices. Phase11 sets0688=A5. Valid phase22/33 completion5A
   publishes checksum seed then status10. Phase22 failure calls68A6C: zero->30, every other
   result->11; no checksum publication. Phase33 failure increments retry below2, calls 6869E and
   returns before cleanup regardless rearm result; exhaustion selects31. A matching request cell
   overrides status to20 after any seed publication. Publish all status planes; clear phase,
   preserve recovered producer index, set active objectFFFF. Invalid phase/object only cleans up.
   Native real classifier/cancellation and accepted whole-write retry; explicit FACI events are not
   physical blankness or programming proof. Phase11 sets0688A5. Valid phase22/33 completion5A
   publishes seed/status10 before any pending-cell override20. Failed phase22 calls
   real68A6C/cancellation: zero->30; all nonzero->11, with seeds untouched. Phase33 failure
   increments retry below2 and returns before cleanup regardless rearm result; Cleanup clears phase,
   preserves recovered producer and sets active objectFFFF; invalid phase/object skips publication.
   Native prior boundaries plus composed all-blank/nonblank/blocked failure and accepted three-write
   retry; explicit FACI inputs are not physical flash proof. */

void f33_nvm_handle_family1_completion(void)

{
  ushort object;
  uint32_t puVar1;
  uint uVar2;
  uchar uVar3;
  uint uVar4;
  uchar uStack_e;
  uchar uStack_d;
  
  object = f33_nvm_family1_active_object;
  uVar3 = f33_nvm_family1_phase;
  puVar1 = 0xfebeb800u;
  uVar4 = (uint)f33_nvm_family1_active_object;
  f33_nvm_recover_family1_request_indices(&uStack_e,&uStack_d);
  uVar2 = f33_nvm_get_family1_completion(object);
  if (uVar3 == '\x11') {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x4e88))))) = 0xa5;
    goto LAB_00067d82;
  }
  if (uVar3 == '\"') {
    if (f33_nvm_family1_object_count <= uVar4) goto LAB_00067d82;
    if (uVar2 == 0x5a) goto LAB_00067d38;
    uVar2 = f33_nvm_classify_family1_pages(object);
    uVar3 = '\x11';
    if (uVar2 == 0) {
      uVar3 = '0';
    }
  }
  else {
    if ((uVar3 != '3') || (f33_nvm_family1_object_count <= uVar4)) goto LAB_00067d82;
    if (uVar2 == 0x5a) {
LAB_00067d38:
      uVar3 = '\x10';
      f33_nvm_publish_family1_checksum(object);
    }
    else {
      if ((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x4e8a))))) < 2) {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x4e8a))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x4e8a))))) + 1;
        f33_nvm_submit_family1_write_copies(object);
        return;
      }
      uVar3 = '1';
    }
  }
  uVar2 = f33_nvm_family1_has_request_cell(object);
  if (uVar2 == 1) {
    uVar3 = ' ';
  }
  f33_publish_redundant_u8
            (uVar3, ((undefined *)camry_host_ptr((uint32_t)(puVar1 + uVar4 + 0x4b28))), ((undefined *)camry_host_ptr((uint32_t)(puVar1 + uVar4 + 0x5888))), ((undefined *)camry_host_ptr((uint32_t)(puVar1 + uVar4 + 0x58ac))));
LAB_00067d82:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x4e89))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x4e86))))) = uStack_e;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + 0x4e8c)))) = 0xffff;
  return;
}



/* Resume068E. Completion5A publishes live-RAM checksum/status10 without charge. Otherwise add3
   modulo16; stop if aboveROM18, else call68A6C and choose30 only for result0,11 for every nonzero
   result. Publish all three planes, advance cursor, store068E; return5A iff cursor>=16. No
   pending-cell override. Native exact/over-budget, disabled and real last-object blank/nonblank
   classification. Completion5A computes live-RAM seed/status10 without charge; otherwise add3
   modulo16 and stop aboveROM18. Real68A6C result0 selects30, every nonzero selects11; publish all
   planes and advance. Store cursor, return5A iff >=16. Native exact/over-budget, disabled and real
   last-object blank/nonblank cancellation paths with explicit hardware inputs. */

uint f33_nvm_classify_family1_pass(ushort already_charged)

{
  int iVar1;
  undefined8 uVar2;
  uint uVar3;
  uint uVar4;
  uchar value;
  uint uVar5;
  ushort object;
  uint uVar6;
  
  uVar2 = 0xfebeb800;
  uVar6 = (uint)f33_nvm_family1_scan_cursor;
  uVar4 = 0;
  while( true ) {
    iVar1 = (int)uVar2;
    uVar5 = (uint)f33_nvm_family1_object_count;
    object = (ushort)uVar6;
    if (uVar5 <= uVar6) break;
    uVar3 = f33_nvm_get_family1_completion(object);
    iVar1 = (int)uVar2;
    if (uVar3 == 0x5a) {
      value = '\x10';
      f33_nvm_publish_family1_checksum(object);
    }
    else {
      already_charged = already_charged + 3;
      if (f33_nvm_classification_budget < already_charged) break;
      uVar5 = f33_nvm_classify_family1_pages(object);
      value = '\x11';
      if (uVar5 == 0) {
        value = '0';
      }
    }
    iVar1 = (int)uVar2;
    f33_publish_redundant_u8
              (value,((uchar *)camry_host_ptr((uint32_t)(iVar1 + 0x4b28 + uVar6))),((uchar *)camry_host_ptr((uint32_t)(iVar1 + 0x5888 + uVar6))),
               ((uchar *)camry_host_ptr((uint32_t)(iVar1 + 0x58ac + uVar6))));
    uVar6 = uVar6 + 1 & 0xffff;
  }
  (*((ushort *)camry_host_ptr((uint32_t)(iVar1 + 0x4e8e)))) = object;
  if (uVar5 <= uVar6) {
    uVar4 = 0x5a;
  }
  return uVar4;
}



/* Truncate both indices to low8. Return producer+1==(consumer==0?ROM cell_count49:consumer). No
   cell inspection; reserves one cell. */

uint f33_nvm_family1_request_full(uint producer,uint consumer)

{
  uint uVar1;
  
  uVar1 = consumer & 0xff;
  if (uVar1 == 0) {
    uVar1 = (uint)f33_nvm_family1_request_cell_count;
  }
  return (uint)((producer & 0xff) + 1 == uVar1);
}



/* Return zero-extended low8 predecessor, with zero wrapping to ROM cell_count49 minus1. No general
   index validation. */

uint f33_nvm_previous_family1_request(uint index)

{
  uint uVar1;
  
  uVar1 = index & 0xff;
  if (uVar1 == 0) {
    uVar1 = (uint)f33_nvm_family1_request_cell_count;
  }
  return uVar1 - 1 & 0xff;
}



/* Recover indices before full and low16 object<16 gates. Immediate predecessor kind11/object
   duplicate returns1 without status publication, even for empty indices. Otherwise store
   kind/object, advance producer and publish20/75/8A. Recovery can change both globals before
   rejection; this routine finally republishes producer. No descriptor, completion or busy gate. */

uint f33_nvm_enqueue_family1_read(uint object)

{
  byte index;
  uint32_t puVar1;
  uint uVar2;
  uint producer;
  uint uVar3;
  byte bStack_e;
  byte bStack_d;
  
  puVar1 = 0xfebeb800u;
  uVar3 = object & 0xffff;
  f33_nvm_recover_family1_request_indices(&bStack_e,&bStack_d);
  index = bStack_e;
  producer = (uint)bStack_e;
  uVar2 = f33_nvm_family1_request_full(producer,(uint)bStack_d);
  if ((uVar2 == 1) || (f33_nvm_family1_object_count <= uVar3)) {
    uVar2 = 0;
  }
  else {
    uVar2 = f33_nvm_previous_family1_request(producer);
    if (((*((ushort *)camry_host_ptr((uint32_t)(0x4d8cu + (int)(puVar1 + uVar2 * 4) + 2)))) != uVar3) ||
       ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x4d8cu + (uint32_t)((int)(puVar1 + uVar2 * 4)))))) != (code)0x11)) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x4d8cu + (uint32_t)((int)(puVar1 + producer * 4)))))) = (code)0x11;
      (*((short *)camry_host_ptr((uint32_t)(puVar1 + producer * 4 + 0x4d8e)))) = (short)object;
      uVar2 = f33_nvm_advance_family1_request_index(index);
      bStack_e = (byte)uVar2;
      f33_publish_redundant_u8
                (' ', ((undefined *)camry_host_ptr((uint32_t)(puVar1 + uVar3 + 0x4b28))), ((undefined *)camry_host_ptr((uint32_t)(puVar1 + uVar3 + 0x5888))), ((undefined *)camry_host_ptr((uint32_t)(puVar1 + uVar3 + 0x58ac))));
    }
    uVar2 = 1;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x4e86))))) = bStack_e;
  return uVar2;
}



/* Reject low16 object>=16 before repair/recovery. Vote status with fallback12, recover indices,
   then reject full or voted21 before source/descriptor-content reads. Inclusive write-kind scan and
   changed-word copy precede placement as in family0. Tail duplicate republishes original voted
   status; other admissions publish20. Opaque bytes stay at physical slots. No checksum, completion,
   disabled-descriptor or busy gate; no normal rejection after copy. */

uint f33_nvm_set_family1_record(uint object,uint *source)

{
  int iVar1;
  int iVar2;
  code cVar3;
  int iVar4;
  undefined8 uVar5;
  uint uVar6;
  uint uVar7;
  uint uVar8;
  uint uVar9;
  code cVar10;
  uint uVar11;
  uint uVar12;
  uint uVar13;
  byte bStack_3a;
  byte bStack_39;
  uchar *puStack_38;
  uchar *puStack_34;
  uint *puStack_30;
  
  uVar5 = 0xfebeb800;
  uVar12 = object & 0xffff;
  if (uVar12 < f33_nvm_family1_object_count) {
    puStack_34 = f33_nvm_family1_status;
    puStack_38 = f33_app_nvm_family1_status_xor55;
    puStack_30 = source;
    uVar6 = f33_read_repair_redundant_u8
                      (camry_host_addr(f33_nvm_family1_status + uVar12), camry_host_addr(f33_app_nvm_family1_status_xor55 + uVar12), camry_host_addr(f33_app_nvm_family1_status_xorAA + uVar12), '\x12');
    f33_nvm_recover_family1_request_indices(&bStack_3a,&bStack_39);
    uVar11 = (uint)bStack_3a;
    uVar13 = (uint)bStack_39;
    uVar7 = f33_nvm_family1_request_full(uVar11,uVar13);
    iVar4 = (int)uVar5;
    if ((uVar7 == 1) || (uVar6 == 0x21)) {
      uVar12 = 0;
    }
    else {
      uVar8 = f33_nvm_previous_family1_request(uVar11);
      cVar10 = (code)0xff;
      uVar9 = (uint)f33_nvm_family1_request_cell_count;
      for (uVar7 = uVar9; uVar7 != 0; uVar7 = uVar7 - 1) {
        iVar4 = uVar13 * 4 + (int)uVar5;
        cVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x4d8cu + (uint32_t)(iVar4)))));
        if (((*((ushort *)camry_host_ptr((uint32_t)(iVar4 + 0x4d8e)))) == uVar12) &&
           ((cVar3 == (code)0x22 || (cVar3 == (code)0x33)))) {
          cVar10 = cVar3;
        }
        if ((uVar13 == uVar11) || (cVar10 != (code)0xff)) break;
        uVar13 = f33_nvm_advance_family1_request_index((uchar)uVar13);
        bStack_39 = (byte)uVar13;
      }
      uVar13 = f33_update_whole_words
                         (((uint32_t *)camry_host_ptr((uint32_t)(f33_nvm_family1_ram_descriptors[uVar12].buffer))), puStack_30, 
                          f33_nvm_family1_ram_descriptors[uVar12].payload_bytes);
      iVar4 = (int)uVar5;
      if ((uVar13 == 1) || (cVar10 == (code)0x22)) {
        cVar10 = (code)0x22;
      }
      else {
        cVar10 = (code)0x33;
      }
      uVar13 = (uint)bStack_39;
      if (uVar13 == uVar8) {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x4d8cu + (uint32_t)(uVar13 * 4 + iVar4))))) = cVar10;
      }
      else {
        uVar6 = (uint)bStack_3a;
        uVar7 = uVar6;
        if (uVar13 != uVar6) {
          for (; uVar7 = uVar6, uVar9 != 0; uVar9 = uVar9 - 1) {
            uVar11 = f33_nvm_advance_family1_request_index((uchar)uVar13);
            iVar4 = (int)uVar5;
            uVar7 = uVar13;
            if (uVar13 == uVar8) break;
            iVar2 = uVar11 * 4 + iVar4;
            iVar1 = uVar13 * 4 + iVar4;
            cVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x4d8cu + (uint32_t)(iVar2)))));
            bStack_39 = (byte)uVar11;
            (*((undefined2 *)camry_host_ptr((uint32_t)(iVar1 + 0x4d8e)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(iVar2 + 0x4d8e))));
            (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x4d8cu + (uint32_t)(iVar1))))) = cVar3;
            uVar13 = uVar11;
          }
        }
        iVar2 = uVar7 * 4 + iVar4;
        uVar6 = 0x20;
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x4d8cu + (uint32_t)(iVar2))))) = cVar10;
        (*((short *)camry_host_ptr((uint32_t)(iVar2 + 0x4d8e)))) = (short)object;
        uVar13 = f33_nvm_advance_family1_request_index((uchar)uVar7);
        bStack_3a = (byte)uVar13;
      }
      f33_publish_redundant_u8
                ((uchar)uVar6,puStack_34 + uVar12,puStack_38 + uVar12,
                 f33_app_nvm_family1_status_xorAA + uVar12);
      uVar12 = 1;
    }
    (*((byte *)camry_host_ptr((uint32_t)(iVar4 + 0x4e86)))) = bStack_3a;
  }
  else {
    uVar12 = 0;
  }
  return uVar12;
}


