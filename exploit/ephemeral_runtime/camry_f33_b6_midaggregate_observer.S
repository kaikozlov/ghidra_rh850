/*
 * Exact-F33 deterministic mid-aggregate B6 ingress observer.
 *
 * The earlier pre-aggregate/inter-tick monitors sampled outside the only
 * deterministic lifetime of the profile-2 queue.  Exact F33 drains the
 * software CAN receive ring in 0x79EDE/0x809FE and can then consume SecOC in
 * 0x6A410 during the same 0x7A254 foreground invocation.  This resident keeps
 * stock ordering but splits that invocation at the return from 0x79EDE:
 *
 *   ... 7BE3C -> 7BBC2 -> 7C43C -> 79EDE
 *                         [OBSERVE HERE]
 *       -> stock 7A254 tail @ 7A272 ... -> 6A410 -> ...
 *
 * The 0x79EDE -> 0x809FE receive-ring drain is unique in the exact image;
 * 0x809FE -> 0x808D6 -> 0x80884 reaches the normal CanIf callback set that
 * contains 0x810F2 and protected PduR/SecOC dispatch.  Therefore this point is
 * after the B6/D7 normal receive dispatch and before this cycle's SecOC
 * consumer.  The stock 0x7A254 tail is entered with the original stack frame,
 * and its stock DISPOSE returns to the caller normally.
 *
 * Observation is autonomous after the same 224-tick startup qualification as
 * the live-qualified generic resident.  No SID23 polling is required during a
 * treatment block: read the mailbox once before and once after.
 *
 * Mailbox FEBF0000..FEBF0027 (observer-owned only after qualification):
 *   +00 magic 0x4D364236       +04 version=1
 *   +08 observation_count      +0C D7_queue32_count
 *   +10 B6_queue32_count       +14 ID63_marker_count
 *   +18..+27 last ID63 B0..B11 || B28..B31
 *
 * Added writes are confined to FEBF0000..FEBF0027.  No source PDU, SecOC
 * result, route44, steering state, CAN/MMIO, or flash location is written.
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

    /* Publish attestation metadata only after the same 224-tick startup
       qualification used by the live-proven residents.  This lives outside
       7A254's FE01 gate so NRTD attestation does not depend on RX state.
       Counters are deliberately not zeroed: the host always takes modulo-u32
       before/after deltas, so preserving arbitrary/stale starting values is
       both safe and substantially smaller than clearing the mailbox. */
    movea -0x7e25, gp, ep
    tst1 7, 0[ep]
    be .L_no_mailbox_attest
    tst1 6, 0[ep]
    be .L_no_mailbox_attest
    tst1 5, 0[ep]
    be .L_no_mailbox_attest
    mov 0x4d364236, r7
    st.w r7, 0x4800[gp]
    movea 1, r0, r7
    st.b r7, 0x4804[gp]
.L_no_mailbox_attest:
    jarl32 observed_aggregate, lp
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

/* Exact 0x667E6 prefix, then tail-call the untouched suffix at 0x667F2.
 * The stock suffix's DISPOSE consumes this frame and returns to our caller. */
observed_aggregate:
    prepare {lp}, 0
    jarl32 agg_69ca2, lp
    jarl32 observed_7a254, lp
    jr32 stock_667e6_tail

/* Exact 0x7A254 prefix through 0x79EDE.  After observing, tail-call stock
 * 0x7A272, which executes every remaining original call including 0x6A410 and
 * consumes this exact PREPARE frame at its original DISPOSE. */
observed_7a254:
    prepare {lp}, 0
    ld.hu -0x7a0e[gp], r6       /* FEBE3DF2 */
    movea -0x1ff, r0, r7        /* FE01 */
    cmp r6, r7
    bne .L_7a254_return
    jarl32 rx_7be3c, lp
    jarl32 rx_7bbc2, lp
    jarl32 rx_7c43c, lp
    jarl32 rx_79ede, lp

    /* Before qualification the mailbox magic is absent, so observation is a
       no-op and stock 7A254 continues unchanged. */
    ld.w 0x4800[gp], r6
    mov 0x4d364236, r7
    cmp r6, r7
    bne .L_7a254_tail

.L_observe:
    ld.w 0x4808[gp], r6
    add 1, r6
    st.w r6, 0x4808[gp]

    /* Native protected D7 profile is the same-scheduler positive control. */
    ld.hu -0x638e[gp], r6       /* FEBE5472 */
    addi -0x20, r6, r7
    cmp r0, r7
    bne .L_b6
    ld.w 0x480c[gp], r6
    add 1, r6
    st.w r6, 0x480c[gp]

.L_b6:
    ld.hu -0x6386[gp], r6       /* FEBE547A */
    addi -0x20, r6, r7
    cmp r0, r7
    bne .L_7a254_tail
    ld.w 0x4810[gp], r6
    add 1, r6
    st.w r6, 0x4810[gp]

    /* ID63 is outside the normal command dictionary and is the ingress-only
       treatment marker. */
    ld.bu -0x6329[gp], r6      /* FEBE54D7 == B3 */
    andi 0x3f, r6, r6
    addi -0x3f, r6, r7
    cmp r0, r7
    bne .L_7a254_tail
    ld.w 0x4814[gp], r6
    add 1, r6
    st.w r6, 0x4814[gp]
    ld.w -0x632c[gp], r6       /* B0..B3 */
    st.w r6, 0x4818[gp]
    ld.w -0x6328[gp], r6       /* B4..B7 */
    st.w r6, 0x481c[gp]
    ld.w -0x6324[gp], r6       /* B8..B11 */
    st.w r6, 0x4820[gp]
    ld.w -0x6310[gp], r6       /* B28..B31 */
    st.w r6, 0x4824[gp]

.L_7a254_tail:
    jr32 stock_7a254_after_79ede
.L_7a254_return:
    dispose 0, {lp}, lp
