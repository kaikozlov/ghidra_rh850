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

        // Pin every recovered absolute materialization of the actual write-window
        // base in executable code.  These are startup clear, application page
        // copy, XCP range/translation, and XCP E4 copy.  None is a load used as a
        // callback/control-transfer source.
        assertInstruction(0x1426L, "mov 0xfebf7c00,ep");
        assertInstruction(0x6263eL, "mov 0xfebf7c00,ep");
        assertInstruction(0x974d0L, "mov 0xfebf7c00,r18");
        assertInstruction(0x976d0L, "mov 0xfebf7c00,ep");

        // A visually suspicious adjacent initializer is deliberately below the
        // attacker-write window.  FUN_62662 starts at FEBF7BB0 and performs
        // exactly 0x40 byte stores, therefore ending at FEBF7BEF; it cannot
        // reach FEBF7C00.  Pin the base and loop bound/store sequence so this
        // near-window negative cannot be lost to a later decompiler/xref drift.
        assertInstruction(0x6266eL, "mov 0xfebf7bb0,ep");
        assertInstruction(0x62676L, "add 0x1,r1");
        assertInstruction(0x62678L, "addi -0x40,r1,r0");
        assertInstruction(0x6267cL, "sst.b 0x0[ep],r19");
        assertInstruction(0x6267eL, "bnc 0x00062664");

        // The adjacent XCP DAQ configuration is a separate read-only dynamic
        // pointer path.  Pin every direct reference to the 112-entry pointer
        // table and the decisive indirect load/store instructions so a future
        // analysis change cannot silently turn this into a reverse write path.
        Set<String> daqRefs = new TreeSet<>();
        for (Reference ref : getReferencesTo(toAddr(0xFEBE4CF0L))) {
            daqRefs.add(ref.getFromAddress().toString() + ":" + ref.getReferenceType());
        }
        Set<String> expectedDaqRefs = new TreeSet<>(Arrays.asList(
            "0008120a:WRITE",
            "000812c2:DATA",
            "000814c8:DATA",
            "000817f2:DATA"
        ));
        if (!daqRefs.equals(expectedDaqRefs)) {
            Set<String> missing = new TreeSet<>(expectedDaqRefs); missing.removeAll(daqRefs);
            Set<String> extra = new TreeSet<>(daqRefs); extra.removeAll(expectedDaqRefs);
            throw new IllegalStateException("XCP DAQ pointer-table topology changed missing=" + missing + " extra=" + extra);
        }
        assertInstruction(0x812c2L, "sld.w 0x0[ep],ep");
        assertInstruction(0x812ceL, "sld.bu 0x0[ep],r18");
        assertInstruction(0x812d0L, "st.b r18,-0x6b38[r19]");
        assertInstruction(0x814c8L, "st.w r28,-0x6b10[ep]");
        assertInstruction(0x81542L, "andi 0x33,r1,r0");
        assertInstruction(0x82078L, "ori 0xf800,r6,r6");

        println(String.format(
            "ASSERT xcp-shadow-write-boundary: block=%s bytes=%d read=true write=true execute=false refs=3 writes=3 reads=0 params=0 calls=0 other=0 functions=0 materializers=4 near_window=FEBF7BB0..FEBF7BEF_bounded_below daq_refs=4 daq_direction=ram_to_dto daq_mode_mask=0x33 unexpected=0",
            block.getName(), END - START + 1));
    }

    private void assertInstruction(long offset, String expected) {
        Instruction ins = getInstructionAt(toAddr(offset));
        if (ins == null || !ins.toString().equals(expected)) {
            throw new IllegalStateException(String.format(
                "instruction changed at %08X expected=%s actual=%s", offset, expected, ins));
        }
    }
}
