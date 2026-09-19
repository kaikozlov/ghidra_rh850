/* Exact-F33 one-boot 0x090 signer/route40 observer carrier.
 * Install once in NRTD. After the single NRTD->READY transition and stock
 * tick 224, an authenticated GlobalRAM helper signs and observes continuously.
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
    st.b r0, 0x4804[gp]       /* helper disabled until tick-224 initialization */
    ei

    prepare {r29,lp}, 0
.L_tick_wait:
    tst1 0, 0x4804[gp]
    be .L_tick_poll
    jarl32 helper_entry, lp
.L_tick_poll:
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
    jarl32 fg_aggregate, lp
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

    tst1 7, 0[ep]
    be .L_tick_wait
    tst1 6, 0[ep]
    be .L_tick_wait
    tst1 5, 0[ep]
    be .L_tick_wait
    tst1 0, 0x4804[gp]
    bne .L_tick_wait

    movea 0x4800, gp, r6
    movea 29, r0, r7          /* clear FEBF0000..FEBF0073 */
.L_clear:
    st.w r0, 0[r6]
    add 4, r6
    add -1, r7
    cmp r0, r7
    bne .L_clear
    mov 0x52303946, r7         /* little-endian "F90R" */
    st.w r7, 0x4800[gp]
    movea 1, r0, r7
    st.b r7, 0x4804[gp]
    br .L_tick_wait
