//@author kaikozlov
//@category Analysis
// Apply evidence-backed StructureDataType / array overlays on LocalRAM roots
// already mapped by ApplyP1MDeviceProfile. Absolute addresses are used; GP
// displacements are recorded in data/ram_overlay_map.csv for verification.
// Invoked during project import after SFR types. Does not invent OEM field
// names — opaque arrays where layouts are unresolved.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.ArrayDataType;
import ghidra.program.model.data.CategoryPath;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.DataTypeConflictHandler;
import ghidra.program.model.data.DataTypeManager;
import ghidra.program.model.data.Pointer32DataType;
import ghidra.program.model.data.StructureDataType;
import ghidra.program.model.data.UnsignedCharDataType;
import ghidra.program.model.data.UnsignedIntegerDataType;
import ghidra.program.model.data.UnsignedShortDataType;
import ghidra.program.model.listing.Data;
import ghidra.program.model.listing.Listing;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.symbol.SourceType;
import ghidra.program.model.symbol.Symbol;
import ghidra.program.model.symbol.SymbolTable;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;

public class ApplyRamTypes extends GhidraScript {
    private static final CategoryPath CAT = new CategoryPath("/P1M_E_RAM");
    private static final long LOCAL_RAM_START = 0xFEBE0000L;
    private static final long LOCAL_RAM_END = 0xFEBFFFFFL; // inclusive

    private DataTypeManager dtm() {
        return currentProgram.getDataTypeManager();
    }

    private DataType resolve(StructureDataType draft) {
        return dtm().addDataType(draft, DataTypeConflictHandler.REPLACE_HANDLER);
    }

    private DataType resolveArray(DataType element, int count) {
        return dtm().addDataType(
                new ArrayDataType(element, count, element.getLength()),
                DataTypeConflictHandler.REPLACE_HANDLER);
    }

    /** 4 KiB download trailer: flash callback slot loaded by 0x4350. */
    private DataType buildPayloadFlashCallback() throws Exception {
        StructureDataType s = new StructureDataType(CAT, "PayloadFlashCallback", 0);
        s.add(Pointer32DataType.dataType, "target",
                "Function pointer; authenticated payloads store 0xFEBF0000");
        return resolve(s);
    }

    /** CRC descriptor words at the end of the authenticated plaintext. */
    private DataType buildPayloadCrcTrailer() throws Exception {
        StructureDataType s = new StructureDataType(CAT, "PayloadCrcTrailer", 0);
        s.add(UnsignedIntegerDataType.dataType, "crc_addr",
                "Embedded CRC start address (0xFEBF0000 in public payloads)");
        s.add(UnsignedIntegerDataType.dataType, "crc_length",
                "Embedded CRC length (0xFF0 covers plaintext before the CMAC tag)");
        s.add(UnsignedIntegerDataType.dataType, "reserved_zero",
                "Zero word in public payload builders");
        s.add(UnsignedIntegerDataType.dataType, "crc_patch",
                "CRC32 residue patch word");
        return resolve(s);
    }

    /** Final 16-byte AES-CMAC tag compared by routine 0x10F0. */
    private DataType buildPayloadCmacTag() throws Exception {
        StructureDataType s = new StructureDataType(CAT, "PayloadCmacTag", 0);
        s.add(resolveArray(UnsignedCharDataType.dataType, 16), "tag",
                "AES-CMAC(DID_0x202_IV || plaintext[0:0xFF0])");
        return resolve(s);
    }

    /** Object 15 CPU mirror: first 16 bytes + key field at +0x10. */
    private DataType buildSecocObject15() throws Exception {
        StructureDataType s = new StructureDataType(CAT, "SecocNvmObject15", 0);
        s.add(resolveArray(UnsignedCharDataType.dataType, 16), "first_field",
                "First 16 bytes of the 32-byte object; OEM meaning unresolved");
        s.add(resolveArray(UnsignedCharDataType.dataType, 16), "key_field",
                "Second field; CMAC-verified SecOC key on related variants");
        return resolve(s);
    }

    /** One raw/XOR55/XORAA 32-byte restore destination group. */
    private DataType buildSecocWorkTriplet() throws Exception {
        StructureDataType s = new StructureDataType(CAT, "SecocNvmWorkTriplet", 0);
        s.add(resolveArray(UnsignedCharDataType.dataType, 32), "raw",
                "Raw NvM_ReadBlock destination");
        s.add(resolveArray(UnsignedCharDataType.dataType, 32), "xor55",
                "XOR55-encoded copy destination");
        s.add(resolveArray(UnsignedCharDataType.dataType, 32), "xoraa",
                "XORAA-encoded copy destination");
        return resolve(s);
    }

    /**
     * Four work groups rooted at application GP+0x5308 = 0xFEBF0B08
     * (docs/security/secoc/key-storage-and-lifecycle.md §3: four groups of three 32-byte work
     * buffers). The groups are generic transient restore slots, not fixed key-set
     * buffers; object 15 specifically uses group 3 at 0xFEBF0C28 / 0xC48 / 0xC68 (§8).
     */
    private DataType buildSecocWorkbufRoot(DataType triplet) throws Exception {
        StructureDataType s = new StructureDataType(CAT, "SecocNvmWorkbufRoot", 0);
        s.add(new ArrayDataType(triplet, 4, triplet.getLength()), "groups",
                "Four generic triplicate work groups (384 bytes)");
        return resolve(s);
    }

    /** Volatile 16-byte DID 0201 / 0202 buffers. */
    private DataType buildAesBlock16(String name, String comment) throws Exception {
        StructureDataType s = new StructureDataType(CAT, name, 0);
        s.add(resolveArray(UnsignedCharDataType.dataType, 16), "bytes", comment);
        return resolve(s);
    }

    /** Opaque sized buffer used for unresolved NvM / checkpoint mirrors. */
    private DataType buildOpaque(String name, int size) throws Exception {
        StructureDataType s = new StructureDataType(CAT, name, 0);
        s.add(resolveArray(UnsignedCharDataType.dataType, size), "bytes",
                "Opaque " + size + "-byte buffer; OEM fields unresolved");
        return resolve(s);
    }

    private void label(long addr, String name, String comment) throws Exception {
        Address a = toAddr(addr);
        SymbolTable symbols = currentProgram.getSymbolTable();
        Symbol symbol = symbols.getPrimarySymbol(a);
        if (symbol != null) {
            if (!name.equals(symbol.getName())) {
                symbol.setName(name, SourceType.USER_DEFINED);
            }
        } else {
            symbol = symbols.createLabel(a, name, SourceType.USER_DEFINED);
            symbol.setPrimary();
        }
        if (comment != null) {
            currentProgram.getListing().setComment(a,
                    ghidra.program.model.listing.CodeUnit.PLATE_COMMENT, comment);
        }
    }

    private void applyAt(long addr, DataType type, String name, String why)
            throws Exception {
        Address start = toAddr(addr);
        Address end = start.add(type.getLength() - 1L);
        if (addr < LOCAL_RAM_START || end.getOffset() > LOCAL_RAM_END) {
            throw new IllegalStateException(String.format(
                    "type %s at 0x%x is outside LocalRAM", type.getName(), addr));
        }
        MemoryBlock block = currentProgram.getMemory().getBlock(start);
        if (block == null || !"LocalRAM".equals(block.getName()) || !block.contains(end)) {
            throw new IllegalStateException(String.format(
                    "type %s at 0x%x is outside the LocalRAM block", type.getName(), addr));
        }
        if (type.getLength() <= 0) {
            throw new IllegalStateException("type " + type.getName() + " has empty length");
        }
        Listing listing = currentProgram.getListing();
        Data existing = listing.getDefinedDataAt(start);
        if (existing != null && existing.getDataType().isEquivalent(type)
                && existing.getLength() == type.getLength()) {
            if (name != null) label(addr, name, why);
            return;
        }
        Data container = listing.getDefinedDataContaining(start);
        if (container != null && !container.getAddress().equals(start)
                && container.getLength() > type.getLength()) {
            println(String.format(
                    "SKIP %s at 0x%x: contained in larger %s (%s)",
                    type.getName(), addr, container.getDataType().getName(), why));
            return;
        }
        listing.clearCodeUnits(start, end, false);
        createData(start, type);
        if (name != null) label(addr, name, why);
        println(String.format("Applied %s (%d bytes) at 0x%x (%s)",
                type.getName(), type.getLength(), addr, why));
    }

    private void applyScalar(long addr, DataType type, String name, String why)
            throws Exception {
        applyAt(addr, type, name, why);
    }

    private void applyCheckpointCsv(File csv) throws Exception {
        int applied = 0;
        try (BufferedReader br = new BufferedReader(new FileReader(csv))) {
            String header = br.readLine();
            if (header == null || !header.startsWith("object_index,")) {
                throw new IllegalStateException(
                        "unexpected checkpoint_payload_map.csv header: " + header);
            }
            String line;
            while ((line = br.readLine()) != null) {
                line = line.trim();
                if (line.isEmpty() || line.startsWith("#")) continue;
                String[] parts = line.split(",", -1);
                if (parts.length < 10) {
                    throw new IllegalStateException(
                            "checkpoint CSV row needs >=10 columns: " + line);
                }
                String enabled = parts[1].trim();
                if (!"yes".equalsIgnoreCase(enabled)) continue;
                int length = Integer.parseInt(parts[2].trim());
                long addr = Long.decode(parts[5].trim());
                String evidenceName = parts[7].trim();
                if (length <= 0 || evidenceName.isEmpty()) {
                    throw new IllegalStateException(
                            "enabled checkpoint missing length/name: " + line);
                }
                String typeName = "Checkpoint_" + evidenceName;
                DataType opaque = buildOpaque(typeName, length);
                applyAt(addr, opaque, "checkpoint_" + evidenceName,
                        "enabled checkpoint slot from checkpoint_payload_map.csv");
                applied++;
            }
        }
        println("Applied " + applied + " enabled checkpoint RAM mirrors from "
                + csv.getAbsolutePath());
    }

    @Override
    public void run() throws Exception {
        DataType u16 = UnsignedShortDataType.dataType;
        DataType u32 = UnsignedIntegerDataType.dataType;

        DataType flashCb = buildPayloadFlashCallback();
        DataType crcTrailer = buildPayloadCrcTrailer();
        DataType cmacTag = buildPayloadCmacTag();
        DataType object15 = buildSecocObject15();
        DataType triplet = buildSecocWorkTriplet();
        DataType workbufRoot = buildSecocWorkbufRoot(triplet);
        DataType did0201 = buildAesBlock16("PayloadDid0201KeyMaterial",
                "Volatile DID 0201 key-derivation input");
        DataType did0202 = buildAesBlock16("PayloadDid0202Iv",
                "Volatile DID 0202 AES-CBC IV / CMAC prefix");
        DataType obj0 = buildOpaque("SecocNvmObject0", 16);
        DataType obj1 = buildOpaque("SecocNvmObject1", 16);
        DataType obj2 = buildOpaque("SecocNvmObject2", 8);
        DataType obj3 = buildOpaque("SecocNvmObject3", 16);

        // Payload download trailer (bootloader programming path).
        applyAt(0xFEBF0FD0L, flashCb, "payload_flash_callback",
                "Flash-driver callback slot; public payloads store 0xFEBF0000");
        applyAt(0xFEBF0FE0L, crcTrailer, "payload_crc_trailer",
                "Embedded CRC address/length/patch words before the CMAC tag");
        applyAt(0xFEBF0FF0L, cmacTag, "payload_cmac_tag",
                "16-byte AES-CMAC tag verified by routine 0x10F0");

        // SecOC / NvM application-GP roots.
        applyAt(0xFEBF02E8L, object15, "secoc_nvm_object15_ram_mirror",
                "32-byte object-15 mirror; key field at +0x10");
        label(0xFEBF02F8L, "secoc_nvm_object15_key_field_ram",
                "Second 16-byte field of object 15 (member of SecocNvmObject15)");
        applyAt(0xFEBF0B08L, workbufRoot, "secoc_nvm_triplicate_workbuf_root",
                "Four groups of raw/XOR55/XORAA 32-byte buffers (GP+0x5308)");
        // Member labels for object 15's restore group (§8 of the SecOC lifecycle doc).
        label(0xFEBF0C28L, "secoc_nvm_object15_raw_workbuf",
                "Object-15 restore group: raw block-41 destination");
        label(0xFEBF0C48L, "secoc_nvm_object15_xor55_workbuf",
                "Object-15 restore group: XOR55 block-45 destination");
        label(0xFEBF0C68L, "secoc_nvm_object15_xoraa_workbuf",
                "Object-15 restore group: XORAA block-49 destination");

        applyAt(0xFEBEF400L, obj2, "secoc_nvm_object2_ram_mirror",
                "8-byte structured NvM object; not key material");
        applyAt(0xFEBEF468L, obj0, "secoc_nvm_object0_ram_mirror",
                "16-byte structured state; not a SecOC AES key");
        applyAt(0xFEBEF478L, obj1, "secoc_nvm_object1_ram_mirror",
                "16-byte structured NvM object; not a SecOC AES key");
        applyAt(0xFEBEF488L, obj3, "secoc_nvm_object3_ram_mirror",
                "16-byte structured NvM object; not a SecOC AES key");

        // Bootloader DID / UDS volatile cluster (boot GP-relative).
        applyAt(0xFEBF2D08L, did0201, "payload_did_0201_key_material",
                "Volatile 16-byte DID 0201 buffer");
        applyAt(0xFEBF2CF8L, did0202, "payload_did_0202_iv",
                "Volatile 16-byte DID 0202 buffer");
        applyScalar(0xFEBF2AB0L, UnsignedCharDataType.dataType, "uds_write_did_descriptor_index",
                "Selected index in the four-entry DID descriptor table");
        applyScalar(0xFEBF2AB1L, UnsignedCharDataType.dataType, "uds_write_did_pending",
                "Asynchronous 0201/0202 write pending flag");
        applyScalar(0xFEBF2AB2L, UnsignedCharDataType.dataType, "payload_did_sequence_state",
                "Required WDBI order state 0/1/2");
        applyScalar(0xFEBF2B0EL, UnsignedCharDataType.dataType, "uds_current_session",
                "Current UDS session: 1/2/3");
        applyScalar(0xFEBF2B0FL, UnsignedCharDataType.dataType, "uds_security_access_state",
                "SecurityAccess state; protected paths require 2");
        applyScalar(0xFEBF2B16L, UnsignedCharDataType.dataType, "payload_did_crypto_ready",
                "Set after successful DID 0202");
        applyScalar(0xFEBF2B6CL, u16, "uds_read_did_response_length",
                "ReadDID response payload length excluding SID 0x62");

        // Application handoff / phase landmarks (application GP 0xFEBEB800).
        // GP-relative roots use signed 16-bit displacements proved at 0x4C942/0x4C960/0x4C98C.
        // FEBF3B14/18/19 are absolute mov immediates, not GP-relative.
        applyScalar(0xFEBEB1A4L, UnsignedCharDataType.dataType, "application_system_transition_phase_live",
                "Live system-transition phase byte (GP-0x65C)");
        applyScalar(0xFEBEE81FL, UnsignedCharDataType.dataType, "application_system_transition_phase_snapshot",
                "Phase snapshot GP+0x301F; 0x11 blocks programming handoff");
        applyScalar(0xFEBEE892L, u16, "application_vehicle_speed_raw",
                "Unsigned speed GP+0x3092; >0x0180 -> NRC 0x88");
        applyScalar(0xFEBE6692L, u16, "application_supply_value_raw",
                "Scaled supply GP-0x516E; <0x0A00 blocks handoff");
        applyScalar(0xFEBE8152L, UnsignedCharDataType.dataType, "application_alternate_handoff_flag",
                "Must be clear for normal PROGRAMMING reset path (GP-0x36AE)");
        applyScalar(0xFEBE8166L, UnsignedCharDataType.dataType, "application_programming_reset_requested",
                "One-request marker set to 0x5A after event 9 (GP-0x369A)");
        applyAt(0xFEBF3B14L, u32, "application_programming_handoff_value",
                "Four-byte handoff payload; absolute mov 0xFEBF3B14");
        applyScalar(0xFEBF3B18L, UnsignedCharDataType.dataType, "application_programming_readiness_latch",
                "Set to 0x5A after readiness check; absolute mov 0xFEBF3B18");
        applyScalar(0xFEBF3B19L, UnsignedCharDataType.dataType, "application_programming_reset_latch",
                "Set to 0x5A after reset request succeeds; FEBF3B14+5");

        // Enabled checkpoint ring mirrors (sizes from evidence CSV).
        String[] args = getScriptArgs();
        if (args.length != 1) {
            throw new IllegalArgumentException(
                    "expected absolute checkpoint_payload_map.csv path");
        }
        File csv = new File(args[0]);
        if (!csv.isFile()) {
            throw new IllegalStateException("missing checkpoint CSV " + csv);
        }
        applyCheckpointCsv(csv);

        println("Applied P1M-E LocalRAM structure types under " + CAT);
    }
}
