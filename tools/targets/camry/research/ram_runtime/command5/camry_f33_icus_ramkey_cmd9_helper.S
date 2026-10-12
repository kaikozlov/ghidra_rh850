/* Exact-F33 volatile ICU-S candidate-command-9 probe.
 * Test: command 9 consumes one 128-bit block; if it is LOAD_PLAIN_KEY, selector
 * 0xE immediately yields the known command-5 CMAC under key 00..0f.
 * No persistent key-update command is issued.
 */
    .section .text
    .global _helper_entry
_helper_entry:
    prepare {lp}, 0
    ld.w 0x4a68[gp], r6
    mov 0x54394b52, r7        /* bytes "RK9T" */
    cmp r6, r7
    be .L_serve

    /* telemetry: magic, terminal, reserved, cmd9 status, cmd5 rc, CMAC16 */
    movea 0x4a68, gp, r6
    movea 8, r0, r7
.L_clear:
    st.w r0, 0[r6]
    add 4, r6
    add -1, r7
    cmp r0, r7
    bne .L_clear

    /* Refuse to touch ICU-S unless the stock asynchronous driver is idle. */
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

    /* Candidate command 9 input = known key 00 01 ... 0f. */
    mov 0x03020100, r6
    st.w r6, 0x4a88[gp]
    mov 0x07060504, r6
    st.w r6, 0x4a8c[gp]
    mov 0x0b0a0908, r6
    st.w r6, 0x4a90[gp]
    mov 0x0f0e0d0c, r6
    st.w r6, 0x4a94[gp]

    mov 0x0008a538, r6       /* input FIFO callback */
    st.w r6, 0x5b1c[gp]
    mov 0x0008a5ae, r7       /* inert output callback, output count 0 */
    st.w r7, 0x5b20[gp]
    mov 0x0008a600, r8       /* finalizer */
    st.w r8, 0x5b24[gp]
    movea 9, r0, r9
    st.w r9, 0x5b28[gp]
    movea 1, r0, r9
    st.w r9, 0x5b2c[gp]
    st.w r0, 0x5b30[gp]
    st.w r0, 0x5b34[gp]
    st.w r0, 0x5b38[gp]
    movea 0x4a88, gp, r9
    st.w r9, 0x5b40[gp]
    st.w r0, 0x5b44[gp]
    not r9, r10
    st.w r10, 0x5b50[gp]
    mov -1, r10
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
    movea 9, r0, r9
    st.w r9, 0[r10]

    /* Bound the asynchronous operation while ICU interrupts service FIFO/finalize. */
    mov 0x4000, r6
.L_wait9:
    ld.bu 0x5b6c[gp], r7
    addi 0x1f, r7, r0
    be .L_done9
    add -1, r6
    cmp r0, r6
    bne .L_wait9
    jarl32 icus_abort_recover, lp
    movea 3, r0, r6
    br .L_finish
.L_done9:
    mov 0xffc5d010, r6
    ld.w 0[r6], r7
    st.w r7, 0x4a70[gp]
    andi 0x0fff, r7, r8
    cmp r0, r8
    bne .L_fail9

    /* Command-5 proof under RAM_KEY selector 0xE. */
    movea 0x4a88, gp, r6
    movea 9, r0, r7
.L_clear_domain:
    st.w r0, 0[r6]
    add 4, r6
    add -1, r7
    cmp r0, r7
    bne .L_clear_domain
    movea 0xb6, r0, r6
    st.b r6, 0x4a89[gp]
    movea 16, r0, r6
    st.w r6, 0x4abc[gp]
    movea 14, r0, r6
    st.w r6, 0x4ac0[gp]
    movea 0x4ac0, gp, r7
    st.w r7, 0x5ba0[gp]
    movea 0x4a88, gp, r7
    st.w r7, 0x5ba4[gp]
    movea 36, r0, r7
    st.w r7, 0x5ba8[gp]
    mov 0, r6
    movea 0x4ac8, gp, r7
    movea 0x4abc, gp, r8
    movea 1, r0, r9
    jarl32 command5_sync, lp
    st.w r10, 0x4a74[gp]
    cmp r0, r10
    bne .L_fail5

    /* Publish actual CMAC and only declare success if all 128 bits match. */
    ld.w 0x4ac8[gp], r6
    st.w r6, 0x4a78[gp]
    mov 0x17271af6, r7
    cmp r6, r7
    bne .L_fail5
    ld.w 0x4acc[gp], r6
    st.w r6, 0x4a7c[gp]
    mov 0x6c70a73c, r7
    cmp r6, r7
    bne .L_fail5
    ld.w 0x4ad0[gp], r6
    st.w r6, 0x4a80[gp]
    mov 0x5d7b4ee4, r7
    cmp r6, r7
    bne .L_fail5
    ld.w 0x4ad4[gp], r6
    st.w r6, 0x4a84[gp]
    mov 0xd3697c6d, r7
    cmp r6, r7
    bne .L_fail5
    mov 0x4f394b52, r7        /* bytes "RK9O": proven cmd9/selector-E continuity marker */
    st.w r7, 0x4af4[gp]
    movea 1, r0, r6
    br .L_finish
.L_fail9:
    movea 2, r0, r6
    br .L_finish
.L_fail5:
    movea 4, r0, r6
    br .L_finish
.L_not_idle:
    movea 5, r0, r6
.L_finish:
    mov 0x54394b52, r7
    st.w r7, 0x4a68[gp]
    st.b r6, 0x4a6c[gp]
    br .L_return

.L_serve:
    /* 00 C8 seq FF asks helper to disarm and reopen loader at word index 0. */
    ld.hu -0x6bcc[gp], r6
    mov 0xc800, r7
    cmp r6, r7
    bne .L_return
    ld.bu -0x6bc9[gp], r6
    movea 0xff, r0, r7
    cmp r6, r7
    bne .L_return
    st.b r0, 0x4a62[gp]      /* armed=0 */
    st.b r0, 0x4a60[gp]      /* next_index=0: permit helper replacement */
.L_return:
    dispose 0, {lp}, lp
