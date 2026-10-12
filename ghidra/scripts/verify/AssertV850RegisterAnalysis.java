//@author kaikozlov
//@category Verification
// Behavioral fixtures for the V850 register/constant propagation analyzer:
// dynamic CTBP/CALLT recovery, fixed CTBP/GP/TP/EP seeds, CFG-join and
// call-clobber negatives, and the selectable compiler/ABI + callee-save
// models. Uses disposable ProgramDB programs and the real analyzer.
import ghidra.app.cmd.disassemble.DisassembleCommand;
import ghidra.app.cmd.function.CreateFunctionCmd;
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.plugin.core.analysis.AutoAnalysisManager;
import ghidra.app.plugin.core.analysis.OneShotAnalysisCommand;
import ghidra.app.plugin.core.analysis.V850RegisterAnalyzer;
import ghidra.app.script.GhidraScript;
import ghidra.app.util.importer.MessageLog;
import ghidra.framework.options.Options;
import ghidra.program.database.ProgramDB;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressSet;
import ghidra.program.model.address.AddressSetView;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.ArrayDataType;
import ghidra.program.model.data.ByteDataType;
import ghidra.program.model.data.UnionDataType;
import ghidra.program.model.data.DWordDataType;
import ghidra.program.model.data.LongLongDataType;
import ghidra.program.model.data.UnsignedLongLongDataType;
import ghidra.program.model.data.StructureDataType;
import ghidra.program.model.lang.CompilerSpec;
import ghidra.program.model.lang.CompilerSpecID;
import ghidra.program.model.lang.Language;
import ghidra.program.model.lang.LanguageID;
import ghidra.program.model.lang.Register;
import ghidra.program.model.lang.RegisterValue;
import ghidra.program.model.listing.Data;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Program;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.pcode.PcodeOp;
import ghidra.program.model.pcode.Varnode;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.listing.VariableStorage;
import ghidra.program.util.DefaultLanguageService;
import ghidra.program.model.symbol.SourceType;

import java.io.ByteArrayInputStream;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public class AssertV850RegisterAnalysis extends GhidraScript {

    private final List<String> failures = new ArrayList<>();

    private void fail(String msg) {
        failures.add(msg);
        println("FAIL: " + msg);
    }

    // ------------------------------------------------------------------
    // Encodings (derived from the vendored SLEIGH specification)
    // ------------------------------------------------------------------

    private static byte[] halfwords(int... words) {
        byte[] out = new byte[words.length * 2];
        for (int i = 0; i < words.length; i++) {
            out[i * 2] = (byte) (words[i] & 0xff);
            out[i * 2 + 1] = (byte) ((words[i] >> 8) & 0xff);
        }
        return out;
    }

    /** movea imm16, r0, reg  (reg = sext(imm16)) */
    private static byte[] movea(int reg, int imm16) {
        return halfwords((reg << 11) | (0x31 << 5), imm16 & 0xffff);
    }

    /** ldsr reg, ctbp (system register 20) */
    private static byte[] ldsrCtbp(int reg) {
        return halfwords((20 << 11) | (0x3f << 5) | reg, 0x0020);
    }

    /** callt imm6 */
    private static byte[] callt(int imm6) {
        return halfwords(0x0200 | (imm6 & 0x3f));
    }

    /** bne disp9 (positive even disp) */
    private static byte[] bne(int disp) {
        int hw = (((disp >> 4) & 0x1f) << 11) | (0xb << 7) | (((disp >> 1) & 0x7) << 4) | 0xa;
        return halfwords(hw);
    }

    /** jr disp22 (positive) */
    private static byte[] jr(int disp) {
        return halfwords((0x1e << 6) | ((disp >> 16) & 0x3f), disp & 0xffff);
    }

    /** jarl disp22, lp */
    private static byte[] jarlLp(int disp) {
        return halfwords((31 << 11) | (0x1e << 6) | ((disp >> 16) & 0x3f), disp & 0xffff);
    }

    /** jmp [lp] */
    private static byte[] jmpLp() {
        return halfwords(0x007f);
    }

    /** nop */
    private static byte[] nop() {
        return halfwords(0x0000);
    }

    /** sld.w 0[ep], reg */
    private static byte[] sldw0Ep(int reg) {
        return halfwords((reg << 11) | (0x0a << 7));
    }

    /** ld.w disp16[reg1], reg2 (even disp) */
    private static byte[] ldwDisp(int reg1, int reg2, int disp) {
        return halfwords((reg2 << 11) | (0x39 << 5) | reg1, (disp & 0xfffe) | 1);
    }

    // ------------------------------------------------------------------
    // Fixture helpers
    // ------------------------------------------------------------------

    private Address addr(Program program, long offset) {
        return program.getAddressFactory().getDefaultAddressSpace().getAddress(offset);
    }

    private ProgramDB newProgram(Language language, String name) throws Exception {
        return new ProgramDB(name, language, language.getDefaultCompilerSpec(), this);
    }

    private void fixtureBlock(ProgramDB program, String name, long start, int size,
            boolean readOnly, boolean execute) throws Exception {
        int tx = program.startTransaction("block " + name);
        try {
            MemoryBlock block = program.getMemory()
                    .createInitializedBlock(name, addr(program, start),
                        new ByteArrayInputStream(new byte[size]), size, monitor, false);
            if (readOnly) {
                block.setRead(true);
                block.setWrite(false);
            }
            else {
                // createInitializedBlock defaults to read-only permissions in
                // native Ghidra; the fixtures model ordinary writable memory.
                block.setRead(true);
                block.setWrite(true);
            }
            if (execute) {
                block.setExecute(true);
            }
        }
        finally {
            program.endTransaction(tx, true);
        }
    }

    private void writeBytes(ProgramDB program, long start, byte[] bytes) throws Exception {
        int tx = program.startTransaction("bytes");
        try {
            program.getMemory().setBytes(addr(program, start), bytes);
        }
        finally {
            program.endTransaction(tx, true);
        }
    }

    private void writeHalfwords(ProgramDB program, long start, int value) throws Exception {
        writeBytes(program, start, halfwords(value));
    }

    private Function setupFunction(ProgramDB program, long entry) throws Exception {
        int tx = program.startTransaction("function");
        try {
            new DisassembleCommand(addr(program, entry), null, true).applyTo(program, monitor);
            new CreateFunctionCmd(addr(program, entry)).applyTo(program, monitor);
        }
        finally {
            program.endTransaction(tx, true);
        }
        return program.getFunctionManager().getFunctionAt(addr(program, entry));
    }

    private void runAnalyzer(ProgramDB program, Map<String, ?> optionValues,
            AddressSetView set) throws Exception {
        V850RegisterAnalyzer analyzer = new V850RegisterAnalyzer();
        if (!analyzer.canAnalyze(program)) {
            throw new IllegalStateException("V850RegisterAnalyzer.canAnalyze failed");
        }
        int tx = program.startTransaction("analyze");
        try {
            Options options = program.getOptions("Analyzers").getOptions(analyzer.getName());
            analyzer.registerOptions(options, program);
            for (Map.Entry<String, ?> entry : optionValues.entrySet()) {
                if (entry.getValue() instanceof Boolean b) {
                    options.setBoolean(entry.getKey(), b);
                }
                else {
                    options.setString(entry.getKey(), String.valueOf(entry.getValue()));
                }
            }
            analyzer.optionsChanged(options, program);
            new OneShotAnalysisCommand(analyzer, set, new MessageLog()).applyTo(program, monitor);
        }
        finally {
            program.endTransaction(tx, true);
        }
    }

    private boolean hasReference(Program program, long from, long to, String refTypeName) {
        for (Reference reference : program.getReferenceManager()
                .getReferencesFrom(addr(program, from))) {
            if (reference.getToAddress().getOffset() == (to & 0xffffffffL) &&
                reference.getReferenceType().getName().equals(refTypeName)) {
                return true;
            }
        }
        return false;
    }

    private boolean hasAnyReference(Program program, long from, long to) {
        for (Reference reference : program.getReferenceManager()
                .getReferencesFrom(addr(program, from))) {
            if (reference.getToAddress().getOffset() == (to & 0xffffffffL)) {
                return true;
            }
        }
        return false;
    }

    private boolean isUndefinedDataOfSize(Program program, long at, int size) {
        Data data = program.getListing().getDataAt(addr(program, at));
        return data != null && data.getDataType().getName().equals("undefined" + size);
    }

    private boolean decompileUsesEpSeed(ProgramDB program, Function function, String label)
            throws Exception {
        DecompInterface ifc = new DecompInterface();
        try {
            ifc.openProgram(program);
            DecompileResults results = ifc.decompileFunction(function, 60, monitor);
            if (results == null || !results.decompileCompleted() || results.getHighFunction() == null) {
                fail(label + ": decompilation failed: " +
                    (results == null ? "null" : results.getErrorMessage()));
                return false;
            }
            var operations = results.getHighFunction().getPcodeOps();
            while (operations.hasNext()) {
                PcodeOp operation = operations.next();
                for (Varnode input : operation.getInputs()) {
                    if ((input.isConstant() && operation.getOpcode() == PcodeOp.LOAD &&
                         input.getOffset() == 0x5008) ||
                        (input.getAddress().isMemoryAddress() && input.getOffset() == 0x5008) ||
                        (input.isConstant() && operation.getOpcode() == PcodeOp.RETURN &&
                         input.getOffset() == 0x12345678L)) {
                        return true;
                    }
                }
            }
            return false;
        }
        finally {
            ifc.dispose();
        }
    }

    // ------------------------------------------------------------------
    // Tests
    // ------------------------------------------------------------------

    /**
     * Dynamic CTBP proven by a flowed LDSR writer resolves the CALLT table
     * entry (data + READ reference) and the call target (COMPUTED_CALL +
     * function creation).
     */
    private void verifyDynamicCalltRecovery(Language language) throws Exception {
        ProgramDB program = newProgram(language, "dynamic-callt");
        try {
            fixtureBlock(program, "code", 0x1000, 0x100, false, true);
            fixtureBlock(program, "cttable", 0x3000, 0x100, true, false);
            fixtureBlock(program, "targets", 0x3200, 0x40, false, true);

            // caller: r2 = 0x3000; ldsr r2, ctbp; callt 2; jmp [lp]
            writeBytes(program, 0x1000, movea(2, 0x3000));
            writeBytes(program, 0x1004, ldsrCtbp(2));
            writeBytes(program, 0x1008, callt(2));
            writeBytes(program, 0x100A, jmpLp());
            // table entry for callt 2 at 0x3004: halfword offset 0x200 -> 0x3200
            writeHalfwords(program, 0x3004, 0x0200);
            // target body
            writeBytes(program, 0x3200, jmpLp());

            Function caller = setupFunction(program, 0x1000);
            if (caller == null) {
                fail("dynamic-callt: caller function not created during setup");
                return;
            }
            runAnalyzer(program, Map.of(),
                new AddressSet(addr(program, 0x1000), addr(program, 0x100C)));

            String label = "dynamic-callt";
            if (!hasReference(program, 0x1008, 0x3200, "COMPUTED_CALL")) {
                fail(label + ": no COMPUTED_CALL reference from callt to 0x3200");
            }
            if (!hasReference(program, 0x1008, 0x3004, "READ")) {
                fail(label + ": no READ reference from callt to table entry 0x3004");
            }
            if (!isUndefinedDataOfSize(program, 0x3004, 2)) {
                fail(label + ": no undefined2 data at table entry 0x3004");
            }
            Function target = program.getFunctionManager().getFunctionAt(addr(program, 0x3200));
            if (target == null) {
                fail(label + ": no function created at CALLT target 0x3200");
            }
        }
        finally {
            program.release(this);
        }
    }

    /**
     * With no CTBP information on any path (no seed, no LDSR writer) the
     * analyzer must not resolve anything, even though a valid table exists.
     */
    private void verifyUnknownCtbpNegative(Language language) throws Exception {
        ProgramDB program = newProgram(language, "unknown-ctbp");
        try {
            fixtureBlock(program, "code", 0x1000, 0x100, false, true);
            fixtureBlock(program, "cttable", 0x3000, 0x100, true, false);
            fixtureBlock(program, "targets", 0x3200, 0x40, false, true);

            writeBytes(program, 0x1000, callt(2));
            writeBytes(program, 0x1002, jmpLp());
            writeHalfwords(program, 0x3004, 0x0200);
            writeBytes(program, 0x3200, jmpLp());

            Function caller = setupFunction(program, 0x1000);
            if (caller == null) {
                fail("unknown-ctbp: caller function not created during setup");
                return;
            }
            runAnalyzer(program, Map.of(),
                new AddressSet(addr(program, 0x1000), addr(program, 0x1004)));

            String label = "unknown-ctbp";
            if (hasAnyReference(program, 0x1000, 0x3200)) {
                fail(label + ": unexpected reference to target 0x3200 without CTBP knowledge");
            }
            if (hasAnyReference(program, 0x1000, 0x3004)) {
                fail(label + ": unexpected reference to table entry 0x3004");
            }
            if (program.getFunctionManager().getFunctionAt(addr(program, 0x3200)) != null) {
                fail(label + ": unexpected function at 0x3200");
            }
            if (isUndefinedDataOfSize(program, 0x3004, 2)) {
                fail(label + ": unexpected data at table entry 0x3004");
            }
        }
        finally {
            program.release(this);
        }
    }

    /**
     * A fixed CTBP seed option resolves the same callt and records the seed in
     * the program context (usable by the decompiler and later analysis).
     */
    private void verifyFixedCtbpOption(Language language) throws Exception {
        ProgramDB program = newProgram(language, "fixed-ctbp");
        try {
            fixtureBlock(program, "code", 0x1000, 0x100, false, true);
            fixtureBlock(program, "cttable", 0x3000, 0x100, true, false);
            fixtureBlock(program, "targets", 0x3200, 0x40, false, true);

            writeBytes(program, 0x1000, callt(2));
            writeBytes(program, 0x1002, jmpLp());
            writeHalfwords(program, 0x3004, 0x0200);
            writeBytes(program, 0x3200, jmpLp());

            Function caller = setupFunction(program, 0x1000);
            if (caller == null) {
                fail("fixed-ctbp: caller function not created during setup");
                return;
            }
            runAnalyzer(program, Map.of("Fixed CTBP value", "0x3000"),
                new AddressSet(addr(program, 0x1000), addr(program, 0x1004)));

            String label = "fixed-ctbp";
            if (!hasReference(program, 0x1000, 0x3200, "COMPUTED_CALL")) {
                fail(label + ": fixed CTBP seed did not resolve COMPUTED_CALL to 0x3200");
            }
            if (!hasReference(program, 0x1000, 0x3004, "READ")) {
                fail(label + ": fixed CTBP seed did not produce READ reference to 0x3004");
            }
            if (program.getFunctionManager().getFunctionAt(addr(program, 0x3200)) == null) {
                fail(label + ": no function created at 0x3200");
            }
            Register ctbp = program.getRegister("CTBP");
            RegisterValue seeded =
                program.getProgramContext().getRegisterValue(ctbp, addr(program, 0x1000));
            if (seeded == null || seeded.getUnsignedValue().longValue() != 0x3000L) {
                fail(label + ": program context CTBP not seeded at function entry");
            }
        }
        finally {
            program.release(this);
        }
    }

    /**
     * A path that bypasses the CTBP writer makes the join unknown, even when
     * another path reaches the same CALLT with a constant base.
     */
    private void verifyConditionalJoinNegative(Language language) throws Exception {
        ProgramDB program = newProgram(language, "join-negative");
        try {
            fixtureBlock(program, "code", 0x1000, 0x100, false, true);
            fixtureBlock(program, "cttable", 0x3000, 0x100, true, false);
            fixtureBlock(program, "targets", 0x3200, 0x40, false, true);

            writeBytes(program, 0x1000, bne(6));           // taken -> 0x1006
            writeBytes(program, 0x1002, jr(0x0E));         // fall-through path -> 0x1010
            writeBytes(program, 0x1006, movea(2, 0x3000)); // conditional setup
            writeBytes(program, 0x100A, ldsrCtbp(2));
            writeBytes(program, 0x100E, nop());
            writeBytes(program, 0x1010, callt(0));
            writeBytes(program, 0x1012, jmpLp());
            writeHalfwords(program, 0x3000, 0x0200);
            writeBytes(program, 0x3200, jmpLp());

            Function caller = setupFunction(program, 0x1000);
            if (caller == null) {
                fail("join-negative: caller function not created during setup");
                return;
            }
            runAnalyzer(program, Map.of(),
                new AddressSet(addr(program, 0x1000), addr(program, 0x1014)));

            String label = "join-negative";
            if (hasAnyReference(program, 0x1010, 0x3200)) {
                fail(label + ": callt resolved across an unproven conditional CTBP setup");
            }
            if (hasAnyReference(program, 0x1010, 0x3000)) {
                fail(label + ": table entry referenced across an unproven conditional setup");
            }
            if (program.getFunctionManager().getFunctionAt(addr(program, 0x3200)) != null) {
                fail(label + ": unexpected function at 0x3200");
            }
        }
        finally {
            program.release(this);
        }
    }

    private void verifyConditionalWriters(Language language, boolean agree) throws Exception {
        String label = agree ? "agreeing-ctbp-writers" : "conflicting-ctbp-writers";
        ProgramDB program = newProgram(language, label);
        try {
            fixtureBlock(program, "code", 0x1000, 0x100, true, true);
            fixtureBlock(program, "tables", 0x3000, 0x200, true, false);
            fixtureBlock(program, "targets", 0x3200, 0x100, true, true);
            writeBytes(program, 0x1000, bne(0x0e));
            writeBytes(program, 0x1002, movea(2, 0x3000));
            writeBytes(program, 0x1006, ldsrCtbp(2));
            writeBytes(program, 0x100a, jr(0x0c));
            writeBytes(program, 0x100e, movea(2, agree ? 0x3000 : 0x3100));
            writeBytes(program, 0x1012, ldsrCtbp(2));
            writeBytes(program, 0x1016, callt(0));
            writeBytes(program, 0x1018, jmpLp());
            writeHalfwords(program, 0x3000, 0x0200);
            writeHalfwords(program, 0x3100, 0x0120);
            writeBytes(program, 0x3200, jmpLp());
            writeBytes(program, 0x3220, jmpLp());
            setupFunction(program, 0x1000);
            runAnalyzer(program, Map.of(),
                new AddressSet(addr(program, 0x1000), addr(program, 0x1019)));
            if (agree) {
                if (!hasReference(program, 0x1016, 0x3200, "COMPUTED_CALL") ||
                    !hasReference(program, 0x1016, 0x3000, "READ")) {
                    fail(label + ": equal CTBP values failed to resolve at the join");
                }
            }
            else {
                for (long target : new long[]{0x3000, 0x3100, 0x3200, 0x3220}) {
                    if (hasAnyReference(program, 0x1016, target)) {
                        fail(label + ": conflicting CTBP values produced a reference");
                    }
                }
            }
        }
        finally {
            program.release(this);
        }
    }

    /**
     * Call clobbering and the exact callee-save policy, observed through
     * references and decompiler folding on the same fixture (caller sets r6,
     * calls, then loads through ep, r6 and gp):
     *
     *   compiler default: ep volatile (no ep ref), gp preserved (gp ref);
     *   policy "ep":      ep preserved (ep ref + folded seed), and gp is
     *                     among the three registers FORCED volatile, so the
     *                     gp ref disappears;
     *   policy "none":    all of ep/gp/tp/r2 volatile, neither ref appears.
     */
    private void verifyCallClobberAndPolicy(Language language) throws Exception {
        Map<String, Object> defaults = new LinkedHashMap<>();
        defaults.put("Fixed EP value", "0x5008");
        defaults.put("Fixed GP value", "0x5000");
        verifyClobberProgram(language, "clobber-default", defaults, false, true, false);
        verifyClobberProgram(language, "indirect-default", defaults, false, true, true);

        Map<String, Object> epPolicy = new LinkedHashMap<>();
        epPolicy.put("Fixed EP value", "0x5008");
        epPolicy.put("Fixed GP value", "0x5000");
        epPolicy.put("Callee-save policy registers", "ep");
        verifyClobberProgram(language, "clobber-policy-ep", epPolicy, true, false, false);
        verifyClobberProgram(language, "indirect-policy-ep", epPolicy, true, false, true);

        Map<String, Object> nonePolicy = new LinkedHashMap<>();
        nonePolicy.put("Fixed EP value", "0x5008");
        nonePolicy.put("Fixed GP value", "0x5000");
        nonePolicy.put("Callee-save policy registers", "none");
        verifyClobberProgram(language, "clobber-policy-none", nonePolicy, false, false, false);
        verifyClobberProgram(language, "indirect-policy-none", nonePolicy, false, false, true);
    }


    private void verifyClobberProgram(Language language, String label,
            Map<String, Object> options, boolean epPreserved, boolean gpPreserved, boolean indirect)
            throws Exception {
        ProgramDB program = newProgram(language, label);
        try {
            fixtureBlock(program, "caller", 0x1ffe, 0x102, false, true);
            fixtureBlock(program, "callee", 0x2100, 0x40, false, true);
            fixtureBlock(program, "data", 0x5000, 0x40, true, false);
            writeBytes(program, 0x5008, halfwords(0x5678, 0x1234));

            writeBytes(program, 0x1ffe, halfwords((20 << 11) | 31)); // mov lp,r20
            writeBytes(program, 0x2000, movea(6, 0x5000));  // r6 = 0x5000
            writeBytes(program, 0x2004, indirect ?
                halfwords(0xc7e9, 0xf960) : jarlLp(0xFC)); // unknown [r9] or direct 0x2100
            writeBytes(program, 0x2008, sldw0Ep(7));        // r7 = [ep]
            writeBytes(program, 0x200A, ldwDisp(6, 8, 0));  // r8 = [r6] (clobbered r6)
            writeBytes(program, 0x200E, ldwDisp(4, 9, 0x10)); // r9 = 0x10[gp]
            writeBytes(program, 0x2012, halfwords((10 << 11) | 7)); // mov r7,r10: return EP load
            writeBytes(program, 0x2014, halfwords((31 << 11) | 20)); // mov r20,lp
            writeBytes(program, 0x2016, jmpLp());
            writeBytes(program, 0x2100, jmpLp());           // callee: preserves what it touches

            Function caller = setupFunction(program, 0x1ffe);
            Function callee = indirect ? null : setupFunction(program, 0x2100);
            if (caller == null || (!indirect && callee == null)) {
                fail(label + ": functions not created during setup");
                return;
            }
            int profileTx = program.startTransaction("target-profile GP");
            try {
                program.getProgramContext().setRegisterValue(addr(program, 0x1ffe),
                    addr(program, 0x2018), new RegisterValue(program.getRegister("gp"),
                        java.math.BigInteger.valueOf(0x5000)));
            }
            finally {
                program.endTransaction(profileTx, true);
            }
            AddressSet both = new AddressSet(addr(program, 0x1ffe), addr(program, 0x2018));
            runAnalyzer(program, options, both);

            if (epPreserved) {
                if (!hasReference(program, 0x2008, 0x5008, "READ")) {
                    fail(label + ": preserved ep did not yield READ reference to 0x5008");
                }
                if (!isUndefinedDataOfSize(program, 0x5008, 4)) {
                    fail(label + ": no undefined4 data at 0x5008");
                }
                if (!decompileUsesEpSeed(program, caller, label)) {
                    fail(label + ": decompiler did not fold the preserved EP seed 0x5008");
                }
            }
            else {
                if (hasAnyReference(program, 0x2008, 0x5008)) {
                    fail(label + ": ep survived a call under the default (volatile ep) convention");
                }
                if (decompileUsesEpSeed(program, caller, label)) {
                    fail(label + ": decompiler folded EP seed even though the call clobbers ep");
                }
            }
            if (gpPreserved) {
                if (!hasReference(program, 0x200E, 0x5010, "READ")) {
                    fail(label + ": preserved gp did not yield READ reference to 0x5010");
                }
            }
            else if (hasAnyReference(program, 0x200E, 0x5010)) {
                fail(label +
                    ": gp survived a call although the policy forces it volatile (seed was set)");
            }
            // r6 is an argument register under every model: killed by the call.
            if (hasAnyReference(program, 0x200A, 0x5000)) {
                fail(label + ": post-call load through clobbered r6 produced a reference");
            }
            if (options.containsKey("Callee-save policy registers")) {
                Map<String, Object> restored = new LinkedHashMap<>(options);
                restored.put("Callee-save policy registers", "");
                runAnalyzer(program, restored, both);
                if (decompileUsesEpSeed(program, caller, label + "-restored")) {
                    fail(label + ": clearing the policy failed to restore volatile EP");
                }
            }
        }
        finally {
            program.release(this);
        }
    }

    /**
     * Fixed GP/TP seeds make GP/TP-relative loads resolve to concrete data
     * references through the standard propagation path.
     */
    private void verifyGpTpSeeds(Language language) throws Exception {
        ProgramDB program = newProgram(language, "gp-tp-seeds");
        try {
            fixtureBlock(program, "code", 0x1000, 0x40, false, true);
            fixtureBlock(program, "gdata", 0x8000, 0x100, true, false);
            fixtureBlock(program, "tdata", 0x9000, 0x100, true, false);

            writeBytes(program, 0x1000, ldwDisp(4, 7, 0x10)); // ld.w 0x10[gp], r7
            writeBytes(program, 0x1004, ldwDisp(5, 8, 0x20)); // ld.w 0x20[tp], r8
            writeBytes(program, 0x1008, jmpLp());

            Function caller = setupFunction(program, 0x1000);
            if (caller == null) {
                fail("gp-tp-seeds: function not created during setup");
                return;
            }
            Map<String, Object> options = new LinkedHashMap<>();
            options.put("Fixed GP value", "0x8000");
            options.put("Fixed TP value", "0x9000");
            runAnalyzer(program, options, new AddressSet(addr(program, 0x1000), addr(program, 0x100A)));

            String label = "gp-tp-seeds";
            if (!hasReference(program, 0x1000, 0x8010, "READ")) {
                fail(label + ": GP seed did not resolve ld.w 0x10[gp] to 0x8010");
            }
            if (!hasReference(program, 0x1004, 0x9020, "READ")) {
                fail(label + ": TP seed did not resolve ld.w 0x20[tp] to 0x9020");
            }
        }
        finally {
            program.release(this);
        }
    }

    /**
     * A halfword table entry of zero is a legal relative offset: the target
     * is the CTBP base itself. With the base in executable memory the callt
     * must resolve (COMPUTED_CALL, function) — zero entries are not treated
     * as empty slots.
     */
    private void verifyZeroOffsetCallt(Language language) throws Exception {
        ProgramDB program = newProgram(language, "zero-offset-callt");
        try {
            fixtureBlock(program, "code", 0x1000, 0x100, false, true);
            // CTBP base lives in executable code flash: the base itself is a
            // real function, the table word for imm 2 follows it.
            fixtureBlock(program, "ctcode", 0x3300, 0x100, false, true);

            writeBytes(program, 0x1000, movea(2, 0x3300));
            writeBytes(program, 0x1004, ldsrCtbp(2));
            writeBytes(program, 0x1008, callt(2));
            writeBytes(program, 0x100A, jmpLp());
            writeBytes(program, 0x3300, jmpLp());  // target = CTBP + 0
            writeHalfwords(program, 0x3304, 0x0000);

            Function caller = setupFunction(program, 0x1000);
            if (caller == null) {
                fail("zero-offset-callt: caller function not created during setup");
                return;
            }
            runAnalyzer(program, Map.of(),
                new AddressSet(addr(program, 0x1000), addr(program, 0x100C)));

            String label = "zero-offset-callt";
            if (!hasReference(program, 0x1008, 0x3300, "COMPUTED_CALL")) {
                fail(label + ": zero entry did not resolve to the CTBP base 0x3300");
            }
            if (!hasReference(program, 0x1008, 0x3304, "READ")) {
                fail(label + ": no READ reference from callt to table entry 0x3304");
            }
            if (!isUndefinedDataOfSize(program, 0x3304, 2)) {
                fail(label + ": no undefined2 data at table entry 0x3304");
            }
            if (program.getFunctionManager().getFunctionAt(addr(program, 0x3300)) == null) {
                fail(label + ": no function created at CTBP base 0x3300");
            }
        }
        finally {
            program.release(this);
        }
    }

    /**
     * A CALLT table in writable memory is untrusted when the analyzer option
     * "Trust values read from writable memory" is disabled: no COMPUTED_CALL
     * reference and no function are produced, even though the entry looks
     * valid.
     */
    private void verifyWritableTableNegative(Language language) throws Exception {
        ProgramDB program = newProgram(language, "writable-table-negative");
        try {
            fixtureBlock(program, "code", 0x1000, 0x100, false, true);
            // initialized read+write block (fixtureBlock !readOnly sets write;
            // native createInitializedBlock alone stays read-only)
            fixtureBlock(program, "cttable", 0x3000, 0x100, false, false);
            fixtureBlock(program, "targets", 0x3200, 0x40, false, true);

            writeBytes(program, 0x1000, movea(2, 0x3000));
            writeBytes(program, 0x1004, ldsrCtbp(2));
            writeBytes(program, 0x1008, callt(2));
            writeBytes(program, 0x100A, jmpLp());
            writeHalfwords(program, 0x3004, 0x0200); // -> 0x3200
            writeBytes(program, 0x3200, jmpLp());

            Function caller = setupFunction(program, 0x1000);
            if (caller == null) {
                fail("writable-table-negative: caller function not created during setup");
                return;
            }
            runAnalyzer(program, Map.of("Trust values read from writable memory", Boolean.FALSE),
                new AddressSet(addr(program, 0x1000), addr(program, 0x100C)));

            String label = "writable-table-negative";
            if (hasAnyReference(program, 0x1008, 0x3200)) {
                fail(label + ": untrusted writable table produced a reference to 0x3200");
            }
            if (program.getFunctionManager().getFunctionAt(addr(program, 0x3200)) != null) {
                fail(label + ": untrusted writable table produced a function at 0x3200");
            }
        }
        finally {
            program.release(this);
        }
    }

    /**
     * Fixed-seed option changes take effect across reruns: seeding GP makes
     * the program context carry the value at the entry and resolves the
     * GP-relative load; rerunning with the option blank must clear the seeded
     * context value instead of retaining it.
     */
    private void verifySeedRerunChange(Language language) throws Exception {
        ProgramDB program = newProgram(language, "seed-rerun-change");
        try {
            fixtureBlock(program, "code", 0x1000, 0x40, false, true);
            fixtureBlock(program, "gdata", 0x8000, 0x100, true, false);

            writeBytes(program, 0x1000, ldwDisp(4, 7, 0x10)); // ld.w 0x10[gp], r7
            writeBytes(program, 0x1004, jmpLp());

            Function caller = setupFunction(program, 0x1000);
            if (caller == null) {
                fail("seed-rerun-change: function not created during setup");
                return;
            }
            AddressSet set = new AddressSet(addr(program, 0x1000), addr(program, 0x1006));
            runAnalyzer(program, Map.of("Fixed GP value", "0x8000"), set);

            String label = "seed-rerun-change";
            Register gp = program.getRegister("gp");
            RegisterValue seeded = program.getProgramContext().getRegisterValue(gp,
                addr(program, 0x1000));
            if (seeded == null || seeded.getUnsignedValue().longValue() != 0x8000L) {
                fail(label + ": GP seed not recorded in program context (got " + seeded + ")");
            }
            if (!hasReference(program, 0x1000, 0x8010, "READ")) {
                fail(label + ": GP seed did not resolve ld.w 0x10[gp] to 0x8010");
            }

            runAnalyzer(program, Map.of("Fixed GP value", ""), set);
            if (program.getProgramContext().getRegisterValue(gp, addr(program, 0x1000)) != null) {
                fail(label + ": blank Fixed GP value retained the stale seeded context");
            }

            // A target profile's context survives the default option and is
            // restored after an explicit temporary override.
            int tx = program.startTransaction("profile GP context");
            try {
                program.getProgramContext().setRegisterValue(addr(program, 0x1000),
                    addr(program, 0x1006), new RegisterValue(gp, java.math.BigInteger.valueOf(0x8080)));
            }
            finally {
                program.endTransaction(tx, true);
            }
            runAnalyzer(program, Map.of(), set);
            if (!hasReference(program, 0x1000, 0x8090, "READ")) {
                fail(label + ": default option erased the target profile's GP context");
            }
            runAnalyzer(program, Map.of("Fixed GP value", "0x8000"), set);
            runAnalyzer(program, Map.of("Fixed GP value", ""), set);
            RegisterValue restored = program.getProgramContext().getRegisterValue(gp,
                addr(program, 0x1000));
            if (restored == null || restored.getUnsignedValue().longValue() != 0x8080L) {
                fail(label + ": clearing the override did not restore the target profile's GP");
            }
        }
        finally {
            program.release(this);
        }
    }

    /**
     * Compiler/ABI model behavior: the selectable compiler entries (default
     * = GHS MULTI, gcc = old-GCC ABI, ccrh = CC-RH) differ in observable
     * ABI behavior — CC-RH preserves ep by default while GHS/GCC treat it
     * as volatile, and GCC returns 8-byte aggregates in r10:r11 while
     * GHS/CC-RH use a hidden return pointer in r6.
     */
    private void verifyCompilerSpecs(Language language) throws Exception {
        ProgramDB program = newProgram(language, "cspec-models");
        try {
            Map<String, CompilerSpec> specs = new LinkedHashMap<>();
            for (String id : new String[] { "default", "gcc", "ccrh" }) {
                specs.put(id, language.getCompilerSpecByID(new CompilerSpecID(id)));
            }
            StructureDataType struct8 = new StructureDataType("agg8", 0);
            struct8.add(new DWordDataType());
            struct8.add(new DWordDataType());

            VariableStorage gccRet =
                specs.get("gcc").getDefaultCallingConvention().getReturnLocation(struct8, program);
            // Native 12.1.4 merges the adjacent r10/r11 join pieces into the
            // formal 8-byte register r10r11; the storage is the same r10:r11
            // pair the ABI specifies.
            if (gccRet == null || !gccRet.isValid() || gccRet.getVarnodes().length != 1 ||
                gccRet.getVarnodes()[0].getSize() != 8 ||
                !"r10r11".equals(registerName(program, gccRet.getVarnodes()[0]))) {
                fail("cspec-models: GCC 8-byte aggregate return is not r10:r11 (got " + gccRet + ")");
            }
            for (String id : new String[] { "default", "ccrh" }) {
                VariableStorage[] locations = specs.get(id).getDefaultCallingConvention()
                    .getStorageLocations(program, new DataType[] { struct8, DWordDataType.dataType },
                        true);
                if (locations.length != 3 || !locations[1].isAutoStorage() ||
                    !"r6".equals(registerName(program, locations[1].getVarnodes()[0])) ||
                    !"r7".equals(registerName(program, locations[2].getVarnodes()[0]))) {
                    fail("cspec-models: " + id +
                        " hidden return buffer must precede the integer argument in r6/r7");
                }
                if (!locations[0].isVoidStorage()) {
                    fail("cspec-models: " + id + " aggregate return must be void, not pointer echo");
                }
            }
            for (String id : new String[] { "default", "gcc", "ccrh" }) {
                // 8-byte scalars: default (GHS) and gcc take the even-aligned
                // r8:r9 pair (native 12.1.4 merges it into the formal r8r9
                // register), CC-RH takes the next consecutive registers. The
                // unsigned long long covers GHS's separate uint alignment
                // rule: datatype filters split by signedness in Ghidra.
                for (DataType wide : new DataType[] { LongLongDataType.dataType,
                    UnsignedLongLongDataType.dataType }) {
                    VariableStorage[] locations = specs.get(id).getDefaultCallingConvention()
                        .getStorageLocations(program, new DataType[] { DWordDataType.dataType,
                            DWordDataType.dataType, wide }, true);
                    Varnode[] pair = locations[2].getVarnodes();
                    boolean aligned = id.equals("default") || id.equals("gcc");
                    boolean ok = aligned
                        ? pair.length == 1 && pair[0].getSize() == 8 &&
                            "r8r9".equals(registerName(program, pair[0]))
                        : pair.length == 2 && "r8".equals(registerName(program, pair[0])) &&
                            "r7".equals(registerName(program, pair[1]));
                    if (!ok) {
                        fail("cspec-models: " + id + " " + wide.getName() +
                            " argument allocation is wrong (got " + locations[2] + ")");
                    }
                }
            }
        }
        finally {
            program.release(this);
        }
    }
    private void verifyGccSmallAggregateReturns(Language language) throws Exception {
        ProgramDB program = new ProgramDB("gcc-small-aggregate-returns", language,
            language.getCompilerSpecByID(new CompilerSpecID("gcc")), this);
        try {
            fixtureBlock(program, "code", 0x1000, 0x100, false, true);
            StructureDataType chars = new StructureDataType("two_chars", 0);
            chars.add(ByteDataType.dataType);
            chars.add(ByteDataType.dataType);
            StructureDataType intChar = new StructureDataType("int_char", 0);
            intChar.add(DWordDataType.dataType);
            intChar.add(ByteDataType.dataType);
            StructureDataType nested = new StructureDataType("nested_array", 0);
            nested.add(new ArrayDataType(ByteDataType.dataType, 2, 1));
            StructureDataType single = new StructureDataType("single_char", 0);
            single.add(ByteDataType.dataType);
            StructureDataType padded = new StructureDataType("leading_padding", 4);
            padded.replaceAtOffset(1, ByteDataType.dataType, 1, "value", null);
            UnionDataType union = new UnionDataType("small_union");
            union.add(ByteDataType.dataType);
            union.add(LongLongDataType.dataType);
            DataType[] types = { chars, intChar, nested, single, union, padded };
            boolean[] indirect = { true, false, true, false, false, true };
            List<Function> functions = new ArrayList<>();
            for (int index = 0; index < types.length; index++) {
                long entry = 0x1000 + index * 0x20;
                writeBytes(program, entry, jmpLp());
                Function function = setupFunction(program, entry);
                int tx = program.startTransaction("typed compiler contract");
                try {
                    function.setReturnType(types[index], SourceType.USER_DEFINED);
                    function.replaceParameters(Function.FunctionUpdateType.DYNAMIC_STORAGE_FORMAL_PARAMS,
                        true, SourceType.USER_DEFINED,
                        new ParameterImpl("argument", DWordDataType.dataType, program));
                }
                finally {
                    program.endTransaction(tx, true);
                }
                functions.add(function);
            }
            AddressSet code = new AddressSet(addr(program, 0x1000), addr(program, 0x10ff));
            runAnalyzer(program, Map.of(), code);
            for (int index = 0; index < functions.size(); index++) {
                Function function = functions.get(index);
                boolean hidden = function.getAutoParameterCount() == 1;
                if (hidden != indirect[index]) {
                    fail("gcc-small-aggregate: hidden buffer disagrees with " + types[index].getName());
                    continue;
                }
                int argumentOrdinal = indirect[index] ? 1 : 0;
                String expectedArgument = indirect[index] ? "r7" : "r6";
                if (!expectedArgument.equals(registerName(program,
                        function.getParameter(argumentOrdinal).getVariableStorage().getVarnodes()[0]))) {
                    fail("gcc-small-aggregate: wrong ordinary argument after " + types[index].getName());
                }
                if (indirect[index] && (!"r6".equals(registerName(program,
                        function.getParameter(0).getVariableStorage().getVarnodes()[0])) ||
                    !function.getReturn().getVariableStorage().isForcedIndirect() ||
                    !"r10".equals(registerName(program,
                        function.getReturn().getVariableStorage().getVarnodes()[0])))) {
                    fail("gcc-small-aggregate: buffer must enter r6 and return through r10");
                }
            }
            // A signature change must remove the old indirect-return contract.
            Function changed = functions.get(0);
            int tx = program.startTransaction("return layout change");
            try {
                changed.setReturnType(single, SourceType.USER_DEFINED);
            }
            finally {
                program.endTransaction(tx, true);
            }
            AutoAnalysisManager manager = AutoAnalysisManager.getAnalysisManager(program);
            manager.functionSignatureChanged(changed.getEntryPoint());
            // startAnalysis runs the queued analysis tasks on this thread but
            // does not open a transaction; the caller owns it (the same
            // contract headless analysis and the GUI background command use).
            int analysisTx = program.startTransaction("re-analyze changed signature");
            try {
                manager.startAnalysis(monitor, false);
            }
            finally {
                program.endTransaction(analysisTx, true);
            }
            if (changed.getAutoParameterCount() != 0 ||
                !"r6".equals(registerName(program,
                    changed.getParameter(0).getVariableStorage().getVarnodes()[0]))) {
                fail("gcc-small-aggregate: changed return layout retained an obsolete hidden buffer");
            }
        }
        finally {
            program.release(this);
        }
    }



    private String registerName(Program program, Varnode varnode) {
        Register register =
            program.getLanguage().getRegister(varnode.getAddress(), varnode.getSize());
        return register == null ? null : register.getName();
    }

    // ------------------------------------------------------------------

    @Override
    public void run() throws Exception {
        LanguageID languageId = new LanguageID("v850e3:LE:32:default");
        Language language = DefaultLanguageService.getLanguageService().getLanguage(languageId);
        if (language == null) {
            throw new IllegalStateException("v850e3 language not installed");
        }
        int before = failures.size();
        verifyCompilerSpecs(language);
        verifyGccSmallAggregateReturns(language);
        verifyDynamicCalltRecovery(language);
        verifyUnknownCtbpNegative(language);
        verifyZeroOffsetCallt(language);
        verifyWritableTableNegative(language);
        verifyFixedCtbpOption(language);
        verifySeedRerunChange(language);
        verifyConditionalJoinNegative(language);
        verifyConditionalWriters(language, true);
        verifyConditionalWriters(language, false);
        verifyCallClobberAndPolicy(language);
        verifyGpTpSeeds(language);
        int count = failures.size() - before;
        if (count > 0) {
            throw new IllegalStateException(
                count + " v850 register-analysis failures: " + String.join("; ", failures));
        }
        println("ASSERT v850-register-analysis: passed");
    }
}
