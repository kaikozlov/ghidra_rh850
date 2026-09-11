/* Exact-F33 non-mutating ingress observer for the live-qualified high-tail
 * loader.  The resident calls this immediately after 0x79EDE drains the
 * software RX ring and before the untouched 0x7A272 tail reaches SecOC.
 *
 * Host-visible telemetry at FEBF0268 (exactly 32 bytes):
 *   +00 observation_count
 *   +04 D7_queue32_count
 *   +08 B6_queue32_count
 *   +0C ID63_marker_count
 *   +10 B0..B11 || B28..B31 of the last ID63 B6
 *
 * This helper only reads receive state and writes its private telemetry.  It
 * does not change the B6 queue, SecOC state, COM, CAN, MMIO, or flash.
 */
    .section .text
    .global _helper_entry
_helper_entry:
    prepare {lp}, 0

    ld.w 0x4a68[gp], r6
    add 1, r6
    st.w r6, 0x4a68[gp]

    ld.hu -0x638e[gp], r6      /* FEBE5472: native D7 queue length */
    addi -0x20, r6, r7
    cmp r0, r7
    bne .L_b6
    ld.w 0x4a6c[gp], r6
    add 1, r6
    st.w r6, 0x4a6c[gp]

.L_b6:
    ld.hu -0x6386[gp], r6      /* FEBE547A: protected B6 queue length */
    addi -0x20, r6, r7
    cmp r0, r7
    bne .L_return
    ld.w 0x4a70[gp], r6
    add 1, r6
    st.w r6, 0x4a70[gp]

    ld.bu -0x6329[gp], r6      /* FEBE54D7: application B3 */
    andi 0x3f, r6, r6
    addi -0x3f, r6, r7
    cmp r0, r7
    bne .L_return
    ld.w 0x4a74[gp], r6
    add 1, r6
    st.w r6, 0x4a74[gp]

    ld.w -0x632c[gp], r6       /* B0..B3 */
    st.w r6, 0x4a78[gp]
    ld.w -0x6328[gp], r6       /* B4..B7 */
    st.w r6, 0x4a7c[gp]
    ld.w -0x6324[gp], r6       /* B8..B11 */
    st.w r6, 0x4a80[gp]
    ld.w -0x6310[gp], r6       /* B28..B31 */
    st.w r6, 0x4a84[gp]

.L_return:
    dispose 0, {lp}, lp
