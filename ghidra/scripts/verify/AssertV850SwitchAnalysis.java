//@author kaikozlov
//@category Verification
// Behavioral fixtures for the V850SwitchAnalysis auto analyzer. Builds
// disposable in-memory v850e3 programs covering all four supported dispatch
// families plus reject/coexistence cases, runs the real auto-analysis pipeline
// (analyzer discovery, disassembly scheduling, function-body fixup), and
// asserts jump-table data, references, labels, disassembly and decompiler
// effects: every recovered dispatch must decompile to a natively modeled
// structured switch, while rejected near-matches must not. Switch indices are
// entry-register values so the decompiler cannot constant-fold the dispatch.
// Throws on any failure; prints "ASSERT v850-switch-analysis: passed".
import ghidra.app.cmd.disassemble.DisassembleCommand;
import ghidra.app.cmd.function.CreateFunctionCmd;
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.plugin.core.analysis.AutoAnalysisManager;
import ghidra.app.script.GhidraScript;
import ghidra.program.database.ProgramDB;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.ArrayDataType;
import ghidra.program.model.data.ShortDataType;
import ghidra.program.model.lang.Language;
import ghidra.program.model.lang.LanguageID;
import ghidra.program.model.listing.Data;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.Program;
import ghidra.program.model.mem.Memory;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.symbol.RefType;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.SourceType;
import ghidra.program.model.symbol.Symbol;
import ghidra.program.util.DefaultLanguageService;
import java.util.ArrayList;
import java.util.List;
import java.util.TreeSet;

public class AssertV850SwitchAnalysis extends GhidraScript {
    private final List<String> failures = new ArrayList<>();

    // ------------------------------------------------------------------
    // V850 encoders (validated against the vendored SLEIGH by disassembly)
    // ------------------------------------------------------------------
    static byte[] u16(int v) { return new byte[] { (byte) v, (byte) (v >> 8) }; }
    static byte[] u32(int v) {
        return new byte[] { (byte) v, (byte) (v >> 8), (byte) (v >> 16), (byte) (v >> 24) };
    }
    static byte[] cat(byte[]... parts) {
        int n = 0;
        for (byte[] p : parts) n += p.length;
        byte[] out = new byte[n];
        int off = 0;
        for (byte[] p : parts) { System.arraycopy(p, 0, out, off, p.length); off += p.length; }
        return out;
    }
    static int w0(int op6, int r1, int r2) { return (op6 << 5) | (r2 << 11) | (r1 & 0x1f); }
    static byte[] movImm5(int imm, int r2) { return u16((0x10 << 5) | (r2 << 11) | (imm & 0x1f)); }
    static byte[] movImm32(int v, int r1) {
        return cat(u16((0x031 << 5) | r1), u16(v & 0xffff), u16((v >> 16) & 0xffff));
    }
    static byte[] movea(int imm16, int r1, int r2) { return cat(u16(w0(0x31, r1, r2)), u16(imm16)); }
    static byte[] addi(int imm16, int r1, int r2) { return cat(u16(w0(0x30, r1, r2)), u16(imm16)); }
    static byte[] movhi(int imm16, int r1, int r2) { return cat(u16(w0(0x32, r1, r2)), u16(imm16)); }
    static byte[] addImm5(int imm, int r2) { return u16(w0(0x12, imm, r2)); }
    static byte[] addReg(int r1, int r2) { return u16(w0(0x0e, r1, r2)); }
    static byte[] cmpImm5(int imm, int r2) { return u16((0x13 << 5) | (r2 << 11) | (imm & 0x1f)); }
    static byte[] shlImm5(int imm, int r2) { return u16((0x16 << 5) | (r2 << 11) | (imm & 0x1f)); }
    static byte[] switchI(int r) { return u16((0x002 << 5) | r); }
    static byte[] jmpReg(int r) { return u16((0x003 << 5) | r); }
    // Bcond addr9: disp = (s5 << 4) | (x3 << 1), relative to instruction start
    static byte[] bcond(int cc, int disp) {
        int s5 = (disp >> 4) & 0x1f;
        int x3 = (disp >> 1) & 0x7;
        return u16((0xB << 7) | (s5 << 11) | (x3 << 4) | cc);
    }
    static byte[] ldH(int d, int r1, int r2) { return cat(u16(w0(0x39, r1, r2)), u16(d & 0xfffe)); }
    static byte[] ldW(int d, int r1, int r2) {
        return cat(u16(w0(0x39, r1, r2)), u16((((d >> 1) & 0x7fff) << 1) | 1));
    }
    static byte[] jmpDisp32(int d, int r1) {
        return cat(u16((0x037 << 5) | r1), u16(((d >> 1) & 0x7fff) << 1), u16((d >> 16) & 0xffff));
    }
    static byte[] jr22(int disp) {
        return cat(u16((0x1e << 6) | ((disp >> 16) & 0x3f)), u16(disp & 0xffff));
    }
    static byte[] jrFrom(long at, long target) { return jr22((int) (target - at)); }

    // ------------------------------------------------------------------
    // Fixture plumbing
    // ------------------------------------------------------------------

    private ProgramDB newProgram(String name) throws Exception {
        Language lang = DefaultLanguageService.getLanguageService()
            .getLanguage(new LanguageID("v850e3:LE:32:default"));
        ProgramDB p = new ProgramDB(name, lang, lang.getDefaultCompilerSpec(), this);
        try (var tx = p.openTransaction("init")) {
            MemoryBlock block = p.getMemory().createInitializedBlock("flash",
                a(p, 0), 0x10000, (byte) 0, monitor, false);
            block.setExecute(true);
            // isolate switch attribution: the generic decompiler-based switch
            // recovery stays out of these fixtures
            p.getOptions(Program.ANALYSIS_PROPERTIES).setBoolean("Decompiler Switch Analysis", false);
        }
        return p;
    }

    private static Address a(Program p, long off) {
        return p.getAddressFactory().getDefaultAddressSpace().getAddress(off);
    }

    private void put(ProgramDB p, long at, byte[] data) throws Exception {
        p.getMemory().setBytes(a(p, at), data);
    }

    private void analyze(ProgramDB p, long entry) throws Exception {
        try (var tx = p.openTransaction("disassemble")) {
            new DisassembleCommand(a(p, entry), null, true).applyTo(p, monitor);
            new CreateFunctionCmd(a(p, entry)).applyTo(p, monitor);
        }
        AutoAnalysisManager am = AutoAnalysisManager.getAnalysisManager(p);
        try (var tx = p.openTransaction("reanalyze")) {
            am.reAnalyzeAll(null);
        }
        int txId = p.startTransaction("analysis");
        boolean ok = false;
        try {
            am.startAnalysis(monitor);
            ok = true;
        }
        finally {
            p.endTransaction(txId, ok);
        }
    }

    private void fail(String msg) {
        failures.add(msg);
        println("FAIL: " + msg);
    }

    private void check(boolean cond, String msg) {
        if (!cond) fail(msg);
    }

    private TreeSet<Long> computedJumpTargets(Program p, long from) {
        TreeSet<Long> out = new TreeSet<>();
        for (Reference ref : p.getReferenceManager().getReferencesFrom(a(p, from))) {
            if (ref.getReferenceType() == RefType.COMPUTED_JUMP) {
                out.add(ref.getToAddress().getOffset());
            }
        }
        return out;
    }

    private void checkCaseChain(ProgramDB p, long dispatch, long[] targets, String what) {
        TreeSet<Long> got = computedJumpTargets(p, dispatch);
        for (long t : targets) {
            check(got.contains(t), what + ": missing COMPUTED_JUMP ref -> 0x" + Long.toHexString(t));
        }
        check(got.size() == targets.length,
            what + ": expected " + targets.length + " computed targets, got " + got.size());
        for (long t : targets) {
            Instruction insn = p.getListing().getInstructionAt(a(p, t));
            check(insn != null, what + ": case target 0x" + Long.toHexString(t) + " not disassembled");
        }
    }

    private void checkBodyContains(ProgramDB p, long entry, long[] addrs, String what) {
        Function fn = p.getFunctionManager().getFunctionAt(a(p, entry));
        check(fn != null, what + ": function at entry missing");
        if (fn == null) return;
        for (long t : addrs) {
            check(fn.getBody().contains(a(p, t)),
                what + ": body missing case target 0x" + Long.toHexString(t));
        }
    }

    private void checkLabel(ProgramDB p, long at, String name, String what) {
        for (Symbol s : p.getSymbolTable().getSymbols(a(p, at))) {
            if (s.getName().equals(name)) {
                check(s.getParentNamespace().getName().startsWith("switchD_"),
                    what + ": label " + name + " not in switchD namespace");
                return;
            }
        }
        fail(what + ": label " + name + " missing at 0x" + Long.toHexString(at));
    }

    /** mov i, r7 ; jr join — six bytes per case arm. */
    private void putCase(ProgramDB p, long at, int value, long join) throws Exception {
        put(p, at, movImm5(value & 0x1f, 7));
        put(p, at + 2, jrFrom(at + 2, join));
    }

    // ------------------------------------------------------------------
    // Fixtures
    // ------------------------------------------------------------------

    // Family 1: native switch, cmp+bh bound, movea normalization (lowcase 3),
    // one backward case target. The index arrives in r6 as an entry-register
    // value (argument-like): a constant index would let the decompiler fold
    // the bound branch and refuse the jump-table model, so no structured
    // switch could be asserted.
    private void fixtureNativeSwitch() throws Exception {
        ProgramDB p = newProgram("native-switch");
        long[] targets = { 0x1020, 0x1026, 0x102c, 0x1032, 0x0ff0 };
        try (var tx = p.openTransaction("bytes")) {
            // dispatch chain
            put(p, 0x1000, movea(-3, 6, 18));                // r18 = r6 - 3
            put(p, 0x1004, cmpImm5(4, 18));           // ncases = 5 (cases 3..7)
            put(p, 0x1006, bcond(0xB, 0x1040 - 0x1006)); // bh default
            put(p, 0x1008, switchI(18));              // table at 0x100a
            for (int i = 0; i < 4; i++) {
                put(p, 0x100a + 2L * i, u16((int) ((targets[i] - 0x100a) / 2)));
            }
            put(p, 0x1012, u16((int) ((0x0ff0 - 0x100a) / 2))); // backward: -13
            for (int i = 0; i < 4; i++) {
                putCase(p, targets[i], i + 1, 0x1060);
            }
            putCase(p, 0x0ff0, 5, 0x1060);
            putCase(p, 0x1040, 0x1f, 0x1060); // default arm
            put(p, 0x1060, jmpReg(31));

        }
        analyze(p, 0x1000);

        Data table = p.getListing().getDefinedDataAt(a(p, 0x100a));
        check(table != null, "native: table data missing at 0x100a");
        if (table != null) {
            check(table.getLength() == 10, "native: table length != 10");
            check(table.getNumComponents() == 5, "native: table components != 5");
            check(((ghidra.program.model.scalar.Scalar) table.getComponent(4).getValue()).getSignedValue() == -13,
                "native: backward element value != -13");
        }
        checkCaseChain(p, 0x1008, targets, "native");
        checkBodyContains(p, 0x1000, new long[] { 0x1020, 0x1026, 0x1032 }, "native");
        checkLabel(p, 0x1020, "caseD_3", "native");
        checkLabel(p, 0x0ff0, "caseD_7", "native");
        checkLabel(p, 0x1040, "default", "native");
        checkLabel(p, 0x100a, "switchdataD_0000100a", "native");
        decompileAsserts(p, 0x1000, "native");
        p.release(this);
    }

    private void decompileAsserts(ProgramDB p, long entry, String what) {
        String c = decompile(p, entry, what);
        if (c == null) {
            return; // decompile already recorded its own failure
        }
        check(c.matches("(?s).*\\bswitch\\s*\\(.*"),
            what + ": decompiler did not recover a structured switch");
    }

    /** Unguarded or unrecovered dispatches must not become structured switches. */
    private void decompileNoSwitch(ProgramDB p, long entry, String what) {
        String c = decompile(p, entry, what);
        if (c == null) {
            return;
        }
        check(!c.matches("(?s).*\\bswitch\\s*\\(.*"),
            what + ": rejected dispatch must not decompile as a structured switch");
    }

    private String decompile(ProgramDB p, long entry, String what) {
        try {
            Function fn = p.getFunctionManager().getFunctionAt(a(p, entry));
            DecompInterface ifc = new DecompInterface();
            ifc.openProgram(p);
            DecompileResults res = ifc.decompileFunction(fn, 60, monitor);
            ifc.dispose();
            check(res != null && res.decompileCompleted(), what + ": decompile failed");
            if (res == null || res.getDecompiledFunction() == null) {
                fail(what + ": no decompiled function");
                return null;
            }
            return res.getDecompiledFunction().getC();
        }
        catch (Exception e) {
            fail(what + ": decompiler exception " + e);
        }
        return null;
    }

    // Family 1: native switch with addi -N,rX,r0 + bc bound.
    private void fixtureNativeSwitchAddi() throws Exception {
        ProgramDB p = newProgram("native-switch-addi");
        long[] targets = new long[6];
        try (var tx = p.openTransaction("bytes")) {
            put(p, 0x1100, addi(-6, 18, 0));              // ncases = 6
            put(p, 0x1104, bcond(0x1, 0x1160 - 0x1104));  // bc default
            put(p, 0x1106, switchI(18));                  // table at 0x1108
            for (int i = 0; i < 6; i++) {
                targets[i] = 0x1120 + 6L * i;
                put(p, 0x1108 + 2L * i, u16((int) ((targets[i] - 0x1108) / 2)));
                putCase(p, targets[i], i + 1, 0x1168);
            }
            putCase(p, 0x1160, 0x1f, 0x1168);
            put(p, 0x1168, jmpReg(31));

        }
        analyze(p, 0x1100);

        checkCaseChain(p, 0x1106, targets, "native-addi");
        Data table = p.getListing().getDefinedDataAt(a(p, 0x1108));
        check(table != null && table.getNumComponents() == 6, "native-addi: table data wrong");
        checkLabel(p, 0x1120, "caseD_0", "native-addi");
        checkLabel(p, 0x1160, "default", "native-addi");
        decompileAsserts(p, 0x1100, "native-addi");
        p.release(this);
    }

    // Family 1: native switch, inverted bnh body-branch + jr default.
    private void fixtureNativeSwitchBnh() throws Exception {
        ProgramDB p = newProgram("native-switch-bnh");
        long[] targets = { 0x1220, 0x1226, 0x122c };
        try (var tx = p.openTransaction("bytes")) {
            put(p, 0x1200, cmpImm5(2, 18));              // ncases = 3
            put(p, 0x1202, bcond(0x3, 0x1208 - 0x1202)); // bnh -> switch (body)
            put(p, 0x1204, jrFrom(0x1204, 0x1240));      // jr default
            put(p, 0x1208, switchI(18));                 // table at 0x120a
            for (int i = 0; i < 3; i++) {
                put(p, 0x120a + 2L * i, u16((int) ((targets[i] - 0x120a) / 2)));
                putCase(p, targets[i], i + 1, 0x1250);
            }
            putCase(p, 0x1240, 0x1f, 0x1250);
            put(p, 0x1250, jmpReg(31));

        }
        analyze(p, 0x1200);

        checkCaseChain(p, 0x1208, targets, "native-bnh");
        checkLabel(p, 0x1240, "default", "native-bnh");
        Data table = p.getListing().getDefinedDataAt(a(p, 0x120a));
        check(table != null && table.getNumComponents() == 3, "native-bnh: table data wrong");
        decompileAsserts(p, 0x1200, "native-bnh");
        p.release(this);
    }

    // Family 2: direct jump table of jr instructions, shl 2 index scale.
    private void fixtureDirectTable() throws Exception {
        ProgramDB p = newProgram("direct-table");
        long[] cases = { 0x1320, 0x1326, 0x132c, 0x12f0 };
        try (var tx = p.openTransaction("bytes")) {
            put(p, 0x1300, cmpImm5(3, 18));                 // ncases = 4
            put(p, 0x1302, bcond(0xB, 0x1360 - 0x1302));    // bh default
            put(p, 0x1304, shlImm5(2, 18));
            put(p, 0x1306, jmpDisp32(0x1400, 18));          // table at 0x1400
            for (int i = 0; i < 4; i++) {
                put(p, 0x1400 + 4L * i, jrFrom(0x1400 + 4L * i, cases[i]));
                putCase(p, cases[i], i + 1, 0x1370);
            }
            putCase(p, 0x1360, 0x1f, 0x1370);
            put(p, 0x1370, jmpReg(31));

        }
        analyze(p, 0x1300);

        long[] entries = { 0x1400, 0x1404, 0x1408, 0x140c };
        checkCaseChain(p, 0x1306, entries, "direct");
        check(p.getListing().getDefinedDataAt(a(p, 0x1400)) == null,
            "direct: instruction table must not become data");
        Instruction entry0 = p.getListing().getInstructionAt(a(p, 0x1400));
        check(entry0 != null && entry0.getMnemonicString().equals("jr"),
            "direct: table entry 0 not disassembled as jr");
        // The backward case body itself is validated via disassembly + the
        // entry stub's flow reference; generic function-start/tail-call
        // heuristics may legitimately claim it as a separate function in a
        // sparse fixture program.
        Instruction back = p.getListing().getInstructionAt(a(p, 0x12f0));
        check(back != null, "direct: backward case code missing");
        if (back != null) {
            boolean flowed = false;
            for (Reference r : p.getReferenceManager().getReferencesTo(a(p, 0x12f0))) {
                if (r.getFromAddress().getOffset() == 0x140c) flowed = true;
            }
            check(flowed, "direct: entry stub flow to backward case missing");
        }
        checkBodyContains(p, 0x1300, new long[] { 0x1320, 0x1326, 0x132c, 0x1400, 0x140c }, "direct");
        decompileAsserts(p, 0x1300, "direct");
        p.release(this);
    }

    // Family 3: loaded signed halfword table with tracked element base.
    private void fixtureLoadedRelative() throws Exception {
        ProgramDB p = newProgram("loaded-relative");
        long[] targets = { 0x1520, 0x1526, 0x152c, 0x1540 };
        try (var tx = p.openTransaction("bytes")) {
            put(p, 0x1500, movImm32(0x1560, 7));            // element base
            put(p, 0x1506, cmpImm5(3, 18));                 // ncases = 4
            put(p, 0x1508, bcond(0xB, 0x1580 - 0x1508));    // bh default
            put(p, 0x150a, shlImm5(1, 18));
            put(p, 0x150c, ldH(0x1600, 18, 18));            // table at 0x1600
            put(p, 0x1510, addReg(7, 18));                  // + element base
            put(p, 0x1512, jmpReg(18));                     // dispatch
            int[] elems = { 0x1520 - 0x1560, 0x1526 - 0x1560, 0x152c - 0x1560, 0x1540 - 0x1560 };
            for (int i = 0; i < 4; i++) {
                put(p, 0x1600 + 2L * i, u16(elems[i]));
                putCase(p, targets[i], i + 1, 0x1590);
            }
            putCase(p, 0x1580, 0x1f, 0x1590);
            put(p, 0x1590, jmpReg(31));

        }
        analyze(p, 0x1500);

        checkCaseChain(p, 0x1512, targets, "loaded-rel");
        Data table = p.getListing().getDefinedDataAt(a(p, 0x1600));
        check(table != null && table.getNumComponents() == 4, "loaded-rel: table data wrong");
        if (table != null) {
            check(((ghidra.program.model.scalar.Scalar) table.getComponent(0).getValue()).getSignedValue() == -64,
                "loaded-rel: element 0 != -64");
        }
        checkLabel(p, 0x1520, "caseD_0", "loaded-rel");
        checkLabel(p, 0x1600, "switchdataD_00001600", "loaded-rel");
        // per-element data references from the table to the case targets
        boolean elemRef = false;
        for (Reference ref : p.getReferenceManager().getReferencesFrom(a(p, 0x1600))) {
            if (ref.getToAddress().getOffset() == 0x1520) elemRef = true;
        }
        check(elemRef, "loaded-rel: element->case data reference missing");
        decompileAsserts(p, 0x1500, "loaded-rel");
        p.release(this);
    }

    // Family 4: loaded absolute word table, jmp [reg].
    private void fixtureLoadedAbsolute() throws Exception {
        ProgramDB p = newProgram("loaded-absolute");
        long[] targets = { 0x1720, 0x1726, 0x172c };
        try (var tx = p.openTransaction("bytes")) {
            put(p, 0x1700, cmpImm5(2, 18));                 // ncases = 3
            put(p, 0x1702, bcond(0xB, 0x1760 - 0x1702));    // bh default
            put(p, 0x1704, shlImm5(2, 18));
            put(p, 0x1706, ldW(0x1800, 18, 18));            // table at 0x1800
            put(p, 0x170a, jmpReg(18));                     // dispatch, element base 0
            for (int i = 0; i < 3; i++) {
                put(p, 0x1800 + 4L * i, u32((int) targets[i]));
                putCase(p, targets[i], i + 1, 0x1770);
            }
            putCase(p, 0x1760, 0x1f, 0x1770);
            put(p, 0x1770, jmpReg(31));

        }
        analyze(p, 0x1700);

        checkCaseChain(p, 0x170a, targets, "loaded-abs");
        Data table = p.getListing().getDefinedDataAt(a(p, 0x1800));
        check(table != null && table.getNumComponents() == 3, "loaded-abs: table data wrong");
        checkLabel(p, 0x1720, "caseD_0", "loaded-abs");
        decompileAsserts(p, 0x1700, "loaded-abs");
        p.release(this);
    }

    private void fixtureMaterializedBases() throws Exception {
        for (int variant = 0; variant < 4; variant++) {
            String label = "materialized-base-" + variant;
            ProgramDB p = newProgram(label);
            long table = variant == 1 ? 0x2400 : 0xf000;
            long[] targets = {0x2140, 0x2146, 0x214c};
            long dispatch;
            try {
                try (var tx = p.openTransaction("bytes")) {
                    put(p, 0x2100, movhi(1, 0, 7));
                    put(p, 0x2104, movea(-0x1000, 7, 7));
                    put(p, 0x2108, addImm5(-5, 18));
                    put(p, 0x210a, cmpImm5(2, 18));
                    put(p, 0x210c, bcond(0xB, 0x2160 - 0x210c));
                    put(p, 0x210e, shlImm5(2, 18));
                    int loadedReg = variant == 2 ? 7 : 18;
                    long at = 0x2110;
                    if (variant == 1) {
                        put(p, at, addi((int) table, 18, 18));
                        at += 4;
                    } else {
                        if (variant == 3) {
                            put(p, at, u16(w0(0, 6, 7))); // unknown writer kills the base
                            at += 2;
                        }
                        put(p, at, variant == 2 ? addReg(18, 7) : addReg(7, 18));
                        at += 2;
                    }
                    put(p, at, ldW(0, loadedReg, loadedReg));
                    at += 4;
                    if (variant == 1) {
                        put(p, at, addImm5(4, loadedReg));
                        at += 2;
                    }
                    dispatch = at;
                    put(p, dispatch, jmpReg(loadedReg));
                    for (int i = 0; i < targets.length; i++) {
                        put(p, table + 4L * i, u32((int) targets[i] - (variant == 1 ? 4 : 0)));
                        putCase(p, targets[i], i + 1, 0x2170);
                    }
                    putCase(p, 0x2160, 15, 0x2170);
                    put(p, 0x2170, jmpReg(31));
                }
                analyze(p, 0x2100);
                if (variant == 3) {
                    check(computedJumpTargets(p, dispatch).isEmpty(),
                        label + ": unknown base must not produce speculative targets");
                } else {
                    checkCaseChain(p, dispatch, targets, label);
                    checkLabel(p, targets[0], "caseD_5", label);
                    checkLabel(p, targets[2], "caseD_7", label);
                    checkBodyContains(p, 0x2100, targets, label);
                    decompileAsserts(p, 0x2100, label);
                }
            } finally {
                p.release(this);
            }
        }
    }

    // Rejects: unbounded switch and a switch whose table decodes off-memory.
    private void fixtureRejects() throws Exception {
        ProgramDB p = newProgram("rejects");
        try (var tx = p.openTransaction("bytes")) {
            // decoy 1: no range-check prefix at all
            put(p, 0x1900, movImm5(1, 5));
            put(p, 0x1902, switchI(18)); // table at 0x1904
            put(p, 0x1904, cat(u16(2), u16(4), u16(6)));
            // decoy 2: valid prefix, table elements point outside any block
            put(p, 0x1a00, cmpImm5(3, 18));
            put(p, 0x1a02, bcond(0xB, 0x1a40 - 0x1a02));
            put(p, 0x1a04, switchI(18)); // table at 0x1a06
            put(p, 0x1a06, cat(u16(0x7fff), u16(0x7ffe), u16(0x7ffd), u16(0x7ffc)));
            put(p, 0x1a40, jmpReg(31));

        }
        analyze(p, 0x1900);

        check(computedJumpTargets(p, 0x1902).isEmpty(), "reject: unbounded switch got refs");
        check(computedJumpTargets(p, 0x1a04).isEmpty(), "reject: off-memory table got refs");
        check(p.getListing().getDefinedDataAt(a(p, 0x1904)) == null,
            "reject: decoy table 0x1904 became data");
        check(p.getListing().getDefinedDataAt(a(p, 0x1a06)) == null,
            "reject: decoy table 0x1a06 became data");
        for (Symbol s : p.getSymbolTable().getAllSymbols(true)) {
            check(!s.getName().startsWith("caseD_") && !s.getName().equals("default"),
                "reject: unexpected switch label " + s.getName());
        }
        decompileNoSwitch(p, 0x1900, "reject");
        p.release(this);
    }

    // Coexistence: pre-curated table data is preserved while refs are added.
    private void fixtureCuration() throws Exception {
        ProgramDB p = newProgram("curation");
        long[] targets = { 0x1c20, 0x1c26, 0x1c2c };
        try (var tx = p.openTransaction("bytes")) {
            put(p, 0x1c00, cmpImm5(2, 18));                 // ncases = 3
            put(p, 0x1c02, bcond(0xB, 0x1c40 - 0x1c02));    // bh default
            put(p, 0x1c04, switchI(18));                    // table at 0x1c06
            for (int i = 0; i < 3; i++) {
                put(p, 0x1c06 + 2L * i, u16((int) ((targets[i] - 0x1c06) / 2)));
                putCase(p, targets[i], i + 1, 0x1c50);
            }
            putCase(p, 0x1c40, 0x1f, 0x1c50);
            put(p, 0x1c50, jmpReg(31));
            // manual curation before analysis
            try (var tx2 = p.openTransaction("curate")) {
                p.getListing().createData(a(p, 0x1c06),
                    new ArrayDataType(ShortDataType.dataType, 3, 2));
            }

        }
        analyze(p, 0x1c00);

        Data table = p.getListing().getDefinedDataAt(a(p, 0x1c06));
        check(table != null && table.getNumComponents() == 3,
            "curation: curated table damaged");
        if (table != null) {
            check(((ghidra.program.model.scalar.Scalar) table.getComponent(0).getValue()).getSignedValue() == 13,
                "curation: curated values changed");
        }
        checkCaseChain(p, 0x1c04, targets, "curation");
        boolean entryLinked = false;
        for (Reference ref : p.getReferenceManager().getReferencesFrom(a(p, 0x1c06))) {
            entryLinked |= ref.getReferenceType() == RefType.DATA &&
                ref.getToAddress().getOffset() == targets[0];
        }
        check(entryLinked, "curation: existing table lacks its element-to-case reference");
        decompileAsserts(p, 0x1c00, "curation");
        p.release(this);
    }

    // Variants: index copy (mov rSrc,rIdx), bound carried in a constant
    // register (mov N,rN; cmp rN,rIdx), unsigned halfword table (ld.hu), and
    // the element base taken from the jmp displacement.
    private void fixtureVariants() throws Exception {
        ProgramDB p = newProgram("variants");
        long[] targets = { 0x1e44, 0x1e4a, 0x1e50, 0x1e56 };
        try (var tx = p.openTransaction("bytes")) {
            put(p, 0x1e00, movImm5(3, 7));            // bound value in r7
            put(p, 0x1e02, u16(w0(0x00, 18, 24)));    // mov r18, r24 (index copy)
            put(p, 0x1e04, u16(w0(0x0f, 7, 24)));     // cmp r7, r24
            put(p, 0x1e06, bcond(0xB, 0x1e80 - 0x1e06)); // bh default
            put(p, 0x1e08, shlImm5(1, 24));
            put(p, 0x1e0a, cat(u16(w0(0x3f, 24, 24)),
                u16((((0x1f00 >> 1) & 0x7fff) << 1) | 1))); // ld.hu 0x1f00[r24], r24
            put(p, 0x1e0e, jmpDisp32(0x1e40, 24));    // elbase in the dispatch
            for (int i = 0; i < 4; i++) {
                put(p, 0x1f00 + 2L * i, u16((int) (targets[i] - 0x1e40)));
                putCase(p, targets[i], i + 1, 0x1e90);
            }
            putCase(p, 0x1e80, 0x1f, 0x1e90);
            put(p, 0x1e90, jmpReg(31));
        }
        analyze(p, 0x1e00);

        checkCaseChain(p, 0x1e0e, targets, "variants");
        Data table = p.getListing().getDefinedDataAt(a(p, 0x1f00));
        check(table != null && table.getNumComponents() == 4, "variants: table data wrong");
        if (table != null) {
            Object v = table.getComponent(0).getValue();
            check(v instanceof ghidra.program.model.scalar.Scalar
                && ((ghidra.program.model.scalar.Scalar) v).getUnsignedValue() == 4,
                "variants: unsigned element wrong");
        }
        checkLabel(p, 0x1e44, "caseD_0", "variants");
        decompileAsserts(p, 0x1e00, "variants");
        p.release(this);
    }

    private void fixtureRepeatedCases() throws Exception {
        for (int count : new int[] { 1, 3, 1025 }) {
            ProgramDB p = newProgram("repeated-cases-" + count);
            try {
                long table = 0x200a;
                long target = 0x4000;
                try (var tx = p.openTransaction("bytes")) {
                    put(p, 0x2000, movea(count - 1, 0, 7));
                    put(p, 0x2004, u16(w0(0x0f, 7, 18)));
                    put(p, 0x2006, bcond(0xB, 0x1fe0 - 0x2006));
                    put(p, 0x2008, switchI(18));
                    for (int i = 0; i < count; i++) {
                        put(p, table + 2L * i, u16((int) ((target - table) / 2)));
                    }
                    putCase(p, target, 7, 0x4010);
                    putCase(p, 0x1fe0, 15, 0x4010);
                    put(p, 0x4010, jmpReg(31));
                }
                analyze(p, 0x2000);
                Data data = p.getListing().getDefinedDataAt(a(p, table));
                check(data != null && data.getNumComponents() == count,
                    "repeated cases: table extent lost for " + count + " entries");
                checkCaseChain(p, 0x2008, new long[] { target }, "repeated cases " + count);
                checkBodyContains(p, 0x2000, new long[] { target }, "repeated cases " + count);
            }
            finally {
                p.release(this);
            }
        }
    }

    @Override
    public void run() throws Exception {
        fixtureNativeSwitch();
        fixtureNativeSwitchAddi();
        fixtureNativeSwitchBnh();
        fixtureDirectTable();
        fixtureLoadedRelative();
        fixtureLoadedAbsolute();
        fixtureMaterializedBases();
        fixtureRejects();
        fixtureCuration();
        fixtureVariants();
        fixtureRepeatedCases();

        if (!failures.isEmpty()) {
            throw new IllegalStateException(failures.size() + " switch-analysis failures");
        }
        println("ASSERT v850-switch-analysis: passed");
    }
}
