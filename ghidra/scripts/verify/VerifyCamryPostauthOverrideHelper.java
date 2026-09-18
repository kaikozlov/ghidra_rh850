//@author kaikozlov
//@category Verification
// Execute the exact-F33 post-auth route44 helper in emulator-local memory.
// Stock aggregate calls are stubbed at their exact entry points; only helper
// control/mutation semantics are executed. Args: <helper.bin> <result.json>
import ghidra.app.script.GhidraScript;
import ghidra.app.emulator.EmulatorHelper;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;

public class VerifyCamryPostauthOverrideHelper extends GhidraScript {
    private static final long BASE = 0xfebf0000L;
    private static final long GP = 0xfebeb800L;
    private static final long DCM_TAG = 0xfebe5752L;
    private static final long DCM_SEQ = 0xfebe5753L;
    private static final long DCM_TARGET = 0xfebe5754L;
    private static final long ROUTE_GEN = 0xfebe5364L;
    private static final long RAW = 0xfebe4bffL;
    private static final long PUB_COUNT = 0xfebf0268L;
    private static final long OVERRIDE_COUNT = 0xfebf026cL;
    private static final long LAST_SEQ = 0xfebf0278L;
    private static final long PUB_OBSERVED = 0xfebf0279L;
    private static final long LEASE = 0xfebf02d4L;
    private static final long CACHED_TARGET = 0xfebf02d6L;
    private static final long SECOC_AGG = 0x000988c2L;
    private static final long COMM_AFTER = 0x00069e7cL;
    private static final long APP_AGG = 0x00058b5eL;
    private static final long AGG_FINAL = 0x00066512L;
    private final List<String> passed = new ArrayList<>();

    private void put8(EmulatorHelper e, long a, int v) { e.writeMemory(toAddr(a), new byte[]{(byte)v}); }
    private void put16be(EmulatorHelper e, long a, int v) {
        e.writeMemory(toAddr(a), new byte[]{(byte)(v >>> 8), (byte)v});
    }
    private void put32le(EmulatorHelper e, long a, long v) {
        e.writeMemory(toAddr(a), new byte[]{(byte)v,(byte)(v>>>8),(byte)(v>>>16),(byte)(v>>>24)});
    }
    private int get8(EmulatorHelper e, long a) throws Exception { return e.readMemoryByte(toAddr(a)) & 0xff; }
    private long get32le(EmulatorHelper e, long a) throws Exception {
        byte[] b = e.readMemory(toAddr(a), 4);
        return (b[0]&255L) | ((b[1]&255L)<<8) | ((b[2]&255L)<<16) | ((b[3]&255L)<<24);
    }
    private void check(String name, boolean ok) throws Exception {
        if (!ok) throw new Exception("FAILED: " + name);
        passed.add(name);
    }
    private void nativeRaw(EmulatorHelper e) {
        byte[] b = new byte[32];
        b[3] = (byte)0xc4; b[4] = 0x11; b[5] = 0x22; b[6] = (byte)0xff;
        b[7] = 0x2a; b[8] = 0x22; b[9] = 0x33;
        b[28] = (byte)0xde; b[29] = (byte)0xad; b[30] = (byte)0xbe; b[31] = (byte)0xef;
        e.writeMemory(toAddr(RAW), b);
    }
    private void runTick(EmulatorHelper e, int tag, int seq, int target, int generation) throws Exception {
        put8(e, DCM_TAG, tag); put8(e, DCM_SEQ, seq); put16be(e, DCM_TARGET, target); put8(e, ROUTE_GEN, generation);
        e.writeRegister("PC", BASE); e.writeRegister("gp", GP); e.writeRegister("sp", 0xfebe1800L); e.writeRegister("lp", 0x10000L);
        long[] expected = {SECOC_AGG, COMM_AFTER, APP_AGG, AGG_FINAL};
        int call = 0;
        for (int i = 0; i < 500; i++) {
            long pc = e.readRegister("PC").longValue() & 0xffffffffL;
            if (call < expected.length && pc == expected[call]) {
                if (pc == AGG_FINAL) { call++; break; }
                long ret = e.readRegister("lp").longValue() & 0xffffffffL;
                e.writeRegister("PC", ret); call++; continue;
            }
            if (!e.step(monitor)) throw new Exception(e.getLastError());
        }
        if (call != expected.length) throw new Exception("stock-call order incomplete: " + call);
    }
    private boolean rawIsNative(EmulatorHelper e) throws Exception {
        return get8(e, RAW+3)==0xc4 && get8(e,RAW+4)==0x11 && get8(e,RAW+5)==0x22 &&
               get8(e,RAW+6)==0xff && get8(e,RAW+7)==0x2a && get8(e,RAW+8)==0x22 && get8(e,RAW+9)==0x33;
    }
    private void checkOverride(String name, EmulatorHelper e, int hi, int lo) throws Exception {
        check(name, get8(e,RAW+3)==0xcb && get8(e,RAW+4)==hi && get8(e,RAW+5)==lo &&
              get8(e,RAW+6)==0xfb && get8(e,RAW+7)==0x2a && get8(e,RAW+8)==100 && get8(e,RAW+9)==100 &&
              get8(e,RAW+28)==0xde && get8(e,RAW+29)==0xad && get8(e,RAW+30)==0xbe && get8(e,RAW+31)==0xef);
    }

    @Override public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length != 2) throw new IllegalArgumentException("helper, result required");
        byte[] blob = Files.readAllBytes(Path.of(args[0]));
        if (blob.length > 600) throw new Exception("helper exceeds fixed F33 C6 image");
        EmulatorHelper e = new EmulatorHelper(currentProgram);
        try {
            e.writeMemory(toAddr(BASE), blob);
            e.writeMemory(toAddr(PUB_COUNT), new byte[0x80]);

            nativeRaw(e); runTick(e, 0xc6, 0xff, 0x7777, 1);
            check("C6 loader tag cannot create runtime ownership", rawIsNative(e) && get8(e,LAST_SEQ)==0 && get8(e,LEASE)==0);
            check("released helper observes native authenticated route44 publication", get32le(e,PUB_COUNT)==1 && get8(e,PUB_OBSERVED)==1 && get32le(e,OVERRIDE_COUNT)==0);

            nativeRaw(e); runTick(e, 0xc7, 1, 0x1234, 2);
            checkOverride("fresh C7 overrides only post-auth application fields", e, 0x12, 0x34);
            check("fresh C7 caches target and starts lease", get8(e,LAST_SEQ)==1 && get8(e,LEASE)==7 && get8(e,CACHED_TARGET)==0x12 && get8(e,CACHED_TARGET+1)==0x34);
            check("override counter advances only with new native publication", get32le(e,OVERRIDE_COUNT)==1);

            nativeRaw(e); runTick(e, 0xc6, 0xff, 0x7777, 3);
            checkOverride("unrelated DCM traffic cannot leak native target during live lease", e, 0x12, 0x34);
            check("unrelated DCM traffic ages but does not replace cached generation", get8(e,LAST_SEQ)==1 && get8(e,LEASE)==6 && get32le(e,OVERRIDE_COUNT)==2);

            // Same route generation: helper may rewrite stale raw COM, but must not count it as a committed new-B6 override.
            nativeRaw(e); runTick(e, 0xc7, 1, 0x9999, 3);
            checkOverride("same C7 generation cannot change cached target", e, 0x12, 0x34);
            check("stale raw-COM rewrite does not satisfy publication counter", get32le(e,OVERRIDE_COUNT)==2);

            nativeRaw(e); runTick(e, 0xc7, 0, 0, 4);
            check("sequence zero immediately releases to native application fields", rawIsNative(e) && get8(e,LAST_SEQ)==0 && get8(e,LEASE)==0);

            nativeRaw(e); runTick(e, 0xc7, 2, 0xabcd, 5);
            checkOverride("fresh generation rearms after release", e, 0xab, 0xcd);
            // Six held ticks remain active; seventh held tick expires before application mutation.
            for (int i=0;i<6;i++) { nativeRaw(e); runTick(e, 0xc7, 2, 0x0000, 6+i); checkOverride("held lease active tick "+(i+1), e, 0xab, 0xcd); }
            nativeRaw(e); runTick(e, 0xc7, 2, 0x0000, 12);
            check("seventh held tick expires to stock target", rawIsNative(e) && get8(e,LEASE)==0);
        } finally { e.dispose(); }

        StringBuilder out = new StringBuilder("{\n  \"schema\": \"camry-f33-postauth-override-emulation-v1\",\n  \"tests\": [\n");
        for (int i=0;i<passed.size();i++) out.append("    \"").append(passed.get(i)).append("\"").append(i+1==passed.size()?"\n":",\n");
        String hash = java.util.HexFormat.of().formatHex(java.security.MessageDigest.getInstance("SHA-256").digest(blob));
        out.append("  ],\n  \"passed\": ").append(passed.size()).append(",\n  \"helper_sha256\": \"").append(hash)
           .append("\",\n  \"vehicle_executed\": false\n}\n");
        Files.writeString(Path.of(args[1]), out);
        println("PASS: " + passed.size() + " Camry post-auth helper assertions");
    }
}
