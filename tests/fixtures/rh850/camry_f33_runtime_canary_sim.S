    .section .sim.harness,"ax"
    .global codeflash_sim_start
codeflash_sim_start:
    mov 0xfebe2000, sp
    jr32 resident_entry

    .global codeflash_sim_stop
codeflash_sim_stop:
    br codeflash_sim_stop

    .equ resident_entry, 0xfebf0000

    .macro RETURN_STUB name
    .section .sim.overlay.\name,"ax"
    jmp [lp]
    .endm

    /* Boot transition boundaries. */
    RETURN_STUB boot_c9a
    RETURN_STUB boot_e54
    RETURN_STUB boot_f80
    RETURN_STUB boot_10c6

    .section .sim.overlay.validity,"ax"
    mov 0, r10
    jmp [lp]

    /* Model only privileged context installation.  The resident then reads the
       real startup JARLs and invokes their original CodeFlash targets. */
    .section .sim.overlay.context,"ax"
    mov 0xfebeb800, gp
    mov 0x00023dfc, tp
    mov 0xfebe2000, sp
    mov 0x43545831, r10
    mov 0xfef01000, r11
    st.w r10, 0[r11]
    jmp [lp]

    /* startup_00 @ 0x632B2 remains real CodeFlash and clears FEBE7000..7FFF. */
    RETURN_STUB startup_01
    RETURN_STUB startup_02
    RETURN_STUB startup_03
    RETURN_STUB startup_04
    RETURN_STUB startup_05
    RETURN_STUB startup_06
    RETURN_STUB startup_07
    RETURN_STUB startup_08
    RETURN_STUB startup_09
    RETURN_STUB startup_10
    RETURN_STUB startup_11
    RETURN_STUB startup_12
    RETURN_STUB startup_13
    RETURN_STUB startup_14
    RETURN_STUB startup_15
    RETURN_STUB startup_16
    RETURN_STUB startup_17
    RETURN_STUB startup_18
    RETURN_STUB startup_19
    RETURN_STUB startup_20

    .section .sim.overlay.startup_final,"ax"
    mov 0x53544152, r10
    mov 0xfef01004, r11
    st.w r10, 0[r11]
    jmp [lp]

    RETURN_STUB fg_pre_0
    RETURN_STUB fg_pre_1
    RETURN_STUB fg_pre_2
    RETURN_STUB fg_pre_3

    .section .sim.overlay.fg_aggregate,"ax"
    mov 0x46475231, r10
    mov 0xfef01008, r11
    st.w r10, 0[r11]
    jmp [lp]

    RETURN_STUB fg_post_1
