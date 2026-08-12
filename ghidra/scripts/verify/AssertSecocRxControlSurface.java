//@author kaikozlov
//@category Verification
// Lock the downstream roles of all six application SecOC receive profiles.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.Function;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;

import java.util.HashSet;
import java.util.Locale;
import java.util.Set;

public class AssertSecocRxControlSurface extends GhidraScript {
    private int failures = 0;
    private int censuses = 0;
    private int calls = 0;

    private void fail(String message) {
        failures++;
        printerr("ASSERT-FAIL secoc-rx-surface: " + message);
    }

    private String refKey(Reference ref) {
        return String.format(Locale.ROOT, "%08x:%s",
                ref.getFromAddress().getOffset(), ref.getReferenceType().toString());
    }

    private void exact(long destination, String... expected) {
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

    private void call(long caller, long callee) {
        Function source = getFunctionAt(toAddr(caller));
        if (source == null) {
            fail(String.format(Locale.ROOT, "missing caller 0x%x", caller));
            return;
        }
        for (Function target : source.getCalledFunctions(monitor)) {
            if (target.getEntryPoint().getOffset() == callee) {
                calls++;
                return;
            }
        }
        fail(String.format(Locale.ROOT, "missing call 0x%x -> 0x%x", caller, callee));
    }

    private void named(long address, String expected) {
        Function fn = getFunctionAt(toAddr(address));
        if (fn == null || !expected.equals(fn.getName())) {
            fail(String.format(Locale.ROOT, "function 0x%x expected=%s actual=%s",
                    address, expected, fn == null ? "<missing>" : fn.getName()));
        }
    }

    @Override
    public void run() throws Exception {
        named(0x4b23cL, "application_unpack_can_090_secoc_fd");
        named(0x4b3aaL, "application_unpack_can_0d7_secoc_fd");
        named(0xbbf0eL, "fd090_rear_wheel_speed_plausibility");
        named(0xbc766L, "fd090_steering_angle_speed_plausibility");
        named(0xbc484L, "fd0d7_sp1_vehicle_speed_normalize");
        named(0xb6396L, "fd0d7_status_fault_monitor");

        // 0x090: three postprocessed measurement channels are staged into the
        // steering subsystem. The first pair terminates at B6AA, the third at B714.
        exact(0xfebef1c6L, "000573f6:WRITE", "0005b298:WRITE", "000bbf36:READ");
        exact(0xfebef1c8L, "00057408:WRITE", "0005b294:WRITE", "000bbf3a:READ");
        exact(0xfebef1caL, "00057464:WRITE", "0005b290:WRITE", "000bc774:READ");
        exact(0xfebeb6aaL, "000baaee:READ", "000bc034:WRITE", "000bd412:WRITE");
        exact(0xfebeb714L, "000bab08:READ", "000bc7f6:WRITE", "000bd42e:WRITE");

        // BA43A promotes those values into steering-cycle state. AE02 has six
        // controller readers; AF00 is validity-gated by BFBA8.
        exact(0xfebeae02L,
                "000ba9ee:WRITE", "000bdee6:WRITE", "000c8f0c:READ", "000c8f36:READ",
                "000c910e:READ", "000c94e4:READ", "000c956e:READ", "000c9642:READ");
        exact(0xfebeaf00L, "000bab0c:WRITE", "000be040:WRITE", "000bfbb2:READ");

        // 0x090 protected status bits become steering validity prerequisites.
        exact(0xfebead71L, "000baab8:WRITE", "000be0ce:WRITE", "000bf7a8:READ");
        exact(0xfebead72L, "000baac0:WRITE", "000be0d0:WRITE", "000bf7b0:READ");
        exact(0xfebeace3L, "000bab14:WRITE", "000bdf70:WRITE", "000bf988:READ");
        exact(0xfebeace4L, "000bab1a:WRITE", "000bdf72:WRITE", "000bf98a:READ");
        exact(0xfebeb75fL, "000bf726:WRITE", "000bf7ba:WRITE", "000bf9de:READ");
        exact(0xfebeb7c4L,
                "000bf808:WRITE", "000bf9ba:WRITE", "000bfba8:READ",
                "000bff74:READ", "000c0980:READ");

        // 0x0D7 signal 283 is staged then normalized into the shared live
        // vehicle-speed state B6F2. The broad B6F2 consumer census is locked by
        // its dedicated application semantics tests; here pin its unique producer.
        exact(0xfebef1b6L, "000573b8:WRITE", "0005b2b8:WRITE", "000bc488:READ");

        // Signal 280 is generated through a stack temporary: 4B3AA preserves the
        // previous byte, receive_signal writes SP+0x0B, and 4B45C persists it to
        // FEBE8076. It then stages to F094 and reaches the fault monitor.
        exact(0xfebe8076L,
                "0004b3ae:READ", "0004b45c:WRITE", "000573cc:READ", "00058032:WRITE",
                "000fcc8e:READ", "0004a0dc:READ", "0003550a:READ",
                "0004ef70:READ", "0004efb4:READ");
        exact(0xfebef094L,
                "000573d0:WRITE", "0005b442:WRITE", "000b63a6:READ", "000ba9f2:READ");

        // The remaining staged 0x0D7 halfwords/status bytes terminate after
        // BA43A publication. Each post-snapshot scalar has only its snapshot
        // write and subsystem initialization write, with zero runtime readers.
        exact(0xfebeaed6L, "000bad94:WRITE", "000be230:WRITE");
        exact(0xfebeaed8L, "000bad9c:WRITE", "000be32a:WRITE");
        exact(0xfebeade1L, "000ba9fc:WRITE", "000be232:WRITE");
        exact(0xfebeade2L, "000baa04:WRITE", "000be234:WRITE");

        // Scheduling edges for the two FD postprocessors.
        call(0xbc520L, 0xbc484L);

        println("ASSERT secoc-rx-surface: censuses=" + censuses + " calls=" + calls
                + " failures=" + failures);
        if (failures != 0) throw new IllegalStateException("AssertSecocRxControlSurface failures=" + failures);
    }
}
