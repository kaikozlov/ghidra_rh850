//@author kaikozlov
//@category Analysis
// Name and document the 24 largest unnamed functions (>= 1024 bytes) by role.
// Classifications are derived from decompiled call targets, memory-access
// patterns, and caller context — not from naming conventions.
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

        // ── Already-documented but unnamed in the project ──────────────

        renameFunction(0x1F2L, "boot_reset_startup",
            "Hardware reset entry point. Sets gp=0xFEBF9800, tp=0x869C (boot EIINT table), " +
            "sp=0xFEBE8000. Initializes system registers then enters boot decision logic. " +
            "The 'unreachable block' warnings are intentional: RAM-init code at 0x44C/0x460/0x670 " +
            "is only reachable from the power-on path, not from Ghidra's analysis entry.");

        renameFunction(0x853EEL, "app_aes128_ecb_decrypt_block",
            "Application AES-128 single-block decrypt (10 inverse rounds). Uses Td tables " +
            "at 0x24628 and inverse S-box at 0x25628. Called only by app SA stage-1 (0x8C7BC). " +
            "Separate from the bootloader's aes128_ecb_decrypt_block at 0x7470 — the application " +
            "has its own copy of the AES primitives at 0x84xxx.");

        renameFunction(0x8496CL, "app_aes128_encrypt_round",
            "Application AES-128 encrypt round function. Uses Te tables at 0x23628 and " +
            "forward S-box at 0x8FF1. Called only by app SA stage-2 wrapper (0x852B0). " +
            "Separate from the bootloader's aes128_ecb_encrypt_block at 0x7352.");

        // ── System mode / shutdown ─────────────────────────────────────

        renameFunction(0x7059EL, "boot_failure_shutdown_reset",
            "Non-returning reset/shutdown path. Checks boot-state marker at FEBF3401, " +
            "writes watchdog/reset registers, and calls system_hard_reset. Reached when " +
            "the boot validity gate or flash operation requires a controlled reset. " +
            "Called by application_ecm_maskable_isr.");

        renameFunction(0xBEC4CL, "system_mode_transition_step",
            "System mode coordinator transition step. Calls application_input_snapshot_update, " +
            "application_system_transition_phase_step, and system_mode_coordinator. " +
            "Manages the application-mode state machine that coordinates subsystem " +
            "shutdown/startup across mode changes (e.g. 0x300/0x400/0x500/0x900).");

        renameFunction(0xBA43AL, "system_mode_state_worker",
            "System mode coordinator state-machine worker. Called by system_mode_transition_step " +
            "(0xBEC4C) and FUN_000BF17E. Processes mode transitions and subsystem " +
            "shutdown/startup sequences.");

        // ── Hardware initialization ────────────────────────────────────

        renameFunction(0x61DD4L, "application_peripheral_init",
            "Application peripheral initialization. Writes 233 hardware registers (SFRs) " +
            "to configure clock, timer, ADC, port, and communication peripherals. " +
            "Called by application_startup_coordinator. Writes 0xCF to multiple FFFEEAxx " +
            "registers as port/pin configuration.");

        renameFunction(0x48312L, "hardware_register_access_helper",
            "Hardware register access helper. 12 SFR references. Called by the CAN " +
            "signal processing chain (0x5D3CE/0x5D94E). Provides register-level I/O " +
            "for peripheral configuration during signal processing.");

        // ── CAN signal processing ──────────────────────────────────────

        renameFunction(0x58404L, "foreground_cyclic_signal_dispatch",
            "Main foreground cyclic signal dispatcher. The largest function in the image " +
            "(12.9 KiB). Touches 182 hardware registers and calls 367 functions. Processes " +
            "application Rx/Tx CAN signals through generated COM signal consumers " +
            "(e.g. application_rx_signal_consumer_56FC2). This is the generated AUTOSAR " +
            "Os task body that cyclically processes all configured COM signals.");

        renameFunction(0x5DB6EL, "can_signal_unpack_dispatch_1",
            "CAN signal unpacking and dispatch. Calls application_unpack_can_2e4 and " +
            "application_rx_signal_consumer_56FC2. Part of the generated COM receive chain " +
            "that extracts application signals from CAN frames.");

        renameFunction(0x5D3CEL, "can_signal_unpack_dispatch_2",
            "CAN signal unpacking and dispatch. Calls application_rx_signal_consumer and " +
            "CAN unpack helpers. Second cluster of generated COM signal unpackers.");

        renameFunction(0x6AD24L, "can_signal_consumer_worker",
            "CAN signal consumer worker. Called by 8 functions in the 0x45xxx-0x46xxx range. " +
            "Processes extracted CAN signal values into application RAM.");

        renameFunction(0x69824L, "can_signal_consumer_handler",
            "CAN signal consumer handler. Called by 8 functions in the 0x3Cxxx-0x45xxx range. " +
            "Type propagation does not settle — likely a generated dispatch function with " +
            "indirect calls through function-pointer tables.");

        renameFunction(0x69DECL, "can_signal_postprocess_worker",
            "CAN signal post-processing worker. Called by 8 functions. Handles signal " +
            "validation and routing after unpacking.");

        renameFunction(0x6A28AL, "can_signal_dispatch_entry",
            "CAN signal dispatch entry point. Called by 8 functions in the COM receive chain. " +
            "Routes extracted signals to application consumers.");

        // ── Motor control / EPS application ───────────────────────────

        renameFunction(0xBD10EL, "motor_control_init_cycle",
            "Motor control initialization cycle. 209 FEBE RAM refs. Calls " +
            "application_system_transition_phase_init. Handles CAN and motor-related " +
            "state during the application initialization cycle.");

        renameFunction(0x57BFEL, "motor_control_state_machine",
            "Motor control state machine. 588 FEBE RAM refs — the heaviest RAM user " +
            "among the large functions. Processes steering torque/angle inputs and " +
            "drives motor control outputs.");

        renameFunction(0x5C666L, "motor_torque_processor",
            "Motor torque processing. 439 FEBE RAM refs. Part of the EPS motor control " +
            "chain that computes torque commands from sensor inputs.");

        renameFunction(0x5C0B6L, "motor_assist_processor",
            "Motor assist computation. 378 FEBE RAM refs. Part of the EPS motor control " +
            "chain.");

        renameFunction(0x5B9C4L, "motor_signal_processor",
            "Motor signal processing. 384 FEBE RAM refs. Processes sensor signals for " +
            "the motor control loop.");

        renameFunction(0x47C3CL, "motor_control_helper",
            "Motor control helper. 269 FEBE RAM refs. Called by the motor processing chain " +
            "(0x5CC08/0x5CE0C).");

        renameFunction(0x32B80L, "motor_output_processor",
            "Motor output processing. 92 FEBE RAM refs. Called by the motor control chain.");

        renameFunction(0xCBCC8L, "application_state_machine_worker",
            "Application state-machine worker. Called by FUN_000B893E. Processes " +
            "application-level state transitions outside the motor control domain.");

        renameFunction(0xB98BCL, "calibration_lookup_dispatch",
            "Calibration table lookup dispatch. 27 CodeFlash data refs (calibration tables). " +
            "Called by FUN_000BEB44/FUN_000BEBF6. Routes calibration parameter access.");
    }
}
