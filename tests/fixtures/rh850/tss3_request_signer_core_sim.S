/*
 * Minimal RH850 simulator entry for the TSS3 request-signer core fixture.
 * All signer logic under test lives in the C core linked from
 * tests/fixtures/rh850/tss3_request_signer_core_sim.c; only the initial
 * stack and simulator stop label belong here.
 */

    .section .text
    .global _start
_start:
    movhi 0xFEBF, r0, sp
    movea 0x7ff0, sp, sp
    jarl32 _oracle_core_sim_main, lp
    .global rh850_sim_stop
rh850_sim_stop:
    br rh850_sim_stop
