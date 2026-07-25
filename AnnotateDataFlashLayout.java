//@author optskug
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
        if (s!=null && s.getSource()!=SourceType.USER_DEFINED) {
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

        label(0x8F14L,"bootloader_payload_did_table",
            "Four 12-byte descriptors. 0x201 len16 -> FEBF2D08; 0x202 len16 -> FEBF2CF8; 0x203 len5 is handled specially. These are volatile session parameters.");
        label(0x2B0ACL,"secoc_nvm_redundant_object_table",
            "16 descriptors (length u16, base NvM block u16, RAM mirror u32). Copies use base/base+4/base+8 as raw/XOR55/XORAA. Object 15 is len32, base block 41, RAM FEBF02E8.");
        label(0x26DE0L,"nvm_block_descriptor_table",
            "124 NvM job descriptors. Jobs 0 and 2 alias storage index 1; job 1 is non-persistent; jobs 3..123 map storage indexes 2..122.");
        label(0x27808L,"nvm_block_storage_map",
            "Six-byte physical records (first page u16, payload length u16, flags u16). Configured records 1..122 pack pages 256..479.");

        label(0xFEBF2D08L,"payload_did_0201_key_material",
            "Volatile 16-byte DID 0x201 buffer used to derive the payload key; not persisted in DataFlash.");
        label(0xFEBF2CF8L,"payload_did_0202_iv",
            "Volatile 16-byte DID 0x202 IV used by payload AES-CBC/CMAC; not persisted in DataFlash.");

        label(0xFF200000L,"dataflash_unmapped_lower_half",
            "Pages 0..255 are absent from the configured normal NvM storage map and contain no valid record boundary markers in this dump; exact role unknown.");
        label(0xFF204000L,"dataflash_configured_nvm_start",
            "Page 256: lowest configured normal NvM physical record. Configured records occupy pages 256..479.");
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
        label(0xFF207800L,"dataflash_reserved_tail_2k",
            "Pages 480..511 are outside the normal NvM map and read as 00/FF only. Strongly consistent with an ICU-S-reserved tail, but the SecOC key is not proven to reside here.");
    }
}
