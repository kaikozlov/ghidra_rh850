//@author kaikozlov
//@category Analysis
// Name and document the 24 largest unnamed functions (>= 1024 bytes) by role.
// Classifications are derived from decompiled code structure, call-graph tracing,
// memory-access patterns, and caller context — verified against the actual binary.
// See docs/LARGE_FUNCTIONS_ANALYSIS.md for the full evidence.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;

public class AnnotateLargeFunctions extends GhidraScript {
    private void renameFunction(long addr, String name, String comment) throws Exception {
        Address a = toAddr(addr);
        Function f = currentProgram.getFunctionManager().getFunctionAt(a);
        if (f == null) throw new IllegalStateException("no function at " + a + " for " + name);
        f.setName(name, SourceType.USER_DEFINED);
        currentProgram.getListing().setComment(a, CodeUnit.PLATE_COMMENT, comment);
        println(String.format("function 0x%x -> %s", addr, name));
    }

    @Override
    public void run() throws Exception {

        // ── Boot / reset ───────────────────────────────────────────────

        renameFunction(0x1F2L, "boot_reset_startup",
            "Hardware reset entry point. Sets gp=0xFEBF9800, tp=0x869C (boot EIINT table), " +
            "sp=0xFEBE8000. Initializes system registers then enters boot decision logic. " +
            "The 'unreachable block' warnings are intentional: RAM-init code at 0x44C/0x460/0x670 " +
            "is only reachable from the power-on path, not from Ghidra's analysis entry.");

        renameFunction(0x7059EL, "boot_shutdown_reset_path",
            "Non-returning reset/shutdown path. Checks boot-state marker at FEBF3401, " +
            "writes watchdog/reset registers, and calls system_hard_reset. Reached when " +
            "the boot validity gate or flash operation requires a controlled reset. " +
            "Called by application_ecm_maskable_isr. 18 SFR references.");

        // ── Application AES (separate from bootloader AES) ─────────────

        renameFunction(0x853EEL, "app_aes128_ecb_decrypt_block",
            "Application AES-128 single-block decrypt (10 inverse rounds, 4582 bytes). " +
            "Uses Td tables at 0x24628 and inverse S-box at 0x25628. Called only by " +
            "app SA stage-1 (0x8C7BC). The application has its own copy of the AES " +
            "primitives at 0x84xxx, separate from the bootloader's at 0x73xx-0x76xx.");

        renameFunction(0x8496CL, "app_aes128_encrypt_round",
            "Application AES-128 encrypt round function (2372 bytes). Uses Te tables " +
            "at 0x23628 and forward S-box at 0x8FF1. Called only by the app SA stage-2 " +
            "wrapper (0x852B0). Separate from the bootloader's aes128_ecb_encrypt_block " +
            "at 0x7352.");

        // ── AUTOSAR RTE / generated task bodies ───────────────────────

        renameFunction(0x58404L, "autosar_os_task_signal_dispatch",
            "Generated AUTOSAR Os task body (12894 bytes, largest function in the image). " +
            "Flat sequential call sequence: 352 unique jarl calls, zero forward conditional " +
            "branches, zero switch statements. Calls each configured COM signal processing " +
            "runnable in fixed declaration order. 241 of 352 callees are 2-byte empty stubs. " +
            "Called from FUN_00057778 which is a periodic dispatcher registered during init " +
            "(application_startup_coordinator -> 0x65626 -> 0x57768 -> 0x57778). Also reached " +
            "cyclically: 0x64FCC -> 0x65750 -> 0x57AC2 ->[CRC gate]-> 0x577D0 -> 0x57778. " +
            "Not the foreground loop itself (that is application_foreground_cyclic_loop " +
            "at 0x64FCC).");

        renameFunction(0x5DB6EL, "autosar_com_rx_dispatch_group_a",
            "Generated AUTOSAR COM receive dispatch group A (2136 bytes). Calls " +
            "application_unpack_can_2e4 and 269 unique sub-functions. Flat call sequence " +
            "that unpacks CAN signals from a group of PDUs and routes them to consumers. " +
            "Called from foreground cyclic loop via 0x65750 -> 0x57AC2.");

        renameFunction(0x5D3CEL, "autosar_com_rx_dispatch_group_b",
            "Generated AUTOSAR COM receive dispatch group B (1078 bytes). Calls 146 unique " +
            "sub-functions. Second cluster of COM signal unpackers. Called from TAUJ0 CH2 " +
            "timer interrupt via application_tauj0_ch2_body (0x64FB0) -> 0x65720 -> 0x579B4.");

        // ── AUTOSAR COM signal deadline monitors ──────────────────────
        // These manage signal lifecycle states (0x11=received, 0x22=timeout,
        // 0x33/0x44=marked) and dispatch callbacks through function-pointer tables.
        // Type propagation fails because of the indirect calls.

        renameFunction(0x69824L, "com_signal_deadline_monitor_a",
            "AUTOSAR COM signal deadline/timeout monitor (1352 bytes). Manages signal " +
            "lifecycle states (0x11=alive, 0x22=timeout, 0x33/0x44=marked) through a " +
            "15-slot function-pointer table (param_3[0]..param_3[0xe]). Type propagation " +
            "does not settle due to indirect dispatch. Called by 8 functions in the " +
            "0x3Cxxx-0x45xxx range.");

        renameFunction(0x6AD24L, "com_signal_deadline_monitor_b",
            "AUTOSAR COM signal deadline monitor variant B (1444 bytes). Same lifecycle " +
            "pattern as 0x69824 with 31 indirect calls. Called by 8 functions in the " +
            "0x45xxx-0x46xxx range.");

        renameFunction(0x69DECL, "com_signal_deadline_monitor_c",
            "AUTOSAR COM signal deadline monitor variant C (1182 bytes). 33 indirect calls. " +
            "Called by 8 functions.");

        renameFunction(0x6A28AL, "com_signal_deadline_monitor_d",
            "AUTOSAR COM signal deadline monitor variant D (1208 bytes). 28 indirect calls. " +
            "Called by 8 functions in the COM receive chain.");

        // ── AUTOSAR RTE input staging (pure data copies) ──────────────

        renameFunction(0x5C666L, "rte_input_staging_copy_a",
            "AUTOSAR RTE-generated input staging copy (1442 bytes). 220 field-by-field " +
            "copies from scattered Rte buffers (0xFEBE6800-0xFEBEE600) into a contiguous " +
            "runnable input struct at 0xFEBE6400-0xFEBE676F. Zero ifs, zero calls, zero " +
            "computation. Called inside critical section (interrupt mask 0xFF00) within " +
            "FUN_00057a7e under the E2E config-management cyclic.");

        renameFunction(0x5C0B6L, "rte_input_staging_copy_b",
            "AUTOSAR RTE-generated input staging copy (1204 bytes). 189 field copies into " +
            "0xFEBE6400-0xFEBE6600. Zero logic. Called inside critical section (mask 0xFFC0), " +
            "executed before 0x5C666.");

        renameFunction(0x5B9C4L, "rte_input_staging_copy_c",
            "AUTOSAR RTE-generated input staging copy (1250 bytes). 192 field copies into " +
            "0xFEBE6200-0xFEBE6400. Zero logic. Called inside critical section (mask 0xFFC0) " +
            "within FUN_00057980, invoked from both TAUJ0 CH2 ISR and foreground cyclic.");

        // ── Boot-time initialization ──────────────────────────────────

        renameFunction(0xBD10EL, "eps_subsystem_init_orchestrator",
            "EPS subsystem initialization orchestrator (5404 bytes). Boot-time one-shot. " +
            "Zero ifs, zero switches, 101 sequential init-helper calls (FUN_b00xx-b7xxx) " +
            "and 1773 RAM assignments. Called from application_startup_coordinator via " +
            "0x65626 -> 0x57768 -> 0x57778 -> 0xFDC14. Likely AUTOSAR EcuM/BswM " +
            "InitRunnable or hand-written Eps_Init(). Not cyclic, not motor computation.");

        renameFunction(0x57BFEL, "application_ram_default_init",
            "Application RAM default-value initializer (2054 bytes). Boot-time one-shot. " +
            "Zero ifs, zero calls — pure assignment block initializing 588 RAM locations " +
            "(0xFEBE6E50-0xFEBE8130 region) with default constants (0, 1, 0x5A, 0xFF, " +
            "0x3480, 0x1A6F, 0x8000, 0xFFFF). Called from init path 0x5778C.");

        renameFunction(0x61DD4L, "application_peripheral_init",
            "Application peripheral initialization (1096 bytes). Writes 233 hardware " +
            "registers (SFRs) to configure clock, timer, ADC, port, and communication " +
            "peripherals. Called by application_startup_coordinator. Writes 0xCF to " +
            "multiple FFFEEAxx port configuration registers.");

        // ── Hand-written OEM motor control ─────────────────────────────
        // 0x47C3C has transition and steady CH0 dispatchers. Stage 6 further
        // recovered the exact version-domain dispatch around the two calibration
        // handlers below; neither is "transition-only".

        renameFunction(0x47C3CL, "dual_motor_phase_current_conditioning",
            "Hand-written OEM dual-motor 3-phase current conditioning step (1632 bytes). " +
            "Contains real fixed-point math: 60 longlong multiplies with saturation " +
            "to 0x7FFF/-0x7FFF, 91 conditional branches, per-phase gain selection. " +
            "Reads 3-phase values from 0xFEBE81E4-0xFEBE81F4, gain table from " +
            "0xFEBE68DE-0xFEBE6900, thresholds from calibration block at CodeFlash " +
            "0x1875x. Reached through transition dispatcher 0x5CC08 and steady " +
            "dispatcher 0x5CE0C from the TAUJ0 CH0 high-rate path.");

        renameFunction(0x32B80L, "motor_coord_transform_calib_handler",
            "Hand-written OEM coordinate-transform/filter calibration handler (1560 bytes). " +
            "Fixed-point matrix math: 6-channel gain multiplication with 64-bit multiply " +
            "and saturation, d/q axis decomposition pattern, Q15 rescale (/ 0x8000), " +
            "low-pass filter with coefficient from calibration at CodeFlash 0x31044. " +
            "Outputs 12 transformed channels + 3 filtered values. Calibration block " +
            "at 0x3103x. Reached as state 0x33 of the 0x33198 six-channel calibration " +
            "state machine; CH0 transition/steady dispatchers select that state machine " +
            "for version domains 0x512 and 0x600.");

        renameFunction(0xB98BCL, "motor_rotor_observer_calib_handler",
            "Hand-written OEM rotor position/speed observer calibration handler (1040 bytes). " +
            "Heavy calibration dependence: ~20 values from CodeFlash 0x1A12x-0x1A15x " +
            "(thresholds, gains, filter coefficients, limits). Calls atan2/sqrt (0xCCCAx), " +
            "abs/clip (0xCBABA), interpolation (0xCC638), and DTC setters. Outputs observer " +
            "state to 0xFEBEB5C4-0xFEBEB5EC. Reached from TAUJ0 CH2 in version domain " +
            "0x200..0x522 through both transition wrapper 0xBEB44 (via 0xFDD18) and " +
            "steady wrapper 0xBEBF6 (via 0xFDD2C).");

        // ── System mode coordination ──────────────────────────────────

        renameFunction(0xBEC4CL, "system_mode_per_tick_dispatcher",
            "System mode per-tick subsystem dispatcher (1330 bytes). Full variant that " +
            "knows old+new mode and runs band-entry init. Calls application_input_snapshot_update, " +
            "application_system_transition_phase_step, and tail-calls system_mode_coordinator. " +
            "Wiring only — does not decide mode transitions.");

        renameFunction(0xBA43AL, "system_mode_telemetry_snapshot",
            "System mode telemetry snapshot copier (2732 bytes). ~200-field telemetry copy " +
            "with one mode-0x400 conditional. Does not decide mode transitions. Called by " +
            "system_mode_per_tick_dispatcher (0xBEC4C) and FUN_000BF17E.");

        renameFunction(0xCBCC8L, "application_substate_machine",
            "Application-level table-driven substate machine (1182 bytes). Uses transition " +
            "codes 0x11/0x22/0x33/0x44 for sequencing, independent of the system-mode enum. " +
            "Reached only when dispatcher flag bit 0x10 is set. Called by FUN_000B893E.");

        // ── Hardware / misc ───────────────────────────────────────────

        renameFunction(0x48312L, "hardware_register_access_helper",
            "Hardware register access helper (2044 bytes). 12 SFR references. Called by " +
            "the CAN signal processing chain (0x5D3CE/0x5D94E). Provides register-level " +
            "I/O for peripheral configuration during signal processing.");
    }
}
