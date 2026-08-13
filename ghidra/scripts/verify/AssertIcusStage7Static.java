//@author kaikozlov
//@category Verification
// Stage-7 exact reference census for ICU result buffers and dormant activator.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;

import java.util.HashSet;
import java.util.Locale;
import java.util.Set;

public class AssertIcusStage7Static extends GhidraScript {
    private int failures = 0;
    private int censuses = 0;

    private void fail(String message) {
        failures++;
        printerr("ASSERT-FAIL icus-stage7: " + message);
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
        censuses++;
    }

    @Override
    public void run() throws Exception {
        // WDBI DID 0x100F action wrapper 0x8A782 directly reaches the bank-1
        // activator. The only interior reference is the activator's own
        // conditional branch to 0x6903e.
        assertExactRefs(0x69018L, "0008a786:UNCONDITIONAL_CALL");
        for (long address = 0x6901aL; address < 0x69042L; address += 2) {
            if (address == 0x6903eL) {
                assertExactRefs(address, "00069022:CONDITIONAL_JUMP");
            } else {
                assertExactRefs(address);
            }
        }

        // Exact activation-state reference set. Only 0x69026 writes value 1;
        // 0x68006 clears it and 0x68d32 writes a terminal state.
        assertExactRefs(0xfebe508fL,
                "00068006:WRITE", "00068c72:READ", "00068d12:READ",
                "00068d32:WRITE", "00068e02:READ", "0006901c:READ",
                "00069026:WRITE");

        // Command-specific staging has no unrelated outward reader. Lower FIFO
        // callbacks write indirectly; these direct refs are setup/copy only.
        assertExactRefs(0xfebf11c4L, "0008770a:DATA", "0008775c:PARAM");
        assertExactRefs(0xfebf1274L, "00087b3e:DATA", "00087b90:PARAM");
        assertExactRefs(0xfebf12b4L, "00087f5c:DATA", "00087fa4:READ");
        assertExactRefs(0xfebf113cL,
                "00086ebc:DATA", "00086f2e:PARAM", "00086f68:PARAM");
        assertExactRefs(0xfebf115cL, "00086f3a:PARAM");
        assertExactRefs(0xfebe555cL, "0008e41a:PARAM", "0008e69e:READ");

        println("ASSERT icus-stage7: reference_censuses=" + censuses + " failures=" + failures);
        if (failures != 0) throw new IllegalStateException("AssertIcusStage7Static failures=" + failures);
    }
}
