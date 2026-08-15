"""Curated exploit-model constants: ingress roots, auth barriers, sinks.

Every address here is pinned by an existing verified finding or a tracked
evidence table (provenance recorded per entry). The ranking pipeline re-derives
table-driven roots from the tracked CSVs at generation time; the constants here
are the firmware-proven anchors that do not live in a machine-readable table.

Nothing in this module is a claim by itself; it is the audit's candidate lens.
"""
from __future__ import annotations

# ---------------------------------------------------------------------------
# Memory map (P1M-E device profile, verified by verify_architecture /
# processor audits).
# ---------------------------------------------------------------------------
LOCAL_RAM_LO = 0xFEBE0000
LOCAL_RAM_HI = 0xFEBFFFFF
DATAFLASH_LO = 0xFF200000
DATAFLASH_HI = 0xFF207FFF
SFR_LO = 0xFF000000  # peripheral/FCU window (DataFlash excluded below)

# COM-005: unauthenticated XCP DOWNLOAD/MODIFY_BITS write window (verified).
XCP_WRITE_WINDOW = (0xFEBF7C00, 0xFEBFFBFF)
# E4 page-copy staging destination (0x10000..0x17DEF -> RAM, verified).
XCP_E4_STAGING = (0xFEBF7C00, 0xFEBFF9EF)
# Five XCP read exclusions (verified; xcp-command-dispatch.md).
XCP_READ_EXCLUSIONS = (
    (0xFEBE0000, 0xFEBE37FF),
    (0xFEBE5030, 0xFEBE529B),
    (0xFEBF0288, 0xFEBF13CB),
    (0xFEBF4958, 0xFEBF4B33),
    (0xFEBF6C00, 0xFEBF78DF),
)

# Curated sink addresses: bytes whose write/reset is a privilege- or
# control-relevant transition (all pinned by verified findings).
SINK_ADDRESSES: dict[str, int] = {
    # SEC-BOOT-007: bootloader SA unlock byte (2 == unlocked).
    "boot_sa_unlock_byte": 0xFEBF2B0F,
    # SEC-BOOT-005: flash-driver callback pointer inside authenticated image.
    "boot_flash_driver_callback": 0xFEBF0FD0,
    # SEC-APP-007: persistent BA authorization marker.
    "ba_persistent_marker": 0xFEBE5F27,
    # COM-005: XCP memory-transfer address register.
    "xcp_mta": 0xFEBE4FF4,
    # XCP DAQ source-pointer table (WRITE_DAQ stores tester addresses here).
    "xcp_daq_pointer_table": 0xFEBE4CF0,
    # DIAG-APP-003: programming-handoff phase snapshot byte.
    "handoff_phase_snapshot": 0xFEBEE81F,
}

# ---------------------------------------------------------------------------
# External ingress roots.
#
# Roots are functions that (transitively) consume attacker-reachable frame
# bytes: CAN Rx acceptance/unpack callbacks, UDS service dispatch (both
# contexts), the XCP 0x7F7 special-route family, and the ICU-S command
# callback driver. Table-driven roots are extracted from tracked CSVs by the
# generator; the anchors below are the firmware-proven constants.
# ---------------------------------------------------------------------------
CURATED_ROOTS: dict[int, str] = {
    # Bootloader UDS dispatch and its verified service handlers.
    0x5222: "bootloader uds_service_dispatch (DIAG-BOOT-003)",
    0x5516: "bootloader SID 0x27 SecurityAccess handler (SEC-BOOT-004)",
    0x5D68: "bootloader RequestDownload (SEC-BOOT-007)",
    0x49C6: "bootloader WDBI (SEC-BOOT-007)",
    0x4B7C: "bootloader TransferData (MEM-SAFE-001)",
    0x610C: "bootloader ECUReset (SEC-BOOT-007)",
    0x567E: "bootloader SID 0x31 routine control (DIAG-BOOT-003)",
    # Application UDS SecurityAccess level-2 implementations (SEC-APP-001).
    0x8C734: "application SA level-2 seed (SEC-APP-001)",
    0x8C82A: "application SA level-2 send-key (SEC-APP-001)",
    # XCP / special CAN 0x7F7 family (COM-005 and xcp-command-dispatch.md).
    0x7FF86: "application_can_special_rx_demux for CAN 0x7F7/0x777/0x7A1/0x7A0",
    0x82042: "special-route Rx acceptance callback (CAN 0x7F7)",
    0x97160: "XCP upper command dispatcher @ table 0x2B3F0",
    0x81FE4: "XCP CTO length gate / Rx staging",
    0x80F12: "XCP DOWNLOAD (COM-005 direct RAM write)",
    0x80FD8: "XCP MODIFY_BITS (COM-005 masked RMW)",
    0x81A2E: "XCP SHORT_UPLOAD 0xF4 (direct addressed RAM read)",
    0x976F4: "XCP 0xE4 page-copy (CodeFlash -> staging)",
    0x81424: "XCP WRITE_DAQ (tester-controlled source pointers)",
    0x8206C: "XCP/0x7F8 response transmit callback",
    # ICU-S crypto-driver command ingress (MEM-SAFE-004, command-5 plumbing).
    0x89044: "ICU-S driver dispatch (unbounded zero-fill caller)",
    0x86EE8: "ICU-S command-8 failure path",
}

# ---------------------------------------------------------------------------
# Authentication barriers and SA-gated ingress.
#
# A *barrier* is the send-key success implementation: executing past it
# requires a correct key. Pre-SA reachability therefore includes the barrier
# body as a frontier but never expands through it.
#
# A *SA-gated ingress* is an external request handler whose verified semantics
# put the SecurityAccess check inside the handler body (SEC-BOOT-007), so its
# cone can only run after SA. Function-level graph search cannot see that
# internal branch; these are removed from the pre-SA root set instead.
# ---------------------------------------------------------------------------
AUTH_BARRIERS: dict[int, str] = {
    0x54DC: "bootloader SA send-key success writer of FEBF2B0F=2 (SEC-BOOT-007)",
    0x8C82A: "application SA level-2 send-key implementation (SEC-APP-001)",
}
SA_GATED_INGRESS: dict[int, str] = {
    0x5D68: "bootloader RequestDownload requires FEBF2B0F==2 (SEC-BOOT-007)",
    0x4948: "uds_write_data_by_identifier requires FEBF2B0F==2 (SEC-BOOT-007; gate instruction 0x49C6 inside body)",
    0x4B7C: "bootloader TransferData requires prior authenticated download state (SEC-BOOT-007, MEM-SAFE-001)",
    0x60C2: "uds_ecu_reset requires FEBF2B0F==2 (SEC-BOOT-007; gate instruction 0x610C inside body)",
}

# ---------------------------------------------------------------------------
# Hazard patterns over decompiled C (deterministic regexes, generated
# evidence only; they select candidates, they never prove a bug).
# ---------------------------------------------------------------------------
HAZARD_PATTERNS: dict[str, str] = {
    # Selector dispatch over an attacker-reachable parameter.
    "selector_switch": r"switch\s*\(",
    "selector_mask": r"\((?:param_\d+|u?Var\d+|i?Var\d+)\s*&\s*0x?f{2,8}\b",
    # Parameter-driven indexing (array index from a call parameter).
    "param_index": r"\[(?:param_\d+|u?Var\d+|i?Var\d+)\]|\[\(short\)(?:param_\d+|u?Var\d+)\]",
    # Truncating casts (narrowing before use in an index/length/compare).
    "narrow_cast": r"\((?:short|char|byte|uchar|ushort|uint8)\)",
    # Calls through a computed/loaded function pointer.
    "indirect_call": r"\(\s*\*\s*[^)]{1,80}\)\s*\(|->\s*\w+\s*\(",
    # Stores through a computed address expression.
    "computed_store": r"\*\([^)]{1,120}\+[^)]{0,60}\)\s*=",
    # Address-of stores (callback/pointer installation).
    "address_of_store": r"=\s*&(?:DAT|LAB|FUN|s_)",
    # Loops (dynamic-bound copy / fill candidates).
    "loop": r"\b(?:for|while)\s*\(",
    # Explicit byte/word copy helpers.
    "copy_call": r"\b\w*copy\w*\s*\(|\bmemcpy\b|\bmemset\b",
}

# Families used for cohort stratification (a function may appear in several).
FAMILIES = (
    "ingress_direct",
    "selector_dispatch",
    "computed_store",
    "indirect_call",
    "dynamic_copy",
    "mmio_flash_write",
    "persistent_transition",
    "pre_sa_write",
)
