//@author kaikozlov
//@category Analysis
// Apply RH850/P1M-E R7F701381 memory map, SFR volatility labels, and
// boot/application GP/TP register context. Invoked during project import.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.lang.Register;
import ghidra.program.model.listing.ProgramContext;
import ghidra.program.model.mem.Memory;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.symbol.SourceType;
import java.math.BigInteger;

public class ApplyP1MDeviceProfile extends GhidraScript {
    private MemoryBlock ensureUninitBlock(String name, long start, long size,
                                          boolean read, boolean write, boolean exec,
                                          boolean volatileBlock) throws Exception {
        Memory mem = currentProgram.getMemory();
        Address addr = toAddr(start);
        MemoryBlock existing = mem.getBlock(addr);
        if (existing != null) {
            if (!name.equals(existing.getName())) {
                // Overlap with a differently named block — leave it.
                println("block already present at " + addr + ": " + existing.getName());
            }
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

    @Override
    public void run() throws Exception {
        // R7F701381 memory map (P1M-E hardware manual):
        //   CodeFlash  0x00000000-0x000FFFFF  (already imported)
        //   DataFlash  0xFF200000-0xFF207FFF  (already imported)
        //   Local RAM  0xFEBE0000-0xFEBFFFFF
        // Peripheral SFRs are volatile in v850.pspec for the full 0xFF600000..
        // 0xFFFFFFFF window, but only verified peripheral *windows* are mapped
        // as memory blocks. Mapping the entire 10 MiB SFR range makes random
        // CodeFlash immediates look like valid pointers and collapses disassembly.
        ensureUninitBlock("LocalRAM", 0xFEBE0000L, 0x20000L, true, true, false, false);
        // EIC / interrupt-control SFRs (EIC136, EIC292, EIC293, …).
        ensureUninitBlock("SFR_EIC", 0xFFFFB000L, 0x1000L, true, true, false, true);
        // RSCFD / RSCAN channel register window used by application CAN.
        ensureUninitBlock("SFR_RSCFD", 0xFFD20000L, 0x10000L, true, true, false, true);
        // ICU-S crypto-driver command/status window (see architecture evidence).
        ensureUninitBlock("SFR_ICUS", 0xFFC5D000L, 0x1000L, true, true, false, true);

        // Frequently referenced SFRs from architecture analysis.
        label(0xFFFFB110L, "EIC136", "TAUJ0 CH3 interrupt control (EIRF polled by foreground loop).");
        label(0xFFFFB248L, "EIC292", "ICU-S crypto-driver interrupt control channel 292.");
        label(0xFFFFB24AL, "EIC293", "ICU-S crypto-driver interrupt control channel 293.");

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

        // Optional CSV of observed SFR labels. Prefer script arg, else cwd-relative.
        java.io.File csv = null;
        String[] args = getScriptArgs();
        if (args.length >= 1) csv = new java.io.File(args[0]);
        if (csv == null || !csv.isFile()) csv = new java.io.File("data/p1m_sfr_labels.csv");
        if (csv.isFile()) {
            try (java.io.BufferedReader br = new java.io.BufferedReader(new java.io.FileReader(csv))) {
                String line = br.readLine(); // header
                while ((line = br.readLine()) != null) {
                    line = line.trim();
                    if (line.isEmpty() || line.startsWith("#")) continue;
                    String[] parts = line.split(",", 5);
                    if (parts.length < 2) continue;
                    long addr = Long.decode(parts[0].trim());
                    String name = parts[1].trim();
                    String comment = parts.length >= 5 ? parts[4].trim() : null;
                    label(addr, name, comment);
                }
            }
            println("Loaded SFR labels from " + csv.getAbsolutePath());
        } else {
            println("No SFR CSV found; using built-in EIC labels only");
        }

        println("Seeded SP at boot_reset_startup and application_entry only");
    }
}
