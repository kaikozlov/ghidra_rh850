//@author kaikozlov
//@category Verification
// Live-project assertions for application-facing Tx producer semantics.
//
// Phase B pins the CAN 0x260 producer graph. Later interface-closure phases may
// extend this script, but every assertion must remain address/data-flow based.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;

import java.util.HashSet;
import java.util.Locale;
import java.util.Set;

public class AssertApplicationTransmitSemantics extends GhidraScript {
    private int failures = 0;
    private int referenceCensuses = 0;
    private int callEdges = 0;
    private int instructionChecks = 0;

    private void fail(String message) {
        failures++;
        printerr("ASSERT-FAIL application-tx-semantics: " + message);
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

    private void assertInstruction(long address, String mnemonic, String... operands) {
        Instruction insn = currentProgram.getListing().getInstructionAt(toAddr(address));
        if (insn == null) {
            fail(String.format(Locale.ROOT, "missing instruction at 0x%x", address));
            return;
        }
        if (!mnemonic.equalsIgnoreCase(insn.getMnemonicString())) {
            fail(String.format(Locale.ROOT, "0x%x mnemonic expected=%s actual=%s",
                    address, mnemonic, insn.getMnemonicString()));
        }
        if (insn.getNumOperands() != operands.length) {
            fail(String.format(Locale.ROOT, "0x%x operand count expected=%d actual=%d",
                    address, operands.length, insn.getNumOperands()));
        } else {
            for (int i = 0; i < operands.length; i++) {
                String actual = insn.getDefaultOperandRepresentation(i);
                if (!operands[i].equalsIgnoreCase(actual)) {
                    fail(String.format(Locale.ROOT,
                            "0x%x operand %d expected=%s actual=%s",
                            address, i, operands[i], actual));
                }
            }
        }
        instructionChecks++;
    }

    private int readU16(long address) throws Exception {
        byte[] bytes = new byte[2];
        currentProgram.getMemory().getBytes(toAddr(address), bytes);
        return (bytes[0] & 0xff) | ((bytes[1] & 0xff) << 8);
    }

    private void assertU16(long address, int expected) throws Exception {
        int actual = readU16(address);
        if (actual != expected) {
            fail(String.format(Locale.ROOT, "u16 0x%x expected=0x%x actual=0x%x",
                    address, expected, actual));
        }
    }

    @Override
    public void run() throws Exception {
        // One foreground staging orchestrator owns all four CAN 0x260 producer
        // helpers. This is structural scheduling evidence, not an OEM name.
        assertCall(0x4ba8cL, 0x4b66cL);
        assertCall(0x4ba8cL, 0x4b900L);
        assertCall(0x4ba8cL, 0x4b976L);
        assertCall(0x4ba8cL, 0x4b9ccL);

        // Signal 0 / B0[7]: legacy public DBC labels this STEER_OVERRIDE, but
        // this calibration's upstream export byte is explicitly zeroed both by
        // init and by the normal steering-command export path, then copied
        // through the snapshot and Tx staging layers.
        assertExactRefs(0xfebead33L,
                "000bcd92:READ", "000be02e:WRITE", "000cb792:WRITE");
        assertExactRefs(0xfebee830L,
                "0004b9cc:READ", "000bcd96:WRITE", "000be564:WRITE");
        assertExactRefs(0xfebe8094L,
                "0004b9d0:WRITE", "0004bcf8:READ", "00058182:WRITE");
        assertInstruction(0xbe02eL, "sst.b", "0x77", "ep", "r0");
        assertInstruction(0xcb792L, "sst.b", "0x77", "ep", "r0");

        // Signal 1 / B0[4]: composite initialization/validity output is written
        // by 0x4B66C and subsequently consumed by the Tx packer plus two local
        // readers. The public DBC STEER_ANGLE_INITIALIZING label is therefore
        // corroboration, while the exact firmware predicate is canonical.
        assertExactRefs(0xfebe8096L,
                "0004b6fe:WRITE", "0004b7c6:READ", "0004bd04:READ",
                "00057292:READ", "00058186:WRITE");

        // Signal 2 / B0[3] is a debounced steering-control consistency state:
        // C100 is initialized asserted, updated by C9D7C, exported through
        // AD4B/E83A, then staged to E8098.
        assertCall(0xcb86eL, 0xc9d7cL);
        assertExactRefs(0xfebec100L,
                "000c98a8:READ", "000c9976:READ", "000c9bc6:WRITE",
                "000c9d8c:READ", "000c9df2:WRITE", "000cb844:READ");
        assertExactRefs(0xfebead4bL,
                "000bcdda:READ", "000be066:WRITE", "000cb848:WRITE");
        assertExactRefs(0xfebee83aL,
                "0004b9bc:READ", "000bcdde:WRITE", "000be54c:WRITE");
        assertExactRefs(0xfebe8098L,
                "0004b9c0:WRITE", "0004bd0a:READ", "0005818a:WRITE");
        assertU16(0x1bd1cL, 524);
        assertU16(0x1bd22L, 40);

        // Signals 3/4 / B0[2:1] are neighboring operational-mode/RTE inhibit
        // predicates synthesized directly by 0x4B66C. Their exact OEM names
        // remain unknown.
        assertExactRefs(0xfebe8099L,
                "0004b6b4:WRITE", "0004bd10:READ", "0005818c:WRITE");
        assertExactRefs(0xfebe809aL,
                "0004b6d6:WRITE", "0004bd16:READ", "0005818e:WRITE");

        // Signal 5 / B0[0]: thresholded motor-feedback magnitude status. The
        // status chain is B724 -> E848 -> E809B; B724 is debounced from B725,
        // and the B725 producer consumes abs(FEBEAFE0), which originates from
        // the motor feedback estimate FEBE6DA8.
        assertExactRefs(0xfebeb724L,
                "000bca30:READ", "000bca6c:WRITE", "000bce5e:READ",
                "000bd0c4:WRITE");
        assertExactRefs(0xfebee848L,
                "0004b900:READ", "000bce62:WRITE", "000be520:WRITE");
        assertExactRefs(0xfebe809bL,
                "0004b904:WRITE", "0004bd1c:READ", "00058190:WRITE");
        assertCall(0xbca74L, 0xbc9dcL);
        assertCall(0xbc9dcL, 0xcbabaL);
        assertCall(0x37f86L, 0x37e60L);
        assertExactRefs(0xfebe6da8L,
                "00056f40:READ", "0005ad40:WRITE", "0005ad86:READ",
                "0005c514:READ", "00037f96:WRITE");
        assertU16(0xaeef2L, 5120);
        assertU16(0xaeef4L, 2560);
        assertU16(0xaeef6L, 0);

        // Signal 6 / B1..B2: the public STEER_TORQUE_DRIVER field is backed by
        // an independently recovered multi-channel sensor-selection path before
        // 0x4B66C applies *100/256 and clamps to +/-700.
        assertExactRefs(0xfebe6680L,
                "0004b70a:READ", "00051c76:READ", "000531fe:READ",
                "000554a2:READ", "00059684:WRITE", "0005c5f2:WRITE",
                "000354f2:READ");
        assertExactRefs(0xfebe810aL,
                "0004b732:WRITE", "0004b7f6:READ", "0004bd22:READ",
                "00057282:READ", "00058192:WRITE", "000fcc82:READ");

        // Signal 7 / B3..B4: C0FC is a saturated signed steering-control
        // difference/estimate exported via AE5C/E8BC into E810E. Public DBC
        // STEER_ANGLE is retained as corroboration, not as sole proof.
        assertExactRefs(0xfebec0fcL,
                "000c9bbe:WRITE", "000c9d00:WRITE", "000cb84a:READ");
        assertExactRefs(0xfebeae5cL,
                "000bcdd4:READ", "000be2a6:WRITE", "000cb858:WRITE");
        assertExactRefs(0xfebee8bcL,
                "0004b9c2:READ", "000bcdd8:WRITE", "000be54e:WRITE");
        assertExactRefs(0xfebe810eL,
                "0004b9c6:WRITE", "0004bd28:READ", "00058196:WRITE");

        // Signal 8 / B5..B6: public STEER_TORQUE_EPS is independently backed
        // by the high-rate motor-feedback domain. 6DA8 is copied through RTE
        // staging to 66F0; 0x4B66C applies a signed -100/128 scale.
        assertExactRefs(0xfebe66f0L,
                "0004b73c:READ", "0005ad92:WRITE", "0005c518:WRITE");
        assertExactRefs(0xfebe8110L,
                "0004b74e:WRITE", "0004b81c:READ", "0004bd2e:READ",
                "00058198:WRITE");

        println("ASSERT application-tx-semantics: call_edges=" + callEdges
                + " reference_censuses=" + referenceCensuses
                + " instruction_checks=" + instructionChecks
                + " failures=" + failures);
        if (failures != 0) {
            throw new IllegalStateException("AssertApplicationTransmitSemantics failures=" + failures);
        }
    }
}
