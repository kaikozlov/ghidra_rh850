#include "common.h"


/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_bc0f6(void)

{
  return;
}



/* Clear BDA8/BDA9 and seed entrycount4/releasecount1. */

void f33_reset_owner3_signal_qualification(void)

{
  DAT_febebda8 = 0;
  DAT_febebda9 = 0;
  DAT_febebdac = DAT_000af110;
  DAT_febebdae = DAT_000af112;
  return;
}



/* AdmitB1A7=5A,B20E0/33,B1BC0. Strict low<2125 withentryinhibit andcount4; release onlystrict>2176
   withcount1. Equality/holdbehaviorretained. */

void f33_qualify_owner3_shutdown_signal(void)

{
  if ((DAT_febeb1a7 == 'Z') &&
     (((DAT_febeb20e == '\0' || (DAT_febeb20e == '3')) && (DAT_febeb1bc == '\0')))) {
    DAT_febebda9 = 1;
    if (DAT_febebda8 < 2) {
      if (DAT_febebda8 == 0) {
        if ((DAT_febeb084 < DAT_000af114) && (DAT_febebdaa == '\0')) {
          if (DAT_febebdac == 0) {
            DAT_febebda8 = 1;
            DAT_febebda9 = 1;
            DAT_febebdae = DAT_000af112;
            return;
          }
          DAT_febebda9 = 1;
          DAT_febebdac = DAT_febebdac + -1;
          return;
        }
      }
      else {
        if (DAT_febeb084 <= DAT_000af116) {
          DAT_febebda9 = 1;
          DAT_febebdae = DAT_000af112;
          return;
        }
        if (DAT_febebdae != 0) {
          DAT_febebda9 = 1;
          DAT_febebdae = DAT_febebdae + -1;
          return;
        }
      }
      DAT_febebda8 = 0;
      DAT_febebdac = DAT_000af110;
    }
  }
  else {
    DAT_febebda8 = 0;
    DAT_febebda9 = 0;
    DAT_febebdac = DAT_000af110;
    DAT_febebdae = DAT_000af112;
  }
  return;
}



/* Store low8 entryinhibitBDAA; does not itself clearactivequalification. */

void f33_set_owner3_entry_inhibit(uint inhibit)

{
  DAT_febebdaa = (char)inhibit;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_bc19c(void)

{
  return;
}



/* Reset feedbackerrorstates/accumulators,nominalbase/request/minimum,entry2/release200/recovery2
   andactioncount520. ExternalBDB2 unchanged. */

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



/* WARNING: Removing unreachable block (ram,0x000bc49e) */
/* WARNING: Removing unreachable block (ram,0x000bc47a) */
/* WARNING: Removing unreachable block (ram,0x000bc430) */
/* WARNING: Removing unreachable block (ram,0x000bc41a) */
/* WARNING: Removing unreachable block (ram,0x000bc39c) */
/* WARNING: Removing unreachable block (ram,0x000bc35c) */
/* WARNING: Removing unreachable block (ram,0x000bc322) */
/* B1A7 andowner5activegate; delayed2304/3072 qualification ofEE20;
   retainedfast/slow/highpasssignedfilters,base/minimum feedbackandsteppedrelease. Publishowner2
   andaction9/class3 countdown. */

void f33_publish_owner2_deficit_limit_request(void)

{
  char cVar1;
  char cVar2;
  char cVar3;
  short sVar4;
  uint32_t puVar5;
  uint uVar6;
  int iVar7;
  short sVar8;
  int iVar9;
  short sVar10;
  short sVar11;
  int iVar12;
  short sVar13;
  short sVar14;
  int iVar15;
  int iVar16;
  char cStack_61;
  char cStack_60;
  short sStack_5e;
  short asStack_5c [2];
  short sStack_58;
  short sStack_56;
  int iStack_54;
  short sStack_50;
  short sStack_4e;
  int iStack_4c;
  int iStack_48;
  int iStack_44;
  short sStack_40;
  short sStack_3e;
  int iStack_3c;
  short sStack_38;
  short sStack_36;
  uint uStack_34;
  short sStack_30;
  short sStack_2e;
  
  iVar16 = DAT_febebdcc;
  sVar11 = DAT_febebdbe;
  cVar3 = DAT_febebdb0;
  cVar2 = DAT_febeb1d1;
  cVar1 = DAT_febeb1a7;
  puVar5 = 0xfebeb800u;
  sStack_36 = DAT_000af134;
  sStack_30 = DAT_febeaf80;
  sStack_2e = DAT_febeaf82;
  sStack_50 = DAT_febeafa4;
  cStack_61 = DAT_febebdb1;
  sStack_38 = DAT_000af132;
  iVar15 = (int)DAT_febebdbc;
  iStack_44 = DAT_febebdd8;
  uVar6 = (uint)DAT_febeee20;
  iVar9 = (int)DAT_febebdba;
  iStack_3c = DAT_febebdc8;
  iVar12 = (int)DAT_febebdb4;
  cStack_60 = DAT_febebdb0;
  sStack_4e = DAT_febebdc4;
  sVar13 = DAT_000af13e;
  sVar14 = DAT_000af140;
  if ((DAT_febeb1a7 == 'Z') && (DAT_febebcaa != 'Z')) {
    if ((uVar6 < DAT_000af11a) && (DAT_febebdb2 == '\0')) {
      if (DAT_febebdc0 == 0) {
        cStack_61 = '\x01';
        sVar13 = 0;
      }
      else {
        sVar13 = DAT_febebdc0 + -1;
      }
    }
    else if ((DAT_febebdb1 == '\x01') && (DAT_000af11c < uVar6)) {
      if (DAT_febebdc2 == 0) {
        cStack_61 = '\0';
        sVar14 = 0;
      }
      else {
        sVar14 = DAT_febebdc2 + -1;
      }
    }
    iVar7 = DAT_000af118 - uVar6;
    if (iVar7 + 0x7fff < 0 == (-1 < iVar7 && iVar7 + 0x7fff < 0) && iVar7 != -0x7fff) {
      if (iVar7 + -0x7fff < 0 == (iVar7 < 0 && -1 < iVar7 + -0x7fff) && iVar7 != 0x7fff) {
        iVar7 = 0x7fff;
      }
      sStack_3e = (short)iVar7;
    }
    else {
      sStack_3e = -0x7fff;
    }
    iStack_4c = (uint)DAT_000af138 * 10;
    if (iStack_4c - 1U < 0xffff) {
      iVar7 = DAT_febebdb6 * iStack_4c;
      iStack_4c = sStack_3e * iStack_4c;
    }
    else {
      iVar7 = (int)DAT_febebdb6 << 0x10;
      iStack_4c = (int)sStack_3e << 0x10;
    }
    iStack_4c = (DAT_febebdd0 - iVar7) + iStack_4c;
    iStack_54 = (uint)DAT_000af13a * 10;
    sVar10 = (short)(iStack_4c / 0x10000);
    uStack_34 = iStack_54 - 1;
    if (uStack_34 < 0xffff) {
      iVar7 = DAT_febebdb8 * iStack_54;
      iStack_48 = sStack_3e * iStack_54;
    }
    else {
      iVar7 = (int)DAT_febebdb8 << 0x10;
      iStack_48 = (int)sStack_3e << 0x10;
    }
    iStack_48 = (DAT_febebdd4 - iVar7) + iStack_48;
    sStack_40 = (short)(iStack_48 / 0x10000);
    puVar5 = 0xfebeb800u;
    FUN_000d2388((int)sStack_3e,(int)sStack_40,&sStack_5e);
    if (uStack_34 < 0xffff) {
      iVar9 = iVar9 * iStack_54;
      iVar7 = sStack_5e * iStack_54;
    }
    else {
      iVar9 = iVar9 << 0x10;
      iVar7 = (int)sStack_5e << 0x10;
    }
    iStack_44 = (iStack_44 - iVar9) + iVar7;
    sVar8 = (short)(iStack_44 / 0x10000);
    iVar9 = (int)sVar8;
    if (cStack_61 == '\x01') {
      if (cVar3 == '\0') {
        FUN_000d1178((int)sStack_2e,&sStack_58);
        FUN_000d1178((int)sStack_30,&sStack_56);
        iVar16 = (int)sStack_56;
        iVar15 = (int)sStack_58;
        cStack_60 = '\x01';
        if (iVar16 - iVar15 < 0 != (iVar16 < 0 != iVar15 < 0 && iVar15 < 0 == iVar16 - iVar15 < 0))
        {
          iVar15 = iVar16;
        }
        iVar16 = iVar15 << 0x10;
      }
      sVar11 = DAT_000af120;
      if (cVar2 != 'Z') {
        sVar11 = DAT_000af11e;
      }
      iVar12 = (int)sVar11;
      if (iVar15 - iVar12 < 0 == (iVar15 < 0 != iVar12 < 0 && iVar12 < 0 == iVar15 - iVar12 < 0) &&
          iVar15 != iVar12) {
        iVar7 = (uint)DAT_000af13c * 10;
        if (iVar7 - 1U < 0xffff) {
          iVar15 = iVar15 * iVar7;
          iVar12 = iVar12 * iVar7;
        }
        else {
          iVar15 = iVar15 << 0x10;
          iVar12 = iVar12 << 0x10;
        }
        iVar16 = (iVar16 - iVar15) + iVar12;
        iVar15 = (int)(short)(iVar16 / 0x10000);
      }
      iVar12 = 0;
      if (-1 < sVar10) {
        iVar12 = ((int)DAT_000af122 * (int)sVar10) / 8;
      }
      iVar7 = iVar15 - iVar12;
      if (iVar15 - iVar12 < 0) {
        iVar7 = 0;
      }
      if (iVar7 - iStack_3c < 0 !=
          (iVar7 < 0 != iStack_3c < 0 && iStack_3c < 0 == iVar7 - iStack_3c < 0)) {
        iStack_3c = iVar7;
      }
      if (sStack_3e < 0) {
        if (cVar2 == 'Z') {
          iVar12 = (int)DAT_000af12a;
        }
        else {
          iVar12 = (int)DAT_000af128;
        }
      }
      else if (cVar2 == 'Z') {
        iVar12 = (int)DAT_000af126;
      }
      else {
        iVar12 = (int)DAT_000af124;
      }
      iVar12 = (sStack_3e * iVar12) / 8;
      iVar7 = (int)DAT_000af12c;
      if (iVar9 - iVar7 < 0 == (iVar9 < 0 != iVar7 < 0 && iVar7 < 0 == iVar9 - iVar7 < 0)) {
        sVar11 = DAT_000af130;
        if (cVar2 != 'Z') {
          sVar11 = DAT_000af12e;
        }
        iVar9 = (iVar9 * sVar11) / 8;
      }
      else {
        iVar9 = 0;
      }
      iVar7 = iStack_3c - iVar12;
      if (iStack_3c - iVar12 < 0) {
        if ((iVar9 < 0) ||
           (iVar12 = (iVar7 + 0x7fffffff) - iVar9,
           iVar12 < 0 == (iVar7 + 0x7fffffff < 0 != iVar9 < 0 && iVar9 < 0 == iVar12 < 0)))
        goto LAB_000bc4da;
        iVar7 = -0x7fffffff;
      }
      else if ((iVar9 < 0) &&
              (iVar12 = -(0x7fffffff - iVar7),
              iVar12 - iVar9 < 0 == (iVar12 < 0 != iVar9 < 0 && iVar9 < 0 == iVar12 - iVar9 < 0) &&
              iVar12 != iVar9)) {
        iVar7 = 0x7fffffff;
      }
      else {
LAB_000bc4da:
        iVar7 = iVar7 - iVar9;
      }
      FUN_000d1cf6(iVar7,(int)sStack_38,(int)sStack_36,asStack_5c);
      iVar9 = (int)asStack_5c[0];
      sVar11 = DAT_000af144;
      goto LAB_000bc552;
    }
    iVar9 = (int)sStack_38;
    if (iVar12 - iVar9 < 0 != (iVar12 < 0 != iVar9 < 0 && iVar9 < 0 == iVar12 - iVar9 < 0)) {
      if (sVar11 == 0) {
        FUN_000d1cf6(DAT_000af136 + iVar12,(int)sStack_38,(int)sStack_36,asStack_5c);
        iVar9 = (int)asStack_5c[0];
        sVar11 = DAT_000af144;
      }
      else {
        sVar11 = sVar11 + -1;
        iVar9 = iVar12;
      }
    }
    iStack_3c = (int)sStack_38;
    iVar16 = iStack_3c << 0x10;
  }
  else {
    iStack_44 = 0;
    iStack_48 = 0;
    iStack_4c = 0;
    sStack_40 = 0;
    iVar16 = 0x569a0000;
    sVar10 = 0;
    iVar9 = 0x569a;
    cStack_61 = '\0';
    iStack_3c = 0x569a;
    sVar8 = 0;
    sVar11 = DAT_000af144;
  }
  cStack_60 = '\0';
  iVar15 = iStack_3c;
LAB_000bc552:
  FUN_000d1178((int)sStack_50,&sStack_50);
  iVar7 = (int)DAT_000af146;
  iVar12 = sStack_50 - iVar9;
  sVar4 = DAT_000af142;
  if ((iVar7 - iVar12 < 0 != (iVar7 < 0 != iVar12 < 0 && iVar12 < 0 == iVar7 - iVar12 < 0) ||
       iVar7 == iVar12) && (sVar4 = DAT_000af142, cVar1 == 'Z')) {
    if (sStack_4e == 0) {
      ((void)(9), thunk_FUN_000545de());
      ((void)(3), (void)(10), thunk_FUN_00051cf6());
      sVar4 = sStack_4e;
    }
    else {
      sVar4 = sStack_4e + -1;
    }
  }
  sStack_4e = sVar4;
  f33_set_current_limit_request(2,(ushort)iVar9);
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + 0x5ba)))) = sVar8;
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + 0x5c0)))) = sVar13;
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + 0x5c2)))) = sVar14;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(0x5b1))))) = cStack_61;
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + 0x5bc)))) = (short)iVar15;
  (*((int *)camry_host_ptr((uint32_t)(puVar5 + 0x5cc)))) = iVar16;
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + 0x5b6)))) = sVar10;
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + 0x5b8)))) = sStack_40;
  (*((int *)camry_host_ptr((uint32_t)(puVar5 + 0x5d0)))) = iStack_4c;
  (*((int *)camry_host_ptr((uint32_t)(puVar5 + 0x5d4)))) = iStack_48;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(0x5b0))))) = cStack_60;
  (*((int *)camry_host_ptr((uint32_t)(puVar5 + 0x5d8)))) = iStack_44;
  (*((int *)camry_host_ptr((uint32_t)(puVar5 + 0x5c8)))) = iStack_3c;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar5 + 0x5b4)))) = (ushort)iVar9;
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + 0x5be)))) = sVar11;
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + 0x5c4)))) = sStack_4e;
  return;
}



/* Store low8 entryinhibitBDB2; no implicitreset ofqualificationorrequest. */

void f33_set_owner2_entry_inhibit(uint inhibit)

{
  DAT_febebdb2 = (char)inhibit;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_bc5fa(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_bc5fc(void)

{
  return;
}



void FUN_000bc5fe(void)

{
  char cVar1;
  uint32_t puVar2;
  puVar2 = 0xfebeb800u;
  cVar1 = DAT_febebddc;
  if ((DAT_febebddc == '\0') &&
     ((((DAT_febebd9c == '\x01' || (DAT_febef38b == 'Z')) || (DAT_febebded == '\x01')) ||
      (DAT_febebde4 == '\x01')))) {
    puVar2 = 0xfebeb800u;
    ((void)(0), thunk_FUN_000545de());
    ((void)(5), (void)(10), thunk_FUN_00051cf6());
    cVar1 = 'Z';
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x5dc))))) = cVar1;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_bc646(void)

{
  return;
}



/* Constant-block fill: 8 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

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



void FUN_000bc65e(void)

{
  ushort uVar1;
  bool bVar2;
  undefined *puVar3;
  uint32_t puVar4;
  char cVar5;
  char cVar6;
  char cVar7;
  ushort uVar8;
  ushort uVar9;
  ushort uVar10;
  char cVar11;
  
  puVar4 = 0xfebeb800u;
  puVar3 = ((undefined *)camry_host_ptr(0xfebeb800u));
  if ((((((DAT_febeb065 != '\0') || (DAT_febef0b2 != '\0')) || (DAT_febeb1a7 != 'Z')) ||
       ((DAT_febeb20e != '\0' && (DAT_febeb20e != '3')))) ||
      ((DAT_febeb1bc == 'Z' || ((DAT_febeb084 < DAT_000af14a || (DAT_000af148 < DAT_febeb084))))))
     || (DAT_febeb30c == 0)) {
    cVar7 = '\0';
    cVar6 = '\0';
    cVar5 = '\0';
    bVar2 = false;
    cVar11 = '\0';
    uVar10 = 0;
    uVar9 = 0;
    uVar8 = 0;
    goto LAB_000bc7a4;
  }
  uVar10 = DAT_000af152;
  uVar1 = DAT_000af14e;
  if (DAT_febeb30c == -0x55aaaa56) {
    uVar10 = DAT_000af150;
    uVar1 = DAT_000af14c;
  }
  if (DAT_febebde3 == 'Z') {
    uVar9 = DAT_febebde8;
    if (DAT_febebde8 < DAT_000af156) {
      uVar9 = DAT_febebde8 + 1;
      goto LAB_000bc6ee;
    }
LAB_000bc6f4:
    cVar5 = 'Z';
  }
  else {
    uVar9 = 0;
LAB_000bc6ee:
    if (DAT_000af156 <= uVar9) goto LAB_000bc6f4;
    cVar5 = '\0';
  }
  cVar11 = '\0';
  uVar8 = DAT_febebdea;
  cVar7 = DAT_febebde0;
  cVar6 = cVar11;
  if (uVar1 < DAT_febeb084) {
    if ((uVar10 <= DAT_febeb084) || (cVar5 == 'Z')) {
      uVar8 = 0;
      cVar7 = cVar11;
    }
LAB_000bc724:
    if ((DAT_febebde1 != 'Z') || (cVar7 != '\0')) goto LAB_000bc712;
    uVar10 = DAT_febebde6;
    if (DAT_febebde6 <= DAT_000af154) {
      uVar10 = DAT_febebde6 + 1;
      goto LAB_000bc738;
    }
  }
  else {
    if ((DAT_febebdea < DAT_000af158) && (uVar8 = DAT_febebdea + 1, uVar8 < DAT_000af158))
    goto LAB_000bc724;
    cVar7 = 'Z';
LAB_000bc712:
    uVar10 = 0;
LAB_000bc738:
    if ((uVar10 <= DAT_000af154) && (cVar5 != 'Z')) {
      if (cVar7 == 'Z') {
        cVar6 = 'Z';
      }
      else {
        cVar6 = DAT_febebde1;
        if (DAT_febebde1 != 'Z') goto LAB_000bc762;
      }
      if (cVar5 == '\0') {
        cVar11 = cVar6;
      }
    }
  }
LAB_000bc762:
  puVar3 = ((undefined *)camry_host_ptr(0xfebeb800u));
  if (DAT_febebde3 == '\0') {
    if (cVar11 == 'Z') {
      ((void)(0xe), thunk_FUN_000545de());
      ((void)(4), (void)(0x32), thunk_FUN_00051cf6());
      puVar3 = ((undefined *)camry_host_ptr((uint32_t)(puVar4)));
    }
  }
  else if (cVar11 != 'Z') {
    puVar3 = ((undefined *)camry_host_ptr(0xfebeb800u));
    ((void)(0xe), thunk_FUN_00054724());
  }
  bVar2 = cVar11 == 'Z';
LAB_000bc7a4:
  puVar3[0x5e0] = cVar7;
  puVar3[0x5e1] = cVar6;
  puVar3[0x5e2] = cVar5;
  puVar3[0x5e3] = cVar11;
  *(ushort *)(puVar3 + 0x5e6) = uVar10;
  *(ushort *)(puVar3 + 0x5e8) = uVar9;
  *(ushort *)(puVar3 + 0x5ea) = uVar8;
  puVar3[0x5e4] = bVar2;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_bc7bc(void)

{
  return;
}



/* Constant-block fill: 5 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_bc7be(void)

{
  DAT_febebdec = 0;
  DAT_febebded = 0;
  DAT_febebdf0 = 0;
  DAT_febebdf2 = 0;
  DAT_febebdf4 = 0;
  return;
}



void FUN_000bc7ce(void)

{
  ushort uVar1;
  char cVar2;
  int iVar3;
  uint32_t puVar4;
  undefined *puVar5;
  int iVar6;
  undefined1 uVar7;
  int iVar8;
  char cVar9;
  ushort uVar10;
  ushort uVar11;
  ushort uVar12;
  short local_2c;
  short sStack_2a;
  
  uVar12 = DAT_febebdf4;
  uVar10 = DAT_febebdf2;
  cVar2 = DAT_febebdee;
  uVar1 = DAT_febeb084;
  puVar4 = 0xfebeb800u;
  puVar5 = ((undefined *)camry_host_ptr(0xfebeb800u));
  iVar8 = (int)DAT_febeb00a;
  uVar11 = DAT_febebdf0;
  cVar9 = DAT_febebded;
  if ((DAT_febeb1a7 == 'Z') && ((DAT_febeb20e == '\0' || (DAT_febeb20e == '3')))) {
    if (DAT_febeb1bc != 'Z') {
      iVar3 = (int)DAT_000af164;
      uVar7 = 1;
      puVar5 = ((undefined *)camry_host_ptr(0xfebeb800u));
      if ((iVar8 - iVar3 < 0 == (iVar8 < 0 != iVar3 < 0 && iVar3 < 0 == iVar8 - iVar3 < 0)) ||
         (DAT_febebee2 < DAT_000af15c)) {
        uVar11 = 0;
      }
      else if (DAT_febebded == '\0') {
        if (DAT_febebdf0 < DAT_000af15e) {
          uVar11 = DAT_febebdf0 + 1;
        }
        else {
          f33_report_diagnostic_event_failure(0x9a,100);
          ((void)(0xd), thunk_FUN_000545de());
          uVar11 = 0;
          puVar5 = ((undefined *)camry_host_ptr((uint32_t)(puVar4)));
          cVar9 = '\x01';
        }
      }
      FUN_000d1178((int)*(short *)(puVar5 + -0x820),&local_2c);
      FUN_000d1178((int)*(short *)(puVar5 + -0x824),&sStack_2a);
      if (uVar1 < DAT_000af16a) {
        iVar3 = (int)DAT_000af166;
        iVar6 = (int)local_2c;
        if (iVar6 - iVar3 < 0 == (iVar6 < 0 != iVar3 < 0 && iVar3 < 0 == iVar6 - iVar3 < 0) &&
            iVar6 != iVar3) goto LAB_000bc8b2;
        iVar3 = (int)DAT_000af16e;
        iVar6 = (int)sStack_2a;
        if ((iVar6 - iVar3 < 0 == (iVar6 < 0 != iVar3 < 0 && iVar3 < 0 == iVar6 - iVar3 < 0) &&
             iVar6 != iVar3) || (cVar2 != '\0')) goto LAB_000bc8b2;
        if (cVar9 == '\0') {
          if (uVar10 < DAT_000af160) {
            uVar10 = uVar10 + 1;
          }
          else {
            f33_report_diagnostic_event_failure(0x9a,100);
            cVar9 = '\x01';
            ((void)(0xd), thunk_FUN_000545de());
            uVar10 = 0;
          }
        }
      }
      else {
LAB_000bc8b2:
        uVar10 = 0;
      }
      if ((DAT_000af16c < uVar1) &&
         (iVar3 = (int)DAT_000af168,
         iVar8 - iVar3 < 0 == (iVar8 < 0 != iVar3 < 0 && iVar3 < 0 == iVar8 - iVar3 < 0))) {
        if (uVar12 < DAT_000af162) {
          uVar12 = uVar12 + 1;
        }
        else {
          f33_report_diagnostic_event_pass(0x9a);
          cVar9 = '\0';
        }
      }
      else {
        uVar12 = 0;
      }
      goto LAB_000bc928;
    }
LAB_000bc8e6:
    if ((DAT_000af16c < DAT_febeb084) &&
       (iVar3 = (int)DAT_000af168,
       iVar8 - iVar3 < 0 == (iVar8 < 0 != iVar3 < 0 && iVar3 < 0 == iVar8 - iVar3 < 0))) {
      if (DAT_000af162 <= DAT_febebdf4) {
        puVar5 = ((undefined *)camry_host_ptr(0xfebeb800u));
        f33_report_diagnostic_event_pass(0x9a);
        goto LAB_000bc924;
      }
      uVar12 = DAT_febebdf4 + 1;
    }
    else {
      uVar12 = 0;
    }
  }
  else {
    if (DAT_febeb1bc == 'Z') goto LAB_000bc8e6;
    puVar5 = ((undefined *)camry_host_ptr(0xfebeb800u));
    f33_report_diagnostic_event_pass(0x9a);
LAB_000bc924:
    uVar12 = 0;
    uVar11 = 0;
    uVar10 = 0;
    cVar9 = '\0';
  }
  uVar7 = 0;
LAB_000bc928:
  puVar5[0x5ec] = uVar7;
  puVar5[0x5ed] = cVar9;
  *(ushort *)(puVar5 + 0x5f0) = uVar11;
  *(ushort *)(puVar5 + 0x5f2) = uVar10;
  *(ushort *)(puVar5 + 0x5f4) = uVar12;
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



void FUN_000bc96a(void)

{
  if (((((((DAT_febeee03 == '\0') && (DAT_febeee04 == '\0')) && (DAT_febeee05 == '\0')) &&
        ((DAT_febeee06 == '\0' && (DAT_febeee07 == '\0')))) &&
       (((DAT_febeee08 == '\0' && ((DAT_febeee09 == '\0' && (DAT_febeee0a == '\0')))) &&
        (DAT_febeee0b == '\0')))) &&
      (((DAT_febeee0c == '\0' && (DAT_febeee0d == '\0')) &&
       ((DAT_febeb358 == '\0' || (DAT_febeb358 == '\x02')))))) && (DAT_febef394 == -0x5aa5a55b)) {
    DAT_febeac02 = 0;
  }
  else {
    DAT_febeac02 = 0x5a;
  }
  DAT_febeac04 = DAT_febeee02 == 'Z';
  return;
}



/* Invoke D1272(AF8C,45,4,&result) and publish result atAC18. The later C32AA negate is a separate
   update; no physical-source identity is inferred from this scaling. Scale sourceAF8C viaD1272
   with45/4 intoAC18; physical source and units are not inferred from the ratio. */

void f33_scale_observer_source_term(void)

{
  uint32_t puVar1;
  undefined4 local_8;
  
  puVar1 = 0xfebeb800u;
  FUN_000d1272(DAT_febeaf8c,0x2d,4,&local_8);
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0xbe8)))) = local_8;
  return;
}



void FUN_000bca08(void)

{
  DAT_febeac14 = DAT_febeaf88;
  DAT_febeac00 = DAT_febeb20e;
  DAT_febeac0c = DAT_febeee1e;
  DAT_febeac03 = DAT_febeb1a7;
  DAT_febeac0e = DAT_febeafbc;
  DAT_febeac06 = DAT_febeee12;
  DAT_febeac10 = DAT_febeafa8;
  DAT_febeac07 = f33_record8_confirmation_complete;
  DAT_febeac12 = DAT_febeb138;
  DAT_febeac20 = DAT_febebed4;
  DAT_febeac0a = DAT_febeb1ce;
  DAT_febeac0b = DAT_febeee14;
  DAT_febeac24 = DAT_febeaf8c;
  return;
}



/* Sequential initializer chain: 5 unconditional calls and no other statements; shape-verified. The
   called sequence is the function's entire behavior; chain family members differ in callee sets. */

void f33_run_init_chain_bca62(void)

{
  FUN_000bc958();
  FUN_000bc96a();
  f33_scale_observer_source_term();
  FUN_000bca08();
  FUN_000d1118();
  return;
}



void FUN_000bca7e(undefined1 param_1)

{
  ((void)(param_1), (void)(10), thunk_FUN_00051cf6());
  return;
}



/* WARNING: Removing unreachable block (ram,0x000bcb34) */

void FUN_000bcaa6(void)

{
  char cVar1;
  undefined1 uVar2;
  ushort uVar3;
  char cVar4;
  char cVar5;
  char cVar6;
  uint uVar7;
  uint32_t puVar8;
  undefined1 uVar9;
  undefined1 uVar10;
  undefined1 uVar11;
  undefined2 uVar12;
  undefined2 uStack_34;
  undefined2 uStack_32;
  undefined4 uStack_30;
  
  cVar5 = DAT_febebe20;
  cVar4 = DAT_febebe1c;
  puVar8 = 0xfebeb800u;
  FUN_000d1232((int)DAT_febeaf56,0x168,0x80,&uStack_34);
  uVar7 = (*((uint *)camry_host_ptr((uint32_t)(puVar8 + 0x3790))));
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar8 + (uint32_t)(0x3500))))) == 'Z') {
    uVar9 = 0x5a;
  }
  else {
    uVar9 = 0;
  }
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar8 + (uint32_t)(0x3781)))));
  uVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar8 + (uint32_t)(0x3b02)))));
  cVar6 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar8 + (uint32_t)(0x3b00)))));
  if ((cVar6 != '\0') && (cVar6 != '\x02')) {
    if (cVar6 == '\x03') {
      cVar6 = '\x04';
    }
    else {
      cVar6 = '\x01';
    }
  }
  uVar3 = (*((ushort *)camry_host_ptr((uint32_t)(puVar8 + 0x3788))));
  if ((uVar3 & 3) == 0) {
    uVar12 = (undefined2)(((int)(*((short *)camry_host_ptr((uint32_t)(puVar8 + -0x8b0)))) + (int)(*((short *)camry_host_ptr((uint32_t)(puVar8 + -0x8ae))))) / 2)
    ;
  }
  else if ((uVar3 & 1) == 0) {
    uVar12 = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar8 + -0x8b0))));
  }
  else {
    uVar12 = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar8 + -0x8ae))));
  }
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar8 + (uint32_t)(-0x8b3))))) == 'Z') || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar8 + (uint32_t)(-0x8b2))))) == 'Z')) {
    uVar11 = 0x5a;
  }
  else {
    uVar11 = 0;
  }
  FUN_000d1232((int)(*((short *)camry_host_ptr((uint32_t)(puVar8 + 0x3b06)))),0x100,100,&uStack_32);
  if ((cVar5 == 'Z') || (cVar4 == 'Z')) {
    uVar10 = 0x5a;
  }
  else {
    uVar10 = 0;
  }
  FUN_000d1272((*((undefined4 *)camry_host_ptr((uint32_t)(puVar8 + -0x8a0)))),0x2d,0x200,&uStack_30);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar8 + (uint32_t)(-0xbca))))) = uVar10;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar8 + (uint32_t)(-0xbd7))))) = (uVar7 & 0x70017001) != 0x70017001;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar8 + (uint32_t)(-0xbd6))))) = (uVar7 & 0x40004) != 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar8 + -0xbbe)))) = uStack_34;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar8 + (uint32_t)(-0xbcf))))) = uVar9;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar8 + (uint32_t)(-0xbd8))))) = cVar1 == 'Z';
  (*((ushort *)camry_host_ptr((uint32_t)(puVar8 + -0xbb0)))) = uVar3;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar8 + -3000)))) = uVar12;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar8 + (uint32_t)(-0xbcc))))) = uVar2;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar8 + (uint32_t)(-0xbcd))))) = cVar6;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar8 + (uint32_t)(-0xbcb))))) = uVar11;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar8 + -0xb84)))) = uStack_32;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar8 + -0xb48)))) = uStack_30;
  return;
}



void FUN_000bcbd8(void)

{
  DAT_febeac88 = DAT_febeaf60;
  DAT_febeac8c = DAT_febeaf6c;
  DAT_febeacac = DAT_febeaf68;
  DAT_febeac44 = DAT_febeed04;
  DAT_febeac4a = DAT_febebee2;
  DAT_febeac46 = DAT_febeaf58;
  DAT_febeac4c = DAT_febeaf40;
  DAT_febeac4e = (ushort)DAT_febeb24d;
  DAT_febeac66 = (ushort)DAT_febeb24e;
  DAT_febeac2b = DAT_febeb112;
  DAT_febeac2c = DAT_febeb113;
  DAT_febeac40 = DAT_febeb116;
  DAT_febeac90 = DAT_febeaf64;
  DAT_febeac2e = DAT_febeb1ce;
  DAT_febeac5a = DAT_febeb1f8;
  DAT_febeac94 = DAT_febef30c;
  DAT_febeac98 = DAT_febef308;
  DAT_febeac9c = DAT_febef314;
  DAT_febeaca0 = DAT_febef318;
  DAT_febeaca4 = DAT_febef310;
  DAT_febeaca8 = DAT_febef31c;
  DAT_febeac2f = DAT_febeb121;
  DAT_febeac30 = DAT_febebef0;
  DAT_febeac5c = DAT_febeb138;
  DAT_febeac5e = DAT_febeb13a;
  DAT_febeac60 = DAT_febeb13c;
  DAT_febeac62 = DAT_febeb13e;
  DAT_febeac64 = DAT_febeb140;
  DAT_febeac6a = DAT_febebcf0;
  DAT_febeacb0 = DAT_febebed4;
  DAT_febeac72 = DAT_febebede;
  DAT_febeac32 = DAT_febef301;
  DAT_febeac74 = DAT_febef304;
  DAT_febeac52 = DAT_febeef8e;
  DAT_febeac3b = DAT_febebe23;
  DAT_febeac6e = DAT_febebd80;
  DAT_febeac6c = DAT_febebd82;
  DAT_febeacb4 = DAT_febeaf70;
  DAT_febeac3a = DAT_febebe22;
  DAT_febeac37 = DAT_febeef80;
  DAT_febeac3c = DAT_febeb354;
  DAT_febeac3d = DAT_febeac02;
  DAT_febeac80 = DAT_febeed12;
  DAT_febeac82 = DAT_febeaf42;
  DAT_febeac41 = DAT_febeb3fd;
  DAT_febeac84 = DAT_febeb400;
  return;
}



void FUN_000bcd02(void)

{
  FUN_000bcaa6();
  FUN_000bcbd8();
  FUN_000d1100();
  return;
}



void FUN_000bcd22(void)

{
  DAT_febead5b = DAT_febef06a;
  f33_run_init_chain_d0ce8();
  return;
}



void FUN_000bd86e(undefined1 param_1)

{
  DAT_febeacec = param_1;
  FUN_000d1160();
  return;
}



undefined4 FUN_000bd87e(void)

{
  uint32_t puVar1;
  undefined4 local_c;
  undefined2 uStack_8;
  undefined1 uStack_6;
  undefined1 uStack_5;
  
  puVar1 = 0xfebeb800u;
  if (DAT_febeacee != '\0') {
    FUN_000d1154();
    local_c = (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x8fc))));
    uStack_5 = 0;
    uStack_8 = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x9f2))));
    uStack_6 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xb14)))));
    FUN_000ff09c(8,&local_c);
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xb15))))) = 0x5a;
  }
  return 1;
}



undefined4 FUN_000bd8ba(void)

{
  undefined4 local_c;
  undefined2 uStack_8;
  undefined1 uStack_6;
  undefined1 uStack_5;
  
  if (DAT_febeacee != '\0') {
    DAT_febeacec = 0;
    uStack_6 = 0;
    uStack_5 = 0;
    local_c = DAT_febeaf04;
    uStack_8 = DAT_febeae0e;
    FUN_000ff09c(8,&local_c);
  }
  return 1;
}



undefined4 FUN_000bd8ea(void)

{
  uint32_t puVar1;
  undefined1 local_2c;
  undefined1 uStack_2b;
  undefined1 uStack_2a;
  undefined1 uStack_29;
  undefined1 uStack_28;
  undefined1 uStack_27;
  undefined1 uStack_26;
  undefined1 uStack_25;
  undefined1 uStack_24;
  undefined1 uStack_23;
  undefined1 uStack_22;
  undefined1 uStack_21;
  undefined1 uStack_20;
  undefined1 uStack_1f;
  undefined1 uStack_1e;
  undefined1 uStack_1d;
  undefined1 uStack_1c;
  undefined1 uStack_1b;
  undefined1 uStack_1a;
  undefined1 uStack_19;
  undefined2 uStack_18;
  undefined2 uStack_16;
  undefined1 uStack_14;
  undefined1 uStack_13;
  undefined1 uStack_12;
  undefined1 uStack_11;
  undefined1 uStack_10;
  undefined1 uStack_f;
  undefined1 uStack_e;
  undefined1 uStack_d;
  undefined1 uStack_c;
  undefined1 uStack_b;
  undefined1 uStack_a;
  undefined1 uStack_9;
  undefined1 uStack_8;
  undefined1 uStack_7;
  undefined1 uStack_6;
  undefined1 uStack_5;
  
  puVar1 = 0xfebeb800u;
  thunk_FUN_000d0d6c();
  uStack_28 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xb0b)))));
  uStack_29 = 0;
  uStack_d = 0;
  local_2c = (undefined1)(*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x9f0))));
  uStack_2b = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xb11)))));
  uStack_5 = 0;
  uStack_27 = (undefined1)(*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x9ec))));
  uStack_26 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xb0e)))));
  uStack_2a = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xb10)))));
  uStack_25 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xb0d)))));
  uStack_24 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xb0c)))));
  uStack_23 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xb00)))));
  uStack_22 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xaff)))));
  uStack_21 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xafe)))));
  uStack_18 = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x9ea))));
  uStack_20 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xaf6)))));
  uStack_1f = (undefined1)(*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x9d4))));
  uStack_1e = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xaf4)))));
  uStack_1d = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xaf3)))));
  uStack_1c = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xaf2)))));
  uStack_1b = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xaf1)))));
  uStack_1a = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xaf0)))));
  uStack_19 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xaef)))));
  uStack_16 = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x9ca))));
  uStack_14 = (undefined1)(*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x996))));
  uStack_13 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xa9e)))));
  uStack_12 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xa9d)))));
  uStack_11 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xa9f)))));
  uStack_10 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xa9b)))));
  uStack_f = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xa9a)))));
  uStack_e = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xa9c)))));
  uStack_c = (undefined1)(*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x994))));
  uStack_b = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xa97)))));
  uStack_a = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xa96)))));
  uStack_9 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xa98)))));
  uStack_8 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xa94)))));
  uStack_7 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xa93)))));
  uStack_6 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xa95)))));
  FUN_000ff09c(9,&local_2c);
  return 1;
}



void FUN_000bdb48(void)

{
  thunk_FUN_000d10e4();
  FUN_000bd8ea();
  return;
}



/* f33_report_diagnostic_event_failure(param_1 & 0xffff,0x32); whole-body shape-verified. The
   literal is the encoded diagnostic event, not a recovered OEM name. */

void f33_report_diagnostic_event_failure_ffff_32_bdb64(uint param_1)

{
  f33_report_diagnostic_event_failure(param_1 & 0xffff,0x32);
  return;
}



/* Narrow selector to low8 and forward through the real49E98 thunk. Preserve the returned byte; the
   former void inference lost consequential estimator/supervisor dataflow. Narrow selector and
   forward through real49E98 thunk, retaining actual returned byte consumed by estimator and
   target-supervisor paths. */

uchar f33_get_application_grouped_status(uint selector)

{
  uchar uVar1;
  
  uVar1 = f33_get_grouped_status_byte(selector & 0xff);
  return uVar1;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_bdb84(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_bdb86(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_bdb88(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_bdb8a(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_bdb8c(void)

{
  return;
}



/* Single constant publisher: DAT_febebe1c = 0; Shape-classified from the canonical corpus; the
   target cell is not yet named, so the written state's meaning is unknown. */

void FUN_000bdb8e(void)

{
  DAT_febebe1c = 0;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_bdb94(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_bdb96(void)

{
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



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_bdba6(void)

{
  return;
}



/* Constant-block fill: 8 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

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



void FUN_000bdbbe(void)

{
  undefined2 local_c;
  undefined2 uStack_a;
  undefined4 uStack_8;
  
  local_c = DAT_febebe28;
  uStack_8 = 0;
  uStack_a = DAT_febebe2a;
  FUN_000ff09c(0xb,&local_c);
  return;
}



void FUN_000bdbe0(void)

{
  ushort uVar1;
  uint32_t puVar2;
  char cVar3;
  char cVar4;
  char cVar5;
  ushort uVar6;
  ushort uVar7;
  ushort uVar8;
  
  uVar6 = DAT_febebe30;
  uVar7 = DAT_febebe2e;
  uVar8 = DAT_febebe2c;
  cVar3 = DAT_febebe26;
  cVar4 = DAT_febebe25;
  cVar5 = DAT_febebe24;
  puVar2 = 0xfebeb800u;
  uVar1 = DAT_febeb11a & 0xff00;
  if (DAT_febeb20e == '\0') {
    if ((uVar1 == 0x100) || (uVar1 == 0x200)) {
      if (((DAT_000af0f4 < DAT_febebe2c) || (uVar8 = DAT_febebe2c + 1, DAT_000af0f4 < uVar8)) &&
         (DAT_febebe24 != 'Z')) {
        DAT_febebe28 = DAT_febeb11a;
        DAT_febebe2a = DAT_febeb080;
        puVar2 = 0xfebeb800u;
        FUN_000bdbbe();
        cVar5 = 'Z';
      }
      goto LAB_000bdca4;
    }
  }
  else {
    if (DAT_febeb20e != '\x11') {
      if ((DAT_febeb20e == '\"') &&
         (((DAT_000af0f8 < DAT_febebe30 || (uVar6 = DAT_febebe30 + 1, DAT_000af0f8 < uVar6)) &&
          (DAT_febebe26 != 'Z')))) {
        DAT_febebe28 = DAT_febeb11a;
        DAT_febebe2a = DAT_febeb080;
        puVar2 = 0xfebeb800u;
        FUN_000bdbbe();
        cVar3 = 'Z';
      }
      goto LAB_000bdca4;
    }
    if (uVar1 != 0x700) {
      if (((DAT_000af0f6 < DAT_febebe2e) || (uVar7 = DAT_febebe2e + 1, DAT_000af0f6 < uVar7)) &&
         (DAT_febebe25 != 'Z')) {
        DAT_febebe28 = DAT_febeb11a;
        DAT_febebe2a = DAT_febeb080;
        puVar2 = 0xfebeb800u;
        FUN_000bdbbe();
        cVar4 = 'Z';
      }
      goto LAB_000bdca4;
    }
  }
  uVar8 = 0;
  uVar7 = 0;
  uVar6 = 0;
LAB_000bdca4:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x624))))) = cVar5;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x625))))) = cVar4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x626))))) = cVar3;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0x62c)))) = uVar8;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0x62e)))) = uVar7;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0x630)))) = uVar6;
  return;
}



void FUN_000bdcfe(void)

{
  undefined2 local_c;
  undefined2 uStack_a;
  undefined4 uStack_8;
  
  DAT_febebe28 = 0;
  DAT_febebe2a = 0;
  local_c = 0;
  uStack_a = 0;
  uStack_8 = 0;
  FUN_000ff09c(0xb,&local_c);
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_bdd20(void)

{
  return;
}



void FUN_000bddba(void)

{
  undefined1 local_1c;
  undefined1 uStack_1b;
  undefined2 uStack_1a;
  undefined4 uStack_18;
  undefined2 uStack_14;
  undefined2 uStack_12;
  undefined1 uStack_10;
  undefined1 uStack_f;
  undefined2 uStack_e;
  undefined4 uStack_c;
  undefined2 uStack_8;
  undefined2 uStack_6;
  
  local_1c = DAT_febebe36;
  uStack_1b = DAT_febebe34;
  uStack_1a = DAT_febebe42;
  uStack_18 = DAT_febebe4c;
  uStack_14 = DAT_febebe3a;
  uStack_12 = DAT_febebe3e;
  uStack_10 = DAT_febebe37;
  uStack_f = DAT_febebe35;
  uStack_e = DAT_febebe44;
  uStack_c = DAT_febebe50;
  uStack_8 = DAT_febebe3c;
  uStack_6 = DAT_febebe40;
  FUN_000ff09c(0xf,&local_1c);
  return;
}



void FUN_000bde16(void)

{
  char cVar1;
  char cVar2;
  ushort uVar3;
  ushort uVar4;
  
  uVar3 = DAT_febebe48;
  uVar4 = DAT_febebe46;
  cVar2 = DAT_febebe39;
  cVar1 = DAT_febebe38;
  if (DAT_febeb20e == '\0') {
    if (((DAT_febeb11a & 0xff00) != 0x100) && ((DAT_febeb11a & 0xff00) != 0x200)) {
      DAT_febebe48 = 0;
      return;
    }
  }
  else {
    if (DAT_febeb20e == '\x11') {
      if (DAT_febeb1d3 != 'Z') {
        DAT_febebe46 = 0;
        return;
      }
      if ((DAT_febeb072 != '\x02') && (DAT_febeb074 != '\x02')) {
        DAT_febebe46 = 0;
        return;
      }
      if (DAT_febeb202 <= DAT_000aef84) {
        DAT_febebe46 = 0;
        return;
      }
      if (DAT_febeb1d2 != '\x11') {
        DAT_febebe46 = 0;
        return;
      }
      if (DAT_febebe48 < DAT_000aef82) {
        DAT_febebe46 = 0;
        DAT_febebe48 = DAT_febebe48 + 1;
        return;
      }
      if (DAT_febebe39 == 'Z') {
        DAT_febebe46 = 0;
        return;
      }
      if (((int8_t)DAT_febebe37) != -1) {
        DAT_febebe37 = DAT_febebe37 + '\x01';
      }
      DAT_febebe3c = DAT_febeb11a;
      DAT_febebe35 = DAT_febebe60;
      DAT_febebe44 = f33_received_retained_word;
      DAT_febebe50 = f33_received_word_unchanged_age;
      DAT_febebe40 = DAT_febeb080;
      FUN_000bddba();
      DAT_febebe38 = cVar1;
      DAT_febebe39 = 0x5a;
      DAT_febebe46 = 0;
      DAT_febebe48 = uVar3;
      return;
    }
    if (DAT_febeb20e != '\"') {
      DAT_febebe38 = 0;
      DAT_febebe46 = 0;
      DAT_febebe48 = 0;
      return;
    }
  }
  if (DAT_febebe46 < DAT_000aef80) {
    uVar4 = DAT_febebe46 + 1;
  }
  else if (DAT_febebe38 != 'Z') {
    if (((int8_t)DAT_febebe36) != -1) {
      DAT_febebe36 = DAT_febebe36 + '\x01';
    }
    DAT_febebe3a = DAT_febeb11a;
    DAT_febebe34 = DAT_febebe60;
    DAT_febebe42 = f33_received_retained_word;
    DAT_febebe4c = f33_received_word_unchanged_age;
    DAT_febebe3e = DAT_febeb080;
    FUN_000bddba();
    DAT_febebe38 = 'Z';
  }
  DAT_febebe39 = cVar2;
  DAT_febebe46 = uVar4;
  DAT_febebe48 = 0;
  return;
}



void FUN_000bdf24(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  undefined1 local_1c;
  undefined1 uStack_1b;
  undefined2 uStack_1a;
  undefined4 uStack_18;
  undefined2 uStack_14;
  undefined2 uStack_12;
  undefined1 uStack_10;
  undefined1 uStack_f;
  undefined2 uStack_e;
  undefined4 uStack_c;
  undefined2 uStack_8;
  undefined2 uStack_6;
  
  iVar3 = 0;
  do {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebebe34u + (uint32_t)(iVar3) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebebe36u + (uint32_t)(iVar3) * 1u)))) = 0;
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebebe42u + (uint32_t)(iVar3) * 2u)))) = 0;
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebebe3eu + (uint32_t)(iVar3) * 2u)))) = 0;
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebebe3au + (uint32_t)(iVar3) * 2u)))) = 0;
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebebe4cu + (uint32_t)(iVar3) * 4u)))) = 0;
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -1;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  local_1c = 0;
  uStack_1b = 0;
  uStack_1a = 0;
  uStack_18 = 0;
  uStack_14 = 0;
  uStack_12 = 0;
  uStack_10 = 0;
  uStack_f = 0;
  uStack_e = 0;
  uStack_c = 0;
  uStack_8 = 0;
  uStack_6 = 0;
  FUN_000ff09c(0xf,&local_1c);
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_bdf7e(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_bdf80(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_bdf82(void)

{
  return;
}



/* Forward real R6 output pointer to profile4/10/default snapshot. Each writes56 bytes; the output
   buffer is not an unused integer argument. Profile4/10/default dispatch preserves real R6 output
   pointer to56-byte application snapshot, repaired by formal pointer signatures. */

void f33_snapshot_diagnostic_application(F33DiagnosticApplicationSample *output,ushort capture_kind)

{
  if (capture_kind == 4) {
    f33_snapshot_diagnostic_application_kind4(output);
  }
  else if (capture_kind == 10) {
    f33_snapshot_diagnostic_application_kind10(output);
  }
  else {
    f33_snapshot_diagnostic_application_default(output);
  }
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_bdfa6(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_bdfa8(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_bdfaa(void)

{
  return;
}



/* 56-byte staged application projection; signedAF40 supplies limit and positive flag, AFA4 supplies
   selected sample. Trailing padding is explicitly zeroed. Kind10 software projection writes56 bytes
   including explicit zero padding; signedAF40 and its positive predicate plus AFA4 sample. No
   hardware read. */

void f33_snapshot_diagnostic_application_kind10(F33DiagnosticApplicationSample *output)

{
  uchar uVar1;
  undefined2 uVar2;
  undefined2 uVar3;
  short sVar4;
  ushort uVar5;
  uint uVar6;
  
  output->raw[0] = DAT_febebe78;
  *(undefined2 *)(output->raw + 10) = DAT_febebee2;
  *(undefined2 *)(output->raw + 0xc) = DAT_febebe82;
  sVar4 = DAT_febeaf40;
  *(short *)(output->raw + 0x18) = DAT_febeaf40;
  uVar2 = DAT_febeb11a;
  output->raw[1] = 0 < sVar4;
  uVar3 = DAT_febeae6e;
  uVar1 = DAT_febeacf1;
  *(undefined2 *)(output->raw + 0xe) = uVar2;
  output->raw[2] = uVar1;
  uVar2 = DAT_febeae12;
  *(undefined2 *)(output->raw + 0x14) = uVar3;
  *(undefined2 *)(output->raw + 0x12) = uVar2;
  output->raw[3] = DAT_febeacf5;
  output->raw[4] = DAT_febead0a;
  *(undefined2 *)(output->raw + 0x16) = DAT_febeae36;
  output->raw[5] = DAT_febeb1c4;
  *(undefined2 *)(output->raw + 0x1a) = DAT_febeafa4;
  uVar5 = f33_received_retained_word;
  *(undefined2 *)(output->raw + 0x1c) = uVar3;
  *(undefined2 *)(output->raw + 0x1e) = uVar3;
  *(ushort *)(output->raw + 0x10) = uVar5;
  *(uint *)(output->raw + 0x20) = f33_received_word_unchanged_age;
  output->raw[6] = DAT_febebe60;
  output->raw[7] = DAT_febebe62;
  uVar6 = f33_received_typed_scalar;
  output->raw[0x34] = '\0';
  output->raw[0x35] = '\0';
  output->raw[0x36] = '\0';
  output->raw[0x37] = '\0';
  *(uint *)(output->raw + 0x24) = uVar6;
  output->raw[0x28] = f33_received_packed_decimal_fields[0];
  output->raw[0x29] = f33_received_packed_decimal_fields[1];
  output->raw[0x2a] = f33_received_packed_decimal_fields[2];
  output->raw[0x2b] = f33_received_packed_decimal_fields[3];
  output->raw[0x2c] = f33_received_packed_decimal_fields[4];
  output->raw[0x2d] = f33_received_packed_decimal_fields[5];
  output->raw[8] = DAT_febead60;
  output->raw[9] = DAT_febead67;
  uVar1 = DAT_febead39;
  output->raw[0x31] = '\0';
  output->raw[0x30] = uVar1;
  uVar2 = DAT_febeae58;
  output->raw[0x32] = '\0';
  output->raw[0x33] = '\0';
  *(undefined2 *)(output->raw + 0x2e) = uVar2;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_be06a(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_be06c(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_be06e(void)

{
  return;
}



/* Same application layout as kind10 but selected sample comes fromAC56. Kind4 application layout
   usesAF40 positive/limit andAC56 selected sample. */

void f33_snapshot_diagnostic_application_kind4(F33DiagnosticApplicationSample *output)

{
  uchar uVar1;
  undefined2 uVar2;
  undefined2 uVar3;
  short sVar4;
  ushort uVar5;
  uint uVar6;
  
  output->raw[0] = DAT_febebe78;
  *(undefined2 *)(output->raw + 10) = DAT_febebee2;
  *(undefined2 *)(output->raw + 0xc) = DAT_febebe82;
  sVar4 = DAT_febeaf40;
  *(short *)(output->raw + 0x18) = DAT_febeaf40;
  uVar2 = DAT_febeb11a;
  output->raw[1] = 0 < sVar4;
  uVar3 = DAT_febeae6e;
  uVar1 = DAT_febeacf1;
  *(undefined2 *)(output->raw + 0xe) = uVar2;
  output->raw[2] = uVar1;
  uVar2 = DAT_febeae12;
  *(undefined2 *)(output->raw + 0x14) = uVar3;
  *(undefined2 *)(output->raw + 0x12) = uVar2;
  output->raw[3] = DAT_febeacf5;
  output->raw[4] = DAT_febead0a;
  *(undefined2 *)(output->raw + 0x16) = DAT_febeae36;
  output->raw[5] = DAT_febeb1c4;
  *(undefined2 *)(output->raw + 0x1a) = DAT_febeac56;
  uVar5 = f33_received_retained_word;
  *(undefined2 *)(output->raw + 0x1c) = uVar3;
  *(undefined2 *)(output->raw + 0x1e) = uVar3;
  *(ushort *)(output->raw + 0x10) = uVar5;
  *(uint *)(output->raw + 0x20) = f33_received_word_unchanged_age;
  output->raw[6] = DAT_febebe60;
  output->raw[7] = DAT_febebe62;
  uVar6 = f33_received_typed_scalar;
  output->raw[0x34] = '\0';
  output->raw[0x35] = '\0';
  output->raw[0x36] = '\0';
  output->raw[0x37] = '\0';
  *(uint *)(output->raw + 0x24) = uVar6;
  output->raw[0x28] = f33_received_packed_decimal_fields[0];
  output->raw[0x29] = f33_received_packed_decimal_fields[1];
  output->raw[0x2a] = f33_received_packed_decimal_fields[2];
  output->raw[0x2b] = f33_received_packed_decimal_fields[3];
  output->raw[0x2c] = f33_received_packed_decimal_fields[4];
  output->raw[0x2d] = f33_received_packed_decimal_fields[5];
  output->raw[8] = DAT_febead60;
  output->raw[9] = DAT_febead67;
  uVar1 = DAT_febead39;
  output->raw[0x31] = '\0';
  output->raw[0x30] = uVar1;
  uVar2 = DAT_febeae58;
  output->raw[0x32] = '\0';
  output->raw[0x33] = '\0';
  *(undefined2 *)(output->raw + 0x2e) = uVar2;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_be12e(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_be130(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_be132(void)

{
  return;
}



/* Same application layout with signedAFD0 limit/positive flag and B02C sample. Default application
   layout substitutesAFD0 positive/limit andB02C selected sample. */

void f33_snapshot_diagnostic_application_default(F33DiagnosticApplicationSample *output)

{
  uchar uVar1;
  undefined2 uVar2;
  undefined2 uVar3;
  short sVar4;
  ushort uVar5;
  uint uVar6;
  
  output->raw[0] = DAT_febebe78;
  *(undefined2 *)(output->raw + 10) = DAT_febebee2;
  *(undefined2 *)(output->raw + 0xc) = DAT_febebe82;
  sVar4 = DAT_febeafd0;
  *(short *)(output->raw + 0x18) = DAT_febeafd0;
  uVar2 = DAT_febeb11a;
  output->raw[1] = 0 < sVar4;
  uVar3 = DAT_febeae6e;
  uVar1 = DAT_febeacf1;
  *(undefined2 *)(output->raw + 0xe) = uVar2;
  output->raw[2] = uVar1;
  uVar2 = DAT_febeae12;
  *(undefined2 *)(output->raw + 0x14) = uVar3;
  *(undefined2 *)(output->raw + 0x12) = uVar2;
  output->raw[3] = DAT_febeacf5;
  output->raw[4] = DAT_febead0a;
  *(undefined2 *)(output->raw + 0x16) = DAT_febeae36;
  output->raw[5] = DAT_febeb1c4;
  *(undefined2 *)(output->raw + 0x1a) = DAT_febeb02c;
  uVar5 = f33_received_retained_word;
  *(undefined2 *)(output->raw + 0x1c) = uVar3;
  *(undefined2 *)(output->raw + 0x1e) = uVar3;
  *(ushort *)(output->raw + 0x10) = uVar5;
  *(uint *)(output->raw + 0x20) = f33_received_word_unchanged_age;
  output->raw[6] = DAT_febebe60;
  output->raw[7] = DAT_febebe62;
  uVar6 = f33_received_typed_scalar;
  output->raw[0x34] = '\0';
  output->raw[0x35] = '\0';
  output->raw[0x36] = '\0';
  output->raw[0x37] = '\0';
  *(uint *)(output->raw + 0x24) = uVar6;
  output->raw[0x28] = f33_received_packed_decimal_fields[0];
  output->raw[0x29] = f33_received_packed_decimal_fields[1];
  output->raw[0x2a] = f33_received_packed_decimal_fields[2];
  output->raw[0x2b] = f33_received_packed_decimal_fields[3];
  output->raw[0x2c] = f33_received_packed_decimal_fields[4];
  output->raw[0x2d] = f33_received_packed_decimal_fields[5];
  output->raw[8] = DAT_febead60;
  output->raw[9] = DAT_febead67;
  uVar1 = DAT_febead39;
  output->raw[0x31] = '\0';
  output->raw[0x30] = uVar1;
  uVar2 = DAT_febeae58;
  output->raw[0x32] = '\0';
  output->raw[0x33] = '\0';
  *(undefined2 *)(output->raw + 0x2e) = uVar2;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_be1f2(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_be1f4(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_be1f6(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_be210(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_be212(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_be214(void)

{
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



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_be288(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_be28a(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_be28c(void)

{
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



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_be300(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_be302(void)

{
  return;
}



/* Scale unsignedF03D/F03E by5243 then logicalshift12 intoBE54/BE56. NormalECUpublisher
   setsbothsources0; no physicalunits. Native steady-prefix compositions distinguish entry199/200
   qualification delay, fixed markers, unsigned scaling and gated record8 ownership; not full
   scheduler execution. */

void f33_scale_staged_byte_pair_to_control_raw(void)

{
  f33_scaled_staged_byte_a = (ushort)((uint)((short)(ushort)DAT_febef03d * 0x147b) >> 0xc);
  f33_scaled_staged_byte_b = (ushort)((uint)((short)(ushort)DAT_febef03e * 0x147b) >> 0xc);
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_be322(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_be324(void)

{
  return;
}



/* F02D8..108 ->signed(F02D-48)*128;outsideholdBE5E andstatus0->1.
   Alwayscopyfourdefaultstatusbytes;noF000gate. Native steady-prefix compositions distinguish
   entry199/200 qualification delay, fixed markers, unsigned scaling and gated record8 ownership;
   not full scheduler execution. */

void f33_condition_staged_offset_scalar(void)

{
  uint32_t puVar1;
  int iVar2;
  char cVar3;
  short sStack_a;
  
  cVar3 = DAT_febef02c;
  puVar1 = 0xfebeb800u;
  if (DAT_febef02d - 8 < 0x65) {
    iVar2 = DAT_febef02d - 0x30;
    sStack_a = (short)iVar2;
    puVar1 = 0xfebeb800u;
    FUN_000d1232(iVar2,0x80,1,&sStack_a);
  }
  else {
    if (DAT_febef02c == '\0') {
      cVar3 = '\x01';
    }
    sStack_a = f33_conditioned_offset_scalar;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x658))))) = cVar3;
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + 0x65e)))) = sStack_a;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x65a))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x385a)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x659))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x385b)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x65c))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x385e)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x65b))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x385f)))));
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_be38a(void)

{
  return;
}



/* Hold5A;resetseedA5;adoptadmittedfreshnonFFFFF18A;resetageonlyonchangedvalue,otherwiseadd5withFFFFFFFEsentinelhandling.
   AlwaysconsumeF039generation. Native hold composition retains all three metadata values despite
   invalid statuses while consuming their generation edges. Nonheld arithmetic/validation remains
   static. */

void f33_condition_received_word_and_age(uchar policy)

{
  int iVar1;
  undefined1 uVar2;
  
  if (policy != 'Z') {
    uVar2 = 0;
    if (policy != 0xa5) {
      uVar2 = DAT_febebe60;
    }
    iVar1 = 0;
    if ((((DAT_febef039 != DAT_febebe61) && (DAT_febef038 == '\0')) && (DAT_febef18a != 0xffff)) &&
       (f33_published_internal_source_admission_state < 2)) {
      if (f33_received_retained_word != DAT_febef18a) {
        iVar1 = 0x5a;
      }
      uVar2 = 1;
      f33_received_retained_word = DAT_febef18a;
    }
    if (0xfffffffd < f33_received_word_unchanged_age) {
      f33_received_word_unchanged_age = 0;
    }
    DAT_febebe60 = uVar2;
    if (iVar1 == 0x5a) {
      f33_received_word_unchanged_age = 0;
    }
    else if (f33_received_word_unchanged_age < 0xfffffff9) {
      f33_received_word_unchanged_age = f33_received_word_unchanged_age + 5;
    }
    else {
      f33_received_word_unchanged_age = 0xfffffffe;
    }
  }
  DAT_febebe61 = DAT_febef039;
  return;
}



/* Hold5A;resetA5;invalidstatusclears;admittednewgenerationadoptsuint32F218<=999999withtype1/2,otherwisezero.
   AlwaysconsumeF066generation;BE74isnotapointer. Native hold composition retains all three metadata
   values despite invalid statuses while consuming their generation edges. Nonheld
   arithmetic/validation remains static. */

void f33_condition_received_typed_scalar(uchar policy)

{
  if (policy != 'Z') {
    if (policy == 0xa5) {
      DAT_febebe62 = '\0';
      f33_received_typed_scalar = 0;
    }
    if ((DAT_febef065 != '\0') ||
       (((DAT_febef066 != DAT_febebe63 && (f33_published_internal_source_admission_state < 2)) &&
        ((0xf423fu < f33_published_route31_numeric_scalar ||
         ((DAT_febebe62 = DAT_febef067,
          f33_received_typed_scalar = f33_published_route31_numeric_scalar, DAT_febef067 != '\x01'
          && (DAT_febef067 != '\x02')))))))) {
      f33_received_typed_scalar = 0;
      DAT_febebe62 = '\0';
    }
  }
  DAT_febebe63 = DAT_febef066;
  return;
}



/* Returnunchangedlow8R6whenbothnibblesaredecimaldigits,elsefullR10=FF. Validationonly,noconversion.
    */

uint f33_validate_packed_decimal_byte(uchar packed_value)

{
  uint uVar1;
  
  uVar1 = (uint)packed_value;
  if (((uVar1 & 0xf) < 10) && ((uVar1 & 0xf0) < 0xa0)) {
    return uVar1;
  }
  return 0xff;
}



/* Hold5A/resetA5;invalidstatusorinvalidfreshsix-membertuple->allFF.
   Nibbledigitsandrawbyteboundsretainedwithoutdecimalconversion;alwaysconsumeF0F7generation. Native
   hold composition retains all three metadata values despite invalid statuses while consuming their
   generation edges. Nonheld arithmetic/validation remains static. */

void f33_condition_received_packed_decimal_fields(uchar policy)

{
  uchar packed_value;
  uchar packed_value_00;
  uchar packed_value_01;
  uchar packed_value_02;
  uchar packed_value_03;
  char cVar1;
  uint32_t puVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  uint uVar7;
  uint uVar8;
  
  cVar1 = DAT_febef0f7;
  packed_value_03 = DAT_febef0f6;
  packed_value_02 = DAT_febef0f5;
  packed_value_01 = DAT_febef0f4;
  packed_value_00 = DAT_febef0f3;
  packed_value = DAT_febef0f2;
  puVar2 = 0xfebeb800u;
  if (policy == 'Z') goto LAB_000be5a2;
  if (policy == 0xa5) {
    uVar8 = 0xffffffff;
    uVar7 = 0xffffffff;
    uVar6 = 0xffffffff;
    uVar5 = 0xffffffff;
    uVar4 = 0xffffffff;
    uVar3 = 0xffffffff;
  }
  else {
    uVar8 = (uint)f33_received_packed_decimal_fields[0];
    uVar7 = (uint)f33_received_packed_decimal_fields[1];
    uVar6 = (uint)f33_received_packed_decimal_fields[2];
    uVar5 = (uint)f33_received_packed_decimal_fields[3];
    uVar4 = (uint)f33_received_packed_decimal_fields[4];
    uVar3 = (uint)f33_received_packed_decimal_fields[5];
  }
  puVar2 = 0xfebeb800u;
  if (DAT_febef0f8 == '\0') {
    puVar2 = 0xfebeb800u;
    if ((DAT_febef0f7 != DAT_febebe6c) && (f33_published_internal_source_admission_state < 2)) {
      puVar2 = 0xfebeb800u;
      uVar8 = f33_validate_packed_decimal_byte(DAT_febef0f1);
      uVar7 = f33_validate_packed_decimal_byte(packed_value);
      uVar6 = f33_validate_packed_decimal_byte(packed_value_00);
      uVar5 = f33_validate_packed_decimal_byte(packed_value_01);
      uVar4 = f33_validate_packed_decimal_byte(packed_value_02);
      uVar3 = f33_validate_packed_decimal_byte(packed_value_03);
      if (((0x38 < uVar8) || (((0x11 < uVar7 - 1 || (0x30 < uVar6 - 1)) || (0x23 < uVar5)))) ||
         ((0x59 < uVar4 || (0x59 < uVar3)))) goto LAB_000be586;
    }
  }
  else {
LAB_000be586:
    uVar8 = 0xffffffff;
    uVar7 = 0xffffffff;
    uVar6 = 0xffffffff;
    uVar5 = 0xffffffff;
    uVar4 = 0xffffffff;
    uVar3 = 0xffffffff;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x666))))) = (char)uVar8;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x667))))) = (char)uVar7;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x668))))) = (char)uVar6;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x669))))) = (char)uVar5;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x66a))))) = (char)uVar4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x66b))))) = (char)uVar3;
LAB_000be5a2:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x66c))))) = cVar1;
  return;
}



/* B20E11/33selecthold5A;prior33->0selectresetA5;else0.
   Callthreeconditioners;saveB20EandpublishBE64=5A. Native hold composition retains all three
   metadata values despite invalid statuses while consuming their generation edges. Nonheld
   arithmetic/validation remains static. */

void f33_refresh_received_control_metadata(void)

{
  uint32_t puVar1;
  uchar policy;
  
  puVar1 = 0xfebeb800u;
  if ((DAT_febeb20e == '3') || (DAT_febeb20e == '\x11')) {
    policy = 'Z';
  }
  else if ((DAT_febebe65 == '3') && (DAT_febeb20e == '\0')) {
    policy = 0xa5;
  }
  else {
    policy = '\0';
  }
  DAT_febebe65 = DAT_febeb20e;
  f33_condition_received_word_and_age(policy);
  f33_condition_received_typed_scalar(policy);
  f33_condition_received_packed_decimal_fields(policy);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x664))))) = 0x5a;
  return;
}



/* StagewordBE6E,reservedhalfword0,ageBE70aslogicalrecord13throughFF09C. */

void f33_stage_received_word_age_record13(void)

{
  ushort local_c [2];
  uint uStack_8;
  
  local_c[1] = 0;
  local_c[0] = f33_received_retained_word;
  uStack_8 = f33_received_word_unchanged_age;
  FUN_000ff09c(0xd,local_c);
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_be620(void)

{
  return;
}



/* TierentryinitializesBE78/7B,BE79/7A=5Aandfixed-ratioF194filterseedindependentlyofoptionalBE778cadence.
   NoOEMsourceidentity. */

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



/* Existing arithmetic uses F194 from route26. F0FB1/0/other->BE79A5/5A/FF; F0FB and F052 both copy
   route30 payload bit8031, not independent physical channels. Existing source arithmetic
   plusF0FB1/0/other->BE79A5/5A/FF; no physicalchannel identity assigned. F194 is independent
   route26 arithmetic; F0FB andF052 both copy route30 payload bit8031. */

void f33_refresh_first_health_source_cache(void)

{
  undefined1 uVar1;
  uint32_t puVar2;
  undefined2 uVar3;
  int local_1c;
  ushort uStack_16;
  uint uStack_14;
  ushort uStack_10;
  undefined2 uStack_e;
  undefined4 uStack_c;
  
  puVar2 = 0xfebeb800u;
  FUN_000d1222((int)DAT_febef194,&local_1c);
  FUN_000d1d6e(local_1c,0x4000,&local_1c);
  uStack_10 = (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0x682))));
  uStack_c = (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0x684))));
  uVar3 = (undefined2)((uint)(local_1c * 800) >> 10);
  uStack_e = uVar3;
  f33_filter_unsigned_sample_accumulator(&uStack_10,(uint)DAT_000aee30 * 100,&uStack_16,&uStack_14);
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x38fb))))) == '\x01') {
    uVar1 = 0xa5;
  }
  else {
    uVar1 = 0xff;
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x38fb))))) == '\0') {
      uVar1 = 0x5a;
    }
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + 0x680)))) = uVar3;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x679))))) = uVar1;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0x682)))) = uStack_16;
  (*((uint *)camry_host_ptr((uint32_t)(puVar2 + 0x684)))) = uStack_14;
  return;
}



/* F0521/0/other->BE7AA5/5A/FF; BE7B uses overrideB18F when not1; save F052 inBE78. Normal58074
   duplicates route30 payload bit8031 into both F052 and F0FB. BE7B usesoverrideB18F whennot1;
   saveF052inBE78. F052 duplicatesF0FB from route30, not an independent physical input. */

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



/* PublishBE7C/BE7D0/11/22 from paired status gates and low F057/F051 bits. Both sources copy
   route30 receive status802F, not payload bits or persisted selection tags. PublishBE7C/BE7D0/11/22
   from exactpaired statusbytes andlow receivedbits; not persistedselection tags. F051/F057 both
   copy route30 receive status802F, not payload bits. */

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



/* Refresh both caches and classifications, then F13F->BE7E on admitted cadence bit1. F13F is
   route30 consumed copy generation; it can advance while payload decoding is frozen. Arithmetic
   sampleF194 comes from separate route26, so this is not simultaneous freshness. Refresh
   first/second source andclassification caches thenF13F->BE7E. Scheduler optionally admits this
   generationbeforeunconditionalhealthtierstep. F13F is consumed route30 copy generation and may
   advance while payload decoding is frozen; separate route26 sample freshness is not established.
    */

void f33_refresh_health_received_source_generation(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  f33_refresh_first_health_source_cache();
  f33_refresh_second_health_source_cache();
  f33_refresh_health_channel_classifications();
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x67e))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x393f)))));
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_be794(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_be796(void)

{
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



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_be80a(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_be80c(void)

{
  return;
}



void FUN_000be80e(void)

{
  uint32_t puVar1;
  uchar uVar2;
  bool bVar3;
  
  puVar1 = 0xfebeb800u;
  if ((DAT_febef09e == '\x01') || (DAT_febef0a6 == '\x01')) {
    bVar3 = true;
  }
  else {
    bVar3 = DAT_febef0a7 == '\x01';
  }
  uVar2 = f33_get_grouped_status_byte(0x16);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x68c))))) = bVar3;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x68d))))) = uVar2;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_be842(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_be844(void)

{
  return;
}



/* WARNING: Removing unreachable block (ram,0x000be8ea) */
/* WARNING: Removing unreachable block (ram,0x000be898) */
/* WARNING: Removing unreachable block (ram,0x000be894) */
/* WARNING: Removing unreachable block (ram,0x000be8ee) */

void FUN_000be846(void)

{
  char cVar1;
  char cVar2;
  char cVar3;
  char cVar4;
  int iVar5;
  byte bVar6;
  undefined1 uVar7;
  int iVar8;
  int iVar9;
  uint32_t puVar10;
  int iVar11;
  char cVar12;
  byte bVar13;
  char cVar14;
  byte bVar15;
  char cVar16;
  char cVar17;
  int local_2c;
  
  bVar13 = DAT_febef0aa;
  cVar4 = DAT_febef0a7;
  cVar3 = DAT_febef0a6;
  cVar1 = DAT_febef0a5;
  cVar2 = DAT_febef0a4;
  puVar10 = 0xfebeb800u;
  if (DAT_febebe8d == 'Z') {
    iVar11 = 0;
    iVar9 = 0;
    cVar16 = '\0';
    cVar12 = '\0';
  }
  else {
    iVar11 = ((short)DAT_febef098 * 0x931) / 0x10;
    iVar9 = ((short)DAT_febef099 * 0x931) / 0x10;
    iVar8 = DAT_000af3f4;
    if ((iVar11 - DAT_000af3f4 < 0 ==
         (iVar11 < 0 != DAT_000af3f4 < 0 && DAT_000af3f4 < 0 == iVar11 - DAT_000af3f4 < 0) &&
         iVar11 != DAT_000af3f4) ||
       (iVar8 = -DAT_000af3f4, cVar16 = DAT_febebe91,
       iVar11 + DAT_000af3f4 < 0 !=
       (iVar11 < 0 != iVar8 < 0 && iVar8 < 0 == iVar11 + DAT_000af3f4 < 0))) {
      iVar11 = iVar8;
      cVar16 = 'Z';
    }
    iVar8 = DAT_000af3f4;
    if ((iVar9 - DAT_000af3f4 < 0 ==
         (iVar9 < 0 != DAT_000af3f4 < 0 && DAT_000af3f4 < 0 == iVar9 - DAT_000af3f4 < 0) &&
         iVar9 != DAT_000af3f4) ||
       (iVar8 = -DAT_000af3f4, cVar12 = DAT_febebe91,
       iVar9 + DAT_000af3f4 < 0 != (iVar9 < 0 != iVar8 < 0 && iVar8 < 0 == iVar9 + DAT_000af3f4 < 0)
       )) {
      iVar9 = iVar8;
      cVar12 = 'Z';
    }
  }
  if ((DAT_febeb11a == 0x400) && (DAT_febebe8d != 'Z')) {
    iVar8 = (DAT_febef1c6 * 0x931) / 0x10;
    local_2c = (DAT_febef1c8 * 0x931) / 0x10;
    if (DAT_febef09c == '\0') {
      iVar8 = -iVar8;
      local_2c = -local_2c;
    }
    iVar5 = DAT_000af3f0;
    if ((iVar8 - DAT_000af3f0 < 0 ==
         (iVar8 < 0 != DAT_000af3f0 < 0 && DAT_000af3f0 < 0 == iVar8 - DAT_000af3f0 < 0) &&
         iVar8 != DAT_000af3f0) ||
       (iVar5 = -DAT_000af3f0, cVar17 = DAT_febebe90,
       iVar8 + DAT_000af3f0 < 0 != (iVar8 < 0 != iVar5 < 0 && iVar5 < 0 == iVar8 + DAT_000af3f0 < 0)
       )) {
      iVar8 = iVar5;
      cVar17 = 'Z';
    }
    iVar5 = DAT_000af3f0;
    if ((local_2c - DAT_000af3f0 < 0 ==
         (local_2c < 0 != DAT_000af3f0 < 0 && DAT_000af3f0 < 0 == local_2c - DAT_000af3f0 < 0) &&
         local_2c != DAT_000af3f0) ||
       (iVar5 = -DAT_000af3f0, cVar14 = DAT_febebe90,
       local_2c + DAT_000af3f0 < 0 !=
       (local_2c < 0 != iVar5 < 0 && iVar5 < 0 == local_2c + DAT_000af3f0 < 0))) {
      local_2c = iVar5;
      cVar14 = 'Z';
    }
    local_2c = local_2c - iVar9;
    if ((DAT_febef0aa >> 1 & 1) == 0) {
      iVar9 = 0x10;
    }
    else {
      iVar9 = 0x10000;
      local_2c = (local_2c + (iVar8 - iVar11)) * 0xb50;
    }
    if (iVar9 != 0) {
      if (local_2c == -0x80000000 && iVar9 == -1) {
        local_2c = -0x80000000;
      }
      else {
        local_2c = local_2c / iVar9;
      }
    }
    puVar10 = 0xfebeb800u;
    FUN_000d1cf6(local_2c,DAT_000af3f8,-DAT_000af3f8,&local_2c);
  }
  else {
    (*((uint16_t *)((uint8_t *)&local_2c + 0u))) = 0;
    cVar17 = '\0';
    cVar14 = '\0';
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar10 + 0x696)))) = (undefined2)local_2c;
  bVar6 = bVar13 & 2;
  if ((bVar13 & 2) == 0) {
    bVar13 = bVar6;
    if (cVar12 == 'Z') {
      bVar13 = 0x5a;
    }
    bVar15 = bVar6;
    if (cVar14 == 'Z') {
      bVar15 = 0x5a;
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar10 + (uint32_t)(0x691))))) = bVar13;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar10 + (uint32_t)(0x690))))) = bVar15;
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar10 + (uint32_t)(0x38a7))))) == '\x01') {
      bVar6 = 0x5a;
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar10 + (uint32_t)(0x692))))) = bVar6;
    cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar10 + (uint32_t)(0x38a5)))));
joined_r0x000be9f4:
    if (cVar1 != '\x01') {
      uVar7 = 0;
      goto LAB_000be9fa;
    }
  }
  else {
    if ((cVar16 == 'Z') || (cVar12 == 'Z')) {
      uVar7 = 0x5a;
    }
    else {
      uVar7 = 0;
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar10 + (uint32_t)(0x691))))) = uVar7;
    if ((cVar17 == 'Z') || (cVar14 == 'Z')) {
      uVar7 = 0x5a;
    }
    else {
      uVar7 = 0;
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar10 + (uint32_t)(0x690))))) = uVar7;
    if ((cVar3 == '\x01') || (cVar4 == '\x01')) {
      uVar7 = 0x5a;
    }
    else {
      uVar7 = 0;
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar10 + (uint32_t)(0x692))))) = uVar7;
    if (cVar2 != '\x01') goto joined_r0x000be9f4;
  }
  uVar7 = 0x5a;
LAB_000be9fa:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar10 + (uint32_t)(0x693))))) = uVar7;
  uVar7 = 0;
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar10 + (uint32_t)(0x68c))))) == '\x01') {
    uVar7 = 0x5a;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar10 + (uint32_t)(0x694))))) = uVar7;
  return;
}



/* SetBED4=55AAAA55,BE9D/BEB3=0,BEA7=5A. Unconditionalsoftwaremarker,notreceivedidentity. */

void f33_publish_first_fixed_received_marker(void)

{
  DAT_febebed4 = 0x55aaaa55;
  DAT_febebe9d = 0;
  DAT_febebeb3 = 0;
  DAT_febebea7 = 0x5a;
  return;
}



/* SetBED8=55AAAA55,BE9E/BEB4=0,BEA8=5A. Unconditionalsoftwaremarker. */

void f33_publish_second_fixed_received_marker(void)

{
  DAT_febebed8 = 0x55aaaa55;
  DAT_febebe9e = 0;
  DAT_febebeb4 = 0;
  DAT_febebea8 = 0x5a;
  return;
}



/* Callbothfixedmarkerpublishersduringcommoncontrolinitialization. */

void f33_initialize_fixed_received_markers(void)

{
  f33_publish_first_fixed_received_marker();
  f33_publish_second_fixed_received_marker();
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_bea54(void)

{
  return;
}



/* WhileBEA2=0,F000<2qualifiesBEC4atentry>=300,clearsBE98;badgateresetscount.
   Stickycompletion;alwaysBEAD0andBEAE=BE98. */

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



/* WhileBEA3=0,F000<2,F0280,F02B1qualifyBEBCatentry>=48->BEA3/BE99=5A;alwaysBEAF0.
   Canonicalpublisherdefaultsinhibitnewqualification. */

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



/* WhileBEA4=0,F000<2,F0600qualifyBEBEatentry>=96->BEA4/BE9A=5A;alwaysBEB00. CanonicalF0601inhibits.
    */

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



/* WhileBEA5=0,F000<2andF069receive-status0qualifyBEC0atentry>=40->BEA5/BE9B5A;alwaysBEB2=BE9B.
   Stickycompletion. */

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



/* WhileBEA6=0,F000<2andF04Creceive-status0qualifyBEC2atentry>=64->BEA6/BE9C5A;alwaysBEB1=BE9C. */

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



/* PublishBE9F/BEB6=5Awithoutwirepredicate. */

void f33_publish_received_channel_f_defaults(void)

{
  DAT_febebe9f = 0x5a;
  DAT_febebeb6 = 0x5a;
  return;
}



/* PublishBEA0=5Awithoutwirepredicate. */

void f33_publish_received_channel_g_default(void)

{
  DAT_febebea0 = 0x5a;
  return;
}



/* PublishBEA1=5Awithoutwirepredicate. */

void f33_publish_received_channel_h_default(void)

{
  DAT_febebea1 = 0x5a;
  return;
}



/* ComposeBEBE4/BEBF2/BEBFCconstantsoftwaredefaults. */

void f33_publish_fixed_received_channel_defaults(void)

{
  f33_publish_received_channel_f_defaults();
  f33_publish_received_channel_g_default();
  f33_publish_received_channel_h_default();
  return;
}



/* ClearBEB8/BEB5;noinputsampling. */

void f33_clear_fixed_received_metadata(void)

{
  DAT_febebeb8 = 0;
  DAT_febebeb5 = 0;
  return;
}



/* WhileBEBB=0,F000<2and(F1480orF1490)qualifyBED0atentry>=200->BEBB/BEBA5A;alwaysBEB7=BEBA.
   Canonicalboth1inhibit. */

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



/* ClearonlyBEADduringglobalstartupdelay;otherchannelstateisretained. */

void f33_publish_received_startup_delay_default(void)

{
  DAT_febebead = 0;
  return;
}



/* EntryBEC6<200onlyclearsBEADandincrements;entry>=200runsreadiness/defaultgroup.
   Alwayspublishbothfixedmarkersaftereitherbranch. Mode>=0101everyforegroundinvocation. Native
   steady-prefix compositions distinguish entry199/200 qualification delay, fixed markers, unsigned
   scaling and gated record8 ownership; not full scheduler execution. */

void f33_update_delayed_received_startup_qualification(void)

{
  uint32_t puVar1;
  ushort uVar2;
  
  uVar2 = f33_received_qualification_startup_count;
  puVar1 = 0xfebeb800u;
  if (f33_received_qualification_startup_count < DAT_000af408) {
    f33_publish_received_startup_delay_default();
    uVar2 = uVar2 + 1;
  }
  else {
    puVar1 = 0xfebeb800u;
    f33_qualify_received_scalar_startup();
    f33_qualify_received_channel_b_startup();
    f33_qualify_received_channel_c_startup();
    f33_qualify_received_channel_d_startup();
    f33_qualify_received_channel_e_startup();
    f33_publish_fixed_received_channel_defaults();
    f33_clear_fixed_received_metadata();
    f33_qualify_received_paired_channel_startup();
  }
  f33_publish_first_fixed_received_marker();
  f33_publish_second_fixed_received_marker();
  (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + 0x6c6)))) = uVar2;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_beccc(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_becce(void)

{
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



void FUN_000becf4(void)

{
  uint32_t puVar1;
  ushort uStack_6;
  
  puVar1 = 0xfebeb800u;
  uStack_6 = DAT_febef1b6;
  if (DAT_febeb218 != 0x5aa5a55a) {
    if ((DAT_febebedd == 'Z') && (DAT_febef002 == '\0')) {
      DAT_febebedc = 0x11;
      goto LAB_000bed6a;
    }
    if (((((DAT_febef013 != '\x02' && DAT_febef013 != '\x03') &&
          (f33_published_internal_source_admission_state != '\x03')) &&
         ((DAT_febef093 >> 1 & 1) == 0)) &&
        (((DAT_febeb1ce != 'Z' && (DAT_febef0b3 != 'Z')) || ((DAT_febef093 & 1) == 0)))) &&
       (DAT_febef002 != 'Z')) {
      DAT_febebedc = 0x22;
      goto LAB_000bed6a;
    }
  }
  DAT_febebedc = 0x44;
LAB_000bed6a:
  FUN_000d1d5c(DAT_febef1b6,30000,&uStack_6);
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + 0x6de)))) = (short)((uint)uStack_6 * 0x147b >> 0xc);
  return;
}



void FUN_000bed90(void)

{
  FUN_000becd0();
  FUN_000becf4();
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_beda0(void)

{
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



void FUN_000bedc4(void)

{
  uint32_t puVar1;
  char cVar2;
  ushort uStack_16;
  uint uStack_14;
  ushort uStack_10;
  ushort uStack_e;
  undefined4 uStack_c;
  
  cVar2 = DAT_febebee1;
  puVar1 = 0xfebeb800u;
  if (DAT_febebee1 == '\0') {
    uStack_16 = DAT_febebede;
    uStack_14 = (uint)DAT_febebede << 0x10;
    if (DAT_febebef0 == '\x11') {
      cVar2 = 'Z';
    }
  }
  else {
    uStack_e = DAT_febebede;
    uStack_10 = DAT_febebee4;
    uStack_c = DAT_febebeec;
    puVar1 = 0xfebeb800u;
    f33_filter_unsigned_sample_accumulator
              (&uStack_10,(uint)DAT_000af410 * 100,&uStack_16,&uStack_14);
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x6e1))))) = cVar2;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + 0x6e4)))) = uStack_16;
  (*((uint *)camry_host_ptr((uint32_t)(puVar1 + 0x6ec)))) = uStack_14;
  return;
}



void FUN_000bee2c(void)

{
  int iVar1;
  char cVar2;
  byte bVar3;
  char cVar4;
  uint32_t puVar5;
  char cVar6;
  ushort local_34;
  ushort uStack_32;
  uint uStack_30;
  uint uStack_2c;
  ushort uStack_28;
  ushort uStack_26;
  undefined2 uStack_24;
  undefined2 uStack_22;
  ushort uStack_20;
  ushort uStack_1e;
  uint uStack_1c;
  
  cVar4 = DAT_febebef0;
  cVar6 = DAT_febebee0;
  bVar3 = DAT_febeb117;
  cVar2 = DAT_febeb116;
  puVar5 = 0xfebeb800u;
  uStack_32 = DAT_febebee2;
  uStack_2c = DAT_febebee8;
  if (DAT_febebef0 == '\x11') {
    if (DAT_febebee0 == 'Z') {
      uStack_26 = DAT_febebee2;
      uStack_28 = DAT_febebee4;
      uStack_24 = DAT_000af416;
      uStack_22 = DAT_000af418;
      puVar5 = 0xfebeb800u;
      FUN_000d1d1c(&uStack_28,&local_34);
    }
    else {
      local_34 = DAT_febebee4;
    }
  }
  else {
    cVar6 = '\0';
    local_34 = DAT_febebee2;
    if (DAT_febebef0 == 'D') {
      local_34 = DAT_000af414;
    }
  }
  if (cVar2 == 'Z') {
    local_34 = (ushort)bVar3 << 7;
  }
  (*((ushort *)camry_host_ptr((uint32_t)(puVar5 + 0x6e6)))) = local_34;
  uStack_30 = (uint)uStack_32 - (uint)local_34;
  FUN_000d1194(uStack_30,&uStack_30);
  iVar1 = uStack_30 - DAT_000af41a;
  if (iVar1 < 0 == ((int)uStack_30 < 0 && -1 < iVar1) && uStack_30 != DAT_000af41a) {
    uStack_1e = local_34;
    uStack_20 = uStack_32;
    uStack_1c = uStack_2c;
    f33_filter_unsigned_sample_accumulator
              (&uStack_20,(uint)DAT_000af412 * 100,&uStack_32,&uStack_2c);
  }
  else {
    uStack_32 = local_34;
    uStack_2c = (uint)local_34 << 0x10;
    if (cVar4 == '\x11') {
      cVar6 = 'Z';
    }
  }
  (*((ushort *)camry_host_ptr((uint32_t)(puVar5 + 0x6e2)))) = uStack_32;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(0x6e0))))) = cVar6;
  (*((uint *)camry_host_ptr((uint32_t)(puVar5 + 0x6e8)))) = uStack_2c;
  return;
}



void FUN_000bef10(void)

{
  FUN_000bedc4();
  FUN_000bee2c();
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_bef20(void)

{
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



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_bef98(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_bef9a(void)

{
  return;
}



void FUN_000bef9c(void)

{
  uint32_t puVar1;
  uchar uVar2;
  bool bVar3;
  
  puVar1 = 0xfebeb800u;
  if ((DAT_febef09e == '\x01') || (DAT_febef0a6 == '\x01')) {
    bVar3 = true;
  }
  else {
    bVar3 = DAT_febef0a7 == '\x01';
  }
  uVar2 = f33_get_grouped_status_byte(0x16);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x6f4))))) = bVar3;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x6f5))))) = uVar2;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_befd2(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_befd4(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_bf0a6(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_bf0a8(void)

{
  return;
}



/* R6resultbyte*,R7completionbyte*,R8zero-countu16*,R9nonzero-countu16*.
   Prefercount>=3resultACEDovercount>=8result0;clampwinningcount. Native strict warmup with third
   admitted observation commits record8 confirmation and real snapshot once; other outcomes remain
   static. */

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



/* Increment16-bittotal;strict>10failsbeforeobservations.
   F0690permitsF06Ezero/nonzeroobservationcounts;statusnonzeroqualifiesinvalidcount>=8.
   Result/completionpointersarepreservedacrossrealBF0AA. Native strict warmup with third admitted
   observation commits record8 confirmation and real snapshot once; other outcomes remain static. */

void f33_step_record8_confirmation_window(uchar *result,uchar *completed)

{
  ushort uVar1;
  ushort uVar2;
  undefined *puVar3;
  ushort uVar5;
  ushort local_10;
  ushort uStack_e;
  uint32_t puVar4;
  uVar2 = DAT_000af42c;
  uVar5 = DAT_000af42a;
  puVar4 = 0xfebeb800u;
  puVar3 = ((undefined *)camry_host_ptr(0xfebeb800u));
  uVar1 = f33_record8_confirmation_window_count + 1;
  if (DAT_000af42a < uVar1) {
    *completed = 'Z';
    *result = '\0';
  }
  else {
    if (DAT_febef069 == '\0') {
      if (DAT_febef06e == '\0') {
        local_10 = f33_record8_zero_observation_count + 1;
        uStack_e = 0;
      }
      else {
        local_10 = 0;
        uStack_e = f33_record8_nonzero_observation_count + 1;
      }
      f33_qualify_record8_admitted_observations(result,completed,&local_10,&uStack_e);
      puVar3 = ((undefined *)camry_host_ptr((uint32_t)(puVar4)));
      uVar5 = 0;
    }
    else {
      local_10 = 0;
      uStack_e = 0;
      puVar3 = ((undefined *)camry_host_ptr(0xfebeb800u));
      uVar5 = f33_record8_invalid_observation_count + 1;
      if (DAT_000af42c <= (ushort)(f33_record8_invalid_observation_count + 1)) {
        *completed = 'Z';
        *result = '\0';
        uVar5 = uVar2;
      }
    }
    *(ushort *)(puVar3 + 0x708) = local_10;
    *(ushort *)(puVar3 + 0x70c) = uVar5;
    *(ushort *)(puVar3 + 0x70a) = uStack_e;
    uVar5 = uVar1;
  }
  *(ushort *)(puVar3 + 0x70e) = uVar5;
  return;
}



/* OnceonlywhileinitialACED5A;strictincrementedwarmup>60;B080>4096rejects;F0015Aadmitswindowelseclearinnercounts.
   OnoldBF040->newcompletion5AcommitBD86Eandsnapshot. Native strict warmup with third admitted
   observation commits record8 confirmation and real snapshot once; other outcomes remain static. */

void f33_advance_record8_startup_confirmation(void)

{
  ushort uVar1;
  uchar uVar2;
  uint32_t puVar3;
  undefined *puVar4;
  ushort uVar5;
  uchar uStack_e;
  uchar uStack_d;
  
  uVar2 = f33_record8_confirmation_complete;
  uVar1 = DAT_000af428;
  puVar3 = 0xfebeb800u;
  puVar4 = ((undefined *)camry_host_ptr(0xfebeb800u));
  uStack_d = f33_record8_confirmation_result;
  uStack_e = f33_record8_confirmation_complete;
  if ((f33_record8_confirmation_complete == '\0') && (DAT_febeaced == 'Z')) {
    uVar5 = f33_record8_confirmation_warmup_count + 1;
    puVar4 = ((undefined *)camry_host_ptr(0xfebeb800u));
    if (DAT_000af428 < (ushort)(f33_record8_confirmation_warmup_count + 1)) {
      uVar5 = uVar1;
      if (DAT_000af432 < DAT_febeb080) {
        uStack_d = '\0';
        uStack_e = 'Z';
      }
      else if (DAT_febef001 == 'Z') {
        f33_step_record8_confirmation_window(&uStack_d,&uStack_e);
        puVar4 = ((undefined *)camry_host_ptr((uint32_t)(puVar3)));
      }
      else {
        f33_record8_zero_observation_count = 0;
        f33_record8_nonzero_observation_count = 0;
        f33_record8_invalid_observation_count = 0;
        f33_record8_confirmation_window_count = 0;
      }
    }
    *(ushort *)(puVar4 + 0x706) = uVar5;
  }
  else {
    uStack_e = 'Z';
  }
  if ((uVar2 == '\0') && (uStack_e == 'Z')) {
    FUN_000bd86e(uStack_d);
  }
  puVar4[0x705] = uStack_d;
  puVar4[0x704] = uStack_e;
  return;
}



/* CallBF18AonlyACEE==5A;closedgatefreezesallstate.
   Calledmode>=0101beforeoptionalhealthsourcecachegeneration. Native steady-prefix compositions
   distinguish entry199/200 qualification delay, fixed markers, unsigned scaling and gated record8
   ownership; not full scheduler execution. */

void f33_update_initialized_record8_confirmation(void)

{
  if (DAT_febeacee == 'Z') {
    f33_advance_record8_startup_confirmation();
  }
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_bf248(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_bf24a(void)

{
  return;
}



/* Saturatingabs16AFE0andROMenable5A;setBF11at>=5120,clearat<=2560,retainbetween.
   Acquiredscalar,notwireidentity. */

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



/* Incrementselectedu16counteronlywhile<=limitandclearoppositeonlyonincrementpath;strict>limitupdatesBF10.
   ROMlimit0givesone-invocationordinaryresponse. */

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



/* ComposeBF24ChysteresisthenBF298debouncedBF10publishedtoE848byBF3AA;mode>=0100. */

void f33_refresh_acquired_scalar_status_publication(void)

{
  f33_update_acquired_scalar_hysteresis();
  f33_debounce_acquired_scalar_hysteresis();
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_bf2f4(void)

{
  return;
}



/* Constant-block fill: 11 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_bf2f8(void)

{
  DAT_febee608 = DAT_febeaf40;
  DAT_febee604 = 0;
  DAT_febee605 = 0;
  DAT_febee600 = DAT_febeaf3d;
  DAT_febee610 = DAT_febeac1c;
  DAT_febee601 = DAT_febeac08;
  DAT_febee602 = DAT_febeac09;
  DAT_febee603 = DAT_febeac02;
  DAT_febee60a = DAT_febebd34;
  DAT_febee606 = DAT_febebe21;
  DAT_febee60c = DAT_febebdb4;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_bf33a(void)

{
  return;
}



/* Constant-block fill: 17 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

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



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_bf3a6(void)

{
  return;
}



/* Publish control/health/current-limit state intoE800+ and copy immutable calibration bounds.
   Includes liveB11A\u2192E8CC after the mode arbiter. Central transition/steady workers call this
   last even for mode0; common initializationBF97A does not. Includes liveB11A→E8CC after the mode
   arbiter. */

void f33_publish_foreground_control_outputs(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  DAT_febee88e = DAT_000aeff6;
  f33_learned_quad_runtime_bounds.pair1_upper = f33_learned_quad_rom_bounds.pair1_upper;
  f33_learned_quad_runtime_bounds.pair1_lower = f33_learned_quad_rom_bounds.pair1_lower;
  f33_learned_quad_runtime_bounds.pair2_upper = f33_learned_quad_rom_bounds.pair2_upper;
  f33_learned_quad_runtime_bounds.pair2_lower = f33_learned_quad_rom_bounds.pair2_lower;
  DAT_febee8f8 = DAT_000aef6c;
  DAT_febee8fc = DAT_000aef70;
  DAT_febee900 = DAT_000aef74;
  DAT_febee904 = DAT_000aef78;
  DAT_febee800 = DAT_febeb1d5;
  DAT_febee801 = DAT_febebe9b;
  DAT_febee802 = DAT_febebe9c;
  DAT_febee803 = DAT_febebe99;
  DAT_febee804 = DAT_febebe9a;
  DAT_febee805 = DAT_febebe9f;
  DAT_febee806 = DAT_febebea0;
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -9;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebee807u + (uint32_t)(iVar3) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebebeaeu + (uint32_t)(iVar3) * 1u))));
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  DAT_febee908 = DAT_febebed4;
  DAT_febee890 = DAT_febebe82;
  DAT_febee811 = DAT_febebe78;
  DAT_febee892 = DAT_febebede;
  DAT_febee812 = DAT_febebef0;
  DAT_febee894 = DAT_febebee2;
  DAT_febee90c = f33_received_word_unchanged_age;
  DAT_febee896 = f33_received_retained_word;
  DAT_febee813 = DAT_febebe64;
  DAT_febee910 = f33_received_typed_scalar;
  DAT_febee814 = DAT_febebe62;
  DAT_febee815 = DAT_febebe60;
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -1;
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebee914u + (uint32_t)(iVar3) * 4u)))) = (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebebe4cu + (uint32_t)(iVar3) * 4u))));
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -1;
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebee898u + (uint32_t)(iVar3) * 2u)))) = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebebe42u + (uint32_t)(iVar3) * 2u))));
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebee816u + (uint32_t)(iVar3) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebebe36u + (uint32_t)(iVar3) * 1u))));
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -1;
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebee89cu + (uint32_t)(iVar3) * 2u)))) = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebebe3eu + (uint32_t)(iVar3) * 2u))));
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebee818u + (uint32_t)(iVar3) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebebe34u + (uint32_t)(iVar3) * 1u))));
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -1;
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebee8a0u + (uint32_t)(iVar3) * 2u)))) = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebebe3au + (uint32_t)(iVar3) * 2u))));
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  DAT_febee81a = DAT_febeaf44;
  DAT_febee91c = DAT_febeb314;
  DAT_febee920 = DAT_febeb30c;
  DAT_febee81b = DAT_febeb307;
  DAT_febee924 = DAT_febeb474;
  DAT_febee81c = DAT_febeb467;
  DAT_febee81d = DAT_febeb33b;
  DAT_febee928 = DAT_febeb218;
  DAT_febee8a4 = DAT_febeb384;
  DAT_febee8a6 = DAT_febeb142;
  DAT_febee8a8 = DAT_febeb138;
  DAT_febee8aa = DAT_febeb13c;
  DAT_febee81e = DAT_febeb18f;
  DAT_febee81f = DAT_febeb1a4;
  DAT_febee820 = DAT_febeb1a7;
  DAT_febee821 = DAT_febeb1a6;
  DAT_febee822 = DAT_febeb1ca;
  DAT_febee823 = DAT_febeb1c9;
  DAT_febee824 = DAT_febeb1ce;
  DAT_febee825 = DAT_febeb1d1;
  DAT_febee826 = DAT_febeb20e;
  DAT_febee827 = DAT_febeb1bd;
  DAT_febee828 = DAT_febeb1bc;
  DAT_febee829 = DAT_febeb1c4;
  DAT_febee82a = DAT_febeb1a8;
  DAT_febee82b = DAT_febebde4;
  DAT_febee8ac = DAT_febebd7e;
  DAT_febee8ae = DAT_febebccc;
  DAT_febee8b0 = DAT_febebcc2;
  DAT_febee8b2 = DAT_febebcd6;
  DAT_febee8b4 = DAT_febebca6;
  DAT_febee82c = DAT_febebca4;
  DAT_febee8b6 = DAT_febeae12;
  DAT_febee82d = DAT_febeacf1;
  DAT_febee8b8 = DAT_febeae10;
  DAT_febee82e = DAT_febead14;
  DAT_febee82f = DAT_febead47;
  DAT_febee830 = DAT_febead33;
  DAT_febee8ba = DAT_febeae58;
  DAT_febee831 = DAT_febead39;
  DAT_febee832 = DAT_febead44;
  DAT_febee833 = DAT_febead43;
  DAT_febee834 = DAT_febead42;
  DAT_febee835 = DAT_febead45;
  DAT_febee836 = DAT_febead15;
  DAT_febee837 = DAT_febead17;
  DAT_febee838 = DAT_febead46;
  DAT_febee839 = DAT_febead0b;
  DAT_febee8bc = DAT_febeae5c;
  DAT_febee83a = DAT_febead4b;
  DAT_febee83b = DAT_febead49;
  DAT_febee83c = DAT_febead4a;
  DAT_febee83d = DAT_febead48;
  DAT_febee83e = DAT_febead60;
  DAT_febee8be = DAT_febeae6a;
  DAT_febee83f = DAT_febead67;
  DAT_febee8c0 = DAT_febeae6c;
  DAT_febee8c2 = DAT_febeae6e;
  DAT_febee8c4 = DAT_febeae2c;
  DAT_febee8c6 = DAT_febeae36;
  DAT_febee840 = DAT_febead0a;
  DAT_febee841 = DAT_febeacf7;
  DAT_febee842 = DAT_febeacf5;
  DAT_febee843 = DAT_febeacf8;
  DAT_febee8c8 = DAT_febeae14;
  DAT_febee8ca = DAT_febeae16;
  DAT_febee844 = DAT_febeacf6;
  DAT_febee845 = DAT_febead09;
  DAT_febee846 = DAT_febead16;
  DAT_febee8cc = DAT_febeb11a;
  DAT_febee847 = DAT_febeb112;
  DAT_febee848 = DAT_febebf10;
  DAT_febee849 = DAT_febeb252;
  DAT_febee84a = DAT_febeb2cd;
  DAT_febee84b = DAT_febeb2c0;
  DAT_febee84c = DAT_febeb2c1;
  DAT_febee84d = DAT_febeb2c2;
  DAT_febee84e = DAT_febeb2c3;
  DAT_febee84f = DAT_febeb2c4;
  DAT_febee850 = DAT_febeb2c5;
  DAT_febee851 = DAT_febeb2c6;
  DAT_febee852 = DAT_febeb2c7;
  DAT_febee92c = DAT_febeb478;
  DAT_febee853 = DAT_febeb358;
  DAT_febee854 = DAT_febeb37e;
  DAT_febee855 = DAT_febeb25a;
  DAT_febee856 = DAT_febeaf49;
  DAT_febee857 = DAT_febeb300;
  DAT_febee858 = DAT_febeb45f;
  DAT_febee859 = DAT_febeb32f;
  DAT_febee85a = DAT_febeaf45;
  DAT_febee872 = 0;
  DAT_febee873 = 0;
  DAT_febee874 = 0;
  DAT_febee85b = DAT_febeaf4a;
  DAT_febee875 = 0;
  DAT_febee876 = 0;
  DAT_febee877 = 0;
  DAT_febee930 = DAT_febeaf10;
  DAT_febee878 = 0;
  DAT_febee85c = DAT_febead8f;
  DAT_febee85d = DAT_febead90;
  DAT_febee85e = DAT_febead91;
  DAT_febee85f = DAT_febead92;
  DAT_febee860 = DAT_febead93;
  DAT_febee861 = DAT_febead94;
  DAT_febee862 = DAT_febead95;
  DAT_febee863 = DAT_febead96;
  DAT_febee8ce = DAT_febeae82;
  DAT_febee864 = DAT_febead97;
  DAT_febee865 = DAT_febeb04c;
  DAT_febee866 = DAT_febebe06;
  DAT_febee934 = DAT_febeaf14;
  DAT_febee8d0 = DAT_febeae80;
  DAT_febee8d2 = DAT_febebcb0;
  DAT_febee867 = f33_received_packed_decimal_fields[0];
  DAT_febee868 = f33_received_packed_decimal_fields[1];
  DAT_febee869 = f33_received_packed_decimal_fields[2];
  DAT_febee86a = f33_received_packed_decimal_fields[3];
  DAT_febee86b = f33_received_packed_decimal_fields[4];
  DAT_febee86c = f33_received_packed_decimal_fields[5];
  DAT_febee86d = DAT_febebeb8;
  DAT_febee8d4 = DAT_febeae84;
  DAT_febee86e = f33_source_coherence_history;
  DAT_febee86f = DAT_febebe9e;
  DAT_febee870 = DAT_febebe9d;
  DAT_febee8d6 = DAT_febeae86;
  DAT_febee871 = DAT_febead9e;
  DAT_febee879 = DAT_febead9f;
  DAT_febee87a = DAT_febeada0;
  DAT_febee87b = DAT_febeada1;
  DAT_febee87c = DAT_febeada9;
  DAT_febee87d = DAT_febeadab;
  DAT_febee87e = DAT_febeb1cd;
  DAT_febee87f = DAT_febeb1d7;
  DAT_febee8d8 = DAT_febeb13e;
  DAT_febee938 = DAT_febeaf2c;
  DAT_febee8da = DAT_febeaecc;
  DAT_febee8dc = DAT_febebd9e;
  DAT_febee880 = DAT_febeadca;
  DAT_febee881 = DAT_febeadce;
  DAT_febee93c = DAT_febeaf30;
  DAT_febee940 = DAT_febeaf34;
  DAT_febee944 = DAT_febeaf38;
  DAT_febee8de = DAT_febeaece;
  DAT_febee882 = DAT_febeadc8;
  DAT_febee883 = DAT_febeadd7;
  DAT_febee8e0 = DAT_febeb38a;
  DAT_febee884 = DAT_febeb3d1;
  DAT_febee885 = DAT_febeb388;
  DAT_febee8e2 = DAT_febeb418;
  DAT_febee886 = DAT_febeb3d2;
  DAT_febee948 = DAT_febeb148;
  DAT_febee887 = DAT_febeb16b;
  DAT_febee888 = DAT_febeb144;
  DAT_febee94c = DAT_febeb158;
  DAT_febee8e4 = DAT_febeaed2;
  DAT_febee8e6 = DAT_febeaed4;
  DAT_febee889 = DAT_febeb3ca;
  DAT_febee88a = DAT_febeb3d7;
  DAT_febee88b = DAT_febeb3d8;
  DAT_febee950 = DAT_febeb3f8;
  DAT_febee88c = DAT_febeadde;
  DAT_febee88d = DAT_febeaddf;
  DAT_febee958 = 0;
  DAT_febee954 = DAT_febeb150;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_bf91a(void)

{
  return;
}



/* Cold-only control-retained state: clearB195/B196 andBE7E with other retained input/filter cells;
   selected qualifiers start1. Warm5886C skips this owner; health edge history can survive the
   common component initialization. */

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


