//@author kaikozlov
//@category Seed
// Observed entry roots only: original reset, metadata-selected application,
// startup relocation code groups, and the populated high flash bank.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.CodeUnit;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.Listing;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.symbol.SourceType;

public class SeedR4pMeterEntries extends GhidraScript {
    private static final String IMAGE_SHA = "cc75cac2aaa4a648dadcad3d3d59d0c1bb293c53f1dbfcf9bc0fc88b4b6a4322";

    private Function ensure(long offset, String name) throws Exception {
        Address address = toAddr(offset);
        MemoryBlock block = currentProgram.getMemory().getBlock(address);
        if (block == null || !block.isInitialized() || !block.isExecute()) {
            throw new IllegalStateException("entry is not initialized executable memory: " + address);
        }
        Listing listing = currentProgram.getListing();
        Instruction containing = listing.getInstructionContaining(address);
        if (containing != null && !containing.getMinAddress().equals(address)) {
            listing.clearCodeUnits(containing.getMinAddress(), containing.getMaxAddress(), false);
        }
        CodeUnit unit = listing.getCodeUnitContaining(address);
        if (unit != null && !(unit instanceof Instruction)) {
            listing.clearCodeUnits(unit.getMinAddress(), unit.getMaxAddress(), false);
        }
        if (listing.getInstructionAt(address) == null && !disassemble(address)) {
            throw new IllegalStateException("disassembly failed at " + address);
        }
        Function function = currentProgram.getFunctionManager().getFunctionAt(address);
        if (function == null) function = createFunction(address, name);
        if (function == null) throw new IllegalStateException("function creation failed at " + address);
        if (!name.equals(function.getName())) function.setName(name, SourceType.USER_DEFINED);
        return function;
    }

    @Override
    public void run() throws Exception {
        if (!IMAGE_SHA.equalsIgnoreCase(currentProgram.getExecutableSHA256()) ||
                !"v850e3:LE:32:default".equals(currentProgram.getLanguageID().toString())) {
            throw new IllegalStateException("wrong R4P meter image or processor");
        }
        if (currentProgram.getMemory().getBlock("RprgCode_FEDC0110") == null ||
                currentProgram.getMemory().getBlock("HighBankCode") == null) {
            throw new IllegalStateException("ApplyR4pMeterDeviceProfile must run first");
        }

        // Exact body ends at 7983C: jmp lp, not an infinite loop. Seed before
        // any analysis can prune the continuations of its numerous callers.
        ensure(0x7982C, "r4p_byte_fill").setNoReturn(false);

        // These five entry addresses are the executable relocation destinations
        // in rows 11A0, 11C8, 11D4, 11E0 and 11EC. Do not seed the data rows.
        ensure(0xFEDC0110L, "r4p_rprg_flash_driver_entry");
        ensure(0xFEDC20D0L, "r4p_rprg_runtime_entry");
        ensure(0xFEDC8B5CL, "r4p_rprg_extended_user_entry");
        ensure(0xFEDD0110L, "r4p_rprg_crypto_entry");
        ensure(0xFEDD8000L, "r4p_rprg_runtime_group_entry");
        // Direct final call at the end of low-flash startup FBC.
        ensure(0xFEDC8814L, "r4p_rprg_main");

        // 1F0E0 calls 1FB176 and 1FAFE0, then resolves the 1FB264 code
        // fragment through 1FB0BA. That fragment directly calls 1FC8A0/1FC0FA.
        ensure(0x1FC8A0, "r4p_highbank_request_dispatch");
        ensure(0x1FC0FA, "r4p_highbank_request_poll");
        ensure(0x1FB176, "r4p_highbank_initialize");
        ensure(0x1FAFE0, "r4p_highbank_prepare_runtime_image");

        // The application reset address is a word in the original end metadata,
        // not the exception-vector bank at 10000. Its final indirect transfer
        // loads 10B28, whose value is 83E88 (application initialization stages).
        if (Integer.toUnsignedLong(getInt(toAddr(0x1FFFE0))) != 0x10634 ||
                Integer.toUnsignedLong(getInt(toAddr(0x10B28))) != 0x83E88) {
            throw new IllegalStateException("application entry metadata drift");
        }
        ensure(0x83E88, "r4p_application_initialize");
        ensure(0x10634, "r4p_application_reset_entry");
        ensure(0xFBC, "r4p_boot_startup");
        ensure(0xEE8, "r4p_reset_startup");
        // Original CodeFlash already contains VA-zero jr EE8; never normalize
        // or trim this specimen as though it were a shifted 1 MiB image.
        ensure(0, "r4p_reset_vector");
        println("SeedR4pMeterEntries: seeded 16 observed roots including returning byte fill");
    }
}
