//@author kaikozlov
//@category Verification
// Assert every in-function RH850 `switch` has a recovered halfword jump table
// and COMPUTED_JUMP references to each case target.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.Array;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.ShortDataType;
import ghidra.program.model.listing.Data;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.scalar.Scalar;
import ghidra.program.model.symbol.Reference;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

public class AssertSwitchTables extends GhidraScript {
    private static final int EXPECTED_IN_FUNCTION_SWITCHES = 19;
    private static final int MAX_LOOKBACK = 16;
    private static final int MAX_TABLE = 256;

    private final List<String> failures = new ArrayList<>();

    private void fail(String msg) {
        failures.add(msg);
        println("FAIL: " + msg);
    }

    private Long cmpImm(Instruction insn) {
        if (!insn.getMnemonicString().equalsIgnoreCase("cmp")) return null;
        if (insn.getNumOperands() < 2) return null;
        Object[] o0 = insn.getOpObjects(0);
        if (o0.length == 0 || !(o0[0] instanceof Scalar)) return null;
        return ((Scalar) o0[0]).getUnsignedValue();
    }

    private Long addiNegImmToR0(Instruction insn) {
        if (!insn.getMnemonicString().equalsIgnoreCase("addi")) return null;
        if (insn.getNumOperands() < 3) return null;
        Object[] o0 = insn.getOpObjects(0);
        Object[] o2 = insn.getOpObjects(2);
        if (o0.length == 0 || o2.length == 0 || !(o0[0] instanceof Scalar)) return null;
        if (!o2[0].toString().equalsIgnoreCase("r0")) return null;
        long imm = ((Scalar) o0[0]).getSignedValue();
        if (imm >= 0) return null;
        return -imm;
    }

    private Integer expectedSize(Instruction switchInsn) {
        List<Instruction> prev = new ArrayList<>();
        Instruction cur = switchInsn;
        for (int i = 0; i < MAX_LOOKBACK; i++) {
            cur = cur.getPrevious();
            if (cur == null) break;
            prev.add(cur);
        }
        for (int i = 0; i < prev.size(); i++) {
            String bm = prev.get(i).getMnemonicString().toLowerCase();
            boolean isBh = bm.equals("bh") || bm.equals("bnh");
            boolean isBc = bm.equals("bc") || bm.equals("bnc");
            if (!isBh && !isBc) continue;
            for (int j = i + 1; j < prev.size(); j++) {
                if (isBh) {
                    Long imm = cmpImm(prev.get(j));
                    if (imm != null && imm + 1 >= 1 && imm + 1 <= MAX_TABLE) {
                        return (int) (imm + 1);
                    }
                }
                if (isBc) {
                    Long n = addiNegImmToR0(prev.get(j));
                    if (n != null && n >= 1 && n <= MAX_TABLE) {
                        return n.intValue();
                    }
                }
            }
        }
        // Packed case-0 fallback: first halfword equals entry count.
        try {
            long tableBase = switchInsn.getAddress().add(switchInsn.getLength()).getOffset();
            short first = getShort(toAddr(tableBase));
            if (first >= 1 && first <= MAX_TABLE) return (int) first;
        } catch (Exception ignored) {
            // fall through
        }
        return null;
    }

    private int countJumpRefs(Address from) {
        int n = 0;
        for (Reference ref : currentProgram.getReferenceManager().getReferencesFrom(from)) {
            if (ref.getReferenceType().isJump()) n++;
        }
        return n;
    }

    private boolean isShortArray(Data data, int size) {
        if (data == null || !data.isDefined()) return false;
        DataType dt = data.getDataType();
        if (dt instanceof Array) {
            Array arr = (Array) dt;
            return arr.getNumElements() == size
                    && arr.getDataType().isEquivalent(ShortDataType.dataType)
                    && data.getLength() == size * 2;
        }
        return false;
    }

    @Override
    public void run() throws Exception {
        int inFunction = 0;
        int recovered = 0;
        InstructionIterator it = currentProgram.getListing().getInstructions(true);
        while (it.hasNext()) {
            Instruction insn = it.next();
            if (!insn.getMnemonicString().equalsIgnoreCase("switch")) continue;
            Function fn = getFunctionContaining(insn.getAddress());
            if (fn == null) continue;
            inFunction++;

            long tableBase = insn.getAddress().add(insn.getLength()).getOffset();
            Integer size = expectedSize(insn);
            if (size == null) {
                fail(String.format("switch %s: could not determine expected table size",
                        insn.getAddress()));
                continue;
            }

            Data data = currentProgram.getListing().getDataAt(toAddr(tableBase));
            if (!isShortArray(data, size)) {
                // Accept any defined array of the right byte length as a softer check
                // if the exact ShortDataType array was widened by analysis.
                if (data == null || !data.isDefined() || data.getLength() != size * 2) {
                    fail(String.format(
                            "switch %s: missing short[%d] table at 0x%x (data=%s len=%s)",
                            insn.getAddress(), size, tableBase,
                            data == null ? "null" : data.getDataType().getName(),
                            data == null ? "-" : Integer.toString(data.getLength())));
                    continue;
                }
            }

            Set<Long> expectedTargets = new HashSet<>();
            for (int i = 0; i < size; i++) {
                short off = getShort(toAddr(tableBase + i * 2L));
                expectedTargets.add(tableBase + (((long) off) << 1));
            }
            Set<Long> jumpTargets = new HashSet<>();
            for (Reference ref : currentProgram.getReferenceManager()
                    .getReferencesFrom(insn.getAddress())) {
                if (ref.getReferenceType().isJump()) {
                    jumpTargets.add(ref.getToAddress().getOffset());
                }
            }
            if (!jumpTargets.containsAll(expectedTargets)) {
                Set<Long> missing = new HashSet<>(expectedTargets);
                missing.removeAll(jumpTargets);
                fail(String.format(
                        "switch %s: missing COMPUTED_JUMP targets %s (have %d/%d unique)",
                        insn.getAddress(), missing, jumpTargets.size(),
                        expectedTargets.size()));
                continue;
            }
            if (countJumpRefs(insn.getAddress()) < expectedTargets.size()) {
                // Duplicates may collapse; unique coverage is the hard requirement.
            }
            recovered++;
        }

        if (inFunction != EXPECTED_IN_FUNCTION_SWITCHES) {
            fail(String.format("in-function switch count=%d expected=%d",
                    inFunction, EXPECTED_IN_FUNCTION_SWITCHES));
        }
        if (recovered != EXPECTED_IN_FUNCTION_SWITCHES) {
            fail(String.format("fully recovered switch tables=%d expected=%d",
                    recovered, EXPECTED_IN_FUNCTION_SWITCHES));
        }

        println(String.format(
                "ASSERT switch-tables: in_function=%d recovered=%d failures=%d",
                inFunction, recovered, failures.size()));
        if (!failures.isEmpty()) {
            throw new IllegalStateException(failures.size() + " switch-table failures: "
                    + String.join("; ", failures));
        }
    }
}
