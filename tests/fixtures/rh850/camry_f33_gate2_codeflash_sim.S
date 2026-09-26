    .section .sim.harness,"ax"
    .global codeflash_sim_start
codeflash_sim_start:
    mov 0xfebeb800, gp
    mov 0xfebe2000, sp

    /* Poison outputs so an unvisited call boundary cannot look successful. */
    mov 0xfef01000, r11
    mov 0xbad00001, r10
    st.w r10, 0[r11]
    st.w r10, 4[r11]
    st.w r10, 8[r11]

    mov 2, r6
    jarl32 gate2_entry, lp

    mov 0xfef01000, r11
    st.w r10, 0[r11]
    .global codeflash_sim_stop
codeflash_sim_stop:
    br codeflash_sim_stop

    .equ gate2_entry, 0x0008f906

    /* External callees are explicit ABI boundary models.  Their section bytes
       are overlaid onto a private image copy after exact preimage checks. */
    .section .sim.overlay.f202,"ax"
    mov 0, r10
    jmp [lp]

    .section .sim.overlay.f8d2,"ax"
    mov 0xfef01004, r11
    st.w r7, 0[r11]
    st.w r26, 4[r11]
    jmp [lp]

    .section .sim.overlay.f4d0,"ax"
    jmp [lp]

    .section .sim.overlay.f546,"ax"
    movea 0x333, r0, r10
    jmp [lp]

    .section .sim.overlay.f60e,"ax"
    movea 0x222, r0, r10
    jmp [lp]

    .section .sim.overlay.f70e,"ax"
    jmp [lp]
