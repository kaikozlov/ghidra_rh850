//@author kaikozlov
//@category Verification
// Behavioral fixtures for the broad RH850 language (v850e3x): decode-parity
// byte fixtures taken from the installed IDA oracle census
// (build/out/ida-v850-census.json) plus derived encodings, and executed
// p-code dataflow checks (registers/memory through the emulator).
// SIMD fixtures follow R01UH0770EJ0121 3.2.6 (FXU exception model, Tables
// 3.121-3.126) and R01US0209EJ0220 chapter 2.5 [Operation] blocks.
// Emits "ASSERT v850-extended-isa: passed" and throws on any failure.
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
import java.math.BigInteger;

public class AssertV850ExtendedIsa extends GhidraScript {
    private static final String LANGUAGE_ID = "v850e3x:LE:32:default";

    // PSW.CU1 (bit 17): every FXU instruction and selID-10 register access
    // requires it (R01UH0770 Tables 3.2/3.3/3.14).
    private static final long PSW_CU1 = 0x00020000L;

    // Decode-parity corpus: hex bytes -> expected mnemonic.
    private static final String[][] DECODE = {
        // clip + link/conditional + MP bursts (census + binutils encodings)
        {"e0070800", "clip.b"}, {"e0070a00", "clip.bu"},
        {"e0070c00", "clip.h"}, {"e0070e00", "clip.hu"},
        {"e0077403", "ldl.hu"}, {"e0077203", "stc.b"}, {"e0077603", "stc.h"},
        {"e0076601", "ldm.mp"}, {"e0076401", "stm.mp"},
        {"e15f6011", "dbpush"},
        // extended system registers / virtualization / debug / TLB
        {"e0073000", "ldtc.sr"}, {"e0075000", "sttc.sr"},
        {"e0073200", "ldtc.gr"}, {"e0075200", "sttc.gr"},
        {"e0073208", "ldtc.vr"}, {"e0075208", "sttc.vr"},
        {"e00732f8", "ldtc.pc"}, {"e00752f8", "sttc.pc"},
        {"e0073400", "ldvc.sr"}, {"e0075400", "stvc.sr"},
        {"e3071001", "hvtrap"},
        {"e1476011", "pushsp"}, {"e1676011", "popsp"},
        {"e5373000", "ldtc.sr"}, {"e22f5018", "sttc.sr"},
        {"e5373400", "ldvc.sr"}, {"e22f5400", "stvc.sr"},
        {"e5373200", "ldtc.gr"}, {"e22f5200", "sttc.gr"},
        {"e5373208", "ldtc.vr"}, {"e22f5208", "sttc.vr"},
        {"e53732f8", "ldtc.pc"}, {"e02f52f8", "sttc.pc"}, {"e0073201", "est"}, {"e0073401", "dst"},
        {"e0074601", "dbret"}, {"e0076081", "resbank"},
        {"40f8", "dbtrap"}, {"40e0", "dbhvtrap"},
        {"40e8", "dbcp"}, {"40f0", "rmtrap"},
        // derived TLB/hypervisor/debug-tag/breakpoint encodings
        {"e0876089", "tlbai"}, {"e0876081", "tlbvi"}, {"e08760c1", "tlbs"},
        {"e08760e1", "tlbw"}, {"e08760e9", "tlbr"},
        {"e0d76041", "hvcall"}, {"e0cf6001", "dbtag"},
        {"ffffffff", "breakpoint"},
        // S4 SIMD FPU: 3-operand arithmetic
        {"e007a405", "addf.s4"}, {"e007a605", "subf.s4"},
        {"e007a805", "mulf.s4"}, {"e007ae05", "divf.s4"},
        {"e007aa05", "maxf.s4"}, {"e007ac05", "minf.s4"},
        {"e007b405", "addrf.s4"}, {"e007b605", "subrf.s4"},
        {"e007b805", "mulrf.s4"}, {"e007ba05", "maxrf.s4"},
        {"e007bc05", "minrf.s4"},
        {"e007c405", "addxf.s4"}, {"e007c605", "subxf.s4"},
        {"e007c805", "mulxf.s4"},
        {"e007d005", "addsubf.s4"}, {"e007d205", "subaddf.s4"},
        {"e007d805", "addsubnf.s4"}, {"e007da05", "subaddnf.s4"},
        {"e007dc05", "addsubnxf.s4"}, {"e007d405", "addsubxf.s4"},
        {"e007de05", "subaddnxf.s4"},
        {"e007c004", "fmaf.s4"}, {"e007c204", "fmsf.s4"},
        {"e007c404", "fnmaf.s4"}, {"e007c604", "fnmsf.s4"},
        {"e0078005", "cmpf.s4"},
        // S4 SIMD FPU: 2-operand conversions/unary (sub-op in hw1 bits 4-0)
        {"e007a005", "roundf.sw4"}, {"e107a005", "roundf.suw4"},
        {"e207a005", "trncf.sw4"}, {"e307a005", "trncf.suw4"},
        {"e407a005", "ceilf.sw4"}, {"e507a005", "ceilf.suw4"},
        {"e607a005", "floorf.sw4"}, {"e707a005", "floorf.suw4"},
        {"e807a005", "cvtf.sw4"}, {"e907a005", "cvtf.suw4"},
        {"ea07a005", "cvtf.ws4"}, {"eb07a005", "cvtf.uws4"},
        {"ec07a005", "cvtf.hs4"}, {"ed07a005", "cvtf.sh4"},
        {"f007a005", "absf.s4"}, {"f107a005", "negf.s4"},
        {"f207a005", "sqrtf.s4"}, {"f307a005", "recipf.s4"},
        {"f407a005", "rsqrtf.s4"}, {"fe07a005", "movv.w4"},
        {"ff07a005", "trfsrv.w4"},
        // 48-bit forms
        {"a0071d060000", "cmovf.w4"}, {"a0079d060000", "shflv.w4"},
        {"a0071d000000", "ldv.w"}, {"a0079d020000", "ldv.qw"},
        {"a007bd020000", "stv.qw"}, {"a0071d030000", "ldv.dw"},
        {"a0071d020000", "stv.w"}, {"a0079d030000", "stv.dw"},
        {"a007dd030000", "ldvz.h4"}, {"a007fd030000", "stvz.h4"},
        // DSP vector
        {"e0070006", "vadd.h"}, {"e0070206", "vadd.w"},
        {"e0070806", "vadds.h"}, {"e0071006", "vaddsat.h"},
        {"e0071806", "vmul.h"}, {"e0071c06", "vmult.h"},
        {"e0074c06", "vmsum.h"}, {"e0074006", "vmadsat.h"},
        {"e0074806", "vmulcx.h"}, {"e0075806", "vadd.dw"},
        {"e0075c06", "vbiq.h"}, {"e0075e06", "pkq30q31"},
        {"e0076806", "pkq15q31"}, {"e0076a06", "pki16i32"},
        {"e6077e06", "cnvq30q15"}, {"e0077e06", "vabs.h"},
        {"e607dc06", "vbswap.w"}, {"e007de06", "vitlv.h"},
        {"e0078006", "vand"}, {"e0078206", "vor"}, {"e0078406", "vxor"},
        {"e0078606", "vsar.dw"}, {"e0078a06", "vshl.dw"},
        {"e0078806", "vshr.dw"}, {"e007ae06", "vshufl.b"},
        {"e0077006", "vcalc.h"}, {"e0077206", "vcalc.w"},
        {"e007b006", "vcmov"}, {"e007b206", "vconcat.b"},
        {"e0075006", "vmaxgt.h"}, {"e007500e", "vmaxge.h"},
        {"e0075606", "vminlt.w"},
        {"e007f806", "vld.b"}, {"e007fc06", "vst.b"},
        {"e007c006", "vld.dw"}, {"e007c406", "vst.dw"},
        {"e007da06", "mov.w"}, {"e007dc06", "mov.h"},
        // scalar roundf (family was previously missing entirely)
        {"e0074004", "roundf.sw"}, {"e0074404", "roundf.sl"},
        {"e0075004", "roundf.dw"}, {"e0075404", "roundf.dl"},
        // pair-register r0 probes (even r0 pair is a legal operand: MAC
        // reg3/reg4 pp.116-117; FP .d reg1/reg2/reg3): r0 half reads as
        // zero, pair writes commit only the high register
        {"e63fc803", "mac"}, {"e117c023", "mac"}, {"e117c633", "mac"},
        {"e63fe803", "macu"},
        {"e0177024", "addf.d"}, {"e1175804", "negf.d"},
        {"e1075034", "trncf.dw"}, {"e02f6434", "mulf.s"},
    };

    private int checked = 0;

    private void fail(String msg) {
        throw new IllegalStateException(msg);
    }

    private static byte[] bytes(String hex) {
        byte[] out = new byte[hex.length() / 2];
        for (int i = 0; i < out.length; i++) {
            out[i] = (byte) Integer.parseInt(hex.substring(2 * i, 2 * i + 2), 16);
        }
        return out;
    }

    @Override
    public void run() throws Exception {
        Language language;
        try {
            language = DefaultLanguageService.getLanguageService()
                    .getLanguage(new LanguageID(LANGUAGE_ID));
        } catch (Exception e) {
            throw new IllegalStateException(
                    "broad RH850 language " + LANGUAGE_ID + " not registered: " + e);
        }
        ProgramDB program = new ProgramDB("v850-extended-isa", language,
                language.getDefaultCompilerSpec(), this);
        int tx = program.startTransaction("extended ISA fixtures");
        try {
            Address base = program.getAddressFactory().getDefaultAddressSpace()
                    .getAddress(0x1000);
            int codeLength = Math.max(0x1000, 0x20 * (DECODE.length + 1));
            program.getMemory().createInitializedBlock("code", base,
                    new ByteArrayInputStream(new byte[codeLength]), codeLength, monitor, false);
            program.getMemory().createInitializedBlock("data",
                    program.getAddressFactory().getDefaultAddressSpace().getAddress(0x8000),
                    new ByteArrayInputStream(new byte[0x100]), 0x100, monitor, false);

            // ---- decode parity ----
            PseudoDisassembler decoder = new PseudoDisassembler(program);
            for (String[] fixture : DECODE) {
                Address a = base.add(0x20 * (++checked));
                program.getMemory().setBytes(a, bytes(fixture[0]));
                PseudoInstruction instruction;
                try {
                    instruction = decoder.disassemble(a);
                } catch (UnknownInstructionException e) {
                    instruction = null;
                }
                if (instruction == null) {
                    fail("decode: " + fixture[0] + " (" + fixture[1] + ") not decoded");
                }
                if (!fixture[1].equals(instruction.getMnemonicString())) {
                    fail("decode: " + fixture[0] + " expected " + fixture[1]
                            + " got " + instruction.getMnemonicString());
                }
                if (instruction.getLength() != fixture[0].length() / 2) {
                    fail("decode: " + fixture[0] + " wrong length "
                            + instruction.getLength());
                }
            }
            println("Decoded " + DECODE.length + " extended-ISA fixtures");

            // ---- executed semantics ----
            execClip(program, base);
            execVaddsat(program, base);
            execVnegSaturation(program, base);
            execDebugTrapReturn(program, base);
            execAddfS4(program, base);
            execSubfMulfDivfOrder(program, base);
            execAddfDirectedRounding(program, base);
            execAddfTrapAtomicity(program, base);
            execCu1Disabled(program, base);
            execAddfFsFlush(program, base);
            execCmovf(program, base);
            execShflv(program, base);
            execLdvQw(program, base);
            execRoundfSw(program, base);
            execModadd(program, base);
            execMacPairZeroSource(program, base);
            execMacPairZeroDestination(program, base);
            execMacAliasedPair(program, base);
            execFpPairZero(program, base);
            execLdlStc(program, base);
            execCmpfTrfsrv(program, base);
            execCmpfSuppressed(program, base);
            execMaxfSnan(program, base);
            execFmafAllLanes(program, base);
            execFmafFnBoundary(program, base);
            execFmafMixedNaN(program, base);
            execCvtfRmNearest(program, base);
            execCvtfSw4Mixed(program, base);
            execRoundfSw4Nan(program, base);
            execTrncfFloorf(program, base);
            execCeilfBoundary(program, base);
            execCvtfUws4Range(program, base);
            execCvtfHs4(program, base);
            execCvtfSh4(program, base);
            execSqrtfRecipf(program, base);
            execButterfly(program, base);
            execAddxfAliased(program, base);
            execPushspPopsp(program, base);
            execLdsrStsrFxsr(program, base);
            execLdvStvNegativeDisp(program, base);
            execVshuflAliased(program, base);
            execRoundfDoubleWord(program, base);
            execRoundfExceptionStates(program, base);
            execNop(program, base);
        } finally {
            program.endTransaction(tx, false);
            program.release(this);
        }
        execCoreZeroBurst();
        println("ASSERT v850-extended-isa: passed (decode fixtures=" + DECODE.length + ")");
    }

    private void execCoreZeroBurst() throws Exception {
        Language core = DefaultLanguageService.getLanguageService()
                .getLanguage(new LanguageID("v850e3:LE:32:default"));
        ProgramDB program = new ProgramDB("g3m-zero-burst", core, core.getDefaultCompilerSpec(), this);
        int tx = program.startTransaction("zero-register burst");
        try {
            Address base = program.getAddressFactory().getDefaultAddressSpace().getAddress(0x1000);
            program.getMemory().createInitializedBlock("code-stack", base,
                    new ByteArrayInputStream(new byte[0x1000]), 0x1000, monitor, false);
            // pushsp r0,r1; popsp r0,r1: r0 reads zero and discards a loaded word.
            program.getMemory().setBytes(base, bytes("e0476009e0676009"));
            EmulatorHelper emu = new EmulatorHelper(program);
            try {
                emu.writeRegister("PC", 0x1000);
                emu.writeRegister("sp", 0x1ff0);
                emu.writeRegister("r0", 0xcafebabeL);
                emu.writeRegister("r1", 0x12345678);
                emu.writeRegister("ll_valid", 0);
                emu.writeRegister("ll_addr", 0);
                step(emu, "core pushsp zero");
                requireReg(emu, "core pushsp zero", "sp", 0x1fe8);
                requireMem(emu, "core pushsp zero", 0x1fec, 0);
                requireMem(emu, "core pushsp r1", 0x1fe8, 0x12345678);
                emu.writeMemory(base.getNewAddress(0x1fec), bytes("efbeadde"));
                emu.writeRegister("r1", 0);
                step(emu, "core popsp zero");
                requireReg(emu, "core popsp zero", "sp", 0x1ff0);
                requireReg(emu, "core popsp zero", "r0", 0xcafebabeL);
                requireReg(emu, "core popsp r1", "r1", 0x12345678);
            } finally {
                emu.dispose();
            }
        } finally {
            program.endTransaction(tx, false);
            program.release(this);
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
        emu.writeRegister("PSW", 0);
        emu.writeRegister("HVCFG", 0);
        emu.writeRegister("FPSR", 0);
        emu.writeRegister("FPEC", 0);
        return emu;
    }

    // Every FXU execution fixture starts with PSW.CU1 set (bit 17).
    private EmulatorHelper prepareFpu(ProgramDB program, Address at, String hexBytes,
            String label) throws Exception {
        EmulatorHelper emu = prepare(program, at, hexBytes, label);
        emu.writeRegister("PSW", PSW_CU1);
        return emu;
    }

    private void requireMem(EmulatorHelper emu, String label, long addr, int expected)
            throws Exception {
        byte[] raw = emu.readMemory(emu.getLanguage().getAddressFactory()
                .getDefaultAddressSpace().getAddress(addr), 4);
        long got = (raw[0] & 0xffL) | ((raw[1] & 0xffL) << 8)
                | ((raw[2] & 0xffL) << 16) | ((raw[3] & 0xffL) << 24);
        if (got != (expected & 0xffffffffL)) {
            fail(label + " expected " + Integer.toHexString(expected) + " got "
                    + Long.toHexString(got));
        }
    }

    private void requireReg(EmulatorHelper emu, String label, String reg, long expected) {
        long actual = emu.readRegister(reg).longValue() & 0xffffffffL;
        if (actual != (expected & 0xffffffffL)) {
            fail(String.format("%s: %s=0x%x expected=0x%x", label, reg, actual, expected));
        }
    }

    private void requireWReg(EmulatorHelper emu, String label, String reg, long[] lanes) {
        BigInteger actual = emu.readRegister(reg);
        if (actual == null) {
            fail(label + ": cannot read " + reg);
        }
        int laneCount = emu.getLanguage().getRegister(reg).getBitLength() / 32;
        if (lanes.length != laneCount) {
            fail(label + ": expected " + laneCount + " lanes for " + reg);
        }
        for (int lane = 0; lane < laneCount; lane++) {
            long laneValue = actual.shiftRight(32 * lane).longValue() & 0xffffffffL;
            if (laneValue != (lanes[lane] & 0xffffffffL)) {
                fail(String.format("%s: %s lane%d=0x%x expected=0x%x (full=%s)", label,
                        reg, lane, laneValue, lanes[lane], actual.toString(16)));
            }
        }
    }

    private void patchInstruction(ProgramDB program, EmulatorHelper emu, Address at,
            String hexBytes) throws Exception {
        byte[] instruction = bytes(hexBytes);
        program.getMemory().setBytes(at, instruction);
        emu.writeMemory(at, instruction);
        emu.getEmulator().setContextRegisterValue(
                emu.getEmulator().getContextRegisterValue());
    }


    private static BigInteger lanes(long lane0, long lane1, long lane2, long lane3) {
        return BigInteger.valueOf(lane0 & 0xffffffffL)
                .add(BigInteger.valueOf(lane1 & 0xffffffffL).shiftLeft(32))
                .add(BigInteger.valueOf(lane2 & 0xffffffffL).shiftLeft(64))
                .add(BigInteger.valueOf(lane3 & 0xffffffffL).shiftLeft(96));
    }

    private void step(EmulatorHelper emu, String label) throws Exception {
        if (!emu.step(monitor)) {
            fail(label + ": emulator step failed: " + emu.getLastError());
        }
    }


    private void execNop(ProgramDB program, Address base) throws Exception {
        Address at = base.add(0x2c);
        EmulatorHelper emu = prepare(program, at, "0000", "nop");
        try {
            emu.writeRegister("PSW", 0x400f);
            emu.writeRegister("r10", 0xdeadbeefL);
            emu.writeRegister("FPSR", 0x12345678L);
            step(emu, "nop");
            requireReg(emu, "nop", "PC", at.add(2).getOffset());
            requireReg(emu, "nop", "PSW", 0x400f);
            requireReg(emu, "nop", "r10", 0xdeadbeefL);
            requireReg(emu, "nop", "FPSR", 0x12345678L);
        } finally {
            emu.dispose();
        }
    }

    // clip.b r1, r2: saturate -> ordinary -> zero transition (G4MH p.47):
    // +0x100/-0x81 saturate, 0x42 passes through, and zero produces zero.
    // CY clears, OV/S/Z reflect this result, and SAT remains accumulated.
    private void execClip(ProgramDB program, Address base) throws Exception {
        Address at = base.add(0x10);
        EmulatorHelper emu = prepare(program, at, "e1170800", "clip");
        try {
            emu.writeRegister("PSW", 0x800f);
            emu.writeRegister("r1", 0x100);
            step(emu, "clip-saturate-hi");
            requireReg(emu, "clip-saturate-hi", "r2", 0x7f);
            requireReg(emu, "clip-saturate-hi", "PSW", 0x8014);
            emu.writeRegister("r1", -0x81);
            emu.writeRegister("PC", at.getOffset());
            step(emu, "clip-saturate-lo");
            requireReg(emu, "clip-saturate-lo", "r2", 0xffffff80L);
            requireReg(emu, "clip-saturate-lo", "PSW", 0x8016);
            emu.writeRegister("r1", 0x42);
            emu.writeRegister("PC", at.getOffset());
            step(emu, "clip-ordinary");
            requireReg(emu, "clip-ordinary", "r2", 0x42);
            requireReg(emu, "clip-ordinary", "PSW", 0x8010);
            emu.writeRegister("r1", 0);
            emu.writeRegister("PC", at.getOffset());
            step(emu, "clip-zero");
            requireReg(emu, "clip-zero", "r2", 0);
            requireReg(emu, "clip-zero", "PSW", 0x8011);
        } finally {
            emu.dispose();
        }
    }

    // vaddsat.h v1, v2, v3: halfword lanes saturate.
    private void execVaddsat(ProgramDB program, Address base) throws Exception {
        Address at = base.add(0x20);
        // v1 (r1 field), v2 (r2 field): hw1 = 1 | (2<<11) | 0x07e0, hw2 = (3<<11)|0x610
        EmulatorHelper emu = prepare(program, at, "e117101e", "vaddsat");
        try {
            emu.writeRegister("SESR", 0);
            emu.writeRegister("v1", BigInteger.valueOf(0x00017fff7fff0002L));
            emu.writeRegister("v2", BigInteger.valueOf(0x0001000100020003L));
            step(emu, "vaddsat");
            requireWReg(emu, "vaddsat", "v3",
                    new long[]{0x7fff0005, 0x00027fff});
            requireReg(emu, "vaddsat", "SESR", 3);
        } finally {
            emu.dispose();
        }
    }
    private void execVnegSaturation(ProgramDB program, Address base) throws Exception {
        Address at = base.add(0x24);
        EmulatorHelper emu = prepare(program, at, "e20f7e1e", "vneg.h");
        try {
            emu.writeRegister("SESR", 0);
            emu.writeRegister("v1", new BigInteger("000080000003fffe", 16));
            step(emu, "vneg.h");
            requireWReg(emu, "vneg.h", "v3",
                    new long[]{0xfffd0002L, 0x00007fffL});
            requireReg(emu, "vneg.h", "SESR", 3);
            patchInstruction(program, emu, at, "e30f7e0e");
            emu.writeRegister("PC", at.getOffset());
            emu.writeRegister("SESR", 0);
            emu.writeRegister("v1", new BigInteger("80000000fffffffe", 16));
            step(emu, "vneg.w-aliased");
            requireWReg(emu, "vneg.w-aliased", "v1",
                    new long[]{2, 0x7fffffffL});
            requireReg(emu, "vneg.w-aliased", "SESR", 3);
        } finally {
            emu.dispose();
        }
    }

    private void execDebugTrapReturn(ProgramDB program, Address base) throws Exception {
        Address at = base.add(0x28);
        Address vector = program.getAddressFactory().getDefaultAddressSpace().getAddress(0x60);
        program.getMemory().createInitializedBlock("debug-vector", vector,
                new ByteArrayInputStream(bytes("e0074601")), 4, monitor, false);
        EmulatorHelper emu = prepare(program, at, "40f8", "dbtrap");
        try {
            emu.writeRegister("PSW", 0x0b);
            emu.writeRegister("dbg_dir", 0x40);
            step(emu, "dbtrap");
            requireReg(emu, "dbtrap", "PC", 0x60);
            requireReg(emu, "dbtrap", "dbg_pc", at.getOffset() + 2);
            requireReg(emu, "dbtrap", "dbg_psw", 0x0b);
            requireReg(emu, "dbtrap", "PSW", 0xeb);
            requireReg(emu, "dbtrap", "dbg_dir", 0x41);
            step(emu, "dbret");
            requireReg(emu, "dbret", "PC", at.getOffset() + 2);
            requireReg(emu, "dbret", "PSW", 0x0b);
            requireReg(emu, "dbret", "dbg_dir", 0x40);
        } finally {
            emu.dispose();
        }
    }


    // addf.s4 w1, w2, w3: float lanes 2.5 + 4.25 = 6.75.
    private void execAddfS4(ProgramDB program, Address base) throws Exception {
        Address at = base.add(0x30);
        EmulatorHelper emu = prepareFpu(program, at, "e117a41d", "addf.s4");
        try {
            emu.writeRegister("w1", lanes(Float.floatToRawIntBits(2.5f),
                    Float.floatToRawIntBits(4.25f), Float.floatToRawIntBits(1.0f),
                    Float.floatToRawIntBits(-0.5f)));
            emu.writeRegister("w2", BigInteger.ZERO);
            step(emu, "addf.s4");
            requireWReg(emu, "addf.s4", "w3", new long[]{
                    Float.floatToRawIntBits(2.5f), Float.floatToRawIntBits(4.25f),
                    Float.floatToRawIntBits(1.0f), Float.floatToRawIntBits(-0.5f)});
        } finally {
            emu.dispose();
        }
    }

    // Operand order is wreg2 OP wreg1 (G4MH [Operation] blocks):
    // subf 5.0-3.0=2.0, mulf 0.5*4.0=2.0, divf 1.0/4.0=0.25.
    private void execSubfMulfDivfOrder(ProgramDB program, Address base) throws Exception {
        Address at = base.add(0x180);
        EmulatorHelper emu = prepareFpu(program, at, "e117a61d", "subf.s4");
        try {
            emu.writeRegister("w1", lanes(Float.floatToRawIntBits(3.0f),
                    Float.floatToRawIntBits(3.0f), Float.floatToRawIntBits(3.0f),
                    Float.floatToRawIntBits(3.0f)));
            emu.writeRegister("w2", lanes(Float.floatToRawIntBits(5.0f),
                    Float.floatToRawIntBits(5.0f), Float.floatToRawIntBits(5.0f),
                    Float.floatToRawIntBits(5.0f)));
            step(emu, "subf.s4");
            requireWReg(emu, "subf.s4", "w3", new long[]{
                    Float.floatToRawIntBits(2.0f), Float.floatToRawIntBits(2.0f),
                    Float.floatToRawIntBits(2.0f), Float.floatToRawIntBits(2.0f)});
            // mulf w1, w2, w3: 0.5 * 4.0 = 2.0
            patchInstruction(program, emu, at, "e117a81d");
            emu.writeRegister("PC", at.getOffset());
            emu.writeRegister("w1", lanes(Float.floatToRawIntBits(4.0f),
                    Float.floatToRawIntBits(4.0f), Float.floatToRawIntBits(4.0f),
                    Float.floatToRawIntBits(4.0f)));
            emu.writeRegister("w2", lanes(Float.floatToRawIntBits(0.5f),
                    Float.floatToRawIntBits(0.5f), Float.floatToRawIntBits(0.5f),
                    Float.floatToRawIntBits(0.5f)));
            step(emu, "mulf.s4");
            requireWReg(emu, "mulf.s4", "w3", new long[]{
                    Float.floatToRawIntBits(2.0f), Float.floatToRawIntBits(2.0f),
                    Float.floatToRawIntBits(2.0f), Float.floatToRawIntBits(2.0f)});
            // divf w1, w2, w3: 1.0 / 4.0 = 0.25
            patchInstruction(program, emu, at, "e117ae1d");
            emu.writeRegister("PC", at.getOffset());
            emu.writeRegister("w1", lanes(Float.floatToRawIntBits(4.0f),
                    Float.floatToRawIntBits(4.0f), Float.floatToRawIntBits(4.0f),
                    Float.floatToRawIntBits(4.0f)));
            emu.writeRegister("w2", lanes(Float.floatToRawIntBits(1.0f),
                    Float.floatToRawIntBits(1.0f), Float.floatToRawIntBits(1.0f),
                    Float.floatToRawIntBits(1.0f)));
            step(emu, "divf.s4");
            requireWReg(emu, "divf.s4", "w3", new long[]{
                    Float.floatToRawIntBits(0.25f), Float.floatToRawIntBits(0.25f),
                    Float.floatToRawIntBits(0.25f), Float.floatToRawIntBits(0.25f)});
        } finally {
            emu.dispose();
        }
    }

    // addf.s4 w1, w2, w3 with 1.0 + 3*2^-24 (exact single midpoint):
    // FXSR.RM RZ keeps 1.0, RP rounds up to 1.0+2^-23; both raise I.
    private void execAddfDirectedRounding(ProgramDB program, Address base) throws Exception {
        Address at = base.add(0x190);
        EmulatorHelper emu = prepareFpu(program, at, "e117a41d", "addf-rz");
        try {
            long one = Float.floatToRawIntBits(1.0f);
            long halfUlp = 0x33800000L; // 2^-24: midpoint between 1.0 and its successor.
            emu.writeRegister("w1", lanes(one, one, one, one));
            emu.writeRegister("w2", lanes(halfUlp, halfUlp, halfUlp, halfUlp));
            emu.writeRegister("FXSR", 0x40000L); // RM = 1 (RZ)
            step(emu, "addf-rz");
            requireWReg(emu, "addf-rz", "w3", new long[]{one, one, one, one});
            long fxsr = emu.readRegister("FXSR").longValue() & 0xffffffffL;
            if ((fxsr & 0x1f) != 0x1) {
                fail(String.format("addf-rz: XP=0x%x expected I (0x1)", fxsr & 0x1f));
            }
            // RP: the same midpoint rounds up to the next single
            emu.writeRegister("PC", at.getOffset());
            emu.writeRegister("FXSR", 0x80000L); // RM = 2 (RP)
            step(emu, "addf-rp");
            long up = Float.floatToRawIntBits(1.0f) + 1; // 0x3F800001
            requireWReg(emu, "addf-rp", "w3", new long[]{up, up, up, up});
            fxsr = emu.readRegister("FXSR").longValue() & 0xffffffffL;
            if ((fxsr & 0x1f) != 0x1) {
                fail(String.format("addf-rp: XP=0x%x expected I (0x1)", fxsr & 0x1f));
            }
            long fxxp = emu.readRegister("FXXP").longValue() & 0xffffffffL;
            if (fxxp != 0x01010101L) {
                fail(String.format("addf-rp: FXXP=0x%x expected 0x01010101", fxxp));
            }
        } finally {
            emu.dispose();
        }
    }

    // addf.s4 with FXSR.EV enabled and an S-NaN lane: the FXE pends with the
    // whole destination suppressed - every lane writes, XP/FXXP untouched
    // (R01UH0770 Figure 3.38).
    private void execAddfTrapAtomicity(ProgramDB program, Address base) throws Exception {
        Address at = base.add(0x1A0);
        EmulatorHelper emu = prepareFpu(program, at, "e117a41d", "addf-trap");
        try {
            long one = Float.floatToRawIntBits(1.0f);
            long two = Float.floatToRawIntBits(2.0f);
            emu.writeRegister("FXSR", 0x200L); // EV enabled (XE bit 9)
            emu.writeRegister("w1", lanes(0x7f800001L, one, one, one));
            emu.writeRegister("w2", lanes(two, two, two, two));
            BigInteger sentinel = new BigInteger("dead1eefbaadf00d123456789abcdef0", 16);
            emu.writeRegister("w3", sentinel);
            step(emu, "addf-trap");
            if (!emu.readRegister("w3").equals(sentinel)) {
                fail("addf-trap: w3 not fully suppressed");
            }
            long fxsr = emu.readRegister("FXSR").longValue() & 0xffffffffL;
            if (fxsr != 0x4200L) {
                fail(String.format("addf-trap: FXSR=0x%x expected 0x4200"
                        + " (XE.EV kept, XC=V, XP untouched)", fxsr));
            }
            long fxxc = emu.readRegister("FXXC").longValue() & 0xffffffffL;
            if (fxxc != 0x10L) {
                fail(String.format("addf-trap: FXXC=0x%x expected lane0 V=0x10", fxxc));
            }
            long fxxp = emu.readRegister("FXXP").longValue() & 0xffffffffL;
            if (fxxp != 0L) {
                fail(String.format("addf-trap: FXXP=0x%x expected 0 (preserved)", fxxp));
            }
            requireReg(emu, "addf-trap", "EIPC", at.getOffset());
            requireReg(emu, "addf-trap", "EIIC", 0x75);
            requireReg(emu, "addf-trap", "PC", 0x70); // RBASE defaults 0
        } finally {
            emu.dispose();
        }
    }

    // addf.s4 with PSW.CU1 clear: FE-level coprocessor-unusable exception
    // UCPOP, cause 81H / vector 80H, no FXU state change at all.
    private void execCu1Disabled(ProgramDB program, Address base) throws Exception {
        Address at = base.add(0x1B0);
        EmulatorHelper emu = prepare(program, at, "e117a41d", "addf-ucpop");
        try {
            emu.writeRegister("PSW", 0L);
            long one = Float.floatToRawIntBits(1.0f);
            emu.writeRegister("w1", lanes(one, one, one, one));
            emu.writeRegister("w2", lanes(one, one, one, one));
            BigInteger sentinel = new BigInteger("cafef00df00dcafe0123456789abcdef", 16);
            emu.writeRegister("w3", sentinel);
            step(emu, "addf-ucpop");
            if (!emu.readRegister("w3").equals(sentinel)) {
                fail("addf-ucpop: w3 changed with CU1 clear");
            }
            requireReg(emu, "addf-ucpop", "FEPC", at.getOffset());
            requireReg(emu, "addf-ucpop", "FEIC", 0x81);
            requireReg(emu, "addf-ucpop", "PC", 0x80); // RBASE defaults 0
            long fxsr = emu.readRegister("FXSR").longValue() & 0xffffffffL;
            if (fxsr != 0L) {
                fail(String.format("addf-ucpop: FXSR=0x%x expected 0", fxsr));
            }
        } finally {
            emu.dispose();
        }
    }

    // addf.s4 against a subnormal input: FXSR.FS=1 flushes the input to +0
    // (FXSR.IF + XP.I accumulate, result commits); FXSR.FS=0 raises the
    // unimplemented-operation exception E, which always traps.
    private void execAddfFsFlush(ProgramDB program, Address base) throws Exception {
        Address at = base.add(0x1C0);
        EmulatorHelper emu = prepareFpu(program, at, "e117a41d", "addf-fs");
        try {
            long one = Float.floatToRawIntBits(1.0f);
            long two = Float.floatToRawIntBits(2.0f);
            // 0x00400000 = 2^-127 (subnormal single)
            emu.writeRegister("FXSR", 0x20000L); // FS
            emu.writeRegister("w1", lanes(0x00400000L, one, one, one));
            emu.writeRegister("w2", lanes(one, one, one, one));
            step(emu, "addf-fs-flush");
            requireWReg(emu, "addf-fs-flush", "w3",
                    new long[]{one, two, two, two});
            long fxsr = emu.readRegister("FXSR").longValue() & 0xffffffffL;
            if (fxsr != 0x420001L) { // FS17|IF22|XP.I
                fail(String.format("addf-fs-flush: FXSR=0x%x expected 0x420001"
                        + " (FS|IF|XP.I)", fxsr));
            }
            long fxxp = emu.readRegister("FXXP").longValue() & 0xffffffffL;
            if (fxxp != 0x1L) {
                fail(String.format("addf-fs-flush: FXXP=0x%x expected lane0 I", fxxp));
            }
            // FS=0: the same subnormal input raises E and traps (XC bit 15)
            emu.writeRegister("PC", at.getOffset());
            emu.writeRegister("FXSR", 0L);
            emu.writeRegister("w1", lanes(0x00400000L, one, one, one));
            emu.writeRegister("w2", lanes(one, one, one, one));
            BigInteger sentinel = BigInteger.valueOf(0x0BAD0BAD0BAD0BADL);
            emu.writeRegister("w3", sentinel);
            step(emu, "addf-fs-e");
            if (!emu.readRegister("w3").equals(sentinel)) {
                fail("addf-fs-e: w3 not suppressed on E trap");
            }
            fxsr = emu.readRegister("FXSR").longValue() & 0xffffffffL;
            if (fxsr != 0x8000L) { // XC = E (bit 15)
                fail(String.format("addf-fs-e: FXSR=0x%x expected 0x8000 (XC.E)",
                        fxsr));
            }
            long fxxc = emu.readRegister("FXXC").longValue() & 0xffffffffL;
            if (fxxc != 0x20L) {
                fail(String.format("addf-fs-e: FXXC=0x%x expected lane0 E=0x20",
                        fxxc));
            }
            requireReg(emu, "addf-fs-e", "EIPC", at.getOffset());
            requireReg(emu, "addf-fs-e", "EIIC", 0x75);
            requireReg(emu, "addf-fs-e", "PC", 0x70);
        } finally {
            emu.dispose();
        }
    }

    // cmovf.w4 w4, w1, w2, w3: lane picks w1 when w4 lane nonzero.
    private void execCmovf(ProgramDB program, Address base) throws Exception {
        Address at = base.add(0x40);
        // w4=4 (bits 32-36), w1=1, w2=2, w3=3
        EmulatorHelper emu = prepareFpu(program, at, "a1171d1e0400", "cmovf.w4");
        try {
            BigInteger ones = BigInteger.ONE;
            emu.writeRegister("w4", ones); // lane0 selects
            emu.writeRegister("w1", BigInteger.valueOf(0x11111110L));
            emu.writeRegister("w2", lanes(0x22222222L, 0x22222222L,
                    0x22222222L, 0x22222222L));
            step(emu, "cmovf.w4");
            // w4 is 1 -> only lane 0 set -> lane0 takes w1 lane0
            requireWReg(emu, "cmovf.w4", "w3", new long[]{0x11111110, 0x22222222,
                    0x22222222, 0x22222222});
        } finally {
            emu.dispose();
        }
    }

    // shflv.w4 imm12, w1, w2, w3: per-lane 8-way source select.
    private void execShflv(ProgramDB program, Address base) throws Exception {
        Address at = base.add(0x50);
        // imm12 = 4 | (1<<3) | (2<<6) | (3<<9) = 0x68C
        EmulatorHelper emu = prepareFpu(program, at, "a1179d1e8c06", "shflv.w4");
        try {
            BigInteger src = BigInteger.valueOf(0xA0L)
                    .add(BigInteger.valueOf(0xA1L).shiftLeft(32))
                    .add(BigInteger.valueOf(0xA2L).shiftLeft(64))
                    .add(BigInteger.valueOf(0xA3L).shiftLeft(96));
            emu.writeRegister("w1", src);
            emu.writeRegister("w2", BigInteger.ZERO); // lanes 4-7 are zero
            step(emu, "shflv.w4");
            // sel: lane0=4 -> w2 lane0; lane1=1 -> w1 lane1; lane2=2; lane3=3 -> w1 lane3
            requireWReg(emu, "shflv.w4", "w3", new long[]{0, 0xA1, 0xA2, 0xA3});
        } finally {
            emu.dispose();
        }
    }

    // ldv.qw disp16[r1], w3: 16-byte load from r1.
    private void execLdvQw(ProgramDB program, Address base) throws Exception {
        Address at = base.add(0x60);
        EmulatorHelper emu = prepareFpu(program, at, "a5079d1a0000", "ldv.qw");
        try {
            Address data = program.getAddressFactory().getDefaultAddressSpace()
                    .getAddress(0x8000);
            byte[] payload = new byte[16];
            for (int i = 0; i < 16; i++) {
                payload[i] = (byte) (0xE0 + i);
            }
            emu.writeMemory(data, payload);
            emu.writeRegister("tp", 0x8000);
            step(emu, "ldv.qw");
            requireWReg(emu, "ldv.qw", "w3",
                    new long[]{0xE3E2E1E0L, 0xE7E6E5E4L, 0xEBEAE9E8L, 0xEFEEEDECL});
        } finally {
            emu.dispose();
        }
    }

    // roundf.sw r2, r6: 2.5f ties to even = 2 (R01US0209 2.4.4.68 p.354;
    // dest is r6, not r0: the R2731 field-0 form discards its write).
    private void execRoundfSw(ProgramDB program, Address base) throws Exception {
        Address at = base.add(0x70);
        EmulatorHelper emu = prepare(program, at, "e0174034", "roundf.sw");
        try {
            emu.writeRegister("FPSR", 0x000c0000); // RM does not alter ROUNDF.
            emu.writeRegister("r2", Float.floatToRawIntBits(2.5f));
            emu.writeRegister("r6", 0xDEADBEEFL);
            step(emu, "roundf.sw");
            requireReg(emu, "roundf.sw", "r6", 2);
            requireReg(emu, "roundf.sw-inexact", "FPSR", 0x000c0001);
        } finally {
            emu.dispose();
        }
    }

    // modadd (pair r0,r1): r0 is architecturally fixed zero, so inc and
    // value read as 0 and the rewritten inc/value word is discarded -- the
    // poked raw r0 varnode is neither read (inc/val = 0, not 1/4) nor
    // written, and the limit in r1 survives untouched.
    private void execModadd(ProgramDB program, Address base) throws Exception {
        Address at = base.add(0x80);
        EmulatorHelper emu = prepare(program, at, "e007d806", "modadd");
        try {
            emu.writeRegister("r0", (1L << 16) | 4);
            emu.writeRegister("r1", 2);
            step(emu, "modadd");
            requireReg(emu, "modadd", "r0", (1L << 16) | 4);
            requireReg(emu, "modadd", "r1", 2);
        } finally {
            emu.dispose();
        }
    }

    // MAC/MACU with the r0:r1 pair as reg3 (legal: R01US0209EJ0220
    // pp.116-117 allow even r0): the accumulate source reads (0 || r1), so
    // the poked raw r0 varnode must not leak into the low accumulator word.
    private void execMacPairZeroSource(ProgramDB program, Address base) throws Exception {
        Address at = base.add(0x290);
        // mac r6, r7, r0:r1, r8:r9: 0x0000000200000000 + 3 * -5
        EmulatorHelper emu = prepare(program, at, "e63fc803", "mac-pair0-src");
        try {
            emu.writeRegister("r0", 0xCAFEBABEL);
            emu.writeRegister("r1", 2);
            emu.writeRegister("r6", 3);
            emu.writeRegister("r7", -5);
            step(emu, "mac-pair0-src");
            requireReg(emu, "mac-pair0-src", "r8", 0xFFFFFFF1L);
            requireReg(emu, "mac-pair0-src", "r9", 1);
            requireReg(emu, "mac-pair0-src", "r0", 0xCAFEBABEL);
            requireReg(emu, "mac-pair0-src", "r1", 2);
            // macu r6, r7, r0:r1, r8:r9: 0x0000000200000000 + 3 * 0xFFFFFFFD
            patchInstruction(program, emu, at, "e63fe803");
            emu.writeRegister("PC", at.getOffset());
            emu.writeRegister("r7", 0xFFFFFFFDL);
            step(emu, "macu-pair0-src");
            requireReg(emu, "macu-pair0-src", "r8", 0xFFFFFFF7L);
            requireReg(emu, "macu-pair0-src", "r9", 4);
            requireReg(emu, "macu-pair0-src", "r0", 0xCAFEBABEL);
        } finally {
            emu.dispose();
        }
    }

    // MAC into the r0:r1 pair as reg4 (reg1 = r1 aliases the destination
    // high word), then a second MAC reading the pair back: only r1 is
    // committed, the raw r0 varnode never changes, and the discarded low
    // word does not reappear in the later read.
    private void execMacPairZeroDestination(ProgramDB program, Address base) throws Exception {
        Address at = base.add(0x2a0);
        // mac r1, r2, r4:r5, r0:r1: 0x0000000140000000 + 0x1234 * -7
        EmulatorHelper emu = prepare(program, at, "e117c023", "mac-pair0-dst");
        try {
            emu.writeRegister("r0", 0xCAFEBABEL);
            emu.writeRegister("r1", 0x1234);
            emu.writeRegister("r2", -7);
            emu.writeRegister("gp", 0x40000000L);
            emu.writeRegister("tp", 1);
            step(emu, "mac-pair0-dst");
            requireReg(emu, "mac-pair0-dst", "r1", 1);
            requireReg(emu, "mac-pair0-dst", "r0", 0xCAFEBABEL);
            requireReg(emu, "mac-pair0-dst", "gp", 0x40000000L);
            requireReg(emu, "mac-pair0-dst", "tp", 1);
            // mac r5, r6, r0:r1, r8:r9 reads the pair back: (0 || 1) + 1 * -7
            patchInstruction(program, emu, at, "e537c803");
            emu.writeRegister("PC", at.getOffset());
            emu.writeRegister("r6", -7);
            step(emu, "mac-pair0-readback");
            requireReg(emu, "mac-pair0-readback", "r8", 0xFFFFFFF9L);
            requireReg(emu, "mac-pair0-readback", "r9", 0);
            requireReg(emu, "mac-pair0-readback", "r0", 0xCAFEBABEL);
            requireReg(emu, "mac-pair0-readback", "r1", 1);
        } finally {
            emu.dispose();
        }
    }

    // MAC with reg3 == reg4 (r6:r7): the same pair is read and rewritten.
    private void execMacAliasedPair(ProgramDB program, Address base) throws Exception {
        Address at = base.add(0x2b0);
        // mac r1, r2, r6:r7, r6:r7: 0x9ABCDEF012345678 + 3 * -4
        EmulatorHelper emu = prepare(program, at, "e117c633", "mac-alias");
        try {
            emu.writeRegister("r1", 3);
            emu.writeRegister("r2", -4);
            emu.writeRegister("r6", 0x12345678L);
            emu.writeRegister("r7", 0x9ABCDEF0L);
            step(emu, "mac-alias");
            requireReg(emu, "mac-alias", "r6", 0x1234566CL);
            requireReg(emu, "mac-alias", "r7", 0x9ABCDEF0L);
        } finally {
            emu.dispose();
        }
    }

    // FP pairs: addf.d reads the r0:r1 pair as (0 || r1) bits; negf.d into
    // r0:r1 commits only r1 (the discarded low word never reaches the raw
    // r0 varnode) and trncf.dw reads the pair back; the scalar mulf.s r0
    // operand reads +0.0.
    private void execFpPairZero(ProgramDB program, Address base) throws Exception {
        Address at = base.add(0x2c0);
        // addf.d r0:r1, r2:r3, r4:r5 = 1.5 + 2.25 with r0 supplying +0 low
        EmulatorHelper emu = prepare(program, at, "e0177024", "addf.d-pair0-src");
        try {
            emu.writeRegister("r0", 0xCAFEBABEL);
            emu.writeRegister("r1", Double.doubleToLongBits(1.5d) >>> 32);
            emu.writeRegister("r2sp", Double.doubleToLongBits(2.25d));
            step(emu, "addf.d-pair0-src");
            long sum = Double.doubleToLongBits(3.75d);
            requireReg(emu, "addf.d-pair0-src", "gp", sum & 0xffffffffL);
            requireReg(emu, "addf.d-pair0-src", "tp", sum >>> 32);
            requireReg(emu, "addf.d-pair0-src", "r0", 0xCAFEBABEL);
            requireReg(emu, "addf.d-pair0-src", "r1", Double.doubleToLongBits(1.5d) >>> 32);
            // negf.d r2:r3, r0:r1: only r1 receives the result high word
            patchInstruction(program, emu, at, "e1175804");
            emu.writeRegister("PC", at.getOffset());
            emu.writeRegister("r2sp", Double.doubleToLongBits(-2.75d));
            step(emu, "negf.d-pair0-dst");
            requireReg(emu, "negf.d-pair0-dst", "r1", Double.doubleToLongBits(2.75d) >>> 32);
            requireReg(emu, "negf.d-pair0-dst", "r0", 0xCAFEBABEL);
            // trncf.dw r0:r1, r6 reads (0 || hi(2.75)) back
            patchInstruction(program, emu, at, "e1075034");
            emu.writeRegister("PC", at.getOffset());
            emu.writeRegister("r6", 0xDEADBEEFL);
            step(emu, "trncf.dw-pair0-read");
            requireReg(emu, "trncf.dw-pair0-read", "r6", 2);
            // mulf.s r0, r5, r6: the scalar r0 operand reads +0.0
            patchInstruction(program, emu, at, "e02f6434");
            emu.writeRegister("PC", at.getOffset());
            emu.writeRegister("tp", Float.floatToRawIntBits(3.5f));
            emu.writeRegister("r6", 0xDEADBEEFL);
            step(emu, "mulf.s-r0");
            requireReg(emu, "mulf.s-r0", "r6", 0);
            requireReg(emu, "mulf.s-r0", "r0", 0xCAFEBABEL);
        } finally {
            emu.dispose();
        }
    }

    // ldl.hu [r5], r6 then stc.h r6, [r5]: reservation succeeds once.
    private void execLdlStc(ProgramDB program, Address base) throws Exception {
        Address at = base.add(0x90);
        program.getMemory().setBytes(at, bytes("e5077433"));
        program.getMemory().setBytes(at.add(4), bytes("e5077633"));
        PseudoDisassembler decoder = new PseudoDisassembler(program);
        if (decoder.disassemble(at) == null || decoder.disassemble(at.add(4)) == null) {
            fail("ldl/stc: fixtures not decoded");
        }
        EmulatorHelper emu = new EmulatorHelper(program);
        try {
            Address data = program.getAddressFactory().getDefaultAddressSpace()
                    .getAddress(0x8040);
            program.getMemory().setShort(data, (short) 0xBEEF);
            emu.writeRegister("PC", at.getOffset());
            emu.writeRegister("tp", 0x8040);
            step(emu, "ldl.hu");
            requireReg(emu, "ldl.hu", "r6", 0xBEEF);
            emu.writeRegister("PC", at.add(4).getOffset());
            emu.writeRegister("r6", 0xCAFE);
            step(emu, "stc.h");
            requireReg(emu, "stc.h", "r6", 1);
            byte[] stored = emu.readMemory(data, 2);
            if (stored == null || stored[0] != (byte) 0xFE || stored[1] != (byte) 0xCA) {
                fail("stc.h: memory not written: " + java.util.Arrays.toString(stored));
            }
            // second store without a new reservation fails
            emu.writeRegister("PC", at.add(4).getOffset());
            step(emu, "stc.h-again");
            requireReg(emu, "stc.h-again", "r6", 0);
        } finally {
            emu.dispose();
        }
    }


    // cmpf.s4 eq, w1, w2, w3 then trfsrv.w4 4, w3: all-equal lanes produce
    // all-ones; TRFSRV imm3=4 ANDs the lane predicates into PSW.Z.
    private void execCmpfTrfsrv(ProgramDB program, Address base) throws Exception {
        Address at = base.add(0xB0);
        program.getMemory().setBytes(at, bytes("e117841d"));
        program.getMemory().setBytes(at.add(8), bytes("ff1fa025"));
        PseudoDisassembler decoder = new PseudoDisassembler(program);
        if (decoder.disassemble(at) == null || decoder.disassemble(at.add(8)) == null) {
            fail("cmpf/trfsrv: fixtures not decoded");
        }
        EmulatorHelper emu = new EmulatorHelper(program);
        try {
            emu.writeRegister("PSW", PSW_CU1);
            BigInteger lanes = lanes(Float.floatToRawIntBits(1.5f),
                    Float.floatToRawIntBits(1.5f), Float.floatToRawIntBits(1.5f),
                    Float.floatToRawIntBits(1.5f));
            emu.writeRegister("PC", at.getOffset());
            emu.writeRegister("w1", lanes);
            emu.writeRegister("w2", lanes);
            step(emu, "cmpf.s4");
            requireWReg(emu, "cmpf.s4", "w3", new long[]{0xffffffffL, 0xffffffffL,
                    0xffffffffL, 0xffffffffL});
            emu.writeRegister("PC", at.add(8).getOffset());
            step(emu, "trfsrv.w4");
            long psw = emu.readRegister("PSW").longValue() & 0xffffffffL;
            if ((psw & 1) != 1) {
                fail(String.format("trfsrv.w4: PSW.Z=0 (psw=0x%x)", psw));
            }
        } finally {
            emu.dispose();
        }
    }

    // cmpf.s4 lt (fcond bit3, unordered-signaling) with FXSR.EV set and a
    // Q-NaN lane: every lane result is suppressed and the FXE pends with
    // EIIC 75H, EIPC = faulting instruction, XC = V (G4MH p.411).
    private void execCmpfSuppressed(ProgramDB program, Address base) throws Exception {
        Address at = base.add(0xD0);
        EmulatorHelper emu = prepareFpu(program, at, "e1179819", "cmpf.s4");
        try {
            emu.writeRegister("FXSR", 0x200L); // EV enabled (XE bit 9)
            emu.writeRegister("w1", BigInteger.ZERO);
            emu.writeRegister("w2", lanes(0x7fc00000L, 1, 1, 1)); // NaN lane0
            BigInteger sentinel = BigInteger.valueOf(0xDEADBEEFL);
            emu.writeRegister("w3", sentinel);
            step(emu, "cmpf.s4");
            if (!emu.readRegister("w3").equals(sentinel)) {
                fail("cmpf.s4 suppressed case overwrote w3");
            }
            long fxsr = emu.readRegister("FXSR").longValue() & 0xffffffffL;
            if ((fxsr & 0xfc00) != 0x4000) {
                fail(String.format("cmpf.s4: XC=0x%x expected V (0x4000)",
                        (fxsr >> 10) & 0x3f));
            }
            long fxxc = emu.readRegister("FXXC").longValue() & 0xffffffffL;
            if (fxxc != 0x10L) {
                fail(String.format("cmpf.s4: FXXC=0x%x expected lane0 V=0x10", fxxc));
            }
            requireReg(emu, "cmpf.s4", "EIPC", at.getOffset());
            requireReg(emu, "cmpf.s4", "EIIC", 0x75);
            requireReg(emu, "cmpf.s4", "PC", 0x70); // RBASE defaults 0
        } finally {
            emu.dispose();
        }
    }

    // maxf.s4 w1, w2, w3: an S-NaN lane yields the canonical 7fffffff with
    // the V cause (R01UH0770 Table 3.125), accumulated masked into FXSR.XP
    // and the per-way FXXP; XC/FXXC stay clear because EV is not enabled.
    private void execMaxfSnan(ProgramDB program, Address base) throws Exception {
        Address at = base.add(0xE0);
        EmulatorHelper emu = prepareFpu(program, at, "e117aa1d", "maxf.s4");
        try {
            emu.writeRegister("w1", lanes(0x7f800001L,
                    Float.floatToRawIntBits(1.0f), 0L, 0L));
            emu.writeRegister("w2", lanes(Float.floatToRawIntBits(5.0f),
                    Float.floatToRawIntBits(2.0f), 0L, 0L));
            emu.writeRegister("FXSR", BigInteger.ZERO);
            step(emu, "maxf.s4");
            requireWReg(emu, "maxf.s4", "w3", new long[]{0x7fffffffL,
                    Float.floatToRawIntBits(2.0f), 0, 0});
            long fxsr = emu.readRegister("FXSR").longValue() & 0xffffffffL;
            if ((fxsr & 0x1f) != 0x10) {
                fail(String.format("maxf.s4: XP=0x%x expected V (0x10)", fxsr & 0x1f));
            }
            if ((fxsr & 0xfc00) != 0) {
                fail(String.format("maxf.s4: XC=0x%x expected 0 (masked)",
                        (fxsr >> 10) & 0x3f));
            }
            long fxxp = emu.readRegister("FXXP").longValue() & 0xffffffffL;
            if (fxxp != 0x10L) {
                fail(String.format("maxf.s4: FXXP=0x%x expected lane0 V=0x10", fxxp));
            }
        } finally {
            emu.dispose();
        }
    }

    // fmaf.s4 w1, w2, w3: every lane evaluates 2*3+1; no enabled exception
    // means all four lanes commit (all-lane evaluation, single commit).
    private void execFmafAllLanes(ProgramDB program, Address base) throws Exception {
        Address at = base.add(0xF0);
        EmulatorHelper emu = prepareFpu(program, at, "e117c01c", "fmaf.s4");
        try {
            emu.writeRegister("w1", lanes(Float.floatToRawIntBits(2.0f),
                    Float.floatToRawIntBits(2.0f), Float.floatToRawIntBits(2.0f),
                    Float.floatToRawIntBits(2.0f)));
            emu.writeRegister("w2", lanes(Float.floatToRawIntBits(3.0f),
                    Float.floatToRawIntBits(3.0f), Float.floatToRawIntBits(3.0f),
                    Float.floatToRawIntBits(3.0f)));
            emu.writeRegister("w3", lanes(Float.floatToRawIntBits(1.0f),
                    Float.floatToRawIntBits(1.0f), Float.floatToRawIntBits(1.0f),
                    Float.floatToRawIntBits(1.0f)));
            step(emu, "fmaf.s4");
            requireWReg(emu, "fmaf.s4", "w3", new long[]{
                    Float.floatToRawIntBits(7.0f), Float.floatToRawIntBits(7.0f),
                    Float.floatToRawIntBits(7.0f), Float.floatToRawIntBits(7.0f)});
        } finally {
            emu.dispose();
        }
    }

    // fmaf.s4 with FXSR = FS|FN|RN (0x820000) and a zero addend: the
    // subnormal-product flush boundary. 2^-127 (half the minimum normal)
    // flushes UP to the minimum normal; 2^-128 flushes to +0 (the G3M
    // quarter-minimum special does not exist in the vector profile);
    // 2^-126 is the minimum normal itself (no U); 2^-124 is normal.
    private void execFmafFnBoundary(ProgramDB program, Address base) throws Exception {
        Address at = base.add(0x100);
        EmulatorHelper emu = prepareFpu(program, at, "e117c01c", "fmaf-fn");
        try {
            long e63 = 0x20000000L; // 2^-63
            long e64 = 0x1F800000L; // 2^-64
            long e62 = 0x20800000L; // 2^-62
            emu.writeRegister("FXSR", 0x820000L);
            emu.writeRegister("w1", lanes(e64, e64, e63, e62));
            emu.writeRegister("w2", lanes(e63, e64, e63, e62));
            emu.writeRegister("w3", BigInteger.ZERO);
            step(emu, "fmaf-fn");
            requireWReg(emu, "fmaf-fn", "w3",
                    new long[]{0x00800000L, 0L, 0x00800000L, 0x01800000L});
            long fxsr = emu.readRegister("FXSR").longValue() & 0xffffffffL;
            if ((fxsr & 0x1f) != 0x3) {
                fail(String.format("fmaf-fn: XP=0x%x expected U|I (0x3)",
                        fxsr & 0x1f));
            }
            long fxxp = emu.readRegister("FXXP").longValue() & 0xffffffffL;
            if (fxxp != 0x0303L) {
                fail(String.format("fmaf-fn: FXXP=0x%x expected 0x0303"
                        + " (lanes 0,1 = U|I)", fxxp));
            }
            long fxxc = emu.readRegister("FXXC").longValue() & 0xffffffffL;
            if (fxxc != 0L) {
                fail(String.format("fmaf-fn: FXXC=0x%x expected 0 (masked)", fxxc));
            }
        } finally {
            emu.dispose();
        }
    }

    // fmaf.s4 mixed NaN classes (R01UH0770 Table 3.125): S-NaN anywhere is
    // invalid with the canonical 7fffffff; a Q-NaN-only lane keeps the
    // payload with priority wreg2 > wreg1 > wreg3.
    private void execFmafMixedNaN(ProgramDB program, Address base) throws Exception {
        Address at = base.add(0x110);
        EmulatorHelper emu = prepareFpu(program, at, "e117c01c", "fmaf-nan");
        try {
            long one = Float.floatToRawIntBits(1.0f);
            long two = Float.floatToRawIntBits(2.0f);
            emu.writeRegister("FXSR", 0L);
            emu.writeRegister("w2", lanes(0x7fc00001L, 0x7fc00002L, one, one));
            emu.writeRegister("w1", lanes(0x7f800001L, one, one, two));
            emu.writeRegister("w3", lanes(one, two, 0x7fc00005L,
                    Float.floatToRawIntBits(3.0f)));
            step(emu, "fmaf-nan");
            requireWReg(emu, "fmaf-nan", "w3", new long[]{0x7fffffffL, 0x7fc00002L,
                    0x7fc00005L, Float.floatToRawIntBits(5.0f)});
            long fxsr = emu.readRegister("FXSR").longValue() & 0xffffffffL;
            if ((fxsr & 0x1f) != 0x10) {
                fail(String.format("fmaf-nan: XP=0x%x expected V (0x10)",
                        fxsr & 0x1f));
            }
            long fxxp = emu.readRegister("FXXP").longValue() & 0xffffffffL;
            if (fxxp != 0x10L) {
                fail(String.format("fmaf-nan: FXXP=0x%x expected lane0 V", fxxp));
            }
        } finally {
            emu.dispose();
        }
    }

    // cvtf.sw4 w1, w3 with FXSR.RM = 0: 1.5 rounds to 2 (per-RM, not trunc).
    private void execCvtfRmNearest(ProgramDB program, Address base) throws Exception {
        Address at = base.add(0x120);
        EmulatorHelper emu = prepareFpu(program, at, "e80fa01d", "cvtf.sw4");
        try {
            emu.writeRegister("w1", lanes(Float.floatToRawIntBits(1.5f),
                    Float.floatToRawIntBits(1.5f), Float.floatToRawIntBits(1.5f),
                    Float.floatToRawIntBits(1.5f)));
            emu.writeRegister("FXSR", BigInteger.ZERO);
            step(emu, "cvtf.sw4");
            requireWReg(emu, "cvtf.sw4", "w3", new long[]{2, 2, 2, 2});
        } finally {
            emu.dispose();
        }
    }

    // cvtf.sw4 exact / inexact / saturated lanes (G4MH p.420-421 tables):
    // 1.0 -> 1 (exact), 1.5 -> 2 (I), +-3e9 saturate to 0x7fffffff /
    // 0x80000000 (V). XP = V|I, FXXP packs per-way 0x10/0x01.
    private void execCvtfSw4Mixed(ProgramDB program, Address base) throws Exception {
        Address at = base.add(0x130);
        EmulatorHelper emu = prepareFpu(program, at, "e80fa01d", "cvtf.sw4-mixed");
        try {
            emu.writeRegister("FXSR", 0L);
            emu.writeRegister("w1", lanes(Float.floatToRawIntBits(1.0f),
                    Float.floatToRawIntBits(1.5f), Float.floatToRawIntBits(3.0e9f),
                    Float.floatToRawIntBits(-3.0e9f)));
            step(emu, "cvtf.sw4-mixed");
            requireWReg(emu, "cvtf.sw4-mixed", "w3",
                    new long[]{1L, 2L, 0x7fffffffL, 0x80000000L});
            long fxsr = emu.readRegister("FXSR").longValue() & 0xffffffffL;
            if ((fxsr & 0x1f) != 0x11) {
                fail(String.format("cvtf.sw4-mixed: XP=0x%x expected V|I (0x11)",
                        fxsr & 0x1f));
            }
            long fxxp = emu.readRegister("FXXP").longValue() & 0xffffffffL;
            if (fxxp != 0x10100100L) {
                fail(String.format("cvtf.sw4-mixed: FXXP=0x%x expected 0x10100100"
                        + " (lane0 none, lane1 I, lanes 2-3 V)", fxxp));
            }
        } finally {
            emu.dispose();
        }
    }

    // roundf.sw4 w1, w3: Q-NaN lane converts to the signed minimum 0x80000000
    // (G4MH p.468 conversion table); the 2.5 lane ties to even = 2 with I.
    private void execRoundfSw4Nan(ProgramDB program, Address base) throws Exception {
        Address at = base.add(0x140);
        EmulatorHelper emu = prepareFpu(program, at, "e00fa01d", "roundf.sw4");
        try {
            emu.writeRegister("w1", lanes(0x7fc00000L,
                    Float.floatToRawIntBits(2.5f), 0L, 0L));
            step(emu, "roundf.sw4");
            requireWReg(emu, "roundf.sw4", "w3",
                    new long[]{0x80000000L, 2L, 0, 0});
            long fxsr = emu.readRegister("FXSR").longValue() & 0xffffffffL;
            if ((fxsr & 0x1f) != 0x11) {
                fail(String.format("roundf.sw4: XP=0x%x expected V|I (0x11)",
                        fxsr & 0x1f));
            }
        } finally {
            emu.dispose();
        }
    }

    // trncf/floorf fixed-direction rounding, signed and unsigned.
    private void execTrncfFloorf(ProgramDB program, Address base) throws Exception {
        Address at = base.add(0x150);
        EmulatorHelper emu = prepareFpu(program, at, "e20fa01d", "trncf.sw4");
        try {
            // trncf.sw4: toward zero
            emu.writeRegister("FXSR", 0L);
            emu.writeRegister("w1", lanes(Float.floatToRawIntBits(1.9f),
                    Float.floatToRawIntBits(-1.9f), Float.floatToRawIntBits(2.0f),
                    Float.floatToRawIntBits(0.5f)));
            step(emu, "trncf.sw4");
            requireWReg(emu, "trncf.sw4", "w3", new long[]{1L, -1L, 2L, 0L});
            // floorf.sw4: toward -inf
            patchInstruction(program, emu, at, "e60fa01d");
            emu.writeRegister("PC", at.getOffset());
            emu.writeRegister("FXSR", 0L);
            emu.writeRegister("w1", lanes(Float.floatToRawIntBits(1.5f),
                    Float.floatToRawIntBits(-1.5f), Float.floatToRawIntBits(2.0f),
                    Float.floatToRawIntBits(0.5f)));
            step(emu, "floorf.sw4");
            requireWReg(emu, "floorf.sw4", "w3", new long[]{1L, -2L, 2L, 0L});
            // trncf.suw4: toward zero, unsigned
            patchInstruction(program, emu, at, "e30fa01d");
            emu.writeRegister("PC", at.getOffset());
            emu.writeRegister("FXSR", 0L);
            emu.writeRegister("w1", lanes(Float.floatToRawIntBits(1.9f),
                    Float.floatToRawIntBits(1.0f), Float.floatToRawIntBits(2.5f), 0L));
            step(emu, "trncf.suw4");
            requireWReg(emu, "trncf.suw4", "w3", new long[]{1L, 1L, 2L, 0L});
            long fxsr = emu.readRegister("FXSR").longValue() & 0xffffffffL;
            if ((fxsr & 0x1f) != 0x1) {
                fail(String.format("trncf.suw4: XP=0x%x expected I", fxsr & 0x1f));
            }
            // floorf.suw4: toward -inf, unsigned
            patchInstruction(program, emu, at, "e70fa01d");
            emu.writeRegister("PC", at.getOffset());
            emu.writeRegister("FXSR", 0L);
            emu.writeRegister("w1", lanes(Float.floatToRawIntBits(2.5f),
                    Float.floatToRawIntBits(0.5f), 0L, 0L));
            step(emu, "floorf.suw4");
            requireWReg(emu, "floorf.suw4", "w3", new long[]{2L, 0L, 0L, 0L});
        } finally {
            emu.dispose();
        }
    }

    // Signed CEILF accepts exactly -2^31; the next binary32 below it is
    // -(2^31 + 256), already an integer, so it remains out of range (V).
    // Unsigned CEILF of a negative normal source is invalid with result 0
    // (G4MH pp.417-419).
    private void execCeilfBoundary(ProgramDB program, Address base) throws Exception {
        Address at = base.add(0x160);
        EmulatorHelper emu = prepareFpu(program, at, "e40fa01d", "ceilf.sw4");
        try {
            emu.writeRegister("FXSR", 0L);
            emu.writeRegister("w1", lanes(0xCF000000L, 0xBE800000L,
                    Float.floatToRawIntBits(1.5f), Float.floatToRawIntBits(2.0f)));
            step(emu, "ceilf.sw4");
            requireWReg(emu, "ceilf.sw4", "w3",
                    new long[]{0x80000000L, 0L, 2L, 2L});
            long fxsr = emu.readRegister("FXSR").longValue() & 0xffffffffL;
            if ((fxsr & 0x10) != 0) {
                fail(String.format("ceilf.sw4: V raised at -2^31 boundary"
                        + " (FXSR=0x%x)", fxsr));
            }
            if ((fxsr & 0x1f) != 0x1) {
                fail(String.format("ceilf.sw4: XP=0x%x expected I only", fxsr & 0x1f));
            }
            emu.writeRegister("PC", at.getOffset());
            emu.writeRegister("FXSR", 0L);
            long one = Float.floatToRawIntBits(1.0f);
            emu.writeRegister("w1", lanes(0xCF000001L, one, one, one));
            step(emu, "ceilf.sw4-out-of-range");
            requireWReg(emu, "ceilf.sw4-out-of-range", "w3",
                    new long[]{0x80000000L, 1L, 1L, 1L});
            requireReg(emu, "ceilf.sw4-out-of-range", "FXSR", 0x10);
            // ceilf.suw4: negative source -> 0 with V
            patchInstruction(program, emu, at, "e50fa01d");
            emu.writeRegister("PC", at.getOffset());
            emu.writeRegister("FXSR", 0L);
            emu.writeRegister("w1", lanes(0xBE800000L, Float.floatToRawIntBits(0.5f),
                    Float.floatToRawIntBits(1.0f), Float.floatToRawIntBits(2.5f)));
            step(emu, "ceilf.suw4");
            requireWReg(emu, "ceilf.suw4", "w3", new long[]{0L, 1L, 1L, 3L});
            fxsr = emu.readRegister("FXSR").longValue() & 0xffffffffL;
            if ((fxsr & 0x1f) != 0x11) {
                fail(String.format("ceilf.suw4: XP=0x%x expected V|I (0x11)",
                        fxsr & 0x1f));
            }
        } finally {
            emu.dispose();
        }
    }

    // cvtf.uws4 integer lanes to float: 0xFFFFFFFF is inexact at RN (2^32)
    // but rounds down to 0x4F7FFFFF at RZ; 0x00800001 is exact.
    private void execCvtfUws4Range(ProgramDB program, Address base) throws Exception {
        Address at = base.add(0x170);
        EmulatorHelper emu = prepareFpu(program, at, "eb0fa01d", "cvtf.uws4");
        try {
            emu.writeRegister("FXSR", 0L);
            emu.writeRegister("w1", lanes(0xFFFFFFFFL, 0x00800001L, 0L, 0L));
            step(emu, "cvtf.uws4-rn");
            requireWReg(emu, "cvtf.uws4-rn", "w3",
                    new long[]{0x4F800000L, 0x4B000001L, 0L, 0L});
            long fxsr = emu.readRegister("FXSR").longValue() & 0xffffffffL;
            if ((fxsr & 0x1f) != 0x1) {
                fail(String.format("cvtf.uws4-rn: XP=0x%x expected I", fxsr & 0x1f));
            }
            // RZ rounds 2^32-1 down to the previous single
            emu.writeRegister("PC", at.getOffset());
            emu.writeRegister("FXSR", 0x40000L); // RM = RZ
            emu.writeRegister("w1", lanes(0xFFFFFFFFL, 0L, 0L, 0L));
            step(emu, "cvtf.uws4-rz");
            requireWReg(emu, "cvtf.uws4-rz", "w3",
                    new long[]{0x4F7FFFFFL, 0L, 0L, 0L});
        } finally {
            emu.dispose();
        }
    }

    // cvtf.hs4 half lanes (low 16 bits) to single: half S-NaN is invalid
    // with the canonical 7fffffff; half Q-NaN widens with the payload in
    // fraction bits 22-13; half subnormal 0x0001 widens exactly to 2^-24;
    // 0x3C00 is 1.0 (R01UH0770 Table 3.126).
    private void execCvtfHs4(ProgramDB program, Address base) throws Exception {
        Address at = base.add(0x1D0);
        EmulatorHelper emu = prepareFpu(program, at, "ec0fa01d", "cvtf.hs4");
        try {
            emu.writeRegister("FXSR", 0L);
            emu.writeRegister("w1", lanes(0x00007D01L, 0x00007E00L,
                    0x00000001L, 0x00003C00L));
            step(emu, "cvtf.hs4");
            requireWReg(emu, "cvtf.hs4", "w3", new long[]{0x7fffffffL, 0x7FC00000L,
                    0x33800000L, 0x3F800000L});
            long fxsr = emu.readRegister("FXSR").longValue() & 0xffffffffL;
            if ((fxsr & 0x1f) != 0x10) {
                fail(String.format("cvtf.hs4: XP=0x%x expected V (0x10)",
                        fxsr & 0x1f));
            }
        } finally {
            emu.dispose();
        }
    }

    // cvtf.sh4 single lanes to half: 1.0 exact; 65519 (above the half max
    // 65504 but under the RN overflow threshold 65520) rounds to 0x7BFF
    // inexact with NO overflow; 65536 overflows to +inf with O|I; a single
    // Q-NaN keeps sign+top-ten payload bits; a single S-NaN is invalid
    // with 0x7FFF (Table 3.126).
    private void execCvtfSh4(ProgramDB program, Address base) throws Exception {
        Address at = base.add(0x1E0);
        EmulatorHelper emu = prepareFpu(program, at, "ed0fa01d", "cvtf.sh4");
        try {
            emu.writeRegister("FXSR", 0L);
            emu.writeRegister("w1", lanes(Float.floatToRawIntBits(1.0f),
                    Float.floatToRawIntBits(65519.0f), Float.floatToRawIntBits(65536.0f),
                    0x7FC00001L));
            step(emu, "cvtf.sh4-below");
            requireWReg(emu, "cvtf.sh4-below", "w3", new long[]{0x3C00L, 0x7BFFL,
                    0x7C00L, 0x7E00L});
            long fxsr = emu.readRegister("FXSR").longValue() & 0xffffffffL;
            if ((fxsr & 0x1f) != 0x5) {
                fail(String.format("cvtf.sh4-below: XP=0x%x expected O|I (0x5)",
                        fxsr & 0x1f));
            }
            long fxxp = emu.readRegister("FXXP").longValue() & 0xffffffffL;
            if (fxxp != 0x050100L) {
                fail(String.format("cvtf.sh4-below: FXXP=0x%x expected 0x050100"
                        + " (lane1 I, lane2 O|I)", fxxp));
            }
            // single S-NaN -> half 0x7FFF with V
            emu.writeRegister("PC", at.getOffset());
            emu.writeRegister("FXSR", 0L);
            emu.writeRegister("w1", lanes(0x7F800001L, 0x80000000L, 0L, 0L));
            step(emu, "cvtf.sh4-snan");
            requireWReg(emu, "cvtf.sh4-snan", "w3",
                    new long[]{0x7FFFL, 0x8000L, 0L, 0L});
            fxsr = emu.readRegister("FXSR").longValue() & 0xffffffffL;
            if ((fxsr & 0x1f) != 0x10) {
                fail(String.format("cvtf.sh4-snan: XP=0x%x expected V (0x10)",
                        fxsr & 0x1f));
            }
            emu.writeRegister("PC", at.getOffset());
            emu.writeRegister("FXSR", 0x20000L);
            emu.writeRegister("FXXP", 0L);
            emu.writeRegister("w1", lanes(1L, 0x80000001L, 0L, 0x80000000L));
            step(emu, "cvtf.sh4-flushed-zero");
            requireWReg(emu, "cvtf.sh4-flushed-zero", "w3",
                    new long[]{0L, 0x8000L, 0L, 0x8000L});
            requireReg(emu, "cvtf.sh4-flushed-zero", "FXSR", 0x420001);
            requireReg(emu, "cvtf.sh4-flushed-zero", "FXXP", 0x101);
        } finally {
            emu.dispose();
        }
    }

    // recipf.s4 of +0 is a DIVF.S4 lane with dividend 1.0: +inf with the
    // zero-divide cause Z (R01UH0770 3.2.6.2(10)(d)); sqrtf.s4 of -4 is
    // invalid with the canonical 7fffffff. Inputs are deliberately
    // architecture-exact: G4MH documents RECIPF/RSQRTF as ~1-2 ULP hardware
    // approximations for general inputs, which this model does not
    // implement, so fixtures only pin exact cases (zero-divide, invalid,
    // and power-of-two inputs like 4.0 where 1/4 and sqrt(4) are exact).
    private void execSqrtfRecipf(ProgramDB program, Address base) throws Exception {
        Address at = base.add(0x1F0);
        EmulatorHelper emu = prepareFpu(program, at, "f30fa01d", "recipf.s4");
        try {
            long four = Float.floatToRawIntBits(4.0f);
            emu.writeRegister("FXSR", 0L);
            emu.writeRegister("w1", lanes(0L, four, four, four));
            step(emu, "recipf.s4");
            long quarter = Float.floatToRawIntBits(0.25f);
            long inf = 0x7f800000L;
            requireWReg(emu, "recipf.s4", "w3", new long[]{inf, quarter, quarter,
                    quarter});
            long fxsr = emu.readRegister("FXSR").longValue() & 0xffffffffL;
            if ((fxsr & 0x1f) != 0x8) {
                fail(String.format("recipf.s4: XP=0x%x expected Z (0x8)",
                        fxsr & 0x1f));
            }
            long fxxp = emu.readRegister("FXXP").longValue() & 0xffffffffL;
            if (fxxp != 0x8L) {
                fail(String.format("recipf.s4: FXXP=0x%x expected lane0 Z", fxxp));
            }
            // sqrtf.s4 of -4: invalid, canonical NaN
            patchInstruction(program, emu, at, "f20fa01d");
            emu.writeRegister("PC", at.getOffset());
            emu.writeRegister("FXSR", 0L);
            long neg4 = Float.floatToRawIntBits(-4.0f);
            emu.writeRegister("w1", lanes(neg4, four, four, four));
            step(emu, "sqrtf.s4");
            long two = Float.floatToRawIntBits(2.0f);
            requireWReg(emu, "sqrtf.s4", "w3", new long[]{0x7fffffffL, two, two,
                    two});
            fxsr = emu.readRegister("FXSR").longValue() & 0xffffffffL;
            if ((fxsr & 0x1f) != 0x10) {
                fail(String.format("sqrtf.s4: XP=0x%x expected V (0x10)",
                        fxsr & 0x1f));
            }
        } finally {
            emu.dispose();
        }
    }

    // Butterfly family, straight from the G4MH [Operation] blocks:
    // ADDSUBF.S4 (p.395) subtracts in the even lanes (w0=w2[0]-w1[0],
    // w2=w2[2]-w1[2]) and adds in the odd lanes; ADDSUBNXF.S4 applies the
    // same op pattern to crossed wreg1 lanes (w0 uses w1[1], w1 uses w1[0],
    // w2 uses w1[3], w3 uses w1[2]) and negates; ADDSUBNF.S4 negates the
    // ADDSUBF results, but a NaN result keeps the Table 3.125 value with
    // its sign bit untouched.
    private void execButterfly(ProgramDB program, Address base) throws Exception {
        Address at = base.add(0x230);
        EmulatorHelper emu = prepareFpu(program, at, "e117d01d", "addsubf.s4");
        try {
            long a1 = Float.floatToRawIntBits(1.0f);
            long a2 = Float.floatToRawIntBits(2.0f);
            long a4 = Float.floatToRawIntBits(4.0f);
            long a8 = Float.floatToRawIntBits(8.0f);
            long b16 = Float.floatToRawIntBits(16.0f);
            long b32 = Float.floatToRawIntBits(32.0f);
            long b64 = Float.floatToRawIntBits(64.0f);
            long b128 = Float.floatToRawIntBits(128.0f);
            emu.writeRegister("FXSR", 0L);
            emu.writeRegister("w1", lanes(a1, a2, a4, a8));
            emu.writeRegister("w2", lanes(b16, b32, b64, b128));
            step(emu, "addsubf.s4");
            // even lanes: 16-1, 64-4; odd lanes: 32+2, 128+8
            requireWReg(emu, "addsubf.s4", "w3", new long[]{
                    Float.floatToRawIntBits(15.0f), Float.floatToRawIntBits(34.0f),
                    Float.floatToRawIntBits(60.0f), Float.floatToRawIntBits(136.0f)});
            // addsubnxf.s4: crossed + negated
            patchInstruction(program, emu, at, "e117dc1d");
            emu.writeRegister("PC", at.getOffset());
            emu.writeRegister("FXSR", 0L);
            step(emu, "addsubnxf.s4");
            // neg(16-2), neg(32+1), neg(64-8), neg(128+4)
            requireWReg(emu, "addsubnxf.s4", "w3", new long[]{
                    Float.floatToRawIntBits(-14.0f), Float.floatToRawIntBits(-33.0f),
                    Float.floatToRawIntBits(-56.0f), Float.floatToRawIntBits(-132.0f)});
            // addsubnf.s4: an S-NaN lane produces the canonical 7fffffff
            // (V) and the N-negation must NOT flip its sign bit
            patchInstruction(program, emu, at, "e117d81d");
            emu.writeRegister("PC", at.getOffset());
            emu.writeRegister("FXSR", 0L);
            emu.writeRegister("w1", lanes(a1, 0x7f800001L, a4, a8));
            step(emu, "addsubnf.s4");
            requireWReg(emu, "addsubnf.s4", "w3", new long[]{
                    Float.floatToRawIntBits(-15.0f), 0x7fffffffL,
                    Float.floatToRawIntBits(-60.0f), Float.floatToRawIntBits(-136.0f)});
            long fxsr = emu.readRegister("FXSR").longValue() & 0xffffffffL;
            if ((fxsr & 0x1f) != 0x10) {
                fail(String.format("addsubnf.s4: XP=0x%x expected V (0x10)",
                        fxsr & 0x1f));
            }
            long fxxp = emu.readRegister("FXXP").longValue() & 0xffffffffL;
            if (fxxp != 0x1000L) {
                fail(String.format("addsubnf.s4: FXXP=0x%x expected lane1 V"
                        + " (0x1000)", fxxp));
            }
        } finally {
            emu.dispose();
        }
    }

    // addxf.s4 w1, w2, w1 (destination aliases wreg1): crossed lanes must all
    // read the ORIGINAL register contents.
    private void execAddxfAliased(ProgramDB program, Address base) throws Exception {
        Address at = base.add(0x200);
        EmulatorHelper emu = prepareFpu(program, at, "e117c40d", "addxf.s4");
        try {
            emu.writeRegister("w1", lanes(Float.floatToRawIntBits(1.0f),
                    Float.floatToRawIntBits(2.0f), Float.floatToRawIntBits(3.0f),
                    Float.floatToRawIntBits(4.0f)));
            emu.writeRegister("w2", lanes(Float.floatToRawIntBits(10.0f),
                    Float.floatToRawIntBits(20.0f), Float.floatToRawIntBits(30.0f),
                    Float.floatToRawIntBits(40.0f)));
            step(emu, "addxf.s4");
            requireWReg(emu, "addxf.s4 alias", "w1", new long[]{
                    Float.floatToRawIntBits(12.0f), Float.floatToRawIntBits(21.0f),
                    Float.floatToRawIntBits(34.0f), Float.floatToRawIntBits(43.0f)});
        } finally {
            emu.dispose();
        }
    }

    // pushsp r4, r6 then popsp r4, r6: real memory burst + SP movement.
    private void execPushspPopsp(ProgramDB program, Address base) throws Exception {
        Address at = base.add(0x210);
        if (program.getMemory().getBlock("pushsp") == null) {
            program.getMemory().createInitializedBlock("pushsp",
                    program.getAddressFactory().getDefaultAddressSpace().getAddress(0x2F00),
                    new ByteArrayInputStream(new byte[0x100]), 0x100, monitor, false);
        }
        // Range r4..r6 excludes sp (r3).
        EmulatorHelper emu = prepare(program, at, "e4476031", "pushsp");
        try {
            emu.writeRegister("gp", 0x44);
            emu.writeRegister("tp", 0x55);
            emu.writeRegister("r6", 0x66);
            emu.writeRegister("sp", 0x3000);
            step(emu, "pushsp");
            requireReg(emu, "pushsp sp", "sp", 0x2FF4);
            requireMem(emu, "pushsp [0x2FFC]", 0x2FFC, 0x44);
            requireMem(emu, "pushsp [0x2FF8]", 0x2FF8, 0x55);
            requireMem(emu, "pushsp [0x2FF4]", 0x2FF4, 0x66);
            patchInstruction(program, emu, at, "e4676031");
            emu.writeRegister("gp", 0);
            emu.writeRegister("tp", 0);
            emu.writeRegister("r6", 0);
            emu.writeRegister("PC", at.getOffset());
            step(emu, "popsp");
            requireReg(emu, "popsp sp", "sp", 0x3000);
            requireReg(emu, "popsp r4", "gp", 0x44);
            requireReg(emu, "popsp r5", "tp", 0x55);
            requireReg(emu, "popsp r6", "r6", 0x66);
        } finally {
            emu.dispose();
        }
    }

    // stsr FXSR, r5 / ldsr r6, FXSR through the real selID-10 selector
    // encoding (SR6,10 per R01UH0770 Table 3.54). Reads are canonicalized
    // (bit 21 reads 1) and writes keep only the writable FXSR fields.
    private void execLdsrStsrFxsr(ProgramDB program, Address base) throws Exception {
        Address at = base.add(0x220);
        // stsr SR6,10: word1 = 0x07E0|6|5<<11 = 0x2FE6; word2 = selID10|0x40
        EmulatorHelper emu = prepareFpu(program, at, "e62f4050", "stsr");
        try {
            emu.writeRegister("FXSR", BigInteger.valueOf(0x000A0000));
            emu.writeRegister("tp", 0);
            step(emu, "stsr FXSR");
            requireReg(emu, "stsr FXSR", "tp", 0x002A0000);
            // ldsr SR6,10: word1 = 0x07E0|6|6<<11 = 0x37E6; word2 = selID10|0x20
            patchInstruction(program, emu, at, "e6372050");
            emu.writeRegister("r6", 0x000C0000);
            emu.writeRegister("PC", at.getOffset());
            step(emu, "ldsr FXSR");
            requireReg(emu, "ldsr FXSR", "FXSR", 0x002C0000);
        } finally {
            emu.dispose();
        }
    }

    // Negative sign-extended disp16 with nonzero masked low bits (G4MH
    // 2.5.4.27/2.5.4.28/2.5.4.48: the low 4/2/3 displacement bits operate
    // as if 0). ldv.qw 0xF00D[r6] lands at 0x8000 (nibble D ignored),
    // stv.w stores lane 1 of w6 at 0x8004 (bits 3 ignored, neighbor words
    // untouched), and ldv.dw imm2=2 broadcasts the double word at 0x8020
    // into the HIGH half of w7 only; the unselected low half keeps its
    // original value (2.5.4.27 [Operation]: imm2[1] selects dw1).
    private void execLdvStvNegativeDisp(ProgramDB program, Address base) throws Exception {
        Address at = base.add(0x240);
        Address stvAt = base.add(0x248);
        Address dwAt = base.add(0x250);
        program.getMemory().setBytes(at, bytes("a6079d2a0df0"));
        program.getMemory().setBytes(stvAt, bytes("a7073d3203f0"));
        program.getMemory().setBytes(dwAt, bytes("a8075d3b0bf0"));
        PseudoDisassembler decoder = new PseudoDisassembler(program);
        if (decoder.disassemble(at) == null || decoder.disassemble(stvAt) == null
                || decoder.disassemble(dwAt) == null) {
            fail("ldv/stv: negative-displacement fixtures not decoded");
        }
        EmulatorHelper emu = new EmulatorHelper(program);
        try {
            emu.writeRegister("PSW", PSW_CU1);
            Address data = program.getAddressFactory().getDefaultAddressSpace()
                    .getAddress(0x8000);
            emu.writeMemory(data, bytes("101112131415161718191a1b1c1d1e1f"));
            emu.writeRegister("PC", at.getOffset());
            emu.writeRegister("r6", 0x9000);
            step(emu, "ldv.qw-neg");
            requireWReg(emu, "ldv.qw-neg", "w5",
                    new long[]{0x13121110, 0x17161514, 0x1B1A1918, 0x1F1E1D1C});
            // stv.w 1, w6, 0xF003[r7]: 0x9004 + sext(0xF003 & ~3) = 0x8004
            emu.writeMemory(data, bytes("aaaaaaaa"));
            emu.writeMemory(data.add(4), bytes("78563412"));
            emu.writeMemory(data.add(8), bytes("bbbbbbbb"));
            emu.writeRegister("w6",
                    lanes(0x11223344, 0x55667788, 0x99AABBCC, 0xDDEEFF00));
            emu.writeRegister("PC", stvAt.getOffset());
            emu.writeRegister("r7", 0x9004);
            step(emu, "stv.w-neg");
            requireMem(emu, "stv.w-neg [0x8004]", 0x8004, 0x55667788);
            requireMem(emu, "stv.w-neg [0x8000]", 0x8000, 0xAAAAAAAA);
            requireMem(emu, "stv.w-neg [0x8008]", 0x8008, 0xBBBBBBBB);
            // ldv.dw 2, 0xF00B[r8], w7: 0x9018 + sext(0xF00B & ~7) = 0x8020
            emu.writeMemory(data.add(0x20), bytes("1122334455667788"));
            emu.writeRegister("w7",
                    lanes(0x01010101, 0x02020202, 0x03030303, 0x04040404));
            emu.writeRegister("PC", dwAt.getOffset());
            emu.writeRegister("r8", 0x9018);
            step(emu, "ldv.dw-neg");
            requireWReg(emu, "ldv.dw-neg", "w7",
                    new long[]{0x01010101, 0x02020202, 0x44332211, 0x88776655});
        } finally {
            emu.dispose();
        }
    }

    // vshufl.b r5, v3, v3: source equals destination; the eight 3-bit
    // selectors in r5 (7,6,5,4,3,2,1,0 = 0x53977) reverse the byte order
    // using the ORIGINAL register contents.
    private void execVshuflAliased(ProgramDB program, Address base) throws Exception {
        Address at = base.add(0x258);
        EmulatorHelper emu = prepare(program, at, "e51fae1e", "vshufl.b");
        try {
            emu.writeRegister("tp", 0x00053977L);
            emu.writeRegister("v3", BigInteger.valueOf(0x8070605040302010L));
            step(emu, "vshufl.b");
            requireWReg(emu, "vshufl.b", "v3",
                    new long[]{0x50607080L, 0x10203040L});
        } finally {
            emu.dispose();
        }
    }

    // Scalar ROUNDF.DW/DUW edges (R01US0209 2.4.4.63/2.4.4.64, pp.344/346):
    // nearest-ties-even regardless of the rounding mode, and an invalid
    // ROUNDED result returns the range extreme. 2^31-0.5 and 2^32-0.5 are
    // exact doubles whose tie rounds up across the limit (the integers
    // below both limits are odd), so DW saturates to 0x7fffffff and DUW to
    // 0xffffffff; NaN returns the signed minimum for DW and 0 for DUW.
    // Destinations tp/r6 are never r0. Invalid supersedes inexact; XP is sticky.
    private void execRoundfDoubleWord(ProgramDB program, Address base) throws Exception {
        Address at = base.add(0x260);
        // roundf.dw r2:r3, r5 / roundf.duw r2:r3, r6
        EmulatorHelper emu = prepare(program, at, "e017502c", "roundf.dw");
        try {
            emu.writeRegister("r2sp", Double.doubleToLongBits(2147483647.5d));
            emu.writeRegister("tp", 0xDEADBEEFL);
            step(emu, "roundf.dw-limit");
            requireReg(emu, "roundf.dw-limit", "tp", 0x7fffffff);
            requireReg(emu, "roundf.dw-limit", "FPSR", 0x10);
            patchInstruction(program, emu, at, "f0175034");
            emu.writeRegister("PC", at.getOffset());
            emu.writeRegister("r2sp", Double.doubleToLongBits(4294967295.5d));
            emu.writeRegister("r6", 0xDEADBEEFL);
            step(emu, "roundf.duw-limit");
            requireReg(emu, "roundf.duw-limit", "r6", 0xffffffff);
            requireReg(emu, "roundf.duw-limit", "FPSR", 0x10);
            patchInstruction(program, emu, at, "e017502c");
            double[] ties = {2.5d, -2.5d, 3.5d, -3.5d};
            long[] tieResults = {2, 0xfffffffeL, 4, 0xfffffffcL};
            for (int i = 0; i < ties.length; i++) {
                emu.writeRegister("PC", at.getOffset());
                emu.writeRegister("r2sp", Double.doubleToLongBits(ties[i]));
                emu.writeRegister("tp", 0xDEADBEEFL);
                step(emu, "roundf.dw-tie");
                requireReg(emu, "roundf.dw-tie", "tp", tieResults[i]);
                requireReg(emu, "roundf.dw-tie", "FPSR", 0x11);
            }
            emu.writeRegister("PC", at.getOffset());
            emu.writeRegister("r2sp", Double.doubleToLongBits(Double.NaN));
            emu.writeRegister("tp", 0xDEADBEEFL);
            step(emu, "roundf.dw-nan");
            requireReg(emu, "roundf.dw-nan", "tp", 0x80000000);
            requireReg(emu, "roundf.dw-nan", "FPSR", 0x11);
            patchInstruction(program, emu, at, "f0175034");
            emu.writeRegister("PC", at.getOffset());
            emu.writeRegister("r2sp", Double.doubleToLongBits(Double.NaN));
            emu.writeRegister("r6", 0xDEADBEEFL);
            step(emu, "roundf.duw-nan");
            requireReg(emu, "roundf.duw-nan", "r6", 0);
            requireReg(emu, "roundf.duw-nan", "FPSR", 0x11);
        } finally {
            emu.dispose();
        }
    }
    private void execRoundfExceptionStates(ProgramDB program, Address base) throws Exception {
        Address at = base.add(0x280);
        EmulatorHelper emu = prepare(program, at, "e017502c", "roundf-states");
        try {
            // A fractional source below INT_MIN can still round IN range.
            emu.writeRegister("r2sp", Double.doubleToLongBits(-2147483648.25d));
            step(emu, "roundf-low-fraction");
            requireReg(emu, "roundf-low-fraction", "tp", 0x80000000L);
            requireReg(emu, "roundf-low-fraction", "FPSR", 1);
            // Unsigned 64-bit high-half conversion must not use signed truncation.
            patchInstruction(program, emu, at, "f0175464");
            emu.writeRegister("PC", at.getOffset());
            emu.writeRegister("FPSR", 0);
            emu.writeRegister("r2sp", 0x43e0000000000001L);
            step(emu, "roundf-unsigned-high");
            requireReg(emu, "roundf-unsigned-high", "r12", 0x800);
            requireReg(emu, "roundf-unsigned-high", "r13", 0x80000000L);
            requireReg(emu, "roundf-unsigned-high", "FPSR", 0);
            // Enabled V suppresses BOTH result words and records the source PC.
            emu.writeRegister("PC", at.getOffset());
            emu.writeRegister("FPSR", 0x00200201);
            emu.writeRegister("RBASE", 0);
            emu.writeRegister("PSW", 0x10000);
            emu.writeRegister("r2sp", Double.doubleToLongBits(Double.NaN));
            emu.writeRegister("r12", 0x12345678);
            emu.writeRegister("r13", 0x23456789);
            step(emu, "roundf-enabled-invalid");
            requireReg(emu, "roundf-enabled-invalid", "r12", 0x12345678);
            requireReg(emu, "roundf-enabled-invalid", "r13", 0x23456789);
            requireReg(emu, "roundf-enabled-invalid", "FPEPC", at.getOffset());
            requireReg(emu, "roundf-enabled-invalid", "FPSR", 0x00204201);
            requireReg(emu, "roundf-enabled-invalid", "EIPC", at.getOffset());
            requireReg(emu, "roundf-enabled-invalid", "EIPSW", 0x10000);
            requireReg(emu, "roundf-enabled-invalid", "EIIC", 0x71);
            requireReg(emu, "roundf-enabled-invalid", "PC", 0x70);
        } finally {
            emu.dispose();
        }
    }



}
