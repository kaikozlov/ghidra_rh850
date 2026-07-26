//@author kaikozlov
//@category Analysis
// Apply application-mode DID/service/session-control findings and corrected bootloader-session labels.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;

public class AnnotateApplicationDiagnostics extends GhidraScript {
    private void fn(long value, String name, String comment) throws Exception {
        Address a=toAddr(value);
        Function f=currentProgram.getFunctionManager().getFunctionAt(a);
        if (f==null) throw new IllegalStateException("no function at "+a+" for "+name);
        if (!f.getName().equals(name)) f.setName(name,SourceType.USER_DEFINED);
        currentProgram.getListing().setComment(a,CodeUnit.PLATE_COMMENT,comment);
        println(a+" -> "+name);
    }

    private void label(long value, String name, String comment) throws Exception {
        Address a=toAddr(value);
        SymbolTable st=currentProgram.getSymbolTable();
        Symbol s=st.getPrimarySymbol(a);
        if (s!=null) {
            if (!s.getName().equals(name)) s.setName(name,SourceType.USER_DEFINED);
        } else {
            s=st.createLabel(a,name,SourceType.USER_DEFINED);
            s.setPrimary();
        }
        currentProgram.getListing().setComment(a,CodeUnit.PLATE_COMMENT,comment);
        println(a+" -> "+name);
    }

    @Override
    public void run() throws Exception {
        fn(0x4E8E4L,"application_read_f181",
            "Application-mode F181 callback. Emit count 1 and copy the 16-byte software-ID record at CodeFlash 0x20860; unlike bootloader F181, this returns the real 8965B4512000 identifier.");
        fn(0x4E90AL,"application_read_f186",
            "Application-mode F186 callback. Delegate to the application Dcm session API at 0x8FDDE.");
        fn(0x4E918L,"application_read_f18c",
            "Application-mode F18C callback. Read NvM record 0x207 and copy the serial bytes, or fill the field with '?' when the record is invalid.");

        fn(0x93FF6L,"application_session_default_callback",
            "Application DiagnosticSessionControl subfunction 0x01 wrapper; call the shared callback state machine with requested session 1.");
        fn(0x94006L,"application_session_programming_callback",
            "Application DiagnosticSessionControl subfunction 0x02 wrapper; call the shared callback state machine with requested session 2. This handles the first PROGRAMMING request before bootloader entry.");
        fn(0x94016L,"application_session_extended_callback",
            "Application DiagnosticSessionControl subfunction 0x03 wrapper; call the shared callback state machine with requested session 3.");
        fn(0x93F3CL,"application_session_callback_dispatch",
            "Dispatch application session-control operation phases: phase 0 starts, phase 2 cancels, and phase 3 polls an asynchronous transition.");
        fn(0x93D28L,"application_session_request_start",
            "Validate and begin an application session transition. Run the policy hook, resolve one of five session configs, then respond immediately or start asynchronous work with NRC 0x78.");
        fn(0x93E32L,"application_session_request_cancel",
            "Cancel/reset a pending application session transition and release its lower-layer operation state.");
        fn(0x93E72L,"application_session_request_poll",
            "Poll the asynchronous application session transition; complete, fail with an NRC, remain pending, or advance to the final transition state.");
        fn(0x8A27EL,"application_session_transition_check_adapter",
            "Read the current application Dcm session into r6, pass requested session in r7 to the policy hook at 0x4C942, and map its internal result to a UDS NRC.");
        fn(0x4C942L,"application_session_transition_policy",
            "Reject requested session 2 with internal result 0x0B / NRC 0x88 (vehicleSpeedTooHigh) when the unsigned raw speed at FEBFC892 exceeds calibration 0x0180 at CodeFlash 0x181DC. The current-session argument in r6 is not tested here.");
        fn(0x8A01CL,"application_programming_lower_request_stub",
            "Compiled lower-request stub. It accepts operation ID, status 10, payload length/data, and token pointer but returns success without using them in this image.");
        fn(0x8A08EL,"application_programming_readiness_check_adapter",
            "Run the lower programming-handoff prerequisites once. On success clear the reset-request marker and latch completion at FEBF3B18.");
        fn(0x4C960L,"application_programming_handoff_prerequisites",
            "Return failure unless system-transition phase snapshot FEBFC81F is not 0x11, scaled supply value FEBF4692 is at least calibration 0x0A00, and alternate-handoff flag FEBF6152 is clear.");
        fn(0xB28ACL,"application_system_transition_phase_init",
            "Initialize the live generated system-transition phase at FEBEB1A4 (application GP-0x65C) to zero.");
        fn(0xB2912L,"application_system_transition_phase_step",
            "Advance the generated system-transition state around modes 0x300/0x400/0x500 and event 0x23. Recovered phase markers are 0, 0x11, and 0x22; adjacent flags, not this phase byte, use 0x5A.");
        fn(0xBCB3AL,"application_input_snapshot_update",
            "Copy the broad generated application input snapshot. At BCD02..BCD06 it copies live system-transition phase FEBEB1A4 (GP-0x65C) to FEBFC81F (GP+0x301F).");
        fn(0x4C986L,"application_programming_reset_marker_clear",
            "Clear the one-request marker at FEBF6166 before the programming reset is queued.");
        fn(0x4C98CL,"application_programming_reset_request",
            "Queue system event 9 once and set marker FEBF6166 to 0x5A. Event 9 drives the system-mode coordinator into shutdown mode 0x900; the alternate FEBF6152 branch reinitializes local stacks instead.");
        fn(0x8A0C2L,"application_programming_prepare_handoff",
            "First asynchronous PROGRAMMING stage: issue compiled-stub operation 0x08000200 with no payload, validate its token, then enforce the 0x4C960 readiness conditions.");
        fn(0x8A172L,"application_programming_commit_handoff",
            "Second asynchronous PROGRAMMING stage: issue compiled-stub operation 0x08000201 with four zero bytes, validate its token, and queue the event-9 reset/shutdown handoff at 0x4C98C.");
        fn(0x8A244L,"application_session_transition_async_worker",
            "Run the two PROGRAMMING handoff stages. A successful reset request latches 0x5A and deliberately returns internal pending value 10 while shutdown/reset proceeds.");
        fn(0x93F9AL,"application_session_transition_background_poll",
            "Background continuation for the session-transition worker. Success advances the UDS state, failure emits NRC 0x22, and internal pending value 10 requeues callback ID 0x0E.");
        fn(0x8A082L,"application_session_transition_state_reset",
            "Reset the application session-transition worker state.");
        fn(0x8D5FCL,"application_internal_result_to_nrc",
            "Map application internal result values to UDS NRCs including 0x12, 0x22, 0x31, 0x72, 0x78, and standard NRC 0x88 vehicleSpeedTooHigh.");

        fn(0xB02BCL,"system_mode_event_set",
            "Set one of 50 system-mode event bits. The PROGRAMMING handoff invokes this through its thunk with event 9.");
        fn(0xB0518L,"system_mode_coordinator",
            "System-mode coordinator. Event 9 moves every active mode toward mode 0x900; mode 0x900 requests subsystem shutdown, then mode 0x800 performs final shutdown/reset sequencing.");
        fn(0xB20EAL,"system_programming_shutdown_mode_entry",
            "Entry action for system mode 0x900: write shutdown request words 0x70017001 and 0x00020002 to the paired subsystem command slots.");
        fn(0x608AAL,"system_hard_reset",
            "Final hardware-reset path reached by the shutdown coordinator: stop peripherals, program reset/watchdog registers, invoke the low-level reset helper, then loop forever.");

        fn(0x6204L,"bootloader_session_positive_response",
            "Build the queued bootloader DiagnosticSessionControl positive response 0x50, requested session, P2, and P2* timing bytes.");
        fn(0x6244L,"bootloader_session_control_task",
            "Advance an asynchronously queued bootloader session transition and emit its eventual positive response or NRC. Valid transitions do not respond directly inside 0x614A.");
        fn(0x4776L,"bootloader_main_operation_reserve",
            "Reserve the transient main-loop operation flag at FEBF2AA3 and set operation kind 2 at FEBF2AA2; return whether it was already busy. This is not a per-boot one-shot latch.");
        fn(0x479AL,"bootloader_main_operation_release",
            "Clear the transient main-loop operation flag and kind bytes. Called from main-loop task 0x137A after the flash-operation task.");
        fn(0x47ACL,"bootloader_main_operation_initialize",
            "Initialize main-loop operation kind 2 while leaving the transient busy flag clear.");

        label(0x20860L,"application_software_id_record_1",
            "First 16-byte application software-ID slot: ASCII 8965B4512000 plus four NUL bytes. Emitted by application F181 with count 1.");
        label(0x20870L,"application_software_id_record_2",
            "Second 16-byte application software-ID slot beginning with ASCII 8A311. Present in this image but not emitted by the count-1 F181 callback.");

        label(0x25E30L,"application_uds_service_table",
            "Seventeen 24-byte primary application UDS service records. SID is byte 8; configured sequence is 10,11,14,19,22,23,27,28,2E,31,34,36,37,3E,85,AB,BA.");
        label(0x25DE0L,"application_uds_service_group_directory",
            "Three 8-byte service-group descriptors: key/count/list are 2/17/25DF8, 3/6/25DC0, and 4/5/25E1C. They select primary physical 7A1, functional 777, and secondary physical 7A0 contexts.");
        label(0x25DC0L,"application_functional_service_indices",
            "Six global service-record indexes 17,2,7,9,13,14, yielding SIDs 10,14,28,31,3E,85 for functional CAN 777.");
        label(0x25DF8L,"application_primary_service_indices",
            "Seventeen indexes 0..16 selecting the primary physical 7A1 service table.");
        label(0x25E1CL,"application_secondary_service_indices",
            "Five global service-record indexes 18..22, yielding SIDs 10,19,22,3E,AB for secondary physical CAN 7A0 / response 7A8.");
        label(0x25FC8L,"application_additional_uds_service_records",
            "Six additional 24-byte service records used by limited groups 3/4. These are shared through index lists, not a standalone linear table.");
        int[] serviceSids={0x10,0x11,0x14,0x19,0x22,0x23,0x27,0x28,0x2E,0x31,0x34,0x36,0x37,0x3E,0x85,0xAB,0xBA};
        for (int i=1;i<serviceSids.length;i++) {
            long value=0x25E30L+i*24L;
            label(value,String.format("application_sid_%02x_record",serviceSids[i]),
                String.format("Application UDS service-table record for SID 0x%02X.",serviceSids[i]));
        }

        label(0x25BC0L,"application_session_subfunction_table",
            "Application SID 0x10 subfunction table and subfunction 0x01/default record; callback 0x93FF6. Rows 2/3 dispatch PROGRAMMING/EXTENDED to 0x94006/0x94016.");
        label(0x25BD0L,"application_session_programming_record",
            "Application DiagnosticSessionControl subfunction 0x02 record; callback 0x94006.");
        label(0x25BE0L,"application_session_extended_record",
            "Application DiagnosticSessionControl subfunction 0x03 record; callback 0x94016.");
        label(0x25B64L,"application_programming_allowed_sessions",
            "Two-byte current-session allow-list for DiagnosticSessionControl subfunction 0x02: PROGRAMMING (2) and EXTENDED (3). DEFAULT (1) cannot directly request PROGRAMMING.");
        label(0x262F6L,"application_session_runtime_config_table",
            "Five 10-byte session runtime records. Each begins with transition kind and session ID, followed by timing/configuration words.");
        label(0x26300L,"application_programming_runtime_config",
            "PROGRAMMING runtime record: transition kind 2, session 2, P2 value 50, additional words 5000/2000, and encoded P2* value 500 (5 seconds).");
        label(0x181DCL,"application_programming_max_speed_raw",
            "Unsigned programming-entry speed ceiling 0x0180. The same raw speed is converted elsewhere as raw*100/128, making the threshold 300 scaled units (strongly indicating 3.00 km/h).");
        label(0x181DEL,"application_programming_min_supply_raw",
            "Lower-handoff minimum supply calibration 0x0A00. Elsewhere this signal is converted as raw*10/256, making the threshold 100 scaled units (strongly indicating 10.0 V).");

        label(0x2A30CL,"application_f181_record",
            "Application DID F181 record: flags 0x0011, read callback 0x4E8E4.");
        label(0x2A31CL,"application_f186_record",
            "Application DID F186 record: flags 0x0001, read callback 0x4E90A.");
        label(0x2A32CL,"application_f18c_record",
            "Application DID F18C record: flags 0x0014, read callback 0x4E918.");

        label(0xFEBFC892L,"application_vehicle_speed_raw",
            "Unsigned speed signal tested against CodeFlash 0x181DC for PROGRAMMING entry; values above 0x0180 map to NRC 0x88 vehicleSpeedTooHigh.");
        label(0xFEBEB1A4L,"application_system_transition_phase_live",
            "Live phase byte owned by 0xB28AC/0xB2912. Recovered phase markers are 0, 0x11, and 0x22; exact OEM phase labels are unknown.");
        label(0xFEBFC81FL,"application_system_transition_phase_snapshot",
            "Snapshot copied from FEBEB1A4 by 0xBCB3A. Phase 0x11 prevents programming reset handoff and produces NRC 0x22; this is not a Dcm-produced programming-status byte.");
        label(0xFEBF4692L,"application_supply_value_raw",
            "Scaled supply signal used by the lower handoff. Values below calibration 0x0A00 prevent reset handoff and produce NRC 0x22.");
        label(0xFEBF6152L,"application_alternate_handoff_flag",
            "Flag set from the application diagnostic initialization callback. It must be clear for the normal event-9 PROGRAMMING reset path.");
        label(0xFEBF6166L,"application_programming_reset_requested",
            "One-request marker: cleared before handoff and set to 0x5A after system event 9 is queued.");
        label(0xFEBF3B14L,"application_programming_handoff_value",
            "Four-byte value passed as an all-zero payload to compiled-stub operation 0x08000201.");
        label(0xFEBF3B18L,"application_programming_readiness_latch",
            "Set to 0x5A after the lower programming readiness check succeeds.");
        label(0xFEBF3B19L,"application_programming_reset_latch",
            "Set to 0x5A after the programming reset request succeeds; subsequent worker polls remain pending until reset.");
        label(0xAEB00L,"system_mode_transition_callbacks",
            "Interleaved entry/exit callback table for system modes 0x000 through 0x900. Mode 0x900 entry pointer at 0xAEB48 is 0xB20EA.");

        label(0xFEBF2AA2L,"bootloader_main_operation_kind",
            "Transient main-loop operation kind associated with the busy byte at FEBF2AA3.");
        label(0xFEBF2AA3L,"bootloader_main_operation_busy",
            "Transient main-loop operation reservation. Set by 0x4776 and cleared by 0x479A; not a per-boot PROGRAMMING latch.");
        label(0xFEBF2B9FL,"bootloader_requested_session_raw",
            "Queued DiagnosticSessionControl subfunction byte, including suppressPosRsp bit.");
        label(0xFEBF2BA0L,"bootloader_requested_session",
            "Queued DiagnosticSessionControl session value with suppressPosRsp bit removed.");
        label(0xFEBF2BA3L,"bootloader_session_task_state",
            "Asynchronous bootloader session-control state consumed by task 0x6244.");
    }
}
