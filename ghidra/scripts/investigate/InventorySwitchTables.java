//@author kaikozlov
//@category Investigation
// Measure EVERY decoded `switch` instruction against the recovery heuristic —
// in-function or not — and emit a per-switch CSV so the in-function/out-of-
// function boundary is evidence rather than an assertion. Read-only: it does
// not createData, disassemble, add references, or label anything.
//
// Faithful replica of RecoverSwitchTables.{boundFromPrefix,boundFromPackedCase0,
// readTargets,validateTable}: if this script reports a switch validates, the
// recoverer would recover it (and vice versa). Differences are intentional:
//  - validate() returns a failure reason instead of a bare boolean;
//  - the function-proximity gate is skipped when the switch is not in a
//    function (otherwise we could never measure out-of-function sites).
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.listing.Listing;
import ghidra.program.model.scalar.Scalar;

import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

public class InventorySwitchTables extends GhidraScript {
    private static final int MAX_TABLE = 256;
    private static final int MAX_LOOKBACK = 16;
    private static final long CODEFLASH_END = 0x100000L;
    private static final long FAR = 0x10000L;

    private static final class Bound {
        final int size;
        final String kind;
        Bound(int size, String kind) {
            this.size = size;
            this.kind = kind;
        }
    }

    private boolean isCodeFlash(long addr) {
        return addr >= 0L && addr < CODEFLASH_END && (addr & 1L) == 0L;
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

    private List<Instruction> previousInstructions(Instruction insn, int limit) {
        List<Instruction> prev = new ArrayList<>();
        Instruction cur = insn;
        for (int i = 0; i < limit; i++) {
            cur = cur.getPrevious();
            if (cur == null) break;
            prev.add(cur);
        }
        return prev;
    }

    private Bound boundFromPrefix(Instruction switchInsn) {
        List<Instruction> prev = previousInstructions(switchInsn, MAX_LOOKBACK);
        for (int i = 0; i < prev.size(); i++) {
            Instruction br = prev.get(i);
            String bm = br.getMnemonicString().toLowerCase();
            boolean isBh = bm.equals("bh") || bm.equals("bnh");
            boolean isBc = bm.equals("bc") || bm.equals("bnc");
            if (!isBh && !isBc) continue;
            for (int j = i + 1; j < prev.size(); j++) {
                Instruction cand = prev.get(j);
                if (isBh) {
                    Long imm = cmpImm(cand);
                    if (imm != null && imm + 1 >= 1 && imm + 1 <= MAX_TABLE) {
                        return new Bound((int) (imm + 1), "cmp+" + bm);
                    }
                }
                if (isBc) {
                    Long n = addiNegImmToR0(cand);
                    if (n != null && n >= 1 && n <= MAX_TABLE) {
                        return new Bound(n.intValue(), "addi+" + bm);
                    }
                }
            }
        }
        return null;
    }

    private Bound boundFromPackedCase0(long tableBase) throws Exception {
        short first = getShort(toAddr(tableBase));
        if (first < 1 || first > MAX_TABLE) return null;
        return new Bound(first, "packed-case0");
    }

    private long[] readTargets(long tableBase, int size) throws Exception {
        long[] targets = new long[size];
        for (int i = 0; i < size; i++) {
            short off = getShort(toAddr(tableBase + i * 2L));
            targets[i] = tableBase + (((long) off) << 1);
        }
        return targets;
    }

    private String validate(Instruction switchInsn, long tableBase, int size,
                            long[] targets, boolean inFunction) {
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

        if (inFunction) {
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
        return null; // ok
    }

    private static final class Outcome {
        boolean ok;
        String reason = "no-bound";
        int size;
        String kind = "";
        int forward;
        int unique;
    }

    private Outcome measure(Instruction switchInsn) throws Exception {
        Outcome o = new Outcome();
        long tableBase = switchInsn.getAddress().getOffset() + switchInsn.getLength();

        Bound fromPrefix = boundFromPrefix(switchInsn);
        if (fromPrefix != null) {
            long[] t = readTargets(tableBase, fromPrefix.size);
            String why = validate(switchInsn, tableBase, fromPrefix.size, t, true);
            if (why == null) {
                o.ok = true; o.size = fromPrefix.size; o.kind = fromPrefix.kind;
                return o;
            }
            o.reason = fromPrefix.kind + ":" + why;
            o.size = fromPrefix.size;
        }

        Bound packed = boundFromPackedCase0(tableBase);
        if (packed != null) {
            long[] t = readTargets(tableBase, packed.size);
            String why = validate(switchInsn, tableBase, packed.size, t, true);
            if (why == null) {
                o.ok = true; o.size = packed.size; o.kind = packed.kind;
                return o;
            }
            if (o.reason.equals("no-bound")) {
                o.reason = packed.kind + ":" + why;
                o.size = packed.size;
            }
        }
        return o;
    }

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        String outPath = args.length > 0 ? args[0] : "switch_inventory.csv";
        PrintWriter pw = new PrintWriter(outPath);
        pw.println("switch_addr,in_function,function_addr,table_base,bound_kind,bound_size,"
                + "validate_ok,fail_reason");

        InstructionIterator it = currentProgram.getListing().getInstructions(true);
        List<Instruction> switches = new ArrayList<>();
        while (it.hasNext()) {
            Instruction insn = it.next();
            if (insn.getMnemonicString().equalsIgnoreCase("switch")) {
                switches.add(insn);
            }
        }

        int total = switches.size();
        int inFn = 0, inFnOk = 0, outFn = 0, outFnOk = 0;
        for (Instruction insn : switches) {
            Function fn = getFunctionContaining(insn.getAddress());
            boolean inFunction = fn != null;
            long tableBase = insn.getAddress().getOffset() + insn.getLength();
            Outcome o = measure(insn);
            if (inFunction) {
                inFn++;
                if (o.ok) inFnOk++;
            } else {
                outFn++;
                if (o.ok) outFnOk++;
            }
            pw.printf("%08x,%s,%s,%08x,%s,%d,%s,%s%n",
                    insn.getAddress().getOffset(),
                    inFunction ? "Y" : "N",
                    inFunction ? String.format("%08x", fn.getEntryPoint().getOffset()) : "-",
                    tableBase,
                    o.ok ? o.kind : "",
                    o.ok ? o.size : 0,
                    o.ok ? "Y" : "N",
                    o.ok ? "" : o.reason);
        }
        pw.close();

        println(String.format(
                "InventorySwitchTables: total=%d in_function=%d (valid=%d) "
                        + "out_of_function=%d (valid=%d) -> %s",
                total, inFn, inFnOk, outFn, outFnOk,
                outPath));
    }
}
