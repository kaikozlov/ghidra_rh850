//@author kaikozlov
//@category Investigation
// Read-only whole-image semantic coverage ledger: one deterministic CSV row per
// recovered function. Reports only structural Ghidra facts and discovery
// provenance. Semantic review/evidence fields are emitted blank and populated
// later from the curated semantic_review_status.csv.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressIterator;
import ghidra.program.model.address.AddressSetView;
import ghidra.program.model.listing.Data;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.listing.Listing;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceManager;
import ghidra.program.model.symbol.SourceType;
import ghidra.program.model.symbol.Symbol;

import java.io.PrintWriter;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

public class ExportSemanticCoverageLedger extends GhidraScript {
    private static final long CODEFLASH_END = 0x100000L;
    private static final long LOCAL_RAM_START = 0xFEBE0000L;
    private static final long LOCAL_RAM_END = 0xFEC00000L; // exclusive
    private static final long APPLICATION_BASE = 0x20000L;
    private static final long SCHEDULER_ROOT = 0x64fccL;

    private static final String HEADER = String.join(",",
            "entry_addr",
            "body_bytes",
            "name",
            "discovery_source",
            "discovery_provenance",
            "name_source",
            "is_thunk",
            "calling_convention",
            "caller_count",
            "callee_count",
            "indirect_reference_count",
            "root_kind",
            "ram_ref_count",
            "ram_read_ref_count",
            "ram_write_ref_count",
            "mmio_ref_count",
            "codeflash_data_ref_count",
            "string_ref_count",
            "subsystem",
            "review_state",
            "evidence_grade",
            "verification_source",
            "oracle_class",
            "execution_status",
            "review_date",
            "review_result");

    private static final class Row {
        long entry;
        long bodyBytes;
        String name;
        String discoverySource;
        String discoveryProvenance;
        String nameSource;
        boolean thunk;
        String callingConvention;
        int callers;
        int callees;
        int indirectReferences;
        String rootKind;
        int ramRefs;
        int ramReadRefs;
        int ramWriteRefs;
        int mmioRefs;
        int codeflashDataRefs;
        int stringRefs;
        String subsystem;
    }

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length != 1) {
            throw new IllegalArgumentException(
                    "expected absolute CSV output path");
        }
        Path outPath = Path.of(args[0]);
        if (!outPath.isAbsolute()) {
            throw new IllegalArgumentException("CSV output path must be absolute: " + outPath);
        }
        if (outPath.getParent() != null) {
            Files.createDirectories(outPath.getParent());
        }

        FunctionManager fm = currentProgram.getFunctionManager();
        ReferenceManager rm = currentProgram.getReferenceManager();
        Listing listing = currentProgram.getListing();
        List<Row> rows = new ArrayList<>();

        FunctionIterator it = fm.getFunctions(true);
        while (it.hasNext()) {
            Function f = it.next();
            rows.add(buildRow(f, fm, rm, listing));
        }

        rows.sort(Comparator.comparingLong(r -> r.entry));

        // Deterministic uniqueness guard before write.
        long prev = -1L;
        for (Row row : rows) {
            if (row.entry == prev) {
                throw new IllegalStateException(
                        "duplicate function entry address 0x" + Long.toHexString(row.entry));
            }
            prev = row.entry;
        }

        try (PrintWriter out = new PrintWriter(Files.newBufferedWriter(outPath))) {
            out.println(HEADER);
            for (Row row : rows) {
                out.printf("%s,%d,%s,%s,%s,%s,%s,%s,%d,%d,%d,%s,%d,%d,%d,%d,%d,%d,%s,,,,,,,%n",
                        addrHex(row.entry),
                        row.bodyBytes,
                        csv(row.name),
                        csv(row.discoverySource),
                        csv(row.discoveryProvenance),
                        csv(row.nameSource),
                        row.thunk ? "true" : "false",
                        csv(row.callingConvention),
                        row.callers,
                        row.callees,
                        row.indirectReferences,
                        csv(row.rootKind),
                        row.ramRefs,
                        row.ramReadRefs,
                        row.ramWriteRefs,
                        row.mmioRefs,
                        row.codeflashDataRefs,
                        row.stringRefs,
                        csv(row.subsystem));
            }
        }

        println("ExportSemanticCoverageLedger: wrote " + rows.size()
                + " functions to " + outPath);
    }

    private Row buildRow(Function f, FunctionManager fm, ReferenceManager rm, Listing listing) {
        Row row = new Row();
        Address entry = f.getEntryPoint();
        row.entry = entry.getOffset();
        row.bodyBytes = f.getBody().getNumAddresses();
        row.name = f.getName();
        row.nameSource = nameSource(f);
        row.discoverySource = discoverySource(f, rm, row.nameSource);
        row.discoveryProvenance = discoveryProvenance(row.discoverySource);
        row.thunk = f.isThunk();
        String cc = f.getCallingConventionName();
        row.callingConvention = cc == null ? "" : cc;
        row.callers = f.getCallingFunctions(monitor).size();
        row.callees = f.getCalledFunctions(monitor).size();
        row.indirectReferences = indirectReferenceCount(entry, rm);
        row.rootKind = rootKind(row.entry, row.callingConvention);
        countReferences(f, fm, rm, listing, row);
        row.subsystem = coarseSubsystem(row.entry);
        return row;
    }

    private static boolean inCallbackPointerRange(long address) {
        return (address >= 0x2b3f4L && address <= 0x2b424L && (address - 0x2b3f4L) % 8 == 0)
            || (address >= 0x22c30L && address < 0x22c78L)
            || (address >= 0x280a0L && address <= 0x28134L)
            || (address >= 0x26cccL && address < 0x26da0L)
            || (address >= 0x26da0L && address < 0x26dc4L)
            || (address >= 0x26218L && address < 0x262c0L)
            || address == 0x21e44L || (address >= 0x21e4cL && address <= 0x21e5cL);
    }

    private String discoverySource(Function function, ReferenceManager rm, String nameSource) {
        if (function.getName().startsWith("direct_call_target_")) return "direct-call seed";
        for (Reference reference : rm.getReferencesTo(function.getEntryPoint())) {
            if (reference.getSource() == SourceType.USER_DEFINED
                    && reference.getReferenceType().isData()
                    && inCallbackPointerRange(reference.getFromAddress().getOffset())) {
                return "callback-table seed";
            }
        }
        if ("__interrupt".equals(function.getCallingConventionName())
                && "USER_DEFINED".equals(nameSource)) return "vector seed";
        if ("USER_DEFINED".equals(nameSource)) return "manual/other";
        return "auto-analysis";
    }

    private static String discoveryProvenance(String source) {
        if ("direct-call seed".equals(source)) return "SeedDirectCallTargets.java";
        if ("callback-table seed".equals(source)) return "USER_DEFINED callback pointer reference";
        if ("vector seed".equals(source)) return "vector recovery/annotation script";
        if ("manual/other".equals(source)) return "seed or annotation script";
        return "Ghidra auto-analysis";
    }

    private static int indirectReferenceCount(Address entry, ReferenceManager rm) {
        int count = 0;
        for (Reference reference : rm.getReferencesTo(entry)) {
            if (reference.getReferenceType().isData()
                    || reference.getReferenceType().isComputed()) count++;
        }
        return count;
    }

    private static String nameSource(Function f) {
        Symbol sym = f.getSymbol();
        if (sym == null) return "UNKNOWN";
        SourceType src = sym.getSource();
        return src == null ? "UNKNOWN" : src.name();
    }

    private static String rootKind(long entry, String cc) {
        // Only mark roots that Ghidra/architecture already classify reliably.
        if ("__interrupt".equals(cc)) return "interrupt";
        if (entry == SCHEDULER_ROOT) return "scheduler";
        return "";
    }

    private void countReferences(Function f, FunctionManager fm, ReferenceManager rm,
                                 Listing listing, Row row) {
        Set<Long> ram = new HashSet<>();
        Set<Long> ramReads = new HashSet<>();
        Set<Long> ramWrites = new HashSet<>();
        Set<Long> mmio = new HashSet<>();
        Set<Long> codeflashData = new HashSet<>();
        Set<Long> strings = new HashSet<>();
        AddressSetView body = f.getBody();
        AddressIterator sources = rm.getReferenceSourceIterator(body, true);
        while (sources.hasNext()) {
            Address from = sources.next();
            if (!body.contains(from)) continue;
            for (Reference ref : rm.getReferencesFrom(from)) {
                if (ref == null || ref.isStackReference()) continue;
                Address to = ref.getToAddress();
                if (to == null || to.getAddressSpace().isRegisterSpace()) continue;
                long off = to.getOffset();
                MemoryBlock block = currentProgram.getMemory().getBlock(to);

                if (off >= LOCAL_RAM_START && off < LOCAL_RAM_END) {
                    ram.add(off);
                    if (ref.getReferenceType().isRead()) ramReads.add(off);
                    if (ref.getReferenceType().isWrite()) ramWrites.add(off);
                }
                if (block != null && block.isVolatile()) {
                    mmio.add(off);
                } else if (block != null && block.getName() != null
                        && block.getName().startsWith("SFR_")) {
                    mmio.add(off);
                }

                // Conservative: any DATA ref into CodeFlash that is not a
                // function entry (includes scalars/literals, not only tables).
                if (off < CODEFLASH_END && ref.getReferenceType().isData()) {
                    Function targetFn = fm.getFunctionAt(to);
                    if (targetFn == null) {
                        codeflashData.add(off);
                    }
                    Data data = listing.getDataAt(to);
                    if (data == null) data = listing.getDataContaining(to);
                    if (data != null && data.hasStringValue()) {
                        strings.add(data.getAddress().getOffset());
                    }
                }
            }
        }
        row.ramRefs = ram.size();
        row.ramReadRefs = ramReads.size();
        row.ramWriteRefs = ramWrites.size();
        row.mmioRefs = mmio.size();
        row.codeflashDataRefs = codeflashData.size();
        row.stringRefs = strings.size();
    }

    private static String coarseSubsystem(long entry) {
        // Architecture-documented partition only: boot image vs application base.
        if (entry < APPLICATION_BASE) return "boot";
        if (entry < CODEFLASH_END) return "application";
        return "";
    }

    private static String addrHex(long addr) {
        return String.format("0x%08x", addr);
    }

    private static String csv(String s) {
        if (s == null) return "";
        if (s.contains(",") || s.contains("\"") || s.contains("\n") || s.contains("\r")) {
            return "\"" + s.replace("\"", "\"\"") + "\"";
        }
        return s;
    }
}
