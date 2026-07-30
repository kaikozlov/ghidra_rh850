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
            "Reject requested session 2 with internal result 0x0B / NRC 0x88 (vehicleSpeedTooHigh) when the unsigned raw speed at FEBEE892 (GP+0x3092) exceeds calibration 0x0180 at CodeFlash 0x181DC. The current-session argument in r6 is not tested here.");
        fn(0x8A01CL,"application_programming_lower_request_stub",
            "Compiled lower-request stub. It accepts operation ID, status 10, payload length/data, and token pointer but returns success without using them in this image.");
        fn(0x8A08EL,"application_programming_readiness_check_adapter",
            "Run the lower programming-handoff prerequisites once. On success clear the reset-request marker and latch completion at absolute FEBF3B18.");
        fn(0x4C960L,"application_programming_handoff_prerequisites",
            "Return failure unless system-transition phase snapshot FEBEE81F (GP+0x301F) is not 0x11, scaled supply FEBE6692 (GP-0x516E) is at least calibration 0x0A00, and alternate-handoff flag FEBE8152 (GP-0x36AE) is clear.");
        fn(0xB28ACL,"application_system_transition_phase_init",
            "Initialize the live generated system-transition phase at FEBEB1A4 (application GP-0x65C) to zero.");
        fn(0xB2912L,"application_system_transition_phase_step",
            "Advance the generated system-transition state around modes 0x300/0x400/0x500 and event 0x23. Recovered phase markers are 0, 0x11, and 0x22; adjacent flags, not this phase byte, use 0x5A.");
        fn(0xBCB3AL,"application_input_snapshot_update",
            "Copy the broad generated application input snapshot. At BCD02..BCD06 it copies live system-transition phase FEBEB1A4 (GP-0x65C) to FEBEE81F (GP+0x301F via EP=GP+0x3000).");
        fn(0x4C986L,"application_programming_reset_marker_clear",
            "Clear the one-request marker at FEBE8166 (GP-0x369A) before the programming reset is queued.");
        fn(0x4C98CL,"application_programming_reset_request",
            "Queue system event 9 once and set marker FEBE8166 (GP-0x369A) to 0x5A. Event 9 drives the system-mode coordinator into shutdown mode 0x900; the alternate FEBE8152 (GP-0x36AE) branch reinitializes local stacks instead.");
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

        label(0xFEBEE892L,"application_vehicle_speed_raw",
            "Unsigned speed at GP+0x3092 tested against CodeFlash 0x181DC for PROGRAMMING entry; values above 0x0180 map to NRC 0x88 vehicleSpeedTooHigh.");
        label(0xFEBEB1A4L,"application_system_transition_phase_live",
            "Live phase byte owned by 0xB28AC/0xB2912. Recovered phase markers are 0, 0x11, and 0x22; exact OEM phase labels are unknown.");
        label(0xFEBEE81FL,"application_system_transition_phase_snapshot",
            "Snapshot at GP+0x301F copied from FEBEB1A4 by 0xBCB3A. Phase 0x11 prevents programming reset handoff and produces NRC 0x22; this is not a Dcm-produced programming-status byte.");
        label(0xFEBE6692L,"application_supply_value_raw",
            "Scaled supply at GP-0x516E used by the lower handoff. Values below calibration 0x0A00 prevent reset handoff and produce NRC 0x22.");
        label(0xFEBE8152L,"application_alternate_handoff_flag",
            "Flag at GP-0x36AE set from the application diagnostic initialization callback. It must be clear for the normal event-9 PROGRAMMING reset path.");
        label(0xFEBE8166L,"application_programming_reset_requested",
            "One-request marker at GP-0x369A: cleared before handoff and set to 0x5A after system event 9 is queued.");
        label(0xFEBF3B14L,"application_programming_handoff_value",
            "Four-byte value at absolute FEBF3B14 passed as an all-zero payload to compiled-stub operation 0x08000201.");
        label(0xFEBF3B18L,"application_programming_readiness_latch",
            "Absolute FEBF3B18 set to 0x5A after the lower programming readiness check succeeds.");
        label(0xFEBF3B19L,"application_programming_reset_latch",
            "Absolute FEBF3B19 (FEBF3B14+5) set to 0x5A after the programming reset request succeeds; subsequent worker polls remain pending until reset.");
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

        // Stage-2 primary SID handlers and tables.
        fn(0x8B1F0L,"application_ecu_reset_callback",
            "Application ECUReset service callback. Phase 0 starts 0x8B144; nonzero finalizes through 0x8B1D4.");
        fn(0x8B144L,"application_ecu_reset_request_start",
            "Require request length 3, pack three request bytes, and enter the lower reset prepare/commit stages.");
        fn(0x8AF28L,"application_ecu_reset_prepare_stage",
            "First ECUReset lower stage: issue compiled-stub operation 0x18000000 and map failures to NRC 0x22/0x31.");
        fn(0x8B014L,"application_ecu_reset_commit_stage",
            "Second ECUReset lower stage: issue compiled-stub operation 0x18000001; success builds the positive response, pending returns 10.");
        fn(0x945DCL,"application_read_dtc_callback",
            "Application ReadDTCInformation service callback. Phase 0 starts 0x944C6; phase 2 completes through 0x9452E.");
        fn(0x8B5AAL,"application_read_dtc_subfunction_01",
            "ReadDTCInformation subfunction 0x01 wrapper; copy request context and start worker 0x8B532.");
        fn(0x8BA2AL,"application_read_dtc_subfunction_02",
            "ReadDTCInformation subfunction 0x02 wrapper; copy request context and start worker 0x8B99A.");
        fn(0x8BD94L,"application_read_dtc_subfunction_03",
            "ReadDTCInformation subfunction 0x03 wrapper; copy request context and start worker 0x8BD30.");
        fn(0x8C326L,"application_read_dtc_subfunction_04",
            "ReadDTCInformation subfunction 0x04 wrapper; copy request context and start worker 0x8C276.");
        fn(0x948AAL,"application_rdbi_callback",
            "Application ReadDataByIdentifier service callback. Phases 0/2/3 start, cancel, and poll DID reads.");
        fn(0x9479AL,"application_rdbi_request_start",
            "Validate RDBI request shape, resolve DID policy, enforce per-DID security, then begin/poll the read.");
        fn(0x946FAL,"application_rdbi_request_poll",
            "Poll an asynchronous RDBI transfer; pending returns 10, failures emit the worker NRC byte.");
        fn(0x94E32L,"application_security_access_subfunction_01",
            "SecurityAccess subfunction 0x01 (level-1 requestSeed) wrapper around 0x94CCE.");
        fn(0x94E46L,"application_security_access_subfunction_02",
            "SecurityAccess subfunction 0x02 (level-1 sendKey) wrapper around 0x94DEE.");
        fn(0x94E5AL,"application_security_access_subfunction_03",
            "SecurityAccess subfunction 0x03 (level-2 requestSeed) wrapper around 0x94CCE.");
        fn(0x94E6EL,"application_security_access_subfunction_04",
            "SecurityAccess subfunction 0x04 (level-2 sendKey) wrapper around 0x94DEE.");
        fn(0x9497CL,"application_security_access_request_seed",
            "Application requestSeed worker for configured levels 1/2. Emits seed bytes or NRC 0x37 when delay-locked.");
        fn(0x94A72L,"application_security_access_send_key",
            "Application sendKey worker. Success unlocks via 0x900FC; failures map to NRC 0x35/0x36.");
        fn(0x93C62L,"application_communication_control_callback",
            "Application CommunicationControl service callback. Phase 0 starts 0x93B56; phase 2 completes 0x93BDE.");
        fn(0x9542CL,"application_communication_control_subfunction_00",
            "CommunicationControl subfunction 0x00 wrapper into shared start helper 0x95306.");
        fn(0x9543CL,"application_communication_control_subfunction_01",
            "CommunicationControl subfunction 0x01 wrapper into shared start helper 0x95306.");
        fn(0x9544CL,"application_communication_control_subfunction_03",
            "CommunicationControl subfunction 0x03 wrapper into shared start helper 0x95306.");
        fn(0x95154L,"application_communication_control_request_start",
            "Validate CommunicationControl request length/control type and apply configured communication-mode updates.");
        fn(0x95DCEL,"application_wdbi_callback",
            "Application WriteDataByIdentifier service callback. Phases 0/2/3 start, cancel, and poll DID writes.");
        fn(0x95C8CL,"application_wdbi_request_start",
            "Validate WDBI DID/security/session policy against the 19-entry write-DID table and begin the write worker.");
        fn(0x93CFEL,"application_tester_present_subfunction_00",
            "TesterPresent subfunction 0x00: accept zero-length request data and build the positive acknowledgment.");
        fn(0x8CCDCL,"application_control_dtc_setting_subfunction_01",
            "ControlDTCSetting subfunction 0x01 wrapper; require zero-length request data then store setting 1.");
        fn(0x8CCFAL,"application_control_dtc_setting_subfunction_02",
            "ControlDTCSetting subfunction 0x02 wrapper; require zero-length request data then store setting 2.");
        fn(0x8D344L,"application_proprietary_ab_callback",
            "Proprietary SID 0xAB event-record callback. Phase 0 mirrors the request and enters asynchronous operation F1 through 0x8D2B2; OEM name unknown.");
        fn(0x96A34L,"application_proprietary_ab_subfunction_01",
            "Proprietary SID 0xAB subfunction 0x01: request the active event-ID list through shared worker 0x96918.");
        fn(0x96A56L,"application_proprietary_ab_subfunction_02",
            "Proprietary SID 0xAB subfunction 0x02: query one 16-bit event ID through shared worker 0x96918. This is not the control-block reset path.");
        fn(0x96A78L,"application_proprietary_ab_subfunction_03",
            "Proprietary SID 0xAB subfunction 0x03: query event detail using a 16-bit event ID and 16-bit secondary selector.");
        fn(0x96918L,"application_proprietary_ab_selector_worker",
            "Validate AB selector payload lengths, copy request context, and configure the event-record query worker for active-list, single-ID, or detail mode.");
        fn(0x8CF84L,"application_proprietary_ab_event_worker",
            "Advance the AB event-record query state machine and dispatch modes 1/2/3 through 0x4F8BA; no edge to the routine-ID table.");
        fn(0x4F8BAL,"application_event_record_query",
            "Query the checkpoint-backed event catalogue: mode 1 lists active IDs, mode 2 reads per-ID state, and mode 3 reads detail/snapshot data.");
        fn(0x54748L,"application_event_active_id_list",
            "Enumerate active IDs from the 64-slot event catalogue at 0x2AD10 using the bitmap at FEBE89BC.");
        fn(0x548B0L,"application_event_state_query",
            "Resolve one event ID in the 64-slot catalogue and return its type-specific state data.");
        fn(0x54BF2L,"application_event_detail_query",
            "Resolve one event ID and secondary selector through the 75 snapshot and six detail descriptors.");
        fn(0x34B74L,"application_proprietary_ab_f1_start",
            "Operation-F1 start callback selected by the AB asynchronous handoff. Check the JTEKM token and enter operation state 3 through the B201A veneer.");
        fn(0x34B9AL,"application_proprietary_ab_f1_result",
            "Operation-F1 result callback selected by the AB asynchronous handoff; read operation state 3 through the B209C veneer.");
        fn(0x8A482L,"application_routine_start_dispatch",
            "Resolve one of the first 13 control-ID records and invoke its start callback through lookup 0x8D3CC. SID 0x28 records link the worker structurally, but stock subfunctions gate its 02xx/20xx selectors.");
        fn(0x8A542L,"application_routine_result_dispatch",
            "Resolve one of the first 13 control-ID records and invoke its result callback through lookup 0x8D416. Some results arm asynchronous NvM updates for objects 0x101/0x102/0x103.");
        fn(0x8A630L,"application_routine_worker",
            "Stock-gated start/poll worker reached by SID 0x28 generic-control wrappers 0x936AA/0x936D6 for selector ranges 02xx/20xx. Separate from SID 0xAB and unattached to null-callback SID 0x31.");
        fn(0x8D3CCL,"application_routine_start_callback_lookup",
            "Scan control-ID table entries 0..12 at 0x25768 and invoke the matching start callback. Sole direct caller is 0x8A50C in the stock-gated worker.");
        fn(0x8D416L,"application_routine_result_callback_lookup",
            "Scan control-ID table entries 0..12 at 0x25768 and invoke the matching result callback. Separate from SID 0xAB; selected results arm objects 0x101/0x102/0x103.");
        fn(0x4F928L,"application_did_table_getter",
            "Return the application DID table base 0x2941C and count 0xF2 (242).");
        fn(0x93910L,"application_uds_negative_response",
            "Common application Dcm negative-response builder used by service workers.");
        fn(0x938F8L,"application_uds_request_busy_set",
            "Set/clear the application Dcm request-busy flag around synchronous and asynchronous service work.");

        label(0x2941CL,"application_did_table",
            "242 x 16-byte application DID records beginning at DID 0x0100 and ending at F18C. Getter 0x4F928 returns count 0xF2.");
        label(0x26AECL,"application_write_did_table",
            "19 x 8-byte write-DID descriptors used by application WDBI. Binary-searched from 0x9545C.");
        label(0x25768L,"application_routine_id_table",
            "32 x 12-byte control-ID records (ID, flags, start_cb, result_cb). A stock-gated SID 0x28 worker consumes entries 0..12; SID 0x31 has a null callback and SID 0xAB has no edge here.");
        label(0x28094L,"application_operation_descriptor_count",
            "Ten generic asynchronous operation descriptors follow at 0x28098. SID 0xAB uses operation F1.");
        label(0x28098L,"application_operation_descriptor_table",
            "Ten 16-byte asynchronous operation descriptors F1..FB. F1 selects AB callbacks 0x34B74/0x34B9A.");
        label(0x2AD10L,"application_event_record_catalogue",
            "64 x 8-byte event-record slots used by SID 0xAB; 51 slots are populated. Each record carries an encoded ID and type/shape bytes.");
        label(0x2A504L,"application_event_snapshot_descriptor_table",
            "75 x 24-byte event snapshot descriptors. 35 non-null callback pointers resolve to 0x54C64..0x551C2.");
        label(0x2AC0CL,"application_event_detail_descriptor_table",
            "Six x 16-byte event detail descriptors with six data callbacks and no configured gate callbacks.");
        label(0xFEBE89BCL,"application_event_active_bitmap",
            "Two-word active-event bitmap restored through checkpoint object 0x11 and enumerated by 0x54748 for AB selector 1.");
        label(0xFEBF45D0L,"application_ab_query_control",
            "AB event-query control block: selector, event ID, secondary selector, worker state, and result length/status fields.");
        label(0x25BF0L,"application_read_dtc_subfunction_table",
            "ReadDTCInformation subfunction records 0x01..0x04 with callbacks 0x8B5AA/0x8BA2A/0x8BD94/0x8C326.");
        label(0x25C30L,"application_security_access_subfunction_table",
            "SecurityAccess subfunction records 0x01..0x04 for application levels 1/2 requestSeed/sendKey.");
        label(0x25C70L,"application_communication_control_subfunction_table",
            "CommunicationControl subfunction records 0x00/0x01/0x03.");
        label(0x25CA0L,"application_tester_present_subfunction_table",
            "TesterPresent subfunction 0x00 record; callback 0x93CFE.");
        label(0x25CB0L,"application_control_dtc_setting_subfunction_table",
            "ControlDTCSetting subfunction records 0x01/0x02.");
        label(0x25CD0L,"application_proprietary_ab_subfunction_table",
            "Proprietary SID 0xAB subfunction records 0x01/0x02/0x03. Structural names only.");
        label(0x26338L,"application_security_access_level1_config",
            "Application SecurityAccess level-1 slot: seed/key length 0x10 and timing words 0x2710.");
        label(0x26350L,"application_security_access_level2_config",
            "Application SecurityAccess level-2 slot: seed/key length 0x10 and timing words 0x2710.");
    }
}
