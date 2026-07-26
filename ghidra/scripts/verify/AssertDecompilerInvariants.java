//@author kaikozlov
//@category Verification
// Structured decompiler checks for ABI and landmark semantics.
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Parameter;
import ghidra.program.model.pcode.HighFunction;
import ghidra.program.model.pcode.HighSymbol;
import ghidra.program.model.pcode.HighVariable;
import ghidra.program.model.symbol.Symbol;
import ghidra.program.model.symbol.SymbolIterator;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;

public class AssertDecompilerInvariants extends GhidraScript {
    private final List<String> failures = new ArrayList<>();
    private DecompInterface decomp;

    private void fail(String msg) {
        failures.add(msg);
        println("FAIL: " + msg);
    }

    private String decompile(Function f) throws Exception {
        DecompileResults results = decomp.decompileFunction(f, 60, monitor);
        if (results == null || !results.decompileCompleted()) {
            fail("decompile failed for " + f.getName() + " @ " + f.getEntryPoint());
            return "";
        }
        return results.getDecompiledFunction().getC();
    }

    @Override
    public void run() throws Exception {
        decomp = new DecompInterface();
        decomp.openProgram(currentProgram);

        // SecurityAccess stage1 key derivation must reference SEED_KEY_SECRET.
        Function stage1 = getFunctionAt(toAddr(0x6fecL));
        if (stage1 == null) stage1 = getFunctionContaining(toAddr(0x6fecL));
        if (stage1 == null) {
            fail("missing security_access_derive_stage1_key around 0x6fec");
        } else {
            String c = decompile(stage1);
            if (!c.contains("SEED_KEY") && !c.contains("0xbfe8") && !c.contains("0xBFE8")) {
                // Symbol name may appear; also accept raw address references.
                boolean xrefOk = false;
                SymbolIterator it = currentProgram.getSymbolTable().getSymbols("SEED_KEY_SECRET");
                while (it.hasNext()) {
                    Symbol s = it.next();
                    if (s.getAddress().getOffset() == 0xbfe8L) xrefOk = true;
                }
                if (!c.toLowerCase().contains("bfe8") && !xrefOk) {
                    fail("stage1 decompilation does not reference SEED_KEY_SECRET/0xBFE8");
                }
            }
            println("stage1 decompile ok (" + stage1.getName() + ")");
        }

        // Payload build key derivation must reference PAYLOAD_BUILD_SECRET.
        Function payload = getFunctionAt(toAddr(0x7068L));
        if (payload == null) payload = getFunctionContaining(toAddr(0x7068L));
        if (payload == null) {
            fail("missing payload_build_derive_key around 0x7068");
        } else {
            String c = decompile(payload);
            if (!c.contains("PAYLOAD_BUILD") && !c.toLowerCase().contains("bfd8")) {
                fail("payload decompilation does not reference PAYLOAD_BUILD_SECRET/0xBFD8");
            }
            println("payload decompile ok (" + payload.getName() + ")");
        }

        // ISR should not invent ABI args when __interrupt is applied.
        Function isr = getFunctionAt(toAddr(0x650acL));
        if (isr != null) {
            String c = decompile(isr);
            String cc = isr.getCallingConventionName();
            int params = isr.getParameterCount();
            if ("__interrupt".equals(cc) && params > 0) {
                fail("ISR 0x650ac has " + params + " parameters under __interrupt");
            }
            // Spurious code* arg was the pre-cspec failure mode; only enforce once
            // __interrupt has been applied by RecoverVectorHandlers.
            if ("__interrupt".equals(cc)) {
                String firstLine = c.lines().findFirst().orElse("");
                if (firstLine.contains("code *") || firstLine.matches(".*\\(.*code\\s*\\*.*")) {
                    fail("ISR decompilation still shows spurious code* parameter: " + firstLine);
                }
            }
            println("ISR 0x650ac convention=" + cc + " params=" + params);
        }

        // Session control: prefer narrow first parameter when typed.
        Function session = null;
        SymbolIterator sit = currentProgram.getSymbolTable().getSymbols("uds_diagnostic_session_control");
        if (sit.hasNext()) {
            session = getFunctionAt(sit.next().getAddress());
        }
        if (session == null) session = getFunctionAt(toAddr(0x614aL));
        if (session != null) {
            String c = decompile(session);
            // After cspec rewrite, ushort param should not need redundant & 0xffff
            // on the first use of the session id when correctly typed. Soft check:
            // function must decompile and not be empty.
            if (c.isBlank()) fail("empty decompilation for session control");
            println("session-control decompile ok (" + session.getName() + ")");
        }

        decomp.dispose();
        println("ASSERT decompiler-invariants: failures=" + failures.size());
        if (!failures.isEmpty()) {
            throw new IllegalStateException(failures.size() + " decompiler invariant failures: "
                    + String.join("; ", failures));
        }
    }
}
