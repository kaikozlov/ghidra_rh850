//@author kaikozlov
//@category Verification
// Instruction-, edge-, table-, and caller-level proof for MEM-SAFE-001..005.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;

import java.util.Arrays;
import java.util.HashSet;
import java.util.Locale;
import java.util.Set;
import java.util.TreeSet;

public class AssertMemorySafetyPaths extends GhidraScript {
    private int failures = 0;
    private int assertions = 0;

    private void fail(String message) {
        failures++;
        printerr("ASSERT-FAIL memory-safety-paths: " + message);
    }

    private void assertInsn(long address, String mnemonic, String... operandFragments) {
        assertions++;
        Instruction insn = currentProgram.getListing().getInstructionAt(toAddr(address));
        if (insn == null) {
            fail(String.format(Locale.ROOT, "missing instruction at 0x%x", address));
            return;
        }
        if (!mnemonic.equalsIgnoreCase(insn.getMnemonicString())) {
            fail(String.format(Locale.ROOT, "0x%x mnemonic expected=%s actual=%s",
                    address, mnemonic, insn.getMnemonicString()));
        }
        StringBuilder operands = new StringBuilder();
        for (int i = 0; i < insn.getNumOperands(); i++) {
            if (i != 0) operands.append(",");
            operands.append(insn.getDefaultOperandRepresentation(i));
        }
        String actual = operands.toString().toLowerCase(Locale.ROOT);
        for (String fragment : operandFragments) {
            if (!actual.contains(fragment.toLowerCase(Locale.ROOT))) {
                fail(String.format(Locale.ROOT, "0x%x operands missing '%s': %s",
                        address, fragment, actual));
            }
        }
    }

    private void assertFlow(long address, long destination) {
        assertions++;
        Instruction insn = currentProgram.getListing().getInstructionAt(toAddr(address));
        if (insn == null) {
            fail(String.format(Locale.ROOT, "missing flow instruction at 0x%x", address));
            return;
        }
        for (Address flow : insn.getFlows()) {
            if (flow.getOffset() == destination) return;
        }
        fail(String.format(Locale.ROOT, "missing flow 0x%x -> 0x%x actual=%s",
                address, destination, Arrays.toString(insn.getFlows())));
    }

    private void assertBytes(long address, String expectedHex) throws Exception {
        assertions++;
        byte[] expected = new byte[expectedHex.length() / 2];
        for (int i = 0; i < expected.length; i++) {
            expected[i] = (byte) Integer.parseInt(expectedHex.substring(i * 2, i * 2 + 2), 16);
        }
        byte[] actual = new byte[expected.length];
        currentProgram.getMemory().getBytes(toAddr(address), actual);
        if (!Arrays.equals(expected, actual)) {
            fail(String.format(Locale.ROOT, "bytes differ at 0x%x expected=%s", address, expectedHex));
        }
    }

    private String refKey(Reference ref) {
        return String.format(Locale.ROOT, "%08x:%s",
                ref.getFromAddress().getOffset(), ref.getReferenceType().toString());
    }

    private void assertExactRefs(long destination, String... expected) {
        assertions++;
        Set<String> actual = new HashSet<>();
        ReferenceIterator refs = currentProgram.getReferenceManager().getReferencesTo(toAddr(destination));
        while (refs.hasNext()) actual.add(refKey(refs.next()));
        Set<String> wanted = Set.of(expected);
        if (!actual.equals(wanted)) {
            fail(String.format(Locale.ROOT, "refs to 0x%x expected=%s actual=%s",
                    destination, wanted, actual));
        }
    }

    private void assertFunctionOwns(long entry, long address) {
        assertions++;
        Function function = getFunctionContaining(toAddr(address));
        if (function == null || function.getEntryPoint().getOffset() != entry) {
            fail(String.format(Locale.ROOT,
                    "0x%x expected function owner 0x%x actual=%s",
                    address, entry,
                    function == null ? "none" : String.format(Locale.ROOT, "0x%x", function.getEntryPoint().getOffset())));
        }
    }

    private void assertExactCallees(long entry, long... expected) throws Exception {
        assertions++;
        Function function = getFunctionAt(toAddr(entry));
        if (function == null) {
            fail(String.format(Locale.ROOT, "missing function 0x%x", entry));
            return;
        }
        Set<Long> actual = new TreeSet<>();
        for (Function called : function.getCalledFunctions(monitor)) {
            actual.add(called.getEntryPoint().getOffset());
        }
        Set<Long> wanted = new TreeSet<>();
        for (long value : expected) wanted.add(value);
        if (!actual.equals(wanted)) {
            fail(String.format(Locale.ROOT, "callees 0x%x expected=%s actual=%s", entry, wanted, actual));
        }
    }

    @Override
    public void run() throws Exception {
        // MEM-SAFE-001: caller count/source/destination state, capped work,
        // floor division, zero-block bypass, completion, and raw staging copy.
        assertInsn(0x6bc2L, "st.h", "r6", "-0x6c24", "gp");
        assertInsn(0x6bc8L, "st.w", "r7", "-0x6c2c", "gp");
        assertInsn(0x6bccL, "st.w", "r8", "-0x6c28", "gp");
        assertInsn(0x6beaL, "ld.hu", "-0x6c24", "gp", "r29");
        assertInsn(0x6beeL, "movea", "0x10", "r0", "r1");
        assertInsn(0x6bf6L, "cmovc", "r1", "r29", "r29");
        assertInsn(0x6bfcL, "sar", "0x4", "r28");
        assertInsn(0x6bfeL, "be", "0x00006c3c");
        assertFlow(0x6bfeL, 0x6c3cL);
        assertInsn(0x6c06L, "jarl", "0x00007108", "lp");
        assertFlow(0x6c06L, 0x7108L);
        assertInsn(0x6c42L, "sub", "r29", "r1");
        assertInsn(0x6c44L, "sst.h", "r1");
        assertInsn(0x6c4aL, "st.b", "r0", "-0x6c22", "gp");
        assertInsn(0x4c2eL, "jarl", "0x000032d2", "lp");
        assertFlow(0x4c2eL, 0x32d2L);
        assertInsn(0x4c72L, "jarl", "0x00006bb4", "lp");
        assertFlow(0x4c72L, 0x6bb4L);
        assertFlow(0x4ddaL, 0x4b7cL);
        assertInsn(0x4f7eL, "ld.w", "-0x6d48", "gp", "r7");
        assertInsn(0x4f82L, "mov", "r29", "r8");
        assertFlow(0x4f84L, 0x153aL);
        assertInsn(0x32d6L, "cmp", "r0", "r7");
        assertFlow(0x32d8L, 0x3316L);
        assertInsn(0x32dcL, "addi", "-0x1", "r7", "r18");
        assertInsn(0x32e0L, "cmp", "r18", "r6");
        assertFlow(0x32e2L, 0x3316L);
        assertBytes(0x8da0L,
                "00000100ff7d01003300000000000000" +
                "00800100fffd0f003300000000000000" +
                "0000bffeff0fbffe3300000001000000");
        assertInsn(0x567eL, "prepare", "r25", "r26", "r27", "r28", "r29", "lp", "0x5");
        assertFunctionOwns(0x567eL, 0x58ccL);
        assertInsn(0x59d2L, "mov", "0x1", "r1");
        assertInsn(0x59d8L, "movea", "-0x6cef", "gp", "ep");
        assertInsn(0x59dcL, "shl", "r19", "r1", "r19");
        assertInsn(0x59e2L, "or", "r19", "r1");
        assertInsn(0x59e4L, "sst.b", "r1");
        assertInsn(0x5e70L, "ld.bu", "-0x6cef", "gp", "r1");
        assertInsn(0x5e74L, "addi", "-0x81", "r1", "r0");
        assertFlow(0x5e78L, 0x5e82L);
        assertInsn(0x58a2L, "ld.bu", "-0x6cef", "gp", "r1");
        assertInsn(0x58a6L, "cmp", "0x1", "r1");
        assertFlow(0x58a8L, 0x58b0L);
        assertInsn(0x58aaL, "addi", "-0x81", "r1", "r0");
        assertFlow(0x58aeL, 0x58d2L);
        assertFlow(0x58b4L, 0x41e0L);
        assertInsn(0x58bcL, "movea", "-0x7f", "r0", "r1");
        assertInsn(0x58c2L, "st.b", "r1", "-0x6cef", "gp");
        assertFlow(0x58ccL, 0x4260L);
        assertBytes(0x58a2L,
                "a40f1193610ac20501067fffaa151d301c38bfff2ce9e051ca0d" +
                "200e81ff0132440f1193020a440f1793bfff94e9");
        assertInsn(0x434cL, "movhi", "-0x141", "r0", "r29");
        assertInsn(0x4350L, "ld.w", "0xfd0", "r29", "r29");
        assertInsn(0x435eL, "jarl", "r29", "lp");

        // MEM-SAFE-002: exact endpoint arithmetic, stride/finality and a bounded
        // callee census showing the step only exposes bytes to the CMAC primitive.
        assertInsn(0x715cL, "st.w", "r28", "-0x6750", "gp");
        assertInsn(0x7160L, "add", "r28", "r29");
        assertInsn(0x7162L, "add", "-0x10", "r29");
        assertInsn(0x7166L, "st.w", "r29", "-0x6758", "gp");
        assertInsn(0x717eL, "addi", "0x10", "r6", "r28");
        assertInsn(0x7182L, "cmp", "r1", "r6");
        assertFlow(0x7184L, 0x7192L);
        assertInsn(0x7198L, "cmp", "r1", "r6");
        assertFlow(0x719aL, 0x71e0L);
        assertFlow(0x71b0L, 0x7e0cL);
        assertInsn(0x71e6L, "st.w", "r28", "-0x6750", "gp");
        assertExactCallees(0x7170L, 0x7e0cL);
        assertBytes(0x8f44L,
                "fffffffff010010a00000000fffffffff110010a00000000" +
                "fffffffff210010a00000000fffffffff310010000000000" +
                "ffffffff00ff010a00000000");

        // MEM-SAFE-003: compare-mode arm, source/target queue, byte compare,
        // equality/mismatch split, and the distinct response code.
        assertInsn(0x5ec2L, "mov", "0x5", "r8");
        assertFlow(0x5ec8L, 0x32d2L);
        assertInsn(0x4d60L, "mov", "r7", "r6");
        assertInsn(0x4d62L, "ld.w", "-0x6d48", "gp", "r7");
        assertFlow(0x4d66L, 0x6c6cL);
        assertInsn(0x6cb4L, "ld.bu", "r19", "r19");
        assertInsn(0x6cbaL, "sld.bu", "r16");
        assertInsn(0x6cbcL, "cmp", "r16", "r19");
        assertFlow(0x6cbeL, 0x6cfaL);
        assertInsn(0x6cd8L, "sub", "r17", "r1");
        assertInsn(0x6ceaL, "st.b", "r0", "-0x6c14", "gp");
        assertInsn(0x6cfaL, "st.b", "r0", "-0x6c13", "gp");
        assertFlow(0x4efeL, 0x4f0aL);
        assertInsn(0x4f00L, "mov", "0x3", "r1");
        assertInsn(0x4f0aL, "movea", "0x10", "r0", "r6");
        assertFlow(0x4f0eL, 0x4b38L);

        // MEM-SAFE-004: failure uses the saved caller length; the only
        // configured submit fixes it at 48 and fixes input at 64.
        assertInsn(0x86e78L, "addi", "-0x40", "r7", "r0");
        assertInsn(0x86e86L, "sld.w", "r1");
        assertInsn(0x86e88L, "addi", "-0x30", "r1", "r0");
        assertFlow(0x86f24L, 0x86f50L);
        assertInsn(0x86f50L, "ld.w", "r27", "r7");
        assertFlow(0x86f54L, 0x89044L);
        assertInsn(0x86f46L, "movea", "0x30", "r0", "r1");
        assertInsn(0x86f4aL, "st.w", "r1", "r27");
        assertInsn(0x6825cL, "movea", "0x30", "r0", "r1");
        assertInsn(0x68262L, "st.w", "r1", "-0x67a8", "gp");
        assertInsn(0x6827aL, "movea", "0x40", "r0", "r8");
        assertFlow(0x6828aL, 0x88936L);
        assertExactRefs(0x86e62L, "000870dc:UNCONDITIONAL_CALL", "00087142:UNCONDITIONAL_CALL");
        assertExactRefs(0x86ee8L, "00086fb4:UNCONDITIONAL_CALL", "000871b2:UNCONDITIONAL_CALL");
        assertExactRefs(0x88936L, "0006828a:UNCONDITIONAL_CALL");

        // MEM-SAFE-005 is a bounded negative, not an unqualified absence:
        // application copy gate, SecOC underflow gate, DLC map, and exact sink caller.
        assertFlow(0x90472L, 0x92398L);
        assertInsn(0x90476L, "ld.hu", "r27", "r1");
        assertInsn(0x9047aL, "cmp", "r10", "r1");
        assertFlow(0x9047cL, 0x9048cL);
        assertFlow(0x90484L, 0x920d2L);
        assertExactRefs(0x920d2L, "00090484:UNCONDITIONAL_CALL");
        assertInsn(0x8e510L, "ld.hu", "r29", "r1");
        assertInsn(0x8e514L, "ld.hu", "sp", "r19");
        assertInsn(0x8e518L, "cmp", "r1", "r19");
        assertFlow(0x8e51aL, 0x8e562L);
        assertInsn(0x8e5e2L, "subr", "r19", "r1");
        assertBytes(0x22f10L, "0001020304050607080c101418203040");

        println("ASSERT memory-safety-paths: assertions=" + assertions + " failures=" + failures);
        if (failures != 0) {
            throw new IllegalStateException("AssertMemorySafetyPaths failures=" + failures);
        }
    }
}
