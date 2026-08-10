//@author kaikozlov
//@category Investigation
// Read-only whole-image semantic coverage ledger: one deterministic CSV row per
// recovered function. Reports Ghidra-supported name provenance, graph counts,
// and conservative evidence grades. Does not invent OEM semantics. Optional
// columns (root kind, RAM/MMIO/CodeFlash-data/string refs, coarse subsystem)
// are filled only from reliable program facts; otherwise left empty or zero.
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
            "name_source",
            "is_thunk",
            "calling_convention",
            "caller_count",
            "callee_count",
            "root_kind",
            "ram_ref_count",
            "mmio_ref_count",
            "codeflash_data_ref_count",
            "string_ref_count",
            "subsystem",
            "evidence_grade");

    private static final class Row {
        long entry;
        long bodyBytes;
        String name;
        String nameSource;
        boolean thunk;
        String callingConvention;
        int callers;
        int callees;
        String rootKind;
        int ramRefs;
        int mmioRefs;
        int codeflashDataRefs;
        int stringRefs;
        String subsystem;
        String evidenceGrade;
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
                out.printf("%s,%d,%s,%s,%s,%s,%d,%d,%s,%d,%d,%d,%d,%s,%s%n",
                        addrHex(row.entry),
                        row.bodyBytes,
                        csv(row.name),
                        csv(row.nameSource),
                        row.thunk ? "true" : "false",
                        csv(row.callingConvention),
                        row.callers,
                        row.callees,
                        csv(row.rootKind),
                        row.ramRefs,
                        row.mmioRefs,
                        row.codeflashDataRefs,
                        row.stringRefs,
                        csv(row.subsystem),
                        csv(row.evidenceGrade));
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
        row.thunk = f.isThunk();
        String cc = f.getCallingConventionName();
        row.callingConvention = cc == null ? "" : cc;
        row.callers = f.getCallingFunctions(monitor).size();
        row.callees = f.getCalledFunctions(monitor).size();
        row.rootKind = rootKind(row.entry, row.callingConvention);
        countReferences(f, fm, rm, listing, row);
        row.subsystem = coarseSubsystem(row.entry);
        row.evidenceGrade = evidenceGrade(row);
        return row;
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

    private static String evidenceGrade(Row row) {
        // Conservative grades: never claim behavioral closure for the whole image.
        // annotated = USER_DEFINED name from seed/annotate scripts (role label only).
        // thunk = Ghidra thunk, no independent body semantics.
        // recovered = function body recovered; auto/default/analysis name only.
        if (row.thunk) return "thunk";
        if ("USER_DEFINED".equals(row.nameSource)) return "annotated";
        return "recovered";
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
