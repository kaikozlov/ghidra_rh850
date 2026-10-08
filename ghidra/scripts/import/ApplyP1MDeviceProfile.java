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

    private MemoryBlock ensureByteMappedBlock(String name, long start, long mappedStart,
                                               long size, boolean read, boolean write,
                                               boolean exec) throws Exception {
        Memory mem = currentProgram.getMemory();
        Address addr = toAddr(start);
        MemoryBlock existing = mem.getBlock(addr);
        if (existing != null) {
            if (!name.equals(existing.getName()) || !existing.getStart().equals(addr)
                    || existing.getSize() != size || !existing.isMapped()) {
                throw new IllegalStateException("conflicting mapped block at " + addr);
            }
            existing.setRead(read);
            existing.setWrite(write);
            existing.setExecute(exec);
            existing.setVolatile(false);
            return existing;
        }
        MemoryBlock block = mem.createByteMappedBlock(
                name, addr, toAddr(mappedStart), size, false);
        block.setRead(read);
        block.setWrite(write);
        block.setExecute(exec);
        block.setVolatile(false);
        println(String.format("Created %s %s..%s -> 0x%x r=%s w=%s x=%s",
                name, block.getStart(), block.getEnd(), mappedStart, read, write, exec));
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
                if (block == null || !block.isVolatile() || !block.contains(end)) {
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
        // R7F701381/R7F701383 memory map (P1M-E hardware manual):
        //   user CodeFlash     0x00000000-0x000FFFFF  (already imported)
        //   extended user area 0x01000000-0x01007FFF  (not present in dumps)
        //   DataFlash          0xFF200000-0xFF207FFF  (already imported)
        //   PE1 Local RAM      0xFEBE0000-0xFEBFFFFF
        //   self Local RAM     0xFEDE0000-0xFEDFFFFF  (same physical RAM)
        //   Global RAM A       0xFEEF8000-0xFEEFFFFF
        //   Global RAM B       0xFEF00000-0xFEF07FFF
        // Section 4.2.1 documents instruction fetch from the self Local-RAM
        // view and Global RAM. Exact firmware and retained live payloads also
        // prove fetch through the PE1 view used by Toyota's callback path.
        ensureUninitBlock("LocalRAM", 0xFEBE0000L, 0x20000L, true, true, true, false);
        ensureByteMappedBlock("LocalRAM_self", 0xFEDE0000L, 0xFEBE0000L,
                0x20000L, true, true, true);
        ensureUninitBlock("GlobalRAM_A", 0xFEEF8000L, 0x8000L, true, true, true, false);
        ensureUninitBlock("GlobalRAM_B", 0xFEF00000L, 0x8000L, true, true, true, false);
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
        // CodeFlash ECC/address-parity safety registers. The boot validity
        // helper reads UCFDERSTR and clears it through UCFDERSTCLR.
        ensureUninitBlock("SFR_CODEFLASH_ECC", 0xFFC62000L, 0x500L,
                true, true, false, true);
        // RAM initialization disable controls for reset-class retention.
        ensureUninitBlock("SFR_STAC", 0xFFF81000L, 0x1000L, true, true, false, true);
        // Clock-generation window. The boot path configures EXTCLK1O through
        // CLKD3DIV/CLKD3STAT and CKSC3C/CKSC3S; it does not reconfigure the PLL.
        ensureUninitBlock("SFR_CLKGEN", 0xFFF88000L, 0x2000L, true, true, false, true);
        // Flash interface (FACI), command-issuing area, self-ID, and base selector.
        ensureUninitBlock("SFR_FACI_ID", 0xFFA08000L, 0x20L, true, true, false, true);
        ensureUninitBlock("SFR_FACI", 0xFFA10000L, 0x200L, true, true, false, true);
        ensureUninitBlock("SFR_FACI_COMMAND", 0xFFA20000L, 0x4L, true, true, false, true);
        ensureUninitBlock("SFR_FACI_CONFIG", 0xFFC59000L, 0x100L, true, true, false, true);
        // Error Control Module master, checker, common, and error-pulse windows.
        ensureUninitBlock("SFR_ECM_MASTER", 0xFFD60000L, 0x100L, true, true, false, true);
        ensureUninitBlock("SFR_ECM_CHECKER", 0xFFD61000L, 0x100L, true, true, false, true);
        ensureUninitBlock("SFR_ECM_COMMON", 0xFFD62000L, 0x100L, true, true, false, true);
        ensureUninitBlock("SFR_ECM_PULSE", 0xFFD63000L, 0x100L, true, true, false, true);
        // ADCG0/1 windows supplying the DMA-backed phase-sample rings.
        ensureUninitBlock("SFR_ADCG0", 0xFFF91000L, 0x1000L, true, true, false, true);
        ensureUninitBlock("SFR_ADCG1", 0xFFF92000L, 0x1000L, true, true, false, true);
        // DMAC channel-master settings used by the sample-transfer setup.
        ensureUninitBlock("SFR_DMAC_CM", 0xFFFF8100L, 0x40L, true, true, false, true);
        // TSG30/31 motor-control timer windows. The CH0 commit worker at 0x60DDC
        // writes extended HT-PWM W/V/U compare registers at offsets 0x180/184/188.
        ensureUninitBlock("SFR_TSG3", 0xFFE70000L, 0x2000L, true, true, false, true);
        // TAUJ0/1/2 are consecutive 0x1000-byte modules on the 80-MHz P-Bus.
        ensureUninitBlock("SFR_TAUJ", 0xFFE50000L, 0x3000L, true, true, false, true);

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
