//@author kaikozlov
//@category Verification
// Live-project assertions for cross-interface application state joins.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.Function;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;

import java.util.HashSet;
import java.util.Locale;
import java.util.Set;

public class AssertApplicationInterfaceStateJoins extends GhidraScript {
    private int failures = 0;
    private int refSets = 0;
    private int callEdges = 0;

    private void fail(String message) {
        failures++;
        printerr("ASSERT-FAIL application-interface-joins: " + message);
    }

    private String key(Reference ref) {
        return String.format(Locale.ROOT, "%08x:%s",
                ref.getFromAddress().getOffset(), ref.getReferenceType().toString());
    }

    private void exactRefs(long destination, String... expected) {
        Set<String> actual = new HashSet<>();
        ReferenceIterator refs = currentProgram.getReferenceManager().getReferencesTo(toAddr(destination));
        while (refs.hasNext()) actual.add(key(refs.next()));
        Set<String> wanted = Set.of(expected);
        if (!actual.equals(wanted)) {
            fail(String.format(Locale.ROOT, "refs 0x%x expected=%s actual=%s",
                    destination, wanted, actual));
        }
        refSets++;
    }

    private void call(long caller, long callee) {
        Function source = getFunctionAt(toAddr(caller));
        if (source == null) {
            fail(String.format(Locale.ROOT, "missing caller 0x%x", caller));
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

    @Override
    public void run() throws Exception {
        // APP-JOIN-003: authenticated 0x2E4 signal 61 ingress to the command
        // mirror, per-tick scaled command, and visible LKA_STATE bit4 status.
        exactRefs(0xfebe7f94L,
                "0004a26e:DATA", "00057138:READ", "00057f8a:WRITE");
        exactRefs(0xfebef184L,
                "00057148:WRITE", "0005b514:WRITE", "000ba4b8:READ");
        exactRefs(0xfebeae20L,
                "000ba808:WRITE", "000be24a:WRITE", "000c8076:READ", "000c8546:READ");
        exactRefs(0xfebebf74L,
                "000c8040:WRITE", "000c81d6:WRITE", "000c81e2:READ", "000c8280:READ");
        exactRefs(0xfebebf7bL,
                "000c804c:WRITE", "000c8292:WRITE", "000c83ba:READ",
                "000c83fc:READ", "000cb77c:READ");
        exactRefs(0xfebeacf6L,
                "000bce40:READ", "000bdf96:WRITE", "000cb788:WRITE");
        exactRefs(0xfebee844L,
                "0004b948:READ", "000bce44:WRITE", "000be52a:WRITE");
        exactRefs(0xfebe80a3L,
                "0004b952:WRITE", "0004be7e:READ", "000581a8:WRITE");

        call(0xba43aL, 0xcbb74L);
        call(0xcb86eL, 0xc853aL);
        call(0xcb86eL, 0xc8072L);
        call(0xcb86eL, 0xc8280L);

        // MAC match/mismatch result is not itself a Tx status source. Its exact
        // reference set remains local to SecOC submission/acceptance: one PARAM
        // output-pointer use plus Gate-2 READ. Accepted command state can later
        // affect Tx status through the command chain above; this assertion does
        // not claim absence of timeout-mediated consequences after rejection.
        exactRefs(0xfebe555cL,
                "0008e41a:PARAM", "0008e69e:READ");

        println("ASSERT application-interface-joins: ref_sets=" + refSets
                + " call_edges=" + callEdges
                + " failures=" + failures);
        if (failures != 0) {
            throw new IllegalStateException("AssertApplicationInterfaceStateJoins failures=" + failures);
        }
    }
}
