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

    private void assertMappedLabel(long address, String expectedBlock, boolean expectedVolatile,
                                   String expectedName) {
        Address target = toAddr(address);
        MemoryBlock block = currentProgram.getMemory().getBlock(target);
        if (block == null || !expectedBlock.equals(block.getName())
                || block.isVolatile() != expectedVolatile) {
            fail(String.format(Locale.ROOT,
                    "0x%x block expected=%s volatile=%s actual=%s",
                    address, expectedBlock, expectedVolatile,
                    block == null ? "<none>" : block.getName() + "/" + block.isVolatile()));
        }
        Symbol symbol = currentProgram.getSymbolTable().getPrimarySymbol(target);
        if (symbol == null || !expectedName.equals(symbol.getName())) {
            fail(String.format(Locale.ROOT, "0x%x label expected=%s actual=%s",
                    address, expectedName, symbol == null ? "<none>" : symbol.getName()));
        }
    }

    private void assertSfr(long address, String expectedBlock, String expectedName) {
        assertMappedLabel(address, expectedBlock, true, expectedName);
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

        assertSfr(0xffe70180L, "SFR_TSG3", "TSG30CMPWE");
        assertSfr(0xffe70184L, "SFR_TSG3", "TSG30CMPVE");
        assertSfr(0xffe70188L, "SFR_TSG3", "TSG30CMPUE");
        assertSfr(0xffe71180L, "SFR_TSG3", "TSG31CMPWE");
        assertSfr(0xffe71184L, "SFR_TSG3", "TSG31CMPVE");
        assertSfr(0xffe71188L, "SFR_TSG3", "TSG31CMPUE");

        // Stage-6 acquisition correction: FEEF81E0/FEEF8A20 are Global RAM A
        // DMA rings, not peripheral SFRs. Their DMA sources are ADCG0/1 DIR00.
        assertMappedLabel(0xfeef81e0L, "GlobalRAM_A", false, "ADCG0_DMA_SAMPLE_RING");
        assertMappedLabel(0xfeef8a20L, "GlobalRAM_A", false, "ADCG1_DMA_SAMPLE_RING");
        assertSfr(0xfff91200L, "SFR_ADCG0", "ADCG0DIR00");
        assertSfr(0xfff92200L, "SFR_ADCG1", "ADCG1DIR00");
        assertSfr(0xffff8100L, "SFR_DMAC_CM", "DM00CM");
        assertSfr(0xffff8120L, "SFR_DMAC_CM", "DM10CM");

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

        // Hidden command-conditioning branch recovered in Stage 6. It stays in
        // foreground command/export state rather than writing the FEBE6Dxx d/q block.
        assertExactRefs(0xfebec144L,
                "000ca4ea:WRITE", "000ca6fa:WRITE", "000ca776:READ");
        assertExactRefs(0xfebec170L,
                "000ca50a:WRITE", "000ca77e:READ", "000ca7e6:WRITE",
                "000cb7b0:READ", "000cac40:READ");
        assertExactRefs(0xfebec1b8L,
                "000cac0e:WRITE", "000cac64:WRITE", "000cac7a:READ");
        assertExactRefs(0xfebeae6eL,
                "000bce0a:READ", "000be2c6:WRITE", "000cb80e:WRITE",
                "000bb69e:READ", "000bb762:READ", "000bb826:READ");

        // Complete direct-reference lock for the d/q-reference feeder state.
        // Only motor-runtime functions and explicit init/reinit writes own these
        // locations; RTE copies appear as READs only.
        assertExactRefs(0xfebe6d4eL,
                "0005ae16:WRITE", "00037b4a:WRITE", "00037726:READ");
        assertExactRefs(0xfebe6d50L,
                "0005ae18:WRITE", "00037b4c:WRITE", "0003772a:READ");
        assertExactRefs(0xfebe6d52L,
                "0005ae1a:WRITE", "00037b4e:WRITE", "00037770:READ");
        assertExactRefs(0xfebe6d54L,
                "0005ae1c:WRITE", "00037b50:WRITE", "0003777c:READ");
        assertExactRefs(0xfebe6d70L,
                "0005add6:WRITE", "00037966:READ", "00037b84:WRITE",
                "00037cd8:READ", "0003771a:READ");
        assertExactRefs(0xfebe6d7eL,
                "0005adee:WRITE", "00037962:READ", "00037cf4:WRITE",
                "00037712:READ");

        // Generic memcpy cannot provide a hidden application transfer into the
        // d/q state: its sole direct caller belongs to bootloader transfer code.
        assertExactRefs(0x153aL, "00004f84:UNCONDITIONAL_CALL");

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
