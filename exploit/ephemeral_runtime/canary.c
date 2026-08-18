/*
 * Inert scheduler-ownership canary for Denso RH850/P1M-E 8965B4512000.
 *
 * This performs the same boot -> application context -> startup transition as
 * the bridge runtime, then reproduces the stock top-level foreground scheduler
 * without intercepting SecOC or COM. Its only added side effect is a heartbeat
 * counter at TARGET_CANARY_HEARTBEAT, supplied by the SHA-bound target manifest.
 * A canary build is refused unless that manifest includes an independently
 * verified observation cell for the target image.
 */

typedef void (*fn0_t)(void);
typedef void (*fn1_t)(unsigned int);

#include "target_config.h"

#define STR_INNER(x) #x
#define STR(x) STR_INNER(x)

static void post_context_startup(void) __attribute__((noreturn, noinline));

void __attribute__((noreturn)) exploit(void) {
  __asm__ volatile (
    "mov " STR(TARGET_BOOT_INIT_0) ", r12\n\tjarl [r12], lp\n\t"
    "mov " STR(TARGET_BOOT_INIT_1) ", r12\n\tjarl [r12], lp\n\t"
    "mov " STR(TARGET_BOOT_INIT_2) ", r12\n\tjarl [r12], lp\n\t"
    "mov " STR(TARGET_BOOT_INIT_3) ", r12\n\tjarl [r12], lp\n\t"
    "mov " STR(TARGET_BOOT_VALIDITY_CHECK) ", r12\n\tjarl [r12], lp\n\t"
    "cmp r0, r10\n\tbne 1f\n\t"
    "mov " STR(TARGET_APP_CPU_CONTEXT_INIT) ", r12\n\tjarl [r12], lp\n\t"
    "jr _post_context_startup\n\t"
    "1: br 1b\n\t"
  );
  __builtin_unreachable();
}

static void call0(unsigned int address) __attribute__((noinline));
static void call0(unsigned int address) { ((fn0_t)address)(); }

static void post_context_startup(void) {
  for (unsigned int pc = TARGET_APP_STARTUP_FIRST_JARL; pc < TARGET_APP_STARTUP_AFTER_JARLS; pc += 4u) {
    unsigned int ins = *(volatile unsigned int *)pc;
    int signed_high6 = (int)(ins & 0x3Fu);
    signed_high6 = (signed_high6 ^ 0x20) - 0x20;
    call0(pc + ((unsigned int)(signed_high6 << 16) | (ins >> 16)));
  }
  ((fn1_t)TARGET_APP_STARTUP_FINAL_INIT)(0u);
  __asm__ volatile("ei");

  *(volatile unsigned int *)TARGET_CANARY_HEARTBEAT = 0x45504843u; /* "CHPE" marker */

  for (;;) {
    unsigned int timing = 0u;

    __asm__ volatile("1: tst1 " STR(TARGET_TICK_BIT) ", " STR(TARGET_TICK_DISPLACEMENT) "[r0]\n\tbe 1b\n\tclr1 " STR(TARGET_TICK_BIT) ", " STR(TARGET_TICK_DISPLACEMENT) "[r0]");

    if (*(volatile unsigned char *)TARGET_FOREGROUND_TIMING_FLAG == 0x5Au) {
      call0(TARGET_FG_TIMING_BEGIN);
      timing = 1u;
    }
    call0(TARGET_FG_PRE_0);
    call0(TARGET_FG_PRE_1);
    call0(TARGET_FG_PRE_2);
    call0(TARGET_FG_PRE_3);
    call0(TARGET_FG_AGGREGATE);
    call0(TARGET_FG_POST_0);
    call0(TARGET_FG_POST_1);
    call0(TARGET_FG_POST_2);
    if (timing != 0u) {
      call0(TARGET_FG_TIMING_END);
    }
    (*(volatile unsigned char *)TARGET_FOREGROUND_TICK_COUNTER)++;
    (*(volatile unsigned int *)TARGET_CANARY_HEARTBEAT)++;
  }
}
