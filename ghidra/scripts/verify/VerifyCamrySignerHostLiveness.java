//@author kaikozlov
//@category Verification
// Execute compiled helper in emulator-local memory. Never modifies the program DB.
// Args: <helper.bin> <result.json>
import ghidra.app.script.GhidraScript;
import ghidra.app.emulator.EmulatorHelper;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;

public class VerifyCamrySignerHostLiveness extends GhidraScript {
    private static final long BASE = 0xfebf0000L;
    private static final long GP = 0xfebeb800L;
    private static final long RETURN = 0x00010000L;
    private static final long COPY = 0x00089f2eL;
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
        put(e, 0xfebe4c34L, 0xc700, 2);
        put(e, 0xfebe4c36L, seq, 1);
        put(e, 0xfebe547aL, nativeFrame ? 32 : 0, 2);
        put(e, 0xfebe54f0L, nativeGeneration++, 4);
        put(e, 0xfebf0279L, 1, 1);  // no-mutation native oracle previously passed
        for (int i = 0; i < 200; i++) {
            long pc = e.readRegister("PC").longValue() & 0xffffffffL;
            if (pc == RETURN) return false;
            if (pc == COPY) {
                // Stop before stock copy/crypto: reaching the first copy proves
                // the actual helper's host/queue gates admitted this generation.
                if (get(e, 0xfebf02d0L) != 2) throw new Exception("unexpected oracle path");
                return true;
            }
            // The RH850 SLEIGH names NOP as an unimplemented __nop userop.
            // Its architectural effect is only advancing the 16-bit PC.
            if (e.readMemoryByte(toAddr(pc)) == 0 && e.readMemoryByte(toAddr(pc + 1)) == 0) {
                e.writeRegister("PC", pc + 2);
            } else if (!e.step(monitor)) throw new Exception(e.getLastError());
        }
        throw new Exception("helper failed to return or reach domain copy");
    }
    private String differentialCase(byte[] code, int messageLow, int committedMessage, int target,
                                    int failure, boolean epochMismatch) throws Exception {
        EmulatorHelper e = new EmulatorHelper(currentProgram);
        try {
            e.writeMemory(toAddr(BASE), code);
            e.writeMemory(toAddr(0xfebf025cL), new byte[0xac]);
            e.writeRegister("PC", BASE);
            e.writeRegister("gp", GP);
            e.writeRegister("sp", 0xfebe1800L);
            e.writeRegister("lp", RETURN);
            put(e, 0xfebe4c34L, 0xc700, 2);
            put(e, 0xfebe4c36L, 1, 1);
            put(e, 0xfebe4c38L, ((target & 255) << 8) | ((target >>> 8) & 255), 2);
            put(e, 0xfebe547aL, 32, 2);
            byte[] queue = new byte[32];
            for (int i = 0; i < queue.length; i++) queue[i] = (byte)(i * 7 + 3);
            queue[28] = (byte)(messageLow << 6);
            e.writeMemory(toAddr(0xfebe54d4L), queue);
            put(e, 0xfebf0279L, 1, 1);
            put(e, 0xfebe55c0L, 123, 4);
            put(e, 0xfebe55c4L, 100, 4);
            put(e, 0xfebe55e8L, epochMismatch ? 124 : 123, 4);
            put(e, 0xfebe55ecL, 100, 4);
            put(e, 0xfebe55f0L, committedMessage, 2);
            List<String> calls = new ArrayList<>();
            for (int i = 0; i < 800; i++) {
                long pc = e.readRegister("PC").longValue() & 0xffffffffL;
                if (pc == RETURN) {
                    byte[] after = e.readMemory(toAddr(0xfebe54d4L), 32);
                    if ((failure != 0 || epochMismatch) && !java.util.Arrays.equals(queue, after))
                        throw new Exception("failure mutated native queue");
                    return String.join(";", calls) + "|queue=" + java.util.HexFormat.of().formatHex(after)
                        + "|telemetry=" + java.util.HexFormat.of().formatHex(e.readMemory(toAddr(0xfebf027cL), 12));
                }
                long r6 = e.readRegister("r6").longValue() & 0xffffffffL;
                long r7 = e.readRegister("r7").longValue() & 0xffffffffL;
                long r8 = e.readRegister("r8").longValue() & 0xffffffffL;
                if (pc == COPY) {
                    calls.add("copy:" + r6 + ":" + r7 + ":" + r8);
                    e.writeMemory(toAddr(r6), e.readMemory(toAddr(r7), (int)r8));
                } else if (pc == 0x90566L) {
                    // Golden differential boundary, not a replacement encoder:
                    // compare exact ABI and freshness witnesses, and supply the
                    // same deterministic six bytes to both compiled helpers.
                    byte[] witness = e.readMemory(toAddr(r6), 12);
                    calls.add("freshness:" + java.util.HexFormat.of().formatHex(witness));
                    e.writeMemory(toAddr(r7), java.util.Arrays.copyOf(witness, 6));
                } else if (pc == 0x89bc2L) {
                    byte[] domain = e.readMemory(toAddr(0xfebf0288L), 36);
                    if ((domain[0] & 255) != 0 || (domain[1] & 255) != 0xb6)
                        throw new Exception("invalid command-5 domain prefix");
                    calls.add("command5:" + r6 + ":" + r7 + ":" + r8 + ":"
                        + e.readRegister("r9") + ":" + java.util.HexFormat.of().formatHex(domain));
                    // Not a cryptographic oracle: deterministic result bytes
                    // test queue commit/error behavior against the archived code.
                    byte[] tag = java.security.MessageDigest.getInstance("SHA-256").digest(domain);
                    e.writeMemory(toAddr(r7), java.util.Arrays.copyOf(tag, 16));
                    e.writeRegister("r10", failure == 1 ? 1 : 0);
                    put(e, 0xfebf13bcL, failure == 2 ? 0 : 1, 1);
                    put(e, 0xfebf13bdL, failure == 3 ? 1 : 0, 1);
                } else {
                    if (e.readMemoryByte(toAddr(pc)) == 0 && e.readMemoryByte(toAddr(pc + 1)) == 0)
                        e.writeRegister("PC", pc + 2);
                    else if (!e.step(monitor)) throw new Exception(e.getLastError());
                    continue;
                }
                e.writeRegister("PC", e.readRegister("lp"));
            }
            throw new Exception("differential helper failed to finish");
        } finally { e.dispose(); }
    }

    @Override public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length < 2 || args.length > 3) throw new IllegalArgumentException("helper, result, optional golden helper required");
        byte[] blob = Files.readAllBytes(Path.of(args[0]));
        if (blob.length > 600) throw new Exception("helper exceeds existing loader");
        var originalBlock = currentProgram.getMemory().getBlock(toAddr(BASE));
        boolean originalInitialized = originalBlock != null && originalBlock.isInitialized();
        EmulatorHelper e = new EmulatorHelper(currentProgram);
        try {
            e.writeMemory(toAddr(BASE), blob);
            e.writeMemory(toAddr(0xfebf025cL), new byte[0xac]);
            check("inactive startup", !tick(e, 0, true));
            check("new active generation", tick(e, 1, true));
            for (int i = 1; i <= 6; i++) check("held command before expiry tick " + i, tick(e, 1, true));
            check("host loss expires at seventh tick", !tick(e, 1, true));
            for (int i = 0; i < 520; i++) {
                if (tick(e, 1, true)) throw new Exception("stale command revived after expiry");
            }
            check("no resurrection across two 8-bit clock wraps", get(e, 0xfebf02d4L) == 0);
            check("fresh sequence rearms after expiry", tick(e, 2, true));
            check("zero immediately releases", !tick(e, 0, true));
            for (int i = 0; i < 10; i++) check("zero stays inactive " + i, !tick(e, 0, true));
            check("active generation after zero", tick(e, 255, true));
            check("sequence 255 to 1 wraps normally", tick(e, 1, true));
            for (int i = 0; i < 7; i++) check("empty queue still ages host command " + i, !tick(e, 1, false));
            check("native traffic cannot revive expired generation", !tick(e, 1, true));
            for (int i = 0; i < 100; i++) {
                int seq = 2 + i / 4;
                if (!tick(e, seq, true)) throw new Exception("normal 50 Hz host / 200 Hz scheduler dropout " + i);
            }
            check("normal 50 Hz host remains active", true);
            var afterBlock = currentProgram.getMemory().getBlock(toAddr(BASE));
            check("program memory mapping unchanged", originalBlock == afterBlock &&
                    originalInitialized == (afterBlock != null && afterBlock.isInitialized()));
        } finally { e.dispose(); }
        if (args.length == 3) {
            byte[] golden = Files.readAllBytes(Path.of(args[2]));
            for (int received = 0; received < 4; received++) {
                for (int committed = 0; committed < 4; committed++) {
                    for (int target : new int[] {-1745, 0, 1745}) {
                        String oldResult = differentialCase(golden, received, 252 + committed, target, 0, false);
                        String newResult = differentialCase(blob, received, 252 + committed, target, 0, false);
                        check("domain/freshness/commit equivalence " + received + "/" + committed + "/" + target,
                              oldResult.equals(newResult));
                    }
                }
            }
            for (int failure = 1; failure <= 3; failure++) {
                check("command5 failure preserves native queue " + failure,
                      differentialCase(golden, 1, 4, 37, failure, false).equals(
                      differentialCase(blob, 1, 4, 37, failure, false)));
            }
            check("epoch mismatch preserves native queue",
                  differentialCase(golden, 1, 4, 37, 0, true).equals(
                  differentialCase(blob, 1, 4, 37, 0, true)));
        }
        StringBuilder out = new StringBuilder("{\n  \"schema\": \"camry-signer-host-liveness-emulation-v1\",\n  \"tests\": [\n");
        for (int i = 0; i < passed.size(); i++) out.append("    \"").append(passed.get(i)).append("\"").append(i + 1 == passed.size() ? "\n" : ",\n");
        String hash = java.util.HexFormat.of().formatHex(java.security.MessageDigest.getInstance("SHA-256").digest(blob));
        out.append("  ],\n  \"passed\": ").append(passed.size()).append(",\n  \"helper_sha256\": \"").append(hash)
           .append("\",\n  \"vehicle_executed\": false\n}\n");
        Files.writeString(Path.of(args[1]), out);
        println("PASS: " + passed.size() + " compiled-helper liveness assertions");
    }
}
