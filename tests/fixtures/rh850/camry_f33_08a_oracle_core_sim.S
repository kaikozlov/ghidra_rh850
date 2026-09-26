#include "../../../exploit/ephemeral_runtime/camry_f33_08a_classic_oracle_core.inc"

    .section .text
    .global _start
_start:
    movhi 0xFEBF, r0, sp
    movea 0x7ff0, sp, sp
    /* GNU sim/v850 does not execute the RH850 jarl32 extension correctly;
       keep simulator-only harness calls in the ordinary near JARL form. */
    jarl _oracle_core_sim_main, lp
    .global rh850_sim_stop
rh850_sim_stop:
    br rh850_sim_stop

    .global _oracle_sim_fragment
_oracle_sim_fragment:
    prepare {r20-r23,lp}, 0
    mov r7, r22
    mov r8, r23
    mov r6, r7
    ORACLE_CORE_ASSEMBLE_FRAGMENT .L_sim_fragment_partial, .L_sim_fragment_reset
    movea 1, r0, r10
    br .L_sim_fragment_done
.L_sim_fragment_partial:
    mov 0, r10
    br .L_sim_fragment_done
.L_sim_fragment_reset:
    st.b r0, 7[r22]
    movea 2, r0, r10
.L_sim_fragment_done:
    dispose 0, {r20-r23,lp}, lp

    .global _oracle_sim_freshness
_oracle_sim_freshness:
    prepare {r20-r23,lp}, 0
    mov r6, r22
    mov r7, r23
    mov r8, r12
    mov r9, r13
    ORACLE_CORE_ADVANCE_FRESHNESS
    mov r14, r10
    dispose 0, {r20-r23,lp}, lp

    .global _oracle_sim_response
_oracle_sim_response:
    prepare {r20-r23,lp}, 0
    mov r6, r22
    mov r7, r23
    mov r8, r20
    ld.w 0[r9], r10
    ld.bu 4[r9], r6
    ld.bu 5[r9], r7
    ld.bu 6[r9], r8
    ORACLE_CORE_PACK_RESPONSE
    mov r21, r10
    dispose 0, {r20-r23,lp}, lp
