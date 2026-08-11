//@author kaikozlov
//@category Verification
// Read-only evidence boundary for pointer-shaped clusters intentionally left
// unresolved. This proves exact bytes/reference absence; it does not infer
// callback semantics from plausible decoding.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.symbol.Reference;

import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.List;

public class AssertReviewedPointerClusters extends GhidraScript {
    private static final long START = 0x27c88L;
    private static final long END = 0x27d78L;
    private static final long DESCRIPTOR = 0x27d84L;
    private static final String SHA256 =
        "53d8c3f4dd2de0354cadac93118c67ef2485d4b3a22d1c5d9cae82de918d9a78";

    @Override
    public void run() throws Exception {
        List<String> failures = new ArrayList<>();
        byte[] bytes = new byte[(int)(END - START)];
        currentProgram.getMemory().getBytes(toAddr(START), bytes);
        if (!SHA256.equals(hash(bytes))) failures.add("cluster byte hash changed");

        int targets = 0;
        int pointerReferences = 0;
        for (long pointerOffset = START; pointerOffset < END; pointerOffset += 4) {
            Address pointer = toAddr(pointerOffset);
            long targetOffset = currentProgram.getMemory().getInt(pointer) & 0xffffffffL;
            if ((targetOffset & 1L) != 0 || targetOffset > 0xfffffL) {
                failures.add(String.format("invalid pointer 0x%x -> 0x%x", pointerOffset, targetOffset));
                continue;
            }
            targets++;
            Address target = toAddr(targetOffset);
            Function exact = getFunctionAt(target);
            Function containing = getFunctionContaining(target);
            if (exact != null || containing != null) {
                failures.add(String.format(
                    "unresolved target became function-owned 0x%x%s",
                    targetOffset,
                    containing == null ? "" : String.format(" (entry 0x%x)", containing.getEntryPoint().getOffset())));
            }
            if (getInstructionAt(target) == null) {
                failures.add(String.format("target is not decoded at 0x%x", targetOffset));
            }
            for (Reference reference : getReferencesTo(target)) {
                long source = reference.getFromAddress().getOffset();
                if (source < START || source >= END || !reference.getReferenceType().isData()) {
                    failures.add(String.format(
                        "target 0x%x has non-cluster/non-data reference %s from 0x%x",
                        targetOffset, reference.getReferenceType(), source));
                } else {
                    pointerReferences++;
                }
            }
        }

        int tableReferences = 0;
        for (long offset = START; offset < END; offset++) {
            for (Reference reference : getReferencesTo(toAddr(offset))) {
                long source = reference.getFromAddress().getOffset();
                boolean allowed = offset == START && source == DESCRIPTOR
                    && reference.getReferenceType().isData()
                    && getFunctionContaining(reference.getFromAddress()) == null;
                if (!allowed) {
                    failures.add(String.format(
                        "cluster address 0x%x referenced by %s from 0x%x",
                        offset, reference.getReferenceType(), source));
                } else {
                    tableReferences++;
                }
            }
        }
        long descriptorValue = currentProgram.getMemory().getInt(toAddr(DESCRIPTOR)) & 0xffffffffL;
        if (descriptorValue != START) failures.add("descriptor no longer points to cluster base");
        if (getFunctionContaining(toAddr(DESCRIPTOR)) != null) {
            failures.add("cluster descriptor became executable/function-owned");
        }
        if (targets != 60) failures.add("expected 60 targets, got " + targets);
        if (pointerReferences != 60) failures.add("expected 60 pointer-to-target data references, got " + pointerReferences);
        if (tableReferences != 1) failures.add("expected one data reference to cluster, got " + tableReferences);
        if (!failures.isEmpty()) {
            for (String failure : failures) printerr("FAIL: " + failure);
            throw new IllegalStateException("reviewed pointer cluster assertion failed");
        }
        println(String.format(
            "ASSERT reviewed-pointer-clusters: targets=%d target_data_refs=%d table_refs=%d no_function_consumers=passed",
            targets, pointerReferences, tableReferences));
    }

    private static String hash(byte[] bytes) throws Exception {
        StringBuilder result = new StringBuilder();
        for (byte value : MessageDigest.getInstance("SHA-256").digest(bytes)) {
            result.append(String.format("%02x", value & 0xff));
        }
        return result.toString();
    }
}
