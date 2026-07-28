//@author kaikozlov
//@category Analysis
// Apply evidence-backed StructureDataType / bitfield overlays on the P1M-E SFR
// windows seeded by ApplyP1MDeviceProfile. Invoked during project import after
// the SFR CSV labels are loaded. Types stay honest: reserved bits stay reserved,
// and only fields already used in-repo docs/firmware are named.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.ArrayDataType;
import ghidra.program.model.data.CategoryPath;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.DataTypeConflictHandler;
import ghidra.program.model.data.DataTypeManager;
import ghidra.program.model.data.StructureDataType;
import ghidra.program.model.data.UnsignedCharDataType;
import ghidra.program.model.data.UnsignedIntegerDataType;
import ghidra.program.model.data.UnsignedShortDataType;
import ghidra.program.model.listing.Data;
import ghidra.program.model.listing.Listing;
import ghidra.program.model.mem.MemoryBlock;

public class ApplyP1MSfrTypes extends GhidraScript {
    private static final CategoryPath CAT = new CategoryPath("/P1M_E_SFR");

    private DataTypeManager dtm() {
        return currentProgram.getDataTypeManager();
    }

    private DataType resolve(StructureDataType draft) {
        return dtm().addDataType(draft, DataTypeConflictHandler.REPLACE_HANDLER);
    }

    /** RH850 EICn layout (family-identical to P1L-C INTC); in-repo docs use EIRF/EIMK. */
    private DataType buildEicRegister() throws Exception {
        StructureDataType s = new StructureDataType(CAT, "EIC_Register", 0);
        s.setPackingEnabled(true);
        s.addBitField(UnsignedShortDataType.dataType, 4, "EIP",
                "Interrupt priority P[3:0] (0=highest)");
        s.addBitField(UnsignedShortDataType.dataType, 2, "reserved_4_5", "Reserved");
        s.addBitField(UnsignedShortDataType.dataType, 1, "EITB",
                "Vector method: 0=direct priority, 1=table reference");
        s.addBitField(UnsignedShortDataType.dataType, 1, "EIMK",
                "Interrupt mask (1=masked)");
        s.addBitField(UnsignedShortDataType.dataType, 4, "reserved_8_11", "Reserved");
        s.addBitField(UnsignedShortDataType.dataType, 1, "EIRF",
                "Interrupt request flag (foreground polls EIC136.EIRF)");
        s.addBitField(UnsignedShortDataType.dataType, 2, "reserved_13_14", "Reserved");
        s.addBitField(UnsignedShortDataType.dataType, 1, "EICT",
                "Channel type: 0=edge, 1=level (read-only)");
        return resolve(s);
    }

    /** ICU-S command word: firmware writes (key_slot << 16) | cmd. */
    private DataType buildIcusCommand() throws Exception {
        StructureDataType s = new StructureDataType(CAT, "ICUS_Command", 0);
        s.setPackingEnabled(true);
        s.addBitField(UnsignedIntegerDataType.dataType, 8, "CMD",
                "Command code (5 = recovered MAC generate, 7 = AES-CMAC verify)");
        s.addBitField(UnsignedIntegerDataType.dataType, 8, "reserved_8_15", "Reserved/unknown");
        s.addBitField(UnsignedIntegerDataType.dataType, 16, "KEY_SLOT",
                "ICU-S key-slot selector (SecOC uses slot 4)");
        return resolve(s);
    }

    /** ICU-S status word; driver polls bit 0 as busy/ready. */
    private DataType buildIcusStatus() throws Exception {
        StructureDataType s = new StructureDataType(CAT, "ICUS_Status", 0);
        s.setPackingEnabled(true);
        s.addBitField(UnsignedIntegerDataType.dataType, 1, "BUSY",
                "Firmware polls bit 0 before accepting a new command");
        s.addBitField(UnsignedIntegerDataType.dataType, 31, "reserved_1_31",
                "Remaining status bits (OEM names not claimed)");
        return resolve(s);
    }

    /** Common-FIFO status; rscfd_common_fifo_read tests bit 3. */
    private DataType buildCfsts() throws Exception {
        StructureDataType s = new StructureDataType(CAT, "RSCFD_CFSTS", 0);
        s.setPackingEnabled(true);
        s.addBitField(UnsignedIntegerDataType.dataType, 3, "reserved_0_2", "Reserved/unknown");
        s.addBitField(UnsignedIntegerDataType.dataType, 1, "status_b3",
                "Bit tested by rscfd_common_fifo_read before consuming a frame");
        s.addBitField(UnsignedIntegerDataType.dataType, 28, "reserved_4_31",
                "Remaining status bits (OEM names not claimed)");
        return resolve(s);
    }

    /** Tx buffer control byte; TMTR bit 0 starts transmission. */
    private DataType buildCfdtmc() throws Exception {
        StructureDataType s = new StructureDataType(CAT, "RSCFD_CFDTMC", 0);
        s.setPackingEnabled(true);
        s.addBitField(UnsignedCharDataType.dataType, 1, "TMTR",
                "Transmit request (set by rscfd_tx_buffer_submit)");
        s.addBitField(UnsignedCharDataType.dataType, 7, "reserved_1_7",
                "Remaining control bits (OEM names not claimed)");
        return resolve(s);
    }

    /** Classic common-FIFO / Tx message window used by this firmware (8-byte payloads). */
    private DataType buildFifoFrame(String name) throws Exception {
        StructureDataType s = new StructureDataType(CAT, name, 0);
        s.add(UnsignedIntegerDataType.dataType, "CFID",
                "CAN ID; bit 31 = IDE, low 29 bits = identifier");
        s.add(UnsignedIntegerDataType.dataType, "CFPTR",
                "Pointer/DLC word; DLC in bits 31:28");
        s.add(UnsignedIntegerDataType.dataType, "CFFDCSTS",
                "FD status/control (cleared for classic frames)");
        s.add(UnsignedIntegerDataType.dataType, "CFDF0", "Data bytes 0-3");
        s.add(UnsignedIntegerDataType.dataType, "CFDF1", "Data bytes 4-7");
        s.add(new ArrayDataType(UnsignedCharDataType.dataType, 0xC, 1), "reserved_14_1f",
                "Remainder of 0x20-byte message slot");
        return resolve(s);
    }

    private DataType buildTxMessageBuffer() throws Exception {
        StructureDataType s = new StructureDataType(CAT, "RSCFD_TxMessageBuffer", 0);
        s.add(UnsignedIntegerDataType.dataType, "CFDTMID",
                "Tx ID; bit 31 = IDE");
        s.add(UnsignedIntegerDataType.dataType, "CFDTMPTR",
                "DLC in bits 31:28");
        s.add(UnsignedIntegerDataType.dataType, "CFDTMFDCTR",
                "FD control; firmware writes zero for classic CAN");
        s.add(UnsignedIntegerDataType.dataType, "CFDTMDF0", "Data bytes 0-3");
        s.add(UnsignedIntegerDataType.dataType, "CFDTMDF1", "Data bytes 4-7");
        s.add(new ArrayDataType(UnsignedCharDataType.dataType, 0xC, 1), "reserved_14_1f",
                "Remainder of 0x20-byte Tx buffer");
        return resolve(s);
    }

    private void applyAt(long addr, DataType type, String why) throws Exception {
        Address start = toAddr(addr);
        Address end = start.add(type.getLength() - 1L);
        MemoryBlock block = currentProgram.getMemory().getBlock(start);
        if (block == null || !block.isVolatile() || !block.contains(end)) {
            throw new IllegalStateException(String.format(
                    "type %s at 0x%x is outside a mapped volatile SFR window",
                    type.getName(), addr));
        }
        if (type.getLength() <= 0) {
            throw new IllegalStateException("type " + type.getName() + " has empty length");
        }
        Listing listing = currentProgram.getListing();
        Data existing = listing.getDefinedDataAt(start);
        if (existing != null && existing.getDataType().isEquivalent(type)
                && existing.getLength() == type.getLength()) {
            return;
        }
        // Replace plain scalars from ApplyP1MDeviceProfile. Refuse only when a
        // larger overlapping definition starts before this address.
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
        println(String.format("Applied %s (%d bytes) at 0x%x (%s)",
                type.getName(), type.getLength(), addr, why));
    }

    @Override
    public void run() throws Exception {
        DataType eic = buildEicRegister();
        DataType icusCmd = buildIcusCommand();
        DataType icusSts = buildIcusStatus();
        DataType cfsts = buildCfsts();
        DataType cfdtmc = buildCfdtmc();
        DataType fifoFrame = buildFifoFrame("RSCFD_CommonFifoFrame");
        DataType txBuf = buildTxMessageBuffer();

        long[] eics = {
                0xFFFFB010L, 0xFFFFB10AL, 0xFFFFB10CL, 0xFFFFB10EL, 0xFFFFB110L,
                0xFFFFB176L, 0xFFFFB178L, 0xFFFFB248L, 0xFFFFB24AL, 0xFFFFB2F6L
        };
        for (long a : eics) {
            applyAt(a, eic, "EICn");
        }

        applyAt(0xFFC5D000L, icusCmd, "ICU-S command");
        applyAt(0xFFC5D00CL, icusSts, "ICU-S status");

        applyAt(0xFFD20178L, cfsts, "CFSTS base");
        applyAt(0xFFD20184L, cfsts, "CFSTS CAN1");
        applyAt(0xFFD20260L, cfdtmc, "diagnostic CFDTMC16");

        applyAt(0xFFD23400L, fifoFrame, "common-FIFO ch0");
        applyAt(0xFFD23580L, fifoFrame, "common-FIFO ch1");
        applyAt(0xFFD24000L, txBuf, "Tx buffer base n=0");
        applyAt(0xFFD24200L, txBuf, "Tx buffer n=16 diagnostic");

        println("Applied P1M-E SFR structure types under " + CAT);
    }
}
