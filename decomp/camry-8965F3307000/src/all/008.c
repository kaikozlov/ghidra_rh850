#include "common.h"


/* WARNING: This function may have set the stack pointer */
/* Exact F33 application entry wrapper -> startup coordinator 0x637EE */

void f33_application_entry(void)

{
  undefined4 unaff_retaddr;
  
  DAT_febe1ffc = unaff_retaddr;
  f33_startup_coordinator();
  return;
}


