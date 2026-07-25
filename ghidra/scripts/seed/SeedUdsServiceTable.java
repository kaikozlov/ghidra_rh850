//@author kaikozlov
//@category Analysis
// Parse the 20-entry bootloader UDS table at 0x8E54, create handler functions,
// label them, and add explicit data references from table pointer fields.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;

public class SeedUdsServiceTable extends GhidraScript {
    private static final long TABLE = 0x8E54L;
    private static final int COUNT = 20;

    private String nameFor(int sid, long handler) {
        if (handler == 0x69B0L) return "uds_unsupported_service_handler";
        switch (sid) {
            case 0x10: return "uds_diagnostic_session_control";
            case 0x11: return "uds_ecu_reset";
            case 0x27: return "uds_security_access";
            case 0x28: return "uds_communication_control";
            case 0x3E: return "uds_tester_present";
            case 0x85: return "uds_control_dtc_setting";
            case 0x22: return "uds_read_data_by_identifier";
            case 0x23: return "uds_read_memory_by_address";
            case 0x2C: return "uds_dynamically_define_data_identifier";
            case 0x2E: return "uds_write_data_by_identifier";
            case 0x14: return "uds_clear_diagnostic_information";
            case 0x19: return "uds_read_dtc_information";
            case 0x2F: return "uds_input_output_control_by_identifier";
            case 0x31: return "uds_routine_control";
            case 0x34: return "uds_request_download";
            case 0x36: return "uds_transfer_data";
            case 0x37: return "uds_request_transfer_exit";
            default: return String.format("uds_sid_%02x_handler", sid);
        }
    }

    @Override
    public void run() throws Exception {
        Listing listing=currentProgram.getListing();
        ReferenceManager refs=currentProgram.getReferenceManager();
        int made=0, renamed=0, addedRefs=0;
        java.util.Set<Long> seen=new java.util.HashSet<>();
        for (int i=0; i<COUNT; i++) {
            Address entry=toAddr(TABLE+i*8L);
            int sid=currentProgram.getMemory().getByte(entry)&0xff;
            int mask=currentProgram.getMemory().getByte(entry.add(1))&0xff;
            long handler=currentProgram.getMemory().getInt(entry.add(4))&0xffffffffL;
            Address target=toAddr(handler);
            refs.addMemoryReference(entry.add(4), target, RefType.DATA, SourceType.USER_DEFINED, 0);
            addedRefs++;
            String name=nameFor(sid,handler);
            if (!seen.add(handler)) {
                println(String.format("SID 0x%02x mask 0x%02x -> shared %s @ %s",sid,mask,name,target));
                continue;
            }
            Instruction containing=listing.getInstructionContaining(target);
            if (containing!=null && !containing.getMinAddress().equals(target)) {
                listing.clearCodeUnits(containing.getMinAddress(),containing.getMaxAddress(),false);
            }
            if (listing.getInstructionAt(target)==null) disassemble(target);
            Function f=currentProgram.getFunctionManager().getFunctionAt(target);
            if (f==null) {
                f=createFunction(target,name);
                if (f!=null) made++;
            } else if (!f.getName().equals(name)) {
                f.setName(name,SourceType.USER_DEFINED); renamed++;
            }
            println(String.format("SID 0x%02x mask 0x%02x -> %s @ %s",sid,mask,name,target));
        }
        println(String.format("SeedUdsServiceTable: functions_created=%d renamed=%d references_added=%d",made,renamed,addedRefs));
    }
}
