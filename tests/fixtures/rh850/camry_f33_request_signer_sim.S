    .section .sim.harness,"ax"
    .global codeflash_sim_start
codeflash_sim_start:
    mov 0xfebe2000, sp
    jr32 exploit_entry

    .global codeflash_sim_stop
codeflash_sim_stop:
    br codeflash_sim_stop

    .equ exploit_entry, 0xfebf0000

    .macro RETURN_STUB name
    .section .sim.overlay.\name,"ax"
    jmp [lp]
    .endm

    RETURN_STUB boot_c9a
    RETURN_STUB boot_e54
    RETURN_STUB boot_f80
    RETURN_STUB boot_10c6

    .section .sim.overlay.validity,"ax"
    mov 0, r10
    jmp [lp]

    .section .sim.overlay.context,"ax"
    mov 0xfebeb800, gp
    mov 0x00023dfc, tp
    mov 0xfebe2000, sp
    mov 0x43545831, r10
    mov 0xfef01000, r11
    st.w r10, 0[r11]
    jmp [lp]

    /* startup_00 remains real CodeFlash; the remaining hardware initializers
       return so the resident's decoded JARL walk itself is exercised. */
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

    RETURN_STUB fg_timing_begin
    RETURN_STUB fg_pre_0
    RETURN_STUB fg_pre_1
    RETURN_STUB fg_pre_2
    RETURN_STUB fg_pre_3
    RETURN_STUB fg_aggregate
    RETURN_STUB fg_post_1
    RETURN_STUB fg_timing_end
