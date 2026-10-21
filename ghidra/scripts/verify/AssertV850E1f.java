//@author kaikozlov
//@category Verification
// Behavioral fixtures for the legacy V850E1F FPU language
// (v850e1f:LE:32:default), following the contract classification of
// v850_e1f.sinc. Two kinds of checks:
// 1. Fully real p-code paths, asserted directly: decode parity; IEEE
//    754-1985 result VALUES of add/sub/mul/div and conversions (PHO3
//    CPU overview: the FPU is "single precision, according to IEEE
//    754-85 standard"); the documented ECT-mask->TR derivation and the
//    reserved-bit register layouts (R01UH0128ED0730 Rev.7.30
//    pp.104-105 Tables 3-10..3-12).
// 2. Unresolved vendor contracts, asserted ONLY at their explicit
//    opaque boundary: per-instruction EFG update/retention
//    (e1f_status_unresolved), TRFF's EFG->PSW mapping
//    (e1f_trff_unresolved; IDA 9.5 Hex-Rays likewise renders trff as
//    opaque inline asm), float->int overflow/NaN result values
//    (e1f_cvt_range_unresolved), and minf/maxf with a NaN operand
//    (e1f_minmax_nan_unresolved). Following the module's existing
//    stepInterruptControl convention, stepping such an instruction
//    stops at the userop and the p-code before the boundary (the result
//    register write) has committed - so result values are asserted and
//    NO guessed flag/mapping state is ever pinned.
// Emits "ASSERT v850-e1f: passed" and throws on any failure.
import ghidra.app.script.GhidraScript;
import ghidra.app.emulator.EmulatorHelper;
import ghidra.app.util.PseudoDisassembler;
import ghidra.app.util.PseudoInstruction;
import ghidra.program.database.ProgramDB;
import ghidra.program.model.lang.Language;
import ghidra.program.model.lang.LanguageID;
import ghidra.program.model.lang.UnknownInstructionException;
import ghidra.program.util.DefaultLanguageService;
import java.io.ByteArrayInputStream;
import ghidra.program.model.address.Address;

public class AssertV850E1f extends GhidraScript {
    private static final String LANGUAGE_ID = "v850e1f:LE:32:default";

    // E1F Format F field values (IDA nec850 ana.cpp E1F block,
    // ref. U16374EJ1V0UM): reg1 bits 0-4, op 0x3F bits 5-10, reg2 bits
    // 11-15, subopcode bits 16-26, reg3 bits 27-31.
    private static final int DIVF = 0x3E0, SUBF = 0x3E4, ADDF = 0x3E8,
            MULF = 0x3EC, MINF = 0x3F0, MAXF = 0x3F4, CVT_SW = 0x360,
            TRNC_SW = 0x368, CVT_WS = 0x370, STFF = 0x378, TRFF = 0x378,
            STFC = 0x37C, LDFF = 0x37A, LDFC = 0x37E, NEGF = 0x3F8,
            ABSF = 0x3FC;

    // Unresolved-contract intrinsics of v850_e1f.sinc.
    private static final String STATUS_U = "e1f_status_unresolved",
            TRFF_U = "e1f_trff_unresolved",
            CVT_RANGE_U = "e1f_cvt_range_unresolved",
            MINMAX_NAN_U = "e1f_minmax_nan_unresolved";

    private int checked = 0;

    private void fail(String msg) {
        throw new IllegalStateException(msg);
    }

    private static String enc(int subop, int r1, int r2, int r3) {
        int w = (r1 & 0x1f) | (0x3f << 5) | ((r2 & 0x1f) << 11)
                | ((subop & 0x7ff) << 16) | ((r3 & 0x1f) << 27);
        return String.format("%02x%02x%02x%02x", w & 0xff, (w >>> 8) & 0xff,
                (w >>> 16) & 0xff, (w >>> 24) & 0xff);
    }

    private static byte[] bytes(String hex) {
        byte[] out = new byte[hex.length() / 2];
        for (int i = 0; i < out.length; i++) {
            out[i] = (byte) Integer.parseInt(hex.substring(2 * i, 2 * i + 2), 16);
        }
        return out;
    }

    private static int f32(float f) {
        return Float.floatToRawIntBits(f);
    }

    @Override
    public void run() throws Exception {
        Language language;
        try {
            language = DefaultLanguageService.getLanguageService()
                    .getLanguage(new LanguageID(LANGUAGE_ID));
        } catch (Exception e) {
            throw new IllegalStateException(
                    "E1F language " + LANGUAGE_ID + " not registered: " + e);
        }
        ProgramDB program = new ProgramDB("v850-e1f", language,
                language.getDefaultCompilerSpec(), this);
        int tx = program.startTransaction("E1F fixtures");
        try {
            Address base = program.getAddressFactory().getDefaultAddressSpace()
                    .getAddress(0x1000);
            program.getMemory().createInitializedBlock("code", base,
                    new ByteArrayInputStream(new byte[0x1000]), 0x1000, monitor, false);
            decodeParity(program, base);
            execAdd(program, base);
            execSubZeroAndSign(program, base);
            execMulOverflow(program, base);
            execDivZero(program, base);
            execDivInvalidNan(program, base);
            execUnderflowToZero(program, base);
            execInexactExponentGap(program, base);
            execDivExactness(program, base);
            execSubnormalExact(program, base);
            execCvtSwRounding(program, base);
            execCvtOverflowBoundary(program, base);
            execTrncNegIntMin(program, base);
            execCvtWs(program, base);
            execMinMax(program, base);
            execMinMaxNanBoundary(program, base);
            execNegAbs(program, base);
            execTrffBoundary(program, base);
            execTrMaskGating(program, base);
            execTransferLayout(program, base);
            execAliasing(program, base);
        } finally {
            program.endTransaction(tx, false);
            program.release(this);
        }
        println("ASSERT v850-e1f: passed (fixtures=" + checked + ")");
    }

    // ---- decode parity: every E1F mnemonic decodes (IDA encodings) ----
    private void decodeParity(ProgramDB program, Address base) throws Exception {
        String[][] fixtures = {
            {enc(DIVF, 1, 2, 3), "divf.s"}, {enc(SUBF, 1, 2, 3), "subf.s"},
            {enc(ADDF, 1, 2, 3), "addf.s"}, {enc(MULF, 1, 2, 3), "mulf.s"},
            {enc(MINF, 1, 2, 3), "minf.s"}, {enc(MAXF, 1, 2, 3), "maxf.s"},
            {enc(CVT_SW, 0, 2, 3), "cvt.sw"}, {enc(TRNC_SW, 0, 2, 3), "trnc.sw"},
            {enc(CVT_WS, 0, 2, 3), "cvt.ws"}, {enc(NEGF, 0, 2, 3), "negf.s"},
            {enc(ABSF, 0, 2, 3), "absf.s"}, {enc(STFF, 0, 0, 3), "stff"},
            {enc(TRFF, 0, 0, 0), "trff"}, {enc(STFC, 0, 0, 3), "stfc"},
            {enc(LDFF, 0, 2, 0), "ldff"}, {enc(LDFC, 0, 2, 0), "ldfc"},
        };
        PseudoDisassembler decoder = new PseudoDisassembler(program);
        for (String[] fixture : fixtures) {
            Address a = base.add(0x20L * (++checked));
            program.getMemory().setBytes(a, bytes(fixture[0]));
            PseudoInstruction instruction;
            try {
                instruction = decoder.disassemble(a);
            } catch (UnknownInstructionException e) {
                instruction = null;
            }
            if (instruction == null || !fixture[1].equals(instruction.getMnemonicString())) {
                fail("decode: " + fixture[0] + " expected " + fixture[1]
                        + " got " + instruction);
            }
        }
    }

    private EmulatorHelper prepare(ProgramDB program, Address at, String hexBytes,
            String label) throws Exception {
        program.getMemory().setBytes(at, bytes(hexBytes));
        PseudoInstruction instruction = new PseudoDisassembler(program).disassemble(at);
        if (instruction == null) {
            fail(label + ": fixture bytes not decoded");
        }
        EmulatorHelper emu = new EmulatorHelper(program);
        emu.writeRegister("PC", at.getOffset());
        return emu;
    }

    private void requireReg(EmulatorHelper emu, String label, String reg, long expected) {
        long actual = emu.readRegister(reg).longValue() & 0xffffffffL;
        if (actual != (expected & 0xffffffffL)) {
            fail(String.format("%s: %s=0x%x expected=0x%x", label, reg, actual, expected));
        }
    }

    // Direction-only check of selected fields; unselected bits are
    // never pinned.
    private void requireBits(EmulatorHelper emu, String label, String reg,
            long mask, long expected) {
        long actual = emu.readRegister(reg).longValue() & mask;
        if (actual != (expected & mask)) {
            fail(String.format("%s: %s&0x%x=0x%x expected=0x%x", label, reg, mask,
                    actual, expected & mask));
        }
    }

    private void step(EmulatorHelper emu, String label) throws Exception {
        if (!emu.step(monitor)) {
            fail(label + ": emulator step failed: " + emu.getLastError());
        }
    }

    // Opaque unresolved-E1F boundary (same convention as
    // AssertProcessorFixtureSemantics.stepInterruptControl): the step
    // must stop AT the named unresolved-intrinsic, proving the unknown
    // vendor contract is modeled opaquely; the real p-code before the
    // boundary (the result write) has committed and is asserted by the
    // caller afterwards. No guessed flag/mapping state is pinned.
    private void stepOpaque(EmulatorHelper emu, String label, String userop)
            throws Exception {
        try {
            emu.getEmulator().executeInstruction(false, monitor);
        } catch (ghidra.pcode.emulate.UnimplementedCallOtherException expected) {
            if (!expected.getMessage().contains(userop)) {
                throw expected;
            }
            return;
        }
        fail(label + ": expected the unresolved boundary " + userop
                + " to stop emulation");
    }

    private void runOne(ProgramDB program, Address at, String hex, String label,
            String[] regs, long[] values, String boundaryUserop, String outReg,
            long expectedResult) throws Exception {
        EmulatorHelper emu = prepare(program, at, hex, label);
        try {
            for (int i = 0; i < regs.length; i++) {
                emu.writeRegister(regs[i], values[i]);
            }
            stepOpaque(emu, label, boundaryUserop);
            requireReg(emu, label, outReg, expectedResult);
        } finally {
            emu.dispose();
        }
    }

    // addf.s r1, r2, r3: 2.5 + 4.25 = 6.75 exactly (IEEE 754-1985); the
    // result write commits before the unresolved status boundary.
    private void execAdd(ProgramDB program, Address base) throws Exception {
        runOne(program, base.add(0x10), enc(ADDF, 1, 2, 3), "addf",
                new String[]{"r1", "r2"}, new long[]{f32(2.5f), f32(4.25f)},
                STATUS_U, "sp", f32(6.75f));
    }

    // subf.s: x - x = +0 (IEEE) and 1 - 2 = -1; values only, each in a
    // fresh emulator (the status boundary stops each step).
    private void execSubZeroAndSign(ProgramDB program, Address base) throws Exception {
        runOne(program, base.add(0x18), enc(SUBF, 1, 2, 3), "subf-zero",
                new String[]{"r1", "r2"}, new long[]{f32(5.0f), f32(5.0f)},
                STATUS_U, "sp", 0);
        runOne(program, base.add(0x18), enc(SUBF, 1, 2, 3), "subf-neg",
                new String[]{"r1", "r2"}, new long[]{f32(2.0f), f32(1.0f)},
                STATUS_U, "sp", f32(-1.0f));
    }

    // mulf.s: 1e30 * 1e30 overflows to +inf (IEEE 754-1985 default
    // rounding).
    private void execMulOverflow(ProgramDB program, Address base) throws Exception {
        runOne(program, base.add(0x20), enc(MULF, 1, 2, 3), "mulf-ovf",
                new String[]{"r1", "r2"}, new long[]{f32(1e30f), f32(1e30f)},
                STATUS_U, "sp", 0x7f800000L);
    }

    // divf.s: 3 / 0 = +inf (IEEE 754-1985).
    private void execDivZero(ProgramDB program, Address base) throws Exception {
        runOne(program, base.add(0x28), enc(DIVF, 1, 2, 3), "divf-zd",
                new String[]{"r1", "r2"}, new long[]{0, f32(3.0f)},
                STATUS_U, "sp", 0x7f800000L);
    }

    // divf.s: 0 / 0 produces a NaN (payload-agnostic: exponent all
    // ones; the modeled canonical payload is not silicon truth).
    private void execDivInvalidNan(ProgramDB program, Address base) throws Exception {
        EmulatorHelper emu = prepare(program, base.add(0x30),
                enc(DIVF, 1, 2, 3), "divf-nan");
        try {
            emu.writeRegister("r1", 0);
            emu.writeRegister("r2", 0);
            stepOpaque(emu, "divf-nan", STATUS_U);
            long nan = emu.readRegister("sp").longValue() & 0xffffffffL;
            if ((nan >>> 23) != 0xff) {
                fail("divf-nan: result not NaN: " + Long.toHexString(nan));
            }
        } finally {
            emu.dispose();
        }
    }

    // mulf.s: 1e-38 * 1e-30 underflows to +0 (tiny and inexact under
    // every tininess-detection choice of IEEE 754-1985 7.4).
    private void execUnderflowToZero(ProgramDB program, Address base) throws Exception {
        runOne(program, base.add(0x38), enc(MULF, 1, 2, 3), "mulf-ud",
                new String[]{"r1", "r2"}, new long[]{f32(1e-38f), f32(1e-30f)},
                STATUS_U, "sp", 0);
    }

    // addf.s: 1.0 + 2^-60 = 1.0 but is inexact; the perturbation sits
    // below the binary64 guard window, so only the exponent-gap clause
    // of the model detects it (the result VALUE is what is asserted).
    private void execInexactExponentGap(ProgramDB program, Address base) throws Exception {
        runOne(program, base.add(0x40), enc(ADDF, 1, 2, 3), "addf-gap",
                new String[]{"r1", "r2"},
                new long[]{f32((float) Math.pow(2.0, -60)), f32(1.0f)},
                STATUS_U, "sp", f32(1.0f));
    }

    // divf.s: 1/3 and 1/0.5 = 2 (IEEE values).
    private void execDivExactness(ProgramDB program, Address base) throws Exception {
        runOne(program, base.add(0x48), enc(DIVF, 1, 2, 3), "divf-inexact",
                new String[]{"r1", "r2"}, new long[]{f32(3.0f), f32(1.0f)},
                STATUS_U, "sp", f32(1.0f / 3.0f));
        runOne(program, base.add(0x48), enc(DIVF, 1, 2, 3), "divf-exact",
                new String[]{"r1", "r2"}, new long[]{f32(0.5f), f32(1.0f)},
                STATUS_U, "sp", f32(2.0f));
    }

    // addf.s: 2^-149 + 2^-149 = 2^-148, an exact subnormal result
    // (gradual underflow, IEEE 754-1985).
    private void execSubnormalExact(ProgramDB program, Address base) throws Exception {
        runOne(program, base.add(0x50), enc(ADDF, 1, 2, 3), "addf-subn",
                new String[]{"r1", "r2"}, new long[]{1, 1},
                STATUS_U, "sp", 2);
    }

    // cvt.sw rounds to nearest (decode-name convention; every nearest
    // variant maps 1.5 to 2, so the tie direction is not pinned).
    private void execCvtSwRounding(ProgramDB program, Address base) throws Exception {
        runOne(program, base.add(0x58), enc(CVT_SW, 0, 2, 3), "cvt.sw-1.5",
                new String[]{"r2"}, new long[]{f32(1.5f)},
                STATUS_U, "sp", 2);
    }

    // cvt.sw of 3.0e9 overflows INT32_MAX: the conversion routes
    // through the explicit unresolved value intrinsic; nothing about
    // the result or the flag state is asserted (the documented OV
    // condition is only an input to the unresolved status merge).
    private void execCvtOverflowBoundary(ProgramDB program, Address base) throws Exception {
        EmulatorHelper emu = prepare(program, base.add(0x60),
                enc(CVT_SW, 0, 2, 3), "cvt.sw-ov");
        try {
            emu.writeRegister("r2", f32(3.0e9f));
            stepOpaque(emu, "cvt.sw-ov", CVT_RANGE_U);
        } finally {
            emu.dispose();
        }
    }

    // trnc.sw rounds toward zero (decode-name convention):
    // -1.9 -> -1, and exactly -2^31 converts representably.
    private void execTrncNegIntMin(ProgramDB program, Address base) throws Exception {
        runOne(program, base.add(0x68), enc(TRNC_SW, 0, 2, 3), "trnc.sw-1.9",
                new String[]{"r2"}, new long[]{f32(-1.9f)},
                STATUS_U, "sp", -1);
        runOne(program, base.add(0x68), enc(TRNC_SW, 0, 2, 3), "trnc.sw-min",
                new String[]{"r2"}, new long[]{f32(-2147483648.0f)},
                STATUS_U, "sp", 0x80000000L);
    }

    // cvt.ws: 7 -> 7.0f exactly; 0x7ffffff1 needs 32 significant bits
    // and rounds to the nearest binary32.
    private void execCvtWs(ProgramDB program, Address base) throws Exception {
        runOne(program, base.add(0x70), enc(CVT_WS, 0, 2, 3), "cvt.ws-7",
                new String[]{"r2"}, new long[]{7},
                STATUS_U, "sp", f32(7.0f));
        runOne(program, base.add(0x70), enc(CVT_WS, 0, 2, 3), "cvt.ws-round",
                new String[]{"r2"}, new long[]{0x7ffffff1L},
                STATUS_U, "sp", f32((float) 0x7ffffff1L));
    }

    // minf.s/maxf.s numeric select (values only).
    private void execMinMax(ProgramDB program, Address base) throws Exception {
        runOne(program, base.add(0x78), enc(MINF, 1, 2, 3), "minf",
                new String[]{"r1", "r2"}, new long[]{f32(1.5f), f32(2.5f)},
                STATUS_U, "sp", f32(1.5f));
        runOne(program, base.add(0x78), enc(MAXF, 1, 2, 3), "maxf",
                new String[]{"r1", "r2"}, new long[]{f32(1.5f), f32(2.5f)},
                STATUS_U, "sp", f32(2.5f));
    }

    // maxf.s with a quiet-NaN operand routes through the explicit
    // unresolved intrinsic; no result value is asserted.
    private void execMinMaxNanBoundary(ProgramDB program, Address base) throws Exception {
        EmulatorHelper emu = prepare(program, base.add(0x7C),
                enc(MAXF, 1, 2, 3), "maxf-nan");
        try {
            emu.writeRegister("r1", 0x7fc00000L);
            emu.writeRegister("r2", f32(1.0f));
            stepOpaque(emu, "maxf-nan", MINMAX_NAN_U);
        } finally {
            emu.dispose();
        }
    }

    // negf.s/absf.s are pure sign-bit operations on the value; their
    // EFG effect (if any) is unresolved, so values only.
    private void execNegAbs(ProgramDB program, Address base) throws Exception {
        runOne(program, base.add(0x80), enc(NEGF, 0, 2, 3), "negf",
                new String[]{"r2"}, new long[]{f32(2.0f)},
                STATUS_U, "sp", f32(-2.0f));
        runOne(program, base.add(0x80), enc(ABSF, 0, 2, 3), "absf",
                new String[]{"r2"}, new long[]{f32(-2.0f)},
                STATUS_U, "sp", f32(2.0f));
    }

    // trff stops at its unresolved mapping intrinsic. The emulator leaves PSW
    // untouched. This asserts only the opaque boundary.
    private void execTrffBoundary(ProgramDB program, Address base) throws Exception {
        EmulatorHelper emu = prepare(program, base.add(0x84),
                enc(TRFF, 0, 0, 0), "trff");
        try {
            emu.writeRegister("PSW", 0x12345678L);
            stepOpaque(emu, "trff", TRFF_U);
            requireReg(emu, "trff", "PSW", 0x12345678L);
        } finally {
            emu.dispose();
        }
    }

    // ECT mask gating of TR through fully real p-code (PHO3 p.104
    // Table 3-11: TR "summarizes the state of the FPU ... one of the
    // bits 12 to 8 of the ECT register is set"; p.105 Table 3-12): a
    // ZD image loaded into EFG keeps TR clear while ZT is clear, turns
    // TR on once ZT is loaded, and a stored TR bit in the LDFF input is
    // discarded because TR is derived. The cause image is set through
    // LDFF, whose write keeps only the defined register bits.
    private void execTrMaskGating(ProgramDB program, Address base) throws Exception {
        Address at = base.add(0x88);
        program.getMemory().setBytes(at, bytes(enc(LDFC, 0, 6, 0)));
        program.getMemory().setBytes(at.add(4), bytes(enc(LDFF, 0, 5, 0)));
        program.getMemory().setBytes(at.add(8), bytes(enc(LDFC, 0, 6, 0)));
        program.getMemory().setBytes(at.add(12), bytes(enc(LDFC, 0, 6, 0)));
        EmulatorHelper emu = new EmulatorHelper(program);
        try {
            emu.writeRegister("PC", at.getOffset());
            emu.writeRegister("r6", 0);
            step(emu, "trg-ldfc0");     // ECT = 0 (the reset value)
            // ZD image with a TR bit in the input: TR must be recomputed
            // (and with ZT clear, read 0), never stored
            emu.writeRegister("tp", 0x0810);
            emu.writeRegister("PC", at.add(4).getOffset());
            step(emu, "trg-ldff");
            requireBits(emu, "trg-ldff", "EFG", 0x0810, 0x0800);
            emu.writeRegister("r6", 0x0800);                   // ZT
            emu.writeRegister("PC", at.add(8).getOffset());
            step(emu, "trg-zt-on");
            requireBits(emu, "trg-zt-on", "EFG", 0x0810, 0x0810);
            requireReg(emu, "trg-zt-on", "ECT", 0x0800);
            emu.writeRegister("r6", 0);
            emu.writeRegister("PC", at.add(12).getOffset());
            step(emu, "trg-zt-off");
            requireBits(emu, "trg-zt-off", "EFG", 0x0810, 0x0800);
        } finally {
            emu.dispose();
        }
    }

    // Register-layout roundtrips: reserved bits of EFG/ECT are fixed at
    // 0 (PHO3 pp.104-105 diagrams). After an all-ones load through
    // LDFC/LDFF, STFC/STFF can only ever read the defined bit sets.
    private void execTransferLayout(ProgramDB program, Address base) throws Exception {
        Address at = base.add(0x98);
        program.getMemory().setBytes(at, bytes(enc(LDFC, 0, 6, 0)));
        program.getMemory().setBytes(at.add(4), bytes(enc(STFC, 0, 0, 7)));
        program.getMemory().setBytes(at.add(8), bytes(enc(LDFF, 0, 5, 0)));
        program.getMemory().setBytes(at.add(12), bytes(enc(STFF, 0, 0, 7)));
        EmulatorHelper emu = new EmulatorHelper(program);
        try {
            emu.writeRegister("PC", at.getOffset());
            emu.writeRegister("r6", 0xffffffffL);
            step(emu, "layout-ldfc");
            emu.writeRegister("PC", at.add(4).getOffset());
            step(emu, "layout-stfc");
            // reserved ECT bits are permanently 0: only IT..PT can read 1
            requireBits(emu, "layout-stfc", "r7", 0xffffe0ffL, 0);
            emu.writeRegister("PC", at.add(8).getOffset());
            emu.writeRegister("tp", 0xffffffffL);
            step(emu, "layout-ldff");
            emu.writeRegister("PC", at.add(12).getOffset());
            step(emu, "layout-stff");
            // reserved EFG bits are permanently 0: only
            // RO,IV,ZD,VF,UD,PR,TR,OV,S,Z can read 1
            requireBits(emu, "layout-stff", "r7", 0xffffc0e8L, 0);
        } finally {
            emu.dispose();
        }
    }

    // Destination aliasing: reg3 == reg2 and reg3 == reg1 must both
    // read the original source values (asserted on the committed result
    // write, before the status boundary).
    private void execAliasing(ProgramDB program, Address base) throws Exception {
        runOne(program, base.add(0xB0), enc(ADDF, 1, 2, 2), "alias-addf",
                new String[]{"r1", "r2"}, new long[]{f32(2.0f), f32(5.0f)},
                STATUS_U, "r2", f32(7.0f));
        runOne(program, base.add(0xB0), enc(DIVF, 1, 2, 1), "alias-divf",
                new String[]{"r1", "r2"}, new long[]{f32(2.0f), f32(10.0f)},
                STATUS_U, "r1", f32(5.0f));
    }
}
