//@author kaikozlov
//@category Verification
// Structured decompiler checks for ABI and landmark semantics.
// Requires ApplyCallingConventions (and RecoverVectorHandlers for ISRs):
// normal landmarks must be __stdcall; ISR wrappers must be __interrupt.
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import ghidra.program.model.listing.Parameter;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;
import ghidra.program.model.symbol.SymbolIterator;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.HexFormat;

public class AssertDecompilerInvariants extends GhidraScript {
    private final List<String> failures = new ArrayList<>();
    private final List<String> signatures = new ArrayList<>();
    private final Set<Long> signedAddrs = new HashSet<>();
    private DecompInterface decomp;

    private void fail(String msg) {
        failures.add(msg);
        println("FAIL: " + msg);
    }

    private Function requireFunction(long addr, String expectedName) {
        Function f = getFunctionAt(toAddr(addr));
        if (f == null) f = getFunctionContaining(toAddr(addr));
        if (f == null) {
            fail(String.format("missing function around 0x%x (%s)", addr, expectedName));
            return null;
        }
        if (expectedName != null && !expectedName.equals(f.getName())) {
            fail(String.format("function at 0x%x named %s, expected %s",
                    addr, f.getName(), expectedName));
        }
        return f;
    }

    private void requireConvention(Function f, String expected) {
        if (f == null) return;
        String actual = f.getCallingConventionName();
        if (actual == null || !actual.equals(expected)) {
            fail(String.format("function 0x%x (%s) convention=%s expected=%s",
                    f.getEntryPoint().getOffset(), f.getName(), actual, expected));
        }
    }

    private String decompile(Function f) throws Exception {
        DecompileResults results = decomp.decompileFunction(f, 60, monitor);
        if (results == null || !results.decompileCompleted()) {
            fail("decompile failed for " + f.getName() + " @ " + f.getEntryPoint());
            return "";
        }
        String c = results.getDecompiledFunction().getC();
        String normalized = c.replaceAll("\\s+", " ").trim();
        String digest = HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256")
                .digest(normalized.getBytes(StandardCharsets.UTF_8)));
        long offset = f.getEntryPoint().getOffset();
        if (signedAddrs.add(offset)) {
            signatures.add(String.format("%08x,%s,%s,%d,%s",
                    offset, f.getName(), f.getCallingConventionName(),
                    f.getParameterCount(), digest));
        }
        return c;
    }

    private boolean hasReferenceFrom(Function function, long destination) {
        ReferenceIterator refs = currentProgram.getReferenceManager()
                .getReferencesTo(toAddr(destination));
        while (refs.hasNext()) {
            Reference ref = refs.next();
            if (function.getBody().contains(ref.getFromAddress())) return true;
        }
        return false;
    }

    private void checkNoUnknownConventions() {
        int unknown = 0;
        int stdcall = 0;
        int interrupt = 0;
        int other = 0;
        FunctionIterator it = currentProgram.getFunctionManager().getFunctions(true);
        while (it.hasNext()) {
            Function f = it.next();
            if (f.isThunk()) continue;
            String cc = f.getCallingConventionName();
            if ("__stdcall".equals(cc)) stdcall++;
            else if ("__interrupt".equals(cc)) interrupt++;
            else if (cc == null || "unknown".equals(cc) || "default".equals(cc)) {
                unknown++;
                if (unknown <= 8) {
                    fail(String.format("function 0x%x (%s) still has unset convention (%s)",
                            f.getEntryPoint().getOffset(), f.getName(), cc));
                }
            } else {
                other++;
                fail(String.format("function 0x%x (%s) unexpected convention %s",
                        f.getEntryPoint().getOffset(), f.getName(), cc));
            }
        }
        if (unknown > 8) {
            fail(String.format("... and %d more functions still on unknown/default",
                    unknown - 8));
        }
        println(String.format("convention census: __stdcall=%d __interrupt=%d unknown=%d other=%d",
                stdcall, interrupt, unknown, other));
        if (stdcall == 0) fail("expected at least one __stdcall function after ApplyCallingConventions");
        if (interrupt == 0) fail("expected at least one __interrupt ISR wrapper");
    }

    @Override
    public void run() throws Exception {
        decomp = new DecompInterface();
        decomp.openProgram(currentProgram);

        checkNoUnknownConventions();

        // SecurityAccess stage1 key derivation must reference SEED_KEY_SECRET.
        Function stage1 = requireFunction(0x6fecL, "security_access_derive_stage1_key");
        requireConvention(stage1, "__stdcall");
        if (stage1 != null) {
            String c = decompile(stage1);
            if (!hasReferenceFrom(stage1, 0xbfe8L)) {
                fail("stage1 function has no reference to SEED_KEY_SECRET/0xBFE8");
            }
            if (!c.contains("SEED_KEY") && !c.toLowerCase().contains("bfe8")) {
                fail("stage1 decompilation does not render SEED_KEY_SECRET/0xBFE8");
            }
            println("stage1 decompile ok (" + stage1.getName() + ")");
        }

        // Payload build key derivation must reference PAYLOAD_BUILD_SECRET.
        Function payload = requireFunction(0x7068L, "payload_build_derive_key");
        requireConvention(payload, "__stdcall");
        if (payload != null) {
            String c = decompile(payload);
            if (!hasReferenceFrom(payload, 0xbfd8L)) {
                fail("payload function has no reference to PAYLOAD_BUILD_SECRET/0xBFD8");
            }
            if (!c.contains("PAYLOAD_BUILD") && !c.toLowerCase().contains("bfd8")) {
                fail("payload decompilation does not reference PAYLOAD_BUILD_SECRET/0xBFD8");
            }
            println("payload decompile ok (" + payload.getName() + ")");
        }

        // Expected-key computation is a second SecurityAccess ABI landmark.
        Function expected = requireFunction(0x704cL, "security_access_compute_expected_key");
        requireConvention(expected, "__stdcall");
        if (expected != null) {
            decompile(expected);
            println("expected-key decompile ok (" + expected.getName() + ")");
        }

        // ISR wrappers must use __interrupt and must not invent ABI args.
        for (long addr : new long[]{0x650acL, 0x650eeL}) {
            Function isr = requireFunction(addr, null);
            requireConvention(isr, "__interrupt");
            if (isr == null) continue;
            String c = decompile(isr);
            int params = isr.getParameterCount();
            if (params > 0) {
                fail(String.format("ISR 0x%x has %d parameters under __interrupt",
                        addr, params));
            }
            String firstLine = c.lines().findFirst().orElse("");
            if (firstLine.contains("code *") || firstLine.matches(".*\\(.*code\\s*\\*.*")) {
                fail("ISR decompilation still shows spurious code* parameter: " + firstLine);
            }
            println(String.format("ISR 0x%x convention=__interrupt params=%d", addr, params));
        }

        // Normal ICU dispatch callees use the RH850/G3 ABI, not __interrupt.
        Function dispatch292 = requireFunction(0x87610L, "icus_interrupt_channel292_dispatch");
        requireConvention(dispatch292, "__stdcall");
        if (dispatch292 != null) {
            decompile(dispatch292);
            println("ICU dispatch 0x87610 decompile ok (" + dispatch292.getName() + ")");
        }

        // Session control: prefer narrow first parameter when typed.
        Function session = null;
        SymbolIterator sit = currentProgram.getSymbolTable()
                .getSymbols("uds_diagnostic_session_control");
        if (sit.hasNext()) {
            session = getFunctionAt(sit.next().getAddress());
        }
        if (session == null) session = getFunctionAt(toAddr(0x614aL));
        if (session == null) {
            fail("missing uds_diagnostic_session_control");
        } else {
            requireConvention(session, "__stdcall");
            String c = decompile(session);
            if (c.isBlank()) fail("empty decompilation for session control");
            Parameter[] params = session.getParameters();
            if (params.length > 0 && params[0].getDataType().getLength() > 2) {
                fail("session-control first parameter widened to "
                        + params[0].getDataType().getDisplayName());
            }
            println("session-control decompile ok (" + session.getName() + ")");
        }

        // Boot reset is a non-ISR entry that must keep the normal ABI.
        Function boot = requireFunction(0x1b0L, "boot_reset_startup");
        requireConvention(boot, "__stdcall");
        if (boot != null) {
            decompile(boot);
            println("boot_reset_startup decompile ok");
        }

        // Programming handoff prerequisites: phase != 0x11 and internal failure 1.
        Function handoff = requireFunction(0x4c960L, "application_programming_handoff_prerequisites");
        requireConvention(handoff, "__stdcall");
        if (handoff != null) {
            String c = decompile(handoff);
            if (!c.contains("0x11") && !c.contains("'\\x11'")) {
                fail("handoff prerequisites decompilation missing phase 0x11 check");
            }
            println("handoff prerequisites decompile ok (" + handoff.getName() + ")");
        }

        // SecurityAccess send-key must expose NRC 0x35 / 0x36 failure paths.
        // The expected-key call at 0x5468 is asserted in raw-image suites; Ghidra's
        // recovered function body does not always own that CALL reference.
        Function sendKey = requireFunction(0x53f2L, "uds_security_access_send_key");
        requireConvention(sendKey, "__stdcall");
        if (sendKey != null) {
            String c = decompile(sendKey);
            if (!c.contains("0x35") || !c.contains("0x36")) {
                fail("send-key decompilation missing NRC 0x35/0x36 literals");
            }
            println("send-key decompile ok (" + sendKey.getName() + ")");
        }

        // RequestDownload is the payload-gate entry landmark.
        Function download = requireFunction(0x5d68L, "uds_request_download");
        requireConvention(download, "__stdcall");
        if (download != null) {
            decompile(download);
            println("request-download decompile ok (" + download.getName() + ")");
        }

        // Checkpoint object update API is the shared writer sink.
        Function nvmUpdate = requireFunction(0x65cd8L, "secoc_nvm_object_update");
        requireConvention(nvmUpdate, "__stdcall");
        if (nvmUpdate != null) {
            decompile(nvmUpdate);
            println("secoc_nvm_object_update decompile ok (" + nvmUpdate.getName() + ")");
        }

        // Application ClearDiagnosticInformation is the Stage-2 service-callback landmark.
        Function appReset = requireFunction(0x8b1f0L, "application_clear_diagnostic_information_callback");
        requireConvention(appReset, "__stdcall");
        if (appReset != null) {
            decompile(appReset);
            println("application ClearDiagnosticInformation decompile ok (" + appReset.getName() + ")");
        }

        // Application SecurityAccess send-key exposes NRC 0x35 / 0x36.
        Function appSendKey = requireFunction(0x94a72L, "application_security_access_send_key");
        requireConvention(appSendKey, "__stdcall");
        if (appSendKey != null) {
            String c = decompile(appSendKey);
            if (!c.contains("0x35") || !c.contains("0x36")) {
                fail("application send-key decompilation missing NRC 0x35/0x36 literals");
            }
            println("application send-key decompile ok (" + appSendKey.getName() + ")");
        }

        decomp.dispose();
        String[] args = getScriptArgs();
        if (args.length > 1) {
            throw new IllegalArgumentException("expected at most one signature report path");
        }
        if (args.length == 1) {
            List<String> lines = new ArrayList<>();
            lines.add("address,name,calling_convention,parameter_count,normalized_c_sha256");
            lines.addAll(signatures);
            Files.writeString(Path.of(args[0]), String.join("\n", lines) + "\n");
            println("Wrote decompiler signature report: " + args[0]);
        }
        println("ASSERT decompiler-invariants: failures=" + failures.size());
        if (!failures.isEmpty()) {
            throw new IllegalStateException(failures.size() + " decompiler invariant failures: "
                    + String.join("; ", failures));
        }
    }
}
