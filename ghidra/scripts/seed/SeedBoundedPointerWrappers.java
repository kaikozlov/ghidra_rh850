//@author kaikozlov
//@category Analysis
// Seed six exact, table-addressed ABI wrappers.  These are bounded as wrapper
// entries only; the pointer table has no proven in-image dispatcher.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.symbol.RefType;
import ghidra.program.model.symbol.SourceType;

import java.security.MessageDigest;

public class SeedBoundedPointerWrappers extends GhidraScript {
    private static final long[] POINTERS = {
        0x21e4cL, 0x21e50L, 0x21e54L, 0x21e58L, 0x21e5cL, 0x21e44L,
    };
    private static final long[] TARGETS = {
        0x7adc8L, 0x7addcL, 0x7adeeL, 0x7ae00L, 0x7ae14L, 0x7ae28L,
    };
    private static final int[] SIZES = {20, 18, 18, 20, 20, 18};
    private static final String[] HASHES = {
        "4affbb3562dd4d74bd263eab107141dd13e71757759be264e073d915f432254f",
        "14deca0a15674fae97125dc05479a94388ab3dcbb64f4b9a7b746b91bef3f434",
        "9cccf459ab62165fc79fafb44384ff9d1e3cffe17b159590dd2520214d52ee39",
        "a15579ca5b9b7c424f52b6d78d2fc05b39122cdc7e2ae2f9c6f927127fdbae53",
        "9f7de03190b9b650fcabeb6d2a69737c0780b94226b6ceed2ca3f7865a50c3eb",
        "b6817167bf8c18fdfd492563ef63a247fd0c0ab551727553a30d36a0ddd31898",
    };

    @Override
    public void run() throws Exception {
        int created = 0;
        for (int index = 0; index < TARGETS.length; index++) {
            Address pointer = toAddr(POINTERS[index]);
            Address target = toAddr(TARGETS[index]);
            long raw = currentProgram.getMemory().getInt(pointer) & 0xffffffffL;
            if (raw != TARGETS[index]) {
                throw new IllegalStateException(String.format(
                    "pointer 0x%x contains 0x%x expected 0x%x",
                    POINTERS[index], raw, TARGETS[index]));
            }
            requireHash(index);
            Function containing = getFunctionContaining(target);
            if (containing != null && !containing.getEntryPoint().equals(target)) {
                throw new IllegalStateException(target + " is an alternate entry into " +
                    containing.getEntryPoint());
            }
            Function function = getFunctionAt(target);
            if (function == null) {
                if (getInstructionAt(target) == null && !disassemble(target)) {
                    throw new IllegalStateException("failed to disassemble " + target);
                }
                Instruction first = getInstructionAt(target);
                if (first == null || !"prepare".equals(first.getMnemonicString())) {
                    throw new IllegalStateException("missing wrapper prologue at " + target);
                }
                function = createFunction(target,
                    String.format("bounded_api_wrapper_%02d", index));
                if (function == null) throw new IllegalStateException("create failed at " + target);
                created++;
            }
            if (function.getBody().getNumAddresses() != SIZES[index]) {
                throw new IllegalStateException(String.format(
                    "wrapper 0x%x size=%d expected=%d", TARGETS[index],
                    function.getBody().getNumAddresses(), SIZES[index]));
            }
            if (!"__stdcall".equals(function.getCallingConventionName())) {
                function.setCallingConvention("__stdcall");
            }
            for (var reference : currentProgram.getReferenceManager().getReferencesFrom(pointer)) {
                if (reference.getToAddress().equals(target) && reference.getReferenceType().isData()) {
                    currentProgram.getReferenceManager().delete(reference);
                }
            }
            currentProgram.getReferenceManager().addMemoryReference(
                pointer, target, RefType.DATA, SourceType.USER_DEFINED, 0);
        }
        println("SeedBoundedPointerWrappers: entries=" + TARGETS.length + " created=" + created);
    }

    private void requireHash(int index) throws Exception {
        byte[] bytes = new byte[SIZES[index]];
        currentProgram.getMemory().getBytes(toAddr(TARGETS[index]), bytes);
        StringBuilder actual = new StringBuilder();
        for (byte value : MessageDigest.getInstance("SHA-256").digest(bytes)) {
            actual.append(String.format("%02x", value & 0xff));
        }
        if (!HASHES[index].equals(actual.toString())) {
            throw new IllegalStateException(String.format("wrapper 0x%x hash mismatch", TARGETS[index]));
        }
    }
}
