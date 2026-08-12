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

        // CAN 0x262 / EPS_STATUS uses five producer helpers in the same staging
        // orchestrator.  The live reference census below makes the RAM-field
        // partition independent of the generated CSV.
        assertCall(0x4ba8cL, 0x4b90aL);
        assertCall(0x4ba8cL, 0x4b920L);
        assertCall(0x4ba8cL, 0x4b93cL);
        assertCall(0x4ba8cL, 0x4b754L);

        // B0: all RAM-backed fields are explicitly zeroed by 0x4B90A. Signal
        // 13 and reserved B0[3] are separately constant-zero in the packer.
        assertExactRefs(0xfebe809cL,
                "0004b90e:WRITE", "0004be60:READ", "00057298:READ", "0005819a:WRITE");
        assertExactRefs(0xfebe80b4L,
                "0004b912:WRITE", "0004be48:READ", "00058174:WRITE");
        assertExactRefs(0xfebe809dL,
                "0004b910:WRITE", "0004be66:READ", "0005819c:WRITE");
        assertExactRefs(0xfebe809eL,
                "0004b914:WRITE", "0004be6c:READ", "0005819e:WRITE");
        assertExactRefs(0xfebe809fL,
                "0004b916:WRITE", "0004be72:READ", "000581a0:WRITE");
        assertExactRefs(0xfebe80a0L,
                "0004b918:WRITE", "0004be78:READ", "000581a2:WRITE");
        assertInstruction(0x4b90eL, "sst.b", "0x8", "ep", "r0");
        assertInstruction(0x4b918L, "sst.b", "0xc", "ep", "r0");

        // B1[7:3] is the public five-bit LTA_STATE field. The five staging bits
        // are independent RAM cells and originate in the steering-control state
        // machine; the low bit passes through helper 0x4B92C's marker gate.
        assertExactRefs(0xfebe80a4L,
                "0004b986:WRITE", "0004be88:READ", "000581aa:WRITE");
        assertExactRefs(0xfebe80a6L,
                "0004b98c:WRITE", "0004be94:READ", "000581ae:WRITE");
        assertExactRefs(0xfebe80a8L,
                "0004b992:WRITE", "0004bea0:READ", "000581b2:WRITE");
        assertExactRefs(0xfebe80aaL,
                "0004b998:WRITE", "0004beac:READ", "000581b6:WRITE");
        assertExactRefs(0xfebe80acL,
                "0004b9a6:WRITE", "0004beb8:READ", "00058180:WRITE");
        assertExactRefs(0xfebec130L,
                "000c98a4:READ", "000c9972:READ", "000c9e06:WRITE",
                "000c9ebe:WRITE", "000cb826:READ");

        // B3[7:1] is public LKA_STATE. The high two bits are explicitly zero;
        // bits 4..0 are state-machine exports, and B3[0] / TYPE is separately
        // zeroed by 0x4B754.
        assertExactRefs(0xfebe80a1L,
                "0004b91a:WRITE", "0004be42:READ", "000581a4:WRITE");
        assertExactRefs(0xfebe80a2L,
                "0004b91c:WRITE", "0004be30:READ", "000581a6:WRITE");
        assertExactRefs(0xfebe80a3L,
                "0004b952:WRITE", "0004be7e:READ", "000581a8:WRITE");
        assertExactRefs(0xfebe80a5L,
                "0004b958:WRITE", "0004be8e:READ", "000581ac:WRITE");
        assertExactRefs(0xfebe80a7L,
                "0004b95e:WRITE", "0004be9a:READ", "000581b0:WRITE");
        assertExactRefs(0xfebe80a9L,
                "0004b964:WRITE", "0004bea6:READ", "000581b4:WRITE");
        assertExactRefs(0xfebe80abL,
                "0004b950:WRITE", "0004beb2:READ", "000581b8:WRITE");
        assertExactRefs(0xfebe80adL,
                "0004b7a4:WRITE", "0004bebe:READ", "0005817e:WRITE");
        assertExactRefs(0xfebebfa9L,
                "000c82fc:WRITE", "000c8306:READ", "000c86a6:WRITE", "000cb798:READ");
        assertInstruction(0x4b91aL, "sst.b", "0xd", "ep", "r0");
        assertInstruction(0x4b91cL, "sst.b", "0xe", "ep", "r0");
        assertInstruction(0x4b7a4L, "sst.b", "0x19", "ep", "r0");

        // B4 is a proprietary steering-control status nibble assembled from two
        // limiter/threshold flags and the C0FE/C0FF transition state.
        assertExactRefs(0xfebe80aeL,
                "0004b9a8:WRITE", "0004bec4:READ", "0005817c:WRITE");
        assertExactRefs(0xfebe80afL,
                "0004b9ae:WRITE", "0004beca:READ", "0005817a:WRITE");
        assertExactRefs(0xfebe80b0L,
                "0004b9b4:WRITE", "0004bed0:READ", "00058178:WRITE");
        assertExactRefs(0xfebe80b1L,
                "0004b9ba:WRITE", "0004bed6:READ", "00058176:WRITE");
        assertExactRefs(0xfebec0d8L,
                "000c8c18:WRITE", "000c964e:READ", "000c9778:WRITE", "000cb82c:READ");
        assertExactRefs(0xfebec0d9L,
                "000c8c1c:WRITE", "000c977c:WRITE", "000cb832:READ");
        assertExactRefs(0xfebec0feL,
                "000c9bb2:WRITE", "000c9cb6:READ", "000c9d5c:WRITE", "000cb838:READ");
        assertExactRefs(0xfebec0ffL,
                "000c9bb6:WRITE", "000c9ccc:READ", "000c9d60:WRITE", "000cb83e:READ");

        // B5/B6 are not opaque dynamic bytes: 0x4B920 writes 0xFF every cycle.
        assertExactRefs(0xfebe80b2L,
                "0004b926:WRITE", "0004be50:READ", "000581bc:WRITE");
        assertExactRefs(0xfebe80b3L,
                "0004b928:WRITE", "0004be58:READ", "000581ba:WRITE");
        assertInstruction(0x4b920L, "mov", "-0x1", "r1");
        assertInstruction(0x4b926L, "sst.b", "0x1e", "ep", "r1");
        assertInstruction(0x4b928L, "sst.b", "0x1f", "ep", "r1");

        // Remaining normal Tx packets are owned by the same foreground staging
        // orchestrator.  0x351 goes through wrapper 0x4B8A4; 0x394 and 0x4A3
        // are direct producers.
        assertCall(0x4ba8cL, 0x4b8a4L);
        assertCall(0x4ba8cL, 0x4b8b6L);
        assertCall(0x4ba8cL, 0x4b7baL);
        assertCall(0x4b8a4L, 0x4b82cL);
        assertCall(0x4b8a4L, 0x4b882L);

        // CAN 0x351: plausibility_fault_debounce_monitor writes FEBEB5F8;
        // application_input_snapshot_update copies it to FEBEE82B; 0x4B82C
        // filters/holds that value before 0x4B882 exports a 3-bit code + gate.
        assertExactRefs(0xfebeb5f8L,
                "000b9d2c:WRITE", "000b9e8e:WRITE", "000bcd4a:READ",
                "000bdbb0:WRITE", "000b9cea:READ");
        assertExactRefs(0xfebe80b8L,
                "0004b82c:READ", "0004b89e:WRITE", "0004c268:READ", "0005816c:WRITE");
        assertExactRefs(0xfebe80b9L,
                "0004b8a0:WRITE", "0004c276:READ", "0005816a:WRITE");
        assertInstruction(0x4b892L, "mov", "0x7", "r6");
        assertInstruction(0x4b894L, "mov", "0x1", "r1");

        // CAN 0x394: FUN_50268 selects one of 17 five-byte table rows and
        // writes the selected tuple plus its 1..16 state. 0x4B8B6 converts the
        // state to a coarse class and maps tuple bytes into the six Tx fields.
        assertExactRefs(0xfebe8258L,
                "0004b8b6:READ", "00050430:WRITE", "00057c72:WRITE");
        assertExactRefs(0xfebe8262L,
                "0004b8ec:READ", "0005041a:WRITE", "00057c70:WRITE");
        assertExactRefs(0xfebe8263L,
                "0004b8f2:READ", "00050420:WRITE", "00057c84:WRITE");
        assertExactRefs(0xfebe8264L,
                "0004b8f8:READ", "00050426:WRITE", "00057c86:WRITE");
        assertExactRefs(0xfebe8265L,
                "0004b8e6:READ", "00050434:WRITE", "00057c88:WRITE");
        assertExactRefs(0xfebe8266L,
                "0004b8e0:READ", "00050414:WRITE", "00057c76:WRITE");
        assertExactRefs(0xfebe80baL,
                "0004b8e4:WRITE", "0004c164:READ", "00058168:WRITE");
        assertExactRefs(0xfebe80c2L,
                "0004b8de:WRITE", "0004c172:READ", "00058158:WRITE");
        assertExactRefs(0xfebe80bdL,
                "0004b8ea:WRITE", "0004c178:READ", "00058162:WRITE");
        assertExactRefs(0xfebe80beL,
                "0004b8f0:WRITE", "0004c17e:READ", "00058160:WRITE");
        assertExactRefs(0xfebe80bfL,
                "0004b8f6:WRITE", "0004c184:READ", "0005815e:WRITE");
        assertExactRefs(0xfebe80c1L,
                "0004b8fc:WRITE", "0004c18a:READ", "0005815a:WRITE");
        assertInstruction(0x5040aL, "mov", "0x2a33c", "r19");
        assertInstruction(0x50406L, "mulhi", "0x5", "r1", "ep");

        // CAN 0x4A3: mixed steering telemetry. B1/B2 mirror incoming CAN 0x025
        // signal 221; B3/B4 carry its clamped difference from incoming CAN
        // 0x64F signal 289; B5 derives from the 0x260 driver-torque staging;
        // B6/B7 mirror the 0x260 EPS-torque staging word.
        assertExactRefs(0xfebe80c3L,
                "0004b7de:WRITE", "0004bb2a:READ", "00058156:WRITE");
        assertExactRefs(0xfebe80c4L,
                "0004b7e8:WRITE", "0004bb38:READ", "00058154:WRITE");
        assertExactRefs(0xfebe80c5L,
                "0004b7d8:WRITE", "0004bb3e:READ", "00058152:WRITE");
        assertExactRefs(0xfebe80c6L,
                "0004b806:WRITE", "0004bb44:READ", "00058150:WRITE");
        assertExactRefs(0xfebe80c7L,
                "0004b800:WRITE", "0004bb4a:READ", "0005814e:WRITE");
        assertExactRefs(0xfebe80c8L,
                "0004b81e:WRITE", "0004bb50:READ", "0005814c:WRITE");
        assertExactRefs(0xfebe80c9L,
                "0004b824:WRITE", "0004bb56:READ", "0005814a:WRITE");
        assertExactRefs(0xfebe80caL,
                "0004b826:WRITE", "0004bb5c:READ", "00058148:WRITE");
        assertExactRefs(0xfebe801cL,
                "00047046:READ", "0004adac:DATA", "0004b7be:READ",
                "00057318:READ", "00057ec2:WRITE");
        assertExactRefs(0xfebe807cL,
                "0004704a:READ", "0004b4b4:DATA", "00057326:READ", "00057e02:WRITE");
        assertExactRefs(0xfebe7ce6L,
                "00047074:WRITE", "0004b7cc:READ", "00051d12:READ",
                "00052e10:READ", "00053056:READ", "0005329e:READ",
                "00055314:READ", "000554ae:READ", "000590f0:WRITE");
        assertCall(0x4703eL, 0x6956aL);
        assertCall(0x4b7baL, 0x6f080L);
        assertCall(0x4b7baL, 0x6953cL);
        assertInstruction(0x4706aL, "sub", "r1", "r6");
        assertInstruction(0x4b7daL, "ori", "0x20", "r1", "r1");

        println("ASSERT application-tx-semantics: call_edges=" + callEdges
                + " reference_censuses=" + referenceCensuses
                + " instruction_checks=" + instructionChecks
                + " failures=" + failures);
        if (failures != 0) {
            throw new IllegalStateException("AssertApplicationTransmitSemantics failures=" + failures);
        }
    }
}
