#include "common.h"

void application_transfer_to_boot_context(uint *handoff_record)

{
  undefined4 uVar1;
  undefined2 uVar2;
  uint in_FPEC = camry_SR[0][11];
  
  __disable_irq();
  PMR = 0xffff;
  if ((in_FPEC & 1) != 0) {
    uVar1 = PMR;
  }
  __synchronize();
  Ramfffee982 = 0;
  Ramfffee988 = 0;
  Ramfffee980 = 0;
  uVar2 = Ramfffee980;
  __synchronize();
  __synchronize();
  if ((in_FPEC & 1) != 0) {
    uVar1 = PMR;
  }
  __synchronize();
  camry_SR[1][3] = 1;
  __synchronize();
  __synchronize();
  __synchronize();
  __synchronize();
  camry_psw = 0x18020u;
  camry_SR[1][4] = 0;
  camry_sp = camry_gpr[3] = 0xfebe8000u;
  camry_gp = camry_gpr[4] = 0xfebf9800u;
  camry_tp = camry_gpr[5] = 0x869cu;
  camry_SR[5][0] = 0;
  camry_gpr[31] = 0x9f62u;
  boot_resident_enter_with_record(handoff_record);
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}
