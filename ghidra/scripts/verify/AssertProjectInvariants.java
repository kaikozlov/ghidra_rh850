//@author kaikozlov
//@category Verification
// Check curated project invariants: critical functions, labels, calling
// conventions, memory blocks, and boot/application register context.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.symbol.Symbol;
import ghidra.program.model.symbol.SymbolTable;
import ghidra.program.model.lang.Register;
import ghidra.program.model.lang.RegisterValue;
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

    @Override
    public void run() throws Exception {
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

        // Optional device-profile RAM/SFR windows (present after Milestone 3).
        MemoryBlock localRam = currentProgram.getMemory().getBlock("LocalRAM");
        if (localRam != null) {
            println("LocalRAM block present: " + localRam.getStart() + ".." + localRam.getEnd());
        }
        for (String sfrName : new String[]{"SFR_EIC", "SFR_RSCFD", "SFR_ICUS"}) {
            MemoryBlock sfr = currentProgram.getMemory().getBlock(sfrName);
            if (sfr != null) {
                println(sfrName + " block present: " + sfr.getStart() + ".." + sfr.getEnd());
                if (!sfr.isVolatile()) fail(sfrName + " block should be volatile");
            }
        }

        // Register context when seeded.
        Address bootAddr = toAddr(0x800L);
        Address appAddr = toAddr(0x30000L);
        Register gp = currentProgram.getRegister("gp");
        if (gp != null) {
            RegisterValue bootGp = currentProgram.getProgramContext().getRegisterValue(gp, bootAddr);
            RegisterValue appGp = currentProgram.getProgramContext().getRegisterValue(gp, appAddr);
            if (bootGp != null && bootGp.hasValue()) {
                requireRegister(bootAddr, "gp", 0xFEBF9800L);
                requireRegister(bootAddr, "tp", 0x869CL);
            }
            if (appGp != null && appGp.hasValue()) {
                requireRegister(appAddr, "gp", 0xFEBEB800L);
                requireRegister(appAddr, "tp", 0x23EE4L);
            }
        }

        // Interrupt conventions when applied.
        Function isr292 = getFunctionAt(toAddr(0x650acL));
        if (isr292 != null) {
            String cc = isr292.getCallingConventionName();
            if ("__interrupt".equals(cc)) {
                println("ISR 0x650ac uses __interrupt");
            } else {
                println("NOTE: ISR 0x650ac convention=" + cc
                        + " (__interrupt applied in interrupt-recovery milestone)");
            }
        }

        println("ASSERT project-invariants: failures=" + failures.size());
        if (!failures.isEmpty()) {
            throw new IllegalStateException(failures.size() + " project invariant failures: "
                    + String.join("; ", failures));
        }
    }
}
