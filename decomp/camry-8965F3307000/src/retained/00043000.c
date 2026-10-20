#include "common.h"

void reset_b_three_channel_residual_window_monitors_430f0(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe78c4 = 0;
  DAT_febe78c6 = 0;
  DAT_febe78c8 = 0;
  DAT_febe78cc = 0;
  reset_windowed_monitor((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe7894u)));
  reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3f5c))));
  reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3f4c))));
  return;
}

void clear_b_three_channel_residual_window_monitors_4311c(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe78c4 = 0;
  DAT_febe78c6 = 0;
  DAT_febe78c8 = 0;
  DAT_febe78cc = 0;
  reset_windowed_monitor((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe7894u)));
  reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3f5c))));
  reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3f4c))));
  return;
}

void update_b_three_channel_residual_window_monitors_43148(void)

{
  uint32_t puVar1;
  byte bVar2;
  
  puVar1 = 0xfebeb800u;
  if (DAT_0002bc04 == 'Z') {
    reset_windowed_monitor((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe7894u)));
    reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3f5c))));
    reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3f4c))));
  }
  else {
    bVar2 = DAT_febe74ad |
            DAT_febe74ac |
            DAT_febe74ab |
            DAT_febe7935 |
            DAT_febe792b |
            DAT_febe792e |
            DAT_febe792d | DAT_febe792c | DAT_febe7934 | DAT_febe792a | DAT_febe7929 | DAT_febe7928;
    if (((DAT_febe71ec >> 1 & 1) == 0) && (DAT_febeeb85 == 'Z')) {
      DAT_febe78cc = (int)((int)(int16_t)DAT_febe7880);
      DAT_febe78c8 = ((int)(int16_t)DAT_febe6396);
      DAT_febe78c6 = 0x26;
      DAT_febe78c4 = bVar2;
      step_windowed_monitor
                ((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe7894u)),(F33WindowedMonitorLimits *)((undefined *)camry_host_ptr(0x2b858u)),
                 (F33TwoSidedMonitorCallbacks *)&PTR_classify_channel_residual_b_000286b0);
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3f3c))))) = bVar2;
      (*((int *)camry_host_ptr((uint32_t)(puVar1 + -0x3f34)))) = (int)(*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x3f7e))));
      (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x3f38)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x5468))));
      (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x3f3a)))) = 0x27;
      step_windowed_monitor
                (((F33WindowedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3f5c))),
                 (F33WindowedMonitorLimits *)((undefined *)camry_host_ptr(0x2b858u)),
                 (F33TwoSidedMonitorCallbacks *)&PTR_classify_channel_residual_b_000286b0);
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3f3c))))) = bVar2;
      (*((int *)camry_host_ptr((uint32_t)(puVar1 + -0x3f34)))) = (int)(*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x3f7c))));
      (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x3f38)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x5466))));
      (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x3f3a)))) = 0x28;
      step_windowed_monitor
                (((F33WindowedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3f4c))),
                 (F33WindowedMonitorLimits *)((undefined *)camry_host_ptr(0x2b858u)),
                 (F33TwoSidedMonitorCallbacks *)&PTR_classify_channel_residual_b_000286b0);
    }
    else {
      classify_counter_limits_and_clear_selected_fields_6ae48(((undefined *)camry_host_ptr(0xfebe7894u)),((undefined *)camry_host_ptr(0x2b858u)));
      classify_counter_limits_and_clear_selected_fields_6ae48(((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x3f5c))), ((undefined *)camry_host_ptr(0x2b858u)));
      classify_counter_limits_and_clear_selected_fields_6ae48(((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x3f4c))), ((undefined *)camry_host_ptr(0x2b858u)));
    }
  }
  set_channel_monitor_status_b(7,(uchar)(*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x3f6c)))));
  set_channel_monitor_status_b(8,(uchar)(*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x3f5c)))));
  set_channel_monitor_status_b(9,(uchar)(*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x3f4c)))));
  return;
}

uint classify_channel_residual_b(void)

{
  ushort uVar1;
  short sVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  
  iVar7 = (int)((int)(int16_t)DAT_febe78c8);
  iVar3 = (int)((int)(int16_t)DAT_febe629e);
  if (iVar7 + 0x7fff < 0 == (-1 < iVar7 && iVar7 + 0x7fff < 0) && iVar7 != -0x7fff) {
    if (iVar7 < 0) {
      iVar7 = (int)-((int)(int16_t)DAT_febe78c8);
    }
  }
  else {
    iVar7 = 0x7fff;
  }
  if (iVar3 + 0x7fff < 0 == (-1 < iVar3 && iVar3 + 0x7fff < 0) && iVar3 != -0x7fff) {
    if (iVar3 < 0) {
      iVar3 = (int)-((int)(int16_t)DAT_febe629e);
    }
  }
  else {
    iVar3 = 0x7fff;
  }
  if (((int)(int32_t)(int)DAT_febe78cc) + 0x7fffffff < 0 == (-1 < ((int)(int32_t)(int)DAT_febe78cc) && ((int)(int32_t)(int)DAT_febe78cc) + 0x7fffffff < 0) &&
      ((int)(int32_t)DAT_febe78cc) != -0x7fffffff) {
    iVar4 = ((int)(int32_t)DAT_febe78cc);
    if (((int)(int32_t)DAT_febe78cc) < 0) {
      iVar4 = -((int)(int32_t)DAT_febe78cc);
    }
  }
  else {
    iVar4 = 0x7fffffff;
  }
  if ((DAT_febe78c4 == '\0') && ((output_request_status & 0x40004) == 0)) {
    uVar1 = DAT_0002b890;
    sVar2 = DAT_0002b88e;
    if (DAT_febeeb88 != 'Z') {
      uVar1 = DAT_0002b88c;
      sVar2 = DAT_0002b88a;
    }
    iVar6 = (int)sVar2;
    iVar5 = (int)DAT_0002b886;
    if ((((iVar7 - iVar5 < 0 != (iVar7 < 0 != iVar5 < 0 && iVar5 < 0 == iVar7 - iVar5 < 0)) &&
         (iVar5 = (int)DAT_0002b888,
         iVar4 - iVar5 < 0 == (iVar4 < 0 != iVar5 < 0 && iVar5 < 0 == iVar4 - iVar5 < 0) &&
         iVar4 != iVar5)) &&
        (iVar3 - iVar6 < 0 != (iVar3 < 0 != iVar6 < 0 && iVar6 < 0 == iVar3 - iVar6 < 0) ||
         iVar3 == iVar6)) && (uVar1 <= DAT_febe7da8)) {
      return 0x22;
    }
    iVar5 = (int)DAT_0002b892;
    if ((((iVar7 - iVar5 < 0 != (iVar7 < 0 != iVar5 < 0 && iVar5 < 0 == iVar7 - iVar5 < 0)) &&
         (iVar7 = (int)DAT_0002b894,
         iVar4 - iVar7 < 0 != (iVar4 < 0 != iVar7 < 0 && iVar7 < 0 == iVar4 - iVar7 < 0) ||
         iVar4 == iVar7)) &&
        ((DAT_febeeb88 == '\0' &&
         ((iVar7 = (int)DAT_0002b896,
          iVar3 - iVar7 < 0 != (iVar3 < 0 != iVar7 < 0 && iVar7 < 0 == iVar3 - iVar7 < 0) ||
          iVar3 == iVar7 && (DAT_0002b898 <= DAT_febe7da8)))))) && (((int16_t)DAT_febe7b36) == -1)) {
      return 0x11;
    }
    return 0x33;
  }
  return 0x44;
}

void report_diagnostic_healthy_observed_cell_4334c(void)

{
  report_diagnostic_healthy_observed((uint)DAT_febe78c6);
  return;
}

void report_diagnostic_event_failure_10_4335c(void)

{
  report_diagnostic_event_failure((uint)DAT_febe78c6,10);
  return;
}

void clear_monitor_b_twelve_status_4336e(void)

{
  DAT_febe78d2 = 0;
  return;
}

void reset_monitor_b_twelve_status_43374(void)

{
  DAT_febe78d2 = 0;
  return;
}

void update_event_19_monitor_status_and_healthy_delay_4337a(void)

{
  uint32_t puVar1;
  char cVar3;
  uchar status;
  byte bVar4;
  uint32_t puVar2;
  cVar3 = DAT_febe78d1;
  bVar4 = DAT_febe78d0;
  puVar2 = 0xfebeb800u;
  puVar1 = (0xfebeb800u);
  if (DAT_0002bc08 != 'Z') {
    if ((DAT_febe71ec >> 1 & 1) == 0) {
      if (DAT_febe6429 == 'Z') {
        status = '\"';
        report_diagnostic_event_failure(0x19,10);
        puVar1 = ((uint32_t)(puVar2));
      }
      else {
        if (DAT_febe6428 == '\0') {
          status = '\0';
          if (((DAT_0002b89c < DAT_febe7da8) || (output_request_status >> 0x10 != 0)) ||
             (DAT_febeeb85 != 'Z')) {
            bVar4 = 0;
          }
          else if (DAT_febe78d0 < DAT_0002b89a) {
            bVar4 = DAT_febe78d0 + 1;
          }
          else if (DAT_febe78d1 != 'Z') {
            puVar1 = (0xfebeb800u);
            report_diagnostic_healthy_observed(0x19);
            cVar3 = 'Z';
          }
          goto LAB_00043418;
        }
        status = '\x11';
        puVar1 = (0xfebeb800u);
      }
      bVar4 = 0;
      goto LAB_00043418;
    }
    status = DAT_febe78d2;
    if (DAT_febe78d2 != '\x11') goto LAB_00043418;
  }
  status = '\0';
LAB_00043418:
  (*((volatile undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(-0x3f30) * 1u)))) = bVar4;
  (*((volatile undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(-0x3f2f) * 1u)))) = cVar3;
  (*((volatile undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(-0x3f2e) * 1u)))) = status;
  set_channel_monitor_status_b(0xc,status);
  return;
}

void return_only_stub_4342e(void)

{
  return;
}

void fill_constant_block_43430(void)

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

int sum_channel_snapshot_differences_b(void)

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

void step_channel_difference_latch_b(void)

{
  short sVar1;
  ushort uVar2;
  byte bVar3;
  int iVar4;
  uint32_t puVar5;
  int iVar6;
  int iVar7;
  byte bVar8;
  undefined1 uVar9;
  byte bVar10;
  byte bVar11;
  
  uVar9 = DAT_febe78d7;
  bVar3 = DAT_febe78d6;
  bVar10 = DAT_febe78d5;
  bVar11 = DAT_febe78d4;
  puVar5 = 0xfebeb800u;
  if (((byte)DAT_febe71ec & 2) == 0) {
    iVar6 = sum_channel_snapshot_differences_b();
    uVar2 = DAT_00031e6a;
    sVar1 = DAT_00031e68;
    if (iVar6 + 0x7fffffff < 0 == (-1 < iVar6 && iVar6 + 0x7fffffff < 0) && iVar6 != -0x7fffffff) {
      iVar4 = iVar6;
      if (iVar6 < 0) {
        iVar4 = -iVar6;
      }
    }
    else {
      iVar4 = 0x7fffffff;
    }
    iVar7 = (int)DAT_00031e68;
    (*((int *)camry_host_ptr((uint32_t)(puVar5 + -0x3f20)))) = iVar6;
    (*((short *)camry_host_ptr((uint32_t)(puVar5 + -0x3f22)))) = sVar1;
    bVar8 = bVar3;
    if ((iVar4 - iVar7 < 0 == (iVar4 < 0 != iVar7 < 0 && iVar7 < 0 == iVar4 - iVar7 < 0) &&
         iVar4 != iVar7) && ((*((ushort *)camry_host_ptr((uint32_t)(puVar5 + -0x3a58)))) <= uVar2)) {
      bVar10 = 0;
      if (bVar11 < DAT_00031e64) {
        uVar9 = 0;
        bVar11 = bVar11 + 1;
        bVar8 = bVar11;
        if (bVar11 <= bVar3) {
          bVar8 = bVar3;
        }
      }
      else {
        uVar9 = 0x5a;
      }
    }
    else if (bVar10 < DAT_00031e65) {
      bVar10 = bVar10 + 1;
    }
    else {
      bVar11 = 0;
      uVar9 = 0xa5;
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3f2c))))) = bVar11;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3f2b))))) = bVar10;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3f2a))))) = bVar8;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3f29))))) = uVar9;
  }
  return;
}

void reset_b_three_window_and_recoverable_monitors_43554(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe78e4 = 0;
  DAT_febe78e6 = 0;
  DAT_febe78e8 = 0;
  reset_windowed_monitor((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe78ecu)));
  reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3f04))));
  reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3ef4))));
  reset_recoverable_monitor(((F33RecoverableMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3ee4))));
  return;
}

void clear_b_three_window_and_recoverable_monitors_43586(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe78e4 = 0;
  DAT_febe78e6 = 0;
  DAT_febe78e8 = 0;
  reset_windowed_monitor((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe78ecu)));
  reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3f04))));
  reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3ef4))));
  reset_recoverable_monitor(((F33RecoverableMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3ee4))));
  return;
}

void step_channel_phase_monitors_b(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bc0c == 'Z') {
    puVar1 = 0xfebeb800u;
    reset_windowed_monitor((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe78ecu)));
    reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3f04))));
    reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3ef4))));
  }
  else {
    if (((DAT_febe71ec >> 1 & 1) == 0) && (DAT_febeeb85 == 'Z')) {
      DAT_febe78e4 = 0x1b;
      DAT_febe78e6 = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebe7e78u + (uint32_t)(3) * 2u))));
      DAT_febe78e8 = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebe7e84u + (uint32_t)(3) * 2u))));
      step_windowed_monitor
                ((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe78ecu)),(F33WindowedMonitorLimits *)((undefined *)camry_host_ptr(0x2b860u)),
                 (F33TwoSidedMonitorCallbacks *)&PTR_classify_channel_phase_sample_b_000286e4);
      (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x3f1c)))) = 0x1c;
      (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x3f1a)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x3980))));
      (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x3f18)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x3974))));
      step_windowed_monitor
                (((F33WindowedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3f04))),
                 (F33WindowedMonitorLimits *)((undefined *)camry_host_ptr(0x2b860u)),
                 (F33TwoSidedMonitorCallbacks *)&PTR_classify_channel_phase_sample_b_000286e4);
      (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x3f1c)))) = 0x1d;
      (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x3f1a)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x397e))));
      (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x3f18)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x3972))));
      step_windowed_monitor
                (((F33WindowedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3ef4))),
                 (F33WindowedMonitorLimits *)((undefined *)camry_host_ptr(0x2b860u)),
                 (F33TwoSidedMonitorCallbacks *)&PTR_classify_channel_phase_sample_b_000286e4);
      step_recoverable_monitor
                (((F33RecoverableMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3ee4))),
                 (F33RecoverableMonitorLimits *)((undefined *)camry_host_ptr(0x2b868u)),
                 (F33RecoverableMonitorCallbacks *)
                 &PTR_classify_channel_phase_failure_count_b_00028718);
      goto LAB_000436a4;
    }
    puVar1 = 0xfebeb800u;
    classify_counter_limits_and_clear_selected_fields_6ae48(((undefined *)camry_host_ptr(0xfebe78ecu)),((undefined *)camry_host_ptr(0x2b860u)));
    classify_counter_limits_and_clear_selected_fields_6ae48(((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x3f04))), ((undefined *)camry_host_ptr(0x2b860u)));
    classify_counter_limits_and_clear_selected_fields_6ae48(((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x3ef4))), ((undefined *)camry_host_ptr(0x2b860u)));
  }
  reset_recoverable_monitor(((F33RecoverableMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3ee4))));
LAB_000436a4:
  set_channel_monitor_status_b(0,(uchar)(*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x3f14)))));
  set_channel_monitor_status_b(1,(uchar)(*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x3f04)))));
  set_channel_monitor_status_b(2,(uchar)(*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x3ef4)))));
  set_channel_monitor_status_b(10,(uchar)(*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x3ee4)))));
  return;
}

uint classify_channel_phase_sample_b(void)

{
  ushort uVar1;
  ushort uVar2;
  char cVar3;
  ushort uVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  short sStack_22;
  
  uVar4 = DAT_febe7da8;
  cVar3 = DAT_febe62e5;
  uVar2 = DAT_0002b8aa;
  uVar1 = DAT_0002b8a4;
  iVar8 = (int)((int)(int16_t)DAT_febe78e8);
  iVar7 = (int)((int)(int16_t)DAT_febe62dc);
  store_saturating_absolute_s16_6a522((int)((int)(int16_t)DAT_febe78e6),&sStack_22);
  iVar5 = (int)sStack_22;
  iVar6 = (int)(int16_t)DAT_0002b8a0;
  if (cVar3 == '\0') {
    if ((((iVar5 - iVar6 < 0 == (iVar5 < 0 != iVar6 < 0 && iVar6 < 0 == iVar5 - iVar6 < 0) &&
           iVar5 != iVar6) ||
         (iVar6 = (int)(int16_t)DAT_0002b8a2,
         iVar8 - iVar6 < 0 != (iVar8 < 0 != iVar6 < 0 && iVar6 < 0 == iVar8 - iVar6 < 0))) &&
        (uVar4 <= uVar1)) &&
       (iVar6 = (int)(int16_t)DAT_0002b8ac,
       iVar7 - iVar6 < 0 == (iVar7 < 0 != iVar6 < 0 && iVar6 < 0 == iVar7 - iVar6 < 0) &&
       iVar7 != iVar6)) {
      return 0x22;
    }
    iVar6 = (int)(int16_t)DAT_0002b8a6;
    if (iVar5 - iVar6 < 0 == (iVar5 < 0 != iVar6 < 0 && iVar6 < 0 == iVar5 - iVar6 < 0) &&
        iVar5 != iVar6) {
      return 0x33;
    }
    iVar5 = (int)(int16_t)DAT_0002b8a8;
    if (iVar8 - iVar5 < 0 != (iVar8 < 0 != iVar5 < 0 && iVar5 < 0 == iVar8 - iVar5 < 0)) {
      return 0x33;
    }
  }
  else {
    if (((iVar5 - iVar6 < 0 == (iVar5 < 0 != iVar6 < 0 && iVar6 < 0 == iVar5 - iVar6 < 0) &&
          iVar5 != iVar6) && (uVar4 <= uVar1)) &&
       (iVar6 = (int)(int16_t)DAT_0002b8ac,
       iVar7 - iVar6 < 0 == (iVar7 < 0 != iVar6 < 0 && iVar6 < 0 == iVar7 - iVar6 < 0) &&
       iVar7 != iVar6)) {
      return 0x22;
    }
    iVar6 = (int)(int16_t)DAT_0002b8a6;
    if (iVar5 - iVar6 < 0 == (iVar5 < 0 != iVar6 < 0 && iVar6 < 0 == iVar5 - iVar6 < 0) &&
        iVar5 != iVar6) {
      return 0x33;
    }
  }
  if (uVar2 < uVar4) {
    return 0x33;
  }
  return 0x11;
}

void report_diagnostic_healthy_observed_cell_43762(void)

{
  report_diagnostic_healthy_observed((uint)DAT_febe78e4);
  return;
}

void report_diagnostic_event_failure_10_43772(void)

{
  report_diagnostic_event_failure((uint)DAT_febe78e4,10);
  return;
}

uint classify_channel_phase_failure_count_b(void)

{
  ushort uVar1;
  
  uVar1 = (ushort)DAT_0002b89e;
  if (((DAT_febe78f4 < uVar1) && (DAT_febe7904 < uVar1)) && (DAT_febe7914 < uVar1)) {
    return 0x11;
  }
  return 0x22;
}

void return_only_stub_437b0(void)

{
  return;
}

void return_only_stub_437b2(void)

{
  return;
}

void publish_channel_monitor_actions_b(void)

{
  byte bVar1;
  byte bVar2;
  ushort uVar3;
  uint32_t puVar4;
  uchar uVar5;
  undefined1 uVar6;
  
  uVar3 = DAT_febe71ec;
  puVar4 = 0xfebeb800u;
  retain_and_clear_fault_record(3);
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ecb))))) |
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ecc))))) |
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed2))))) |
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed3))))) |
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed4))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed5))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed6))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed7))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed8)))))) &
      0x11) == 0x11) {
    encode_fault_action_kind('\x03','\n');
  }
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ecc))))) |
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed6))))) |
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed7))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed8))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed2))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed3))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed4)))))) &
      0x22) == 0x22) {
    encode_fault_action_kind('\x03','$');
  }
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ecb))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed5))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ecf))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed0))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed1)))))) &
      0x22) == 0x22) {
    encode_fault_action_kind('\x03','\x1c');
  }
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ecd))))) & 0x22) == 0x22) {
    encode_fault_action_kind('\x03','\x1e');
  }
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ece))))) & 0x22) == 0x22) {
    encode_fault_action_kind('\x03','(');
  }
  if (((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ecb))))) |
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ecc))))) |
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed2))))) |
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed3))))) |
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed4))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed5))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed6))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed7))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed8)))))) &
       0x22) == 0x22) && ((uVar3 >> 1 & 1) == 0)) {
    encode_fault_action_kind('\x03','\n');
  }
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ecc))))) |
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed2))))) |
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed3))))) |
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed4))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed5))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed6))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed7))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed8)))))) &
      0x22) == 0x22) {
    encode_fault_action_kind('\x03','2');
  }
  select_current_fault_record(3);
  bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed6))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed7))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed8)))));
  uVar6 = 0;
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed1))))) | bVar1 | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed0))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ecf)))))) & 0x11) == 0x11) {
    uVar6 = 0x5a;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3eca))))) = uVar6;
  uVar6 = 0x11;
  if ((((((bVar1 == 0 && (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed5))))) == '\0') && (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed4))))) == '\0') &&
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed3))))) == '\0') && (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed2))))) == '\0') && (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ecc))))) == '\0') &&
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ecb))))) == '\0') {
    uVar6 = 0;
  }
  uVar5 = '\0';
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ec9))))) = uVar6;
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ecb))))) != '\0' ||
      ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ecd))))) != '\0' ||
      ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ecf))))) != 0 ||
      ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed0))))) != 0 ||
      ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed1))))) != 0 ||
      ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed5))))) != '\0' ||
      ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed6))))) != 0 ||
      ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed7))))) != 0 ||
      ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed8))))) != 0 ||
      ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed2))))) != '\0' ||
      ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed3))))) != '\0' || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed4))))) != '\0' || (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ecc))))) != '\0')))))))))))) {
    uVar5 = '\x11';
  }
  set_diagnostic_cache_blocker('\x04',uVar5);
  bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed6))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed7))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed8)))));
  bVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ecb))))) |
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ecd))))) |
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ecf))))) |
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ecc))))) | bVar1 | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed4))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed3))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed2))))) |
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed5))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed1))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed0)))));
  if ((bVar2 == 0) || (bVar2 == 0x11)) {
    uVar6 = 0;
  }
  else {
    uVar6 = 0x5a;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ec8))))) = uVar6;
  uVar5 = '\0';
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ecd))))) |
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ecf))))) |
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed0))))) |
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed1))))) |
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ecb))))) |
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ecc))))) |
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed2))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed3))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed4))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3ed5))))) | bVar1) & 0x11) ==
      0x11) {
    uVar5 = 'Z';
  }
  set_monitor_pending_projection('\x03',uVar5);
  return;
}

void set_channel_monitor_status_b(uint index,uchar status)

{
  if ((index & 0xff) < 0xe) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7928u + (uint32_t)(index & 0xff) * 1u)))) = status;
  }
  return;
}

void reset_latched_monitor_febe793c(void)

{
  reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe793cu)));
  return;
}

void reset_latched_monitor_febe793c_43a1c(void)

{
  reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe793cu)));
  return;
}

void update_gated_latched_monitor_b_eleven_43a2c(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bc10 == 'Z') {
    reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe793cu)));
  }
  else if (((DAT_febe6764 >> 1 & 1) == 0) && (DAT_febee820 == 'Z')) {
    step_latched_monitor
              ((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe793cu)),(F33MonitorLimits *)((undefined *)camry_host_ptr(0x2b86eu)),
               (F33TwoSidedMonitorCallbacks *)&PTR_FUN_00028754);
  }
  else {
    retain_disabled_latched_monitor
              ((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe793cu)),(F33MonitorLimits *)((undefined *)camry_host_ptr(0x2b86eu)));
  }
  set_channel_monitor_status_b(0xb,(uchar)(*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x3ec4)))));
  return;
}

undefined4 test_b_sample_absolute_or_delta_limit_43a86(void)

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

undefined4 classify_b_sample_flag_combination_43ab6(void)

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
  iVar6 = test_b_sample_absolute_or_delta_limit_43a86();
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

void report_diagnostic_healthy_observed_87_43b12(void)

{
  report_diagnostic_healthy_observed(0x87);
  return;
}

void report_diagnostic_event_failure_87_32_43b22(void)

{
  report_diagnostic_event_failure(0x87,0x32);
  return;
}

void reset_latched_monitor_febe7948(void)

{
  reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7948u)));
  return;
}

void reset_latched_monitor_febe7948_43b46(void)

{
  reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7948u)));
  return;
}

void update_raw_lower_bound_latched_monitor_b_43b56(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bc14 == 'Z') {
    reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7948u)));
  }
  else if (((DAT_febe71ec >> 1 & 1) == 0) && (DAT_febeeb85 == 'Z')) {
    step_latched_monitor
              ((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7948u)),(F33MonitorLimits *)((undefined *)camry_host_ptr(0x2b872u)),
               (F33TwoSidedMonitorCallbacks *)&PTR_classify_channel_raw_lower_bound_b_00028788);
  }
  else {
    retain_disabled_latched_monitor
              ((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7948u)),(F33MonitorLimits *)((undefined *)camry_host_ptr(0x2b872u)));
  }
  set_channel_monitor_status_b(0xd,(uchar)(*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x3eb8)))));
  return;
}

uint classify_channel_raw_lower_bound_b(void)

{
  if (output_request_status >> 0x10 != 0) {
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

void report_diagnostic_healthy_observed_139_43c2c(void)

{
  report_diagnostic_healthy_observed(0x139);
  return;
}

void report_diagnostic_event_failure_139_10_43c3c(void)

{
  report_diagnostic_event_failure(0x139,10);
  return;
}

void reset_windowed_monitor_febe7954(void)

{
  reset_windowed_monitor((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe7954u)));
  return;
}

void reset_windowed_monitor_febe7954_43c5e(void)

{
  reset_windowed_monitor((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe7954u)));
  return;
}

void update_sample_sum_window_monitor_b_43c6e(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bc18 == 'Z') {
    reset_windowed_monitor((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe7954u)));
  }
  else if (((DAT_febe71ec >> 1 & 1) == 0) && (DAT_febeeb85 == 'Z')) {
    step_windowed_monitor
              ((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe7954u)),(F33WindowedMonitorLimits *)((undefined *)camry_host_ptr(0x2b876u)),
               (F33TwoSidedMonitorCallbacks *)&PTR_classify_channel_sample_sum_b_000287bc);
  }
  else {
    classify_counter_limits_and_clear_selected_fields_6ae48(((undefined *)camry_host_ptr(0xfebe7954u)), ((ushort *)camry_host_ptr((uint32_t)(0x2b876))));
  }
  set_channel_monitor_status_b(3,(uchar)(*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x3eac)))));
  return;
}

uint classify_channel_sample_sum_b(void)

{
  char cVar1;
  short sVar2;
  char cVar3;
  int iVar4;
  int iVar5;
  uint uVar6;
  int iVar7;
  int iVar8;
  int local_24;
  
  cVar3 = DAT_febeeb88;
  uVar6 = output_request_status;
  sVar2 = DAT_febe7b32;
  cVar1 = DAT_febe6369;
  iVar8 = (int)(*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebe7e78u + (uint32_t)(4) * 2u))));
  iVar4 = (int)(*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebe7e78u + (uint32_t)(3) * 2u))));
  iVar7 = (int)(*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebe7e78u + (uint32_t)(5) * 2u))));
  iVar5 = iVar7 + iVar8 + iVar4;
  if (iVar4 + 0x7fff < 0 == (-1 < iVar4 && iVar4 + 0x7fff < 0) && iVar4 != -0x7fff) {
    if (iVar4 < 0) {
      iVar4 = (int)-(*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebe7e78u + (uint32_t)(3) * 2u))));
    }
  }
  else {
    iVar4 = 0x7fff;
  }
  if (iVar8 + 0x7fff < 0 == (-1 < iVar8 && iVar8 + 0x7fff < 0) && iVar8 != -0x7fff) {
    if (iVar8 < 0) {
      iVar8 = (int)-(*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebe7e78u + (uint32_t)(4) * 2u))));
    }
  }
  else {
    iVar8 = 0x7fff;
  }
  if (iVar7 + 0x7fff < 0 == (-1 < iVar7 && iVar7 + 0x7fff < 0) && iVar7 != -0x7fff) {
    if (iVar7 < 0) {
      iVar7 = (int)-(*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebe7e78u + (uint32_t)(5) * 2u))));
    }
  }
  else {
    iVar7 = 0x7fff;
  }
  store_saturating_absolute_s32_6a53e(iVar5,&local_24);
  if (((uVar6 & 0x40004) == 0) &&
     ((cVar3 == 'Z' ||
      (((iVar5 = (int)DAT_0002b8b8,
        iVar4 - iVar5 < 0 != (iVar4 < 0 != iVar5 < 0 && iVar5 < 0 == iVar4 - iVar5 < 0) &&
        (iVar8 - iVar5 < 0 != (iVar8 < 0 != iVar5 < 0 && iVar5 < 0 == iVar8 - iVar5 < 0))) &&
       (iVar7 - iVar5 < 0 != (iVar7 < 0 != iVar5 < 0 && iVar5 < 0 == iVar7 - iVar5 < 0))))))) {
    if (((int)local_24 - (int)PTR_LAB_000010ca_4_0002b8bc < 0 ==
         ((int)local_24 < 0 != (int)PTR_LAB_000010ca_4_0002b8bc < 0 &&
         (int)PTR_LAB_000010ca_4_0002b8bc < 0 ==
         (int)local_24 - (int)PTR_LAB_000010ca_4_0002b8bc < 0) &&
         local_24 != PTR_LAB_000010ca_4_0002b8bc) && (cVar1 == 'Z')) {
      uVar6 = 0x22;
    }
    else if (((int)local_24 - (int)PTR_LAB_000010ca_4_0002b8c0 < 0 ==
              ((int)local_24 < 0 != (int)PTR_LAB_000010ca_4_0002b8c0 < 0 &&
              (int)PTR_LAB_000010ca_4_0002b8c0 < 0 ==
              (int)local_24 - (int)PTR_LAB_000010ca_4_0002b8c0 < 0) &&
              local_24 != PTR_LAB_000010ca_4_0002b8c0) || ((cVar1 != 'Z' || (sVar2 != -1)))) {
      uVar6 = 0x33;
    }
    else {
      uVar6 = 0x11;
    }
  }
  else {
    uVar6 = 0x44;
  }
  return uVar6;
}

void report_diagnostic_healthy_observed_24_43da2(void)

{
  report_diagnostic_healthy_observed(0x24);
  return;
}

void report_diagnostic_event_failure_24_10_43db2(void)

{
  report_diagnostic_event_failure(0x24,10);
  return;
}

void return_only_stub_43dc4(void)

{
  return;
}

void fill_constant_block_43dc6(void)

{
  DAT_febe7964 = 0;
  DAT_febe7965 = 0;
  DAT_febe7966 = 0;
  DAT_febe7967 = 0;
  DAT_febe7968 = 0;
  DAT_febe796c = 0;
  return;
}

undefined1 update_dual_threshold_hysteresis_latch_43dd8(ushort param_1,undefined1 param_2)

{
  if (((DAT_0002fbce < DAT_febe7db0) && (DAT_0002fbca < param_1)) && (DAT_febe7bb9 != 'Z')) {
    return 0x5a;
  }
  if ((DAT_febe7db0 <= (ushort)PTR_DAT_0002fbd0) && (param_1 <= DAT_0002fbcc)) {
    param_2 = 0;
  }
  return param_2;
}

void apply_a_latch_command_mask_43e14(char param_1)

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
  set_request_word_8aa8_bounded6_56cda(4,uVar2);
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x3e98)))) = uVar2;
  return;
}

void update_a_dual_threshold_latch_and_mask_43e54(void)

{
  uint32_t puVar1;
  uint uVar2;
  
  puVar1 = 0xfebeb800u;
  uVar2 = (uint)DAT_febe7964;
  if (((byte)DAT_febe71ec & 1) == 0) {
    puVar1 = 0xfebeb800u;
    uVar2 = update_dual_threshold_hysteresis_latch_43dd8(DAT_febe7da6,uVar2);
  }
  apply_a_latch_command_mask_43e14(uVar2);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3e9c))))) = (char)uVar2;
  return;
}

void apply_b_latch_command_mask_43e7c(char param_1)

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
  set_request_word_8aa8_bounded6_56cda(5,uVar2);
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x3e94)))) = uVar2;
  return;
}

void update_b_dual_threshold_latch_and_mask_43ec0(void)

{
  uint32_t puVar1;
  uint uVar2;
  
  puVar1 = 0xfebeb800u;
  uVar2 = (uint)DAT_febe7965;
  if (((byte)DAT_febe71ec & 2) == 0) {
    puVar1 = 0xfebeb800u;
    uVar2 = update_dual_threshold_hysteresis_latch_43dd8(DAT_febe7da8,uVar2);
  }
  apply_b_latch_command_mask_43e7c(uVar2);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3e9b))))) = (char)uVar2;
  return;
}

void publish_enabled_dual_threshold_latches_43ee8(void)

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

void update_dual_threshold_latches_when_enabled_43f1a(void)

{
  if (DAT_febeeb85 == 'Z') {
    update_a_dual_threshold_latch_and_mask_43e54();
    update_b_dual_threshold_latch_and_mask_43ec0();
    publish_enabled_dual_threshold_latches_43ee8();
  }
  return;
}

void reset_latched_monitor_febe7970(void)

{
  reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7970u)));
  return;
}

void reset_latched_monitor_febe7970_43f48(void)

{
  reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7970u)));
  return;
}

void update_inverse_gate_shared_monitor_seven_43f58(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bc1c == 'Z') {
    reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7970u)));
  }
  else if (((DAT_febe71ec >> 1 & 1) == 0) || (DAT_febeeb85 != 'Z')) {
    report_diagnostic_healthy_observed(0xe2);
  }
  else {
    step_latched_monitor
              ((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7970u)),(F33MonitorLimits *)((undefined *)camry_host_ptr(0x2b8c4u)),
               (F33TwoSidedMonitorCallbacks *)&PTR_classify_inverse_gate_a_000287f0);
  }
  publish_shared_condition_monitor_status(7,(*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x3e90)))));
  return;
}

uint classify_inverse_gate_a(void)

{
  if ((DAT_0002b8ea < DAT_febe7da6) && (DAT_febe7db0 <= DAT_0002b8e8)) {
    return 0x22;
  }
  return 0x11;
}

void report_diagnostic_event_failure_e2_10_43fd8(void)

{
  report_diagnostic_event_failure(0xe2,10);
  return;
}

void reset_latched_monitor_febe797c(void)

{
  reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe797cu)));
  return;
}

void reset_latched_monitor_febe797c_43ffa(void)

{
  reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe797cu)));
  return;
}
