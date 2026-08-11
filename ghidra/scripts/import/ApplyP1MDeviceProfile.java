//@author kaikozlov
//@category Analysis
// Apply RH850/P1M-E R7F701381 memory map, SFR volatility labels, and
// boot/application GP/TP register context. Invoked during project import.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.UnsignedCharDataType;
import ghidra.program.model.data.UnsignedIntegerDataType;
import ghidra.program.model.data.UnsignedLongDataType;
import ghidra.program.model.data.UnsignedShortDataType;
import ghidra.program.model.lang.Register;
import ghidra.program.model.listing.ProgramContext;
import ghidra.program.model.mem.Memory;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.symbol.SourceType;
import java.math.BigInteger;
import java.util.HashSet;
import java.util.Set;

public class ApplyP1MDeviceProfile extends GhidraScript {
    private MemoryBlock ensureUninitBlock(String name, long start, long size,
                                          boolean read, boolean write, boolean exec,
                                          boolean volatileBlock) throws Exception {
        Memory mem = currentProgram.getMemory();
        Address addr = toAddr(start);
        MemoryBlock existing = mem.getBlock(addr);
        if (existing != null) {
            if (!name.equals(existing.getName()) || !existing.getStart().equals(addr)
                    || existing.getSize() != size) {
                throw new IllegalStateException("conflicting block at " + addr + ": "
                        + existing.getName() + " " + existing.getStart() + ".."
                        + existing.getEnd());
            }
            existing.setRead(read);
            existing.setWrite(write);
            existing.setExecute(exec);
            existing.setVolatile(volatileBlock);
            return existing;
        }
        MemoryBlock block = mem.createUninitializedBlock(name, addr, size, false);
        block.setRead(read);
        block.setWrite(write);
        block.setExecute(exec);
        block.setVolatile(volatileBlock);
        println(String.format("Created %s %s..%s r=%s w=%s x=%s vol=%s",
                name, block.getStart(), block.getEnd(), read, write, exec, volatileBlock));
        return block;
    }

    private void label(long addr, String name, String comment) throws Exception {
        Address a = toAddr(addr);
        var symbols = currentProgram.getSymbolTable();
        var symbol = symbols.getPrimarySymbol(a);
        if (symbol != null) symbol.setName(name, SourceType.USER_DEFINED);
        else {
            symbol = symbols.createLabel(a, name, SourceType.USER_DEFINED);
            symbol.setPrimary();
        }
        if (comment != null) {
            currentProgram.getListing().setComment(a,
                ghidra.program.model.listing.CodeUnit.PLATE_COMMENT, comment);
        }
    }

    private void setRegRange(String regName, long value, long start, long endExclusive)
            throws Exception {
        Register reg = currentProgram.getRegister(regName);
        if (reg == null) throw new IllegalStateException("missing register " + regName);
        ProgramContext ctx = currentProgram.getProgramContext();
        ctx.setValue(reg, toAddr(start), toAddr(endExclusive - 1), BigInteger.valueOf(value));
        println(String.format("Context %s=0x%x over 0x%x..0x%x",
                regName, value, start, endExclusive - 1));
    }

    private DataType unsignedType(int size) {
        return switch (size) {
            case 1 -> UnsignedCharDataType.dataType;
            case 2 -> UnsignedShortDataType.dataType;
            case 4 -> UnsignedIntegerDataType.dataType;
            case 8 -> UnsignedLongDataType.dataType;
            default -> throw new IllegalArgumentException("unsupported SFR width " + size);
        };
    }

    private void loadSfrCsv(java.io.File csv) throws Exception {
        Set<Long> addresses = new HashSet<>();
        Set<String> names = new HashSet<>();
        try (java.io.BufferedReader br = new java.io.BufferedReader(new java.io.FileReader(csv))) {
            String header = br.readLine();
            if (!"address,name,size,access,comment".equals(header)) {
                throw new IllegalStateException("unexpected SFR CSV header: " + header);
            }
            String line;
            int lineNo = 1;
            while ((line = br.readLine()) != null) {
                lineNo++;
                line = line.trim();
                if (line.isEmpty() || line.startsWith("#")) continue;
                String[] parts = line.split(",", 5);
                if (parts.length != 5) {
                    throw new IllegalStateException("SFR CSV line " + lineNo
                            + " must have five columns");
                }
                long addr = Long.decode(parts[0].trim());
                String name = parts[1].trim();
                int size = Integer.parseInt(parts[2].trim());
                String access = parts[3].trim();
                String comment = parts[4].trim();
                if (!addresses.add(addr)) {
                    throw new IllegalStateException(String.format(
                            "duplicate SFR address 0x%x at line %d", addr, lineNo));
                }
                if (name.isEmpty() || !names.add(name)) {
                    throw new IllegalStateException("empty/duplicate SFR name at line " + lineNo);
                }
                if (!Set.of("r", "w", "rw").contains(access)) {
                    throw new IllegalStateException("invalid SFR access at line " + lineNo);
                }
                DataType type = unsignedType(size);
                Address start = toAddr(addr);
                Address end = start.add(size - 1L);
                MemoryBlock block = currentProgram.getMemory().getBlock(start);
                if (addr < 0xFF600000L || block == null || !block.isVolatile()
                        || !block.contains(end)) {
                    throw new IllegalStateException(String.format(
                            "SFR %s 0x%x..0x%x is outside a mapped volatile window",
                            name, addr, addr + size - 1L));
                }
                label(addr, name, comment + " [" + access + ", u" + (size * 8) + "]");
                var existingData = currentProgram.getListing().getDataAt(start);
                if (existingData == null || !existingData.isDefined()) {
                    createData(start, type);
                } else if (existingData.getLength() != size) {
                    throw new IllegalStateException("conflicting SFR data width for " + name);
                }
            }
        }
        println("Loaded " + addresses.size() + " validated SFR labels from "
                + csv.getAbsolutePath());
    }

    @Override
    public void run() throws Exception {
        // R7F701381 memory map (P1M-E hardware manual):
        //   CodeFlash    0x00000000-0x000FFFFF  (already imported)
        //   DataFlash    0xFF200000-0xFF207FFF  (already imported)
        //   Local RAM    0xFEBE0000-0xFEBFFFFF
        //   Global RAM A 0xFEEF8000-0xFEEFFFFF
        //   Global RAM B 0xFEF00000-0xFEF07FFF
        // Peripheral SFRs are volatile in v850.pspec for the full 0xFF600000..
        // 0xFFFFFFFF window, but only verified peripheral *windows* are mapped
        // as memory blocks. Mapping the entire 10 MiB SFR range makes random
        // CodeFlash immediates look like valid pointers and collapses disassembly.
        ensureUninitBlock("LocalRAM", 0xFEBE0000L, 0x20000L, true, true, false, false);
        ensureUninitBlock("GlobalRAM_A", 0xFEEF8000L, 0x8000L, true, true, false, false);
        ensureUninitBlock("GlobalRAM_B", 0xFEF00000L, 0x8000L, true, true, false, false);
        // The CH0 sample path uses two 432-entry DMA rings in Global RAM A.
        // Firmware DMA descriptors source ADCG0DIR00/ADCG1DIR00 and target these
        // addresses; names are structural and do not claim physical ADC pins.
        label(0xFEEF81E0L, "ADCG0_DMA_SAMPLE_RING",
                "432-entry x32-bit Global RAM ring fed from ADCG0DIR00 by DMAC");
        label(0xFEEF8A20L, "ADCG1_DMA_SAMPLE_RING",
                "432-entry x32-bit Global RAM ring fed from ADCG1DIR00 by DMAC");
        // EIC / interrupt-control SFRs (EIC136, EIC292, EIC293, …).
        ensureUninitBlock("SFR_EIC", 0xFFFFB000L, 0x1000L, true, true, false, true);
        // RSCFD / RSCAN channel register window used by application CAN.
        ensureUninitBlock("SFR_RSCFD", 0xFFD20000L, 0x10000L, true, true, false, true);
        // ICU-S crypto-driver command/status window (see architecture evidence).
        ensureUninitBlock("SFR_ICUS", 0xFFC5D000L, 0x1000L, true, true, false, true);
        // PLL / clock generation SFRs written by boot_clock_init (0x10C6) and
        // application PLL reconfig (0x607DE): 0xFFF88818 config, 0xFFF890C0
        // control, 0xFFF890C8 status.
        ensureUninitBlock("SFR_CLKGEN", 0xFFF88000L, 0x2000L, true, true, false, true);
        // Flash sequencer SFRs written throughout boot/flashing: 0xFFD62000-0x44
        // FCU command/protection window (enable key 0xA5), 0xFFD60000/0xFFD61000
        // DataFlash bank control.
        ensureUninitBlock("SFR_FCU", 0xFFD62000L, 0x100L, true, true, false, true);
        // ADCG0/1 windows supplying the DMA-backed phase-sample rings.
        ensureUninitBlock("SFR_ADCG0", 0xFFF91000L, 0x1000L, true, true, false, true);
        ensureUninitBlock("SFR_ADCG1", 0xFFF92000L, 0x1000L, true, true, false, true);
        // DMAC channel-master settings used by the sample-transfer setup.
        ensureUninitBlock("SFR_DMAC_CM", 0xFFFF8100L, 0x40L, true, true, false, true);
        // TSG30/31 motor-control timer windows. The CH0 commit worker at 0x60DDC
        // writes extended HT-PWM W/V/U compare registers at offsets 0x180/184/188.
        ensureUninitBlock("SFR_TSG3", 0xFFE70000L, 0x2000L, true, true, false, true);

        // Boot code occupies low CodeFlash; application starts at 0x20000.
        // GP/TP are constant within each region after startup.
        setRegRange("gp", 0xFEBF9800L, 0x00000000L, 0x00020000L);
        setRegRange("tp", 0x0000869CL, 0x00000000L, 0x00020000L);
        setRegRange("gp", 0xFEBEB800L, 0x00020000L, 0x00100000L);
        setRegRange("tp", 0x00023EE4L, 0x00020000L, 0x00100000L);

        // SP only at known startup entry points (not a global constant).
        Register sp = currentProgram.getRegister("sp");
        ProgramContext ctx = currentProgram.getProgramContext();
        ctx.setValue(sp, toAddr(0x1b0L), toAddr(0x1b0L), BigInteger.valueOf(0xFEBE8000L));
        ctx.setValue(sp, toAddr(0x20880L), toAddr(0x20880L), BigInteger.valueOf(0xFEBE2000L));

        // Required, validated CSV of observed SFR labels and access widths.
        // Structured bitfield/frame overlays are applied by ApplyP1MSfrTypes.
        // LocalRAM structure overlays are applied by ApplyRamTypes.
        String[] args = getScriptArgs();
        if (args.length != 1) {
            throw new IllegalArgumentException("expected absolute p1m_sfr_labels.csv path");
        }
        java.io.File csv = new java.io.File(args[0]);
        if (!csv.isFile()) throw new IllegalStateException("missing SFR CSV " + csv);
        loadSfrCsv(csv);

        println("Seeded SP at boot_reset_startup and application_entry only");
    }
}
