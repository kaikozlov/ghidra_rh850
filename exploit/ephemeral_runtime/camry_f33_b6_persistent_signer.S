/* Exact-F33 normal-boot C7/native-B6 signer.
 *
 * This omits the RAM experiment's verbose transaction telemetry so it fits one
 * xref-free CodeFlash pocket. Native selector/key compatibility is established
 * by the separate passive 0x08A verifier before installation. This resident
 * retains exact freshness reconstruction, command-5 checks, the fresh-sequence
 * gate, and native pass-through on every runtime failure.
 */
    .section .persistent_first,"ax"
    .global _persistent_entry
_persistent_entry:
    prepare {lp}, 0
    ld.w 0x4a5c[gp], r6
    mov 0x53364249, r7
    cmp r6, r7
    be .L_state_ready
    st.w r7, 0x4a5c[gp]
    st.w r0, 0x4a78[gp]       /* last C7 sequence and status scratch */
    st.w r0, 0x4af0[gp]       /* last processed native trailer */
.L_state_ready:
    jarl32 _persistent_signer_body, lp
    jarl32 displaced_stock_call, lp
    dispose 0, {lp}, lp

_persistent_signer_body:
    prepare {lp}, 0
    ld.hu -0x6386[gp], r6      /* FEBE547A profile-2 queue length */
    addi -0x20, r6, r7
    cmp r0, r7
    bne .L_return_early
    ld.w -0x6310[gp], r6       /* native B28..B31 */
    ld.w 0x4af0[gp], r7
    cmp r6, r7
    be .L_return_early
    st.w r6, 0x4af0[gp]

    ld.hu -0x6bcc[gp], r6      /* 00 C7 seq 00 target-hi target-lo 00 00 */
    mov 0xc700, r7
    cmp r6, r7
    bne .L_return_early
    ld.bu -0x6bca[gp], r8
    cmp r0, r8
    be .L_return_early
    ld.bu 0x4a78[gp], r7
    cmp r8, r7
    be .L_return_early
    st.b r8, 0x4a78[gp]

.L_build_domain:
    ld.w -0x6310[gp], r6
    st.w r6, 0x4a70[gp]
    movea 0x4a88, gp, r6      /* 00 B6 || native B0..B27 */
    st.b r0, 0[r6]
    movea 0xb6, r0, r7
    st.b r7, 1[r6]
    addi 2, r6, r6
    movea -0x632c, gp, r7
    movea 28, r0, r8
    jarl32 mem_copy, lp
    ld.bu 0x4a8d[gp], r6
    andi 0xc0, r6, r6
    ori 0x0b, r6, r6
    st.b r6, 0x4a8d[gp]
    ld.hu -0x6bc8[gp], r6     /* target bytes directly from C7 */
    st.h r6, 0x4a8e[gp]
    ld.bu 0x4a90[gp], r6
    andi 0xfb, r6, r6
    st.b r6, 0x4a90[gp]
    movea 100, r0, r6
    st.b r6, 0x4a92[gp]
    st.b r6, 0x4a93[gp]
.L_domain_ready:
    ld.bu 0x4a70[gp], r14
    mov r14, r15
    shr 6, r15
    mov r14, r16
    shr 4, r16
    andi 3, r16, r16
    ld.w -0x623c[gp], r13     /* authenticated reset */
    mov r16, r18
    mov r13, r17
    andi 3, r17, r17
    sub r17, r18
    /* Preserve the four-byte stock marker at 0x000FFF00 between the two
     * erased tail spans.  The linker fixes this short branch to 0x000FFF04. */
    br .L_second
.L_return_early:
    jr32 .L_return

    .section .persistent_second,"ax"
.L_second:
    andi 3, r18, r18
    shl 30, r18
    sar 30, r18
    add r18, r13
    ld.w -0x6240[gp], r12     /* authenticated trip */
    ld.w -0x6218[gp], r17     /* committed slot-1 trip/reset/message */
    cmp r17, r12
    bne .L_return
    ld.w -0x6214[gp], r17
    cmp r17, r13
    bne .L_return
    ld.hu -0x6210[gp], r17
    mov r17, r18
    andi 3, r18, r18
    sub r18, r15
    andi 3, r15, r15
    cmp r0, r15
    bne .L_message_delta_ready
    add 4, r15
.L_message_delta_ready:
    add r15, r17
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

    movea 1, r0, r6          /* {type=1, selector=4} */
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
    mov 0, r6
    movea 0x4aac, gp, r7
    movea 0x4abc, gp, r8
    movea 1, r0, r9
    jarl32 command5_sync, lp
    cmp r0, r10
    bne .L_return
    ld.bu 0x5bbc[gp], r6
    addi -1, r6, r0
    bne .L_return
    ld.bu 0x5bbd[gp], r6
    cmp r0, r6
    bne .L_return

    /* Assemble FV4 || CMAC-MSB28 in wire byte order. */
    ld.bu 0x4a70[gp], r6
    andi 0xf0, r6, r6
    shl 24, r6
    ld.w 0x4aac[gp], r7
    bsw r7, r7
    shr 4, r7
    or r7, r6
    bsw r6, r6
.L_replace:
    st.w r6, -0x6310[gp]     /* safe before memcpy; SecOC runs after return */
    movea -0x6329, gp, r6
    movea 0x4a8d, gp, r7
    movea 7, r0, r8
    jarl32 mem_copy, lp
    ld.w -0x6310[gp], r6
    st.w r6, 0x4af0[gp]
.L_return:
    dispose 0, {lp}, lp
