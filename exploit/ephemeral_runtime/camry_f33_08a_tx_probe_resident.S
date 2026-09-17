/*
 * Exact-F33 high-tail scheduler for the non-actuating EPS-origin 0x08A
 * forwarding discriminator.
 *
 * The authenticated boot-stage payload copies this resident to the proven
 * FEBFF9F0 high tail and parks the experiment helper at FEF07C00.  The resident
 * replays the exact stock application startup/foreground sequence.  It invokes
 * the helper only after the already-qualified foreground-count-224 boundary.
 * Before that point there are no experiment-owned application-memory writes.
 */

    .section .text
    .global _resident_entry
_resident_entry:
    prepare {lp}, 0
    jarl32 app_cpu_context_init, lp
    jarl32 startup_00, lp
    jarl32 startup_01, lp
    jarl32 startup_02, lp
    jarl32 startup_03, lp
    jarl32 startup_04, lp
    jarl32 startup_05, lp
    jarl32 startup_06, lp
    jarl32 startup_07, lp
    jarl32 startup_08, lp
    jarl32 startup_09, lp
    jarl32 startup_10, lp
    jarl32 startup_11, lp
    jarl32 startup_12, lp
    jarl32 startup_13, lp
    jarl32 startup_14, lp
    jarl32 startup_15, lp
    jarl32 startup_16, lp
    jarl32 startup_17, lp
    jarl32 startup_18, lp
    jarl32 startup_19, lp
    jarl32 startup_20, lp
    mov 0, r6
    jarl32 app_startup_final_init, lp
    ei

    prepare {r29,lp}, 0
.L_tick_wait:
    tst1 4, -0x4eef[r0]
    be .L_tick_wait
    clr1 4, -0x4eef[r0]
    movhi 0x3, r0, r1
    ld.bu 0x1910[r1], r1
    mov 0, r29
    addi -0x5a, r1, r0
    bne .L_skip_timing_begin
    jarl32 fg_timing_begin, lp
    movea 0x5a, r0, r29
.L_skip_timing_begin:
    jarl32 fg_pre_0, lp
    jarl32 fg_pre_1, lp
    jarl32 fg_pre_2, lp
    jarl32 fg_pre_3, lp
    jarl32 fg_aggregate, lp
    jarl32 fg_post_0, lp
    jarl32 fg_post_1, lp
    jarl32 fg_post_2, lp
    addi -0x5a, r29, r0
    bne .L_skip_timing_end
    jarl32 fg_timing_end, lp
.L_skip_timing_end:
    movea -0x7e25, gp, ep
    sld.bu 0[ep], r1
    add 1, r1
    sst.b r1, 0[ep]

    /* Experiment helper remains inert until the same 224-tick gate used by the
       qualified F33 runtime work. */
    tst1 7, 0[ep]
    be .L_tick_wait
    tst1 6, 0[ep]
    be .L_tick_wait
    tst1 5, 0[ep]
    be .L_tick_wait
    jarl32 helper_entry, lp
    br .L_tick_wait
