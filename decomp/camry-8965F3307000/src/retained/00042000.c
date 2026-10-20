#include "common.h"

void filter_clipped_three_channel_q16_state_42030(void)

{
  uint uVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  
  if ((int)DAT_febe62f8 + 0x7fff < 0 == (-1 < (int)DAT_febe62f8 && (int)DAT_febe62f8 + 0x7fff < 0) &&
      ((int)(int32_t)DAT_febe62f8) != -0x7fff) {
    iVar2 = (int)(short)((int)(int32_t)DAT_febe62f8);
    if ((int)DAT_febe62f8 + -0x7fff < 0 == ((int)DAT_febe62f8 < 0 && -1 < (int)DAT_febe62f8 + -0x7fff) &&
        ((int)(int32_t)DAT_febe62f8) != 0x7fff) {
      iVar2 = 0x7fff;
    }
  }
  else {
    iVar2 = -0x7fff;
  }
  if ((int)DAT_febe62fc + 0x7fff < 0 == (-1 < (int)DAT_febe62fc && (int)DAT_febe62fc + 0x7fff < 0) &&
      ((int)(int32_t)DAT_febe62fc) != -0x7fff) {
    iVar3 = (int)(short)((int)(int32_t)DAT_febe62fc);
    if ((int)DAT_febe62fc + -0x7fff < 0 == ((int)DAT_febe62fc < 0 && -1 < (int)DAT_febe62fc + -0x7fff) &&
        ((int)(int32_t)DAT_febe62fc) != 0x7fff) {
      iVar3 = 0x7fff;
    }
  }
  else {
    iVar3 = -0x7fff;
  }
  if ((int)DAT_febe6300 + 0x7fff < 0 == (-1 < (int)DAT_febe6300 && (int)DAT_febe6300 + 0x7fff < 0) &&
      ((int)(int32_t)DAT_febe6300) != -0x7fff) {
    iVar4 = (int)(short)((int)(int32_t)DAT_febe6300);
    if ((int)DAT_febe6300 + -0x7fff < 0 == ((int)DAT_febe6300 < 0 && -1 < (int)DAT_febe6300 + -0x7fff) &&
        ((int)(int32_t)DAT_febe6300) != 0x7fff) {
      iVar4 = 0x7fff;
    }
  }
  else {
    iVar4 = -0x7fff;
  }
  uVar1 = (uint)DAT_0002b812;
  if (uVar1 - 1 < 0xffff) {
    iVar5 = (int)((int)(int16_t)DAT_febe7770) * uVar1;
    iVar2 = iVar2 * uVar1;
  }
  else {
    iVar5 = (int)((int)(int16_t)DAT_febe7770) << 0x10;
    iVar2 = iVar2 << 0x10;
  }
  DAT_febe7778 = iVar2 + (DAT_febe7778 - iVar5);
  if (uVar1 - 1 < 0xffff) {
    iVar2 = (int)((int)(int16_t)DAT_febe7772) * uVar1;
    iVar3 = iVar3 * uVar1;
  }
  else {
    iVar2 = (int)((int)(int16_t)DAT_febe7772) << 0x10;
    iVar3 = iVar3 << 0x10;
  }
  DAT_febe777c = iVar3 + (DAT_febe777c - iVar2);
  if (uVar1 - 1 < 0xffff) {
    iVar2 = (int)((int)(int16_t)DAT_febe7774) * uVar1;
    iVar4 = iVar4 * uVar1;
  }
  else {
    iVar2 = (int)((int)(int16_t)DAT_febe7774) << 0x10;
    iVar4 = iVar4 << 0x10;
  }
  DAT_febe7770 = (short)((int)DAT_febe7778 / 0x10000);
  DAT_febe7780 = iVar4 + (DAT_febe7780 - iVar2);
  DAT_febe7772 = (short)((int)DAT_febe777c / 0x10000);
  DAT_febe7774 = (short)((int)DAT_febe7780 / 0x10000);
  return;
}

void reset_three_channel_residual_window_monitors_42132(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe77b4 = 0;
  DAT_febe77b6 = 0;
  DAT_febe77b8 = 0;
  DAT_febe77bc = 0;
  reset_windowed_monitor((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe7784u)));
  reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)((0xffffbf94u + (uint32_t)((int)puVar1))))));
  reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)((0xffffbfa4u + (uint32_t)((int)puVar1))))));
  return;
}

void clear_three_channel_residual_window_monitors_4215e(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe77b4 = 0;
  DAT_febe77b6 = 0;
  DAT_febe77b8 = 0;
  DAT_febe77bc = 0;
  reset_windowed_monitor((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe7784u)));
  reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)((0xffffbf94u + (uint32_t)((int)puVar1))))));
  reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)((0xffffbfa4u + (uint32_t)((int)puVar1))))));
  return;
}

void update_three_channel_residual_window_monitors_4218a(void)

{
  uint32_t puVar1;
  byte bVar2;
  
  puVar1 = 0xfebeb800u;
  if (DAT_0002bbe8 == 'Z') {
    reset_windowed_monitor((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe7784u)));
    reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)((0xffffbf94u + (uint32_t)((int)puVar1))))));
    reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)((0xffffbfa4u + (uint32_t)((int)puVar1))))));
  }
  else {
    bVar2 = DAT_febe74ad |
            DAT_febe74ac |
            DAT_febe74aa |
            DAT_febe7825 |
            DAT_febe781b |
            DAT_febe781e |
            DAT_febe781d | DAT_febe781c | DAT_febe7824 | DAT_febe781a | DAT_febe7819 | DAT_febe7818;
    if (((DAT_febe71ec & 1) == 0) && (DAT_febeeb85 == 'Z')) {
      DAT_febe77bc = (int)((int)(int16_t)DAT_febe7770);
      DAT_febe77b8 = ((int)(int16_t)DAT_febe6390);
      DAT_febe77b6 = 0x43;
      DAT_febe77b4 = bVar2;
      step_windowed_monitor
                ((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe7784u)),(F33WindowedMonitorLimits *)((undefined *)camry_host_ptr(0x2b7e8u)),
                 (F33TwoSidedMonitorCallbacks *)&PTR_classify_channel_residual_a_0002853c);
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbfb4u + (uint32_t)((int)puVar1) * 1u)))) = bVar2;
      (*((int *)camry_host_ptr((uint32_t)((0xffffbfbcu + (uint32_t)((int)puVar1)))))) = (int)(*((short *)camry_host_ptr((uint32_t)((0xffffbf72u + (uint32_t)((int)puVar1))))));
      (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffbfb8u + (uint32_t)((int)puVar1)))))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x546e))));
      (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffbfb6u + (uint32_t)((int)puVar1)))))) = 0x44;
      step_windowed_monitor
                (((F33WindowedMonitorState *)camry_host_ptr((uint32_t)((0xffffbf94u + (uint32_t)((int)puVar1))))),
                 (F33WindowedMonitorLimits *)((undefined *)camry_host_ptr(0x2b7e8u)),
                 (F33TwoSidedMonitorCallbacks *)&PTR_classify_channel_residual_a_0002853c);
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbfb4u + (uint32_t)((int)puVar1) * 1u)))) = bVar2;
      (*((int *)camry_host_ptr((uint32_t)((0xffffbfbcu + (uint32_t)((int)puVar1)))))) = (int)(*((short *)camry_host_ptr((uint32_t)((0xffffbf74u + (uint32_t)((int)puVar1))))));
      (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffbfb8u + (uint32_t)((int)puVar1)))))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x546c))));
      (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffbfb6u + (uint32_t)((int)puVar1)))))) = 0x45;
      step_windowed_monitor
                (((F33WindowedMonitorState *)camry_host_ptr((uint32_t)((0xffffbfa4u + (uint32_t)((int)puVar1))))),
                 (F33WindowedMonitorLimits *)((undefined *)camry_host_ptr(0x2b7e8u)),
                 (F33TwoSidedMonitorCallbacks *)&PTR_classify_channel_residual_a_0002853c);
    }
    else {
      classify_counter_limits_and_clear_selected_fields_6ae48(((undefined *)camry_host_ptr(0xfebe7784u)),((undefined *)camry_host_ptr(0x2b7e8u)));
      classify_counter_limits_and_clear_selected_fields_6ae48(((undefined *)camry_host_ptr((uint32_t)((0xffffbf94u + (uint32_t)((int)puVar1))))), ((undefined *)camry_host_ptr(0x2b7e8u)));
      classify_counter_limits_and_clear_selected_fields_6ae48(((undefined *)camry_host_ptr((uint32_t)((0xffffbfa4u + (uint32_t)((int)puVar1))))), ((undefined *)camry_host_ptr(0x2b7e8u)));
    }
  }
  set_channel_monitor_status_a(7,(uchar)(*((undefined4 *)camry_host_ptr((uint32_t)((0xffffbf84u + (uint32_t)((int)puVar1)))))));
  set_channel_monitor_status_a(8,(uchar)(*((undefined4 *)camry_host_ptr((uint32_t)((0xffffbf94u + (uint32_t)((int)puVar1)))))));
  set_channel_monitor_status_a(9,(uchar)(*((undefined4 *)camry_host_ptr((uint32_t)((0xffffbfa4u + (uint32_t)((int)puVar1)))))));
  return;
}

void report_diagnostic_healthy_observed_cell_4238e(void)

{
  report_diagnostic_healthy_observed((uint)DAT_febe77b6);
  return;
}

void report_diagnostic_event_failure_10_4239e(void)

{
  report_diagnostic_event_failure((uint)DAT_febe77b6,10);
  return;
}

void clear_monitor_a_twelve_status_423b0(void)

{
  DAT_febe77c2 = 0;
  return;
}

void reset_monitor_a_twelve_status_423b6(void)

{
  DAT_febe77c2 = 0;
  return;
}

void update_event_36_monitor_status_and_healthy_delay_423bc(void)

{
  undefined *puVar1;
  char cVar3;
  uchar status;
  byte bVar4;
  uint32_t puVar2;
  cVar3 = DAT_febe77c1;
  bVar4 = DAT_febe77c0;
  puVar2 = 0xfebeb800u;
  puVar1 = ((undefined *)camry_host_ptr(0xfebeb800u));
  if (DAT_0002bbec != 'Z') {
    if ((DAT_febe71ec & 1) == 0) {
      if (DAT_febe6425 == 'Z') {
        status = '\"';
        report_diagnostic_event_failure(0x36,10);
        puVar1 = ((undefined *)camry_host_ptr((uint32_t)(puVar2)));
      }
      else {
        if (DAT_febe6424 == '\0') {
          status = '\0';
          if (((DAT_0002b82c < DAT_febe7da6) || ((short)output_request_status != 0)) ||
             (DAT_febeeb85 != 'Z')) {
            bVar4 = 0;
          }
          else if (DAT_febe77c0 < DAT_0002b82a) {
            bVar4 = DAT_febe77c0 + 1;
          }
          else if (DAT_febe77c1 != 'Z') {
            puVar1 = ((undefined *)camry_host_ptr(0xfebeb800u));
            report_diagnostic_healthy_observed(0x36);
            cVar3 = 'Z';
          }
          goto LAB_00042456;
        }
        status = '\x11';
        puVar1 = ((undefined *)camry_host_ptr(0xfebeb800u));
      }
      bVar4 = 0;
      goto LAB_00042456;
    }
    status = DAT_febe77c2;
    if (DAT_febe77c2 != '\x11') goto LAB_00042456;
  }
  status = '\0';
LAB_00042456:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbfc0u + (uint32_t)((int)camry_host_addr(puVar1)) * 1u)))) = bVar4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbfc1u + (uint32_t)((int)camry_host_addr(puVar1)) * 1u)))) = cVar3;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbfc2u + (uint32_t)((int)camry_host_addr(puVar1)) * 1u)))) = status;
  set_channel_monitor_status_a(0xc,status);
  return;
}

void return_only_stub_4246c(void)

{
  return;
}

void fill_constant_block_4246e(void)

{
  DAT_febe77c4 = 0;
  DAT_febe77c5 = 0;
  DAT_febe77c6 = 0;
  DAT_febe77c7 = 0;
  DAT_febe77c8 = 0x8000;
  DAT_febe77ca = 0x8000;
  DAT_febe77cc = 0x8000;
  return;
}

int sum_channel_snapshot_differences_a(void)

{
  ushort uVar1;
  char cVar4;
  char cVar5;
  ushort uVar2;
  ushort uVar3;
  
  uVar1 = DAT_febe8238;
  uVar2 = DAT_febe823c;
  uVar3 = DAT_febe823a;
  if (DAT_00031e5e != 'Z') goto LAB_000424f0;
  if (DAT_febeeac1 == 'Z') {
    cVar4 = DAT_febe7e21;
    cVar5 = DAT_febe7e22;
    if (DAT_febe7e20 == 'Z') goto LAB_000424b6;
  }
  else {
    cVar4 = 'Z';
    cVar5 = 'Z';
LAB_000424b6:
    DAT_febe77c8 = DAT_febe8238;
  }
  if (cVar4 == 'Z') {
    DAT_febe77ca = DAT_febe823a;
  }
  uVar1 = DAT_febe77c8;
  uVar2 = DAT_febe77cc;
  uVar3 = DAT_febe77ca;
  if (cVar5 == 'Z') {
    DAT_febe77cc = DAT_febe823c;
    uVar2 = DAT_febe823c;
  }
LAB_000424f0:
  return ((uint)uVar2 - (uint)DAT_febe8230) +
         ((uint)uVar3 - (uint)DAT_febe822e) + ((uint)uVar1 - (uint)DAT_febe822c);
}

void step_channel_difference_latch_a(void)

{
  ushort uVar1;
  short sVar2;
  ushort uVar3;
  byte bVar4;
  int iVar5;
  uint32_t puVar6;
  int iVar7;
  int iVar8;
  byte bVar9;
  undefined1 uVar10;
  byte bVar11;
  byte bVar12;
  
  uVar10 = DAT_febe77c7;
  bVar4 = DAT_febe77c6;
  bVar11 = DAT_febe77c5;
  bVar12 = DAT_febe77c4;
  puVar6 = 0xfebeb800u;
  if (((byte)DAT_febe71ec & 1) == 0) {
    iVar7 = sum_channel_snapshot_differences_a();
    uVar3 = DAT_00031e62;
    sVar2 = DAT_00031e60;
    if (iVar7 + 0x7fffffff < 0 == (-1 < iVar7 && iVar7 + 0x7fffffff < 0) && iVar7 != -0x7fffffff) {
      iVar5 = iVar7;
      if (iVar7 < 0) {
        iVar5 = -iVar7;
      }
    }
    else {
      iVar5 = 0x7fffffff;
    }
    iVar8 = (int)DAT_00031e60;
    uVar1 = (*((ushort *)camry_host_ptr((uint32_t)(puVar6 + -0x3a5a))));
    (*((int *)camry_host_ptr((uint32_t)((0xffffbfd0u + (uint32_t)((int)puVar6)))))) = iVar7;
    (*((short *)camry_host_ptr((uint32_t)((0xffffbfceu + (uint32_t)((int)puVar6)))))) = sVar2;
    bVar9 = bVar4;
    if ((iVar5 - iVar8 < 0 == (iVar5 < 0 != iVar8 < 0 && iVar8 < 0 == iVar5 - iVar8 < 0) &&
         iVar5 != iVar8) && (uVar1 <= uVar3)) {
      bVar11 = 0;
      if (bVar12 < DAT_00031e5c) {
        uVar10 = 0;
        bVar12 = bVar12 + 1;
        bVar9 = bVar12;
        if (bVar12 <= bVar4) {
          bVar9 = bVar4;
        }
      }
      else {
        uVar10 = 0x5a;
      }
    }
    else if (bVar11 < DAT_00031e5d) {
      bVar11 = bVar11 + 1;
    }
    else {
      bVar12 = 0;
      uVar10 = 0xa5;
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbfc4u + (uint32_t)((int)puVar6) * 1u)))) = bVar12;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbfc5u + (uint32_t)((int)puVar6) * 1u)))) = bVar11;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbfc6u + (uint32_t)((int)puVar6) * 1u)))) = bVar9;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbfc7u + (uint32_t)((int)puVar6) * 1u)))) = uVar10;
  }
  return;
}

void reset_three_window_and_recoverable_monitors_42592(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe77d4 = 0;
  DAT_febe77d6 = 0;
  DAT_febe77d8 = 0;
  reset_windowed_monitor((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe77dcu)));
  reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)((0xffffbfecu + (uint32_t)((int)puVar1))))));
  reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)((0xffffbffcu + (uint32_t)((int)puVar1))))));
  reset_recoverable_monitor(((F33RecoverableMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3ff4))));
  return;
}

void clear_three_window_and_recoverable_monitors_425c4(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe77d4 = 0;
  DAT_febe77d6 = 0;
  DAT_febe77d8 = 0;
  reset_windowed_monitor((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe77dcu)));
  reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)((0xffffbfecu + (uint32_t)((int)puVar1))))));
  reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)((0xffffbffcu + (uint32_t)((int)puVar1))))));
  reset_recoverable_monitor(((F33RecoverableMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3ff4))));
  return;
}

void step_channel_phase_monitors_a(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bbf0 == 'Z') {
    puVar1 = 0xfebeb800u;
    reset_windowed_monitor((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe77dcu)));
    reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)((0xffffbfecu + (uint32_t)((int)puVar1))))));
    reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)((0xffffbffcu + (uint32_t)((int)puVar1))))));
  }
  else {
    if (((DAT_febe71ec & 1) == 0) && (DAT_febeeb85 == 'Z')) {
      DAT_febe77d4 = 0x38;
      DAT_febe77d6 = ((volatile int16_t *)camry_host_ptr(0xfebe7e78u))[0];
      DAT_febe77d8 = ((volatile int16_t *)camry_host_ptr(0xfebe7e84u))[0];
      step_windowed_monitor
                ((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe77dcu)),(F33WindowedMonitorLimits *)((undefined *)camry_host_ptr(0x2b7f0u)),
                 (F33TwoSidedMonitorCallbacks *)&PTR_classify_channel_phase_sample_a_00028570);
      (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffbfd4u + (uint32_t)((int)puVar1)))))) = 0x39;
      (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffbfd6u + (uint32_t)((int)puVar1)))))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x3986))));
      (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffbfd8u + (uint32_t)((int)puVar1)))))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x397a))));
      step_windowed_monitor
                (((F33WindowedMonitorState *)camry_host_ptr((uint32_t)((0xffffbfecu + (uint32_t)((int)puVar1))))),
                 (F33WindowedMonitorLimits *)((undefined *)camry_host_ptr(0x2b7f0u)),
                 (F33TwoSidedMonitorCallbacks *)&PTR_classify_channel_phase_sample_a_00028570);
      (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffbfd4u + (uint32_t)((int)puVar1)))))) = 0x3a;
      (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffbfd6u + (uint32_t)((int)puVar1)))))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x3984))));
      (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffbfd8u + (uint32_t)((int)puVar1)))))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x3978))));
      step_windowed_monitor
                (((F33WindowedMonitorState *)camry_host_ptr((uint32_t)((0xffffbffcu + (uint32_t)((int)puVar1))))),
                 (F33WindowedMonitorLimits *)((undefined *)camry_host_ptr(0x2b7f0u)),
                 (F33TwoSidedMonitorCallbacks *)&PTR_classify_channel_phase_sample_a_00028570);
      step_recoverable_monitor
                (((F33RecoverableMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3ff4))),
                 (F33RecoverableMonitorLimits *)((undefined *)camry_host_ptr(0x2b7f8u)),
                 (F33RecoverableMonitorCallbacks *)
                 &PTR_classify_channel_phase_failure_count_a_000285a4);
      goto LAB_000426e2;
    }
    puVar1 = 0xfebeb800u;
    classify_counter_limits_and_clear_selected_fields_6ae48(((undefined *)camry_host_ptr(0xfebe77dcu)),((undefined *)camry_host_ptr(0x2b7f0u)));
    classify_counter_limits_and_clear_selected_fields_6ae48(((undefined *)camry_host_ptr((uint32_t)((0xffffbfecu + (uint32_t)((int)puVar1))))), ((undefined *)camry_host_ptr(0x2b7f0u)));
    classify_counter_limits_and_clear_selected_fields_6ae48(((undefined *)camry_host_ptr((uint32_t)((0xffffbffcu + (uint32_t)((int)puVar1))))), ((undefined *)camry_host_ptr(0x2b7f0u)));
  }
  reset_recoverable_monitor(((F33RecoverableMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3ff4))));
LAB_000426e2:
  set_channel_monitor_status_a(0,(uchar)(*((undefined4 *)camry_host_ptr((uint32_t)((0xffffbfdcu + (uint32_t)((int)puVar1)))))));
  set_channel_monitor_status_a(1,(uchar)(*((undefined4 *)camry_host_ptr((uint32_t)((0xffffbfecu + (uint32_t)((int)puVar1)))))));
  set_channel_monitor_status_a(2,(uchar)(*((undefined4 *)camry_host_ptr((uint32_t)((0xffffbffcu + (uint32_t)((int)puVar1)))))));
  set_channel_monitor_status_a(10,(uchar)(*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x3ff4)))));
  return;
}

uint classify_channel_phase_sample_a(void)

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
  
  uVar4 = DAT_febe7da6;
  cVar3 = DAT_febe62e4;
  uVar2 = DAT_0002b83a;
  uVar1 = DAT_0002b834;
  iVar8 = (int)((int)(int16_t)DAT_febe77d8);
  iVar7 = (int)((int)(int16_t)DAT_febe62dc);
  store_saturating_absolute_s16_6a522((int)((int)(int16_t)DAT_febe77d6),&sStack_22);
  iVar5 = (int)sStack_22;
  iVar6 = (int)(int16_t)DAT_0002b830;
  if (cVar3 == '\0') {
    if ((((iVar5 - iVar6 < 0 == (iVar5 < 0 != iVar6 < 0 && iVar6 < 0 == iVar5 - iVar6 < 0) &&
           iVar5 != iVar6) ||
         (iVar6 = (int)(int16_t)DAT_0002b832,
         iVar8 - iVar6 < 0 != (iVar8 < 0 != iVar6 < 0 && iVar6 < 0 == iVar8 - iVar6 < 0))) &&
        (uVar4 <= uVar1)) &&
       (iVar6 = (int)(int16_t)DAT_0002b83c,
       iVar7 - iVar6 < 0 == (iVar7 < 0 != iVar6 < 0 && iVar6 < 0 == iVar7 - iVar6 < 0) &&
       iVar7 != iVar6)) {
      return 0x22;
    }
    iVar6 = (int)(int16_t)DAT_0002b836;
    if (iVar5 - iVar6 < 0 == (iVar5 < 0 != iVar6 < 0 && iVar6 < 0 == iVar5 - iVar6 < 0) &&
        iVar5 != iVar6) {
      return 0x33;
    }
    iVar5 = (int)(int16_t)DAT_0002b838;
    if (iVar8 - iVar5 < 0 != (iVar8 < 0 != iVar5 < 0 && iVar5 < 0 == iVar8 - iVar5 < 0)) {
      return 0x33;
    }
  }
  else {
    if (((iVar5 - iVar6 < 0 == (iVar5 < 0 != iVar6 < 0 && iVar6 < 0 == iVar5 - iVar6 < 0) &&
          iVar5 != iVar6) && (uVar4 <= uVar1)) &&
       (iVar6 = (int)(int16_t)DAT_0002b83c,
       iVar7 - iVar6 < 0 == (iVar7 < 0 != iVar6 < 0 && iVar6 < 0 == iVar7 - iVar6 < 0) &&
       iVar7 != iVar6)) {
      return 0x22;
    }
    iVar6 = (int)(int16_t)DAT_0002b836;
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

void report_diagnostic_healthy_observed_cell_427a0(void)

{
  report_diagnostic_healthy_observed((uint)DAT_febe77d4);
  return;
}

void report_diagnostic_event_failure_10_427b0(void)

{
  report_diagnostic_event_failure((uint)DAT_febe77d4,10);
  return;
}

uint classify_channel_phase_failure_count_a(void)

{
  ushort uVar1;
  
  uVar1 = (ushort)DAT_0002b82e;
  if (((DAT_febe77e4 < uVar1) && (DAT_febe77f4 < uVar1)) && (DAT_febe7804 < uVar1)) {
    return 0x11;
  }
  return 0x22;
}

void return_only_stub_427ee(void)

{
  return;
}

void return_only_stub_427f0(void)

{
  return;
}

void publish_channel_monitor_actions_a(void)

{
  byte bVar1;
  byte bVar2;
  ushort uVar3;
  uint32_t puVar4;
  uchar uVar5;
  undefined1 uVar6;
  
  uVar3 = DAT_febe71ec;
  puVar4 = 0xfebeb800u;
  retain_and_clear_fault_record(2);
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fdb))))) |
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fdc))))) |
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe2))))) |
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe3))))) |
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe4))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe5))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe6))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe7))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe8)))))) &
      0x11) == 0x11) {
    encode_fault_action_kind('\x02','\n');
  }
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fdc))))) |
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe6))))) |
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe7))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe8))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe2))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe3))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe4)))))) &
      0x22) == 0x22) {
    encode_fault_action_kind('\x02','#');
  }
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fdb))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe5))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fdf))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe0))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe1)))))) &
      0x22) == 0x22) {
    encode_fault_action_kind('\x02','\x1b');
  }
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fdd))))) & 0x22) == 0x22) {
    encode_fault_action_kind('\x02','\x1d');
  }
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fde))))) & 0x22) == 0x22) {
    encode_fault_action_kind('\x02','\'');
  }
  if (((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fdb))))) |
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fdc))))) |
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe2))))) |
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe3))))) |
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe4))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe5))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe6))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe7))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe8)))))) &
       0x22) == 0x22) && ((uVar3 & 1) == 0)) {
    encode_fault_action_kind('\x02','\n');
  }
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fdc))))) |
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe2))))) |
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe3))))) |
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe4))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe5))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe6))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe7))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe8)))))) &
      0x22) == 0x22) {
    encode_fault_action_kind('\x02','2');
  }
  select_current_fault_record(2);
  bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe6))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe7))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe8)))));
  uVar6 = 0;
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe1))))) | bVar1 | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe0))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fdf)))))) & 0x11) == 0x11) {
    uVar6 = 0x5a;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fda))))) = uVar6;
  uVar6 = 0x11;
  if ((((((bVar1 == 0 && (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe5))))) == '\0') && (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe4))))) == '\0') &&
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe3))))) == '\0') && (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe2))))) == '\0') && (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fdc))))) == '\0') &&
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fdb))))) == '\0') {
    uVar6 = 0;
  }
  uVar5 = '\0';
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fd9))))) = uVar6;
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fdb))))) != '\0' ||
      ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fdd))))) != '\0' ||
      ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fdf))))) != 0 ||
      ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe0))))) != 0 ||
      ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe1))))) != 0 ||
      ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe5))))) != '\0' ||
      ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe6))))) != 0 ||
      ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe7))))) != 0 ||
      ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe8))))) != 0 ||
      ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe2))))) != '\0' ||
      ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe3))))) != '\0' || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe4))))) != '\0' || (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fdc))))) != '\0')))))))))))) {
    uVar5 = '\x11';
  }
  set_diagnostic_cache_blocker('\x03',uVar5);
  bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe6))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe7))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe8)))));
  bVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fdb))))) |
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fdd))))) |
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fdf))))) |
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fdc))))) | bVar1 | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe4))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe3))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe2))))) |
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe5))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe1))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe0)))));
  if ((bVar2 == 0) || (bVar2 == 0x11)) {
    uVar6 = 0;
  }
  else {
    uVar6 = 0x5a;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fd8))))) = uVar6;
  uVar5 = '\0';
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fdd))))) |
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fdf))))) |
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe0))))) |
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe1))))) |
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fdb))))) |
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fdc))))) |
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe2))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe3))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe4))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x3fe5))))) | bVar1) & 0x11) ==
      0x11) {
    uVar5 = 'Z';
  }
  set_monitor_pending_projection('\x02',uVar5);
  return;
}

void set_channel_monitor_status_a(uint index,uchar status)

{
  if ((index & 0xff) < 0xe) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7818u + (uint32_t)(index & 0xff) * 1u)))) = status;
  }
  return;
}

void reset_latched_monitor_febe782c(void)

{
  reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe782cu)));
  return;
}

void reset_latched_monitor_febe782c_42a5a(void)

{
  reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe782cu)));
  return;
}

void update_gated_latched_monitor_a_eleven_42a6a(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bbf4 == 'Z') {
    reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe782cu)));
  }
  else if (((DAT_febe6764 & 1) == 0) && (DAT_febee820 == 'Z')) {
    step_latched_monitor
              ((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe782cu)),(F33MonitorLimits *)((undefined *)camry_host_ptr(0x2b7feu)),
               (F33TwoSidedMonitorCallbacks *)&PTR_FUN_000285e0);
  }
  else {
    retain_disabled_latched_monitor
              ((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe782cu)),(F33MonitorLimits *)((undefined *)camry_host_ptr(0x2b7feu)));
  }
  set_channel_monitor_status_a(0xb,(uchar)(*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x3fd4)))));
  return;
}

undefined4 test_a_sample_absolute_or_delta_limit_42ac4(void)

{
  int iVar1;
  int iVar2;
  
  iVar1 = (uint)DAT_febe66b8 - (uint)DAT_febe66ae;
  if ((DAT_febe827c == 'Z') &&
     (((uint)DAT_0002b83e < (uint)DAT_febe66b8 ||
      (iVar2 = (int)DAT_0002b840,
      iVar1 - iVar2 < 0 != (iVar1 < 0 != iVar2 < 0 && iVar2 < 0 == iVar1 - iVar2 < 0) ||
      iVar1 == iVar2)))) {
    return 0x5a;
  }
  return 0;
}

undefined4 classify_a_sample_flag_combination_42af4(void)

{
  char cVar1;
  uint uVar2;
  char cVar3;
  char cVar4;
  char cVar5;
  int iVar6;
  undefined4 uVar7;
  
  cVar5 = DAT_febe8280;
  cVar4 = DAT_febe827c;
  cVar3 = DAT_febe827b;
  uVar2 = DAT_febe6618;
  cVar1 = DAT_febe65f6;
  iVar6 = test_a_sample_absolute_or_delta_limit_42ac4();
  if ((cVar1 == 'Z') && ((uVar2 & 1) == 0)) {
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

void report_diagnostic_healthy_observed_86_42b50(void)

{
  report_diagnostic_healthy_observed(0x86);
  return;
}

void report_diagnostic_event_failure_86_32_42b60(void)

{
  report_diagnostic_event_failure(0x86,0x32);
  return;
}

void reset_latched_monitor_febe7838(void)

{
  reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7838u)));
  return;
}

void reset_latched_monitor_febe7838_42b84(void)

{
  reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7838u)));
  return;
}

void update_raw_lower_bound_latched_monitor_a_42b94(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bbf8 == 'Z') {
    reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7838u)));
  }
  else if (((DAT_febe71ec & 1) == 0) && (DAT_febeeb85 == 'Z')) {
    step_latched_monitor
              ((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7838u)),(F33MonitorLimits *)((undefined *)camry_host_ptr(0x2b802u)),
               (F33TwoSidedMonitorCallbacks *)&PTR_classify_channel_raw_lower_bound_a_00028614);
  }
  else {
    retain_disabled_latched_monitor
              ((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7838u)),(F33MonitorLimits *)((undefined *)camry_host_ptr(0x2b802u)));
  }
  set_channel_monitor_status_a(0xd,(uchar)(*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x3fc8)))));
  return;
}

uint classify_channel_raw_lower_bound_a(void)

{
  if ((short)output_request_status != 0) {
    return 0x44;
  }
  if ((((DAT_0002b842 <= DAT_febe6238) || (DAT_febe636c != 'Z')) &&
      ((DAT_0002b842 <= DAT_febe623a || (DAT_febe636d != 'Z')))) &&
     ((DAT_0002b842 <= DAT_febe623c || (DAT_febe636e != 'Z')))) {
    if ((DAT_0002b844 <= DAT_febe6238) &&
       ((((DAT_febe636c == 'Z' && (DAT_0002b844 <= DAT_febe623a)) && (DAT_febe636d == 'Z')) &&
        ((DAT_0002b844 <= DAT_febe623c && (DAT_febe636e == 'Z')))))) {
      return 0x11;
    }
    return 0x33;
  }
  return 0x22;
}

void report_diagnostic_healthy_observed_136_42c68(void)

{
  report_diagnostic_healthy_observed(0x136);
  return;
}

void report_diagnostic_event_failure_136_10_42c78(void)

{
  report_diagnostic_event_failure(0x136,10);
  return;
}

void reset_windowed_monitor_febe7844(void)

{
  reset_windowed_monitor((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe7844u)));
  return;
}

void reset_windowed_monitor_febe7844_42c9a(void)

{
  reset_windowed_monitor((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe7844u)));
  return;
}

void update_sample_sum_window_monitor_a_42caa(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bbfc == 'Z') {
    reset_windowed_monitor((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe7844u)));
  }
  else if (((DAT_febe71ec & 1) == 0) && (DAT_febeeb85 == 'Z')) {
    step_windowed_monitor
              ((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe7844u)),(F33WindowedMonitorLimits *)((undefined *)camry_host_ptr(0x2b806u)),
               (F33TwoSidedMonitorCallbacks *)&PTR_classify_channel_sample_sum_a_00028648);
  }
  else {
    classify_counter_limits_and_clear_selected_fields_6ae48(((undefined *)camry_host_ptr(0xfebe7844u)), ((ushort *)camry_host_ptr((uint32_t)(0x2b806))));
  }
  set_channel_monitor_status_a(3,(uchar)(*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x3fbc)))));
  return;
}

uint classify_channel_sample_sum_a(void)

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
  sVar2 = DAT_febe7b30;
  cVar1 = DAT_febe6368;
  iVar8 = (int)(*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebe7e78u + (uint32_t)(1) * 2u))));
  iVar4 = (int)((volatile int16_t *)camry_host_ptr(0xfebe7e78u))[0];
  iVar7 = (int)(*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebe7e78u + (uint32_t)(2) * 2u))));
  iVar5 = iVar7 + iVar8 + iVar4;
  if (iVar4 + 0x7fff < 0 == (-1 < iVar4 && iVar4 + 0x7fff < 0) && iVar4 != -0x7fff) {
    if (iVar4 < 0) {
      iVar4 = (int)-((volatile int16_t *)camry_host_ptr(0xfebe7e78u))[0];
    }
  }
  else {
    iVar4 = 0x7fff;
  }
  if (iVar8 + 0x7fff < 0 == (-1 < iVar8 && iVar8 + 0x7fff < 0) && iVar8 != -0x7fff) {
    if (iVar8 < 0) {
      iVar8 = (int)-(*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebe7e78u + (uint32_t)(1) * 2u))));
    }
  }
  else {
    iVar8 = 0x7fff;
  }
  if (iVar7 + 0x7fff < 0 == (-1 < iVar7 && iVar7 + 0x7fff < 0) && iVar7 != -0x7fff) {
    if (iVar7 < 0) {
      iVar7 = (int)-(*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebe7e78u + (uint32_t)(2) * 2u))));
    }
  }
  else {
    iVar7 = 0x7fff;
  }
  store_saturating_absolute_s32_6a53e(iVar5,&local_24);
  if (((uVar6 & 0x40004) == 0) &&
     ((cVar3 == 'Z' ||
      (((iVar5 = (int)DAT_0002b848,
        iVar4 - iVar5 < 0 != (iVar4 < 0 != iVar5 < 0 && iVar5 < 0 == iVar4 - iVar5 < 0) &&
        (iVar8 - iVar5 < 0 != (iVar8 < 0 != iVar5 < 0 && iVar5 < 0 == iVar8 - iVar5 < 0))) &&
       (iVar7 - iVar5 < 0 != (iVar7 < 0 != iVar5 < 0 && iVar5 < 0 == iVar7 - iVar5 < 0))))))) {
    if (((int)local_24 - (int)PTR_LAB_000010ca_4_0002b84c < 0 ==
         ((int)local_24 < 0 != (int)PTR_LAB_000010ca_4_0002b84c < 0 &&
         (int)PTR_LAB_000010ca_4_0002b84c < 0 ==
         (int)local_24 - (int)PTR_LAB_000010ca_4_0002b84c < 0) &&
         local_24 != PTR_LAB_000010ca_4_0002b84c) && (cVar1 == 'Z')) {
      uVar6 = 0x22;
    }
    else if (((int)local_24 - (int)PTR_LAB_000010ca_4_0002b850 < 0 ==
              ((int)local_24 < 0 != (int)PTR_LAB_000010ca_4_0002b850 < 0 &&
              (int)PTR_LAB_000010ca_4_0002b850 < 0 ==
              (int)local_24 - (int)PTR_LAB_000010ca_4_0002b850 < 0) &&
              local_24 != PTR_LAB_000010ca_4_0002b850) || ((cVar1 != 'Z' || (sVar2 != -1)))) {
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

void report_diagnostic_healthy_observed_41_42dde(void)

{
  report_diagnostic_healthy_observed(0x41);
  return;
}

void report_diagnostic_event_failure_41_10_42dee(void)

{
  report_diagnostic_event_failure(0x41,10);
  return;
}

void reset_midpoint_pair_b_latched_triplet_42e00(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe7854 = 0;
  DAT_febe7856 = 0;
  DAT_febe7858 = 0;
  reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe785cu)));
  reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3f98))));
  reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3f8c))));
  return;
}

void clear_midpoint_pair_b_latched_triplet_42e2a(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe7854 = 0;
  DAT_febe7856 = 0;
  DAT_febe7858 = 0;
  reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe785cu)));
  reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3f98))));
  reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3f8c))));
  return;
}

void update_midpoint_pair_b_latched_triplet_42e54(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bc00 == 'Z') {
    reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe785cu)));
    reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3f98))));
    reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3f8c))));
  }
  else if ((DAT_febe71ec >> 1 & 1) == 0) {
    DAT_febe7854 = 0x2d;
    DAT_febe7856 = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebe7e84u + (uint32_t)(3) * 2u))));
    DAT_febe7858 = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebe7e90u + (uint32_t)(3) * 2u))));
    step_latched_monitor
              ((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe785cu)),(F33MonitorLimits *)&PTR_DAT_0002b854,
               (F33TwoSidedMonitorCallbacks *)&PTR_classify_channel_negative_pair_b_0002867c);
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x3fac)))) = 0x2e;
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x3faa)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x3974))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x3fa8)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x3968))));
    step_latched_monitor
              (((F33LatchedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3f98))),(F33MonitorLimits *)&PTR_DAT_0002b854,
               (F33TwoSidedMonitorCallbacks *)&PTR_classify_channel_negative_pair_b_0002867c);
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x3fac)))) = 0x2f;
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x3faa)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x3972))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x3fa8)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x3966))));
    step_latched_monitor
              (((F33LatchedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3f8c))),(F33MonitorLimits *)&PTR_DAT_0002b854,
               (F33TwoSidedMonitorCallbacks *)&PTR_classify_channel_negative_pair_b_0002867c);
  }
  else {
    retain_disabled_latched_monitor
              ((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe785cu)),(F33MonitorLimits *)&PTR_DAT_0002b854);
    retain_disabled_latched_monitor
              (((F33LatchedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3f98))),(F33MonitorLimits *)&PTR_DAT_0002b854);
    retain_disabled_latched_monitor
              (((F33LatchedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3f8c))),(F33MonitorLimits *)&PTR_DAT_0002b854);
  }
  set_channel_monitor_status_b(4,(uchar)(*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x3fa4)))));
  set_channel_monitor_status_b(5,(uchar)(*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x3f98)))));
  set_channel_monitor_status_b(6,(uchar)(*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x3f8c)))));
  return;
}

uint classify_channel_negative_pair_b(void)

{
  int iVar1;
  int iVar2;
  
  iVar2 = (int)(int16_t)DAT_0002b87e;
  iVar1 = ((int)(int16_t)DAT_febe7856) - iVar2;
  if ((iVar1 < 0 != (((int)(int16_t)DAT_febe7856) < 0 != iVar2 < 0 && iVar2 < 0 == iVar1 < 0)) &&
     (iVar2 = (int)(int16_t)DAT_0002b880, iVar1 = ((int)(int16_t)DAT_febe7858) - iVar2,
     iVar1 < 0 != (((int)(int16_t)DAT_febe7858) < 0 != iVar2 < 0 && iVar2 < 0 == iVar1 < 0))) {
    return 0x22;
  }
  return 0x11;
}

void report_diagnostic_healthy_observed_cell_42f58(void)

{
  report_diagnostic_healthy_observed((uint)DAT_febe7854);
  return;
}

void report_diagnostic_event_failure_10_42f68(void)

{
  report_diagnostic_event_failure((uint)DAT_febe7854,10);
  return;
}

void return_only_stub_42f7a(void)

{
  return;
}

void initialize_clipped_b_three_channel_q16_state_42f7c(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  if ((int)DAT_febe6310 + 0x7fff < 0 == (-1 < (int)DAT_febe6310 && (int)DAT_febe6310 + 0x7fff < 0) &&
      ((int)(int32_t)DAT_febe6310) != -0x7fff) {
    iVar3 = ((int)(int32_t)DAT_febe6310);
    if ((int)DAT_febe6310 + -0x7fff < 0 == ((int)DAT_febe6310 < 0 && -1 < (int)DAT_febe6310 + -0x7fff) &&
        ((int)(int32_t)DAT_febe6310) != 0x7fff) {
      iVar3 = 0x7fff;
    }
  }
  else {
    iVar3 = -0x7fff;
  }
  if ((int)DAT_febe6314 + 0x7fff < 0 == (-1 < (int)DAT_febe6314 && (int)DAT_febe6314 + 0x7fff < 0) &&
      ((int)(int32_t)DAT_febe6314) != -0x7fff) {
    iVar2 = ((int)(int32_t)DAT_febe6314);
    if ((int)DAT_febe6314 + -0x7fff < 0 == ((int)DAT_febe6314 < 0 && -1 < (int)DAT_febe6314 + -0x7fff) &&
        ((int)(int32_t)DAT_febe6314) != 0x7fff) {
      iVar2 = 0x7fff;
    }
  }
  else {
    iVar2 = -0x7fff;
  }
  if ((int)DAT_febe6318 + 0x7fff < 0 == (-1 < (int)DAT_febe6318 && (int)DAT_febe6318 + 0x7fff < 0) &&
      ((int)(int32_t)DAT_febe6318) != -0x7fff) {
    iVar1 = ((int)(int32_t)DAT_febe6318);
    if ((int)DAT_febe6318 + -0x7fff < 0 == ((int)DAT_febe6318 < 0 && -1 < (int)DAT_febe6318 + -0x7fff) &&
        ((int)(int32_t)DAT_febe6318) != 0x7fff) {
      iVar1 = 0x7fff;
    }
  }
  else {
    iVar1 = -0x7fff;
  }
  DAT_febe7880 = (short)iVar3;
  DAT_febe7882 = (short)iVar2;
  DAT_febe7884 = (short)iVar1;
  DAT_febe7888 = iVar3 << 0x10;
  DAT_febe788c = iVar2 << 0x10;
  DAT_febe7890 = iVar1 << 0x10;
  return;
}

void filter_clipped_b_three_channel_q16_state_42fee(void)

{
  uint uVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  
  if ((int)DAT_febe6310 + 0x7fff < 0 == (-1 < (int)DAT_febe6310 && (int)DAT_febe6310 + 0x7fff < 0) &&
      ((int)(int32_t)DAT_febe6310) != -0x7fff) {
    iVar2 = (int)(short)((int)(int32_t)DAT_febe6310);
    if ((int)DAT_febe6310 + -0x7fff < 0 == ((int)DAT_febe6310 < 0 && -1 < (int)DAT_febe6310 + -0x7fff) &&
        ((int)(int32_t)DAT_febe6310) != 0x7fff) {
      iVar2 = 0x7fff;
    }
  }
  else {
    iVar2 = -0x7fff;
  }
  if ((int)DAT_febe6314 + 0x7fff < 0 == (-1 < (int)DAT_febe6314 && (int)DAT_febe6314 + 0x7fff < 0) &&
      ((int)(int32_t)DAT_febe6314) != -0x7fff) {
    iVar3 = (int)(short)((int)(int32_t)DAT_febe6314);
    if ((int)DAT_febe6314 + -0x7fff < 0 == ((int)DAT_febe6314 < 0 && -1 < (int)DAT_febe6314 + -0x7fff) &&
        ((int)(int32_t)DAT_febe6314) != 0x7fff) {
      iVar3 = 0x7fff;
    }
  }
  else {
    iVar3 = -0x7fff;
  }
  if ((int)DAT_febe6318 + 0x7fff < 0 == (-1 < (int)DAT_febe6318 && (int)DAT_febe6318 + 0x7fff < 0) &&
      ((int)(int32_t)DAT_febe6318) != -0x7fff) {
    iVar4 = (int)(short)((int)(int32_t)DAT_febe6318);
    if ((int)DAT_febe6318 + -0x7fff < 0 == ((int)DAT_febe6318 < 0 && -1 < (int)DAT_febe6318 + -0x7fff) &&
        ((int)(int32_t)DAT_febe6318) != 0x7fff) {
      iVar4 = 0x7fff;
    }
  }
  else {
    iVar4 = -0x7fff;
  }
  uVar1 = (uint)DAT_0002b882;
  if (uVar1 - 1 < 0xffff) {
    iVar5 = (int)((int)(int16_t)DAT_febe7880) * uVar1;
    iVar2 = iVar2 * uVar1;
  }
  else {
    iVar5 = (int)((int)(int16_t)DAT_febe7880) << 0x10;
    iVar2 = iVar2 << 0x10;
  }
  DAT_febe7888 = iVar2 + (DAT_febe7888 - iVar5);
  if (uVar1 - 1 < 0xffff) {
    iVar2 = (int)((int)(int16_t)DAT_febe7882) * uVar1;
    iVar3 = iVar3 * uVar1;
  }
  else {
    iVar2 = (int)((int)(int16_t)DAT_febe7882) << 0x10;
    iVar3 = iVar3 << 0x10;
  }
  DAT_febe788c = iVar3 + (DAT_febe788c - iVar2);
  if (uVar1 - 1 < 0xffff) {
    iVar2 = (int)((int)(int16_t)DAT_febe7884) * uVar1;
    iVar4 = iVar4 * uVar1;
  }
  else {
    iVar2 = (int)((int)(int16_t)DAT_febe7884) << 0x10;
    iVar4 = iVar4 << 0x10;
  }
  DAT_febe7880 = (short)((int)DAT_febe7888 / 0x10000);
  DAT_febe7890 = iVar4 + (DAT_febe7890 - iVar2);
  DAT_febe7882 = (short)((int)DAT_febe788c / 0x10000);
  DAT_febe7884 = (short)((int)DAT_febe7890 / 0x10000);
  return;
}
