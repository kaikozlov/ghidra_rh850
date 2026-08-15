//@author kaikozlov
//@category Verification
// Read-only assertion for the XCP generic-write LocalRAM window.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.*;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.symbol.Reference;
import java.util.*;

public class AssertXcpShadowWriteBoundary extends GhidraScript {
    private static final long START = 0xFEBF7C00L;
    private static final long END   = 0xFEBFFBFFL;

    @Override public void run() throws Exception {
        Address start = toAddr(START), end = toAddr(END);
        MemoryBlock block = currentProgram.getMemory().getBlock(start);
        if (block == null || !block.contains(end))
            throw new IllegalStateException("XCP write window is not wholly inside one memory block");
        if (!block.isRead() || !block.isWrite() || block.isExecute())
            throw new IllegalStateException(String.format(
                "unexpected XCP window permissions block=%s read=%s write=%s execute=%s",
                block.getName(), block.isRead(), block.isWrite(), block.isExecute()));

        Set<String> actual = new TreeSet<>();
        int readRefs = 0, writeRefs = 0, paramRefs = 0, callRefs = 0, otherRefs = 0;
        int functionsInWindow = 0;
        FunctionIterator funcs = currentProgram.getFunctionManager().getFunctions(true);
        while (funcs.hasNext()) {
            monitor.checkCancelled();
            Function f = funcs.next();
            long entry = f.getEntryPoint().getOffset();
            if (START <= entry && entry <= END) functionsInWindow++;
            InstructionIterator it = currentProgram.getListing().getInstructions(f.getBody(), true);
            while (it.hasNext()) {
                monitor.checkCancelled();
                Instruction ins = it.next();
                for (Reference ref : ins.getReferencesFrom()) {
                    Address target = ref.getToAddress();
                    if (target == null || !target.isMemoryAddress()) continue;
                    long off = target.getOffset();
                    if (off < START || off > END) continue;
                    String type = ref.getReferenceType().toString();
                    actual.add(ins.getAddress().toString() + ":" + type + ":" + target.toString());
                    if (type.equals("READ")) readRefs++;
                    else if (type.equals("WRITE")) writeRefs++;
                    else if (type.equals("PARAM")) paramRefs++;
                    else if (type.contains("CALL") || type.contains("JUMP")) callRefs++;
                    else otherRefs++;
                }
            }
        }

        Set<String> expected = new TreeSet<>(Arrays.asList(
            "0000142e:WRITE:febf7c00",
            "00062652:WRITE:febf7c00",
            "000976e4:WRITE:febf7c00"
        ));
        if (!actual.equals(expected)) {
            Set<String> missing = new TreeSet<>(expected); missing.removeAll(actual);
            Set<String> extra = new TreeSet<>(actual); extra.removeAll(expected);
            throw new IllegalStateException("XCP shadow direct-reference topology changed missing=" + missing + " extra=" + extra);
        }
        if (readRefs != 0 || paramRefs != 0 || callRefs != 0 || otherRefs != 0 || writeRefs != 3 || functionsInWindow != 0)
            throw new IllegalStateException(String.format(
                "unexpected XCP shadow consumers reads=%d writes=%d params=%d calls=%d other=%d functions=%d",
                readRefs, writeRefs, paramRefs, callRefs, otherRefs, functionsInWindow));

        println(String.format(
            "ASSERT xcp-shadow-write-boundary: block=%s bytes=%d read=true write=true execute=false refs=3 writes=3 reads=0 params=0 calls=0 other=0 functions=0 unexpected=0",
            block.getName(), END - START + 1));
    }
}
