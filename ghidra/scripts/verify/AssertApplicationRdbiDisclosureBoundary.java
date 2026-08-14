//@author kaikozlov
//@category Verification
// Read-only bounded audit of unauthenticated application RDBI callbacks.
// The conservative direct-call closure is intentionally path-insensitive; three
// apparent NvM-workspace hits are then discharged with exact literal-callsite
// and dispatcher evidence because 0x2xx checkpoint IDs cannot enter the 0x000
// family that owns FEBF0308. The branch-resolved boundary therefore retains
// only the known non-secret DID-0110 status accumulator.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.Reference;
import java.util.*;

public class AssertApplicationRdbiDisclosureBoundary extends GhidraScript {
    private static final long TABLE = 0x2941cL;
    private static final int COUNT = 242, STRIDE = 16, MAX_DEPTH = 4;

    private static final class Node {
        final Function function; final int depth;
        Node(Function function, int depth) { this.function = function; this.depth = depth; }
    }

    private static boolean auditRange(long address) {
        // Crypto-test / key-update application RAM.
        if (address >= 0xfebe5000L && address <= 0xfebe5269L) return true;
        // NvM scratch/key-like workspace used by diagnostic persistence paths.
        if (address >= 0xfebf0200L && address <= 0xfebf03ffL) return true;
        // Payload-derived key material.
        if (address >= 0xfebf2d08L && address <= 0xfebf2d17L) return true;
        // Application SecurityAccess seed/data/temp neighborhood.
        if (address >= 0xfebf4958L && address <= 0xfebf49ffL) return true;
        // Application crypto temporary workspace and nearby SA state.
        if (address >= 0xfebf4a40L && address <= 0xfebf4b33L) return true;
        return false;
    }

    private static String hitKey(int did, Address from, Reference reference) {
        return String.format("%04X:%s:%s:%s", did, from,
            reference.getReferenceType(), reference.getToAddress());
    }

    @Override
    public void run() throws Exception {
        Set<String> expectedConservative = new TreeSet<>(Arrays.asList(
            "0105:000668e0:DATA:febf0308",
            "010B:000668e0:DATA:febf0308",
            "0110:0006909a:READ:febe5050",
            "F18C:000668e0:DATA:febf0308"
        ));
        Set<String> infeasibleCheckpointHits = new TreeSet<>(Arrays.asList(
            "0105:000668e0:DATA:febf0308",
            "010B:000668e0:DATA:febf0308",
            "F18C:000668e0:DATA:febf0308"
        ));
        Set<String> expectedResolved = new TreeSet<>(Arrays.asList(
            "0110:0006909a:READ:febe5050"
        ));
        Set<String> actual = new TreeSet<>();
        Set<String> fixedGlobalWrites = new TreeSet<>();
        Set<String> rootFixedGlobalWrites = new TreeSet<>();
        Set<Long> uniqueCallbacks = new HashSet<>();

        for (int index = 0; index < COUNT; index++) {
            long row = TABLE + (long) index * STRIDE;
            int did = currentProgram.getMemory().getShort(toAddr(row)) & 0xffff;
            long callback = currentProgram.getMemory().getInt(toAddr(row + 4)) & 0xffffffffL;
            if (callback == 0) continue;
            uniqueCallbacks.add(callback);
            Function root = getFunctionAt(toAddr(callback));
            if (root == null) throw new IllegalStateException(String.format(
                "RDBI DID %04X missing callback function %06X", did, callback));

            ArrayDeque<Node> queue = new ArrayDeque<>();
            Set<Address> seen = new HashSet<>();
            queue.add(new Node(root, 0));
            seen.add(root.getEntryPoint());
            while (!queue.isEmpty()) {
                monitor.checkCancelled();
                Node node = queue.remove();
                InstructionIterator instructions = currentProgram.getListing().getInstructions(
                    node.function.getBody(), true);
                while (instructions.hasNext()) {
                    Instruction instruction = instructions.next();
                    for (Reference reference : instruction.getReferencesFrom()) {
                        Address target = reference.getToAddress();
                        if (target == null || !target.isMemoryAddress()) continue;
                        long address = target.getOffset();
                        if (!reference.getReferenceType().isCall() && auditRange(address)) {
                            actual.add(hitKey(did, instruction.getAddress(), reference));
                        }
                        if (reference.getReferenceType().isWrite()
                                && address >= 0xfebe0000L && address <= 0xfebfffffL) {
                            String write = hitKey(did, instruction.getAddress(), reference);
                            fixedGlobalWrites.add(write);
                            if (node.depth == 0) rootFixedGlobalWrites.add(write);
                        }
                        if (node.depth < MAX_DEPTH && reference.getReferenceType().isCall()) {
                            Function callee = getFunctionAt(target);
                            if (callee != null && seen.add(callee.getEntryPoint())) {
                                queue.add(new Node(callee, node.depth + 1));
                            }
                        }
                    }
                }
            }
        }

        if (uniqueCallbacks.size() != 196) {
            throw new IllegalStateException("RDBI unique callback count changed: " + uniqueCallbacks.size());
        }
        if (!actual.equals(expectedConservative)) {
            Set<String> missing = new TreeSet<>(expectedConservative); missing.removeAll(actual);
            Set<String> extra = new TreeSet<>(actual); extra.removeAll(expectedConservative);
            throw new IllegalStateException("RDBI conservative disclosure boundary changed; missing="
                + missing + " extra=" + extra);
        }

        // Resolve the three path-insensitive FEBF0308 observations. Each RDBI
        // callback loads a literal 0x2xx checkpoint ID immediately before its
        // call to 0x65D66. The dispatcher masks 0xFF00 and routes the 0x200
        // family to 0x66172; FEBF0308 is referenced only through the mutually
        // exclusive 0x000-family callee 0x668B2. Exact bytes pin both the
        // caller constants and the relevant dispatcher decision.
        requireBytes(0x4cce4L, "20360402"); // movea 0x204,r0,r6
        requireBytes(0x4cce8L, "81ff7e90"); // jarl 0x65D66
        requireBytes(0x4cd94L, "20360a02"); // movea 0x20A,r0,r6
        requireBytes(0x4cd98L, "81ffce8f"); // jarl 0x65D66
        requireBytes(0x4e93cL, "20360702"); // movea 0x207,r0,r6
        requireBytes(0x4e940L, "81ff2674"); // jarl 0x65D66
        requireBytes(0x65d6aL, "c60e00ff"); // andi 0xFF00,r6,r1
        requireBytes(0x65d84L, "010600fe"); // compare normalized family with 0x200
        requireBytes(0x65d88L, "ca05");     // branch away when not 0x200
        requireBytes(0x65d8aL, "80ffe803"); // jarl 0x66172

        Set<String> resolved = new TreeSet<>(actual);
        resolved.removeAll(infeasibleCheckpointHits);
        if (!resolved.equals(expectedResolved)) {
            throw new IllegalStateException("RDBI branch-resolved disclosure boundary changed: "
                + resolved);
        }
        Set<String> branch200Hits = collectSensitiveHits(getFunctionAt(toAddr(0x66172L)), 3, 0xffff);
        if (!branch200Hits.isEmpty()) {
            throw new IllegalStateException("RDBI 0x200 checkpoint branch gained sensitive refs: "
                + branch200Hits);
        }

        // A ReadDataByIdentifier callback should not mutate fixed application
        // state. Across the same four-hop closure there are no fixed-global
        // writes at any RDBI root. The only transitive fixed RAM writes are the
        // balanced interrupt-mask nesting counter updates reached by F186's Dcm
        // session getter. Pin both the exact write census and lock/read/unlock
        // instruction order so ordinary RDBI cannot silently acquire a new
        // control/persistence side effect.
        Set<String> expectedWrites = new TreeSet<>(Arrays.asList(
            "F186:000693f8:WRITE:febe39dc",
            "F186:00069420:WRITE:febe39dc",
            "F186:0006945c:WRITE:febe39dc",
            "F186:00069486:WRITE:febe39dc"
        ));
        if (!rootFixedGlobalWrites.isEmpty()) {
            throw new IllegalStateException("RDBI root gained fixed-global writes: "
                + rootFixedGlobalWrites);
        }
        if (!fixedGlobalWrites.equals(expectedWrites)) {
            throw new IllegalStateException("RDBI fixed-global write boundary changed: expected="
                + expectedWrites + " actual=" + fixedGlobalWrites);
        }
        requireBytes(0x4e90eL, "84ffd014"); // F186 -> Dcm session getter 0x8FDDE
        requireBytes(0x907ecL, "80ffd867"); // critical-section enter 0x96FC4
        requireBytes(0x907f0L, "840f35a1"); // read current session FEBE5934
        requireBytes(0x907f8L, "80ffd867"); // critical-section exit 0x96FD0

        // The sole branch-resolved crypto-neighborhood hit is a status
        // accumulator, not the generated command-5 output. Pin its complete
        // xref topology.
        assertExactRefs(0xfebe5050L,
            "00068190:WRITE", "00068d52:READ", "00068da4:WRITE",
            "0006909a:READ", "000690e4:WRITE");

        println(String.format(
            "ASSERT application-rdbi-disclosure-boundary: dids=%d unique_callbacks=%d max_depth=%d conservative_hits=%d branch_resolved_hits=%d checkpoint_0x200_hits=0 root_fixed_global_writes=0 fixed_global_writes=%d unexpected=0",
            COUNT, uniqueCallbacks.size(), MAX_DEPTH, actual.size(), resolved.size(), fixedGlobalWrites.size()));
    }

    private Set<String> collectSensitiveHits(Function root, int maxDepth, int did) throws Exception {
        if (root == null) throw new IllegalStateException("missing sensitive-closure root");
        Set<String> hits = new TreeSet<>();
        ArrayDeque<Node> queue = new ArrayDeque<>();
        Set<Address> seen = new HashSet<>();
        queue.add(new Node(root, 0));
        seen.add(root.getEntryPoint());
        while (!queue.isEmpty()) {
            monitor.checkCancelled();
            Node node = queue.remove();
            InstructionIterator instructions = currentProgram.getListing().getInstructions(
                node.function.getBody(), true);
            while (instructions.hasNext()) {
                Instruction instruction = instructions.next();
                for (Reference reference : instruction.getReferencesFrom()) {
                    Address target = reference.getToAddress();
                    if (target == null || !target.isMemoryAddress()) continue;
                    if (!reference.getReferenceType().isCall() && auditRange(target.getOffset())) {
                        hits.add(hitKey(did, instruction.getAddress(), reference));
                    }
                    if (node.depth < maxDepth && reference.getReferenceType().isCall()) {
                        Function callee = getFunctionAt(target);
                        if (callee != null && seen.add(callee.getEntryPoint())) {
                            queue.add(new Node(callee, node.depth + 1));
                        }
                    }
                }
            }
        }
        return hits;
    }

    private void requireBytes(long offset, String expectedHex) throws Exception {
        byte[] expected = hexBytes(expectedHex);
        byte[] actual = new byte[expected.length];
        currentProgram.getMemory().getBytes(toAddr(offset), actual);
        if (!Arrays.equals(actual, expected)) {
            throw new IllegalStateException(String.format(
                "bytes changed at %s: expected=%s actual=%s",
                toAddr(offset), expectedHex, toHex(actual)));
        }
    }

    private byte[] hexBytes(String hex) {
        byte[] out = new byte[hex.length() / 2];
        for (int i = 0; i < out.length; i++) {
            out[i] = (byte) Integer.parseInt(hex.substring(i * 2, i * 2 + 2), 16);
        }
        return out;
    }

    private String toHex(byte[] bytes) {
        StringBuilder out = new StringBuilder();
        for (byte value : bytes) out.append(String.format("%02x", value & 0xff));
        return out.toString();
    }

    private void assertExactRefs(long targetOffset, String... expectedRefs) {
        Set<String> expected = new TreeSet<>(Arrays.asList(expectedRefs));
        Set<String> actual = new TreeSet<>();
        for (Reference reference : getReferencesTo(toAddr(targetOffset))) {
            actual.add(reference.getFromAddress() + ":" + reference.getReferenceType());
        }
        if (!actual.equals(expected)) {
            throw new IllegalStateException(String.format(
                "xref census for %s changed; expected=%s actual=%s",
                toAddr(targetOffset), expected, actual));
        }
    }
}
