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
            "Read the current application Dcm session, call the transition-policy hook at 0x4C942, and map its internal result to a UDS NRC.");
        fn(0x4C942L,"application_session_transition_policy",
            "Application-specific session-transition policy hook. The incomplete RH850 calling convention hides one argument; confirm register setup before assigning semantic names to both inputs.");
        fn(0x8A244L,"application_session_transition_async_worker",
            "Asynchronous lower-layer worker used while the application enters a new diagnostic session, including PROGRAMMING bootloader transition work.");
        fn(0x8A082L,"application_session_transition_state_reset",
            "Reset the application session-transition worker state.");
        fn(0x8D5FCL,"application_internal_result_to_nrc",
            "Map application internal result values to UDS NRCs including 0x12, 0x22, 0x31, 0x72, 0x78, and vendor NRC 0x88.");

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
            "Seventeen 24-byte application UDS service records. SID is byte 8; configured sequence is 10,11,14,19,22,23,27,28,2E,31,34,36,37,3E,85,AB,BA.");
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

        label(0x2A30CL,"application_f181_record",
            "Application DID F181 record: flags 0x0011, read callback 0x4E8E4.");
        label(0x2A31CL,"application_f186_record",
            "Application DID F186 record: flags 0x0001, read callback 0x4E90A.");
        label(0x2A32CL,"application_f18c_record",
            "Application DID F18C record: flags 0x0014, read callback 0x4E918.");

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
