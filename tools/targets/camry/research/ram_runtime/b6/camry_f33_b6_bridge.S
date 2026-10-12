/*
 * Exact-F33 ABI-preserving protected-B6 receive bridge.
 *
 * RAM-only. This resident reproduces the stock application startup and
 * foreground scheduler with direct JARL32 calls. While explicitly armed by
 * the host control frame, it snapshots each complete profile-2 queue record
 * before the stock SecOC aggregate consumes it, then conditionally publishes
 * those exact 32 bytes through the firmware's native PduR route-44 receive
 * callback after the aggregate. The native COM unpacker, assist gates, limits,
 * and motor-command funnel remain unchanged.
 *
 * Added writes are confined to FEBF0000..FEBF003F and the resident's 8-byte
 * stack frame. There are no CAN transmit calls, dynamic calls, stock-code
 * patches, or persistent flash writes. Reset restores the stock path.
 *
 * Control frame at FEBE4C34: 00 F3 seq 20 arg32-le. arg0=STOP, nonzero=RUN.
 * Mailbox at FEBF0000:
 *   +00 magic "R6B6"  +04 version  +05 last_seq  +06 running
 *   +08 bridged  +0C pending  +10..2F saved B6
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

    /* Eight-byte PduInfoType: data pointer, u16 length, u16 reserved. */
    prepare {r29,lp}, 2

.L_tick_wait:
    /* Do not inspect or mutate the queue until startup has initialized our
       reference-free low-RAM mailbox and installed its magic. */
    ld.w 0x4800[gp], r6
    mov 0x42364252, r7
    cmp r6, r7
    bne .L_tick_test

    /* Acknowledge only the fixed RUN/STOP control opcode. */
    ld.hu -0x6bcc[gp], r6
    mov 0xf300, r7
    cmp r6, r7
    bne .L_queue_gate
    ld.bu -0x6bca[gp], r6
    ld.bu -0x6bc9[gp], r7
    addi -0x20, r7, r8
    cmp r0, r8
    bne .L_queue_gate
    st.w r0, 0x480c[gp]        /* valid RUN/STOP cancels any stale pending snapshot */
    st.b r6, 0x4805[gp]
    ld.bu -0x6bc8[gp], r7
    st.b r7, 0x4806[gp]

.L_queue_gate:
    ld.bu 0x4806[gp], r6
    cmp r0, r6
    be .L_tick_test
    ld.hu -0x6386[gp], r6       /* FEBE547A profile-2 queued length */
    addi -0x20, r6, r8
    cmp r0, r8
    bne .L_queue_absent
    /* Queue insertion publishes length only after copying the secured bytes.
       The foreground immediately follows the short fixed-size snapshot, so
       the single profile slot cannot be consumed underneath it. */
    movea -0x632c, gp, r6       /* FEBE54D4 secured B6 */
    movea 0x4810, gp, r7        /* FEBF0010 saved B6 */
    movea 32, r0, r8
.L_copy_b6:
    ld.bu 0[r6], r9
    st.b r9, 0[r7]
    add 1, r6
    add 1, r7
    add -1, r8
    cmp r0, r8
    bne .L_copy_b6
    mov 1, r6
    st.w r6, 0x480c[gp]
    br .L_tick_test

.L_queue_absent:
    st.w r0, 0x480c[gp]

.L_tick_test:
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

    /* Startup uses this pocket. Claim it only after stock tick 224. */
    movea -0x7e25, gp, ep
    tst1 7, 0[ep]
    be .L_run_aggregate
    tst1 6, 0[ep]
    be .L_run_aggregate
    tst1 5, 0[ep]
    be .L_run_aggregate
    ld.w 0x4800[gp], r6
    mov 0x42364252, r7
    cmp r6, r7
    be .L_run_aggregate
    movea 0x4800, gp, r6
    mov 12, r7
.L_clear_mailbox:
    st.w r0, 0[r6]
    add 4, r6
    add -1, r7
    cmp r0, r7
    bne .L_clear_mailbox
    mov 0x42364252, r7
    st.w r7, 0x4800[gp]
    mov 3, r7
    st.b r7, 0x4804[gp]

.L_run_aggregate:
    jarl32 fg_aggregate, lp

    /* Hand the saved bytes, not a reconstructed message, to the exact native
       successful-delivery endpoint. If stock already published a frame with the
       same B3, conservatively skip reinjection. Exact native success necessarily
       has the same B3; an unrelated same-B3 publication can only create a safe
       false negative for this bridge, never a duplicate publication. */
    ld.w 0x480c[gp], r6
    cmp r0, r6
    be .L_after_bridge
    ld.bu 0x4813[gp], r6       /* saved secured B3 */
    ld.bu -0x6bfe[gp], r7      /* route44 raw B3 at FEBE4C02 */
    cmp r6, r7
    be .L_clear_pending
    movea 0x4810, gp, r6
    st.w r6, 0[sp]
    movea 32, r0, r6
    st.h r6, 4[sp]
    st.h r0, 6[sp]
    movea 44, r0, r6
    mov sp, r7
    jarl32 b6_com_rx, lp
    ld.w 0x4808[gp], r6
    add 1, r6
    st.w r6, 0x4808[gp]
.L_clear_pending:
    st.w r0, 0x480c[gp]

.L_after_bridge:
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
    br .L_tick_wait
