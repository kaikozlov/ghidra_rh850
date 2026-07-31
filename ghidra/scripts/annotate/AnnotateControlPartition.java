//@author kaikozlov
//@category Analysis
// Correct cyclic-partition labels and annotate the protected command and
// independently recovered motor-control/PWM paths.
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
            "Convert FEBEBF80 to signed 16-bit range, rate-limit against prior FEBEBF9A using calibration 1BD8E, and write conditioned command state FEBEBF9A/FEBEBF84 plus derived bounded state FEBEBFA2. No static edge from these states to the independently recovered d/q current references is established.");
        fn(0xCB700L, "steering_command_export_scale",
            "Scale command-derived state FEBEBFA2 by gain FEBEAE3C and write application export FEBEAE16. Snapshot/transport consumers copy it to FEBEE8CA/FEBEEB1C/FEBEEBA4; none is a recovered current-reference consumer.");

        fn(0x6578EL, "tauj0_ch0_sample_snapshot",
            "TAUJ0 CH0 sample snapshot. Calls the two indexed peripheral-result readers and copies their sampled banks into FEBE5EA0..FEBE5EB6 before the phase-current pipeline.");
        fn(0x4FB02L, "dual_motor_phase_sample_publish",
            "Publish two three-phase raw-sample sets and paired offset/zero samples from FEBE5EA0..FEBE5EB6 into FEBE81E4..FEBE81FA.");
        fn(0x47C3CL, "dual_motor_phase_current_conditioning",
            "High-rate TAUJ0 CH0 step reached through both transition dispatcher 5CC08 and steady dispatcher 5CE0C. Offset/gain-condition two U/V/W phase-current sample sets, saturate them, and reconstruct missing-phase values into FEBE7DE6..FEBE7DF0; not calibration-only.");
        fn(0x35960L, "dual_motor_clarke_park_feedback",
            "Transform two conditioned U/V/W phase-current sets into rotating-frame feedback using coefficient pairs FEBE7CEE/7CF0 and FEBE7CFA/7CFC and fixed-point constants 3441/5A82.");
        fn(0x37644L, "dual_motor_dq_feedback_combine",
            "Combine the two transformed feedback banks into bounded d/q feedback state at FEBE6D18/FEBE6D1C and paired intermediate state.");
        fn(0x37712L, "dual_motor_dq_current_reference",
            "Construct bounded d/q current-reference state at FEBE6D28/FEBE6D2A from upstream CH0 control state and calibration 1842C/1842E. No static edge from the authenticated 2E4 command snapshots is established.");
        fn(0x36902L, "dq_current_pi_axis_a",
            "PI-like saturated current-control loop over reference FEBE6D2A minus feedback FEBE6D1C, using gain/limit block 18334..18340.");
        fn(0x36A44L, "dq_current_pi_axis_b",
            "PI-like saturated current-control loop over reference FEBE6D28 minus feedback FEBE6D18, using gain/limit block 18344..1834C.");
        fn(0x36742L, "dual_motor_rotating_frame_command_limit",
            "Combine current-loop-derived bounded state and motor coefficient state into two rotating-frame command pairs FEBE6BE8..FEBE6BEE for inverse transformation.");
        fn(0x38464L, "motor0_inverse_rotating_frame_transform",
            "Rotate command pair FEBE6BE8/6BEA into bounded three-phase command triplet FEBE6E10/12/14.");
        fn(0x38554L, "motor1_inverse_rotating_frame_transform",
            "Rotate command pair FEBE6BEC/6BEE into bounded three-phase command triplet FEBE6E18/1A/1C.");
        fn(0x3875AL, "dual_motor_phase_duty_publish",
            "Finalize two three-phase command triplets and publish them through output-arbitration slot writer 56B18.");
        fn(0x569A8L, "dual_motor_phase_duty_select",
            "Select one enabled arbitration slot for each three-phase output bank and publish normalized commands at FEBE8BA2..FEBE8BAC.");
        fn(0x60BFAL, "tsg3_phase_compare_compute",
            "Convert one selected normalized three-phase command bank into staged TSG3 compare values using timer period/scaling state.");
        fn(0x60DDCL, "tsg3_pwm_compare_commit",
            "At the start of TAUJ0 CH0 work, commit the previously staged W/V/U values to TSG30/31 CMPWE/CMPVE/CMPUE at FFE70180/184/188 and FFE71180/184/188. These are physical HT-PWM compare registers, not proof that authenticated 2E4 controls them.");
        fn(0x5D18CL, "tauj0_ch0_motor_control_worker",
            "High-rate CH0 worker that orders d/q feedback and reference preparation, PI-like current loops, inverse rotating-frame transforms, phase-duty publication/selection, and TSG3 compare computation.");
    }
}
