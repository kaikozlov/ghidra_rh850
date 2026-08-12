//@author kaikozlov
//@category Investigation
// Read-only export of references to application COM Tx staging RAM.
//
// The source set is discovered from the six normal Tx packer bodies themselves.
// For every referenced staging cell, emit every Ghidra reference plus owning
// function identity/body hash. No OEM semantics are inferred here.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.AddressRange;
import ghidra.program.model.address.AddressRangeIterator;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;
import ghidra.program.model.symbol.ReferenceManager;

import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Locale;
import java.util.Set;
import java.util.TreeSet;

public class ExportApplicationTxProducerRefs extends GhidraScript {
    private static final long RAM_LO = 0xfebe8094L;
    private static final long RAM_HI = 0xfebe8110L;
    private static final long[] PACKERS = {
            0x4bceeL, 0x4be24L, 0x4c25cL, 0x4c158L, 0x4bb1eL, 0x4bc54L,
    };

    private static final String HEADER = String.join(",",
            "source_ram",
            "ref_from",
            "ref_type",
            "owner_entry",
            "owner_name",
            "owner_body_size",
            "owner_body_sha256");

    private static final class Row {
        long source;
        long from;
        String refType;
        long ownerEntry;
        String ownerName;
        long ownerSize;
        String ownerSha;
    }

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length != 1) {
            throw new IllegalArgumentException("expected absolute CSV output path");
        }
        Path out = Path.of(args[0]);
        if (!out.isAbsolute()) {
            throw new IllegalArgumentException("output path must be absolute: " + out);
        }

        ReferenceManager rm = currentProgram.getReferenceManager();
        Set<Long> sources = new TreeSet<>();
        for (long packerEntry : PACKERS) {
            Function packer = getFunctionAt(toAddr(packerEntry));
            if (packer == null) {
                throw new IllegalStateException(String.format("missing Tx packer at 0x%x", packerEntry));
            }
            InstructionIterator instructions = currentProgram.getListing().getInstructions(packer.getBody(), true);
            while (instructions.hasNext()) {
                Instruction insn = instructions.next();
                for (Reference ref : rm.getReferencesFrom(insn.getAddress())) {
                    long target = ref.getToAddress().getOffset();
                    if (target >= RAM_LO && target <= RAM_HI) {
                        sources.add(target);
                    }
                }
            }
        }
        if (sources.isEmpty()) {
            throw new IllegalStateException("no Tx staging RAM discovered from packer bodies");
        }

        List<Row> rows = new ArrayList<>();
        for (long source : sources) {
            ReferenceIterator refs = rm.getReferencesTo(toAddr(source));
            int count = 0;
            while (refs.hasNext()) {
                Reference ref = refs.next();
                Row row = new Row();
                row.source = source;
                row.from = ref.getFromAddress().getOffset();
                row.refType = ref.getReferenceType().getName();
                Function owner = getFunctionContaining(ref.getFromAddress());
                if (owner == null) {
                    row.ownerEntry = 0;
                    row.ownerName = "<none>";
                    row.ownerSize = 0;
                    row.ownerSha = "";
                } else {
                    row.ownerEntry = owner.getEntryPoint().getOffset();
                    row.ownerName = owner.getName();
                    row.ownerSize = owner.getBody().getNumAddresses();
                    row.ownerSha = sha256(owner);
                }
                rows.add(row);
                count++;
            }
            if (count == 0) {
                throw new IllegalStateException(String.format("Tx source 0x%x has no references", source));
            }
        }

        rows.sort(Comparator
                .comparingLong((Row r) -> r.source)
                .thenComparingLong(r -> r.from)
                .thenComparing(r -> r.refType));

        Files.createDirectories(out.getParent());
        try (PrintWriter w = new PrintWriter(Files.newBufferedWriter(out, StandardCharsets.UTF_8))) {
            w.println(HEADER);
            for (Row row : rows) {
                w.printf(Locale.ROOT,
                        "0x%08X,0x%08X,%s,0x%08X,%s,%d,%s%n",
                        row.source,
                        row.from,
                        row.refType,
                        row.ownerEntry,
                        csvEscape(row.ownerName),
                        row.ownerSize,
                        row.ownerSha);
            }
        }
        println("ExportApplicationTxProducerRefs: sources=" + sources.size()
                + " refs=" + rows.size() + " output=" + out);
    }

    private String sha256(Function function) throws Exception {
        MessageDigest md = MessageDigest.getInstance("SHA-256");
        byte[] bytes = new byte[(int) function.getBody().getNumAddresses()];
        int cursor = 0;
        AddressRangeIterator ranges = function.getBody().getAddressRanges();
        while (ranges.hasNext()) {
            AddressRange range = ranges.next();
            int size = (int) range.getLength();
            byte[] chunk = new byte[size];
            currentProgram.getMemory().getBytes(range.getMinAddress(), chunk);
            System.arraycopy(chunk, 0, bytes, cursor, size);
            cursor += size;
        }
        byte[] digest = md.digest(bytes);
        StringBuilder out = new StringBuilder(digest.length * 2);
        for (byte value : digest) out.append(String.format("%02x", value));
        return out.toString();
    }

    private static String csvEscape(String value) {
        if (value.indexOf(',') < 0 && value.indexOf('"') < 0) return value;
        return "\"" + value.replace("\"", "\"\"") + "\"";
    }
}
