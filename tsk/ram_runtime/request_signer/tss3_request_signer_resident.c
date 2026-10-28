/*
 * Shared TSS3 foreground resident (C).
 *
 * The staging shell writes one machine-resolved runtime config from active
 * CodeFlash. This resident walks the stock startup and foreground schedules
 * recovered from those machine roles. It services pending
 * private-ring records after checking an idle window, with the outer
 * end-of-tick helper call retained as the fallback.
 *
 * tss3_request_signer_resident.S keeps only the architectural entry stub: it
 * installs the application CPU context before any compiled prologue or stack
 * access, then enters resident_startup. Section contract with the builder's
 * linker script: .text.entry (stub) first, then .text.startup (this one-shot
 * startup walker, dead once the state prefix reclaims the first 0x24 bytes at
 * the resident base), then .text (the live loop).
 */
#include "tss3_request_signer.h"

/* Resident private-state markers shared with build_tss3_request_signer.py. */
#define STATE_MAGIC 0x4C433841u /* little-endian "A8CL" */
#define STATE_VERSION 3u

/* Stock foreground tick flag bit; its OS address is firmware-resolved. */
#define TICK_FLAG_BIT 4

/* Shared TAUJ0 channel-3 interval counter: pending private-ring records are
 * serviced only while more than 3 ms of the stock interval remains. */
#define TAUJ0CNT3_ADDRESS 0xFFE5001Cu
#define TAUJ0_IDLE_MINIMUM_COUNTS 240000u

/* Only the GlobalRAM helper is far; other calls keep their ordinary encoding. */
extern void helper_entry(void) __attribute__((long_call));

__attribute__((noreturn, noinline)) void resident_forever(void);


_Static_assert(sizeof(SignerState) % sizeof(uint32_t) == 0,
               "state clear walks whole words");

/* One-shot stock startup, entered by the assembly stub after the application
 * CPU context is installed. Dead after it hands control to the live loop, so
 * the reclaimed state prefix can never overlap a live return destination. */
__attribute__((section(".text.startup"), noreturn))
void resident_startup(void)
{
    const SignerConfig *config = SIGNER_CONFIG;

    /* Execute the exact contiguous startup JARL span. Sites may be 2 mod 4,
     * so decode the two halfwords directly rather than using a word load.
     * The low halfword holds the displacement's signed upper six bits; the
     * high halfword holds its unsigned lower 16 bits. */
    for (uintptr_t site = config->startup_first; site != config->startup_after; site += 4) {
        uint32_t low = *(const volatile uint16_t *)site;
        uint32_t high = *(const volatile uint16_t *)(site + 2);
        /* GCC signed right shift sign-extends displacement bit 21. Keep
         * the original startup call's r6 argument: the high halfword. */
        int32_t disp = ((int32_t)((low & 0x3fu) << 26) >> 10) + (int32_t)high;
        ((void (*)(uint32_t))(site + (uint32_t)disp))(high);
    }
    config->startup_final(0);

    /* Initialize private state only after every stock initializer returned,
     * reclaiming the already-executed entry prefix. */
    /* Anchor for the builder's reclaimed-prefix safety check: the clear site
       must live beyond the 0x24-byte state prefix at the resident base. */
    __asm__ volatile(".global _resident_state_clear\n_resident_state_clear:" ::: "memory");
    volatile SignerState *state = config->state_base;
    volatile uint32_t *clear = (volatile uint32_t *)state;
    for (uint32_t i = 0; i < sizeof(*state) / sizeof(*clear); i++) {
        clear[i] = 0;
    }
    state->magic = STATE_MAGIC;
    state->version = STATE_VERSION;
    state->active = 1;
    state->cursor = *config->ring_producer;

    __asm__ volatile("ei" ::: "memory");

    resident_forever();
}

/* Live stock foreground schedule. Alias one compiler-owned poll label from
 * outside the loop: loop duplication must not redefine an assembler symbol. */
__attribute__((noreturn, noinline))
void resident_forever(void)
{
    const SignerConfig *config = SIGNER_CONFIG;
    volatile uint8_t *tick_flag = (volatile uint8_t *)(uintptr_t)(uint32_t)(int32_t)
        config->runtime_geometry.foreground_flag_displacement;
    const volatile uint32_t *idle_timer = (const volatile uint32_t *)TAUJ0CNT3_ADDRESS;
    const uint8_t tick_mask = (uint8_t)(1u << TICK_FLAG_BIT);

    __asm__ goto(
        ".global _resident_tick_wait\n.set _resident_tick_wait, %l[tick_wait]"
        ::: "memory" : tick_wait);

    for (;;) {
tick_wait:
        /* Keep the poll boundary ordered without emitting a named label in
         * an instruction sequence the optimizer may duplicate. */
        __asm__ volatile("" ::: "memory");

        if ((*tick_flag & tick_mask) == 0) {
            /* Service a pending private-ring record immediately when the shared
             * TAUJ0 channel-3 interval has more than 3 ms remaining. The second
             * flag check closes the expiry/reload race. The post-foreground
             * call below remains the fallback after foreground work. Neither
             * entry path bounds the helper's complete drain duration. */
            if (*config->ring_producer != config->state_base->cursor
                && *idle_timer > TAUJ0_IDLE_MINIMUM_COUNTS
                && (*tick_flag & tick_mask) == 0) {
                helper_entry();
            }
            continue;
        }

        /* Atomic tick acknowledge at the firmware-resolved OS byte. */
        __asm__ volatile("clr1 4, 0[%0]" :: "r"(tick_flag) : "cc", "memory");

        const int paired_timing = *config->timing_flag == 0x5A;
        if (paired_timing) {
            config->fg_timing_begin();
        }
        config->fg_pre_0();
        config->fg_pre_1();
        config->fg_pre_2();
        config->fg_pre_3();
        config->fg_aggregate();
        config->fg_post_0();
        config->fg_post_1();
        config->fg_post_2();
        if (paired_timing) {
            config->fg_timing_end();
        }
        *config->tick_counter += 1;

        /* The stock tick is complete: no receive, SecOC, or COM subtask is
         * cloned. */
        helper_entry();
    }
}
