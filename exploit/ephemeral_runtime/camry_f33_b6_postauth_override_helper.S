/* Exact-F33 post-authenticated B6 application override.
 *
 * Entry is a tail replacement for FUN_000667E6 after the target receive task.
 * The high resident already owns the stock aggregate stack frame. This helper:
 *   1. runs the stock SecOC/result publication task,
 *   2. runs the normal communications follow-up,
 *   3. rewrites only authenticated route44 raw-COM B3..B9 while C7 is live,
 *   4. resumes the stock application/control aggregate and final tail.
 *
 * No native B6 freshness, sequence, SecOC trailer, or queue metadata is changed.
 */
    .section .text
    .global _helper_entry
_helper_entry:
    /* Native secured PDU -> verified upper delivery -> route44 raw COM. */
    jarl32 secoc_aggregate, lp
    jarl32 comm_after_secoc, lp

    /* Count observed route44 publications. The generation is specific to PDU44. */
    mov 0, r10                    /* this foreground tick published a new native B6 */
    ld.bu TSS3_ROUTE_GENERATION_OFF[gp], r6
    ld.bu 0x4ad5[gp], r7
    cmp r6, r7
    be .L_control
    st.b r6, 0x4ad5[gp]
    ld.w 0x4a68[gp], r7
    add 1, r7
    st.w r7, 0x4a68[gp]
    mov 1, r10
    st.b r10, 0x4a79[gp]      /* native route44 publication observed */

.L_control:
    /* C6/other diagnostics may reuse the DCM buffer. Only an exact C7 tag may
       create/change ownership, but once accepted the target is cached for the
       complete lease so later DCM traffic cannot leak one native target. */
    ld.bu TSS3_DCM_TAG_OFF[gp], r6
    movea 0xc7, r0, r9
    cmp r6, r9
    bne .L_age_cached_control

    ld.bu TSS3_DCM_SEQ_OFF[gp], r8
    ld.bu 0x4a78[gp], r7
    cmp r8, r7
    be .L_age_cached_control
    st.b r8, 0x4a78[gp]
    cmp r0, r8
    be .L_zero_lease

    /* A changed nonzero generation atomically snapshots the target bytes. */
    ld.bu TSS3_DCM_TARGET_OFF[gp], r6
    st.b r6, 0x4ad6[gp]
    ld.bu TSS3_DCM_TARGET_OFF + 1[gp], r6
    st.b r6, 0x4ad7[gp]
    mov 7, r7
    st.b r7, 0x4ad4[gp]
    br .L_apply_override

.L_zero_lease:
    st.b r0, 0x4ad4[gp]
    br .L_stock_application

.L_age_cached_control:
    ld.bu 0x4ad4[gp], r7
    cmp r0, r7
    be .L_stock_application
    add -1, r7
    st.b r7, 0x4ad4[gp]
    cmp r0, r7
    be .L_stock_application

.L_apply_override:
    /* Route44 raw B3: preserve native top two bits, select Target Lateral ID11. */
    ld.bu TSS3_RAW_B3_OFF[gp], r6
    andi 0xc0, r6, r6
    ori 0x0b, r6, r6
    st.b r6, TSS3_RAW_B3_OFF[gp]

    /* Raw B4:B5: byte-identical signed16 target cached with the C7 generation. */
    ld.bu 0x4ad6[gp], r6
    st.b r6, TSS3_RAW_B4_OFF[gp]
    ld.bu 0x4ad7[gp], r6
    st.b r6, TSS3_RAW_B5_OFF[gp]

    /* Preserve native B6 except signal265 bit2=0; keep native B7 sequence. */
    ld.bu TSS3_RAW_B6_OFF[gp], r6
    andi 0xfb, r6, r6
    st.b r6, TSS3_RAW_B6_OFF[gp]
    mov 100, r6
    st.b r6, TSS3_RAW_B8_OFF[gp]
    st.b r6, TSS3_RAW_B9_OFF[gp]

    /* Only count a committed ownership event when this tick carried a newly
       authenticated route44 publication. Rewrites of an already-consumed raw
       COM image are harmless but do not satisfy stationary qualification. */
    cmp r0, r10
    be .L_stock_application
    ld.w 0x4a6c[gp], r6       /* post-auth override count */
    add 1, r6
    st.w r6, 0x4a6c[gp]
    st.w r6, 0x4a64[gp]       /* state counter: override count */

.L_stock_application:
    jarl32 application_aggregate, lp
    jarl32 aggregate_final, lp
    /* Consume the high resident's signed_aggregate frame exactly like the
       original 0x667F2..0x66802 stock tail. */
    dispose 0, {lp}, lp
