//@author kaikozlov
//@category Verification
// Behavioral fixtures for the extended FX register file and the indexed MPU
// descriptor state of the broad RH850 language (v850e3x), all driven through
// real opcode consumers (LDSR/STSR selID 10 and selID 5, LDM.MP/STM.MP):
//   - bidirectional FXST/FXCFG views over canonical FXSR preserving every
//     unrelated field across writes (R01UH0770EJ0121 Tables 3.55-3.58),
//   - distinct indexed MPU regions (including the 24-31 entries of the
//     G4MH virtualization profile) round-tripping independently, bank
//     selection through the real MPBK selector (SR17,5): invalid bank
//     writes preserve the selected bank, MPIDX untouched by the bursts,
//   - access-permission faults before side effects: FE-level UCPOP
//     (cause 81H/vector 80H) for CU1-disabled selID-10 access, FE-level PIE
//     (cause A0H/vector A0H) for user-mode FXSR/MPU access, with FEPC,
//     updated PSW bits, handler target, and destination registers verified,
//   - ordinary multi-register PUSHSP/POPSP round-trips (rt at the lowest
//     address, descending POPSP order) and the architecturally constant r0
//     (PUSHSP stores literal 0, POPSP discards the load).
// Emits "ASSERT v850-extended-registers: passed" and throws on any failure.
// Run from the verification harness alongside AssertV850ExtendedIsa.
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

public class AssertV850ExtendedRegisters extends GhidraScript {
    private static final String LANGUAGE_ID = "v850e3x:LE:32:default";

    // PSW bits (R01UH0770EJ0121 Table 3.14)
    private static final long PSW_UM = 0x40000000L;
    private static final long PSW_CU1 = 0x00020000L;
    private static final long PSW_EXC_BITS = 0x000000E0L; // NP|EP|ID

    // LDSR r1, regID, selID:  w1 = (regID<<11)|0x07E0|1, w2 = (selID<<11)|0x20
    // STSR regID, r5, selID:  w1 = (5<<11)|0x07E0|regID, w2 = (selID<<11)|0x40
    private static final String LDSR_FXSR = "e1372050";
    private static final String STSR_FXSR = "e62f4050";
    private static final String LDSR_FXST = "e1472050";
    private static final String STSR_FXST = "e82f4050";
    private static final String LDSR_FXINFO = "e14f2050";
    private static final String STSR_FXINFO = "e92f4050";
    private static final String LDSR_FXCFG = "e1572050";
    private static final String STSR_FXCFG = "ea2f4050";
    private static final String LDSR_FXXC = "e1672050";
    private static final String STSR_FXXC = "ec2f4050";
    private static final String LDSR_FXXP = "e16f2050";
    private static final String STSR_FXXP = "ed2f4050";
    private static final String LDSR_MPIDX = "e1872028";
    private static final String STSR_MPIDX = "f02f4028";
    private static final String LDSR_MPBK = "e18f2028";
    private static final String STSR_MPBK = "f12f4028";
    private static final String LDSR_MPLA = "e1a72028";
    private static final String STSR_MPLA = "f42f4028";
    private static final String LDSR_MPUA = "e1af2028";
    private static final String STSR_MPUA = "f52f4028";
    private static final String LDSR_MPAT = "e1b72028";
    private static final String STSR_MPAT = "f62f4028";
    // ldm.mp [r2], eh-et:  w1 = (eh<<11)|0x07E0|2, w2 = (et<<11)|0x166
    // stm.mp eh-et, [r2]:  w1 = (eh<<11)|0x07E0|2, w2 = (et<<11)|0x164
    private static final String LDM_MP_2_3 = "e2176619";
    private static final String STM_MP_2_3 = "e2176419";
    private static final String LDM_MP_5_5 = "e22f6629";
    private static final String STM_MP_5_5 = "e22f6429";

    private int fixtures;

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

    private static String words(long... values) {
        StringBuilder sb = new StringBuilder();
        for (long v : values) {
            for (int b = 0; b < 4; b++) {
                sb.append(String.format("%02x", (v >>> (8 * b)) & 0xffL));
            }
        }
        return sb.toString();
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
        ProgramDB program = new ProgramDB("v850-extended-registers", language,
                language.getDefaultCompilerSpec(), this);
        int tx = program.startTransaction("extended register fixtures");
        try {
            Address base = program.getAddressFactory().getDefaultAddressSpace()
                    .getAddress(0x1000);
            program.getMemory().createInitializedBlock("code", base,
                    new ByteArrayInputStream(new byte[0x1000]), 0x1000, monitor, false);
            program.getMemory().createInitializedBlock("data",
                    program.getAddressFactory().getDefaultAddressSpace().getAddress(0x8000),
                    new ByteArrayInputStream(new byte[0x400]), 0x400, monitor, false);

            execFxsrCanonical(program, base);
            execFxstViewPreservesUnrelated(program, base);
            execFxcfgViewPreservesUnrelated(program, base);
            execFxinfoReadOnly(program, base);
            execFxxIndependent(program, base);
            execMpuRegionsRoundtrip(program, base);
            execMpuBankIsolation(program, base);
            execMpuBurstRegionsAndMpidx(program, base);
            execFxPermissionUcpop(program, base);
            execFxPermissionFxsrPie(program, base);
            execFxPermissionUcpopBeforeUm(program, base);
            execMpuPermissionPie(program, base);
            execPushPopRoundtrip(program, base);
            execPushPopR0Constant(program, base);
        } finally {
            program.endTransaction(tx, false);
            program.release(this);
        }
        println("ASSERT v850-extended-registers: passed (fixtures=" + fixtures + ")");
    }

    private EmulatorHelper prepare(ProgramDB program, Address at, String hexBytes,
            String label) throws Exception {
        program.getMemory().setBytes(at, bytes(hexBytes));
        PseudoInstruction instruction = new PseudoDisassembler(program).disassemble(at);
        if (instruction == null) {
            fail(label + ": fixture bytes not decoded: " + hexBytes);
        }
        EmulatorHelper emu = new EmulatorHelper(program);
        emu.writeRegister("PC", at.getOffset());
        emu.writeRegister("PSW", PSW_CU1);
        emu.writeRegister("HVCFG", 0);
        emu.writeRegister("RBASE", 0);
        emu.writeRegister("EBASE", 0);
        emu.writeRegister("FXSR", 0);
        emu.writeRegister("FXXC", 0);
        emu.writeRegister("FXXP", 0);
        emu.writeRegister("MPBK", 0);
        emu.writeRegister("MPIDX", 0);
        return emu;
    }

    // Re-run one instruction in an emulator session: patch the code bytes,
    // reset PC, execute a single step.
    private void again(ProgramDB program, EmulatorHelper emu, Address at, String hexBytes,
            String label) throws Exception {
        program.getMemory().setBytes(at, bytes(hexBytes));
        new PseudoDisassembler(program).disassemble(at);
        emu.writeMemory(at, bytes(hexBytes));
        emu.getEmulator().setContextRegisterValue(
                emu.getEmulator().getContextRegisterValue());
        emu.writeRegister("PC", at.getOffset());
        step(emu, label);
    }

    // Execute one instruction at an auxiliary slot (at+4) inside an
    // emulator session, e.g. seeding MPIDX/MPBK through machine LDSR
    // instead of synthetic register writes.
    private void execAt(ProgramDB program, EmulatorHelper emu, Address aux, String hexBytes,
            String label) throws Exception {
        program.getMemory().setBytes(aux, bytes(hexBytes));
        new PseudoDisassembler(program).disassemble(aux);
        emu.writeMemory(aux, bytes(hexBytes));
        emu.getEmulator().setContextRegisterValue(
                emu.getEmulator().getContextRegisterValue());
        emu.writeRegister("PC", aux.getOffset());
        step(emu, label);
    }

    private void step(EmulatorHelper emu, String label) throws Exception {
        if (!emu.step(monitor)) {
            fail(label + ": emulator step failed: " + emu.getLastError());
        }
    }

    private void requireReg(EmulatorHelper emu, String label, String reg, long expected) {
        long actual = emu.readRegister(reg).longValue() & 0xffffffffL;
        if (actual != (expected & 0xffffffffL)) {
            fail(String.format("%s: %s=0x%x expected=0x%x", label, reg, actual, expected));
        }
    }

    private void requireMem(EmulatorHelper emu, String label, long addr, long expected)
            throws Exception {
        byte[] raw = emu.readMemory(emu.getLanguage().getAddressFactory()
                .getDefaultAddressSpace().getAddress(addr), 4);
        long got = (raw[0] & 0xffL) | ((raw[1] & 0xffL) << 8)
                | ((raw[2] & 0xffL) << 16) | ((raw[3] & 0xffL) << 24);
        if (got != (expected & 0xffffffffL)) {
            fail(label + " expected mem " + Long.toHexString(addr) + "="
                    + Integer.toHexString((int) expected) + " got " + Long.toHexString(got));
        }
    }

    // Assert an FE-level permission fault: FEIC cause, FEPC = faulting
    // instruction, PSW exception bits set with UM cleared, control at the
    // RBASE-derived vector, and the destination register untouched.
    private void requireFeFault(EmulatorHelper emu, String label, Address at, long cause,
            long vector, String destReg, long destExpected) {
        requireReg(emu, label, "FEIC", cause);
        requireReg(emu, label, "FEPC", at.getOffset());
        long psw = emu.readRegister("PSW").longValue() & 0xffffffffL;
        if ((psw & PSW_EXC_BITS) != PSW_EXC_BITS) {
            fail(label + ": PSW NP|EP|ID not all set: " + Long.toHexString(psw));
        }
        if ((psw & PSW_UM) != 0) {
            fail(label + ": PSW.UM not cleared: " + Long.toHexString(psw));
        }
        requireReg(emu, label, "PC", vector);
        if (destReg != null) {
            requireReg(emu, label, destReg, destExpected);
        }
    }

    // FXSR keeps its canonical form through both selID-10 directions
    // (Table 3.55: bit 21 reads 1, reserved bits 0).
    private void execFxsrCanonical(ProgramDB program, Address base) throws Exception {
        Address at = base.add(0x20 * (++fixtures));
        EmulatorHelper emu = prepare(program, at, LDSR_FXSR, "fxsr-canonical");
        try {
            emu.writeRegister("PSW", PSW_CU1);
            emu.writeRegister("r1", 0xffffffffL);
            step(emu, "fxsr-canonical");
            requireReg(emu, "fxsr-canonical", "FXSR", 0x00eeffffL);
            again(program, emu, at, STSR_FXSR, "fxsr-canonical");
            requireReg(emu, "fxsr-canonical", "tp", 0x00eeffffL);
        } finally {
            emu.dispose();
        }
    }

    // FXST writes update only XC/IF/XP in FXSR; FN/RM/FS/bit21 survive.
    private void execFxstViewPreservesUnrelated(ProgramDB program, Address base)
            throws Exception {
        Address at = base.add(0x20 * (++fixtures));
        EmulatorHelper emu = prepare(program, at, LDSR_FXSR, "fxst-view");
        try {
            emu.writeRegister("PSW", PSW_CU1);
            emu.writeRegister("r1", 0x008effffL); // FN=1 RM=3 FS=1 XC=0x3f XE=0x1f XP=0x1f
            step(emu, "fxst-view");
            requireReg(emu, "fxst-view", "FXSR", 0x00aeffffL);
            emu.writeRegister("r1", 0x0000003aL); // XC=0 IF=1 XP=0x1a
            again(program, emu, at, LDSR_FXST, "fxst-view");
            // FN23 RM[19:18] FS17 bit21 XE[9:5] survive; XC cleared, IF/XP replaced.
            requireReg(emu, "fxst-view", "FXSR", 0x00ee03faL);
            again(program, emu, at, STSR_FXST, "fxst-view");
            requireReg(emu, "fxst-view", "tp", 0x0000003aL);
        } finally {
            emu.dispose();
        }
    }

    // FXCFG writes update only RM/XE in FXSR; XC/IF/XP survive.
    private void execFxcfgViewPreservesUnrelated(ProgramDB program, Address base)
            throws Exception {
        Address at = base.add(0x20 * (++fixtures));
        EmulatorHelper emu = prepare(program, at, LDSR_FXSR, "fxcfg-view");
        try {
            emu.writeRegister("PSW", PSW_CU1);
            emu.writeRegister("r1", 0x0040a815L); // IF=1 XC=0x2a XP=0x15
            step(emu, "fxcfg-view");
            requireReg(emu, "fxcfg-view", "FXSR", 0x0060a815L);
            emu.writeRegister("r1", 0x0000020fL); // RM=2 XE=0xf
            again(program, emu, at, LDSR_FXCFG, "fxcfg-view");
            requireReg(emu, "fxcfg-view", "FXSR", 0x0068a9f5L);
            again(program, emu, at, STSR_FXCFG, "fxcfg-view");
            requireReg(emu, "fxcfg-view", "tp", 0x0000020fL);
        } finally {
            emu.dispose();
        }
    }

    // FXINFO reads 3 (NFPU=1 RSIZE=1) and ignores writes.
    private void execFxinfoReadOnly(ProgramDB program, Address base) throws Exception {
        Address at = base.add(0x20 * (++fixtures));
        EmulatorHelper emu = prepare(program, at, STSR_FXINFO, "fxinfo-ro");
        try {
            emu.writeRegister("PSW", PSW_CU1);
            step(emu, "fxinfo-ro");
            requireReg(emu, "fxinfo-ro", "tp", 3);
            emu.writeRegister("r1", 0xdeadbeefL);
            again(program, emu, at, LDSR_FXINFO, "fxinfo-ro");
            requireReg(emu, "fxinfo-ro", "FXSR", 0); // raw storage untouched
            again(program, emu, at, STSR_FXINFO, "fxinfo-ro");
            requireReg(emu, "fxinfo-ro", "tp", 3);
        } finally {
            emu.dispose();
        }
    }

    // FXXC/FXXP take their per-way write masks and never alias FXSR.
    private void execFxxIndependent(ProgramDB program, Address base) throws Exception {
        Address at = base.add(0x20 * (++fixtures));
        EmulatorHelper emu = prepare(program, at, LDSR_FXXC, "fxx-independent");
        try {
            emu.writeRegister("r1", 0xffffffffL);
            step(emu, "fxx-independent");
            requireReg(emu, "fxx-independent", "FXXC", 0x3f3f3f3fL);
            again(program, emu, at, LDSR_FXXP, "fxx-independent");
            requireReg(emu, "fxx-independent", "FXXP", 0x1f1f1f1fL);
            emu.writeRegister("r1", 0x0000fc1fL); // XC|XP through FXSR
            again(program, emu, at, LDSR_FXSR, "fxx-independent");
            requireReg(emu, "fxx-independent", "FXSR", 0x0020fc1fL);
            requireReg(emu, "fxx-independent", "FXXC", 0x3f3f3f3fL);
            requireReg(emu, "fxx-independent", "FXXP", 0x1f1f1f1fL);
            again(program, emu, at, STSR_FXXC, "fxx-independent");
            requireReg(emu, "fxx-independent", "tp", 0x3f3f3f3fL);
            again(program, emu, at, STSR_FXXP, "fxx-independent");
            requireReg(emu, "fxx-independent", "tp", 0x1f1f1f1fL);
        } finally {
            emu.dispose();
        }
    }

    // Two distinct regions keep independent descriptors through the indexed
    // views, and the write masks of Tables 3.70-3.72 apply (MPLA/MPUA bits
    // 1:0 read 0, MPAT reserved bits 13:8/6 read 0, MPIDX keeps bits 4:0).
    private void execMpuRegionsRoundtrip(ProgramDB program, Address base) throws Exception {
        Address at = base.add(0x20 * (++fixtures));
        EmulatorHelper emu = prepare(program, at, LDSR_MPIDX, "mpu-regions");
        try {
            emu.writeRegister("PSW", PSW_CU1);
            emu.writeRegister("r1", 5);
            step(emu, "mpu-regions");
            emu.writeRegister("r1", 0x10000006L);
            again(program, emu, at, LDSR_MPLA, "mpu-regions");
            emu.writeRegister("r1", 0x1ffffff3L);
            again(program, emu, at, LDSR_MPUA, "mpu-regions");
            emu.writeRegister("r1", 0xffffffffL);
            again(program, emu, at, LDSR_MPAT, "mpu-regions");
            emu.writeRegister("r1", 17);
            again(program, emu, at, LDSR_MPIDX, "mpu-regions");
            emu.writeRegister("r1", 0x20000000L);
            again(program, emu, at, LDSR_MPLA, "mpu-regions");
            emu.writeRegister("r1", 0x2ffffffcL);
            again(program, emu, at, LDSR_MPUA, "mpu-regions");
            emu.writeRegister("r1", 0x000000bfL);
            again(program, emu, at, LDSR_MPAT, "mpu-regions");
            // region 17 round-trips intact (single-triple storage would fail)
            again(program, emu, at, STSR_MPLA, "mpu-regions");
            requireReg(emu, "mpu-regions", "tp", 0x20000000L);
            again(program, emu, at, STSR_MPUA, "mpu-regions");
            requireReg(emu, "mpu-regions", "tp", 0x2ffffffcL);
            again(program, emu, at, STSR_MPAT, "mpu-regions");
            requireReg(emu, "mpu-regions", "tp", 0x000000bfL);
            // region 30 (entries 24-31 live on the G4MH virtualization
            // profile, MPCFG.NMPUE = 31) round-trips too
            emu.writeRegister("r1", 30);
            again(program, emu, at, LDSR_MPIDX, "mpu-regions");
            emu.writeRegister("r1", 0xc0000000L);
            again(program, emu, at, LDSR_MPLA, "mpu-regions");
            emu.writeRegister("r1", 0xc00fffbcL);
            again(program, emu, at, LDSR_MPUA, "mpu-regions");
            emu.writeRegister("r1", 0x0000c0bfL);
            again(program, emu, at, LDSR_MPAT, "mpu-regions");
            again(program, emu, at, STSR_MPLA, "mpu-regions");
            requireReg(emu, "mpu-regions", "tp", 0xc0000000L);
            again(program, emu, at, STSR_MPUA, "mpu-regions");
            requireReg(emu, "mpu-regions", "tp", 0xc00fffbcL);
            again(program, emu, at, STSR_MPAT, "mpu-regions");
            requireReg(emu, "mpu-regions", "tp", 0x0000c0bfL);
            emu.writeRegister("r1", 5);
            again(program, emu, at, LDSR_MPIDX, "mpu-regions");
            again(program, emu, at, STSR_MPLA, "mpu-regions");
            requireReg(emu, "mpu-regions", "tp", 0x10000004L);
            again(program, emu, at, STSR_MPUA, "mpu-regions");
            requireReg(emu, "mpu-regions", "tp", 0x1ffffff0L);
            again(program, emu, at, STSR_MPAT, "mpu-regions");
            requireReg(emu, "mpu-regions", "tp", 0xffffc0bfL);
            // MPIDX write mask: only bits 4:0
            emu.writeRegister("r1", 0x25L);
            again(program, emu, at, LDSR_MPIDX, "mpu-regions");
            again(program, emu, at, STSR_MPIDX, "mpu-regions");
            requireReg(emu, "mpu-regions", "tp", 5);
        } finally {
            emu.dispose();
        }
    }

    // MPBK (SR17,5) routes the indexed views to independent descriptor
    // banks. Selection happens through the machine LDSR/STSR selector: the
    // BK is bits 1:0; values beyond the two-bank profile are ignored.
    // Each bank's regions stay isolated in both directions.
    private void execMpuBankIsolation(ProgramDB program, Address base) throws Exception {
        Address at = base.add(0x20 * (++fixtures));
        EmulatorHelper emu = prepare(program, at, LDSR_MPIDX, "mpu-banks");
        try {
            emu.writeRegister("PSW", PSW_CU1);
            emu.writeRegister("r1", 5);
            step(emu, "mpu-banks");
            emu.writeRegister("r1", 0x11110000L);
            again(program, emu, at, LDSR_MPLA, "mpu-banks");
            // Invalid bank 3 must not alias valid bank 1.
            emu.writeRegister("r1", 3);
            execAt(program, emu, at.add(4), LDSR_MPBK, "mpu-banks invalid bank 3");
            requireReg(emu, "mpu-banks", "MPBK", 0);
            emu.writeRegister("r1", 1);
            execAt(program, emu, at.add(4), LDSR_MPBK, "mpu-banks mpbk=1");
            requireReg(emu, "mpu-banks", "MPBK", 1);
            again(program, emu, at, STSR_MPBK, "mpu-banks");
            requireReg(emu, "mpu-banks", "tp", 1);
            again(program, emu, at, STSR_MPLA, "mpu-banks");
            requireReg(emu, "mpu-banks", "tp", 0); // bank 1 region 5 empty
            emu.writeRegister("r1", 0x22220000L);
            again(program, emu, at, LDSR_MPLA, "mpu-banks");
            emu.writeRegister("r1", 0);
            execAt(program, emu, at.add(4), LDSR_MPBK, "mpu-banks mpbk=0");
            again(program, emu, at, STSR_MPBK, "mpu-banks");
            requireReg(emu, "mpu-banks", "tp", 0);
            again(program, emu, at, STSR_MPLA, "mpu-banks");
            requireReg(emu, "mpu-banks", "tp", 0x11110000L);
            emu.writeRegister("r1", 1);
            execAt(program, emu, at.add(4), LDSR_MPBK, "mpu-banks mpbk=1");
            again(program, emu, at, STSR_MPLA, "mpu-banks");
            requireReg(emu, "mpu-banks", "tp", 0x22220000L);
            emu.writeRegister("r1", 2);
            execAt(program, emu, at.add(4), LDSR_MPBK, "mpu-banks invalid bank 2");
            requireReg(emu, "mpu-banks", "MPBK", 1);
        } finally {
            emu.dispose();
        }
    }

    // LDM.MP/STM.MP move whole multi-region descriptor sets through the same
    // backing, never touch MPIDX or reg1, and honor the region write masks.
    private void execMpuBurstRegionsAndMpidx(ProgramDB program, Address base)
            throws Exception {
        Address at = base.add(0x20 * (++fixtures));
        Address data = program.getAddressFactory().getDefaultAddressSpace()
                .getAddress(0x8000);
        program.getMemory().setBytes(data, bytes(words(
                0x00020000L, 0x0002fffcL, 0x000000bfL,
                0x00030000L, 0x0003fffcL, 0x0000c0bfL)));
        EmulatorHelper emu = prepare(program, at, LDM_MP_2_3, "mpu-burst");
        try {
            emu.writeRegister("PSW", PSW_CU1);
            emu.writeRegister("r2", 0x8000L);
            emu.writeRegister("r1", 17);
            execAt(program, emu, at.add(4), LDSR_MPIDX, "mpu-burst mpidx=17");
            requireReg(emu, "mpu-burst mpidx", "MPIDX", 17);
            again(program, emu, at, LDM_MP_2_3, "mpu-burst");
            requireReg(emu, "mpu-burst", "MPIDX", 17); // bursts never touch MPIDX
            requireReg(emu, "mpu-burst", "r2", 0x8000L); // reg1 unchanged
            // both regions hold their own three words (single-triple or
            // last-region-repeat storage would fail one of these)
            emu.writeRegister("r1", 2);
            again(program, emu, at, LDSR_MPIDX, "mpu-burst");
            again(program, emu, at, STSR_MPLA, "mpu-burst");
            requireReg(emu, "mpu-burst", "tp", 0x00020000L);
            again(program, emu, at, STSR_MPUA, "mpu-burst");
            requireReg(emu, "mpu-burst", "tp", 0x0002fffcL);
            again(program, emu, at, STSR_MPAT, "mpu-burst");
            requireReg(emu, "mpu-burst", "tp", 0x000000bfL);
            emu.writeRegister("r1", 3);
            again(program, emu, at, LDSR_MPIDX, "mpu-burst");
            again(program, emu, at, STSR_MPLA, "mpu-burst");
            requireReg(emu, "mpu-burst", "tp", 0x00030000L);
            again(program, emu, at, STSR_MPUA, "mpu-burst");
            requireReg(emu, "mpu-burst", "tp", 0x0003fffcL);
            again(program, emu, at, STSR_MPAT, "mpu-burst");
            requireReg(emu, "mpu-burst", "tp", 0x0000c0bfL);
            // STM.MP writes all six words in ascending region order
            emu.writeRegister("r2", 0x8100L);
            emu.writeRegister("r1", 9);
            execAt(program, emu, at.add(4), LDSR_MPIDX, "mpu-burst mpidx=9");
            again(program, emu, at, STM_MP_2_3, "mpu-burst");
            requireReg(emu, "mpu-burst", "MPIDX", 9);
            requireMem(emu, "mpu-burst", 0x8100L, 0x00020000L);
            requireMem(emu, "mpu-burst", 0x8104L, 0x0002fffcL);
            requireMem(emu, "mpu-burst", 0x8108L, 0x000000bfL);
            requireMem(emu, "mpu-burst", 0x810cL, 0x00030000L);
            requireMem(emu, "mpu-burst", 0x8110L, 0x0003fffcL);
            requireMem(emu, "mpu-burst", 0x8114L, 0x0000c0bfL);
            // single-region bursts use the bank selected by MPBK
            emu.writeRegister("r1", 1);
            execAt(program, emu, at.add(4), LDSR_MPBK, "mpu-burst mpbk=1");
            emu.writeRegister("r2", 0x8200L);
            emu.writeMemory(program.getAddressFactory().getDefaultAddressSpace().getAddress(0x8200L), bytes(words(0x00050000L, 0x0005fffcL, 0x0000003fL)));
            emu.writeRegister("r1", 23);
            execAt(program, emu, at.add(4), LDSR_MPIDX, "mpu-burst mpidx=23");
            again(program, emu, at, LDM_MP_5_5, "mpu-burst");
            requireReg(emu, "mpu-burst", "MPIDX", 23);
            emu.writeRegister("r2", 0x8300L);
            again(program, emu, at, STM_MP_5_5, "mpu-burst");
            requireMem(emu, "mpu-burst", 0x8300L, 0x00050000L);
            requireMem(emu, "mpu-burst", 0x8304L, 0x0005fffcL);
            requireMem(emu, "mpu-burst", 0x8308L, 0x0000003fL);
            // bank 0 region 5 was never touched by the bank 1 burst
            emu.writeRegister("r1", 0);
            execAt(program, emu, at.add(4), LDSR_MPBK, "mpu-burst mpbk=0");
            emu.writeRegister("r1", 5);
            again(program, emu, at, LDSR_MPIDX, "mpu-burst");
            again(program, emu, at, STSR_MPLA, "mpu-burst");
            requireReg(emu, "mpu-burst", "tp", 0);
        } finally {
            emu.dispose();
        }
    }

    // CU1-disabled selID-10 access: FE-level UCPOP before any side effect.
    private void execFxPermissionUcpop(ProgramDB program, Address base) throws Exception {
        Address at = base.add(0x20 * (++fixtures));
        EmulatorHelper emu = prepare(program, at, STSR_FXST, "fx-ucpop");
        try {
            emu.writeRegister("PSW", 0); // supervisor, CU1 clear
            emu.writeRegister("tp", 0x12345678L);
            emu.writeRegister("FXSR", 0xaaaaaaaaL);
            step(emu, "fx-ucpop");
            requireFeFault(emu, "fx-ucpop", at, 0x81, 0x80, "tp", 0x12345678L);
            requireReg(emu, "fx-ucpop", "FXSR", 0xaaaaaaaaL);
            again(program, emu, at, LDSR_FXXP, "fx-ucpop");
            requireFeFault(emu, "fx-ucpop", at, 0x81, 0x80, null, 0);
            requireReg(emu, "fx-ucpop", "FXXP", 0);
        } finally {
            emu.dispose();
        }
    }

    // User-mode FXSR access with CU1 enabled: FE-level PIE (cause A0H,
    // vector A0H); the CU1-only views stay accessible in user mode.
    private void execFxPermissionFxsrPie(ProgramDB program, Address base) throws Exception {
        Address at = base.add(0x20 * (++fixtures));
        EmulatorHelper emu = prepare(program, at, LDSR_FXSR, "fxsr-pie");
        try {
            emu.writeRegister("PSW", PSW_UM | PSW_CU1);
            emu.writeRegister("r1", 0x0000ffffL);
            emu.writeRegister("FXSR", 0x99999999L);
            step(emu, "fxsr-pie");
            requireFeFault(emu, "fxsr-pie", at, 0xa0, 0xa0, null, 0);
            requireReg(emu, "fxsr-pie", "FXSR", 0x99999999L);
            // the first fault cleared PSW.UM; re-arm user mode for the read fault
            emu.writeRegister("PSW", PSW_UM | PSW_CU1);
            emu.writeRegister("tp", 0x12345678L);
            again(program, emu, at, STSR_FXSR, "fxsr-pie");
            requireFeFault(emu, "fxsr-pie", at, 0xa0, 0xa0, "tp", 0x12345678L);
            // CU1-only views remain user-accessible (Table 3.3 UM permission);
            // after the fault the CPU is supervisor with CU1 still set
            emu.writeRegister("FXSR", 0);
            emu.writeRegister("r1", 0x0000002aL); // IF=1 XP=0x0a
            again(program, emu, at, LDSR_FXST, "fxsr-pie");
            requireReg(emu, "fxsr-pie", "FXSR", 0x0040000aL);
        } finally {
            emu.dispose();
        }
    }

    // User mode with CU1 clear is still UCPOP, not PIE (Table 3.3 order).
    private void execFxPermissionUcpopBeforeUm(ProgramDB program, Address base)
            throws Exception {
        Address at = base.add(0x20 * (++fixtures));
        EmulatorHelper emu = prepare(program, at, STSR_FXSR, "fx-ucpop-um");
        try {
            emu.writeRegister("PSW", PSW_UM); // user mode, CU1 clear
            emu.writeRegister("tp", 0x12345678L);
            step(emu, "fx-ucpop-um");
            requireFeFault(emu, "fx-ucpop-um", at, 0x81, 0x80, "tp", 0x12345678L);
        } finally {
            emu.dispose();
        }
    }

    // User-mode indexed-MPU access and LDM.MP/STM.MP: FE-level PIE with
    // vector A0H, destination/reg1 and the descriptor file untouched.
    private void execMpuPermissionPie(ProgramDB program, Address base) throws Exception {
        Address at = base.add(0x20 * (++fixtures));
        EmulatorHelper emu = prepare(program, at, STSR_MPIDX, "mpu-pie");
        try {
            emu.writeRegister("r1", 17);
            execAt(program, emu, at.add(4), LDSR_MPIDX, "mpu-pie mpidx=17");
            emu.writeRegister("PSW", PSW_UM);
            emu.writeRegister("tp", 0x12345678L);
            emu.writeRegister("PC", at.getOffset());
            step(emu, "mpu-pie");
            requireFeFault(emu, "mpu-pie", at, 0xa0, 0xa0, "tp", 0x12345678L);
            requireReg(emu, "mpu-pie", "MPIDX", 17);
            emu.writeRegister("PSW", PSW_UM); // re-arm: the fault cleared UM
            emu.writeRegister("r2", 0x8000L);
            emu.writeMemory(program.getAddressFactory().getDefaultAddressSpace().getAddress(0x8000L), bytes(words(0x13579bdfL, 0x13579bdfL, 0x13579bdfL)));
            again(program, emu, at, LDM_MP_5_5, "mpu-pie");
            requireFeFault(emu, "mpu-pie", at, 0xa0, 0xa0, "r2", 0x8000L);
            requireMem(emu, "mpu-pie", 0x8000L, 0x13579bdfL); // memory untouched
            emu.writeRegister("PSW", PSW_UM); // re-arm: the fault cleared UM
            again(program, emu, at, STM_MP_5_5, "mpu-pie");
            requireFeFault(emu, "mpu-pie", at, 0xa0, 0xa0, "r2", 0x8000L);
            requireMem(emu, "mpu-pie", 0x8000L, 0x13579bdfL);
            // the faulted bursts wrote nothing: bank 0 region 5 still empty
            emu.writeRegister("PSW", 0);
            emu.writeRegister("r1", 5);
            again(program, emu, at, LDSR_MPIDX, "mpu-pie");
            again(program, emu, at, STSR_MPLA, "mpu-pie");
            requireReg(emu, "mpu-pie", "tp", 0);
        } finally {
            emu.dispose();
        }
    }

    // Ordinary multi-register PUSHSP/POPSP round-trip plus an independent
    // pop-order pin: PUSHSP r4-r6 puts GR[rh] at the highest address and
    // GR[rt] at the final SP; POPSP r4-r6 reloads rt from the lowest word
    // first (R01US0209EJ0220 pp.135-141), so a push immediately followed by
    // a pop restores every register and the stack pointer.
    private void execPushPopRoundtrip(ProgramDB program, Address base) throws Exception {
        Address at = base.add(0x20 * (++fixtures));
        // pushsp r4, r6: w1 = (8<<11)|0x07E0|4 = 0x47E4; w2 = (6<<11)|0x160
        EmulatorHelper emu = prepare(program, at, "e4476031", "pushpop");
        try {
            emu.writeRegister("sp", 0x8380L);
            emu.writeRegister("gp", 0x44444444L);
            emu.writeRegister("tp", 0x55555555L);
            emu.writeRegister("r6", 0x66666666L);
            step(emu, "pushpop push");
            requireReg(emu, "pushpop push", "sp", 0x8374L);
            requireMem(emu, "pushpop push", 0x8374L, 0x66666666L); // rt lowest
            requireMem(emu, "pushpop push", 0x8378L, 0x55555555L);
            requireMem(emu, "pushpop push", 0x837cL, 0x44444444L); // rh highest
            // popsp r4, r6: w1 = (0xC<<11)|0x07E0|4 = 0x67E4; w2 = 0x3160
            again(program, emu, at, "e4676031", "pushpop pop");
            requireReg(emu, "pushpop pop", "gp", 0x44444444L);
            requireReg(emu, "pushpop pop", "tp", 0x55555555L);
            requireReg(emu, "pushpop pop", "r6", 0x66666666L);
            requireReg(emu, "pushpop pop", "sp", 0x8380L);
            // independent order pin: three stacked words reload rt..rh, not
            // rh..rt (an ascending POPSP expansion fails this mapping)
            emu.writeMemory(program.getAddressFactory().getDefaultAddressSpace().getAddress(0x8380L), bytes(words(0x00000aaaL, 0x00000bbbL, 0x00000cccL)));
            emu.writeRegister("sp", 0x8380L);
            emu.writeRegister("gp", 0);
            emu.writeRegister("tp", 0);
            emu.writeRegister("r6", 0);
            again(program, emu, at, "e4676031", "pushpop order");
            requireReg(emu, "pushpop order", "r6", 0x00000aaaL); // rt <- [sp]
            requireReg(emu, "pushpop order", "tp", 0x00000bbbL);
            requireReg(emu, "pushpop order", "gp", 0x00000cccL); // rh <- top
            requireReg(emu, "pushpop order", "sp", 0x838cL);
        } finally {
            emu.dispose();
        }
    }

    // r0 is architecturally constant zero: PUSHSP stores literal 0 for it
    // even when the raw r0 varnode holds a foreign value, and POPSP
    // discards its load (R01US0209EJ0220 p.136/140; the discarded word is
    // still consumed so SP advances).
    private void execPushPopR0Constant(ProgramDB program, Address base) throws Exception {
        Address at = base.add(0x20 * (++fixtures));
        // pushsp r0, r2: w1 = (8<<11)|0x07E0|0 = 0x47E0; w2 = (2<<11)|0x160
        EmulatorHelper emu = prepare(program, at, "e0476011", "pushpop-r0");
        try {
            emu.writeRegister("sp", 0x8380L);
            emu.writeRegister("r0", 0x55555555L); // corrupt the raw varnode
            emu.writeRegister("r1", 0x11111111L);
            emu.writeRegister("r2", 0x22222222L);
            step(emu, "pushpop-r0 push");
            requireReg(emu, "pushpop-r0 push", "sp", 0x8374L);
            requireMem(emu, "pushpop-r0 push", 0x8374L, 0x22222222L); // rt
            requireMem(emu, "pushpop-r0 push", 0x8378L, 0x11111111L);
            requireMem(emu, "pushpop-r0 push", 0x837cL, 0); // r0 -> constant 0
            // popsp r0, r1: w1 = (0xC<<11)|0x07E0|0 = 0x67E0; w2 = (1<<11)|0x160
            again(program, emu, at, "e0676009", "pushpop-r0 pop");
            requireReg(emu, "pushpop-r0 pop", "r1", 0x22222222L);
            requireReg(emu, "pushpop-r0 pop", "r0", 0x55555555L); // discarded
            requireReg(emu, "pushpop-r0 pop", "sp", 0x837cL); // word consumed
        } finally {
            emu.dispose();
        }
    }
}
