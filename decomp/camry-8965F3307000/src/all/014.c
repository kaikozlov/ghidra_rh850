#include "common.h"


/* 5002C/2E loads,50030 shl8,50032or;B8A4C fullu16setterB418;owner0/status0. */

uint f33_write_2013_service_numeric_target(uchar *payload,ushort unused_length)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  f33_set_service_numeric_target_thunk(CONCAT11(*payload,payload[1]));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x364e)))) = 0;
  return 0;
}



/* Exact40-byte identity4FFFE, GNU decoded50042..50068;receive-status80A5 separate
   fromgeneration80A4. */

uint f33_write_2014_precondition(void)

{
  if (((DAT_febe80a5 == '\0') && (DAT_febe80a0 == '\0')) && (DAT_febee892 <= DAT_000318ae)) {
    return 0;
  }
  return 5;
}



/* 0/1->B3D2 0/5A throughB85A2;invalid4 no setter. All clear81B2. */

uint f33_write_2014_service_qualification_mode(uchar *payload,ushort unused_length)

{
  uint32_t puVar1;
  uchar mode;
  uint uVar2;
  
  puVar1 = 0xfebeb800u;
  if (*payload == '\0') {
    mode = '\0';
  }
  else {
    if (*payload != '\x01') {
      uVar2 = 4;
      goto LAB_0005008c;
    }
    mode = 'Z';
  }
  puVar1 = 0xfebeb800u;
  f33_set_service_qualification_mode_thunk(mode);
  uVar2 = 0;
LAB_0005008c:
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x364e)))) = 0;
  return uVar2;
}



void FUN_00050094(undefined1 param_1)

{
  FUN_0008b79a(param_1);
  return;
}



/* Raw500A2..AC819A==1?5:0;nooperationinputconsumed. */

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



/* start:4D222(out,32) builds high-byte family support bitmap using low-byte-zero RID
   entries;outlen32,result2. results:byte,outlen1;other=>7. No asynchronous application service.
   Raw500AE..50886:
   R6zxbcontrols1/2/3;R9output;fifthargumentatentrySP+0pointsu16length(st.h);return32-bitR10;inputargumentsunusedbytheseactions.
   Result requestsproduce1byte;starts/stops0exceptcapabilitystarts32. */

uint f33_diag_routine_1001_family_capabilities
               (uchar control_type,uchar *unused_input,ushort unused_input_length,uchar *output,
               ushort *output_length)

{
  uint32_t puVar1;
  uint uVar2;
  
  puVar1 = 0xfebeb800u;
  uVar2 = 0;
  if (control_type == '\x01') {
    ((void)(unused_input_length), FUN_0004d222(camry_host_addr(output), 0x20));
    *output_length = 0x20;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3664))))) = 2;
  }
  else if (control_type == '\x03') {
    *output = DAT_febe819c;
    *output_length = 1;
  }
  else {
    uVar2 = 7;
  }
  return uVar2;
}



/* 819A==1?5:0. */

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



/* start:4D308(1000,out,32) builds10xx RID support bitmap from26918;outlen=32;result=2 immediately.
   results:copy result byte,outlen1. Other direct control=>7. No asynchronous application service.
   Raw500AE..50886:
   R6zxbcontrols1/2/3;R9output;fifthargumentatentrySP+0pointsu16length(st.h);return32-bitR10;inputargumentsunusedbytheseactions.
   Result requestsproduce1byte;starts/stops0exceptcapabilitystarts32. */

uint f33_diag_routine_1000_capabilities
               (uchar control_type,uchar *unused_input,ushort unused_input_length,uchar *output,
               ushort *output_length)

{
  uint32_t puVar1;
  uint uVar2;
  
  puVar1 = 0xfebeb800u;
  uVar2 = 0;
  if (control_type == '\x01') {
    FUN_0004d308(0x1000, camry_host_addr(output), 0x20);
    *output_length = 0x20;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3665))))) = 2;
  }
  else if (control_type == '\x03') {
    *output = DAT_febe819b;
    *output_length = 1;
  }
  else {
    uVar2 = 7;
  }
  return uVar2;
}



/* 819A==1=>5. start requires unsignedE892<=CodeFlash318AE (0200);already running=>8;results
   accepted;other=>7. Proof50164..72. Raw50152..5081E zxbR6andfullR10return0/5/7/8;gate details in
   companion recovery rows. */

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



/* start:35AA2 conditionally requests internal6AE2=22 normalization (only when6AF0 neitherFFFFFFFF
   norA55A5AA5 and6ADD neither88 nor11 and6AE2!=11), thenB9320(44) writesAF47, unconditionally marks
   result1,outlen0. ScheduledB9212 consumes44: ifAF46!=5A andB8D9C(1)==5A thenB8DDA(1) restarts
   lifecycle groupB439;setsAF46=5A,AF44 active,consumesAF47 and reports selector2 success. This is
   normalization acknowledgement, NOT lower group convergence. A rejected lower restart still sets
   normalization flag and acknowledges. Later normalizer request88 clearsAF46. Result3 returns
   byte,len1. Raw500AE..50886:
   R6zxbcontrols1/2/3;R9output;fifthargumentatentrySP+0pointsu16length(st.h);return32-bitR10;inputargumentsunusedbytheseactions.
   Result requestsproduce1byte;starts/stops0exceptcapabilitystarts32. */

uint f33_diag_routine_1002_normalize_lifecycle
               (uchar control_type,uchar *unused_input,ushort unused_input_length,uchar *output,
               ushort *output_length)

{
  ushort uVar1;
  uint32_t puVar2;
  puVar2 = 0xfebeb800u;
  if (control_type == '\x01') {
    ((void)(1), (void)(unused_input), (void)(unused_input_length), FUN_00035aa2());
    ((void)(0x44), thunk_FUN_000b9320());
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x3663))))) = 1;
    uVar1 = 0;
  }
  else {
    if (control_type != '\x03') {
      return 7;
    }
    *output = DAT_febe819d;
    uVar1 = 1;
  }
  *output_length = uVar1;
  return 0;
}



/* Raw501D0..50212;819Ainhibit,startFFFFpayload,819E==1duplicate;noinputlengthconsumed. */

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



/* start calls518E0 operation5 producer, translates return through4D118,marks result1 on0,len0. Idle
   producer immediately5551A history initialization then lifecycle85;busy producer deduplicates5/6
   in four slots or writes producer slot (no full acknowledgement). Parent-owned5F91C/5F972
   scheduler and51A98 later apply global AA/A5 hold, then85 needs89C4==0 for selector3
   success,otherwise failure20;dispatcher51A12 may start queued request afterwards. No persistent
   success is implied by immediate callback return0. Raw500AE..50886:
   R6zxbcontrols1/2/3;R9output;fifthargumentatentrySP+0pointsu16length(st.h);return32-bitR10;inputargumentsunusedbytheseactions.
   Result requestsproduce1byte;starts/stops0exceptcapabilitystarts32. */

uint f33_diag_routine_1004_request_history_rewrite
               (uchar control_type,uchar *unused_input,ushort unused_input_length,uchar *output,
               ushort *output_length)

{
  ushort uVar1;
  int application_status;
  uint uVar2;
  
  if (control_type == '\x01') {
    application_status = ((void)(1), (void)(unused_input), (void)(unused_input_length), FUN_000518e0());
    uVar2 = f33_diag_translate_application_request_status(application_status);
    if (uVar2 == 0) {
      DAT_febe819e = '\x01';
    }
    uVar1 = 0;
  }
  else {
    if (control_type != '\x03') {
      return 7;
    }
    uVar2 = 0;
    *output = DAT_febe819e;
    uVar1 = 1;
  }
  *output_length = uVar1;
  return uVar2;
}



/* startB8DDA(0) initializes B438=11,counterB440=0 (with shared dependent reinitializers
   whenB439!=11),result1,len0. B8D9C(0) checksB439 andB43A, notB438. B8B38 waits five status
   wordsB2D4/B26C/B324/B490/B352 high bytes88;all low bytes22=>group22 and selector4
   success;otherwisegroup44 andfail20. Waiting timeout setsB43C=5A but does not directly
   acknowledge. Control type3 returns result byte,len1. Raw500AE..50886:
   R6zxbcontrols1/2/3;R9output;fifthargumentatentrySP+0pointsu16length(st.h);return32-bitR10;inputargumentsunusedbytheseactions.
   Result requestsproduce1byte;starts/stops0exceptcapabilitystarts32. */

uint f33_diag_routine_1007_restart_lifecycle_group0
               (uchar control_type,uchar *unused_input,ushort unused_input_length,uchar *output,
               ushort *output_length)

{
  ushort uVar1;
  uint32_t puVar2;
  puVar2 = 0xfebeb800u;
  if (control_type == '\x01') {
    ((void)(0), (void)(unused_input), (void)(unused_input_length), thunk_FUN_000b8dda());
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x3661))))) = 1;
    uVar1 = 0;
  }
  else {
    if (control_type != '\x03') {
      return 7;
    }
    *output = DAT_febe819f;
    uVar1 = 1;
  }
  *output_length = uVar1;
  return 0;
}



/* startB8E52 restarts five dependencies,setsB43A=11,counterB442=0,result1,len0. B8CCE waits
   B2CE/B25C/B302/B462/B334;all22=>selector5 success andgroup22;all no longer11 but not
   all22=>failure20 andgroup44;otherwise waits withB43D timeout flag. Results byte,len1.
   Raw500AE..50886:
   R6zxbcontrols1/2/3;R9output;fifthargumentatentrySP+0pointsu16length(st.h);return32-bitR10;inputargumentsunusedbytheseactions.
   Result requestsproduce1byte;starts/stops0exceptcapabilitystarts32. */

uint f33_diag_routine_1008_restart_lifecycle_group2
               (uchar control_type,uchar *unused_input,ushort unused_input_length,uchar *output,
               ushort *output_length)

{
  ushort uVar1;
  uint32_t puVar2;
  puVar2 = 0xfebeb800u;
  if (control_type == '\x01') {
    ((void)(1), (void)(unused_input), (void)(unused_input_length), thunk_FUN_000b8e52());
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x3660))))) = 1;
    uVar1 = 0;
  }
  else {
    if (control_type != '\x03') {
      return 7;
    }
    *output = DAT_febe81a0;
    uVar1 = 1;
  }
  *output_length = uVar1;
  return 0;
}



/* 819A!=1;start result!=1 else8;results admitted;other7. No additional feature/E958 gate in THIS
   F33 raw precondition! Do not transfer Sienna semantics. Raw50152..5081E
   zxbR6andfullR10return0/5/7/8;gate details in companion recovery rows. */

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



/* startB69C6 resets B6990/B692A and setsB2C9=11,result1,len0. B6658 waitsB2C8/B2CA not22,thenB65CA
   queues selector103 with first8 zero,last8 FF;state22 pollsFF0C4(103):exact10
   success=>B2C9=44,selector6 success plus reinit;high20 remains pending;other=>state88 and
   selector6 fail20. Results byte,len1. Admission, RAM reset and asynchronous selector103
   persistence are distinct. Raw500AE..50886:
   R6zxbcontrols1/2/3;R9output;fifthargumentatentrySP+0pointsu16length(st.h);return32-bitR10;inputargumentsunusedbytheseactions.
   Result requestsproduce1byte;starts/stops0exceptcapabilitystarts32. */

uint f33_diag_routine_1009_reset_record103
               (uchar control_type,uchar *unused_input,ushort unused_input_length,uchar *output,
               ushort *output_length)

{
  ushort uVar1;
  uint32_t puVar2;
  puVar2 = 0xfebeb800u;
  if (control_type == '\x01') {
    ((void)(1), (void)(unused_input), (void)(unused_input_length), thunk_FUN_000b69c6());
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x365f))))) = 1;
    uVar1 = 0;
  }
  else {
    if (control_type != '\x03') {
      return 7;
    }
    *output = DAT_febe81a1;
    uVar1 = 1;
  }
  *output_length = uVar1;
  return 0;
}



/* Raw503A0..AA819A==1?5:0. */

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



/* start4D308(1100,out,32) builds11xx RID support bitmap,result2,outlen32;results byte,len1;other7.
   Raw500AE..50886:
   R6zxbcontrols1/2/3;R9output;fifthargumentatentrySP+0pointsu16length(st.h);return32-bitR10;inputargumentsunusedbytheseactions.
   Result requestsproduce1byte;starts/stops0exceptcapabilitystarts32. */

uint f33_diag_routine_1100_capabilities
               (uchar control_type,uchar *unused_input,ushort unused_input_length,uchar *output,
               ushort *output_length)

{
  uint32_t puVar1;
  uint uVar2;
  
  puVar1 = 0xfebeb800u;
  uVar2 = 0;
  if (control_type == '\x01') {
    FUN_0004d308(0x1100, camry_host_addr(output), 0x20);
    *output_length = 0x20;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x365e))))) = 2;
  }
  else if (control_type == '\x03') {
    *output = DAT_febe81a2;
    *output_length = 1;
  }
  else {
    uVar2 = 7;
  }
  return uVar2;
}



/* 819A!=1;start35A06()==1 and81A6!=1,then81A3!=1;5 vs8.35A06 raw
   gatesE81A==1,66B8>=30E32,E892<=30E34,80A5/80A0==0,saturatingabs66A8<512,clear6764&81FF. Results
   allowed;other7. Raw50152..5081E zxbR6andfullR10return0/5/7/8;gate details in companion recovery
   rows. */

uint f33_diag_routine_1103_admit(uchar control_type)

{
  int iVar1;
  uint uVar2;
  
  if (DAT_febe819a == '\x01') {
LAB_0005042c:
    uVar2 = 5;
  }
  else {
    if (control_type == '\x01') {
      iVar1 = FUN_00035a06();
      if ((iVar1 != 1) || (DAT_febe81a6 == '\x01')) goto LAB_0005042c;
      if (DAT_febe81a3 == '\x01') {
        return 8;
      }
    }
    else if (control_type != '\x03') {
      return 7;
    }
    uVar2 = 0;
  }
  return uVar2;
}



/* start35A96 sets6AE2=11 andreturns2;callback converts to0,result1,len0.357C0 later
   requestsB3224(1),sets6ADD=88 on queued-1 or reportsselector8 failure. Existing
   family0500\u21920522 acquisition, selector100 learned quad+marker and service cleanup ownership
   in \u00a777.24 applies. This is not direct physical acquisition or immediate persistence. Results
   byte,len1. Raw500AE..50886:
   R6zxbcontrols1/2/3;R9output;fifthargumentatentrySP+0pointsu16length(st.h);return32-bitR10;inputargumentsunusedbytheseactions.
   Result requestsproduce1byte;starts/stops0exceptcapabilitystarts32. Existing family0500→0522
   acquisition, selector100 learned quad+marker and service cleanup ownership in §77.24 applies. */

uint f33_diag_routine_1103_request_service1
               (uchar control_type,uchar *unused_input,ushort unused_input_length,uchar *output,
               ushort *output_length)

{
  ushort uVar1;
  uint uVar2;
  
  if (control_type == '\x01') {
    uVar2 = ((void)(1), (void)(unused_input), (void)(unused_input_length), FUN_00035a96());
    if (uVar2 == 2) {
      uVar2 = 0;
      DAT_febe81a3 = '\x01';
    }
    uVar1 = 0;
  }
  else {
    if (control_type != '\x03') {
      return 7;
    }
    uVar2 = 0;
    *output = DAT_febe81a3;
    uVar1 = 1;
  }
  *output_length = uVar1;
  return uVar2;
}



/* 819A!=1;start unsignedE892<=0200,thenresult!=1 else8;results allowed;other7. Raw50152..5081E
   zxbR6andfullR10return0/5/7/8;gate details in companion recovery rows. */

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



/* startB524A invokesB5EC6/B707A/B8FA8 andsetsB214=11,result1,len0. B51BE succeeds
   onlyB311/B471/B256 all44\u2192group22 andselector9 success;when none remain11/22 but
   notall44\u2192group44 andfail20;otherwise waits. No local callback persistence/done assumption.
   Results byte,len1. Raw500AE..50886:
   R6zxbcontrols1/2/3;R9output;fifthargumentatentrySP+0pointsu16length(st.h);return32-bitR10;inputargumentsunusedbytheseactions.
   Result requestsproduce1byte;starts/stops0exceptcapabilitystarts32. B51BE succeeds
   onlyB311/B471/B256 all44→group22 andselector9 success;when none remain11/22 but
   notall44→group44 andfail20;otherwise waits. */

uint f33_diag_routine_1106_restart_lifecycle_groups
               (uchar control_type,uchar *unused_input,ushort unused_input_length,uchar *output,
               ushort *output_length)

{
  ushort uVar1;
  uint32_t puVar2;
  puVar2 = 0xfebeb800u;
  if (control_type == '\x01') {
    ((void)(1), (void)(unused_input), (void)(unused_input_length), thunk_FUN_000b524a());
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x365c))))) = 1;
    uVar1 = 0;
  }
  else {
    if (control_type != '\x03') {
      return 7;
    }
    *output = DAT_febe81a4;
    uVar1 = 1;
  }
  *output_length = uVar1;
  return 0;
}



/* 819A!=1;start result!=1 else8;no local speed gate;results allowed;other7. Raw50152..5081E
   zxbR6andfullR10return0/5/7/8;gate details in companion recovery rows. */

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



/* start517DC operation2 producer and4D118;on0 result1,len0. Idle51788 performs multi-owner
   diagnostic reset/preservation then lifecycle82;busy deduplicates2/6 or writes producer slot,no
   capacity acknowledgement. Existing diagnostic scheduler51A98 requires all four persistence
   phaseszero for82 success;AA/A5 anygroup holds;other terminal phase yieldsfail20.
   Aggregateoperation86 canack both selector3/A via4D0E8. Results byte,len1. Raw500AE..50886:
   R6zxbcontrols1/2/3;R9output;fifthargumentatentrySP+0pointsu16length(st.h);return32-bitR10;inputargumentsunusedbytheseactions.
   Result requestsproduce1byte;starts/stops0exceptcapabilitystarts32. */

uint f33_diag_routine_1108_request_checkpoint_reset
               (uchar control_type,uchar *unused_input,ushort unused_input_length,uchar *output,
               ushort *output_length)

{
  ushort uVar1;
  int application_status;
  uint uVar2;
  
  if (control_type == '\x01') {
    application_status = ((void)(1), (void)(unused_input), (void)(unused_input_length), FUN_000517dc());
    uVar2 = f33_diag_translate_application_request_status(application_status);
    if (uVar2 == 0) {
      DAT_febe81a5 = '\x01';
    }
    uVar1 = 0;
  }
  else {
    if (control_type != '\x03') {
      return 7;
    }
    uVar2 = 0;
    *output = DAT_febe81a5;
    uVar1 = 1;
  }
  *output_length = uVar1;
  return uVar2;
}



/* 819A!=1;startE892<=0200,81A3!=1,80A0==0,80A5==0,E81E==0,E884!=5A,E88A!=5A,then ownresult!=1
   (8);otherwise5. Results allowed;other7. Proof5057A..5C8. Raw50152..5081E
   zxbR6andfullR10return0/5/7/8;gate details in companion recovery rows. */

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



/* 819A!=1. startB84B8(kind1) qualified,81A6!=1,E884/E88A!=5A,ownresult!=1 (8). stopresult!=0
   else8;results accepted;other7. Kind1 is retainedR6 at50646,not absentargument. Raw50152..5081E
   zxbR6andfullR10return0/5/7/8;gate details in companion recovery rows. */

uint f33_diag_routine_110a_admit(uchar control_type)

{
  uint32_t puVar1;
  uint uVar2;
  
  puVar1 = 0xfebeb800u;
  if (DAT_febe819a == '\x01') {
    return 5;
  }
  if (control_type == '\x01') {
    uVar2 = f33_qualify_service_admission('\x01');
    if ((((uVar2 == 0) || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x365a))))) == '\x01')) || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x3084))))) == 'Z')) ||
       ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x308a))))) == 'Z')) {
      return 5;
    }
    if (DAT_febe81a7 == '\x01') {
      return 8;
    }
  }
  else if (control_type == '\x02') {
    if (DAT_febe81a7 == '\0') {
      return 8;
    }
  }
  else if (control_type != '\x03') {
    return 7;
  }
  return 0;
}



/* startB3224(2),4D118;queued=>callback0,B85D0 clearsstoplatch,result1,len0. stop whenrunning1
   callsB85BC (B3DD=5A,B3CB=0) but leavesresult1;when terminal nonzero clearsresult0;len0. Existing
   family0520 kind1 engine, B303E completion and forcedexitB3194 apply. Results byte,len1.
   Raw500AE..50886:
   R6zxbcontrols1/2/3;R9output;fifthargumentatentrySP+0pointsu16length(st.h);return32-bitR10;inputargumentsunusedbytheseactions.
   Result requestsproduce1byte;starts/stops0exceptcapabilitystarts32. */

uint f33_diag_routine_110a_control_service2
               (uchar control_type,uchar *unused_input,ushort unused_input_length,uchar *output,
               ushort *output_length)

{
  ushort uVar1;
  int application_status;
  uint uVar2;
  
  if (control_type == '\x01') {
    application_status = f33_queue_application_service('\x02');
    uVar2 = f33_diag_translate_application_request_status(application_status);
    if (uVar2 == 2) {
      uVar2 = 0;
      thunk_FUN_000b85d0();
      DAT_febe81a7 = '\x01';
    }
    uVar1 = 0;
  }
  else if (control_type == '\x02') {
    if (DAT_febe81a7 == '\x01') {
      ((void)(2), (void)(unused_input), (void)(unused_input_length), thunk_FUN_000b85bc());
    }
    else {
      DAT_febe81a7 = '\0';
    }
    uVar2 = 0;
    uVar1 = 0;
  }
  else {
    if (control_type != '\x03') {
      return 7;
    }
    uVar2 = 0;
    *output = DAT_febe81a7;
    uVar1 = 1;
  }
  *output_length = uVar1;
  return uVar2;
}



/* Raw50702mov0,R10;50704jmpLP. */

uint f33_diag_routine_110b_admit_noop(void)

{
  return 0;
}



/* Raw50706mov0,R10;50708jmpLP;NOoutputlengthor81A8resultaccess. */

uint f33_diag_routine_110b_action_noop(void)

{
  return 0;
}



/* 819A!=1;startB84B8(kind2),81A6!=1,E884/E88A!=5A,andE889!=0;ownresult!=1 else8. E889 is published
   ID2 completionB3CA,not generic NvM validity. No stop support. Raw50152..5081E
   zxbR6andfullR10return0/5/7/8;gate details in companion recovery rows. */

uint f33_diag_routine_110c_admit(uchar control_type)

{
  uint32_t puVar1;
  uint uVar2;
  
  puVar1 = 0xfebeb800u;
  if (DAT_febe819a == '\x01') {
LAB_00050758:
    uVar2 = 5;
  }
  else {
    if (control_type == '\x01') {
      uVar2 = f33_qualify_service_admission('\x02');
      if ((((uVar2 == 0) || (DAT_febe81a6 == '\x01')) || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x308a))))) == 'Z')) ||
         (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x3084))))) == 'Z' || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x3089))))) == '\0')))) goto LAB_00050758;
      if (DAT_febe81a9 == '\x01') {
        return 8;
      }
    }
    else if (control_type != '\x03') {
      return 7;
    }
    uVar2 = 0;
  }
  return uVar2;
}



/* startB3224(3),4D118 queued=>callback0,result1,len0. Existing0520 kind2 preserves center/extrema
   andresumestracking;B303E emitsselectorE;forcedexit fails (no stop latch). Results byte,len1.
   Raw500AE..50886:
   R6zxbcontrols1/2/3;R9output;fifthargumentatentrySP+0pointsu16length(st.h);return32-bitR10;inputargumentsunusedbytheseactions.
   Result requestsproduce1byte;starts/stops0exceptcapabilitystarts32. */

uint f33_diag_routine_110c_request_service3
               (uchar control_type,uchar *unused_input,ushort unused_input_length,uchar *output,
               ushort *output_length)

{
  ushort uVar1;
  int application_status;
  uint uVar2;
  
  if (control_type == '\x01') {
    application_status = f33_queue_application_service('\x03');
    uVar2 = f33_diag_translate_application_request_status(application_status);
    if (uVar2 == 2) {
      uVar2 = 0;
      DAT_febe81a9 = '\x01';
    }
    uVar1 = 0;
  }
  else {
    if (control_type != '\x03') {
      return 7;
    }
    uVar2 = 0;
    *output = DAT_febe81a9;
    uVar1 = 1;
  }
  *output_length = uVar1;
  return uVar2;
}



/* 819A!=1;startB84B8(kind3),81A6!=1,E884/E88A!=5A,ownresult!=1 else8. stopresult!=0 else8;results
   allowed. Raw50152..5081E zxbR6andfullR10return0/5/7/8;gate details in companion recovery rows. */

uint f33_diag_routine_110d_admit(uchar control_type)

{
  uint32_t puVar1;
  uint uVar2;
  
  puVar1 = 0xfebeb800u;
  if (DAT_febe819a == '\x01') {
    return 5;
  }
  if (control_type == '\x01') {
    uVar2 = f33_qualify_service_admission('\x03');
    if ((((uVar2 == 0) || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x365a))))) == '\x01')) || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x308a))))) == 'Z')) ||
       ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x3084))))) == 'Z')) {
      return 5;
    }
    if (DAT_febe81aa == '\x01') {
      return 8;
    }
  }
  else if (control_type == '\x02') {
    if (DAT_febe81aa == '\0') {
      return 8;
    }
  }
  else if (control_type != '\x03') {
    return 7;
  }
  return 0;
}



/* startB3224(4),4D118 queued=>callback0,B85CA clearsstoplatch,result1,len0. stoprunning1 callsB85AE
   settingB3DC=5A,B3CB=0,doesnotterminallycompleteresult;terminalnonzero clearsresult0.
   Existing0520kind3 andB303E/forcedexit cleanup apply. Results byte,len1. Raw500AE..50886:
   R6zxbcontrols1/2/3;R9output;fifthargumentatentrySP+0pointsu16length(st.h);return32-bitR10;inputargumentsunusedbytheseactions.
   Result requestsproduce1byte;starts/stops0exceptcapabilitystarts32. */

uint f33_diag_routine_110d_control_service4
               (uchar control_type,uchar *unused_input,ushort unused_input_length,uchar *output,
               ushort *output_length)

{
  ushort uVar1;
  int application_status;
  uint uVar2;
  
  if (control_type == '\x01') {
    application_status = f33_queue_application_service('\x04');
    uVar2 = f33_diag_translate_application_request_status(application_status);
    if (uVar2 == 2) {
      uVar2 = 0;
      thunk_FUN_000b85ca();
      DAT_febe81aa = '\x01';
    }
    uVar1 = 0;
  }
  else if (control_type == '\x02') {
    if (DAT_febe81aa == '\x01') {
      ((void)(2), (void)(unused_input), (void)(unused_input_length), thunk_FUN_000b85ae());
    }
    else {
      DAT_febe81aa = '\0';
    }
    uVar2 = 0;
    uVar1 = 0;
  }
  else {
    if (control_type != '\x03') {
      return 7;
    }
    uVar2 = 0;
    *output = DAT_febe81aa;
    uVar1 = 1;
  }
  *output_length = uVar1;
  return uVar2;
}



/* Alwayspreservesrunning1;argument5Aadditionallypreservesindex2.4D582calls0. */

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



/* Onlyselector<16andcurrentresult1;status10noop,0\u21922,30\u21920,other\u21923.8-bitselector/statusmasking;no
   meaningfulreturn.
   Onlyselector<16andcurrentresult1;status10noop,0→2,30→0,other→3.8-bitselector/statusmasking;no
   meaningfulreturn. */

void f33_diag_routine_publish_terminal_result(uchar result_selector,uchar completion_status)

{
  undefined1 uVar1;
  uint uVar2;
  
  uVar2 = (uint)result_selector;
  if (uVar2 < 0x10) {
    if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe819bu + (uint32_t)(uVar2) * 1u)))) == '\x01') && (completion_status != '\x10')) {
      if (completion_status == '\0') {
        uVar1 = 2;
      }
      else if (completion_status == '0') {
        uVar1 = 0;
      }
      else {
        uVar1 = 3;
      }
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe819bu + (uint32_t)(uVar2) * 1u)))) = uVar1;
    }
  }
  return;
}



/* Constant source: return 0; shape-classified from the canonical corpus. Callers receive this
   literal directly; its meaning is not recovered. */

undefined4 f33_return_const_0_50900(void)

{
  return 0;
}



/* Store8197=5A only for selection2, otherwise0. Does not clear events, captures, classifiers or
   control actions; later49E22 and58074 publish consequences. */

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



/* Selector1 formats enabled IDs,2 event data,3 selected event record. Bounded catalogue2AB70 has51
   populated IDs in64 slots. Map signed helper errors-4/-1 to4/6, otherwise10; do not assign OEM
   names from ID/type. */

uint f33_serialize_selected_proprietary_event(uchar *output,ushort *length)

{
  uint uVar1;
  uint uVar2;
  
  if (((uintptr_t)(output)!=(uintptr_t)((uchar *)0x0)) && ((uintptr_t)(length)!=(uintptr_t)((ushort *)0x0))) {
    uVar2 = (uint)*length;
    if (DAT_febe81ad != 0) {
      if (DAT_febe81ad == 1) {
        uVar1 = FUN_000557c4(camry_host_addr(output), uVar2);
      }
      else if (DAT_febe81ad < 3) {
        uVar1 = FUN_0005592c(DAT_febe81ba, camry_host_addr(output), uVar2);
      }
      else {
        if (DAT_febe81ad != 3) {
          return 10;
        }
        uVar1 = FUN_00055c6e(DAT_febe81ba, DAT_febe81bc, camry_host_addr(output), uVar2);
      }
      if ((-1 < (int)uVar1) &&
         ((int)(uVar1 - uVar2) < 0 != ((int)uVar1 < 0 && -1 < (int)(uVar1 - uVar2)) ||
          uVar1 == uVar2)) {
        *length = (ushort)uVar1;
        return 0;
      }
      if (uVar1 == 0xfffffffc) {
        return 4;
      }
      if (uVar1 == 0xffffffff) {
        return 6;
      }
    }
  }
  return 10;
}



/* Write exact count242 and return2927C, including leading0100/4FB10. Metadata membership is
   distinct from kind0 plus current availability admission. */

F33DidPublicationMetadata * f33_get_did_publication_metadata(ushort *count)

{
  *count = 0xf2;
  return f33_did_publication_metadata;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_509a0(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_509a2(void)

{
  return;
}



/* E826=33/11 or7BBA=5A clears81CC; otherwise5A. Separate crypto availability81CD additionally
   requires7F97!=5A, with transition cleanup5704E. The two publications are not interchangeable. */

void f33_refresh_diagnostic_application_availability(void)

{
  char cVar1;
  uint32_t puVar2;
  undefined1 uVar3;
  undefined1 uVar4;
  
  cVar1 = DAT_febe81cd;
  puVar2 = 0xfebeb800u;
  if (((DAT_febee826 == '3') || (DAT_febee826 == '\x11')) || (DAT_febe7bba == 'Z')) {
    uVar3 = 0;
  }
  else {
    uVar3 = 0x5a;
    uVar4 = 0x5a;
    if (DAT_febe7f97 != 'Z') {
      puVar2 = 0xfebeb800u;
      FUN_0006a174(0x5a);
      uVar3 = uVar4;
      if (((int8_t)cVar1) == -0x5b) {
        FUN_0005704e();
      }
      goto LAB_000509f6;
    }
  }
  FUN_0006a174(0xa5);
  uVar4 = 0xa5;
LAB_000509f6:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x3633))))) = uVar4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x3634))))) = uVar3;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_50a02(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_50a04(void)

{
  return;
}



/* Copy5F26/5F27 to81D0/81D1. Their producer66932 copies cached380A/380B; no physical error identity
   is inferred. */

void f33_snapshot_acquisition_status_flags(void)

{
  DAT_febe81d0 = DAT_febe5f26;
  DAT_febe81d1 = DAT_febe5f27;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_50a18(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_50a1a(void)

{
  return;
}



/* Copy5EEA/C/E/5EF0 to81D6/8/A/C; publish valid markers81D4/5 as5F26/27 XOR5A. Only source byte0
   produces the exact5A marker admitted by range predicates. */

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



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_50a4e(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_50a50(void)

{
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



void FUN_00050ae2(void)

{
  if (DAT_febe8a1c == 'Z') {
    FUN_00050a52();
    FUN_00050a9a();
  }
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_50afc(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_50afe(void)

{
  return;
}



/* Constant-block fill: 12 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

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



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_50b22(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_50b24(void)

{
  return;
}



/* Cell-block copy: 15 whole-cell assignments with a fixed source-to-destination mapping;
   shape-verified. The mapping is per-cell; cell meanings are not recovered. */

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



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_50b66(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_50b68(void)

{
  return;
}



/* Copy fast5EC8..5EDE banks into application822C..8242: group first triples ->8238/823E
   reference-side inputs; group last triples ->822C/8232 measured-side inputs. No validity/freshness
   test.5DE82 mode>FF admits copy, mode>100 admits downstream conditioning. */

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



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_50bb8(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_50bba(void)

{
  return;
}



/* Publish first two cached serial fields shiftedleft2, third unchanged; expand eight cached
   wrapping counters5F29..30 to interleaved application8244..4B; independently copy
   masks5F18/1A/22/24 ->8258/5A/5C/5E. These mask fields come from66932/6294E, not629A2, and may be
   another generation. No per-call validity gate. */

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



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_50c36(void)

{
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



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_50c96(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_50c98(void)

{
  return;
}



/* Publish62CD4 result at8294; expand cached local3838/383A/383C bits into8278..8292 and
   packed8298,clear829C. In particular8284/8282/8283/8281 reflect383A bits3/9/2/8. These are
   software cached status-link fields, not CAN wire joins or independent freshness proof. */

void f33_snapshot_local_status_link_flags(void)

{
  ushort uVar1;
  ushort uVar2;
  char cVar3;
  uint32_t puVar4;
  undefined4 uVar5;
  uint uVar6;
  uint uVar7;
  uint uVar8;
  uint uVar9;
  uint uVar10;
  uint uVar11;
  uint uVar12;
  uint uVar13;
  uint uVar14;
  uint uVar15;
  uint uVar16;
  uint uVar17;
  uint uVar18;
  uint uVar19;
  uint uVar20;
  uint uVar21;
  uint uVar22;
  uint uVar23;
  uint uVar24;
  uint uVar25;
  uint uVar26;
  uint uVar27;
  uint uVar28;
  uint uVar29;
  uint uVar30;
  uint uVar31;
  uint uVar32;
  
  puVar4 = 0xfebeb800u;
  uVar5 = FUN_00062cd4();
  uVar1 = (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + -0x7fc8))));
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar4 + -0x356c)))) = uVar5;
  cVar3 = '\0';
  if ((uVar1 >> 6 & 1) != 0) {
    cVar3 = 'Z';
  }
  uVar32 = 0;
  if (cVar3 != '\0') {
    uVar32 = 0x20;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3588))))) = cVar3;
  cVar3 = '\0';
  if ((uVar1 >> 4 & 1) != 0) {
    cVar3 = 'Z';
  }
  uVar20 = 0;
  if (cVar3 != '\0') {
    uVar20 = 0x40000000;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3587))))) = cVar3;
  cVar3 = '\0';
  if ((uVar1 >> 2 & 1) != 0) {
    cVar3 = 'Z';
  }
  uVar21 = 0;
  if (cVar3 != '\0') {
    uVar21 = 0x10000000;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3586))))) = cVar3;
  cVar3 = '\0';
  if ((uVar1 >> 5 & 1) != 0) {
    cVar3 = 'Z';
  }
  uVar22 = 0;
  if (cVar3 != '\0') {
    uVar22 = 0x80000000;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3585))))) = cVar3;
  cVar3 = '\0';
  if ((uVar1 >> 3 & 1) != 0) {
    cVar3 = 'Z';
  }
  uVar23 = 0;
  if (cVar3 != '\0') {
    uVar23 = 0x20000000;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3584))))) = cVar3;
  uVar2 = (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + -0x7fc6))));
  cVar3 = '\0';
  if ((uVar2 >> 0xc & 1) != 0) {
    cVar3 = 'Z';
  }
  uVar6 = 0;
  if (cVar3 != '\0') {
    uVar6 = 0x4000000;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3583))))) = cVar3;
  cVar3 = '\0';
  if ((uVar2 >> 0xd & 1) != 0) {
    cVar3 = 'Z';
  }
  uVar7 = 0;
  if (cVar3 != '\0') {
    uVar7 = 0x8000000;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3582))))) = cVar3;
  cVar3 = '\0';
  if ((uVar1 & 1) != 0) {
    cVar3 = 'Z';
  }
  uVar8 = 0;
  if (cVar3 != '\0') {
    uVar8 = 0x1000000;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3581))))) = cVar3;
  cVar3 = '\0';
  if ((uVar1 >> 1 & 1) != 0) {
    cVar3 = 'Z';
  }
  uVar24 = 0;
  if (cVar3 != '\0') {
    uVar24 = 0x2000000;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3580))))) = cVar3;
  cVar3 = '\0';
  if ((uVar2 >> 8 & 1) != 0) {
    cVar3 = 'Z';
  }
  uVar25 = 0;
  if (cVar3 != '\0') {
    uVar25 = 0x400000;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x357f))))) = cVar3;
  cVar3 = '\0';
  if ((uVar2 >> 9 & 1) != 0) {
    cVar3 = 'Z';
  }
  uVar26 = 0;
  if (cVar3 != '\0') {
    uVar26 = 0x800000;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x357e))))) = cVar3;
  cVar3 = '\0';
  if ((uVar2 >> 2 & 1) != 0) {
    cVar3 = 'Z';
  }
  uVar27 = 0;
  if (cVar3 != '\0') {
    uVar27 = 0x100000;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x357d))))) = cVar3;
  cVar3 = '\0';
  if ((uVar2 >> 3 & 1) != 0) {
    cVar3 = 'Z';
  }
  uVar28 = 0;
  if (cVar3 != '\0') {
    uVar28 = 0x200000;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x357c))))) = cVar3;
  uVar1 = (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + -0x7fc4))));
  cVar3 = '\0';
  if ((uVar1 >> 0xb & 1) != 0) {
    cVar3 = 'Z';
  }
  uVar9 = 0;
  if (cVar3 != '\0') {
    uVar9 = 0x80000;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x357b))))) = cVar3;
  cVar3 = '\0';
  if ((uVar1 >> 10 & 1) != 0) {
    cVar3 = 'Z';
  }
  uVar10 = 0;
  if (cVar3 != '\0') {
    uVar10 = 0x40000;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x357a))))) = cVar3;
  cVar3 = '\0';
  if ((uVar1 >> 9 & 1) != 0) {
    cVar3 = 'Z';
  }
  uVar11 = 0;
  if (cVar3 != '\0') {
    uVar11 = 0x20000;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3579))))) = cVar3;
  cVar3 = '\0';
  if ((uVar1 >> 8 & 1) != 0) {
    cVar3 = 'Z';
  }
  uVar12 = 0;
  if (cVar3 != '\0') {
    uVar12 = 0x10000;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3578))))) = cVar3;
  cVar3 = '\0';
  if ((uVar1 >> 7 & 1) != 0) {
    cVar3 = 'Z';
  }
  uVar13 = 0;
  if (cVar3 != '\0') {
    uVar13 = 0x8000;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3577))))) = cVar3;
  cVar3 = '\0';
  if ((uVar1 >> 6 & 1) != 0) {
    cVar3 = 'Z';
  }
  uVar14 = 0;
  if (cVar3 != '\0') {
    uVar14 = 0x4000;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3576))))) = cVar3;
  cVar3 = '\0';
  if ((uVar1 >> 5 & 1) != 0) {
    cVar3 = 'Z';
  }
  uVar15 = 0;
  if (cVar3 != '\0') {
    uVar15 = 0x2000;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3575))))) = cVar3;
  cVar3 = '\0';
  if ((uVar1 >> 4 & 1) != 0) {
    cVar3 = 'Z';
  }
  uVar16 = 0;
  if (cVar3 != '\0') {
    uVar16 = 0x1000;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3574))))) = cVar3;
  cVar3 = '\0';
  if ((uVar1 >> 3 & 1) != 0) {
    cVar3 = 'Z';
  }
  uVar17 = 0;
  if (cVar3 != '\0') {
    uVar17 = 0x800;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3573))))) = cVar3;
  cVar3 = '\0';
  if ((uVar1 >> 2 & 1) != 0) {
    cVar3 = 'Z';
  }
  uVar18 = 0;
  if (cVar3 != '\0') {
    uVar18 = 0x400;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3572))))) = cVar3;
  cVar3 = '\0';
  if ((uVar1 >> 1 & 1) != 0) {
    cVar3 = 'Z';
  }
  uVar19 = 0;
  if (cVar3 != '\0') {
    uVar19 = 0x200;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3571))))) = cVar3;
  cVar3 = '\0';
  if ((uVar1 & 1) != 0) {
    cVar3 = 'Z';
  }
  uVar29 = 0;
  if (cVar3 != '\0') {
    uVar29 = 0x100;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3570))))) = cVar3;
  cVar3 = '\0';
  if ((uVar2 >> 5 & 1) != 0) {
    cVar3 = 'Z';
  }
  uVar30 = 0;
  if (cVar3 != '\0') {
    uVar30 = 0x80;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x356f))))) = cVar3;
  cVar3 = '\0';
  if ((uVar2 >> 4 & 1) != 0) {
    cVar3 = 'Z';
  }
  uVar31 = 0;
  if (cVar3 != '\0') {
    uVar31 = 0x40;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x356e))))) = cVar3;
  DAT_febe829c = 0;
  DAT_febe8298 = uVar32 | uVar20 | uVar21 | uVar22 | uVar23 | uVar6 | uVar7 | uVar8 | uVar24 |
                 uVar25 | uVar26 | uVar27 | uVar28 | uVar9 | uVar10 | uVar11 | uVar12 | uVar13 |
                 uVar14 | uVar15 | uVar16 | uVar17 | uVar18 | uVar19 | uVar29 | uVar30 | uVar31;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_50fac(void)

{
  return;
}



void FUN_00050fae(void)

{
  DAT_febe82ca = f33_classifier_primary_age_threshold;
  DAT_febe82cc = f33_classifier_secondary_age_threshold;
  DAT_febe82ce = f33_classifier_retained_age_threshold;
  return;
}



/* Descriptor class2/4/8/0F/10/20/40/80/F0 selects its16-bit counter and class-specific latches.
   Counter increments wrap16; not saturating. Unknown classes make no update. Descriptor classes
   select wrapping16-bit counters and latched flags under PMRFF00; unknown class does nothing.
   Class2 counter82BA and flags82A3/A5.bit0 are distinct from control fault records. */

void f33_assert_diagnostic_classifier(uchar classification)

{
  uint32_t puVar1;
  uint saved_mask;
  
  puVar1 = 0xfebeb800u;
  saved_mask = f33_priority_mask_enter(0xff00);
  if (classification == '\x02') {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x355d))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x355d))))) | 1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x355b))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x355b))))) | 1;
    (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x3546)))) = (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x3546)))) + 1;
  }
  else {
    if (classification != '\x04') {
      if (classification == '\b') {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x355c))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x355c))))) | 8;
        (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x3542)))) = (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x3542)))) + 1;
      }
      else if (classification == '\x0f') {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x355c))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x355c))))) | 4;
        (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x3540)))) = (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x3540)))) + 1;
      }
      else if (classification == '\x10') {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x355c))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x355c))))) | 0x10;
        (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x353e)))) = (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x353e)))) + 1;
      }
      else {
        if (classification == ' ') {
          (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x353c)))) = (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x353c)))) + 1;
        }
        else {
          if (classification == '@') {
            (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x355c))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x355c))))) | 0x40;
            (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x353a)))) = (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x353a)))) + 1;
            goto LAB_0005107a;
          }
          if (classification == 0x80) {
            (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x3538)))) = (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x3538)))) + 1;
            goto LAB_000510ac;
          }
          if (classification != 0xf0) goto LAB_000510ac;
          (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x3530)))) = (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x3530)))) + 1;
        }
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x355c))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x355c))))) | 0x20;
      }
LAB_0005107a:
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3559))))) = 0x5a;
      goto LAB_000510ac;
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x355d))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x355d))))) | 2;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x355b))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x355b))))) | 2;
    (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x3544)))) = (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x3544)))) + 1;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x355a))))) = 0x5a;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3558))))) = 0x5a;
LAB_000510ac:
  f33_priority_mask_restore(saved_mask);
  return;
}



void FUN_000510b6(void)

{
  char cVar1;
  uint32_t puVar2;
  puVar2 = 0xfebeb800u;
  cVar1 = DAT_febe82af;
  if ((DAT_febe82af != 'Z') && (cVar1 = '\0', (DAT_febe6764 & 0x8000) != 0)) {
    puVar2 = 0xfebeb800u;
    f33_assert_diagnostic_classifier('\x02');
    cVar1 = 'Z';
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x3551))))) = cVar1;
  return;
}



/* Return/store actual R10 byte82B4. Zero latch asserts5A only for7F515A; nonzero latch clears only
   when7F51 andE827 are both zero. Caller512E4 uses nonzero, not equality5A. Real R10 byte is both
   stored82B4 and consumed by512E4. Zero latch asserts only for7F515A; nonzero latch clears only
   with7F51/E827 zero. */

uchar f33_update_classifier_status_latch(void)

{
  if (DAT_febe82b4 == '\0') {
    if (DAT_febe7f51 == 'Z') {
      DAT_febe82b4 = 'Z';
    }
    else {
      DAT_febe82b4 = '\0';
    }
  }
  else if ((DAT_febe7f51 == '\0') && (DAT_febee827 == '\0')) {
    DAT_febe82b4 = '\0';
  }
  return DAT_febe82b4;
}



/* Snapshot unsignedE8B0 before PMRFF00. Consume activity5A and reset age, then increment while
   age<=threshold. Clear whole flag group only for age>threshold andE8B0>=22170. Consumed activity
   leaves age1; already-over-threshold age holds. No class-counter decrement. Consume activity5A,
   reset then increment age; strict expiry and unsigned stagedE8B0>=22170 clear whole flag group.
   Over-threshold age holds; active counters and event bitmaps untouched. */

void f33_age_classifier_flag_group(uchar *flags,uchar *activity,ushort *age,ushort threshold)

{
  ushort uVar1;
  ushort uVar2;
  uint saved_mask;
  uchar uVar3;
  uchar uVar4;
  
  uVar1 = DAT_febee8b0;
  saved_mask = f33_priority_mask_enter(0xff00);
  uVar4 = *activity;
  uVar2 = *age;
  uVar3 = *flags;
  if (uVar4 == 'Z') {
    uVar4 = '\0';
    uVar2 = 0;
  }
  if (((threshold < uVar2) || (uVar2 = uVar2 + 1, threshold < uVar2)) &&
     (f33_classifier_age_release_threshold <= uVar1)) {
    uVar3 = '\0';
  }
  *flags = uVar3;
  *activity = uVar4;
  *age = uVar2;
  f33_priority_mask_restore(saved_mask);
  return;
}



/* Same activity/strict age contract for82A5/82A8/82CE with exact600, but noE8B0 gate. PMRFF00
   protects updates; histories and active class counts are untouched. Retained flag-group aging uses
   same consumed-marker and strict-expiry rules with600 invocations, without E8B0 gate. */

void f33_age_classifier_retained_flags(void)

{
  ushort uVar1;
  ushort uVar2;
  uint32_t puVar3;
  uint saved_mask;
  undefined1 uVar4;
  char cVar5;
  
  uVar1 = f33_classifier_retained_age_threshold;
  puVar3 = 0xfebeb800u;
  saved_mask = f33_priority_mask_enter(0xff00);
  uVar2 = (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x3532))));
  cVar5 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3558)))));
  uVar4 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x355b)))));
  if (cVar5 == 'Z') {
    cVar5 = '\0';
    uVar2 = 0;
  }
  if ((uVar1 < uVar2) || (uVar2 = uVar2 + 1, uVar1 < uVar2)) {
    uVar4 = 0;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x355b))))) = uVar4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3558))))) = cVar5;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x3532)))) = uVar2;
  f33_priority_mask_restore(saved_mask);
  return;
}



/* Snapshot flagsA4/A5, then age nonzero groups in A3,A5,A4 order. Exact thresholds 200/600/200 are
   invocation counts, not elapsed time or event-bitmap aging. SnapshotA4/A5 flags and age nonzero
   groups inA3,A5,A4 order. Individual PMR sections are not one atomic classifier snapshot. */

void f33_age_classifier_groups(void)

{
  char cVar1;
  char cVar2;
  
  cVar2 = DAT_febe82a5;
  cVar1 = DAT_febe82a4;
  if (DAT_febe82a3 != '\0') {
    f33_age_classifier_flag_group
              ((uchar *)((undefined *)camry_host_ptr(0xfebe82a3u)),((undefined *)camry_host_ptr(0xfebe82a6u)),((undefined *)camry_host_ptr(0xfebe82cau)),
               f33_classifier_primary_age_threshold);
  }
  if (cVar2 != '\0') {
    f33_age_classifier_retained_flags();
  }
  if (cVar1 != '\0') {
    f33_age_classifier_flag_group
              ((uchar *)((undefined *)camry_host_ptr(0xfebe82a4u)),((undefined *)camry_host_ptr(0xfebe82a7u)),((undefined *)camry_host_ptr(0xfebe82ccu)),
               f33_classifier_secondary_age_threshold);
  }
  return;
}



/* Return5A for zero6AF0, E8533/4, E854FF, E85511, sentinel33333333 inE91C/E924/E92C or62E12
   resultA55AA55A; otherwise0. Structural classifier priority, not a recovered OEM fault name.
   Application zero/status/sentinel predicates select structural classifier priority3. No recovered
   OEM fault identity or permission semantics. */

uint f33_classifier_selector3_predicate(void)

{
  int iVar1;
  char cVar2;
  char cVar3;
  char cVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  uint uVar9;
  
  iVar7 = DAT_febee92c;
  iVar6 = DAT_febee924;
  iVar5 = DAT_febee91c;
  cVar4 = DAT_febee855;
  cVar3 = DAT_febee854;
  cVar2 = DAT_febee853;
  iVar1 = DAT_febe6af0;
  iVar8 = FUN_00062e12();
  if (((((iVar1 == 0) || (cVar2 == '\x03' || cVar2 == '\x04')) || (((int8_t)cVar3) == -1)) ||
      ((cVar4 == '\x11' || (iVar5 == 0x33333333)))) ||
     ((iVar6 == 0x33333333 || ((iVar7 == 0x33333333 || (iVar8 == -0x5aa55aa6)))))) {
    uVar9 = 0x5a;
  }
  else {
    uVar9 = 0;
  }
  return uVar9;
}



/* Each E857/8/9==22 asserts its82B1/2/3 latch; rising edges set82A4.bit5 and activity82A75A. Other
   values clear that latch. Return5A while any source equals22. Rising status22 on any E857/8/9
   source sets classifier bit5 and activity; continued22 returns5A without refreshing the edge
   marker. Other values release individual latches. */

uint f33_update_classifier_status22_edges(void)

{
  uint uVar1;
  
  if (DAT_febee857 == '\"') {
    if (DAT_febe82b1 == '\0') {
      DAT_febe82b1 = 'Z';
      DAT_febe82a4 = DAT_febe82a4 | 0x20;
      DAT_febe82a7 = 0x5a;
    }
    uVar1 = 0x5a;
  }
  else {
    uVar1 = 0;
    DAT_febe82b1 = '\0';
  }
  if (DAT_febee858 == '\"') {
    if (DAT_febe82b2 == '\0') {
      DAT_febe82b2 = 'Z';
      DAT_febe82a4 = DAT_febe82a4 | 0x20;
      DAT_febe82a7 = 0x5a;
    }
    uVar1 = 0x5a;
  }
  else {
    DAT_febe82b2 = '\0';
  }
  if (DAT_febee859 == '\"') {
    if (DAT_febe82b3 == '\0') {
      DAT_febe82b3 = 'Z';
      DAT_febe82a4 = DAT_febe82a4 | 0x20;
      DAT_febe82a7 = 0x5a;
    }
    uVar1 = 0x5a;
  }
  else {
    DAT_febe82b3 = '\0';
  }
  return uVar1;
}



/* Update bank predicate, snapshot active counts, update status latch, then age flags. Select using
   pre-aging counts and post-aging flags plus application predicates; publish selector82A0 and its
   five-byte2A19C row. Cleared age flags do not imply cleared active counts or event histories.
   Stateful selectors1/2 have separate counters82B6/82B8. Pre-aging active-counter snapshots and
   post-aging flags select five-byte ROM output row. Native equality/expiry cases preserve active
   class2 and all event histories despite bitmap inhibition. */

void f33_update_diagnostic_classifier_output(void)

{
  char cVar1;
  byte bVar2;
  undefined1 uVar3;
  short sVar4;
  short sVar5;
  short sVar6;
  char cVar7;
  char cVar8;
  char cVar9;
  char cVar10;
  char cVar11;
  short sVar12;
  short sVar13;
  short sVar14;
  short sVar15;
  short sVar16;
  short sVar17;
  ushort uVar18;
  uint32_t puVar19;
  uchar uVar20;
  uint uVar21;
  uint uVar22;
  char cVar23;
  char cVar24;
  ushort uVar25;
  ushort uVar26;
  int iVar27;
  
  puVar19 = 0xfebeb800u;
  FUN_000510b6();
  sVar12 = (*((short *)camry_host_ptr((uint32_t)(puVar19 + -0x3540))));
  sVar4 = (*((short *)camry_host_ptr((uint32_t)(puVar19 + -0x3546))));
  sVar5 = (*((short *)camry_host_ptr((uint32_t)(puVar19 + -0x3544))));
  sVar6 = (*((short *)camry_host_ptr((uint32_t)(puVar19 + -0x3542))));
  sVar13 = (*((short *)camry_host_ptr((uint32_t)(puVar19 + -0x353e))));
  sVar14 = (*((short *)camry_host_ptr((uint32_t)(puVar19 + -0x353c))));
  sVar15 = (*((short *)camry_host_ptr((uint32_t)(puVar19 + -0x3530))));
  sVar16 = (*((short *)camry_host_ptr((uint32_t)(puVar19 + -0x353a))));
  cVar7 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar19 + (uint32_t)(0x301a)))));
  cVar8 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar19 + (uint32_t)(0x301d)))));
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar19 + (uint32_t)(-0x3557)))));
  cVar24 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar19 + (uint32_t)(-0x355e)))));
  cVar23 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar19 + (uint32_t)(-0x355f)))));
  uVar26 = (*((ushort *)camry_host_ptr((uint32_t)(puVar19 + -0x3548))));
  uVar25 = (*((ushort *)camry_host_ptr((uint32_t)(puVar19 + -0x354a))));
  cVar9 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar19 + (uint32_t)(-0x3550)))));
  sVar17 = (*((short *)camry_host_ptr((uint32_t)(puVar19 + -0x3538))));
  cVar10 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar19 + (uint32_t)(0x301b)))));
  cVar11 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar19 + (uint32_t)(0x301c)))));
  uVar20 = f33_update_classifier_status_latch();
  f33_age_classifier_groups();
  uVar21 = f33_classifier_selector3_predicate();
  uVar22 = f33_update_classifier_status22_edges();
  if (cVar24 == 'Z') {
    if (cVar23 == 'Z') {
      uVar25 = uVar25 + 1;
      uVar18 = 1;
      if (DAT_00030e48 < uVar25) {
        cVar23 = '\0';
      }
    }
    else {
      uVar26 = uVar26 + 1;
      uVar18 = 2;
      if (DAT_00030e4a <= uVar26) {
        cVar24 = '\0';
      }
    }
  }
  else {
    bVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar19 + (uint32_t)(-0x355c)))));
    if (uVar21 == 0x5a) {
      uVar18 = 3;
    }
    else if ((sVar4 == 0) && (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar19 + (uint32_t)(-0x355d))))) & 1) == 0)) {
      if ((sVar5 == 0) && (((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar19 + (uint32_t)(-0x355d))))) >> 1 & 1) == 0)) {
        if ((sVar13 == 0) && ((bVar2 >> 4 & 1) == 0)) {
          if ((((sVar14 == 0) && (sVar15 == 0)) && (uVar22 != 0x5a)) && ((bVar2 >> 5 & 1) == 0)) {
            if ((sVar16 == 0) && ((bVar2 >> 6 & 1) == 0)) {
              if ((sVar12 == 0) && ((bVar2 >> 2 & 1) == 0)) {
                if ((sVar6 == 0) && (uVar18 = bVar2 & 8, (bVar2 & 8) == 0)) {
                  if ((cVar7 == '\x01') && (cVar9 != 'Z')) {
                    uVar18 = 0xf;
                    goto LAB_00051482;
                  }
                  if ((((cVar1 == 'Z') && (cVar10 != 'Z')) && (cVar11 != 'Z')) &&
                     ((cVar8 != 'Z' && (sVar17 == 0)))) goto LAB_00051482;
                }
                else if (uVar20 == '\0') {
                  uVar18 = 0xd;
                  goto LAB_00051482;
                }
              }
              else if (uVar20 == '\0') {
                uVar18 = 0xe;
                goto LAB_00051482;
              }
              uVar18 = 0x10;
            }
            else {
              uVar18 = 0xc;
            }
          }
          else {
            uVar18 = 0xb;
          }
        }
        else {
          uVar18 = 10;
        }
      }
      else if (((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar19 + (uint32_t)(-0x355b))))) >> 1 & 1) == 0) {
        uVar18 = 9;
      }
      else {
        uVar18 = 8;
      }
    }
    else if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar19 + (uint32_t)(-0x355b))))) & 1) == 0) {
      uVar18 = 7;
    }
    else {
      uVar18 = 6;
    }
  }
LAB_00051482:
  iVar27 = (short)uVar18 * 5;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar19 + (uint32_t)(-0x3552))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2a19cu + (uint32_t)(iVar27) * 1u))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar19 + (uint32_t)(-0x3556))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2a19du + (uint32_t)(iVar27) * 1u))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar19 + (uint32_t)(-0x3555))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2a19eu + (uint32_t)(iVar27) * 1u))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar19 + (uint32_t)(-0x3554))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2a19fu + (uint32_t)(iVar27) * 1u))));
  uVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2a1a0u + (uint32_t)(iVar27) * 1u))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar19 + (uint32_t)(-0x3560))))) = (char)uVar18;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar19 + (uint32_t)(-0x355e))))) = cVar24;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar19 + (uint32_t)(-0x3553))))) = uVar3;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar19 + (uint32_t)(-0x355f))))) = cVar23;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar19 + -0x3548)))) = uVar26;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar19 + -0x354a)))) = uVar25;
  return;
}



/* Decrement the selected class counter only if nonzero. Existing class/aging flags are not cleared
   here; classifier aging/projection remains a separate operation. Decrement selected classifier
   counter only when nonzero; leave class flags latched for separate aging/projection. */

void f33_release_diagnostic_classifier(uchar classification)

{
  uint32_t puVar1;
  uint saved_mask;
  
  puVar1 = 0xfebeb800u;
  saved_mask = f33_priority_mask_enter(0xff00);
  if (classification == '\x02') {
    if ((*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x3546)))) != 0) {
      (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x3546)))) = (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x3546)))) + -1;
    }
  }
  else if (classification == '\x04') {
    if ((*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x3544)))) != 0) {
      (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x3544)))) = (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x3544)))) + -1;
    }
  }
  else if (classification == '\b') {
    if ((*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x3542)))) != 0) {
      (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x3542)))) = (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x3542)))) + -1;
    }
  }
  else if (classification == '\x0f') {
    if ((*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x3540)))) != 0) {
      (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x3540)))) = (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x3540)))) + -1;
    }
  }
  else if (classification == '\x10') {
    if ((*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x353e)))) != 0) {
      (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x353e)))) = (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x353e)))) + -1;
    }
  }
  else if (classification == ' ') {
    if ((*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x353c)))) != 0) {
      (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x353c)))) = (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x353c)))) + -1;
    }
  }
  else if (classification == '@') {
    if ((*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x353a)))) != 0) {
      (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x353a)))) = (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x353a)))) + -1;
    }
  }
  else if (classification == 0x80) {
    if ((*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x3538)))) != 0) {
      (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x3538)))) = (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x3538)))) + -1;
    }
  }
  else if ((classification == 0xf0) && ((*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x3530)))) != 0)) {
    (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x3530)))) = (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x3530)))) + -1;
  }
  f33_priority_mask_restore(saved_mask);
  return;
}



/* Clear nine active counters and82A3/A4/A5 flags, reload ages200/200/600. Do not clear
   activity82A6/A7/A8 or describe this as resetting every classifier field. Clear nine active
   counters and three flag groups, reload age thresholds, retain activity markers. Not a
   whole-classifier reset. */

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



/* Single constant publisher: DAT_febe82a9 = 0x5a; Shape-classified from the canonical corpus; the
   target cell is not yet named, so the written state's meaning is unknown. */

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



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_51610(void)

{
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



/* Only consumer82D7>=4 triggers bounded four-cell search beginning at producer82D6. A valid
   consumer pointing to an empty slot is not rescanned. Only invalid consumer>=4 triggers bounded
   scan from producer; valid consumer at empty slot is not repaired. */

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



/* Write six halfwords: ROM2FC44 event ID when its entry current bit is set, otherwise0.
   Retained-only exceptions do not qualify; the real buffer is12 bytes, not six byte flags.
   Twelve-byte output contains six event IDs or zero slots according to entry current bit;
   retained-only state does not qualify. */

void f33_snapshot_preserved_current_events(ushort *events)

{
  int iVar1;
  int iVar2;
  ushort uVar3;
  uint uVar4;
  int iVar5;
  
  iVar5 = 0;
  do {
    uVar3 = *(ushort *)(((undefined *)camry_host_ptr(0x2fc44u)) + iVar5 * 2);
    uVar4 = f33_get_diagnostic_event_state((uint)uVar3);
    if ((uVar4 & 1) == 0) {
      uVar3 = 0;
    }
    events[iVar5] = uVar3;
    iVar2 = iVar5 + 1;
    iVar1 = iVar5 + -5;
    iVar5 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  return;
}



/* Read six saved IDs/zero slots;525E0 restores valid events into three histories. Pass descriptor
   byte1 in realR6 to classifier assertion when nonzero. Exact preserved-event classes1/0 do not
   rebuild class2 counters; class1 has no50FC8 handler. Restore six saved IDs through real
   three-history writer and descriptor classification inR6. Exact classes1/0 do not reconstruct
   class2 counts. */

void f33_restore_preserved_current_events(ushort *events)

{
  int iVar1;
  int iVar2;
  ushort uVar3;
  int iVar4;
  
  iVar4 = 0;
  do {
    uVar3 = events[iVar4];
    FUN_000525e0((uint)uVar3);
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2fc51u + (uint32_t)((uint)uVar3 * 8) * 1u)))) != '\0') {
      f33_assert_diagnostic_classifier((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2fc51u + (uint32_t)((uint)uVar3 * 8) * 1u)))));
    }
    iVar2 = iVar4 + 1;
    iVar1 = iVar4 + -5;
    iVar4 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  return;
}



/* If E856==11, save six current exceptional event IDs around bitmap reset, capture maintenance and
   classifier reset, then restore them. Otherwise run the same reset without preservation. Second
   retained history60F0 is not cleared by this operation. E85611 brackets selective
   bitmap/capture/classifier reset with six-current-event preservation. Second retained history
   survives; native composition checks ordinary versus current/retained-only exception generations.
    */

void f33_clear_diagnostic_ram_generation(void)

{
  ushort auStack_10 [6];
  
  if (DAT_febee856 == '\x11') {
    f33_snapshot_preserved_current_events(auStack_10);
    f33_clear_current_and_first_event_history();
    f33_mark_capture_slots_for_clear();
    f33_reset_classifier_counts_and_flags();
    f33_restore_preserved_current_events(auStack_10);
  }
  else {
    f33_clear_current_and_first_event_history();
    f33_mark_capture_slots_for_clear();
    f33_reset_classifier_counts_and_flags();
  }
  return;
}



/* Idle lifecycle82D4: set1, reset RAM state, then set high bit to81. Other states except81
   deduplicate request1 in four queue bytes82D8..DB and insert at normalized circular index82D6.
   Return0, not a persistence acknowledgement or queue-full status. Idle lifecycle1 transitions to81
   after RAM clear. Other busy phases deduplicate operation1 in four-slot circular queue;81 does not
   requeue. Constant return0 is not persistence acknowledgement. */

uint f33_request_diagnostic_clear(void)

{
  uint uVar1;
  uint32_t puVar2;
  int iVar3;
  
  puVar2 = 0xfebeb800u;
  if (DAT_febe82d4 == '\0') {
    DAT_febe82d4 = '\x01';
    f33_clear_diagnostic_ram_generation();
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x352c))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x352c))))) | 0x80;
  }
  else if (((int8_t)DAT_febe82d4) != -0x7f) {
    iVar3 = 0;
    uVar1 = 0;
    do {
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe82d8u + (uint32_t)(uVar1) * 1u)))) == '\x01') {
        iVar3 = 0x5a;
      }
      uVar1 = uVar1 + 1 & 0xff;
    } while ((uVar1 < 4) && (iVar3 != 0x5a));
    if (iVar3 == 0) {
      uVar1 = (uint)DAT_febe82d6;
      if (3 < uVar1) {
        uVar1 = 0;
      }
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe82d8u + (uint32_t)(uVar1) * 1u)))) = 1;
      if (uVar1 < 3) {
        DAT_febe82d6 = (char)uVar1 + 1;
      }
      else {
        DAT_febe82d6 = 0;
      }
    }
  }
  return 0;
}



void FUN_00051788(void)

{
  char cVar1;
  ushort auStack_14 [6];
  
  cVar1 = DAT_febee856;
  thunk_FUN_000bdb48();
  FUN_00054a24();
  FUN_0003990c();
  FUN_00045e12();
  thunk_FUN_000bdf24();
  thunk_FUN_000bdcfe();
  FUN_00055658();
  if (cVar1 == '\x11') {
    f33_snapshot_preserved_current_events(auStack_14);
    f33_clear_second_event_history();
    FUN_00052f32();
    FUN_000546a2();
    f33_restore_preserved_current_events(auStack_14);
  }
  else {
    f33_clear_second_event_history();
    FUN_00052f32();
    FUN_000546a2();
  }
  return;
}



undefined4 FUN_000517dc(void)

{
  uint uVar1;
  uint32_t puVar2;
  int iVar3;
  
  puVar2 = 0xfebeb800u;
  if (DAT_febe82d4 == '\0') {
    DAT_febe82d4 = '\x02';
    FUN_00051788();
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x352c))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x352c))))) | 0x80;
  }
  else if ((((int8_t)DAT_febe82d4) != -0x7e) && (((int8_t)DAT_febe82d4) != -0x7a)) {
    iVar3 = 0;
    uVar1 = 0;
    do {
      if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe82d8u + (uint32_t)(uVar1) * 1u)))) == '\x02') || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe82d8u + (uint32_t)(uVar1) * 1u)))) == '\x06')) {
        iVar3 = 0x5a;
      }
      uVar1 = uVar1 + 1 & 0xff;
    } while ((uVar1 < 4) && (iVar3 != 0x5a));
    if (iVar3 == 0) {
      if (3 < DAT_febe82d6) {
        DAT_febe82d6 = 0;
      }
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe82d8u + (uint32_t)(DAT_febe82d6) * 1u)))) = 2;
      if (DAT_febe82d6 < 3) {
        DAT_febe82d6 = DAT_febe82d6 + 1;
      }
      else {
        DAT_febe82d6 = 0;
      }
    }
  }
  return 0;
}



undefined4 FUN_00051866(void)

{
  uint uVar1;
  uint32_t puVar2;
  puVar2 = 0xfebeb800u;
  if (DAT_febe82d4 == '\0') {
    DAT_febe82d4 = '\x04';
    f33_clear_diagnostic_ram_generation();
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x352c))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x352c))))) | 0x80;
  }
  else if (((int8_t)DAT_febe82d4) != -0x7c) {
    uVar1 = 0;
    do {
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe82d8u + (uint32_t)(uVar1) * 1u)))) == '\x04') break;
      uVar1 = uVar1 + 1;
    } while (uVar1 < 4);
    if (uVar1 == 4) {
      if (3 < DAT_febe82d6) {
        DAT_febe82d6 = 0;
      }
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe82d8u + (uint32_t)(DAT_febe82d6) * 1u)))) = 4;
      if (DAT_febe82d6 < 3) {
        DAT_febe82d6 = DAT_febe82d6 + 1;
      }
      else {
        DAT_febe82d6 = 0;
      }
    }
  }
  return 0;
}



/* Far-call trampoline: prepare {lp},0 / jarl 0x5551A / dispose 0,{lp},lp; byte-verified against the
   exact image. Forwards with registers and stack unchanged; marked as a thunk. Forwarding shape
   machine-verified; target semantics not recovered. */

void thunk_FUN_0005551a(void)

{
  FUN_0005551a();
  return;
}



undefined4 FUN_000518e0(void)

{
  uint uVar1;
  uint32_t puVar2;
  int iVar3;
  
  puVar2 = 0xfebeb800u;
  if (DAT_febe82d4 == '\0') {
    DAT_febe82d4 = '\x05';
    thunk_FUN_0005551a();
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x352c))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x352c))))) | 0x80;
  }
  else if ((((int8_t)DAT_febe82d4) != -0x7b) && (((int8_t)DAT_febe82d4) != -0x7a)) {
    iVar3 = 0;
    uVar1 = 0;
    do {
      if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe82d8u + (uint32_t)(uVar1) * 1u)))) == '\x05') || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe82d8u + (uint32_t)(uVar1) * 1u)))) == '\x06')) {
        iVar3 = 0x5a;
      }
      uVar1 = uVar1 + 1 & 0xff;
    } while ((uVar1 < 4) && (iVar3 != 0x5a));
    if (iVar3 == 0) {
      uVar1 = (uint)DAT_febe82d6;
      if (3 < uVar1) {
        uVar1 = 0;
      }
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe82d8u + (uint32_t)(uVar1) * 1u)))) = 5;
      if (uVar1 < 3) {
        DAT_febe82d6 = (char)uVar1 + 1;
      }
      else {
        DAT_febe82d6 = 0;
      }
    }
  }
  return 0;
}



void FUN_00051962(void)

{
  ushort auStack_10 [6];
  
  thunk_FUN_000bdb48();
  FUN_00054a24();
  FUN_0003990c();
  FUN_00045e12();
  thunk_FUN_000bdf24();
  thunk_FUN_000bdcfe();
  FUN_0005575e();
  f33_snapshot_preserved_current_events(auStack_10);
  f33_clear_second_event_history();
  FUN_00053092();
  FUN_000546a2();
  f33_restore_preserved_current_events(auStack_10);
  return;
}



undefined4 FUN_0005199e(void)

{
  uint uVar1;
  uint32_t puVar2;
  int iVar3;
  
  puVar2 = 0xfebeb800u;
  if (DAT_febe82d4 == '\0') {
    DAT_febe82d4 = '\x06';
    FUN_00051962();
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x352c))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x352c))))) | 0x80;
  }
  else if (((int8_t)DAT_febe82d4) != -0x7a) {
    iVar3 = 0;
    uVar1 = 0;
    do {
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe82d8u + (uint32_t)(uVar1) * 1u)))) == '\x06') {
        iVar3 = 0x5a;
      }
      uVar1 = uVar1 + 1 & 0xff;
    } while ((uVar1 < 4) && (iVar3 != 0x5a));
    if (iVar3 == 0) {
      uVar1 = (uint)DAT_febe82d6;
      if (3 < uVar1) {
        uVar1 = 0;
      }
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe82d8u + (uint32_t)(uVar1) * 1u)))) = 6;
      if (uVar1 < 3) {
        DAT_febe82d6 = (char)uVar1 + 1;
      }
      else {
        DAT_febe82d6 = 0;
      }
    }
  }
  return 0;
}



/* Repair consumer, clear lifecycle82D4, then skip unsupported nonzero entries and dispatch at most
   one of1/2/4/5/6. Clear consumed slot and advance circular consumer; stop at empty slot or after
   four unsupported entries. Opcode3 is not recognized. Clear lifecycle, skip unsupported entries
   and dispatch at most one recognized opcode1/2/4/5/6 with circular advancement. Empty slot stops
   service; opcode3 is not recognized. */

void f33_dispatch_next_diagnostic_request(void)

{
  char cVar1;
  int iVar2;
  undefined8 uVar3;
  int iVar4;
  byte bVar5;
  uint uVar6;
  
  uVar3 = 0xfebeb800;
  f33_repair_diagnostic_queue_consumer();
  uVar6 = (uint)DAT_febe82d7;
  DAT_febe82d4 = 0;
  bVar5 = 0;
  while( true ) {
    iVar2 = (int)uVar3;
    cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe82d8u + (uint32_t)(uVar6) * 1u))));
    if (cVar1 == '\0') break;
    bVar5 = bVar5 + 1;
    iVar4 = 0x5a;
    if (cVar1 == '\x01') {
      f33_request_diagnostic_clear();
    }
    else if (cVar1 == '\x02') {
      FUN_000517dc();
    }
    else if (cVar1 == '\x04') {
      FUN_00051866();
    }
    else if (cVar1 == '\x05') {
      FUN_000518e0();
    }
    else if (cVar1 == '\x06') {
      FUN_0005199e();
    }
    else {
      iVar4 = 0;
    }
    iVar2 = (int)uVar3;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe82d8u + (uint32_t)(uVar6) * 1u)))) = 0;
    if (uVar6 < 3) {
      uVar6 = uVar6 + 1 & 0xff;
    }
    else {
      uVar6 = 0;
    }
    if ((iVar4 != 0) || (3 < bVar5)) goto LAB_00051a90;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe82d8u + (uint32_t)(uVar6) * 1u)))) = 0;
LAB_00051a90:
  (*((char *)camry_host_ptr((uint32_t)(iVar2 + -0x3529)))) = (char)uVar6;
  return;
}



/* Active lifecycle waits while ANY phase5F85/6150/8608/89C4 isAA/A5. Terminal lifecycle-specific
   acknowledgement precedes bounded queue dispatch; phase55 is failure, not hold. A dispatched
   request can immediately restore busy phase and dirty state. Any group phaseAA/A5 globally holds
   active completion. Terminal acknowledgement is lifecycle-specific; failure55 still allows bounded
   queue dispatch and immediate new busy generation. */

void f33_complete_diagnostic_request_and_dispatch(void)

{
  undefined4 uVar1;
  undefined1 uVar2;
  
  if (DAT_febe82d4 == '\0') {
    return;
  }
  if (((int8_t)DAT_febe5f85) == -0x56) {
    return;
  }
  if (((int8_t)DAT_febe5f85) == -0x5b) {
    return;
  }
  if (((int8_t)DAT_febe6150) == -0x56) {
    return;
  }
  if (((int8_t)DAT_febe6150) == -0x5b) {
    return;
  }
  if (((int8_t)DAT_febe8608) == -0x56) {
    return;
  }
  if (((int8_t)DAT_febe8608) == -0x5b) {
    return;
  }
  if (((int8_t)DAT_febe89c4) == -0x56) {
    return;
  }
  if (((int8_t)DAT_febe89c4) == -0x5b) {
    return;
  }
  if (((int8_t)DAT_febe82d4) == -0x7f) {
    if ((DAT_febe5f85 != '\0') || (DAT_febe6150 != '\0')) {
      uVar1 = 0x11;
      goto LAB_00051b54;
    }
    uVar1 = 0x11;
    uVar2 = 0;
  }
  else {
    if (((int8_t)DAT_febe82d4) == -0x7a) {
      if (((DAT_febe5f85 == '\0') && (DAT_febe6150 == '\0')) &&
         ((DAT_febe8608 == '\0' && (DAT_febe89c4 == '\0')))) {
        uVar2 = 0;
      }
      else {
        uVar2 = 0x20;
      }
      FUN_0004d0e8(uVar2);
      goto LAB_00051b5c;
    }
    if (((int8_t)DAT_febe82d4) == -0x7e) {
      if ((((DAT_febe5f85 == '\0') && (DAT_febe6150 == '\0')) && (DAT_febe8608 == '\0')) &&
         (DAT_febe89c4 == '\0')) {
        uVar1 = 10;
        uVar2 = 0;
      }
      else {
        uVar1 = 10;
LAB_00051b54:
        uVar2 = 0x20;
      }
    }
    else {
      if (((int8_t)DAT_febe82d4) != -0x7b) goto LAB_00051b5c;
      uVar1 = 3;
      if (DAT_febe89c4 != '\0') goto LAB_00051b54;
      uVar2 = 0;
    }
  }
  FUN_0004d0a4(uVar1,uVar2);
LAB_00051b5c:
  f33_dispatch_next_diagnostic_request();
  return;
}



void FUN_00051b64(void)

{
  uint32_t puVar1;
  uint uVar2;
  
  puVar1 = 0x23dfcu;
  if ((DAT_febee856 == '\x11') && ((DAT_febee85b == '\0' || (DAT_febee85b == '\"')))) {
    uVar2 = 0;
    do {
      if ((uintptr_t)(*(code **)(puVar1 + uVar2 * 4 + -0x2ab0))!=(uintptr_t)(f33_reset_vector)) {
        (*(int (*)())*(code **)(puVar1 + uVar2 * 4 + -0x2ab0))();
      }
      uVar2 = uVar2 + 1;
    } while (uVar2 < 4);
  }
  return;
}



/* Nonzero82D4 invokes completion/dispatch, then independently run51B64 mode-gated callbacks. Those
   E85611/E85B0-or22 callbacks are not persistence acknowledgement. Native scheduler interval
   composes old-status polling, acknowledgement and queued restart, or holds callback/queue when a
   failed peer still has a pending companion. Independent callbacks load both mode bytes before
   their gate. Terminal software statuses are explicit inputs, not generated physical completion. */

void f33_service_diagnostic_request_lifecycle(void)

{
  if (DAT_febe82d4 != '\0') {
    f33_complete_diagnostic_request_and_dispatch();
  }
  FUN_00051b64();
  return;
}



/* Descriptor byte0 must intersect2, or6 when prior qualification==5A. Forward capture kind and
   boolean prior qualification to52E18; event validity belongs to caller. Descriptor byte0 mask2 or6
   by prior qualification5A gates240-byte capture; forwards profile kind and boolean qualification.
    */

void f33_gate_diagnostic_event_capture(uint event,ushort capture_kind,uchar prior_qualification)

{
  byte bVar1;
  
  if (prior_qualification == 'Z') {
    bVar1 = 6;
  }
  else {
    bVar1 = 2;
  }
  if ((bVar1 & (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2fc50u + (uint32_t)((event & 0xffff) * 8) * 1u))))) != 0) {
    f33_capture_diagnostic_event((ushort)event,capture_kind,prior_qualification == 'Z');
  }
  return;
}



/* Only prior qualification0 admits descriptor byte4 classes81/82/86..8C. Increment their
   selected5470C/54632 counter up toFFFF. This can run even when current event already failed,
   independently of first-failure bitmap/capture/classifier work. Prior qualification0 and
   descriptor byte4 class81/82/86..8C select counter getter5470C/setter54632. Increment
   saturatesFFFF; distinct from wrapping classifier counts. */

void f33_update_diagnostic_event_statistics(uint event,uchar prior_qualification)

{
  uint uVar1;
  undefined1 uVar2;
  
  if (prior_qualification == '\0') {
    switch((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2fc54u + (uint32_t)((event & 0xffff) * 8) * 1u))))) {
    case 0x81:
      uVar2 = 5;
      break;
    case 0x82:
      uVar2 = 6;
      break;
    default:
      goto switchD_00051c0a_caseD_83;
    case 0x86:
      uVar2 = 2;
      break;
    case 0x87:
      uVar2 = 3;
      break;
    case 0x88:
      uVar2 = 7;
      break;
    case 0x89:
      uVar2 = 8;
      break;
    case 0x8a:
      uVar2 = 9;
      break;
    case 0x8b:
      uVar2 = 0;
      break;
    case 0x8c:
      uVar2 = 1;
    }
    uVar1 = FUN_0005470c(uVar2);
    if (uVar1 < 0xffff) {
      uVar1 = uVar1 + 1 & 0xffff;
    }
    FUN_00054632(uVar2,uVar1);
  }
switchD_00051c0a_caseD_83:
  return;
}



/* Low16 event1..17F, excluding lifecycle82D4 states1/2/4/6. Snapshot old82D5, then set it5A if
   event descriptor byte4.bit7. Only entry current-bit0 clear invokes bitmap failure, capture and
   classifier assertion; statistics path can run separately. The second argument selects capture
   profile4/10/default, not an occurrence count. New failure composes bitmap mutation,
   profile-selected capture and classifier assertion. Old82D5 qualifies capture before descriptor
   may change the global latch. Repeated statistics have separate gating. */

void f33_report_diagnostic_event_failure(uint event,ushort capture_kind)

{
  char cVar1;
  uchar classification;
  uchar prior_qualification;
  uint32_t puVar2;
  uint uVar3;
  uint event_00;
  
  puVar2 = 0xfebeb800u;
  event_00 = event & 0xffff;
  if ((((event_00 - 1 < 0x17f) && (DAT_febe82d4 != '\x01')) && (DAT_febe82d4 != '\x02')) &&
     ((DAT_febe82d4 != '\x04' && (DAT_febe82d4 != '\x06')))) {
    cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2fc54u + (uint32_t)(event_00 * 8) * 1u))));
    classification = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2fc51u + (uint32_t)(event_00 * 8) * 1u))));
    uVar3 = f33_priority_mask_enter(0xff00);
    prior_qualification = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x352b)))));
    if (cVar1 < '\0') {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x352b))))) = 0x5a;
    }
    f33_priority_mask_restore(uVar3);
    uVar3 = f33_get_diagnostic_event_state(event_00);
    if ((uVar3 & 1) == 0) {
      f33_mark_diagnostic_event_failed(event_00,prior_qualification);
      f33_gate_diagnostic_event_capture(event_00,capture_kind,prior_qualification);
      if (classification != '\0') {
        f33_assert_diagnostic_classifier(classification);
      }
    }
    if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x509b))))) & 0x40) == 0) {
      f33_update_diagnostic_event_statistics(event_00,prior_qualification);
    }
  }
  return;
}



void FUN_00051cf6(byte param_1,undefined2 param_2)

{
  int iVar1;
  
  if ((((param_1 < 0x29) && (DAT_febe82d4 != '\x05')) && (DAT_febe82d4 != '\x02')) &&
     (((DAT_febe82d4 != '\x06' && (DAT_febee85a != '\0')) &&
      (iVar1 = FUN_0005578c(param_1), iVar1 == 0x5a)))) {
    FUN_00055398(param_1,param_2);
  }
  return;
}



void FUN_00051d38(uint param_1,undefined1 param_2,ushort param_3)

{
  if (DAT_febee85a == '\0') {
    f33_report_diagnostic_event_failure(param_1 & 0xffff,param_3);
  }
  else {
    FUN_00051cf6(param_2, (uint)(ushort)param_3);
  }
  return;
}



/* Same event/lifecycle admission as failure. Read ENTRY current bit, invoke bitmap pass, then
   release the descriptor's classifier when entry bit was set. Thus5F85==AA can inhibit bitmap
   mutation without inhibiting classifier decrement. Pass uses entry current bit for classifier
   release even when5F85AA inhibits bitmap mutation. Ordinary and exception-event history lifetimes
   differ. Combined-state execution does not establish production lifecycle reachability. */

void f33_report_diagnostic_event_pass(uint event)

{
  uchar classification;
  uint uVar1;
  uint event_00;
  
  event_00 = event & 0xffff;
  if ((((event_00 - 1 < 0x17f) && (DAT_febe82d4 != '\x01')) && (DAT_febe82d4 != '\x02')) &&
     ((DAT_febe82d4 != '\x04' && (DAT_febe82d4 != '\x06')))) {
    classification = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2fc51u + (uint32_t)(event_00 * 8) * 1u))));
    uVar1 = f33_get_diagnostic_event_state(event_00);
    f33_mark_diagnostic_event_passed(event_00);
    if (((uVar1 & 1) != 0) && (classification != '\0')) {
      f33_release_diagnostic_classifier(classification);
    }
  }
  return;
}



/* Far-call trampoline: prepare {lp},0 / jarl 0x54662 / dispose 0,{lp},lp; byte-verified against the
   exact image. Forwards with registers and stack unchanged; marked as a thunk. Forwarding shape
   machine-verified; target semantics not recovered. */

void thunk_FUN_00054662(void)

{
  FUN_00054662();
  return;
}



undefined4 FUN_00051dbe(void)

{
  uint uVar1;
  uint32_t puVar2;
  puVar2 = 0xfebeb800u;
  if (DAT_febe82d4 == '\0') {
    DAT_febe82d4 = '\x03';
    thunk_FUN_00054662();
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x352c))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x352c))))) | 0x80;
  }
  else if (((int8_t)DAT_febe82d4) != -0x7d) {
    uVar1 = 0;
    do {
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe82d8u + (uint32_t)(uVar1) * 1u)))) == '\x03') break;
      uVar1 = uVar1 + 1;
    } while (uVar1 < 4);
    if (uVar1 == 4) {
      if (3 < DAT_febe82d6) {
        DAT_febe82d6 = 0;
      }
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe82d8u + (uint32_t)(DAT_febe82d6) * 1u)))) = 3;
      if (DAT_febe82d6 < 3) {
        DAT_febe82d6 = DAT_febe82d6 + 1;
      }
      else {
        DAT_febe82d6 = 0;
      }
    }
  }
  return 0;
}



/* For low16(event)1..17F, call52A2A to mark the independent6120 bitmap. No diagnostic lifecycle
   gate and no ordinary-pass clearing of6090/60C0/60F0. */

void f33_report_diagnostic_healthy_observed(uint event)

{
  if ((event & 0xffff) - 1 < 0x17f) {
    f33_mark_diagnostic_healthy_observed(event & 0xffff);
  }
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_51e44(void)

{
  return;
}



/* Rows0..17F inclusive: set6120 bit when descriptor byte2 OR byte5 is zero. Includes row0; does not
   simply copy an existing failure history. Rebuild6120 from descriptor byte2-or-byte5 zero over
   rows0..17F inclusive, including row0. Not a copy of failure history. */

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



void FUN_00051e8a(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint *puVar4;
  int iVar5;
  uint32_t puVar6;
  uint uVar7;
  uint *puVar8;
  undefined4 local_b0;
  undefined4 uStack_ac;
  uint local_a8 [2];
  undefined1 auStack_a0 [8];
  undefined4 auStack_98 [12];
  uint auStack_68 [12];
  undefined4 auStack_38 [12];
  
  puVar6 = 0xfebeb800u;
  puVar8 = ((undefined *)camry_host_ptr(0x21364u));
  puVar4 = local_a8;
  do {
    uVar7 = *puVar8;
    puVar8 = puVar8 + 1;
    *puVar4 = uVar7;
    puVar4 = puVar4 + 1;
  } while ((uintptr_t)(puVar8)!=(uintptr_t)((uint *)((undefined *)camry_host_ptr(0x21404u))));
  local_b0 = DAT_0002135c;
  uStack_ac = DAT_00021360;
  uVar7 = f33_nvm_get_record(0, camry_host_addr(local_a8));
  iVar5 = 0;
  if (uVar7 == 0x10) {
    do {
      iVar3 = iVar5 * 4;
      iVar2 = iVar5 + 1;
      iVar1 = iVar5 + -0xb;
      *(undefined4 *)(((undefined *)camry_host_ptr(0xfebe60c0u)) + iVar3) = auStack_98[iVar5];
      *(uint *)(((undefined *)camry_host_ptr(0xfebe60f0u)) + iVar3) = auStack_68[iVar5];
      *(undefined4 *)(((undefined *)camry_host_ptr(0xfebe6120u)) + iVar3) = auStack_38[iVar5];
      iVar5 = iVar2;
    } while (((iVar1 < 0) || (iVar2 < 0)));
    iVar5 = 0;
    do {
      iVar2 = iVar5 + 1;
      iVar1 = iVar5 + -7;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5f71u + (uint32_t)(iVar5) * 1u)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(local_a8) + iVar5))));
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5f79u + (uint32_t)(iVar5) * 1u)))) = auStack_a0[iVar5];
      iVar5 = iVar2;
    } while (((iVar1 < 0) || (iVar2 < 0)));
  }
  else if (uVar7 == 0x11) {
    do {
      iVar3 = iVar5 * 4;
      iVar2 = iVar5 + 1;
      iVar1 = iVar5 + -0xb;
      *(undefined4 *)(((undefined *)camry_host_ptr(0xfebe60c0u)) + iVar3) = 0;
      *(undefined4 *)(((undefined *)camry_host_ptr(0xfebe60f0u)) + iVar3) = 0;
      *(undefined4 *)(((undefined *)camry_host_ptr(0xfebe6120u)) + iVar3) = 0;
      iVar5 = iVar2;
    } while (((iVar1 < 0) || (iVar2 < 0)));
    iVar5 = 0;
    do {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5f71u + (uint32_t)(iVar5) * 1u)))) = 0;
      iVar2 = iVar5 + 1;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5f79u + (uint32_t)(iVar5) * 1u)))) = 0;
      iVar1 = iVar5 + -7;
      iVar5 = iVar2;
    } while (((iVar1 < 0) || (iVar2 < 0)));
  }
  else {
    do {
      iVar1 = iVar5 * 4;
      iVar2 = iVar5 + 1;
      *(undefined4 *)(((undefined *)camry_host_ptr(0xfebe60c0u)) + iVar1) = *(undefined4 *)(((undefined *)camry_host_ptr(0xfebe6090u)) + iVar1);
      uVar7 = auStack_68[iVar5];
      *(undefined4 *)(((undefined *)camry_host_ptr(0xfebe6120u)) + iVar1) = 0;
      *(uint *)(((undefined *)camry_host_ptr(0xfebe60f0u)) + iVar1) = *(uint *)(((undefined *)camry_host_ptr(0xfebe60f0u)) + iVar1) | uVar7;
      iVar1 = iVar5 + -0xb;
      iVar5 = iVar2;
    } while (((iVar1 < 0) || (iVar2 < 0)));
    iVar5 = 0;
    do {
      iVar2 = iVar5 + 1;
      iVar1 = iVar5 + -7;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5f71u + (uint32_t)(iVar5) * 1u)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(local_a8) + iVar5))));
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5f79u + (uint32_t)(iVar5) * 1u)))) = auStack_a0[iVar5];
      iVar5 = iVar2;
    } while (((iVar1 < 0) || (iVar2 < 0)));
  }
  f33_rebuild_event_descriptor_bitmap();
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x587e))))) = 0x5a;
  uVar7 = f33_nvm_get_record(10, camry_host_addr(&local_b0));
  if (uVar7 == 0x11) {
    (*((uint16_t *)((uint8_t *)&local_b0 + 0u))) = 0;
    (*((uint16_t *)((uint8_t *)&local_b0 + 2u))) = 0;
  }
  else if ((((int16_t)(*((uint16_t *)((uint8_t *)&local_b0 + 2u)))) == -0x5aa6) && ((short)local_b0 != -1)) {
    (*((uint16_t *)((uint8_t *)&local_b0 + 0u))) = (short)local_b0 + 1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x587c))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x587c))))) | 0x40;
  }
  DAT_febe6028 = (short)local_b0;
  DAT_febe602a = (*((uint16_t *)((uint8_t *)&local_b0 + 2u)));
  return;
}



/* A5 maps current6090 into602C and classifier-qualified6054; other selector maps retained60C0
   into6040. Map descriptors only for event1..17F, nonzero DTC index<160 and flagbit6. Rebuild
   auxiliary banks separately;6054 is not60F0. */

void f33_rebuild_derived_diagnostic_banks(uchar generation_selector)

{
  int iVar1;
  int iVar2;
  byte bVar3;
  uint uVar4;
  undefined *puVar5;
  uint *puVar6;
  undefined *puVar7;
  uint uVar8;
  uint uVar9;
  int iVar10;
  undefined1 *puVar11;
  uint auStack_3c [10];
  uint auStack_14 [5];
  
  iVar10 = 0;
  do {
    iVar2 = iVar10 + 1;
    auStack_14[iVar10] = 0;
    auStack_3c[iVar10 + 5] = 0;
    auStack_3c[iVar10] = 0;
    iVar1 = iVar10 + -4;
    iVar10 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  if (generation_selector == 0xa5) {
    puVar7 = ((undefined *)camry_host_ptr(0xfebe6090u));
    puVar6 = f33_derived_current_dtc_bitmap;
    puVar5 = ((undefined *)camry_host_ptr(0xfebe6068u));
    puVar11 = ((undefined *)camry_host_ptr(0xfebe5f81u));
  }
  else {
    puVar7 = ((undefined *)camry_host_ptr(0xfebe60c0u));
    puVar6 = f33_derived_retained_dtc_bitmap;
    puVar5 = ((undefined *)camry_host_ptr(0xfebe607cu));
    puVar11 = ((undefined *)camry_host_ptr(0xfebe5f82u));
  }
  *puVar11 = 0;
  uVar9 = 1;
  do {
    if ((*(uint *)(puVar7 + (uVar9 >> 5) * 4) >> (uVar9 & 0x1f) & 1) != 0) {
      iVar10 = uVar9 * 8;
      uVar8 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2fc52u + (uint32_t)(iVar10) * 1u))));
      if (((uVar8 != 0) && (uVar8 < 0xa0)) && (((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2fc50u + (uint32_t)(iVar10) * 1u)))) >> 6 & 1) != 0)) {
        bVar3 = (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2fc52u + (uint32_t)(iVar10) * 1u)))) >> 5;
        uVar8 = 1 << (uVar8 & 0x1f);
        auStack_14[bVar3] = auStack_14[bVar3] | uVar8;
        if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2fc51u + (uint32_t)(iVar10) * 1u)))) != '\0') && (generation_selector == 0xa5)) {
          auStack_3c[bVar3] = auStack_3c[bVar3] | uVar8;
        }
      }
      uVar8 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2fc53u + (uint32_t)(iVar10) * 1u))));
      if ((uVar8 != 0) && (uVar8 < 0x40)) {
        uVar4 = (uint)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2fc53u + (uint32_t)(iVar10) * 1u)))) >> 5);
        auStack_3c[uVar4 + 5] = auStack_3c[uVar4 + 5] | 1 << (uVar8 & 0x1f);
      }
    }
    uVar9 = uVar9 + 1;
  } while (uVar9 < 0x180);
  iVar10 = 0;
  do {
    puVar6[iVar10] = auStack_14[iVar10];
    *(uint *)(puVar5 + iVar10 * 4) = auStack_3c[iVar10 + 5];
    if (generation_selector == 0xa5) {
      f33_derived_classified_current_dtc_bitmap[iVar10] = auStack_3c[iVar10];
    }
    iVar2 = iVar10 + 1;
    iVar1 = iVar10 + -4;
    iVar10 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  return;
}



/* Trackers5F83/86 equal1 inspect real software status: high20 stays1, high10 becomes2, other
   becomes3. Wait for every armed peer; then phase5F85=55 if either failed, else0, and clear
   trackers. Low nibble is ignored; no local timeout/retry or physical read. Software status high20
   remains pending, high10 succeeds, others fail. A failed peer cannot terminate a pending peer;
   all-terminal aggregate0/55 clears trackers. Low nibble ignored. */

void f33_poll_diagnostic_record_completion(void)

{
  uint32_t puVar1;
  uint uVar2;
  uint uVar3;
  undefined1 uVar4;
  char cVar5;
  char cVar6;
  
  cVar5 = DAT_febe5f86;
  uVar4 = DAT_febe5f85;
  cVar6 = DAT_febe5f83;
  puVar1 = 0xfebeb800u;
  if ((DAT_febe5f83 != '\0') || (DAT_febe5f86 != '\0')) {
    puVar1 = 0xfebeb800u;
    uVar2 = f33_nvm_get_record_status(0);
    uVar3 = f33_nvm_get_record_status(10);
    if ((cVar6 == '\x01') && ((uVar2 & 0xf0) != 0x20)) {
      if ((uVar2 & 0xf0) == 0x10) {
        cVar6 = '\x02';
      }
      else {
        cVar6 = '\x03';
      }
    }
    if ((cVar5 == '\x01') && ((uVar3 & 0xf0) != 0x20)) {
      if ((uVar3 & 0xf0) == 0x10) {
        cVar5 = '\x02';
      }
      else {
        cVar5 = '\x03';
      }
    }
    if ((cVar6 != '\x01') && (cVar5 != '\x01')) {
      if ((cVar6 == '\x03') || (cVar5 == '\x03')) {
        uVar4 = 0x55;
      }
      else {
        uVar4 = 0;
      }
      cVar6 = '\0';
      cVar5 = '\0';
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x587d))))) = cVar6;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x587a))))) = cVar5;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x587b))))) = uVar4;
  return;
}



/* PMRFF00-protected160-byte object0 serialization: eight bytes each5F71/5F79 then 48 bytes
   each60C0/60F0/6120. Current bitmap6090 is excluded. Real66D6E acceptance is ignored; RAM
   mirror/queue publication is not durable storage. Serialize two8-byte auxiliary banks
   and60C0/60F0/6120 into160-byte object0; exclude current6090. PMR spans real set-record call,
   whose acceptance is ignored. */

void f33_stage_diagnostic_history_record(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  uint saved_mask;
  uint local_ac [2];
  undefined1 auStack_a4 [8];
  undefined4 auStack_9c [12];
  undefined4 auStack_6c [12];
  undefined4 auStack_3c [12];
  
  saved_mask = f33_priority_mask_enter(0xff00);
  iVar4 = 0;
  do {
    iVar3 = iVar4 * 4;
    iVar2 = iVar4 + 1;
    iVar1 = iVar4 + -0xb;
    auStack_9c[iVar4] = *(undefined4 *)(((undefined *)camry_host_ptr(0xfebe60c0u)) + iVar3);
    auStack_6c[iVar4] = *(undefined4 *)(((undefined *)camry_host_ptr(0xfebe60f0u)) + iVar3);
    auStack_3c[iVar4] = *(undefined4 *)(((undefined *)camry_host_ptr(0xfebe6120u)) + iVar3);
    iVar4 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  iVar4 = 0;
  do {
    iVar2 = iVar4 + 1;
    iVar1 = iVar4 + -7;
    (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(local_ac) + iVar4)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5f71u + (uint32_t)(iVar4) * 1u))));
    auStack_a4[iVar4] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5f79u + (uint32_t)(iVar4) * 1u))));
    iVar4 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  f33_nvm_set_record(0,local_ac);
  f33_priority_mask_restore(saved_mask);
  return;
}



/* PMRFF00-protected object10 serialization:6028/602A halfwords plus zero word. Submit real66D6E and
   restore mask without propagating acceptance. Serialize6028/602A and zero word into decimal
   object10; retain PMR across set-record and ignore acceptance. */

void f33_stage_diagnostic_invocation_record(void)

{
  uint32_t puVar1;
  uint saved_mask;
  undefined2 local_10;
  undefined2 uStack_e;
  undefined4 uStack_c;
  
  puVar1 = 0xfebeb800u;
  saved_mask = f33_priority_mask_enter(0xff00);
  local_10 = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x57d8))));
  uStack_c = 0;
  uStack_e = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x57d6))));
  f33_nvm_set_record(10,(uint *)&local_10);
  f33_priority_mask_restore(saved_mask);
  return;
}



/* Snapshot5F84; permissionE8215A or dirty bits3/4 admit. Remove captured bits under PMR, then
   separately snapshot payloads. MasksBA/52 select objects0/10; bit3 arms object0, bit4 arms both
   completion trackers, irrespective of set-record acceptance. Native forced dirtybit4 bypasses
   closed ordinary permission and composes both serializers with real family0 RAM mirror/queue
   publication. Dirty consumed and trackers armed; acceptance remains unchecked, physical durability
   unclaimed. */

void f33_publish_dirty_diagnostic_records(void)

{
  byte bVar1;
  byte bVar2;
  uint32_t puVar3;
  uint saved_mask;
  undefined1 uVar4;
  undefined1 uVar5;
  
  uVar4 = DAT_febe5f86;
  bVar2 = DAT_febe5f84;
  uVar5 = DAT_febe5f83;
  puVar3 = 0xfebeb800u;
  if ((((DAT_febee821 == 'Z') || ((DAT_febe5f84 >> 3 & 1) != 0)) || ((DAT_febe5f84 >> 4 & 1) != 0))
     && (DAT_febe5f84 != 0)) {
    bVar1 = ~DAT_febe5f84;
    puVar3 = 0xfebeb800u;
    saved_mask = f33_priority_mask_enter(0xff00);
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x587c))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x587c))))) & bVar1;
    f33_priority_mask_restore(saved_mask);
    if ((bVar2 & 0xba) != 0) {
      f33_stage_diagnostic_history_record();
    }
    if ((bVar2 & 0x52) != 0) {
      f33_stage_diagnostic_invocation_record();
    }
    if ((bVar2 >> 3 & 1) != 0) {
      uVar5 = 1;
    }
    if ((bVar2 >> 4 & 1) != 0) {
      uVar5 = 1;
      uVar4 = 1;
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x587d))))) = uVar5;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x587a))))) = uVar4;
  return;
}



/* Rebuild one pending derived bank, refresh derived presence, poll previous submissions BEFORE
   publishing new dirty records. Completion later in the scheduler may start a new dirty generation
   that cannot be serialized retroactively. Derived-bank maintenance precedes polling previous
   submissions then publishing current dirty records. Later lifecycle dispatch can dirty a new
   generation only for a future serializer invocation. */

void f33_service_diagnostic_record_transaction(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint32_t puVar4;
  uchar generation_selector;
  
  puVar4 = 0xfebeb800u;
  generation_selector = 0xa5;
  if ((DAT_febe5f81 == 'Z') || (generation_selector = DAT_febe5f82, DAT_febe5f82 == 'Z')) {
    puVar4 = 0xfebeb800u;
    f33_rebuild_derived_diagnostic_banks(generation_selector);
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x5890))))) = 0;
  iVar3 = 0;
  do {
    if (f33_derived_current_dtc_bitmap[iVar3] != 0) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x5890))))) = 1;
    }
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -4;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  f33_poll_diagnostic_record_completion();
  f33_publish_dirty_diagnostic_records();
  return;
}



/* Unless5F85==AA, atomically set all three event bitmap bits on a new current failure; dirty5F81/82
   and5F84.bit1. Descriptor flags and packedDTC determine bounded pending-code counter updates
   and6028/602A requests. No local event bounds check; caller owns admission. New current failure
   sets all three bitmap generations and dirty flags unless5F85AA. Descriptor/DTC gates select
   pending-code counters and requests; event admission belongs to caller. */

void f33_mark_diagnostic_event_failed(uint event,uchar prior_qualification)

{
  int iVar1;
  byte bVar2;
  byte bVar3;
  uint uVar4;
  uint32_t puVar5;
  uint saved_mask;
  byte bVar6;
  uint uVar7;
  
  puVar5 = 0xfebeb800u;
  iVar1 = (event & 0xffff) * 8;
  bVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2fc50u + (uint32_t)(iVar1) * 1u))));
  bVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2fc52u + (uint32_t)(iVar1) * 1u))));
  uVar7 = (uint)bVar3;
  if (((int8_t)DAT_febe5f85) != -0x56) {
    saved_mask = f33_priority_mask_enter(0xff00);
    iVar1 = ((event & 0xffff) >> 5) * 4;
    if ((*(uint *)(((undefined *)camry_host_ptr(0xfebe6090u)) + iVar1) >> (event & 0x1f) & 1) == 0) {
      uVar4 = 1 << (event & 0x1f);
      *(uint *)(((undefined *)camry_host_ptr(0xfebe6090u)) + iVar1) = uVar4 | *(uint *)(((undefined *)camry_host_ptr(0xfebe6090u)) + iVar1);
      *(uint *)(((undefined *)camry_host_ptr(0xfebe60c0u)) + iVar1) = *(uint *)(((undefined *)camry_host_ptr(0xfebe60c0u)) + iVar1) | uVar4;
      *(uint *)(((undefined *)camry_host_ptr(0xfebe60f0u)) + iVar1) = *(uint *)(((undefined *)camry_host_ptr(0xfebe60f0u)) + iVar1) | uVar4;
      DAT_febe5f81 = 0x5a;
      DAT_febe5f82 = 0x5a;
      uVar4 = 0;
      if (uVar7 < 0xa0) {
        uVar4 = *(uint *)(((undefined *)camry_host_ptr(0x30850u)) + uVar7 * 8);
      }
      if (prior_qualification == 'Z') {
        bVar6 = 6;
      }
      else {
        bVar6 = 2;
      }
      if ((uVar4 != 0) && ((bVar6 & bVar2) != 0)) {
        if ((uVar4 & 0xc00000) != 0xc00000) {
          uVar4 = 0;
          do {
            if (((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5f71u + (uint32_t)(uVar4) * 1u)))) == uVar7) || ((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5f71u + (uint32_t)(uVar4) * 1u)))) == 0)) {
              if (((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5f79u + (uint32_t)(uVar4) * 1u))))) != -1) {
                (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5f79u + (uint32_t)(uVar4) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5f79u + (uint32_t)(uVar4) * 1u)))) + '\x01';
              }
              (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5f71u + (uint32_t)(uVar4) * 1u)))) = bVar3;
              break;
            }
            uVar4 = uVar4 + 1;
          } while (uVar4 < 8);
        }
        if ((*((short *)camry_host_ptr((uint32_t)(puVar5 + -0x57d6)))) != -0x5aa6) {
          (*((undefined2 *)camry_host_ptr((uint32_t)(puVar5 + -0x57d6)))) = 0xa55a;
        }
        (*((undefined2 *)camry_host_ptr((uint32_t)(puVar5 + -0x57d8)))) = 0;
      }
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x587c))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x587c))))) | 2;
    }
    f33_priority_mask_restore(saved_mask);
  }
  return;
}



/* Unless5F85==AA, ordinary pass clears only current6090 bit and dirties5F81. Exact exception
   list0E/51/BE/FF/20/120 clears all three bits even if only retained bits were set, dirties5F81/82
   and5F84.bit5. Does not itself clear captures or classifier latches. Ordinary pass retains two
   histories. Exact exceptions0E/51/BE/FF/20/120 clear all three generations even with only retained
   bits set. Dirty semantics and5F85 inhibition are independent of classifier release. */

void f33_mark_diagnostic_event_passed(uint event)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint32_t puVar4;
  uint saved_mask;
  uint uVar5;
  uint uVar6;
  int iVar7;
  uint uVar8;
  
  puVar4 = 0xfebeb800u;
  uVar8 = event & 0xffff;
  if (((uVar8 != 0) && (uVar8 < 0x180)) && (((int8_t)DAT_febe5f85) != -0x56)) {
    iVar7 = 0;
    iVar3 = 0;
    do {
      if (*(ushort *)(((undefined *)camry_host_ptr(0x2fc44u)) + iVar3 * 2) == uVar8) {
        iVar7 = 0x5a;
      }
      iVar2 = iVar3 + 1;
      iVar1 = iVar3 + -5;
      iVar3 = iVar2;
    } while (((iVar1 < 0) || (iVar2 < 0)));
    saved_mask = f33_priority_mask_enter(0xff00);
    iVar3 = (uVar8 >> 5) * 4;
    uVar6 = event & 0x1f;
    uVar5 = *(uint *)(((undefined *)camry_host_ptr(0xfebe6090u)) + iVar3);
    uVar8 = uVar5 >> uVar6 & 1;
    if (iVar7 == 0x5a) {
      if (((uVar8 != 0) || ((*(uint *)(((undefined *)camry_host_ptr(0xfebe60c0u)) + iVar3) >> uVar6 & 1) != 0)) ||
         ((*(uint *)(((undefined *)camry_host_ptr(0xfebe60f0u)) + iVar3) >> uVar6 & 1) != 0)) {
        uVar8 = ~(1 << uVar6);
        *(uint *)(((undefined *)camry_host_ptr(0xfebe6090u)) + iVar3) = uVar8 & uVar5;
        *(uint *)(((undefined *)camry_host_ptr(0xfebe60c0u)) + iVar3) = *(uint *)(((undefined *)camry_host_ptr(0xfebe60c0u)) + iVar3) & uVar8;
        *(uint *)(((undefined *)camry_host_ptr(0xfebe60f0u)) + iVar3) = *(uint *)(((undefined *)camry_host_ptr(0xfebe60f0u)) + iVar3) & uVar8;
        DAT_febe5f81 = 0x5a;
        DAT_febe5f82 = 0x5a;
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x587c))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x587c))))) | 0x20;
      }
    }
    else if (uVar8 != 0) {
      *(uint *)(((undefined *)camry_host_ptr(0xfebe6090u)) + iVar3) = ~(1 << uVar6) & uVar5;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x587f))))) = 0x5a;
    }
    f33_priority_mask_restore(saved_mask);
  }
  return;
}



void FUN_000524be(uint param_1)

{
  int iVar1;
  uint32_t puVar2;
  uint saved_mask;
  uint uVar3;
  
  puVar2 = 0xfebeb800u;
  uVar3 = param_1 & 0xffff;
  if (((uVar3 != 0) && (uVar3 < 0x180)) && (((int8_t)DAT_febe5f85) != -0x56)) {
    saved_mask = f33_priority_mask_enter(0xff00);
    iVar1 = (uVar3 >> 5) * 4;
    param_1 = param_1 & 0x1f;
    if ((((*(uint *)(((undefined *)camry_host_ptr(0xfebe6090u)) + iVar1) >> param_1 & 1) != 0) ||
        ((*(uint *)(((undefined *)camry_host_ptr(0xfebe60c0u)) + iVar1) >> param_1 & 1) != 0)) ||
       ((*(uint *)(((undefined *)camry_host_ptr(0xfebe60f0u)) + iVar1) >> param_1 & 1) != 0)) {
      uVar3 = ~(1 << param_1);
      *(uint *)(((undefined *)camry_host_ptr(0xfebe6090u)) + iVar1) = uVar3 & *(uint *)(((undefined *)camry_host_ptr(0xfebe6090u)) + iVar1);
      *(uint *)(((undefined *)camry_host_ptr(0xfebe60c0u)) + iVar1) = *(uint *)(((undefined *)camry_host_ptr(0xfebe60c0u)) + iVar1) & uVar3;
      *(uint *)(((undefined *)camry_host_ptr(0xfebe60f0u)) + iVar1) = *(uint *)(((undefined *)camry_host_ptr(0xfebe60f0u)) + iVar1) & uVar3;
      DAT_febe5f81 = 0x5a;
      DAT_febe5f82 = 0x5a;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x587c))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x587c))))) | 0x80;
    }
    f33_priority_mask_restore(saved_mask);
  }
  return;
}



/* Phase5F85AA, clear12 words each6090/60C0/6120, rebuild descriptor bitmap, set dirty5F81/82
   and5F84.bit3, then phaseA5. Preserve second retained60F0. Clear6090/60C0, rebuild6120, mark dirty
   and progressAA->A5. Preserve60F0; this is not all-history clearing. */

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



/* Distinct operation: phase5F85AA, clear60F0, eight-byte banks5F71/5F79 and6028/602A, set
   dirty5F84.bit4 and phaseA5. InitialAA store is instruction-visible despite C folding. Separate
   operation clears60F0 and auxiliary histories6028/602A/5F71/5F79 with dirtybit4. Initial phaseAA
   store is instruction-visible though folded from C. */

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



/* For configured DTC indices synthesize bit0 from602C,28 from6040 and80 from6054. Add10 when an
   associated event lacks6120 healthy observation and retained bit3 is clear. These are derived DTC
   generations, not raw event bitmaps. */

void f33_build_dtc_status_snapshot(uchar *status)

{
  byte bVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  
  uVar4 = 0;
  do {
    bVar1 = 0;
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x30854u + (uint32_t)(uVar4 * 8) * 1u)))) == '\x01') {
      uVar3 = uVar4 >> 5;
      uVar2 = uVar4 & 0x1f;
      bVar1 = (f33_derived_current_dtc_bitmap[uVar3] >> uVar2 & 1) != 0;
      if ((f33_derived_retained_dtc_bitmap[uVar3] >> uVar2 & 1) != 0) {
        bVar1 = bVar1 | 0x28;
      }
      if ((f33_derived_classified_current_dtc_bitmap[uVar3] >> uVar2 & 1) != 0) {
        bVar1 = bVar1 | 0x80;
      }
    }
    status[uVar4] = bVar1;
    uVar4 = uVar4 + 1;
  } while (uVar4 < 0xa0);
  uVar4 = 0;
  do {
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x30854u + (uint32_t)((uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2fc52u + (uint32_t)(uVar4 * 8) * 1u)))) * 8) * 1u)))) == '\x01') {
      bVar1 = status[(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2fc52u + (uint32_t)(uVar4 * 8) * 1u))))];
      if (((*(uint *)(((undefined *)camry_host_ptr(0xfebe6120u)) + (uVar4 >> 5) * 4) >> (uVar4 & 0x1f) & 1) == 0) &&
         ((bVar1 >> 3 & 1) == 0)) {
        status[(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2fc52u + (uint32_t)(uVar4 * 8) * 1u))))] = bVar1 | 0x10;
      }
    }
    uVar4 = uVar4 + 1;
  } while (uVar4 < 0x180);
  return;
}



void FUN_000526cc(void)

{
  uint uVar1;
  byte local_a8 [160];
  
  f33_build_dtc_status_snapshot(local_a8);
  uVar1 = 0;
  do {
    uVar1 = uVar1 + 1;
  } while (uVar1 < 0xa0);
  return;
}



void FUN_00052710(int param_1,uint param_2)

{
  uint *puVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  uint auStack_14 [5];
  
  uVar3 = 0;
  do {
    iVar2 = uVar3 * 4;
    puVar1 = auStack_14 + uVar3;
    uVar3 = uVar3 + 1;
    *puVar1 = *(uint *)(((undefined *)camry_host_ptr(0xfebe6068u)) + iVar2) | *(uint *)(((undefined *)camry_host_ptr(0xfebe607cu)) + iVar2);
  } while (uVar3 < 5);
  uVar4 = 0;
  uVar3 = 0;
  do {
    if (((((auStack_14[uVar3 >> 5] >> (uVar3 & 0x1f) & 1) != 0) && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2fc04u + (uint32_t)(uVar3) * 1u)))) != '\0'))
        && (param_1 != 0)) && ((param_2 & 0xff) != 0)) {
      (*((undefined1 *)camry_host_ptr((uint32_t)(uVar4 + param_1)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2fc04u + (uint32_t)(uVar3) * 1u))));
      uVar4 = uVar4 + 1 & 0xff;
      if ((param_2 & 0xff) <= uVar4) {
        return;
      }
    }
    uVar3 = uVar3 + 1;
  } while (uVar3 < 0x40);
  return;
}



/* Low16 event1..17F(hex) returns bits0/1/2 from6090/60C0/60F0 bitmaps; otherwise0. These three
   internal generations are not by themselves the UDS eight-bit status byte. Event1..17F yields
   three bits from6090/60C0/60F0; invalid returns0. Internal generations are not a UDS status-byte
   join. */

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



/* Starting index1 refreshes160 status bytes at5F87 from derived DTC banks and healthy-observed
   events, then scans configured nonzero DTCs. Later cursor reads use that status generation rather
   than rebuilding each item. */

uint f33_scan_dtc_status_snapshot(uchar mask,uint *dtc,uchar *status,ushort start_index)

{
  byte bVar1;
  uint *extraout_r7;
  byte *extraout_r8;
  uint uVar2;
  
  uVar2 = (uint)start_index;
  if (uVar2 == 1) {
    f33_build_dtc_status_snapshot(f33_dtc_status_iteration_snapshot);
    status = extraout_r8;
    dtc = extraout_r7;
  }
  while( true ) {
    if (0x9f < uVar2) {
      return 0;
    }
    bVar1 = f33_dtc_status_iteration_snapshot[uVar2];
    if (((mask & bVar1) != 0) && (*(uint *)(((undefined *)camry_host_ptr(0x30850u)) + uVar2 * 8) != 0)) break;
    uVar2 = uVar2 + 1;
  }
  *dtc = *(uint *)(((undefined *)camry_host_ptr(0x30850u)) + uVar2 * 8);
  *status = bVar1;
  return uVar2;
}



undefined4 FUN_00052830(int param_1)

{
  uint uVar1;
  uint uVar2;
  
  uVar1 = 0;
  while (param_1 != *(int *)(((undefined *)camry_host_ptr(0x30850u)) + uVar1 * 8)) {
    uVar1 = uVar1 + 1 & 0xff;
    if (0x9f < uVar1) {
      return 0;
    }
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x30854u + (uint32_t)(uVar1 * 8) * 1u)))) == '\x01') {
    uVar2 = 0;
    if ((1 << (uVar1 & 0x1f) & f33_derived_retained_dtc_bitmap[uVar1 >> 5]) != 0) {
      return 0x5a;
    }
    do {
      if (((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2fc52u + (uint32_t)(uVar2 * 8) * 1u)))) == uVar1) &&
         ((1 << (uVar2 & 0x1f) & *(uint *)(((undefined *)camry_host_ptr(0xfebe6120u)) + (uVar2 >> 5) * 4)) == 0)) {
        return 0;
      }
      uVar2 = uVar2 + 1 & 0xffff;
    } while (uVar2 < 0x180);
  }
  return 0x5a;
}



byte FUN_000528bc(uint param_1)

{
  uint uVar1;
  int iVar2;
  uint uVar3;
  byte bVar4;
  
  uVar1 = (param_1 & 0xff) >> 5;
  uVar3 = param_1 & 0x1f;
  bVar4 = (f33_derived_current_dtc_bitmap[uVar1] >> uVar3 & 1) != 0;
  if ((f33_derived_retained_dtc_bitmap[uVar1] >> uVar3 & 1) != 0) {
    bVar4 = bVar4 | 0x28;
  }
  if ((f33_derived_classified_current_dtc_bitmap[uVar1] >> uVar3 & 1) != 0) {
    bVar4 = bVar4 | 0x80;
  }
  iVar2 = FUN_00052830(*(undefined4 *)(((undefined *)camry_host_ptr(0x30850u)) + (param_1 & 0xff) * 8));
  if (iVar2 == 0) {
    bVar4 = bVar4 | 0x10;
  }
  return bVar4;
}



void FUN_00052972(int param_1,uint param_2)

{
  int iVar1;
  undefined1 *puVar2;
  undefined1 uVar3;
  int iVar4;
  uint uVar5;
  undefined4 uVar6;
  uint uVar7;
  uint uVar8;
  undefined1 local_20 [8];
  byte abStack_18 [8];
  
  for (iVar4 = 0; iVar1 = iVar4 - (param_2 & 0xffff), ((iVar1 < 0) || (iVar4 < 0));
      iVar4 = iVar4 + 1) {
    (*((undefined1 *)camry_host_ptr((uint32_t)(iVar4 + param_1)))) = 0;
  }
  uVar5 = f33_priority_mask_enter(0xff00);
  uVar8 = 0;
  do {
    uVar7 = uVar8 + 1;
    abStack_18[uVar8] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5f71u + (uint32_t)(uVar8) * 1u))));
    local_20[uVar8] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5f79u + (uint32_t)(uVar8) * 1u))));
    uVar8 = uVar7;
  } while (uVar7 < 8);
  f33_priority_mask_restore(uVar5);
  uVar5 = 0;
  uVar8 = 0;
  do {
    uVar7 = (uint)abStack_18[uVar8];
    uVar3 = local_20[uVar8];
    if (-1 < (int)((uVar5 + 3) - (param_2 & 0xffff))) {
      return;
    }
    if ((uVar7 != 0) && (uVar7 < 0xa0)) {
      uVar6 = *(undefined4 *)(((undefined *)camry_host_ptr(0x30850u)) + uVar7 * 8);
      puVar2 = ((undefined1 *)camry_host_ptr((uint32_t)(uVar5 + param_1)));
      uVar5 = uVar5 + 3 & 0xff;
      puVar2[2] = (char)uVar6;
      *puVar2 = (char)((uint)uVar6 >> 0x10);
      puVar2[1] = (char)((uint)uVar6 >> 8);
      (*((undefined1 *)camry_host_ptr((uint32_t)(uVar5 + param_1)))) = uVar3;
      uVar5 = uVar5 + 1 & 0xff;
    }
    uVar8 = uVar8 + 1;
  } while (uVar8 < 8);
  return;
}



void FUN_00052a10(void)

{
  uint32_t puVar1;
  uint saved_mask;
  
  puVar1 = 0xfebeb800u;
  saved_mask = f33_priority_mask_enter(0xff00);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x587c))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x587c))))) | 2;
  f33_priority_mask_restore(saved_mask);
  return;
}



/* For event1..17F, set its6120 bitmap bit only when absent, under saved/restored PMRFF00. Current
   and retained failure histories are untouched. */

void f33_mark_diagnostic_healthy_observed(uint event)

{
  int iVar1;
  uint saved_mask;
  
  if ((event & 0xffff) - 1 < 0x17f) {
    iVar1 = ((event & 0xffff) >> 5) * 4;
    if ((*(uint *)(((undefined *)camry_host_ptr(0xfebe6120u)) + iVar1) >> (event & 0x1f) & 1) == 0) {
      saved_mask = f33_priority_mask_enter(0xff00);
      *(uint *)(((undefined *)camry_host_ptr(0xfebe6120u)) + iVar1) = *(uint *)(((undefined *)camry_host_ptr(0xfebe6120u)) + iVar1) | 1 << (event & 0x1f);
      f33_priority_mask_restore(saved_mask);
    }
  }
  return;
}



/* Clear18 words (72 bytes); used only for the supplemental region, not the whole capture. Clear18
   words in72-byte supplement; not a whole capture. */

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



/* Copy60 words forward. Exact leaf changes only R1/R19/EP and flags; call also changes LP. Its
   target-local convention preserves R10 carrying saved PMR in52E18. Do not invent a mask return or
   rely on repeated-loop inlining, which fails at later calls. Forward60-word copy preserves R10.
   Exact target-local convention retains saved PMR across every call in52E18; repeated-loop inlining
   only handled the first call. No fictitious return or replacement body. */

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



void FUN_00052ad4(void)

{
  bool bVar1;
  uint32_t puVar2;
  uint uVar3;
  
  puVar2 = 0xfebeb800u;
  uVar3 = f33_nvm_get_record(1, camry_host_addr(((uint *)camry_host_ptr((uint32_t)(f33_diagnostic_capture_slots)))));
  bVar1 = false;
  if (uVar3 != 0x11) {
    bVar1 = (*((short *)camry_host_ptr((uint32_t)(puVar2 + -0x3492)))) != 0;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x56af))))) = bVar1;
  uVar3 = f33_nvm_get_record(2, camry_host_addr(((uint *)camry_host_ptr((uint32_t)(puVar2 + -0x3434)))));
  bVar1 = false;
  if (uVar3 == 0x10) {
    bVar1 = (*((short *)camry_host_ptr((uint32_t)(puVar2 + -0x33a2)))) != 0;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x56ae))))) = bVar1;
  uVar3 = f33_nvm_get_record(3, camry_host_addr(((uint *)camry_host_ptr((uint32_t)(puVar2 + -0x3344)))));
  bVar1 = false;
  if (uVar3 == 0x10) {
    bVar1 = (*((short *)camry_host_ptr((uint32_t)(puVar2 + -0x32b2)))) != 0;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x56ad))))) = bVar1;
  return;
}



/* Objects1/2/3 use trackers6157..59: high20 pending, high10 success, other failure. Only after no
   tracker1 remains clear trackers and publish aggregate6150=0/55. Capture objects1/2/3 share
   all-peer terminal barrier and high-nibble status classification; aggregate0/55 only after no
   tracker1 remains. */

void f33_poll_diagnostic_capture_completion(void)

{
  uint32_t puVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  undefined1 uVar5;
  char cVar6;
  char cVar7;
  char cVar8;
  
  cVar6 = DAT_febe6159;
  cVar7 = DAT_febe6158;
  cVar8 = DAT_febe6157;
  uVar5 = DAT_febe6150;
  puVar1 = 0xfebeb800u;
  if (((DAT_febe6157 != '\0') || (DAT_febe6158 != '\0')) || (DAT_febe6159 != '\0')) {
    puVar1 = 0xfebeb800u;
    uVar2 = f33_nvm_get_record_status(1);
    uVar3 = f33_nvm_get_record_status(2);
    uVar4 = f33_nvm_get_record_status(3);
    if ((cVar8 == '\x01') && ((uVar2 & 0xf0) != 0x20)) {
      if ((uVar2 & 0xf0) == 0x10) {
        cVar8 = '\x02';
      }
      else {
        cVar8 = '\x03';
      }
    }
    if ((cVar7 == '\x01') && ((uVar3 & 0xf0) != 0x20)) {
      if ((uVar3 & 0xf0) == 0x10) {
        cVar7 = '\x02';
      }
      else {
        cVar7 = '\x03';
      }
    }
    if ((cVar6 == '\x01') && ((uVar4 & 0xf0) != 0x20)) {
      if ((uVar4 & 0xf0) == 0x10) {
        cVar6 = '\x02';
      }
      else {
        cVar6 = '\x03';
      }
    }
    if (((cVar8 != '\x01') && (cVar7 != '\x01')) && (cVar6 != '\x01')) {
      if (((cVar8 == '\x03') || (cVar7 == '\x03')) || (cVar6 == '\x03')) {
        uVar5 = 0x55;
      }
      else {
        uVar5 = 0;
      }
      cVar8 = '\0';
      cVar7 = '\0';
      cVar6 = '\0';
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x56a9))))) = cVar8;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x56a8))))) = cVar7;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x56a7))))) = cVar6;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x56b0))))) = uVar5;
  return;
}



/* Permission5A or aggregate dirtybit2 admits publication. Captured masks&6 submit 240-byte
   objects1/2/3; bit2 arms trackers. Consume captured masks and ignore submission acceptance; do not
   infer physical completion from armed software trackers. Permission or aggregate dirtybit2 admits
   captured masks; masks&6 submit three240-byte records and bit2 arms corresponding trackers without
   checking acceptance. */

void f33_publish_dirty_diagnostic_captures(void)

{
  byte bVar1;
  byte bVar2;
  byte bVar3;
  byte bVar4;
  uint32_t puVar5;
  uint saved_mask;
  undefined1 uVar6;
  undefined1 uVar7;
  undefined1 uVar8;
  
  uVar6 = DAT_febe6159;
  uVar7 = DAT_febe6158;
  uVar8 = DAT_febe6157;
  bVar4 = DAT_febe6156;
  bVar3 = DAT_febe6155;
  bVar2 = DAT_febe6154;
  puVar5 = 0xfebeb800u;
  bVar1 = DAT_febe6156 | DAT_febe6155 | DAT_febe6154;
  if (((DAT_febee821 == 'Z') || ((bVar1 >> 2 & 1) != 0)) && ((bVar1 & 6) != 0)) {
    puVar5 = 0xfebeb800u;
    saved_mask = f33_priority_mask_enter(0xff00);
    if ((bVar2 & 6) != 0) {
      f33_nvm_set_record(1,((uint *)camry_host_ptr((uint32_t)(puVar5 + -0x3524))));
    }
    if ((bVar3 & 6) != 0) {
      f33_nvm_set_record(2,((uint *)camry_host_ptr((uint32_t)(puVar5 + -0x3434))));
    }
    if ((bVar4 & 6) != 0) {
      f33_nvm_set_record(3,((uint *)camry_host_ptr((uint32_t)(puVar5 + -0x3344))));
    }
    if ((bVar2 >> 2 & 1) != 0) {
      uVar8 = 1;
    }
    if ((bVar3 >> 2 & 1) != 0) {
      uVar7 = 1;
    }
    if ((bVar4 >> 2 & 1) != 0) {
      uVar6 = 1;
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x56ac))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x56ac))))) & ~bVar2;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x56ab))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x56ab))))) & ~bVar3;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x56aa))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x56aa))))) & ~bVar4;
    f33_priority_mask_restore(saved_mask);
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x56a9))))) = uVar8;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x56a8))))) = uVar7;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x56a7))))) = uVar6;
  return;
}



void FUN_00052ca0(void)

{
  byte *pbVar1;
  byte bVar2;
  uint32_t puVar3;
  uint uVar4;
  F33DiagnosticApplicationSample local_3c;
  
  puVar3 = 0xfebeb800u;
  bVar2 = 0;
  uVar4 = 0;
  do {
    pbVar1 = ((undefined *)camry_host_ptr(0xfebe615bu)) + uVar4;
    uVar4 = uVar4 + 1;
    bVar2 = bVar2 | *pbVar1;
  } while (uVar4 < 0xb);
  if (bVar2 == 0) {
    f33_snapshot_diagnostic_application(&local_3c,0x32);
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x320e)))) = 0;
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar3 + -0x3254)))) = (*((undefined4 *)camry_host_ptr((uint32_t)(puVar3 + -0x517c))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x324c)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x515c))));
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3212))))) = local_3c.raw[0];
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3250)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x50f2))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x324e)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x50dc))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x324a)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x5148))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3248)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x5158))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3246)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x50f4))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3244)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x5188))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3242)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x5186))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3240)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x5184))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x323e)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x5182))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x323c)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x5180))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x323a)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x517e))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3238)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x51ac))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3236)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x51aa))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3234)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x51a8))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3232)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x51a6))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3230)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x51a4))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x322e)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x51a2))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x322c)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x535e))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x322a)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x535c))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3228)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x535a))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3226)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x5358))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3224)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x5356))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3222)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x5354))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3220)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x5152))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x321e)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x5150))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x321c)))) = (*((uint16_t *)((uint8_t *)&local_3c + 10u)));
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x321a)))) = (*((uint16_t *)((uint8_t *)&local_3c + 12u)));
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3218)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x50da))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3216)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x5146))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3214)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3aba))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3210)))) = (*((uint16_t *)((uint8_t *)&local_3c + 24u)));
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3211))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3814)))));
  }
  return;
}



void FUN_00052da4(void)

{
  short sVar1;
  uint32_t puVar2;
  uint saved_mask;
  
  puVar2 = 0xfebeb800u;
  if (DAT_febe615a == '\0') {
    saved_mask = f33_priority_mask_enter(0xff00);
    if ((*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x569a)))) < DAT_00030e4c) {
      sVar1 = (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x569a)))) + 1;
    }
    else {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x56a6))))) = 0x5a;
      sVar1 = 0;
    }
    (*((short *)camry_host_ptr((uint32_t)(puVar2 + -0x569a)))) = sVar1;
    f33_priority_mask_restore(saved_mask);
  }
  return;
}



/* Sequential initializer chain: 4 unconditional calls and no other statements; shape-verified. The
   called sequence is the function's entire behavior; chain family members differ in callee sets. */

void f33_run_init_chain_52de4(void)

{
  f33_poll_diagnostic_capture_completion();
  f33_publish_dirty_diagnostic_captures();
  FUN_00052ca0();
  FUN_00052da4();
  return;
}



/* Copy18 words (72 bytes) forward; the retained85AC supplement is distinct from current profile
   data. Forward18-word supplemental copy; independent of240-byte whole-record copy. */

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



/* Construct240-byte profile4/10/default record, fill supplemental72 bytes from85AC or zeros when
   qualified==1, and write duplicate event words at90/92. Only then check 6150==AA storage inhibit.
   Under PMRFF00, unqualified first capture fills82DC once; 615A==5A and nonzero packedDTC distinct
   from both prior records also fills83CC. Qualified capture fills84BC. Update occupancy/dirty flags
   and consume615A on replacement. 240-byte profile and72-byte supplement precede storage
   inhibition. First and distinct-DTC unqualified slots differ from qualified slot. Native composed
   failure verifies selected sources, thermal projection, slot isolation and preserved PMR; not
   physical freshness or persistence. */

void f33_capture_diagnostic_event(ushort event,ushort capture_kind,uchar qualified)

{
  uint32_t puVar1;
  uint saved_mask;
  int iVar2;
  int iVar3;
  int iVar4;
  F33DiagnosticCapture FStack_108;
  
  puVar1 = 0xfebeb800u;
  if (capture_kind == 4) {
    f33_build_diagnostic_capture_kind4(&FStack_108);
  }
  else if (capture_kind == 10) {
    f33_build_diagnostic_capture_kind10(&FStack_108);
  }
  else {
    f33_build_diagnostic_capture_default(&FStack_108);
  }
  FStack_108.event = event;
  FStack_108.event_copy = event;
  if (qualified == '\x01') {
    f33_clear_diagnostic_supplement(FStack_108.supplemental);
  }
  else {
    f33_copy_diagnostic_supplement(FStack_108.supplemental, ((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x3254))));
  }
  iVar3 = 0;
  iVar4 = *(int *)(((undefined *)camry_host_ptr(0x30850u)) + (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2fc52u + (uint32_t)((uint)event * 8) * 1u)))) * 8);
  if ((*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x3494)))) < 0x180) {
    iVar3 = *(int *)(((undefined *)camry_host_ptr(0x30850u)) +
                    (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2fc52u + (uint32_t)((uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x3494)))) * 8) * 1u)))) * 8);
  }
  iVar2 = 0;
  if ((*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x33a4)))) < 0x180) {
    iVar2 = *(int *)(((undefined *)camry_host_ptr(0x30850u)) +
                    (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2fc52u + (uint32_t)((uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x33a4)))) * 8) * 1u)))) * 8);
  }
  if (((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x56b0)))))) == -0x56) {
    return;
  }
  saved_mask = f33_priority_mask_enter(0xff00);
  if (qualified != '\x01') {
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x56af))))) == '\0') {
      f33_copy_diagnostic_capture(((F33DiagnosticCapture *)camry_host_ptr((uint32_t)(puVar1 + -0x3524))),&FStack_108);
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x56af))))) = 1;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x56ac))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x56ac))))) | 2;
    }
    if (((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x56a6))))) != 'Z') || (iVar4 == iVar3)) || (iVar4 == iVar2)) || (iVar4 == 0))
    goto LAB_00052f22;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x56a6))))) = 0;
  if (qualified == '\x01') {
    f33_copy_diagnostic_capture(((F33DiagnosticCapture *)camry_host_ptr((uint32_t)(puVar1 + -0x3344))),&FStack_108);
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x56ad))))) = 1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x56aa))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x56aa))))) | 2;
  }
  else {
    f33_copy_diagnostic_capture(((F33DiagnosticCapture *)camry_host_ptr((uint32_t)(puVar1 + -0x3434))),&FStack_108);
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x56ae))))) = 1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x56ab))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x56ab))))) | 2;
  }
LAB_00052f22:
  f33_priority_mask_restore(saved_mask);
  return;
}



void FUN_00052f32(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe6150 = 0xaa;
  DAT_febe615a = 0x5a;
  DAT_febe6166 = 0;
  if (f33_diagnostic_capture_slots[0].extended_prefix[0x23] == '\"') {
    DAT_febe6151 = 0;
    puVar1 = 0xfebeb800u;
    f33_copy_diagnostic_capture(f33_diagnostic_capture_slots,(F33DiagnosticCapture *)((undefined *)camry_host_ptr(0x2a1f4u)));
  }
  else {
    f33_diagnostic_capture_slots[0].extended_prefix[0x23] = 'D';
  }
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
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x328d))))) == '\"') {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x56ad))))) = 0;
    f33_copy_diagnostic_capture
              (((F33DiagnosticCapture *)camry_host_ptr((uint32_t)(puVar1 + -0x3344))),(F33DiagnosticCapture *)((undefined *)camry_host_ptr(0x2a1f4u)));
  }
  else {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x328d))))) = 0x44;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x56aa))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x56aa))))) | 4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x56b0))))) = 0xa5;
  return;
}



/* For occupied slots, marker44 drops occupancy and copies240-byte ROM defaults. Other markers
   retain occupancy/data except event halfword90=0 and markerB7=22. Set corresponding dirty bit2 and
   global phaseA5; if no slot is occupied, restore entry6150 phase. Always set615A5A and clear6166.
   Retained supplement85AC is not erased. Occupied marker44 resets record/occupancy; other markers
   preserve captured data except event90=0 and markerB7=22. Dirtybit2 and pending phase remain
   separate from physical storage; supplement85AC survives. */

void f33_mark_capture_slots_for_clear(void)

{
  undefined1 uVar1;
  uint32_t puVar2;
  undefined *puVar3;
  
  uVar1 = DAT_febe6150;
  puVar2 = 0xfebeb800u;
  puVar3 = ((undefined *)camry_host_ptr(0xfebeb800u));
  DAT_febe6150 = 0xaa;
  DAT_febe615a = 0x5a;
  DAT_febe6166 = 0;
  if (DAT_febe6151 == '\x01') {
    if (f33_diagnostic_capture_slots[0].extended_prefix[0x23] == 'D') {
      DAT_febe6151 = '\0';
      f33_copy_diagnostic_capture
                (f33_diagnostic_capture_slots,(F33DiagnosticCapture *)((undefined *)camry_host_ptr(0x2a1f4u)));
      puVar3 = ((undefined *)camry_host_ptr((uint32_t)(puVar2)));
    }
    else {
      f33_diagnostic_capture_slots[0].event = 0;
      f33_diagnostic_capture_slots[0].extended_prefix[0x23] = '\"';
      puVar3 = ((undefined *)camry_host_ptr(0xfebeb800u));
    }
    puVar3[-0x56ac] = puVar3[-0x56ac] | 4;
    uVar1 = 0xa5;
  }
  if (puVar3[-0x56ae] == '\x01') {
    if (puVar3[-0x337d] == 'D') {
      puVar3[-0x56ae] = 0;
      f33_copy_diagnostic_capture
                ((F33DiagnosticCapture *)(puVar3 + -0x3434),(F33DiagnosticCapture *)((undefined *)camry_host_ptr(0x2a1f4u)));
    }
    else {
      *(undefined2 *)(puVar3 + -0x33a4) = 0;
      puVar3[-0x337d] = 0x22;
    }
    puVar3[-0x56ab] = puVar3[-0x56ab] | 4;
    uVar1 = 0xa5;
  }
  if (puVar3[-0x56ad] == '\x01') {
    if (puVar3[-0x328d] == 'D') {
      puVar3[-0x56ad] = 0;
      f33_copy_diagnostic_capture
                ((F33DiagnosticCapture *)(puVar3 + -0x3344),(F33DiagnosticCapture *)((undefined *)camry_host_ptr(0x2a1f4u)));
    }
    else {
      *(undefined2 *)(puVar3 + -0x32b4) = 0;
      puVar3[-0x328d] = 0x22;
    }
    puVar3[-0x56aa] = puVar3[-0x56aa] | 4;
    uVar1 = 0xa5;
  }
  puVar3[-0x56b0] = uVar1;
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



/* Store low8(status) at615B+low8(index) only for index<11. Independent families feed healthy-cache
   refresh admission; a pending monitor may block without confirmed actions. */

void f33_set_diagnostic_cache_blocker(uchar index,uchar status)

{
  if (index < 0xb) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe615bu + (uint32_t)(index) * 1u)))) = status;
  }
  return;
}



/* For occupied capture slot1 require duplicate events to map to same nonzero packed DTC, then
   return mask3 for available record numbers1 and10. Event duplicates are not complements. */

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



undefined4 FUN_00053190(uint param_1,char param_2)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  ushort uStack_12;
  
  uVar2 = 0;
  iVar1 = camry_host_addr(FUN_00056664(&uStack_12));
  if ((param_1 & 0xffff) < (uint)uStack_12) {
    iVar1 = (param_1 & 0xffff) * 0x18 + iVar1;
    iVar3 = iVar1;
    if (param_2 != '\0') {
      iVar3 = iVar1 + 8;
    }
    if ((*((int *)camry_host_ptr((uint32_t)(iVar3 + 4)))) != 0) {
      uVar2 = 0x5a;
      if ((uintptr_t)(*(code **)(iVar1 + 0x10))!=(uintptr_t)(f33_reset_vector)) {
        uVar2 = (*(int (*)())*(code **)(iVar1 + 0x10))();
      }
    }
  }
  return uVar2;
}



/* Views0/1 serialize record numbers1/10 from configured75-field table2A364, with field gate and
   view exclusion. Emit record number/count then identifier/length/payload. Return-1 on capacity
   crossing; payload callbacks choose retained sources, not a new physical sample. */

int f33_serialize_retained_capture_record(uchar record_view,uchar *output,ushort capacity)

{
  undefined2 *puVar1;
  uchar *puVar2;
  uchar uVar3;
  int iVar4;
  int iVar5;
  uchar uVar6;
  uint uVar7;
  int iVar8;
  ushort uStack_2a;
  
  iVar8 = 0;
  uVar6 = '\0';
  if (((record_view < 2) && ((uintptr_t)(output)!=(uintptr_t)((uchar *)0x0))) &&
     (iVar4 = camry_host_addr(FUN_00056664(&uStack_2a)), iVar4 != 0)) {
    uVar3 = '\x10';
    if (record_view == '\0') {
      uVar3 = '\x01';
    }
    iVar8 = 2;
    *output = uVar3;
    for (uVar7 = 0; uVar7 < uStack_2a; uVar7 = uVar7 + 1 & 0xffff) {
      if ((record_view == '\0') || ((*((char *)camry_host_ptr((uint32_t)(uVar7 * 0x18 + iVar4 + 2)))) == '\0')) {
        puVar1 = ((undefined2 *)camry_host_ptr((uint32_t)(uVar7 * 0x18 + iVar4)));
        iVar5 = (uint)*(byte *)(puVar1 + 0xb) + iVar8 + 3;
        if ((int)((uint)capacity - iVar5) < 0 !=
            (iVar5 < 0 && iVar5 < 0 == (int)((uint)capacity - iVar5) < 0)) {
          iVar8 = -1;
          break;
        }
        iVar5 = FUN_00053190(uVar7,0);
        if (iVar5 == 0x5a) {
          puVar2 = output + iVar8;
          uVar6 = uVar6 + '\x01';
          FUN_0006a574(*puVar1,puVar2);
          puVar2[2] = *(uchar *)(puVar1 + 0xb);
          (*(int (*)())*(code **)(puVar1 + 2))(record_view,puVar2 + 3);
          iVar8 = iVar8 + (uint)*(byte *)(puVar1 + 0xb) + 3;
        }
      }
    }
    output[1] = uVar6;
  }
  return iVar8;
}



void FUN_00053298(undefined4 param_1,char param_2,undefined4 param_3,ushort param_4)

{
  int iVar1;
  uint32_t puVar2;
  uchar record_view;
  int extraout_r6;
  uchar *output;
  int iVar3;
  char acStack_15 [9];
  
  puVar2 = 0xfebeb800u;
  FUN_00053168(param_1,param_3,param_4,acStack_15);
  if (acStack_15[0] == '\0') {
    iVar1 = 0;
    if ((*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x33a4)))) < 0x180) {
      iVar1 = *(int *)(((undefined *)camry_host_ptr(0x30850u)) +
                      (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2fc52u + (uint32_t)((uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x33a4)))) * 8) * 1u)))) * 8);
    }
    iVar3 = 0;
    if ((*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x33a2)))) < 0x180) {
      iVar3 = *(int *)(((undefined *)camry_host_ptr(0x30850u)) +
                      (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2fc52u + (uint32_t)((uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x33a2)))) * 8) * 1u)))) * 8);
    }
    if ((iVar1 == iVar3) && (extraout_r6 == iVar1)) {
      if (param_2 == '\x01') {
        record_view = '\0';
      }
      else {
        if (param_2 != '\x10') {
          return;
        }
        record_view = '\x01';
      }
      f33_serialize_retained_capture_record(record_view,output,param_4);
    }
  }
  return;
}



/* Capture-slot field dispatch: reads one field from a diagnostic capture slot record and passes it
   through a fixed transform to one dispatch callee; shape-verified family of per-field accessors.
    */

void f33_capture_slot_dispatch_53316(undefined4 param_1,int param_2)

{
  bool bVar1;
  undefined2 uVar2;
  undefined4 uVar3;
  
  uVar2 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * 240u + 186u))));
  if (0xfffe < (ushort)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * 240u + 186u))))) {
    (*((uint8_t *)((uint8_t *)&uVar2 + 0u))) = 0xff;
    (*((uint8_t *)((uint8_t *)&uVar2 + 1u))) = 0xff;
  }
  uVar3 = (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * 240u + 188u))));
  if ((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * 240u + 188u)))) == -1) {
    (*((uint8_t *)((uint8_t *)&uVar3 + 0u))) = 0xff;
    (*((uint8_t *)((uint8_t *)&uVar3 + 1u))) = 0xff;
    (*((uint8_t *)((uint8_t *)&uVar3 + 2u))) = 0xff;
    (*((uint8_t *)((uint8_t *)&uVar3 + 3u))) = 0xff;
  }
  bVar1 = f33_diagnostic_capture_slots[1].extended_middle[6] != '\0';
  FUN_0006a574(uVar2, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  FUN_0006a55c(uVar3, ((undefined1 *)camry_host_ptr((uint32_t)(param_2 + 2))));
  (*((bool *)camry_host_ptr((uint32_t)(param_2 + 6)))) = bVar1;
  return;
}



/* Capture-slot field dispatch: reads one field from a diagnostic capture slot record and passes it
   through a fixed transform to one dispatch callee; shape-verified family of per-field accessors.
    */

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



/* Capture-slot field dispatch: reads one field from a diagnostic capture slot record and passes it
   through a fixed transform to one dispatch callee; shape-verified family of per-field accessors.
    */

void f33_capture_slot_dispatch_533a0(ushort param_1, undefined4 param_2)

{
  uint uVar1;
  
  uVar1 = (uint)(*((ushort *)camry_host_ptr((uint32_t)(f33_diagnostic_capture_slots[1].profile_prefix +
                 (short)(param_1 & 0xff) * 0x48 + 0x38)))) * 10 >> 7;
  if (2999 < uVar1) {
    uVar1 = 3000;
  }
  FUN_0006a574(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}



/* Capture-slot field dispatch: reads one field from a diagnostic capture slot record and passes it
   through a fixed transform to one dispatch callee; shape-verified family of per-field accessors.
    */

void f33_capture_slot_dispatch_533cc(ushort param_1, undefined4 param_2)

{
  ushort uVar1;
  
  uVar1 = (*((ushort *)camry_host_ptr((uint32_t)(f33_diagnostic_capture_slots[1].profile_prefix + (short)(param_1 & 0xff) * 0x48 + 0x3a))));
  if (0x31ff < uVar1) {
    uVar1 = 0x3200;
  }
  FUN_0006a574(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}



/* Capture-slot field dispatch: reads one field from a diagnostic capture slot record and passes it
   through a fixed transform to one dispatch callee; shape-verified family of per-field accessors.
    */

void f33_capture_slot_dispatch_53408(ushort param_1, undefined4 param_2)

{
  uint uVar1;
  
  uVar1 = (uint)(*((ushort *)camry_host_ptr((uint32_t)(f33_diagnostic_capture_slots[1].profile_prefix +
                 (short)(param_1 & 0xff) * 0x48 + 0x3e)))) * 100 >> 8;
  if (0x9c3 < uVar1) {
    uVar1 = 0x9c4;
  }
  FUN_0006a574(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}



/* WARNING: Removing unreachable block (ram,0x0005344c) */
/* Capture-slot field dispatch: reads one field from a diagnostic capture slot record and passes it
   through a fixed transform to one dispatch callee; shape-verified family of per-field accessors.
    */

void f33_capture_slot_dispatch_53434(ushort param_1, undefined4 param_2)

{
  int iVar1;
  
  iVar1 = ((*((short *)camry_host_ptr((uint32_t)(f33_diagnostic_capture_slots[1].profile_prefix +
                     (short)(param_1 & 0xff) * 0x48 + 0xc)))) * 1000) / 0x100;
  if (iVar1 + -25000 < 0 == (iVar1 < 0 && -1 < iVar1 + -25000)) {
    iVar1 = 25000;
  }
  if (iVar1 + 25000 < 0 != (-1 < iVar1 && iVar1 + 25000 < 0)) {
    iVar1 = -25000;
  }
  FUN_0006a5ac((int)(short)iVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}



/* WARNING: Removing unreachable block (ram,0x00053488) */
/* Capture-slot field dispatch: reads one field from a diagnostic capture slot record and passes it
   through a fixed transform to one dispatch callee; shape-verified family of per-field accessors.
    */

void f33_capture_slot_dispatch_53470(ushort param_1, undefined4 param_2)

{
  int iVar1;
  
  iVar1 = (int)(short)(((*((short *)camry_host_ptr((uint32_t)(f33_diagnostic_capture_slots[1].profile_prefix +
                                  (short)(param_1 & 0xff) * 0x48 + 8)))) * 0x168) / 0x400);
  if (iVar1 + -0x7fff < 0 == (iVar1 < 0 && -1 < iVar1 + -0x7fff)) {
    iVar1 = 0x7fff;
  }
  if (iVar1 + 0x7fff < 0 != (-1 < iVar1 && iVar1 + 0x7fff < 0)) {
    iVar1 = -0x7fff;
  }
  FUN_0006a5ac(iVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}



/* Capture-slot field dispatch: reads one field from a diagnostic capture slot record and passes it
   through a fixed transform to one dispatch callee; shape-verified family of per-field accessors.
    */

void f33_capture_slot_dispatch_534ac(ushort param_1, undefined4 param_2)

{
  int iVar1;
  
  iVar1 = (int)(*((short *)camry_host_ptr((uint32_t)(f33_diagnostic_capture_slots[1].profile_prefix +
                         (short)(param_1 & 0xff) * 0x48 + 0x40))));
  if (iVar1 + -0x7ff < 0 == (iVar1 < 0 && -1 < iVar1 + -0x7ff)) {
    iVar1 = 0x7ff;
  }
  if (iVar1 + 0x800 < 0 != (-1 < iVar1 && iVar1 + 0x800 < 0)) {
    iVar1 = -0x800;
  }
  FUN_0006a5ac(iVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}



/* Capture-slot field dispatch: reads one field from a diagnostic capture slot record and passes it
   through a fixed transform to one dispatch callee; shape-verified family of per-field accessors.
    */

void f33_capture_slot_dispatch_534da(ushort param_1, undefined4 param_2)

{
  uint uVar1;
  
  uVar1 = (uint)(*((ushort *)camry_host_ptr((uint32_t)(f33_diagnostic_capture_slots[1].profile_prefix +
                 (short)(param_1 & 0xff) * 0x48 + 10)))) * 100 >> 8;
  if (0x9c3 < uVar1) {
    uVar1 = 0x9c4;
  }
  FUN_0006a574(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}



/* Capture-slot field dispatch: reads one field from a diagnostic capture slot record and passes it
   through a fixed transform to one dispatch callee; shape-verified family of per-field accessors.
    */

void f33_capture_slot_dispatch_53506(ushort param_1, undefined4 param_2)

{
  uint uVar1;
  
  uVar1 = (uint)(*((ushort *)camry_host_ptr((uint32_t)(f33_diagnostic_capture_slots[1].profile_prefix +
                 (short)(param_1 & 0xff) * 0x48 + 0x36)))) * 100 >> 8;
  if (0x9c3 < uVar1) {
    uVar1 = 0x9c4;
  }
  FUN_0006a574(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}



/* WARNING: Removing unreachable block (ram,0x0005353a) */

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



/* Capture-slot field dispatch: reads one field from a diagnostic capture slot record and passes it
   through a fixed transform to one dispatch callee; shape-verified family of per-field accessors.
    */

void f33_capture_slot_dispatch_53558(undefined4 param_1, undefined4 param_2)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  
  iVar1 = (int)(short)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * 240u + 222u))));
  iVar3 = (int)(short)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * 240u + 150u))));
  if (iVar1 - iVar3 < 0 == (iVar1 < 0 != iVar3 < 0 && iVar3 < 0 == iVar1 - iVar3 < 0) &&
      iVar1 != iVar3) {
    iVar3 = iVar1;
  }
  uVar2 = FUN_00053532(iVar3);
  FUN_0006a5ac(uVar2, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}



/* Capture-slot field dispatch: reads one field from a diagnostic capture slot record and passes it
   through a fixed transform to one dispatch callee; shape-verified family of per-field accessors.
    */

void f33_capture_slot_dispatch_53578(undefined4 param_1, undefined4 param_2)

{
  undefined4 uVar1;
  
  uVar1 = 0x7fff;
  if (f33_diagnostic_capture_slots[1].ecu_thermal_source != '\0') {
    uVar1 = FUN_00053532((int)f33_diagnostic_capture_slots[1].ecu_thermal_estimate);
  }
  FUN_0006a5ac(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}



/* Capture-slot field dispatch: reads one field from a diagnostic capture slot record and passes it
   through a fixed transform to one dispatch callee; shape-verified family of per-field accessors.
    */

void f33_capture_slot_dispatch_5359a(undefined4 param_1, undefined4 param_2)

{
  undefined4 uVar1;
  
  uVar1 = 0x7fff;
  if (f33_diagnostic_capture_slots[1].motor_thermal_active != '\0') {
    uVar1 = FUN_00053532((int)f33_diagnostic_capture_slots[1].motor_thermal_estimate);
  }
  FUN_0006a5ac(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}



/* WARNING: Removing unreachable block (ram,0x00053610) */

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



/* Capture-slot field dispatch: reads one field from a diagnostic capture slot record and passes it
   through a fixed transform to one dispatch callee; shape-verified family of per-field accessors.
    */

void f33_capture_slot_dispatch_5362e(undefined4 param_1, undefined4 param_2)

{
  undefined4 uVar1;
  
  uVar1 = FUN_00053608((int)(short)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * 240u + 164u)))));
  FUN_0006a5ac(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}



/* Capture-slot field dispatch: reads one field from a diagnostic capture slot record and passes it
   through a fixed transform to one dispatch callee; shape-verified family of per-field accessors.
    */

void f33_capture_slot_dispatch_53644(undefined4 param_1, undefined4 param_2)

{
  undefined4 uVar1;
  
  uVar1 = FUN_00053608((int)(short)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * 240u + 166u)))));
  FUN_0006a5ac(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}



/* Capture-slot field dispatch: reads one field from a diagnostic capture slot record and passes it
   through a fixed transform to one dispatch callee; shape-verified family of per-field accessors.
    */

void f33_capture_slot_dispatch_5365a(undefined4 param_1, undefined4 param_2)

{
  undefined4 uVar1;
  
  uVar1 = FUN_00053608((int)(short)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * 240u + 168u)))));
  FUN_0006a5ac(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}



/* Capture-slot field dispatch: reads one field from a diagnostic capture slot record and passes it
   through a fixed transform to one dispatch callee; shape-verified family of per-field accessors.
    */

void f33_capture_slot_dispatch_53670(undefined4 param_1, undefined4 param_2)

{
  undefined4 uVar1;
  
  uVar1 = FUN_00053608((int)(short)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * 240u + 170u)))));
  FUN_0006a5ac(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}



/* WARNING: Removing unreachable block (ram,0x0005368e) */

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



/* Capture-slot field dispatch: reads one field from a diagnostic capture slot record and passes it
   through a fixed transform to one dispatch callee; shape-verified family of per-field accessors.
    */

void f33_capture_slot_dispatch_536ac(ushort param_1, undefined4 param_2)

{
  undefined4 uVar1;
  
  uVar1 = FUN_00053686((int)(*((short *)camry_host_ptr((uint32_t)(f33_diagnostic_capture_slots[1].profile_prefix +
                                      (short)(param_1 & 0xff) * 0x48 + 0x1c)))));
  FUN_0006a5ac(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}



/* Capture-slot field dispatch: reads one field from a diagnostic capture slot record and passes it
   through a fixed transform to one dispatch callee; shape-verified family of per-field accessors.
    */

void f33_capture_slot_dispatch_536ca(ushort param_1, undefined4 param_2)

{
  undefined4 uVar1;
  
  uVar1 = FUN_00053686((int)(*((short *)camry_host_ptr((uint32_t)(f33_diagnostic_capture_slots[1].profile_prefix +
                                      (short)(param_1 & 0xff) * 0x48 + 0x1e)))));
  FUN_0006a5ac(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}



/* Capture-slot field dispatch: reads one field from a diagnostic capture slot record and passes it
   through a fixed transform to one dispatch callee; shape-verified family of per-field accessors.
    */

void f33_capture_slot_dispatch_536e8(ushort param_1, undefined4 param_2)

{
  undefined4 uVar1;
  
  uVar1 = FUN_00053686((int)(*((short *)camry_host_ptr((uint32_t)(f33_diagnostic_capture_slots[1].profile_prefix +
                                      (short)(param_1 & 0xff) * 0x48 + 0x20)))));
  FUN_0006a5ac(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
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



/* Capture-slot field dispatch: reads one field from a diagnostic capture slot record and passes it
   through a fixed transform to one dispatch callee; shape-verified family of per-field accessors.
    */

void f33_capture_slot_dispatch_53722(ushort param_1, undefined4 param_2)

{
  undefined4 uVar1;
  
  uVar1 = FUN_00053706((*((undefined2 *)camry_host_ptr((uint32_t)(f33_diagnostic_capture_slots[1].profile_prefix +
                        (short)(param_1 & 0xff) * 0x48 + 0x28)))));
  FUN_0006a574(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}



/* Capture-slot field dispatch: reads one field from a diagnostic capture slot record and passes it
   through a fixed transform to one dispatch callee; shape-verified family of per-field accessors.
    */

void f33_capture_slot_dispatch_53740(ushort param_1, undefined4 param_2)

{
  undefined4 uVar1;
  
  uVar1 = FUN_00053706((*((undefined2 *)camry_host_ptr((uint32_t)(f33_diagnostic_capture_slots[1].profile_prefix +
                        (short)(param_1 & 0xff) * 0x48 + 0x2a)))));
  FUN_0006a574(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}



/* Capture-slot field dispatch: reads one field from a diagnostic capture slot record and passes it
   through a fixed transform to one dispatch callee; shape-verified family of per-field accessors.
    */

void f33_capture_slot_dispatch_5375e(ushort param_1, undefined4 param_2)

{
  undefined4 uVar1;
  
  uVar1 = FUN_00053706((*((undefined2 *)camry_host_ptr((uint32_t)(f33_diagnostic_capture_slots[1].profile_prefix +
                        (short)(param_1 & 0xff) * 0x48 + 0x2c)))));
  FUN_0006a574(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
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



/* Capture-slot field dispatch: reads one field from a diagnostic capture slot record and passes it
   through a fixed transform to one dispatch callee; shape-verified family of per-field accessors.
    */

void f33_capture_slot_dispatch_53794(ushort param_1, undefined4 param_2)

{
  undefined4 uVar1;
  
  uVar1 = FUN_0005377c((*((undefined2 *)camry_host_ptr((uint32_t)(f33_diagnostic_capture_slots[1].profile_prefix +
                        (short)(param_1 & 0xff) * 0x48 + 0x10)))));
  FUN_0006a574(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}



/* Capture-slot field dispatch: reads one field from a diagnostic capture slot record and passes it
   through a fixed transform to one dispatch callee; shape-verified family of per-field accessors.
    */

void f33_capture_slot_dispatch_537b2(ushort param_1, undefined4 param_2)

{
  undefined4 uVar1;
  
  uVar1 = FUN_0005377c((*((undefined2 *)camry_host_ptr((uint32_t)(f33_diagnostic_capture_slots[1].profile_prefix +
                        (short)(param_1 & 0xff) * 0x48 + 0x12)))));
  FUN_0006a574(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}



/* Capture-slot field dispatch: reads one field from a diagnostic capture slot record and passes it
   through a fixed transform to one dispatch callee; shape-verified family of per-field accessors.
    */

void f33_capture_slot_dispatch_537d0(ushort param_1, undefined4 param_2)

{
  undefined4 uVar1;
  
  uVar1 = FUN_0005377c((*((undefined2 *)camry_host_ptr((uint32_t)(f33_diagnostic_capture_slots[1].profile_prefix +
                        (short)(param_1 & 0xff) * 0x48 + 0x14)))));
  FUN_0006a574(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}



/* Capture-slot field dispatch: reads one field from a diagnostic capture slot record and passes it
   through a fixed transform to one dispatch callee; shape-verified family of per-field accessors.
    */

void f33_capture_slot_dispatch_537ee(ushort param_1, undefined4 param_2)

{
  uint uVar1;
  
  uVar1 = (uint)(*((ushort *)camry_host_ptr((uint32_t)(f33_diagnostic_capture_slots[1].profile_prefix +
                 (short)(param_1 & 0xff) * 0x48 + 0x34)))) * 100 >> 8;
  if (0x9c3 < uVar1) {
    uVar1 = 0x9c4;
  }
  FUN_0006a574(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}



/* Capture-slot field dispatch: reads one field from a diagnostic capture slot record and passes it
   through a fixed transform to one dispatch callee; shape-verified family of per-field accessors.
    */

void f33_capture_slot_dispatch_5381a(ushort param_1, undefined4 param_2)

{
  undefined4 uVar1;
  
  uVar1 = FUN_00053686((int)(*((short *)camry_host_ptr((uint32_t)(f33_diagnostic_capture_slots[1].profile_prefix +
                                      (short)(param_1 & 0xff) * 0x48 + 0x22)))));
  FUN_0006a5ac(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}



/* Capture-slot field dispatch: reads one field from a diagnostic capture slot record and passes it
   through a fixed transform to one dispatch callee; shape-verified family of per-field accessors.
    */

void f33_capture_slot_dispatch_53838(ushort param_1, undefined4 param_2)

{
  undefined4 uVar1;
  
  uVar1 = FUN_00053686((int)(*((short *)camry_host_ptr((uint32_t)(f33_diagnostic_capture_slots[1].profile_prefix +
                                      (short)(param_1 & 0xff) * 0x48 + 0x24)))));
  FUN_0006a5ac(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}



/* Capture-slot field dispatch: reads one field from a diagnostic capture slot record and passes it
   through a fixed transform to one dispatch callee; shape-verified family of per-field accessors.
    */

void f33_capture_slot_dispatch_53856(ushort param_1, undefined4 param_2)

{
  undefined4 uVar1;
  
  uVar1 = FUN_00053686((int)(*((short *)camry_host_ptr((uint32_t)(f33_diagnostic_capture_slots[1].profile_prefix +
                                      (short)(param_1 & 0xff) * 0x48 + 0x26)))));
  FUN_0006a5ac(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}



/* Capture-slot field dispatch: reads one field from a diagnostic capture slot record and passes it
   through a fixed transform to one dispatch callee; shape-verified family of per-field accessors.
    */

void f33_capture_slot_dispatch_53874(ushort param_1, undefined4 param_2)

{
  undefined4 uVar1;
  
  uVar1 = FUN_00053706((*((undefined2 *)camry_host_ptr((uint32_t)(f33_diagnostic_capture_slots[1].profile_prefix +
                        (short)(param_1 & 0xff) * 0x48 + 0x2e)))));
  FUN_0006a574(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}



/* Capture-slot field dispatch: reads one field from a diagnostic capture slot record and passes it
   through a fixed transform to one dispatch callee; shape-verified family of per-field accessors.
    */

void f33_capture_slot_dispatch_53892(ushort param_1, undefined4 param_2)

{
  undefined4 uVar1;
  
  uVar1 = FUN_00053706((*((undefined2 *)camry_host_ptr((uint32_t)(f33_diagnostic_capture_slots[1].profile_prefix +
                        (short)(param_1 & 0xff) * 0x48 + 0x30)))));
  FUN_0006a574(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}



/* Capture-slot field dispatch: reads one field from a diagnostic capture slot record and passes it
   through a fixed transform to one dispatch callee; shape-verified family of per-field accessors.
    */

void f33_capture_slot_dispatch_538b0(ushort param_1, undefined4 param_2)

{
  undefined4 uVar1;
  
  uVar1 = FUN_00053706((*((undefined2 *)camry_host_ptr((uint32_t)(f33_diagnostic_capture_slots[1].profile_prefix +
                        (short)(param_1 & 0xff) * 0x48 + 0x32)))));
  FUN_0006a574(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}



/* Capture-slot field dispatch: reads one field from a diagnostic capture slot record and passes it
   through a fixed transform to one dispatch callee; shape-verified family of per-field accessors.
    */

void f33_capture_slot_dispatch_538ce(ushort param_1, undefined4 param_2)

{
  undefined4 uVar1;
  
  uVar1 = FUN_0005377c((*((undefined2 *)camry_host_ptr((uint32_t)(f33_diagnostic_capture_slots[1].profile_prefix +
                        (short)(param_1 & 0xff) * 0x48 + 0x16)))));
  FUN_0006a574(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}



/* Capture-slot field dispatch: reads one field from a diagnostic capture slot record and passes it
   through a fixed transform to one dispatch callee; shape-verified family of per-field accessors.
    */

void f33_capture_slot_dispatch_538ec(ushort param_1, undefined4 param_2)

{
  undefined4 uVar1;
  
  uVar1 = FUN_0005377c((*((undefined2 *)camry_host_ptr((uint32_t)(f33_diagnostic_capture_slots[1].profile_prefix +
                        (short)(param_1 & 0xff) * 0x48 + 0x18)))));
  FUN_0006a574(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}



/* Capture-slot field dispatch: reads one field from a diagnostic capture slot record and passes it
   through a fixed transform to one dispatch callee; shape-verified family of per-field accessors.
    */

void f33_capture_slot_dispatch_5390a(ushort param_1, undefined4 param_2)

{
  undefined4 uVar1;
  
  uVar1 = FUN_0005377c((*((undefined2 *)camry_host_ptr((uint32_t)(f33_diagnostic_capture_slots[1].profile_prefix +
                        (short)(param_1 & 0xff) * 0x48 + 0x1a)))));
  FUN_0006a574(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}



/* Capture-slot field dispatch: reads one field from a diagnostic capture slot record and passes it
   through a fixed transform to one dispatch callee; shape-verified family of per-field accessors.
    */

void f33_capture_slot_dispatch_53928(ushort param_1, undefined4 param_2)

{
  undefined4 uVar1;
  
  uVar1 = FUN_00053686((int)(*((short *)camry_host_ptr((uint32_t)(f33_diagnostic_capture_slots[1].profile_prefix +
                                      (short)(param_1 & 0xff) * 0x48 + 4)))));
  FUN_0006a5ac(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}



/* Capture-slot field dispatch: reads one field from a diagnostic capture slot record and passes it
   through a fixed transform to one dispatch callee; shape-verified family of per-field accessors.
    */

void f33_capture_slot_dispatch_53946(ushort param_1, undefined4 param_2)

{
  undefined4 uVar1;
  
  uVar1 = FUN_00053686((int)(*((short *)camry_host_ptr((uint32_t)(f33_diagnostic_capture_slots[1].profile_prefix +
                                      (short)(param_1 & 0xff) * 0x48 + 6)))));
  FUN_0006a5ac(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}



/* Capture-slot field dispatch: reads one field from a diagnostic capture slot record and passes it
   through a fixed transform to one dispatch callee; shape-verified family of per-field accessors.
    */

void f33_capture_slot_dispatch_53964(ushort param_1, undefined4 param_2)

{
  undefined4 uVar1;
  
  uVar1 = FUN_00053686((int)(*((short *)camry_host_ptr((uint32_t)(f33_diagnostic_capture_slots[1].profile_prefix +
                                      (short)(param_1 & 0xff) * 0x48 + 0xe)))));
  FUN_0006a5ac(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}



/* Capture-slot field dispatch: reads one field from a diagnostic capture slot record and passes it
   through a fixed transform to one dispatch callee; shape-verified family of per-field accessors.
    */

void f33_capture_slot_dispatch_53982(ushort param_1, undefined4 param_2)

{
  undefined4 uVar1;
  
  uVar1 = FUN_00053686((int)(*((short *)camry_host_ptr((uint32_t)(f33_diagnostic_capture_slots[1].profile_prefix +
                                      (short)(param_1 & 0xff) * 0x48 + 0x3c)))));
  FUN_0006a5ac(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}



/* Capture-slot field dispatch: reads one field from a diagnostic capture slot record and passes it
   through a fixed transform to one dispatch callee; shape-verified family of per-field accessors.
    */

void f33_capture_slot_dispatch_539a0(ushort param_1, undefined4 param_2)

{
  undefined *puVar1;
  
  puVar1 = ((undefined *)camry_host_ptr((uint32_t)((uint)*(ushort *)
                   (f33_diagnostic_capture_slots[1].profile_prefix + (short)(param_1 & 0xff) * 0x48)
            * 36000 >> 0x10)));
  if ((uintptr_t)(((undefined *)camry_host_ptr(0x8c9fu)))<(uintptr_t)(puVar1)) {
    puVar1 = ((undefined *)camry_host_ptr(0x8ca0u));
  }
  FUN_0006a574(camry_host_addr(puVar1), ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}



/* WARNING: Removing unreachable block (ram,0x000539f0) */
/* Capture-slot field dispatch: reads one field from a diagnostic capture slot record and passes it
   through a fixed transform to one dispatch callee; shape-verified family of per-field accessors.
    */

void f33_capture_slot_dispatch_539cc(ushort param_1,undefined4 param_2)

{
  short sStack_a;
  
  sStack_a = (short)(((*((short *)camry_host_ptr((uint32_t)(f33_diagnostic_capture_slots[1].profile_prefix +
                                (short)(param_1 & 0xff) * 0x48 + 0x44)))) * 100) / 0x80);
  FUN_00070110((int)sStack_a,0x7fff,0,&sStack_a);
  FUN_0006a5ac((int)sStack_a, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}



/* WARNING: Removing unreachable block (ram,0x00053a32) */

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



void FUN_00053a4e(void)

{
  undefined1 *extraout_r7;
  undefined1 uVar1;
  
  uVar1 = FUN_00053a2c((int)(short)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * 240u + 178u)))));
  *extraout_r7 = uVar1;
  return;
}



void FUN_00053a62(void)

{
  undefined1 *extraout_r7;
  undefined1 uVar1;
  
  uVar1 = FUN_00053a2c((int)(short)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * 240u + 180u)))));
  *extraout_r7 = uVar1;
  return;
}



/* Capture-slot field dispatch: reads one field from a diagnostic capture slot record and passes it
   through a fixed transform to one dispatch callee; shape-verified family of per-field accessors.
    */

void f33_capture_slot_dispatch_53a76(undefined4 param_1, undefined4 param_2)

{
  undefined2 uVar1;
  
  uVar1 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * 240u + 174u))));
  if (29999 < (ushort)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * 240u + 174u))))) {
    (*((uint8_t *)((uint8_t *)&uVar1 + 0u))) = '0';
    (*((uint8_t *)((uint8_t *)&uVar1 + 1u))) = 'u';
  }
  FUN_0006a574(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}



/* Capture-slot field dispatch: reads one field from a diagnostic capture slot record and passes it
   through a fixed transform to one dispatch callee; shape-verified family of per-field accessors.
    */

void f33_capture_slot_dispatch_53a92(undefined4 param_1, undefined4 param_2)

{
  int iVar1;
  
  iVar1 = (int)(short)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * 240u + 176u))));
  if (iVar1 + -0x7fff < 0 == (iVar1 < 0 && -1 < iVar1 + -0x7fff)) {
    iVar1 = 0x7fff;
  }
  if (iVar1 + 0x7fff < 0 != (-1 < iVar1 && iVar1 + 0x7fff < 0)) {
    iVar1 = -0x7fff;
  }
  FUN_0006a5ac(iVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}



/* WARNING: Removing unreachable block (ram,0x00053ad8) */
/* WARNING: Removing unreachable block (ram,0x00053acc) */
/* Capture-slot field dispatch: reads one field from a diagnostic capture slot record and passes it
   through a fixed transform to one dispatch callee; shape-verified family of per-field accessors.
    */

void f33_capture_slot_dispatch_53ab8(undefined4 param_1, undefined4 param_2)

{
  undefined2 *puVar1;
  
  puVar1 = ((undefined2 *)camry_host_ptr((uint32_t)((((int)((int)(short)f33_diagnostic_capture_slots[1].selected_sample * (uint)DAT_febee8a6
                   ) / 0x2000) * 100) / 0x100)));
  if ((int)0xffffb1e0u + (int)camry_host_addr(puVar1) < 0 ==
      ((int)camry_host_addr(puVar1) < 0 && -1 < (int)0xffffb1e0u + (int)camry_host_addr(puVar1))) {
    puVar1 = ((undefined2 *)camry_host_ptr((uint32_t)(0x4e20)));
  }
  if ((int)camry_host_addr((puVar1 + 10000)) < 0 != (-1 < (int)camry_host_addr(puVar1) && (int)camry_host_addr((puVar1 + 10000)) < 0)) {
    puVar1 = ((undefined *)camry_host_ptr(0xffffb1e0u));
  }
  FUN_0006a5ac((int)(short)puVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}



/* Capture-slot field dispatch: reads one field from a diagnostic capture slot record and passes it
   through a fixed transform to one dispatch callee; shape-verified family of per-field accessors.
    */

void f33_capture_slot_dispatch_53afc(undefined4 param_1, undefined4 param_2)

{
  FUN_0006a574((*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * 240u + 148u)))), ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}



/* WARNING: Removing unreachable block (ram,0x00053b24) */

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



/* Capture-slot field dispatch: reads one field from a diagnostic capture slot record and passes it
   through a fixed transform to one dispatch callee; shape-verified family of per-field accessors.
    */

void f33_capture_slot_dispatch_53b42(undefined4 param_1, undefined4 param_2)

{
  undefined4 uVar1;
  
  uVar1 = FUN_00053b1c((int)(short)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * 240u + 162u)))));
  FUN_0006a5ac(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}



/* Capture-slot field dispatch: reads one field from a diagnostic capture slot record and passes it
   through a fixed transform to one dispatch callee; shape-verified family of per-field accessors.
    */

void f33_capture_slot_dispatch_53b68(undefined4 param_1, undefined4 param_2)

{
  undefined4 uVar1;
  
  uVar1 = FUN_00053b1c((int)(short)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * 240u + 158u)))));
  FUN_0006a5ac(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}



/* Capture-slot field dispatch: reads one field from a diagnostic capture slot record and passes it
   through a fixed transform to one dispatch callee; shape-verified family of per-field accessors.
    */

void f33_capture_slot_dispatch_53b8e(undefined4 param_1, undefined4 param_2)

{
  undefined4 uVar1;
  
  uVar1 = FUN_00053b1c((int)(short)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * 240u + 154u)))));
  FUN_0006a5ac(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}



/* Capture-slot field dispatch: reads one field from a diagnostic capture slot record and passes it
   through a fixed transform to one dispatch callee; shape-verified family of per-field accessors.
    */

void f33_capture_slot_dispatch_53bb4(undefined4 param_1, undefined4 param_2)

{
  undefined4 uVar1;
  
  uVar1 = FUN_00053b1c((int)(short)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * 240u + 172u)))));
  FUN_0006a5ac(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}



/* Capture-slot field dispatch: reads one field from a diagnostic capture slot record and passes it
   through a fixed transform to one dispatch callee; shape-verified family of per-field accessors.
    */

void f33_capture_slot_dispatch_53bda(undefined4 param_1, undefined4 param_2)

{
  undefined4 uVar1;
  
  uVar1 = FUN_00053b1c((int)(short)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * 240u + 194u)))));
  FUN_0006a5ac(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}



/* Capture-slot field dispatch: reads one field from a diagnostic capture slot record and passes it
   through a fixed transform to one dispatch callee; shape-verified family of per-field accessors.
    */

void f33_capture_slot_dispatch_53c00(undefined4 param_1, undefined4 param_2)

{
  undefined4 uVar1;
  
  uVar1 = FUN_00053b1c((int)(short)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * 240u + 198u)))));
  FUN_0006a5ac(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}



/* Capture-slot field dispatch: reads one field from a diagnostic capture slot record and passes it
   through a fixed transform to one dispatch callee; shape-verified family of per-field accessors.
    */

void f33_capture_slot_dispatch_53c16(undefined4 param_1,int param_2)

{
  undefined4 uVar1;
  
  uVar1 = (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * 240u + 228u))));
  FUN_0006a55c((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * 240u + 224u)))), ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  FUN_0006a55c(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2 + 4))));
  return;
}



/* Capture-slot field dispatch: reads one field from a diagnostic capture slot record and passes it
   through a fixed transform to one dispatch callee; shape-verified family of per-field accessors.
    */

void f33_capture_slot_dispatch_53c36(undefined4 param_1,undefined4 param_2)

{
  undefined2 uStack_a;
  
  uStack_a = (undefined2)
             ((uint)(ushort)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * 240u + 204u)))) * 36000 >> 0x10);
  FUN_00070180((uint)(ushort)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * 240u + 204u)))) * 36000 >> 0x10, camry_host_addr(((undefined *)camry_host_ptr(0x8ca0u))), &uStack_a);
  FUN_0006a574(uStack_a, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}



/* Capture-slot field dispatch: reads one field from a diagnostic capture slot record and passes it
   through a fixed transform to one dispatch callee; shape-verified family of per-field accessors.
    */

void f33_capture_slot_dispatch_53c68(undefined4 param_1,undefined4 param_2)

{
  undefined2 uStack_a;
  
  uStack_a = (undefined2)
             ((uint)(ushort)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * 240u + 206u)))) * 36000 >> 0x10);
  FUN_00070180((uint)(ushort)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * 240u + 206u)))) * 36000 >> 0x10, camry_host_addr(((undefined *)camry_host_ptr(0x8ca0u))), &uStack_a);
  FUN_0006a574(uStack_a, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}



/* Capture-slot field dispatch: reads one field from a diagnostic capture slot record and passes it
   through a fixed transform to one dispatch callee; shape-verified family of per-field accessors.
    */

void f33_capture_slot_dispatch_53c9a(undefined4 param_1, undefined4 param_2)

{
  FUN_0006a574((*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * 240u + 208u)))), ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}



/* Capture-slot field dispatch: reads one field from a diagnostic capture slot record and passes it
   through a fixed transform to one dispatch callee; shape-verified family of per-field accessors.
    */

void f33_capture_slot_dispatch_53caa(undefined4 param_1, undefined4 param_2)

{
  FUN_0006a574((*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * 240u + 210u)))), ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}



/* Capture-slot field dispatch: reads one field from a diagnostic capture slot record and passes it
   through a fixed transform to one dispatch callee; shape-verified family of per-field accessors.
    */

void f33_capture_slot_dispatch_53cba(undefined4 param_1, undefined4 param_2)

{
  FUN_0006a574((*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * 240u + 212u)))), ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}



/* Capture-slot field dispatch: reads one field from a diagnostic capture slot record and passes it
   through a fixed transform to one dispatch callee; shape-verified family of per-field accessors.
    */

void f33_capture_slot_dispatch_53cca(undefined4 param_1, undefined4 param_2)

{
  FUN_0006a574((*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe82dcu + (uint32_t)(1) * 240u + 214u)))), ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_53db2(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_53db4(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_53db6(void)

{
  return;
}



/* Populate profile/extended fields from staged software sources and kind10 application sample.
   Preserve supplemental/event regions for52E18. Thermal D8/DA/DC/DD fields copy
   6F7A/6F7C/6F6C/6F6D; selected sampleB8 comes fromAFA4. Kind10 profile source bank plus56-byte
   application projection; leave supplement/event words to caller. RecordB8 selectsAFA4 and
   D8/DA/DC/DD copy6F7A/6F7C/6F6C/6F6D. */

void f33_build_diagnostic_capture_kind10(F33DiagnosticCapture *output)

{
  undefined2 uVar1;
  uchar uVar2;
  uint32_t puVar3;
  F33DiagnosticApplicationSample local_40;
  
  puVar3 = 0xfebeb800u;
  f33_snapshot_diagnostic_application(&local_40,10);
  *(undefined4 *)output->profile_prefix = (*((undefined4 *)camry_host_ptr((uint32_t)(puVar3 + -0x544c))));
  *(undefined2 *)(output->profile_prefix + 8) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x542c))));
  output->profile_prefix[0x42] = local_40.raw[0];
  *(undefined2 *)(output->profile_prefix + 4) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x53f2))));
  *(undefined2 *)(output->profile_prefix + 6) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x53e0))));
  *(undefined2 *)(output->profile_prefix + 10) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3a50))));
  *(undefined2 *)(output->profile_prefix + 0xc) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x5428))));
  *(undefined2 *)(output->profile_prefix + 0xe) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x53f4))));
  *(undefined2 *)(output->profile_prefix + 0x10) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3964))));
  *(undefined2 *)(output->profile_prefix + 0x12) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3962))));
  *(undefined2 *)(output->profile_prefix + 0x14) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3960))));
  *(undefined2 *)(output->profile_prefix + 0x16) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x395e))));
  *(undefined2 *)(output->profile_prefix + 0x18) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x395c))));
  *(undefined2 *)(output->profile_prefix + 0x1a) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x395a))));
  *(undefined2 *)(output->profile_prefix + 0x1c) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x5470))));
  *(undefined2 *)(output->profile_prefix + 0x1e) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x546e))));
  *(undefined2 *)(output->profile_prefix + 0x20) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x546c))));
  *(undefined2 *)(output->profile_prefix + 0x22) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x546a))));
  *(undefined2 *)(output->profile_prefix + 0x24) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x5468))));
  *(undefined2 *)(output->profile_prefix + 0x26) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x5466))));
  *(undefined2 *)(output->profile_prefix + 0x28) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x55a2))));
  *(undefined2 *)(output->profile_prefix + 0x2a) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x55a0))));
  *(undefined2 *)(output->profile_prefix + 0x2c) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x559e))));
  *(undefined2 *)(output->profile_prefix + 0x2e) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x559c))));
  *(undefined2 *)(output->profile_prefix + 0x30) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x559a))));
  *(undefined2 *)(output->profile_prefix + 0x32) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x5598))));
  *(undefined2 *)(output->profile_prefix + 0x34) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3a5a))));
  *(undefined2 *)(output->profile_prefix + 0x36) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3a58))));
  *(undefined2 *)(output->profile_prefix + 0x38) = (*((uint16_t *)((uint8_t *)&local_40 + 10u)));
  *(undefined2 *)(output->profile_prefix + 0x3a) = (*((uint16_t *)((uint8_t *)&local_40 + 12u)));
  *(undefined2 *)(output->profile_prefix + 0x3c) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x53de))));
  *(undefined2 *)(output->profile_prefix + 0x3e) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3a4e))));
  uVar1 = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3aba))));
  output->profile_prefix[0x46] = '\0';
  output->profile_prefix[0x47] = '\0';
  *(undefined2 *)(output->profile_prefix + 0x40) = uVar1;
  *(undefined2 *)(output->profile_prefix + 0x44) = (*((uint16_t *)((uint8_t *)&local_40 + 24u)));
  output->profile_prefix[0x43] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3814)))));
  output->extended_prefix[5] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x37fa)))));
  *(undefined2 *)output->extended_prefix = (*((uint16_t *)((uint8_t *)&local_40 + 14u)));
  *(undefined2 *)(output->extended_prefix + 2) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3a32))));
  output->extended_prefix[4] = local_40.raw[1];
  output->extended_prefix[0xc] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3abc)))));
  output->extended_prefix[8] = local_40.raw[2];
  *(undefined2 *)(output->extended_prefix + 6) = (*((uint16_t *)((uint8_t *)&local_40 + 18u)));
  output->extended_prefix[9] = local_40.raw[3];
  *(undefined2 *)(output->extended_prefix + 10) = (*((uint16_t *)((uint8_t *)&local_40 + 20u)));
  output->extended_prefix[0xd] = local_40.raw[4];
  *(undefined2 *)(output->extended_prefix + 0xe) = (*((uint16_t *)((uint8_t *)&local_40 + 22u)));
  *(undefined2 *)(output->extended_prefix + 0x10) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x5552))));
  *(undefined2 *)(output->extended_prefix + 0x12) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x5550))));
  *(undefined2 *)(output->extended_prefix + 0x14) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x554e))));
  *(undefined2 *)(output->extended_prefix + 0x16) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x554c))));
  *(undefined2 *)(output->extended_prefix + 0x1a) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3766))));
  *(undefined2 *)(output->extended_prefix + 0x1c) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x37b6))));
  *(undefined2 *)(output->extended_prefix + 0x1e) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x37a0))));
  *(undefined2 *)(output->extended_prefix + 0x20) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x379e))));
  output->extended_prefix[0x22] = local_40.raw[5];
  output->selected_sample = (*((uint16_t *)((uint8_t *)&local_40 + 26u)));
  output->extended_prefix[0x23] = '\x11';
  *(undefined2 *)output->extended_middle = (*((uint16_t *)((uint8_t *)&local_40 + 16u)));
  *(undefined4 *)(output->extended_middle + 2) = (*((uint32_t *)((uint8_t *)&local_40 + 32u)));
  output->extended_middle[6] = local_40.raw[6];
  output->extended_middle[7] = local_40.raw[7];
  *(undefined4 *)(output->extended_middle + 0xe) = (*((uint32_t *)((uint8_t *)&local_40 + 36u)));
  output->extended_tail[10] = local_40.raw[0x28];
  output->extended_tail[0xb] = local_40.raw[0x29];
  output->extended_tail[0xc] = local_40.raw[0x2a];
  output->extended_tail[0xd] = local_40.raw[0x2b];
  output->extended_tail[0xe] = local_40.raw[0x2c];
  output->extended_tail[0xf] = local_40.raw[0x2d];
  output->extended_middle[10] = local_40.raw[8];
  *(undefined2 *)(output->extended_middle + 8) = (*((uint16_t *)((uint8_t *)&local_40 + 28u)));
  output->extended_middle[0xb] = local_40.raw[9];
  *(undefined2 *)(output->extended_middle + 0xc) = (*((uint16_t *)((uint8_t *)&local_40 + 30u)));
  output->extended_tail[0x10] = local_40.raw[0x30];
  *(undefined2 *)(output->extended_prefix + 0x18) = (*((uint16_t *)((uint8_t *)&local_40 + 46u)));
  *(undefined2 *)(output->extended_middle + 0x12) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x54ac))));
  *(undefined2 *)(output->extended_middle + 0x14) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x54aa))));
  *(undefined2 *)(output->extended_middle + 0x16) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x54a4))));
  *(undefined2 *)(output->extended_middle + 0x18) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x54a8))));
  *(undefined2 *)(output->extended_middle + 0x1a) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x54a6))));
  *(undefined2 *)(output->extended_middle + 0x1c) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x54a2))));
  output->ecu_thermal_estimate = (*((short *)camry_host_ptr((uint32_t)((0xffffb77au + (uint32_t)((int)puVar3))))));
  output->motor_thermal_estimate = (*((short *)camry_host_ptr((uint32_t)((0xffffb77cu + (uint32_t)((int)puVar3))))));
  output->ecu_thermal_source = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb76cu + (uint32_t)((int)puVar3) * 1u))));
  uVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb76du + (uint32_t)((int)puVar3) * 1u))));
  output->extended_tail[0x11] = '\0';
  output->motor_thermal_active = uVar2;
  *(undefined2 *)output->extended_tail = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3a2a))));
  *(undefined4 *)(output->extended_tail + 2) = (*((undefined4 *)camry_host_ptr((uint32_t)(puVar3 + -0x3568))));
  *(undefined4 *)(output->extended_tail + 6) = (*((undefined4 *)camry_host_ptr((uint32_t)(puVar3 + -0x3564))));
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_53ff8(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_53ffa(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_53ffc(void)

{
  return;
}



/* Kind4 staged source bank; selected sampleB8 comes fromAC56. Same240-byte layout and thermal
   publication fields, but not the same acquisition generation as kind10. Kind4 source bank
   shares240-byte capture layout and thermal projection but selectsAC56 sample, not kind10 AFA4. */

void f33_build_diagnostic_capture_kind4(F33DiagnosticCapture *output)

{
  undefined2 uVar1;
  uchar uVar2;
  uint32_t puVar3;
  F33DiagnosticApplicationSample local_40;
  
  puVar3 = 0xfebeb800u;
  f33_snapshot_diagnostic_application(&local_40,4);
  *(undefined4 *)output->profile_prefix = (*((undefined4 *)camry_host_ptr((uint32_t)(puVar3 + -0x55f8))));
  *(undefined2 *)(output->profile_prefix + 8) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x55f4))));
  output->profile_prefix[0x42] = local_40.raw[0];
  *(undefined2 *)(output->profile_prefix + 4) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x55ea))));
  *(undefined2 *)(output->profile_prefix + 6) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x55d8))));
  *(undefined2 *)(output->profile_prefix + 10) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3a50))));
  *(undefined2 *)(output->profile_prefix + 0xc) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x39f4))));
  *(undefined2 *)(output->profile_prefix + 0xe) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x55ec))));
  *(undefined2 *)(output->profile_prefix + 0x10) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3964))));
  *(undefined2 *)(output->profile_prefix + 0x12) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3962))));
  *(undefined2 *)(output->profile_prefix + 0x14) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3960))));
  *(undefined2 *)(output->profile_prefix + 0x16) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x395e))));
  *(undefined2 *)(output->profile_prefix + 0x18) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x395c))));
  *(undefined2 *)(output->profile_prefix + 0x1a) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x395a))));
  *(undefined2 *)(output->profile_prefix + 0x1c) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x561c))));
  *(undefined2 *)(output->profile_prefix + 0x1e) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x561a))));
  *(undefined2 *)(output->profile_prefix + 0x20) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x5618))));
  *(undefined2 *)(output->profile_prefix + 0x22) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x5616))));
  *(undefined2 *)(output->profile_prefix + 0x24) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x5614))));
  *(undefined2 *)(output->profile_prefix + 0x26) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x5612))));
  *(undefined2 *)(output->profile_prefix + 0x28) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x5696))));
  *(undefined2 *)(output->profile_prefix + 0x2a) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x5694))));
  *(undefined2 *)(output->profile_prefix + 0x2c) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x5692))));
  *(undefined2 *)(output->profile_prefix + 0x2e) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x5690))));
  *(undefined2 *)(output->profile_prefix + 0x30) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x568e))));
  *(undefined2 *)(output->profile_prefix + 0x32) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x568c))));
  *(undefined2 *)(output->profile_prefix + 0x34) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3a5a))));
  *(undefined2 *)(output->profile_prefix + 0x36) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3a58))));
  *(undefined2 *)(output->profile_prefix + 0x38) = (*((uint16_t *)((uint8_t *)&local_40 + 10u)));
  *(undefined2 *)(output->profile_prefix + 0x3a) = (*((uint16_t *)((uint8_t *)&local_40 + 12u)));
  *(undefined2 *)(output->profile_prefix + 0x3c) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x55d6))));
  *(undefined2 *)(output->profile_prefix + 0x3e) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3a4e))));
  uVar1 = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3aba))));
  output->profile_prefix[0x46] = '\0';
  output->profile_prefix[0x47] = '\0';
  *(undefined2 *)(output->profile_prefix + 0x40) = uVar1;
  *(undefined2 *)(output->profile_prefix + 0x44) = (*((uint16_t *)((uint8_t *)&local_40 + 24u)));
  output->profile_prefix[0x43] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3814)))));
  output->extended_prefix[5] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x37fa)))));
  *(undefined2 *)output->extended_prefix = (*((uint16_t *)((uint8_t *)&local_40 + 14u)));
  *(undefined2 *)(output->extended_prefix + 2) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3a32))));
  output->extended_prefix[4] = local_40.raw[1];
  output->extended_prefix[0xc] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3abc)))));
  output->extended_prefix[8] = local_40.raw[2];
  *(undefined2 *)(output->extended_prefix + 6) = (*((uint16_t *)((uint8_t *)&local_40 + 18u)));
  output->extended_prefix[9] = local_40.raw[3];
  *(undefined2 *)(output->extended_prefix + 10) = (*((uint16_t *)((uint8_t *)&local_40 + 20u)));
  output->extended_prefix[0xd] = local_40.raw[4];
  *(undefined2 *)(output->extended_prefix + 0xe) = (*((uint16_t *)((uint8_t *)&local_40 + 22u)));
  *(undefined2 *)(output->extended_prefix + 0x10) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3a14))));
  *(undefined2 *)(output->extended_prefix + 0x12) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3a12))));
  *(undefined2 *)(output->extended_prefix + 0x14) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3a10))));
  *(undefined2 *)(output->extended_prefix + 0x16) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3a0e))));
  *(undefined2 *)(output->extended_prefix + 0x1a) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3766))));
  *(undefined2 *)(output->extended_prefix + 0x1c) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x37b6))));
  *(undefined2 *)(output->extended_prefix + 0x1e) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x37a0))));
  *(undefined2 *)(output->extended_prefix + 0x20) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x379e))));
  output->extended_prefix[0x22] = local_40.raw[5];
  output->selected_sample = (*((uint16_t *)((uint8_t *)&local_40 + 26u)));
  output->extended_prefix[0x23] = '\x11';
  *(undefined2 *)output->extended_middle = (*((uint16_t *)((uint8_t *)&local_40 + 16u)));
  *(undefined4 *)(output->extended_middle + 2) = (*((uint32_t *)((uint8_t *)&local_40 + 32u)));
  output->extended_middle[6] = local_40.raw[6];
  output->extended_middle[7] = local_40.raw[7];
  *(undefined4 *)(output->extended_middle + 0xe) = (*((uint32_t *)((uint8_t *)&local_40 + 36u)));
  output->extended_tail[10] = local_40.raw[0x28];
  output->extended_tail[0xb] = local_40.raw[0x29];
  output->extended_tail[0xc] = local_40.raw[0x2a];
  output->extended_tail[0xd] = local_40.raw[0x2b];
  output->extended_tail[0xe] = local_40.raw[0x2c];
  output->extended_tail[0xf] = local_40.raw[0x2d];
  output->extended_middle[10] = local_40.raw[8];
  *(undefined2 *)(output->extended_middle + 8) = (*((uint16_t *)((uint8_t *)&local_40 + 28u)));
  output->extended_middle[0xb] = local_40.raw[9];
  *(undefined2 *)(output->extended_middle + 0xc) = (*((uint16_t *)((uint8_t *)&local_40 + 30u)));
  output->extended_tail[0x10] = local_40.raw[0x30];
  *(undefined2 *)(output->extended_prefix + 0x18) = (*((uint16_t *)((uint8_t *)&local_40 + 46u)));
  *(undefined2 *)(output->extended_middle + 0x12) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x5658))));
  *(undefined2 *)(output->extended_middle + 0x14) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x5656))));
  *(undefined2 *)(output->extended_middle + 0x16) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x5650))));
  *(undefined2 *)(output->extended_middle + 0x18) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x5654))));
  *(undefined2 *)(output->extended_middle + 0x1a) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x5652))));
  *(undefined2 *)(output->extended_middle + 0x1c) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x564e))));
  output->ecu_thermal_estimate = (*((short *)camry_host_ptr((uint32_t)((0xffffb77au + (uint32_t)((int)puVar3))))));
  output->motor_thermal_estimate = (*((short *)camry_host_ptr((uint32_t)((0xffffb77cu + (uint32_t)((int)puVar3))))));
  output->ecu_thermal_source = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb76cu + (uint32_t)((int)puVar3) * 1u))));
  uVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb76du + (uint32_t)((int)puVar3) * 1u))));
  output->extended_tail[0x11] = '\0';
  output->motor_thermal_active = uVar2;
  *(undefined2 *)output->extended_tail = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3a2a))));
  *(undefined4 *)(output->extended_tail + 2) = (*((undefined4 *)camry_host_ptr((uint32_t)(puVar3 + -0x3568))));
  *(undefined4 *)(output->extended_tail + 6) = (*((undefined4 *)camry_host_ptr((uint32_t)(puVar3 + -0x3564))));
  return;
}


