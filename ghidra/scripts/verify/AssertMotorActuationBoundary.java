//@author kaikozlov
//@category Verification
// Lock the independently recovered motor-control/PWM chain and the bounded
// negative between authenticated 0x2E4 command state and d/q current references.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;
import ghidra.program.model.symbol.Symbol;

import java.util.HashSet;
import java.util.Locale;
import java.util.Set;

public class AssertMotorActuationBoundary extends GhidraScript {
    private int failures = 0;
    private int referenceCensuses = 0;
    private int callEdges = 0;

    private void fail(String message) {
        failures++;
        printerr("ASSERT-FAIL motor-actuation: " + message);
    }

    private String refKey(Reference ref) {
        return String.format(Locale.ROOT, "%08x:%s",
                ref.getFromAddress().getOffset(), ref.getReferenceType().toString());
    }

    private void assertExactRefs(long destination, String... expected) {
        Set<String> actual = new HashSet<>();
        ReferenceIterator refs = currentProgram.getReferenceManager().getReferencesTo(toAddr(destination));
        while (refs.hasNext()) actual.add(refKey(refs.next()));
        Set<String> wanted = Set.of(expected);
        if (!actual.equals(wanted)) {
            fail(String.format(Locale.ROOT, "refs to 0x%x expected=%s actual=%s",
                    destination, wanted, actual));
        }
        referenceCensuses++;
    }

    private void assertCall(long caller, long callee) {
        Function source = getFunctionAt(toAddr(caller));
        if (source == null) {
            fail(String.format(Locale.ROOT, "missing caller function 0x%x", caller));
            return;
        }
        for (Function target : source.getCalledFunctions(monitor)) {
            if (target.getEntryPoint().getOffset() == callee) {
                callEdges++;
                return;
            }
        }
        fail(String.format(Locale.ROOT, "missing call 0x%x -> 0x%x", caller, callee));
    }

    private void assertNamedFunction(long address, String expectedName) {
        Function fn = getFunctionAt(toAddr(address));
        if (fn == null) {
            fail(String.format(Locale.ROOT, "missing function 0x%x", address));
        } else if (!expectedName.equals(fn.getName())) {
            fail(String.format(Locale.ROOT, "function 0x%x name expected=%s actual=%s",
                    address, expectedName, fn.getName()));
        }
    }

    private void assertSfr(long address, String expectedName) {
        Address target = toAddr(address);
        MemoryBlock block = currentProgram.getMemory().getBlock(target);
        if (block == null || !"SFR_TSG3".equals(block.getName()) || !block.isVolatile()) {
            fail(String.format(Locale.ROOT, "0x%x is not in volatile SFR_TSG3", address));
        }
        Symbol symbol = currentProgram.getSymbolTable().getPrimarySymbol(target);
        if (symbol == null || !expectedName.equals(symbol.getName())) {
            fail(String.format(Locale.ROOT, "0x%x label expected=%s actual=%s",
                    address, expectedName, symbol == null ? "<none>" : symbol.getName()));
        }
    }

    @Override
    public void run() throws Exception {
        // High-rate path and independently recovered current-control/PWM chain.
        assertCall(0x656f0L, 0x60ddcL);
        assertCall(0x656f0L, 0x5784cL);
        assertCall(0x5ce0cL, 0x47c3cL);
        assertCall(0x5cea8L, 0x35960L);
        assertCall(0x5d18cL, 0x37644L);
        assertCall(0x5d18cL, 0x37712L);
        assertCall(0x5d18cL, 0x36902L);
        assertCall(0x5d18cL, 0x36a44L);
        assertCall(0x5d18cL, 0x38464L);
        assertCall(0x5d18cL, 0x38554L);
        assertCall(0x5d18cL, 0x3875aL);
        assertCall(0x3875aL, 0x56b18L);
        assertCall(0x5d18cL, 0x569a8L);
        assertCall(0x5d18cL, 0x56d3eL);
        assertCall(0x65944L, 0x60bfaL);
        assertCall(0x659aaL, 0x60bfaL);

        assertNamedFunction(0x47c3cL, "dual_motor_phase_current_conditioning");
        assertNamedFunction(0x35960L, "dual_motor_clarke_park_feedback");
        assertNamedFunction(0x36902L, "dq_current_pi_axis_a");
        assertNamedFunction(0x36a44L, "dq_current_pi_axis_b");
        assertNamedFunction(0x60ddcL, "tsg3_pwm_compare_commit");

        assertSfr(0xffe70180L, "TSG30CMPWE");
        assertSfr(0xffe70184L, "TSG30CMPVE");
        assertSfr(0xffe70188L, "TSG30CMPUE");
        assertSfr(0xffe71180L, "TSG31CMPWE");
        assertSfr(0xffe71184L, "TSG31CMPVE");
        assertSfr(0xffe71188L, "TSG31CMPUE");

        // Exact direct-reference census for the command-side stopping boundary.
        // BF84 has writes only; BF9A has a self-history read inside its producer.
        assertExactRefs(0xfebebf84L,
                "000c8300:WRITE", "000c8678:WRITE");
        assertExactRefs(0xfebebf9aL,
                "000c82f4:WRITE", "000c85be:READ", "000c8628:WRITE");
        assertExactRefs(0xfebebfa2L,
                "000c82d8:WRITE", "000c868a:WRITE",
                "000ca6ce:READ", "000cb730:READ");
        assertExactRefs(0xfebeae16L,
                "000bb008:READ", "000bce3a:READ", "000be17a:WRITE",
                "000cb764:WRITE", "000fd53c:READ", "000fd5f8:READ",
                "000bb102:WRITE", "000bb170:WRITE");
        assertExactRefs(0xfebee8caL,
                "000bce3e:WRITE", "000be52c:WRITE");
        assertExactRefs(0xfebeeb1cL, "000fd540:WRITE");
        assertExactRefs(0xfebeeba4L, "000fd5fc:WRITE");

        // The proved current-reference state is independently produced in the
        // CH0 worker; none of the command snapshot owners above writes it.
        assertExactRefs(0xfebe6d28L,
                "0005ae30:WRITE", "0005ae44:READ", "0005b9aa:READ",
                "0005bdf8:READ", "0005c528:READ", "00036a74:READ",
                "00038246:READ", "00038356:READ", "00037748:WRITE");
        assertExactRefs(0xfebe6d2aL,
                "0005ae32:WRITE", "0005ae46:READ", "0005b9b0:READ",
                "0005bdfe:READ", "0005c52e:READ", "00036930:READ",
                "00038244:READ", "00038358:READ", "00037778:WRITE");

        println("ASSERT motor-actuation-boundary: call_edges=" + callEdges
                + " reference_censuses=" + referenceCensuses
                + " failures=" + failures);
        if (failures != 0) {
            throw new IllegalStateException("AssertMotorActuationBoundary failures=" + failures);
        }
    }
}
