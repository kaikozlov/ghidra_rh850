/*
 * Exact-F33 high-rate 0x08A command-5 oracle helper.
 *
 * Request transport is the stock physical diagnostic path 0x7A1 -> CanTp/PduR
 * -> DCM physical buffer FEBE5651. The fixed 40-byte N-SDU is:
 *
 *   B0=C9 (unsupported SID) B1=C9 (durable tag) B2=transaction_seq
 *   B3..B38 = 36-byte authenticated domain
 *              00 8A || application[28] || freshness[6]
 *   B39 = transaction_seq ^ FF      (final-byte commit marker)
 *
 * The helper runs only after 0x79EDE has drained receive work. The commit byte
 * prevents a partially reassembled First/Consecutive Frame sequence from being
 * consumed. Each sequence is attempted once.
 *
 * On completion, one raw classic response is emitted through the exact lower
 * hardware object used by stock EPS response CAN ID 0x7A9:
 *
 *   07 C9 seq status cmac0 cmac1 cmac2 cmac3
 *
 * status 0 = command5 rc0/done1/status0/outlen16
 * status 1 = command5 wrapper/completion error
 * status 2 = command5 transient busy/timeout
 * status 3 = bad authenticated-domain DataID
 *
 * The lower response uses software handle 0x00F0, whose exact F33 confirmation
 * dispatch is a no-op; it therefore cannot manufacture a CanTp TxConfirmation.
 * The host already owns the full freshness value and can construct
 * FV4||MAC28 from the first four CMAC bytes. No 0x08A/B6 transmit or flash
 * mutation exists here.
 */

    .section .text
    .global _helper_entry
_helper_entry:
    prepare {r20-r21,lp}, 0

    /* DCM B0 is the unsupported-service SID and may be cleared/reused by
       stock teardown before this recurring helper runs. Match the already-live
       C6/C7 carrier rule: B1 is the durable private tag. */
    ld.bu -0x61ae[gp], r6      /* FEBE5652 = physical N-SDU B1 */
    movea 0xc9, r0, r7
    cmp r6, r7
    bne .L_return

    ld.bu -0x61ad[gp], r20     /* N-SDU B2 = transaction seq */
    ld.bu 0x4a62[gp], r7       /* last processed seq */
    cmp r20, r7
    be .L_return

    /* Final-byte commit: B39 == seq ^ FF. */
    ld.bu -0x6188[gp], r6
    mov r20, r7
    xori 0x00ff, r7, r7
    zxb r7
    cmp r6, r7
    bne .L_return

    st.b r20, 0x4a62[gp]
    ld.w 0x4a64[gp], r6
    add 1, r6
    st.w r6, 0x4a64[gp]        /* request_count */

    /* Domain begins at DCM B3 and must be exact DataID 0x008A. */
    ld.hu -0x61ac[gp], r6
    mov 0x8a00, r7              /* little-endian bytes 00 8A */
    cmp r6, r7
    bne .L_bad_domain

    /* Scratch: output 0288, outlen 0298, config 029C/02A0. */
    mov 1, r6
    st.w r6, 0x4a9c[gp]
    mov 4, r6
    st.w r6, 0x4aa0[gp]
    movea 0x4a9c, gp, r6
    st.w r6, 0x5ba0[gp]        /* stock wrapper config pointer */
    movea -0x61ac, gp, r6
    st.w r6, 0x5ba4[gp]        /* input = DCM B3, 36 bytes */
    movea 36, r0, r6
    st.w r6, 0x5ba8[gp]
    movea 16, r0, r6
    st.w r6, 0x4a98[gp]

    mov 0, r6                   /* clean command5 driver record 0 */
    movea 0x4a88, gp, r7       /* 16-byte output */
    movea 0x4a98, gp, r8       /* in/out length */
    mov 1, r9
    jarl32 command5_sync, lp

    st.b r10, 0x4a70[gp]       /* last wrapper rc */
    ld.bu 0x5bbc[gp], r6
    st.b r6, 0x4a71[gp]        /* done */
    ld.bu 0x5bbd[gp], r7
    st.b r7, 0x4a72[gp]        /* command status */
    ld.bu 0x4a98[gp], r8
    st.b r8, 0x4a73[gp]        /* output length low byte */

    cmp r0, r10
    bne .L_wrapper_error
    addi -1, r6, r0
    bne .L_error
    cmp r0, r7
    bne .L_error
    movea 16, r0, r7
    cmp r7, r8
    bne .L_error

    ld.w 0x4a88[gp], r6
    st.w r6, 0x4a74[gp]        /* last CMAC first4 witness */
    ld.w 0x4a68[gp], r7
    add 1, r7
    st.w r7, 0x4a68[gp]        /* success_count */
    mov 0, r21
    br .L_respond

.L_wrapper_error:
    addi -2, r10, r0
    be .L_busy
.L_error:
    mov 1, r21
    br .L_respond_zero
.L_busy:
    mov 2, r21
    br .L_respond_zero
.L_bad_domain:
    mov 3, r21
.L_respond_zero:
    st.w r0, 0x4a88[gp]

.L_respond:
    st.b r21, 0x4a63[gp]       /* last_status */

    /* ISO-TP single-frame-looking private response on stock 0x7A9. */
    movea 0x07, r0, r6
    st.b r6, 0x4aa4[gp]
    movea 0xc9, r0, r6
    st.b r6, 0x4aa5[gp]
    st.b r20, 0x4aa6[gp]
    st.b r21, 0x4aa7[gp]
    ld.w 0x4a88[gp], r6
    st.w r6, 0x4aa8[gp]

    /* Lower Can_PduType: use the exact HTH2 lower object 53 that stock 0x7A9
       resolves through, but a special no-op software handle 0x00F0. This avoids
       forging a CanTp TxConfirmation for source PDU 0x0800. */
    movea 0x00f0, r0, r6
    st.h r6, 0x4aac[gp]
    movea 8, r0, r6
    st.b r6, 0x4aae[gp]
    st.b r0, 0x4aaf[gp]
    movea 0x07a9, r0, r6
    st.w r6, 0x4ab0[gp]
    movea 0x4aa4, gp, r6
    st.w r6, 0x4ab4[gp]
    movea 53, r0, r6           /* HTH2 lower object 53 -> node1/mailbox6 */
    movea 0x4aac, gp, r7
    jarl32 lower_can_write, lp
    st.b r10, 0x4a78[gp]       /* last response lower-writer rc */
    cmp r0, r10
    bne .L_return

    ld.w 0x4a6c[gp], r6
    add 1, r6
    st.w r6, 0x4a6c[gp]        /* accepted response count */

.L_return:
    dispose 0, {r20-r21,lp}, lp
