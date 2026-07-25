//@author optskug
//@category Analysis
// Attach the 32 KiB DataFlash prefix to an imported 1 MiB CodeFlash program.
// Usage: AddDataFlash.java /absolute/path/to/RH850_P1M-E_DataFlash.bin
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Program;
import ghidra.program.model.mem.Memory;
import ghidra.program.model.mem.MemoryBlock;
import java.io.File;
import java.io.FileInputStream;

public class AddDataFlash extends GhidraScript {
    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length != 1) {
            throw new IllegalArgumentException("expected absolute DataFlash .bin path");
        }
        File input = new File(args[0]);
        if (!input.isFile() || input.length() != 0x8000L) {
            throw new IllegalArgumentException("DataFlash must exist and be exactly 0x8000 bytes: " + input);
        }

        Memory mem = currentProgram.getMemory();
        Address codeStart = toAddr(0x00000000L);
        MemoryBlock code = mem.getBlock(codeStart);
        if (code == null || code.getSize() != 0x100000L) {
            throw new IllegalStateException("expected 1 MiB CodeFlash block at 0x0");
        }
        code.setName("CodeFlash");
        code.setRead(true);
        code.setWrite(false);
        code.setExecute(true);

        Address dataStart = toAddr(0xFF200000L);
        MemoryBlock old = mem.getBlock(dataStart);
        if (old != null) {
            println("DataFlash already mapped: " + old.getStart() + ".." + old.getEnd());
            return;
        }
        try (FileInputStream in = new FileInputStream(input)) {
            MemoryBlock data = mem.createInitializedBlock(
                "DataFlash", dataStart, in, 0x8000L, monitor, false);
            data.setRead(true);
            data.setWrite(true);
            data.setExecute(false);
            println("Mapped CodeFlash 0x00000000..0x000FFFFF and DataFlash "
                    + data.getStart() + ".." + data.getEnd());
        }
    }
}
