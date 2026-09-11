/* Exact-F33 low-RAM native-B6 verify/replace signer, loaded after startup. */
    .section .text
    .global _helper_entry
_helper_entry:
    prepare {lp}, 0
    ld.hu -0x6386[gp], r6      /* FEBE547A profile-2 queue length */
    addi -0x20, r6, r7
    cmp r0, r7
    bne .L_return

    /* The queue can remain length 32 across scheduler ticks.  Its protected
       trailer changes per native frame; process a given frame only once. */
    ld.w -0x6310[gp], r6
    ld.w 0x4af0[gp], r7      /* private last-seen native trailer */
    cmp r6, r7
    be .L_return
    st.w r6, 0x4af0[gp]
    ld.w 0x4a68[gp], r10
    add 1, r10
    st.w r10, 0x4a68[gp]      /* distinct native B6 count */

    /* Before replacement is ever allowed, automatically prove the local
       freshness+command5 construction against one untouched Toyota B6. */
    ld.bu 0x4a79[gp], r6      /* 0=untried, 1=verified, 2=failed */
    cmp r0, r6
    be .L_verify
    addi -1, r6, r0
    bne .L_return

    /* One-shot replacement control on the proven latest-frame mailbox:
         00 C7 seq 00 target_hi target_lo 00 00
       seq zero is reserved; each nonzero sequence is consumed at most once. */
    ld.hu -0x6bcc[gp], r6
    mov 0xc700, r7
    cmp r6, r7
    bne .L_return
    ld.bu -0x6bca[gp], r8
    cmp r0, r8
    be .L_return
    ld.bu 0x4a78[gp], r7
    cmp r8, r7
    be .L_return
    st.b r8, 0x4a78[gp]
    movea 2, r0, r6
    st.b r6, 0x4ad0[gp]       /* operation = replace */
    ld.hu -0x6bc8[gp], r6
    st.h r6, 0x4ad2[gp]       /* last requested target bytes */
    br .L_build_domain

.L_verify:
    movea 2, r0, r6
    st.b r6, 0x4a79[gp]       /* terminal failure unless equality below */
    movea 1, r0, r6
    st.b r6, 0x4ad0[gp]       /* operation = verify-native */

.L_build_domain:
    /* Preserve the exact trailer paired with this command-5 operation.  Do
       not overwrite it while later native frames pass after a failed oracle. */
    ld.w -0x6310[gp], r6
    st.w r6, 0x4a70[gp]

    /* Scratch FEBF0288: 00 B6 || native B0..B27.  This lies in the statically
       reference-free FEBF0000..0307 pocket; only SID23 visibility changes at
       0288, so command5 scratch need not consume host-readable space. */
    movea 0x4a88, gp, r6
    st.b r0, 0[r6]
    movea 0xb6, r0, r7
    st.b r7, 1[r6]
    addi 2, r6, r6
    movea -0x632c, gp, r7
    movea 28, r0, r8
    jarl32 mem_copy, lp

    ld.bu 0x4ad0[gp], r9
    addi -2, r9, r0
    bne .L_domain_ready
    ld.bu 0x4a8d[gp], r6      /* scratch application B3 */
    andi 0xc0, r6, r6
    ori 0x0b, r6, r6          /* Target Lateral ID 11 */
    st.b r6, 0x4a8d[gp]
    ld.hu 0x4ad2[gp], r6
    st.h r6, 0x4a8e[gp]       /* B4:B5 target, byte-identical signed16 BE */
    ld.bu 0x4a90[gp], r6      /* application B6 */
    andi 0xfb, r6, r6         /* signal265=0 */
    st.b r6, 0x4a90[gp]
    movea 100, r0, r6
    st.b r6, 0x4a92[gp]       /* B8 contribution = 100% */
    st.b r6, 0x4a93[gp]       /* B9 contribution = 100% */
.L_domain_ready:

    /* Reconstruct the same ordinary-profile freshness arithmetic recovered
       from exact-F33 0x909CA/0x90A48.  B28[7:6] is message-low2 and
       B28[5:4] is reset-low2.  Select reset current/-1/+1/-2/+2 in stock
       order, then advance the committed slot-1 message to the nearest later
       value.  Epoch/reset disagreement is deliberately fail-closed: the
       untouched native B6 continues through the stock receiver. */
    ld.bu 0x4a70[gp], r14
    mov r14, r15
    shr 6, r15              /* received message-low2 */
    mov r14, r16
    shr 4, r16
    andi 3, r16, r16        /* received reset-low2 */
    ld.w -0x623c[gp], r13   /* authenticated current reset */
    mov r16, r18
    mov r13, r17
    andi 3, r17, r17
    sub r17, r18
    andi 3, r18, r18
    shl 30, r18
    sar 30, r18             /* 2-bit signed delta: 0,+1,-2,-1 */
    add r18, r13
    ld.w -0x6240[gp], r12   /* authenticated current trip */
    ld.w -0x6218[gp], r17   /* committed ordinary slot-1 trip */
    cmp r17, r12
    bne .L_return
    ld.w -0x6214[gp], r17   /* committed ordinary slot-1 reset */
    cmp r17, r13
    bne .L_return
    ld.hu -0x6210[gp], r17  /* committed ordinary slot-1 message */
    mov r17, r18
    andi 3, r18, r18
    sub r18, r15
    andi 3, r15, r15
    cmp r0, r15
    bne .L_message_delta_ready
    add 4, r15
.L_message_delta_ready:
    add r15, r17

    /* Preserve an exact transaction witness, then pack the 46-bit full
       freshness exactly as stock 0x90566 does for command 5. */
    st.w r12, 0x4a7c[gp]
    st.w r13, 0x4a80[gp]
    st.h r17, 0x4a84[gp]
    st.b r16, 0x4a86[gp]
    movea 0x2e, r0, r6
    st.b r6, 0x4a87[gp]
    st.w r6, 0x4af4[gp]
    movea 0x4a7c, gp, r6
    movea 0x4aa6, gp, r7
    movea 0x4af4, gp, r8
    jarl32 freshness_encode, lp

    /* command5 output 02AC, outlen 02BC, config 02C0/02C4. */
    movea 1, r0, r6
    st.w r6, 0x4ac0[gp]
    movea 4, r0, r7
    st.w r7, 0x4ac4[gp]
    movea 0x4ac0, gp, r7
    st.w r7, 0x5ba0[gp]
    movea 0x4a88, gp, r7
    st.w r7, 0x5ba4[gp]
    movea 36, r0, r7
    st.w r7, 0x5ba8[gp]
    movea 16, r0, r7
    st.w r7, 0x4abc[gp]

    ld.w 0x4a6c[gp], r10
    add 1, r10
    st.w r10, 0x4a6c[gp]      /* command5 attempts */
    mov 0, r6
    movea 0x4aac, gp, r7
    movea 0x4abc, gp, r8
    movea 1, r0, r9
    jarl32 command5_sync, lp
    st.b r10, 0x4a63[gp]      /* state.last_command5_rc */
    cmp r0, r10
    bne .L_return
    ld.bu 0x5bbc[gp], r6
    st.b r6, 0x4a7a[gp]
    addi -1, r6, r0
    bne .L_return
    ld.bu 0x5bbd[gp], r6
    st.b r6, 0x4a7b[gp]
    cmp r0, r6
    bne .L_return
    /* FV4 || CMAC-MSB28 -> readable last_computed_trailer. */
    ld.bu 0x4a70[gp], r6
    andi 0xf0, r6, r6
    shl 24, r6
    ld.w 0x4aac[gp], r7
    bsw r7, r7
    shr 4, r7
    or r7, r6
    bsw r6, r6
    st.w r6, 0x4a74[gp]

    ld.bu 0x4ad0[gp], r6
    addi -2, r6, r0
    be .L_replace

    /* First native oracle: equality enables replacement for later frames. */
    ld.w 0x4a74[gp], r6
    ld.w 0x4a70[gp], r7
    cmp r6, r7
    bne .L_verify_mismatch
    movea 1, r0, r6
    st.b r6, 0x4a79[gp]
    br .L_return
.L_verify_mismatch:
    br .L_return

.L_replace:
    /* Only after successful command5: commit B3..B9.  The ordinary signer
       installs the locally computed trailer.  The deliberately separate
       stage-5-carrier build preserves the paired native trailer, making the
       modified application bytes cryptographically invalid on purpose; its
       only intended use is to test the already-installed receiver-result
       bypass at this proven post-drain/pre-SecOC boundary. */
    movea -0x6329, gp, r6
    movea 0x4a8d, gp, r7
    movea 7, r0, r8
    jarl32 mem_copy, lp
#ifdef F33_STAGE5_CARRIER
    ld.w 0x4a70[gp], r6
#else
    ld.w 0x4a74[gp], r6
    st.w r6, -0x6310[gp]
#endif
    st.w r6, 0x4af0[gp]     /* dedup replacement without destroying native witness */
    ld.w 0x4a64[gp], r6
    add 1, r6
    st.w r6, 0x4a64[gp]
.L_return:
    dispose 0, {lp}, lp
