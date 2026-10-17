#include "common.h"


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



void FUN_00064986(void)

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
  FUN_000648ae();
  return;
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



/* Apply real task-rate increment/upper-bound guard to state8DB0 using ROM30DC0. Runs before the
   corresponding task body. */

void f33_record_ch0_dispatch(void)

{
  f33_record_supervised_task_dispatch(f33_task_rate_windows,f33_task_rate_policies);
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
    FUN_00062b90(0xd6d6d6d6);
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
      FUN_00062b90(0xc7c7c7c7);
                    /* WARNING: Subroutine does not return */
      f33_enter_terminal_hardware_sequence();
    }
    FUN_00065d6e();
  }
  return;
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
    FUN_00062b90(0xe3e3e3e3);
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



/* Single constant publisher: DAT_febe5f28 = 0; Shape-classified from the canonical corpus; the
   target cell is not yet named, so the written state's meaning is unknown. */

void FUN_0006681e(void)

{
  DAT_febe5f28 = 0;
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



void FUN_00066f68(void)

{
  f33_publish_redundant_u8('Z',((undefined *)camry_host_ptr(0xfebf0671u)),((undefined *)camry_host_ptr(0xfebf10a9u)),((undefined *)camry_host_ptr(0xfebf10cdu)));
  return;
}



void FUN_00066f84(void)

{
  f33_publish_redundant_u8('\0',((undefined *)camry_host_ptr(0xfebf0671u)),((undefined *)camry_host_ptr(0xfebf10a9u)),((undefined *)camry_host_ptr(0xfebf10cdu)));
  return;
}



void FUN_00066f9e(void)

{
  f33_publish_redundant_u8('Z',((undefined *)camry_host_ptr(0xfebf0672u)),((undefined *)camry_host_ptr(0xfebf10aau)),((undefined *)camry_host_ptr(0xfebf10ceu)));
  return;
}



void FUN_00066fba(void)

{
  f33_publish_redundant_u8('\0',((undefined *)camry_host_ptr(0xfebf0672u)),((undefined *)camry_host_ptr(0xfebf10aau)),((undefined *)camry_host_ptr(0xfebf10ceu)));
  return;
}



void FUN_00066fd4(void)

{
  f33_publish_redundant_u8
            ('\0', ((uchar *)camry_host_ptr((uint32_t)((0xfebf0670u)))), ((uchar *)camry_host_ptr((uint32_t)((0xfebf10a8u)))), ((uchar *)camry_host_ptr((uint32_t)((0xfebf10ccu)))));
  return;
}



/* Return full R10=0. Exact-image selector used through FF038: ready0701 request2 takes software
   foreground restart, not0800. */

uint f33_platform_restart_selector_constant_zero(void)

{
  return 0;
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



void FUN_00067346(void)

{
  f33_nvm_family0_scan_cursor = 0;
  f33_nvm_family0_probe_offset = 0;
  return;
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


