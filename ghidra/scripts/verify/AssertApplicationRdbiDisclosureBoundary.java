//@author kaikozlov
//@category Verification
// Read-only bounded audit of unauthenticated application RDBI callbacks.
// Follows direct calls to depth 4 and requires the only references into the
// selected security-sensitive RAM neighborhoods to remain the four known,
// non-secret status/workspace observations below.
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
        Set<String> expected = new TreeSet<>(Arrays.asList(
            "0105:000668e0:DATA:febf0308",
            "010B:000668e0:DATA:febf0308",
            "0110:0006909a:READ:febe5050",
            "F18C:000668e0:DATA:febf0308"
        ));
        Set<String> actual = new TreeSet<>();
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
        if (!actual.equals(expected)) {
            Set<String> missing = new TreeSet<>(expected); missing.removeAll(actual);
            Set<String> extra = new TreeSet<>(actual); extra.removeAll(expected);
            throw new IllegalStateException("RDBI disclosure boundary changed; missing="
                + missing + " extra=" + extra);
        }

        // The one crypto-neighborhood hit is a status accumulator, not the
        // generated command-5 output. Pin its complete xref topology.
        assertExactRefs(0xfebe5050L,
            "00068190:WRITE", "00068d52:READ", "00068da4:WRITE",
            "0006909a:READ", "000690e4:WRITE");

        println(String.format(
            "ASSERT application-rdbi-disclosure-boundary: dids=%d unique_callbacks=%d max_depth=%d sensitive_hits=%d unexpected=0",
            COUNT, uniqueCallbacks.size(), MAX_DEPTH, actual.size()));
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
