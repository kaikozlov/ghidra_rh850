//@author kaikozlov
//@category Verification
// Assert application_rx_map.csv recovered rows against Ghidra references:
// - listed unpacker must DATA/WRITE-target each concrete destination (store path)
// - every concrete WRITE ref owner must be the unpacker, receive_signal, or an
//   explicit bounded co-writer (boot BSS clear / app init defaults)
// - listed first_consumer must READ the destination; every other READ owner must
//   be an explicit bounded secondary reader
// Opaque COM shadow destinations are bounded exceptions (no stable per-signal RAM).
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.symbol.RefType;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;

import java.io.BufferedReader;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Set;

public class AssertApplicationReceiveMap extends GhidraScript {
    private int failures = 0;
    private int checkedWrites = 0;
    private int checkedReads = 0;
    private int localPostprocess = 0;
    private int storedNoDirectConsumer = 0;
    private int boundedExceptions = 0;

    private static final Set<Integer> EXPECTED_LOCAL_POSTPROCESS = Set.of(
            231, 233, 235, 237, 270, 273, 276);
    private static final Set<Integer> EXPECTED_STORED_NO_DIRECT_CONSUMER = Set.of(
            62, 70, 107, 115, 144, 173, 177, 194, 197,
            256, 257, 261, 262, 263, 278, 286, 291, 292);

    private static final long RECEIVE_SIGNAL = 0x7c03eL;

    // Boot RAM clear (0x1404) and application default-init (0x57bfe) also WRITE
    // recovered signal destinations; they are not extraction owners.
    private static final Set<Long> BOUNDED_WRITE_COOWNERS = Set.of(0x1404L, 0x57bfeL);

    // Secondary readers observed on recovered destinations beyond first_consumer.
    // These are allowed explicitly; unknown readers fail the audit.
    private static final Set<Long> BOUNDED_READ_COOWNERS = Set.of(
            0x4a1e8L,
            0x4b7baL,
            // CAN-FD 0x0D7 signal 280 persists through FEBE8076 and is
            // consumed by diagnostic/routine gating plus the normal 56FC2
            // application staging path. These readers are exact and bounded.
            0x4ef68L,
            0x4efacL,
            0xfcc4eL,
            0x52f82L,
            0x531c8L,
            0x552baL,
            0x55452L,
            0x56fc2L);

    private void fail(String msg) {
        failures++;
        printerr("ASSERT-FAIL application-rx: " + msg);
    }

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length != 1) {
            throw new IllegalArgumentException("expected absolute path to application_rx_map.csv");
        }
        Path csvPath = Path.of(args[0]);
        if (!csvPath.isAbsolute() || !Files.isRegularFile(csvPath)) {
            throw new IllegalArgumentException("missing CSV: " + csvPath);
        }

        List<String> header;
        List<String[]> rows = new ArrayList<>();
        try (BufferedReader br = Files.newBufferedReader(csvPath, StandardCharsets.UTF_8)) {
            String headerLine = br.readLine();
            if (headerLine == null) {
                fail("empty CSV");
                println("ASSERT application-rx-map: failures=" + failures);
                return;
            }
            header = List.of(parseCsv(headerLine));
            Map<String, Integer> idx = indexOf(header);
            for (String required : List.of(
                    "signal_id", "unpacker", "dest_kind", "dest", "first_consumer", "evidence_status")) {
                if (!idx.containsKey(required)) {
                    fail("missing CSV column: " + required);
                    println("ASSERT application-rx-map: failures=" + failures);
                    return;
                }
            }
            String line;
            while ((line = br.readLine()) != null) {
                if (line.isBlank()) continue;
                rows.add(parseCsv(line));
            }
            auditRows(rows, idx);
        }

        println("ASSERT application-rx-map: write_checks=" + checkedWrites
                + " read_checks=" + checkedReads
                + " local_postprocess=" + localPostprocess
                + " stored_no_direct_consumer=" + storedNoDirectConsumer
                + " bounded_exceptions=" + boundedExceptions
                + " failures=" + failures);
        if (failures != 0) {
            throw new IllegalStateException("AssertApplicationReceiveMap failures=" + failures);
        }
    }

    private void auditRows(List<String[]> rows, Map<String, Integer> idx) {
        int recovered = 0;
        for (String[] row : rows) {
            String status = col(row, idx, "evidence_status");
            if (!"recovered".equals(status)) continue;
            recovered++;
            int signalId = Integer.parseInt(col(row, idx, "signal_id"));
            long unpacker = Long.decode(col(row, idx, "unpacker"));
            String dest = col(row, idx, "dest");
            String destKind = col(row, idx, "dest_kind");
            String consumer = col(row, idx, "first_consumer");

            if ("com_opaque".equals(destKind) || dest.startsWith("COM+")) {
                boundedExceptions++;
                continue;
            }
            if (!dest.startsWith("0x") && !dest.startsWith("0X")) {
                fail("signal " + signalId + " recovered without concrete hex dest: " + dest);
                continue;
            }
            long destAddr = Long.decode(dest);
            Address destA = toAddr(destAddr);

            boolean unpackerTargets = false;
            boolean consumerReads = false;
            int directRefCount = 0;
            Set<Long> writeOwners = new HashSet<>();
            Set<Long> readOwners = new HashSet<>();
            ReferenceIterator rit = currentProgram.getReferenceManager().getReferencesTo(destA);
            while (rit.hasNext()) {
                Reference ref = rit.next();
                directRefCount++;
                RefType rt = ref.getReferenceType();
                Function fn = getFunctionContaining(ref.getFromAddress());
                long ea = fn == null ? -1L : fn.getEntryPoint().getOffset();
                if (rt.isData() && ea == unpacker) {
                    unpackerTargets = true;
                }
                if (rt.isWrite()) {
                    writeOwners.add(ea);
                    if (ea == unpacker) {
                        unpackerTargets = true;
                    }
                }
                if (rt.isRead()) {
                    readOwners.add(ea);
                }
            }

            if (!unpackerTargets) {
                // Indirect store through receive_signal: require DATA target + call edge.
                if (functionCalls(unpacker, RECEIVE_SIGNAL)) {
                    fail(String.format(Locale.ROOT,
                            "signal %d dest 0x%x unpacker 0x%x calls receive_signal but has no DATA/WRITE target ref",
                            signalId, destAddr, unpacker));
                } else {
                    fail(String.format(Locale.ROOT,
                            "signal %d dest 0x%x has no DATA/WRITE from unpacker 0x%x",
                            signalId, destAddr, unpacker));
                }
            } else {
                checkedWrites++;
            }

            for (long ea : writeOwners) {
                if (ea == unpacker || ea == RECEIVE_SIGNAL || BOUNDED_WRITE_COOWNERS.contains(ea)) {
                    continue;
                }
                fail(String.format(Locale.ROOT,
                        "signal %d dest 0x%x unexpected WRITE owner 0x%x (unpacker=0x%x)",
                        signalId, destAddr, ea, unpacker));
            }

            if (consumer.startsWith("configured-unresolved")) {
                if (EXPECTED_LOCAL_POSTPROCESS.contains(signalId)) {
                    if (!readOwners.equals(Set.of(unpacker))) {
                        fail(String.format(Locale.ROOT,
                                "signal %d expected unpacker-local READ only, got owners=%s",
                                signalId, readOwners));
                    }
                    if (!writeOwners.equals(Set.of(0x57bfeL))) {
                        fail(String.format(Locale.ROOT,
                                "signal %d local-postprocess WRITE owners changed: %s",
                                signalId, writeOwners));
                    }
                    if (directRefCount != 3) {
                        fail(String.format(Locale.ROOT,
                                "signal %d local-postprocess direct-ref count expected=3 actual=%d",
                                signalId, directRefCount));
                    }
                    localPostprocess++;
                } else if (EXPECTED_STORED_NO_DIRECT_CONSUMER.contains(signalId)) {
                    if (!readOwners.isEmpty()) {
                        fail(String.format(Locale.ROOT,
                                "signal %d expected no direct READ, got owners=%s",
                                signalId, readOwners));
                    }
                    if (!writeOwners.equals(Set.of(0x57bfeL))) {
                        fail(String.format(Locale.ROOT,
                                "signal %d store-only WRITE owners changed: %s",
                                signalId, writeOwners));
                    }
                    if (directRefCount != 2) {
                        fail(String.format(Locale.ROOT,
                                "signal %d store-only direct-ref count expected=2 actual=%d",
                                signalId, directRefCount));
                    }
                    storedNoDirectConsumer++;
                } else {
                    fail("unexpected configured-unresolved signal " + signalId);
                }
                boundedExceptions++;
                continue;
            }
            if (!consumer.startsWith("0x") && !consumer.startsWith("0X")) {
                fail("signal " + signalId + " concrete consumer not hex: " + consumer);
                continue;
            }
            long consumerAddr = Long.decode(consumer.split("\\s+")[0]);
            for (long ea : readOwners) {
                if (ea == consumerAddr) {
                    consumerReads = true;
                    continue;
                }
                if ((signalId == 280 && ea == unpacker)
                        || BOUNDED_READ_COOWNERS.contains(ea) || ea == -1L) {
                    // Signal 280's generated stack-temporary persistence first
                    // reloads FEBE8076 in its own unpacker to preserve the prior
                    // value when no new update is accepted. -1 is a READ site
                    // outside a recovered function body (explicitly bounded).
                    continue;
                }
                fail(String.format(Locale.ROOT,
                        "signal %d dest 0x%x unexpected READ owner 0x%x (consumer=0x%x)",
                        signalId, destAddr, ea, consumerAddr));
            }
            if (!consumerReads) {
                fail(String.format(Locale.ROOT,
                        "signal %d dest 0x%x has no READ from consumer 0x%x",
                        signalId, destAddr, consumerAddr));
            } else {
                checkedReads++;
            }
        }
        println("ASSERT application-rx-map: recovered=" + recovered);
    }

    private boolean functionCalls(long callerEntry, long calleeEntry) {
        Function fn = getFunctionAt(toAddr(callerEntry));
        if (fn == null) return false;
        Set<Function> called = fn.getCalledFunctions(monitor);
        for (Function c : called) {
            if (c.getEntryPoint().getOffset() == calleeEntry) return true;
        }
        return false;
    }

    private static Map<String, Integer> indexOf(List<String> header) {
        Map<String, Integer> idx = new HashMap<>();
        for (int i = 0; i < header.size(); i++) {
            idx.put(header.get(i), i);
        }
        return idx;
    }

    private static String col(String[] row, Map<String, Integer> idx, String name) {
        Integer i = idx.get(name);
        if (i == null || i >= row.length) {
            throw new IllegalStateException("missing column " + name);
        }
        return row[i];
    }

    private static String[] parseCsv(String line) {
        List<String> cols = new ArrayList<>();
        StringBuilder cur = new StringBuilder();
        boolean inQuotes = false;
        for (int i = 0; i < line.length(); i++) {
            char ch = line.charAt(i);
            if (ch == '"') {
                inQuotes = !inQuotes;
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
}
