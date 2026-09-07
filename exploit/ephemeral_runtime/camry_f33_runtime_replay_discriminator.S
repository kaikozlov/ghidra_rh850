/*
 * Exact-F33 ABI-preserving application-startup / foreground replay discriminator.
 *
 * Unlike the superseded C resident, all recovered stock calls use JARL disp32.
 * JARL changes only LP, just like the stock disp22 calls; no target address is
 * passed through r6 or another data register.  The startup/foreground register
 * flow is therefore preserved across calls.
 *
 * The foreground loop is stock-equivalent through FEBE39DB count 223. Exact
 * startup calls FUN_000666bc, which calls FUN_00065f8e and initializes FEBE39DB
 * to zero. Counts 224..255 snapshot the canonical D0218 source terms into
 * FEBF0000..FEBF0024. That low pocket is outside the high-tail code carrier and
 * is RWX in both recovered application MPU contexts. No steering, B6, SecOC,
 * command-5, or flash path is touched.
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

    /* Exact FUN_00066062 foreground body, with disp32 calls because the resident
       is >22-bit branch range from CodeFlash. */
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

    /* Preserve a completely write-free instrumentation window through tick 223.
       The stock counter starts at zero in startup_18 -> FUN_00065F8E.  Testing
       bits 7/6/5 directly in the stock counter requires no scratch register or
       application-memory write.  Counts 224..255 enter the snapshot path; after
       u8 wrap, the final coherent sample remains in the mailbox. */
    tst1 7, 0[ep]
    be .L_tick_wait
    tst1 6, 0[ep]
    be .L_tick_wait
    tst1 5, 0[ep]
    be .L_tick_wait

    /* First added application-memory write is the r2 save below, at tick 224.
       Snapshot only with r1 plus saved/restored r2; all live register state is
       restored before the next stock call. */
    addi -4, sp, sp
    st.w r2, 0[sp]
    movhi 0x5250, r0, r2
    movea 0x4c59, r2, r2
    st.w r2, 0x4800[gp]

    /* Layout at FEBF0000:
       +00 magic 0x52504C59
       +04 generation-start (stock FEBE39DB)
       +05 AC2B, +06 C7BF, +07 reserved
       +08 C43C, +0A C3BA, +0C CB38, +0E C5EE, +10 CBE8
       +12 reserved2
       +14 C4C0, +18 CC2C, +1C BF3C, +20 CC48
       +24 generation-end. */
    sld.bu 0[ep], r1
    st.b r1, 0x4804[gp]
    ld.bu -0x0bd5[gp], r1
    st.b r1, 0x4805[gp]
    ld.bu 0x0fbf[gp], r1
    st.b r1, 0x4806[gp]
    ld.h 0x0c3c[gp], r1
    st.h r1, 0x4808[gp]
    ld.h 0x0bba[gp], r1
    st.h r1, 0x480a[gp]
    ld.h 0x1338[gp], r1
    st.h r1, 0x480c[gp]
    ld.h 0x0dee[gp], r1
    st.h r1, 0x480e[gp]
    ld.h 0x13e8[gp], r1
    st.h r1, 0x4810[gp]
    ld.w 0x0cc0[gp], r1
    st.w r1, 0x4814[gp]
    ld.w 0x142c[gp], r1
    st.w r1, 0x4818[gp]
    ld.w 0x073c[gp], r1
    st.w r1, 0x481c[gp]
    ld.w 0x1448[gp], r1
    st.w r1, 0x4820[gp]
    sld.bu 0[ep], r1
    st.b r1, 0x4824[gp]

.L_restore_and_loop:
    ld.w 0[sp], r2
    addi 4, sp, sp
    br .L_tick_wait
