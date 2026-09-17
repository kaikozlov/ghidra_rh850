/*
 * Exact-F33 one-shot native-CAN 0x08A forwarding discriminator.
 *
 * The host may load exactly one 32-byte frame through the already-observed
 * extended-CAN staging cell.  The helper then calls the stock lower CAN writer
 * using the normal F33 CAN-FD HTH and CAN ID 0x08A.  The intended host workflow
 * loads a byte-exact, freshly captured stock 0x08A whose Target Lateral ID is 0;
 * the helper independently rejects any frame with nonzero B21[5:0].
 *
 * Control frame (extended 0x1FDC0002, classic CAN):
 *   B0=00 B1=C8 B2=sequence B3=opcode B4..B7=argument LE
 *   opcode 40..47: set complete-frame word 0..7
 *   opcode 48:     transmit once after all eight words are present
 *
 * Mailbox FEBF0000..FEBF003B:
 *   +00 magic "8ATX" / 0x58544138
 *   +04 version, +05 last sequence, +06 state, +07 lower-driver return code
 *   +08 input bitmap (low 8 bits), +0A enqueue count, +0B completion count
 *   +0C successor pending-handle observed after our 0x00F0 leaves the HTH
 *   +10 frame[32]
 *   +30 AUTOSAR Can_PduType used only for the one-shot lower-driver call
 *
 * state: 0 assembling, 1 lower-driver busy/retryable, 2 Tx pending, 3 Tx
 * completed, 4 terminal error.  A successful enqueue permanently closes
 * mutation/transmit for
 * this application boot.  No command-5 operation, SecOC bypass, steering B6
 * path, or flash write exists here.
 */

    .section .text
    .global _helper_entry
_helper_entry:
    prepare {r20-r21,lp}, 0

    /* Once the lower driver accepts the frame, do not parse any more control.
       Exact F33 HTH0 is lower object 47; its pending software handle is
       FEBE502A.  The stock Tx completion path removes our 0x00F0 before
       dispatching its no-op confirmation. Because stock 0x030 shares this HTH,
       it may enqueue again before our next 5-ms observation; any value other
       than our unique 0x00F0 therefore proves our pending ownership ended. */
    ld.bu 0x4806[gp], r6
    cmp 2, r6
    bne .L_init
    ld.hu -0x67d6[gp], r6
    movea 0x00f0, r0, r7
    cmp r6, r7
    be .L_return
    st.h r6, 0x480c[gp]       /* idle FFFF or successor stock PDU handle */
    movea 1, r0, r6
    st.b r6, 0x480b[gp]       /* completion_count=1 */
    movea 3, r0, r6
    st.b r6, 0x4806[gp]       /* our Tx no longer owns HTH0 */
    br .L_return

.L_init:
    ld.w 0x4800[gp], r6
    mov 0x58544138, r7
    cmp r6, r7
    be .L_parse
    st.w r7, 0x4800[gp]
    movea 1, r0, r6
    st.w r6, 0x4804[gp]       /* version=1; seq/state/rc start zero */
    st.w r0, 0x4808[gp]       /* bitmap / tx_count / reserved */

.L_parse:
    ld.bu 0x480a[gp], r6      /* accepted enqueue permanently closes probe */
    cmp r0, r6
    bne .L_return

    ld.hu -0x6bcc[gp], r6     /* FEBE4C34 B0:B1 */
    mov 0xc800, r7            /* bytes 00 C8 */
    cmp r6, r7
    bne .L_return
    ld.bu -0x6bca[gp], r6     /* sequence */
    ld.bu 0x4805[gp], r7
    cmp r6, r7
    be .L_return
    st.b r6, 0x4805[gp]
    ld.bu -0x6bc9[gp], r7     /* opcode */
    addi -0x40, r7, r8
    cmp 7, r8
    bnh .L_set_word
    addi -8, r8, r8
    cmp r0, r8
    bne .L_return

    ld.bu 0x4808[gp], r6
    addi -0xff, r6, r0
    bne .L_return

    /* Hard non-actuation bound: only Target Lateral ID 0 may leave EPS. */
    ld.bu 0x4825[gp], r6      /* frame B21 */
    andi 0x3f, r6, r6
    cmp r0, r6
    bne .L_terminal

    /* AUTOSAR Can_PduType: u16 swPduHandle, u8 length, pad, u32 id, data*.
       Use 0x00F0 deliberately: low-byte class F0 enters FUN_0008043c's special
       completion branch, whose exact F33 target FUN_0008152e is a no-op.  Unlike
       idle 0xFFFF, 0x00F0 also lets us observe the pending->completed transition
       in FEBE502A without forging a normal 0x030 confirmation. */
    movea 0x00f0, r0, r6
    st.h r6, 0x4830[gp]
    movea 0x20, r0, r6
    st.b r6, 0x4832[gp]
    st.b r0, 0x4833[gp]
    mov 0x4000008a, r6        /* standard CAN-FD 0x08A */
    st.w r6, 0x4834[gp]
    movea 0x4810, gp, r6
    st.w r6, 0x4838[gp]

    movea 47, r0, r6           /* HTH0 exact lower driver object ID 47 */
    movea 0x4830, gp, r7
    jarl32 lower_can_write, lp
    st.b r10, 0x4807[gp]
    cmp r0, r10
    be .L_success
    cmp 2, r10
    be .L_busy
.L_terminal:
    movea 4, r0, r6
    st.b r6, 0x4806[gp]
    br .L_return
.L_busy:
    movea 1, r0, r6
    st.b r6, 0x4806[gp]
    br .L_return
.L_success:
    movea 1, r0, r6
    st.b r6, 0x480a[gp]       /* enqueue_count=1 */
    movea 2, r0, r6
    st.b r6, 0x4806[gp]       /* pending physical Tx completion */
    br .L_return

.L_set_word:
    shl 2, r8
    movea 0x4810, gp, r6
    add r8, r6
    ld.w -0x6bc8[gp], r7      /* staging B4:B7 */
    st.w r7, 0[r6]
    shr 2, r8
    movea 1, r0, r7
    shl r8, r7
    ld.bu 0x4808[gp], r6
    or r7, r6
    st.b r6, 0x4808[gp]
    st.b r0, 0x4806[gp]
    st.b r0, 0x4807[gp]

.L_return:
    dispose 0, {r20-r21,lp}, lp
