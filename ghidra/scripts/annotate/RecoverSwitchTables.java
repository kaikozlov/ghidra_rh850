//@author kaikozlov
//@category Analysis
// Recover RH850 `switch` jump tables for in-function sites: size the table from
// the compiler bound check (or the packed case-0 idiom), define the halfword
// array, and add COMPUTED_JUMP references from the switch to every case target.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.ArrayDataType;
import ghidra.program.model.data.ShortDataType;
import ghidra.program.model.listing.Data;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.listing.Listing;
import ghidra.program.model.scalar.Scalar;
import ghidra.program.model.symbol.RefType;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.SourceType;
import ghidra.program.model.symbol.SymbolTable;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

public class RecoverSwitchTables extends GhidraScript {
    private static final int MAX_TABLE = 256;
    private static final int MAX_LOOKBACK = 16;
    private static final long CODEFLASH_END = 0x100000L;

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

    private String switchReg(Instruction insn) {
        if (insn.getNumOperands() < 1) return null;
        Object[] ops = insn.getOpObjects(0);
        return ops.length == 0 ? null : ops[0].toString();
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
            prev.add(cur); // index 0 = closest to switch
        }
        return prev;
    }

    private Bound boundFromPrefix(Instruction switchInsn) {
        List<Instruction> prev = previousInstructions(switchInsn, MAX_LOOKBACK);
        for (int i = 0; i < prev.size(); i++) {
            Instruction br = prev.get(i);
            String bm = br.getMnemonicString().toLowerCase();
            boolean isBh = bm.equals("bh") || bm.equals("bnh");
            boolean isBc = bm.equals("bc");
            boolean isBnc = bm.equals("bnc");
            if (!isBh && !isBc && !isBnc) continue;
            for (int j = i + 1; j < prev.size(); j++) {
                Instruction cand = prev.get(j);
                if (isBh) {
                    Long imm = cmpImm(cand);
                    if (imm != null && imm + 1 >= 1 && imm + 1 <= MAX_TABLE) {
                        return new Bound((int) (imm + 1), "cmp+" + bm);
                    }
                }
                if (isBc || isBnc) {
                    Long n = addiNegImmToR0(cand);
                    if (n != null && n >= 1 && n <= MAX_TABLE) {
                        // addi -N,rX,r0; bc default  => CY when rX >= N => size N
                        // bnc is the inverted idiom; still size N when present.
                        return new Bound(n.intValue(), "addi+" + bm);
                    }
                }
            }
        }
        return null;
    }

    private Bound boundFromPackedCase0(long tableBase) throws Exception {
        // Common RH850/GHS packing: case 0 starts immediately after the table, so
        // the first signed halfword equals the entry count.
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

    private boolean validateTable(Instruction switchInsn, long tableBase, int size,
                                  long[] targets) {
        if (size < 1 || size > MAX_TABLE) return false;
        long tableEnd = tableBase + size * 2L;
        if (!isCodeFlash(tableBase) || !isCodeFlash(tableEnd - 2)) return false;

        Function fn = getFunctionContaining(switchInsn.getAddress());
        int forward = 0;
        Set<Long> unique = new HashSet<>();
        for (long tgt : targets) {
            if (!isCodeFlash(tgt)) return false;
            // Reject wildly far targets; real cases stay near the switch site.
            if (Math.abs(tgt - switchInsn.getAddress().getOffset()) > 0x10000L) {
                return false;
            }
            if (tgt >= tableEnd) forward++;
            unique.add(tgt);
        }
        // At least one forward case (typical packed layout) and enough unique arms.
        if (forward < 1) return false;
        if (unique.size() < 1) return false;
        // Prefer targets that stay near the enclosing function, but do not require
        // them to already lie inside the body — computed jumps often leave cases
        // outside the analyzer's current function bounds.
        if (fn != null) {
            long fmin = fn.getBody().getMinAddress().getOffset();
            long fmax = fn.getBody().getMaxAddress().getOffset();
            long pad = 0x1000L;
            for (long tgt : targets) {
                if (tgt < fmin - pad || tgt > fmax + pad) {
                    // Still allow near-switch targets outside a tight body.
                    if (Math.abs(tgt - switchInsn.getAddress().getOffset()) > 0x2000L) {
                        return false;
                    }
                }
            }
        }
        // Overlap with ordinary code is OK (we clear the table range); refuse if
        // another switch instruction sits inside the candidate table.
        Listing listing = currentProgram.getListing();
        Address cursor = toAddr(tableBase);
        Address end = toAddr(tableEnd - 1);
        InstructionIterator it = listing.getInstructions(cursor, true);
        while (it.hasNext()) {
            Instruction insn = it.next();
            if (insn.getAddress().compareTo(end) > 0) break;
            if (insn.getMnemonicString().equalsIgnoreCase("switch")
                    && !insn.getAddress().equals(switchInsn.getAddress())) {
                return false;
            }
        }
        return true;
    }

    private Bound chooseBound(Instruction switchInsn, long tableBase) throws Exception {
        Bound fromPrefix = boundFromPrefix(switchInsn);
        if (fromPrefix != null) {
            long[] targets = readTargets(tableBase, fromPrefix.size);
            if (validateTable(switchInsn, tableBase, fromPrefix.size, targets)) {
                return fromPrefix;
            }
        }
        Bound packed = boundFromPackedCase0(tableBase);
        if (packed != null) {
            long[] targets = readTargets(tableBase, packed.size);
            if (validateTable(switchInsn, tableBase, packed.size, targets)) {
                return packed;
            }
        }
        return null;
    }

    private void ensureTableData(long tableBase, int size) throws Exception {
        Listing listing = currentProgram.getListing();
        Address start = toAddr(tableBase);
        Address end = toAddr(tableBase + size * 2L - 1L);
        // Drop instructions/data that collide with the halfword table.
        listing.clearCodeUnits(start, end, false);
        ArrayDataType arr = new ArrayDataType(ShortDataType.dataType, size, 2);
        Data existing = listing.getDataAt(start);
        if (existing != null && existing.isDefined()
                && existing.getDataType().isEquivalent(arr)
                && existing.getLength() == size * 2) {
            return;
        }
        if (existing != null) {
            listing.clearCodeUnits(start, end, false);
        }
        createData(start, arr);
    }

    private void labelTable(long tableBase, int size) throws Exception {
        SymbolTable symbols = currentProgram.getSymbolTable();
        Address a = toAddr(tableBase);
        String name = String.format("switch_table_%08x", tableBase);
        var primary = symbols.getPrimarySymbol(a);
        if (primary == null) {
            symbols.createLabel(a, name, SourceType.ANALYSIS);
        } else if (primary.getSource() != SourceType.USER_DEFINED
                && primary.getSource() != SourceType.IMPORTED) {
            try {
                primary.setName(name, SourceType.ANALYSIS);
            } catch (Exception ignored) {
                // Keep an existing stronger name.
            }
        }
        currentProgram.getListing().setComment(a,
                ghidra.program.model.listing.CodeUnit.PLATE_COMMENT,
                String.format("RH850 switch jump table (%d signed halfword offsets)", size));
    }

    private void addJumpRef(Address from, Address to) {
        Reference[] refs = currentProgram.getReferenceManager().getReferencesFrom(from);
        for (Reference ref : refs) {
            if (ref.getToAddress().equals(to) && ref.getReferenceType().isJump()) {
                return;
            }
        }
        currentProgram.getReferenceManager().addMemoryReference(
                from, to, RefType.COMPUTED_JUMP, SourceType.ANALYSIS, 0);
    }

    private void addDataRef(Address from, Address to) {
        Reference[] refs = currentProgram.getReferenceManager().getReferencesFrom(from);
        for (Reference ref : refs) {
            if (ref.getToAddress().equals(to)) return;
        }
        currentProgram.getReferenceManager().addMemoryReference(
                from, to, RefType.DATA, SourceType.ANALYSIS, 0);
    }

    private void ensureCaseCode(long target) {
        if (!isCodeFlash(target)) return;
        Address a = toAddr(target);
        Listing listing = currentProgram.getListing();
        if (listing.getInstructionAt(a) != null) return;
        // Don't clear large ranges; only claim the entry byte if undefined/data.
        Data data = listing.getDataContaining(a);
        if (data != null) {
            listing.clearCodeUnits(data.getMinAddress(), data.getMaxAddress(), false);
        }
        disassemble(a);
    }

    private int recoverOne(Instruction switchInsn) throws Exception {
        long switchAddr = switchInsn.getAddress().getOffset();
        long tableBase = switchAddr + switchInsn.getLength();
        Bound bound = chooseBound(switchInsn, tableBase);
        if (bound == null) {
            println(String.format("skip switch %s: no validated table size",
                    switchInsn.getAddress()));
            return 0;
        }
        long[] targets = readTargets(tableBase, bound.size);
        ensureTableData(tableBase, bound.size);
        labelTable(tableBase, bound.size);

        Set<Long> unique = new HashSet<>();
        for (int i = 0; i < targets.length; i++) {
            long tgt = targets[i];
            unique.add(tgt);
            addJumpRef(switchInsn.getAddress(), toAddr(tgt));
            addDataRef(toAddr(tableBase + i * 2L), toAddr(tgt));
            ensureCaseCode(tgt);
        }

        currentProgram.getListing().setComment(switchInsn.getAddress(),
                ghidra.program.model.listing.CodeUnit.EOL_COMMENT,
                String.format("switch table @ 0x%x (%d entries, %s)",
                        tableBase, bound.size, bound.kind));

        println(String.format(
                "recovered switch %s table@0x%x size=%d unique=%d kind=%s",
                switchInsn.getAddress(), tableBase, bound.size, unique.size(), bound.kind));
        return bound.size;
    }

    @Override
    public void run() throws Exception {
        int considered = 0;
        int recovered = 0;
        int entries = 0;
        int skippedOutsideFn = 0;

        InstructionIterator it = currentProgram.getListing().getInstructions(true);
        List<Instruction> switches = new ArrayList<>();
        while (it.hasNext()) {
            Instruction insn = it.next();
            if (insn.getMnemonicString().equalsIgnoreCase("switch")) {
                switches.add(insn);
            }
        }

        for (Instruction insn : switches) {
            Function fn = getFunctionContaining(insn.getAddress());
            if (fn == null) {
                skippedOutsideFn++;
                continue;
            }
            considered++;
            int n = recoverOne(insn);
            if (n > 0) {
                recovered++;
                entries += n;
            }
        }

        println(String.format(
                "RecoverSwitchTables: in_function=%d recovered=%d entries=%d skipped_outside_fn=%d total_decoded_switch=%d",
                considered, recovered, entries, skippedOutsideFn, switches.size()));
        if (considered > 0 && recovered == 0) {
            throw new IllegalStateException("no in-function switch tables recovered");
        }
    }
}
