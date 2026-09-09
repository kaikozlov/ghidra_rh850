/*
 * Exact-F33 bounded ICU-S command-5 selector-4 probe.
 *
 * This resident preserves the proven direct-JARL application startup and
 * foreground replay.  After foreground tick 224 it accepts only nine fixed
 * 4-byte input chunks and one EXECUTE command through the already-observed
 * extended-CAN staging cell at FEBE4C34.  EXECUTE calls the stock synchronous
 * record-0 wrapper at 0x89BC2 for exactly 36 input bytes and 16 output bytes.
 *
 * Control frame (extended 0x1FDC0002, classic CAN):
 *   B0=00 B1=C5 B2=sequence B3=opcode B4..B7=argument LE
 *   opcode 30..38: set input word 0..8
 *   opcode 39:     execute only after all nine words were received
 *
 * Probe RAM FEBF0000..FEBF004F:
 *   +00 magic 0x53333346 (little-endian "F33S")
 *   +04 version, +05 last sequence, +06 state, +07 wrapper return code
 *   +08 input bitmap (low nine bits), +0A command status, +0B done flag
 *   +0C output length, +10 input[36], +34 output[16]
 *   +48 private fixed config word type=1, +4C selector word=4
 *
 * state: 0 idle/assembling, 1 executing, 2 complete.
 * The selector and lengths are constants.  No CAN transmit, SecOC bypass,
 * steering path, flash write, dynamic memory access, or key extraction exists.
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

    /* Do not touch the probe mailbox before the live-qualified tick-224 gate. */
    tst1 7, 0[ep]
    be .L_tick_wait
    tst1 6, 0[ep]
    be .L_tick_wait
    tst1 5, 0[ep]
    be .L_tick_wait

    ld.w 0x4800[gp], r6
    mov 0x53333346, r7
    cmp r6, r7
    be .L_parse
    st.w r7, 0x4800[gp]
    movea 2, r0, r6
    st.w r6, 0x4804[gp]
    st.w r0, 0x4808[gp]
    st.w r0, 0x480c[gp]

.L_parse:
    ld.hu -0x6bcc[gp], r6
    mov 0xc500, r7
    cmp r6, r7
    bne .L_tick_wait
    ld.bu -0x6bca[gp], r6
    ld.bu 0x4805[gp], r7
    cmp r6, r7
    be .L_tick_wait
    st.b r6, 0x4805[gp]
    ld.bu -0x6bc9[gp], r7
    addi -0x30, r7, r8
    cmp 8, r8
    bnh .L_set_word
    addi -9, r8, r8
    cmp r0, r8
    bne .L_tick_wait

    ld.hu 0x4808[gp], r6
    addi -0x1ff, r6, r0
    be .L_execute
    br .L_tick_wait

.L_set_word:
    shl 2, r8
    movea 0x4810, gp, r6
    add r8, r6
    ld.w -0x6bc8[gp], r7
    st.w r7, 0[r6]
    shr 2, r8
    movea 1, r0, r7
    shl r8, r7
    ld.hu 0x4808[gp], r6
    or r7, r6
    st.h r6, 0x4808[gp]
    st.b r0, 0x4806[gp]
    br .L_tick_wait

.L_execute:
    movea 1, r0, r6
    st.b r6, 0x4806[gp]
    st.b r0, 0x4807[gp]
    st.w r6, 0x4848[gp]       /* config word 0: type = 1 exactly */
    movea 4, r0, r8
    st.w r8, 0x484c[gp]       /* config word 1: protected selector = 4 */
    movea 0x4810, gp, r6
    st.w r6, 0x5ba4[gp]       /* stock wrapper input pointer */
    movea 0x24, r6, r7        /* fixed output buffer = FEBF0034 */
    movea 0x4848, gp, r8
    st.w r8, 0x5ba0[gp]       /* stock wrapper config pointer */
    movea 36, r0, r8
    st.w r8, 0x5ba8[gp]       /* fixed input length */
    movea 16, r0, r8
    st.w r8, 0x480c[gp]
    movea 0x480c, gp, r8
    movea 1, r0, r9
    mov 0, r6                  /* clean driver record 0 */
    jarl32 command5_sync, lp
    st.b r10, 0x4807[gp]
    ld.bu 0x5bbd[gp], r6
    st.b r6, 0x480a[gp]
    ld.bu 0x5bbc[gp], r6
    st.b r6, 0x480b[gp]
    movea 2, r0, r6
    st.b r6, 0x4806[gp]
    br .L_tick_wait
