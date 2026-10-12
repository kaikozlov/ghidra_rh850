//@category Verification
// Real LDSR/STSR/HVTRAP/EIRET/FERET paths, not simulated helper callbacks.
// Authorities: R01US0432EJ0110 pp.13-25; R01UH0865EJ0140 Tables
// 2.2/2.3/3.12/3.21-3.25/3.50, Sections 3.9 and 4.3;
// R01UH0864EJ0150 Tables 3.30/3.72 for SVLOCK and invalid MPBK writes.
import ghidra.app.emulator.EmulatorHelper;
import ghidra.app.script.GhidraScript;
import ghidra.program.database.ProgramDB;
import ghidra.program.model.address.Address;
import ghidra.program.model.lang.Language;
import ghidra.program.model.lang.LanguageID;
import ghidra.program.util.DefaultLanguageService;

public class AssertV850Virtualization extends GhidraScript {
    private Address at(ProgramDB p, long value) {
        return p.getAddressFactory().getDefaultAddressSpace().getAddress(value);
    }
    private void put(ProgramDB p, long pc, int... words) throws Exception {
        byte[] raw = new byte[words.length * 2];
        for (int i = 0; i < words.length; ++i) {
            raw[2 * i] = (byte) words[i];
            raw[2 * i + 1] = (byte) (words[i] >>> 8);
        }
        p.getMemory().setBytes(at(p, pc), raw);
    }
    private void ldsr(ProgramDB p, long pc, int id, int sel) throws Exception {
        put(p, pc, (id << 11) | 0x07e1, (sel << 11) | 0x20);
    }
    private void stsr(ProgramDB p, long pc, int id, int sel) throws Exception {
        put(p, pc, (5 << 11) | 0x07e0 | id, (sel << 11) | 0x40);
    }
    private void step(EmulatorHelper emu, long pc) throws Exception {
        emu.writeRegister("PC", pc);
        if (!emu.step(monitor)) throw new IllegalStateException(emu.getLastError());
    }
    private void write(EmulatorHelper emu, long pc, long value) throws Exception {
        emu.writeRegister("r1", value);
        step(emu, pc);
    }
    private void eq(EmulatorHelper emu, String reg, long value) {
        long actual = emu.readRegister(reg).longValue() & 0xffffffffL;
        if (actual != (value & 0xffffffffL)) {
            throw new IllegalStateException(reg + "=" + Long.toHexString(actual)
                + " expected " + Long.toHexString(value));
        }
    }
    private EmulatorHelper host(ProgramDB p, boolean capable) {
        EmulatorHelper emu = new EmulatorHelper(p);
        // Hardware identity/configuration inputs, not software-writable defaults.
        emu.writeRegister("PID", capable ? 0x00800000L : 0);
        emu.writeRegister("SPIDLIST", 0xffffffffL);
        emu.writeRegister("RBASE", 0x1000);
        emu.writeRegister("EBASE", 0x2000);
        emu.writeRegister("PSW", 0x800a);
        emu.writeRegister("EIPSW", 0x8012);
        emu.writeRegister("EIPC", 0x4100);
        emu.writeRegister("SPID", 7);
        emu.writeRegister("PEID", 11);
        return emu;
    }
    private void configureGuest(EmulatorHelper emu) throws Exception {
        write(emu, 0x3000, 1);          // HVCFG.HVE
        write(emu, 0x3010, 0x8025);     // GMPSW, distinct from HMPSW
        write(emu, 0x3014, 0x4200);     // GMEIPC for guest-local return
        write(emu, 0x3018, 0x8023);     // GMEIPSW
        write(emu, 0x301c, 0x8000);     // GMEBASE
        write(emu, 0x3020, 3);          // GMSPID
        write(emu, 0x3058, 17);         // virtual PEID, host PEID is read-only
        write(emu, 0x3060, 0x01234567); // host notification, not banked
        write(emu, 0x3008, 0x80000300L);// EIPSWH.GM + GPID 3
    }
    @Override protected void run() throws Exception {
        Language lang = DefaultLanguageService.getLanguageService()
            .getLanguage(new LanguageID("v850e3x:LE:32:default"));
        ProgramDB p = new ProgramDB("virtualization", lang, lang.getDefaultCompilerSpec(), this);
        int tx = p.startTransaction("virtualization fixtures");
        try {
            p.getMemory().createInitializedBlock("memory", at(p, 0x1000), 0x8000,
                (byte) 0, monitor, false);
            ldsr(p, 0x3000, 16, 1); stsr(p, 0x3004, 16, 1);
            ldsr(p, 0x3008, 18, 0); ldsr(p, 0x300c, 19, 0);
            ldsr(p, 0x3010, 5, 9); ldsr(p, 0x3014, 0, 9);
            ldsr(p, 0x3018, 1, 9); ldsr(p, 0x301c, 19, 9);
            ldsr(p, 0x3020, 16, 9); ldsr(p, 0x3024, 24, 9);
            ldsr(p, 0x3028, 15, 0); ldsr(p, 0x302c, 17, 1);
            ldsr(p, 0x3030, 16, 5); ldsr(p, 0x3034, 20, 5);
            stsr(p, 0x3038, 20, 5); ldsr(p, 0x303c, 8, 1);
            ldsr(p, 0x3040, 17, 5); ldsr(p, 0x3044, 6, 1);
            ldsr(p, 0x3054, 0, 2); ldsr(p, 0x3058, 30, 9);
            stsr(p, 0x305c, 20, 1); ldsr(p, 0x3060, 20, 1);
            ldsr(p, 0x3064, 5, 0); stsr(p, 0x3068, 0, 2);
            put(p, 0x4000, 0x07e0, 0x0148); // EIRET
            put(p, 0x4004, 0x07e0, 0x014a); // FERET
            put(p, 0x4100, 0x07e7, 0x0110); // HVTRAP 7
            put(p, 0x4104, 0x07e0, 0x0148); // guest-local EIRET
            put(p, 0x2020, 0x07e0, 0x0148); // host handler EIRET
            put(p, 0x3050, 0x17e2, 0x1166); // LDM.MP [r2],2-2
            put(p, 0x7000, 0x0000, 0x2222, 0xfffc, 0x2222, 0x00bf, 0x0000);

            EmulatorHelper emu = host(p, false);
            try {
                write(emu, 0x3000, 1);
                eq(emu, "HVCFG", 0); // cannot fabricate PID.HV support
                step(emu, 0x4100);
                eq(emu, "FEPC", 0x4100); eq(emu, "FEIC", 0x60);
                eq(emu, "PC", 0x2060); eq(emu, "EIPC", 0x4100);
            } finally {
                emu.dispose();
            }
            emu = host(p, true);
            try {
                configureGuest(emu);
                write(emu, 0x3044, 0); eq(emu, "PID", 0x00800000L);
                write(emu, 0x3054, 31); eq(emu, "PEID", 11);
                write(emu, 0x3028, 0x80000700L); eq(emu, "PSWH", 0); // read-only
                write(emu, 0x3024, 1); // guest SVLOCK, host remains unlocked
                step(emu, 0x4000);
                eq(emu, "PC", 0x4100); eq(emu, "PSWH", 0x80000300L);
                eq(emu, "PSW", 0x8025); eq(emu, "EBASE", 0x8000);
                eq(emu, "SPID", 3); eq(emu, "SVLOCK", 1);
                eq(emu, "PEID", 17);
                write(emu, 0x3054, 31); eq(emu, "PEID", 17);
                step(emu, 0x4100);
                eq(emu, "PC", 0x2020); eq(emu, "PSWH", 0x300);
                eq(emu, "EIPC", 0x4104); eq(emu, "EIPSW", 0x8012);
                eq(emu, "EIPSWH", 0x80000300L); eq(emu, "EIIC", 0xf007);
                eq(emu, "PSW", 0x8072); eq(emu, "EBASE", 0x2000);
                eq(emu, "SPID", 7); eq(emu, "SVLOCK", 0);
                write(emu, 0x3020, 5); // inactive guest write bypasses guest SVLOCK
                step(emu, 0x2020);
                eq(emu, "PC", 0x4104); eq(emu, "PSWH", 0x80000300L);
                eq(emu, "PSW", 0x8025); eq(emu, "SPID", 5); eq(emu, "SVLOCK", 1);
                step(emu, 0x4104);
                eq(emu, "PC", 0x4200); eq(emu, "PSW", 0x8023);
            } finally {
                emu.dispose();
            }
            emu = host(p, true);
            try {
                configureGuest(emu);
                emu.writeRegister("FEPC", 0x4104);
                emu.writeRegister("FEPSW", 0x8012);
                write(emu, 0x300c, 0x80000300L);
                write(emu, 0x3008, 0); // deliberately different saved EI mode
                step(emu, 0x4004); step(emu, 0x4104);
                eq(emu, "PC", 0x4200); eq(emu, "PSWH", 0x80000300L);
            } finally {
                emu.dispose();
            }
            emu = host(p, true);
            try {
                configureGuest(emu); write(emu, 0x3024, 1); step(emu, 0x4000);
                write(emu, 0x3040, 1); // MPBK is HV, even with guest SVLOCK set
                eq(emu, "MPBK", 0); eq(emu, "FEPC", 0x3040); eq(emu, "FEIC", 0xa0);
                eq(emu, "PC", 0x80a0); eq(emu, "PSWH", 0x80000300L);
            } finally {
                emu.dispose();
            }
            emu = host(p, true);
            try {
                write(emu, 0x3030, 2); write(emu, 0x3034, 0x11110000L);
                write(emu, 0x303c, 1); write(emu, 0x3034, 0x33330000L);
                step(emu, 0x3038); eq(emu, "tp", 0x11110000L);
                emu.writeRegister("r2", 0x7000); step(emu, 0x3050);
                step(emu, 0x3038); eq(emu, "tp", 0x11110000L);
                write(emu, 0x3040, 1); eq(emu, "MPBK", 0);
                write(emu, 0x3030, 3); eq(emu, "MPIDX", 3); // not protected
                write(emu, 0x303c, 0); write(emu, 0x3030, 2);
                step(emu, 0x3050); step(emu, 0x3038); eq(emu, "tp", 0x22220000L);
            } finally {
                emu.dispose();
            }
            emu = host(p, true);
            try {
                configureGuest(emu); step(emu, 0x4000);
                write(emu, 0x3064, 0x70000); eq(emu, "PSW", 0x8000);
                write(emu, 0x3064, 0x40070000L); eq(emu, "PSW", 0x40008000L);
                step(emu, 0x305c); eq(emu, "tp", 0x01234567); // UM-readable
                write(emu, 0x3060, 0x76543210);
                eq(emu, "HVSB", 0x01234567); eq(emu, "FEIC", 0xa0);
                eq(emu, "FEPC", 0x3060); eq(emu, "FEPSW", 0x40008000L);
                eq(emu, "PC", 0x80a0);
            } finally {
                emu.dispose();
            }
            println("ASSERT v850-virtualization: passed");
        } finally {
            p.endTransaction(tx, false);
            p.release(this);
        }
    }
}
