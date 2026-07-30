//@author kaikozlov
//@category Analysis
// Correct cyclic-partition labels and annotate the protected steering-command ingress.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.SourceType;

public class AnnotateControlPartition extends GhidraScript {
    private void fn(long value, String name, String comment) throws Exception {
        Address a = toAddr(value);
        Function f = currentProgram.getFunctionManager().getFunctionAt(a);
        if (f == null) throw new IllegalStateException("no function at " + a + " for " + name);
        if (!f.getName().equals(name)) f.setName(name, SourceType.USER_DEFINED);
        currentProgram.getListing().setComment(a, CodeUnit.PLATE_COMMENT, comment);
        println(a + " -> " + name);
    }

    @Override
    public void run() throws Exception {
        fn(0x68C0CL, "application_crypto_test_cyclic_step",
            "Foreground cyclic for the three dormant CAN-controlled crypto-test banks. This is not a motor-control state machine; descendants include crypto_test_bank1_state_step at 0x68BC2.");
        fn(0x68DE6L, "application_crypto_test_cyclic_finalize",
            "Foreground continuation/finalization cyclic for the dormant crypto-test banks. This is not a motor-control continuation; descendants include the bank-1 command-5 finalizer at 0x68D0E.");
        fn(0x57AC2L, "application_foreground_system_mode_dispatch",
            "Validate E2E-protected version state and dispatch full/reduced system-mode pipelines. The full path reaches the protected steering-command conditioner through FDD40 -> BEC4C -> BA43A -> CBA72 -> CB86E.");
        fn(0x6547CL, "application_timer_peripheral_reload",
            "Reload timer/peripheral MMIO blocks at FFE20000, FFE21000, and FFE50000 from calibration tables with interrupts disabled. Exact motor/PWM ownership remains unproven.");
        fn(0xBA43AL, "system_mode_input_snapshot_and_control_dispatch",
            "Snapshot and scale foreground inputs, then dispatch the control cycle through CBA72. At BA4B8..BA808, scale protected 0x2E4 command state FEBEF184 by 0x100/100 into FEBEAE20.");
        fn(0xCBA72L, "steering_control_cycle_wrapper",
            "Wrapper reached from the system-mode input snapshot; dispatch the large steering-control pipeline at 0xCB86E.");
        fn(0xCB86EL, "steering_control_cycle_pipeline",
            "Large foreground steering-control pipeline. Calls torque-command clamp/gain stage 0xC853A and saturation/rate-limit stage 0xC85B6 among many other bounded control stages.");
        fn(0xC853AL, "steering_torque_command_clamp_gain",
            "Read protected steering command snapshot FEBEAE20, clamp to calibration +/-1BD80, apply mode-indexed gain, and write gain-adjusted command FEBEBF80.");
        fn(0xC85B6L, "steering_torque_command_rate_limit",
            "Convert FEBEBF80 to signed 16-bit range, rate-limit against prior FEBEBF9A using calibration 1BD8E, and write conditioned command state FEBEBF9A/FEBEBF84. Downstream current/PWM mapping remains unresolved.");
    }
}
