//@author kaikozlov
//@category Verification
// Check curated project invariants: critical functions, labels, calling
// conventions, memory blocks, and boot/application register context.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.listing.Data;
import ghidra.program.model.listing.Function;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.symbol.Symbol;
import ghidra.program.model.symbol.SymbolTable;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.lang.Register;
import ghidra.program.model.lang.RegisterValue;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.math.BigInteger;
import java.util.ArrayList;
import java.util.List;

public class AssertProjectInvariants extends GhidraScript {
    private final List<String> failures = new ArrayList<>();

    private void fail(String msg) {
        failures.add(msg);
        println("FAIL: " + msg);
    }

    private void requireFunction(long addr, String name) {
        Function f = getFunctionAt(toAddr(addr));
        if (f == null) {
            fail(String.format("missing function at 0x%x (expected %s)", addr, name));
            return;
        }
        if (name != null && !name.equals(f.getName())) {
            fail(String.format("function at 0x%x named %s, expected %s",
                    addr, f.getName(), name));
        }
    }

    private void requireLabel(long addr, String name) {
        SymbolTable symbols = currentProgram.getSymbolTable();
        Symbol[] syms = symbols.getSymbols(toAddr(addr));
        boolean found = false;
        for (Symbol s : syms) {
            if (name.equals(s.getName())) { found = true; break; }
        }
        if (!found) {
            fail(String.format("missing label %s at 0x%x", name, addr));
        }
    }

    private void requireConvention(long addr, String convention) {
        Function f = getFunctionAt(toAddr(addr));
        if (f == null) {
            fail(String.format("missing function at 0x%x for convention check", addr));
            return;
        }
        String actual = f.getCallingConventionName();
        if (actual == null || !actual.equals(convention)) {
            fail(String.format("function 0x%x (%s) convention=%s expected=%s",
                    addr, f.getName(), actual, convention));
        }
    }

    private void requireReference(long from, long to) {
        Reference[] refs = currentProgram.getReferenceManager()
                .getReferencesFrom(toAddr(from));
        for (Reference ref : refs) {
            if (ref.getToAddress().equals(toAddr(to))) return;
        }
        fail(String.format("missing vector reference 0x%x -> 0x%x", from, to));
    }

    private void requireBlock(String name, long start, long size,
                              boolean read, boolean write, boolean execute,
                              boolean volatileBlock) {
        MemoryBlock block = currentProgram.getMemory().getBlock(name);
        if (block == null) {
            fail("missing memory block " + name);
            return;
        }
        if (block.getStart().getOffset() != start || block.getSize() != size) {
            fail(String.format("%s range=%s..%s expected 0x%x..0x%x",
                    name, block.getStart(), block.getEnd(), start, start + size - 1));
        }
        if (block.isRead() != read || block.isWrite() != write
                || block.isExecute() != execute || block.isVolatile() != volatileBlock) {
            fail(String.format("%s permissions r=%s w=%s x=%s volatile=%s",
                    name, block.isRead(), block.isWrite(), block.isExecute(),
                    block.isVolatile()));
        }
    }

    private void requireRegister(Address addr, String regName, long expected) {
        Register reg = currentProgram.getRegister(regName);
        if (reg == null) {
            fail("missing register " + regName);
            return;
        }
        RegisterValue rv = currentProgram.getProgramContext().getRegisterValue(reg, addr);
        if (rv == null || !rv.hasValue()) {
            fail(String.format("no %s context at %s (expected 0x%x)",
                    regName, addr, expected));
            return;
        }
        BigInteger val = rv.getUnsignedValue();
        if (val.longValue() != expected) {
            fail(String.format("%s at %s = 0x%x expected 0x%x",
                    regName, addr, val.longValue(), expected));
        }
    }

    private void requireDataType(long addr, String typeName, int length) {
        Data data = currentProgram.getListing().getDataAt(toAddr(addr));
        if (data == null || !data.isDefined()) {
            fail(String.format("missing defined data at 0x%x (expected %s)", addr, typeName));
            return;
        }
        DataType dt = data.getDataType();
        String actual = dt.getName();
        // Accept either the bare type name or a CategoryPath-qualified form.
        if (!typeName.equals(actual) && !actual.endsWith("/" + typeName)
                && !typeName.equals(dt.getDisplayName())) {
            fail(String.format("data at 0x%x typed %s, expected %s", addr, actual, typeName));
        }
        if (data.getLength() != length) {
            fail(String.format("data at 0x%x length=%d expected=%d (%s)",
                    addr, data.getLength(), length, typeName));
        }
    }

    private void requireDefinedLength(long addr, int length) {
        Data data = currentProgram.getListing().getDataAt(toAddr(addr));
        if (data == null || !data.isDefined()) {
            fail(String.format("missing defined data at 0x%x (expected length %d)",
                    addr, length));
            return;
        }
        if (data.getLength() != length) {
            fail(String.format("data at 0x%x length=%d expected=%d",
                    addr, data.getLength(), length));
        }
    }

    /**
     * Assert every enabled checkpoint RAM mirror is present and correctly typed,
     * mirroring ApplyRamTypes.applyCheckpointCsv's CSV parsing. When invoked
     * without the gate's CSV arg, checkpoint coverage is left to the firmware
     * suite tests/verify_ram_overlays.py.
     */
    private void requireCheckpointCsv(String csvPath) throws Exception {
        if (csvPath == null || csvPath.isEmpty()) {
            return;
        }
        File csv = new File(csvPath);
        if (!csv.isFile()) {
            fail("missing checkpoint CSV: " + csvPath);
            return;
        }
        int checked = 0;
        try (BufferedReader br = new BufferedReader(new FileReader(csv))) {
            String header = br.readLine();
            if (header == null || !header.startsWith("object_index,")) {
                fail("unexpected checkpoint CSV header: " + header);
                return;
            }
            String line;
            while ((line = br.readLine()) != null) {
                line = line.trim();
                if (line.isEmpty() || line.startsWith("#")) continue;
                String[] parts = line.split(",", -1);
                if (parts.length < 10) {
                    fail("checkpoint CSV row needs >=10 columns: " + line);
                    continue;
                }
                if (!"yes".equalsIgnoreCase(parts[1].trim())) continue;
                int length = Integer.parseInt(parts[2].trim());
                long addr = Long.decode(parts[5].trim());
                String evidenceName = parts[7].trim();
                requireDataType(addr, "Checkpoint_" + evidenceName, length);
                requireLabel(addr, "checkpoint_" + evidenceName);
                checked++;
            }
        }
        if (checked == 0) {
            fail("checkpoint CSV yielded zero enabled entries: " + csvPath);
        } else {
            println("ASSERT checkpoint-overlays: verified " + checked
                    + " enabled checkpoints from " + csvPath);
        }
    }

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        String checkpointCsv = (args.length >= 1) ? args[0] : null;

        // Critical boot/application landmarks.
        requireFunction(0x1b0L, "boot_reset_startup");
        requireFunction(0x6fecL, "security_access_derive_stage1_key");
        requireFunction(0x7068L, "payload_build_derive_key");
        requireFunction(0x650acL, "application_icus_ch292_isr");
        requireFunction(0x650eeL, "application_icus_ch293_isr");

        requireLabel(0xbfd8L, "PAYLOAD_BUILD_SECRET");
        requireLabel(0xbfe8L, "SEED_KEY_SECRET");
        requireLabel(0x8e54L, "uds_service_table");

        // Memory map.
        MemoryBlock code = currentProgram.getMemory().getBlock(toAddr(0x0L));
        MemoryBlock data = currentProgram.getMemory().getBlock(toAddr(0xFF200000L));
        if (code == null || code.getSize() != 0x100000L) {
            fail("CodeFlash block missing or wrong size");
        } else {
            if (!code.isExecute()) fail("CodeFlash should be executable");
            if (code.isWrite()) fail("CodeFlash should not be writable");
        }
        if (data == null || data.getSize() != 0x8000L) {
            fail("DataFlash block missing or wrong size");
        }

        // Device-profile RAM/SFR windows are mandatory in the final project.
        requireBlock("LocalRAM", 0xFEBE0000L, 0x20000L, true, true, false, false);
        requireBlock("SFR_EIC", 0xFFFFB000L, 0x1000L, true, true, false, true);
        requireBlock("SFR_RSCFD", 0xFFD20000L, 0x10000L, true, true, false, true);
        requireBlock("SFR_ICUS", 0xFFC5D000L, 0x1000L, true, true, false, true);

        // Evidence-backed SFR labels from data/p1m_sfr_labels.csv.
        requireLabel(0xFFFFB110L, "EIC136");
        requireLabel(0xFFFFB10AL, "EIC133");
        requireLabel(0xFFFFB248L, "EIC292");
        requireLabel(0xFFFFB24AL, "EIC293");
        requireLabel(0xFFFFB176L, "EIC187");
        requireLabel(0xFFD20178L, "CFSTS");
        requireLabel(0xFFD20184L, "CFSTS_CH1");
        requireLabel(0xFFD201D8L, "CFPCTR");
        requireLabel(0xFFD20250L, "CFDTMC");
        requireLabel(0xFFD20260L, "CFDTMC16");
        requireLabel(0xFFD202D0L, "CFDTMSTS");
        requireLabel(0xFFD23400L, "CFID");
        requireLabel(0xFFD24200L, "CFDTMID16");
        requireLabel(0xFFC5D000L, "ICUSCMD");
        requireLabel(0xFFC5D00CL, "ICUSSTS");

        // Structured overlays from ApplyP1MSfrTypes.
        requireDataType(0xFFFFB110L, "EIC_Register", 2);
        requireDataType(0xFFFFB248L, "EIC_Register", 2);
        requireDataType(0xFFC5D000L, "ICUS_Command", 4);
        requireDataType(0xFFC5D00CL, "ICUS_Status", 4);
        requireDataType(0xFFD20178L, "RSCFD_CFSTS", 4);
        requireDataType(0xFFD20260L, "RSCFD_CFDTMC", 1);
        requireDataType(0xFFD23400L, "RSCFD_CommonFifoFrame", 0x20);
        requireDataType(0xFFD24200L, "RSCFD_TxMessageBuffer", 0x20);

        // LocalRAM overlays from ApplyRamTypes (absolute addresses; GP context
        // already seeded by ApplyP1MDeviceProfile).
        requireDataType(0xFEBF0FD0L, "PayloadFlashCallback", 4);
        requireDataType(0xFEBF0FE0L, "PayloadCrcTrailer", 16);
        requireDataType(0xFEBF0FF0L, "PayloadCmacTag", 16);
        requireDataType(0xFEBF02E8L, "SecocNvmObject15", 32);
        requireDataType(0xFEBF0B08L, "SecocNvmWorkbufRoot", 384);
        requireDataType(0xFEBF2D08L, "PayloadDid0201KeyMaterial", 16);
        requireDataType(0xFEBF2CF8L, "PayloadDid0202Iv", 16);
        requireLabel(0xFEBF0FD0L, "payload_flash_callback");
        requireLabel(0xFEBF0B08L, "secoc_nvm_triplicate_workbuf_root");
        requireLabel(0xFEBF02F8L, "secoc_nvm_object15_key_field_ram");
        requireLabel(0xFEBF0C28L, "secoc_nvm_object15_raw_workbuf");
        // Every enabled checkpoint RAM mirror must be present and correctly typed.
        requireCheckpointCsv(checkpointCsv);
        requireDefinedLength(0xFEBEB1A4L, 1);
        requireDefinedLength(0xFEBFC81FL, 1);
        requireDefinedLength(0xFEBF2B16L, 1);
        requireLabel(0xFEBEB1A4L, "application_system_transition_phase_live");
        requireLabel(0xFEBF2D08L, "payload_did_0201_key_material");

        // Register context is mandatory after applying the device profile.
        Address bootAddr = toAddr(0x800L);
        Address appAddr = toAddr(0x30000L);
        requireRegister(bootAddr, "gp", 0xFEBF9800L);
        requireRegister(bootAddr, "tp", 0x869CL);
        requireRegister(appAddr, "gp", 0xFEBEB800L);
        requireRegister(appAddr, "tp", 0x23EE4L);
        requireRegister(toAddr(0x1b0L), "sp", 0xFEBE8000L);
        requireRegister(toAddr(0x20880L), "sp", 0xFEBE2000L);

        requireConvention(0x650acL, "__interrupt");
        requireConvention(0x650eeL, "__interrupt");
        for (long handler : new long[]{
                0x61d88L, 0x64b3eL, 0x70a54L, 0x70320L, 0x703caL,
                0x70476L, 0x6506aL, 0x65028L, 0x650acL, 0x650eeL, 0x65130L}) {
            requireConvention(handler, "__interrupt");
        }
        // ApplyCallingConventions pins the RH850/G3 ABI on normal functions.
        requireConvention(0x1b0L, "__stdcall");
        requireConvention(0x6fecL, "__stdcall");
        requireConvention(0x7068L, "__stdcall");
        requireConvention(0x704cL, "__stdcall");
        requireConvention(0x614aL, "__stdcall");
        requireConvention(0x87610L, "__stdcall");
        requireConvention(0x87636L, "__stdcall");
        requireReference(0x20010L, 0x61d88L);
        requireReference(0x20090L, 0x64b3eL);
        int intbpRefs = 0;
        for (int channel = 0; channel < 384; channel++) {
            long entry = 0x20200L + channel * 4L;
            long target = Integer.toUnsignedLong(getInt(toAddr(entry)));
            if (target < 0x100000L && (target & 1L) == 0L) {
                requireReference(entry, target);
                intbpRefs++;
            }
        }
        if (intbpRefs != 382) {
            fail("INTBP CodeFlash reference count=" + intbpRefs + " expected=382");
        }
        Function normal292 = getFunctionAt(toAddr(0x87610L));
        if (normal292 != null && "__interrupt".equals(normal292.getCallingConventionName())) {
            fail("normal ICU dispatch callee 0x87610 must not use __interrupt");
        }
        Function normal293 = getFunctionAt(toAddr(0x87636L));
        if (normal293 != null && "__interrupt".equals(normal293.getCallingConventionName())) {
            fail("normal ICU dispatch callee 0x87636 must not use __interrupt");
        }

        // Census: every non-thunk function must have an explicit RH850 prototype.
        int unknown = 0;
        var fit = currentProgram.getFunctionManager().getFunctions(true);
        while (fit.hasNext()) {
            Function f = fit.next();
            if (f.isThunk()) continue;
            String cc = f.getCallingConventionName();
            if (cc == null || "unknown".equals(cc) || "default".equals(cc)) {
                unknown++;
                if (unknown <= 5) {
                    fail(String.format("function 0x%x (%s) convention unset (%s)",
                            f.getEntryPoint().getOffset(), f.getName(), cc));
                }
            }
        }
        if (unknown > 5) {
            fail("... and " + (unknown - 5) + " more functions with unset calling convention");
        }

        println("ASSERT project-invariants: failures=" + failures.size());
        if (!failures.isEmpty()) {
            throw new IllegalStateException(failures.size() + " project invariant failures: "
                    + String.join("; ", failures));
        }
    }
}
