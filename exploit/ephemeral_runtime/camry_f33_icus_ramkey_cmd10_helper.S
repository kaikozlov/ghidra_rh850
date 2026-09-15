/* Exact-F33 volatile ICU-S candidate-command-10 probe.
 * Preconditions: previous helper proved command9 LOAD_PLAIN_KEY by selector-E
 * command5 CMAC and left RK9O at private scratch 0xFEBF02F4. Resident helper
 * replacement does not reset the ECU/HSM, so RAM_KEY remains live.
 * Test: command 10, no input, seven 128-bit outputs = SHE M1..M5 geometry
 * (1 + 2 + 1 + 2 + 1 blocks = 112 bytes).
 */
    .section .text
    .global _helper_entry
_helper_entry:
    prepare {lp}, 0
    ld.w 0x4a68[gp], r6
    mov 0x54303152, r7        /* bytes "R10T"; resident clears telemetry on arm */
    cmp r6, r7
    be .L_serve

    /* Hard continuity gate: do not issue unknown command unless cmd9 was proven. */
    ld.w 0x4af4[gp], r6
    mov 0x4f394b52, r7        /* bytes "RK9O" */
    cmp r6, r7
    bne .L_precondition_fail

    /* The previous command-5 proof must have returned the stock driver to idle. */
    ld.bu 0x5b6c[gp], r6
    movea 0xe1, r0, r7
    cmp r7, r6
    bne .L_not_idle
    mov 0xffc5d00c, r6
    ld.w 0[r6], r7
    andi 1, r7, r7
    cmp r0, r7
    bne .L_not_idle
    mov 0xffc5d014, r6
    ld.w 0[r6], r7
    andi 3, r7, r7
    cmp r0, r7
    bne .L_not_idle

    /* Clear 112-byte export destination only after consuming the marker. */
    movea 0x4a88, gp, r6
    movea 28, r0, r7
.L_clear:
    st.w r0, 0[r6]
    add 4, r6
    add -1, r7
    cmp r0, r7
    bne .L_clear

    /* Candidate command 10: zero input blocks, seven output blocks. */
    mov 0x0008a538, r6       /* inert input callback, count 0 */
    st.w r6, 0x5b1c[gp]
    mov 0x0008a5ae, r7       /* output FIFO callback */
    st.w r7, 0x5b20[gp]
    mov 0x0008a600, r8       /* finalizer */
    st.w r8, 0x5b24[gp]
    movea 10, r0, r9
    st.w r9, 0x5b28[gp]
    st.w r0, 0x5b2c[gp]
    st.w r0, 0x5b30[gp]
    movea 7, r0, r9
    st.w r9, 0x5b34[gp]
    st.w r0, 0x5b38[gp]
    st.w r0, 0x5b40[gp]
    movea 0x4a88, gp, r9
    st.w r9, 0x5b44[gp]
    mov -1, r10
    st.w r10, 0x5b50[gp]
    not r9, r10
    st.w r10, 0x5b54[gp]
    not r6, r10
    st.w r10, 0x5b60[gp]
    not r7, r10
    st.w r10, 0x5b64[gp]
    not r8, r10
    st.w r10, 0x5b68[gp]
    st.b r0, 0x5b6d[gp]
    movea -46, r0, r10
    st.b r10, 0x5b6c[gp]
    mov 0xffc5d000, r10
    movea 10, r0, r9
    st.w r9, 0[r10]

    mov 0x8000, r6
.L_wait10:
    ld.bu 0x5b6c[gp], r7
    addi 0x1f, r7, r0
    be .L_done10
    add -1, r6
    cmp r0, r6
    bne .L_wait10
    jarl32 icus_abort_recover, lp
    movea 3, r0, r6
    br .L_finish

.L_done10:
    mov 0xffc5d010, r6
    ld.w 0[r6], r7          /* full ICUS error/status word */
    ld.w 0x5b38[gp], r8     /* completed output block count */
    andi 0x0fff, r7, r9
    cmp r0, r9
    bne .L_engine_fail
    addi -7, r8, r0
    bne .L_geometry_fail
    movea 1, r0, r6
    br .L_finish_status
.L_engine_fail:
    movea 4, r0, r6
    br .L_finish_status
.L_geometry_fail:
    movea 5, r0, r6
.L_finish_status:
    /* Telemetry holds status/count because all 112 private bytes are export. */
    mov 0x54303152, r9       /* bytes "R10T" */
    st.w r9, 0x4a68[gp]
    st.b r6, 0x4a6e[gp]     /* terminal */
    st.w r7, 0x4a70[gp]     /* initial status */
    st.w r8, 0x4a74[gp]     /* initial output count */
    br .L_mark_private

.L_precondition_fail:
    movea 2, r0, r6
    mov 0x54303152, r9
    st.w r9, 0x4a68[gp]
    st.b r6, 0x4a6e[gp]
    br .L_mark_private

.L_not_idle:
    movea 6, r0, r6
    mov 0x54303152, r9
    st.w r9, 0x4a68[gp]
    st.b r6, 0x4a6e[gp]
    br .L_mark_private

.L_finish:
    /* timeout: preserve abort rc in telemetry word +0x08 */
    mov 0x54303152, r9
    st.w r9, 0x4a68[gp]
    st.b r6, 0x4a6e[gp]
    st.w r10, 0x4a70[gp]
.L_mark_private:
    st.b r0, 0x4af8[gp]      /* private page-sequence byte, outside 112-byte export */
    br .L_return

.L_serve:
    /* Explicit 00 C8 seq page. Pages 0..4 copy the 112-byte export in 24-byte chunks. */
    ld.hu -0x6bcc[gp], r6
    mov 0xc800, r7
    cmp r6, r7
    bne .L_return
    ld.bu -0x6bca[gp], r8
    ld.bu 0x4af8[gp], r7     /* last page sequence, immediately after export */
    cmp r8, r7
    be .L_return
    st.b r8, 0x4af8[gp]
    ld.bu -0x6bc9[gp], r6
    movea 0xff, r0, r7
    cmp r6, r7
    be .L_disarm
    cmp 4, r6
    bh .L_return
    /* Publish header + 24-byte slice. */
    mov 0x54303152, r7
    st.w r7, 0x4a68[gp]
    ld.bu 0x4a6c[gp], r7
    add 1, r7
    st.b r7, 0x4a6c[gp]     /* generation */
    st.b r6, 0x4a6d[gp]     /* page */
    mov r6, r8
    shl 3, r8
    mov r6, r9
    shl 4, r9
    add r9, r8              /* page * 24 */
    movea 0x4a88, gp, r7
    add r8, r7
    movea 0x4a70, gp, r8
    movea 6, r0, r9
    movea 4, r0, r10
    cmp r10, r6
    bne .L_copy_page
    /* Page 4 contains only the final 16 export bytes; zero the unused tail. */
    movea 4, r0, r9
    st.w r0, 0x4a80[gp]
    st.w r0, 0x4a84[gp]
.L_copy_page:
    ld.w 0[r7], r10
    st.w r10, 0[r8]
    add 4, r7
    add 4, r8
    add -1, r9
    cmp r0, r9
    bne .L_copy_page
    br .L_return

.L_disarm:
    st.b r0, 0x4a62[gp]
    st.b r0, 0x4a60[gp]
.L_return:
    dispose 0, {lp}, lp
