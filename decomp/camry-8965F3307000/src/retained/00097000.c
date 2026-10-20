#include "common.h"

void dcm_cancel_communication_continuation(void)

{
  dcm_invalidate_queued_event('&','\0');
  set_diagnostic_busy_marker_from_done_flag_9560e(1);
  return;
}

uint dcm_dispatch_communication_control_lifetime
               (uchar operation,F33DcmMessageContext *message,uchar subfunction)

{
  uint uVar1;
  
  if (operation == '\0') {
    uVar1 = dcm_begin_configured_communication_request(message,subfunction);
  }
  else {
    uVar1 = 0;
    if (operation == '\x02') {
      dcm_cancel_communication_continuation();
    }
  }
  return uVar1;
}

void dcm_notify_communication_session_change(uchar old_session,uchar new_session)

{
  undefined1 uVar1;
  undefined8 uVar2;
  int iVar3;
  uint uVar4;
  
  uVar2 = 0x23dfcfebeb800;
  if ((dcm_communication_configuration.restore_enabled == '\x01') &&
     ((new_session == '\x01' ||
      ((dcm_communication_lifetime.accepted_active == '\x01' &&
       (iVar3 = check_dcm_service_and_optional_subfunction_membership_916ec(0x28,dcm_communication_lifetime.protocol_selector, (uint)(byte)new_session), iVar3 != 0)))))
     ) {
    for (uVar4 = 0; iVar3 = (int)((ulonglong)uVar2 >> 0x20), uVar4 < (*((byte *)camry_host_ptr((uint32_t)(iVar3 + 0x23cc))));
        uVar4 = uVar4 + 1 & 0xff) {
      if ((*((char *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)(iVar3 + 0x23d0)))) + uVar4 * 2)))) == '\x01') {
        uVar1 = (*((undefined1 *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)(iVar3 + 0x23d0)))) + uVar4 * 2 + 1))));
        iVar3 = ((void)(uVar1), return_const_b_9713e());
        if (iVar3 != 8) {
          ((void)(uVar1), (void)(8), return_const_0_9713a());
          ((void)(uVar1), (void)(8), return_only_stub_97138());
        }
      }
    }
  }
  return;
}

void dcm_resume_queued_communication_request(void)

{
  uint uVar1;
  ushort node;
  
  if (dcm_communication_lifetime.subfunction < 6) {
    uVar1 = *((uint8_t *)camry_host_ptr((uint32_t)(dcm_communication_lifetime.retained_message.request))) & 0xf;
    if (uVar1 - 1 < 3) {
      node = 0;
      if (dcm_communication_lifetime.subfunction == '\x04' ||
          dcm_communication_lifetime.subfunction == '\x05') {
        node = CONCAT11((*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(dcm_communication_lifetime.retained_message.request) + (uint32_t)(1) * 1u)))),
                        (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(dcm_communication_lifetime.retained_message.request) + (uint32_t)(2) * 1u)))));
      }
      dcm_complete_or_queue_communication_request
                ((uchar)((int)(uint)*((uint8_t *)camry_host_ptr((uint32_t)(dcm_communication_lifetime.retained_message.request))) >> 4),
                 dcm_communication_lifetime.subfunction,node,
                 (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x261abu + (uint32_t)((short)(ushort)dcm_communication_lifetime.subfunction * 3 + uVar1) * 1u)))),
                 dcm_communication_lifetime.resume_row);
    }
  }
  return;
}

uint dcm_check_communication_application_admission
               (uchar subfunction,uchar communication_type,ushort node,uchar *nrc)

{
  uint uVar1;
  
  uVar1 = admit_application_communication_request(subfunction,communication_type,node,nrc);
  return uVar1;
}

uint apply_and_complete_communication_policy_97128(uchar param_1,uchar param_2)

{
  return apply_and_complete_communication_policy_request(param_1,param_2);
}

void return_only_stub_97138(void)

{
  return;
}

undefined4 return_const_0_9713a(void)

{
  return 0;
}

undefined4 return_const_b_9713e(void)

{
  return 0xb;
}

uint dcm_communication_enable_rx_tx(uchar operation,F33DcmMessageContext *message)

{
  uint uVar1;
  
  uVar1 = dcm_dispatch_communication_control_lifetime(operation,message,'\0');
  return uVar1;
}

uint dcm_communication_enable_rx_disable_tx(uchar operation,F33DcmMessageContext *message)

{
  uint uVar1;
  
  uVar1 = dcm_dispatch_communication_control_lifetime(operation,message,'\x01');
  return uVar1;
}

uint dcm_communication_disable_rx_tx_request(uchar operation,F33DcmMessageContext *message)

{
  uint uVar1;
  
  uVar1 = dcm_dispatch_communication_control_lifetime(operation,message,'\x03');
  return uVar1;
}

bool find_enabled_routine_id_row_97172(ushort param_1,undefined2 *param_2)

{
  ushort uVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  
  if (DAT_00026492 != 0) {
    uVar4 = 0;
    uVar3 = (uint)(ushort)(DAT_00026492 - 1);
    if ((DAT_00026918 <= param_1) && (uVar1 = DAT_00026918, param_1 <= (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x26918u + (uint32_t)(uVar3 * 4) * 2u))))))
    {
      while( true ) {
        if (uVar1 == param_1) {
          *param_2 = (short)uVar4;
          return (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2691bu + (uint32_t)(uVar4 * 8) * 1u)))) != '\x01';
        }
        if (uVar3 <= uVar4) break;
        uVar2 = uVar3 + uVar4 >> 1;
        if ((*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x26918u + (uint32_t)(uVar2 * 4) * 2u)))) < param_1) {
          uVar4 = uVar2 + 1 & 0xffff;
          uVar2 = uVar3;
        }
        uVar3 = uVar2;
        uVar1 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x26918u + (uint32_t)(uVar4 * 4) * 2u))));
      }
    }
  }
  return true;
}

undefined4 check_routine_session_allowlist_971e8(ushort param_1)

{
  int iVar1;
  uint uVar2;
  uint32_t puVar3;
  uint uVar4;
  uchar uStack_11;
  
  puVar3 = 0x23dfcu;
  uVar4 = (uint)param_1;
  if (DAT_00026492 <= uVar4) {
    return 1;
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x269b9u + (uint32_t)((short)param_1 * 0xf) * 1u)))) != '\0') {
    if (1 < *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x264bcu + (uint32_t)(uVar4 * 2) * 1u))))) {
      return 1;
    }
    iVar1 = (uint)*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x264bcu + (uint32_t)(uVar4 * 2) * 1u)))) * 2;
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2624du + (uint32_t)(iVar1) * 1u)))) != '\0') {
      uStack_11 = '\0';
      dcm_get_session(&uStack_11);
      uVar2 = 0;
      while( true ) {
        if ((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2624du + (uint32_t)(iVar1) * 1u)))) <= uVar2) {
          return 1;
        }
        if ((*((uchar *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)(uVar2 * 4 + (*((volatile int32_t *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)(puVar3 + uVar4 * 8 + 0x2b20)))) + 4)))))))) + 1
                      )))) == uStack_11) break;
        uVar2 = uVar2 + 1 & 0xffff;
      }
    }
  }
  return 0;
}

undefined4 check_routine_security_allowlist_9726c(ushort param_1)

{
  int iVar1;
  uint uVar2;
  uint32_t puVar3;
  uint uVar4;
  uchar uStack_11;
  
  puVar3 = 0x23dfcu;
  uVar4 = (uint)param_1;
  if (DAT_00026492 <= uVar4) {
    return 1;
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x269b9u + (uint32_t)((short)param_1 * 0xf) * 1u)))) != '\0') {
    if (1 < *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x264bcu + (uint32_t)(uVar4 * 2) * 1u))))) {
      return 1;
    }
    iVar1 = (uint)*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x264bcu + (uint32_t)(uVar4 * 2) * 1u)))) * 2;
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2624cu + (uint32_t)(iVar1) * 1u)))) != '\0') {
      uStack_11 = '\0';
      dcm_get_security_level(&uStack_11);
      uVar2 = 0;
      while( true ) {
        if ((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2624cu + (uint32_t)(iVar1) * 1u)))) <= uVar2) {
          return 1;
        }
        if ((*((uchar *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)(uVar2 * 4 + (*((volatile int *)camry_host_ptr((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x23dfcu + (uint32_t)(uVar4 * 8 + 0x2b20) * 1u))))))))))) + 0x14)))) ==
            uStack_11) break;
        uVar2 = uVar2 + 1 & 0xffff;
      }
    }
  }
  return 0;
}

uint diag_routine_control_type_supported(ushort configured_index,uchar control_type)

{
  char cVar1;
  uint uVar2;
  
  uVar2 = 1;
  if (configured_index < DAT_00026492) {
    if (control_type == '\x01') {
      cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x269bdu + (uint32_t)((short)configured_index * 0xf) * 1u))));
    }
    else if (control_type == '\x02') {
      cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x269c2u + (uint32_t)((short)configured_index * 0xf) * 1u))));
    }
    else {
      if (control_type != '\x03') {
        return uVar2;
      }
      cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x269bau + (uint32_t)((short)configured_index * 0xf) * 1u))));
    }
    if (cVar1 == '\0') {
      return uVar2;
    }
    uVar2 = 0;
  }
  return uVar2;
}

bool reject_routine_request_length_mismatch_9733a(int param_1,ushort param_2,char param_3)

{
  undefined **ppuVar1;
  uint uVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  undefined *puVar6;
  undefined *puVar7;
  
  uVar5 = (uint)param_2;
  if (DAT_00026492 <= uVar5) {
    return true;
  }
  uVar2 = 0;
  if (param_3 == '\x01') {
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x269bfu + (uint32_t)((short)param_2 * 0xf) * 1u)))) == 0) goto LAB_000973ce;
    ppuVar1 = &PTR_DAT_00026698 + uVar5;
    iVar3 = (short)(ushort)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x269bfu + (uint32_t)((short)param_2 * 0xf) * 1u)))) * 6;
    iVar4 = iVar3 + -6;
    puVar6 = *ppuVar1;
    puVar7 = *ppuVar1;
    if ((*ppuVar1)[iVar3 + -5] == '\a') goto LAB_000973be;
LAB_000973b0:
    puVar6 = puVar6 + iVar4;
    uVar5 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x261d8u + (uint32_t)((byte)puVar7[iVar4 + 1]) * 1u))));
  }
  else {
    if ((param_3 != '\x02') || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x269c4u + (uint32_t)((short)param_2 * 0xf) * 1u)))) == 0)) goto LAB_000973ce;
    ppuVar1 = &PTR_DAT_000267d8 + uVar5;
    iVar3 = (short)(ushort)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x269c4u + (uint32_t)((short)param_2 * 0xf) * 1u)))) * 6;
    iVar4 = iVar3 + -6;
    puVar6 = *ppuVar1;
    puVar7 = *ppuVar1;
    if ((*ppuVar1)[iVar3 + -5] != '\a') goto LAB_000973b0;
LAB_000973be:
    puVar6 = puVar6 + iVar4;
    uVar5 = (uint)*(ushort *)(puVar7 + iVar4 + 2);
  }
  uVar2 = uVar5 + *(ushort *)(puVar6 + 4) + 7 >> 3;
LAB_000973ce:
  return uVar2 + 3 != (*((int *)camry_host_ptr((uint32_t)(param_1 + 4))));
}

bool reject_routine_response_capacity_shortage_973dc(int param_1,ushort param_2,char param_3)

{
  undefined **ppuVar1;
  char cVar2;
  uint uVar3;
  int iVar4;
  uint uVar5;
  undefined *puVar6;
  undefined *puVar7;
  
  uVar5 = (uint)param_2;
  if (DAT_00026492 <= uVar5) {
    return true;
  }
  uVar3 = 0;
  if (param_3 == '\x01') {
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x269c1u + (uint32_t)((short)param_2 * 0xf) * 1u)))) == 0) goto LAB_000974a2;
    ppuVar1 = &PTR_DAT_000266e8 + uVar5;
    iVar4 = (short)(ushort)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x269c1u + (uint32_t)((short)param_2 * 0xf) * 1u)))) * 6;
    cVar2 = (*ppuVar1)[iVar4 + -5];
    puVar6 = *ppuVar1;
    puVar7 = *ppuVar1;
  }
  else if (param_3 == '\x02') {
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x269c6u + (uint32_t)((short)param_2 * 0xf) * 1u)))) == 0) goto LAB_000974a2;
    ppuVar1 = &PTR_DAT_00026828 + uVar5;
    iVar4 = (short)(ushort)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x269c6u + (uint32_t)((short)param_2 * 0xf) * 1u)))) * 6;
    cVar2 = (*ppuVar1)[iVar4 + -5];
    puVar6 = *ppuVar1;
    puVar7 = *ppuVar1;
  }
  else {
    if ((param_3 != '\x03') || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x269bcu + (uint32_t)((short)param_2 * 0xf) * 1u)))) == 0)) goto LAB_000974a2;
    ppuVar1 = &PTR_DAT_000265f8 + uVar5;
    iVar4 = (short)(ushort)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x269bcu + (uint32_t)((short)param_2 * 0xf) * 1u)))) * 6;
    cVar2 = (*ppuVar1)[iVar4 + -5];
    puVar6 = *ppuVar1;
    puVar7 = *ppuVar1;
  }
  if (cVar2 == '\a') {
    uVar5 = (uint)*(ushort *)(puVar7 + iVar4 + -4);
  }
  else {
    uVar5 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x261d8u + (uint32_t)((byte)puVar7[iVar4 + -5]) * 1u))));
  }
  uVar3 = uVar5 + *(ushort *)(puVar6 + iVar4 + -2) + 7 >> 3;
LAB_000974a2:
  return (*((uint *)camry_host_ptr((uint32_t)(param_1 + 0x14)))) < uVar3 + 3;
}

void unpack_routine_arguments_and_zero_response_payload_974b0(int *param_1,ushort param_2,char param_3,int param_4)

{
  uint8_t *puVar1;
  char *pcVar2;
  ushort uVar3;
  uint uVar4;
  undefined *puVar5;
  uint32_t puVar6;
  uint uVar7;
  char cVar8;
  undefined *puVar9;
  ushort uVar10;
  byte bVar11;
  uint uVar12;
  uint uVar13;
  int iVar14;
  
  uVar4 = (uint)param_2;
  if (uVar4 < DAT_00026492) {
    iVar14 = (short)param_2 * 0xf;
    if (param_3 == '\x01') {
      puVar5 = ((void *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x26738u + (uint32_t)(uVar4) * 4u)))))));
      uVar7 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x269bfu + (uint32_t)(iVar14) * 1u))));
      puVar6 = (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x26698u + (uint32_t)(uVar4) * 4u))));
      uVar10 = (ushort)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x269c1u + (uint32_t)(iVar14) * 1u))));
      puVar9 = ((void *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x266e8u + (uint32_t)(uVar4) * 4u)))))));
    }
    else if (param_3 == '\x02') {
      puVar5 = ((void *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x26878u + (uint32_t)(uVar4) * 4u)))))));
      uVar7 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x269c4u + (uint32_t)(iVar14) * 1u))));
      puVar6 = (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x267d8u + (uint32_t)(uVar4) * 4u))));
      uVar10 = (ushort)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x269c6u + (uint32_t)(iVar14) * 1u))));
      puVar9 = ((void *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x26828u + (uint32_t)(uVar4) * 4u)))))));
    }
    else {
      uVar10 = (ushort)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x269bcu + (uint32_t)(iVar14) * 1u))));
      puVar9 = ((void *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x265f8u + (uint32_t)(uVar4) * 4u)))))));
      uVar7 = 0;
      puVar6 = (0x0);
      puVar5 = (undefined *)0x0;
    }
    for (uVar4 = 0; uVar4 < uVar7; uVar4 = uVar4 + 1 & 0xff) {
      pcVar2 = ((void *)camry_host_ptr((uint32_t)(puVar6 + (short)uVar4 * 6)));
      iVar14 = ((int)(uint)*(ushort *)(pcVar2 + 4) >> 3) + 3;
      if (pcVar2[1] == '\a') {
        uVar3 = *(ushort *)(pcVar2 + 2);
        (*((int *)camry_host_ptr((uint32_t)(param_4 + 0x10)))) = *param_1 + iVar14;
        (*((short *)camry_host_ptr((uint32_t)(param_4 + 0x18)))) = (short)(uVar3 + 7 >> 3);
      }
      else {
        if (pcVar2[1] == '\0') {
          bVar11 = (*((byte *)camry_host_ptr((uint32_t)(param_4 + 0x1a))));
          (*((uint *)camry_host_ptr((uint32_t)((uint)bVar11 * 4 + param_4)))) =
               (int)(uint)(*((byte *)camry_host_ptr((uint32_t)(*param_1 + iVar14)))) >> (*(ushort *)(pcVar2 + 4) & 7) & 0xff;
        }
        else {
          if ((pcVar2[1] == '\x06') || (pcVar2[1] == '\x03')) {
            bVar11 = (*((byte *)camry_host_ptr((uint32_t)(param_4 + 0x1a))));
            uVar13 = (uint)(*((byte *)camry_host_ptr((uint32_t)(*param_1 + iVar14))));
          }
          else {
            if ((puVar5[uVar4 * 2] == '\0') || (*pcVar2 == '\x02')) {
              cVar8 = '\x01';
            }
            else {
              cVar8 = *pcVar2;
            }
            if ((pcVar2[1] == '\x04') || (pcVar2[1] == '\x01')) {
              uVar12 = (uint)(((byte *)camry_host_ptr((uint32_t)(*param_1 + iVar14))))[1];
              uVar13 = (uint)(*((byte *)camry_host_ptr((uint32_t)(*param_1 + iVar14))));
              if (cVar8 == '\x01') {
                uVar12 = uVar12 << 8;
              }
              else {
                uVar13 = uVar13 << 8;
              }
            }
            else {
              puVar1 = ((uint8_t *)camry_host_ptr((uint32_t)(*param_1 + iVar14)));
              if (cVar8 == '\x01') {
                uVar13 = (uint)((uint32_t)puVar1[0] | ((uint32_t)puVar1[1] << 8) | ((uint32_t)puVar1[2] << 16));
                uVar12 = (uint)(*((byte *)camry_host_ptr((uint32_t)((int)puVar1 + 3)))) << 0x18;
              }
              else {
                uVar13 = (uint)(*((byte *)camry_host_ptr((uint32_t)((int)puVar1 + 3))));
                uVar12 = (uint)(*((byte *)camry_host_ptr((uint32_t)((int)puVar1 + 2)))) << 8 |
                         (uint)(*((byte *)camry_host_ptr((uint32_t)((int)puVar1 + 1)))) << 0x10 | (uint)puVar1[0] << 0x18;
              }
            }
            uVar13 = uVar13 | uVar12;
            bVar11 = (*((byte *)camry_host_ptr((uint32_t)(param_4 + 0x1a))));
          }
          (*((uint *)camry_host_ptr((uint32_t)((uint)bVar11 * 4 + param_4)))) = uVar13;
        }
        (*((byte *)camry_host_ptr((uint32_t)(param_4 + 0x1a)))) = bVar11 + 1;
      }
    }
    for (uVar3 = 0; uVar3 < uVar10; uVar3 = uVar3 + 1 & 0xff) {
      if (puVar9[(short)uVar3 * 6 + 1] == '\a') {
        (*((int *)camry_host_ptr((uint32_t)(param_4 + 0x14)))) =
             param_1[2] + ((int)(uint)*(ushort *)(puVar9 + (short)uVar3 * 6 + 4) >> 3) + 3;
      }
      else {
        (*((char *)camry_host_ptr((uint32_t)(param_4 + 0x1b)))) = (*((char *)camry_host_ptr((uint32_t)(param_4 + 0x1b)))) + '\x01';
      }
    }
    if (uVar10 != 0) {
      if (puVar9[(short)uVar10 * 6 + -5] == '\a') {
        uVar4 = (uint)*(ushort *)(puVar9 + (short)uVar10 * 6 + -4);
      }
      else {
        uVar4 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x261d8u + (uint32_t)((byte)puVar9[(short)uVar10 * 6 + -5]) * 1u))));
      }
      uVar10 = *(ushort *)(puVar9 + (short)uVar10 * 6 + -2);
      for (uVar7 = 0; uVar7 < uVar10 + uVar4 + 7 >> 3; uVar7 = uVar7 + 1 & 0xffff) {
        (*((undefined1 *)camry_host_ptr((uint32_t)(param_1[2] + uVar7 + 3)))) = 0;
      }
    }
  }
  return;
}

void pack_routine_scalar_response_and_advance_length_9767c(ushort param_1,char param_2,int param_3)

{
  char *pcVar1;
  undefined2 uVar2;
  undefined **ppuVar3;
  uint uVar4;
  undefined *puVar5;
  undefined *puVar6;
  char cVar7;
  short sVar8;
  uint uVar9;
  undefined1 uVar10;
  uint uVar11;
  undefined1 uVar12;
  undefined **ppuVar13;
  int iVar14;
  
  uVar4 = (uint)param_1;
  if (uVar4 < DAT_00026492) {
    iVar14 = (short)param_1 * 0xf;
    if (param_2 == '\x01') {
      uVar9 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x269c1u + (uint32_t)(iVar14) * 1u))));
      ppuVar3 = &PTR_DAT_000266e8;
      ppuVar13 = &PTR_DAT_00026788;
    }
    else if (param_2 == '\x02') {
      uVar9 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x269c6u + (uint32_t)(iVar14) * 1u))));
      ppuVar3 = &PTR_DAT_00026828;
      ppuVar13 = &PTR_DAT_000268c8;
    }
    else {
      uVar9 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x269bcu + (uint32_t)(iVar14) * 1u))));
      ppuVar3 = &PTR_DAT_000265f8;
      ppuVar13 = &PTR_DAT_00026648;
    }
    puVar6 = ((undefined *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)((uint8_t *)ppuVar3 + (uint32_t)(uVar4) * 4u))))));
    puVar5 = ((undefined *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)((uint8_t *)ppuVar13 + (uint32_t)(uVar4) * 4u))))));
    for (uVar4 = 0; uVar4 < uVar9; uVar4 = uVar4 + 1 & 0xff) {
      pcVar1 = puVar6 + (short)uVar4 * 6;
      iVar14 = ((int)(uint)*(ushort *)(pcVar1 + 4) >> 3) + 3;
      if (pcVar1[1] != '\a') {
        if (pcVar1[1] == '\0') {
          (*((byte *)camry_host_ptr((uint32_t)(DAT_febe5e20 + iVar14)))) =
               (*((byte *)camry_host_ptr((uint32_t)(DAT_febe5e20 + iVar14)))) |
               (byte)((*((int *)camry_host_ptr((uint32_t)(uVar4 * 4 + param_3)))) << (*(ushort *)(pcVar1 + 4) & 7));
        }
        else if ((pcVar1[1] == '\x06') || (pcVar1[1] == '\x03')) {
          (*((char *)camry_host_ptr((uint32_t)(DAT_febe5e20 + iVar14)))) = (char)(*((undefined4 *)camry_host_ptr((uint32_t)(uVar4 * 4 + param_3))));
        }
        else {
          if ((puVar5[uVar4 * 2] == '\0') || (*pcVar1 == '\x02')) {
            cVar7 = '\x01';
          }
          else {
            cVar7 = *pcVar1;
          }
          if ((pcVar1[1] == '\x04') || (pcVar1[1] == '\x01')) {
            uVar2 = (*((undefined2 *)camry_host_ptr((uint32_t)(uVar4 * 4 + param_3))));
            uVar12 = (undefined1)((ushort)uVar2 >> 8);
            uVar10 = (undefined1)uVar2;
            if (cVar7 == '\x01') {
              (*((undefined1 *)camry_host_ptr((uint32_t)(DAT_febe5e20 + iVar14)))) = uVar10;
              (*((undefined1 *)camry_host_ptr((uint32_t)(DAT_febe5e20 + iVar14 + 1)))) = uVar12;
            }
            else {
              (*((undefined1 *)camry_host_ptr((uint32_t)(DAT_febe5e20 + iVar14)))) = uVar12;
              (*((undefined1 *)camry_host_ptr((uint32_t)(DAT_febe5e20 + iVar14 + 1)))) = uVar10;
            }
          }
          else {
            uVar11 = (*((uint *)camry_host_ptr((uint32_t)(uVar4 * 4 + param_3))));
            uVar10 = (undefined1)(uVar11 >> 0x10);
            uVar12 = (undefined1)(uVar11 >> 8);
            if (cVar7 == '\x01') {
              (*((undefined1 *)camry_host_ptr((uint32_t)(DAT_febe5e20 + iVar14)))) = (char)uVar11;
              uVar11 = uVar11 >> 0x18;
              (*((undefined1 *)camry_host_ptr((uint32_t)(DAT_febe5e20 + iVar14 + 1)))) = uVar12;
              (*((undefined1 *)camry_host_ptr((uint32_t)(DAT_febe5e20 + iVar14 + 2)))) = uVar10;
            }
            else {
              (*((undefined1 *)camry_host_ptr((uint32_t)(DAT_febe5e20 + iVar14)))) = (char)(uVar11 >> 0x18);
              (*((undefined1 *)camry_host_ptr((uint32_t)(DAT_febe5e20 + iVar14 + 1)))) = uVar10;
              (*((undefined1 *)camry_host_ptr((uint32_t)(DAT_febe5e20 + iVar14 + 2)))) = uVar12;
            }
            (*((char *)camry_host_ptr((uint32_t)(DAT_febe5e20 + iVar14 + 3)))) = (char)uVar11;
          }
        }
      }
    }
    if (uVar9 != 0) {
      sVar8 = (short)uVar9;
      if (puVar6[sVar8 * 6 + -5] == '\a') {
        uVar4 = (uint)*(ushort *)(puVar6 + sVar8 * 6 + -4);
      }
      else {
        uVar4 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x261d8u + (uint32_t)((byte)puVar6[sVar8 * 6 + -5]) * 1u))));
      }
      DAT_febe5e24 = DAT_febe5e24 + (uVar4 + *(ushort *)(puVar6 + sVar8 * 6 + -2) + 7 >> 3);
    }
  }
  return;
}

undefined4 execute_routine_callback_and_report_result_97822(char param_1,undefined4 param_2,ushort param_3,char param_4)

{
  uint8_t stack_record_31[49];
  uint uVar1;
  uint uVar2;
  uint32_t puVar3;
  int iVar4;
  undefined4 uVar5;
  undefined4 auStack_30 [4];
  
  puVar3 = 0xfebeb800u;
  uVar5 = 0;
  if (param_3 < DAT_00026492) {
    stack_record_31[0] = '\0';
    uVar2 = 0;
    do {
      uVar1 = uVar2 + 1;
      auStack_30[uVar2] = 0;
      uVar2 = uVar1;
    } while (uVar1 < 4);
    stack_record_31[27] = 0;
    stack_record_31[28] = 0;
    (*((uint32_t *)(stack_record_31 + 17))) = 0;
    (*((uint32_t *)(stack_record_31 + 21))) = 0;
    (*((uint16_t *)(stack_record_31 + 25))) = 0;
    if (param_1 != '\x02') {
      puVar3 = 0xfebeb800u;
      unpack_routine_arguments_and_zero_response_payload_974b0(((int *)camry_host_ptr((uint32_t)(param_2))), param_3, param_4, camry_host_addr(auStack_30));
    }
    if (param_4 == '\x01') {
      iVar4 = dispatch_routine_start_callbacks_by_row_9847a((uint)(ushort)param_3,  auStack_30,  (uint)(byte)param_1, camry_host_addr(stack_record_31));
    }
    else if (param_4 == '\x02') {
      iVar4 = dispatch_routine_stop_callbacks_rows_f_and_12_98590((uint)(ushort)param_3, camry_host_addr(auStack_30),  (uint)(byte)param_1, camry_host_addr(stack_record_31));
    }
    else {
      iVar4 = dispatch_routine_result_callbacks_by_row_982e4(param_3, auStack_30, param_1, camry_host_addr(stack_record_31));
    }
    if (param_1 != '\x02') {
      if (iVar4 == 0) {
        set_diagnostic_callback_pending_955b6(0);
        pack_routine_scalar_response_and_advance_length_9767c(param_3, param_4, camry_host_addr(auStack_30 + stack_record_31[27]));
        dcm_report_positive_response(((F33DcmMessageContext *)camry_host_ptr((uint32_t)(puVar3 + -0x59e8))));
      }
      else if (iVar4 == 1) {
        set_diagnostic_callback_pending_955b6(0);
        dcm_report_negative_or_pending(((F33DcmMessageContext *)camry_host_ptr((uint32_t)(puVar3 + -0x59e8))),stack_record_31[0]);
      }
      else if (iVar4 == 10) {
        set_diagnostic_callback_pending_955b6(1);
        dcm_enqueue_event('\x06');
        uVar5 = 10;
      }
      else if (iVar4 == 0xc) {
        set_diagnostic_callback_pending_955b6(1);
        dcm_report_negative_or_pending(((F33DcmMessageContext *)camry_host_ptr((uint32_t)(puVar3 + -0x59e8))),'x');
        uVar5 = 0xc;
      }
      else {
        set_diagnostic_callback_pending_955b6(0);
      }
    }
  }
  return uVar5;
}

undefined4 validate_routine_buffers_build_header_and_execute_97912(undefined4 param_1,undefined1 *param_2,undefined1 *param_3)

{
  uint32_t puVar1;
  uint32_t puVar2;
  undefined4 extraout_r6;
  int iVar3;
  undefined4 uVar4;
  uint uVar5;
  
  puVar1 = 0xfebeb800u;
  puVar2 = 0x23dfcu;
  *param_3 = 0;
  uVar4 = 0;
  *param_2 = 0;
  uVar5 = (uint)DAT_febe5e14;
  if (uVar5 < DAT_00026492) {
    iVar3 = reject_routine_request_length_mismatch_9733a(param_1,uVar5,DAT_febe5e16);
    if (iVar3 == 0) {
      iVar3 = reject_routine_response_capacity_shortage_973dc(param_1,uVar5,(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x59ea))))));
      if (iVar3 == 0) {
        (*((volatile undefined1 *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)((puVar1 + -0x59e0))))))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x59ea)))));
        (*((char *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)(puVar1 + -0x59e0)))) + 1)))) =
             (char)((ushort)(*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + uVar5 * 8 + 0x2b1c)))) >> 8);
        (*((char *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)(puVar1 + -0x59e0)))) + 2)))) =
             (char)(*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + uVar5 * 8 + 0x2b1c))));
        (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x59dc)))) = 3;
        uVar4 = execute_routine_callback_and_report_result_97822(0,((undefined4)(param_1)),uVar5,(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x59ea))))));
      }
    }
    else {
      *param_3 = 1;
      *param_2 = 0x13;
    }
  }
  return uVar4;
}

undefined4 begin_routine_control_request_979a2(undefined4 *param_1)

{
  uint8_t stack_record_14[20];
  byte bVar1;
  undefined4 *puVar2;
  uint32_t puVar3;
  int iVar4;
  uint uVar5;
  undefined4 uVar6;
  undefined4 uVar7;
  undefined4 *puVar8;
  byte *pbVar9;
  
  puVar3 = 0xfebeb800u;
  (*((uint16_t *)(stack_record_14 + 2))) = 0;
  stack_record_14[1] = '\0';
  uVar7 = 0;
  stack_record_14[0] = '\0';
  set_diagnostic_busy_marker_from_done_flag_9560e(0);
  puVar2 = ((undefined4 *)camry_host_ptr((uint32_t)(puVar3 + -0x59e8)));
  puVar8 = param_1;
  do {
    uVar6 = *puVar8;
    puVar8 = puVar8 + 1;
    *puVar2 = uVar6;
    puVar2 = puVar2 + 1;
  } while (camry_host_addr(param_1 + 7)!=camry_host_addr(puVar8));
  set_diagnostic_callback_pending_955b6(0);
  if ((uint)param_1[1] < 3) {
    stack_record_14[1] = '\x13';
  }
  else {
    pbVar9 = ((byte *)camry_host_ptr((uint32_t)(*param_1)));
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-22999))))) = *pbVar9 >> 7;
    iVar4 = find_enabled_routine_id_row_97172(CONCAT11(pbVar9[1],pbVar9[2]),(stack_record_14 + 2));
    if ((iVar4 == 0) && (iVar4 = check_routine_session_allowlist_971e8((*((uint16_t *)(stack_record_14 + 2)))), iVar4 == 0)) {
      iVar4 = check_routine_security_allowlist_9726c((*((uint16_t *)(stack_record_14 + 2))));
      if (iVar4 == 0) {
        bVar1 = (*((byte *)camry_host_ptr((uint32_t)(*param_1))));
        uVar5 = diag_routine_control_type_supported((*((uint16_t *)(stack_record_14 + 2))),bVar1 & 0x7f);
        if (uVar5 == 0) {
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x59ea))))) = bVar1 & 0x7f;
          (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x59ec)))) = (*((uint16_t *)(stack_record_14 + 2)));
          uVar7 = validate_routine_buffers_build_header_and_execute_97912(camry_host_addr(param_1), (stack_record_14 + 1), stack_record_14);
          goto LAB_00097a7a;
        }
        stack_record_14[1] = '\x12';
      }
      else {
        stack_record_14[1] = '3';
      }
    }
    else {
      stack_record_14[1] = '1';
    }
  }
  stack_record_14[0] = '\x01';
LAB_00097a7a:
  if (stack_record_14[0] != '\0') {
    dcm_report_negative_or_pending(((F33DcmMessageContext *)camry_host_ptr((uint32_t)(puVar3 + -0x59e8))),stack_record_14[1]);
  }
  return uVar7;
}

void cancel_routine_control_and_clear_event_97a94(void)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  iVar2 = get_diagnostic_callback_pending_955bc();
  if (iVar2 == 1) {
    execute_routine_callback_and_report_result_97822(2, ((uint32_t)((uint32_t)(puVar1 + -0x59e8))),  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x59ec)))),  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x59ea))))));
    set_diagnostic_callback_pending_955b6(0);
  }
  dcm_invalidate_queued_event('\x06','\0');
  set_diagnostic_busy_marker_from_done_flag_9560e(1);
  return;
}

undefined4 continue_routine_control_with_status_three_97aca(void)

{
  return execute_routine_callback_and_report_result_97822(3, (int)((uint32_t)(0xfebe5e18u)), DAT_febe5e14, DAT_febe5e16);
}

undefined4 dispatch_routine_control_operation_status_97ae4(char param_1,undefined4 param_2)

{
  undefined4 uVar1;
  
  if (param_1 == '\0') {
    uVar1 = begin_routine_control_request_979a2(((undefined4 *)camry_host_ptr((uint32_t)(param_2))));
  }
  else {
    uVar1 = 0;
    if (param_1 == '\x02') {
      cancel_routine_control_and_clear_event_97a94();
    }
    else if (param_1 == '\x03') {
      uVar1 = continue_routine_control_with_status_three_97aca();
    }
  }
  return uVar1;
}

undefined4 resume_routine_control_callback_97b12(void)

{
  return execute_routine_callback_and_report_result_97822(1, (int)((uint32_t)(0xfebe5e18u)), DAT_febe5e14, DAT_febe5e16);
}

uint diag_routine_class03_97b2c(byte param_1,uchar *param_2,uchar *param_3)

{
  uint uVar1;
  ushort uStack_a;
  
  uStack_a = 0;
  if (param_1 < 2) {
    uVar1 = diag_routine_application_class('\x03',0,0,param_2,&uStack_a,param_3);
  }
  else {
    uVar1 = 0;
    reset_routine_class_state_wrapper_a_8b83c();
  }
  return uVar1;
}

uint diag_routine_class03_97b60(byte param_1,uchar *param_2,uchar *param_3)

{
  uint uVar1;
  ushort uStack_a;
  
  uStack_a = 0;
  if (param_1 < 2) {
    uVar1 = diag_routine_application_class('\x03',1,0,param_2,&uStack_a,param_3);
  }
  else {
    uVar1 = 0;
    reset_routine_class_state_wrapper_a_8b83c();
  }
  return uVar1;
}

uint diag_routine_class03_97b94(byte param_1,uchar *param_2,uchar *param_3)

{
  uint uVar1;
  ushort uStack_a;
  
  uStack_a = 0;
  if (param_1 < 2) {
    uVar1 = diag_routine_application_class('\x03',2,0,param_2,&uStack_a,param_3);
  }
  else {
    uVar1 = 0;
    reset_routine_class_state_wrapper_a_8b83c();
  }
  return uVar1;
}

uint diag_routine_class03_97bc8(byte param_1,uchar *param_2,uchar *param_3)

{
  uint uVar1;
  ushort uStack_a;
  
  uStack_a = 0;
  if (param_1 < 2) {
    uVar1 = diag_routine_application_class('\x03',3,0,param_2,&uStack_a,param_3);
  }
  else {
    uVar1 = 0;
    reset_routine_class_state_wrapper_a_8b83c();
  }
  return uVar1;
}

uint diag_routine_class03_97bfc(byte param_1,uchar *param_2,uchar *param_3)

{
  uint uVar1;
  ushort uStack_a;
  
  uStack_a = 0;
  if (param_1 < 2) {
    uVar1 = diag_routine_application_class('\x03',4,0,param_2,&uStack_a,param_3);
  }
  else {
    uVar1 = 0;
    reset_routine_class_state_wrapper_a_8b83c();
  }
  return uVar1;
}

uint diag_routine_class03_97c30(byte param_1,uchar *param_2,uchar *param_3)

{
  uint uVar1;
  ushort uStack_a;
  
  uStack_a = 0;
  if (param_1 < 2) {
    uVar1 = diag_routine_application_class('\x03',5,0,param_2,&uStack_a,param_3);
  }
  else {
    uVar1 = 0;
    reset_routine_class_state_wrapper_a_8b83c();
  }
  return uVar1;
}

uint diag_routine_class03_97c64(byte param_1,uchar *param_2,uchar *param_3)

{
  uint uVar1;
  ushort uStack_a;
  
  uStack_a = 0;
  if (param_1 < 2) {
    uVar1 = diag_routine_application_class('\x03',6,0,param_2,&uStack_a,param_3);
  }
  else {
    uVar1 = 0;
    reset_routine_class_state_wrapper_a_8b83c();
  }
  return uVar1;
}

undefined4 request_routine_payload_service31_or_reset_97c98(char param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  
  if (param_1 == '\0') {
    uVar1 = run_direct_read_sequence_and_map_nrc_8ba2c(param_2, 0x31, ((uchar *)camry_host_ptr((uint32_t)(param_4))));
  }
  else {
    uVar1 = 0;
    reset_routine_class_state_wrapper_a_8b83c();
  }
  return uVar1;
}

uint diag_routine_class03_97cbc(byte param_1,uchar *param_2,uchar *param_3)

{
  uint uVar1;
  ushort uStack_a;
  
  uStack_a = 0;
  if (param_1 < 2) {
    uVar1 = diag_routine_application_class('\x03',10,0,param_2,&uStack_a,param_3);
  }
  else {
    uVar1 = 0;
    reset_routine_class_state_wrapper_a_8b83c();
  }
  return uVar1;
}

uint diag_routine_class03_97cf0(byte param_1,uchar *param_2,uchar *param_3)

{
  uint uVar1;
  ushort uStack_a;
  
  uStack_a = 0;
  if (param_1 < 2) {
    uVar1 = diag_routine_application_class('\x03',0xb,0,param_2,&uStack_a,param_3);
  }
  else {
    uVar1 = 0;
    reset_routine_class_state_wrapper_a_8b83c();
  }
  return uVar1;
}

uint diag_routine_class03_97d24(byte param_1,uchar *param_2,uchar *param_3)

{
  uint uVar1;
  ushort uStack_a;
  
  uStack_a = 0;
  if (param_1 < 2) {
    uVar1 = diag_routine_application_class('\x03',0xc,0,param_2,&uStack_a,param_3);
  }
  else {
    uVar1 = 0;
    reset_routine_class_state_wrapper_a_8b83c();
  }
  return uVar1;
}

uint diag_routine_class03_97d58(byte param_1,uchar *param_2,uchar *param_3)

{
  uint uVar1;
  ushort uStack_a;
  
  uStack_a = 0;
  if (param_1 < 2) {
    uVar1 = diag_routine_application_class('\x03',0xd,0,param_2,&uStack_a,param_3);
  }
  else {
    uVar1 = 0;
    reset_routine_class_state_wrapper_a_8b83c();
  }
  return uVar1;
}

uint diag_routine_class03_97d8c(byte param_1,uchar *param_2,uchar *param_3)

{
  uint uVar1;
  ushort uStack_a;
  
  uStack_a = 0;
  if (param_1 < 2) {
    uVar1 = diag_routine_application_class('\x03',0xe,0,param_2,&uStack_a,param_3);
  }
  else {
    uVar1 = 0;
    reset_routine_class_state_wrapper_a_8b83c();
  }
  return uVar1;
}

uint diag_routine_class03_97dc0(byte param_1,uchar *param_2,uchar *param_3)

{
  uint uVar1;
  ushort uStack_a;
  
  uStack_a = 0;
  if (param_1 < 2) {
    uVar1 = diag_routine_application_class('\x03',0xf,0,param_2,&uStack_a,param_3);
  }
  else {
    uVar1 = 0;
    reset_routine_class_state_wrapper_a_8b83c();
  }
  return uVar1;
}

uint diag_routine_class03_97df4(byte param_1,uchar *param_2,uchar *param_3)

{
  uint uVar1;
  ushort uStack_a;
  
  uStack_a = 0;
  if (param_1 < 2) {
    uVar1 = diag_routine_application_class('\x03',0x10,0,param_2,&uStack_a,param_3);
  }
  else {
    uVar1 = 0;
    reset_routine_class_state_wrapper_a_8b83c();
  }
  return uVar1;
}

uint diag_routine_class03_97e2a(byte param_1,uchar *param_2,uchar *param_3)

{
  uint uVar1;
  ushort uStack_a;
  
  uStack_a = 0;
  if (param_1 < 2) {
    uVar1 = diag_routine_application_class('\x03',0x11,0,param_2,&uStack_a,param_3);
  }
  else {
    uVar1 = 0;
    reset_routine_class_state_wrapper_a_8b83c();
  }
  return uVar1;
}

uint diag_routine_class03_97e60(byte param_1,uchar *param_2,uchar *param_3)

{
  uint uVar1;
  ushort uStack_a;
  
  uStack_a = 0;
  if (param_1 < 2) {
    uVar1 = diag_routine_application_class('\x03',0x12,0,param_2,&uStack_a,param_3);
  }
  else {
    uVar1 = 0;
    reset_routine_class_state_wrapper_a_8b83c();
  }
  return uVar1;
}

uint diag_routine_class01_97e96(byte param_1,uchar *param_2,ushort *param_3,uchar *param_4)

{
  uint uVar1;
  
  if (param_1 < 2) {
    uVar1 = diag_routine_application_class('\x01',0,0,param_2,param_3,param_4);
  }
  else {
    uVar1 = 0;
    reset_routine_class_state_wrapper_a_8b83c();
  }
  return uVar1;
}

uint diag_routine_class01_97ec2(byte param_1,uchar *param_2,ushort *param_3,uchar *param_4)

{
  uint uVar1;
  
  if (param_1 < 2) {
    uVar1 = diag_routine_application_class('\x01',1,0,param_2,param_3,param_4);
  }
  else {
    uVar1 = 0;
    reset_routine_class_state_wrapper_a_8b83c();
  }
  return uVar1;
}

uint diag_routine_class01_97eee(byte param_1,uchar *param_2)

{
  uint8_t stack_record_b[12];
  uint uVar1;
  
  stack_record_b[0] = '\0';
  (*((uint16_t *)(stack_record_b + 1))) = 0;
  if (param_1 < 2) {
    uVar1 = diag_routine_application_class('\x01',2,0,((uint8_t *)(stack_record_b)),((uint16_t *)((stack_record_b + 1))),param_2);
  }
  else {
    uVar1 = 0;
    reset_routine_class_state_wrapper_a_8b83c();
  }
  return uVar1;
}

uint invoke_routine_class_one_index_three_97f24(uint param_1,byte param_2,uchar *param_3)

{
  uint8_t stack_record_b[11];
  uint uVar1;
  
  stack_record_b[0] = '\0';
  (*((uint16_t *)(stack_record_b + 1))) = 0;
  if (param_2 < 2) {
    uVar1 = diag_routine_application_class
                      ('\x01',3,param_1 & 0xffff,((uint8_t *)(stack_record_b)),((uint16_t *)((stack_record_b + 1))),param_3);
  }
  else {
    uVar1 = 0;
    reset_routine_class_state_wrapper_a_8b83c();
  }
  return uVar1;
}

uint diag_routine_class01_97f5c(byte param_1,uchar *param_2)

{
  uint8_t stack_record_b[12];
  uint uVar1;
  
  stack_record_b[0] = '\0';
  (*((uint16_t *)(stack_record_b + 1))) = 0;
  if (param_1 < 2) {
    uVar1 = diag_routine_application_class('\x01',4,0,((uint8_t *)(stack_record_b)),((uint16_t *)((stack_record_b + 1))),param_2);
  }
  else {
    uVar1 = 0;
    reset_routine_class_state_wrapper_a_8b83c();
  }
  return uVar1;
}

uint diag_routine_class01_97f92(byte param_1,uchar *param_2)

{
  uint8_t stack_record_b[12];
  uint uVar1;
  
  stack_record_b[0] = '\0';
  (*((uint16_t *)(stack_record_b + 1))) = 0;
  if (param_1 < 2) {
    uVar1 = diag_routine_application_class('\x01',5,0,((uint8_t *)(stack_record_b)),((uint16_t *)((stack_record_b + 1))),param_2);
  }
  else {
    uVar1 = 0;
    reset_routine_class_state_wrapper_a_8b83c();
  }
  return uVar1;
}

uint diag_routine_class01_97fc8(byte param_1,uchar *param_2)

{
  uint8_t stack_record_b[12];
  uint uVar1;
  
  stack_record_b[0] = '\0';
  (*((uint16_t *)(stack_record_b + 1))) = 0;
  if (param_1 < 2) {
    uVar1 = diag_routine_application_class('\x01',6,0,((uint8_t *)(stack_record_b)),((uint16_t *)((stack_record_b + 1))),param_2);
  }
  else {
    uVar1 = 0;
    reset_routine_class_state_wrapper_a_8b83c();
  }
  return uVar1;
}

uint diag_routine_class01_97ffe(byte param_1,uchar *param_2)

{
  uint8_t stack_record_b[12];
  uint uVar1;
  
  stack_record_b[0] = '\0';
  (*((uint16_t *)(stack_record_b + 1))) = 0;
  if (param_1 < 2) {
    uVar1 = diag_routine_application_class('\x01',7,0,((uint8_t *)(stack_record_b)),((uint16_t *)((stack_record_b + 1))),param_2);
  }
  else {
    uVar1 = 0;
    reset_routine_class_state_wrapper_a_8b83c();
  }
  return uVar1;
}
