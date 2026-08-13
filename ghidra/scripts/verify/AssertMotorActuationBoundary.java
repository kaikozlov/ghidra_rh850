//@author kaikozlov
//@category Verification
// Lock the independently recovered motor-control/PWM chain and the bounded
// negative between both authenticated steering command modes and d/q current references.
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

        // Protected 0x131 LTA command stages execute before the common selector.
        assertCall(0xcb86eL, 0xc8de0L);
        assertCall(0xcb86eL, 0xc978eL);
        assertCall(0xc978eL, 0xc96d2L);
        assertCall(0xcb86eL, 0xc97b2L);
        assertCall(0xcb86eL, 0xc8dc8L);
        assertCall(0xc8dc8L, 0xc8d62L);
        assertCall(0xcb86eL, 0xca7f0L);

        assertNamedFunction(0x47c3cL, "dual_motor_phase_current_conditioning");
        assertNamedFunction(0x35960L, "dual_motor_clarke_park_feedback");
        assertNamedFunction(0x36902L, "dq_current_pi_axis_a");
        assertNamedFunction(0x36a44L, "dq_current_pi_axis_b");
        assertNamedFunction(0x60ddcL, "tsg3_pwm_compare_commit");
        assertNamedFunction(0xca354L, "steering_request_source_arbitration");
        assertNamedFunction(0xca3b8L, "steering_lta_mode_latch");
        assertNamedFunction(0xca3f8L, "steering_lka_torque_mode_latch");
        assertNamedFunction(0xc8de0L, "lta_angle_command_smoothing");
        assertNamedFunction(0xc8d62L, "lta_internal_command_rate_limit");
        assertNamedFunction(0xca6b8L, "steering_command_mode_select_stage");
        assertNamedFunction(0xc07faL, "steering_command_plausibility_monitor");

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

        // Base-relative decompiler aliases are locked by canonical-address xrefs.
        // 0x2E4 STEER_REQUEST: F02A is copied by BA43A to ACFF, which CA354 reads.
        assertExactRefs(0xfebef02aL,
                "00057126:WRITE", "0005b3b2:WRITE", "000ba7fe:READ");
        assertExactRefs(0xfebeacffL,
                "000ba802:WRITE", "000bdfa8:WRITE", "000ca36a:READ");

        // Protected 0x131 STEERING_LTA_2 angle/controller branch.
        assertExactRefs(0xfebead4fL,
                "000ba868:WRITE", "000be06e:WRITE", "000c9ef8:READ");
        assertExactRefs(0xfebead50L,
                "000ba86e:WRITE", "000be070:WRITE", "000ca360:READ");
        assertExactRefs(0xfebead52L,
                "000ba882:WRITE", "000be074:WRITE", "000ca3c0:READ");
        assertExactRefs(0xfebead53L,
                "000ba888:WRITE", "000be076:WRITE");
        assertExactRefs(0xfebead54L,
                "000ba88e:WRITE", "000be078:WRITE", "000ca3c2:READ");
        assertExactRefs(0xfebeae60L,
                "000ba874:WRITE", "000be2ae:WRITE", "000c8de4:READ", "000ca0bc:READ");
        assertExactRefs(0xfebebff0L,
                "000c8b0c:WRITE", "000c8e30:WRITE", "000c8ed2:READ", "000c9004:READ");
        assertExactRefs(0xfebec0beL,
                "000c8be4:WRITE", "000c9774:WRITE", "000c97b6:READ");
        assertExactRefs(0xfebec0c8L,
                "000c8c2c:WRITE", "000c8d62:READ", "000c97e6:WRITE");
        assertExactRefs(0xfebec0d6L,
                "000c8c30:WRITE", "000c8dc2:WRITE", "000ca6c8:READ");

        // The common command cone continues beyond the former C1BC stopping point.
        assertExactRefs(0xfebec1bcL,
                "000cabb4:WRITE", "000cacba:WRITE", "000caccc:READ", "000cad5a:READ");
        assertExactRefs(0xfebec1d4L,
                "000bf8f6:READ", "000cabe8:WRITE", "000cae50:WRITE", "000cb454:READ");
        assertExactRefs(0xfebeb788L,
                "000bf7e4:WRITE", "000bf91a:WRITE", "000c081e:READ");
        assertExactRefs(0xfebeb87eL,
                "000c02fe:READ", "000c05d4:WRITE", "000c07dc:READ",
                "000c08c6:WRITE", "000c0d00:WRITE", "000c0ef4:READ");

        // Protected 0x132 parallel-PDU audit: after the BA43A snapshot, all six
        // recovered scalar destinations have no runtime reader at all.
        // Signal 196 is a useful decompiler-alias regression: the instruction
        // graph reads canonical byte FEBE8001 even though pseudocode currently
        // renders it as DAT_febe8000._1_1_.
        assertExactRefs(0xfebe8001L,
                "0004ab90:DATA", "000572b0:READ", "00057d5a:WRITE");
        assertExactRefs(0xfebef063L,
                "000572b4:WRITE", "0005b348:WRITE", "000ba8f4:READ");
        assertExactRefs(0xfebead04L, "000ba8d6:WRITE", "000bdfb2:WRITE");
        assertExactRefs(0xfebead05L, "000ba8dc:WRITE", "000bdfb4:WRITE");
        assertExactRefs(0xfebead06L, "000ba8ea:WRITE", "000bdfb6:WRITE");
        assertExactRefs(0xfebead07L, "000ba8f8:WRITE", "000bdfb8:WRITE");
        assertExactRefs(0xfebeae28L, "000ba8e2:WRITE", "000be25a:WRITE");
        assertExactRefs(0xfebeae2aL, "000ba8f0:WRITE", "000be25e:WRITE");

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

        // Application WDBI service-mode controls 0x110A/0x110C/0x110D enter
        // system submode 0x520 and operate on a distinct service-state island.
        // Pin representative computed outputs and their snapshots so a future
        // rebuild cannot silently invent a transfer into the proved d/q state
        // above. These exact censuses bound static dataflow only; they do not
        // claim anything about unobserved hardware-side effects.
        assertExactRefs(0xfebeb3e0L,
                "000b6758:WRITE", "000b6880:WRITE", "000b68b8:WRITE",
                "000b68d6:WRITE", "000bd8bc:WRITE", "000b6682:READ");
        assertExactRefs(0xfebeb448L,
                "000b750a:WRITE", "000b7664:WRITE", "000bd900:WRITE",
                "000b7686:WRITE", "000b76a4:WRITE", "000b76d4:READ");
        assertExactRefs(0xfebeb44cL,
                "000bd916:WRITE", "000bd928:READ", "000be826:READ",
                "000b777a:WRITE", "000b778c:WRITE", "000b76bc:WRITE",
                "000b7744:WRITE");
        assertExactRefs(0xfebeb452L,
                "000bd914:WRITE", "000bd922:READ", "000be820:READ",
                "000b7778:WRITE", "000b778a:WRITE", "000b7314:READ",
                "000b76ba:WRITE", "000b7746:WRITE");
        assertExactRefs(0xfebeb000L,
                "000b67de:READ", "000bd8ec:WRITE", "000be81c:WRITE");
        assertExactRefs(0xfebeb002L,
                "000bd8de:WRITE", "000be812:WRITE");
        assertExactRefs(0xfebeb004L,
                "000b7586:READ", "000bd932:WRITE", "000be82c:WRITE");
        assertExactRefs(0xfebeb006L,
                "000bd924:WRITE", "000be822:WRITE");

        println("ASSERT motor-actuation-boundary: call_edges=" + callEdges
                + " reference_censuses=" + referenceCensuses
                + " failures=" + failures);
        if (failures != 0) {
            throw new IllegalStateException("AssertMotorActuationBoundary failures=" + failures);
        }
    }
}
