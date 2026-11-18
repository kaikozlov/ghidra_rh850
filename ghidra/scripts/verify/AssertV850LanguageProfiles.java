//@category Verification
// Synthetic fixtures for V850/RH850 language selection and profile behavior.
import ghidra.app.emulator.EmulatorHelper;
import ghidra.app.script.GhidraScript;
import ghidra.app.util.PseudoDisassembler;
import ghidra.app.util.PseudoInstruction;
import ghidra.app.util.bin.ByteArrayProvider;
import ghidra.app.util.bin.format.dwarf.DWARFRegisterMappingsManager;
import ghidra.app.util.opinion.ElfLoader;
import ghidra.app.util.opinion.LoadSpec;
import ghidra.program.database.ProgramDB;
import ghidra.program.model.address.Address;
import ghidra.program.model.lang.Language;
import ghidra.program.model.lang.LanguageCompilerSpecPair;
import ghidra.program.model.lang.LanguageID;
import ghidra.program.model.lang.UnknownInstructionException;
import ghidra.program.util.DefaultLanguageService;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.util.Arrays;
import java.util.HexFormat;
import java.util.List;
import java.util.Map;

public class AssertV850LanguageProfiles extends GhidraScript {
    private static final String E1F = "v850e1f:LE:32:default";
    private static final String E2M = "v850:LE:32:default";
    private static final String G3M = "v850e3:LE:32:default";
    private static final String P1XC = "v850e3:LE:32:P1xC";
    private static final String D1LD1M = "v850e3:LE:32:D1LD1M";
    private static final String BROAD = "v850e3x:LE:32:default";
    private static final HexFormat HEX = HexFormat.of();
    private static final String[][] FORMAT_XIV = {
        {"a60767440000", "ld.hu"}, // Also the positive disp23 execution case.
        {"860735400000", "ld.b"}, {"860767440000", "ld.h"}, {"860769440000", "ld.w"},
        {"86073d400000", "st.b"}, {"86076f440000", "st.w"},
        {"a60735400000", "ld.bu"}, {"a6076d440000", "st.h"}
    };
    private static final Map<Integer, String> DWARF_PROBES =
        Map.of(32, "EIPC", 33, "EIPSW", 34, "FEPC", 35, "FEPSW", 37, "PSW",
            48, "CTPC", 49, "CTPSW", 52, "CTBP");
    // CPU MMIO mask: P1M-E = 1, P1x-C = 2, D1L/D1M = 4.
    private static final long[][] MMIO_PROBES = {
        {0, 0}, {0x10000000, 1}, {0x1fffffff, 1}, {0x20000000, 0},
        {0xfebfffffL, 0}, {0xff000000L, 3}, {0xff1fffffL, 3},
        {0xff200000L, 0}, {0xff300040L, 0}, {0xff3fffffL, 0},
        {0xff400000L, 7}, {0xfffdffffL, 7}, {0xfffe0000L, 0},
        {0xfffedfffL, 0}, {0xfffee000L, 7}, {0xfffeffffL, 7},
        {0xffff0000L, 4}, {0xffff4fffL, 4}, {0xffff5000L, 7}, {0xffffffffL, 7},
    };

    private static void require(boolean ok, String message) {
        if (!ok) throw new IllegalStateException(message);
    }

    private static void expectElf(int machine, int flags, LanguageCompilerSpecPair expected)
            throws Exception {
        ByteBuffer elf = ByteBuffer.allocate(52).order(ByteOrder.LITTLE_ENDIAN);
        elf.put(new byte[]{0x7f, 'E', 'L', 'F', 1, 1, 1});  // ELF32, LE, version 1
        elf.putShort(16, (short) 1);                       // ET_REL
        elf.putShort(18, (short) machine);
        elf.putInt(20, 1);
        elf.putInt(36, flags);
        elf.putShort(40, (short) elf.capacity());
        try (ByteArrayProvider provider = new ByteArrayProvider("fixture.elf", elf.array())) {
            var specs = new ElfLoader().findSupportedLoadSpecs(provider);
            String label = String.format("ELF machine=%#x flags=%#x", machine, flags);
            require(!specs.isEmpty(), label + ": not recognized as ELF");
            if (expected == null) {
                require(specs.stream().noneMatch(LoadSpec::isComplete),
                    label + ": unexpectedly assigned a language");
                return;
            }
            List<LanguageCompilerSpecPair> preferred = specs.stream()
                .filter(LoadSpec::isPreferred).map(LoadSpec::getLanguageCompilerSpec).toList();
            require(preferred.equals(List.of(expected)), label + ": preferred " + preferred
                + ", expected " + expected);
            require(specs.stream().allMatch(spec -> spec.getLanguageCompilerSpec() != null
                    && spec.getLanguageCompilerSpec().getLanguageID().equals(expected.getLanguageID())),
                label + ": offered an unrelated language");
        }
    }

    private static void verifyDwarfRegisters(Language language) throws Exception {
        var mapping = DWARFRegisterMappingsManager.getMappingForLang(language);
        for (var probe : DWARF_PROBES.entrySet()) {
            var register = mapping.getGhidraReg(probe.getKey());
            require(register != null && register.equals(language.getRegister(probe.getValue())),
                language.getLanguageID() + ": DWARF register " + probe.getKey()
                    + " should resolve to " + probe.getValue());
        }
        var pc = mapping.getGhidraReg(64);
        require(pc != null && pc.equals(language.getProgramCounter()),
            language.getLanguageID() + ": DWARF register 64 should resolve to the program counter");
    }

    private static void expectManualPage(Language language, String mnemonic, String page) {
        var entry = language.getManualEntry(mnemonic);
        require(entry != null && page.equals(entry.getPageNumber()),
            language.getLanguageID() + ": expected " + mnemonic + " help on page " + page);
    }

    private static void verifyDeviceWindows(Language language, int device) {
        for (long[] probe : MMIO_PROBES) {
            Address address = language.getDefaultSpace().getAddress(probe[0]);
            require(language.isVolatile(address) == ((probe[1] & device) != 0),
                language.getLanguageID() + ": incorrect volatility at " + address);
        }
    }

    private static PseudoInstruction decode(ProgramDB program, PseudoDisassembler decoder,
            Address at, String raw, String mnemonic) throws Exception {
        byte[] bytes = HEX.parseHex(raw);
        program.getMemory().setBytes(at, bytes);
        PseudoInstruction instruction;
        try {
            instruction = decoder.disassemble(at);
        } catch (UnknownInstructionException e) {
            instruction = null;
        }
        String label = program.getLanguageID() + " bytes " + raw;
        if (mnemonic == null) {
            require(instruction == null, label + ": unexpectedly decoded as " + instruction);
        } else {
            require(instruction != null && mnemonic.equals(instruction.getMnemonicString())
                    && instruction.getLength() == bytes.length,
                label + ": expected " + mnemonic + ", got " + instruction);
        }
        return instruction;
    }

    private void step(EmulatorHelper emu, Address pc) throws Exception {
        emu.writeRegister("PC", pc.getOffset());
        require(emu.step(monitor), pc + ": " + emu.getLastError());
    }

    private void exerciseLoads(EmulatorHelper emu, Address pc, Address negative) throws Exception {
        Address data = pc.getNewAddress(0x3000);
        emu.writeRegister("r6", data.getOffset());
        emu.writeMemory(data.add(0x46), HEX.parseHex("23b1"));
        emu.writeMemory(data.subtract(2), HEX.parseHex("78a5"));
        step(emu, pc);
        require(emu.readRegister("r8").longValue() == 0xb123, "LD.HU positive disp23");
        step(emu, negative);
        require(emu.readRegister("r8").longValue() == 0xa578, "LD.HU negative disp23");
    }

    private void exerciseCaxi(EmulatorHelper emu, Address pc, boolean e2m) throws Exception {
        Address data = pc.getNewAddress(0x3000);
        emu.writeRegister("r6", data.getOffset());
        emu.writeRegister("PSW", 0x1f);
        emu.writeRegister("r10", 1);
        emu.writeMemory(data, HEX.parseHex("03000000"));
        step(emu, pc);
        require(emu.readRegister("r10").longValue() == 3
                && (emu.readRegister("PSW").longValue() & 0x1f) == 0x1a
                && Arrays.equals(emu.readMemory(data, 4), HEX.parseHex("03000000")),
            "CAXI aliases: compare-miss must update CY and S, retain SAT, and return token");
        emu.writeRegister("r10", 0x80000000L);
        emu.writeMemory(data, HEX.parseHex("01000000"));
        step(emu, pc);
        require(emu.readRegister("r10").longValue() == 1
                && (emu.readRegister("PSW").longValue() & 0xf) == 4,
            "CAXI aliases: signed overflow is from the original compare operand");
        if (e2m) {
            emu.writeRegister("r6", data.getOffset() + 1);
            emu.writeRegister("r10", 0x11223344);
            emu.writeRegister("r11", 0x55667788);
            emu.writeMemory(data, HEX.parseHex("44332211aa"));
            step(emu, pc.add(8));
            require(emu.readRegister("r11").longValue() == 0x11223344
                    && (emu.readRegister("PSW").longValue() & 0xf) == 1
                    && Arrays.equals(emu.readMemory(data, 5), HEX.parseHex("88776655aa")),
                "E2M CAXI must mask the same address for the load and store");
        }
    }

    private void verifyInstructions(Language language, String id) throws Exception {
        ProgramDB program = new ProgramDB("v850-language-profile", language,
            language.getDefaultCompilerSpec(), this);
        int tx = program.startTransaction("instruction fixtures");
        try {
            Address base = program.getAddressFactory().getDefaultAddressSpace().getAddress(0x1000);
            program.getMemory().createInitializedBlock("fixture", base, 0x3000,
                (byte) 0, monitor, false);
            PseudoDisassembler decoder = new PseudoDisassembler(program);
            for (int i = 0; i < FORMAT_XIV.length; i++) {
                String[] fixture = FORMAT_XIV[i];
                decode(program, decoder, base.add(8L * i), fixture[0],
                    id.equals(E1F) ? null : fixture[1]);
            }
            if (id.equals(E1F)) return;

            Address negative = base.add(0x40);
            decode(program, decoder, negative, "a607e747ffff", "ld.hu");
            decode(program, decoder, base.add(0x48), "a60777440000", null);
            Address caxi = base.add(0x50);
            decode(program, decoder, caxi, "e657ee50", "caxi"); // CAXI [r6],r10,r10
            if (id.equals(E2M)) {
                decode(program, decoder, caxi.add(8), "e657ee58", "caxi"); // CAXI [r6],r10,r11
            }
            if (id.equals(G3M)) {
                String[][] stores = {{"830b", "sst.b", "r1"}, {"821c", "sst.h", "sp"},
                    {"0315", "sst.w", "r2"}};
                for (int i = 0; i < stores.length; i++) {
                    String[] store = stores[i];
                    PseudoInstruction ins =
                        decode(program, decoder, base.add(0x60 + 8L * i), store[0], store[1]);
                    require(ins.getNumOperands() == 3
                            && language.getRegister(store[2]).equals(ins.getRegister(0))
                            && ins.getScalar(1).getUnsignedValue() == (i == 0 ? 3 : 4)
                            && language.getRegister("ep").equals(ins.getRegister(2)),
                        store[1] + " operand order: " + ins);
                }
            }
            EmulatorHelper emu = new EmulatorHelper(program);
            try {
                exerciseLoads(emu, base, negative);
                exerciseCaxi(emu, caxi, id.equals(E2M));
            } finally {
                emu.dispose();
            }
        } finally {
            program.endTransaction(tx, false);
            program.release(this);
        }
    }

    @Override
    protected void run() throws Exception {
        expectElf(36, 0xf0000041, new LanguageCompilerSpecPair(E2M, "default"));
        expectElf(36, 0xf0100041, new LanguageCompilerSpecPair(BROAD, "default"));
        expectElf(87, 0x40000020, new LanguageCompilerSpecPair(E2M, "gcc"));
        expectElf(87, 0x60000020, new LanguageCompilerSpecPair(BROAD, "gcc"));
        expectElf(0x9080, 0x60000020, new LanguageCompilerSpecPair(BROAD, "gcc"));
        expectElf(36, 0, null);
        expectElf(87, 0x70000000, null);
        for (String id : List.of(E1F, E2M, BROAD, G3M, P1XC, D1LD1M)) {
            Language language = DefaultLanguageService.getLanguageService().getLanguage(new LanguageID(id));
            verifyDwarfRegisters(language);
            int device = switch (id) {
                case G3M -> 1;
                case P1XC -> 2;
                case D1LD1M -> 4;
                default -> 0;
            };
            if (device != 0) {
                verifyDeviceWindows(language, device);
                // BNE uses the B family entry; an exact BSH match must win over B.
                expectManualPage(language, "bne", "204");
                expectManualPage(language, "bsh", "207");
            } else if (id.equals(E2M)) {
                expectManualPage(language, "ld.hu", "112");
            }
            // The three device profiles share the G3M instruction decoder.
            if (device == 0 || id.equals(G3M)) verifyInstructions(language, id);
        }
        println("ASSERT v850-language-profiles: passed");
    }
}
