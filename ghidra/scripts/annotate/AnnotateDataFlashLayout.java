//@author kaikozlov
//@category Analysis
// Annotate the complete DataFlash/NvM map and the field-known object-15 key slot.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;

public class AnnotateDataFlashLayout extends GhidraScript {
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
        if (s!=null && !s.getName().equals(name)) {
            s.setName(name,SourceType.USER_DEFINED);
        } else if (s==null) {
            s=st.createLabel(a,name,SourceType.USER_DEFINED);
            s.setPrimary();
        }
        currentProgram.getListing().setComment(a,CodeUnit.PLATE_COMMENT,comment);
        println(a+" -> "+name);
    }
    @Override public void run() throws Exception {
        rename(0x6D5EL,"bootloader_did_write_dispatch",
            "Dispatch a bootloader DID write to either a callback or a direct RAM copy. DIDs 0x201/0x202 are volatile payload-crypto inputs, not DataFlash-backed values.");
        rename(0x6D3AL,"bootloader_did_direct_ram_copy",
            "Copy a DID payload directly to the RAM pointer in its 12-byte descriptor.");
        rename(0x67A98L,"checkpoint_restore_complete",
            "Validate checkpoint generation/complement, select the current ring record, and restore bytes after the generation word to the configured RAM mirror.");
        rename(0x65D66L,"checkpoint_object_restore_read",
            "Read an indexed checkpoint object through the generated restore API. Object-specific startup consumers call this with literal indexes.");
        rename(0x5110AL,"checkpoint_monitor_aggregate_persist",
            "Assemble and persist checkpoint object 0: two eight-byte groups and three 12-word monitor groups.");
        rename(0x51B70L,"checkpoint_monitor_state_bank_persist",
            "Persist one of checkpoint objects 1..3 as a whole 240-byte monitor-state bank.");
        rename(0x53492L,"checkpoint_event_counter_groups_persist",
            "Assemble and persist checkpoint object 4 as arrays of 18 and 10 16-bit counters.");
        rename(0x38CECL,"checkpoint_multi_channel_u16_state_persist",
            "Assemble and persist checkpoint object 6's 16-bit field groups. The OEM physical meaning is not established.");
        rename(0x4528CL,"checkpoint_dual_incident_snapshot_persist",
            "Assemble and persist checkpoint object 12: two counters, reserved zero, and two state/value/sample entries.");
        rename(0x538D4L,"checkpoint_three_entry_condition_history_persist",
            "Assemble and persist checkpoint object 14: 12 trigger counters and three condition-history entries.");
        rename(0x53F5EL,"checkpoint_event_history_group_persist",
            "Persist one of 168-byte checkpoint objects 20, 21, or 23 as a whole event-history buffer; entry-level OEM schema remains unresolved.");
        rename(0x53FC4L,"checkpoint_event_log_banks_persist",
            "Persist checkpoint object 17 control state and alternating 96-byte event-log banks 18/19.");
        rename(0x34FB6L,"checkpoint_persistent_countdown_step",
            "Decrement checkpoint object 24's one-byte countdown and clear related redundant state when it reaches zero.");
        rename(0x4EA78L,"application_ram_range_allowed",
            "Validate a RAM range while rejecting overlap with five protected RAM intervals at CodeFlash 0x293F4.");
        rename(0x4EAD8L,"application_dataflash_range_allowed",
            "Validate a DataFlash range and reject overlap with FF207800..FF207FFF or FF206C00..FF206EFF from the table at 0x293E4.");

        label(0x8F14L,"bootloader_payload_did_table",
            "Four 12-byte descriptors. 0x201 len16 -> FEBF2D08; 0x202 len16 -> FEBF2CF8; 0x203 len5 is handled specially. These are volatile session parameters.");
        label(0x2B0ACL,"secoc_nvm_redundant_object_table",
            "16 descriptors (length u16, base NvM block u16, RAM mirror u32). Copies use base/base+4/base+8 as raw/XOR55/XORAA. Object 15 is len32, base block 41, RAM FEBF02E8.");
        label(0x26DE0L,"nvm_block_descriptor_table",
            "124 NvM job descriptors. Jobs 0 and 2 alias storage index 1; job 1 is non-persistent; jobs 3..123 map storage indexes 2..122.");
        label(0x27808L,"nvm_block_storage_map",
            "Six-byte physical records (first page u16, payload length u16, flags u16). Configured records 1..122 pack pages 256..479.");
        label(0x2AF10L,"checkpoint_object_count",
            "Value 32: number of generation-protected checkpoint object descriptors at 0x2AF2C.");
        label(0x2AF2CL,"checkpoint_object_descriptor_table",
            "32 x 12-byte descriptors: data length, ring-block count, first NvM block, reserved zero, RAM mirror. Twenty-four entries are enabled; data/checkpoint_payload_map.csv records their evidence-bounded producer/layout names.");
        label(0x2B1B0L,"nvm_logical_owner_table",
            "124 x 2-byte block owners: object index then class (0 checkpoint ring, 1 triplicate). Blocks 0/1 are FFFF; every persistent block 2..123 has an owner.");
        label(0x293E4L,"dataflash_protected_range_table",
            "Two inclusive ranges rejected by 0x4EAD8: FF207800..FF207FFF ICU-S-shaped tail and FF206C00..FF206EFF optional objects 12..15.");

        label(0xFEBF2D08L,"payload_did_0201_key_material",
            "Volatile 16-byte DID 0x201 buffer used to derive the payload key; not persisted in DataFlash.");
        label(0xFEBF2CF8L,"payload_did_0202_iv",
            "Volatile 16-byte DID 0x202 IV used by payload AES-CBC/CMAC; not persisted in DataFlash.");

        label(0xFF200000L,"dataflash_currently_unallocated_lower_half",
            "Pages 0..255 have no configured owner or credible runtime object reference. Their patterns are erased-readback-compatible and not recoverable records; whether they were used before erase is indeterminable.");
        label(0xFF204000L,"dataflash_checkpoint_ring_start",
            "Page 256: lowest checkpoint-ring physical allocation. Pages 256..431 hold 74 records for 32 logical slots (24 enabled, 8 disabled).");
        label(0xFF206B40L,"checkpoint_object0_ring_record0",
            "Checkpoint object 0, ring block 50/storage 49. Record payload is generation + 160 RAM bytes + inverse generation; valid in this dump.");
        label(0xFF206C00L,"secoc_nvm_triplicate_bank_object15_xoraa_record",
            "Page 432 starts the 48-record SecOC triplicate bank and is object 15's XORAA copy (NvM block 49, storage index 48); invalid in this dump.");

        label(0xFF206EC0L,"secoc_nvm_object12_raw_record",
            "Object 12 raw copy: NvM block 38, storage index 37, page 443, len32; invalid/uncommitted in this dump.");
        label(0xFF206E80L,"secoc_nvm_object13_raw_record",
            "Object 13 raw copy: NvM block 39, storage index 38, page 442, len32; invalid/uncommitted in this dump.");
        label(0xFF206E40L,"secoc_nvm_object14_raw_record",
            "Object 14 raw copy: NvM block 40, storage index 39, page 441, len32; invalid/uncommitted in this dump.");
        label(0xFF206E00L,"secoc_nvm_object15_raw_record",
            "Object 15 raw copy: NvM block 41, storage index 40, page 440, len32. Field-verified related variants store the SecOC key in payload bytes 16..31; this record is invalid in this dump.");
        label(0xFF206E14L,"secoc_nvm_object15_raw_key_field",
            "Second 16-byte field of object 15 raw payload. CMAC-verified as the operational SecOC key on related Sienna/Yaris/8965B4514000 data; this exact dump contains low-entropy non-key bytes and an invalid record.");
        label(0xFF206D00L,"secoc_nvm_object15_xor55_record",
            "Object 15 XOR55 copy: NvM block 45, storage index 44, page 436; invalid in this dump.");
        label(0xFF206D14L,"secoc_nvm_object15_xor55_key_field",
            "Expected key XOR 0x55 field when object 15 is valid; invalid/uncommitted in this dump.");
        label(0xFF206C14L,"secoc_nvm_object15_xoraa_key_field",
            "Expected key XOR 0xAA field when object 15 is valid; invalid/uncommitted in this dump.");

        label(0xFEBF02E8L,"secoc_nvm_object15_ram_mirror",
            "32-byte CPU-visible RAM mirror for object 15. A valid triplicate consensus is copied here by 0x67C34.");
        label(0xFEBF02F8L,"secoc_nvm_object15_key_field_ram",
            "Second 16-byte field of object 15 RAM mirror; corresponding field is the CMAC-verified SecOC key on related variants. Not validated for this dump.");
        label(0xFF207800L,"dataflash_icus_reserved_tail_2k",
            "Pages 480..511 are outside both NvM owner classes, protected by 0x4EAD8, and align with the documented final 2 KiB ICU-S reservation. CPU-visible 00/FF words do not reveal secure contents or locate the SecOC slot-4 key.");
    }
}
