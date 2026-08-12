//@author kaikozlov
//@category Investigation
// Read-only adjudication support for recovered Rx destinations whose generated
// map currently has no non-unpacker direct READ consumer.
//
// Distinguishes immediate local post-processing inside the unpacker from a
// strict store-only direct-reference shape. Also records whether sibling fields
// from the same unpacker do have downstream consumers and scans a bounded
// per-unpacker RAM neighborhood for pointer/PARAM alias candidates.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.symbol.RefType;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;

import java.io.BufferedReader;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Set;
import java.util.TreeSet;

public class ExportApplicationRxConsumerAudit extends GhidraScript {
    private static final long DEFAULT_INIT = 0x57bfeL;
    private static final long RX_BANK_LO = 0xfebe7f94L;
    private static final long RX_BANK_HI = 0xfebe8084L;

    private static final String HEADER = String.join(",",
            "signal_id",
            "can_id",
            "secoc_envelope",
            "unpacker",
            "dest",
            "dest_width",
            "direct_ref_count",
            "unpacker_data_sites",
            "unpacker_read_sites",
            "outside_read_sites",
            "default_write_sites",
            "other_direct_refs",
            "consumed_siblings_same_unpacker",
            "alias_scan_lo",
            "alias_scan_hi",
            "outside_param_alias_sites",
            "outside_unpacker_bank_pointer_sites",
            "disposition");

    private static final class MapRow {
        int signalId;
        String canId;
        String secoc;
        long unpacker;
        long dest;
        int width;
        String firstConsumer;
        String evidenceStatus;
        String destKind;
    }

    private static final class AuditRow {
        MapRow source;
        int directRefCount;
        Set<Long> unpackerData = new TreeSet<>();
        Set<Long> unpackerReads = new TreeSet<>();
        Set<Long> outsideReads = new TreeSet<>();
        Set<Long> defaultWrites = new TreeSet<>();
        Set<String> otherDirect = new TreeSet<>();
        int consumedSiblings;
        long aliasLo;
        long aliasHi;
        Set<String> outsideParamAliases = new TreeSet<>();
        String disposition;
    }

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length != 2) {
            throw new IllegalArgumentException("expected application_rx_map.csv and output.csv");
        }
        Path mapPath = Path.of(args[0]);
        Path outPath = Path.of(args[1]);
        if (!mapPath.isAbsolute() || !Files.isRegularFile(mapPath)) {
            throw new IllegalArgumentException("missing absolute map CSV: " + mapPath);
        }
        if (!outPath.isAbsolute()) {
            throw new IllegalArgumentException("output must be absolute: " + outPath);
        }

        List<MapRow> rows = readMap(mapPath);
        Map<Long, List<MapRow>> byUnpacker = new HashMap<>();
        for (MapRow row : rows) {
            if (!"recovered".equals(row.evidenceStatus) || !"ram".equals(row.destKind)) continue;
            byUnpacker.computeIfAbsent(row.unpacker, ignored -> new ArrayList<>()).add(row);
        }

        Set<String> outsideBankPointers = scanOutsideUnpackerBankPointers();

        List<AuditRow> audits = new ArrayList<>();
        for (MapRow row : rows) {
            if (!"recovered".equals(row.evidenceStatus)
                    || !"ram".equals(row.destKind)
                    || !row.firstConsumer.startsWith("configured-unresolved")) {
                continue;
            }
            audits.add(audit(row, byUnpacker.get(row.unpacker)));
        }
        audits.sort(Comparator.comparingInt(a -> a.source.signalId));

        Files.createDirectories(outPath.getParent());
        try (PrintWriter w = new PrintWriter(Files.newBufferedWriter(outPath, StandardCharsets.UTF_8))) {
            w.println(HEADER);
            for (AuditRow a : audits) {
                MapRow r = a.source;
                w.printf(Locale.ROOT,
                        "%d,%s,%s,0x%X,0x%08X,%d,%d,%s,%s,%s,%s,%s,%d,0x%08X,0x%08X,%s,%s,%s%n",
                        r.signalId, r.canId, r.secoc, r.unpacker, r.dest, r.width,
                        a.directRefCount,
                        sites(a.unpackerData),
                        sites(a.unpackerReads),
                        sites(a.outsideReads),
                        sites(a.defaultWrites),
                        csvEscape(String.join(";", a.otherDirect)),
                        a.consumedSiblings,
                        a.aliasLo,
                        a.aliasHi,
                        csvEscape(String.join(";", a.outsideParamAliases)),
                        csvEscape(String.join(";", outsideBankPointers)),
                        a.disposition);
            }
        }

        long local = audits.stream().filter(a -> a.disposition.equals("local-postprocess")).count();
        long stored = audits.stream().filter(a -> a.disposition.equals("stored-no-direct-consumer")).count();
        long other = audits.size() - local - stored;
        println("ExportApplicationRxConsumerAudit: rows=" + audits.size()
                + " local_postprocess=" + local
                + " stored_no_direct_consumer=" + stored
                + " outside_unpacker_bank_pointers=" + outsideBankPointers.size()
                + " other=" + other
                + " output=" + outPath);
    }

    private Set<String> scanOutsideUnpackerBankPointers() {
        Set<String> out = new TreeSet<>();
        for (long address = RX_BANK_LO; address <= RX_BANK_HI; address++) {
            ReferenceIterator refs = currentProgram.getReferenceManager().getReferencesTo(toAddr(address));
            while (refs.hasNext()) {
                Reference ref = refs.next();
                Function owner = getFunctionContaining(ref.getFromAddress());
                long ownerEntry = owner == null ? -1L : owner.getEntryPoint().getOffset();
                if (ownerEntry >= 0x4a200L && ownerEntry <= 0x4b700L) continue;
                String type = ref.getReferenceType().toString();
                // PARAM is Ghidra's explicit address-as-argument reference. Plain
                // DATA (not READ/WRITE) is the other address-taking representation
                // used by this project. Direct READ/WRITE consumers are audited
                // separately per destination and are not pointer aliases.
                if (!"PARAM".equals(type) && !"DATA".equals(type)) continue;
                out.add(String.format(Locale.ROOT,
                        "target=0x%X;site=0x%X;owner=0x%X;type=%s",
                        address, ref.getFromAddress().getOffset(), ownerEntry, type));
            }
        }
        return out;
    }

    private AuditRow audit(MapRow row, List<MapRow> siblings) {
        AuditRow out = new AuditRow();
        out.source = row;

        // Exact destination-base reference census. The corrected dest_width is
        // retained in the artifact, but receive_signal creates its DATA target
        // at the base and generated consumers likewise load the scalar base.
        ReferenceIterator refs = currentProgram.getReferenceManager().getReferencesTo(toAddr(row.dest));
        while (refs.hasNext()) {
            Reference ref = refs.next();
            out.directRefCount++;
            Function owner = getFunctionContaining(ref.getFromAddress());
            long ownerEntry = owner == null ? -1L : owner.getEntryPoint().getOffset();
            long site = ref.getFromAddress().getOffset();
            RefType type = ref.getReferenceType();
            if (ownerEntry == row.unpacker && type.isRead()) {
                out.unpackerReads.add(site);
            } else if (ownerEntry == row.unpacker && type.isData()) {
                out.unpackerData.add(site);
            } else if (type.isRead()) {
                out.outsideReads.add(site);
            } else if (ownerEntry == DEFAULT_INIT && type.isWrite()) {
                out.defaultWrites.add(site);
            } else {
                out.otherDirect.add(String.format(Locale.ROOT, "0x%X:%s:owner=0x%X",
                        site, type.toString(), ownerEntry));
            }
        }

        int consumed = 0;
        long min = Long.MAX_VALUE;
        long max = Long.MIN_VALUE;
        for (MapRow sibling : siblings) {
            min = Math.min(min, sibling.dest);
            max = Math.max(max, sibling.dest + Math.max(1, sibling.width) - 1L);
            if (!sibling.firstConsumer.startsWith("configured-unresolved")) consumed++;
        }
        out.consumedSiblings = consumed;
        out.aliasLo = Math.max(RX_BANK_LO, min);
        out.aliasHi = Math.min(RX_BANK_HI, max);

        // PARAM refs are the highest-signal representation for a function being
        // handed a pointer into a scalar destination bank. Scan the exact
        // same-unpacker destination range for an outside-function pointer alias.
        for (long address = out.aliasLo; address <= out.aliasHi; address++) {
            ReferenceIterator nearby = currentProgram.getReferenceManager().getReferencesTo(toAddr(address));
            while (nearby.hasNext()) {
                Reference ref = nearby.next();
                if (!"PARAM".equals(ref.getReferenceType().toString())) continue;
                Function owner = getFunctionContaining(ref.getFromAddress());
                long ownerEntry = owner == null ? -1L : owner.getEntryPoint().getOffset();
                if (ownerEntry == row.unpacker) continue;
                out.outsideParamAliases.add(String.format(Locale.ROOT,
                        "target=0x%X;site=0x%X;owner=0x%X",
                        address, ref.getFromAddress().getOffset(), ownerEntry));
            }
        }

        if (!out.outsideReads.isEmpty()) {
            out.disposition = "unexpected-outside-read";
        } else if (!out.unpackerReads.isEmpty()) {
            out.disposition = "local-postprocess";
        } else if (out.directRefCount == 2
                && out.unpackerData.size() == 1
                && out.defaultWrites.size() == 1
                && out.otherDirect.isEmpty()) {
            out.disposition = "stored-no-direct-consumer";
        } else {
            out.disposition = "unresolved-ref-shape";
        }
        return out;
    }

    private List<MapRow> readMap(Path path) throws Exception {
        List<MapRow> out = new ArrayList<>();
        try (BufferedReader br = Files.newBufferedReader(path, StandardCharsets.UTF_8)) {
            String first = br.readLine();
            if (first == null) return out;
            String[] header = parseCsv(first);
            Map<String, Integer> idx = new HashMap<>();
            for (int i = 0; i < header.length; i++) idx.put(header[i], i);
            for (String required : List.of(
                    "signal_id", "can_id", "secoc_envelope", "unpacker", "dest",
                    "dest_width", "first_consumer", "evidence_status", "dest_kind")) {
                if (!idx.containsKey(required)) {
                    throw new IllegalStateException("missing map column: " + required);
                }
            }
            String line;
            while ((line = br.readLine()) != null) {
                if (line.isBlank()) continue;
                String[] fields = parseCsv(line);
                String dest = fields[idx.get("dest")];
                if (!dest.startsWith("0x") && !dest.startsWith("0X")) continue;
                MapRow r = new MapRow();
                r.signalId = Integer.parseInt(fields[idx.get("signal_id")]);
                r.canId = fields[idx.get("can_id")];
                r.secoc = fields[idx.get("secoc_envelope")];
                r.unpacker = Long.decode(fields[idx.get("unpacker")]);
                r.dest = Long.decode(dest);
                r.width = Integer.parseInt(fields[idx.get("dest_width")]);
                r.firstConsumer = fields[idx.get("first_consumer")];
                r.evidenceStatus = fields[idx.get("evidence_status")];
                r.destKind = fields[idx.get("dest_kind")];
                out.add(r);
            }
        }
        return out;
    }

    private static String sites(Set<Long> addresses) {
        List<String> out = new ArrayList<>();
        for (long address : addresses) out.add(String.format(Locale.ROOT, "0x%X", address));
        return String.join(";", out);
    }

    private static String[] parseCsv(String line) {
        List<String> cols = new ArrayList<>();
        StringBuilder cur = new StringBuilder();
        boolean inQuotes = false;
        for (int i = 0; i < line.length(); i++) {
            char ch = line.charAt(i);
            if (ch == '"') {
                if (inQuotes && i + 1 < line.length() && line.charAt(i + 1) == '"') {
                    cur.append('"');
                    i++;
                } else {
                    inQuotes = !inQuotes;
                }
                continue;
            }
            if (ch == ',' && !inQuotes) {
                cols.add(cur.toString());
                cur.setLength(0);
                continue;
            }
            cur.append(ch);
        }
        cols.add(cur.toString());
        return cols.toArray(new String[0]);
    }

    private static String csvEscape(String value) {
        if (value.indexOf(',') < 0 && value.indexOf('"') < 0) return value;
        return "\"" + value.replace("\"", "\"\"") + "\"";
    }
}
