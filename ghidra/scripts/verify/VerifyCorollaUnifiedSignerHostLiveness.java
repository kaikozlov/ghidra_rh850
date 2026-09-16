//@author kaikozlov
//@category Verification
// Execute the exact Corolla unified helper's host-liveness gates in emulator-local memory.
// Args: <helper.bin> <result.json>
import ghidra.app.script.GhidraScript;
import ghidra.app.emulator.EmulatorHelper;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;

public class VerifyCorollaUnifiedSignerHostLiveness extends GhidraScript {
    private static final long BASE = 0xfebf0000L;
    private static final long GP = 0xfebeb800L;
    private static final long STATE = 0xfebff9f0L;
    private static final long RETURN = 0x00010000L;
    private static final long MEM_COPY = 0x0008323eL;
    private static final long DCM_TAG = 0xfebe563eL;
    private static final long DCM_SEQ = 0xfebe563fL;
    private static final long DCM_TARGET = 0xfebe5640L;
    private static final long B6_QUEUE_LEN = 0xfebe5366L;
    private static final long B6_TRAILER = 0xfebe53dcL;
    private final List<String> passed = new ArrayList<>();
    private int nativeGeneration = 1;

    private void put(EmulatorHelper e, long a, int v, int n) {
        byte[] data = new byte[n];
        for (int i = 0; i < n; i++) data[i] = (byte)(v >>> (8 * i));
        e.writeMemory(toAddr(a), data);
    }
    private int get(EmulatorHelper e, long a) throws Exception {
        return e.readMemoryByte(toAddr(a)) & 255;
    }
    private void check(String name, boolean ok) throws Exception {
        if (!ok) throw new Exception("FAILED: " + name);
        passed.add(name);
    }
    private boolean tick(EmulatorHelper e, int seq, boolean nativeFrame) throws Exception {
        e.writeRegister("PC", BASE);
        e.writeRegister("gp", GP);
        e.writeRegister("sp", 0xfebe1800L);
        e.writeRegister("lp", RETURN);
        put(e, DCM_TAG, 0xc7, 1);
        put(e, DCM_SEQ, seq, 1);
        put(e, DCM_TARGET, 0x3412, 2);
        put(e, B6_QUEUE_LEN, nativeFrame ? 32 : 0, 2);
        put(e, B6_TRAILER, nativeGeneration++, 4);
        put(e, STATE + 8, 1, 1);  // native-MAC oracle already qualified
        for (int i = 0; i < 240; i++) {
            long pc = e.readRegister("PC").longValue() & 0xffffffffL;
            if (pc == RETURN) return false;
            if (pc == MEM_COPY) return true;  // host/lease/native gates admitted replacement
            if (e.readMemoryByte(toAddr(pc)) == 0 && e.readMemoryByte(toAddr(pc + 1)) == 0) {
                e.writeRegister("PC", pc + 2);
            } else if (!e.step(monitor)) {
                throw new Exception(e.getLastError());
            }
        }
        throw new Exception("helper failed to return or reach native-domain copy");
    }

    @Override public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length != 2) throw new IllegalArgumentException("helper, result required");
        byte[] blob = Files.readAllBytes(Path.of(args[0]));
        if (blob.length > 464) throw new Exception("helper exceeds exact Corolla low-RAM pocket");
        var originalBlock = currentProgram.getMemory().getBlock(toAddr(BASE));
        boolean originalInitialized = originalBlock != null && originalBlock.isInitialized();
        EmulatorHelper e = new EmulatorHelper(currentProgram);
        try {
            e.writeMemory(toAddr(BASE), blob);
            e.writeMemory(toAddr(STATE), new byte[24]);
            check("inactive startup", !tick(e, 0, true));
            check("new active generation", tick(e, 1, true));
            for (int i = 1; i <= 6; i++) check("held command before expiry tick " + i, tick(e, 1, true));
            check("host loss expires at seventh tick", !tick(e, 1, true));
            for (int i = 0; i < 520; i++) {
                if (tick(e, 1, false)) throw new Exception("stale command unexpectedly admitted with empty queue");
            }
            check("stale generation never rearms", !tick(e, 1, true));
            check("fresh sequence rearms after expiry", tick(e, 2, true));
            check("zero immediately releases", !tick(e, 0, true));
            for (int i = 0; i < 10; i++) check("zero stays inactive " + i, !tick(e, 0, true));
            check("active generation after zero", tick(e, 255, true));
            check("sequence 255 to 1 wraps normally", tick(e, 1, true));

            // A fresh generation observed while B6 is absent still starts the
            // same wall-clock lease. Seven 5-ms foreground ticks later, a
            // returning native B6 cannot resurrect the stale request.
            check("fresh command with empty queue does not actuate", !tick(e, 3, false));
            for (int i = 1; i <= 6; i++) check("empty queue ages host command " + i, !tick(e, 3, false));
            check("returning native B6 after empty-queue expiry stays native", !tick(e, 3, true));

            // openpilot's 50-Hz C7 stream changes generation every four
            // nominal 5-ms foreground ticks, comfortably inside the 7-tick lease.
            for (int i = 0; i < 100; i++) {
                int seq = 10 + i / 4;
                if (!tick(e, seq, true)) throw new Exception("normal 50 Hz host / 200 Hz scheduler dropout " + i);
            }
            check("normal 50 Hz host remains continuously admitted", true);
            check("lease saturates at zero after host loss", get(e, STATE + 5) > 0); // active after final fresh stream
            for (int i = 0; i < 7; i++) tick(e, 34, false);
            check("lease reaches zero without wrap", get(e, STATE + 5) == 0);
            var afterBlock = currentProgram.getMemory().getBlock(toAddr(BASE));
            check("program memory mapping unchanged", originalBlock == afterBlock &&
                    originalInitialized == (afterBlock != null && afterBlock.isInitialized()));
        } finally { e.dispose(); }

        StringBuilder out = new StringBuilder("{\n  \"schema\": \"corolla-unified-signer-host-liveness-emulation-v1\",\n  \"tests\": [\n");
        for (int i = 0; i < passed.size(); i++) out.append("    \"").append(passed.get(i)).append("\"").append(i + 1 == passed.size() ? "\n" : ",\n");
        String hash = java.util.HexFormat.of().formatHex(java.security.MessageDigest.getInstance("SHA-256").digest(blob));
        out.append("  ],\n  \"passed\": ").append(passed.size()).append(",\n  \"helper_sha256\": \"").append(hash)
           .append("\",\n  \"vehicle_executed\": false\n}\n");
        Files.writeString(Path.of(args[1]), out);
        println("PASS: " + passed.size() + " Corolla unified helper liveness assertions");
    }
}
