//@author kaikozlov
//@category Verification
// Stock-code, emulator-local verification. No vehicle access or database mutation.
// Args: <CodeFlash.bin> <result.json>.
import ghidra.app.script.GhidraScript;
import ghidra.app.emulator.EmulatorHelper;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;

public class VerifyCamryCooperativeFaultProjection extends GhidraScript {
    private static final long GP = 0xfebeb800L;
    private static final long RETURN = 0x10000L;
    private final List<String> passed = new ArrayList<>();
    private int commandWire = -1;
    private int angleWire = -1;

    private void put(EmulatorHelper e, long a, int v) { e.writeMemory(toAddr(a), new byte[]{(byte)v}); }
    private int get(EmulatorHelper e, long a) throws Exception { return e.readMemoryByte(toAddr(a)) & 255; }
    private long word(EmulatorHelper e, long a) throws Exception {
        long v = 0;
        for (int i = 0; i < 4; i++) v |= (long)get(e, a + i) << (8 * i);
        return v;
    }
    private void check(String name, boolean condition) throws Exception {
        if (!condition) throw new Exception("FAILED: " + name);
        passed.add(name);
    }
    private long reg(EmulatorHelper e, String name) { return e.readRegister(name).longValue() & 0xffffffffL; }
    private int call(EmulatorHelper e, long entry, int argument) throws Exception {
        e.writeRegister("PC", entry); e.writeRegister("gp", GP);
        e.writeRegister("sp", 0xfebe1800L); e.writeRegister("lp", RETURN);
        e.writeRegister("r6", argument);
        for (int count = 0; count < 4000; count++) {
            long pc = reg(e, "PC");
            if (pc == RETURN) return (int)reg(e, "r10");
            if (pc == 0x7d31eL) {
                // Observe the actual stock caller's generated-COM binding.
                // Scalar packer and CAN submission are outside this unit model.
                int id = (int)reg(e, "r6");
                if (id == 25 || id == 31) {
                    int value = get(e, word(e, reg(e, "sp")));
                    int expectedByte = id == 25 ? 16 : 19;
                    check("signal " + id + " stock wire binding", reg(e,"r7") == expectedByte && reg(e,"r8") == 1 && reg(e,"r9") == 0);
                    if (id == 25) commandWire = value; else angleWire = value;
                }
                e.writeRegister("PC", reg(e, "lp"));
            } else if (pc == 0x7d05cL) {
                e.writeMemory(toAddr(reg(e, "r7")), new byte[32]);
                e.writeRegister("PC", reg(e, "lp"));
            } else if (pc == 0x7d0eaL) {
                e.writeRegister("r10", 0); e.writeRegister("PC", reg(e, "lp"));
            } else if (get(e, pc) == 0 && get(e, pc + 1) == 0) {
                e.writeRegister("PC", pc + 2); // architectural NOP, no custom-pcode handler required
            } else if (!e.step(monitor)) {
                throw new Exception(e.getLastError() + " at " + Long.toHexString(pc));
            }
        }
        throw new Exception("stock function did not return: " + Long.toHexString(entry));
    }
    @Override public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length != 2) throw new IllegalArgumentException("image and result required");
        byte[] image = Files.readAllBytes(Path.of(args[0]));
        byte[] program = new byte[image.length]; currentProgram.getMemory().getBytes(toAddr(0), program);
        if (!java.util.Arrays.equals(image, program)) throw new Exception("Ghidra image differs from CodeFlash");
        EmulatorHelper e = new EmulatorHelper(currentProgram);
        try {
            e.writeMemory(toAddr(0xfebe0000L), new byte[0x20000]);
            for (int commandTransient = 0; commandTransient < 2; commandTransient++) {
                for (int commandLatched = 0; commandLatched < 2; commandLatched++) {
                    for (int angle = 0; angle < 2; angle++) {
                        String name = commandTransient + "/" + commandLatched + "/" + angle;
                        put(e,0xfebecafbL,commandTransient); put(e,0xfebecafdL,commandLatched); put(e,0xfebecad9L,angle);
                        call(e,0xcec72L,0);
                        int command = commandTransient | commandLatched;
                        check("command-source OR " + name, get(e,0xfebecafcL) == command);
                        check("ready entry " + name, call(e,0xce772L,0) == ((command | angle) == 0 ? 1 : 0));
                        check("active exit " + name, call(e,0xce7a6L,1) == ((command | angle) == 0 ? 1 : 0));
                        call(e,0xd0d7cL,0); call(e,0xbf3aaL,0); call(e,0x4c2dcL,0);
                        commandWire = angleWire = -1;
                        call(e,0x4c97aL,0);
                        check("command wire value " + name, commandWire == command);
                        check("angle wire value " + name, angleWire == angle);
                    }
                }
            }
            // Show why the single transmitted command flag cannot distinguish
            // a cleared-on-inactive request failure from a persistent rate latch.
            put(e,0xfebecb00L,7); put(e,0xfebecafbL,1); put(e,0xfebecafdL,0);
            call(e,0xcee7cL,0); call(e,0xcec72L,0);
            check("inactive profile clears request-failure source", get(e,0xfebecafbL) == 0 && get(e,0xfebecafcL) == 0);
            put(e,0xfebecafdL,1);
            call(e,0xcef26L,0); call(e,0xcec72L,0);
            check("inactive profile does not clear latched rate source", get(e,0xfebecafdL) == 1 && get(e,0xfebecafcL) == 1);
            call(e,0xcec0cL,0);
            check("subsystem initialization clears both sources", get(e,0xfebecafbL) == 0 && get(e,0xfebecafdL) == 0 && get(e,0xfebecafcL) == 0);
        } finally { e.dispose(); }
        StringBuilder out = new StringBuilder("{\n  \"schema\": \"camry-cooperative-fault-emulation-v1\",\n  \"vehicle_executed\": false,\n  \"passed\": ");
        out.append(passed.size()).append(",\n  \"tests\": [\n");
        for (int i=0; i<passed.size(); i++) out.append("    \"").append(passed.get(i)).append("\"").append(i+1==passed.size()?"\n":",\n");
        out.append("  ]\n}\n"); Files.writeString(Path.of(args[1]),out);
        println("PASS: " + passed.size() + " cooperative fault-projection assertions");
    }
}
