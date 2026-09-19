/* READY-time 0x090 command-5 and sticky route40 helper.
 * Control: extended classic 0x1FDC0002 -> 00 F5 seq opcode argument32-le.
 * 30..38 set fixed domain words; 39 signs DataID 0090; 10 arms trailer.
 */
    .section .text
    .global _helper_entry
_helper_entry:
    prepare {r20-r23,lp}, 0
    ld.bu 0x4844[gp], r6
    cmp r0, r6
    be .L_parse
    ld.bu -0x6c35[gp], r6
    ld.bu 0x4850[gp], r7
    cmp r6, r7
    bne .L_parse
    ld.bu -0x6c34[gp], r6
    ld.bu 0x4851[gp], r7
    cmp r6, r7
    bne .L_parse
    ld.bu -0x6c33[gp], r6
    ld.bu 0x4852[gp], r7
    cmp r6, r7
    bne .L_parse
    ld.bu -0x6c32[gp], r6
    ld.bu 0x4853[gp], r7
    cmp r6, r7
    bne .L_parse
    movea -0x6c51, gp, r6
    movea 0x4854, gp, r7
    movea 32, r0, r8
.L_copy_route40:
    ld.bu 0[r6], r9
    st.b r9, 0[r7]
    add 1, r6
    add 1, r7
    add -1, r8
    cmp r0, r8
    bne .L_copy_route40
    ld.bu -0x64a0[gp], r6
    st.b r6, 0x4846[gp]
    st.b r0, 0x4844[gp]
    movea 1, r0, r6
    st.b r6, 0x4845[gp]

.L_parse:
    ld.hu -0x6bcc[gp], r6
    mov 0xf500, r7
    cmp r6, r7
    bne .L_return
    ld.bu -0x6bca[gp], r6
    ld.bu 0x4805[gp], r7
    cmp r6, r7
    be .L_return
    st.b r6, 0x4805[gp]
    ld.bu -0x6bc9[gp], r7
    addi -0x10, r7, r8
    cmp r0, r8
    be .L_arm
    addi -0x20, r8, r8
    cmp 8, r8
    bnh .L_set_word
    addi -9, r8, r8
    cmp r0, r8
    be .L_execute
    br .L_return

.L_arm:
    ld.w -0x6bc8[gp], r6
    st.w r6, 0x4850[gp]
    st.b r0, 0x4845[gp]
    movea 1, r0, r6
    st.b r6, 0x4844[gp]
    br .L_return

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
    br .L_return

.L_execute:
    ld.hu 0x4808[gp], r6
    addi -0x1ff, r6, r0
    bne .L_return
    ld.hu 0x4810[gp], r6
    mov 0x9000, r7
    cmp r6, r7
    bne .L_return
    movea 1, r0, r6
    st.b r6, 0x4806[gp]
    st.b r0, 0x4807[gp]
    st.w r6, 0x4848[gp]
    movea 4, r0, r8
    st.w r8, 0x484c[gp]
    movea 0x4810, gp, r6
    st.w r6, 0x5ba4[gp]
    movea 0x24, r6, r7
    movea 0x4848, gp, r8
    st.w r8, 0x5ba0[gp]
    movea 36, r0, r8
    st.w r8, 0x5ba8[gp]
    movea 16, r0, r8
    st.w r8, 0x480c[gp]
    movea 0x480c, gp, r8
    movea 1, r0, r9
    mov 0, r6
    jarl32 command5_sync, lp
    st.b r10, 0x4807[gp]
    ld.bu 0x5bbd[gp], r6
    st.b r6, 0x480a[gp]
    ld.bu 0x5bbc[gp], r6
    st.b r6, 0x480b[gp]
    movea 2, r0, r6
    st.b r6, 0x4806[gp]

.L_return:
    dispose 0, {r20-r23,lp}, lp
