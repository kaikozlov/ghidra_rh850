//@author kaikozlov
//@category Verification
// Execute stock fault-aggregation instructions in emulator-local memory only.
// Args: <CodeFlash.bin> <result.json>. No vehicle access or program-database mutation.
import ghidra.app.script.GhidraScript;
import ghidra.app.emulator.EmulatorHelper;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;

public class VerifyCamryFaultProjection extends GhidraScript {
    private static final long GP = 0xfebeb800L;
    private static final long RETURN = 0x10000L;
    private final List<String> passed = new ArrayList<>();

    private void put(EmulatorHelper e, long address, int value, int size) {
        byte[] bytes = new byte[size];
        for (int i = 0; i < size; i++) bytes[i] = (byte)(value >>> (8 * i));
        e.writeMemory(toAddr(address), bytes);
    }
    private int get(EmulatorHelper e, long address) throws Exception {
        return e.readMemoryByte(toAddr(address)) & 255;
    }
    private void check(String name, boolean condition) throws Exception {
        if (!condition) throw new Exception("FAILED: " + name);
        passed.add(name);
    }
    private void call(EmulatorHelper e, long entry, int argument) throws Exception {
        e.writeRegister("PC", entry);
        e.writeRegister("gp", GP);
        e.writeRegister("sp", 0xfebe1800L);
        e.writeRegister("lp", RETURN);
        e.writeRegister("r6", argument);
        for (int count = 0; count < 500; count++) {
            long pc = e.readRegister("PC").longValue() & 0xffffffffL;
            if (pc == RETURN) return;
            // Interrupt save/restore has no concurrent actor in this unit
            // model. All aggregation and count-update instructions are stock.
            if (pc == 0x701c4L || pc == 0x701eaL) {
                e.writeRegister("r10", 0);
                e.writeRegister("PC", e.readRegister("lp"));
            } else if (get(e, pc) == 0 && get(e, pc + 1) == 0) {
                e.writeRegister("PC", pc + 2);
            } else if (!e.step(monitor)) {
                throw new Exception(e.getLastError());
            }
        }
        throw new Exception("stock function did not return");
    }
    @Override public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length != 2) throw new IllegalArgumentException("image and result paths required");
        byte[] image = Files.readAllBytes(Path.of(args[0]));
        byte[] program = new byte[image.length];
        currentProgram.getMemory().getBytes(toAddr(0), program);
        if (!java.util.Arrays.equals(image, program)) throw new Exception("Ghidra bytes differ from verified CodeFlash");
        EmulatorHelper e = new EmulatorHelper(currentProgram);
        try {
            e.writeMemory(toAddr(0xfebe8000L), new byte[0x1000]);
            e.writeMemory(toAddr(0xfebee800L), new byte[0x100]);
            put(e, 0xfebee8ccL, 0x400, 2);
            put(e, 0xfebe6764L, 0, 2);
            put(e, 0xfebe66a8L, 0, 2);
            put(e, 0xfebe6718L, 0, 2);
            long[] counters = {0xfebe82baL, 0xfebe82c2L, 0xfebe82c4L};
            for (int mask = 0; mask < 64; mask++) {
                for (int i = 0; i < 3; i++) {
                    put(e, counters[i], (mask >>> i) & 1, 2);
                    put(e, 0xfebee857L + i, (mask & (8 << i)) != 0 ? 0x22 : 0x11, 1);
                }
                call(e, 0x4c000L, 0);
                check("six-input live OR mask " + mask, get(e, 0xfebe80deL) == (mask == 0 ? 0 : 1));
            }
            for (long address : counters) put(e, address, 0, 2);
            for (int i = 0; i < 3; i++) put(e, 0xfebee857L + i, 0x11, 1);
            put(e, 0xfebe82a3L, 0xffffff, 3); // latched event history is NOT a live fault
            call(e, 0x4c000L, 0);
            check("history alone does not assert live fault", get(e, 0xfebe80deL) == 0);
            int[] classes = {2, 4, 8, 15, 16, 32, 64, 128, 240};
            for (int cls : classes) {
                boolean selected = cls == 2 || cls == 16 || cls == 32;
                call(e, 0x50fc8L, cls);
                call(e, 0x4c000L, 0);
                check("class assertion " + cls, get(e, 0xfebe80deL) == (selected ? 1 : 0));
                call(e, 0x514bcL, cls);
                call(e, 0x4c000L, 0);
                check("class recovery " + cls, get(e, 0xfebe80deL) == 0);
            }
            call(e, 0x50fc8L, 2);
            call(e, 0x50fc8L, 2);
            call(e, 0x514bcL, 2);
            call(e, 0x4c000L, 0);
            check("one remaining active event keeps aggregate set", get(e, 0xfebe80deL) == 1);
            call(e, 0x514bcL, 2);
            call(e, 0x514bcL, 2);
            call(e, 0x4c000L, 0);
            check("last recovery clears and extra recovery cannot underflow", get(e, 0xfebe80deL) == 0);
        } finally { e.dispose(); }
        StringBuilder out = new StringBuilder("{\n  \"schema\": \"camry-live-fault-emulation-v1\",\n  \"vehicle_executed\": false,\n  \"passed\": ");
        out.append(passed.size()).append(",\n  \"tests\": [\n");
        for (int i = 0; i < passed.size(); i++) out.append("    \"").append(passed.get(i)).append("\"")
                .append(i + 1 == passed.size() ? "\n" : ",\n");
        out.append("  ]\n}\n");
        Files.writeString(Path.of(args[1]), out);
        println("PASS: " + passed.size() + " stock fault-projection assertions");
    }
}
