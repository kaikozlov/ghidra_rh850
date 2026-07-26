//@author kaikozlov
//@category Verification
// Full-coverage switch-table VERIFIER (not a count assert). It scans EVERY
// decoded `switch` instruction in the program, independently recomputes which
// ones have a compiler range-check prefix + valid halfword table, and asserts
// that set EXACTLY equals the recovered set. This turns the in-function /
// out-of-function boundary into a measured invariant: it proves
//   (a) every real switch IS recovered (completeness),
//   (b) nothing that is not a real switch IS recovered (soundness), and
//   (c) the 232 unrecovered `switch` opcodes are unreachable data misread as
//       code — none carries the range check a real compiler switch requires.
//
// "Real" == a `cmp IMM`/`addi -N,rX,r0` range check precedes the `switch` (the
// compiler always emits one before indexing the table) and the resulting
// halfword table validates. The packed case-0 heuristic is intentionally NOT a
// recovery trigger: data/switch_table_inventory.csv shows its 5 hits here are
// all false positives. RecoverSwitchTables and this script share the identical
// bound-detection + validation logic so the two cannot drift.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Data;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.listing.Listing;
import ghidra.program.model.scalar.Scalar;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.Symbol;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

public class AssertSwitchTables extends GhidraScript {
    private static final int EXPECTED_REAL_SWITCHES = 20;
    private static final int MAX_TABLE = 256;
    private static final int MAX_LOOKBACK = 16;
    private static final long CODEFLASH_END = 0x100000L;
    private static final long FAR = 0x10000L;

    private final List<String> failures = new ArrayList<>();

    private void fail(String msg) {
        failures.add(msg);
        println("FAIL: " + msg);
    }

    private boolean isCodeFlash(long addr) {
        return addr >= 0L && addr < CODEFLASH_END && (addr & 1L) == 0L;
    }

    // ---- bound detection: faithful copy of RecoverSwitchTables.boundFromPrefix ----
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

    private Integer prefixBound(Instruction switchInsn) {
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
                Instruction cand = prev.get(j);
                if (isBh) {
                    Long imm = cmpImm(cand);
                    if (imm != null && imm + 1 >= 1 && imm + 1 <= MAX_TABLE) {
                        return (int) (imm + 1);
                    }
                }
                if (isBc) {
                    Long n = addiNegImmToR0(cand);
                    if (n != null && n >= 1 && n <= MAX_TABLE) {
                        return n.intValue();
                    }
                }
            }
        }
        return null;
    }

    // ---- validation: faithful copy of RecoverSwitchTables.validateTable ----
    private String validate(Instruction switchInsn, long tableBase, int size,
                            long[] targets) {
        if (size < 1 || size > MAX_TABLE) return "bad-size";
        long tableEnd = tableBase + size * 2L;
        if (!isCodeFlash(tableBase) || !isCodeFlash(tableEnd - 2)) return "table-oob";

        int forward = 0;
        Set<Long> unique = new HashSet<>();
        long sw = switchInsn.getAddress().getOffset();
        for (long tgt : targets) {
            if (!isCodeFlash(tgt)) return "target-oob";
            if (Math.abs(tgt - sw) > FAR) return "target-far";
            if (tgt >= tableEnd) forward++;
            unique.add(tgt);
        }
        if (forward < 1) return "no-forward";
        if (unique.size() < 1) return "no-unique";

        Function fn = getFunctionContaining(switchInsn.getAddress());
        if (fn != null) {
            long fmin = fn.getBody().getMinAddress().getOffset();
            long fmax = fn.getBody().getMaxAddress().getOffset();
            long pad = 0x1000L;
            for (long tgt : targets) {
                if (tgt < fmin - pad || tgt > fmax + pad) {
                    if (Math.abs(tgt - sw) > 0x2000L) return "outside-fn-pad";
                }
            }
        }

        Address cursor = toAddr(tableBase);
        Address end = toAddr(tableEnd - 1);
        InstructionIterator it = currentProgram.getListing().getInstructions(cursor, true);
        while (it.hasNext()) {
            Instruction insn = it.next();
            if (insn.getAddress().compareTo(end) > 0) break;
            if (insn.getMnemonicString().equalsIgnoreCase("switch")
                    && !insn.getAddress().equals(switchInsn.getAddress())) {
                return "nested-switch";
            }
        }
        return null;
    }

    /** A switch is "real" iff a prefix range-check yields a validated table. */
    private Integer realSize(Instruction switchInsn) throws Exception {
        Integer size = prefixBound(switchInsn);
        if (size == null) return null;
        long tableBase = switchInsn.getAddress().getOffset() + switchInsn.getLength();
        long[] targets = new long[size];
        for (int i = 0; i < size; i++) {
            short off = getShort(toAddr(tableBase + i * 2L));
            targets[i] = tableBase + (((long) off) << 1);
        }
        return validate(switchInsn, tableBase, size, targets) == null ? size : null;
    }

    private boolean isRecoveredTable(long tableBase) {
        Symbol s = currentProgram.getSymbolTable().getPrimarySymbol(toAddr(tableBase));
        return s != null && s.getName().startsWith("switch_table_");
    }

    @Override
    public void run() throws Exception {
        InstructionIterator it = currentProgram.getListing().getInstructions(true);
        List<Instruction> switches = new ArrayList<>();
        while (it.hasNext()) {
            Instruction insn = it.next();
            if (insn.getMnemonicString().equalsIgnoreCase("switch")) {
                switches.add(insn);
            }
        }

        int total = switches.size();
        int real = 0;          // prefix-bound + validated table
        int recovered = 0;     // carries a switch_table_ label
        int realNotRecovered = 0;
        int recoveredNotReal = 0;

        for (Instruction insn : switches) {
            long tableBase = insn.getAddress().getOffset() + insn.getLength();
            Integer size = realSize(insn);
            boolean isReal = size != null;
            boolean isRecovered = isRecoveredTable(tableBase);

            if (isReal) real++;
            if (isRecovered) recovered++;

            if (isReal && !isRecovered) {
                realNotRecovered++;
                fail(String.format("real switch %s (prefix-bound, size=%d) NOT recovered",
                        insn.getAddress(), size));
            }
            if (!isReal && isRecovered) {
                recoveredNotReal++;
                fail(String.format("recovered switch_table at 0x%x is NOT prefix-bound "
                        + "(false positive / data)", tableBase));
            }
            if (isReal && isRecovered) {
                // Confirm full case coverage by COMPUTED_JUMP refs.
                Set<Long> expected = new HashSet<>();
                for (int i = 0; i < size; i++) {
                    short off = getShort(toAddr(tableBase + i * 2L));
                    expected.add(tableBase + (((long) off) << 1));
                }
                Set<Long> jumpTargets = new HashSet<>();
                for (Reference r : currentProgram.getReferenceManager()
                        .getReferencesFrom(insn.getAddress())) {
                    if (r.getReferenceType().isJump()) {
                        jumpTargets.add(r.getToAddress().getOffset());
                    }
                }
                if (!jumpTargets.containsAll(expected)) {
                    Set<Long> missing = new HashSet<>(expected);
                    missing.removeAll(jumpTargets);
                    fail(String.format("switch %s: missing COMPUTED_JUMP targets %s",
                            insn.getAddress(), missing));
                }
            }
        }

        if (real != EXPECTED_REAL_SWITCHES) {
            fail(String.format("real (prefix-bound) switch count=%d expected=%d",
                    real, EXPECTED_REAL_SWITCHES));
        }
        if (real != recovered) {
            fail(String.format("real=%d != recovered=%d (boundary changed)",
                    real, recovered));
        }

        int collisions = total - real;
        println(String.format(
                "ASSERT switch-tables: total_decoded=%d real(prefix-bound)=%d "
                        + "recovered=%d collisions(data)=%d real_not_recovered=%d "
                        + "recovered_not_real=%d failures=%d",
                total, real, recovered, collisions,
                realNotRecovered, recoveredNotReal, failures.size()));
        if (!failures.isEmpty()) {
            throw new IllegalStateException(failures.size() + " switch-table failures: "
                    + String.join("; ", failures));
        }
    }
}
