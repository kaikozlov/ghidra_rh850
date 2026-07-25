//@author kaikozlov
//@category Analysis
// Correct the report's CSM/ICU/key-lifecycle misidentification: this path is NvM.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;

public class AnnotateSecocNvmCorrection extends GhidraScript {
    private void rename(long value, String name, String comment) throws Exception {
        Address a=toAddr(value);
        Function f=currentProgram.getFunctionManager().getFunctionAt(a);
        if (f==null) throw new IllegalStateException("no function at "+a);
        f.setName(name,SourceType.USER_DEFINED);
        currentProgram.getListing().setComment(a,CodeUnit.PLATE_COMMENT,comment);
        println(a+" -> "+name);
    }
    private void label(long value, String name, String comment) throws Exception {
        Address a=toAddr(value);
        SymbolTable st=currentProgram.getSymbolTable();
        Symbol s=st.getPrimarySymbol(a);
        if (s!=null && s.getSource()!=SourceType.USER_DEFINED) s.setName(name,SourceType.USER_DEFINED);
        else if (s==null) { s=st.createLabel(a,name,SourceType.USER_DEFINED); s.setPrimary(); }
        currentProgram.getListing().setComment(a,CodeUnit.PLATE_COMMENT,comment);
        println(a+" -> "+name);
    }
    @Override public void run() throws Exception {
        rename(0x65C60L,"secoc_nvm_cyclic_task",
            "Cyclic scheduler for SecOC-associated redundant NvM state. This is not a CSM/ICU MAC scheduler.");
        rename(0x65C84L,"secoc_nvm_restore_request",
            "Request-side dispatcher. Namespace 0x100 queues an NvM restore via 0x66DB2; it does not request a key set.");
        rename(0x65CD8L,"secoc_nvm_object_update",
            "Update dispatcher for configured SecOC-associated state objects. Namespace 0x100 reaches the redundant NvM mirror update at 0x66E48.");
        rename(0x66DB2L,"secoc_nvm_queue_restore",
            "Queue state 0x11 for a configured redundant object. The scheduler later calls NvM_ReadBlock for its three copies.");
        rename(0x66E48L,"secoc_nvm_redundant_object_update",
            "Copy a changed object into its configured RAM mirror and queue triplicate persistence. This is generic NvM rather than a CSM key-set API; object 15 is key-bearing on field-verified related variants.");
        rename(0x66AC2L,"secoc_nvm_redundancy_scheduler",
            "Processes restore/write requests for redundant NvM objects. State 0x11 restores; 0x22/0x33 persists or validates.");
        rename(0x67162L,"secoc_nvm_state_init",
            "Initialize SecOC-associated NvM state; explicitly zeroes all 3x32-byte work-buffer groups before restore requests.");
        rename(0x6728EL,"secoc_nvm_restore_all",
            "Submit NvM_ReadBlock (service 0x06) for configured objects and checkpoint blocks. Zero buffers are destinations, not keys being installed.");
        rename(0x66374L,"secoc_nvm_checkpoint_scheduler",
            "Schedules persistence of ordinary checkpoint/state objects; 0x674A8 submits NvM_WriteBlock, not MAC generation.");
        rename(0x674A8L,"secoc_nvm_checkpoint_write_submit",
            "Build counter/payload/complement NvM block and submit NvM_WriteBlock through 0x72F84. No CMAC is generated here.");
        rename(0x67590L,"secoc_nvm_restore_triplicate",
            "Submit three NvM_ReadBlock jobs into raw/XOR55/XORAA work buffers at FEBFEB08. This is generic object restore, not an ICU key-set command; configured object 15 may carry key data.");
        rename(0x67608L,"secoc_nvm_persist_triplicate",
            "Create raw, XOR55, and XORAA copies of a structured RAM object and submit three NvM_WriteBlock jobs. This is not MAC verification.");
        rename(0x67C34L,"secoc_nvm_triplicate_read_complete",
            "Handle NvM read completion/retries, reconcile the three encoded copies, and copy the consensus value into the configured RAM mirror.");
        rename(0x679D6L,"nvm_validate_triplicate_records",
            "Validate that an object's three configured 64-byte NvM/DataFlash records are readable. No key derivation or ICU call occurs.");
        rename(0x71D9EL,"nvm_queue_service_request",
            "Generic AUTOSAR NvM asynchronous request queue. Magic selects an NvM service, not an ICU crypto operation.");
        rename(0x72F58L,"nvm_read_block_submit",
            "Submit AUTOSAR NvM service 0x06 (ReadBlock), magic 0xA1A62093, with block ID and destination pointer.");
        rename(0x72F84L,"nvm_write_block_submit",
            "Submit AUTOSAR NvM service 0x07 (WriteBlock), magic 0x22AA8A36, with block ID and source pointer.");
        rename(0x758A0L,"nvm_read_block_sync",
            "Synchronous/status-mapped NvM/DataFlash read into a local 76-byte buffer. This is not ICU key derivation.");
        rename(0x785D2L,"nvm_set_current_service_id",
            "Validate/store NvM service IDs 0x06/07/08/0C/0D/16/17/18. These match AUTOSAR NvM APIs, not ICU opcodes.");

        label(0x2B0ACL,"secoc_nvm_redundant_object_table",
            "16 descriptors: length u16, base NvM block u16, RAM mirror u32. Configured objects use base/base+4/base+8 as raw/XOR55/XORAA; object 15 is len32/base41/RAM FEBF02E8.");
        label(0x26DE0L,"nvm_block_descriptor_table",
            "124 AUTOSAR NvM block descriptors, addressed with application tp=0x23EE4.");
        label(0x277A0L,"nvm_service_magic_table",
            "NvM service-to-magic map; entry 0x06=ReadBlock/A1A62093 and 0x07=WriteBlock/22AA8A36.");
        label(0x27808L,"nvm_block_storage_map",
            "Six-byte NvM storage records; first u16 maps configured block to a 64-byte DataFlash page.");

        label(0xFEBEF400L,"secoc_nvm_object2_ram_mirror","8-byte structured NvM object; not key material.");
        label(0xFEBEF468L,"secoc_nvm_object0_ram_mirror","16-byte structured state (A55A5AA5/counter fields), not a SecOC AES key.");
        label(0xFEBEF478L,"secoc_nvm_object1_ram_mirror","16-byte structured NvM object; not a SecOC AES key.");
        label(0xFEBEF488L,"secoc_nvm_object3_ram_mirror","16-byte structured NvM object; not a SecOC AES key.");
        label(0xFEBFEB08L,"secoc_nvm_triplicate_workbuf","Four groups of generic raw/XOR55/XORAA 32-byte buffers used by NvM restore/write operations. Not an ICU key-set API, though a key-bearing configured object can pass through them.");

        label(0xFF207500L,"secoc_nvm_obj3_xoraa_record","Object 3 XOR-AA persistent copy (NvM block/job 13, page 468).");
        label(0xFF207540L,"secoc_nvm_obj2_xoraa_record","Object 2 XOR-AA persistent copy (job 12, page 469).");
        label(0xFF207580L,"secoc_nvm_obj1_xoraa_record","Object 1 XOR-AA persistent copy (job 11, page 470).");
        label(0xFF2075C0L,"secoc_nvm_obj0_xoraa_record","Object 0 XOR-AA persistent copy (job 10, page 471).");
        label(0xFF207600L,"secoc_nvm_obj3_xor55_record","Object 3 XOR-55 persistent copy (job 9, page 472).");
        label(0xFF207640L,"secoc_nvm_obj2_xor55_record","Object 2 XOR-55 persistent copy (job 8, page 473).");
        label(0xFF207680L,"secoc_nvm_obj1_xor55_record","Object 1 XOR-55 persistent copy (job 7, page 474).");
        label(0xFF2076C0L,"secoc_nvm_obj0_xor55_record","Object 0 XOR-55 persistent copy (job 6, page 475).");
        label(0xFF207700L,"secoc_nvm_obj3_raw_record","Object 3 raw persistent copy (job 5, page 476).");
        label(0xFF207740L,"secoc_nvm_obj2_raw_record","Object 2 raw persistent copy (job 4, page 477).");
        label(0xFF207780L,"secoc_nvm_obj1_raw_record","Object 1 raw persistent copy (job 3, page 478).");
        label(0xFF2077C0L,"secoc_nvm_obj0_raw_record","Object 0 raw persistent copy (job 2, page 479); highest normal NvM page.");
        label(0xFF207800L,"dataflash_reserved_tail_2k",
            "Pages 480..511 are absent from the normal NvM map and read only as 00/FF. Strongly consistent with an ICU-S-reserved tail, but the SecOC key is not proven to reside here.");
    }
}
