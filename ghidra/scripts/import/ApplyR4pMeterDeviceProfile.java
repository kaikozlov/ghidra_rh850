//@author kaikozlov
//@category Analysis
// Exact yc 2024 RAV4 Prime meter 838004AD91 capture. The MCU part is not
// established: no P1M-E SFR map or RAM aliases are imported by this profile.
import ghidra.app.script.GhidraScript;
import ghidra.framework.options.Options;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.ArrayDataType;
import ghidra.program.model.data.ByteDataType;
import ghidra.program.model.lang.Register;
import ghidra.program.model.listing.CodeUnit;
import ghidra.program.model.listing.Program;
import ghidra.program.model.mem.Memory;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.symbol.SourceType;
import java.io.ByteArrayInputStream;
import java.math.BigInteger;
import java.security.MessageDigest;

public class ApplyR4pMeterDeviceProfile extends GhidraScript {
    private static final String CODE_SHA = "cc75cac2aaa4a648dadcad3d3d59d0c1bb293c53f1dbfcf9bc0fc88b4b6a4322";
    private static final String BOOT_SHA = "e8c3058f637725ca9a32b3ec6e38eb9408cf76c18847139cac22b853da6225d9";
    private static final String DATA_SHA = "569ef4661fb2e98a156c698e3eba160d6389cd811b41a75cebb78baa681618eb";
    private static final long RAM_START = 0xFEDC0000L;
    private static final long RAM_END = 0xFEE00000L;

    // {table row, destination, source start, source end, executable}.
    // 0x1170/0x1188 describe executable copies; 0x1178/0x1190 data copies.
    // The code-copy loops at C1E/DAE synchronize their instruction streams.
    private static final long[][] COPIES = {
        {0x11A0, 0xFEDC0110L, 0x1510, 0x34A0, 1},
        {0x11C8, 0xFEDC20D0L, 0x34A0, 0x9F2C, 1},
        {0x11D4, 0xFEDC8B5CL, 0x01000000, 0x010075B4, 1},
        {0x11E0, 0xFEDD0110L, 0x9F2C, 0xB8C0, 1},
        {0x11AC, 0xFEDD3A98L, 0xC0AC, 0xCD00, 0},
        {0x11F8, 0xFEDD46ECL, 0xCD00, 0xD370, 0},
        {0x1204, 0xFEDD4D5CL, 0x010075B4, 0x01007C94, 0},
        {0x1210, 0xFEDD543CL, 0xD370, 0xDF0C, 0},
        {0x11EC, 0xFEDD8000L, 0xB8C0, 0xC0AC, 1},
        {0x121C, 0xFEDDA884L, 0xDF0C, 0xDF50, 0},
    };

    private void requireImage(long start, int size, String expected) throws Exception {
        MessageDigest md = MessageDigest.getInstance("SHA-256");
        byte[] buffer = new byte[0x4000];
        for (int offset = 0; offset < size; offset += buffer.length) {
            int count = Math.min(buffer.length, size - offset);
            if (currentProgram.getMemory().getBytes(toAddr(start + offset), buffer, 0, count) != count) {
                throw new IllegalStateException("incomplete image at " + toAddr(start + offset));
            }
            md.update(buffer, 0, count);
        }
        StringBuilder actual = new StringBuilder();
        for (byte b : md.digest()) actual.append(String.format("%02x", b & 0xff));
        if (!expected.equals(actual.toString())) {
            throw new IllegalStateException("wrong R4P image at " + toAddr(start) + ": " + actual);
        }
    }

    private MemoryBlock partition(String name, long start, long end, boolean executable) throws Exception {
        Memory mem = currentProgram.getMemory();
        MemoryBlock block = mem.getBlock(toAddr(start));
        if (block == null || !block.isInitialized() || block.getEnd().getOffset() < end - 1) {
            throw new IllegalStateException("missing contiguous flash range " + name);
        }
        if (!block.getStart().equals(toAddr(start))) mem.split(block, toAddr(start));
        block = mem.getBlock(toAddr(start));
        if (block.getEnd().getOffset() >= end) mem.split(block, toAddr(end));
        block = mem.getBlock(toAddr(start));
        block.setName(name);
        block.setRead(true);
        block.setWrite(false);
        block.setExecute(executable);
        return block;
    }

    private void erased(String name, long start, long end) throws Exception {
        MemoryBlock block = partition(name, start, end, false);
        byte[] bytes = new byte[(int) (end - start)];
        currentProgram.getMemory().getBytes(block.getStart(), bytes);
        for (byte b : bytes) {
            if (b != (byte) 0xff) throw new IllegalStateException("non-erased byte in " + name);
        }
        if (getDataAt(block.getStart()) == null) {
            createData(block.getStart(), new ArrayDataType(ByteDataType.dataType, bytes.length, 1));
        }
    }

    private void flashLayout() throws Exception {
        partition("BootResetCode", 0, 0x1248, true);
        erased("BootResetFFFill", 0x1248, 0x1400);
        partition("BootRelocationSource", 0x1400, 0xC0AC, true);
        partition("BootRelocationDataSource", 0xC0AC, 0xDF50, false);
        erased("BootRelocationFFFill", 0xDF50, 0xDFFC);
        partition("BootMetadata", 0xDFFC, 0xE000, false);
        partition("BootCheckPattern", 0xE000, 0xE100, false);
        erased("BootTailFFFill", 0xE100, 0x10000);
        partition("ApplicationCode", 0x10000, 0xD7D38, true);
        erased("ApplicationCodeFFFill", 0xD7D38, 0xD8674);
        partition("ApplicationDataLow", 0xD8674, 0xD88B0, false);
        erased("ApplicationDataFFFill", 0xD88B0, 0xD919E);
        partition("ApplicationData", 0xD919E, 0x177A50, false);
        // The large erased run starts before 0x180000 and extends into bank 1F.
        erased("ApplicationTailFFFill", 0x177A50, 0x1FAFE0);
        partition("HighBankCode", 0x1FAFE0, 0x1FCA88, true);
        partition("HighBankData", 0x1FCA88, 0x1FCAD8, false);
        erased("HighBankFFFill", 0x1FCAD8, 0x1FFFE0);
        partition("ApplicationMetadata", 0x1FFFE0, 0x1FFFF0, false);
        erased("CodeFlashEndFFFill", 0x1FFFF0, 0x200000);
        partition("ExtendedUserCode", 0x01000000, 0x010075B4, true);
        partition("ExtendedUserData", 0x010075B4, 0x01008000, false);
    }

    private void ramGap(long start, long end) throws Exception {
        if (start == end) return;
        MemoryBlock block = currentProgram.getMemory().createUninitializedBlock(
            String.format("RuntimeRAM_%08X", start), toAddr(start), end - start, false);
        block.setRead(true);
        block.setWrite(true);
        block.setExecute(false);
        block.setComment("Observed startup RAM range; uninitialized in this reprogramming-state snapshot. " +
            "Application startup reuses this physical RAM; not a device-wide peripheral map.");
    }

    private void runtimeCopies() throws Exception {
        Memory mem = currentProgram.getMemory();
        for (long[] row : COPIES) {
            for (int i = 0; i < 3; i++) {
                long actual = Integer.toUnsignedLong(mem.getInt(toAddr(row[0] + i * 4)));
                if (actual != row[i + 1]) throw new IllegalStateException("relocation row drift at " + toAddr(row[0]));
            }
        }
        long cursor = RAM_START;
        for (long[] row : COPIES) {
            long start = row[1];
            int size = (int) (row[3] - row[2]);
            if (mem.getBlock(toAddr(start)) != null) {
                throw new IllegalStateException("R4P profile requires fresh, unmapped runtime RAM at " + toAddr(start));
            }
            ramGap(cursor, start);
            byte[] bytes = new byte[size];
            mem.getBytes(toAddr(row[2]), bytes);
            MemoryBlock block = mem.createInitializedBlock(
                String.format("Rprg%s_%08X", row[4] == 1 ? "Code" : "Data", start),
                toAddr(start), new ByteArrayInputStream(bytes), size, monitor, false);
            block.setRead(true);
            block.setWrite(true);
            block.setExecute(row[4] == 1);
            block.setComment(String.format("Reprogramming-state copy: row %04X, source [%08X,%08X). " +
                "Overlaps the application's separately initialized RAM; do not treat as application constants.",
                row[0], row[2], row[3]));
            cursor = start + size;
        }
        ramGap(cursor, RAM_END);
    }

    private void context(String name, long value, long start, long end) throws Exception {
        Register register = currentProgram.getRegister(name);
        if (register == null) throw new IllegalStateException("missing register " + name);
        currentProgram.getProgramContext().setValue(register, toAddr(start), toAddr(end - 1), BigInteger.valueOf(value));
    }

    private void bootContext(long start, long end) throws Exception {
        context("gp", 0xFEDD9AD4L, start, end);
        context("tp", 0xFEDDBA98L, start, end);
        context("ep", 0xFEDD5FD8L, start, end);
    }

    private void label(long offset, String name, String comment) throws Exception {
        Address address = toAddr(offset);
        var symbols = currentProgram.getSymbolTable();
        var symbol = symbols.getPrimarySymbol(address);
        if (symbol == null) symbol = symbols.createLabel(address, name, SourceType.USER_DEFINED);
        else if (!name.equals(symbol.getName())) symbol.setName(name, SourceType.USER_DEFINED);
        symbol.setPrimary();
        currentProgram.getListing().setComment(address, CodeUnit.PLATE_COMMENT, comment);
    }

    @Override
    public void run() throws Exception {
        if (!"v850e3:LE:32:default".equals(currentProgram.getLanguageID().toString()) ||
                !"default".equals(currentProgram.getCompilerSpec().getCompilerSpecID().toString())) {
            throw new IllegalStateException("R4P meter requires v850e3:LE:32:default with GHS (not v850e3x)");
        }
        requireImage(0, 0x200000, CODE_SHA);
        requireImage(0x01000000, 0x8000, BOOT_SHA);
        requireImage(0xFF200000L, 0x10000, DATA_SHA);
        // D1L/D1M R01UH0451EJ0220 Fig. 5.1 (p377), Fig. 52.3 (p3679):
        // 64 KiB DataFlash at FF200000 is compatible; this does not identify the MCU.
        MemoryBlock data = currentProgram.getMemory().getBlock(toAddr(0xFF200000L));
        if (!data.getStart().equals(toAddr(0xFF200000L)) || data.getSize() != 0x10000) {
            throw new IllegalStateException("expected exact 64 KiB DataFlash mapping");
        }
        data.setRead(true);
        data.setWrite(true);
        data.setExecute(false);
        flashLayout();
        runtimeCopies();

        // F24/F2A/F30 configure the boot/reprogramming state. Application reset
        // 106F6/106F8 instead loads GP/TP from 10B48/10B4C. EP is reused for
        // temporary table pointers in the application, so no fixed APP EP exists.
        bootContext(0, 0x10000);
        bootContext(0x01000000, 0x01008000);
        bootContext(RAM_START, RAM_END);
        context("gp", 0xFEDC04C0L, 0x10000, 0x200000);
        context("tp", 0xD9FE0, 0x10000, 0x200000);
        Options analysis = currentProgram.getOptions(Program.ANALYSIS_PROPERTIES);
        String analyzer = "v850 Constant Reference Analyzer.";
        analysis.setString(analyzer + "Fixed GP value", "");
        analysis.setString(analyzer + "Fixed TP value", "");
        analysis.setString(analyzer + "Fixed EP value", "");
        analysis.setBoolean(analyzer + "Trust values read from writable memory", false);
        // 7982C returns. The discovered-noReturn heuristic previously removed
        // continuations at 161 calls to it; disable before the first analysis.
        analysis.setBoolean("Non-Returning Functions - Discovered", false);

        label(0x1FFFE0, "r4p_application_entry_metadata", "First word is application reset entry 00010634; original capture bytes preserved.");
        label(0x166064, "r4p_application_bss_descriptor", "Application initializer 84EB0 clears [FEDC04C0,FEDFFBB8), overwriting RPRG code/data. Alternate lifetime, not a second simultaneous RAM image.");
        label(0x16606C, "r4p_application_data_copy_descriptor", "Application initializer 84EB0 copies CF[D9B38,D9FE0) to FEDC0018. Not applied over the reprogramming-state RAM snapshot.");
        label(0x10B48, "r4p_application_gp_initial_value", "Application GP=FEDC04C0; unlike boot GP=FEDD9AD4.");
        label(0x10B4C, "r4p_application_tp_initial_value", "Application TP=D9FE0; unlike boot TP=FEDDBA98.");
        println("ApplyR4pMeterDeviceProfile: pinned 2 MiB capture, exact flash partitions, 10 runtime copies, and separate boot/application context");
    }
}
