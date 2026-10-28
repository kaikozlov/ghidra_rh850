/*
 * Shared TSS3 foreground resident: architectural entry glue only.
 *
 * The application CPU context (GP/TP/SP/EBASE/INTBP) must be installed before
 * any compiled prologue or stack access, so this stub calls the config's
 * context initializer first, then enters the C startup walker in
 * tss3_request_signer_resident.c. Section .text.entry keeps the stub at the
 * exact resident entry address; the startup walker lives in .text.startup and
 * the live loop in .text, beyond the state prefix reclaimed after startup.
 */
#ifndef ORACLE_CONFIG_BASE
#error ORACLE_CONFIG_BASE is required
#endif

    .section .text.entry
    .global _resident_entry
_resident_entry:
    mov ORACLE_CONFIG_BASE, r24
    ld.w CFG_APP_CONTEXT[r24], r12
    jarl [r12], lp
    /* The context initializer changed the register environment; the C body
       re-materializes the config pointer itself, so enter it directly. */
    jr _resident_startup
