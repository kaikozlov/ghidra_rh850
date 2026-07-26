//@author kaikozlov
//@category Analysis
// Find decode gaps: bytes inside a function body that Ghidra left undefined
// (no instruction and no defined data). A genuine SLEIGH decode failure shows
// up here, whereas data/padding between functions does not. Reports affected
// functions, total undefined bytes, and a sample of each with surrounding
// bytes for diagnosis.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.mem.Memory;

public class FindUndefinedInFunctions extends GhidraScript {
    @Override
    public void run() throws Exception {
        Listing listing = currentProgram.getListing();
        Memory mem = currentProgram.getMemory();
        FunctionIterator it = currentProgram.getFunctionManager().getFunctions(true);
        long totalFuncs = 0, funcsWithUndef = 0, totalUndef = 0;
        java.util.List<String> samples = new java.util.ArrayList<>();
        while (it.hasNext()) {
            Function f = it.next();
            totalFuncs++;
            int funcUndef = 0;
            for (AddressRange r : f.getBody()) {
                Address a = r.getMinAddress();
                Address max = r.getMaxAddress();
                while (a.compareTo(max) <= 0) {
                    CodeUnit cu = listing.getCodeUnitAt(a);
                    if (cu == null) {
                        funcUndef++;
                        if (samples.size() < 80) {
                            byte[] buf = new byte[8];
                            try { mem.getBytes(a, buf); } catch (Exception e) { }
                            StringBuilder hex = new StringBuilder();
                            for (byte b : buf) hex.append(String.format("%02x ", b));
                            samples.add(String.format("%-10s %-26s bytes: %s", a, f.getName(), hex));
                        }
                        a = a.add(1);
                    } else {
                        a = cu.getMaxAddress().add(1);
                    }
                }
            }
            if (funcUndef > 0) { funcsWithUndef++; totalUndef += funcUndef; }
        }
        println("functions scanned: " + totalFuncs);
        println("functions with undefined bytes inside body: " + funcsWithUndef);
        println("total undefined bytes inside function bodies: " + totalUndef);
        println("== samples (addr func bytes) ==");
        for (String s : samples) println("  " + s);
    }
}
