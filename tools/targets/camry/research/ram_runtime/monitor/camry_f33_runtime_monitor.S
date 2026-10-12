/*
 * Exact-F33 ABI-preserving generic observation monitor.
 *
 * Stock startup/foreground calls use direct JARL disp32. Through foreground
 * count 223 this resident performs no added application-memory writes. From
 * count 224 onward it owns only the low-RAM control/snapshot block at
 * FEBF0000..FEBF0057 and reads configured 4-byte-aligned LocalRAM windows.
 *
 * Host commands arrive through the already-proven extended-CAN XCP staging
 * buffer at FEBE4C34. Frames are deliberately not XCP commands:
 *   B0=00 B1=F3 B2=sequence B3=opcode B4..B7=argument LE.
 * Opcodes:
 *   10..17   SET_WATCH slot0..7, argument = aligned LocalRAM address; 0 disables
 *   20       RUN/STOP, argument byte0 = 0/1
 *   21       SNAPSHOT once
 *
 * No source-memory write, CAN transmit, SecOC path, command-5 path, or flash
 * path is present. The host validates configured source addresses.
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

    /* Preserve the same write-free application-reappearance window as the
       v2 discriminator. */
    tst1 7, 0[ep]
    be .L_tick_wait
    tst1 6, 0[ep]
    be .L_tick_wait
    tst1 5, 0[ep]
    be .L_tick_wait

    /* Initialize the low-RAM monitor block once. Version byte +4 is the
       one-time sentinel; startup has already overwritten this low-RAM pocket. */
    ld.w 0x4800[gp], r6
    mov 0x4d333346, r7
    cmp r6, r7
    be .L_control_ready
    movea 0x4800, gp, r6
    mov 22, r7               /* clear +0x00..+0x57 */
.L_clear_control:
    st.w r0, 0[r6]
    add 4, r6
    add -1, r7
    cmp r0, r7
    bne .L_clear_control
    mov 0x4d333346, r7       /* little-endian bytes "F33M" */
    st.w r7, 0x4800[gp]
    movea 1, r0, r7
    st.b r7, 0x4804[gp]

.L_control_ready:
    /* Parse one new host command from FEBE4C34. */
    ld.hu -0x6bcc[gp], r6
    mov 0xf300, r7
    cmp r6, r7
    bne .L_sample_gate
    ld.bu -0x6bca[gp], r6    /* sequence */
    ld.bu 0x4805[gp], r7
    cmp r6, r7
    be .L_sample_gate
    st.b r6, 0x4805[gp]
    ld.bu -0x6bc9[gp], r7    /* opcode */

    addi -0x10, r7, r8
    cmp 7, r8
    bnh .L_set_watch
    addi -0x10, r8, r8       /* opcode-0x20 */
    cmp r0, r8
    be .L_set_run
    addi -1, r8, r8          /* opcode-0x21 */
    cmp r0, r8
    be .L_force_snapshot
    br .L_sample_gate

.L_set_watch:
    shl 2, r8
    movea 0x4810, gp, r6
    add r8, r6
    ld.w -0x6bc8[gp], r9     /* address argument */
    andi 3, r9, r10
    cmp r0, r10
    bne .L_sample_gate        /* reject unaligned windows in-resident */
    st.w r9, 0[r6]
    br .L_sample_gate

.L_set_run:
    ld.bu -0x6bc8[gp], r8    /* 0=stop, nonzero=run */
    st.b r8, 0x4806[gp]
    br .L_sample_gate

.L_force_snapshot:
    movea 1, r0, r8
    st.b r8, 0x4807[gp]

.L_sample_gate:
    ld.bu 0x4807[gp], r6
    cmp r0, r6
    bne .L_snapshot
    ld.bu 0x4806[gp], r6
    cmp r0, r6
    be .L_tick_wait

.L_snapshot:
    st.b r0, 0x4807[gp]
    ld.w 0x4808[gp], r6
    add 1, r6
    st.w r6, 0x4808[gp]
    st.w r6, 0x4830[gp]
    movea 0x4810, gp, r7
    movea 0x4834, gp, r8
    movea 8, r0, r9
.L_watch_loop:
    ld.w 0[r7], r10
    cmp r0, r10
    be .L_watch_zero
    ld.w 0[r10], r1
    br .L_watch_store
.L_watch_zero:
    mov 0, r1
.L_watch_store:
    st.w r1, 0[r8]
    add 4, r7
    add 4, r8
    add -1, r9
    cmp r0, r9
    bne .L_watch_loop
    st.w r6, 0x4854[gp]
    br .L_tick_wait
